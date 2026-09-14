"""從實際程式碼、設定檔與資料庫產生文件（docs/generated/*.md），讓說明文件對應真實實作。

    python scripts/generate_docs.py

產生：
    docs/generated/registry-attributes.md   屬性登錄表逐欄（來自 attribute_registry.yaml + 語料統計別名 + 規則使用次數）
    docs/generated/taxonomy.md              領域／類別樹與身分本體
    docs/generated/sources.md               官方來源登錄與驗證結果（來自 sources.yaml + official_domains.yaml）
    docs/generated/pipeline-stats.md        目前 MongoDB 統計（來源 × 處理狀態、benefits 分布、規則統計、本地 AI 補齊統計）
    docs/generated/keyword-table.md         分類器實際使用的關鍵字表（來自 keyword_rules_v2.yaml；統計報告在 keyword-report.md）
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.config import get_settings  # noqa: E402
from app.registry import get_registry  # noqa: E402
from app.services.classifier import get_classifier  # noqa: E402
from benefit_crawler.base.registry import load_sources_config  # noqa: E402
from benefit_crawler.base.source_validator import SourceValidator  # noqa: E402

OUT = BACKEND.parent / "docs" / "generated"


def registry_attributes() -> str:
    registry = get_registry()
    usage: Counter = Counter()
    try:
        from app.db import get_db, ping

        if ping():
            for row in get_db().benefits.aggregate([{"$unwind": "$rules"}, {"$group": {"_id": "$rules.attribute_id", "n": {"$sum": 1}}}]):
                usage[row["_id"]] = row["n"]
    except Exception:
        pass
    lines = ["# 屬性登錄表（實際載入內容）", "", f"來源：`backend/app/registry/attribute_registry.yaml`（version {registry.version}）＋ `attribute_aliases_mined.yaml`（語料統計別名，只在本地 AI 候選中使用）。", "", "| 屬性 id | 型態 | 單位／允許值 | 領域 | 標籤 | 追問句 | 敏感度 | 硬過濾 | 推導 | 種子別名 | 統計別名（z≥3） | 規則使用次數 |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |"]
    for attribute in registry.attributes.values():
        values = attribute.unit or ("、".join(str(v.get("value")) for v in attribute.values[:8]) + ("…" if len(attribute.values) > 8 else ""))
        mined = "、".join(m["term"] for m in attribute.mined_aliases if float(m.get("z", 0)) >= 3)[:80]
        lines.append(f"| `{attribute.id}` | {attribute.type}{'（有序）' if attribute.ordered else ''} | {values} | {'、'.join(attribute.domains)} | {attribute.label} | {attribute.question} | {attribute.sensitivity} | {'✓' if attribute.hard_filter else ''} | {attribute.derived or ''} | {'、'.join(attribute.aliases)[:80]} | {mined} | {usage.get(attribute.id, 0)} |")
    return "\n".join(lines) + "\n"


def taxonomy() -> str:
    registry = get_registry()
    lines = ["# 領域／類別樹與身分本體（實際載入內容）", "", f"來源：`backend/app/registry/taxonomy.yaml`（version {registry.taxonomy_version}）、`identity_ontology.yaml`", "", "## 類別樹", ""]
    for domain in registry.domains():
        lines.append(f"- **{domain.label}**（`{domain.id}`）：{domain.description}")
        for child_id in domain.children:
            child = registry.taxonomy[child_id]
            if child.is_leaf:
                lines.append(f"  - {child.label}（`{child.id}`）— {child.description}；需求類型：{'、'.join(child.need_types) or '—'}；預設給付形式：{child.default_benefit_form or '—'}")
            else:
                lines.append(f"  - {child.label}（`{child.id}`）")
                for leaf_id in child.children:
                    leaf = registry.taxonomy[leaf_id]
                    lines.append(f"    - {leaf.label}（`{leaf.id}`）— {leaf.description}")
    lines += ["", "## 身分本體", "", "| id | 標籤 | 同義詞 | 對應屬性 | 隱含（具備即視為具備） | 依據 |", "| --- | --- | --- | --- | --- | --- |"]
    for tag in registry.tags.values():
        lines.append(f"| `{tag.id}` | {tag.label} | {'、'.join(tag.aliases)} | `{tag.attribute}` | {'、'.join(tag.implies) or '—'} | {tag.basis or '—'} |")
    return "\n".join(lines) + "\n"


def sources_table() -> str:
    settings = get_settings()
    validator = SourceValidator(settings.official_domains_file)
    lines = ["# 官方來源登錄與驗證結果", "", "來源：`backend/benefit_crawler/config/sources.yaml` + `official_domains.yaml`；驗證方法為網域白名單／後綴 + HTTPS + 頁面標題關鍵字。", "", "| id | 名稱 | 機關 | 類型 | 啟用 | 領域 | 頁面數（略過） | 追連結 | 網域驗證 | crawler |", "| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- |"]
    for config in load_sources_config(settings.sources_config_file):
        validation = validator.validate_url(config["base_url"])
        pages = config.get("pages") or []
        skipped = sum(1 for p in pages if p.get("skip"))
        follow = config.get("follow_links") or {}
        lines.append(f"| {config['id']} | {config['name']} | {config.get('organization', '')} | {config.get('provider_type', '')} | {'✓' if config.get('enabled', True) else ''} | {'、'.join(config.get('domains') or [])} | {len(pages)}（{skipped}） | {('深度 ' + str(follow.get('depth'))) if follow else ''} | {'✅ ' if validation.verified else '⚠️ '}{validation.method} | `{config.get('crawler', '').split('.')[-1]}` |")
    lines += ["", "## 略過的頁面（記錄原因，資料不進正式資料表）", "", "| 來源 | 頁面 | 網址 | 原因 |", "| --- | --- | --- | --- |"]
    for config in load_sources_config(settings.sources_config_file):
        for page in config.get("pages") or []:
            if page.get("skip"):
                lines.append(f"| {config['id']} | {page.get('title', '')} | {page['url'][:80]} | {page.get('skip_reason', '')} |")
    return "\n".join(lines) + "\n"


def keyword_table() -> str:
    classifier = get_classifier()
    rules = classifier.rules
    lines = ["# 分類器實際使用的關鍵字表", "", f"來源：`{get_settings().keyword_rules_file.name}`（{rules.get('source')}；產生時間 {rules.get('generated_at', '—')}）", f"方法：{rules.get('method', '種子規則')}", f"threshold = {classifier.threshold}，title_bonus = {classifier.title_bonus}；完整統計（z 分數、文件頻率、語料組成）見 keyword-report.md", ""]
    lines += ["## 補助訊號詞", "", "| 詞 | 權重 |", "| --- | ---: |"]
    lines += [f"| {t} | {w:g} |" for _, t, w in classifier.signal_terms]
    lines += ["", "## 負面詞", "", "| 詞 | 權重 |", "| --- | ---: |"]
    lines += [f"| {t} | {w:g} |" for _, t, w in classifier.negative_terms]
    lines += ["", "## 條件句提示詞", "", "、".join(classifier.condition_cues) or "—", ""]
    lines += ["## 各類別關鍵字", ""]
    for cat, terms in classifier.categories.items():
        spec = (rules.get("categories") or {}).get(cat, {})
        lines.append(f"- **{classifier.category_labels.get(cat, cat)}**（`{cat}`，{spec.get('source', 'seed')}，標記文件 {spec.get('documents', 0)}）：" + "、".join(f"{t}({w:g})" for _, t, w in terms))
    return "\n".join(lines) + "\n"


def pipeline_stats() -> str:
    lines = ["# Pipeline 統計（由目前 MongoDB 產生）", ""]
    try:
        from app.db import get_db, ping

        if not ping():
            return "\n".join(lines + ["（MongoDB 不可用，未產生統計）"]) + "\n"
        db = get_db()
    except Exception as exc:  # pragma: no cover
        return "\n".join(lines + [f"（無法連線 MongoDB：{exc}）"]) + "\n"
    registry = get_registry()
    sources = {s["_id"]: s for s in db.sources.find({})}
    raw_counts: Counter = Counter()
    for row in db.raw_documents.aggregate([{"$group": {"_id": {"s": "$source_id", "st": "$processing_status"}, "n": {"$sum": 1}}}]):
        raw_counts[(row["_id"]["s"], row["_id"]["st"])] = row["n"]
    benefit_counts = {r["_id"]: r["n"] for r in db.benefits.aggregate([{"$group": {"_id": "$source_id", "n": {"$sum": 1}}}])}
    statuses = ["new", "filtered_out", "extracted", "needs_review", "provider_data", "skipped", "error"]
    lines += ["| 來源 | raw_documents | " + " | ".join(statuses) + " | benefits |", "| --- | ---: | " + " | ".join("---:" for _ in statuses) + " | ---: |"]
    for sid, source in sorted(sources.items()):
        total = sum(c for (s, _), c in raw_counts.items() if s == sid)
        lines.append(f"| {source.get('name', sid)} | {total} | " + " | ".join(str(raw_counts[(sid, st)]) for st in statuses) + f" | {benefit_counts.get(sid, 0)} |")
    total = db.benefits.count_documents({})
    lines += ["", f"- benefits 總數：{total}（canonical {db.benefits.count_documents({'is_canonical': True})}；彙整頁 {db.benefits.count_documents({'is_overview': True})}）"]
    lines.append(f"- 有可判斷規則：{db.benefits.count_documents({'index.simple_rules': {'$gt': 0}})}；本地 AI 已補齊：{db.benefits.count_documents({'llm.processed': True})}；待人工確認：{db.benefits.count_documents({'review.needs_review': True})}")
    lines.append("- 領域：" + "、".join(f"{registry.domain_label(r['_id'])} {r['n']}" for r in db.benefits.aggregate([{"$group": {"_id": "$domain", "n": {"$sum": 1}}}])))
    lines.append("- 類別：" + "、".join(f"{registry.category_label(r['_id'])} {r['n']}" for r in sorted(db.benefits.aggregate([{"$group": {"_id": "$category", "n": {"$sum": 1}}}]), key=lambda r: -r["n"])))
    lines.append("- 給付形式：" + "、".join(f"{r['_id']} {r['n']}" for r in db.benefits.aggregate([{"$group": {"_id": "$benefit.benefit_form", "n": {"$sum": 1}}}])))
    rule_stats: Counter = Counter()
    complexity: Counter = Counter()
    extractors: Counter = Counter()
    for b in db.benefits.find({}, {"rules": 1}):
        for r in b.get("rules") or []:
            rule_stats[r.get("attribute_id")] += 1
            complexity[r.get("complexity")] += 1
            extractors[(r.get("evidence") or {}).get("extractor", "")] += 1
    lines.append(f"- 規則總數：{sum(complexity.values())}（simple {complexity['simple']}、complex {complexity['complex']}）；抽取方式：" + "、".join(f"{k or '—'} {v}" for k, v in extractors.items()))
    lines.append("- 規則最常用的屬性：" + "、".join(f"`{k}` {v}" for k, v in rule_stats.most_common(12)))
    accepted = rejected = 0
    for b in db.benefits.find({"llm.processed": True}, {"llm.accepted": 1, "llm.rejected": 1}):
        accepted += len((b.get("llm") or {}).get("accepted") or [])
        rejected += len((b.get("llm") or {}).get("rejected") or [])
    lines.append(f"- 本地 AI 補齊：接受 {accepted} 項、拒絕（驗證未通過）{rejected} 項")
    lines.append(f"- 服務提供者（providers）：{db.providers.count_documents({})} 筆；審核佇列（open）：{db.review_items.count_documents({'status': 'open'})}")
    keyword = db.keyword_stats.find_one({"_id": "latest"}) or {}
    if keyword:
        lines.append(f"- 關鍵字統計：{keyword.get('generated_at')}；語料 {keyword.get('corpus', {}).get('documents')} 份（標記 {keyword.get('corpus', {}).get('positives')}）；補助訊號詞 {keyword.get('benefit_terms')}、負面詞 {keyword.get('negative_terms')}、統計出關鍵字的類別 {keyword.get('categories_mined')}")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, builder in [("registry-attributes.md", registry_attributes), ("taxonomy.md", taxonomy), ("sources.md", sources_table), ("keyword-table.md", keyword_table), ("pipeline-stats.md", pipeline_stats)]:
        (OUT / name).write_text(builder(), encoding="utf-8")
        print(f"wrote docs/generated/{name}")


if __name__ == "__main__":
    main()
