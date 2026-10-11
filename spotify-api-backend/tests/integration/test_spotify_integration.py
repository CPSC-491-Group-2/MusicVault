import os
import pytest

from services.spotify_service import SpotifyService


SPOTIFY_ACCESS_TOKEN = os.getenv("SPOTIFY_ACCESS_TOKEN")


@pytest.mark.integration
@pytest.mark.skipif(
    not SPOTIFY_ACCESS_TOKEN,
    reason="SPOTIFY_ACCESS_TOKEN is not set"
)
def test_live_search_track_and_retrieve_details():
    service = SpotifyService(SPOTIFY_ACCESS_TOKEN)

    # 1. Search for a real track
    search_result = service.search_track(
        query='track:"Lose Yourself" artist:"Eminem"',
        limit=10
    )

    assert "tracks" in search_result
    assert "items" in search_result["tracks"]
    assert len(search_result["tracks"]["items"]) > 0

    # 2. Find the expected track
    matching_track = None

    for track in search_result["tracks"]["items"]:
        track_name = track["name"]
        artist_names = [
            artist["name"]
            for artist in track["artists"]
        ]

        if (
            track_name.lower() == "lose yourself"
            and "Eminem" in artist_names
        ):
            matching_track = track
            break

    assert matching_track is not None

    # 3. Retrieve the track using its real Spotify ID
    track_id = matching_track["id"]

    track_result = service.get_track(track_id)

    assert track_result["id"] == track_id
    assert track_result["name"].lower() == "lose yourself"
    assert any(
        artist["name"] == "Eminem"
        for artist in track_result["artists"]
    )

    # 4. Retrieve the artist using the artist ID
    artist_id = track_result["artists"][0]["id"]

    artist_result = service.get_artist(artist_id)

    assert artist_result["id"] == artist_id
    assert artist_result["name"] == "Eminem"