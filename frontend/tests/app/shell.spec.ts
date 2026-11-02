import { expect, test } from "../fixtures";
import { NAV_ROUTES, visit } from "../support/routes";

// Short on purpose: these double as an example of a plain feature test.
test.describe("app shell", { tag: "@smoke" }, () => {
  for (const route of NAV_ROUTES) {
    test(`${route.name} renders inside the shell`, async ({ page }) => {
      await visit(page, route.path);

      await expect(page.getByRole("navigation", { name: "Main" })).toBeVisible();
      await expect(page.getByRole("main").getByRole("heading", { level: 1 })).toHaveText(
        route.heading,
      );
    });
  }

  test("each nav item opens its page", async ({ page }) => {
    // Start on the last page so every click, Home included, has to navigate.
    await visit(page, NAV_ROUTES[NAV_ROUTES.length - 1].path);
    const nav = page.getByRole("navigation", { name: "Main" });

    for (const route of NAV_ROUTES) {
      await nav.getByRole("link", { name: route.name, exact: true }).click();

      await expect(page).toHaveURL((url) => url.pathname === route.path);
      await expect(page.getByRole("heading", { level: 1 })).toHaveText(route.heading);
    }
  });
});
