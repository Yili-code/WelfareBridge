"""把稽核（audit_rules_llm.py）已通過查核、依據明確的錯誤自動修回資料庫；其餘留在清單，不動。

可自動修的只有兩類（其他類型如 AND／OR 邏輯、缺漏條件、規則無依據，都要人看）：
  wrong_value     規則數值錯：建議值必須出現在 AI 引用的原文句子裡，單位量級相同
  wrong_operator  方向相反：引句裡數字後面接的是以下／以上，且規則目前的數值確實等於那個數字

    python scripts/apply_audit_fixes.py --llm /app/data/audit/llm.jsonl            # 只列出會修什麼（預設）
    python scripts/apply_audit_fixes.py --llm /app/data/audit/llm.jsonl --apply    # 實際寫入
"""
from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db import get_db, init_db  # noqa: E402
from app.numfmt import fmt_num  # noqa: E402
from app.registry import get_registry  # noqa: E402
from audit_rules import ABOVE, BELOW, token_positions  # noqa: E402

SYMBOL = {">=": "≥", "<=": "≤", "<": "<", ">": ">"}
UNIT_LABEL = {"years": "歲", "months": "個月", "score": "分", "TWD": "元", "TWD_year": "元／年", "TWD_month": "元／月", "percent": "%", "level": "級", "multiple": "倍", "gpa": ""}
NUMERIC = set(UNIT_LABEL)


def plan_fix(issue: dict, rule: dict) -> dict | None:
    """回傳 {'value':…, 'operator':…} 要改的欄位；沒有把握就回傳 None。"""
    unit = rule.get("unit")
    current = rule.get("value")
    if unit not in NUMERIC or not isinstance(current, (int, float)) or isinstance(current, bool):
        return None
    quote = unicodedata.normalize("NFKC", issue.get("quote", ""))
    if issue["type"] == "wrong_value":
        suggested = issue.get("suggested_value")
        if not isinstance(suggested, (int, float)) or isinstance(suggested, bool) or suggested == current:
            return None
        if unit.startswith("TWD") and suggested < 1000:
            return None  # 「70」與「70萬」量級不同，不敢猜
        if not any(True for _ in token_positions(quote, float(suggested))):
            return None
        return {"value": float(suggested)}
    if issue["type"] == "wrong_operator":
        operator = issue.get("suggested_operator")
        if operator not in SYMBOL or operator == rule.get("operator"):
            return None
        for match in token_positions(quote, float(current)):
            after = quote[match.end(): match.end() + 8]
            if BELOW.search(after) and operator in {"<", "<="}:
                return {"operator": operator}
            if ABOVE.search(after) and operator in {">", ">="}:
                return {"operator": operator}
            break
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", default="data/audit/llm.jsonl")
    parser.add_argument("--log", default="data/audit/fixes.json")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    init_db()
    db = get_db()
    registry = get_registry()
    changes = []
    for line in Path(args.llm).read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        for issue in row["issues"]:
            if issue["type"] not in {"wrong_value", "wrong_operator"} or not issue.get("rule_id"):
                continue
            record = db.benefits.find_one({"_id": row["id"]})
            rule = next((r for r in (record or {}).get("rules", []) if r.get("id") == issue["rule_id"]), None)
            if not rule:
                continue
            fix = plan_fix(issue, rule)
            if not fix:
                continue
            before = {"operator": rule["operator"], "value": rule["value"], "human_readable": rule.get("human_readable", "")}
            operator, value = fix.get("operator", rule["operator"]), fix.get("value", rule["value"])
            attribute = registry.get(rule["attribute_id"])
            human = f"{attribute.label if attribute else rule['attribute_id']} {SYMBOL.get(operator, operator)} {fmt_num(value)}{UNIT_LABEL.get(rule.get('unit'), '')}"
            changes.append({"id": row["id"], "title": row["title"], "rule_id": rule["id"], "type": issue["type"], "before": before,
                            "after": {"operator": operator, "value": value, "human_readable": human}, "quote": issue["quote"][:120], "explanation": issue["explanation"][:120]})
            if args.apply:
                note = f"稽核修正：{before['human_readable']} → {human}"
                db.benefits.update_one(
                    {"_id": row["id"], "rules.id": rule["id"]},
                    {"$set": {"rules.$.operator": operator, "rules.$.value": value, "rules.$.human_readable": human, "rules.$.evidence.audit_fix": note, "review.needs_review": True},
                     "$addToSet": {"review.reasons": note}})
    Path(args.log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.log).write_text(json.dumps(changes, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'已修正' if args.apply else '可修正（尚未寫入）'} {len(changes)} 條規則")
    for change in changes:
        print(f"  {change['title'][:30]}｜{change['before']['human_readable']} → {change['after']['human_readable']}")


if __name__ == "__main__":
    main()
