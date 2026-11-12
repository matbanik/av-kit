"""DownloadService — queue commands, SABR session, and one worker thread."""

from __future__ import annotations

import math
import re
import threading
import time
import unicodedata
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog

from avkit_core.domain.download import (
    ANSI_CSI,
    BLOCKER_REMEDIATION,
    DROPPED_CATEGORIES,
    CookieTestResult,
    DownloadArchiveEntry,
    DownloadJob,
    DownloadOptions,
    PlaylistInfo,
    SABRStatus,
    VideoInfo,
    clean_line,
    download_failure_message,
)
from avkit_core.domain.enums import (
    SABR_RESTRICTED_AUDIO,
    AudioFormat,
    DownloadFailureCause,
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
    DownloadCancelledError,
    DownloadFailedError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.queue import QueueRuntime
from avkit_core.domain.transcript import replace_links, safe_reason
from avkit_core.domain.wire import AUDIO_WIRE_MAP, COOKIE_MODE_WIRES, QUALITY_WIRE_MAP
from avkit_core.ports.storage import UnitOfWork
from avkit_core.ports.youtube import YouTubePort
from avkit_core.services import health
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


#: SCRUB_LINE marks: a whitespace character other than U+0020 becomes a tab, and an ANSI code
#: or a `Cc`, `Cf` or `Cs` code point a NUL, so the home match can step over either.
_SPLIT_GAP = "[\t\x00]*"
_HOME_SEPARATORS = re.compile(r"[\\/]+")


def _mark_splits(text: str) -> str:
    text = ANSI_CSI.sub("\x00", text)
    marked: list[str] = []
    for char in text:
        if char.isspace() and char != " ":
            marked.append("\t")
        elif unicodedata.category(char) in DROPPED_CATEGORIES:
            marked.append("\x00")
        else:
            marked.append(char)
    return "".join(marked)


def _scrub_split_home(marked: str) -> str:
    """`marked` with the home folder as "~", matched as `scrub_home` matches but across marks.

    `health.home_folder` is read through the module at each call, so a test's patch reaches it.
    """
    home = health.home_folder().rstrip("\\/")
    if not _HOME_SEPARATORS.search(home):
        return marked

    def spread(part: str) -> str:
        return _SPLIT_GAP.join(re.escape(char) for char in part)

    separator = "(?:" + r"\\" + _SPLIT_GAP + r"\\" + r"|\\|/)"
    body = (_SPLIT_GAP + separator + _SPLIT_GAP).join(
        spread(part) for part in _HOME_SEPARATORS.split(home)
    )
    pattern = r"(?<![\w\\/.~-])" + body + r"(?=[\t\x00]*[\\/'\"]|[\t\x00 ]*$)"
    flags = re.IGNORECASE if health.HOME_IGNORES_CASE else 0
    return re.sub(pattern, "~", marked, flags=flags)


def _scrub(text: str) -> str:
    return health.redact_message(replace_links(health.scrub_home(text)))


def scrub_line(text: str) -> str:
    """The text a site keeps from one line of yt-dlp's text (`SCRUB_LINE`, MEU-137, D-627).

    The home folder is matched before any character is removed, then the line is cleaned two
    ways: `readable` keeps a split as a space, `joined` closes it. A needle or link split by a
    whitespace or control character is whole in `joined`, so `joined` is scrubbed when that
    finds something; otherwise the readable form is kept.
    """
    homed = _scrub_split_home(_mark_splits(text))
    readable = clean_line(homed)
    joined = clean_line(homed.replace("\t", ""))
    scrubbed = _scrub(joined)
    return scrubbed if scrubbed != joined else _scrub(readable)


_LINE_BREAKS = re.compile(r"\r\n|\r|\n")


def first_line(text: str) -> str:
    """The first line of `text` that `clean_line` leaves non-empty, as written (D-639).

    Only CR, LF and CRLF end a line, so a U+2028, U+0085 or other split inside a secret or
    the home folder stays in the line for `scrub_line` to close. Returns "" when no line has
    text. Never raises.
    """
    for line in _LINE_BREAKS.split(text):
        if clean_line(line):
            return line
    return ""


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
        # ADD_OPTS (D-646): the add-time extract runs with the options the download will use,
        # read fresh from the settings, so a missing cookie file fails the add (422).
        options = self._download_options(quality, audio_only, audio_format)
        info = self._coordinator.extract_info(url.strip(), options=options)
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
        try:
            status = self._youtube.check_sabr_status()
        except Exception as exc:
            # SABR_LOG: one ERROR line with the scrubbed text; the error goes on unchanged.
            log.error("download.sabr_check", error=scrub_line(str(exc)))
            raise
        if status.mode is SABRMode.Active:
            # SABR_RESULT: the stored status keeps the phrase the port matched.
            self._sabr = SABRStatus(
                mode=SABRMode.Active,
                source=SABRSource.Detected,
                checked_at=_now(),
                matched_phrase=status.matched_phrase,
            )
            self.apply_lock()
            detail = (
                "Active, no phrase recorded"
                if status.matched_phrase is None
                else f"Active, matched '{status.matched_phrase}'"
            )
        else:
            self._sabr = status
            detail = "Inactive, no phrase matched"
        log.info("download.sabr_check", detail=detail)
        return self._sabr

    def force_sabr(self) -> SABRStatus:
        self._sabr = SABRStatus(
            mode=SABRMode.Active,
            source=SABRSource.Forced,
            checked_at=_now(),
        )
        self.apply_lock()
        log.info("download.sabr_force", detail="Active, forced")
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
        log.info("download.sabr_clear", detail="Inactive, cleared")
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
        return self._download_options(job.quality, job.audio_only, job.audio_format)

    def _download_options(
        self, quality: QualityPreset, audio_only: bool, audio_format: AudioFormat
    ) -> DownloadOptions:
        """The download's options from its own fields and the cookie settings, read fresh."""
        raw_path = str(self._settings.get("downloader", "path"))
        cookie_mode = str(self._settings.get("downloader", "cookie_mode"))
        browser = str(self._settings.get("downloader", "cookie_browser")) or None
        profile = str(self._settings.get("downloader", "cookie_browser_profile")) or None
        cookie_path = str(self._settings.get("downloader", "cookie_file_path"))
        return DownloadOptions(
            quality=quality,
            audio_only=audio_only,
            audio_format=audio_format,
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
        # FAILURE_LOG (D-633, D-634, D-638): started before the port call, done after the Done
        # commit, and one failed line per failure, Cancelled excepted.
        log.info("download.started", job_id=job.id, video_id=job.video_id)
        try:
            result = self._youtube.download(job.url, self._options_from(job))
        except AgeRestrictedError as exc:
            stored = str(exc)
            self._finish(job.id, DownloadStatus.AgeRestricted, error=stored)
            lines = stored.splitlines()
            log.error(
                "download.failed",
                job_id=job.id,
                video_id=job.video_id,
                error=stored,
                detail=scrub_line(lines[0] if lines else ""),
            )
            return
        except DownloadCancelledError:
            self._finish(job.id, DownloadStatus.Cancelled)
            self._cancel = True
            return
        except Exception as exc:
            if isinstance(exc, DownloadFailedError):
                cause, raw = exc.cause, exc.detail
            else:
                raw = first_line(str(exc))
                cause = (
                    DownloadFailureCause.cookies
                    if isinstance(exc, CookieTestError)
                    else DownloadFailureCause.other
                )
            detail = scrub_line(raw)
            reason = None
            if cause is DownloadFailureCause.other:
                reason = safe_reason(detail) or type(exc).__name__
            stored = download_failure_message(cause, reason)
            self._finish(job.id, DownloadStatus.Failed, error=stored)
            log.error(
                "download.failed",
                job_id=job.id,
                video_id=job.video_id,
                error=stored,
                detail=detail,
            )
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
        log.info("download.done", job_id=job.id, video_id=job.video_id)
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
