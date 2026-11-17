from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.spotify_account import SpotifyAccount
from models.user import User


def get_spotify_account_by_spotify_id(
    db: Session, spotify_account_id: str
) -> SpotifyAccount | None:
    return db.scalar(
        select(SpotifyAccount).where(
            SpotifyAccount.spotify_account_id == spotify_account_id
        )
    )


def _store_profile_and_token(
    account: SpotifyAccount, profile: dict, token: dict
) -> None:
    spotify_email = profile.get("email")

    if spotify_email:
        account.email = spotify_email.strip()

    account.spotify_user_id = profile["id"]
    account.display_name = profile.get("display_name")
    account.access_token = token["access_token"]
    # Spotify may omit the refresh token; keep the one we already have.
    account.refresh_token = token.get("refresh_token") or account.refresh_token
    account.token_expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=token.get("expires_in", 3600)
    )
    account.scope = token.get("scope")


def link_spotify_account(db: Session, *, profile: dict, token: dict) -> User:
    """Create or update the user behind a Spotify login and return them.

    Accounts are matched on the Spotify user ID only, never on email: Spotify
    doesn't guarantee the email is verified, so matching on it would let
    someone take over an existing MusicVault account.
    """
    spotify_id = profile["id"]

    account = get_spotify_account_by_spotify_id(db, spotify_id)

    if account is None:
        user = User(
            email=None,
            display_name=profile.get("display_name"),
        )

        account = SpotifyAccount(
            user=user,
            spotify_account_id=spotify_id,
        )

        db.add(account)
    else:
        user = account.user

    _store_profile_and_token(account, profile, token)

    db.commit()
    db.refresh(user)
    return user


def link_spotify_to_user(
    db: Session, user: User, *, profile: dict, token: dict
) -> str | None:
    """Link a Spotify account to an existing user, or return why it cannot be."""
    spotify_id = profile["id"]
    user_id = user.id

    # Locked until commit, so a password change can't land between check and link.
    current_version = db.scalar(
        select(User.auth_version).where(User.id == user_id).with_for_update()
    )
    if current_version != user.auth_version:
        return "invalid_state"

    taken = get_spotify_account_by_spotify_id(db, spotify_id)
    if taken is not None:
        return "already_connected" if taken.user_id == user_id else "spotify_in_use"

    own = db.scalar(select(SpotifyAccount).where(SpotifyAccount.user_id == user_id))
    if own is not None:
        return "already_connected"

    account = SpotifyAccount(user_id=user_id, spotify_account_id=spotify_id)
    _store_profile_and_token(account, profile, token)
    db.add(account)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        taken = get_spotify_account_by_spotify_id(db, spotify_id)
        if taken is not None and taken.user_id != user_id:
            return "spotify_in_use"
        return "already_connected"

    return None


def unlink_spotify(db: Session, user_id: uuid.UUID) -> bool:
    account = db.scalar(
        select(SpotifyAccount).where(SpotifyAccount.user_id == user_id)
    )
    if account is None:
        return False
    db.delete(account)
    db.commit()
    return True
