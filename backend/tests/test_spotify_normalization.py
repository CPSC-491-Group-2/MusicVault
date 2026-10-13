"""Unit tests for Spotify metadata normalization."""

import pytest

from spotify.parsers import normalize_top_tracks, normalize_track


def test_normalize_valid_spotify_track():
    """A Spotify track should map to MusicVault's internal schema."""

    spotify_track = {
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
            "images": [
                {
                    "url": "https://example.com/album.jpg",
                }
            ],
        },
        "duration_ms": 215000,
        "popularity": 75,
        "explicit": False,
        "external_urls": {
            "spotify": "https://open.spotify.com/track/track123",
        },
    }

    normalized = normalize_track(spotify_track)

    assert normalized == {
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
        "duration_ms": 215000,
        "popularity": 75,
        "explicit": False,
        "spotify_url": "https://open.spotify.com/track/track123",
    }


def test_normalize_track_with_multiple_artists():
    """All contributing artists should be preserved in order."""

    spotify_track = {
        "id": "track456",
        "name": "Collaboration Song",
        "artists": [
            {"id": "artist1", "name": "First Artist"},
            {"id": "artist2", "name": "Second Artist"},
            {"id": "artist3", "name": "Third Artist"},
        ],
        "album": {
            "id": "album456",
            "name": "Collaboration Album",
            "images": [],
        },
    }

    normalized = normalize_track(spotify_track)

    assert normalized["spotify_id"] == "track456"
    assert normalized["title"] == "Collaboration Song"

    assert normalized["artists"] == [
        {"spotify_id": "artist1", "name": "First Artist"},
        {"spotify_id": "artist2", "name": "Second Artist"},
        {"spotify_id": "artist3", "name": "Third Artist"},
    ]

    assert normalized["album"]["image_url"] is None


def test_normalize_track_with_missing_optional_fields():
    """Missing optional Spotify metadata should use safe defaults."""

    spotify_track = {
        "id": "track789",
        "name": "Minimal Song",
    }

    normalized = normalize_track(spotify_track)

    assert normalized == {
        "spotify_id": "track789",
        "title": "Minimal Song",
        "artists": [],
        "album": {
            "spotify_id": None,
            "name": None,
            "image_url": None,
        },
        "duration_ms": None,
        "popularity": None,
        "explicit": False,
        "spotify_url": None,
    }


@pytest.mark.parametrize(
    "track, expected_error",
    [
        (None, "Spotify track must be an object"),
        ([], "Spotify track must be an object"),
        ({}, "Spotify track is missing an ID or title"),
        (
            {"id": "track123"},
            "Spotify track is missing an ID or title",
        ),
        (
            {"name": "Example Song"},
            "Spotify track is missing an ID or title",
        ),
        (
            {
                "id": "track123",
                "name": "Example Song",
                "album": "Not an album object",
            },
            "Spotify album must be an object",
        ),
        (
            {
                "id": "track123",
                "name": "Example Song",
                "artists": "Not an artist list",
            },
            "Spotify artists must be a list",
        ),
        (
            {
                "id": "track123",
                "name": "Example Song",
                "artists": [None],
            },
            "Spotify artist must be an object",
        ),
        (
            {
                "id": "track123",
                "name": "Example Song",
                "artists": [{"id": "artist123"}],
            },
            "Spotify artist is missing an ID or name",
        ),
    ],
)
def test_normalize_track_rejects_invalid_data(track, expected_error):
    """Malformed Spotify track data should raise ValueError."""

    with pytest.raises(ValueError, match=expected_error):
        normalize_track(track)


def test_normalize_top_tracks_with_pagination():
    """Normalize tracks and preserve pagination metadata."""

    spotify_response = {
        "items": [
            {
                "id": "track123",
                "name": "First Song",
                "artists": [{"id": "artist123", "name": "First Artist"}],
                "album": {
                    "id": "album123",
                    "name": "First Album",
                },
            },
            {
                "id": "track456",
                "name": "Second Song",
                "artists": [{"id": "artist456", "name": "Second Artist"}],
            },
        ],
        "total": 40,
        "limit": 2,
        "offset": 10,
        "next": "https://api.spotify.com/v1/me/top/tracks?offset=12",
        "previous": "https://api.spotify.com/v1/me/top/tracks?offset=8",
    }

    normalized = normalize_top_tracks(spotify_response)

    assert len(normalized["items"]) == 2
    assert normalized["items"][0]["spotify_id"] == "track123"
    assert normalized["items"][0]["title"] == "First Song"
    assert normalized["items"][1]["spotify_id"] == "track456"
    assert normalized["items"][1]["title"] == "Second Song"

    assert normalized["total"] == 40
    assert normalized["limit"] == 2
    assert normalized["offset"] == 10
    assert normalized["next"] == spotify_response["next"]
    assert normalized["previous"] == spotify_response["previous"]


def test_normalize_top_tracks_with_missing_pagination():
    """Missing pagination fields should use documented defaults."""

    spotify_response = {
        "items": [
            {
                "id": "track789",
                "name": "Minimal Song",
            }
        ]
    }

    normalized = normalize_top_tracks(spotify_response)

    assert normalized["items"][0]["spotify_id"] == "track789"
    assert normalized["total"] == 1
    assert normalized["limit"] == 1
    assert normalized["offset"] == 0
    assert normalized["next"] is None
    assert normalized["previous"] is None


@pytest.mark.parametrize(
    "response, expected_error",
    [
        (None, "Spotify response must be an object"),
        ([], "Spotify response must be an object"),
        (
            {"items": "invalid"},
            "Spotify response items must be a list",
        ),
        (
            {"items": [None]},
            "Spotify track must be an object",
        ),
        (
            {"items": [{"name": "Missing ID"}]},
            "Spotify track is missing an ID or title",
        ),
    ],
)
def test_normalize_top_tracks_rejects_invalid_data(response, expected_error):
    """Reject malformed Spotify top-tracks responses."""

    with pytest.raises(ValueError, match=expected_error):
        normalize_top_tracks(response)
