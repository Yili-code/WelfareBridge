# 補助爬蟲與媒合後端

爬蟲已融合至 WelfareBridge，Python 模組名稱為 `benefit_crawler`。前端由根目錄 Next.js 提供，不再啟動另一個 Vite 網站。

- 主入口與安裝：[專案 README](../README.md)
- Python API：`backend/app/main.py`
- 爬蟲 CLI：在 `backend` 執行 `python -m benefit_crawler --help`
- 來源：`backend/benefit_crawler/config/sources.yaml`
- 原文、官方 seed、gold labels：`data/`
- API 文件：後端啟動後開啟 http://127.0.0.1:8000/docs

本機模式預設用背景執行緒處理資料中心送出的工作；Docker 使用 Redis 佇列及 `benefit_crawler --worker`。週期爬取需額外設定非零的 `CRAWL_INTERVAL_SECONDS`。

來源驗證、robots、速率限制、HTML/PDF/CSV/JSON/XML 解析、抽取驗證、去重、規則式媒合、追問與 Ollama 介面均保留。Ollama 未啟用時，保留純規則式結果與缺資料狀態。

技術規格：[資料模型](data-model-v2.md)、[媒合策略](matching-strategy.md)、[欄位說明](data-dictionary.md)、[實例](example-walkthrough.md)。

`backend/scripts/round3/` 為人工審閱與資料探索工具，需要相應的輸入檔案。原作者電腦的絕對路徑已改為相對於本專案；候選與標註工作檔預設放在 `data/round3/`。其中 `label_workflow.js` 需要支援其 workflow API 的外部執行環境，並非網站啟動所需。
