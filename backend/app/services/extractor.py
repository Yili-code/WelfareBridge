"""Extractor v2：原文 → benefits 文件（core + benefit meta + 條件句 → 登錄表規則 + evidence）。

原則：
- 只從原文（含來源頁面本身的標籤欄位）抽取，每個值都附原文摘錄。
- 條件句的偵測用「語料統計出的條件提示詞 + 登錄表別名」，對到屬性後依屬性型態抽 operator / value。
- 對不到屬性、或抽不出值的條件句記錄為 unmapped，交給本地 AI（app/llm/fill.py）在候選屬性中選擇；仍失敗 → complex。
- 程序條款（逾期、證件不齊、名額、擇優）不產生規則。
- 「本市／本縣」只在能由機關名稱推定時才填縣市，且 inferred=true。
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from ..config import Settings, get_settings
from ..registry import Attribute, Registry, get_registry
from .classifier import ClassificationResult, get_classifier
from .normalization import AMOUNT_RE, chinese_to_int, find_cities, normalize_city, normalize_text, parse_amounts, parse_date_range, parse_duration_months, taiwan_today, to_iso_date

# 已停止受理：標題（【已不再受理新申請案】…）或原文（額度已用罄）明說不再受理 → status=expired（保留紀錄，預設不列出、不進媒合）
CLOSED_TITLE_RE = re.compile(r"已不再受理|不再受理新申請|已停辦|已停止受理|已截止|已結束|已額滿|已用罄")
# 隨時受理（沒有截止日）的用語：社會救助類方案多半如此，不算「缺截止日」
ROLLING_RE = re.compile(
    r"隨到隨辦|全年受理|隨時受理|全年度受理|常年受理|不定期受理|隨時申請|隨時提出申請|全年皆可申請|不限申請期間|無申請期限|逕向.{0,12}(?:申請|提出)"
    r"|(?:之日|之翌日|發生日|出生|死亡|事實發生)(?:起|後)\s*[0-9一二三四五六七八九十]{1,3}\s*(?:日|個月|月|年)內"
)
CLOSED_TEXT_RE = re.compile(r"額度已用罄|已停辦|已停止受理|不再受理新申請|停止新增(?:補助)?對象|停止受理新(?:案|申請)|本(?:方案|計畫|貸款|專案|措施)已(?:結束|停止|截止|停辦)")


# 「發布單位」常寫成科室：社會局、婦幼發展及平權科、社會救助科…；沒有機關名詞時不能當主辦機關
AGENCY_WORD_RE = re.compile(r"(部|署|局|處|府|公所|委員會|管理所|大學|學校|基金會|協會|公司)")
CONTACT_JUNK_PROVIDER_RE = re.compile(r"(電話|傳真|聯絡資訊|聯絡人|分機|信箱|地址|通知)")
DIVISION_TAIL_RE = re.compile(r"(科|課|組|室|中心|站|隊)\s*$")


def is_division_name(unit: str) -> bool:
    unit = (unit or "").strip()
    if not unit or AGENCY_WORD_RE.search(unit):
        return False
    return bool(DIVISION_TAIL_RE.search(unit)) or len(unit) <= 4


# 佔位規則（operator=exists）的守門：句子要真的是條件，attribute_id 要真的被摘錄提到
HEADING_ONLY_RE = re.compile(r"^[^，。；]{0,24}[:：]\s*$")  # 「三、申請期限：」「限制條件：一、申請資格：」
NO_LIMIT_VALUE_RE = re.compile(r"[:：]\s*(不拘|不限|無|無限制|不予限制|依各校規定)\s*$")
CONDITION_CUE_RE = re.compile(r"(者|須|應|得|限|僅|滿|以上|以下|未滿|超過|符合|具有|具備|經|不得|低收入|中低收入|設籍|就讀|持有|領有|年滿)")


AMOUNT_LINE_RE = re.compile(r"^[（(]?[一二三四五六七八九十0-9]+[）)、.]?[^。；]{0,40}(?:每名|每人|每月|每學期|每年|共)?[^。；]{0,20}[0-9０-９,，一二三四五六七八九十萬千仟佰百]+\s*元")


# 視窗式金額回退：要有「發給／核發／補助金額／每人…」這種給付語氣，且不能是自付費用
AMOUNT_WINDOW_CUE_RE = re.compile(
    r"(補助金額|補助標準|發放標準|救助標準|扶助標準|給付標準|發給|發放|核發|核給|給付|補助|補貼|津貼|獎助|救助|扶助|禮金|慰問|每人|每戶|每名|每餐|每月|每學期"
    r"|一般家庭|一般戶|低收入戶|中低收入戶|弱勢家庭|元\s*[/／]\s*(?:月|年|次|日|餐|人))"
)
# 「低收入戶：50萬元」的「收入」是身分不是門檻 → 用負向後顧排除低／中低收入戶
AMOUNT_WINDOW_VETO_RE = re.compile(r"(工本費|製作費|規費|繳納|自付|自行負擔|收費|罰款|保證金|押金|所得總額|(?<!低)收入(?!戶)|財產|不予核給|不予補助)")
AMOUNT_CLAUSE_SPLIT_RE = re.compile(r"[，。；：、\n]")


# 互斥的身分標籤：同時要求就不可能成立（低收與中低收是法定互斥）
EXCLUSIVE_TAG_SETS = [
    # 只列法律上不可能同時成立的身分：一戶要嘛低收、要嘛中低收、要嘛都不是。
    # 「老人＋身心障礙」「老人＋原住民」可以同時成立，不能因為看起來像擇一就併成擇一群組（那是放寬資格）。
    {"low_income", "middle_low_income"},
    {"low_income", "middle_low_income", "economic_hardship"},
]


def _tag_of(value):
    return value if isinstance(value, str) else (value[0] if isinstance(value, list) and value else None)


def _conflicting_groups(attribute_id: str, rules_by_group: dict[str, list[dict]]) -> list[tuple[str, str]]:
    """回傳「彼此互斥」的群組配對：同一屬性、分屬不同群組（＝必須同時成立）、但值不可能同時為真。"""
    pairs: list[tuple[str, str]] = []
    groups = sorted(rules_by_group)
    for i, left in enumerate(groups):
        for right in groups[i + 1:]:
            left_rules, right_rules = rules_by_group[left], rules_by_group[right]
            conflict = False
            if attribute_id == "identity.tags":
                left_tags = {_tag_of(r.get("value")) for r in left_rules} - {None}
                right_tags = {_tag_of(r.get("value")) for r in right_rules} - {None}
                conflict = any(
                    (left_tags & exclusive) and (right_tags & exclusive) and not (left_tags & right_tags)
                    for exclusive in EXCLUSIVE_TAG_SETS
                )
            else:
                operators = {r.get("operator") for r in left_rules + right_rules}
                if len(operators) == 1 and operators <= {">=", ">", "<=", "<", "="}:
                    conflict = {str(r.get("value")) for r in left_rules} != {str(r.get("value")) for r in right_rules}
                elif len(operators) == 1 and operators == {"in"}:
                    left_values = set().union(*[set(r.get("value") or []) if isinstance(r.get("value"), list) else {r.get("value")} for r in left_rules])
                    right_values = set().union(*[set(r.get("value") or []) if isinstance(r.get("value"), list) else {r.get("value")} for r in right_rules])
                    conflict = bool(left_values) and bool(right_values) and not (left_values & right_values)
            if conflict:
                pairs.append((left, right))
    return pairs


def relax_contradictory_rules(rules: list[dict]) -> int:
    """同一屬性的必要條件分屬不同群組（＝AND）卻互斥 → 把那些群組併成一個擇一群組。
    「低收入戶＋學生」這種可以同時成立的組合不會被併。回傳併了幾個屬性。"""
    from collections import defaultdict

    merged = 0
    by_attribute: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for rule in rules:
        if rule.get("role") == "required" and rule.get("complexity") == "simple":
            by_attribute[rule.get("attribute_id", "")][rule.get("group_id", "")].append(rule)
    for attribute_id, rules_by_group in by_attribute.items():
        pairs = _conflicting_groups(attribute_id, rules_by_group)
        if not pairs:
            continue
        # 把互相衝突的群組連成一個集合（A↔B、B↔C ⇒ A、B、C 同組）
        union: dict[str, str] = {}

        def find(name: str) -> str:
            while union.get(name, name) != name:
                name = union[name]
            return name

        for left, right in pairs:
            union.setdefault(left, left)
            union.setdefault(right, right)
            union[find(right)] = find(left)
        clusters: dict[str, list[str]] = defaultdict(list)
        for group in list(union):
            clusters[find(group)].append(group)
        for index, (_root, group_names) in enumerate(sorted(clusters.items()), start=1):
            if len(group_names) < 2:
                continue
            target = f"any_{attribute_id.replace(chr(46), chr(95))}_{index}"
            for group in group_names:
                for rule in rules_by_group[group]:
                    rule["group_id"] = target
                    if "（擇一）" not in rule.get("human_readable", ""):
                        rule["human_readable"] = rule.get("human_readable", "") + "（擇一）"
            merged += 1
    return merged



def _values_of(rule: dict) -> set:
    value = rule.get("value")
    if isinstance(value, list):
        return {str(v) for v in value}
    return {str(value)}


def drop_contradictory_rules(rules: list[dict]) -> int:
    """刪掉與必要條件直接矛盾的排除規則；布林屬性同時要 True 與 False 時兩條都改標為需語意判斷。"""
    from collections import defaultdict

    changed = 0
    by_attribute: dict[str, list[dict]] = defaultdict(list)
    for rule in rules:
        if rule.get("complexity") == "simple":
            by_attribute[rule.get("attribute_id", "")].append(rule)
    removed: list[dict] = []
    for _attribute_id, group in by_attribute.items():
        required = [r for r in group if r.get("role") == "required"]
        exclusions = [r for r in group if r.get("role") == "exclusion"]
        for exclusion in exclusions:
            if any(_values_of(exclusion) & _values_of(r) for r in required):
                removed.append(exclusion)
                changed += 1
        booleans = [r for r in required if r.get("operator") == "="]
        if len({str(r.get("value")) for r in booleans}) > 1:
            for rule in booleans:
                rule["complexity"] = "complex"
                if "（原文兩種說法都有）" not in rule.get("human_readable", ""):
                    rule["human_readable"] = rule.get("human_readable", "") + "（原文兩種說法都有）"
            changed += 1
    for rule in removed:
        if rule in rules:
            rules.remove(rule)
    return changed

def is_real_condition(text: str) -> bool:
    """「三、申請期限：」「學門：不拘」是段落標題或無限制欄位，「（二）私立高中職學生每名6,000元。」是金額級距，
    都不該變成資格規則；有條件語氣或提到登錄表屬性／身分標籤的句子才算條件。"""
    value = (text or "").strip()
    if len(value) < 6:
        return False
    if HEADING_ONLY_RE.match(value) or NO_LIMIT_VALUE_RE.search(value):
        return False
    if AMOUNT_LINE_RE.match(value) and not re.search(r"(者|須|應|限|僅|符合|不得)", value):
        return False
    if CONDITION_CUE_RE.search(value):
        return True
    registry = get_registry()
    return bool(registry.attributes_in_text(value) or registry.tags_in_text(value))


def placeholder_attribute(registry, candidates: list[str], excerpt: str) -> str:
    """佔位規則的屬性：摘錄裡真的提到才填，否則留空（不要拿候選清單的第一個硬湊）。"""
    mentioned = registry.attributes_in_text(excerpt or "", include_mined=True) or {}
    best, best_len = "", 0
    for candidate in candidates or []:
        if registry.get(candidate) is None:
            continue
        alias = mentioned.get(candidate)
        if alias and len(str(alias)) > best_len:  # 命中的別名越長越具體（「設籍」勝過「滿」）
            best, best_len = candidate, len(str(alias))
        elif candidate == "identity.tags" and registry.tags_in_text(excerpt or "") and not best:
            best, best_len = candidate, 1
    return best


def closed_marker(title: str, text: str) -> str:
    """標題或原文明說已停止受理時回傳那個字眼，否則空字串。"""
    match = CLOSED_TITLE_RE.search(title or "") or CLOSED_TEXT_RE.search(text or "")
    return match.group(0) if match else ""

EXTRACTION_VERSION = "2.0.0"

LEVEL_PATTERNS: list[tuple[str, list[str]]] = [
    (r"高級中等以上|中等以上學校|高中職以上|高中以上", ["senior_high", "vocational_high", "junior_college", "university", "master", "doctoral"]),
    (r"大專以上|大學以上|大專校院以上|大專院校以上", ["university", "master", "doctoral"]),
    (r"國民?小學|國小", ["elementary"]),
    (r"國民中學|國中", ["junior_high"]),
    (r"高中職|高級中等學校|高級中學|高中|高職|職業學校", ["senior_high", "vocational_high"]),
    (r"五專|五年制專科", ["junior_college"]),
    (r"大專院校|大專校院|大學校院|大專|大學部|大學|技專校院|科技大學|技術學院|二專|四技|二技|學士班|專科學校", ["university"]),
    (r"研究所|碩博士|碩士", ["master"]),
    (r"研究所|碩博士|博士", ["doctoral"]),
]
LEVEL_ORDER = ["elementary", "junior_high", "senior_high", "vocational_high", "junior_college", "university", "master", "doctoral"]
PROGRAM_TYPE_TERMS: list[tuple[str, str]] = [
    (r"夜間部|夜校", "night"), (r"進修部|進修學院|進修學校|補習學校|進修學士班", "continuing"), (r"在職專班|在職進修", "in_service"), (r"空中大學|空大", "open_university"),
    (r"學分班|推廣教育|推廣進修|教育推廣", "credit_program"), (r"軍警學校|軍校|警察大學|警專", "military_police"), (r"日間部", "day"),
]
CN_NUM = r"[0-9０-９]+(?:\.[0-9]+)?|[一二兩三四五六七八九十百千萬零〇]+"
NUM_TOKEN_RE = re.compile(rf"({CN_NUM})\s*(萬)?\s*(歲|分|元|個月|月|年|級|倍|%|％|人|名|學分|點)?")
# 「低於新臺幣一百萬元」：限定詞與數字之間可以夾幣別
QUAL_BEFORE_RE = re.compile(r"(年滿|已滿|滿|達|至少|超過|逾|高於|未滿|未達|低於|不超過|不逾|未逾|未超過|以上|以下)\s*(?:新臺幣|新台幣|NT\$|NTD|\$)?\s*$")
QUAL_AFTER_RE = re.compile(r"^\s*(?:\(含\)|（含）)?\s*(以上|以下|以內|以下者|以上者|未滿|前|以前|之後|後)")
RANGE_RE = re.compile(rf"({CN_NUM})\s*(?:歲|分|元|個月|級)?\s*[至到~～\-－]\s*({CN_NUM})\s*(歲|分|元|個月|級|倍)")
NEGATION_BEFORE_RE = re.compile(r"(未|無|不|非|沒有|尚未|不具|未具|不得|不含|不包括|除外|排除)(享有|領有|具有|持有|曾|得|受|接受|具備|取得|列入|符合)?\s*$")
NEGATION_ADJACENT_RE = re.compile(r"(無|未|非|沒有|不具|未具|不需|免|不得有)\s*$")
# 否定詞＋動詞之後到屬性別名之間沒有跨子句標點 → 否定仍然作用在這個屬性上
# （「未接受公共化或準公共托育服務」「未領有身心障礙證明」「未參加勞保或農保」）
NEGATION_SCOPE_RE = re.compile(r"(未|無|不|非|沒有|尚未|不具|未具)(享有|領有|具有|持有|接受|受領|受|參加|參與|加入|取得|列入|符合|使用|就讀|申請|請領|領取|安置|收容)[^、，；。]{0,20}$")
NEGATED_ALIAS_RE = re.compile(r"^(無|未|非|沒有|不具|未具)")
OR_GROUPABLE_ATTRIBUTES = {"identity.tags", "applicant.age", "disability.has_certificate", "disability.level", "care.cms_level", "family.youngest_child_age", "identity.indigenous", "identity.new_immigrant"}
# 布林屬性只有在子句有「資格語氣」時才產生規則（避免只是提到名詞就變條件）
REQUIRE_CUE_RE = re.compile(r"(具有?|具備|領有|持有|經[^，。]{0,12}(評估|認定|核定|證明|鑑定)|符合|屬於?|列冊|身分|資格|對象|限|須|應|者|且|並|為|已|正|目前|中者|之)")
DOCUMENT_LINE_RE = re.compile(r"(影本|正本|證明書|申請書|申請表|表件|檢附|繳交|附件|範本|下載|填寫)")
DOC_NOUN_RE = re.compile(r"(證明|證件|證書|申請書|申請表|表件|表格|影本|正本|收據|存摺|帳號|身分證|戶口名簿|戶籍|診斷|切結|同意書|委託書|清冊|名冊|照片|報告|資料|文件|合約|契約|發票|明細|存款|證照|手冊|卡)")
DOC_LABEL_RE = re.compile(r"^(受理單位|受理窗口|諮詢電話|服務電話|聯絡電話|洽詢|服務內容|注意事項|備註|宣導方式|動產限額|不動產限額|申請方式|申辦方式|補助標準|補助金額|給付標準|辦理方式|審核|核定|其他)")
DOC_CONTACT_RE = re.compile(r"(電話|傳真|分機|地址|網址|http)")


def _looks_like_document(item: str) -> bool:
    """應備文件必須像一份文件：排除段落標題（以冒號結尾）、受理單位／電話／說明句。"""
    value = item.strip()
    if not value or value.endswith(("：", ":")) or DOC_LABEL_RE.match(value):
        return False
    if DOC_CONTACT_RE.search(value):
        return False
    return bool(DOC_NOUN_RE.search(value))

NAV_LINE_RE = re.compile(r"(連結|網站|專區|查詢|更多|相關資訊|說明會|懶人包|問答|Q&A|FAQ|點選|按此|網址|http)")
OVERVIEW_TITLE_RE = re.compile(r"(總覽|總整理|有哪些|一覽|懶人包|專區|彙整|整理|福利地圖|服務地圖)")
PROGRAM_NAME_RE = re.compile(r"[一-鿿]{2,16}(獎學金|獎助學金|助學金|津貼|補助金|補助|補貼|給付|扶助|減免)")
INCOME_SENTENCE_RE = re.compile(r"(所得|收入|財產|存款|不動產|房屋|土地|價值|保費|租金上限|利率)")
THRESHOLD_QUAL_RE = re.compile(r"(以上|超過|逾|未達|以下|以內|低於|不得|不予|門檻|限額|未逾|不超過|達)")
BENEFIT_AMOUNT_CUE_RE = re.compile(r"(核給|發給|補助|給付|津貼|獎學金|助學金|獎助|獎勵金|補貼|每名|每人|每月|每年|每學期|每學年|每戶|每案|上限|最高|金額)")


SELF_PAY_THRESHOLD_RE = re.compile(r"(自行負擔|自付|自費)[^。；]{0,20}(累計|合計)?[^。；]{0,12}(超過|以上|達|逾)")


def _is_threshold_clause(clause: str) -> bool:
    """「所得總額達新臺幣一百萬元以上」「自行負擔看護費用累計超過三萬元」：資格門檻，不是給付金額。"""
    if SELF_PAY_THRESHOLD_RE.search(clause):
        return True
    return bool(INCOME_SENTENCE_RE.search(clause)) and bool(THRESHOLD_QUAL_RE.search(clause)) and not BENEFIT_AMOUNT_CUE_RE.search(clause)
NUMBER_UNITS: dict[str, set[str]] = {
    "applicant.age": {"歲"}, "family.youngest_child_age": {"歲"}, "employment.insured_years": {"年"}, "education.years_in_program": {"年"},
    "residence.duration_months": {"個月", "月", "年"}, "employment.unemployed_months": {"個月", "月", "年"}, "care.cms_level": {"級"}, "care.adl_score": {"分"},
    "household.size": {"人", "口"}, "household.dependents": {"人"}, "family.children_count": {"名", "人", "位"}, "education.grade": {"年級"},
}
CHILD_AGE_CATEGORIES = {"child_allowance", "childcare_subsidy", "parental_leave_allowance"}
EXCEPTION_PREFIX_RE = re.compile(r"^\s*(?:[（(][一二三四五六七八九十0-9]+[)）]|[0-9]{1,2}[、.])?\s*(但|惟|除|另|如|若|倘|前項|前款|其)")
# 「…失能者，包含：」「服務對象如下：」後面接的條列也是擇一，不是要同時成立
OR_LIST_HEADER_RE = re.compile(r"(之一|任一|其中一項|符合下列|下列.{0,6}(對象|身分|資格|情形|條件)|(對象|身分|資格|情形|條件|者)[^。；\n]{0,6}(包含|包括|如下|分為))")
LIST_ITEM_RE = re.compile(r"^\s*(?:[0-9０-９]{1,2}[、.．)）]|[（(][一二三四五六七八九十0-9]+[)）]|[一二三四五六七八九十]+、|[•●◎※])")
EXCLUSION_CUE_RE = re.compile(r"(不得申請|不得重複|不得同時|不予|不含|不包括|排除|除外|不適用|不符合|不得再|不能|不可|不得)")
BONUS_CUE_RE = re.compile(r"(優先|加分|酌予|得優先|從優|優先補助|優先錄取|優先受理)")
STRONG_BONUS_RE = re.compile(r"為優先|優先(獎助|補助|錄取|受理|核發|輔導|安排|入住|入園)|優先順序|優先次序")
PROCEDURAL_CUE_RE = re.compile(r"(逾期|證件不齊|不予受理|依序|審查|核定|撥付|退還|另行通知|造冊|初審|複審|以.{0,6}為限$|名額.{0,10}(名|人)|擇優|抽籤|先到先得|額滿)")
SECTION_START_RE = re.compile(r"(申請資格|補助對象|服務對象|申請對象|給付對象|資格條件|申請條件|補助條件|補助資格|受理對象|對象[:：]|資格[:：]|適用對象|符合下列|具備下列|條件如下|對象如下)")
SECTION_END_RE = re.compile(r"(申請文件|應備文件|檢附文件|所需文件|申請方式|申請程序|申請流程|補助金額|補助標準|給付標準|補助內容|服務內容|聯絡|洽辦|備註|注意事項|受理單位|辦理單位|申請期間|申請期限)")
DEFAULT_CONDITION_CUES = ["設籍", "年滿", "未滿", "歲", "領有", "持有", "評估", "符合", "具有", "身分", "以上", "以下", "不得", "未領", "未享", "經", "屬", "列冊", "證明", "在學", "就讀", "失能", "失業", "所得"]
RESTRICTION_RE = re.compile(r"(不得申請|不得重複|以一項為限|不含|不包括|排除|不予受理|不得再|不能重複|已領|擇一|以.{1,6}為限)")
DOC_LINE_RE = re.compile(r"^\s*(?:[0-9０-９]{1,2}[、.．)）]|[（(][一二三四五六七八九十]+[)）]|[一二三四五六七八九十]+、|[•●◎※]|\([0-9]+\))\s*(.+)$")
DOC_TRIGGER_RE = re.compile(r"(檢附|繳交|備齊|應備|申請文件|所需文件|繳驗|下列資料|下列文件|申請表件|應繳|應備文件|準備文件)")
PHONE_RE = re.compile(r"\(?0\d{1,2}\)?[-\s]?\d{3,4}[-\s]?\d{3,4}(?:\s*(?:分機|轉|#|ext\.?)\s*\d{1,5})?|1966|1957|1999", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PROVIDER_RULES: list[tuple[str, str]] = [
    (r"公所", "township"),
    (r"市政府|縣政府|教育局|教育處|社會局|社會處|民政局|原民局|客家事務|青年局|衛生局|勞動局|勞工局|市議會|縣議會|市府|縣府", "local_government"),
    (r"基金會|協會|公司|宮|寺|廟|堂|社團法人|財團法人|總會|慈善|文教|企業|銀行|工會|同鄉會|學會|扶輪|獅子會|商會|教會|基金", "private_organization"),
    (r"大學|學院|學校|高中|高級中等|高職|國中|國小|校友會", "school"),
    (r"部|署|委員會|總統府|行政院|考試院|監察院|司法院|立法院|國科會|中央|行政法人|國家|長期照顧司|國民及學前教育署|勞動力發展署|勞工保險局|國土管理署", "central_government"),
]
REPOST_ORG_RE = re.compile(r"轉知[】\]\s]*[「『]?([一-鿿A-Za-z0-9]{2,30}?(?:部|署|委員會|市政府|縣政府|教育局|教育處|社會局|公所|基金會|協會|總會|文教|宮|寺|會|公司|大學|學校|學院))")
TITLE_ORG_RE = re.compile(r"^(?:【[^】]*】|\[[^\]]*\])?\s*([一-鿿]{2,20}?(?:部|署|委員會|市政府|縣政府|教育局|教育處|社會局|公所|基金會|協會|總會|文教基金|宮|寺|公司|大學|科技大學|學院|高級中學))")
ALTERNATIVE_PREFIX_RE = re.compile(r"(或|或者|亦得|另|以及)[^。；\n]{0,12}$")

BENEFIT_FORM_CUES: list[tuple[str, str]] = [
    (r"貸款|利息補貼|利率", "loan"), (r"減免|免繳|免收|免學費|免除", "waiver"), (r"輔具|實物|物資|餐飲|送餐|裝置", "in_kind"),
    (r"額度|券|點數", "voucher"), (r"服務時數|照顧服務|居家服務|日間照顧|托顧|接送|喘息|安置|給付單位", "service"),
    (r"元|津貼|獎學金|助學金|補助金|補助費|生活補助|獎助金|發給|核發|撥付", "cash"),
]
AWARD_BASIS_CUES: list[tuple[str, str]] = [
    (r"擇優|評選|評審|審查委員|依成績高低|依序錄取|名額有限|以.{1,6}名為限|從優", "competitive"), (r"抽籤", "lottery"), (r"額滿為止|先到先得|受理完畢|經費用罄", "first_come"),
    (r"符合資格者均|均予|不限名額|名額不限|符合.{0,8}即|皆可申請|均可申請|依規定核給|按月發給|每人每月", "criteria"),
]
CHANNEL_CUES: list[tuple[str, str]] = [
    (r"線上申請|線上申辦|網路申請|系統申請|e化|網站申請|線上填寫", "online"), (r"向.{0,6}學校|由學校|學校統一|就讀學校|各校", "school"),
    (r"郵寄|掛號|寄送|寄至", "mail"), (r"公所|區公所|鄉公所|鎮公所|社會局|社福中心|照管中心|臨櫃|親自|現場|就業服務|勞保局|健保署|戶政|社會處", "agency"),
]
OBLIGATION_RE = re.compile(r"(服務時數|回饋|出席.{0,8}(典禮|頒獎)|繳交.{0,8}(心得|報告|成果)|履約|志工|義務|返還|繳回|追回|服務學習)")
EXCLUSIVE_CUES: list[tuple[str, str]] = [
    (r"公費", "public_funding"), (r"政府.{0,8}(其他|各項|同性質).{0,6}(補助|獎助|津貼)|其他政府|公設獎學金|政府機關.{0,4}獎", "government_benefit"),
    (r"本(會|部|局|署|府).{0,6}其他|同一(機關|單位)", "same_provider"), (r"同性質|性質相同|同類|相同項目", "same_category"), (r"其他.{0,6}(獎學金|補助|津貼).{0,8}(擇一|不得|重複)|擇一|不得重複|不得同時", "any_other"),
]
RENEWABLE_RE = re.compile(r"(續領|連續.{0,4}(領|補助)|得繼續|每學期核發|按月發給|按月核發|逐年|持續補助|每年申請)")
NOT_RENEWABLE_RE = re.compile(r"(一次性|一次給付|僅限一次|以一次為限|限領一次)")
DECISION_RE = re.compile(r"(\d{1,3})\s*(?:個)?(工作)?(日|天)內.{0,6}(核定|審核|核發|完成)")
QUOTA_RE = re.compile(r"(?:預計總名額|名額|以)[:：]?\s*([0-9０-９,，]{1,6})\s*(?:名|人)(?:為限)?")
PERIOD_WORD_RE = re.compile(r"(每學期|每學年|每年|每月|每日|每次|一次性|每名|每人|每戶|每案)")


@dataclass
class ExtractionOutput:
    benefit: dict
    review_reasons: list[str]
    unmapped_conditions: list[dict] = field(default_factory=list)


def classify_provider(name: str, default: str = "unknown") -> str:
    for pattern, provider_type in PROVIDER_RULES:
        if re.search(pattern, name or ""):
            return provider_type
    return default


def sentences_of(text: str) -> list[str]:
    parts = re.split(r"(?<=[。；;！\n])", text or "")
    return [p.strip() for p in parts if p and p.strip()]


def clauses_of(sentence: str) -> list[str]:
    # 半形逗號只在不是數字千分位（10,020）時才當子句分隔
    parts = re.split(r"[，；;：:]|(?<!\d),|,(?!\d)|(?<=者)、", sentence)
    return [p.strip("。 ") for p in parts if p and len(p.strip("。 ")) >= 2]


def _excerpt_for(text: str, start: int, end: int, window: int = 60) -> str:
    left = max(text.rfind("。", 0, start), text.rfind("\n", 0, start), text.rfind("；", 0, start)) + 1
    right_candidates = [i for i in (text.find("。", end), text.find("\n", end), text.find("；", end)) if i != -1]
    right = min(right_candidates) + 1 if right_candidates else len(text)
    excerpt = text[left:right].strip()
    if len(excerpt) > 200:
        excerpt = text[max(left, start - window) : min(right, end + window)].strip()
    return excerpt


def _num(token: str) -> float | None:
    token = (token or "").replace(",", "").replace("，", "")
    try:
        return float(token)
    except ValueError:
        value = chinese_to_int(token)
        return float(value) if value is not None else None


def _new_id() -> str:
    return str(uuid.uuid4())


# PDF 斷行會把中文數字切成兩行（「每坪新臺幣二」換行「百元」→ 句子切割後只剩「百元」＝100）。
# 只有在「前一行以中文數字結尾、下一行以位數字（十百千萬）開頭」時才接回；這種組合幾乎一定是同一個被切開的數字。
CJK_NUMBER_BREAK_RE = re.compile(r"(?<=[一二兩三四五六七八九十百千萬零〇壹貳貮參叁肆伍陸柒捌玖拾佰仟万])[ \t]*\n[ \t]*(?=[十百千萬拾佰仟万])")



def list_item_kind(sentence: str) -> str:
    """條列標記的層級樣式：一、＝cjk，1.＝digit，（一）＝paren，※＝bullet。空字串代表不是條列項。"""
    text = (sentence or "").lstrip()
    if re.match(r"^[（(]", text):
        return "paren"
    if re.match(r"^[0-9０-９]{1,2}[、.．)）]", text):
        return "digit"
    if re.match(r"^[一二三四五六七八九十]+、", text):
        return "cjk"
    if re.match(r"^[•●◎※]", text):
        return "bullet"
    return ""

class Extractor:
    def __init__(self, settings: Settings | None = None, registry: Registry | None = None):
        self.settings = settings or get_settings()
        self.registry = registry or get_registry()
        try:
            cues = get_classifier().condition_cues
        except Exception:
            cues = []
        self.condition_cues = list(dict.fromkeys([*cues, *DEFAULT_CONDITION_CUES]))

    # ================================================================== main
    def extract(self, doc: dict, source: dict, classification: ClassificationResult) -> ExtractionOutput:
        registry = self.registry
        evidence: list[dict] = []
        rules: list[dict] = []
        conditions: list[dict] = []
        review: list[str] = []
        structured = dict(doc.get("structured") or {})
        structured.pop("sample_rows", None)
        meta = dict(doc.get("meta") or {})
        title = (doc.get("title") or "").strip()
        self._current_title = title
        text = CJK_NUMBER_BREAK_RE.sub("", (doc.get("raw_text") or "").replace("ㄧ", "一"))  # 中文數字被 PDF 斷行切開時接回；注音「ㄧ」當「一」
        if title and title not in text:
            text = f"{title}\n{text}"
        organization = (meta.get("organization") or "").strip()
        if structured.get("發布單位") and f"發布單位：{structured['發布單位']}" not in text:
            text = f"發布單位：{structured['發布單位']}\n{text}"
        elif organization and f"機關單位名稱：{organization}" not in text and not structured.get("發布單位"):
            text = f"機關單位名稱：{organization}\n{text}"

        provider, provider_type, is_repost = self._provider(doc, source, structured, meta, title, evidence)
        jurisdiction = self._jurisdiction(provider, title, structured)
        category = classification.category or (meta.get("seed_category") or "")
        node = registry.category(category)
        domain = node.domain if node else registry.domain_of(category)

        benefit_meta = self._benefit_meta(structured, text, doc, title, category, evidence, review)
        self.current_category = category
        is_overview = self._is_overview(title, text, structured)
        if is_overview:
            review.append("彙整頁（同一頁列出多項補助），不逐條產生資格規則；請由連結前往各項補助")
        else:
            self._structured_rules(structured, text, jurisdiction, rules, evidence)
            self._title_identity_rules(title, rules, evidence)
            self._condition_rules(text, structured, jurisdiction, rules, evidence, conditions)
            self._dedupe_rules(rules)

        relax_contradictory_rules(rules)  # 互斥條件被寫成必要條件 → 併成擇一群組
        drop_contradictory_rules(rules)  # 同時要求又排除同一件事 → 刪排除；布林互相打架 → 標為需語意判斷
        simple_rules = [r for r in rules if r["complexity"] == "simple"]
        if not simple_rules and not is_overview:
            review.append("未能從原文抽取任何可直接判斷的資格規則")
        if provider_type == "unknown":
            review.append("無法判斷提供機關類型")
        if not category:
            review.append("分類器未能判定類別")
        notes: list[str] = []
        if any(e.get("field") == "benefit.amount" and e.get("extractor") == "rule_based_window" for e in evidence):
            notes.append("金額是從表格或沒有標點的段落回推（原文摘錄附在金額說明），需人工確認")
        amount = benefit_meta["amount"]
        if amount["value"] is None and amount["min"] is None and amount["max"] is None:
            notes.append("原文未找到明確金額")
        if not benefit_meta["application_period"]["end_date"] and not benefit_meta["application_period"]["rolling"]:
            notes.append("原文未找到申請截止日期")

        today = taiwan_today().isoformat()
        end_date = benefit_meta["application_period"]["end_date"]
        closed = closed_marker(title, text)
        status = "expired" if (end_date and end_date < today) or closed else "active"
        if closed and not (end_date and end_date < today):
            notes.append(f"標題／原文標示「{closed}」：已停止受理，狀態設為已截止（預設不列出、不進媒合）")
        confidence = self._overall_confidence(evidence, rules)
        keywords = sorted({t for terms in classification.matched_category.values() for t in terms} | set(classification.matched_signal[:8]))
        benefit = {
            "raw_document_id": doc["_id"],
            "source_id": doc["source_id"],
            "title": title,
            "domain": domain,
            "category": category,
            "category_label": registry.category_label(category) if category else "",
            "provider": provider[:200],
            "provider_type": provider_type,
            "provider_region": jurisdiction or ("national" if provider_type == "central_government" else ""),
            "source": {
                "source_id": doc["source_id"],
                "source_name": source.get("name", ""),
                "source_url": doc["source_url"],
                "official_domain": source.get("official_domain", ""),
                "source_type": source.get("source_type", "government_site"),
                "source_verified": bool(source.get("source_verified")),
                "source_verification_method": source.get("source_verification_method", ""),
                "crawl_time": doc.get("crawl_time").isoformat() if hasattr(doc.get("crawl_time"), "isoformat") else str(doc.get("crawl_time") or ""),
                "published_date": doc.get("published_date", "") or "",
                "is_repost": is_repost,
                "data_confidence": int(source.get("data_confidence", 95)),
                "source_page": meta.get("source_page", ""),
                "content_type": doc.get("content_type", "html"),
                "file_path": doc.get("file_path", ""),
            },
            "original_text": text,
            "description": (structured.get("申請說明") or structured.get("獎助內容") or structured.get("服務內容") or text)[:400],
            "is_overview": is_overview,
            "status": status,
            "benefit": benefit_meta,
            "rules": rules,
            "evidence": evidence,
            "conditions": conditions,
            "keywords": keywords,
            "attachments": list(doc.get("attachments") or []),
            "structured_fields": {k: v for k, v in structured.items() if isinstance(v, (str, int, float))},
            "classification": classification.to_dict(),
            "llm": {"processed": False, "model": "", "provider": "", "processed_at": None, "tasks": {}, "accepted": [], "rejected": [], "errors": []},
            "review": {"needs_review": bool(review), "reasons": list(review) + notes},
            "confidence": confidence,
            "extraction_version": EXTRACTION_VERSION,
            "registry_version": registry.version,
            "content_hash": doc.get("content_hash", ""),
        }
        benefit["index"] = self.build_index(benefit)
        unmapped = [c for c in conditions if c["status"] == "unmapped"]
        return ExtractionOutput(benefit=benefit, review_reasons=review, unmapped_conditions=unmapped)

    # ============================================================== provider
    def _provider(self, doc: dict, source: dict, structured: dict, meta: dict, title: str, evidence: list[dict]) -> tuple[str, str, bool]:
        organization = (meta.get("organization") or "").strip()
        is_repost = bool(meta.get("is_repost"))
        list_kind = meta.get("list_kind")
        unit = (structured.get("發布單位") or "").strip()
        if unit and (CONTACT_JUNK_PROVIDER_RE.search(unit) or len(unit) > 30):
            unit = ""  # 「社會救助科 聯絡資訊」「臺中市政府地方稅務局(電話…」不是可用的機關名
        if unit and meta.get("document_kind") in {"page", "program", "pdf"} and source.get("id") in {"gov_tw_services"}:
            evidence.append({"field": "provider", "value": unit, "excerpt": f"發布單位：{unit}", "extractor": "structured_field", "confidence": 0.95, "inferred": False, "inference_basis": ""})
            return unit, classify_provider(unit, "central_government"), True
        if list_kind == "private":
            provider = organization or "民間團體（公告未載明名稱）"
            evidence.append({"field": "provider", "value": provider, "excerpt": f"機關單位名稱：{organization}" if organization else title, "extractor": "structured_field", "confidence": 0.98, "inferred": False, "inference_basis": ""})
            return provider, "private_organization", False
        if list_kind == "government" and organization:
            evidence.append({"field": "provider", "value": organization, "excerpt": f"機關單位名稱：{organization}", "extractor": "structured_field", "confidence": 0.98, "inferred": False, "inference_basis": ""})
            return organization, classify_provider(organization, "central_government"), False
        if source.get("source_type") == "school_site" or "轉知" in title:
            classification = meta.get("classification", "") or ""
            private_classified = "民間" in classification
            government_classified = "政府" in classification
            match = REPOST_ORG_RE.search(title) or REPOST_ORG_RE.search((doc.get("raw_text") or "")[:400]) or TITLE_ORG_RE.search(title)
            if match:
                provider = match.group(1)
                provider_type = "private_organization" if private_classified else classify_provider(provider, "unknown")
                evidence.append({"field": "provider", "value": provider, "excerpt": match.group(0), "extractor": "rule_based", "confidence": 0.9, "inferred": False, "inference_basis": ""})
                return provider, provider_type, True
            cities = find_cities(title)
            if cities and not private_classified and (government_classified or "轉知" in title):
                provider = f"{cities[0]}政府"
                evidence.append({"field": "provider", "value": provider, "excerpt": title, "extractor": "rule_based", "confidence": 0.7, "inferred": True, "inference_basis": f"標題以縣市名稱「{cities[0]}」開頭且公告分類為「{classification or '轉知'}」，推定提供機關為該縣市政府"})
                return provider, "local_government", True
            if private_classified:
                return "民間團體（公告未載明名稱）", "private_organization", True
            if source.get("source_type") == "school_site":
                provider = source.get("organization") or organization
                evidence.append({"field": "provider", "value": provider, "excerpt": f"機關單位名稱：{provider}", "extractor": "rule_based", "confidence": 0.8, "inferred": False, "inference_basis": ""})
                return provider, "school", False
        if unit and unit != organization:
            # 「發布單位：社會局／婦幼發展及平權科」是科室，不是機關：改用來源登錄的機關名；摘錄仍是原文
            value = organization if (organization and (organization.endswith(unit) or is_division_name(unit))) else unit
            evidence.append({"field": "provider", "value": value, "excerpt": f"發布單位：{unit}", "extractor": "structured_field", "confidence": 0.9, "inferred": value != unit, "inference_basis": f"發布單位「{unit}」是科室名稱，主辦機關取自來源登錄的「{organization}」" if value != unit else ""})
            default = source.get("provider_type") if source.get("provider_type") not in {"mixed", "unknown", None} else "unknown"
            return value, classify_provider(value, default), is_repost
        provider = organization or source.get("organization", "")
        if provider:
            evidence.append({"field": "provider", "value": provider, "excerpt": f"機關單位名稱：{provider}", "extractor": "structured_field", "confidence": 0.9, "inferred": False, "inference_basis": ""})
            default = source.get("provider_type") if source.get("provider_type") not in {"mixed", "unknown", None} else "unknown"
            return provider, classify_provider(provider, default), is_repost
        return "", "unknown", is_repost

    @staticmethod
    def _is_overview(title: str, text: str, structured: dict) -> bool:
        """彙整頁：標題像總覽，或同一頁出現 ≥ 6 個不同的補助／獎學金名稱（各自條件不同，不能 AND 在一起）。"""
        if structured.get("獎學金名稱"):
            return False
        if OVERVIEW_TITLE_RE.search(title):
            return True
        names = {m.group(0) for m in PROGRAM_NAME_RE.finditer(text)}
        names = {n for n in names if n not in title and title not in n and len(n) <= 14}
        return len(names) >= 8 and len(text) > 2500

    @staticmethod
    def _jurisdiction(provider: str, title: str, structured: dict) -> str | None:
        cities = find_cities(provider) or find_cities(title) or find_cities(structured.get("發布單位", "") or "")
        return cities[0] if cities else None

    # ========================================================== benefit meta
    def _benefit_meta(self, structured: dict, text: str, doc: dict, title: str, category: str, evidence: list[dict], review: list[str]) -> dict:
        registry = self.registry
        node = registry.category(category)
        form, form_ev = self._benefit_form(title, node)
        if form_ev:
            evidence.append(form_ev)
        amount = self._amount(structured, text, evidence)
        period = self._period(structured, text, doc, evidence)
        award_basis, basis_ev = self._cue_field(text, AWARD_BASIS_CUES, "benefit.award_basis")
        if basis_ev:
            evidence.append(basis_ev)
        quota = None
        for match in QUOTA_RE.finditer(text):
            value = _num(match.group(1))
            if value and 1 <= value <= 100000:
                quota = int(value)
                evidence.append({"field": "benefit.quota", "value": quota, "excerpt": _excerpt_for(text, match.start(), match.end()), "extractor": "rule_based", "confidence": 0.85, "inferred": False, "inference_basis": ""})
                break
        channel, channel_ev = self._cue_field(structured.get("申請方式", "") + "\n" + text, CHANNEL_CUES, "benefit.application.channel")
        if channel_ev:
            evidence.append(channel_ev)
        documents = self._documents(structured, text)
        flags = {
            "requires_interview": bool(re.search(r"面試|口試|面談", text)),
            "requires_recommendation": bool(re.search(r"推薦函|推薦信|推薦書", text)),
            "requires_essay": bool(re.search(r"自傳|讀書計畫|研究計畫|心得", text)),
            "requires_office_proof": bool(re.search(r"村里長|里長|公所出具|區公所.{0,6}證明|里辦公處", text)),
            "requires_financial_proof": bool(re.search(r"財產清單|所得清單|財力證明|財稅|綜合所得稅|所得證明|財產歸戶", text)),
        }
        effort_points = min(len(documents), 8) * 0.5 + (2 if flags["requires_interview"] else 0) + (1.5 if flags["requires_recommendation"] or flags["requires_essay"] else 0) + (1 if flags["requires_office_proof"] else 0)
        effort = "low" if effort_points <= 1.5 else "medium" if effort_points <= 4 else "high"
        obligations: list[str] = []
        for sentence in sentences_of(text):
            if OBLIGATION_RE.search(sentence) and len(sentence) <= 160 and sentence not in obligations:
                obligations.append(sentence)
            if len(obligations) >= 4:
                break
        exclusive: list[str] = []
        exclusive_excerpts: list[str] = []
        for sentence in sentences_of(text):
            if not RESTRICTION_RE.search(sentence) and "公費" not in sentence:
                continue
            for pattern, value in EXCLUSIVE_CUES:
                if re.search(pattern, sentence) and value not in exclusive:
                    exclusive.append(value)
                    exclusive_excerpts.append(sentence[:160])
        if exclusive:
            evidence.append({"field": "benefit.exclusive_with", "value": exclusive, "excerpt": exclusive_excerpts[0], "extractor": "rule_based", "confidence": 0.75, "inferred": False, "inference_basis": ""})
        renewable: bool | None = None
        if NOT_RENEWABLE_RE.search(text):
            renewable = False
        elif RENEWABLE_RE.search(text):
            renewable = True
        decision = DECISION_RE.search(text)
        decision_days = int(decision.group(1)) if decision else None
        contact = self._contact(structured, text)
        return {
            "benefit_form": form,
            "benefit_form_inferred": form_ev is None,
            "amount": amount,
            "amount_annualized": self._annualize(amount),
            "application_period": period,
            "award_basis": award_basis or "unknown",
            "quota": quota,
            "quota_tiers": [],
            "application": {"channel": channel or "unknown", "effort": effort, "documents": documents, **flags, "method": structured.get("申請方式") or self._apply_section(text) or self._first_sentence_with(text, r"(向.{1,12}申請|線上申請|至.{1,10}辦理|送件|報名|洽.{1,8}辦理|撥打1966)") or "", "contact": contact},
            "obligations": obligations,
            "exclusive_with": exclusive or ["none"] if RESTRICTION_RE.search(text) is None else exclusive,
            "renewable": renewable,
            "decision_lead_days": decision_days,
            "target_population_text": "",
        }

    def _benefit_form(self, title: str, node) -> tuple[str, dict | None]:
        """只用標題判斷（內文的「元」「服務」太泛）；標題沒線索就用類別預設並標記 inferred，交給本地 AI 補齊。"""
        title_cues: list[tuple[str, str]] = [
            (r"貸款|利息補貼", "loan"), (r"減免|免學費|免繳|免收", "waiver"), (r"輔具|無障礙|餐飲|送餐|實物", "in_kind"),
            (r"津貼|獎學金|獎助學金|助學金|補助金|補助費|生活補助|扶助金|獎助金|補貼|補助", "cash"),
            (r"居家服務|日間照顧|托顧|接送|喘息|照顧服務|安置|給付|服務$", "service"),
        ]
        for pattern, form in title_cues:
            match = re.search(pattern, title)
            if match:
                return form, {"field": "benefit.benefit_form", "value": form, "excerpt": title[:120], "extractor": "rule_based", "confidence": 0.75, "inferred": False, "inference_basis": ""}
        default = node.default_benefit_form if node else "cash"
        return default or "cash", None

    @staticmethod
    def _cue_field(text: str, cues: list[tuple[str, str]], field_name: str) -> tuple[str, dict | None]:
        for pattern, value in cues:
            match = re.search(pattern, text)
            if match:
                return value, {"field": field_name, "value": value, "excerpt": _excerpt_for(text, match.start(), match.end()), "extractor": "rule_based", "confidence": 0.7, "inferred": False, "inference_basis": ""}
        return "", None

    def _amount(self, structured: dict, text: str, evidence: list[dict]) -> dict:
        empty = {"type": "unknown", "value": None, "min": None, "max": None, "unit": "TWD", "period": "unknown", "count_per_year": None, "description": "", "tiers": []}
        source_text = structured.get("獎助內容") or structured.get("獲獎金額") or structured.get("補助金額") or structured.get("補助標準") or ""
        # (原文句子, 只拿來讀數字的文字, 抽取器)：門檻子句（所得／財產達 N 元以上）從「讀數字的文字」剔除，摘錄仍是原句
        candidates: list[tuple[str, str, str]] = []
        if source_text:
            candidates.append((source_text, source_text, "structured_field"))
        for sentence in sentences_of(text):
            if "元" not in sentence or len(sentence) > 240:
                continue
            if re.search(r"(獎學金|助學金|補助|津貼|給付|每名|每人|每月|每學期|每學年|每戶|金額|核發|發給|新臺幣|新台幣|上限|最高)", sentence):
                kept = [c for c in (clauses_of(sentence) or [sentence]) if "元" in c and not _is_threshold_clause(c)]
                if kept:
                    candidates.append((sentence, "，".join(kept), "rule_based"))
        for candidate, parse_text, extractor in candidates:
            range_match = re.search(r"([0-9０-９,，]+)\s*[～~\-－至]\s*([0-9０-９,，]+)\s*元", parse_text)
            if range_match:
                low, high = _num(range_match.group(1)), _num(range_match.group(2))
                if low and high and low >= 100:
                    period, count = self._period_of(candidate)
                    evidence.append({"field": "benefit.amount", "value": {"min": low, "max": high}, "excerpt": candidate[:200], "extractor": extractor, "confidence": 0.95 if extractor == "structured_field" else 0.85, "inferred": False, "inference_basis": ""})
                    return {**empty, "type": "range", "min": low, "max": high, "period": period, "count_per_year": count, "description": candidate[:200]}
            if extractor == "structured_field":
                values = [v for v in parse_amounts(parse_text) if v >= 100]
                if values:
                    return self._amount_from_values(values, candidate, extractor, evidence, empty)
        all_values: list[int] = []
        first_sentence = ""
        for candidate, parse_text, extractor in candidates:
            if extractor != "rule_based":
                continue
            values = [v for v in parse_amounts(parse_text) if v >= 100]
            if values:
                if not first_sentence:
                    first_sentence = candidate
                all_values.extend(values)
        if all_values:
            return self._amount_from_values(all_values, first_sentence, "rule_based", evidence, empty)
        window = self._amount_from_windows(text, evidence, empty)
        if window is not None:
            return window
        return {**empty, "description": source_text[:200]}

    def _amount_from_windows(self, text: str, evidence: list[dict], empty: dict) -> dict | None:
        """最後手段：PDF 表格或沒有標點的長段落切不出句子時，改用「金額前後 40 字內有給付語氣」的視窗抓。
        門檻句（所得／財產／不予核給）與明顯是預算總額的數字（≥ 1 千萬）不算。"""
        values: list[int] = []
        best_window = ""
        for match in AMOUNT_RE.finditer(text):
            window = text[max(0, match.start() - 40): match.end() + 12]
            # 給付語氣看整個視窗，否決條件只看金額所在的子句（避免 40 字內剛好提到門檻就整個放棄）
            pieces = AMOUNT_CLAUSE_SPLIT_RE.split(window)
            clause = next((c for c in pieces if match.group(0).strip() in c), window)
            if not AMOUNT_WINDOW_CUE_RE.search(window) or AMOUNT_WINDOW_VETO_RE.search(clause) or _is_threshold_clause(clause):
                continue
            parsed = [v for v in parse_amounts(match.group(0)) if 10 <= v < 10_000_000]  # 每餐 90 元這種小額也要收
            if not parsed:
                continue
            values.extend(parsed)
            if not best_window:
                best_window = " ".join(window.split())
        if not values:
            return None
        return self._amount_from_values(values, best_window, "rule_based_window", evidence, empty)

    BUDGET_SCALE = 100_000_000  # 1 億以上視為預算總額／貸款額度，不是個人給付

    def _amount_from_values(self, values: list[int], excerpt: str, extractor: str, evidence: list[dict], empty: dict) -> dict:
        values = [v for v in values if v < self.BUDGET_SCALE] or values
        period, count = self._period_of(excerpt)
        if len(set(values)) == 1:
            amount = {**empty, "type": "fixed", "value": float(values[0]), "min": float(values[0]), "max": float(values[0]), "period": period, "count_per_year": count, "description": excerpt[:200]}
        else:
            amount = {**empty, "type": "tiered", "min": float(min(values)), "max": float(max(values)), "period": period, "count_per_year": count, "description": excerpt[:200], "tiers": [{"value": v} for v in sorted(set(values))]}
        evidence.append({"field": "benefit.amount", "value": {"values": sorted(set(values))}, "excerpt": excerpt[:200], "extractor": extractor, "confidence": 0.9 if extractor == "structured_field" else 0.8, "inferred": False, "inference_basis": ""})
        return amount

    @staticmethod
    def _period_of(text: str) -> tuple[str, int | None]:
        match = PERIOD_WORD_RE.search(text)
        word = match.group(1) if match else ""
        mapping = {"每月": ("month", 12), "每學期": ("semester", 2), "每學年": ("year", 1), "每年": ("year", 1), "一次性": ("once", 1), "每次": ("once", None), "每日": ("day", None)}
        if word in mapping:
            return mapping[word]
        if re.search(r"每人每月|每月", text):
            return "month", 12
        if re.search(r"學期", text):
            return "semester", 2
        if re.search(r"學年|年度|每年", text):
            return "year", 1
        return "unknown", None

    @staticmethod
    def _annualize(amount: dict) -> float | None:
        base = amount.get("value")
        if base is None:
            low, high = amount.get("min"), amount.get("max")
            if low is None and high is None:
                return None
            base = ((low or high) + (high or low)) / 2
        count = amount.get("count_per_year")
        if amount.get("period") == "unknown" or count is None:
            return float(base)
        return float(base) * count

    def _period(self, structured: dict, text: str, doc: dict, evidence: list[dict]) -> dict:
        empty = {"start_date": "", "end_date": "", "rolling": False, "description": "", "by_school_deadline": bool(re.search(r"依各校公告|各校.{0,6}截止|學校公告之截止", text))}
        source_text = structured.get("申請期間") or structured.get("申請日期") or structured.get("受理期間") or ""
        if source_text:
            start, end = parse_date_range(source_text)
            if end:
                evidence.append({"field": "benefit.application_period", "value": {"start_date": start, "end_date": end}, "excerpt": source_text[:200], "extractor": "structured_field", "confidence": 0.98, "inferred": False, "inference_basis": ""})
                return {**empty, "start_date": start, "end_date": end, "description": source_text[:200]}
            md = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", source_text)
            year_source = to_iso_date(doc.get("published_date") or "") or (doc.get("crawl_time").strftime("%Y-%m-%d") if hasattr(doc.get("crawl_time"), "strftime") else "")
            if md and year_source:
                end = f"{year_source[:4]}-{int(md.group(1)):02d}-{int(md.group(2)):02d}"
                evidence.append({"field": "benefit.application_period.end_date", "value": end, "excerpt": source_text[:200], "extractor": "rule_based", "confidence": 0.75, "inferred": True, "inference_basis": f"原文只有月日，年份取自公告日期 {year_source}"})
                return {**empty, "end_date": end, "description": source_text[:200]}
        if ROLLING_RE.search(text):
            match = ROLLING_RE.search(text)
            evidence.append({"field": "benefit.application_period.rolling", "value": True, "excerpt": _excerpt_for(text, match.start(), match.end()), "extractor": "rule_based", "confidence": 0.85, "inferred": False, "inference_basis": ""})
            start, end = "", ""
            for sentence in sentences_of(text):
                if re.search(r"(受理申請期間|申請期間|受理期間)", sentence):
                    start, end = parse_date_range(sentence)
                    if end:
                        break
            return {**empty, "start_date": start, "end_date": end, "rolling": True, "description": _excerpt_for(text, match.start(), match.end())[:200]}
        for sentence in sentences_of(text):
            if re.search(r"(申請期間|申請期限|受理申請|受理期間|申請日期|收件|截止|報名期間|受理時間)", sentence):
                start, end = parse_date_range(sentence)
                if end:
                    evidence.append({"field": "benefit.application_period", "value": {"start_date": start, "end_date": end}, "excerpt": sentence[:200], "extractor": "rule_based", "confidence": 0.85, "inferred": False, "inference_basis": ""})
                    return {**empty, "start_date": start, "end_date": end, "description": sentence[:200]}
        meta = doc.get("meta") or {}
        deadline = meta.get("deadline_iso") or ""
        if deadline:
            evidence.append({"field": "benefit.application_period.end_date", "value": deadline, "excerpt": f"申請期間(迄)：{meta.get('deadline_roc', deadline)}", "extractor": "structured_field", "confidence": 0.95, "inferred": False, "inference_basis": ""})
            return {**empty, "end_date": deadline, "description": f"申請期間(迄)：{meta.get('deadline_roc', deadline)}"}
        return empty

    APPLY_SECTION_RE = re.compile(
        r"(?:[（(]?[一二三四五六七八九十0-9]+[)）、.]?\s*)?(?:申請|申辦|受理)(?:方式|程序|流程|管道)\s*[:：]?\s*([^\n。]{6,200})"
    )

    def _apply_section(self, text: str) -> str:
        """原文的「申請方式／申辦方式」段落：民眾最需要的一句，之前常留空。"""
        match = self.APPLY_SECTION_RE.search(text or "")
        if not match:
            return ""
        value = " ".join(match.group(1).split())
        return value[:200] if len(value) >= 6 else ""

    def _documents(self, structured: dict, text: str) -> list[str]:
        source = structured.get("繳交文件") or structured.get("申請說明") or structured.get("申請文件") or structured.get("應備文件") or ""
        if not source:
            for sentence in sentences_of(text):
                if DOC_TRIGGER_RE.search(sentence):
                    source = text[text.find(sentence) :][:1500]
                    break
        documents: list[str] = []
        active = bool(structured.get("繳交文件") or structured.get("應備文件"))
        for line in source.splitlines():
            if DOC_TRIGGER_RE.search(line):
                active = True
                continue
            if not active:
                continue
            m = DOC_LINE_RE.match(line)
            if m:
                item = m.group(1).strip()
                if 2 <= len(item) <= 80 and item not in documents and not PROCEDURAL_CUE_RE.search(item) and _looks_like_document(item):
                    documents.append(item)
            if len(documents) >= 12:
                break
        return documents

    @staticmethod
    def _contact(structured: dict, text: str) -> dict:
        source = structured.get("聯絡資訊") or structured.get("發布單位") or ""
        haystack = source or text
        phone = PHONE_RE.search(haystack)
        email = EMAIL_RE.search(haystack)
        return {"phone": phone.group(0).strip() if phone else "", "email": email.group(0) if email else "", "department": source[:120]}

    @staticmethod
    def _first_sentence_with(text: str, pattern: str) -> str:
        for sentence in sentences_of(text):
            if re.search(pattern, sentence):
                return sentence[:300]
        return ""

    # ======================================================= structured rules
    def _structured_rules(self, structured: dict, text: str, jurisdiction: str | None, rules: list[dict], evidence: list[dict]) -> None:
        """圓夢助學網等來源的標籤欄位（學制／成績／獎助身分／戶籍地限制）：高信心規則。"""
        level_text = structured.get("學制") or ""
        if level_text and level_text not in {"不拘", "不限", "無"}:
            levels = self._levels_in(level_text)
            if levels:
                rules.append(self._rule("education.level", "in", levels, group_id="education", human=f"教育階段：{'／'.join(self.registry.get('education.level').value_label(l) for l in levels)}", excerpt=f"學制：{level_text}"[:200], confidence=0.95, extractor="structured_field", condition_text=level_text))
                evidence.append({"field": "education.level", "value": levels, "excerpt": f"學制：{level_text}"[:200], "extractor": "structured_field", "confidence": 0.95, "inferred": False, "inference_basis": ""})
        residence_text = structured.get("戶籍地限制") or ""
        cities = find_cities(residence_text) if residence_text else []
        if cities:
            rules.append(self._rule("residence.household_city", "in", cities, group_id="residence", human="戶籍地：" + "／".join(cities), excerpt=f"戶籍地限制：{residence_text}", confidence=0.98, extractor="structured_field", condition_text=residence_text))
            evidence.append({"field": "residence.household_city", "value": cities, "excerpt": f"戶籍地限制：{residence_text}", "extractor": "structured_field", "confidence": 0.98, "inferred": False, "inference_basis": ""})
        score_text = structured.get("成績") or ""
        if score_text and score_text not in {"不拘", "不限"}:
            seen: set[str] = set()
            for label, attribute_id in (("平均", "academic.average_score"), ("智育", "academic.average_score"), ("德育", "academic.conduct_score"), ("操行", "academic.conduct_score"), ("體育", None)):
                if attribute_id is None:
                    continue
                m = re.search(rf"{label}[^:：\d]*[:：]\s*([0-9０-９]{{2,3}})", score_text)
                if m and attribute_id not in seen:
                    value = _num(m.group(1))
                    if value is None:
                        continue
                    seen.add(attribute_id)
                    rules.append(self._rule(attribute_id, ">=", value, unit="score", group_id=attribute_id.replace(".", "_"), human=f"{self.registry.get(attribute_id).label} ≥ {value:g}", excerpt=f"成績：{score_text}"[:200], confidence=0.98, extractor="structured_field", condition_text=score_text))
        identity_text = structured.get("獎助身分") or ""
        if identity_text and not re.search(r"(不拘|不限|一般生|無限制)", identity_text):
            tags = self.registry.tags_in_text(identity_text)
            for tag_id, alias in tags.items():
                tag = self.registry.tags[tag_id]
                rules.append(self._rule("identity.tags", "contains", tag_id, group_id="identity_any", human=f"身分：{tag.label}", excerpt=f"獎助身分：{identity_text}"[:200], confidence=0.95, extractor="structured_field", condition_text=identity_text))
                evidence.append({"field": "identity.tags", "value": tag.label, "excerpt": f"獎助身分：{identity_text}"[:200], "extractor": "structured_field", "confidence": 0.95, "inferred": False, "inference_basis": ""})
        program_text = structured.get("獎助資格") or ""
        if program_text and program_text not in {"不拘", "不限"}:
            tags = self.registry.tags_in_text(program_text)
            for tag_id in tags:
                if not any(r["attribute_id"] == "identity.tags" and r["value"] == tag_id for r in rules):
                    tag = self.registry.tags[tag_id]
                    rules.append(self._rule("identity.tags", "contains", tag_id, group_id="identity_any", human=f"身分：{tag.label}", excerpt=f"獎助資格：{program_text}"[:200], confidence=0.9, extractor="structured_field", condition_text=program_text))

    def _levels_in(self, text: str) -> list[str]:
        levels: list[str] = []
        for pattern, mapped in LEVEL_PATTERNS:
            if re.search(pattern, text):
                for level in mapped:
                    if level not in levels:
                        levels.append(level)
        return [l for l in LEVEL_ORDER if l in levels]

    def _title_identity_rules(self, title: str, rules: list[dict], evidence: list[dict]) -> None:
        """標題中的身分（例如「清寒優秀學生獎學金」「身心障礙者生活補助」）是必要條件（AND）。"""
        for tag_id, alias in self.registry.tags_in_text(title).items():
            tag = self.registry.tags[tag_id]
            if tag.virtual:
                continue
            if any(r["attribute_id"] == "identity.tags" and r["value"] == tag_id for r in rules):
                continue
            rules.append(self._rule("identity.tags", "contains", tag_id, group_id=f"identity_required_{tag_id}", human=f"身分：{tag.label}", excerpt=title, confidence=0.9, extractor="rule_based", condition_text=title))
            evidence.append({"field": "identity.tags", "value": tag.label, "excerpt": title, "extractor": "rule_based", "confidence": 0.9, "inferred": False, "inference_basis": "標題含身分名稱"})

    # ======================================================= condition rules
    def _condition_sentences(self, text: str, structured: dict) -> list[tuple[str, bool]]:
        """優先取「申請資格／補助對象」段落（in_region=True）；沒有段落標記時，取含條件提示詞的句子。"""
        region_source = structured.get("限制條件") or structured.get("申請資格") or ""
        pool: list[tuple[str, bool]] = [(s, True) for s in sentences_of(region_source)] if region_source else []
        all_sentences = sentences_of(text)
        in_region = False
        region: list[str] = []
        for sentence in all_sentences:
            if SECTION_START_RE.search(sentence):
                in_region = True
                region.append(sentence)
                continue
            if in_region and SECTION_END_RE.search(sentence) and not SECTION_START_RE.search(sentence):
                in_region = False
            if in_region:
                region.append(sentence)
        seen = {s for s, _ in pool}
        for s in region:
            if s not in seen:
                pool.append((s, True))
                seen.add(s)
        if len(pool) < 3:
            for sentence in all_sentences:
                if sentence in seen or len(sentence) > 300:
                    continue
                norm = normalize_text(sentence)
                if any(normalize_text(cue) in norm for cue in self.condition_cues) and (NUM_TOKEN_RE.search(sentence) or self.registry.tags_in_text(sentence) or self.registry.attributes_in_text(sentence)):
                    pool.append((sentence, False))
                    seen.add(sentence)
        return pool[:120]

    def _condition_rules(self, text: str, structured: dict, jurisdiction: str | None, rules: list[dict], evidence: list[dict], conditions: list[dict]) -> None:
        inherited_role = ""
        inherited_left = 0
        alt_group = ""
        alt_left = 0
        alt_counter = 0
        alt_header_kind = ""
        category = getattr(self, "current_category", "")
        domain = self.registry.domain_of(category) if category else ""
        domain_candidates = [a.id for a in self.registry.for_domains([domain] if domain else None) if a.hard_filter and a.type != "text"][:6]
        for sentence, in_region in self._condition_sentences(text, structured):
            sentence_role = "required"
            if EXCLUSION_CUE_RE.search(sentence):
                sentence_role = "exclusion"
            elif STRONG_BONUS_RE.search(sentence):
                sentence_role = "bonus"  # 「具…證明者為優先獎助對象」：即使句中有「限於設定名額」也還是優先順序，不是資格
            elif BONUS_CUE_RE.search(sentence) and not re.search(r"(應|須|必須|限|僅)", sentence):
                sentence_role = "bonus"
            # 「有下列情形之一者不得申請：」→ 接下來的條列句繼承排除語氣
            is_list_item = bool(LIST_ITEM_RE.match(sentence))
            if SECTION_START_RE.search(sentence):
                inherited_left = 0  # 新的段落標題（申請資格／補助對象…）：前一段的排除語氣不再往後蓋
            if inherited_left > 0 and is_list_item and sentence_role == "required" and not BONUS_CUE_RE.search(sentence):
                sentence_role = inherited_role
                inherited_left -= 1
            elif not is_list_item and not EXCEPTION_PREFIX_RE.match(sentence) and len(sentence) > 12:
                inherited_left = 0
            if sentence_role == "exclusion" and sentence.rstrip().endswith(("：", ":")):
                inherited_role, inherited_left = "exclusion", 8
            # 「符合下列條件之一：」「下列對象之一：」→ 接下來的條列句彼此是 OR（同一群組）
            if alt_left > 0 and is_list_item:
                alt_left -= 1
            elif not is_list_item and not EXCEPTION_PREFIX_RE.match(sentence) and len(sentence) > 12:
                alt_left = 0
                alt_group = ""
            if alt_left > 0 and alt_header_kind and list_item_kind(sentence) == alt_header_kind:
                # 回到引導句自己的層級（「三、符合下列之一：」→「四、…」）：擇一群組到此結束
                alt_left, alt_group = 0, ""
                current_alt_group = ""
            if OR_LIST_HEADER_RE.search(sentence) and sentence.rstrip().endswith(("：", ":")) and sentence_role != "exclusion":
                alt_counter += 1
                alt_group, alt_left = f"alternative_{alt_counter}", 10
                alt_header_kind = list_item_kind(sentence)
            current_alt_group = alt_group if (alt_left > 0 and is_list_item) else ""
            attributes = self.registry.attributes_in_text(sentence)
            tags = self.registry.tags_in_text(sentence)
            # 例外／但書句（但、惟、除…）與過長的句子不直接產生規則，交給本地 AI
            if EXCEPTION_PREFIX_RE.match(sentence) or len(sentence) > 180:
                candidates = [a for a in self.registry.attributes_in_text(sentence, include_mined=True).keys() if self.registry.get(a) and self.registry.get(a).type != "text"][:6]
                conditions.append({"text": sentence[:200], "excerpt": sentence[:200], "role": sentence_role, "status": "unmapped", "attribute_id": None, "candidates": candidates or domain_candidates, "method": "rule"})
                continue
            if not attributes and not tags:
                if PROCEDURAL_CUE_RE.search(sentence) or DOCUMENT_LINE_RE.search(sentence):
                    conditions.append({"text": sentence[:200], "excerpt": sentence[:200], "role": "procedural", "status": "procedural", "attribute_id": None, "method": "rule"})
                elif in_region and len(sentence) <= 220 and not NAV_LINE_RE.search(sentence) and re.search(r"(者|符合|具|經|限|須|應|滿|以上|以下|未)", sentence):
                    conditions.append({"text": sentence[:200], "excerpt": sentence[:200], "role": sentence_role, "status": "unmapped", "attribute_id": None, "candidates": domain_candidates, "method": "rule"})
                continue
            if PROCEDURAL_CUE_RE.search(sentence) and not NUM_TOKEN_RE.search(sentence) and not tags and len(attributes) <= 1 and "名額" in sentence:
                conditions.append({"text": sentence[:200], "excerpt": sentence[:200], "role": "procedural", "status": "procedural", "attribute_id": None, "method": "rule"})
                continue
            produced_any = False
            clause_list = clauses_of(sentence) or [sentence]
            before_count = len(rules)
            self._current_alt_group = current_alt_group
            # 「A 達 X 以上，或 B 達 Y 以上，不予核給」：排除詞在句尾、而且那個子句本身沒有條件（只是判決），
            # 排除語氣要回溯套用到前面所有子句；否則排除語氣只作用在含排除詞的子句及其後方子句
            verdict_only_tail = False
            if sentence_role == "exclusion" and len(clause_list) > 1:
                cue_index = next((i for i, c in enumerate(clause_list) if EXCLUSION_CUE_RE.search(c)), None)
                if cue_index is not None:
                    tail = clause_list[cue_index]
                    verdict_only_tail = cue_index == len(clause_list) - 1 and not NUM_TOKEN_RE.search(tail) and not self.registry.attributes_in_text(tail) and not self.registry.tags_in_text(tail)
            for clause in clause_list:
                clause_role = sentence_role
                if EXCLUSION_CUE_RE.search(clause):
                    clause_role = "exclusion"
                elif sentence_role == "exclusion" and inherited_left == 0 and len(clause_list) > 1 and not verdict_only_tail:
                    position = sentence.find(clause)
                    cue = EXCLUSION_CUE_RE.search(sentence)
                    clause_role = "exclusion" if (cue and position >= cue.start() - 2) else "required"
                produced = self._clause_rules(clause, sentence, clause_role, jurisdiction, rules, evidence)
                produced_any = produced_any or produced
            if produced_any and len(rules) - before_count > 5:
                # 一句話產生太多規則 → 語意太複雜，整句改交給本地 AI
                # （門檻 5：「年滿65歲或領有身障證明，且設籍本市滿六個月」會產生 4 條，屬正常資格句）
                del rules[before_count:]
                produced_any = False
            if produced_any:
                conditions.append({"text": sentence[:200], "excerpt": sentence[:200], "role": sentence_role, "status": "mapped", "attribute_id": None, "method": "rule"})
            else:
                candidates = [a for a in self.registry.attributes_in_text(sentence, include_mined=True).keys() if self.registry.get(a) and self.registry.get(a).type != "text"][:5]
                for tag_id in tags:
                    tag_attr = self.registry.tag_attribute(tag_id)
                    if tag_attr and tag_attr not in candidates:
                        candidates.append(tag_attr)
                conditions.append({"text": sentence[:200], "excerpt": sentence[:200], "role": sentence_role, "status": "unmapped", "attribute_id": None, "candidates": (candidates or domain_candidates)[:6], "method": "rule"})

    def _clause_rules(self, clause: str, sentence: str, role: str, jurisdiction: str | None, rules: list[dict], evidence: list[dict]) -> bool:
        registry = self.registry
        produced = False
        before_clause = len(rules)
        attributes = registry.attributes_in_text(clause)
        tags = registry.tags_in_text(clause)
        alternative = bool(re.search(r"(或|之一|任一|擇一)", clause))

        # ---- 身分標籤（同一子句多個身分 → OR 群組）
        tag_ids = [t for t in tags if not registry.tags[t].virtual]
        if tag_ids:
            group_id = "identity_any" if (len(tag_ids) > 1 or alternative) else f"identity_required_{tag_ids[0]}"
            if getattr(self, "_current_alt_group", "") and role != "exclusion":
                group_id = self._current_alt_group
            for tag_id in tag_ids:
                tag = registry.tags[tag_id]
                if any(r["attribute_id"] == "identity.tags" and r["value"] == tag_id and r["role"] == ("exclusion" if role == "exclusion" else "required") for r in rules):
                    continue
                negated = bool(NEGATION_BEFORE_RE.search(clause[: clause.find(tags[tag_id])])) if tags[tag_id] in clause else False
                if (role == "exclusion" or negated) and tag_id in registry.tags_in_text(getattr(self, "_current_title", "") or ""):
                    continue  # 排除句裡出現方案自己的受益身分（榮民子女獎助學金排除榮民子女）＝抓錯對象，不寫規則
                operator = "not_in" if (role == "exclusion" or negated) else "contains"
                value = [tag_id] if operator == "not_in" else tag_id
                rules.append(self._rule("identity.tags", operator, value, group_id=f"exclusion_identity_{tag_id}" if operator == "not_in" else group_id, human=("排除身分：" if operator == "not_in" else "身分：") + tag.label, excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion" if operator == "not_in" else ("bonus" if role == "bonus" else "required")))
                produced = True
            # 身分別名已處理，避免同一子句再被當成 boolean 屬性重複產生
            for tag_id in tag_ids:
                attributes.pop(registry.tag_attribute(tag_id), None)

        # ---- 一般屬性
        if DOCUMENT_LINE_RE.search(clause) or NAV_LINE_RE.search(clause) or len(sentence) > 260:
            return produced
        current_domain = registry.domain_of(getattr(self, "current_category", "") or "")
        for attribute_id, aliases in attributes.items():
            attribute = registry.get(attribute_id)
            if attribute is None or attribute.derived or attribute.type == "text":
                continue
            if current_domain and "all" not in attribute.domains and current_domain not in attribute.domains:
                continue  # 其他領域的屬性（例如教育公告裡的「照顧者」）不產生規則
            if attribute.id == "applicant.age" and getattr(self, "current_category", "") in CHILD_AGE_CATEGORIES:
                attribute = registry.get("family.youngest_child_age") or attribute
            alias = aliases[0]
            pos = clause.find(alias)
            before = clause[:pos] if pos >= 0 else ""
            after = clause[pos + len(alias) :] if pos >= 0 else clause
            # 「無自有住宅」「未領有身心障礙證明」：否定詞緊接在屬性別名前面也算否定（原規則要求否定詞後面接動詞）
            # 別名本身就是否定寫法（登錄表把「無自有住宅」也列為 housing.owns_property 的別名）
            negated = bool(NEGATION_BEFORE_RE.search(before)) or bool(NEGATION_ADJACENT_RE.search(before)) or bool(NEGATION_SCOPE_RE.search(before)) or bool(NEGATED_ALIAS_RE.match(alias))
            exclusion = role == "exclusion"
            rule: dict | None = None
            if attribute.type == "number":
                rule = self._number_rule(attribute, clause, alias, before, after, sentence, exclusion)
            elif attribute.type == "boolean":
                if not REQUIRE_CUE_RE.search(clause):
                    continue
                if _is_threshold_clause(clause):
                    continue  # 「土地及房屋價值合計未超過450萬元」是財產門檻，不是「必須有自有住宅」
                value = not negated
                if exclusion:
                    value = not value
                rule = self._rule(attribute_id, "=", value, group_id=("exclusion_" if exclusion else "") + attribute.namespace + "_" + attribute.id.split(".")[1], human=f"{attribute.label}：{'是' if value else '否'}", excerpt=sentence[:200], confidence=0.8, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else ("bonus" if role == "bonus" else "required"))
            elif attribute.type == "enum":
                rule = self._enum_rule(attribute, clause, alias, after, sentence, exclusion != negated)
            elif attribute.type == "city":
                rule = self._city_rule(attribute, clause, alias, sentence, jurisdiction, exclusion != negated, evidence)
            elif attribute.type == "multi_enum" and attribute_id == "financial.receiving_other_benefit":
                kinds = []
                if re.search(r"獎學金|獎助", clause):
                    kinds.append("government_scholarship")
                if re.search(r"減免", clause):
                    kinds.append("tuition_waiver")
                if re.search(r"助學金", clause):
                    kinds.append("student_aid")
                if re.search(r"津貼|生活補助|補助", clause):
                    kinds.append("living_allowance")
                if not kinds:
                    kinds = ["government_scholarship", "tuition_waiver", "student_aid", "living_allowance"]
                rule = self._rule(attribute_id, "not_in", kinds, group_id="exclusion_other_benefit", human="不得同時領取：" + "、".join(attribute.value_label(k) for k in kinds), excerpt=sentence[:200], confidence=0.7, extractor="rule_based", condition_text=clause, role="exclusion")
            if rule is None:
                continue
            if role == "bonus" and rule["role"] == "required":
                rule["role"] = "bonus"
                rule["group_id"] = "priority"
            if attribute_id == "residence.household_city" and "設籍" in clause:
                months = parse_duration_months(clause)
                if months and not any(r["attribute_id"] == "residence.duration_months" for r in rules):
                    rules.append(self._rule("residence.duration_months", ">=", months, unit="months", group_id="residence_duration", human=f"設籍滿 {months} 個月以上", excerpt=sentence[:200], confidence=0.9, extractor="rule_based", condition_text=clause))
            if getattr(self, "_current_alt_group", ""):
                if rule["role"] == "required" and attribute_id in OR_GROUPABLE_ATTRIBUTES:
                    # 條列「符合下列之一」：身分型條件就是那幾個選項
                    rule["group_id"] = self._current_alt_group
                    rule["human_readable"] = rule["human_readable"] + "（擇一）"
                else:
                    # 其他屬性是「某一條路徑自己的細節」，不是全案條件；當成全案條件會與別條路徑矛盾
                    rule["complexity"] = "complex"
                    if "（擇一條件之一的細項）" not in rule["human_readable"]:
                        rule["human_readable"] = rule["human_readable"] + "（擇一條件之一的細項）"
            if not self._duplicate(rules, rule):
                rules.append(rule)
                produced = True
        # 同一子句用「或／之一／任一／擇一」並列的條件（例如「年滿65歲或領有身心障礙證明」）→ 同一個 OR 群組，
        # 否則不同屬性會落在不同群組而被當成必須同時成立。
        # 只把「或」前後緊鄰的條件收進同一組：「設籍本市之低收入戶或中低收入戶」裡的「設籍本市」不是選項之一。
        if alternative and not getattr(self, "_current_alt_group", ""):
            # 只把「身分條件」收進 OR 群組（低收入戶或中低收入戶、年滿65歲或領有身障證明）；
            # 設籍、所得、學制這類條件即使句子裡有「或」也維持各自獨立（避免把必要條件變成可選）
            produced_rules = [r for r in rules[before_clause:] if r.get("role") == "required" and r["attribute_id"] in OR_GROUPABLE_ATTRIBUTES]
            if len(produced_rules) > 1:
                self._any_group_counter = getattr(self, "_any_group_counter", 0) + 1
                group = f"clause_any_{self._any_group_counter}"
                for rule in produced_rules:
                    rule["group_id"] = group
                    if "（擇一）" not in rule["human_readable"]:
                        rule["human_readable"] = rule["human_readable"] + "（擇一）"
        return produced

    def _number_rule(self, attribute: Attribute, clause: str, alias: str, before: str, after: str, sentence: str, exclusion: bool) -> dict | None:
        unit_map = {"years": {"歲", "年"}, "months": {"個月", "月", "年"}, "score": {"分"}, "TWD": {"元"}, "TWD_year": {"元"}, "TWD_month": {"元"}, "percent": {"%", "％"}, "level": {"級"}, "multiple": {"倍"}, "gpa": set(), "": set()}
        allowed_units = NUMBER_UNITS.get(attribute.id, unit_map.get(attribute.unit, set()))
        if not allowed_units and attribute.unit != "gpa":
            return None  # 無單位的數值屬性不用「最近的數字」猜
        range_match = RANGE_RE.search(clause)
        if range_match and (range_match.group(3) in allowed_units):
            low, high = _num(range_match.group(1)), _num(range_match.group(2))
            if low is not None and high is not None:
                low, high = self._convert_unit(attribute, low, range_match.group(3)), self._convert_unit(attribute, high, range_match.group(3))
                return self._rule(attribute.id, "between", [low, high], unit=attribute.unit, group_id=attribute.id.replace(".", "_"), human=f"{attribute.label}：{low:g}～{high:g}", excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")
        candidates: list[tuple[re.Match, str]] = []
        for match in NUM_TOKEN_RE.finditer(clause):
            unit = match.group(3) or ""
            if attribute.unit == "gpa":
                if unit or not re.search(r"gpa", clause, re.I):
                    continue
            elif unit not in allowed_units:
                continue
            candidates.append((match, unit))
        if not candidates:
            return None
        pos = clause.find(alias)
        # 中文條件句多半是「屬性 … 達／滿 N 單位 以上」：優先配對別名後方的數字；
        # 用前方的數字時，數字與別名之間不能夾著別的屬性（「所得達一百萬元以上或不動產價值達一千萬元」不能把一百萬配給不動產）
        other_aliases = [a for aid, als in self.registry.attributes_in_text(clause).items() if aid != attribute.id for a in als]
        after = sorted([c for c in candidates if c[0].start() >= pos + len(alias)], key=lambda c: c[0].start() - pos)
        before = sorted([c for c in candidates if c[0].start() < pos], key=lambda c: pos - c[0].start())
        chosen = None
        if after and after[0][0].start() - pos <= 40:
            chosen = after[0]
        elif before and pos - before[0][0].start() <= 40:
            between = clause[before[0][0].end() : pos]
            if not any(a in between for a in other_aliases):
                chosen = before[0]
        if chosen is None:
            return None  # 數字離屬性別名太遠或中間夾了別的屬性，不視為同一條件
        match, unit = chosen
        value = _num(match.group(1))
        if value is None:
            return None
        if match.group(2):
            value *= 10000
        value = self._convert_unit(attribute, value, unit)
        qual_before = QUAL_BEFORE_RE.search(clause[: match.start()])
        qual_after = QUAL_AFTER_RE.search(clause[match.end() :])
        qualifier = (qual_before.group(1) if qual_before else "") + (qual_after.group(1) if qual_after else "")
        if re.search(r"(未滿|前|以前)", qualifier):
            operator = "<"
        elif re.search(r"(以下|以內|未達|低於|不超過|不逾|未逾|未超過|以下者)", qualifier):
            operator = "<="
        elif re.search(r"(以上|滿|年滿|已滿|達|至少|超過|逾|高於|以上者|之後|後)", qualifier):
            operator = ">="
        else:
            return None
        if exclusion:
            operator = {">=": "<", ">": "<=", "<=": ">", "<": ">="}[operator]
        symbol = {">=": "≥", "<=": "≤", "<": "<", ">": ">"}[operator]
        unit_label = {"years": "歲", "months": "個月", "score": "分", "TWD": "元", "TWD_year": "元／年", "TWD_month": "元／月", "percent": "%", "level": "級", "multiple": "倍", "gpa": ""}.get(attribute.unit, "")
        if attribute.id == "applicant.age" and not (5 <= value <= 120):
            return None
        if attribute.unit == "score" and not (0 < value <= 100):
            return None
        return self._rule(attribute.id, operator, value, unit=attribute.unit, group_id=attribute.id.replace(".", "_"), human=f"{attribute.label} {symbol} {value:g}{unit_label}", excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")

    @staticmethod
    def _convert_unit(attribute: Attribute, value: float, unit: str) -> float:
        if attribute.unit == "months" and unit == "年":
            return value * 12
        if attribute.unit == "TWD_year" and unit == "元" and False:
            return value
        return value

    def _enum_rule(self, attribute: Attribute, clause: str, alias: str, after: str, sentence: str, exclusion: bool) -> dict | None:
        if attribute.id == "education.level":
            levels = self._levels_in(clause)
            if not levels:
                return None
            operator = "not_in" if exclusion else "in"
            return self._rule(attribute.id, operator, levels, group_id="education", human=("排除教育階段：" if exclusion else "教育階段：") + "／".join(attribute.value_label(l) for l in levels), excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")
        if attribute.id == "education.program_type":
            found = [value for pattern, value in PROGRAM_TYPE_TERMS if re.search(pattern, clause)]
            if not found:
                return None
            if exclusion or re.search(r"不含|不包括|除外|排除|不得", clause):
                return self._rule(attribute.id, "not_in", found, group_id="program_type", human="不含：" + "／".join(attribute.value_label(v) for v in found), excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion")
            return self._rule(attribute.id, "in", found, group_id="program_type", human="限：" + "／".join(attribute.value_label(v) for v in found), excerpt=sentence[:200], confidence=0.8, extractor="rule_based", condition_text=clause, role="required")
        if attribute.id == "education.school_type":
            # 「公私立大專校院」是「公立或私立都可以」，不是限私立；只有「限公立／私立學校為限」才是限制
            if "公私立" in clause or "公、私立" in clause:
                return None
            restriction = re.search(r"(?:限|僅限|以)\s*(公立|私立)|(公立|私立)\s*(?:學校)?\s*為限", clause)
            if not restriction:
                return None
        values_found = [v for v in attribute.value_list if v and v in clause]
        labels_found = [v.get("value") for v in attribute.values if v.get("label") and str(v.get("label")) in clause and v.get("value") not in values_found]
        found = list(dict.fromkeys([*values_found, *labels_found]))
        if not found:
            # 有序 enum 才允許用「中度以上」推 >=
            return None
        if attribute.ordered and len(found) == 1:
            qualifier = clause[clause.find(str(found[0])) + len(str(found[0])) :][:4]
            if "以上" in qualifier:
                operator = "<" if exclusion else ">="
                return self._rule(attribute.id, operator, found[0], group_id=attribute.id.replace(".", "_"), human=f"{attribute.label}：{attribute.value_label(found[0])}以上", excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")
            if "以下" in qualifier:
                operator = ">" if exclusion else "<="
                return self._rule(attribute.id, operator, found[0], group_id=attribute.id.replace(".", "_"), human=f"{attribute.label}：{attribute.value_label(found[0])}以下", excerpt=sentence[:200], confidence=0.85, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")
        operator = "not_in" if exclusion else "in"
        return self._rule(attribute.id, operator, found, group_id=attribute.id.replace(".", "_"), human=f"{attribute.label}：" + "／".join(attribute.value_label(v) for v in found), excerpt=sentence[:200], confidence=0.8, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")

    def _city_rule(self, attribute: Attribute, clause: str, alias: str, sentence: str, jurisdiction: str | None, exclusion: bool, evidence: list[dict]) -> dict | None:
        cities = find_cities(clause)
        inferred = False
        basis = ""
        if not cities and re.search(r"本市|本縣|本鄉|本鎮|本區", clause):
            if self.settings.infer_jurisdiction_from_provider and jurisdiction:
                cities = [jurisdiction]
                inferred = True
                basis = f"原文寫「{re.search(r'本市|本縣|本鄉|本鎮|本區', clause).group(0)}」，依機關名稱／標題中的「{jurisdiction}」推定"
            else:
                # 原文只寫「本市」又推不出縣市：當成需人工／語意確認的佔位條件，不要留一條沒有值的簡單規則
                return self._rule(attribute.id, "exists", None, group_id=attribute.id.replace(".", "_"), human=f"{attribute.label}（原文只寫「本市」，未寫明縣市）", excerpt=sentence[:200], confidence=0.6, extractor="rule_based", condition_text=clause, complexity="complex")
        if not cities:
            return None
        if jurisdiction and jurisdiction not in cities:
            # 原文提到別的縣市（鄰近縣市併計年資、受理機關所在地…）不是本方案的戶籍限制；
            # 若真的限定別縣市，本方案的機關轄區也不會是這個縣市
            return None
        if ALTERNATIVE_PREFIX_RE.search(sentence[: sentence.find(clause)] if clause in sentence else ""):
            return self._rule(attribute.id, "in", cities, group_id=attribute.id.replace(".", "_") + "_alternative", human=f"{attribute.label}：{'／'.join(cities)}（擇一條件）", excerpt=sentence[:200], confidence=0.6, extractor="rule_based", condition_text=clause, complexity="complex")
        operator = "not_in" if exclusion else "in"
        rule = self._rule(attribute.id, operator, cities, group_id=("exclusion_" if exclusion else "") + attribute.id.replace(".", "_"), human=f"{attribute.label}：" + "／".join(cities) + ("（依機關推定）" if inferred else ""), excerpt=sentence[:200], confidence=0.7 if inferred else 0.9, extractor="rule_based", condition_text=clause, role="exclusion" if exclusion else "required")
        rule["inferred"] = inferred
        rule["inference_basis"] = basis
        return rule

    # ================================================================ helpers
    def _rule(self, attribute_id: str, operator: str, value: Any, *, group_id: str, human: str, excerpt: str, confidence: float, extractor: str, condition_text: str = "", role: str = "required", unit: str = "", complexity: str = "simple") -> dict:
        attribute = self.registry.get(attribute_id)
        return {
            "id": _new_id(),
            "attribute_id": attribute_id,
            "operator": operator,
            "value": value,
            "unit": unit or (attribute.unit if attribute else ""),
            "group_id": group_id,
            "group_logic": "any",
            "complexity": complexity,
            "role": role,
            "human_readable": human[:200],
            "evidence": {"excerpt": excerpt[:300], "extractor": extractor, "condition_text": condition_text[:200]},
            "confidence": confidence,
            "inferred": False,
            "inference_basis": "",
            "registry_version": self.registry.version,
        }

    @staticmethod
    def _duplicate(rules: list[dict], rule: dict) -> bool:
        for existing in rules:
            if existing["attribute_id"] == rule["attribute_id"] and existing["operator"] == rule["operator"] and existing["value"] == rule["value"] and existing["role"] == rule["role"]:
                return True
        return False

    @staticmethod
    def _dedupe_rules(rules: list[dict]) -> None:
        seen: set[tuple] = set()
        kept: list[dict] = []
        for rule in rules:
            key = (rule["attribute_id"], rule["operator"], repr(rule["value"]), rule["role"])
            if key in seen:
                continue
            seen.add(key)
            kept.append(rule)
        rules[:] = kept

    @staticmethod
    def _overall_confidence(evidence: list[dict], rules: list[dict]) -> float:
        values = [float(e.get("confidence", 0)) for e in evidence] + [float(r.get("confidence", 0)) for r in rules]
        if not values:
            return 0.3
        return round(sum(values) / len(values), 3)

    @staticmethod
    def build_index(benefit: dict) -> dict:
        rules = benefit.get("rules") or []
        cities: list[str] = []
        levels: list[str] = []
        tags: list[str] = []
        for rule in rules:
            if rule["attribute_id"] == "residence.household_city" and rule["operator"] == "in" and isinstance(rule["value"], list):
                cities.extend(c for c in rule["value"] if c not in cities)
            if rule["attribute_id"] == "education.level" and rule["operator"] == "in" and isinstance(rule["value"], list):
                levels.extend(l for l in rule["value"] if l not in levels)
            if rule["attribute_id"] == "identity.tags" and rule["operator"] == "contains":
                tags.append(str(rule["value"]))
        amount = benefit.get("benefit", {}).get("amount", {})
        return {
            "attribute_ids": sorted({r["attribute_id"] for r in rules}),
            "residence_cities": cities,
            "education_levels": levels,
            "tags_required": sorted(set(tags)),
            "amount_min": amount.get("min"),
            "amount_max": amount.get("max"),
            "application_end": benefit.get("benefit", {}).get("application_period", {}).get("end_date", ""),
            "simple_rules": sum(1 for r in rules if r["complexity"] == "simple" and r["role"] != "bonus"),
            "complex_rules": sum(1 for r in rules if r["complexity"] == "complex"),
        }
