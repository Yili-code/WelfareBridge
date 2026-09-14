# WelfareBridge 整合驗證

驗證日期：2026-09-14。環境：Windows、Node.js 24.17.0、Python 3.12、MongoDB 8.2.6、Chrome。

## 完成的整合

- 取消外層的 `welfare-app` gitlink，網站原始碼、設定與依賴移到根目錄，由單一 Git 工作目錄管理。
- 原爬蟲後端移到 `backend/`，Python 模組改為 `benefit_crawler`，同步修正 import、動態載入來源設定、CLI、測試與工具腳本。
- 原資料中心與完整媒合介面併入 `src/benefits/`，由同一個 Next.js 網站提供；不再啟動 Vite 或 nginx 前端。
- `/dashboard` 直接呼叫官方資格比對；`/my-benefits` 帶入目前服務對象的明確條件。沒有把模糊問卷答案轉成確切資格。
- 保留 `/api/appeals` 的驗證與 SQLite，其他 `/api/*` 代理到 FastAPI。
- 統一 `Start-WelfareBridge.cmd`、安裝腳本、Docker Compose 與開發啟動設定。

## 驗證結果

| 檢查 | 結果 |
| --- | --- |
| Next.js 正式版編譯及 TypeScript | 通過，所有頁面與 API 路由成功產生 |
| ESLint | 通過 |
| Python 後端回歸 | 91 passed，含真實 MongoDB API、爬蟲解析、規則、搜尋一致性與模型健康檢查 |
| 即時官方來源爬取 | 1 passed，實際連線教育部來源並解析一筆公告 |
| 問卷到媒合資料轉換 | 2 passed，保留未知與戶籍／居住地差異 |
| SQLite 保存 | 1 passed，跨連線、重試去重、更新與重開資料庫 |
| Chrome 端對端 | 5 passed，24.1 秒 |
| 整組服務重啟 | 1,226 筆補助與 4 筆隔離測試需求摘要一致；原始 SQLite 雜湊一致 |
| 原資料與 Git 備份 | 80 個原始資料及 Git 檔案 SHA-256 一致 |
| Docker Compose | 設定解析通過；未完成容器實跑 |

Chrome 測試涵蓋十題建檔、主畫面的真實媒合、條件帶入完整表單、送出完整比對、搜尋、詳情頁及重新整理、服務錯誤與重試入口、文字解析、追問、背景工作完成、需求送出重試、後台讀取及狀態更新。測試使用獨立的 `test-results/appeals.sqlite`，沒有將測試需求寫進原資料庫。

頁面截圖保存在本機 `test-results/dashboard.png` 與 `test-results/benefit-detail.png`；測試輸出不提交 Git。

## 執行時發現並修正

- Windows 缺少 `tzdata`，導致後端無法載入 Asia/Taipei。
- Next.js 阻擋 `127.0.0.1` 開發資源，造成事件未啟動；加入明確允許的本機來源。
- 原前端的 ref 更新與表單同步不符合合併後 React 檢查，已修正。
- 搜尋 API 直接呼叫清單函式時未提供新增參數，誤用了 FastAPI Query 預設值。
- Ollama 健康檢查只比模型家族名稱，會把 0.5b 誤當成已安裝 7b；改成精確標籤比對，快取也區分模型。
- Docker worker 原設計啟動就週期爬取；新增只處理佇列的模式，預設可處理網頁送出的工作而不自動全站爬取。

## 明確限制

- 本機只安裝 `qwen2.5:0.5b`，原設定的 `qwen2.5:7b` 未安裝。因此 AI 生成／AI 抽取尚未以指定模型驗證；已實際確認缺模型時 API 能正確退回規則式解析。
- Docker Desktop 在此環境未提供可用引擎，Docker 僅完成設定驗證；本機 MongoDB、API 與網站已實際運行。
- 官方 seed 是既有爬取資料，不代表本次重新查核所有公告。即時爬蟲測試只驗證一個官方來源，不能據此保證每個外部網站永久可用。
- 個人檔案、手動資源與通知仍維持原有 localStorage 行為；助理仍為原有腳本式引導。此次沒有新增帳號同步或 Gemini 串接。
- 後端測試存在一項上游 Starlette/httpx 棄用提示，不影響目前測試結果。

目前正常使用入口為 http://localhost:3000，使用原本 `.env.local` 與 `data/welfare.sqlite`。版本整合保留原本的本機與遠端歷史；舊子專案 Git metadata、原設定與原 README 保留在 `.project-history/`。

推送前另移除兩個官方 HTML 測試存檔中的公開地圖 API key，保留解析所需內容。
