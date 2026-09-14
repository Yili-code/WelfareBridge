# 實例：一筆公告從擷取、填入到比對

以資料庫裡真實的一筆公告「基隆市高級中等以上學校清寒優秀學生獎學金」（來源：教育部圓夢助學網，機關：基隆市政府）走完整流程。
第 1～3 節是目標設計（[data-model-v2.md](data-model-v2.md)）的填入結果；第 4 節的比對輸出是**用現有引擎實際跑出來的**（2026-09-10，77 筆 canonical 公告，無 LLM），並標出現況與目標的差異。

---

## 0. 原文（節錄）

```text
機關單位名稱：基隆市政府
學制：研究所、大專院校、五專前三年、高中職
成績：智育: 不限 德育(操行): 80 體育: 65 平均: 80
獎助身分：低收入戶學生、中低收入戶學生
獎助資格：清寒
戶籍地限制：基隆市
申請方式：向就讀學校申請
限制條件：一、申請資格：
設籍基隆市6個月以上，就讀國內公私立高級中學以上學校、專科學校、大學校院家境清寒之學生，
符合下列各款之標準且未享有公費待遇得申請本獎學金:
（一）成績標準：1. 前一學年學業成績總平均80分以上，其餘各科成績達65分以上。
              2. 德行評量之獎懲紀錄相抵後，未受警告以上懲處或操行成績80分以上(甲等)。
（二）家境清寒標準:經里辦公處證明家境清寒或列為低收入戶經區公所證明者。
二、獎勵金額及名額：
（一）高級中等學校及五專制專科學校1-3年級學生以140名為限，每學年每名3,000元。
（二）大專院校及二年制專科學校及五專制專科學校四、五年級學生35名，每名5,000元。
三、申請期間自9月1日起至9月30日止，逾期不予受理。
預計總名額: 175 名
申請期間：115/09/01～115/09/30
申請文件：（一）獎學金申請表 （二）前一學年成績證明書 （三）操行成績證明書 （四）在學證明
（五）戶口名簿或身分證影本。未享公費待遇證明書。（六）低收入戶、中低收入戶或其他家境清寒證明。
申請程序：由就讀學校先行初審資格後，由就讀學校統一造冊，並依申請學生成績高低順序裝訂相關表件。
```

---

## 1. 擷取：分類與 core + benefit meta

### 1.1 分類（3.2）

```json
{"is_benefit": true, "domain": "education", "category": "scholarship", "confidence": 0.97,
 "evidence": "獎學金名稱：基隆市高級中等以上學校清寒優秀學生獎學金"}
```

### 1.2 core + benefit meta（3.3，每欄附摘錄）

| 欄位 | 值 | 摘錄 |
| --- | --- | --- |
| title | 基隆市高級中等以上學校清寒優秀學生獎學金 | 頁面標題 |
| provider / provider_type / provider_region | 基隆市政府 / local_government / 基隆市 | 機關單位名稱：基隆市政府 |
| benefit_form | cash | 每學年每名3,000元 |
| amount | {type: tiered, tiers: [{when: education.level in [senior_high, vocational_high, junior_college≤3], value: 3000}, {when: education.level in [university, junior_college≥4], value: 5000}], unit: TWD, period: year} | 二、獎勵金額及名額（一）（二） |
| amount_annualized | 依使用者學制取 3,000 或 5,000 | 系統推導 |
| application_period | {start: 2026-09-01, end: 2026-09-30, rolling: false} | 申請期間：115/09/01～115/09/30 |
| award_basis | competitive | 依申請學生成績高低順序裝訂相關表件；以140名為限 |
| quota | 175（分層 140 / 35） | 預計總名額: 175 名 |
| application.channel | school | 向就讀學校申請 |
| application.effort | medium | 6 份文件、需公所或里辦公處證明、無面試 |
| application.requires_office_proof | true | 經里辦公處證明家境清寒或列為低收入戶經區公所證明者 |
| application.requires_financial_proof | false | 無財產／所得清單要求 |
| application.requires_interview | false | 無 |
| obligations | [] | 無 |
| exclusive_with | [public_funding] | 未享有公費待遇 |
| renewable | null | 原文未提 |
| target_population_text | 設籍基隆市、高中職以上在學、家境清寒或低收／中低收入戶、成績平均 80 分以上的學生 | 各句附摘錄 |

**與現況的差異**：現況 `amount.period` 是「每名」，無法年化；名額、擇優、公費互斥都留在原文沒有結構化。

---

## 2. 擷取：條件句 → 登錄表 → 規則

### 2.1 條件句（3.4）

| # | 條件句 | role | 摘錄 |
| --- | --- | --- | --- |
| c1 | 設籍基隆市 6 個月以上 | required | 設籍基隆市6個月以上 |
| c2 | 就讀國內公私立高級中學以上學校、專科學校、大學校院 | required | 就讀國內公私立高級中學以上學校、專科學校、大學校院 |
| c3 | 家境清寒（里辦公處證明）或低收入戶（區公所證明） | required | 經里辦公處證明家境清寒或列為低收入戶經區公所證明者 |
| c4 | 未享有公費待遇 | required | 且未享有公費待遇得申請 |
| c5 | 前一學年學業成績總平均 80 分以上 | required | 前一學年學業成績總平均80分以上 |
| c6 | 其餘各科成績達 65 分以上 | required | 其餘各科成績達65分以上 |
| c7 | 未受警告以上懲處或操行成績 80 分以上 | required | 未受警告以上懲處或操行成績80分以上(甲等) |
| c8 | 逾期不予受理 | procedural | 逾期不予受理 |
| c9 | 名額 140 / 35 名 | meta | 以140名為限 … 35名 |

c8、c9 標為程序與 meta，**不產生規則**（現況把它們做成兩條 complex 規則，每筆結果都多兩行「需進一步確認」）。

### 2.2 對登錄表（3.5）

| 條件句 | embedding 前 3 候選 | LLM 選定 | operator / value |
| --- | --- | --- | --- |
| c1 | residence.household_city 0.91、residence.duration_months 0.88、residence.current_city 0.74 | 兩個屬性（一句含兩條件） | household_city in [基隆市]；duration_months >= 6 |
| c2 | education.level 0.93 | education.level | in [senior_high, vocational_high, junior_college, university, master, doctoral] |
| c3 | identity.economic_hardship 0.90、identity.low_income 0.89、identity.middle_low_income 0.86 | identity.tags（身分群組） | in [清寒, 低收入戶, 中低收入戶]（結構化欄位「獎助身分」含中低收） |
| c4 | financial.receiving_public_funding 0.87、financial.receiving_other_scholarship 0.79 | financial.receiving_public_funding | = false |
| c5 | academic.average_score 0.95 | academic.average_score | >= 80 |
| c6 | academic.subject_min_score 0.92 | academic.subject_min_score | >= 65 |
| c7 | academic.conduct_score 0.90、conduct.no_disciplinary_record 0.85 | 兩屬性同組 OR | conduct_score >= 80 ∨ no_disciplinary_record = true |

c4 的屬性 `financial.receiving_public_funding` 若登錄表尚無，走「提案佇列」：LLM 提議 `{id, type: boolean, label: 是否享有公費待遇, question: 你目前是否為公費生？}`，核准前 c4 保持 complex。

### 2.3 規則（3.6～3.7 驗證後）

```json
[
  {"attribute_id": "education.level", "operator": "in", "value": ["senior_high","vocational_high","junior_college","university","master","doctoral"], "group_id": "education", "confidence": 0.95, "evidence": {"excerpt": "學制：研究所、大專院校、五專前三年、高中職", "extractor": "structured_field"}},
  {"attribute_id": "residence.household_city", "operator": "in", "value": ["基隆市"], "group_id": "residence", "confidence": 0.98, "inferred": false, "evidence": {"excerpt": "戶籍地限制：基隆市"}},
  {"attribute_id": "residence.duration_months", "operator": ">=", "value": 6, "unit": "months", "group_id": "residence_duration", "confidence": 0.9, "evidence": {"excerpt": "設籍基隆市6個月以上"}},
  {"attribute_id": "identity.tags", "operator": "in", "value": ["清寒","低收入戶","中低收入戶"], "group_id": "identity", "confidence": 0.95, "evidence": {"excerpt": "獎助身分：低收入戶學生、中低收入戶學生"}},
  {"attribute_id": "financial.receiving_public_funding", "operator": "=", "value": false, "group_id": "public_funding", "role": "exclusion", "confidence": 0.85, "evidence": {"excerpt": "且未享有公費待遇得申請"}},
  {"attribute_id": "academic.average_score", "operator": ">=", "value": 80, "unit": "score", "group_id": "academic_average", "confidence": 0.98, "evidence": {"excerpt": "平均: 80"}},
  {"attribute_id": "academic.subject_min_score", "operator": ">=", "value": 65, "unit": "score", "group_id": "academic_subject_min", "confidence": 0.9, "evidence": {"excerpt": "其餘各科成績達65分以上"}},
  {"attribute_id": "academic.conduct_score", "operator": ">=", "value": 80, "unit": "score", "group_id": "conduct", "confidence": 0.98, "evidence": {"excerpt": "操行成績80分以上(甲等)"}},
  {"attribute_id": "conduct.no_disciplinary_record", "operator": "=", "value": true, "group_id": "conduct", "confidence": 0.85, "evidence": {"excerpt": "未受警告以上懲處"}}
]
```

驗證通過項目：9 個 attribute_id 都在登錄表（c4 待核准前為 complex）；每個數字都在摘錄裡；每個摘錄都在原文裡；operator 與型態相容。
結果：**9 條 simple、0 條 complex**（現況：9 條 simple + 2 條 complex 噪音，且漏掉「公費」與「未受懲處」兩個條件）。

---

## 3. 使用者側：對話 → profile

機器人第一句：「說說你的情況和現在最需要什麼？」
使用者：「我是基隆人，海洋大學資工大二，平均82分，學費有點吃緊」

`extract_profile` 實際輸出（現有 profile_parser）：

```json
{"education": {"level": "university", "school": "國立臺灣海洋大學", "department": "資訊工程", "grade": 2, "school_type": "public"},
 "location": {"household_registration_city": "基隆市"},
 "academic": {"average_score": 82}}
```

目標設計再多抽：`need_type: cash_now`（摘錄「學費有點吃緊」）、`urgency: normal`。
機器人回述確認：「你是基隆市戶籍、海洋大學大二、上學期平均 82，對嗎？」→ 使用者「對」→ 三個值 `confirmed: true`。

---

## 4. 比對（實際執行結果）

### 4.1 第一輪：只有快速輸入的三個值

全庫 77 筆：

| 狀態 | 筆數 |
| --- | ---: |
| high_match | 1 |
| possible_match | 44 |
| insufficient_data | 3 |
| not_match | 29 |

目標公告：`possible_match`，score 0.667

```text
✓ 教育階段：高中／高職／五專／大專院校／碩士／博士
✓ 戶籍地：基隆市
✓ 學業平均成績 ≥ 80
？ 尚未提供：設籍時間（月）
？ 尚未提供：操行成績
？ 尚未提供：最低單科成績
？ 尚未提供：特殊身分
△ 需進一步確認：限制：（一）高級中等學校及五專制專科學校1-3年級學生以140名為限…   ← 現況噪音，目標設計不會出現
△ 需進一步確認：限制：三、申請期間自9月1日起至9月30日止…                       ← 同上
```

追問規劃（現有 planner，依「幾筆缺這欄位」加權）：

| 順位 | 問題 | 影響筆數 | 優先度 |
| --- | --- | ---: | ---: |
| 1 | 你上一學期的操行成績約幾分？ | 15 | 12.5 |
| 2 | 你今年幾歲？ | 16 | 12.1 |
| 3 | 你是否具有低收入戶身分？ | 12 | 9.7 |

目標設計（期望資訊增益）會把「低收入戶」提前：它是身分類硬條件，一題能讓約 12 筆從 possible 翻成 high 或 not，翻轉量高於「年齡」（年齡只影響少數民間獎學金的上限）。機器人講法：「你戶籍在基隆、成績也過門檻，有幾筆清寒獎學金要看身分，你有低收入戶或中低收入戶證明嗎？」

### 4.2 第二輪：回答設籍 20 年、低收入戶、操行 85

| 狀態 | 筆數 |
| --- | ---: |
| high_match | 16 |
| possible_match | 23 |
| insufficient_data | 3 |
| not_match | 35 |

目標公告：`possible_match`，score 0.889，只剩「最低單科成績」未提供。
下一題（現況）：年齡（影響 9 筆）、家庭年所得（5 筆）、最低單科（1 筆）。
目標設計：最低單科只影響 1 筆，但那筆已經 0.889 且是使用者所在縣市的公家獎學金（適合度高），增益 = 翻轉量 × 適合度，仍可能排前面；同時把 c4「你是否為公費生」列入（現況沒有這條規則，所以不會問）。

### 4.3 第三輪：回答最低單科 70、非公費生

目標公告：**`high_match`**，score 0.944（目標設計下為 1.0，因為沒有 complex 噪音）

```text
✓ 教育階段  ✓ 戶籍地：基隆市  ✓ 設籍滿 6 個月  ✓ 學業平均 ≥ 80
✓ 操行 ≥ 80  ✓ 各科 ≥ 65  ✓ 身分：清寒（由低收入戶推得）  ✓ 身分：低收入戶
```

全庫此時 high_match 17 筆，這就是「篩選後的候選集」。

### 4.4 篩選後漏斗（對 17 筆 high_match）

**A 實際不能申請**（今天 2026-09-10）

| 公告 | 截止 | 處理 |
| --- | --- | --- |
| 正德基金會秋季獎學金 | 09-10（今天） | 移到「其他」：來不及備件 |
| 趙自強基金會熱河省學生獎助金 | 10-31 | 移到「其他」：目標族群為海外來台學生，需 `target_population` 或身分規則排除（現況規則只抽到教育階段，所以誤判 high） |
| 其餘 15 筆 | 09-15 ～ 12-31 | 留下 |

**B 需求分流**（need_type = cash_now，dislikes 空）：15 筆皆為現金，全部留下。

**C 適合度計分**（示意三筆；其他筆 benefit meta 未抽時對候選集即時抽）

| 公告 | 年化金額 | 獲獎機率估計 | 時效 | 成本 | suitability |
| --- | ---: | ---: | ---: | ---: | ---: |
| 基隆市清寒優秀學生獎學金 | 5,000 | 0.8（限縣市＋身分，competitive 但 35 名，成績 82 vs 80 邊緣 → 0.7×1.0 限制係數再加名額修正） | 0.8（20 天） | 0.3（6 份文件、需公所證明、學校統一送件） | 中 |
| 鴻海獎學鯨 | 50,000 | 0.4（全國、競爭大，award_basis 待抽） | 0.8（18 天） | 0.5（推估需自傳／推薦，待抽） | 高 |
| 國泰卓越獎助計劃 | 50,000～200,000 | 0.3（全國、擇優、名額待抽） | 0.8（20 天） | 0.6（待抽） | 高 |

期望價值差距大，金額高者即使機率低仍排前；基隆市獎學金勝在「幾乎確定」與「與其他多數獎學金不互斥」。

**D 互斥組合**：基隆市獎學金只與「公費」互斥；民間獎學金多數註明「不得重複領取本會其他獎學金」或無限制 → 三筆可同時申請。

**E 呈現**

```text
💰 金額最高     國泰卓越獎助計劃      5～20 萬、擇優、9/30 截止   ⚠ 競爭大，需準備完整資料
⚡ 最有把握     基隆市清寒優秀學生獎學金  5,000、限基隆市＋低收、9/30 截止、向學校申請
                ✓ 你的條件全部符合   △ 需區公所低收證明   ⚠ 公費生不可申請
🪶 最省力       115學年度大專院校學生獎助學金  10,000、10/16 截止   （文件數待抽）
建議組合：三筆互不衝突，可同時申請；合計期望價值最高。
```

使用者點「為什麼趙自強基金會那筆不適合我？」→ `explain` 回：目標族群「海外來台深造熱河省學生」（摘錄），你的資料不符；規則層目前未抽到此條件，已回報審核。

---

## 5. 這個實例暴露的現況問題（對應 matching-strategy）

| 觀察 | 對應方法 |
| --- | --- |
| 兩條 complex「限制」是名額與申請期間，不是資格 | 第 4.1 節：程序條款不產規則 |
| 「未享有公費待遇」「未受警告以上懲處」沒被抽成規則 | 第 4.1 節句型庫 / data-model 3.4～3.5 條件句流程 |
| 「趙自強熱河省學生」被判 high_match | 目標族群條件未結構化 → 第 4.4 節信心門檻 + target_population 檢查 |
| planner 先問年齡而非低收入戶 | 第 9.2 節期望資訊增益 |
| 金額「每名」無法年化、名額與擇優未結構化 | 第 6.1 節 benefit meta |
| 17 筆 high_match 依 score 排，5,000 元與 200,000 元同分 | 第 6.2 節適合度計分 |
