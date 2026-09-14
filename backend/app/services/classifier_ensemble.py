"""三方投票分類（閘門 + 類別）：關鍵字加減分 × embedding（bge-m3）× 本地 LLM。

原則（依使用者要求「不要漏抓、也不要輕易放行」）：
- 放行（是補助）：至少兩個獨立訊號同意；只有一個同意時交給 LLM 判斷。
- 不漏抓：任一訊號說「是補助」的頁面不會被直接丟掉——LLM 也說不是時保留為「疑似補助，待人工確認」（uncertain），
  進資料中心但不進媒合；LLM 不可用時同樣保留為待確認。
- 類別：關鍵字前 3 名、embedding 前 3 名、LLM 的答案三方投票；兩方一致才算確定，否則標「類別待確認」並保留候選為次類別。
- 結構性排除（申請書、進度查詢、統計…）仍由 admission.page_kind 決定，因為那是頁面類型而不是語意。
每個決定都寫進 signals / decision_basis，資料中心可以看到三方各自的判斷。
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field

from ..config import get_settings
from ..registry import get_registry
from . import admission
from .classifier import ClassificationResult, get_classifier

log = logging.getLogger(__name__)

# 門檻（可依黃金集回測調整；scripts/eval_classifier.py 會印出各門檻的 precision / recall）
KW_YES_CONF = 0.6      # 關鍵字：is_benefit 且 confidence >= 此值才投「是」
KW_NO_RATIO = 0.5      # 關鍵字：signal < threshold × 此值才投「否」；其餘棄權
EMB_YES = 0.65         # embedding：p_benefit >= 此值投「是」
EMB_NO = 0.35          # embedding：p_benefit <= 此值投「否」
EMB_CAT_MARGIN = 0.005  # embedding 第一名與第二名的餘弦差距達此值才算有明確類別意見（bge-m3 的餘弦差距通常很小）
SECONDARY_EMB_GAP = 0.03
SECONDARY_KW_RATIO = 0.5


@dataclass
class EnsembleResult:
    is_benefit: bool
    page_kind: str                 # program | portal | 結構性排除的 kind
    category: str
    categories_secondary: list[str]
    domain: str
    confidence: float              # 0–1，代表三方一致程度
    category_confidence: str       # high | medium | low
    uncertain: bool                # True = 閘門不確定（疑似補助），需人工確認，不進媒合
    llm_used: bool
    decision_basis: str
    signals: dict = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    keyword: ClassificationResult | None = None
    category_uncertain: bool = False  # True = 類別待確認（閘門確定，仍可媒合，因為媒合用的是規則）

    def to_dict(self) -> dict:
        data = asdict(self)
        data.pop("keyword", None)
        if self.keyword is not None:
            data["keyword_result"] = {"is_benefit": self.keyword.is_benefit, "signal_score": self.keyword.signal_score, "threshold": self.keyword.threshold, "confidence": self.keyword.confidence, "category_scores": self.keyword.category_scores, "matched_signal": self.keyword.matched_signal[:8], "matched_negative": self.keyword.matched_negative[:6], "regions": self.keyword.regions}
        data["method"] = "ensemble"
        return data


def _keyword_vote(kw: ClassificationResult) -> str:
    if kw.is_benefit and kw.confidence >= KW_YES_CONF:
        return "yes"
    if not kw.is_benefit and kw.signal_score < kw.threshold * KW_NO_RATIO:
        return "no"
    return "abstain"


def _embedding_vote(emb: dict) -> str:
    p = emb.get("p_benefit")
    if p is None:
        return "unavailable"
    if p >= EMB_YES:
        return "yes"
    if p <= EMB_NO:
        return "no"
    return "abstain"


def _category_candidates(kw: ClassificationResult, emb: dict, llm_category: str) -> tuple[list[str], list[str]]:
    kw_top = [c for c in list(kw.category_scores.keys())[:3]]
    emb_top = [c for c, _ in (emb.get("top") or [])[:3]]
    union: list[str] = []
    for c in kw_top + emb_top + ([llm_category] if llm_category else []):
        if c and c not in union:
            union.append(c)
    return union, [kw_top[0] if kw_top else "", emb_top[0] if emb_top else "", llm_category]


def classify_ensemble(title: str, text: str, *, url: str = "", content_hash: str = "", use_llm: bool = True, llm_classify=None, seed_category: str = "") -> EnsembleResult:
    """llm_classify(title, text, candidates) -> verdict dict（llm/fill.classify_document）；use_llm=False 或 None 時不呼叫。"""
    registry = get_registry()
    settings = get_settings()
    signals: dict = {}
    reasons: list[str] = []

    # ---- 0. 頁面類型（結構性）
    kind, kind_reason = admission.page_kind(title, text, url)
    thin_program = kind == "attachment" and bool(admission.PROGRAM_NOUN_RE.search(admission.clean_title(title)))
    if kind in admission.EXCLUDED_KINDS and not thin_program:
        return EnsembleResult(False, kind, "", [], "", 1.0, "high", False, False, f"結構性排除：{kind_reason}", {"admission": {"kind": kind, "reason": kind_reason}}, [kind_reason])
    if kind == "portal":
        # 彙整頁：同一頁整理多項補助，保留供查閱（record_kind=portal，不進清單與媒合），不需要三方投票也不會被判成疑似補助
        kw_portal = get_classifier().classify(title, text)
        cat = seed_category if (seed_category and registry.category(seed_category) is not None) else (list(kw_portal.category_scores.keys()) or [""])[0]
        return EnsembleResult(True, "portal", cat, [], registry.domain_of(cat) if cat else "", 0.6, "low", False, False, f"彙整頁：{kind_reason}", {"admission": {"kind": kind, "reason": kind_reason}}, [kind_reason], kw_portal)
    if thin_program:
        # 標題像方案、但頁面只有附件清單：不漏抓 → 保留為待確認（資格與給付內容在附件，目前不抓附件）
        kw_thin = get_classifier().classify(title, text)
        cat = (list(kw_thin.category_scores.keys()) or [""])[0]
        return EnsembleResult(True, "program", cat, [], registry.domain_of(cat) if cat else "", 0.4, "low", True, False, "方案頁但內容只在附件，保留為待人工確認", {"admission": {"kind": "attachment", "reason": kind_reason}}, [kind_reason, "資格與給付內容在附件裡，需人工或抓附件後確認"], kw_thin)

    # ---- 1. 關鍵字
    kw = get_classifier().classify(title, text)
    kw_vote = _keyword_vote(kw)
    signals["keyword"] = {"vote": kw_vote, "is_benefit": kw.is_benefit, "confidence": kw.confidence, "signal": kw.signal_score, "threshold": kw.threshold, "top": list(kw.category_scores.keys())[:3]}

    # ---- 2. embedding
    emb: dict = {}
    try:
        from .embeddings import embedding_signal

        emb = embedding_signal(content_hash or title, title, text) or {}
    except Exception as exc:  # embedding 不可用 → 只剩兩方；不能因此放寬放行
        log.warning("embedding signal unavailable: %s", exc)
        emb = {}
    emb_vote = _embedding_vote(emb)
    signals["embedding"] = {"vote": emb_vote, "p_benefit": emb.get("p_benefit"), "knn": [emb.get("knn_yes"), emb.get("knn_no")], "top": [c for c, _ in (emb.get("top") or [])[:3]], "margin": emb.get("margin"), "model": emb.get("model")}

    votes = [v for v in (kw_vote, emb_vote) if v in {"yes", "no"}]
    yes_votes = votes.count("yes")
    no_votes = votes.count("no")

    # ---- 3. 閘門決策
    llm_used = False
    verdict: dict | None = None
    uncertain = False
    if seed_category and registry.category(seed_category) is not None and kind != "portal":
        # 來源設定檔明確指定的補助頁：閘門直接放行，類別仍三方確認
        is_benefit, basis = True, "來源設定檔指定為補助頁（seed_category）"
    elif yes_votes >= 2 and no_votes == 0:
        is_benefit, basis = True, "關鍵字與 embedding 都判定是補助"
    elif no_votes >= 2 and yes_votes == 0:
        is_benefit, basis = False, "關鍵字與 embedding 都判定不是補助"
    else:
        # 不一致或只有一方有意見 → LLM
        if use_llm and llm_classify is not None:
            try:
                candidates = list(kw.category_scores.keys())[:6]
                verdict = llm_classify(title, text, candidates)
            except Exception as exc:
                log.warning("llm classify failed: %s", exc)
                verdict = None
        if verdict is not None:
            llm_used = True
            signals["llm"] = {k: verdict.get(k) for k in ("is_benefit", "page_kind", "category", "confidence", "reason", "model")}
            if verdict.get("page_kind") in admission.EXCLUDED_KINDS and yes_votes == 0:
                return EnsembleResult(False, verdict["page_kind"], "", [], "", 0.8, "high", False, True, f"LLM 判定為 {verdict['page_kind']}，且無其他訊號說是補助", signals, reasons)
            if verdict.get("is_benefit"):
                is_benefit, basis = True, "三方不一致，LLM 判定是補助" if yes_votes else "關鍵字與 embedding 都無明確意見，LLM 判定是補助"
                if yes_votes == 0 and (no_votes >= 1):
                    uncertain = True  # 只有 LLM 說是：保留但待確認
                    basis += "（僅 LLM 一方，待人工確認）"
            else:
                if yes_votes >= 1:
                    is_benefit, uncertain, basis = True, True, "有訊號說是補助但 LLM 說不是：依「不漏抓」原則保留為疑似補助，待人工確認"
                else:
                    is_benefit, basis = False, "無訊號說是補助，LLM 也判定不是"
        else:
            # LLM 不可用：不能因為缺一方就漏抓；關鍵字弱弱地說是（is_benefit 但信心不足）或 embedding 過半也算「有人說是」
            weak_yes = yes_votes >= 1 or kw.is_benefit or (emb.get("p_benefit") or 0) >= 0.5
            if emb_vote == "unavailable" and kw.is_benefit and kw.confidence >= settings.classifier_uncertain_high:
                is_benefit, basis = True, "embedding 索引不存在、本地 AI 不可用：關鍵字信心足夠，單獨放行"
            elif weak_yes:
                is_benefit, uncertain, basis = True, True, "三方不一致且本地 AI 不可用：保留為疑似補助，待人工確認"
            else:
                is_benefit, basis = False, "無訊號說是補助（本地 AI 不可用）"

    if not is_benefit:
        return EnsembleResult(False, kind, "", [], "", 0.7 if votes else 0.5, "high", False, llm_used, basis, signals, reasons)

    # ---- 4. 類別（三方投票）
    llm_category = (verdict or {}).get("category") or ""
    union, tops = _category_candidates(kw, emb, llm_category)
    kw_top, emb_top = tops[0], tops[1]
    emb_has_opinion = bool(emb_top) and float(emb.get("margin") or 0) >= EMB_CAT_MARGIN
    category, cat_conf, cat_basis = "", "low", ""
    category_uncertain = False
    if seed_category and registry.category(seed_category) is not None:
        category, cat_conf, cat_basis = seed_category, "high", "來源設定檔指定類別"
    elif kw_top and emb_has_opinion and kw_top == emb_top:
        category, cat_conf, cat_basis = kw_top, "high", "關鍵字與 embedding 類別一致"
    elif llm_category and llm_category in {kw_top, emb_top}:
        category, cat_conf, cat_basis = llm_category, "medium", "LLM 與另一方類別一致"
    else:
        if verdict is None and use_llm and llm_classify is not None:
            try:
                verdict = llm_classify(title, text, union[:6] or list(kw.category_scores.keys())[:6])
                llm_used = True
                signals["llm"] = {k: verdict.get(k) for k in ("is_benefit", "page_kind", "category", "confidence", "reason", "model")}
                llm_category = verdict.get("category") or ""
            except Exception as exc:
                log.warning("llm category failed: %s", exc)
        if llm_category and llm_category in {kw_top, emb_top}:
            category, cat_conf, cat_basis = llm_category, "medium", "LLM 與另一方類別一致"
        elif llm_category and registry.category(llm_category) is not None:
            category, cat_conf, cat_basis = llm_category, "low", "只有 LLM 的類別意見，關鍵字與 embedding 不同（類別待確認）"
            category_uncertain = True
        elif emb_has_opinion:
            # 黃金集回測：embedding 分類別（助學金 vs 獎學金）比關鍵字準，不一致時以 embedding 為主、關鍵字列為次類別
            category, cat_conf, cat_basis = emb_top, "low", "關鍵字與 embedding 類別不同，以 embedding 為主（類別待確認）"
            category_uncertain = True
        elif kw_top:
            category, cat_conf, cat_basis = kw_top, "low" if emb else "medium", "只有關鍵字的類別意見" + ("（類別待確認）" if emb else "（embedding 索引不存在）")
            category_uncertain = bool(emb)
    if not category:
        category, cat_conf, cat_basis = (union[0] if union else ""), "low", "沒有任何類別意見"
        category_uncertain = True
    if llm_category and llm_category not in union:
        union.append(llm_category)

    # 次類別：其他候選中有支持的（embedding 接近第一名、關鍵字分數達第一名一半、或 LLM 提到）
    secondary: list[str] = []
    emb_scores = emb.get("category_scores") or {}
    kw_scores = kw.category_scores or {}
    top_emb = max(emb_scores.values()) if emb_scores else 0.0
    top_kw = max(kw_scores.values()) if kw_scores else 0.0
    for c in union:
        if c == category or registry.category(c) is None:
            continue
        supported = (c in emb_scores and top_emb - emb_scores[c] <= SECONDARY_EMB_GAP) or (c in kw_scores and top_kw and kw_scores[c] >= SECONDARY_KW_RATIO * top_kw) or (c == llm_category)
        if supported:
            secondary.append(c)
    secondary = secondary[:3]

    page_kind = "portal" if (kind == "portal" or (verdict or {}).get("page_kind") == "portal") else "program"
    agree = sum(1 for v in (kw_vote, emb_vote) if v == "yes") + (1 if (verdict or {}).get("is_benefit") else 0)
    confidence = round(min(1.0, 0.4 + 0.2 * agree + (0.2 if cat_conf == "high" else 0.1 if cat_conf == "medium" else 0.0)), 3)
    reasons.append(basis)
    reasons.append(cat_basis)
    if uncertain:
        reasons.append("閘門三方不一致：保留為疑似補助，待人工確認，不進媒合")
    elif category_uncertain:
        reasons.append("類別三方不一致：主類別待確認（候選存為次類別），仍可媒合")
    return EnsembleResult(True, page_kind, category, secondary, registry.domain_of(category) if category else "", confidence, cat_conf, uncertain, llm_used, basis + "；" + cat_basis, signals, reasons, kw, category_uncertain)
