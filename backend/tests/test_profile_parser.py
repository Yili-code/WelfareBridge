"""快速輸入解析（規則式）。"""

from app.matching import parse_profile_text


def values(parsed):
    return {p["attribute_id"]: p["value"] for p in parsed}


def test_student_sentence():
    profile, parsed, hints = parse_profile_text("我是基隆人，海洋大學資工大二，平均82分，沒有低收入戶，學費繳不出來")
    got = values(parsed)
    assert got["residence.household_city"] == "基隆市"
    assert got["education.level"] == "university" and got["education.grade"] == 2.0
    assert got["academic.average_score"] == 82.0
    assert got["identity.low_income"] is False
    assert profile.need_type == "cash_now"
    assert all(p["excerpt"] for p in parsed)


def test_long_term_care_sentence():
    profile, parsed, hints = parse_profile_text("我爸70歲住台北，中度身障，長照評估是第5級，需要人照顧")
    got = values(parsed)
    assert got["residence.current_city"] == "臺北市"
    assert got["disability.certificate_level"] == "中度" and got["disability.has_certificate"] is True
    assert got["care.cms_level"] == 5.0
    assert profile.need_type == "service"
    assert any("家人" in h for h in hints)


def test_unemployed_and_rent():
    profile, parsed, _ = parse_profile_text("我被資遣失業三個月，租屋房租12000元")
    got = values(parsed)
    assert got["employment.status"] == "unemployed" and got["employment.involuntary_separation"] is True
    assert got["housing.tenure"] == "rent" and got["housing.rent_month"] == 12000.0
