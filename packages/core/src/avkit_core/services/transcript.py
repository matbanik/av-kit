"""TranscriptService — channel queue, item fetch, compile, and zip."""

from __future__ import annotations

import json
import re
import threading
import time
import zipfile
from collections import deque
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog

from avkit_core.domain.download import ListedVideo, PlaylistInfo, VideoInfo
from avkit_core.domain.enums import QueueProcessorState, TranscriptItemStatus, TranscriptStatus
from avkit_core.domain.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    TranscriptRetryableError,
    ValidationError,
)
from avkit_core.domain.queue import QueueRuntime
from avkit_core.domain.transcript import (
    TranscriptFailureCause,
    TranscriptItem,
    TranscriptJob,
    TranscriptResult,
    TranscriptSkip,
    failure_message,
    retry_message,
    safe_reason,
)
from avkit_core.ports.filesystem import FilesystemPort
from avkit_core.ports.storage import UnitOfWork
from avkit_core.ports.transcript import TranscriptPort
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.health import redact_message
from avkit_core.services.settings import SettingsService

COMPILE_READ_MAX_BYTES = 20 * 1024 * 1024
TRANSCRIPT_LANGUAGES_DEFAULT = ["en"]
#: A Failed job's `error_message`. `Last` is the message of the Failed item processed last.
JOB_MESSAGE = "{n} of {total} videos failed. Last: {message}"
#: A Done job's `error_message` when at least one video was skipped.
SKIPPED_JOB_MESSAGE = "{n} of {total} videos had no transcript. Last: {message}"
#: Seconds in the rolling window of `transcript.requests_per_hour` (MEU-116).
RATE_WINDOW = 3600.0
UoWFactory = Callable[[], UnitOfWork]
log = structlog.get_logger(module="transcript")


def _now() -> datetime:
    return datetime.now(UTC)


def _as_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        if isinstance(value, float) and value.is_integer():
            return int(value)
        raise ValidationError("setting must be an int")
    return value


def _as_float(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValidationError("setting must be a number")
    return float(value)


def slugify(value: str) -> str:
    """Return a filesystem-safe slug for a channel or heading."""
    text = value.strip().casefold()
    pieces: list[str] = []
    for char in text:
        if char.isalnum():
            pieces.append(char)
        elif pieces and pieces[-1] != "-":
            pieces.append("-")
    return "".join(pieces).strip("-") or "channel"


class TranscriptService:
    """Transcript queue owner. Hexagonal: ports and UoW factory only."""

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        coordinator: ExtractCoordinator,
        captions: TranscriptPort,
        filesystem: FilesystemPort,
        settings: SettingsService,
        sleep: Callable[[float], None] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._coordinator = coordinator
        self._captions = captions
        self._filesystem = filesystem
        self._settings = settings
        self._sleep = sleep or time.sleep
        self._clock = clock or time.monotonic
        self._request_starts: deque[float] = deque()
        self._runtime = QueueRuntime(
            queue_name="transcripts",
            state=QueueProcessorState.Idle,
            current_job_id=None,
        )
        self._pause = False
        self._stop = False
        self._pick_processing = False
        # The retry message this worker last wrote on the job it runs (rc.3 F6).
        self._retry_message: str | None = None
        self._thread: threading.Thread | None = None
        # True from a worker's start until it decides, under `_lock`, to exit (D-306).
        self._worker_active = False
        self._lock = threading.Lock()

    def get_processor_state(self) -> QueueRuntime:
        return self._runtime

    def get_queue(self) -> list[TranscriptJob]:
        with self._uow_factory() as uow:
            jobs = uow.transcripts.list_jobs_ordered()
            return [self._with_aggregates(uow, job) for job in jobs]

    def get_job(self, job_id: str) -> TranscriptJob:
        with self._uow_factory() as uow:
            job = uow.transcripts.get_job(job_id)
            if job is None:
                raise NotFoundError(f"transcript job {job_id} not found")
            return self._with_aggregates(uow, job)

    def list_items(self, job_id: str) -> list[TranscriptItem]:
        with self._uow_factory() as uow:
            if uow.transcripts.get_job(job_id) is None:
                raise NotFoundError(f"transcript job {job_id} not found")
            return uow.transcripts.list_items(job_id)

    def add_channel(self, channel_url: str) -> TranscriptJob:
        if not isinstance(channel_url, str) or channel_url.strip() == "":
            raise ValidationError("channel_url must be a non-empty str")
        url = channel_url.strip()
        with self._uow_factory() as uow:
            for job in uow.transcripts.list_jobs_ordered():
                if job.channel_url == url:
                    raise ConflictError("channel_url is already in the queue")
        # Flat: the folder title and IDs read the same, without opening every video first.
        info = self._coordinator.extract_info(url, flat=True)
        listing = self._coordinator.extract_video_ids(url)
        videos = listing.videos
        playlist_end = _as_int(self._settings.get("transcript", "playlist_end"))
        if playlist_end > 0:
            videos = videos[:playlist_end]
        if not videos and isinstance(info, VideoInfo):
            videos = (ListedVideo(info.video_id, None),)
        if isinstance(info, PlaylistInfo):
            folder = info.title
            channel_id = info.playlist_id
        elif isinstance(info, VideoInfo):
            folder = info.title
            channel_id = info.video_id
        else:
            raise ValidationError("extract_info returned an unknown type")
        _ = channel_id
        # The folder keeps the extract title's slug (SLUG_SOURCE); the name is the channel's.
        name = listing.channel_name or info.title
        root = Path(str(self._settings.get("transcript", "output_dir"))).expanduser()
        output_dir = root / slugify(folder)
        self._filesystem.ensure_channel_dirs(output_dir)
        created = TranscriptJob(
            id=str(uuid4()),
            channel_url=url,
            channel_name=name,
            status=TranscriptStatus.Pending,
            output_dir=output_dir,
            video_count=len(videos),
            word_count=0,
            zip_path=None,
            queue_position=0,
            error_message=None,
            created_at=_now(),
            updated_at=_now(),
        )
        items = [
            TranscriptItem(
                id=str(uuid4()),
                job_id=created.id,
                video_id=video.video_id,
                title=video.title,
                language=None,
                word_count=0,
                path=None,
                status=TranscriptItemStatus.Pending,
                error_message=None,
                retry_count=0,
                processed_at=None,
            )
            for video in videos
        ]
        with self._uow_factory() as uow:
            created = replace(
                created,
                queue_position=len(uow.transcripts.list_jobs_ordered()),
            )
            uow.transcripts.add_job(created)
            uow.transcripts.replace_items(created.id, items)
            uow.commit()
        return created

    def start_processing(self) -> None:
        with self._lock:
            if self._runtime.state is QueueProcessorState.Processing:
                raise ConflictError("start_processing requires Idle or Paused")
            self._pause = False
            self._stop = False
            self._pick_processing = False
            self._runtime = QueueRuntime(
                queue_name="transcripts",
                state=QueueProcessorState.Processing,
                current_job_id=None,
            )
            self._ensure_worker()

    def pause_processing(self) -> None:
        self._pause = True

    def resume_processing(self) -> None:
        # One critical section with the worker's exits (D-306): either the worker sees
        # this resume before it exits, or this resume sees no worker and starts one.
        with self._lock:
            paused: TranscriptJob | None = None
            with self._uow_factory() as uow:
                for job in uow.transcripts.list_jobs_ordered():
                    if job.status is TranscriptStatus.Paused:
                        paused = job
                        break
            if self._runtime.state is not QueueProcessorState.Paused and paused is None:
                raise ConflictError("resume_processing requires Paused")
            if paused is not None:
                with self._uow_factory() as uow:
                    latest = uow.transcripts.get_job(paused.id)
                    if latest is None or latest.status is not TranscriptStatus.Paused:
                        raise ConflictError("resume_processing requires Paused")
                    uow.transcripts.save_job(
                        replace(
                            latest.transition(TranscriptStatus.Processing),
                            error_message=None,
                            updated_at=_now(),
                        )
                    )
                    uow.commit()
            self._pause = False
            self._stop = False
            self._pick_processing = True
            self._runtime = QueueRuntime(
                queue_name="transcripts",
                state=QueueProcessorState.Processing,
                current_job_id=paused.id if paused is not None else None,
            )
            self._ensure_worker()

    def stop_processing(self) -> None:
        with self._lock:
            self._stop = True
            if not self._worker_active:
                self._apply_stop()

    def _ensure_worker(self) -> None:
        """Start a worker unless one is active. The caller holds `_lock`."""
        if self._worker_active:
            return
        self._worker_active = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def requeue_channel(self, job_id: str) -> TranscriptJob:
        with self._uow_factory() as uow:
            job = self._require_job(uow, job_id)
            updated = replace(job.transition(TranscriptStatus.Pending), updated_at=_now())
            uow.transcripts.save_job(updated)
            uow.commit()
        return updated

    def retry_failed_channel(self, job_id: str) -> TranscriptJob:
        with self._uow_factory() as uow:
            job = self._require_job(uow, job_id)
            updated = replace(
                job.transition(TranscriptStatus.Pending),
                error_message=None,
                updated_at=_now(),
            )
            uow.transcripts.save_job(updated)
            items: list[TranscriptItem] = []
            for item in uow.transcripts.list_items(job_id):
                if item.status is TranscriptItemStatus.Failed:
                    items.append(
                        replace(
                            item.transition(TranscriptItemStatus.Pending),
                            error_message=None,
                            retry_count=0,
                        )
                    )
                else:
                    items.append(item)
            uow.transcripts.replace_items(job_id, items)
            uow.commit()
        return updated

    def remove_channel(self, job_id: str) -> None:
        with self._uow_factory() as uow:
            self._require_job(uow, job_id)
            uow.transcripts.delete_job(job_id)
            uow.commit()

    def reorder_queue(self, job_ids: list[str]) -> None:
        with self._uow_factory() as uow:
            current = [job.id for job in uow.transcripts.list_jobs_ordered()]
            if sorted(job_ids) != sorted(current):
                raise ValidationError("reorder_queue requires a permutation of current ids")
            uow.transcripts.reorder_jobs(job_ids)
            uow.commit()

    def recover_stale_processing(self) -> None:
        with self._uow_factory() as uow:
            for job in uow.transcripts.list_jobs_ordered():
                if job.status is TranscriptStatus.Processing:
                    uow.transcripts.save_job(
                        replace(job.transition(TranscriptStatus.Pending), updated_at=_now())
                    )
            uow.commit()

    def compile_channel(self, job_id: str) -> list[Path]:
        with self._uow_factory() as uow:
            job = self._require_job(uow, job_id)
            items = [
                item
                for item in uow.transcripts.list_items(job_id)
                if item.status is TranscriptItemStatus.Done and item.path is not None
            ]
        return self._write_volumes(job, items)

    def _write_volumes(self, job: TranscriptJob, items: list[TranscriptItem]) -> list[Path]:
        max_words = _as_int(self._settings.get("transcript", "max_words_per_document"))
        slug = job.output_dir.name
        compiled_dir = job.output_dir / "compiled"
        volumes: list[list[TranscriptItem]] = [[]]
        running = 0
        for item in items:
            next_words = item.word_count
            if volumes[-1] and running + next_words > max_words:
                volumes.append([])
                running = 0
            volumes[-1].append(item)
            running += next_words
        paths: list[Path] = []
        for index, volume_items in enumerate(volumes, start=1):
            path = compiled_dir / f"{slug}_vol{index}.md"
            self._filesystem.write_text_atomic(path, self._volume_markdown(job, volume_items))
            paths.append(path)
        return paths

    def _volume_markdown(self, job: TranscriptJob, items: list[TranscriptItem]) -> str:
        lines = [f"# {job.channel_name}", "", "## Contents"]
        for item in items:
            title = item.title or item.video_id
            lines.append(f"- [{_contents_label(title)}](#{slugify(title)})")
        lines.append("")
        for item in items:
            title = item.title or item.video_id
            body = ""
            if item.path is not None:
                text = self._filesystem.read_text(item.path, max_bytes=COMPILE_READ_MAX_BYTES)
                body = _markdown_body(text)
            lines.extend([f"## {title}", "", body, ""])
        return "\n".join(lines).rstrip() + "\n"

    def _zip_raw(self, job: TranscriptJob, items: list[TranscriptItem]) -> Path:
        slug = job.output_dir.name
        zip_path = job.output_dir / f"{slug}_raw.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in items:
                if item.path is None:
                    continue
                archive.write(item.path, arcname=item.path.name)
        return zip_path

    def _worker(self) -> None:
        # Each exit re-checks its flag under `_lock` and gives up the worker slot in the
        # same critical section, so a resume or start racing it is never lost (D-306).
        try:
            while True:
                if self._stop:
                    with self._lock:
                        if self._stop:
                            self._apply_stop()
                            self._stop = False
                            self._worker_active = False
                            return
                    continue
                if self._pause:
                    with self._lock:
                        if self._pause:
                            self._pause_current()
                            self._worker_active = False
                            return
                    continue
                job = self._next_job()
                if job is None:
                    with self._lock:
                        if not self._pick_processing:
                            self._runtime = QueueRuntime(
                                queue_name="transcripts",
                                state=QueueProcessorState.Idle,
                                current_job_id=None,
                            )
                            self._worker_active = False
                            return
                    continue
                self._run_parent(job)
                self._sleep(0)
        finally:
            with self._lock:
                # Reached with the slot still held only when an exception ended the loop.
                if self._worker_active and self._thread is threading.current_thread():
                    self._worker_active = False
                    if self._stop:
                        self._runtime = QueueRuntime(
                            queue_name="transcripts",
                            state=QueueProcessorState.Idle,
                            current_job_id=None,
                        )
                        self._stop = False

    def _next_job(self) -> TranscriptJob | None:
        # Read and clear before the jobs are read, so a resume landing after this point
        # sets the flag again and the idle exit goes round (D-306).
        with self._lock:
            pick_processing = self._pick_processing
            self._pick_processing = False
        with self._uow_factory() as uow:
            jobs = uow.transcripts.list_jobs_ordered()
        for job in jobs:
            if pick_processing and job.status is TranscriptStatus.Processing:
                return job
            if job.status is TranscriptStatus.Pending:
                if pick_processing:
                    # The resumed job comes later in the queue; keep it selectable.
                    with self._lock:
                        self._pick_processing = True
                return job
        return None

    def _run_parent(self, job: TranscriptJob) -> None:
        with self._uow_factory() as uow:
            latest = uow.transcripts.get_job(job.id)
            if latest is None:
                return
            if latest.status is TranscriptStatus.Pending:
                # A message from an earlier run (a requeued Done or Failed job) would read as
                # this run's on the Processing card.
                latest = replace(
                    latest.transition(TranscriptStatus.Processing),
                    error_message=None,
                    updated_at=_now(),
                )
                uow.transcripts.save_job(latest)
                uow.commit()
            elif latest.status is not TranscriptStatus.Processing:
                return
            items = uow.transcripts.list_items(job.id)
        self._runtime = QueueRuntime(
            queue_name="transcripts",
            state=QueueProcessorState.Processing,
            current_job_id=job.id,
        )
        pending = [item for item in items if item.status is TranscriptItemStatus.Pending]
        delay = _as_float(self._settings.get("transcript", "delay_between_requests"))
        batch_size = _as_int(self._settings.get("transcript", "batch_size"))
        batch_pause = _as_float(self._settings.get("transcript", "pause_between_batches"))
        for index, item in enumerate(pending):
            if self._stop:
                self._cancel_parent(job.id)
                return
            if self._pause:
                self._pause_parent(job.id)
                return
            if index > 0:
                self._sleep(delay)
                if batch_size > 0 and index % batch_size == 0:
                    self._sleep(batch_pause)
            if self._fetch_item(job.id, item):
                # A block that outlasted its retries stops the run: no request for the next
                # video of this job or any other until Resume (MEU-116). Under `_lock`, so a
                # Resume either lands after this pause or finds the job still Processing.
                with self._lock:
                    self._pause = True
                    self._pause_parent(job.id, failure_message(TranscriptFailureCause.blocked))
                return
        with self._uow_factory() as uow:
            latest = uow.transcripts.get_job(job.id)
            items = uow.transcripts.list_items(job.id) if latest is not None else []
            if latest is None:
                return
            failed_message = _job_message(JOB_MESSAGE, items, TranscriptItemStatus.Failed)
            if failed_message is not None:
                uow.transcripts.save_job(
                    replace(
                        latest.transition(TranscriptStatus.Failed),
                        error_message=failed_message,
                        updated_at=_now(),
                    )
                )
                uow.commit()
                return
            if any(item.status is TranscriptItemStatus.Pending for item in items):
                return
            done_items = [
                item
                for item in items
                if item.status is TranscriptItemStatus.Done and item.path is not None
            ]
        paths = self._write_volumes(latest, done_items)
        _ = paths
        zip_path = self._zip_raw(latest, done_items)
        with self._uow_factory() as uow:
            current = uow.transcripts.get_job(job.id)
            if current is None:
                return
            uow.transcripts.save_job(
                replace(
                    current.transition(TranscriptStatus.Done),
                    zip_path=zip_path,
                    word_count=sum(item.word_count for item in items),
                    error_message=_job_message(
                        SKIPPED_JOB_MESSAGE, items, TranscriptItemStatus.Skipped
                    ),
                    updated_at=_now(),
                )
            )
            uow.commit()

    def _fetch_item(self, job_id: str, item: TranscriptItem) -> bool:
        """Fetch one video. True when a block outlasted `max_retries` (the item stays Pending).

        A retry message shown on the job while it waited is cleared however the fetch ends; a
        block that pauses the job then writes its own message.
        """
        try:
            return self._fetch_item_attempts(job_id, item)
        finally:
            if self._retry_message is not None:
                self._set_job_message(job_id, None, only_if=self._retry_message)
                self._retry_message = None

    def _fetch_item_attempts(self, job_id: str, item: TranscriptItem) -> bool:
        max_retries = _as_int(self._settings.get("transcript", "max_retries"))
        retry_delay = _as_float(self._settings.get("transcript", "retry_delay"))
        languages = list(TRANSCRIPT_LANGUAGES_DEFAULT)
        current = item
        while True:
            if self._stop or self._pause:
                return False
            if not self._await_request_slot():
                return False
            try:
                result = self._captions.get_transcript(current.video_id, languages)
            except TranscriptRetryableError:
                retry_count = current.retry_count + 1
                attempts = max(max_retries, 1)
                waiting = retry_message(retry_count, attempts, retry_delay)
                self._set_job_message(job_id, waiting, only_if=self._retry_message)
                self._retry_message = waiting
                # No log line per retry: a blocked video logs once, `transcript.blocked` (AC-115.7).
                self._sleep(retry_delay)
                blocked = failure_message(TranscriptFailureCause.blocked)
                if max_retries <= 0 or retry_count >= max_retries:
                    self._save_item(replace(current, retry_count=0, error_message=blocked))
                    log.error(
                        "transcript.blocked",
                        job_id=job_id,
                        video_id=current.video_id,
                        error=blocked,
                    )
                    return True
                current = replace(current, retry_count=retry_count, error_message=blocked)
                self._save_item(current)
                continue
            except DomainError as exc:
                reason = safe_reason(redact_message(str(exc))) or type(exc).__name__
                message = failure_message(TranscriptFailureCause.other, reason)
                self._save_item(
                    replace(
                        current.transition(TranscriptItemStatus.Failed),
                        error_message=message,
                        processed_at=_now(),
                    )
                )
                log.error(
                    "transcript.item_failed",
                    job_id=job_id,
                    video_id=current.video_id,
                    error=message,
                )
                return False
            break
        if self._stop or self._pause:
            return False
        if isinstance(result, TranscriptSkip):
            message = failure_message(result.cause)
            self._save_item(
                replace(
                    current.transition(TranscriptItemStatus.Skipped),
                    error_message=message,
                    processed_at=_now(),
                )
            )
            log.warning(
                "transcript.item_skipped",
                job_id=job_id,
                video_id=current.video_id,
                error=message,
                persist=True,
            )
            return False
        with self._uow_factory() as uow:
            job = uow.transcripts.get_job(job_id)
        if job is None:
            return False
        path = job.output_dir / "raw" / f"{result.video_id}.md"
        # The listed title wins; the result's title, the ID, is the fallback (TITLE_KEPT).
        title = current.title or result.title
        self._filesystem.write_text_atomic(path, _raw_markdown(job, result, title))
        if self._stop or self._pause:
            return False
        done = replace(
            replace(current, path=path).transition(TranscriptItemStatus.Done),
            title=title,
            language=result.language,
            word_count=len(result.text.split()),
            error_message=None,
            processed_at=_now(),
        )
        self._save_item(done)
        self._recompute_word_count(job_id)
        return False

    def _await_request_slot(self) -> bool:
        """Wait until a request fits `requests_per_hour` over the last `RATE_WINDOW` seconds.

        Reads the cap on every pass, so a lowered, raised or cleared cap applies to a wait
        already under way. Sleeps in slices of at most a second; False when Stop or Pause
        ends the wait.
        """
        while True:
            cap = _as_float(self._settings.get("transcript", "requests_per_hour"))
            now = self._clock()
            while self._request_starts and self._request_starts[0] <= now - RATE_WINDOW:
                self._request_starts.popleft()
            if cap <= 0 or len(self._request_starts) < cap:
                self._request_starts.append(now)
                return True
            self._sleep(min(1.0, self._request_starts[0] + RATE_WINDOW - now))
            if self._stop or self._pause:
                return False

    def _set_job_message(self, job_id: str, message: str | None, *, only_if: str | None) -> None:
        """Write a Processing job's `error_message` while it still holds `only_if`."""
        with self._uow_factory() as uow:
            job = uow.transcripts.get_job(job_id)
            if (
                job is None
                or job.status is not TranscriptStatus.Processing
                or job.error_message != only_if
            ):
                return
            uow.transcripts.save_job(replace(job, error_message=message, updated_at=_now()))
            uow.commit()

    def _save_item(self, item: TranscriptItem) -> None:
        with self._uow_factory() as uow:
            uow.transcripts.save_item(item)
            uow.commit()

    def _recompute_word_count(self, job_id: str) -> None:
        with self._uow_factory() as uow:
            job = uow.transcripts.get_job(job_id)
            if job is None:
                return
            items = uow.transcripts.list_items(job_id)
            uow.transcripts.save_job(
                replace(
                    job,
                    word_count=sum(item.word_count for item in items),
                    video_count=len(items),
                    updated_at=_now(),
                )
            )
            uow.commit()

    def _apply_stop(self) -> None:
        with self._uow_factory() as uow:
            for job in uow.transcripts.list_jobs_ordered():
                if job.status in {TranscriptStatus.Processing, TranscriptStatus.Paused}:
                    uow.transcripts.save_job(
                        replace(job.transition(TranscriptStatus.Cancelled), updated_at=_now())
                    )
            uow.commit()
        self._runtime = QueueRuntime(
            queue_name="transcripts",
            state=QueueProcessorState.Idle,
            current_job_id=None,
        )

    def _cancel_parent(self, job_id: str) -> None:
        with self._uow_factory() as uow:
            job = uow.transcripts.get_job(job_id)
            if job is not None and job.status in {
                TranscriptStatus.Processing,
                TranscriptStatus.Paused,
            }:
                uow.transcripts.save_job(
                    replace(job.transition(TranscriptStatus.Cancelled), updated_at=_now())
                )
                uow.commit()
        self._runtime = QueueRuntime(
            queue_name="transcripts",
            state=QueueProcessorState.Idle,
            current_job_id=None,
        )

    def _pause_parent(self, job_id: str, reason: str | None = None) -> None:
        """Pause the job; `reason` (a block's message) replaces its `error_message`."""
        with self._uow_factory() as uow:
            job = uow.transcripts.get_job(job_id)
            if job is not None and job.status is TranscriptStatus.Processing:
                paused = replace(job.transition(TranscriptStatus.Paused), updated_at=_now())
                if reason is not None:
                    paused = replace(paused, error_message=reason)
                uow.transcripts.save_job(paused)
                uow.commit()
        self._runtime = QueueRuntime(
            queue_name="transcripts",
            state=QueueProcessorState.Paused,
            current_job_id=None,
        )

    def _pause_current(self) -> None:
        job_id = self._runtime.current_job_id
        if job_id is not None:
            self._pause_parent(job_id)
            return
        self._runtime = QueueRuntime(
            queue_name="transcripts",
            state=QueueProcessorState.Paused,
            current_job_id=None,
        )

    def _require_job(self, uow: UnitOfWork, job_id: str) -> TranscriptJob:
        job = uow.transcripts.get_job(job_id)
        if job is None:
            raise NotFoundError(f"transcript job {job_id} not found")
        return job

    def _with_aggregates(self, uow: UnitOfWork, job: TranscriptJob) -> TranscriptJob:
        items = uow.transcripts.list_items(job.id)
        return replace(
            job,
            video_count=len(items),
            word_count=sum(item.word_count for item in items),
        )


def _job_message(
    template: str, items: list[TranscriptItem], status: TranscriptItemStatus
) -> str | None:
    """`template` over the items in `status`; `Last` is the one processed last, ties by order."""
    matching = [(index, item) for index, item in enumerate(items) if item.status is status]
    if not matching:
        return None
    earliest = datetime.min.replace(tzinfo=UTC)
    _, last = max(matching, key=lambda pair: (pair[1].processed_at or earliest, pair[0]))
    return template.format(n=len(matching), total=len(items), message=last.error_message)


def _raw_markdown(job: TranscriptJob, result: TranscriptResult, title: str) -> str:
    video_id = result.video_id
    text = result.text
    url = f"https://www.youtube.com/watch?v={video_id}"
    # Quoted, so a title holding ":" or a quote can't break the front matter (D-351).
    front = (
        "---\n"
        f"video_id: {video_id}\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"channel: {json.dumps(job.channel_name, ensure_ascii=False)}\n"
        f"url: {url}\n"
        "---\n\n"
    )
    return front + text + "\n"


def _contents_label(title: str) -> str:
    """Link text with backslashes and square brackets escaped (D-351); the anchor isn't."""
    return title.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


def _markdown_body(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("---"):
        parts = re.split(r"^---\s*$", stripped, maxsplit=2, flags=re.MULTILINE)
        if len(parts) >= 3:
            return parts[2].strip()
    return stripped
