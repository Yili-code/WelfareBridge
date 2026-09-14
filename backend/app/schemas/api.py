"""API 輸出入模型（v2）。profile 以 dict 傳遞（{attributes: {id: value | {value,...}}, need_type, dislikes, ...}），由 matching.Profile 解析。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

DISCLAIMER = "以上為系統依官方公告內容進行的初步資格比對，實際資格仍以主辦機關審核結果為準。"


class MatchRequest(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    user_id: str | None = None
    input_mode: str = "form"  # form | step | quick
    raw_input: str = ""
    include_expired: bool = False
    use_llm: bool = True
    # 整個請求最多呼叫本地 AI 幾次（複雜條件判斷）；0 = 不呼叫
    llm_budget: int = Field(12, ge=0, le=60)
    limit: int = Field(300, ge=1, le=2000)
    domains: list[str] | None = None


class QuestionsRequest(BaseModel):
    profile: dict[str, Any] = Field(default_factory=dict)
    mode: str = "dynamic"  # dynamic | step
    max_questions: int = Field(3, ge=1, le=10)
    domains: list[str] | None = None


class ProfileParseRequest(BaseModel):
    text: str
    base_profile: dict[str, Any] | None = None
    use_llm: bool = True


class SaveProfileRequest(BaseModel):
    profile: dict[str, Any]
    user_id: str | None = None
    input_mode: str = "form"
    raw_input: str = ""


class FeedbackRequest(BaseModel):
    benefit_id: str
    profile_id: str | None = None
    event: str  # viewed | expanded | clicked_source | applied | awarded | rejected | not_interested | reported_error
    reason: str | None = None
    note: str = ""


class PipelineRequest(BaseModel):
    source_ids: list[str] | None = None
    force: bool = False
    use_llm: bool | None = None
    limit: int | None = Field(None, ge=1, le=5000)


class RunRequest(BaseModel):
    source_ids: list[str] | None = None
    run_pipeline: bool = True
    max_items: int | None = Field(None, ge=1, le=1000)


class ReviewActionRequest(BaseModel):
    action: str  # accept | edit | mark_synonym | approve_attribute | reject
    note: str = ""
    payload: dict[str, Any] | None = None
