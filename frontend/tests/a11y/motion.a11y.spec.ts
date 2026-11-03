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

  test("buttons, icon buttons and icon links on /ui change instantly", async ({ page }) => {
    await visit(page, "/ui");

    // The gallery's sections have no names, so find each one by its heading.
    const section = (title: string) =>
      page.locator("section").filter({
        has: page.getByRole("heading", { level: 2, name: title, exact: true }),
      });
    const buttons = section("Button");
    const icons = section("icons");
    await expect(buttons.getByRole("button").first()).toBeVisible();

    const targets = [
      ...(await buttons.getByRole("button").all()),
      ...(await buttons.getByRole("link").all()),
      ...(await section("IconButton").getByRole("button").all()),
      ...(await icons.getByRole("link").all()),
      ...(await icons.getByRole("button").all()),
    ];
    expect(targets.length).toBeGreaterThan(0);

    for (const target of targets) {
      await expectInstant(target);
    }
  });

  test("the sidebar collapses instantly", async ({ page, isMobile }) => {
    await visit(page, "/dashboard");

    const collapse = page.getByRole("button", { name: "Collapse sidebar" });

    if (isMobile) {
      await expect(collapse).toHaveCount(0);

      return;
    }

    const shell = page.locator("[style*='--sidebar-w']");
    const aside = page.locator("#app-sidebar");
    await expectInstant(shell);
    await expectInstant(aside);

    await collapse.click();
    await expect(page.getByRole("button", { name: "Expand sidebar" })).toBeVisible();

    // The column is already at its collapsed width on the next painted frame.
    const width = await aside.evaluate(async (el) => {
      await new Promise(requestAnimationFrame);

      return el.getBoundingClientRect().width;
    });
    expect(width).toBe(76);
  });

  test("the error field on /ui appears without shaking", async ({ page }) => {
    await visit(page, "/ui");

    const form = page.locator("form").filter({
      has: page.getByRole("button", { name: "Submit", exact: true }),
    });
    const field = form.getByRole("textbox", { name: "Email" }).locator("..");

    // The first click can land before React hydrates; retry until it takes.
    await expect(async () => {
      await form.getByRole("button", { name: "Submit", exact: true }).click();
      await expect(form.getByText("Enter your email")).toBeVisible({ timeout: 1_000 });
    }).toPass();

    // The class still goes on, so the shake is killed by CSS, not by the code.
    await expect(field).toHaveClass(/\bmv-shake\b/);
    await expect(field).toHaveCSS("animation-name", "none");
  });

  test("the loading stack on /ui holds a still frame", async ({ page }) => {
    await visit(page, "/ui");

    const stack = page.getByRole("status", { name: "Loading your vault" }).locator("> div");
    const layers = stack.locator("> svg");

    await expect(stack).toHaveCSS("animation-name", "none");
    expect(await layers.count()).toBeGreaterThan(0);

    for (const layer of await layers.all()) {
      await expect(layer).toHaveCSS("animation-name", "none");
    }
  });

  test("the button trace ring on /ui holds a still frame", async ({ page }) => {
    await visit(page, "/ui");

    // Loading swaps the label, so match either name to keep one handle.
    const sync = page.getByRole("button", { name: /^(Sync library|Syncing)$/ });

    await expect(async () => {
      await sync.click();
      await expect(sync).toHaveAttribute("aria-busy", "true", { timeout: 1_000 });
    }).toPass();

    const arc = sync.locator("> svg > rect").nth(1);
    await expect(arc).toHaveCSS("animation-name", "none");
    await expect(arc).toHaveCSS("stroke-dasharray", "60px, 40px");
  });
});

// Spec section 7: transitions run 150 to 250ms, and the focus ring appears at
// once, so only its offset may animate.
const MAX_DURATION = 0.25;
const UNANIMATABLE = ["outline", "outline-color", "outline-width", "all"];

test.describe("normal motion", { tag: "@a11y" }, () => {
  for (const path of ["/ui", "/dashboard"]) {
    test(`transitions on ${path} are short and spare the focus ring`, async ({ page }) => {
      await visit(page, path);

      const { checked, violations } = await page.evaluate(
        ({ maxDuration, unanimatable }) => {
          const elements = new Set<Element>(
            document.querySelectorAll("button, a[href], input, [aria-pressed]"),
          );
          const aside = document.querySelector("#app-sidebar");
          const grid = aside?.closest("[style*='--sidebar-w']");

          for (const extra of [aside, grid]) {
            if (extra) {
              elements.add(extra);
            }
          }

          const violations: string[] = [];

          for (const el of elements) {
            const { transitionProperty, transitionDuration } = getComputedStyle(el);

            if (transitionProperty === "none") {
              continue;
            }

            const durations = transitionDuration.split(",").map((value) => parseFloat(value));
            const name =
              el.getAttribute("aria-label") ??
              el.getAttribute("id") ??
              el.textContent?.trim().slice(0, 30) ??
              "";

            transitionProperty.split(",").forEach((raw, i) => {
              const property = raw.trim();
              // A shorter duration list repeats over the property list.
              const duration = durations[i % durations.length] ?? 0;

              if (duration > maxDuration) {
                violations.push(`<${el.localName}> "${name}" ${property} ${duration}s`);
              }

              if (duration > 0 && unanimatable.includes(property)) {
                violations.push(`<${el.localName}> "${name}" animates ${property}`);
              }
            });
          }

          return { checked: elements.size, violations };
        },
        { maxDuration: MAX_DURATION, unanimatable: UNANIMATABLE },
      );

      expect(checked, "no interactive element was found to check").toBeGreaterThan(0);
      expect(violations).toEqual([]);
    });
  }
});
