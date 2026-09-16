"""GenericPageCrawler：設定檔驅動的官方頁面 crawler。

支援：
- HTML 頁面：以 content_selectors 取主內容區（沒命中時用啟發式：文字最多、連結比例最低的區塊）
  pages 可逐頁設定 content_selectors（排在來源設定之前），讓同一來源收錄其他主機（公所、法規系統）的頁面而不影響既有頁面
- 一頁多方案：split_selector 命中 ≥ 2 個區塊時，每個區塊拆成一份文件（URL 加 #part-N）
- 往下追一層同網域連結（follow_links.allow / deny 正規表達式；只追白名單官方網域）
- PDF：pypdf 轉文字；Download.ashx 的 base64 檔名解碼成標題
- CSV / JSON / XML：解析成列（rows），data_kind=providers 的資料集由 pipeline 匯入 providers 集合
- skip: true 的項目不抓取，但會產生一份 content_type=skipped 的文件記錄原因（資料中心可看到）

所有文字都是原文照抄；不做任何猜測或補值。
"""

from __future__ import annotations

import base64
import csv
import io
import json
import re
import time
import xml.etree.ElementTree as ET
from typing import Callable, Iterable
from urllib.parse import parse_qs, unquote, urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

from ..base.base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData
from ..base.http_client import FetchError, FetchResult
from ..base.parser import DROP_TAGS, clean_text, find_attachments, headline_title, make_soup, meaningless_name, node_to_text, page_title, pdf_to_text

DEFAULT_SELECTORS = ["#CCMS_Content", "section.cp", "article.cpArticle", ".law-reg-content", "#site_content", "main#main", "main", "article", "#content", ".content"]
NOISE_TAGS = set(DROP_TAGS) | {"aside", "header", "footer", "nav", "button", "select", "input"}
ROC_DATE_RE = re.compile(r"(\d{2,4})\s*[/\-.年]\s*(\d{1,2})\s*[/\-.月]\s*(\d{1,2})\s*日?")
PUBLISHED_RE = re.compile(r"(?:更新日期|發布日期|建檔日期|更新時間|公告日期|發布時間)[:：]?\s*(\d{2,4}\s*[/\-.年]\s*\d{1,2}\s*[/\-.月]\s*\d{1,2}\s*日?)")
UNIT_RE = re.compile(r"(?:發布單位|資料來源|主辦單位|承辦單位|發布機關)[:：]?\s*([^\n:：]{2,40})")
ATTACHMENT_FORMATS = {"pdf", "csv", "json", "xml"}
BOILERPLATE_LINE_RE = re.compile(r"^(?:分享(?:至)?|列印內容|列印|友善列印|回上一頁.*|Facebook|X|line|Email|Bopomofo|網頁功能|字級|小|中|大|:::|::: ?首頁.*|搜尋|進階搜尋|轉寄友人|您的瀏覽器不支援.*)$")


def roc_to_iso(text: str) -> str:
    match = ROC_DATE_RE.search(text or "")
    if not match:
        return ""
    year, month, day = (int(x) for x in match.groups())
    if year < 1911:
        year += 1911
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return ""
    return f"{year:04d}-{month:02d}-{day:02d}"


def decode_download_name(url: str) -> str:
    """www-ws.gov.taipei/Download.ashx?u=...&n=<base64 檔名>：解碼檔名作為標題。"""
    try:
        query = parse_qs(urlsplit(url).query)
        raw = query.get("n", [""])[0]
        if not raw:
            return ""
        padded = unquote(raw)
        padded += "=" * (-len(padded) % 4)
        return base64.b64decode(padded).decode("utf-8", errors="ignore").strip()
    except Exception:  # pragma: no cover - 非標準參數
        return ""


def strip_boilerplate(text: str) -> str:
    lines = [line for line in text.splitlines() if not BOILERPLATE_LINE_RE.match(line.strip())]
    return clean_text("\n".join(lines))


def link_ratio(node: Tag) -> float:
    total = len(clean_text(node.get_text(" ")))
    if total == 0:
        return 1.0
    links = sum(len(clean_text(a.get_text(" "))) for a in node.find_all("a"))
    return min(1.0, links / total)


def heuristic_main(soup: BeautifulSoup) -> Tag | BeautifulSoup:
    """沒有 selector 命中時：移除導覽區塊後，取「文字量 × (1 − 連結比例)」最高、且最深的區塊。"""
    for tag in soup.find_all(list(NOISE_TAGS)):
        tag.decompose()
    best: tuple[float, int, Tag] | None = None
    for tag in soup.find_all(["main", "article", "section", "div", "td"]):
        text_len = len(clean_text(tag.get_text(" ")))
        if text_len < 200:
            continue
        score = text_len * (1.0 - link_ratio(tag))
        depth = len(list(tag.parents))
        if best is None or score > best[0] * 1.08 or (score >= best[0] * 0.92 and depth > best[1]):
            best = (score, depth, tag)
    return best[2] if best else (soup.body or soup)


ANCHOR_NOISE_RE = re.compile(r"^(連結到|前往|另開新視窗|另開視窗|詳見|更多|more|read more|點此|按此|點選|下載|檔案下載|網址|link)|^(線上申請|線上申辦|申請服務|申辦服務|申請入口)$", re.I)


def page_name(html_title: str, container: Tag | BeautifulSoup | None, organization: str = "") -> str:
    """頁面自己的名稱：主內容區的第一個標題（不是機關名）；否則從 <title> 的「網站 - 分類 -- 頁名」取最具體的一段。"""
    org = clean_text(organization or "")
    if container is not None:
        heading = container.find(["h1", "h2", "h3"])
        text = clean_text(heading.get_text()) if heading else ""
        if text and text != org and not ANCHOR_NOISE_RE.search(text) and len(text) <= 80:
            return text
    segments = [clean_text(s) for s in re.split(r"\s*(?:\||｜|--|—|–| - |::|»|>)\s*", html_title or "") if clean_text(s)]
    segments = [s for s in segments if not (org and org in s) and not ANCHOR_NOISE_RE.search(s)]
    return segments[-1] if segments else clean_text(html_title or "")


FILENAME_LABEL_RE = re.compile(r"\.(?:pdf|docx?|odt|ods|xlsx?|csv)\b", re.I)
WINDOW_NOTE_RE = re.compile(r"\s*[\(（\[]\s*(?:開啟|另開)\s*新?\s*視窗\s*[\)）\]]\s*")


def anchor_label(anchor: Tag) -> str:
    """追連結時的連結文字：以看得到的文字為主；title 屬性只在沒有文字時用。
    「20250415-02.pdf(開啟新視窗)」這種檔名或視窗提示不算標題（回傳空字串，解析時改用頁面自己的標題）。"""
    visible = clean_text(anchor.get_text())
    label = visible or clean_text(anchor.get("title") or "")
    label = WINDOW_NOTE_RE.sub(" ", label).strip()
    if not label or FILENAME_LABEL_RE.search(label):
        return ""
    return label


def looks_like_shell(text: str, selectors: list[str]) -> bool:
    """HTTP 200 但頁面沒有任何設定的主內容區（只有選單／頁尾）：有些站台偶爾會這樣回應，重抓一次通常就正常。"""
    if not selectors or not text:
        return False
    soup = make_soup(text)
    for selector in selectors:
        try:
            if soup.select_one(selector) is not None:
                return False
        except Exception:
            continue
    return True


def outermost_blocks(blocks: list[Tag]) -> list[Tag]:
    """split_selector 同時命中外層區塊與其內層區塊（例如 .tab-pane 與其中的 .page-content）時只保留最外層，
    避免同一段內容被拆成兩份文件。"""
    ids = {id(b) for b in blocks}
    kept: list[Tag] = []
    for block in blocks:
        if any(id(parent) in ids for parent in block.parents):
            continue
        kept.append(block)
    return kept


class GenericPageCrawler(BaseCrawler):
    content_selectors: list[str] = DEFAULT_SELECTORS

    def __init__(self, source_config: dict, **kwargs):
        super().__init__(source_config, **kwargs)
        self._configured_selectors: list[str] = list(source_config.get("content_selectors") or [])
        if source_config.get("content_selectors"):
            self.content_selectors = list(source_config["content_selectors"]) + [s for s in DEFAULT_SELECTORS if s not in source_config["content_selectors"]]
        self.split_selector: str = source_config.get("split_selector", "") or ""
        follow = source_config.get("follow_links") or {}
        self.follow_depth: int = int(follow.get("depth", 0) or 0)
        self.follow_allow = [re.compile(p) for p in follow.get("allow", []) or []]
        self.follow_deny = [re.compile(p) for p in follow.get("deny", []) or []]
        self.follow_max: int = int(follow.get("max_links", 50) or 50)
        self.is_repost: bool = bool(source_config.get("is_repost", False))
        self._fetch_cache: dict[str, FetchResult] = {}
        self._page_selectors: dict[str, list[str]] = {page["url"]: list(page["content_selectors"]) for page in source_config.get("pages") or [] if page.get("content_selectors")}

    # ------------------------------------------------------------ discover
    def discover(self) -> Iterable[DiscoveredItem]:
        for page in self.config.get("pages") or []:
            meta = {
                "content_selectors": list(page.get("content_selectors") or []),
                "config_title": page.get("title", ""),
                "seed_category": page.get("seed_category", ""),
                "format": (page.get("format") or "html").lower(),
                "data_kind": page.get("data_kind", "text"),
                "provider_kind": page.get("provider_kind", ""),
                "source_page": page.get("source_page", ""),
                "skip": bool(page.get("skip")),
                "skip_reason": page.get("skip_reason", ""),
                "depth": 0,
                "organization": page.get("organization") or self.organization,  # 同一來源裡由別的機關主辦的頁（例如民政局的生育獎勵金）可逐頁覆寫
                "is_repost": self.is_repost,
            }
            yield DiscoveredItem(url=page["url"], title=page.get("title", ""), meta=meta)

    # ------------------------------------------------------------- fetching
    def fetch(self, url: str) -> FetchResult:
        cached = self._fetch_cache.get(url)
        if cached is not None:
            return cached
        result = super().fetch(url)
        selectors = self._page_selectors.get(url) or self._configured_selectors
        if result.is_html and selectors and url.rstrip("/") != (self.base_url or "").rstrip("/") and looks_like_shell(result.text, selectors):  # 首頁本來就沒有主內容區，不算空殼
            # 桃園市社會局等站台偶爾回傳只有選單的空殼頁（HTTP 200、沒有 #CCMS_Content）：等 2 秒重抓一次
            self.log("WARNING", "頁面沒有設定的主內容區（疑似空殼回應），2 秒後重抓一次", url)
            time.sleep(2)
            retry = super().fetch(url)
            if not looks_like_shell(retry.text, selectors):
                result = retry
        self._fetch_cache[url] = result
        return result

    def _allowed_link(self, url: str, host: str) -> bool:
        parts = urlsplit(url)
        if parts.scheme != "https" or parts.netloc.lower() != host:
            return False
        if self.validator is not None and not self.validator.validate_url(url).verified:
            return False
        if any(p.search(url) for p in self.follow_deny):
            return False
        if self.follow_allow and not any(p.search(url) for p in self.follow_allow):
            return False
        return True

    def _collect_links(self, fetch: FetchResult) -> list[DiscoveredItem]:
        soup = make_soup(fetch.text)
        host = urlsplit(fetch.final_url).netloc.lower()
        found: list[DiscoveredItem] = []
        seen: set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            url = urljoin(fetch.final_url, href.replace("&amp;", "&")).split("#", 1)[0]
            if url in seen or not self._allowed_link(url, host):
                continue
            seen.add(url)
            title = anchor_label(anchor)  # 檔名／「(開啟新視窗)」不當標題 → 解析時改用頁面自己的標題
            found.append(DiscoveredItem(url=url, title=title, meta={"depth": 1, "parent_url": fetch.final_url, "format": "html", "data_kind": "text", "organization": self.organization, "is_repost": self.is_repost, "config_title": title}))
        # 查詢參數越少的網址越先抓（同一頁的 ?fm=1、&s=… 變體之後會因內容相同被略過）
        found.sort(key=lambda d: d.url.count("?") + d.url.count("&"))
        return found

    # ------------------------------------------------------------------ run
    def run(self, on_document: Callable[[RawDocumentData], None] | None = None):  # type: ignore[override]
        result = self.result
        from datetime import datetime, timezone

        try:
            validation = self.validate_source()
            if not validation.verified:
                result.status = "skipped"
                result.errors.append("官方來源驗證未通過：" + "；".join(validation.reasons))
                self.log("ERROR", result.errors[-1], self.base_url)
                return result

            items = list(self.discover())
            result.discovered = len(items)
            # max_items（--max-items、API、MAX_ITEMS_PER_SOURCE）限制本輪最多處理幾筆：先截登錄的頁面，追連結只用剩下的額度
            limit = int(self.max_items) if self.max_items else None
            if limit is not None:
                items = items[:limit]
            followed: list[DiscoveredItem] = []
            visited: set[str] = set()

            seen_hashes: dict[str, str] = {}

            def emit(document: RawDocumentData | None, url: str) -> None:
                if document is None:
                    self.log("INFO", "略過（非有效資料頁）", url)
                    return
                if document.content_type != "skipped":
                    self.read_attachments(document)  # 詳細說明類的 PDF 附件併進原文（要在算 hash 之前）
                    # 同一頁內容完全相同但網址不同（例如 ?fm=1 / ?fm=2 的分頁參數）→ 只保留第一個，其餘記為略過
                    digest = document.content_hash()
                    first_url = seen_hashes.get(digest)
                    if first_url and first_url != document.source_url:
                        reason = f"內容與 {first_url} 完全相同（同一頁的不同網址參數）"
                        self.log("INFO", "略過：" + reason, document.source_url)
                        result.skipped_duplicate += 1
                        document = RawDocumentData(
                            source_url=document.source_url,
                            title=document.title,
                            content_type="skipped",
                            raw_html="",
                            raw_text="",
                            structured={"略過原因": reason},
                            meta={**(document.meta or {}), "document_kind": "skipped", "skip_reason": reason, "duplicate_of_url": first_url},
                        )
                    else:
                        seen_hashes.setdefault(digest, document.source_url)
                result.fetched += 1
                result.documents.append(document)
                if on_document is not None:
                    on_document(document)

            for item in items:
                if item.url in visited:
                    continue
                visited.add(item.url)
                if item.meta.get("skip"):
                    emit(self._skipped_document(item), item.url)
                    continue
                try:
                    fetch = self.fetch(item.url)
                    for document in self._parse_all(fetch, item):
                        emit(document, item.url)
                    if self.follow_depth >= 1 and fetch.is_html and item.meta.get("format", "html") == "html":
                        for link in self._collect_links(fetch):
                            if link.url not in visited and all(link.url != f.url for f in followed):
                                followed.append(link)
                except FetchError as exc:
                    result.failed += 1
                    result.errors.append(f"{item.url}: {exc}")
                    self.log("ERROR", f"抓取失敗：{exc}", item.url)
                except Exception as exc:  # 單筆失敗不中斷
                    result.failed += 1
                    result.errors.append(f"{item.url}: {type(exc).__name__}: {exc}")
                    self.log("ERROR", f"解析失敗：{exc}", item.url)

            if followed:
                self.log("INFO", f"往下追連結（深度 {self.follow_depth}，最多 {self.follow_max} 頁）：第一層 {len(followed)} 個")
                queue: list[DiscoveredItem] = list(followed)
                processed = 0
                follow_budget = self.follow_max if limit is None else min(self.follow_max, max(0, limit - len(items)))
                while queue and processed < follow_budget:
                    link = queue.pop(0)
                    if link.url in visited:
                        continue
                    visited.add(link.url)
                    if self.title_prefilter and link.title and not self.title_prefilter.search(link.title):
                        result.skipped_prefilter += 1
                        continue
                    processed += 1
                    result.discovered += 1
                    try:
                        fetch = self.fetch(link.url)
                        for document in self._parse_all(fetch, link):
                            emit(document, link.url)
                        depth = int(link.meta.get("depth", 1))
                        if depth < self.follow_depth and fetch.is_html:
                            for nxt in self._collect_links(fetch):
                                if nxt.url in visited or any(nxt.url == q.url for q in queue):
                                    continue
                                nxt.meta["depth"] = depth + 1
                                queue.append(nxt)
                    except FetchError as exc:
                        result.failed += 1
                        result.errors.append(f"{link.url}: {exc}")
                        self.log("WARNING", f"連結抓取失敗：{exc}", link.url)
                    except Exception as exc:
                        result.failed += 1
                        result.errors.append(f"{link.url}: {type(exc).__name__}: {exc}")
                        self.log("WARNING", f"連結解析失敗：{exc}", link.url)

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

    # -------------------------------------------------------------- parsing
    def _parse_all(self, fetch: FetchResult, item: DiscoveredItem) -> list[RawDocumentData]:
        fmt = (item.meta.get("format") or "html").lower()
        if fmt == "html" and fetch.is_pdf:
            fmt = "pdf"
        if fmt == "pdf" or fetch.is_pdf:
            document = self._parse_pdf(fetch, item)
            return [document] if document else []
        if fmt in {"csv", "json", "xml"}:
            document = self._parse_table(fetch, item, fmt)
            return [document] if document else []
        if not fetch.is_html:
            self.log("INFO", f"非 HTML 內容（{fetch.content_type}），略過", fetch.final_url)
            return []
        return self._parse_html(fetch, item)

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        documents = self._parse_all(fetch, item)
        return documents[0] if documents else None

    def _skipped_document(self, item: DiscoveredItem) -> RawDocumentData:
        return RawDocumentData(
            source_url=item.url,
            title=item.meta.get("config_title") or item.title,
            content_type="skipped",
            raw_html="",
            raw_text="",
            structured={"略過原因": item.meta.get("skip_reason", "")},
            meta={**item.meta, "document_kind": "skipped"},
        )

    def _main_container(self, soup: BeautifulSoup, page_selectors: list[str] | None = None) -> Tag | BeautifulSoup:
        for selector in list(page_selectors or []) + self.content_selectors:
            try:
                found = soup.select_one(selector)
            except Exception:
                found = None
            if found is not None and len(clean_text(found.get_text(" "))) >= 80:
                return found
        return heuristic_main(soup)

    @staticmethod
    def _page_meta(text: str) -> tuple[str, dict]:
        structured: dict = {}
        published = ""
        match = PUBLISHED_RE.search(text)
        if match:
            published = roc_to_iso(match.group(1))
            if published:
                structured["更新日期"] = published
        unit = UNIT_RE.search(text)
        if unit:
            structured["發布單位"] = clean_text(unit.group(1))[:60]
        return published, structured

    def _parse_html(self, fetch: FetchResult, item: DiscoveredItem) -> list[RawDocumentData]:
        soup = make_soup(fetch.text)
        title_tag = soup.find(["h1", "h2"])
        html_title = page_title(fetch.text)
        container = self._main_container(soup, item.meta.get("content_selectors"))
        blocks: list[Tag] = []
        if self.split_selector:
            try:
                blocks = outermost_blocks([b for b in container.select(self.split_selector) if len(clean_text(b.get_text(" "))) >= 150])
            except Exception:
                blocks = []
        anchor_title = clean_text(item.meta.get("config_title") or item.title or "")
        anchor_title = re.sub(r"^[\[（(]\s*另開新視窗\s*[\]）)]\s*", "", anchor_title)  # 「[另開新視窗]弱勢兒少福利報您知」→ 去掉前綴
        if int(item.meta.get("depth", 0) or 0) >= 1 and (not anchor_title or ANCHOR_NOISE_RE.search(anchor_title)):
            # 追連結抓到的頁面：連結文字是「連結到…頁面」「另開新視窗」之類的雜訊 → 用頁面本身的標題
            base_title = page_name(html_title, container, self.organization) or anchor_title
        else:
            base_title = anchor_title or (clean_text(title_tag.get_text()) if title_tag else "") or html_title
        documents: list[RawDocumentData] = []
        if len(blocks) >= 2:
            for index, block in enumerate(blocks, start=1):
                heading = block.find(["h1", "h2", "h3", "h4", "strong"])
                block_title = clean_text(heading.get_text()) if heading and clean_text(heading.get_text()) else f"{base_title}（{index}）"
                text = strip_boilerplate(node_to_text(block))
                if len(text) < 100:
                    continue
                published, structured = self._page_meta(text)
                structured.update({"區塊": index, "頁面標題": html_title})
                documents.append(
                    RawDocumentData(
                        source_url=f"{fetch.final_url}#part-{index}",
                        title=block_title,
                        content_type="html",
                        raw_html=str(block),
                        raw_text=text,
                        structured=structured,
                        attachments=find_attachments(block, fetch.final_url),
                        published_date=published,
                        meta={**item.meta, "page_title": html_title, "part": index, "document_kind": "program"},
                        full_html=fetch.text if index == 1 else "",
                    )
                )
            if documents:
                return documents
        text = strip_boilerplate(node_to_text(container))
        if len(text) < 80:
            return []
        published, structured = self._page_meta(text)
        structured["頁面標題"] = html_title
        heading = container.find(["h1", "h2", "h3"]) if isinstance(container, Tag) else None
        if heading is not None and clean_text(heading.get_text()):
            structured["內容標題"] = clean_text(heading.get_text())[:120]
        title = base_title or (structured.get("內容標題") or "") or item.title or html_title
        return [
            RawDocumentData(
                source_url=fetch.final_url or fetch.url,
                title=title,
                content_type="html",
                raw_html=str(container),
                raw_text=text,
                structured=structured,
                attachments=find_attachments(container if isinstance(container, Tag) else soup, fetch.final_url),
                published_date=published,
                meta={**item.meta, "page_title": html_title, "document_kind": "page"},
                full_html=fetch.text,
            )
        ]

    def _parse_pdf(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        try:
            text = pdf_to_text(fetch.content)
        except Exception as exc:
            self.log("ERROR", f"PDF 解析失敗：{exc}", fetch.final_url)
            return None
        if len(text) < 50:
            self.log("WARNING", "PDF 沒有可抽取文字（可能是掃描影像）", fetch.final_url)
            return RawDocumentData(source_url=fetch.final_url or fetch.url, title=item.meta.get("config_title") or item.title, content_type="pdf", raw_text="", structured={"備註": "PDF 無可抽取文字（可能為掃描影像）"}, meta={**item.meta, "document_kind": "pdf", "size_bytes": len(fetch.content)})
        decoded = decode_download_name(fetch.url)
        # 連結文字常常只寫「pdf」「檔案下載」：這種標題無法對應到任何方案，改用 PDF 內文第一行
        title = item.meta.get("config_title") or item.title
        if meaningless_name(title):
            named = "" if meaningless_name(decoded) else decoded.rsplit(".", 1)[0]
            title = headline_title(text) or named or title
        published, structured = self._page_meta(text)
        structured["檔案大小"] = f"{len(fetch.content) / 1024:.1f} KB"
        if decoded:
            structured["檔名"] = decoded
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=title,
            content_type="pdf",
            raw_html="",
            raw_text=text,
            structured=structured,
            attachments=[],
            published_date=published,
            meta={**item.meta, "document_kind": "pdf", "size_bytes": len(fetch.content), "file_name": decoded},
        )

    # ------------------------------------------------------------- tabular
    @staticmethod
    def _decode(content: bytes) -> str:
        for charset in ("utf-8-sig", "utf-8", "big5", "cp950"):
            try:
                return content.decode(charset)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    def _rows_from(self, fetch: FetchResult, fmt: str) -> tuple[list[str], list[dict]]:
        if fmt == "csv":
            text = self._decode(fetch.content)
            reader = csv.reader(io.StringIO(text))
            rows = [r for r in reader if any(cell.strip() for cell in r)]
            if not rows:
                return [], []
            header = [clean_text(h) for h in rows[0]]
            records = [{header[i] if i < len(header) else f"col{i}": clean_text(v) for i, v in enumerate(r)} for r in rows[1:]]
            return header, records
        if fmt == "json":
            data = json.loads(self._decode(fetch.content))
            if isinstance(data, dict):
                for key in ("data", "result", "records", "items", "rows"):
                    if isinstance(data.get(key), list):
                        data = data[key]
                        break
                else:
                    nested = next((v for v in data.values() if isinstance(v, list)), [])
                    data = nested
            records = [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []
            header = list(records[0].keys()) if records else []
            return header, [{k: clean_text(str(v)) if v is not None else "" for k, v in r.items()} for r in records]
        if fmt == "xml":
            root = ET.fromstring(self._decode(fetch.content))
            records = []
            for node in root.iter():
                children = list(node)
                if children and all(len(list(c)) == 0 for c in children):
                    records.append({c.tag: clean_text(c.text or "") for c in children})
            header = list(records[0].keys()) if records else []
            return header, records
        return [], []

    def _parse_table(self, fetch: FetchResult, item: DiscoveredItem, fmt: str) -> RawDocumentData | None:
        try:
            header, records = self._rows_from(fetch, fmt)
        except Exception as exc:
            self.log("ERROR", f"{fmt.upper()} 解析失敗：{exc}", fetch.final_url)
            return None
        data_kind = item.meta.get("data_kind", "text")
        if data_kind == "auto":
            joined = " ".join(header)
            data_kind = "providers" if re.search(r"名稱|地址|電話", joined) else "text"
        preview_lines = [" | ".join(header)] + [" | ".join(str(r.get(h, "")) for h in header) for r in records[:400]]
        raw_text = "\n".join(preview_lines)
        structured = {"欄位": header, "列數": len(records), "資料型態": data_kind, "sample_rows": records[:5]}
        return RawDocumentData(
            source_url=fetch.final_url or fetch.url,
            title=item.meta.get("config_title") or item.title,
            content_type=fmt,
            raw_html="",
            raw_text=raw_text,
            structured=structured,
            attachments=[],
            meta={**item.meta, "data_kind": data_kind, "document_kind": "dataset", "rows": records[:5000], "columns": header},
        )
