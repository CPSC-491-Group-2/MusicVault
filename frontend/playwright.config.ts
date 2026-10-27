import { defineConfig } from "@playwright/test";

// Set PLAYWRIGHT_BASE_URL to run against a site that's already up (a preview
// deploy, say). The local server below is skipped in that case.
const baseURL = process.env.PLAYWRIGHT_BASE_URL;
const PORT = 3100;

// Shared device settings. Adding a browser is one more line in `projects`:
//   { name: "desktop-firefox", use: { browserName: "firefox", ...desktop } },
// Firefox doesn't support isMobile, so pair it with `desktop` only.
const desktop = { viewport: { width: 1440, height: 900 } };
const mobile = {
  viewport: { width: 390, height: 844 },
  isMobile: true,
  hasTouch: true,
  deviceScaleFactor: 3,
};

export default defineConfig({
  testDir: "./tests",
  testMatch: "**/*.spec.ts",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: process.env.CI
    ? [["github"], ["html", { open: "never" }]]
    : "list",
  use: {
    baseURL: baseURL ?? `http://localhost:${PORT}`,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop", use: { browserName: "chromium", ...desktop } },
    { name: "mobile", use: { browserName: "chromium", ...mobile } },
  ],
  // The backend isn't started for tests. Pages have to render without it, and
  // the mockApi fixture answers every /api request (tests/fixtures/api.ts).
  webServer: baseURL
    ? undefined
    : {
        command: process.env.CI
          ? `npm run build && npm run start -- -p ${PORT}`
          : `npm run dev -- -p ${PORT}`,
        url: `http://localhost:${PORT}`,
        reuseExistingServer: !process.env.CI,
        timeout: 180_000,
      },
});
