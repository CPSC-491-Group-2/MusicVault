from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

from .classification import DataClass, classified


class CrawlJob(Base):
    """One unit of crawler work, claimed by lane and priority."""

    __tablename__ = "crawl_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        info=classified(DataClass.INTERNAL),
    )
    kind: Mapped[str] = mapped_column(
        String(50), nullable=False, info=classified(DataClass.INTERNAL)
    )
    lane: Mapped[str] = mapped_column(
        String(50), nullable=False, info=classified(DataClass.INTERNAL)
    )
    target: Mapped[str] = mapped_column(
        String(255), nullable=False, info=classified(DataClass.INTERNAL)
    )
    # none_as_null stores None as SQL NULL rather than JSON null.
    payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB(none_as_null=True), nullable=True, info=classified(DataClass.INTERNAL)
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        server_default="50",
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="queued",
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    run_after: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        info=classified(DataClass.INTERNAL),
    )
    last_error: Mapped[str | None] = mapped_column(
        Text, nullable=True, info=classified(DataClass.INTERNAL)
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
        return (
            f"CrawlJob(id={self.id!r}, kind={self.kind!r}, "
            f"target={self.target!r}, status={self.status!r})"
        )
