"""把「互斥卻被寫成必須同時成立」的資格規則就地鬆綁成擇一群組（不重抽、不呼叫 LLM）。

對應 extractor.relax_contradictory_rules：同一屬性的必要條件分屬不同群組（AND）卻不可能同時為真時，
把那些群組併成一個擇一（OR）群組，並在說明後面加「（擇一）」。加 --dry 只看不改。
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, utcnow  # noqa: E402
from app.services.extractor import Extractor, relax_contradictory_rules  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_unsatisfiable_rules import unsatisfiable_reasons  # noqa: E402


def main() -> int:
    dry = "--dry" in sys.argv
    db = get_db()
    changed = fixed = still = 0
    examples: list[str] = []
    for row in db.benefits.find({}, {"rules": 1, "title": 1, "benefit": 1}):
        rules = row.get("rules") or []
        before = unsatisfiable_reasons(rules)
        if not before:
            continue
        merged = relax_contradictory_rules(rules)
        after = unsatisfiable_reasons(rules)
        if not merged:
            continue
        changed += 1
        if after:
            still += 1
        else:
            fixed += 1
        if len(examples) < 12:
            examples.append(f"{(row.get('title') or '')[:34]}：{before[0][:70]}")
        if not dry:
            db.benefits.update_one({"_id": row["_id"]}, {"$set": {"rules": rules, "index": Extractor.build_index({**row, "rules": rules}), "updated_at": utcnow()}})
    print(f"鬆綁 {changed} 筆；其中完全解決 {fixed} 筆、仍有互斥 {still} 筆")
    for line in examples:
        print("   ", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
