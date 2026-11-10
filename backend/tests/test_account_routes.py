import uuid

import pytest
from argon2 import PasswordHasher
from sqlalchemy import func, select

import app.routes.account as account_routes
from app.security.passwords import hash_password, needs_rehash, verify_password
from db.queries.user import create_user
from db.session import SessionLocal
from models.song import Song
from models.spotify_account import SpotifyAccount
from models.user import User
from models.user_top_song import UserTopSong

REGISTER = "/api/v1/auth/register"
LOGIN = "/api/v1/auth/login"
ME = "/api/v1/me"
PASSWORD = "/api/v1/me/password"
SPOTIFY = "/api/v1/me/spotify"

ME_KEYS = {
    "id",
    "email",
    "display_name",
    "created_at",
    "updated_at",
    "has_password",
    "spotify",
}
INVALID_CREDENTIALS = {
    "error": "Unauthorized",
    "message": "Incorrect email or password.",
    "code": "invalid_credentials",
}
EMAIL_TAKEN = {
    "error": "Conflict",
    "message": "An account with this email already exists.",
    "code": "email_taken",
}
STALE_HASHER = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1)


def make_user(email=None, password=None, display_name="Test User"):
    with SessionLocal() as db:
        user = create_user(
            db,
            email=email,
            display_name=display_name,
            password_hash=hash_password(password) if password else None,
        )
    return user.id


def login(client, email, password):
    return client.post(LOGIN, json={"email": email, "password": password})


def auth_version(user_id):
    with SessionLocal() as db:
        return db.get(User, user_id).auth_version


def stored_user(user_id):
    with SessionLocal() as db:
        return db.get(User, user_id)


def store_stale_hash(user_id, password):
    with SessionLocal() as db:
        db.get(User, user_id).password_hash = STALE_HASHER.hash(password)
        db.commit()


def change_password_mid_request(monkeypatch, user_id, **columns):
    # The routes hash after they have checked access and before they write.
    def change_then_hash(password):
        with SessionLocal() as db:
            user = db.get(User, user_id)
            user.password_hash = hash_password("other-password-1")
            user.auth_version += 1
            for name, value in columns.items():
                setattr(user, name, value)
            db.commit()
        return hash_password(password)

    monkeypatch.setattr(account_routes, "hash_password", change_then_hash)


def link_spotify(user_id):
    with SessionLocal() as db:
        db.add(
            SpotifyAccount(
                user_id=user_id,
                spotify_account_id=f"spotify-{uuid.uuid4()}",
                display_name="Linked",
                access_token="token",
            )
        )
        db.commit()


def spotify_rows(user_id):
    with SessionLocal() as db:
        return db.scalar(
            select(func.count())
            .select_from(SpotifyAccount)
            .where(SpotifyAccount.user_id == user_id)
        )


def test_register_creates_account_and_logs_in(auth_client, clean_database):
    response = auth_client.post(
        REGISTER,
        json={
            "email": "New@Example.com",
            "password": "correct-horse-1",
            "display_name": "New",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert set(body) == ME_KEYS
    assert body["email"] == "new@example.com"
    assert body["display_name"] == "New"
    assert body["has_password"] is True
    assert body["spotify"] == {"connected": False, "display_name": None}
    assert "correct-horse-1" not in response.get_data(as_text=True)

    me = auth_client.get(ME)
    assert me.status_code == 200
    assert me.get_json()["id"] == body["id"]


def test_register_duplicate_email_is_rejected(auth_app, clean_database):
    first = auth_app.test_client().post(
        REGISTER, json={"email": "taken@example.com", "password": "correct-horse-1"}
    )
    assert first.status_code == 201

    response = auth_app.test_client().post(
        REGISTER, json={"email": "TAKEN@example.com", "password": "another-pass-1"}
    )

    assert response.status_code == 409
    assert response.get_json() == EMAIL_TAKEN


def test_register_rejects_invalid_email(client):
    response = client.post(
        REGISTER,
        json={
            "email": "invalid-email",
            "password": "ExamplePassword123",
        },
    )

    assert response.status_code == 422


def test_login_returns_user_and_rotates_session(auth_client, clean_database):
    user_id = make_user("login@example.com", "correct-horse-1")
    with auth_client.session_transaction() as sess:
        sess["leftover"] = "from before login"

    response = login(auth_client, "LOGIN@example.com", "correct-horse-1")

    assert response.status_code == 200
    assert set(response.get_json()) == ME_KEYS
    assert response.get_json()["id"] == str(user_id)
    with auth_client.session_transaction() as sess:
        assert sess["user_id"] == str(user_id)
        assert sess["auth_version"] == 1
        assert "leftover" not in sess


def test_login_failures_share_one_response(auth_client, clean_database):
    make_user("login@example.com", "correct-horse-1")
    make_user("no-password@example.com")

    for email, password in [
        ("login@example.com", "wrong-password"),
        ("nobody@example.com", "correct-horse-1"),
        ("no-password@example.com", "correct-horse-1"),
    ]:
        response = login(auth_client, email, password)
        assert response.status_code == 401, email
        assert response.get_json() == INVALID_CREDENTIALS, email

    with auth_client.session_transaction() as sess:
        assert "user_id" not in sess


def test_logout_clears_session(auth_client):
    with auth_client.session_transaction() as sess:
        sess["user_id"] = str(uuid.uuid4())

    response = auth_client.post("/api/v1/auth/logout")

    assert response.status_code == 204

    with auth_client.session_transaction() as sess:
        assert "user_id" not in sess


def test_password_change_revokes_other_sessions(auth_app, clean_database):
    user_id = make_user("change@example.com", "correct-horse-1")
    current, other = auth_app.test_client(), auth_app.test_client()
    assert login(current, "change@example.com", "correct-horse-1").status_code == 200
    assert login(other, "change@example.com", "correct-horse-1").status_code == 200

    response = current.put(
        PASSWORD,
        json={"current_password": "correct-horse-1", "new_password": "correct-horse-2"},
    )

    assert response.status_code == 200
    assert set(response.get_json()) == ME_KEYS
    assert auth_version(user_id) == 2
    assert current.get(ME).status_code == 200
    revoked = other.get(ME)
    assert revoked.status_code == 401
    assert revoked.get_json()["code"] == "session_revoked"
    assert login(other, "change@example.com", "correct-horse-1").status_code == 401
    assert login(other, "change@example.com", "correct-horse-2").status_code == 200


def test_password_change_needs_the_current_password(auth_client, clean_database):
    user_id = make_user("change@example.com", "correct-horse-1")
    login(auth_client, "change@example.com", "correct-horse-1")

    for body in (
        {"new_password": "correct-horse-2"},
        {"current_password": "wrong-password", "new_password": "correct-horse-2"},
    ):
        response = auth_client.put(PASSWORD, json=body)
        assert response.status_code == 403
        assert response.get_json() == {
            "error": "Forbidden",
            "message": "The current password is incorrect.",
            "code": "current_password_wrong",
        }

    assert auth_version(user_id) == 1


def test_passwordless_user_sets_password_and_email(
    auth_client, log_in, clean_database
):
    make_user("taken@example.com", "correct-horse-1")
    user_id = make_user(display_name="Spotify Only")
    log_in(user_id)

    missing = auth_client.put(PASSWORD, json={"new_password": "spotify-pass-1"})
    assert missing.status_code == 422
    assert missing.get_json()["errors"]["json"] == {
        "email": ["Missing data for required field."]
    }

    invalid = auth_client.put(
        PASSWORD, json={"email": "not-an-email", "new_password": "spotify-pass-1"}
    )
    assert invalid.status_code == 422
    assert invalid.get_json()["errors"]["json"] == {
        "email": ["Not a valid email address."]
    }

    taken = auth_client.put(
        PASSWORD, json={"email": "TAKEN@example.com", "new_password": "spotify-pass-1"}
    )
    assert taken.status_code == 409
    assert taken.get_json() == EMAIL_TAKEN

    response = auth_client.put(
        PASSWORD,
        json={
            "email": "Mine@Example.com",
            "new_password": "spotify-pass-1",
            "current_password": "ignored",
        },
    )
    assert response.status_code == 200
    assert response.get_json()["email"] == "mine@example.com"
    assert response.get_json()["has_password"] is True
    assert auth_client.get(ME).status_code == 200
    assert login(auth_client, "mine@example.com", "spotify-pass-1").status_code == 200


def test_disconnect_needs_a_password(auth_client, log_in, clean_database):
    user_id = make_user(display_name="Spotify Only")
    link_spotify(user_id)
    log_in(user_id)

    response = auth_client.delete(SPOTIFY)

    assert response.status_code == 409
    assert response.get_json() == {
        "error": "Conflict",
        "message": "Set a password before disconnecting Spotify.",
        "code": "password_required",
    }
    assert spotify_rows(user_id) == 1


def test_disconnect_removes_tokens_and_keeps_listening_data(
    auth_client, log_in, clean_database
):
    user_id = make_user("both@example.com", "correct-horse-1")
    link_spotify(user_id)
    with SessionLocal() as db:
        song = Song(title="Kept Song", artist_name="Kept Artist")
        db.add(song)
        db.flush()
        db.add(
            UserTopSong(
                user_id=user_id, song_id=song.id, time_range="short_term", rank=1
            )
        )
        db.commit()
    log_in(user_id)

    response = auth_client.delete(SPOTIFY)

    assert response.status_code == 200
    assert response.get_json()["spotify"] == {"connected": False, "display_name": None}
    assert spotify_rows(user_id) == 0
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(UserTopSong)) == 1

    assert auth_client.delete(SPOTIFY).status_code == 200


def test_account_changes_require_login(auth_client):
    for response in (
        auth_client.put(PASSWORD, json={"new_password": "correct-horse-2"}),
        auth_client.delete(SPOTIFY),
    ):
        assert response.status_code == 401
        assert response.get_json()["code"] == "unauthorized"


def test_login_upgrades_a_stale_hash(auth_client, clean_database):
    user_id = make_user("stale@example.com")
    store_stale_hash(user_id, "correct-horse-1")

    response = login(auth_client, "stale@example.com", "correct-horse-1")

    assert response.status_code == 200
    user = stored_user(user_id)
    assert verify_password(user.password_hash, "correct-horse-1")
    assert not needs_rehash(user.password_hash)
    assert user.auth_version == 1


def test_login_rehash_never_restores_a_changed_password(
    auth_client, monkeypatch, clean_database
):
    user_id = make_user("stale@example.com")
    store_stale_hash(user_id, "correct-horse-1")
    change_password_mid_request(monkeypatch, user_id)

    response = login(auth_client, "stale@example.com", "correct-horse-1")

    assert response.status_code == 401
    assert response.get_json() == INVALID_CREDENTIALS
    assert verify_password(stored_user(user_id).password_hash, "other-password-1")
    with auth_client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize(
    ("password", "body", "columns"),
    [
        ("correct-horse-1", {"current_password": "correct-horse-1"}, {}),
        (None, {"email": "mine@example.com"}, {"email": "first@example.com"}),
    ],
    ids=["has_password", "spotify_only"],
)
def test_password_change_that_loses_a_race_is_revoked(
    auth_client, log_in, monkeypatch, clean_database, password, body, columns
):
    user_id = make_user("race@example.com" if password else None, password)
    log_in(user_id)
    change_password_mid_request(monkeypatch, user_id, **columns)

    response = auth_client.put(
        PASSWORD, json={**body, "new_password": "mine-password-1"}
    )

    assert response.status_code == 401
    assert response.get_json()["code"] == "session_revoked"
    user = stored_user(user_id)
    assert verify_password(user.password_hash, "other-password-1")
    assert user.auth_version == 2
    with auth_client.session_transaction() as sess:
        assert "user_id" not in sess


@pytest.mark.parametrize(
    ("password", "body"),
    [
        (
            "correct-horse-1",
            {"current_password": "correct-horse-1", "email": "not-an-email"},
        ),
        (None, {"email": ""}),
    ],
    ids=["has_password", "email_already_set"],
)
def test_password_change_ignores_an_email_it_does_not_need(
    auth_client, log_in, clean_database, password, body
):
    user_id = make_user("kept@example.com", password)
    log_in(user_id)

    response = auth_client.put(
        PASSWORD, json={**body, "new_password": "correct-horse-2"}
    )

    assert response.status_code == 200
    assert response.get_json()["email"] == "kept@example.com"
    assert response.get_json()["has_password"] is True
