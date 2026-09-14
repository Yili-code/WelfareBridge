"""Schema Validator v2：任何解析結果（規則式或本地 AI）進 benefits 集合前都要通過這裡。

檢查：
- 規則：attribute_id 必在登錄表、operator 與屬性型態相容、value 型態與 enum 值合法、數值必在摘錄、摘錄必在原文
- evidence：摘錄必在原文
- benefit meta：列舉值、日期格式、金額為正數、名額為正整數
不通過的規則／欄位會被移除並記錄原因（review.reasons），整份只有在缺 title / source_url 時才拒絕。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..registry import get_registry
from .normalization import chinese_to_int, compact

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CN_NUM_RE = re.compile(r"[一二兩三四五六七八九十百千萬零〇]+")
BENEFIT_FORMS = {"cash", "waiver", "service", "in_kind", "voucher", "loan", "mixed"}
AWARD_BASIS = {"criteria", "competitive", "lottery", "first_come", "unknown"}
CHANNELS = {"school", "agency", "online", "mail", "unknown"}
EXCLUSIVE = {"public_funding", "government_benefit", "same_provider", "same_category", "any_other", "none"}
PROVIDER_TYPES = {"central_government", "local_government", "township", "school", "private_organization", "mixed", "unknown"}
ROLES = {"required", "exclusion", "bonus"}


@dataclass
class ValidationOutcome:
    ok: bool
    benefit: dict | None
    errors: list[str] = field(default_factory=list)
    dropped: list[str] = field(default_factory=list)
    review_reasons: list[str] = field(default_factory=list)


def excerpt_in_text(excerpt: str, original: str) -> bool:
    if not excerpt:
        return False
    needle = compact(excerpt)
    haystack = compact(original)
    if not needle:
        return False
    if needle in haystack:
        return True
    # 長摘錄可以是原文中幾句的拼接，但每一段都必須逐字存在（不接受改寫）
    segments = [compact(s) for s in re.split(r"[。；;\n]", excerpt) if compact(s)]
    segments = [s for s in segments if len(s) >= 6]
    return bool(segments) and all(s in haystack for s in segments)


def number_in_excerpt(value, excerpt: str) -> bool:
    if value is None or isinstance(value, (bool, dict, str)):
        return True
    if isinstance(value, list):
        return all(number_in_excerpt(v, excerpt) for v in value)
    try:
        number = float(value)
    except (TypeError, ValueError):
        return True
    text = compact(excerpt).replace(",", "").replace("，", "")
    candidates = {str(int(number)) if number == int(number) else str(number)}
    if number >= 10000 and number % 10000 == 0:
        candidates.add(f"{int(number // 10000)}萬")
    if number >= 1000 and number % 1000 == 0 and number < 10000:
        candidates.add(f"{int(number // 1000)}千")
    if number == int(number) and number % 12 == 0 and number >= 12:
        candidates.add(f"{int(number // 12)}年")
    if any(candidate in text for candidate in candidates):
        return True
    for chunk in CN_NUM_RE.findall(excerpt or ""):
        parsed = chinese_to_int(chunk)
        if parsed is not None and (parsed == number or parsed * 12 == number or parsed * 10000 == number):
            return True
    return False


def _value_ok(attribute, operator: str, value) -> tuple[bool, str]:
    if operator == "exists":
        return True, ""
    if value is None:
        return False, "缺少 value"
    kind = attribute.type
    if kind == "number":
        if operator == "between":
            return (isinstance(value, list) and len(value) == 2 and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in value)), "between 需要兩個數值"
        return (isinstance(value, (int, float)) and not isinstance(value, bool)), "數值型態錯誤"
    if kind == "boolean":
        return isinstance(value, bool), "布林型態錯誤"
    if kind in {"enum", "multi_enum"}:
        allowed = set(attribute.value_list)
        values = value if isinstance(value, list) else [value]
        bad = [v for v in values if str(v) not in allowed]
        return (not bad), f"enum 值不在允許清單：{bad[:3]}"
    if kind == "city":
        from .normalization import CITIES

        values = value if isinstance(value, list) else [value]
        bad = [v for v in values if v not in CITIES]
        return (not bad), f"縣市名稱不合法：{bad[:3]}"
    if kind == "date":
        values = value if isinstance(value, list) else [value]
        return all(isinstance(v, str) and DATE_RE.match(v) for v in values), "日期格式錯誤"
    return True, ""


def validate_benefit(benefit: dict, original_text: str | None = None) -> ValidationOutcome:
    registry = get_registry()
    errors: list[str] = []
    dropped: list[str] = []
    original = original_text if original_text is not None else benefit.get("original_text", "")
    if not (benefit.get("title") or "").strip():
        errors.append("缺少 title")
    if not (benefit.get("source") or {}).get("source_url"):
        errors.append("缺少 source_url（沒有來源 URL 的資料不得進正式資料庫）")
    if errors:
        return ValidationOutcome(ok=False, benefit=None, errors=errors)

    review = list((benefit.get("review") or {}).get("reasons") or [])
    if benefit.get("provider_type") not in PROVIDER_TYPES:
        review.append(f"provider_type 非法值 {benefit.get('provider_type')!r}，改為 unknown")
        benefit["provider_type"] = "unknown"
    if benefit.get("category") and not registry.category(benefit["category"]):
        review.append(f"category {benefit['category']!r} 不在 taxonomy，清空")
        benefit["category"] = ""
        benefit["domain"] = ""
    if benefit.get("status") not in {"active", "expired", "needs_review", "superseded"}:
        benefit["status"] = "active"

    meta = benefit.setdefault("benefit", {})
    if meta.get("benefit_form") not in BENEFIT_FORMS:
        dropped.append(f"benefit_form 非法值 {meta.get('benefit_form')!r}")
        meta["benefit_form"] = "cash"
    if meta.get("award_basis") not in AWARD_BASIS:
        meta["award_basis"] = "unknown"
    application = meta.setdefault("application", {})
    if application.get("channel") not in CHANNELS:
        application["channel"] = "unknown"
    meta["exclusive_with"] = [v for v in (meta.get("exclusive_with") or []) if v in EXCLUSIVE] or ["none"]
    if meta.get("quota") is not None and (not isinstance(meta["quota"], int) or meta["quota"] <= 0):
        dropped.append(f"quota 非正整數：{meta['quota']!r}")
        meta["quota"] = None
    period = meta.setdefault("application_period", {})
    for attr in ("start_date", "end_date"):
        value = period.get(attr) or ""
        if value and not DATE_RE.match(value):
            dropped.append(f"application_period.{attr}={value!r} 不是 YYYY-MM-DD")
            period[attr] = ""
    amount = meta.setdefault("amount", {})
    for attr in ("value", "min", "max"):
        value = amount.get(attr)
        if value is not None and (not isinstance(value, (int, float)) or value <= 0):
            dropped.append(f"amount.{attr}={value!r} 非正數")
            amount[attr] = None
    if amount.get("min") is not None and amount.get("max") is not None and amount["min"] > amount["max"]:
        amount["min"], amount["max"] = amount["max"], amount["min"]

    kept_evidence = []
    for item in benefit.get("evidence") or []:
        item["confidence"] = max(0.0, min(1.0, float(item.get("confidence", 0.5))))
        excerpt = item.get("excerpt") or ""
        if excerpt and original and not excerpt_in_text(excerpt, original):
            dropped.append(f"evidence[{item.get('field')}] 摘錄不在原文：{excerpt[:40]}")
            continue
        kept_evidence.append(item)
    benefit["evidence"] = kept_evidence

    kept_rules = []
    for rule in benefit.get("rules") or []:
        attribute_id = rule.get("attribute_id", "")
        attribute = registry.get(attribute_id)
        rule["confidence"] = max(0.0, min(1.0, float(rule.get("confidence", 0.5))))
        rule.setdefault("role", "required")
        rule.setdefault("complexity", "simple")
        rule.setdefault("group_logic", "any")
        if rule["role"] not in ROLES:
            rule["role"] = "required"
        if attribute is None:
            if rule.get("operator") == "exists" and not attribute_id:
                # 佔位規則：有一條無法量化的條件，沒有對應屬性是正常的（媒合時歸為需語意判斷）
                rule["complexity"] = "complex"
                kept_rules.append(rule)
                continue
            dropped.append(f"rule[{attribute_id}] 不在屬性登錄表")
            continue
        operator = rule.get("operator", "")
        if operator not in attribute.allowed_operators:
            dropped.append(f"rule[{attribute_id}] operator {operator!r} 與型態 {attribute.type} 不相容")
            continue
        excerpt = (rule.get("evidence") or {}).get("excerpt", "")
        if not excerpt:
            dropped.append(f"rule[{attribute_id}] 缺少原文摘錄")
            continue
        if original and not excerpt_in_text(excerpt, original):
            dropped.append(f"rule[{attribute_id}] 摘錄不在原文：{excerpt[:40]}")
            continue
        if rule["complexity"] == "complex":
            kept_rules.append(rule)
            continue
        ok, reason = _value_ok(attribute, operator, rule.get("value"))
        if not ok:
            dropped.append(f"rule[{attribute_id}] {reason}")
            continue
        if attribute.type == "number" and not number_in_excerpt(rule.get("value"), excerpt):
            dropped.append(f"rule[{attribute_id}] 數值 {rule.get('value')} 未出現在摘錄：{excerpt[:40]}")
            continue
        kept_rules.append(rule)
    benefit["rules"] = kept_rules

    if dropped:
        review.append(f"驗證時移除 {len(dropped)} 個欄位／規則")
        review.extend(dropped[:12])
    benefit.setdefault("review", {})
    benefit["review"]["reasons"] = review
    benefit["review"]["needs_review"] = bool(benefit["review"].get("needs_review") or dropped or not any(r["complexity"] == "simple" for r in kept_rules))
    benefit["confidence"] = max(0.0, min(1.0, float(benefit.get("confidence", 0.5))))
    return ValidationOutcome(ok=True, benefit=benefit, errors=[], dropped=dropped, review_reasons=review)
