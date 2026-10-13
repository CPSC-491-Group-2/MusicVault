from spotify.parsers import parse_track


def test_parse_track():
    spotify_response = {
        "id": "track123",
        "name": "Lose Yourself",
        "duration_ms": 326000,
        "explicit": True,
        "external_urls": {
            "spotify": "https://open.spotify.com/track/track123"
        },
        "artists": [
            {
                "id": "artist123",
                "name": "Eminem"
            }
        ],
        "album": {
            "id": "album123",
            "name": "8 Mile",
            "release_date": "2002-10-29",
            "images": [
                {
                    "url": "https://example.com/album.jpg"
                }
            ]
        }
    }

    track = parse_track(spotify_response)

    assert track.spotify_id == "track123"
    assert track.name == "Lose Yourself"

    assert track.artists == ["Eminem"]
    assert track.artist_ids == ["artist123"]

    assert track.album_name == "8 Mile"
    assert track.release_date == "2002-10-29"

    assert track.duration_ms == 326000
    assert track.explicit is True

    assert track.spotify_url == (
        "https://open.spotify.com/track/track123"
    )

    assert track.image_url == (
        "https://example.com/album.jpg"
    )