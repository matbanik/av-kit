"""Kokoro runtime assets: the vocab/config file and the managed spaCy English model (MEU-62).

`TtsAssetAdapter` implements `avkit_core.ports.tts.TtsAssetPort`. The spaCy model is a
managed download (human-approved D-22): one pinned wheel per installed spaCy
``major.minor``, sha256-verified, extracted with its ``.dist-info`` into the models
directory, and put on ``sys.path``. `spacy.util.is_package` and ``spacy.load`` then resolve
it by name, which is what misaki's G2P and ``prepare._chunk`` call. Nothing runs ``pip`` at
runtime. This module never imports the Hugging Face hub client (AC-9.12): the vocab fetch is
injected from ``avkit_infra.model_manager.vocab`` and the voice-pack fetch (MEU-73
`VOICE_PACK_DOWNLOAD`) from ``avkit_infra.model_manager.voice_packs``.
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import importlib.util
import json
import os
import shutil
import ssl
import sys
import threading
import urllib.request
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import assert_never
from uuid import uuid4

import certifi
import structlog

from avkit_core.domain.errors import ModelDownloadError
from avkit_core.domain.tts import SPACY_MODEL, AssetState, TtsAsset
from avkit_infra.tts.voices import (
    KOKORO_VOICE_IDS,
    VOICE_PACK_BYTES,
    voice_pack_path,
    voice_pack_ready,
)

log = structlog.get_logger(module="tts")

ONNX_VOCAB_REPO = "hexgrad/Kokoro-82M"
ONNX_VOCAB_FILE = "config.json"
SPACY_DIR_NAME = "spacy"
FETCH_CHUNK_BYTES = 1 << 16

# `SPACY_PATH_SWAP`: the `sys.path` entries `activate_spacy_dir` appended itself.
_ACTIVE_SPACY_ENTRIES: set[str] = set()
_ACTIVE_SPACY_LOCK = threading.Lock()

ProgressFn = Callable[[float], None]
FetchFn = Callable[[str, Path, ProgressFn], None]
VocabFetchFn = Callable[[Path, ProgressFn], Path]
PackFetchFn = Callable[[str, Path], Path]


@dataclass(frozen=True)
class WheelPin:
    """One pinned spaCy model wheel (`SPACY_MODEL_PIN` value)."""

    name: str
    version: str
    url: str
    sha256: str


# SPACY_MODEL_PIN, keyed by the installed spaCy major.minor. The sha256 was measured on
# 2026-09-30 from a 12 806 118-byte download of this URL (METADATA: spaCy >=3.8.0,<3.9.0).
SPACY_MODEL_PIN: dict[str, WheelPin] = {
    "3.8": WheelPin(
        name=SPACY_MODEL,
        version="3.8.0",
        url=(
            "https://github.com/explosion/spacy-models/releases/download/"
            f"{SPACY_MODEL}-3.8.0/{SPACY_MODEL}-3.8.0-py3-none-any.whl"
        ),
        sha256="1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85",
    ),
}


def vocab_path(models_dir: Path) -> Path:
    """`VOCAB_LOCATION`: the single Kokoro config/vocab file for every variant."""
    return models_dir / ONNX_VOCAB_FILE


def resolve_vocab_path(models_dir: Callable[[], Path]) -> Callable[[], Path]:
    """Return a `VOCAB_LOCATION` resolver evaluated per call.

    `models_dir` is the composition root's `tts.models_directory` reader, so a changed
    setting is honoured by the next load or chunk.
    """
    return lambda: vocab_path(models_dir())


def vocab_is_valid(path: Path) -> bool:
    """True when `path` parses as JSON with a dict `vocab` (the adapter's own rule)."""
    if not path.is_file():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(payload, dict) and isinstance(payload.get("vocab"), dict)


def _installed_spacy_minor() -> str:
    """Return the installed spaCy `major.minor`, or raise ModelDownloadError."""
    try:
        version = importlib.metadata.version("spacy")
    except importlib.metadata.PackageNotFoundError as exc:
        raise ModelDownloadError("spaCy is not installed") from exc
    parts = version.split(".")
    return ".".join(parts[:2])


def spacy_install_dir(models_dir: Path, pin: WheelPin) -> Path:
    """`SPACY_INSTALL_DIR` for `pin` under `models_dir`."""
    return models_dir / SPACY_DIR_NAME / f"{pin.name}-{pin.version}"


def activate_spacy_dir(models_dir: Path) -> None:
    """Append every existing pinned install dir to `sys.path` exactly once (idempotent).

    Appended, not prepended, so the install dir never shadows site-packages (AC-73.12).
    `SPACY_PATH_SWAP`: an entry this function appended for another `models_dir` is removed,
    so a changed `tts.models_directory` stops reading the old install. Entries it did not
    append are never touched.
    """
    current = [
        str(install)
        for install in (spacy_install_dir(models_dir, pin) for pin in SPACY_MODEL_PIN.values())
        if install.is_dir()
    ]
    changed = False
    with _ACTIVE_SPACY_LOCK:
        for entry in sorted(_ACTIVE_SPACY_ENTRIES - set(current)):
            _ACTIVE_SPACY_ENTRIES.discard(entry)
            if entry in sys.path:
                sys.path.remove(entry)
                changed = True
        for entry in current:
            if entry not in sys.path:
                sys.path.append(entry)
                _ACTIVE_SPACY_ENTRIES.add(entry)
                changed = True
        if changed:
            importlib.invalidate_caches()


def spacy_ready(models_dir: Path) -> bool:
    """`SPACY_READY`: `spacy.util.is_package(SPACY_MODEL)` and the package is importable."""
    activate_spacy_dir(models_dir)
    importlib.invalidate_caches()
    try:
        import spacy.util
    except ImportError:
        return False
    try:
        return bool(spacy.util.is_package(SPACY_MODEL)) and (
            importlib.util.find_spec(SPACY_MODEL) is not None
        )
    except (ImportError, ValueError):
        return False


def _default_fetch(url: str, dest: Path, on_progress: ProgressFn) -> None:
    """Stream `url` to `dest` with the process proxy environment (urllib honours it).

    Verifies against certifi's roots, like the other downloads: a fresh Windows install
    holds few roots in its store and Python never triggers the lazy fetch of the rest.
    """
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(  # noqa: S310 — pinned https URL
        url, timeout=60, context=context
    ) as response:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        with dest.open("wb") as handle:
            while True:
                chunk = response.read(FETCH_CHUNK_BYTES)
                if not chunk:
                    break
                handle.write(chunk)
                done += len(chunk)
                if total > 0:
                    on_progress(min(done / total, 1.0))
    on_progress(1.0)


def _safe_member(name: str) -> PurePosixPath:
    """Return a wheel member path, rejecting absolute, drive-qualified or `..` paths."""
    member = PurePosixPath(name.replace("\\", "/"))
    unsafe = (
        not member.parts
        or member.is_absolute()
        or ":" in member.parts[0]
        or any(part == ".." for part in member.parts)
    )
    if unsafe:
        raise ModelDownloadError(f"unsafe path in spaCy wheel: {name}")
    return member


def install_spacy_wheel(wheel: Path, models_dir: Path, pin: WheelPin) -> Path:
    """Verify, extract and move `wheel` into `SPACY_INSTALL_DIR`; return that directory.

    Atomic: members go to `spacy/.tmp-<uuid>`, which replaces the destination with
    `os.replace` only after every member extracted. A stale destination (a corrupt
    install) is removed first. Any failure removes the temp dir and leaves no install.
    """
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    if digest != pin.sha256:
        raise ModelDownloadError(
            f"spaCy wheel sha256 mismatch: expected {pin.sha256}, got {digest}"
        )
    root = models_dir / SPACY_DIR_NAME
    root.mkdir(parents=True, exist_ok=True)
    temp = root / f".tmp-{uuid4().hex}"
    dest = spacy_install_dir(models_dir, pin)
    try:
        temp.mkdir()
        temp_resolved = temp.resolve()
        with zipfile.ZipFile(wheel) as archive:
            for info in archive.infolist():
                member = _safe_member(info.filename)
                target = (temp / Path(*member.parts)).resolve()
                if not target.is_relative_to(temp_resolved):
                    raise ModelDownloadError(f"unsafe path in spaCy wheel: {info.filename}")
                if info.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as src, target.open("wb") as out:
                    shutil.copyfileobj(src, out)
        if dest.exists():
            shutil.rmtree(dest)
        os.replace(temp, dest)
    except zipfile.BadZipFile as exc:
        raise ModelDownloadError("spaCy wheel is not a valid zip archive") from exc
    finally:
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
    for name in list(sys.modules):
        if name == pin.name or name.startswith(f"{pin.name}."):
            del sys.modules[name]
    return dest


def _missing_packs(models_dir: Path) -> list[str]:
    """Catalog voices whose `VOICE_PACK` is absent or not exactly `VOICE_PACK_BYTES`."""
    return [voice_id for voice_id in KOKORO_VOICE_IDS if not voice_pack_ready(models_dir, voice_id)]


class TtsAssetAdapter:
    """`TtsAssetPort` over the models directory."""

    def __init__(
        self,
        *,
        fetch_vocab: VocabFetchFn,
        fetch: FetchFn | None = None,
        fetch_pack: PackFetchFn | None = None,
    ) -> None:
        self._fetch_vocab = fetch_vocab
        self._fetch = fetch
        self._fetch_pack = fetch_pack

    def state(self, asset: TtsAsset, models_dir: Path) -> AssetState:
        match asset:
            case TtsAsset.ONNX_VOCAB:
                ready = vocab_is_valid(vocab_path(models_dir))
            case TtsAsset.SPACY_MODEL:
                ready = spacy_ready(models_dir)
            case TtsAsset.VOICE_PACKS:
                ready = not _missing_packs(models_dir)
            case _:
                assert_never(asset)
        return AssetState.READY if ready else AssetState.MISSING

    def version(self, asset: TtsAsset, models_dir: Path) -> str | None:
        match asset:
            case TtsAsset.ONNX_VOCAB:
                return None
            case TtsAsset.SPACY_MODEL:
                if not spacy_ready(models_dir):
                    return None
                try:
                    return importlib.metadata.version(SPACY_MODEL)
                except importlib.metadata.PackageNotFoundError:
                    return None
            case TtsAsset.VOICE_PACKS:
                return None
            case _:
                assert_never(asset)

    def download(self, asset: TtsAsset, models_dir: Path, on_progress: ProgressFn) -> Path:
        match asset:
            case TtsAsset.ONNX_VOCAB:
                return self._download_vocab(models_dir, on_progress)
            case TtsAsset.SPACY_MODEL:
                return self._download_spacy(models_dir, on_progress)
            case TtsAsset.VOICE_PACKS:
                return self._download_packs(models_dir, on_progress)
            case _:
                assert_never(asset)

    def activate(self, models_dir: Path) -> None:
        activate_spacy_dir(models_dir)

    def _download_vocab(self, models_dir: Path, on_progress: ProgressFn) -> Path:
        models_dir.mkdir(parents=True, exist_ok=True)
        path = self._fetch_vocab(models_dir, on_progress)
        if not vocab_is_valid(path):
            path.unlink(missing_ok=True)
            raise ModelDownloadError("vocab file is invalid: no vocab mapping")
        log.info("model.asset_downloaded", asset=TtsAsset.ONNX_VOCAB.value, path=str(path))
        return path

    def _download_packs(self, models_dir: Path, on_progress: ProgressFn) -> Path:
        """`VOICE_PACK_DOWNLOAD`: fetch each missing or wrong-size pack, then check its size."""
        missing = _missing_packs(models_dir)
        voices_dir = voice_pack_path(models_dir, KOKORO_VOICE_IDS[0]).parent
        if not missing:
            on_progress(1.0)
            return voices_dir
        if self._fetch_pack is None:
            raise ModelDownloadError("voice pack download is not configured")
        on_progress(0.0)
        for done, voice_id in enumerate(missing, start=1):
            path = voice_pack_path(models_dir, voice_id)
            path.unlink(missing_ok=True)
            fetched = self._fetch_pack(voice_id, models_dir)
            size = fetched.stat().st_size if fetched.is_file() else -1
            if size != VOICE_PACK_BYTES:
                fetched.unlink(missing_ok=True)
                path.unlink(missing_ok=True)
                raise ModelDownloadError(
                    f"voice pack {voice_id} is {size} bytes, expected {VOICE_PACK_BYTES}"
                )
            on_progress(done / len(missing))
        log.info(
            "model.asset_downloaded",
            asset=TtsAsset.VOICE_PACKS.value,
            path=str(voices_dir),
            fetched=len(missing),
        )
        return voices_dir

    def _download_spacy(self, models_dir: Path, on_progress: ProgressFn) -> Path:
        minor = _installed_spacy_minor()
        pin = SPACY_MODEL_PIN.get(minor)
        if pin is None:
            raise ModelDownloadError(f"no pinned {SPACY_MODEL} for spaCy {minor}")
        root = models_dir / SPACY_DIR_NAME
        root.mkdir(parents=True, exist_ok=True)
        wheel = root / f".dl-{uuid4().hex}.whl"
        fetch = self._fetch if self._fetch is not None else _default_fetch
        try:
            try:
                fetch(pin.url, wheel, lambda fraction: on_progress(min(fraction, 1.0) * 0.9))
            except ModelDownloadError:
                raise
            except Exception as exc:
                raise ModelDownloadError(f"spaCy model download failed: {exc}") from exc
            dest = install_spacy_wheel(wheel, models_dir, pin)
        finally:
            wheel.unlink(missing_ok=True)
        activate_spacy_dir(models_dir)
        on_progress(1.0)
        log.info("model.asset_downloaded", asset=TtsAsset.SPACY_MODEL.value, path=str(dest))
        return dest
