from __future__ import annotations

from urllib.parse import urlencode

import requests

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PROFILE_URL = "https://api.spotify.com/v1/me"

REQUEST_TIMEOUT = 10


class SpotifyAuthError(Exception):
    """Spotify rejected a request or couldn't be reached."""


class SpotifyRefreshTokenError(SpotifyAuthError):
    """Spotify explicitly rejected the refresh token."""


def build_authorize_url(
    *, client_id: str, redirect_uri: str, scope: str, state: str
) -> str:
    """Build the Spotify OAuth authorization URL."""

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    }

    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(
    *, code: str, client_id: str, client_secret: str, redirect_uri: str
) -> dict:
    """Exchange a Spotify authorization code for tokens."""

    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
            auth=(client_id, client_secret),
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise SpotifyAuthError("Could not reach Spotify token endpoint") from exc

    if response.status_code != 200:
        raise SpotifyAuthError(f"Token exchange failed ({response.status_code})")

    return response.json()


def refresh_access_token(
    *,
    refresh_token: str,
    client_id: str,
    client_secret: str,
) -> dict:
    """Refresh an expired or rejected Spotify access token."""

    if not refresh_token:
        raise SpotifyAuthError("Spotify refresh token is missing")

    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            auth=(client_id, client_secret),
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise SpotifyAuthError("Could not reach Spotify token endpoint") from exc

    # An invalid_grant response indicates that Spotify rejected
    # the refresh token itself.
    if response.status_code == 400:
        try:
            error_data = response.json()
        except ValueError:
            error_data = {}

        if isinstance(error_data, dict) and error_data.get("error") == "invalid_grant":
            raise SpotifyRefreshTokenError("Spotify refresh token is invalid")

    if response.status_code != 200:
        raise SpotifyAuthError("Spotify token refresh request failed")

    try:
        token_data = response.json()
    except ValueError as exc:
        raise SpotifyAuthError("Invalid Spotify token response") from exc

    if not isinstance(token_data, dict):
        raise SpotifyAuthError("Invalid Spotify token response")

    if not token_data.get("access_token"):
        raise SpotifyAuthError("Spotify did not return an access token")

    return token_data


def get_current_user_profile(access_token: str) -> dict:
    """Retrieve the authenticated Spotify user's profile."""

    try:
        response = requests.get(
            PROFILE_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise SpotifyAuthError("Could not reach Spotify profile endpoint") from exc

    if response.status_code != 200:
        raise SpotifyAuthError(f"Profile request failed ({response.status_code})")

    return response.json()
