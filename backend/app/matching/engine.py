"""Matching Engine v2：使用者資料 × 所有補助規則 → 可解釋的媒合結果。

每筆補助：
    規則依 group_id 分組；同組 OR、不同組 AND；role=bonus 的規則不參與資格判定（只加分）。
    group 狀態：任一 match → match；否則有 unknown → unknown；否則 not_match。
    - 任一「可拒絕」的 simple group not_match → not_match（🔴 目前不符合）
      可拒絕 = 規則 confidence ≥ REJECT_MIN_CONFIDENCE 且 inferred=false；否則該 not_match 降為 unknown 並標「推定條件，請確認」
    - 全部 simple group match、沒有 unknown → high_match（🟢 高度符合；已符合群組的鑑別力權重總和需 ≥ 2.5）
    - 有 match 也有 unknown → possible_match（🟡 可能符合）
    - 沒有任何 match → insufficient_data（⚪ 資料不足）
    eligibility_score = Σ(match 權重 × confidence) + 0.5 × Σ unknown 權重，除以 Σ 權重；權重依鑑別力（戶籍／身分 2.0 … 教育階段 0.5）。
complex 條件在本地 AI 可用時交給 AI 判斷（只能升級為 match 或維持 unknown；AI 的 not_match 只降為 possible_match）。

已建立資格骨幹（record["eligibility_core"]，見 eligibility_core.py）的補助改用分層：
    - 確認過的骨幹條件不符 → not_match（tier hidden）
    - 骨幹涵蓋的屬性（戶籍、年齡、學制、身分…）的逐條規則不再單獨排除，只提示「需確認」；其他屬性的可拒絕規則照舊
    - 骨幹全部符合且至少一項有鑑別力、其他規則沒有不符 → high_match（tier1 ✅ 符合）
    - 其他 → possible_match（tier2 🟡 可能符合・需補充資料），needs 列出要補的欄位
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from ..config import Settings, get_settings
from ..registry import Registry, get_registry
from .eligibility_core import CoreOutcome, evaluate_core
from .profile import Profile
from .rule_engine import evaluate_rule

log = logging.getLogger(__name__)

STATUS_ORDER = {"high_match": 0, "possible_match": 1, "insufficient_data": 2, "not_match": 3}
TIER_ORDER = {"tier1": 0, "tier2": 1, "hidden": 2}
# 骨幹已涵蓋的屬性：這些屬性的逐條規則常抽錯（本縣／外縣市、推定身分…），有骨幹時不再單獨排除
CORE_ATTRIBUTES = {
    "residence.household_city", "residence.current_city", "education.school_city", "applicant.age", "applicant.is_elderly", "family.youngest_child_age",
    "education.level", "applicant.is_student", "identity.tags", "applicant.nationality", "applicant.gender", "employment.status", "employment.involuntary_separation",
    "housing.tenure", "care.needs_care", "care.is_primary_caregiver",
}


def has_core(record: dict) -> bool:
    return isinstance(record.get("eligibility_core"), dict) and isinstance(record["eligibility_core"].get("facets"), list)


FACET_ATTRIBUTES = {
    "residence": {"residence.household_city", "residence.current_city", "education.school_city"},
    "age": {"applicant.age", "applicant.is_elderly", "family.youngest_child_age"},
    "education": {"education.level", "applicant.is_student"},
    "student": {"applicant.is_student", "education.level"},
    "nationality": {"applicant.nationality"},
}


def _violated_attributes(outcome: CoreOutcome, registry: Registry) -> set[str]:
    """已確認不符的骨幹條件涵蓋哪些屬性：這些屬性上不符的逐條規則照實列為「不符合」，讓使用者看得到原因。"""
    out: set[str] = set()
    for result in outcome.violated_confirmed:
        kind = result.facet.get("kind")
        if kind in {"identity_any", "identity_exclude"}:
            out.add("identity.tags")
            out.update(a for a in (registry.tag_attribute(t) for t in result.facet.get("tags") or []) if a)
        elif kind == "attr":
            out.add(result.facet.get("attribute_id", ""))
        else:
            out.update(FACET_ATTRIBUTES.get(kind, set()))
    return out


def _core_attribute(attribute_id: str, registry: Registry) -> bool:
    if attribute_id in CORE_ATTRIBUTES:
        return True
    return any(tag.attribute == attribute_id for tag in registry.tags.values())


GROUP_WEIGHTS: list[tuple[str, float]] = [
    ("residence", 2.0), ("identity", 2.0), ("exclusion_identity", 2.0), ("disability", 2.0), ("care_cms", 2.0), ("care_needs", 2.0), ("household_income", 1.5), ("household", 1.5), ("employment", 1.5), ("housing", 1.5), ("family", 1.5),
    ("academic", 1.0), ("applicant_age", 1.0), ("family_youngest", 1.0), ("residence_duration", 1.0), ("program_type", 1.0), ("exclusion", 1.0), ("financial", 1.0), ("care", 1.0),
    ("education", 0.5), ("applicant", 0.7), ("complex", 0.5),
]
MIN_HIGH_MATCH_WEIGHT = 2.5


def concrete_attributes(result: "ConditionResult", registry: Registry) -> list[str]:
    """identity.tags（虛擬屬性）→ 對應的具體布林屬性；其他屬性原樣。"""
    if result.attribute_id != "identity.tags":
        return [result.attribute_id]
    values = result.value if isinstance(result.value, list) else [result.value]
    ids: list[str] = []
    for tag_id in values:
        attribute = registry.tag_attribute(str(tag_id))
        if attribute and attribute not in ids:
            ids.append(attribute)
    return ids or ["identity.tags"]


def group_weight(group_id: str, is_complex: bool) -> float:
    if is_complex:
        return 0.5
    for prefix, weight in GROUP_WEIGHTS:
        if group_id == prefix or group_id.startswith(prefix):
            return weight
    return 1.0


@dataclass
class ConditionResult:
    rule_id: str
    attribute_id: str
    operator: str
    value: Any
    unit: str
    group_id: str
    role: str
    human_readable: str
    excerpt: str
    status: str
    reason: str
    user_value: Any = None
    complexity: str = "simple"
    inferred: bool = False
    confidence: float = 1.0
    llm_used: bool = False
    rejectable: bool = True

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class MatchItem:
    benefit_id: str
    canonical_id: str
    title: str
    domain: str
    category: str
    category_label: str
    provider: str
    provider_type: str
    benefit: dict
    source_url: str
    source_name: str
    status: str
    eligibility_score: float
    matched: list[ConditionResult] = field(default_factory=list)
    missing: list[ConditionResult] = field(default_factory=list)
    failed: list[ConditionResult] = field(default_factory=list)
    complex: list[ConditionResult] = field(default_factory=list)
    bonus: list[ConditionResult] = field(default_factory=list)
    missing_attributes: list[str] = field(default_factory=list)
    explanation: list[str] = field(default_factory=list)
    needs_review: bool = False
    llm_used: bool = False
    benefit_status: str = "active"
    is_overview: bool = False
    matched_weight: float = 0.0
    tier: str = "hidden"  # tier1 ✅ 符合 | tier2 🟡 可能符合・需補充資料 | hidden
    core: list[dict] = field(default_factory=list)  # 資格骨幹逐項判斷
    needs: list[str] = field(default_factory=list)  # 補哪些欄位可以確認（依重要性）
    needs_labels: list[str] = field(default_factory=list)
    core_built: bool = False

    def to_dict(self) -> dict:
        data = {k: v for k, v in self.__dict__.items() if k not in {"matched", "missing", "failed", "complex", "bonus"}}
        data.update({"matched_conditions": [c.to_dict() for c in self.matched], "missing_conditions": [c.to_dict() for c in self.missing], "failed_conditions": [c.to_dict() for c in self.failed], "complex_conditions": [c.to_dict() for c in self.complex], "bonus_conditions": [c.to_dict() for c in self.bonus]})
        return data


BENEFIT_PROJECTION = {"title": 1, "domain": 1, "category": 1, "category_label": 1, "provider": 1, "provider_type": 1, "provider_region": 1, "benefit": 1, "source": 1, "rules": 1, "status": 1, "review": 1, "is_overview": 1, "canonical_id": 1, "is_canonical": 1, "index": 1, "eligibility_core": 1, "original_text": 1}


def load_records(db, *, include_expired: bool = False, canonical_only: bool = True, domains: list[str] | None = None, categories: list[str] | None = None, with_text: bool = False) -> list[dict]:
    query: dict = {"record_kind": {"$ne": "portal"}, "classification.uncertain": {"$ne": True}}  # 彙整頁與分類待確認的紀錄不參與媒合
    if canonical_only:
        query["is_canonical"] = True
    if not include_expired:
        query["status"] = {"$ne": "expired"}
    if domains:
        query["domain"] = {"$in": domains}
    if categories:
        query["category"] = {"$in": categories}
    projection = dict(BENEFIT_PROJECTION)
    if not with_text:
        projection.pop("original_text")
    return list(db.benefits.find(query, projection))


def hard_filter_candidates(records: list[dict], profile: Profile, registry: Registry, settings: Settings) -> tuple[list[dict], list[dict]]:
    """候選檢索：只用使用者已確認的 hard_filter 屬性排除「確定不符」的補助；缺資料者保留。回傳 (候選, 被排除)。"""
    known = {aid for aid, item in profile.attributes.items() if item.value is not None and (item.confirmed or item.source in {"asked", "form"})}
    hard_ids = {a.id for a in registry.attributes.values() if a.hard_filter} & known
    kept, excluded = [], []
    for record in records:
        rejected = False
        core = has_core(record)
        if core and evaluate_core(record["eligibility_core"], profile, registry).violated_confirmed:
            excluded.append(record)  # 確認過的資格骨幹不符
            continue
        if not hard_ids:
            kept.append(record)
            continue
        for rule in record.get("rules") or []:
            if rule.get("attribute_id") not in hard_ids or rule.get("complexity") != "simple" or rule.get("role") == "bonus":
                continue
            if core and _core_attribute(rule.get("attribute_id", ""), registry):
                continue
            if float(rule.get("confidence", 0)) < settings.reject_min_confidence or rule.get("inferred"):
                continue
            evaluation = evaluate_rule(rule, profile, registry)
            if evaluation.status != "not_match":
                continue
            # 同群組若有其他規則可能成立（OR），不能只憑這條排除
            group_rules = [r for r in record.get("rules") or [] if r.get("group_id") == rule.get("group_id")]
            if any(evaluate_rule(r, profile, registry).status != "not_match" for r in group_rules if r is not rule):
                continue
            rejected = True
            break
        (excluded if rejected else kept).append(record)
    return kept, excluded


class MatchingEngine:
    def __init__(self, settings: Settings | None = None, registry: Registry | None = None, llm_judge: Callable[[dict, dict, str], dict | None] | None = None):
        self.settings = settings or get_settings()
        self.registry = registry or get_registry()
        self.llm_judge = llm_judge

    def match_all(self, records: list[dict], profile: Profile, *, use_llm: bool = False, llm_budget: int = 20, max_llm_rules_per_record: int = 3) -> list[MatchItem]:
        """llm_budget = 整個請求最多呼叫本地 AI 的次數（不是候選數）；每筆候選最多判斷 max_llm_rules_per_record 條複雜條件。"""
        items: list[MatchItem] = []
        # 先不用 AI 跑一輪，只對「可能符合」的前幾名補 AI 判斷（省時間）
        for record in records:
            items.append(self.match_one(record, profile, use_llm=False))
        if use_llm and self.llm_judge is not None and self.settings.llm_assist_matching:
            items.sort(key=self._sort_key)
            calls_left = llm_budget
            for index, item in enumerate(items):
                if calls_left <= 0:
                    break
                if item.status not in {"possible_match", "high_match"} or not item.complex:
                    continue
                record = next(r for r in records if r["_id"] == item.benefit_id)
                allowed = min(max_llm_rules_per_record, calls_left)
                items[index] = self.match_one(record, profile, use_llm=True, max_llm_rules=allowed)
                calls_left -= min(allowed, len(item.complex))
        items.sort(key=self._sort_key)
        return items

    @staticmethod
    def _sort_key(item: MatchItem):
        return (TIER_ORDER.get(item.tier, 9), STATUS_ORDER.get(item.status, 9), -item.eligibility_score, (item.benefit.get("application_period") or {}).get("end_date") or "9999")

    def match_one(self, record: dict, profile: Profile, *, use_llm: bool = False, max_llm_rules: int = 3) -> MatchItem:
        registry = self.registry
        groups: dict[str, list[ConditionResult]] = {}
        llm_used = False
        llm_calls = 0
        core_built = has_core(record)
        outcome: CoreOutcome | None = evaluate_core(record["eligibility_core"], profile, registry) if core_built else None
        confirmed_violations = _violated_attributes(outcome, registry) if outcome else set()
        for rule in record.get("rules") or []:
            evaluation = evaluate_rule(rule, profile, registry)
            covered = core_built and _core_attribute(rule.get("attribute_id", ""), registry) and rule.get("attribute_id") not in confirmed_violations
            rejectable = rule.get("complexity") == "simple" and float(rule.get("confidence", 0)) >= self.settings.reject_min_confidence and not rule.get("inferred") and not covered
            status, reason = evaluation.status, evaluation.reason
            if status == "not_match" and not rejectable:
                status, reason = "unknown", reason + ("（此項以資格骨幹判斷為準，細節請至官方公告確認）" if covered else "（此條件為推定或低信心抽取，請至官方公告確認）")
            result = ConditionResult(
                rule_id=rule.get("id", ""), attribute_id=rule.get("attribute_id", ""), operator=rule.get("operator", ""), value=rule.get("value"), unit=rule.get("unit", ""), group_id=rule.get("group_id") or rule.get("attribute_id", ""),
                role=rule.get("role", "required"), human_readable=rule.get("human_readable", ""), excerpt=(rule.get("evidence") or {}).get("excerpt", ""), status=status, reason=reason, user_value=evaluation.user_value,
                complexity=rule.get("complexity", "simple"), inferred=bool(rule.get("inferred")), confidence=float(rule.get("confidence", 1.0)), rejectable=rejectable,
            )
            if result.complexity == "complex" and use_llm and self.llm_judge is not None and llm_calls < max_llm_rules:
                llm_calls += 1
                try:
                    verdict = self.llm_judge(rule, profile.all_values(registry), record.get("original_text", ""))
                except Exception as exc:
                    log.warning("llm judge failed: %s", exc)
                    verdict = None
                if verdict and verdict.get("result") in {"match", "not_match", "unknown"}:
                    result.status = verdict["result"]
                    result.reason = verdict.get("reason", "") or result.reason
                    result.llm_used = True
                    result.confidence = float(verdict.get("confidence", 0.5))
                    llm_used = True
            groups.setdefault(result.group_id, []).append(result)

        matched, missing, failed, complex_conditions, bonus = [], [], [], [], []
        total_weight = match_weight = unknown_weight = 0.0
        simple_failed = simple_unknown = simple_matched = False
        matched_weight = 0.0
        llm_not_match = False
        for group_id, entries in groups.items():
            if all(r.role == "bonus" for r in entries):
                bonus.extend(entries)
                continue
            is_complex = all(r.complexity == "complex" for r in entries)
            weight = group_weight(group_id, is_complex)
            total_weight += weight
            statuses = [r.status for r in entries]
            if "match" in statuses:
                group_status = "match"
                match_weight += weight * max(r.confidence for r in entries if r.status == "match")
            elif "unknown" in statuses:
                group_status = "unknown"
                unknown_weight += weight
            else:
                group_status = "not_match"
            for result in entries:
                if result.complexity == "complex" and not result.llm_used:
                    complex_conditions.append(result)
                elif result.status == "match":
                    matched.append(result)
                elif result.status == "unknown":
                    missing.append(result)
                else:
                    failed.append(result)
            if is_complex:
                if group_status == "not_match":
                    llm_not_match = True
                continue
            if group_status == "not_match":
                simple_failed = True
            elif group_status == "unknown":
                simple_unknown = True
            else:
                simple_matched = True
                matched_weight += weight

        score = (match_weight + 0.5 * unknown_weight) / total_weight if total_weight else 0.0
        rules = [r for r in record.get("rules") or [] if r.get("role") != "bonus"]
        if record.get("is_overview"):
            status = "insufficient_data"
            score = 0.0
        elif not rules:
            status = "insufficient_data"
            score = 0.0
        elif simple_failed:
            status = "not_match"
        elif simple_matched and not simple_unknown:
            status = "high_match" if score >= self.settings.match_high_threshold and matched_weight >= MIN_HIGH_MATCH_WEIGHT else "possible_match"
            if llm_not_match:
                status = "possible_match"
        elif simple_matched:
            status = "possible_match"
        else:
            status = "insufficient_data"
        tier = "tier1" if status == "high_match" else "tier2" if status == "possible_match" else "hidden"

        if outcome is not None:
            if outcome.violated_confirmed or simple_failed:  # simple_failed 此時只剩骨幹以外屬性的可拒絕規則
                status, tier = "not_match", "hidden"
            elif not outcome.violated_uncertain and not outcome.unknown_confirmed and outcome.discriminating_confirmed:
                status, tier = "high_match", "tier1"
            else:
                status, tier = "possible_match", "tier2"
            if outcome.results:
                core_score = (len(outcome.satisfied) + 0.5 * len(outcome.unknown) + 0.3 * len(outcome.violated_uncertain)) / len(outcome.results)
                score = 0.7 * core_score + 0.3 * score

        satisfied = {gid for gid, entries in groups.items() if any(r.status == "match" for r in entries)}
        failed = [r for r in failed if r.group_id not in satisfied]
        missing = [r for r in missing if r.group_id not in satisfied]
        missing_attributes: list[str] = []
        for result in missing:
            if result.complexity == "complex":
                continue
            for attribute_id in concrete_attributes(result, registry):
                if attribute_id not in missing_attributes:
                    missing_attributes.append(attribute_id)
        needs = list(dict.fromkeys([*(outcome.needs() if outcome else []), *([] if core_built else missing_attributes)]))
        explanation = self._explain(status, matched, missing, failed, complex_conditions, bonus, record, matched_weight, outcome)
        source = record.get("source") or {}
        return MatchItem(
            benefit_id=record["_id"], canonical_id=record.get("canonical_id", record["_id"]), title=record.get("title", ""), domain=record.get("domain", ""), category=record.get("category", ""), category_label=record.get("category_label", ""),
            provider=record.get("provider", ""), provider_type=record.get("provider_type", ""), benefit=record.get("benefit") or {}, source_url=source.get("source_url", ""), source_name=source.get("source_name", ""),
            status=status, eligibility_score=round(score, 3), matched=matched, missing=missing, failed=failed, complex=complex_conditions, bonus=bonus, missing_attributes=missing_attributes, explanation=explanation,
            needs_review=bool((record.get("review") or {}).get("needs_review")), llm_used=llm_used, benefit_status=record.get("status", "active"),
            # 「彙整頁」偵測常把單一方案誤判（同頁列出多項補助名稱）；有骨幹時依骨幹分層，不再整筆藏起來（真正的入口頁 record_kind=portal 不會載入）
            is_overview=bool(record.get("is_overview")) and not core_built, matched_weight=round(matched_weight, 2),
            tier=tier, core=[r.to_dict() for r in outcome.results] if outcome else [], needs=needs, needs_labels=[registry.get(a).label if registry.get(a) else a for a in needs], core_built=core_built,
        )

    def _explain(self, status: str, matched, missing, failed, complex_conditions, bonus, record: dict, matched_weight: float, outcome: CoreOutcome | None = None) -> list[str]:
        registry = self.registry
        lines: list[str] = []
        if record.get("is_overview") and outcome is None:
            lines.append("此頁為彙整頁（同一頁列出多項補助），請由官方連結前往各項補助查看條件。")
            return lines
        if outcome is not None:
            # 資格骨幹在前（決定分層的依據），逐條規則只補充骨幹沒涵蓋的屬性
            icon = {"satisfied": "✓", "violated": "✗", "unknown": "？"}
            for result in sorted(outcome.results, key=lambda r: ({"violated": 0, "unknown": 1, "satisfied": 2}[r.state], not r.confirmed)):
                if result.facet.get("kind") == "residence" and not result.facet.get("cities"):
                    continue
                if result.state == "unknown" and result not in outcome.unknown_confirmed:
                    continue  # 單一來源的條件在資料不足時不提示，避免雜訊
                note = "（公告條件未完全確認，請看原文）" if result.state == "violated" and not result.confirmed else ""
                lines.append(f"{icon[result.state]} {result.reason}{note}")
            for result in failed:
                if not _core_attribute(result.attribute_id, registry):
                    lines.append(f"✗ {result.human_readable or result.attribute_id}：{result.reason}")
            for attribute_id in dict.fromkeys(r.attribute_id for r in missing if r.complexity != "complex" and not _core_attribute(r.attribute_id, registry)):
                attribute = registry.get(attribute_id)
                lines.append(f"？ 申請前請確認：{attribute.label if attribute else attribute_id}")
            for result in complex_conditions[:3]:
                lines.append(f"△ 需進一步確認：{result.human_readable}")
            for result in bonus[:2]:
                lines.append(f"★ 優先／加分條件：{result.human_readable}")
            if not outcome.results:
                lines.append("此公告沒有明確的申請資格限制，詳細條件請看官方公告。")
            return lines
        if not [r for r in record.get("rules") or [] if r.get("role") != "bonus"]:
            lines.append("此公告尚未抽取到可判斷的資格條件，請直接查看官方公告。")
            return lines
        seen: set[str] = set()
        for result in matched:
            if result.group_id in seen:
                continue
            seen.add(result.group_id)
            lines.append(f"✓ {result.human_readable or result.attribute_id}")
        for result in failed:
            lines.append(f"✗ {result.human_readable or result.attribute_id}：{result.reason}")
        for attribute_id in dict.fromkeys(r.attribute_id for r in missing if r.complexity != "complex"):
            attribute = registry.get(attribute_id)
            lines.append(f"？ 尚未提供：{attribute.label if attribute else attribute_id}")
        for result in complex_conditions[:3]:
            lines.append(f"△ 需進一步確認：{result.human_readable}")
        for result in bonus[:2]:
            lines.append(f"★ 優先／加分條件：{result.human_readable}")
        if status == "possible_match" and not missing and not failed and matched_weight < MIN_HIGH_MATCH_WEIGHT:
            lines.append("△ 可判斷的條件不多，其餘條件請詳閱官方公告")
        return lines
