"""把探索代理寫好的候選來源 YAML 合併進 sources.yaml（只加新 id，不動既有來源）。

用法：python merge_candidates.py <id1> <id2> ...   （或 --all 合併 candidates/ 裡所有不以 _ 開頭的檔）
- 標題含「生育」的 pages 其 seed_category 改為 birth_incentive（探索時還沒有這個類別）
- 檢查 id 唯一、crawler 是 GenericPageCrawler、網域是 gov.tw / gov.taipei、pages 網址皆為 https
- 以文字附加在 sources.yaml 末尾的「本輪新增」區段，保留註解與排版
"""
from __future__ import annotations

import io
import os
import re
from pathlib import Path
import sys
from urllib.parse import urlsplit

import yaml

BACKEND = str(Path(__file__).resolve().parents[2])
SOURCES = os.path.join(BACKEND, "benefit_crawler/config/sources.yaml")
CAND_DIR = str(Path(__file__).resolve().parents[3] / "data/round3/candidates")
SECTION = "  # ======================================================================= 本輪新增：中央部會、縣市社會局、區公所（探索代理乾跑驗證後合併）\n"


def _whitelist() -> set[str]:
    data = yaml.safe_load(io.open(os.path.join(BACKEND, "benefit_crawler/config/official_domains.yaml"), encoding="utf-8").read()) or {}
    return {h.lower() for h in (data.get("whitelist") or {})}


WHITELIST = _whitelist()


def official(host: str) -> bool:
    host = host.lower()
    return host.endswith(".gov.tw") or host == "gov.tw" or host.endswith(".gov.taipei") or host in WHITELIST


def normalize(cfg: dict) -> tuple[dict, list[str]]:
    problems = []
    cfg = dict(cfg)
    if cfg.get("crawler") != "benefit_crawler.generic.page_crawler.GenericPageCrawler":
        problems.append(f"crawler 不是 GenericPageCrawler: {cfg.get('crawler')}")
    host = urlsplit(cfg.get("base_url", "")).netloc
    if not official(host):
        problems.append(f"base_url 網域不是官方: {host}")
    pages = []
    for p in cfg.get("pages") or []:
        url = p.get("url", "")
        h = urlsplit(url).netloc
        if not url.startswith("https://") or not official(h):
            problems.append(f"page 網址不合格: {url}")
            continue
        if "getgrant" in url.lower():
            problems.append(f"page 網址指向 getgrant: {url}")
            continue
        p = dict(p)
        if "生育" in (p.get("title") or "") and p.get("seed_category") in {"child_allowance", "", None}:
            p["seed_category"] = "birth_incentive"
        pages.append(p)
    cfg["pages"] = pages
    if not pages:
        problems.append("沒有任何 pages")
    for key in ("id", "name", "organization", "provider_type", "base_url", "expected_title_keywords", "domains"):
        if not cfg.get(key):
            problems.append(f"缺少欄位 {key}")
    cfg.setdefault("source_type", "government_site")
    cfg.setdefault("data_confidence", 100)
    cfg.setdefault("enabled", True)
    return cfg, problems


def inline(val) -> str:
    """單行 YAML 值：safe_dump 對純量會附上文件結尾符號「...」，要去掉。"""
    s = yaml.safe_dump(val, allow_unicode=True, default_flow_style=True, sort_keys=False, width=10000).strip()
    if s.endswith("\n..."):
        s = s[:-4].strip()
    return s


def dump_source(cfg: dict) -> str:
    order = ["id", "name", "organization", "provider_type", "source_type", "base_url", "crawler", "expected_title_keywords", "data_confidence", "enabled", "max_pages", "domains", "content_selectors", "split_selector", "follow_links", "notes", "pages"]
    lines = []
    first = True
    for key in order:
        if key not in cfg:
            continue
        val = cfg[key]
        prefix = "  - " if first else "    "
        first = False
        if key == "pages":
            lines.append(f"{prefix}pages:")
            for p in val:
                item = {k: v for k, v in p.items() if v not in (None, "")}
                lines.append("      - " + inline(item))
        elif key == "follow_links":
            lines.append(f"{prefix}follow_links:")
            for k, v in val.items():
                lines.append(f"      {k}: " + inline(v))
        else:
            lines.append(f"{prefix}{key}: " + inline(val))
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    ids = [a for a in argv if not a.startswith("--")]
    if "--all" in argv:
        ids = [f[:-5] for f in sorted(os.listdir(CAND_DIR)) if f.endswith(".yaml") and not f.startswith("_")]
    text = io.open(SOURCES, encoding="utf-8").read()
    existing = set(re.findall(r"^\s*- id:\s*(\S+)", text, re.M))
    added, blocks = [], []
    for sid in ids:
        path = os.path.join(CAND_DIR, sid + ".yaml")
        try:
            raw = yaml.safe_load(io.open(path, encoding="utf-8").read())
        except Exception as exc:  # 例如 regex 的 \. 在雙引號字串裡是非法跳脫
            print("SKIP", sid, "| YAML 讀不進來:", str(exc).splitlines()[0][:120])
            continue
        cfg = raw["sources"][0] if isinstance(raw, dict) and "sources" in raw else raw
        cfg, problems = normalize(cfg)
        if cfg.get("id") != sid:
            problems.append(f"檔名 {sid} 與 id {cfg.get('id')} 不一致")
        if cfg.get("id") in existing:
            problems.append(f"id 已存在於 sources.yaml: {cfg.get('id')}")
        if problems:
            print("SKIP", sid, "|", "; ".join(problems))
            continue
        blocks.append(dump_source(cfg))
        added.append(sid)
        existing.add(sid)
    if not blocks:
        print("nothing merged")
        return 1
    if SECTION not in text:
        text = text.rstrip("\n") + "\n\n" + SECTION
    text = text.rstrip("\n") + "\n\n" + "\n".join(blocks)
    yaml.safe_load(text)  # 合併後必須仍是合法 YAML
    io.open(SOURCES, "w", encoding="utf-8").write(text)
    print("merged:", ", ".join(added))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
