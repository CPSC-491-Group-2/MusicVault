import secrets
from urllib.parse import urlencode

from flask import Blueprint, current_app, jsonify, redirect, request, session

from app.auth import SESSION_USER_KEY
from app.services.spotify_auth import (
    SpotifyAuthError,
    build_authorize_url,
    exchange_code_for_token,
    get_current_user_profile,
)
from db.queries.spotify_account import link_spotify_account
from db.session import SessionLocal

# Plain Flask blueprint (not flask-smorest): these endpoints are browser
# redirects, not JSON API resources. The path matches frontend/lib/auth.ts.
auth_bp = Blueprint("auth", __name__)

STATE_SESSION_KEY = "spotify_oauth_state"
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


@auth_bp.get("/login")
def spotify_login():
    not_configured = _not_configured_response()
    if not_configured:
        return not_configured

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


@auth_bp.get("/callback")
def spotify_callback():
    not_configured = _not_configured_response()
    if not_configured:
        return not_configured

    # pop() makes each state single-use, even if this attempt fails.
    expected_state = session.pop(STATE_SESSION_KEY, None)
    received_state = request.args.get("state")
    if (
        not expected_state
        or not received_state
        or not secrets.compare_digest(expected_state, received_state)
    ):
        current_app.logger.warning("Spotify callback rejected: invalid state")
        return _redirect_to_frontend("invalid_state")

    if request.args.get("error"):
        if request.args["error"] == "access_denied":
            return _redirect_to_frontend("access_denied")
        return _redirect_to_frontend("spotify_error")

    code = request.args.get("code")
    if not code:
        return _redirect_to_frontend("spotify_error")

    config = current_app.config
    try:
        token = exchange_code_for_token(
            code=code,
            client_id=config["SPOTIFY_CLIENT_ID"],
            client_secret=config["SPOTIFY_CLIENT_SECRET"],
            redirect_uri=config["SPOTIFY_REDIRECT_URI"],
        )
        profile = get_current_user_profile(token["access_token"])
    except SpotifyAuthError as exc:
        current_app.logger.warning("Spotify callback failed: %s", exc)
        return _redirect_to_frontend("spotify_error")

    with SessionLocal() as db:
        user = link_spotify_account(db, profile=profile, token=token)
        user_id = str(user.id)

    # Start a fresh session on login so nothing set before it carries over.
    session.clear()
    session[SESSION_USER_KEY] = user_id
    return _redirect_to_frontend()


@auth_bp.post("/logout")
def logout():
    # POST only, so a link or image on another site can't log the user out;
    # SameSite=Lax also keeps the cookie off cross-site POSTs.
    session.clear()
    return "", 204
