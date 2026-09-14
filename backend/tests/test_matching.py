"""Matching engine v2、追問規劃、排序（用記憶體內的 benefit 文件，不需要資料庫）。"""

from app.matching import MatchingEngine, Profile, plan_questions, rank


def make_benefit(bid: str, rules: list[dict], **extra) -> dict:
    base = {
        "_id": bid, "canonical_id": bid, "title": f"補助 {bid}", "domain": "education", "category": "scholarship", "category_label": "獎學金", "provider": "測試機關", "provider_type": "local_government",
        "benefit": {"benefit_form": "cash", "amount": {"type": "fixed", "value": 5000, "min": 5000, "max": 5000, "period": "year", "count_per_year": 1}, "amount_annualized": 5000, "application_period": {"end_date": "2099-12-31", "rolling": False}, "award_basis": "criteria", "quota": None, "application": {"channel": "school", "documents": ["申請表"], "requires_interview": False}, "obligations": [], "exclusive_with": ["none"], "renewable": None},
        "source": {"source_url": "https://www.edu.tw/x", "source_name": "測試"}, "status": "active", "review": {"needs_review": False}, "is_overview": False, "rules": rules, "index": {}, "original_text": "",
    }
    base.update(extra)
    return base


def rule(attribute_id, operator, value, group_id=None, **extra):
    return {"id": f"{attribute_id}-{operator}", "attribute_id": attribute_id, "operator": operator, "value": value, "group_id": group_id or attribute_id.replace(".", "_"), "complexity": "simple", "role": "required", "confidence": 0.95, "inferred": False, "human_readable": f"{attribute_id} {operator} {value}", "evidence": {"excerpt": "x"}, **extra}


CITY = rule("residence.household_city", "in", ["基隆市"], "residence")
SCORE = rule("academic.average_score", ">=", 80, "academic_average")
LOW = rule("identity.tags", "contains", "low_income", "identity_any")
MID = rule("identity.tags", "contains", "middle_low_income", "identity_any")
LEVEL = rule("education.level", "in", ["university"], "education")


def test_high_possible_not_match_and_or_groups():
    engine = MatchingEngine()
    benefit = make_benefit("b1", [CITY, SCORE, LOW, MID, LEVEL])
    full = Profile.from_dict({"attributes": {"residence.household_city": "基隆市", "academic.average_score": 85, "identity.middle_low_income": True, "education.level": "university"}})
    item = engine.match_one(benefit, full)
    assert item.status == "high_match" and not item.failed
    partial = Profile.from_dict({"attributes": {"residence.household_city": "基隆市", "education.level": "university"}})
    item = engine.match_one(benefit, partial)
    assert item.status == "possible_match" and "academic.average_score" in item.missing_attributes
    wrong = Profile.from_dict({"attributes": {"residence.household_city": "臺北市", "education.level": "university"}})
    assert engine.match_one(benefit, wrong).status == "not_match"


def test_low_confidence_or_inferred_rule_cannot_reject():
    engine = MatchingEngine()
    inferred_city = {**CITY, "inferred": True, "confidence": 0.7}
    benefit = make_benefit("b2", [inferred_city, LEVEL])
    item = engine.match_one(benefit, Profile.from_dict({"attributes": {"residence.household_city": "臺北市", "education.level": "university"}}))
    assert item.status == "possible_match"
    assert any("推定" in c.reason for c in item.missing)


def test_bonus_rules_do_not_affect_status_and_overview_is_insufficient():
    engine = MatchingEngine()
    bonus = {**LOW, "role": "bonus", "group_id": "priority"}
    benefit = make_benefit("b3", [CITY, SCORE, bonus])
    item = engine.match_one(benefit, Profile.from_dict({"attributes": {"residence.household_city": "基隆市", "academic.average_score": 90, "identity.low_income": False}}))
    assert item.status == "high_match" and item.bonus
    overview = make_benefit("b4", [CITY], is_overview=True)
    assert engine.match_one(overview, Profile.from_dict({"attributes": {"residence.household_city": "基隆市"}})).status == "insufficient_data"


def test_single_weak_group_is_only_possible_match():
    engine = MatchingEngine()
    benefit = make_benefit("b5", [LEVEL])
    item = engine.match_one(benefit, Profile.from_dict({"attributes": {"education.level": "university"}}))
    assert item.status == "possible_match"


def test_planner_prefers_attribute_that_flips_most_candidates():
    engine = MatchingEngine()
    records = [make_benefit(f"c{i}", [CITY, LOW]) for i in range(3)] + [make_benefit("d", [CITY, rule("applicant.age", "<=", 30, "applicant_age")])]
    profile = Profile.from_dict({"attributes": {"residence.household_city": "基隆市"}})
    items = engine.match_all(records, profile)
    plan = plan_questions(profile, items, records, mode="dynamic", max_questions=2, engine=engine)
    assert plan["questions"], plan
    assert plan["questions"][0]["attribute_id"] == "identity.low_income"
    assert plan["candidate_count"] == 4


def test_ranking_funnel_and_cards():
    engine = MatchingEngine()
    cheap = make_benefit("r1", [CITY])
    rich = make_benefit("r2", [CITY], benefit={**make_benefit("x", [])["benefit"], "amount": {"type": "fixed", "value": 50000, "min": 50000, "max": 50000, "period": "year", "count_per_year": 1}, "amount_annualized": 50000, "award_basis": "competitive", "application": {"channel": "agency", "documents": ["a", "b", "c", "d"], "requires_interview": True}})
    expired = make_benefit("r3", [CITY], benefit={**make_benefit("x", [])["benefit"], "application_period": {"end_date": "2000-01-01", "rolling": False}})
    loan = make_benefit("r4", [CITY], benefit={**make_benefit("x", [])["benefit"], "benefit_form": "loan"}, category="student_loan", category_label="就學貸款")
    profile = Profile.from_dict({"attributes": {"residence.household_city": "基隆市", "academic.average_score": 90}, "need_type": "cash_now", "dislikes": ["interview"]})
    items = engine.match_all([cheap, rich, expired, loan], profile)
    result = rank(items, profile)
    recommended = {r["benefit_id"]: r for r in result["recommended"]}
    assert "r1" in recommended and "r2" in recommended
    assert recommended["r2"]["suitability"]["penalty"] < 1.0
    assert {r["benefit_id"] for r in result["removed"]} >= {"r3"}
    assert {r["benefit_id"] for r in result["other"]} >= {"r4"}
    assert result["cards"]["highest"] == "r2"
    assert result["bundle"]
