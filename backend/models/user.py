from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from .classification import DataClass, classified

if TYPE_CHECKING:
    from .spotify_account import SpotifyAccount


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        info=classified(DataClass.CONFIDENTIAL),
    )
    email: Mapped[str | None] = mapped_column(
        String(320), nullable=True, info=classified(DataClass.CONFIDENTIAL)
    )
    password_hash: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.RESTRICTED)
    )
    auth_version: Mapped[int] = mapped_column(
        Integer,
        server_default="1",
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    display_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, info=classified(DataClass.CONFIDENTIAL)
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

    spotify_account: Mapped["SpotifyAccount | None"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"
