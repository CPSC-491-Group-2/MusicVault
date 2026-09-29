from __future__ import annotations

import uuid

from db.queries.user import create_user, delete_user
from db.session import SessionLocal


def test_get_user_route_returns_user_from_database(client, require_live_database):
    # The route opens its own DB connection, so the fixture user has to be a
    # real commit (not the SAVEPOINT-isolated db_session) to be visible to it.
    with SessionLocal() as setup_db:
        user = create_user(
            setup_db, email="flask-route@example.com", display_name="Route Test"
        )
        user_id = user.id

    try:
        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        body = response.get_json()
        assert body["id"] == str(user_id)
        assert body["email"] == "flask-route@example.com"
        assert body["display_name"] == "Route Test"
    finally:
        with SessionLocal() as cleanup_db:
            delete_user(cleanup_db, user_id)


def test_get_user_route_missing_returns_404(client, require_live_database):
    response = client.get(f"/api/v1/users/{uuid.uuid4()}")

    assert response.status_code == 404
