"""LLM 層（v2）：本地 Ollama provider + 四個受控任務（分類、給付特徵補齊、條件句對屬性、複雜條件判斷、使用者描述解析）。

所有輸出都必須是 JSON、都會經過白名單與「摘錄必須出現在原文」檢查；AI 只能補充，不能覆蓋原文證據。
"""

from .factory import get_provider, ollama_status
from .provider import LLMError, LLMProvider, LLMResponse

__all__ = ["get_provider", "ollama_status", "LLMError", "LLMProvider", "LLMResponse"]
