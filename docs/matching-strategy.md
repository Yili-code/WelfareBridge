# 申請者 × 補助內容 媒合方法（收斂版）

> 2026-09 更新：目前的媒合改為「資格骨幹 + 分層顯示」，設計與回測數字見 [資格骨幹與分層媒合](eligibility-core.md)。本文保留早期分析。

目標：在「只用官方原文、缺資料不判不符合、結果可解釋」的前提下，把媒合準度拉高。
本文以目前資料庫（87 筆獎助、574 條資格規則）的實際數字為依據，列出方法與優先順序。

---

## 0. 一句話結論

準度瓶頸不在關鍵字、也不在媒合引擎的邏輯，而在**規則層**：574 條規則有 222 條（39%）是 `complex`，媒合時一律 `unknown`；其中至少 134 條是固定句型，可以規則化。
最有效的三件事依序是：**complex 規則結構化 → 身分本體一致化 → Profile 欄位補齊**。LLM 應從「媒合時判斷」移到「解析時結構化」，媒合時只處理殘餘。

---

## 1. 先定義「準」——沒有測試集就沒有準度

| 指標 | 定義 | 目標 |
| --- | --- | --- |
| 高度符合精確率 | 被判 `high_match` 的，人工確認真的符合的比例 | ≥ 0.95 |
| 可申請召回率 | 人工判定可申請的，被判為 `high` 或 `possible` 的比例 | ≥ 0.95 |
| 誤拒率 | 人工判定可申請，卻被判 `not_match` 的比例（最傷使用者） | ≤ 0.02 |
| 可判定率 | 在完整填寫 profile 下，結果不是 `insufficient_data` 的比例 | ≥ 0.90 |
| 平均追問題數 | 動態追問到 `complete=True` 的平均題數 | ≤ 5 |

做法：
1. 手工建 **黃金測試集**：30～50 組（user profile, scholarship, 人工判定 + 理由），涵蓋每種身分、每個縣市限制、夜間部／在職專班、已領其他獎學金等邊界案例。
2. 寫成 `tests/test_matching_gold.py` 參數化測試，每次改 extractor / rule_engine / engine 都跑。
3. 每個方法改動做消融（開／關比較），只保留真的讓指標上升的改動。

---

## 2. 現況診斷（以 demo_seed.json 計算）

| 項目 | 數字 | 意義 |
| --- | ---: | --- |
| 規則總數 | 574 | |
| simple / complex | 352 / 222 | complex 全部 unknown，佔 39% |
| complex 中「限制句」(`restriction_*`) | 126 | 整句原文塞進 `identity.tags not_in null`，沒有可判斷的 field/value |
| complex 中「內文提到的身分」(`identity_mentioned`) | 81 | 身分只在內文出現，無法確定是必要條件 |
| 有 ≥1 complex 規則的獎學金 | 72 / 87 | 大多數公告都有「需進一步確認」 |
| simple 群組 < 2 的獎學金 | 14 | 現行 `MIN_GROUPS_FOR_HIGH_MATCH=2` 下永遠不可能 `high_match` |
| 規則欄位分布 | identity.tags 316、education.level 82、average_score 62、city 32、conduct 28、duration 25、age 17、income 6 | 身分是最大宗，本體一致性直接決定準度 |
| 規則中出現但 profile 無法回答的身分 | 榮民子女 4、弱勢學生 5、特定疾病 3、客家 1、失依兒少 1、勞工子女 1 | 永遠 unknown |

complex 規則句型統計（regex 粗分，一條可命中多類）：

| 句型 | 條數 | 該怎麼處理 |
| --- | ---: | --- |
| 排除學制（夜間部／進修部／在職專班／空中大學／學分班／軍警校） | 42 | 新欄位 `education.program_type`，`not_in` |
| 已領其他獎學金／公費／擇一請領 | 41 | 新欄位 `financial.receiving_other_scholarship`，`= false` |
| 身分（特殊境遇／榮民／弱勢／僑生／客家…） | 37 | 身分本體擴充後轉 simple |
| 前一學期／學年成績 | 14 | 多為成績條件的措辭變體；已有 simple 規則者丟棄重複 |
| 證明文件來源（村里長／公所出具） | 10 | 不是資格，是文件要求 → 歸 `required_documents`，不產規則 |
| 逾期／證件不齊／不予受理 | 10 | 程序條款 → 不產規則 |
| 延長修業／重修／補修 | 9 | 新欄位 `education.extended_study`，`= false` |
| 研究所修業第 N 年以上 | 8 | `education.grade <= N`（限 master / doctoral） |
| 名額／擇優 | 3 | 非資格 → 加註「擇優錄取」，不產規則 |
| 未命中任何句型 | 88 | 留給解析時 LLM 結構化（見 4.6） |

程序條款（約 23 條）目前每條都是權重 0.5 的 complex 群組，會**拉低分母**、並在結果頁堆出一串「需進一步確認」。這些應該在 extractor 就不產生規則。

---

## 3. 媒合架構：四層，各層責任分明

```text
L0 前置過濾     status != expired、canonical_only、截止日未過
L1 硬條件       education.level / program_type / city / age / nationality
                → 只有這層能產生 not_match；只接受 confidence ≥ 0.8 且 inferred=false 的 simple 規則
L2 軟條件計分   成績、所得、身分 OR 群組、設籍月數
                → 決定 high_match / possible_match；score 依鑑別力與信心加權
L3 語意殘餘     解析時未能結構化的 complex 條件
                → LLM 只能「升級為 match」或「加註提醒」，單獨不能拒絕；無 LLM 時 unknown
```

現行引擎已經是「同組 OR、不同組 AND、unknown 不拒絕」，這個骨架不用改；改的是餵進去的規則品質與各層權重。

---

## 4. 方法清單（依預期效益排序）

### 4.1 complex 規則結構化（效益最大）

- 在 `services/extractor.py` 加 **句型庫**（pattern library）：每個句型 = regex + 對應 field / operator / value 產生器 + 必附 `source_excerpt`。以第 2 節的表為起點。
- 程序條款（逾期、證件、名額、文件來源）改為只寫入 `restrictions` / `required_documents`，**不產生規則**。
- 對 `identity_mentioned`（81 條）加上下文判斷：句子含「限」「須」「應」「僅」「以…為限」→ 必要條件（simple）；含「優先」「酌予」「得」→ 加分條件，不當資格規則，只在說明中提示。
- 殘餘 88 條交給 **解析時 LLM**（不是媒合時）：輸出仍必須通過 `schema_validator`（field 白名單、摘錄在原文、數字在摘錄），結果進 `needs_review` 由人工放行。
- 預期：complex 從 222 降到約 60 以下；72 筆「有 complex」的獎學金大部分變成可完整判定。

### 4.2 身分本體（identity ontology）一致化

現況三處各自維護、彼此不一致：`rule_engine.IDENTITY_EQUIVALENTS`、`catalog.TAG_TO_FIELD`、`catalog.FIELD_CATALOG["identity.tags"].options`。

- 改成單一設定檔 `benefit_crawler/config/identity_ontology.yaml`，每個標籤記：canonical 名稱、同義詞（給 extractor 與 profile_parser）、對應 profile 欄位、追問文字、隱含關係。三個模組都讀它。
- 隱含關係要能寫「有 A 就算有 B」：`低收入戶 ⇒ 清寒`、`低收入戶 / 中低收入戶 / 特殊境遇 / 身心障礙 / 原住民 ⇒ 弱勢學生`（依教育部弱勢助學定義寫明依據）。
- 補 profile 欄位：`identity.veteran_family`（榮民子女）、`identity.special_circumstances`（特殊境遇家庭）、`identity.hakka`、`identity.overseas_chinese`（僑生）、`identity.orphan`（失依兒少）。
- 規則裡「身分 A 或 B」應該用 `in [A, B]` 一條，而不是拆成同 group 的多條 `contains`，讓 UI 說明更清楚。

### 4.3 Profile 欄位補齊與追問策略

新增欄位（依規則需求頻率）：

| 欄位 | 覆蓋規則 | 問法 |
| --- | ---: | --- |
| `education.program_type`（日間部／夜間部／進修部／在職專班／空中大學／學分班） | 42 | 單選，預設日間部但仍要確認 |
| `financial.receiving_other_scholarship`（本學期已領政府獎助／公費） | 41 | 是／否／不確定 |
| `education.extended_study`（延長修業／重修中） | 9 | 是／否 |
| `education.school_city`（就讀學校所在縣市） | 少量，但地方政府公告常見「就讀本市學校」 | 城市選單 |
| `identity.nationality` | 部分排除外籍生 | 單選 |

追問策略（`question_planner` 已依「接近符合的獎學金」加權，保留）再加兩條：
1. **硬條件先問**：level、city、program_type 一題能淘汰最多候選，優先度加乘 2。
2. 布林題提供「不確定」→ 保持 `null`，不強迫使用者猜；猜錯的 false 會造成誤拒。

快速輸入模式：`profile_parser` 補同義詞（「夜校」「在職專班」「進修部」「我有領過 XX 獎學金」）。

### 4.4 規則信心納入判定（防誤拒）

- 現況 `confidence` 與 `inferred` 只顯示、不參與判定。
- 改為：**`not_match` 只能由 confidence ≥ 0.8 且 `inferred=false` 的 simple 規則產生**；否則降為 `unknown`，說明標「此條件為推定，請至官方公告確認」。
- 目前只有 4 條 simple 規則信心 < 0.8（都是縣市推定），代價很小，但把「抽取錯誤直接害使用者錯過」這條路堵住。
- score 以 confidence 加權：match 貢獻 = 權重 × confidence。

### 4.5 計分權重依鑑別力

`education.level` 幾乎人人符合（82 條，大多含 university），卻和「戶籍限基隆市」同權重。建議群組權重：

| 群組 | 權重 | 理由 |
| --- | ---: | --- |
| residence_city、identity_required | 2.0 | 直接決定資格，鑑別力最高 |
| household_income、identity_any | 1.5 | 決定資格，但常是擇一 |
| academic_*、age、residence_duration | 1.0 | 門檻型 |
| education | 0.5 | 幾乎不篩人 |
| complex（殘餘） | 0.5 | 維持現狀 |

- 狀態仍由規則決定（L1 不符 → `not_match`），score 只負責 `high / possible` 門檻與同狀態內排序。
- `MIN_GROUPS_FOR_HIGH_MATCH=2` 改成「已符合群組的鑑別力權重總和 ≥ 2.5」，讓只有「戶籍 + 身分」兩條但都高鑑別力的公告能成為 `high_match`，同時仍擋住「只符合教育階段」的情況。目前有 14 筆公告在舊規則下永遠無法 `high_match`。

### 4.6 LLM 用法收斂

| 時機 | 任務 | 模型 | 特性 |
| --- | --- | --- | --- |
| 解析時（離線） | 把殘餘 complex 條件結構化成 field/operator/value | `claude-opus-5` | 量小、要準、可人工審核、結果進資料庫 |
| 媒合時（線上） | 判斷解析時仍無法結構化的條件 | `claude-sonnet-5` | 量大、任務窄、需快取 |

媒合時的具體改法：
- **每筆獎學金一次呼叫**，把該筆所有殘餘 complex 條件一起送（現在是每條一次），輸出逐條結果；同一公告內判斷一致、成本降數倍。
- 快取 key = (scholarship_id, rules_hash, profile_hash)，同一使用者反覆比對不重算。
- 現有保護全部保留：只能輸出三態、`source_text` 必須在原文、否則降 unknown。再加一條：**LLM 的 `not_match` 最多把狀態降到 `possible_match` 並標示**，不直接拒絕。
- **不建議**用向量相似度做資格媒合：87 筆可全量逐條評估，embedding 對「設籍滿 6 個月」這種條件沒有精確度可言。它只適合自由文字搜尋，或 0 條規則的公告做 fallback 推薦。

### 4.7 評估與回饋迴路（讓準度可持續）

- 黃金測試集進 pytest（第 1 節）。
- 資料中心加「規則審核」：每條規則可標「正確／錯誤／應為 simple」，錯誤的回饋直接變成句型庫的新案例。
- 結果頁加使用者回饋：「我申請了」「被拒，原因是…」→ 累積真實標籤，定期回頭校正權重與句型。
- 每次改動跑消融：關 LLM、關 4.4、關 4.5 各跑一次黃金集，數字寫進 `docs/generated/`。

---

## 5. 建議執行順序

1. **黃金測試集**（第 1 節）——先有尺，再改東西。
2. **4.1 句型庫 + 程序條款不產規則**——一次動作解決約 130 條 complex，效益最大。
3. **4.2 身分本體 + 4.3 新欄位**——兩者互相依賴，一起做。
4. **4.4 + 4.5 引擎調整**——改動小、風險低，但要有測試集才能證明有效。
5. **4.6 LLM 批次與快取**——在 1～4 之後 complex 數量已少，LLM 成本自然降。
6. **4.7 回饋迴路**——持續。

每一步完成後重跑第 1 節的五個指標，只有指標上升的改動才保留。

---

## 6. 篩選後的排序：哪一個最適合使用者

### 6.0 先分清兩個軸

| 軸 | 問的問題 | 現有欄位 |
| --- | --- | --- |
| 資格確定度（eligibility） | 「符不符合」 | `status`、`score`（第 3～4 節） |
| 適合度（suitability） | 「符合的裡面，哪個最值得先申請」 | 目前沒有，只有 `-score` 與截止日排序 |

現行排序是 `status → -score → end_date`。`score` 是「有多確定符合」，不是「有多值得申請」：一筆只有教育階段一條規則的 5,000 元獎學金，會排在一筆五條規則全符合的 30,000 元獎學金前面。適合度要另外算，資格確定度只用來分層。

### 6.1 資料裡已經有的排序訊號（87 筆）

| 訊號 | 覆蓋 | 目前狀態 | 要做的事 |
| --- | ---: | --- | --- |
| 金額（value / min / max） | 81 | 已結構化，但 `period` 70 筆是「每名」，無法分辨每學期或每學年 | 抽「每學期／每學年／每月／一次」，換算成年化金額 |
| 截止日 | 79 | 已結構化 | 直接用 |
| 名額 | 69 提到 | 只在原文或 `structured_fields`（「預計總名額: 150 名」「未定」） | 抽成 `quota` 整數，抽不到給 null |
| 擇優／審查 vs 符合即發 | 24 / 4 | 未結構化 | 抽成 `award_basis`: `criteria`（符合即發）/ `competitive`（擇優）/ `unknown` |
| 互斥條款（不得兼領／擇一） | 30 | 現在是 complex 規則，會扣分 | 抽成 `exclusive_with`: `government_scholarship` / `same_provider` / `none`，用在組合建議而不是扣分 |
| 申請成本 | 文件 0～9 份；20 筆需村里長／公所證明；32 筆透過學校、47 筆自行申請 | 已有 `required_documents`、`application_method` | 算成本分數 |
| 競爭範圍 | 31 筆限縣市、52 筆民間團體 | 已有 `residence_locations`、`provider_type`、身分限制 | 限制越多 → 競爭者越少 |
| 使用者與門檻的距離 | 成績、所得、設籍月數 | rule engine 有 `user_value` 與 `value` | 算 margin |
| 使用者偏好 | `preferences.minimum_amount`、`preferred_location` | schema 有、沒人用 | 加 `preferred_categories`、`urgency` |

### 6.2 適合度模型：期望價值 × 時效 × 成本 × 偏好

對每一筆已通過篩選（`high_match`，其次 `possible_match`）的獎學金：

```text
expected_value  = 年化金額 × 獲獎機率估計
獲獎機率估計    = 1.0                                  若 award_basis = criteria（符合即發）
                = clamp(名額 / 估計競爭人數, 0.1, 0.9)  若 competitive 且抽到名額
                = 0.5 × 限制係數 × margin 係數          若 competitive 但無名額
    限制係數：全國且無身分限制 0.6；限縣市 0.8；限縣市＋身分 1.0（限制多 = 競爭者少）
    margin 係數：使用者超過門檻 ≥ 10 分／20% 為 1.0；剛好達標 0.7（擇優時邊緣達標勝率低）

urgency         = 截止日在 3 天內 0.3（來不及備件）；3～14 天 1.0；14～60 天 0.8；> 60 天 0.6；已過 0
cost            = 0.1 × 文件數 + 0.3 × 需村里長證明 + 0.2 × 需自行送件（透過學校較省事）
preference_fit  = 1.0；金額低於 minimum_amount 降 0.5；類型在 preferred_categories 升 1.2；地點在 preferred_location 升 1.1

suitability     = expected_value_norm × urgency × (1 − min(cost, 0.6)) × preference_fit
```

`expected_value_norm` 是同一批候選內做 min-max 正規化，讓分數落在 0～1。權重先用上面的預設，之後用第 4.7 節的回饋（申請了／拿到了）校正。

排序規則：
1. 先分層：`high_match` 一層、`possible_match` 一層，不混排（資格確定度優先於適合度）。
2. 層內依 `suitability` 由高到低。
3. 同分依截止日近者優先。

### 6.3 「最適合」不是單筆，是組合

30 筆有互斥條款。使用者真正要的是「這學期申請哪幾個，總收益最大」：

1. 把候選依 `exclusive_with` 建互斥圖：互斥的兩筆不能同時選。
2. 在互斥圖上取「總 expected_value 最大的獨立集」。候選通常 < 20 筆，直接窮舉或貪婪（先選 suitability 最高，移除與它互斥的，重複）即可。
3. 結果頁分兩區：**「建議申請組合」**（互不衝突、總額最高）與 **「其他可申請」**（列出「與 X 互斥，二擇一」）。

### 6.4 一定要給推薦理由

每張卡片顯示為什麼排這裡，否則使用者不信也無法糾正：

```text
🥇 基隆市清寒優秀學生獎學金 — 建議優先
   ✓ 你的成績 82 分高於門檻 80（擇優時略有風險）
   ✓ 限基隆市戶籍＋低收入戶，競爭者少
   ✓ 每學期 5,000 元，10/31 截止（還有 21 天）
   △ 需村里長清寒證明
   ⚠ 與「教育部弱勢助學金」不得兼領
```

同時讓使用者切換排序：**推薦（預設）／金額高→低／截止日近→遠／申請最簡單**。多準則排序沒有唯一正解，把主控權留給使用者，並記錄他們的選擇當作回饋。

### 6.5 實作順序

1. extractor 抽 `quota`、`award_basis`、`exclusive_with`、金額週期（一次改，四個欄位）。
2. `matching/ranking.py`：算 `suitability`，回傳每筆的分項（expected_value、urgency、cost、preference_fit）與理由字串。
3. `engine.match_all` 改成「資格分層 → 層內 suitability 排序」；API 加 `sort` 參數。
4. 互斥組合建議（6.3）。
5. 結果頁顯示分項理由與排序切換；記錄使用者點「我申請了」。

---

## 7. 擴充到其他領域（長照、身心障礙…）：語意比對的正確位置

### 7.0 結論

語意比對（embedding 相似度）適合做「找候選」與「認欄位」，不適合做「判資格」。
「設籍滿 6 個月」「所得低於最低生活費 1.5 倍」「CMS 第 4 級以上」這類條件，相似度只能說明「相關」，不能說明「符合」。
擴充性的問題不在規則引擎，而在「每個領域手寫 regex 與固定 profile 欄位」；該換掉的是這兩件事。

### 7.1 哪些元件擋住擴充

| 元件 | 擴充性 | 處理 |
| --- | --- | --- |
| 規則格式 field / operator / value / evidence | 好 | 保留 |
| rule engine（同組 OR、不同組 AND、unknown 不拒絕） | 好 | 保留 |
| `services/extractor.py` 的 regex | 差 | 降級為加速器，主抽取改 LLM |
| `schemas/profile.py` 固定欄位 | 差 | 改為屬性登錄表 + key-value profile |
| `keyword_rules.yaml` | 差 | 改為分類器（LLM 或 embedding），領域清單是資料 |
| 身分本體 | 中 | 保留為資料，同義詞合併改半自動（7.3） |

### 7.2 屬性登錄表（attribute registry）

一張表取代固定欄位，profile 變成 `{attribute_id: value}`：

```yaml
- id: applicant.age
  type: number
  label: 年齡
  question: 你今年幾歲？
  domains: [all]
  aliases: [年滿, 歲以上, 未滿]
- id: disability.certificate_level
  type: enum
  values: [輕度, 中度, 重度, 極重度]
  label: 身心障礙證明等級
  question: 你的身心障礙證明等級是？
  domains: [disability, long_term_care]
- id: care.cms_level
  type: number
  label: 長照需要等級（CMS）
  question: 照顧管理專員評估的 CMS 等級是第幾級？
  domains: [long_term_care]
- id: household.income_per_capita
  type: number
  unit: TWD/month
  derived: household.income / household.size
  domains: [all]
```

- 新增領域 = 加幾列資料，不改程式。年齡、戶籍、所得、身分在所有領域共用，登錄表成長遠慢於領域數。
- `question_planner` 已是「缺哪個屬性就問哪個」，直接改讀登錄表。
- validator 的欄位白名單就是登錄表；LLM 抽出登錄表外的屬性一律進 `needs_review`。
- operator 小幅擴充：`between`、衍生欄位（`derived` 用固定的四則運算，不做通用表達式）。

### 7.3 語意比對用在「認欄位」（最有價值的位置）

解析時 LLM 抽出條件描述（例如「持中度以上身心障礙證明」）後：
1. 把描述做 embedding，與登錄表每個屬性的 label + aliases + question 的 embedding 比相似度。
2. 相似度高於門檻 → 對到既有屬性（`disability.certificate_level >= 中度`），不自創欄位。
3. 低於門檻 → `needs_review`，由人決定是新屬性還是同義詞；決定後回寫登錄表。
4. 身分本體的同義詞合併（「身障」「身心障礙者」「領有身心障礙手冊」）用同一機制。

這把「每個領域人工維護對照表」變成半自動，是語意比對真正省人力的地方。

### 7.4 語意比對用在「找候選」

資料量從 87 筆變成數千筆時：
1. 每筆補助存一段「目標族群描述」（LLM 由原文產生，附摘錄）的 embedding。
2. 使用者自由描述 → embedding → 取前 50～100 筆。
3. 對這些候選逐條跑規則引擎；未進前 K 的不評估。

這層只影響召回與速度，不影響判定；資料量小時可以整個跳過。

### 7.5 判定層不變

```text
非結構化公告 ──LLM 抽取 + 語意認欄位 + validator──▶ 規則（登錄表屬性）
使用者描述   ──LLM 抽取 + 追問──────────────────────▶ profile（登錄表屬性）
                                     規則引擎（可解釋、可測試）──▶ 符合 / 可能 / 不符合 / 資料不足
                                     殘餘 complex ──LLM 判斷（只能升級或加註）
```

新增一個領域的成本 = 登錄幾個屬性 + 跑一次 LLM 抽取 + 審核 `needs_review`，不需要寫程式。

---

## 8. 符合 ≠ 想要：推薦使用者真正需要的補助

### 8.0 三個問題分開

| 問題 | 看誰 | 章節 |
| --- | --- | --- |
| 符合（eligibility） | 補助的規則 × 使用者條件 | 3～4 |
| 適合（suitability） | 補助的價值、時效、成本 | 6 |
| 想要（intent） | 使用者的需求、偏好、排斥 | 本節 |

目前系統沒有「需求」這個輸入；`preferences` 只有 `minimum_amount` 與 `preferred_location`。

### 8.1 一題問出需求類型

「你現在最需要的是？」四選一，每個選項對應一組第 6.2 節的權重預設：

| 需求類型 `need_type` | 偏好的補助特徵 | 權重偏向 |
| --- | --- | --- |
| `cash_now` 急需一筆錢 | 急難救助、助學金、金額確定、審核快、符合即發 | urgency ×2、獲獎機率 ×2 |
| `reduce_burden` 長期減輕負擔 | 學雜費減免、續領型、每學期核發 | 年化金額 ×2、可續領 +0.3 |
| `honor` 榮譽或履歷 | 擇優獎學金、公家或知名機構、有頒獎 | 機構聲望 +、競爭度不扣分 |
| `service` 需要服務不是錢（長照、身障） | 服務給付、輔具、居家照顧 | benefit_form=service 優先、就近提供者 |

長照與身障領域的起點是「情境」而非「條件」，同一機制直接適用。

### 8.2 抽出「不想要的」

符合但不想要，多半是下列原因；原文都有訊號，需結構化：

| 原因 | 87 筆中的數量 | 新欄位 |
| --- | ---: | --- |
| 得獎後有義務（服務時數、出席典禮、交心得） | 14 | `obligations: [str]` |
| 要面試、推薦函、自傳、讀書計畫 | 21 | `application_effort: low / medium / high` |
| 要交家庭財產、所得清單 | 17 | `requires_financial_proof: bool` |
| 不是現金（減免、服務、實物） | 31 | `benefit_form: cash / waiver / service / in_kind / loan` |
| 貸款 | category `loan` | 預設排最後，需求為 `cash_now` 時才提示 |
| 與已領補助互斥 | 30 | profile 加 `current_benefits: [str]`，互斥者邊際價值 0 |

可選追問「哪些你不想要？」多選：要面試、有服務義務、要交財力證明、貸款。選中者硬過濾或重罰（×0.2）。

### 8.3 從自由文字抽需求

`profile_parser` 多抽兩個屬性，保護同現有規則（摘錄必在使用者文字中）：

| 使用者說 | `need_type` | `urgency` |
| --- | --- | --- |
| 「學費繳不出來」「下週要註冊」 | cash_now | high |
| 「想減輕家裡負擔」 | reduce_burden | normal |
| 「想找個獎學金充實履歷」 | honor | low |
| 「媽媽中風需要人照顧」 | service | high |

### 8.4 呈現：三張卡，不是一個排行

「最好」依需求不同，首頁先給三張各有理由的卡，再列完整清單（排序可切換）：

```text
⚡ 最快拿到錢     基隆市急難救助金   符合即發、7 天內核定、要 3 份文件
💰 金額最高       XX 基金會獎學金    每學年 30,000、擇優、要面試與讀書計畫
🪶 最省力         教育部弱勢助學金   學校統一辦理、免面試   ⚠ 與急難救助金不得兼領
```

每張卡固定三段：為什麼推薦給你（需求 + 條件）、要注意什麼（義務、面試、互斥）、下一步（官方來源、截止日）。

### 8.5 從行為學，不做協同過濾

收集三個訊號：點開、「我申請了」、「不感興趣」+ 原因（金額太少／太麻煩／不想面試／已經有了）。
- 「不感興趣的原因」直接回寫成該使用者的負面偏好，下次比對即生效。
- 「我申請了」用來校正 8.1 的權重預設（哪種需求的人實際選了什麼）。
- 使用者少、資料敏感：規則預設 + 簡單權重校正即可，不上推薦模型。

### 8.6 實作順序

1. profile 加 `need_type`、`urgency`、`current_benefits`、`dislikes`；前端加一題需求、一題（可選）排斥。
2. extractor 抽 `benefit_form`、`obligations`、`application_effort`、`requires_financial_proof`。
3. `ranking.py` 依 `need_type` 套權重預設、依 `dislikes` 過濾或重罰。
4. 結果頁改為三張卡 + 清單；加「不感興趣 + 原因」。

---

## 9. 聊天機器人：用工具的對話代理，而不是自由判斷的 LLM

### 9.0 分工

| 角色 | 負責 | 不負責 |
| --- | --- | --- |
| LLM（對話代理） | 聽懂自由文字、把該問的題講得自然、解釋結果、回答追問 | 決定問什麼、判定符不符合、發明條件 |
| `plan_questions`（確定性） | 依資訊增益決定下一題 | 措辭 |
| `rule engine` + `rank` | 符合 / 適合 / 想要 | 對話 |

後端已有對應 API：`POST /api/profile/parse`、`POST /api/profile/questions (mode=dynamic)`、`POST /api/matching`。機器人是這三個工具的編排層。

### 9.1 代理迴圈

```text
使用者說話
 ├─ extract_profile(text)      抽屬性；每個值附使用者原話摘錄；enum 對登錄表正規化；抽不到 → null
 ├─ match(profile)             每筆狀態、missing_fields、failed_conditions
 ├─ 可停止？ ── 是 ─▶ rank(profile, need_type) ─▶ 三張卡 + 清單（第 8.4 節）
 └─ 否 ─▶ plan_questions(profile, matches) ─▶ 1～3 個候選題 + 各自解鎖幾筆
          └─ LLM 選 1 題（可合併 2 題）講成自然語句，並說明為什麼問 ─▶ 回到開頭
```

工具介面（給 LLM 的 tool definitions）：

| 工具 | 輸入 | 輸出 |
| --- | --- | --- |
| `extract_profile` | 使用者文字、目前 profile | 新增／更新的屬性 + evidence |
| `match` | profile | 每筆 status、score、missing_fields、failed_conditions |
| `plan_questions` | profile、matches、skipped | 候選題（attribute、question、options、解鎖筆數、資訊增益） |
| `rank` | profile（含 need_type、dislikes） | 三張卡 + 排序清單 + 理由 |
| `explain` | scholarship_id | 該筆的條件逐項狀態、原文摘錄、來源 |
| `what_if` | profile 修改 | 重跑 match 的差異（反事實） |

### 9.2 「有目的」＝期望資訊增益

把 `question_planner` 的優先度從「幾筆缺這欄位」升級為：

```text
對每個缺的屬性 a：
  列舉可能回答 v（布林：是/否；enum：各值；數值：依候選規則門檻分桶）
  對每個 v：模擬填入 → 重跑候選 → 計算狀態翻轉（possible→high 或 →not_match）的候選適合度總和
  gain(a) = Σ_v P(v) × 翻轉量(v)        P(v) 先用均勻，之後用歷史回答分布
選 gain 最高者；硬條件屬性（level、city、program_type）額外 ×2
```

確定性、可解釋；LLM 拿到的是「問設籍時間可以確定 3 筆」這種摘要，再講成人話。

### 9.3 LLM 讀「大量補助」的正確形式

- 補助已結構化為規則 → 規則決定登錄表裡有哪些屬性 → 屬性決定能問什麼。
- 每輪 context 只放：候選摘要（筆數、狀態分布）、planner 的候選題與解鎖數、已確認的 profile。不放 87 份原文。
- 需要引用原文時用 `explain` 工具即時取，附摘錄。

### 9.4 對話策略

1. 第一句開放式：「說說你的情況和現在最需要什麼」→ 一次抽多個屬性 + `need_type`。
2. 硬條件先問（level、city、program_type）。
3. 問需求類型（第 8.1 節），再問鑑別力高的屬性。
4. 每輪回報進度：「目前 12 筆可能符合，再 2 題就能確定」。
5. 停止條件：下一題的 gain 低於門檻、或高度符合已 ≥ 3 筆、或已問 7 題。

### 9.5 護欄

- LLM 不判資格；所有狀態來自 `match` 回傳，LLM 只轉述。
- 只能問登錄表內的屬性；對不到的內容記入 `notes`，不進判定。
- 抽出的值先回述確認再用於硬過濾（避免抽錯造成誤拒）。
- 「不知道／不想說」→ null，維持資料不足；敏感題先說明用途、允許跳過。
- 每個屬性值存來源句子；結果頁可回答「為什麼認為我是低收入戶」。
- 使用者文字中若含指令性內容（要求改規則、要求判定符合），視為資料不執行。

### 9.6 學什麼、不學什麼

- 學：問題順序、措辭、`P(v)` 的回答分布、哪些題常被跳過 → 調 planner 權重與 prompt 範例。
- 不學：判定邏輯。判定永遠以第 1 節黃金測試集驗證。

### 9.7 結束後的追問

| 使用者問 | 工具 |
| --- | --- |
| 「為什麼 X 不符合？」 | `explain` → failed_conditions + 原文摘錄 |
| 「如果我成績到 85 呢？」 | `what_if` → 差異清單 |
| 「這個要準備什麼？」 | `explain` → required_documents、application_method、截止日 |

---

## 10. 資格篩選之後：從 50 筆到推薦的漏斗

第 3～4 節的規則引擎把 1000 筆篩成約 50 筆「符合資格」。之後的處理分五段，前兩段是再篩（確定性、不計分），後三段是排序與呈現。方法在第 6、8 節，這裡是執行總覽。

| 段 | 做什麼 | 依據欄位 | 示意 |
| --- | --- | --- | ---: |
| A 實際不能申請 | 截止日已過或 < 3 天來不及備件；與 `current_benefits` 互斥；貸款且 need_type ≠ cash_now | `application_end`、`exclusive_with`、`category` | 50 → 35 |
| B 需求分流 | `benefit_form` 與 `need_type` 不合者移到「其他」；`dislikes` 命中者硬過濾或 ×0.2 | `need_type`、`benefit_form`、`dislikes`、`obligations`、`application_effort` | 35 → 20 |
| C 適合度計分 | 期望價值 × 時效 × 成本 × 偏好，權重依 `need_type` 套預設（6.2、8.1） | 金額、名額、擇優、文件、面試 | 20 有序 |
| D 組合最佳化 | 互斥圖上取總期望價值最高的獨立集（6.3） | `exclusive_with` | 建議組合 3～5 |
| E 呈現 | 三張卡 + 建議組合 + 清單可切換排序（8.4） | | 使用者選 |

A、B 移出的項目仍列在「其他可申請」並註明原因，不是消失。

### 10.1 排序分不出高下時：偏好題

第 9 節的機器人問的是資格題。這裡可再問 1～2 題，但只在答案會改變前 5 名時才問。
計算與 9.2 相同，目標從「翻轉資格狀態」改成「改變前 K 名的排序」：

| 前幾名的差異在 | 問 |
| --- | --- |
| 一個要面試、一個不用 | 你願意面試嗎？ |
| 一個 3 天後截止、一個下個月 | 你多快需要這筆錢？ |
| 金額相近但一個有服務義務 | 你介意得獎後要做服務時數嗎？ |
| 一個現金、一個減免 | 你比較需要現金還是減免學費？ |

前幾名在該欄位無差異 → 不問，直接出結果。

### 10.2 排序所需的結構化欄位（解析時抽好）

| 欄位 | 用途 | 段 |
| --- | --- | --- |
| `amount_annualized`、`amount.type` | 期望價值 | C |
| `application_end`、`decision_lead_days` | 時效 | A、C |
| `quota`、`award_basis` | 獲獎機率 | C |
| `required_documents` 數、`requires_interview`、`requires_office_proof`、`application_channel` | 申請成本 | B、C |
| `benefit_form` | 需求分流 | B |
| `obligations` | 排斥過濾 | B |
| `exclusive_with` | 互斥 | A、D |
| `renewable` | 減輕負擔型需求 | C |

### 10.3 仍然太多時：分群而非再砍

同類型合併成一組顯示（「6 筆各縣市清寒獎學金，你只符合基隆那筆」「同一基金會 4 個科系別」），使用者看到 5～8 組，展開才是清單。分群鍵：`canonical_id`、provider、category + residence 限制。

### 10.4 回饋

- 使用者在 E 段的行為（點開、申請、不感興趣 + 原因）回寫個人偏好，下次從 B 段生效。
- 跨使用者統計校正 C 段各 `need_type` 的權重預設。

---

## 11. Schema 會不會一直長：三種欄位，只有一種會長，而且長的是資料

| 種類 | 內容 | 成長 | 放哪 |
| --- | --- | --- | --- |
| 核心 | title、provider、source、original_text、amount、application_period、status | 不會 | 固定 schema |
| 給付特徵 benefit meta | `benefit_form`、`amount_annualized`、`quota`、`award_basis`、`application_end`、`application_effort`、`obligations`、`exclusive_with`、`renewable` | 設計一次即封閉（約 10 欄） | 固定 schema |
| 資格屬性 | 年齡、戶籍、成績、身障等級、CMS 等級… | 隨領域增加 | 屬性登錄表（資料），規則引用 `attribute_id` |

給付特徵描述「任何補助怎麼運作」（錢或服務、何時截止、多難申請、能否兼領），跨領域相同，所以能封閉。第 6、8、10 節新增的欄位全屬此類。
資格屬性描述「誰能申請」，隨領域長，但在第 7 節的設計中是登錄表的一列資料：不改 schema、不改程式、validator 白名單即登錄表。

### 11.1 入庫時只抽「篩得動」的最小集合

| 用途 | 何時抽 | 欄位 |
| --- | --- | --- |
| 在全量（1000 筆）上篩選 | 入庫時 | 資格規則、`application_end`、`benefit_form`、`exclusive_with`、`status` |
| 只在候選（50 筆）上排序 | 即時抽 + 快取回寫 | `obligations`、`requires_interview`、`required_documents` 數、`quota`、`award_basis`、`renewable` |

候選集小，即時抽的成本可忽略；抽完存回該筆，之後不再抽。

### 11.2 登錄表新增屬性時，舊資料不用動

- 舊公告沒有新屬性的規則 → 媒合時 unknown → 本來就不拒絕，系統照常。
- 要補齊時對舊資料增量重跑抽取（`--pipeline-only`），不改結構。
- `original_text` 永遠保留，任何新欄位都能從原文補抽。

### 11.3 最終形狀

```text
scholarship
├─ core            固定
├─ benefit         固定約 10 欄，跨領域相同
├─ rules[]         {attribute_id, operator, value, group_id, complexity, evidence}
│                  attribute_id 必在 attribute_registry.yaml
└─ original_text   永遠保留

attribute_registry.yaml   會長的只有這個檔，且是資料
user_profile              {attribute_id: value, evidence}  + need_type / urgency / dislikes / current_benefits
```
