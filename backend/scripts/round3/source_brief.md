# 新增官方補助來源：工作說明（給探索代理）

## 專案背景
temp_demo 是台灣政府補助的爬蟲／抽取／媒合系統（FastAPI + MongoDB，只用本地 LLM）。來源登錄在
`C:/Users/wei/OneDrive/Desktop/temp_demo/backend/benefit_crawler/config/sources.yaml`（先讀檔頭 1–22 行的設定說明，與 187–216 行的 `taipei_dosw` 範例）。
新來源幾乎都用 `benefit_crawler.generic.page_crawler.GenericPageCrawler`，不用寫程式，只要一個 YAML 設定：`pages` 清單 +（可選）`follow_links`。

## 鐵律
1. **只收官方網站**：網域必須是 `*.gov.tw`、`*.gov.taipei`，或 `official_domains.yaml` 白名單裡的網域（edu.tw 要在白名單）。不是就不要提。
2. **GetGrant（getgrant.tw）只能當「有哪些補助類型」的參考，絕對不能把它的網址當來源、不能抓它的資料、不能複製它的文字。**
3. **不能造假**：每個網址都要真的抓過（用下面的乾跑腳本），沒抓到的頁面不要寫進設定。
4. **每筆紀錄要對應到一個補助方案頁**：頁面本身要有「誰可以申請、給多少／給什麼、怎麼申請」的內文。純表單、附件下載、流程圖、進度查詢、統計、FAQ、名單、公告、只有段落名的分頁片段、法律本文都會被收錄政策排除（見 `docs/inclusion-policy.md`），別把這些當主要頁面。
5. 不要改 `sources.yaml`（多個代理同時工作會互相覆蓋）。把你的設定寫到指定的候選檔，由主流程合併。

## 目標類別（這一輪優先）
- 生育、育兒、托育：生育獎勵金／生育津貼（縣市、鄉鎮各有不同）、育兒津貼、托育補助、育嬰留停津貼、幼兒園就學補助
- 社會救助與老人福利：低收／中低收入戶生活補助、急難救助、馬上關懷、特殊境遇家庭扶助、中低收入老人生活津貼、老人假牙、老人健保補助、重陽敬老金、獨居老人服務
- 也歡迎順手收：身心障礙者生活補助、輔具補助、長照服務

taxonomy 類別 id（`seed_category` 只能用這些；沒有合適的就留空）：
`birth_incentive` 生育獎勵金／生育津貼／生育給付、`low_income_allowance` 低收入戶生活補助、`special_circumstances_aid` 特殊境遇家庭扶助、`child_allowance` 育兒津貼、`childcare_subsidy` 托育補助、
`parental_leave_allowance` 育嬰留停津貼、`emergency_relief` 急難救助、`elderly_allowance` 老人生活津貼（含特別照顧津貼、假牙、健保補助、重陽敬老金）、
`elderly_service` 老人福利服務、`home_care` 居家服務、`day_care` 日間照顧、`family_care_home` 家庭托顧、`respite_care` 喘息服務、
`institutional_care_subsidy` 機構住宿補助、`transport_service` 交通接送、`assistive_device` 輔具、`meal_service` 營養餐飲、
`disability_living_allowance` 身心障礙者生活補助、`disability_care_subsidy` 身心障礙照顧補助、`disability_other` 身心障礙其他福利、
`rental_subsidy` 租金補貼、`scholarship` 獎學金、`student_aid` 助學金、`education_subsidy` 就學補助。
`education_subsidy` 也涵蓋幼兒園就學補助；`parental_leave_allowance` 育嬰留停津貼。
已登錄且不要重複的來源 id（見 sources.yaml）：taipei_dosw、taipei_health、mohw_gov、ltc_1966、moi_pip、mol_gov、wda_emps、sfaa_childcare、mohw_social_assistance、ntpc_sw、taichung_sw、kaohsiung_sw、taoyuan_sw、taipei_daan_office、ntpc_banqiao_office。
白名單外的 edu.tw 網域不通過驗證；目前已加白名單：www.ece.moe.edu.tw（全國教保資訊網）、www.bli.gov.tw（勞保局，本來就是 gov.tw）。

## 設定檔格式（寫成一個 YAML 檔，單一來源）
```yaml
id: ntpc_sw                      # 小寫英數與底線，全專案唯一（既有 id 見 sources.yaml）
name: 新北市政府社會局 — 社會救助、兒少福利、老人福利
organization: 新北市政府社會局
provider_type: local_government  # central_government | local_government | township | school | mixed
source_type: government_site
base_url: https://www.sw.ntpc.gov.tw/
crawler: benefit_crawler.generic.page_crawler.GenericPageCrawler
expected_title_keywords: [新北市政府社會局]   # 抓到的頁面 <title> 要含其中一個，驗證用
data_confidence: 100
enabled: true
domains: [social_welfare, long_term_care, disability]   # education | youth | social_welfare | long_term_care | disability | labor | housing | health
content_selectors: ["#content", ".content"]   # 主內容區 CSS；不確定就省略（會用啟發式）
follow_links:                     # 可選：從 pages 出發追同網域、白名單內的連結（depth 1）
  depth: 1
  allow: ["cp\\.aspx\\?n="]        # regex，只追符合的網址（方案內容頁的網址型態）
  deny: ["News\\.aspx", "Default"]
  max_links: 40
pages:
  - {url: "https://…", title: 新北市生育獎勵金, seed_category: child_allowance}
  - {url: "https://…", title: 新北市急難救助, seed_category: emergency_relief}
  - {url: "https://…/list", title: 社會救助業務總覽, skip: true, skip_reason: 只是分類目錄頁}
```
`pages` 裡放「方案內容頁」或「列出多個方案連結的目錄頁」（目錄頁配合 `follow_links` 才有用；目錄頁本身通常會被判為彙整頁）。

## 乾跑（一定要做，不寫資料庫）
```bash
cd C:/Users/wei/OneDrive/Desktop/temp_demo/backend && PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe "C:/Users/wei/AppData/Local/Temp/claude/C--Users-wei-OneDrive-Desktop-temp-demo/5f47be9f-799f-4942-9726-6aadfffe13d2/scratchpad/dry_run_candidate.py" <你的候選 yaml> --max-items 12
```
輸出每份文件的 `kind=`（program 才是方案頁；attachment/form/fragment/notice… 會被排除）、`kw_benefit=`（關鍵字分類器是否認為是補助）、字數與前 160 字。
好的來源：至少 3 份 `kind=program` 且字數 ≥ 300 且內文真的講資格與給付。抓不到內文（字數 < 100、都是選單）就換 `content_selectors` 或換頁面。
`official=False` 代表網域不通過驗證，直接放棄該網站。

## 怎麼找頁面
- 用 WebFetch 讀該機關網站的社會福利／社會救助／兒少福利／老人福利選單，找出各方案的「內容頁」網址型態（例如 `cp.aspx?n=…`、`News_Content.aspx?n=…&s=…`、`/xxx/yyy.html`）。
- 每個方案頁抓來看一眼，確認有申請資格與給付內容。
- 區公所頁面常只是「本所受理業務」列表；只有真的寫出資格與金額的頁面才值得收。

## 回報格式（StructuredOutput）
- `id`、`name`、`host`、`official`（乾跑印的 official）、`candidate_file`（你寫的 yaml 完整路徑）
- `pages_program`（乾跑中 kind=program 且字數 ≥ 300 的文件數）、`pages_total`
- `samples`：3–8 筆 {title, url, seed_category, chars}
- `birth_incentive_pages`：生育獎勵／生育津貼頁面數
- `issues`：抓不到的頁面、內文太短、需要特殊 selector、疑似 JavaScript 動態載入等
- `verdict`：`ready`（可直接合併）| `partial`（有些頁面要再處理）| `reject`（網站不適合，說明原因）
