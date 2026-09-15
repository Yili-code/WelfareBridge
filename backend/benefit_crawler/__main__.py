"""Crawler / pipeline CLI（v2）。

    python -m benefit_crawler                       # 爬取所有啟用的官方來源，接著跑 pipeline（分類 → 抽取 → 本地 AI 補齊 → 驗證 → MongoDB）
    python -m benefit_crawler --source taipei_dosw --source mol_gov
    python -m benefit_crawler --list                # 列出來源與官方驗證結果
    python -m benefit_crawler --no-pipeline         # 只爬取、存 raw_documents
    python -m benefit_crawler --pipeline-only       # 不爬取，只處理待處理／有變更的 raw_documents
    python -m benefit_crawler --pipeline-only --force   # 強制重新解析所有 raw_documents
    python -m benefit_crawler --no-llm              # pipeline 不呼叫本地 AI
    python -m benefit_crawler --llm-fill            # 只對已抽取但 AI 尚未補齊的 benefits 執行本地 AI 補齊
    python -m benefit_crawler --mine-keywords       # 依目前語料統計關鍵字 → keyword_rules_v2.yaml + docs/generated/keyword-report.md
    python -m benefit_crawler --import-legacy       # 把 v1 demo_seed.json 的原始文件匯入 MongoDB（之後用 --pipeline-only --force 重新解析）
    python -m benefit_crawler --dry-run --max-items 3
    python -m benefit_crawler --export-seed         # 匯出 data/demo/seed_v2.json
    python -m benefit_crawler --loop 21600          # worker 模式

需在 backend/ 目錄執行（或設定 PYTHONPATH=backend）。
"""

from __future__ import annotations

import argparse
import logging
import sys
import time


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m benefit_crawler", description="官方補助來源爬蟲與解析 pipeline（v2）")
    parser.add_argument("--source", action="append", help="只執行指定來源 id（可重複）")
    parser.add_argument("--list", action="store_true", help="列出所有來源與驗證狀態")
    parser.add_argument("--no-pipeline", action="store_true", help="只爬取，不執行解析 pipeline")
    parser.add_argument("--pipeline-only", action="store_true", help="不爬取，只執行解析 pipeline")
    parser.add_argument("--force", action="store_true", help="pipeline 強制重新處理所有文件")
    parser.add_argument("--no-llm", action="store_true", help="pipeline 不使用本地 AI")
    parser.add_argument("--reset-llm", action="store_true", help="pipeline --force 時連已經過本地 AI 補齊的資料也重新抽取（預設保留）")
    parser.add_argument("--no-fill", action="store_true", help="pipeline 的本地 AI 只用在分類投票，欄位補齊延後用 --llm-fill（只補 canonical）")
    parser.add_argument("--llm-fill", action="store_true", help="只執行本地 AI 補齊（對尚未補齊的 benefits）")
    parser.add_argument("--include-non-canonical", action="store_true", help="--llm-fill 時連非 canonical 的重複紀錄也補齊（預設只補 canonical）")
    parser.add_argument("--mine-keywords", action="store_true", help="依語料統計關鍵字並產生 keyword_rules_v2.yaml 與報告")
    parser.add_argument("--import-legacy", action="store_true", help="匯入 v1 demo_seed.json 的原始文件")
    parser.add_argument("--dry-run", action="store_true", help="不寫入資料庫")
    parser.add_argument("--export-seed", action="store_true", help="匯出 seed_v2.json")
    parser.add_argument("--max-items", type=int, default=None, help="每個來源最多抓幾筆")
    parser.add_argument("--limit", type=int, default=None, help="pipeline / llm-fill 最多處理幾筆")
    parser.add_argument("--loop", type=int, default=0, help="worker 模式：每 N 秒重跑一次")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--worker", action="store_true", help="只處理 API 工作佇列；搭配 --loop 可啟用週期爬取")
    args = parser.parse_args(argv)

    logging.basicConfig(level=args.log_level.upper(), format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    from app.db import init_db
    from app.services import crawl_service

    if args.list:
        for line in crawl_service.describe_sources():
            print(line)
        return 0

    if args.dry_run:
        for line in crawl_service.dry_run(source_ids=args.source, max_items=args.max_items):
            print(line)
        return 0

    init_db()
    crawl_service.ensure_sources()

    if args.import_legacy:
        from app.services.legacy_import import import_legacy_seed

        print(f"[legacy] {import_legacy_seed()}")
        return 0

    if args.mine_keywords:
        from app.services.keyword_mining import mine_and_write

        report = mine_and_write()
        print(f"[mine-keywords] {report}")
        return 0

    if args.export_seed:
        from app.services.seed import export_seed

        print(f"seed 已匯出：{export_seed()}")
        return 0

    if args.llm_fill:
        from app.services import pipeline

        print(f"[llm-fill] {pipeline.llm_fill_pending(limit=args.limit, canonical_only=not args.include_non_canonical)}")
        return 0

    def one_round() -> None:
        if not args.pipeline_only:
            results = crawl_service.run_sources(source_ids=args.source, triggered_by="cli", max_items=args.max_items)
            for result in results:
                print(
                    f"[{result['source_id']}] {result['status']}: discovered={result['discovered']} fetched={result['fetched']} "
                    f"new={result['new_documents']} updated={result['updated_documents']} unchanged={result['unchanged_documents']} "
                    f"failed={result['failed_items']}"
                )
                if result.get("error"):
                    print(f"    ! {result['error'][:300]}")
        if not args.no_pipeline:
            from app.services import pipeline

            stats = pipeline.process_pending(source_ids=args.source, force=args.force, use_llm=False if args.no_llm else None, limit=args.limit, reset_llm=args.reset_llm, fill=not args.no_fill)
            print(f"[pipeline] {stats}")

    if args.loop > 0 or args.worker:
        from app.db import utcnow
        from app.services import tasks

        interrupted = tasks.recover_interrupted_tasks() + crawl_service.fail_interrupted_jobs(utcnow())
        if interrupted:
            logging.getLogger("crawler").warning("worker 啟動：%d 筆上次中斷的工作已標記為失敗", interrupted)

        next_round = 0.0 if args.loop > 0 else float("inf")
        while True:
            try:
                if time.monotonic() >= next_round:
                    one_round()
                    next_round = time.monotonic() + args.loop
                wait = max(1, int(next_round - time.monotonic())) if args.loop > 0 else 30
                if not tasks.consume_queue(timeout=min(wait, 30)):
                    if tasks.get_redis() is None:
                        time.sleep(min(wait, 30))
            except KeyboardInterrupt:
                return 0
            except Exception as exc:  # worker 不因單輪失敗而結束
                logging.getLogger("crawler").exception("round failed: %s", exc)
                time.sleep(10)
    else:
        one_round()
    return 0


if __name__ == "__main__":
    sys.exit(main())
