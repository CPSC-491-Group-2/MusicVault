# Frontend tests

These tests use [Playwright](https://playwright.dev). Playwright opens the app in a real browser (Chromium), clicks and types like a person would, and checks what's on the screen. There are two kinds of tests:

- **Smoke tests**: pages render, the nav works, links point where they should.
- **Accessibility tests**: an automated [axe](https://github.com/dequelabs/axe-core) scan of every page, plus checks for keyboard use, focus rings, landmarks and headings, tap target size, reflow at 320px and reduced motion. They enforce section 11 of the [design spec](../../docs/design-spec.md).

Every test runs twice: once in a desktop window (1440 x 900) and once as a phone (390 x 844).

You don't need the backend. Tests answer every `/api` request themselves (see [Mocking the API](#mocking-the-api)).

First time only:

```bash
cd frontend
npm install
npx playwright install chromium
```

## What's where

```text
tests/
  fixtures/     test, expect, mockApi, toPassAxe, the axe allowlist. Import from here.
  support/      routes.ts (every page in the app) and focus.ts (keyboard helpers)
  templates/    feature.spec.ts.txt, a starter to copy
  a11y/         the accessibility suite
  app/          smoke tests for the logged-in shell
  marketing/    smoke tests for the splash page
```

Tests live in `tests/<area>/` and are named `<thing>.spec.ts`. Accessibility-focused specs end in `.a11y.spec.ts`. Whoever builds a feature creates its folder, e.g. `tests/swipe/`.

## Running tests

```bash
npm run test:e2e                     # everything, both desktop and mobile
npm run test:a11y                    # only the accessibility tests
npm run test:smoke                   # only the smoke tests
npx playwright test tests/a11y/keyboard.a11y.spec.ts   # one file
npx playwright test -g "Swipe"       # tests whose name contains "Swipe"
npx playwright test --project=mobile # only the phone run (or --project=desktop)
npm run test:ui                      # UI mode: pick tests, watch them run, time-travel through each step
npx playwright test --headed --project=desktop          # watch the browser while it runs
```

`npm run test:e2e` starts the app with `npm run dev -- -p 3100` and stops it when it's done. If something is already running on port 3100, the tests use that instead. So if you want to keep a dev server open while you write tests, start it with `npm run dev -- -p 3100`.

To test a deployed site instead of your machine, set `PLAYWRIGHT_BASE_URL`. No local server is started then:

```bash
PLAYWRIGHT_BASE_URL=https://musicvault.example.com npm run test:e2e
```

Two more helpers:

- `npm run test:codegen` opens a browser on `http://localhost:3100` and writes test code as you click around. Start the dev server on port 3100 first. Treat the output as a draft: swap its locators for role and label ones (see below).
- `npm run test:report` opens the HTML report of the last run that produced one (CI always does; locally add `--reporter=html`).

Good to know: `next dev` shows a floating dev tools button in the bottom left corner. It sits on top of the mobile tab bar, so the fixtures hide it in every test. Production builds don't have it.

## Adding a page

Add one line to `ROUTES` in [`support/routes.ts`](support/routes.ts):

```ts
{ name: "Settings", path: "/settings", heading: "Settings", area: "app", inNav: true },
```

That's it. The page is now covered by the axe scan, the landmark and heading checks, the keyboard checks (every Tab stop has a visible focus ring, focus never gets stuck or lands on something hidden) and the 320px reflow check. With `inNav: true` it also gets the shell smoke tests and the `aria-current="page"` check.

- `name`: what to call the page in test names. For `inNav` pages it must be the nav link's label.
- `heading`: the page's h1, exactly. Use a RegExp if it changes, e.g. `/^Welcome back/`.
- `a11y: { skip: "reason" }`: only if the page truly can't be scanned. It still shows up in every run as skipped, with your reason.

## Writing a feature test

1. Copy [`templates/feature.spec.ts.txt`](templates/feature.spec.ts.txt) to `tests/<feature>/<thing>.spec.ts` (drop the `.txt`).
2. Import `test` and `expect` from the fixtures, never from `@playwright/test`. Lint fails if you do:

   ```ts
   import { expect, test } from "../fixtures";
   ```

3. Find elements the way a person would, by role and accessible name, or by label:

   ```ts
   await page.getByRole("button", { name: "Save to vault" }).click();
   await page.getByLabel("Find a song").fill("Porch Light");
   await expect(page.getByRole("heading", { level: 1 })).toHaveText("Your vault");
   ```

   If a test can't find something by role or label, a screen reader user probably can't either, so fix the markup first. Use `data-testid` only when there's no accessible handle, and leave a comment saying why.

Useful helpers:

- `visit(page, path)` from `support/routes.ts` opens a page and waits until its h1 is on screen and the fonts have loaded.
- `support/focus.ts` has `tabTo(page, locator)`, `tabThrough(page)`, `expectVisibleFocus(locator)` and `expectMinTargetSize(locator, 44)`.

## Mocking the API

The backend isn't running during tests. Every request to `/api/...` gets a `503` with `{ "error": "not mocked in tests" }` unless the test answers it. Use the `mockApi` fixture, with a response type from [`types/api.ts`](../types/api.ts):

```ts
import type { HealthResponse } from "@/types/api";

import { expect, test } from "../fixtures";

test("shows the backend status", async ({ page, mockApi }) => {
  await mockApi<HealthResponse>("health", { status: "ok", service: "MusicVault API" });

  await page.goto("/status");
  await expect(page.getByText("MusicVault API")).toBeVisible();

  // Nothing went to an API route the test forgot to mock.
  expect(mockApi.calls).toEqual([]);
});
```

- `"health"` means `/api/v1/health`. A path starting with `/` is used as is, e.g. `"/api/auth/spotify/login"`.
- Options: `{ status: 201 }` for another status (the default is 200), `{ method: "POST" }` to answer only that method.
- Mock before the page makes the request, usually before `page.goto`.
- `mockApi.calls` lists the URLs nothing mocked, in order.
- Only requests made by the browser can be mocked. A fetch inside a server component runs on the Next server and goes straight to `BACKEND_URL`. No page does that today.

## Checking accessibility of your feature

Scan just your part of the page:

```ts
test("saved songs are accessible", async ({ page, a11yAllowlist }) => {
  await page.goto("/library");
  await expect(page).toPassAxe({ include: "#saved-songs", allowlist: a11yAllowlist });
});
```

`toPassAxe` checks WCAG 2.0, 2.1 and 2.2 at levels A and AA. Its options:

- `include`: a CSS selector to scan inside. Give your feature's container an id to aim at.
- `exclude`: CSS selectors to leave out.
- `disableRules`: axe rule ids to turn off. Every use needs a comment right there explaining why, or it won't pass review.
- `allowlist`: pass the `a11yAllowlist` fixture (see below).

Scan each state that looks different: open the menu, press the toggle, show the error, then scan again. Hover states are the exception. The spec allows blush text on a green hover fill, which axe would flag, so they aren't scanned.

## When axe fails

The failure lists each problem like this:

```text
color-contrast (serious): Elements must meet minimum color contrast ratio thresholds
  https://dequeuniversity.com/rules/axe/4.14/color-contrast?application=playwright
  - .text-olive\/45
```

That's the rule id, how serious it is, what's wrong, a page that explains the rule and how to fix it, and up to five CSS selectors of elements that fail.

1. Open the link. It explains the fix better than anything here.
2. For more detail, run the test with `--reporter=html`, then `npm run test:report`. Each scan attaches its full results as `axe-results`. Failed tests also have a screenshot and a trace: click the trace to step through the test and inspect the page at the moment it failed.
3. Fix the markup: a missing label or alt text, a color pair the spec doesn't allow, a skipped heading level.

[`fixtures/a11y-allowlist.ts`](fixtures/a11y-allowlist.ts) exists for rare cases where a violation can't be fixed yet. Every entry needs a reason and a Jira ticket for the real fix, and adding one needs a review from the design spec owner (CODEOWNERS enforces it). Never add an entry to get a PR green. If a test is blocked by a known bug you can't fix in your PR, mark that test `test.fixme(...)` with a comment naming the problem.

## Tags

Tests are tagged so groups can run on their own:

- `@a11y`: everything in `tests/a11y/`. `npm run test:a11y`
- `@smoke`: the quick "does it render" tests. `npm run test:smoke`

Add your own on a group or a single test:

```ts
test.describe("vault", { tag: "@vault" }, () => {
  test("lists saved songs", async ({ page }) => {
    // ...
  });
});

test("exports a CSV", { tag: ["@vault", "@export"] }, async ({ page }) => {
  // ...
});
```

Then `npx playwright test --grep @vault`, or `--grep-invert @a11y` to run everything except a tag.

## CI

The `frontend-e2e` job in [`.github/workflows/docker-build.yml`](../../.github/workflows/docker-build.yml) runs on every pull request and every push to `master`. It builds the app, serves the production build on port 3100, and runs every test in both projects with 2 workers. A failing test gets one retry; one that only passes on the retry is reported as flaky. A `test.only` left in the code fails the run.

Failures show up as annotations on the pull request. For the full picture, open the failed run in the Actions tab, download the `playwright-report` artifact at the bottom of its summary page (kept for 7 days), unzip it and run:

```bash
npx playwright show-report playwright-report
```

It has the HTML report with every failure's error, screenshot, trace and axe results.
