from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from db.queries.user import create_user
from models.spotify_account import SpotifyAccount


def test_spotify_account_id_is_required(db_session):
    user = create_user(db_session, display_name="Missing Spotify ID")

    db_session.add(SpotifyAccount(user_id=user.id))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_spotify_account_id_must_be_unique(db_session):
    user_one = create_user(db_session, display_name="First")
    user_two = create_user(db_session, display_name="Second")

    db_session.add(SpotifyAccount(user_id=user_one.id, spotify_account_id="shared-id"))
    db_session.commit()

    db_session.add(SpotifyAccount(user_id=user_two.id, spotify_account_id="shared-id"))
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_user_can_only_have_one_spotify_account(db_session):
    user = create_user(db_session, display_name="Double Link")

    db_session.add(SpotifyAccount(user_id=user.id, spotify_account_id="first-account"))
    db_session.commit()

    db_session.add(SpotifyAccount(user_id=user.id, spotify_account_id="second-account"))
    with pytest.raises(IntegrityError):
        db_session.commit()
