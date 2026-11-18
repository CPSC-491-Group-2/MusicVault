from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Double, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from .classification import DataClass, classified

if TYPE_CHECKING:
    from .song import Song


class Artist(Base):
    """An artist, shared by every song that credits them."""

    __tablename__ = "artists"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        info=classified(DataClass.INTERNAL),
    )
    name: Mapped[str] = mapped_column(
        String(500), nullable=False, info=classified(DataClass.PUBLIC)
    )
    spotify_artist_id: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, info=classified(DataClass.PUBLIC)
    )
    mbid: Mapped[str | None] = mapped_column(
        String(36), unique=True, nullable=True, info=classified(DataClass.PUBLIC)
    )
    fans: Mapped[int | None] = mapped_column(
        Integer, nullable=True, info=classified(DataClass.PUBLIC)
    )
    fans_source: Mapped[str | None] = mapped_column(
        String(100), nullable=True, info=classified(DataClass.INTERNAL)
    )
    # Null until the crawler has pulled this artist's neighbours.
    last_expanded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, info=classified(DataClass.INTERNAL)
    )
    # None until a genre lookup has run; [] means it ran and found none.
    # none_as_null stores None as SQL NULL; JSON null would fail the check.
    genres: Mapped[list[str] | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, info=classified(DataClass.PUBLIC)
    )
    genres_source: Mapped[str | None] = mapped_column(
        String(100), nullable=True, info=classified(DataClass.INTERNAL)
    )
    genres_fetched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, info=classified(DataClass.INTERNAL)
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

    def __repr__(self) -> str:
        return f"Artist(id={self.id!r}, name={self.name!r})"


class SongArtist(Base):
    """One credited artist of a song; position 1 is the first credit."""

    __tablename__ = "song_artists"

    song_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
        info=classified(DataClass.INTERNAL),
    )
    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
        info=classified(DataClass.INTERNAL),
    )
    position: Mapped[int] = mapped_column(
        Integer, nullable=False, info=classified(DataClass.PUBLIC)
    )

    song: Mapped["Song"] = relationship(back_populates="artist_credits")
    artist: Mapped["Artist"] = relationship()

    def __repr__(self) -> str:
        return (
            f"SongArtist(song_id={self.song_id!r}, "
            f"artist_id={self.artist_id!r}, position={self.position!r})"
        )


class ArtistExternalId(Base):
    """One provider's own ID for an artist, used to match crawled records."""

    __tablename__ = "artist_external_ids"

    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
        info=classified(DataClass.INTERNAL),
    )
    provider: Mapped[str] = mapped_column(
        String(50), primary_key=True, info=classified(DataClass.INTERNAL)
    )
    external_id: Mapped[str] = mapped_column(
        String(255), nullable=False, info=classified(DataClass.PUBLIC)
    )

    def __repr__(self) -> str:
        return (
            f"ArtistExternalId(artist_id={self.artist_id!r}, "
            f"provider={self.provider!r})"
        )


class ArtistEdge(Base):
    """A directed similarity edge from one artist to another."""

    __tablename__ = "artist_edges"

    src_artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
        info=classified(DataClass.INTERNAL),
    )
    dst_artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
        info=classified(DataClass.INTERNAL),
    )
    provider: Mapped[str] = mapped_column(
        String(50), primary_key=True, info=classified(DataClass.INTERNAL)
    )
    weight: Mapped[float] = mapped_column(
        Double, nullable=False, info=classified(DataClass.INTERNAL)
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )

    def __repr__(self) -> str:
        return (
            f"ArtistEdge(src_artist_id={self.src_artist_id!r}, "
            f"dst_artist_id={self.dst_artist_id!r}, provider={self.provider!r})"
        )


class ArtistTag(Base):
    """One provider's tag for an artist, with that provider's weight."""

    __tablename__ = "artist_tags"

    artist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
        info=classified(DataClass.INTERNAL),
    )
    tag: Mapped[str] = mapped_column(
        String(100), primary_key=True, info=classified(DataClass.PUBLIC)
    )
    provider: Mapped[str] = mapped_column(
        String(50), primary_key=True, info=classified(DataClass.INTERNAL)
    )
    weight: Mapped[float | None] = mapped_column(
        Double, nullable=True, info=classified(DataClass.INTERNAL)
    )

    def __repr__(self) -> str:
        return (
            f"ArtistTag(artist_id={self.artist_id!r}, tag={self.tag!r}, "
            f"provider={self.provider!r})"
        )
