"""seed_v2.json：把「實際從官方來源爬取並解析」的 MongoDB 內容匯出／匯入，讓第一次啟動不必現場爬完。

seed 只包含真實爬取結果（sources / raw_documents / benefits / providers / crawl_jobs / keyword_stats / app_meta），沒有任何人工虛構資料；
每筆都保留 source_url、原文與 crawl_time。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from ..config import get_settings
from ..db import get_db

log = logging.getLogger(__name__)
COLLECTIONS = ["sources", "raw_documents", "benefits", "providers", "crawl_jobs", "keyword_stats", "app_meta", "review_items"]
DATETIME_FIELDS = {"created_at", "updated_at", "last_run_at", "crawl_time", "first_seen_at", "last_seen_at", "last_crawled_at", "processed_at", "started_at", "finished_at", "synced_at", "resolved_at"}


def _encode(value):
    if isinstance(value, datetime):
        return {"$date": value.isoformat()}
    if isinstance(value, dict):
        return {k: _encode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_encode(v) for v in value]
    return value


def _decode(value):
    if isinstance(value, dict):
        if set(value.keys()) == {"$date"}:
            try:
                return datetime.fromisoformat(value["$date"])
            except ValueError:
                return None
        return {k: _decode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_decode(v) for v in value]
    return value


def export_seed(path: str | Path | None = None) -> Path:
    settings = get_settings()
    target = Path(path) if path else settings.demo_seed_file
    target.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    payload: dict = {
        "exported_at": datetime.utcnow().isoformat(),
        "note": "全部來自官方來源實際爬取與解析結果（python -m benefit_crawler --export-seed）；不含任何人工虛構資料。raw_documents 省略 raw_html 以縮小檔案（原始 HTML 在 data/raw/）。",
    }
    for name in COLLECTIONS:
        rows = []
        for row in db[name].find({}):
            if name == "raw_documents":
                row = {k: v for k, v in row.items() if k not in {"raw_html", "rows"}}
            rows.append(_encode(row))
        payload[name] = rows
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info("seed exported: %s (%d benefits)", target, len(payload.get("benefits", [])))
    return target


def load_seed_if_empty(path: str | Path | None = None) -> int:
    settings = get_settings()
    source = Path(path) if path else settings.demo_seed_file
    if not source.exists():
        log.info("seed not found: %s", source)
        return 0
    db = get_db()
    if db.benefits.count_documents({}) > 0:
        return 0
    payload = json.loads(source.read_text(encoding="utf-8"))
    count = 0
    for name in COLLECTIONS:
        rows = payload.get(name) or []
        if not rows:
            continue
        for row in rows:
            decoded = _decode(row)
            db[name].update_one({"_id": decoded["_id"]}, {"$set": decoded}, upsert=True)
            if name == "benefits":
                count += 1
    log.info("seed loaded: %d benefits from %s", count, source)
    return count
