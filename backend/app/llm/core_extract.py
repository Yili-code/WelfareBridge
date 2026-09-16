"""本地 AI 抽取資格骨幹：輸出一律附原文引用，引用驗證不過的值丟棄；結果只是 core_builder 的其中一票。"""

from __future__ import annotations

import logging
import re

from ..config import get_settings
from ..registry import get_registry
from ..services.normalization import CITIES, normalize_city
from ..services.schema_validator import excerpt_in_text
from .factory import get_provider
from .prompts import render, split_system_user

log = logging.getLogger(__name__)

LEVELS = ["elementary", "junior_high", "senior_high", "vocational_high", "junior_college", "university", "master", "doctoral"]
OTHER_REQUIRED = {
    "employment.involuntary_separation=true": ("employment.involuntary_separation", True),
    "employment.status=unemployed": ("employment.status", "unemployed"),
    "employment.status=employed": ("employment.status", "employed"),
    "housing.tenure=rent": ("housing.tenure", "rent"),
    "care.needs_care=true": ("care.needs_care", True),
    "care.is_primary_caregiver=true": ("care.is_primary_caregiver", True),
    "applicant.gender=female": ("applicant.gender", "female"),
    "applicant.is_student=false": ("applicant.is_student", False),
}
OTHER_LABELS = {
    "employment.involuntary_separation=true": "非自願離職（就業保險）", "employment.status=unemployed": "目前失業／待業", "employment.status=employed": "目前受僱在職", "housing.tenure=rent": "租屋居住",
    "care.needs_care=true": "本人或受照顧者經評估需要長期照顧", "care.is_primary_caregiver=true": "家庭主要照顧者", "applicant.gender=female": "限女性", "applicant.is_student=false": "不得為在學學生",
}
QUOTED = {"type": "string"}
CORE_SCHEMA = {
    "type": "object",
    "properties": {
        "multiple_programs": {"type": "boolean"},
        "residence": {"type": "object", "properties": {"scope": {"type": "string", "enum": ["national", "local", "unknown"]}, "cities": {"type": "array", "items": {"type": "string"}}, "basis": {"type": "string", "enum": ["household", "current", "either", "school", "unknown"]}, "quote": QUOTED}, "required": ["scope", "cities", "basis", "quote"]},
        "age": {"type": "object", "properties": {"applies_to": {"type": "string", "enum": ["applicant", "child", "none"]}, "min": {"type": ["integer", "null"]}, "max": {"type": ["integer", "null"]}, "quote": QUOTED}, "required": ["applies_to", "min", "max", "quote"]},
        "education": {"type": "object", "properties": {"levels": {"type": "array", "items": {"type": "string", "enum": LEVELS}}, "applies_to": {"type": "string", "enum": ["applicant", "child"]}, "quote": QUOTED}, "required": ["levels", "applies_to", "quote"]},
        "identity_required": {"type": "array", "items": {"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}}, "quote": QUOTED}, "required": ["tags", "quote"]}},
        "identity_excluded": {"type": "array", "items": {"type": "object", "properties": {"tags": {"type": "array", "items": {"type": "string"}}, "quote": QUOTED}, "required": ["tags", "quote"]}},
        "nationality": {"type": "object", "properties": {"value": {"type": "string", "enum": ["roc", "foreign", "none"]}, "quote": QUOTED}, "required": ["value", "quote"]},
        "other_required": {"type": "array", "items": {"type": "object", "properties": {"attribute": {"type": "string", "enum": sorted(OTHER_REQUIRED)}, "quote": QUOTED}, "required": ["attribute", "quote"]}},
    },
    "required": ["multiple_programs", "residence", "age", "education", "identity_required", "identity_excluded", "nationality", "other_required"],
}
MAX_TEXT = 5000


def _prompt(record: dict) -> tuple[str, str]:
    registry = get_registry()
    tags = "; ".join(f"{tag.id}={tag.label}" for tag in registry.tags.values() if tag.id not in {"elderly", "yami"})
    attrs = "; ".join(f"{key}（{OTHER_LABELS[key]}）" for key in OTHER_REQUIRED)
    text = record.get("original_text") or ""
    prompt = render("eligibility_core", TAGS=tags, ATTRS=attrs, TITLE=record.get("title", ""), PROVIDER=record.get("provider", ""), REGION=record.get("provider_region") or "未知縣市", TEXT=text[:MAX_TEXT])
    return split_system_user(prompt)


def core_provider():
    settings = get_settings()
    return get_provider(settings.model_copy(update={"llm_model": settings.core_llm_model or settings.llm_model}))


def extract_raw(record: dict) -> dict | None:
    """呼叫本地 AI，回傳原始 JSON（存進 eligibility_core.llm，之後重算投票不必再跑模型）。"""
    provider = core_provider()
    if provider is None:
        return None
    system, user = _prompt(record)
    output = provider.complete_json(system, user, json_schema=CORE_SCHEMA, max_tokens=1500)  # 模型常把 JSON 排版成多行；700 會截斷
    output["_model"] = provider.model
    return output


def _age_in_quote(low: int | None, high: int | None, quote: str) -> bool:
    """年齡上下限的數字要真的出現在引用句（「未滿 2 歲」→ 上限 1；模型常把月數當歲數）。"""
    from ..services.normalization import chinese_to_int

    if "歲" not in quote:
        return False
    numbers = {int(n) for n in re.findall(r"\d{1,3}", quote)}
    numbers |= {v for v in (chinese_to_int(t) for t in re.findall(r"[一二三四五六七八九十]{1,3}(?=歲)", quote)) if v is not None}
    ok_low = low in (None, 0) or low in numbers
    ok_high = high is None or high in numbers or high + 1 in numbers
    return ok_low and ok_high


def _tag_aliases(registry, tag_id: str) -> list[str]:
    tag = registry.tags.get(tag_id)
    aliases = [a for a in ([tag.label, *tag.aliases] if tag else []) if len(a) >= 2]
    if tag_id in {"low_income", "middle_low_income"}:
        aliases += ["低收", "中低收"]
    if tag_id == "disabled":
        aliases += ["障礙"]
    return aliases


def proposals_from_llm(output: dict | None, record: dict) -> list[dict]:
    """把 AI 輸出轉成候選 facet；引用不在原文（含標題）裡的值一律丟棄。"""
    if not output:
        return []
    registry = get_registry()
    source_text = f"{record.get('title', '')}\n{record.get('provider', '')}\n{record.get('original_text') or ''}"
    region = normalize_city(record.get("provider_region") or "")
    proposals: list[dict] = []

    def quoted(item: dict | None) -> str:
        quote = str((item or {}).get("quote") or "").strip()
        return quote if quote and excerpt_in_text(quote, source_text) else ""

    residence = output.get("residence") or {}
    if residence.get("scope") == "local" and quoted(residence):
        cities = []
        for name in residence.get("cities") or []:
            city = region if str(name).strip() in {"本市", "本縣"} else normalize_city(str(name))
            if city in CITIES and city not in cities:
                cities.append(city)
        if cities:
            basis = residence.get("basis") if residence.get("basis") in {"household", "current", "either", "school"} else "household"
            proposals.append({"kind": "residence", "cities": cities, "basis": basis, "quote": quoted(residence)})
    elif residence.get("scope") == "national":
        proposals.append({"kind": "residence", "cities": [], "quote": quoted(residence)})

    age = output.get("age") or {}
    low, high = age.get("min"), age.get("max")
    if age.get("applies_to") in {"applicant", "child"} and (isinstance(low, int) or isinstance(high, int)) and quoted(age):
        low = low if isinstance(low, int) and 0 <= low <= 120 else None
        high = high if isinstance(high, int) and 0 <= high <= 120 else None
        if low == 0 and high is None or (high is not None and high >= 100):
            low = high = None  # 「0 歲以上」「100 歲以下」等於沒有年齡限制
        if (low is not None or high is not None) and (low is None or high is None or low <= high):
            proposals.append({"kind": "age", "min": low, "max": high, "via_child": age.get("applies_to") == "child", "quote": quoted(age), "verified_numbers": _age_in_quote(low, high, quoted(age))})

    education = output.get("education") or {}
    levels = [level for level in LEVELS if level in (education.get("levels") or [])]
    if levels and quoted(education):
        proposals.append({"kind": "education", "levels": levels, "via_child": education.get("applies_to") == "child", "quote": quoted(education)})

    for key, kind in (("identity_required", "identity_any"), ("identity_excluded", "identity_exclude")):
        for item in output.get(key) or []:
            tags = [t for t in dict.fromkeys(item.get("tags") or []) if t in registry.tags]
            if not tags or not quoted(item):
                continue
            # 引用句裡要真的提到這個身分（模型常引用「經醫師診斷有療育需求」卻填身心障礙）
            mentioned = [t for t in tags if t == "elderly" or any(alias in quoted(item) for alias in _tag_aliases(registry, t))]
            if not mentioned:
                continue
            tags = mentioned
            if "elderly" in tags:  # 老人是年齡條件
                if kind == "identity_any" and tags == ["elderly"]:
                    proposals.append({"kind": "age", "min": 65, "max": None, "via_child": False, "quote": quoted(item)})
                tags = [t for t in tags if t != "elderly"]
                if not tags:
                    continue
            proposals.append({"kind": kind, "tags": tags, "quote": quoted(item)})

    nationality = output.get("nationality") or {}
    if nationality.get("value") in {"roc", "foreign"} and quoted(nationality):
        proposals.append({"kind": "nationality", "value": nationality["value"], "quote": quoted(nationality)})

    for item in output.get("other_required") or []:
        mapped = OTHER_REQUIRED.get(str(item.get("attribute")))
        if mapped and quoted(item):
            proposals.append({"kind": "attr", "attribute_id": mapped[0], "value": mapped[1], "quote": quoted(item)})
    for proposal in proposals:
        proposal["source"] = "llm"
    return proposals
