"""LLMProvider 抽象介面。"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class LLMError(RuntimeError):
    pass


@dataclass
class LLMResponse:
    text: str
    model: str
    raw: Any = None
    input_tokens: int | None = None
    output_tokens: int | None = None


_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def extract_json(text: str) -> dict:
    """從模型輸出取出第一個 JSON 物件（容忍 code fence 與前後說明文字）。"""
    candidate = text.strip()
    fenced = _FENCE_RE.search(candidate)
    if fenced:
        candidate = fenced.group(1).strip()
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        start, end = candidate.find("{"), candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMError("模型輸出不是 JSON")
        try:
            data = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMError(f"模型輸出 JSON 解析失敗：{exc}") from exc
    if not isinstance(data, dict):
        raise LLMError("模型輸出的 JSON 不是物件")
    return data


class LLMProvider(ABC):
    name: str = "abstract"

    def __init__(self, model: str, *, timeout: float = 120.0):
        self.model = model
        self.timeout = timeout

    @abstractmethod
    def complete(self, system: str, user: str, *, json_schema: dict | None = None, max_tokens: int = 4096) -> LLMResponse:
        """送出一次請求並回傳文字。json_schema 給支援結構化輸出的 provider 使用。"""

    def complete_json(self, system: str, user: str, *, json_schema: dict | None = None, max_tokens: int = 4096) -> dict:
        response = self.complete(system, user, json_schema=json_schema, max_tokens=max_tokens)
        return extract_json(response.text)

    def describe(self) -> dict:
        return {"provider": self.name, "model": self.model}
