import type { Page } from "@playwright/test";

type MockOptions = {
  /** Response status. Defaults to 200. */
  status?: number;
  /** Only answer this method, e.g. "POST". Defaults to every method. */
  method?: string;
};

export type MockApi = {
  /**
   * Answers one API route with JSON. "health" means /api/v1/health. A path
   * that starts with "/" is used as-is, e.g. "/api/auth/spotify/login".
   */
  <T>(path: string, body: T, options?: MockOptions): Promise<void>;
  /** URLs of the /api requests nothing mocked, in the order they were made. */
  calls: string[];
};

function toPathname(path: string) {
  return path.startsWith("/") ? path : `/api/v1/${path}`;
}

export async function createMockApi(page: Page): Promise<MockApi> {
  const calls: string[] = [];

  // The backend isn't running during tests, so anything not mocked fails fast
  // instead of hanging. Registered first: Playwright tries the most recently
  // added route first, so every mockApi(...) call wins over this one.
  await page.route("**/api/**", async (route) => {
    calls.push(route.request().url());
    await route.fulfill({ status: 503, json: { error: "not mocked in tests" } });
  });

  async function mockApi<T>(
    path: string,
    body: T,
    { status = 200, method }: MockOptions = {},
  ) {
    const pathname = toPathname(path);

    await page.route(
      (url) => url.pathname === pathname,
      async (route) => {
        if (method && route.request().method() !== method.toUpperCase()) {
          await route.fallback();
          return;
        }

        await route.fulfill({ status, json: body });
      },
    );
  }

  return Object.assign(mockApi, { calls });
}
