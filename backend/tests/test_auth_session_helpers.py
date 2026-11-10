import uuid

from flask import session

from app.auth import SESSION_USER_KEY, SESSION_VERSION_KEY, login_user, logout_user


def test_login_user_creates_session(auth_app):
    user_id = uuid.uuid4()

    with auth_app.test_request_context():
        session["old_session_value"] = "temporary"

        login_user(user_id, 3)

        assert session[SESSION_USER_KEY] == str(user_id)
        assert session[SESSION_VERSION_KEY] == 3
        assert "old_session_value" not in session


def test_logout_user_clears_session(auth_app):
    user_id = uuid.uuid4()

    with auth_app.test_request_context():
        login_user(user_id, 1)

        logout_user()

        assert SESSION_USER_KEY not in session
        assert SESSION_VERSION_KEY not in session
