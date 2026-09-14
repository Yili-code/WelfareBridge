"""追問規劃 v2：期望資訊增益。

動態模式（dynamic）：
    1. 對目前 profile 跑一次 matching（由呼叫端提供 items）。
    2. 只看還有機會的補助（possible_match / insufficient_data）：收集每筆缺的屬性（missing_attributes）。
    3. 對每個缺的屬性 a，模擬每種可能回答 v（布林：是/否；enum：各值；城市：規則裡出現的縣市 + 其他；數值：規則門檻上下）：
       重新評估相關候選 → 狀態翻轉（possible→high 或 →not_match）的候選以其分數加權 → gain(a) = 平均翻轉量
    4. hard_filter 屬性 ×2；sensitivity=high ×0.7；已回答／已跳過排除；同增益依 ask_priority。
逐步模式（step）：依 ask_priority 由高到低、只問候選補助用得到的屬性。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..registry import Attribute, Registry, get_registry
from .engine import MatchItem, MatchingEngine
from .profile import Profile


@dataclass
class Question:
    attribute_id: str
    question: str
    type: str
    options: list[dict] = field(default_factory=list)
    reason: str = ""
    help: str = ""
    priority: float = 0.0
    affected: int = 0
    sensitivity: str = "low"

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def _simulated_answers(attribute: Attribute, records: list[dict]) -> list[Any]:
    if attribute.type == "boolean":
        return [True, False]
    if attribute.type == "enum":
        return [v.get("value") for v in attribute.values][:10]
    if attribute.type == "multi_enum":
        return [[v.get("value")] for v in attribute.values][:8] + [[]]
    if attribute.type == "city":
        cities: list[str] = []
        for record in records:
            for rule in record.get("rules") or []:
                if rule.get("attribute_id") == attribute.id and isinstance(rule.get("value"), list):
                    cities.extend(c for c in rule["value"] if c not in cities)
        return cities[:8] + ["__other__"]
    if attribute.type == "number":
        thresholds: list[float] = []
        for record in records:
            for rule in record.get("rules") or []:
                if rule.get("attribute_id") == attribute.id:
                    value = rule.get("value")
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        thresholds.append(float(value))
                    elif isinstance(value, list):
                        thresholds.extend(float(v) for v in value if isinstance(v, (int, float)))
        if not thresholds:
            return []
        thresholds = sorted(set(thresholds))
        answers = [thresholds[0] - 1]
        for t in thresholds:
            answers.append(t)
            answers.append(t + 1)
        return answers[:12]
    return []


def plan_questions(profile: Profile, items: list[MatchItem] | None, records: list[dict] | None, *, mode: str = "dynamic", max_questions: int = 3, engine: MatchingEngine | None = None, registry: Registry | None = None) -> dict:
    registry = registry or get_registry()
    engine = engine or MatchingEngine(registry=registry)
    skipped = set(profile.skipped)
    askable = {a.id: a for a in registry.askable() if a.id not in skipped and not profile.answered(a.id)}

    if mode == "step":
        candidate_domains = {i.domain for i in (items or []) if i.status != "not_match"} if items else set()
        relevant = [a for a in askable.values() if not candidate_domains or "all" in a.domains or candidate_domains & set(a.domains)]
        relevant.sort(key=lambda a: (-a.ask_priority, a.id))
        questions = [_question(a, 1.0, 0, "") for a in relevant[:max_questions]]
        return {"questions": [q.to_dict() for q in questions], "complete": not questions, "missing_attributes": [a.id for a in relevant], "candidate_count": len([i for i in (items or []) if i.status in {"possible_match", "insufficient_data"}])}

    items = items or []
    records = records or []
    by_id = {r["_id"]: r for r in records}
    candidates = [i for i in items if i.status in {"possible_match", "insufficient_data"} and not i.is_overview]
    needed: dict[str, list[MatchItem]] = {}
    for item in candidates:
        for attribute_id in item.missing_attributes:
            if attribute_id in askable and item not in needed.setdefault(attribute_id, []):
                needed[attribute_id].append(item)
    gains: list[tuple[str, float, int]] = []
    for attribute_id, affected in needed.items():
        attribute = askable[attribute_id]
        answers = _simulated_answers(attribute, [by_id[i.benefit_id] for i in affected if i.benefit_id in by_id])
        if not answers:
            gains.append((attribute_id, 0.1 * len(affected), len(affected)))
            continue
        total = 0.0
        for answer in answers:
            trial = Profile.from_dict(profile.to_dict(), registry)
            if answer == "__other__":
                trial.set(attribute_id, "澎湖縣" if attribute.type == "city" else answer, source="asked")
            else:
                trial.set(attribute_id, answer, source="asked")
            flipped = 0.0
            for item in affected:
                record = by_id.get(item.benefit_id)
                if record is None:
                    continue
                new_item = engine.match_one(record, trial, use_llm=False)
                if new_item.status != item.status:
                    flipped += max(item.eligibility_score, 0.2)
            total += flipped
        gain = total / len(answers)
        if attribute.hard_filter:
            gain *= 2.0
        if attribute.sensitivity == "high":
            gain *= 0.7
        gains.append((attribute_id, gain, len(affected)))
    gains.sort(key=lambda g: (-g[1], -askable[g[0]].ask_priority, g[0]))
    questions = []
    for attribute_id, gain, affected in gains[:max_questions]:
        attribute = askable[attribute_id]
        reason = f"有 {affected} 筆補助需要這項資料才能判斷"
        questions.append(_question(attribute, gain, affected, reason))
    return {"questions": [q.to_dict() for q in questions], "complete": not gains, "missing_attributes": [g[0] for g in gains], "candidate_count": len(candidates)}


def _question(attribute: Attribute, priority: float, affected: int, reason: str) -> Question:
    options: list[dict] = []
    if attribute.type in {"enum", "multi_enum"}:
        options = [{"value": v.get("value"), "label": v.get("label", v.get("value"))} for v in attribute.values]
    elif attribute.type == "boolean":
        options = [{"value": True, "label": "是"}, {"value": False, "label": "否"}]
    return Question(attribute_id=attribute.id, question=attribute.question or f"請提供：{attribute.label}", type=attribute.question_type(), options=options, reason=reason, help=attribute.help, priority=round(priority, 3), affected=affected, sensitivity=attribute.sensitivity)
