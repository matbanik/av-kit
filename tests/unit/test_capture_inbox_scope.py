"""MEU-166 (Session 103): the capture catalog follows the inbox folder (AC-166.1 to AC-166.3).

Folders A (two PNG files) and B (one) under tmp_path, on the real SQLite store and the real
Pillow adapter, built as tests/unit/test_capture_export_service.py builds its real stack. The
backup folder is an absolute tmp_path folder, so a backup made on inbox A is found on inbox B.
Nothing outside tmp_path is read or written.
"""

from __future__ import annotations

import hashlib
import inspect
import os
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from PIL import Image

from avkit_core.domain.capture import RectAnnotation
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

NOW = datetime(2026, 11, 26, 12, 0, 0, tzinfo=UTC)
SIZE = (64, 48)
RECT = RectAnnotation(x=10, y=10, width=20, height=15, color="red", stroke_width=2)
UNKNOWN_ID = "00000000-0000-4000-8000-000000000000"
#: Row 0's census of the public by-id methods, when the session's receipts are present.
CENSUS = (
    Path(os.environ.get("RECEIPTS_DIR", "C:/Temp/av-kit"))
    / "2026-11-26-capture-key-inbox-scrollbars"
    / "cki-by-id-methods.txt"
)

#: INBOX_SCOPE_BY_ID (D-1424): every public CaptureService method that takes a shot id, with a
#: call that succeeds on the shot that `_a_shot_on_b` sets up.
CALLS: dict[str, Callable[[CaptureService, str], object]] = {
    "annotate_and_save": lambda s, shot_id: s.annotate_and_save(shot_id, [RECT]),
    "crop_shot": lambda s, shot_id: s.crop_shot(shot_id, x=0, y=0, width=32, height=24),
    "export_shot": lambda s, shot_id: s.export_shot(shot_id, fmt="png"),
    "flatten": lambda s, shot_id: s.flatten(shot_id),
    "get_shot": lambda s, shot_id: s.get_shot(shot_id),
    "latest_backup": lambda s, shot_id: s.latest_backup(shot_id),
    "load_shot_annotations": lambda s, shot_id: s.load_shot_annotations(shot_id),
    "read_image": lambda s, shot_id: s.read_image(shot_id, "original"),
    "read_image_view": lambda s, shot_id: s.read_image_view(shot_id, "original"),
    "remove": lambda s, shot_id: s.remove(shot_id),
    "render_marks": lambda s, shot_id: s.render_marks(shot_id, [RECT]),
    "revert": lambda s, shot_id: s.revert(shot_id),
}
NEEDS_BACKUP = frozenset({"latest_backup", "revert"})


class Factory:
    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory

    def __call__(self) -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(self.session_factory)


def _png(path: Path, colour: tuple[int, int, int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", SIZE, colour).save(path, format="PNG")
    return path.resolve()


def _same(a: Path, b: Path) -> bool:
    return os.path.normcase(str(a)) == os.path.normcase(str(b))


@dataclass
class Scope:
    service: CaptureService
    settings: SettingsService
    factory: Factory
    adapter: CaptureAdapter
    root: Path
    a: Path
    b: Path
    a_files: tuple[Path, Path]
    b_file: Path

    def use(self, folder: Path) -> None:
        self.settings.set("capture", "inbox_dir", str(folder))

    def rows(self) -> dict[str, Any]:
        with self.factory() as uow:
            return {row.id: row for row in uow.capture_shots.list()}

    def row_for(self, path: Path) -> Any:
        with self.factory() as uow:
            return uow.capture_shots.get_by_path(path)

    def files(self, prefix: str = "") -> dict[str, str]:
        out: dict[str, str] = {}
        for path in sorted(self.root.rglob("*")):
            name = path.relative_to(self.root).as_posix()
            if path.is_file() and not name.startswith("avkit.db") and name.startswith(prefix):
                out[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        return out

    @property
    def a_names(self) -> list[str]:
        return sorted(path.name for path in self.a_files)


def _names(shots: list[Any]) -> list[str]:
    return sorted(shot.display_name for shot in shots)


@pytest.fixture
def scope(tmp_path: Path) -> Iterator[Scope]:
    root = tmp_path.resolve()
    engine = create_sqlite_engine(root / "avkit.db")
    init_schema(engine)
    factory = Factory(create_session_factory(engine))
    settings = SettingsService(factory)
    a = root / "inbox-a"
    b = root / "inbox-b"
    a_files = (_png(a / "a-1.png", (200, 30, 30)), _png(a / "a-2.png", (30, 200, 30)))
    b_file = _png(b / "b-1.png", (30, 30, 200))
    settings.set("capture", "backup_dir", str(root / "backups"))
    settings.set("capture", "inbox_dir", str(a))
    adapter = CaptureAdapter()
    service = CaptureService(
        factory, capture=adapter, annotate=adapter, settings=settings, clock=lambda: NOW
    )
    try:
        yield Scope(service, settings, factory, adapter, root, a, b, a_files, b_file)
    finally:
        engine.dispose()


@pytest.mark.unit
def test_ac_166_1_list_follows_inbox(scope: Scope) -> None:
    assert _names(scope.service.scan_inbox()) == scope.a_names
    assert _names(scope.service.list_shots()) == scope.a_names
    scope.use(scope.b)
    assert _names(scope.service.scan_inbox()) == [scope.b_file.name], "inbox B scans only B"
    assert _names(scope.service.list_shots()) == [scope.b_file.name], "inbox B lists only B"


@pytest.mark.unit
def test_ac_166_1_change_back_restores_rows(scope: Scope) -> None:
    first = {shot.id: shot.display_name for shot in scope.service.list_shots()}
    marked = scope.row_for(scope.a_files[0])
    scope.service.annotate_and_save(marked.id, [RECT])
    linked = scope.row_for(scope.a_files[0]).sidecar_path
    assert linked is not None
    scope.use(scope.b)
    scope.service.list_shots()
    scope.use(scope.a)
    back = {shot.id: shot.display_name for shot in scope.service.list_shots()}
    assert back == first, "back on A the list is A's two rows with the same ids"
    assert scope.row_for(scope.a_files[0]).sidecar_path == linked
    assert len(scope.service.load_shot_annotations(marked.id)) == 1


@pytest.mark.unit
def test_ac_166_1_subfolder_is_not_listed(scope: Scope) -> None:
    _png(scope.a / "sub" / "nested.png", (1, 2, 3))
    names = _names(scope.service.list_shots())
    assert "nested.png" not in names
    assert names == scope.a_names


@pytest.mark.unit
def test_ac_166_2_scan_leaves_other_folder_rows(scope: Scope) -> None:
    scope.service.list_shots()
    gone = scope.row_for(scope.a_files[1])
    scope.use(scope.b)
    scope.service.list_shots()
    before = scope.files("inbox-a/")
    scope.a_files[1].unlink()
    scope.service.scan_inbox()
    assert scope.rows().get(gone.id) == gone, "inbox B's scan leaves A's row as it was"
    expected = {name: digest for name, digest in before.items() if name != "inbox-a/a-2.png"}
    assert scope.files("inbox-a/") == expected, "no file in A is created or changed"


@pytest.mark.unit
def test_ac_166_2_prune_resumes_in_scope(scope: Scope) -> None:
    scope.service.list_shots()
    gone = scope.row_for(scope.a_files[1])
    scope.use(scope.b)
    scope.service.list_shots()
    scope.a_files[1].unlink()
    scope.service.scan_inbox()
    scope.use(scope.a)
    listed = scope.service.list_shots()
    assert gone.id not in {shot.id for shot in listed}
    assert gone.id not in scope.rows(), "back on A the scan prunes the vanished original"
    assert scope.a_files[0].name in _names(listed)


@pytest.mark.unit
def test_ac_166_2_linked_file_is_not_probed(scope: Scope, monkeypatch: pytest.MonkeyPatch) -> None:
    scope.use(scope.b)
    scope.service.list_shots()
    b_row = scope.row_for(scope.b_file)
    assert b_row is not None
    link = scope.a / "link.png"
    try:
        os.symlink(scope.b_file, link)
    except (OSError, NotImplementedError):
        # The host refuses a link: a plain A child that a fake resolver maps to B's file.
        _png(link, (9, 9, 9))
        real_resolve = Path.resolve

        def fake_resolve(self: Path, strict: bool = False) -> Path:
            if _same(self, link):
                return real_resolve(scope.b_file, strict)
            return real_resolve(self, strict)

        monkeypatch.setattr(Path, "resolve", fake_resolve)
    probed: list[Path] = []
    real_probe = scope.adapter.probe

    def spy(path: Path) -> Any:
        probed.append(Path(path))
        return real_probe(path)

    monkeypatch.setattr(scope.adapter, "probe", spy)
    scope.use(scope.a)
    scope.service.scan_inbox()
    scope.service.list_shots()
    hits = [str(path) for path in probed if _same(path, scope.b_file)]
    assert hits == [], "neither scan loop probes B's file through the A link"
    assert scope.row_for(scope.b_file) == b_row, "B's row is unchanged"


def _by_id_methods() -> set[str]:
    return {
        name
        for name, member in inspect.getmembers(CaptureService, inspect.isfunction)
        if not name.startswith("_") and "shot_id" in inspect.signature(member).parameters
    }


def _a_shot_on_b(scope: Scope, method: str) -> str:
    """A's first shot, marked (and flattened when the call needs a backup), with inbox B set."""
    scope.service.list_shots()
    shot = scope.row_for(scope.a_files[0])
    scope.service.annotate_and_save(shot.id, [RECT])
    if method in NEEDS_BACKUP:
        scope.service.flatten(shot.id)
        assert scope.service.latest_backup(shot.id) is not None
    scope.use(scope.b)
    scope.service.list_shots()
    return shot.id


@pytest.mark.unit
@pytest.mark.parametrize("method", sorted(CALLS))
def test_ac_166_3_by_id_outside_inbox_is_not_found(scope: Scope, method: str) -> None:
    shot_id = _a_shot_on_b(scope, method)
    with pytest.raises(NotFoundError) as unknown:
        CALLS[method](scope.service, UNKNOWN_ID)
    files, rows = scope.files(), scope.rows()
    with pytest.raises(NotFoundError) as outside:
        CALLS[method](scope.service, shot_id)
    assert str(outside.value).replace(shot_id, "<id>") == str(unknown.value).replace(
        UNKNOWN_ID, "<id>"
    ), "an A shot on inbox B reads as an unknown id"
    assert scope.files() == files, "no file changed"
    assert scope.rows() == rows, "no row changed"


@pytest.mark.unit
def test_ac_166_3_by_id_census() -> None:
    found = _by_id_methods()
    assert set(CALLS) == found, "every public by-id method has a row in CALLS"
    if CENSUS.is_file():
        lines = CENSUS.read_bytes().decode("utf-8").splitlines()
        assert {line.split("(", 1)[0].strip() for line in lines if line.strip()} == found


@pytest.mark.unit
def test_ac_166_3_by_id_inside_inbox_still_works(scope: Scope) -> None:
    scope.service.list_shots()
    shot = scope.row_for(scope.a_files[0])
    scope.service.annotate_and_save(shot.id, [RECT])
    scope.use(scope.b)
    scope.service.list_shots()
    scope.use(scope.a)
    scope.service.list_shots()
    got = scope.service.get_shot(shot.id)
    assert (got.id, got.original_path) == (shot.id, shot.original_path)
    assert len(scope.service.load_shot_annotations(shot.id)) == 1
    assert scope.service.read_image(shot.id, "original")
    data, _frame = scope.service.read_image_view(shot.id, "original")
    assert data
    assert len(scope.service.render_marks(shot.id, [RECT])) > 0
