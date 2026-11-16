"""MEU-145 (Session 75): the inbox scan lists past a file it cannot read (D-900 to D-902).

AC-145.1 to AC-145.11. The adapter cases use the real `CaptureAdapter` on files written in
the test; the service cases use `FakeCapturePort` with a probe that raises for named files.
New names are imported inside each test, and each test catches what a call raises and then
asserts on it, so a Red run fails by assertion, never by setup. Every path check uses a
folder whose name holds `s75mark`, so any path in a message or a log line would match.
"""

from __future__ import annotations

import io
import random
import struct
import zlib
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pytest

OPEN_FAILED = "the image could not be opened"
NO_FILE = "no file at that path"
MARK = "s75mark"
SKIP_EVENT = "capture.scan_skipped"
LOG_KEYS = {"event", "log_level", "module", "count"}


def _ac145(n: int) -> pytest.MarkDecorator:
    label = f"AC-145.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _raised(call: Callable[[], object]) -> tuple[object, Exception | None]:
    """Run `call`; return its result and the exception it raised (None when it returned)."""
    try:
        return call(), None
    except Exception as exc:
        return None, exc


def _noisy_png(size: tuple[int, int] = (40, 30)) -> bytes:
    """A PNG of random pixels, so its IDAT is long enough to split in place."""
    from PIL import Image

    rng = random.Random(75)
    pixels = bytes(rng.randrange(256) for _ in range(size[0] * size[1] * 3))
    buffer = io.BytesIO()
    Image.frombytes("RGB", size, pixels).save(buffer, format="PNG")
    return buffer.getvalue()


def _damaged_png() -> bytes:
    """Split the IDAT into a 4-byte IDAT and a BAD! chunk: same length, Pillow's SyntaxError.

    The same split as `tests/e2e/test_api_capture_crop.py::_damage_idat_in_place`.
    """
    data = _noisy_png()
    at = data.index(b"IDAT") - 4
    (length,) = struct.unpack(">I", data[at : at + 4])
    end = at + 12 + length
    body = data[at + 8 : at + 12]
    idat = struct.pack(">I", 4) + b"IDAT" + body + struct.pack(">I", zlib.crc32(b"IDAT" + body))
    filler = b"\0" * (length - 16)
    bad = struct.pack(">I", len(filler)) + b"BAD!" + filler
    bad += struct.pack(">I", zlib.crc32(b"BAD!" + filler))
    damaged = data[:at] + idat + bad + data[end:]
    assert len(damaged) == len(data)
    return damaged


def _truncated_png() -> bytes:
    data = _noisy_png()
    return data[: len(data) // 2]


def _marked_dir(tmp_path: Path, name: str = "inbox") -> Path:
    folder = tmp_path / f"{MARK}-{name}"
    folder.mkdir()
    return folder


def _bad_files(folder: Path) -> dict[str, Path]:
    """The three unreadable kinds: a non-image named .png, a damaged PNG and a cut PNG."""
    files = {
        "non-image": folder / f"{MARK}-fake.png",
        "damaged": folder / f"{MARK}-broken.png",
        "truncated": folder / f"{MARK}-half.png",
    }
    files["non-image"].write_bytes(b"not an image at all " + MARK.encode())
    files["damaged"].write_bytes(_damaged_png())
    files["truncated"].write_bytes(_truncated_png())
    return files


def _assert_fixed(exc: Exception | None, message: str, where: str) -> None:
    from avkit_core.domain.errors import InboxPathError

    assert exc is not None, f"{where}: no raise"
    assert isinstance(exc, InboxPathError), f"{where}: raised {type(exc).__name__}"
    assert str(exc) == message, f"{where}: message is not the fixed one"
    assert MARK not in str(exc), f"{where}: the message names the path"


@_ac145(1)
@pytest.mark.unit
def test_ac_145_1_probe_non_image_gives_fixed_message(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.1"
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _bad_files(_marked_dir(tmp_path))
    good = files["non-image"].with_name("good.png")
    good.write_bytes(_noisy_png())
    probe, exc = _raised(lambda: CaptureAdapter().probe(good))
    assert exc is None and getattr(probe, "width", None) == 40
    _, exc = _raised(lambda: CaptureAdapter().probe(files["non-image"]))
    _assert_fixed(exc, OPEN_FAILED, "non-image")


@_ac145(2)
@pytest.mark.unit
def test_ac_145_2_probe_damaged_idat_gives_fixed_message(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.2"
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _bad_files(_marked_dir(tmp_path))
    assert files["damaged"].stat().st_size == len(_noisy_png())
    _, exc = _raised(lambda: CaptureAdapter().probe(files["damaged"]))
    _assert_fixed(exc, OPEN_FAILED, "damaged")


@_ac145(3)
@pytest.mark.unit
def test_ac_145_3_probe_truncated_png_gives_fixed_message(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.3"
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _bad_files(_marked_dir(tmp_path))
    _, exc = _raised(lambda: CaptureAdapter().probe(files["truncated"]))
    _assert_fixed(exc, OPEN_FAILED, "truncated")


@_ac145(4)
@pytest.mark.unit
def test_ac_145_4_probe_missing_path_gives_fixed_message(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.4"
    from avkit_infra.capture.adapter import CaptureAdapter

    missing = _marked_dir(tmp_path) / f"{MARK}-gone.png"
    _, exc = _raised(lambda: CaptureAdapter().probe(missing))
    _assert_fixed(exc, NO_FILE, "missing")


@_ac145(5)
@pytest.mark.unit
def test_ac_145_5_bake_unreadable_gives_fixed_message(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.5"
    from avkit_core.domain.capture import RedactAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _bad_files(_marked_dir(tmp_path))
    out_dir = _marked_dir(tmp_path, "out")
    mark = RedactAnnotation(x=1, y=1, width=5, height=5, color="#000000")
    good = out_dir.parent / "good.png"
    good.write_bytes(_noisy_png())
    _, exc = _raised(lambda: CaptureAdapter().bake(good, [mark], out_dir / "good.annotated.png"))
    assert exc is None and (out_dir / "good.annotated.png").is_file()
    (out_dir / "good.annotated.png").unlink()
    for kind, path in files.items():
        out = out_dir / f"{kind}.annotated.png"
        _, exc = _raised(lambda path=path, out=out: CaptureAdapter().bake(path, [mark], out))
        _assert_fixed(exc, OPEN_FAILED, kind)
        assert not out.exists(), f"{kind}: an output file was written"
    assert sorted(child.name for child in out_dir.iterdir()) == []


@_ac145(6)
@pytest.mark.unit
def test_ac_145_6_render_unreadable_gives_fixed_message(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.6"
    from avkit_core.domain.capture import RedactAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    files = _bad_files(_marked_dir(tmp_path))
    mark = RedactAnnotation(x=1, y=1, width=5, height=5, color="#000000")
    good = tmp_path / "good.png"
    good.write_bytes(_noisy_png())
    rendered, exc = _raised(lambda: CaptureAdapter().render(good, [mark]))
    assert exc is None and isinstance(rendered, bytes) and rendered.startswith(b"\x89PNG")
    for kind, path in files.items():
        _, exc = _raised(lambda path=path: CaptureAdapter().render(path, [mark]))
        _assert_fixed(exc, OPEN_FAILED, kind)


class _Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 15, 12, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.now

    def tick(self) -> None:
        self.now += timedelta(minutes=5)


def _service(tmp_path: Path, clock: _Clock | None = None) -> tuple[Any, Any, Any, Path, set[str]]:
    """The service stack with a probe that raises for each name in the returned `bad` set.

    A name starting `os-` raises `OSError`; any other raises `InboxPathError`. Each message
    holds the path and the marker, as the adapter's message did before D-902.
    """
    from tests.unit.test_capture_service import _stack

    from avkit_core.domain.errors import InboxPathError

    service, uow, port, inbox = _stack(tmp_path, clock)
    real_probe = port.probe
    bad: set[str] = set()

    def probe(path: Path) -> object:
        if path.name in bad:
            if path.name.startswith("os-"):
                raise OSError(f"{path} {MARK} could not be read")
            raise InboxPathError(f"{path} {MARK} is not an image")
        return real_probe(path)

    port.probe = probe
    return service, uow, port, inbox, bad


def _row(uow: Any, path: Path) -> tuple[object, ...] | None:
    shot = uow.capture_shots.get_by_path(path)
    if shot is None:
        return None
    return (shot.id, shot.width, shot.height, shot.file_size, shot.updated_at)


def _names(shots: object) -> list[str]:
    assert isinstance(shots, list)
    return sorted(shot.original_path.name for shot in shots)


@_ac145(7)
@pytest.mark.unit
def test_ac_145_7_scan_lists_only_readable_shots(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-145.7"
    from tests.unit.test_capture_service import _write_inbox_file

    service, uow, _port, inbox, bad = _service(tmp_path)
    for name in ("a.png", "b.jpg", "bad-inbox.png", "os-bad.png", "bad-resolve.png"):
        _write_inbox_file(inbox, name)
    bad.update({"bad-inbox.png", "os-bad.png"})
    real_resolve = Path.resolve

    def resolve(self: Path, strict: bool = False) -> Path:
        if self.name == "bad-resolve.png":
            raise OSError(f"{self} {MARK} could not be resolved")
        return real_resolve(self, strict=strict)

    monkeypatch.setattr(Path, "resolve", resolve)
    shots, exc = _raised(service.scan_inbox)
    monkeypatch.undo()
    assert exc is None, f"the scan raised {type(exc).__name__}"
    assert _names(shots) == ["a.png", "b.jpg"]
    assert sorted(shot.original_path.name for shot in uow.capture_shots.list()) == [
        "a.png",
        "b.jpg",
    ]


@_ac145(8)
@pytest.mark.unit
def test_ac_145_8_unreadable_file_keeps_its_row(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.8"
    from tests.unit.test_capture_service import _write_inbox_file

    clock = _Clock()
    service, uow, _port, inbox, bad = _service(tmp_path, clock)
    kept = _write_inbox_file(inbox, "kept.png")
    _write_inbox_file(inbox, "other.png")
    service.scan_inbox()
    before = _row(uow, kept)
    assert before is not None
    # A new length, so a scan that read the file would change file_size and updated_at.
    kept.write_bytes(b"a longer payload than before, now unreadable")
    bad.add("kept.png")
    clock.tick()
    shots, exc = _raised(service.scan_inbox)
    assert exc is None, f"the scan raised {type(exc).__name__}"
    assert _row(uow, kept) == before
    assert _names(shots) == ["kept.png", "other.png"]


@_ac145(9)
@pytest.mark.unit
def test_ac_145_9_readable_again_is_listed_next_scan(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.9"
    from tests.unit.test_capture_service import _write_inbox_file

    clock = _Clock()
    service, uow, _port, inbox, bad = _service(tmp_path, clock)
    kept = _write_inbox_file(inbox, "kept.png")
    service.scan_inbox()
    before = _row(uow, kept)
    assert before is not None
    late = _write_inbox_file(inbox, "late.png")
    kept.write_bytes(b"a longer payload than before")
    bad.update({"late.png", "kept.png"})
    clock.tick()
    first, exc = _raised(service.scan_inbox)
    assert exc is None, f"the first scan raised {type(exc).__name__}"
    assert _names(first) == ["kept.png"]
    assert _row(uow, late) is None
    bad.clear()
    clock.tick()
    second, exc = _raised(service.scan_inbox)
    assert exc is None, f"the second scan raised {type(exc).__name__}"
    assert _names(second) == ["kept.png", "late.png"]
    assert _row(uow, late) is not None
    after = _row(uow, kept)
    assert after is not None
    assert after[0] == before[0]
    assert after[3] == kept.stat().st_size != before[3]
    assert after[4] == clock.now


def _skip_events(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in logs if entry.get("event") == SKIP_EVENT]


def _no_mark_in(logs: list[dict[str, Any]], *names: str) -> None:
    for entry in logs:
        for value in entry.values():
            text = str(value)
            assert MARK not in text, "a log value holds the marker"
            for name in names:
                assert name not in text, "a log value holds a file name"
            assert "is not an image" not in text and "could not be read" not in text


@_ac145(10)
@pytest.mark.unit
def test_ac_145_10_skips_log_one_count_only_warning(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.10"
    from structlog.testing import capture_logs
    from tests.unit.test_capture_service import _write_inbox_file

    from avkit_core.services import capture as capture_service

    root = _marked_dir(tmp_path, "root")
    service, _uow, _port, inbox, bad = _service(root)
    assert MARK in str(inbox)
    _write_inbox_file(inbox, "good.png")
    _write_inbox_file(inbox, f"{MARK}-one.png")
    _write_inbox_file(inbox, f"os-{MARK}-two.png")
    bad.update({f"{MARK}-one.png", f"os-{MARK}-two.png"})
    with capture_logs() as logs:
        shots, exc = _raised(service.scan_inbox)
    assert exc is None, f"the scan raised {type(exc).__name__}"
    assert _names(shots) == ["good.png"]
    assert getattr(capture_service, "SCAN_SKIPPED_EVENT", None) == SKIP_EVENT
    events = _skip_events(logs)
    assert len(events) == 1, f"{len(events)} skip events"
    assert set(events[0]) == LOG_KEYS
    assert events[0]["count"] == 2
    assert events[0]["log_level"] == "warning"
    _no_mark_in(logs, f"{MARK}-one.png", f"os-{MARK}-two.png")


@_ac145(11)
@pytest.mark.unit
def test_ac_145_11_skip_log_dedupes_and_resets(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.11"
    from structlog.testing import capture_logs
    from tests.unit.test_capture_service import _write_inbox_file

    service, _uow, _port, inbox, bad = _service(tmp_path)
    for name in ("good.png", "x1.png", "x2.png", "x3.png"):
        _write_inbox_file(inbox, name)

    def counts(skipped: set[str]) -> list[object]:
        bad.clear()
        bad.update(skipped)
        with capture_logs() as logs:
            _, exc = _raised(service.scan_inbox)
        assert exc is None, f"the scan raised {type(exc).__name__}"
        return [entry.get("count") for entry in _skip_events(logs)]

    assert counts({"x1.png", "x2.png"}) == [2], "the first skip logs once"
    assert counts({"x1.png", "x2.png"}) == [], "the same set logs again"
    assert counts({"x1.png", "x2.png", "x3.png"}) == [3], "a changed set logs nothing"
    assert counts(set()) == [], "a clean scan logs"
    assert counts({"x3.png"}) == [1], "a later bad file logs nothing"
    assert counts(set()) == [], "a clean scan logs"
    assert counts({"x3.png"}) == [1], "a recurrence after a clean scan logs nothing"
