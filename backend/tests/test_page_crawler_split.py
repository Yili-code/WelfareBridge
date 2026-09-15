"""一頁多方案切割：巢狀區塊只留最外層。"""

from bs4 import BeautifulSoup

from benefit_crawler.generic.page_crawler import ANCHOR_NOISE_RE, anchor_label, looks_like_shell, outermost_blocks, page_name


def test_outermost_blocks_drops_nested_duplicates():
    html = (
        "<div class='tab-content'>"
        "<div class='tab-pane'><h3>缺工就業獎勵</h3><div class='page-content'><p>內容 A</p></div></div>"
        "<div class='tab-pane'><h3>專案缺工就業獎勵</h3><div class='page-content'><p>內容 B</p></div></div>"
        "</div>"
    )
    soup = BeautifulSoup(html, "html.parser")
    blocks = soup.select(".tab-content > .tab-pane, .tab-content .page-content")
    assert len(blocks) == 4
    kept = outermost_blocks(blocks)
    assert [b.get("class") for b in kept] == [["tab-pane"], ["tab-pane"]]
    assert [b.find("h3").get_text() for b in kept] == ["缺工就業獎勵", "專案缺工就業獎勵"]


def test_anchor_label_ignores_filenames_and_window_notes():
    soup = BeautifulSoup(
        "<a href='/a.pdf' title='20250415-02.pdf(開啟新視窗)'>育有未滿二歲兒童育兒津貼</a>"
        "<a href='/b.pdf' title='20250415-03.pdf(開啟新視窗)'></a>"
        "<a href='/c' title='中低收入老人生活津貼'>  </a>"
        "<a href='/d'>低收入戶申請資格（另開新視窗）</a>",
        "html.parser",
    )
    labels = [anchor_label(a) for a in soup.find_all("a")]
    assert labels == ["育有未滿二歲兒童育兒津貼", "", "中低收入老人生活津貼", "低收入戶申請資格"]


def test_looks_like_shell_only_when_configured_selectors_missing():
    shell = "<html><body><nav><a href='/'>首頁</a></nav><footer>版權</footer></body></html>"
    page = "<html><body><div id='CCMS_Content'><h2>桃園市假牙補助</h2><p>設籍本市…</p></div></body></html>"
    assert looks_like_shell(shell, ["#CCMS_Content"])
    assert not looks_like_shell(page, ["#CCMS_Content"])
    assert not looks_like_shell(shell, [])  # 沒設定 selector 就不判斷（用啟發式）


def test_page_level_content_selectors_take_priority_over_source_selectors():
    from benefit_crawler.base.http_client import FetchResult
    from benefit_crawler.generic.page_crawler import GenericPageCrawler

    other_host = "https://office.example.gov.tw/news/1"
    config = {
        "id": "t", "base_url": "https://sw.example.gov.tw/", "content_selectors": ["#CCMS_Content"],
        "pages": [
            {"url": "https://sw.example.gov.tw/a", "title": "社會局頁"},
            {"url": other_host, "title": "公所頁", "content_selectors": ["#printdata"]},
        ],
    }
    crawler = GenericPageCrawler(config, http=object())
    items = {item.url: item for item in crawler.discover()}
    assert items["https://sw.example.gov.tw/a"].meta["content_selectors"] == []
    assert items[other_host].meta["content_selectors"] == ["#printdata"]
    html = (
        "<html><body><div class='menu'>" + "選單連結 " * 40 + "</div>"
        "<div id='printdata'><p>" + "設籍本鄉年滿六十五歲者，得申請假牙補助，最高補助四萬元。" * 4 + "</p></div></body></html>"
    )
    fetch = FetchResult(url=other_host, final_url=other_host, status_code=200, content=html.encode(), text=html, content_type="text/html")
    documents = crawler._parse_all(fetch, items[other_host])
    assert len(documents) == 1 and documents[0].raw_text.startswith("設籍本鄉") and "選單" not in documents[0].raw_text


def test_page_name_prefers_content_heading_then_title_segments():
    soup = BeautifulSoup("<main><h2>失業給付</h2><p>目的…</p></main>", "html.parser")
    assert page_name("勞動部勞動力發展署 - 就業服務 -- 失業給付", soup.find("main"), "勞動部勞動力發展署") == "失業給付"
    assert page_name("勞動部勞動力發展署 - 就業服務 -- 失業給付", None, "勞動部勞動力發展署") == "失業給付"
    assert page_name("住宅性能評估[2025版]|內政部不動產資訊平台", None, "內政部") == "住宅性能評估[2025版]"
    assert ANCHOR_NOISE_RE.search("連結到失業給付頁面")
    assert not ANCHOR_NOISE_RE.search("缺工就業獎勵")


def test_generic_crawler_respects_max_items_for_pages_and_followed_links():
    from benefit_crawler.base.http_client import FetchResult
    from benefit_crawler.base.source_validator import ValidationResult
    from benefit_crawler.generic.page_crawler import GenericPageCrawler

    body = "<html><body><main><p>" + "設籍本市年滿六十五歲者得申請補助，每月三千元。" * 5 + "</p><a href='/p/9'>補助九</a></main></body></html>"

    class FakeHttp:
        def __init__(self):
            self.urls: list[str] = []

        def get(self, url, delay=None):
            self.urls.append(url)
            return FetchResult(url=url, final_url=url, status_code=200, content=body.encode(), text=body.replace("補助", f"補助{len(self.urls)}"), content_type="text/html")

    def run(max_items):
        http = FakeHttp()
        config = {"id": "t", "base_url": "https://sw.example.gov.tw/", "follow_links": {"depth": 1, "allow": ["/p/"], "max_links": 10},
                  "pages": [{"url": f"https://sw.example.gov.tw/a{i}", "title": f"頁{i}"} for i in range(3)]}
        crawler = GenericPageCrawler(config, http=http, max_items=max_items)
        crawler.validate_source = lambda: ValidationResult(url=config["base_url"], domain="sw.example.gov.tw", https=True, verified=True, status="verified", method="test")
        return crawler.run(), [u for u in http.urls if u != config["base_url"]]

    result, fetched = run(1)
    assert fetched == ["https://sw.example.gov.tw/a0"] and result.fetched == 1
    result, fetched = run(4)
    assert fetched[:3] == [f"https://sw.example.gov.tw/a{i}" for i in range(3)] and fetched[3:] == ["https://sw.example.gov.tw/p/9"]
    result, fetched = run(None)
    assert len(fetched) == 4


def test_content_hash_ignores_view_counters_but_not_real_changes():
    from benefit_crawler.base.base_crawler import RawDocumentData

    def doc(text):
        return RawDocumentData(source_url="https://x.gov.tw/a", title="補助", content_type="html", raw_html="", raw_text=text, structured={"頁面標題": "補助"})

    base = "發布日期：114/04/29 點閱次數：14572\n瀏覽人數： 832人\n點擊數: 25061\n補助金額每月三千元"
    changed_counters = "發布日期：114/04/29 點閱次數：14579\n瀏覽人數： 834人\n點擊數: 25063\n補助金額每月三千元"
    assert doc(base).content_hash() == doc(changed_counters).content_hash()
    assert doc(base).content_hash() != doc(base.replace("三千", "五千")).content_hash()
    assert doc(base).raw_text == base
