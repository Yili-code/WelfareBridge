"""小幫手對話：追問由資格規劃器決定（不需要本地 AI）；只有「整理需求登記」用本地 AI 寫摘要。"""
import json
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError
from ..llm.factory import get_provider
from ..llm.provider import LLMError
from ..matching.guidance import guidance
from ..registry import get_registry
from pymongo.errors import PyMongoError

router = APIRouter(prefix="/api", tags=["assistant"])
LEARNED_SOURCES = {"asked", "parsed", "unsure"}


def _value_label(attribute, value) -> str:
    if value is None:
        return "不確定"
    if attribute.type == "boolean":
        return "是" if value else "否"
    if attribute.type == "multi_enum":
        return "、".join(attribute.value_label(v) for v in (value if isinstance(value, list) else [value]))
    if attribute.type == "enum":
        return attribute.value_label(value)
    if attribute.type == "number":
        number = float(value)
        return f"{number:g}{attribute.unit or ''}"
    return str(value)


def learned_attributes(profile: dict) -> list[dict]:
    """對話中問到或從回答判讀出的資料（不含問卷原本就有的）：前端寫回「我的資料卡」，主畫面依此重新比對。"""
    registry = get_registry()
    out = []
    for attribute_id, item in ((profile or {}).get("attributes") or {}).items():
        if not isinstance(item, dict) or item.get("source") not in LEARNED_SOURCES:
            continue
        attribute = registry.get(attribute_id)
        if attribute is None:
            continue
        options = [{"value": str(v.get("value")), "label": str(v.get("label", v.get("value")))} for v in attribute.values] if attribute.type in {"enum", "multi_enum"} else []
        out.append({"attribute_id": attribute_id, "label": attribute.label, "type": attribute.type, "unit": attribute.unit or "", "value": item.get("value"),
                    "value_label": _value_label(attribute, item.get("value")), "options": options, "source": item["source"], "evidence": str(item.get("evidence") or "")[:120]})
    return out

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

class Request(BaseModel):
    profile: dict | None = None
    messages: list[Message] = Field(default_factory=list, max_length=40)
    guidance_profile: dict | None = None
    question_attribute: str = Field(default="", max_length=150)

class Answer(BaseModel):
    reply: str = Field(min_length=1, max_length=2000)
    quickReplies: list[str] = Field(default_factory=list, max_length=4)
    summary: str = Field(default="", max_length=2000)
    mainRequest: str = Field(default="", max_length=500)

class Summary(BaseModel):
    summary: str = Field(min_length=1, max_length=2000)
    mainRequest: str = Field(min_length=1, max_length=500)

SUMMARY_SYSTEM = "你是需求登記整理員。依提供的對話與身分資料，以繁體中文整理已明確說出的需求。未回答的成績、收入或資格請標示未提供，不得推測。不要繼續問問題，也不要聲稱已送出或審核通過。只輸出兩個字串欄位的 JSON：mainRequest（50字內需求標題）、summary（300字內摘要）。不要輸出 reply 或 quickReplies；不要把助理提問當成使用者事實。"

@router.post("/assistant")
def converse(body: Request):
    if len(json.dumps(body.profile, ensure_ascii=False)) > 12000:
        raise HTTPException(422, "身分資料過長")
    if body.messages and body.messages[-1].role != "user":
        raise HTTPException(422, "最後一則訊息需為使用者回答")
    turn_count = sum(m.role == 'user' for m in body.messages)
    if turn_count > 9:
        raise HTTPException(422, '對話最多 9 輪，請重新開始。')
    latest = body.messages[-1].content if body.messages else ""
    explicit_summary = "整理需求登記" in latest
    summary_requested = explicit_summary or turn_count >= 9
    # 追問與選項完全由規劃器決定（依哪一題最能確認資格）；以前模型只寫一句承接語，而且一定會被追問覆蓋，
    # 卻要等模型 5～30 秒、模型忙碌時整段對話失敗。現在只有「整理需求登記」這一步用模型。
    provider = get_provider() if summary_requested else None
    if summary_requested and provider is None:
        raise HTTPException(503, "本地 AI 未啟用或指定模型尚未就緒，暫時無法整理需求登記。")
    try:
        context = guidance(body.guidance_profile or {}, "" if explicit_summary else latest, body.question_attribute)
    except PyMongoError:
        raise HTTPException(503, "補助資料庫暫時無法連線，無法根據候選條件縮小範圍，請重試。") from None
    question = context['question']
    if summary_requested:
        payload = json.dumps({**body.model_dump(), "guidance": context}, ensure_ascii=False)
        schema = Summary.model_json_schema()
        try:
            try:
                result = provider.complete_json(SUMMARY_SYSTEM, payload, json_schema=schema, max_tokens=1400)
            except LLMError as exc:
                # Older Ollama runners may reject JSON-schema grammar generation.
                # JSON mode still goes through the same strict response validation.
                if "failed to parse grammar" not in str(exc):
                    raise
                result = provider.complete_json(SUMMARY_SYSTEM, payload, max_tokens=1400)
            summary = Summary.model_validate(result)
            answer = Answer(reply="請確認以下需求摘要，尚未送出：\n" + summary.summary, quickReplies=[], summary=summary.summary, mainRequest=summary.mainRequest)
        except (LLMError, ValidationError, ValueError, KeyError):
            raise HTTPException(502, "AI 暫時無法產生有效回應，請重試。") from None
    elif question:
        # 規劃器只看使用者選的需求領域；說清楚範圍，免得和畫面上全部補助的數字對不起來
        reason = f"在您想找的補助中，有 {question['affected']} 筆需要這項資料才能判斷" if question.get('affected') else question['reason']
        reply = reason + "。\n" + question['question']
        labels = [o['label'] for o in question['options'] if o['label'] != '不確定']
        if len(labels) > 3:
            reply += "\n可回答：" + "、".join(labels) + "；也可以回答不確定。"
        answer = Answer(reply=reply, quickReplies=labels[:3] + ['不確定'])
    else:
        answer = Answer(reply="目前沒有仍可能符合的補助。可以回到「我的資料卡」調整條件，或到「訴求專區」說出您需要的服務。" if not context['candidate_count'] else "目前能問的條件都確認了，比對結果已更新在畫面上；其餘細節請以官方公告為準。")
    return {**answer.model_dump(), "search": context.get('search'), "model": provider.model if provider else "", "llm_used": provider is not None, "guidance_profile": context['profile'], "learned": learned_attributes(context['profile']), "question_attribute": question['attribute_id'] if question and not summary_requested else "", "candidate_count": context['candidate_count'], "turn_count": turn_count, "max_turns": 9, "completed": summary_requested}
