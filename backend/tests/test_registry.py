"""屬性登錄表、類別樹、身分本體。"""

from app.registry import get_registry


def test_registry_loads_all_definitions():
    registry = get_registry()
    assert len(registry.attributes) >= 70
    assert len(registry.leaves()) >= 40
    assert {d.id for d in registry.domains()} >= {"education", "long_term_care", "disability", "labor", "housing"}
    assert "low_income" in registry.tags
    assert registry.domain_of("home_care") == "long_term_care"


def test_alias_lookup_does_not_use_mined_aliases_by_default():
    registry = get_registry()
    hits = registry.attributes_in_text("設籍本市六個月以上，領有中度以上身心障礙證明，經評估長照需要等級第4級以上")
    assert "residence.household_city" in hits
    assert "disability.certificate_level" in hits
    assert "care.cms_level" in hits
    assert set(registry.tags_in_text("低收入戶及原住民學生")) == {"low_income", "indigenous"}


def test_identity_implies_and_operator_compat():
    registry = get_registry()
    assert registry.expand_tags({"low_income"}) >= {"low_income", "economic_hardship", "disadvantaged"}
    assert registry.operator_allowed("disability.certificate_level", ">=")
    assert not registry.operator_allowed("identity.low_income", ">=")
    assert registry.enum_rank("disability.certificate_level", "重度") > registry.enum_rank("disability.certificate_level", "中度")


def test_derived_attributes_and_unverified_poverty_line():
    registry = get_registry()
    assert registry.evaluate_derived(registry.get("household.income_month"), {"household.income_year": 600000}) == 50000.0
    assert registry.evaluate_derived(registry.get("applicant.is_elderly"), {"applicant.age": 66}) is True
    assert registry.evaluate_derived(registry.get("household.income_vs_poverty_line"), {"household.income_per_capita": 15000, "residence.household_city": "臺北市"}) is None
