"""Crawler 管理（v2 / MongoDB）：來源登錄、執行爬蟲、寫入 raw_documents、crawl_jobs / crawl_logs。

單一來源失敗只影響該來源；每筆文件以 (source_id, source_url) 為唯一鍵，內容 hash 相同就只更新 last_seen_at。
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from benefit_crawler.base.base_crawler import RawDocumentData
from benefit_crawler.base.http_client import PoliteHttpClient
from benefit_crawler.base.registry import build_crawler, load_sources_config, select_sources
from benefit_crawler.base.source_validator import SourceValidator

from ..config import Settings, get_settings
from ..db import get_db, utcnow

log = logging.getLogger(__name__)


def _settings() -> Settings:
    return get_settings()


def source_configs() -> list[dict]:
    return load_sources_config(_settings().sources_config_file)


def _validator() -> SourceValidator:
    return SourceValidator(_settings().official_domains_file)


def _http() -> PoliteHttpClient:
    settings = _settings()
    return PoliteHttpClient(
        user_agent=settings.user_agent,
        timeout=settings.http_timeout_seconds,
        max_retries=settings.http_max_retries,
        request_delay=settings.request_delay_seconds,
        respect_robots=settings.respect_robots_txt,
        strict_x509=settings.ssl_strict_x509,
    )


# ---------------------------------------------------------------- sources
def ensure_sources() -> list[dict]:
    """把 sources.yaml 同步到 sources 集合（只新增／更新設定欄位，不刪除；保留執行狀態）。"""
    validator = _validator()
    db = get_db()
    rows: list[dict] = []
    for config in source_configs():
        validation = validator.validate_url(config["base_url"])
        existing = db.sources.find_one({"_id": config["id"]}) or {}
        pages = config.get("pages") or []
        doc = {
            "_id": config["id"],
            "name": config["name"],
            "organization": config.get("organization", ""),
            "provider_type": config.get("provider_type", "unknown"),
            "source_type": config.get("source_type", "government_site"),
            "base_url": config["base_url"],
            "official_domain": urlsplit(config["base_url"]).netloc,
            "crawler_class": config.get("crawler", ""),
            "enabled": bool(config.get("enabled", True)),
            "request_delay_seconds": float(config.get("request_delay_seconds", 1.0)),
            "data_confidence": int(config.get("data_confidence", 95)),
            "notes": config.get("notes", "") or "",
            "domains": list(config.get("domains") or []),
            "pages_total": len(pages),
            "pages_skipped": sum(1 for p in pages if p.get("skip")),
            "follow_links": bool(config.get("follow_links")),
            "updated_at": utcnow(),
        }
        if not existing:
            doc["created_at"] = utcnow()
            doc.update({"last_run_at": None, "last_status": "never", "last_record_count": 0, "last_error": ""})
        if not existing.get("last_run_at"):
            doc["source_verified"] = validation.verified
            doc["source_verification_method"] = validation.method
            doc["source_status"] = "disabled" if not doc["enabled"] else validation.status
            doc["verification_details"] = validation.to_dict()
        elif not doc["enabled"]:
            doc["source_status"] = "disabled"
        db.sources.update_one({"_id": config["id"]}, {"$set": doc, "$setOnInsert": {}}, upsert=True)
        rows.append({**existing, **doc})
    return rows


def describe_sources() -> list[str]:
    validator = _validator()
    lines = []
    for config in source_configs():
        validation = validator.validate_url(config["base_url"])
        flag = "✅" if validation.verified else "⚠️"
        enabled = "enabled " if config.get("enabled", True) else "disabled"
        pages = config.get("pages") or []
        extra = f" pages={len(pages)}" if pages else ""
        lines.append(f"{flag} {config['id']:<18} {enabled} {config['provider_type']:<20} {config['name']}{extra}  [{validation.method}]")
    return lines


# ------------------------------------------------------------- persistence
def _raw_file_path(source_id: str, content_hash: str, suffix: str = ".html") -> Path:
    directory = _settings().raw_storage_path / source_id
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{content_hash[:16]}{suffix}"


def persist_document(source_id: str, source_name: str, document: RawDocumentData, counters: dict[str, int]) -> str:
    """寫入／更新 raw_documents；回傳 raw_document id。"""
    db = get_db()
    content_hash = document.content_hash()
    now = utcnow()
    file_path = ""
    if document.full_html:
        path = _raw_file_path(source_id, content_hash)
        if not path.exists():
            path.write_text(document.full_html, encoding="utf-8")
        file_path = str(path)
    meta = dict(document.meta or {})
    rows = meta.pop("rows", None)  # 資料集列另存欄位，避免 meta 過大
    base = {
        "source_id": source_id,
        "source_name": source_name,
        "source_url": document.source_url,
        "title": (document.title or "")[:500],
        "content_type": document.content_type,
        "raw_html": document.raw_html,
        "raw_text": document.raw_text,
        "structured": document.structured or {},
        "meta": meta,
        "attachments": document.attachments or [],
        "file_path": file_path,
        "content_hash": content_hash,
        "published_date": document.published_date or "",
        "last_seen_at": now,
        "last_crawled_at": now,
    }
    if rows is not None:
        base["rows"] = rows
    existing = db.raw_documents.find_one({"source_id": source_id, "source_url": document.source_url}, {"content_hash": 1, "file_path": 1, "published_date": 1, "title": 1})
    if existing is None:
        status = "skipped" if document.content_type == "skipped" else "new"
        doc = {
            "_id": str(uuid.uuid4()),
            **base,
            "crawl_time": now,
            "first_seen_at": now,
            "classification": None,
            "processing_status": status,
            "processing_error": "",
            "processed_at": None,
            "skip_reason": meta.get("skip_reason", "") if status == "skipped" else "",
        }
        db.raw_documents.insert_one(doc)
        counters["new"] = counters.get("new", 0) + 1
        return doc["_id"]
    if existing.get("content_hash") != content_hash:
        skipped = document.content_type == "skipped"
        update = {**base, "crawl_time": now, "processing_status": "skipped" if skipped else "new", "processing_error": "", "skip_reason": meta.get("skip_reason", "") if skipped else ""}
        if not file_path:
            update.pop("file_path")
        if not document.published_date:
            update.pop("published_date")
        if skipped:
            # 原本是補助頁、這次判定為略過（例如被認定是重複網址）→ 移除舊的 benefit，避免資料中心殘留
            update["benefit_id"] = None
            db.benefits.delete_many({"raw_document_id": existing["_id"]})
        db.raw_documents.update_one({"_id": existing["_id"]}, {"$set": update})
        counters["updated"] = counters.get("updated", 0) + 1
    else:
        touch = {"last_seen_at": now, "last_crawled_at": now}
        # 內容沒變但標題判定方式改了（例如連結文字 → 頁面標題）：一併更新標題，pipeline 重跑時 benefit 會跟著更新
        if base["title"] and base["title"] != existing.get("title"):
            touch["title"] = base["title"]
            touch["meta.page_title"] = meta.get("page_title", "")
        db.raw_documents.update_one({"_id": existing["_id"]}, {"$set": touch})
        counters["unchanged"] = counters.get("unchanged", 0) + 1
    return existing["_id"]


# ---------------------------------------------------------------- running
def run_sources(source_ids: list[str] | None = None, *, triggered_by: str = "manual", max_items: int | None = None) -> list[dict]:
    settings = _settings()
    configs = select_sources(source_configs(), ids=source_ids)
    validator = _validator()
    http = _http()
    summaries: list[dict] = []
    try:
        for config in configs:
            summaries.append(_run_one(config, http=http, validator=validator, triggered_by=triggered_by, max_items=max_items or settings.max_items_per_source or None))
    finally:
        http.close()
    return summaries


def _run_one(config: dict, *, http: PoliteHttpClient, validator: SourceValidator, triggered_by: str, max_items: int | None) -> dict:
    db = get_db()
    source_id = config["id"]
    job_id = str(uuid.uuid4())
    started = utcnow()
    db.crawl_jobs.insert_one({"_id": job_id, "source_id": source_id, "status": "running", "triggered_by": triggered_by, "started_at": started, "finished_at": None,
                              "discovered": 0, "fetched": 0, "failed_items": 0, "new_documents": 0, "updated_documents": 0, "unchanged_documents": 0, "error": ""})
    counters: dict[str, int] = {"new": 0, "updated": 0, "unchanged": 0}
    status = "failed"
    result = None
    error = ""
    try:
        crawler = build_crawler(config, http=http, validator=validator, max_items=max_items)
        result = crawler.run(on_document=lambda doc: persist_document(source_id, config["name"], doc, counters))
        status = result.status
        error = "\n".join(result.errors[:20])
    except Exception as exc:  # 建立 crawler 本身失敗
        log.exception("source %s crashed", source_id)
        error = f"{type(exc).__name__}: {exc}"
    finished = utcnow()
    job_update = {"finished_at": finished, "status": status, "error": error, "new_documents": counters["new"], "updated_documents": counters["updated"], "unchanged_documents": counters["unchanged"]}
    if result is not None:
        job_update.update({"discovered": result.discovered, "fetched": result.fetched, "failed_items": result.failed})
        logs = [{"job_id": job_id, "source_id": source_id, "level": level, "message": message[:2000], "url": url[:1000], "created_at": finished} for level, message, url in result.logs[-300:]]
        if logs:
            db.crawl_logs.insert_many(logs)
    db.crawl_jobs.update_one({"_id": job_id}, {"$set": job_update})
    source_update = {"last_run_at": finished, "last_status": status, "last_record_count": result.fetched if result else 0, "last_error": error[:2000]}
    if result is not None and result.validation is not None:
        source_update.update({"source_verified": result.validation.verified, "source_verification_method": result.validation.method, "source_status": result.validation.status, "verification_details": result.validation.to_dict()})
    db.sources.update_one({"_id": source_id}, {"$set": source_update})
    return {
        "source_id": source_id,
        "job_id": job_id,
        "status": status,
        "discovered": result.discovered if result else 0,
        "fetched": result.fetched if result else 0,
        "failed_items": result.failed if result else 0,
        "new_documents": counters["new"],
        "updated_documents": counters["updated"],
        "unchanged_documents": counters["unchanged"],
        "error": error,
    }


def dry_run(source_ids: list[str] | None = None, max_items: int | None = None) -> list[str]:
    validator = _validator()
    http = _http()
    lines: list[str] = []
    try:
        for config in select_sources(source_configs(), ids=source_ids):
            crawler = build_crawler(config, http=http, validator=validator, max_items=max_items or 5)
            result = crawler.run()
            lines.append(f"[{config['id']}] {result.status}: discovered={result.discovered} fetched={result.fetched} failed={result.failed}")
            if result.validation:
                lines.append(f"    validation: verified={result.validation.verified} method={result.validation.method}")
            for document in result.documents[:8]:
                lines.append(f"    - [{document.content_type}] {document.title[:60]} | {document.source_url[:90]}")
                lines.append(f"      structured keys: {list(document.structured)[:6]} text={len(document.raw_text)} chars")
            for err in result.errors[:3]:
                lines.append(f"    ! {err}")
    finally:
        http.close()
    return lines


def content_sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
