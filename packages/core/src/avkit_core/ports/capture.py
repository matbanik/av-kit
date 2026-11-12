"""Screen grab and image annotate ports. Adapters live in infrastructure."""

from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Protocol

from avkit_core.domain.capture import AnnotatedFormat, Annotation, BBox, ImageProbe, ViewFrame
from avkit_core.domain.progress import MediaInfo


class ScreenCapturePort(Protocol):
    """OS screenshot surface. Implemented with mss in infrastructure."""

    def capture_fullscreen(self, output_path: Path) -> ImageProbe: ...

    def capture_region(self, output_path: Path, bbox: BBox) -> ImageProbe: ...


class ImageAnnotatePort(Protocol):
    """Probe and bake annotations onto an original image copy."""

    def probe(self, path: Path) -> ImageProbe: ...

    def bake(
        self,
        original_path: Path,
        annotations: Sequence[Annotation],
        output_path: Path,
        output_format: AnnotatedFormat = "png",
    ) -> ImageProbe: ...

    def ensure_dir(self, path: Path) -> None:
        """Create a folder (and parents) if missing; services never call mkdir (AC-12.8)."""
        ...

    def view(self, path: Path, frame: ViewFrame) -> bytes:
        """Return the image's bytes for `frame`: cropped, scaled and encoded in memory (MEU-128)."""
        ...

    def inspect_import(self, data: bytes) -> int:
        """Decode `data` in full and return its EXIF orientation, 1 with no tag (MEU-129)."""
        ...

    def write_upright_png(self, data: bytes, path: Path) -> ImageProbe:
        """Write `data` turned upright by its EXIF orientation as a PNG at `path` (MEU-129)."""
        ...

    def crop(
        self,
        source: Path,
        box: tuple[int, int, int, int],
        source_size: tuple[int, int],
        out: Path,
    ) -> ImageProbe:
        """CROP_PIXELS: write `box` (left, top, width, height) of `source` as a PNG at `out`.

        No resampling; the ICC profile is kept and no other metadata is written (MEU-130).
        """
        ...

    def sheet(
        self,
        cells: Sequence[bytes],
        *,
        grid: int,
        cell_size: tuple[int, int],
        labels: Sequence[str],
    ) -> bytes:
        """SHEET_TILE (MEU-135): `cells` tiled `grid` by `grid`, each labelled, as PNG bytes.

        Each cell is shrunk to fit `cell_size` (never enlarged) and centred on black; cells
        past `len(cells)` stay black. No file is written.
        """
        ...

    def export(
        self,
        source: Path,
        source_size: tuple[int, int],
        out: Path,
        *,
        fmt: str,
        size: tuple[int, int],
        quality: int | None,
    ) -> ImageProbe:
        """EXPORT_ENCODE (MEU-136): write `source` as `fmt` (png, jpeg or webp) at `size`.

        `source_size` is the size the caller listed; any other size is crop's fixed
        conflict. `size` never exceeds it. The ICC profile is kept and no other metadata
        is written (D-613, D-614, D-619). Writes `out` and returns its probe.
        """
        ...


# FRAME_PORT (MEU-134): how `grab_frame` seeks. "output" decodes from the start, for a raw
# stream with no duration (NO_DURATION).
FrameSeek = Literal["input", "output"]


class FramePort(Protocol):
    """Read a local video's streams and one of its frames. The FFmpeg adapter implements it."""

    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo: ...

    def grab_frame(
        self,
        path: Path,
        time_ms: int,
        *,
        seek: FrameSeek,
        timeout_s: float,
        box: tuple[int, int] | None = None,
    ) -> bytes:
        """FRAME_GRAB: the frame at `time_ms` as PNG bytes, or b"" when FFmpeg gives none.

        CELL_GRAB (MEU-135): with `box`, the frame is scaled down to fit inside it.
        """
        ...
