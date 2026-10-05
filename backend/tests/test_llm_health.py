from types import SimpleNamespace
from app.config import Settings
from app.llm import factory

def test_model_size_must_match_and_cache_is_model_specific(monkeypatch):
    factory.reset_provider_cache()
    monkeypatch.setattr(factory.httpx, "get", lambda *args, **kwargs: SimpleNamespace(status_code=200, json=lambda: {"models": [{"name": "gemma4:e2b"}]}))
    assert not factory.ollama_status(Settings(llm_provider="ollama", llm_model="gemma4:e4b"))["online"]
    assert factory.ollama_status(Settings(llm_provider="ollama", llm_model="gemma4:e2b"))["online"]
    factory.reset_provider_cache()

def test_untagged_model_only_aliases_latest(monkeypatch):
    factory.reset_provider_cache()
    monkeypatch.setattr(factory.httpx, "get", lambda *args, **kwargs: SimpleNamespace(status_code=200, json=lambda: {"models": [{"name": "example:latest"}]}))
    assert factory.ollama_status(Settings(llm_provider="ollama", llm_model="example"))["online"]
    factory.reset_provider_cache()

def test_disabled_llm_does_not_probe_network(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("disabled provider made a network request")
    monkeypatch.setattr(factory.httpx, "get", unexpected)
    assert not factory.ollama_status(Settings(llm_provider="none"))["online"]

def test_gemma4_disables_thinking_for_structured_output(monkeypatch):
    from app.llm import ollama_provider

    sent = []
    reply = SimpleNamespace(status_code=200, json=lambda: {"message": {"content": "{}"}, "model": "gemma4:e4b"})
    monkeypatch.setattr(ollama_provider.httpx, "post", lambda url, json, timeout: sent.append(json) or reply)
    ollama_provider.OllamaProvider("gemma4:e4b").complete("system", "user")
    ollama_provider.OllamaProvider("gemma3:4b").complete("system", "user")
    assert sent[0]["think"] is False
    assert "think" not in sent[1]
