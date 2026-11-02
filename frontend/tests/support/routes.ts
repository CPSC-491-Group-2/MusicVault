import { expect, type Page } from "../fixtures";

export type RouteEntry = {
  name: string; // "Swipe". For inNav routes, the nav link's label
  path: string; // "/swipe"
  heading: string | RegExp; // the page's h1
  area: "marketing" | "app" | "dev";
  inNav?: boolean; // shows in the shell nav
  a11y?: { skip?: string }; // reason, only if the page truly can't be scanned
};

// Every page in the app, listed once. The a11y specs and the smoke tests loop
// over this list, so adding a page here is all it takes to get it checked.
export const ROUTES: RouteEntry[] = [
  { name: "Splash", path: "/", heading: "Music you'd love, from artists you haven't heard yet.", area: "marketing" },
  { name: "Home", path: "/dashboard", heading: "Welcome back", area: "app", inNav: true },
  { name: "Swipe", path: "/swipe", heading: "Swipe to tune", area: "app", inNav: true },
  { name: "Vault", path: "/library", heading: "Your vault", area: "app", inNav: true },
  { name: "Search", path: "/search", heading: "Find a song you love", area: "app", inNav: true },
  { name: "Taste", path: "/taste", heading: "Your taste", area: "app", inNav: true },
  { name: "Profile", path: "/profile", heading: "Profile", area: "app", inNav: true },
  { name: "UI components", path: "/ui", heading: "UI components", area: "dev" },
];

export const NAV_ROUTES = ROUTES.filter((route) => route.inNav);

// Opens a page and waits until it has rendered: the h1 is on screen and the
// web font has loaded, so text sizes and layout are final.
export async function visit(page: Page, path: string) {
  await page.goto(path);
  // .first(): landmarks.a11y.spec.ts is where "exactly one h1" is checked.
  await expect(page.getByRole("heading", { level: 1 }).first()).toBeVisible();
  await page.evaluate(async () => {
    await document.fonts.ready;
  });
}
