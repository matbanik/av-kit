"""FFmpeg convert/probe/encode port protocol."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from avkit_core.domain.conversion import (
    CutOptions,
    ExtractOptions,
    FFmpegBinaries,
    GPUCapabilities,
    VideoEncodeOptions,
)
from avkit_core.domain.progress import ConvertOptions, MediaInfo, ProgressSnapshot


class MediaPort(Protocol):
    """Subprocess FFmpeg adapter surface."""

    def is_available(self) -> bool: ...

    def ffmpeg_version(self) -> str | None: ...

    def ffmpeg_binaries(self) -> FFmpegBinaries | None: ...

    def convert(self, input_path: Path, output_path: Path, options: ConvertOptions) -> None: ...

    def probe(self, file_path: Path) -> MediaInfo: ...

    def detect_gpu(self) -> GPUCapabilities: ...

    def encode(
        self,
        input_path: Path,
        output_path: Path,
        options: VideoEncodeOptions,
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
    ) -> None: ...

    def cut(
        self,
        input_path: Path,
        output_path: Path,
        options: CutOptions,
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
    ) -> None: ...

    def extract_stream(
        self,
        input_path: Path,
        output_path: Path,
        options: ExtractOptions,
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
    ) -> None: ...
