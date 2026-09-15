"""worker 中途停止後重新啟動：卡在 running 的工作要標成失敗，資料中心才不會一直鎖住按鈕。"""

import json
from datetime import datetime, timedelta

from app.services import crawl_service, tasks


class FakeRedis:
    def __init__(self):
        self.data: dict[str, str] = {}
        self.lists: dict[str, list[str]] = {}

    def get(self, key):
        return self.data.get(key)

    def set(self, key, value, ex=None):
        self.data[key] = value

    def lrange(self, key, start, end):
        items = self.lists.get(key, [])
        return items[start:] if end == -1 else items[start:end + 1]


def test_recover_interrupted_tasks_marks_only_running_tasks(monkeypatch):
    fake = FakeRedis()
    fake.lists[tasks.TASK_IDS_KEY] = ["a", "b", "c"]
    for task_id, status in [("a", "running"), ("b", "finished"), ("c", "queued")]:
        fake.set(tasks.TASK_KEY.format(task_id=task_id), json.dumps({"task_id": task_id, "kind": "crawl", "status": status}))
    monkeypatch.setattr(tasks, "get_redis", lambda: fake)

    assert tasks.recover_interrupted_tasks() == 1
    records = {t: json.loads(fake.get(tasks.TASK_KEY.format(task_id=t))) for t in "abc"}
    assert {t: r["status"] for t, r in records.items()} == {"a": "failed", "b": "finished", "c": "queued"}
    assert records["a"]["error"] and records["a"]["finished_at"]


def test_recover_interrupted_tasks_without_redis(monkeypatch):
    monkeypatch.setattr(tasks, "get_redis", lambda: None)
    assert tasks.recover_interrupted_tasks() == 0


def test_fail_interrupted_jobs_only_touches_running_jobs_started_before(db):
    now = datetime(2026, 9, 15, 12, 0)
    ids = ["t-old-running", "t-old-success", "t-new-running"]
    db.crawl_jobs.insert_many([
        {"_id": ids[0], "status": "running", "started_at": now - timedelta(hours=1), "error": ""},
        {"_id": ids[1], "status": "success", "started_at": now - timedelta(hours=1), "error": ""},
        {"_id": ids[2], "status": "running", "started_at": now + timedelta(seconds=1), "error": ""},
    ])
    try:
        assert crawl_service.fail_interrupted_jobs(now) >= 1
        statuses = {j["_id"]: j["status"] for j in db.crawl_jobs.find({"_id": {"$in": ids}})}
        assert statuses == {"t-old-running": "failed", "t-old-success": "success", "t-new-running": "running"}
        assert db.crawl_jobs.find_one({"_id": ids[0]})["error"]
    finally:
        db.crawl_jobs.delete_many({"_id": {"$in": ids}})
