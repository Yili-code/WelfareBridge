from app.services.normalization import (
    chinese_to_int,
    find_cities,
    normalize_city,
    normalize_text,
    parse_amounts,
    parse_date_range,
    parse_duration_months,
    to_iso_date,
)


def test_dates_roc_and_western():
    assert to_iso_date("115/10/01") == "2026-10-01"
    assert to_iso_date("115-10-31") == "2026-10-31"
    assert to_iso_date("民國115年9月30日") == "2026-09-30"
    assert to_iso_date("2026/10/23") == "2026-10-23"
    assert to_iso_date("10月23日") == ""  # 沒有年份不猜


def test_date_range():
    assert parse_date_range("115/10/01～115/10/31") == ("2026-10-01", "2026-10-31")
    assert parse_date_range("自115年10月1日起至115年10月30日止受理申請") == ("2026-10-01", "2026-10-30")
    assert parse_date_range("即日起至10月23日止") == ("", "")


def test_chinese_numbers():
    assert chinese_to_int("三萬二千") == 32000
    assert chinese_to_int("七十") == 70
    assert chinese_to_int("六") == 6
    assert chinese_to_int("一百二十") == 120
    assert chinese_to_int("２萬") == 20000
    assert chinese_to_int("abc") is None


def test_amounts_handle_formal_numerals():
    from app.services.normalization import chinese_to_int, parse_amounts

    assert parse_amounts("每名新台幣2仟元") == [2000]
    assert parse_amounts("核發新臺幣壹萬元整") == [10000]
    assert parse_amounts("每名新臺幣伍仟元") == [5000]
    assert parse_amounts("補助新臺幣貳萬伍仟元") == [25000]
    assert chinese_to_int("參萬") == 30000
    assert parse_amounts("每月最高8,329元") == [8329]
    assert parse_amounts("3萬5千元") == [35000]
    assert parse_amounts("1.5萬元") == [15000]
    assert parse_amounts("每人每月最高補助新臺幣2萬2千元") == [22000]


def test_amounts():
    assert parse_amounts("每名新臺幣5,000元") == [5000]
    assert parse_amounts("得申請獎學金新臺幣三萬二千元") == [32000]
    assert parse_amounts("補助金額為15,000 元或20,000 元") == [15000, 20000]
    assert parse_amounts("家庭年所得70萬元以下") == [700000]


def test_cities():
    assert normalize_city("台北") == "臺北市"
    assert normalize_city("基隆") == "基隆市"
    assert normalize_city("新竹縣") == "新竹縣"
    assert find_cities("設籍高雄市6個月以上，且非臺東縣") == ["高雄市", "臺東縣"]
    assert normalize_text("台北市　ＡＢＣ") == "臺北市 abc"


def test_duration():
    assert parse_duration_months("設籍本市滿一年") == 12
    assert parse_duration_months("設籍高雄市6個月以上") == 6
    assert parse_duration_months("設籍高雄市六個月以上") == 6
    assert parse_duration_months("無設籍要求") is None
