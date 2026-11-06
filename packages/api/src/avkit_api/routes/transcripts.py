"""Transcript queue routes. Static paths register before `/{id}`."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_transcript_service
from avkit_api.formatters import format_iso
from avkit_api.schemas.common import EmptyIn, QueueRuntimeOut
from avkit_api.schemas.transcripts import (
    TranscriptCompileOut,
    TranscriptCreateIn,
    TranscriptJobOut,
    TranscriptListOut,
    TranscriptReorderIn,
)
from avkit_core.domain.enums import TranscriptItemStatus

router = APIRouter(prefix="/transcripts", dependencies=[Depends(require_bearer)])


_MESSAGE_STATUSES = frozenset({TranscriptItemStatus.Failed, TranscriptItemStatus.Skipped})


def _aggregates(items: list[Any]) -> tuple[int, str | None, str | None, str | None]:
    done = sum(1 for item in items if item.status is TranscriptItemStatus.Done)
    if not items:
        return done, None, None, None
    dated = [item for item in items if item.processed_at is not None]
    chosen = max(dated, key=lambda item: item.processed_at) if dated else items[-1]
    title = chosen.title
    message = chosen.error_message if chosen.status in _MESSAGE_STATUSES else None
    return done, title, chosen.status.value, message


def _job_out(transcript: Any, job: Any) -> TranscriptJobOut:
    items = transcript.list_items(job.id)
    done, last_title, last_status, last_message = _aggregates(items)
    zip_path = None if job.zip_path is None else str(job.zip_path)
    return TranscriptJobOut(
        id=job.id,
        channel_url=job.channel_url,
        channel_name=job.channel_name,
        status=job.status.value,
        output_dir=str(job.output_dir),
        video_count=job.video_count,
        transcripts_done=done,
        word_count=job.word_count,
        zip_path=zip_path,
        last_title=last_title,
        last_item_status=last_status,
        last_item_message=last_message,
        queue_position=job.queue_position,
        error_message=job.error_message,
        created_at=format_iso(job.created_at),
        updated_at=format_iso(job.updated_at),
    )


@router.post("", status_code=201, response_model=TranscriptJobOut)
def create_transcript(
    body: TranscriptCreateIn,
    transcript: Any = Depends(get_transcript_service),
) -> TranscriptJobOut:
    """Add a channel batch."""
    return _job_out(transcript, transcript.add_channel(body.channel_url))


@router.get("", response_model=TranscriptListOut)
def list_transcripts(transcript: Any = Depends(get_transcript_service)) -> TranscriptListOut:
    """Return the transcript queue plus processor snapshot."""
    runtime = transcript.get_processor_state()
    return TranscriptListOut(
        items=[_job_out(transcript, job) for job in transcript.get_queue()],
        processor=QueueRuntimeOut(state=runtime.state.value, current_job_id=runtime.current_job_id),
    )


@router.post("/start", status_code=202)
def start_transcripts(
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> Response:
    """Start the transcript worker."""
    del body
    transcript.start_processing()
    return Response(status_code=202)


@router.post("/pause", status_code=202)
def pause_transcripts(
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> Response:
    """Pause the transcript worker."""
    del body
    transcript.pause_processing()
    return Response(status_code=202)


@router.post("/resume", status_code=202)
def resume_transcripts(
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> Response:
    """Resume the transcript worker."""
    del body
    transcript.resume_processing()
    return Response(status_code=202)


@router.post("/stop", status_code=202)
def stop_transcripts(
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> Response:
    """Stop the transcript worker (parent → Cancelled)."""
    del body
    transcript.stop_processing()
    return Response(status_code=202)


@router.put("/reorder", response_model=TranscriptListOut)
def reorder_transcripts(
    body: TranscriptReorderIn,
    transcript: Any = Depends(get_transcript_service),
) -> TranscriptListOut:
    """Reorder the transcript queue."""
    transcript.reorder_queue(body.job_ids)
    runtime = transcript.get_processor_state()
    return TranscriptListOut(
        items=[_job_out(transcript, job) for job in transcript.get_queue()],
        processor=QueueRuntimeOut(state=runtime.state.value, current_job_id=runtime.current_job_id),
    )


@router.get("/{id}", response_model=TranscriptJobOut)
def get_transcript(id: str, transcript: Any = Depends(get_transcript_service)) -> TranscriptJobOut:
    """Return one parent job with aggregates."""
    return _job_out(transcript, transcript.get_job(id))


@router.delete("/{id}", status_code=204)
def delete_transcript(id: str, transcript: Any = Depends(get_transcript_service)) -> Response:
    """Remove a channel. Files stay."""
    transcript.remove_channel(id)
    return Response(status_code=204)


@router.post("/{id}/compile", response_model=TranscriptCompileOut)
def compile_transcript(
    id: str,
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> TranscriptCompileOut:
    """Compile volumes. Paths only, no text."""
    del body
    paths = transcript.compile_channel(id)
    return TranscriptCompileOut(compiled_paths=[str(path) for path in paths])


@router.post("/{id}/requeue", response_model=TranscriptJobOut)
def requeue_transcript(
    id: str,
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> TranscriptJobOut:
    """Requeue a Cancelled channel."""
    del body
    return _job_out(transcript, transcript.requeue_channel(id))


@router.post("/{id}/retry", response_model=TranscriptJobOut)
def retry_transcript(
    id: str,
    body: EmptyIn | None = Body(default=None),
    transcript: Any = Depends(get_transcript_service),
) -> TranscriptJobOut:
    """Retry a Failed channel."""
    del body
    return _job_out(transcript, transcript.retry_failed_channel(id))
