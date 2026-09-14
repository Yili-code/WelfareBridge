"""清掉既有紀錄裡的垃圾佔位規則（operator=exists）：
  1. 摘錄根本不是條件（段落標題、「學門：不拘」）→ 整條刪掉，對應的 condition 標為 not_a_condition
  2. 摘錄是條件但 attribute_id 是硬湊的（摘錄沒提到該屬性）→ attribute_id 清空（媒合行為不變：需語意判斷）
  3. 同一句已經有具體規則涵蓋 → 刪掉重複的佔位規則
不呼叫 LLM、不改任何欄位值；僅整理規則。加 --dry 只看不改。
"""
from __future__ import annotations

import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, utcnow  # noqa: E402
from app.registry import get_registry  # noqa: E402
from app.services.extractor import Extractor, is_real_condition, placeholder_attribute  # noqa: E402


def main() -> int:
    dry = "--dry" in sys.argv
    db = get_db()
    registry = get_registry()
    stats = Counter()
    examples: list[str] = []
    changed = 0
    for row in db.benefits.find({}, {"rules": 1, "conditions": 1, "title": 1}):
        rules = row.get("rules") or []
        if not rules:
            continue
        concrete_excerpts = {(r.get("evidence") or {}).get("excerpt") for r in rules if r.get("operator") != "exists"}
        kept: list[dict] = []
        dropped_texts: set[str] = set()
        for rule in rules:
            if rule.get("operator") != "exists":
                kept.append(rule)
                continue
            evidence = rule.get("evidence") or {}
            excerpt = (evidence.get("excerpt") or evidence.get("condition_text") or "").strip()
            if not is_real_condition(excerpt):
                stats["dropped_not_a_condition"] += 1
                dropped_texts.add(evidence.get("condition_text") or excerpt)
                if len(examples) < 20:
                    examples.append(f"刪除（不是條件）：{rule.get('attribute_id')} ← 「{excerpt[:40]}」")
                continue
            if excerpt in concrete_excerpts:
                stats["dropped_duplicate"] += 1
                dropped_texts.add(evidence.get("condition_text") or excerpt)
                continue
            candidates = [rule.get("attribute_id")] if rule.get("attribute_id") else []
            fixed = placeholder_attribute(registry, candidates, excerpt)
            if rule.get("attribute_id") and not fixed:
                stats["attribute_cleared"] += 1
                if len(examples) < 20:
                    examples.append(f"清空屬性：{rule.get('attribute_id')} ← 「{excerpt[:40]}」")
                rule = {**rule, "attribute_id": ""}
            kept.append(rule)
        if len(kept) == len(rules) and all(a is b for a, b in zip(kept, rules)):
            continue
        changed += 1
        conditions = []
        for condition in row.get("conditions") or []:
            if condition.get("status") == "complex" and (condition.get("text") in dropped_texts or condition.get("excerpt") in dropped_texts):
                condition = {**condition, "status": "not_a_condition"}
            conditions.append(condition)
        if not dry:
            update = {"rules": kept, "conditions": conditions, "updated_at": utcnow()}
            update["index"] = Extractor.build_index({**row, "rules": kept})
            db.benefits.update_one({"_id": row["_id"]}, {"$set": update})
    print("records changed:", changed)
    for code, n in stats.most_common():
        print(f"  {n:>6}  {code}")
    for line in examples:
        print("   ", line)
    total_rules = sum(len(r.get("rules") or []) for r in db.benefits.find({}, {"rules": 1}))
    print("rules now:", total_rules)
    return 0


if __name__ == "__main__":
    sys.exit(main())
