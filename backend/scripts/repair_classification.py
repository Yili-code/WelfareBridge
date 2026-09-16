"""補助分類資料修復（一次性，可重跑）：

  1. 縣市政府來源的補助沒有轄區（機關欄抽成「林社工為您服務」等）→ 以來源機關的縣市補上 provider_region
  2. 重跑去重：各縣市同名方案（低收入戶生活補助、育兒津貼…）不再被併成一筆，被藏起來的縣市版本恢復為主要紀錄
  3. 分類「待確認」的補助：本地 AI 在線時重新處理原始文件（當初常是 AI 離線才留在待確認）

    python scripts/repair_classification.py --dry     # 只列出會改什麼
    python scripts/repair_classification.py
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_db  # noqa: E402
from app.llm import fill as llm_fill  # noqa: E402
from app.services import pipeline  # noqa: E402
from app.services.normalization import find_cities  # noqa: E402

log = logging.getLogger("repair_classification")


def backfill_regions(db, dry: bool) -> int:
    sources = {s["_id"]: s for s in db.sources.find({"provider_type": {"$in": ["local_government", "township"]}}, {"organization": 1, "name": 1, "provider_type": 1})}
    changed = 0
    for row in db.benefits.find({"source_id": {"$in": list(sources)}, "$or": [{"provider_region": None}, {"provider_region": ""}]}, {"title": 1, "source_id": 1}):
        source = sources[row["source_id"]]
        cities = find_cities(source.get("organization") or source.get("name") or "")
        if not cities:
            continue
        print(f"  region {cities[0]} ← {row['title'][:40]}")
        if not dry:
            db.benefits.update_one({"_id": row["_id"]}, {"$set": {"provider_region": cities[0]}})
        changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    db = get_db()
    print("1. 補上縣市政府來源的轄區")
    print(f"   {backfill_regions(db, args.dry)} 筆")
    print("2. 重跑去重（不同轄區不合併）")
    before = db.benefits.count_documents({"is_canonical": True})
    if not args.dry:
        changed = pipeline.dedup_pass()
        print(f"   更新 {changed} 筆；主要紀錄 {before} → {db.benefits.count_documents({'is_canonical': True})}")
    print("3. 分類待確認的補助重新交給本地 AI 判斷")
    uncertain = list(db.benefits.find({"classification.uncertain": True}, {"title": 1, "raw_document_id": 1}))
    if not llm_fill.llm_available():
        print(f"   本地 AI 不在線，略過 {len(uncertain)} 筆")
        return 0
    for row in uncertain:
        if args.dry:
            print(f"   待處理：{row['title'][:40]}")
            continue
        outcome = pipeline.process_document(row["raw_document_id"], use_llm=True)
        print(f"   {outcome}: {row['title'][:40]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
