from unittest.mock import Mock, patch

import pytest

from services.spotify_service import SpotifyService


def make_spotify_track():
    """Create a sample Spotify track response."""
    return {
        "id": "track123",
        "name": "Example Song",
        "artists": [
            {
                "id": "artist123",
                "name": "Example Artist",
            }
        ],
        "album": {
            "id": "album123",
            "name": "Example Album",
            "images": [{"url": "https://example.com/album.jpg"}],
        },
        "duration_ms": 200000,
        "popularity": 75,
        "explicit": False,
        "external_urls": {"spotify": "https://open.spotify.com/track/track123"},
        "external_ids": {"isrc": "USABC1234567"},
    }


def make_spotify_response(items=None):
    """Create a sample paginated Spotify response."""
    if items is None:
        items = [make_spotify_track()]

    return {
        "items": items,
        "total": len(items),
        "limit": 20,
        "offset": 0,
        "next": None,
        "previous": None,
    }


@patch("services.spotify_service.requests.get")
def test_service_normalizes_successful_top_tracks(mock_get):
    """Successful Spotify responses return complete normalized tracks."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = make_spotify_response()
    mock_get.return_value = mock_response

    service = SpotifyService("test-access-token")

    result = service.get_normalized_user_top_tracks()

    assert result == {
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
                    "image_url": "https://example.com/album.jpg",
                },
                "duration_ms": 200000,
                "popularity": 75,
                "explicit": False,
                "spotify_url": "https://open.spotify.com/track/track123",
                "isrc": "USABC1234567",
            }
        ],
        "total": 1,
        "limit": 20,
        "offset": 0,
        "next": None,
        "previous": None,
    }

    mock_get.assert_called_once()


@patch("services.spotify_service.requests.get")
def test_service_handles_empty_top_tracks(mock_get):
    """Empty Spotify responses produce valid empty results."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = make_spotify_response(items=[])
    mock_get.return_value = mock_response

    service = SpotifyService("test-access-token")

    result = service.get_normalized_user_top_tracks()

    assert result["items"] == []
    assert result["total"] == 0
    assert result["limit"] == 20
    assert result["offset"] == 0

    mock_get.assert_called_once()


@patch("services.spotify_service.requests.get")
def test_service_forwards_pagination_parameters(mock_get):
    """Spotify receives the requested pagination parameters."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = make_spotify_response()
    mock_get.return_value = mock_response

    service = SpotifyService("test-access-token")

    service.get_user_top_track(limit=10, offset=30)

    mock_get.assert_called_once_with(
        "https://api.spotify.com/v1/me/top/tracks",
        headers={"Authorization": "Bearer test-access-token"},
        params={
            "limit": 10,
            "time_range": "medium_term",
            "offset": 30,
        },
        timeout=10,
    )


@patch("services.spotify_service.requests.get")
def test_service_forwards_time_range(mock_get):
    """Spotify receives the selected time range."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = make_spotify_response()
    mock_get.return_value = mock_response

    service = SpotifyService("test-access-token")

    service.get_user_top_track(time_range="short_term")

    assert mock_get.call_args.kwargs["params"]["time_range"] == "short_term"


@patch("services.spotify_service.requests.get")
def test_service_does_not_expose_access_tokens(mock_get):
    """Normalized API results must not include Spotify access tokens."""
    secret_token = "private-spotify-access-token"

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = make_spotify_response()
    mock_get.return_value = mock_response

    service = SpotifyService(secret_token)

    result = service.get_normalized_user_top_tracks()

    assert "access_token" not in result
    assert "access_token" not in result["items"][0]
    assert secret_token not in str(result)

    assert mock_get.call_args.kwargs["headers"]["Authorization"] == (
        f"Bearer {secret_token}"
    )


@pytest.mark.parametrize(
    "invalid_track",
    [
        {**make_spotify_track(), "id": None},
        {**make_spotify_track(), "name": ""},
        {**make_spotify_track(), "artists": "invalid-artists"},
    ],
)
@patch("services.spotify_service.requests.get")
def test_service_rejects_malformed_spotify_track_data(
    mock_get,
    invalid_track,
):
    """Malformed Spotify data must fail instead of producing corrupted output."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = make_spotify_response(
        items=[invalid_track]
    )
    mock_get.return_value = mock_response

    service = SpotifyService("test-access-token")

    with pytest.raises(ValueError):
        service.get_normalized_user_top_tracks()