from pathlib import Path
import pytest
from app.config import Settings
from benefit_crawler.base.registry import get_crawler_class, load_sources_config
from benefit_crawler.__main__ import main

def test_all_registered_crawlers_resolve_after_rename():
    settings = Settings()
    for source in load_sources_config(settings.sources_config_file):
        assert get_crawler_class(source["crawler"])
    assert settings.demo_seed_file.is_file()
    assert settings.attribute_registry_file.is_file()
    assert settings.keyword_rules_file.is_file()

def test_worker_only_does_not_schedule_a_crawl(monkeypatch):
    from app import db
    from app.services import crawl_service, tasks
    monkeypatch.setattr(db, "init_db", lambda: None)
    monkeypatch.setattr(crawl_service, "ensure_sources", lambda: None)
    monkeypatch.setattr(crawl_service, "run_sources", lambda **kwargs: pytest.fail("worker-only scheduled a crawl"))
    monkeypatch.setattr(crawl_service, "fail_interrupted_jobs", lambda _now: 0)
    monkeypatch.setattr(tasks, "recover_interrupted_tasks", lambda: 0)
    def consume(timeout):
        assert timeout == 30
        raise KeyboardInterrupt
    monkeypatch.setattr(tasks, "consume_queue", consume)
    assert main(["--worker"]) == 0
