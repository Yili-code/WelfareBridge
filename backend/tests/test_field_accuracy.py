"""欄位正確性：門檻不是金額、數字配對正確的屬性、摘錄不得改寫。"""

from datetime import datetime

from app.services.classifier import get_classifier
from app.services.extractor import Extractor, _is_threshold_clause
from app.services.schema_validator import excerpt_in_text

TEXT = """機關單位名稱：教育部
學生急難慰問金
申請資格：
一、學生傷病住院七日以上或發生意外死亡者，核給新臺幣一萬元；住院未滿七日者，核給新臺幣五千元。
二、前項學生之家庭總收入，依最近一年綜合所得總額達新臺幣一百萬元以上，或不動產價值合計達新臺幣一千萬元以上，不予核給。
三、家庭年所得達一百萬元以上或不動產價值達一千萬元以上者不予核給。
申請方式：由學校向教育部申請。
"""


def test_threshold_clause_is_not_amount():
    assert _is_threshold_clause("依最近一年綜合所得總額達新臺幣一百萬元以上")
    assert _is_threshold_clause("或不動產價值合計達新臺幣一千萬元以上")
    assert not _is_threshold_clause("核給新臺幣一萬元")
    assert not _is_threshold_clause("補助每月3,000元")


def extract(title: str = "學生急難慰問金", text: str = TEXT, category: str = "emergency_aid_student", domain: str = "education"):
    doc = {"_id": "doc-amt", "source_id": "helpdreams_gov", "source_url": "https://www.edu.tw/helpdreams/cp.aspx?n=TEST", "title": title, "raw_text": text, "structured": {}, "meta": {"organization": "教育部", "seed_category": category, "depth": 0}, "content_type": "html", "crawl_time": datetime(2026, 9, 12, 0, 0), "published_date": "", "attachments": [], "content_hash": "amt"}
    source = {"id": "helpdreams_gov", "name": "教育部圓夢助學網", "organization": "教育部", "provider_type": "central_government", "source_type": "government_site", "official_domain": "edu.tw", "source_verified": True, "data_confidence": 100}
    classification = get_classifier().classify(doc["title"], text)
    if not classification.is_benefit or classification.category != category:
        classification.is_benefit, classification.category, classification.domain = True, category, domain
    return Extractor().extract(doc, source, classification).benefit


def test_rolling_phrases_set_rolling_period():
    text = "桃園市急難救助\n一、申請資格：設籍本市之家庭遭逢變故者。\n二、補助金額：每戶最高新臺幣二萬元。\n三、申請方式：隨時申請，向戶籍地區公所提出。"
    benefit = extract(title="桃園市急難救助", text=text, category="emergency_relief", domain="social_welfare")
    assert benefit["benefit"]["application_period"]["rolling"] is True
    assert not any("截止日期" in r for r in benefit["review"]["reasons"]), benefit["review"]


def test_department_shorthand_uses_full_source_organization():
    from app.services.extractor import Extractor, is_division_name
    ex = Extractor()
    source = {"id": "taoyuan_sw", "organization": "桃園市政府社會局", "provider_type": "local_government", "source_type": "government_site"}
    for unit in ("社會局", "婦幼發展及平權科", "社會救助科", "兒少福利課"):
        ev = []
        provider, ptype, _ = ex._provider({"raw_text": ""}, source, {"發布單位": unit}, {"organization": "桃園市政府社會局"}, "桃園市急難救助", ev)
        assert provider == "桃園市政府社會局" and ptype == "local_government", (unit, provider)
        assert ev and ev[-1]["excerpt"] == f"發布單位：{unit}"  # 摘錄仍是原文
    # 本身就是機關的發布單位不覆寫
    ev = []
    provider, _t, _r = ex._provider({"raw_text": ""}, source, {"發布單位": "衛生福利部社會及家庭署"}, {"organization": "桃園市政府社會局"}, "育兒津貼", ev)
    assert provider == "衛生福利部社會及家庭署"
    assert is_division_name("社會救助科") and not is_division_name("臺北市政府社會局")


def test_closed_programs_are_marked_expired():
    closed_text = "內政部主辦4,000億元優惠購屋專案貸款\n公布日期:113年10月\n統計截止日期實際貸款餘額\n113年8月31日326億9,496萬4,606元\n【備註】本貸款自97年9月22日開辦，目前額度已用罄。"
    benefit = extract(title="【已不再受理新申請案】內政部主辦4,000億元優惠購屋專案貸款", text=closed_text, category="housing_loan_subsidy", domain="housing")
    assert benefit["status"] == "expired"
    assert any("已停止受理" in r for r in benefit["review"]["reasons"]), benefit["review"]
    assert extract()["status"] == "active"


def test_amount_skips_income_thresholds():
    benefit = extract()
    amount = benefit["benefit"]["amount"]
    values = {t["value"] for t in amount.get("tiers") or []} | {amount.get("value"), amount.get("max"), amount.get("min")}
    assert 1000000 not in values and 10000000 not in values, amount
    assert amount.get("max") in (10000, 10000.0), amount


def test_numbers_pair_with_the_right_attribute():
    benefit = extract()
    rules = {(r["attribute_id"], r["operator"], r["value"]) for r in benefit["rules"]}
    assert ("household.income_year", "<", 1000000.0) in rules, rules
    assert ("household.assets", "<", 10000000.0) in rules, rules
    assert ("household.assets", "<", 1000000.0) not in rules, rules
    assert ("household.income_year", "<", 10000000.0) not in rules, rules


def test_excerpt_must_be_verbatim():
    text = "申請人須同時符合下列各項資格條件：(一）具中華民國國籍。(二）就讀國內大專校院。(三）家庭年所得低於一百萬元。"
    assert excerpt_in_text("(一）具中華民國國籍。(三）家庭年所得低於一百萬元。", text)  # 拼接原句可以
    assert not excerpt_in_text("(一）具中華民國國籍。(三）家庭年所得低於兩百萬元。", text)  # 改寫不行
    assert not excerpt_in_text("申請人須同時符合下列各項資格條件，並且需要推薦函", text)
