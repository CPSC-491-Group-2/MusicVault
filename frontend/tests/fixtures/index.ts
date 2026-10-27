// Import test and expect from here, not from "@playwright/test":
//
//   import { test, expect } from "../fixtures";
//
// `test` adds the mockApi and a11yAllowlist fixtures, and `expect` adds the
// toPassAxe matcher. Lint blocks importing @playwright/test in specs.
import { test as base, expect as baseExpect } from "@playwright/test";

import { A11Y_ALLOWLIST, type AllowlistEntry } from "./a11y-allowlist";
import { createMockApi, type MockApi } from "./api";
import { axeMatchers } from "./axe";

export const test = base.extend<{
  mockApi: MockApi;
  a11yAllowlist: AllowlistEntry[];
  hideNextDevTools: void;
}>({
  // auto: every test gets the /api catch-all, even ones that never use mockApi.
  mockApi: [
    async ({ page }, use) => {
      await use(await createMockApi(page));
    },
    { auto: true },
  ],
  a11yAllowlist: [A11Y_ALLOWLIST, { option: true }],
  // `next dev` floats a dev tools button over the bottom left corner, on top of
  // the mobile tab bar, where it swallows clicks. It isn't part of the app and
  // production builds don't have it, so every test hides it.
  hideNextDevTools: [
    async ({ page }, use) => {
      await page.addInitScript(() => {
        const sheet = new CSSStyleSheet();
        sheet.replaceSync("nextjs-portal { display: none !important; }");
        document.adoptedStyleSheets.push(sheet);
      });
      await use();
    },
    { auto: true },
  ],
});

export const expect = baseExpect.extend(axeMatchers);

export type { Locator, Page } from "@playwright/test";
export type { AllowlistEntry } from "./a11y-allowlist";
export type { MockApi } from "./api";
export type { AxeOptions } from "./axe";
