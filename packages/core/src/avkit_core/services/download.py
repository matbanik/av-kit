"""DownloadService — queue commands, SABR session, and one worker thread."""

from __future__ import annotations

import math
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog

from avkit_core.domain.download import (
    BLOCKER_REMEDIATION,
    CookieTestResult,
    DownloadArchiveEntry,
    DownloadJob,
    DownloadOptions,
    PlaylistInfo,
    SABRStatus,
    VideoInfo,
)
from avkit_core.domain.enums import (
    SABR_RESTRICTED_AUDIO,
    AudioFormat,
    DownloadStatus,
    QualityPreset,
    QueueProcessorState,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import (
    AgeRestrictedError,
    ConflictError,
    CookieTestError,
    DomainError,
    DownloadCancelledError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.queue import QueueRuntime
from avkit_core.domain.wire import AUDIO_WIRE_MAP, COOKIE_MODE_WIRES, QUALITY_WIRE_MAP
from avkit_core.ports.storage import UnitOfWork
from avkit_core.ports.youtube import YouTubePort
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.settings import SettingsService

ARCHIVE_EXTRACTOR = "youtube"
SABR_COMPAT_QUALITY = frozenset({QualityPreset.P360, QualityPreset.Lowest})
SABR_COMPAT_AUDIO = SABR_RESTRICTED_AUDIO
PROGRESS_COMMIT_INTERVAL_S = 1.0
# `VIDEO_TARGET` (D-392): a list item's job stores its own video's URL, not the list's.
WATCH_URL_PREFIX = "https://www.youtube.com/watch?v="

UoWFactory = Callable[[], UnitOfWork]
log = structlog.get_logger(module="download")


def _now() -> datetime:
    return datetime.now(UTC)


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _incompatible(job: DownloadJob) -> bool:
    if job.audio_only:
        return job.audio_format not in SABR_COMPAT_AUDIO
    return job.quality not in SABR_COMPAT_QUALITY


class DownloadService:
    """Downloader queue owner. Hexagonal: ports and UoW factory only."""

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        youtube: YouTubePort,
        coordinator: ExtractCoordinator,
        settings: SettingsService,
        sleep: Callable[[float], None] | None = None,
        clock: Callable[[], float] | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._youtube = youtube
        self._coordinator = coordinator
        self._settings = settings
        self._sleep = sleep or time.sleep
        self._clock = clock or time.monotonic
        self._runtime = QueueRuntime(
            queue_name="downloads",
            state=QueueProcessorState.Idle,
            current_job_id=None,
        )
        self._sabr = SABRStatus(mode=SABRMode.Inactive, source=None, checked_at=None)
        self._pause = False
        self._cancel = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._last_progress_at = 0.0

    def on_download_progress(
        self,
        downloaded: int,
        total: int | None,
        speed: float | None,
    ) -> None:
        if not _is_finite_number(downloaded):
            return
        if total is not None and not _is_finite_number(total):
            return
        if speed is not None and not _is_finite_number(speed):
            return
        now = self._clock()
        if now - self._last_progress_at < PROGRESS_COMMIT_INTERVAL_S and total not in {0, None}:
            return
        self._last_progress_at = now
        job_id = self._runtime.current_job_id
        if job_id is None:
            return
        progress = 0.0
        if total is not None and total > 0:
            progress = min(1.0, max(0.0, float(downloaded) / float(total)))
        with self._uow_factory() as uow:
            job = uow.downloads.get(job_id)
            if job is None:
                return
            uow.downloads.save(
                DownloadJob(
                    **{
                        **job.__dict__,
                        "progress": progress,
                        "speed_bps": float(speed) if speed is not None else None,
                        "file_size": int(total) if total is not None else job.file_size,
                        "updated_at": _now(),
                    }
                )
            )
            uow.commit()

    def should_stop(self) -> bool:
        return self._cancel

    def get_queue(self) -> list[DownloadJob]:
        with self._uow_factory() as uow:
            return uow.downloads.list_ordered()

    def get_job(self, job_id: str) -> DownloadJob:
        with self._uow_factory() as uow:
            job = uow.downloads.get(job_id)
        if job is None:
            raise NotFoundError(f"download job {job_id} not found")
        return job

    def get_processor_state(self) -> QueueRuntime:
        return self._runtime

    def get_sabr_status(self) -> SABRStatus:
        return self._sabr

    def add_to_queue(
        self,
        url: str,
        quality: QualityPreset,
        audio_only: bool,
        audio_format: AudioFormat,
    ) -> list[DownloadJob]:
        if not isinstance(url, str) or url.strip() == "":
            raise ValidationError("url must be a non-empty str")
        log.info("add_to_queue_extract_start", url=url.strip())
        info = self._coordinator.extract_info(url.strip())
        log.info(
            "add_to_queue_extract_done",
            info_type=type(info).__name__,
        )
        items: list[tuple[str, str, str]] = []
        if isinstance(info, VideoInfo):
            items.append((url.strip(), info.video_id, info.title or info.video_id))
        elif isinstance(info, PlaylistInfo):
            for video_id in info.video_ids:
                items.append((f"{WATCH_URL_PREFIX}{video_id}", video_id, video_id))
        else:
            raise ValidationError("extract_info returned an unknown type")
        created: list[DownloadJob] = []
        with self._uow_factory() as uow:
            existing = {job.video_id for job in uow.downloads.list_ordered()}
            position = len(uow.downloads.list_ordered())
            archive_on = bool(self._settings.get("downloader", "archive_tracking"))
            for item_url, video_id, title in items:
                if video_id in existing:
                    log.warning("skip duplicate video_id")
                    continue
                existing.add(video_id)
                archived = (
                    archive_on and uow.archive.get(ARCHIVE_EXTRACTOR, video_id) is not None
                )
                status = DownloadStatus.Skipped if archived else DownloadStatus.Pending
                if (
                    not archived
                    and self._sabr.mode is SABRMode.Active
                    and _incompatible(
                        DownloadJob(
                            id=str(uuid4()),
                            url=item_url,
                            video_id=video_id,
                            title=title,
                            quality=quality,
                            audio_only=audio_only,
                            audio_format=audio_format,
                            status=DownloadStatus.Pending,
                            progress=0.0,
                            speed_bps=None,
                            eta_seconds=None,
                            file_size=None,
                            file_path=None,
                            error_message=None,
                            queue_position=position,
                            created_at=_now(),
                            updated_at=_now(),
                        )
                    )
                ):
                    status = DownloadStatus.QualityBlocked
                job = DownloadJob(
                    id=str(uuid4()),
                    url=item_url,
                    video_id=video_id,
                    title=title,
                    quality=quality,
                    audio_only=audio_only,
                    audio_format=audio_format,
                    status=status,
                    progress=0.0,
                    speed_bps=None,
                    eta_seconds=None,
                    file_size=None,
                    file_path=None,
                    error_message=None,
                    queue_position=position,
                    created_at=_now(),
                    updated_at=_now(),
                )
                uow.downloads.add(job)
                created.append(job)
                position += 1
            uow.commit()
        return created

    def start_processing(self) -> None:
        with self._lock:
            if self._runtime.state is QueueProcessorState.Processing:
                return
            self._pause = False
            self._cancel = False
            self._runtime = QueueRuntime(
                queue_name="downloads",
                state=QueueProcessorState.Processing,
                current_job_id=self._runtime.current_job_id,
            )
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(target=self._worker, daemon=True)
                self._thread.start()

    def pause_processing(self) -> None:
        self._pause = True

    def resume_processing(self) -> None:
        if self._runtime.state is not QueueProcessorState.Paused:
            raise ConflictError("resume_processing requires Paused")
        self.start_processing()

    def cancel_processing(self) -> None:
        self._cancel = True

    def stop_processing(self) -> None:
        self.cancel_processing()

    def remove_from_queue(self, job_id: str) -> None:
        with self._uow_factory() as uow:
            if uow.downloads.get(job_id) is None:
                raise NotFoundError(f"download job {job_id} not found")
            uow.downloads.delete(job_id)
            uow.commit()

    def clear_queue(self) -> None:
        with self._uow_factory() as uow:
            uow.downloads.delete_all()
            uow.commit()

    def reorder_queue(self, job_ids: list[str]) -> None:
        with self._uow_factory() as uow:
            current = [job.id for job in uow.downloads.list_ordered()]
            if sorted(job_ids) != sorted(current):
                raise ValidationError("reorder_queue requires a permutation of current ids")
            uow.downloads.reorder(job_ids)
            uow.commit()

    def _with_current_defaults(self, job: DownloadJob) -> DownloadJob:
        """Return `job` carrying the downloader defaults Apply Defaults would write."""
        return DownloadJob(
            **{
                **job.__dict__,
                "quality": QUALITY_WIRE_MAP[str(self._settings.get("downloader", "quality"))],
                "audio_format": AUDIO_WIRE_MAP[
                    str(self._settings.get("downloader", "audio_format"))
                ],
                "audio_only": bool(self._settings.get("downloader", "audio_only")),
            }
        )

    def reset_failed(self, job_id: str) -> DownloadJob:
        with self._uow_factory() as uow:
            job = uow.downloads.get(job_id)
            if job is None:
                raise NotFoundError(f"download job {job_id} not found")
            if job.status is DownloadStatus.QualityBlocked:
                # The lock is re-evaluated here because _run_one never re-runs
                # apply_lock: re-queueing a still-incompatible job would hand the
                # worker the very quality the lock rejected.
                candidate = self._with_current_defaults(job)
                if self._sabr.mode is SABRMode.Active and _incompatible(candidate):
                    # Nothing about the job changes; the save exists so the row the
                    # user is looking at when the refusal lands carries its reason.
                    uow.downloads.save(job)
                    uow.commit()
                    raise ConflictError(
                        "download is still blocked; change "
                        + BLOCKER_REMEDIATION[DownloadStatus.QualityBlocked]
                    )
                updated = candidate.reset_failed()
            else:
                updated = job.reset_failed()
            uow.downloads.save(updated)
            uow.commit()
        return updated

    def check_sabr(self) -> SABRStatus:
        status = self._youtube.check_sabr_status()
        if status.mode is SABRMode.Active:
            self._sabr = SABRStatus(
                mode=SABRMode.Active,
                source=SABRSource.Detected,
                checked_at=_now(),
            )
            self.apply_lock()
        else:
            self._sabr = status
        return self._sabr

    def force_sabr(self) -> SABRStatus:
        self._sabr = SABRStatus(
            mode=SABRMode.Active,
            source=SABRSource.Forced,
            checked_at=_now(),
        )
        self.apply_lock()
        return self._sabr

    def clear_sabr(self) -> SABRStatus:
        self._sabr = SABRStatus(mode=SABRMode.Inactive, source=None, checked_at=_now())
        with self._uow_factory() as uow:
            for job in uow.downloads.list_ordered():
                if job.status is DownloadStatus.QualityBlocked:
                    uow.downloads.save(
                        DownloadJob(
                            **{
                                **job.transition(DownloadStatus.Pending).__dict__,
                                "updated_at": _now(),
                            }
                        )
                    )
            uow.commit()
        return self._sabr

    def apply_lock(self) -> None:
        with self._uow_factory() as uow:
            for job in uow.downloads.list_ordered():
                if job.status not in {DownloadStatus.Pending, DownloadStatus.QualityBlocked}:
                    continue
                if not _incompatible(job):
                    continue
                blocked = (
                    job
                    if job.status is DownloadStatus.QualityBlocked
                    else job.transition(DownloadStatus.QualityBlocked)
                )
                uow.downloads.save(
                    DownloadJob(**{**blocked.__dict__, "updated_at": _now()})
                )
            uow.commit()

    def apply_defaults_to_pending(self) -> int:
        quality = QUALITY_WIRE_MAP[str(self._settings.get("downloader", "quality"))]
        audio_format = AUDIO_WIRE_MAP[str(self._settings.get("downloader", "audio_format"))]
        audio_only = bool(self._settings.get("downloader", "audio_only"))
        count = 0
        with self._uow_factory() as uow:
            for job in uow.downloads.list_ordered():
                if job.status not in {DownloadStatus.Pending, DownloadStatus.QualityBlocked}:
                    continue
                uow.downloads.save(
                    DownloadJob(
                        **{
                            **job.__dict__,
                            "quality": quality,
                            "audio_format": audio_format,
                            "audio_only": audio_only,
                            "updated_at": _now(),
                        }
                    )
                )
                count += 1
            uow.commit()
        return count

    def test_cookies(
        self,
        mode: str,
        browser: str | None,
        profile: str | None,
        cookie_file: Path | None,
    ) -> CookieTestResult:
        if mode not in COOKIE_MODE_WIRES:
            raise ValidationError("cookie mode is not a known wire value")
        try:
            return self._youtube.test_cookies(mode, browser, profile, cookie_file)
        except CookieTestError:
            raise
        except OSError as exc:
            raise CookieTestError(str(exc) or "cookie test failed") from exc

    def _options_from(self, job: DownloadJob) -> DownloadOptions:
        raw_path = str(self._settings.get("downloader", "path"))
        cookie_mode = str(self._settings.get("downloader", "cookie_mode"))
        browser = str(self._settings.get("downloader", "cookie_browser")) or None
        profile = str(self._settings.get("downloader", "cookie_browser_profile")) or None
        cookie_path = str(self._settings.get("downloader", "cookie_file_path"))
        return DownloadOptions(
            quality=job.quality,
            audio_only=job.audio_only,
            audio_format=job.audio_format,
            output_dir=Path(raw_path).expanduser(),
            mode=cookie_mode,
            browser=browser,
            profile=profile,
            cookie_file=Path(cookie_path) if cookie_path else None,
        )

    def _worker(self) -> None:
        try:
            while True:
                if self._cancel:
                    self._cancel_inflight()
                    break
                if self._pause:
                    self._runtime = QueueRuntime(
                        queue_name="downloads",
                        state=QueueProcessorState.Paused,
                        current_job_id=None,
                    )
                    break
                job = self._next_pending()
                if job is None:
                    self._runtime = QueueRuntime(
                        queue_name="downloads",
                        state=QueueProcessorState.Idle,
                        current_job_id=None,
                    )
                    break
                if self._archive_skip(job):
                    continue
                self._run_one(job)
                self._sleep(0)
        finally:
            if self._cancel:
                self._runtime = QueueRuntime(
                    queue_name="downloads",
                    state=QueueProcessorState.Idle,
                    current_job_id=None,
                )
                self._cancel = False

    def _next_pending(self) -> DownloadJob | None:
        with self._uow_factory() as uow:
            pending = [
                job
                for job in uow.downloads.list_ordered()
                if job.status is DownloadStatus.Pending
            ]
        return pending[0] if pending else None

    def _archive_skip(self, job: DownloadJob) -> bool:
        if not bool(self._settings.get("downloader", "archive_tracking")):
            return False
        with self._uow_factory() as uow:
            latest = uow.downloads.get(job.id)
            if latest is None or latest.status is not DownloadStatus.Pending:
                return True
            if uow.archive.get(ARCHIVE_EXTRACTOR, latest.video_id) is None:
                return False
            uow.downloads.save(
                DownloadJob(
                    **{
                        **latest.transition(DownloadStatus.Skipped).__dict__,
                        "updated_at": _now(),
                    }
                )
            )
            uow.commit()
        return True

    def _run_one(self, job: DownloadJob) -> None:
        with self._uow_factory() as uow:
            latest = uow.downloads.get(job.id)
            if latest is None or latest.status is not DownloadStatus.Pending:
                return
            downloading = DownloadJob(
                **{**latest.transition(DownloadStatus.Downloading).__dict__, "updated_at": _now()}
            )
            uow.downloads.save(downloading)
            uow.commit()
        self._runtime = QueueRuntime(
            queue_name="downloads",
            state=QueueProcessorState.Processing,
            current_job_id=job.id,
        )
        try:
            result = self._youtube.download(job.url, self._options_from(job))
        except AgeRestrictedError as exc:
            self._finish(job.id, DownloadStatus.AgeRestricted, error=str(exc))
            return
        except DownloadCancelledError:
            self._finish(job.id, DownloadStatus.Cancelled)
            self._cancel = True
            return
        except DomainError as exc:
            self._finish(job.id, DownloadStatus.Failed, error=str(exc))
            return
        except Exception as exc:
            self._finish(job.id, DownloadStatus.Failed, error=str(exc))
            return
        if result.sabr_detected:
            self._sabr = SABRStatus(
                mode=SABRMode.Active,
                source=SABRSource.Detected,
                checked_at=_now(),
            )
            self.apply_lock()
        with self._uow_factory() as uow:
            latest = uow.downloads.get(job.id)
            if latest is None:
                return
            done = DownloadJob(
                **{
                    **latest.transition(DownloadStatus.Done).__dict__,
                    "file_path": result.file_path,
                    "file_size": result.file_size,
                    "progress": 1.0,
                    "updated_at": _now(),
                    "received_height": None if latest.audio_only else result.height,
                }
            )
            uow.downloads.save(done)
            uow.archive.add(
                DownloadArchiveEntry(
                    extractor=ARCHIVE_EXTRACTOR,
                    video_id=result.video_id,
                    title=result.title,
                    recorded_at=_now(),
                )
            )
            uow.commit()
        self._runtime = QueueRuntime(
            queue_name="downloads",
            state=self._runtime.state,
            current_job_id=None,
        )

    def _finish(self, job_id: str, status: DownloadStatus, error: str | None = None) -> None:
        with self._uow_factory() as uow:
            latest = uow.downloads.get(job_id)
            if latest is None:
                return
            uow.downloads.save(
                DownloadJob(
                    **{
                        **latest.transition(status).__dict__,
                        "error_message": error,
                        "updated_at": _now(),
                    }
                )
            )
            uow.commit()
        self._runtime = QueueRuntime(
            queue_name="downloads",
            state=self._runtime.state,
            current_job_id=None,
        )

    def _cancel_inflight(self) -> None:
        job_id = self._runtime.current_job_id
        if job_id is None:
            return
        with self._uow_factory() as uow:
            latest = uow.downloads.get(job_id)
            if latest is None:
                return
            if latest.status is DownloadStatus.Downloading:
                uow.downloads.save(
                    DownloadJob(
                        **{
                            **latest.transition(DownloadStatus.Cancelled).__dict__,
                            "updated_at": _now(),
                        }
                    )
                )
                uow.commit()
