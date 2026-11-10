
"""
MusicVault SOC 2 Incident Simulation:
Unauthorized Cross-User Data Access

All users are synthetic.
Uses the existing test database fixtures.
No Spotify credentials or production data are used.
"""

import uuid

import pytest


@pytest.fixture
def two_test_users(auth_app, make_db_user):
    """Create two independent users and sessions."""

    user_a = make_db_user("SOC2 User A")
    user_b = make_db_user("SOC2 User B")

    client_a = auth_app.test_client()
    client_b = auth_app.test_client()

    # Simulate authenticated User A.
    with client_a.session_transaction() as session:
        session["user_id"] = str(user_a)
        session["auth_version"] = 1

    # Simulate authenticated User B.
    with client_b.session_transaction() as session:
        session["user_id"] = str(user_b)
        session["auth_version"] = 1

    return user_a, user_b, client_a, client_b


def test_users_can_access_their_own_profiles(two_test_users):
    """Baseline: legitimate access must succeed."""

    user_a, user_b, client_a, client_b = two_test_users

    response_a = client_a.get(f"/api/v1/users/{user_a}")
    response_b = client_b.get(f"/api/v1/users/{user_b}")

    assert response_a.status_code == 200
    assert response_a.get_json()["id"] == str(user_a)
    assert response_a.get_json()["display_name"] == "SOC2 User A"

    assert response_b.status_code == 200
    assert response_b.get_json()["id"] == str(user_b)
    assert response_b.get_json()["display_name"] == "SOC2 User B"


def test_user_a_cannot_access_user_b(two_test_users):
    """Simulate User A attempting to read User B's account."""

    user_a, user_b, client_a, client_b = two_test_users

    response = client_a.get(f"/api/v1/users/{user_b}")

    assert response.status_code == 403
    assert response.get_json() == {
        "error": "Forbidden",
        "message": "You do not have access to this resource.",
    }

    response_text = response.get_data(as_text=True)

    assert str(user_b) not in response_text
    assert "SOC2 User B" not in response_text


def test_user_b_cannot_access_user_a(two_test_users):
    """Verify authorization in the opposite direction."""

    user_a, user_b, client_a, client_b = two_test_users

    response = client_b.get(f"/api/v1/users/{user_a}")

    assert response.status_code == 403
    assert str(user_a) not in response.get_data(as_text=True)


def test_anonymous_user_cannot_access_profile(
    auth_app,
    make_db_user,
):
    """An unauthenticated client must be rejected."""

    target_user = make_db_user("Protected Account")

    anonymous_client = auth_app.test_client()

    response = anonymous_client.get(
        f"/api/v1/users/{target_user}"
    )

    assert response.status_code == 401
    assert "Protected Account" not in response.get_data(
        as_text=True
    )


def test_forged_header_cannot_change_identity(two_test_users):
    """A client-supplied user header must not override the session."""

    user_a, user_b, client_a, client_b = two_test_users

    response = client_a.get(
        f"/api/v1/users/{user_b}",
        headers={"X-User-ID": str(user_b)},
    )

    assert response.status_code == 403

    # Verify the actual session still belongs to A.
    me = client_a.get("/api/v1/me")

    assert me.status_code == 200
    assert me.get_json()["id"] == str(user_a)


def test_unknown_user_id_returns_same_forbidden_response(
    two_test_users,
):
    """Prevent determining whether a different account exists."""

    user_a, user_b, client_a, client_b = two_test_users

    known_user_response = client_a.get(
        f"/api/v1/users/{user_b}"
    )

    unknown_user_response = client_a.get(
        f"/api/v1/users/{uuid.uuid4()}"
    )

    assert known_user_response.status_code == 403
    assert unknown_user_response.status_code == 403

    assert (
        known_user_response.get_json()
        == unknown_user_response.get_json()
    )
