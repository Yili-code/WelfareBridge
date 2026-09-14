"""背景工作：crawler / pipeline 由 API 觸發時在背景執行。

有設定 REDIS_URL 時把工作推進 Redis queue（由 `python -m benefit_crawler --loop` worker 消化），worker 會把狀態寫回 Redis，
API 的 /api/crawler/status 就能看到 queued → running → finished；沒有 Redis 時直接在 API 程序內開執行緒執行。
"""

from __future__ import annotations

import json
import logging
import threading
import traceback
from datetime import datetime, timezone

from ..config import get_settings

log = logging.getLogger(__name__)

QUEUE_KEY = "scholarship_ai:jobs"
TASK_IDS_KEY = "scholarship_ai:task_ids"
TASK_KEY = "scholarship_ai:task:{task_id}"
TASK_TTL_SECONDS = 7 * 24 * 3600
_lock = threading.Lock()
_tasks: dict[str, dict] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# worker 的 BLPOP 最多等這麼久；redis-py 8 預設 socket 逾時只有 5 秒，阻塞式命令等更久會被切斷（Timeout reading from socket）
QUEUE_BLOCK_SECONDS = 30
_redis_client = None


def get_redis():
    global _redis_client
    settings = get_settings()
    if not settings.redis_url:
        return None
    if _redis_client is not None:
        try:
            _redis_client.ping()
            return _redis_client
        except Exception:
            _redis_client = None
    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=QUEUE_BLOCK_SECONDS + 5, decode_responses=True)
        client.ping()
        _redis_client = client
        return client
    except Exception as exc:  # Redis 不可用 → 退回執行緒
        log.warning("Redis 無法使用（%s），改用背景執行緒", exc)
        return None


def _redis_save(client, record: dict) -> None:
    try:
        client.set(TASK_KEY.format(task_id=record["task_id"]), json.dumps(record, ensure_ascii=False, default=str), ex=TASK_TTL_SECONDS)
    except Exception as exc:  # 狀態寫回失敗不影響工作本身
        log.warning("redis task status write failed: %s", exc)


def _redis_load(client, task_id: str) -> dict | None:
    try:
        raw = client.get(TASK_KEY.format(task_id=task_id))
    except Exception:
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def run_job(kind: str, params: dict) -> dict:
    """實際執行一個工作（API 執行緒與 worker 都呼叫這裡）。"""
    from . import crawl_service, pipeline

    result: dict = {}
    if kind == "crawl":
        result["crawl"] = crawl_service.run_sources(params.get("source_ids"), triggered_by=params.get("triggered_by", "api"), max_items=params.get("max_items"))
        if params.get("run_pipeline", True):
            result["pipeline"] = pipeline.process_pending(params.get("source_ids"))
    elif kind == "pipeline":
        result["pipeline"] = pipeline.process_pending(params.get("source_ids"), force=bool(params.get("force")), use_llm=params.get("use_llm"), limit=params.get("limit"))
    elif kind == "llm_fill":
        result["llm_fill"] = pipeline.llm_fill_pending(limit=params.get("limit"))
    elif kind == "mine_keywords":
        from .keyword_mining import mine_and_write

        result["mine_keywords"] = mine_and_write()
    else:
        raise ValueError(f"unknown job kind: {kind}")
    return result


def enqueue(kind: str, params: dict) -> dict:
    task_id = f"{kind}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    record = {"task_id": task_id, "kind": kind, "params": params, "status": "queued", "queued_at": _now(), "backend": "thread", "result": None, "error": ""}
    client = get_redis()
    if client is not None:
        record["backend"] = "redis"
        _redis_save(client, record)
        client.lpush(TASK_IDS_KEY, task_id)
        client.ltrim(TASK_IDS_KEY, 0, 49)
        client.rpush(QUEUE_KEY, json.dumps({"task_id": task_id, "kind": kind, "params": params}, ensure_ascii=False))
        with _lock:
            _tasks[task_id] = record
        return record

    def _worker() -> None:
        with _lock:
            record["status"] = "running"
            record["started_at"] = _now()
        try:
            result = run_job(kind, params)
            with _lock:
                record["status"] = "finished"
                record["result"] = result
        except Exception as exc:
            log.exception("background task failed")
            with _lock:
                record["status"] = "failed"
                record["error"] = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-1500:]}"
        finally:
            with _lock:
                record["finished_at"] = _now()

    with _lock:
        _tasks[task_id] = record
    threading.Thread(target=_worker, name=task_id, daemon=True).start()
    return record


def list_tasks(limit: int = 20) -> list[dict]:
    with _lock:
        items = {task_id: dict(record) for task_id, record in _tasks.items()}
    client = get_redis()
    if client is not None:
        try:
            for task_id in client.lrange(TASK_IDS_KEY, 0, limit - 1):
                record = _redis_load(client, task_id)
                if record is not None:
                    items[task_id] = record
        except Exception as exc:
            log.warning("redis task list failed: %s", exc)
    ordered = sorted(items.values(), key=lambda t: t.get("queued_at", ""), reverse=True)
    return ordered[:limit]


def running_kinds() -> list[str]:
    return [t["kind"] for t in list_tasks(50) if t.get("status") in {"queued", "running"}]


def consume_queue(timeout: int) -> bool:
    """worker 用：BLPOP 一個工作並執行，狀態寫回 Redis；沒有 Redis 或逾時回傳 False。"""
    client = get_redis()
    if client is None:
        return False
    try:
        item = client.blpop(QUEUE_KEY, timeout=max(1, min(int(timeout), QUEUE_BLOCK_SECONDS)))
    except Exception as exc:  # 連線中斷／逾時：這一輪當作沒有工作，下一輪重連
        global _redis_client
        _redis_client = None
        log.warning("redis queue read failed (%s)；下一輪重連", exc)
        return False
    if not item:
        return False
    payload = json.loads(item[1])
    task_id = payload.get("task_id", "")
    record = _redis_load(client, task_id) or {"task_id": task_id, "kind": payload.get("kind"), "params": payload.get("params") or {}, "queued_at": _now(), "backend": "redis"}
    record.update({"status": "running", "started_at": _now(), "worker": "crawler-worker"})
    _redis_save(client, record)
    log.info("worker picked job %s", task_id)
    try:
        record["result"] = run_job(payload["kind"], payload.get("params") or {})
        record["status"] = "finished"
    except Exception as exc:
        log.exception("worker job failed")
        record["status"] = "failed"
        record["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        record["finished_at"] = _now()
        _redis_save(client, record)
    return True
