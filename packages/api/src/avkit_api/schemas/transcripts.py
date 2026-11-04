"""Transcript request and response schemas."""

from __future__ import annotations

from pydantic import Field

from avkit_api.schemas.common import ApiModel, QueueRuntimeOut


class TranscriptCreateIn(ApiModel):
    """POST /transcripts body."""

    channel_url: str = Field(min_length=1)


class TranscriptReorderIn(ApiModel):
    """PUT /transcripts/reorder body."""

    job_ids: list[str]


class TranscriptJobOut(ApiModel):
    """Formatted transcript parent row with computed aggregates."""

    id: str
    channel_url: str
    channel_name: str
    status: str
    output_dir: str
    video_count: int
    transcripts_done: int
    word_count: int
    zip_path: str | None
    last_title: str | None
    last_item_status: str | None
    queue_position: int
    error_message: str | None
    created_at: str
    updated_at: str


class TranscriptListOut(ApiModel):
    """GET /transcripts envelope."""

    items: list[TranscriptJobOut]
    processor: QueueRuntimeOut


class TranscriptCompileOut(ApiModel):
    """POST /transcripts/{id}/compile body."""

    compiled_paths: list[str]
