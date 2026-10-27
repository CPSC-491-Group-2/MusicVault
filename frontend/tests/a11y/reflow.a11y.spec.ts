import { expect, test } from "../fixtures";
import { ROUTES, visit } from "../support/routes";

// WCAG 1.4.10 Reflow: at 320 CSS px wide, the page must not scroll sideways.
test.describe("reflow at 320px", { tag: "@a11y" }, () => {
  test.skip(({ isMobile }) => !isMobile, "reflow is checked in the mobile project");

  for (const route of ROUTES) {
    test(`${route.name} (${route.path})`, async ({ page }) => {
      test.skip(!!route.a11y?.skip, route.a11y?.skip);

      await page.setViewportSize({ width: 320, height: 844 });
      await visit(page, route.path);

      // Compared with clientWidth (the layout viewport), not window.innerWidth:
      // a mobile browser zooms out to fit a page that's too wide, innerWidth
      // grows with it, and the check could never fail.
      const { scrollWidth, clientWidth } = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
      }));

      expect(
        scrollWidth,
        `the page is ${scrollWidth}px wide in a ${clientWidth}px viewport`,
      ).toBeLessThanOrEqual(clientWidth);
    });
  }
});
