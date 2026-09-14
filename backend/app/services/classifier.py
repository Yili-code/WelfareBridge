"""分類器（v2）：keyword_rules_v2.yaml（語料統計）→ 是否為補助頁面 + 類別；不確定時由本地 AI 二次判斷。

流程：
    normalize（全形→半形、小寫、台→臺）
    → benefit_signal：正向詞加權、負面詞扣分、標題命中加分 → signal_score
    → categories：每個類別關鍵字加權（每詞只算一次，最多 6 個詞）→ category_scores
    → is_benefit = signal_score >= threshold 且最高類別分數 > 0
    → confidence = 0.5 × min(1, signal/threshold/2) + 0.5 × (best − second)/(best)
    → confidence 落在 [low, high) 或沒有類別 → 交給 LLM（pipeline 決定）
"""

from __future__ import annotations

import re

import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

from ..config import get_settings
from ..registry import get_registry
from .normalization import find_cities, normalize_text

log = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    is_benefit: bool
    signal_score: float
    threshold: float
    category: str
    domain: str
    category_scores: dict[str, float]
    confidence: float
    matched_signal: list[str]
    matched_negative: list[str]
    matched_category: dict[str, list[str]]
    regions: list[str]
    method: str = "keyword"
    rules_source: str = "seed"
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


LISTING_RE = re.compile(r"(共\s*\d+\s*筆|每頁顯示|第\s*\d+\s*/\s*\d+\s*頁)")


class BenefitClassifier:
    def __init__(self, rules_path: str | Path):
        with open(rules_path, encoding="utf-8") as handle:
            self.rules: dict = yaml.safe_load(handle) or {}
        signal = self.rules.get("benefit_signal", {}) or {}
        self.threshold = float(signal.get("threshold", 4))
        self.title_bonus = float(signal.get("title_bonus", 2))
        # 類別分數達到這個值才算「類別證據充分」（信心值的類別部分拿滿分）
        self.category_strong_score = float(signal.get("category_strong_score", 6))
        self.signal_terms: list[tuple[str, str, float]] = [(normalize_text(str(k["term"])), str(k["term"]),float(k.get("weight", 1))) for k in signal.get("keywords", []) if k.get("term")]
        self.negative_terms: list[tuple[str, str, float]] = [(normalize_text(str(k["term"])), str(k["term"]),float(k.get("weight", -2))) for k in signal.get("negative", []) if k.get("term")]
        self.categories: dict[str, list[tuple[str, str, float]]] = {}
        self.category_labels: dict[str, str] = {}
        for cat, spec in (self.rules.get("categories", {}) or {}).items():
            self.category_labels[cat] = spec.get("label", cat)
            self.categories[cat] = [(normalize_text(str(k["term"])), str(k["term"]),float(k.get("weight", 1))) for k in spec.get("keywords", []) if k.get("term")]
        self.max_terms_per_category = 6
        self.rules_source = str(self.rules.get("source", "seed"))
        self.condition_cues: list[str] = [k["term"] for k in self.rules.get("condition_cues", []) if k.get("term")]

    def classify(self, title: str, text: str) -> ClassificationResult:
        registry = get_registry()
        norm_title = normalize_text(title or "")
        norm_body = normalize_text(f"{title}\n{text}")
        signal = 0.0
        matched_signal: list[str] = []
        for norm, term, weight in self.signal_terms:
            if norm in norm_body:
                signal += weight
                matched_signal.append(term)
                if norm in norm_title:
                    signal += self.title_bonus
        matched_negative: list[str] = []
        for norm, term, weight in self.negative_terms:
            if norm in norm_body:
                signal += weight
                matched_negative.append(term)
        if LISTING_RE.search((text or "")[:800]):
            # 帶分頁標記的列表頁（最新消息、公告列表）：不是單一補助的內容頁
            signal -= 3
            matched_negative.append("列表頁分頁標記")
        scores: dict[str, float] = {}
        matched_category: dict[str, list[str]] = {}
        for cat, terms in self.categories.items():
            hits = [(term, weight, norm in norm_title) for norm, term, weight in terms if norm in norm_body]
            if not hits:
                continue
            hits.sort(key=lambda h: -h[1])
            counted = hits[: self.max_terms_per_category]
            score = sum(w for _, w, _ in counted) + sum(self.title_bonus for _, _, in_title in counted if in_title)
            scores[cat] = score
            matched_category[cat] = [t for t, _, _ in counted]
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        best, best_score = (ranked[0] if ranked else ("", 0.0))
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0
        is_benefit = signal >= self.threshold and best_score > 0
        margin = (best_score - second_score) / best_score if best_score > 0 else 0.0
        # 類別證據太弱（例如只命中一個權重 1 的「福利」）時，即使沒有第二名也不能拿滿分：margin 乘以類別強度
        category_part = min(1.0, best_score / self.category_strong_score) if best_score > 0 else 0.0
        signal_part = min(1.0, signal / (self.threshold * 2)) if signal > 0 else 0.0
        confidence = round(0.5 * signal_part + 0.5 * margin * category_part, 3) if is_benefit else round(min(0.5, signal_part * 0.5), 3)
        reasons = [f"signal={signal:.1f}/{self.threshold:.0f}（{', '.join(matched_signal[:6])}）"]
        if matched_negative:
            reasons.append("negative：" + "、".join(matched_negative[:5]))
        if ranked:
            reasons.append("categories：" + "；".join(f"{self.category_labels.get(c, c)} {s:.0f}" for c, s in ranked[:3]))
        return ClassificationResult(
            is_benefit=is_benefit, signal_score=round(signal, 2), threshold=self.threshold, category=best if is_benefit else "", domain=registry.domain_of(best) if is_benefit else "",
            category_scores={c: round(s, 2) for c, s in ranked[:6]}, confidence=confidence, matched_signal=matched_signal[:12], matched_negative=matched_negative[:8],
            matched_category={c: v for c, v in matched_category.items() if c in dict(ranked[:6])}, regions=find_cities(f"{title}\n{text[:3000]}"), method="keyword", rules_source=self.rules_source, reasons=reasons,
        )

    def top_candidates(self, result: ClassificationResult, k: int = 5) -> list[str]:
        """給 LLM 二次判斷的候選類別：分數前 k 名；沒有分數時用整個葉節點清單的前 k。"""
        registry = get_registry()
        ranked = list(result.category_scores.keys())
        if len(ranked) < k:
            for leaf in registry.leaves():
                if leaf.id not in ranked:
                    ranked.append(leaf.id)
                if len(ranked) >= k:
                    break
        return ranked[:k]

    def keyword_table(self) -> list[dict]:
        rows = [{"group": "benefit_signal", "term": t, "weight": w} for _, t, w in self.signal_terms]
        rows += [{"group": "negative", "term": t, "weight": w} for _, t, w in self.negative_terms]
        for cat, terms in self.categories.items():
            rows += [{"group": cat, "term": t, "weight": w} for _, t, w in terms]
        return rows


_default: BenefitClassifier | None = None
_default_path: Path | None = None


def get_classifier(path: str | Path | None = None) -> BenefitClassifier:
    global _default, _default_path
    if path is not None:
        return BenefitClassifier(path)
    target = get_settings().keyword_rules_file
    if _default is None or _default_path != target:
        _default = BenefitClassifier(target)
        _default_path = target
    return _default


def reset_classifier() -> None:
    global _default, _default_path
    _default = None
    _default_path = None
