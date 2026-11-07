import type { AuthErrorCode, LoginRequest, RegisterRequest } from "@/types/api";

export const SPOTIFY_LOGIN_URL = "/api/auth/spotify/login";
export const SPOTIFY_CONNECT_URL = "/api/auth/spotify/connect";

const LOGIN_URL = "/api/v1/auth/login";
const REGISTER_URL = "/api/v1/auth/register";
const LOGOUT_URL = "/api/v1/auth/logout";

export type AuthResult = { ok: true } | { ok: false; error: AuthErrorCode };

function errorForStatus(status: number): AuthErrorCode {
  if (status === 401) return "invalid_credentials";
  if (status === 409) return "email_taken";
  return "service_unavailable";
}

async function post(path: string, body: unknown): Promise<AuthResult> {
  try {
    const response = await fetch(path, {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    return response.ok
      ? { ok: true }
      : { ok: false, error: errorForStatus(response.status) };
  } catch {
    return { ok: false, error: "service_unavailable" };
  }
}

export function loginWithEmail(values: LoginRequest): Promise<AuthResult> {
  return post(LOGIN_URL, values);
}

export function registerWithEmail(values: RegisterRequest): Promise<AuthResult> {
  return post(REGISTER_URL, values);
}

export async function logout(): Promise<void> {
  try {
    await fetch(LOGOUT_URL, { method: "POST", credentials: "same-origin" });
  } catch {
    return;
  }
}
