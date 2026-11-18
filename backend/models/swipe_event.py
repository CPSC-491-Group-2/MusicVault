from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

from .classification import DataClass, classified


class SwipeEvent(Base):
    """One keep/pass/skip a user made on a song in the swipe deck."""

    __tablename__ = "swipe_events"

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
        info=classified(DataClass.CONFIDENTIAL),
    )
    action: Mapped[str] = mapped_column(
        String(20), nullable=False, info=classified(DataClass.CONFIDENTIAL)
    )
    deck_position: Mapped[int | None] = mapped_column(
        Integer, nullable=True, info=classified(DataClass.CONFIDENTIAL)
    )
    algorithm_version: Mapped[str | None] = mapped_column(
        String(100), nullable=True, info=classified(DataClass.INTERNAL)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )

    def __repr__(self) -> str:
        return f"SwipeEvent(id={self.id!r})"
