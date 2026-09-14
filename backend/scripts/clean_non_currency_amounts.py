"""清掉「數量被當成金額」的紀錄：金額數字在摘錄裡每次出現後面接的都是量詞（副、份、點、cc…）。

例：「每人以1副並限本人使用」→ 1 元、「單胞胎 1份(箱/打)」→ 1～3 元。
這些金額不是錯抄原文，而是把數量詞當成錢，會直接誤導民眾，所以整個金額欄位清空並重算完整度。
加 --dry 只看不改。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, utcnow  # noqa: E402
from app.services import admission  # noqa: E402
from app.services.extractor import Extractor  # noqa: E402
from app.services.normalization import number_is_counted  # noqa: E402

EMPTY = {"type": "unknown", "value": None, "min": None, "max": None, "unit": "TWD",
         "period": "unknown", "count_per_year": None, "description": "", "tiers": []}


def main() -> int:
    dry = "--dry" in sys.argv
    db = get_db()
    cleaned = 0
    for row in db.benefits.find({"benefit.amount.min": {"$ne": None}}):
        amount = (row.get("benefit") or {}).get("amount") or {}
        numbers = [v for v in (amount.get("value"), amount.get("min"), amount.get("max")) if isinstance(v, (int, float))]
        if not numbers:
            continue
        excerpt = amount.get("description") or ""
        evidence = next((e for e in (row.get("evidence") or []) if e.get("field") == "benefit.amount"), None)
        if evidence and not excerpt:
            excerpt = evidence.get("excerpt") or ""
        if not any(number_is_counted(v, excerpt) for v in numbers):
            continue
        cleaned += 1
        print(f"- {(row.get('title') or '')[:36]}：{sorted({int(v) for v in numbers})} ← 「{excerpt[:60]}」")
        if dry:
            continue
        benefit = dict(row.get("benefit") or {})
        benefit["amount"] = dict(EMPTY)
        benefit.pop("amount_annualized", None)
        evidence_left = [e for e in (row.get("evidence") or []) if e.get("field") != "benefit.amount"]
        updated = {**row, "benefit": benefit, "evidence": evidence_left}
        fields = admission.completeness(updated)
        kind = (row.get("admission") or {}).get("kind") or row.get("record_kind") or "program"
        db.benefits.update_one(
            {"_id": row["_id"]},
            {"$set": {"benefit": benefit, "evidence": evidence_left,
                      "admission.completeness": fields,
                      "admission.quality_tier": admission.quality_tier(updated, kind, fields),
                      "index": Extractor.build_index(updated), "updated_at": utcnow()}},
        )
    print(f"{'（試跑）' if dry else ''}清掉 {cleaned} 筆沒有幣別字樣的金額")
    return 0


if __name__ == "__main__":
    sys.exit(main())
