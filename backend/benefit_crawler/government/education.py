"""教育部圓夢助學網（https://www.edu.tw/helpdreams/）。

三個來源：
    HelpDreamsGovernmentCrawler   政府機關獎助學金清單（Grants.aspx → Grants_Content.aspx）
    HelpDreamsPrivateCrawler      民間團體獎助學金清單（同版型；provider_type=private_organization）
    MoeAssistanceProgramCrawler   教育部助學措施說明頁（cp.aspx：弱勢助學、學雜費減免、免學費、急難救助…）

詳細頁是「標籤 + 內容」版型（獎學金名稱／學制／成績／獎助身分／獎助資格／戶籍地限制／獎助內容／申請期間…），
這些欄位原文照抄進 structured，後續 extractor 才有依據，不需要猜。
"""

from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import parse_qs, urlsplit

from ..base.base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData, StaticPagesCrawler
from ..base.http_client import FetchResult
from ..base.parser import absolutize, clean_text, extract_labeled_blocks, find_attachments, make_soup, node_to_text

ROC_DATE_RE = re.compile(r"(\d{2,3})[-/.](\d{1,2})[-/.](\d{1,2})")


def roc_to_iso(text: str) -> str:
    """115-10-31 / 115/10/31 → 2026-10-31。無法解析回傳空字串（不猜）。"""
    match = ROC_DATE_RE.search(text or "")
    if not match:
        return ""
    year, month, day = (int(x) for x in match.groups())
    if year < 1911:
        year += 1911
    try:
        return f"{year:04d}-{month:02d}-{day:02d}"
    except ValueError:
        return ""


class HelpDreamsCrawler(BaseCrawler):
    kind = "government"
    content_selectors = ["#ContentPlaceHolder1_data_midlle_grants", "#data_midlle", ".content-detail-wrap"]

    # ---- 清單 ----
    def _parse_list(self, html: str, page_url: str) -> tuple[list[DiscoveredItem], list[str]]:
        soup = make_soup(html)
        items: list[DiscoveredItem] = []
        table = soup.select_one("#ContentPlaceHolder1_gvIndex") or soup.select_one("table.css_tr")
        if table is not None:
            for row in table.select("tr"):
                anchor = row.select_one("a[href*='Grants_Content.aspx']")
                if anchor is None:
                    continue
                cells = row.find_all("td")
                organization = clean_text(cells[1].get_text()) if len(cells) > 1 else ""
                deadline = clean_text(cells[2].get_text()) if len(cells) > 2 else ""
                items.append(
                    DiscoveredItem(
                        url=absolutize(page_url, anchor["href"]),
                        title=clean_text(anchor.get_text()),
                        meta={"organization": organization, "deadline_roc": deadline, "list_kind": self.kind},
                    )
                )
        page_links = []
        for anchor in soup.select("a[href*='Grants.aspx']"):
            href = anchor.get("href", "")
            if "page=" in href:
                page_links.append(absolutize(page_url, href))
        return items, page_links

    def discover(self) -> Iterable[DiscoveredItem]:
        first = getattr(self, "_base_fetch", None) or self.fetch(self.base_url)
        items, page_links = self._parse_list(first.text, first.final_url)
        yield from items
        visited = {first.final_url, self.base_url}
        queue = [link for link in page_links if link not in visited]
        pages_fetched = 1
        while queue and pages_fetched < self.max_pages:
            link = queue.pop(0)
            if link in visited:
                continue
            visited.add(link)
            page_number = parse_qs(urlsplit(link).query).get("page", ["?"])[0]
            self.log("INFO", f"抓取清單第 {page_number} 頁", link)
            fetch = self.fetch(link)
            pages_fetched += 1
            more_items, more_links = self._parse_list(fetch.text, fetch.final_url)
            yield from more_items
            queue.extend(l for l in more_links if l not in visited)

    # ---- 詳細頁 ----
    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        soup = make_soup(fetch.text)
        container = None
        for selector in self.content_selectors:
            container = soup.select_one(selector)
            if container is not None:
                break
        if container is None:
            return None
        structured = extract_labeled_blocks(
            container, block_selector="div[id^='ContentPlaceHolder1_div']", label_selector=".title", content_selector=".content"
        )
        # 說明網址是連結，另外取 href
        url_block = container.select_one("#ContentPlaceHolder1_divtUrl a[href]")
        if url_block is not None:
            structured["說明網址"] = url_block["href"].strip()
        if "獎學金名稱" not in structured:
            return None
        # 特別提醒是網站固定文字，不屬於該獎學金資料
        structured.pop("特別提醒", None)
        lines = [f"{label}：{value}" for label, value in structured.items()]
        raw_text = "\n".join(lines)
        organization = item.meta.get("organization", "")
        deadline_iso = roc_to_iso(item.meta.get("deadline_roc", ""))
        document = RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=structured.get("獎學金名稱", item.title),
            content_type="html",
            raw_html=str(container),
            raw_text=raw_text,
            structured=structured,
            attachments=find_attachments(container, fetch.final_url),
            published_date="",
            meta={
                **item.meta,
                "organization": organization,
                "deadline_iso": deadline_iso,
                "list_kind": self.kind,
            },
            full_html=fetch.text,
        )
        return document


class HelpDreamsGovernmentCrawler(HelpDreamsCrawler):
    kind = "government"


class HelpDreamsPrivateCrawler(HelpDreamsCrawler):
    kind = "private"


class MoeAssistanceProgramCrawler(StaticPagesCrawler):
    """教育部助學措施說明頁（cp.aspx）。每頁是一個方案（例如大專校院弱勢學生助學計畫）。"""

    content_selectors = ["#ContentPlaceHolder1_data_midlle_cp", ".data_midlle", "#data_midlle"]

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        soup = make_soup(fetch.text)
        container = None
        for selector in self.content_selectors:
            container = soup.select_one(selector)
            if container is not None:
                break
        if container is None:
            return None
        raw_text = node_to_text(container)
        if len(raw_text) < 80:
            return None
        title = item.meta.get("config_title") or item.title
        heading = container.find(["h2", "h3"])
        if heading is not None and clean_text(heading.get_text()):
            structured_title = clean_text(heading.get_text())
        else:
            structured_title = title
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=structured_title or title,
            content_type="html",
            raw_html=str(container),
            raw_text=raw_text,
            structured={"方案名稱": structured_title or title, "頁面分類": title},
            attachments=find_attachments(container, fetch.final_url),
            meta={**item.meta, "organization": "教育部"},
            full_html=fetch.text,
        )
