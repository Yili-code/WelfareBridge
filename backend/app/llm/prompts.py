"""Prompt 載入器。實際使用的 prompt 存在 app/llm/prompts/*.md（docs/prompts/ 由 scripts/export_prompts.py 同步）。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent / "prompts"

ANTI_HALLUCINATION_RULES = """You MUST NOT invent eligibility conditions.
Only infer from provided source text.
If the source does not contain sufficient information: return unknown / null.
Never create a numeric threshold that does not exist in the source.
Never assume a city, school, identity, age, income, or grade unless explicitly stated.
Always provide source_excerpt copied verbatim from the source text for every extracted value."""


@lru_cache
def load_prompt(name: str) -> str:
    path = PROMPT_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def render(name: str, **values: str) -> str:
    """以 {{KEY}} 佔位符替換（不用 str.format，避免 JSON 範例中的大括號衝突）。"""
    text = load_prompt(name)
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def split_system_user(text: str) -> tuple[str, str]:
    """prompt 檔以 `## SYSTEM` / `## USER` 兩段撰寫。"""
    if "## USER" not in text:
        return "", text
    system_part, user_part = text.split("## USER", 1)
    system_part = system_part.replace("## SYSTEM", "", 1).strip()
    return system_part, user_part.strip()
