from __future__ import annotations

import uuid

from db.queries.user import create_user
from db.session import SessionLocal
from models.spotify_account import SpotifyAccount
from models.user import User

FORBIDDEN = {
    "error": "Forbidden",
    "message": "You do not have access to this resource.",
}


def test_get_own_user_returns_user_from_database(auth_client, log_in, db_user):
    log_in(db_user)

    response = auth_client.get(f"/api/v1/users/{db_user}")

    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == str(db_user)
    assert body["display_name"] == "Protected Test"


def test_get_another_user_is_forbidden(auth_client, log_in, make_db_user):
    me = make_db_user("Me")
    someone_else = make_db_user("Someone Else")
    log_in(me)

    response = auth_client.get(f"/api/v1/users/{someone_else}")

    assert response.status_code == 403
    assert response.get_json() == FORBIDDEN
    assert "Someone Else" not in response.get_data(as_text=True)


def test_get_nonexistent_user_is_forbidden_not_404(auth_client, log_in, db_user):
    # Same answer as for a real account, so the route can't be used to find
    # out which user IDs exist.
    log_in(db_user)

    response = auth_client.get(f"/api/v1/users/{uuid.uuid4()}")

    assert response.status_code == 403
    assert response.get_json() == FORBIDDEN


def test_get_user_without_login_is_unauthorized(client):
    response = client.get(f"/api/v1/users/{uuid.uuid4()}")

    assert response.status_code == 401


# ============================================================
# CURRENT USER AUTHENTICATION METHOD TESTS
# ============================================================


def test_get_me_requires_login(client):
    response = client.get("/api/v1/me")

    assert response.status_code == 401


def test_get_me_without_auth_methods(auth_client, log_in, db_user):
    log_in(db_user)

    response = auth_client.get("/api/v1/me")

    assert response.status_code == 200

    body = response.get_json()

    assert body["id"] == str(db_user)
    assert body["has_password"] is False
    assert body["spotify"]["connected"] is False
    assert body["spotify"]["display_name"] is None


def test_get_me_local_password_account(auth_client, log_in, db_user):
    # Dummy hash for database testing; not used for authentication.
    with SessionLocal() as db:
        user = db.get(User, db_user)
        assert user is not None
        user.password_hash = "test-placeholder-not-a-real-hash"
        db.commit()

    log_in(db_user)

    response = auth_client.get("/api/v1/me")

    assert response.status_code == 200

    body = response.get_json()

    assert body["has_password"] is True
    assert body["spotify"]["connected"] is False
    assert "password_hash" not in body


def test_get_me_spotify_only(auth_client, log_in, clean_database):
    with SessionLocal() as db:
        user = create_user(
            db,
            display_name="Spotify Only",
        )
        user_id = user.id

        account = SpotifyAccount(
            user_id=user_id,
            spotify_account_id="test-spotify-only",
            display_name="Spotify Listener",
            access_token="test-token-do-not-expose",
        )

        db.add(account)
        db.commit()

    log_in(user_id)

    response = auth_client.get("/api/v1/me")

    assert response.status_code == 200

    body = response.get_json()

    assert body["email"] is None
    assert body["has_password"] is False
    assert body["spotify"]["connected"] is True
    assert body["spotify"]["display_name"] == "Spotify Listener"
    assert "access_token" not in str(body)


def test_get_me_with_both_auth_methods(auth_client, log_in, clean_database):
    with SessionLocal() as db:
        user = create_user(
            db,
            email="both@example.com",
            display_name="Both Methods",
            password_hash="test-placeholder-not-a-real-hash",
        )
        user_id = user.id

        account = SpotifyAccount(
            user_id=user_id,
            spotify_account_id="test-spotify-both",
            display_name="Connected Listener",
        )

        db.add(account)
        db.commit()

    log_in(user_id)

    response = auth_client.get("/api/v1/me")

    assert response.status_code == 200

    body = response.get_json()

    assert body["email"] == "both@example.com"
    assert body["has_password"] is True
    assert body["spotify"]["connected"] is True
    assert body["spotify"]["display_name"] == "Connected Listener"

    assert "password_hash" not in body
    assert "access_token" not in body
    assert "refresh_token" not in body
