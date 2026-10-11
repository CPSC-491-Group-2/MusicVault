import uuid
from functools import wraps

from flask import g, jsonify, session

from db.queries.user import get_user_by_id
from db.session import SessionLocal

# Set by the Spotify OAuth callback once login succeeds.
SESSION_USER_KEY = "user_id"


def _error_response(status_code, error, message):
    # A Response object (not a tuple) so flask-smorest passes it through
    # untouched instead of serializing it with the route's response schema.
    response = jsonify({"error": error, "message": message})
    response.status_code = status_code
    return response


def _unauthorized():
    return _error_response(
        401, "Unauthorized", "You must be logged in to access this resource."
    )


def login_required(view):
    """Reject the request with 401 unless the session holds a real user.

    The session cookie is signed with SECRET_KEY, so its contents can't be
    forged, but the user it points at may since have been deleted. On
    success the user is available to the view as g.current_user.
    """

    @wraps(view)
    def wrapper(*args, **kwargs):
        raw_user_id = session.get(SESSION_USER_KEY)
        if not isinstance(raw_user_id, str):
            return _unauthorized()
        try:
            user_id = uuid.UUID(raw_user_id)
        except ValueError:
            return _unauthorized()

        with SessionLocal() as db:
            user = get_user_by_id(db, user_id)

        if user is None:
            # Account was deleted after login; drop the stale session.
            session.clear()
            return _unauthorized()

        g.current_user = user
        return view(*args, **kwargs)

    return wrapper
