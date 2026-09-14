"""爬蟲／pipeline／來源／審核佇列／健康檢查。"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from ..config import get_settings
from ..db import get_db, ping, utcnow
from ..llm.factory import ollama_status
from ..schemas import PipelineRequest, ReviewActionRequest, RunRequest
from ..services import tasks
from .serializers import iso, job_to_dict, source_to_dict

router = APIRouter(prefix="/api", tags=["admin"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    db_ok = ping()
    llm = ollama_status(settings)
    return {"status": "ok" if db_ok else "degraded", "version": settings.app_version, "database": "ok" if db_ok else "error", "database_name": settings.mongodb_db, "llm_provider": settings.llm_provider, "llm_model": settings.llm_model, "llm_online": llm["online"], "llm_detail": llm["detail"], "redis": bool(settings.redis_url)}


def _source_counts(db) -> tuple[dict, dict, dict]:
    doc_counts = {r["_id"]: r["n"] for r in db.raw_documents.aggregate([{"$group": {"_id": "$source_id", "n": {"$sum": 1}}}])}
    benefit_counts = {r["_id"]: r["n"] for r in db.benefits.aggregate([{"$group": {"_id": "$source_id", "n": {"$sum": 1}}}])}
    job_stats: dict[str, dict] = {}
    for r in db.crawl_jobs.aggregate([{"$group": {"_id": {"s": "$source_id", "st": "$status"}, "n": {"$sum": 1}}}]):
        job_stats.setdefault(r["_id"]["s"], {})[r["_id"]["st"]] = r["n"]
    return doc_counts, benefit_counts, job_stats


@router.get("/sources")
def list_sources() -> list[dict]:
    db = get_db()
    doc_counts, benefit_counts, _ = _source_counts(db)
    result = []
    for row in db.sources.find({}).sort("_id", 1):
        data = source_to_dict(row)
        data["raw_documents"] = doc_counts.get(row["_id"], 0)
        data["benefits"] = benefit_counts.get(row["_id"], 0)
        result.append(data)
    return result


@router.get("/sources/{source_id}")
def get_source(source_id: str) -> dict:
    db = get_db()
    row = db.sources.find_one({"_id": source_id})
    if row is None:
        raise HTTPException(status_code=404, detail="source not found")
    data = source_to_dict(row)
    data["recent_jobs"] = [job_to_dict(j) for j in db.crawl_jobs.find({"source_id": source_id}).sort("started_at", -1).limit(10)]
    data["raw_documents"] = db.raw_documents.count_documents({"source_id": source_id})
    data["benefits"] = db.benefits.count_documents({"source_id": source_id})
    data["raw_by_status"] = {r["_id"]: r["n"] for r in db.raw_documents.aggregate([{"$match": {"source_id": source_id}}, {"$group": {"_id": "$processing_status", "n": {"$sum": 1}}}])}
    return data


@router.get("/crawler/status")
def crawler_status() -> dict:
    db = get_db()
    doc_counts, benefit_counts, job_stats = _source_counts(db)
    sources = []
    for row in db.sources.find({}).sort("_id", 1):
        data = source_to_dict(row)
        stats = job_stats.get(row["_id"], {})
        data.update({"raw_documents": doc_counts.get(row["_id"], 0), "benefits": benefit_counts.get(row["_id"], 0), "jobs_success": stats.get("success", 0) + stats.get("partial", 0), "jobs_failed": stats.get("failed", 0) + stats.get("skipped", 0), "jobs_total": sum(stats.values())})
        sources.append(data)
    running = tasks.running_kinds()
    last = db.crawl_jobs.find_one({"finished_at": {"$ne": None}}, {"finished_at": 1}, sort=[("finished_at", -1)])
    return {"sources": sources, "running": bool(running), "running_kinds": running, "tasks": tasks.list_tasks(10), "redis": tasks.get_redis() is not None, "last_crawl": iso(last.get("finished_at")) if last else None}


@router.post("/crawler/run")
def run_crawler(body: RunRequest) -> dict:
    record = tasks.enqueue("crawl", {"source_ids": body.source_ids, "run_pipeline": body.run_pipeline, "max_items": body.max_items, "triggered_by": "api"})
    return {"task": record, "message": "已送出爬蟲工作，請以 GET /api/crawler/status 追蹤"}


@router.get("/crawler/jobs")
def list_jobs(limit: int = Query(20, ge=1, le=200), source_id: str | None = None) -> list[dict]:
    db = get_db()
    query = {"source_id": source_id} if source_id else {}
    return [job_to_dict(j) for j in db.crawl_jobs.find(query).sort("started_at", -1).limit(limit)]


@router.get("/crawler/logs")
def list_logs(job_id: str | None = None, source_id: str | None = None, limit: int = Query(200, ge=1, le=1000)) -> list[dict]:
    db = get_db()
    query: dict = {}
    if job_id:
        query["job_id"] = job_id
    if source_id:
        query["source_id"] = source_id
    return [{"id": str(r["_id"]), "job_id": r.get("job_id"), "source_id": r.get("source_id"), "level": r.get("level"), "message": r.get("message"), "url": r.get("url"), "created_at": iso(r.get("created_at"))} for r in db.crawl_logs.find(query).sort("_id", -1).limit(limit)]


@router.get("/crawler/tasks")
def list_background_tasks() -> list[dict]:
    return tasks.list_tasks(20)


@router.post("/pipeline/run")
def run_pipeline(body: PipelineRequest) -> dict:
    record = tasks.enqueue("pipeline", {"source_ids": body.source_ids, "force": body.force, "use_llm": body.use_llm, "limit": body.limit})
    return {"task": record, "message": "已送出解析工作，請以 GET /api/pipeline/status 追蹤"}


@router.post("/pipeline/llm-fill")
def run_llm_fill(limit: int | None = Query(None, ge=1, le=5000)) -> dict:
    record = tasks.enqueue("llm_fill", {"limit": limit})
    return {"task": record, "message": "已送出本地 AI 補齊工作"}


@router.post("/pipeline/mine-keywords")
def run_mine_keywords() -> dict:
    record = tasks.enqueue("mine_keywords", {})
    return {"task": record, "message": "已送出關鍵字統計工作"}


@router.get("/pipeline/status")
def pipeline_status() -> dict:
    db = get_db()
    settings = get_settings()
    counts = {r["_id"]: r["n"] for r in db.raw_documents.aggregate([{"$group": {"_id": "$processing_status", "n": {"$sum": 1}}}])}
    return {
        "raw_documents_by_status": counts,
        "pending": counts.get("new", 0) + counts.get("error", 0),
        "benefits_total": db.benefits.count_documents({}),
        "llm_pending": db.benefits.count_documents({"llm.processed": {"$ne": True}}),
        "llm": {"provider": settings.llm_provider, **ollama_status(settings), "max_documents_per_run": settings.llm_max_documents_per_run},
        "running": bool(tasks.running_kinds()),
        "running_kinds": tasks.running_kinds(),
        "tasks": tasks.list_tasks(10),
    }


@router.get("/review")
def list_review(status: str = Query("open"), limit: int = Query(100, ge=1, le=500)) -> dict:
    db = get_db()
    query = {"status": status} if status != "all" else {}
    items = []
    for row in db.review_items.find(query).sort("created_at", -1).limit(limit):
        items.append({"id": row["_id"], "kind": row.get("kind"), "benefit_id": row.get("benefit_id"), "raw_document_id": row.get("raw_document_id"), "payload": row.get("payload"), "status": row.get("status"), "action": row.get("action", ""), "created_at": iso(row.get("created_at")), "resolved_at": iso(row.get("resolved_at"))})
    return {"items": items, "total": db.review_items.count_documents(query)}


@router.post("/review/{item_id}")
def resolve_review(item_id: str, body: ReviewActionRequest) -> dict:
    db = get_db()
    row = db.review_items.find_one({"_id": item_id})
    if row is None:
        raise HTTPException(status_code=404, detail="review item not found")
    db.review_items.update_one({"_id": item_id}, {"$set": {"status": "resolved", "action": body.action, "note": body.note, "resolution_payload": body.payload, "resolved_at": utcnow()}})
    return {"ok": True}
