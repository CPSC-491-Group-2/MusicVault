from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    artist_name: Mapped[str] = mapped_column(String(500), nullable=False)
    album_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    spotify_track_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    explicit: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    popularity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    popularity_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    audio_features: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    audio_features_source: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    spotify_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    album_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"Song(id={self.id!r}, title={self.title!r})"
