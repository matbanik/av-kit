"""MEU-135 `CaptureService.sheet_from_video` (Session 63): SHEET_CHECKS to SHEET_DEADLINE.

AC-135.9 to AC-135.13. A recording fake `FramePort` stands in for FFmpeg and a recording fake
`sheet` for Pillow's tiling; the rows live in a real SQLite file, so a failed call's rollback is
the real unit of work's. The clock is injected through `monotonic`, so no test waits out a real
deadline.
"""

from __future__ import annotations

import io
import os
import threading
import time
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from PIL import Image

from avkit_core.domain.capture import ImageProbe
from avkit_core.domain.enums import CaptureSource
from avkit_core.domain.errors import (
    CaptureFailedError,
    InboxPathError,
    MediaProbeError,
    ValidationError,
)
from avkit_core.domain.progress import MediaInfo
from avkit_core.services import capture as capture_mod
from avkit_core.services.capture import CaptureService
from avkit_core.services.settings import SettingsService
from avkit_core.services.video_input import (
    format_timecode,
    sheet_cell_size,
    sheet_label,
    sheet_spacing_ms,
)
from avkit_infra.database.engine import (
    create_session_factory,
    create_sqlite_engine,
    init_schema,
)
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

START = 1000.0
TMP = ".avkit-tmp"
WORKER = "avkit-sheet"
FRAMES_WORKER = "avkit-frames"
PNG_SIGNATURE = bytes.fromhex("89504e470d0a1a0a")
TIME_TEXT = "a time must be seconds or HH:MM:SS.mmm"
NOT_FOUND = "video file not found"
LOCAL = "path must be a local absolute file path"
NOT_PROBED = "the file could not be probed"
NOT_VIDEO = "not a video: no video stream"
BEFORE_END = "start must be before end"
NO_DURATION = "sheet needs a duration; this video has none"
GRID_RANGE = "grid must be 2 to 5"
EDGE_RANGE = "max_edge must be between 64 and 2576"
NOT_WRITTEN = "the sheet could not be written"
SHEET = "clip-sheet-00h00m00s-00h00m03s.png"
SHEET_2 = "clip-sheet-00h00m00s-00h00m03s_2.png"
#: FRAME_TIMES of [0, 3000) in 4 and 9 parts: grid 2's and grid 3's cells.
TIMES_4 = [375, 1125, 1875, 2625]
TIMES_9 = [167, 500, 833, 1167, 1500, 1833, 2167, 2500, 2833]
#: A 320x240 (4:3) source at grid 3 and max_edge 1568, from the planning probe.
CELL_4_3_G3 = (417, 313)
#: The same source at grid 2 and max_edge 64.
CELL_4_3_G2_E64 = (32, 24)


def _png(colour: tuple[int, int, int] = (200, 10, 10), size: tuple[int, int] = (8, 6)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _failed_at(ms: int) -> str:
    return f"frame grab failed at {format_timecode(ms)}"


class FakeClock:
    """The injected `monotonic`: it moves only when a test or a fake moves it.

    `jump_after(reads, value)` moves it to `value` once the sheet worker has read it `reads`
    more times, so a test can pass the deadline between two checks with no hook between them.
    """

    def __init__(self) -> None:
        self.now = START
        self._jump: list[float] | None = None

    def jump_after(self, reads: int, value: float) -> None:
        self._jump = [reads, value]

    def __call__(self) -> float:
        if self._jump is not None and threading.current_thread().name == WORKER:
            if self._jump[0] <= 0:
                self.now = self._jump[1]
                self._jump = None
            else:
                self._jump[0] -= 1
        return self.now


@dataclass
class Grab:
    path: Path
    time_ms: int
    seek: str
    timeout_s: float
    box: tuple[int, int] | None
    thread: str


class FakeFrames:
    """A recording `FramePort`: each probe and grab is kept with what it was given.

    Grab `i` answers a distinct solid PNG of the box size, so the order the cells reach the
    tiler can be checked.
    """

    def __init__(self, info: MediaInfo) -> None:
        self.info = info
        self.error: Exception | None = None
        self.probes: list[tuple[Path, float | None]] = []
        self.grabs: list[Grab] = []
        self.answers: list[bytes] = []
        self.on_probe: Callable[[], None] | None = None
        self.on_grab: Callable[[int, int], bytes | None] | None = None

    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo:
        self.probes.append((file_path, timeout_s))
        if self.on_probe is not None:
            self.on_probe()
        if self.error is not None:
            raise self.error
        return self.info

    def grab_frame(
        self,
        path: Path,
        time_ms: int,
        *,
        seek: str,
        timeout_s: float,
        box: tuple[int, int] | None = None,
    ) -> bytes:
        index = len(self.grabs)
        thread = threading.current_thread().name
        self.grabs.append(Grab(path, time_ms, seek, timeout_s, box, thread))
        answer: bytes | None = None
        if self.on_grab is not None:
            answer = self.on_grab(index, time_ms)
        if answer is None:
            answer = _png((index * 20 % 256, 100, 255 - index * 20 % 256), box or (8, 6))
        self.answers.append(answer)
        return answer

    def grab_times(self) -> list[int]:
        return [grab.time_ms for grab in self.grabs]


@dataclass
class SheetCall:
    cells: list[bytes]
    grid: int
    cell_size: tuple[int, int]
    labels: list[str]
    thread: str


@dataclass
class FakeAnnotate:
    """The annotate port's probe, folder and tiling calls; `sheet` answers a real PNG."""

    colour: tuple[int, int, int] = (30, 140, 90)
    temp_probes: list[Path] = field(default_factory=list)
    sheets: list[SheetCall] = field(default_factory=list)
    outputs: list[bytes] = field(default_factory=list)
    on_temp_probe: Callable[[int, Path], None] | None = None
    on_sheet: Callable[[], None] | None = None

    def probe(self, path: Path) -> ImageProbe:
        if path.name.endswith(TMP):
            index = len(self.temp_probes)
            self.temp_probes.append(path)
            if self.on_temp_probe is not None:
                self.on_temp_probe(index, path)
        if not path.is_file():
            raise InboxPathError(f"{path} is not a file")
        with Image.open(path) as image:
            width, height = image.size
        return ImageProbe(width=width, height=height, file_size=path.stat().st_size)

    def ensure_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)

    def sheet(
        self,
        cells: Sequence[bytes],
        *,
        grid: int,
        cell_size: tuple[int, int],
        labels: Sequence[str],
    ) -> bytes:
        thread = threading.current_thread().name
        self.sheets.append(SheetCall(list(cells), grid, cell_size, list(labels), thread))
        if self.on_sheet is not None:
            self.on_sheet()
        data = _png(self.colour, (grid * cell_size[0], grid * cell_size[1]))
        self.outputs.append(data)
        return data


class HookedUoW(SqlAlchemyUnitOfWork):
    """The real unit of work with a hook on each enter and each commit."""

    def __init__(self, session_factory: Any, owner: HookedFactory) -> None:
        super().__init__(session_factory)
        self._owner = owner

    def __enter__(self) -> HookedUoW:
        if self._owner.on_enter is not None:
            self._owner.on_enter()
        return super().__enter__()

    def commit(self) -> None:
        if self._owner.on_commit is not None:
            self._owner.on_commit()
        super().commit()


class HookedFactory:
    def __init__(self, session_factory: Any) -> None:
        self.session_factory = session_factory
        self.on_enter: Callable[[], None] | None = None
        self.on_commit: Callable[[], None] | None = None

    def __call__(self) -> HookedUoW:
        return HookedUoW(self.session_factory, self)


@dataclass
class Stack:
    service: CaptureService
    factory: HookedFactory
    frames: FakeFrames
    annotate: FakeAnnotate
    clock: FakeClock
    inbox: Path
    video: Path
    keep: Path | None = None
    keep_bytes: bytes = b""
    keep_row: object | None = None

    def rows(self) -> list[Any]:
        with self.factory() as uow:
            return list(uow.capture_shots.list())

    def names(self) -> list[str]:
        return sorted(child.name for child in self.inbox.iterdir())

    def new_names(self) -> list[str]:
        return [name for name in self.names() if self.keep is None or name != self.keep.name]

    def new_rows(self) -> list[Any]:
        keep_id = getattr(self.keep_row, "id", None)
        return [row for row in self.rows() if row.id != keep_id]


def _info(**changes: object) -> MediaInfo:
    values: dict[str, Any] = {
        "duration": 3.0,
        "container": "mov,mp4,m4a,3gp,3g2,mj2",
        "video_codec": "h264",
        "audio_codec": "aac",
        "sample_rate": 48000,
        "channels": 2,
        "width": 320,
        "height": 240,
        "fps": 25.0,
    }
    values.update(changes)
    return MediaInfo(**values)


def _workers(name: str = WORKER) -> list[threading.Thread]:
    return [thread for thread in threading.enumerate() if thread.name == name]


def _join_workers() -> None:
    for name in (WORKER, FRAMES_WORKER):
        for thread in _workers(name):
            thread.join(10)


@pytest.fixture
def make_stack(tmp_path: Path) -> Iterator[Callable[..., Stack]]:
    engines: list[Any] = []

    def build(
        name: str = "a",
        *,
        info: MediaInfo | None = None,
        keep: bool = False,
        factory: HookedFactory | None = None,
        inbox: Path | None = None,
    ) -> Stack:
        root = tmp_path / name
        root.mkdir(parents=True, exist_ok=True)
        if factory is None:
            engine = create_sqlite_engine(root / "avkit.db")
            init_schema(engine)
            engines.append(engine)
            factory = HookedFactory(create_session_factory(engine))
        if inbox is None:
            inbox = root / "inbox"
            inbox.mkdir()
        videos = root / "videos"
        videos.mkdir()
        video = videos / "clip.mp4"
        video.write_bytes(b"video")
        settings = SettingsService(factory)
        settings.set("capture", "inbox_dir", str(inbox))
        clock = FakeClock()
        frames = FakeFrames(info if info is not None else _info())
        annotate = FakeAnnotate()
        service = CaptureService(
            factory,
            capture=annotate,  # type: ignore[arg-type]
            annotate=annotate,  # type: ignore[arg-type]
            settings=settings,
            frames=frames,
            monotonic=clock,
        )
        stack = Stack(service, factory, frames, annotate, clock, inbox, video)
        if keep:
            stack.keep = inbox / "keep.png"
            stack.keep.write_bytes(_png((1, 2, 3)))
            stack.keep_bytes = stack.keep.read_bytes()
            service.register_shot(stack.keep.resolve(), CaptureSource.Gui)
            # The row as the database gives it back, so later reads compare like with like.
            (stack.keep_row,) = stack.rows()
        return stack

    yield build
    _join_workers()
    for engine in engines:
        engine.dispose()


def _assert_nothing_left(stack: Stack) -> None:
    assert stack.new_names() == []
    assert stack.new_rows() == []
    if stack.keep is not None:
        assert stack.keep.read_bytes() == stack.keep_bytes
        assert stack.rows() == [stack.keep_row]


@contextmanager
def _looping(link: Path) -> Iterator[None]:
    """A self-loop symlink at `link`, or, where `os.symlink` is refused, a `Path.resolve` that
    raises as Python 3.12 does on a loop, for that one path only."""
    try:
        os.symlink(link, link)
    except OSError:
        original = Path.resolve

        def _resolve(self: Path, strict: bool = False) -> Path:
            if str(self) == str(link):
                raise RuntimeError(f"Symlink loop from {self}")
            return original(self, strict=strict)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(Path, "resolve", _resolve)
            yield
        return
    try:
        yield
    finally:
        link.unlink()


class _OsProxy:
    """The capture module's `os`, with `replace` swapped for a test's wrapper."""

    def __init__(self, replace: Callable[[Any, Any], None]) -> None:
        self.replace = replace

    def __getattr__(self, name: str) -> object:
        return getattr(os, name)


class _Holder(threading.Thread):
    """Holds `CAPTURE_FILE_LOCK` from another thread until told to let go (5 s at most)."""

    def __init__(self) -> None:
        super().__init__(daemon=True, name="s63-lock-holder")
        self.held = threading.Event()
        self.release = threading.Event()

    def run(self) -> None:
        capture_mod.CAPTURE_FILE_LOCK.acquire()
        self.held.set()
        try:
            self.release.wait(5)
        finally:
            capture_mod.CAPTURE_FILE_LOCK.release()


class RecordingLock:
    """Stands in for `CAPTURE_FILE_LOCK` and records how every acquisition was asked for."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.acquires: list[tuple[tuple[object, ...], dict[str, object]]] = []
        self.plain_withs = 0

    def acquire(self, *args: object, **kwargs: object) -> bool:
        self.acquires.append((args, kwargs))
        return self._lock.acquire(*args, **kwargs)  # type: ignore[arg-type]

    def release(self) -> None:
        self._lock.release()

    def locked(self) -> bool:
        return self._lock.locked()

    def __enter__(self) -> RecordingLock:
        self.plain_withs += 1
        self._lock.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self._lock.release()


def _refused(caught: pytest.ExceptionInfo[Any], kind: type[Exception], message: str) -> None:
    """Type and membership first (Session 62 RULE-3), then the exact message and no chain."""
    assert type(caught.value) is kind
    assert str(caught.value) in {message}
    assert str(caught.value) == message
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None


def _assert_made(result: Any) -> None:
    """A sheet call's result holds a shot, checked before any of its values is read."""
    assert getattr(result, "shot", None) is not None


# AC-135.9 SHEET_CHECKS --------------------------------------------------------------------------


def _missing(stack: Stack) -> dict[str, Any]:
    return {"path": str(stack.video.parent / "gone.mp4")}


def _video(**kwargs: Any) -> Callable[[Stack], dict[str, Any]]:
    return lambda stack: {"path": str(stack.video), **kwargs}


BEFORE_PROBE: list[tuple[str, Callable[[Stack], dict[str, Any]], str]] = [
    ("not-found", _missing, NOT_FOUND),
    ("url", lambda s: {"path": "http://x/clip.mp4"}, LOCAL),
    ("bad-start", _video(start="1:60"), TIME_TEXT),
    ("bad-end", _video(end="a"), TIME_TEXT),
    ("grid-1", _video(grid=1), GRID_RANGE),
    ("grid-6", _video(grid=6), GRID_RANGE),
    ("grid-true", _video(grid=True), GRID_RANGE),
    ("grid-float", _video(grid=3.0), GRID_RANGE),
    ("grid-huge", _video(grid=10**18), GRID_RANGE),
    ("edge-63", _video(max_edge=63), EDGE_RANGE),
    ("edge-2577", _video(max_edge=2577), EDGE_RANGE),
    ("edge-true", _video(max_edge=True), EDGE_RANGE),
    ("edge-huge", _video(max_edge=10**18), EDGE_RANGE),
    # Magnitude bounds (Session 62 RULE-2): each is refused before the probe.
    ("start-1e308", _video(start=1e308), TIME_TEXT),
    ("start-minus-1e308", _video(start=-1e308), TIME_TEXT),
    ("start-100h-text", _video(start="100:00:00"), TIME_TEXT),
    ("start-100h-seconds", _video(start=360000), TIME_TEXT),
    ("end-1e308", _video(end=1e308), TIME_TEXT),
    # SHEET_CHECKS' order: the path before the times, the times before grid, grid first.
    ("path-before-grid", lambda s: {"path": "http://x/clip.mp4", "grid": 1}, LOCAL),
    ("time-before-grid", _video(start="a", grid=1), TIME_TEXT),
    ("grid-before-edge", _video(grid=1, max_edge=63), GRID_RANGE),
]


@pytest.mark.parametrize(
    ("case", "body", "message"), BEFORE_PROBE, ids=[case for case, _, _ in BEFORE_PROBE]
)
def test_ac_135_9_refusals_before_the_probe(
    make_stack: Callable[..., Stack],
    case: str,
    body: Callable[[Stack], dict[str, Any]],
    message: str,
) -> None:
    del case
    stack = make_stack()
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(**body(stack))
    _refused(caught, ValidationError, message)
    assert stack.frames.probes == []
    assert stack.frames.grabs == []
    assert stack.annotate.sheets == []
    assert stack.names() == []
    assert stack.rows() == []


def test_ac_135_9_self_loop_symlink_is_not_found(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    link = stack.video.parent / "loop.mp4"
    with _looping(link), pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(link))
    _refused(caught, ValidationError, NOT_FOUND)
    assert stack.frames.probes == []
    assert stack.frames.grabs == []
    assert stack.names() == []
    assert stack.rows() == []


AFTER_PROBE: list[tuple[str, dict[str, Any], dict[str, Any], str]] = [
    ("not-probed", {}, {}, NOT_PROBED),
    ("not-video", {"video_codec": None}, {}, NOT_VIDEO),
    ("no-duration", {"duration": None}, {}, NO_DURATION),
    ("no-duration-with-a-span", {"duration": None}, {"start": 0, "end": 1}, NO_DURATION),
    ("start-at-the-end", {}, {"start": 3}, "time 00:00:03.000 is past the end (00:00:03.000)"),
    ("end-past-the-end", {}, {"end": 3.001}, "time 00:00:03.001 is past the end (00:00:03.000)"),
    ("start-after-end", {}, {"start": 2, "end": 1}, BEFORE_END),
    ("start-equals-end", {}, {"start": 1, "end": 1}, BEFORE_END),
]


@pytest.mark.parametrize(
    ("case", "changes", "kwargs", "message"),
    AFTER_PROBE,
    ids=[case for case, _, _, _ in AFTER_PROBE],
)
def test_ac_135_9_refusals_after_the_probe(
    make_stack: Callable[..., Stack],
    case: str,
    changes: dict[str, Any],
    kwargs: dict[str, Any],
    message: str,
) -> None:
    stack = make_stack(info=_info(**changes))
    marker = f"s63MARKER{uuid4().hex}"
    if case == "not-probed":
        stack.frames.error = MediaProbeError(f"{stack.video}: Invalid data {marker}")
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video), **kwargs)
    _refused(caught, ValidationError, message)
    assert marker not in str(caught.value)
    assert len(stack.frames.probes) == 1
    assert stack.frames.grabs == []
    assert stack.annotate.sheets == []
    assert stack.names() == []
    assert stack.rows() == []


def test_ac_135_9_end_equal_to_the_duration_is_accepted(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.sheet_from_video(str(stack.video), end=3, grid=2)
    _assert_made(result)
    assert stack.frames.grab_times() == TIMES_4
    assert [cell.time_ms for cell in result.cells] == TIMES_4


def test_ac_135_9_a_span_inside_the_video(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.sheet_from_video(str(stack.video), start=1, end="00:00:02", grid=2)
    _assert_made(result)
    assert stack.frames.grab_times() == [1125, 1375, 1625, 1875]
    assert result.spacing_ms == 250
    assert result.shot is not None
    assert Path(result.shot.path).name == "clip-sheet-00h00m01s-00h00m02s.png"


# AC-135.10 SHEET_WRITE trace -------------------------------------------------------------------


def test_ac_135_10_one_grab_per_cell_and_one_list_for_cells_and_labels(
    make_stack: Callable[..., Stack],
) -> None:
    stack = make_stack()

    def after_probe() -> None:
        stack.clock.now += 2

    def after_grab(index: int, ms: int) -> None:
        stack.clock.now += 3

    stack.frames.on_probe = after_probe
    stack.frames.on_grab = after_grab
    result = stack.service.sheet_from_video(str(stack.video))
    _assert_made(result)
    assert result.shot is not None
    cell = sheet_cell_size(320, 240, 3, 1568)
    assert cell == CELL_4_3_G3
    # The probe and each grab: one per cell, in time order, input seek, the box, the time left.
    assert [timeout for _, timeout in stack.frames.probes] == [pytest.approx(100.0)]
    assert stack.frames.grab_times() == TIMES_9
    assert {grab.seek for grab in stack.frames.grabs} == {"input"}
    assert {grab.box for grab in stack.frames.grabs} == {CELL_4_3_G3}
    assert {grab.path for grab in stack.frames.grabs} == {stack.video.resolve()}
    assert [grab.timeout_s for grab in stack.frames.grabs] == [
        pytest.approx(98.0 - 3 * index) for index in range(9)
    ]
    # The tiler gets the grabs' bytes in the same order, and labels from the same list.
    assert len(stack.annotate.sheets) == 1
    call = stack.annotate.sheets[0]
    assert call.cells == stack.frames.answers
    assert (call.grid, call.cell_size) == (3, CELL_4_3_G3)
    assert result.spacing_ms == sheet_spacing_ms(0, 3000, 3) == 333
    assert [(c.cell, c.time_ms, c.timecode) for c in result.cells] == [
        (n, ms, format_timecode(ms)) for n, ms in enumerate(TIMES_9, 1)
    ]
    assert call.labels == [sheet_label(c.cell, c.timecode, result.spacing_ms) for c in result.cells]
    assert call.labels[0] == "1 00:00:00.167"
    # The shot is the tiler's bytes, a Video row with the probed sheet's size.
    shot_path = Path(result.shot.path)
    assert shot_path.parent == stack.inbox.resolve()
    assert shot_path.name == SHEET
    assert shot_path.read_bytes() == stack.annotate.outputs[0]
    assert (result.shot.width, result.shot.height) == (3 * 417, 3 * 313)
    rows = stack.rows()
    assert [row.id for row in rows] == [result.shot.id]
    assert rows[0].source == CaptureSource.Video
    assert (rows[0].width, rows[0].height) == (1251, 939)
    assert stack.names() == [SHEET]
    assert result.video is not None
    assert result.video.path == str(stack.video.resolve())
    assert result.video.duration_ms == 3000
    assert stack.video.read_bytes() == b"video"


def test_ac_135_10_max_edge_and_grid_reach_the_box(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.sheet_from_video(str(stack.video), grid=2, max_edge=64)
    _assert_made(result)
    assert result.shot is not None
    assert {grab.box for grab in stack.frames.grabs} == {CELL_4_3_G2_E64}
    assert len(stack.annotate.sheets) == 1
    assert stack.annotate.sheets[0].cell_size == CELL_4_3_G2_E64
    assert stack.annotate.sheets[0].grid == 2
    assert (result.shot.width, result.shot.height) == (64, 48)
    assert result.spacing_ms == 750
    assert stack.annotate.sheets[0].labels == [
        "1 00:00:00.375",
        "2 00:00:01.125",
        "3 00:00:01.875",
        "4 00:00:02.625",
    ]


def test_ac_135_10_the_body_runs_on_the_sheet_worker(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert {grab.thread for grab in stack.frames.grabs} == {WORKER}
    assert [call.thread for call in stack.annotate.sheets] == [WORKER]


# AC-135.11 all or nothing ----------------------------------------------------------------------


@pytest.mark.parametrize("answer", [b"", b"GIF89a-not-a-png"], ids=["empty", "bad-signature"])
def test_ac_135_11_a_bad_fifth_grab_leaves_nothing(
    make_stack: Callable[..., Stack], answer: bytes
) -> None:
    stack = make_stack(keep=True)
    stack.frames.on_grab = lambda index, ms: answer if index == 4 else None
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video))
    _refused(caught, ValidationError, _failed_at(1500))
    assert stack.frames.grab_times() == TIMES_9[:5]
    assert stack.annotate.sheets == []
    _assert_nothing_left(stack)


def test_ac_135_11_a_tiling_failure_is_masked(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(keep=True)
    marker = f"s63MARKER{uuid4().hex}"

    def broken() -> None:
        raise OSError(f"cannot tile {marker}")

    stack.annotate.on_sheet = broken
    with pytest.raises(CaptureFailedError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, CaptureFailedError, NOT_WRITTEN)
    assert marker not in str(caught.value)
    assert stack.frames.grab_times() == TIMES_4
    _assert_nothing_left(stack)


def test_ac_135_11_an_output_probe_refusal_is_masked(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(keep=True)
    marker = f"s63MARKER{uuid4().hex}"

    def refuse(index: int, path: Path) -> None:
        raise InboxPathError(f"{path} {marker} is not an image")

    stack.annotate.on_temp_probe = refuse
    with pytest.raises(CaptureFailedError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, CaptureFailedError, NOT_WRITTEN)
    assert marker not in str(caught.value)
    assert len(stack.annotate.temp_probes) == 1
    _assert_nothing_left(stack)


def test_ac_135_11_a_failed_replace_is_masked(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack(keep=True)
    marker = f"s63MARKER{uuid4().hex}"
    tried: list[Path] = []

    def replace(source: Any, dest: Any) -> None:
        if str(source).endswith(TMP):
            tried.append(Path(dest))
            raise OSError(f"{dest} {marker} is locked")
        os.replace(source, dest)

    monkeypatch.setattr(capture_mod, "os", _OsProxy(replace))
    with pytest.raises(CaptureFailedError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, CaptureFailedError, NOT_WRITTEN)
    assert marker not in str(caught.value)
    assert [path.name for path in tried] == [SHEET]
    _assert_nothing_left(stack)


def test_ac_135_11_a_failed_commit_is_masked(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(keep=True)
    marker = f"s63MARKER{uuid4().hex}"
    fired: list[bool] = []

    def broken_commit() -> None:
        if stack.annotate.sheets and not fired:
            fired.append(True)
            raise OSError(f"disk I/O error {marker}")

    stack.factory.on_commit = broken_commit
    with pytest.raises(CaptureFailedError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    stack.factory.on_commit = None
    _refused(caught, CaptureFailedError, NOT_WRITTEN)
    assert marker not in str(caught.value)
    assert fired == [True]
    _assert_nothing_left(stack)


# AC-135.12 never overwrite ---------------------------------------------------------------------


def test_ac_135_12_two_calls_at_once_get_two_names(make_stack: Callable[..., Stack]) -> None:
    first = make_stack("a")
    second = make_stack("b", factory=first.factory, inbox=first.inbox)
    first.annotate.colour = (250, 0, 0)
    second.annotate.colour = (0, 0, 250)
    barrier = threading.Barrier(2, timeout=10)

    def meet(index: int, ms: int) -> None:
        if index == 0:
            barrier.wait()

    first.frames.on_grab = meet
    second.frames.on_grab = meet
    results: dict[str, Any] = {}

    def run(key: str, stack: Stack) -> None:
        try:
            results[key] = stack.service.sheet_from_video(str(stack.video), grid=2)
        except Exception as exc:  # noqa: BLE001 - kept for the assertion below
            results[key] = exc

    threads = [
        threading.Thread(target=run, args=("a", first)),
        threading.Thread(target=run, args=("b", second)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(20)
    assert sorted(results) == ["a", "b"]
    assert [getattr(results[key], "shot", None) is not None for key in ("a", "b")] == [True, True]
    paths = {key: Path(results[key].shot.path) for key in ("a", "b")}
    assert sorted(path.name for path in paths.values()) == [SHEET, SHEET_2]
    assert paths["a"].read_bytes() == first.annotate.outputs[0]
    assert paths["b"].read_bytes() == second.annotate.outputs[0]
    assert first.annotate.outputs[0] != second.annotate.outputs[0]
    assert first.names() == [SHEET, SHEET_2]
    assert len(first.rows()) == 2


def test_ac_135_12_an_inbox_file_of_that_name_is_kept(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    (stack.inbox / SHEET).write_bytes(b"someone else's")
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert Path(result.shot.path).name == SHEET_2
    assert (stack.inbox / SHEET).read_bytes() == b"someone else's"


def test_ac_135_12_a_row_of_that_name_is_kept(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    taken = stack.inbox / SHEET
    taken.write_bytes(_png((9, 9, 9)))
    row = stack.service.register_shot(taken.resolve(), CaptureSource.Gui)
    taken.unlink()
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert Path(result.shot.path).name == SHEET_2
    assert not taken.exists()
    assert row.id in [shot.id for shot in stack.rows()]


def test_ac_135_12_another_writers_temp_is_left_alone(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    other = stack.inbox / (SHEET + TMP)
    other.write_bytes(b"partial write")
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert Path(result.shot.path).name == SHEET_2
    assert other.read_bytes() == b"partial write"
    assert stack.names() == [SHEET + TMP, SHEET_2]


def test_ac_135_12_the_temp_is_opened_exclusively(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack()
    modes: list[tuple[str, str]] = []
    real_open = Path.open

    def recording_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if self.name.endswith(TMP):
            modes.append((self.name, mode))
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", recording_open)
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert modes == [(SHEET + TMP, "xb")]


# AC-135.13 SHEET_DEADLINE ----------------------------------------------------------------------


def _past() -> float:
    return START + capture_mod.SHEET_DEADLINE_S + 0.01


def test_ac_135_13a_no_time_before_the_third_grab(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()

    def late(index: int, ms: int) -> None:
        if index == 1:
            # (b) after this grab reads the clock once and passes; (a) before the third fails.
            stack.clock.jump_after(1, _past())

    stack.frames.on_grab = late
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, ValidationError, _failed_at(TIMES_4[2]))
    assert stack.frames.grab_times() == TIMES_4[:2]
    assert stack.annotate.sheets == []
    _assert_nothing_left(stack)


def test_ac_135_13b_time_runs_out_during_the_second_grab(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()

    def slow(index: int, ms: int) -> None:
        if index == 1:
            stack.clock.now = _past()

    stack.frames.on_grab = slow
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, ValidationError, _failed_at(TIMES_4[1]))
    assert stack.frames.grab_times() == TIMES_4[:2]
    assert stack.annotate.sheets == []
    _assert_nothing_left(stack)


def test_ac_135_13b_time_runs_out_during_tiling(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()

    def slow() -> None:
        stack.clock.now = _past()

    stack.annotate.on_sheet = slow
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, ValidationError, _failed_at(TIMES_4[-1]))
    assert stack.frames.grab_times() == TIMES_4
    assert len(stack.annotate.sheets) == 1
    assert stack.annotate.temp_probes == []
    _assert_nothing_left(stack)


def test_ac_135_13c_the_publish_lock_wait_is_bounded(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    holder = _Holder()

    def hold() -> None:
        holder.start()
        holder.held.wait(5)
        stack.clock.now = START + capture_mod.SHEET_DEADLINE_S - 0.05

    stack.annotate.on_sheet = hold
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.sheet_from_video(str(stack.video), grid=2)
        elapsed = time.perf_counter() - began
        still_held = holder.held.is_set() and not holder.release.is_set()
    finally:
        holder.release.set()
        if holder.is_alive():
            holder.join(10)
    _refused(caught, ValidationError, _failed_at(TIMES_4[-1]))
    assert still_held
    assert elapsed < 2
    _join_workers()
    _assert_nothing_left(stack)


def test_ac_135_13c_the_first_lock_wait_is_bounded(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()

    def little_left() -> None:
        stack.clock.now = START + capture_mod.SHEET_DEADLINE_S - 0.05

    stack.frames.on_probe = little_left
    holder = _Holder()
    holder.start()
    holder.held.wait(5)
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.sheet_from_video(str(stack.video), grid=2)
        elapsed = time.perf_counter() - began
        still_held = not holder.release.is_set()
    finally:
        holder.release.set()
        holder.join(10)
    _refused(caught, ValidationError, _failed_at(TIMES_4[0]))
    assert still_held
    assert elapsed < 2
    assert stack.frames.grabs == []
    _join_workers()
    _assert_nothing_left(stack)


def test_ac_135_13d_time_runs_out_between_publish_and_commit(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack()
    replaced: list[Path] = []

    def replace(source: Any, dest: Any) -> None:
        if str(source).endswith(TMP):
            replaced.append(Path(dest))
            stack.clock.now = START + capture_mod.SHEET_DEADLINE_S
        os.replace(source, dest)

    monkeypatch.setattr(capture_mod, "os", _OsProxy(replace))
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    _refused(caught, ValidationError, _failed_at(TIMES_4[-1]))
    assert [path.name for path in replaced] == [SHEET]
    assert [path.exists() for path in replaced] == [False]
    _assert_nothing_left(stack)


def test_ac_135_13_every_lock_acquire_passes_a_timeout(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack()
    lock = RecordingLock()
    monkeypatch.setattr(capture_mod, "CAPTURE_FILE_LOCK", lock)
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert len(lock.acquires) >= 2
    assert lock.plain_withs == 0
    assert [
        kwargs.get("timeout") is not None or len(args) >= 2 for args, kwargs in lock.acquires
    ] == [True] * len(lock.acquires)
    assert not lock.locked()


# AC-135.13 (e) the return gate -----------------------------------------------------------------


def test_ac_135_13e_a_stuck_tiler_is_abandoned(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    gate = threading.Event()

    def stuck() -> None:
        stack.clock.now = START + capture_mod.SHEET_RETURN_S + 0.01
        gate.wait(10)

    stack.annotate.on_sheet = stuck
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.sheet_from_video(str(stack.video), grid=2)
        elapsed = time.perf_counter() - began
        blocked = [thread.is_alive() for thread in _workers()]
    finally:
        gate.set()
    _refused(caught, ValidationError, _failed_at(TIMES_4[-1]))
    assert elapsed < 2
    assert blocked == [True]
    _join_workers()
    assert _workers() == []
    _assert_nothing_left(stack)


def test_ac_135_13e_a_slow_commit_is_waited_for(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    fired: list[bool] = []

    def slow_commit() -> None:
        if not fired and stack.annotate.temp_probes:
            fired.append(True)
            stack.clock.now = START + capture_mod.SHEET_RETURN_S + 0.01
            time.sleep(0.2)

    stack.factory.on_commit = slow_commit
    result = stack.service.sheet_from_video(str(stack.video), grid=2)
    _assert_made(result)
    assert fired == [True]
    stack.factory.on_commit = None
    assert [row.id for row in stack.rows()] == [result.shot.id]
    assert stack.names() == [SHEET]


def test_ac_135_13e_a_stuck_commit_is_masked(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    gate = threading.Event()
    fired: list[bool] = []

    def stuck_commit() -> None:
        if not fired and stack.annotate.temp_probes:
            fired.append(True)
            stack.clock.now = START + capture_mod.SHEET_RETURN_S + capture_mod.COMMIT_WAIT_S + 0.01
            gate.wait(10)

    stack.factory.on_commit = stuck_commit
    began = time.perf_counter()
    try:
        with pytest.raises(CaptureFailedError) as caught:
            stack.service.sheet_from_video(str(stack.video), grid=2)
        elapsed = time.perf_counter() - began
    finally:
        gate.set()
    _refused(caught, CaptureFailedError, NOT_WRITTEN)
    assert elapsed < 2
    _join_workers()
    assert _workers() == []


def test_ac_135_13e_the_workers_error_is_the_callers(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    made: list[tuple[BaseException, str]] = []

    class RecordedValidationError(ValidationError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
            made.append((self, threading.current_thread().name))

    monkeypatch.setattr(capture_mod, "ValidationError", RecordedValidationError)
    stack = make_stack()
    stack.frames.on_grab = lambda index, ms: b""
    with pytest.raises(ValidationError) as caught:
        stack.service.sheet_from_video(str(stack.video), grid=2)
    assert str(caught.value) == _failed_at(TIMES_4[0])
    assert [name for error, name in made if error is caught.value] == [WORKER]
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    _join_workers()
    _assert_nothing_left(stack)


def test_ac_135_13_frames_keeps_its_own_worker(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.frames_from_video(str(stack.video), at=[1])
    assert len(result.frames) == 1
    assert [grab.thread for grab in stack.frames.grabs] == [FRAMES_WORKER]
    assert capture_mod.FRAMES_WORKER == FRAMES_WORKER
    assert (
        capture_mod.FRAMES_DEADLINE_S,
        capture_mod.FRAMES_RETURN_S,
        capture_mod.COMMIT_WAIT_S,
    ) == (100, 105, 6)


def test_ac_135_13_the_deadlines_are_the_ruled_values() -> None:
    assert capture_mod.SHEET_WORKER == WORKER
    assert (
        capture_mod.SHEET_DEADLINE_S,
        capture_mod.SHEET_RETURN_S,
        capture_mod.COMMIT_WAIT_S,
    ) == (100, 105, 6)
    assert capture_mod.SHEET_NOT_WRITTEN == NOT_WRITTEN
    assert capture_mod.SHEET_NO_DURATION == NO_DURATION
    assert capture_mod.SHEET_GRID_RANGE == GRID_RANGE
    assert PNG_SIGNATURE == _png()[:8]
