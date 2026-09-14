"""基隆市政府教育處（https://www.klcg.gov.tw/tw/education/）。

版型：清單頁 /tw/education/3473.html → 公告 /tw/education/3473-322121.html
詳細頁：div.center_block > h2.title（標題）、section.cp（內文）、div.publish_info（發布日期／發布單位）
"""

from __future__ import annotations

from ..base.list_crawler import AnnouncementListCrawler


class KeelungEducationCrawler(AnnouncementListCrawler):
    item_link_pattern = r"/tw/education/\d+-\d+\.html$"
    page_link_pattern = r"/tw/education/\d+\.html\?page=\d+"
    title_selectors = ["div.center_block h2.title", "h2.title", "h1"]
    content_selectors = ["div.center_block section.cp", "section.cp", ".center_block"]
    date_selectors = [".publish_info"]
