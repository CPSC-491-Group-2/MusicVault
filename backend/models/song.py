from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from .classification import DataClass, classified

if TYPE_CHECKING:
    from .artist import SongArtist


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        info=classified(DataClass.INTERNAL),
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False, info=classified(DataClass.PUBLIC)
    )
    artist_name: Mapped[str] = mapped_column(
        String(500), nullable=False, info=classified(DataClass.PUBLIC)
    )
    album_name: Mapped[str | None] = mapped_column(
        String(500), nullable=True, info=classified(DataClass.PUBLIC)
    )
    spotify_track_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, info=classified(DataClass.PUBLIC)
    )
    isrc: Mapped[str | None] = mapped_column(
        String(32), nullable=True, info=classified(DataClass.PUBLIC)
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True, info=classified(DataClass.PUBLIC)
    )
    explicit: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, info=classified(DataClass.PUBLIC)
    )
    popularity: Mapped[int | None] = mapped_column(
        Integer, nullable=True, info=classified(DataClass.PUBLIC)
    )
    popularity_source: Mapped[str | None] = mapped_column(
        String(100), nullable=True, info=classified(DataClass.INTERNAL)
    )
    # none_as_null stores None as SQL NULL rather than JSON null.
    audio_features: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, info=classified(DataClass.PUBLIC)
    )
    audio_features_source: Mapped[str | None] = mapped_column(
        String(100), nullable=True, info=classified(DataClass.INTERNAL)
    )
    spotify_url: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.PUBLIC)
    )
    album_image_url: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.PUBLIC)
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

    # Credited artists in credit order; artist_name is the display string.
    artist_credits: Mapped[list["SongArtist"]] = relationship(
        back_populates="song",
        order_by="SongArtist.position",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Song(id={self.id!r}, title={self.title!r})"
