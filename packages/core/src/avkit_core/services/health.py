"""HealthService — sole seq owner, redacted console ring, optional log file."""

from __future__ import annotations

import json
import re
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
from avkit_core.domain.transcript import replace_links
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
# job_id and video_id name the transcript job and video; variant_id and device name the
# TTS model load; error is the stored reason or error type, detail its first line of text
# (MEU-115, D-296); request_id and route tie an API error to its request.
CONSOLE_FIELDS: tuple[str, ...] = (
    "job_id",
    "video_id",
    "variant_id",
    "device",
    "error",
    "detail",
    "request_id",
    "route",
)
#: The most characters a Console field value keeps after it is made single-line.
FIELD_LIMIT = 300
#: Whether the home folder matches in any case; Windows paths ignore case (D-335).
HOME_IGNORES_CASE = sys.platform == "win32"
#: Lines at these levels always go to console.log, whatever app.log_to_file holds (D-247).
PERSIST_LEVELS: tuple[str, ...] = ("ERROR", "CRITICAL")
#: An event with this key true also always goes to console.log. The key is never shown.
PERSIST_FIELD = "persist"
#: structlog method names that are not level names, and the level each one logs at.
LEVEL_ALIASES: dict[str, str] = {
    "exception": "ERROR",
    "fatal": "CRITICAL",
    "warn": "WARNING",
}
_LINE_BREAKS = re.compile(r"[\r\n]+")
_SEPARATORS = re.compile(r"[\\/]+")
UoWFactory = Callable[[], UnitOfWork]


def redact_message(message: str) -> str:
    """Replace token/cookie material before enqueue or file append.

    Fail-closed: once a needle appears, the needle and the remainder of the
    message are replaced so leftover secret tokens cannot survive.
    """
    # A character can fold to several ("ß" to "ss"), so each folded position maps back to
    # the original character it came from, and the cut lands before the needle.
    origins = [index for index, char in enumerate(message) for _ in char.casefold()]
    lowered = message.casefold()
    hits = [lowered.find(needle) for needle in REDACT_NEEDLES if needle in lowered]
    if not hits:
        return message
    first = origins[min(hits)]
    prefix = message[:first].rstrip()
    if prefix:
        return f"{prefix} [REDACTED]"
    return "[REDACTED]"


def home_folder() -> str:
    """The user's home folder, or "" when it cannot be found."""
    try:
        return str(Path.home())
    except RuntimeError:
        return ""


def scrub_home(text: str) -> str:
    """`text` with the home folder as "~" where it starts a path (`HOME_SCRUB`, D-335).

    Its parts match joined by `\\`, `/` or a doubled `\\\\` (an `OSError` quotes its path that
    way). A match follows no word character, separator, `.`, `~` or `-`, and is followed by
    a separator, a quote or the end, so a longer user name or a nested path is kept. A home
    folder with no separator, such as a bare drive, changes nothing.
    """
    home = home_folder().rstrip("\\/")
    if not _SEPARATORS.search(home):
        return text
    parts = [re.escape(part) for part in _SEPARATORS.split(home)]
    pattern = r"(?<![\w\\/.~-])" + r"(?:\\\\|\\|/)".join(parts) + r"(?=[\\/'\"]|$)"
    return re.sub(pattern, "~", text, flags=re.IGNORECASE if HOME_IGNORES_CASE else 0)


def console_field(value: object) -> str:
    """`value` as one line, the home folder as "~", each URL as "[link]", redacted and cut.

    The scrub runs before the FIELD_LIMIT cut, so the cut keeps no part of a user name.
    """
    single = _LINE_BREAKS.sub(" ", str(value))
    return redact_message(replace_links(scrub_home(single)))[:FIELD_LIMIT]


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
        self._file_lock = threading.Lock()
        self._seq = 0
        self._guard = threading.local()
        self._ring: deque[ConsoleEvent] = deque(maxlen=ring_capacity)
        HealthService._active = self
        self._ensure_processor()

    def _ensure_processor(self) -> None:
        if HealthService._configured:
            return
        current = structlog.get_config()
        processors = list(current.get("processors") or [])
        # Bound context (a request's request_id) is merged before the safe message is built,
        # so no later processor can add a raw value back to the rendered line.
        merge = structlog.contextvars.merge_contextvars
        position = processors.index(merge) + 1 if merge in processors else 0
        processors.insert(position, HealthService._dispatch)
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
        # A log raised while this thread processes a log passes through unprocessed.
        if getattr(self._guard, "active", False):
            return event_dict
        self._guard.active = True
        try:
            raw = str(event_dict.get("event", method_name))
            fields = "".join(
                f" {key}={console_field(event_dict[key])}"
                for key in CONSOLE_FIELDS
                if key in event_dict
            )
            message = redact_message(raw + fields)
            module = str(event_dict.get("module") or "app")
            candidate = LEVEL_ALIASES.get(method_name, method_name.upper())
            level = candidate if candidate in LOG_LEVEL_WIRES else "INFO"
            persist = level in PERSIST_LEVELS or event_dict.get(PERSIST_FIELD) is True
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
            if persist or self._settings.get("app", "log_to_file") is True:
                self._append_console_log(json.dumps(payload))
            # Downstream renderers print only the safe message: no field, no traceback.
            event_dict.clear()
            event_dict.update({"event": message, "seq": seq, "exc_info": False})
            return event_dict
        finally:
            self._guard.active = False

    def _append_console_log(self, line: str) -> None:
        """Append one line. A locked or read-only file never fails the call that logged."""
        log_dir = self._app_data / "logs"
        path = log_dir / "console.log"
        with self._file_lock:
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                with path.open("a", encoding="utf-8") as handle:
                    handle.write(line + "\n")
            except OSError:
                return

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
