"""FilesystemPort adapter: atomic writes, progress export, WAV, compile reads."""

from __future__ import annotations

import json
import os
import tempfile
import wave
from pathlib import Path

import numpy as np
import structlog

from avkit_core.domain.errors import FilesystemError, ValidationError

log = structlog.get_logger(module="filesystem")

COMPILE_PARENT_NAMES = frozenset({"raw", "compiled"})
COMPILE_SUFFIX = ".md"
PROGRESS_EXPORT_FILENAME = "progress.json"
PROGRESS_EXPORT_KEY = "video_ids_done"


class FilesystemAdapter:
    """Bounded file writes. read_text is compile-only and keyword-only."""

    def write_text_atomic(self, path: Path, text: str) -> None:
        destination = Path(path)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            handle, temp_name = tempfile.mkstemp(prefix=destination.name, dir=destination.parent)
        except OSError as exc:
            raise FilesystemError(f"cannot prepare atomic write for {destination}") from exc
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as temp_file:
                temp_file.write(text)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_name, destination)
        except OSError as exc:
            raise FilesystemError(f"atomic write failed for {destination}") from exc
        finally:
            leftover = Path(temp_name)
            if leftover.exists() and leftover != destination:
                try:
                    leftover.unlink()
                except OSError:
                    log.warning("filesystem.temp_cleanup_failed", path=str(leftover))
        log.debug("filesystem.write_text_atomic", path=str(destination))

    def write_progress_export(self, output_dir: Path, video_ids_done: list[str]) -> None:
        payload = {PROGRESS_EXPORT_KEY: list(video_ids_done)}
        target = Path(output_dir) / PROGRESS_EXPORT_FILENAME
        self.write_text_atomic(target, json.dumps(payload))

    def ensure_channel_dirs(self, output_dir: Path) -> None:
        root = Path(output_dir)
        try:
            (root / "raw").mkdir(parents=True, exist_ok=True)
            (root / "compiled").mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise FilesystemError(f"cannot create channel dirs under {root}") from exc
        log.debug("filesystem.ensure_channel_dirs", path=str(root))

    def write_audio_wav(self, path: Path, samples: np.ndarray, sample_rate: int) -> None:
        if not isinstance(sample_rate, int) or isinstance(sample_rate, bool) or sample_rate <= 0:
            raise ValidationError("sample_rate must be a positive int")
        array = np.asarray(samples)
        if array.ndim != 1:
            raise ValidationError("samples must be a 1-D array")
        if array.dtype == np.int16:
            pcm = np.ascontiguousarray(array)
        elif np.issubdtype(array.dtype, np.floating):
            if array.size and not bool(np.isfinite(array).all()):
                raise ValidationError("float samples must be finite values in [-1.0, 1.0]")
            if array.size and (float(np.min(array)) < -1.0 or float(np.max(array)) > 1.0):
                raise ValidationError("float samples must be within [-1.0, 1.0]")
            scaled = np.clip(array * 32768.0, -32768.0, 32767.0)
            pcm = np.ascontiguousarray(scaled.astype(np.int16))
        else:
            raise ValidationError("samples must be int16 or floating")
        destination = Path(path)
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with wave.open(str(destination), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(sample_rate)
                handle.writeframes(pcm.tobytes())
        except OSError as exc:
            raise FilesystemError(f"cannot write wav {destination}") from exc
        log.debug("filesystem.write_audio_wav", path=str(destination), frames=int(pcm.size))

    def read_text(self, path: Path, *, max_bytes: int) -> str:
        if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes < 0:
            raise FilesystemError("max_bytes must be a non-negative int")
        try:
            resolved = Path(path).resolve()
            size = resolved.stat().st_size
        except OSError as exc:
            raise FilesystemError(f"cannot read {path}") from exc
        if resolved.parent.name not in COMPILE_PARENT_NAMES:
            raise FilesystemError("read_text is compile-only for raw/compiled markdown")
        if resolved.suffix != COMPILE_SUFFIX:
            raise FilesystemError("read_text requires a .md suffix")
        if size > max_bytes:
            raise FilesystemError("file exceeds max_bytes")
        try:
            text = resolved.read_text(encoding="utf-8")
        except OSError as exc:
            raise FilesystemError(f"cannot read {resolved}") from exc
        log.debug("filesystem.read_text", path=str(resolved), bytes=size)
        return text
