from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
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


def link_spotify_account(db: Session, *, profile: dict, token: dict) -> User:
    """Create or update the user behind a Spotify login and return them.

    Accounts are matched on the Spotify user ID only, never on email: Spotify
    doesn't guarantee the email is verified, so matching on it would let
    someone take over an existing MusicVault account.
    """
    spotify_id = profile["id"]
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=token.get("expires_in", 3600)
    )

    account = get_spotify_account_by_spotify_id(db, spotify_id)
    if account is None:
        email = profile.get("email")
        if email and db.scalar(select(User.id).where(User.email == email)):
            email = None
        user = User(email=email, display_name=profile.get("display_name"))
        account = SpotifyAccount(user=user, spotify_account_id=spotify_id)
        db.add(account)
    else:
        user = account.user

    account.spotify_user_id = spotify_id
    account.display_name = profile.get("display_name")
    account.access_token = token["access_token"]
    # Spotify may omit the refresh token; keep the one we already have.
    account.refresh_token = token.get("refresh_token") or account.refresh_token
    account.token_expires_at = expires_at
    account.scope = token.get("scope")

    db.commit()
    db.refresh(user)
    return user
