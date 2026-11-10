import { expect, test } from "../fixtures";

test.describe("song search", { tag: "@search" }, () => {
  test("shows the song search field", async ({
    page,
    a11yAllowlist,
  }) => {
    await page.goto("/search");

    await expect(
      page.getByRole("heading", {
        level: 1,
        name: "Find a song you love",
      }),
    ).toBeVisible();

    await expect(
      page.getByRole("searchbox", {
        name: "Search for a song",
      }),
    ).toBeVisible();

    await expect(page).toPassAxe({
      include: "#song-search",
      allowlist: a11yAllowlist,
    });
  });
});