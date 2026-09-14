"""依設定建立 LLMProvider（v2 只支援本地 Ollama）。LLM_PROVIDER=none 或 Ollama 無法連線時回傳 None，系統改以純規則式運作。"""

from __future__ import annotations

import logging
import time

import httpx

from ..config import Settings, get_settings
from .provider import LLMError, LLMProvider

log = logging.getLogger(__name__)
_cache: dict[str, LLMProvider | None] = {}
_health: dict[str, tuple[float, bool, str]] = {}
HEALTH_TTL = 30.0


def ollama_status(settings: Settings | None = None) -> dict:
    """GET /api/tags：Ollama 是否在線、模型是否已下載（結果快取 30 秒）。"""
    settings = settings or get_settings()
    base = settings.ollama_base_url.rstrip("/")
    if settings.llm_provider == "none":
        return {"online": False, "detail": "未啟用本地 AI", "base_url": base, "model": settings.llm_model}
    cache_key = f"{base}|{settings.llm_model}"
    cached = _health.get(cache_key)
    now = time.monotonic()
    if cached and now - cached[0] < HEALTH_TTL:
        return {"online": cached[1], "detail": cached[2], "base_url": base, "model": settings.llm_model}
    online, detail = False, ""
    try:
        response = httpx.get(f"{base}/api/tags", timeout=3.0)
        if response.status_code == 200:
            names = [m.get("name", "") for m in response.json().get("models", [])]
            wanted = settings.llm_model
            normalize = lambda name: name if ":" in name.rsplit("/", 1)[-1] else f"{name}:latest"
            has_model = any(normalize(n) == normalize(wanted) for n in names)
            online = True
            detail = f"models={names}" + ("" if has_model else f"；找不到 {wanted}，請執行 ollama pull {wanted}")
            if not has_model:
                online = False
        else:
            detail = f"HTTP {response.status_code}"
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
    _health[cache_key] = (now, online, detail)
    return {"online": online, "detail": detail, "base_url": base, "model": settings.llm_model}


def get_provider(settings: Settings | None = None) -> LLMProvider | None:
    settings = settings or get_settings()
    name = (settings.llm_provider or "none").lower()
    if name == "none":
        return None
    if name != "ollama":
        log.warning("v2 只支援本地 Ollama；LLM_PROVIDER=%s 視為 none", name)
        return None
    status = ollama_status(settings)
    if not status["online"]:
        log.info("Ollama 不可用（%s），改用純規則式", status["detail"])
        return None
    key = f"ollama:{settings.llm_model}:{settings.ollama_base_url}"
    if key not in _cache:
        from .ollama_provider import OllamaProvider

        _cache[key] = OllamaProvider(settings.llm_model, base_url=settings.ollama_base_url, timeout=max(settings.llm_timeout_seconds, 120))
    return _cache[key]


def reset_provider_cache() -> None:
    _cache.clear()
    _health.clear()
