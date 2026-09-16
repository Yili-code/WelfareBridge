"""資格骨幹（eligibility core）：每筆補助少數幾個「決定誰能申請」的條件，用來分層顯示。

骨幹由 services/core_builder.py 離線建立（結構訊號 + 原文 + 抽取規則 + 本地 AI 投票），存在 record["eligibility_core"]：
    {"version": 1, "facets": [facet, ...]}
facet 種類：
    residence         {"cities": [...] | [] 表示全國, "basis": household|current|either|school}
    age               {"min": n|None, "max": n|None, "via_child": bool}          受補助者年齡（含端點）
    education         {"levels": [...], "via_child": bool}                      限定學制
    student           {"value": True, "via_child": bool}                        必須在學
    identity_any      {"tags": [...]}                                            至少具備其中一個身分
    identity_exclude  {"tags": [...]}                                            具備任一即不符
    nationality       {"value": roc|foreign}
    attr              {"attribute_id": ..., "value": ...}                        其他布林／enum 必要條件
每個 facet 另有 status：confirmed（兩個以上獨立訊號一致，可據以排除）／uncertain（只有單一訊號，只能提示）。

媒合時逐項判斷 satisfied / violated / unknown：
    - confirmed facet violated → 不顯示（媒合診斷仍看得到原因）
    - 沒有任何 facet violated、confirmed facet 都 satisfied、至少一個有鑑別力 → ✅ 符合（tier1）
      （只有單一來源的 uncertain facet 未知時不擋 tier1、也不要求補資料；多來源但語氣像擇一的會擋；明確不符一律降為 tier2 並提示）
    - 其他 → 🟡 可能符合・需補充資料（tier2），列出要補的欄位
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..registry import Registry
from ..services.normalization import normalize_city
from .profile import Profile

# 「須在學」「全國皆可」單獨不足以標 ✅（獎學金幾乎都另有學制、科系、成績限制）
DISCRIMINATING = {"residence", "age", "education", "identity_any", "identity_exclude", "nationality", "attr"}
LEVEL_LABELS = {"elementary": "國小", "junior_high": "國中", "senior_high": "高中", "vocational_high": "高職", "junior_college": "專科", "university": "大學", "master": "碩士", "doctoral": "博士"}
BASIS_LABELS = {"household": "設籍", "current": "居住", "either": "設籍或居住", "school": "就讀學校位於"}


@dataclass
class FacetResult:
    facet: dict
    state: str  # satisfied | violated | unknown
    reason: str
    needs: list[str] = field(default_factory=list)  # 補哪些欄位可以判斷

    @property
    def confirmed(self) -> bool:
        return self.facet.get("status") == "confirmed"

    def to_dict(self) -> dict:
        return {"kind": self.facet.get("kind"), "status": self.facet.get("status"), "state": self.state, "reason": self.reason, "needs": self.needs, "label": describe(self.facet), "signals": self.facet.get("signals") or []}


def describe(facet: dict) -> str:
    kind = facet.get("kind")
    if kind == "residence":
        cities = facet.get("cities") or []
        return "全國皆可申請" if not cities else f"{BASIS_LABELS.get(facet.get('basis') or 'household', '設籍')}{'、'.join(cities)}"
    if kind == "age":
        low, high = facet.get("min"), facet.get("max")
        who = "子女或本人" if facet.get("via_child") else ""
        if low is not None and high is not None:
            return f"{who}年齡 {low:g}～{high:g} 歲"
        if low is not None:
            return f"{who}年齡 {low:g} 歲以上"
        return f"{who}年齡 {high:g} 歲以下" if high is not None else "年齡條件"
    if kind == "education":
        return ("子女或本人" if facet.get("via_child") else "") + "就讀" + "、".join(dict.fromkeys(LEVEL_LABELS.get(v, v) for v in facet.get("levels") or []))
    if kind == "student":
        return "須為在學學生" + ("（或其子女）" if facet.get("via_child") else "")
    if kind in {"identity_any", "identity_exclude"}:
        from ..registry import get_registry

        registry = get_registry()
        labels = "、".join(registry.tags[t].label if t in registry.tags else t for t in facet.get("tags") or [])
        return f"具{labels}身分" + ("（其一）" if len(facet.get("tags") or []) > 1 else "") if kind == "identity_any" else f"非{labels}"
    if kind == "nationality":
        return {"roc": "中華民國國籍", "foreign": "外國籍"}.get(facet.get("value"), str(facet.get("value")))
    if kind == "attr":
        from ..registry import get_registry

        attribute = get_registry().get(facet.get("attribute_id", ""))
        if attribute is None:
            return str(facet.get("attribute_id"))
        value = facet.get("value")
        if attribute.type == "boolean":
            return attribute.label if value else f"非{attribute.label}"
        return f"{attribute.label}：{attribute.value_label(value)}"
    return str(kind)


def _range_state(low: Any, high: Any, value_low: float, value_high: float | None) -> str:
    low = float("-inf") if low is None else float(low)
    high = float("inf") if high is None else float(high)
    value_high = float("inf") if value_high is None else float(value_high)
    if low <= value_low and value_high <= high:
        return "satisfied"
    if value_high < low or value_low > high:
        return "violated"
    return "unknown"


def _combine_child(self_state: str, via_child: bool, child_state: str) -> str:
    if not via_child:
        return self_state
    if "satisfied" in (self_state, child_state):
        return "satisfied"
    if self_state == "violated" and child_state == "violated":
        return "violated"
    return "unknown"


def _child_age_state(facet: dict, values: dict) -> str:
    count = values.get("family.children_count")
    if count is not None and float(count) == 0:
        return "violated"
    youngest = values.get("family.youngest_child_age")
    if youngest is None:
        return "unknown"
    state = _range_state(facet.get("min"), facet.get("max"), float(youngest), float(youngest))
    return "satisfied" if state == "satisfied" else "unknown"  # 只知道最小的孩子；其他孩子可能落在範圍內


def evaluate_facet(facet: dict, profile: Profile, registry: Registry, values: dict | None = None, tag_states: tuple[set[str], set[str]] | None = None) -> FacetResult:
    values = values if values is not None else profile.all_values(registry, include_tags=False)
    kind = facet.get("kind")
    if kind == "residence":
        cities = {normalize_city(c) or c for c in facet.get("cities") or []}
        if not cities:
            return FacetResult(facet, "satisfied", "全國皆可申請")
        basis = facet.get("basis") or "household"
        household = normalize_city(values.get("residence.household_city"))
        current = normalize_city(values.get("residence.current_city"))
        school = normalize_city(values.get("education.school_city"))
        label = "、".join(sorted(cities))
        if basis == "school":
            if school is None:
                return FacetResult(facet, "unknown", f"需就讀{label}的學校", ["education.school_city"])
            return FacetResult(facet, "satisfied" if school in cities else "violated", f"學校所在縣市{'符合' if school in cities else '不在'}{label}")
        if household in cities or (basis in {"current", "either"} and current in cities):
            return FacetResult(facet, "satisfied", f"{BASIS_LABELS.get(basis, '設籍')}{label}")
        if basis == "current":
            if current is None:
                return FacetResult(facet, "unknown", f"需居住於{label}", ["residence.current_city"])
            return FacetResult(facet, "violated", f"限居住於{label}")
        if basis == "household":
            if household is None:
                return FacetResult(facet, "unknown", f"需設籍{label}", ["residence.household_city"])
            return FacetResult(facet, "violated", f"限設籍{label}")
        # either
        if household is None or current is None:
            return FacetResult(facet, "unknown", f"需設籍或居住於{label}", [a for a, v in (("residence.household_city", household), ("residence.current_city", current)) if v is None])
        return FacetResult(facet, "violated", f"限設籍或居住於{label}")

    if kind == "age":
        age = values.get("applicant.age")
        ranges = ((profile.preferences or {}).get("number_ranges") or {}).get("applicant.age")
        if age is not None:
            self_state = _range_state(facet.get("min"), facet.get("max"), float(age), float(age))
        elif isinstance(ranges, list) and len(ranges) == 2 and ranges[0] is not None:
            self_state = _range_state(facet.get("min"), facet.get("max"), float(ranges[0]), ranges[1])
        else:
            self_state = "unknown"
        via_child = bool(facet.get("via_child"))
        state = _combine_child(self_state, via_child, _child_age_state(facet, values) if via_child else "violated")
        needs = [] if state != "unknown" else (["applicant.age"] if self_state == "unknown" else []) + (["family.youngest_child_age"] if via_child else [])
        text = describe(facet)
        return FacetResult(facet, state, {"satisfied": f"符合{text}", "violated": f"不符{text}", "unknown": f"需確認{text}"}[state], needs)

    if kind in {"education", "student"}:
        via_child = bool(facet.get("via_child"))
        is_student = values.get("applicant.is_student")
        level = values.get("education.level")
        levels = set(facet.get("levels") or []) if kind == "education" else None
        if is_student is False:
            self_state = "violated"
        elif kind == "student":
            self_state = "satisfied" if is_student is True or level else "unknown"
        elif level:
            self_state = "satisfied" if level in levels else "violated"
        else:
            candidates = ((profile.preferences or {}).get("enum_candidates") or {}).get("education.level")
            if isinstance(candidates, list) and candidates:
                inside = [c in levels for c in candidates]
                self_state = "satisfied" if all(inside) else "violated" if not any(inside) else "unknown"
            else:
                self_state = "unknown"
        child_state = "violated"
        if via_child:
            count = values.get("family.children_count")
            child_state = "violated" if count is not None and float(count) == 0 else "unknown"
        state = _combine_child(self_state, via_child, child_state)
        needs = [] if state != "unknown" else (["education.level"] if self_state == "unknown" else []) + (["family.children_count"] if via_child else [])
        text = describe(facet)
        return FacetResult(facet, state, {"satisfied": f"符合{text}", "violated": f"不符{text}", "unknown": f"需確認{text}"}[state], needs)

    if kind in {"identity_any", "identity_exclude"}:
        true_tags, false_tags = tag_states if tag_states is not None else registry.tag_states(values)
        tags = set(facet.get("tags") or [])
        text = describe(facet)
        needs = [a for a in (registry.tag_attribute(t) for t in sorted(tags - true_tags - false_tags)) if a]
        if kind == "identity_any":
            strict = set(facet.get("strict_tags") or tags)
            if strict & true_tags:
                return FacetResult(facet, "satisfied", f"符合{text}")
            if tags & true_tags:
                return FacetResult(facet, "unknown", f"需確認你的身分是否屬於{text.removeprefix('具')}（公告寫法不一）", needs)
            if tags <= false_tags:
                return FacetResult(facet, "violated", f"未具{text.removeprefix('具')}")
            return FacetResult(facet, "unknown", f"需確認是否{text}", needs)
        if tags & true_tags:
            return FacetResult(facet, "violated", f"不得為{text.removeprefix('非')}")
        if tags <= false_tags:
            return FacetResult(facet, "satisfied", f"符合{text}")
        return FacetResult(facet, "unknown", f"需確認是否屬於排除身分（{text.removeprefix('非')}）", needs)

    if kind == "nationality":
        value = values.get("applicant.nationality")
        if value is None:
            return FacetResult(facet, "unknown", f"需確認國籍（{describe(facet)}）", ["applicant.nationality"])
        return FacetResult(facet, "satisfied" if value == facet.get("value") else "violated", f"限{describe(facet)}")

    if kind == "attr":
        attribute_id = facet.get("attribute_id", "")
        value = values.get(attribute_id)
        text = describe(facet)
        if value is None:
            return FacetResult(facet, "unknown", f"需確認：{text}", [attribute_id])
        expected = facet.get("value")
        ok = (bool(value) == bool(expected)) if isinstance(expected, bool) else str(value) == str(expected)
        return FacetResult(facet, "satisfied" if ok else "violated", f"{'符合' if ok else '不符'}：{text}")

    return FacetResult(facet, "unknown", f"未支援的骨幹條件 {kind}")


@dataclass
class CoreOutcome:
    results: list[FacetResult]
    violated_confirmed: list[FacetResult]
    violated_uncertain: list[FacetResult]
    unknown: list[FacetResult]
    satisfied: list[FacetResult]

    @property
    def has_core(self) -> bool:
        return bool(self.results)

    @property
    def discriminating_confirmed(self) -> bool:
        return any(r.confirmed and r.state == "satisfied" and r.facet.get("kind") in DISCRIMINATING and not (r.facet.get("kind") == "residence" and not r.facet.get("cities")) for r in self.results)

    @property
    def unknown_confirmed(self) -> list[FacetResult]:
        """資料不足時要擋住 tier1 的條件：已確認的，或多個來源都提到但原文語氣像擇一／優先而未確認的。"""
        # 兒少／子女方案（via_child）在不知道有沒有孩子時也不能標 ✅
        # 戶籍縣市（回測準確度高）不論票數都要確認
        return [r for r in self.unknown if r.confirmed or len(r.facet.get("signals") or []) >= 2 or r.facet.get("via_child") or (r.facet.get("kind") == "residence" and r.facet.get("cities"))]

    def needs(self) -> list[str]:
        out: list[str] = []
        for result in self.unknown_confirmed:
            for attribute_id in result.needs:
                if attribute_id not in out:
                    out.append(attribute_id)
        return out


def evaluate_core(core: dict | None, profile: Profile, registry: Registry) -> CoreOutcome:
    facets = [f for f in ((core or {}).get("facets") or []) if f.get("status") in {"confirmed", "uncertain"}]
    values = profile.all_values(registry, include_tags=False)
    states = registry.tag_states(values)
    results = [evaluate_facet(f, profile, registry, values, states) for f in facets]
    return CoreOutcome(
        results=results,
        violated_confirmed=[r for r in results if r.state == "violated" and r.confirmed],
        violated_uncertain=[r for r in results if r.state == "violated" and not r.confirmed],
        unknown=[r for r in results if r.state == "unknown"],
        satisfied=[r for r in results if r.state == "satisfied"],
    )
