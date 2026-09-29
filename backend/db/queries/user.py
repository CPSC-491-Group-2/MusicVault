from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User


def create_user(
    db: Session, *, email: str | None = None, display_name: str | None = None
) -> User:
    user = User(email=email, display_name=display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


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
        user.email = email
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
