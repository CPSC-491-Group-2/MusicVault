from __future__ import annotations

import uuid
from urllib.parse import parse_qs, urlparse

import pytest
import requests
from sqlalchemy import select

from app import create_app
from app.services import spotify_auth
from db.session import SessionLocal
from models.spotify_account import SpotifyAccount
from models.user import User

FRONTEND_URL = "http://127.0.0.1:3000"
REDIRECT_URI = "http://127.0.0.1:3000/api/auth/spotify/callback"
CLIENT_SECRET = "test-client-secret"

LOGIN = "/api/auth/spotify/login"
CALLBACK = "/api/auth/spotify/callback"


class FakeResponse:
    def __init__(self, status_code, body=None):
        self.status_code = status_code
        self._body = body or {}

    def json(self):
        return self._body


class FakeSpotify:
    """Stands in for Spotify's token and profile endpoints.

    Patches requests inside the service module, so the real route, service,
    query, and database code all run; only the network is faked.
    """

    def __init__(self, monkeypatch):
        self.token_response = FakeResponse(
            200,
            {
                "access_token": "access-1",
                "refresh_token": "refresh-1",
                "expires_in": 3600,
                "scope": "user-read-email",
            },
        )
        self.profile_response = FakeResponse(
            200,
            {
                "id": f"spotify-{uuid.uuid4()}",
                "display_name": "OAuth Tester",
                "email": f"{uuid.uuid4()}@example.com",
            },
        )
        self.token_requests = []
        self.profile_requests = []
        monkeypatch.setattr(spotify_auth.requests, "post", self._post)
        monkeypatch.setattr(spotify_auth.requests, "get", self._get)

    def _post(self, url, **kwargs):
        self.token_requests.append((url, kwargs))
        if isinstance(self.token_response, Exception):
            raise self.token_response
        return self.token_response

    def _get(self, url, **kwargs):
        self.profile_requests.append((url, kwargs))
        return self.profile_response

    @property
    def spotify_id(self):
        return self.profile_response.json()["id"]


@pytest.fixture
def app():
    app = create_app()
    app.testing = True
    app.config.update(
        SECRET_KEY="test-secret-key",
        FRONTEND_URL=FRONTEND_URL,
        SPOTIFY_CLIENT_ID="test-client-id",
        SPOTIFY_CLIENT_SECRET=CLIENT_SECRET,
        SPOTIFY_REDIRECT_URI=REDIRECT_URI,
    )
    return app


@pytest.fixture
def oauth_client(app):
    return app.test_client()


@pytest.fixture
def spotify(monkeypatch):
    return FakeSpotify(monkeypatch)


def start_login(client):
    """Hit /login and return the state it stored in the session."""
    client.get(LOGIN)
    with client.session_transaction() as sess:
        return sess["spotify_oauth_state"]


def auth_error(response):
    query = parse_qs(urlparse(response.location).query)
    return query.get("auth_error", [None])[0]


def session_user_id(client):
    with client.session_transaction() as sess:
        return sess.get("user_id")


# --- /login ---------------------------------------------------------------


def test_login_redirects_to_spotify_with_state(oauth_client):
    response = oauth_client.get(LOGIN)

    assert response.status_code == 302
    url = urlparse(response.location)
    query = parse_qs(url.query)
    assert f"{url.scheme}://{url.netloc}{url.path}" == spotify_auth.AUTHORIZE_URL
    assert query["client_id"] == ["test-client-id"]
    assert query["response_type"] == ["code"]
    assert query["redirect_uri"] == [REDIRECT_URI]
    with oauth_client.session_transaction() as sess:
        assert query["state"] == [sess["spotify_oauth_state"]]
    assert CLIENT_SECRET not in response.location


def test_login_generates_a_new_state_each_time(oauth_client):
    assert start_login(oauth_client) != start_login(oauth_client)


def test_login_ignores_redirect_uri_from_request(oauth_client):
    response = oauth_client.get(f"{LOGIN}?redirect_uri=https://evil.example.com")

    query = parse_qs(urlparse(response.location).query)
    assert query["redirect_uri"] == [REDIRECT_URI]


# --- /callback: happy path (needs the test database) ----------------------


def test_callback_logs_in_new_user(oauth_client, spotify, clean_database):
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state={state}")

    assert response.status_code == 302
    assert response.location == FRONTEND_URL

    token_url, token_kwargs = spotify.token_requests[0]
    assert token_url == spotify_auth.TOKEN_URL
    assert token_kwargs["data"]["code"] == "auth-code"
    assert token_kwargs["data"]["redirect_uri"] == REDIRECT_URI
    assert token_kwargs["auth"] == ("test-client-id", CLIENT_SECRET)

    with SessionLocal() as db:
        account = db.scalar(
            select(SpotifyAccount).where(
                SpotifyAccount.spotify_account_id == spotify.spotify_id
            )
        )
        assert account is not None
        assert account.access_token == "access-1"
        assert account.refresh_token == "refresh-1"
        assert account.token_expires_at is not None
        assert account.user.display_name == "OAuth Tester"
        assert session_user_id(oauth_client) == str(account.user_id)


def test_login_grants_access_to_protected_routes(oauth_client, spotify, clean_database):
    assert oauth_client.get("/api/v1/me").status_code == 401

    oauth_client.get(f"{CALLBACK}?code=auth-code&state={start_login(oauth_client)}")
    response = oauth_client.get("/api/v1/me")

    assert response.status_code == 200
    assert response.get_json()["display_name"] == "OAuth Tester"


def test_failed_login_does_not_grant_access(oauth_client, spotify):
    oauth_client.get(f"{CALLBACK}?code=auth-code&state=forged")

    assert oauth_client.get("/api/v1/me").status_code == 401


def test_callback_state_cannot_be_replayed(oauth_client, spotify, clean_database):
    state = start_login(oauth_client)
    oauth_client.get(f"{CALLBACK}?code=auth-code&state={state}")

    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state={state}")

    assert auth_error(response) == "invalid_state"
    assert len(spotify.token_requests) == 1


def test_callback_returning_user_reuses_account(oauth_client, spotify, clean_database):
    oauth_client.get(f"{CALLBACK}?code=c1&state={start_login(oauth_client)}")
    first_user_id = session_user_id(oauth_client)

    # Spotify often leaves out refresh_token on later logins.
    spotify.token_response = FakeResponse(
        200, {"access_token": "access-2", "expires_in": 3600}
    )
    oauth_client.get(f"{CALLBACK}?code=c2&state={start_login(oauth_client)}")

    assert session_user_id(oauth_client) == first_user_id
    with SessionLocal() as db:
        accounts = db.scalars(
            select(SpotifyAccount).where(
                SpotifyAccount.spotify_account_id == spotify.spotify_id
            )
        ).all()
        assert len(accounts) == 1
        assert accounts[0].access_token == "access-2"
        assert accounts[0].refresh_token == "refresh-1"


def test_callback_does_not_link_existing_user_by_email(
    oauth_client, spotify, clean_database
):
    # Spotify emails aren't guaranteed verified, so a matching email must not
    # log someone into an account that already exists.
    taken_email = spotify.profile_response.json()["email"]
    with SessionLocal() as db:
        existing = User(email=taken_email, display_name="Already Here")
        db.add(existing)
        db.commit()
        existing_id = str(existing.id)

    oauth_client.get(f"{CALLBACK}?code=auth-code&state={start_login(oauth_client)}")

    new_user_id = session_user_id(oauth_client)
    assert new_user_id is not None
    assert new_user_id != existing_id
    with SessionLocal() as db:
        assert db.get(User, uuid.UUID(new_user_id)).email is None


# --- /callback: state / CSRF failures --------------------------------------


def test_callback_without_login_is_rejected(oauth_client, spotify):
    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state=anything")

    assert response.status_code == 302
    assert auth_error(response) == "invalid_state"
    assert spotify.token_requests == []
    assert session_user_id(oauth_client) is None


def test_callback_without_state_param_is_rejected(oauth_client, spotify):
    start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?code=auth-code")

    assert auth_error(response) == "invalid_state"
    assert spotify.token_requests == []


def test_callback_with_wrong_state_is_rejected(oauth_client, spotify):
    start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state=forged")

    assert auth_error(response) == "invalid_state"
    assert spotify.token_requests == []
    assert session_user_id(oauth_client) is None


def test_failed_attempt_uses_up_the_state(oauth_client, spotify):
    state = start_login(oauth_client)
    oauth_client.get(f"{CALLBACK}?code=auth-code&state=forged")

    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state={state}")

    assert auth_error(response) == "invalid_state"
    assert spotify.token_requests == []


# --- /callback: Spotify-side failures --------------------------------------


def test_callback_user_denied_access(oauth_client, spotify):
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?error=access_denied&state={state}")

    assert auth_error(response) == "access_denied"
    assert spotify.token_requests == []


def test_callback_other_spotify_error_is_not_echoed(oauth_client, spotify):
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?error=<script>&state={state}")

    assert auth_error(response) == "spotify_error"
    assert "script" not in response.location


def test_callback_missing_code(oauth_client, spotify):
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?state={state}")

    assert auth_error(response) == "spotify_error"
    assert spotify.token_requests == []


def test_callback_token_exchange_rejected(oauth_client, spotify):
    spotify.token_response = FakeResponse(400, {"error": "invalid_grant"})
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?code=expired&state={state}")

    assert auth_error(response) == "spotify_error"
    assert spotify.profile_requests == []
    assert session_user_id(oauth_client) is None


def test_callback_spotify_unreachable(oauth_client, spotify):
    spotify.token_response = requests.ConnectionError("network down")
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state={state}")

    assert auth_error(response) == "spotify_error"
    assert session_user_id(oauth_client) is None


def test_callback_profile_request_rejected(oauth_client, spotify):
    spotify.profile_response = FakeResponse(401)
    state = start_login(oauth_client)

    response = oauth_client.get(f"{CALLBACK}?code=auth-code&state={state}")

    assert auth_error(response) == "spotify_error"
    assert session_user_id(oauth_client) is None


# --- configuration ---------------------------------------------------------


@pytest.mark.parametrize("missing", ["SECRET_KEY", "SPOTIFY_CLIENT_SECRET"])
@pytest.mark.parametrize("path", [LOGIN, CALLBACK])
def test_routes_refuse_to_run_without_config(app, missing, path):
    app.config[missing] = None

    response = app.test_client().get(path)

    assert response.status_code == 503
    assert response.get_json()["message"] == "Spotify login is not configured."
# --- refresh token ---------------------------------------------------------


def test_refresh_access_token_success(monkeypatch):
    requests_made = []

    def fake_post(url, **kwargs):
        requests_made.append((url, kwargs))
        return FakeResponse(
            200,
            {
                "access_token": "new-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": "user-read-email",
            },
        )

    monkeypatch.setattr(spotify_auth.requests, "post", fake_post)

    token = spotify_auth.refresh_access_token(
        refresh_token="refresh-123",
        client_id="test-client-id",
        client_secret=CLIENT_SECRET,
    )

    assert token["access_token"] == "new-access-token"

    url, kwargs = requests_made[0]
    assert url == spotify_auth.TOKEN_URL
    assert kwargs["data"] == {
        "grant_type": "refresh_token",
        "refresh_token": "refresh-123",
    }
    assert kwargs["auth"] == ("test-client-id", CLIENT_SECRET)
    assert kwargs["timeout"] == spotify_auth.REQUEST_TIMEOUT


def test_refresh_access_token_rejected(monkeypatch):
    def fake_post(url, **kwargs):
        return FakeResponse(400, {"error": "invalid_grant"})

    monkeypatch.setattr(spotify_auth.requests, "post", fake_post)

    with pytest.raises(
    spotify_auth.SpotifyRefreshTokenError,
    match="Spotify refresh token is invalid",
    ):
        spotify_auth.refresh_access_token(
            refresh_token="bad-refresh-token",
            client_id="test-client-id",
            client_secret=CLIENT_SECRET,
        )


def test_refresh_access_token_spotify_unreachable(monkeypatch):
    def fake_post(url, **kwargs):
        raise requests.ConnectionError("network down")

    monkeypatch.setattr(spotify_auth.requests, "post", fake_post)

    with pytest.raises(
        spotify_auth.SpotifyAuthError,
        match="Could not reach Spotify token endpoint",
    ):
        spotify_auth.refresh_access_token(
            refresh_token="refresh-123",
            client_id="test-client-id",
            client_secret=CLIENT_SECRET,
        )