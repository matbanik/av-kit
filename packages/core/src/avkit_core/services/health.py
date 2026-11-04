"""HealthService — sole seq owner, redacted console ring, optional log file."""

from __future__ import annotations

import json
import sys
import threading
from collections import deque
from collections.abc import Callable, MutableMapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

from avkit_core.domain.errors import ValidationError
from avkit_core.domain.health import ConsoleEvent, DependencyHealth, HealthLiveness
from avkit_core.domain.tts import (
    ESPEAK_UNAVAILABLE,
    AssetState,
    ModelDownloadRuntime,
    TtsAsset,
)
from avkit_core.domain.wire import LOG_LEVEL_WIRES
from avkit_core.ports.media import MediaPort
from avkit_core.ports.storage import UnitOfWork
from avkit_core.ports.tts import EspeakPort, TtsAssetPort
from avkit_core.ports.youtube import YouTubePort
from avkit_core.services.models import models_directory
from avkit_core.services.settings import SettingsService

CONSOLE_RING_CAPACITY = 10000
REDACT_NEEDLES: tuple[str, ...] = (
    "bearer",
    "cookie",
    "authorization",
    "avkit_token",
    "mcp-token",
)
# CONSOLE_FIELDS: event keys appended to the console message as ` key=value`, in this
# order, so a failure's reason reaches the Console (MEU-62, D-13). Other keys stay off.
CONSOLE_FIELDS: tuple[str, ...] = ("job_id", "error", "request_id", "route")
UoWFactory = Callable[[], UnitOfWork]


def redact_message(message: str) -> str:
    """Replace token/cookie material before enqueue or file append.

    Fail-closed: once a needle appears, the needle and the remainder of the
    message are replaced so leftover secret tokens cannot survive.
    """
    lowered = message.casefold()
    hits = [lowered.find(needle) for needle in REDACT_NEEDLES if needle in lowered]
    if not hits:
        return message
    first = min(hits)
    prefix = message[:first].rstrip()
    if prefix:
        return f"{prefix} [REDACTED]"
    return "[REDACTED]"


class HealthService:
    """Process liveness, dependency versions, and the console ring."""

    _active: HealthService | None = None
    _configured = False

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        app_data: Path,
        settings: SettingsService,
        media: MediaPort,
        youtube: YouTubePort,
        assets: TtsAssetPort,
        download_runtime: Callable[[], ModelDownloadRuntime],
        ring_capacity: int = CONSOLE_RING_CAPACITY,
        espeak: EspeakPort | None = None,
    ) -> None:
        if ring_capacity < 1:
            raise ValidationError("ring_capacity must be positive")
        self._uow_factory = uow_factory
        self._app_data = app_data
        self._settings = settings
        self._media = media
        self._youtube = youtube
        self._assets = assets
        self._download_runtime = download_runtime
        self._espeak = espeak
        self._lock = threading.Lock()
        self._seq = 0
        self._processing = False
        self._ring: deque[ConsoleEvent] = deque(maxlen=ring_capacity)
        HealthService._active = self
        self._ensure_processor()

    def _ensure_processor(self) -> None:
        if HealthService._configured:
            return
        current = structlog.get_config()
        processors = list(current.get("processors") or [])
        processors.insert(0, HealthService._dispatch)
        structlog.configure(
            processors=processors,
            wrapper_class=current.get("wrapper_class", structlog.stdlib.BoundLogger),
            context_class=current.get("context_class", dict),
            logger_factory=current.get("logger_factory", structlog.PrintLoggerFactory()),
            cache_logger_on_first_use=False,
        )
        HealthService._configured = True

    @staticmethod
    def _dispatch(
        logger: object,
        method_name: str,
        event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        active = HealthService._active
        if active is None:
            return event_dict
        return active._process(logger, method_name, event_dict)

    def _process(
        self,
        logger: object,
        method_name: str,
        event_dict: MutableMapping[str, Any],
    ) -> MutableMapping[str, Any]:
        with self._lock:
            if self._processing:
                return event_dict
            self._processing = True
        try:
            raw = str(event_dict.get("event", method_name))
            fields = "".join(
                f" {key}={event_dict[key]}" for key in CONSOLE_FIELDS if key in event_dict
            )
            message = redact_message(raw + fields)
            module = str(event_dict.get("module") or "app")
            candidate = method_name.upper()
            level = candidate if candidate in LOG_LEVEL_WIRES else "INFO"
            with self._lock:
                self._seq += 1
                seq = self._seq
                event = ConsoleEvent(
                    seq=seq,
                    message=message,
                    module=module,
                    timestamp=datetime.now(UTC),
                    level=level,
                )
                self._ring.append(event)
            payload = {"seq": seq, "message": message, "module": module, "level": level}
            print(json.dumps(payload), file=sys.stdout)
            if self._settings.get("app", "log_to_file") is True:
                self._append_console_log(json.dumps(payload))
            event_dict["event"] = message
            event_dict["seq"] = seq
            return event_dict
        finally:
            with self._lock:
                self._processing = False

    def _append_console_log(self, line: str) -> None:
        log_dir = self._app_data / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        path = log_dir / "console.log"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def console_snapshot(self, after_seq: object) -> list[ConsoleEvent]:
        if isinstance(after_seq, bool) or not isinstance(after_seq, int) or after_seq < 0:
            raise ValidationError("after_seq must be an int >= 0")
        with self._lock:
            return [event for event in self._ring if event.seq > after_seq]

    def liveness(self) -> HealthLiveness:
        return HealthLiveness(ok=True)

    def dependencies(self) -> DependencyHealth:
        models_dir = models_directory(self._settings)
        runtime = self._download_runtime()
        states = {asset: self._asset_state(asset, models_dir, runtime) for asset in TtsAsset}
        binaries = self._media.ffmpeg_binaries()
        return DependencyHealth(
            ffmpeg_version=self._media.ffmpeg_version(),
            ytdlp_version=self._youtube.ytdlp_version(),
            tts_onnx_vocab=states[TtsAsset.ONNX_VOCAB],
            tts_spacy_model=states[TtsAsset.SPACY_MODEL],
            tts_voice_packs=states[TtsAsset.VOICE_PACKS],
            tts_spacy_version=self._assets.version(TtsAsset.SPACY_MODEL, models_dir),
            tts_espeak=ESPEAK_UNAVAILABLE if self._espeak is None else self._espeak.status(),
            ffmpeg_path=str(binaries.ffmpeg) if binaries is not None else None,
            ffprobe_available=binaries is not None and binaries.ffprobe is not None,
        )

    def _asset_state(
        self,
        asset: TtsAsset,
        models_dir: Path,
        runtime: ModelDownloadRuntime,
    ) -> AssetState:
        """`downloading` while the runtime fetches this asset; otherwise the on-disk state."""
        if runtime.state == "Downloading" and runtime.asset is asset:
            return AssetState.DOWNLOADING
        return self._assets.state(asset, models_dir)

    def record_startup_metric(self, name: str, value: object) -> None:
        if not isinstance(name, str) or name == "":
            raise ValidationError("metric name must be a non-empty str")
        structlog.get_logger(module="health").info(f"startup {name}={value}")
