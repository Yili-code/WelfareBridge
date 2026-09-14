"""原住民族委員會（law.cip.gov.tw 主管法規共用系統）。

實施要點是正式法規文字，包含申請基準與獎助金額（例如「前一學期學業成績達七十分以上者，得申請獎學金新臺幣三萬二千元」）。
"""

from __future__ import annotations

import re

from ..base.base_crawler import DiscoveredItem, RawDocumentData, StaticPagesCrawler
from ..base.http_client import FetchResult
from ..base.parser import clean_text, find_attachments, make_soup, node_to_text

META_RE = {
    "法規名稱": re.compile(r"法規名稱[：:]\s*(.+)"),
    "公發布日": re.compile(r"公發布日[：:]\s*(.+)"),
    "修正日期": re.compile(r"修正日期[：:]\s*(.+)"),
    "發文字號": re.compile(r"發文字號[：:]\s*(.+)"),
}


class CipRegulationCrawler(StaticPagesCrawler):
    content_selectors = [".law-reg-content", ".law-content", "#content-con"]

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        soup = make_soup(fetch.text)
        article = soup.select_one(".law-reg-content") or soup.select_one(".law-content")
        if article is None:
            return None
        article_text = node_to_text(article)
        if len(article_text) < 80:
            return None
        header_text = node_to_text(soup.select_one("#content-con") or soup)
        structured: dict[str, str] = {}
        for label, pattern in META_RE.items():
            match = pattern.search(header_text)
            if match:
                structured[label] = clean_text(match.group(1).splitlines()[0])
        title = structured.get("法規名稱") or item.meta.get("config_title") or item.title
        structured.setdefault("法規名稱", title)
        structured["條文"] = article_text
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=title,
            content_type="html",
            raw_html=str(article),
            raw_text="\n".join(f"{k}：{v}" for k, v in structured.items() if k != "條文") + "\n" + article_text,
            structured=structured,
            attachments=find_attachments(soup, fetch.final_url),
            published_date="",
            meta={**item.meta, "organization": self.organization or "原住民族委員會", "document_kind": "regulation"},
            full_html=fetch.text,
        )
