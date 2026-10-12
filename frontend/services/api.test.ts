import { describe, expect, it } from "vitest";

import { API_URL } from "./api";

describe("API configuration", () => {
  it("loads an API base URL", () => {
    expect(API_URL).toBeTruthy();
  });

  it("uses the expected default API URL when no override is provided", () => {
    expect(API_URL).toContain("http");
  });
});