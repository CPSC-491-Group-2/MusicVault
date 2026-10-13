"""Integration tests for saving and reading a user's top songs.

Saves are really committed (through clean_database) and read back in a
fresh session, so they prove the data reached the database.
"""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from db.queries.top_songs import get_top_songs, save_top_songs
from db.queries.user import delete_user
from db.session import SessionLocal
from models.song import Song
from models.user_top_song import UserTopSong


def make_track(n, **overrides):
    """A normalized track, shaped like GET /api/v1/spotify/top-tracks items."""
    track = {
        "spotify_id": f"track-{n}",
        "title": f"Song {n}",
        "artists": [
            {"spotify_id": f"artist-{n}", "name": f"Artist {n}"},
            {"spotify_id": "artist-feat", "name": "Featured"},
        ],
        "album": {
            "spotify_id": f"album-{n}",
            "name": f"Album {n}",
            "image_url": f"https://i.scdn.co/image/{n}",
        },
        "duration_ms": 180_000 + n,
        "popularity": 40 + n,
        "explicit": True,
        "spotify_url": f"https://open.spotify.com/track/track-{n}",
    }
    track.update(overrides)
    return track


def saved_titles(user_id, time_range="medium_term"):
    with SessionLocal() as db:
        return [entry.song.title for entry in get_top_songs(db, user_id, time_range)]


def count(model):
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(model))


@pytest.fixture
def user_id(make_db_user):
    return make_db_user("Top Songs Listener")


# --- storing and retrieving -------------------------------------------------


def test_save_stores_songs_and_ranked_entries(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [make_track(1), make_track(2)])

    assert count(Song) == 2
    assert count(UserTopSong) == 2


def test_get_returns_songs_in_rank_order(user_id):
    tracks = [make_track(3), make_track(1), make_track(2)]
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", tracks)

    with SessionLocal() as db:
        entries = get_top_songs(db, user_id, "medium_term")

    assert [e.rank for e in entries] == [1, 2, 3]
    assert [e.song.spotify_track_id for e in entries] == [
        "track-3",
        "track-1",
        "track-2",
    ]


def test_save_returns_the_saved_list(user_id):
    with SessionLocal() as db:
        saved = save_top_songs(db, user_id, "short_term", [make_track(1)])

        assert [(e.rank, e.song.title) for e in saved] == [(1, "Song 1")]


def test_fields_survive_a_round_trip(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "long_term", [make_track(7)])

    with SessionLocal() as db:
        [entry] = get_top_songs(db, user_id, "long_term")
        song = entry.song

    assert entry.user_id == user_id
    assert entry.time_range == "long_term"
    assert entry.rank == 1
    assert entry.fetched_at is not None
    assert song.spotify_track_id == "track-7"
    assert song.title == "Song 7"
    assert song.artist_name == "Artist 7, Featured"
    assert song.album_name == "Album 7"
    assert song.album_image_url == "https://i.scdn.co/image/7"
    assert song.duration_ms == 180_007
    assert song.popularity == 47
    assert song.popularity_source == "spotify"
    assert song.explicit is True
    assert song.spotify_url == "https://open.spotify.com/track/track-7"


def test_text_is_stored_exactly(user_id):
    track = make_track(
        1,
        title="Señorita (feat. Ñandú) — 日本語 'quoted' \"double\"",
        artists=[{"spotify_id": "a", "name": "Beyoncé"}],
    )
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [track])

    with SessionLocal() as db:
        [entry] = get_top_songs(db, user_id, "medium_term")

    assert entry.song.title == track["title"]
    assert entry.song.artist_name == "Beyoncé"


# --- refreshing ---------------------------------------------------------------


def test_save_replaces_the_previous_list_for_that_range(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [make_track(1), make_track(2)])
        save_top_songs(db, user_id, "medium_term", [make_track(3)])

    assert saved_titles(user_id) == ["Song 3"]
    assert count(UserTopSong) == 1


def test_time_ranges_are_kept_separately(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "short_term", [make_track(1)])
        save_top_songs(db, user_id, "long_term", [make_track(2), make_track(3)])
        save_top_songs(db, user_id, "short_term", [make_track(4)])

    assert saved_titles(user_id, "short_term") == ["Song 4"]
    assert saved_titles(user_id, "long_term") == ["Song 2", "Song 3"]
    assert saved_titles(user_id, "medium_term") == []


def test_users_lists_do_not_affect_each_other(make_db_user):
    first, second = make_db_user("First"), make_db_user("Second")
    with SessionLocal() as db:
        save_top_songs(db, first, "medium_term", [make_track(1)])
        save_top_songs(db, second, "medium_term", [make_track(2)])
        save_top_songs(db, first, "medium_term", [])

    assert saved_titles(first) == []
    assert saved_titles(second) == ["Song 2"]


def test_shared_song_is_stored_once_with_latest_details(make_db_user):
    first, second = make_db_user("First"), make_db_user("Second")
    with SessionLocal() as db:
        save_top_songs(db, first, "medium_term", [make_track(1, popularity=10)])
        save_top_songs(db, second, "medium_term", [make_track(1, popularity=90)])

    assert count(Song) == 1
    with SessionLocal() as db:
        [entry] = get_top_songs(db, first, "medium_term")
        assert entry.song.popularity == 90


# --- missing and empty data ---------------------------------------------------


def test_nothing_saved_returns_empty_list(user_id):
    assert saved_titles(user_id) == []


def test_empty_list_clears_the_range(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [make_track(1)])
        assert save_top_songs(db, user_id, "medium_term", []) == []

    assert saved_titles(user_id) == []
    # The song itself stays; only the user's list is cleared.
    assert count(Song) == 1


def test_missing_optional_fields_are_stored_as_null(user_id):
    track = {"spotify_id": "bare-track", "title": "Bare Song"}
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [track])

    with SessionLocal() as db:
        [entry] = get_top_songs(db, user_id, "medium_term")
        song = entry.song

    assert song.artist_name == ""
    assert song.album_name is None
    assert song.album_image_url is None
    assert song.duration_ms is None
    assert song.popularity is None
    assert song.popularity_source is None
    assert song.explicit is None
    assert song.spotify_url is None


def test_null_album_and_empty_artists_are_accepted(user_id):
    track = make_track(1, album=None, artists=[], popularity=None)
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [track])

    with SessionLocal() as db:
        [entry] = get_top_songs(db, user_id, "medium_term")

    assert entry.song.album_name is None
    assert entry.song.artist_name == ""
    assert entry.song.popularity_source is None


def test_refresh_overwrites_details_that_went_missing(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [make_track(1)])
        save_top_songs(
            db, user_id, "medium_term", [make_track(1, popularity=None, album=None)]
        )

    with SessionLocal() as db:
        [entry] = get_top_songs(db, user_id, "medium_term")

    assert entry.song.popularity is None
    assert entry.song.album_name is None


def test_repeated_track_keeps_its_first_rank(user_id):
    tracks = [make_track(1), make_track(2), make_track(1)]
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", tracks)

    with SessionLocal() as db:
        entries = get_top_songs(db, user_id, "medium_term")

    assert [(e.rank, e.song.title) for e in entries] == [(1, "Song 1"), (2, "Song 2")]


@pytest.mark.parametrize(
    "bad_track, message",
    [
        ({"title": "No ID"}, "missing spotify_id"),
        ({"spotify_id": "", "title": "Blank ID"}, "missing spotify_id"),
        ({"spotify_id": "no-title"}, "missing title"),
        ({"spotify_id": "blank-title", "title": "   "}, "missing title"),
        ({"spotify_id": 123, "title": "Numeric ID"}, "missing spotify_id"),
        ("not a track", "not a dictionary"),
    ],
)
def test_invalid_track_is_rejected_without_changing_anything(
    user_id, bad_track, message
):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [make_track(1)])

        with pytest.raises(ValueError, match=message):
            save_top_songs(db, user_id, "medium_term", [make_track(2), bad_track])

    assert saved_titles(user_id) == ["Song 1"]
    assert count(Song) == 1


def test_none_instead_of_a_list_is_rejected(user_id):
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="must be a list"):
            save_top_songs(db, user_id, "medium_term", None)


@pytest.mark.parametrize("time_range", ["all_time", "", "SHORT_TERM", None])
def test_invalid_time_range_is_rejected(user_id, time_range):
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="time_range must be one of"):
            save_top_songs(db, user_id, time_range, [make_track(1)])
        with pytest.raises(ValueError, match="time_range must be one of"):
            get_top_songs(db, user_id, time_range)

    assert count(Song) == 0


# --- database integrity ---------------------------------------------------------


def test_unknown_user_rolls_back_the_whole_save(clean_database):
    with SessionLocal() as db:
        with pytest.raises(IntegrityError):
            save_top_songs(db, uuid.uuid4(), "medium_term", [make_track(1)])

        # The session is still usable after the failed save.
        assert get_top_songs(db, uuid.uuid4(), "medium_term") == []

    assert count(Song) == 0
    assert count(UserTopSong) == 0


def test_deleting_a_user_removes_their_list_but_keeps_songs(user_id):
    with SessionLocal() as db:
        save_top_songs(db, user_id, "medium_term", [make_track(1)])
        delete_user(db, user_id)

    assert count(UserTopSong) == 0
    assert count(Song) == 1
