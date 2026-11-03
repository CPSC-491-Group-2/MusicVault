from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base

from .classification import DataClass, classified

if TYPE_CHECKING:
    from .user import User


class SpotifyAccount(Base):
    __tablename__ = "spotify_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        info=classified(DataClass.INTERNAL),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        info=classified(DataClass.CONFIDENTIAL),
    )
    spotify_account_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        info=classified(DataClass.CONFIDENTIAL),
    )
    spotify_user_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, info=classified(DataClass.CONFIDENTIAL)
    )
    display_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, info=classified(DataClass.CONFIDENTIAL)
    )
    email: Mapped[str | None] = mapped_column(
        String(320), nullable=True, info=classified(DataClass.CONFIDENTIAL)
    )
    access_token: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.RESTRICTED)
    )
    refresh_token: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.RESTRICTED)
    )
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, info=classified(DataClass.INTERNAL)
    )
    scope: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.CONFIDENTIAL)
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

    user: Mapped["User"] = relationship(back_populates="spotify_account")

    def __repr__(self) -> str:
        return f"SpotifyAccount(id={self.id!r}, user_id={self.user_id!r})"
