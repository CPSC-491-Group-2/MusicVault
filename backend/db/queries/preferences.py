from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from models.user_preference import PREFERENCE_TYPES, UserPreference


def set_preference(
    db: Session,
    user_id: uuid.UUID,
    song_id: uuid.UUID,
    preference_type: str,
    rating: int | None = None,
) -> UserPreference:
    """Create or replace a user's preference for one song and return it.

    A user has at most one preference per song: setting it again overwrites
    the type and rating instead of adding a row. This is a single
    INSERT ... ON CONFLICT, so concurrent submissions for the same song also
    end with one row. An unknown user or song raises IntegrityError.
    """
    return save_preferences(
        db,
        user_id,
        [{"song_id": song_id, "preference_type": preference_type, "rating": rating}],
    )[0]


def save_preferences(
    db: Session, user_id: uuid.UUID, preferences: list[dict]
) -> list[UserPreference]:
    """Set several preferences in one transaction, all or nothing.

    Each entry is a dict with `song_id`, `preference_type` and an optional
    `rating`. If a song appears more than once, the last entry wins. Invalid
    input raises ValueError before anything is written; any database error
    (such as an unknown song) rolls the whole batch back. Returns one saved
    preference per song, in the order of each song's last entry.
    """
    entries = _validated(preferences)

    try:
        ids = [db.scalar(_upsert(user_id, entry)) for entry in entries]
        db.commit()
    except Exception:
        db.rollback()
        raise

    saved = {
        p.id: p
        for p in db.scalars(
            select(UserPreference)
            .where(UserPreference.id.in_(ids))
            .execution_options(populate_existing=True)
        )
    }
    return [saved[i] for i in ids]


def get_preference(
    db: Session, user_id: uuid.UUID, song_id: uuid.UUID
) -> UserPreference | None:
    return db.scalar(
        select(UserPreference).where(
            UserPreference.user_id == user_id, UserPreference.song_id == song_id
        )
    )


def get_preferences(
    db: Session, user_id: uuid.UUID, preference_types: tuple[str, ...] | None = None
) -> list[UserPreference]:
    """A user's preferences, optionally only some types, oldest first."""
    query = select(UserPreference).where(UserPreference.user_id == user_id)
    if preference_types is not None:
        for preference_type in preference_types:
            _check_type(preference_type)
        query = query.where(UserPreference.preference_type.in_(preference_types))
    return list(
        db.scalars(
            query.order_by(
                UserPreference.created_at, UserPreference.song_id, UserPreference.id
            )
        )
    )


def delete_preference(db: Session, user_id: uuid.UUID, song_id: uuid.UUID) -> bool:
    """Remove a user's preference for a song; False if there wasn't one."""
    deleted = db.execute(
        delete(UserPreference).where(
            UserPreference.user_id == user_id, UserPreference.song_id == song_id
        )
    ).rowcount
    db.commit()
    return deleted > 0


def _upsert(user_id: uuid.UUID, entry: dict):
    statement = insert(UserPreference).values(
        user_id=user_id,
        song_id=entry["song_id"],
        preference_type=entry["preference_type"],
        rating=entry["rating"],
    )
    return statement.on_conflict_do_update(
        constraint="uq_user_preferences_user_song",
        set_={
            "preference_type": statement.excluded.preference_type,
            "rating": statement.excluded.rating,
            "updated_at": func.now(),
        },
    ).returning(UserPreference.id)


def _validated(preferences: list[dict]) -> list[dict]:
    """Check every entry and drop earlier repeats of a song, keeping order."""
    if preferences is None:
        raise ValueError("preferences must be a list")

    by_song = {}
    for position, entry in enumerate(preferences, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"preference {position} is not a dictionary")
        if not isinstance(entry.get("song_id"), uuid.UUID):
            raise ValueError(f"preference {position} is missing song_id")
        _check_type(entry.get("preference_type"), position)
        rating = entry.get("rating")
        if rating is not None and (
            not isinstance(rating, int)
            or isinstance(rating, bool)
            or not 1 <= rating <= 5
        ):
            raise ValueError(
                f"preference {position} rating must be 1-5 (got {rating!r})"
            )
        # Re-inserting moves a repeated song to its last position.
        by_song.pop(entry["song_id"], None)
        by_song[entry["song_id"]] = {
            "song_id": entry["song_id"],
            "preference_type": entry["preference_type"],
            "rating": rating,
        }
    return list(by_song.values())


def _check_type(preference_type, position: int | None = None) -> None:
    if preference_type not in PREFERENCE_TYPES:
        where = f"preference {position} " if position is not None else ""
        raise ValueError(
            f"{where}preference_type must be one of {', '.join(PREFERENCE_TYPES)} "
            f"(got {preference_type!r})"
        )
