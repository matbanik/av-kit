"""MEU-67 contract tests: flatten, revert, backups, conversion and annotated formats.

Real `CaptureService` + real Pillow `CaptureAdapter` + real SQLite settings behind the real
FastAPI app (plan `docs/execution/plans/2026-10-02-capture-flatten-backup/`). "No change"
oracles compare SHA-256 of every file under the inbox and backup roots, and the shot row.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from PIL import Image

TOKENS = frozenset({"t" * 32})
AUTH = {"Authorization": f"Bearer {'t' * 32}"}
PREFIX = "/api/v1/captures"
FLATTEN_PATHS = ("/api/v1/captures/{id}/flatten", "/api/v1/captures/{id}/revert")


def _ac(n: int):
    label = f"AC-67.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


class _Lifecycle:
    def recover_stale_processing(self) -> None:
        return None

    def stop_processing(self) -> None:
        return None

    def unload(self) -> None:
        return None

    def cancel_processing(self) -> None:
        return None

    def liveness(self) -> SimpleNamespace:
        return SimpleNamespace(ok=True)

    def dependencies(self) -> SimpleNamespace:
        return SimpleNamespace(ffmpeg_version="6.0", ytdlp_version="2024.12")


@dataclass
class Stack:
    client: TestClient
    service: Any
    settings: Any
    adapter: Any
    inbox: Path
    root: Path
    clock: Callable[[], datetime]


class _Clock:
    """Deterministic clock: each call advances one second unless frozen."""

    def __init__(self) -> None:
        self.now = datetime(2026, 10, 2, 12, 0, 0, tzinfo=UTC)
        self.frozen = False

    def __call__(self) -> datetime:
        current = self.now
        if not self.frozen:
            self.now = self.now + timedelta(seconds=1)
        return current


def _stack(tmp_path: Path) -> Stack:
    from avkit_api.main import create_app
    from avkit_api.wiring import AppServices
    from avkit_core.services.capture import CaptureService
    from avkit_core.services.settings import SettingsService
    from avkit_infra.capture.adapter import CaptureAdapter
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    root = tmp_path / "files"
    inbox = root / "inbox"
    inbox.mkdir(parents=True)
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    engine = create_sqlite_engine(db_dir / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    adapter = CaptureAdapter(mss_factory=lambda: None, platform="linux")
    clock = _Clock()
    service = CaptureService(
        factory, capture=adapter, annotate=adapter, settings=settings, clock=clock
    )
    life = _Lifecycle()
    services = AppServices(
        download=life,  # type: ignore[arg-type]
        transcript=life,  # type: ignore[arg-type]
        tts=life,
        models=life,  # type: ignore[arg-type]
        settings=settings,
        health=life,
        conversion=life,  # type: ignore[arg-type]
        capture=service,
    )
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    return Stack(TestClient(app), service, settings, adapter, inbox, root, clock)


def _require_meu67(s: Stack) -> None:
    """Assert the MEU-67 surface exists first, so a Red is an assertion, not a TypeError."""
    import inspect

    from avkit_core.services.settings import SETTINGS_KEY_TABLE

    assert "output_format" in inspect.signature(s.adapter.bake).parameters, (
        "BAKE_PORT output_format missing"
    )
    for leaf in ("flatten_backup", "backup_dir", "annotated_format"):
        assert ("capture", leaf) in SETTINGS_KEY_TABLE, f"NEW_SETTINGS {leaf} missing"
    assert callable(getattr(s.service, "flatten", None)), "CaptureService.flatten missing"
    assert callable(getattr(s.service, "revert", None)), "CaptureService.revert missing"


def _image(path: Path, size: tuple[int, int] = (64, 48), fmt: str | None = None) -> Path:
    image = Image.new("RGB", size, (20, 40, 60))
    for x in range(0, size[0], 4):
        image.putpixel((x, x % size[1]), (250, 250, 250))
    image.save(path, format=fmt)
    return path.resolve()


MARKS = [
    {"type": "rect", "x": 2, "y": 2, "width": 20, "height": 12, "color": "red", "stroke_width": 2},
    {"type": "arrow", "from": [30, 30], "to": [50, 10], "color": "#00ff00", "stroke_width": 3},
]


def _register(
    s: Stack, name: str, fmt: str | None = None, marks: list[dict[str, object]] | None = None
) -> str:
    path = _image(s.inbox / name, fmt=fmt)
    created = s.client.post(
        PREFIX, headers=AUTH, json={"mode": "register", "path": str(path), "source": "gui"}
    )
    assert created.status_code == 201, created.text
    shot_id = str(created.json()["item"]["id"])
    if marks:
        saved = s.client.post(
            f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": marks}
        )
        assert saved.status_code == 200, saved.text
    return shot_id


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshot(root: Path) -> dict[str, str]:
    """Every file under `root` (recursive) -> SHA-256."""
    return {str(p.relative_to(root)): _sha(p) for p in sorted(root.rglob("*")) if p.is_file()}


def _row(s: Stack, shot_id: str) -> dict[str, object]:
    # The list endpoint, not the detail: a malformed sidecar makes the detail 422 by design.
    got = s.client.get(PREFIX, headers=AUTH)
    assert got.status_code == 200, got.text
    body = next(item for item in got.json()["items"] if item["id"] == shot_id)
    return {
        k: body[k]
        for k in (
            "original_path",
            "annotated_path",
            "sidecar_path",
            "width",
            "height",
            "file_size",
            "updated_at",
        )
    }


def _expected_bake(
    s: Stack, source: Path, marks: list[object], work: Path, fmt: str = "png"
) -> bytes:
    out = work / f"expected-{source.stem}.{fmt}"
    s.adapter.bake(source, marks, out, fmt)
    return out.read_bytes()


def _backup_dir(s: Stack) -> Path:
    return s.inbox / ".avkit-backup"


@_ac(1)
def test_ac_67_1_flatten_png_with_backup(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.1"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png", marks=MARKS)
    original = s.inbox / "shot.png"
    before_sha = _sha(original)
    saved_marks = s.service.load_shot_annotations(shot_id)
    work = tmp_path / "work"
    work.mkdir()
    pristine = work / "pristine.png"
    shutil.copyfile(original, pristine)
    expected = _expected_bake(s, pristine, saved_marks, work)
    older = _backup_dir(s) / "shot.20200101-000000.png"
    older.parent.mkdir(parents=True)
    older.write_bytes(b"older")
    before = _row(s, shot_id)

    resp = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["annotations"] == []
    assert body["annotated_path"] is None
    assert body["sidecar_path"] is None
    backup = Path(str(body["backup_path"]))
    assert backup != older.resolve() and backup.parent == _backup_dir(s).resolve()
    assert backup.name.startswith("shot.") and backup.suffix == ".png"
    assert _sha(backup) == before_sha
    assert original.read_bytes() == expected
    assert (body["width"], body["height"]) == (before["width"], before["height"])
    assert body["file_size"] == original.stat().st_size
    assert body["updated_at"] > before["updated_at"]
    assert not (s.inbox / "shot.annotated.png").exists()
    assert not (s.inbox / "shot.ann.json").exists()


@_ac(4)
def test_ac_67_4_flatten_conflicts_change_nothing(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.4"
    s = _stack(tmp_path)
    _require_meu67(s)
    bare = _register(s, "bare.png")
    empty = _register(s, "empty.png")
    (s.inbox / "empty.ann.json").write_text(
        json.dumps({"version": 1, "annotations": []}), encoding="utf-8"
    )
    bmp = _register(s, "photo.bmp", fmt="BMP", marks=MARKS)
    marked = _register(s, "marked.png", marks=MARKS)
    malformed = _register(s, "bad.png")
    (s.inbox / "bad.ann.json").write_text("{not json", encoding="utf-8")

    def refused(shot_id: str, status: int) -> None:
        files = _snapshot(tmp_path / "files")
        row = _row(s, shot_id)
        resp = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={})
        assert resp.status_code == status, resp.text
        assert "error" in resp.json()
        assert _snapshot(tmp_path / "files") == files
        assert _row(s, shot_id) == row

    refused(bare, 409)  # (a) no sidecar
    refused(empty, 409)  # (a) empty-list sidecar
    refused(bmp, 409)  # (b) suffix outside FLATTEN_INPUTS
    s.settings.set("capture", "backup_dir", "rel/dir")
    refused(marked, 409)  # (c) relative backup dir
    s.settings.set("capture", "backup_dir", str(s.inbox))
    refused(marked, 409)  # (c) backup dir is the inbox
    blocker = tmp_path / "files" / "not-a-dir"
    blocker.write_bytes(b"x")
    s.settings.set("capture", "backup_dir", str(blocker))
    refused(marked, 409)  # (d) backup dir is an existing file
    s.settings.set("capture", "backup_dir", "")
    refused(malformed, 422)
    files = _snapshot(tmp_path / "files")
    missing = s.client.post(
        f"{PREFIX}/00000000-0000-4000-8000-000000000000/flatten", headers=AUTH, json={}
    )
    assert missing.status_code == 404
    assert _snapshot(tmp_path / "files") == files


@_ac(5)
def test_ac_67_5_boundary_bodies_and_auth(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.5"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png", marks=MARKS)
    original = s.inbox / "shot.png"
    sha = _sha(original)
    for path in (f"{PREFIX}/{shot_id}/flatten", f"{PREFIX}/{shot_id}/revert"):
        extra = s.client.post(path, headers=AUTH, json={"x": 1})
        assert extra.status_code == 422, extra.text
        assert _sha(original) == sha
        assert s.client.post(path, json={}).status_code == 401
    assert _sha(original) == sha
    no_body = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH)
    assert no_body.status_code == 200, no_body.text
    empty_body = s.client.post(f"{PREFIX}/{shot_id}/revert", headers=AUTH, json={})
    assert empty_body.status_code == 200, empty_body.text
    assert _sha(original) == sha


@_ac(6)
def test_ac_67_6_flatten_with_backups_off(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.6"
    s = _stack(tmp_path)
    _require_meu67(s)
    s.settings.set("capture", "flatten_backup", False)
    first = _register(s, "one.png", marks=MARKS)
    resp = s.client.post(f"{PREFIX}/{first}/flatten", headers=AUTH, json={})
    assert resp.status_code == 200, resp.text
    assert resp.json()["backup_path"] is None
    assert not _backup_dir(s).exists()
    assert not (s.inbox / "one.annotated.png").exists()
    assert not (s.inbox / "one.ann.json").exists()
    second = _register(s, "two.png", marks=MARKS)
    older = _backup_dir(s) / "two.20200101-000000.png"
    older.parent.mkdir(parents=True)
    older.write_bytes(b"older")
    listing = sorted(p.name for p in _backup_dir(s).iterdir())
    resp2 = s.client.post(f"{PREFIX}/{second}/flatten", headers=AUTH, json={})
    assert resp2.status_code == 200, resp2.text
    assert resp2.json()["backup_path"] == str(older.resolve())
    assert sorted(p.name for p in _backup_dir(s).iterdir()) == listing


@_ac(7)
def test_ac_67_7_revert_restores_and_rebakes(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.7"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png", marks=MARKS)
    original = s.inbox / "shot.png"
    flat = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={}).json()
    backup = Path(str(flat["backup_path"]))
    reverted = s.client.post(f"{PREFIX}/{shot_id}/revert", headers=AUTH, json={})
    assert reverted.status_code == 200, reverted.text
    body = reverted.json()
    assert _sha(original) == _sha(backup)
    assert backup.is_file()
    assert body["backup_path"] == str(backup)
    assert body["file_size"] == original.stat().st_size
    assert body["updated_at"] > flat["updated_at"]
    assert body["annotated_path"] is None and body["sidecar_path"] is None
    assert not (s.inbox / "shot.annotated.png").exists()
    # Marks saved after a flatten are re-baked over the restored original (ANNOTATED_CONSISTENCY).
    other = _register(s, "other.png", marks=MARKS)
    assert s.client.post(f"{PREFIX}/{other}/flatten", headers=AUTH, json={}).status_code == 200
    new_marks = [
        {
            "type": "highlight",
            "x": 4,
            "y": 4,
            "width": 10,
            "height": 10,
            "color": "yellow",
            "opacity": 0.4,
        }
    ]
    assert (
        s.client.post(
            f"{PREFIX}/{other}/annotate", headers=AUTH, json={"annotations": new_marks}
        ).status_code
        == 200
    )
    again = s.client.post(f"{PREFIX}/{other}/revert", headers=AUTH, json={})
    assert again.status_code == 200, again.text
    restored = again.json()
    work = tmp_path / "work"
    work.mkdir()
    expected = _expected_bake(
        s, s.inbox / "other.png", s.service.load_shot_annotations(other), work
    )
    assert Path(str(restored["annotated_path"])).read_bytes() == expected
    assert restored["annotations"] == new_marks


@_ac(8)
def test_ac_67_8_revert_without_backup_is_404(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.8"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png")
    files = _snapshot(tmp_path / "files")
    assert s.client.post(f"{PREFIX}/{shot_id}/revert", headers=AUTH, json={}).status_code == 404
    assert _snapshot(tmp_path / "files") == files
    decoys = _backup_dir(s)
    decoys.mkdir()
    (decoys / "shot_2.20261002-120000.png").write_bytes(b"other stem")
    (decoys / "shot.20261002-120000.20261002-120001.png").write_bytes(b"dotted stem")
    (decoys / "shot.20261002-120002.png").mkdir()
    files = _snapshot(tmp_path / "files")
    assert s.client.post(f"{PREFIX}/{shot_id}/revert", headers=AUTH, json={}).status_code == 404
    assert _snapshot(tmp_path / "files") == files
    assert (
        s.client.post(
            f"{PREFIX}/00000000-0000-4000-8000-000000000000/revert", headers=AUTH, json={}
        ).status_code
        == 404
    )


@_ac(10)
def test_ac_67_10_detail_backup_path_list_unchanged(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.10"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png", marks=MARKS)
    assert s.client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()["backup_path"] is None
    flat = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={}).json()
    detail = s.client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()
    assert detail["backup_path"] == flat["backup_path"] is not None
    items = s.client.get(PREFIX, headers=AUTH).json()["items"]
    assert set(items[0]) == {
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
    }


@_ac(11)
def test_ac_67_11_capture_settings_leaves(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.11"
    s = _stack(tmp_path)
    _require_meu67(s)
    got = s.client.get("/api/v1/settings/capture", headers=AUTH).json()
    assert got["flatten_backup"] is True
    assert got["backup_dir"] == ""
    assert got["annotated_format"] == "png"
    assert (
        got["hotkey"] == "F2" and got["copy_to_clipboard"] is False and got["close_to_tray"] is True
    )
    put = s.client.put(
        "/api/v1/settings/capture",
        headers=AUTH,
        json={"flatten_backup": False, "backup_dir": "C:/Backups", "annotated_format": "webp"},
    )
    assert put.status_code in (200, 204), put.text
    back = s.client.get("/api/v1/settings/capture", headers=AUTH).json()
    assert (back["flatten_backup"], back["backup_dir"], back["annotated_format"]) == (
        False,
        "C:/Backups",
        "webp",
    )
    for bad in ({"flatten_backup": "yes"}, {"backup_dir": 5}, {"annotated_format": "gif"}):
        resp = s.client.put("/api/v1/settings/capture", headers=AUTH, json=bad)
        assert resp.status_code == 422, (bad, resp.text)
        again = s.client.get("/api/v1/settings/capture", headers=AUTH).json()
        assert (again["flatten_backup"], again["backup_dir"], again["annotated_format"]) == (
            False,
            "C:/Backups",
            "webp",
        )


@_ac(13)
def test_ac_67_13_backups_and_temps_never_become_shots(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.13"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png", marks=MARKS)
    ids_before = sorted(item["id"] for item in s.client.get(PREFIX, headers=AUTH).json()["items"])
    assert s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={}).status_code == 200
    (s.inbox / "shot.png.avkit-tmp").write_bytes(b"leftover")
    (s.inbox / "other.annotated.jpg").write_bytes(b"x")
    (s.inbox / "other.annotated.webp").write_bytes(b"x")
    items = s.client.get(PREFIX, headers=AUTH).json()["items"]
    assert sorted(item["id"] for item in items) == ids_before
    names = {Path(str(item["original_path"])).name for item in items}
    assert names == {"shot.png"}


@_ac(15)
def test_ac_67_15_openapi_routes_and_detail_schema(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.15"
    s = _stack(tmp_path)
    _require_meu67(s)
    schema = s.client.app.openapi()  # type: ignore[attr-defined]
    for path in FLATTEN_PATHS:
        op = schema["paths"][path]["post"]
        ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        assert ref.endswith("/CaptureShotDetailOut")
    detail = schema["components"]["schemas"]["CaptureShotDetailOut"]
    assert "backup_path" in detail["properties"]
    put = schema["components"]["schemas"]["SettingsPutIn"]["properties"]
    assert {"flatten_backup", "backup_dir", "annotated_format"} <= set(put)


@_ac(27)
@pytest.mark.parametrize("name,fmt", [("photo.jpg", "JPEG"), ("art.webp", "WEBP")])
def test_ac_67_27_convert_on_apply(ac_id: str, name: str, fmt: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.27"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, name, fmt=fmt, marks=MARKS)
    source = s.inbox / name
    stem = source.stem
    keep = {p: _sha(p) for p in s.inbox.iterdir() if p.is_file()}
    row = _row(s, shot_id)
    marks = s.service.load_shot_annotations(shot_id)
    work = tmp_path / "work"
    work.mkdir()
    unmarked = work / "unmarked.png"
    s.adapter.bake(source, [], unmarked, "png")
    expected = _expected_bake(s, unmarked, marks, work)

    resp = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={})

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] != shot_id
    target = Path(str(body["original_path"]))
    assert target.name == f"{stem}-converted.png"
    assert target.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    assert target.read_bytes() == expected
    assert Path(str(body["backup_path"])).read_bytes() == unmarked.read_bytes()
    for path, sha in keep.items():
        assert _sha(path) == sha, path
    assert _row(s, shot_id) == row
    ids = {item["id"] for item in s.client.get(PREFIX, headers=AUTH).json()["items"]}
    assert {shot_id, body["id"]} <= ids
    # A second Apply on the same original gets the _2 name, never an overwrite.
    second = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={})
    assert second.status_code == 200, second.text
    assert Path(str(second.json()["original_path"])).name == f"{stem}-converted_2.png"
    assert target.read_bytes() == expected


@_ac(27)
def test_ac_67_27_convert_failure_leaves_nothing(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-67.27"
    from avkit_core.domain.errors import CaptureFailedError

    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "photo.jpg", fmt="JPEG", marks=MARKS)
    files = _snapshot(tmp_path / "files")
    ids = sorted(item["id"] for item in s.client.get(PREFIX, headers=AUTH).json()["items"])
    real_bake = s.adapter.bake
    calls = {"n": 0}

    def failing_bake(
        original: Path, annotations: object, output: Path, output_format: str = "png"
    ) -> object:
        calls["n"] += 1
        if calls["n"] == 2:  # the conversion succeeded; the flatten bake of the new PNG fails
            raise CaptureFailedError("injected bake failure")
        return real_bake(original, annotations, output, output_format)

    monkeypatch.setattr(s.adapter, "bake", failing_bake)
    resp = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={})
    assert resp.status_code == 503, resp.text
    assert calls["n"] == 2
    assert _snapshot(tmp_path / "files") == files
    assert sorted(item["id"] for item in s.client.get(PREFIX, headers=AUTH).json()["items"]) == ids


@_ac(28)
def test_ac_67_28_annotated_formats(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-67.28"
    s = _stack(tmp_path)
    _require_meu67(s)
    shot_id = _register(s, "shot.png")
    stem = s.inbox / "shot"

    def save() -> dict[str, Any]:
        resp = s.client.post(
            f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": MARKS}
        )
        assert resp.status_code == 200, resp.text
        return resp.json()

    def siblings() -> list[str]:
        return sorted(p.name for p in s.inbox.iterdir() if ".annotated." in p.name)

    s.settings.set("capture", "annotated_format", "jpeg")
    body = save()
    assert Path(str(body["annotated_path"])) == Path(f"{stem}.annotated.jpg").resolve()
    assert Path(f"{stem}.annotated.jpg").read_bytes()[:3] == b"\xff\xd8\xff"
    assert siblings() == ["shot.annotated.jpg"]
    image = s.client.get(f"{PREFIX}/{shot_id}/image?variant=annotated", headers=AUTH)
    assert image.status_code == 200 and image.headers["content-type"] == "image/jpeg"
    s.settings.set("capture", "annotated_format", "webp")
    save()
    data = Path(f"{stem}.annotated.webp").read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    assert siblings() == ["shot.annotated.webp"]
    s.settings.set("capture", "annotated_format", "png")
    save()
    assert siblings() == ["shot.annotated.png"]
    names = {
        Path(str(item["original_path"])).name
        for item in s.client.get(PREFIX, headers=AUTH).json()["items"]
    }
    assert names == {"shot.png"}
    # Flatten removes whichever sibling exists; revert re-bakes in the current format.
    s.settings.set("capture", "annotated_format", "jpeg")
    save()
    assert s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={}).status_code == 200
    assert siblings() == []
    save()
    assert s.client.post(f"{PREFIX}/{shot_id}/revert", headers=AUTH, json={}).status_code == 200
    assert siblings() == ["shot.annotated.jpg"]


# ------------------------------------------------------------ MEU-90 pixelate (Session 39)


def _ac90(n: int):
    label = f"AC-90.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _uniform_blocks(image: Image.Image, box: tuple[int, int, int, int], block: int) -> bool:
    x0, y0, x1, y1 = box
    for by in range(y0, y1, block):
        for bx in range(x0, x1, block):
            cells = {
                image.getpixel((x, y))
                for y in range(by, min(by + block, y1))
                for x in range(bx, min(bx + block, x1))
            }
            if len(cells) != 1:
                return False
    return True


@_ac90(13)
def test_ac_90_13_flatten_bakes_the_mosaic(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-90.13"
    from avkit_core.domain.capture import PixelateAnnotation

    s = _stack(tmp_path)
    box, block = (0, 0, 36, 36), 8
    mark = PixelateAnnotation(x=0, y=0, width=36, height=36, block_size=block)
    wire = {"type": "pixelate", "x": mark.x, "y": mark.y, "width": mark.width}
    wire |= {"height": mark.height, "block_size": mark.block_size}
    shot_id = _register(s, "mosaic.png", marks=[wire])
    original = s.inbox / "mosaic.png"
    with Image.open(original) as opened:
        before = opened.convert("RGB")
    assert not _uniform_blocks(before, box, block)

    resp = s.client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH, json={})

    assert resp.status_code == 200, resp.text
    with Image.open(original) as opened:
        after = opened.convert("RGB")
    assert _uniform_blocks(after, box, block)
    for y in range(after.height):
        for x in range(after.width):
            if not (box[0] <= x < box[2] and box[1] <= y < box[3]):
                assert after.getpixel((x, y)) == before.getpixel((x, y)), (x, y)

    # The same flatten without the pixelate (a rect outside the rectangle) leaves it unchanged.
    rect = {"type": "rect", "x": 40, "y": 4, "width": 10, "height": 8}
    rect |= {"color": "red", "stroke_width": 1}
    plain_id = _register(s, "plain.png", marks=[rect])
    plain = s.inbox / "plain.png"
    with Image.open(plain) as opened:
        plain_before = opened.convert("RGB")
    flat = s.client.post(f"{PREFIX}/{plain_id}/flatten", headers=AUTH, json={})
    assert flat.status_code == 200, flat.text
    with Image.open(plain) as opened:
        plain_after = opened.convert("RGB")
    assert plain_after.crop(box).tobytes() == plain_before.crop(box).tobytes()
    assert not _uniform_blocks(plain_after, box, block)
