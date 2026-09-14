"""POST /api/matching、/api/profile/parse、/api/profile/questions、/api/users/profile、/api/feedback。"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException

from ..config import get_settings
from ..db import get_db, utcnow
from ..llm import fill as llm_fill
from ..matching import MatchingEngine, Profile, hard_filter_candidates, load_records, parse_profile_text, plan_questions, rank
from ..registry import get_registry
from ..schemas import DISCLAIMER, FeedbackRequest, MatchRequest, ProfileParseRequest, QuestionsRequest, SaveProfileRequest

log = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["matching"])
FEEDBACK_EVENTS = {"viewed", "expanded", "clicked_source", "applied", "awarded", "rejected", "not_interested", "reported_error"}


def _save_profile(db, profile: Profile, body_user_id: str | None, input_mode: str, raw_input: str) -> tuple[str, str]:
    user_id = body_user_id or str(uuid.uuid4())
    profile_id = str(uuid.uuid4())
    db.user_profiles.insert_one({"_id": profile_id, "user_id": user_id, "input_mode": input_mode, "raw_input": raw_input, "profile": profile.to_dict(), "registry_version": get_registry().version, "created_at": utcnow()})
    return user_id, profile_id


@router.post("/matching")
def run_matching(body: MatchRequest) -> dict:
    db = get_db()
    settings = get_settings()
    registry = get_registry()
    profile = Profile.from_dict(body.profile, registry)
    records = load_records(db, include_expired=body.include_expired, domains=body.domains, with_text=True)
    candidates, excluded = hard_filter_candidates(records, profile, registry, settings)
    llm_available = llm_fill.llm_available()  # 本地 AI 是否在線（與「本次有沒有用」分開回報）
    use_llm_now = bool(body.use_llm and llm_available)
    engine = MatchingEngine(registry=registry, llm_judge=llm_fill.judge_complex if use_llm_now else None)
    items = engine.match_all(candidates, profile, use_llm=use_llm_now, llm_budget=body.llm_budget)
    # 被硬過濾排除的也列出（狀態 not_match），讓使用者看得到原因
    for record in excluded:
        items.append(engine.match_one(record, profile, use_llm=False))
    items = items[: body.limit]
    summary = {"high_match": 0, "possible_match": 0, "insufficient_data": 0, "not_match": 0, "total": len(items)}
    for item in items:
        summary[item.status] = summary.get(item.status, 0) + 1
    ranking = rank(items, profile, registry=registry)
    user_id, profile_id = _save_profile(db, profile, body.user_id, body.input_mode, body.raw_input)
    for item in items:
        if item.status == "not_match":
            continue
        db.match_results.insert_one({"_id": str(uuid.uuid4()), "profile_id": profile_id, "benefit_id": item.benefit_id, "status": item.status, "eligibility_score": item.eligibility_score, "missing_attributes": item.missing_attributes, "registry_version": registry.version, "created_at": utcnow()})
    return {
        "matches": [item.to_dict() for item in items],
        "summary": summary,
        "ranking": ranking,
        "disclaimer": DISCLAIMER,
        "profile_used": profile.to_dict(),
        "profile_chips": profile.summary_chips(registry),
        "user_id": user_id,
        "profile_id": profile_id,
        "llm_used": any(item.llm_used for item in items),
        "llm_available": llm_available,
        "hard_filter_excluded": len(excluded),
    }


@router.post("/profile/parse")
def parse_profile(body: ProfileParseRequest) -> dict:
    registry = get_registry()
    base = Profile.from_dict(body.base_profile, registry) if body.base_profile else None
    profile, parsed, hints = parse_profile_text(body.text, base, registry)
    llm_used = False
    if body.use_llm and llm_fill.llm_available():
        try:
            result = llm_fill.parse_profile(body.text, profile.raw_values())
            for item in result["attributes"]:
                if item["id"] in profile.attributes and profile.attributes[item["id"]].value is not None:
                    continue
                profile.set(item["id"], item["value"], source="parsed", evidence=item["excerpt"], confirmed=False, confidence=item["confidence"])
                parsed.append({"attribute_id": item["id"], "value": profile.attributes[item["id"]].value if item["id"] in profile.attributes else item["value"], "excerpt": item["excerpt"], "extractor": "llm", "confidence": item["confidence"]})
                llm_used = True
            if profile.need_type == "unknown" and result["need_type"] != "unknown":
                profile.need_type = result["need_type"]
                parsed.append({"attribute_id": "need_type", "value": result["need_type"], "excerpt": result["need_excerpt"], "extractor": "llm", "confidence": 0.6})
                llm_used = True
        except Exception as exc:
            log.warning("llm profile parse failed: %s", exc)
            hints.append("本地 AI 補充解析失敗，僅使用規則式結果")
    return {"profile": profile.to_dict(), "parsed_fields": parsed, "unparsed_hints": hints, "llm_used": llm_used, "chips": profile.summary_chips(registry)}


@router.post("/profile/questions")
def next_questions(body: QuestionsRequest) -> dict:
    db = get_db()
    registry = get_registry()
    settings = get_settings()
    profile = Profile.from_dict(body.profile, registry)
    records = load_records(db, domains=body.domains)
    candidates, _excluded = hard_filter_candidates(records, profile, registry, settings)
    engine = MatchingEngine(registry=registry)
    items = engine.match_all(candidates, profile, use_llm=False) if body.mode != "step" or records else []
    return plan_questions(profile, items, candidates, mode=body.mode, max_questions=body.max_questions, engine=engine, registry=registry)


@router.post("/users/profile")
def create_profile(body: SaveProfileRequest) -> dict:
    db = get_db()
    profile = Profile.from_dict(body.profile)
    user_id, profile_id = _save_profile(db, profile, body.user_id, body.input_mode, body.raw_input)
    return {"user_id": user_id, "profile_id": profile_id, "profile": profile.to_dict()}


@router.get("/users/profile/{profile_id}")
def get_profile(profile_id: str) -> dict:
    db = get_db()
    row = db.user_profiles.find_one({"_id": profile_id})
    if row is None:
        raise HTTPException(status_code=404, detail="profile not found")
    return {"user_id": row.get("user_id"), "profile_id": profile_id, "profile": row.get("profile"), "input_mode": row.get("input_mode"), "raw_input": row.get("raw_input", "")}


@router.post("/feedback")
def feedback(body: FeedbackRequest) -> dict:
    if body.event not in FEEDBACK_EVENTS:
        raise HTTPException(status_code=400, detail=f"unknown event {body.event}")
    db = get_db()
    doc = {"_id": str(uuid.uuid4()), "benefit_id": body.benefit_id, "profile_id": body.profile_id, "event": body.event, "reason": body.reason, "note": body.note[:500], "created_at": utcnow()}
    db.feedback_events.insert_one(doc)
    if body.event == "reported_error":
        db.review_items.insert_one({"_id": str(uuid.uuid4()), "kind": "user_reported", "benefit_id": body.benefit_id, "raw_document_id": None, "payload": {"reason": body.reason, "note": body.note[:500]}, "status": "open", "created_at": utcnow(), "resolved_at": None, "action": ""})
    return {"ok": True, "id": doc["_id"]}
