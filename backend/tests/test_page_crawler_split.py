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


def test_page_name_prefers_content_heading_then_title_segments():
    soup = BeautifulSoup("<main><h2>失業給付</h2><p>目的…</p></main>", "html.parser")
    assert page_name("勞動部勞動力發展署 - 就業服務 -- 失業給付", soup.find("main"), "勞動部勞動力發展署") == "失業給付"
    assert page_name("勞動部勞動力發展署 - 就業服務 -- 失業給付", None, "勞動部勞動力發展署") == "失業給付"
    assert page_name("住宅性能評估[2025版]|內政部不動產資訊平台", None, "內政部") == "住宅性能評估[2025版]"
    assert ANCHOR_NOISE_RE.search("連結到失業給付頁面")
    assert not ANCHOR_NOISE_RE.search("缺工就業獎勵")
