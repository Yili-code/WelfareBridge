"""國立臺灣海洋大學 學務處生活輔導組 — 校外獎學金公告（RPage 校園 CMS）。

清單：/p/403-1023-1039-1.php（分頁 403-1023-1039-N.php）
詳細：/p/406-1023-XXXXX,r1039.php；內容為 div.mpgdetail > div.meditor 內的表格：
    獎學金分類 / 申請日期 / 獎學金名稱 / 申請方式 / 申請資格 / 繳交文件 / 獲獎金額
"""

from __future__ import annotations

import re
from typing import Iterable

from ..base.base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData
from ..base.http_client import FetchResult
from ..base.parser import absolutize, clean_text, find_attachments, make_soup, node_to_text, normalize_label


class NtouScholarshipCrawler(BaseCrawler):
    content_selectors = ["div.mpgdetail", ".module-detail", "#pageptdetail"]
    list_link_re = re.compile(r"/p/406-1023-\d+,r1039\.php")
    page_link_re = re.compile(r"/p/403-1023-1039-(\d+)\.php")

    def _parse_list(self, html: str, page_url: str) -> tuple[list[DiscoveredItem], list[str]]:
        soup = make_soup(html)
        items: list[DiscoveredItem] = []
        page_links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            url = absolutize(page_url, href)
            if self.list_link_re.search(href):
                title = clean_text(anchor.get("title") or anchor.get_text())
                if title:
                    items.append(DiscoveredItem(url=url, title=title))
            elif self.page_link_re.search(href):
                page_links.append(url)
        return items, page_links

    def discover(self) -> Iterable[DiscoveredItem]:
        first = getattr(self, "_base_fetch", None) or self.fetch(self.base_url)
        items, page_links = self._parse_list(first.text, first.final_url)
        yield from items
        visited = {first.final_url, self.base_url}
        pages = 1
        for link in page_links:
            if pages >= self.max_pages or link in visited:
                continue
            visited.add(link)
            pages += 1
            fetch = self.fetch(link)
            more, _ = self._parse_list(fetch.text, fetch.final_url)
            yield from more

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        soup = make_soup(fetch.text)
        container = None
        for selector in self.content_selectors:
            container = soup.select_one(selector)
            if container is not None:
                break
        if container is None:
            return None
        structured: dict[str, str] = {}
        for row in container.select("table tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            label = normalize_label(cells[0].get_text())
            value = node_to_text(cells[1])
            if label and value:
                structured[label] = value
        body_text = node_to_text(container)
        if not structured and len(body_text) < 40:
            return None
        updated = ""
        updated_node = container.select_one(".ptinfoproperty_update span")
        if updated_node is not None:
            updated = clean_text(updated_node.get_text())
        title = structured.get("獎學金名稱") or item.title
        structured.setdefault("公告標題", item.title)
        raw_text = "\n".join(f"{k}：{v}" for k, v in structured.items())
        classification = structured.get("獎學金分類", "")
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=title,
            content_type="html",
            raw_html=str(container),
            raw_text=raw_text if structured else body_text,
            structured=structured,
            attachments=find_attachments(container, fetch.final_url),
            published_date=updated,
            meta={
                **item.meta,
                "organization": self.organization,
                "classification": classification,
                "is_repost": ("政府" in classification) or ("民間" in classification) or "【" in item.title,
            },
            full_html=fetch.text,
        )
