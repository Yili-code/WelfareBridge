"""使用者資料（v2）：{attribute_id: AttributeValue} + 需求類型／排斥／已領補助。

- 未提供的屬性一律 None；rule engine 對 None 回 unknown（資料不足），不會判成不符合。
- 推導屬性（derived）與虛擬屬性 identity.tags 由 registry 即時計算。
- 每個值記錄來源（asked / parsed / form / inferred）與使用者原話摘錄，供結果頁說明「為什麼認為你是…」。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..registry import Registry, get_registry

NEED_TYPES = {"cash_now", "reduce_burden", "honor", "service", "unknown"}
DISLIKES = {"interview", "essay", "recommendation", "obligations", "financial_proof", "office_proof", "loan", "competitive"}


@dataclass
class AttributeValue:
    value: Any
    source: str = "form"  # asked | parsed | form | inferred | skipped | unsure
    evidence: str = ""
    confirmed: bool = False
    confidence: float = 1.0

    def to_dict(self) -> dict:
        return {"value": self.value, "source": self.source, "evidence": self.evidence, "confirmed": self.confirmed, "confidence": self.confidence}


@dataclass
class Profile:
    attributes: dict[str, AttributeValue] = field(default_factory=dict)
    need_type: str = "unknown"
    urgency: str = "normal"
    dislikes: list[str] = field(default_factory=list)
    current_benefits: list[str] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)
    asked: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    # ------------------------------------------------------------ building
    @classmethod
    def from_dict(cls, data: dict | None, registry: Registry | None = None) -> "Profile":
        registry = registry or get_registry()
        data = data or {}
        profile = cls()
        raw_attributes = data.get("attributes") or {}
        for attribute_id, raw in raw_attributes.items():
            if not registry.has(attribute_id):
                profile.notes.append(f"忽略未知屬性 {attribute_id}")
                continue
            if isinstance(raw, dict) and "value" in raw:
                value = cls._coerce(registry, attribute_id, raw.get("value"))
                if value is None and raw.get("source") not in {"skipped", "unsure"}:
                    continue
                profile.attributes[attribute_id] = AttributeValue(value=value, source=str(raw.get("source", "form")), evidence=str(raw.get("evidence", "") or ""), confirmed=bool(raw.get("confirmed", False)), confidence=float(raw.get("confidence", 1.0)))
            else:
                value = cls._coerce(registry, attribute_id, raw)
                if value is None:
                    continue
                profile.attributes[attribute_id] = AttributeValue(value=value, source="form", confirmed=True)
        profile.need_type = data.get("need_type") if data.get("need_type") in NEED_TYPES else "unknown"
        profile.urgency = data.get("urgency") if data.get("urgency") in {"high", "normal", "low"} else "normal"
        profile.dislikes = [d for d in (data.get("dislikes") or []) if d in DISLIKES]
        profile.current_benefits = [str(b) for b in (data.get("current_benefits") or []) if b]
        profile.preferences = dict(data.get("preferences") or {})
        profile.asked = list(data.get("asked") or [])
        profile.skipped = list(data.get("skipped") or [])
        return profile

    @staticmethod
    def _coerce(registry: Registry, attribute_id: str, value: Any) -> Any:
        attribute = registry.get(attribute_id)
        if attribute is None or value is None or value == "":
            return None
        kind = attribute.type
        try:
            if kind == "number":
                if isinstance(value, bool):
                    return None
                return float(value)
            if kind == "boolean":
                if isinstance(value, bool):
                    return value
                if isinstance(value, str):
                    if value.lower() in {"true", "1", "yes", "是"}:
                        return True
                    if value.lower() in {"false", "0", "no", "否"}:
                        return False
                return None
            if kind == "multi_enum":
                values = value if isinstance(value, list) else [value]
                allowed = set(attribute.value_list)
                return [str(v) for v in values if str(v) in allowed]
            if kind in {"enum", "city", "date", "text"}:
                if isinstance(value, list):
                    value = value[0] if value else None
                if value is None:
                    return None
                if kind == "city":
                    from ..services.normalization import normalize_city

                    return normalize_city(str(value))
                if kind == "enum" and str(value) not in attribute.value_list:
                    labels = {str(v.get("label")): str(v.get("value")) for v in attribute.values}
                    return labels.get(str(value))
                return str(value)
        except (TypeError, ValueError):
            return None
        return value

    def to_dict(self) -> dict:
        return {
            "attributes": {k: v.to_dict() for k, v in self.attributes.items()},
            "need_type": self.need_type,
            "urgency": self.urgency,
            "dislikes": self.dislikes,
            "current_benefits": self.current_benefits,
            "preferences": self.preferences,
            "asked": self.asked,
            "skipped": self.skipped,
        }

    # ------------------------------------------------------------- values
    def raw_values(self) -> dict[str, Any]:
        return {k: v.value for k, v in self.attributes.items() if v.value is not None}

    def value(self, attribute_id: str, registry: Registry | None = None) -> Any:
        registry = registry or get_registry()
        item = self.attributes.get(attribute_id)
        if item is not None and item.value is not None:
            return item.value
        attribute = registry.get(attribute_id)
        if attribute is None:
            return None
        if attribute_id == "identity.tags":
            tags, answered = registry.tags_from_attribute_values(self.all_values(registry, include_tags=False))
            return sorted(tags) if answered else None
        if attribute.derived and attribute.derived != "tags":
            return registry.evaluate_derived(attribute, self.all_values(registry, include_derived=False))
        return None

    def all_values(self, registry: Registry | None = None, *, include_derived: bool = True, include_tags: bool = True) -> dict[str, Any]:
        registry = registry or get_registry()
        values = self.raw_values()
        if include_derived:
            for attribute in registry.attributes.values():
                if attribute.id == "identity.tags" or not attribute.derived or attribute.id in values:
                    continue
                derived = registry.evaluate_derived(attribute, values)
                if derived is not None:
                    values[attribute.id] = derived
            if include_tags:
                tags = self.value("identity.tags", registry)
                if tags is not None:
                    values["identity.tags"] = tags
        return values

    def has(self, attribute_id: str, registry: Registry | None = None) -> bool:
        return self.value(attribute_id, registry) is not None

    def answered(self, attribute_id: str) -> bool:
        item = self.attributes.get(attribute_id)
        return item is not None and (item.value is not None or item.source in {"skipped", "unsure"})

    def set(self, attribute_id: str, value: Any, *, source: str = "asked", evidence: str = "", confirmed: bool = True, confidence: float = 1.0) -> None:
        coerced = self._coerce(get_registry(), attribute_id, value)
        if coerced is None and source not in {"skipped", "unsure"}:
            return
        self.attributes[attribute_id] = AttributeValue(value=coerced, source=source, evidence=evidence, confirmed=confirmed, confidence=confidence)

    def merge(self, other: "Profile") -> "Profile":
        merged = Profile.from_dict(self.to_dict())
        for attribute_id, item in other.attributes.items():
            if item.value is not None or attribute_id not in merged.attributes:
                merged.attributes[attribute_id] = item
        if other.need_type != "unknown":
            merged.need_type = other.need_type
        merged.dislikes = list(dict.fromkeys([*merged.dislikes, *other.dislikes]))
        merged.current_benefits = list(dict.fromkeys([*merged.current_benefits, *other.current_benefits]))
        merged.preferences.update(other.preferences)
        merged.asked = list(dict.fromkeys([*merged.asked, *other.asked]))
        merged.skipped = list(dict.fromkeys([*merged.skipped, *other.skipped]))
        return merged

    def summary_chips(self, registry: Registry | None = None) -> list[dict]:
        registry = registry or get_registry()
        chips = []
        for attribute_id, item in self.attributes.items():
            attribute = registry.get(attribute_id)
            if attribute is None or item.value is None:
                continue
            value = item.value
            if attribute.type == "enum":
                display = attribute.value_label(value)
            elif attribute.type == "multi_enum":
                display = "、".join(attribute.value_label(v) for v in value)
            elif attribute.type == "boolean":
                display = "是" if value else "否"
            else:
                display = f"{value:g}" if isinstance(value, float) else str(value)
            chips.append({"attribute_id": attribute_id, "label": attribute.label, "value": display, "source": item.source, "evidence": item.evidence})
        return chips
