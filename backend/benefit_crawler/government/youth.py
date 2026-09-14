"""教育部青年發展署（https://www.yda.gov.tw/）。

Status: TODO — 官網主選單由 JavaScript 動態產生，尚未找到可穩定爬取的獎補助清單頁。
crawler 沿用 StaticPagesCrawler：在 sources.yaml 的 pages 補上經人工確認的官方頁面 URL 後即可啟用（enabled: true）。
若清單頁必須由 JS 產生，可改用 benefit_crawler.base.http_client.fetch_rendered（Playwright）取得 HTML。
"""

from __future__ import annotations

from ..base.base_crawler import StaticPagesCrawler


class YouthDevelopmentCrawler(StaticPagesCrawler):
    content_selectors = [".content", "#content", "main", "article"]
