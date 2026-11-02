import { expect, test } from "../fixtures";
import { accessibleName } from "../support/focus";
import { ROUTES, visit } from "../support/routes";

test.describe("landmarks and headings", { tag: "@a11y" }, () => {
  for (const route of ROUTES) {
    test(`${route.name} (${route.path})`, async ({ page }) => {
      test.skip(!!route.a11y?.skip, route.a11y?.skip);

      await visit(page, route.path);

      // Soft assertions: report every problem on the page, not just the first.
      await expect.soft(page.locator("html")).toHaveAttribute("lang", "en");
      await expect.soft(page, "the page needs a <title>").toHaveTitle(/\S/);
      await expect.soft(page.getByRole("main")).toHaveCount(1);

      const h1 = page.getByRole("heading", { level: 1 });
      await expect.soft(h1).toHaveCount(1);
      await expect.soft(h1.first()).toHaveText(route.heading);

      // h1 to h6, or role="heading" with aria-level (which defaults to 2).
      const levels = await page.getByRole("heading").evaluateAll((headings) =>
        headings.map((heading) => {
          const level = heading.getAttribute("aria-level");
          if (level) return Number(level);
          return /^h[1-6]$/.test(heading.localName) ? Number(heading.localName[1]) : 2;
        }),
      );
      for (let i = 1; i < levels.length; i++) {
        expect
          .soft(levels[i], `heading ${i + 1} jumps from h${levels[i - 1]} to h${levels[i]}`)
          .toBeLessThanOrEqual(levels[i - 1] + 1);
      }

      const navNames: string[] = [];
      for (const nav of await page.getByRole("navigation").all()) {
        navNames.push(await accessibleName(nav));
      }
      expect
        .soft(navNames, "every nav needs an accessible name (aria-label)")
        .not.toContain("");
      expect
        .soft(new Set(navNames).size, `nav names have to differ: ${navNames.join(", ")}`)
        .toBe(navNames.length);
    });
  }
});
