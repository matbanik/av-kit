"""Screen grab and image annotate ports. Adapters live in infrastructure."""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from avkit_core.domain.capture import AnnotatedFormat, Annotation, BBox, ImageProbe


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
