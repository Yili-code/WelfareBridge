# 第三輪（來源擴充）工具與資料

scripts/round3/：探索代理用的乾跑、候選合併、確定性驗證、標註匯出、黃金集合併、回填腳本（路徑仍指向當時的 session scratchpad，重用前把 CAND_DIR / labels 路徑改成 benefit_crawler/config/candidates 與 data/gold/round3）。
benefit_crawler/config/candidates/：探索代理寫的候選來源 YAML（已合併者見 sources.yaml「本輪新增」區段；未合併：mohw_dops、kaohsiung_sanmin_office、yunlin_sw、taichung_xitun_office、tier-3b 待驗證）。
data/gold/round3/：本輪抽樣的 150 份原文批次（batch_01–10.txt）與兩次獨立標註的 JSON（labels/）。
