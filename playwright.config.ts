import { defineConfig } from "@playwright/test";
export default defineConfig({
 testDir: "tests/e2e", outputDir: "test-results/browser", fullyParallel: false, workers: 1,
 use: { baseURL: process.env.TEST_BASE_URL || "http://127.0.0.1:3000", channel: "chrome", headless: true, screenshot: "only-on-failure" },
 timeout: 60000,
});
