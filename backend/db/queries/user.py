from __future__ import annotations

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from models.user import User

def normalize_email(email: str) -> str:
    normalized = email.strip().lower()

    if not normalized:
        raise ValueError("Email cannot be empty")

    return normalized

def create_user(
    db: Session,
    *,
    email: str | None = None,
    display_name: str | None = None,
    password_hash: str | None = None,
) -> User:
    """Create a MusicVault user with optional local credentials."""

    normalized_email = normalize_email(email) if email is not None else None

    if password_hash is not None and normalized_email is None:
        raise ValueError("An email is required for password authentication")

    user = User(
        email=normalized_email,
        display_name=display_name,
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = normalize_email(email)
    return db.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )


def update_user(
    db: Session,
    user_id: uuid.UUID,
    *,
    email: str | None = None,
    display_name: str | None = None,
) -> User | None:
    user = db.get(User, user_id)
    if user is None:
        return None
    if email is not None:
        user.email = normalize_email(email)
    if display_name is not None:
        user.display_name = display_name
    db.commit()
    db.refresh(user)
    return user


def set_password(
    db: Session,
    user_id: uuid.UUID,
    password_hash: str,
    *,
    expected_version: int,
    email: str | None = None,
) -> int | None:
    """New auth_version, or None if the user changed since expected_version."""
    # Sessions issued before this change now fail login_required.
    values = {"password_hash": password_hash, "auth_version": User.auth_version + 1}
    if email is not None:
        values["email"] = normalize_email(email)
    auth_version = db.scalar(
        update(User)
        .where(User.id == user_id, User.auth_version == expected_version)
        .values(values)
        .returning(User.auth_version)
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return auth_version


def rehash_password(db: Session, user: User, password_hash: str) -> bool:
    """Swap in a fresh hash of the same password; False if it changed meanwhile."""
    result = db.execute(
        update(User)
        .where(
            User.id == user.id,
            User.password_hash == user.password_hash,
            User.auth_version == user.auth_version,
        )
        .values(password_hash=password_hash)
        .execution_options(synchronize_session=False)
    )
    replaced = result.rowcount == 1
    db.commit()
    return replaced


def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    user = db.get(User, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
