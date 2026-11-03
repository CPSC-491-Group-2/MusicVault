from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from models.artist import Artist, SongArtist
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
    overwritten with the latest values, including missing ones. Each song's
    artists are stored as shared Artist rows, matched on Spotify artist ID,
    and its credits are replaced with the track's current artist list.

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
    # Artists are looked up first: those queries autoflush the session, and a
    # new song must not be flushed before its required fields are set.
    artists = track.get("artists") or []
    credited = _upsert_artists(db, artists)

    song = db.scalar(select(Song).where(Song.spotify_track_id == track["spotify_id"]))
    if song is None:
        song = Song(spotify_track_id=track["spotify_id"])
        db.add(song)

    album = track.get("album") or {}
    popularity = track.get("popularity")

    song.title = track["title"]
    # artist_name is the display string; artist_credits holds the artists.
    song.artist_name = ", ".join(a["name"] for a in artists if a.get("name"))
    song.album_name = album.get("name")
    song.album_image_url = album.get("image_url")
    song.isrc = track.get("isrc")
    song.duration_ms = track.get("duration_ms")
    song.explicit = track.get("explicit")
    song.popularity = popularity
    song.popularity_source = "spotify" if popularity is not None else None
    song.spotify_url = track.get("spotify_url")
    _set_artist_credits(db, song, credited)
    return song


def _upsert_artists(db: Session, artists: list[dict]) -> list[Artist]:
    """The track's artists as Artist rows, in credit order.

    Artists are matched on their Spotify artist ID and their name is updated
    to the latest value. Genres are left alone; they come from a separate
    lookup. Artists without an ID or name, and repeats, are skipped.
    """
    credited, seen = [], set()
    for entry in artists:
        spotify_artist_id, name = entry.get("spotify_id"), entry.get("name")
        if not spotify_artist_id or not name or spotify_artist_id in seen:
            continue
        seen.add(spotify_artist_id)

        artist = db.scalar(
            select(Artist).where(Artist.spotify_artist_id == spotify_artist_id)
        )
        if artist is None:
            artist = Artist(spotify_artist_id=spotify_artist_id, name=name)
            db.add(artist)
        artist.name = name
        credited.append(artist)
    return credited


def _set_artist_credits(db: Session, song: Song, artists: list[Artist]) -> None:
    if [credit.artist for credit in song.artist_credits] == artists:
        return
    # Old credits are deleted before the new ones are inserted, so a
    # reordered list can't collide on (song_id, position) or the primary key.
    song.artist_credits.clear()
    db.flush()
    song.artist_credits.extend(
        SongArtist(artist=artist, position=position)
        for position, artist in enumerate(artists, start=1)
    )
