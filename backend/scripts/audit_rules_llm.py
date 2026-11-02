"""用本地 AI 逐筆對照原文複核規則，結果寫成 jsonl（可中斷續跑，已完成的會跳過）。不修改資料庫。

    python scripts/audit_rules_llm.py --out /app/data/audit/llm.jsonl [--limit N] [--only-title 關鍵字]

AI 只負責「提出疑點」：每個疑點必須附上原文引句，且引句要真的出現在原文裡，數值修正還要出現在原文數字裡，
否則視為 AI 幻覺丟棄。通過查核的疑點會標 verified=true，後續才能當成自動修正的依據。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db import get_db, init_db  # noqa: E402
from app.llm.factory import get_provider  # noqa: E402
from app.llm.provider import LLMError  # noqa: E402
from app.registry import get_registry  # noqa: E402
from audit_rules import norm, numbers_in  # noqa: E402

TYPES = ["wrong_value", "wrong_operator", "wrong_role", "wrong_group_logic", "not_supported_by_text", "missing_condition", "wrong_attribute"]
SCHEMA = {
    "type": "object",
    "properties": {"issues": {"type": "array", "items": {"type": "object", "properties": {
        "rule_index": {"type": ["integer", "null"]},
        "type": {"type": "string", "enum": TYPES},
        "quote": {"type": "string"},
        "explanation": {"type": "string"},
        "suggested_operator": {"type": ["string", "null"]},
        "suggested_value": {},
    }, "required": ["rule_index", "type", "quote", "explanation"]}}},
    "required": ["issues"],
}
SYSTEM = (
    "你是補助規則稽核員。使用者會給你一份補助公告原文，以及系統從原文抽出的結構化規則（編號、屬性、運算子、值、角色、群組）。"
    "請只找出『規則與原文不一致』的地方，每項都必須引用原文中的原句（quote 必須逐字出現在原文）。類型：\n"
    "wrong_value＝數值與原文不同（例如把利息所得上限當成家庭所得上限）；wrong_operator＝以上／以下／未滿方向相反；"
    "wrong_role＝原文是排除條件卻當成必要條件（或相反）；wrong_group_logic＝原文是『下列之一／或』卻被當成全部必備（或相反）；"
    "not_supported_by_text＝規則在原文找不到依據；missing_condition＝原文有明確的資格條件（身分、年齡、所得、地區、學制）規則沒有抽到；"
    "wrong_attribute＝屬性放錯。\n"
    "missing_condition 只限『申請人本身或家庭的資格條件』（身分、年齡、所得財產、設籍居住、學制成績、就業狀態）；"
    "應備文件、申請流程、核銷方式、補助金額與名額都不是資格條件，不要報。屬性是（複雜條件）的規則是留給人工確認的，不要評論它們。\n"
    "規則嚴格：不要猜測、不要挑剔措辭、不要重複同一件事；原文沒有明說的不要報。沒有問題就回傳 {\"issues\": []}。"
    "rule_index 填規則編號（missing_condition 填 null）。只輸出 JSON。"
)


def describe(record: dict, registry) -> str:
    lines = []
    for index, rule in enumerate(record.get("rules", [])):
        attribute = registry.get(rule.get("attribute_id"))
        label = attribute.label if attribute else rule.get("attribute_id") or "（複雜條件）"
        lines.append(f"[{index}] {label} {rule.get('operator')} {rule.get('value')}｜{rule.get('role')}｜群組 {rule.get('group_id')}｜依據：{(rule.get('evidence') or {}).get('excerpt', '')[:90]}")
    return "\n".join(lines) or "（沒有規則）"


def verify(issue: dict, text: str, numbers: set[float], rule_count: int) -> tuple[bool, str]:
    quote = norm(unicodedata.normalize("NFKC", issue.get("quote", "")))
    if len(quote) < 6 or quote not in text:
        return False, "引句不在原文"
    index = issue.get("rule_index")
    if issue["type"] != "missing_condition" and (not isinstance(index, int) or not 0 <= index < rule_count):
        return False, "規則編號無效"
    suggested = issue.get("suggested_value")
    if issue["type"] == "wrong_value" and isinstance(suggested, (int, float)) and not any(abs(n - float(suggested)) <= 0.5 for n in numbers):
        return False, "建議的數值不在原文"
    return True, ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/audit/llm.jsonl")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only-title", default="")
    args = parser.parse_args()
    init_db()
    provider = get_provider()
    if provider is None:
        raise SystemExit("本地 AI 未啟用")
    registry = get_registry()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(line)["id"] for line in out.read_text(encoding="utf-8").splitlines() if line.strip()} if out.exists() else set()
    query = {"is_canonical": True, "record_kind": {"$ne": "portal"}, "status": {"$ne": "expired"}}
    if args.only_title:
        query["title"] = {"$regex": args.only_title}
    records = [r for r in get_db().benefits.find(query, {"title": 1, "provider": 1, "original_text": 1, "rules": 1}) if r["_id"] not in done]
    if args.limit:
        records = records[: args.limit]
    print(f"待複核 {len(records)} 筆（已完成 {len(done)}）", flush=True)
    started = time.time()
    with out.open("a", encoding="utf-8") as handle:
        for position, record in enumerate(records, 1):
            text_raw = record.get("original_text", "")
            text = norm(unicodedata.normalize("NFKC", text_raw))
            numbers = numbers_in(unicodedata.normalize("NFKC", text_raw))
            user = f"補助名稱：{record['title']}\n機關：{record.get('provider', '')}\n\n【原文】\n{text_raw[:6000]}\n\n【系統抽出的規則】\n{describe(record, registry)}"
            row = {"id": record["_id"], "title": record["title"][:60], "issues": [], "dropped": 0, "error": ""}
            try:
                result = provider.complete_json(SYSTEM, user, json_schema=SCHEMA, max_tokens=1500, salvage=True)
                for issue in result.get("issues", []) if isinstance(result, dict) else []:
                    if not isinstance(issue, dict) or issue.get("type") not in TYPES:
                        row["dropped"] += 1
                        continue
                    ok, why = verify(issue, text, numbers, len(record.get("rules", [])))
                    if ok:
                        rule = record["rules"][issue["rule_index"]] if isinstance(issue.get("rule_index"), int) else {}
                        row["issues"].append({**issue, "rule_id": rule.get("id", ""), "attribute": rule.get("attribute_id", ""), "current": f"{rule.get('operator', '')} {rule.get('value', '')}"})
                    else:
                        row["dropped"] += 1
            except (LLMError, Exception) as exc:  # 單筆失敗不中斷整批
                row["error"] = str(exc)[:200]
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()
            if position % 20 == 0:
                rate = (time.time() - started) / position
                print(f"{position}/{len(records)}  平均 {rate:.1f}s／筆，預估剩 {rate * (len(records) - position) / 60:.0f} 分鐘", flush=True)


if __name__ == "__main__":
    main()
