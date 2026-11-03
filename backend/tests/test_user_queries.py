from __future__ import annotations

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from db.queries.user import (
    create_user,
    delete_user,
    get_user_by_email,
    get_user_by_id,
    normalize_email,
    update_user,
)
from models.spotify_account import SpotifyAccount


def test_create_user_sets_id_and_timestamps(db_session):
    user = create_user(db_session, email="test@example.com", display_name="Test User")

    assert user.id is not None
    assert user.created_at is not None
    assert user.updated_at is not None


def test_create_user_without_email(db_session):
    # Spotify no longer guarantees email, so Spotify-only accounts must work.
    user = create_user(db_session, display_name="Spotify Only")

    assert user.id is not None
    assert user.email is None


def test_create_user_with_no_optional_fields(db_session):
    # email and display_name are both optional; a bare user must still work.
    user = create_user(db_session)

    assert user.id is not None
    assert user.email is None
    assert user.display_name is None


def test_duplicate_email_is_rejected(db_session):
    create_user(db_session, email="dup@example.com")

    with pytest.raises(IntegrityError):
        create_user(db_session, email="dup@example.com")


def test_get_user_by_id_returns_match(db_session):
    created = create_user(db_session, email="lookup@example.com")

    fetched = get_user_by_id(db_session, created.id)

    assert fetched is not None
    assert fetched.id == created.id


def test_get_user_by_id_missing_returns_none(db_session):
    assert get_user_by_id(db_session, uuid.uuid4()) is None


def test_get_user_by_email_returns_match(db_session):
    created = create_user(db_session, email="byemail@example.com")

    fetched = get_user_by_email(db_session, "byemail@example.com")

    assert fetched is not None
    assert fetched.id == created.id


def test_update_user_changes_fields_and_bumps_updated_at(db_session):
    user = create_user(db_session, email="before@example.com", display_name="Before")
    original_updated_at = user.updated_at

    updated = update_user(db_session, user.id, display_name="After")

    assert updated is not None
    assert updated.display_name == "After"
    assert updated.email == "before@example.com"
    assert updated.updated_at >= original_updated_at


def test_update_user_missing_returns_none(db_session):
    assert update_user(db_session, uuid.uuid4(), display_name="Nobody") is None


def test_delete_user_removes_record(db_session):
    user = create_user(db_session, email="todelete@example.com")

    assert delete_user(db_session, user.id) is True
    assert get_user_by_id(db_session, user.id) is None


def test_delete_user_missing_returns_false(db_session):
    assert delete_user(db_session, uuid.uuid4()) is False


def test_delete_user_cascades_to_spotify_account(db_session):
    user = create_user(db_session, display_name="Has Spotify")
    spotify_account = SpotifyAccount(user_id=user.id, spotify_account_id="spotify-123")
    db_session.add(spotify_account)
    db_session.commit()
    spotify_account_id = spotify_account.id

    delete_user(db_session, user.id)

    assert db_session.get(SpotifyAccount, spotify_account_id) is None

# ============================================================
# LOCAL AUTHENTICATION DATABASE TESTS
# ============================================================


def test_normalize_email():
    email = normalize_email("  MusicFan@Example.COM  ")

    assert email == "musicfan@example.com"


def test_create_user_normalizes_email(db_session):
    user = create_user(
        db_session,
        email="  MusicFan@Example.COM  ",
        display_name="Music Fan",
    )

    assert user.email == "musicfan@example.com"


def test_get_user_by_email_case_insensitive(db_session):
    created = create_user(
        db_session,
        email="musicfan@example.com",
    )

    fetched = get_user_by_email(
        db_session,
        "MUSICFAN@EXAMPLE.COM",
    )

    assert fetched is not None
    assert fetched.id == created.id


def test_duplicate_email_different_case_rejected(db_session):
    create_user(
        db_session,
        email="musicfan@example.com",
    )

    with pytest.raises(IntegrityError):
        create_user(
            db_session,
            email="MUSICFAN@EXAMPLE.COM",
        )


def test_create_user_with_password_hash(db_session):
    # Dummy value for database storage testing only.
    # No password hashing or verification is performed.
    test_hash = "dummy-hash-not-for-authentication"

    user = create_user(
        db_session,
        email="local@example.com",
        display_name="Local User",
        password_hash=test_hash,
    )

    assert user.id is not None
    assert user.email == "local@example.com"
    assert user.password_hash == test_hash


def test_password_hash_requires_email(db_session):
    with pytest.raises(ValueError):
        create_user(
            db_session,
            password_hash="dummy-hash-not-for-authentication",
        )


def test_update_user_normalizes_email(db_session):
    user = create_user(
        db_session,
        email="original@example.com",
    )

    updated = update_user(
        db_session,
        user.id,
        email="  UPDATED@EXAMPLE.COM  ",
    )

    assert updated is not None
    assert updated.email == "updated@example.com"