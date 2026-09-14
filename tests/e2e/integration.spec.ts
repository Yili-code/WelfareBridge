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

test("ten-question onboarding reaches live matching, shared profile and source detail", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  await page.goto("/");
  await page.getByRole("button", { name: "開始建立我的檔案" }).click();
  const answers = ["就學、學費或獎助學金", "18～未滿 25 歲", "戶籍與居住地在同一縣市，設籍已滿半年", "大學、二專或五專後兩年", "已取得低收入戶資格", "以上皆無／不確定", "受僱工作中，包含兼職", "租屋，包含整戶或分租", "以上皆無／不確定", "沒有／不確定"];
  for (let i = 0; i < answers.length; i++) {
    await page.getByRole("button", { name: answers[i], exact: true }).click();
    if (i === 1) await page.getByRole("spinbutton").fill("22");
    if (i === 2) await page.getByLabel("戶籍及居住縣市").selectOption("臺北市");
    await page.getByRole("button", { name: i === 9 ? "完成建檔" : "下一步", exact: true }).click();
  }
  await expect(page).toHaveURL(/dashboard/);
  const official = page.getByRole("region", { name: "官方補助媒合" });
  await expect(official.getByRole("link", { name: "查看條件與官方來源" }).first()).toBeVisible({ timeout: 30000 });
  await page.screenshot({ path: "test-results/dashboard.png", fullPage: true });
  await page.getByRole("link", { name: "補充條件與完整媒合" }).click();
  await expect(page).toHaveURL(/my-benefits/);
  await expect(page.getByRole("spinbutton").first()).toBeVisible();
  await expect(page.locator('input[type="number"][value="22"]')).toHaveCount(1);
  await page.getByRole("button", { name: "開始比對", exact: true }).click();
  await expect(page.getByRole("heading", { name: "為你推薦", exact: true })).toBeVisible({ timeout: 30000 });
  await page.getByRole("link", { name: "資料中心", exact: true }).click();
  await expect(page.getByRole("heading", { name: "資料中心", exact: true })).toBeVisible();
  await page.getByPlaceholder("名稱、機關、關鍵字或原文").fill("補助");
  await page.getByRole("button", { name: "搜尋", exact: true }).click();
  const table = page.getByRole("table").filter({ has: page.getByRole("columnheader", { name: "提供機關", exact: true }) });
  const row = table.locator("tbody tr").first();
  await expect(row).not.toContainText("沒有符合條件的資料");
  await row.getByRole("cell").first().click();
  await expect(page).toHaveURL(/data-center\/.+/);
  await page.reload();
  await expect(page.getByRole("link", { name: /返回.*資料|回到.*資料|資料中心/ }).first()).toBeVisible();
  await page.screenshot({ path: "test-results/benefit-detail.png", fullPage: true });
  expect(errors).toEqual([]);
});

test("unknown service failure is visible, not an empty success", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("wf.profiles", JSON.stringify([{ id: "test", nickname: "測試對象", relation: "self", region: "", age: null, economy: "不確定", identities: [], needs: [], createdAt: "" }]));
    localStorage.setItem("wf.activeProfile", JSON.stringify("test"));
  });
  await page.route("**/api/matching", route => route.fulfill({ status: 503, body: "unavailable" }));
  await page.goto("/dashboard");
  await expect(page.getByRole("region", { name: "官方補助媒合" }).getByRole("alert")).toContainText("暫時無法連線");
  await expect(page.getByRole("button", { name: "重試", exact: true })).toBeVisible();
});

test("profile parsing, follow-up questions and queued pipeline execution", async ({ request }) => {
  const parsed = await request.post("/api/profile/parse", { data: { text: "我是22歲的大學生，戶籍在臺北市", use_llm: false } });
  expect(parsed.ok()).toBeTruthy();
  const { profile } = await parsed.json();
  expect(profile.attributes["applicant.age"].value).toBe(22);
  const questions = await request.post("/api/profile/questions", { data: { profile, mode: "step", max_questions: 1 } });
  expect(questions.ok()).toBeTruthy();
  expect(Array.isArray((await questions.json()).questions)).toBeTruthy();
  const job = await request.post("/api/pipeline/run", { data: { source_ids: ["__integration_no_documents__"], use_llm: false, limit: 1 } });
  expect(job.ok()).toBeTruthy();
  const id = (await job.json()).task.task_id;
  await expect.poll(async () => {
    const tasks = await (await request.get("/api/crawler/tasks")).json();
    return tasks.find((item: { task_id: string }) => item.task_id === id)?.status;
  }, { timeout: 30000 }).toBe("finished");
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
