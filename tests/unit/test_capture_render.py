"""MEU-104 render tests: RENDER_PORT, RENDER_BAKE and RENDER_SERVICE (Session 69 plan).

Imports stay inside the tests so a Red fails by assertion, not at collection.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
RENDERED = PNG_MAGIC + b"rendered"


def _ac(label: str, case: str | None = None):
    ident = label if case is None else f"{label}-{case}"
    return pytest.mark.parametrize("ac_id", [label], ids=[ident])


def _original(folder: Path, fmt: str) -> Path:
    """A 40x30 original: RGBA with part-transparent pixels for PNG, RGB for JPEG and WebP."""
    from PIL import Image

    image = Image.new("RGBA", (40, 30), (20, 40, 60, 255))
    for x in range(0, 40, 3):
        image.putpixel((x, x % 30), (250, 250, 250, 120))
    if fmt == "png":
        path = folder / "shot.png"
        image.save(path, format="PNG")
    elif fmt == "jpeg":
        path = folder / "shot.jpg"
        image.convert("RGB").save(path, format="JPEG", quality=90)
    else:
        path = folder / "shot.webp"
        image.convert("RGB").save(path, format="WEBP", quality=90)
    return path.resolve()


def _marks(case: str) -> list[object]:
    from avkit_core.domain.capture import PixelateAnnotation, RectAnnotation

    if case == "none":
        return []
    return [
        PixelateAnnotation(x=2, y=2, width=12, height=10, block_size=4),
        RectAnnotation(x=5, y=5, width=20, height=12, color="red", stroke_width=2),
    ]


def _state(folder: Path) -> dict[str, tuple[int, int]]:
    """Every file under `folder` -> (size, mtime_ns)."""
    return {
        str(p.relative_to(folder)): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in sorted(folder.rglob("*"))
        if p.is_file()
    }


class _RenderingPort:
    """The MEU-36 fake port plus a recording `render` that reads the file lock's state."""

    def __init__(self) -> None:
        from tests.unit.test_capture_service import FakeCapturePort

        self.base = FakeCapturePort()
        self.renders: list[tuple[Path, list[object]]] = []
        self.lock_held: list[bool] = []

    def __getattr__(self, name: str) -> object:
        return getattr(self.base, name)

    def render(self, original_path: Path, annotations: object) -> bytes:
        from avkit_core.services.capture import CAPTURE_FILE_LOCK

        self.renders.append((original_path, list(annotations)))  # type: ignore[call-overload]
        self.lock_held.append(CAPTURE_FILE_LOCK.locked())
        return RENDERED


def _service_stack(tmp_path: Path):
    from datetime import UTC, datetime

    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    port = _RenderingPort()
    service = CaptureService(
        factory,
        capture=port,  # type: ignore[arg-type]
        annotate=port,  # type: ignore[arg-type]
        settings=settings,
        clock=lambda: datetime(2026, 11, 13, 12, 0, 0, tzinfo=UTC),
    )
    return service, uow, port, inbox


def _register(service: object, inbox: Path, name: str = "shot.png") -> object:
    from avkit_core.domain.enums import CaptureSource

    path = (inbox / name).resolve()
    path.write_bytes(b"png-bytes")
    return service.register_shot(path, CaptureSource.Gui)  # type: ignore[attr-defined]


@_ac("AC-104.1")
@pytest.mark.unit
def test_ac_104_1_python_signatures(ac_id: str) -> None:
    assert ac_id == "AC-104.1"
    import inspect

    from avkit_core.ports.capture import ImageAnnotatePort
    from avkit_core.services.capture import CaptureService
    from avkit_infra.capture.adapter import CaptureAdapter

    def names(fn: object) -> list[str]:
        return list(inspect.signature(fn).parameters)  # type: ignore[arg-type]

    assert names(ImageAnnotatePort.render) == ["self", "original_path", "annotations"]
    assert names(CaptureAdapter.render) == ["self", "original_path", "annotations"]
    assert names(CaptureAdapter._bake_canvas) == ["self", "canvas", "annotations"]
    assert names(CaptureService.render_marks) == ["self", "shot_id", "annotations"]


@pytest.mark.parametrize(
    "ac_id,fmt,case",
    [("AC-104.2", fmt, case) for fmt in ("png", "jpeg", "webp") for case in ("none", "marks")],
    ids=[f"AC-104.2-{fmt}-{case}" for fmt in ("png", "jpeg", "webp") for case in ("none", "marks")],
)
@pytest.mark.unit
def test_ac_104_2_render_equals_bake_png(ac_id: str, fmt: str, case: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.2"
    from avkit_infra.capture.adapter import CaptureAdapter

    source = tmp_path / "src"
    source.mkdir()
    original = _original(source, fmt)
    marks = _marks(case)
    adapter = CaptureAdapter()
    out = tmp_path / "expected.png"
    adapter.bake(original, marks, out, "png")  # type: ignore[arg-type]

    got = adapter.render(original, marks)  # type: ignore[arg-type]

    assert got[:8] == PNG_MAGIC
    assert got == out.read_bytes()


@_ac("AC-104.2", "webp-setting")
@pytest.mark.unit
def test_ac_104_2_webp_setting_still_png(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.2"
    from tests.e2e.test_api_capture_flatten import MARKS, _register, _stack

    from avkit_api.routes.captures import _annotations_from_in
    from avkit_api.schemas.captures import AnnotateIn

    s = _stack(tmp_path)
    s.settings.set("capture", "annotated_format", "webp")
    shot_id = _register(s, "shot.png")
    marks = _annotations_from_in(AnnotateIn.model_validate({"annotations": MARKS}).annotations)
    expected = tmp_path / "expected.png"
    s.adapter.bake(s.inbox / "shot.png", marks, expected, "png")

    got = s.service.render_marks(shot_id, marks)

    assert got[:8] == PNG_MAGIC
    assert got == expected.read_bytes()


@_ac("AC-104.3", "writes-nothing")
@pytest.mark.unit
def test_ac_104_3_render_writes_nothing(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.3"
    from avkit_infra.capture.adapter import CaptureAdapter

    folder = tmp_path / "inbox"
    folder.mkdir()
    original = _original(folder, "png")
    before = _state(folder)

    got = CaptureAdapter().render(original, _marks("marks"))  # type: ignore[arg-type]

    assert got[:8] == PNG_MAGIC
    assert _state(folder) == before
    assert sorted(p.name for p in folder.iterdir()) == ["shot.png"]


@_ac("AC-104.3", "unreadable")
@pytest.mark.unit
def test_ac_104_3_unreadable_names_no_path(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.3"
    from avkit_core.domain.errors import InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter

    folder = tmp_path / "secret-folder"
    folder.mkdir()
    bogus = folder / "not-an-image.png"
    bogus.write_bytes(b"this is not an image")
    before = _state(folder)

    with pytest.raises(InboxPathError) as info:
        CaptureAdapter().render(bogus, [])

    message = str(info.value)
    assert message == "the image could not be opened"
    assert "secret-folder" not in message
    assert "not-an-image" not in message
    assert _state(folder) == before


@_ac("AC-104.4", "clamp")
@pytest.mark.unit
def test_ac_104_4_clamps_like_annotate_writes_nothing(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.4"
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation, TextAnnotation

    service, uow, port, inbox = _service_stack(tmp_path)
    shot = _register(service, inbox)
    marks = [
        RectAnnotation(x=40, y=-3, width=2, height=2, color="red", stroke_width=1),
        ArrowAnnotation(from_xy=(0, 0), to_xy=(32, 99), color="blue", stroke_width=2),
        TextAnnotation(x=32, y=32, text="hi", color="white", font_size=12, bg_color=None),
    ]
    files_before = _state(inbox)
    rows_before = [repr(row) for row in uow.capture_shots.list()]

    got = service.render_marks(shot.id, marks)  # type: ignore[attr-defined]

    assert got == RENDERED
    assert len(port.renders) == 1
    rendered_path, rendered_marks = port.renders[0]
    assert rendered_path == shot.original_path  # type: ignore[attr-defined]
    assert _state(inbox) == files_before
    assert [repr(row) for row in uow.capture_shots.list()] == rows_before
    assert port.base.bakes == []

    service.annotate_and_save(shot.id, marks)  # type: ignore[attr-defined]

    assert rendered_marks == port.base.bakes[-1]


@_ac("AC-104.4", "not-found")
@pytest.mark.unit
def test_ac_104_4_unknown_shot_and_missing_original(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.4"
    from avkit_core.domain.errors import NotFoundError

    service, _uow, port, inbox = _service_stack(tmp_path)

    with pytest.raises(NotFoundError) as unknown:
        service.render_marks("no-such-shot", [])
    assert str(unknown.value) == "capture shot no-such-shot not found"

    shot = _register(service, inbox, "gone.png")
    Path(shot.original_path).unlink()  # type: ignore[attr-defined]
    with pytest.raises(NotFoundError) as missing:
        service.render_marks(shot.id, [])  # type: ignore[attr-defined]
    assert str(missing.value) == "original image is missing"
    assert port.renders == []


@_ac("AC-104.5")
@pytest.mark.unit
def test_ac_104_5_render_holds_the_file_lock(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.5"
    from avkit_core.services.capture import CAPTURE_FILE_LOCK

    service, _uow, port, inbox = _service_stack(tmp_path)
    shot = _register(service, inbox)
    assert CAPTURE_FILE_LOCK.locked() is False

    service.render_marks(shot.id, [])  # type: ignore[attr-defined]

    assert port.lock_held == [True]
    assert CAPTURE_FILE_LOCK.locked() is False


@_ac("AC-104.10")
@pytest.mark.unit
def test_ac_104_10_one_mark_traced_to_pixels(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-104.10"
    import io

    from PIL import Image
    from tests.e2e.test_api_capture_flatten import AUTH, PREFIX, _register, _stack

    import avkit_api.routes.captures as routes
    from avkit_core.services.capture import CaptureService
    from avkit_infra.capture.adapter import CaptureAdapter

    seen: dict[str, list[object]] = {"from_in": [], "service": [], "clamp": [], "bake": []}
    from_in = routes._annotations_from_in
    render_marks = CaptureService.render_marks
    clamp = CaptureService._clamp_annotation
    bake_canvas = CaptureAdapter._bake_canvas

    def rec_from_in(items):  # type: ignore[no-untyped-def]
        out = from_in(items)
        seen["from_in"].append(list(out))
        return out

    def rec_render(self, shot_id, annotations):  # type: ignore[no-untyped-def]
        seen["service"].append(list(annotations))
        return render_marks(self, shot_id, annotations)

    def rec_clamp(self, item, width, height):  # type: ignore[no-untyped-def]
        seen["clamp"].append(item)
        return clamp(self, item, width, height)

    def rec_bake(self, canvas, annotations):  # type: ignore[no-untyped-def]
        seen["bake"].append(list(annotations))
        return bake_canvas(self, canvas, annotations)

    monkeypatch.setattr(routes, "_annotations_from_in", rec_from_in)
    monkeypatch.setattr(CaptureService, "render_marks", rec_render)
    monkeypatch.setattr(CaptureService, "_clamp_annotation", rec_clamp)
    monkeypatch.setattr(CaptureAdapter, "_bake_canvas", rec_bake)

    s = _stack(tmp_path)
    shot_id = _register(s, "shot.png")
    mark = {
        "type": "rect",
        "x": 2,
        "y": 2,
        "width": 20,
        "height": 12,
        "color": "#ff0000",
        "stroke_width": 2,
    }

    resp = s.client.post(f"{PREFIX}/{shot_id}/render", headers=AUTH, json={"annotations": [mark]})

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert [len(batch) for batch in seen["from_in"]] == [1]  # type: ignore[arg-type]
    domain = seen["from_in"][0][0]  # type: ignore[index]
    assert (domain.x, domain.y, domain.width, domain.height) == (2, 2, 20, 12)
    assert seen["service"] == [[domain]]
    assert seen["clamp"] == [domain]
    assert seen["bake"] == [[domain]]
    pixels = Image.open(io.BytesIO(resp.content)).convert("RGB")
    red, green, blue = pixels.getpixel((2, 8))  # type: ignore[misc]
    assert red > 200 and green < 60 and blue < 60
    assert pixels.getpixel((40, 40)) != (255, 0, 0)
