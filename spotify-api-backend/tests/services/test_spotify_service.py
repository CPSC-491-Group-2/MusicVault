import pytest
from unittest.mock import patch, Mock

from services.spotify_service import SpotifyService

FAKE_TOKEN = "fake-access-token"


def test_get_user_top_track_rejects_limit_above_50():
    service = SpotifyService(FAKE_TOKEN)

    with pytest.raises(ValueError, match="limit must be between 1 and 50"):
        service.get_user_top_track(limit=51)


def test_get_user_top_track_rejects_limit_below_1():
    service = SpotifyService(FAKE_TOKEN)

    with pytest.raises(ValueError, match="limit must be between 1 and 50"):
        service.get_user_top_track(limit=0)


def test_get_user_top_track_rejects_invalid_time_range():
    service = SpotifyService(FAKE_TOKEN)

    with pytest.raises(ValueError, match="time range invalid"):
        service.get_user_top_track(time_range="all_time")


def test_get_user_top_track_rejects_negative_offset():
    service = SpotifyService(FAKE_TOKEN)

    with pytest.raises(ValueError, match="offset must be greater than 0"):
        service.get_user_top_track(offset=-1)


@patch("services.spotify_service.requests.get")
def test_get_user_top_track_success(mock_get):
    # Create a fake Spotify HTTP response
    mock_response = Mock()

    mock_response.status_code = 200

    mock_response.json.return_value = {
        "items": [
            {
                "id": "track123",
                "name": "Example Song",
                "artists": [
                    {
                        "id": "artist123",
                        "name": "Example Artist"
                    }
                ]
            }
        ],
        "limit": 20,
        "offset": 0
    }

    # Tell requests.get() to return our fake response
    mock_get.return_value = mock_response

    service = SpotifyService(FAKE_TOKEN)

    result = service.get_user_top_track(
        limit=20,
        time_range="medium_term",
        offset=0
    )

    # Verify returned data
    assert result["items"][0]["id"] == "track123"
    assert result["items"][0]["name"] == "Example Song"
    assert result["items"][0]["artists"][0]["name"] == "Example Artist"

    # Verify Spotify was called correctly
    mock_get.assert_called_once_with(
        "https://api.spotify.com/v1/me/top/tracks",
        headers={
            "Authorization": f"Bearer {FAKE_TOKEN}"
        },
        params={
            "limit": 20,
            "time_range": "medium_term",
            "offset": 0
        },
        timeout=10
    )