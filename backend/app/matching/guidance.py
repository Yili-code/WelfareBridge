"""Choose follow-ups from unresolved eligibility rules, retaining explicit answers."""
from . import MatchingEngine, Profile, load_records, parse_profile_text, plan_questions
from ..db import get_db
from ..registry import get_registry

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
    topics = {'education': ('就學', '學費', '獎學金'), 'housing': ('租屋', '房租', '住宅'), 'labor': ('失業', '求職', '職訓'), 'health': ('醫療', '健保'), 'disability': ('身障', '身心障礙'), 'social_welfare': ('生活費', '育兒', '急難')}
    mentioned = [domain for domain, words in topics.items() if any(word in latest for word in words)]
    # Eligibility answers must not silently replace the user's chosen needs.
    if mentioned and (target == 'guidance.scope' or (not scopes and not scope_skipped)):
        scopes = mentioned
        scope_skipped = False
    if target == 'guidance.scope' and latest.strip() in {'不確定', '不知道', '跳過', '不想回答'}:
        scope_skipped = True
    profile = Profile.from_dict(data, registry)
    if latest:
        profile, _, _ = parse_profile_text(latest, profile, registry)
        attribute = registry.get(target) if target else None
        if attribute:
            text = latest.strip()
            if text in {"不確定", "不知道", "跳過", "不想回答"}:
                profile.set(target, None, source="unsure")
            elif attribute.type == "boolean" and text in {"是", "否", "有", "沒有"}:
                profile.set(target, text in {"是", "有"}, evidence=text)
            elif attribute.type == "number":
                try:
                    profile.set(target, float(text), evidence=text)
                except ValueError:
                    pass
            elif attribute.type in {"enum", "multi_enum"}:
                for option in attribute.values:
                    if text == option.get("label") or text == option.get("value"):
                        profile.set(target, [option['value']] if attribute.type == 'multi_enum' else option['value'], evidence=text)
            elif attribute.type == "city":
                from ..services.normalization import normalize_city
                city = normalize_city(text)
                if city:
                    profile.set(target, city, evidence=text)
    records, search = search_for_assistant({'_domains': scopes, '_search_keyword': search_keyword})
    if records is None:
        records = load_records(get_db())
        if scopes:
            records = [r for r in records if r.get('domain') in scopes]
    engine = MatchingEngine(registry=registry)
    items = engine.match_all(records, profile)
    remaining = [i for i in items if i.status != 'not_match']
    plan = plan_questions(profile, items, records, registry=registry, engine=engine, max_questions=1)
    question = (plan['questions'] or [None])[0]
    if not scopes and not scope_skipped and not search_keyword:
        question = {'attribute_id': 'guidance.scope', 'question': '你想先解決哪方面的需要？例如房租、學費、求職、醫療或生活費。', 'reason': '先確定要找的補助類型，才不會問到無關的資格', 'options': [{'label': v, 'value': v} for v in ['房租', '學費', '求職']]}
    output_profile = profile.to_dict()
    output_profile['_domains'] = scopes
    output_profile['_scope_skipped'] = scope_skipped
    if search_keyword:
        output_profile['_search_keyword'] = search_keyword
    if search is not None:
        search['items'] = search_results(remaining)
        search['candidate_count'] = len(remaining)
    return {"profile": output_profile, "candidate_count": len(remaining), "question": question,
            "matched_count": sum(i.status == 'high_match' for i in remaining), "total": len(records), "search": search}
