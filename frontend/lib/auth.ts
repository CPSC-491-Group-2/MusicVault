
import type { LoginRequest, RegisterRequest } from "../types/api";
import { API_URL } from "../services/api";

// Preserve the existing Spotify OAuth entry point.
export const SPOTIFY_LOGIN_URL = "/api/auth/spotify/login";

// Authentication endpoint errors.
export class AuthApiError extends Error {
  constructor(
    public readonly status: number,
    message: string
  ) {
    super(message);
    this.name = "AuthApiError";
  }
}

// Shared helper for local authentication requests.
async function postAuthRequest(
  endpoint: string,
  data?: LoginRequest | RegisterRequest
): Promise<void> {
  const response = await fetch(`${API_URL}/v1/auth/${endpoint}`, {
    method: "POST",
    credentials: "same-origin",
    headers: data
      ? { "Content-Type": "application/json" }
      : undefined,
    body: data ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    const result: unknown = await response.json().catch(() => null);

    const message =
      typeof result === "object" &&
      result !== null &&
      "message" in result &&
      typeof result.message === "string"
        ? result.message
        : `Authentication request failed (${response.status}).`;

    throw new AuthApiError(response.status, message);
  }
}

// Create a MusicVault account.
// Backend remains disabled until password security is integrated.
export async function registerAccount(
  data: RegisterRequest
): Promise<void> {
  await postAuthRequest("register", data);
}

// Authenticate an existing MusicVault account.
// Backend remains disabled until password security is integrated.
export async function loginAccount(
  data: LoginRequest
): Promise<void> {
  await postAuthRequest("login", data);
}

// End the current MusicVault session.
export async function logoutAccount(): Promise<void> {
  await postAuthRequest("logout");
}
