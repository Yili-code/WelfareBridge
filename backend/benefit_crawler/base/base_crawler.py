"""BaseCrawler：所有官方來源爬蟲的共同骨架。

生命週期：
    validate_source()  官方來源驗證（domain + HTTPS + title metadata）；未通過 → 整個來源 skipped，不寫任何資料
    discover()         找出要抓的項目（清單頁、分頁、固定 URL…）
    fetch + parse_detail()  逐筆抓取詳細頁，轉成 RawDocumentData（原文照抄，不猜測）
    run()              串起以上流程；單筆失敗只記錄、不中斷整個來源
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Iterable

from .http_client import FetchError, FetchResult, PoliteHttpClient
from .parser import find_attachments, html_to_text, make_soup, page_title, select_html
from .source_validator import SourceValidator, ValidationResult

log = logging.getLogger(__name__)


VIEW_COUNTER_RE = re.compile(r"(點閱次數|點閱人次|點閱數|瀏覽人數|瀏覽人次|瀏覽次數|瀏覽數|點擊次數|點擊數|閱讀次數|觀看次數)\s*[:：]?\s*[\d,]+\s*(?:人次|人|次)?")


@dataclass
class DiscoveredItem:
    url: str
    title: str = ""
    meta: dict = field(default_factory=dict)


@dataclass
class RawDocumentData:
    source_url: str
    title: str
    content_type: str = "html"
    raw_html: str = ""
    raw_text: str = ""
    structured: dict = field(default_factory=dict)
    attachments: list = field(default_factory=list)
    published_date: str = ""
    meta: dict = field(default_factory=dict)
    full_html: str = ""  # 完整頁面（寫入 data/raw 檔案，不進 DB）

    def content_hash(self) -> str:
        # 點閱次數、瀏覽人數這類計數每次抓都會變：計算 hash 時忽略，避免內容沒變卻被當成更新而重跑解析與本地 AI（原文照存不動）
        payload = self.raw_text + "\n" + json.dumps(self.structured, ensure_ascii=False, sort_keys=True)
        payload = VIEW_COUNTER_RE.sub(r"\1", payload)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class CrawlResult:
    source_id: str
    status: str = "running"  # success | partial | failed | skipped
    discovered: int = 0
    fetched: int = 0
    failed: int = 0
    skipped_prefilter: int = 0
    skipped_duplicate: int = 0  # 同一輪內容相同、僅網址參數不同而略過的文件數
    documents: list[RawDocumentData] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    logs: list[tuple[str, str, str]] = field(default_factory=list)
    validation: ValidationResult | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None


class BaseCrawler(ABC):
    """繼承後至少要實作 discover() 與 parse_detail()。"""

    #: 詳細頁主要內容區的 CSS selector（依序嘗試；用於 raw_text / raw_html）
    content_selectors: list[str] = []

    def __init__(
        self,
        source_config: dict,
        *,
        http: PoliteHttpClient | None = None,
        validator: SourceValidator | None = None,
        max_items: int | None = None,
    ):
        self.config = source_config
        self.source_id: str = source_config["id"]
        self.name: str = source_config.get("name", self.source_id)
        self.base_url: str = source_config["base_url"]
        self.provider_type: str = source_config.get("provider_type", "unknown")
        self.source_type: str = source_config.get("source_type", "government_site")
        self.organization: str = source_config.get("organization", "")
        self.request_delay: float = float(source_config.get("request_delay_seconds", 1.0))
        self.max_pages: int = int(source_config.get("max_pages", 3))
        self.max_items: int | None = max_items if max_items is not None else source_config.get("max_items")
        self.title_prefilter = re.compile(source_config["title_prefilter"]) if source_config.get("title_prefilter") else None
        self.http = http or PoliteHttpClient(request_delay=self.request_delay)
        self._owns_http = http is None
        self.validator = validator
        self.result = CrawlResult(source_id=self.source_id)

    # ---- 子類別必須實作 ----
    @abstractmethod
    def discover(self) -> Iterable[DiscoveredItem]:
        """回傳要抓取的項目（詳細頁 URL）。"""

    @abstractmethod
    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        """把詳細頁轉成 RawDocumentData；回傳 None 代表這頁不是有效資料。"""

    # ---- 共用工具 ----
    def log(self, level: str, message: str, url: str = "") -> None:
        self.result.logs.append((level, message, url))
        getattr(log, level.lower(), log.info)("[%s] %s %s", self.source_id, message, url)

    def fetch(self, url: str) -> FetchResult:
        return self.http.get(url, delay=self.request_delay)

    def build_document(self, fetch: FetchResult, item: DiscoveredItem, *, title: str = "", structured: dict | None = None,
                       published_date: str = "", meta: dict | None = None, selectors: list[str] | None = None) -> RawDocumentData:
        """以 content_selectors 取主內容區，產生原文照抄的 RawDocumentData。"""
        selectors = selectors or self.content_selectors
        soup = make_soup(fetch.text)
        container = None
        for selector in selectors:
            container = soup.select_one(selector)
            if container is not None:
                break
        attachments = find_attachments(container or soup, fetch.final_url)
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=title or item.title or page_title(fetch.text),
            content_type="html",
            raw_html=select_html(fetch.text, selectors) if selectors else fetch.text,
            raw_text=html_to_text(fetch.text, selectors),
            structured=structured or {},
            attachments=attachments,
            published_date=published_date,
            meta={**item.meta, **(meta or {})},
            full_html=fetch.text,
        )

    # ---- 官方來源驗證 ----
    def validate_source(self) -> ValidationResult:
        expected = self.config.get("expected_title_keywords") or []
        title: str | None = None
        if self.validator is None:
            raise RuntimeError("SourceValidator 未設定")
        try:
            fetch = self.fetch(self.base_url)
            title = page_title(fetch.text) if fetch.is_html else ""
            self._base_fetch = fetch
        except FetchError as exc:
            self._base_fetch = None
            self.log("WARNING", f"來源首頁抓取失敗，僅以網域規則驗證：{exc}", self.base_url)
        result = self.validator.validate_url(self.base_url, expected_title_keywords=expected, page_title=title)
        self.result.validation = result
        return result

    # ---- 主流程 ----
    def run(self, on_document: Callable[[RawDocumentData], None] | None = None) -> CrawlResult:
        result = self.result
        try:
            validation = self.validate_source()
            if not validation.verified:
                result.status = "skipped"
                result.errors.append("官方來源驗證未通過：" + "；".join(validation.reasons))
                self.log("ERROR", result.errors[-1], self.base_url)
                return result

            try:
                items = list(self.discover())
            except Exception as exc:  # discover 失敗 → 整個來源失敗，但不影響其他來源
                result.status = "failed"
                result.errors.append(f"discover 失敗：{exc}")
                self.log("ERROR", result.errors[-1], self.base_url)
                return result

            seen: set[str] = set()
            unique_items: list[DiscoveredItem] = []
            for item in items:
                if item.url in seen:
                    continue
                seen.add(item.url)
                unique_items.append(item)
            result.discovered = len(unique_items)
            self.log("INFO", f"discover 完成：{len(unique_items)} 筆")

            if self.max_items:
                unique_items = unique_items[: int(self.max_items)]

            for item in unique_items:
                if self.title_prefilter and item.title and not self.title_prefilter.search(item.title):
                    result.skipped_prefilter += 1
                    continue
                try:
                    fetch = self.fetch(item.url)
                    document = self.parse_detail(fetch, item)
                    if document is None:
                        self.log("INFO", "略過（非有效資料頁）", item.url)
                        continue
                    result.fetched += 1
                    result.documents.append(document)
                    if on_document is not None:
                        on_document(document)
                except Exception as exc:  # 單筆失敗不中斷
                    result.failed += 1
                    result.errors.append(f"{item.url}: {exc}")
                    self.log("ERROR", f"抓取／解析失敗：{exc}", item.url)

            if result.fetched == 0 and result.failed > 0:
                result.status = "failed"
            elif result.failed > 0:
                result.status = "partial"
            else:
                result.status = "success"
            return result
        finally:
            result.finished_at = datetime.now(timezone.utc)
            if self._owns_http:
                self.http.close()


class StaticPagesCrawler(BaseCrawler):
    """固定 URL 清單的文件型來源（法規頁、方案說明頁）。設定檔 pages: [{url, title}]。"""

    def discover(self) -> Iterable[DiscoveredItem]:
        for page in self.config.get("pages") or []:
            yield DiscoveredItem(url=page["url"], title=page.get("title", ""), meta={"config_title": page.get("title", "")})

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        if not fetch.is_html:
            return None
        document = self.build_document(fetch, item, meta={"organization": self.organization})
        if len(document.raw_text) < 50:
            return None
        return document
