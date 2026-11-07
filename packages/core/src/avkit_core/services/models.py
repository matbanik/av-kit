"""ModelService — catalog merge, load/unload, and in-memory download runtime."""

from __future__ import annotations

import math
import threading
from collections.abc import Callable
from pathlib import Path

import structlog

from avkit_core.domain.enums import DeviceType, ModelFormat
from avkit_core.domain.errors import (
    ConflictError,
    ModelDownloadError,
    ModelLoadError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.tts import (
    AssetState,
    ModelAvailability,
    ModelDownloadRuntime,
    ModelStatus,
    ModelVariant,
    TtsAsset,
    is_legacy_onnx_path,
    model_availability,
)
from avkit_core.ports.models import ModelCatalogPort
from avkit_core.ports.storage import UnitOfWork
from avkit_core.ports.tts import TtsAssetPort, TTSPort
from avkit_core.services.settings import SettingsService

UoWFactory = Callable[[], UnitOfWork]
log = structlog.get_logger(module="model_manager")
IDLE_RUNTIME = ModelDownloadRuntime(
    variant_id=None,
    asset=None,
    state="Idle",
    fraction=0.0,
    error_message=None,
)


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, int | float)
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def models_directory(settings: SettingsService) -> Path:
    """Return the configured `tts.models_directory`, user-expanded."""
    return Path(str(settings.get("tts", "models_directory"))).expanduser()


def asset_missing(asset: TtsAsset) -> ConflictError:
    """`ASSET_MISSING_ERROR` for `asset` (HTTP 409)."""
    return ConflictError(f"tts asset missing: {asset.value}")


def _not_downloaded(row: ModelVariant) -> ModelVariant:
    return ModelVariant(
        id=row.id,
        name=row.name,
        format=row.format,
        precision=row.precision,
        size_bytes=row.size_bytes,
        path=row.path,
        is_downloaded=False,
    )


def _is_legacy(row: ModelVariant, models_dir: Path) -> bool:
    return row.path is not None and is_legacy_onnx_path(row.path, models_dir)


class ModelService:
    """Owns ModelDownloadRuntime. Load delegates to TTSPort only."""

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        catalog: ModelCatalogPort,
        tts: TTSPort,
        settings: SettingsService,
        assets: TtsAssetPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._catalog = catalog
        self._tts = tts
        self._settings = settings
        self._assets = assets
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._worker_error: BaseException | None = None
        self._runtime = IDLE_RUNTIME

    def get_download_runtime(self) -> ModelDownloadRuntime:
        return self._runtime

    def get_status(self) -> ModelStatus:
        return self._tts.get_model_status()

    def available_devices(self, fmt: ModelFormat) -> tuple[DeviceType, ...]:
        return self._tts.available_devices(fmt)

    def availability(self, fmt: ModelFormat) -> ModelAvailability:
        """`AVAILABILITY` of `fmt` in this build, from the port's `RUNTIME_PRESENT`."""
        return model_availability(fmt, self._tts.runtime_present(fmt))

    def list_available(self) -> list[ModelVariant]:
        """Catalog union sideload. A variant counts as downloaded only with a valid vocab.

        A scanned file whose id has a catalog row is recorded first (`SIDELOAD_RECORD`). A
        row whose persisted path is `LEGACY_ONNX_PATH` (a v0.19 file) reads as not
        downloaded; its database path is left unchanged.
        """
        models_dir = models_directory(self._settings)
        with self._uow_factory() as uow:
            self._record_sideload(uow, models_dir)
            rows = {row.id: row for row in uow.models.list_catalog()}
        for row in self._catalog.sideload(models_dir):
            rows[row.id] = row
        vocab_ready = self._assets.state(TtsAsset.ONNX_VOCAB, models_dir) is AssetState.READY
        rows = {
            key: (
                _not_downloaded(row)
                if row.is_downloaded and (not vocab_ready or _is_legacy(row, models_dir))
                else row
            )
            for key, row in rows.items()
        }
        return list(rows.values())

    def list_downloaded(self) -> list[ModelVariant]:
        return [row for row in self.list_available() if row.is_downloaded]

    def load(self, variant_id: str, device: DeviceType) -> None:
        """Load a variant; refuse (409) without the vocab; then start the spaCy download.

        A sideloaded file is recorded before the row is read (`SIDELOAD_RECORD`), so the
        port receives its path.

        Raises:
            NotFoundError: unknown variant.
            ModelLoadError: the variant can't run in this build (`MODEL_REFUSAL`, the reason
                as message). It is checked first, as a vocab 409 would ask for an asset the
                build can't use; the port is never called.
            ConflictError: `LEGACY_MODEL_409` (the row's path is a v0.19 file) or
                `ASSET_MISSING_ERROR(ONNX_VOCAB)`; the port is never called.
        """
        models_dir = models_directory(self._settings)
        with self._uow_factory() as uow:
            self._record_sideload(uow, models_dir)
            variant = uow.models.get(variant_id)
        if variant is None:
            raise NotFoundError(f"model variant {variant_id} not found")
        # `reason` is set exactly when this build can't run the variant (`AVAILABILITY`).
        reason = self.availability(variant.format).reason
        if reason is not None:
            log.warning("model.load_refused", variant_id=variant.id, detail=reason)
            raise ModelLoadError(reason)
        if _is_legacy(variant, models_dir):
            raise ConflictError(f"model variant {variant_id} needs a re-download (v0.19 file)")
        if self._assets.state(TtsAsset.ONNX_VOCAB, models_dir) is not AssetState.READY:
            raise asset_missing(TtsAsset.ONNX_VOCAB)
        self._tts.load_model(variant, device)
        self._auto_download_spacy(models_dir)

    def _record_sideload(self, uow: UnitOfWork, models_dir: Path) -> None:
        """`SIDELOAD_RECORD`: persist each scanned file whose id has a catalog row.

        `RECORD_RULE`: a row is written only when it is not downloaded or its path differs
        from the scanned one, so a repeat scan with no file change writes nothing. A scanned
        id with no row stays display-only. The scan is the port's; core touches no files.
        """
        wrote = False
        for scanned in self._catalog.sideload(models_dir):
            row = uow.models.get(scanned.id)
            if row is None or scanned.path is None:
                continue
            if row.is_downloaded and row.path == scanned.path:
                continue
            uow.models.mark_downloaded(scanned.id, scanned.path)
            wrote = True
        if wrote:
            uow.commit()

    def _auto_download_spacy(self, models_dir: Path) -> None:
        """Start the managed spaCy download after a load (D-22, D-10) unless one is running.

        The check-then-start runs under `_lock`, so the runtime already reads `Downloading`
        when `load` returns.
        """
        if self._assets.state(TtsAsset.SPACY_MODEL, models_dir) is AssetState.READY:
            return
        with self._lock:
            if self._runtime.state == "Downloading":
                log.info(
                    "model.asset_download_deferred",
                    asset=TtsAsset.SPACY_MODEL.value,
                    busy_variant=self._runtime.variant_id,
                    busy_asset=None if self._runtime.asset is None else self._runtime.asset.value,
                )
                return
            self._start_locked(None, TtsAsset.SPACY_MODEL, models_dir)
        log.info("model.asset_download_started", asset=TtsAsset.SPACY_MODEL.value)

    def unload(self) -> None:
        self._tts.unload_model()

    def download(self, variant_id: str) -> ModelVariant:
        """Start a variant download: weights, the vocab if missing, then `MODEL_CHAINS_PACKS`.

        Raises:
            ConflictError: a download is in flight, or the variant can't run in this build
                (`MODEL_REFUSAL`, the reason as message); nothing starts and no file is written.
            NotFoundError: unknown variant.
        """
        dest_dir = models_directory(self._settings)
        # Warm the runtime probe before the lock: the first PyTorch probe imports kokoro.
        with self._uow_factory() as uow:
            row = uow.models.get(variant_id)
        if row is not None:
            self._tts.runtime_present(row.format)
        with self._lock:
            if self._runtime.state == "Downloading":
                raise ConflictError("a model download is already in progress")
            with self._uow_factory() as uow:
                variant = uow.models.get(variant_id)
            if variant is None:
                raise NotFoundError(f"model variant {variant_id} not found")
            reason = self.availability(variant.format).reason
            if reason is not None:
                log.warning("model.download_refused", variant_id=variant.id, detail=reason)
                raise ConflictError(reason)
            self._start_locked(variant, None, dest_dir)
            return variant

    def download_asset(self, asset: TtsAsset) -> None:
        """Start a TTS runtime-asset download (`POST /models/download {asset}`).

        Raises:
            ConflictError: another download runs, or the asset is already ready
                (`SPACY_INSTALL_EXISTING`: nothing is fetched).
        """
        dest_dir = models_directory(self._settings)
        with self._lock:
            if self._runtime.state == "Downloading":
                raise ConflictError("a model download is already in progress")
            if self._assets.state(asset, dest_dir) is AssetState.READY:
                raise ConflictError(f"tts asset already ready: {asset.value}")
            self._start_locked(None, asset, dest_dir)

    def _start_locked(
        self,
        variant: ModelVariant | None,
        asset: TtsAsset | None,
        dest_dir: Path,
    ) -> None:
        """Set the runtime to `Downloading` and start the worker. Caller holds `_lock`."""
        self._worker_error = None
        self._runtime = ModelDownloadRuntime(
            variant_id=None if variant is None else variant.id,
            asset=asset,
            state="Downloading",
            fraction=0.0,
            error_message=None,
        )
        self._thread = threading.Thread(
            target=self._run_download,
            args=(variant, asset, dest_dir),
            daemon=True,
        )
        self._thread.start()

    def _run_download(
        self,
        variant: ModelVariant | None,
        asset: TtsAsset | None,
        dest_dir: Path,
    ) -> None:
        # The target the runtime reports; `MODEL_CHAINS_PACKS` switches it to the packs.
        variant_id = None if variant is None else variant.id
        target_asset = asset

        def on_progress(fraction: float) -> None:
            if not _is_finite_number(fraction):
                return
            number = float(fraction)
            if number < 0.0 or number > 1.0:
                raise ValidationError("progress fraction must be between 0.0 and 1.0")
            with self._lock:
                self._runtime = ModelDownloadRuntime(
                    variant_id=variant_id,
                    asset=target_asset,
                    state="Downloading",
                    fraction=number,
                    error_message=None,
                )

        try:
            if variant is not None:
                path = self._catalog.download(variant, dest_dir, on_progress)
                if self._assets.state(TtsAsset.ONNX_VOCAB, dest_dir) is not AssetState.READY:
                    self._assets.download(TtsAsset.ONNX_VOCAB, dest_dir, on_progress)
                with self._uow_factory() as uow:
                    uow.models.mark_downloaded(variant.id, path)
                    uow.commit()
                if self._assets.state(TtsAsset.VOICE_PACKS, dest_dir) is not AssetState.READY:
                    variant_id, target_asset = None, TtsAsset.VOICE_PACKS
                    on_progress(0.0)
                    try:
                        self._assets.download(TtsAsset.VOICE_PACKS, dest_dir, on_progress)
                    except Exception as exc:
                        message = f"{TtsAsset.VOICE_PACKS.value} download failed: {exc}"
                        raise ModelDownloadError(message) from exc
            elif asset is not None:
                self._assets.download(asset, dest_dir, on_progress)
        except ModelDownloadError as exc:
            self._fail(variant_id, target_asset, str(exc), exc)
            return
        except Exception as exc:
            wrapped = ModelDownloadError(str(exc) or "model download failed")
            wrapped.__cause__ = exc
            self._fail(variant_id, target_asset, str(exc) or type(exc).__name__, wrapped)
            return
        with self._lock:
            self._runtime = IDLE_RUNTIME
            self._worker_error = None

    def _fail(
        self,
        variant_id: str | None,
        asset: TtsAsset | None,
        message: str,
        error: BaseException,
    ) -> None:
        log.warning(
            "model.download_failed",
            variant_id=variant_id,
            asset=None if asset is None else asset.value,
            error=message,
        )
        with self._lock:
            self._runtime = ModelDownloadRuntime(
                variant_id=variant_id,
                asset=asset,
                state="Failed",
                fraction=self._runtime.fraction,
                error_message=message,
            )
            self._worker_error = error
