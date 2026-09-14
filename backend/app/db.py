"""MongoDB 連線與集合定義（v2）。

集合：
    sources             官方來源登錄與最近執行狀態（_id = source id）
    raw_documents       原始文件（原文不改動；分類結果、處理狀態）
    benefits            標準化補助（core + benefit meta + rules[] + evidence[]）
    providers           服務提供者名單（機構、特約單位；來自官方開放資料）
    attribute_registry  屬性登錄表（YAML 載入；_id = attribute id）
    taxonomy            領域／類別樹（YAML 載入）
    identity_ontology   身分本體（YAML 載入）
    user_profiles / match_results / feedback_events / review_items
    crawl_jobs / crawl_logs / keyword_stats / app_meta
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from functools import lru_cache

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from .config import get_settings

log = logging.getLogger(__name__)

COLLECTIONS = [
    "sources", "raw_documents", "benefits", "providers", "attribute_registry", "taxonomy", "identity_ontology",
    "user_profiles", "match_results", "feedback_events", "review_items", "crawl_jobs", "crawl_logs", "keyword_stats", "app_meta",
]


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@lru_cache
def get_client() -> MongoClient:
    settings = get_settings()
    return MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=5000, tz_aware=False)


def get_db() -> Database:
    return get_client()[get_settings().mongodb_db]


def ping() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except Exception as exc:  # pragma: no cover - 連線失敗
        log.warning("MongoDB ping failed: %s", exc)
        return False


def init_db() -> Database:
    """建立索引（冪等）。"""
    db = get_db()
    db.raw_documents.create_index([("source_id", ASCENDING), ("source_url", ASCENDING)], unique=True, name="ux_source_url")
    db.raw_documents.create_index([("content_hash", ASCENDING)], name="ix_hash")
    db.raw_documents.create_index([("processing_status", ASCENDING)], name="ix_status")
    db.raw_documents.create_index([("classification.category", ASCENDING)], name="ix_category")
    db.benefits.create_index([("raw_document_id", ASCENDING)], name="ix_raw_document")
    db.benefits.create_index([("canonical_id", ASCENDING)], name="ix_canonical")
    db.benefits.create_index([("status", ASCENDING), ("is_canonical", ASCENDING)], name="ix_status_canonical")
    db.benefits.create_index([("domain", ASCENDING), ("category", ASCENDING)], name="ix_domain_category")
    db.benefits.create_index([("provider_type", ASCENDING)], name="ix_provider_type")
    db.benefits.create_index([("index.attribute_ids", ASCENDING)], name="ix_attribute_ids")
    db.benefits.create_index([("index.residence_cities", ASCENDING)], name="ix_residence")
    db.benefits.create_index([("index.education_levels", ASCENDING)], name="ix_levels")
    db.benefits.create_index([("application_period.end_date", ASCENDING)], name="ix_end_date")
    db.benefits.create_index([("updated_at", DESCENDING)], name="ix_updated")
    db.benefits.create_index([("title", "text"), ("provider", "text"), ("keywords", "text")], name="tx_title", default_language="none")
    db.providers.create_index([("source_id", ASCENDING), ("record_key", ASCENDING)], unique=True, name="ux_provider")
    db.providers.create_index([("city", ASCENDING), ("service_kind", ASCENDING)], name="ix_city_kind")
    db.crawl_jobs.create_index([("started_at", DESCENDING)], name="ix_started")
    db.crawl_logs.create_index([("job_id", ASCENDING)], name="ix_job")
    db.match_results.create_index([("profile_id", ASCENDING)], name="ix_profile")
    db.feedback_events.create_index([("benefit_id", ASCENDING)], name="ix_benefit")
    db.review_items.create_index([("status", ASCENDING), ("kind", ASCENDING)], name="ix_review")
    return db


def reset_db_for_tests() -> None:  # pragma: no cover - 測試用
    client = get_client()
    client.drop_database(get_settings().mongodb_db)
