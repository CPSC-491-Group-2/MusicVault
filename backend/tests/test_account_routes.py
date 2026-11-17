
import uuid

from db.queries.user import get_user_by_email
from db.session import SessionLocal
from werkzeug.security import check_password_hash


def test_register_success(auth_client, clean_database):
    response = auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "ExamplePassword123",
            "display_name": "Test User",
        },
    )

    assert response.status_code == 201
    assert response.json["email"] == "test@example.com"
    assert response.json["display_name"] == "Test User"

    with SessionLocal() as db:
        user = get_user_by_email(db, "test@example.com")
        assert user is not None
        assert user.password_hash != "ExamplePassword123"
        assert check_password_hash(
            user.password_hash, "ExamplePassword123"
        )


def test_login_success(auth_client, clean_database):
    auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "ExamplePassword123",
        },
    )

    response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "ExamplePassword123",
        },
    )

    assert response.status_code == 200
    assert response.json["email"] == "login@example.com"


def test_login_invalid_password(auth_client, clean_database):
    auth_client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid@example.com",
            "password": "ExamplePassword123",
        },
    )

    response = auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "invalid@example.com",
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_register_duplicate_email(auth_client, clean_database):
    account = {
        "email": "duplicate@example.com",
        "password": "ExamplePassword123",
    }

    first = auth_client.post(
        "/api/v1/auth/register",
        json=account,
    )

    second = auth_client.post(
        "/api/v1/auth/register",
        json=account,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_register_rejects_invalid_email(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "ExamplePassword123",
        },
    )

    assert response.status_code == 422


def test_logout_clears_session(auth_client):
    with auth_client.session_transaction() as sess:
        sess["user_id"] = str(uuid.uuid4())

    response = auth_client.post("/api/v1/auth/logout")

    assert response.status_code == 204

    with auth_client.session_transaction() as sess:
        assert "user_id" not in sess
