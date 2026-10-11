from __future__ import annotations

from urllib.parse import urlencode

import requests

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PROFILE_URL = "https://api.spotify.com/v1/me"

REQUEST_TIMEOUT = 10


class SpotifyAuthError(Exception):
    """Spotify rejected a request or couldn't be reached."""


def build_authorize_url(
    *, client_id: str, redirect_uri: str, scope: str, state: str
) -> str:
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
    # The client secret only ever travels server-to-server, as HTTP Basic auth
    # on this request. It is never sent to the browser.
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


def get_current_user_profile(access_token: str) -> dict:
    try:
        response = requests.get(
            PROFILE_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise SpotifyAuthError("Could not reach Spotify profile endpoint") from exc

    if response.status_code != 200:
        raise SpotifyAuthError(f"Profile request failed ({response.status_code})")
    return response.json()
