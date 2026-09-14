"""Embedding（bge-m3，經本地 Ollama /api/embed）：文件向量快取、類別／閘門原型、相似度。

用途：分類的第二個獨立訊號（第一個是關鍵字加減分，第三個是本地 LLM）。
- 文件向量：標題 + 內文前 2500 字，以 content_hash 快取在 embeddings 集合，內容沒變不重算。
- 類別原型：每個葉節點類別 = 「名稱＋說明＋種子關鍵字」的向量，與已標記文件（黃金集、設定檔 seed_category、經 AI 確認的方案）的平均向量混合。
- 閘門原型：補助頁 vs 非補助頁的平均向量 + kNN 投票（k=7）。
所有向量都來自本機模型，不上雲；索引可用 rebuild_index() 重建（黃金集或登錄表更新後）。
"""

from __future__ import annotations

import logging
import math
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

import httpx
import yaml

from ..config import get_settings
from ..db import get_db
from ..registry import get_registry

log = logging.getLogger(__name__)
DOC_CHARS = 2500
BATCH = 16
INDEX_ID = "latest"


def embedding_model() -> str:
    return getattr(get_settings(), "embedding_model", None) or "bge-m3"


def embedding_available() -> bool:
    try:
        response = httpx.get(f"{get_settings().ollama_base_url.rstrip('/')}/api/tags", timeout=3.0)
        names = [m.get("name", "") for m in response.json().get("models", [])] if response.status_code == 200 else []
        wanted = embedding_model()
        return any(n == wanted or n.split(":")[0] == wanted.split(":")[0] for n in names)
    except Exception:
        return False


def embed_texts(texts: list[str]) -> list[list[float]]:
    """POST /api/embed（批次 16）。回傳 L2 正規化後的向量。"""
    base = get_settings().ollama_base_url.rstrip("/")
    model = embedding_model()
    out: list[list[float]] = []
    for i in range(0, len(texts), BATCH):
        chunk = [t[:DOC_CHARS] if t else " " for t in texts[i : i + BATCH]]
        response = httpx.post(f"{base}/api/embed", json={"model": model, "input": chunk}, timeout=120.0)
        if response.status_code >= 400:
            raise RuntimeError(f"Ollama embed 錯誤 {response.status_code}: {response.text[:200]}")
        for vec in response.json().get("embeddings", []):
            out.append(_normalize(vec))
    return out


def _normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def doc_text(title: str, text: str) -> str:
    return f"{title or ''}\n{(text or '')[:DOC_CHARS]}"


def doc_embedding(content_hash: str, title: str, text: str) -> list[float]:
    """依 content_hash 快取；內容沒變不重算。"""
    db = get_db()
    key = f"{embedding_model()}:{content_hash}"
    cached = db.embeddings.find_one({"_id": key}, {"vector": 1})
    if cached and cached.get("vector"):
        return cached["vector"]
    vec = embed_texts([doc_text(title, text)])[0]
    db.embeddings.update_one({"_id": key}, {"$set": {"vector": vec, "model": embedding_model(), "dims": len(vec), "created_at": datetime.now(timezone.utc)}}, upsert=True)
    return vec


def _mean(vectors: list[list[float]]) -> list[float] | None:
    if not vectors:
        return None
    dims = len(vectors[0])
    acc = [0.0] * dims
    for v in vectors:
        for i, x in enumerate(v):
            acc[i] += x
    return _normalize([x / len(vectors) for x in acc])


def _mix(a: list[float] | None, b: list[float] | None, wa: float = 0.5) -> list[float] | None:
    if a is None:
        return b
    if b is None:
        return a
    return _normalize([wa * x + (1 - wa) * y for x, y in zip(a, b)])


# ----------------------------------------------------------------- labelled examples
def gold_path() -> Path:
    base = Path(__file__).resolve().parents[3]  # repo root
    return base / "data" / "gold" / "gold_labels.yaml"


def normalize_verdict(value) -> str:
    """YAML 1.1 會把 yes/no 讀成布林：統一成 yes / no / portal。"""
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return str(value or "").strip().lower()


def gold_labels() -> list[dict]:
    path = gold_path()
    if not path.exists():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = []
    for row in data.get("labels") or []:
        row = dict(row)
        row["is_benefit"] = normalize_verdict(row.get("is_benefit"))
        rows.append(row)
    return rows


def labelled_examples() -> tuple[list[tuple[str, list[float], str]], dict[str, list[dict]]]:
    """回傳 (閘門樣本 [(doc_id, vec, "yes"|"no")], 類別樣本 {cat: [vec]})。
    來源優先序：黃金集（人工標記）> 設定檔 seed_category > 經 AI 確認的方案（keyword+llm）。負例：黃金集 no + 結構性排除頁。"""
    db = get_db()
    registry = get_registry()
    gate: list[tuple[str, list[float], str]] = []
    cats: dict[str, list[dict]] = {}
    seen: set[str] = set()

    def add(doc: dict, label: str, category: str) -> None:
        if not doc or doc["_id"] in seen or len(doc.get("raw_text") or "") < 60:
            return
        seen.add(doc["_id"])
        vec = doc_embedding(doc.get("content_hash", doc["_id"]), doc.get("title", ""), doc.get("raw_text", ""))
        gate.append((doc["_id"], vec, label))
        if label == "yes" and category and registry.category(category) is not None:
            cats.setdefault(category, []).append({"id": doc["_id"], "vector": vec})

    for row in gold_labels():
        doc = db.raw_documents.find_one({"_id": row.get("id")}, {"title": 1, "raw_text": 1, "content_hash": 1})
        verdict = row.get("is_benefit", "")
        if verdict in {"yes", "portal"}:
            add(doc, "yes", str(row.get("category") or ""))
        elif verdict == "no":
            add(doc, "no", "")
    for doc in db.raw_documents.find({"meta.seed_category": {"$exists": True, "$ne": ""}, "processing_status": {"$in": ["extracted", "needs_review"]}}, {"title": 1, "raw_text": 1, "content_hash": 1, "meta.seed_category": 1}):
        add(doc, "yes", (doc.get("meta") or {}).get("seed_category", ""))
    for b in db.benefits.find({"record_kind": "program", "is_canonical": True, "classification.method": "keyword+llm"}, {"raw_document_id": 1, "category": 1}):
        doc = db.raw_documents.find_one({"_id": b.get("raw_document_id")}, {"title": 1, "raw_text": 1, "content_hash": 1})
        add(doc, "yes", b.get("category", ""))
    for doc in db.raw_documents.find({"processing_status": "filtered_out", "classification.method": "admission"}, {"title": 1, "raw_text": 1, "content_hash": 1}):
        add(doc, "no", "")
    return gate, cats


# ----------------------------------------------------------------- index
def rebuild_index() -> dict:
    """重建類別原型與閘門樣本，存到 embedding_index.latest。"""
    db = get_db()
    registry = get_registry()
    model = embedding_model()
    gate, cats = labelled_examples()
    leaves = registry.leaves()
    seed_rules = {}
    try:
        seed_rules = yaml.safe_load(Path(get_settings().resolve_path(get_settings().keyword_rules_seed_path)).read_text(encoding="utf-8")) or {}
    except Exception:
        pass
    desc_texts = []
    for leaf in leaves:
        seeds = [k.get("term") for k in ((seed_rules.get("categories") or {}).get(leaf.id) or {}).get("keywords", []) if k.get("term")]
        desc_texts.append(f"{leaf.label}：{leaf.description}。關鍵字：{'、'.join(str(s) for s in seeds[:8])}")
    desc_vecs = embed_texts(desc_texts)
    prototypes = {}
    for leaf, dvec in zip(leaves, desc_vecs):
        examples = cats.get(leaf.id, [])
        centroid = _mean([e["vector"] for e in examples])
        prototypes[leaf.id] = {"vector": _mix(dvec, centroid, 0.5) if centroid else dvec, "description_vector": dvec, "example_vectors": examples, "examples": len(examples), "label": leaf.label, "domain": leaf.domain}
    pos = _mean([v for _, v, y in gate if y == "yes"])
    neg = _mean([v for _, v, y in gate if y == "no"])
    doc = {
        "_id": INDEX_ID, "model": model, "registry_version": registry.version, "built_at": datetime.now(timezone.utc),
        "prototypes": prototypes, "gate": {"positive": pos, "negative": neg, "examples": [{"id": i, "vector": v, "label": y} for i, v, y in gate]},
        "counts": {"gate_yes": sum(1 for _, _, y in gate if y == "yes"), "gate_no": sum(1 for _, _, y in gate if y == "no"), "categories_with_examples": sum(1 for p in prototypes.values() if p["examples"])},
    }
    db.embedding_index.replace_one({"_id": INDEX_ID}, doc, upsert=True)
    get_index.cache_clear()
    return doc["counts"]


@lru_cache
def get_index() -> dict | None:
    return get_db().embedding_index.find_one({"_id": INDEX_ID})


# ----------------------------------------------------------------- classification signal
def gate_probability(vec: list[float], pos: list[float] | None, neg: list[float] | None, cat_scores: dict[str, float], knn_yes: int, knn_no: int) -> dict:
    """是補助的機率：max(對補助頁平均向量, 對最像的類別原型) − 對非補助頁平均向量 → sigmoid，再與 kNN 投票平均。
    類別原型含類別說明文字，所以正例很少的領域（長照服務頁）也能靠「像不像日間照顧的描述」得到訊號。"""
    neg_cos = cosine(vec, neg) if neg is not None else 0.0
    pos_cos = cosine(vec, pos) if pos is not None else 0.0
    top_cat = max(cat_scores.values()) if cat_scores else 0.0
    p_centroid = 1.0 / (1.0 + math.exp(-(pos_cos - neg_cos) * 40.0)) if pos is not None and neg is not None else 0.5
    p_topic = 1.0 / (1.0 + math.exp(-(top_cat - neg_cos) * 40.0)) if neg is not None and cat_scores else 0.5
    p_knn = (knn_yes + 0.5) / (knn_yes + knn_no + 1.0) if (knn_yes + knn_no) else 0.5
    p_benefit = round(0.5 * max(p_centroid, p_topic) + 0.5 * p_knn, 3)
    return {"p_benefit": p_benefit, "p_centroid": round(p_centroid, 3), "p_topic": round(p_topic, 3), "p_knn": round(p_knn, 3)}


def embedding_signal(content_hash: str, title: str, text: str, *, k: int = 7) -> dict:
    """回傳 {p_benefit, knn_yes, knn_no, category_scores:{cat: cos}, top:[(cat, cos)], margin}。索引不存在 → {}。"""
    index = get_index()
    if not index:
        return {}
    vec = doc_embedding(content_hash, title, text)
    gate = index.get("gate") or {}
    pos, neg = gate.get("positive"), gate.get("negative")
    scored = sorted(((cosine(vec, e["vector"]), e["label"]) for e in gate.get("examples") or []), key=lambda t: -t[0])[:k]
    knn_yes = sum(1 for _, y in scored if y == "yes")
    knn_no = sum(1 for _, y in scored if y == "no")
    cat_scores = {cat: round(cosine(vec, p["vector"]), 4) for cat, p in (index.get("prototypes") or {}).items()}
    probs = gate_probability(vec, pos, neg, cat_scores, knn_yes, knn_no)
    top = sorted(cat_scores.items(), key=lambda kv: -kv[1])[:5]
    margin = round(top[0][1] - top[1][1], 4) if len(top) > 1 else 0.0
    return {**probs, "knn_yes": knn_yes, "knn_no": knn_no, "category_scores": dict(top), "top": top, "margin": margin, "model": index.get("model")}
