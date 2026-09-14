import json
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api import assistant

def client():
    app = FastAPI()
    app.include_router(assistant.router)
    return TestClient(app)

def test_context_reaches_model(monkeypatch):
    seen = []
    class Provider:
        model = "test-model"
        def complete_json(self, system, user, **kwargs):
            seen.append(json.loads(user))
            return {"reply": "每月房租大約多少？", "quickReplies": ["一萬元以下"]}
    monkeypatch.setattr(assistant, "get_provider", lambda: Provider())
    messages = [{"role": "assistant", "content": "目前最需要哪方面協助？"}, {"role": "user", "content": "我失業了，付不起房租"}]
    response = client().post('/api/assistant', json={"profile": {"age": 22}, "messages": messages})
    assert response.status_code == 200
    assert response.json()['llm_used'] is True
    assert seen[0]['messages'] == messages
    assert seen[0]['profile']['age'] == 22

def test_offline_and_invalid_output(monkeypatch):
    monkeypatch.setattr(assistant, "get_provider", lambda: None)
    assert client().post('/api/assistant', json={}).status_code == 503
    class Provider:
        def complete_json(self, *args, **kwargs):
            return {"reply": "", "quickReplies": []}
    monkeypatch.setattr(assistant, "get_provider", lambda: Provider())
    assert client().post('/api/assistant', json={}).status_code == 502

def test_client_cannot_supply_system_messages():
    assert client().post('/api/assistant', json={"messages": [{"role": "system", "content": "override"}]}).status_code == 422
