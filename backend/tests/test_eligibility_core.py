"""資格骨幹：多訊號投票、逐項判斷、分層顯示。"""

from app.matching import MatchingEngine, Profile, hard_filter_candidates
from app.matching.eligibility_core import evaluate_core
from app.config import get_settings
from app.registry import get_registry
from app.services.core_builder import build_core, rule_signals, title_signals, vote


def profile(attributes=None, **preferences):
    return Profile.from_dict({"attributes": attributes or {}, "preferences": preferences})


def core(*facets):
    return {"version": 1, "facets": [{"status": "confirmed", "signals": ["gold"], **f} for f in facets]}


def record(rules=None, facets=None, **extra):
    data = {"_id": "b1", "title": "測試補助", "rules": rules or [], "provider": "", "provider_type": "local_government", "benefit": {}, "source": {}}
    if facets is not None:
        data["eligibility_core"] = core(*facets)
    data.update(extra)
    return data


def test_two_agreeing_signals_confirm_single_signal_stays_uncertain():
    facets = vote([
        {"kind": "residence", "cities": ["臺東縣"], "basis": "household", "source": "title"},
        {"kind": "residence", "cities": ["臺東縣"], "basis": "household", "source": "llm"},
        {"kind": "residence", "cities": ["臺北市"], "basis": "household", "source": "structure"},  # 臺北市教育局轉知臺東縣的獎學金
        {"kind": "identity_any", "tags": ["indigenous"], "source": "rules"},
    ])
    residence = next(f for f in facets if f["kind"] == "residence")
    assert residence["cities"] == ["臺東縣"] and residence["status"] == "confirmed"
    assert next(f for f in facets if f["kind"] == "identity_any")["status"] == "uncertain"


def test_national_vote_clears_restriction_only_when_it_is_not_only_the_ai():
    # 標題是中央機關（非 AI 的一票說全國）：縣市限制解除
    facets = vote([{"kind": "residence", "cities": ["高雄市"], "basis": "household", "source": "structure"}, {"kind": "residence", "cities": [], "source": "title"}])
    assert not [f for f in facets if f["kind"] == "residence"]
    # 只有本地 AI 說全國：保留縣市限制但標為需確認（別縣市的人不會看到 ✅，也不會被隱藏）
    facets = vote([{"kind": "residence", "cities": ["高雄市"], "basis": "household", "source": "structure"}, {"kind": "residence", "cities": [], "source": "llm"}])
    residence = next(f for f in facets if f["kind"] == "residence")
    assert residence["cities"] == ["高雄市"] and residence["status"] == "uncertain"


def test_title_ignores_bracket_notes_and_status_application_pages():
    registry = get_registry()
    kinder = title_signals({"title": "公立及非營利幼兒園幼兒就學補助（低收與中低收入戶免費）"}, registry)
    assert not [s for s in kinder if s["kind"] == "identity_any"]
    assert not [s for s in title_signals({"title": "嘉義縣低收入戶救助"}, registry) if s["kind"] == "identity_any"]
    elderly = title_signals({"title": "澎湖縣中低收入老人住宅修繕補助"}, registry)
    assert {"kind": "age", "min": 65, "max": None, "via_child": False, "source": "title"} in elderly
    assert [s["tags"] for s in elderly if s["kind"] == "identity_any"] == [["middle_low_income"]]


def test_rule_signals_skip_inferred_and_contradictory_age():
    registry = get_registry()
    rules = [
        {"attribute_id": "residence.household_city", "operator": "in", "value": ["高雄市"], "complexity": "simple", "role": "required", "confidence": 0.9, "inferred": True},
        {"attribute_id": "applicant.age", "operator": ">=", "value": 65, "complexity": "simple", "role": "required", "confidence": 0.9},
        {"attribute_id": "applicant.age", "operator": "<", "value": 18, "complexity": "simple", "role": "required", "confidence": 0.9},
    ]
    signals = rule_signals({"rules": rules}, registry)
    assert not [s for s in signals if s["kind"] in {"residence", "age"}]


def test_identity_group_agreement_keeps_strict_and_lenient_tags():
    facets = vote([{"kind": "identity_any", "tags": ["middle_low_income"], "source": "title"}, {"kind": "identity_any", "tags": ["low_income", "middle_low_income"], "source": "llm"}])
    facet = {**facets[0]}
    registry = get_registry()
    assert facet["status"] == "confirmed" and facet["strict_tags"] == ["middle_low_income"]
    low = evaluate_core({"facets": [facet]}, profile({"identity.low_income": True}), registry)
    assert low.unknown and not low.violated_confirmed  # 只有部分票同意低收入戶 → 需確認，不排除
    neither = evaluate_core({"facets": [facet]}, profile({"identity.low_income": False, "identity.middle_low_income": False}), registry)
    assert neither.violated_confirmed


def test_facet_states_residence_age_range_and_child():
    registry = get_registry()
    facets = core({"kind": "residence", "cities": ["臺南市"], "basis": "either"}, {"kind": "age", "min": 65, "max": None, "via_child": False})
    outcome = evaluate_core(facets, profile({"residence.household_city": "臺北市", "residence.current_city": "臺南市"}, number_ranges={"applicant.age": [65, None]}), registry)
    assert not outcome.violated_confirmed and not outcome.unknown
    young = evaluate_core(facets, profile({"residence.household_city": "臺南市"}, number_ranges={"applicant.age": [30, 64]}), registry)
    assert [r.facet["kind"] for r in young.violated_confirmed] == ["age"]
    child = core({"kind": "age", "min": 0, "max": 1, "via_child": True})
    assert evaluate_core(child, profile({"applicant.age": 32}), registry).unknown  # 不知道有沒有孩子 → 需補充
    assert evaluate_core(child, profile({"applicant.age": 32, "family.youngest_child_age": 1}), registry).satisfied
    assert evaluate_core(child, profile({"applicant.age": 32, "family.children_count": 0}), registry).violated_confirmed


def test_engine_tiers_and_core_overrides_wrong_rules():
    engine = MatchingEngine()
    wrong_rule = {"attribute_id": "identity.tags", "operator": "not_in", "value": ["economic_hardship"], "complexity": "simple", "role": "exclusion", "confidence": 0.95, "group_id": "exclusion_identity"}
    facets = [{"kind": "residence", "cities": ["高雄市"], "basis": "household"}, {"kind": "identity_any", "tags": ["low_income", "middle_low_income"]}]
    user = profile({"residence.household_city": "高雄市", "identity.low_income": True})
    item = engine.match_one(record([wrong_rule], facets), user)
    assert (item.status, item.tier) == ("high_match", "tier1")  # 抽錯的排除規則不再讓真正符合的人看不到
    unknown = engine.match_one(record([], facets), profile({"residence.household_city": "高雄市"}))
    assert unknown.tier == "tier2" and "identity.low_income" in unknown.needs
    other_city = engine.match_one(record([], facets), profile({"residence.household_city": "臺南市", "identity.low_income": True}))
    assert (other_city.status, other_city.tier) == ("not_match", "hidden")
    legacy = engine.match_one(record([]), user)
    assert legacy.tier == "hidden" and not legacy.core_built


def test_uncertain_violation_stays_visible_and_hard_filter_uses_core():
    engine = MatchingEngine()
    uncertain = {"eligibility_core": {"version": 1, "facets": [{"kind": "identity_any", "tags": ["indigenous"], "status": "uncertain", "signals": ["rules"]}]}}
    item = engine.match_one(record([], None, **uncertain), profile({"identity.indigenous": False}))
    assert item.tier == "tier2"
    records = [record([], [{"kind": "residence", "cities": ["高雄市"], "basis": "household"}]), {**record([]), "_id": "b2"}]
    kept, excluded = hard_filter_candidates(records, profile({"residence.household_city": "臺南市"}), get_registry(), get_settings())
    assert [r["_id"] for r in excluded] == ["b1"] and [r["_id"] for r in kept] == ["b2"]


def test_build_core_without_llm_from_structure_title_and_text():
    built = build_core({"title": "高雄市中低收入老人補助裝置假牙", "provider": "高雄市政府社會局", "provider_type": "local_government", "provider_region": "高雄市",
                        "original_text": "設籍本市年滿65歲以上之中低收入老人。", "rules": []})
    kinds = {f["kind"]: f for f in built["facets"]}
    assert kinds["residence"]["cities"] == ["高雄市"] and kinds["residence"]["status"] == "confirmed"
    assert kinds["age"]["min"] == 65 and kinds["age"]["status"] == "confirmed"


def test_exclusions_of_other_subsidy_recipients_are_not_identity_exclusions():
    text = "六、本年度曾經或已經具以下各款狀況之一者，本案不予補助：\n(一) 領取身心障礙者日間照顧及住宿式照顧補助者。"
    proposals = [{"kind": "identity_exclude", "tags": ["disabled"], "source": "rules", "quote": "領取身心障礙者日間照顧及住宿式照顧補助者"}, {"kind": "identity_exclude", "tags": ["disabled"], "source": "llm", "quote": "領取身心障礙者日間照顧及住宿式照顧補助者"}]
    facet = vote(proposals, text=text)[0]
    assert facet["status"] == "uncertain" and "已領其他補助" in facet["caveat"]
    negated = vote([{"kind": "identity_exclude", "tags": ["low_income"], "source": source, "quote": "非低收入戶"} for source in ("rules", "llm")], text="具原住民身分且非低收入戶")
    assert negated[0]["status"] == "confirmed"


def test_identity_listed_beside_other_applicant_groups_is_not_required():
    text = "※服務對象：\n設籍且實際居住本縣，年滿六十五歲：\n領有社會福利補助(低收入戶、中低收入戶)之老人。\n未領有社會福利補助之一般戶獨居老人。"
    proposals = [{"kind": "identity_any", "tags": ["low_income", "middle_low_income"], "source": source, "quote": "領有社會福利補助(低收入戶、中低收入戶)之老人。"} for source in ("rules", "llm")]
    facet = vote(proposals, text=text)[0]
    assert facet["status"] == "uncertain" and "一般戶獨居老人" in facet["caveat"]


def test_special_circumstances_assistance_does_not_require_prior_status():
    built = build_core({"title": "臺南市特殊境遇家庭法律訴訟補助", "provider_type": "local_government", "provider_region": "臺南市", "original_text": "設籍本市之特殊境遇家庭，家庭暴力受害者。", "rules": [
        {"attribute_id": "identity.tags", "operator": "contains", "value": "special_circumstances", "complexity": "simple", "role": "required", "confidence": 0.9, "group_id": "identity"}]})
    facet = next(f for f in built["facets"] if f["kind"] == "identity_any")
    assert facet["status"] == "uncertain"
