"""ORM models for MVP."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base model class."""


class Track(Base):
    """Track metadata record."""

    __tablename__ = "tracks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    absolute_path: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    file_name: Mapped[str] = mapped_column(Text, nullable=False)
    extension: Mapped[str] = mapped_column(String(16), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(nullable=False)
    mtime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    sha256: Mapped[Optional[str]] = mapped_column(Text)
    duration_sec: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 3))
    title: Mapped[Optional[str]] = mapped_column(Text)
    artist: Mapped[Optional[str]] = mapped_column(Text)
    album: Mapped[Optional[str]] = mapped_column(Text)
    year: Mapped[Optional[int]] = mapped_column(Integer)
    genre: Mapped[Optional[str]] = mapped_column(Text)
    bpm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2))
    musical_key: Mapped[Optional[str]] = mapped_column(Text)
    comment: Mapped[Optional[str]] = mapped_column(Text)
    track_number: Mapped[Optional[str]] = mapped_column(Text)
    tag_version: Mapped[Optional[str]] = mapped_column(Text)
    sync_status: Mapped[str] = mapped_column(Text, default="pending", nullable=False)
    last_tag_read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_tag_write_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    missing_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
