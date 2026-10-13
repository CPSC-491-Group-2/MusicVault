from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from .song import Song

TIME_RANGES = ("short_term", "medium_term", "long_term")


class UserTopSong(Base):
    """One ranked entry in a user's top songs for a Spotify time range."""

    __tablename__ = "user_top_songs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("songs.id", ondelete="CASCADE"), nullable=False
    )
    time_range: Mapped[str] = mapped_column(String(20), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    song: Mapped["Song"] = relationship()

    def __repr__(self) -> str:
        return (
            f"UserTopSong(user_id={self.user_id!r}, "
            f"time_range={self.time_range!r}, rank={self.rank!r})"
        )
