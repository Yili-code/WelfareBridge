"""建立／重算資格骨幹（eligibility_core）。

    python scripts/build_eligibility_core.py                    # 全部可媒合的補助：規則式訊號 + 本地 AI（已跑過 AI 的沿用結果）
    python scripts/build_eligibility_core.py --gold             # 只跑黃金集標註過的補助
    python scripts/build_eligibility_core.py --no-llm           # 只用規則式訊號（AI 不在線時）
    python scripts/build_eligibility_core.py --refresh-llm      # 重新呼叫 AI（換模型後）
    python scripts/build_eligibility_core.py --gold --report    # 不寫入，只和黃金集比對各類條件的準確度

模型：CORE_LLM_MODEL（預設 qwen3:8b；空字串＝沿用 LLM_MODEL）。
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections import Counter
from pathlib import Path

import yaml

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.config import get_settings  # noqa: E402
from app.db import get_db  # noqa: E402
from app.llm import core_extract  # noqa: E402
from app.services.core_builder import build_core  # noqa: E402

log = logging.getLogger("build_eligibility_core")
GOLD = Path(get_settings().data_path) / "gold" / "matching" / "benefit_facets.yaml"


def _key(facet: dict) -> tuple:
    kind = facet["kind"]
    if kind == "residence":
        return (kind, tuple(sorted(facet.get("cities") or [])))
    if kind == "age":
        return (kind, facet.get("min"), facet.get("max"))
    if kind == "education":
        from app.services.core_builder import BANDS

        return (kind, tuple(sorted({BANDS[l] for l in facet.get("levels") or []})))
    if kind in {"identity_any", "identity_exclude"}:
        return (kind, tuple(sorted(facet.get("tags") or [])))
    if kind == "attr":
        return (kind, facet.get("attribute_id"), str(facet.get("value")))
    return (kind, str(facet.get("value")))


def compare(built: list[dict], gold: list[dict]) -> Counter:
    """逐類比較：confirmed 正確／錯誤（會誤排除）、uncertain、漏抽、多抽。"""
    counts: Counter = Counter()
    gold_keys = {_key(f): f for f in gold}
    used: set[tuple] = set()
    for facet in built:
        key = _key(facet)
        kind = facet["kind"]
        if kind == "residence" and not facet.get("cities"):
            continue
        status = facet.get("status")
        match = key in gold_keys
        if not match and kind == "identity_any":
            match = any(k[0] == kind and set(k[1]) & set(key[1]) for k in gold_keys)
            if match:
                key = next(k for k in gold_keys if k[0] == kind and set(k[1]) & set(key[1]))
        same_kind = [k for k in gold_keys if k[0] == kind and k not in used]
        if match:
            used.add(key)
            counts[f"{kind}:{status}_ok"] += 1
        elif same_kind and kind not in {"identity_any", "attr"}:
            used.add(same_kind[0])
            counts[f"{kind}:{status}_wrong"] += 1
        else:
            counts[f"{kind}:{status}_spurious"] += 1
    for key in gold_keys:
        if key not in used and not (key[0] == "residence" and not key[1]):
            counts[f"{key[0]}:missing"] += 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", action="store_true")
    parser.add_argument("--label-file", default="benefit_facets", help="--gold 使用的標註檔（benefit_facets｜holdout_facets）")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--refresh-llm", action="store_true")
    parser.add_argument("--report", action="store_true", help="不寫入資料庫，只和黃金集比對")
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    db = get_db()
    gold_file = GOLD.with_name(f"{args.label_file}.yaml")
    labels = {row["id"]: row for row in yaml.safe_load(gold_file.read_text(encoding="utf-8"))["labels"]} if gold_file.exists() else {}
    query: dict = {"record_kind": {"$ne": "portal"}}
    if args.gold:
        query["_id"] = {"$in": list(labels)}
    rows = list(db.benefits.find(query, {"_id": 1, "is_canonical": 1, "status": 1}))
    rows.sort(key=lambda r: (not r.get("is_canonical"), r.get("status") == "expired"))  # 先做會出現在媒合裡的
    if args.limit:
        rows = rows[: args.limit]
    use_llm = not args.no_llm and core_extract.core_provider() is not None
    log.info("records=%d llm=%s model=%s", len(rows), use_llm, get_settings().core_llm_model or get_settings().llm_model)
    totals: Counter = Counter()
    started = time.monotonic()
    for index, row in enumerate(rows, 1):
        record = db.benefits.find_one({"_id": row["_id"]})
        previous = record.get("eligibility_core") or {}
        llm_output = previous.get("llm")
        if use_llm and (args.refresh_llm or not llm_output):
            try:
                llm_output = core_extract.extract_raw(record)
                totals["llm_calls"] += 1
            except Exception as exc:  # 單筆失敗不中斷批次
                log.warning("llm failed %s: %s", record["_id"], exc)
                totals["llm_errors"] += 1
        elif args.no_llm:
            llm_output = None
        core = build_core(record, llm_output=llm_output)
        if args.report and record["_id"] in labels:
            from scripts_eval import facets_from_label  # type: ignore

            counts = compare(core["facets"], facets_from_label(labels[record["_id"]]))
            totals.update(counts)
            if args.details and any(k.endswith(("_wrong", "_spurious")) and "confirmed" in k or k.endswith("missing") for k in counts):
                print(f"--- {record['title'][:40]}  {dict(counts)}")
                print("    built:", [{k: v for k, v in f.items() if k not in {"quote"}} for f in core["facets"]])
                print("    gold :", [{k: v for k, v in f.items() if k not in {"status", "signals"}} for f in facets_from_label(labels[record["_id"]])])
        if not args.report:
            db.benefits.update_one({"_id": record["_id"]}, {"$set": {"eligibility_core": core}})
        totals["records"] += 1
        totals.update(f"facet:{f['kind']}:{f['status']}" for f in core["facets"])
        if index % 25 == 0:
            elapsed = time.monotonic() - started
            log.info("%d/%d (%.1fs/record)", index, len(rows), elapsed / index)
    for key in sorted(totals):
        print(f"{key}: {totals[key]}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import importlib

    sys.modules["scripts_eval"] = importlib.import_module("eval_matching")
    raise SystemExit(main())
