import { expect, test, type Locator } from "../fixtures";
import { accessibleName } from "../support/focus";
import { visit } from "../support/routes";

// Fails if the element or anything inside it still transitions. Instant means
// no transitioned property, or a duration of at most 10ms.
async function expectInstant(locator: Locator) {
  const moving = await locator.evaluate((root) =>
    [root, ...root.querySelectorAll("*")].flatMap((el) => {
      const { transitionProperty, transitionDuration } = getComputedStyle(el);
      const instant =
        transitionProperty === "none" ||
        transitionDuration.split(",").every((duration) => parseFloat(duration) <= 0.01);

      return instant ? [] : [`<${el.localName}> ${transitionProperty} ${transitionDuration}`];
    }),
  );

  expect(moving, `"${await accessibleName(locator)}" still animates`).toEqual([]);
}

// Spec section 7: with reduced motion on, drop the animation, keep the state
// change.
test.describe("reduced motion", { tag: "@a11y" }, () => {
  test.beforeEach(async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
  });

  test("smooth scrolling is off", async ({ page }) => {
    await visit(page, "/");
    await expect(page.locator("html")).toHaveCSS("scroll-behavior", "auto");
  });

  for (const path of ["/", "/ui"]) {
    test(`chips on ${path} change instantly`, async ({ page }) => {
      await visit(page, path);

      // Chips are the toggle buttons.
      const chips = await page.locator("button[aria-pressed]").all();
      expect(chips.length).toBeGreaterThan(0);

      for (const chip of chips) {
        await expectInstant(chip);
      }
    });
  }

  test("popularity tiles on / change instantly", async ({ page }) => {
    await visit(page, "/");

    const tiles = await page
      .getByRole("region", { name: "What you play most, and what we find for you" })
      .getByRole("link")
      .all();
    expect(tiles.length).toBeGreaterThan(0);

    for (const tile of tiles) {
      await expectInstant(tile);
    }
  });
});
