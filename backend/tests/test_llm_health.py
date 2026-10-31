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


def test_json_output_with_a_missing_comma_is_repaired_and_bad_output_is_retried():
    from app.llm.provider import LLMProvider, LLMResponse, extract_json

    assert extract_json('{"a": {"x": 1}\n "b": [1, 2,]}') == {"a": {"x": 1}, "b": [1, 2]}

    class Flaky(LLMProvider):
        calls = []

        def complete(self, system, user, *, json_schema=None, max_tokens=4096, temperature=0.0):
            self.calls.append((max_tokens, temperature))
            return LLMResponse(text='{"a": ' if len(self.calls) == 1 else '{"a": 1}', model="m")

    provider = Flaky("m")
    assert provider.complete_json("s", "u", max_tokens=100) == {"a": 1}
    assert provider.calls == [(100, 0.0), (200, 0.3)]


def test_unescaped_quotes_inside_a_quoted_excerpt_are_repaired():
    from app.llm.provider import extract_json

    assert extract_json('{"q": "他說"不得重複申請"，另有", "n": 1}') == {"q": '他說"不得重複申請"，另有', "n": 1}


def test_truncated_output_keeps_only_complete_fields():
    from app.llm.provider import close_truncated

    assert close_truncated('{"a": 1, "r": {"x": "y", "q": "尚未輸出完') == {"a": 1, "r": {"x": "y"}}
    assert close_truncated('{"a": [1, 2], "b": {"c": "d"}, "e": "f') == {"a": [1, 2], "b": {"c": "d"}}
    assert close_truncated("沒有 JSON") is None
