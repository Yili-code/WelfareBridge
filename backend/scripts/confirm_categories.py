"""用指定的本地模型逐筆確認 canonical 補助方案的類別，只在「有獨立佐證」時才改：

    python scripts/confirm_categories.py --model qwen3:8b [--min-confidence 0.8] [--dry-run]
    python scripts/confirm_categories.py --revert-unsupported      # 把之前沒有佐證的變更改回去（依 category_history）

改類別的條件（三者缺一不可）：
1. 新類別是登錄表的葉節點（不能是領域 id）；
2. 模型信心 >= 門檻；
3. 有獨立佐證：pipeline 先前的 AI 判定（另一個模型）也是同一類別，或標題／內文前 300 字符合新類別的特徵字（CATEGORY_HINTS）。
小模型的信心值幾乎都是 0.95，不能單獨當依據；沒有佐證的變更只記錄在 category_history（applied=false）供人工檢視。
每次變更都寫進 benefits.classification.llm 與 category_history，可追溯、可回復。
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import get_db, utcnow  # noqa: E402
from app.registry import get_registry  # noqa: E402

CATEGORY_HINTS = {
    "scholarship": r"(獎學金|獎助學金|獎助金)",
    "student_aid": r"(助學金|助學計畫|弱勢助學)",
    "education_subsidy": r"(就學補助|教育補助|就學.{0,4}補助|學費補助|補助費)",
    "tuition_waiver": r"(學雜費|減免|免學費)",
    "emergency_aid_student": r"(?=.*(學生|就學|學校|助學))(?=.*(急難|慰問|賑災|災害|災))",  # 學生急難：學生字眼與急難字眼都要有
    "emergency_relief": r"(急難|救助|紓困|慰問)",
    "study_abroad": r"(海外|留學|國外|出國)",
    "rental_subsidy": r"(租金|租屋|租賃)",
    "housing_loan_subsidy": r"(貸款|利息|房貸|購屋)",
    "housing_support": r"(住宅|房屋|修繕|補強|居住)",
    "social_housing": r"(社會住宅|社宅)",
    "unemployment_benefit": r"(失業給付|失業)",
    "employment_incentive": r"(就業|津貼|獎勵|工作|僱用)",
    "youth_employment": r"(青年|少年)",
    "training_allowance": r"(訓練|職訓|充電)",
    "employer_subsidy": r"(雇主|事業單位)",
    "elderly_allowance": r"(老人|長者|銀髮|高齡|敬老)",
    "elderly_service": r"(老人|長者|銀髮|樂齡)",
    "ltc_general": r"(長照|長期照顧)",
    "home_care": r"(居家)",
    "day_care": r"(日間照顧|日照)",
    "respite_care": r"(喘息)",
    "transport_service": r"(交通|接送)",
    "assistive_device": r"(輔具|無障礙)",
    "meal_service": r"(餐飲|送餐|營養)",
    "institutional_care_subsidy": r"(機構|安置|住宿)",
    "family_care_home": r"(托顧)",
    "child_allowance": r"(育兒|幼兒|兒童)",
    "childcare_subsidy": r"(托育|準公共)",
    "parental_leave_allowance": r"(育嬰|留職停薪)",
    "disability_living_allowance": r"(身心障礙|身障)",
    "disability_care_subsidy": r"(身心障礙|身障)",
    "disability_other": r"(身心障礙|身障)",
    "low_income_allowance": r"(低收|中低收|弱勢|生活補助|生活扶助)",
    "medical_subsidy": r"(醫療|健保|假牙|就醫)",
    "worker_welfare": r"(勞工|職工)",
}


def supported(new_cat: str, benefit: dict, previous_ai_category: str) -> tuple[bool, str]:
    registry = get_registry()
    leaf = registry.category(new_cat)
    if leaf is None or new_cat not in {x.id for x in registry.leaves()}:
        return False, "不是葉節點類別"
    if previous_ai_category and previous_ai_category == new_cat:
        return True, "另一個模型先前判定一致"
    hint = CATEGORY_HINTS.get(new_cat)
    text = (benefit.get("title") or "") + "\n" + (benefit.get("original_text") or "")[:300]
    if hint and re.search(hint, text, re.S):
        return True, f"標題／內文含特徵字 {hint}"
    return False, "沒有獨立佐證（另一模型不一致、標題與內文也沒有該類別特徵字）"


def apply_change(db, benefit: dict, new_cat: str, verdict: dict, basis: str, applied: bool) -> None:
    registry = get_registry()
    history = {"from": benefit.get("category"), "to": new_cat, "model": verdict.get("model"), "confidence": verdict.get("confidence"), "reason": verdict.get("reason", ""), "basis": basis, "applied": applied, "at": utcnow()}
    update: dict = {"$push": {"category_history": history}}
    if applied:
        domain = registry.domain_of(new_cat)
        update["$set"] = {"category": new_cat, "domain": domain, "category_label": registry.category_label(new_cat), "classification.llm": verdict, "classification.category": new_cat, "classification.domain": domain, "classification.method": "keyword+llm", "updated_at": utcnow()}
    db.benefits.update_one({"_id": benefit["_id"]}, update)
    if applied and benefit.get("raw_document_id"):
        db.raw_documents.update_one({"_id": benefit["raw_document_id"]}, {"$set": {"classification.llm": verdict, "classification.category": new_cat, "classification.domain": registry.domain_of(new_cat)}})


def revert_unsupported(db) -> int:
    """依 category_history 檢查每筆最後一次已套用的變更；沒有佐證的改回原值。"""
    registry = get_registry()
    reverted = 0
    for b in db.benefits.find({"category_history.0": {"$exists": True}}, {"title": 1, "original_text": 1, "category": 1, "category_history": 1, "classification": 1, "raw_document_id": 1}):
        applied = [h for h in b.get("category_history") or [] if h.get("applied", True) and h.get("model") != "revert"]  # 撤銷紀錄本身不算變更
        if not applied:
            continue
        last = applied[-1]
        if last.get("to") != b.get("category"):
            continue
        prev_ai = ""  # 先前 pipeline 的 AI 判定已被覆寫，只能用特徵字佐證
        ok, basis = supported(last["to"], b, prev_ai)
        if ok:
            continue
        old = last.get("from") or ""
        if not old or registry.category(old) is None:
            continue
        domain = registry.domain_of(old)
        db.benefits.update_one({"_id": b["_id"]}, {"$set": {"category": old, "domain": domain, "category_label": registry.category_label(old), "classification.category": old, "classification.domain": domain, "updated_at": utcnow()}, "$push": {"category_history": {"from": last["to"], "to": old, "model": "revert", "basis": "撤銷：" + basis, "applied": True, "at": utcnow()}}})
        if b.get("raw_document_id"):
            db.raw_documents.update_one({"_id": b["raw_document_id"]}, {"$set": {"classification.category": old, "classification.domain": domain}})
        print(f"revert {b.get('title', '')[:32]}: {last['to']} -> {old} ({basis})")
        reverted += 1
    return reverted


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=os.environ.get("AUDIT_MODEL", "qwen3:8b"))
    parser.add_argument("--min-confidence", type=float, default=0.8)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--revert-unsupported", action="store_true")
    args = parser.parse_args()
    db = get_db()
    if args.revert_unsupported:
        print("reverted:", revert_unsupported(db))
        return 0
    os.environ["LLM_MODEL"] = args.model
    from app.config import get_settings

    get_settings.cache_clear()
    from app.llm import fill

    registry = get_registry()
    cursor = db.benefits.find({"record_kind": "program", "is_canonical": True}, {"title": 1, "original_text": 1, "category": 1, "classification": 1, "raw_document_id": 1})
    if args.limit:
        cursor = cursor.limit(args.limit)
    rows = list(cursor)
    changed = unsupported = 0
    started = time.time()
    for n, b in enumerate(rows, 1):
        candidates = list(((b.get("classification") or {}).get("category_scores") or {}).keys())[:6] or [b.get("category")]
        prev_ai = (((b.get("classification") or {}).get("llm")) or {}).get("category") or ""
        t = time.time()
        try:
            verdict = fill.classify_document(b.get("title", ""), b.get("original_text", ""), [c for c in candidates if c])
        except Exception as exc:
            print(f"[{n}/{len(rows)}] {b.get('title', '')[:30]} error {exc}")
            continue
        new_cat = (verdict or {}).get("category") or ""
        conf = float((verdict or {}).get("confidence") or 0)
        if not new_cat or new_cat == b.get("category"):
            print(f"[{n}/{len(rows)}] {b.get('title', '')[:30]} | {b.get('category')} = ({conf:.2f}, {round(time.time() - t, 1)}s)")
            continue
        ok, basis = supported(new_cat, b, prev_ai) if conf >= args.min_confidence else (False, f"信心 {conf:.2f} 低於門檻")
        mark = "->" if ok else "?"
        print(f"[{n}/{len(rows)}] {b.get('title', '')[:30]} | {b.get('category')} {mark} {new_cat} ({conf:.2f}) {basis}")
        if not args.dry_run:
            apply_change(db, b, new_cat, verdict, basis, ok)
        changed += int(ok)
        unsupported += int(not ok)
    print(f"done: {len(rows)} checked, {changed} applied, {unsupported} unsupported (recorded only), {round(time.time() - started)}s, model={args.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
