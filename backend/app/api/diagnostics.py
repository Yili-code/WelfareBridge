"""Read-only diagnosis of caller-supplied profiles against public benefit rules."""
import re
from fastapi import APIRouter
from pydantic import BaseModel, Field
from ..db import get_db
from ..matching import MatchingEngine, Profile, rank

router = APIRouter(prefix="/api", tags=["matching"])

class DiagnosticRequest(BaseModel):
    profile: dict
    search: str = Field(default="", max_length=200)

def exclusions(record):
    reasons = []
    if record.get("record_kind") == "portal":
        reasons.append("入口／彙整頁不參與候選檢索")
    if (record.get("classification") or {}).get("uncertain") is True:
        reasons.append("補助分類尚待確認")
    if record.get("is_canonical") is not True:
        reasons.append("非主要紀錄（重複或尚未完成去重）")
    if record.get("status") == "expired":
        reasons.append("資料標示已過期")
    return reasons

@router.post("/matching/diagnose")
def diagnose(body: DiagnosticRequest):
    db = get_db()
    query = {"title": {"$regex": re.escape(body.search.strip()), "$options": "i"}} if body.search.strip() else {}
    total = db.benefits.count_documents(query)
    records = list(db.benefits.find(query).sort("_id", 1).limit(200))
    profile = Profile.from_dict(body.profile)
    engine = MatchingEngine()
    results = []
    for record in records:
        item = engine.match_one(record, profile, use_llm=False)
        blocked = exclusions(record)
        ranking = rank([item], profile)
        ranked = (ranking["recommended"] + ranking["removed"] + ranking["other"])
        results.append({**item.to_dict(), "retrieval_exclusions": blocked,
                        "ranking_stage": ranked[0]["funnel_stage"] if ranked else "not_ranked",
                        "ranking_reasons": ranked[0]["why"] if ranked else [],
                        "rule_count": len(record.get("rules") or [])})
    return {"profile_used": profile.to_dict(), "profile_notes": profile.notes,
            "items": results, "total": total, "returned": len(results),
            "truncated": total > len(results), "llm_used": False}
