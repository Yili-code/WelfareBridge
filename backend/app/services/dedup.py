"""Deduplication：同一份獎學金出現在多個官方來源時共用 canonical_id，但每個來源的紀錄都保留。

判斷依據（工程 heuristic，不是官方標準）：
    1. 標題正規化後（去空白／全形／學年度學期字樣）相似度 >= TITLE_THRESHOLD
    2. 且 提供機關相同、或其中一方的機關名稱包含對方、或申請截止日相同
canonical 優先順序：官方原始公告（data_confidence 高）> 政府網站轉載 > 學校轉知。
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from .normalization import compact

TITLE_THRESHOLD = 0.82
MIN_CONTAINED_TITLE = 10
YEAR_TERM_RE = re.compile(r"(\d{2,4}學年度|第[一二12]學期|\d{2,4}年度|\d{2,4}-[12]學期|【[^】]*】|\[[^\]]*\]|\([^)]*\)|（[^）]*）)")


def normalize_title(title: str) -> str:
    text = YEAR_TERM_RE.sub("", title or "")
    text = re.sub(r"(轉知|函轉|公告|申請|相關資訊|受理|自即日起|截止|止)", "", text)
    text = re.sub(r"(實施計畫|作業要點|計畫|方案|專區|辦法|要點|須知|簡章)$", "", text.strip())
    return compact(text)


def title_similarity(a: str, b: str) -> float:
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    if na == nb:
        return 1.0
    return SequenceMatcher(None, na, nb).ratio()


def provider_compatible(a: str, b: str) -> bool:
    ca, cb = compact(a), compact(b)
    if not ca or not cb:
        return False
    return ca == cb or ca in cb or cb in ca


def is_duplicate(candidate: dict, existing: dict) -> tuple[bool, float, str]:
    """candidate / existing 都是 {title, provider, region, application_end, source_url}。回傳 (是否重複, 相似度, 原因)。"""
    if candidate.get("source_url") and candidate.get("source_url") == existing.get("source_url"):
        return True, 1.0, "同一個官方 URL"
    # 各縣市都有同名方案（低收入戶生活補助、育兒津貼…）：轄區不同就是不同紀錄，不能只留一個縣市的版本
    region_a, region_b = candidate.get("region") or "", existing.get("region") or ""
    if region_a and region_b and region_a != region_b:
        return False, 0.0, f"不同轄區的方案（{region_a}／{region_b}）"
    similarity = title_similarity(candidate.get("title", ""), existing.get("title", ""))
    # 「【轉知】基隆市政府「基隆市高級中等以上學校清寒優秀學生獎學金給與辦法」…」包含原標題：只要機關相容即視為同一份
    short, long = sorted((normalize_title(candidate.get("title", "")), normalize_title(existing.get("title", ""))), key=len)
    if len(short) >= MIN_CONTAINED_TITLE and short in long and provider_compatible(candidate.get("provider", ""), existing.get("provider", "")):
        return True, max(similarity, len(short) / len(long)), "較短標題完整包含於較長標題且提供機關相同"
    # 「缺工就業獎勵」vs「專案缺工就業獎勵」、「臨時工作津貼」vs「天災臨時工作津貼」：短標題前後多了限定詞，是不同方案
    if short and short != long and short in long and len(short) < MIN_CONTAINED_TITLE:
        return False, similarity, "短標題加上限定詞，視為不同方案"
    if similarity < TITLE_THRESHOLD:
        return False, similarity, "標題不相似"
    if provider_compatible(candidate.get("provider", ""), existing.get("provider", "")):
        return True, similarity, f"標題相似度 {similarity:.2f} 且提供機關相同"
    end_a, end_b = candidate.get("application_end"), existing.get("application_end")
    if end_a and end_b and end_a == end_b:
        return True, similarity, f"標題相似度 {similarity:.2f} 且申請截止日相同"
    if similarity >= 0.95:
        return True, similarity, f"標題幾乎相同（{similarity:.2f}）"
    return False, similarity, "標題相似但機關／期限不同"


def canonical_rank(record: dict) -> tuple:
    """越大越優先成為 canonical。record: {data_confidence, source_type, is_repost}"""
    return (
        0 if record.get("is_repost") else 1,
        1 if record.get("source_type") == "government_site" else 0,
        int(record.get("data_confidence", 0)),
    )
