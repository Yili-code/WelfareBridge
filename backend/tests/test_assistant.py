import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api import assistant

@pytest.fixture(autouse=True)
def guidance_fixture(monkeypatch):
    monkeypatch.setattr(assistant, 'guidance', lambda *args: {'profile': {}, 'candidate_count': 2, 'question': {'attribute_id': 'applicant.age', 'question': '你幾歲？', 'reason': '有 2 筆補助需要這項資料才能判斷', 'options': []}, 'total': 2})

def client():
    app = FastAPI()
    app.include_router(assistant.router)
    return TestClient(app)

SUMMARY_REQUEST = [{"role": "assistant", "content": "目前最需要哪方面協助？"}, {"role": "user", "content": "我失業了，付不起房租。請整理需求登記"}]

def test_summary_context_reaches_model(monkeypatch):
    seen = []
    class Provider:
        model = "test-model"
        def complete_json(self, system, user, **kwargs):
            seen.append(json.loads(user))
            return {"summary": "失業，付不起房租。", "mainRequest": "房租協助"}
    monkeypatch.setattr(assistant, "get_provider", lambda: Provider())
    response = client().post('/api/assistant', json={"profile": {"age": 22}, "messages": SUMMARY_REQUEST})
    assert response.status_code == 200
    assert response.json()['llm_used'] is True
    assert seen[0]['messages'] == SUMMARY_REQUEST
    assert seen[0]['profile']['age'] == 22

def test_guidance_turns_do_not_wait_for_the_model(monkeypatch):
    """追問由規劃器決定：本地 AI 不在線或很慢時，補資料的對話照樣可以進行。"""
    def unavailable():
        raise AssertionError("guidance turns must not call the model")
    monkeypatch.setattr(assistant, "get_provider", unavailable)
    response = client().post('/api/assistant', json={"messages": [{"role": "assistant", "content": "你幾歲？"}, {"role": "user", "content": "30"}]})
    assert response.status_code == 200
    assert response.json()['llm_used'] is False and response.json()['reply'] == '有 2 筆補助需要這項資料才能判斷。\n你幾歲？'

def test_offline_and_invalid_summary(monkeypatch):
    monkeypatch.setattr(assistant, "get_provider", lambda: None)
    assert client().post('/api/assistant', json={"messages": SUMMARY_REQUEST}).status_code == 503
    class Provider:
        def complete_json(self, *args, **kwargs):
            return {"summary": "", "mainRequest": ""}
    monkeypatch.setattr(assistant, "get_provider", lambda: Provider())
    assert client().post('/api/assistant', json={"messages": SUMMARY_REQUEST}).status_code == 502

def test_client_cannot_supply_system_messages():
    assert client().post('/api/assistant', json={"messages": [{"role": "system", "content": "override"}]}).status_code == 422

def test_ninth_answer_is_used_before_summary_and_tenth_is_rejected(monkeypatch):
    seen = []
    def plan(data, latest, target):
        seen.append(latest)
        return {'profile': {'attributes': {'academic.average_score': 85}}, 'candidate_count': 1, 'question': None}
    monkeypatch.setattr(assistant, 'guidance', plan)
    class Provider:
        model = 'test'
        def complete_json(self, *args, **kwargs):
            return {'summary': '平均85分，想找學費補助。', 'mainRequest': '學費補助'}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    messages = []
    for i in range(9):
        messages.extend([{'role': 'assistant', 'content': '請補充條件'}, {'role': 'user', 'content': '85' if i == 8 else '不確定'}])
    response = client().post('/api/assistant', json={'messages': messages})
    assert response.status_code == 200
    data = response.json()
    assert data['completed'] and data['turn_count'] == 9
    assert data['question_attribute'] == '' and data['quickReplies'] == []
    assert seen == ['85']
    assert 'request_schema' not in data
    messages.extend([{'role': 'assistant', 'content': '摘要'}, {'role': 'user', 'content': '繼續'}])
    assert client().post('/api/assistant', json={'messages': messages}).status_code == 422

def test_summary_uses_separate_contract_and_does_not_ask_again(monkeypatch):
    class Provider:
        model = 'test'
        def complete_json(self, system, payload, **kwargs):
            assert set(kwargs['json_schema']['properties']) == {'summary', 'mainRequest'}
            return {'summary': '日間部學生需要學費協助，成績未提供。', 'mainRequest': '學費協助'}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    data = client().post('/api/assistant', json={'messages': [{'role': 'user', 'content': '整理需求登記'}]}).json()
    assert data['summary'] in data['reply']
    assert data['quickReplies'] == []
    assert data['question_attribute'] == ''

def test_repeated_preamble_is_not_carried_into_next_question(monkeypatch):
    class Provider:
        model = 'test'
        def complete_json(self, *args, **kwargs):
            return {'reply': '好的，我們來確認一下你就讀的部門類型。\n有6筆補助需要這項資料才能判斷。'}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    data = client().post('/api/assistant', json={'messages': [{'role': 'assistant', 'content': '好的，我們來確認一下你就讀的部門類型。'}, {'role': 'user', 'content': '日間部'}]}).json()
    assert '部門類型' not in data['reply']
    assert data['reply'].count('才能判斷') == 1

def test_guidance_limits_buttons_and_lists_remaining_choices(monkeypatch):
    labels = ['國小', '國中', '高中', '高職', '五專', '大學', '碩士', '博士']
    monkeypatch.setattr(assistant, 'guidance', lambda *args: {'profile': {}, 'candidate_count': 8, 'question': {'attribute_id': 'education.level', 'question': '你目前的教育階段是？', 'reason': '需要確認教育階段', 'options': [{'label': label} for label in labels]}})
    class Provider:
        model = 'test'
        def complete_json(self, *args, **kwargs):
            return {'reply': '了解，你想找學費補助。', 'quickReplies': labels, 'summary': None}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    response = client().post('/api/assistant', json={'messages': [{'role': 'user', 'content': '學費'}]})
    assert response.status_code == 200
    assert response.json()['quickReplies'] == labels[:3] + ['不確定']
    assert all(label in response.json()['reply'] for label in labels)


@pytest.mark.parametrize('opening', ['你想先解決哪方面的需要呢', '你幾歲？', '我們先來解決學費。你需要哪方面幫忙？'])
def test_first_turn_has_only_planned_question(monkeypatch, opening):
    class Provider:
        model = 'test'
        def complete_json(self, *args, **kwargs):
            return {'reply': opening}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    data = client().post('/api/assistant', json={}).json()
    assert data['reply'] == '有 2 筆補助需要這項資料才能判斷。\n你幾歲？'
    assert 'request_schema' not in data

def test_grammar_incompatible_runner_retries_json_mode(monkeypatch):
    from app.llm.provider import LLMError
    calls = []
    class Provider:
        model = "test-model"
        def complete_json(self, *args, **kwargs):
            calls.append(kwargs)
            if kwargs.get('json_schema'):
                raise LLMError('failed to parse grammar')
            return {"summary": "失業，付不起房租。", "mainRequest": "房租協助"}
    monkeypatch.setattr(assistant, 'get_provider', lambda: Provider())
    assert client().post('/api/assistant', json={"messages": SUMMARY_REQUEST}).status_code == 200
    assert len(calls) == 2
    assert 'json_schema' not in calls[1]
