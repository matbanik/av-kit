"""MEU-134 `CaptureService.frames_from_video` (Session 62): FRAME_CHECKS to FRAME_DEADLINE.

A recording fake `FramePort` stands in for FFmpeg and a fake annotate port for Pillow; the rows
live in a real SQLite file, so a failed call's rollback is the real unit of work's. The clock is
injected through `monotonic`, so no test waits out a real deadline.
"""

from __future__ import annotations

import io
import os
import threading
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
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
from avkit_infra.database.engine import (
    create_session_factory,
    create_sqlite_engine,
    init_schema,
)
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

START = 1000.0
TMP = ".avkit-tmp"
WORKER = "avkit-frames"
PNG_SIGNATURE = bytes.fromhex("89504e470d0a1a0a")
TIME_TEXT = "a time must be seconds or HH:MM:SS.mmm"
NOT_FOUND = "video file not found"
LOCAL = "path must be a local absolute file path"
NOT_PROBED = "the file could not be probed"
NOT_VIDEO = "not a video: no video stream"
BEFORE_END = "start must be before end"
NO_DURATION = "count needs a duration; this video has none, so use at"
NOT_WRITTEN = "the frames could not be written"
NAME_1S = "clip-t00h00m01.000s.png"
NAME_1S_2 = "clip-t00h00m01.000s_2.png"


def _png(colour: tuple[int, int, int] = (200, 10, 10), size: tuple[int, int] = (8, 6)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


def _failed_at(timecode: str) -> str:
    return f"frame grab failed at {timecode}"


class FakeClock:
    """The injected `monotonic`: it moves only when a test or a fake moves it."""

    def __init__(self) -> None:
        self.now = START

    def __call__(self) -> float:
        return self.now


class FakeFrames:
    """A recording `FramePort`: each probe and grab is kept with the timeout it was given."""

    def __init__(self, info: MediaInfo) -> None:
        self.info = info
        self.error: Exception | None = None
        self.colour = (200, 10, 10)
        self.probes: list[tuple[Path, float | None]] = []
        self.grabs: list[tuple[Path, int, str, float]] = []
        self.on_probe: Callable[[], None] | None = None
        self.on_grab: Callable[[int, int], bytes | None] | None = None

    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo:
        self.probes.append((file_path, timeout_s))
        if self.on_probe is not None:
            self.on_probe()
        if self.error is not None:
            raise self.error
        return self.info

    def grab_frame(self, path: Path, time_ms: int, *, seek: str, timeout_s: float) -> bytes:
        index = len(self.grabs)
        self.grabs.append((path, time_ms, seek, timeout_s))
        if self.on_grab is not None:
            answer = self.on_grab(index, time_ms)
            if answer is not None:
                return answer
        return _png(self.colour)

    def grab_times(self) -> list[int]:
        return [grab[1] for grab in self.grabs]


class FakeAnnotate:
    """The annotate port's probe and folder calls; `on_temp_probe` sees each temp's probe."""

    def __init__(self) -> None:
        self.temp_probes: list[Path] = []
        self.on_temp_probe: Callable[[int, Path], None] | None = None

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


def _workers() -> list[threading.Thread]:
    return [thread for thread in threading.enumerate() if thread.name == WORKER]


def _join_workers() -> None:
    for thread in _workers():
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
        super().__init__(daemon=True, name="s62-lock-holder")
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


# AC-134.5 FRAME_CHECKS ------------------------------------------------------------------------


def _missing(stack: Stack) -> dict[str, Any]:
    return {"path": str(stack.video.parent / "gone.mp4"), "at": [1]}


BEFORE_PROBE: list[tuple[str, Callable[[Stack], dict[str, Any]], str | None]] = [
    ("not-found", _missing, NOT_FOUND),
    ("url", lambda s: {"path": "http://x/clip.mp4", "at": [1]}, LOCAL),
    ("bad-time", lambda s: {"path": str(s.video), "at": ["1:60"]}, TIME_TEXT),
    ("bad-start", lambda s: {"path": str(s.video), "count": 2, "start": "a"}, TIME_TEXT),
    ("21-times", lambda s: {"path": str(s.video), "at": list(range(21))}, None),
    ("count-0", lambda s: {"path": str(s.video), "count": 0}, None),
    ("count-21", lambda s: {"path": str(s.video), "count": 21}, None),
]


@pytest.mark.parametrize(
    ("case", "body", "message"), BEFORE_PROBE, ids=[case for case, _, _ in BEFORE_PROBE]
)
def test_ac_134_5_refusals_before_the_probe(
    make_stack: Callable[..., Stack],
    case: str,
    body: Callable[[Stack], dict[str, Any]],
    message: str | None,
) -> None:
    del case
    stack = make_stack()
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(**body(stack))
    if message is not None:
        assert str(caught.value) == message
    assert caught.value.__context__ is None
    assert stack.frames.probes == []
    assert stack.frames.grabs == []
    assert stack.names() == []
    assert stack.rows() == []


def test_ac_134_5_self_loop_symlink_is_not_found(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    link = stack.video.parent / "loop.mp4"
    with _looping(link), pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(link), at=[1])
    assert str(caught.value) == NOT_FOUND
    assert caught.value.__context__ is None
    assert stack.frames.probes == []
    assert stack.frames.grabs == []
    assert stack.names() == []
    assert stack.rows() == []


AFTER_PROBE: list[tuple[str, dict[str, Any], dict[str, Any], str]] = [
    ("not-probed", {}, {"at": [1]}, NOT_PROBED),
    ("not-video", {"video_codec": None}, {"at": [1]}, NOT_VIDEO),
    (
        "at-the-end",
        {},
        {"at": [3]},
        "time 00:00:03.000 is past the end (00:00:03.000)",
    ),
    (
        "start-at-the-end",
        {},
        {"count": 2, "start": 3},
        "time 00:00:03.000 is past the end (00:00:03.000)",
    ),
    (
        "end-past-the-end",
        {},
        {"count": 2, "end": 3.001},
        "time 00:00:03.001 is past the end (00:00:03.000)",
    ),
    ("start-after-end", {}, {"count": 2, "start": 2, "end": 1}, BEFORE_END),
    ("start-equals-end", {}, {"count": 2, "start": 1, "end": 1}, BEFORE_END),
    ("no-duration-count", {"duration": None}, {"count": 2}, NO_DURATION),
]


@pytest.mark.parametrize(
    ("case", "changes", "kwargs", "message"),
    AFTER_PROBE,
    ids=[case for case, _, _, _ in AFTER_PROBE],
)
def test_ac_134_5_refusals_after_the_probe(
    make_stack: Callable[..., Stack],
    case: str,
    changes: dict[str, Any],
    kwargs: dict[str, Any],
    message: str,
) -> None:
    stack = make_stack(info=_info(**changes))
    marker = f"s62MARKER{uuid4().hex}"
    if case == "not-probed":
        stack.frames.error = MediaProbeError(f"{stack.video}: Invalid data {marker}")
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), **kwargs)
    assert str(caught.value) == message
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    assert marker not in str(caught.value)
    assert len(stack.frames.probes) == 1
    assert stack.frames.grabs == []
    assert stack.names() == []
    assert stack.rows() == []


def test_ac_134_5_both_or_neither_of_at_and_count(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    for kwargs in ({"at": [1], "count": 2}, {}, {"at": [1], "start": 0}, {"at": [1], "end": 2}):
        with pytest.raises(ValidationError) as caught:
            stack.service.frames_from_video(str(stack.video), **kwargs)
        assert str(caught.value) == "use either at or count"
    assert stack.frames.probes == []
    assert stack.frames.grabs == []
    assert stack.names() == []


def test_ac_134_5_end_equal_to_the_duration_is_accepted(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.frames_from_video(str(stack.video), count=2, end=3)
    assert len(result.frames) == 2
    assert stack.frames.grab_times() == [750, 2250]
    assert [frame.time_ms for frame in result.frames] == [750, 2250]


def test_ac_134_5_a_start_just_before_the_end_grabs_once(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.frames_from_video(str(stack.video), count=2, start=2.999)
    assert len(result.frames) == 1
    assert stack.frames.grab_times() == [2999]
    assert [grab[2] for grab in stack.frames.grabs] == ["input"]
    assert result.frames[0].time_ms == 2999
    assert result.frames[0].timecode == "00:00:02.999"


def test_ac_134_5_no_duration_at_grabs_with_output_seek(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=None, container="h264", audio_codec=None))
    result = stack.service.frames_from_video(str(stack.video), at=[1, 9000])
    assert len(result.frames) == 2
    assert [(grab[1], grab[2]) for grab in stack.frames.grabs] == [
        (1000, "output"),
        (9_000_000, "output"),
    ]
    assert result.video is not None
    assert result.video.duration_ms is None


def test_ac_134_3_at_duplicates_collapse_and_sort(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    result = stack.service.frames_from_video(str(stack.video), at=["2", 1, 2.0, "0:01", 0.5])
    assert len(result.frames) == 3
    assert stack.frames.grab_times() == [500, 1000, 2000]
    assert [frame.time_ms for frame in result.frames] == [500, 1000, 2000]


def test_ac_134_5_a_frames_call_returns_its_video_and_shots(
    make_stack: Callable[..., Stack],
) -> None:
    stack = make_stack()
    result = stack.service.frames_from_video(str(stack.video), at=[1, 2])
    assert len(result.frames) == 2
    assert result.video is not None
    assert result.video.path == str(stack.video.resolve())
    assert result.video.duration_ms == 3000
    assert [Path(frame.path).name for frame in result.frames] == [
        NAME_1S,
        "clip-t00h00m02.000s.png",
    ]
    assert [(frame.width, frame.height) for frame in result.frames] == [(8, 6), (8, 6)]
    assert [frame.timecode for frame in result.frames] == ["00:00:01.000", "00:00:02.000"]
    rows = {row.id: row for row in stack.rows()}
    assert sorted(rows) == sorted(frame.id for frame in result.frames)
    assert {row.source for row in rows.values()} == {CaptureSource.Video}
    assert stack.names() == [NAME_1S, "clip-t00h00m02.000s.png"]
    assert stack.video.read_bytes() == b"video"


# AC-134.6 FRAME_WRITE ------------------------------------------------------------------------


@pytest.mark.parametrize("answer", [b"", b"GIF89a-not-a-png"], ids=["empty", "bad-signature"])
def test_ac_134_6_a_bad_third_grab_leaves_nothing(
    make_stack: Callable[..., Stack], answer: bytes
) -> None:
    stack = make_stack(info=_info(duration=5.0), keep=True)
    stack.frames.on_grab = lambda index, ms: answer if index == 2 else None
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2, 3, 4])
    assert str(caught.value) == _failed_at("00:00:03.000")
    assert caught.value.__context__ is None
    assert stack.frames.grab_times() == [1000, 2000, 3000]
    _assert_nothing_left(stack)


def test_ac_134_6_an_image_probe_refusal_leaves_nothing(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0), keep=True)
    marker = f"s62MARKER{uuid4().hex}"

    def refuse(index: int, path: Path) -> None:
        if index == 1:
            raise InboxPathError(f"{path} {marker} is not an image")

    stack.annotate.on_temp_probe = refuse
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2, 3, 4])
    assert str(caught.value) == _failed_at("00:00:02.000")
    assert marker not in str(caught.value)
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    _assert_nothing_left(stack)


def test_ac_134_6_a_failed_publish_unlinks_what_it_moved(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack(info=_info(duration=5.0), keep=True)
    marker = f"s62MARKER{uuid4().hex}"
    moved: list[Path] = []

    def replace(source: Any, dest: Any) -> None:
        if str(source).endswith(TMP):
            if len(moved) == 1:
                raise OSError(f"{dest} {marker} is locked")
            moved.append(Path(dest))
        os.replace(source, dest)

    monkeypatch.setattr(capture_mod, "os", _OsProxy(replace))
    with pytest.raises(CaptureFailedError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2, 3, 4])
    assert str(caught.value) == NOT_WRITTEN
    assert marker not in str(caught.value)
    assert caught.value.__context__ is None
    assert len(moved) == 1
    assert not moved[0].exists()
    _assert_nothing_left(stack)


# AC-134.7 concurrency and names ----------------------------------------------------------------


def test_ac_134_7_two_calls_at_once_get_two_names(make_stack: Callable[..., Stack]) -> None:
    first = make_stack("a")
    second = make_stack("b", factory=first.factory, inbox=first.inbox)
    first.frames.colour = (250, 0, 0)
    second.frames.colour = (0, 0, 250)
    barrier = threading.Barrier(2, timeout=10)

    def meet(index: int, ms: int) -> None:
        barrier.wait()

    first.frames.on_grab = meet
    second.frames.on_grab = meet
    results: dict[str, Any] = {}

    def run(key: str, stack: Stack) -> None:
        try:
            results[key] = stack.service.frames_from_video(str(stack.video), at=[1])
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
    assert [len(getattr(results[key], "frames", ())) for key in ("a", "b")] == [1, 1]
    paths = {key: Path(results[key].frames[0].path) for key in ("a", "b")}
    assert sorted(path.name for path in paths.values()) == [NAME_1S, NAME_1S_2]
    assert paths["a"].read_bytes() == _png((250, 0, 0))
    assert paths["b"].read_bytes() == _png((0, 0, 250))
    assert first.names() == [NAME_1S, NAME_1S_2]
    assert len(first.rows()) == 2


def test_ac_134_7_an_inbox_file_of_that_name_is_kept(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    (stack.inbox / NAME_1S).write_bytes(b"someone else's")
    result = stack.service.frames_from_video(str(stack.video), at=[1])
    assert len(result.frames) == 1
    assert Path(result.frames[0].path).name == NAME_1S_2
    assert (stack.inbox / NAME_1S).read_bytes() == b"someone else's"


def test_ac_134_7_a_row_of_that_name_is_kept(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    taken = stack.inbox / NAME_1S
    taken.write_bytes(_png((9, 9, 9)))
    row = stack.service.register_shot(taken.resolve(), CaptureSource.Gui)
    taken.unlink()
    result = stack.service.frames_from_video(str(stack.video), at=[1])
    assert len(result.frames) == 1
    assert Path(result.frames[0].path).name == NAME_1S_2
    assert not taken.exists()
    assert row.id in [shot.id for shot in stack.rows()]


def test_ac_134_7_another_writers_temp_is_left_alone(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack()
    other = stack.inbox / (NAME_1S + TMP)
    other.write_bytes(b"partial write")
    result = stack.service.frames_from_video(str(stack.video), at=[1])
    assert len(result.frames) == 1
    assert Path(result.frames[0].path).name == NAME_1S_2
    assert other.read_bytes() == b"partial write"
    assert stack.names() == [NAME_1S + TMP, NAME_1S_2]


# AC-134.8 FRAME_DEADLINE -----------------------------------------------------------------------


def test_ac_134_8_the_probe_and_each_grab_get_the_time_left(
    make_stack: Callable[..., Stack],
) -> None:
    stack = make_stack(info=_info(duration=5.0))

    def after_probe() -> None:
        stack.clock.now += 2

    def after_grab(index: int, ms: int) -> None:
        stack.clock.now += 3

    stack.frames.on_probe = after_probe
    stack.frames.on_grab = after_grab
    result = stack.service.frames_from_video(str(stack.video), at=[1, 2, 3])
    assert len(result.frames) == 3
    assert [timeout for _, timeout in stack.frames.probes] == [pytest.approx(100.0)]
    assert [grab[3] for grab in stack.frames.grabs] == [
        pytest.approx(98.0),
        pytest.approx(95.0),
        pytest.approx(92.0),
    ]


def test_ac_134_8a_no_time_before_the_third_grab(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))

    def late(index: int, path: Path) -> None:
        if index == 1:
            stack.clock.now = START + capture_mod.FRAMES_DEADLINE_S + 0.01

    stack.annotate.on_temp_probe = late
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2, 3])
    assert str(caught.value) == _failed_at("00:00:03.000")
    assert stack.frames.grab_times() == [1000, 2000]
    _assert_nothing_left(stack)


def test_ac_134_8b_time_runs_out_during_the_second_grab(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))

    def slow(index: int, ms: int) -> bytes | None:
        if index == 1:
            stack.clock.now = START + capture_mod.FRAMES_DEADLINE_S + 0.01
        return None

    stack.frames.on_grab = slow
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2, 3])
    assert str(caught.value) == _failed_at("00:00:02.000")
    assert stack.frames.grab_times() == [1000, 2000]
    _assert_nothing_left(stack)


def test_ac_134_8c_the_publish_lock_wait_is_bounded(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))
    holder = _Holder()

    def last(index: int, ms: int) -> bytes | None:
        if index == 2:
            holder.start()
            holder.held.wait(5)
            stack.clock.now = START + capture_mod.FRAMES_DEADLINE_S - 0.05
        return None

    stack.frames.on_grab = last
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.frames_from_video(str(stack.video), at=[1, 2, 3])
        elapsed = time.perf_counter() - began
        still_held = holder.held.is_set() and not holder.release.is_set()
    finally:
        holder.release.set()
        if holder.is_alive():
            holder.join(10)
    assert str(caught.value) == _failed_at("00:00:03.000")
    assert still_held
    assert elapsed < 2
    _join_workers()
    _assert_nothing_left(stack)


def test_ac_134_8c_the_first_lock_wait_is_bounded(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))

    def little_left() -> None:
        stack.clock.now = START + capture_mod.FRAMES_DEADLINE_S - 0.05

    stack.frames.on_probe = little_left
    holder = _Holder()
    holder.start()
    holder.held.wait(5)
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.frames_from_video(str(stack.video), at=[1, 2, 3])
        elapsed = time.perf_counter() - began
        still_held = not holder.release.is_set()
    finally:
        holder.release.set()
        holder.join(10)
    assert str(caught.value) == _failed_at("00:00:01.000")
    assert still_held
    assert elapsed < 2
    assert stack.frames.grabs == []
    _join_workers()
    _assert_nothing_left(stack)


def test_ac_134_8d_time_runs_out_between_publish_and_commit(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack(info=_info(duration=5.0))
    replaced: list[Path] = []

    def replace(source: Any, dest: Any) -> None:
        if str(source).endswith(TMP):
            replaced.append(Path(dest))
            if len(replaced) == 2:
                stack.clock.now = START + capture_mod.FRAMES_DEADLINE_S
        os.replace(source, dest)

    monkeypatch.setattr(capture_mod, "os", _OsProxy(replace))
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2, 3])
    assert str(caught.value) == _failed_at("00:00:03.000")
    assert len(replaced) == 3
    assert [path.exists() for path in replaced] == [False, False, False]
    _assert_nothing_left(stack)


def test_ac_134_8_every_lock_acquire_passes_a_timeout(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    stack = make_stack(info=_info(duration=5.0))
    lock = RecordingLock()
    monkeypatch.setattr(capture_mod, "CAPTURE_FILE_LOCK", lock)
    result = stack.service.frames_from_video(str(stack.video), at=[1, 2])
    assert len(result.frames) == 2
    assert len(lock.acquires) >= 2
    assert lock.plain_withs == 0
    assert [
        kwargs.get("timeout") is not None or len(args) >= 2 for args, kwargs in lock.acquires
    ] == [True] * len(lock.acquires)
    assert not lock.locked()


# AC-134.8 (e) the return gate ------------------------------------------------------------------


def _all_grabbed(stack: Stack, count: int) -> bool:
    return len(stack.frames.grabs) == count and len(stack.annotate.temp_probes) == count


def test_ac_134_8e_a_stuck_decode_is_abandoned(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))
    gate = threading.Event()

    def stuck(index: int, path: Path) -> None:
        if index == 0:
            stack.clock.now = START + capture_mod.FRAMES_RETURN_S + 0.01
            gate.wait(10)

    stack.annotate.on_temp_probe = stuck
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.frames_from_video(str(stack.video), at=[1, 2])
        elapsed = time.perf_counter() - began
        blocked = [thread.is_alive() for thread in _workers()]
    finally:
        gate.set()
    assert str(caught.value) == _failed_at("00:00:02.000")
    assert elapsed < 2
    assert blocked == [True]
    _join_workers()
    assert _workers() == []
    _assert_nothing_left(stack)


def test_ac_134_8e_a_stuck_checkout_is_abandoned(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))
    gate = threading.Event()
    fired: list[bool] = []

    def exhausted_pool() -> None:
        if not fired and _all_grabbed(stack, 2):
            fired.append(True)
            stack.clock.now = START + capture_mod.FRAMES_RETURN_S + 0.01
            gate.wait(10)

    stack.factory.on_enter = exhausted_pool
    began = time.perf_counter()
    try:
        with pytest.raises(ValidationError) as caught:
            stack.service.frames_from_video(str(stack.video), at=[1, 2])
        elapsed = time.perf_counter() - began
        blocked = [thread.is_alive() for thread in _workers()]
    finally:
        gate.set()
    assert str(caught.value) == _failed_at("00:00:02.000")
    assert elapsed < 2
    assert blocked == [True]
    _join_workers()
    stack.factory.on_enter = None
    _assert_nothing_left(stack)


def test_ac_134_8e_a_slow_commit_is_waited_for(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))
    fired: list[bool] = []

    def slow_commit() -> None:
        if not fired and _all_grabbed(stack, 2):
            fired.append(True)
            stack.clock.now = START + capture_mod.FRAMES_RETURN_S + 0.01
            time.sleep(0.2)

    stack.factory.on_commit = slow_commit
    result = stack.service.frames_from_video(str(stack.video), at=[1, 2])
    assert len(result.frames) == 2
    assert fired == [True]
    stack.factory.on_commit = None
    assert sorted(row.id for row in stack.rows()) == sorted(frame.id for frame in result.frames)
    assert stack.names() == [NAME_1S, "clip-t00h00m02.000s.png"]


def test_ac_134_8e_a_stuck_commit_is_masked(make_stack: Callable[..., Stack]) -> None:
    stack = make_stack(info=_info(duration=5.0))
    gate = threading.Event()
    fired: list[bool] = []

    def stuck_commit() -> None:
        if not fired and _all_grabbed(stack, 2):
            fired.append(True)
            stack.clock.now = START + capture_mod.FRAMES_RETURN_S + capture_mod.COMMIT_WAIT_S + 0.01
            gate.wait(10)

    stack.factory.on_commit = stuck_commit
    began = time.perf_counter()
    try:
        with pytest.raises(CaptureFailedError) as caught:
            stack.service.frames_from_video(str(stack.video), at=[1, 2])
        elapsed = time.perf_counter() - began
    finally:
        gate.set()
    assert str(caught.value) == NOT_WRITTEN
    assert caught.value.__context__ is None
    assert elapsed < 2
    _join_workers()
    assert _workers() == []


def test_ac_134_8e_the_workers_error_is_the_callers(
    make_stack: Callable[..., Stack], monkeypatch: pytest.MonkeyPatch
) -> None:
    made: list[tuple[BaseException, str]] = []

    class RecordedValidationError(ValidationError):
        def __init__(self, *args: object) -> None:
            super().__init__(*args)
            made.append((self, threading.current_thread().name))

    monkeypatch.setattr(capture_mod, "ValidationError", RecordedValidationError)
    stack = make_stack(info=_info(duration=5.0))
    stack.frames.on_grab = lambda index, ms: b""
    with pytest.raises(ValidationError) as caught:
        stack.service.frames_from_video(str(stack.video), at=[1, 2])
    assert str(caught.value) == _failed_at("00:00:01.000")
    assert [name for error, name in made if error is caught.value] == [WORKER]
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    _join_workers()
    _assert_nothing_left(stack)


def test_ac_134_8_the_deadlines_are_the_ruled_values() -> None:
    assert (
        capture_mod.FRAMES_DEADLINE_S,
        capture_mod.FRAMES_RETURN_S,
        capture_mod.COMMIT_WAIT_S,
    ) == (100, 105, 6)
    assert PNG_SIGNATURE == _png()[:8]
