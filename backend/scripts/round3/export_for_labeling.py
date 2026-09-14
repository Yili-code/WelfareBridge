"""從指定來源抽樣原始文件，輸出成黃金標註用的批次檔（與 data/gold/batch_*.txt 同格式）。

用法：python export_for_labeling.py --sources ntpc_sw taichung_sw ... --per-source 25 --batch-size 15 --out <dir> [--exclude-gold]
每個批次檔含 N 份文件：id / TITLE / SOURCE|STATUS|SYSTEM / URL / TEXT（最多 3500 字）。
抽樣：每個來源依 processing_status 分層（extracted / needs_review / filtered_out 都要有），確定性隨機（seed 7）。
"""
from __future__ import annotations

import argparse
import io
import json
import os
import random
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.db import get_db  # noqa: E402

GOLD = str(Path(__file__).resolve().parents[3] / "data/gold/gold_labels.yaml")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--per-source", type=int, default=25)
    ap.add_argument("--batch-size", type=int, default=15)
    ap.add_argument("--out", required=True)
    ap.add_argument("--exclude-gold", action="store_true")
    ap.add_argument("--max-chars", type=int, default=3500)
    args = ap.parse_args()

    db = get_db()
    gold_ids = set()
    if args.exclude_gold and os.path.exists(GOLD):
        import yaml
        gold_ids = {g["id"] for g in (yaml.safe_load(io.open(GOLD, encoding="utf-8").read()) or {}).get("labels", [])}
    rng = random.Random(7)
    picked = []
    for sid in args.sources:
        rows = list(db.raw_documents.find({"source_id": sid, "_id": {"$nin": list(gold_ids)}}, {"title": 1, "source_url": 1, "raw_text": 1, "processing_status": 1, "classification": 1, "meta.seed_category": 1, "source_id": 1}))
        rows = [r for r in rows if len(r.get("raw_text") or "") >= 60]
        by_status: dict[str, list] = {}
        for r in rows:
            by_status.setdefault(r.get("processing_status") or "?", []).append(r)
        quota = args.per_source
        chosen = []
        statuses = sorted(by_status)
        while quota > 0 and any(by_status.values()):
            for st in statuses:
                bucket = by_status[st]
                if bucket and quota > 0:
                    chosen.append(bucket.pop(rng.randrange(len(bucket))))
                    quota -= 1
        picked.extend(chosen)
        summary = ", ".join(f"{k}={sum(1 for c in chosen if c.get('processing_status') == k)}" for k in statuses)
        print(f"{sid}: {len(rows)} docs, picked {len(chosen)} ({summary})")
    rng.shuffle(picked)
    os.makedirs(args.out, exist_ok=True)
    ids = []
    for b in range(0, len(picked), args.batch_size):
        batch = picked[b:b + args.batch_size]
        path = os.path.join(args.out, f"batch_{b // args.batch_size + 1:02d}.txt")
        with io.open(path, "w", encoding="utf-8") as f:
            for r in batch:
                c = r.get("classification") or {}
                f.write(f"##### {r['_id']}\n")
                f.write(f"TITLE: {r.get('title', '')}\n")
                f.write(f"SOURCE: {r.get('source_id')} | STATUS: {r.get('processing_status')} | SYSTEM: is_benefit={c.get('is_benefit')} category={c.get('category')} method={c.get('method')} seed={(r.get('meta') or {}).get('seed_category')}\n")
                f.write(f"URL: {r.get('source_url', '')}\n")
                f.write("TEXT:\n")
                f.write((r.get("raw_text") or "")[: args.max_chars].rstrip() + "\n\n")
                ids.append(r["_id"])
        print("wrote", path, len(batch))
    io.open(os.path.join(args.out, "sample_ids.json"), "w", encoding="utf-8").write(json.dumps(ids, ensure_ascii=False, indent=0))
    print("total", len(ids))
    return 0


if __name__ == "__main__":
    sys.exit(main())
