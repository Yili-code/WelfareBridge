"""把 v1（SQL 版）demo_seed.json 裡的原始文件匯入 MongoDB，讓舊資料重新走 v2 pipeline。

只匯入 sources（執行狀態）與 raw_documents（原文、結構化欄位、爬取時間）；v1 的解析結果（scholarships / eligibility_rules）
不匯入，一律由 v2 extractor 重新產生，避免兩套 schema 混用。
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from ..config import get_settings
from ..db import get_db, utcnow

log = logging.getLogger(__name__)
DATETIME_FIELDS = {"crawl_time", "first_seen_at", "last_seen_at", "last_crawled_at", "last_run_at"}


def _dt(value):
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return value


def import_legacy_seed(path: str | Path | None = None) -> dict:
    settings = get_settings()
    source = Path(path) if path else settings.legacy_seed_file
    if not source.exists():
        return {"error": f"legacy seed not found: {source}"}
    payload = json.loads(source.read_text(encoding="utf-8"))
    db = get_db()
    stats = {"sources": 0, "raw_documents": 0, "skipped_existing": 0}
    for data in payload.get("sources", []):
        if db.sources.find_one({"_id": data["id"]}):
            update = {k: _dt(v) if k in DATETIME_FIELDS else v for k, v in data.items() if k in {"last_run_at", "last_status", "last_record_count", "source_verified", "source_verification_method", "source_status", "verification_details"} and v is not None}
            if update:
                db.sources.update_one({"_id": data["id"]}, {"$set": update})
            stats["sources"] += 1
    for data in payload.get("raw_documents", []):
        if db.raw_documents.find_one({"_id": data["id"]}) or db.raw_documents.find_one({"source_id": data["source_id"], "source_url": data["source_url"]}):
            stats["skipped_existing"] += 1
            continue
        structured = dict(data.get("structured") or {})
        meta = structured.pop("_meta", None) or {}
        doc = {
            "_id": data["id"],
            "source_id": data["source_id"],
            "source_name": data.get("source_name", ""),
            "source_url": data["source_url"],
            "title": data.get("title", ""),
            "content_type": data.get("content_type", "html"),
            "raw_html": data.get("raw_html", ""),
            "raw_text": data.get("raw_text", ""),
            "structured": structured,
            "meta": {**meta, "legacy_import": True, "document_kind": meta.get("document_kind", "page")},
            "attachments": data.get("attachments") or [],
            "file_path": data.get("file_path", ""),
            "content_hash": data.get("content_hash", ""),
            "published_date": data.get("published_date", "") or "",
            "crawl_time": _dt(data.get("crawl_time")) or utcnow(),
            "first_seen_at": _dt(data.get("first_seen_at")) or utcnow(),
            "last_seen_at": _dt(data.get("last_seen_at")) or utcnow(),
            "last_crawled_at": _dt(data.get("last_crawled_at")) or utcnow(),
            "classification": None,
            "processing_status": "new",
            "processing_error": "",
            "processed_at": None,
            "skip_reason": "",
        }
        db.raw_documents.insert_one(doc)
        stats["raw_documents"] += 1
    log.info("legacy seed imported: %s", stats)
    return stats
