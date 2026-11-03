from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

if TYPE_CHECKING:
    from .song import Song


class Artist(Base):
    """An artist, shared by every song that credits them."""

    __tablename__ = "artists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    spotify_artist_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    # None until a genre lookup has run; [] means it ran and found none.
    # none_as_null stores None as SQL NULL; JSON null would fail the check.
    genres: Mapped[list[str] | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True
    )
    genres_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    genres_fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
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
        return f"Artist(id={self.id!r}, name={self.name!r})"


class SongArtist(Base):
    """One credited artist of a song; position 1 is the first credit."""

    __tablename__ = "song_artists"

    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    song: Mapped["Song"] = relationship(back_populates="artist_credits")
    artist: Mapped["Artist"] = relationship()

    def __repr__(self) -> str:
        return (
            f"SongArtist(song_id={self.song_id!r}, "
            f"artist_id={self.artist_id!r}, position={self.position!r})"
        )
