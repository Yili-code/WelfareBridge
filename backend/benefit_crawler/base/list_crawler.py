"""通用「公告清單 → 詳細頁」crawler，給地方政府／區公所這類一般公告版使用。

設定（sources.yaml）：
    list_urls:          清單頁 URL（可多個）
    item_link_pattern:  詳細頁連結的 regex（對 href 判斷）
    page_link_pattern:  分頁連結的 regex（可省略）
    max_pages:          最多追幾頁
    title_prefilter:    標題 regex；不符合的公告不抓詳細頁（節省請求；內容仍會再經 keyword filter）
    content_selectors:  詳細頁主內容 CSS selector（依序嘗試）
    title_selectors:    詳細頁標題 selector
    date_pattern:       發布日期 regex（含一個群組）
"""

from __future__ import annotations

import re
from typing import Iterable

from .base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData
from .http_client import FetchResult
from .parser import absolutize, clean_text, find_attachments, make_soup, node_to_text, page_title

DATE_RE = re.compile(r"(\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2}|\d{2,3}[/\-.]\d{1,2}[/\-.]\d{1,2}|\d{2,4}年\d{1,2}月\d{1,2}日)")


class AnnouncementListCrawler(BaseCrawler):
    item_link_pattern: str = ""
    page_link_pattern: str = ""
    title_selectors: list[str] = ["h2.title", "h1", "h2", "h3"]
    date_selectors: list[str] = [".publish_info", ".date", ".news_date", "time"]
    content_selectors: list[str] = ["section.cp", "article", ".cp", ".content", "#content", "main"]

    def __init__(self, source_config: dict, **kwargs):
        super().__init__(source_config, **kwargs)
        self.list_urls: list[str] = list(source_config.get("list_urls") or [source_config.get("list_url") or self.base_url])
        self._item_re = re.compile(source_config.get("item_link_pattern") or self.item_link_pattern)
        page_pattern = source_config.get("page_link_pattern") or self.page_link_pattern
        self._page_re = re.compile(page_pattern) if page_pattern else None
        if source_config.get("content_selectors"):
            self.content_selectors = list(source_config["content_selectors"])
        if source_config.get("title_selectors"):
            self.title_selectors = list(source_config["title_selectors"])

    def parse_list(self, html: str, page_url: str) -> tuple[list[DiscoveredItem], list[str]]:
        soup = make_soup(html)
        items: list[DiscoveredItem] = []
        page_links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            url = absolutize(page_url, href)
            title = clean_text(anchor.get("title") or anchor.get_text())
            if self._item_re.search(url) or self._item_re.search(href):
                if title:
                    items.append(DiscoveredItem(url=url, title=title))
            elif self._page_re is not None and (self._page_re.search(url) or self._page_re.search(href)):
                page_links.append(url)
        return items, page_links

    def discover(self) -> Iterable[DiscoveredItem]:
        visited: set[str] = set()
        for list_url in self.list_urls:
            queue = [list_url]
            pages = 0
            while queue and pages < self.max_pages:
                url = queue.pop(0)
                if url in visited:
                    continue
                visited.add(url)
                fetch = self._base_fetch if (url == self.base_url and getattr(self, "_base_fetch", None)) else self.fetch(url)
                pages += 1
                items, page_links = self.parse_list(fetch.text, fetch.final_url)
                self.log("INFO", f"清單頁：{len(items)} 筆公告", url)
                yield from items
                queue.extend(link for link in page_links if link not in visited)

    def extract_published_date(self, soup) -> str:
        for selector in self.date_selectors:
            node = soup.select_one(selector)
            if node is None:
                continue
            match = DATE_RE.search(node.get_text())
            if match:
                return match.group(1)
        return ""

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        if not fetch.is_html:
            return None
        soup = make_soup(fetch.text)
        title = ""
        for selector in self.title_selectors:
            node = soup.select_one(selector)
            if node is not None and clean_text(node.get_text()):
                title = clean_text(node.get_text())
                break
        container = None
        for selector in self.content_selectors:
            container = soup.select_one(selector)
            if container is not None and clean_text(container.get_text()):
                break
        if container is None:
            return None
        raw_text = node_to_text(container)
        if len(raw_text) < 20:
            return None
        published = self.extract_published_date(soup)
        unit_node = soup.select_one(".publish_info")
        unit = ""
        if unit_node is not None:
            match = re.search(r"發布單位[：:]\s*([^\n]+)", unit_node.get_text())
            if match:
                unit = clean_text(match.group(1))
        structured = {"公告標題": title or item.title or page_title(fetch.text), "公告內容": raw_text}
        if published:
            structured["發布日期"] = published
        if unit:
            structured["發布單位"] = unit
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=structured["公告標題"],
            content_type="html",
            raw_html=str(container),
            raw_text=f"公告標題：{structured['公告標題']}\n" + (f"發布單位：{unit}\n" if unit else "") + raw_text,
            structured=structured,
            attachments=find_attachments(container, fetch.final_url),
            published_date=published,
            meta={**item.meta, "organization": unit or self.organization, "document_kind": "announcement"},
            full_html=fetch.text,
        )
