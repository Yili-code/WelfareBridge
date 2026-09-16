"""資格骨幹建立：多個獨立訊號投票，一致的才算「確認」，只有確認過的骨幹條件能讓媒合排除補助。

訊號來源（每個來源最多一票）：
    structure  發布機關的層級與轄區（地方政府 → 該縣市；中央部會 → 全國）
    title      標題中的縣市、身分、學制、年齡字樣
    text       原文中的「設籍／居住於本市」「就讀國小」等明確句型
    rules      抽取管線的 simple 規則（非推定、confidence ≥ 門檻）
    llm        本地 AI（每個值都要附原文引用，驗證不過即丟棄；見 llm/core_extract.py）
投票：同一類條件的候選依相容性分群；票數（不同來源數）最多的一群勝出，≥ 2 → confirmed，1 → uncertain。
輸出存在 record["eligibility_core"]（媒合端判斷見 matching/eligibility_core.py）。
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

from ..registry import Registry, get_registry
from .normalization import CITIES, chinese_to_int, find_cities, normalize_city

CORE_VERSION = 1
LOCAL_PROVIDERS = {"local_government", "township"}
# 這些類別的受補助者一定是在學學生（或其子女）；education_subsidy 含幼兒園補助、兒少帳戶，不列入
STUDENT_CATEGORIES = {"scholarship", "student_aid", "tuition_waiver", "emergency_aid_student", "student_loan", "study_abroad"}
CENTRAL_AGENCY_RE = re.compile(r"(衛生福利部|勞動部|教育部|內政部|國防部|國軍退除役官兵輔導委員會|原住民族委員會|客家委員會|行政院|國家發展委員會|文化部|經濟部|農業部|僑務委員會|社會及家庭署|勞動力發展署|勞工保險局|國民健康署|中央健康保險署|國家住宅及都市更新中心|中央)")
NUM = r"(\d{1,3}|[零一二三四五六七八九十]{1,3})"
LOCAL_PLACE = r"(本市|本縣|本鄉|本鎮|本區|本島|(?:臺|台)?[一-鿿]{1,2}[市縣])"
RESIDENCE_RE = re.compile(r"(?P<verb>設籍|戶籍(?:設|設於|在)?|實際居住|現居|居住|住居|寄居)(?:於|在|並居住於|且居住於)?\s*" + LOCAL_PLACE)
SCHOOL_RE = re.compile(r"就讀(?:於)?\s*" + LOCAL_PLACE + r"[^。；\n]{0,12}?學校")
ECONOMIC_TAGS = {"low_income", "middle_low_income", "economic_hardship"}

# 學制字樣 → 學制（長的先比對）
LEVEL_PHRASES: list[tuple[str, list[str]]] = [
    ("高級中等以上", ["senior_high", "vocational_high", "junior_college", "university", "master", "doctoral"]),
    ("高中職以上", ["senior_high", "vocational_high", "junior_college", "university", "master", "doctoral"]),
    ("中等以上學校", ["junior_high", "senior_high", "vocational_high", "junior_college", "university", "master", "doctoral"]),
    ("大專以上", ["junior_college", "university", "master", "doctoral"]),
    ("大專校院", ["junior_college", "university", "master", "doctoral"]),
    ("大專院校", ["junior_college", "university", "master", "doctoral"]),
    ("國民中小學", ["elementary", "junior_high"]),
    ("國中小", ["elementary", "junior_high"]),
    ("國民小學", ["elementary"]),
    ("國民中學", ["junior_high"]),
    ("高中職", ["senior_high", "vocational_high"]),
    ("高級中等學校", ["senior_high", "vocational_high"]),
    ("研究所", ["master", "doctoral"]),
    ("碩士", ["master"]),
    ("博士", ["doctoral"]),
    ("五專", ["junior_college"]),
    ("二專", ["junior_college"]),
    ("專科", ["junior_college"]),
    ("科技大學", ["university"]),
    ("四技", ["university"]),
    ("二技", ["university"]),
    ("國小", ["elementary"]),
    ("國中", ["junior_high"]),
    ("大學生", ["university"]),
    ("大學部", ["university"]),
]
BANDS = {"elementary": "elementary", "junior_high": "junior_high", "senior_high": "senior", "vocational_high": "senior", "junior_college": "college", "university": "college", "master": "graduate", "doctoral": "graduate"}
CHILD_TITLE_RE = re.compile(r"(兒童|幼兒|嬰|育兒|托育|新生兒|出生|生育|兒少|少年|學童|幼童|早期療育|發展遲緩|子女)")
# 標題括號裡的「低收與中低收免費」是加碼說明，不是資格；「低收入戶救助／資格審查」是申請取得身分本身
TITLE_NOTE_RE = re.compile(r"[（(【\[][^）)】\]]*[）)】\]]")
STATUS_APPLICATION_RE = re.compile(r"(低收入戶|中低收入戶|特殊境遇家庭)(?:及中低收入戶)?(?:救助|資格|認定|審查|審核|申請|調查|扶助){1,3}(?:作業|實施計畫|計畫)?$")
ELDERLY_TITLE_RE = re.compile(r"(老人|長者|敬老|老年|銀髮|長青)")
TITLE_AGE_RANGE_RE = re.compile(NUM + r"\s*(?:歲)?\s*(?:至|到|~|～|-)\s*(未滿)?\s*" + NUM + r"\s*歲")
TITLE_UNDER_RE = re.compile(r"未滿\s*" + NUM + r"\s*歲")
TEXT_AGE_MIN_RE = re.compile(r"(?:年滿|年齡(?:在)?)\s*" + NUM + r"\s*歲以上|" + NUM + r"\s*歲以上(?:之|的)?(?:老人|長者|民眾|市民|縣民|國民|者)")
NATIONALITY_RE = re.compile(r"(?:具|有|具有)(?:中華民國|我國|本國)國籍|(?:中華民國|我國|本國)國籍(?:之|者)")
ATTR_TITLE_CUES: list[tuple[re.Pattern, str, Any]] = [
    (re.compile(r"租金補貼|租屋補助|租金補助|租屋補貼|租賃住宅補貼"), "housing.tenure", "rent"),
    (re.compile(r"失業給付|職業訓練生活津貼"), "employment.involuntary_separation", True),
    (re.compile(r"家庭照顧者"), "care.is_primary_caregiver", True),
    (re.compile(r"臨時工作津貼|求職交通補助|跨域就業|缺工就業獎勵|照顧服務就業獎勵|就業促進津貼|職業訓練生活津貼"), "employment.status", "unemployed"),
    (re.compile(r"減班休息"), "employment.status", "employed"),
]
TEXT_UNEMPLOYED_RE = re.compile(r"(?:失業|待業)(?:者|勞工|期間|週數)|辦理求職登記|向公立就業服務機構(?:辦理)?求職")
# 條件句的語氣：加碼、優先、擇一、條列其中一款 → 這個身分／年齡不是每位申請人都要具備
CAVEAT_RE = re.compile(r"優先|之一|之ㄧ|下列|任一|其中一|家屬|免費|減免|加發|加碼|另發|另補助|酌增|提高補助|增加補助")
NON_STUDENT_RE = re.compile(r"不具學生身分|非在學|社會青年|已畢業|應屆畢業|畢業生")
PAYOUT_ITEM_RE = re.compile(r"每人每月(?:補助|發給)|每月(?:補助|發給)新臺幣|每名(?:補助|發給)新臺幣")
RECEIVER_RE = re.compile(r"(?:領取|領有|接受|申領|使用)[^，。；]{0,24}(?:補助|津貼|安置|扶助|給付|服務)|(?:補助|津貼|安置費|給付)者")
TARGET_END = r"(?:者|老人|長者|遊民|民眾|家庭|兒童|少年|學生)[。；;．.]?$"
PRESCHOOL_RE = re.compile(r"入國小前|入國民小學前|學齡前|未達就學年齡|幼兒園")
PRIORITY_RE = re.compile(r"優先|免費|減免|加發|加碼|另發|另補助|酌增|提高補助|增加補助")
LIST_ITEM_RE = re.compile(r"^\s*[（(]?[一二三四五六七八九十0-9]{1,2}[）)、.．]")


def _int(token: str | None) -> int | None:
    if not token:
        return None
    value = chinese_to_int(token)
    return value if value is not None and 0 <= value <= 120 else None


def _jurisdiction(record: dict) -> str | None:
    title_cities = [c for c in find_cities(record.get("title", "")) if c in CITIES]
    if len(title_cities) == 1:
        return title_cities[0]
    region = normalize_city(record.get("provider_region") or "")
    return region if region in CITIES else None


# ============================================================ 規則式訊號
def structure_signals(record: dict) -> list[dict]:
    out: list[dict] = []
    region = normalize_city(record.get("provider_region") or "")
    if record.get("provider_type") in LOCAL_PROVIDERS and region in CITIES:
        out.append({"kind": "residence", "cities": [region], "basis": "household"})
    elif record.get("provider_type") == "central_government":
        out.append({"kind": "residence", "cities": []})
    if record.get("category") in STUDENT_CATEGORIES:
        out.append({"kind": "student", "value": True, "via_child": bool(CHILD_TITLE_RE.search(record.get("title", "") or ""))})
    return [{**p, "source": "structure"} for p in out]


def title_signals(record: dict, registry: Registry) -> list[dict]:
    title = record.get("title", "") or ""
    out: list[dict] = []
    cities = [c for c in find_cities(title) if c in CITIES]
    if cities:
        out.append({"kind": "residence", "cities": cities, "basis": "household"})
    elif CENTRAL_AGENCY_RE.search(title):
        out.append({"kind": "residence", "cities": []})
    # 年齡
    via_child = bool(CHILD_TITLE_RE.search(title))
    match = TITLE_AGE_RANGE_RE.search(title)
    if match:
        low, high = _int(match.group(1)), _int(match.group(3))
        if low is not None and high is not None:
            out.append({"kind": "age", "min": low, "max": high - 1 if match.group(2) else high, "via_child": via_child})
    elif (under := TITLE_UNDER_RE.search(title)) and _int(under.group(1)):
        out.append({"kind": "age", "min": 0, "max": _int(under.group(1)) - 1, "via_child": via_child})
    elif ELDERLY_TITLE_RE.search(title) and not CHILD_TITLE_RE.search(title):
        out.append({"kind": "age", "min": 65, "max": None, "via_child": False})
    elif via_child and not re.search(r"學生|學童|就學|學雜費|獎學金|助學金", title):
        # 兒少／育兒方案：標題沒寫年齡時先標成「未成年子女（或本人未成年）」，其他來源有確切年齡時由投票取代
        out.append({"kind": "age", "min": 0, "max": 17, "via_child": True, "hint": True})
    # 在學（標題寫明學生、就學）
    if re.search(r"學生|學童|就學|學雜費|獎學金|助學金", title) and not re.search(r"幼兒|學前|幼兒園|托育|托嬰", title):  # 幼兒園「就學補助」的幼兒不算在學學生
        out.append({"kind": "student", "value": True, "via_child": via_child})
    # 學制
    levels = _levels_in(title)
    if levels:
        out.append({"kind": "education", "levels": levels, "via_child": via_child})
    # 身分（去掉括號說明；申請身分本身的頁面不算）
    identity_title = TITLE_NOTE_RE.sub("", title) or title
    for tags in ([] if STATUS_APPLICATION_RE.search(identity_title.strip()) else _identity_groups_in(identity_title, registry)):
        out.append({"kind": "identity_any", "tags": tags})
    for pattern, attribute_id, value in ATTR_TITLE_CUES:
        if pattern.search(title):
            out.append({"kind": "attr", "attribute_id": attribute_id, "value": value})
    return [{**p, "source": "title"} for p in out]


def _levels_in(text: str) -> list[str]:
    found: list[str] = []
    remaining = text
    for phrase, levels in LEVEL_PHRASES:
        if phrase in remaining:
            remaining = remaining.replace(phrase, "　")
            found.extend(level for level in levels if level not in found)
    return found


def _identity_groups_in(title: str, registry: Registry) -> list[list[str]]:
    remaining = title
    spans: list[tuple[int, int, str]] = []
    aliases = sorted(((alias, tag.id) for tag in registry.tags.values() if tag.id not in {"elderly", "yami"} for alias in [tag.label, *tag.aliases] if len(alias) >= 2), key=lambda item: -len(item[0]))
    for alias, tag_id in aliases:
        start = remaining.find(alias)
        while start >= 0:
            spans.append((start, start + len(alias), tag_id))
            remaining = remaining[:start] + "　" * len(alias) + remaining[start + len(alias):]
            start = remaining.find(alias)
    if "中低收入" in title and not any(t == "middle_low_income" for _s, _e, t in spans):
        index = title.find("中低收入")
        spans.append((index, index + 4, "middle_low_income"))
    spans.sort()
    groups: list[list[str]] = []
    previous_end = None
    for start, end, tag_id in spans:
        gap = title[previous_end:start] if previous_end is not None else None
        # 「低收入戶及中低收入戶」「單親及弱勢家庭」：相連的身分是擇一；「清寒原住民」沒有連接詞是同時具備
        if groups and gap is not None and len(gap) <= 3 and re.search(r"及|與|或|、|暨|/|／|家庭|戶", gap) and not re.search(r"[\u4e00-\u9fff]{3}", gap.replace("家庭", "").replace("戶", "")):
            if tag_id not in groups[-1]:
                groups[-1].append(tag_id)
        elif not any(tag_id in group for group in groups):
            groups.append([tag_id])
        previous_end = end
    economic = [t for group in groups for t in group if t in ECONOMIC_TAGS]
    merged = [group for group in groups if not (set(group) <= ECONOMIC_TAGS)]
    if economic and not any(set(group) & ECONOMIC_TAGS for group in merged):
        merged.append(list(dict.fromkeys(economic)))  # 標題並列的經濟身分是「其一」
    return [group for group in merged if group != ["disadvantaged"]]  # 只寫「弱勢」太籠統，不單獨當條件


def text_signals(record: dict) -> list[dict]:
    text = record.get("original_text") or ""
    out: list[dict] = []
    jurisdiction = _jurisdiction(record)
    region = normalize_city(record.get("provider_region") or "")
    cities: list[str] = []
    verbs: set[str] = set()
    for match in RESIDENCE_RE.finditer(text):
        place = match.group(2)
        city = jurisdiction if place in {"本市", "本縣"} else region if place in {"本鄉", "本鎮", "本區", "本島"} else normalize_city(place)
        if city not in CITIES:
            continue
        # 「戶籍所在地之區公所」「居住地」這類不是資格；RESIDENCE_RE 已要求後面接縣市
        verbs.add("household" if match.group("verb").startswith(("設籍", "戶籍")) else "current")
        if city not in cities:
            cities.append(city)
    if cities:
        basis = "either" if verbs == {"household", "current"} else verbs.pop()
        out.append({"kind": "residence", "cities": cities, "basis": basis})
    for match in SCHOOL_RE.finditer(text):
        place = match.group(1)
        city = jurisdiction if place in {"本市", "本縣"} else normalize_city(place)
        if city in CITIES:
            out.append({"kind": "residence", "cities": [city], "basis": "school"})
            break
    ages = [_int(m.group(1) or m.group(2)) for m in TEXT_AGE_MIN_RE.finditer(text)]
    ages = [a for a in ages if a is not None and a >= 50]
    if ages and len(set(ages)) == 1:
        out.append({"kind": "age", "min": ages[0], "max": None, "via_child": False})
    if NATIONALITY_RE.search(text):
        out.append({"kind": "nationality", "value": "roc"})
    unemployed = TEXT_UNEMPLOYED_RE.search(text)
    if unemployed:
        out.append({"kind": "attr", "attribute_id": "employment.status", "value": "unemployed", "quote": _sentence(text, unemployed.start(), unemployed.end())})
    return [{**p, "source": "text"} for p in out]


def _excerpt(rule: dict) -> str:
    return str((rule.get("evidence") or {}).get("excerpt") or rule.get("condition_text") or "")


def rule_signals(record: dict, registry: Registry, min_confidence: float = 0.8) -> list[dict]:
    rules = [r for r in record.get("rules") or [] if r.get("complexity") == "simple" and not r.get("inferred") and float(r.get("confidence", 0)) >= min_confidence and r.get("role") in {"required", "exclusion"}]
    out: list[dict] = []
    residence: dict[str, list[str]] = {}
    for rule in rules:
        attribute_id, operator, value = rule.get("attribute_id"), rule.get("operator"), rule.get("value")
        if attribute_id in {"residence.household_city", "residence.current_city", "education.school_city"} and operator in {"in", "="}:
            values = value if isinstance(value, list) else [value]
            basis = {"residence.household_city": "household", "residence.current_city": "current", "education.school_city": "school"}[attribute_id]
            for city in values:
                city = normalize_city(str(city))
                if city in CITIES:
                    residence.setdefault(basis, [])
                    if city not in residence[basis]:
                        residence[basis].append(city)
    if residence:
        cities = list(dict.fromkeys(c for values in residence.values() for c in values))
        basis = "either" if {"household", "current"} <= set(residence) else next(iter(residence))
        out.append({"kind": "residence", "cities": cities, "basis": basis})
    # 年齡：本人
    low = high = None
    child_low = child_high = None
    age_quote = ""
    for rule in rules:
        attribute_id, operator, value = rule.get("attribute_id"), rule.get("operator"), rule.get("value")
        if attribute_id not in {"applicant.age", "family.youngest_child_age"} or rule.get("role") != "required":
            continue
        bounds = _bounds(operator, value)
        if bounds is None:
            continue
        if attribute_id == "applicant.age":
            if (bounds[0] is not None and high is not None and bounds[0] > high) or (bounds[1] is not None and low is not None and bounds[1] < low):
                return [{**p, "source": "rules"} for p in out]  # 規則自相矛盾（65 歲以上且未滿 18 歲）：年齡規則不可信
            low = bounds[0] if bounds[0] is not None else low
            high = bounds[1] if bounds[1] is not None else high
            age_quote = age_quote or _excerpt(rule)
        else:
            child_low = bounds[0] if bounds[0] is not None else child_low
            child_high = bounds[1] if bounds[1] is not None else child_high
    if low is not None or high is not None:
        out.append({"kind": "age", "min": low, "max": high, "via_child": False, "quote": age_quote})
    elif child_low is not None or child_high is not None:
        out.append({"kind": "age", "min": child_low if child_low is not None else 0, "max": child_high, "via_child": True})
    # 學制、在學、身分、其他
    groups: dict[str, list[str]] = {}
    group_quotes: dict[str, str] = {}
    for rule in rules:
        attribute_id, operator, value = rule.get("attribute_id"), rule.get("operator"), rule.get("value")
        if attribute_id == "education.level" and operator == "in" and rule.get("role") == "required" and isinstance(value, list):
            out.append({"kind": "education", "levels": [v for v in value if v in BANDS], "via_child": False, "quote": _excerpt(rule)})
        elif attribute_id == "applicant.is_student" and operator == "=" and value is True and rule.get("role") == "required":
            out.append({"kind": "student", "value": True, "via_child": False})
        elif attribute_id == "identity.tags":
            tags = [t for t in (value if isinstance(value, list) else [value]) if t in registry.tags]
            if operator in {"contains", "in"} and rule.get("role") == "required":
                if tags == ["elderly"]:
                    out.append({"kind": "age", "min": 65, "max": None, "via_child": False, "quote": _excerpt(rule)})
                    continue
                key = rule.get("group_id") or rule.get("id", "")
                group = groups.setdefault(key, [])
                group.extend(t for t in tags if t not in group and t != "elderly")
                group_quotes.setdefault(key, _excerpt(rule))
            elif operator == "not_in":
                out.append({"kind": "identity_exclude", "tags": tags, "quote": _excerpt(rule)})
        elif attribute_id == "applicant.nationality" and operator in {"in", "="} and rule.get("role") == "required":
            values = value if isinstance(value, list) else [value]
            if values == ["roc"] or values == ["foreign"]:
                out.append({"kind": "nationality", "value": values[0]})
        elif attribute_id in {"employment.involuntary_separation", "care.needs_care", "care.is_primary_caregiver"} and operator == "=" and rule.get("role") == "required":
            out.append({"kind": "attr", "attribute_id": attribute_id, "value": value, "quote": _excerpt(rule)})
        elif attribute_id == "housing.tenure" and operator in {"in", "="} and rule.get("role") == "required" and (value == "rent" or value == ["rent"]):
            out.append({"kind": "attr", "attribute_id": attribute_id, "value": "rent"})
    for key, tags in groups.items():
        if tags:
            out.append({"kind": "identity_any", "tags": tags, "quote": group_quotes.get(key, "")})
    return [{**p, "source": "rules"} for p in out]


def _bounds(operator: str, value: Any) -> tuple[int | None, int | None] | None:
    try:
        if operator == "between" and isinstance(value, list) and len(value) == 2:
            return int(float(value[0])), int(float(value[1]))
        number = float(value)
    except (TypeError, ValueError):
        return None
    return {">=": (int(number), None), ">": (int(number) + 1, None), "<=": (None, int(number)), "<": (None, int(number) - 1 if number == int(number) else int(number))}.get(operator)


# ============================================================ 條件句語氣
def _sentence(text: str, start: int, end: int) -> str:
    left = max(text.rfind(mark, 0, start) for mark in "。；\n") + 1
    rights = [i for i in (text.find(mark, end) for mark in "。；\n") if i != -1]
    return text[left : min(rights) if rights else len(text)].strip()


def _context(quote: str, text: str) -> str:
    quote = (quote or "").strip()
    if not quote:
        return ""
    index = text.find(quote[:24])
    return _sentence(text, index, index + len(quote)) if index >= 0 else quote


def _sibling_group(quote: str, text: str, keys: list[str]) -> str:
    """身分所在的那一行若和上下行並列（都是「…者／老人／遊民」這種申請對象），而相鄰行沒提到該身分 → 回傳那一行（擇一的其他對象）。"""
    index = text.find((quote or "").strip()[:24])
    if index < 0 or not keys:
        return ""
    lines = text.split("\n")
    offset = 0
    for position, line in enumerate(lines):
        if offset <= index <= offset + len(line):
            break
        offset += len(line) + 1
    else:
        return ""
    if not re.search(TARGET_END, lines[position].strip()):
        return ""
    for neighbor in (lines[position - 1] if position else "", lines[position + 1] if position + 1 < len(lines) else ""):
        candidate = neighbor.strip()
        if len(candidate) >= 4 and re.search(TARGET_END, candidate) and not any(k in candidate for k in keys):
            return candidate
    return ""


def _aliases(registry: Registry, tags: list[str]) -> list[str]:
    out: list[str] = []
    for tag_id in tags:
        tag = registry.tags.get(tag_id)
        if tag:
            out.extend(a for a in [tag.label, *tag.aliases] if len(a) >= 2)
    if "middle_low_income" in tags or "low_income" in tags:
        out.extend(["低收", "中低收"])
    return out


def caveat(facet: dict, quotes: list[str], text: str, registry: Registry) -> str:
    """回傳降級原因（空字串＝沒有疑慮）。只看支持這個 facet 的原文句子。"""
    kind = facet["kind"]
    if kind not in {"identity_any", "identity_exclude", "age", "education", "student", "attr"}:
        return ""
    keys = _aliases(registry, facet.get("tags") or []) if kind in {"identity_any", "identity_exclude"} else ["歲"] if kind == "age" else []
    for quote in quotes:
        sentence = _context(quote, text)
        if not sentence:
            continue
        if kind == "identity_exclude":
            # 「領取身心障礙者日間照顧補助者不予補助」排除的是領過某項補助的人，不是具備該身分的人
            if RECEIVER_RE.search(sentence):
                return "原文排除的是已領其他補助者，不是身分本身"
            continue
        sibling = _sibling_group(quote, text, keys) if kind == "identity_any" else ""
        if sibling:
            return f"原文另列「{sibling[:24]}」等其他申請對象，身分可能只是其中之一"
        plain_title = TITLE_NOTE_RE.sub("", text.split("\n", 1)[0])  # 括號裡的「低收與中低收免費」仍算加碼說明
        marker = next((m for m in CAVEAT_RE.finditer(sentence) if m.group(0) not in plain_title), None)  # 「學雜費減免」方案裡的「減免」是給付本身，不是加碼
        if kind in {"education", "student"} and PRESCHOOL_RE.search(sentence):
            return "原文說的是入學前的幼兒"
        if marker:
            return f"原文有「{marker.group(0)}」，可能是優先、加碼或擇一條件"
        if LIST_ITEM_RE.search(sentence):
            return "原文是條列的其中一款"
        if kind in {"identity_any", "age", "education", "student"} and PAYOUT_ITEM_RE.search(sentence):
            return "原文是某個給付項目的說明（同頁可能有多項補助）"
        if keys and "或" in sentence:
            for clause in re.split(r"[，,；：:]", sentence):
                if "或" not in clause or not any(k in clause for k in keys):
                    continue
                parts = [p for p in re.split(r"或|、", clause) if p.strip()]
                others = [p for p in parts if not any(k in p for k in keys) and len(re.findall(r"[\u4e00-\u9fff]", p)) >= 4]
                if others:
                    return f"原文「{clause.strip()[:30]}」列了其他選項，{'身分' if kind == 'identity_any' else '年齡'}可能只是其中之一"
        if kind == "age":
            ages = {int(n) for n in re.findall(r"(\d{1,3})\s*歲以上", sentence)}
            if len(ages) > 1:
                return "原文依身分列了不同的年齡門檻"
    if kind == "student":
        other = NON_STUDENT_RE.search(text)
        if other:
            return f"原文提到「{other.group(0)}」，非在學者也可能可以申請"
    return ""


# ============================================================ 投票
def _compatible(a: dict, b: dict) -> bool:
    kind = a["kind"]
    if kind == "residence":
        return set(a.get("cities") or []) == set(b.get("cities") or [])
    if kind == "age":
        return a.get("min") == b.get("min") and a.get("max") == b.get("max")
    if kind == "education":
        return {BANDS[l] for l in a.get("levels") or []} == {BANDS[l] for l in b.get("levels") or []}
    if kind in {"identity_any", "identity_exclude"}:
        return bool(set(a.get("tags") or []) & set(b.get("tags") or []))
    if kind == "nationality":
        return a.get("value") == b.get("value")
    if kind == "student":
        return True
    if kind == "attr":
        return a.get("attribute_id") == b.get("attribute_id") and a.get("value") == b.get("value")
    return a == b


def _via_child(cluster: list[dict], text: str) -> bool:
    """家長代子女申請：規則式訊號說是就算；只有本地 AI 說是時，標題要真的提到兒童／子女（模型常把大學獎學金標成子女申請）。"""
    if any(p.get("via_child") for p in cluster if p["source"] != "llm"):
        return True
    title = text.split("\n", 1)[0]
    return any(p.get("via_child") for p in cluster) and bool(CHILD_TITLE_RE.search(title) or re.search(r"家長|父母", title))


def _merge(cluster: list[dict], text: str = "", registry: Registry | None = None) -> dict:
    """同一群的候選合併成一個 facet；範圍取寬（避免因某一票較嚴而誤排除）。"""
    first = cluster[0]
    kind = first["kind"]
    facet: dict[str, Any] = {"kind": kind}
    if kind == "residence":
        facet["cities"] = list(first.get("cities") or [])
        if facet["cities"]:
            bases = {p.get("basis") or "household" for p in cluster}
            facet["basis"] = "school" if bases == {"school"} else "either" if len(bases - {"school"}) > 1 or "either" in bases else next(iter(bases - {"school"}), "household")
    elif kind == "age":
        facet.update({"min": first.get("min"), "max": first.get("max"), "via_child": _via_child(cluster, text)})
    elif kind == "education":
        facet["levels"] = [level for level in BANDS if any(level in (p.get("levels") or []) for p in cluster)]
        facet["via_child"] = _via_child(cluster, text)
    elif kind == "student":
        facet.update({"value": True, "via_child": _via_child(cluster, text)})
    elif kind in {"identity_any", "identity_exclude"}:
        tags: list[str] = []
        for proposal in cluster:
            tags.extend(t for t in proposal.get("tags") or [] if t not in tags)
        common = set(cluster[0].get("tags") or [])
        for proposal in cluster[1:]:
            common &= set(proposal.get("tags") or [])
        if kind == "identity_exclude":  # 排除身分取交集（只排除大家都同意的）
            tags = [t for t in tags if t in common] or tags
        elif common and len(common) < len(tags):
            facet["strict_tags"] = [t for t in tags if t in common]  # 各票都同意的身分才算「符合」；只在部分票裡的身分算「需確認」
        facet["tags"] = tags
    elif kind in {"nationality"}:
        facet["value"] = first.get("value")
    elif kind == "attr":
        facet.update({"attribute_id": first.get("attribute_id"), "value": first.get("value")})
    sources = list(dict.fromkeys(p["source"] for p in cluster))
    facet["signals"] = sources
    facet["status"] = "confirmed" if len(sources) >= 2 else "uncertain"
    quotes = [p.get("quote") for p in cluster if p.get("quote")]
    if quotes:
        facet["quote"] = quotes[0][:160]
    # 標題本身就寫明對象身分／條件（「身心障礙者輔具補助」「失業給付」）時，內文的「或」「下列之一」多半是細項，不降級
    title_backed = kind in {"identity_any", "attr"} and "title" in sources
    if facet["status"] == "confirmed" and text:
        reason = caveat(facet, quotes, text, registry or get_registry())
        marker = re.search(r"「(.+?)」", reason or "")
        if reason and title_backed and not (marker and PRIORITY_RE.search(marker.group(1))):
            reason = ""
        if reason:
            facet["status"] = "uncertain"
            facet["caveat"] = reason
    return facet


def _clusters(proposals: list[dict]) -> list[list[dict]]:
    clusters: list[list[dict]] = []
    for proposal in proposals:
        for cluster in clusters:
            if any(_compatible(proposal, member) for member in cluster):
                cluster.append(proposal)
                break
        else:
            clusters.append([proposal])
    return clusters


GATE_POLICY = os.environ.get("CORE_GATE_POLICY", "llm_gate")


def vote(proposals: list[dict], *, llm_ran: bool = False, policy: str | None = None, text: str = "", registry: Registry | None = None) -> list[dict]:
    """policy：
    default   單一來源的條件保留為 uncertain
    llm_gate  本地 AI 有跑成功時，AI 沒提到的單一來源身分／年齡／學制／其他條件視為雜訊丟掉（抽取規則常把加碼、文件、家人條件誤當資格）
    """
    policy = policy or GATE_POLICY
    facets: list[dict] = []
    by_kind: dict[str, list[dict]] = {}
    # 限定學制的每一票同時也是「須在學」的一票（和類別訊號一起決定在學條件）
    proposals = [*proposals, *({"kind": "student", "value": True, "via_child": p.get("via_child", False), "source": p["source"], "quote": p.get("quote", "")} for p in proposals if p["kind"] == "education")]
    for proposal in proposals:
        by_kind.setdefault(proposal["kind"], []).append(proposal)
    for kind, items in by_kind.items():
        clusters = sorted(_clusters(items), key=lambda c: -len({p["source"] for p in c}))
        if kind != "residence":
            # 黃金集回測：只有本地 AI 一票的身分／學制／其他條件 9 成是錯的（把文件、家人、加碼條件當資格），不採用；
            # 只有 AI 一票的年齡須通過數字對照（proposals_from_llm 已驗證）才保留
            def keep(cluster: list[dict]) -> bool:
                sources = {p["source"] for p in cluster}
                if len(sources) >= 2:
                    return True
                if sources == {"llm"}:
                    return kind == "age" and all(p.get("verified_numbers") for p in cluster)
                if sources == {"rules"}:
                    return not (policy == "llm_gate" and llm_ran)
                return True

            clusters = [c for c in clusters if keep(c)]
            if kind == "age" and any(not p.get("hint") for c in clusters for p in c):
                clusters = [c for c in clusters if any(not p.get("hint") for p in c)]  # 有確切年齡時，標題的「兒少方案」提示退場
            if not clusters:
                continue
        if kind in {"identity_any", "identity_exclude", "attr"}:
            # 可以同時有多個身分群組／屬性條件：每群各自成一個 facet
            facets.extend(_merge(c, text, registry) for c in clusters)
            continue
        best = clusters[0]
        best_votes = len({p["source"] for p in best})
        rivals = [c for c in clusters[1:] if len({p["source"] for p in c}) == best_votes]
        if rivals:
            # 同票數互相矛盾：不確認任何一方；保留較寬鬆的一方當提示（全國／較寬的年齡範圍）
            candidates = [best, *rivals]
            if kind == "residence":
                lenient = next((c for c in candidates if not c[0].get("cities")), None)
                strict = next((c for c in candidates if c[0].get("cities")), None)
                if lenient is not None and (strict is None or {p["source"] for p in lenient} != {"llm"}):
                    continue  # 有非 AI 的一票說全國（中央機關發布／標題是中央機關）：不設戶籍限制
                if lenient is not None:
                    # 縣市機關發布、原文沒明寫「設籍本縣」時，本地 AI 常判成全國。
                    # 全刪會讓別縣市的人看到 ✅；保留戶籍限制但標為需確認（仍不會被隱藏，只是不進 ✅）
                    merged = _merge(strict, text, registry)
                    merged.update({"status": "uncertain", "conflict": True, "caveat": f"由{strict[0]['cities'][0]}的機關發布，但原文沒寫明設籍限制"})
                    facets.append(merged)
                    continue
            merged = _merge(best, text, registry)
            merged["status"] = "uncertain"
            merged["conflict"] = True
            facets.append(merged)
            continue
        facets.append(_merge(best, text, registry))
    # 學制已確認就不需要另外的「在學」facet（學制本身就要求在學）
    if any(f["kind"] == "education" and f["status"] == "confirmed" for f in facets):
        facets = [f for f in facets if f["kind"] != "student"]
    return facets


def build_core(record: dict, *, llm_output: dict | None = None, registry: Registry | None = None, min_rule_confidence: float = 0.8) -> dict:
    from ..llm.core_extract import proposals_from_llm

    registry = registry or get_registry()
    proposals = [*structure_signals(record), *title_signals(record, registry), *text_signals(record), *rule_signals(record, registry, min_rule_confidence), *proposals_from_llm(llm_output, record)]
    facets = vote(proposals, llm_ran=bool(llm_output), text=f"{record.get('title', '')}\n{record.get('original_text') or ''}", registry=registry)
    plain_title = (TITLE_NOTE_RE.sub("", record.get("title", "")) or "").strip()
    if STATUS_APPLICATION_RE.search(plain_title):
        # 申請取得低收／中低收／特境身分本身的頁面：身分是審核結果，不是申請前提
        for facet in facets:
            if facet["kind"] == "identity_any" and set(facet.get("tags") or []) <= ECONOMIC_TAGS | {"special_circumstances"}:
                facet["status"], facet["caveat"] = "uncertain", "此頁是申請取得該身分，不以已具身分為前提"
    if "特殊境遇" in plain_title:
        # 特境家庭的各項扶助（緊急生活扶助、法律訴訟補助、子女教育補助…）在申請時一併依條件認定，不以已具特境身分為前提
        for facet in facets:
            if facet["kind"] == "identity_any" and facet.get("tags") == ["special_circumstances"]:
                facet["status"], facet["caveat"] = "uncertain", "特境扶助在申請時依條件認定，不以已具特境身分為前提"
    return {
        "version": CORE_VERSION,
        "facets": facets,
        "llm": llm_output,
        "llm_model": (llm_output or {}).get("_model"),
        "built_at": datetime.now(timezone.utc).replace(tzinfo=None),
    }
