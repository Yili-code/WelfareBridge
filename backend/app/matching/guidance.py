"""Choose follow-ups from unresolved eligibility rules, retaining explicit answers."""
import re
from . import MatchingEngine, Profile, load_records, parse_profile_text, plan_questions
from ..db import get_db
from ..registry import get_registry

YES_WORDS = {"是", "有", "對", "是的", "有的", "對的", "沒錯", "有喔", "是喔", "對啊", "是啊", "有啊", "yes", "y"}
NO_WORDS = {"否", "沒有", "沒", "不是", "無", "沒有喔", "不是喔", "沒有啊", "不是啊", "不對", "沒有的", "no", "n"}


TOPICS = {
    'education': ('就學', '學費', '獎學金', '助學', '學貸', '念書', '讀書', '大學', '學生', '註冊'),
    'housing': ('租屋', '房租', '租金', '住宅', '買房', '購屋', '房貸', '修繕', '住的地方', '搬家'),
    'labor': ('失業', '求職', '職訓', '裁員', '被資遣', '資遣', '找工作', '轉職', '創業', '離職', '打工'),
    'health': ('醫療', '健保', '看病', '就醫', '住院', '重病', '癌', '手術', '醫藥費'),
    'disability': ('身障', '身心障礙', '殘障', '輔具', '早療', '發展遲緩'),
    'long_term_care': ('長照', '照顧', '照護', '失智', '看護', '居家服務', '日間照顧', '老人', '長輩', '臥床'),
    'social_welfare': ('生活費', '育兒', '急難', '缺錢', '單親', '托育', '育嬰', '生育', '津貼', '低收', '生活困難', '養小孩', '撫養', '喪葬'),
}
UNSURE = "unsure"
HEDGES = ("應該", "好像", "可能", "大概", "似乎", "也許", "不太確定", "不確定", "不知道", "不清楚", "還在申請", "申請中", "審核中", "還沒下來")
UNSURE_PHRASES = ("不太確定", "不確定", "不知道", "不清楚", "不太清楚", "不曉得", "沒概念", "忘了")
GRADE_RE = re.compile(r"(?:大|高|國|研)[一二三四五六七八九]|[一二三四五六七八九]年級")
OTHER_PEOPLE = ("朋友", "同學", "別人", "鄰居", "同事")


STUDENT_ONLY = ('education.grade', 'education.program_type', 'education.is_freshman', 'education.extended_study', 'education.years_in_program', 'education.school_city', 'education.school',
                'education.school_type', 'education.department', 'academic.average_score', 'academic.conduct_score', 'academic.gpa', 'academic.ranking_percent', 'academic.subject_min_score',
                'academic.no_disciplinary_record', 'academic.no_failed_subject', 'financial.receiving_public_funding', 'financial.student_loan')
# 子題 → (前提題, 前提必須的答案)；前提已明確答成別的，就不用問子題
DEPENDS = {
    'disability.certificate_level': ('disability.has_certificate', True), 'disability.category': ('disability.has_certificate', True),
    'identity.indigenous_tribe': ('identity.indigenous', True),
    'care.cms_level': ('care.needs_care', True), 'care.adl_score': ('care.needs_care', True), 'care.institutional_placement': ('care.needs_care', True), 'care.has_foreign_caregiver': ('care.needs_care', True),
    'employment.involuntary_separation': ('employment.status', 'unemployed'), 'employment.unemployed_months': ('employment.status', 'unemployed'), 'employment.insured_years': ('financial.labor_insured', True),
    'housing.rent_month': ('housing.tenure', 'rent'),
    **{attribute_id: ('applicant.is_student', True) for attribute_id in STUDENT_ONLY},
}


def blocked(attribute_id, profile, registry):
    if attribute_id == 'identity.middle_low_income' and profile.value('identity.low_income', registry) is True:
        return True  # 已是低收入戶就不是中低收入戶，不必再問
    parent = DEPENDS.get(attribute_id)
    if not parent:
        return False
    value = profile.value(parent[0], registry)
    return value is not None and not isinstance(value, list) and value != parent[1]


NUM = r"(\d[\d,]*(?:\.\d+)?|[一二兩三四五六七八九十百]+)"


def _value(token):
    from ..services.normalization import chinese_to_int
    return float(token.replace(",", "")) if token[0].isdigit() else chinese_to_int(token)


def parse_number(text, attribute_id=""):
    """口語的數字：「30000元」「約 8,000」「四萬」「一萬二」「半年」「兩年三個月」。年資類的欄位以月為單位。讀不出來回傳 None。"""
    if attribute_id.endswith("_months"):
        if "半年" in text:
            return 6.0
        years = re.search(NUM + r"\s*年", text)
        months = re.search(NUM + r"\s*個?月", text)
        if years or months:
            return float((_value(years.group(1)) or 0) * 12 + ((_value(months.group(1)) or 0) if months else 0))
    wan = re.search(NUM + r"\s*萬\s*(\d|[一二兩三四五六七八九])?", text)
    if wan and _value(wan.group(1)) is not None:
        base = _value(wan.group(1)) * 10000
        if wan.group(2):
            base += _value(wan.group(2)) * 1000
        return float(base)
    found = re.search(NUM, text)
    value = _value(found.group(1)) if found else None
    return None if value is None else float(value)


def yes_no(text):
    """口語的是／否。回傳 True／False；說得不確定（「應該有吧」「申請中」）回傳 UNSURE；
    讀不出來、或在講別人（「我朋友有」）回傳 None，由呼叫端提示使用者換個說法。"""
    cleaned = text.strip().strip("。.！!，,？? 吧喔啊耶囉").lower()
    if cleaned in YES_WORDS:
        return True
    if cleaned in NO_WORDS:
        return False
    if not cleaned or len(cleaned) > 16 or any(word in cleaned for word in OTHER_PEOPLE):
        return None
    if any(word in cleaned for word in HEDGES):
        return UNSURE
    if re.match(r"^(沒有|沒|無|不是|不曾|從來沒)", cleaned):
        return False
    if re.match(r"^(有|是|對|領有|持有|已經有|已有)", cleaned):
        return True
    return None


def guidance(data, latest, target):
    from ..api.assistant_search import requested_keyword, search_for_assistant, search_results
    registry = get_registry()
    keyword = requested_keyword(latest)
    search_keyword = keyword or data.get('_search_keyword')
    if keyword:
        # A search request is not an answer to the pending eligibility question.
        latest, target = '', ''
    scopes = list(data.get('_domains', []))
    scope_skipped = data.get('_scope_skipped', False)
    mentioned = [domain for domain, words in TOPICS.items() if any(word in latest for word in words)]
    # Eligibility answers must not silently replace the user's chosen needs.
    if mentioned and (target == 'guidance.scope' or (not scopes and not scope_skipped)):
        scopes = mentioned
        scope_skipped = False
    if target == 'guidance.scope' and latest.strip() in {'不確定', '不知道', '跳過', '不想回答'}:
        scope_skipped = True
    profile = Profile.from_dict(data, registry)
    pending = bool(latest and target and target != 'guidance.scope' and registry.get(target) and not profile.answered(target))
    if latest:
        profile, _, _ = parse_profile_text(latest, profile, registry)
        attribute = registry.get(target) if target else None
        if attribute:
            text = latest.strip()
            if text in {"不確定", "不知道", "跳過", "不想回答"}:
                profile.set(target, None, source="unsure")
            elif attribute.type == "boolean" and yes_no(text) is UNSURE:
                profile.set(target, None, source="unsure", evidence=text)
            elif attribute.type == "boolean" and yes_no(text) is not None:
                profile.set(target, yes_no(text), evidence=text)
            elif attribute.type != "boolean" and len(text) <= 16 and any(word in text for word in UNSURE_PHRASES):
                profile.set(target, None, source="unsure", evidence=text)
            elif attribute.type == "number":
                # Accept "30000元" / "約 8,000 元" so an answer with units is not dropped and re-asked.
                # 「大三」「高二」是年級不是數量，不能當成年齡或金額
                number = None if GRADE_RE.search(text) else parse_number(text, target)
                if number is not None:
                    profile.set(target, number, evidence=text)
            elif attribute.type in {"enum", "multi_enum"}:
                for option in attribute.values:
                    if text == option.get("label") or text == option.get("value"):
                        profile.set(target, [option['value']] if attribute.type == 'multi_enum' else option['value'], evidence=text)
                if not profile.answered(target):
                    # Free text that names exactly one option (longest label first) still counts as the answer.
                    hits = [o for o in attribute.values if str(o.get("label", "")) and str(o.get("label")) in text]
                    if len(hits) == 1:
                        profile.set(target, [hits[0]['value']] if attribute.type == 'multi_enum' else hits[0]['value'], evidence=text)
            elif attribute.type == "city":
                from ..services.normalization import normalize_city
                city = normalize_city(text)
                if city:
                    profile.set(target, city, evidence=text)
    if pending and not profile.answered(target) and mentioned and len(latest.strip()) >= 6 and not set(mentioned) <= set(scopes):
        # 沒答到上一題、卻用一句話提出別的需求（「其實我想找長照服務…」）：改找新的領域，不當成答錯
        scopes = mentioned
        scope_skipped = False
        pending = False
    # 這一輪在回答某一題，但沒讀出答案：先提示換個說法；同一題連續兩次都讀不出來就當「不確定」跳過，不卡在同一題
    not_understood = bool(pending and not profile.answered(target))
    misses = {k: v for k, v in (data.get('_misses') or {}).items() if isinstance(v, int)}
    skipped_target = ''
    if not_understood:
        misses[target] = misses.get(target, 0) + 1
        if misses[target] >= 2:
            profile.set(target, None, source='unsure', evidence=latest.strip()[:60])
            not_understood, skipped_target = False, target
    # 只有使用者明確說「幫我找…」才用關鍵字縮小範圍並回傳搜尋結果（前台會把關鍵字帶到查詢頁）；
    # 需求領域只用來篩選候選，讓追問依全部相關補助挑「最能確認資格」的題目，而不是只看關鍵字搜到的前 50 筆
    records, search = search_for_assistant({'_search_keyword': search_keyword}) if search_keyword else (None, None)
    if records is None:
        records = load_records(get_db())
        if scopes:
            records = [r for r in records if r.get('domain') in scopes]
    engine = MatchingEngine(registry=registry)
    items = engine.match_all(records, profile)
    remaining = [i for i in items if i.status != 'not_match']
    plan = plan_questions(profile, items, records, registry=registry, engine=engine, max_questions=8)
    # 前提已經否定的追問不問（沒有身障證明就不問等級、不是學生就不問成績）
    question = next((q for q in plan['questions'] if not blocked(q['attribute_id'], profile, registry)), None)
    if question and question['attribute_id'] == 'residence.duration_months':
        question = {**question, 'question': '你在戶籍地連續設籍多久了？（例如：半年、兩年、30 個月）'}
    if question and question['attribute_id'] == 'applicant.age' and 'long_term_care' in scopes:
        question = {**question, 'question': '請問申請對象（本人或被照顧的家人）今年幾歲？'}
    narrowed = (profile.preferences.get('enum_candidates') or {}).get(question['attribute_id']) if question and isinstance(profile.preferences, dict) else None
    if question and isinstance(narrowed, list) and narrowed:
        # 資料卡已經答過大範圍（例如「大學、二專或五專後兩年」）：只問範圍內的差別，不重問所有選項
        options = [o for o in question['options'] if o['value'] in narrowed]
        if len(options) >= 2:
            question = {**question, 'options': options, 'question': '你的資料卡已填學制範圍，請問確切是哪一種？'}
    if not scopes and not scope_skipped and not search_keyword:
        question = {'attribute_id': 'guidance.scope', 'question': '你想先解決哪方面的需要？例如房租、學費、求職、醫療或生活費。', 'reason': '先確定要找的補助類型，才不會問到無關的資格', 'options': [{'label': v, 'value': v} for v in ['房租', '學費', '求職']]}
    output_profile = profile.to_dict()
    output_profile['_misses'] = misses
    output_profile['_domains'] = scopes
    output_profile['_scope_skipped'] = scope_skipped
    if search_keyword:
        output_profile['_search_keyword'] = search_keyword
    if search is not None:
        search['items'] = search_results(remaining)
        search['candidate_count'] = len(remaining)
    return {"profile": output_profile, "candidate_count": len(remaining), "question": question,
            "matched_count": sum(i.status == 'high_match' for i in remaining), "total": len(records), "search": search, "not_understood": not_understood, "skipped_target": skipped_target}
