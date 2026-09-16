"""附件取捨與併入原文：規範文件（要點、計畫、辦法）要抓，申請書、預算書不抓。"""

from benefit_crawler.base.base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData
from benefit_crawler.base.http_client import FetchResult
from benefit_crawler.base.parser import attachment_is_detail, headline_title, meaningless_name


class _Crawler(BaseCrawler):
    """只用來測 read_attachments：附件下載改成回傳假的 PDF bytes。"""

    def __init__(self, texts: dict[str, str]):
        super().__init__({"id": "test", "name": "test", "base_url": "https://example.gov.tw"})
        self._texts = texts
        self.fetched: list[str] = []

    def discover(self):  # pragma: no cover - 測試不會用到
        return []

    def parse_detail(self, fetch, item):  # pragma: no cover - 測試不會用到
        return None

    def fetch(self, url: str) -> FetchResult:
        self.fetched.append(url)
        return FetchResult(url=url, final_url=url, status_code=200, content=b"%PDF-1.4 fake", text="", content_type="application/pdf")


def document(*attachments: dict, body: str = "詳如附件。") -> RawDocumentData:
    return RawDocumentData(source_url="https://example.gov.tw/news/1", title="某某補助", raw_text=body, attachments=list(attachments))


def attachment(name: str, url: str = "https://example.gov.tw/a.pdf") -> dict:
    return {"url": url, "name": name, "type": "pdf"}


def test_detail_documents_are_read_and_forms_are_not():
    assert attachment_is_detail("實施要點(111年7月27日修正)", body_chars=5000)
    assert attachment_is_detail("弱勢兒童及少年生活扶助與托育及醫療費用補助辦法.pdf", body_chars=5000)
    assert not attachment_is_detail("設置專戶申請書", body_chars=100)
    assert not attachment_is_detail("法定預算書", body_chars=100)
    assert not attachment_is_detail("共同委任切結書", body_chars=100)
    # 名稱看不出內容：本文不足才抓
    assert attachment_is_detail("pdf", body_chars=300)
    assert not attachment_is_detail("pdf", body_chars=5000)


def test_read_attachments_merges_text_into_original_text(monkeypatch):
    monkeypatch.setattr("benefit_crawler.base.base_crawler.pdf_to_text", lambda content: "一、申請資格：設籍本市且實際居住本市，年滿六十五歲之中低收入老人，且未接受政府其他生活補助。二、補助金額：每人每月新臺幣三千元，按月撥入申請人帳戶。")
    crawler = _Crawler({})
    doc = document(attachment("中低收入老人生活津貼發給辦法", "https://example.gov.tw/rule.pdf"), attachment("申請書", "https://example.gov.tw/form.pdf"))
    crawler.read_attachments(doc)
    assert crawler.fetched == ["https://example.gov.tw/rule.pdf"]  # 申請書不抓
    assert "【附件：中低收入老人生活津貼發給辦法】" in doc.raw_text
    assert "設籍本市" in doc.raw_text and "設籍本市" in doc.structured["附件文字"]
    assert doc.attachments[0]["text_extracted"] and "text_extracted" not in doc.attachments[1]


def test_read_attachments_skips_long_pages_with_unnamed_files(monkeypatch):
    monkeypatch.setattr("benefit_crawler.base.base_crawler.pdf_to_text", lambda content: "x" * 200)
    crawler = _Crawler({})
    doc = document(attachment("pdf"), body="本文" * 800)
    crawler.read_attachments(doc)
    assert crawler.fetched == [] and "附件文字" not in doc.structured


def test_meaningless_link_text_falls_back_to_the_first_line_of_the_pdf():
    assert meaningless_name("pdf") and meaningless_name("【PDF】") and meaningless_name("(pdf檔)") and meaningless_name("202305010858500.pdf")
    assert meaningless_name("請點此下載參閱") and not meaningless_name("實施要點")
    assert not meaningless_name("急難救助資源.pdf")  # 中文檔名去掉副檔名後仍是可用的標題
    text = "pdf\n衛生福利部急難救助實施要點\n一、依據：社會救助法第二十一條。"
    assert headline_title(text) == "衛生福利部急難救助實施要點"
    assert headline_title("pdf\n檔案下載\n(PDF檔)") == ""
