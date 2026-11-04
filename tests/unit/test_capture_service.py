"""MEU-36 CaptureService tests. Imports stay inside tests so collection cannot ERROR."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pytest

SCAN_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
REQUEST_TTL_S = 120
ANNOTATED_SUFFIX = ".annotated.png"
SIDECAR_SUFFIX = ".ann.json"
SIDECAR_VERSION = 1
ANNOTATION_CLAMP_MIN = 0
# TA-4 (Session 30, MEU-67): + flatten_backup, backup_dir, annotated_format.
CAPTURE_KEYS = (
    "inbox_dir",
    "hotkey",
    "copy_to_clipboard",
    "close_to_tray",
    "flatten_backup",
    "backup_dir",
    "annotated_format",
)
CAPTURE_DEFAULTS = {
    "inbox_dir": "~/Pictures/av-kit",
    "hotkey": "F2",
    "copy_to_clipboard": False,
    "close_to_tray": True,
    "flatten_backup": True,
    "backup_dir": "",
    "annotated_format": "png",
}


class FakeCapturePort:
    def __init__(self) -> None:
        self.fullscreen_paths: list[Path] = []
        self.region_calls: list[object] = []
        self.bakes: list[object] = []
        self.formats: list[str] = []
        self.ensured: list[Path] = []
        self.width = 32
        self.height = 32

    def capture_fullscreen(self, output_path: Path) -> object:
        from avkit_core.domain.capture import ImageProbe

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"png-bytes")
        self.fullscreen_paths.append(output_path)
        return ImageProbe(
            width=self.width,
            height=self.height,
            file_size=output_path.stat().st_size,
        )

    def capture_region(self, output_path: Path, bbox: object) -> object:
        from avkit_core.domain.capture import ImageProbe

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"png-bytes")
        self.region_calls.append(bbox)
        return ImageProbe(
            width=self.width,
            height=self.height,
            file_size=output_path.stat().st_size,
        )

    def probe(self, path: Path) -> object:
        from avkit_core.domain.capture import ImageProbe
        from avkit_core.domain.errors import InboxPathError

        if not path.is_file():
            raise InboxPathError(f"{path} is not a file")
        return ImageProbe(width=self.width, height=self.height, file_size=path.stat().st_size)

    def ensure_dir(self, path: Path) -> None:
        # FIXTURE_REPAIRS (h) (Session 30, A-5): the port creates folders, not the service.
        path.mkdir(parents=True, exist_ok=True)
        self.ensured.append(path)

    def bake(
        self,
        original_path: Path,
        annotations: object,
        output_path: Path,
        output_format: str = "png",
    ) -> object:
        from avkit_core.domain.capture import ImageProbe

        # FIXTURE_REPAIRS (f) (Session 30): BAKE_PORT's output_format, recorded for inspection.
        self.formats.append(output_format)
        self.bakes.append(list(annotations))  # type: ignore[arg-type]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"baked")
        return ImageProbe(
            width=self.width,
            height=self.height,
            file_size=output_path.stat().st_size,
        )


def _stack(tmp_path: Path, clock: object | None = None):
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    port = FakeCapturePort()
    frozen = clock or (lambda: datetime(2026, 8, 27, 12, 0, 0, tzinfo=UTC))
    service = CaptureService(
        factory,
        capture=port,
        annotate=port,
        settings=settings,
        clock=frozen,
    )
    return service, uow, port, inbox


def _write_inbox_file(inbox: Path, name: str, payload: bytes = b"png-bytes") -> Path:
    path = (inbox / name).resolve()
    path.write_bytes(payload)
    return path


@pytest.mark.parametrize("ac_id", ["AC-36.1"], ids=["AC-36.1"])
@pytest.mark.unit
def test_ac_36_1_scan_extensions_non_recursive(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.1"
    from avkit_core.domain.enums import CaptureSource

    service, uow, _port, inbox = _stack(tmp_path)
    png = _write_inbox_file(inbox, "a.png")
    _write_inbox_file(inbox, "b.gif")
    nested = inbox / "sub"
    nested.mkdir()
    (nested / "nested.png").write_bytes(b"png-bytes")
    shots = service.scan_inbox()
    paths = {shot.original_path for shot in shots}
    assert png in paths
    assert all(shot.source is CaptureSource.Scan for shot in shots)
    assert all(shot.original_path.suffix.lower() in SCAN_EXTENSIONS for shot in shots)
    assert not any(p.name == "b.gif" for p in paths)
    assert not any("nested.png" in str(p) for p in paths)
    assert len(uow.capture_shots.list()) == 1


@pytest.mark.parametrize("ac_id", ["AC-36.2"], ids=["AC-36.2"])
@pytest.mark.unit
def test_ac_36_2_scan_deletes_vanished_originals(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.2"
    service, uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "gone.png")
    service.scan_inbox()
    assert uow.capture_shots.get_by_path(path) is not None
    path.unlink()
    service.scan_inbox()
    assert uow.capture_shots.get_by_path(path) is None
    assert uow.capture_shots.list() == []


@pytest.mark.parametrize("ac_id", ["AC-36.3"], ids=["AC-36.3"])
@pytest.mark.unit
def test_ac_36_3_list_shots_newest_then_filename(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.3"
    from dataclasses import replace

    service, uow, _port, inbox = _stack(tmp_path)
    older = _write_inbox_file(inbox, "z-old.png")
    newer = _write_inbox_file(inbox, "a-new.png")
    same_a = _write_inbox_file(inbox, "m-a.png")
    same_b = _write_inbox_file(inbox, "m-b.png")
    service.scan_inbox()
    t0 = datetime(2026, 8, 1, tzinfo=UTC)
    t1 = datetime(2026, 8, 2, tzinfo=UTC)
    t2 = datetime(2026, 8, 3, tzinfo=UTC)
    for shot in list(uow.capture_shots.list()):
        if shot.original_path == older:
            uow.capture_shots.save(replace(shot, created_at=t0, updated_at=t0))
        elif shot.original_path == newer:
            uow.capture_shots.save(replace(shot, created_at=t2, updated_at=t2))
        else:
            uow.capture_shots.save(replace(shot, created_at=t1, updated_at=t1))
    listed = service.list_shots()
    names = [shot.display_name for shot in listed]
    assert names[0] == newer.name
    assert names[-1] == older.name
    mid = [name for name in names if name in {same_a.name, same_b.name}]
    assert mid == [same_a.name, same_b.name]


@pytest.mark.parametrize("ac_id", ["AC-36.4"], ids=["AC-36.4"])
@pytest.mark.unit
def test_ac_36_4_register_inbox_and_idempotent(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.4"
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.domain.errors import InboxPathError

    service, uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "ok.png")
    first = service.register_shot(path, CaptureSource.Gui)
    second = service.register_shot(path, CaptureSource.Gui)
    assert first.id == second.id
    assert len(uow.capture_shots.list()) == 1
    with pytest.raises(InboxPathError):
        service.register_shot(Path("relative.png"), CaptureSource.Gui)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"png-bytes")
    sneaky = inbox / ".." / outside.name
    with pytest.raises(InboxPathError):
        service.register_shot(sneaky, CaptureSource.Gui)


@pytest.mark.parametrize("ac_id", ["AC-36.5"], ids=["AC-36.5"])
@pytest.mark.unit
def test_ac_36_5_timestamp_local_collision_and_sources(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.5"
    from avkit_core.domain.capture import BBox
    from avkit_core.domain.enums import CaptureSource

    frozen = datetime(2026, 8, 27, 15, 4, 5)
    service, _uow, port, inbox = _stack(tmp_path, clock=lambda: frozen)
    stem = frozen.strftime(TIMESTAMP_FORMAT)
    taken = inbox / f"{stem}.png"
    taken.write_bytes(b"taken")
    shot = service.capture_fullscreen()
    assert shot.source is CaptureSource.McpFullscreen
    assert shot.original_path.name == f"{stem}_2.png"
    assert shot.original_path.parent == inbox.resolve()
    region = service.capture_region(BBox(x=0, y=0, width=16, height=16))
    assert region.source is CaptureSource.McpRegion
    assert region.original_path.name == f"{stem}_3.png"
    assert port.fullscreen_paths
    utc_name = datetime(2026, 8, 27, 15, 4, 5, tzinfo=UTC).strftime(TIMESTAMP_FORMAT)
    assert shot.original_path.name != f"{utc_name}.png"


@pytest.mark.parametrize("ac_id", ["AC-36.6"], ids=["AC-36.6"])
@pytest.mark.unit
def test_ac_36_6_request_interactive_ttl_and_conflict(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.6"
    from avkit_core.domain.enums import CaptureRequestStatus
    from avkit_core.domain.errors import CaptureRequestConflictError

    now = datetime(2026, 8, 27, 12, 0, 0, tzinfo=UTC)
    service, uow, _port, _inbox = _stack(tmp_path, clock=lambda: now)
    first = service.request_interactive()
    assert first.status is CaptureRequestStatus.Pending
    assert first.expires_at == now + timedelta(seconds=REQUEST_TTL_S)
    with pytest.raises(CaptureRequestConflictError):
        service.request_interactive()
    assert len(uow.capture_requests.rows) == 1


@pytest.mark.parametrize("ac_id", ["AC-36.7"], ids=["AC-36.7"])
@pytest.mark.unit
def test_ac_36_7_expire_stale_from_list_and_get(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.7"
    from dataclasses import replace

    from avkit_core.domain.enums import CaptureRequestStatus

    now = datetime(2026, 8, 27, 12, 0, 0, tzinfo=UTC)
    service, uow, _port, _inbox = _stack(tmp_path, clock=lambda: now)
    req = service.request_interactive()
    uow.capture_requests.save(
        replace(req, expires_at=now - timedelta(seconds=1))
    )
    service.list_shots()
    loaded = uow.capture_requests.get(req.id)
    assert loaded is not None
    assert loaded.status is CaptureRequestStatus.Expired
    again = service.request_interactive()
    uow.capture_requests.save(
        replace(again, expires_at=now - timedelta(seconds=1))
    )
    with pytest.raises(Exception):
        service.get_shot(str(uuid4()))
    stale = uow.capture_requests.get(again.id)
    assert stale is not None
    assert stale.status is CaptureRequestStatus.Expired


@pytest.mark.parametrize("ac_id", ["AC-36.8"], ids=["AC-36.8"])
@pytest.mark.unit
def test_ac_36_8_complete_and_cancel_request(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.8"
    from avkit_core.domain.enums import CaptureRequestStatus
    from avkit_core.domain.errors import ValidationError

    service, uow, _port, inbox = _stack(tmp_path)
    pending = service.request_interactive()
    path = _write_inbox_file(inbox, "done.png")
    completed = service.complete_request(pending.id, path)
    assert completed.status is CaptureRequestStatus.Completed
    assert completed.shot_id is not None
    assert uow.capture_shots.get(completed.shot_id) is not None
    other = service.request_interactive()
    cancelled = service.cancel_request(other.id)
    assert cancelled.status is CaptureRequestStatus.Cancelled
    assert cancelled.shot_id is None
    third = service.request_interactive()
    with pytest.raises((TypeError, ValidationError)):
        service.complete_request(third.id)  # type: ignore[misc]


@pytest.mark.parametrize("ac_id", ["AC-36.9"], ids=["AC-36.9"])
@pytest.mark.unit
def test_ac_36_9_annotate_sidecar_and_empty_clears(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.9"
    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.services.capture import parse_sidecar_document

    service, _uow, port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "draw.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    annotated = service.annotate_and_save(
        shot.id,
        [RectAnnotation(x=1, y=2, width=4, height=4, color="red", stroke_width=1)],
    )
    assert annotated.annotated_path is not None
    assert annotated.sidecar_path is not None
    assert annotated.annotated_path.name.endswith(ANNOTATED_SUFFIX.lstrip(".")) or (
        annotated.annotated_path.name == f"{path.stem}{ANNOTATED_SUFFIX}"
    )
    payload = json.loads(annotated.sidecar_path.read_text(encoding="utf-8"))
    assert payload["version"] == SIDECAR_VERSION
    assert set(payload.keys()) == {"version", "annotations"}
    assert payload["annotations"][0]["type"] == "rect"
    assert parse_sidecar_document({"version": 1, "annotations": [], "extra": True}) == []
    cleared = service.annotate_and_save(shot.id, [])
    assert cleared.annotated_path is None
    assert cleared.sidecar_path is None
    assert not (inbox / f"{path.stem}{ANNOTATED_SUFFIX}").exists()
    assert not (inbox / f"{path.stem}{SIDECAR_SUFFIX}").exists()
    assert port.bakes


@pytest.mark.parametrize("ac_id", ["AC-36.10"], ids=["AC-36.10"])
@pytest.mark.unit
def test_ac_36_10_read_image_variants(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.10"
    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.domain.errors import NotFoundError

    service, _uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "img.png", b"orig-bytes")
    shot = service.register_shot(path, CaptureSource.Gui)
    assert service.read_image(shot.id, "original") == b"orig-bytes"
    with pytest.raises(NotFoundError):
        service.read_image(shot.id, "annotated")
    service.annotate_and_save(
        shot.id,
        [RectAnnotation(x=0, y=0, width=2, height=2, color="blue", stroke_width=1)],
    )
    assert service.read_image(shot.id, "annotated") == b"baked"
    with pytest.raises(NotFoundError):
        service.read_image(str(uuid4()), "original")


@pytest.mark.parametrize("ac_id", ["AC-36.11"], ids=["AC-36.11"])
@pytest.mark.unit
def test_ac_36_11_remove_deletes_files_then_row(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.11"
    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.enums import CaptureSource

    service, uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "rm.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    shot = service.annotate_and_save(
        shot.id,
        [RectAnnotation(x=0, y=0, width=2, height=2, color="red", stroke_width=1)],
    )
    original = shot.original_path
    annotated = shot.annotated_path
    sidecar = shot.sidecar_path
    assert annotated is not None and sidecar is not None
    service.remove(shot.id)
    assert original.exists() is False
    assert annotated.exists() is False
    assert sidecar.exists() is False
    assert uow.capture_shots.get(shot.id) is None


@pytest.mark.parametrize("ac_id", ["AC-36.12"], ids=["AC-36.12"])
@pytest.mark.unit
def test_ac_36_12_capture_settings_keys(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.12"
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, SettingsService

    keys = {key for ns, key in SETTINGS_KEY_TABLE if ns == "capture"}
    assert keys == set(CAPTURE_KEYS)
    assert SETTINGS_KEY_TABLE[("capture", "inbox_dir")].default == CAPTURE_DEFAULTS["inbox_dir"]
    assert SETTINGS_KEY_TABLE[("capture", "hotkey")].default == CAPTURE_DEFAULTS["hotkey"]
    assert SETTINGS_KEY_TABLE[("capture", "copy_to_clipboard")].default is False
    assert SETTINGS_KEY_TABLE[("capture", "close_to_tray")].default is True
    # TA-4 (Session 30, MEU-67): the three new leaves and their defaults.
    assert SETTINGS_KEY_TABLE[("capture", "flatten_backup")].default is True
    assert SETTINGS_KEY_TABLE[("capture", "backup_dir")].default == CAPTURE_DEFAULTS["backup_dir"]
    annotated_default = CAPTURE_DEFAULTS["annotated_format"]
    assert SETTINGS_KEY_TABLE[("capture", "annotated_format")].default == annotated_default
    settings = SettingsService(SharedFakeFactory(FakeUnitOfWork()))
    with pytest.raises(ValidationError):
        settings.get("capture", "not_a_leaf")
    _ = tmp_path


@pytest.mark.parametrize("ac_id", ["AC-36.13"], ids=["AC-36.13"])
@pytest.mark.unit
def test_ac_36_13_g29_tmp_sqlite_and_isolation(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.13"
    import inspect

    from PIL import Image

    from avkit_core.domain.enums import CaptureSource
    from avkit_core.services import conversion as conversion_mod
    from avkit_core.services import download as download_mod
    from avkit_core.services import tts as tts_mod
    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService
    from avkit_infra.capture.adapter import CaptureAdapter
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    png = inbox / "g29.png"
    Image.new("RGB", (16, 16), (12, 34, 56)).save(png)
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    adapter = CaptureAdapter(mss_factory=lambda: None, platform="linux")
    service = CaptureService(
        factory, capture=adapter, annotate=adapter, settings=settings
    )
    registered = service.register_shot(png.resolve(), CaptureSource.Gui)
    listed = service.list_shots()
    assert listed[0].id == registered.id
    for module in (download_mod, tts_mod, conversion_mod):
        source = inspect.getsource(module)
        assert "CaptureService" not in source
        assert "CaptureShot" not in source
        assert "capture_shots" not in source


@pytest.mark.parametrize("ac_id", ["AC-36.14"], ids=["AC-36.14"])
@pytest.mark.unit
def test_ac_36_14_clamp_before_bake(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.14"
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation, TextAnnotation
    from avkit_core.domain.enums import CaptureSource

    service, _uow, port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "clamp.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    service.annotate_and_save(
        shot.id,
        [
            RectAnnotation(x=40, y=-3, width=2, height=2, color="red", stroke_width=1),
            ArrowAnnotation(from_xy=(0, 0), to_xy=(32, 99), color="blue", stroke_width=2),
            TextAnnotation(x=32, y=32, text="hi", color="white", font_size=12, bg_color=None),
        ],
    )
    baked = port.bakes[-1]
    rect, arrow, text = baked
    assert rect.x == 32
    assert rect.y == ANNOTATION_CLAMP_MIN
    assert arrow.to_xy == (32, 32)
    assert text.x == 32
    assert text.y == 32


@pytest.mark.parametrize("ac_id", ["AC-36.1"], ids=["AC-36.1-annotated-skip"])
@pytest.mark.unit
def test_ac_36_1_scan_skips_annotated_derivative(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.1"
    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.enums import CaptureSource

    service, uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "original.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    service.annotate_and_save(
        shot.id,
        [RectAnnotation(x=1, y=1, width=4, height=4, color="red", stroke_width=1)],
    )
    shots = service.scan_inbox()
    names = sorted(item.display_name for item in shots)
    assert names == ["original.png"]
    assert len(uow.capture_shots.list()) == 1
    assert (inbox / f"original{ANNOTATED_SUFFIX}").is_file()


@pytest.mark.parametrize("ac_id", ["AC-36.8"], ids=["AC-36.8-no-orphan"])
@pytest.mark.unit
def test_ac_36_8_failed_complete_does_not_orphan_shot(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.8"
    from dataclasses import replace

    from avkit_core.domain.enums import CaptureRequestStatus
    from avkit_core.domain.errors import ConflictError, NotFoundError

    service, uow, _port, inbox = _stack(tmp_path)
    unknown_path = _write_inbox_file(inbox, "orphan.png")
    with pytest.raises(NotFoundError):
        service.complete_request(str(uuid4()), unknown_path)
    assert uow.capture_shots.list() == []

    cancelled = service.request_interactive()
    cancelled_path = _write_inbox_file(inbox, "after-cancel.png")
    service.cancel_request(cancelled.id)
    with pytest.raises(ConflictError):
        service.complete_request(cancelled.id, cancelled_path)
    assert uow.capture_shots.list() == []

    stale = service.request_interactive()
    uow.capture_requests.save(
        replace(
            stale,
            expires_at=datetime(2026, 8, 27, 11, 0, 0, tzinfo=UTC),
        )
    )
    expired_path = _write_inbox_file(inbox, "after-expire.png")
    with pytest.raises(ConflictError):
        service.complete_request(stale.id, expired_path)
    loaded = uow.capture_requests.get(stale.id)
    assert loaded is not None
    assert loaded.status is CaptureRequestStatus.Expired
    assert uow.capture_shots.list() == []


@pytest.mark.parametrize("ac_id", ["AC-36.9"], ids=["AC-36.9-real-scan"])
@pytest.mark.unit
def test_ac_36_9_real_sqlite_bake_scan_one_original(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-36.9"
    from PIL import Image

    from avkit_core.domain.capture import RectAnnotation
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.domain.errors import NotFoundError
    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService
    from avkit_infra.capture.adapter import CaptureAdapter
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    png = inbox / "original.png"
    Image.new("RGB", (16, 16), (12, 34, 56)).save(png)
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    adapter = CaptureAdapter(mss_factory=lambda: None, platform="linux")
    service = CaptureService(
        factory, capture=adapter, annotate=adapter, settings=settings
    )
    shot = service.register_shot(png.resolve(), CaptureSource.Gui)
    service.annotate_and_save(
        shot.id,
        [RectAnnotation(x=1, y=1, width=4, height=4, color="red", stroke_width=1)],
    )
    listed = service.list_shots()
    assert [item.display_name for item in listed] == ["original.png"]
    missing = inbox / "missing.png"
    Image.new("RGB", (8, 8), (1, 2, 3)).save(missing)
    with pytest.raises(NotFoundError):
        service.complete_request(str(uuid4()), missing.resolve())
    with factory() as uow:
        names = sorted(item.display_name for item in uow.capture_shots.list())
    assert names == ["original.png"]


@pytest.mark.parametrize("ac_id", ["AC-40.31"], ids=["AC-40.31"])
@pytest.mark.unit
def test_ac_40_31_register_repairs_source_on_a_scanned_row(ac_id: str, tmp_path: Path) -> None:
    """A file the inbox scanner sees first must not keep source=Scan forever.

    The native region picker writes its PNG into the inbox and only then calls
    register. If the watcher's rescan wins that race the row already exists with
    source=Scan, and the early return on the idempotent path left it there - so
    the UI could never tell a scanned file from a captured one.
    """
    assert ac_id == "AC-40.31"
    from avkit_core.domain.enums import CaptureSource

    service, uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "picked.png")

    scanned = service.scan_inbox()
    assert len(scanned) == 1
    assert scanned[0].source is CaptureSource.Scan
    scanned_id = scanned[0].id

    registered = service.register_shot(path, CaptureSource.Gui)

    assert registered.source is CaptureSource.Gui
    assert registered.id == scanned_id
    assert registered.original_path == path
    assert registered.display_name == path.name
    assert len(uow.capture_shots.list()) == 1
    assert uow.capture_shots.get(scanned_id).source is CaptureSource.Gui

    # Idempotent in every other respect: registering again changes nothing.
    again = service.register_shot(path, CaptureSource.Gui)
    assert again.id == scanned_id
    assert again.source is CaptureSource.Gui
    assert len(uow.capture_shots.list()) == 1


@pytest.mark.parametrize("ac_id", ["AC-59.8"], ids=["AC-59.8"])
@pytest.mark.unit
def test_ac_59_8_load_shot_annotations_from_sidecar(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-59.8"
    from avkit_core.domain.capture import ArrowAnnotation
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import CaptureService

    assert hasattr(CaptureService, "load_shot_annotations")
    service, _uow, _port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "marks.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    saved = service.annotate_and_save(
        shot.id,
        [ArrowAnnotation(from_xy=(1, 1), to_xy=(8, 8), color="red", stroke_width=2)],
    )
    loaded = service.load_shot_annotations(saved.id)
    assert len(loaded) == 1
    assert isinstance(loaded[0], ArrowAnnotation)
    empty = service.annotate_and_save(saved.id, [])
    assert service.load_shot_annotations(empty.id) == []
    sidecar = path.with_name(f"{path.stem}{SIDECAR_SUFFIX}")
    sidecar.write_text(
        json.dumps({"version": 1, "annotations": [{"type": "circle", "x": 1}]}),
        encoding="utf-8",
    )
    broken = service.register_shot(path, CaptureSource.Gui)
    with pytest.raises(AnnotationValidationError):
        service.load_shot_annotations(broken.id)
    sidecar.write_text(
        json.dumps({"version": 1, "annotations": [17]}),
        encoding="utf-8",
    )
    with pytest.raises(AnnotationValidationError):
        service.load_shot_annotations(broken.id)
    sidecar.write_text(
        json.dumps(
            {
                "version": 1,
                "annotations": [
                    None,
                    {
                        "type": "arrow",
                        "from": [0, 0],
                        "to": [1, 1],
                        "color": "red",
                        "stroke_width": 1,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(AnnotationValidationError):
        service.load_shot_annotations(broken.id)


@pytest.mark.parametrize("ac_id", ["AC-59.11"], ids=["AC-59.11"])
@pytest.mark.unit
def test_ac_59_11_sidecar_rejects_circle_and_marker(ac_id: str) -> None:
    assert ac_id == "AC-59.11"
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import annotations_from_sidecar

    for forbidden in ("circle", "marker"):
        with pytest.raises(AnnotationValidationError):
            annotations_from_sidecar(
                {"version": 1, "annotations": [{"type": forbidden, "x": 0, "y": 0}]}
            )


# ------------------------------------------------------------ MEU-67 flatten / revert (Session 30)


def _ac67(n: int):
    label = f"AC-67.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _rect() -> object:
    from avkit_core.domain.capture import RectAnnotation

    return RectAnnotation(x=1, y=1, width=4, height=4, color="red", stroke_width=1)


def _files(root: Path) -> dict[str, bytes]:
    return {
        str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()
    }


def _marked_shot(tmp_path: Path, name: str = "shot.png", clock: object | None = None):
    from avkit_core.domain.enums import CaptureSource

    service, uow, port, inbox = _stack(tmp_path, clock)
    path = _write_inbox_file(inbox, name)
    shot = service.register_shot(path, CaptureSource.Gui)
    service.annotate_and_save(shot.id, [_rect()])
    return service, uow, port, inbox, shot


@_ac67(2)
@pytest.mark.unit
def test_ac_67_2_backup_exists_before_bake(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.2"
    import hashlib

    service, _uow, port, inbox, shot = _marked_shot(tmp_path)
    original = shot.original_path
    original_sha = hashlib.sha256(original.read_bytes()).hexdigest()
    seen: dict[str, object] = {}
    real_bake = port.bake

    def recording_bake(
        src: Path, annotations: object, out: Path, output_format: str = "png"
    ) -> object:
        backups = sorted((inbox / ".avkit-backup").glob("shot.*.png"))
        seen["backups"] = [hashlib.sha256(b.read_bytes()).hexdigest() for b in backups]
        seen["original_sha"] = hashlib.sha256(original.read_bytes()).hexdigest()
        seen["out_is_original"] = out.resolve() == original.resolve()
        return real_bake(src, annotations, out, output_format)

    port.bake = recording_bake  # type: ignore[method-assign]
    service.flatten(shot.id)
    assert seen["backups"] == [original_sha]
    assert seen["original_sha"] == original_sha
    assert seen["out_is_original"] is False
    assert original.read_bytes() == b"baked"


@_ac67(3)
@pytest.mark.unit
def test_ac_67_3_rollback_on_bake_and_replace_failure(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-67.3"
    from avkit_core.domain.errors import CaptureFailedError, CaptureFlattenConflictError
    from avkit_core.services import capture as capture_mod

    service, uow, port, inbox, shot = _marked_shot(tmp_path)
    before = _files(inbox)
    row = uow.capture_shots.get(shot.id)

    def failing_bake(
        src: Path, annotations: object, out: Path, output_format: str = "png"
    ) -> object:
        raise CaptureFailedError("injected")

    port.bake = failing_bake  # type: ignore[method-assign]
    with pytest.raises(CaptureFailedError):
        service.flatten(shot.id)
    assert _files(inbox) == before
    assert uow.capture_shots.get(shot.id) == row
    assert not list(inbox.rglob("*.avkit-tmp"))

    del port.bake  # back to the class method
    real_replace = capture_mod.os.replace

    def failing_replace(src: object, dst: object) -> None:
        if str(dst) == str(shot.original_path):
            raise OSError("locked by another program")
        real_replace(src, dst)  # type: ignore[arg-type]

    monkeypatch.setattr(capture_mod.os, "replace", failing_replace)
    with pytest.raises(CaptureFlattenConflictError):
        service.flatten(shot.id)
    assert _files(inbox) == before
    assert uow.capture_shots.get(shot.id) == row
    assert not list(inbox.rglob("*.avkit-tmp"))


@_ac67(9)
@pytest.mark.unit
def test_ac_67_9_backup_names_and_latest(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.9"
    import os

    from avkit_core.services.capture import latest_backup_in

    frozen = lambda: datetime(2026, 10, 2, 12, 0, 0, tzinfo=UTC)  # noqa: E731
    service, _uow, _port, inbox, shot = _marked_shot(tmp_path, clock=frozen)
    first = service.flatten(shot.id)
    service.annotate_and_save(first.id, [_rect()])
    service.flatten(first.id)
    backup_dir = inbox / ".avkit-backup"
    names = sorted(p.name for p in backup_dir.iterdir())
    assert names == ["shot.20261002-120000.png", "shot.20261002-120000_2.png"]
    # Newest by (timestamp, n), never by mtime: make _2 the oldest file on disk.
    os.utime(backup_dir / "shot.20261002-120000_2.png", (1, 1))
    assert latest_backup_in(backup_dir, "shot") == (backup_dir / "shot.20261002-120000_2.png")
    for name in (
        "a+b.20261001-000000.png",
        "aab.20261003-000000.png",
        "a.b.20261001-000000.png",
        "a.20261003-000000.png",
    ):
        (backup_dir / name).write_bytes(b"x")
    assert latest_backup_in(backup_dir, "a+b") == backup_dir / "a+b.20261001-000000.png"
    assert latest_backup_in(backup_dir, "a.b") == backup_dir / "a.b.20261001-000000.png"
    assert latest_backup_in(backup_dir, "missing") is None
    assert latest_backup_in(tmp_path / "absent", "shot") is None


@_ac67(12)
@pytest.mark.unit
def test_ac_67_12_resolve_backup_dir(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-67.12"
    from avkit_core.domain.errors import CaptureFlattenConflictError
    from avkit_core.services.capture import resolve_backup_dir

    inbox = (tmp_path / "inbox").resolve()
    inbox.mkdir()
    assert resolve_backup_dir("", inbox) == inbox / ".avkit-backup"
    assert resolve_backup_dir("   ", inbox) == inbox / ".avkit-backup"
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("USERPROFILE", str(tmp_path / "home"))
    assert resolve_backup_dir("~/x", inbox) == (tmp_path / "home" / "x").resolve()
    absolute = (tmp_path / "elsewhere").resolve()
    assert resolve_backup_dir(str(absolute), inbox) == absolute
    for bad in ("rel/dir", str(inbox), str(inbox) + os_sep()):
        with pytest.raises(CaptureFlattenConflictError):
            resolve_backup_dir(bad, inbox)
    # A refused flatten (no saved marks) never creates the backup dir.
    from avkit_core.domain.enums import CaptureSource

    (tmp_path / "second").mkdir()
    service, _uow, _port, inbox2 = _stack(tmp_path / "second")
    bare = service.register_shot(_write_inbox_file(inbox2, "bare.png"), CaptureSource.Gui)
    with pytest.raises(CaptureFlattenConflictError):
        service.flatten(bare.id)
    assert not (inbox2 / ".avkit-backup").exists()


def os_sep() -> str:
    import os

    return os.sep


@_ac67(14)
@pytest.mark.unit
def test_ac_67_14_file_lock_serializes_flatten_and_scan(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-67.14"
    import threading
    import time

    from avkit_core.domain.errors import CaptureFlattenConflictError
    from avkit_core.services import capture as capture_mod

    service, uow, port, inbox, shot = _marked_shot(tmp_path)
    real_bake = port.bake

    def slow_bake(src: Path, annotations: object, out: Path, output_format: str = "png") -> object:
        time.sleep(0.2)
        return real_bake(src, annotations, out, output_format)

    port.bake = slow_bake  # type: ignore[method-assign]
    outcomes: list[str] = []

    def run() -> None:
        try:
            service.flatten(shot.id)
            outcomes.append("ok")
        except CaptureFlattenConflictError:
            outcomes.append("conflict")

    threads = [threading.Thread(target=run) for _ in range(2)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    assert sorted(outcomes) == ["conflict", "ok"]
    assert len(list((inbox / ".avkit-backup").glob("shot.*.png"))) == 1
    assert shot.original_path.read_bytes() == b"baked"

    # A scan started while a non-atomic replace has the original briefly absent waits for the lock.
    service.annotate_and_save(shot.id, [_rect()])
    del port.bake
    real_replace = capture_mod.os.replace
    started = threading.Event()

    def slow_replace(src: object, dst: object) -> None:
        if str(dst) == str(shot.original_path):
            Path(str(dst)).unlink()
            started.set()
            time.sleep(0.3)
        real_replace(src, dst)  # type: ignore[arg-type]

    monkeypatch.setattr(capture_mod.os, "replace", slow_replace)
    deletes: list[str] = []
    real_delete = uow.capture_shots.delete

    def recording_delete(shot_id: str) -> None:
        deletes.append(shot_id)
        real_delete(shot_id)

    monkeypatch.setattr(uow.capture_shots, "delete", recording_delete)
    flattener = threading.Thread(target=service.flatten, args=(shot.id,))
    flattener.start()
    assert started.wait(2)
    service.scan_inbox()
    flattener.join()
    assert deletes == []
    assert uow.capture_shots.get(shot.id) is not None


# Session 30 execution review round 1, F4: rollback and consistency edges.


@_ac67(27)
@pytest.mark.unit
def test_review_f4a_convert_failure_after_replace_leaves_no_orphan_backup(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-67.27"
    from avkit_core.domain.errors import CaptureFailedError

    service, uow, port, inbox, shot = _marked_shot(tmp_path, "photo.jpg")
    before = _files(inbox)
    real_probe = port.probe
    probes: list[Path] = []

    def probe_failing_after_flatten(path: Path) -> object:
        # The converted copy is probed once after its creation and once after the inner flatten
        # has replaced it; fail the second one, after os.replace and the backup.
        if path.name.startswith("photo-converted"):
            probes.append(path)
            if len(probes) == 2:
                raise CaptureFailedError("injected after replace")
        return real_probe(path)

    port.probe = probe_failing_after_flatten  # type: ignore[method-assign]
    with pytest.raises(CaptureFailedError):
        service.flatten(shot.id)
    assert len(probes) == 2
    assert _files(inbox) == before
    assert [row.id for row in uow.capture_shots.list()] == [shot.id]


@_ac67(7)
@pytest.mark.unit
def test_review_f4b_revert_without_marks_removes_a_stale_sidecar(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-67.7"
    import json

    service, uow, _port, _inbox, shot = _marked_shot(tmp_path)
    service.flatten(shot.id)
    sidecar = shot.original_path.with_name(shot.original_path.stem + ".ann.json")
    sidecar.write_text(json.dumps({"version": 1, "annotations": []}), encoding="utf-8")
    reverted = service.revert(shot.id)
    assert reverted.sidecar_path is None
    assert not sidecar.exists()
    assert uow.capture_shots.get(shot.id).sidecar_path is None


def _ac84(n: int):
    label = f"AC-84.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _ticking_clock():
    """A clock that moves one second per call, so a re-save changes ``updated_at``."""
    base = datetime(2026, 10, 16, 12, 0, 0, tzinfo=UTC)
    calls = {"n": 0}

    def clock() -> datetime:
        calls["n"] += 1
        return base + timedelta(seconds=calls["n"])

    return clock


def _reconcile_shot(tmp_path: Path):
    service, uow, _port, _inbox, shot = _marked_shot(tmp_path, "shot.png", _ticking_clock())
    before = uow.capture_shots.get(shot.id)
    assert before.annotated_path is not None and before.annotated_path.is_file()
    assert before.sidecar_path is not None and before.sidecar_path.is_file()
    return service, uow, before


@_ac84(1)
@pytest.mark.unit
def test_ac_84_1a_reconcile_clears_a_missing_annotated_copy(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-84.1"
    service, uow, before = _reconcile_shot(tmp_path)
    before.annotated_path.unlink()
    service.scan_inbox()
    after = uow.capture_shots.get(before.id)
    assert after.annotated_path is None
    assert after.sidecar_path == before.sidecar_path
    assert after.updated_at > before.updated_at


@_ac84(1)
@pytest.mark.unit
def test_ac_84_1b_reconcile_clears_a_missing_sidecar(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-84.1"
    service, uow, before = _reconcile_shot(tmp_path)
    before.sidecar_path.unlink()
    service.scan_inbox()
    after = uow.capture_shots.get(before.id)
    assert after.sidecar_path is None
    assert after.annotated_path == before.annotated_path
    assert after.updated_at > before.updated_at


@_ac84(1)
@pytest.mark.unit
def test_ac_84_1c_reconcile_clears_both_when_both_are_gone(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-84.1"
    service, uow, before = _reconcile_shot(tmp_path)
    before.annotated_path.unlink()
    before.sidecar_path.unlink()
    service.scan_inbox()
    after = uow.capture_shots.get(before.id)
    assert (after.annotated_path, after.sidecar_path) == (None, None)
    assert after.updated_at > before.updated_at


@_ac84(1)
@pytest.mark.unit
def test_ac_84_1d_reconcile_leaves_a_complete_row_unsaved(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-84.1"
    service, uow, before = _reconcile_shot(tmp_path)
    saved: list[object] = []
    real_save = uow.capture_shots.save

    def spy(shot: object) -> None:
        saved.append(shot)
        real_save(shot)

    monkeypatch.setattr(uow.capture_shots, "save", spy)
    service.scan_inbox()
    assert saved == []
    assert uow.capture_shots.get(before.id) == before


@_ac84(1)
@pytest.mark.unit
def test_ac_84_1e_reconcile_still_deletes_a_row_without_its_original(
    ac_id: str, tmp_path: Path
) -> None:
    # Characterisation (task row 6): this pins the existing scan_inbox behaviour, so it passes
    # on the baseline code and must keep passing after RECONCILE.
    assert ac_id == "AC-84.1"
    service, uow, before = _reconcile_shot(tmp_path)
    before.original_path.unlink()
    service.scan_inbox()
    assert uow.capture_shots.get(before.id) is None
    assert uow.capture_shots.list() == []


# ------------------------------------------------------------ MEU-90 pixelate (Session 39)


@pytest.mark.parametrize("ac_id", ["AC-90.2"], ids=["AC-90.2"])
@pytest.mark.unit
def test_ac_90_2_pixelate_sidecar_round_trip_and_clamp(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-90.2"
    from avkit_core.domain.capture import PixelateAnnotation
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import _annotation_from_wire, _annotation_to_wire

    mark = PixelateAnnotation(x=3, y=4, width=10, height=6, block_size=7)
    wire = _annotation_to_wire(mark)
    assert wire == {"type": "pixelate", "x": 3, "y": 4, "width": 10, "height": 6, "block_size": 7}
    assert _annotation_from_wire(wire) == mark
    assert _annotation_from_wire({**wire, "color": "red", "note": 1}) == mark
    missing = {key: value for key, value in wire.items() if key != "block_size"}
    with pytest.raises(AnnotationValidationError, match="missing annotation field"):
        _annotation_from_wire(missing)

    service, _uow, port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "pixelate.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    saved = service.annotate_and_save(
        shot.id, [PixelateAnnotation(x=40, y=-3, width=9, height=5, block_size=4)]
    )
    clamped = PixelateAnnotation(x=32, y=ANNOTATION_CLAMP_MIN, width=9, height=5, block_size=4)
    assert port.bakes[-1] == [clamped]
    assert saved.sidecar_path is not None
    sidecar = json.loads(saved.sidecar_path.read_text(encoding="utf-8"))
    assert sidecar == {
        "version": SIDECAR_VERSION,
        "annotations": [
            {"type": "pixelate", "x": 32, "y": 0, "width": 9, "height": 5, "block_size": 4}
        ],
    }
    assert service.load_shot_annotations(saved.id) == [clamped]


@pytest.mark.parametrize("ac_id", ["AC-91.2"], ids=["AC-91.2"])
@pytest.mark.unit
def test_ac_91_2_eraser_sidecar_round_trip_and_clamp(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-91.2"
    from avkit_core.domain.capture import EraserAnnotation, RectAnnotation
    from avkit_core.domain.enums import CaptureSource
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import _annotation_from_wire, _annotation_to_wire

    mark = EraserAnnotation(x=3, y=4, width=10, height=6)
    wire = _annotation_to_wire(mark)
    assert wire == {"type": "eraser", "x": 3, "y": 4, "width": 10, "height": 6}
    assert _annotation_from_wire(wire) == mark
    assert _annotation_from_wire({**wire, "color": "red", "block_size": 4}) == mark
    missing = {key: value for key, value in wire.items() if key != "height"}
    with pytest.raises(AnnotationValidationError, match="missing annotation field"):
        _annotation_from_wire(missing)

    service, _uow, port, inbox = _stack(tmp_path)
    path = _write_inbox_file(inbox, "eraser.png")
    shot = service.register_shot(path, CaptureSource.Gui)
    # _clamp_annotation clamps an eraser like a rect: the same origin for the same rectangle.
    eraser = EraserAnnotation(x=40, y=-3, width=9, height=5)
    rect = RectAnnotation(x=40, y=-3, width=9, height=5, color="red", stroke_width=2)
    saved = service.annotate_and_save(shot.id, [eraser, rect])
    clamped = EraserAnnotation(x=32, y=ANNOTATION_CLAMP_MIN, width=9, height=5)
    baked_eraser, baked_rect = port.bakes[-1]
    assert baked_eraser == clamped
    assert (baked_rect.x, baked_rect.y) == (clamped.x, clamped.y)
    assert saved.sidecar_path is not None
    sidecar = json.loads(saved.sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["version"] == SIDECAR_VERSION
    assert sidecar["annotations"][0] == {"type": "eraser", "x": 32, "y": 0, "width": 9, "height": 5}
    assert service.load_shot_annotations(saved.id)[0] == clamped
