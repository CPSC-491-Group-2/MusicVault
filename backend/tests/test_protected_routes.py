from __future__ import annotations

import uuid

import pytest
from flask import Flask

from db.queries.user import delete_user
from db.session import SessionLocal

ME = "/api/v1/me"
LOGOUT = "/api/auth/spotify/logout"

# Every route that needs a logged-in user. Add new ones here so the
# unauthorized cases below run against them too.
PROTECTED_ROUTES = [ME, f"/api/v1/users/{uuid.uuid4()}"]


def assert_unauthorized(response):
    assert response.status_code == 401
    assert response.is_json
    assert response.get_json() == {
        "error": "Unauthorized",
        "message": "You must be logged in to access this resource.",
    }


# --- unauthorized ----------------------------------------------------------


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_without_session_is_rejected(auth_client, path):
    assert_unauthorized(auth_client.get(path))


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_unsigned_session_cookie_is_rejected(auth_client, path):
    # Flask's cookie format, but without a valid signature.
    auth_client.set_cookie("session", '{"user_id": "%s"}' % uuid.uuid4())

    assert_unauthorized(auth_client.get(path))


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_cookie_signed_by_another_key_is_rejected(auth_client, path):
    other_app = Flask(__name__)
    other_app.secret_key = "some-other-key"
    serializer = other_app.session_interface.get_signing_serializer(other_app)
    auth_client.set_cookie("session", serializer.dumps({"user_id": str(uuid.uuid4())}))

    assert_unauthorized(auth_client.get(path))


@pytest.mark.parametrize("bad_user_id", ["not-a-uuid", "", 12345, None])
@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_malformed_user_id_is_rejected(auth_client, path, bad_user_id):
    with auth_client.session_transaction() as sess:
        sess["user_id"] = bad_user_id

    assert_unauthorized(auth_client.get(path))


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_without_secret_key_is_rejected(auth_app, path):
    # Without SECRET_KEY Flask can't read a session at all, so nobody is
    # logged in -- the route must fail closed rather than error.
    auth_app.config["SECRET_KEY"] = None

    assert_unauthorized(auth_app.test_client().get(path))


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_deleted_user_is_rejected_and_session_cleared(
    auth_client, log_in, db_user, path
):
    log_in(db_user)
    with SessionLocal() as db:
        delete_user(db, db_user)

    assert_unauthorized(auth_client.get(path))
    with auth_client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize("path", PROTECTED_ROUTES)
def test_unknown_user_is_rejected(auth_client, log_in, require_live_database, path):
    log_in(uuid.uuid4())

    assert_unauthorized(auth_client.get(path))


# --- authenticated ---------------------------------------------------------


def test_me_returns_logged_in_user(auth_client, log_in, db_user):
    log_in(db_user)

    response = auth_client.get(ME)

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == str(db_user)
    assert body["display_name"] == "Protected Test"
    assert set(body) == {"id", "email", "display_name", "created_at", "updated_at"}


def test_me_only_returns_the_session_user(auth_client, log_in, db_user):
    # There is no way to ask /me for someone else; the session decides.
    log_in(db_user)

    response = auth_client.get(f"{ME}?user_id={uuid.uuid4()}")

    assert response.get_json()["id"] == str(db_user)


# --- logout ----------------------------------------------------------------


def test_logout_ends_the_session(auth_client, log_in, db_user):
    log_in(db_user)
    assert auth_client.get(ME).status_code == 200

    response = auth_client.post(LOGOUT)

    assert response.status_code == 204
    assert_unauthorized(auth_client.get(ME))


def test_logout_without_session_is_harmless(auth_client):
    assert auth_client.post(LOGOUT).status_code == 204


def test_logout_rejects_get(auth_client):
    assert auth_client.get(LOGOUT).status_code == 405
