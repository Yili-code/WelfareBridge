"""Rule engine v2：型態、缺資料 unknown、身分本體展開。"""

from app.matching import Profile, evaluate_rule


def rule(attribute_id, operator, value, **extra):
    return {"attribute_id": attribute_id, "operator": operator, "value": value, "complexity": "simple", "role": "required", **extra}


def profile(**attributes):
    return Profile.from_dict({"attributes": attributes})


def test_placeholder_condition_guards():
    from app.services.extractor import is_real_condition, placeholder_attribute
    from app.registry import get_registry

    assert not is_real_condition("三、申請期限：")
    assert not is_real_condition("學門：不拘")
    assert not is_real_condition("戶籍地限制：不拘")
    assert not is_real_condition("限制條件：一、申請資格：")
    assert is_real_condition("設籍高雄市6個月以上，就讀國內高級中等以上學校之低收入戶或中低收入戶學生。")
    assert is_real_condition("（三）有下列情形之一者，不得申請：就讀空中大學")
    registry = get_registry()
    assert placeholder_attribute(registry, ["applicant.age"], "三、申請期限：") == ""
    assert placeholder_attribute(registry, ["residence.household_city"], "戶籍地限制：高雄市") == "residence.household_city"
    assert placeholder_attribute(registry, ["applicant.age", "residence.household_city"], "設籍本市滿六個月") == "residence.household_city"


def test_missing_data_is_unknown_not_not_match():
    assert evaluate_rule(rule("applicant.age", ">=", 18), profile()).status == "unknown"


def test_number_and_between():
    assert evaluate_rule(rule("applicant.age", ">=", 65), profile(**{"applicant.age": 70})).status == "match"
    assert evaluate_rule(rule("applicant.age", "<", 5), profile(**{"applicant.age": 5})).status == "not_match"
    assert evaluate_rule(rule("applicant.age", "between", [15, 29]), profile(**{"applicant.age": 20})).status == "match"


def test_city_alias_and_duration():
    assert evaluate_rule(rule("residence.household_city", "in", ["基隆市"]), profile(**{"residence.household_city": "基隆"})).status == "match"
    assert evaluate_rule(rule("residence.duration_months", ">=", 6), profile(**{"residence.duration_months": 3})).status == "not_match"


def test_ordered_enum_and_boolean():
    assert evaluate_rule(rule("disability.certificate_level", ">=", "中度"), profile(**{"disability.certificate_level": "重度"})).status == "match"
    assert evaluate_rule(rule("disability.certificate_level", ">=", "中度"), profile(**{"disability.certificate_level": "輕度"})).status == "not_match"
    assert evaluate_rule(rule("care.institutional_placement", "=", False), profile(**{"care.institutional_placement": True})).status == "not_match"


def test_identity_tags_with_ontology_expansion():
    p = profile(**{"identity.low_income": True})
    assert evaluate_rule(rule("identity.tags", "contains", "economic_hardship"), p).status == "match"
    # 只回答過經濟狀況：沒問過的身分是未知，不能判定「不是原住民」「不是身障」
    assert evaluate_rule(rule("identity.tags", "contains", "indigenous"), p).status == "unknown"
    assert evaluate_rule(rule("identity.tags", "not_in", ["disabled"]), p).status == "unknown"
    answered = profile(**{"identity.low_income": True, "identity.indigenous": False, "disability.has_certificate": False})
    assert evaluate_rule(rule("identity.tags", "contains", "indigenous"), answered).status == "not_match"
    assert evaluate_rule(rule("identity.tags", "not_in", ["disabled"]), answered).status == "match"
    assert evaluate_rule(rule("identity.tags", "in", ["indigenous", "low_income"]), profile(**{"identity.indigenous": False})).status == "unknown"
    assert evaluate_rule(rule("identity.tags", "contains", "low_income"), profile()).status == "unknown"
    # 低收入與中低收入都確定不是 → 虛擬的「弱勢學生」仍未知（還可能是原住民、身障…）
    assert evaluate_rule(rule("identity.tags", "contains", "disadvantaged"), profile(**{"identity.low_income": False, "identity.middle_low_income": False})).status == "unknown"


def test_derived_elderly_tag_from_age():
    p = profile(**{"applicant.age": 70})
    assert evaluate_rule(rule("identity.tags", "contains", "elderly"), p).status == "match"


def test_complex_rule_is_unknown():
    assert evaluate_rule({**rule("applicant.age", "exists", None), "complexity": "complex"}, profile(**{"applicant.age": 20})).status == "unknown"
