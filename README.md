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
資格媒合可在 `.env` 設定 `LLM_PROVIDER=none` 使用純規則模式。資源引導助理透過 `/api/assistant` 帶入目前身分、已選需求與對話紀錄，由候選補助的資格規則選出追問，快捷選項最多 4 個，其餘選項可直接輸入。Ollama 協助整理需求摘要；模型離線時顯示錯誤並提供重試。可點「整理需求登記」產生摘要，確認後才送出。切換或修改身分會重設助理對話，避免混用不同人的條件。

助理使用後端的 `LLM_PROVIDER=ollama`、`LLM_MODEL` 與 `OLLAMA_BASE_URL` 設定。請啟動主機 Ollama 並安裝設定中完全相同名稱的模型，Docker 仍透過 `host.docker.internal:11434` 連線。對話每則最多 2000 字，最多回答 9 輪，第 9 輪後自動整理摘要。助理會依資料庫候選補助追問，完整資格比對請使用媒合頁面。

助理會直接呼叫與 `/api/benefits/search` 相同的搜尋功能：已有需求時自動查詢，也可輸入「幫我找租金補助」或「搜尋：獎學金」指定關鍵字。查詢的是資料中心已收錄的資料，並非即時爬取全網。每個搜尋條件最多檢索 50 筆，依已知資格排除明確不符者後顯示前 3 筆，附補助詳情、來源連結與待確認條件；無結果時可換關鍵字。後續回答會沿用搜尋條件重新篩選。搜尋結果由伺服器提供，不使用模型自行編造的補助名稱或網址。

預設模型為 `qwen2.5:7b`。實際安裝狀態請用 `ollama list` 確認；系統精確比對 `LLM_MODEL` 標籤，不會以較小模型替代。缺少指定模型時，資格媒合使用規則模式，資源引導助理則提示模型尚未就緒。

## Docker

需要 Docker Desktop（Windows/macOS）或 Docker Engine + Compose v2（Linux）。整包服務由根目錄的
`docker-compose.yml` 定義：`web`（Next.js）、`backend`（FastAPI）、`benefit_crawler`（工作佇列 worker）、
`mongo`、`redis`。

### 啟動

最簡單的方式：開啟 Docker Desktop 後，雙擊 `Start-Docker.cmd`。它會建置、等所有服務健康後開啟瀏覽器。
之後可在 Docker Desktop 的 Containers 頁面找到 `welfarebridge`，直接啟動／停止。手動步驟如下：

```powershell
# 1. 後台密碼（/admin 需求審閱要用；未設定時 /api/appeals 的 GET/PATCH 會回 401）
Copy-Item .env.local.example .env.local
#    編輯 .env.local，把 WELFARE_ADMIN_PASSWORD 改成自己的長密碼

# 2. 選用：爬蟲與本地 AI 設定（不建立此檔也能啟動，會用 compose 內建預設值）
Copy-Item .env.example .env

# 3. 建置並啟動
docker compose up -d --build --wait
```

首次建置會下載 Node 24、Python 3.13、MongoDB 7、Redis 7 的基礎映像並安裝依賴，需要網路，時間較久。
啟動後開啟 http://localhost:3000 。

| 服務 | 對外位址 | 說明 |
| --- | --- | --- |
| `web` | http://127.0.0.1:3000 | Next.js 網站，`/api/*` 代理到 backend |
| `backend` | http://127.0.0.1:8000 | FastAPI，健康檢查 `/api/health` |
| `mongo` | 127.0.0.1:27017 | 官方補助資料 |
| `redis` | 不對外 | 工作佇列 |
| `benefit_crawler` | 不對外 | 處理資料中心送出的工作 |

三個對外 port 都只綁 `127.0.0.1`，不會暴露到區域網路。

### 確認狀態

```powershell
docker compose ps            # 每個服務都應為 running，web/backend 顯示 healthy
docker compose logs -f web   # 或 backend / benefit_crawler
```

`backend` 第一次啟動會把 `data/demo/seed_v2.json` 載入空資料庫，不會自動全站爬取。

### 週期爬取

預設只處理資料中心送出的工作。需要週期爬取時，在 `.env` 設定 `CRAWL_INTERVAL_SECONDS=21600`，然後：

```powershell
docker compose up -d benefit_crawler
```

### 停止與資料

```powershell
docker compose down          # 停止，保留資料
docker compose down -v       # 連同 MongoDB 與 Redis volumes 一起刪除（資料不可復原）
```

需求登記的 `data/welfare.sqlite` 與官方 seed 走 `./data` bind mount，直接留在專案資料夾。
Compose 的 MongoDB 使用自己的 `welfarebridge_mongo_data` volume，與可攜模式的 `data/mongodb/` 分開；
切換模式不會自動搬移資料，備份時 Docker MongoDB 需另外備份 volume。

### 本地 AI（選用）

`OLLAMA_BASE_URL` 預設指向 `http://host.docker.internal:11434`，也就是**主機上**的 Ollama；
容器不會自己安裝。沒有 Ollama 或缺少指定模型時，系統回到純規則模式（可在 `.env` 設 `LLM_PROVIDER=none` 明確關閉）。

SQLite 與爬蟲檔案保存在本機 `data/`，Redis 佇列使用 `redis_data` volume 保存。`docker compose down` 保留這些資料；加上 `-v` 會刪除 MongoDB 與 Redis volumes，請勿用於一般停止操作。

## 驗證

```powershell
npm run build
npm run lint
npm test
npm run test:backend
# 網站與後端啟動後：
npm run test:e2e
```

Docker 環境（映像內含 `tests/`，不需要本機 Node／Python）：

```powershell
# 後端與爬蟲（使用 compose 的 MongoDB，測試資料庫固定為 benefits_test）
docker compose run --rm --no-deps benefit_crawler python -m pytest tests -m "not network"
# 即時官方網站測試（會連線到官方網站）
docker compose run --rm --no-deps benefit_crawler python -m pytest tests -m network
# 前端單元測試
docker build --target build -t welfarebridge-web-build .
docker run --rm welfarebridge-web-build npm test
```

後端資料庫測試使用獨立的 `benefits_test`，不可將正式資料放入該名稱。即時官方網站測試需另執行 `backend/.venv/Scripts/python.exe -m pytest backend/tests -m network`。測試結果與未驗證項目見 [整合驗證紀錄](docs/integration-verification.md)。

## 版本紀錄與備份

所有程式由根目錄 Git 管理，不再使用子專案 gitlink。原兩個子專案的 Git metadata 與舊設定完整保留在本機 `.project-history/`，此目錄不提交。整合內容統一由根目錄版本紀錄追蹤。
備份前先停止服務，再複製整個 `data/`；Docker MongoDB 需另備份 volume。既有 SQLite 及瀏覽器儲存鍵未變更。
