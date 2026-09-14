"""禮貌性 HTTP client：timeout、retry + exponential backoff、每個 host 的 request_delay、robots.txt。

只用 httpx 抓靜態 HTML / JSON / 文件；需要 JavaScript 的頁面另外由 PlaywrightFetcher 處理（見 fetch_rendered）。
"""

from __future__ import annotations

import logging
import random
import re
import ssl
import time
import urllib.robotparser
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import urlsplit

import httpx

log = logging.getLogger(__name__)

RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


class FetchError(RuntimeError):
    def __init__(self, url: str, message: str, status_code: int | None = None):
        super().__init__(f"{message} ({url})")
        self.url = url
        self.status_code = status_code


@dataclass
class FetchResult:
    url: str
    final_url: str
    status_code: int
    content: bytes
    text: str
    content_type: str
    headers: dict = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_html(self) -> bool:
        return "html" in self.content_type or self.text.lstrip()[:200].lower().startswith(("<!doctype", "<html"))

    @property
    def is_pdf(self) -> bool:
        return "pdf" in self.content_type or self.content[:5] == b"%PDF-"


def build_ssl_context(strict_x509: bool) -> ssl.SSLContext:
    """Python 3.13 預設 VERIFY_X509_STRICT 會拒絕部分政府主機憑證鏈；只關閉嚴格旗標，CA 與主機名稱驗證仍在。"""
    context = ssl.create_default_context()
    if not strict_x509 and hasattr(ssl, "VERIFY_X509_STRICT"):
        context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return context


_META_CHARSET_RE = re.compile(rb"""<meta[^>]+charset=["']?\s*([a-zA-Z0-9_\-]+)""", re.I)


def decode_body(content: bytes, header_charset: str | None) -> str:
    """依序嘗試 header charset → <meta charset> → utf-8 → big5（台灣舊網站）。"""
    candidates: list[str] = []
    if header_charset:
        candidates.append(header_charset)
    match = _META_CHARSET_RE.search(content[:4096])
    if match:
        candidates.append(match.group(1).decode("ascii", "ignore"))
    candidates.extend(["utf-8", "big5", "cp950"])
    for charset in candidates:
        try:
            return content.decode(charset)
        except (LookupError, UnicodeDecodeError):
            continue
    return content.decode("utf-8", errors="replace")


class PoliteHttpClient:
    def __init__(
        self,
        *,
        user_agent: str = "ScholarshipAI-Crawler/0.1",
        timeout: float = 30.0,
        max_retries: int = 3,
        request_delay: float = 1.0,
        respect_robots: bool = True,
        strict_x509: bool = False,
        backoff_base: float = 1.5,
        backoff_max: float = 30.0,
    ):
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_retries = max_retries
        self.request_delay = request_delay
        self.respect_robots = respect_robots
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/json,application/pdf;q=0.9,*/*;q=0.8",
                "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.5",
            },
            verify=build_ssl_context(strict_x509),
        )
        self._last_request_at: dict[str, float] = {}
        self._robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}
        self.request_count = 0

    # ---- robots.txt ----
    def _robots_for(self, url: str) -> urllib.robotparser.RobotFileParser | None:
        parts = urlsplit(url)
        host = f"{parts.scheme}://{parts.netloc}"
        if host in self._robots:
            return self._robots[host]
        parser: urllib.robotparser.RobotFileParser | None = None
        try:
            response = self._client.get(f"{host}/robots.txt")
            if response.status_code == 200 and "html" not in response.headers.get("content-type", ""):
                parser = urllib.robotparser.RobotFileParser()
                parser.parse(response.text.splitlines())
        except httpx.HTTPError as exc:  # robots 抓不到就視為允許，但記錄
            log.debug("robots.txt unavailable for %s: %s", host, exc)
        self._robots[host] = parser
        return parser

    def allowed_by_robots(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parser = self._robots_for(url)
        if parser is None:
            return True
        return parser.can_fetch(self.user_agent, url) and parser.can_fetch("*", url)

    # ---- rate limit ----
    def _wait_for_slot(self, url: str, delay: float | None) -> None:
        delay = self.request_delay if delay is None else delay
        host = urlsplit(url).netloc
        last = self._last_request_at.get(host)
        if last is not None and delay > 0:
            elapsed = time.monotonic() - last
            if elapsed < delay:
                time.sleep(delay - elapsed)
        self._last_request_at[host] = time.monotonic()

    # ---- fetch ----
    def get(self, url: str, *, delay: float | None = None) -> FetchResult:
        if not self.allowed_by_robots(url):
            raise FetchError(url, "robots.txt 不允許抓取此路徑")
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            self._wait_for_slot(url, delay)
            try:
                self.request_count += 1
                response = self._client.get(url)
                if response.status_code in RETRYABLE_STATUS:
                    raise FetchError(url, f"HTTP {response.status_code}", response.status_code)
                if response.status_code >= 400:
                    raise FetchError(url, f"HTTP {response.status_code}", response.status_code)
                content_type = response.headers.get("content-type", "").lower()
                text = ""
                if "pdf" not in content_type and not response.content[:5] == b"%PDF-":
                    text = decode_body(response.content, response.charset_encoding)
                return FetchResult(
                    url=url,
                    final_url=str(response.url),
                    status_code=response.status_code,
                    content=response.content,
                    text=text,
                    content_type=content_type,
                    headers=dict(response.headers),
                )
            except FetchError as exc:
                last_error = exc
                if exc.status_code is not None and exc.status_code not in RETRYABLE_STATUS:
                    raise
            except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
                last_error = FetchError(url, f"{type(exc).__name__}: {exc}")
            if attempt < self.max_retries:
                sleep_for = min(self.backoff_max, self.backoff_base * (2**attempt)) + random.uniform(0, 0.5)
                log.warning("retry %d/%d for %s in %.1fs (%s)", attempt + 1, self.max_retries, url, sleep_for, last_error)
                time.sleep(sleep_for)
        assert last_error is not None
        raise last_error

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "PoliteHttpClient":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def fetch_rendered(url: str, *, wait_selector: str | None = None, timeout_ms: int = 30000) -> str:
    """需要 JavaScript 的頁面才用 Playwright（可選依賴；未安裝瀏覽器時丟出明確錯誤）。

    使用前需執行：pip install playwright && playwright install chromium
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise FetchError(url, "Playwright 未安裝：pip install playwright && playwright install chromium") from exc
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            if wait_selector:
                page.wait_for_selector(wait_selector, timeout=timeout_ms)
            return page.content()
        finally:
            browser.close()
