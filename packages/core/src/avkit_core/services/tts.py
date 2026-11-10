"""TTSService — one background generation at a time, hash/preview only."""

from __future__ import annotations

import hashlib
import math
import threading
from collections.abc import Callable
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import structlog

from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
from avkit_core.domain.errors import (
    ConflictError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.progress import ConvertOptions
from avkit_core.domain.tts import (
    TEXT_PREVIEW_MAX,
    TTS_OUTPUT_FORMATS,
    TTS_SPEED_MAX,
    TTS_SPEED_MIN,
    AssetState,
    TTSJob,
    VoiceAvailability,
    VoiceConfig,
    output_stem,
    required_tts_assets,
    voice_availability,
)
from avkit_core.ports.filesystem import FilesystemPort
from avkit_core.ports.media import MediaPort
from avkit_core.ports.storage import UnitOfWork
from avkit_core.ports.tts import EspeakPort, TtsAssetPort, TTSPort
from avkit_core.services.models import asset_missing, models_directory
from avkit_core.services.prepare import TextPreparationService
from avkit_core.services.settings import SettingsService

TTS_PROGRESS_RESOLUTION = 1000
TTS_WAV_SAMPLE_RATE = 24000
TTS_MP3_CONVERT = ConvertOptions(
    codec="libmp3lame",
    bitrate_kbps=192,
    sample_rate=24000,
    channels=1,
)
UoWFactory = Callable[[], UnitOfWork]
Spawn = Callable[[Callable[[], None]], None]
RESTART_ERROR = "interrupted by restart"
log = structlog.get_logger(module="tts")


def _now() -> datetime:
    return datetime.now(UTC)


def _default_spawn(worker: Callable[[], None]) -> None:
    threading.Thread(target=worker, name="tts-generate", daemon=True).start()


def _error_text(exc: BaseException) -> str:
    detail = str(exc)
    return f"{type(exc).__name__}: {detail}" if detail else type(exc).__name__


class _Cancelled(Exception):
    """Raised from `on_progress` when the running job's cancel flag is set."""


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _free_paths(root: Path, stem: str) -> tuple[Path, Path]:
    """The WAV and MP3 paths for `stem`, numbered `-2`, `-3`... past a name already taken.

    One generation runs at a time (`_current_id`), so no job takes the name between this
    check and the write.
    """
    name = stem
    number = 1
    while (root / f"{name}.wav").exists() or (root / f"{name}.mp3").exists():
        number += 1
        name = f"{stem}-{number}"
    return root / f"{name}.wav", root / f"{name}.mp3"


class TTSService:
    """Single-job TTS owner. `generate` admits one job and runs it on a worker.

    `_lock` guards `_current_id` (the reservation), the cancel flag, `_closing` and
    `_callers`; `_idle` is its condition. Does not read source_path.
    """

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        tts: TTSPort,
        filesystem: FilesystemPort,
        media: MediaPort,
        settings: SettingsService,
        prepare: TextPreparationService,
        assets: TtsAssetPort,
        espeak: EspeakPort | None = None,
        spawn: Spawn | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._assets = assets
        self._espeak = espeak
        self._tts = tts
        self._filesystem = filesystem
        self._media = media
        self._settings = settings
        self._prepare = prepare
        self._spawn = spawn or _default_spawn
        self._current_id: str | None = None
        self._cancel_flag = False
        self._closing = False
        self._callers = 0
        self._lock = threading.Lock()
        self._idle = threading.Condition(self._lock)

    def list_voices(self) -> list[tuple[VoiceConfig, VoiceAvailability]]:
        """Return the public voice catalog, each voice with its `VOICE_REASON` (D-89)."""
        espeak = self._espeak_available()
        return [
            (voice, voice_availability(voice.lang_code, espeak))
            for voice in self._tts.list_voices()
        ]

    def _espeak_available(self) -> bool:
        """`ESPEAK_DETECT` now; no port (a host without the adapter) means absent."""
        return self._espeak is not None and self._espeak.status().available

    def prepare(
        self,
        text: str,
        enabled_steps: list[str],
        chunk_max_chars: int | None = None,
    ) -> str:
        return self._prepare.prepare(text, enabled_steps, chunk_max_chars)

    def get_status(self, job_id: str) -> TTSJob:
        with self._uow_factory() as uow:
            job = uow.tts_jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"tts job {job_id} not found")
        return job

    def cancel(self, job_id: str) -> None:
        """Flag the running job for cancellation; any other id changes nothing."""
        with self._lock:
            if job_id == self._current_id:
                self._cancel_flag = True

    def wait_idle(self, timeout: float) -> bool:
        """True once no job is reserved and no `generate` call is in flight."""
        with self._idle:
            return self._idle.wait_for(
                lambda: self._current_id is None and self._callers == 0, timeout
            )

    def recover_stale_processing(self) -> None:
        """Fail every `Generating` row left by a previous process."""
        with self._uow_factory() as uow:
            for job in uow.tts_jobs.list_by_status(TTSStatus.Generating):
                uow.tts_jobs.save(
                    replace(
                        job.transition(TTSStatus.Failed),
                        error_message=RESTART_ERROR,
                        updated_at=_now(),
                    )
                )
            uow.commit()

    def stop_processing(self, timeout: float = 10.0) -> bool:
        """Refuse new jobs, cancel the running one and wait up to `timeout` for idle."""
        with self._lock:
            self._closing = True
            job_id = self._current_id
            if job_id is not None:
                self._cancel_flag = True
        idle = self.wait_idle(timeout)
        if not idle:
            log.warning("tts.stop_timeout", job_id=job_id, timeout=timeout)
        return idle

    def generate(
        self,
        text: str,
        voice: str,
        speed: float,
        format: MediaFormat,
        enabled_steps: list[str],
        source_kind: TTSSourceKind,
        source_path: Path | None,
    ) -> TTSJob:
        """Check the request, admit one `Generating` job and start its worker."""
        with self._lock:
            if self._closing:
                raise ConflictError("the TTS service is stopping")
            self._callers += 1
        try:
            return self._admit_and_spawn(
                text, voice, speed, format, enabled_steps, source_kind, source_path
            )
        finally:
            with self._idle:
                self._callers -= 1
                self._idle.notify_all()

    def _admit_and_spawn(
        self,
        text: str,
        voice: str,
        speed: float,
        format: MediaFormat,
        enabled_steps: list[str],
        source_kind: TTSSourceKind,
        source_path: Path | None,
    ) -> TTSJob:
        if not isinstance(text, str) or text.strip() == "":
            raise ValidationError("text must be a non-empty str")
        if not isinstance(speed, int | float) or isinstance(speed, bool):
            raise ValidationError("speed must be a number")
        if speed < TTS_SPEED_MIN or speed > TTS_SPEED_MAX:
            raise ValidationError("speed is out of range")
        if format not in TTS_OUTPUT_FORMATS:
            raise ValidationError("format must be one of TTS_OUTPUT_FORMATS")
        status = self._tts.get_model_status()
        if not status.is_loaded:
            raise ConflictError("a TTS model must be loaded")
        voices = {item.voice_id: item for item in self._tts.list_voices()}
        config = voices.get(voice)
        if config is None:
            raise ValidationError("voice is not available")
        # `VOICE_AVAILABLE_409`, ahead of the asset check and the job row (`ASSET_409_ORDER`).
        availability = voice_availability(config.lang_code, self._espeak_available())
        if availability.reason is not None:
            raise ConflictError(f"voice unavailable: {voice} ({availability.reason.value})")
        variant_id = status.variant_id
        self._require_assets(variant_id, voice, enabled_steps)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        preview = text[:TEXT_PREVIEW_MAX]
        job = TTSJob(
            id=str(uuid4()),
            source_kind=source_kind,
            source_path=source_path,
            text_hash=digest,
            text_preview=preview,
            voice=voice,
            speed=float(speed),
            format=format,
            status=TTSStatus.Pending,
            output_path=None,
            segments_total=TTS_PROGRESS_RESOLUTION,
            segments_done=0,
            error_message=None,
            created_at=_now(),
            updated_at=_now(),
        )
        job = replace(job.transition(TTSStatus.Generating), updated_at=_now())
        with self._lock:
            if self._closing:
                raise ConflictError("the TTS service is stopping")
            if self._current_id is not None:
                raise ConflictError("a TTS generation is already in progress")
            with self._uow_factory() as uow:
                uow.tts_jobs.add(job)
                uow.commit()
            self._current_id = job.id
            self._cancel_flag = False
        log.info("tts.generate", job_id=job.id, voice=voice, variant=variant_id)

        def worker() -> None:
            self._work(job.id, text, config, float(speed), format, enabled_steps)

        try:
            self._spawn(worker)
        except Exception as exc:
            # The worker never ran: release the reservation, then re-raise (500).
            self._finish(job.id, TTSStatus.Failed, error=_error_text(exc))
            raise
        return self.get_status(job.id)

    def _work(
        self,
        job_id: str,
        text: str,
        config: VoiceConfig,
        speed: float,
        format: MediaFormat,
        enabled_steps: list[str],
    ) -> None:
        """Run one admitted job to a terminal state. Never raises."""
        outcome = TTSStatus.Failed
        output: Path | None = None
        partials: tuple[Path, ...] = ()
        error = "generation failed"

        def on_progress(fraction: float) -> None:
            if self._cancel_flag:
                raise _Cancelled
            if not _is_finite_number(fraction):
                return
            number = float(fraction)
            if number < 0.0 or number > 1.0:
                raise ValidationError("progress fraction must be between 0.0 and 1.0")
            done = min(TTS_PROGRESS_RESOLUTION, max(0, round(number * TTS_PROGRESS_RESOLUTION)))
            with self._uow_factory() as uow:
                latest = uow.tts_jobs.get(job_id)
                if latest is None:
                    return
                uow.tts_jobs.save(
                    replace(
                        latest,
                        segments_total=TTS_PROGRESS_RESOLUTION,
                        segments_done=done,
                        updated_at=_now(),
                    )
                )
                uow.commit()

        try:
            if self._cancel_flag:
                outcome = TTSStatus.Cancelled
                return
            cleaned = self._prepare.prepare(text, enabled_steps)
            samples = self._tts.generate(cleaned, config, speed, on_progress)
            root = self._output_root()
            wav_path, mp3_path = _free_paths(root, output_stem(text, config.voice_id))
            partials = (wav_path, mp3_path)
            self._filesystem.write_audio_wav(wav_path, samples, TTS_WAV_SAMPLE_RATE)
            if self._cancel_flag:
                outcome = TTSStatus.Cancelled
                return
            output = wav_path
            if format is MediaFormat.MP3:
                output = mp3_path
                self._media.convert(wav_path, output, TTS_MP3_CONVERT)
                if self._cancel_flag:
                    outcome = TTSStatus.Cancelled
                    return
                # The WAV was only the encoder's input (rc.3 F7); a failed unlink is logged.
                self._remove_partial(job_id, (wav_path,))
            outcome = TTSStatus.Done
        except _Cancelled:
            outcome = TTSStatus.Cancelled
        except DomainError as exc:
            error = str(exc) or "generation failed"
            log.warning("tts.generate_failed", job_id=job_id, error=error, exc_info=True)
        except Exception as exc:
            error = _error_text(exc)
            log.warning("tts.generate_failed", job_id=job_id, error=error, exc_info=True)
        finally:
            try:
                self._finish(job_id, outcome, output=output, partials=partials, error=error)
            except Exception:
                log.error("tts.finish_failed", job_id=job_id, exc_info=True)

    def _finish(
        self,
        job_id: str,
        outcome: TTSStatus,
        *,
        output: Path | None = None,
        partials: tuple[Path, ...] = (),
        error: str | None = None,
    ) -> None:
        """Write the terminal state and release the reservation, all under `_lock`."""
        with self._idle:
            if self._current_id != job_id:
                return
            try:
                if self._cancel_flag or outcome is TTSStatus.Cancelled:
                    self._remove_partial(job_id, partials)
                    self._mark(job_id, TTSStatus.Cancelled)
                elif outcome is TTSStatus.Done and output is not None:
                    self._finish_done(job_id, output)
                    log.info("tts.generate_done", job_id=job_id, output=str(output))
                else:
                    self._remove_partial(job_id, partials)
                    self._mark(job_id, TTSStatus.Failed, error or "generation failed")
            finally:
                self._current_id = None
                self._cancel_flag = False
                self._idle.notify_all()

    def _output_root(self) -> Path:
        return Path(str(self._settings.get("tts", "output_path"))).expanduser()

    def _remove_partial(self, job_id: str, partials: tuple[Path, ...]) -> None:
        """Unlink the WAV and MP3 paths this job captured when present; an unlink error is logged.

        The paths come from the job's own run, never from a later `tts.output_path`.
        """
        for path in partials:
            try:
                if path.is_file():
                    path.unlink()
            except OSError as exc:
                log.warning("tts.cleanup_failed", job_id=job_id, path=str(path), error=str(exc))

    def _require_assets(
        self,
        variant_id: str | None,
        voice: str,
        enabled_steps: list[str],
    ) -> None:
        """Raise `ASSET_MISSING_ERROR` for the first asset the run needs but lacks.

        Runs before the job row exists, so a refusal leaves no row and no audio file.
        """
        if variant_id is None:
            raise ConflictError("a TTS model must be loaded")
        with self._uow_factory() as uow:
            variant = uow.models.get(variant_id)
        if variant is None:
            raise NotFoundError(f"model variant {variant_id} not found")
        models_dir = models_directory(self._settings)
        for asset in required_tts_assets(variant.format, voice, enabled_steps):
            if self._assets.state(asset, models_dir) is not AssetState.READY:
                raise asset_missing(asset)

    def _finish_done(self, job_id: str, output_path: Path) -> TTSJob:
        with self._uow_factory() as uow:
            latest = uow.tts_jobs.get(job_id)
            if latest is None:
                raise NotFoundError(f"tts job {job_id} not found")
            updated = replace(
                latest.transition(TTSStatus.Done),
                output_path=output_path,
                updated_at=_now(),
            )
            uow.tts_jobs.save(updated)
            uow.commit()
        return updated

    def _mark(self, job_id: str, status: TTSStatus, error: str | None = None) -> TTSJob:
        with self._uow_factory() as uow:
            latest = uow.tts_jobs.get(job_id)
            if latest is None:
                raise NotFoundError(f"tts job {job_id} not found")
            updated = replace(
                latest.transition(status),
                error_message=error,
                updated_at=_now(),
            )
            uow.tts_jobs.save(updated)
            uow.commit()
        return updated
