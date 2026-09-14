"""關鍵字統計（v2）：由實際爬回的語料統計出「篩選補助頁面」與「分類」用的關鍵字，而不是人工缺什麼補什麼。

方法（可重現、可解釋）：
1. 語料 = MongoDB raw_documents（html / pdf / 文字型資料集；不含 skipped）。
   - P（正例，有類別標籤）：來源設定檔 pages 的 seed_category、以及 v1 資料庫已標記類別的舊文件
   - U（未標記）：往下追連結抓到的頁面（可能是補助，也可能是導覽、隱私權等一般頁面）
2. 斷詞：中文以字元 n-gram（2～6 字）、英數以 token；每份文件只算一次（document frequency）。
3. 對每個 n-gram 做「含 Dirichlet 先驗的 log-odds ratio」（Monroe et al. 2008）的 z 分數：
   - benefit_signal：P vs U → z ≥ +2.5 為補助訊號詞，z ≤ −2.5 為負面詞（導覽、隱私權、瀏覽人次…）
   - categories：每個類別 vs P 中其他類別 → z ≥ 1.64 的詞為該類別關鍵字
   - condition_cues：含登錄表屬性別名的句子 vs 其他句子 → 條件句提示詞
   - attribute aliases：含某屬性種子別名的句子 vs 其他句子 → 該屬性的候選新別名
4. 冗餘過濾：子字串／超字串且文件頻率相近的詞只保留 z 較高者。
5. 產出 keyword_rules_v2.yaml（分類器讀取）、attribute_aliases_mined.yaml（登錄表載入）與
   docs/generated/keyword-report.md（完整統計表，供審核）。
"""

from __future__ import annotations

import json
import logging
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..config import PROJECT_DIR, get_settings
from ..db import get_db, utcnow
from ..registry import get_registry
from .normalization import normalize_text

log = logging.getLogger(__name__)

CJK_RUN_RE = re.compile(r"[一-鿿]+")
ASCII_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9]{1,15}")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[。；;！\n])")
NUMBER_RE = re.compile(r"[0-9０-９一二三四五六七八九十百千萬]+\s*(?:歲|分|元|個月|年|級|倍|%|％)")
ASCII_STOP = {"https", "http", "www", "com", "gov", "edu", "org", "tw", "pdf", "odt", "docx", "doc", "xls", "xlsx", "html", "aspx", "php", "jpg", "png", "google", "forms", "gle", "line", "facebook", "email"}
# 網站結構頁（不是補助內容）的標題特徵：只用於「語料標記」（結構性負例），不直接當分類規則
STRUCTURAL_NEGATIVE_TITLE_RE = re.compile(
    r"(隱私權|資訊安全|網站導覽|開放宣告|粉絲團|youtube|facebook|最新消息|資訊公開|新聞稿|短片|宣導|標售|拍賣|得標|契約價|試算|商品查詢|統計|名單|名冊|窗口|會議|報告|範本|問答集|條例|廢止|聯絡|交通位置|常見問題|下載專區|另開新視窗|檔案下載|訓練班|登錄辦法|法人|授權公告|開課資訊|徵求)",
    re.I,
)
# 列表頁（分頁標記）：「共 62 筆資料」「每頁顯示 20 40 60 筆」「第 1/4 頁」
LISTING_RE = re.compile(r"(共\s*\d+\s*筆|每頁顯示|第\s*\d+\s*/\s*\d+\s*頁)")
# 偽正例（種子分類器自我標記）額外要求：標題本身要像一項給付／服務
BENEFIT_TITLE_RE = re.compile(r"(補助|津貼|給付|獎學金|獎助|助學|減免|救助|扶助|獎勵|補貼|方案|計畫|服務|安置|照顧|貸款|福利|保險|喘息|輔具|交通接送|租金)")
STOP_GRAMS = {"的", "之", "及", "或", "與", "於", "在", "者", "為", "以", "其", "本", "並", "所", "但", "由", "至", "自", "如", "各", "等", "後", "前", "上", "下", "中", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十"}

LEGACY_CATEGORY_MAP = {
    "scholarship": "scholarship", "student_aid": "student_aid", "grant": "scholarship", "tuition_support": "tuition_waiver", "education_subsidy": "education_subsidy",
    "housing_support": "housing_support", "youth_support": "youth_development", "emergency_aid": "emergency_aid_student", "loan": "student_loan", "other": "",
}


# ------------------------------------------------------------------ tokens
def region_forms() -> set[str]:
    """縣市名（含台／臺寫法與去掉市／縣的短寫）：地區是另外抽的欄位，不可混進訊號詞或類別詞。"""
    from .normalization import CITIES

    forms: set[str] = set()
    for city in CITIES:
        for variant in {city, city.replace("臺", "台")}:
            forms.add(variant)
            forms.add(variant[:-1])
    forms.update({"臺灣", "台灣", "全國", "全台", "全臺"})
    return forms


def is_region_term(term: str, forms: set[str] | None = None) -> bool:
    forms = forms if forms is not None else region_forms()
    norm = normalize_text(term)
    return any(f in norm or norm in f for f in forms if len(f) >= 2)


def ngrams(text: str, n_min: int = 2, n_max: int = 6) -> set[str]:
    grams: set[str] = set()
    norm = normalize_text(text)
    for run in CJK_RUN_RE.findall(norm):
        length = len(run)
        for n in range(n_min, n_max + 1):
            for i in range(0, length - n + 1):
                gram = run[i : i + n]
                if gram[0] in STOP_GRAMS or gram[-1] in STOP_GRAMS:
                    continue
                grams.add(gram)
    for token in ASCII_TOKEN_RE.findall(norm):
        token = token.lower()
        if token in ASCII_STOP or len(token) < 3:
            continue
        grams.add(token)
    return grams


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT_RE.split(text or "") if s and len(s.strip()) >= 6]


# ---------------------------------------------------------------- log-odds
def log_odds_z(counts_a: Counter, n_a: int, counts_b: Counter, n_b: int, background: Counter, alpha0: float = 200.0, min_df: int = 3) -> dict[str, tuple[float, int, int]]:
    """回傳 {term: (z, df_a, df_b)}；z > 0 代表在 A 中更常見。"""
    total_bg = sum(background.values()) or 1
    result: dict[str, tuple[float, int, int]] = {}
    for term, bg in background.items():
        y_a, y_b = counts_a.get(term, 0), counts_b.get(term, 0)
        if y_a + y_b < min_df:
            continue
        alpha = alpha0 * bg / total_bg
        delta = math.log((y_a + alpha) / (n_a + alpha0 - y_a - alpha)) - math.log((y_b + alpha) / (n_b + alpha0 - y_b - alpha))
        var = 1.0 / (y_a + alpha) + 1.0 / (y_b + alpha)
        result[term] = (delta / math.sqrt(var), y_a, y_b)
    return result


def dedupe_terms(items: list[tuple[str, float, int]], *, keep: int) -> list[tuple[str, float, int]]:
    """items: (term, z, df)。子字串／超字串且 df 相近者只留一個：df 相近時偏好較長（較具體）的詞，
    例如「申請資」「請資格」「申請資格」三者 df 相近 → 只留「申請資格」。"""
    ordered = sorted(items, key=lambda t: (-t[1], -len(t[0])))
    kept: list[tuple[str, float, int]] = []
    for term, z, df in ordered:
        replaced = False
        redundant = False
        for index, (k_term, k_z, k_df) in enumerate(kept):
            close = abs(df - k_df) <= max(1, int(0.3 * max(df, k_df)))
            if term in k_term and close:
                redundant = True  # 已有更長且 df 相近的詞
                break
            if k_term in term and close and z >= 0.7 * k_z:
                kept[index] = (term, z, df)  # 用較長的詞取代較短的
                replaced = True
                break
        if redundant or replaced:
            continue
        kept.append((term, z, df))
    # 取代後可能仍有彼此包含的詞，再掃一次
    final: list[tuple[str, float, int]] = []
    for term, z, df in sorted(kept, key=lambda t: (-len(t[0]), -t[1])):
        if any(term in f_term and abs(df - f_df) <= max(1, int(0.3 * max(df, f_df))) for f_term, _f_z, f_df in final):
            continue
        final.append((term, z, df))
    final.sort(key=lambda t: -t[1])
    return final[:keep]


def weight_from_z(z: float, cap: int = 5) -> int:
    return max(1, min(cap, int(round(abs(z) / 2.0))))


# ------------------------------------------------------------------ corpus
def load_corpus() -> dict:
    """從 MongoDB 取語料並貼標籤。

    標籤來源（優先順序）：
    0. 黃金標註集 data/gold/gold_labels.yaml（逐筆讀原文標的：yes → 主類別、no → 明確負例、portal → 不參與）
    1. 來源設定檔的 seed_category（設定檔明確指定的補助頁）
    2. v1 資料庫已分類的舊文件
    3. 機構名單／統計資料集 → 明確負例
    4. 其餘（往下追連結抓到的頁面）用「種子分類器」自我標記：訊號分數高且有明確類別 → 該類別的偽正例；
       訊號分數低 → 負例；中間地帶 → 不參與統計（避免把真正的補助頁當成負例，例如台灣就業通拆出來的各項津貼）
    """
    from .classifier import BenefitClassifier

    db = get_db()
    settings = get_settings()
    seed_classifier = BenefitClassifier(settings.resolve_path(settings.keyword_rules_seed_path))
    legacy_labels: dict[str, str] = {}
    legacy = settings.legacy_seed_file
    if legacy.exists():
        try:
            payload = json.loads(legacy.read_text(encoding="utf-8"))
            for row in payload.get("scholarships", []):
                mapped = LEGACY_CATEGORY_MAP.get(row.get("category", ""), "")
                if mapped and row.get("raw_document_id"):
                    legacy_labels[row["raw_document_id"]] = mapped
            for row in payload.get("raw_documents", []):
                if row.get("processing_status") == "filtered_out":
                    legacy_labels[row["id"]] = "__negative__"
        except Exception as exc:  # pragma: no cover
            log.warning("legacy seed unreadable: %s", exc)
    gold: dict[str, str] = {}
    try:
        from .embeddings import gold_labels

        for row in gold_labels():
            verdict = row.get("is_benefit")
            if verdict == "yes" and row.get("category"):
                gold[row["id"]] = row["category"]
            elif verdict == "no":
                gold[row["id"]] = "__negative__"
            elif verdict == "portal":
                gold[row["id"]] = "__portal__"
    except Exception as exc:  # pragma: no cover
        log.warning("gold labels unreadable: %s", exc)
    docs: list[dict] = []
    pseudo = {"positive": 0, "negative": 0, "undecided": 0, "structural_negative": 0, "gold": 0}
    for raw in db.raw_documents.find({"processing_status": {"$ne": "skipped"}, "content_type": {"$in": ["html", "pdf", "csv", "json", "xml"]}}, {"title": 1, "raw_text": 1, "meta": 1, "source_id": 1, "content_type": 1}):
        text = (raw.get("title", "") + "\n" + (raw.get("raw_text") or "")).strip()
        if len(text) < 60:
            continue
        meta = raw.get("meta") or {}
        if gold.get(raw["_id"]) == "__portal__":
            continue  # 彙整頁：既不是負例也不是單一類別的正例，不參與統計
        label = gold.get(raw["_id"]) or meta.get("seed_category") or legacy_labels.get(raw["_id"], "")
        label_source = "gold" if raw["_id"] in gold else ("seed" if label else "")
        if label_source == "gold":
            pseudo["gold"] += 1
        if meta.get("data_kind") in {"providers", "statistics", "providers_text"}:
            label, label_source = "__negative__", "dataset"
        title_text = raw.get("title", "") or ""
        if not label and (STRUCTURAL_NEGATIVE_TITLE_RE.search(title_text) or LISTING_RE.search((raw.get("raw_text") or "")[:800])):
            # 網站結構頁／列表頁：結構性負例（只影響語料標記）
            label, label_source = "__negative__", "structural"
            pseudo["structural_negative"] += 1
        if not label:
            result = seed_classifier.classify(title_text, raw.get("raw_text") or "")
            best = max(result.category_scores.values(), default=0.0)
            if result.is_benefit and result.signal_score >= 2.0 * result.threshold and best >= 6 and BENEFIT_TITLE_RE.search(title_text):
                label, label_source = result.category, "pseudo"
                pseudo["positive"] += 1
            elif result.signal_score < result.threshold:
                label, label_source = "__negative__", "pseudo"
                pseudo["negative"] += 1
            else:
                pseudo["undecided"] += 1
                continue
        docs.append({"id": raw["_id"], "source_id": raw["source_id"], "title": raw.get("title", ""), "text": text, "label": label, "label_source": label_source, "depth": int(meta.get("depth", 0) or 0), "content_type": raw.get("content_type")})
    return {"docs": docs, "pseudo": pseudo}


# -------------------------------------------------------------------- mine
def mine(min_df: int = 3) -> dict:
    registry = get_registry()
    corpus = load_corpus()
    docs = corpus["docs"]
    positives = [d for d in docs if d["label"] and d["label"] != "__negative__"]
    negatives = [d for d in docs if d["label"] == "__negative__"]
    unlabeled = [d for d in docs if not d["label"]]
    contrast = negatives + unlabeled  # 弱負例：一般頁面 + 未標記頁面

    doc_grams = {d["id"]: ngrams(d["text"]) for d in docs}
    df_all: Counter = Counter()
    for grams in doc_grams.values():
        df_all.update(grams)
    # 跨來源性：每個詞出現在幾個不同來源的文件裡；只在單一網站出現的詞多半是版面樣板字，不能當通用規則
    sources_by_term: dict[str, set[str]] = defaultdict(set)
    for d in docs:
        for gram in doc_grams[d["id"]]:
            sources_by_term[gram].add(d["source_id"])

    def multi_source(term: str) -> bool:
        return len(sources_by_term.get(term, ())) >= 2
    df_pos: Counter = Counter()
    for d in positives:
        df_pos.update(doc_grams[d["id"]])
    df_con: Counter = Counter()
    for d in contrast:
        df_con.update(doc_grams[d["id"]])

    # ---- benefit signal
    regions = region_forms()
    n_pos, n_con = max(1, len(positives)), max(1, len(contrast))
    signal = log_odds_z(df_pos, len(positives), df_con, len(contrast), df_all, min_df=min_df) if contrast else {}

    def lift(a: int, b: int) -> float:
        """在補助頁的文件出現率 ÷ 在非補助頁的文件出現率（b=0 時以 0.5 筆計）。"""
        return (a / n_pos) / (max(b, 0.5) / n_con)

    # 訊號詞：z>=3、至少出現在 8% 的補助頁、非補助頁出現率 <=30%、lift>=3（避免「資訊」「辦理」「相關」這類公文常用詞）
    pos_terms = dedupe_terms(
        [(t, z, a) for t, (z, a, b) in signal.items() if z >= 3.0 and a >= max(3, int(0.08 * n_pos)) and b / n_con <= 0.30 and lift(a, b) >= 3.0 and multi_source(t) and not is_region_term(t, regions)],
        keep=80,
    )
    max_pos_df = max(2, int(0.03 * len(positives)))
    neg_terms = dedupe_terms([(t, -z, b) for t, (z, a, b) in signal.items() if z <= -3.5 and b >= 5 and a <= max_pos_df and len(t) >= 2 and not is_region_term(t, regions)], keep=40)
    term_stats = {t: {"pos_rate": round(a / n_pos, 3), "neg_rate": round(b / n_con, 3), "lift": round(lift(a, b), 2)} for t, (z, a, b) in signal.items()}

    # ---- categories
    df_by_cat: dict[str, Counter] = defaultdict(Counter)
    n_by_cat: Counter = Counter()
    for d in positives:
        df_by_cat[d["label"]].update(doc_grams[d["id"]])
        n_by_cat[d["label"]] += 1
    category_terms: dict[str, list[tuple[str, float, int]]] = {}
    for cat, df_cat in df_by_cat.items():
        rest = Counter(df_pos)
        rest.subtract(df_cat)
        rest = +rest
        n_rest = len(positives) - n_by_cat[cat]
        if n_by_cat[cat] < 2 or n_rest < 2:
            continue
        stats = log_odds_z(df_cat, n_by_cat[cat], rest, n_rest, df_pos, alpha0=100.0, min_df=2)
        # 類別詞：z>=2、在其他類別的出現率 <=30%、排除縣市名（地區另外抽）
        min_cat_df = max(2, int(math.ceil(0.3 * n_by_cat[cat])))
        category_terms[cat] = dedupe_terms(
            [
                (t, z, a)
                for t, (z, a, b) in stats.items()
                if z >= 2.0 and a >= min_cat_df and len(t) <= 5 and b / max(1, n_rest) <= 0.30 and multi_source(t) and not is_region_term(t, regions)
                # 對非補助頁也要有鑑別力：在非補助頁的出現率不能超過該類別出現率的一半（去掉「相關連結」「客服專線」等版面字）
                and (df_con.get(t, 0) / n_con) <= 0.5 * (a / n_by_cat[cat])
            ],
            keep=25,
        )

    # ---- condition cues + attribute aliases（句子層級）
    all_sentences: list[str] = []
    for d in positives:
        all_sentences.extend(sentences(d["text"]))
    sent_grams = [ngrams(s, 2, 4) for s in all_sentences]
    sent_df_all: Counter = Counter()
    for grams in sent_grams:
        sent_df_all.update(grams)
    is_condition = [bool(registry.attributes_in_text(s)) and bool(NUMBER_RE.search(s) or registry.tags_in_text(s)) for s in all_sentences]
    cond_df: Counter = Counter()
    other_df: Counter = Counter()
    for grams, flag in zip(sent_grams, is_condition):
        (cond_df if flag else other_df).update(grams)
    n_cond = sum(is_condition)
    n_other = len(all_sentences) - n_cond
    cue_stats = log_odds_z(cond_df, n_cond, other_df, n_other, sent_df_all, alpha0=300.0, min_df=4) if n_cond and n_other else {}
    condition_cues = dedupe_terms([(t, z, a) for t, (z, a, b) in cue_stats.items() if z >= 3.0 and a >= 4 and len(t) >= 2], keep=40)

    mined_aliases: dict[str, list[dict]] = {}
    for attribute in registry.attributes.values():
        seeds = [normalize_text(a) for a in [attribute.label, *attribute.aliases]]
        with_df: Counter = Counter()
        without_df: Counter = Counter()
        n_with = 0
        for s, grams in zip(all_sentences, sent_grams):
            norm = normalize_text(s)
            if any(seed in norm for seed in seeds if len(seed) >= 2):
                with_df.update(grams)
                n_with += 1
            else:
                without_df.update(grams)
        if n_with < 4:
            continue
        stats = log_odds_z(with_df, n_with, without_df, len(all_sentences) - n_with, sent_df_all, alpha0=300.0, min_df=3)
        candidates = []
        for term, (z, a, b) in stats.items():
            if z < 3.0 or a < 3 or len(term) < 2:
                continue
            if any(term in seed or seed in term for seed in seeds):
                continue
            if any(term == c[0] for c in condition_cues):
                continue
            candidates.append((term, z, a))
        top = dedupe_terms(candidates, keep=8)
        if top:
            mined_aliases[attribute.id] = [{"term": t, "z": round(z, 2), "df": a, "sentences_with_seed": n_with} for t, z, a in top]

    generated_at = datetime.now(timezone.utc).isoformat()
    return {
        "generated_at": generated_at,
        "corpus": {
            "documents": len(docs), "positives": len(positives), "negatives": len(negatives), "unlabeled": len(unlabeled),
            "seed_labeled": sum(1 for d in positives if d.get("label_source") == "seed"), "pseudo_labeled": corpus.get("pseudo", {}),
            "categories": dict(n_by_cat), "sources": sorted({d["source_id"] for d in docs}), "sentences": len(all_sentences), "condition_sentences": n_cond,
        },
        "benefit_signal": {"positive": pos_terms, "negative": neg_terms},
        "term_stats": term_stats,
        "docs": docs,
        "categories": category_terms,
        "condition_cues": condition_cues,
        "mined_aliases": mined_aliases,
    }


# ------------------------------------------------------------------- write
def build_rules_yaml(result: dict, seed_rules: dict) -> dict:
    registry = get_registry()
    rules: dict = {
        "version": 2,
        "source": "mined",
        "generated_at": result["generated_at"],
        "method": "log-odds ratio with informative Dirichlet prior over character n-grams (2-6), document frequency; signal: z >= 3 and lift >= 3 (pos_rate / neg_rate) and neg_rate <= 0.30, region names excluded, term must occur in >= 2 sources; category: z >= 2 and other-category rate <= 0.30, >= 2 sources",
        "corpus": result["corpus"],
        "benefit_signal": {
            "threshold": int(seed_rules.get("benefit_signal", {}).get("threshold", 4)),
            "title_bonus": int(seed_rules.get("benefit_signal", {}).get("title_bonus", 2)),
            "keywords": [{"term": t, "weight": weight_from_z(z), "z": round(z, 2), "df": df, **result.get("term_stats", {}).get(t, {})} for t, z, df in result["benefit_signal"]["positive"]],
            "negative": [{"term": t, "weight": -weight_from_z(z, cap=4), "z": round(-z, 2), "df": df} for t, z, df in result["benefit_signal"]["negative"]],
        },
        "condition_cues": [{"term": t, "z": round(z, 2), "df": df} for t, z, df in result["condition_cues"]],
        "categories": {},
    }
    mined_negative = {k["term"] for k in rules["benefit_signal"]["negative"]}
    for kw in (seed_rules.get("benefit_signal", {}) or {}).get("negative", []) or []:
        if str(kw.get("term")) not in mined_negative:
            rules["benefit_signal"]["negative"].append({"term": str(kw["term"]), "weight": int(kw.get("weight", -2)), "z": None, "df": None, "seed": True})
    seed_categories = seed_rules.get("categories", {}) or {}
    for leaf in registry.leaves():
        mined = result["categories"].get(leaf.id, [])
        entry: dict = {"label": leaf.label}
        if mined:
            entry["source"] = "mined"
            entry["documents"] = result["corpus"]["categories"].get(leaf.id, 0)
            entry["keywords"] = [{"term": t, "weight": weight_from_z(z, cap=4), "z": round(z, 2), "df": df} for t, z, df in mined]
            # 種子詞若未被統計到，保留為低權重（標記 seed）
            mined_terms = {t for t, _, _ in mined}
            for kw in seed_categories.get(leaf.id, {}).get("keywords", []):
                if kw["term"] not in mined_terms:
                    entry["keywords"].append({"term": kw["term"], "weight": max(1, int(kw.get("weight", 2)) - 1), "z": None, "df": None, "seed": True})
        else:
            entry["source"] = "seed"
            entry["documents"] = result["corpus"]["categories"].get(leaf.id, 0)
            entry["keywords"] = [{"term": kw["term"], "weight": int(kw.get("weight", 2)), "z": None, "df": None, "seed": True} for kw in seed_categories.get(leaf.id, {}).get("keywords", [])]
        rules["categories"][leaf.id] = entry
    return rules


def calibrate_threshold(rules: dict, docs: list[dict], *, max_negative_pass: float = 0.05) -> dict:
    """用探勘出的規則在標記語料上算每份文件的訊號分數，選門檻：非補助頁通過率 <= max_negative_pass 的門檻中 F1 最高者。
    回傳新的 rules（threshold 已更新，benefit_signal.calibration 記錄各門檻的 precision / recall）。"""
    import tempfile

    from .classifier import BenefitClassifier

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as handle:
        yaml.safe_dump(rules, handle, allow_unicode=True, sort_keys=False, width=200)
        tmp_path = handle.name
    try:
        classifier = BenefitClassifier(tmp_path)
    finally:
        try:
            Path(tmp_path).unlink()
        except OSError:
            pass
    scored = [(classifier.classify(d["title"], d["text"]).signal_score, d["label"] != "__negative__") for d in docs]
    n_pos = sum(1 for _, pos in scored if pos)
    n_neg = len(scored) - n_pos
    curve: list[dict] = []
    for threshold in range(4, 41):
        tp = sum(1 for s, pos in scored if pos and s >= threshold)
        fp = sum(1 for s, pos in scored if not pos and s >= threshold)
        precision = tp / max(1, tp + fp)
        recall = tp / max(1, n_pos)
        f1 = 2 * precision * recall / max(1e-9, precision + recall)
        curve.append({"threshold": threshold, "precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3), "negative_pass_rate": round(fp / max(1, n_neg), 3), "tp": tp, "fp": fp})
    eligible = [c for c in curve if c["negative_pass_rate"] <= max_negative_pass] or curve
    chosen = max(eligible, key=lambda c: (c["f1"], -c["threshold"]))
    rules["benefit_signal"]["threshold"] = int(chosen["threshold"])
    rules["benefit_signal"]["calibration"] = {
        "method": f"在標記語料（補助頁 {n_pos}、非補助頁 {n_neg}）上以探勘規則計算訊號分數；門檻取「非補助頁通過率 <= {int(max_negative_pass * 100)}%」中 F1 最高者",
        "chosen": chosen,
        "curve": [c for c in curve if c["threshold"] in {4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 28, 32, 36, 40} or c is chosen],
    }
    return rules


def build_report(result: dict, rules: dict) -> str:
    registry = get_registry()
    corpus = result["corpus"]
    lines: list[str] = []
    lines.append("# 關鍵字統計報告（由實際語料產生）\n")
    lines.append(f"產生時間：{result['generated_at']}（UTC）  \n方法：{rules['method']}\n")
    lines.append("## 1. 語料組成\n")
    lines.append("| 項目 | 數量 |\n| --- | ---: |")
    lines.append(f"| 文件總數 | {corpus['documents']} |")
    lines.append(f"| 有類別標籤（P） | {corpus['positives']} |")
    lines.append(f"| 明確負例（機構名單、統計、v1 過濾掉的公告） | {corpus['negatives']} |")
    lines.append(f"| 未標記（往下追連結抓到的頁面，作為弱負例） | {corpus['unlabeled']} |")
    pseudo = corpus.get("pseudo_labeled") or {}
    lines.append(f"| 種子分類器自我標記：偽正例 / 負例 / 不參與 | {pseudo.get('positive', 0)} / {pseudo.get('negative', 0)} / {pseudo.get('undecided', 0)}（設定檔與 v1 標記的正例 {corpus.get('seed_labeled', 0)}） |")
    lines.append(f"| 結構性負例（隱私權／最新消息列表／標售／統計／名單等網站結構頁，只用於標記語料） | {pseudo.get('structural_negative', 0)} |")
    lines.append("| 訊號詞篩選條件 | z ≥ 3、至少出現在 8% 的補助頁、非補助頁出現率 ≤ 30%、lift（補助頁出現率 ÷ 非補助頁出現率）≥ 3、至少出現在 2 個來源、排除縣市名 |")
    lines.append(f"| 句子數（P） | {corpus['sentences']}（其中條件句 {corpus['condition_sentences']}） |")
    lines.append(f"| 來源 | {', '.join(corpus['sources'])} |\n")
    lines.append("每個類別的標記文件數：\n")
    lines.append("| 類別 | 文件數 |\n| --- | ---: |")
    for cat, n in sorted(corpus["categories"].items(), key=lambda kv: -kv[1]):
        lines.append(f"| {registry.category_label(cat)}（{cat}） | {n} |")
    calibration = (rules.get("benefit_signal") or {}).get("calibration") or {}
    if calibration:
        chosen = calibration.get("chosen") or {}
        lines.append("\n## 1b. 訊號門檻校正（在標記語料上的自我評估）\n")
        lines.append(calibration.get("method", "") + "\n")
        lines.append("| 門檻 | precision | recall | F1 | 非補助頁通過率 | 通過的補助頁 | 通過的非補助頁 |\n| ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for c in calibration.get("curve", []):
            mark = " **←採用**" if c.get("threshold") == chosen.get("threshold") else ""
            lines.append(f"| {c['threshold']}{mark} | {c['precision']} | {c['recall']} | {c['f1']} | {c['negative_pass_rate']} | {c['tp']} | {c['fp']} |")
        lines.append("\n注意：語料標籤一部分來自設定檔與 v1 標記，一部分由種子分類器／結構規則自我標記，因此這是訓練資料上的估計；分數落在不確定區間的頁面仍會交給本地 AI 二次判斷。")
    lines.append("\n## 2. 補助訊號詞（補助頁 vs 非補助頁；z ≥ 3、lift ≥ 3、非補助頁出現率 ≤ 30%、跨 ≥ 2 個來源）\n")
    lines.append("| 詞 | 權重 | z | 在補助文件中出現的文件數 |\n| --- | ---: | ---: | ---: |")
    for kw in rules["benefit_signal"]["keywords"]:
        lines.append(f"| {kw['term']} | {kw['weight']} | {kw['z']} | {kw['df']} |")
    lines.append("\n## 3. 負面詞（一般頁面特徵，z ≤ −2.5）\n")
    lines.append("| 詞 | 權重 | z | 在一般頁面中出現的文件數 |\n| --- | ---: | ---: | ---: |")
    for kw in rules["benefit_signal"]["negative"]:
        lines.append(f"| {kw['term']} | {kw['weight']} | {kw['z']} | {kw['df']} |")
    lines.append("\n## 4. 各類別關鍵字（該類別 vs 其他類別；z ≥ 2、其他類別出現率 ≤ 30%、至少出現在 30% 的該類別文件、長度 ≤ 5、跨 ≥ 2 個來源、非補助頁出現率 ≤ 該類別出現率的一半）\n")
    for cat, entry in rules["categories"].items():
        source = "統計" if entry.get("source") == "mined" else "種子（語料不足，待補）"
        lines.append(f"### {entry['label']}（{cat}）— 來源：{source}，標記文件 {entry.get('documents', 0)} 份\n")
        if not entry["keywords"]:
            lines.append("（無）\n")
            continue
        lines.append("| 詞 | 權重 | z | df |\n| --- | ---: | ---: | ---: |")
        for kw in entry["keywords"]:
            lines.append(f"| {kw['term']} | {kw['weight']} | {kw['z'] if kw['z'] is not None else '—'} | {kw['df'] if kw['df'] is not None else '—'} |")
        lines.append("")
    lines.append("## 5. 條件句提示詞（含屬性別名與數值／身分的句子 vs 其他句子，z ≥ 3）\n")
    lines.append("| 詞 | z | 句子數 |\n| --- | ---: | ---: |")
    for kw in rules["condition_cues"]:
        lines.append(f"| {kw['term']} | {kw['z']} | {kw['df']} |")
    lines.append("\n## 6. 屬性別名候選（與種子別名同句共現，z ≥ 3；載入時只採用 z ≥ 3 者）\n")
    for attribute_id, aliases in result["mined_aliases"].items():
        attribute = registry.get(attribute_id)
        lines.append(f"- **{attribute.label if attribute else attribute_id}**（`{attribute_id}`，含種子別名的句子 {aliases[0]['sentences_with_seed']} 句）：" + "、".join(f"{a['term']}（z={a['z']}, df={a['df']}）" for a in aliases))
    lines.append("\n## 7. 使用方式\n")
    lines.append("- 分類器（app/services/classifier.py）讀取 `benefit_crawler/config/keyword_rules_v2.yaml`：補助訊號分數 ≥ threshold 且有類別分數才視為補助頁面；分數落在不確定區間時交給本地 AI 二次判斷。")
    lines.append("- 登錄表載入時合併 `app/registry/attribute_aliases_mined.yaml` 中 z ≥ 3 的別名，供條件句對屬性使用。")
    lines.append("- 重新爬取後執行 `python -m benefit_crawler --mine-keywords` 即可重算；所有數字皆可由語料重現。")
    return "\n".join(lines) + "\n"


def mine_and_write() -> dict:
    settings = get_settings()
    result = mine()
    seed_rules = {}
    seed_path = settings.resolve_path(settings.keyword_rules_seed_path)
    if seed_path.exists():
        seed_rules = yaml.safe_load(seed_path.read_text(encoding="utf-8")) or {}
    rules = build_rules_yaml(result, seed_rules)
    rules = calibrate_threshold(rules, result["docs"])
    target = settings.resolve_path(settings.keyword_rules_path)
    target.write_text(yaml.safe_dump(rules, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    aliases_doc = {"version": 2, "generated_at": result["generated_at"], "note": "由語料統計（同句共現 log-odds）產生的屬性別名候選；載入時只採用 z >= 3 者", "attributes": [{"id": k, "aliases": v} for k, v in result["mined_aliases"].items()]}
    settings.attribute_aliases_mined_file.write_text(yaml.safe_dump(aliases_doc, allow_unicode=True, sort_keys=False, width=200), encoding="utf-8")
    report_path = PROJECT_DIR / "docs" / "generated" / "keyword-report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, rules), encoding="utf-8")
    db = get_db()
    db.keyword_stats.update_one({"_id": "latest"}, {"$set": {"generated_at": result["generated_at"], "corpus": result["corpus"], "rules_path": str(target), "report_path": str(report_path), "benefit_terms": len(rules["benefit_signal"]["keywords"]), "negative_terms": len(rules["benefit_signal"]["negative"]), "categories_mined": sum(1 for c in rules["categories"].values() if c.get("source") == "mined"), "updated_at": utcnow()}}, upsert=True)
    from ..registry import reset_registry

    reset_registry()
    return {"rules": str(target), "report": str(report_path), "corpus": result["corpus"], "benefit_terms": len(rules["benefit_signal"]["keywords"]), "negative_terms": len(rules["benefit_signal"]["negative"]), "categories_mined": sum(1 for c in rules["categories"].values() if c.get("source") == "mined"), "mined_alias_attributes": len(result["mined_aliases"])}
