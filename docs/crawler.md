# Crawler（v2）

## 來源登錄

`backend/benefit_crawler/config/sources.yaml` 每一段是一個來源；新來源多半用 `GenericPageCrawler`：

```yaml
- id: taipei_dosw
  name: 臺北市政府社會局 — 社會救助、老人福利、身心障礙、長期照顧
  organization: 臺北市政府社會局
  provider_type: local_government
  source_type: government_site
  base_url: https://dosw.gov.taipei/
  crawler: benefit_crawler.generic.page_crawler.GenericPageCrawler
  expected_title_keywords: [臺北市政府社會局]   # base_url 頁面 <title> 必須含其一
  data_confidence: 100
  domains: [social_welfare, long_term_care, disability]
  content_selectors: ["#CCMS_Content", "#base-content"]   # 主內容區（依序嘗試；沒命中用啟發式）
  follow_links: {depth: 1, allow: ["cp\\.aspx\\?n="], deny: ["News\\.aspx"], max_links: 60}
  pages:
    - {url: "https://dosw.gov.taipei/cp.aspx?n=C764A5808F9A3B08", title: 臺北市身心障礙者生活補助, seed_category: disability_living_allowance}
    - {url: "https://map.dosw.gov.taipei/...", title: 服務地圖, skip: true, skip_reason: 互動式地圖，沒有可抽取的補助條文}
```

| 設定 | 說明 |
| --- | --- |
| `pages[].format` | html（預設）/ pdf / csv / json / xml |
| `pages[].data_kind` | text（預設）/ providers（名單 → providers 集合）/ statistics（略過）/ providers_text（名單 PDF，略過）/ auto（依欄位判斷） |
| `pages[].seed_category` | 語料統計的種子標籤；分類器仍會重新判斷，但關鍵字沒過時保留並標記 method=seed_category |
| `pages[].source_page` | 附件（PDF）對應的官方頁面 |
| `split_selector` | 一頁多方案（例如台灣就業通的分頁）→ 每個區塊一份文件（URL 加 `#part-N`）；同時命中外層與內層區塊時只取最外層 |
| `follow_links` | 只追同網域、白名單內、符合 allow 且不符合 deny 的連結；深度與最大頁數可設；查詢參數少的網址先抓，同一輪內容完全相同的其他網址（`?fm=1`、`&s=…`）記為略過並附「與哪個網址相同」；連結文字只是「連結到…頁面」時改用頁面本身的標題 |
| `is_repost` | 彙整站（我的E政府）：提供機關以頁面的「發布單位」為準 |

## 官方來源驗證

`official_domains.yaml`：suffix_rules（gov.tw / gov.taipei / edu.tw）、whitelist（host → 機關）、blocklist（非官方，記錄原因）、public_school_domains。
驗證 = 網域 + HTTPS + 標題關鍵字；未通過的來源整個 skipped，不寫任何原始文件。

## 執行

```bash
cd backend
python -m benefit_crawler --list
python -m benefit_crawler --dry-run --source mol_gov --max-items 3
python -m benefit_crawler --source taipei_dosw --source ltc_1966
python -m benefit_crawler --no-pipeline
python -m benefit_crawler --pipeline-only --force --no-llm
python -m benefit_crawler --pipeline-only --force        # 正式重跑（不確定的頁面交給本地 AI 二次判斷）
python -m benefit_crawler --llm-fill                     # 只補 canonical 紀錄
python -m benefit_crawler --llm-fill --include-non-canonical
python -m benefit_crawler --mine-keywords
python -m benefit_crawler --export-seed
python -m benefit_crawler --loop 21600
```

也可由 API 觸發：`POST /api/crawler/run`、`POST /api/pipeline/run`、`POST /api/pipeline/llm-fill`、`POST /api/pipeline/mine-keywords`（有 Redis 時交給 crawler-worker）。

## 禮貌性爬取

`PoliteHttpClient`：timeout、retry + exponential backoff、每個 host 的 request_delay（預設 1 秒）、robots.txt、Python 3.13 對部分政府憑證鏈的 VERIFY_X509_STRICT 關閉（CA 驗證仍在）。

## source.xlsx 的處理方式

51 個網址全部登錄在 `sources.yaml`：

- HTML 頁面（28）：依網站分成 gov_tw_services、taipei_dosw、taipei_health、mol_gov、wda_emps、mohw_gov、ltc_1966、moi_pip、moe_law；每個都往下追一層同網域連結（1966 追兩層）。
- PDF（12）：taipei_ws_files、mohw_gov（長照給付及支付基準）；轉文字後與 HTML 一樣走 pipeline。
- CSV/JSON/XML（11）：機構名單匯入 providers（臺北市長照專業服務特約單位、居家護理所、臺中市老人福利機構）；統計資料（職工福利概況、機構床數）與同一資料集的其他格式標記 skip。
- 服務地圖（map.dosw.gov.taipei）與銀行登入頁（sloan.bot.com.tw）標記 skip 並記錄原因；銀行網域同時列在 blocklist。

實際結果見 [generated/sources.md](generated/sources.md) 與 [generated/pipeline-stats.md](generated/pipeline-stats.md)。
