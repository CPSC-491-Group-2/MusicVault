import type { AuthErrorCode } from "@/types/api";

const AUTH_ERROR_MESSAGES: Record<AuthErrorCode, string> = {
  invalid_state: "That sign-in link expired. Try again.",
  access_denied:
    "Spotify sign-in was canceled. Try again, or log in with your email.",
  spotify_error:
    "Spotify didn't respond. Try again in a minute, or log in with your email.",
  spotify_not_allowed:
    "Spotify sign-in is limited to a small test group right now. Log in with your email instead.",
  spotify_in_use:
    "That Spotify account is already linked to a different MusicVault account.",
  already_connected:
    "You already have a Spotify account connected. Disconnect it first to switch.",
  invalid_credentials:
    "That email and password don't match. Check them and try again.",
  email_taken: "An account with that email already exists. Log in instead.",
};

function isAuthErrorCode(code: string): code is AuthErrorCode {
  return Object.hasOwn(AUTH_ERROR_MESSAGES, code);
}

export function authErrorMessage(code: string): string {
  return isAuthErrorCode(code)
    ? AUTH_ERROR_MESSAGES[code]
    : AUTH_ERROR_MESSAGES.spotify_error;
}
