# 收錄政策（什麼算一筆補助方案）

標準參考 [GetGrant 的公開編輯與查核標準](https://getgrant.tw/editorial-standards)（另見 [首頁](https://getgrant.tw/) 的分類方式）。
**只借用它「收什麼、不收什麼、每筆要有哪些欄位」的定義；不使用、不抓取它的任何資料**——本系統的每一筆紀錄仍只來自官方來源（`sources.yaml` 登錄、通過網域驗證），並附原文與來源網址。

## 1. 收什麼

只收對申請人有**具體經濟價值**的項目：補助、補貼、津貼、獎助／獎學金、減免、貸款（含利息補貼）、有經濟價值的服務（長照、托育、交通接送、輔具…）。

## 2. 不收什麼（pipeline 直接 `filtered_out`，原因寫在 `raw_documents.classification.reason`，`method=admission`）

| `page_kind` | 例子 | 判斷依據 |
| --- | --- | --- |
| form | 申請書、申請表、切結書、同意書、範本；整份都是空白表單的 PDF | 標題以表單字眼結尾，或含表單字眼且沒有方案名詞（計畫／辦法／補助／津貼…）；或開頭 120 字寫明是申請書／訪查表且滿是 □ 待填欄位（標題有方案名詞時不適用，方案頁常把申請表附在要點後面） |
| attachment | 「(PDF檔案下載)」、標題就叫「pdf」的下載連結、只有附件清單沒有內文的頁 | 去掉「檔案下載」「.pdf」後沒有名稱，或整個標題只有檔案格式字眼（pdf／檔案／附件／下載）；或內文 < 400 字且 ≥ 3 個附件檔名 |
| progress_query | 申辦進度查詢、核發進度查詢、稅金試算 | 標題含進度查詢／案件查詢／試算（線上服務入口，不是方案） |
| flowchart | 服務流程圖 | 標題含流程圖 |
| logo | 識別標誌、標章 | 標題含 LOGO／標章／標誌 |
| statistics | 統計表、統計年刊、預算書、決算書 | 標題含統計／預算書／決算書 |
| faq | 問答集、常見問題 | 標題含問答集／Q&A |
| directory | 名單、名冊、一覽表、聯繫窗口；據點表 PDF | 標題含名單／名冊／一覽表／窗口；或標題其實是表格欄位名（「縣市別 共照名稱 共照地址 共照電話」）且內文一行一筆機構、地址、電話 |
| notice | 修正條文、修正發布、修正案、條文對照表、草案、廢止、公聽會、說明會、徵求、招標、得獎名單、遴選、查核督導、稽核 | 標題含這些行政公告字眼；爬蟲標題是「…（來源頁）」或 PDF 檔名時也看內文首行（≤ 80 字） |
| fragment | 「應備文件」「相關檔案」「洽辦資訊」「申請說明」等只有段落名的分頁 | 整個標題就是一個段落名（臺北市社會局 cp.aspx 的分頁各成一份文件），沒有方案名稱 |
| garbled | PDF 文字擷取失敗的亂碼 | 去掉空白後中文字 < 5% 且三成以上不是中英數與標點；純英文頁不算 |
| site_info | 資料來源與更新頻率、隱私權、網站導覽、無障礙聲明、聯絡我們 | 標題含這些網站資訊字眼 |
| statute | 長期照顧服務法、長期照顧服務機構法人條例、老人福利法施行細則 | 標題以「法／條例／施行細則」結尾且沒有方案名詞（「…補助辦法」「…扶助條例」仍是方案） |

關鍵字分類器不確定的頁面交給本地 AI 時，AI 也要回 `page_kind`；回上述任何一種即視為不是方案。

已停止受理的方案（標題「【已不再受理新申請案】」或原文「額度已用罄」「已停辦」）仍是方案頁，照常收錄，但 `status=expired`：
資料中心預設只列「受理中」，媒合也不納入；`review.reasons` 會寫明是依哪個字眼判定。

## 3. 保留但不進清單、統計主數字與媒合：彙整頁（`record_kind=portal`）

總整理、懶人包、專區、有哪些、福利地圖、報您知等頁面同一頁列出多項補助，各項條件不同，不能當成一筆方案來比對。
它們仍保留在資料中心（篩選「紀錄類型：含彙整頁／只看彙整頁」），供追溯連結。

## 4. 每筆方案要有的欄位與品質等級（`benefits.admission`）

必要欄位（同 GetGrant）：方案名稱、主辦機關、申請資格、金額／給付內容、申請期間、申請方式、官方來源網址。

- `completeness.present / missing`：哪些欄位已從官方原文（含本地 AI 補齊並驗證過的）抽到、哪些沒有。**沒有就是沒有，不猜。**
- `quality_tier`：
  - `verified`：資格與給付內容都有、來源已通過官方驗證
  - `needs_review`：缺申請資格或金額／給付內容（清單上顯示「待補：…」，媒合時顯示為資料不足，不會判定不符合）
  - `portal`：彙整頁

## 4b. 疑似補助／類別待確認（`classification.uncertain`）

三方投票（關鍵字、embedding、本地 LLM）不一致時，依「不漏抓」原則保留紀錄，但標 `uncertain=true`、`review.needs_review=true`，資料中心顯示「疑似／類別待確認」，媒合排除，直到人工在審核佇列確認。

## 4c. 資格寫在附件 PDF 裡的方案

爬蟲會把「詳細說明類」的 PDF 附件（要點、計畫、辦法、簡章…）下載下來，文字以 `【附件：檔名】` 併進原文，
所以這類頁面的資格與金額不再只靠頁面上的兩三行摘要。規則與上限見 [crawler.md](crawler.md#附件-pdf-併入原文)。
申請書、切結書、預算書這類表單與帳務文件不抓——抓進來只會讓抽取誤把「應備文件」當成資格。

## 5. 程式位置

- `backend/app/services/admission.py`：`page_kind()`、`completeness()`、`quality_tier()`、`admit()`
- `backend/app/services/pipeline.py`：分類前先做 `page_kind` 排除；`_upsert_benefit` 寫入 `record_kind` 與 `admission`；保留的紀錄也會重新計算
- `backend/app/llm/prompts/classify_benefit.md`：AI 分類回 `page_kind`
- `GET /api/benefits?kind=program|portal|all`（預設 program）、`GET /api/stats` 的 `benefits_programs / benefits_portals / quality_verified`
- 媒合 `load_records` 排除 portal
- `backend/benefit_crawler/base/base_crawler.py`：`read_attachments()`；`base/parser.py`：`attachment_is_detail()`、`meaningless_name()`、`headline_title()`
- 測試：`backend/tests/test_admission.py`、`backend/tests/test_attachments.py`
