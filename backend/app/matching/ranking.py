"""資格篩選之後的漏斗與排序（v2）。

A 實際不能申請：截止日已過或 < 3 天；與 current_benefits 互斥；貸款且需求不是急需現金
B 需求分流：類別的 need_types 與 need_type 不合 → 「其他可申請」；dislikes 命中 → 硬過濾（×0）或重罰（×0.2）
C 適合度：expected_value（年化金額 × 獲獎機率）× 時效 × (1 − 成本) × 偏好；權重依 need_type 套預設
D 組合：互斥圖上貪婪取總期望價值最高的組合
E 呈現：三張卡（最快、最多、最省力）+ 建議組合 + 依適合度排序的清單
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from ..registry import Registry, get_registry
from ..services.normalization import taiwan_today
from .engine import MatchItem
from .profile import Profile

NEED_WEIGHTS = {
    "cash_now": {"value": 1.0, "probability": 2.0, "urgency": 2.0, "cost": 1.0},
    "reduce_burden": {"value": 2.0, "probability": 1.0, "urgency": 0.6, "cost": 1.0},
    "honor": {"value": 1.0, "probability": 0.5, "urgency": 0.8, "cost": 0.5},
    "service": {"value": 0.5, "probability": 1.5, "urgency": 1.0, "cost": 1.0},
    "unknown": {"value": 1.0, "probability": 1.0, "urgency": 1.0, "cost": 1.0},
}
DISLIKE_FIELDS = {"interview": "requires_interview", "essay": "requires_essay", "recommendation": "requires_recommendation", "financial_proof": "requires_financial_proof", "office_proof": "requires_office_proof"}


@dataclass
class RankedItem:
    item: MatchItem
    stage: str  # eligible | removed_deadline | removed_exclusive | removed_need | removed_dislike | other_need
    reasons: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)
    suitability: dict = field(default_factory=dict)
    bundle: bool = False

    def to_dict(self) -> dict:
        data = self.item.to_dict()
        data.update({"funnel_stage": self.stage, "why": self.reasons, "cautions": self.cautions, "suitability": self.suitability, "in_bundle": self.bundle})
        return data


def _days_left(period: dict, today: date) -> int | None:
    end = (period or {}).get("end_date") or ""
    if not end:
        return None
    try:
        return (date.fromisoformat(end) - today).days
    except ValueError:
        return None


def _win_probability(item: MatchItem, profile: Profile) -> tuple[float, str]:
    meta = item.benefit or {}
    basis = meta.get("award_basis", "unknown")
    if basis == "criteria":
        return 0.9, "符合資格即核發"
    restriction = 0.6
    reasons = []
    if any(c.attribute_id == "residence.household_city" for c in item.matched):
        restriction += 0.15
        reasons.append("限縣市")
    if any(c.attribute_id in {"identity.tags", "identity.low_income", "identity.middle_low_income", "disability.has_certificate"} for c in item.matched):
        restriction += 0.15
        reasons.append("限身分")
    margin = 1.0
    for c in item.matched:
        if c.attribute_id == "academic.average_score" and isinstance(c.user_value, (int, float)) and isinstance(c.value, (int, float)):
            if c.user_value - c.value < 5:
                margin = 0.75
    if basis == "competitive":
        quota = meta.get("quota")
        base = 0.45 if not quota else min(0.85, 0.3 + quota / 400)
        return round(min(0.9, base * restriction * margin), 2), "擇優" + ("，" + "、".join(reasons) if reasons else "") + ("，成績接近門檻" if margin < 1 else "")
    if basis in {"lottery", "first_come"}:
        return 0.5, "抽籤／先到先得"
    return round(min(0.85, 0.6 * restriction * margin), 2), "核發方式未載明" + ("，" + "、".join(reasons) if reasons else "")


def _urgency(days: int | None, need: str) -> tuple[float, str]:
    if days is None:
        return 0.7, "未載明截止日"
    if days < 0:
        return 0.0, "已截止"
    if days <= 3:
        return 0.3, f"{days} 天內截止，備件時間緊"
    if days <= 14:
        return 1.0, f"{days} 天後截止"
    if days <= 60:
        return 0.8, f"{days} 天後截止"
    return 0.6 if need != "cash_now" else 0.5, f"{days} 天後截止"


def _cost(item: MatchItem) -> tuple[float, list[str]]:
    application = (item.benefit or {}).get("application") or {}
    cost = 0.1 * min(len(application.get("documents") or []), 8)
    notes = []
    if application.get("requires_interview"):
        cost += 0.3
        notes.append("需面試")
    if application.get("requires_recommendation") or application.get("requires_essay"):
        cost += 0.2
        notes.append("需自傳／推薦函")
    if application.get("requires_office_proof"):
        cost += 0.2
        notes.append("需公所／村里長證明")
    if application.get("requires_financial_proof"):
        cost += 0.15
        notes.append("需財力證明")
    if application.get("channel") in {"agency", "mail"}:
        cost += 0.1
    return min(cost, 0.8), notes


def rank(items: list[MatchItem], profile: Profile, *, registry: Registry | None = None, today: date | None = None) -> dict:
    registry = registry or get_registry()
    today = today or taiwan_today()
    need = profile.need_type or "unknown"
    weights = NEED_WEIGHTS.get(need, NEED_WEIGHTS["unknown"])
    allowed_categories = registry.categories_for_need(need)
    eligible: list[RankedItem] = []
    removed: list[RankedItem] = []
    other: list[RankedItem] = []
    current = [b.lower() for b in profile.current_benefits]
    for item in items:
        if item.status not in {"high_match", "possible_match"} or item.is_overview:
            continue
        meta = item.benefit or {}
        period = meta.get("application_period") or {}
        days = _days_left(period, today)
        ranked = RankedItem(item=item, stage="eligible")
        if days is not None and days < 0 and not period.get("rolling"):
            ranked.stage, ranked.reasons = "removed_deadline", ["申請期間已結束"]
            removed.append(ranked)
            continue
        if days is not None and days <= 2 and (meta.get("application") or {}).get("documents") and len((meta.get("application") or {}).get("documents") or []) >= 4:
            ranked.stage, ranked.reasons = "removed_deadline", [f"{days} 天內截止且需準備多份文件，可能來不及"]
            removed.append(ranked)
            continue
        if current and meta.get("exclusive_with") and any(e in {"government_benefit", "any_other", "same_category"} for e in meta["exclusive_with"]):
            ranked.stage, ranked.reasons = "removed_exclusive", ["你已領取其他政府補助，此項註明不得重複領取"]
            removed.append(ranked)
            continue
        if meta.get("benefit_form") == "loan" and need not in {"cash_now", "unknown"}:
            ranked.stage, ranked.reasons = "removed_need", ["屬貸款，與你的需求不符"]
            other.append(ranked)
            continue
        if need != "unknown" and item.category and item.category not in allowed_categories:
            ranked.stage, ranked.reasons = "other_need", [f"類別「{item.category_label}」與你的需求（{need}）不同"]
            other.append(ranked)
            continue
        application = meta.get("application") or {}
        penalty = 1.0
        for dislike in profile.dislikes:
            flag = DISLIKE_FIELDS.get(dislike)
            if flag and application.get(flag):
                penalty *= 0.2
                ranked.cautions.append(f"你不想要：{dislike}")
            if dislike == "obligations" and meta.get("obligations"):
                penalty *= 0.2
                ranked.cautions.append("得獎後有義務")
            if dislike == "loan" and meta.get("benefit_form") == "loan":
                penalty = 0.0
            if dislike == "competitive" and meta.get("award_basis") == "competitive":
                penalty *= 0.5
        if penalty == 0.0:
            ranked.stage, ranked.reasons = "removed_dislike", ["你標記為不想要的類型"]
            removed.append(ranked)
            continue
        annual = meta.get("amount_annualized")
        probability, prob_reason = _win_probability(item, profile)
        urgency, urgency_reason = _urgency(days, need)
        cost, cost_notes = _cost(item)
        preference = 1.0
        minimum = (profile.preferences or {}).get("minimum_amount")
        if minimum and annual and annual < float(minimum):
            preference *= 0.5
        ranked.suitability = {"annual_value": annual, "win_probability": probability, "win_reason": prob_reason, "urgency": urgency, "urgency_reason": urgency_reason, "cost": round(cost, 2), "cost_notes": cost_notes, "preference": preference, "penalty": penalty, "days_left": days}
        ranked.reasons = [f"資格：{ '高度符合' if item.status == 'high_match' else '可能符合'}（{int(item.eligibility_score * 100)}%）", prob_reason, urgency_reason]
        if meta.get("benefit_form") == "service":
            ranked.reasons.append("給付形式：服務")
        ranked.cautions.extend(cost_notes)
        if meta.get("obligations"):
            ranked.cautions.append("得獎後義務：" + meta["obligations"][0][:40])
        if meta.get("exclusive_with") and meta["exclusive_with"] != ["none"]:
            ranked.cautions.append("有不得兼領條款")
        eligible.append(ranked)

    values = [r.suitability["annual_value"] for r in eligible if r.suitability.get("annual_value")]
    vmax = max(values) if values else 0.0
    for ranked in eligible:
        s = ranked.suitability
        value_norm = (s["annual_value"] / vmax) if (vmax and s.get("annual_value")) else 0.3
        expected = value_norm * s["win_probability"]
        score = (weights["value"] * value_norm + weights["probability"] * s["win_probability"] + weights["urgency"] * s["urgency"] + weights["cost"] * (1 - s["cost"])) / (weights["value"] + weights["probability"] + weights["urgency"] + weights["cost"])
        score *= s["preference"] * s["penalty"]
        if ranked.item.status == "high_match":
            score *= 1.15
        s["expected_value_norm"] = round(expected, 3)
        s["total"] = round(score, 3)
    eligible.sort(key=lambda r: -r.suitability["total"])

    # ---- D 互斥組合（貪婪）
    bundle: list[RankedItem] = []
    for ranked in eligible:
        meta = ranked.item.benefit or {}
        exclusive = set(meta.get("exclusive_with") or [])
        conflict = False
        for chosen in bundle:
            other_meta = chosen.item.benefit or {}
            other_exclusive = set(other_meta.get("exclusive_with") or [])
            same_provider = chosen.item.provider and chosen.item.provider == ranked.item.provider
            same_category = chosen.item.category == ranked.item.category
            if "any_other" in exclusive or "any_other" in other_exclusive:
                conflict = True
            elif ("government_benefit" in exclusive or "government_benefit" in other_exclusive) and (chosen.item.provider_type != "private_organization" and ranked.item.provider_type != "private_organization"):
                conflict = True
            elif ("same_provider" in exclusive or "same_provider" in other_exclusive) and same_provider:
                conflict = True
            elif ("same_category" in exclusive or "same_category" in other_exclusive) and same_category:
                conflict = True
            if conflict:
                break
        if not conflict and len(bundle) < 5:
            ranked.bundle = True
            bundle.append(ranked)

    # ---- E 三張卡
    cards: dict[str, dict | None] = {"fastest": None, "highest": None, "easiest": None}
    if eligible:
        fastest = max(eligible, key=lambda r: (r.suitability["win_probability"] * (1 if r.suitability["urgency"] > 0 else 0), -(r.suitability.get("days_left") or 999)))
        highest = max(eligible, key=lambda r: (r.suitability.get("annual_value") or 0))
        easiest = min(eligible, key=lambda r: (r.suitability["cost"], -r.suitability["total"]))
        cards = {"fastest": fastest.item.benefit_id, "highest": highest.item.benefit_id if highest.suitability.get("annual_value") else None, "easiest": easiest.item.benefit_id}
    return {
        "need_type": need,
        "recommended": [r.to_dict() for r in eligible],
        "bundle": [r.item.benefit_id for r in bundle],
        "cards": cards,
        "other": [r.to_dict() for r in other],
        "removed": [r.to_dict() for r in removed],
    }
