# 福利資源導引平台

協助民眾在不知道「該找什麼」的情況下，找到可申請的福利與社會資源。

```bash
npm run dev
```

開啟 http://localhost:3000

## 目前完成的範圍

| 頁面 | 路徑 | 說明 |
| --- | --- | --- |
| 入口 | `/` | 五步驟建立第一份服務對象檔案（對象關係 → 地區 → 年齡 → 身分與經濟狀況 → 需求類別） |
| 主畫面 | `/dashboard` | 左側切換／新增服務對象，主區顯示符合的資源與主動通知，右下角 AI 助理 |
| 後台 | `/admin` | 檢視使用者送出的需求登記（含對話逐字稿）、上架新資源並觸發通知 |

### 三條主要流程

1. **建檔**：一份 profile ＝ 一個服務對象。媽媽想知道 17 歲的孩子能申請什麼，就替孩子單獨建一份檔案（`ProfileWizard`，入口頁與側欄共用同一個元件）。
2. **AI 引導**：主畫面右下角的助理會依序問「困擾什麼 → 持續多久 → 申請過什麼 → 最希望得到什麼 → 補充」，最後整理出地區、身分、年齡、主要訴求的摘要。系統若沒有對應資源，使用者可一鍵送出需求登記，後台看得到。
3. **主動通知**：後台上架新資源時，`publishResource()` 會立刻用 `matchReason()` 比對每一份 profile（地區、年齡區間、身分、需求），命中的產生一筆通知，並在側欄與主畫面顯示未讀數。

## 專案結構

```
src/
  app/
    page.tsx            入口與建檔精靈
    dashboard/page.tsx  主畫面（側欄 + 資源 + 通知 + 助理）
    admin/page.tsx      後台：需求登記 / 資源上架
  components/
    ProfileWizard.tsx   建檔精靈（入口與新增對象共用）
    Sidebar.tsx         服務對象清單
    AssistantWidget.tsx 右下角浮動助理
  lib/
    types.ts            Profile / Resource / Appeal / Notification
    options.ts          縣市、身分、需求等選項清單
    matching.ts         資源 × profile 的比對規則
    store.ts            資料層（localStorage）＋ React hooks
    assistant/          對話引擎
```

## 之後要接的兩件事

**1. 換成 Gemini API。** `src/lib/assistant/` 定義了 `AssistantEngine` 介面（`start()` / `reply()`），目前由 `mockEngine.ts` 用寫死的腳本實作。改接 Gemini 時：

- 新增 `geminiEngine.ts`，兩個方法改成呼叫自己的 `/api/assistant` route（金鑰放伺服器端，不要進瀏覽器）。
- 把 `src/lib/assistant/index.ts` 的 `export const engine` 指向新的實作。
- UI 與需求登記流程不需要改動——`AssistantTurn.draft` 就是送進後台的那份摘要。

**2. 換成真的後端。** `src/lib/store.ts` 是唯一碰資料的地方，目前全部存在瀏覽器 localStorage（所以後台看到的是同一台裝置上的資料，重整不會消失、換裝置會消失）。改接資料庫時把這一層的讀寫換成 API 呼叫即可，元件用的是 `useProfiles()` / `useAppeals()` 這類 hook，介面不變。
