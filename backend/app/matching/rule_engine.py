"""Deterministic Rule Engine v2：一條規則 + 使用者資料 → match / not_match / unknown。

- 使用者沒填的屬性 → unknown（資料不足），絕不判成不符合。
- complexity=complex 的規則 → unknown（交給本地 AI 或人工），理由標明「需語意判斷」。
- 型態依登錄表：number（含 between）、boolean、enum（有序 enum 可 >= <=）、multi_enum、city、identity.tags（含本體 implies 展開）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..registry import Registry, get_registry
from ..services.normalization import normalize_city
from .profile import Profile


@dataclass
class RuleEvaluation:
    status: str  # match | not_match | unknown
    reason: str
    user_value: Any = None


def _num(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compare(actual: float, operator: str, target: Any) -> bool | None:
    if operator == "between":
        if not (isinstance(target, list) and len(target) == 2):
            return None
        low, high = _num(target[0]), _num(target[1])
        if low is None or high is None:
            return None
        return low <= actual <= high
    number = _num(target)
    if number is None:
        return None
    return {">": actual > number, ">=": actual >= number, "<": actual < number, "<=": actual <= number, "=": actual == number, "!=": actual != number}.get(operator)


def evaluate_rule(rule: dict, profile: Profile, registry: Registry | None = None) -> RuleEvaluation:
    registry = registry or get_registry()
    attribute_id = rule.get("attribute_id", "")
    operator = rule.get("operator", "")
    expected = rule.get("value")
    attribute = registry.get(attribute_id)
    if rule.get("complexity") == "complex":
        return RuleEvaluation("unknown", "此條件需要語意判斷（本地 AI 輔助或人工確認）")
    if attribute is None:
        return RuleEvaluation("unknown", f"屬性 {attribute_id} 不在登錄表")
    if operator not in attribute.allowed_operators:
        return RuleEvaluation("unknown", f"operator {operator} 與屬性型態不相容")
    user_value = profile.value(attribute_id, registry)
    enum_candidates = profile.preferences.get('enum_candidates')
    candidates = enum_candidates.get(attribute_id) if isinstance(enum_candidates, dict) else None
    if user_value is None and attribute.type == 'enum' and isinstance(candidates, list) and candidates:
        if any(value not in attribute.value_list for value in candidates):
            return RuleEvaluation('unknown', '教育階段範圍需確認')
        outcomes = []
        for value in candidates:
            possible = Profile.from_dict(profile.to_dict(), registry)
            possible.set(attribute_id, value)
            outcomes.append(evaluate_rule(rule, possible, registry).status)
        status = outcomes[0] if len(set(outcomes)) == 1 else 'unknown'
        return RuleEvaluation(status, {'match': '已填範圍全部符合此條件', 'not_match': '已填範圍均不符合此條件', 'unknown': '已知大致教育階段，仍需確認確切學制'}[status], candidates)
    if user_value is None or (isinstance(user_value, list) and not user_value and attribute_id != "identity.tags"):
        return RuleEvaluation("unknown", "你尚未提供此資料", None)
    if operator == "exists":
        return RuleEvaluation("match", "已提供此資料", user_value)

    # ---- 身分標籤（含本體展開）
    if attribute_id == "identity.tags":
        tags = set(user_value)
        wanted = set(expected if isinstance(expected, list) else [expected])
        if operator == "contains":
            ok = expected in tags
            label = registry.tags[expected].label if expected in registry.tags else str(expected)
            return RuleEvaluation("match" if ok else "not_match", "具備此身分" if ok else f"未具備「{label}」身分", sorted(tags))
        if operator == "in":
            ok = bool(tags & wanted)
            return RuleEvaluation("match" if ok else "not_match", "具備其中一種身分" if ok else "未具備所列身分", sorted(tags))
        if operator == "not_in":
            ok = not (tags & wanted)
            return RuleEvaluation("match" if ok else "not_match", "不在排除身分內" if ok else "屬於排除身分", sorted(tags))
        return RuleEvaluation("unknown", f"身分欄位不支援 operator {operator}")

    # ---- 數值
    if attribute.type == "number":
        actual = _num(user_value)
        if actual is None:
            return RuleEvaluation("unknown", "無法以數值比較", user_value)
        outcome = _compare(actual, operator, expected)
        if outcome is None:
            return RuleEvaluation("unknown", "規則缺少可比較的數值", user_value)
        symbol = {">": ">", ">=": "≥", "<": "<", "<=": "≤", "=": "=", "!=": "≠", "between": "介於"}[operator]
        target_text = f"{expected[0]:g}～{expected[1]:g}" if operator == "between" else f"{_num(expected):g}"
        return RuleEvaluation("match" if outcome else "not_match", f"你的資料 {actual:g} {'符合' if outcome else '不符合'} {symbol} {target_text}", user_value)

    # ---- 布林
    if attribute.type == "boolean":
        expected_bool = bool(expected)
        equal = bool(user_value) == expected_bool
        ok = equal if operator == "=" else not equal
        return RuleEvaluation("match" if ok else "not_match", "相符" if ok else ("需要具備此條件" if expected_bool else "屬於排除對象"), user_value)

    # ---- 有序 enum 比較
    if attribute.type == "enum" and operator in {">", ">=", "<", "<="}:
        actual_rank, target_rank = registry.enum_rank(attribute_id, user_value), registry.enum_rank(attribute_id, expected)
        if actual_rank is None or target_rank is None:
            return RuleEvaluation("unknown", "無法比較等級", user_value)
        outcome = _compare(float(actual_rank), operator, float(target_rank))
        return RuleEvaluation("match" if outcome else "not_match", f"你的等級為「{attribute.value_label(user_value)}」，條件為「{attribute.value_label(expected)}」{'以上' if operator in {'>', '>='} else '以下'}", user_value)

    # ---- 集合／相等
    def normalize(v: Any) -> Any:
        if attribute.type == "city" and isinstance(v, str):
            return normalize_city(v) or v
        return str(v).strip().lower() if isinstance(v, str) else v

    if operator in {"in", "not_in"}:
        options = {normalize(o) for o in (expected if isinstance(expected, list) else [expected])}
        if isinstance(user_value, list):
            hit = bool({normalize(v) for v in user_value} & options)
        else:
            hit = normalize(user_value) in options
        ok = hit if operator == "in" else not hit
        return RuleEvaluation("match" if ok else "not_match", "符合所列選項" if hit else "不在所列選項內", user_value)
    if operator == "contains":
        values = user_value if isinstance(user_value, list) else [user_value]
        ok = normalize(expected) in {normalize(v) for v in values}
        return RuleEvaluation("match" if ok else "not_match", "包含" if ok else "不包含", user_value)
    if operator in {"=", "!="}:
        equal = normalize(user_value) == normalize(expected)
        ok = equal if operator == "=" else not equal
        return RuleEvaluation("match" if ok else "not_match", "相符" if equal else "不相符", user_value)
    return RuleEvaluation("unknown", f"不支援的 operator：{operator}")
