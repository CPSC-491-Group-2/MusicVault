from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from models.song import Song
from models.user_top_song import TIME_RANGES, UserTopSong


def save_top_songs(
    db: Session, user_id: uuid.UUID, time_range: str, tracks: list[dict]
) -> list[UserTopSong]:
    """Replace a user's top songs for one time range and return the saved list.

    `tracks` are normalized Spotify tracks (see
    spotify-api-backend/NORMALIZATION.md), best first; rank is the position
    in the list, starting at 1. Songs are matched on their Spotify track ID,
    so a song in many users' lists is stored once, and its details are
    overwritten with the latest values, including missing ones.

    An empty list clears the user's songs for that range. A repeated track
    keeps its first (highest) rank. Invalid input raises ValueError before
    anything is written; any database error rolls the whole save back.
    """
    _check_time_range(time_range)
    tracks = _unique_tracks(tracks)

    try:
        db.execute(
            delete(UserTopSong).where(
                UserTopSong.user_id == user_id, UserTopSong.time_range == time_range
            )
        )
        for rank, track in enumerate(tracks, start=1):
            db.add(
                UserTopSong(
                    user_id=user_id,
                    song=_upsert_song(db, track),
                    time_range=time_range,
                    rank=rank,
                )
            )
        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_top_songs(db, user_id, time_range)


def get_top_songs(
    db: Session, user_id: uuid.UUID, time_range: str
) -> list[UserTopSong]:
    """A user's saved top songs for one time range, in rank order.

    Returns an empty list if nothing has been saved for that range.
    """
    _check_time_range(time_range)
    return list(
        db.scalars(
            select(UserTopSong)
            .options(joinedload(UserTopSong.song))
            .where(UserTopSong.user_id == user_id, UserTopSong.time_range == time_range)
            .order_by(UserTopSong.rank)
        )
    )


def _check_time_range(time_range: str) -> None:
    if time_range not in TIME_RANGES:
        raise ValueError(
            f"time_range must be one of {', '.join(TIME_RANGES)} (got {time_range!r})"
        )


def _unique_tracks(tracks: list[dict]) -> list[dict]:
    """Validate the required fields and drop repeated tracks, keeping order."""
    if tracks is None:
        raise ValueError("tracks must be a list (use [] to clear)")

    unique, seen = [], set()
    for position, track in enumerate(tracks, start=1):
        if not isinstance(track, dict):
            raise ValueError(f"track {position} is not a dictionary")
        for field in ("spotify_id", "title"):
            value = track.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"track {position} is missing {field}")
        if track["spotify_id"] not in seen:
            seen.add(track["spotify_id"])
            unique.append(track)
    return unique


def _upsert_song(db: Session, track: dict) -> Song:
    song = db.scalar(select(Song).where(Song.spotify_track_id == track["spotify_id"]))
    if song is None:
        song = Song(spotify_track_id=track["spotify_id"])
        db.add(song)

    album = track.get("album") or {}
    artists = track.get("artists") or []
    popularity = track.get("popularity")

    song.title = track["title"]
    # songs has one artist column; multiple artists are kept in order.
    song.artist_name = ", ".join(a["name"] for a in artists if a.get("name"))
    song.album_name = album.get("name")
    song.album_image_url = album.get("image_url")
    song.duration_ms = track.get("duration_ms")
    song.explicit = track.get("explicit")
    song.popularity = popularity
    song.popularity_source = "spotify" if popularity is not None else None
    song.spotify_url = track.get("spotify_url")
    return song
