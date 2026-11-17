import uuid
from functools import wraps
from http import HTTPStatus

from flask import g, jsonify, session

from db.queries.user import get_user_by_id
from db.session import SessionLocal

# Shared session keys for Spotify and local authentication.
SESSION_USER_KEY = "user_id"
SESSION_VERSION_KEY = "auth_version"

def login_user(user_id: uuid.UUID, auth_version: int) -> None:
    """Establish a fresh authenticated MusicVault session."""

    session.clear()
    session[SESSION_USER_KEY] = str(user_id)
    session[SESSION_VERSION_KEY] = auth_version


def logout_user() -> None:
    """Clear the current MusicVault session."""

    session.clear()

def _json_response(status_code, body):
    # A Response object (not a tuple) so flask-smorest passes it through
    # untouched instead of serializing it with the route's response schema.
    response = jsonify(body)
    response.status_code = status_code
    return response


def error_response(status_code, code, message):
    return _json_response(
        status_code,
        {
            "error": HTTPStatus(status_code).phrase,
            "message": message,
            "code": code,
        },
    )


def unauthorized():
    return error_response(
        401, "unauthorized", "You must be logged in to access this resource."
    )


def session_revoked():
    return error_response(
        401, "session_revoked", "Your session has ended. Please log in again."
    )


def forbidden():
    """For a logged-in user asking for something that isn't theirs."""
    return _json_response(
        403,
        {"error": "Forbidden", "message": "You do not have access to this resource."},
    )


def get_session_user():
    """Resolve the session's user, or return the error code that rejects it."""

    raw_user_id = session.get(SESSION_USER_KEY)
    if not isinstance(raw_user_id, str):
        return None, "unauthorized"
    try:
        user_id = uuid.UUID(raw_user_id)
    except ValueError:
        return None, "unauthorized"

    with SessionLocal() as db:
        user = get_user_by_id(db, user_id)

    if user is None:
        # Account was deleted after login; drop the stale session.
        session.clear()
        return None, "unauthorized"

    if session.get(SESSION_VERSION_KEY) != user.auth_version:
        session.clear()
        return None, "session_revoked"

    return user, None


def login_required(view):
    """Reject the request with 401 unless the session holds a real user.

    The session cookie is signed with SECRET_KEY, so its contents can't be
    forged, but the user it points at may since have been deleted, and its
    auth_version may be older than the user's after a password change. On
    success the user is available to the view as g.current_user.
    """

    @wraps(view)
    def wrapper(*args, **kwargs):
        user, code = get_session_user()
        if user is None:
            if code == "session_revoked":
                return session_revoked()
            return unauthorized()

        g.current_user = user
        return view(*args, **kwargs)

    return wrapper
