"""Integration tests for the recommendation candidate queries.

The fixed recommendation dataset is saved to a real database, read back with
get_recommendation_inputs, and ranked. The result has to match the same
snapshot as the in-memory regression tests, proving the database hands the
ranker exactly the data the fixtures describe.
"""

from __future__ import annotations

import json
import uuid
from contextlib import contextmanager

import pytest
from sqlalchemy import event, func, select

from app.services.similarity import rank_candidates, track_features_from_song
from db.queries.preferences import set_preference
from db.queries.recommendations import get_recommendation_inputs
from db.session import SessionLocal, engine
from models.artist import Artist, SongArtist
from models.song import Song
from models.user import User
from models.user_top_song import UserTopSong
from recommendation_fixtures import (
    DATASET,
    KEY_BY_TRACK_ID,
    PROFILES,
    SNAPSHOT_FILE,
    build_songs,
    load_into_database,
    snapshot,
    stable_id,
)

pytestmark = pytest.mark.recommendation


@pytest.fixture
def users(clean_database):
    with SessionLocal() as db:
        return load_into_database(db)


def song_id(key):
    return stable_id("song", key)


def keys(songs):
    return [KEY_BY_TRACK_ID[str(song.id)] for song in songs]


def inputs_for(user_id, time_range="medium_term"):
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, user_id, time_range)
        return (
            [track_features_from_song(s) for s in inputs.seeds],
            [track_features_from_song(s) for s in inputs.candidates],
        )


@contextmanager
def count_queries():
    statements = []

    def record(conn, cursor, statement, *args):
        statements.append(statement)

    event.listen(engine, "before_cursor_execute", record)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", record)


# --- the controlled dataset -------------------------------------------------


def test_dataset_is_stored_completely(users):
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(Song)) == len(
            DATASET["songs"]
        )
        assert db.scalar(select(func.count()).select_from(Artist)) == len(
            DATASET["artists"]
        )
        assert db.scalar(select(func.count()).select_from(SongArtist)) == sum(
            len(s["artists"]) for s in DATASET["songs"].values()
        )


@pytest.mark.parametrize("profile", sorted(PROFILES))
def test_seeds_are_the_profiles_top_songs_in_rank_order(users, profile):
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, users[profile])
        assert keys(inputs.seeds) == PROFILES[profile]


@pytest.mark.parametrize("profile", sorted(PROFILES))
def test_candidates_are_every_other_song_in_id_order(users, profile):
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, users[profile])
        expected = sorted(set(DATASET["songs"]) - set(PROFILES[profile]))
        assert sorted(keys(inputs.candidates)) == expected
        assert [s.id for s in inputs.candidates] == sorted(
            s.id for s in inputs.candidates
        )


def test_features_from_the_database_match_the_fixtures(users):
    """The database gives the ranker the same features as the in-memory rows."""
    expected = {
        str(song.id): track_features_from_song(song) for song in build_songs().values()
    }
    seeds, candidates = inputs_for(users["indie_listener"])
    for features in seeds + candidates:
        assert features == expected[features.track_id]


@pytest.mark.parametrize("profile", sorted(PROFILES))
def test_rankings_from_the_database_match_the_snapshot(users, profile):
    seeds, candidates = inputs_for(users[profile])
    expected = json.loads(SNAPSHOT_FILE.read_text())["profiles"][profile]
    assert snapshot(rank_candidates(seeds, candidates)) == expected


def test_inputs_are_repeatable(users):
    assert inputs_for(users["mixed_listener"]) == inputs_for(users["mixed_listener"])


# --- preferences ------------------------------------------------------------


def test_liked_and_saved_songs_become_seeds_after_top_songs(users):
    user = users["indie_listener"]
    with SessionLocal() as db:
        set_preference(db, user, song_id("jazz-1"), "saved")
        set_preference(db, user, song_id("hiphop-2"), "liked", rating=5)
        set_preference(db, user, song_id("electronic-2"), "liked", rating=2)
        # Already a top song: stays in its top-song position, once.
        set_preference(db, user, song_id("indie-2"), "liked", rating=5)

        inputs = get_recommendation_inputs(db, user)

    # Top songs first, then preferences by rating (unrated last).
    assert keys(inputs.seeds) == [
        "indie-1",
        "indie-2",
        "indie-3",
        "hiphop-2",
        "electronic-2",
        "jazz-1",
    ]
    assert not set(keys(inputs.seeds)) & set(keys(inputs.candidates))


@pytest.mark.parametrize("preference_type", ["disliked", "skipped"])
def test_disliked_and_skipped_songs_are_left_out(users, preference_type):
    user = users["indie_listener"]
    with SessionLocal() as db:
        set_preference(db, user, song_id("indie-4"), preference_type)
        set_preference(db, user, song_id("indie-2"), preference_type)  # a top song
        inputs = get_recommendation_inputs(db, user)

    assert keys(inputs.seeds) == ["indie-1", "indie-3"]
    assert "indie-4" not in keys(inputs.candidates)
    assert "indie-2" not in keys(inputs.candidates)


def test_neutral_preferences_change_nothing(users):
    user = users["indie_listener"]
    before = inputs_for(user)
    with SessionLocal() as db:
        set_preference(db, user, song_id("indie-4"), "neutral")

    assert inputs_for(user) == before


def test_one_users_preferences_do_not_affect_another(users):
    with SessionLocal() as db:
        set_preference(db, users["indie_listener"], song_id("indie-4"), "disliked")
        set_preference(db, users["indie_listener"], song_id("jazz-1"), "liked")
        inputs = get_recommendation_inputs(db, users["hiphop_listener"])

    assert keys(inputs.seeds) == PROFILES["hiphop_listener"]
    assert "indie-4" in keys(inputs.candidates)
    assert "jazz-1" in keys(inputs.candidates)


# --- empty and missing data -------------------------------------------------


def test_user_with_no_top_songs_or_preferences_has_no_seeds(users):
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, users["empty_listener"])

    assert inputs.seeds == []
    assert len(inputs.candidates) == len(DATASET["songs"])


def test_other_time_ranges_have_no_seeds(users):
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, users["indie_listener"], "short_term")
    assert inputs.seeds == []


def test_unknown_user_gets_every_song_as_a_candidate(users):
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, uuid.uuid4())
    assert inputs.seeds == []
    assert len(inputs.candidates) == len(DATASET["songs"])


def test_empty_catalog_returns_nothing(make_db_user):
    user = make_db_user("Nobody")
    with SessionLocal() as db:
        inputs = get_recommendation_inputs(db, user)
    assert (inputs.seeds, inputs.candidates) == ([], [])


def test_invalid_time_range_is_rejected(users):
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="time_range must be one of"):
            get_recommendation_inputs(db, users["indie_listener"], "all_time")


def test_songs_with_only_required_fields_are_handled(clean_database):
    with SessionLocal() as db:
        user = User(display_name="Sparse")
        bare = Song(title="Bare", artist_name="")
        db.add_all([user, bare])
        db.flush()
        db.add(
            UserTopSong(
                user_id=user.id, song_id=bare.id, time_range="long_term", rank=1
            )
        )
        db.add(Song(title="Also bare", artist_name=""))
        db.commit()
        user_id = user.id

    seeds, candidates = inputs_for(user_id, "long_term")
    [result] = rank_candidates(seeds, candidates)
    assert seeds[0].artists == frozenset()
    assert seeds[0].audio == {}
    assert seeds[0].popularity is None
    assert (result.score, result.reason) == (0.0, None)


def test_malformed_stored_metadata_is_ignored_not_fatal(clean_database):
    with SessionLocal() as db:
        artist = Artist(name="Odd", genres=["", 7, None, " Pop "])
        song = Song(
            title="Odd",
            artist_name="Odd",
            audio_features={"energy": "high", "tempo": None, "valence": True},
        )
        song.artist_credits = [SongArtist(artist=artist, position=1)]
        db.add(song)
        db.commit()
        user = User(display_name="Odd")
        db.add(user)
        db.commit()
        user_id = user.id

    _, [candidate] = inputs_for(user_id)
    assert candidate.genres == frozenset({"pop"})
    assert candidate.audio == {}


# --- query performance --------------------------------------------------------


def add_catalog(size):
    """Add `size` songs, each crediting two of `size // 4 + 1` artists."""
    with SessionLocal() as db:
        artists = [
            Artist(name=f"Artist {n}", genres=["pop", f"genre {n % 7}"])
            for n in range(size // 4 + 1)
        ]
        db.add_all(artists)
        for n in range(size):
            song = Song(
                title=f"Song {n}",
                artist_name="",
                audio_features={"energy": n % 10 / 10, "valence": 0.5, "tempo": 120},
            )
            song.artist_credits = [
                SongArtist(artist=artists[n % len(artists)], position=1),
                SongArtist(artist=artists[(n + 1) % len(artists)], position=2),
            ]
            db.add(song)
        db.commit()


def queries_for(user_id):
    with SessionLocal() as db, count_queries() as statements:
        inputs = get_recommendation_inputs(db, user_id)
        for song in [*inputs.seeds, *inputs.candidates]:
            track_features_from_song(song)
    return len(statements)


def test_query_count_does_not_grow_with_the_catalog(users):
    user = users["mixed_listener"]
    with SessionLocal() as db:
        set_preference(db, user, song_id("jazz-1"), "liked")

    small = queries_for(user)
    add_catalog(400)
    large = queries_for(user)

    # A fixed number of queries (songs, then their credits, then artists, for
    # each of top songs, preferences and candidates), not one per song.
    assert large == small
    assert small <= 9
