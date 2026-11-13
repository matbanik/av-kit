"""Composition root: UoW, adapters, and the seven application services."""

from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from avkit_core.ports.storage import UnitOfWork
from avkit_core.services.capture import CaptureService
from avkit_core.services.conversion import ConversionService
from avkit_core.services.download import DownloadService
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.health import HealthService
from avkit_core.services.models import ModelService, models_directory
from avkit_core.services.prepare import TextPreparationService
from avkit_core.services.settings import SettingsService
from avkit_core.services.transcript import TranscriptService
from avkit_core.services.tts import TTSService
from avkit_infra.capture.adapter import CaptureAdapter
from avkit_infra.database.engine import (
    create_session_factory,
    create_sqlite_engine,
    default_db_path,
    init_schema,
    resolve_app_data,
)
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork
from avkit_infra.filesystem.writer import FilesystemAdapter
from avkit_infra.media.adapter import FFmpegAdapter
from avkit_infra.model_manager.manager import ModelCatalogAdapter
from avkit_infra.model_manager.vocab import fetch_vocab
from avkit_infra.model_manager.voice_packs import fetch_voice_pack
from avkit_infra.transcript.adapter import TranscriptAdapter
from avkit_infra.tts.adapter import KokoroAdapter
from avkit_infra.tts.assets import TtsAssetAdapter, resolve_vocab_path
from avkit_infra.tts.espeak import EspeakCliAdapter
from avkit_infra.youtube.adapter import YouTubeAdapter
from avkit_infra.youtube.js_runtime import JsRuntimeLocator, runtime_status


class _DownloadRuntime(Protocol):
    def cancel_processing(self) -> None: ...


class _TranscriptRuntime(Protocol):
    def recover_stale_processing(self) -> None: ...
    def stop_processing(self) -> None: ...


class _TTSRuntime(Protocol):
    def recover_stale_processing(self) -> None: ...
    def stop_processing(self, timeout: float = 10.0) -> bool: ...


class _ModelRuntime(Protocol):
    def unload(self) -> None: ...


class _ConversionRuntime(Protocol):
    def cancel_processing(self) -> None: ...


@dataclass(frozen=True)
class AppServices:
    """Frozen service bundle stored on `app.state.services`."""

    download: _DownloadRuntime
    transcript: _TranscriptRuntime
    tts: _TTSRuntime
    models: _ModelRuntime
    settings: object
    health: object
    conversion: _ConversionRuntime
    capture: object


class _DownloadHooks:
    """Late-bind download progress/stop after `DownloadService` exists."""

    def __init__(self) -> None:
        self._progress: Callable[[int, int | None, float | None], None] | None = None
        self._stop: Callable[[], bool] | None = None

    def bind(
        self,
        progress: Callable[[int, int | None, float | None], None],
        stop: Callable[[], bool],
    ) -> None:
        self._progress = progress
        self._stop = stop

    def on_progress(self, downloaded: int, total: int | None, speed: float | None) -> None:
        hook = self._progress
        if hook is not None:
            hook(downloaded, total, speed)

    def should_stop(self) -> bool:
        hook = self._stop
        if hook is None:
            return False
        return hook()


def _as_playlist_end(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return 0
    return max(0, int(value))


def bundled_ffmpeg() -> Path | None:
    """Resolve packaged FFmpeg from the frozen onedir sibling layout."""
    if not getattr(sys, "frozen", False):
        return None
    return Path(sys.executable).resolve().parent.parent / "ffmpeg" / "ffmpeg.exe"


def bundled_deno() -> Path | None:
    """Resolve packaged Deno from the frozen onedir sibling layout (`DENO_BUNDLE`)."""
    if not getattr(sys, "frozen", False):
        return None
    return Path(sys.executable).resolve().parent.parent / "deno" / "deno.exe"


def _ffmpeg_configured(value: object) -> Path | None:
    if not isinstance(value, str) or value.strip() == "":
        return None
    return Path(value).expanduser()


def build_services(
    *,
    app_data: Path | None = None,
    database_path: Path | None = None,
) -> tuple[AppServices, Callable[[], None]]:
    """Construct production services and an engine dispose callback."""
    root = app_data if app_data is not None else resolve_app_data()
    db_path = database_path if database_path is not None else default_db_path()
    if app_data is not None and database_path is None:
        db_path = root / "avkit.db"
    engine = create_sqlite_engine(db_path)
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def _make_uow() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    uow_factory = cast(Callable[[], UnitOfWork], _make_uow)

    def dispose() -> None:
        engine.dispose()

    settings = SettingsService(uow_factory)
    playlist_end = _as_playlist_end(settings.get("transcript", "playlist_end"))
    hooks = _DownloadHooks()
    # LIVE_SOURCE: the ffmpeg setting is read at each resolution, so a PUT needs no restart.
    media = FFmpegAdapter(
        configured_source=lambda: _ffmpeg_configured(settings.get("downloader", "ffmpeg_path")),
        bundle_path=bundled_ffmpeg(),
    )
    # LIVE_SOURCE: the deno setting is read at each resolution, so a PUT needs no restart.
    js_runtime = JsRuntimeLocator(lambda: settings.get("downloader", "deno_path"), bundled_deno())
    youtube = YouTubeAdapter(
        playlist_end=playlist_end,
        on_progress=hooks.on_progress,
        should_stop=hooks.should_stop,
        # LIVE_SOURCE: the yt-dlp debug switch is read at each public call (YTDLP_LIVE).
        yt_dlp_debug=lambda: settings.get("downloader", "yt_dlp_debug") is True,
        ffmpeg_location=lambda: b.ffmpeg if (b := media.ffmpeg_binaries()) else None,
        js_runtime=js_runtime.resolve,
    )
    coordinator = ExtractCoordinator(youtube)
    download = DownloadService(
        uow_factory,
        youtube=youtube,
        media=media,
        coordinator=coordinator,
        settings=settings,
    )
    hooks.bind(download.on_download_progress, download.should_stop)
    captions = TranscriptAdapter()
    filesystem = FilesystemAdapter()
    transcript = TranscriptService(
        uow_factory,
        coordinator=coordinator,
        captions=captions,
        filesystem=filesystem,
        settings=settings,
    )
    tts_port = KokoroAdapter(vocab_path=resolve_vocab_path(lambda: models_directory(settings)))
    assets = TtsAssetAdapter(fetch_vocab=fetch_vocab, fetch_pack=fetch_voice_pack)
    # A spaCy model installed by an earlier run is importable again after a restart.
    assets.activate(models_directory(settings))
    catalog = ModelCatalogAdapter()
    prepare = TextPreparationService()
    # The user-installed eSpeak NG CLI, re-probed per call (MEU-74 `ESPEAK_DETECT`).
    espeak = EspeakCliAdapter()
    tts = TTSService(
        uow_factory,
        tts=tts_port,
        filesystem=filesystem,
        media=media,
        settings=settings,
        prepare=prepare,
        assets=assets,
        espeak=espeak,
    )
    models = ModelService(
        uow_factory,
        catalog=catalog,
        tts=tts_port,
        settings=settings,
        assets=assets,
    )
    health = HealthService(
        uow_factory,
        app_data=root,
        settings=settings,
        media=media,
        youtube=youtube,
        assets=assets,
        download_runtime=models.get_download_runtime,
        espeak=espeak,
        js_runtime=lambda: runtime_status(js_runtime),
    )
    conversion = ConversionService(uow_factory, media=media, settings=settings)
    grab = CaptureAdapter()
    capture = CaptureService(
        uow_factory,
        capture=grab,
        annotate=grab,
        settings=settings,
        frames=media,
    )
    return (
        AppServices(
            download=download,
            transcript=transcript,
            tts=tts,
            models=models,
            settings=settings,
            health=health,
            conversion=conversion,
            capture=capture,
        ),
        dispose,
    )
