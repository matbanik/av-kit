"""Screen grab and image annotate ports. Adapters live in infrastructure."""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from avkit_core.domain.capture import AnnotatedFormat, Annotation, BBox, ImageProbe, ViewFrame


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
