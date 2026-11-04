"""Filesystem write/export port protocol."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np


class FilesystemPort(Protocol):
    """Bounded file writes. read_text is compile-only and keyword-only."""

    def write_text_atomic(self, path: Path, text: str) -> None: ...

    def write_progress_export(self, output_dir: Path, video_ids_done: list[str]) -> None: ...

    def ensure_channel_dirs(self, output_dir: Path) -> None: ...

    def write_audio_wav(self, path: Path, samples: np.ndarray, sample_rate: int) -> None: ...

    def read_text(self, path: Path, *, max_bytes: int) -> str: ...
