"""分類器、extractor v2、驗證器（純函式，不需要資料庫）。"""

from datetime import datetime

from app.services.classifier import ClassificationResult, get_classifier
from app.services.extractor import Extractor
from app.services.schema_validator import validate_benefit

LTC_TEXT = """機關單位名稱：臺北市政府社會局
長期照顧居家服務補助
申請資格：
一、設籍並實際居住本市六個月以上。
二、經長期照顧管理中心評估長照需要等級第2級以上。
三、符合下列身分之一：
（一）65歲以上老人。
（二）領有身心障礙證明。
（三）失智症。
四、已入住住宿式機構者不得申請。
補助標準：一般戶每月最高補助 10,020 元，低收入戶全額補助。
申請方式：請撥打 1966 長照專線或至臺北市長期照顧管理中心申請。
申請期間：自即日起隨到隨辦。
"""


def make_doc(text: str, title: str) -> dict:
    return {"_id": "doc-1", "source_id": "taipei_dosw", "source_url": "https://dosw.gov.taipei/cp.aspx?n=TEST", "title": title, "raw_text": text, "structured": {}, "meta": {"organization": "臺北市政府社會局", "seed_category": "home_care", "depth": 0}, "content_type": "html", "crawl_time": datetime(2026, 9, 12, 0, 0), "published_date": "", "attachments": [], "content_hash": "abc"}


SOURCE = {"id": "taipei_dosw", "name": "臺北市政府社會局", "organization": "臺北市政府社會局", "provider_type": "local_government", "source_type": "government_site", "official_domain": "dosw.gov.taipei", "source_verified": True, "data_confidence": 100}


def test_classifier_recognises_benefit_and_rejects_boilerplate():
    classifier = get_classifier()
    good = classifier.classify("長期照顧居家服務補助", LTC_TEXT)
    assert good.is_benefit and good.signal_score >= good.threshold
    bad = classifier.classify("資訊安全與隱私權政策", "本網站隱私權政策、網站導覽、瀏覽人次與資訊安全政策說明。")
    assert not bad.is_benefit


def test_extractor_builds_registry_rules_with_or_groups_and_exclusions():
    classifier = get_classifier()
    classification = classifier.classify("長期照顧居家服務補助", LTC_TEXT)
    classification.category, classification.domain, classification.is_benefit = "home_care", "long_term_care", True
    output = Extractor().extract(make_doc(LTC_TEXT, "長期照顧居家服務補助"), SOURCE, classification)
    benefit = output.benefit
    rules = {(r["attribute_id"], r["operator"]): r for r in benefit["rules"] if r["complexity"] == "simple"}
    assert ("care.cms_level", ">=") in rules and rules[("care.cms_level", ">=")]["value"] == 2.0
    assert ("residence.household_city", "in") in rules and rules[("residence.household_city", "in")]["inferred"] is True
    assert ("residence.duration_months", ">=") in rules and rules[("residence.duration_months", ">=")]["value"] == 6
    alternative_groups = {r["group_id"] for r in benefit["rules"] if r["group_id"].startswith("alternative_")}
    assert alternative_groups, [r["group_id"] for r in benefit["rules"]]
    placement = rules.get(("care.institutional_placement", "="))
    assert placement is not None and placement["value"] is False and placement["role"] == "exclusion"
    assert benefit["benefit"]["application_period"]["rolling"] is True
    assert benefit["benefit"]["amount"]["value"] == 10020.0 and benefit["benefit"]["amount"]["period"] == "month"
    assert benefit["benefit"]["benefit_form"] == "cash"
    assert benefit["provider"] == "臺北市政府社會局" and benefit["provider_type"] == "local_government"
    assert all(r["evidence"]["excerpt"] for r in benefit["rules"])


def test_validator_drops_rules_not_supported_by_text():
    classifier = get_classifier()
    classification = classifier.classify("長期照顧居家服務補助", LTC_TEXT)
    classification.category, classification.domain, classification.is_benefit = "home_care", "long_term_care", True
    benefit = Extractor().extract(make_doc(LTC_TEXT, "長期照顧居家服務補助"), SOURCE, classification).benefit
    benefit["rules"].append({"id": "fake", "attribute_id": "applicant.age", "operator": ">=", "value": 99, "complexity": "simple", "role": "required", "evidence": {"excerpt": "年滿99歲以上"}, "confidence": 0.9, "group_id": "x"})
    benefit["rules"].append({"id": "bad-attr", "attribute_id": "made.up", "operator": "=", "value": True, "complexity": "simple", "role": "required", "evidence": {"excerpt": LTC_TEXT[:20]}, "confidence": 0.9, "group_id": "y"})
    benefit["rules"].append({"id": "bad-op", "attribute_id": "identity.low_income", "operator": ">=", "value": True, "complexity": "simple", "role": "required", "evidence": {"excerpt": "低收入戶全額補助"}, "confidence": 0.9, "group_id": "z"})
    outcome = validate_benefit(benefit, LTC_TEXT)
    assert outcome.ok
    ids = {r["id"] for r in outcome.benefit["rules"]}
    assert "fake" not in ids and "bad-attr" not in ids and "bad-op" not in ids
    assert len(outcome.dropped) == 3
    assert outcome.benefit["review"]["needs_review"] is True


def test_overview_page_produces_no_rules():
    text = "本文羅列低收及中低收入戶就學、生活及就業相關之補助方案。\n" + "\n".join(f"{i}. 某某{kind}：請至各機關申請。" for i, kind in enumerate(["獎學金", "助學金", "生活補助", "租金補貼", "就業津貼", "醫療補助", "急難救助", "托育補助", "教育補助", "交通補助"]))
    text = text + " 詳細內容請參考各機關網站。" * 60
    classifier = get_classifier()
    classification = classifier.classify("中低收入戶的福利總整理", text)
    classification.category, classification.domain, classification.is_benefit = "low_income_allowance", "social_welfare", True
    benefit = Extractor().extract(make_doc(text, "中低收入戶的福利總整理"), SOURCE, classification).benefit
    assert benefit["is_overview"] is True and benefit["rules"] == []

def test_alternative_identity_conditions_share_one_group():
    """「低收入戶或中低收入戶」是擇一（同組 OR）；同句的「設籍本市」仍是必要條件（不同組 AND）。"""
    from app.services.extractor import Extractor

    extractor = Extractor()
    extractor.current_category = "scholarship"
    rules: list[dict] = []
    extractor._condition_rules("申請資格：設籍本市之低收入戶或中低收入戶學生。", {}, "臺北市", rules, [], [])
    tag_groups = {r["group_id"] for r in rules if r["attribute_id"] == "identity.tags"}
    city_groups = {r["group_id"] for r in rules if r["attribute_id"] == "residence.household_city"}
    assert len(tag_groups) == 1, rules
    assert city_groups and not (tag_groups & city_groups), rules


def test_age_or_disability_share_one_group_and_negation_flips_value():
    from app.services.extractor import Extractor

    extractor = Extractor()
    rules: list[dict] = []
    extractor._condition_rules("一、補助對象：年滿六十五歲或領有身心障礙證明，且設籍本市滿六個月者。", {}, "臺北市", rules, [], [])
    age = next(r for r in rules if r["attribute_id"] == "applicant.age")
    tag = next(r for r in rules if r["attribute_id"] == "identity.tags")
    duration = next(r for r in rules if r["attribute_id"] == "residence.duration_months")
    assert age["group_id"] == tag["group_id"] and age["operator"] == ">=" and age["value"] == 65
    assert duration["group_id"] != age["group_id"]

    rules = []
    extractor._condition_rules("申請資格：無自有住宅且家庭年所得低於新臺幣一百萬元之家庭。", {}, "臺北市", rules, [], [])
    tenure = next(r for r in rules if r["attribute_id"] == "housing.tenure")
    income = next(r for r in rules if r["attribute_id"] == "household.income_year")
    assert tenure["operator"] == "not_in" and tenure["value"] == ["own"], tenure
    assert income["operator"] in {"<", "<="} and income["value"] == 1000000, income


def test_public_or_private_school_is_not_a_private_only_rule():
    from app.services.extractor import Extractor

    extractor = Extractor()
    rules: list[dict] = []
    extractor._condition_rules("就讀國內公私立大專校院之學生。", {}, "臺北市", rules, [], [])
    assert not [r for r in rules if r["attribute_id"] == "education.school_type"], rules


def test_relax_merges_only_exclusive_economic_identities():
    from app.services.extractor import relax_contradictory_rules

    def tag_rule(group, tag):
        return {"attribute_id": "identity.tags", "operator": "contains", "value": tag, "group_id": group, "role": "required", "complexity": "simple", "human_readable": tag}

    rules = [tag_rule("identity_any", "elderly"), tag_rule("identity_any", "low_income"), tag_rule("identity_required_middle_low_income", "middle_low_income")]
    assert relax_contradictory_rules(rules) == 1
    groups = {r["value"]: r["group_id"] for r in rules}
    assert groups["low_income"] == groups["middle_low_income"]  # 低收／中低收擇一
    assert groups["elderly"] == "identity_any"  # 老人仍是另一組必要條件


def test_application_period_takes_the_end_of_a_month_day_range():
    """「9月15日起至10月15日止」的截止日是 10/15；取第一個月日會讓還能申請的獎學金被標成已過期。"""
    classifier = get_classifier()
    text = "宋映潭先生獎學金\n申請資格：清寒優秀之大專學生。\n獎助金額：每名 2 萬元。\n申請期間：9月15日起至10月15日止。"
    classification = classifier.classify("宋映潭先生獎學金", text)
    classification.category, classification.domain, classification.is_benefit = "scholarship", "education", True
    doc = {**make_doc(text, "宋映潭先生獎學金"), "structured": {"申請期間": "9月15日起至10月15日止"}, "published_date": "2026-09-01"}
    period = Extractor().extract(doc, SOURCE, classification).benefit["benefit"]["application_period"]
    assert period["end_date"] == "2026-10-15"
    # 只寫起始日時不猜截止日
    doc_start_only = {**doc, "structured": {"申請期間": "自9月15日起受理"}}
    assert Extractor().extract(doc_start_only, SOURCE, classification).benefit["benefit"]["application_period"]["end_date"] == ""


def test_means_test_limits_are_not_benefit_amounts():
    """資力審查的動產／不動產上限不是補助金額（附件併入辦法全文後，這種句子變多了）。"""
    classifier = get_classifier()
    text = ("弱勢兒童及少年生活扶助\n"
            "一、補助對象：遭遇困境之中低收入戶內兒童、少年。\n"
            "二、家庭總收入按全家人口平均分配後，每人每月未達最低生活費；動產每人不超過新臺幣15萬元，不動產不超過650萬元。\n"
            "三、領取生活扶助者，每人每月補助新臺幣一千九百元。")
    classification = classifier.classify("弱勢兒童及少年生活扶助", text)
    classification.category, classification.domain, classification.is_benefit = "child_allowance", "social_welfare", True
    amount = Extractor().extract(make_doc(text, "弱勢兒童及少年生活扶助"), SOURCE, classification).benefit["benefit"]["amount"]
    assert amount["max"] is None or amount["max"] <= 1900, amount
    assert amount["value"] == 1900 or amount["min"] == 1900, amount


def test_property_limits_written_after_a_colon_are_not_amounts():
    """「不動產：115年度每戶不超過578萬元」是資力門檻；從冒號切開後看不出來，會變成補助金額。"""
    classifier = get_classifier()
    text = ("中低收入戶資格認定\n"
            "七、服務對象：設籍本市且實際居住本市符合以下條件者：\n"
            "1.家庭總收入平均分配全家人口，每人每月在最低生活費標準1.5倍以下（本市115年度為2萬3,273元）。\n"
            "2.動產：115年度每人不超過14萬4,000元（包括存款本金、投資、汽車與有價證券等）。\n"
            "3.不動產：115年度每戶不超過578萬元 (包含房屋及土地)。")
    classification = classifier.classify("中低收入戶資格認定", text)
    classification.category, classification.domain, classification.is_benefit = "living_allowance", "social_welfare", True
    amount = Extractor().extract(make_doc(text, "中低收入戶資格認定"), SOURCE, classification).benefit["benefit"]["amount"]
    assert amount["value"] != 5780000 and (amount["max"] or 0) < 5780000, amount
    # 財產上限寫在括號裡、被逗號切成「不動產577萬元」時也不算補助金額
    bracket = ("中低收入戶\n二、動產及不動產均須低於衛生福利部公告之財產金額者（動產14萬4,000元，不動產577萬元）。\n"
               "三、生活扶助：每人每月發給新臺幣3,000元。")
    classification2 = classifier.classify("中低收入戶", bracket)
    classification2.category, classification2.domain, classification2.is_benefit = "living_allowance", "social_welfare", True
    amount2 = Extractor().extract(make_doc(bracket, "中低收入戶"), SOURCE, classification2).benefit["benefit"]["amount"]
    assert (amount2["max"] or 0) <= 3000 and amount2["value"] in (3000, None), amount2
