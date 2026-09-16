"""Processing pipeline v2（MongoDB）：

    raw_documents(new / changed)
        → 來源未驗證 → needs_review（不進正式資料）
        → 資料集（providers）→ providers 集合；statistics / skipped → 記錄原因
        → 分類器（語料統計關鍵字）→ 不是補助 → filtered_out；不確定 → 本地 AI 二次判斷
        → Extractor（core + benefit meta + 條件句 → 登錄表規則）
        → 本地 AI 補齊（給付特徵空缺、對不到屬性的條件句）→ 驗證器（摘錄必在原文、屬性必在登錄表）
        → 資格骨幹（規則式訊號 + 本地 AI 投票，媒合分層用；見 core_builder.py）
        → 去重（canonical_id）→ benefits 集合 → 過期標記
"""

from __future__ import annotations

import hashlib
import logging
import re
import uuid

from ..config import get_settings
from ..db import get_db, utcnow
from ..llm import core_extract
from ..llm import fill as llm_fill
from ..registry import get_registry
from . import admission
from .classifier import get_classifier
from .classifier_ensemble import classify_ensemble
from .core_builder import build_core
from .dedup import canonical_rank, is_duplicate
from .extractor import Extractor, closed_marker, is_real_condition, placeholder_attribute
from .normalization import find_cities, taiwan_today
from .schema_validator import validate_benefit

log = logging.getLogger(__name__)

PROVIDER_NAME_COLS = re.compile(r"名稱|機構|單位|護理所|中心")
PROVIDER_ADDR_COLS = re.compile(r"地址|住址|所在地")
PROVIDER_PHONE_COLS = re.compile(r"電話|聯絡")
PROVIDER_CITY_COLS = re.compile(r"縣市|所在縣市|行政區|區域")
TAB_FRAGMENT_TITLES = {"申請說明", "應備文件", "洽辦資訊", "相關檔案", "申請方式", "服務內容", "常見問答", "注意事項", "相關連結", "聯絡資訊", "簡介", "說明", "補助標準", "申請流程", "下載專區", "表單下載"}


def eligibility_core_for(benefit: dict, previous: dict | None, *, use_llm: bool) -> dict:
    """重建資格骨幹：原文沒變就沿用上次的 AI 投票（不重跑模型）；有 AI 時補上 AI 這一票。"""
    previous = previous or {}
    old = previous.get("eligibility_core") or {}
    llm_output = old.get("llm") if old.get("llm") and previous.get("content_hash") == benefit.get("content_hash") else None
    if llm_output is None and use_llm:
        try:
            llm_output = core_extract.extract_raw(benefit)
        except Exception as exc:  # AI 失敗仍用規則式訊號建立骨幹
            log.warning("eligibility core llm failed for %s: %s", benefit.get("title", "")[:40], exc)
    return build_core(benefit, llm_output=llm_output)


def _drop_benefit(db, doc_id: str) -> None:
    """文件重新處理後不再是補助（被過濾／略過／拒絕）→ 移除舊的 benefit，避免資料中心殘留。"""
    db.benefits.delete_many({"raw_document_id": doc_id})


def _refresh_admission(db, benefit_id: str) -> None:
    """保留（kept）的 benefit 也要有最新的 record_kind／admission（收錄政策更新後不用重抽）。"""
    row = db.benefits.find_one({"_id": benefit_id})
    if row is None:
        return
    update = admission.admit(row)
    if update["record_kind"] == "portal":
        update["is_overview"] = True
    if row.get("record_kind") != update["record_kind"] or (row.get("admission") or {}).get("quality_tier") != update["admission"]["quality_tier"] or (row.get("admission") or {}).get("completeness") != update["admission"]["completeness"]:
        db.benefits.update_one({"_id": benefit_id}, {"$set": update})


def _looks_statistical(doc: dict) -> bool:
    rows = (doc.get("rows") or [])[:50]
    if not rows:
        return False
    cells = [str(v) for row in rows for v in row.values() if v not in (None, "")]
    if not cells:
        return False
    avg_len = sum(len(c) for c in cells) / len(cells)
    numeric = sum(1 for c in cells if re.fullmatch(r"[0-9,.%\-]+", c)) / len(cells)
    return avg_len < 12 and numeric > 0.4


def process_pending(source_ids: list[str] | None = None, *, force: bool = False, use_llm: bool | None = None, limit: int | None = None, reset_llm: bool = False, fill: bool = True) -> dict:
    """fill=False：本地 AI 只用在三方投票，抽取後的欄位補齊留給 --llm-fill（只補 canonical，較省）。"""
    db = get_db()
    settings = get_settings()
    stats = {"processed": 0, "filtered_out": 0, "extracted": 0, "needs_review": 0, "errors": 0, "llm_used": 0, "source_unverified": 0, "providers": 0, "skipped": 0, "kept": 0, "expired": 0}
    query: dict = {} if force else {"processing_status": {"$in": ["new", "error"]}}
    if force:
        query["processing_status"] = {"$ne": "skipped"}
    if source_ids:
        query["source_id"] = {"$in": source_ids}
    cursor = db.raw_documents.find(query, {"_id": 1}).sort("crawl_time", 1)
    if limit:
        cursor = cursor.limit(limit)
    doc_ids = [d["_id"] for d in cursor]
    if use_llm is None:
        use_llm = settings.llm_provider != "none"
    if use_llm and not llm_fill.llm_available():
        log.info("本地 AI 不可用，本輪只用規則式抽取（之後可用 --llm-fill 補齊）")
        use_llm = False
    llm_budget = settings.llm_max_documents_per_run
    for doc_id in doc_ids:
        try:
            outcome = process_document(doc_id, use_llm=use_llm and llm_budget > 0, keep_llm=not reset_llm, fill=fill)
        except Exception as exc:
            log.exception("document %s failed", doc_id)
            outcome = "errors"
            db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "error", "processing_error": f"{type(exc).__name__}: {exc}"[:2000], "processed_at": utcnow()}})
        stats["processed"] += 1
        if outcome.endswith("+llm"):
            llm_budget -= 1
            stats["llm_used"] += 1
            outcome = outcome[: -len("+llm")]
        stats[outcome] = stats.get(outcome, 0) + 1
    stats["expired"] = expire_pass()
    stats["dedup_changed"] = dedup_pass()
    return stats


def _needs_llm_classification(result, settings) -> bool:
    if result.is_benefit and result.confidence >= settings.classifier_uncertain_high:
        return False
    if not result.is_benefit and result.signal_score < settings.classifier_uncertain_low * result.threshold:
        return False
    return True


def keep_prior_classification(ens, prior: dict | None) -> bool:
    """本地 AI 這次不在線（忙碌／逾時）時，是否沿用先前 AI 已確認「是補助」的判斷。

    不沿用的話，這一輪會把紀錄標成「疑似補助・待確認」，而 load_records 會把 uncertain 整筆排除在媒合之外——
    等於一次模型逾時就讓真的補助從媒合裡消失（2026-09-16 的整站重爬就發生過，62 筆）。
    """
    if not (ens.uncertain and not ens.llm_used and ens.is_benefit) or not prior:
        return False
    return bool((((prior.get("classification") or {}).get("llm")) or {}).get("is_benefit"))


def process_document(doc_id: str, *, use_llm: bool = False, keep_llm: bool = True, fill: bool = True) -> str:
    db = get_db()
    settings = get_settings()
    doc = db.raw_documents.find_one({"_id": doc_id})
    if doc is None:
        return "errors"
    source = db.sources.find_one({"_id": doc["source_id"]}) or {}
    source["id"] = doc["source_id"]
    now = utcnow()
    if doc.get("processing_status") == "skipped" or doc.get("content_type") == "skipped":
        _drop_benefit(db, doc_id)
        return "skipped"
    if not source.get("source_verified"):
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "needs_review", "processing_error": "來源未通過官方驗證，資料不進正式資料表", "processed_at": now}})
        _drop_benefit(db, doc_id)
        return "source_unverified"
    meta = doc.get("meta") or {}
    data_kind = meta.get("data_kind", "text")
    if doc.get("content_type") in {"csv", "json", "xml"} and data_kind in {"providers", "statistics"}:
        if data_kind == "providers":
            count = ingest_providers(doc, source)
            db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "provider_data", "processing_error": "", "processed_at": now, "classification": {"is_benefit": False, "category": "", "reason": f"服務提供者名單（{count} 筆）", "method": "config"}}})
            _drop_benefit(db, doc_id)
            return "providers"
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "skipped", "skip_reason": "統計資料集，不是補助條文", "processed_at": now, "classification": {"is_benefit": False, "category": "", "reason": "統計資料集", "method": "config"}}})
        _drop_benefit(db, doc_id)
        return "skipped"
    if (doc.get("title") or "").strip() in TAB_FRAGMENT_TITLES:
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "filtered_out", "processing_error": "", "processed_at": now, "classification": {"is_benefit": False, "category": "", "reason": "頁面分頁片段（申請說明／應備文件等），主頁面已另行收錄", "method": "rule"}}})
        _drop_benefit(db, doc_id)
        return "filtered_out"
    if doc.get("content_type") in {"csv", "json", "xml"} and data_kind in {"text", "auto"} and _looks_statistical(doc):
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "skipped", "skip_reason": "統計表（數值欄位為主），不是補助條文", "processed_at": now, "classification": {"is_benefit": False, "category": "", "reason": "統計表", "method": "rule"}}})
        _drop_benefit(db, doc_id)
        return "skipped"
    if data_kind == "providers_text":
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "skipped", "skip_reason": "服務單位一覽表（附件），不是補助條文", "processed_at": now, "classification": {"is_benefit": False, "category": "", "reason": "服務單位一覽表", "method": "config"}}})
        _drop_benefit(db, doc_id)
        return "skipped"
    if len(doc.get("raw_text") or "") < 60:
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "filtered_out", "processing_error": "原文太短", "processed_at": now, "classification": {"is_benefit": False, "category": "", "reason": "原文太短", "method": "rule"}}})
        _drop_benefit(db, doc_id)
        return "filtered_out"
    # 收錄政策：申請書／附件／流程圖／進度查詢／標章／統計／問答／名單／行政公告不是補助方案內容 → 不收（附原因）
    page_kind, kind_reason = admission.page_kind(doc.get("title", ""), doc.get("raw_text", ""), doc.get("source_url", ""))
    if page_kind in admission.EXCLUDED_KINDS:
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "filtered_out", "processing_error": "", "processed_at": now, "benefit_id": None, "classification": {"is_benefit": False, "category": "", "reason": kind_reason, "method": "admission", "page_kind": page_kind}}})
        _drop_benefit(db, doc_id)
        return "filtered_out"
    # ---- 分類：三方投票（關鍵字加減分 × embedding × 本地 LLM），見 services/classifier_ensemble.py
    seed_category = meta.get("seed_category") if int(meta.get("depth", 0) or 0) == 0 else ""
    ens = classify_ensemble(doc.get("title", ""), doc.get("raw_text", ""), url=doc.get("source_url", ""), content_hash=doc.get("content_hash") or doc_id, use_llm=use_llm, llm_classify=(llm_fill.classify_document if use_llm else None), seed_category=seed_category or "")
    llm_used = ens.llm_used
    result = ens.keyword or get_classifier().classify(doc.get("title", ""), doc.get("raw_text", ""))
    result.is_benefit, result.category, result.domain = ens.is_benefit, ens.category, ens.domain
    result.method = "ensemble"
    if ens.uncertain and not ens.llm_used and ens.is_benefit:
        prior = db.benefits.find_one({"raw_document_id": doc_id}, {"classification.llm.is_benefit": 1})
        if keep_prior_classification(ens, prior):
            ens.uncertain = False
            ens.decision_basis += "；本次本地 AI 不在線，沿用先前 AI 已確認是補助的判斷"
    classification = {**result.to_dict(), **ens.to_dict()}
    if ens.page_kind in admission.EXCLUDED_KINDS:
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "filtered_out", "processing_error": "", "processed_at": now, "benefit_id": None, "classification": {**classification, "is_benefit": False, "category": "", "page_kind": ens.page_kind, "reason": ens.decision_basis}}})
        _drop_benefit(db, doc_id)
        return "filtered_out" + ("+llm" if llm_used else "")
    # 內容沒變且已經過本地 AI 補齊的 benefit：重跑 pipeline 時保留（除非 reset_llm）；分類一定用目前的三方投票重算
    if keep_llm:
        existing = db.benefits.find_one({"raw_document_id": doc_id}, {"content_hash": 1, "llm.processed": 1, "title": 1, "category": 1, "domain": 1, "category_label": 1, "status": 1, "classification.llm.is_benefit": 1})
        if existing and existing.get("content_hash") == doc.get("content_hash") and (existing.get("llm") or {}).get("processed") and ens.is_benefit:
            prior_llm_ok = bool((((existing.get("classification") or {}).get("llm")) or {}).get("is_benefit"))
            if not ens.uncertain or prior_llm_ok:
                update = {"classification": classification, "categories_secondary": ens.categories_secondary, "category_confidence": ens.category_confidence, "updated_at": now}
                if doc.get("title") and doc.get("title") != existing.get("title"):
                    update["title"] = doc["title"]  # 原始文件標題被爬蟲更新（例如連結文字 → 頁面標題）：同步到 benefit
                if ens.category and ens.category != existing.get("category") and ens.category_confidence in {"high", "medium"}:
                    update.update({"category": ens.category, "domain": ens.domain, "category_label": get_registry().category_label(ens.category)})
                closed = closed_marker(doc.get("title", ""), doc.get("raw_text", ""))
                if closed and existing.get("status") != "expired":
                    # 已停辦規則更新後，沿用的舊 benefit 也要標 expired（預設不列出、不進媒合）
                    update["status"] = "expired"
                    db.benefits.update_one({"_id": existing["_id"]}, {"$set": {"review.needs_review": True}, "$addToSet": {"review.reasons": f"標題／原文標示「{closed}」：已停止受理，狀態設為已截止（預設不列出、不進媒合）"}})
                db.benefits.update_one({"_id": existing["_id"]}, {"$set": update})
                db.raw_documents.update_one({"_id": doc_id}, {"$set": {"classification": classification, "processed_at": now}})
                _refresh_admission(db, existing["_id"])
                return "kept" + ("+llm" if llm_used else "")
            log.info("kept benefit is now uncertain, re-evaluating: %s", doc.get("title", "")[:60])
    if not ens.is_benefit:
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "filtered_out", "processing_error": "", "processed_at": now, "classification": {**classification, "reason": ens.decision_basis, "page_kind": ens.page_kind}, "benefit_id": None}})
        _drop_benefit(db, doc_id)  # 規則更新後不再是補助 → 移除舊 benefit
        return "filtered_out" + ("+llm" if llm_used else "")

    extractor = Extractor()
    output = extractor.extract(doc, source, result)
    benefit = output.benefit
    benefit["classification"] = classification
    benefit["categories_secondary"] = ens.categories_secondary
    benefit["category_confidence"] = ens.category_confidence
    if ens.uncertain or ens.category_uncertain:
        review = benefit.setdefault("review", {"needs_review": False, "reasons": []})
        review["needs_review"] = True
        note = "閘門三方不一致（" + ens.decision_basis + "）：保留為疑似補助，未確認前不進媒合" if ens.uncertain else "類別三方不一致（" + ens.decision_basis + "）：主類別待確認，候選存為次類別"
        review["reasons"] = list(review.get("reasons") or []) + [note]
    if use_llm and fill:
        llm_report = {"processed": True, "model": "", "provider": "ollama", "processed_at": utcnow(), "tasks": {}, "accepted": [], "rejected": [], "errors": []}
        try:
            report = llm_fill.fill_benefit_meta(benefit)
            llm_report["model"] = report.get("model", "")
            llm_report["tasks"]["benefit_meta"] = {"accepted": len(report["accepted"]), "rejected": len(report["rejected"])}
            llm_report["accepted"].extend(report["accepted"])
            llm_report["rejected"].extend(report["rejected"])
            llm_used = True
        except Exception as exc:
            log.warning("llm benefit_meta failed for %s: %s", doc_id, exc)
            llm_report["errors"].append(f"benefit_meta: {type(exc).__name__}: {str(exc)[:200]}")
        try:
            report = llm_fill.map_conditions_batch(benefit, output.unmapped_conditions)
            llm_report["model"] = llm_report["model"] or report.get("model", "")
            llm_report["tasks"]["condition_mapping"] = {"accepted": len(report["accepted"]), "rejected": len(report["rejected"]), "proposed_attributes": len(report["proposed_attributes"])}
            llm_report["accepted"].extend(report["accepted"])
            llm_report["rejected"].extend(report["rejected"])
            for proposal in report["proposed_attributes"]:
                _enqueue_review("attribute_proposal", benefit_id=None, raw_document_id=doc_id, payload=proposal)
            llm_used = True
        except Exception as exc:
            log.warning("llm condition_mapping failed for %s: %s", doc_id, exc)
            llm_report["errors"].append(f"condition_mapping: {type(exc).__name__}: {str(exc)[:200]}")
        benefit["llm"] = llm_report
    else:
        for condition in output.unmapped_conditions:
            condition["status"] = "unmapped"
    _finalize_conditions(benefit)
    outcome = validate_benefit(benefit, benefit.get("original_text"))
    if not outcome.ok or outcome.benefit is None:
        db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": "needs_review", "processing_error": "；".join(outcome.errors)[:2000], "processed_at": now, "classification": classification}})
        _drop_benefit(db, doc_id)
        return "needs_review"
    benefit = outcome.benefit
    _refresh_status(benefit)  # 本地 AI 可能補上／改寫申請期間，狀態要依最後的截止日重算
    benefit["index"] = Extractor.build_index(benefit)
    previous = db.benefits.find_one({"raw_document_id": doc_id}, {"eligibility_core": 1, "content_hash": 1})
    benefit["eligibility_core"] = eligibility_core_for(benefit, previous, use_llm=use_llm and fill)
    row = _upsert_benefit(db, doc, source, benefit)
    status = "needs_review" if row["review"]["needs_review"] else "extracted"
    db.raw_documents.update_one({"_id": doc_id}, {"$set": {"processing_status": status, "processing_error": "", "processed_at": now, "classification": classification, "benefit_id": row["_id"]}})
    return ("needs_review" if status == "needs_review" else "extracted") + ("+llm" if llm_used else "")


def _refresh_status(benefit: dict) -> None:
    """截止日已過或原文寫明停辦 → status=expired（補齊流程補上期間後要重算）。"""
    from .normalization import taiwan_today

    period = (benefit.get("benefit") or {}).get("application_period") or {}
    end = period.get("end_date") or ""
    closed = closed_marker(benefit.get("title", ""), benefit.get("original_text", ""))
    today = taiwan_today().isoformat()
    if (end and end < today) or closed:
        if benefit.get("status") != "expired":
            benefit["status"] = "expired"
            review = benefit.setdefault("review", {"needs_review": False, "reasons": []})
            review["needs_review"] = True
            reason = f"申請期間已於 {end} 截止" if end and end < today else f"原文標示「{closed}」"
            note = reason + "：狀態改為已截止（預設不列出、不進媒合）"
            if note not in (review.get("reasons") or []):
                review["reasons"] = list(review.get("reasons") or []) + [note]


def _finalize_conditions(benefit: dict) -> None:
    """規則式與 AI 都對不到的條件句 → complex 規則（永不拒絕、顯示為需進一步確認）。"""
    registry = get_registry()
    rules = benefit.setdefault("rules", [])
    covered = {r.get("evidence", {}).get("condition_text") for r in rules} | {r.get("evidence", {}).get("excerpt") for r in rules}
    for condition in benefit.get("conditions") or []:
        if condition.get("status") not in {"unmapped", "unresolved"}:
            continue
        text = condition.get("text") or ""
        excerpt = condition.get("excerpt") or text
        if text in covered or excerpt in covered:
            continue
        if not is_real_condition(excerpt):
            # 段落標題、「不拘」欄位：不是條件，不產生規則（仍留在 conditions 裡供追溯）
            condition["status"] = "not_a_condition"
            continue
        candidates = [c for c in (condition.get("candidates") or []) if registry.get(c) and registry.get(c).type != "text"]
        rules.append({
            "id": uuid.uuid4().hex, "attribute_id": placeholder_attribute(registry, candidates, excerpt), "operator": "exists", "value": None, "unit": "", "group_id": f"complex_{len(rules)}", "group_logic": "any",
            "complexity": "complex", "role": condition.get("role", "required") if condition.get("role") in {"required", "exclusion", "bonus"} else "required",
            "human_readable": ("限制：" if condition.get("role") == "exclusion" else "條件：") + condition.get("text", "")[:80], "evidence": {"excerpt": condition.get("excerpt", "")[:300], "extractor": "rule_based", "condition_text": condition.get("text", "")[:200]},
            "confidence": 0.5, "inferred": False, "inference_basis": "", "registry_version": registry.version,
        })
        condition["status"] = "complex"


def _enqueue_review(kind: str, *, benefit_id: str | None, raw_document_id: str | None, payload: dict) -> None:
    db = get_db()
    db.review_items.insert_one({"_id": str(uuid.uuid4()), "kind": kind, "benefit_id": benefit_id, "raw_document_id": raw_document_id, "payload": payload, "status": "open", "created_at": utcnow(), "resolved_at": None, "action": ""})


# ------------------------------------------------------------- benefits
def _upsert_benefit(db, doc: dict, source: dict, benefit: dict) -> dict:
    # 收錄政策：record_kind（program／portal）與完整度、品質等級
    benefit.update(admission.admit(benefit))
    if benefit["record_kind"] == "portal":
        benefit["is_overview"] = True
    existing = db.benefits.find_one({"raw_document_id": doc["_id"]}, {"_id": 1, "canonical_id": 1, "is_canonical": 1, "first_seen_at": 1})
    now = utcnow()
    if existing is None:
        benefit_id = str(uuid.uuid4())
        benefit.update({"_id": benefit_id, "first_seen_at": now, "canonical_id": benefit_id, "is_canonical": True})
        benefit["last_seen_at"] = now
        benefit["updated_at"] = now
        db.benefits.insert_one(benefit)
        _assign_canonical(db, benefit)
        return db.benefits.find_one({"_id": benefit_id})
    benefit.update({"_id": existing["_id"], "first_seen_at": existing.get("first_seen_at", now), "canonical_id": existing.get("canonical_id", existing["_id"]), "is_canonical": bool(existing.get("is_canonical", True)), "last_seen_at": now, "updated_at": now})
    db.benefits.replace_one({"_id": existing["_id"]}, benefit)
    return benefit


def _candidate(row: dict) -> dict:
    return {"title": row.get("title", ""), "provider": row.get("provider", ""), "region": row.get("provider_region") or "", "application_end": (row.get("benefit") or {}).get("application_period", {}).get("end_date", ""), "source_url": (row.get("source") or {}).get("source_url", "")}


def _rank_info(row: dict) -> dict:
    source = row.get("source") or {}
    return {"data_confidence": source.get("data_confidence", 0), "source_type": source.get("source_type", "government_site"), "is_repost": source.get("is_repost", False)}


def _assign_canonical(db, benefit: dict) -> None:
    candidate = _candidate(benefit)
    others = list(db.benefits.find({"_id": {"$ne": benefit["_id"]}}, {"title": 1, "provider": 1, "provider_region": 1, "benefit.application_period.end_date": 1, "source": 1, "canonical_id": 1, "first_seen_at": 1}))
    for other in others:
        duplicate, _sim, _reason = is_duplicate(candidate, _candidate(other))
        if not duplicate:
            continue
        canonical_id = other.get("canonical_id", other["_id"])
        group = [o for o in others if o.get("canonical_id") == canonical_id] + [benefit]
        ranked = sorted(group, key=lambda item: canonical_rank(_rank_info(item)), reverse=True)
        for item in group:
            db.benefits.update_one({"_id": item["_id"]}, {"$set": {"canonical_id": canonical_id, "is_canonical": item["_id"] == ranked[0]["_id"]}})
        return


def dedup_pass() -> int:
    db = get_db()
    rows = list(db.benefits.find({}, {"title": 1, "provider": 1, "provider_region": 1, "benefit.application_period.end_date": 1, "source": 1, "canonical_id": 1, "is_canonical": 1, "first_seen_at": 1}))
    rows.sort(key=lambda r: (canonical_rank(_rank_info(r)), (r.get("first_seen_at") or utcnow()).isoformat()), reverse=True)
    groups: list[list[dict]] = []
    for row in rows:
        for group in groups:
            if is_duplicate(_candidate(row), _candidate(group[0]))[0]:
                group.append(row)
                break
        else:
            groups.append([row])
    changed = 0
    for group in groups:
        canonical_id = group[0]["_id"]
        for index, row in enumerate(group):
            is_canonical = index == 0
            if row.get("canonical_id") != canonical_id or bool(row.get("is_canonical")) != is_canonical:
                db.benefits.update_one({"_id": row["_id"]}, {"$set": {"canonical_id": canonical_id, "is_canonical": is_canonical}})
                changed += 1
    return changed


def expire_pass() -> int:
    db = get_db()
    today = taiwan_today().isoformat()
    changed = 0
    for row in db.benefits.find({}, {"status": 1, "benefit.application_period.end_date": 1}):
        end = ((row.get("benefit") or {}).get("application_period") or {}).get("end_date", "")
        status = row.get("status", "active")
        new_status = status
        if end and end < today and status == "active":
            new_status = "expired"
        elif status == "expired" and (not end or end >= today):
            new_status = "active"
        if new_status != status:
            db.benefits.update_one({"_id": row["_id"]}, {"$set": {"status": new_status}})
            changed += 1
    return changed


# ------------------------------------------------------------- providers
def ingest_providers(doc: dict, source: dict) -> int:
    db = get_db()
    rows = doc.get("rows") or []
    columns = (doc.get("meta") or {}).get("columns") or []
    kind = (doc.get("meta") or {}).get("provider_kind") or doc.get("title", "")
    name_col = next((c for c in columns if PROVIDER_NAME_COLS.search(c)), None)
    addr_col = next((c for c in columns if PROVIDER_ADDR_COLS.search(c)), None)
    phone_col = next((c for c in columns if PROVIDER_PHONE_COLS.search(c)), None)
    city_col = next((c for c in columns if PROVIDER_CITY_COLS.search(c)), None)
    default_city = (find_cities(source.get("organization", "")) or find_cities(doc.get("title", "")) or [""])[0]
    count = 0
    now = utcnow()
    for row in rows:
        name = (row.get(name_col) if name_col else "") or next((v for v in row.values() if v), "")
        if not name:
            continue
        address = row.get(addr_col, "") if addr_col else ""
        city = (find_cities(row.get(city_col, "")) if city_col else []) or find_cities(address) or ([default_city] if default_city else [])
        key = hashlib.sha1(f"{name}|{address}".encode("utf-8")).hexdigest()[:20]
        db.providers.update_one(
            {"source_id": doc["source_id"], "record_key": key},
            {"$set": {"name": name[:200], "service_kind": kind, "city": city[0] if city else "", "address": address[:200], "phone": (row.get(phone_col, "") if phone_col else "")[:60], "record": row, "raw_document_id": doc["_id"], "source_url": doc["source_url"], "source_name": source.get("name", ""), "crawl_time": doc.get("crawl_time"), "updated_at": now}, "$setOnInsert": {"_id": str(uuid.uuid4()), "created_at": now}},
            upsert=True,
        )
        count += 1
    return count


# --------------------------------------------------------------- llm fill
def llm_fill_pending(limit: int | None = None, *, canonical_only: bool = True) -> dict:
    """對尚未經本地 AI 補齊的 benefits 執行 benefit_meta + condition_mapping（可中斷、可重跑）。

    canonical_only=True：只補齊 canonical 紀錄（媒合與列表只用 canonical）；同內容的重複紀錄（is_canonical=False）
    先略過並計入 skipped_non_canonical，之後可用 --include-non-canonical 補齊。
    """
    db = get_db()
    settings = get_settings()
    stats = {"processed": 0, "accepted": 0, "rejected": 0, "errors": 0, "skipped_no_llm": 0, "reclassified_out": 0, "skipped_non_canonical": 0}
    if not llm_fill.llm_available():
        stats["skipped_no_llm"] = 1
        stats["detail"] = "Ollama 不可用"
        return stats
    query: dict = {"llm.processed": {"$ne": True}}
    if canonical_only:
        stats["skipped_non_canonical"] = db.benefits.count_documents({"llm.processed": {"$ne": True}, "is_canonical": False})
        query["is_canonical"] = {"$ne": False}
    cursor = db.benefits.find(query).sort([("is_canonical", -1), ("updated_at", 1)])
    if limit:
        cursor = cursor.limit(limit)
    for benefit in cursor:
        report = {"processed": True, "model": "", "provider": "ollama", "processed_at": utcnow(), "tasks": {}, "accepted": [], "rejected": [], "errors": []}
        # 關鍵字分類不確定的文件：先讓本地 AI 確認是不是補助；不是 → filtered_out 並移除 benefit
        classification = benefit.get("classification") or {}
        # 關鍵字分類還沒經本地 AI 確認過的方案：一律請 AI 用完整類別清單確認類別（信心不足者同時確認是不是補助）
        if classification.get("method") == "keyword" and not (classification.get("llm") or {}):
            try:
                candidates = list((classification.get("category_scores") or {}).keys())[:6] or [benefit.get("category")]
                verdict = llm_fill.classify_document(benefit.get("title", ""), benefit.get("original_text", ""), [c for c in candidates if c])
            except Exception as exc:
                verdict = None
                report["errors"].append(f"classify: {type(exc).__name__}: {str(exc)[:120]}")
            if verdict is not None:
                classification = {**classification, "llm": verdict, "method": "keyword+llm"}
                if not verdict["is_benefit"] and benefit.get("record_kind") != "portal":  # 彙整頁依收錄政策保留，不因 AI 判定刪除
                    db.raw_documents.update_one({"_id": benefit.get("raw_document_id")}, {"$set": {"processing_status": "filtered_out", "processing_error": "", "processed_at": utcnow(), "classification": {**classification, "is_benefit": False, "category": ""}, "benefit_id": None}})
                    db.benefits.delete_one({"_id": benefit["_id"]})
                    stats["reclassified_out"] = stats.get("reclassified_out", 0) + 1
                    log.info("llm-fill: %s 由本地 AI 判定不是補助 → filtered_out", benefit.get("title", "")[:40])
                    continue
                if verdict["category"] and verdict["category"] != benefit.get("category"):
                    benefit["category"] = verdict["category"]
                    benefit["domain"] = get_registry().domain_of(verdict["category"])
                    benefit["category_label"] = get_registry().category_label(verdict["category"])
                    classification.update({"category": verdict["category"], "domain": benefit["domain"]})
                benefit["classification"] = classification
                db.raw_documents.update_one({"_id": benefit.get("raw_document_id")}, {"$set": {"classification": classification}})
        try:
            meta_report = llm_fill.fill_benefit_meta(benefit)
            report["model"] = meta_report.get("model", "")
            report["tasks"]["benefit_meta"] = {"accepted": len(meta_report["accepted"]), "rejected": len(meta_report["rejected"])}
            report["accepted"].extend(meta_report["accepted"])
            report["rejected"].extend(meta_report["rejected"])
        except Exception as exc:
            report["errors"].append(f"benefit_meta: {type(exc).__name__}: {str(exc)[:200]}")
            stats["errors"] += 1
        if not (benefit.get("rules") or []) and not (benefit.get("conditions") or []) and not benefit.get("is_overview"):
            # 規則式一句資格條件都沒抓到：請本地 AI 逐字列出資格句（逐段驗證），再交給屬性對應
            try:
                elig = llm_fill.extract_eligibility_sentences(benefit)
                report["model"] = report["model"] or elig.get("model", "")
                report["tasks"]["eligibility_sentences"] = {"accepted": len(elig["accepted"]), "rejected": len(elig["rejected"])}
                report["accepted"].extend(elig["accepted"])
                report["rejected"].extend(elig["rejected"])
                benefit["conditions"] = list(benefit.get("conditions") or []) + elig["sentences"]
            except Exception as exc:
                report["errors"].append(f"eligibility_sentences: {type(exc).__name__}: {str(exc)[:200]}")
                stats["errors"] += 1
        unmapped = [c for c in benefit.get("conditions") or [] if c.get("status") in {"unmapped", "unresolved", "complex"} and c.get("method") != "llm"]
        # complex 規則若由這些條件句產生，先移除，交給 AI 重新對屬性
        texts = {c.get("text") for c in unmapped}
        benefit["rules"] = [r for r in benefit.get("rules") or [] if not (r.get("complexity") == "complex" and (r.get("evidence") or {}).get("condition_text") in texts)]
        for c in unmapped:
            c["status"] = "unmapped"
        try:
            cond_report = llm_fill.map_conditions_batch(benefit, unmapped)
            report["model"] = report["model"] or cond_report.get("model", "")
            report["tasks"]["condition_mapping"] = {"accepted": len(cond_report["accepted"]), "rejected": len(cond_report["rejected"]), "proposed_attributes": len(cond_report["proposed_attributes"])}
            report["accepted"].extend(cond_report["accepted"])
            report["rejected"].extend(cond_report["rejected"])
            for proposal in cond_report["proposed_attributes"]:
                _enqueue_review("attribute_proposal", benefit_id=benefit["_id"], raw_document_id=benefit.get("raw_document_id"), payload=proposal)
        except Exception as exc:
            report["errors"].append(f"condition_mapping: {type(exc).__name__}: {str(exc)[:200]}")
            stats["errors"] += 1
        benefit["llm"] = report
        _finalize_conditions(benefit)
        outcome = validate_benefit(benefit, benefit.get("original_text"))
        if outcome.ok and outcome.benefit is not None:
            benefit = outcome.benefit
            benefit.update(admission.admit(benefit))  # 補齊後欄位變多 → 重算完整度與品質等級
            _refresh_status(benefit)  # AI 補上截止日／停辦字眼之後，狀態也要跟著重算
            if benefit.get("record_kind") == "portal":
                benefit["is_overview"] = True
            benefit["index"] = Extractor.build_index(benefit)
            benefit["eligibility_core"] = eligibility_core_for(benefit, benefit, use_llm=True)
            benefit["updated_at"] = utcnow()
            db.benefits.replace_one({"_id": benefit["_id"]}, benefit)
        stats["processed"] += 1
        stats["accepted"] += len(report["accepted"])
        stats["rejected"] += len(report["rejected"])
        log.info("llm-fill %s/%s: %s accepted=%d rejected=%d errors=%d", stats["processed"], "?", benefit.get("title", "")[:40], len(report["accepted"]), len(report["rejected"]), len(report["errors"]))
    return stats
