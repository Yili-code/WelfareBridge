"""修正稽核（audit_rules.py／audit_rules_llm.py）確認過的系統性規則錯誤。預設只列出，加 --apply 才寫入；
被移除或修改的規則完整內容寫進 --log，可據此還原。

  age_after_18      「年滿18歲後才能提領」被讀成申請人年齡 ≥ 18（未來教育與發展帳戶），未成年的人反而被排除
  inferred_city     原文寫「無需／不限設籍」，卻有依機關推定的設籍縣市必要條件
  stateless_excl    「無國籍或未取得居留…」是受益對象之一，被當成排除條件
  income_interest   家庭年所得上限誤抓成年利息所得的 2 萬（已在抽取器修正，這裡修既有資料）

    python scripts/fix_known_rule_errors.py [--apply] [--log /app/data/audit/known_fixes.json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import get_db, init_db  # noqa: E402

AFTER_18 = re.compile(r"(年滿|滿|至|直到|繳存至)\s*18\s*歲(?:後|方得|始得|止)|滿18歲(?:後|方)|18歲後|十八歲後")
NO_RESIDENCE = re.compile(r"無需設籍|不限設籍|無須設籍|免設籍|不需設籍|不拘設籍|不以設籍")
EXCLUDE_CUE = re.compile(r"不得|不予|排除|除外|不適用|限|非")
FIXED_INCOME = {"title": "弱勢助學", "attribute": "household.income_year", "old": 20000.0, "new": 700000.0, "human": "家庭年所得 ≤ 700,000元／年"}


def decide(record: dict, rule: dict) -> tuple[str, dict | None] | None:
    attribute, excerpt = rule.get("attribute_id", ""), (rule.get("evidence") or {}).get("excerpt", "")
    text = record.get("original_text", "")
    title = record.get("title", "")
    # 這個帳戶的對象是未滿 18 歲的兒少，18 歲是「可以提領」的時間點，申請人 ≥ 18 歲不可能是資格條件
    if "未來教育與發展帳戶" in title and attribute == "applicant.age" and "18" in excerpt.replace("十八", "18") and (
            (rule.get("operator") in {">=", ">"} and rule.get("value") == 18) or (rule.get("role") == "exclusion" and rule.get("operator") in {"<", "<="})):
        return "age_after_18", None
    if attribute == "residence.household_city" and rule.get("role") == "required" and (NO_RESIDENCE.search(text) or NO_RESIDENCE.search(excerpt)) and "推定" in rule.get("human_readable", ""):
        return "inferred_city", None
    if attribute == "applicant.nationality" and rule.get("role") == "exclusion" and "無國籍" in excerpt and not EXCLUDE_CUE.search(excerpt.replace("無國籍", "")):
        return "stateless_excl", None
    if FIXED_INCOME["title"] in title and attribute == FIXED_INCOME["attribute"] and rule.get("value") == FIXED_INCOME["old"]:
        return "income_interest", {"operator": rule["operator"], "value": FIXED_INCOME["new"], "human_readable": FIXED_INCOME["human"]}
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--log", default="data/audit/known_fixes.json")
    args = parser.parse_args()
    init_db()
    db = get_db()
    log: list[dict] = []
    counts: Counter = Counter()
    touched: set[str] = set()
    for record in db.benefits.find({"is_canonical": True, "record_kind": {"$ne": "portal"}}):
        for rule in record.get("rules", []):
            verdict = decide(record, rule)
            if not verdict:
                continue
            kind, patch = verdict
            counts[kind] += 1
            touched.add(record["_id"])
            log.append({"id": record["_id"], "title": record["title"][:60], "kind": kind, "action": "modify" if patch else "remove", "rule": rule})
            if args.apply:
                if patch:
                    db.benefits.update_one({"_id": record["_id"], "rules.id": rule["id"]}, {"$set": {f"rules.$.{k}": v for k, v in patch.items()} | {"rules.$.evidence.audit_fix": kind}})
                else:
                    db.benefits.update_one({"_id": record["_id"]}, {"$pull": {"rules": {"id": rule["id"]}}})
    if args.apply:
        for benefit_id in touched:
            db.benefits.update_one({"_id": benefit_id}, {"$set": {"review.needs_review": True}, "$addToSet": {"review.reasons": "規則稽核修正（見 data/audit/known_fixes.json）"}})
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'已修正' if args.apply else '可修正（尚未寫入）'}：{sum(counts.values())} 條規則，涉及 {len(touched)} 筆補助")
    for kind, n in counts.items():
        print(f"  {kind:16} {n}")
    for item in log[:60]:
        print(f"  [{item['kind']}] {item['title'][:34]}｜{item['rule'].get('human_readable', '')[:40]}")


if __name__ == "__main__":
    main()
