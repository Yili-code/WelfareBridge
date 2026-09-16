"""使用者介面專用 API（/api/public/*）。

前台只需要「看得懂、該看到」的內容：名稱、類型、適用對象、金額、怎麼申請、官方連結、資格初步比對。
抽取證據、規則信心、分類依據、本地 AI 處理狀態、爬蟲資訊等作業欄位只留在 /api/benefits 與資料中心，
不送到使用者的瀏覽器。

    GET  /api/public/benefits        可申請的補助清單（卡片欄位）
    GET  /api/public/benefits/{id}   單筆補助詳情（詳情面板欄位）
    POST /api/public/match           依資料卡比對：每筆補助的比對狀態、原因、還缺哪些資料
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..config import get_settings
from ..db import get_db
from ..matching import MatchingEngine, Profile, hard_filter_candidates, load_records
from ..matching.eligibility_core import describe
from ..registry import get_registry
from ..schemas import DISCLAIMER
from .serializers import CHANNEL_LABELS

router = APIRouter(prefix="/api/public", tags=["public"])

# 與 matching.engine.load_records 相同的收錄範圍：媒合看得到的，清單才列出來
LISTED = {"record_kind": {"$ne": "portal"}, "classification.uncertain": {"$ne": True}, "is_canonical": True, "status": {"$ne": "expired"}}
CARD_PROJECTION = {"title": 1, "domain": 1, "category": 1, "category_label": 1, "provider": 1, "provider_region": 1, "benefit": 1, "eligibility_core.facets": 1, "source.source_url": 1, "source.published_date": 1, "updated_at": 1}
PERIOD_LABELS = {"month": "每月", "year": "每年", "semester": "每學期", "day": "每日", "once": "一次"}
FORM_LABELS = {"waiver": ("費用減免", "依規定減免"), "service": ("提供服務", "依評估核定"), "in_kind": ("提供實物／輔具", "依評估核定"), "voucher": ("提供補助額度", "依規定核定"), "loan": ("貸款協助", "依貸款條件"), "cash": ("提供補助", "金額依核定"), "mixed": ("提供補助", "依規定核定")}
AUDIENCE_TAGS = {
    "low_income": "低收／中低收", "middle_low_income": "低收／中低收", "economic_hardship": "經濟困難家庭", "disabled": "身心障礙者", "disabled_family": "身心障礙者家庭",
    "indigenous": "原住民", "single_parent": "單親／特境家庭", "special_circumstances": "單親／特境家庭", "new_immigrant": "新住民", "elderly": "長者",
    "veteran_family": "榮民與遺族", "military_civil_bereaved": "榮民與遺族", "orphan": "兒童及少年", "dementia": "失智症者",
}
AUDIENCE_ATTRS = {("employment.status", "unemployed"): "求職／失業者", ("employment.involuntary_separation", True): "求職／失業者", ("housing.tenure", "rent"): "租屋族", ("care.needs_care", True): "需要照顧者", ("care.is_primary_caregiver", True): "家庭照顧者"}
NUMBERING_RE = re.compile(r"^\s*(?:[（(][一二三四五六七八九十0-9]{1,3}[)）]|[一二三四五六七八九十]{1,3}、|[0-9]{1,2}\s*[.、．])\s*")
THRESHOLD_AMOUNT_RE = re.compile(r"(基本工資|最低生活費|平均分配|家庭總收入|所得|動產|不動產|存款|財產)")
MEANINGLESS_ATTACHMENT_RE = re.compile(r"^[\s\[\(【（]*(?:pdf|odt|docx?|ods|xlsx?|csv|檔案|附件|下載|點此|請點此下載參閱)[\s\]\)】）檔案下載參閱]*$", re.I)


# ============================================================ 顯示用小工具
def _money(value: float | int) -> str:
    number = int(round(float(value)))
    if number >= 10000 and number % 10000 == 0:
        return f"{number // 10000:,} 萬元"
    return f"{number:,} 元"


def _money_range(low: float, high: float) -> str:
    low, high = int(round(float(low))), int(round(float(high)))
    if low == high:
        return _money(low)
    if low >= 10000 and low % 10000 == 0 and high % 10000 == 0:
        return f"{low // 10000:,}～{high // 10000:,} 萬元"
    return f"{low:,}～{high:,} 元"


def _roc(date: str) -> str:
    match = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", date or "")
    return f"{int(match.group(1)) - 1911} 年 {int(match.group(2))} 月 {int(match.group(3))} 日" if match else ""


def _region(row: dict) -> str:
    region = row.get("provider_region") or ""
    return "全國" if region in {"", "national"} else region


def _short(text: str, limit: int) -> str:
    text = NUMBERING_RE.sub("", re.sub(r"\s+", " ", text or "")).strip(" ；;，,。")
    return text if len(text) <= limit else text[:limit] + "…"


def price(benefit: dict) -> dict | None:
    """卡片右側與詳情的金額方塊。範圍差距太大（多半混進門檻或年度總額）時不硬寫數字。"""
    amount = benefit.get("amount") or {}
    per = PERIOD_LABELS.get(amount.get("period") or "", "")
    value, low, high = amount.get("value"), amount.get("min"), amount.get("max")
    form = benefit.get("benefit_form") or ""
    # 金額出處是基本工資、最低生活費、所得或財產門檻時，那個數字不是補助金額
    threshold_like = bool(THRESHOLD_AMOUNT_RE.search(amount.get("description") or ""))
    if form != "loan" and not threshold_like:
        if value:
            return {"type": "amount", "unit": f"{per}補助" if per and per != "一次" else "補助金額", "amount": _money(value), "note": ""}
        if low and high and float(high) / float(low) <= 20:
            return {"type": "amount", "unit": f"{per}補助" if per and per != "一次" else "補助金額", "amount": _money_range(low, high), "note": "" if low == high else "依身分或資格不同"}
        if high and not low:
            return {"type": "amount", "unit": f"{per}最高" if per and per != "一次" else "最高", "amount": _money(high), "note": ""}
    label, note = FORM_LABELS.get(form, ("", ""))
    if not label:
        return None
    return {"type": "soft", "unit": label, "amount": note, "note": ""}


def period_label(benefit: dict) -> str:
    period = benefit.get("application_period") or {}
    if period.get("rolling"):
        return "隨時可以申請"
    if period.get("end_date"):
        start = _roc(period.get("start_date") or "")
        end = _roc(period["end_date"])
        return f"{start}起至{end}止" if start and start != end else f"申請截止：{end}"
    if period.get("by_school_deadline"):
        return "依各校公告的截止日期"
    return ""


def audiences(facets: list[dict]) -> list[str]:
    out: list[str] = []

    def add(label: str) -> None:
        if label and label not in out:
            out.append(label)

    for facet in facets:
        kind = facet.get("kind")
        if kind == "age":
            if facet.get("via_child"):
                add("育兒家庭")
            elif (facet.get("min") or 0) >= 55:
                add("長者")
            elif facet.get("max") is not None and facet["max"] <= 18:
                add("兒童及少年")
            elif facet.get("max") is not None and facet["max"] <= 45 and (facet.get("min") or 0) >= 15:
                add("青年")
        elif kind in {"education", "student"}:
            add("育兒家庭" if facet.get("via_child") else "學生")
        elif kind == "identity_any":
            for tag in facet.get("tags") or []:
                add(AUDIENCE_TAGS.get(tag, ""))
        elif kind == "attr":
            add(AUDIENCE_ATTRS.get((facet.get("attribute_id"), facet.get("value")), ""))
    return out or ["一般民眾"]


def who_text(facets: list[dict]) -> str:
    parts = [describe(f) for f in facets if f.get("kind") not in {"residence", "identity_exclude", "nationality"}]
    parts = [p for p in dict.fromkeys(parts) if p]
    return "、".join(parts[:3]) + (" 等" if len(parts) > 3 else "")


def card(row: dict) -> dict:
    benefit = row.get("benefit") or {}
    facets = (row.get("eligibility_core") or {}).get("facets") or []
    registry = get_registry()
    points: list[str] = []
    who = who_text(facets)
    if who:
        points.append(f"對象：{who}")
    residence = next((f for f in facets if f.get("kind") == "residence" and f.get("cities")), None)
    if residence:
        points.append(f"地區：{describe(residence)}")
    content = _short((benefit.get("amount") or {}).get("description") or "", 34)
    if content:
        points.append(content)
    when = period_label(benefit)
    channel = CHANNEL_LABELS.get((benefit.get("application") or {}).get("channel") or "unknown", "")
    apply = "、".join(p for p in (when, channel if channel != "未載明" else "") if p)
    if apply:
        points.append(f"申請：{apply}")
    source = row.get("source") or {}
    return {
        "id": row["_id"],
        "title": row.get("title", ""),
        "domain_id": row.get("domain", ""),
        "domain": registry.domain_label(row.get("domain", "")) if row.get("domain") else "其他",
        "service_type": row.get("category_label") or registry.category_label(row.get("category", "")) or "其他福利",
        "audiences": audiences(facets),
        "region": _region(row),
        "agency": row.get("provider", ""),
        "points": points[:4],
        "price": price(benefit),
        "updated": (source.get("published_date") or "")[:10],  # 官方公告日期；系統重新處理的時間不是官方更新
    }


# ============================================================ 清單與詳情
@router.get("/benefits")
def public_benefits() -> dict:
    rows = get_db().benefits.find(LISTED, CARD_PROJECTION).sort("title", 1)
    items = [card(row) for row in rows]
    return {"items": items, "total": len(items), "disclaimer": DISCLAIMER, "generated_at": datetime.now(timezone.utc).isoformat()}


def _attachments(row: dict, db) -> list[dict]:
    doc = db.raw_documents.find_one({"_id": row.get("raw_document_id")}, {"attachments": 1}) or {}
    out, seen = [], set()
    for index, attachment in enumerate(row.get("attachments") or doc.get("attachments") or [], 1):
        url = attachment.get("url") or ""
        if not url or url in seen:
            continue
        seen.add(url)
        name = re.sub(r"\s*\(\s*[\d.]+\s*[KMG]?B\s*\)\s*$", "", (attachment.get("name") or "").replace("\n", " ")).strip()
        name = re.sub(r"^(?:下載|檔案下載|附件)\s*[:：]?\s*", "", name)
        if not name or len(name) <= 2 or MEANINGLESS_ATTACHMENT_RE.match(name):
            name = f"附件 {index}"
        out.append({"name": name, "url": url, "type": (attachment.get("type") or "").upper()})
    return out[:12]


CLAUSE_START_RE = re.compile(r"^\s*(?:第[一二三四五六七八九十百0-9]+條|[（(][一二三四五六七八九十0-9]{1,3}[)）]|[一二三四五六七八九十]{1,3}、|[0-9]{1,2}\s*[.、．])")
DOCUMENT_RE = re.compile(r"(證|表|影本|正本|書|謄本|存摺|照片|證明|文件|卡|單據|收據|清冊|帳戶|診斷|名冊|計畫)")


def _sentences(lines: list[str], limit: int) -> list[str]:
    """PDF 轉出的條文會在行尾斷開（「二、未接受機構收容安置、未」＋「領有政府提供之…」）：接回完整的一條再顯示。"""
    out: list[str] = []
    buffer = ""
    for line in (re.sub(r"\s+", " ", x).strip() for x in lines if x and x.strip()):
        if buffer and (CLAUSE_START_RE.match(line) or re.search(r"[。；;：:！？]$", buffer)):
            out.append(buffer)
            buffer = ""
        buffer = f"{buffer}{line}" if buffer else line
    if buffer:
        out.append(buffer)
    return [s for s in dict.fromkeys(out) if len(s) >= 6][:limit]


@router.get("/benefits/{benefit_id}")
def public_benefit(benefit_id: str) -> dict:
    db = get_db()
    row = db.benefits.find_one({"_id": benefit_id})
    if row is None or row.get("record_kind") == "portal":
        raise HTTPException(status_code=404, detail="找不到這項補助，可能已下架或截止。")
    benefit = row.get("benefit") or {}
    application = benefit.get("application") or {}
    facets = (row.get("eligibility_core") or {}).get("facets") or []
    conditions = row.get("conditions") or []
    main = [describe(f) for f in facets if f.get("kind") != "identity_exclude"]
    excluded = [describe(f) for f in facets if f.get("kind") == "identity_exclude"]
    official = _sentences([c.get("text", "") for c in conditions if c.get("role") in {None, "required"}], 12)
    not_for = _sentences([c.get("text", "") for c in conditions if c.get("role") == "exclusion"], 4)
    contact = application.get("contact") or {}
    documents = [_short(d, 120) for d in application.get("documents") or [] if d and DOCUMENT_RE.search(d) and len(d) <= 160]
    amount_text = (benefit.get("amount") or {}).get("description") or ""
    source = row.get("source") or {}
    return {
        **card({**row, "eligibility_core": {"facets": facets}}),
        "eligibility": {"main": list(dict.fromkeys(main)), "excluded": list(dict.fromkeys(excluded)) + not_for, "official": official, "summary": benefit.get("target_population_text") or ""},
        "content": [_short(amount_text, 400)] if amount_text.strip() else [],
        "application": {"period": period_label(benefit), "channel": CHANNEL_LABELS.get(application.get("channel") or "unknown", ""), "method": application.get("method") or "", "documents": documents[:10],
                        "contact": {k: v for k, v in {"department": contact.get("department"), "phone": contact.get("phone"), "email": contact.get("email")}.items() if v}},
        "attachments": _attachments(row, db),
        "source_url": source.get("source_url", ""),
    }


# ============================================================ 資格比對
class MatchBody(BaseModel):
    profile: dict = Field(default_factory=dict)


def reasons(item) -> list[dict]:
    """把資格骨幹逐項判斷轉成使用者看得懂的原因；不確定是否不符的，明講要向承辦單位確認。"""
    if not item.core:
        return [{"state": "unknown", "text": "官方公告沒有能自動比對的資格條件，請查看官方頁面或洽詢承辦單位"}]
    order = {"violated": 0, "unknown": 1, "satisfied": 2}
    out = []
    for result in sorted(item.core, key=lambda r: order.get(r.get("state"), 3)):
        state, text = result.get("state"), result.get("reason", "")
        if not text or text.startswith("未支援的"):
            continue  # 系統還不會判斷的條件種類：不把內部訊息顯示給使用者
        if state == "satisfied":
            text = text.removeprefix("符合").removeprefix("：")  # 打勾圖示已經表示符合
        if state == "violated" and result.get("status") != "confirmed":
            out.append({"state": "unsure", "text": f"{text}（公告寫法不完全明確，請向承辦單位確認）"})
        elif text:
            out.append({"state": state, "text": text})
    return out


@router.post("/match")
def public_match(body: MatchBody) -> dict:
    registry = get_registry()
    settings = get_settings()
    profile = Profile.from_dict(body.profile, registry)
    records = load_records(get_db())
    candidates, excluded = hard_filter_candidates(records, profile, registry, settings)
    engine = MatchingEngine(settings=settings, registry=registry)
    items = engine.match_all(candidates, profile) + [engine.match_one(record, profile) for record in excluded]
    results: dict[str, dict] = {}
    counts = {"yes": 0, "maybe": 0, "no": 0}
    for item in items:
        status = {"tier1": "yes", "tier2": "maybe"}.get(item.tier, "no")
        counts[status] += 1
        results[item.benefit_id] = {"status": status, "reasons": reasons(item), "needs": item.needs_labels[:4]}
    return {"results": results, "counts": counts, "disclaimer": DISCLAIMER}
