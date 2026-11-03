import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { cache } from "react";
import type { User } from "@/types/api";

const TEST_USER: User = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "playwright@example.com",
  display_name: "Playwright Test User",
  has_password: false,
  spotify: { connected: false, display_name: null },
  created_at: "2026-01-01T00:00:00.000Z",
  updated_at: "2026-01-01T00:00:00.000Z",
};

export const getCurrentUser = cache(async (): Promise<User | null> => {
  const cookie = (await cookies()).toString();
  if (!cookie) return null;
  const base = process.env.BACKEND_URL ?? "http://127.0.0.1:5000";
  try {
    const response = await fetch(`${base}/api/v1/me`, {
      headers: { Cookie: cookie },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as User;
  } catch {
    return null;
  }
});

export async function requireUser(): Promise<User> {
  if (process.env.PLAYWRIGHT_TEST === "1" && !process.env.BACKEND_URL) {
    return TEST_USER;
  }
  const user = await getCurrentUser();
  if (!user) redirect("/login");
  return user;
}
