import uuid


def test_register_temporarily_disabled(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "ExamplePassword123",
        },
    )

    assert response.status_code == 503
    assert response.json["error"] == "Service Unavailable"


def test_login_temporarily_disabled(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "ExamplePassword123",
        },
    )

    assert response.status_code == 503


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