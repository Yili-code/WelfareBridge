"""Crawler Test：真實官方頁面（存檔）→ 正確取得資料。"""

import pytest

from benefit_crawler.government.education import HelpDreamsGovernmentCrawler
from benefit_crawler.local.keelung import KeelungEducationCrawler
from benefit_crawler.local.taipei import TaipeiEducationCrawler
from benefit_crawler.school.universities import NtouScholarshipCrawler
from tests.conftest import fake_fetch, fixture_text, make_crawler, parse_case


def test_helpdreams_list_parses_19_rows(source_configs, validator):
    crawler = make_crawler(HelpDreamsGovernmentCrawler, source_configs["helpdreams_gov"], validator)
    items, page_links = crawler._parse_list(fixture_text("helpdreams_gov_list.html"), source_configs["helpdreams_gov"]["base_url"])
    assert len(items) == 19
    assert all("Grants_Content.aspx" in item.url for item in items)
    assert items[0].meta["organization"] == "高雄市政府教育局"
    assert items[0].meta["deadline_roc"] == "115-10-31"
    assert any("基隆市" in item.title for item in items)


def test_helpdreams_detail_structured_fields(source_configs, validator):
    _, doc = parse_case("helpdreams_kaohsiung", source_configs, validator)
    assert doc.title == "高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金"
    assert doc.structured["戶籍地限制"] == "高雄市"
    assert "低收入戶" in doc.structured["獎助身分"]
    assert doc.structured["申請期間"].startswith("115/10/01")
    assert "1,500" in doc.structured["獎助內容"]
    assert "特別提醒" not in doc.structured  # 網站固定文字不算資料
    assert doc.content_hash() == doc.content_hash()  # deterministic


def test_moe_program_page(source_configs, validator):
    _, doc = parse_case("moe_weak", source_configs, validator)
    assert "大專校院" in doc.raw_text and "家庭年所得70萬以下" in doc.raw_text
    assert doc.meta["organization"] == "教育部"


def test_cip_regulation_page(source_configs, validator):
    _, doc = parse_case("cip", source_configs, validator)
    assert doc.title == "原住民族委員會獎助大專校院原住民學生實施要點"
    assert "七十分以上" in doc.raw_text
    assert doc.structured.get("法規名稱")


def test_keelung_list_and_detail(source_configs, validator):
    crawler = make_crawler(KeelungEducationCrawler, source_configs["keelung_edu"], validator)
    items, _ = crawler.parse_list(fixture_text("keelung_list.html"), "https://www.klcg.gov.tw/tw/education/3473.html")
    assert len(items) >= 10
    assert all("/tw/education/3473-" in item.url for item in items)
    _, doc = parse_case("keelung_family", source_configs, validator)
    assert doc.structured["發布單位"].startswith("基隆市政府教育處")
    assert doc.published_date == "2026/09/09"


def test_taipei_list_prefilter_and_detail(source_configs, validator):
    crawler = make_crawler(TaipeiEducationCrawler, source_configs["taipei_doe"], validator)
    items, page_links = crawler._parse_list(fixture_text("taipei_list.html"), source_configs["taipei_doe"]["base_url"])
    assert len(items) >= 20
    assert any("page=2" in link for link in page_links)
    scholarship_titles = [i.title for i in items if crawler.title_prefilter.search(i.title)]
    assert scholarship_titles, "標題預篩應該留下獎學金公告"
    _, doc = parse_case("taipei_pingtung", source_configs, validator)
    assert doc.title.startswith("【轉知】屏東縣政府")
    assert doc.meta["is_repost"] is True
    assert any(a.get("type") == "pdf" for a in doc.attachments)
    assert doc.structured["發布單位"].startswith("臺北市政府教育局")


def test_ntou_list_and_detail(source_configs, validator):
    crawler = make_crawler(NtouScholarshipCrawler, source_configs["ntou_stu"], validator)
    items, _ = crawler._parse_list(fixture_text("ntou_list.html"), source_configs["ntou_stu"]["base_url"])
    assert len(items) >= 10
    _, doc = parse_case("ntou_kaohsiung", source_configs, validator)
    assert doc.structured["獎學金分類"] == "政府機構"
    assert "設籍高雄市六個月以上" in doc.structured["申請資格"]
    assert doc.meta["is_repost"] is True


@pytest.mark.network
def test_live_helpdreams_list(source_configs, validator):
    """實際連線官方網站（pytest -m network）。"""
    from benefit_crawler.base.http_client import PoliteHttpClient

    crawler = HelpDreamsGovernmentCrawler(source_configs["helpdreams_gov"], http=PoliteHttpClient(request_delay=1.0), validator=validator, max_items=1)
    result = crawler.run()
    assert result.validation is not None and result.validation.verified
    assert result.discovered >= 1
    assert result.fetched == 1
    assert result.documents[0].structured.get("獎學金名稱")
