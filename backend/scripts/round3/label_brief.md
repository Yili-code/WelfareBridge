# 黃金標註集：標註規則（給標註代理）

你會拿到一個批次檔（`batch_XX.txt`），裡面有多份從官方網站爬回的原文。每份以 `##### <id>` 開頭，接著 TITLE / SOURCE / URL / TEXT。
請**逐份完整讀 TEXT**（不是只看標題），為每份文件給出標註。SYSTEM 那一行是系統目前的判斷，**不要參考它**，你要獨立判斷。

## 每份文件要回答
- `id`：照抄。
- `is_benefit`：
  - `yes`：頁面本身描述一項對申請人有具體經濟價值的方案（現金、津貼、補貼、獎助、減免、貸款利息補貼、或有經濟價值的服務如托育／長照／餐飲／交通接送），而且頁面寫出「誰可以申請」或「給什麼」至少其一。
  - `portal`：同一頁整理多項不同方案（總整理、懶人包、專區目錄、福利一覽），各項條件不同，不能當一筆方案。
  - `no`：不收。包括：申請書／表單／切結書／範本；只有附件清單或檔案下載；流程圖；進度查詢；統計、預算決算；FAQ；名單／名冊／窗口；行政公告（修正條文、草案、公聽會、說明會、徵求、招標、得獎、查核督導）；只有段落名的分頁片段（例如整份只是「應備文件」「相關檔案」「洽辦資訊」）；法律本文（xx法、xx條例，只有條文沒有方案）；純新聞稿／活動報導；網站資訊頁；PDF 亂碼；商業金融商品；機構或廠商導向（給服務單位、雇主的補助另計，見下）。
- `kind`：program | portal | form | attachment | flowchart | progress_query | logo | statistics | faq | directory | notice | fragment | garbled | site_info | statute | news | other。
- `category`：主類別（下方 id 之一）；`no`/`portal` 可留空字串。
- `secondary`：次類別清單（頁面也涵蓋的其他類別；可空）。
- `closed`：true 若頁面明說已停辦／不再受理／額度用罄（此時 is_benefit 仍依內容判 yes 或 no，並標 closed）。
- `reason`：一句中文理由，指出你根據原文的哪個線索判斷。
- `confidence`：high | medium | low（low 代表原文不足以判斷）。

## 邊界案例
- 區公所「本所受理業務」列表：只列業務名稱沒有資格與給付 → `portal`（若列多項）或 `no`（若只是選單）。
- 給服務單位、雇主、機構的補助（例如「日照中心導入科技輔具補助計畫」、「僱用獎助」給雇主）：仍是 `yes`（對申請人有經濟價值），category 選最接近者，reason 註明對象是機構／雇主。
- 只有標題像方案、內文只有附件清單：`no`，kind=attachment。
- 法規「辦法／要點」若條文本身寫了資格與給付（例如「xx補助辦法」）：`yes`；純「xx法」「xx條例」：`no`，kind=statute。
- 修正發布、修正條文對照表：`no`，kind=notice，即使裡面引用了資格條文。
- 生育獎勵金／生育津貼 → category `birth_incentive`；育兒津貼（0–5 歲每月）→ `child_allowance`；托育補助（送托）→ `childcare_subsidy`。
- 中低收入老人生活津貼、特別照顧津貼、老人假牙、老人健保費補助、重陽敬老金 → `elderly_allowance`；老人餐飲／日照／安置等服務 → `elderly_service`（長照給付類另有 home_care / day_care 等）。
- 低收／中低收入戶資格說明頁（寫了審核標準與給付項目）→ `yes`，`low_income_allowance`。

## 類別 id（只能用這些）
education：scholarship 獎學金、student_aid 助學金、tuition_waiver 學雜費減免、education_subsidy 就學補助、housing_support 住宿補助（學生宿舍／租屋補助）、emergency_aid_student 學生急難救助、student_loan 就學貸款、study_abroad 留學獎助
youth：youth_employment 青年就業獎勵、youth_entrepreneurship 青年創業、youth_development 青年發展
social_welfare：low_income_allowance 低收入戶生活補助、special_circumstances_aid 特殊境遇家庭扶助、birth_incentive 生育獎勵金、child_allowance 育兒津貼、childcare_subsidy 托育補助、parental_leave_allowance 育嬰留停津貼、emergency_relief 急難救助、elderly_allowance 老人生活津貼、elderly_service 老人福利服務
long_term_care：ltc_general 長照服務總覽、home_care 居家服務、day_care 日間照顧、family_care_home 家庭托顧、meal_service 營養餐飲、transport_service 交通接送、respite_care 喘息服務、assistive_device 輔具與無障礙、institutional_care_subsidy 機構住宿補助
disability：disability_living_allowance 身心障礙者生活補助、disability_assistive_device 身心障礙輔具補助、disability_care_subsidy 身心障礙照顧補助、disability_other 身心障礙其他福利
labor：unemployment_benefit 失業給付、training_allowance 職業訓練生活津貼、employment_incentive 就業促進津貼、employer_subsidy 雇主補助、worker_welfare 勞工福利
housing：rental_subsidy 租金補貼、housing_loan_subsidy 住宅貸款利息補貼、social_housing 社會住宅
health：medical_subsidy 醫療費用補助、health_service 健康服務

（這份清單抄自 `backend/app/registry/taxonomy.yaml`；有疑問就讀那個檔。老人健保費補助歸 elderly_allowance，一般民眾的健保補助歸 medical_subsidy。）

## 輸出
用 StructuredOutput 回傳 `{labels: [ {id, title, is_benefit, kind, category, secondary, closed, reason, confidence}, ... ]}`，
批次檔裡每一份文件都要有一筆，順序不限。不要編造不存在的 id。
