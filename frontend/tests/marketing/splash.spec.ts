import { POPULARITY_ROW } from "@/data/popularity-row";
import { SPOTIFY_LOGIN_URL } from "@/lib/auth";

import { expect, test } from "../fixtures";
import { visit } from "../support/routes";

test.describe("splash", { tag: "@smoke" }, () => {
  test.beforeEach(async ({ page }) => {
    await visit(page, "/");
  });

  test("shows the headline", async ({ page }) => {
    const headline = page.getByRole("heading", { level: 1 });

    await expect(headline).toBeVisible();
    await expect(headline).toHaveText("Music you'd love, from artists you haven't heard yet.");
  });

  test("both login links go to Spotify login", async ({ page }) => {
    const links = page.getByRole("link", { name: "Log in with Spotify" });
    await expect(links).toHaveCount(2);

    for (const link of await links.all()) {
      await expect(link).toHaveAttribute("href", SPOTIFY_LOGIN_URL);
    }
  });

  test("the popularity row shows nine album covers", async ({ page }) => {
    const tiles = page
      .getByRole("region", { name: "What you play most, and what we find for you" })
      .getByRole("link");
    await expect(tiles).toHaveCount(9);

    for (const [i, track] of POPULARITY_ROW.entries()) {
      const cover = tiles
        .nth(i)
        .getByRole("img", { name: `${track.title} by ${track.artist}, album cover` });
      await expect(cover).toBeVisible();

      // A visible box isn't enough, the image itself has to load. Covers load
      // lazily, so scroll each one into view first.
      await cover.scrollIntoViewIfNeeded();
      await expect
        .poll(() => cover.evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 0), {
          message: `the ${track.title} cover didn't load`,
          timeout: 10_000,
        })
        .toBe(true);
    }
  });

  test("the How it works link scrolls to that section", async ({ page, isMobile }) => {
    test.skip(isMobile, "the How it works link is hidden below 768px");

    await page.getByRole("link", { name: "How it works" }).click();

    await expect(page).toHaveURL(/#how-it-works$/);
    await expect(page.getByRole("heading", { level: 2, name: "How it works" })).toBeInViewport();
  });
});
