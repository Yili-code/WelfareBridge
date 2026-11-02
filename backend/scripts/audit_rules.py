"""資料庫規則稽核：逐筆檢查補助的規則、金額、期間、狀態是否與原文一致，輸出問題清單（不修改資料庫）。

    python scripts/audit_rules.py --out /app/data/audit/static.json

檢查項目（severity：high＝幾乎確定有誤、med＝很可能有誤、low＝需要人看）：
  number_not_in_text   規則數值在原文找不到（high）
  direction_conflict   運算子方向與數字旁的用語相反，例如「70萬以下」卻是 ≥（high）
  misattributed_number 數字前面是利息／租金／存款等，卻被當成所得或年齡（high）
  implausible_value    數值不合理（年齡超出 0–120、成績超過 100、所得／財產過小）（med）
  evidence_not_in_text 引用的原文片段不在原文裡（med）
  residence_not_in_text 設籍／居住縣市規則的縣市沒有出現在原文、標題或機關（med）
  exclusion_no_cue     排除條件的原文沒有「不得／不予／已領」這類排除用語（low）
  date_order / status_conflict / amount_not_in_text / display_exponent
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import get_db, init_db  # noqa: E402
from app.services.extractor import closed_marker  # noqa: E402
from app.services.normalization import chinese_to_int, taiwan_today  # noqa: E402

NUM_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?|[零〇一二兩三四五六七八九十百千]+)\s*(萬|億|千)?")
BELOW = re.compile(r"^\s*(?:元|歲|分|個月|月|年|人|倍|%|％|級|萬元)?\s*(以下|以內|未滿|不超過|未達|低於|不逾|未逾|未超過|為限|以前)")
ABOVE = re.compile(r"^\s*(?:元|歲|分|個月|月|年|人|倍|%|％|級|萬元)?\s*(以上|年滿|已滿|至少|超過|高於|之後)")
BAD_BEFORE = re.compile(r"(利息|股利|租金|存款|本金|薪資|獎金|財產|不動產|房屋|土地|資產)\s*(?:所得|收入|價值|總額|公告現值)?\s*[:：為達逾約]?\s*(?:新臺幣|新台幣|NT\$)?\s*$")
EXCLUDE_CUE = re.compile(r"不得|不予|排除|除外|已領|已獲|重複|不適用|未曾|不在此限|不符|非|無法|禁止|不含")
NUMERIC_UNITS = {"TWD", "TWD_year", "TWD_month", "years", "months", "score", "percent", "multiple", "level", "gpa"}
INCOME_ATTRS = {"household.income_year", "household.income_month", "household.income_per_capita"}


def norm(text: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text or ""))


def numbers_in(text: str) -> set[float]:
    found: set[float] = set()
    for match in NUM_RE.finditer(text):
        token, unit = match.group(1), match.group(2)
        try:
            value = float(token.replace(",", "")) if token[0].isdigit() else chinese_to_int(token)
        except (ValueError, TypeError):
            continue
        if value is None:
            continue
        found.add(float(value))
        if unit == "萬":
            found.add(float(value) * 10_000)
        elif unit == "億":
            found.add(float(value) * 100_000_000)
        elif unit == "千":
            found.add(float(value) * 1000)
    return found


def has_value(values: set[float], target: float) -> bool:
    candidates = {target, target / 12, target * 12}
    return any(abs(v - c) <= 0.5 for v in values for c in candidates)


def token_positions(excerpt: str, value: float):
    """在片段裡找出等於 value 的數字（含「N萬」）及其結尾位置，用來看後面接的是以下還是以上。"""
    for match in NUM_RE.finditer(excerpt):
        token, unit = match.group(1), match.group(2)
        try:
            number = float(token.replace(",", "")) if token[0].isdigit() else chinese_to_int(token)
        except (ValueError, TypeError):
            continue
        if number is None:
            continue
        number = float(number) * {"萬": 10_000, "億": 100_000_000, "千": 1000}.get(unit or "", 1)
        if abs(number - value) <= 0.5 or abs(number - value / 12) <= 0.5 or abs(number - value * 12) <= 0.5:
            yield match


def audit(record: dict) -> list[dict]:
    issues: list[dict] = []
    title = record.get("title", "")
    text = norm(record.get("original_text", "")) + norm(title)
    values = numbers_in(unicodedata.normalize("NFKC", record.get("original_text", "") + " " + title))

    def add(check: str, severity: str, detail: str, rule: dict | None = None):
        issues.append({"id": record["_id"], "title": title[:60], "check": check, "severity": severity, "detail": detail,
                       "rule_id": (rule or {}).get("id", ""), "attribute": (rule or {}).get("attribute_id", "")})

    for rule in record.get("rules", []):
        attribute, operator, value = rule.get("attribute_id", ""), rule.get("operator", ""), rule.get("value")
        excerpt = unicodedata.normalize("NFKC", (rule.get("evidence") or {}).get("excerpt", ""))
        human = rule.get("human_readable", "")
        if re.search(r"\d[eE]\+\d|nan|None", human):
            add("display_exponent", "med", human, rule)
        if excerpt and norm(excerpt)[:40] not in text and rule.get("evidence", {}).get("extractor") != "llm":
            add("evidence_not_in_text", "med", excerpt[:80], rule)
        if rule.get("unit") in NUMERIC_UNITS and isinstance(value, (int, float)) and not isinstance(value, bool):
            if not has_value(values, float(value)):
                add("number_not_in_text", "high", f"{human}（值 {value}）", rule)
            if attribute == "applicant.age" and not (0 <= value <= 120):
                add("implausible_value", "med", f"年齡 {value}", rule)
            if rule.get("unit") == "score" and not (0 <= value <= 100):
                add("implausible_value", "med", f"成績 {value}", rule)
            if attribute == "household.income_year" and 0 < value < 100_000:
                add("implausible_value", "med", f"家庭年所得上限只有 {value:g}", rule)
            if attribute == "household.assets" and 0 < value < 100_000:
                add("implausible_value", "med", f"家庭財產上限只有 {value:g}", rule)
            for match in token_positions(excerpt, float(value)):
                after, before = excerpt[match.end():match.end() + 8], excerpt[max(0, match.start() - 12):match.start()]
                if attribute in INCOME_ATTRS | {"household.assets", "applicant.age"} and BAD_BEFORE.search(before) and not (attribute == "household.assets" and re.search(r"財產|不動產|資產|存款", before)):
                    add("misattributed_number", "high", f"「…{before}{match.group(0)}」被當成 {attribute}", rule)
                below, above = BELOW.search(after), ABOVE.search(after)
                if below and operator in {">=", ">"} and not rule.get("role") == "exclusion":
                    add("direction_conflict", "high", f"原文「{match.group(0)}{after[:4]}」但規則是 {operator}", rule)
                elif above and operator in {"<=", "<"} and not rule.get("role") == "exclusion":
                    add("direction_conflict", "high", f"原文「{match.group(0)}{after[:4]}」但規則是 {operator}", rule)
                break
        if attribute in {"residence.household_city", "residence.current_city"} and operator in {"in", "=", "contains"}:
            cities = value if isinstance(value, list) else [value]
            context = norm(f"{title}{record.get('provider', '')}{record.get('provider_region', '')}") + text
            for city in cities:
                if city and city not in context and city.replace("臺", "台") not in context:
                    add("residence_not_in_text", "med", f"{attribute} 含 {city}，原文沒有", rule)
        if rule.get("role") == "exclusion" and excerpt and not EXCLUDE_CUE.search(excerpt):
            add("exclusion_no_cue", "low", f"{human}｜{excerpt[:60]}", rule)

    benefit = record.get("benefit") or {}
    period = benefit.get("application_period") or {}
    start, end = period.get("start_date") or "", period.get("end_date") or ""
    today = taiwan_today().isoformat()
    status = record.get("status", "active")
    if start and end and end < start:
        add("date_order", "high", f"{start} ~ {end}")
    closed = closed_marker(title, record.get("original_text", ""))
    if status == "active" and ((end and end < today) or closed):
        add("status_conflict", "high", f"狀態 active，但{'截止日 ' + end if end and end < today else '原文標示 ' + closed}")
    if status == "expired" and not closed and (not end or end >= today):
        add("status_conflict", "med", f"狀態 expired，但截止日 {end or '無'}、原文沒有停辦用語")
    amount = benefit.get("amount") or {}
    for key in ("value", "min", "max"):
        v = amount.get(key)
        if isinstance(v, (int, float)) and v and amount.get("unit") == "TWD" and not has_value(values, float(v)):
            add("amount_not_in_text", "med", f"金額 {key}={v:g}")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/audit/static.json")
    parser.add_argument("--include-expired", action="store_true")
    args = parser.parse_args()
    init_db()
    query = {"is_canonical": True, "record_kind": {"$ne": "portal"}}
    if not args.include_expired:
        query["status"] = {"$ne": "expired"}
    issues: list[dict] = []
    records = 0
    for record in get_db().benefits.find(query):
        records += 1
        issues.extend(audit(record))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"records": records, "issues": issues}, ensure_ascii=False, indent=1), encoding="utf-8")
    by = Counter((i["check"], i["severity"]) for i in issues)
    print(f"稽核 {records} 筆，問題 {len(issues)} 項（涉及 {len({i['id'] for i in issues})} 筆補助）")
    for (check, severity), n in sorted(by.items(), key=lambda kv: (kv[0][1] != 'high', -kv[1])):
        print(f"  {severity:4} {check:24} {n}")


if __name__ == "__main__":
    main()
