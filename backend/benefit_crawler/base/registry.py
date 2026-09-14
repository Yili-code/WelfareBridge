"""來源設定載入與 crawler class 解析。"""

from __future__ import annotations

import importlib
from pathlib import Path

import yaml

from .base_crawler import BaseCrawler


def load_sources_config(path: str | Path) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    defaults = data.get("defaults", {}) or {}
    sources: list[dict] = []
    for raw in data.get("sources", []) or []:
        merged = {**defaults, **raw}
        merged.setdefault("enabled", True)
        merged.setdefault("provider_type", "unknown")
        merged.setdefault("source_type", "government_site")
        merged.setdefault("data_confidence", 95)
        sources.append(merged)
    return sources


def select_sources(sources: list[dict], *, ids: list[str] | None = None, only_enabled: bool = True) -> list[dict]:
    selected = []
    for source in sources:
        if ids and source["id"] not in ids:
            continue
        if only_enabled and not ids and not source.get("enabled", True):
            continue
        selected.append(source)
    return selected


def get_crawler_class(dotted_path: str) -> type[BaseCrawler]:
    module_name, _, class_name = dotted_path.rpartition(".")
    module = importlib.import_module(module_name)
    crawler_class = getattr(module, class_name)
    if not (isinstance(crawler_class, type) and issubclass(crawler_class, BaseCrawler)):
        raise TypeError(f"{dotted_path} 不是 BaseCrawler 的子類別")
    return crawler_class


def build_crawler(source_config: dict, **kwargs) -> BaseCrawler:
    crawler_class = get_crawler_class(source_config["crawler"])
    return crawler_class(source_config, **kwargs)
