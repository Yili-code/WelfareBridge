"""候選來源設定的乾跑（不寫資料庫）：讀一個只含單一來源的 YAML，套 sources.yaml 的 defaults，真的去抓頁面，
印出每份文件的標題／網址／字數／收錄判斷（page_kind）／關鍵字分類器意見，方便判斷設定檔對不對。

用法（在 backend/ 執行，或任何目錄）：
    python dry_run_candidate.py <candidate.yaml> [--max-items 8]
candidate.yaml 可以是單一來源的 mapping（含 id, name, base_url, crawler, pages…），或 {sources: [ ... ]}。
"""
from __future__ import annotations

import argparse
import io
import os
from pathlib import Path
import sys
import tempfile

BACKEND = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import yaml  # noqa: E402

from app.services import crawl_service  # noqa: E402
from app.services.admission import page_kind  # noqa: E402
from app.services.classifier import get_classifier  # noqa: E402
from benefit_crawler.base.registry import build_crawler, load_sources_config  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate")
    ap.add_argument("--max-items", type=int, default=8)
    args = ap.parse_args()

    raw = yaml.safe_load(io.open(args.candidate, encoding="utf-8").read())
    sources = raw["sources"] if isinstance(raw, dict) and "sources" in raw else [raw]
    base = yaml.safe_load(io.open(os.path.join(BACKEND, "benefit_crawler/config/sources.yaml"), encoding="utf-8").read())
    merged = {"defaults": base.get("defaults", {}), "sources": sources}
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as tmp:
        yaml.safe_dump(merged, tmp, allow_unicode=True, sort_keys=False)
        tmp_path = tmp.name

    validator = crawl_service._validator()
    http = crawl_service._http()
    clf = get_classifier()
    try:
        for config in load_sources_config(tmp_path):
            validation = validator.validate_url(config["base_url"])
            print(f"[{config['id']}] {config['name']}")
            print(f"    base_url={config['base_url']} official={validation.verified} method={validation.method} status={validation.status}")
            if not validation.verified:
                print("    !! 不是通過驗證的官方網域：不能收錄。", validation.to_dict())
            crawler = build_crawler(config, http=http, validator=validator, max_items=args.max_items)
            result = crawler.run()
            print(f"    run: status={result.status} discovered={result.discovered} fetched={result.fetched} failed={result.failed} documents={len(result.documents)}")
            for err in result.errors[:5]:
                print(f"    ! {err}")
            kinds = {}
            for doc in result.documents:
                kind, reason = page_kind(doc.title, doc.raw_text, doc.source_url)
                kinds[kind] = kinds.get(kind, 0) + 1
                kw = clf.classify(doc.title, doc.raw_text)
                cats = list(kw.category_scores.keys())[:2]
                preview = " ".join((doc.raw_text or "").split())[:160]
                print(f"    - [{doc.content_type}] {doc.title[:50]} | {doc.source_url[:100]}")
                print(f"      kind={kind} kw_benefit={kw.is_benefit} conf={kw.confidence} cats={cats} text={len(doc.raw_text or '')} chars {('| ' + reason[:60]) if reason else ''}")
                print(f"      {preview}")
            print(f"    kinds: {kinds}")
    finally:
        http.close()
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
