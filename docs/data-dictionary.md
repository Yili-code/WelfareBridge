# 資料字典：結構內容與類別詳細說明

對應 [data-model-v2.md](data-model-v2.md) 的每個結構，逐欄說明型態、允許值、意義、填入來源、用途。
通用約定見第 0 節；所有列舉值都是封閉集合，新增值視為 schema 變更需升版。

---

## 0. 通用約定

| 約定 | 內容 |
| --- | --- |
| id | uuid v4；`attribute_id`、taxonomy id 用小寫英文加點號命名空間（`residence.household_city`） |
| 日期 | ISO `YYYY-MM-DD`；民國年在正規化階段轉換；只有月日者取公告年份並標 `inferred` |
| 金額 | 整數新臺幣元；「萬元」在正規化階段換算 |
| 縣市 | 22 個標準名稱（臺北市、新北市…），「台」統一為「臺」 |
| null 語意 | 「原文未提」或「使用者未答」，永遠不是「否」；rule engine 對 null 回 unknown |
| evidence | 任何由原文或使用者文字得出的值都要有 `{excerpt, offset?, extractor, confidence, inferred}`；excerpt 必須是原文子字串 |
| 版本 | `extraction_version`（程式＋prompt）、`registry_version`（登錄表）、`taxonomy_version` |
| 保留原則 | 原文、被驗證器移除的欄位（記在 review_reasons）、過期公告都不刪 |

---

## 1. `benefits.core`

| 欄位 | 型態 | 必填 | 允許值／格式 | 意義 | 填入 | 用途 |
| --- | --- | --- | --- | --- | --- | --- |
| id | uuid | ✓ | | 本筆識別 | 系統 | |
| canonical_id | uuid | ✓ | | 去重後代表筆的 id；代表筆自身 id = canonical_id | 去重（標題相似 ≥ 0.82 ＋機關相容或截止日相同） | 媒合只用 canonical |
| is_canonical | bool | ✓ | | 是否為代表筆 | 去重；官方原始公告優先 | |
| raw_document_id | uuid | ✓ | | 來源原文 | 系統 | 回溯 |
| title | str | ✓ | ≤ 200 字 | 公告名稱 | 頁面標題；LLM 可去除「【轉知】」等前綴並記錄原標題 | 顯示、去重 |
| domain | str | ✓ | taxonomy 非葉節點 id | 領域 | 分類器 | 候選檢索、需求分流 |
| category | str | ✓ | taxonomy 葉節點 id | 類別 | 分類器 | 分流、分群顯示 |
| provider | str | ✓ | | 主辦機關全名 | 結構化欄位或 LLM | 顯示、去重 |
| provider_type | enum | ✓ | `central_government` 中央機關 / `local_government` 地方政府 / `township` 鄉鎮市區公所 / `school` 學校 / `private_organization` 民間團體 / `unknown` | 機關層級 | 機關名稱分類器（「部」「署」→ central；「市政府」「縣政府」→ local；「公所」→ township；「基金會」「協會」→ private） | 競爭範圍估計、篩選 |
| provider_region | str | ✓ | 22 縣市之一 或 `national` | 機關轄區 | 由機關名稱推定 | 「本市」推定依據、競爭範圍 |
| source | json | ✓ | 見 1.1 | 來源與驗證 | crawler | 顯示官方來源 |
| original_text | text | ✓ | | 完整純文字原文 | parser | 所有摘錄驗證依據；補抽 |
| description | text | | ≤ 300 字 | 摘要 | LLM，每句附摘錄 | 卡片顯示 |
| status | enum | ✓ | `active` 可申請 / `expired` 已過截止 / `needs_review` 待審核 / `superseded` 被新版本取代 | 生命週期 | 系統（截止日）、驗證器、去重 | 候選檢索先過濾 |
| extraction_version | str | ✓ | 例 `2.3.0` | 抽取程式與 prompt 版本 | 系統 | 增量重抽 |
| registry_version | int | ✓ | | 產生規則時的登錄表版本 | 系統 | 增量補抽 |
| created_at / updated_at | datetime | ✓ | | | 系統 | |

### 1.1 `source`

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| source_id | str | sources.yaml 的 id | 來源登錄 |
| source_name | str | | 顯示名 |
| source_url | str | https | 原始公告網址 |
| official_domain | str | | 網域 |
| source_type | enum | `government_site` / `school_site` / `repost` | 是否為轉載 |
| source_verified | bool | | 通過白名單＋HTTPS＋標題驗證 |
| source_verification_method | str | | 例 `domain + metadata + manual whitelist` |
| crawl_time / published_date / last_updated | datetime / date | | |
| is_repost | bool | | 轉載（例：學校轉知縣政府公告）；去重時原始優先 |
| data_confidence | 0～100 | | 來源可信度（官方原始 95、轉載 85） |

---

### 1.2 `record_kind` 與 `admission`（收錄政策，見 [inclusion-policy.md](inclusion-policy.md)）

| 欄位 | 型別 | 說明 |
| --- | --- | --- |
| `record_kind` | `program` \| `portal` | 補助方案 / 彙整頁。表單、附件、流程圖、進度查詢、標章、統計、問答、名單、行政公告在 pipeline 就被排除，不會成為紀錄 |
| `admission.kind` / `kind_label` | string | 同上（含中文標籤） |
| `admission.reason` | string | 判定原因（portal 時說明命中的標題字眼） |
| `admission.quality_tier` | `verified` \| `needs_review` \| `portal` | 資格與給付內容都有且來源已驗證 → verified |
| `admission.completeness.present / missing / missing_labels` | string[] | 依 GetGrant 必要欄位（name, agency, eligibility, amount, period, method, source_url）算出的有／無 |

## 2. `benefits.benefit`（給付特徵，跨領域固定）

| 欄位 | 型態 | 允許值 | 判定規則 | 填入 | 用途 |
| --- | --- | --- | --- | --- | --- |
| benefit_form | enum | `cash` 現金 / `waiver` 減免 / `service` 服務給付 / `in_kind` 實物 / `voucher` 券或額度 / `loan` 貸款 / `mixed` | 原文「發給…元」→ cash；「減免」「免繳」→ waiver；「服務」「照顧」「時數」→ service；「輔具」「物資」→ in_kind；「額度」「券」→ voucher；「貸款」「利息補貼」→ loan | LLM 固定選項 | 需求分流（8.1） |
| amount | json | 見 2.1 | | 規則＋LLM | 期望價值 |
| amount_annualized | int/null | 元／年 | fixed：value × 年內次數；range：取 (min+max)/2；tiered：依使用者條件選層 | 系統推導 | 排序 |
| application_period | json | 見 2.2 | | 規則＋LLM | 時效、A 段過濾 |
| award_basis | enum | `criteria` 符合即發 / `competitive` 擇優 / `lottery` 抽籤 / `first_come` 先到先得 / `unknown` | 「擇優」「評選」「依成績高低」「名額有限」→ competitive；「符合資格者均」「不限名額」→ criteria；「抽籤」→ lottery；「額滿為止」→ first_come | LLM | 獲獎機率 |
| quota | int/null | ≥ 1 | 「名額 N 名」「以 N 名為限」；「未定」「若干」→ null | LLM，數字必在摘錄 | 獲獎機率 |
| quota_tiers | json[]/null | [{when, quota}] | 分層名額 | LLM | 同上 |
| application | json | 見 2.3 | | 規則＋LLM | 申請成本 |
| obligations | str[] | 自由文字，每項附摘錄 | 得獎後義務：服務時數、出席典禮、繳交心得、成果報告、履約 | LLM | 排斥過濾 |
| exclusive_with | enum[] | `public_funding` 公費生 / `government_benefit` 其他政府獎助 / `same_provider` 同機關其他獎助 / `same_category` 同類補助 / `any_other` 任何其他獎助 / `none` | 「不得同時領取…」對應 | LLM | A 段、D 段互斥 |
| renewable | bool/null | | 「得續領」「連續」→ true；「一次」→ false | LLM | 減輕負擔型需求 |
| decision_lead_days | int/null | | 「N 日內核定」 | LLM | 急需現金時效 |
| target_population_text | text | ≤ 200 字 | 給誰的一段描述，每句附摘錄 | LLM | embedding 檢索、誤判檢查 |
| keywords | str[] | | 正規化後關鍵字 | 系統 | 關鍵字搜尋 |

### 2.1 `amount`

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| type | enum | `fixed` 固定 / `range` 範圍 / `tiered` 分層 / `unknown` | |
| value / min / max | int/null | 元 | fixed 用 value；range 用 min/max |
| tiers | json[] | [{when: {attribute_id, operator, value}, value}] | tiered 專用；when 引用登錄表屬性 |
| unit | str | `TWD` | |
| period | enum | `once` 一次 / `month` 每月 / `semester` 每學期 / `year` 每學年或每年 / `unknown` | 「每名」不是週期，需再判斷 |
| count_per_year | int/null | | period=semester → 2；month → 12 |
| description | str | | 原文金額段落 |

### 2.2 `application_period`

| 欄位 | 型態 | 說明 |
| --- | --- | --- |
| start_date / end_date | date/null | 只有月日時取公告年，`inferred=true` |
| rolling | bool | 隨到隨辦（無截止） |
| description | str | 原文 |
| by_school_deadline | bool | 「依各校公告截止日」→ true，UI 提示提早 |

### 2.3 `application`

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| channel | enum | `school` 向就讀學校 / `agency` 向機關臨櫃或郵寄 / `online` 線上 / `mail` 郵寄 / `unknown` | |
| effort | enum | `low` ≤ 3 份文件且無證明機關 / `medium` / `high` 需面試、自傳、讀書計畫或推薦函 | 系統由下列布林與文件數推導 |
| documents | str[] | | 每項附摘錄；程序性文字（「申請程序：」）不算文件 |
| requires_interview | bool | | 「面試」「口試」 |
| requires_recommendation | bool | | 「推薦函」「推薦信」 |
| requires_essay | bool | | 「自傳」「讀書計畫」「心得」 |
| requires_office_proof | bool | | 「村里長」「區公所出具」證明 |
| requires_financial_proof | bool | | 「財產清單」「所得清單」「稅」 |
| contact | json | {phone, email, department} | |

---

## 3. `benefit_rules`

| 欄位 | 型態 | 允許值 | 意義 | 用途 |
| --- | --- | --- | --- | --- |
| id / benefit_id | uuid | | | |
| attribute_id | str | 登錄表 id | 比對哪個使用者屬性 | rule engine |
| operator | enum | 見 3.1 | | |
| value | json | 依屬性型態 | | |
| unit | str | 與登錄表相同 | 填入時已換算 | |
| group_id | str | | 同組 OR、不同組 AND | 群組語意 |
| group_logic | enum | `any`（預設）/ `all` | 同組內是 OR 還是 AND | 少數「須同時具備」 |
| complexity | enum | `simple` / `complex` | complex 由 LLM 或人工判斷，永不單獨拒絕 | |
| role | enum | `required` 必要 / `exclusion` 排除（已取反成 required 語意，僅供顯示）/ `bonus` 加分，不判資格 | | 排序加分、說明 |
| human_readable | str | | UI 顯示 | |
| evidence | json | {excerpt, offset, extractor: `structured_field` / `pattern` / `llm`, condition_text} | | 追溯 |
| confidence | 0～1 | | structured_field 0.95～0.98、pattern 0.85～0.9、llm 0.6～0.85 | not_match 門檻 0.8 |
| inferred / inference_basis | bool / str | | 「本市」→ 機關轄區等 | 不得產生 not_match |
| registry_version | int | | | 增量補抽 |

### 3.1 operator 與屬性型態

| operator | 適用型態 | value 型態 | 語意 |
| --- | --- | --- | --- |
| `=` / `!=` | 全部 | 單值 | 相等；boolean 用 `= true/false` |
| `>` `>=` `<` `<=` | number、date、ordered enum | 單值 | 數值比較；ordered enum 依 values 順序 |
| `between` | number、date | [min, max] | 含端點 |
| `in` / `not_in` | enum、multi_enum、city、text | 清單 | 使用者值（或清單任一）落在／不落在集合 |
| `contains` | multi_enum、text | 單值 | 使用者清單含該值 |
| `exists` | 全部 | null | 使用者提供了此屬性即符合（例：持有某證明） |
| `duration_gte` / `duration_lte` | number（月） | 單值 | 相容舊資料，等同 `>=` `<=` |

### 3.2 群組命名慣例

`education`、`residence`、`residence_duration`、`identity`、`academic_average`、`academic_conduct`、`academic_subject_min`、`age`、`household_income`、`public_funding`、`program_type`、`other_benefit`、`disability`、`care_level`、`priority`（bonus 專用）。同一公告同名群組視為 OR。

---

## 4. `attribute_registry`

### 4.1 一筆屬性的欄位

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| id | str | `namespace.name` | 命名空間見 4.2 |
| type | enum | `number` / `boolean` / `enum` / `multi_enum` / `city` / `date` / `text` | 決定允許的 operator 與問題型態 |
| values | str[] | enum / multi_enum 必填 | 允許值 |
| ordered | bool | enum 專用 | true 才允許 `>=` `<=` |
| unit | str | number 專用 | `years`、`months`、`score`、`TWD/year`、`TWD/month`、`percent`、`level` |
| domains | str[] | taxonomy 節點或 `all` | 哪些領域會用到；候選檢索與追問範圍 |
| label | str | | 中文標籤 |
| question | str | | 追問句 |
| help | str | | 補充說明（為什麼問、怎麼查） |
| aliases | str[] | | 原文與使用者文字中的同義詞；供 embedding 與 pattern |
| sensitivity | enum | `low` / `medium` / `high` | high：先說明用途、允許跳過、不得推定 |
| hard_filter | bool | | 可建位圖索引做候選檢索 |
| ask_priority | 0～100 | | 同增益時的平手排序；0 = 不直接問 |
| derived | str | | 由其他屬性推導的公式（四則運算與查表） |
| identity_tag | str | | 對應 identity_ontology 的 id（身分類屬性） |
| deprecated / replaced_by | bool / str | | 廢止與取代 |
| owner | str | | 維護者 |
| since_version | int | | 加入時的登錄表版本 |

### 4.2 命名空間

| 命名空間 | 內容 | 主要領域 |
| --- | --- | --- |
| applicant | 申請人基本：年齡、性別、國籍、婚姻 | all |
| education | 學制、年級、學校、科系、學校類型、部別 | education |
| academic | 成績、排名、操行、懲處 | education |
| residence | 戶籍、居住、設籍時間、學校所在地 | all |
| household | 家庭人口、所得、財產、扶養 | all |
| financial | 領取中的補助、公費、貸款 | all |
| identity | 身分別（低收、原住民、新住民、單親…） | all |
| disability | 身心障礙證明、等級、類別 | disability、long_term_care、education |
| care | 長照評估、失能、照顧者 | long_term_care |
| health | 疾病、重大傷病 | health、social_welfare |
| employment | 就業狀態、失業、職業 | labor、youth |
| housing | 住宅、租屋、自有 | housing |
| family | 子女數、生育、家庭狀況 | social_welfare |

### 4.3 初始屬性清單（v1，約 70 個）

**applicant**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| applicant.age | number | years | 你今年幾歲？ | low | ✓ |
| applicant.birth_date | date | | 出生年月日？（可只填年） | low | |
| applicant.gender | enum | male / female / other | 性別？ | medium | |
| applicant.nationality | enum | roc / foreign / stateless | 國籍？ | medium | ✓ |
| applicant.marital_status | enum | single / married / divorced / widowed | 婚姻狀況？ | medium | |

**education**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| education.level | enum (ordered) | elementary / junior_high / senior_high / vocational_high / junior_college / university / master / doctoral | 目前教育階段？ | low | ✓ |
| education.grade | number | | 幾年級？ | low | |
| education.enrolled | boolean | | 目前是否在學？ | low | ✓ |
| education.school | text | | 就讀學校？ | low | |
| education.school_type | enum | public / private | 公立或私立？ | low | |
| education.school_city | city | | 學校所在縣市？ | low | ✓ |
| education.department | text | | 科系？ | low | |
| education.field | enum | 依教育部學門分類 | 學門？ | low | |
| education.program_type | enum | day / night / continuing / in_service / open_university / credit_program / military_police | 日間部、夜間部、進修部、在職專班…？ | low | ✓ |
| education.extended_study | boolean | | 是否延長修業、重修或補修？ | low | |
| education.years_in_program | number | years | 就讀本學制第幾年？ | low | |
| education.is_freshman | boolean | | 是否為新生？ | low | |

**academic**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| academic.average_score | number | score | 上學期／學年學業平均？ | low | |
| academic.gpa | number | gpa (4.3) | GPA？ | low | |
| academic.ranking_percent | number | percent | 班級排名前百分之幾？ | low | |
| academic.conduct_score | number | score | 操行成績？ | low | |
| academic.subject_min_score | number | score | 最低一科成績？ | low | |
| academic.no_disciplinary_record | boolean | | 是否無警告以上懲處？ | medium | |
| academic.no_failed_subject | boolean | | 是否無不及格科目？ | low | |

**residence**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| residence.household_city | city | | 戶籍縣市？ | low | ✓ |
| residence.household_district | text | | 戶籍鄉鎮市區？ | low | |
| residence.duration_months | number | months | 設籍多久？ | low | |
| residence.current_city | city | | 目前居住縣市？ | low | ✓ |
| residence.same_household_as_parent | boolean | | 是否與父母同一戶籍？ | medium | |

**household / financial**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| household.size | number | | 家庭人口數？ | medium | |
| household.income_year | number | TWD/year | 家庭年所得？ | high | |
| household.income_month | number | TWD/month | derived: income_year / 12 | | |
| household.income_per_capita | number | TWD/month | derived: income_month / size | | |
| household.income_vs_poverty_line | number | multiple | derived: per_capita / poverty_line(residence.household_city) | | |
| household.assets | number | TWD | 家庭動產與不動產總額？ | high | |
| household.dependents | number | | 扶養人數？ | medium | |
| financial.receiving_public_funding | boolean | | 是否為公費生？ | low | |
| financial.receiving_other_benefit | multi_enum | government_scholarship / tuition_waiver / student_aid / living_allowance / none | 目前領取哪些政府補助？ | medium | |
| financial.student_loan | boolean | | 是否有就學貸款？ | medium | |

**identity**（每個對應 identity_ontology 一個 tag）

| id | type | tag | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| identity.low_income | boolean | 低收入戶 | 是否具低收入戶身分？ | high | ✓ |
| identity.middle_low_income | boolean | 中低收入戶 | 是否具中低收入戶身分？ | high | ✓ |
| identity.economic_hardship | boolean | 清寒 | 是否有清寒證明？ | high | |
| identity.special_circumstances | boolean | 特殊境遇家庭 | 是否為特殊境遇家庭？ | high | |
| identity.indigenous | boolean | 原住民 | 是否具原住民身分？ | high | ✓ |
| identity.indigenous_tribe | enum | 16 族 | 族別？ | high | |
| identity.hakka | boolean | 客家 | 是否為客家子弟？ | medium | |
| identity.new_immigrant | boolean | 新住民 | 是否為新住民或其子女？ | high | |
| identity.single_parent | boolean | 單親家庭 | 是否來自單親家庭？ | high | |
| identity.grandparent_family | boolean | 隔代教養 | 是否為隔代教養？ | high | |
| identity.orphan | boolean | 失依兒少 | 是否為失依兒少？ | high | |
| identity.veteran_family | boolean | 榮民子女 | 是否為榮民或榮眷子女？ | medium | |
| identity.military_civil_bereaved | boolean | 軍公教遺族 | 是否為軍公教遺族？ | medium | |
| identity.unemployed_worker_child | boolean | 失業勞工子女 | 父母是否為非自願失業勞工？ | high | |
| identity.overseas_chinese | boolean | 僑生 | 是否為僑生？ | medium | ✓ |
| identity.foreign_student | boolean | 外籍生 | 是否為外籍學生？ | medium | ✓ |
| identity.tags | multi_enum | 由上列布林組成的虛擬欄位 | | | |

**disability**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| disability.has_certificate | boolean | | 是否領有身心障礙證明？ | high | ✓ |
| disability.certificate_level | enum (ordered) | 輕度 / 中度 / 重度 / 極重度 | 證明等級？ | high | ✓ |
| disability.category | multi_enum | ICF 八大類 | 障礙類別？ | high | |
| disability.family_member_has_certificate | boolean | | 家中是否有身心障礙者？ | high | |

**care**（長照）

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| care.cms_level | number | level 1～8 | 長照需要等級（CMS）？ | high | ✓ |
| care.adl_score | number | score | 巴氏量表分數？ | high | |
| care.institutional_placement | boolean | | 是否已入住機構？ | high | ✓ |
| care.has_foreign_caregiver | boolean | | 是否聘有外籍看護？ | high | |
| care.is_primary_caregiver | boolean | | 你是否為主要照顧者？ | medium | |
| care.dementia_diagnosis | boolean | | 是否有失智診斷？ | high | |

**health / employment / housing / family**

| id | type | values / unit | question | sens | hard |
| --- | --- | --- | --- | --- | --- |
| health.catastrophic_illness | boolean | | 是否持有重大傷病卡？ | high | |
| health.specific_disease | text | | 特定疾病名稱？ | high | |
| employment.status | enum | employed / unemployed / student / retired / self_employed | 就業狀態？ | medium | ✓ |
| employment.unemployed_months | number | months | 失業多久？ | medium | |
| employment.labor_insured | boolean | | 是否有勞保？ | medium | |
| housing.tenure | enum | own / rent / family / dorm / none | 居住型態？ | medium | ✓ |
| housing.rent_month | number | TWD/month | 每月租金？ | medium | |
| family.children_count | number | | 子女數？ | medium | |
| family.youngest_child_age | number | years | 最小子女年齡？ | medium | |
| family.pregnant | boolean | | 是否懷孕？ | high | |

---

## 5. `taxonomy`（初始樹）

| domain | category（葉節點） | 說明 |
| --- | --- | --- |
| education | scholarship 獎學金 / student_aid 助學金 / tuition_waiver 學雜費減免 / education_subsidy 就學補助 / housing_support 住宿補助 / emergency_aid 急難救助 / loan 就學貸款 / study_abroad 留學獎助 | |
| youth | entrepreneurship 創業 / travel 壯遊 / employment_incentive 就業獎勵 / rental_subsidy 青年租金 | |
| social_welfare | low_income_allowance 低收生活補助 / special_circumstances_aid 特殊境遇扶助 / child_allowance 育兒津貼 / childcare_subsidy 托育補助 / emergency_relief 急難救助 | |
| social_welfare.long_term_care | home_care_subsidy 居家服務 / day_care 日照 / respite_care 喘息 / assistive_device 輔具 / home_modification 無障礙改善 / institutional_subsidy 機構費用補助 / caregiver_allowance 照顧者津貼 | |
| social_welfare.disability | living_allowance 生活補助 / assistive_device 輔具 / care_subsidy 照顧費用 / transport 交通 / education_subsidy 身障學生就學 | |
| labor | unemployment_benefit 失業給付 / training_allowance 職訓津貼 / employment_subsidy 僱用獎助 | |
| housing | rental_subsidy 租金補貼 / mortgage_subsidy 利息補貼 / social_housing 社宅 | |
| health | medical_subsidy 醫療補助 / catastrophic_illness 重大傷病 / mental_health 心理諮商 | |

每個節點欄位：`id`、`label`、`description`（給分類器 embedding）、`parent`、`default_benefit_form`、`need_types`（此類別能滿足的需求：cash_now / reduce_burden / honor / service）。

---

## 6. `identity_ontology`

| id | label | aliases | implies（有此即視為有…） | 對應屬性 |
| --- | --- | --- | --- | --- |
| low_income | 低收入戶 | 低收、低收入家庭 | economic_hardship、disadvantaged | identity.low_income |
| middle_low_income | 中低收入戶 | 中低收 | economic_hardship、disadvantaged | identity.middle_low_income |
| economic_hardship | 清寒 | 家境清寒、清寒家庭 | disadvantaged | identity.economic_hardship |
| special_circumstances | 特殊境遇家庭 | 特境 | disadvantaged | identity.special_circumstances |
| disadvantaged | 弱勢學生 | 弱勢、經濟弱勢 | — | （虛擬，僅由 implies 得出） |
| indigenous | 原住民 | 原住民族 | disadvantaged | identity.indigenous |
| disabled | 身心障礙 | 身障、身心障礙者、領有身心障礙證明 | disadvantaged | disability.has_certificate |
| disabled_family | 身心障礙人士子女 | 身心障礙者子女 | — | disability.family_member_has_certificate |
| new_immigrant | 新住民 | 新移民、外籍配偶、新住民子女 | — | identity.new_immigrant |
| single_parent | 單親家庭 | 單親 | — | identity.single_parent |
| orphan | 失依兒少 | 孤兒 | disadvantaged | identity.orphan |
| veteran_family | 榮民子女 | 榮眷 | — | identity.veteran_family |
| military_civil_bereaved | 軍公教遺族 | | — | identity.military_civil_bereaved |
| unemployed_worker_child | 失業勞工子女 | | — | identity.unemployed_worker_child |
| overseas_chinese | 僑生 | | — | identity.overseas_chinese |
| hakka | 客家 | 客家子弟 | — | identity.hakka |
| yami | 雅美族 | 達悟族 | indigenous | identity.indigenous_tribe = 雅美 |

`implies` 有 `basis` 欄位記依據（例：弱勢學生依教育部弱勢學生助學計畫）。

---

## 7. `user_profiles`

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| id / user_id | uuid | | |
| attributes | map | {attribute_id: AttributeValue} | 見 7.1 |
| need_type | enum | `cash_now` 急需現金 / `reduce_burden` 長期減負 / `honor` 榮譽履歷 / `service` 需要服務 / `unknown` | 排序權重預設 |
| urgency | enum | `high`（2 週內）/ `normal` / `low` | 時效權重 |
| dislikes | enum[] | `interview` / `essay` / `recommendation` / `obligations` / `financial_proof` / `office_proof` / `loan` / `competitive` | 硬過濾或 ×0.2 |
| current_benefits | str[] | 自由文字或 benefit_id | 互斥判斷 |
| preferences | json | {minimum_amount, preferred_categories[], preferred_location[]} | |
| asked / skipped | str[] | attribute_id | 追問狀態 |
| input_mode | enum | `form` / `step` / `chat` | |
| raw_inputs | str[] | 使用者原話 | evidence 依據 |
| registry_version | int | | |
| consent | json | {sensitive_data: bool, at} | 敏感屬性收集前同意 |

### 7.1 `AttributeValue`

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| value | 依屬性 | null = 未提供 | |
| source | enum | `asked` 追問回答 / `parsed` 自由文字抽取 / `form` 表單 / `inferred` 推導 / `skipped` 跳過 / `unsure` 答不確定 | |
| evidence | str | 使用者原話片段 | parsed 必填 |
| confirmed | bool | | 回述確認過；硬過濾只用 confirmed 或 asked/form |
| updated_at | datetime | | |

---

## 8. `match_results`

| 欄位 | 型態 | 允許值 | 說明 |
| --- | --- | --- | --- |
| status | enum | `high_match` / `possible_match` / `insufficient_data` / `not_match` | 資格層 |
| eligibility_score | 0～1 | | 規則層分數 |
| suitability | json | {expected_value, win_probability, urgency, cost, preference_fit, total} | 排序層分項 |
| rank | int | | 層內排序 |
| funnel_stage | enum | `eligible` / `removed_deadline` / `removed_exclusive` / `removed_need` / `removed_dislike` / `recommended` / `bundle` | 漏斗位置 |
| bundle_id | str/null | | 建議組合 |
| condition_results | json[] | 每條規則 {rule_id, status: match/not_match/unknown, reason, user_value, excerpt, llm_used} | 解釋 |
| explanation | str[] | | 卡片文字 |
| reasons | json | {why_recommended[], cautions[]} | 三張卡用 |
| registry_version / extraction_version | | | |

## 9. `feedback_events`

| 欄位 | 型態 | 允許值 |
| --- | --- | --- |
| event | enum | `viewed` / `expanded` / `clicked_source` / `applied` / `awarded` / `rejected` / `not_interested` / `reported_error` |
| reason | enum/null | not_interested：`amount_low` / `too_much_effort` / `interview` / `obligations` / `already_have` / `not_eligible_actually` / `other`；rejected：`eligibility` / `quota` / `documents` / `other`；reported_error：`wrong_rule` / `wrong_amount` / `wrong_deadline` / `expired` |
| note | str | 自由文字 |
| 回寫 | | not_interested 原因 → 該使用者 dislikes；reported_error → 審核佇列；applied/awarded → 權重校正 |

---

## 10. 審核佇列 `review_items`

| 欄位 | 允許值 | 說明 |
| --- | --- | --- |
| kind | `classification` / `core_field` / `condition_no_match` / `validation_failed` / `inferred` / `user_reported` / `attribute_proposal` | |
| benefit_id / rule_id / raw_document_id | | |
| suggested | json | 系統建議值 |
| excerpt | str | 對應原文 |
| action | `accept` / `edit` / `mark_synonym` / `approve_attribute` / `reject` | 審核操作 |
| resolved_by / resolved_at | | |
