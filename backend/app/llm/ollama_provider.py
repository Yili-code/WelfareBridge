"""本地 LLM（Ollama）provider。"""

from __future__ import annotations

import os
import re

import httpx

from .provider import LLMError, LLMProvider, LLMResponse

DEFAULT_MODEL = "llama3.1"


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, model: str = "", *, base_url: str = "http://localhost:11434", timeout: float = 300.0):
        super().__init__(model or DEFAULT_MODEL, timeout=timeout)
        self.base_url = base_url.rstrip("/")

    def complete(self, system: str, user: str, *, json_schema: dict | None = None, max_tokens: int = 4096) -> LLMResponse:
        options = {"temperature": 0, "num_predict": max_tokens}
        num_ctx = os.environ.get("LLM_NUM_CTX", "").strip()
        if num_ctx.isdigit():
            options["num_ctx"] = int(num_ctx)  # 5090 主機跑 qwen3:32b 時可設 8192／16384，讓更長的原文進得去
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "stream": False,
            "format": json_schema or "json",
            "options": options,
        }
        if re.search(r"(qwen3|deepseek-r1|gpt-oss|magistral)", self.model, re.I):
            body["think"] = False  # 思考型模型：結構化輸出不需要思考鏈，關掉才不會拖慢且更守 JSON 格式
        try:
            response = httpx.post(f"{self.base_url}/api/chat", json=body, timeout=self.timeout)
        except httpx.HTTPError as exc:
            raise LLMError(f"Ollama 連線失敗：{exc}") from exc
        if response.status_code >= 400:
            raise LLMError(f"Ollama 錯誤 {response.status_code}: {response.text[:200]}")
        data = response.json()
        text = (data.get("message") or {}).get("content", "")
        if not text:
            raise LLMError("Ollama 沒有回傳內容")
        return LLMResponse(text=text, model=data.get("model", self.model), raw=data, input_tokens=data.get("prompt_eval_count"), output_tokens=data.get("eval_count"))
