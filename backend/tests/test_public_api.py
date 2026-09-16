"""前台 API：只給使用者看得懂的內容（金額、適用對象、比對原因），不含作業欄位。"""

from types import SimpleNamespace

from app.api import public


def test_price_shows_amounts_but_not_suspicious_ranges():
    assert public.price({"benefit_form": "cash", "amount": {"value": 5000, "period": "month"}}) == {"type": "amount", "unit": "每月補助", "amount": "5,000 元", "note": ""}
    ranged = public.price({"benefit_form": "cash", "amount": {"min": 4049, "max": 9485, "period": "month"}})
    assert ranged["amount"] == "4,049～9,485 元" and ranged["note"] == "依身分或資格不同"
    assert public.price({"benefit_form": "cash", "amount": {"value": 40000, "period": "once"}})["amount"] == "4 萬元"
    # 差距上百倍多半混進了資力門檻或年度總額：不寫數字
    assert public.price({"benefit_form": "cash", "amount": {"min": 100, "max": 300000, "period": "month"}}) == {"type": "soft", "unit": "提供補助", "amount": "金額依核定", "note": ""}
    assert public.price({"benefit_form": "loan", "amount": {"value": 2200000}})["type"] == "soft"
    # 金額出處是基本工資或所得門檻：不是補助金額
    assert public.price({"benefit_form": "cash", "amount": {"value": 26400, "period": "month", "description": "年基本工資每月 26,400 元"}})["type"] == "soft"
    assert public.price({"benefit_form": "", "amount": {}}) is None


def test_audiences_and_card_points_come_from_the_eligibility_core():
    facets = [
        {"kind": "residence", "cities": ["花蓮縣"], "basis": "household", "status": "confirmed"},
        {"kind": "age", "min": 65, "max": None, "via_child": False, "status": "confirmed"},
        {"kind": "identity_any", "tags": ["low_income", "middle_low_income"], "status": "confirmed"},
        {"kind": "attr", "attribute_id": "employment.status", "value": "unemployed", "status": "uncertain"},
    ]
    assert public.audiences(facets) == ["長者", "低收／中低收", "求職／失業者"]
    assert public.audiences([]) == ["一般民眾"]
    row = {"_id": "b1", "title": "測試津貼", "domain": "social_welfare", "category_label": "老人生活津貼", "provider": "花蓮縣政府社會處", "provider_region": "花蓮縣",
           "benefit": {"benefit_form": "cash", "amount": {"value": 5000, "period": "month", "description": "（一）每月補助5,000元"}, "application_period": {"rolling": True}, "application": {"channel": "agency"}},
           "eligibility_core": {"facets": facets}, "source": {"published_date": "2026-01-02"}}
    card = public.card(row)
    assert card["points"][0].startswith("對象：年齡 65 歲以上") and card["points"][1] == "地區：設籍花蓮縣"
    assert "每月補助5,000元" in card["points"][2] and card["points"][3] == "申請：隨時可以申請、向機關申請"
    assert card["region"] == "花蓮縣" and card["updated"] == "2026-01-02"
    assert public.card({**row, "provider_region": "national"})["region"] == "全國"
    assert not {"rules", "evidence", "classification", "llm", "confidence"} & set(card)


def test_match_reasons_are_user_facing():
    item = SimpleNamespace(core=[
        {"state": "satisfied", "status": "confirmed", "reason": "符合年齡 65 歲以上"},
        {"state": "violated", "status": "uncertain", "reason": "限設籍彰化縣"},
        {"state": "unknown", "status": "confirmed", "reason": "需確認是否具低收入戶身分"},
    ])
    assert public.reasons(item) == [
        {"state": "unsure", "text": "限設籍彰化縣（公告寫法不完全明確，請向承辦單位確認）"},
        {"state": "unknown", "text": "需確認是否具低收入戶身分"},
        {"state": "satisfied", "text": "年齡 65 歲以上"},
    ]
    assert public.reasons(SimpleNamespace(core=[]))[0]["state"] == "unknown"


def test_official_clauses_broken_by_pdf_line_wraps_are_joined():
    lines = ["依據作業辦法應符合下列規定：", "一、領有中低收入老人生活津貼。", "二、未接受機構收容安置、未", "領有政府提供之日間照顧服務補助。", "第三條 照顧者並應符合下列規定："]
    assert public._sentences(lines, 10) == [
        "依據作業辦法應符合下列規定：", "一、領有中低收入老人生活津貼。", "二、未接受機構收容安置、未領有政府提供之日間照顧服務補助。", "第三條 照顧者並應符合下列規定：",
    ]
