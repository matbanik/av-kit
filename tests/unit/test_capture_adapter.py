"""MEU-35 capture adapter + table tests. Imports stay inside tests so collection cannot ERROR."""

from __future__ import annotations

import ast
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"
INFRA_PYPROJECT = REPO_ROOT / "packages" / "infrastructure" / "pyproject.toml"
ADAPTER_REL = "capture/adapter.py"
PIL_FORBIDDEN = {"PIL", "mss"}
CAPTURE_SHOT_COLUMNS = (
    "id",
    "original_path",
    "annotated_path",
    "sidecar_path",
    "display_name",
    "width",
    "height",
    "file_size",
    "source",
    "created_at",
    "updated_at",
)
CAPTURE_REQUEST_COLUMNS = ("id", "status", "shot_id", "created_at", "expires_at")
CAPTURE_MIN_EDGE_PX = 8
MSS_VIRTUAL_INDEX = 0
GEOMETRY_FIXTURE = REPO_ROOT / "ui" / "tests" / "e2e" / "fixtures" / "capture-geometry.json"
# ARROW_HEAD, ARROW_SHAFT_OVERLAP_PX and AA_LIMITS (Session 36 plan), restated so the oracles
# do not take their geometry from the adapter under test.
PLAN_HEAD = (5, 0.45, 10)
PLAN_OVERLAP_PX = 1
AA_HALO_PX = 3
AA_CHANNEL_TOL = 8


def _arrow_cases() -> list[dict[str, object]]:
    import json

    return json.loads(GEOMETRY_FIXTURE.read_text(encoding="utf-8"))["arrows"]


def _plan_head(
    from_xy: tuple[float, float], to_xy: tuple[float, float], stroke: int
) -> tuple[float, tuple[float, float], tuple[float, float], tuple[float, float]]:
    import math

    factor, angle, minimum = PLAN_HEAD
    theta = math.atan2(to_xy[1] - from_xy[1], to_xy[0] - from_xy[0])
    head = max(minimum, factor * stroke)
    left = (to_xy[0] - head * math.cos(theta - angle), to_xy[1] - head * math.sin(theta - angle))
    right = (to_xy[0] - head * math.cos(theta + angle), to_xy[1] - head * math.sin(theta + angle))
    return head, (float(to_xy[0]), float(to_xy[1])), left, right


def _plan_shaft_end(
    from_xy: tuple[float, float], to_xy: tuple[float, float], stroke: int
) -> tuple[float, float] | None:
    import math

    head = _plan_head(from_xy, to_xy, stroke)[0]
    length = math.hypot(to_xy[0] - from_xy[0], to_xy[1] - from_xy[1])
    back = head * math.cos(PLAN_HEAD[1]) - PLAN_OVERLAP_PX
    if length <= back:
        return None
    ux, uy = (to_xy[0] - from_xy[0]) / length, (to_xy[1] - from_xy[1]) / length
    return (to_xy[0] - ux * back, to_xy[1] - uy * back)


def _plan_tile(
    from_xy: tuple[int, int], to_xy: tuple[int, int], stroke: int, size: tuple[int, int]
) -> tuple[int, int, int, int]:
    # BAKE_AA step (1): bbox of from, the shaft end and the head, padded by stroke/2 + 4,
    # rounded outward (end-exclusive) and clipped to the image.
    import math

    _, tip, left, right = _plan_head(from_xy, to_xy, stroke)
    end = _plan_shaft_end(from_xy, to_xy, stroke)
    points = [(float(from_xy[0]), float(from_xy[1])), tip, left, right] + ([end] if end else [])
    pad = stroke / 2 + 4
    x0 = max(0, math.floor(min(p[0] for p in points) - pad))
    y0 = max(0, math.floor(min(p[1] for p in points) - pad))
    x1 = min(size[0], math.ceil(max(p[0] for p in points) + pad) + 1)
    y1 = min(size[1], math.ceil(max(p[1] for p in points) + pad) + 1)
    return x0, y0, x1, y1


def _inside_triangle(p: tuple[float, float], tri: tuple[tuple[float, float], ...]) -> bool:
    def cross(o: tuple[float, float], a: tuple[float, float]) -> float:
        return (a[0] - o[0]) * (p[1] - o[1]) - (a[1] - o[1]) * (p[0] - o[0])

    signs = [cross(tri[0], tri[1]), cross(tri[1], tri[2]), cross(tri[2], tri[0])]
    return all(s >= -1e-9 for s in signs) or all(s <= 1e-9 for s in signs)


def _outside_triangle(p: tuple[float, float], tri: tuple[tuple[float, float], ...]) -> float:
    # Distance outside the triangle (0 inside), measured at PIXEL_CENTRE (x, y).
    import math

    worst = -math.inf
    cx = sum(v[0] for v in tri) / 3
    cy = sum(v[1] for v in tri) / 3
    for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
        nx, ny = b[1] - a[1], a[0] - b[0]
        n = math.hypot(nx, ny)
        nx, ny = nx / n, ny / n
        if (cx - a[0]) * nx + (cy - a[1]) * ny > 0:
            nx, ny = -nx, -ny
        worst = max(worst, (p[0] - a[0]) * nx + (p[1] - a[1]) * ny)
    return max(0.0, worst)


def _coverage(px: tuple[int, ...], color: tuple[int, int, int]) -> float:
    return max((255 - px[i]) / 255 for i in range(3) if color[i] == 0)


def _equals(px: tuple[int, ...], color: tuple[int, int, int]) -> bool:
    return all(abs(c - m) <= AA_CHANNEL_TOL for c, m in zip(px[:3], color, strict=True))


def _bake_arrow(
    tmp_path: Path, size: tuple[int, int], arrow: object, name: str
) -> tuple[object, object]:
    from PIL import Image
    from tools import capture_bake_fixture as fixture

    original = fixture.write_original(tmp_path / f"{name}-original.png", size)
    baked = fixture.bake(original, [arrow], tmp_path / f"{name}-baked.png")
    return Image.open(original).convert("RGB"), Image.open(baked).convert("RGB")


def _changed_outside(original: object, baked: object, tile: tuple[int, int, int, int]) -> list:
    x0, y0, x1, y1 = tile
    return [
        (x, y)
        for y in range(baked.height)
        for x in range(baked.width)
        if not (x0 <= x < x1 and y0 <= y < y1)
        and baked.getpixel((x, y)) != original.getpixel((x, y))
    ]


def _tip_oracle(image: object) -> tuple[int, int]:
    # ARROW_TIP_ORACLE over x > head base: (leak pixels, max channel deviation from white
    # of the pixels more than AA_HALO_PX outside the head).
    import math

    head, tip, left, right = _plan_head((20, 60), (200, 60), 12)
    base_x = 200 - head * math.cos(PLAN_HEAD[1])
    leaks, halo = 0, 0
    for y in range(image.height):
        for x in range(math.floor(base_x) + 1, image.width):
            if x <= base_x:
                continue
            out = _outside_triangle((x, y), (tip, left, right))
            px = image.getpixel((x, y))
            if out > AA_HALO_PX:
                halo = max(halo, max(255 - c for c in px))
            if out > 1 and _coverage(px, (255, 0, 0)) >= 0.5:
                leaks += 1
    return leaks, halo


def _now() -> datetime:
    return datetime.now(UTC)


class FakeShot:
    def __init__(self, width: int, height: int, rgb: bytes) -> None:
        self.size = (width, height)
        self.rgb = rgb


class FakeMss:
    def __init__(self, shot: FakeShot | None = None) -> None:
        self.monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080},
            {"left": 0, "top": 0, "width": 800, "height": 600},
        ]
        self.grabs: list[object] = []
        self._shot = shot or FakeShot(32, 32, b"\xff\xff\xff" * (32 * 32))

    def grab(self, region: object) -> FakeShot:
        self.grabs.append(region)
        return self._shot

    def __enter__(self) -> FakeMss:
        return self

    def __exit__(self, *args: object) -> None:
        return None


def _white_rgb(width: int, height: int) -> bytes:
    return b"\xff\xff\xff" * (width * height)


def _black_rgb(width: int, height: int) -> bytes:
    return b"\x00\x00\x00" * (width * height)


def _imported_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


@pytest.mark.parametrize("ac_id", ["AC-35.1"], ids=["AC-35.1"])
@pytest.mark.unit
def test_ac_35_1_capture_tables_exist_no_jobs_sti(ac_id: str) -> None:
    assert ac_id == "AC-35.1"
    from tests.integration.test_sqlite_uow import TABLES

    from avkit_infra.database.models import Base

    names = set(Base.metadata.tables)
    assert "capture_shots" in names
    assert "capture_requests" in names
    assert "jobs" not in names
    assert "capture_shots" in TABLES
    assert "capture_requests" in TABLES
    shots = Base.metadata.tables["capture_shots"]
    requests = Base.metadata.tables["capture_requests"]
    assert "original_path" in shots.columns
    path_unique = bool(shots.c.original_path.unique) or any(
        bool(getattr(idx, "unique", False)) and "original_path" in idx.columns.keys()
        for idx in shots.indexes
    )
    assert path_unique
    shot_index_cols = {name for idx in shots.indexes for name in idx.columns.keys()}
    req_index_cols = {name for idx in requests.indexes for name in idx.columns.keys()}
    assert "created_at" in shot_index_cols
    assert "status" in req_index_cols
    assert "expires_at" in req_index_cols


@pytest.mark.parametrize("ac_id", ["AC-35.2"], ids=["AC-35.2"])
@pytest.mark.unit
def test_ac_35_2_migrations_if_not_exists_both_tables(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.2"
    from avkit_infra.database.engine import create_sqlite_engine
    from avkit_infra.database.migrations import MIGRATIONS, apply_migrations
    from avkit_infra.database.models import CaptureRequestRow, CaptureShotRow

    assert CaptureShotRow.__tablename__ == "capture_shots"
    assert CaptureRequestRow.__tablename__ == "capture_requests"
    blob = "\n".join(MIGRATIONS).lower()
    assert "create table if not exists capture_shots" in blob
    assert "create table if not exists capture_requests" in blob
    engine = create_sqlite_engine(tmp_path / "capture-mig.db")
    apply_migrations(engine)
    apply_migrations(engine)


@pytest.mark.parametrize("ac_id", ["AC-35.3"], ids=["AC-35.3"])
@pytest.mark.unit
def test_ac_35_3_uow_capture_repo_methods(ac_id: str) -> None:
    assert ac_id == "AC-35.3"
    from avkit_core.ports.storage import CaptureRequestRepository, CaptureShotRepository, UnitOfWork

    shot_methods = ("add", "get", "list", "save", "delete", "get_by_path")
    req_methods = ("add", "get", "save", "list", "get_pending_request")
    for name in shot_methods:
        assert hasattr(CaptureShotRepository, name)
    for name in req_methods:
        assert hasattr(CaptureRequestRepository, name)
    assert hasattr(UnitOfWork, "capture_shots")
    assert hasattr(UnitOfWork, "capture_requests")


@pytest.mark.parametrize("ac_id", ["AC-35.4"], ids=["AC-35.4"])
@pytest.mark.unit
def test_ac_35_4_round_trip_columns(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.4"
    from avkit_core.domain.capture import CaptureRequest, CaptureShot
    from avkit_core.domain.enums import CaptureRequestStatus, CaptureSource
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.models import CaptureRequestRow, CaptureShotRow
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    shot_cols = tuple(col.name for col in CaptureShotRow.__table__.columns)
    req_cols = tuple(col.name for col in CaptureRequestRow.__table__.columns)
    assert shot_cols == CAPTURE_SHOT_COLUMNS
    assert req_cols == CAPTURE_REQUEST_COLUMNS
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    factory = create_session_factory(engine)
    now = _now()
    original = (tmp_path / "shot.png").resolve()
    annotated = (tmp_path / "shot.annotated.png").resolve()
    sidecar = (tmp_path / "shot.ann.json").resolve()
    shot = CaptureShot(
        id=str(uuid4()),
        original_path=original,
        annotated_path=annotated,
        sidecar_path=sidecar,
        display_name="shot.png",
        width=32,
        height=32,
        file_size=12,
        source=CaptureSource.Scan,
        created_at=now,
        updated_at=now,
    )
    request = CaptureRequest(
        id=str(uuid4()),
        status=CaptureRequestStatus.Pending,
        shot_id=None,
        created_at=now,
        expires_at=now + timedelta(seconds=120),
    )
    with SqlAlchemyUnitOfWork(factory) as uow:
        uow.capture_shots.add(shot)
        uow.capture_requests.add(request)
    with SqlAlchemyUnitOfWork(factory) as uow:
        loaded = uow.capture_shots.get(shot.id)
        by_path = uow.capture_shots.get_by_path(original)
        listed = uow.capture_shots.list()
        pending = uow.capture_requests.get_pending_request()
        loaded_req = uow.capture_requests.get(request.id)
        listed_reqs = uow.capture_requests.list()
    assert loaded is not None
    assert loaded.sidecar_path == sidecar
    assert loaded.annotated_path == annotated
    assert loaded.source is CaptureSource.Scan
    assert by_path is not None
    assert by_path.id == shot.id
    assert listed[0].id == shot.id
    assert pending is not None
    assert pending.id == request.id
    assert loaded_req is not None
    assert loaded_req.status is CaptureRequestStatus.Pending
    assert listed_reqs[0].id == request.id
    from dataclasses import replace

    with SqlAlchemyUnitOfWork(factory) as uow:
        stored = uow.capture_shots.get(shot.id)
        assert stored is not None
        uow.capture_shots.save(replace(stored, display_name="renamed.png"))
        uow.capture_requests.save(
            replace(request, status=CaptureRequestStatus.Cancelled)
        )
    with SqlAlchemyUnitOfWork(factory) as uow:
        renamed = uow.capture_shots.get(shot.id)
        cancelled = uow.capture_requests.get(request.id)
        assert renamed is not None
        assert renamed.display_name == "renamed.png"
        assert cancelled is not None
        assert cancelled.status is CaptureRequestStatus.Cancelled
        uow.capture_shots.delete(shot.id)
    with SqlAlchemyUnitOfWork(factory) as uow:
        assert uow.capture_shots.get(shot.id) is None


@pytest.mark.parametrize("ac_id", ["AC-35.5"], ids=["AC-35.5"])
@pytest.mark.unit
def test_ac_35_5_pillow_mss_in_infra_not_core(ac_id: str) -> None:
    assert ac_id == "AC-35.5"
    text = INFRA_PYPROJECT.read_text(encoding="utf-8").lower()
    assert "pillow" in text
    assert "mss" in text
    hits: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        found = sorted(_imported_names(path) & PIL_FORBIDDEN)
        if found:
            hits.append(f"{path}:{found}")
    assert hits == []


@pytest.mark.parametrize("ac_id", ["AC-35.6"], ids=["AC-35.6"])
@pytest.mark.unit
def test_ac_35_6_fullscreen_grabs_monitor_zero(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.6"
    from avkit_infra.capture.adapter import CaptureAdapter

    fake = FakeMss(FakeShot(32, 32, _white_rgb(32, 32)))
    adapter = CaptureAdapter(mss_factory=lambda: fake, platform="win32")
    out = tmp_path / "full.png"
    probe = adapter.capture_fullscreen(out)
    assert fake.grabs == [fake.monitors[MSS_VIRTUAL_INDEX]]
    assert out.is_file()
    assert probe.width == 32
    assert probe.height == 32
    assert probe.file_size == out.stat().st_size


@pytest.mark.parametrize("ac_id", ["AC-35.7"], ids=["AC-35.7"])
@pytest.mark.unit
def test_ac_35_7_region_bbox_and_min_edge(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.7"
    from avkit_core.domain.capture import BBox
    from avkit_infra.capture.adapter import CaptureAdapter

    fake = FakeMss(FakeShot(16, 16, _white_rgb(16, 16)))
    adapter = CaptureAdapter(mss_factory=lambda: fake, platform="win32")
    bbox = BBox(x=10, y=20, width=16, height=16)
    adapter.capture_region(tmp_path / "region.png", bbox)
    assert fake.grabs == [{"left": 10, "top": 20, "width": 16, "height": 16}]
    fake.grabs.clear()
    from avkit_core.domain.errors import ValidationError

    tiny = SimpleNamespace(x=0, y=0, width=7, height=7)
    with pytest.raises(ValidationError):
        adapter.capture_region(tmp_path / "tiny.png", tiny)  # type: ignore[arg-type]
    assert fake.grabs == []
    with pytest.raises(ValidationError):
        BBox(x=0, y=0, width=CAPTURE_MIN_EDGE_PX - 1, height=CAPTURE_MIN_EDGE_PX - 1)


@pytest.mark.parametrize("ac_id", ["AC-35.8"], ids=["AC-35.8"])
@pytest.mark.unit
def test_ac_35_8_non_windows_raises_before_grab(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.8"
    from avkit_core.domain.errors import CaptureNotSupportedError
    from avkit_infra.capture.adapter import CaptureAdapter

    fake = FakeMss()
    adapter = CaptureAdapter(mss_factory=lambda: fake, platform="linux")
    with pytest.raises(CaptureNotSupportedError):
        adapter.capture_fullscreen(tmp_path / "x.png")
    assert fake.grabs == []


@pytest.mark.parametrize("ac_id", ["AC-35.9"], ids=["AC-35.9"])
@pytest.mark.unit
def test_ac_35_9_black_frame_fails_and_leaves_no_png(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.9"
    from avkit_core.domain.errors import CaptureFailedError
    from avkit_infra.capture.adapter import CaptureAdapter

    fake = FakeMss(FakeShot(16, 16, _black_rgb(16, 16)))
    adapter = CaptureAdapter(mss_factory=lambda: fake, platform="win32")
    out = tmp_path / "black.png"
    with pytest.raises(CaptureFailedError):
        adapter.capture_fullscreen(out)
    assert out.exists() is False


@pytest.mark.parametrize("ac_id", ["AC-35.10"], ids=["AC-35.10"])
@pytest.mark.unit
def test_ac_35_10_probe_rejects_non_image(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.10"
    from avkit_core.domain.errors import InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter(mss_factory=lambda: FakeMss(), platform="win32")
    missing = tmp_path / "missing.png"
    with pytest.raises(InboxPathError):
        adapter.probe(missing)
    text = tmp_path / "note.txt"
    text.write_text("not an image", encoding="utf-8")
    with pytest.raises(InboxPathError):
        adapter.probe(text)


@pytest.mark.parametrize("ac_id", ["AC-35.11"], ids=["AC-35.11"])
@pytest.mark.unit
def test_ac_35_11_bake_does_not_mutate_original(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.11"
    import hashlib

    from PIL import Image

    from avkit_core.domain.capture import RectAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    original = tmp_path / "orig.png"
    Image.new("RGB", (32, 32), (255, 255, 255)).save(original)
    before = hashlib.sha256(original.read_bytes()).hexdigest()
    adapter = CaptureAdapter(mss_factory=lambda: FakeMss(), platform="win32")
    out = tmp_path / "baked.png"
    adapter.bake(
        original,
        [RectAnnotation(x=2, y=2, width=8, height=8, color="red", stroke_width=1)],
        out,
    )
    assert out.is_file()
    assert hashlib.sha256(original.read_bytes()).hexdigest() == before


@pytest.mark.parametrize("ac_id", ["AC-35.12"], ids=["AC-35.12"])
@pytest.mark.unit
def test_ac_35_12_highlight_is_alpha_composite_not_opaque(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-35.12"
    from PIL import Image, ImageStat

    from avkit_core.domain.capture import HighlightAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    original = tmp_path / "white.png"
    Image.new("RGB", (32, 32), (255, 255, 255)).save(original)
    adapter = CaptureAdapter(mss_factory=lambda: FakeMss(), platform="win32")
    out = tmp_path / "hl.png"
    adapter.bake(
        original,
        [HighlightAnnotation(x=0, y=0, width=32, height=32, color="red", opacity=0.4)],
        out,
    )
    baked = Image.open(out).convert("RGB")
    mean = ImageStat.Stat(baked).mean
    assert mean != [255.0, 0.0, 0.0]
    assert mean != [255.0, 255.0, 255.0]


@pytest.mark.parametrize("ac_id", ["AC-35.13"], ids=["AC-35.13"])
@pytest.mark.unit
def test_ac_35_13_arrow_uses_line_and_polygon(ac_id: str) -> None:
    assert ac_id == "AC-35.13"
    source = (
        REPO_ROOT
        / "packages"
        / "infrastructure"
        / "src"
        / "avkit_infra"
        / "capture"
        / "adapter.py"
    ).read_text(encoding="utf-8")
    assert "polygon" in source
    assert ".line(" in source or "draw.line" in source
    assert "segoeui.ttf" in source
    assert "arial.ttf" in source
    assert "load_default" in source


@pytest.mark.parametrize("ac_id", ["AC-35.14"], ids=["AC-35.14"])
@pytest.mark.unit
def test_ac_35_14_log_module_layout_and_fake_uow(ac_id: str) -> None:
    assert ac_id == "AC-35.14"
    from tests.integration.test_sqlite_uow import INFRA_LAYOUT, UOW_ATTRIBUTES
    from tests.unit.test_conversion_service import FakeUnitOfWork as ConvFake
    from tests.unit.test_services import FakeUnitOfWork as SvcFake

    assert ADAPTER_REL in INFRA_LAYOUT
    assert "capture_shots" in UOW_ATTRIBUTES
    assert "capture_requests" in UOW_ATTRIBUTES
    assert "conversion_jobs" in UOW_ATTRIBUTES
    source = (
        REPO_ROOT
        / "packages"
        / "infrastructure"
        / "src"
        / "avkit_infra"
        / "capture"
        / "adapter.py"
    ).read_text(encoding="utf-8")
    assert 'module="capture"' in source or "module='capture'" in source
    assert hasattr(SvcFake(), "capture_shots")
    assert hasattr(SvcFake(), "capture_requests")
    assert hasattr(ConvFake(), "capture_shots")
    assert hasattr(ConvFake(), "capture_requests")
    _ = uuid4()


@pytest.mark.parametrize("ac_id", ["AC-59.2"], ids=["AC-59.2"])
@pytest.mark.unit
def test_ac_59_2_shared_arrowhead_vertices(ac_id: str) -> None:
    assert ac_id == "AC-59.2"
    import math

    from avkit_infra.capture import adapter as capture_adapter

    assert hasattr(capture_adapter, "arrowhead_vertices")
    tip, left, right = capture_adapter.arrowhead_vertices((0, 0), (100, 0), 3)
    head = max(10, 5 * 3)
    expected_left = (
        100 - head * math.cos(0.0 - 0.45),
        0 - head * math.sin(0.0 - 0.45),
    )
    expected_right = (
        100 - head * math.cos(0.0 + 0.45),
        0 - head * math.sin(0.0 + 0.45),
    )
    assert tip == (100, 0)
    assert left == pytest.approx(expected_left)
    assert right == pytest.approx(expected_right)
    assert head == 15
    horizontal = _arrow_cases()[0]
    assert left == pytest.approx(tuple(horizontal["left"]), abs=1e-9)
    assert right == pytest.approx(tuple(horizontal["right"]), abs=1e-9)


@pytest.mark.parametrize("ac_id", ["AC-59.3"], ids=["AC-59.3"])
@pytest.mark.unit
def test_ac_59_3_text_anchor_la_and_bg_plate(ac_id: str) -> None:
    assert ac_id == "AC-59.3"
    source = (
        REPO_ROOT
        / "packages"
        / "infrastructure"
        / "src"
        / "avkit_infra"
        / "capture"
        / "adapter.py"
    ).read_text(encoding="utf-8")
    apply = source.split("def _apply_text", 1)[1].split("def ", 1)[0]
    assert 'anchor="la"' in apply or "anchor='la'" in apply
    assert "textbbox" in apply or "text_plate_box" in apply
    assert "bg_color" in apply
    from avkit_infra.capture.adapter import text_plate_box

    assert text_plate_box(10, 20, "Hi", 16) == (10, 26, 25, 38)


@pytest.mark.parametrize("ac_id", ["AC-67.29"], ids=["AC-67.29"])
@pytest.mark.unit
def test_ac_67_29_bake_output_formats(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.29"
    import io

    from PIL import Image

    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.errors import ValidationError
    from avkit_infra.capture.adapter import LOSSY_QUALITY, CaptureAdapter

    original = tmp_path / "orig.png"
    image = Image.new("RGB", (40, 30), (10, 120, 200))
    for x in range(0, 40, 3):
        image.putpixel((x, x % 30), (255, 255, 255))
    image.save(original)
    marks = [RectAnnotation(x=2, y=2, width=12, height=9, color="red", stroke_width=2)]
    adapter = CaptureAdapter(mss_factory=lambda: FakeMss(), platform="win32")

    default_png = tmp_path / "default.png"
    named_png = tmp_path / "named.png"
    adapter.bake(original, marks, default_png)
    adapter.bake(original, marks, named_png, "png")
    assert default_png.read_bytes() == named_png.read_bytes()
    canvas = Image.open(default_png).convert("RGB")

    for fmt, pil_format, magic in (("jpeg", "JPEG", b"\xff\xd8\xff"), ("webp", "WEBP", b"RIFF")):
        out = tmp_path / f"baked.{fmt}"
        probe = adapter.bake(original, marks, out, fmt)
        data = out.read_bytes()
        assert data[: len(magic)] == magic
        expected = io.BytesIO()
        canvas.save(expected, format=pil_format, quality=LOSSY_QUALITY)
        assert data == expected.getvalue(), fmt
        assert (probe.width, probe.height) == (40, 30)

    rejected = tmp_path / "baked.gif"
    with pytest.raises(ValidationError):
        adapter.bake(original, marks, rejected, "gif")
    assert not rejected.exists()


@pytest.mark.parametrize("ac_id", ["AC-83.2"], ids=["AC-83.2"])
@pytest.mark.unit
def test_ac_83_2_python_arrow_geometry_reproduces_arrow_cases(ac_id: str) -> None:
    assert ac_id == "AC-83.2"
    import math

    from avkit_infra.capture import adapter as capture_adapter

    assert (
        capture_adapter.ARROWHEAD_LENGTH_FACTOR,
        capture_adapter.ARROWHEAD_ANGLE_RAD,
        capture_adapter.ARROWHEAD_MIN_PX,
    ) == PLAN_HEAD
    assert capture_adapter.ARROW_SHAFT_OVERLAP_PX == 1
    cases = _arrow_cases()
    assert len(cases) == 5
    for case in cases:
        frm, to, stroke = tuple(case["from"]), tuple(case["to"]), case["stroke"]
        end = capture_adapter.arrow_shaft_end(frm, to, stroke)
        if case["shaft_end"] is None:
            assert end is None, case
        else:
            assert end == pytest.approx(tuple(case["shaft_end"]), abs=1e-9), case
        if case["head"] is None:
            # Zero length: the legacy from->to shaft and no head (SHAFT_END, 09:366).
            assert math.hypot(to[0] - frm[0], to[1] - frm[1]) == 0
            assert end == pytest.approx(to)
            continue
        factor, minimum = capture_adapter.ARROWHEAD_LENGTH_FACTOR, capture_adapter.ARROWHEAD_MIN_PX
        assert max(minimum, factor * stroke) == case["head"]
        tip, left, right = capture_adapter.arrowhead_vertices(frm, to, stroke)
        assert tip == to
        assert left == pytest.approx(tuple(case["left"]), abs=1e-9), case
        assert right == pytest.approx(tuple(case["right"]), abs=1e-9), case


@pytest.mark.parametrize("ac_id", ["AC-83.3"], ids=["AC-83.3"])
@pytest.mark.unit
def test_ac_83_3_shaft_corners_inside_head(ac_id: str) -> None:
    assert ac_id == "AC-83.3"
    import math

    from avkit_infra.capture import adapter as capture_adapter

    directions = [case for case in _arrow_cases() if case["head"] is not None]
    assert len(directions) == 4
    for case in directions:
        to = tuple(case["to"])
        length = math.hypot(to[0] - case["from"][0], to[1] - case["from"][1])
        ux, uy = (to[0] - case["from"][0]) / length, (to[1] - case["from"][1]) / length
        frm = (to[0] - 1000 * ux, to[1] - 1000 * uy)
        for stroke in range(1, 65):
            tri = capture_adapter.arrowhead_vertices(frm, to, stroke)
            end = capture_adapter.arrow_shaft_end(frm, to, stroke)
            assert end is not None, (case, stroke)
            for side in (1, -1):
                corner = (end[0] - side * stroke / 2 * uy, end[1] + side * stroke / 2 * ux)
                assert _inside_triangle(corner, tri), (case, stroke, side)
                # Negative: with the shaft ending at the tip, the corner falls outside the head.
                at_tip = (to[0] - side * stroke / 2 * uy, to[1] + side * stroke / 2 * ux)
                assert not _inside_triangle(at_tip, tri), (case, stroke, side)


@pytest.mark.parametrize("ac_id", ["AC-83.5"], ids=["AC-83.5"])
@pytest.mark.integration
def test_ac_83_5_arrow_tip_oracle(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-83.5"
    from avkit_core.domain.capture import ArrowAnnotation
    from avkit_infra.capture import adapter as capture_adapter

    arrow = ArrowAnnotation(from_xy=(20, 60), to_xy=(200, 60), color="#FF0000", stroke_width=12)
    _, baked = _bake_arrow(tmp_path, (240, 120), arrow, "tip")
    leaks, halo = _tip_oracle(baked)
    assert leaks == 0
    assert halo <= AA_CHANNEL_TOL

    # Negative control: the same bake with the shaft run to the tip must fail the oracle.
    def shaft_to_tip(
        from_xy: tuple[int, int], to_xy: tuple[int, int], stroke_width: int
    ) -> tuple[float, float]:
        return (float(to_xy[0]), float(to_xy[1]))

    monkeypatch.setattr(capture_adapter, "arrow_shaft_end", shaft_to_tip)
    _, control = _bake_arrow(tmp_path, (240, 120), arrow, "control")
    control_leaks, control_halo = _tip_oracle(control)
    assert control_leaks > 0 or control_halo > AA_CHANNEL_TOL


@pytest.mark.parametrize("ac_id", ["AC-83.6"], ids=["AC-83.6"])
@pytest.mark.integration
def test_ac_83_6_edge_oracle(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-83.6"
    import math

    from avkit_core.domain.capture import ArrowAnnotation

    frm, to, stroke, color = (20, 100), (200, 20), 6, (0, 0, 255)
    arrow = ArrowAnnotation(from_xy=frm, to_xy=to, color="#0000FF", stroke_width=stroke)
    original, baked = _bake_arrow(tmp_path, (240, 120), arrow, "edge")
    length = math.hypot(to[0] - frm[0], to[1] - frm[1])
    ux, uy = (to[0] - frm[0]) / length, (to[1] - frm[1]) / length
    head = _plan_head(frm, to, stroke)[0]
    half = stroke / 2
    edge, blends, interior_bad = 0, 0, []
    for y in range(baked.height):
        for x in range(baked.width):
            rx, ry = x - frm[0], y - frm[1]
            along = rx * ux + ry * uy
            if not (half + 3 <= along <= length - head - 3):
                continue
            dist = abs(rx * uy - ry * ux)
            px = baked.getpixel((x, y))
            if abs(dist - half) <= 1:
                edge += 1
                blends += not _equals(px, (255, 255, 255)) and not _equals(px, color)
            if dist <= half - 1.5 and not _equals(px, color):
                interior_bad.append(((x, y), px))
    assert edge > 0
    assert blends / edge >= 0.40
    assert interior_bad == []
    assert _changed_outside(original, baked, _plan_tile(frm, to, stroke, baked.size)) == []


@pytest.mark.parametrize("ac_id", ["AC-83.7"], ids=["AC-83.7"])
@pytest.mark.integration
def test_ac_83_7_arrow_tile_clipped_to_image(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-83.7"
    from avkit_core.domain.capture import ArrowAnnotation

    arrow = ArrowAnnotation(from_xy=(20, 60), to_xy=(119, 60), color="#FF0000", stroke_width=3)
    original, baked = _bake_arrow(tmp_path, (120, 120), arrow, "clip")
    tile = _plan_tile((20, 60), (119, 60), 3, (120, 120))
    assert tile[2] == 120
    assert _changed_outside(original, baked, tile) == []
    head = _plan_head((20, 60), (119, 60), 3)[0]
    assert (119 - round(head / 2), 60) == (111, 60)
    assert _equals(baked.getpixel((111, 60)), (255, 0, 0))
    far = ArrowAnnotation(from_xy=(300, 300), to_xy=(400, 300), color="#FF0000", stroke_width=3)
    far_original, far_baked = _bake_arrow(tmp_path, (120, 120), far, "far")
    assert far_baked.tobytes() == far_original.tobytes()


@pytest.mark.parametrize("ac_id", ["AC-83.8"], ids=["AC-83.8"])
@pytest.mark.unit
def test_ac_83_8_apply_arrow_supersamples_the_tile_only(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-83.8"
    from PIL import Image

    from avkit_core.domain.capture import ArrowAnnotation
    from avkit_infra.capture import adapter as capture_adapter

    source = (
        REPO_ROOT
        / "packages"
        / "infrastructure"
        / "src"
        / "avkit_infra"
        / "capture"
        / "adapter.py"
    ).read_text(encoding="utf-8")
    apply = source.split("def _apply_arrow", 1)[1].split("\n    def ", 1)[0]
    assert "draw.line" in apply
    assert "draw.polygon" in apply
    assert "Image.Resampling.LANCZOS" in apply
    assert "SUPERSAMPLE" in apply
    assert capture_adapter.SUPERSAMPLE == 4
    sizes: list[tuple[int, int]] = []
    real_new = Image.new

    def spy_new(mode: str, size: tuple[int, int], *args: object, **kwargs: object) -> Image.Image:
        sizes.append((int(size[0]), int(size[1])))
        return real_new(mode, size, *args, **kwargs)

    monkeypatch.setattr(capture_adapter.Image, "new", spy_new)
    arrow = ArrowAnnotation(from_xy=(20, 60), to_xy=(200, 60), color="#FF0000", stroke_width=12)
    _bake_arrow(tmp_path, (240, 120), arrow, "spy")
    full = (240 * capture_adapter.SUPERSAMPLE, 120 * capture_adapter.SUPERSAMPLE)
    assert [s for s in sizes if s[0] >= full[0] and s[1] >= full[1]] == []
    x0, y0, x1, y1 = _plan_tile((20, 60), (200, 60), 12, (240, 120))
    scale = capture_adapter.SUPERSAMPLE
    assert ((x1 - x0) * scale, (y1 - y0) * scale) in sizes


# ------------------------------------------------------------ MEU-90 region pass (Session 39)
# PIXELATE_QUANT and REGION_RECT (Session 39 plan), restated so the oracles do not take their
# arithmetic from the adapter under test.
PIXELATE_CASE_NAMES = {
    "pixelate-interior",
    "pixelate-clipped",
    "pixelate-negative-origin",
    "pixelate-big-block",
    "pixelate-empty",
    "pixelate-repeat-overlap",
}


def _ac90(n: int):
    label = f"AC-90.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _quant(total: int, n: int) -> int:
    return ((total + n // 2) * ((1 << 24) // n)) >> 24


def _clip(mark: dict, width: int, height: int) -> tuple[int, int, int, int] | None:
    x0, y0 = max(0, mark["x"]), max(0, mark["y"])
    x1 = min(width, mark["x"] + mark["width"])
    y1 = min(height, mark["y"] + mark["height"])
    return (x0, y0, x1, y1) if x0 < x1 and y0 < y1 else None


def _blocks(box: tuple[int, int, int, int], block: int) -> list[list[tuple[int, int]]]:
    x0, y0, x1, y1 = box
    return [
        [
            (x, y)
            for y in range(by, min(by + block, y1))
            for x in range(bx, min(bx + block, x1))
        ]
        for by in range(y0, y1, block)
        for bx in range(x0, x1, block)
    ]


def _ref_pixelate(pixels: list[int], width: int, height: int, mark: dict) -> list[int]:
    out = list(pixels)
    box = _clip(mark, width, height)
    if box is None:
        return out
    for cells in _blocks(box, mark["block_size"]):
        for c in range(3):
            total = sum(pixels[(y * width + x) * 3 + c] for x, y in cells)
            value = _quant(total, len(cells))
            for x, y in cells:
                out[(y * width + x) * 3 + c] = value
    return out


def _within_exact_mean(
    source: list[int], got: list[int], width: int, height: int, mark: dict
) -> bool:
    box = _clip(mark, width, height)
    for cells in _blocks(box, mark["block_size"]) if box else []:
        n = len(cells)
        for c in range(3):
            total = sum(source[(y * width + x) * 3 + c] for x, y in cells)
            exact = (2 * total + n) // (2 * n)
            x, y = cells[0]
            if abs(got[(y * width + x) * 3 + c] - exact) > 1:
                return False
    return True


def _blocks_uniform(pixels: list[int], width: int, height: int, mark: dict) -> bool:
    box = _clip(mark, width, height)
    for cells in _blocks(box, mark["block_size"]) if box else []:
        first = [pixels[(cells[0][1] * width + cells[0][0]) * 3 + c] for c in range(3)]
        for x, y in cells:
            if pixels[(y * width + x) * 3 : (y * width + x) * 3 + 3] != first:
                return False
    return True


def _outside_unchanged(
    source: list[int], got: list[int], width: int, height: int, marks: list[dict]
) -> bool:
    boxes = [box for box in (_clip(mark, width, height) for mark in marks) if box]
    for y in range(height):
        for x in range(width):
            if any(x0 <= x < x1 and y0 <= y < y1 for x0, y0, x1, y1 in boxes):
                continue
            i = (y * width + x) * 3
            if got[i : i + 3] != source[i : i + 3]:
                return False
    return True


def _bake_rgb(
    tmp_path: Path, name: str, width: int, height: int, pixels: list[int], marks: list
) -> list[int]:
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    source = tmp_path / f"{name}.png"
    Image.frombytes("RGB", (width, height), bytes(pixels)).save(source, format="PNG")
    out = tmp_path / f"{name}.baked.png"
    CaptureAdapter().bake(source, marks, out)
    with Image.open(out) as baked:
        return list(baked.convert("RGB").tobytes())


@_ac90(5)
@pytest.mark.unit
def test_ac_90_5_pixelate_bake_equals_pixelate_quant(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-90.5"
    from PIL import Image
    from tools import capture_bake_fixture as fixture

    from avkit_infra.capture.adapter import CaptureAdapter, apply_region_pass

    assert callable(apply_region_pass)
    cases = [case for case in fixture.region_cases() if case[0] in PIXELATE_CASE_NAMES]
    assert {case[0] for case in cases} == PIXELATE_CASE_NAMES
    for name, width, height, pixels, marks in cases:
        got = _bake_rgb(tmp_path, name, width, height, pixels, fixture.region_annotations(marks))
        expected = pixels
        for mark in marks:
            expected = _ref_pixelate(expected, width, height, mark)
        assert got == expected, name
        assert _outside_unchanged(pixels, got, width, height, marks), name
        assert _blocks_uniform(got, width, height, marks[-1]), name
        if len(marks) == 1:
            assert _within_exact_mean(pixels, got, width, height, marks[0]), name
        if name == "pixelate-empty":
            assert got == pixels
    name, width, height, pixels, marks = next(c for c in cases if c[0] == "pixelate-interior")
    for fmt, suffix in (("JPEG", ".jpg"), ("WEBP", ".webp")):
        source = tmp_path / f"lossy{suffix}"
        Image.frombytes("RGB", (width, height), bytes(pixels)).save(source, format=fmt)
        with Image.open(source) as opened:
            decoded = list(opened.convert("RGB").tobytes())
        out = tmp_path / f"lossy-{fmt}.png"
        CaptureAdapter().bake(source, fixture.region_annotations(marks), out)
        with Image.open(out) as baked:
            assert list(baked.convert("RGB").tobytes()) == _ref_pixelate(
                decoded, width, height, marks[0]
            ), fmt
    # Block 1 is the identity: it leaves the rectangle unchanged, and the uniform-block check
    # must be able to fail on that.
    assert _ref_pixelate(pixels, width, height, {**marks[0], "block_size": 1}) == pixels
    assert not _blocks_uniform(pixels, width, height, marks[0])


@_ac90(6)
@pytest.mark.unit
def test_ac_90_6_region_pass_runs_before_drawn_marks(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-90.6"
    import random

    from PIL import Image

    from avkit_core.domain.capture import ArrowAnnotation, PixelateAnnotation, RectAnnotation
    from avkit_infra.capture import adapter as adapter_mod
    from avkit_infra.capture.adapter import CaptureAdapter, apply_region_pass

    width, height = 40, 30
    rng = random.Random(90)
    pixels = [rng.randrange(256) for _ in range(width * height * 3)]
    pixelate = PixelateAnnotation(x=0, y=0, width=width, height=height, block_size=5)
    rect = RectAnnotation(x=5, y=5, width=20, height=12, color="#12AB34", stroke_width=2)
    stroke = [(x, y) for x in range(5, 26) for y in (5, 6, 16, 17)]
    stroke += [(x, y) for y in range(5, 18) for x in (5, 6, 24, 25)]

    after = _bake_rgb(tmp_path, "after", width, height, pixels, [pixelate, rect])
    before = _bake_rgb(tmp_path, "before", width, height, pixels, [rect, pixelate])
    for label, got in (("rect after", after), ("rect before", before)):
        for x, y in stroke:
            i = (y * width + x) * 3
            assert got[i : i + 3] == [0x12, 0xAB, 0x34], (label, x, y)
    assert after == before

    canvas = Image.frombytes("RGB", (width, height), bytes(pixels)).convert("RGBA")
    arrow = ArrowAnnotation(from_xy=(1, 1), to_xy=(30, 20), color="red", stroke_width=2)
    assert apply_region_pass(canvas.copy(), [rect, arrow]).tobytes() == canvas.tobytes()

    # A bake in plain list order (no region pass; the pixelate applied inline by _apply) puts
    # the rect under the mosaic when the rect is listed first.
    real_apply = CaptureAdapter._apply

    def plain_order_apply(self: object, image: object, annotation: object) -> object:
        if isinstance(annotation, PixelateAnnotation):
            return apply_region_pass(image, [annotation])
        return real_apply(self, image, annotation)  # type: ignore[arg-type]

    monkeypatch.setattr(adapter_mod, "apply_region_pass", lambda image, marks: image)
    monkeypatch.setattr(CaptureAdapter, "_apply", plain_order_apply)
    plain = _bake_rgb(tmp_path, "plain", width, height, pixels, [rect, pixelate])
    assert plain != before


# ------------------------------------------------------------ MEU-91 eraser (Session 39)
# ERASER_SAMPLE (Session 39 plan), restated so the oracle takes neither its ring nor its mode from
# the adapter under test.
ERASER_CASE_NAMES = {
    "eraser-stems",
    "eraser-tie",
    "eraser-clipped",
    "eraser-cover",
    "pixelate-then-eraser",
}


def _ac91(n: int):
    label = f"AC-91.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _inner_ring(box: tuple[int, int, int, int]) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    return [
        (x, y)
        for y in range(y0, y1)
        for x in range(x0, x1)
        if x in (x0, x1 - 1) or y in (y0, y1 - 1)
    ]


def _ring(box: tuple[int, int, int, int], width: int, height: int) -> list[tuple[int, int]]:
    """The outer ring (1 px outside, corners included, clipped to the image), else the inner."""
    x0, y0, x1, y1 = box
    points = [(x, y) for x in range(x0 - 1, x1 + 1) for y in (y0 - 1, y1)]
    points += [(x, y) for y in range(y0, y1) for x in (x0 - 1, x1)]
    outer = [(x, y) for x, y in points if 0 <= x < width and 0 <= y < height]
    return outer or _inner_ring(box)


def _ring_mode(pixels: list[int], width: int, ring: list[tuple[int, int]]) -> tuple[int, ...]:
    counts: dict[tuple[int, ...], int] = {}
    for x, y in ring:
        rgb = tuple(pixels[(y * width + x) * 3 : (y * width + x) * 3 + 3])
        counts[rgb] = counts.get(rgb, 0) + 1
    top = max(counts.values())
    return min(
        (rgb for rgb, count in counts.items() if count == top),
        key=lambda rgb: (rgb[0] << 16) | (rgb[1] << 8) | rgb[2],
    )


def _ref_eraser(pixels: list[int], width: int, height: int, mark: dict) -> list[int]:
    out = list(pixels)
    box = _clip(mark, width, height)
    if box is None:
        return out
    fill = list(_ring_mode(pixels, width, _ring(box, width, height)))
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            out[(y * width + x) * 3 : (y * width + x) * 3 + 3] = fill
    return out


def _ref_region(pixels: list[int], width: int, height: int, marks: list[dict]) -> list[int]:
    for mark in marks:
        ref = _ref_eraser if mark["type"] == "eraser" else _ref_pixelate
        pixels = ref(pixels, width, height, mark)
    return pixels


def _rect_colours(
    pixels: list[int], width: int, box: tuple[int, int, int, int]
) -> set[tuple[int, ...]]:
    x0, y0, x1, y1 = box
    return {
        tuple(pixels[(y * width + x) * 3 : (y * width + x) * 3 + 3])
        for y in range(y0, y1)
        for x in range(x0, x1)
    }


@_ac91(5)
@pytest.mark.unit
def test_ac_91_5_eraser_fill_is_the_ring_mode(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-91.5"
    from PIL import Image
    from tools import capture_bake_fixture as fixture

    from avkit_infra.capture.adapter import CaptureAdapter, eraser_fill

    assert callable(eraser_fill)
    cases = [case for case in fixture.region_cases() if case[0] in ERASER_CASE_NAMES]
    assert {case[0] for case in cases} == ERASER_CASE_NAMES
    fills: dict[str, tuple[int, ...]] = {}
    for name, width, height, pixels, marks in cases:
        got = _bake_rgb(tmp_path, name, width, height, pixels, fixture.region_annotations(marks))
        assert got == _ref_region(pixels, width, height, marks), name
        assert _outside_unchanged(pixels, got, width, height, marks), name
        box = _clip(marks[-1], width, height)
        assert box is not None, name
        colours = _rect_colours(got, width, box)
        assert len(colours) == 1, name
        fills[name] = colours.pop()
    assert fills["eraser-stems"] == fixture.REGION_BG
    assert fills["eraser-tie"] == (0, 0, 0)
    assert fills["eraser-cover"] == (1, 2, 3)
    # Negative: the ring mean of eraser-stems is not REGION_BG, so only the mode passes.
    name, width, height, pixels, marks = next(c for c in cases if c[0] == "eraser-stems")
    box = _clip(marks[0], width, height)
    ring = _ring(box, width, height)
    mean = tuple(
        round(sum(pixels[(y * width + x) * 3 + c] for x, y in ring) / len(ring)) for c in range(3)
    )
    assert mean != fixture.REGION_BG
    for fmt, suffix in (("JPEG", ".jpg"), ("WEBP", ".webp")):
        source = tmp_path / f"eraser-lossy{suffix}"
        Image.frombytes("RGB", (width, height), bytes(pixels)).save(source, format=fmt)
        with Image.open(source) as opened:
            decoded = list(opened.convert("RGB").tobytes())
        out = tmp_path / f"eraser-lossy-{fmt}.png"
        CaptureAdapter().bake(source, fixture.region_annotations(marks), out)
        with Image.open(out) as baked:
            got = list(baked.convert("RGB").tobytes())
        assert _rect_colours(got, width, box) == {_ring_mode(decoded, width, ring)}, fmt
        assert got == _ref_eraser(decoded, width, height, marks[0]), fmt


@_ac91(6)
@pytest.mark.unit
def test_ac_91_6_eraser_samples_the_pixelated_ring_and_text_stays_crisp(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-91.6"
    from tools import capture_bake_fixture as fixture

    from avkit_core.domain.capture import EraserAnnotation, TextAnnotation

    name, width, height, pixels, marks = next(
        case for case in fixture.region_cases() if case[0] == "pixelate-then-eraser"
    )
    pixelate, eraser = marks
    got = _bake_rgb(tmp_path, name, width, height, pixels, fixture.region_annotations(marks))
    mosaic = _ref_pixelate(pixels, width, height, pixelate)
    box = _clip(eraser, width, height)
    assert box is not None
    ring = _ring(box, width, height)
    assert _rect_colours(got, width, box) == {_ring_mode(mosaic, width, ring)}
    # The original ring (before the pixelate) has another mode, so the order is visible.
    assert _ring_mode(pixels, width, ring) != _ring_mode(mosaic, width, ring)
    reversed_marks = fixture.region_annotations([eraser, pixelate])
    assert _bake_rgb(tmp_path, "reversed", width, height, pixels, reversed_marks) != got

    # A text mark is drawn after the region pass in either list position, so it stays crisp.
    flat = [200, 210, 220] * (60 * 40)
    erase = EraserAnnotation(x=5, y=5, width=50, height=30)
    text = TextAnnotation(x=10, y=10, text="Hi", color="black", font_size=16, bg_color=None)
    after = _bake_rgb(tmp_path, "text-after", 60, 40, flat, [erase, text])
    before = _bake_rgb(tmp_path, "text-before", 60, 40, flat, [text, erase])
    assert after == before
    dark = [
        (x, y)
        for y in range(5, 35)
        for x in range(5, 55)
        if max(after[(y * 60 + x) * 3 : (y * 60 + x) * 3 + 3]) <= 60
    ]
    assert dark


# MEU-128 capture-region-view (Session 58): the adapter's view. The tests build ViewFrame
# directly and their images with Pillow under tmp_path.
VIEW_SIZE = (64, 48)


def _distinct_rgb(size: tuple[int, int] = VIEW_SIZE) -> Any:
    from PIL import Image

    width, height = size
    image = Image.new("RGB", size)
    image.putdata(
        [
            ((x * 4) % 256, (y * 5) % 256, (x * 3 + y * 7) % 256)
            for y in range(height)
            for x in range(width)
        ]
    )
    return image


def _view_frame(
    region: tuple[int, int, int, int],
    returned: tuple[int, int],
    *,
    source: tuple[int, int] = VIEW_SIZE,
) -> Any:
    from avkit_core.domain.capture import ViewFrame

    x, y, width, height = region
    return ViewFrame(
        source_width=source[0],
        source_height=source[1],
        x=x,
        y=y,
        width=width,
        height=height,
        returned_width=returned[0],
        returned_height=returned[1],
        scale=returned[0] / width,
        clamped=False,
    )


def _decode(data: bytes) -> Any:
    import io

    from PIL import Image

    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def _folder_state(folder: Path) -> list[tuple[str, int, int]]:
    return sorted((p.name, p.stat().st_size, p.stat().st_mtime_ns) for p in folder.iterdir())


@pytest.mark.parametrize("ac_id", ["AC-128.6"], ids=["AC-128.6"])
@pytest.mark.unit
def test_ac_128_6_view_crops_exact_pixels(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.6"
    from avkit_infra.capture.adapter import CaptureAdapter

    path = tmp_path / "shot.png"
    source = _distinct_rgb()
    source.save(path)
    got = _decode(CaptureAdapter().view(path, _view_frame((10, 8, 20, 16), (20, 16))))
    assert got.size == (20, 16)
    want = source.crop((10, 8, 30, 24))
    assert got.convert("RGB").tobytes() == want.tobytes()


@pytest.mark.parametrize("ac_id", ["AC-128.7"], ids=["AC-128.7"])
@pytest.mark.unit
def test_ac_128_7_view_resizes_with_lanczos(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.7"
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter()
    frame = _view_frame((10, 8, 20, 16), (80, 64))
    box = (10, 8, 30, 24)

    rgb_path = tmp_path / "rgb.png"
    rgb = _distinct_rgb()
    rgb.save(rgb_path)
    got = _decode(adapter.view(rgb_path, frame))
    want = rgb.crop(box).resize((80, 64), Image.LANCZOS)
    assert got.size == (80, 64)
    assert got.tobytes() == want.tobytes()

    palette_path = tmp_path / "palette.png"
    palette = rgb.quantize(colors=64)
    palette.info["transparency"] = 0
    palette.save(palette_path, transparency=0)
    with Image.open(palette_path) as opened:
        assert opened.mode == "P"
        expected = opened.convert("RGBA").crop(box).resize((80, 64), Image.LANCZOS)
    got_palette = _decode(adapter.view(palette_path, frame))
    assert got_palette.mode == "RGBA"
    assert got_palette.tobytes() == expected.tobytes()

    rgba_path = tmp_path / "rgba.png"
    rgba = rgb.convert("RGBA")
    rgba.putalpha(200)
    rgba.save(rgba_path)
    got_rgba = _decode(adapter.view(rgba_path, frame))
    assert got_rgba.mode == "RGBA"
    assert got_rgba.size == (80, 64)


@pytest.mark.parametrize("ac_id", ["AC-128.8"], ids=["AC-128.8"])
@pytest.mark.unit
def test_ac_128_8_view_keeps_the_format(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.8"
    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter()
    frame = _view_frame((10, 8, 20, 16), (40, 32))
    jpeg_path = tmp_path / "photo.jpg"
    _distinct_rgb().save(jpeg_path, format="JPEG", quality=90)
    jpeg = _decode(adapter.view(jpeg_path, frame))
    assert (jpeg.format, jpeg.mode, jpeg.size) == ("JPEG", "RGB", (40, 32))
    webp_path = tmp_path / "page.webp"
    _distinct_rgb().save(webp_path, format="WEBP", quality=90)
    webp = _decode(adapter.view(webp_path, frame))
    assert (webp.format, webp.size) == ("WEBP", (40, 32))


@pytest.mark.parametrize("ac_id", ["AC-128.9"], ids=["AC-128.9"])
@pytest.mark.unit
def test_ac_128_9_view_writes_no_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.9"
    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter()
    rgb = _distinct_rgb()
    rgb.save(tmp_path / "shot.png")
    rgb.quantize(colors=64).save(tmp_path / "palette.png", transparency=0)
    rgb.convert("RGBA").save(tmp_path / "rgba.png")
    rgb.save(tmp_path / "photo.jpg", format="JPEG", quality=90)
    rgb.save(tmp_path / "page.webp", format="WEBP", quality=90)
    before = _folder_state(tmp_path)
    frames = (
        _view_frame((0, 0, 64, 48), (64, 48)),
        _view_frame((10, 8, 20, 16), (20, 16)),
        _view_frame((10, 8, 20, 16), (80, 64)),
        _view_frame((0, 0, 64, 48), (32, 24)),
    )
    for name in ("shot.png", "palette.png", "rgba.png", "photo.jpg", "page.webp"):
        for frame in frames:
            assert adapter.view(tmp_path / name, frame)
    assert _folder_state(tmp_path) == before


@pytest.mark.parametrize("ac_id", ["AC-128.10"], ids=["AC-128.10"])
@pytest.mark.unit
def test_ac_128_10_view_refuses_a_changed_or_bad_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.10"
    from avkit_core.domain.errors import ConflictError, InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter()
    folder = tmp_path / "private-folder"
    folder.mkdir()
    path = folder / "secret-shot.png"
    _distinct_rgb().save(path)
    stale = _view_frame((10, 8, 20, 16), (20, 16), source=(100, 80))
    with pytest.raises(ConflictError) as changed:
        adapter.view(path, stale)
    text = str(changed.value)
    for part in (str(path), str(folder), "private-folder", "secret-shot", tmp_path.name):
        assert part not in text
    fake = folder / "notes.png"
    fake.write_text("not an image", encoding="utf-8")
    with pytest.raises(InboxPathError) as unopened:
        adapter.view(fake, _view_frame((0, 0, 64, 48), (64, 48)))
    assert str(unopened.value) == "the image could not be opened"


def _broken_chunk_png() -> bytes:
    """A PNG whose IDAT is cut and followed by an invalid chunk: Pillow raises SyntaxError."""
    import io
    import struct
    import zlib

    buffer = io.BytesIO()
    _distinct_rgb().save(buffer, format="PNG")
    data = buffer.getvalue()
    at = data.index(b"IDAT") - 4
    (length,) = struct.unpack(">I", data[at : at + 4])
    body = data[at + 8 : at + 8 + length][:4]
    crc = struct.pack(">I", zlib.crc32(b"IDAT" + body))
    idat = struct.pack(">I", len(body)) + b"IDAT" + body + crc
    bad = struct.pack(">I", 0) + b"BAD!" + struct.pack(">I", zlib.crc32(b"BAD!"))
    return data[:at] + idat + bad


@pytest.mark.parametrize("fault", ["broken-chunk", "second-read"])
@pytest.mark.parametrize("ac_id", ["AC-128.10"], ids=["AC-128.10"])
@pytest.mark.unit
def test_ac_128_10_view_maps_decode_and_read_faults(
    ac_id: str, fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-128.10"
    from avkit_core.domain.errors import InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter()
    folder = tmp_path / "private-folder"
    folder.mkdir()
    path = folder / "secret-shot.png"
    if fault == "broken-chunk":
        path.write_bytes(_broken_chunk_png())
        frame = _view_frame((10, 8, 20, 16), (20, 16))
    else:
        _distinct_rgb().save(path)
        frame = _view_frame((0, 0, *VIEW_SIZE), VIEW_SIZE)
        real_read = Path.read_bytes

        def broken_read(self: Path) -> bytes:
            if self == path:
                raise PermissionError(13, "Permission denied", str(self))
            return real_read(self)

        monkeypatch.setattr(Path, "read_bytes", broken_read)
    with pytest.raises(InboxPathError) as refused:
        adapter.view(path, frame)
    assert str(refused.value) == "the image could not be opened"

# MEU-130 capture-crop-copy (Session 59): the adapter's crop. Every image is built with Pillow
# under tmp_path, and the box is always (10, 8, 20, 16) on a 64x48 source.
CROP_BOX = (10, 8, 20, 16)
CROP_PIL_BOX = (10, 8, 30, 24)
CROP_CHANGED = "the image file changed since the captures were listed; list them again and retry"
CROP_MODE_CASES = ("1", "L", "LA", "P", "RGB", "RGBA", "I;16", "jpg", "webp")


def _crop_source(case: str, folder: Path) -> Path:
    """A 64x48 source for AC-130.9 in the mode or format `case` names."""
    from PIL import Image

    base = _distinct_rgb()
    alpha = Image.new("L", VIEW_SIZE)
    width, height = VIEW_SIZE
    alpha.putdata([(x * 3 + y * 2) % 256 for y in range(height) for x in range(width)])
    if case == "jpg":
        path = folder / "source.jpg"
        base.save(path, format="JPEG", quality=90)
        return path
    if case == "webp":
        path = folder / "source.webp"
        rgba = base.convert("RGBA")
        rgba.putalpha(alpha)
        rgba.save(path, format="WEBP", quality=90)
        return path
    path = folder / "source.png"
    if case == "P":
        base.quantize(16).save(path, format="PNG", transparency=3)
    elif case == "I;16":
        deep = Image.new("I;16", VIEW_SIZE)
        deep.putdata([x * 1000 + y for y in range(height) for x in range(width)])
        deep.save(path, format="PNG")
    elif case in ("LA", "RGBA"):
        image = base.convert(case)
        image.putalpha(alpha)
        image.save(path, format="PNG")
    else:
        base.convert(case).save(path, format="PNG")
    return path


@pytest.mark.parametrize("ac_id", ["AC-130.8"], ids=["AC-130.8"])
@pytest.mark.unit
def test_ac_130_8_crop_writes_the_box_exactly(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.8"
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    source = tmp_path / "source.png"
    image = _distinct_rgb()
    image.save(source)
    out = tmp_path / "crop.png"
    probe = CaptureAdapter().crop(source, CROP_BOX, VIEW_SIZE, out)
    assert (probe.width, probe.height) == (20, 16)
    assert out.is_file()
    assert probe.file_size == out.stat().st_size
    with Image.open(out) as cropped:
        assert cropped.format == "PNG"
        cropped.load()
        assert (cropped.mode, cropped.size) == ("RGB", (20, 16))
        assert cropped.tobytes() == image.crop(CROP_PIL_BOX).tobytes()
        for x, y in ((0, 0), (19, 0), (0, 15), (19, 15), (10, 8)):
            assert cropped.getpixel((x, y)) == image.getpixel((10 + x, 8 + y)), (x, y)


@pytest.mark.parametrize(
    "case", CROP_MODE_CASES, ids=[case.replace(";", "") for case in CROP_MODE_CASES]
)
@pytest.mark.parametrize("ac_id", ["AC-130.9"], ids=["AC-130.9"])
@pytest.mark.unit
def test_ac_130_9_crop_keeps_the_mode(ac_id: str, case: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.9"
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    source = _crop_source(case, tmp_path)
    with Image.open(source) as opened:
        opened.load()
        decoded = opened.copy()
    want_mode = {"jpg": "RGB", "webp": "RGBA"}.get(case, case)
    assert decoded.mode == want_mode, (case, decoded.mode)
    out = tmp_path / "crop.png"
    CaptureAdapter().crop(source, CROP_BOX, VIEW_SIZE, out)
    assert out.is_file()
    with Image.open(out) as cropped:
        assert cropped.format == "PNG"
        cropped.load()
        assert (cropped.mode, cropped.size) == (want_mode, (20, 16))
        want = decoded.crop(CROP_PIL_BOX)
        assert cropped.tobytes() == want.tobytes()
        if case == "P":
            assert cropped.getpalette() == decoded.getpalette()
            assert cropped.info.get("transparency") == 3


@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])
@pytest.mark.unit
def test_ac_130_10_crop_keeps_icc_and_drops_the_rest(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.10"
    from PIL import Image, ImageCms, PngImagePlugin

    from avkit_infra.capture.adapter import CaptureAdapter

    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    exif = Image.Exif()
    exif[0x010F] = "private maker"
    text = PngImagePlugin.PngInfo()
    text.add_text("Comment", "private comment")
    source = tmp_path / "source.png"
    _distinct_rgb().save(source, format="PNG", icc_profile=icc, exif=exif, pnginfo=text)
    with Image.open(source) as opened:
        assert opened.info.get("icc_profile") == icc
        assert "exif" in opened.info
        assert opened.text == {"Comment": "private comment"}  # type: ignore[attr-defined]
    out = tmp_path / "crop.png"
    CaptureAdapter().crop(source, CROP_BOX, VIEW_SIZE, out)
    assert out.is_file()
    with Image.open(out) as cropped:
        cropped.load()
        assert cropped.info.get("icc_profile") == icc
        assert "exif" not in cropped.info
        assert dict(cropped.getexif()) == {}
        assert cropped.text == {}  # type: ignore[attr-defined]
        assert "Comment" not in cropped.info


def _s15(value: float) -> bytes:
    import struct

    return struct.pack(">i", round(value * 65536))


def _cmyk_icc() -> bytes:
    """A minimal ICC v2 CMYK profile built from bytes: Lab PCS and a 2-point lut16 A2B0.

    Each CLUT corner is the plain RGB of that ink mix, so it differs from Pillow's plain
    CMYK conversion in the mid-tones. The test reads no system profile.
    """
    import struct

    from PIL import Image, ImageCms

    to_lab = ImageCms.buildTransform(
        ImageCms.createProfile("sRGB"), ImageCms.createProfile("LAB"), "RGB", "LAB"
    )
    corners = [
        tuple(round(255 * (1 - ink) * (1 - k)) for ink in (c, m, y))
        for c in (0, 1)
        for m in (0, 1)
        for y in (0, 1)
        for k in (0, 1)
    ]
    strip = Image.new("RGB", (len(corners), 1))
    strip.putdata(corners)
    raw = ImageCms.applyTransform(strip, to_lab)
    assert raw is not None
    clut = bytes(
        byte for value in raw.tobytes() for byte in struct.pack(">H", value * 256)
    )
    ramp = struct.pack(">2H", 0, 0xFFFF)
    lut = (
        b"mft2"
        + bytes(4)
        + bytes([4, 3, 2, 0])
        + b"".join(_s15(v) for v in (1, 0, 0, 0, 1, 0, 0, 0, 1))
        + struct.pack(">2H", 2, 2)
        + ramp * 4
        + clut
        + ramp * 3
    )
    size = 128 + 4 + 12 + len(lut)
    header = (
        struct.pack(">I", size)
        + bytes(4)
        + struct.pack(">I", 0x02100000)
        + b"prtrCMYKLab "
        + bytes(12)
        + b"acsp"
        + bytes(28)
        + _s15(0.9642)
        + _s15(1.0)
        + _s15(0.8249)
        + bytes(48)
    )
    assert len(header) == 128
    return header + struct.pack(">I", 1) + b"A2B0" + struct.pack(">2I", 144, len(lut)) + lut


def _cmyk_jpeg(path: Path, icc: bytes | None) -> None:
    from PIL import Image

    image = Image.new("CMYK", (64, 48))
    image.putdata(
        [
            ((x * 4) % 256, (y * 5) % 256, ((x + y) * 3) % 256, 40)
            for y in range(48)
            for x in range(64)
        ]
    )
    extra = {} if icc is None else {"icc_profile": icc}
    image.save(path, format="JPEG", quality=95, **extra)


@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])
@pytest.mark.unit
def test_ac_130_10_cmyk_icc_to_srgb(ac_id: str, tmp_path: Path) -> None:
    """Round 1 F1, D-506 A: a CMYK source converts through its profile; the crop is sRGB."""
    assert ac_id == "AC-130.10"
    import io

    from PIL import Image, ImageCms

    from avkit_infra.capture.adapter import CaptureAdapter

    icc = _cmyk_icc()
    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB"))
    source = tmp_path / "source.jpg"
    _cmyk_jpeg(source, icc)
    with Image.open(source) as opened:
        opened.load()
        assert (opened.mode, opened.info.get("icc_profile")) == ("CMYK", icc)
        part = opened.crop(CROP_PIL_BOX)
    managed = ImageCms.profileToProfile(
        part, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb, outputMode="RGB"
    )
    assert managed is not None
    assert managed.tobytes() != part.convert("RGB").tobytes()
    out = tmp_path / "crop.png"
    CaptureAdapter().crop(source, CROP_BOX, VIEW_SIZE, out)
    with Image.open(out) as cropped:
        cropped.load()
        assert (cropped.mode, cropped.size) == ("RGB", (20, 16))
        assert cropped.info.get("icc_profile") == srgb.tobytes()
        assert cropped.tobytes() == managed.tobytes()


@pytest.mark.parametrize("icc", [None, b"not a profile"], ids=["none", "junk"])
@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])
@pytest.mark.unit
def test_ac_130_10_cmyk_plain_fallback(ac_id: str, icc: bytes | None, tmp_path: Path) -> None:
    """D-506 A: with no profile, or one that builds no transform, plain RGB and no profile."""
    assert ac_id == "AC-130.10"
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    source = tmp_path / "source.jpg"
    _cmyk_jpeg(source, icc)
    with Image.open(source) as opened:
        opened.load()
        assert opened.mode == "CMYK"
        assert opened.info.get("icc_profile") == icc
        want = opened.crop(CROP_PIL_BOX).convert("RGB")
    out = tmp_path / "crop.png"
    CaptureAdapter().crop(source, CROP_BOX, VIEW_SIZE, out)
    with Image.open(out) as cropped:
        cropped.load()
        assert cropped.mode == "RGB"
        assert "icc_profile" not in cropped.info
        assert cropped.tobytes() == want.tobytes()


@pytest.mark.parametrize("ac_id", ["AC-130.11"], ids=["AC-130.11"])
@pytest.mark.unit
def test_ac_130_11_crop_refusals_name_no_path(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.11"
    from avkit_core.domain.errors import ConflictError, InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter

    adapter = CaptureAdapter()
    folder = tmp_path / "private-folder"
    folder.mkdir()
    source = folder / "secret-shot.png"
    _distinct_rgb().save(source)
    out = folder / "secret-crop.png"
    with pytest.raises(ConflictError) as changed:
        adapter.crop(source, CROP_BOX, (100, 80), out)
    assert str(changed.value) == CROP_CHANGED
    for part in (str(tmp_path), folder.name, source.name, out.name):
        assert part not in str(changed.value), part
    assert not out.exists()
    text = folder / "secret-text.png"
    text.write_text("not an image at all", encoding="utf-8")
    with pytest.raises(InboxPathError) as unopened:
        adapter.crop(text, CROP_BOX, VIEW_SIZE, out)
    assert str(unopened.value) == "the image could not be opened"
    assert not out.exists()
