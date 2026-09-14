"""共用解析工具：HTML → 純文字、標籤欄位抽取、PDF / DOCX 文字、附件連結。

只做「原文 → 文字」的轉換，不做任何猜測或補值。
"""

from __future__ import annotations

import io
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

BLOCK_TAGS = {"p", "div", "li", "tr", "br", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "article", "dd", "dt"}
# 注意：不能丟 <form>——ASP.NET 網站（例如內政部住宅補貼平台）整個內容區都包在 <form> 裡
DROP_TAGS = {"script", "style", "noscript", "iframe", "svg", "nav", "header", "footer"}
ATTACHMENT_EXT = re.compile(r"\.(pdf|docx?|odt|ods|xlsx?|pptx?|zip|rar|7z)(\?|$)", re.I)


def make_soup(html: str) -> BeautifulSoup:
    # 環境沒有 lxml wheel，統一使用內建 html.parser
    return BeautifulSoup(html, "html.parser")


def page_title(html: str) -> str:
    soup = make_soup(html)
    if soup.title and soup.title.string:
        return clean_text(soup.title.string)
    return ""


def clean_text(text: str) -> str:
    """去除多餘空白但保留段落換行。"""
    text = text.replace("\xa0", " ").replace("　", " ").replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def node_to_text(node: Tag | BeautifulSoup) -> str:
    """把 HTML 節點轉成保留區塊換行的純文字。"""
    for tag in node.find_all(DROP_TAGS):
        tag.decompose()
    for br in node.find_all("br"):
        br.replace_with("\n")
    for tag in node.find_all(list(BLOCK_TAGS - {"br"})):
        tag.insert_before("\n")
        tag.insert_after("\n")
    return clean_text(node.get_text())


def html_to_text(html: str, selectors: list[str] | None = None) -> str:
    """依序嘗試 selectors，取第一個命中的節點；都沒有就取 <body>。"""
    soup = make_soup(html)
    target: Tag | BeautifulSoup | None = None
    for selector in selectors or []:
        found = soup.select_one(selector)
        if found is not None and clean_text(found.get_text()):
            target = found
            break
    if target is None:
        target = soup.body or soup
    return node_to_text(target)


def select_html(html: str, selectors: list[str]) -> str:
    """回傳第一個命中 selector 的節點 HTML（用來保存 raw_html 主內容區）。"""
    soup = make_soup(html)
    for selector in selectors:
        found = soup.select_one(selector)
        if found is not None:
            return str(found)
    return html


def normalize_label(label: str) -> str:
    """「學　　制」→「學制」、「申請(學)年度」→「申請(學)年度」。"""
    return re.sub(r"[\s　]+", "", label).strip("：:")


def extract_labeled_blocks(container: Tag, *, block_selector: str, label_selector: str, content_selector: str) -> dict[str, str]:
    """通用「標籤 + 內容」區塊抽取（圓夢助學網、海大生輔組都用這種版型）。"""
    result: dict[str, str] = {}
    for block in container.select(block_selector):
        label_node = block.select_one(label_selector)
        content_node = block.select_one(content_selector)
        if label_node is None or content_node is None:
            continue
        label = normalize_label(label_node.get_text())
        content = node_to_text(content_node)
        if label and content:
            result[label] = content
    return result


def find_attachments(container: Tag, base_url: str) -> list[dict]:
    attachments: list[dict] = []
    seen: set[str] = set()
    for anchor in container.find_all("a", href=True):
        href = anchor["href"].strip()
        if not ATTACHMENT_EXT.search(href):
            continue
        url = urljoin(base_url, href)
        if url in seen:
            continue
        seen.add(url)
        name = clean_text(anchor.get_text()) or url.rsplit("/", 1)[-1]
        ext = ATTACHMENT_EXT.search(href)
        attachments.append({"url": url, "name": name, "type": (ext.group(1).lower() if ext else "")})
    return attachments


def absolutize(base_url: str, href: str) -> str:
    return urljoin(base_url, href.replace("&amp;", "&"))


def pdf_to_text(content: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # pragma: no cover - 個別頁面解析失敗不影響整份
            continue
    return clean_text("\n".join(pages))


def docx_to_text(content: bytes) -> str:
    import docx  # python-docx

    document = docx.Document(io.BytesIO(content))
    parts = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text for cell in row.cells))
    return clean_text("\n".join(parts))
