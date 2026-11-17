import { isAuthErrorCode } from "@/components/auth/authErrors";
import type {
  AuthErrorCode,
  ChangePasswordRequest,
  LoginRequest,
  RegisterRequest,
  User,
} from "@/types/api";

export const SPOTIFY_LOGIN_URL = "/api/auth/spotify/login";
export const SPOTIFY_CONNECT_URL = "/api/auth/spotify/connect";

const LOGIN_URL = "/api/v1/auth/login";
const REGISTER_URL = "/api/v1/auth/register";
const LOGOUT_URL = "/api/v1/auth/logout";
const PASSWORD_URL = "/api/v1/me/password";
const SPOTIFY_URL = "/api/v1/me/spotify";

export type AuthResult =
  | { ok: true; user?: User }
  | { ok: false; error?: AuthErrorCode; fieldErrors?: Record<string, string> };

function errorForStatus(status: number): AuthErrorCode {
  if (status === 401) return "invalid_credentials";
  if (status === 409) return "email_taken";
  return "service_unavailable";
}

function fieldErrorsFrom(data: unknown): Record<string, string> {
  const json = (data as { errors?: { json?: unknown } } | null)?.errors?.json;
  if (typeof json !== "object" || json === null) return {};
  const fieldErrors: Record<string, string> = {};
  for (const [field, messages] of Object.entries(
    json as Record<string, unknown>,
  )) {
    const first = Array.isArray(messages) ? messages[0] : undefined;
    if (typeof first === "string") {
      fieldErrors[field] = first;
    }
  }
  return fieldErrors;
}

async function request(
  method: "POST" | "PUT" | "DELETE",
  path: string,
  body?: unknown,
): Promise<AuthResult> {
  const init: RequestInit = { method, credentials: "same-origin" };
  if (body !== undefined) {
    init.headers = { "Content-Type": "application/json" };
    init.body = JSON.stringify(body);
  }

  let response: Response;
  try {
    response = await fetch(path, init);
  } catch {
    return { ok: false, error: "service_unavailable" };
  }

  const data: unknown = await response.json().catch(() => null);

  if (response.ok) {
    return typeof data === "object" && data !== null
      ? { ok: true, user: data as User }
      : { ok: true };
  }

  if (response.status === 422) {
    const fieldErrors = fieldErrorsFrom(data);
    return Object.keys(fieldErrors).length > 0
      ? { ok: false, fieldErrors }
      : { ok: false, error: "service_unavailable" };
  }

  if (response.status >= 400 && response.status < 500) {
    const code = (data as { code?: unknown } | null)?.code;
    if (typeof code === "string" && isAuthErrorCode(code)) {
      return { ok: false, error: code };
    }
  }

  return { ok: false, error: errorForStatus(response.status) };
}

export function loginWithEmail(values: LoginRequest): Promise<AuthResult> {
  return request("POST", LOGIN_URL, values);
}

export function registerWithEmail(values: RegisterRequest): Promise<AuthResult> {
  return request("POST", REGISTER_URL, values);
}

export function changePassword(
  values: ChangePasswordRequest,
): Promise<AuthResult> {
  return request("PUT", PASSWORD_URL, values);
}

export function disconnectSpotify(): Promise<AuthResult> {
  return request("DELETE", SPOTIFY_URL);
}

export async function logout(): Promise<void> {
  try {
    await fetch(LOGOUT_URL, { method: "POST", credentials: "same-origin" });
  } catch {
    return;
  }
}
