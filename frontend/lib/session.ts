import "server-only";

import { cache } from "react";
import { cookies } from "next/headers";

import type { CurrentUser } from "@/types/api";

// Absolute backend URL for server-side requests.
// The fallback supports local development.
const BACKEND_URL =
  process.env.BACKEND_URL ?? "http://127.0.0.1:5000";

export const getCurrentUser = cache(
  async (): Promise<CurrentUser | null> => {
    // Provide a deterministic authenticated user for Playwright tests.
    // This is only active when explicitly enabled by the test environment.
    if (process.env.PLAYWRIGHT_TEST === "1") {
      return {
        id: "00000000-0000-0000-0000-000000000001",
        email: "playwright@example.com",
        display_name: "Playwright Test User",
        created_at: "2026-01-01T00:00:00.000Z",
        updated_at: "2026-01-01T00:00:00.000Z",
        has_password: false,
        spotify: {
          connected: false,
          display_name: null,
        },
      };
    }

    const cookieStore = await cookies();

    const cookieHeader = cookieStore
      .getAll()
      .map(({ name, value }) => `${name}=${value}`)
      .join("; ");

    // No browser cookies means no Flask session to validate.
    if (!cookieHeader) {
      return null;
    }

    const response = await fetch(
      `${BACKEND_URL.replace(/\/$/, "")}/api/v1/me`,
      {
        headers: {
          Cookie: cookieHeader,
        },
        cache: "no-store",
      }
    );

    if (response.status === 401) {
      return null;
    }

    if (!response.ok) {
      throw new Error("Failed to retrieve MusicVault session");
    }

    return (await response.json()) as CurrentUser;
  }
);
