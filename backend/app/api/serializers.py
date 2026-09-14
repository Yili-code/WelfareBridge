"""MongoDB 文件 → API JSON（v2）。"""

from __future__ import annotations

from datetime import datetime, timezone

from ..registry import get_registry

PROVIDER_TYPE_LABELS = {
    "central_government": "中央政府", "local_government": "地方政府", "township": "鄉鎮市區公所", "school": "學校", "private_organization": "民間團體（經官方網站公告）", "mixed": "多個機關", "unknown": "未分類",
}
BENEFIT_FORM_LABELS = {"cash": "現金", "waiver": "減免", "service": "服務", "in_kind": "實物／輔具", "voucher": "額度／券", "loan": "貸款", "mixed": "混合"}
AWARD_BASIS_LABELS = {"criteria": "符合即核發", "competitive": "擇優", "lottery": "抽籤", "first_come": "先到先得", "unknown": "未載明"}
CHANNEL_LABELS = {"school": "向學校申請", "agency": "向機關申請", "online": "線上申請", "mail": "郵寄", "unknown": "未載明"}
NEED_TYPE_LABELS = {"cash_now": "急需一筆錢", "reduce_burden": "長期減輕負擔", "honor": "榮譽／履歷", "service": "需要照顧服務", "unknown": "不確定"}
DISLIKE_LABELS = {"interview": "要面試", "essay": "要寫自傳／計畫", "recommendation": "要推薦函", "obligations": "得獎後有義務", "financial_proof": "要交財力證明", "office_proof": "要公所／村里長證明", "loan": "貸款", "competitive": "擇優競爭"}


def iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return str(value)


def benefit_summary(row: dict) -> dict:
    registry = get_registry()
    source = row.get("source") or {}
    meta = row.get("benefit") or {}
    review = row.get("review") or {}
    llm = row.get("llm") or {}
    index = row.get("index") or {}
    rules = row.get("rules") or []
    return {
        "id": row["_id"],
        "canonical_id": row.get("canonical_id", row["_id"]),
        "is_canonical": bool(row.get("is_canonical", True)),
        "title": row.get("title", ""),
        "domain": row.get("domain", ""),
        "domain_label": registry.domain_label(row.get("domain", "")) if row.get("domain") else "",
        "category": row.get("category", ""),
        "category_label": row.get("category_label") or registry.category_label(row.get("category", "")),
        "provider": row.get("provider", ""),
        "provider_type": row.get("provider_type", "unknown"),
        "provider_type_label": PROVIDER_TYPE_LABELS.get(row.get("provider_type", "unknown"), row.get("provider_type", "")),
        "provider_region": row.get("provider_region", ""),
        "benefit_form": meta.get("benefit_form", ""),
        "benefit_form_label": BENEFIT_FORM_LABELS.get(meta.get("benefit_form", ""), meta.get("benefit_form", "")),
        "amount": meta.get("amount") or {},
        "amount_annualized": meta.get("amount_annualized"),
        "application_period": meta.get("application_period") or {},
        "award_basis": meta.get("award_basis", "unknown"),
        "award_basis_label": AWARD_BASIS_LABELS.get(meta.get("award_basis", "unknown"), ""),
        "quota": meta.get("quota"),
        "application_channel": (meta.get("application") or {}).get("channel", "unknown"),
        "application_effort": (meta.get("application") or {}).get("effort", ""),
        "exclusive_with": meta.get("exclusive_with") or [],
        "residence_cities": index.get("residence_cities") or [],
        "education_levels": index.get("education_levels") or [],
        "tags_required": index.get("tags_required") or [],
        "status": row.get("status", "active"),
        "is_overview": bool(row.get("is_overview")),
        "record_kind": row.get("record_kind") or "program",
        "quality_tier": (row.get("admission") or {}).get("quality_tier", ""),
        "categories_secondary": row.get("categories_secondary") or [],
        "categories_secondary_labels": [registry.category_label(c) for c in (row.get("categories_secondary") or [])],
        "category_confidence": row.get("category_confidence", ""),
        "uncertain": bool((row.get("classification") or {}).get("uncertain")),
        "category_uncertain": bool((row.get("classification") or {}).get("category_uncertain")),
        "classification_basis": (row.get("classification") or {}).get("decision_basis", ""),
        "missing_fields": (((row.get("admission") or {}).get("completeness") or {}).get("missing_labels")) or [],
        "needs_review": bool(review.get("needs_review")),
        "review_reasons": review.get("reasons") or [],
        "source_id": row.get("source_id", ""),
        "source_name": source.get("source_name", ""),
        "source_url": source.get("source_url", ""),
        "official_domain": source.get("official_domain", ""),
        "source_type": source.get("source_type", ""),
        "source_verified": bool(source.get("source_verified")),
        "is_repost": bool(source.get("is_repost")),
        "content_type": source.get("content_type", "html"),
        "data_confidence": source.get("data_confidence"),
        "confidence": row.get("confidence"),
        "llm_processed": bool(llm.get("processed")),
        "llm_model": llm.get("model", ""),
        "llm_accepted": len(llm.get("accepted") or []),
        "rules_count": len(rules),
        "simple_rules": index.get("simple_rules", sum(1 for r in rules if r.get("complexity") == "simple")),
        "complex_rules": index.get("complex_rules", sum(1 for r in rules if r.get("complexity") == "complex")),
        "keywords": row.get("keywords") or [],
        "extraction_version": row.get("extraction_version", ""),
        "registry_version": row.get("registry_version"),
        "first_seen_at": iso(row.get("first_seen_at")),
        "updated_at": iso(row.get("updated_at")),
    }


def benefit_detail(row: dict) -> dict:
    """完整 schema（給前端「標準 Schema」分頁）：去掉 _id 以外的內部欄位。"""
    data = {k: v for k, v in row.items() if k not in {"_id"}}
    data["id"] = row["_id"]
    for key in ("first_seen_at", "last_seen_at", "updated_at"):
        if key in data:
            data[key] = iso(data[key])
    if isinstance((data.get("llm") or {}).get("processed_at"), datetime):
        data["llm"]["processed_at"] = iso(data["llm"]["processed_at"])
    source = data.get("source") or {}
    crawl_time = source.get("crawl_time")
    if isinstance(crawl_time, str) and crawl_time and "+" not in crawl_time and not crawl_time.endswith("Z"):
        try:
            source["crawl_time"] = iso(datetime.fromisoformat(crawl_time))
        except ValueError:
            pass
    return data


def rule_to_dict(rule: dict) -> dict:
    registry = get_registry()
    attribute = registry.get(rule.get("attribute_id", ""))
    value = rule.get("value")
    value_label = None
    if attribute is not None:
        if attribute.type in {"enum", "multi_enum"}:
            value_label = "、".join(attribute.value_label(v) for v in value) if isinstance(value, list) else attribute.value_label(value)
        if attribute.id == "identity.tags":
            tags = value if isinstance(value, list) else [value]
            value_label = "、".join(registry.tags[t].label if t in registry.tags else str(t) for t in tags if t is not None)
    return {**rule, "attribute_label": attribute.label if attribute else rule.get("attribute_id", ""), "attribute_type": attribute.type if attribute else "", "value_label": value_label}


def raw_document_to_dict(doc: dict, *, include_html: bool = False) -> dict:
    data = {
        "id": doc["_id"], "source_id": doc.get("source_id", ""), "source_name": doc.get("source_name", ""), "source_url": doc.get("source_url", ""), "title": doc.get("title", ""),
        "content_type": doc.get("content_type", "html"), "raw_text": doc.get("raw_text", ""), "structured": doc.get("structured") or {}, "meta": doc.get("meta") or {}, "attachments": doc.get("attachments") or [],
        "file_path": doc.get("file_path", ""), "content_hash": doc.get("content_hash", ""), "crawl_time": iso(doc.get("crawl_time")), "first_seen_at": iso(doc.get("first_seen_at")), "last_seen_at": iso(doc.get("last_seen_at")),
        "last_crawled_at": iso(doc.get("last_crawled_at")), "published_date": doc.get("published_date", ""), "classification": doc.get("classification"), "processing_status": doc.get("processing_status", ""),
        "processing_error": doc.get("processing_error", ""), "processed_at": iso(doc.get("processed_at")), "skip_reason": doc.get("skip_reason", ""), "benefit_id": doc.get("benefit_id"), "rows_count": len(doc.get("rows") or []) if "rows" in doc else None,
    }
    if include_html:
        data["raw_html"] = doc.get("raw_html", "")
    return data


def source_to_dict(row: dict) -> dict:
    return {
        "id": row["_id"], "name": row.get("name", ""), "organization": row.get("organization", ""), "provider_type": row.get("provider_type", "unknown"), "provider_type_label": PROVIDER_TYPE_LABELS.get(row.get("provider_type", "unknown"), row.get("provider_type", "")),
        "source_type": row.get("source_type", ""), "base_url": row.get("base_url", ""), "official_domain": row.get("official_domain", ""), "crawler_class": row.get("crawler_class", ""), "enabled": bool(row.get("enabled", True)),
        "request_delay_seconds": row.get("request_delay_seconds", 1.0), "source_verified": bool(row.get("source_verified")), "source_verification_method": row.get("source_verification_method", ""), "source_status": row.get("source_status", ""),
        "verification_details": row.get("verification_details"), "data_confidence": row.get("data_confidence"), "notes": row.get("notes", ""), "domains": row.get("domains") or [], "pages_total": row.get("pages_total", 0), "pages_skipped": row.get("pages_skipped", 0),
        "follow_links": bool(row.get("follow_links")), "last_run_at": iso(row.get("last_run_at")), "last_status": row.get("last_status", "never"), "last_record_count": row.get("last_record_count", 0), "last_error": row.get("last_error", ""),
    }


def job_to_dict(job: dict) -> dict:
    return {"id": job["_id"], "source_id": job.get("source_id", ""), "started_at": iso(job.get("started_at")), "finished_at": iso(job.get("finished_at")), "status": job.get("status", ""), "triggered_by": job.get("triggered_by", ""), "discovered": job.get("discovered", 0), "fetched": job.get("fetched", 0), "new_documents": job.get("new_documents", 0), "updated_documents": job.get("updated_documents", 0), "unchanged_documents": job.get("unchanged_documents", 0), "failed_items": job.get("failed_items", 0), "error": job.get("error", "")}


def provider_to_dict(row: dict) -> dict:
    return {"id": row["_id"], "name": row.get("name", ""), "service_kind": row.get("service_kind", ""), "city": row.get("city", ""), "address": row.get("address", ""), "phone": row.get("phone", ""), "record": row.get("record") or {}, "source_url": row.get("source_url", ""), "source_name": row.get("source_name", ""), "crawl_time": iso(row.get("crawl_time"))}
