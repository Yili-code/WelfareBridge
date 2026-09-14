"""快速輸入的規則式解析（v2）：「我是基隆人，海大資工大二，平均82分，沒有低收入戶，學費繳不出來」→ Profile。

只抽取明確寫出的資訊；每個值都附使用者原話摘錄。本地 AI（app/llm/fill.parse_profile）只在可用時補充，
輸出同樣經過登錄表型態檢查與「摘錄必須在原文」。
"""

from __future__ import annotations

import re

from ..registry import Registry, get_registry
from ..services.normalization import chinese_to_int, find_cities, fullwidth_to_halfwidth
from .profile import Profile

SCHOOL_ALIASES: dict[str, tuple[str, str]] = {
    "海大": ("國立臺灣海洋大學", "public"), "海洋大學": ("國立臺灣海洋大學", "public"), "臺灣海洋大學": ("國立臺灣海洋大學", "public"),
    "臺大": ("國立臺灣大學", "public"), "台大": ("國立臺灣大學", "public"), "臺灣大學": ("國立臺灣大學", "public"),
    "政大": ("國立政治大學", "public"), "清大": ("國立清華大學", "public"), "陽明交大": ("國立陽明交通大學", "public"), "交大": ("國立陽明交通大學", "public"),
    "成大": ("國立成功大學", "public"), "中央大學": ("國立中央大學", "public"), "中山大學": ("國立中山大學", "public"), "中興": ("國立中興大學", "public"),
    "師大": ("國立臺灣師範大學", "public"), "臺科大": ("國立臺灣科技大學", "public"), "台科大": ("國立臺灣科技大學", "public"), "北科大": ("國立臺北科技大學", "public"),
    "北大": ("國立臺北大學", "public"), "高科大": ("國立高雄科技大學", "public"), "東華": ("國立東華大學", "public"), "中正大學": ("國立中正大學", "public"),
    "淡江": ("淡江大學", "private"), "輔大": ("輔仁大學", "private"), "東海": ("東海大學", "private"), "逢甲": ("逢甲大學", "private"), "中原": ("中原大學", "private"),
    "元智": ("元智大學", "private"), "銘傳": ("銘傳大學", "private"), "文化大學": ("中國文化大學", "private"), "世新": ("世新大學", "private"), "東吳": ("東吳大學", "private"),
}
DEPARTMENT_ALIASES: dict[str, str] = {
    "資工": "資訊工程", "資訊工程": "資訊工程", "電機": "電機工程", "機械": "機械工程", "企管": "企業管理", "資管": "資訊管理", "財金": "財務金融", "會計": "會計", "法律": "法律",
    "外文": "外國語文", "護理": "護理", "醫學": "醫學", "土木": "土木工程", "化工": "化學工程", "材料": "材料工程", "生科": "生命科學", "航管": "航運管理", "輪機": "輪機工程",
    "食科": "食品科學", "光電": "光電", "通訊": "通訊工程", "電子": "電子工程", "教育": "教育", "心理": "心理", "社工": "社會工作", "設計": "設計", "建築": "建築",
}
LEVEL_PATTERNS = [(r"大([一二三四五六七])", "university"), (r"碩([一二三四])", "master"), (r"博([一二三四五六七])", "doctoral"), (r"高([一二三])", "senior_high"), (r"國([一二三])", "junior_high"), (r"五專([一二三四五])?", "junior_college")]
LEVEL_WORDS = [(r"研究生|碩士生|碩士班", "master"), (r"博士生|博士班", "doctoral"), (r"大學生|大學部|大專生|科大|大學", "university"), (r"高中生|高職生|高中職|高中|高職", "senior_high"), (r"國中生|國中", "junior_high"), (r"國小生|小學生|國小", "elementary")]
PROGRAM_WORDS = [(r"夜間部|夜校", "night"), (r"進修部|進修學院", "continuing"), (r"在職專班|在職", "in_service"), (r"空中大學|空大", "open_university"), (r"日間部", "day")]
NEGATION_BEFORE = re.compile(r"(沒有|不是|非|無|不具|並非|沒|未具|不屬於|不算)\s*$")
NEGATION_AFTER = re.compile(r"^\s*(身分)?\s*(以外|之外)?\s*(否|沒有|不是)")
NEED_CUES: list[tuple[str, str]] = [
    (r"急需|繳不出|付不出|缺錢|沒錢|吃緊|學費.{0,4}(困難|問題|付不)|生活費.{0,4}(困難|不夠)|急用", "cash_now"),
    (r"減輕.{0,4}負擔|負擔.{0,4}(重|大)|長期|每學期|減免|租金|房租|補貼", "reduce_burden"),
    (r"履歷|榮譽|表現|優秀|成績好|想拿獎|充實", "honor"),
    (r"照顧|照護|失能|失智|臥床|中風|長照|輔具|居家服務|日照|送餐|喘息", "service"),
]


def parse_profile_text(text: str, base: Profile | None = None, registry: Registry | None = None) -> tuple[Profile, list[dict], list[str]]:
    registry = registry or get_registry()
    profile = Profile.from_dict(base.to_dict(), registry) if base else Profile()
    original = text or ""
    normalized = fullwidth_to_halfwidth(original)
    parsed: list[dict] = []
    hints: list[str] = []

    def record(attribute_id: str, value, excerpt: str, confidence: float = 0.9) -> None:
        if not registry.has(attribute_id):
            return
        profile.set(attribute_id, value, source="parsed", evidence=excerpt, confirmed=False, confidence=confidence)
        if profile.attributes.get(attribute_id) is not None:
            parsed.append({"attribute_id": attribute_id, "value": profile.attributes[attribute_id].value, "excerpt": excerpt, "extractor": "rule_based", "confidence": confidence})

    # ---- 戶籍／居住縣市
    for pattern, group, confidence in [(r"(戶籍|設籍|籍貫)(?:在|於|地)?[:：]?\s*([一-鿿]{2,3}(?:市|縣)?)", 2, 0.9), (r"([一-鿿]{2,3}(?:市|縣))\s*(?:的)?(?:戶籍|籍)", 1, 0.9), (r"([一-鿿]{2,3}(?:市|縣)?)人", 1, 0.8)]:
        match = next((m for m in re.finditer(pattern, normalized) if find_cities(m.group(group))), None)
        if match:
            record("residence.household_city", find_cities(match.group(group))[0], match.group(0), confidence)
            break
    match = re.search(r"(住在|住|居住(?:在|於)|目前在|人在)\s*([一-鿿]{2,3}(?:市|縣)?)", normalized)
    if match and find_cities(match.group(2)):
        record("residence.current_city", find_cities(match.group(2))[0], match.group(0), 0.8)
    match = re.search(r"(?:設籍|戶籍)[^，,。]{0,6}?(滿|已)?\s*([0-9]+|[一二兩三四五六七八九十]+)\s*(年|個月)", normalized)
    if match:
        number = chinese_to_int(match.group(2))
        if number:
            record("residence.duration_months", number * 12 if match.group(3) == "年" else number, match.group(0))

    # ---- 學校／科系／學制／年級／部別
    for alias in sorted(SCHOOL_ALIASES, key=len, reverse=True):
        if alias in normalized:
            name, school_type = SCHOOL_ALIASES[alias]
            record("education.school", name, alias)
            record("education.school_type", school_type, alias, 0.8)
            break
    for alias in sorted(DEPARTMENT_ALIASES, key=len, reverse=True):
        if alias in normalized:
            record("education.department", DEPARTMENT_ALIASES[alias], alias, 0.85)
            break
    level_done = False
    for pattern, level in LEVEL_PATTERNS:
        match = re.search(pattern, normalized)
        if match:
            record("education.level", level, match.group(0))
            record("applicant.is_student", True, match.group(0), 0.8)
            grade = chinese_to_int(match.group(1)) if match.lastindex and match.group(1) else None
            if grade:
                record("education.grade", grade, match.group(0))
            level_done = True
            break
    if not level_done:
        for pattern, level in LEVEL_WORDS:
            match = re.search(pattern, normalized)
            if match:
                record("education.level", level, match.group(0), 0.8)
                record("applicant.is_student", True, match.group(0), 0.7)
                break
    for pattern, program in PROGRAM_WORDS:
        match = re.search(pattern, normalized)
        if match:
            record("education.program_type", program, match.group(0), 0.85)
            break

    # ---- 成績
    for pattern, attribute_id in [(r"(?:平均|學業|成績)[^0-9]{0,6}([0-9]{2,3}(?:\.[0-9])?)\s*分?", "academic.average_score"), (r"(?:操行|德育)[^0-9]{0,4}([0-9]{2,3})\s*分?", "academic.conduct_score"), (r"GPA\s*[:：]?\s*([0-4](?:\.[0-9]{1,2})?)", "academic.gpa"), (r"(?:排名|名次)[^0-9]{0,6}前\s*([0-9]{1,2})\s*%", "academic.ranking_percent")]:
        match = re.search(pattern, normalized, re.I)
        if match:
            try:
                record(attribute_id, float(match.group(1)), match.group(0))
            except ValueError:
                continue

    # ---- 年齡／所得／家庭
    match = re.search(r"(?<![0-9])([0-9]{1,2})\s*歲", normalized)
    if match and 5 <= int(match.group(1)) <= 110:
        target = "applicant.age"
        if re.search(r"(爸|媽|父|母|阿公|阿嬤|祖|長輩|家人|小孩|孩子|兒子|女兒)[^。，]{0,8}" + re.escape(match.group(0)), normalized):
            hints.append(f"「{match.group(0)}」看起來是家人的年齡，請確認是申請者本人還是受照顧者")
        record(target, int(match.group(1)), match.group(0), 0.85)
    match = re.search(r"(?:年所得|年收入|家庭所得|家庭收入|所得)[^0-9]{0,6}([0-9]+(?:\.[0-9]+)?)\s*(萬)?", normalized)
    if match:
        value = float(match.group(1)) * (10000 if match.group(2) else 1)
        if value >= 10000:
            record("household.income_year", value, match.group(0), 0.85)
    match = re.search(r"(?:家裡|家中|家庭|全家)[^0-9]{0,4}([0-9]|[一二三四五六七八九十]+)\s*(?:口|人)", normalized)
    if match:
        number = chinese_to_int(match.group(1))
        if number:
            record("household.size", number, match.group(0), 0.85)
    match = re.search(r"([0-9]|[一二三四五])\s*(?:個|名|位)?(?:小孩|孩子|子女)", normalized)
    if match:
        number = chinese_to_int(match.group(1))
        if number:
            record("family.children_count", number, match.group(0), 0.8)

    # ---- 身分（本體別名 + 否定）
    for tag_id, alias in registry.tags_in_text(normalized).items():
        tag = registry.tags[tag_id]
        if not tag.attribute or tag.virtual:
            continue
        attribute = registry.get(tag.attribute)
        if attribute is None:
            continue
        position = normalized.find(alias)
        before = normalized[max(0, position - 6) : position]
        after = normalized[position + len(alias) : position + len(alias) + 6]
        negated = bool(NEGATION_BEFORE.search(before) or NEGATION_AFTER.match(after))
        if attribute.type == "boolean":
            record(tag.attribute, not negated, normalized[max(0, position - 6) : position + len(alias) + 4].strip(), 0.85)
        elif attribute.type == "enum" and tag.label in attribute.value_list:
            record(tag.attribute, tag.label, alias, 0.8)
    match = re.search(r"(中度|重度|極重度|輕度)\s*(?:身心障礙|身障|障礙)", normalized) or re.search(r"(?:身心障礙|身障|障礙)[^。，]{0,4}(輕度|中度|重度|極重度)", normalized)
    if match:
        record("disability.certificate_level", match.group(1), match.group(0), 0.85)
        record("disability.has_certificate", True, match.group(0), 0.85)
    match = re.search(r"(?:CMS|長照(?:需要)?等級|評估)[^0-9]{0,6}(?:第)?\s*([1-8])\s*級", normalized, re.I)
    if match:
        record("care.cms_level", int(match.group(1)), match.group(0), 0.85)
        record("care.needs_care", True, match.group(0), 0.8)
    if re.search(r"失業|被資遣|沒工作|待業", normalized):
        match = re.search(r"失業|被資遣|沒工作|待業", normalized)
        record("employment.status", "unemployed", match.group(0), 0.8)
        if "資遣" in match.group(0):
            record("employment.involuntary_separation", True, match.group(0), 0.8)
    if re.search(r"租屋|租房|房租|租金", normalized):
        match = re.search(r"租屋|租房|房租|租金", normalized)
        record("housing.tenure", "rent", match.group(0), 0.75)
        rent = re.search(r"(?:房租|租金)[^0-9]{0,4}([0-9]+(?:\.[0-9]+)?)\s*(萬)?", normalized)
        if rent:
            record("housing.rent_month", float(rent.group(1)) * (10000 if rent.group(2) else 1), rent.group(0), 0.8)

    # ---- 需求類型
    for pattern, need in NEED_CUES:
        match = re.search(pattern, normalized)
        if match:
            profile.need_type = need
            parsed.append({"attribute_id": "need_type", "value": need, "excerpt": match.group(0), "extractor": "rule_based", "confidence": 0.7})
            break
    if not parsed:
        hints.append("沒有解析出任何欄位，請試著寫得更具體一點（縣市、學校、年級、成績、身分、需求）。")
    return profile, parsed, hints
