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

test("data card reaches live matching, labels search results and opens user-facing detail", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "福利補助導覽", level: 1 })).toBeVisible();
  await page.getByRole("tab", { name: /我的資料卡/ }).click();
  for (const option of ["就學、學費或獎助學金", "18～未滿 25 歲", "戶籍與居住地在同一縣市，設籍已滿半年", "大學、二專或五專後兩年", "已取得低收入戶資格"]) {
    await page.getByLabel(option, { exact: true }).check();
  }
  await page.getByLabel("實際年齡（選填，填了比對會更準）").fill("22");
  await page.getByLabel("戶籍及居住縣市").selectOption("臺北市");
  await page.getByRole("button", { name: "儲存並比對", exact: true }).click();
  const results = page.getByRole("region", { name: "我的資料卡" });
  await expect(results.getByText("主動提醒：您可能符合")).toBeVisible({ timeout: 30000 });
  await page.getByRole("tab", { name: "查詢補助與服務" }).click();
  await expect(page.locator(".card .badge").first()).toBeVisible({ timeout: 30000 });
  await page.locator(".card").first().click();
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
  await expect(page.getByRole("combobox", { name: "就業狀態" })).toHaveValue("unemployed");
});

test("unknown service failure is visible, not an empty success", async ({ page }) => {
  await page.route("**/api/public/benefits", route => route.fulfill({ status: 503, body: "unavailable" }));
  await page.goto("/");
  await expect(page.getByRole("alert")).toContainText("補助資料服務暫時無法使用");
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
