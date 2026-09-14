# WelfareBridge

單一福利導引網站，整合建檔、需求登記、官方補助資料中心、爬蟲與資格媒合。

```text
src/app/                  Next.js 頁面與需求登記 API
src/components/           福利導引與共用介面
src/benefits/             資料中心、規則檢視、完整媒合介面
backend/app/              FastAPI、抽取與資格規則引擎
backend/benefit_crawler/  官方來源爬蟲（修正後的模組名稱）
data/                     原有 SQLite、官方 seed、本機 MongoDB 資料
docs/                     資料規格與整合驗證紀錄
scripts/                  統一啟動與測試入口
```

## Windows 本機啟動

需要 Node.js 24、Python 3.12 或更新版本；首次安裝需網路。

1. 在此資料夾執行 `./Setup-WelfareBridge.ps1`。它會安裝專案依賴與官方 MongoDB 可攜執行檔，不安裝 Windows 服務。
2. 在 `.env.local` 設定 `WELFARE_ADMIN_PASSWORD=自己的長密碼`。原網站的設定檔與 SQLite 已搬到根目錄，無需重新建立。
3. 雙擊 `Start-WelfareBridge.cmd`，或執行 `npm run dev`。
4. 開啟 http://localhost:3000。啟動器會依序確認／啟動 MongoDB、後端與網站；關閉時只停止本次啟動的程序。

若系統已有 MongoDB，直接沿用 `backend/.env` 或根目錄 `.env` 設定的 `MONGODB_URL`。自帶的 MongoDB 僅監聽 `127.0.0.1:27017`，資料永久保存於 `data/mongodb/`。
自訂 MongoDB 執行檔可設定 `MONGOD_PATH`；Python 可設定 `PYTHON`。若要使用已啟動的後端，可在 `.env.local` 設定 `BENEFIT_API_URL=http://127.0.0.1:8000`。

若系統的 npm 捷徑損壞，可直接用 `node scripts/dev.mjs` 啟動；安裝腳本會使用 Node 安裝目錄內的 npm。

## 網站功能

| 路徑 | 功能 |
| --- | --- |
| `/` | 十題初篩與建立服務對象 |
| `/dashboard` | 官方補助初步比對、原有資源與通知、需求助理 |
| `/admin` | 需求登記、審閱與資源上架 |
| `/data-center` | 搜尋補助、官方原文、爬取與處理狀態 |
| `/data-center/{id}` | 原始資料、資格規則與證據 |
| `/registry` | 屬性登錄表與類別 |
| `/my-benefits` | 完整表單、逐步追問、快速輸入與媒合結果 |

完整媒合頁會帶入目前服務對象的明確條件。年齡區間、合併學制、本人或家人的身分等模糊回答不會轉成確切條件。缺資料保留「需補充資料」；初步符合不等於機關核准。

`/api/appeals` 由 Next.js 處理，其餘 `/api/*` 代理到 FastAPI，前端不需要切換網址。需求登記存在 `data/welfare.sqlite`；官方補助存在 MongoDB。個人檔案、手動上架資源與通知維持原有 localStorage 行為，尚非跨裝置同步。請沿用原本的網站 hostname/port，才能讀到原瀏覽器資料。

## 爬蟲與本地 AI

```powershell
cd backend
./.venv/Scripts/python.exe -m benefit_crawler --list
./.venv/Scripts/python.exe -m benefit_crawler --source taipei_dosw --no-llm
```

來源設定在 `backend/benefit_crawler/config/sources.yaml`。初次啟動只在空資料庫載入既有官方 seed；不會自動全站爬取。可透過資料中心啟動工作。
Ollama 是可選服務；`.env` 設定 `LLM_PROVIDER=none` 可使用純規則模式。未啟用 AI 時，助理仍是原有腳本式引導，不能聲稱已接 Gemini。

目前本機僅安裝 `qwen2.5:0.5b`，原後端設定的 `qwen2.5:7b` 尚未安裝。系統會精確比對模型標籤，缺少指定模型時回到規則模式。若要啟用原設定的 AI 抽取，需先自行安裝該模型；未將較小模型冒充成 7b。

## Docker

```powershell
docker compose up -d --build
# 需要週期爬取時，在 .env 設定 CRAWL_INTERVAL_SECONDS=21600，然後：
docker compose up -d benefit_crawler
```

同一個 Next.js 網站在 port 3000。Compose 的 MongoDB 使用自己的 `welfarebridge_mongo_data` volume，與可攜模式的 `data/mongodb/` 分開；切換模式不會自動搬移資料。Redis 與 worker 預設處理資料中心送出的工作；只有設定非零的 `CRAWL_INTERVAL_SECONDS` 才啟用週期爬取。

## 驗證

```powershell
npm run build
npm run lint
npm test
npm run test:backend
# 网站與後端啟動後：
npm run test:e2e
```

後端資料庫測試使用獨立的 `benefits_test`，不可將正式資料放入該名稱。即時官方網站測試需另執行 `backend/.venv/Scripts/python.exe -m pytest backend/tests -m network`。測試結果與未驗證項目見 [整合驗證紀錄](docs/integration-verification.md)。

## 版本紀錄與備份

所有程式由根目錄 Git 管理，不再使用子專案 gitlink。原兩個子專案的 Git metadata 與舊設定完整保留在本機 `.project-history/`，此目錄不提交。整合內容統一由根目錄版本紀錄追蹤。
備份前先停止服務，再複製整個 `data/`；Docker MongoDB 需另備份 volume。既有 SQLite 及瀏覽器儲存鍵未變更。
