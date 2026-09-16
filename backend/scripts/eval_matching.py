"""媒合回測：黃金集（data/gold/matching/）× 真實媒合引擎。

    python scripts/eval_matching.py                 # 儀表板輸入與完整輸入兩種模式
    python scripts/eval_matching.py --details 20    # 另列錯誤樣本
    python scripts/eval_matching.py --out ../docs/generated/matching-eval.md

每一組（使用者 × 補助）先用黃金標註算出兩個答案：
  truth：以使用者真實情況判斷 → 符合 eligible／不符 ineligible
  view ：只用系統實際收到的欄位判斷 → 符合／不符／資料不足 unknown
再和系統輸出比較：tier1（符合）／tier2（可能符合・需補充）／hidden（不顯示）。
  漏掉        truth=符合，系統卻不顯示
  可避免誤推  truth=不符且 view 已足以判斷不符，系統仍顯示
  誤標符合    truth=不符，系統卻標成 tier1
  需補充      truth=不符但 view 資料不足，系統放在 tier2（可接受）
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.config import get_settings  # noqa: E402
from app.db import get_db  # noqa: E402
from app.matching import MatchingEngine, Profile, hard_filter_candidates, load_records, rank  # noqa: E402
from app.registry import get_registry  # noqa: E402

GOLD = Path(get_settings().data_path) / "gold" / "matching"

# ---- src/lib/questionnaire.ts 的選項（索引順序必須一致）
OPTIONS = {
    "needs": ["就學、學費或獎助學金", "求職、失業或職業訓練", "租屋、住宅或居住改善", "生活費、育兒或急難救助", "醫療、身心障礙或長期照顧"],
    "age": ["未滿 18 歲", "18～未滿 25 歲", "25～未滿 30 歲", "30～未滿 65 歲", "65 歲以上"],
    "residence": ["戶籍與居住地在同一縣市，設籍未滿半年", "戶籍與居住地在同一縣市，設籍已滿半年", "戶籍與居住地在不同縣市", "在臺居住，但沒有臺灣戶籍", "不確定戶籍或設籍時間"],
    "education": ["目前未在學", "國小或國中", "高中職或五專前三年", "大學、二專或五專後兩年", "碩士班或博士班"],
    "economy": ["已取得低收入戶資格", "已取得中低收入戶資格", "沒有上述資格，但家庭經濟困難", "沒有上述資格，目前經濟大致穩定", "不清楚家庭經濟資料或認定狀態"],
    "identity": ["原住民", "本人或家庭成員持有身心障礙證明", "單親家庭，或經認定的特殊境遇家庭", "其他特定身分，例如僑生、榮民子女、軍公教遺族或客家身分", "以上皆無／不確定"],
    "employment": ["受僱工作中，包含兼職", "自營工作或接案", "待業中，正在找工作", "正在參加職業訓練", "目前未工作，也未求職", "學生"],
    "housing": ["租屋，包含整戶或分租", "學校宿舍", "自己或配偶持有的住宅", "與親友同住或借住", "機構住宿、無固定住所或其他情況"],
    "support": ["懷孕、育兒，或扶養未成年子女", "家人需要協助進食、洗澡、行動等日常生活", "本人因照顧家人而減少工作或無法工作", "最近遭遇重病、事故、災害或主要經濟來源中斷", "以上皆無／不確定"],
    "benefits": ["學費減免、助學金或獎學金", "失業給付、職訓津貼或就業補助", "租金或其他住宅補助", "生活、育兒、身障或長照相關補助", "沒有／不確定"],
}
AGE_RANGES = [[0, 17], [18, 24], [25, 29], [30, 64], [65, None]]
LEVELS = {"國小或國中": ["elementary", "junior_high"], "高中職或五專前三年": ["senior_high", "vocational_high", "junior_college"],
          "大學、二專或五專後兩年": ["university", "junior_college"], "碩士班或博士班": ["master", "doctoral"]}
TAG_ATTRIBUTE = {"low_income": "identity.low_income", "middle_low_income": "identity.middle_low_income", "economic_hardship": "identity.economic_hardship",
                 "special_circumstances": "identity.special_circumstances", "indigenous": "identity.indigenous", "hakka": "identity.hakka",
                 "disabled": "disability.has_certificate", "disabled_family": "disability.family_member_has_certificate", "new_immigrant": "identity.new_immigrant",
                 "single_parent": "identity.single_parent", "grandparent_family": "identity.grandparent_family", "orphan": "identity.orphan",
                 "veteran_family": "identity.veteran_family", "military_civil_bereaved": "identity.military_civil_bereaved",
                 "unemployed_worker_child": "identity.unemployed_worker_child", "overseas_chinese": "identity.overseas_chinese",
                 "foreign_student": "identity.foreign_student", "catastrophic_illness": "health.catastrophic_illness", "dementia": "care.dementia_diagnosis"}
ATTR_OF_TRUTH = {"employment": "employment.status", "involuntary_separation": "employment.involuntary_separation", "housing": "housing.tenure",
                 "needs_care": "care.needs_care", "caregiver": "care.is_primary_caregiver", "gender": "applicant.gender", "nationality": "applicant.nationality"}


# ============================================================ 系統收到的欄位（儀表板）
def wizard_profile(persona: dict) -> dict:
    """建檔精靈存下的 Profile（src/components/ProfileWizard.tsx + questionnaire.profileTags）。"""
    q = persona["q"]
    screening = {key: [OPTIONS[key][i] for i in (value if isinstance(value, list) else [value])] for key, value in q.items()}
    economy = ["低收入戶", "中低收入戶", "近貧／經濟不穩定", "一般家庭", "不確定"][q["economy"]]
    region = persona.get("region") or ""
    no_household = q["residence"] == 3
    same_city = q["residence"] in (0, 1)
    return {"age": persona.get("exact_age"), "region": "" if no_household else region, "currentRegion": region if same_city else (persona.get("current_region") or ""),
            "economy": economy, "screening": screening}


def to_benefit_profile(profile: dict) -> dict:
    """src/lib/benefit-profile.ts 的 Python 移植版（兩邊必須同步修改）。"""
    screening = profile.get("screening") or {}
    attributes: dict = {}
    if profile.get("age") is not None:
        attributes["applicant.age"] = profile["age"]
    if screening.get("residence") and profile.get("region"):
        attributes["residence.household_city"] = profile["region"]
    if profile.get("currentRegion"):
        attributes["residence.current_city"] = profile["currentRegion"]
    if profile.get("economy") == "低收入戶":
        attributes["identity.low_income"] = True
    if profile.get("economy") == "中低收入戶":
        attributes["identity.middle_low_income"] = True
    economy = (screening.get("economy") or [None])[0]
    if economy in (OPTIONS["economy"][2], OPTIONS["economy"][3]):
        attributes["identity.low_income"] = False
        attributes["identity.middle_low_income"] = False
    education = (screening.get("education") or [None])[0]
    if education in OPTIONS["education"]:
        attributes["applicant.is_student"] = education != OPTIONS["education"][0]
    preferences = {"enum_candidates": {"education.level": LEVELS[education]} if education in LEVELS else {}}
    return {"attributes": attributes, "need_type": "unknown", "dislikes": [], "current_benefits": [], "asked": [], "skipped": [], "preferences": preferences}


EMPLOYMENT = ["employed", "self_employed", "unemployed", None, None, "student"]
HOUSING = ["rent", "dorm", "own", "family", None]


def to_matching_profile(profile: dict) -> dict:
    """src/lib/benefit-profile.ts toMatchingProfile 的 Python 移植版（兩邊必須同步修改）。"""
    base = to_benefit_profile(profile)
    attributes, preferences = dict(base["attributes"]), dict(base["preferences"])
    screening = profile.get("screening") or {}
    chosen = lambda key: [OPTIONS[key].index(o) for o in screening.get(key) or [] if o in OPTIONS[key]]
    if profile.get("age") is None and chosen("age"):
        preferences["number_ranges"] = {"applicant.age": AGE_RANGES[chosen("age")[0]]}
    economy = chosen("economy")
    if economy == [2]:
        attributes["identity.economic_hardship"] = True
    if economy == [3]:
        attributes["identity.economic_hardship"] = False
    identity = chosen("identity")
    if identity:
        attributes["identity.indigenous"] = 0 in identity
        if 1 not in identity:
            attributes["disability.has_certificate"] = False
            attributes["disability.family_member_has_certificate"] = False
        if 2 not in identity:
            attributes["identity.single_parent"] = False
            attributes["identity.special_circumstances"] = False
    employment = [EMPLOYMENT[i] for i in chosen("employment") if EMPLOYMENT[i]]
    if len(employment) == 1:
        attributes["employment.status"] = employment[0]
    housing = chosen("housing")
    if housing and HOUSING[housing[0]]:
        attributes["housing.tenure"] = HOUSING[housing[0]]
    support = chosen("support")
    if 1 in support:
        attributes["care.needs_care"] = True
    if 2 in support:
        attributes["care.is_primary_caregiver"] = True
    return {**base, "attributes": attributes, "preferences": preferences}


# ============================================================ 事實（三值）
def truth_facts(persona: dict) -> dict:
    t = persona["truth"]
    tags = {tag: (tag in (t.get("tags") or [])) for tag in TAG_ATTRIBUTE}
    attrs = {attr: t[key] for key, attr in ATTR_OF_TRUTH.items() if key in t}
    attrs.setdefault("employment.involuntary_separation", False)
    attrs.setdefault("care.needs_care", False)
    attrs.setdefault("care.is_primary_caregiver", False)
    return {"age": t.get("age"), "age_range": None, "household_city": t.get("household_city"), "household_known": True, "current_city": t.get("current_city"),
            "school_city": t.get("school_city") or (t.get("household_city") if t.get("student") else None),
            "student": t.get("student"), "education_level": t.get("education_level"), "education_candidates": None,
            "tags": tags, "attrs": attrs, "children": t.get("children") or [], "child_levels": t.get("child_levels") or []}


def facts_from_engine_input(data: dict) -> dict:
    """由「系統實際收到的欄位」推回事實；沒送的一律未知。"""
    a = data.get("attributes") or {}
    prefs = data.get("preferences") or {}
    tags = {tag: a.get(attr) for tag, attr in TAG_ATTRIBUTE.items()}
    ranges = (prefs.get("number_ranges") or {}).get("applicant.age")
    return {"age": a.get("applicant.age"), "age_range": ranges, "household_city": a.get("residence.household_city"), "household_known": "residence.household_city" in a,
            "current_city": a.get("residence.current_city"), "school_city": a.get("education.school_city"),
            "student": a.get("applicant.is_student"), "education_level": a.get("education.level"), "education_candidates": (prefs.get("enum_candidates") or {}).get("education.level"),
            "tags": tags, "attrs": {attr: a[attr] for attr in ATTR_OF_TRUTH.values() if attr in a},
            "children": data.get("_children"), "child_levels": data.get("_child_levels")}


def engine_input_from_truth(facts: dict) -> dict:
    attributes = {"applicant.age": facts["age"], "applicant.is_student": facts["student"]}
    if facts["household_city"]:
        attributes["residence.household_city"] = facts["household_city"]
    if facts["current_city"]:
        attributes["residence.current_city"] = facts["current_city"]
    if facts["education_level"]:
        attributes["education.level"] = facts["education_level"]
    if facts.get("school_city"):
        attributes["education.school_city"] = facts["school_city"]
    for tag, value in facts["tags"].items():
        attributes[TAG_ATTRIBUTE[tag]] = value
    attributes.update(facts["attrs"])
    if facts["children"] is not None:
        attributes["family.children_count"] = len(facts["children"])
        if facts["children"]:
            attributes["family.youngest_child_age"] = min(facts["children"])
    return {"attributes": {k: v for k, v in attributes.items() if v is not None}, "need_type": "unknown", "_children": facts["children"], "_child_levels": facts["child_levels"]}


# ============================================================ 黃金判斷
class Tags:
    def __init__(self, facts: dict, registry):
        self.registry = registry
        known_true = {tag for tag, value in facts["tags"].items() if value is True}
        age = facts.get("age")
        if age is not None and age >= 65:
            known_true.add("elderly")
        self.true = registry.expand_tags(known_true)
        self.values = dict(facts["tags"])
        if age is not None:
            self.values["elderly"] = age >= 65

    def state(self, tag: str):
        if tag in self.true:
            return True
        if tag == "disadvantaged":
            implying = [t.id for t in self.registry.tags.values() if "disadvantaged" in t.implies]
            return False if all(self.values.get(t) is False for t in implying) else None
        return False if self.values.get(tag) is False else None


def _range_vs(lo, hi, value_lo, value_hi):
    """回傳 True（值域全在範圍內）／False（完全在外）／None（部分重疊）。"""
    lo = float("-inf") if lo is None else lo
    hi = float("inf") if hi is None else hi
    value_hi = float("inf") if value_hi is None else value_hi
    if lo <= value_lo and value_hi <= hi:
        return True
    if value_hi < lo or value_lo > hi:
        return False
    return None


def facet_eval(label: dict, facts: dict, registry) -> tuple[str, list[str]]:
    violations, unknowns = [], []

    def check(name: str, result):
        (violations if result is False else unknowns if result is None else []).append(name)

    # 戶籍／居住
    residence = label.get("residence")
    if isinstance(residence, list):
        basis = label.get("residence_basis", "household")
        cities = set(residence)
        household = facts["household_city"]
        if basis == "current":
            city = facts["current_city"]
            check("residence", None if city is None else city in cities)
        elif basis == "either":
            options = [c for c in (household, facts["current_city"]) if c]
            if any(c in cities for c in options):
                check("residence", True)
            else:
                check("residence", False if (facts["household_known"] and facts["current_city"]) else None)
        elif basis == "school":
            city = facts.get("school_city")
            check("residence", None if city is None else city in cities)
        else:
            if household is None:
                check("residence", False if facts["household_known"] else None)  # 已知沒有臺灣戶籍 → 不符；沒提供 → 未知
            else:
                check("residence", household in cities)
    # 年齡（本人或代子女）
    age_rule = label.get("age")
    via_child = bool(label.get("via_child"))
    children = facts.get("children")
    if age_rule:
        lo, hi = age_rule
        if facts["age"] is not None:
            self_ok = _range_vs(lo, hi, facts["age"], facts["age"])
        elif facts.get("age_range"):
            self_ok = _range_vs(lo, hi, facts["age_range"][0], facts["age_range"][1])
        else:
            self_ok = None
        child_ok = False
        if via_child:
            child_ok = None if children is None else any(_range_vs(lo, hi, c, c) for c in children)
        if self_ok is True or child_ok is True:
            check("age", True)
        elif self_ok is False and child_ok is False:
            check("age", False)
        else:
            check("age", None)
    # 學制與在學
    levels = label.get("education")
    child_levels = facts.get("child_levels")
    if levels or label.get("student") is True:
        if facts["education_level"]:
            self_ok = (facts["education_level"] in levels) if levels else True
            if facts["student"] is False:
                self_ok = False
        elif facts.get("education_candidates"):
            inside = [lvl in levels for lvl in facts["education_candidates"]] if levels else [True]
            self_ok = True if all(inside) else False if not any(inside) else None
        elif facts["student"] is False:
            self_ok = False
        else:
            self_ok = None
        child_ok = False
        if via_child:
            child_ok = None if child_levels is None else any((lvl in levels) if levels else True for lvl in child_levels)
        check("education", True if (self_ok is True or child_ok is True) else False if (self_ok is False and child_ok is False) else None)
    if label.get("student") is False:
        check("not_student", None if facts["student"] is None else facts["student"] is False)
    # 身分
    tags = Tags(facts, registry)
    for tag in label.get("identity_all") or []:
        check(f"identity:{tag}", tags.state(tag))
    for group in label.get("identity_any") or []:
        states = [tags.state(tag) for tag in group]
        check(f"identity_any:{'/'.join(group)}", True if True in states else False if all(s is False for s in states) else None)
    for tag in label.get("identity_exclude") or []:
        state = tags.state(tag)
        check(f"exclude:{tag}", None if state is None else not state)
    # 國籍與其他屬性
    if label.get("nationality"):
        value = facts["attrs"].get("applicant.nationality")
        check("nationality", None if value is None else value == label["nationality"])
    for attr, expected in (label.get("attrs") or {}).items():
        value = facts["attrs"].get(attr)
        check(f"attr:{attr}", None if value is None else value == expected)
    if violations:
        return "ineligible", violations
    if unknowns:
        return "unknown", unknowns
    return "eligible", []


def facets_from_label(label: dict) -> list[dict]:
    """黃金標註 → eligibility_core facets（全部 confirmed）；也用來和建出來的骨幹比對。"""
    facets: list[dict] = []
    residence = label.get("residence")
    if residence == "national":
        facets.append({"kind": "residence", "cities": []})
    elif isinstance(residence, list):
        facets.append({"kind": "residence", "cities": residence, "basis": label.get("residence_basis", "household")})
    via_child = bool(label.get("via_child"))
    if label.get("age"):
        facets.append({"kind": "age", "min": label["age"][0], "max": label["age"][1], "via_child": via_child})
    if label.get("education"):
        facets.append({"kind": "education", "levels": label["education"], "via_child": via_child})
    elif label.get("student") is True:
        facets.append({"kind": "student", "value": True, "via_child": via_child})
    if label.get("student") is False:
        facets.append({"kind": "attr", "attribute_id": "applicant.is_student", "value": False})
    for tag in label.get("identity_all") or []:
        facets.append({"kind": "identity_any", "tags": [tag]})
    for group in label.get("identity_any") or []:
        facets.append({"kind": "identity_any", "tags": list(group)})
    if label.get("identity_exclude"):
        facets.append({"kind": "identity_exclude", "tags": list(label["identity_exclude"])})
    if label.get("nationality"):
        facets.append({"kind": "nationality", "value": label["nationality"]})
    for attr, value in (label.get("attrs") or {}).items():
        facets.append({"kind": "attr", "attribute_id": attr, "value": value})
    return [{**f, "status": "confirmed", "signals": ["gold"]} for f in facets]


# ============================================================ 系統輸出
def system_output(persona_input: dict, records: list[dict], labeled: set[str], registry, settings) -> dict[str, dict]:
    profile = Profile.from_dict(persona_input, registry)
    candidates, excluded = hard_filter_candidates(records, profile, registry, settings)
    engine = MatchingEngine(registry=registry)
    items = engine.match_all(candidates, profile, use_llm=False) + [engine.match_one(r, profile, use_llm=False) for r in excluded]
    ranking = rank(items, profile, registry=registry)
    deadline = {x["benefit_id"] for x in ranking["removed"] if x.get("funnel_stage") == "removed_deadline"}
    out = {}
    for item in items:
        if item.benefit_id not in labeled:
            continue
        tier = getattr(item, "tier", None)
        if tier is None:
            tier = "tier1" if item.status == "high_match" else "tier2" if item.status == "possible_match" else "hidden"
        if item.is_overview:
            tier = "hidden"
        if item.benefit_id in deadline:
            tier = "deadline"
        out[item.benefit_id] = {"tier": tier, "status": item.status, "explanation": item.explanation[:4]}
    return out


def evaluate(mode: str, personas: list[dict], labels: dict[str, dict], records: list[dict], registry, settings, details: int) -> dict:
    labeled = set(labels)
    present = {r["_id"] for r in records}
    counts = Counter()
    per_persona = defaultdict(Counter)
    samples = defaultdict(list)
    for persona in personas:
        truth = truth_facts(persona)
        if mode == "dashboard":
            engine_input = to_matching_profile(wizard_profile(persona))
        else:
            engine_input = engine_input_from_truth(truth)
        view = facts_from_engine_input(engine_input)
        outputs = system_output(engine_input, records, labeled, registry, settings)
        for benefit_id, label in labels.items():
            t_label, t_reasons = facet_eval(label, truth, registry)
            v_label, v_reasons = facet_eval(label, view, registry)
            if t_label == "unknown":  # 真實情況仍無法判斷（黃金標註缺欄位）→ 不計
                counts["gold_unknown"] += 1
                continue
            output = outputs.get(benefit_id, {"tier": "absent" if benefit_id not in present else "hidden", "status": "absent"})
            tier = output["tier"]
            if tier == "deadline":
                counts["deadline"] += 1
                continue
            shown = tier in ("tier1", "tier2")
            key = None
            if t_label == "eligible":
                counts["truth_eligible"] += 1
                if tier == "tier1":
                    counts["eligible_tier1"] += 1
                elif tier == "tier2":
                    counts["eligible_tier2"] += 1
                else:
                    key = "miss"
            else:
                counts["truth_ineligible"] += 1
                if v_label == "ineligible" and shown:
                    key = "avoidable_wrong"
                elif tier == "tier1":
                    key = "wrong_tier1"
                elif shown:
                    counts["needs_info_tier2"] += 1
                else:
                    counts["ineligible_hidden"] += 1
            if tier == "tier1":
                counts["tier1"] += 1
            if shown:
                counts["shown"] += 1
            if key:
                counts[key] += 1
                per_persona[persona["id"]][key] += 1
                if len(samples[key]) < details:
                    samples[key].append(f"{persona['id']} × {label['title'][:30]} → 系統 {tier}/{output['status']}；真實 {t_label} {t_reasons[:2]}；系統可見 {v_label} {v_reasons[:2]}")
    c = counts
    ratio = lambda a, b: f"{a}/{b} ({100 * a / b:.1f}%)" if b else f"{a}/0"
    summary = {
        "mode": mode,
        "漏掉（真實符合卻不顯示）": ratio(c["miss"], c["truth_eligible"]),
        "可避免誤推（資料足以排除卻顯示）": ratio(c["avoidable_wrong"], c["truth_ineligible"]),
        "誤標符合（不符卻標 tier1）": ratio(c["wrong_tier1"], c["tier1"]),
        "tier1 準確率": ratio(c["eligible_tier1"], c["tier1"]),
        "顯示清單中真實符合的比例": ratio(c["eligible_tier1"] + c["eligible_tier2"], c["shown"]),
        "真實符合的放在 tier1": ratio(c["eligible_tier1"], c["truth_eligible"]),
        "不符但資料不足而放 tier2（可接受）": c["needs_info_tier2"],
        "計入組數": c["truth_eligible"] + c["truth_ineligible"],
    }
    return {"summary": summary, "counts": dict(counts), "samples": samples, "per_persona": per_persona}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--details", type=int, default=0)
    parser.add_argument("--labels", default="benefit_facets", help="benefit_facets（調整規則用的黃金集）｜holdout_facets（保留集，只驗證不調整）")
    parser.add_argument("--out", default="")
    parser.add_argument("--mode", choices=["dashboard", "complete", "both"], default="both")
    parser.add_argument("--core", choices=["db", "rebuild", "oracle", "none"], default="db", help="db＝資料庫裡建好的骨幹；rebuild＝用目前程式與已存的 AI 投票在記憶體重算（不寫入）；oracle＝以黃金標註當骨幹（分層設計的上限）；none＝舊引擎")
    args = parser.parse_args()
    registry, settings = get_registry(), get_settings()
    labels = {row["id"]: row for row in yaml.safe_load((GOLD / f"{args.labels}.yaml").read_text(encoding="utf-8"))["labels"] if not row.get("skip")}
    personas = yaml.safe_load((GOLD / "personas.yaml").read_text(encoding="utf-8"))["personas"]
    records = load_records(get_db())
    for record in records:
        if args.core == "none":
            record.pop("eligibility_core", None)
        elif args.core == "oracle" and record["_id"] in labels:
            record["eligibility_core"] = {"version": 1, "facets": facets_from_label(labels[record["_id"]])}
        elif args.core == "rebuild" and record["_id"] in labels:
            from app.services.core_builder import build_core

            full = get_db().benefits.find_one({"_id": record["_id"]})
            record["eligibility_core"] = build_core(full, llm_output=(full.get("eligibility_core") or {}).get("llm"))
    lines = ["# 媒合回測（黃金集）", "", f"- 標註檔 {args.labels}：補助 {len(labels)} 筆 × 使用者 {len(personas)} 人；骨幹來源：{args.core}", ""]
    modes = ["dashboard", "complete"] if args.mode == "both" else [args.mode]
    for mode in modes:
        result = evaluate(mode, personas, labels, records, registry, settings, args.details)
        print(f"\n===== {mode}")
        lines.append(f"## {'儀表板實際輸入' if mode == 'dashboard' else '完整正確輸入'}")
        lines.append("")
        for key, value in result["summary"].items():
            if key == "mode":
                continue
            print(f"  {key}: {value}")
            lines.append(f"- {key}：{value}")
        lines.append("")
        for key, rows in result["samples"].items():
            print(f"  -- {key}")
            for row in rows:
                print("     ", row)
    if args.out:
        Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
