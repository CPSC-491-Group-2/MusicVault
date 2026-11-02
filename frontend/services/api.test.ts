import { describe, expect, it, vi, afterEach } from "vitest";

import { API_URL, getHealth } from "./api";

describe("API configuration", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("uses the Next.js API proxy", () => {
    expect(API_URL).toBe("/api");
  });

  it("requests backend health through the proxy", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        service: "musicvault",
        status: "ok",
      }),
    });

    vi.stubGlobal("fetch", mockFetch);

    await getHealth();

    expect(mockFetch).toHaveBeenCalledWith("/api/v1/health");
  });
});