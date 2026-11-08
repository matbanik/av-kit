"""SQLAlchemy ORM models mapped to the Phase 2 tables plus conversion and capture."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for av-kit SQLite tables."""


class DownloadJobRow(Base):
    """Queue row for one downloader job."""

    __tablename__ = "download_jobs"
    __table_args__ = (
        Index("ix_download_jobs_queue_position", "queue_position"),
        Index("ix_download_jobs_status", "status"),
        Index("ix_download_jobs_video_id", "video_id"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    video_id: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    quality: Mapped[str] = mapped_column(Text, nullable=False)
    audio_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    audio_format: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    speed_bps: Mapped[float | None] = mapped_column(Float, nullable=True)
    eta_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queue_position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Last, so a fresh database and one upgraded by COLUMN_MIGRATIONS have the same order.
    received_height: Mapped[int | None] = mapped_column(Integer, nullable=True)


class DownloadArchiveRow(Base):
    """Skip catalog keyed by extractor + video_id."""

    __tablename__ = "download_archive"

    extractor: Mapped[str] = mapped_column(Text, primary_key=True)
    video_id: Mapped[str] = mapped_column(Text, primary_key=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TranscriptJobRow(Base):
    """Parent channel-batch transcript job."""

    __tablename__ = "transcript_jobs"
    __table_args__ = (Index("ix_transcript_jobs_queue_position", "queue_position"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    channel_url: Mapped[str] = mapped_column(Text, nullable=False)
    channel_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    output_dir: Mapped[str] = mapped_column(Text, nullable=False)
    video_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    zip_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    queue_position: Mapped[int] = mapped_column(Integer, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TranscriptItemRow(Base):
    """Per-video transcript resume row."""

    __tablename__ = "transcript_items"
    __table_args__ = (
        UniqueConstraint("job_id", "video_id", name="uq_transcript_items_job_video"),
        Index("ix_transcript_items_job_status", "job_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("transcript_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    video_id: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TTSJobRow(Base):
    """TTS generation job. Full input text is not stored."""

    __tablename__ = "tts_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_kind: Mapped[str] = mapped_column(Text, nullable=False)
    source_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    text_hash: Mapped[str] = mapped_column(Text, nullable=False)
    text_preview: Mapped[str] = mapped_column(Text, nullable=False)
    voice: Mapped[str] = mapped_column(Text, nullable=False)
    speed: Mapped[float] = mapped_column(Float, nullable=False)
    format: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    output_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    segments_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    segments_done: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ModelVariantRow(Base):
    """Kokoro catalog row. Runtime load flags are not columns."""

    __tablename__ = "model_variants"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(Text, nullable=False)
    precision: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    path: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_downloaded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ConversionJobRow(Base):
    """Queue row for one conversion job."""

    __tablename__ = "conversion_jobs"
    __table_args__ = (
        Index("ix_conversion_jobs_queue_position", "queue_position"),
        Index("ix_conversion_jobs_status", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    input_path: Mapped[str] = mapped_column(Text, nullable=False)
    output_path: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    preset_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    cq: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scale_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    audio_mode: Mapped[str | None] = mapped_column(Text, nullable=True)
    gpu_encoder: Mapped[str | None] = mapped_column(Text, nullable=True)
    in_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    out_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    copy_mode: Mapped[str | None] = mapped_column(Text, nullable=True)
    stream_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    progress: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    speed_bps: Mapped[float | None] = mapped_column(Float, nullable=True)
    eta_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    queue_position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Last, so a fresh database and one upgraded by COLUMN_MIGRATIONS have the same order.
    gpu_preference: Mapped[str | None] = mapped_column(Text, nullable=True)


class CaptureShotRow(Base):
    """Inbox original plus optional annotated sibling paths."""

    __tablename__ = "capture_shots"
    __table_args__ = (Index("ix_capture_shots_created_at", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    original_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    annotated_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    sidecar_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    width: Mapped[int] = mapped_column(Integer, nullable=False)
    height: Mapped[int] = mapped_column(Integer, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CaptureRequestRow(Base):
    """Short-lived interactive capture wait row."""

    __tablename__ = "capture_requests"
    __table_args__ = (
        Index("ix_capture_requests_status", "status"),
        Index("ix_capture_requests_expires_at", "expires_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    shot_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SettingRow(Base):
    """Namespaced settings leaf."""

    __tablename__ = "settings"

    namespace: Mapped[str] = mapped_column(Text, primary_key=True)
    key: Mapped[str] = mapped_column(Text, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    value_type: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
