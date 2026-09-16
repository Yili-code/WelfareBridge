"""臺北市政府教育局（https://www.doe.gov.taipei/）一般公告。

版型（與教育部同一套 CMS）：清單 News.aspx?n=…&sms=…&page=N&PageSize=20 → News_Content.aspx?…&s=…
詳細頁：#CCMS_Content 內 h3.h3（標題）、.area-essay .essay（內文，常常只有「詳如附件」）、
        .page-footer .file-download-multiple（PDF 附件）、.bottom-detail（資料更新／資料維護單位）。
內文常常只寫「詳如附件」：PDF 附件的文字由 BaseCrawler.read_attachments 併進 raw_text（見 base/parser.py 的取捨規則）。
"""

from __future__ import annotations

import re
from typing import Iterable

from ..base.base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData
from ..base.http_client import FetchResult
from ..base.parser import absolutize, clean_text, find_attachments, make_soup, node_to_text



class TaipeiEducationCrawler(BaseCrawler):
    content_selectors = ["#CCMS_Content", ".page-content", "main"]

    def _parse_list(self, html: str, page_url: str) -> tuple[list[DiscoveredItem], list[str]]:
        soup = make_soup(html)
        items: list[DiscoveredItem] = []
        page_links: list[str] = []
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"]
            if "News_Content.aspx" in href:
                title = clean_text(anchor.get("title") or anchor.get_text())
                if title:
                    items.append(DiscoveredItem(url=absolutize(page_url, href), title=title))
            elif "News.aspx" in href and "page=" in href:
                page_links.append(absolutize(page_url, href))
        return items, page_links

    def discover(self) -> Iterable[DiscoveredItem]:
        first = getattr(self, "_base_fetch", None) or self.fetch(self.base_url)
        items, page_links = self._parse_list(first.text, first.final_url)
        yield from items
        visited = {first.final_url, self.base_url}
        pages = 1
        # 依 page=N 排序，只追前 max_pages 頁
        def page_no(url: str) -> int:
            m = re.search(r"page=(\d+)", url)
            return int(m.group(1)) if m else 0

        for link in sorted(set(page_links), key=page_no):
            if pages >= self.max_pages:
                break
            if link in visited or page_no(link) <= 1:
                continue
            visited.add(link)
            pages += 1
            fetch = self.fetch(link)
            more, _ = self._parse_list(fetch.text, fetch.final_url)
            yield from more

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        soup = make_soup(fetch.text)
        container = soup.select_one("#CCMS_Content") or soup.select_one(".page-content")
        if container is None:
            return None
        heading = container.select_one("h3.h3") or container.select_one("h3")
        title = clean_text(heading.get_text()) if heading else item.title
        essay = container.select_one(".area-essay") or container
        body = node_to_text(essay)
        footer = soup.select_one(".page-footer") or soup
        attachments = find_attachments(footer, fetch.final_url)
        for attachment in attachments:
            # Download.ashx?...&icon=..pdf 這種連結沒有副檔名，用 icon 參數判斷
            if not attachment.get("type") and "icon=..pdf" in attachment["url"]:
                attachment["type"] = "pdf"
        # 教育局的 Download.ashx 連結沒有副檔名，find_attachments 會漏掉，另外補抓
        for anchor in footer.find_all("a", href=True):
            href = anchor["href"]
            if "Download.ashx" in href and all(a["url"] != absolutize(fetch.final_url, href) for a in attachments):
                name = clean_text(anchor.get("data-title") or anchor.get("title") or anchor.get_text())
                kind = "pdf" if "pdf" in href.lower() or "pdf" in name.lower() else ""
                attachments.append({"url": absolutize(fetch.final_url, href), "name": name, "type": kind})

        structured: dict[str, str] = {"公告標題": title, "公告內容": body}
        info = soup.select_one(".bottom-detail")
        published = ""
        unit = ""
        if info is not None:
            info_text = info.get_text()
            m = re.search(r"資料更新[：:]\s*(\d{2,4}-\d{1,2}-\d{1,2})", info_text)
            if m:
                published = m.group(1)
                structured["資料更新"] = published
            m = re.search(r"資料維護[：:]\s*([^\n]+)", info_text)
            if m:
                unit = clean_text(m.group(1))
                structured["發布單位"] = unit

        # 附件文字由 BaseCrawler.read_attachments 統一併入（取捨規則見 parser.attachment_is_detail）
        raw_text = f"公告標題：{title}\n" + (f"發布單位：{unit}\n" if unit else "") + body
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=title,
            content_type="html",
            raw_html=str(container),
            raw_text=raw_text,
            structured=structured,
            attachments=attachments,
            published_date=published,
            meta={**item.meta, "organization": unit or self.organization, "document_kind": "announcement", "is_repost": "轉知" in title},
            full_html=fetch.text,
        )
