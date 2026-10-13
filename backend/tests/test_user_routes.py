from __future__ import annotations

import uuid

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
