"""儀表板統計、登錄表、表單選項、關鍵字統計。"""

from __future__ import annotations

from fastapi import APIRouter

from ..config import get_settings
from ..db import get_db
from ..llm.factory import ollama_status
from ..registry import get_registry
from ..services.classifier import get_classifier
from ..services.normalization import CITIES, taiwan_day_start_utc
from .serializers import AWARD_BASIS_LABELS, BENEFIT_FORM_LABELS, CHANNEL_LABELS, DISLIKE_LABELS, NEED_TYPE_LABELS, PROVIDER_TYPE_LABELS, iso

router = APIRouter(prefix="/api", tags=["meta"])


def _group_counts(db, collection: str, field: str, query: dict | None = None) -> dict[str, int]:
    pipeline = [{"$match": query or {}}, {"$group": {"_id": f"${field}", "n": {"$sum": 1}}}]
    return {(row["_id"] if row["_id"] is not None else ""): row["n"] for row in db[collection].aggregate(pipeline)}


@router.get("/stats")
def stats() -> dict:
    db = get_db()
    registry = get_registry()
    settings = get_settings()
    today_start = taiwan_day_start_utc()
    sources = list(db.sources.find({}))
    last_updated = db.benefits.find_one({}, {"updated_at": 1}, sort=[("updated_at", -1)])
    last_job = db.crawl_jobs.find_one({"finished_at": {"$ne": None}}, {"finished_at": 1}, sort=[("finished_at", -1)])
    keyword_stats = db.keyword_stats.find_one({"_id": "latest"}) or {}
    by_domain = _group_counts(db, "benefits", "domain")
    by_category = _group_counts(db, "benefits", "category")
    return {
        "benefits_total": db.benefits.count_documents({}),
        "benefits_canonical": db.benefits.count_documents({"is_canonical": True}),
        "benefits_active": db.benefits.count_documents({"status": "active"}),
        "benefits_expired": db.benefits.count_documents({"status": "expired"}),
        "benefits_overview": db.benefits.count_documents({"is_overview": True}),
        "benefits_programs": db.benefits.count_documents({"is_canonical": True, "record_kind": {"$ne": "portal"}}),
        "benefits_portals": db.benefits.count_documents({"record_kind": "portal"}),
        "quality_verified": db.benefits.count_documents({"is_canonical": True, "admission.quality_tier": "verified"}),
        "uncertain": db.benefits.count_documents({"is_canonical": True, "classification.uncertain": True}),
        "today_new": db.benefits.count_documents({"first_seen_at": {"$gte": today_start}}),
        "needs_review": db.benefits.count_documents({"review.needs_review": True}),
        "llm_processed": db.benefits.count_documents({"llm.processed": True}),
        "with_rules": db.benefits.count_documents({"index.simple_rules": {"$gt": 0}}),
        "providers_total": db.providers.count_documents({}),
        "last_updated": iso(last_updated.get("updated_at")) if last_updated else None,
        "last_crawl": iso(last_job.get("finished_at")) if last_job else None,
        "official_sources": sum(1 for s in sources if s.get("source_verified")),
        "sources_enabled": sum(1 for s in sources if s.get("enabled")),
        "sources_total": len(sources),
        "crawlers_success": sum(1 for s in sources if s.get("last_status") in {"success", "partial"}),
        "crawlers_failed": sum(1 for s in sources if s.get("last_status") in {"failed", "skipped"}),
        "crawlers_never_run": sum(1 for s in sources if s.get("last_status", "never") == "never"),
        "raw_documents_total": db.raw_documents.count_documents({}),
        "raw_documents_by_status": _group_counts(db, "raw_documents", "processing_status"),
        "by_domain": {k: {"count": v, "label": registry.domain_label(k)} for k, v in by_domain.items()},
        "by_category": {k: {"count": v, "label": registry.category_label(k), "domain": registry.domain_of(k)} for k, v in by_category.items()},
        "by_provider_type": {k: {"count": v, "label": PROVIDER_TYPE_LABELS.get(k, k)} for k, v in _group_counts(db, "benefits", "provider_type").items()},
        "by_benefit_form": {k: {"count": v, "label": BENEFIT_FORM_LABELS.get(k, k)} for k, v in _group_counts(db, "benefits", "benefit.benefit_form").items()},
        "by_source": _group_counts(db, "benefits", "source_id"),
        "registry": {"version": registry.version, "attributes": len(registry.attributes), "categories": len(registry.leaves()), "domains": len(registry.domains()), "tags": len(registry.tags)},
        "keyword_stats": {"generated_at": keyword_stats.get("generated_at"), "corpus": keyword_stats.get("corpus"), "benefit_terms": keyword_stats.get("benefit_terms"), "negative_terms": keyword_stats.get("negative_terms"), "categories_mined": keyword_stats.get("categories_mined")},
        "llm": {"provider": settings.llm_provider, **ollama_status(settings)},
        "review_open": db.review_items.count_documents({"status": "open"}),
    }


@router.get("/registry")
def registry_view() -> dict:
    registry = get_registry()
    db = get_db()
    usage = {}
    for row in db.benefits.aggregate([{"$unwind": "$rules"}, {"$group": {"_id": "$rules.attribute_id", "n": {"$sum": 1}}}]):
        usage[row["_id"]] = row["n"]
    attributes = []
    for attribute in registry.attributes.values():
        data = attribute.to_dict()
        data["rules_using"] = usage.get(attribute.id, 0)
        attributes.append(data)
    return {
        "version": registry.version,
        "taxonomy_version": registry.taxonomy_version,
        "attributes": attributes,
        "taxonomy": [node.to_dict() for node in registry.taxonomy.values()],
        "identity_ontology": [tag.to_dict() for tag in registry.tags.values()],
        "poverty_line": {"verified": bool(registry.poverty.get("verified")), "year": registry.poverty.get("year"), "source_url": registry.poverty.get("source_url")},
        "catalog": registry.catalog(),
    }


@router.get("/keywords")
def keywords_view() -> dict:
    classifier = get_classifier()
    db = get_db()
    stats_row = db.keyword_stats.find_one({"_id": "latest"}) or {}
    return {"source": classifier.rules_source, "generated_at": classifier.rules.get("generated_at"), "method": classifier.rules.get("method"), "corpus": classifier.rules.get("corpus") or stats_row.get("corpus"), "threshold": classifier.threshold, "table": classifier.keyword_table(), "condition_cues": classifier.condition_cues, "report_path": stats_row.get("report_path")}


@router.get("/categories")
def categories() -> list[dict]:
    registry = get_registry()
    return [{"value": leaf.id, "label": leaf.label, "domain": leaf.domain, "domain_label": registry.domain_label(leaf.domain), "need_types": leaf.need_types} for leaf in registry.leaves()]


@router.get("/meta/options")
def options() -> dict:
    registry = get_registry()
    catalog = registry.catalog()
    step_order = [a.id for a in sorted(registry.askable(), key=lambda a: (-a.ask_priority, a.id))]
    return {
        "cities": list(CITIES),
        "domains": [{"value": d.id, "label": d.label, "description": d.description} for d in registry.domains()],
        "categories": [{"value": leaf.id, "label": leaf.label, "domain": leaf.domain} for leaf in registry.leaves()],
        "provider_types": [{"value": k, "label": v} for k, v in PROVIDER_TYPE_LABELS.items()],
        "benefit_forms": [{"value": k, "label": v} for k, v in BENEFIT_FORM_LABELS.items()],
        "award_basis": [{"value": k, "label": v} for k, v in AWARD_BASIS_LABELS.items()],
        "channels": [{"value": k, "label": v} for k, v in CHANNEL_LABELS.items()],
        "need_types": [{"value": k, "label": v} for k, v in NEED_TYPE_LABELS.items()],
        "dislikes": [{"value": k, "label": v} for k, v in DISLIKE_LABELS.items()],
        "education_levels": [{"value": v.get("value"), "label": v.get("label")} for v in (registry.get("education.level").values if registry.get("education.level") else [])],
        "catalog": catalog,
        "field_catalog": catalog,
        "step_order": step_order,
        "namespaces": {"applicant": "基本資料", "education": "就學", "academic": "成績", "residence": "戶籍與居住", "household": "家庭經濟", "financial": "補助與保險", "identity": "身分", "disability": "身心障礙", "care": "長期照顧", "health": "健康", "employment": "就業", "housing": "住宅", "family": "家庭"},
        "registry_version": registry.version,
    }
