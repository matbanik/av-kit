"""CaptureService — inbox scan, register, grab, request, annotate, flatten, revert, remove."""

from __future__ import annotations

import contextlib
import json
import math
import os
import re
import shutil
import threading
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from io import BufferedWriter
from pathlib import Path
from typing import TypeVar
from uuid import uuid4

import structlog

from avkit_core.domain.capture import (
    ANNOTATED_EXT,
    ANNOTATED_FORMATS,
    ANNOTATED_SUFFIXES,
    CAPTURE_REQUEST_TRANSITIONS,
    REGION_MAX_EDGE_DEFAULT,
    REGION_MAX_EDGE_MAX,
    REGION_MAX_EDGE_MIN,
    AnnotatedFormat,
    Annotation,
    ArrowAnnotation,
    BBox,
    CaptureRequest,
    CaptureShot,
    CropResult,
    EraserAnnotation,
    HighlightAnnotation,
    ImageProbe,
    PixelateAnnotation,
    RectAnnotation,
    RedactAnnotation,
    RegionUnit,
    TextAnnotation,
    ViewFrame,
    clip_mark,
    resolve_region,
    view_frame,
)
from avkit_core.domain.enums import AnnotationType, CaptureRequestStatus, CaptureSource
from avkit_core.domain.errors import (
    AnnotationValidationError,
    CaptureFailedError,
    CaptureFlattenConflictError,
    CaptureRequestConflictError,
    ConflictError,
    InboxPathError,
    MediaProbeError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.progress import MediaInfo
from avkit_core.ports.capture import FramePort, FrameSeek, ImageAnnotatePort, ScreenCapturePort
from avkit_core.ports.storage import UnitOfWork
from avkit_core.services.settings import SettingsService
from avkit_core.services.video_input import (
    FRAMES_MAX,
    SHEET_GRID_DEFAULT,
    SHEET_GRID_MAX,
    SHEET_GRID_MIN,
    SheetCell,
    SheetShot,
    VideoFrame,
    VideoFrames,
    VideoSheet,
    duration_ms,
    format_timecode,
    frame_name,
    frame_times,
    parse_time,
    require_local_video,
    sheet_cell_size,
    sheet_label,
    sheet_name,
    sheet_spacing_ms,
    video_probe,
)

UoWFactory = Callable[[], UnitOfWork]
_T = TypeVar("_T")
Clock = Callable[[], datetime]
log = structlog.get_logger(module="capture")

SCAN_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
# IMPORT_ACCEPT (MEU-129, D-425, Human-approved): the largest file mode=import reads.
IMPORT_MAX_BYTES = 50_000_000
# IMPORT_NAME (MEU-129, D-420): the copy's stem.
IMPORT_STEM_MAX = 100
IMPORT_STEM_FALLBACK = "import"
_IMPORT_STEM_DROP = re.compile(r"[^\w\- ]+")
WINDOWS_RESERVED_STEMS = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{n}" for n in range(1, 10)}
    | {f"LPT{n}" for n in range(1, 10)}
)
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
REQUEST_TTL_S = 120
SIDECAR_SUFFIX = ".ann.json"
SIDECAR_VERSION = 1
ANNOTATION_CLAMP_MIN = 0
# MEU-67 flatten with backup (plan 2026-10-02-capture-flatten-backup §Single-statement contracts).
BACKUP_DIR_DEFAULT_NAME = ".avkit-backup"
TMP_SUFFIX = ".avkit-tmp"


def _is_file(path: Path) -> bool:
    """`Path.is_file`, with a denied lookup read as missing, so its path-bearing text stays out."""
    try:
        return path.is_file()
    except OSError:
        return False
BACKUP_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"
FLATTEN_PNG_SUFFIX = ".png"
CONVERTIBLE_SUFFIXES = frozenset({".jpg", ".jpeg", ".webp"})
CONVERT_STEM_TAG = "-converted"
# CAPTURE_FILE_LOCK: one process lock over every capture file mutation and the scan's row pruning.
# The API is a single uvicorn process; this lock is not reentrant, so a held section never calls
# another locked public method.
CAPTURE_FILE_LOCK = threading.Lock()
# FRAME_DEADLINE (MEU-134, D-577 A): a frames call commits nothing after this many seconds.
FRAMES_DEADLINE_S = 100
# FRAME_DEADLINE (e), the return gate (MEU-134, D-587): the call answers by FRAMES_RETURN_S,
# and waits COMMIT_WAIT_S more only for a worker that is already committing.
FRAMES_RETURN_S = 105
COMMIT_WAIT_S = 6
# FRAME_DEADLINE (e): the worker thread's name and the caller's join step.
FRAMES_WORKER = "avkit-frames"
FRAMES_JOIN_STEP_S = 0.05
# FRAME_WRITE: a grab's bytes must start with this, and the masked failure's fixed text.
PNG_SIGNATURE = bytes.fromhex("89504e470d0a1a0a")
FRAMES_NOT_WRITTEN = "the frames could not be written"
# FRAME_CHECKS' fixed refusals. None echoes the input.
FRAMES_EITHER = "use either at or count"
FRAMES_AT_RANGE = f"at takes 1 to {FRAMES_MAX} times"
FRAMES_COUNT_RANGE = f"count must be 1 to {FRAMES_MAX}"
FRAMES_NOT_PROBED = "the file could not be probed"
FRAMES_NOT_VIDEO = "not a video: no video stream"
FRAMES_BEFORE_END = "start must be before end"
FRAMES_NO_DURATION = "count needs a duration; this video has none, so use at"
# SHEET_DEADLINE (MEU-135, D-601 A): the sheet call's deadline, its return gate and its worker
# thread's name. It shares COMMIT_WAIT_S and FRAMES_JOIN_STEP_S with frames.
SHEET_DEADLINE_S = 100
SHEET_RETURN_S = 105
SHEET_WORKER = "avkit-sheet"
# SHEET_WRITE's masked failure and SHEET_CHECKS' fixed refusals (D-599). None echoes the input.
SHEET_NOT_WRITTEN = "the sheet could not be written"
SHEET_NO_DURATION = "sheet needs a duration; this video has none"
SHEET_GRID_RANGE = f"grid must be {SHEET_GRID_MIN} to {SHEET_GRID_MAX}"
# The view's own max_edge refusal (domain/capture.py), the same words for a sheet.
SHEET_EDGE_RANGE = f"max_edge must be between {REGION_MAX_EDGE_MIN} and {REGION_MAX_EDGE_MAX}"

# CROP_NAME (MEU-130, D-483): a crop's file name. A given `name` keeps these characters only.
CROP_NAME_MAX = 80
CROP_STEM_TAG = "-crop"
CROP_RESERVED_PREFIX = "crop_"
_CROP_NAME_DROP = re.compile(r"[^A-Za-z0-9 ._-]")
_CROP_NAME_STRIP = " ._-"
CROP_NAME_LENGTH = f"name must be 1 to {CROP_NAME_MAX} characters"
CROP_NAME_UNUSABLE = (
    "name has no usable characters; use letters, digits, space, dot, underscore or hyphen"
)
CROP_NAME_ANNOTATED = "name may not end in .annotated"
# A crop stem is taken when an inbox-root entry is the stem plus one of these, case-folded.
CROP_TAKEN_SUFFIXES: tuple[str, ...] = (
    *SCAN_EXTENSIONS,
    SIDECAR_SUFFIX,
    *ANNOTATED_SUFFIXES,
    f".png{TMP_SUFFIX}",
)
# CROP_CLEANUP (D-476): raised before the crop is cut, these are refusals and pass unchanged.
CROP_REFUSALS: tuple[type[Exception], ...] = (
    ValidationError,
    NotFoundError,
    ConflictError,
    AnnotationValidationError,
    InboxPathError,
)

# EXPORT_CHECKS, EXPORT_NAME and EXPORT_WRITE (MEU-136): the formats, bounds, names and
# fixed texts of POST /captures/{id}/export. None echoes the input (D-609, D-610, D-615).
EXPORT_FORMATS = ("png", "jpeg", "webp")
EXPORT_SUFFIXES: dict[str, str] = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}
EXPORT_STEM_TAG = "-export"
EXPORT_STEM_FALLBACK = "export"
EXPORT_MAX_EDGE_MAX = 16383
# The largest edge each lossy format stores (D-610).
EXPORT_EDGE_LIMIT: dict[str, int] = {"jpeg": 65500, "webp": 16383}
EXPORT_QUALITY_PNG = "quality applies to jpeg and webp only"
EXPORT_TOO_LARGE = "the export is too large for this format; lower max_edge"
EXPORT_NOT_WRITTEN = "the export could not be written"
# EXPORT_WRITE: raised before the encode has run, these are refusals and pass unchanged.
EXPORT_REFUSALS: tuple[type[Exception], ...] = CROP_REFUSALS


@dataclass(frozen=True)
class ExportResult:
    """EXPORT_WRITE (MEU-136): the export's new shot, its source's id and its file size."""

    shot: CaptureShot
    source_id: str
    bytes: int


def crop_name_stem(name: str) -> str:
    """CROP_NAME: a caller's `name` made into a crop stem, or a fixed 422 that never repeats it."""
    if not 1 <= len(name) <= CROP_NAME_MAX:
        raise ValidationError(CROP_NAME_LENGTH)
    text = _CROP_NAME_DROP.sub("", name).strip(_CROP_NAME_STRIP)
    if text.lower().endswith(FLATTEN_PNG_SUFFIX):
        text = text[: -len(FLATTEN_PNG_SUFFIX)].strip(_CROP_NAME_STRIP)
    if text == "":
        raise ValidationError(CROP_NAME_UNUSABLE)
    if len(text) > CROP_NAME_MAX:
        raise ValidationError(CROP_NAME_LENGTH)
    if text.lower().endswith(".annotated"):
        raise ValidationError(CROP_NAME_ANNOTATED)
    # Windows reserves CON, NUL and the rest with any extension, so the part before a dot counts.
    if text.split(".", 1)[0].rstrip(" ").upper() in WINDOWS_RESERVED_STEMS:
        return f"{CROP_RESERVED_PREFIX}{text}"
    return text


def crop_default_stem(source_stem: str) -> str:
    """CROP_NAME: `{stem}-crop` from the source's stem, cut to IMPORT_STEM_MAX characters."""
    stem = source_stem[:IMPORT_STEM_MAX].strip(_CROP_NAME_STRIP)
    return f"{stem}{CROP_STEM_TAG}" if stem else CROP_STEM_TAG.lstrip("-")


def export_size(width: int, height: int, max_edge: int | None) -> tuple[int, int]:
    """EXPORT_SIZE (MEU-136): the long edge at `max_edge`, never enlarged.

    Integers only: the short edge is `max_edge * short / long` rounded half up, at least 1,
    and the pair keeps the source's orientation.
    """
    long_edge = max(width, height)
    if max_edge is None or max_edge >= long_edge:
        return (width, height)
    short_edge = min(width, height)
    scaled = max(1, (2 * max_edge * short_edge + long_edge) // (2 * long_edge))
    return (max_edge, scaled) if width >= height else (scaled, max_edge)


def export_stem(source_stem: str) -> str:
    """EXPORT_NAME (MEU-136, D-612): `{stem}-export`, its stem made safe, or `export`."""
    text = _IMPORT_STEM_DROP.sub("_", source_stem).strip(" _-")[:IMPORT_STEM_MAX]
    text = text.strip(" _-")
    return f"{text}{EXPORT_STEM_TAG}" if text else EXPORT_STEM_FALLBACK


def resolve_backup_dir(raw: str, inbox: Path) -> Path:
    """BACKUP_DIR_RULE: '' derives {inbox}/.avkit-backup; else absolute after ~, never the inbox."""
    text = raw.strip()
    if text == "":
        return inbox / BACKUP_DIR_DEFAULT_NAME
    candidate = Path(text).expanduser()
    if not candidate.is_absolute():
        raise CaptureFlattenConflictError("capture.backup_dir must be an absolute folder path")
    resolved = candidate.resolve()
    if resolved == inbox.resolve():
        raise CaptureFlattenConflictError("capture.backup_dir must not be the inbox folder itself")
    return resolved


def import_stem(stem: str) -> str:
    """IMPORT_NAME: the source stem made safe for a file name in the inbox."""
    text = _IMPORT_STEM_DROP.sub("_", stem).strip(" _-")[:IMPORT_STEM_MAX]
    if text == "":
        return IMPORT_STEM_FALLBACK
    if text.upper() in WINDOWS_RESERVED_STEMS:
        return f"{IMPORT_STEM_FALLBACK}_{text}"
    return text


def _backup_pattern(stem: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(stem)}\.(\d{{8}}-\d{{6}})(?:_(\d+))?\.png$")


def latest_backup_in(backup_dir: Path, stem: str) -> Path | None:
    """LATEST_BACKUP: newest `{stem}.{YYYYMMDD-HHMMSS}[_n].png` by (timestamp, n), not mtime."""
    if not backup_dir.is_dir():
        return None
    pattern = _backup_pattern(stem)
    best: Path | None = None
    best_key: tuple[str, int] | None = None
    for child in backup_dir.iterdir():
        match = pattern.match(child.name)
        if match is None or not child.is_file():
            continue
        key = (match.group(1), int(match.group(2) or 1))
        if best_key is None or key > best_key:
            best, best_key = child, key
    return best


def backup_path_for(backup_dir: Path, stem: str, stamp: datetime) -> Path:
    """BACKUP_NAME: `{stem}.{YYYYMMDD-HHMMSS}.png`, then `_2`, `_3` … when that name is taken."""
    base = stamp.strftime(BACKUP_TIMESTAMP_FORMAT)
    candidate = backup_dir / f"{stem}.{base}.png"
    index = 2
    while candidate.exists():
        candidate = backup_dir / f"{stem}.{base}_{index}.png"
        index += 1
    return candidate


def annotated_path_for(original: Path, output_format: AnnotatedFormat) -> Path:
    """The Save overlay sibling for `output_format` (ANNOTATED_FORMATS)."""
    return original.with_name(f"{original.stem}.annotated{ANNOTATED_EXT[output_format]}")


def _annotated_siblings(original: Path) -> list[Path]:
    return [original.with_name(f"{original.stem}{suffix}") for suffix in ANNOTATED_SUFFIXES]


def _sidecar_for(original: Path) -> Path:
    return original.with_name(f"{original.stem}{SIDECAR_SUFFIX}")


def parse_sidecar_document(payload: object) -> list[object]:
    """Return sidecar annotation objects, ignoring unknown top-level keys."""
    if not isinstance(payload, dict):
        raise AnnotationValidationError("sidecar must be an object")
    annotations = payload.get("annotations", [])
    if not isinstance(annotations, list):
        raise AnnotationValidationError("annotations must be a list")
    parsed: list[object] = []
    for item in annotations:
        if not isinstance(item, dict):
            raise AnnotationValidationError("annotation must be an object")
        parsed.append(item)
    return parsed


def _wire_point(value: object, field: str) -> tuple[object, object]:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise AnnotationValidationError(f"{field} must be a pair")
    return (value[0], value[1])


def _annotation_from_wire(item: object) -> Annotation:
    if not isinstance(item, dict):
        raise AnnotationValidationError("annotation must be an object")
    kind = item.get("type")
    try:
        if kind == AnnotationType.Arrow.to_wire():
            return ArrowAnnotation(
                from_xy=_wire_point(item["from"], "from"),  # type: ignore[arg-type]
                to_xy=_wire_point(item["to"], "to"),  # type: ignore[arg-type]
                color=item["color"],
                stroke_width=item["stroke_width"],
            )
        if kind == AnnotationType.Rect.to_wire():
            return RectAnnotation(
                x=item["x"],
                y=item["y"],
                width=item["width"],
                height=item["height"],
                color=item["color"],
                stroke_width=item["stroke_width"],
            )
        if kind == AnnotationType.Highlight.to_wire():
            return HighlightAnnotation(
                x=item["x"],
                y=item["y"],
                width=item["width"],
                height=item["height"],
                color=item["color"],
                opacity=item["opacity"],
            )
        if kind == AnnotationType.Text.to_wire():
            return TextAnnotation(
                x=item["x"],
                y=item["y"],
                text=item["text"],
                color=item["color"],
                font_size=item["font_size"],
                bg_color=item.get("bg_color"),
            )
        if kind == AnnotationType.Pixelate.to_wire():
            return PixelateAnnotation(
                x=item["x"],
                y=item["y"],
                width=item["width"],
                height=item["height"],
                block_size=item["block_size"],
            )
        if kind == AnnotationType.Eraser.to_wire():
            return EraserAnnotation(
                x=item["x"],
                y=item["y"],
                width=item["width"],
                height=item["height"],
            )
        if kind == AnnotationType.Redact.to_wire():
            # REDACT_WIRE (D-682): exactly these keys; the sidecar always carries the colour.
            extra = sorted(set(item) - set(("type", "x", "y", "width", "height", "color")))
            if extra:
                raise AnnotationValidationError(f"unexpected redact field(s): {extra}")
            return RedactAnnotation(
                x=item["x"],
                y=item["y"],
                width=item["width"],
                height=item["height"],
                color=item["color"],
            )
    except KeyError as exc:
        raise AnnotationValidationError(f"missing annotation field: {exc}") from exc
    raise AnnotationValidationError(f"unsupported annotation type: {kind!r}")


def annotations_from_sidecar(payload: object) -> list[Annotation]:
    """Parse sidecar JSON into domain annotations. Unknown types are 422, not []."""
    return [_annotation_from_wire(item) for item in parse_sidecar_document(payload)]


def annotations_to_wire(items: Sequence[Annotation]) -> list[dict[str, object]]:
    """Serialize domain annotations to the annotate/GET-detail wire list."""
    return [_annotation_to_wire(item) for item in items]


def _clamp_int(value: int, lo: int, hi: int) -> int:
    if value < lo:
        return lo
    if value > hi:
        return hi
    return value


def _annotation_to_wire(annotation: Annotation) -> dict[str, object]:
    if isinstance(annotation, ArrowAnnotation):
        return {
            "type": AnnotationType.Arrow.to_wire(),
            "from": [annotation.from_xy[0], annotation.from_xy[1]],
            "to": [annotation.to_xy[0], annotation.to_xy[1]],
            "color": annotation.color,
            "stroke_width": annotation.stroke_width,
        }
    if isinstance(annotation, RectAnnotation):
        return {
            "type": AnnotationType.Rect.to_wire(),
            "x": annotation.x,
            "y": annotation.y,
            "width": annotation.width,
            "height": annotation.height,
            "color": annotation.color,
            "stroke_width": annotation.stroke_width,
        }
    if isinstance(annotation, HighlightAnnotation):
        return {
            "type": AnnotationType.Highlight.to_wire(),
            "x": annotation.x,
            "y": annotation.y,
            "width": annotation.width,
            "height": annotation.height,
            "color": annotation.color,
            "opacity": annotation.opacity,
        }
    if isinstance(annotation, TextAnnotation):
        payload: dict[str, object] = {
            "type": AnnotationType.Text.to_wire(),
            "x": annotation.x,
            "y": annotation.y,
            "text": annotation.text,
            "color": annotation.color,
            "font_size": annotation.font_size,
        }
        if annotation.bg_color is not None:
            payload["bg_color"] = annotation.bg_color
        return payload
    if isinstance(annotation, PixelateAnnotation):
        return {
            "type": AnnotationType.Pixelate.to_wire(),
            "x": annotation.x,
            "y": annotation.y,
            "width": annotation.width,
            "height": annotation.height,
            "block_size": annotation.block_size,
        }
    if isinstance(annotation, EraserAnnotation):
        return {
            "type": AnnotationType.Eraser.to_wire(),
            "x": annotation.x,
            "y": annotation.y,
            "width": annotation.width,
            "height": annotation.height,
        }
    if isinstance(annotation, RedactAnnotation):
        return {
            "type": AnnotationType.Redact.to_wire(),
            "x": annotation.x,
            "y": annotation.y,
            "width": annotation.width,
            "height": annotation.height,
            "color": annotation.color,
        }
    raise AnnotationValidationError(f"unsupported annotation type: {type(annotation)!r}")


class _FramesGate:
    """FRAME_DEADLINE (e) and SHEET_DEADLINE (e): what a call and its worker share, under `lock`.

    `state` is `running`, `committing` or `abandoned`; `last_ms` is the call's last time once
    it is known, the time an abandoned call reports.
    """

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.state = "running"
        self.last_ms = 0
        self.done = False
        self.error: BaseException | None = None


class _FrameFailed(Exception):
    """Internal to FRAME_WRITE: a failure the caller reports as `frame grab failed at t`."""

    def __init__(self, ms: int) -> None:
        super().__init__(ms)
        self.ms = ms


def _frame_failed_text(ms: int) -> str:
    return f"frame grab failed at {format_timecode(ms)}"


def _past_end(ms: int, total_ms: int) -> ValidationError:
    return ValidationError(
        f"time {format_timecode(ms)} is past the end ({format_timecode(total_ms)})"
    )


class CaptureService:
    """Synchronous capture inbox and annotation service. Not a processor queue."""

    def __init__(
        self,
        uow_factory: UoWFactory,
        *,
        capture: ScreenCapturePort,
        annotate: ImageAnnotatePort,
        settings: SettingsService,
        clock: Clock | None = None,
        frames: FramePort | None = None,
        monotonic: Callable[[], float] | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._capture = capture
        self._annotate = annotate
        self._settings = settings
        self._clock = clock if clock is not None else (lambda: datetime.now(UTC))
        self._frames = frames
        self._monotonic = monotonic if monotonic is not None else time.monotonic

    def scan_inbox(self) -> list[CaptureShot]:
        """Upsert inbox images, drop rows whose original vanished, and clear stale derived paths."""
        inbox = self._inbox()
        with CAPTURE_FILE_LOCK, self._uow_factory() as uow:
            if inbox.is_dir():
                for child in inbox.iterdir():
                    if not child.is_file():
                        continue
                    if child.suffix.lower() not in SCAN_EXTENSIONS:
                        continue
                    if child.name.lower().endswith(ANNOTATED_SUFFIXES):
                        continue
                    resolved = child.resolve()
                    probe = self._annotate.probe(resolved)
                    now = self._now()
                    existing = uow.capture_shots.get_by_path(resolved)
                    if existing is None:
                        uow.capture_shots.add(
                            CaptureShot(
                                id=str(uuid4()),
                                original_path=resolved,
                                annotated_path=None,
                                sidecar_path=None,
                                display_name=resolved.name,
                                width=probe.width,
                                height=probe.height,
                                file_size=probe.file_size,
                                source=CaptureSource.Scan,
                                created_at=now,
                                updated_at=now,
                            )
                        )
                    elif existing.file_size != probe.file_size:
                        uow.capture_shots.save(
                            replace(
                                existing,
                                width=probe.width,
                                height=probe.height,
                                file_size=probe.file_size,
                                updated_at=now,
                            )
                        )
            for shot in list(uow.capture_shots.list()):
                if not shot.original_path.is_file():
                    uow.capture_shots.delete(shot.id)
                    continue
                # RECONCILE (MEU-84, D-15): clear each derived path whose file is gone, per
                # field, and save only when one changed.
                annotated = shot.annotated_path
                if annotated is not None and not annotated.is_file():
                    annotated = None
                sidecar = shot.sidecar_path
                if sidecar is not None and not sidecar.is_file():
                    sidecar = None
                if (annotated, sidecar) != (shot.annotated_path, shot.sidecar_path):
                    uow.capture_shots.save(
                        replace(
                            shot,
                            annotated_path=annotated,
                            sidecar_path=sidecar,
                            updated_at=self._now(),
                        )
                    )
            return list(uow.capture_shots.list())

    def list_shots(self) -> list[CaptureShot]:
        """Expire stale requests, scan the inbox, return newest first."""
        self.expire_stale_requests()
        self.scan_inbox()
        with self._uow_factory() as uow:
            shots = list(uow.capture_shots.list())
        return sorted(
            shots,
            key=lambda shot: (-shot.created_at.timestamp(), shot.display_name.lower()),
        )

    def get_shot(self, shot_id: str) -> CaptureShot:
        """Return one shot or raise NotFoundError."""
        self.expire_stale_requests()
        with self._uow_factory() as uow:
            shot = uow.capture_shots.get(shot_id)
        if shot is None:
            raise NotFoundError(f"capture shot {shot_id} not found")
        return shot

    def load_shot_annotations(self, shot_id: str) -> list[Annotation]:
        """Read sidecar annotations for a shot. Missing file is []. Malformed is 422."""
        shot = self.get_shot(shot_id)
        sidecar = shot.original_path.with_name(f"{shot.original_path.stem}{SIDECAR_SUFFIX}")
        if not sidecar.is_file():
            return []
        try:
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AnnotationValidationError("sidecar is malformed") from exc
        return annotations_from_sidecar(payload)

    def register_shot(self, path: Path, source: CaptureSource) -> CaptureShot:
        """Insert or return the existing row for an inbox original."""
        inbox = self._inbox()
        resolved = self._require_inbox_file(path, inbox)
        probe = self._annotate.probe(resolved)
        now = self._now()
        with self._uow_factory() as uow:
            return self._upsert_shot(uow, resolved, probe, now, source)

    def import_image(self, path: Path) -> CaptureShot:
        """IMPORT_MODE: copy a local image into the inbox root, or register one already there.

        Every refusal is a fixed message that names no path (D-416), and nothing is written
        until every check has passed. The source file is only read.
        """
        if not path.is_absolute():
            raise InboxPathError("path must be absolute")
        inbox = self._inbox()
        try:
            resolved, data = self._read_import(path, inbox)
        except OSError as exc:
            # A denied folder or a failed lookup carries the path in its text (D-421).
            raise InboxPathError("the file could not be read") from exc
        in_root = resolved.parent == inbox
        orientation = self._annotate.inspect_import(data)
        if in_root:
            return self._import_in_place(resolved)
        return self._import_copy(resolved, inbox, data, orientation)

    @staticmethod
    def _read_import(path: Path, inbox: Path) -> tuple[Path, bytes]:
        """IMPORT_ACCEPT's file checks, in order. An `OSError` from any of them propagates."""
        if not path.exists():
            raise InboxPathError("no file at that path")
        if not path.is_file():
            raise InboxPathError("path is not a regular file")
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            raise InboxPathError("not an image av-kit can open (png, jpg, jpeg, webp)")
        size = path.stat().st_size
        if size > IMPORT_MAX_BYTES:
            raise InboxPathError(
                f"file is {math.ceil(size / 1_000_000)} MB; "
                f"the import limit is {IMPORT_MAX_BYTES // 1_000_000} MB"
            )
        resolved = path.resolve()
        if resolved.parent == inbox and resolved.name.lower().endswith(ANNOTATED_SUFFIXES):
            raise InboxPathError("this file is an annotated copy; import its original instead")
        return resolved, path.read_bytes()

    def _import_in_place(self, resolved: Path) -> CaptureShot:
        """IMPORT_IN_PLACE: an existing row keeps its source; a new row is `Import`."""
        with CAPTURE_FILE_LOCK, self._uow_factory() as uow:
            try:
                probe = self._annotate.probe(resolved)
            except (InboxPathError, OSError) as exc:
                raise InboxPathError("the image could not be opened") from exc
            now = self._now()
            existing = uow.capture_shots.get_by_path(resolved)
            if existing is None:
                return self._upsert_shot(uow, resolved, probe, now, CaptureSource.Import)
            if existing.file_size == probe.file_size:
                return existing
            updated = replace(
                existing,
                width=probe.width,
                height=probe.height,
                file_size=probe.file_size,
                updated_at=now,
            )
            uow.capture_shots.save(updated)
            return updated

    def frames_from_video(
        self,
        path: str,
        *,
        at: Sequence[object] | None = None,
        count: int | None = None,
        start: object | None = None,
        end: object | None = None,
    ) -> VideoFrames:
        """FRAME_CHECKS to FRAME_WRITE (MEU-134): stills from a local video as new shots.

        The body runs on a daemon worker named `avkit-frames`; this call waits for it in
        `FRAMES_JOIN_STEP_S` steps and answers by FRAME_DEADLINE (e)'s return gate whatever
        the body is waiting on. The worker's error is raised here as the same object, outside
        any `except` clause, so its `__context__` stays `None`.
        """

        def body(gate: _FramesGate, deadline: float) -> VideoFrames:
            return self._frames_body(gate, deadline, path, at, count, start, end)

        return self._run_gated(
            FRAMES_WORKER, FRAMES_DEADLINE_S, FRAMES_RETURN_S, FRAMES_NOT_WRITTEN, body
        )

    def sheet_from_video(
        self,
        path: str,
        *,
        start: object | None = None,
        end: object | None = None,
        grid: int = SHEET_GRID_DEFAULT,
        max_edge: int = REGION_MAX_EDGE_DEFAULT,
    ) -> VideoSheet:
        """SHEET_CHECKS to SHEET_WRITE (MEU-135): one labelled grid of a span as a new shot.

        The body runs on a daemon worker named `avkit-sheet` under SHEET_DEADLINE, through the
        same return gate as frames (`_run_gated`).
        """

        def body(gate: _FramesGate, deadline: float) -> VideoSheet:
            return self._sheet_body(gate, deadline, path, start, end, grid, max_edge)

        return self._run_gated(
            SHEET_WORKER, SHEET_DEADLINE_S, SHEET_RETURN_S, SHEET_NOT_WRITTEN, body
        )

    def _run_gated(
        self,
        worker_name: str,
        deadline_s: float,
        return_s: float,
        not_written: str,
        body: Callable[[_FramesGate, float], _T],
    ) -> _T:
        """FRAME_DEADLINE (e) and SHEET_DEADLINE (e): run `body` on a daemon worker.

        The clock starts here. This call waits in `FRAMES_JOIN_STEP_S` steps and answers by
        `return_s`, or by `return_s + COMMIT_WAIT_S` while the worker is committing, whatever
        the body is waiting on. An abandoned call reports `frame grab failed at` its last time;
        a commit that outlasts the wait gives the masked `not_written`. The worker's error is
        raised here as the same object, outside any `except` clause, so its `__context__`
        stays `None`.
        """
        began = self._monotonic()
        deadline = began + deadline_s
        gate = _FramesGate()
        results: list[_T] = []

        def work() -> None:
            error: BaseException | None = None
            try:
                results.append(body(gate, deadline))
            except BaseException as exc:  # handed to the caller, which raises it
                error = exc
            with gate.lock:
                gate.error = error
                gate.done = True

        worker = threading.Thread(target=work, name=worker_name, daemon=True)
        worker.start()
        returned: BaseException | None = None
        while True:
            worker.join(FRAMES_JOIN_STEP_S)
            elapsed = self._monotonic() - began
            with gate.lock:
                if gate.done:
                    break
                if elapsed < return_s:
                    continue
                if gate.state == "running":
                    gate.state = "abandoned"
                state = gate.state
                last_ms = gate.last_ms
            if state == "abandoned":
                returned = ValidationError(_frame_failed_text(last_ms))
                break
            if elapsed >= return_s + COMMIT_WAIT_S:
                returned = CaptureFailedError(not_written)
                break
        if returned is None:
            returned = gate.error
        if returned is None and results:
            return results[0]
        if returned is None:
            returned = CaptureFailedError(not_written)
        raise returned

    def _sheet_body(
        self,
        gate: _FramesGate,
        deadline: float,
        path: str,
        start: object | None,
        end: object | None,
        grid: object,
        max_edge: object,
    ) -> VideoSheet:
        """SHEET_CHECKS, then SHEET_WRITE's three phases, on the worker thread."""
        resolved = require_local_video(path)
        start_ms = None if start is None else parse_time(start)
        end_ms = None if end is None else parse_time(end)
        if (
            isinstance(grid, bool)
            or not isinstance(grid, int)
            or not SHEET_GRID_MIN <= grid <= SHEET_GRID_MAX
        ):
            raise ValidationError(SHEET_GRID_RANGE)
        if (
            isinstance(max_edge, bool)
            or not isinstance(max_edge, int)
            or not REGION_MAX_EDGE_MIN <= max_edge <= REGION_MAX_EDGE_MAX
        ):
            raise ValidationError(SHEET_EDGE_RANGE)
        if start_ms is not None:
            gate.last_ms = start_ms
        port = self._frames
        if port is None:
            raise CaptureFailedError(SHEET_NOT_WRITTEN)
        info: MediaInfo | None = None
        try:
            info = port.probe(resolved, timeout_s=deadline - self._monotonic())
        except MediaProbeError:
            info = None
        if info is None:
            raise ValidationError(FRAMES_NOT_PROBED)
        if info.video_codec is None:
            raise ValidationError(FRAMES_NOT_VIDEO)
        total = duration_ms(info.duration)
        if total is None:
            raise ValidationError(SHEET_NO_DURATION)
        first, last = self._span_ms(total, start_ms, end_ms)
        times = frame_times(first, last, grid * grid)
        gate.last_ms = times[-1]
        cell_size = sheet_cell_size(info.width, info.height, grid, max_edge)
        spacing = sheet_spacing_ms(first, last, grid)
        cells = tuple(
            SheetCell(cell=number, time_ms=ms, timecode=format_timecode(ms))
            for number, ms in enumerate(times, 1)
        )
        labels = [sheet_label(cell.cell, cell.timecode, spacing) for cell in cells]
        name = sheet_name(resolved.stem, first, last)
        inbox = self._inbox()
        failed_ms: int | None = None
        masked = False
        written: tuple[CaptureShot, ImageProbe] | None = None
        try:
            written = self._write_sheet(
                gate, deadline, port, resolved, inbox, name, times, grid, cell_size, labels
            )
        except _FrameFailed as exc:
            failed_ms = exc.ms
        except Exception:
            masked = True
        if failed_ms is not None:
            raise ValidationError(_frame_failed_text(failed_ms))
        if masked or written is None:
            raise CaptureFailedError(SHEET_NOT_WRITTEN)
        shot, probe = written
        log.info("capture.sheet", cells=len(cells), shot_id=shot.id)
        return VideoSheet(
            video=video_probe(resolved, info),
            shot=SheetShot(
                id=shot.id,
                path=str(shot.original_path),
                width=probe.width,
                height=probe.height,
            ),
            spacing_ms=spacing,
            cells=cells,
        )

    def _write_sheet(
        self,
        gate: _FramesGate,
        deadline: float,
        port: FramePort,
        resolved: Path,
        inbox: Path,
        name: str,
        times: list[int],
        grid: int,
        cell_size: tuple[int, int],
        labels: list[str],
    ) -> tuple[CaptureShot, ImageProbe]:
        """SHEET_WRITE: reserve, grab and tile, publish. Any failure leaves nothing this call made.

        The handle is closed and the temp this call made, if not moved, is unlinked; a temp
        another writer made is never touched.
        """
        handles: list[BufferedWriter] = []
        temps: list[Path] = []
        dests: list[Path] = []
        owned: list[Path] = []
        names = [name]
        try:
            self._reserve_frames(deadline, inbox, names, times[0], handles, temps, dests, owned)
            probe = self._grab_sheet(
                deadline, port, resolved, times, grid, cell_size, labels, handles[0], temps[0]
            )
            shots = self._publish_frames(
                gate,
                deadline,
                inbox,
                names,
                times[-1],
                CaptureSource.Video,
                temps,
                dests,
                owned,
                [probe],
            )
        finally:
            for handle in handles:
                with contextlib.suppress(OSError):
                    handle.close()
            for tmp in owned:
                with contextlib.suppress(OSError):
                    tmp.unlink(missing_ok=True)
        return shots[0], probe

    def _grab_sheet(
        self,
        deadline: float,
        port: FramePort,
        resolved: Path,
        times: list[int],
        grid: int,
        cell_size: tuple[int, int],
        labels: list[str],
        handle: BufferedWriter,
        tmp: Path,
    ) -> ImageProbe:
        """SHEET_WRITE (2), unlocked: grab each cell in time order, tile, write and probe."""
        cells: list[bytes] = []
        for ms in times:
            left = deadline - self._monotonic()
            if left <= 0:  # SHEET_DEADLINE (a)
                raise _FrameFailed(ms)
            data = port.grab_frame(resolved, ms, seek="input", timeout_s=left, box=cell_size)
            if deadline - self._monotonic() <= 0:  # SHEET_DEADLINE (b)
                raise _FrameFailed(ms)
            if not isinstance(data, bytes) or not data.startswith(PNG_SIGNATURE):
                raise _FrameFailed(ms)
            cells.append(data)
        image = self._annotate.sheet(cells, grid=grid, cell_size=cell_size, labels=labels)
        if deadline - self._monotonic() <= 0:  # SHEET_DEADLINE (b')
            raise _FrameFailed(times[-1])
        handle.write(image)
        handle.close()
        return self._annotate.probe(tmp)

    def _frames_body(
        self,
        gate: _FramesGate,
        deadline: float,
        path: str,
        at: Sequence[object] | None,
        count: int | None,
        start: object | None,
        end: object | None,
    ) -> VideoFrames:
        """FRAME_CHECKS, then FRAME_WRITE's three phases, on the worker thread."""
        if (at is None) == (count is None) or (
            at is not None and (start is not None or end is not None)
        ):
            raise ValidationError(FRAMES_EITHER)
        resolved = require_local_video(path)
        at_ms = None if at is None else sorted({parse_time(value) for value in at})
        start_ms = None if start is None else parse_time(start)
        end_ms = None if end is None else parse_time(end)
        if at is not None and not 1 <= len(at) <= FRAMES_MAX:
            raise ValidationError(FRAMES_AT_RANGE)
        if count is not None and (
            isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= FRAMES_MAX
        ):
            raise ValidationError(FRAMES_COUNT_RANGE)
        if at_ms:
            gate.last_ms = at_ms[-1]
        elif start_ms is not None:
            gate.last_ms = start_ms
        port = self._frames
        if port is None:
            raise CaptureFailedError(FRAMES_NOT_WRITTEN)
        info: MediaInfo | None = None
        try:
            info = port.probe(resolved, timeout_s=deadline - self._monotonic())
        except MediaProbeError:
            info = None
        if info is None:
            raise ValidationError(FRAMES_NOT_PROBED)
        if info.video_codec is None:
            raise ValidationError(FRAMES_NOT_VIDEO)
        times, seek = self._frame_plan(info, at_ms, count, start_ms, end_ms)
        gate.last_ms = times[-1]
        inbox = self._inbox()
        shots: list[CaptureShot] = []
        probes: list[ImageProbe] = []
        failed_ms: int | None = None
        masked = False
        try:
            shots, probes = self._write_frames(gate, deadline, port, resolved, inbox, times, seek)
        except _FrameFailed as exc:
            failed_ms = exc.ms
        except Exception:
            masked = True
        if failed_ms is not None:
            raise ValidationError(_frame_failed_text(failed_ms))
        if masked:
            raise CaptureFailedError(FRAMES_NOT_WRITTEN)
        log.info("capture.frames", count=len(shots), shot_ids=[shot.id for shot in shots])
        return VideoFrames(
            video=video_probe(resolved, info),
            frames=tuple(
                VideoFrame(
                    id=shot.id,
                    path=str(shot.original_path),
                    time_ms=ms,
                    timecode=format_timecode(ms),
                    width=probe.width,
                    height=probe.height,
                )
                for shot, probe, ms in zip(shots, probes, times, strict=True)
            ),
        )

    @staticmethod
    def _frame_plan(
        info: MediaInfo,
        at_ms: list[int] | None,
        count: int | None,
        start_ms: int | None,
        end_ms: int | None,
    ) -> tuple[list[int], FrameSeek]:
        """FRAME_CHECKS after the probe, and NO_DURATION (D-576 A): the times and the seek."""
        total = duration_ms(info.duration)
        if total is None:
            if at_ms is None:
                raise ValidationError(FRAMES_NO_DURATION)
            return at_ms, "output"
        if at_ms is not None:
            for ms in at_ms:
                if ms >= total:
                    raise _past_end(ms, total)
            return at_ms, "input"
        first, last = CaptureService._span_ms(total, start_ms, end_ms)
        if count is None:
            raise ValidationError(FRAMES_EITHER)
        return frame_times(first, last, count), "input"

    @staticmethod
    def _span_ms(total: int, start_ms: int | None, end_ms: int | None) -> tuple[int, int]:
        """FRAME_CHECKS and SHEET_CHECKS: the span, start 0 and end the duration by default."""
        first = 0 if start_ms is None else start_ms
        last = total if end_ms is None else end_ms
        if first >= total:
            raise _past_end(first, total)
        if last > total:
            raise _past_end(last, total)
        if first >= last:
            raise ValidationError(FRAMES_BEFORE_END)
        return first, last

    def _file_lock_by(self, deadline: float) -> threading.Lock | None:
        """FRAME_WRITE: `CAPTURE_FILE_LOCK`, waited for no longer than the time left, or None."""
        lock = CAPTURE_FILE_LOCK
        left = deadline - self._monotonic()
        if left <= 0 or not lock.acquire(timeout=left):
            return None
        return lock

    def _write_frames(
        self,
        gate: _FramesGate,
        deadline: float,
        port: FramePort,
        resolved: Path,
        inbox: Path,
        times: list[int],
        seek: FrameSeek,
    ) -> tuple[list[CaptureShot], list[ImageProbe]]:
        """FRAME_WRITE: reserve, grab, publish. Any failure leaves nothing this call made.

        Every handle is closed and every temp this call made and hasn't moved is unlinked; a
        temp another writer made is never touched.
        """
        handles: list[BufferedWriter] = []
        temps: list[Path] = []
        dests: list[Path] = []
        owned: list[Path] = []
        names = [frame_name(resolved.stem, ms) for ms in times]
        try:
            self._reserve_frames(deadline, inbox, names, times[0], handles, temps, dests, owned)
            probes = self._grab_frames(deadline, port, resolved, times, seek, handles, temps)
            shots = self._publish_frames(
                gate,
                deadline,
                inbox,
                names,
                times[-1],
                CaptureSource.Video,
                temps,
                dests,
                owned,
                probes,
            )
        finally:
            for handle in handles:
                with contextlib.suppress(OSError):
                    handle.close()
            for tmp in owned:
                with contextlib.suppress(OSError):
                    tmp.unlink(missing_ok=True)
        return shots, probes

    def _reserve_frames(
        self,
        deadline: float,
        inbox: Path,
        names: list[str],
        failed_ms: int,
        handles: list[BufferedWriter],
        temps: list[Path],
        dests: list[Path],
        owned: list[Path],
    ) -> None:
        """FRAME_WRITE and SHEET_WRITE (1): under the lock, each name's exclusive temp file.

        A lock not had in time fails at `failed_ms`, the call's first time (D-600).
        """
        lock = self._file_lock_by(deadline)
        if lock is None:
            raise _FrameFailed(failed_ms)
        try:
            with self._uow_factory() as uow:
                self._annotate.ensure_dir(inbox)
                for name in names:
                    dest = self._import_dest(uow, inbox, name, ".png")
                    tmp = dest.with_name(dest.name + TMP_SUFFIX)
                    handles.append(tmp.open("xb"))
                    owned.append(tmp)
                    temps.append(tmp)
                    dests.append(dest)
        finally:
            lock.release()

    def _grab_frames(
        self,
        deadline: float,
        port: FramePort,
        resolved: Path,
        times: list[int],
        seek: FrameSeek,
        handles: list[BufferedWriter],
        temps: list[Path],
    ) -> list[ImageProbe]:
        """FRAME_WRITE (2), unlocked: grab, check, write and probe each frame in time order."""
        probes: list[ImageProbe] = []
        for index, ms in enumerate(times):
            left = deadline - self._monotonic()
            if left <= 0:  # FRAME_DEADLINE (a)
                raise _FrameFailed(ms)
            data = port.grab_frame(resolved, ms, seek=seek, timeout_s=left)
            if deadline - self._monotonic() <= 0:  # FRAME_DEADLINE (b)
                raise _FrameFailed(ms)
            if not isinstance(data, bytes) or not data.startswith(PNG_SIGNATURE):
                raise _FrameFailed(ms)
            handle = handles[index]
            handle.write(data)
            handle.close()
            probe: ImageProbe | None = None
            try:
                probe = self._annotate.probe(temps[index])
            except InboxPathError:
                probe = None
            if probe is None:
                raise _FrameFailed(ms)
            probes.append(probe)
        return probes

    def _publish_frames(
        self,
        gate: _FramesGate,
        deadline: float,
        inbox: Path,
        names: list[str],
        failed_ms: int,
        source: CaptureSource,
        temps: list[Path],
        dests: list[Path],
        owned: list[Path],
        probes: list[ImageProbe],
    ) -> list[CaptureShot]:
        """FRAME_WRITE and SHEET_WRITE (3): under the lock and one unit of work, move, register
        and commit. A deadline check that fails reports `failed_ms`, the call's last time (D-600).

        A failure unlinks every dest this call moved before the lock is released, and the unit
        of work rolls back.
        """
        last = failed_ms
        lock = self._file_lock_by(deadline)
        if lock is None:  # FRAME_DEADLINE (c), the lock not had in time
            raise _FrameFailed(last)
        moved: list[Path] = []
        shots: list[CaptureShot] = []
        failure: BaseException | None = None
        try:
            try:
                with self._uow_factory() as uow:
                    if deadline - self._monotonic() <= 0:  # FRAME_DEADLINE (c)
                        raise _FrameFailed(last)
                    now = self._now()
                    for index, tmp in enumerate(temps):
                        dest = dests[index]
                        if _is_file(dest) or uow.capture_shots.get_by_path(dest) is not None:
                            dest = self._import_dest(uow, inbox, names[index], ".png")
                        os.replace(tmp, dest)
                        owned.remove(tmp)
                        moved.append(dest)
                        shot = self._upsert_shot(uow, dest, probes[index], now, source)
                        shots.append(shot)
                    with gate.lock:  # FRAME_DEADLINE (d)
                        expired = gate.state == "abandoned" or deadline - self._monotonic() <= 0
                        if not expired:
                            gate.state = "committing"
                    if expired:
                        raise _FrameFailed(last)
            except BaseException as exc:
                failure = exc
                for dest in moved:
                    with contextlib.suppress(OSError):
                        dest.unlink(missing_ok=True)
        finally:
            lock.release()
        if failure is not None:
            raise failure
        return shots

    def _import_copy(
        self, source: Path, inbox: Path, data: bytes, orientation: int
    ) -> CaptureShot:
        """IMPORT_COPY: write a temporary file, move it into place, probe and register it.

        Any failure from the first write through the commit removes what this call wrote and
        raises the fixed 503, so no message that names a path reaches the response. The
        temporary file is created exclusively, so a file another writer left under that name is
        never written over or removed.
        """
        suffix = source.suffix.lower() if orientation == 1 else ".png"
        tmp: Path | None = None
        dest: Path | None = None
        moved = False
        with CAPTURE_FILE_LOCK:
            try:
                with self._uow_factory() as uow:
                    self._annotate.ensure_dir(inbox)
                    dest = self._import_dest(uow, inbox, import_stem(source.stem), suffix)
                    with dest.with_name(dest.name + TMP_SUFFIX).open("xb") as handle:
                        tmp = Path(handle.name)
                        if orientation == 1:
                            handle.write(data)
                    if orientation != 1:
                        self._annotate.write_upright_png(data, tmp)
                    os.replace(tmp, dest)
                    moved = True
                    probe = self._annotate.probe(dest)
                    shot = self._upsert_shot(uow, dest, probe, self._now(), CaptureSource.Import)
            except Exception as exc:
                self._unlink_if_file(tmp)
                if moved:
                    self._unlink_if_file(dest)
                raise CaptureFailedError("the import could not be written") from exc
        return shot

    @staticmethod
    def _import_dest(uow: UnitOfWork, inbox: Path, stem: str, suffix: str) -> Path:
        """IMPORT_NAME: `stem`, then `_2`, `_3` … until no inbox-root file or row holds it.

        A name whose temporary file is in the inbox root is taken too, so the copy never writes
        over another writer's `NAME.avkit-tmp`.
        """
        taken: set[str] = set()
        for child in inbox.iterdir():
            name = child.name.casefold()
            taken.add(name)
            if name.endswith(TMP_SUFFIX):
                taken.add(name.removesuffix(TMP_SUFFIX))
        taken |= {
            shot.original_path.name.casefold()
            for shot in uow.capture_shots.list()
            if shot.original_path.parent == inbox
        }
        name = f"{stem}{suffix}"
        index = 2
        while name.casefold() in taken:
            name = f"{stem}_{index}{suffix}"
            index += 1
        return inbox / name

    def capture_fullscreen(self) -> CaptureShot:
        """Grab the virtual desktop into the inbox and register it."""
        dest = self._unique_png(self._inbox())
        self._capture.capture_fullscreen(dest)
        return self.register_shot(dest, CaptureSource.McpFullscreen)

    def capture_region(self, bbox: BBox) -> CaptureShot:
        """Grab a rectangle into the inbox and register it."""
        dest = self._unique_png(self._inbox())
        self._capture.capture_region(dest, bbox)
        return self.register_shot(dest, CaptureSource.McpRegion)

    def request_interactive(self) -> CaptureRequest:
        """Insert a Pending overlay wait, or conflict if one already exists."""
        self.expire_stale_requests()
        now = self._now()
        with self._uow_factory() as uow:
            if uow.capture_requests.get_pending_request() is not None:
                raise CaptureRequestConflictError("a pending capture request already exists")
            request = CaptureRequest(
                id=str(uuid4()),
                status=CaptureRequestStatus.Pending,
                shot_id=None,
                created_at=now,
                expires_at=now + timedelta(seconds=REQUEST_TTL_S),
            )
            uow.capture_requests.add(request)
            return request

    def complete_request(self, request_id: str, path: Path) -> CaptureRequest:
        """Register the overlay path and mark the request Completed in one UoW."""
        self.expire_stale_requests()
        inbox = self._inbox()
        resolved = self._require_inbox_file(path, inbox)
        probe = self._annotate.probe(resolved)
        now = self._now()
        with self._uow_factory() as uow:
            request = uow.capture_requests.get(request_id)
            if request is None:
                raise NotFoundError(f"capture request {request_id} not found")
            allowed = CAPTURE_REQUEST_TRANSITIONS[request.status]
            if CaptureRequestStatus.Completed not in allowed:
                raise ConflictError(
                    f"cannot transition capture request from {request.status.name}"
                )
            shot = self._upsert_shot(
                uow, resolved, probe, now, CaptureSource.McpInteractive
            )
            updated = replace(
                request, status=CaptureRequestStatus.Completed, shot_id=shot.id
            )
            uow.capture_requests.save(updated)
            return updated

    def cancel_request(self, request_id: str) -> CaptureRequest:
        """Mark the request Cancelled without a shot."""
        self.expire_stale_requests()
        return self._transition_request(
            request_id,
            CaptureRequestStatus.Cancelled,
            shot_id=None,
        )

    def expire_stale_requests(self) -> None:
        """Pending rows whose ttl has elapsed become Expired."""
        now = self._now()
        with self._uow_factory() as uow:
            pending = uow.capture_requests.get_pending_request()
            if pending is None:
                return
            if self._as_utc(pending.expires_at) <= self._as_utc(now):
                uow.capture_requests.save(
                    replace(pending, status=CaptureRequestStatus.Expired)
                )

    def list_requests(
        self, status: CaptureRequestStatus | None = None
    ) -> list[CaptureRequest]:
        """Expire stale rows, then return requests optionally filtered by status."""
        self.expire_stale_requests()
        with self._uow_factory() as uow:
            rows = list(uow.capture_requests.list())
        if status is not None:
            rows = [item for item in rows if item.status is status]
        return rows

    def annotate_and_save(
        self,
        shot_id: str,
        annotations: Sequence[Annotation],
    ) -> CaptureShot:
        """Bake annotations in the configured format and write the sidecar.

        Empty annotations clear both.
        """
        output_format = self._annotated_format()
        with CAPTURE_FILE_LOCK, self._uow_factory() as uow:
            shot = uow.capture_shots.get(shot_id)
            if shot is None:
                raise NotFoundError(f"capture shot {shot_id} not found")
            now = self._now()
            annotated_path = annotated_path_for(shot.original_path, output_format)
            sidecar_path = _sidecar_for(shot.original_path)
            siblings = _annotated_siblings(shot.original_path)
            if len(annotations) == 0:
                for sibling in siblings:
                    self._unlink_if_file(sibling)
                self._unlink_if_file(sidecar_path)
                updated = replace(
                    shot,
                    annotated_path=None,
                    sidecar_path=None,
                    updated_at=now,
                )
                uow.capture_shots.save(updated)
                return updated
            clamped = [
                self._clamp_annotation(item, shot.width, shot.height) for item in annotations
            ]
            self._annotate.bake(shot.original_path, clamped, annotated_path, output_format)
            for sibling in siblings:
                if sibling != annotated_path:
                    self._unlink_if_file(sibling)
            sidecar_path.write_text(
                json.dumps(
                    {
                        "version": SIDECAR_VERSION,
                        "annotations": [_annotation_to_wire(item) for item in clamped],
                    }
                ),
                encoding="utf-8",
            )
            updated = replace(
                shot,
                annotated_path=annotated_path,
                sidecar_path=sidecar_path,
                updated_at=now,
            )
            uow.capture_shots.save(updated)
            return updated

    def read_image(self, shot_id: str, variant: str) -> bytes:
        """Return original or annotated file bytes."""
        return self._variant_path(self.get_shot(shot_id), variant).read_bytes()

    def read_image_view(
        self,
        shot_id: str,
        variant: str,
        *,
        x: float | None = None,
        y: float | None = None,
        width: float | None = None,
        height: float | None = None,
        unit: RegionUnit | None = None,
        max_edge: int | None = None,
    ) -> tuple[bytes, ViewFrame]:
        """Return a region view of the variant and its frame (MEU-128, D-411). Writes no file.

        The annotated copy is baked at the original's size, so one frame serves both variants.
        """
        shot = self.get_shot(shot_id)
        path = self._variant_path(shot, variant)
        frame = view_frame(
            shot.width,
            shot.height,
            x=x,
            y=y,
            width=width,
            height=height,
            unit=unit,
            max_edge=max_edge,
        )
        return self._annotate.view(path, frame), frame

    @staticmethod
    def _variant_path(shot: CaptureShot, variant: str) -> Path:
        if variant == "original":
            if not _is_file(shot.original_path):
                raise NotFoundError("original image is missing")
            return shot.original_path
        if variant == "annotated":
            if shot.annotated_path is None or not _is_file(shot.annotated_path):
                raise NotFoundError("annotated image is missing")
            return shot.annotated_path
        raise ValidationError("variant must be original or annotated")

    def remove(self, shot_id: str) -> None:
        """Delete original, sidecar, and annotated files, then the row."""
        with CAPTURE_FILE_LOCK, self._uow_factory() as uow:
            shot = uow.capture_shots.get(shot_id)
            if shot is None:
                raise NotFoundError(f"capture shot {shot_id} not found")
            self._unlink_if_file(shot.original_path)
            self._unlink_if_file(shot.annotated_path)
            for sibling in _annotated_siblings(shot.original_path):
                self._unlink_if_file(sibling)
            self._unlink_if_file(shot.sidecar_path)
            uow.capture_shots.delete(shot_id)

    def latest_backup(self, shot_id: str) -> Path | None:
        """LATEST_BACKUP for a shot, or None (non-PNG shot, no backup, or an invalid backup dir)."""
        return self._latest_backup_for(self.get_shot(shot_id))

    def flatten(self, shot_id: str) -> CaptureShot:
        """Bake saved marks into the original after a backup.

        JPEG/WebP shots get a new PNG copy instead.
        """
        with CAPTURE_FILE_LOCK:
            shot = self.get_shot(shot_id)
            marks = self.load_shot_annotations(shot_id)
            if not marks:
                raise CaptureFlattenConflictError("this capture has no saved marks to apply")
            suffix = shot.original_path.suffix.lower()
            if suffix != FLATTEN_PNG_SUFFIX and suffix not in CONVERTIBLE_SUFFIXES:
                raise CaptureFlattenConflictError(
                    f"{suffix or 'extensionless'} files cannot be flattened"
                )
            backup_dir = self._backup_dir_if_enabled()
            if suffix == FLATTEN_PNG_SUFFIX:
                return self._flatten_png_locked(shot, marks, backup_dir)
            return self._convert_and_flatten_locked(shot, marks, backup_dir)

    def revert(self, shot_id: str) -> CaptureShot:
        """Restore the newest backup over the original (the backup is kept); re-bake saved marks."""
        with CAPTURE_FILE_LOCK:
            shot = self.get_shot(shot_id)
            marks = self.load_shot_annotations(shot_id)
            source = self._latest_backup_for(shot)
            if source is None:
                raise NotFoundError("no backup for this capture")
            original = shot.original_path
            tmp = original.with_name(original.name + TMP_SUFFIX)
            try:
                shutil.copyfile(source, tmp)
                os.replace(tmp, original)
            except OSError as exc:
                self._unlink_if_file(tmp)
                log.warning("capture.revert_failed", shot_id=shot.id, error=str(exc))
                raise CaptureFlattenConflictError(f"could not restore the backup: {exc}") from exc
            probe = self._annotate.probe(original)
            annotated_path, sidecar_path = self._rebake_annotated(original, marks)
            now = self._now()
            with self._uow_factory() as uow:
                current = uow.capture_shots.get(shot.id) or shot
                updated = replace(
                    current,
                    width=probe.width,
                    height=probe.height,
                    file_size=probe.file_size,
                    annotated_path=annotated_path,
                    sidecar_path=sidecar_path,
                    updated_at=now,
                )
                uow.capture_shots.save(updated)
            log.info("capture.reverted", shot_id=shot.id, backup=str(source))
            return updated

    def crop_shot(
        self,
        shot_id: str,
        *,
        x: float,
        y: float,
        width: float,
        height: float,
        unit: RegionUnit | None = None,
        name: str | None = None,
    ) -> CropResult:
        """CROP_READ to CROP_CLEANUP: cut a region of a shot into a new PNG shot (MEU-130).

        The source's file, sidecar and row are only read. Saved marks travel through
        `clip_mark` (MARK_CARRY) and are baked onto the crop (CROP_BAKE). A refusal names no
        path; any other failure removes only what this call wrote and raises the fixed 503
        (D-476, D-490).
        """
        chosen = None if name is None else crop_name_stem(name)
        output_format = self._annotated_format()
        inbox = self._inbox()
        tmp: Path | None = None
        crop: Path | None = None
        cut = False
        moved = False
        with CAPTURE_FILE_LOCK:
            try:
                with self._uow_factory() as uow:
                    shot = uow.capture_shots.get(shot_id)
                    if shot is None:
                        raise NotFoundError(f"capture shot {shot_id} not found")
                    marks = self._saved_marks(shot.original_path)
                    if not all(math.isfinite(value) for value in (x, y, width, height)):
                        raise ValidationError("x, y, width and height must be finite numbers")
                    left, top, crop_width, crop_height, clamped = resolve_region(
                        shot.width, shot.height, x, y, width, height, unit or "px"
                    )
                    carried: list[Annotation] = []
                    counts = {"kept": 0, "clipped": 0, "dropped": 0}
                    for mark in marks:
                        clipped_mark, carry = clip_mark(mark, left, top, crop_width, crop_height)
                        counts[carry] += 1
                        if clipped_mark is not None:
                            carried.append(clipped_mark)
                    self._annotate.ensure_dir(inbox)
                    stem = chosen if chosen is not None else crop_default_stem(
                        shot.original_path.stem
                    )
                    crop = self._crop_dest(uow, inbox, stem)
                    with crop.with_name(crop.name + TMP_SUFFIX).open("xb") as handle:
                        tmp = Path(handle.name)
                    self._annotate.crop(
                        shot.original_path,
                        (left, top, crop_width, crop_height),
                        (shot.width, shot.height),
                        tmp,
                    )
                    cut = True
                    os.replace(tmp, crop)
                    moved = True
                    # The name is no longer this call's once it is moved; never remove it later.
                    tmp = None
                    probe = self._annotate.probe(crop)
                    now = self._now()
                    new = self._upsert_shot(uow, crop, probe, now, CaptureSource.Crop)
                    if carried:
                        sidecar = _sidecar_for(crop)
                        sidecar.write_text(
                            json.dumps(
                                {
                                    "version": SIDECAR_VERSION,
                                    "annotations": annotations_to_wire(carried),
                                }
                            ),
                            encoding="utf-8",
                        )
                        annotated = annotated_path_for(crop, output_format)
                        self._annotate.bake(crop, carried, annotated, output_format)
                        new = replace(
                            new, annotated_path=annotated, sidecar_path=sidecar, updated_at=now
                        )
                        uow.capture_shots.save(new)
            except Exception as exc:
                self._discard(tmp)
                if moved and crop is not None:
                    # CROP_NAME found each of these free under this hold, so each is the crop's.
                    for path in (crop, _sidecar_for(crop), *_annotated_siblings(crop)):
                        self._discard(path)
                if not cut and isinstance(exc, CROP_REFUSALS):
                    raise
                raise CaptureFailedError("the crop could not be written") from exc
        return CropResult(
            shot=new,
            source_id=shot.id,
            requested=(x, y, width, height, unit or "px"),
            applied=(left, top, crop_width, crop_height),
            clamped=clamped,
            kept=counts["kept"],
            clipped=counts["clipped"],
            dropped=counts["dropped"],
        )

    def export_shot(
        self,
        shot_id: str,
        *,
        fmt: str,
        max_edge: int | None = None,
        quality: int | None = None,
    ) -> ExportResult:
        """EXPORT_CHECKS to EXPORT_WRITE (MEU-136): write a resized or re-encoded copy.

        The copy is a new shot in the inbox; the source's file, sidecar, bake and row are
        only read. Every refusal is a fixed text, and any other failure removes only what
        this call wrote and raises the fixed 503 (D-609, D-610, D-611).
        """
        if fmt not in EXPORT_FORMATS:
            raise ValidationError("format must be png, jpeg or webp")
        if max_edge is not None and (
            not isinstance(max_edge, int)
            or isinstance(max_edge, bool)
            or not REGION_MAX_EDGE_MIN <= max_edge <= EXPORT_MAX_EDGE_MAX
        ):
            raise ValidationError(
                f"max_edge must be between {REGION_MAX_EDGE_MIN} and {EXPORT_MAX_EDGE_MAX}"
            )
        if quality is not None and (
            not isinstance(quality, int) or isinstance(quality, bool) or not 1 <= quality <= 100
        ):
            raise ValidationError("quality must be between 1 and 100")
        if quality is not None and fmt == "png":
            raise ValidationError(EXPORT_QUALITY_PNG)
        tmp: Path | None = None
        dest: Path | None = None
        encoded = False
        moved = False
        with CAPTURE_FILE_LOCK:
            try:
                with self._uow_factory() as uow:
                    shot = uow.capture_shots.get(shot_id)
                    if shot is None:
                        raise NotFoundError(f"capture shot {shot_id} not found")
                    marks = self._saved_marks(shot.original_path)
                    source = self._variant_path(shot, "annotated" if marks else "original")
                    size = export_size(shot.width, shot.height, max_edge)
                    limit = EXPORT_EDGE_LIMIT.get(fmt)
                    if limit is not None and max(size) > limit:
                        raise ValidationError(EXPORT_TOO_LARGE)
                    inbox = self._inbox()
                    self._annotate.ensure_dir(inbox)
                    dest = self._crop_dest(
                        uow, inbox, export_stem(shot.original_path.stem), ext=EXPORT_SUFFIXES[fmt]
                    )
                    with dest.with_name(dest.name + TMP_SUFFIX).open("xb") as handle:
                        tmp = Path(handle.name)
                    self._annotate.export(
                        source,
                        (shot.width, shot.height),
                        tmp,
                        fmt=fmt,
                        size=size,
                        quality=quality,
                    )
                    encoded = True
                    os.replace(tmp, dest)
                    moved = True
                    # The name is no longer this call's once it is moved; never remove it later.
                    tmp = None
                    probe = self._annotate.probe(dest)
                    size_bytes = dest.stat().st_size
                    now = self._now()
                    new = self._upsert_shot(uow, dest, probe, now, CaptureSource.Export)
            except Exception as exc:
                self._discard(tmp)
                if moved and dest is not None:
                    # EXPORT_NAME found this name free under this hold, so it is the export's.
                    self._discard(dest)
                if not encoded and isinstance(exc, EXPORT_REFUSALS):
                    raise
                raise CaptureFailedError(EXPORT_NOT_WRITTEN) from exc
        log.info("capture.export", shot_id=new.id, source_id=shot.id)
        return ExportResult(shot=new, source_id=shot.id, bytes=size_bytes)

    @staticmethod
    def _saved_marks(original: Path) -> list[Annotation]:
        """CROP_READ: the source's saved marks. A missing sidecar is []; a malformed one is 422."""
        sidecar = _sidecar_for(original)
        if not _is_file(sidecar):
            return []
        try:
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AnnotationValidationError("sidecar is malformed") from exc
        return annotations_from_sidecar(payload)

    @staticmethod
    def _crop_dest(
        uow: UnitOfWork, inbox: Path, stem: str, *, ext: str = FLATTEN_PNG_SUFFIX
    ) -> Path:
        """CROP_NAME: `{stem}{ext}`, then `{stem}_2{ext}` … until the stem is free.

        `ext` is `.png` for a crop; an export passes its format's suffix (MEU-136, D-615).

        A stem is taken when an inbox-root entry case-folds to it plus any suffix in
        CROP_TAKEN_SUFFIXES, or a row in the inbox root holds its PNG name. A name whose
        temporary file is in the inbox root is taken too, so the crop never writes over
        another writer's `NAME.avkit-tmp`.
        """
        taken: set[str] = set()
        for child in inbox.iterdir():
            entry = child.name.casefold()
            taken.add(entry)
            if entry.endswith(TMP_SUFFIX):
                taken.add(entry.removesuffix(TMP_SUFFIX))
        taken |= {
            shot.original_path.name.casefold()
            for shot in uow.capture_shots.list()
            if shot.original_path.parent == inbox
        }
        candidate = stem
        index = 2
        while any(f"{candidate}{suffix}".casefold() in taken for suffix in CROP_TAKEN_SUFFIXES):
            candidate = f"{stem}_{index}"
            index += 1
        return inbox / f"{candidate}{ext}"

    def _discard(self, path: Path | None) -> None:
        """Remove a file this call wrote; a failed removal can't replace the fixed 503."""
        try:
            self._unlink_if_file(path)
        except OSError:
            pass

    def _flatten_png_locked(
        self,
        shot: CaptureShot,
        marks: Sequence[Annotation],
        backup_dir: Path | None,
    ) -> CaptureShot:
        """FLATTEN_SEQUENCE steps 3-8; the caller holds CAPTURE_FILE_LOCK."""
        original = shot.original_path
        tmp = original.with_name(original.name + TMP_SUFFIX)
        backup: Path | None = None
        step = 3
        try:
            if backup_dir is not None:
                self._annotate.ensure_dir(backup_dir)
                backup = backup_path_for(backup_dir, original.stem, self._now())
                shutil.copyfile(original, backup)
            step = 4
            self._annotate.bake(original, marks, tmp, "png")
            step = 5
            os.replace(tmp, original)
        except Exception as exc:
            # FLATTEN_ROLLBACK: nothing written by this call survives; the original is untouched.
            self._unlink_if_file(tmp)
            self._unlink_if_file(backup)
            log.warning("capture.flatten_failed", shot_id=shot.id, step=step, error=str(exc))
            if isinstance(exc, OSError):
                raise CaptureFlattenConflictError(f"flatten failed at step {step}: {exc}") from exc
            raise
        for sibling in _annotated_siblings(original):
            self._unlink_if_file(sibling)
        self._unlink_if_file(_sidecar_for(original))
        probe = self._annotate.probe(original)
        now = self._now()
        with self._uow_factory() as uow:
            current = uow.capture_shots.get(shot.id) or shot
            updated = replace(
                current,
                annotated_path=None,
                sidecar_path=None,
                width=probe.width,
                height=probe.height,
                file_size=probe.file_size,
                updated_at=now,
            )
            uow.capture_shots.save(updated)
        log.info("capture.flattened", shot_id=shot.id, backup=str(backup) if backup else "none")
        return updated

    def _convert_and_flatten_locked(
        self,
        shot: CaptureShot,
        marks: Sequence[Annotation],
        backup_dir: Path | None,
    ) -> CaptureShot:
        """CONVERT_ON_APPLY: a new PNG copy carries the marks and is flattened; source untouched."""
        source = shot.original_path
        target = self._convert_target(source)
        target_tmp = target.with_name(target.name + TMP_SUFFIX)
        sidecar = _sidecar_for(target)
        new_id: str | None = None
        # Backups of the target stem that predate this call; any other one it leaves is an orphan.
        prior_backups = self._target_backups(backup_dir, target)
        try:
            self._annotate.bake(source, [], target_tmp, "png")
            os.replace(target_tmp, target)
            probe = self._annotate.probe(target)
            with self._uow_factory() as uow:
                new_shot = self._upsert_shot(uow, target, probe, self._now(), shot.source)
            new_id = new_shot.id
            sidecar.write_text(
                json.dumps({"version": SIDECAR_VERSION, "annotations": annotations_to_wire(marks)}),
                encoding="utf-8",
            )
            result = self._flatten_png_locked(new_shot, marks, backup_dir)
        except Exception as exc:
            self._unlink_if_file(target_tmp)
            self._unlink_if_file(target)
            self._unlink_if_file(sidecar)
            for orphan in self._target_backups(backup_dir, target) - prior_backups:
                self._unlink_if_file(orphan)
            if new_id is not None:
                with self._uow_factory() as uow:
                    uow.capture_shots.delete(new_id)
            log.warning(
                "capture.convert_failed", shot_id=shot.id, target=str(target), error=str(exc)
            )
            if isinstance(exc, OSError):
                raise CaptureFlattenConflictError(f"could not convert to PNG: {exc}") from exc
            raise
        log.info(
            "capture.converted",
            shot_id=shot.id,
            from_path=str(source),
            to_path=str(target),
            new_id=result.id,
        )
        return result

    @staticmethod
    def _target_backups(backup_dir: Path | None, target: Path) -> set[Path]:
        """Backups in `backup_dir` that belong to `target`'s stem (BACKUP_NAME)."""
        if backup_dir is None or not backup_dir.is_dir():
            return set()
        pattern = _backup_pattern(target.stem)
        return {p for p in backup_dir.iterdir() if p.is_file() and pattern.fullmatch(p.name)}

    def _convert_target(self, source: Path) -> Path:
        """CONVERT_NAME: `{stem}-converted.png`, then `_2`, `_3` … when the file or a row exists."""
        stem = f"{source.stem}{CONVERT_STEM_TAG}"
        candidate = source.with_name(f"{stem}.png")
        index = 2
        with self._uow_factory() as uow:
            while candidate.exists() or uow.capture_shots.get_by_path(candidate) is not None:
                candidate = source.with_name(f"{stem}_{index}.png")
                index += 1
        return candidate

    def _rebake_annotated(
        self,
        original: Path,
        marks: Sequence[Annotation],
    ) -> tuple[Path | None, Path | None]:
        """ANNOTATED_CONSISTENCY after a revert; never calls the locked annotate_and_save."""
        siblings = _annotated_siblings(original)
        if not marks:
            for sibling in siblings:
                self._unlink_if_file(sibling)
            # The row reports no sidecar, so a stale (empty-list) one must not stay on disk.
            self._unlink_if_file(_sidecar_for(original))
            return None, None
        output_format = self._annotated_format()
        target = annotated_path_for(original, output_format)
        self._annotate.bake(original, marks, target, output_format)
        for sibling in siblings:
            if sibling != target:
                self._unlink_if_file(sibling)
        return target, _sidecar_for(original)

    def _latest_backup_for(self, shot: CaptureShot) -> Path | None:
        # Backups are only ever made for PNG originals, so another format never offers one.
        if shot.original_path.suffix.lower() != FLATTEN_PNG_SUFFIX:
            return None
        try:
            backup_dir = resolve_backup_dir(self._backup_dir_raw(), self._inbox())
        except CaptureFlattenConflictError:
            return None
        return latest_backup_in(backup_dir, shot.original_path.stem)

    def _backup_dir_if_enabled(self) -> Path | None:
        enabled = self._settings.get("capture", "flatten_backup")
        if not isinstance(enabled, bool):
            raise ValidationError("capture.flatten_backup must be a boolean")
        if not enabled:
            return None
        return resolve_backup_dir(self._backup_dir_raw(), self._inbox())

    def _backup_dir_raw(self) -> str:
        raw = self._settings.get("capture", "backup_dir")
        if not isinstance(raw, str):
            raise ValidationError("capture.backup_dir must be a string")
        return raw

    def _annotated_format(self) -> AnnotatedFormat:
        raw = self._settings.get("capture", "annotated_format")
        for candidate in ANNOTATED_FORMATS:
            if raw == candidate:
                return candidate
        allowed = ", ".join(ANNOTATED_FORMATS)
        raise ValidationError(f"capture.annotated_format must be one of {allowed}")

    def _now(self) -> datetime:
        return self._as_utc(self._clock())

    @staticmethod
    def _as_utc(stamp: datetime) -> datetime:
        if stamp.tzinfo is None:
            return stamp.replace(tzinfo=UTC)
        return stamp.astimezone(UTC)

    def _inbox(self) -> Path:
        raw = self._settings.get("capture", "inbox_dir")
        if not isinstance(raw, str) or raw.strip() == "":
            raise ValidationError("capture.inbox_dir must be a non-empty string")
        path = Path(raw).expanduser().resolve()
        return path

    def _require_inbox_file(self, path: Path, inbox: Path) -> Path:
        if not isinstance(path, Path):
            raise InboxPathError("path must be a Path")
        if not path.is_absolute():
            raise InboxPathError("path must be an absolute Path")
        try:
            resolved = path.resolve()
            resolved.relative_to(inbox)
        except (ValueError, OSError) as exc:
            raise InboxPathError("path is outside the capture inbox") from exc
        if not resolved.is_file():
            raise InboxPathError(f"{resolved} is not a file")
        return resolved

    def _unique_png(self, inbox: Path) -> Path:
        stem = self._now().strftime(TIMESTAMP_FORMAT)
        candidate = inbox / f"{stem}.png"
        if not candidate.exists():
            return candidate
        index = 2
        while True:
            candidate = inbox / f"{stem}_{index}.png"
            if not candidate.exists():
                return candidate
            index += 1

    def _upsert_shot(
        self,
        uow: UnitOfWork,
        resolved: Path,
        probe: ImageProbe,
        now: datetime,
        source: CaptureSource,
    ) -> CaptureShot:
        existing = uow.capture_shots.get_by_path(resolved)
        if existing is not None:
            # The registering source wins over whatever the row already carries. The
            # region picker writes its PNG into the inbox and registers it a moment
            # later, so the inbox scanner can reach the file first and insert the row
            # as CaptureSource.Scan; returning that row unchanged would leave every
            # captured shot indistinguishable from a file the user dropped in by hand.
            if existing.file_size == probe.file_size and existing.source == source:
                return existing
            updated = replace(
                existing,
                width=probe.width,
                height=probe.height,
                file_size=probe.file_size,
                source=source,
                updated_at=now,
            )
            uow.capture_shots.save(updated)
            return updated
        shot = CaptureShot(
            id=str(uuid4()),
            original_path=resolved,
            annotated_path=None,
            sidecar_path=None,
            display_name=resolved.name,
            width=probe.width,
            height=probe.height,
            file_size=probe.file_size,
            source=source,
            created_at=now,
            updated_at=now,
        )
        uow.capture_shots.add(shot)
        log.info("capture.registered", shot_id=shot.id, source=source.name)
        return shot

    def _transition_request(
        self,
        request_id: str,
        next_status: CaptureRequestStatus,
        *,
        shot_id: str | None,
    ) -> CaptureRequest:
        with self._uow_factory() as uow:
            request = uow.capture_requests.get(request_id)
            if request is None:
                raise NotFoundError(f"capture request {request_id} not found")
            allowed = CAPTURE_REQUEST_TRANSITIONS[request.status]
            if next_status not in allowed:
                raise ConflictError(
                    f"cannot transition capture request from {request.status.name}"
                )
            updated = replace(request, status=next_status, shot_id=shot_id)
            uow.capture_requests.save(updated)
            return updated

    def _clamp_annotation(
        self,
        annotation: Annotation,
        width: int,
        height: int,
    ) -> Annotation:
        lo = ANNOTATION_CLAMP_MIN
        if isinstance(annotation, ArrowAnnotation):
            return replace(
                annotation,
                from_xy=(
                    _clamp_int(annotation.from_xy[0], lo, width),
                    _clamp_int(annotation.from_xy[1], lo, height),
                ),
                to_xy=(
                    _clamp_int(annotation.to_xy[0], lo, width),
                    _clamp_int(annotation.to_xy[1], lo, height),
                ),
            )
        if isinstance(
            annotation,
            (
                RectAnnotation,
                HighlightAnnotation,
                PixelateAnnotation,
                EraserAnnotation,
                RedactAnnotation,
            ),
        ):
            return replace(
                annotation,
                x=_clamp_int(annotation.x, lo, width),
                y=_clamp_int(annotation.y, lo, height),
            )
        if isinstance(annotation, TextAnnotation):
            return replace(
                annotation,
                x=_clamp_int(annotation.x, lo, width),
                y=_clamp_int(annotation.y, lo, height),
            )
        raise AnnotationValidationError(
            f"unsupported annotation type: {type(annotation)!r}"
        )

    def _unlink_if_file(self, path: Path | None) -> None:
        if path is None:
            return
        if path.is_file():
            path.unlink()
