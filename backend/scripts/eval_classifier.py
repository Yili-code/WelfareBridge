"""用黃金集（data/gold/gold_labels.yaml）回測分類器：關鍵字單獨 vs embedding 單獨 vs 三方投票（含／不含 LLM）。

    python scripts/eval_classifier.py [--llm] [--out ../docs/generated/classifier-eval.md]

閘門（是不是補助）：把 yes 與 portal 都當正例（都要抓到，portal 只是不進媒合）；no 為負例。
類別：只對黃金集標 yes 的方案算主類別正確率；次類別命中也另計。
注意：embedding 索引若含黃金集本身（預設會），閘門 kNN 有洩漏；本腳本會用「留一法」重算 embedding 訊號（把該筆自己從 kNN 樣本排除），
類別原型也扣掉該筆的向量後再算，數字才有意義。
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_db  # noqa: E402
from app.registry import get_registry  # noqa: E402
from app.services import admission, embeddings  # noqa: E402
from app.services.classifier import get_classifier  # noqa: E402
from app.services.classifier_ensemble import EMB_NO, EMB_YES, KW_NO_RATIO, KW_YES_CONF, classify_ensemble  # noqa: E402


def loo_embedding_signal(index: dict, doc_id: str, vec: list[float], k: int = 7) -> dict:
    """留一法：kNN 與類別原型都排除自己。"""
    gate = index["gate"]
    examples = [e for e in gate["examples"] if e["id"] != doc_id]
    scored = sorted(((embeddings.cosine(vec, e["vector"]), e["label"]) for e in examples), key=lambda t: -t[0])[:k]
    knn_yes = sum(1 for _, y in scored if y == "yes")
    knn_no = sum(1 for _, y in scored if y == "no")
    pos = embeddings._mean([e["vector"] for e in examples if e["label"] == "yes"])
    neg = embeddings._mean([e["vector"] for e in examples if e["label"] == "no"])
    cat_scores = {}
    for cat, p in index["prototypes"].items():
        others = [e["vector"] for e in (p.get("example_vectors") or []) if e.get("id") != doc_id]
        centroid = embeddings._mean(others)
        proto = embeddings._mix(p.get("description_vector") or p["vector"], centroid, 0.5) if centroid else (p.get("description_vector") or p["vector"])
        cat_scores[cat] = round(embeddings.cosine(vec, proto), 4)
    top = sorted(cat_scores.items(), key=lambda kv: -kv[1])[:5]
    probs = embeddings.gate_probability(vec, pos, neg, cat_scores, knn_yes, knn_no)
    return {**probs, "knn_yes": knn_yes, "knn_no": knn_no, "category_scores": dict(top), "top": top, "margin": round(top[0][1] - top[1][1], 4) if len(top) > 1 else 0.0}


def prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return round(p, 3), round(r, 3), round(f, 3)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="三方投票時允許呼叫本地 LLM（慢）")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parents[2] / "docs" / "generated" / "classifier-eval.md"))
    args = parser.parse_args()
    db = get_db()
    registry = get_registry()
    index = embeddings.get_index()
    if not index:
        print("no embedding index; run embeddings.rebuild_index() first")
        return 1
    gold = embeddings.gold_labels()
    llm_fn = None
    if args.llm:
        from app.llm import fill

        llm_fn = fill.classify_document if fill.llm_available() else None
        print("llm:", "available" if llm_fn else "unavailable")

    rows = []
    for g in gold:
        doc = db.raw_documents.find_one({"_id": g["id"]}, {"title": 1, "raw_text": 1, "content_hash": 1, "source_url": 1, "meta.seed_category": 1})
        if not doc:
            continue
        title, text, url = doc.get("title", ""), doc.get("raw_text", ""), doc.get("source_url", "")
        truth = g["is_benefit"]
        if truth == "no" and g.get("closed"):
            truth = "yes"  # 已停辦的方案頁：閘門仍應放行，由 extractor 標 status=expired 隱藏，不算誤放行
        kind, _ = admission.page_kind(title, text, url)
        excluded = kind in admission.EXCLUDED_KINDS
        kw = get_classifier().classify(title, text)
        vec = embeddings.doc_embedding(doc.get("content_hash", g["id"]), title, text)
        emb = loo_embedding_signal(index, g["id"], vec)
        # 三方投票：用留一法的 embedding 訊號，需 monkeypatch embedding_signal
        embeddings_signal_backup = embeddings.embedding_signal
        embeddings.embedding_signal = lambda *_a, **_k: emb  # noqa: E731
        try:
            ens = classify_ensemble(title, text, url=url, content_hash=doc.get("content_hash", g["id"]), use_llm=bool(llm_fn), llm_classify=llm_fn)
        finally:
            embeddings.embedding_signal = embeddings_signal_backup
        rows.append({
            "id": g["id"], "title": g.get("title", "")[:36], "truth": truth, "truth_cat": g.get("category") or "", "truth_sec": g.get("secondary") or [], "kind_truth": g.get("kind", ""),
            "kw_yes": (not excluded) and kw.is_benefit, "kw_conf": kw.confidence, "kw_cat": (list(kw.category_scores.keys()) or [""])[0],
            "emb_p": emb["p_benefit"], "emb_yes": (not excluded) and emb["p_benefit"] >= 0.5, "emb_cat": emb["top"][0][0] if emb["top"] else "",
            "ens_yes": ens.is_benefit, "ens_cat": ens.category, "ens_sec": ens.categories_secondary, "ens_uncertain": ens.uncertain, "ens_llm": ens.llm_used, "ens_basis": ens.decision_basis, "excluded": excluded, "kind": kind,
        })

    def gate_stats(key: str) -> dict:
        tp = sum(1 for r in rows if r[key] and r["truth"] in {"yes", "portal"})
        fp = sum(1 for r in rows if r[key] and r["truth"] == "no")
        fn = sum(1 for r in rows if not r[key] and r["truth"] in {"yes", "portal"})
        tn = sum(1 for r in rows if not r[key] and r["truth"] == "no")
        p, rc, f = prf(tp, fp, fn)
        return {"tp": tp, "fp": fp, "fn": fn, "tn": tn, "precision": p, "recall": rc, "f1": f}

    def cat_stats(key: str) -> dict:
        yes_rows = [r for r in rows if r["truth"] == "yes" and r["truth_cat"]]
        exact = sum(1 for r in yes_rows if r[key] == r["truth_cat"])
        loose = sum(1 for r in yes_rows if r[key] == r["truth_cat"] or r[key] in r["truth_sec"])
        return {"n": len(yes_rows), "exact": exact, "loose": loose, "exact_rate": round(exact / len(yes_rows), 3) if yes_rows else 0, "loose_rate": round(loose / len(yes_rows), 3) if yes_rows else 0}

    gate = {"keyword": gate_stats("kw_yes"), "embedding": gate_stats("emb_yes"), "ensemble": gate_stats("ens_yes")}
    cats = {"keyword": cat_stats("kw_cat"), "embedding": cat_stats("emb_cat"), "ensemble": cat_stats("ens_cat")}
    ens_sec_hit = sum(1 for r in rows if r["truth"] == "yes" and r["truth_cat"] and r["ens_cat"] != r["truth_cat"] and r["truth_cat"] in r["ens_sec"])
    uncertain = sum(1 for r in rows if r["ens_yes"] and r["ens_uncertain"])
    llm_calls = sum(1 for r in rows if r["ens_llm"])

    lines = [f"# 分類器回測（黃金集 {len(rows)} 筆，留一法）", "", f"- 產生於 {datetime.now(timezone.utc).isoformat()}；LLM {'有' if llm_fn else '未'}參與三方投票；門檻 KW_YES_CONF={KW_YES_CONF} KW_NO_RATIO={KW_NO_RATIO} EMB_YES={EMB_YES} EMB_NO={EMB_NO}", f"- 黃金集：yes {sum(1 for r in rows if r['truth']=='yes')}、portal {sum(1 for r in rows if r['truth']=='portal')}、no {sum(1 for r in rows if r['truth']=='no')}（yes 與 portal 都算閘門正例；標 closed 的已停辦方案也算正例，由 status=expired 處理）", "", "## 1. 閘門（是不是補助）", "", "| 方法 | precision | recall | F1 | 漏抓 (FN) | 誤放行 (FP) |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name, s in gate.items():
        lines.append(f"| {name} | {s['precision']} | {s['recall']} | {s['f1']} | {s['fn']} | {s['fp']} |")
    lines += ["", f"- 三方投票放行中標「待人工確認」：{uncertain} 筆；LLM 被呼叫：{llm_calls} 筆", "", "## 2. 主類別（黃金集 yes 的方案）", "", "| 方法 | 樣本 | 主類別正確 | 主或次類別命中 | 主類別正確率 | 寬鬆正確率 |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name, s in cats.items():
        lines.append(f"| {name} | {s['n']} | {s['exact']} | {s['loose']} | {s['exact_rate']} | {s['loose_rate']} |")
    lines += ["", f"- 三方投票主類別錯但黃金集主類別出現在其次類別：{ens_sec_hit} 筆", "", "## 3. 漏抓（黃金集是補助但三方投票沒放行）", ""]
    for r in rows:
        if r["truth"] in {"yes", "portal"} and not r["ens_yes"]:
            lines.append(f"- {r['title']}（{r['truth']}/{r['truth_cat']}）：kw={r['kw_yes']}({r['kw_conf']}) emb={r['emb_p']} kind={r['kind']} → {r['ens_basis']}")
    lines += ["", "## 4. 誤放行（黃金集不收但三方投票放行）", ""]
    for r in rows:
        if r["truth"] == "no" and r["ens_yes"]:
            lines.append(f"- {r['title']}（{r['kind_truth']}）：kw={r['kw_yes']}({r['kw_conf']}) emb={r['emb_p']} uncertain={r['ens_uncertain']} → {r['ens_basis']}")
    lines += ["", "## 5. 主類別不同（三方投票 vs 黃金集）", ""]
    for r in rows:
        if r["truth"] == "yes" and r["truth_cat"] and r["ens_yes"] and r["ens_cat"] != r["truth_cat"]:
            lines.append(f"- {r['title']}：gold={r['truth_cat']} ens={r['ens_cat']} sec={r['ens_sec']} kw={r['kw_cat']} emb={r['emb_cat']}")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:22]))
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
