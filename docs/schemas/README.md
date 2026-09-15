# 問卷 Schema 交付

questionnaire-profile.schema.json 定義完成現行十題問卷的單一 Profile；questionnaire-profiles.storage.schema.json 定義 wf.profiles 陣列，以相對路徑引用前者，請一起交付。questionnaire-profile.example.json 是獨立測試瀏覽器實際填寫產生的合成資料，不是使用者個資。

此格式針對現行新建檔案，不相容所有歷史資料。TypeScript 的 screening、currentRegion 是選填，但現行建檔會輸出，交付格式因此要求必填。應用程式尚未接入這份 JSON Schema 做執行期驗證。

十題原始文字完整存於 screening。identities、economy、needs 是 questionnaire.ts 的 profileTags 計算結果，不能當成原始答案。schema 檢查欄位、選項、數量、互斥及年齡區間；跨欄位的衍生標籤一致性與同縣市 currentRegion = region 由應用程式負責，未全部以 schema 表達。

identities：在學→學生；待業求職→待業／失業；自營接案→非典型就業；租屋→租屋族；懷孕育兒扶養未成年→育兒家庭；65歲以上→高齡長者。
economy：第五題五個選項依序對應低收入戶、中低收入戶、近貧／經濟不穩定、一般家庭、不確定。
needs：第一題依序對應 [就學與學費]、[就業與職訓]、[住宅與租金]、[經濟補助,育兒與托育,生活物資]、[醫療與健保,長照與照顧,身心健康支持]。

未填實際年齡為 null，未填縣市為空字串。district 是舊檔案可保留的選填字串，新問卷不收集；undefined 不會寫入 JSON。

驗證日期：2026-09-15。獨立 Chrome context 實際完成十題，逐題比對 wf.profiles，再重新整理並確認整份 JSON 不變。媒合 API 使用 stub；未驗證真實後端媒合，未讀取使用者既有瀏覽器資料。

完成建檔才持久化，未完成回答僅存在 React state。wf.profiles 是陣列，wf.activeProfile 是目前 ID 的 JSON 字串。資料按瀏覽器與 origin 區隔；清除網站資料會刪除。後端媒合保存的是轉換後資格快照，不是完整原始問卷備份。

來源：src/lib/types.ts、src/lib/questionnaire.ts、src/components/ProfileWizard.tsx、src/app/page.tsx、src/lib/store.ts。題目或輸出變更時需同步更新 schema。
