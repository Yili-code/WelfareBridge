"""數出「邏輯上不可能成立」的資格規則：同一屬性的互斥條件被寫成多條必要規則、又分屬不同群組（＝AND）。

例：同時必須是低收入戶與中低收入戶、同時 age>=65 與 age>=55、同時設籍 A 縣與 B 市。
這種紀錄在媒合時永遠比對不上，是稽核代理回報最多的一類問題。

用法：
  python scripts/check_unsatisfiable_rules.py                 # 看目前資料庫
  python scripts/check_unsatisfiable_rules.py --seed <path>   # 看某個 seed_v2.json 快照（比較修正前後）
"""
from __future__ import annotations

import io
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.extractor import _conflicting_groups  # noqa: E402


def unsatisfiable_reasons(rules: list[dict]) -> list[str]:
    """同一屬性的必要條件分屬不同群組（AND）卻互斥 → 這筆永遠比對不上。"""
    from collections import defaultdict

    reasons: list[str] = []
    by_attribute: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for rule in rules or []:
        if rule.get("role") == "required" and rule.get("complexity") == "simple":
            by_attribute[rule.get("attribute_id", "")][rule.get("group_id", "")].append(rule)
    for attribute_id, rules_by_group in by_attribute.items():
        for left, right in _conflicting_groups(attribute_id, rules_by_group):
            left_values = [r.get("value") for r in rules_by_group[left]]
            right_values = [r.get("value") for r in rules_by_group[right]]
            reasons.append(f"{attribute_id} 同時必須 {left_values} 與 {right_values}")
    return reasons


def main() -> int:
    rows: list[dict]
    if "--seed" in sys.argv:
        path = sys.argv[sys.argv.index("--seed") + 1]
        payload = json.load(io.open(path, encoding="utf-8"))
        rows = [b for b in payload.get("benefits", []) if b.get("record_kind") == "program" and b.get("is_canonical", True)]
        label = os.path.basename(path)
    else:
        from app.db import get_db

        rows = list(get_db().benefits.find({"is_canonical": True, "record_kind": "program"}, {"title": 1, "rules": 1}))
        label = "目前資料庫"
    bad = []
    kinds = Counter()
    for row in rows:
        reasons = unsatisfiable_reasons(row.get("rules") or [])
        if reasons:
            bad.append((row.get("title", "")[:40], reasons))
            for reason in reasons:
                kinds[reason.split(" 同時")[0]] += 1
    print(f"{label}：{len(rows)} 筆方案，其中 {len(bad)} 筆（{len(bad) / max(len(rows), 1):.1%}）的必要條件互斥、永遠比對不上")
    for attribute_id, count in kinds.most_common(8):
        print(f"   {count:>4}  {attribute_id}")
    for title, reasons in bad[:12]:
        print(f"   - {title}：{reasons[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
