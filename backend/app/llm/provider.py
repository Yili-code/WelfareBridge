"""LLMProvider 抽象介面。"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


log = logging.getLogger(__name__)
JSON_ATTEMPTS = 3


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


def _repair(body: str) -> str:
    """只做不改變語意的修補：去掉尾端逗號、補上相鄰值之間漏掉的逗號、補上字串內漏跳脫的引號。"""
    body = re.sub(r",\s*([}\]])", r"\1", body)
    body = re.sub(r'("|\d|true|false|null|\}|\])(\s*\n\s*)("(?:[^"\\]|\\.)*"\s*:|\{)', r"\1,\2\3", body)
    return _escape_inner_quotes(body)


def _escape_inner_quotes(body: str) -> str:
    """字串裡漏跳脫的雙引號（引文常含「"」）：字串中遇到後面不是 , } ] : 的引號，就視為字串內容並補上跳脫。"""
    out, in_string, i = [], False, 0
    while i < len(body):
        ch = body[i]
        if in_string and ch == "\\":
            out.append(body[i:i + 2])
            i += 2
            continue
        if ch == '"':
            if not in_string:
                in_string = True
            else:
                rest = body[i + 1:].lstrip()
                if rest[:1] in {",", "}", "]", ":", ""}:
                    in_string = False
                else:
                    out.append("\\")
        out.append(ch)
        i += 1
    return "".join(out)


def close_truncated(text: str) -> dict | None:
    """模型提早停止、JSON 只輸出到一半時：丟掉最後不完整的項目，補上括號，保留已經完整輸出的欄位。救不回來回傳 None。"""
    start = text.find("{")
    if start < 0:
        return None
    body = text[start:]
    stack, in_string, escaped, last_safe = [], False, False, None
    for i, ch in enumerate(body):
        if in_string:
            escaped = (ch == "\\") and not escaped
            if ch == '"' and not escaped:
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]":
            if stack:
                stack.pop()
            last_safe = (i + 1, list(stack))
        elif ch == ",":
            last_safe = (i, list(stack))
    if last_safe is None:
        return None
    cut, open_stack = last_safe
    try:
        data = json.loads(body[:cut] + "".join(reversed(open_stack)))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


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
        body = candidate[start : end + 1]
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            try:
                data = json.loads(_repair(body))
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
    def complete(self, system: str, user: str, *, json_schema: dict | None = None, max_tokens: int = 4096, temperature: float = 0.0) -> LLMResponse:
        """送出一次請求並回傳文字。json_schema 給支援結構化輸出的 provider 使用；temperature 只在重試時調高，讓重問不會得到同一份壞輸出。"""

    def complete_json(self, system: str, user: str, *, json_schema: dict | None = None, max_tokens: int = 4096, salvage: bool = False) -> dict:
        """模型偶爾輸出缺逗號或被截斷的 JSON（約 1～3%）。先試修復；仍失敗就換溫度、加大長度上限重問，最多共 3 次。"""
        last: LLMError | None = None
        text = ""
        for attempt in range(JSON_ATTEMPTS):
            response = self.complete(system, user, json_schema=json_schema, max_tokens=max_tokens * (1 + attempt), temperature=0.0 if attempt == 0 else 0.3)
            text = response.text
            try:
                return extract_json(text)
            except LLMError as exc:
                last = exc
                log.info("模型 JSON 無法解析（第 %d 次）：%s", attempt + 1, exc)
        if salvage and (partial := close_truncated(text)):
            log.info("模型輸出被截斷，只採用已完整輸出的欄位")
            return partial
        raise last  # type: ignore[misc]

    def describe(self) -> dict:
        return {"provider": self.name, "model": self.model}
