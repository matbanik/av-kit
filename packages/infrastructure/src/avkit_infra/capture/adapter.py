"""mss grab + Pillow bake adapter."""

from __future__ import annotations

import io
import math
import os
import sys
import warnings
from collections.abc import Callable, Sequence
from pathlib import Path

import structlog
from PIL import (
    Image,
    ImageCms,
    ImageDraw,
    ImageFont,
    ImageOps,
    ImageStat,
    UnidentifiedImageError,
)

from avkit_core.domain.capture import (
    ANNOTATED_FORMATS,
    CAPTURE_MIN_EDGE_PX,
    AnnotatedFormat,
    Annotation,
    ArrowAnnotation,
    BBox,
    EraserAnnotation,
    HighlightAnnotation,
    ImageProbe,
    PixelateAnnotation,
    RectAnnotation,
    TextAnnotation,
    ViewFrame,
)
from avkit_core.domain.errors import (
    CaptureFailedError,
    CaptureNotSupportedError,
    ConflictError,
    InboxPathError,
    ValidationError,
)

log = structlog.get_logger(module="capture")

MSS_VIRTUAL_INDEX = 0
BLACK_LUM_MAX = 2.0
# ARROW_HEAD (MEU-83, D-12): head = max(ARROWHEAD_MIN_PX, ARROWHEAD_LENGTH_FACTOR * stroke).
ARROWHEAD_LENGTH_FACTOR = 5
ARROWHEAD_MIN_PX = 10
ARROWHEAD_ANGLE_RAD = 0.45
# ARROW_SHAFT_OVERLAP_PX (MEU-83, D-13): the shaft runs this far past the head base, so no
# background gap shows between them.
ARROW_SHAFT_OVERLAP_PX = 1
# BAKE_AA (MEU-83, D-14): arrows are drawn at SUPERSAMPLE x on their own tile, then LANCZOS down.
SUPERSAMPLE = 4
# The tile pad past stroke/2: the LANCZOS halo (3 px at 4x) plus 1, so the spread is never cut.
ARROW_TILE_PAD_PX = 4
FONT_CANDIDATES = ("segoeui.ttf", "arial.ttf")
# LOSSY_QUALITY (MEU-67, Human-approved): Pillow quality for JPEG and lossy WebP bake output.
LOSSY_QUALITY = 90
# IMPORT_ACCEPT (MEU-129, D-416, D-417): the fixed, path-free refusals of inspect_import.
IMPORT_OPEN_MESSAGE = "not an image av-kit can open (png, jpg, jpeg, webp)"
IMPORT_PIXEL_MESSAGE = "image is larger than the 89478485-pixel limit"
EXIF_ORIENTATION_TAG = 0x0112
_UPRIGHT_MODES = frozenset({"RGB", "RGBA", "L", "LA"})
# CROP_PIXELS (MEU-130, D-482): the modes a PNG stores, which a crop keeps; any other mode
# becomes RGBA or RGB. A CMYK, YCbCr or LAB source converts through its profile to sRGB
# (D-506 A), because PNG can't hold those colour spaces or their profiles.
_CROP_KEPT_MODES = frozenset({"1", "L", "LA", "P", "RGB", "RGBA", "I;16"})
_CROP_ICC_CONVERT_MODES = frozenset({"CMYK", "YCbCr", "LAB"})
_PIL_FORMAT: dict[str, str] = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}
NAMED_RGB: dict[str, tuple[int, int, int]] = {
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "yellow": (255, 255, 0),
    "green": (0, 128, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}


def arrowhead_vertices(
    from_xy: tuple[int, int],
    to_xy: tuple[int, int],
    stroke_width: int,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Return tip, left, and right vertices for an arrow head."""
    x1, y1 = from_xy
    x2, y2 = to_xy
    angle = math.atan2(float(y2 - y1), float(x2 - x1))
    head = max(ARROWHEAD_MIN_PX, stroke_width * ARROWHEAD_LENGTH_FACTOR)
    left = (
        x2 - head * math.cos(angle - ARROWHEAD_ANGLE_RAD),
        y2 - head * math.sin(angle - ARROWHEAD_ANGLE_RAD),
    )
    right = (
        x2 - head * math.cos(angle + ARROWHEAD_ANGLE_RAD),
        y2 - head * math.sin(angle + ARROWHEAD_ANGLE_RAD),
    )
    return ((float(x2), float(y2)), left, right)


def arrow_shaft_end(
    from_xy: tuple[int, int],
    to_xy: tuple[int, int],
    stroke_width: int,
) -> tuple[float, float] | None:
    """Return where the shaft ends (``SHAFT_END``), or ``None`` when only the head is drawn.

    The shaft stops ``ARROW_SHAFT_OVERLAP_PX`` past the head base. A zero-length arrow keeps
    its legacy ``from -> to`` shaft and has no head.
    """
    x1, y1 = from_xy
    x2, y2 = to_xy
    dx, dy = float(x2 - x1), float(y2 - y1)
    length = math.hypot(dx, dy)
    if length == 0:
        return (float(x2), float(y2))
    head = max(ARROWHEAD_MIN_PX, stroke_width * ARROWHEAD_LENGTH_FACTOR)
    back = head * math.cos(ARROWHEAD_ANGLE_RAD) - ARROW_SHAFT_OVERLAP_PX
    if length <= back:
        return None
    return (x2 - dx / length * back, y2 - dy / length * back)


def text_plate_box(x: int, y: int, text: str, font_size: int) -> tuple[int, int, int, int]:
    """Return Pillow ``la`` ink bbox ``(left, top, right, bottom)``."""
    font = _load_font(max(1, font_size))
    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    bbox = draw.textbbox((x, y), text, font=font, anchor="la")
    return (int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]))


def _color_rgb(color: str) -> tuple[int, int, int]:
    if color.startswith("#") and len(color) == 7:
        return (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
    return NAMED_RGB[color]


def _load_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    windir = os.environ.get("WINDIR", r"C:\Windows")
    fonts_dir = Path(windir) / "Fonts"
    for name in FONT_CANDIDATES:
        candidate = fonts_dir / name
        if not candidate.is_file():
            continue
        try:
            return ImageFont.truetype(str(candidate), font_size)
        except OSError:
            continue
    return ImageFont.load_default()


def region_clip(
    annotation: PixelateAnnotation | EraserAnnotation, width: int, height: int
) -> tuple[int, int, int, int] | None:
    """``REGION_RECT``: ``[x, x + width) x [y, y + height)`` within the image, else ``None``."""
    x0 = max(0, annotation.x)
    y0 = max(0, annotation.y)
    x1 = min(width, annotation.x + annotation.width)
    y1 = min(height, annotation.y + annotation.height)
    if x0 >= x1 or y0 >= y1:
        return None
    return (x0, y0, x1, y1)


def _apply_pixelate(canvas: Image.Image, annotation: PixelateAnnotation) -> Image.Image:
    # PIXELATE_BAKE: per-band box reduce (an RGBA reduce weights colour by alpha), NEAREST back
    # up, crop to the clipped rectangle, paste at its top-left.
    box = region_clip(annotation, canvas.width, canvas.height)
    if box is None:
        return canvas
    block = annotation.block_size
    region = canvas.crop(box)
    small = Image.merge(region.mode, [band.reduce(block) for band in region.split()])
    big = small.resize((small.width * block, small.height * block), Image.Resampling.NEAREST)
    canvas.paste(big.crop((0, 0, region.width, region.height)), box[:2])
    return canvas


def eraser_fill(canvas: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """``ERASER_SAMPLE``: the most frequent RGB in the ring around the clipped ``box``.

    The ring is the pixels 1 px outside the box (corners included, clipped to the image), or the
    box's own edge pixels when that is empty. A tie goes to the smallest packed value
    ``(r << 16) | (g << 8) | b``.
    """
    x0, y0, x1, y1 = box
    width, height = canvas.size
    outer = [(x, y) for x in range(x0 - 1, x1 + 1) for y in (y0 - 1, y1)]
    outer += [(x, y) for y in range(y0, y1) for x in (x0 - 1, x1)]
    ring = [(x, y) for x, y in outer if 0 <= x < width and 0 <= y < height]
    if not ring:
        ring = [
            (x, y)
            for y in range(y0, y1)
            for x in range(x0, x1)
            if x in (x0, x1 - 1) or y in (y0, y1 - 1)
        ]
    left, top = max(0, x0 - 1), max(0, y0 - 1)
    area = canvas.crop((left, top, min(width, x1 + 1), min(height, y1 + 1))).convert("RGB")
    data = area.tobytes()
    counts: dict[tuple[int, int, int], int] = {}
    for x, y in ring:
        i = ((y - top) * area.width + (x - left)) * 3
        rgb = (data[i], data[i + 1], data[i + 2])
        counts[rgb] = counts.get(rgb, 0) + 1
    top_count = max(counts.values())
    return min(
        (rgb for rgb, count in counts.items() if count == top_count),
        key=lambda rgb: (rgb[0] << 16) | (rgb[1] << 8) | rgb[2],
    )


def _apply_eraser(canvas: Image.Image, annotation: EraserAnnotation) -> Image.Image:
    # ERASER_SAMPLE on the canvas as it stands at this mark, filled at alpha 255.
    box = region_clip(annotation, canvas.width, canvas.height)
    if box is None:
        return canvas
    canvas.paste((*eraser_fill(canvas, box), 255), box)
    return canvas


def apply_region_pass(canvas: Image.Image, annotations: Sequence[Annotation]) -> Image.Image:
    """``REGION_PASS`` step 1: every region mark in list order; drawn marks are skipped."""
    for annotation in annotations:
        if isinstance(annotation, PixelateAnnotation):
            canvas = _apply_pixelate(canvas, annotation)
        elif isinstance(annotation, EraserAnnotation):
            canvas = _apply_eraser(canvas, annotation)
    return canvas


def _encode_view(image: Image.Image, suffix: str) -> bytes:
    """VIEW_FORMAT: encode a view as the source file's format (PNG keeps the mode)."""
    buffer = io.BytesIO()
    if suffix in (".jpg", ".jpeg"):
        image.convert("RGB").save(buffer, format="JPEG", quality=LOSSY_QUALITY)
    elif suffix == ".webp":
        has_alpha = image.mode in ("RGBA", "LA")
        image.convert("RGBA" if has_alpha else "RGB").save(
            buffer, format="WEBP", quality=LOSSY_QUALITY
        )
    else:
        if image.mode not in ("RGBA", "RGB", "L", "LA"):
            image = image.convert("RGBA" if "A" in image.getbands() else "RGB")
        image.save(buffer, format="PNG")
    return buffer.getvalue()


def _to_srgb(image: Image.Image, icc: bytes | None) -> tuple[Image.Image, bytes | None]:
    """D-506 A: CMYK, YCbCr or LAB pixels to RGB, through `icc` to sRGB when it builds."""
    if icc:
        srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
        try:
            managed = ImageCms.profileToProfile(
                image, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb, outputMode="RGB"
            )
        except (OSError, ValueError, ImageCms.PyCMSError):
            managed = None
        if managed is not None:
            return managed, srgb.tobytes()
    return image.convert("RGB"), None


class CaptureAdapter:
    """Windows mss grabber and Pillow annotator."""

    def __init__(
        self,
        *,
        mss_factory: Callable[[], object] | None = None,
        platform: str | None = None,
    ) -> None:
        self._mss_factory = mss_factory
        self._platform = sys.platform if platform is None else platform

    def capture_fullscreen(self, output_path: Path) -> ImageProbe:
        """Grab the virtual desktop (mss monitors[0]) and write a PNG."""
        self._require_windows()
        return self._grab_and_write(self._fullscreen_region, output_path)

    def capture_region(self, output_path: Path, bbox: BBox) -> ImageProbe:
        """Grab a virtual-desktop rectangle and write a PNG."""
        self._require_windows()
        if bbox.width < CAPTURE_MIN_EDGE_PX or bbox.height < CAPTURE_MIN_EDGE_PX:
            raise ValidationError(
                f"width and height must be >= {CAPTURE_MIN_EDGE_PX}"
            )
        region = {
            "left": bbox.x,
            "top": bbox.y,
            "width": bbox.width,
            "height": bbox.height,
        }
        return self._grab_and_write(lambda sct: region, output_path)

    def ensure_dir(self, path: Path) -> None:
        """Create the folder and its parents if missing (the flatten backup folder)."""
        path.mkdir(parents=True, exist_ok=True)

    def probe(self, path: Path) -> ImageProbe:
        """Open an image with Pillow and return pixel size plus byte length."""
        if not path.is_file():
            raise InboxPathError(f"{path} is not a file")
        try:
            with Image.open(path) as image:
                image.load()
                width, height = image.size
        except (UnidentifiedImageError, OSError) as exc:
            raise InboxPathError(f"{path} is not an image") from exc
        return ImageProbe(width=width, height=height, file_size=path.stat().st_size)

    def view(self, path: Path, frame: ViewFrame) -> bytes:
        """Return `frame` of the image in the file's own format, in memory (MEU-128, D-410).

        Writes no file. Errors name no path: the open failure and the size check are
        Console-visible API messages.
        """
        try:
            with Image.open(path) as opened:
                opened.load()
                image = opened.copy()
        except Exception as exc:
            # Pillow raises SyntaxError, ValueError and others for a damaged file, and an
            # OSError's text holds the path; each becomes the one fixed refusal (D-421).
            raise InboxPathError("the image could not be opened") from exc
        if image.size != (frame.source_width, frame.source_height):
            raise ConflictError(
                "the image file changed since the captures were listed; list them again and retry"
            )
        whole = (frame.x, frame.y, frame.width, frame.height) == (0, 0, *image.size)
        returned = (frame.returned_width, frame.returned_height)
        # RETURN_UNCHANGED: the whole image at scale 1 is the file itself.
        if whole and returned == image.size:
            try:
                return path.read_bytes()
            except OSError as exc:
                raise InboxPathError("the image could not be opened") from exc
        if image.mode in ("P", "PA"):
            # A palette image resizes with NEAREST whatever filter is given; convert it first.
            has_alpha = image.mode == "PA" or "transparency" in image.info
            image = image.convert("RGBA" if has_alpha else "RGB")
        box = (frame.x, frame.y, frame.x + frame.width, frame.y + frame.height)
        if not whole:
            image = image.crop(box)
        if image.size != returned:
            image = image.resize(returned, Image.Resampling.LANCZOS)
        return _encode_view(image, path.suffix.lower())

    def inspect_import(self, data: bytes) -> int:
        """IMPORT_ACCEPT: decode `data` in full and return its EXIF orientation (1 with no tag).

        Pillow only warns between 1x and 2x MAX_IMAGE_PIXELS, so the warning is an error here
        and the pixel count is checked as well. `verify()` passes a truncated JPEG, so the
        bytes are reopened and every pixel is loaded.
        """
        limit = Image.MAX_IMAGE_PIXELS
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            try:
                with Image.open(io.BytesIO(data)) as probe:
                    width, height = probe.size
                    if limit is not None and width * height > limit:
                        raise ValidationError(IMPORT_PIXEL_MESSAGE)
                    probe.verify()
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    orientation = image.getexif().get(EXIF_ORIENTATION_TAG, 1)
            except ValidationError:
                raise
            except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
                raise ValidationError(IMPORT_PIXEL_MESSAGE) from exc
            except Exception as exc:
                raise ValidationError(IMPORT_OPEN_MESSAGE) from exc
        if isinstance(orientation, int) and 2 <= orientation <= 8:
            return orientation
        return 1

    def write_upright_png(self, data: bytes, path: Path) -> ImageProbe:
        """IMPORT_UPRIGHT: apply the EXIF orientation and write the result as a PNG at `path`."""
        with Image.open(io.BytesIO(data)) as opened:
            upright = ImageOps.exif_transpose(opened)
        if upright.mode not in _UPRIGHT_MODES:
            alpha = upright.mode in ("P", "PA") and "transparency" in upright.info
            alpha = alpha or upright.mode.endswith("A")
            upright = upright.convert("RGBA" if alpha else "RGB")
        return self._write_png(upright, path)

    def crop(
        self,
        source: Path,
        box: tuple[int, int, int, int],
        source_size: tuple[int, int],
        out: Path,
    ) -> ImageProbe:
        """CROP_PIXELS: cut `box` from the original's pixels into a PNG at `out` (MEU-130).

        `box` is `(left, top, width, height)` inside the image, as `resolve_region` returns it.
        No resampling and no `exif_transpose`: the crop is the stored frame's pixels. The mode
        is kept when PNG stores it; the ICC profile is kept; EXIF, XMP and text are dropped.
        A CMYK, YCbCr or LAB source converts through its profile to sRGB and carries the
        sRGB profile; with no profile, or one that builds no transform, it converts plainly
        and carries none (D-506 A).
        The only refusals are the two fixed, path-free ones (D-481, D-482, D-476).
        """
        try:
            with Image.open(source) as opened:
                opened.load()
                image = opened.copy()
        except Exception as exc:
            # Pillow raises SyntaxError, ValueError and others for a damaged file, and an
            # OSError's text holds the path; each becomes the one fixed refusal (D-421).
            raise InboxPathError("the image could not be opened") from exc
        if image.size != source_size:
            raise ConflictError(
                "the image file changed since the captures were listed; list them again and retry"
            )
        left, top, width, height = box
        icc = image.info.get("icc_profile")
        transparency = image.info.get("transparency")
        cropped = image.crop((left, top, left + width, top + height))
        if image.mode in _CROP_KEPT_MODES:
            info: dict[str | tuple[int, int], object] = {}
            if transparency is not None:
                info["transparency"] = transparency
        else:
            info = {}
            if image.mode in _CROP_ICC_CONVERT_MODES:
                cropped, icc = _to_srgb(cropped, icc)
            else:
                has_alpha = "A" in image.mode or "a" in image.mode or transparency is not None
                cropped = cropped.convert("RGBA" if has_alpha else "RGB")
        if icc:
            info["icc_profile"] = icc
        # Only the ICC profile and the kept mode's transparency survive: no EXIF, XMP or text.
        cropped.info = info
        try:
            cropped.save(out, format="PNG")
            return self.probe(out)
        except Exception as exc:
            raise OSError("the crop could not be saved") from exc

    def bake(
        self,
        original_path: Path,
        annotations: Sequence[Annotation],
        output_path: Path,
        output_format: AnnotatedFormat = "png",
    ) -> ImageProbe:
        """Draw annotations onto a copy of the original; write `output_format` (PNG by default)."""
        if output_format not in ANNOTATED_FORMATS:
            raise ValidationError(f"output_format must be one of {', '.join(ANNOTATED_FORMATS)}")
        try:
            with Image.open(original_path) as opened:
                canvas = opened.convert("RGBA")
        except (UnidentifiedImageError, OSError) as exc:
            raise InboxPathError(f"{original_path} is not an image") from exc
        # REGION_PASS: region marks first, then the drawn marks painted over the result.
        canvas = apply_region_pass(canvas, annotations)
        for annotation in annotations:
            canvas = self._apply(canvas, annotation)
        if output_format == "png":
            return self._write_png(canvas.convert("RGB"), output_path)
        return self._write_lossy(canvas.convert("RGB"), output_path, output_format)

    def _require_windows(self) -> None:
        if self._platform != "win32":
            raise CaptureNotSupportedError("screen capture requires Windows")

    def _open_session(self) -> object:
        factory = self._mss_factory
        if factory is None:
            import mss as mss_mod

            factory = mss_mod.mss
        return factory()

    def _fullscreen_region(self, sct: object) -> object:
        monitors = getattr(sct, "monitors", None)
        if not isinstance(monitors, Sequence) or len(monitors) <= MSS_VIRTUAL_INDEX:
            raise CaptureFailedError("mss monitors are missing")
        return monitors[MSS_VIRTUAL_INDEX]

    def _grab_and_write(
        self,
        region_for: Callable[[object], object],
        output_path: Path,
    ) -> ImageProbe:
        session = self._open_session()
        try:
            if hasattr(session, "__enter__") and hasattr(session, "__exit__"):
                with session as sct:  # type: ignore[union-attr]
                    raw = self._call_grab(sct, region_for(sct))
            else:
                raw = self._call_grab(session, region_for(session))
        except (CaptureFailedError, CaptureNotSupportedError, ValidationError):
            raise
        except Exception as exc:
            raise CaptureFailedError(f"mss grab failed: {exc}") from exc
        image = self._shot_to_image(raw)
        self._reject_black_or_empty(image)
        return self._write_png(image.convert("RGB"), output_path)

    def _call_grab(self, sct: object, region: object) -> object:
        grab = getattr(sct, "grab", None)
        if not callable(grab):
            raise CaptureFailedError("mss session has no grab")
        return grab(region)

    def _shot_to_image(self, shot: object) -> Image.Image:
        size = getattr(shot, "size", None)
        rgb = getattr(shot, "rgb", None)
        if size is None or rgb is None:
            raise CaptureFailedError("mss returned an empty frame")
        try:
            width = int(size[0])
            height = int(size[1])
        except (TypeError, ValueError, IndexError) as exc:
            raise CaptureFailedError("mss returned an empty frame") from exc
        if width <= 0 or height <= 0:
            raise CaptureFailedError("mss returned an empty frame")
        if not isinstance(rgb, (bytes, bytearray)) or len(rgb) == 0:
            raise CaptureFailedError("mss returned an empty frame")
        try:
            return Image.frombytes("RGB", (width, height), bytes(rgb))
        except ValueError as exc:
            raise CaptureFailedError(f"mss frame decode failed: {exc}") from exc

    def _reject_black_or_empty(self, image: Image.Image) -> None:
        if image.width <= 0 or image.height <= 0:
            raise CaptureFailedError("captured frame is empty")
        mean = ImageStat.Stat(image.convert("L")).mean[0]
        if mean <= BLACK_LUM_MAX:
            raise CaptureFailedError("captured frame is black")

    def _write_png(self, image: Image.Image, output_path: Path) -> ImageProbe:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            image.save(output_path, format="PNG")
        except OSError as exc:
            if output_path.exists():
                output_path.unlink()
            raise CaptureFailedError(f"failed to write PNG: {exc}") from exc
        log.info("capture.wrote", path=str(output_path), width=image.width, height=image.height)
        return ImageProbe(
            width=image.width,
            height=image.height,
            file_size=output_path.stat().st_size,
        )

    def _write_lossy(self, image: Image.Image, output_path: Path, output_format: str) -> ImageProbe:
        pil_format = _PIL_FORMAT[output_format]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            image.save(output_path, format=pil_format, quality=LOSSY_QUALITY)
        except OSError as exc:
            if output_path.exists():
                output_path.unlink()
            raise CaptureFailedError(f"failed to write {pil_format}: {exc}") from exc
        log.info(
            "capture.wrote",
            path=str(output_path),
            format=pil_format,
            width=image.width,
            height=image.height,
        )
        return ImageProbe(
            width=image.width,
            height=image.height,
            file_size=output_path.stat().st_size,
        )

    def _apply(self, canvas: Image.Image, annotation: Annotation) -> Image.Image:
        if isinstance(annotation, (PixelateAnnotation, EraserAnnotation)):
            return canvas  # applied by apply_region_pass before the drawn marks
        if isinstance(annotation, HighlightAnnotation):
            return self._apply_highlight(canvas, annotation)
        if isinstance(annotation, ArrowAnnotation):
            return self._apply_arrow(canvas, annotation)
        if isinstance(annotation, RectAnnotation):
            return self._apply_rect(canvas, annotation)
        if isinstance(annotation, TextAnnotation):
            return self._apply_text(canvas, annotation)
        raise ValidationError(f"unsupported annotation type: {type(annotation)!r}")

    def _apply_highlight(self, canvas: Image.Image, annotation: HighlightAnnotation) -> Image.Image:
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        red, green, blue = _color_rgb(annotation.color)
        alpha = int(round(annotation.opacity * 255))
        x1 = annotation.x
        y1 = annotation.y
        x2 = annotation.x + annotation.width - 1
        y2 = annotation.y + annotation.height - 1
        draw.rectangle([x1, y1, x2, y2], fill=(red, green, blue, alpha))
        return Image.alpha_composite(canvas.convert("RGBA"), overlay)

    def _apply_arrow(self, canvas: Image.Image, annotation: ArrowAnnotation) -> Image.Image:
        # BAKE_AA: draw a coverage mask at SUPERSAMPLE x over the arrow's tile only, LANCZOS it
        # down, and composite the solid colour through it. Pixels outside the tile are untouched.
        overlay = canvas.convert("RGBA")
        color = _color_rgb(annotation.color)
        stroke = max(1, annotation.stroke_width)
        x1, y1 = annotation.from_xy
        x2, y2 = annotation.to_xy
        start = (float(x1), float(y1))
        end = arrow_shaft_end(annotation.from_xy, annotation.to_xy, annotation.stroke_width)
        head: tuple[tuple[float, float], ...] = ()
        if math.hypot(float(x2 - x1), float(y2 - y1)) != 0:
            head = arrowhead_vertices(annotation.from_xy, annotation.to_xy, annotation.stroke_width)
        points = [start, *([end] if end is not None else []), *head]
        pad = stroke / 2 + ARROW_TILE_PAD_PX
        left = max(0, math.floor(min(p[0] for p in points) - pad))
        top = max(0, math.floor(min(p[1] for p in points) - pad))
        right = min(overlay.width, math.ceil(max(p[0] for p in points) + pad) + 1)
        bottom = min(overlay.height, math.ceil(max(p[1] for p in points) + pad) + 1)
        if right <= left or bottom <= top:
            return overlay
        tile_size = (right - left, bottom - top)
        mask = Image.new("L", (tile_size[0] * SUPERSAMPLE, tile_size[1] * SUPERSAMPLE), 0)
        draw = ImageDraw.Draw(mask)
        centre = (SUPERSAMPLE - 1) / 2  # PIXEL_CENTRE: the middle of each pixel's block

        def big(point: tuple[float, float]) -> tuple[float, float]:
            return (
                SUPERSAMPLE * (point[0] - left) + centre,
                SUPERSAMPLE * (point[1] - top) + centre,
            )

        if end is not None:
            draw.line([big(start), big(end)], fill=255, width=SUPERSAMPLE * stroke)
        if head:
            draw.polygon([big(vertex) for vertex in head], fill=255)
        coverage = mask.resize(tile_size, Image.Resampling.LANCZOS)
        box = (left, top, right, bottom)
        tile = overlay.crop(box)
        solid = Image.new("RGBA", tile_size, (*color, 255))
        overlay.paste(Image.composite(solid, tile, coverage), (left, top))
        return overlay

    def _apply_rect(self, canvas: Image.Image, annotation: RectAnnotation) -> Image.Image:
        overlay = canvas.convert("RGBA")
        draw = ImageDraw.Draw(overlay)
        color = _color_rgb(annotation.color)
        x1 = annotation.x
        y1 = annotation.y
        x2 = annotation.x + annotation.width
        y2 = annotation.y + annotation.height
        draw.rectangle([x1, y1, x2, y2], outline=color, width=max(1, annotation.stroke_width))
        return overlay

    def _apply_text(self, canvas: Image.Image, annotation: TextAnnotation) -> Image.Image:
        overlay = canvas.convert("RGBA")
        draw = ImageDraw.Draw(overlay)
        font = _load_font(max(1, annotation.font_size))
        color = _color_rgb(annotation.color)
        bbox = text_plate_box(annotation.x, annotation.y, annotation.text, annotation.font_size)
        if annotation.bg_color is not None:
            draw.rectangle(bbox, fill=_color_rgb(annotation.bg_color))
        draw.text(
            (annotation.x, annotation.y),
            annotation.text,
            fill=color,
            font=font,
            anchor="la",
        )
        return overlay
