"""把標註代理輸出的 JSON（{labels:[...]}）合併進 data/gold/gold_labels.yaml。
- 檢查 id 存在於 raw_documents、不與既有黃金列重複、category/secondary 都是 taxonomy 葉節點 id
- is_benefit 只接受 yes/portal/no；kind 只接受已知種類；closed 轉布林
- 逐列以單行 flow style 追加，保留檔頭註解
用法：python merge_gold_labels.py <labels1.json> <labels2.json> ... [--dry]
"""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import sys

import yaml

BACKEND = str(Path(__file__).resolve().parents[2])
GOLD = str(Path(__file__).resolve().parents[3] / "data/gold/gold_labels.yaml")
sys.path.insert(0, BACKEND)
from app.db import get_db  # noqa: E402
from app.registry import get_registry  # noqa: E402

KINDS = {"program", "portal", "form", "attachment", "flowchart", "progress_query", "logo", "statistics", "faq", "directory", "notice", "fragment", "garbled", "site_info", "statute", "news", "other"}


def inline(d: dict) -> str:
    s = yaml.safe_dump(d, allow_unicode=True, default_flow_style=True, sort_keys=False, width=10000).strip()
    return s[:-4].strip() if s.endswith("\n...") else s


def main(argv: list[str]) -> int:
    dry = "--dry" in argv
    files = [a for a in argv if not a.startswith("--")]
    registry = get_registry()
    leaves = {node.id for node in registry.leaves()}
    db = get_db()
    gold_text = io.open(GOLD, encoding="utf-8").read()
    existing = {g["id"] for g in (yaml.safe_load(gold_text) or {}).get("labels", [])}
    rows, problems = [], []
    seen = set()
    for path in files:
        data = json.load(io.open(path, encoding="utf-8"))
        for lab in data.get("labels", []):
            i = lab.get("id", "")
            if i in existing or i in seen:
                problems.append(f"重複 id {i}")
                continue
            doc = db.raw_documents.find_one({"_id": i}, {"title": 1})
            if not doc:
                problems.append(f"資料庫沒有 id {i}")
                continue
            verdict = str(lab.get("is_benefit", "")).lower()
            if verdict in {"true", "y"}:
                verdict = "yes"
            if verdict in {"false", "n"}:
                verdict = "no"
            if verdict not in {"yes", "portal", "no"}:
                problems.append(f"{i} is_benefit 不合法: {lab.get('is_benefit')}")
                continue
            cat = lab.get("category") or ""
            if cat and cat not in leaves:
                problems.append(f"{i} category 不在 taxonomy: {cat}")
                cat = ""
            sec = [s for s in (lab.get("secondary") or []) if s in leaves and s != cat]
            kind = lab.get("kind") or ("program" if verdict == "yes" else "other")
            if kind not in KINDS:
                kind = "other"
            row = {"id": i, "title": (doc.get("title") or lab.get("title") or "")[:80], "is_benefit": verdict, "kind": kind, "category": cat, "secondary": sec}
            if lab.get("closed"):
                row["closed"] = True
            row["reason"] = (lab.get("reason") or "")[:120]
            if lab.get("confidence") in {"medium", "low"}:
                row["confidence"] = lab["confidence"]
            rows.append(row)
            seen.add(i)
    print(f"新標註 {len(rows)} 筆；問題 {len(problems)} 筆")
    for p in problems[:20]:
        print("  !", p)
    if dry or not rows:
        return 0
    block = "\n".join("  - " + inline(r) for r in rows)
    new_text = gold_text.rstrip("\n") + "\n" + block + "\n"
    yaml.safe_load(new_text)
    io.open(GOLD, "w", encoding="utf-8").write(new_text)
    total = len((yaml.safe_load(new_text) or {}).get("labels", []))
    print("gold_labels.yaml 現在共", total, "筆")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
