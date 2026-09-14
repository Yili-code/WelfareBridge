# 補助資料模型 v2：儲存 Schema、填入流程、比對流程

適用範圍：上千到上萬筆、跨領域（教育、社福、長照、身障、青年、住宅…）的補助。
設計原則：**schema 固定、屬性登錄表成長、規則引用登錄表、原文永遠保留**。方法依據見 [matching-strategy.md](matching-strategy.md)。

---

## 1. 總覽

```text
                 ┌──────────────────────┐
官方網站 ──爬取──▶│ raw_documents         │ 原文、hash、時間（不改動）
                 └──────────┬───────────┘
                            │ 填入流程（第 3 節）
                            ▼
┌───────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│ taxonomy      │◀──│ benefits              │──▶│ benefit_rules         │
│ 領域／類別樹   │   │ core + benefit meta   │   │ attribute_id/op/value │
└───────────────┘   └──────────┬───────────┘   └──────────┬───────────┘
                               │                          │ 引用
                               ▼                          ▼
                    ┌──────────────────────┐   ┌──────────────────────┐
                    │ benefit_embeddings    │   │ attribute_registry    │ 唯一會成長的定義（資料）
                    └──────────────────────┘   └──────────┬───────────┘
                                                          │ 引用
                    ┌──────────────────────┐   ┌──────────▼───────────┐
                    │ match_results /       │◀──│ user_profiles         │ {attribute_id: value}
                    │ feedback_events       │   └──────────────────────┘
                    └──────────────────────┘
```

五個固定表（`raw_documents`、`benefits`、`benefit_rules`、`user_profiles`、`match_results`）與三個「資料型定義」（`attribute_registry`、`taxonomy`、`identity_ontology`）。新增領域只改後三者。

---

## 2. 儲存 Schema

### 2.1 `raw_documents`（沿用現有）

| 欄位 | 型態 | 說明 |
| --- | --- | --- |
| id | uuid | |
| source_id | str | 來源登錄 id |
| source_url | str | 唯一鍵（與 source_id） |
| title、raw_html、raw_text | text | 原文不改動 |
| content_hash | str | 變更偵測 |
| fetched_at、last_seen_at | datetime | |
| processing_status | enum | pending / classified / extracted / filtered_out / failed |
| classification | json | 第 3.2 步輸出：domain、category、is_benefit、confidence |

### 2.2 `benefits`（原 `scholarships`，改名以涵蓋所有領域）

**core（固定）**

| 欄位 | 型態 | 必填 | 填入方式 |
| --- | --- | --- | --- |
| id、canonical_id、is_canonical | uuid | ✓ | 系統、去重 |
| raw_document_id | uuid | ✓ | 系統 |
| title | str | ✓ | 頁面標題／LLM 修正 |
| domain | str | ✓ | taxonomy 節點 id，例：`education`、`social_welfare.long_term_care` |
| category | str | ✓ | taxonomy 葉節點，例：`scholarship`、`home_care_subsidy` |
| provider、provider_type、provider_region | str | ✓ | 機關分類器；`provider_region` 為縣市或 `national` |
| source | json | ✓ | url、domain、verified、method、crawl_time |
| original_text | text | ✓ | 原文（所有摘錄驗證的依據） |
| description | text | | LLM 摘要，附摘錄 |
| status | enum | ✓ | active / expired / needs_review / superseded |
| extraction_version、registry_version | str | ✓ | 追溯用（第 2.10） |

**benefit meta（固定約 10 欄，跨領域相同）**

| 欄位 | 型態 | 說明 | 填入 |
| --- | --- | --- | --- |
| benefit_form | enum | cash / waiver / service / in_kind / loan / voucher | LLM，固定選項 |
| amount | json | {type: fixed/range/tiered/unknown, value, min, max, unit, period: once/month/semester/year, description} | 規則 + LLM |
| amount_annualized | number | 由 amount × period 換算，排序用 | 系統推導 |
| application_period | json | {start_date, end_date, rolling: bool, description} | 規則 + LLM |
| award_basis | enum | criteria（符合即發）/ competitive（擇優）/ lottery / unknown | LLM |
| quota | int/null | 名額 | LLM，數字必在摘錄 |
| application | json | {channel: school/agency/online/mail, effort: low/medium/high, requires_interview, requires_office_proof, requires_financial_proof, documents: [str]} | 規則 + LLM |
| obligations | [str] | 得獎後義務（服務時數、出席、心得） | LLM，附摘錄 |
| exclusive_with | [enum] | government_benefit / same_provider / same_category / none | LLM |
| renewable | bool/null | 可續領 | LLM |
| target_population_text | text | 一段「給誰的」描述，供 embedding | LLM，每句附摘錄 |

**evidence**

| 欄位 | 型態 | 說明 |
| --- | --- | --- |
| evidence | json[] | 每個非系統欄位一筆 {field, value, excerpt, offset, extractor, confidence, inferred} |
| llm_result | json | 模型、prompt 版本、merge_report{accepted, rejected} |
| needs_review、review_reasons | bool、[str] | 進審核佇列的原因 |

### 2.3 `benefit_rules`

| 欄位 | 型態 | 說明 |
| --- | --- | --- |
| id、benefit_id | uuid | |
| attribute_id | str | **必在 attribute_registry** |
| operator | enum | `=`、`!=`、`>`、`>=`、`<`、`<=`、`in`、`not_in`、`contains`、`between`、`exists` |
| value | json | 依屬性型態；complex 可為 null |
| unit | str | 與登錄表一致，不一致時在填入階段換算 |
| group_id | str | 同組 OR、不同組 AND |
| group_logic | enum | any / all（預設 any；保留給「需同時具備」的組） |
| complexity | enum | simple / complex |
| role | enum | required（必要）/ exclusion（排除）/ bonus（加分，不判資格） |
| human_readable | str | UI 顯示 |
| evidence | json | {excerpt, offset, extractor: pattern/llm/structured_field} |
| confidence | 0～1 | |
| inferred、inference_basis | bool、str | 由機關推定「本市」等 |
| registry_version | str | 產生此規則時的登錄表版本 |

索引：`(attribute_id)`、`(benefit_id)`、`(attribute_id, operator)`。

### 2.4 `attribute_registry`（YAML 進版控，載入為表）

```yaml
version: 3
attributes:
  - id: applicant.age
    type: number            # number / boolean / enum / multi_enum / city / date / text
    unit: years
    domains: [all]
    label: 年齡
    question: 你今年幾歲？
    aliases: [年滿, 歲以上, 未滿, 歲以下]
    sensitivity: low        # low / medium / high（high 者追問前先說明用途、可跳過）
    hard_filter: true       # 可作為候選檢索的索引欄位
    ask_priority: 90

  - id: residence.household_city
    type: city
    domains: [all]
    label: 戶籍縣市
    question: 你的戶籍在哪個縣市？
    aliases: [設籍, 戶籍地, 本市, 本縣]
    hard_filter: true
    ask_priority: 95

  - id: disability.certificate_level
    type: enum
    values: [輕度, 中度, 重度, 極重度]
    ordered: true           # 有序 enum 才允許 >= <=
    domains: [disability, long_term_care, education]
    label: 身心障礙證明等級
    question: 你的身心障礙證明等級是？
    aliases: [身心障礙手冊, 身障證明, 障礙等級]
    sensitivity: high
    hard_filter: true
    ask_priority: 80

  - id: care.cms_level
    type: number
    domains: [long_term_care]
    label: 長照需要等級（CMS）
    question: 照顧管理專員評估的 CMS 等級是第幾級？
    aliases: [CMS, 照顧管理評估, 長照需要等級]
    sensitivity: high
    ask_priority: 85

  - id: household.income_per_capita
    type: number
    unit: TWD/month
    domains: [all]
    label: 家庭每人每月平均所得
    derived: household.income_month / household.size
    aliases: [平均每人每月收入, 最低生活費]
    ask_priority: 60

  - id: household.income_vs_poverty_line
    type: number
    domains: [all]
    label: 家庭每人所得為最低生活費的倍數
    derived: household.income_per_capita / poverty_line(residence.household_city)
    ask_priority: 0         # 不直接問，由推導得出
```

治理規則：
- 新增屬性要有 owner、至少一筆引用它的規則、與既有屬性的 embedding 相似度 < 0.85（否則視為同義詞，加進 aliases）。
- 刪除屬性不允許；廢止用 `deprecated: true` + `replaced_by`。
- 每次變更 `version` +1，`benefit_rules.registry_version` 記錄。

### 2.5 `taxonomy`（YAML）

```yaml
- id: education
  label: 教育
  children:
    - {id: scholarship, label: 獎學金}
    - {id: student_aid, label: 助學金}
    - {id: tuition_waiver, label: 學雜費減免}
- id: social_welfare
  label: 社會福利
  children:
    - id: long_term_care
      label: 長期照顧
      children:
        - {id: home_care_subsidy, label: 居家照顧服務給付}
        - {id: assistive_device, label: 輔具補助}
    - {id: disability_living_allowance, label: 身心障礙者生活補助}
```

類別是資料；分類器的候選清單就是這棵樹的葉節點。

### 2.6 `identity_ontology`（YAML）

```yaml
- id: low_income            # 對應屬性 identity.low_income
  label: 低收入戶
  aliases: [低收, 低收入家庭]
  implies: [economic_hardship, disadvantaged_student]
- id: disadvantaged_student
  label: 弱勢學生
  basis: 教育部弱勢學生助學計畫定義
  implied_by: [low_income, middle_low_income, special_circumstances, disability, indigenous]
```

### 2.7 `benefit_embeddings`

| 欄位 | 說明 |
| --- | --- |
| benefit_id | |
| text_kind | target_population / title / summary |
| embedding | vector（pgvector 或外部向量庫） |
| model、model_version | 換模型時整表重算 |

### 2.8 `user_profiles`

```json
{
  "id": "…",
  "attributes": {
    "education.level":            {"value": "university", "source": "parsed", "evidence": "海洋大學資工大二", "confirmed": true},
    "residence.household_city":   {"value": "基隆市", "source": "asked", "confirmed": true},
    "academic.average_score":     {"value": 82, "source": "parsed", "evidence": "平均82分", "confirmed": false},
    "identity.low_income":        {"value": null, "source": "skipped"}
  },
  "need_type": "cash_now",
  "urgency": "high",
  "dislikes": ["interview", "obligations"],
  "current_benefits": ["教育部弱勢助學金"],
  "asked": ["residence.household_city"],
  "skipped": ["identity.low_income"],
  "registry_version": 3
}
```

`source`：asked（追問）/ parsed（自由文字抽取）/ inferred（推導欄位）/ skipped。硬過濾只用 `confirmed: true` 或 `source: asked` 的值。

### 2.9 `match_results`、`feedback_events`

| 表 | 欄位 |
| --- | --- |
| match_results | profile_id、benefit_id、status、eligibility_score、suitability_score、rank、condition_results[]、explanation[]、registry_version、created_at |
| feedback_events | profile_id、benefit_id、event（viewed / applied / awarded / rejected / not_interested）、reason、created_at |

### 2.10 版本與追溯

每筆 benefit 記 `extraction_version`（抽取程式與 prompt 版本）與 `registry_version`。登錄表升版後：
- 舊規則照常可用（屬性只新增不刪）。
- 背景工作對 `registry_version < 現行` 的公告做增量補抽，只針對新屬性。

---

## 3. 填入流程（每份公告）

```text
raw_document
 3.1 正規化 ──▶ 3.2 分類 ──▶ 3.3 抽 core + benefit meta ──▶ 3.4 抽條件句
 ──▶ 3.5 條件句對登錄表 ──▶ 3.6 組規則 ──▶ 3.7 驗證 ──▶ 3.8 去重與索引 ──▶ 3.9 審核佇列
```

### 3.1 正規化
全形半形、民國年、中文數字、縣市別名、單位（萬元→元、學期→年化）。原文不改，另存正規化文字供比對。

### 3.2 分類（取代 keyword_rules）
- 輸入：title + 前 2,000 字。
- 方法：embedding 對 taxonomy 葉節點描述取前 5 → LLM 在這 5 個中選 1 並判斷 `is_benefit`。
- 輸出：`{is_benefit, domain, category, confidence}`；`is_benefit=false` → filtered_out。
- 成本：每份一次小模型呼叫（`claude-haiku-4-5`）。

### 3.3 抽 core + benefit meta（固定 JSON schema）
- 一次 LLM 呼叫（`claude-sonnet-5`），輸出嚴格對應 2.2 的欄位，每個欄位附 `excerpt`。
- 規則式 extractor 先跑，結果放進 prompt 當「已知值」，LLM 只補空缺或糾正並說明理由。
- 數字必在摘錄、摘錄必在原文，否則該欄位丟棄並記 review_reason。

### 3.4 抽條件句
LLM 把「申請資格」「不得申請」「優先」段落切成條件句清單：

```json
[
  {"text": "設籍本市六個月以上", "excerpt": "凡設籍本市六個月以上", "role": "required"},
  {"text": "持有中度以上身心障礙證明", "excerpt": "領有中度以上身心障礙證明者", "role": "required"},
  {"text": "已接受機構安置者不得申請", "excerpt": "已接受機構安置者，不得申請", "role": "exclusion"},
  {"text": "低收入戶優先", "excerpt": "低收入戶優先補助", "role": "bonus"}
]
```

只切句、標角色，**不在這步決定屬性**。

### 3.5 條件句對登錄表（語意認欄位）
對每個條件句：
1. embedding 與登錄表每個屬性的 `label + aliases + question` 比相似度，取前 5。
2. LLM 在前 5 中選 1 個屬性並輸出 operator / value / unit；若都不合適，輸出 `no_match` 並提議新屬性（id、label、type、question）。
3. 相似度最高者 ≥ 0.85 且 LLM 同意 → 直接採用；否則 → needs_review。
4. 提議的新屬性進「登錄表提案佇列」，人工核准後才進登錄表；核准前該條件保持 complex。

### 3.6 組規則
- 同一條件句內「A 或 B」→ 同 group_id 多條，或一條 `in [A, B]`。
- `role: exclusion` → operator 取反（`not_in`、`!=`、`<`），仍是 required 規則。
- `role: bonus` → 不參與資格判定，存為 `role=bonus` 供排序加分與說明。
- 身分類 → 經 identity_ontology 展開 implies。
- 單位換算到登錄表單位。

### 3.7 驗證（schema_validator，沿用並擴充）
- attribute_id 在登錄表；operator 與屬性型態相容（enum 未 ordered 不得用 `>=`）。
- value 型態、enum 值合法；數字必在摘錄；摘錄必在原文。
- 不通過的規則降為 complex 並記原因，不丟原文。

### 3.8 去重與索引
- 標題相似 + 機關相容 + 截止日相同 → 同 canonical_id。
- 寫入 `benefit_rules` 索引；產生 `benefit_embeddings.target_population`。
- 更新「屬性 → benefit 清單」倒排索引（第 4.1）。

### 3.9 審核佇列
進佇列條件：分類 confidence < 0.7、任一 core 欄位缺、條件句 no_match、驗證失敗、`inferred=true`。
審核 UI 每筆顯示原文摘錄與建議值，操作只有：接受／修正／標為同義詞／核准新屬性。

### 3.10 成本估算（上萬筆）
每份公告：分類 1 次小模型、抽取 1 次中模型、條件句認欄位 N 次小模型（N ≈ 5～10，可批次成 1 次）。內容 hash 未變不重跑；登錄表升版只補抽新屬性。

---

## 4. 比對流程（上萬筆）

```text
profile
 4.1 候選檢索（索引） 10,000 → 300
 4.2 規則評估          300 → 符合 / 可能 / 不符合 / 資料不足
 4.3 追問迴圈          直到停止條件
 4.4 篩選後漏斗        符合 50 → 建議 3～8
 4.5 解釋與回饋
```

### 4.1 候選檢索
用 profile 中 `hard_filter: true` 且已確認的屬性查索引，不掃原文：

```sql
-- 概念：只排除「確定不符」的，缺資料者保留
SELECT b.id FROM benefits b
WHERE b.status = 'active'
  AND (b.application_end IS NULL OR b.application_end >= today)
  AND b.domain IN (:do          mains_for_need_type)
  AND NOT EXISTS (          -- 有規則明確排除使用者已知值
    SELECT 1 FROM benefit_rules r
    WHERE r.benefit_id = b.id AND r.complexity = 'simple' AND r.confidence >= 0.8
      AND r.attribute_id = 'residence.household_city' AND r.operator = 'in'
      AND NOT (:user_city = ANY(r.value)))
  -- 同型態條件對 education.level、applicant.age、disability.certificate_level…
```

實作上為每個 `hard_filter` 屬性預先算「值 → 明確排除的 benefit 集合」位圖，檢索 = 全集減去各位圖的聯集。可選：需求為自由文字時，用 `target_population` embedding 取前 200 與位圖結果取聯集（只加候選，不減）。

### 4.2 規則評估（現有 rule engine）
對候選逐筆：同組 OR、不同組 AND；缺資料 unknown；complex unknown；`not_match` 只能由 confidence ≥ 0.8 且非 inferred 的 simple 規則產生；`role=bonus` 不參與。
輸出每筆 status、eligibility_score、missing_attributes、failed_conditions。300 筆 × 10 條規則為毫秒級。

### 4.3 追問迴圈
- 對 possible / insufficient 的候選，算每個缺屬性的期望資訊增益（模擬各回答 → 翻轉的候選適合度總和），硬過濾屬性 ×2，`sensitivity: high` 者 ×0.7 且先說明用途。
- 停止：最高增益 < 門檻、high_match ≥ 3、或已問 7 題。
- 每答一題只重算受影響的候選（該屬性倒排索引命中的那些）。

### 4.4 篩選後漏斗（matching-strategy 第 10 節）
A 實際不能申請 → B 需求分流 → C 適合度計分 → D 互斥組合 → E 三張卡 + 清單。
C 段需要的 benefit meta 若未抽（舊資料），對這 ≤ 50 筆即時抽並回寫。

### 4.5 解釋與回饋
每筆結果附 condition_results（含原文摘錄）與 suitability 分項；`feedback_events` 回寫個人 dislikes 與全域權重。

### 4.6 效能要點
- profile hash 快取整個 4.1～4.2 結果；追問只做增量。
- 複雜條件的 LLM 判斷只對進入前 20 名的候選做，且每筆一次呼叫、逐條輸出。
- 倒排索引與位圖在規則寫入時維護；登錄表升版後重建受影響屬性的位圖即可。

---

## 5. 監控指標（上萬筆時必看）

| 指標 | 意義 | 警戒 |
| --- | --- | --- |
| needs_review 比例 | 抽取品質 | > 15% |
| 條件句 no_match 比例 | 登錄表覆蓋不足 | > 10%，看提案佇列 |
| 每屬性 unknown 比例（媒合時） | 使用者答不出／沒問到 | 單屬性 > 50% 檢討問法 |
| 誤拒率（黃金集） | 最傷的錯誤 | > 2% |
| 平均追問題數 | 體驗 | > 6 |
| 登錄表屬性數 | 治理 | 每領域新增 > 20 檢討同義詞合併 |

---

## 6. 範例：一筆長照補助走完流程

原文片段：「凡設籍本市六個月以上，領有中度以上身心障礙證明，經照顧管理專員評估為長照需要等級第 4 級以上者，得申請居家照顧服務補助；已接受機構安置者不得申請。低收入戶優先。」

```json
{
  "domain": "social_welfare.long_term_care", "category": "home_care_subsidy",
  "benefit_form": "service", "award_basis": "criteria", "exclusive_with": ["same_category"],
  "rules": [
    {"attribute_id": "residence.household_city", "operator": "in", "value": ["臺北市"], "inferred": true, "inference_basis": "機關為臺北市政府社會局", "group_id": "residence"},
    {"attribute_id": "residence.duration_months", "operator": ">=", "value": 6, "group_id": "residence_duration"},
    {"attribute_id": "disability.certificate_level", "operator": ">=", "value": "中度", "group_id": "disability"},
    {"attribute_id": "care.cms_level", "operator": ">=", "value": 4, "group_id": "cms"},
    {"attribute_id": "care.institutional_placement", "operator": "=", "value": false, "role": "exclusion", "group_id": "placement"},
    {"attribute_id": "identity.low_income", "operator": "=", "value": true, "role": "bonus", "group_id": "priority"}
  ]
}
```

使用者說「我爸 70 歲住台北，中度身障，剛做完長照評估是第 5 級」→ profile 抽出 city、certificate_level、cms_level；缺 `residence.duration_months` 與 `care.institutional_placement` → 追問這兩題（增益最高）→ 兩題都答 → high_match；`identity.low_income` 未問，僅影響排序說明「若為低收入戶可優先」。
