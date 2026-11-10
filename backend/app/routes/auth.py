import secrets
from urllib.parse import urlencode

from flask import Blueprint, current_app, jsonify, redirect, request, session

from app.auth import get_session_user, login_user, logout_user
from app.services.spotify_auth import (
    SpotifyAuthError,
    SpotifyNotAllowedError,
    build_authorize_url,
    exchange_code_for_token,
    get_current_user_profile,
)
from db.queries.spotify_account import link_spotify_account, link_spotify_to_user
from db.session import SessionLocal

# Plain Flask blueprint (not flask-smorest): these endpoints are browser
# redirects, not JSON API resources. The path matches frontend/lib/auth.ts.
auth_bp = Blueprint("auth", __name__)

STATE_SESSION_KEY = "spotify_oauth_state"
CONNECT_SESSION_KEY = "spotify_connect_user_id"
REQUIRED_SETTINGS = (
    "SECRET_KEY",
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "SPOTIFY_REDIRECT_URI",
)


def _not_configured_response():
    missing = [key for key in REQUIRED_SETTINGS if not current_app.config.get(key)]
    if not missing:
        return None
    current_app.logger.error("Spotify login is missing config: %s", ", ".join(missing))
    return (
        jsonify(
            {
                "error": "Service Unavailable",
                "message": "Spotify login is not configured.",
            }
        ),
        503,
    )


def _redirect_to_frontend(error=None):
    url = current_app.config["FRONTEND_URL"].rstrip("/")
    if error:
        # Only fixed error codes are passed along, never text from the request.
        url = f"{url}/?{urlencode({'auth_error': error})}"
    return redirect(url)


def _redirect_to_profile(**params):
    url = current_app.config["FRONTEND_URL"].rstrip("/")
    return redirect(f"{url}/profile?{urlencode(params)}")


def _callback_error(code, connect):
    if connect:
        return _redirect_to_profile(error=code)
    return _redirect_to_frontend(code)


def _start_authorization():
    # Random, unguessable value tied to this browser's signed session cookie.
    # The callback only proceeds if Spotify hands the same value back, which
    # stops another site from completing a login on this user's behalf.
    state = secrets.token_urlsafe(32)
    session[STATE_SESSION_KEY] = state

    config = current_app.config
    return redirect(
        build_authorize_url(
            client_id=config["SPOTIFY_CLIENT_ID"],
            # Always the configured URI, never one taken from the request.
            redirect_uri=config["SPOTIFY_REDIRECT_URI"],
            scope=config["SPOTIFY_SCOPES"],
            state=state,
        )
    )


@auth_bp.get("/login")
def spotify_login():
    not_configured = _not_configured_response()
    if not_configured:
        return not_configured

    # A stale connect flag must not turn a login into a connect.
    session.pop(CONNECT_SESSION_KEY, None)

    return _start_authorization()


@auth_bp.get("/connect")
def spotify_connect():
    not_configured = _not_configured_response()
    if not_configured:
        return not_configured

    user, _ = get_session_user()
    if user is None:
        return redirect(current_app.config["FRONTEND_URL"].rstrip("/") + "/login")

    session[CONNECT_SESSION_KEY] = str(user.id)

    return _start_authorization()


@auth_bp.get("/callback")
def spotify_callback():
    not_configured = _not_configured_response()
    if not_configured:
        return not_configured

    # pop() makes each state single-use, even if this attempt fails.
    expected_state = session.pop(STATE_SESSION_KEY, None)
    connect_user_id = session.pop(CONNECT_SESSION_KEY, None)
    connect = connect_user_id is not None
    received_state = request.args.get("state")
    if (
        not expected_state
        or not received_state
        or not secrets.compare_digest(expected_state, received_state)
    ):
        current_app.logger.warning("Spotify callback rejected: invalid state")
        return _callback_error("invalid_state", connect)

    user = None
    if connect:
        # A revoked or replaced session must not finish linking.
        user, _ = get_session_user()
        if user is None or str(user.id) != connect_user_id:
            return _callback_error("invalid_state", True)

    if request.args.get("error"):
        if request.args["error"] == "access_denied":
            return _callback_error("access_denied", connect)
        return _callback_error("spotify_error", connect)

    code = request.args.get("code")
    if not code:
        return _callback_error("spotify_error", connect)

    config = current_app.config
    try:
        token = exchange_code_for_token(
            code=code,
            client_id=config["SPOTIFY_CLIENT_ID"],
            client_secret=config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=config["SPOTIFY_REDIRECT_URI"],
        )
        profile = get_current_user_profile(token["access_token"])
    except SpotifyNotAllowedError as exc:
        current_app.logger.warning("Spotify callback not allowed: %s", exc)
        return _callback_error("spotify_not_allowed", connect)
    except SpotifyAuthError as exc:
        current_app.logger.warning("Spotify callback failed: %s", exc)
        return _callback_error("spotify_error", connect)

    if connect:
        with SessionLocal() as db:
            problem = link_spotify_to_user(db, user, profile=profile, token=token)
        if problem:
            return _callback_error(problem, True)
        return _redirect_to_profile(spotify="connected")

    with SessionLocal() as db:
        user = link_spotify_account(db, profile=profile, token=token)
        user_id = user.id
        auth_version = user.auth_version

    # Establish a fresh MusicVault session.
    login_user(user_id, auth_version)

    return _redirect_to_frontend()


@auth_bp.post("/logout")
def logout():
    # POST only, so a link or image on another site can't log the user out;
    # SameSite=Lax also keeps the cookie off cross-site POSTs.
    logout_user()
    return "", 204