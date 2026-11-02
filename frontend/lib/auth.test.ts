
import { afterEach, describe, expect, it, vi } from "vitest";

import {
  loginAccount,
  logoutAccount,
  registerAccount,
  SPOTIFY_LOGIN_URL,
} from "./auth";

describe("MusicVault authentication helpers", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("preserves the existing Spotify login URL", () => {
    expect(SPOTIFY_LOGIN_URL).toBe("/api/auth/spotify/login");
  });

  it("sends registration data to the Flask API", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 201,
    });

    vi.stubGlobal("fetch", mockFetch);

    const data = {
      email: "test@example.com",
      password: "ExamplePassword123",
      display_name: "Test User",
    };

    await registerAccount(data);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/auth/register",
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }
    );
  });

  it("sends login credentials to the Flask API", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
    });

    vi.stubGlobal("fetch", mockFetch);

    const data = {
      email: "test@example.com",
      password: "ExamplePassword123",
    };

    await loginAccount(data);

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/auth/login",
      {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      }
    );
  });

  it("sends logout without credentials in the body", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 204,
    });

    vi.stubGlobal("fetch", mockFetch);

    await logoutAccount();

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/auth/logout",
      {
        method: "POST",
        credentials: "same-origin",
        headers: undefined,
        body: undefined,
      }
    );
  });

  it("reports when local login is unavailable", async () => {
    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({
        error: "Service Unavailable",
        message: "Local login is not enabled yet.",
      }),
    });

    vi.stubGlobal("fetch", mockFetch);

    await expect(
      loginAccount({
        email: "test@example.com",
        password: "ExamplePassword123",
      })
    ).rejects.toMatchObject({
      name: "AuthApiError",
      status: 503,
      message: "Local login is not enabled yet.",
    });
  });
});
