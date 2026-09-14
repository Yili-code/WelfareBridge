"""patch33 之後對已處理的紀錄做確定性回填（不重跑本地 AI）：
1. 彙整頁（page_kind=portal）若被過濾或標成疑似補助 → 用新規則重跑 process_document（portal 不投票、不呼叫 LLM）
2. provider 是科室簡稱（發布單位：社會局）且來源機關名以它結尾 → 改成完整機關名（evidence 摘錄不動）
3. 原文有「隨時申請／全年受理…」且沒有截止日 → application_period.rolling=True，移除「原文未找到申請截止日期」備註
用法：python backfill_round3.py <source_id> ... [--dry]
"""
from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.db import get_db  # noqa: E402
from app.services import admission  # noqa: E402
from app.services.extractor import ROLLING_RE  # noqa: E402
from app.services.pipeline import process_document  # noqa: E402


def main(argv: list[str]) -> int:
    dry = "--dry" in argv
    sources = [a for a in argv if not a.startswith("--")]
    db = get_db()
    q = {"source_id": {"$in": sources}} if sources else {}
    # 1. 彙整頁
    n_portal = 0
    for d in db.raw_documents.find({**q, "processing_status": {"$in": ["filtered_out", "needs_review", "extracted"]}}, {"title": 1, "raw_text": 1, "source_url": 1, "processing_status": 1, "classification.uncertain": 1, "classification.page_kind": 1}):
        kind, _ = admission.page_kind(d.get("title") or "", d.get("raw_text") or "", d.get("source_url") or "")
        if kind != "portal":
            continue
        c = d.get("classification") or {}
        if d.get("processing_status") == "filtered_out" or c.get("uncertain") or c.get("page_kind") != "portal":
            n_portal += 1
            if not dry:
                r = process_document(d["_id"], use_llm=True)
                print("  portal →", r, "|", (d.get("title") or "")[:40])
    print("portal docs reprocessed:", n_portal)
    # 2. provider 科室簡稱
    src_org = {s["_id"]: s.get("organization") or "" for s in db.sources.find({}, {"organization": 1})}
    n_prov = 0
    for b in db.benefits.find(q, {"provider": 1, "source_id": 1, "title": 1}):
        prov = (b.get("provider") or "").strip()
        org = src_org.get(b.get("source_id"), "")
        if prov and org and prov != org and len(prov) <= 6 and org.endswith(prov):
            n_prov += 1
            if not dry:
                db.benefits.update_one({"_id": b["_id"]}, {"$set": {"provider": org}})
            print("  provider", prov, "→", org, "|", (b.get("title") or "")[:40])
    print("providers fixed:", n_prov)
    # 3. rolling
    n_roll = 0
    for b in db.benefits.find(q, {"original_text": 1, "benefit.application_period": 1, "review.reasons": 1, "title": 1}):
        ap = (b.get("benefit") or {}).get("application_period") or {}
        if ap.get("end_date") or ap.get("rolling"):
            continue
        m = ROLLING_RE.search(b.get("original_text") or "")
        if not m:
            continue
        n_roll += 1
        reasons = [r for r in ((b.get("review") or {}).get("reasons") or []) if r != "原文未找到申請截止日期"]
        if not dry:
            db.benefits.update_one({"_id": b["_id"]}, {"$set": {"benefit.application_period.rolling": True, "benefit.application_period.description": f"隨時受理：「{m.group(0)}」", "review.reasons": reasons}})
    print("rolling set:", n_roll)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
