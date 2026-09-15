from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api import assistant, assistant_search, benefits
from app.matching import guidance as guidance_module


def test_search_intent_does_not_treat_ordinary_answers_as_keywords():
    assert assistant_search.requested_keyword('幫我找租金補助') == '租金補助'
    assert assistant_search.requested_keyword('搜尋：學費？') == '學費'
    assert assistant_search.requested_keyword('我是學生') is None
    assert assistant_search.requested_keyword('不確定') is None


def test_assistant_calls_shared_search_and_refines_results(db, monkeypatch):
    from types import SimpleNamespace
    db = SimpleNamespace(benefits=db.assistant_search_test)
    monkeypatch.setattr(benefits, 'get_db', lambda: db)
    monkeypatch.setattr(assistant_search, 'get_db', lambda: db)
    monkeypatch.setattr(guidance_module, 'get_db', lambda: db)
    db.benefits.delete_many({})
    for id, low_income in [('yes', True), ('no', False)]:
        db.benefits.insert_one({'_id': id, 'is_canonical': True, 'title': '測試租金補助 ' + id, 'domain': 'housing',
            'source': {'source_url': 'https://example.gov.tw/benefit', 'source_name': '測試機關'},
            'rules': [{'id': id, 'attribute_id': 'identity.low_income', 'group_id': 'identity',
                       'operator': '=', 'value': low_income, 'complexity': 'simple', 'confidence': 1, 'inferred': False}]})
    db.benefits.insert_one({'_id': 'expired', 'is_canonical': True, 'title': '測試租金補助 expired', 'domain': 'housing', 'status': 'expired'})
    seen = []
    shared_search = assistant_search.search_benefits
    def spy(**kwargs):
        seen.append(kwargs)
        return shared_search(**kwargs)
    monkeypatch.setattr(assistant_search, 'search_benefits', spy)
    class Provider:
        model = 'test'
        def complete_json(self, *args, **kwargs):
            return {'reply': '這裡有模型虛構補助', 'quickReplies': []}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    app = FastAPI()
    app.include_router(assistant.router)
    client = TestClient(app)
    # A direct search from the opening scope question must return results,
    # without asking the user to choose a need category again.
    direct = client.post('/api/assistant', json={
        'question_attribute': 'guidance.scope',
        'messages': [{'role': 'user', 'content': '幫我找租金補助'}],
    }).json()
    assert direct['search']['queries'] == ['租金補助']
    assert {r['id'] for r in direct['search']['items']} == {'yes', 'no'}
    assert direct['question_attribute'] == 'identity.low_income'
    refined = client.post('/api/assistant', json={
        'guidance_profile': direct['guidance_profile'],
        'question_attribute': direct['question_attribute'],
        'messages': [{'role': 'user', 'content': '是'}],
    }).json()
    assert refined['search']['queries'] == ['租金補助']
    assert [r['id'] for r in refined['search']['items']] == ['yes']
    seen.clear()
    initial = client.post('/api/assistant', json={'guidance_profile': {'_domains': ['housing']}}).json()
    assert seen[0]['domain'] == 'housing'
    assert initial['search']['candidate_count'] == 2
    assert {r['id'] for r in initial['search']['items']} == {'yes', 'no'}
    assert '虛構' not in initial['reply']
    assert initial['question_attribute'] == 'identity.low_income'
    answered = client.post('/api/assistant', json={'guidance_profile': initial['guidance_profile'],
        'question_attribute': initial['question_attribute'], 'messages': [{'role': 'user', 'content': '是'}]}).json()
    assert [r['id'] for r in answered['search']['items']] == ['yes']
    explicit = client.post('/api/assistant', json={'guidance_profile': initial['guidance_profile'],
        'question_attribute': initial['question_attribute'], 'messages': [{'role': 'user', 'content': '幫我找不存在的方案'}]}).json()
    assert explicit['search']['items'] == []
    assert seen[-1]['keyword'] == '不存在的方案'
    assert 'identity.low_income' not in explicit['guidance_profile']['attributes']
    assert explicit['guidance_profile']['_search_keyword'] == '不存在的方案'


def test_results_limit_and_unsafe_source_links():
    from types import SimpleNamespace
    items = [SimpleNamespace(status='possible_match', benefit_id=str(i), title='補助', source_url='javascript:alert(1)',
                             source_name='機關', missing=[], complex=[]) for i in range(5)]
    results = assistant_search.search_results(items)
    assert len(results) == 3
    assert all(item['source_url'] == '' for item in results)
