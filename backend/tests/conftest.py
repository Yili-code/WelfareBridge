"""測試共用 fixture（v2）：獨立的 MongoDB 測試資料庫、離線 fixture HTML（真實官方頁面存檔）、TestClient。

需要本機 MongoDB（docker compose up -d mongo）；連不到時，需要資料庫的測試會自動跳過。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")
os.environ["MONGODB_DB"] = "benefits_test"
os.environ["DEMO_SEED_ON_STARTUP"] = "false"
os.environ["CRAWL_ON_STARTUP"] = "false"
os.environ["LLM_PROVIDER"] = "none"
os.environ["REDIS_URL"] = ""
os.environ["RESPECT_ROBOTS_TXT"] = "false"
os.environ["DATA_DIR"] = str(BACKEND_DIR / "data" / "test_data")

from app.config import get_settings  # noqa: E402
from app.db import get_client, get_db, init_db, ping  # noqa: E402
from benefit_crawler.base.base_crawler import DiscoveredItem  # noqa: E402
from benefit_crawler.base.http_client import FetchResult  # noqa: E402
from benefit_crawler.base.registry import load_sources_config  # noqa: E402
from benefit_crawler.base.source_validator import SourceValidator  # noqa: E402


def fixture_text(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8", errors="ignore")


def fake_fetch(name: str, url: str) -> FetchResult:
    text = fixture_text(name)
    return FetchResult(url=url, final_url=url, status_code=200, content=text.encode("utf-8"), text=text, content_type="text/html; charset=utf-8")


class NoNetwork:
    def __call__(self, url: str):
        raise RuntimeError(f"network disabled in tests: {url}")


def mongo_available() -> bool:
    try:
        return ping()
    except Exception:
        return False


@pytest.fixture(scope="session")
def source_configs() -> dict[str, dict]:
    return {c["id"]: c for c in load_sources_config(get_settings().sources_config_file)}


@pytest.fixture(scope="session")
def validator() -> SourceValidator:
    return SourceValidator(get_settings().official_domains_file)


def make_crawler(crawler_class, config: dict, validator: SourceValidator):
    crawler = crawler_class(config, validator=validator)
    crawler.fetch = NoNetwork()  # type: ignore[assignment]
    return crawler


@pytest.fixture(scope="session")
def db():
    if not mongo_available():
        pytest.skip("MongoDB 不可用（docker compose up -d mongo）")
    client = get_client()
    client.drop_database(get_settings().mongodb_db)
    database = init_db()
    yield database
    client.drop_database(get_settings().mongodb_db)


@pytest.fixture(scope="session")
def seeded_db(db, validator):
    """把 fixture 官方頁面經 crawler parser → raw_documents → pipeline（純規則式）。"""
    from app.services import crawl_service, pipeline
    from benefit_crawler.government.education import HelpDreamsGovernmentCrawler
    from benefit_crawler.school.universities import NtouScholarshipCrawler

    crawl_service.ensure_sources()
    configs = {c["id"]: c for c in crawl_service.source_configs()}
    counters: dict[str, int] = {}
    gov = make_crawler(HelpDreamsGovernmentCrawler, configs["helpdreams_gov"], validator)
    item = DiscoveredItem(url="https://www.edu.tw/helpdreams/Grants_Content.aspx?n=11EFF33070D6DF4B&sms=931FF851D2FB2128&s=4ACFA38B877F185F", title="高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金", meta={"organization": "高雄市政府教育局", "deadline_roc": "115-10-31", "list_kind": "government"})
    doc = gov.parse_detail(fake_fetch("helpdreams_detail_kaohsiung.html", item.url), item)
    crawl_service.persist_document("helpdreams_gov", configs["helpdreams_gov"]["name"], doc, counters)
    ntou = make_crawler(NtouScholarshipCrawler, configs["ntou_stu"], validator)
    item2 = DiscoveredItem(url="https://stu.ntou.edu.tw/p/406-1023-99999,r1039.php?Lang=zh-tw", title="【轉知】高雄市政府教育局115學年度第1學期中等以上學校清寒優秀學生獎學金", meta={"classification": "政府機構"})
    doc2 = ntou.parse_detail(fake_fetch("ntou_detail_kaohsiung.html", item2.url), item2)
    if doc2 is not None:
        crawl_service.persist_document("ntou_stu", configs["ntou_stu"]["name"], doc2, counters)
    db.sources.update_many({}, {"$set": {"source_verified": True}})
    pipeline.process_pending(force=True, use_llm=False)
    return db


@pytest.fixture(scope="session")
def client(seeded_db):
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


# ---- 真實官方頁面（存檔於 tests/fixtures）對應的 crawler 與 discovered item（crawler parser 測試用）----
FIXTURE_CASES = {
    "helpdreams_kaohsiung": dict(
        source_id="helpdreams_gov",
        crawler="benefit_crawler.government.education.HelpDreamsGovernmentCrawler",
        fixture="helpdreams_detail_kaohsiung.html",
        url="https://www.edu.tw/helpdreams/Grants_Content.aspx?n=11EFF33070D6DF4B&sms=931FF851D2FB2128&s=4ACFA38B877F185F",
        item=DiscoveredItem(url="", title="高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金", meta={"organization": "高雄市政府教育局", "deadline_roc": "115-10-31", "list_kind": "government"}),
    ),
    "moe_weak": dict(
        source_id="moe_programs",
        crawler="benefit_crawler.government.education.MoeAssistanceProgramCrawler",
        fixture="moe_program_weak.html",
        url="https://www.edu.tw/helpdreams/cp.aspx?n=294130B70B308624&s=A8A03607552A5F17",
        item=DiscoveredItem(url="", title="弱勢助學", meta={"config_title": "弱勢助學"}),
    ),
    "cip": dict(
        source_id="cip_regulations",
        crawler="benefit_crawler.government.indigenous.CipRegulationCrawler",
        fixture="cip_regulation.html",
        url="https://law.cip.gov.tw/LawContent.aspx?id=FL029068",
        item=DiscoveredItem(url="", title="原住民族委員會獎助大專校院原住民學生實施要點", meta={"config_title": "原住民族委員會獎助大專校院原住民學生實施要點"}),
    ),
    "keelung_family": dict(
        source_id="keelung_edu",
        crawler="benefit_crawler.local.keelung.KeelungEducationCrawler",
        fixture="keelung_detail_family_education.html",
        url="https://www.klcg.gov.tw/tw/education/3473-322121.html",
        item=DiscoveredItem(url="", title="", meta={}),
    ),
    "taipei_pingtung": dict(
        source_id="taipei_doe",
        crawler="benefit_crawler.local.taipei.TaipeiEducationCrawler",
        fixture="taipei_detail_pingtung.html",
        url="https://www.doe.gov.taipei/News_Content.aspx?n=9AA0CC873BD001A2&sms=2E90303507CA4A6B&s=8AA7B0340372BCA3",
        item=DiscoveredItem(url="", title="", meta={}),
    ),
    "ntou_kaohsiung": dict(
        source_id="ntou_stu",
        crawler="benefit_crawler.school.universities.NtouScholarshipCrawler",
        fixture="ntou_detail_kaohsiung.html",
        url="https://stu.ntou.edu.tw/p/406-1023-128817,r1039.php?Lang=zh-tw",
        item=DiscoveredItem(url="", title="【115-1學期-政府】高雄市115學年度第1學期中等以上學校清寒優秀學生獎學金(10月23日止)", meta={}),
    ),
}


def parse_case(name: str, source_configs: dict, validator: SourceValidator):
    from benefit_crawler.base.registry import get_crawler_class

    case = FIXTURE_CASES[name]
    crawler = make_crawler(get_crawler_class(case["crawler"]), source_configs[case["source_id"]], validator)
    item = DiscoveredItem(url=case["url"], title=case["item"].title, meta=dict(case["item"].meta))
    document = crawler.parse_detail(fake_fetch(case["fixture"], case["url"]), item)
    return crawler, document
