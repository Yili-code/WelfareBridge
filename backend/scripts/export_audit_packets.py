"""把每一筆補助紀錄輸出成「稽核包」：欄位現況＋原文，供逐筆對照原文檢查（代理或人工）。

每個批次一個 .txt 檔，每筆紀錄的格式固定：
  ##### <id>
  TITLE / SOURCE / URL / CATEGORY / PROVIDER / STATUS / TIER / MISSING
  AMOUNT / PERIOD / APPLY / OBLIGATIONS / TARGET / FORM / QUOTA
  RULES（簡單規則逐條；佔位規則只計數）
  FLAGS（規則式稽核抓到的可疑之處）
  TEXT（原文，預設 4000 字）

用法：python scripts/export_audit_packets.py --out <dir> --batch-size 22 [--flagged-only] [--audit docs/generated/record-audit.json]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db  # noqa: E402
from app.registry import get_registry  # noqa: E402


def one_line(value: str, limit: int = 300) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def amount_line(amount: dict) -> str:
    parts = [f"type={amount.get('type')}"]
    for key in ("value", "min", "max"):
        if amount.get(key) is not None:
            parts.append(f"{key}={amount[key]:.0f}" if isinstance(amount[key], (int, float)) else f"{key}={amount[key]}")
    if amount.get("period") and amount["period"] != "unknown":
        parts.append(f"period={amount['period']}")
    tiers = amount.get("tiers") or []
    if tiers:
        parts.append("tiers=" + "; ".join(f"{t.get('label', '')}={t.get('value')}" for t in tiers[:6]))
    if amount.get("description"):
        parts.append("摘錄=「" + one_line(amount["description"], 160) + "」")
    return " ｜ ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch-size", type=int, default=22)
    ap.add_argument("--max-chars", type=int, default=4000)
    ap.add_argument("--flagged-only", action="store_true")
    ap.add_argument("--sample", type=int, default=0, help="每個來源輪流取樣，共取 N 筆（不隨機，可重現）")
    ap.add_argument("--audit", default="docs/generated/record-audit.json")
    args = ap.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    audit_path = args.audit if os.path.isabs(args.audit) else os.path.join(root, args.audit)
    flags_by_id: dict[str, list[str]] = {}
    if os.path.exists(audit_path):
        data = json.load(io.open(audit_path, encoding="utf-8"))
        for record in data.get("records", []):
            if record.get("flags"):
                flags_by_id[record["id"]] = [f"{f['code']} {f['field']}：{one_line(f['detail'], 160)}" for f in record["flags"]]

    db = get_db()
    registry = get_registry()
    rows = list(db.benefits.find({"is_canonical": True, "record_kind": "program"}).sort("source_id", 1))
    if args.flagged_only:
        rows = [r for r in rows if r["_id"] in flags_by_id]
    if args.sample and args.sample < len(rows):
        by_source: dict[str, list[dict]] = {}
        for row in rows:
            by_source.setdefault(row.get("source_id") or "", []).append(row)
        order = sorted(by_source)
        picked: list[dict] = []
        depth = 0
        while len(picked) < args.sample:
            added = False
            for source in order:
                bucket = by_source[source]
                if depth < len(bucket) and len(picked) < args.sample:
                    picked.append(bucket[depth])
                    added = True
            if not added:
                break
            depth += 1
        rows = picked
    os.makedirs(args.out, exist_ok=True)
    written = []
    for index in range(0, len(rows), args.batch_size):
        batch = rows[index : index + args.batch_size]
        path = os.path.join(args.out, f"audit_{index // args.batch_size + 1:02d}.txt")
        with io.open(path, "w", encoding="utf-8") as out:
            for row in batch:
                meta = row.get("benefit") or {}
                amount = meta.get("amount") or {}
                period = meta.get("application_period") or {}
                application = meta.get("application") or {}
                admission = row.get("admission") or {}
                node = registry.category(row.get("category") or "")
                out.write(f"##### {row['_id']}\n")
                out.write(f"TITLE: {one_line(row.get('title'), 120)}\n")
                out.write(f"SOURCE: {row.get('source_id')} ｜ URL: {(row.get('source') or {}).get('source_url', '')}\n")
                out.write(f"CATEGORY: {row.get('category')}（{node.label if node else '?'}）｜ 次類別: {row.get('categories_secondary') or []} ｜ 領域: {row.get('domain')} ｜ 信心: {row.get('category_confidence')}\n")
                out.write(f"PROVIDER: {row.get('provider')} ｜ 類型: {row.get('provider_type')} ｜ 地區: {row.get('provider_region')}\n")
                out.write(f"STATUS: {row.get('status')} ｜ 等級: {admission.get('quality_tier')} ｜ 缺欄位: {(admission.get('completeness') or {}).get('missing') or []}\n")
                out.write(f"FORM: {meta.get('benefit_form')}（推定={meta.get('benefit_form_inferred')}）｜ 名額: {meta.get('quota')} ｜ 排他: {meta.get('exclusive_with')}\n")
                out.write(f"AMOUNT: {amount_line(amount)}\n")
                out.write(f"PERIOD: start={period.get('start_date')} end={period.get('end_date')} rolling={period.get('rolling')} 說明=「{one_line(period.get('description'), 120)}」\n")
                out.write(f"APPLY: channel={application.get('channel')} 方式=「{one_line(application.get('method'), 200)}」 文件={[one_line(d, 40) for d in (application.get('documents') or [])][:6]}\n")
                out.write(f"OBLIGATIONS: {[one_line(o, 60) for o in (meta.get('obligations') or [])][:5]}\n")
                out.write(f"TARGET: {one_line(meta.get('target_population_text'), 200)}\n")
                simple = [r for r in (row.get("rules") or []) if r.get("complexity") == "simple"]
                placeholders = [r for r in (row.get("rules") or []) if r.get("complexity") != "simple"]
                out.write(f"RULES（簡單規則 {len(simple)} 條、待語意判斷 {len(placeholders)} 條；同一群組＝擇一，不同群組＝須同時成立）:\n")
                for rule in simple[:18]:
                    out.write(f"  - {rule.get('attribute_id')} {rule.get('operator')} {json.dumps(rule.get('value'), ensure_ascii=False)}"
                              f" ｜ 角色={rule.get('role')} ｜ 群組={rule.get('group_id')} ｜ 推定={rule.get('inferred')} ｜ 說明={one_line(rule.get('human_readable'), 60)}"
                              f" ｜ 摘錄=「{one_line((rule.get('evidence') or {}).get('excerpt'), 90)}」\n")
                if row["_id"] in flags_by_id:
                    out.write("FLAGS:\n")
                    for line in flags_by_id[row["_id"]][:12]:
                        out.write(f"  - {line}\n")
                out.write("TEXT:\n")
                out.write((row.get("original_text") or "")[: args.max_chars].rstrip() + "\n\n")
        written.append(path)
        print("wrote", path, len(batch))
    io.open(os.path.join(args.out, "index.json"), "w", encoding="utf-8").write(json.dumps({"batches": written, "records": len(rows)}, ensure_ascii=False, indent=1))
    print("records", len(rows), "batches", len(written))
    return 0


if __name__ == "__main__":
    sys.exit(main())
