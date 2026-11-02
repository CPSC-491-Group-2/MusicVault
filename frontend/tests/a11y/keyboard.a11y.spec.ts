import { POPULARITY_ROW } from "@/data/popularity-row";

import { expect, test } from "../fixtures";
import {
  accessibleName,
  expectMinTargetSize,
  expectVisibleFocus,
  tabThrough,
  tabTo,
} from "../support/focus";
import { NAV_ROUTES, ROUTES, visit } from "../support/routes";

// Known focus ring bugs, by path. Each one runs as a test.fixme until fixed.
const FOCUS_RING_FIXMES: Record<string, string> = {
  "/ui": "SearchField has no focus ring: its input sets outline-none and the field only thickens its border on focus-within. Where the 2px ring should go (the input or the whole field) is a design call.",
};

// Toggle chips to drive with the mouse and the keyboard.
const CHIPS = [
  { path: "/", chip: "Rainy afternoon", fixme: "" },
  {
    path: "/ui",
    chip: "Not selected",
    fixme:
      'The /ui gallery chips are static examples with no onPressedChange, so they never toggle. Making them interactive needs a call on their "Selected" and "Not selected" labels.',
  },
];

test.describe("keyboard", { tag: "@a11y" }, () => {
  for (const route of ROUTES) {
    test(`${route.name} (${route.path}): every tab stop shows a focus ring`, async ({
      page,
    }) => {
      test.skip(!!route.a11y?.skip, route.a11y?.skip);
      const fixme = FOCUS_RING_FIXMES[route.path];
      test.fixme(!!fixme, fixme);

      await visit(page, route.path);
      const stops = await tabThrough(page, {
        onStop: () => expectVisibleFocus(page.locator(":focus")),
      });

      expect(stops.length, "nothing on the page takes focus").toBeGreaterThan(0);
    });

    test(`${route.name} (${route.path}): focus never lands on hidden elements or gets stuck`, async ({
      page,
    }) => {
      test.skip(!!route.a11y?.skip, route.a11y?.skip);

      await visit(page, route.path);
      const stops = await tabThrough(page);
      expect(stops.length, "nothing on the page takes focus").toBeGreaterThan(0);

      stops.forEach((stop, i) => {
        const label = `stop ${i + 1}, ${stop.role} "${stop.name}"`;

        expect.soft(stop.hidden, `${label} is hidden`).toBe(false);
        // sr-only elements measure 1x1, so anything that small counts as hidden.
        expect
          .soft(stop.width > 1 && stop.height > 1, `${label} is ${stop.width} x ${stop.height}px`)
          .toBe(true);
        expect.soft(stop.key, `focus is stuck on ${label}`).not.toBe(stops[i - 1]?.key);
      });
    });
  }

  // Keeps the other controls on /ui (Button, IconButton, Chip) covered while the
  // full /ui check above is a fixme. Delete it once SearchField has a ring.
  test("UI components (/ui): every tab stop except the search fields shows a focus ring", async ({
    page,
  }) => {
    await visit(page, "/ui");
    const stops = await tabThrough(page, {
      onStop: async (stop) => {
        if (stop.role !== "searchbox") {
          await expectVisibleFocus(page.locator(":focus"));
        }
      },
    });

    expect(stops.length).toBeGreaterThan(0);
  });

  for (const route of NAV_ROUTES) {
    test(`shell nav marks only ${route.name} as the current page on ${route.path}`, async ({
      page,
      isMobile,
    }) => {
      test.skip(!!route.a11y?.skip, route.a11y?.skip);

      await visit(page, route.path);

      // Desktop shows the sidebar (a complementary landmark), mobile shows the
      // bottom tab bar. Only one of the two is ever in the accessibility tree.
      const nav = page.getByRole("navigation", { name: "Main" });

      if (isMobile) {
        await expect(page.getByRole("complementary")).toHaveCount(0);
        await expect(page.getByRole("complementary", { includeHidden: true })).toHaveCount(1);

        // The tab bar is pinned to the bottom of the viewport.
        const box = await nav.boundingBox();
        expect(Math.round((box?.y ?? 0) + (box?.height ?? 0))).toBe(page.viewportSize()?.height);
      } else {
        await expect(
          page.getByRole("complementary").getByRole("navigation", { name: "Main" }),
        ).toBeVisible();
      }

      await expect(nav.getByRole("link", { name: route.name, exact: true })).toHaveAttribute(
        "aria-current",
        "page",
      );
      await expect(nav.locator("[aria-current]")).toHaveCount(1);
    });
  }

  test("Tab and Enter on the Swipe link open /swipe", async ({ page }) => {
    await visit(page, "/dashboard");

    const swipe = page
      .getByRole("navigation", { name: "Main" })
      .getByRole("link", { name: "Swipe", exact: true });
    await tabTo(page, swipe);
    await page.keyboard.press("Enter");

    await expect(page).toHaveURL((url) => url.pathname === "/swipe");
    await expect(page.getByRole("heading", { level: 1, name: "Swipe to tune" })).toBeVisible();
  });

  for (const { path, chip, fixme } of CHIPS) {
    test(`a chip on ${path} toggles aria-pressed with a click, Space and Enter`, async ({
      page,
    }) => {
      test.fixme(!!fixme, fixme);

      await visit(page, path);

      const toggle = page.getByRole("button", { name: chip, exact: true });
      await expect(toggle).toHaveAttribute("aria-pressed", "false");

      // The first click can land before React hydrates; retry until it takes.
      await expect(async () => {
        await toggle.click();
        await expect(toggle).toHaveAttribute("aria-pressed", "true", { timeout: 1_000 });
      }).toPass();

      await toggle.press("Space");
      await expect(toggle).toHaveAttribute("aria-pressed", "false");

      await toggle.press("Enter");
      await expect(toggle).toHaveAttribute("aria-pressed", "true");
    });
  }

  test("popularity tiles are named links that open a new tab and show their details on focus", async ({
    page,
  }) => {
    await visit(page, "/");

    const tiles = page
      .getByRole("region", { name: "What you play most, and what we find for you" })
      .getByRole("link");
    await expect(tiles).toHaveCount(POPULARITY_ROW.length);

    for (const [i, track] of POPULARITY_ROW.entries()) {
      const tile = tiles.nth(i);
      // The overlay is the element around the visible title text.
      const overlay = tile.getByText(track.title, { exact: true }).locator("..");

      await expect(overlay).toHaveCSS("opacity", "0");

      // Real Tab presses, so the tile matches :focus-visible like it would for
      // a keyboard user.
      if (i === 0) {
        await tabTo(page, tile);
      } else {
        await page.keyboard.press("Tab");
      }
      await expect(tile).toBeFocused();

      const name = await accessibleName(tile);
      expect(name).toContain(track.title);
      expect(name).toContain(track.artist);
      await expect(tile).toHaveAttribute("target", "_blank");
      await expect(tile).toHaveAttribute("rel", /\bnoopener\b/);
      await expect(overlay).toHaveCSS("opacity", "1");
    }
  });

  // The search page doesn't have its field yet, so this checks the shared
  // SearchField on /ui. Point it at /search once that page renders one.
  test("the search field is reachable by Tab and has a name", async ({ page }) => {
    await visit(page, "/ui");

    const fields = await page.getByRole("searchbox").all();
    expect(fields.length).toBeGreaterThan(0);

    for (const field of fields) {
      await tabTo(page, field);
      await expect(field).toHaveAccessibleName(/\S/);
    }
  });

  // Spec section 11: tap targets are at least 44px. Inline text links inside
  // paragraphs are exempt, so they aren't collected here.
  test.describe("tap targets", () => {
    test.skip(({ isMobile }) => !isMobile, "tap targets are checked in the mobile project");

    test("tab bar links and buttons are at least 44px", async ({ page }) => {
      await visit(page, "/dashboard");

      const tabBar = page.getByRole("navigation", { name: "Main" });
      const targets = [
        ...(await tabBar.getByRole("link").all()),
        ...(await tabBar.getByRole("button").all()),
      ];
      expect(targets.length).toBeGreaterThan(0);

      for (const target of targets) {
        await expectMinTargetSize(target, 44);
      }
    });

    test("every Button and IconButton on /ui is at least 44px", async ({ page }) => {
      await visit(page, "/ui");

      // The gallery's sections have no names, so find each one by its heading.
      const section = (title: string) =>
        page.locator("section").filter({
          has: page.getByRole("heading", { level: 2, name: title, exact: true }),
        });
      const buttons = section("Button");
      const iconButtons = section("IconButton");
      await expect(buttons.getByRole("button").first()).toBeVisible();
      await expect(iconButtons.getByRole("button").first()).toBeVisible();

      const targets = [
        page.getByRole("main").getByRole("link", { name: "Back to home" }),
        ...(await buttons.getByRole("button").all()),
        ...(await buttons.getByRole("link").all()),
        ...(await iconButtons.getByRole("button").all()),
      ];

      for (const target of targets) {
        await expectMinTargetSize(target, 44);
      }
    });
  });
});
