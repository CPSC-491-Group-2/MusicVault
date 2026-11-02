from __future__ import annotations

import uuid

from sqlalchemy import func, select
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


def delete_user(db: Session, user_id: uuid.UUID) -> bool:
    user = db.get(User, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
