"""獨立審核：用「另一個」本地模型（預設 qwen3:8b；5090 主機建議 qwen3:32b）逐筆核對補助方案的欄位是否有原文依據。

    python scripts/audit_with_llm.py --model qwen3:8b --limit 40 --out ../docs/generated/field-audit.md

每筆送給審核模型：原文（節錄）＋系統抽出的欄位（類別、機關、金額、申請期間、申請方式、前 8 條資格規則與摘錄）。
審核模型只回答每個欄位「correct / wrong / unverifiable」與一句理由；不會改資料。結果寫成 Markdown 報告與 JSON（可重現）。
審核模型的判斷也可能錯，報告只當作第二意見；wrong 的項目要回到原文人工確認。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_db  # noqa: E402
from app.llm.ollama_provider import OllamaProvider  # noqa: E402
from app.registry import get_registry  # noqa: E402

AUDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["correct", "wrong", "unverifiable"]},
        "category_note": {"type": "string"},
        "provider": {"type": "string", "enum": ["correct", "wrong", "unverifiable"]},
        "provider_note": {"type": "string"},
        "amount": {"type": "string", "enum": ["correct", "wrong", "unverifiable", "not_extracted"]},
        "amount_note": {"type": "string"},
        "period": {"type": "string", "enum": ["correct", "wrong", "unverifiable", "not_extracted"]},
        "period_note": {"type": "string"},
        "channel": {"type": "string", "enum": ["correct", "wrong", "unverifiable", "not_extracted"]},
        "channel_note": {"type": "string"},
        "rules": {"type": "array", "items": {"type": "object", "properties": {"index": {"type": "integer"}, "verdict": {"type": "string", "enum": ["correct", "wrong", "unverifiable"]}, "note": {"type": "string"}}, "required": ["index", "verdict", "note"]}},
        "missed_eligibility": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["category", "category_note", "provider", "provider_note", "amount", "amount_note", "period", "period_note", "channel", "channel_note", "rules", "missed_eligibility"],
}

SYSTEM = (
    "You are auditing structured data extracted from an official Taiwanese government benefit page. "
    "For each extracted field decide, using ONLY the original text: correct (the text supports exactly this value), "
    "wrong (the text contradicts it or the value belongs to something else, e.g. an income threshold recorded as a benefit amount), "
    "unverifiable (the text does not say), or not_extracted (the system left it empty). "
    "For each eligibility rule judge whether the rule faithfully represents the quoted sentence (operator, number, unit, who it applies to, required vs exclusion). "
    "List eligibility conditions clearly stated in the text that the system did not extract (verbatim short quotes). "
    "Be strict and concise. Notes in Traditional Chinese, one sentence. Return ONLY JSON."
)


def build_user(benefit: dict, registry) -> tuple[str, list[dict]]:
    meta = benefit.get("benefit") or {}
    amount = meta.get("amount") or {}
    period = meta.get("application_period") or {}
    application = meta.get("application") or {}
    rules = [r for r in (benefit.get("rules") or []) if r.get("role") != "bonus"][:8]
    rule_lines = []
    for i, r in enumerate(rules):
        ev = r.get("evidence") or {}
        rule_lines.append(f"{i}. {r.get('human_readable', '')}  [{r.get('attribute_id')} {r.get('operator')} {json.dumps(r.get('value'), ensure_ascii=False)}; role={r.get('role')}]\n   摘錄：{(ev.get('excerpt') or '')[:160]}")
    amount_desc = {k: amount.get(k) for k in ("type", "value", "min", "max", "period") if amount.get(k) not in (None, "", "unknown")}
    user = f"""標題：{benefit.get('title', '')}

系統抽出的欄位：
- 類別：{registry.category_label(benefit.get('category', ''))}（{benefit.get('category', '')}；領域 {benefit.get('domain', '')}）
- 主辦機關：{benefit.get('provider', '')}（{benefit.get('provider_type', '')}）
- 金額：{json.dumps(amount_desc, ensure_ascii=False) if amount_desc else '（未抽出）'}；tiers={[t.get('value') for t in amount.get('tiers') or []][:8]}
- 申請期間：start={period.get('start_date') or ''} end={period.get('end_date') or ''} rolling={period.get('rolling')}；{(period.get('description') or '')[:80]}
- 申請管道：{application.get('channel', '')}；{(application.get('method') or '')[:60]}
- 資格規則（前 {len(rules)} 條）：
{chr(10).join(rule_lines) if rule_lines else '（無）'}

原文（節錄）：
<<<
{(benefit.get('original_text') or '')[:6000]}
>>>

請輸出 JSON。"""
    return user, rules


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("AUDIT_MODEL", "qwen3:8b"))
    parser.add_argument("--base-url", default=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
    parser.add_argument("--limit", type=int, default=0, help="0 = 全部 canonical 補助方案")
    parser.add_argument("--domain", default="")
    parser.add_argument("--out", default=str(Path(__file__).resolve().parents[2] / "docs" / "generated" / "field-audit.md"))
    parser.add_argument("--json", default=str(Path(__file__).resolve().parents[2] / "docs" / "generated" / "field-audit.json"))
    args = parser.parse_args()

    db = get_db()
    registry = get_registry()
    provider = OllamaProvider(args.model, base_url=args.base_url, timeout=600)
    query: dict = {"record_kind": "program", "is_canonical": True}
    if args.domain:
        query["domain"] = args.domain
    cursor = db.benefits.find(query).sort("domain", 1)
    if args.limit:
        cursor = cursor.limit(args.limit)
    rows = list(cursor)
    results = []
    started = time.time()
    for n, b in enumerate(rows, 1):
        user, rules = build_user(b, registry)
        t = time.time()
        try:
            out = provider.complete_json(SYSTEM, user, json_schema=AUDIT_SCHEMA, max_tokens=900)
        except Exception as exc:  # 單筆失敗不中斷
            out = {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
        rule_verdicts = []
        for rv in (out.get("rules") or []) if isinstance(out, dict) else []:
            idx = rv.get("index")
            if isinstance(idx, int) and 0 <= idx < len(rules):
                rule_verdicts.append({"index": idx, "human_readable": rules[idx].get("human_readable", ""), "attribute_id": rules[idx].get("attribute_id"), "verdict": rv.get("verdict"), "note": rv.get("note", "")})
        results.append({"benefit_id": b["_id"], "title": b.get("title", ""), "domain": b.get("domain", ""), "category": b.get("category", ""), "source_url": (b.get("source") or {}).get("source_url", ""), "seconds": round(time.time() - t, 1), "audit": {k: v for k, v in out.items() if k != "rules"}, "rule_verdicts": rule_verdicts, "rules_total": len(b.get("rules") or [])})
        print(f"[{n}/{len(rows)}] {b.get('title', '')[:30]} {round(time.time() - t, 1)}s", flush=True)

    # ---- summary
    fields = ["category", "provider", "amount", "period", "channel"]
    counts = {f: Counter(r["audit"].get(f, "error") for r in results) for f in fields}
    rule_counts = Counter(v["verdict"] for r in results for v in r["rule_verdicts"])
    missed = sum(1 for r in results if r["audit"].get("missed_eligibility"))
    generated = datetime.now(timezone.utc).isoformat()
    lines = [f"# 欄位審核（第二模型獨立核對）", "", f"- 審核模型：`{args.model}`（{args.base_url}）；產生於 {generated}", f"- 審核筆數：{len(results)} 筆 canonical 補助方案；平均每筆 {round((time.time() - started) / max(1, len(results)), 1)} 秒", "",
             "審核模型只用原文判斷：correct＝原文支持這個值；wrong＝原文矛盾或值屬於別的東西（例如把所得門檻當金額）；unverifiable＝原文沒寫；not_extracted＝系統留空。", "審核模型本身也可能誤判，wrong 的項目請回到原文確認後再修規則。", "", "## 1. 各欄位", "", "| 欄位 | correct | wrong | unverifiable | not_extracted | 正確率（排除未抽出） |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for f in fields:
        c = counts[f]
        judged = c["correct"] + c["wrong"] + c["unverifiable"]
        acc = f"{100 * c['correct'] / judged:.0f}%" if judged else "—"
        lines.append(f"| {f} | {c['correct']} | {c['wrong']} | {c['unverifiable']} | {c.get('not_extracted', 0)} | {acc} |")
    judged_rules = rule_counts["correct"] + rule_counts["wrong"] + rule_counts["unverifiable"]
    lines += ["", "## 2. 資格規則（每筆最多前 8 條）", "", f"- 審核規則數：{judged_rules}；correct {rule_counts['correct']}、wrong {rule_counts['wrong']}、unverifiable {rule_counts['unverifiable']}；正確率 {100 * rule_counts['correct'] / judged_rules:.0f}%" if judged_rules else "- 沒有規則可審", f"- 審核模型認為原文還有未抽出的資格條件：{missed} 筆", "", "## 3. 被判 wrong 的項目（請人工回原文確認）", ""]
    for r in results:
        wrong_fields = [f for f in fields if r["audit"].get(f) == "wrong"]
        wrong_rules = [v for v in r["rule_verdicts"] if v["verdict"] == "wrong"]
        if not wrong_fields and not wrong_rules:
            continue
        lines.append(f"### {r['title'][:60]}（{r['domain']}／{r['category']}）")
        lines.append(f"- 來源：{r['source_url']}")
        for f in wrong_fields:
            lines.append(f"- **{f}**：{r['audit'].get(f + '_note', '')}")
        for v in wrong_rules:
            lines.append(f"- **規則** {v['human_readable']}（{v['attribute_id']}）：{v['note']}")
        lines.append("")
    lines += ["## 4. 審核模型認為漏抽的資格條件（節錄）", ""]
    for r in results:
        m = r["audit"].get("missed_eligibility") or []
        if m:
            lines.append(f"- {r['title'][:40]}：" + "；".join(str(x)[:80] for x in m[:3]))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path(args.json).write_text(json.dumps({"model": args.model, "generated_at": generated, "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
