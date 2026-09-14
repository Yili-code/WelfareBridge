"""把本地 AI 改寫（非原文逐字）的義務條款清掉，只留原文逐字的句子。

原則：義務條款會被當成「原文規定」顯示，所以必須逐字出自原文；AI 的摘要留在 llm.accepted 紀錄裡可追溯，
但不進正式欄位。其他敘述型欄位（適用對象、申請方式）允許改寫，只要裡面的數字與縣市出自原文（由 audit_records.py 檢查）。
加 --dry 只看不改。
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, utcnow  # noqa: E402
from app.services.schema_validator import excerpt_in_text  # noqa: E402


def main() -> int:
    dry = "--dry" in sys.argv
    db = get_db()
    stats = Counter()
    examples = []
    changed = 0
    for row in db.benefits.find({}, {"benefit.obligations": 1, "original_text": 1, "title": 1, "review": 1}):
        obligations = ((row.get("benefit") or {}).get("obligations")) or []
        if not obligations:
            continue
        text = row.get("original_text") or ""
        kept = [o for o in obligations if excerpt_in_text(o, text)]
        removed = [o for o in obligations if o not in kept]
        if not removed:
            continue
        changed += 1
        stats["obligations_removed"] += len(removed)
        if len(examples) < 15:
            examples.append(f"{(row.get('title') or '')[:26]}：移除 {removed[:2]}")
        if not dry:
            reasons = list(((row.get("review") or {}).get("reasons")) or [])
            note = f"本地 AI 改寫的義務條款 {len(removed)} 條未逐字出現在原文，已移除（原始建議保留在 llm.accepted）"
            if note not in reasons:
                reasons.append(note)
            db.benefits.update_one({"_id": row["_id"]}, {"$set": {"benefit.obligations": kept, "review.needs_review": True, "review.reasons": reasons, "updated_at": utcnow()}})
    print("records changed:", changed)
    for code, n in stats.most_common():
        print(f"  {n:>6}  {code}")
    for line in examples:
        print("   ", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
