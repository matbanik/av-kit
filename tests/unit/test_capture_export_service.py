"""MEU-136 `CaptureService.export_shot` (Session 64): EXPORT_SIZE to NO_RAW_OUTPUT.

AC-136.2, AC-136.3 and AC-136.8 to AC-136.12. Rows live in a real SQLite file, so a failed
call's rollback is the real unit of work's. A recording fake `ImageAnnotatePort` records each
`export` call and writes a real image, except in AC-136.10, which runs the real adapter. Every
call is made through `_call`, which hands an exception back as the value, so a Red fails by an
assertion on what came back.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from structlog.testing import capture_logs

from avkit_core.domain.capture import ImageProbe, RectAnnotation
from avkit_core.domain.enums import CaptureSource
from avkit_core.domain.errors import (
    AnnotationValidationError,
    CaptureFailedError,
    ConflictError,
    InboxPathError,
    NotFoundError,
    ValidationError,
)
from avkit_core.services import capture as capture_mod
from avkit_core.services.capture import CaptureService
from avkit_core.services.settings import SettingsService
from avkit_infra.capture.adapter import CaptureAdapter
from avkit_infra.database.engine import (
    create_session_factory,
    create_sqlite_engine,
    init_schema,
)
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

TMP = ".avkit-tmp"
FORMAT = "format must be png, jpeg or webp"
MAX_EDGE = "max_edge must be between 64 and 16383"
QUALITY = "quality must be between 1 and 100"
QUALITY_PNG = "quality applies to jpeg and webp only"
TOO_LARGE = "the export is too large for this format; lower max_edge"
NOT_WRITTEN = "the export could not be written"
NO_BAKE = "annotated image is missing"
NO_ORIGINAL = "original image is missing"
MALFORMED = "sidecar is malformed"
NOT_OPENED = "the image could not be opened"
CHANGED = "the image file changed since the captures were listed; list them again and retry"
PIL_FORMAT = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}
SUFFIX = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}
NOW = datetime(2026, 11, 11, 12, 0, tzinfo=UTC)
SOURCE_SIZE = (300, 200)


def _ac(label: str) -> pytest.MarkDecorator:
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _png(size: tuple[int, int], colour: tuple[int, int, int] = (40, 90, 160)) -> bytes:
    import io

    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True)
class ExportCall:
    source: Path
    source_size: tuple[int, int]
    out: Path
    fmt: str
    size: tuple[int, int]
    quality: int | None


@dataclass
class FakeAnnotate:
    """A recording `ImageAnnotatePort`: probes with Pillow and writes real images."""

    exports: list[ExportCall] = field(default_factory=list)
    export_error: Exception | None = None
    on_probe: Callable[[Path], None] | None = None

    def probe(self, path: Path) -> ImageProbe:
        if self.on_probe is not None:
            self.on_probe(path)
        if not path.is_file():
            raise InboxPathError(f"{path} is not a file")
        with Image.open(path) as opened:
            width, height = opened.size
        return ImageProbe(width=width, height=height, file_size=path.stat().st_size)

    def ensure_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def bake(
        self,
        original_path: Path,
        annotations: object,
        output_path: Path,
        output_format: str = "png",
    ) -> ImageProbe:
        with Image.open(original_path) as opened:
            size = opened.size
        output_path.write_bytes(_png(size, (200, 40, 40)))
        return self.probe(output_path)

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
        self.exports.append(ExportCall(source, source_size, out, fmt, size, quality))
        if self.export_error is not None:
            raise self.export_error
        Image.new("RGB", size, (10, 120, 30)).save(out, format=PIL_FORMAT[fmt])
        return self.probe(out)


class Factory:
    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    def __call__(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_factory)


@dataclass
class Stack:
    service: CaptureService
    factory: Factory
    annotate: Any
    inbox: Path

    def rows(self) -> list[Any]:
        with self.factory() as uow:
            return sorted(uow.capture_shots.list(), key=lambda row: row.id)

    def names(self) -> list[str]:
        return sorted(child.name for child in self.inbox.iterdir())

    def shot(self, name: str = "x.png", size: tuple[int, int] = SOURCE_SIZE) -> Any:
        path = (self.inbox / name).resolve()
        path.write_bytes(_png(size))
        return self.service.register_shot(path, CaptureSource.Gui)

    def marked(self, name: str = "x.png") -> Any:
        shot = self.shot(name)
        rect = RectAnnotation(x=10, y=10, width=40, height=30, color="red", stroke_width=2)
        self.service.annotate_and_save(shot.id, [rect])
        return self.row(shot.id)

    def row(self, shot_id: str) -> Any:
        with self.factory() as uow:
            return uow.capture_shots.get(shot_id)


@pytest.fixture
def make_stack(tmp_path: Path) -> Iterator[Callable[..., Stack]]:
    engines: list[Any] = []

    def build(name: str = "a", *, real: bool = False) -> Stack:
        root = tmp_path / name
        root.mkdir(parents=True, exist_ok=True)
        engine = create_sqlite_engine(root / "avkit.db")
        init_schema(engine)
        engines.append(engine)
        factory = Factory(create_session_factory(engine))
        inbox = root / "inbox"
        inbox.mkdir()
        settings = SettingsService(factory)
        settings.set("capture", "inbox_dir", str(inbox))
        annotate: Any = CaptureAdapter() if real else FakeAnnotate()
        service = CaptureService(
            factory,
            capture=annotate,
            annotate=annotate,
            settings=settings,
            clock=lambda: NOW,
        )
        return Stack(service, factory, annotate, inbox.resolve())

    yield build
    for engine in engines:
        engine.dispose()


def _call(stack: Stack, shot_id: str, **kwargs: Any) -> Any:
    """`export_shot`; an exception comes back as the value."""
    try:
        return stack.service.export_shot(shot_id, **kwargs)
    except Exception as exc:  # noqa: BLE001 - a Red must fail by assertion, not by the raise
        return exc


def _raised(result: object) -> tuple[type, str]:
    return (type(result), str(result))


def _done(result: object) -> Any:
    from avkit_core.services.capture import ExportResult

    assert isinstance(result, ExportResult), f"export raised {type(result).__name__}: {result}"
    return result


# --- AC-136.2: EXPORT_SIZE ---------------------------------------------------------------------

NAMED_SIZES = (
    ((128, 3, 64), (64, 2)),
    ((128, 5, 64), (64, 3)),
    ((128, 7, 64), (64, 4)),
    ((130, 3, 64), (64, 1)),
    ((101, 51, 64), (64, 32)),
    ((51, 101, 64), (32, 64)),
    ((100000, 1, 64), (64, 1)),
    ((3840, 2160, 1920), (1920, 1080)),
)


@_ac("AC-136.2")
@pytest.mark.unit
def test_ac_136_2_export_size(ac_id: str) -> None:
    from avkit_core.services.capture import export_size

    assert ac_id == "AC-136.2"
    for (width, height, edge), want in NAMED_SIZES:
        assert export_size(width, height, edge) == want, (width, height, edge)
    for width, height in ((300, 200), (64, 64), (1, 1), (200, 300)):
        assert export_size(width, height, None) == (width, height)
        long = max(width, height)
        assert export_size(width, height, long) == (width, height)
        assert export_size(width, height, long + 1) == (width, height)
    assert export_size(300, 200, 64) == (64, 43)
    half = Fraction(1, 2)
    wrong: list[tuple[int, int, int, tuple[int, int]]] = []
    for edge in range(64, 221):
        for width in range(1, 201):
            for height in range(1, 201):
                got = export_size(width, height, edge)
                long, short = max(width, height), min(width, height)
                if edge >= long:
                    want = (width, height)
                else:
                    new_short = max(1, int(Fraction(edge * short, long) + half))
                    want = (edge, new_short) if width >= height else (new_short, edge)
                if got != want:
                    wrong.append((width, height, edge, got))
                    if len(wrong) > 20:
                        break
            if len(wrong) > 20:
                break
        if len(wrong) > 20:
            break
    assert wrong == []


@_ac("AC-136.2")
@pytest.mark.unit
def test_ac_136_2_export_size_properties(ac_id: str) -> None:
    from avkit_core.services.capture import export_size

    assert ac_id == "AC-136.2"
    broken: list[tuple[int, int, int, tuple[int, int]]] = []
    for edge in (64, 65, 127, 128, 199, 220):
        for width in range(1, 201):
            for height in range(1, 201):
                new_w, new_h = export_size(width, height, edge)
                ok = (
                    max(new_w, new_h) == min(edge, max(width, height))
                    and new_w <= width
                    and new_h <= height
                    and new_w >= 1
                    and new_h >= 1
                    # Orientation is kept: a square stays square and no edge order flips.
                    # A near-square can round to square (127x128 at 64 is 63.5 -> 64).
                    and (width != height or new_w == new_h)
                    and (width >= height or new_w <= new_h)
                    and (width <= height or new_w >= new_h)
                )
                if not ok:
                    broken.append((width, height, edge, (new_w, new_h)))
    assert broken[:20] == []


# --- AC-136.3: EXPORT_NAME ---------------------------------------------------------------------


def _clean(name: str) -> bool:
    return not any(0xD800 <= ord(c) <= 0xDFFF or ord(c) < 32 or ord(c) == 127 for c in name)


@_ac("AC-136.3")
@pytest.mark.unit
def test_ac_136_3_export_stem(ac_id: str) -> None:
    from avkit_core.services.capture import export_stem

    assert ac_id == "AC-136.3"
    assert export_stem("shot") == "shot-export"
    assert export_stem("Łodz") == "Łodz-export"
    assert export_stem("CON") == "CON-export"
    for raw in ("a\ud800b", "\ud800", "bell\x07esc\x1b", "\x07\x1b", "..", ""):
        got = export_stem(raw)
        assert _clean(got), (raw, got)
        assert got.endswith("-export") or got == "export", (raw, got)
        assert got.removesuffix("-export") != "", (raw, got)
    assert export_stem("") == "export"
    assert export_stem("..") == "export"
    assert export_stem("\x07\x1b") == "export"
    assert export_stem("\ud800") == "export"
    assert export_stem("a\ud800b") == "a_b-export"
    assert export_stem("bell\x07esc\x1b") == "bell_esc-export"
    long = "a" * 150
    assert export_stem(long) == "a" * 100 + "-export"
    assert export_stem("b" * 99 + " " + "c" * 50) == "b" * 99 + "-export"


@_ac("AC-136.3")
@pytest.mark.unit
def test_ac_136_3_crop_dest_ext(ac_id: str, make_stack: Callable[..., Stack]) -> None:
    assert ac_id == "AC-136.3"
    stack = make_stack()
    with stack.factory() as uow:
        assert CaptureService._crop_dest(uow, stack.inbox, "x-export", ext=".jpg") == (
            stack.inbox / "x-export.jpg"
        )
        assert CaptureService._crop_dest(uow, stack.inbox, "x-export") == (
            stack.inbox / "x-export.png"
        )
        (stack.inbox / "x-export.png").write_bytes(b"png")
        assert CaptureService._crop_dest(uow, stack.inbox, "x-export", ext=".jpg") == (
            stack.inbox / "x-export_2.jpg"
        )
        (stack.inbox / "x-export.png").unlink()
        (stack.inbox / f"x-export.jpg{TMP}").write_bytes(b"other writer")
        assert CaptureService._crop_dest(uow, stack.inbox, "x-export", ext=".jpg") == (
            stack.inbox / "x-export_2.jpg"
        )


# --- AC-136.8: EXPORT_CHECKS -------------------------------------------------------------------

ARGUMENT_REFUSALS: tuple[tuple[str, dict[str, Any], tuple[type, str]], ...] = (
    ("format-gif", {"fmt": "gif"}, (ValidationError, FORMAT)),
    ("format-upper", {"fmt": "JPEG"}, (ValidationError, FORMAT)),
    ("format-empty", {"fmt": ""}, (ValidationError, FORMAT)),
    ("edge-63", {"fmt": "png", "max_edge": 63}, (ValidationError, MAX_EDGE)),
    ("edge-16384", {"fmt": "png", "max_edge": 16384}, (ValidationError, MAX_EDGE)),
    ("edge-true", {"fmt": "png", "max_edge": True}, (ValidationError, MAX_EDGE)),
    ("edge-float", {"fmt": "png", "max_edge": 64.0}, (ValidationError, MAX_EDGE)),
    ("edge-1e308", {"fmt": "png", "max_edge": 1e308}, (ValidationError, MAX_EDGE)),
    ("edge-neg", {"fmt": "png", "max_edge": -(10**18)}, (ValidationError, MAX_EDGE)),
    ("edge-huge", {"fmt": "png", "max_edge": 10**18}, (ValidationError, MAX_EDGE)),
    ("quality-0", {"fmt": "jpeg", "quality": 0}, (ValidationError, QUALITY)),
    ("quality-101", {"fmt": "jpeg", "quality": 101}, (ValidationError, QUALITY)),
    ("quality-true", {"fmt": "jpeg", "quality": True}, (ValidationError, QUALITY)),
    ("quality-float", {"fmt": "jpeg", "quality": 50.0}, (ValidationError, QUALITY)),
    ("quality-1e308", {"fmt": "jpeg", "quality": 1e308}, (ValidationError, QUALITY)),
    ("quality-neg", {"fmt": "jpeg", "quality": -(10**18)}, (ValidationError, QUALITY)),
    ("quality-huge", {"fmt": "jpeg", "quality": 10**18}, (ValidationError, QUALITY)),
    ("quality-png", {"fmt": "png", "quality": 50}, (ValidationError, QUALITY_PNG)),
)


def _assert_untouched(stack: Stack, names: list[str], rows: list[Any]) -> None:
    assert stack.annotate.exports == []
    assert stack.names() == names
    assert stack.rows() == rows


@pytest.mark.parametrize(
    ("kwargs", "want"),
    [(kwargs, want) for _, kwargs, want in ARGUMENT_REFUSALS],
    ids=[label for label, _, _ in ARGUMENT_REFUSALS],
)
@_ac("AC-136.8")
@pytest.mark.unit
def test_ac_136_8_argument_refusals(
    ac_id: str, kwargs: dict[str, Any], want: tuple[type, str], make_stack: Callable[..., Stack]
) -> None:
    assert ac_id == "AC-136.8"
    stack = make_stack()
    shot = stack.shot()
    names, rows = stack.names(), stack.rows()
    assert _raised(_call(stack, shot.id, **kwargs)) == want
    _assert_untouched(stack, names, rows)


def _no_bake(stack: Stack) -> str:
    shot = stack.marked()
    assert shot.annotated_path is not None
    shot.annotated_path.unlink()
    return shot.id


def _no_original(stack: Stack) -> str:
    shot = stack.shot()
    shot.original_path.unlink()
    return shot.id


def _malformed(stack: Stack) -> str:
    shot = stack.shot()
    (stack.inbox / "x.ann.json").write_text("{", encoding="utf-8")
    return shot.id


def _wide(stack: Stack) -> str:
    return stack.shot("wide.png", (20000, 10)).id


def _long(stack: Stack) -> str:
    return stack.shot("long.png", (70000, 1)).id


SHOT_REFUSALS: tuple[tuple[str, Callable[[Stack], str], str, tuple[type, str] | None], ...] = (
    ("unknown-id", lambda stack: "no-such-shot", "png", None),
    ("no-bake", _no_bake, "png", (NotFoundError, NO_BAKE)),
    ("no-original", _no_original, "png", (NotFoundError, NO_ORIGINAL)),
    ("malformed-sidecar", _malformed, "png", (AnnotationValidationError, MALFORMED)),
    ("webp-20000", _wide, "webp", (ValidationError, TOO_LARGE)),
    ("jpeg-70000", _long, "jpeg", (ValidationError, TOO_LARGE)),
)


@pytest.mark.parametrize(
    ("setup", "fmt", "want"),
    [(setup, fmt, want) for _, setup, fmt, want in SHOT_REFUSALS],
    ids=[label for label, _, _, _ in SHOT_REFUSALS],
)
@_ac("AC-136.8")
@pytest.mark.unit
def test_ac_136_8_shot_refusals(
    ac_id: str,
    setup: Callable[[Stack], str],
    fmt: str,
    want: tuple[type, str] | None,
    make_stack: Callable[..., Stack],
) -> None:
    assert ac_id == "AC-136.8"
    stack = make_stack()
    shot_id = setup(stack)
    names, rows = stack.names(), stack.rows()
    expected = want if want is not None else (NotFoundError, f"capture shot {shot_id} not found")
    assert _raised(_call(stack, shot_id, fmt=fmt)) == expected
    _assert_untouched(stack, names, rows)


@_ac("AC-136.8")
@pytest.mark.unit
def test_ac_136_8_bounds_accepted(ac_id: str, make_stack: Callable[..., Stack]) -> None:
    assert ac_id == "AC-136.8"
    stack = make_stack()
    shot = stack.shot()
    cases: tuple[dict[str, Any], ...] = (
        {"fmt": "png", "max_edge": 64},
        {"fmt": "png", "max_edge": 16383},
        {"fmt": "jpeg", "quality": 1},
        {"fmt": "webp", "quality": 100},
        {"fmt": "jpeg", "max_edge": 64, "quality": 100},
    )
    for kwargs in cases:
        _done(_call(stack, shot.id, **kwargs))
    assert [(c.size, c.quality) for c in stack.annotate.exports] == [
        ((64, 43), None),
        (SOURCE_SIZE, None),
        (SOURCE_SIZE, 1),
        (SOURCE_SIZE, 100),
        ((64, 43), 100),
    ]


# --- AC-136.9: EXPORT_SOURCE and the call trace -------------------------------------------------


@_ac("AC-136.9")
@pytest.mark.unit
def test_ac_136_9_marked_shot_exports_the_bake(
    ac_id: str, make_stack: Callable[..., Stack]
) -> None:
    from avkit_core.services.capture import export_size

    assert ac_id == "AC-136.9"
    stack = make_stack()
    shot = stack.marked()
    assert shot.annotated_path is not None and shot.annotated_path.is_file()
    result = _done(_call(stack, shot.id, fmt="jpeg", max_edge=64, quality=37))
    assert stack.annotate.exports == [
        ExportCall(
            source=shot.annotated_path,
            source_size=SOURCE_SIZE,
            out=stack.inbox / f"x-export.jpg{TMP}",
            fmt="jpeg",
            size=export_size(*SOURCE_SIZE, 64),
            quality=37,
        )
    ]
    assert export_size(*SOURCE_SIZE, 64) == (64, 43)
    assert result.source_id == shot.id


@pytest.mark.parametrize("sidecar", ["none", "empty"])
@_ac("AC-136.9")
@pytest.mark.unit
def test_ac_136_9_unmarked_shot_exports_the_original(
    ac_id: str, sidecar: str, make_stack: Callable[..., Stack]
) -> None:
    assert ac_id == "AC-136.9"
    stack = make_stack()
    shot = stack.shot()
    if sidecar == "empty":
        (stack.inbox / "x.ann.json").write_text(
            json.dumps({"version": 1, "annotations": []}), encoding="utf-8"
        )
    _done(_call(stack, shot.id, fmt="webp"))
    assert stack.annotate.exports == [
        ExportCall(
            source=shot.original_path,
            source_size=SOURCE_SIZE,
            out=stack.inbox / f"x-export.webp{TMP}",
            fmt="webp",
            size=SOURCE_SIZE,
            quality=None,
        )
    ]


# --- AC-136.10: EXPORT_WRITE with the real adapter ----------------------------------------------


def _tmp_opens(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    assert callable(Path.open)
    real_open = Path.open
    seen: list[tuple[str, str]] = []

    def recording_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if self.name.endswith(TMP):
            seen.append((self.name, mode))
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", recording_open)
    return seen


@_ac("AC-136.10")
@pytest.mark.unit
def test_ac_136_10_names_and_writes(
    ac_id: str, make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-136.10"
    stack = make_stack(real=True)
    shot = stack.marked()
    assert shot.annotated_path is not None and shot.sidecar_path is not None
    kept = {
        path: _sha(path) for path in (shot.original_path, shot.sidecar_path, shot.annotated_path)
    }
    source_row = stack.row(shot.id)
    opens = _tmp_opens(monkeypatch)
    first = _done(_call(stack, shot.id, fmt="png"))
    second = _done(_call(stack, shot.id, fmt="png", max_edge=64))
    third = _done(_call(stack, shot.id, fmt="jpeg"))
    assert [r.shot.original_path.name for r in (first, second, third)] == [
        "x-export.png",
        "x-export_2.png",
        "x-export_3.jpg",
    ]
    # Each temp's first open is the service's reservation; the adapter may open it again to write.
    first_open: dict[str, str] = {}
    for name, mode in opens:
        first_open.setdefault(name, mode)
    assert first_open == {
        "x-export.png" + TMP: "xb",
        "x-export_2.png" + TMP: "xb",
        "x-export_3.jpg" + TMP: "xb",
    }
    for result, size, fmt in (
        (first, SOURCE_SIZE, "PNG"),
        (second, (64, 43), "PNG"),
        (third, SOURCE_SIZE, "JPEG"),
    ):
        path = result.shot.original_path
        assert path.parent == stack.inbox
        assert result.source_id == shot.id
        assert result.bytes == path.stat().st_size
        with Image.open(path) as opened:
            assert (opened.format, opened.size) == (fmt, size)
        row = stack.row(result.shot.id)
        assert row.source == CaptureSource.Export
        assert (row.width, row.height, row.file_size) == (*size, path.stat().st_size)
        assert row.sidecar_path is None
        assert row.annotated_path is None
        assert row.original_path == path
    assert {path: _sha(path) for path in kept} == kept
    assert stack.row(shot.id) == source_row
    assert [name for name in stack.names() if name.endswith(TMP)] == []
    assert len(stack.rows()) == 4


@_ac("AC-136.10")
@pytest.mark.unit
def test_ac_136_10_png_then_jpeg(ac_id: str, make_stack: Callable[..., Stack]) -> None:
    assert ac_id == "AC-136.10"
    stack = make_stack(real=True)
    shot = stack.shot()
    png = _done(_call(stack, shot.id, fmt="png"))
    jpeg = _done(_call(stack, shot.id, fmt="jpeg"))
    assert (png.shot.original_path.name, jpeg.shot.original_path.name) == (
        "x-export.png",
        "x-export_2.jpg",
    )


@_ac("AC-136.10")
@pytest.mark.unit
def test_ac_136_10_another_writers_temp_is_left(
    ac_id: str, make_stack: Callable[..., Stack]
) -> None:
    assert ac_id == "AC-136.10"
    stack = make_stack(real=True)
    shot = stack.shot()
    other = stack.inbox / f"x-export.png{TMP}"
    other.write_bytes(b"another writer's temp")
    result = _done(_call(stack, shot.id, fmt="png"))
    assert result.shot.original_path.name == "x-export_2.png"
    assert other.read_bytes() == b"another writer's temp"
    assert [name for name in stack.names() if name.endswith(TMP)] == [other.name]


# --- AC-136.11: failure cleanup ----------------------------------------------------------------


class _OsProxy:
    """`os` for the service module, whose `replace` fails once the export is encoded."""

    def __getattr__(self, name: str) -> Any:
        if name == "replace":
            return self._replace
        return getattr(os, name)

    @staticmethod
    def _replace(*_: object, **__: object) -> None:
        raise OSError("replace failed at a private path")


def _fail_export(stack: Stack, monkeypatch: pytest.MonkeyPatch) -> None:
    stack.annotate.export_error = OSError("encode failed at a private path")


def _fail_probe(stack: Stack, monkeypatch: pytest.MonkeyPatch) -> None:
    def probe_hook(path: Path) -> None:
        # The output's probe only: the fake's own export probes the temp, which must pass.
        if "-export" in path.name and not path.name.endswith(TMP):
            raise InboxPathError(f"{path} is not a file")

    stack.annotate.on_probe = probe_hook


def _fail_replace(stack: Stack, monkeypatch: pytest.MonkeyPatch) -> None:
    assert hasattr(capture_mod, "os")
    monkeypatch.setattr(capture_mod, "os", _OsProxy())


def _fail_upsert(stack: Stack, monkeypatch: pytest.MonkeyPatch) -> None:
    assert hasattr(CaptureService, "_upsert_shot")

    def failing_upsert(*_: object, **__: object) -> None:
        raise RuntimeError("row failed at a private path")

    monkeypatch.setattr(CaptureService, "_upsert_shot", failing_upsert)


FAILURES: tuple[tuple[str, Callable[[Stack, pytest.MonkeyPatch], None]], ...] = (
    ("export-oserror", _fail_export),
    ("probe-inboxpath", _fail_probe),
    ("replace-oserror", _fail_replace),
    ("upsert-raises", _fail_upsert),
)


@pytest.mark.parametrize(
    "fail", [fail for _, fail in FAILURES], ids=[label for label, _ in FAILURES]
)
@pytest.mark.parametrize("fmt", ["png", "jpeg"])
@_ac("AC-136.11")
@pytest.mark.unit
def test_ac_136_11_failure_leaves_nothing(
    ac_id: str,
    fail: Callable[[Stack, pytest.MonkeyPatch], None],
    fmt: str,
    make_stack: Callable[..., Stack],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert ac_id == "AC-136.11"
    stack = make_stack()
    shot = stack.shot()
    names, rows, sha = stack.names(), stack.rows(), _sha(shot.original_path)
    fail(stack, monkeypatch)
    result = _call(stack, shot.id, fmt=fmt)
    assert _raised(result) == (CaptureFailedError, NOT_WRITTEN)
    assert "private" not in str(result)
    assert stack.names() == names
    assert stack.rows() == rows
    assert _sha(shot.original_path) == sha


@pytest.mark.parametrize(
    "error",
    [InboxPathError(NOT_OPENED), ConflictError(CHANGED)],
    ids=["inboxpath", "conflict"],
)
@_ac("AC-136.11")
@pytest.mark.unit
def test_ac_136_11_adapter_refusal_passes(
    ac_id: str, error: Exception, make_stack: Callable[..., Stack]
) -> None:
    assert ac_id == "AC-136.11"
    stack = make_stack()
    shot = stack.shot()
    names, rows = stack.names(), stack.rows()
    stack.annotate.export_error = error
    result = _call(stack, shot.id, fmt="png")
    assert _raised(result) == (type(error), str(error))
    assert len(stack.annotate.exports) == 1
    assert stack.names() == names
    assert stack.rows() == rows


# --- AC-136.12: NO_RAW_OUTPUT ------------------------------------------------------------------

MARKER = "private-marker-136"


@_ac("AC-136.12")
@pytest.mark.unit
def test_ac_136_12_log_keys_and_marker(ac_id: str, make_stack: Callable[..., Stack]) -> None:
    assert ac_id == "AC-136.12"
    stack = make_stack()
    shot = stack.shot(f"{MARKER}.png")
    with capture_logs() as logs:
        capture_mod.log.info("export.control", detail=MARKER)
        result = _call(stack, shot.id, fmt="jpeg", max_edge=64)
    control = [record for record in logs if record.get("event") == "export.control"]
    assert len(control) == 1 and control[0]["detail"] == MARKER
    _done(result)
    records = [record for record in logs if record.get("event") == "capture.export"]
    assert len(records) == 1, logs
    assert set(records[0]) - {"event", "log_level", "module"} == {"shot_id", "source_id"}
    assert records[0]["source_id"] == shot.id
    assert records[0]["shot_id"] == result.shot.id
    others = [record for record in logs if record.get("event") != "export.control"]
    assert all(MARKER not in repr(record) for record in others), others


@_ac("AC-136.12")
@pytest.mark.unit
def test_ac_136_12_refusals_hold_no_marker(ac_id: str, make_stack: Callable[..., Stack]) -> None:
    assert ac_id == "AC-136.12"
    stack = make_stack()
    shot = stack.shot(f"{MARKER}.png")
    messages: list[tuple[type, str]] = []
    for _, kwargs, want in ARGUMENT_REFUSALS:
        result = _call(stack, shot.id, **kwargs)
        assert _raised(result) == want
        messages.append(_raised(result))
    stack.annotate.export_error = OSError(f"encode failed at {MARKER}")
    failed = _call(stack, shot.id, fmt="png")
    assert _raised(failed) == (CaptureFailedError, NOT_WRITTEN)
    messages.append(_raised(failed))
    shot.original_path.unlink()
    missing = _call(stack, shot.id, fmt="png")
    assert _raised(missing) == (NotFoundError, NO_ORIGINAL)
    messages.append(_raised(missing))
    assert [text for _, text in messages if MARKER in text] == []
