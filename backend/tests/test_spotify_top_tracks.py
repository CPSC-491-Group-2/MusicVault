"""Tests for MusicVault's Spotify top-tracks endpoint."""

import pytest
from app import create_app
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from services.spotify_service import (
    SpotifyAuthenticationError,
    SpotifyPermissionError,
    SpotifyRateLimitError,
    SpotifyResourceNotFoundError,
    SpotifyServiceError,
)


def test_top_tracks_requires_authentication():
    """Unauthenticated users cannot retrieve Spotify listening data."""

    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()

    response = client.get("/api/v1/spotify/top-tracks")

    assert response.status_code == 401

    response_data = response.get_json()
    assert response_data["message"] == "Authentication required"


def test_linked_user_receives_normalized_top_tracks():
    """A linked user can retrieve normalized Spotify tracks."""

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="mv28-test-only-secret-key",
    )

    user_id = uuid.uuid4()

    fake_account = SimpleNamespace(
        user_id=user_id,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
        token_expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)),
        scope="user-top-read",
    )

    normalized_response = {
        "items": [
            {
                "spotify_id": "track123",
                "title": "Example Song",
                "artists": [
                    {
                        "spotify_id": "artist123",
                        "name": "Example Artist",
                    }
                ],
                "album": {
                    "spotify_id": "album123",
                    "name": "Example Album",
                    "image_url": None,
                },
                "duration_ms": 215000,
                "popularity": 75,
                "explicit": False,
                "spotify_url": None,
            }
        ],
        "total": 1,
        "limit": 20,
        "offset": 0,
        "next": None,
        "previous": None,
    }

    fake_db = MagicMock()
    fake_db.scalar.return_value = fake_account

    fake_session = MagicMock()
    fake_session.__enter__.return_value = fake_db
    fake_session.__exit__.return_value = None

    with (
        patch(
            "app.routes.spotify.SessionLocal",
            return_value=fake_session,
        ),
        patch("app.routes.spotify.SpotifyService") as mock_service_class,
    ):
        mock_service_class.return_value.get_normalized_user_top_tracks.return_value = (
            normalized_response
        )

        client = app.test_client()

        with client.session_transaction() as flask_session:
            flask_session["user_id"] = str(user_id)

        response = client.get("/api/v1/spotify/top-tracks")

    assert response.status_code == 200

    response_data = response.get_json()

    assert response_data["items"][0]["spotify_id"] == "track123"
    assert response_data["items"][0]["title"] == "Example Song"
    assert response_data["items"][0]["artists"][0]["name"] == ("Example Artist")
    assert response_data["total"] == 1
    assert response_data["limit"] == 20
    assert response_data["offset"] == 0

    mock_service_class.assert_called_once_with("fake-access-token")
    mock_service_class.return_value.get_normalized_user_top_tracks.assert_called_once_with(
        limit=20,
        time_range="medium_term",
        offset=0,
    )


def test_top_tracks_accepts_pagination_and_time_range():
    """Valid query parameters are forwarded to SpotifyService."""

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="mv28-test-only-secret-key",
    )

    user_id = uuid.uuid4()

    fake_account = SimpleNamespace(
        user_id=user_id,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
        token_expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)),
        scope="user-top-read",
    )

    fake_db = MagicMock()
    fake_db.scalar.return_value = fake_account

    fake_session = MagicMock()
    fake_session.__enter__.return_value = fake_db

    normalized_response = {
        "items": [],
        "total": 0,
        "limit": 10,
        "offset": 5,
        "next": None,
        "previous": None,
    }

    with (
        patch("app.routes.spotify.SessionLocal", return_value=fake_session),
        patch("app.routes.spotify.SpotifyService") as mock_service_class,
    ):
        mock_service = mock_service_class.return_value
        mock_service.get_normalized_user_top_tracks.return_value = normalized_response

        client = app.test_client()

        with client.session_transaction() as flask_session:
            flask_session["user_id"] = str(user_id)

        response = client.get(
            "/api/v1/spotify/top-tracks" "?limit=10&offset=5&time_range=short_term"
        )

    assert response.status_code == 200
    assert response.get_json()["limit"] == 10
    assert response.get_json()["offset"] == 5

    mock_service.get_normalized_user_top_tracks.assert_called_once_with(
        limit=10,
        time_range="short_term",
        offset=5,
    )


@pytest.mark.parametrize(
    "query_string",
    [
        "?limit=0",
        "?limit=51",
        "?limit=invalid",
        "?offset=-1",
        "?offset=invalid",
        "?time_range=invalid",
    ],
)
def test_top_tracks_rejects_invalid_query_parameters(query_string):
    """Invalid query parameters should fail validation."""

    app = create_app()
    app.config.update(TESTING=True)

    client = app.test_client()

    response = client.get(f"/api/v1/spotify/top-tracks{query_string}")

    assert response.status_code == 422


@pytest.mark.parametrize(
    "spotify_error, expected_status",
    [
        (SpotifyPermissionError("Spotify permission denied"), 403),
        (SpotifyRateLimitError(retry_after="30"), 429),
    ],
)
def test_top_tracks_handles_spotify_errors(spotify_error, expected_status):
    """Spotify permission and rate-limit errors return correct status codes."""

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="mv28-test-only-secret-key",
    )

    user_id = uuid.uuid4()

    fake_account = SimpleNamespace(
        user_id=user_id,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
        token_expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)),
        scope="user-top-read",
    )

    fake_db = MagicMock()
    fake_db.scalar.return_value = fake_account

    fake_session = MagicMock()
    fake_session.__enter__.return_value = fake_db

    with (
        patch(
            "app.routes.spotify.SessionLocal",
            return_value=fake_session,
        ),
        patch(
            "app.routes.spotify.SpotifyService",
        ) as mock_service_class,
    ):
        mock_service = mock_service_class.return_value
        mock_service.get_normalized_user_top_tracks.side_effect = spotify_error

        client = app.test_client()

        with client.session_transaction() as flask_session:
            flask_session["user_id"] = str(user_id)

        response = client.get("/api/v1/spotify/top-tracks")

    assert response.status_code == expected_status

    response_data = response.get_json()
    assert response_data["message"]

    if expected_status == 429:
        assert response.headers["Retry-After"] == "30"


def test_top_tracks_refreshes_rejected_token_and_retries():
    """A rejected access token is refreshed and retried once."""

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="mv28-test-only-secret-key",
    )

    user_id = uuid.uuid4()

    fake_account = SimpleNamespace(
        user_id=user_id,
        access_token="old-access-token",
        refresh_token="fake-refresh-token",
        token_expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)),
        scope="user-top-read",
    )

    fake_db = MagicMock()
    fake_db.scalar.return_value = fake_account

    fake_session = MagicMock()
    fake_session.__enter__.return_value = fake_db

    normalized_response = {
        "items": [],
        "total": 0,
        "limit": 20,
        "offset": 0,
        "next": None,
        "previous": None,
    }

    with (
        patch(
            "app.routes.spotify.SessionLocal",
            return_value=fake_session,
        ),
        patch(
            "app.routes.spotify.SpotifyService",
        ) as mock_service_class,
        patch(
            "app.routes.spotify.refresh_access_token",
        ) as mock_refresh,
    ):
        mock_service = mock_service_class.return_value

        # Spotify rejects the first request, then accepts the retry.
        mock_service.get_normalized_user_top_tracks.side_effect = [
            SpotifyAuthenticationError("Spotify authentication failed"),
            normalized_response,
        ]

        mock_refresh.return_value = {
            "access_token": "new-access-token",
            "expires_in": 3600,
        }

        app.config["SPOTIFY_CLIENT_ID"] = "test-client-id"
        app.config["SPOTIFY_CLIENT_SECRET"] = "test-client-secret"

        client = app.test_client()

        with client.session_transaction() as flask_session:
            flask_session["user_id"] = str(user_id)

        response = client.get("/api/v1/spotify/top-tracks")

    assert response.status_code == 200
    assert response.get_json()["items"] == []

    # Initial request plus one retry.
    assert mock_service.get_normalized_user_top_tracks.call_count == 2

    # Refresh should only happen once.
    mock_refresh.assert_called_once()

    # Updated credentials should be saved.
    assert fake_account.access_token == "new-access-token"
    fake_db.commit.assert_called_once()

    # Verify that the second request used the refreshed token.
    assert mock_service_class.call_args_list[0].args == ("old-access-token",)
    assert mock_service_class.call_args_list[1].args == ("new-access-token",)


def test_top_tracks_response_matches_documented_schema():
    """Normalized Spotify responses match the documented API contract."""
    from app.schemas.spotify import SpotifyTopTracksResponseSchema

    response_data = {
        "items": [
            {
                "spotify_id": "track123",
                "title": "Example Song",
                "artists": [
                    {
                        "spotify_id": "artist123",
                        "name": "Example Artist",
                    }
                ],
                "album": {
                    "spotify_id": "album123",
                    "name": "Example Album",
                    "image_url": "https://example.com/cover.jpg",
                },
                "duration_ms": 215000,
                "popularity": 75,
                "explicit": False,
                "spotify_url": "https://open.spotify.com/track/track123",
            }
        ],
        "total": 1,
        "limit": 20,
        "offset": 0,
        "next": None,
        "previous": None,
    }

    schema = SpotifyTopTracksResponseSchema()

    errors = schema.validate(response_data)

    assert errors == {}

    serialized = schema.dump(response_data)

    assert set(serialized.keys()) == {
        "items",
        "total",
        "limit",
        "offset",
        "next",
        "previous",
    }

    track = serialized["items"][0]

    assert set(track.keys()) == {
        "spotify_id",
        "title",
        "artists",
        "album",
        "duration_ms",
        "popularity",
        "explicit",
        "spotify_url",
    }

    assert isinstance(track["spotify_id"], str)
    assert isinstance(track["title"], str)
    assert isinstance(track["artists"], list)
    assert isinstance(track["album"], dict)
    assert isinstance(track["duration_ms"], int)
    assert isinstance(track["popularity"], int)
    assert isinstance(track["explicit"], bool)

    assert set(track["artists"][0].keys()) == {
        "spotify_id",
        "name",
    }

    assert set(track["album"].keys()) == {
        "spotify_id",
        "name",
        "image_url",
    }


@pytest.mark.parametrize(
    "spotify_error, expected_message",
    [
        (
            SpotifyResourceNotFoundError("Spotify resource not found"),
            "Spotify resource unavailable",
        ),
        (
            SpotifyServiceError("Spotify request failed"),
            "Spotify service unavailable",
        ),
        (
            ValueError("Invalid Spotify track metadata"),
            "Invalid response from Spotify",
        ),
    ],
)
def test_top_tracks_handles_upstream_failures(spotify_error, expected_message):
    """Upstream failures should return safe HTTP 502 responses."""

    app = create_app()
    app.config.update(
        TESTING=True,
        SECRET_KEY="mv28-test-only-secret-key",
    )

    user_id = uuid.uuid4()

    fake_account = SimpleNamespace(
        user_id=user_id,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
        token_expires_at=(datetime.now(timezone.utc) + timedelta(hours=1)),
        scope="user-top-read",
    )

    fake_db = MagicMock()
    fake_db.scalar.return_value = fake_account

    fake_session = MagicMock()
    fake_session.__enter__.return_value = fake_db

    with (
        patch("app.routes.spotify.SessionLocal", return_value=fake_session),
        patch("app.routes.spotify.SpotifyService") as mock_service_class,
    ):
        mock_service = mock_service_class.return_value
        mock_service.get_normalized_user_top_tracks.side_effect = spotify_error

        client = app.test_client()

        with client.session_transaction() as flask_session:
            flask_session["user_id"] = str(user_id)

        response = client.get("/api/v1/spotify/top-tracks")

    assert response.status_code == 502

    response_data = response.get_json()
    assert response_data["message"] == expected_message

    # Internal Spotify exception details must not be exposed.
    assert str(spotify_error) not in response.get_data(as_text=True)

    mock_service.get_normalized_user_top_tracks.assert_called_once()
