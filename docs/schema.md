# Schema（v2）

完整說明：[data-model-v2.md](data-model-v2.md)（結構與流程）、[data-dictionary.md](data-dictionary.md)（逐欄與列舉值）。
實際載入的登錄表：[generated/registry-attributes.md](generated/registry-attributes.md)、[generated/taxonomy.md](generated/taxonomy.md)。

## benefits 文件（MongoDB）

```json
{
  "_id": "uuid", "raw_document_id": "uuid", "source_id": "taipei_dosw", "canonical_id": "uuid", "is_canonical": true,
  "title": "臺北市身心障礙者生活補助", "domain": "disability", "category": "disability_living_allowance", "category_label": "身心障礙者生活補助",
  "provider": "臺北市政府社會局", "provider_type": "local_government", "provider_region": "臺北市",
  "source": {"source_id": "taipei_dosw", "source_name": "…", "source_url": "https://dosw.gov.taipei/cp.aspx?n=C764A5808F9A3B08", "official_domain": "dosw.gov.taipei", "source_verified": true, "crawl_time": "2026-09-12T05:…", "is_repost": false, "data_confidence": 100, "content_type": "html"},
  "original_text": "…（完整原文）", "description": "…", "is_overview": false, "status": "active",
  "benefit": {
    "benefit_form": "cash", "benefit_form_inferred": false,
    "amount": {"type": "range", "value": null, "min": 4049, "max": 9485, "unit": "TWD", "period": "month", "count_per_year": 12, "description": "…", "tiers": []}, "amount_annualized": 81204,
    "application_period": {"start_date": "", "end_date": "", "rolling": false, "description": "", "by_school_deadline": false},
    "award_basis": "criteria", "quota": null, "quota_tiers": [],
    "application": {"channel": "agency", "effort": "medium", "documents": ["…"], "requires_interview": false, "requires_recommendation": false, "requires_essay": false, "requires_office_proof": false, "requires_financial_proof": true, "method": "…", "contact": {"phone": "…", "email": "", "department": "…"}},
    "obligations": [], "exclusive_with": ["public_funding"], "renewable": null, "decision_lead_days": null, "target_population_text": "…（本地 AI 填入，附摘錄）"
  },
  "rules": [
    {"id": "…", "attribute_id": "identity.tags", "operator": "contains", "value": "disabled", "unit": "", "group_id": "identity_required_disabled", "group_logic": "any", "complexity": "simple", "role": "required",
     "human_readable": "身分：身心障礙", "evidence": {"excerpt": "臺北市身心障礙者生活補助", "extractor": "rule_based", "condition_text": "…"}, "confidence": 0.9, "inferred": false, "inference_basis": "", "registry_version": 2},
    {"id": "…", "attribute_id": "residence.household_city", "operator": "in", "value": ["臺北市"], "group_id": "residence_household_city", "complexity": "simple", "role": "required", "human_readable": "戶籍縣市：臺北市（依機關推定）", "evidence": {"excerpt": "設籍並實際居住本市", "extractor": "rule_based"}, "confidence": 0.7, "inferred": true, "inference_basis": "原文寫「本市」，依機關名稱／標題中的「臺北市」推定"},
    {"id": "…", "attribute_id": "care.institutional_placement", "operator": "=", "value": false, "group_id": "exclusion_care_institutional_placement", "complexity": "simple", "role": "exclusion", "human_readable": "已入住機構：否", "evidence": {"excerpt": "已入住住宿式機構者不得申請", "extractor": "rule_based"}, "confidence": 0.8}
  ],
  "evidence": [{"field": "benefit.amount", "value": {"min": 4049, "max": 9485}, "excerpt": "…", "extractor": "rule_based", "confidence": 0.85, "inferred": false, "inference_basis": ""}],
  "conditions": [{"text": "…", "excerpt": "…", "role": "required", "status": "mapped | unmapped | complex | procedural", "attribute_id": null, "candidates": ["…"], "method": "rule | llm"}],
  "classification": {"is_benefit": true, "category": "disability_living_allowance", "signal_score": 21, "threshold": 4, "confidence": 0.82, "matched_signal": ["補助", "申請資格", "…"], "matched_category": {"disability_living_allowance": ["身心障礙者生活補助"]}, "method": "keyword"},
  "llm": {"processed": true, "model": "qwen2.5:7b", "provider": "ollama", "processed_at": "…", "tasks": {"benefit_meta": {"accepted": 3, "rejected": 1}, "condition_mapping": {"accepted": 2, "rejected": 1, "proposed_attributes": 0}}, "accepted": [{"field": "award_basis", "value": "criteria", "excerpt": "…"}], "rejected": [{"field": "quota", "reason": "數值未出現在摘錄或摘錄不在原文"}], "errors": []},
  "review": {"needs_review": false, "reasons": []}, "confidence": 0.86,
  "index": {"attribute_ids": ["identity.tags", "residence.household_city", "…"], "residence_cities": ["臺北市"], "education_levels": [], "tags_required": ["disabled"], "amount_min": 4049, "amount_max": 9485, "application_end": "", "simple_rules": 4, "complex_rules": 5},
  "keywords": ["…"], "attachments": [], "structured_fields": {}, "extraction_version": "2.0.0", "registry_version": 2, "content_hash": "…",
  "first_seen_at": "…", "last_seen_at": "…", "updated_at": "…"
}
```

## 規則規格

| 欄位 | 說明 |
| --- | --- |
| `attribute_id` | 屬性登錄表 id（`app/registry/attribute_registry.yaml`）；`identity.tags` 為虛擬屬性（由布林身分與本體 implies 推得） |
| `operator` | `=`、`!=`、`>`、`>=`、`<`、`<=`、`in`、`not_in`、`contains`、`between`、`exists`；允許的組合依屬性型態（enum 需 `ordered: true` 才能 `>=`） |
| `group_id` | 同組 OR、不同組 AND；`alternative_N`：原文「符合下列條件之一」的條列 |
| `role` | `required` 必要／`exclusion` 排除（已轉成必要語意）／`bonus` 加分（不判資格） |
| `complexity` | `simple`（rule engine 判斷）／`complex`（本地 AI 或人工；永不單獨拒絕） |
| `evidence.excerpt` | 官方原文摘錄；validator 確認真的在原文 |
| `confidence` / `inferred` | not_match 只能由 confidence ≥ 0.8 且非推定的 simple 規則產生 |

## User Profile

```json
{
  "attributes": {
    "education.level": {"value": "university", "source": "parsed", "evidence": "海洋大學資工大二", "confirmed": false, "confidence": 0.9},
    "residence.household_city": {"value": "基隆市", "source": "asked", "evidence": "", "confirmed": true, "confidence": 1.0},
    "identity.low_income": {"value": true, "source": "form", "confirmed": true}
  },
  "need_type": "cash_now", "urgency": "normal", "dislikes": ["interview"], "current_benefits": [], "preferences": {"minimum_amount": null}, "asked": [], "skipped": []
}
```

`identity.tags`、`household.income_month`、`applicant.is_elderly` 等推導屬性由登錄表即時計算；未提供的屬性 rule engine 回 unknown（資料不足）。
