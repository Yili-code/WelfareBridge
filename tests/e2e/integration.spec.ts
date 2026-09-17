import { test, expect } from "@playwright/test";

test("one origin serves database APIs and keeps appeal authorization separate", async ({ request }) => {
  const health = await request.get("/api/health");
  expect(health.ok()).toBeTruthy();
  expect((await health.json()).database).toBe("ok");
  const list = await request.get("/api/benefits?page_size=3");
  const body = await list.json();
  expect(body.total).toBeGreaterThan(0);
  const detail = await request.get(`/api/benefits/${encodeURIComponent(body.items[0].id)}`);
  expect(detail.ok()).toBeTruthy();
  expect((await detail.json()).benefit.title).toBe(body.items[0].title);
  expect((await request.get("/api/appeals")).status()).toBe(401);
});

test("first visit invites a data card; the step-by-step dialog leads to grouped results, quick answers and saving", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  let matchCalls = 0;
  await page.route("**/api/public/match", async route => { matchCalls++; await route.continue(); });
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "福利補助導覽", level: 1 })).toBeVisible();
  await page.getByRole("region", { name: /花 2 分鐘建立資料卡/ }).getByRole("button", { name: "開始建立資料卡" }).click();

  // 小視窗一次一題
  const dialog = page.locator(".modal");
  await expect(dialog.getByRole("heading", { name: "這張資料卡是為誰建立的？" })).toBeVisible();
  const next = dialog.getByRole("button", { name: "下一題 →" });
  await next.click();
  await dialog.getByRole("button", { name: "就學、學費或獎助學金", exact: true }).click();
  await next.click();
  await dialog.getByRole("button", { name: "18～未滿 25 歲", exact: true }).click();
  await dialog.getByLabel("實際年齡（選填，填了比對會更準）").fill("22");
  await next.click();
  await dialog.getByRole("button", { name: "戶籍與居住地在同一縣市，設籍已滿半年", exact: true }).click();
  await dialog.getByLabel("戶籍及居住縣市").selectOption("臺北市");
  await next.click();
  await dialog.getByRole("button", { name: "大學、二專或五專後兩年", exact: true }).click();
  await expect(dialog.getByText(/第 5 題／共 10 題/)).toBeVisible(); // 單選題選完自動到下一題
  const skip = dialog.getByRole("button", { name: "跳過", exact: true });
  while (await skip.isVisible()) await skip.click();
  await dialog.getByRole("button", { name: "完成並比對", exact: true }).click();
  await expect(dialog).toHaveCount(0);

  // 結果頁：摘要＋依比對狀態分區
  const results = page.getByRole("region", { name: "我的資料卡" });
  await expect(results.getByRole("heading", { name: "我自己的資料卡" })).toBeVisible();
  await expect(results.locator(".group-title").first()).toBeVisible({ timeout: 30000 });

  // 補這幾題：直接回答就重新比對
  const quick = page.getByRole("region", { name: "補這幾題，就能確認更多補助" });
  if (await quick.isVisible()) {
    const before = matchCalls;
    await quick.locator(".qq").first().getByRole("button").first().click();
    await expect.poll(() => matchCalls).toBeGreaterThan(before);
  }

  // 收藏 → 收藏清單 → 列印
  await results.locator(".group .card").first().getByRole("button", { name: "☆ 收藏" }).click();
  await page.getByRole("tab", { name: /收藏清單/ }).click();
  const saved = page.getByRole("region", { name: "收藏清單" });
  await expect(saved.locator(".card")).toHaveCount(1);
  await page.evaluate(() => { (window as unknown as { printed: number }).printed = 0; window.print = () => { (window as unknown as { printed: number }).printed++; }; });
  await saved.getByRole("button", { name: /列印／存成 PDF/ }).click();
  await expect.poll(() => page.evaluate(() => (window as unknown as { printed: number }).printed)).toBe(1);
  await expect(page.locator(".print-sheet li")).toHaveCount(1);

  // 查詢：依截止日排序、打開詳情
  await page.getByRole("tab", { name: "查詢補助與服務" }).click();
  await page.getByLabel("排序方式").selectOption("deadline");
  await expect(page.locator("#wui-panel-search .card .tag.due").first()).toBeVisible();
  await page.locator("#wui-panel-search .card").first().getByRole("button", { name: "查看詳情 →" }).click();
  const drawer = page.getByRole("dialog");
  await expect(drawer.getByText("資格初步比對")).toBeVisible();
  await expect(drawer.getByRole("link", { name: "前往官方頁面 ↗" })).toBeVisible();
  // 使用者介面不顯示作業資訊
  await expect(page.getByText(/信心|規則式|本地 AI|資料中心|Schema/)).toHaveCount(0);
  await page.screenshot({ path: "test-results/welfare-ui.png", fullPage: true });
  expect(errors).toEqual([]);
});

test("assistant answers are written into the data card and the main screen re-matches", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("wf.profiles", JSON.stringify([{ id: "test", nickname: "測試對象", relation: "self", region: "臺北市", currentRegion: "臺北市", age: 30, economy: "不確定", identities: [], needs: [], createdAt: "",
      screening: { needs: ["求職、失業或職業訓練"], age: ["30～未滿 65 歲"], residence: ["戶籍與居住地在同一縣市，設籍已滿半年"] } }]));
    localStorage.setItem("wf.activeProfile", JSON.stringify("test"));
  });
  const learned = [{ attribute_id: "employment.status", label: "就業狀態", type: "enum", value: "unemployed", value_label: "失業中", options: [{ value: "unemployed", label: "失業中" }], source: "asked", evidence: "失業中" }];
  let matchBodies: { profile: { attributes: Record<string, unknown> } }[] = [];
  await page.route("**/api/public/match", async route => { matchBodies.push(route.request().postDataJSON()); await route.continue(); });
  await page.route("**/api/assistant", route => {
    const answered = route.request().postDataJSON().messages.length > 0;
    return route.fulfill({ json: { reply: answered ? "目前能問的條件都確認了" : "你目前的就業狀態是？", quickReplies: answered ? [] : ["失業中", "不確定"], summary: "", mainRequest: "", search: null, guidance_profile: {}, learned: answered ? learned : [], question_attribute: answered ? "" : "employment.status", candidate_count: 3, turn_count: answered ? 1 : 0, completed: false } });
  });
  await page.goto("/");
  await expect(page.locator(".card .badge").first()).toBeVisible({ timeout: 30000 });
  matchBodies = [];
  await page.getByRole("button", { name: /問問小幫手/ }).click();
  await page.getByRole("button", { name: "失業中", exact: true }).click();
  await expect(page.getByText("已寫進資料卡：")).toBeVisible();
  await expect.poll(() => matchBodies.some(body => JSON.stringify(body.profile.attributes["employment.status"]).includes("unemployed"))).toBeTruthy();
  // 補助清單在主畫面更新；聊天視窗不列補助
  await expect(page.getByRole("dialog", { name: "福利小幫手" }).locator(".card")).toHaveCount(0);
  await page.getByRole("tab", { name: /我的資料卡/ }).click();
  await page.getByText(/補充的資料（/).click();
  await expect(page.getByRole("combobox", { name: "就業狀態" })).toHaveValue("unemployed");
});

test("unknown service failure is visible, not an empty success", async ({ page }) => {
  await page.route("**/api/public/benefits", route => route.fulfill({ status: 503, body: "unavailable" }));
  await page.goto("/");
  await expect(page.getByRole("alert").filter({ hasText: "補助資料服務暫時無法使用" })).toBeVisible();
});

test("old user pages redirect to the new home page", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/$/);
  await page.goto("/my-benefits");
  await expect(page.getByRole("tab", { name: /我的資料卡/ })).toHaveAttribute("aria-selected", "true");
});

test("appeal submission retry, admin read and status update", async ({ page, request }) => {
  const password = process.env.TEST_ADMIN_PASSWORD;
  test.skip(!password, "Use TEST_ADMIN_PASSWORD with an isolated WELFARE_DB_PATH for this write test.");
  const id = `integration_${Date.now()}`;
  const title = `整合測試需求 ${id}`;
  const data = { profileId: null, profileNickname: "整合測試", region: "臺北市", identities: [], age: 22, mainRequest: title, summary: "測試資料", transcript: [{ role: "user", text: "需要學費協助" }] };
  for (let i = 0; i < 2; i++) {
    expect((await request.post("/api/appeals", { headers: { "Idempotency-Key": id }, data })).status()).toBe(201);
  }
  const headers = { Authorization: `Bearer ${password}` };
  const stored = await (await request.get("/api/appeals", { headers })).json();
  expect(stored.filter((item: { id: string }) => item.id === id)).toHaveLength(1);
  expect((await request.patch("/api/appeals", { headers, data: { id, status: "reviewing" } })).ok()).toBeTruthy();
  await page.goto("/admin");
  await page.getByLabel("後台密碼").fill(password!);
  await page.getByRole("button", { name: "讀取需求", exact: true }).click();
  await expect(page.getByText(title, { exact: true })).toBeVisible();
});
