from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from .classification import DataClass, classified

if TYPE_CHECKING:
    from .song import Song

PREFERENCE_TYPES = ("liked", "disliked", "saved", "skipped", "neutral")


class UserPreference(Base):
    """A user's sentiment about one song; at most one per user and song."""

    __tablename__ = "user_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        info=classified(DataClass.INTERNAL),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        info=classified(DataClass.CONFIDENTIAL),
    )
    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("songs.id", ondelete="CASCADE"),
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    preference_type: Mapped[str] = mapped_column(
        String(50), nullable=False, info=classified(DataClass.CONFIDENTIAL)
    )
    rating: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True, info=classified(DataClass.CONFIDENTIAL)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )

    song: Mapped["Song"] = relationship()

    def __repr__(self) -> str:
        return (
            f"UserPreference(id={self.id!r}, user_id={self.user_id!r}, "
            f"song_id={self.song_id!r})"
        )
