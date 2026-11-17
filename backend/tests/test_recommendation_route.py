"""Integration tests for the recommendation API endpoint."""

from __future__ import annotations

import pytest

from db.session import SessionLocal
from recommendation_fixtures import load_into_database


RECOMMENDATIONS_URL = "/api/v1/recommendations"

pytestmark = pytest.mark.recommendation


@pytest.fixture
def recommendation_users(clean_database):
    """Load the fixed recommendation dataset into the test database."""

    with SessionLocal() as db:
        return load_into_database(db)


def test_recommendations_requires_login(auth_client):
    """A user must be authenticated before viewing recommendations."""

    response = auth_client.get(RECOMMENDATIONS_URL)

    assert response.status_code == 401
    assert response.is_json
    assert response.get_json() == {
        "error": "Unauthorized",
        "message": "You must be logged in to access this resource.",
        "code": "unauthorized",
    }


def test_recommendations_returns_ranked_results(
    auth_client,
    log_in,
    recommendation_users,
):
    """An authenticated user receives ranked recommendation results."""

    user_id = recommendation_users["indie_listener"]
    log_in(user_id)

    response = auth_client.get(RECOMMENDATIONS_URL)

    assert response.status_code == 200
    assert response.is_json

    body = response.get_json()

    assert "items" in body
    assert "total" in body

    assert body["total"] == len(body["items"])
    assert body["total"] > 0

    scores = [
        item["score"]
        for item in body["items"]
    ]

    assert scores == sorted(
        scores,
        reverse=True,
    )

    first = body["items"][0]

    assert "id" in first
    assert "title" in first
    assert "artist" in first
    assert "score" in first
    assert "reason" in first
    assert "components" in first

    assert isinstance(first["components"], dict)


def test_recommendations_returns_empty_when_user_has_no_seeds(
    auth_client,
    log_in,
    recommendation_users,
    make_db_user,
):
    """A user with no music preferences receives an empty result."""

    user_id = make_db_user("No Recommendation Seeds")

    log_in(user_id)

    response = auth_client.get(RECOMMENDATIONS_URL)

    assert response.status_code == 200
    assert response.is_json

    assert response.get_json() == {
        "items": [],
        "total": 0,
    }