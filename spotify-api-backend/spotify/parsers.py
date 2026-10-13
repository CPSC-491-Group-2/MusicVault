"""Normalize Spotify track data into the MusicVault API format."""


def normalize_track(track: dict) -> dict:
    """Convert a Spotify track into a consistent MusicVault track."""

    if not isinstance(track, dict):
        raise ValueError("Spotify track must be an object")

    if not track.get("id") or not track.get("name"):
        raise ValueError("Spotify track is missing an ID or title")

    album = track.get("album") or {}
    artists = track.get("artists") or []
    external_urls = track.get("external_urls") or {}

    if not isinstance(album, dict):
        raise ValueError("Spotify album must be an object")
    if not isinstance(artists, list):
        raise ValueError("Spotify artists must be a list")

    normalized_artists = []

    for artist in artists:
        if not isinstance(artist, dict):
            raise ValueError("Spotify artist must be an object")

        if not artist.get("id") or not artist.get("name"):
            raise ValueError("Spotify artist is missing an ID or name")

        normalized_artists.append(
            {
                "spotify_id": artist["id"],
                "name": artist["name"],
            }
        )

    images = album.get("images") or []
    image_url = None

    if isinstance(images, list):
        for image in images:
            if isinstance(image, dict) and image.get("url"):
                image_url = image["url"]
                break

    if not isinstance(external_urls, dict):
        external_urls = {}

    return {
        "spotify_id": track["id"],
        "title": track["name"],
        "artists": normalized_artists,
        "album": {
            "spotify_id": album.get("id"),
            "name": album.get("name"),
            "image_url": image_url,
        },
        "duration_ms": track.get("duration_ms"),
        "popularity": track.get("popularity"),
        "explicit": (
            track.get("explicit") if track.get("explicit") is not None else False
        ),
        "spotify_url": external_urls.get("spotify"),
    }


def normalize_top_tracks(response: dict) -> dict:
    """Normalize a Spotify top-tracks response with pagination."""

    if not isinstance(response, dict):
        raise ValueError("Spotify response must be an object")

    tracks = response.get("items") or []

    if not isinstance(tracks, list):
        raise ValueError("Spotify response items must be a list")

    return {
        "items": [normalize_track(track) for track in tracks],
        "total": response.get("total", len(tracks)),
        "limit": response.get("limit", len(tracks)),
        "offset": response.get("offset", 0),
        "next": response.get("next"),
        "previous": response.get("previous"),
    }
