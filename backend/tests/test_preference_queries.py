"""Integration tests for user song preferences.

Writes are really committed (through clean_database) and read back in a
fresh session, so they prove what reached the database.
"""

from __future__ import annotations

import threading
import uuid

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from db.queries.preferences import (
    delete_preference,
    get_preference,
    get_preferences,
    save_preferences,
    set_preference,
)
from db.queries.user import delete_user
from db.session import SessionLocal
from models.song import Song
from models.user_preference import UserPreference


@pytest.fixture
def make_song(clean_database):
    def _make(title="Song", **fields):
        with SessionLocal() as db:
            song = Song(title=title, artist_name="Artist", **fields)
            db.add(song)
            db.commit()
            return song.id

    return _make


@pytest.fixture
def user_id(make_db_user):
    return make_db_user("Preference Listener")


def count_preferences():
    with SessionLocal() as db:
        return db.scalar(select(func.count()).select_from(UserPreference))


def stored(user_id):
    """A user's preferences as {song_id: (type, rating)}, read fresh."""
    with SessionLocal() as db:
        return {
            p.song_id: (p.preference_type, p.rating)
            for p in get_preferences(db, user_id)
        }


# --- creating and reading ---------------------------------------------------


def test_set_preference_stores_and_returns_it(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        saved = set_preference(db, user_id, song_id, "liked", rating=5)

        assert (saved.user_id, saved.song_id) == (user_id, song_id)
        assert (saved.preference_type, saved.rating) == ("liked", 5)
        assert saved.created_at is not None

    with SessionLocal() as db:
        found = get_preference(db, user_id, song_id)
        assert found.id == saved.id
        assert (found.preference_type, found.rating) == ("liked", 5)


def test_rating_is_optional(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, user_id, song_id, "saved")

    assert stored(user_id) == {song_id: ("saved", None)}


@pytest.mark.parametrize(
    "preference_type", ["liked", "disliked", "saved", "skipped", "neutral"]
)
def test_every_preference_type_can_be_stored(user_id, make_song, preference_type):
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, user_id, song_id, preference_type)

    assert stored(user_id) == {song_id: (preference_type, None)}


def test_missing_preference_returns_none(user_id, make_song):
    with SessionLocal() as db:
        assert get_preference(db, user_id, make_song()) is None
        assert get_preferences(db, user_id) == []


def test_preferences_can_be_filtered_by_type(user_id, make_song):
    liked, saved, skipped = make_song("A"), make_song("B"), make_song("C")
    with SessionLocal() as db:
        save_preferences(
            db,
            user_id,
            [
                {"song_id": liked, "preference_type": "liked"},
                {"song_id": saved, "preference_type": "saved"},
                {"song_id": skipped, "preference_type": "skipped"},
            ],
        )
        found = get_preferences(db, user_id, ("liked", "saved"))

    assert {p.song_id for p in found} == {liked, saved}


def test_filtering_by_an_unknown_type_is_rejected(user_id):
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="preference_type must be one of"):
            get_preferences(db, user_id, ("loved",))


def test_delete_preference(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, user_id, song_id, "liked")
        assert delete_preference(db, user_id, song_id) is True
        assert delete_preference(db, user_id, song_id) is False

    assert count_preferences() == 0


# --- the right user ---------------------------------------------------------


def test_preferences_stay_with_their_user(make_db_user, make_song):
    first, second = make_db_user("First"), make_db_user("Second")
    shared, only_first = make_song("Shared"), make_song("Only first")
    with SessionLocal() as db:
        set_preference(db, first, shared, "liked", rating=5)
        set_preference(db, second, shared, "disliked", rating=1)
        set_preference(db, first, only_first, "saved")

    assert stored(first) == {shared: ("liked", 5), only_first: ("saved", None)}
    assert stored(second) == {shared: ("disliked", 1)}


def test_changing_one_users_preference_leaves_others_alone(make_db_user, make_song):
    first, second = make_db_user("First"), make_db_user("Second")
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, first, song_id, "liked")
        set_preference(db, second, song_id, "liked")
        set_preference(db, first, song_id, "skipped")
        delete_preference(db, first, song_id)

    assert stored(first) == {}
    assert stored(second) == {song_id: ("liked", None)}


# --- duplicates and repeated writes -----------------------------------------


def test_setting_again_updates_the_same_row(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        first = set_preference(db, user_id, song_id, "liked", rating=3)
        second = set_preference(db, user_id, song_id, "disliked", rating=1)

    assert second.id == first.id
    assert count_preferences() == 1
    assert stored(user_id) == {song_id: ("disliked", 1)}


def test_updating_clears_a_rating_left_out(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, user_id, song_id, "liked", rating=4)
        set_preference(db, user_id, song_id, "liked")

    assert stored(user_id) == {song_id: ("liked", None)}


def test_updating_keeps_created_at_and_moves_updated_at(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        first = set_preference(db, user_id, song_id, "liked")
        created, updated = first.created_at, first.updated_at

    with SessionLocal() as db:
        second = set_preference(db, user_id, song_id, "saved")
        assert second.created_at == created
        assert second.updated_at > updated


def test_repeated_identical_writes_leave_one_row(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        for _ in range(10):
            set_preference(db, user_id, song_id, "liked", rating=5)

    assert count_preferences() == 1
    assert stored(user_id) == {song_id: ("liked", 5)}


def test_repeated_song_in_one_batch_keeps_the_last_entry(user_id, make_song):
    a, b = make_song("A"), make_song("B")
    with SessionLocal() as db:
        saved = save_preferences(
            db,
            user_id,
            [
                {"song_id": a, "preference_type": "liked", "rating": 5},
                {"song_id": b, "preference_type": "saved"},
                {"song_id": a, "preference_type": "skipped"},
            ],
        )

    assert [p.song_id for p in saved] == [b, a]
    assert count_preferences() == 2
    assert stored(user_id) == {a: ("skipped", None), b: ("saved", None)}


def test_duplicate_row_is_rejected_by_the_database(user_id, make_song):
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, user_id, song_id, "liked")
        # Bypasses the upsert, as code writing rows directly would.
        db.add(
            UserPreference(user_id=user_id, song_id=song_id, preference_type="saved")
        )
        with pytest.raises(IntegrityError):
            db.commit()

    assert stored(user_id) == {song_id: ("liked", None)}


# --- concurrent submissions -------------------------------------------------


def run_at_once(tasks):
    """Run each task in its own thread and session, released together."""
    barrier = threading.Barrier(len(tasks))
    errors = []

    def run(task):
        try:
            with SessionLocal() as db:
                barrier.wait()
                task(db)
        except Exception as exc:  # noqa: BLE001 - reported below
            errors.append(exc)

    threads = [threading.Thread(target=run, args=(task,)) for task in tasks]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert not errors, errors


def test_concurrent_submissions_for_one_song_leave_one_row(user_id, make_song):
    song_id = make_song()
    submitted = [("liked", 5), ("disliked", 1), ("saved", 4), ("skipped", None)] * 3
    run_at_once(
        [
            lambda db, t=t, r=r: set_preference(db, user_id, song_id, t, rating=r)
            for t, r in submitted
        ]
    )

    assert count_preferences() == 1
    # Whichever write landed last wins, and it is one complete submission.
    assert stored(user_id)[song_id] in submitted


def test_concurrent_submissions_for_different_songs_all_land(user_id, make_song):
    songs = [make_song(f"Song {n}") for n in range(8)]
    run_at_once(
        [lambda db, s=s: set_preference(db, user_id, s, "liked") for s in songs]
    )

    assert stored(user_id) == {s: ("liked", None) for s in songs}


def test_concurrent_users_on_the_same_song_each_keep_their_own(make_db_user, make_song):
    users = [make_db_user(f"User {n}") for n in range(6)]
    song_id = make_song()
    run_at_once(
        [lambda db, u=u: set_preference(db, u, song_id, "saved") for u in users]
    )

    assert count_preferences() == len(users)
    for user in users:
        assert stored(user) == {song_id: ("saved", None)}


# --- invalid input and relationships ----------------------------------------


@pytest.mark.parametrize(
    "entry, message",
    [
        ({"preference_type": "liked"}, "missing song_id"),
        ({"song_id": "not-a-uuid", "preference_type": "liked"}, "missing song_id"),
        ({"song_id": uuid.uuid4(), "preference_type": "loved"}, "preference_type"),
        ({"song_id": uuid.uuid4()}, "preference_type"),
        ({"song_id": uuid.uuid4(), "preference_type": "liked", "rating": 0}, "1-5"),
        ({"song_id": uuid.uuid4(), "preference_type": "liked", "rating": 6}, "1-5"),
        ({"song_id": uuid.uuid4(), "preference_type": "liked", "rating": 4.5}, "1-5"),
        ({"song_id": uuid.uuid4(), "preference_type": "liked", "rating": True}, "1-5"),
        ("liked", "not a dictionary"),
    ],
)
def test_invalid_preference_is_rejected_before_writing(
    user_id, make_song, entry, message
):
    good = make_song()
    with SessionLocal() as db:
        with pytest.raises(ValueError, match=message):
            save_preferences(
                db, user_id, [{"song_id": good, "preference_type": "liked"}, entry]
            )

    assert count_preferences() == 0


def test_none_instead_of_a_list_is_rejected(user_id):
    with SessionLocal() as db:
        with pytest.raises(ValueError, match="must be a list"):
            save_preferences(db, user_id, None)


def test_unknown_user_is_rejected(make_song):
    with SessionLocal() as db:
        with pytest.raises(IntegrityError):
            set_preference(db, uuid.uuid4(), make_song(), "liked")

    assert count_preferences() == 0


def test_unknown_song_is_rejected(user_id):
    with SessionLocal() as db:
        with pytest.raises(IntegrityError):
            set_preference(db, user_id, uuid.uuid4(), "liked")

    assert count_preferences() == 0


@pytest.mark.parametrize(
    "fields",
    [{"preference_type": "loved"}, {"preference_type": "liked", "rating": 6}],
)
def test_database_rejects_invalid_values_written_directly(user_id, make_song, fields):
    with SessionLocal() as db:
        db.add(UserPreference(user_id=user_id, song_id=make_song(), **fields))
        with pytest.raises(IntegrityError):
            db.commit()

    assert count_preferences() == 0


def test_deleting_a_user_removes_their_preferences_only(make_db_user, make_song):
    leaving, staying = make_db_user("Leaving"), make_db_user("Staying")
    song_id = make_song()
    with SessionLocal() as db:
        set_preference(db, leaving, song_id, "liked")
        set_preference(db, staying, song_id, "liked")
        delete_user(db, leaving)

    assert stored(staying) == {song_id: ("liked", None)}
    assert count_preferences() == 1
    with SessionLocal() as db:
        assert db.get(Song, song_id) is not None


def test_deleting_a_song_removes_its_preferences(user_id, make_song):
    kept, removed = make_song("Kept"), make_song("Removed")
    with SessionLocal() as db:
        set_preference(db, user_id, kept, "liked")
        set_preference(db, user_id, removed, "liked")
        db.delete(db.get(Song, removed))
        db.commit()

    assert stored(user_id) == {kept: ("liked", None)}


# --- failed transactions ----------------------------------------------------


def test_failed_batch_leaves_no_partial_data(user_id, make_song):
    existing, new = make_song("Existing"), make_song("New")
    with SessionLocal() as db:
        set_preference(db, user_id, existing, "liked", rating=5)

        with pytest.raises(IntegrityError):
            save_preferences(
                db,
                user_id,
                [
                    {"song_id": existing, "preference_type": "disliked"},
                    {"song_id": new, "preference_type": "saved"},
                    {"song_id": uuid.uuid4(), "preference_type": "liked"},
                ],
            )

        # The session is still usable after the failed batch.
        assert get_preference(db, user_id, new) is None

    # Neither the update nor the new row from the failed batch was kept.
    assert stored(user_id) == {existing: ("liked", 5)}


def test_failed_batch_for_unknown_user_leaves_nothing(make_song):
    songs = [make_song(f"Song {n}") for n in range(3)]
    with SessionLocal() as db:
        with pytest.raises(IntegrityError):
            save_preferences(
                db,
                uuid.uuid4(),
                [{"song_id": s, "preference_type": "liked"} for s in songs],
            )

    assert count_preferences() == 0
