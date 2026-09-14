"""GET /api/benefits、/api/benefits/search、/api/benefits/{id}、/api/benefits/{id}/raw、/api/providers。"""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, Query

from ..db import get_db
from ..registry import get_registry
from ..services.normalization import normalize_city, normalize_text
from .serializers import benefit_detail, benefit_summary, provider_to_dict, raw_document_to_dict, rule_to_dict, source_to_dict

router = APIRouter(prefix="/api", tags=["benefits"])

# classification 只留摘要要用的旗標（uncertain / category_uncertain / decision_basis / method），笨重的訊號與命中詞不回傳
SUMMARY_PROJECTION = {"original_text": 0, "evidence": 0, "conditions": 0, "structured_fields": 0, "classification.signals": 0, "classification.reasons": 0, "classification.matched_category": 0, "classification.matched_signal": 0, "classification.category_scores": 0, "classification.llm": 0}


def _query(keyword: str | None, domain: str | None, category: str | None, provider: str | None, provider_type: str | None, benefit_form: str | None, application_status: str, needs_review: bool | None, canonical_only: bool, source_id: str | None, region: str | None, education_level: str | None, min_amount: float | None, overview: str, kind: str = "program", uncertain: bool | None = None) -> dict:
    query: dict = {}
    # 收錄政策：預設只列補助方案（record_kind=program）；彙整頁（portal）保留供查閱
    if kind == "program":
        query["record_kind"] = {"$ne": "portal"}
    elif kind == "portal":
        query["record_kind"] = "portal"
    if canonical_only:
        query["is_canonical"] = True
    if domain:
        query["domain"] = domain
    if category:
        query.setdefault("$and", []).append({"$or": [{"category": category}, {"categories_secondary": category}]})  # 主類別或次類別命中都算
    if provider_type:
        query["provider_type"] = provider_type
    if provider:
        query["provider"] = {"$regex": re.escape(provider)}
    if benefit_form:
        query["benefit.benefit_form"] = benefit_form
    if source_id:
        query["source_id"] = source_id
    if application_status == "active":
        query["status"] = {"$ne": "expired"}
    elif application_status == "expired":
        query["status"] = "expired"
    if needs_review is not None:
        query["review.needs_review"] = needs_review
    if uncertain is not None:
        query["classification.uncertain"] = True if uncertain else {"$ne": True}
    if overview == "hide":
        query["is_overview"] = {"$ne": True}
    elif overview == "only":
        query["is_overview"] = True
    if education_level:
        query["index.education_levels"] = education_level
    if region:
        city = normalize_city(region) or region
        query.setdefault("$and", []).append({"$or": [{"index.residence_cities": city}, {"provider_region": city}, {"provider": {"$regex": re.escape(city)}}, {"title": {"$regex": re.escape(city)}}]})
    if min_amount is not None:
        query["$expr"] = {"$gte": [{"$ifNull": ["$index.amount_max", {"$ifNull": ["$benefit.amount.value", 0]}]}, min_amount]}
    if keyword:
        needle = keyword.strip()
        alt = needle.replace("台", "臺")
        patterns = [{"title": {"$regex": re.escape(needle), "$options": "i"}}, {"provider": {"$regex": re.escape(needle), "$options": "i"}}, {"keywords": needle}, {"original_text": {"$regex": re.escape(needle)}}]
        if alt != needle:
            patterns += [{"title": {"$regex": re.escape(alt)}}, {"original_text": {"$regex": re.escape(alt)}}]
        query.setdefault("$and", []).append({"$or": patterns})
    return query


@router.get("/benefits")
def list_benefits(
    keyword: str | None = Query(None),
    domain: str | None = Query(None),
    category: str | None = Query(None),
    provider: str | None = Query(None),
    provider_type: str | None = Query(None),
    benefit_form: str | None = Query(None),
    region: str | None = Query(None),
    education_level: str | None = Query(None),
    min_amount: float | None = Query(None),
    application_status: str = Query("active", pattern="^(active|expired|all)$"),
    needs_review: bool | None = Query(None),
    canonical_only: bool = Query(True),
    source_id: str | None = Query(None),
    overview: str = Query("all", pattern="^(all|hide|only)$"),
    kind: str = Query("program", pattern="^(program|portal|all)$"),
    uncertain: bool | None = Query(None),
    sort: str = Query("updated", pattern="^(updated|deadline|title)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
) -> dict:
    db = get_db()
    query = _query(keyword, domain, category, provider, provider_type, benefit_form, application_status, needs_review, canonical_only, source_id, region, education_level, min_amount, overview, kind, uncertain)
    total = db.benefits.count_documents(query)
    if sort == "deadline":
        order = [("benefit.application_period.end_date", 1), ("updated_at", -1)]
    elif sort == "title":
        order = [("title", 1)]
    else:
        order = [("updated_at", -1)]
    cursor = db.benefits.find(query, SUMMARY_PROJECTION).sort(order).skip((page - 1) * page_size).limit(page_size)
    items = [benefit_summary(row) for row in cursor]
    if sort == "deadline":
        items.sort(key=lambda i: (i["application_period"].get("end_date") or "9999"))
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/benefits/search")
def search_benefits(keyword: str = Query(..., min_length=1), domain: str | None = None, category: str | None = None, application_status: str = Query("active", pattern="^(active|expired|all)$"), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=500)) -> dict:
    return list_benefits(keyword=keyword, domain=domain, category=category, provider=None, provider_type=None, benefit_form=None, region=None, education_level=None, min_amount=None, application_status=application_status, needs_review=None, canonical_only=True, source_id=None, overview="all", sort="updated", page=page, page_size=page_size, kind="program", uncertain=None)


@router.get("/benefits/{benefit_id}")
def get_benefit(benefit_id: str, include_html: bool = Query(False)) -> dict:
    db = get_db()
    row = db.benefits.find_one({"_id": benefit_id})
    if row is None:
        raise HTTPException(status_code=404, detail="benefit not found")
    doc = db.raw_documents.find_one({"_id": row.get("raw_document_id")}, {"rows": 0} if include_html else {"rows": 0, "raw_html": 0})
    source = db.sources.find_one({"_id": row.get("source_id")})
    related = list(db.benefits.find({"canonical_id": row.get("canonical_id"), "_id": {"$ne": benefit_id}}, {"title": 1, "source_id": 1, "source": 1, "is_canonical": 1, "provider": 1}))
    registry = get_registry()
    providers = []
    if row.get("domain") in {"long_term_care", "social_welfare", "disability"}:
        city = row.get("provider_region") or ""
        providers = [provider_to_dict(p) for p in db.providers.find({"city": city} if city and city != "national" else {}).limit(12)]
    return {
        "benefit": benefit_summary(row),
        "schema": benefit_detail(row),
        "rules": [rule_to_dict(rule) for rule in row.get("rules") or []],
        "evidence": row.get("evidence") or [],
        "conditions": row.get("conditions") or [],
        "llm": row.get("llm") or {},
        "classification": row.get("classification") or {},
        "raw_document": raw_document_to_dict(doc, include_html=include_html) if doc else None,
        "source": source_to_dict(source) if source else None,
        "related_records": [{"id": r["_id"], "source_id": r.get("source_id", ""), "source_name": (r.get("source") or {}).get("source_name", ""), "source_url": (r.get("source") or {}).get("source_url", ""), "is_canonical": bool(r.get("is_canonical")), "provider": r.get("provider", ""), "title": r.get("title", "")} for r in related],
        "providers_nearby": providers,
        "registry_version": registry.version,
    }


@router.get("/benefits/{benefit_id}/raw")
def get_benefit_raw(benefit_id: str) -> dict:
    db = get_db()
    row = db.benefits.find_one({"_id": benefit_id}, {"raw_document_id": 1})
    if row is None:
        raise HTTPException(status_code=404, detail="benefit not found")
    doc = db.raw_documents.find_one({"_id": row.get("raw_document_id")}, {"rows": 0})
    if doc is None:
        raise HTTPException(status_code=404, detail="raw document not found")
    return raw_document_to_dict(doc, include_html=True)


@router.get("/raw-documents")
def list_raw_documents(source_id: str | None = None, processing_status: str | None = None, keyword: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=500)) -> dict:
    db = get_db()
    query: dict = {}
    if source_id:
        query["source_id"] = source_id
    if processing_status:
        query["processing_status"] = processing_status
    if keyword:
        query["$or"] = [{"title": {"$regex": re.escape(keyword)}}, {"source_url": {"$regex": re.escape(keyword)}}]
    total = db.raw_documents.count_documents(query)
    rows = db.raw_documents.find(query, {"raw_html": 0, "raw_text": 0, "rows": 0, "structured": 0}).sort("crawl_time", -1).skip((page - 1) * page_size).limit(page_size)
    return {"items": [raw_document_to_dict(r) | {"raw_text": ""} for r in rows], "total": total, "page": page, "page_size": page_size}


@router.get("/providers")
def list_providers(city: str | None = None, kind: str | None = None, keyword: str | None = None, limit: int = Query(100, ge=1, le=1000)) -> dict:
    db = get_db()
    query: dict = {}
    if city:
        query["city"] = normalize_city(city) or city
    if kind:
        query["service_kind"] = kind
    if keyword:
        query["$or"] = [{"name": {"$regex": re.escape(keyword)}}, {"address": {"$regex": re.escape(keyword)}}]
    rows = [provider_to_dict(r) for r in db.providers.find(query).limit(limit)]
    kinds = [k["_id"] for k in db.providers.aggregate([{"$group": {"_id": "$service_kind"}}])]
    return {"items": rows, "total": db.providers.count_documents(query), "kinds": kinds}
