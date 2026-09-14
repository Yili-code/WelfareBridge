"""本地 AI 補齊（v2）：規則式抽取後的空缺由 Ollama 填入，每個值都要有原文摘錄且通過驗證。

四個任務：
    classify_document      分類器不確定時判斷是否為補助與類別（只能選候選）
    fill_benefit_meta      給付特徵空缺欄位
    map_conditions         對不到屬性的條件句 → 候選屬性 + operator / value
    judge_complex          媒合時的複雜條件判斷（只能 match / not_match / unknown）
    parse_profile          使用者描述 → 屬性值（補充規則式）
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

from ..registry import get_registry
from ..services.normalization import CITIES, find_cities, normalize_city, number_is_counted
from ..services.extractor import is_real_condition, placeholder_attribute

BUDGET_SCALE_RE = re.compile(r"[0-9０-９,，一二三四五六七八九十百千]+\s*億")  # 「4,000億元」是預算總額，不是個人給付
# 幣別字樣（給其他檢查用）；金額是否為量詞改用 number_is_counted 判斷
CURRENCY_RE = re.compile(r"[元圓]|新臺幣|新台幣|NT\$|NTD")
from ..services.schema_validator import DATE_RE, excerpt_in_text, number_in_excerpt
from .factory import get_provider
from .prompts import render, split_system_user

log = logging.getLogger(__name__)

CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {"is_benefit": {"type": "boolean"}, "page_kind": {"type": "string", "enum": ["program", "portal", "form", "attachment", "progress_query", "flowchart", "logo", "statistics", "faq", "directory", "notice", "other"]}, "category": {"type": "string"}, "category_label": {"type": "string"}, "confidence": {"type": "number"}, "reason": {"type": "string"}},
    "required": ["is_benefit", "page_kind", "category", "category_label", "confidence", "reason"],
}
PAGE_KINDS = {"program", "portal", "form", "attachment", "progress_query", "flowchart", "logo", "statistics", "faq", "directory", "notice", "other"}
CONDITION_SCHEMA = {
    "type": "object",
    "properties": {
        "attribute_id": {"type": ["string", "null"]}, "operator": {"type": "string"}, "value": {}, "role": {"type": "string"}, "human_readable": {"type": "string"},
        "confidence": {"type": "number"}, "excerpt": {"type": "string"}, "proposed_attribute": {"type": ["object", "null"]},
    },
    "required": ["attribute_id", "operator", "value", "role", "human_readable", "confidence", "excerpt"],
}
VERDICT_SCHEMA = {
    "type": "object",
    "properties": {"result": {"type": "string", "enum": ["match", "not_match", "unknown"]}, "confidence": {"type": "number"}, "reason": {"type": "string"}, "missing_information": {"type": "array", "items": {"type": "string"}}, "source_text": {"type": "string"}},
    "required": ["result", "confidence", "reason", "missing_information", "source_text"],
}
PROFILE_SCHEMA = {
    "type": "object",
    "properties": {"attributes": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "string"}, "value": {}, "excerpt": {"type": "string"}, "confidence": {"type": "number"}}, "required": ["id", "value", "excerpt"]}}, "need_type": {"type": "string"}, "need_excerpt": {"type": "string"}},
    "required": ["attributes", "need_type"],
}
META_FIELDS = ["benefit_form", "award_basis", "quota", "amount", "application_period", "channel", "obligations", "exclusive_with", "renewable", "target_population_text", "provider"]
BENEFIT_FORMS = {"cash", "waiver", "service", "in_kind", "voucher", "loan", "mixed"}
AWARD_BASIS = {"criteria", "competitive", "lottery", "first_come", "unknown"}
CHANNELS = {"school", "agency", "online", "mail", "unknown"}
EXCLUSIVE = {"public_funding", "government_benefit", "same_provider", "same_category", "any_other", "none"}
MAX_TEXT = 9000


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def llm_available() -> bool:
    return get_provider() is not None


def _clip(text: str, limit: int = MAX_TEXT) -> str:
    return text if len(text) <= limit else text[:limit]


# ------------------------------------------------------------ classification
def classify_document(title: str, text: str, candidates: list[str]) -> dict | None:
    provider = get_provider()
    if provider is None:
        return None
    registry = get_registry()
    # 給完整類別清單（關鍵字候選只是提示），避免模型被迫在錯的候選裡挑一個
    lines = []
    candidate_set = set(candidates or [])
    for leaf in registry.leaves():
        hint = "（關鍵字候選）" if leaf.id in candidate_set else ""
        lines.append(f"- {leaf.id}：{leaf.label}{hint}。{leaf.description}")
    prompt = render("classify_benefit", TITLE=title, CANDIDATES="\n".join(lines), TEXT=_clip(text, 4000))
    system, user = split_system_user(prompt)
    output = provider.complete_json(system, user, json_schema=CLASSIFY_SCHEMA, max_tokens=300)
    category = str(output.get("category") or "").strip()
    label = str(output.get("category_label") or "").strip()
    if category and registry.category(category) is None:
        category = ""
    # 小模型常把 id 與名稱配錯（id 寫 youth_employment、名稱寫「就業促進津貼」）：id 與名稱不一致時以名稱反查；查不到就不改類別
    if label:
        by_label = next((leaf.id for leaf in registry.leaves() if leaf.label == label), "")
        if by_label and by_label != category:
            category = by_label  # 名稱在清單裡：以名稱為準（id 常被小模型寫錯）
        # 名稱不在清單裡但 id 合法：保留 id（不能因為名稱寫錯就把整筆判成不是補助）
    page_kind = str(output.get("page_kind") or "program").strip().lower()
    if page_kind not in PAGE_KINDS:
        page_kind = "program"
    # 是不是補助只看 is_benefit 與頁面類型；類別對不上（category 空）時由呼叫端沿用關鍵字類別
    is_benefit = bool(output.get("is_benefit")) and page_kind in {"program", "portal"}
    return {"is_benefit": is_benefit, "page_kind": page_kind, "category": category, "confidence": float(output.get("confidence", 0.5)), "reason": str(output.get("reason", ""))[:200], "model": provider.model}


# ------------------------------------------------------------- eligibility sentences（規則式一句都沒抓到時）
ELIGIBILITY_SCHEMA = {
    "type": "object",
    "properties": {"sentences": {"type": "array", "items": {"type": "object", "properties": {"excerpt": {"type": "string"}, "role": {"type": "string", "enum": ["required", "exclusion"]}}, "required": ["excerpt", "role"]}}},
    "required": ["sentences"],
}


def extract_eligibility_sentences(benefit: dict, *, max_sentences: int = 8) -> dict:
    """規則式沒抓到任何條件句時：請本地 AI 從原文「逐字」列出資格句；每句逐段驗證存在於原文，通過的才進 conditions（status=unmapped）。"""
    provider = get_provider()
    text = benefit.get("original_text") or ""
    report = {"model": provider.model if provider else "", "accepted": [], "rejected": [], "sentences": []}
    if provider is None or not text.strip():
        return report
    prompt = render("eligibility_sentences", TITLE=benefit.get("title", ""), TEXT=_clip(text, 5000), MAX=str(max_sentences))
    system, user = split_system_user(prompt)
    output = provider.complete_json(system, user, json_schema=ELIGIBILITY_SCHEMA, max_tokens=900)
    seen = set()
    for item in (output.get("sentences") or [])[:max_sentences]:
        excerpt = str(item.get("excerpt") or "").strip()
        role = item.get("role") if item.get("role") in {"required", "exclusion"} else "required"
        if not excerpt or excerpt in seen:
            continue
        seen.add(excerpt)
        if len(excerpt) < 6 or not excerpt_in_text(excerpt, text):
            report["rejected"].append({"task": "eligibility_sentences", "excerpt": excerpt[:120], "reason": "摘錄不在原文（不接受改寫）"})
            continue
        report["accepted"].append({"task": "eligibility_sentences", "field": "conditions", "value": role, "excerpt": excerpt[:200], "confidence": 0.7})
        report["sentences"].append({"text": excerpt[:200], "excerpt": excerpt[:200], "role": role, "status": "unmapped", "attribute_id": None, "candidates": [], "method": "llm_sentence"})
    return report


# ------------------------------------------------------------- benefit meta
def _missing_meta_fields(benefit: dict) -> list[str]:
    meta = benefit.get("benefit") or {}
    missing: list[str] = []
    if meta.get("benefit_form_inferred"):
        missing.append("benefit_form")
    if meta.get("award_basis") in {None, "", "unknown"}:
        missing.append("award_basis")
    if meta.get("quota") is None:
        missing.append("quota")
    amount = meta.get("amount") or {}
    if amount.get("value") is None and amount.get("min") is None:
        missing.append("amount")
    period = meta.get("application_period") or {}
    if not period.get("end_date") and not period.get("rolling"):
        missing.append("application_period")
    if (meta.get("application") or {}).get("channel") in {None, "", "unknown"}:
        missing.append("channel")
    if not meta.get("obligations"):
        missing.append("obligations")
    if meta.get("exclusive_with") in (None, [], ["none"]):
        missing.append("exclusive_with")
    if meta.get("renewable") is None:
        missing.append("renewable")
    missing.append("target_population_text")
    if not benefit.get("provider"):
        missing.append("provider")
    return missing


def fill_benefit_meta(benefit: dict) -> dict:
    """回傳 report {accepted: [...], rejected: [...], model}; 直接修改 benefit。"""
    provider = get_provider()
    report: dict = {"accepted": [], "rejected": [], "model": provider.model if provider else "", "task": "benefit_meta"}
    if provider is None:
        return report
    text = benefit.get("original_text", "")
    fields = _missing_meta_fields(benefit)
    prompt = render("benefit_meta", TITLE=benefit.get("title", ""), CATEGORY=benefit.get("category_label") or benefit.get("category", ""), FIELDS="、".join(fields), TEXT=_clip(text))
    system, user = split_system_user(prompt)
    output = provider.complete_json(system, user, max_tokens=1200)
    meta = benefit.setdefault("benefit", {})
    evidence: list[dict] = benefit.setdefault("evidence", [])

    def supported(excerpt: Any) -> bool:
        return isinstance(excerpt, str) and bool(excerpt.strip()) and excerpt_in_text(excerpt, text)

    def accept(field_name: str, value: Any, excerpt: str, confidence: float = 0.7) -> None:
        report["accepted"].append({"field": field_name, "value": value, "excerpt": excerpt[:120]})
        evidence.append({"field": f"benefit.{field_name}" if field_name != "provider" else "provider", "value": value, "excerpt": excerpt[:200], "extractor": "llm", "confidence": confidence, "inferred": False, "inference_basis": ""})

    def reject(field_name: str, reason: str) -> None:
        report["rejected"].append({"field": field_name, "reason": reason})

    if "benefit_form" in fields and output.get("benefit_form"):
        value, excerpt = output.get("benefit_form"), output.get("benefit_form_excerpt") or ""
        if value in BENEFIT_FORMS and supported(excerpt):
            meta["benefit_form"], meta["benefit_form_inferred"] = value, False
            accept("benefit_form", value, excerpt)
        else:
            reject("benefit_form", "值不合法或摘錄不在原文")
    if "award_basis" in fields and output.get("award_basis"):
        value, excerpt = output.get("award_basis"), output.get("award_basis_excerpt") or ""
        if value in AWARD_BASIS and value != "unknown" and supported(excerpt):
            meta["award_basis"] = value
            accept("award_basis", value, excerpt)
        elif value:
            reject("award_basis", "值不合法或摘錄不在原文")
    if "quota" in fields and output.get("quota") is not None:
        value, excerpt = output.get("quota"), output.get("quota_excerpt") or ""
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0 and supported(excerpt) and number_in_excerpt(int(value), excerpt):
            meta["quota"] = int(value)
            accept("quota", int(value), excerpt, 0.8)
        else:
            reject("quota", "數值未出現在摘錄或摘錄不在原文")
    if "amount" in fields and isinstance(output.get("amount"), dict):
        amt, excerpt = output["amount"], output.get("amount_excerpt") or ""
        numbers = [v for v in (amt.get("value"), amt.get("min"), amt.get("max")) if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0]
        if numbers and supported(excerpt) and not any(number_is_counted(v, excerpt) for v in numbers) and all(number_in_excerpt(v, excerpt) for v in numbers) and not BUDGET_SCALE_RE.search(excerpt) and max(numbers) < 100_000_000:
            period = amt.get("period") if amt.get("period") in {"once", "month", "semester", "year"} else "unknown"
            count = {"once": 1, "month": 12, "semester": 2, "year": 1}.get(period)
            new_amount = {"type": amt.get("type") if amt.get("type") in {"fixed", "range", "tiered"} else ("fixed" if amt.get("value") else "range"), "value": float(amt["value"]) if isinstance(amt.get("value"), (int, float)) else None,
                          "min": float(amt.get("min") or amt.get("value") or min(numbers)), "max": float(amt.get("max") or amt.get("value") or max(numbers)), "unit": "TWD", "period": period, "count_per_year": count, "description": excerpt[:200], "tiers": []}
            meta["amount"] = new_amount
            base = new_amount["value"] if new_amount["value"] is not None else (new_amount["min"] + new_amount["max"]) / 2
            meta["amount_annualized"] = base * count if count else base
            accept("amount", {k: new_amount[k] for k in ("type", "value", "min", "max", "period")}, excerpt, 0.75)
        else:
            reject("amount", "數值未出現在摘錄、摘錄不在原文，或數字後面接的是量詞不是金額")
    if "application_period" in fields and isinstance(output.get("application_period"), dict):
        per, excerpt = output["application_period"], output.get("application_period_excerpt") or ""
        start, end = str(per.get("start_date") or ""), str(per.get("end_date") or "")
        rolling = bool(per.get("rolling"))
        if supported(excerpt) and ((end and DATE_RE.match(end)) or rolling):
            if end and DATE_RE.match(end) and end[:4] not in excerpt and str(int(end[:4]) - 1911) not in excerpt.replace(" ", ""):
                reject("application_period", "年份未出現在摘錄")
            else:
                meta["application_period"] = {**(meta.get("application_period") or {}), "start_date": start if DATE_RE.match(start) else "", "end_date": end if DATE_RE.match(end) else "", "rolling": rolling, "description": excerpt[:200]}
                accept("application_period", {"start_date": start, "end_date": end, "rolling": rolling}, excerpt, 0.75)
        elif end or rolling:
            reject("application_period", "日期格式錯誤或摘錄不在原文")
    if "channel" in fields and output.get("channel"):
        value, excerpt = output.get("channel"), output.get("channel_excerpt") or ""
        if value in CHANNELS and value != "unknown" and supported(excerpt):
            meta.setdefault("application", {})["channel"] = value
            accept("application.channel", value, excerpt)
        else:
            reject("channel", "值不合法或摘錄不在原文")
    if "obligations" in fields and isinstance(output.get("obligations"), list):
        # 義務條款會被當成原文規定顯示 → 只收原文逐字：AI 的改寫若不是逐字，就改存它引用的原文摘錄
        kept = []
        for item in output["obligations"]:
            if not isinstance(item, dict):
                continue
            proposed, excerpt = (item.get("text") or "").strip(), (item.get("excerpt") or "").strip()
            if not proposed or not supported(excerpt):
                continue
            kept.append(proposed if excerpt_in_text(proposed, text) else excerpt[:200])
        if kept:
            meta["obligations"] = kept[:5]
            accept("obligations", kept[:5], output["obligations"][0].get("excerpt", ""))
        elif output["obligations"]:
            reject("obligations", "摘錄不在原文")
    if "exclusive_with" in fields and isinstance(output.get("exclusive_with"), list) and output["exclusive_with"]:
        values = [v for v in output["exclusive_with"] if v in EXCLUSIVE and v != "none"]
        excerpt = output.get("exclusive_with_excerpt") or ""
        if values and supported(excerpt):
            meta["exclusive_with"] = values
            accept("exclusive_with", values, excerpt)
        elif values:
            reject("exclusive_with", "摘錄不在原文")
    if "renewable" in fields and isinstance(output.get("renewable"), bool):
        excerpt = output.get("renewable_excerpt") or ""
        if supported(excerpt):
            meta["renewable"] = output["renewable"]
            accept("renewable", output["renewable"], excerpt)
        else:
            reject("renewable", "摘錄不在原文")
    if output.get("target_population_text"):
        excerpt = output.get("target_population_excerpt") or ""
        value = str(output["target_population_text"])[:200]
        if supported(excerpt):
            meta["target_population_text"] = value
            accept("target_population_text", value, excerpt, 0.6)
        else:
            reject("target_population_text", "摘錄不在原文")
    if "provider" in fields and output.get("provider"):
        value, excerpt = str(output["provider"])[:120], output.get("provider_excerpt") or ""
        if supported(excerpt) and value in text:
            benefit["provider"] = value
            from ..services.extractor import classify_provider

            benefit["provider_type"] = classify_provider(value, benefit.get("provider_type", "unknown"))
            accept("provider", value, excerpt, 0.8)
        else:
            reject("provider", "機關名稱不在原文")
    return report


# --------------------------------------------------------- condition mapping
def _candidate_lines(candidate_ids: list[str]) -> str:
    registry = get_registry()
    lines = []
    for attribute_id in candidate_ids:
        attribute = registry.get(attribute_id)
        if attribute is None:
            continue
        values = ""
        if attribute.type in {"enum", "multi_enum"}:
            values = "；允許值：" + " | ".join(f"{v.get('value')}（{v.get('label')}）" for v in attribute.values[:16])
        unit = f"；單位：{attribute.unit}" if attribute.unit else ""
        lines.append(f"- {attribute.id}：{attribute.label}，型態 {attribute.type}{'（有序）' if attribute.ordered else ''}{unit}{values}")
    return "\n".join(lines)


TRUE_WORDS = {"true", "yes", "是", "有", "需要", "具備", "具有", "符合", "已", "y", "1"}
FALSE_WORDS = {"false", "no", "否", "無", "沒有", "不", "不需要", "未", "不具", "n", "0"}


def _number_from(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace(",", "").replace("，", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            pass
        from ..services.normalization import chinese_to_int, fullwidth_to_halfwidth

        match = re.search(r"[0-9]+(?:\.[0-9]+)?", fullwidth_to_halfwidth(cleaned))
        if match:
            number = float(match.group(0))
            if "萬" in cleaned:
                number *= 10000
            if "年" in cleaned and "月" not in cleaned and "歲" not in cleaned:
                number *= 12  # 年 → 月（只用於月數屬性；其他屬性的年份數字不會帶「年」字）
            return number
        run = re.search(r"[一二三四五六七八九十百千萬零〇兩]+", cleaned)
        parsed = chinese_to_int(run.group(0)) if run else None
        if parsed is None:
            return None
        number = float(parsed)
        if "年" in cleaned and "月" not in cleaned and "歲" not in cleaned:
            number *= 12
        return number
    return None


def normalize_operator(attribute, operator: str, value: Any) -> str:
    """7B 模型常把布林寫成 in／contains、把單值 enum 寫成 =：轉成該型態允許的 operator。"""
    operator = (operator or "").strip()
    if attribute.type == "boolean" and operator in {"in", "contains", "exists", "==", "is"}:
        return "="
    if attribute.type == "multi_enum" and operator in {"=", "==", "contains"}:
        return "contains" if not isinstance(value, list) or len(value) == 1 else "in"
    if attribute.type in {"enum", "city"} and operator in {"=", "=="} and isinstance(value, list):
        return "in"
    if attribute.type in {"enum", "city"} and operator == "contains":
        return "in"
    if attribute.type == "number" and operator == "==":
        return "="
    if operator == "≥":
        return ">="
    if operator == "≤":
        return "<="
    return operator


def _coerce_value(attribute, operator: str, value: Any) -> Any:
    if attribute.type == "number":
        if operator == "between":
            if isinstance(value, list) and len(value) == 2:
                low, high = _number_from(value[0]), _number_from(value[1])
                return [low, high] if low is not None and high is not None else None
            return None
        if isinstance(value, list) and value:
            value = value[0]
        number = _number_from(value)
        if number is not None and attribute.unit == "months" and isinstance(value, str) and "年" in value and "月" not in value:
            return number  # 已在 _number_from 轉成月
        return number
    if attribute.type == "boolean":
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, list) and value:
            value = value[0]
        if isinstance(value, str):
            token = value.strip().lower()
            if token in TRUE_WORDS:
                return True
            if token in FALSE_WORDS or token.startswith(("未", "不", "無", "非", "沒")):
                return False
            if token:
                return True  # 模型常直接回覆身分／狀態名稱（例如「單親家長」）：屬性已選定，視為具備
        return None
    if attribute.type in {"enum", "multi_enum"}:
        values = value if isinstance(value, list) else re.split(r"[、,，/／|]+", str(value))
        values = [str(v).strip(" 「」『』\"") for v in values if str(v).strip()]
        allowed = set(attribute.value_list)
        labels = {str(v.get("label")): str(v.get("value")) for v in attribute.values}
        out = []
        for v in values:
            key = str(v)
            if key in allowed:
                out.append(key)
            elif key in labels:
                out.append(labels[key])
        if not out:
            return None
        if operator in {"in", "not_in"}:
            return out
        return out[0]
    if attribute.type == "city":
        values = value if isinstance(value, list) else re.split(r"[、,，/／ ]+", str(value))
        cities = [normalize_city(str(v)) for v in values if str(v).strip()]
        cities = [c for c in cities if c in CITIES]
        if not cities:
            return None
        return cities if operator in {"in", "not_in"} else cities[0]
    return value


def map_conditions(benefit: dict, unmapped: list[dict], *, max_conditions: int = 12) -> dict:
    """對每個 unmapped 條件句呼叫一次本地 AI；驗證後加入 benefit["rules"]，回傳 report。"""
    provider = get_provider()
    registry = get_registry()
    report: dict = {"task": "condition_mapping", "model": provider.model if provider else "", "accepted": [], "rejected": [], "proposed_attributes": []}
    if provider is None or not unmapped:
        return report
    text = benefit.get("original_text", "")
    rules: list[dict] = benefit.setdefault("rules", [])
    for condition in unmapped[:max_conditions]:
        candidates = list(condition.get("candidates") or [])
        if not candidates:
            hits = registry.attributes_in_text(condition.get("text", ""))
            candidates = list(hits.keys())[:5]
        if not candidates:
            domain = benefit.get("domain") or ""
            candidates = [a.id for a in registry.for_domains([domain] if domain else None) if a.hard_filter][:6]
        sentence = condition.get("text", "")
        index = text.find(sentence[:40])
        context = text[max(0, index - 300) : index + 500] if index >= 0 else text[:800]
        prompt = render("condition_mapping", TITLE=benefit.get("title", ""), CANDIDATES=_candidate_lines(candidates), SENTENCE=sentence, CONTEXT=context)
        system, user = split_system_user(prompt)
        try:
            output = provider.complete_json(system, user, json_schema=CONDITION_SCHEMA, max_tokens=400)
        except Exception as exc:
            report["rejected"].append({"sentence": sentence[:80], "reason": f"LLM 失敗：{type(exc).__name__}"})
            continue
        role = str(output.get("role") or "required")
        excerpt = str(output.get("excerpt") or "")
        attribute_id = output.get("attribute_id")
        if output.get("proposed_attribute") and isinstance(output["proposed_attribute"], dict):
            proposal = output["proposed_attribute"]
            if proposal.get("id") and not registry.has(str(proposal["id"])):
                report["proposed_attributes"].append({**proposal, "sentence": sentence[:160]})
        if role == "procedural" or not attribute_id:
            condition["status"] = "procedural" if role == "procedural" else "unresolved"
            condition["method"] = "llm"
            if role != "procedural" and is_real_condition(excerpt if excerpt_in_text(excerpt, text) else sentence):
                # 仍然是條件但無法對屬性 → complex 規則（永不拒絕）；屬性只在摘錄真的提到時才填
                rules.append({"id": __import__("uuid").uuid4().hex, "attribute_id": placeholder_attribute(registry, candidates, excerpt if excerpt_in_text(excerpt, text) else sentence), "operator": "exists", "value": None, "unit": "", "group_id": f"complex_{len(rules)}", "group_logic": "any", "complexity": "complex", "role": "required",
                              "human_readable": str(output.get("human_readable") or sentence)[:200], "evidence": {"excerpt": (excerpt if excerpt_in_text(excerpt, text) else sentence)[:300], "extractor": "llm", "condition_text": sentence[:200]}, "confidence": 0.5, "inferred": False, "inference_basis": "", "registry_version": registry.version})
                report["accepted"].append({"sentence": sentence[:80], "result": "complex"})
            continue
        attribute_id = str(attribute_id).strip().lower()
        attribute = registry.get(attribute_id)
        if attribute is None or attribute_id not in candidates:
            report["rejected"].append({"sentence": sentence[:80], "reason": f"屬性 {attribute_id} 不在候選"})
            condition["status"] = "unresolved"
            continue
        operator = normalize_operator(attribute, str(output.get("operator") or ""), output.get("value"))
        if operator not in attribute.allowed_operators:
            report["rejected"].append({"sentence": sentence[:80], "reason": f"operator {operator} 不相容"})
            condition["status"] = "unresolved"
            continue
        if not excerpt_in_text(excerpt, text):
            report["rejected"].append({"sentence": sentence[:80], "reason": "摘錄不在原文"})
            condition["status"] = "unresolved"
            continue
        if not _excerpt_mentions_attribute(attribute, excerpt):
            # 小模型會把「房屋破損之修繕」對到 identity.low_income 這種無關屬性：摘錄裡必須出現該屬性（或其身分標籤）的別名
            report["rejected"].append({"sentence": sentence[:80], "reason": f"摘錄未提到屬性「{attribute.label}」的任何別名"})
            condition["status"] = "unresolved"
            continue
        value = _coerce_value(attribute, operator, output.get("value")) if operator != "exists" else None
        if operator != "exists" and value is None:
            report["rejected"].append({"sentence": sentence[:80], "reason": "value 型態或值不合法", "proposed": {"attribute_id": attribute.id, "operator": operator, "value": str(output.get("value"))[:60]}})
            condition["status"] = "unresolved"
            continue
        if attribute.type == "number" and not number_in_excerpt(value, excerpt):
            report["rejected"].append({"sentence": sentence[:80], "reason": "數值未出現在摘錄"})
            condition["status"] = "unresolved"
            continue
        if not _cities_in_excerpt(attribute.id, value, excerpt):
            report["rejected"].append({"sentence": sentence[:80], "reason": "摘錄裡沒有這些縣市（不接受推定戶籍地）"})
            condition["status"] = "unresolved"
            continue
        if role not in {"required", "exclusion", "bonus"}:
            role = "required"
        rule = {
            "id": __import__("uuid").uuid4().hex, "attribute_id": attribute.id, "operator": operator, "value": value, "unit": attribute.unit,
            "group_id": ("exclusion_" if role == "exclusion" else "") + attribute.id.replace(".", "_") + ("_llm" if attribute.id == "identity.tags" else ""), "group_logic": "any", "complexity": "simple", "role": role,
            "human_readable": str(output.get("human_readable") or "")[:200] or f"{attribute.label} {operator} {value}", "evidence": {"excerpt": excerpt[:300], "extractor": "llm", "condition_text": sentence[:200]},
            "confidence": max(0.5, min(0.85, float(output.get("confidence", 0.6)))), "inferred": False, "inference_basis": "", "registry_version": registry.version,
        }
        if any(r["attribute_id"] == rule["attribute_id"] and r["operator"] == rule["operator"] and r["value"] == rule["value"] for r in rules):
            condition["status"] = "mapped"
            continue
        rules.append(rule)
        condition["status"] = "mapped"
        condition["attribute_id"] = attribute.id
        condition["method"] = "llm"
        report["accepted"].append({"sentence": sentence[:80], "attribute_id": attribute.id, "operator": operator, "value": value})
    return report



BATCH_SCHEMA = {
    "type": "object",
    "properties": {"results": {"type": "array", "items": {"type": "object", "properties": {"index": {"type": "integer"}, "attribute_id": {"type": ["string", "null"]}, "operator": {"type": "string"}, "value": {}, "role": {"type": "string"}, "human_readable": {"type": "string"}, "confidence": {"type": "number"}, "excerpt": {"type": "string"}}, "required": ["index", "attribute_id", "operator", "value", "role", "excerpt"]}}},
    "required": ["results"],
}


def _excerpt_mentions_attribute(attribute, excerpt: str) -> bool:
    """摘錄必須出現該屬性的別名（含語料別名）；identity.tags 則要出現任一身分標籤的別名。"""
    registry = get_registry()
    if attribute.id == "identity.tags":
        return bool(registry.tags_in_text(excerpt))
    if attribute.id in registry.attributes_in_text(excerpt, include_mined=True):
        return True
    tag_attr_ids = {registry.tag_attribute(t) for t in registry.tags_in_text(excerpt)}
    return attribute.id in tag_attr_ids



def _cities_in_excerpt(attribute_id: str, value, excerpt: str) -> bool:
    """戶籍縣市規則的每個縣市都要逐字出現在摘錄裡（「設籍本市」不能變成某個具體縣市）。"""
    if attribute_id != "residence.household_city":
        return True
    wanted = value if isinstance(value, list) else [value]
    named = set(find_cities(excerpt or ''))
    return all(city in named for city in wanted if city)

def _apply_condition_output(benefit: dict, condition: dict, output: dict, candidates: list[str], report: dict, text: str, rules: list[dict]) -> None:
    """把一句條件的 AI 輸出驗證後寫入 rules / condition 狀態（單句與批次共用）。"""
    registry = get_registry()
    sentence = condition.get("text", "")
    role = str(output.get("role") or "required")
    excerpt = str(output.get("excerpt") or "")
    attribute_id = output.get("attribute_id")
    if role == "procedural" or not attribute_id:
        condition["status"] = "procedural" if role == "procedural" else "unresolved"
        condition["method"] = "llm"
        if role != "procedural" and is_real_condition(excerpt if excerpt_in_text(excerpt, text) else sentence):
            rules.append({"id": __import__("uuid").uuid4().hex, "attribute_id": placeholder_attribute(registry, candidates, excerpt if excerpt_in_text(excerpt, text) else sentence), "operator": "exists", "value": None, "unit": "", "group_id": f"complex_{len(rules)}", "group_logic": "any", "complexity": "complex", "role": "required",
                          "human_readable": str(output.get("human_readable") or sentence)[:200], "evidence": {"excerpt": (excerpt if excerpt_in_text(excerpt, text) else sentence)[:300], "extractor": "llm", "condition_text": sentence[:200]}, "confidence": 0.5, "inferred": False, "inference_basis": "", "registry_version": registry.version})
            report["accepted"].append({"sentence": sentence[:80], "result": "complex"})
        return
    attribute_id = str(attribute_id).strip().lower()
    attribute = registry.get(attribute_id)
    if attribute is None or attribute_id not in candidates:
        report["rejected"].append({"sentence": sentence[:80], "reason": f"屬性 {attribute_id} 不在候選"})
        condition["status"] = "unresolved"
        return
    operator = normalize_operator(attribute, str(output.get("operator") or ""), output.get("value"))
    if operator not in attribute.allowed_operators:
        report["rejected"].append({"sentence": sentence[:80], "reason": f"operator {operator} 不相容", "proposed": {"attribute_id": attribute.id, "operator": operator, "value": str(output.get("value"))[:60]}})
        condition["status"] = "unresolved"
        return
    if not excerpt_in_text(excerpt, text):
        report["rejected"].append({"sentence": sentence[:80], "reason": "摘錄不在原文"})
        condition["status"] = "unresolved"
        return
    value = _coerce_value(attribute, operator, output.get("value")) if operator != "exists" else None
    if operator != "exists" and value is None:
        report["rejected"].append({"sentence": sentence[:80], "reason": "value 型態或值不合法", "proposed": {"attribute_id": attribute.id, "operator": operator, "value": str(output.get("value"))[:60]}})
        condition["status"] = "unresolved"
        return
    if attribute.type == "number" and not number_in_excerpt(value, excerpt):
        report["rejected"].append({"sentence": sentence[:80], "reason": "數值未出現在摘錄"})
        condition["status"] = "unresolved"
        return
    if not _cities_in_excerpt(attribute.id, value, excerpt):
        report["rejected"].append({"sentence": sentence[:80], "reason": "摘錄裡沒有這些縣市（不接受推定戶籍地）"})
        condition["status"] = "unresolved"
        return
    if role not in {"required", "exclusion", "bonus"}:
        role = "required"
    rule = {
        "id": __import__("uuid").uuid4().hex, "attribute_id": attribute.id, "operator": operator, "value": value, "unit": attribute.unit,
        "group_id": ("exclusion_" if role == "exclusion" else "") + attribute.id.replace(".", "_") + ("_llm" if attribute.id == "identity.tags" else ""), "group_logic": "any", "complexity": "simple", "role": role,
        "human_readable": str(output.get("human_readable") or "")[:200] or f"{attribute.label} {operator} {value}", "evidence": {"excerpt": excerpt[:300], "extractor": "llm", "condition_text": sentence[:200]},
        "confidence": max(0.5, min(0.85, float(output.get("confidence", 0.6) or 0.6))), "inferred": False, "inference_basis": "", "registry_version": registry.version,
    }
    if any(r["attribute_id"] == rule["attribute_id"] and r["operator"] == rule["operator"] and r["value"] == rule["value"] for r in rules):
        condition["status"] = "mapped"
        return
    rules.append(rule)
    condition["status"] = "mapped"
    condition["attribute_id"] = attribute.id
    condition["method"] = "llm"
    report["accepted"].append({"sentence": sentence[:80], "attribute_id": attribute.id, "operator": operator, "value": value})


def map_conditions_batch(benefit: dict, unmapped: list[dict], *, max_conditions: int = 10) -> dict:
    """每筆公告一次呼叫：把所有 unmapped 條件句一起送給本地 AI；逐句驗證後寫入 rules。"""
    provider = get_provider()
    registry = get_registry()
    report: dict = {"task": "condition_mapping", "model": provider.model if provider else "", "accepted": [], "rejected": [], "proposed_attributes": [], "mode": "batch"}
    if provider is None or not unmapped:
        return report
    text = benefit.get("original_text", "")
    rules: list[dict] = benefit.setdefault("rules", [])
    selected = unmapped[:max_conditions]
    candidate_union: list[str] = []
    for condition in selected:
        candidates = list(condition.get("candidates") or [])
        if not candidates:
            candidates = list(registry.attributes_in_text(condition.get("text", ""), include_mined=True).keys())[:5]
        if not candidates:
            domain = benefit.get("domain") or ""
            candidates = [a.id for a in registry.for_domains([domain] if domain else None) if a.hard_filter][:6]
        condition["_candidates"] = candidates
        for c in candidates:
            if c not in candidate_union:
                candidate_union.append(c)
    candidate_union = candidate_union[:16]
    sentences = "\n".join(f"{i}. {c.get('text', '')[:200]}" for i, c in enumerate(selected, start=1))
    prompt = render("condition_mapping_batch", TITLE=benefit.get("title", ""), CANDIDATES=_candidate_lines(candidate_union), SENTENCES=sentences)
    system, user = split_system_user(prompt)
    try:
        output = provider.complete_json(system, user, json_schema=BATCH_SCHEMA, max_tokens=200 + 140 * len(selected))
    except Exception as exc:
        report["rejected"].append({"sentence": "(batch)", "reason": f"LLM 失敗：{type(exc).__name__}"})
        for condition in selected:
            condition.pop("_candidates", None)
        return report
    by_index = {}
    for item in output.get("results") or []:
        if isinstance(item, dict) and isinstance(item.get("index"), int):
            by_index[item["index"]] = item
    for i, condition in enumerate(selected, start=1):
        candidates = condition.pop("_candidates", [])
        item = by_index.get(i)
        if item is None:
            condition["status"] = "unresolved"
            report["rejected"].append({"sentence": condition.get("text", "")[:80], "reason": "AI 未回覆此句"})
            continue
        _apply_condition_output(benefit, condition, item, [c for c in candidates if c in candidate_union] or candidate_union, report, text, rules)
    return report

# ------------------------------------------------------- complex judgement
def _context_around(text: str, excerpt: str, window: int = 600) -> str:
    if excerpt and excerpt in text:
        index = text.find(excerpt)
        return text[max(0, index - window) : index + len(excerpt) + window]
    return text[: 2 * window]


def judge_complex(rule: dict, profile_values: dict, original_text: str) -> dict | None:
    provider = get_provider()
    if provider is None:
        return None
    excerpt = (rule.get("evidence") or {}).get("excerpt", "")
    prompt = render("complex_eligibility", CONDITION=rule.get("human_readable") or rule.get("attribute_id", ""), EXCERPT=excerpt, TEXT=_context_around(original_text, excerpt), PROFILE=json.dumps(profile_values, ensure_ascii=False, indent=1))
    system, user = split_system_user(prompt)
    output = provider.complete_json(system, user, json_schema=VERDICT_SCHEMA, max_tokens=400)
    result = output.get("result")
    if result not in {"match", "not_match", "unknown"}:
        return None
    source_text = str(output.get("source_text", ""))
    if result != "unknown" and not excerpt_in_text(source_text, original_text):
        output["result"] = "unknown"
        output["reason"] = "模型引用的原文無法驗證，維持資料不足"
    output["provider"] = provider.name
    output["model"] = provider.model
    return output


# ------------------------------------------------------------ profile parse
def parse_profile(text: str, known: dict[str, Any]) -> dict:
    """回傳 {"attributes": [{id, value, excerpt, confidence}], "need_type": str, "need_excerpt": str, "model": str}（已驗證）。"""
    provider = get_provider()
    registry = get_registry()
    result: dict = {"attributes": [], "need_type": "unknown", "need_excerpt": "", "model": provider.model if provider else ""}
    if provider is None or not text.strip():
        return result
    lines = []
    for attribute in registry.askable():
        if attribute.id in known or attribute.type == "text":
            continue
        values = ""
        if attribute.type in {"enum", "multi_enum"}:
            values = "：" + " | ".join(str(v.get("value")) for v in attribute.values[:12])
        lines.append(f"- {attribute.id}：{attribute.label}：{attribute.type}{values}")
    prompt = render("user_profile_parser", ATTRIBUTES="\n".join(lines[:70]), TEXT=text[:1500])
    system, user = split_system_user(prompt)
    output = provider.complete_json(system, user, json_schema=PROFILE_SCHEMA, max_tokens=800)
    for item in output.get("attributes") or []:
        attribute = registry.get(str(item.get("id", "")))
        excerpt = str(item.get("excerpt") or "")
        if attribute is None or attribute.type == "text" or not excerpt or excerpt not in text:
            continue
        operator = "in" if attribute.type in {"multi_enum"} else "="
        value = _coerce_value(attribute, operator, item.get("value"))
        if value is None:
            continue
        if attribute.type == "number" and not number_in_excerpt(value, excerpt):
            continue
        result["attributes"].append({"id": attribute.id, "value": value, "excerpt": excerpt, "confidence": max(0.4, min(0.9, float(item.get("confidence", 0.6))))})
    need = str(output.get("need_type") or "unknown")
    if need in {"cash_now", "reduce_burden", "honor", "service"}:
        result["need_type"] = need
        result["need_excerpt"] = str(output.get("need_excerpt") or "")[:80]
    return result
