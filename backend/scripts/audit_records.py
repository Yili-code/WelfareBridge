"""規則式全庫稽核：對每一筆補助紀錄做確定性檢查（不呼叫 LLM），列出可疑之處給人／代理逐筆判讀。

檢查項目（每項都只看原文與登錄表，不猜）：
  摘錄類   evidence / rules[].evidence / documents / obligations / target_population 的摘錄是否逐字出現在原文
  金額類   金額數字是否出現在原文、是否其實是收入或財產門檻、同一頁是否有多個年度版本的金額
  類別類   標題關鍵字與主類別是否衝突、是否已標類別待確認
  機關類   提供機關是否為科室名／電話／空白、provider_type 與機關名是否相符、地區是否與機關衝突
  期間類   狀態與截止日是否矛盾、rolling 與截止日是否並存、起迄日是否顛倒
  結構類   收錄政策是否已改判為排除、是否沒有任何可判斷的資格規則、完整度與品質等級是否相符
  邏輯類   必要條件是否互斥（同時要是低收與中低收、同時年滿65與55）而永遠比對不上
  綱要類   schema_validator.validate_benefit 是否通過、去重後是否仍有同名同機關的重複紀錄

用法：
  python scripts/audit_records.py                       # 全部 canonical program
  python scripts/audit_records.py --all-records         # 連非 canonical 與彙整頁一起查
  python scripts/audit_records.py --out docs/generated/record-audit
輸出：<out>.json（每筆的 flags）與 <out>.md（統計與清單）
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db  # noqa: E402
from app.registry import get_registry  # noqa: E402
from app.services import admission  # noqa: E402
from app.services.extractor import _is_threshold_clause, is_division_name, is_real_condition, placeholder_attribute  # noqa: E402
from app.services.extractor import _conflicting_groups  # noqa: E402
from app.services.normalization import chinese_to_int, find_cities, parse_amounts, taiwan_today  # noqa: E402
from app.services.schema_validator import excerpt_in_text, validate_benefit  # noqa: E402

# 標題關鍵字 → 應該落在哪個主類別（只放語意非常明確的詞；用來抓「標題與類別衝突」）
TITLE_CATEGORY_HINTS: list[tuple[str, set[str]]] = [
    (r"生育(津貼|獎勵|補助|給付)|新生兒|產婦|坐月子|好孕", {"birth_incentive", "medical_subsidy", "low_income_allowance", "special_circumstances_aid"}),
    (r"育兒津貼", {"child_allowance"}),
    (r"托育|托嬰|保母|居家式托育", {"childcare_subsidy", "child_allowance", "disability_care_subsidy", "special_circumstances_aid", "low_income_allowance"}),
    (r"育嬰留職停薪", {"parental_leave_allowance"}),
    (r"低收入戶|中低收入戶(?!老人)", {"low_income_allowance", "medical_subsidy", "insurance_premium_subsidy", "education_subsidy", "student_aid", "rental_subsidy", "emergency_relief", "childcare_subsidy", "child_allowance", "birth_incentive", "housing_support", "elderly_allowance", "assistive_device", "special_circumstances_aid", "scholarship", "tuition_waiver", "elderly_service", "institutional_care_subsidy", "disability_living_allowance"}),
    (r"急難救助|急難紓困|馬上關懷|災害救助", {"emergency_relief", "special_circumstances_aid", "low_income_allowance", "medical_subsidy"}),
    (r"特殊境遇", {"special_circumstances_aid", "emergency_relief", "education_subsidy", "childcare_subsidy", "medical_subsidy", "student_aid"}),
    (r"假牙|老花眼鏡|助聽器", {"elderly_allowance", "elderly_service", "medical_subsidy", "assistive_device", "disability_assistive_device", "disability_other", "disability_care_subsidy", "low_income_allowance"}),
    (r"重陽|敬老(禮金|金)|人瑞", {"elderly_allowance", "elderly_service"}),
    (r"慰問金", {"emergency_relief", "low_income_allowance", "medical_subsidy", "special_circumstances_aid", "elderly_allowance", "disability_other", "disability_living_allowance", "worker_welfare"}),
    (r"老人生活津貼|特別照顧津貼", {"elderly_allowance"}),
    (r"輔具", {"assistive_device", "disability_assistive_device", "disability_other", "elderly_service"}),
    (r"日間照顧|日照", {"day_care", "elderly_service", "disability_care_subsidy", "ltc_general"}),
    (r"家庭托顧", {"family_care_home", "ltc_general", "elderly_service"}),
    (r"居家服務", {"home_care", "ltc_general", "elderly_service", "disability_care_subsidy"}),
    (r"喘息", {"respite_care", "ltc_general"}),
    (r"交通接送|復康巴士", {"transport_service", "ltc_general", "disability_other", "elderly_service"}),
    (r"送餐|營養餐飲|老人共餐", {"meal_service", "elderly_service"}),
    (r"機構(安置|收容|住宿)|養護|住宿式", {"institutional_care_subsidy", "disability_care_subsidy", "elderly_service", "ltc_general"}),
    (r"身心障礙者?生活補助", {"disability_living_allowance"}),
    (r"租金(補貼|補助)|包租代管", {"rental_subsidy", "social_housing", "housing_support", "disability_other", "low_income_allowance"}),
    (r"社會住宅", {"social_housing", "rental_subsidy"}),
    (r"房貸|購屋|貸款利息", {"housing_loan_subsidy", "housing_support", "disability_other", "social_housing", "rental_subsidy"}),
    (r"修繕|住宅改善|無障礙環境改善", {"housing_support", "housing_loan_subsidy", "elderly_service", "elderly_allowance", "disability_other", "assistive_device", "low_income_allowance", "social_housing"}),
    (r"獎學金", {"scholarship", "student_aid", "education_subsidy", "study_abroad"}),
    (r"助學金", {"student_aid", "scholarship", "education_subsidy"}),
    (r"學雜費減免|學費減免", {"tuition_waiver", "education_subsidy"}),
    (r"就學補助|就學生活補助|教育補助", {"education_subsidy", "student_aid", "low_income_allowance", "tuition_waiver", "scholarship"}),
    (r"失業給付", {"unemployment_benefit"}),
    (r"職業訓練生活津貼|職訓津貼", {"training_allowance"}),
    (r"(就業|僱用|雇用)獎助|就業獎勵|臨時工作津貼|求職交通", {"employment_incentive", "employer_subsidy", "youth_employment", "training_allowance"}),
    (r"健保(費)?(自付額)?補助|全民健康保險.*補助|國民年金.*保險費", {"insurance_premium_subsidy", "medical_subsidy", "elderly_allowance", "low_income_allowance", "disability_other"}),
    (r"醫療補助|看護費", {"medical_subsidy", "low_income_allowance", "elderly_allowance", "disability_care_subsidy"}),
]
ROC_YEAR_RE = re.compile(r"(?:民國)?\s*([一二三四五六七八九十百零\d]{2,4})\s*年")
CONTACT_JUNK_RE = re.compile(r"(電話|傳真|地址|信箱|分機|聯絡|洽詢|窗口|承辦)")
THRESHOLD_SPLIT_RE = re.compile("[，。；：、" + chr(10) + "]")


def roc_years(text: str) -> set[int]:
    years = set()
    for raw in ROC_YEAR_RE.findall(text or ""):
        value = int(raw) if raw.isdigit() else (chinese_to_int(raw) or 0)
        if 100 <= value <= 130:
            years.add(value)
    return years


def amount_numbers(amount: dict) -> list[float]:
    values = [amount.get("value"), amount.get("min"), amount.get("max")]
    values += [tier.get("value") for tier in (amount.get("tiers") or [])]
    return [float(v) for v in values if isinstance(v, (int, float))]


def audit_record(row: dict, registry, dup_keys: Counter, today: str) -> list[dict]:
    flags: list[dict] = []

    def flag(code: str, detail: str, field: str = "") -> None:
        flags.append({"code": code, "field": field, "detail": detail[:400]})

    text = row.get("original_text") or ""
    title = row.get("title") or ""
    meta = row.get("benefit") or {}
    amount = meta.get("amount") or {}
    period = meta.get("application_period") or {}
    application = meta.get("application") or {}

    # ---------------- 摘錄逐字
    for ev in row.get("evidence") or []:
        excerpt = (ev.get("excerpt") or "").strip()
        if not excerpt or ev.get("inferred"):
            continue
        if excerpt.startswith("機關單位名稱：") or excerpt.startswith("發布單位："):
            continue  # 由來源登錄組出來的欄位，不是原文句子
        if not excerpt_in_text(excerpt, text):
            flag("evidence_not_verbatim", f"{ev.get('field')}：{excerpt}", ev.get("field", ""))
    for rule in row.get("rules") or []:
        excerpt = ((rule.get("evidence") or {}).get("excerpt") or "").strip()
        if excerpt and not excerpt_in_text(excerpt, text):
            flag("rule_excerpt_not_verbatim", f"{rule.get('attribute_id')}：{excerpt}", rule.get("attribute_id", ""))
    for doc in application.get("documents") or []:
        if doc and not excerpt_in_text(doc, text):
            flag("document_not_in_text", doc, "benefit.application.documents")
    ai_fields = {a.get("field") for a in ((row.get("llm") or {}).get("accepted") or []) if a.get("field")}

    def check_derived(value: str, field: str) -> None:
        """本地 AI 寫的敘述允許改寫，但裡面的數字與縣市必須出自原文（抓造假，不抓改寫）。"""
        if not value:
            return
        if excerpt_in_text(value, text):
            return
        text_numbers = set(re.findall(r"\d+", text.replace(",", "")))
        for number in re.findall(r"\d+", value.replace(",", "")):
            if number not in text_numbers and len(number) >= 2:
                flag("derived_number_not_in_text", f"{field}：「{value}」中的 {number} 不在原文", field)
                break
        for city in find_cities(value):
            if city not in text and city.replace("臺", "台") not in text and city.replace("台", "臺") not in text:
                flag("derived_city_not_in_text", f"{field}：「{value}」提到 {city}，原文沒有", field)
                break

    for ob in meta.get("obligations") or []:
        if "benefit.obligations" in ai_fields or not excerpt_in_text(ob, text):
            check_derived(ob, "benefit.obligations")
        if ob and "benefit.obligations" not in ai_fields and not excerpt_in_text(ob, text):
            flag("obligation_not_in_text", ob, "benefit.obligations")
    target = meta.get("target_population_text") or ""
    if target:
        if "benefit.target_population_text" in ai_fields or not excerpt_in_text(target, text):
            check_derived(target, "benefit.target_population_text")
        elif not excerpt_in_text(target, text):
            flag("target_population_not_in_text", target, "benefit.target_population_text")
    method = application.get("method") or ""
    if method and not excerpt_in_text(method, text):
        check_derived(method, "benefit.application.method")
        if "benefit.application.method" not in ai_fields:
            flag("method_not_in_text", method, "benefit.application.method")

    # ---------------- 金額
    # 原文裡「看得到的數字」：金額寫法 + 區間端點 + 表格裡沒有「元」的純數字
    text_amounts = set(parse_amounts(text))
    compact_text = re.sub(r"[,\s]", "", text)
    for raw in re.findall(r"[0-9]{2,9}", compact_text):
        text_amounts.add(int(raw))
    for value in amount_numbers(amount):
        if value and float(value).is_integer() and int(value) not in text_amounts:
            flag("amount_not_in_text", f"{int(value)} 不在原文可解析的金額中（原文金額：{sorted(text_amounts)[:12]}）", "benefit.amount")
    description = amount.get("description") or ""
    if description:
        # 只有「整段敘述都是門檻、沒有任何給付語氣」才算抓錯；
        # 「自行負擔超過3萬元之部分，最高補助70%」是正常的給付規則
        clauses = [c for c in THRESHOLD_SPLIT_RE.split(description) if re.search(r"[0-9０-９一二三四五六七八九十百千萬]", c)]
        if clauses and all(_is_threshold_clause(c) for c in clauses):
            flag("amount_is_threshold", description, "benefit.amount.description")
    if description:
        # 「112年4月1日以後所生」是生效日不是版本年，扣掉再比
        effective = re.sub(r"(民國)?[0-9０-９一二三四五六七八九十百]{1,4}\s*年[^，。；]{0,12}?(以後|起|之後|以降)", "", description)
        desc_years = roc_years(effective)
        other_years = roc_years(target) | roc_years(title)
        if desc_years and other_years and max(other_years) > max(desc_years):
            flag("amount_older_version", f"金額摘錄是民國 {sorted(desc_years)} 年的版本，資格／標題提到民國 {sorted(other_years)} 年", "benefit.amount")
    if (meta.get("benefit_form") == "cash") and not amount_numbers(amount) and not description:
        flag("cash_without_amount", "給付形式是現金但沒有任何金額", "benefit.amount")

    # ---------------- 類別
    category = row.get("category") or ""
    node = registry.category(category) if category else None
    if not category:
        flag("category_missing", "沒有主類別", "category")
    elif node is None:
        flag("category_not_in_registry", category, "category")
    if (row.get("category_label") or "") and node is not None and row["category_label"] != node.label:
        flag("category_label_mismatch", f"{row['category_label']} vs 登錄表 {node.label}", "category_label")
    if node is not None and row.get("domain") and registry.domain_of(category) != row.get("domain"):
        flag("domain_mismatch", f"{row.get('domain')} vs 登錄表 {registry.domain_of(category)}", "domain")
    secondary = set(row.get("categories_secondary") or [])
    for pattern, expected in TITLE_CATEGORY_HINTS:
        if re.search(pattern, title):
            if category and category not in expected and not (secondary & expected):
                flag("category_title_conflict", f"標題含「{re.search(pattern, title).group(0)}」，預期 {sorted(expected)[:6]}，實際 {category}", "category")
            break
    classification = row.get("classification") or {}
    if classification.get("category_uncertain"):
        flag("category_uncertain", classification.get("decision_basis") or "", "category")
    if classification.get("uncertain"):
        flag("gate_uncertain", classification.get("decision_basis") or "", "classification")

    # ---------------- 機關與地區
    provider = (row.get("provider") or "").strip()
    if not provider:
        flag("provider_missing", "沒有主辦機關", "provider")
    else:
        if is_division_name(provider):
            flag("provider_is_division", provider, "provider")
        if CONTACT_JUNK_RE.search(provider):
            flag("provider_looks_like_contact", provider, "provider")
        ptype = row.get("provider_type") or ""
        if re.search(r"(市政府|縣政府|市立|縣立)", provider) and ptype not in {"local_government", "school"}:
            flag("provider_type_mismatch", f"{provider} / {ptype}", "provider_type")
        if re.search(r"(區公所|鄉公所|鎮公所|市公所)", provider) and ptype != "township":
            flag("provider_type_mismatch", f"{provider} / {ptype}", "provider_type")
        if re.match(r"^(衛生福利部|勞動部|教育部|內政部|原住民族委員會|客家委員會|國軍退除役官兵輔導委員會|財政部|經濟部)", provider) and ptype != "central_government":
            flag("provider_type_mismatch", f"{provider} / {ptype}", "provider_type")
        cities = find_cities(provider)
        region = row.get("provider_region") or ""
        if cities and region and region != "national" and region not in cities:
            flag("region_mismatch", f"provider_region={region} / 機關 {provider}", "provider_region")
        if cities and not region:
            flag("region_missing", f"機關是 {provider} 但沒有 provider_region", "provider_region")
    for rule in row.get("rules") or []:
        attribute = rule.get("attribute_id") or ""
        operator = rule.get("operator") or ""
        value = rule.get("value")
        excerpt = ((rule.get("evidence") or {}).get("excerpt") or "").strip()
        if operator == "exists":
            # 佔位規則（條件太複雜無法量化）：摘錄要真的是條件，屬性也要真的被摘錄提到
            if not is_real_condition(excerpt):
                flag("placeholder_rule_junk_excerpt", f"{attribute or '(空)'} exists ← 「{excerpt}」", attribute)
            elif attribute and placeholder_attribute(registry, [attribute], excerpt) != attribute:
                flag("placeholder_attribute_unsupported", f"{attribute} exists ← 「{excerpt}」（摘錄沒提到這個屬性）", attribute)
        elif value is None or (isinstance(value, list) and not value) or value == "":
            flag("rule_value_missing", f"{attribute} {operator} 沒有值", attribute)
        if attribute in {"residence.household_city", "residence.current_city"} and operator != "exists":
            values = value if isinstance(value, list) else [value]
            values = [v for v in values if v]
            cities = find_cities(provider) + find_cities(title)
            if cities and values and not (set(values) & set(cities)):
                flag("rule_city_conflict", f"規則城市 {values} 與機關／標題 {cities} 不同", attribute)
        if isinstance(value, (int, float)) and attribute.startswith(("household.income", "household.assets", "household.income_year")) and value >= 1000:
            if int(value) not in set(parse_amounts(text)) and str(int(value)) not in text.replace(",", ""):
                flag("rule_number_not_in_text", f"{attribute} {operator} {int(value)} 不在原文", attribute)

    # ---------------- 期間與狀態
    start, end = period.get("start_date") or "", period.get("end_date") or ""
    if end and start and start > end:
        flag("period_reversed", f"{start} → {end}", "benefit.application_period")
    if end and end < today and row.get("status") != "expired":
        flag("status_should_be_expired", f"截止日 {end} 已過但 status={row.get('status')}", "status")
    if row.get("status") == "expired" and not end and "已不再受理" not in title and not re.search(r"已停辦|停辦|額度已用罄|已停止受理|停止受理|停止新增|不再新增|不再受理|終止辦理", text):
        flag("expired_without_reason", "status=expired 但原文沒有停辦字眼也沒有截止日", "status")
    period_note = (period.get("description") or "") + " " + text[:2000]
    if period.get("rolling") and end and not re.search(r"隨到隨辦|隨時受理|全年受理|隨時提出|常年受理", period_note):
        flag("rolling_with_end_date", f"rolling=True 但有截止日 {end}", "benefit.application_period")

    # ---------------- 結構與綱要
    kind, reason = admission.page_kind(title, text, (row.get("source") or {}).get("source_url", ""))
    if kind in admission.EXCLUDED_KINDS:
        flag("admission_drift", f"收錄政策現在判為 {kind}：{reason}", "record_kind")
    elif kind == "portal" and row.get("record_kind") != "portal":
        flag("should_be_portal", reason, "record_kind")
    simple_rules = [r for r in (row.get("rules") or []) if r.get("complexity") == "simple"]
    if not simple_rules and not row.get("is_overview"):
        flag("no_simple_rules", "沒有任何可直接判斷的資格規則（媒合時只能歸為資料不足）", "rules")
    by_attribute: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for rule in simple_rules:
        if rule.get("role") == "required":
            by_attribute[rule.get("attribute_id", "")][rule.get("group_id", "")].append(rule)
    for attribute_id, rules_by_group in by_attribute.items():
        for left, right in _conflicting_groups(attribute_id, rules_by_group):
            left_values = [r.get("value") for r in rules_by_group[left]]
            right_values = [r.get("value") for r in rules_by_group[right]]
            flag("rules_unsatisfiable", f"{attribute_id} 同時必須 {left_values} 與 {right_values}，永遠比對不上", attribute_id)
    completeness = (row.get("admission") or {}).get("completeness") or {}
    tier = (row.get("admission") or {}).get("quality_tier")
    missing = set(completeness.get("missing") or [])
    if tier == "verified" and (missing & {"name", "agency", "eligibility", "amount"}):
        flag("tier_conflict", f"quality_tier=verified 但缺 {sorted(missing)}", "admission.quality_tier")
    outcome = validate_benefit(json.loads(json.dumps(row, default=str)), text)
    if not outcome.ok:
        flag("schema_invalid", "; ".join(outcome.errors)[:300], "schema")
    elif outcome.dropped:
        flag("schema_dropped_fields", "驗證時移除：" + "; ".join(outcome.dropped)[:300], "schema")
    if dup_keys[(title.strip(), provider)] > 1:
        flag("duplicate_canonical", f"同名同機關的代表紀錄有 {dup_keys[(title.strip(), provider)]} 筆", "dedup")
    if len(text) < 200:
        flag("text_too_short", f"原文只有 {len(text)} 字，難以判斷", "original_text")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/generated/record-audit")
    ap.add_argument("--all-records", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    db = get_db()
    registry = get_registry()
    today = taiwan_today().isoformat()
    query = {} if args.all_records else {"is_canonical": True, "record_kind": "program"}
    rows = list(db.benefits.find(query))
    if args.limit:
        rows = rows[: args.limit]
    dup_keys = Counter(((r.get("title") or "").strip(), (r.get("provider") or "").strip()) for r in rows)

    results = []
    counts = Counter()
    by_source = defaultdict(Counter)
    for row in rows:
        flags = audit_record(row, registry, dup_keys, today)
        for f in flags:
            counts[f["code"]] += 1
            by_source[row.get("source_id")][f["code"]] += 1
        results.append({
            "id": row["_id"], "title": row.get("title", ""), "source_id": row.get("source_id"),
            "category": row.get("category", ""), "provider": row.get("provider", ""),
            "quality_tier": (row.get("admission") or {}).get("quality_tier"),
            "flags": flags,
        })
    clean = sum(1 for r in results if not r["flags"])
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_base = args.out if os.path.isabs(args.out) else os.path.join(os.path.dirname(root), args.out)
    os.makedirs(os.path.dirname(out_base), exist_ok=True)
    io.open(out_base + ".json", "w", encoding="utf-8").write(json.dumps({"total": len(results), "clean": clean, "counts": dict(counts), "records": results}, ensure_ascii=False, indent=1))

    lines = [f"# 紀錄稽核（規則式，{len(results)} 筆）", "", f"- 乾淨（沒有任何旗標）：{clean}（{clean / max(len(results), 1):.1%}）", "", "## 旗標統計", "", "| 旗標 | 筆數 | 說明 |", "| --- | ---: | --- |"]
    labels = {
        "evidence_not_verbatim": "證據摘錄不是原文逐字", "rule_excerpt_not_verbatim": "資格規則的摘錄不是原文逐字",
        "document_not_in_text": "應備文件不在原文", "obligation_not_in_text": "義務條款不在原文",
        "target_population_not_in_text": "適用對象敘述不在原文", "method_not_in_text": "申請方式敘述不在原文",
        "amount_not_in_text": "金額數字不在原文", "amount_is_threshold": "金額其實是收入／財產門檻",
        "amount_older_version": "金額是舊年度版本", "cash_without_amount": "現金給付但沒有金額",
        "category_missing": "沒有主類別", "category_not_in_registry": "主類別不在登錄表",
        "category_label_mismatch": "類別標籤與登錄表不符", "domain_mismatch": "領域與登錄表不符",
        "category_title_conflict": "標題與主類別衝突", "category_uncertain": "類別三方不一致（待確認）",
        "gate_uncertain": "是否補助三方不一致（待確認）", "provider_missing": "沒有主辦機關",
        "provider_is_division": "主辦機關是科室名", "provider_looks_like_contact": "主辦機關像聯絡資訊",
        "provider_type_mismatch": "機關類型與機關名不符", "region_mismatch": "地區與機關不符", "region_missing": "缺地區",
        "rule_city_conflict": "規則城市與機關不符", "period_reversed": "起迄日顛倒",
        "status_should_be_expired": "截止日已過但狀態仍為受理中", "expired_without_reason": "標為已截止但找不到依據",
        "rolling_with_end_date": "隨時受理卻有截止日", "admission_drift": "依現行收錄政策應排除",
        "should_be_portal": "應為彙整頁", "no_simple_rules": "沒有可判斷的資格規則", "rules_unsatisfiable": "必要條件互斥、永遠比對不上",
        "tier_conflict": "品質等級與完整度矛盾", "schema_invalid": "綱要驗證不通過",
        "schema_dropped_fields": "綱要驗證移除了欄位（值在原文找不到）", "duplicate_canonical": "同名同機關的重複代表紀錄",
        "text_too_short": "原文過短",
        "derived_number_not_in_text": "AI 改寫的敘述裡有原文沒有的數字", "derived_city_not_in_text": "AI 改寫的敘述裡有原文沒有的縣市",
        "placeholder_rule_junk_excerpt": "佔位規則掛在段落標題上", "placeholder_attribute_unsupported": "佔位規則的屬性摘錄沒提到", "rule_value_missing": "規則缺值", "rule_number_not_in_text": "規則數字不在原文",
    }
    for code, n in counts.most_common():
        lines.append(f"| `{code}` | {n} | {labels.get(code, '')} |")
    lines += ["", "## 各來源旗標數", "", "| 來源 | 紀錄 | 旗標 |", "| --- | ---: | ---: |"]
    per_source_rows = Counter(r["source_id"] for r in results)
    for source, n in per_source_rows.most_common():
        lines.append(f"| {source} | {n} | {sum(by_source[source].values())} |")
    lines += ["", "## 逐筆（只列有旗標的）", ""]
    for r in results:
        if not r["flags"]:
            continue
        lines.append(f"### {r['title'][:60]}")
        lines.append(f"- id `{r['id']}` ｜ 來源 {r['source_id']} ｜ 類別 {r['category']} ｜ 機關 {r['provider']} ｜ 等級 {r['quality_tier']}")
        for f in r["flags"]:
            lines.append(f"- `{f['code']}` {f['field']}：{f['detail']}")
        lines.append("")
    io.open(out_base + ".md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"records={len(results)} clean={clean} flags={sum(counts.values())}")
    for code, n in counts.most_common(30):
        print(f"  {n:>5}  {code}  {labels.get(code, '')}")
    print("wrote", out_base + ".json", "and", out_base + ".md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
