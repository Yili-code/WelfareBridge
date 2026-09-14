"""只重跑「收錄規則更新後 page_kind 變成排除」但目前仍被收錄的原始文件（不用整庫重跑）。"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from app.db import get_db  # noqa: E402
from app.services import admission  # noqa: E402
from app.services.pipeline import process_document  # noqa: E402

db = get_db()
targets = []
for d in db.raw_documents.find({"processing_status": {"$nin": ["filtered_out", "skipped", "provider_data"]}}, {"title": 1, "raw_text": 1, "source_url": 1, "processing_status": 1}):
    kind, reason = admission.page_kind(d.get("title") or "", d.get("raw_text") or "", d.get("source_url") or "")
    if kind in admission.EXCLUDED_KINDS:
        targets.append((d["_id"], d.get("title") or "", d.get("processing_status"), kind, reason))
print("to reprocess:", len(targets))
for doc_id, title, status, kind, reason in targets:
    result = process_document(doc_id, use_llm=True)
    print("  ", status, "→", result, "|", kind, "|", title[:50], "|", reason[:60])
print("benefits now:", db.benefits.count_documents({}))
