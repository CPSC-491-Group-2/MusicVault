import { expect, test } from "../fixtures";
import { ROUTES, visit } from "../support/routes";

// Hover states aren't scanned, on purpose. The spec allows blush text on a
// green hover fill (section 2), which axe would report as low contrast. Every
// page is scanned at rest, and the pages with toggles again with one pressed.

// Pressed chips swap fill and text color, so that state gets its own scan.
const PRESSED_CHIPS = [
  { path: "/", chip: "Rainy afternoon", fixme: "" },
  {
    path: "/ui",
    chip: "Not selected",
    fixme:
      'The /ui gallery chips are static examples with no onPressedChange, so they never toggle. Making them interactive needs a call on their "Selected" and "Not selected" labels. The gallery already renders pressed chips, so the scan above covers the pressed styles.',
  },
];

test.describe("axe scan", { tag: "@a11y" }, () => {
  for (const route of ROUTES) {
    test(`${route.name} (${route.path})`, async ({ page, a11yAllowlist }) => {
      test.skip(!!route.a11y?.skip, route.a11y?.skip);

      await visit(page, route.path);
      await expect(page).toPassAxe({ allowlist: a11yAllowlist });
    });
  }

  for (const { path, chip, fixme } of PRESSED_CHIPS) {
    test(`${path} with the "${chip}" chip pressed`, async ({
      page,
      a11yAllowlist,
    }) => {
      test.fixme(!!fixme, fixme);

      await visit(page, path);

      const toggle = page.getByRole("button", { name: chip, exact: true });
      await expect(toggle).toHaveAttribute("aria-pressed", "false");

      // The first click can land before React hydrates; retry until it takes.
      await expect(async () => {
        await toggle.click();
        await expect(toggle).toHaveAttribute("aria-pressed", "true", {
          timeout: 1_000,
        });
      }).toPass();

      await expect(page).toPassAxe({ allowlist: a11yAllowlist });
    });
  }
});
