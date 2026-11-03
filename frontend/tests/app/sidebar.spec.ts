import { expect, test, type Locator, type Page } from "../fixtures";
import { NAV_ROUTES, visit } from "../support/routes";

const OPEN_WIDTH = 260;
const COLLAPSED_WIDTH = 76;

const LAST_NAV = NAV_ROUTES[NAV_ROUTES.length - 1];

function rail(page: Page) {
  return page.getByRole("complementary");
}

function collapseHandle(page: Page) {
  return page.getByRole("button", { name: "Collapse sidebar" });
}

function expandHandle(page: Page) {
  return page.getByRole("button", { name: "Expand sidebar" });
}

function mainNav(page: Page) {
  return page.getByRole("navigation", { name: "Main" });
}

async function expectWidth(page: Page, width: number) {
  await expect
    .poll(async () => Math.round((await rail(page).boundingBox())?.width ?? 0))
    .toBe(width);
}

async function collapse(page: Page) {
  // The first click can land before React hydrates; retry until it takes.
  await expect(async () => {
    await collapseHandle(page).click();
    await expect(expandHandle(page)).toBeAttached({ timeout: 1_000 });
  }).toPass();

  await expectWidth(page, COLLAPSED_WIDTH);
}

// /ui has several "Email" fields; this is the one in the submittable form.
function errorForm(page: Page): Locator {
  return page
    .locator("form")
    .filter({ has: page.getByRole("button", { name: "Submit", exact: true }) });
}

function focusInRail(page: Page) {
  return page.evaluate(
    () => !!document.activeElement?.closest("#app-sidebar"),
  );
}

test.describe("sidebar", { tag: "@smoke" }, () => {
  test.skip(
    ({ isMobile }) => isMobile,
    "desktop-only: the sidebar and its edge handle are not rendered at 390px",
  );

  test("the edge handle collapses the rail", async ({ page }) => {
    await visit(page, "/dashboard");
    await expectWidth(page, OPEN_WIDTH);
    await expect(collapseHandle(page)).toHaveAttribute("aria-expanded", "true");

    await collapse(page);

    const handle = expandHandle(page);
    await expect(handle).toHaveAttribute("aria-expanded", "false");
    await expect(handle).toHaveAttribute("aria-controls", "app-sidebar");
  });

  test("a reload keeps it collapsed", async ({ page, context }) => {
    await visit(page, "/dashboard");
    await collapse(page);

    await expect
      .poll(async () =>
        (await context.cookies()).find((cookie) => cookie.name === "mv-sidebar")
          ?.value,
      )
      .toBe("collapsed");

    await page.reload();
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    await expectWidth(page, COLLAPSED_WIDTH);
    await expect(expandHandle(page)).toBeAttached();
  });

  test("the [ shortcut toggles the rail", async ({ page }) => {
    await visit(page, "/dashboard");
    await expectWidth(page, OPEN_WIDTH);

    // The first press can land before React hydrates; retry until it takes.
    await expect(async () => {
      await page.keyboard.press("[");
      await expect(expandHandle(page)).toBeAttached({ timeout: 1_000 });
    }).toPass();
    await expectWidth(page, COLLAPSED_WIDTH);

    await page.keyboard.press("[");
    await expect(collapseHandle(page)).toBeAttached();
    await expectWidth(page, OPEN_WIDTH);
  });

  test("typing [ in a field does not toggle the rail", async ({ page }) => {
    await visit(page, "/ui");

    // Toggle once first, so a lost press can't make the next check pass for
    // the wrong reason.
    await expect(async () => {
      await page.keyboard.press("[");
      await expect(expandHandle(page)).toBeAttached({ timeout: 1_000 });
    }).toPass();
    await page.keyboard.press("[");
    await expect(collapseHandle(page)).toBeAttached();
    await expectWidth(page, OPEN_WIDTH);

    const email = errorForm(page).getByRole("textbox", { name: "Email" });
    await email.press("[");

    await expect(email).toHaveValue("[");
    await expect(collapseHandle(page)).toHaveAttribute("aria-expanded", "true");
    await expectWidth(page, OPEN_WIDTH);
  });

  test("collapsed nav links keep their names and still navigate", async ({
    page,
  }) => {
    await visit(page, "/dashboard");
    await collapse(page);

    const nav = mainNav(page);

    for (const route of NAV_ROUTES) {
      await expect(
        nav.getByRole("link", { name: route.name, exact: true }),
      ).toHaveAccessibleName(route.name);
    }

    await nav.getByRole("link", { name: LAST_NAV.name, exact: true }).click();

    await expect(page).toHaveURL((url) => url.pathname === LAST_NAV.path);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(
      LAST_NAV.heading,
    );
    await expectWidth(page, COLLAPSED_WIDTH);
  });

  test("collapsed account details leave the tab order", async ({ page }) => {
    await visit(page, "/dashboard");

    const lastLink = mainNav(page).getByRole("link", {
      name: LAST_NAV.name,
      exact: true,
    });
    await lastLink.focus();
    await page.keyboard.press("Tab");
    await expect.poll(() => focusInRail(page)).toBe(true);

    await collapse(page);

    // Hidden by visibility, which lands a beat after the rail has narrowed.
    const logOut = rail(page).locator("button", { hasText: "Log out" });
    await expect
      .poll(() => logOut.evaluate((el) => getComputedStyle(el).visibility))
      .toBe("hidden");

    await lastLink.focus();
    await page.keyboard.press("Tab");

    expect(await focusInRail(page)).toBe(false);
    await expect(logOut).not.toBeFocused();
  });
});
