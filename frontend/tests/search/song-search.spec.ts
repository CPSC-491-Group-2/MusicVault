import {
  expect,
  test,
} from "../fixtures";

const numbTrack = {
  spotify_id: "spotify-numb",
  title: "Numb",
  artists: [
    {
      spotify_id: "linkin-park",
      name: "Linkin Park",
    },
  ],
  album: {
    spotify_id: "meteora",
    name: "Meteora",
    image_url: null,
  },
  duration_ms: 185586,
  popularity: 90,
  explicit: false,
  spotify_url: "https://open.spotify.com/track/example",
  isrc: "USWB12345678",
};

test.describe(
  "song search",
  { tag: "@search" },
  () => {
    test(
      "searches for a song and saves it to the vault",
      async ({
        page,
        mockApi,
        a11yAllowlist,
      }) => {
        await mockApi(
          "vault",
          {
            items: [],
          },
          {
            method: "GET",
          },
        );

        await mockApi(
          "spotify/search",
          {
            items: [numbTrack],
            total: 1,
            limit: 12,
            offset: 0,
            next: null,
            previous: null,
          },
          {
            method: "GET",
          },
        );

        await mockApi(
          "vault",
          {
            spotify_id: "spotify-numb",
          },
          {
            method: "POST",
          },
        );

        await page.goto("/search");

        const searchField =
          page.getByRole("searchbox", {
            name: "Search for a song",
          });

        await searchField.fill("Numb");

        await page
          .getByRole("button", {
            name: "Search",
          })
          .click();

        await expect(
          page.getByRole("heading", {
            name: "Numb",
          }),
        ).toBeVisible();

        await expect(
          page.getByText("Linkin Park"),
        ).toBeVisible();

        const result =
          page
            .locator("article")
            .filter({
              hasText: "Numb",
            });

        await result
          .getByRole("button", {
            name: "Add to vault",
          })
          .click();

        await expect(
          result.getByRole("button", {
            name: "Saved",
          }),
        ).toBeVisible();

        await expect(page).toPassAxe({
          include: "#song-search",
          allowlist: a11yAllowlist,
        });
      },
    );
  },
);