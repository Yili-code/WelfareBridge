"""Read-only assistant tool using the same search as /api/benefits/search."""
import re
from urllib.parse import urlsplit

from .benefits import search_benefits
from ..db import get_db
from ..matching.engine import BENEFIT_PROJECTION

DOMAIN_KEYWORDS = {'education': '學', 'housing': '租', 'labor': '就業', 'health': '醫療',
                   'disability': '身心障礙', 'social_welfare': '補助', 'long_term_care': '照顧'}


def requested_keyword(text):
    match = re.search(r'(?:搜尋|搜索|查詢|幫我找|幫我查|查找|找一下)\s*[:：]?\s*(.+)', text)
    if not match:
        return None
    keyword = re.sub(r'[？?。！!]+$', '', match.group(1).strip()).strip('「」『』" ')
    return keyword[:100] or None


def search_for_assistant(data):
    keyword = data.get('_search_keyword')
    queries = [(keyword, None)] if keyword else [(DOMAIN_KEYWORDS[d], d) for d in data.get('_domains', []) if d in DOMAIN_KEYWORDS]
    if not queries:
        return None, None
    ids = []
    truncated = False
    for term, domain in queries:
        found = search_benefits(keyword=term, domain=domain, category=None, application_status='active', page=1, page_size=50)
        truncated = truncated or found['total'] > len(found['items'])
        ids.extend(item['id'] for item in found['items'])
    records = list(get_db().benefits.find({'_id': {'$in': list(dict.fromkeys(ids))},
        'is_canonical': True, 'status': {'$ne': 'expired'}, 'is_overview': {'$ne': True},
        'classification.uncertain': {'$ne': True}}, BENEFIT_PROJECTION))
    return records, {'queries': [term for term, _ in queries], 'searched_count': len(records), 'truncated': truncated}


def search_results(items):
    results = []
    for item in items:
        if item.status == 'not_match':
            continue
        url = item.source_url
        try:
            parsed = urlsplit(url)
            safe = parsed.scheme in {'http', 'https'} and bool(parsed.hostname) and not parsed.username and not parsed.password
        except ValueError:
            safe = False
        results.append({'id': item.benefit_id, 'title': item.title, 'status': item.status,
            'source_url': url if safe else '', 'source_name': item.source_name,
            'missing_conditions': [c.human_readable or c.reason for c in [*item.missing, *item.complex]][:3]})
        if len(results) == 3:
            break
    return results
