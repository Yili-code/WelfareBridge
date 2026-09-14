"""各區／鄉／鎮公所公告（設定檔驅動的通用公告版 crawler）。

sources.yaml 範例：
    - id: district_offices
      crawler: benefit_crawler.township.district_offices.DistrictOfficeCrawler
      offices:
        - name: 基隆市中正區公所
          list_url: https://www.klcg.gov.tw/tw/zzdo/xxxx.html      # 經人工確認的公告清單頁
          item_link_pattern: "/tw/zzdo/\\d+-\\d+\\.html$"
          content_selectors: ["section.cp"]
      title_prefilter: "獎學金|助學金|獎助|補助"

Status: TODO — 尚未登錄經驗證的公所公告頁；補上 offices 後把 enabled 改為 true 即可。
每個 office 會各自跑一次 AnnouncementListCrawler，並以 office.name 作為 organization。
"""

from __future__ import annotations

from typing import Iterable

from ..base.base_crawler import BaseCrawler, DiscoveredItem, RawDocumentData
from ..base.http_client import FetchResult
from ..base.list_crawler import AnnouncementListCrawler


class _OfficeCrawler(AnnouncementListCrawler):
    pass


class DistrictOfficeCrawler(BaseCrawler):
    content_selectors = ["section.cp", "article", ".content", "main"]

    def __init__(self, source_config: dict, **kwargs):
        super().__init__(source_config, **kwargs)
        self._offices: list[_OfficeCrawler] = []
        for office in source_config.get("offices") or []:
            config = {
                **source_config,
                "id": f"{self.source_id}:{office.get('name', 'office')}",
                "name": office.get("name", ""),
                "organization": office.get("name", ""),
                "base_url": office["list_url"],
                "list_urls": [office["list_url"]],
                "item_link_pattern": office.get("item_link_pattern", r"\d+-\d+\.html$"),
                "page_link_pattern": office.get("page_link_pattern", ""),
                "content_selectors": office.get("content_selectors") or self.content_selectors,
                "offices": [],
            }
            self._offices.append(_OfficeCrawler(config, http=self.http, validator=self.validator, max_items=self.max_items))

    def discover(self) -> Iterable[DiscoveredItem]:
        for office in self._offices:
            validation = office.validate_source()
            if not validation.verified:
                self.log("WARNING", f"{office.name} 官方驗證未通過，略過：{'；'.join(validation.reasons)}", office.base_url)
                continue
            for item in office.discover():
                item.meta["office"] = office
                item.meta["organization"] = office.organization
                yield item

    def parse_detail(self, fetch: FetchResult, item: DiscoveredItem) -> RawDocumentData | None:
        office: _OfficeCrawler | None = item.meta.pop("office", None)
        if office is None:
            return None
        document = office.parse_detail(fetch, item)
        if document is not None:
            document.meta["organization"] = office.organization
        return document
