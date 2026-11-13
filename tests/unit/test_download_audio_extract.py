"""MEU-142 download audio extract: an audio-only `StandardMp3` job ends as an MP3.

AC-142.1, AC-142.2, AC-142.4 to AC-142.16 and AC-142.18. Module-level imports use only names
that row 1 added or that existed at the baseline, so a behaviour test fails by assertion on a
row 1 stub, never by an import error (Session 62 RULE-3). Every test asserts a length before it
indexes (Session 62 RULE-3). No test reaches YouTube or the network: the YouTube port is a fake
that writes a local source file, and the one real adapter here (AC-142.18) has no FFmpeg.
"""

from __future__ import annotations

import inspect
import shutil
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

import pytest
from structlog.testing import capture_logs
from tests.unit.test_services import (
    FakeMedia,
    FakeUnitOfWork,
    FakeYouTube,
    SharedFakeFactory,
    _health,
)

from avkit_core.domain.download import (
    DownloadJob,
    DownloadResult,
    VideoInfo,
    download_failure_message,
)
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadFailureCause,
    DownloadStatus,
    QualityPreset,
    QueueProcessorState,
)
from avkit_core.domain.errors import DownloadCancelledError, FFmpegNotFoundError, FilesystemError
from avkit_core.domain.progress import ConvertOptions
from avkit_core.ports.media import MediaPort
from avkit_core.services import download as download_mod
from avkit_core.services import health as health_module
from avkit_core.services.download import DownloadService, last_line, scrub_line
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.settings import SettingsService

pytestmark = pytest.mark.unit

#: The D-665 options, written out so the test does not read the map it checks.
MP3_OPTIONS = ConvertOptions(codec="libmp3lame", bitrate_kbps=192, sample_rate=None, channels=None)
NOT_FOUND_CARD = "Download failed: ffmpeg binary was not found."
CONVERT_CARD = "Download failed: MP3 convert failed."
WRITE_CARD = download_failure_message(DownloadFailureCause.write_failed, None)
SOURCE_BYTES = b"s67 source audio bytes"
MP3_BYTES = b"ID3 s67 converted mp3 bytes"


class SourceYouTube(FakeYouTube):
    """A YouTube port that writes a local source file, `<stem><suffix>`, and returns it."""

    def __init__(self, folder: Path, suffix: str, stem: str) -> None:
        super().__init__()
        self.folder = folder
        self.suffix = suffix
        self.stem = stem
        self.service: DownloadService | None = None
        self.written: list[Path] = []
        self.last_options: Any = None
        self.trace: list[tuple[Any, ...]] | None = None
        self.on_download: Callable[[], None] | None = None

    def extract_info(self, url: str, flat: bool = False, options: object = None) -> VideoInfo:
        video_id = url.rsplit("/", 1)[-1]
        return VideoInfo(video_id=video_id, title="One", duration=1.0, formats=[])

    def download(self, url: str, options: object) -> DownloadResult:
        self.last_options = options
        if self.trace is not None:
            self.trace.append(("download",))
        if self.on_download is not None:
            self.on_download()
        if self.service is not None and self.service.should_stop():
            raise DownloadCancelledError("cancelled")
        path = self.folder / f"{self.stem}{self.suffix}"
        path.write_bytes(SOURCE_BYTES)
        self.written.append(path)
        return DownloadResult(
            file_path=path,
            file_size=len(SOURCE_BYTES),
            video_id=url.rsplit("/", 1)[-1],
            title="One",
            sabr_detected=False,
        )


class RecordingMedia(FakeMedia):
    """A `MediaPort` whose `convert` records each call, then writes the MP3 or raises."""

    def __init__(
        self,
        *,
        error: Callable[[Path, Path], BaseException] | None = None,
        partial: bool = False,
        on_convert: Callable[[Path, Path], None] | None = None,
    ) -> None:
        super().__init__()
        self.calls: list[tuple[Path, Path, object]] = []
        self.error = error
        self.partial = partial
        self.on_convert = on_convert
        self.trace: list[tuple[Any, ...]] | None = None
        self.status_inside: Callable[[], str] | None = None

    def convert(self, input_path: Path, output_path: Path, options: object) -> None:
        self.calls.append((input_path, output_path, options))
        if self.trace is not None and self.status_inside is not None:
            self.trace.append(("convert", self.status_inside()))
        if self.on_convert is not None:
            self.on_convert(input_path, output_path)
        if self.error is not None:
            if self.partial:
                output_path.write_bytes(b"partial mp3")
            raise self.error(input_path, output_path)
        output_path.write_bytes(MP3_BYTES)


@dataclass
class Stack:
    service: DownloadService
    youtube: SourceYouTube
    media: RecordingMedia
    factory: Any
    folder: Path
    settings: SettingsService


def _stack(
    tmp_path: Path,
    media: Any = None,
    *,
    suffix: str = ".m4a",
    stem: str = "a",
    uow: FakeUnitOfWork | None = None,
    folder: Path | None = None,
) -> Stack:
    factory = SharedFakeFactory(uow or FakeUnitOfWork())
    settings = SettingsService(factory)
    out = folder or tmp_path / "out"
    out.mkdir(parents=True, exist_ok=True)
    youtube = SourceYouTube(out, suffix, stem)
    chosen = media if media is not None else RecordingMedia()
    service = DownloadService(
        factory,
        youtube=youtube,
        media=chosen,
        coordinator=ExtractCoordinator(youtube),
        settings=settings,
        sleep=lambda _seconds: None,
    )
    youtube.service = service
    return Stack(service, youtube, chosen, factory, out, settings)


def _add(
    stack: Stack,
    video_id: str = "vid1",
    *,
    audio_only: bool = True,
    audio_format: AudioFormat = AudioFormat.StandardMp3,
) -> DownloadJob:
    jobs = stack.service.add_to_queue(
        f"https://youtu.be/{video_id}", QualityPreset.P1080, audio_only, audio_format
    )
    assert len(jobs) == 1
    return jobs[0]


def _drain(stack: Stack) -> None:
    stack.service.start_processing()
    thread = stack.service._thread
    if thread is not None:
        thread.join(timeout=10)
        assert not thread.is_alive()


def _job(stack: Stack, job_id: str) -> DownloadJob | None:
    with stack.factory() as uow:
        return uow.downloads.get(job_id)


def _run(stack: Stack, **add: Any) -> DownloadJob:
    added = _add(stack, **add)
    _drain(stack)
    job = _job(stack, added.id)
    assert job is not None
    return job


def _raised(call: Callable[[], object]) -> type[BaseException] | None:
    """The class `call` raised, or None, so a wrong class fails by assertion."""
    try:
        call()
    except Exception as exc:  # noqa: BLE001 - the class is the observation
        return type(exc)
    return None


def _events(logs: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [entry for entry in logs if entry.get("event") == name]


# --- AC-142.1 AUDIO_EXTRACT ---------------------------------------------------------------


def test_ac_142_1_audio_extract_map_is_exact() -> None:
    assert hasattr(download_mod, "AUDIO_EXTRACT")
    expected = {AudioFormat.StandardMp3: (".mp3", MP3_OPTIONS)}
    assert download_mod.AUDIO_EXTRACT == expected
    keys = [
        audio_format for audio_format in AudioFormat if audio_format in download_mod.AUDIO_EXTRACT
    ]
    assert keys == [AudioFormat.StandardMp3]
    assert AudioFormat.HighM4a not in download_mod.AUDIO_EXTRACT
    assert AudioFormat.StandardM4a not in download_mod.AUDIO_EXTRACT


# --- AC-142.2 MEDIA_PORT (type; passes where row 2 writes it) ------------------------------


def test_ac_142_2_media_is_a_required_keyword_right_after_youtube(tmp_path: Path) -> None:
    parameters = inspect.signature(DownloadService.__init__).parameters
    names = list(parameters)
    assert "media" in names and "youtube" in names
    assert names.index("media") == names.index("youtube") + 1
    media = parameters["media"]
    assert media.kind is inspect.Parameter.KEYWORD_ONLY
    assert media.default is inspect.Parameter.empty
    assert media.annotation in ("MediaPort", MediaPort)

    factory = SharedFakeFactory(FakeUnitOfWork())
    youtube = SourceYouTube(tmp_path, ".m4a", "a")
    missing = _raised(
        lambda: DownloadService(  # type: ignore[call-arg]
            factory,
            youtube=youtube,
            coordinator=ExtractCoordinator(youtube),
            settings=SettingsService(factory),
        )
    )
    assert missing is TypeError


# --- AC-142.4 EXTRACT_TRIGGER ------------------------------------------------------------

CELLS = [(audio_format, audio_only) for audio_format in AudioFormat for audio_only in (True, False)]


@pytest.mark.parametrize(
    ("audio_format", "audio_only"),
    CELLS,
    ids=[f"{fmt.value}-{'audio' if only else 'video'}" for fmt, only in CELLS],
)
def test_ac_142_4_only_audio_mp3_converts(
    tmp_path: Path, audio_format: AudioFormat, audio_only: bool
) -> None:
    stack = _stack(tmp_path)
    job = _run(stack, audio_only=audio_only, audio_format=audio_format)
    assert len(stack.youtube.written) == 1
    source = stack.youtube.written[0]
    if audio_only and audio_format is AudioFormat.StandardMp3:
        assert len(stack.media.calls) == 1
        assert stack.media.calls[0] == (source, source.with_suffix(".mp3"), MP3_OPTIONS)
    else:
        assert stack.media.calls == []
        assert job.status is DownloadStatus.Done
        assert job.file_path == source


@pytest.mark.parametrize("suffix", [".mp3", ".MP3"], ids=["mp3", "upper-mp3"])
def test_ac_142_4_an_mp3_source_is_not_converted(tmp_path: Path, suffix: str) -> None:
    stack = _stack(tmp_path, suffix=suffix)
    job = _run(stack)
    assert stack.media.calls == []
    assert len(stack.youtube.written) == 1
    assert job.status is DownloadStatus.Done
    assert job.file_path == stack.youtube.written[0]
    assert stack.youtube.written[0].read_bytes() == SOURCE_BYTES


# --- AC-142.5 MP3_RESERVE ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("present", "expected"),
    [((), "a.mp3"), (("a.mp3",), "a-2.mp3"), (("a.mp3", "a-2.mp3"), "a-3.mp3")],
    ids=["free", "a-taken", "a-and-a2-taken"],
)
def test_ac_142_5_mp3_name_never_reused(
    tmp_path: Path, present: tuple[str, ...], expected: str
) -> None:
    stack = _stack(tmp_path)
    kept = {name: f"existing {name}".encode() for name in present}
    for name, data in kept.items():
        (stack.folder / name).write_bytes(data)
    job = _run(stack)
    assert len(stack.media.calls) == 1
    output = stack.media.calls[0][1]
    assert output == stack.folder / expected
    assert output.name not in kept
    assert job.file_path == stack.folder / expected
    assert {name: (stack.folder / name).read_bytes() for name in kept} == kept


# --- AC-142.6 CONVERT_DONE ---------------------------------------------------------------


class TraceUnitOfWork(FakeUnitOfWork):
    """Records each commit's job state, archive state and whether the source still exists."""

    def __init__(self) -> None:
        super().__init__()
        self.trace: list[tuple[Any, ...]] | None = None
        self.source: Callable[[], Path | None] = lambda: None

    def commit(self) -> None:
        super().commit()
        if self.trace is None:
            return
        jobs = self.downloads.list_ordered()
        assert len(jobs) == 1
        job = jobs[0]
        if job.status is not DownloadStatus.Done:
            self.trace.append(("commit", job.status.name))
            return
        source = self.source()
        self.trace.append(
            (
                "commit",
                job.status.name,
                job.file_path,
                job.file_size,
                job.progress,
                job.received_height,
                len(self.archive.list()),
                source is not None and source.exists(),
            )
        )


class TraceLog:
    """Stands in for the module logger so log lines join the same trace."""

    def __init__(self, trace: list[tuple[Any, ...]], source: Callable[[], Path | None]) -> None:
        self._trace = trace
        self._source = source

    def _record(self, event: str, **_fields: object) -> None:
        source = self._source()
        self._trace.append(("log", event, source is not None and source.exists()))

    info = warning = error = debug = _record


def test_ac_142_6_one_job_traced_from_download_to_source_removal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    uow = TraceUnitOfWork()
    stack = _stack(tmp_path, uow=uow)

    def source() -> Path | None:
        return stack.youtube.written[0] if stack.youtube.written else None

    def status_inside() -> str:
        with stack.factory() as current:
            jobs = current.downloads.list_ordered()
        assert len(jobs) == 1
        return jobs[0].status.name

    added = _add(stack)
    trace: list[tuple[Any, ...]] = []
    uow.trace, uow.source = trace, source
    stack.youtube.trace = trace
    stack.media.trace, stack.media.status_inside = trace, status_inside
    monkeypatch.setattr(download_mod, "log", TraceLog(trace, source))
    _drain(stack)

    mp3 = stack.folder / "a.mp3"
    assert trace == [
        ("commit", "Downloading"),
        ("log", "download.started", False),
        ("download",),
        ("convert", "Downloading"),
        ("commit", "Done", mp3, len(MP3_BYTES), 1.0, None, 1, True),
        ("log", "download.done", True),
    ]
    assert not (stack.folder / "a.m4a").exists()
    assert mp3.read_bytes() == MP3_BYTES
    job = _job(stack, added.id)
    assert job is not None
    assert (job.status, job.file_path) == (DownloadStatus.Done, mp3)


# --- AC-142.7 NO_CONVERSION_ROW ----------------------------------------------------------


def test_ac_142_7_sqlite_job_ends_done_with_no_conversion_row(tmp_path: Path) -> None:
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    out = tmp_path / "out"
    out.mkdir()
    youtube = SourceYouTube(out, ".m4a", "a")
    media = RecordingMedia()
    service = DownloadService(
        factory,
        youtube=youtube,
        media=media,
        coordinator=ExtractCoordinator(youtube),
        settings=SettingsService(factory),
        sleep=lambda _seconds: None,
    )
    youtube.service = service
    try:
        stack = Stack(service, youtube, media, factory, out, SettingsService(factory))
        job = _run(stack)
        assert job.status is DownloadStatus.Done
        assert job.file_path == out / "a.mp3"
        with factory() as uow:
            assert uow.conversion_jobs.list_ordered() == []
    finally:
        engine.dispose()


# --- AC-142.8 any cookie mode ------------------------------------------------------------


@pytest.mark.parametrize("mode", ["none", "browser", "file"])
def test_ac_142_8_the_convert_runs_in_every_cookie_mode(tmp_path: Path, mode: str) -> None:
    stack = _stack(tmp_path)
    stack.settings.set("downloader", "cookie_mode", mode)
    if mode == "file":
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        stack.settings.set("downloader", "cookie_file_path", str(cookie_file))
    job = _run(stack)
    assert stack.youtube.last_options is not None
    assert stack.youtube.last_options.mode == mode
    assert len(stack.media.calls) == 1
    assert job.status is DownloadStatus.Done
    assert job.file_path == stack.folder / "a.mp3"


# --- AC-142.9 no ffmpeg ------------------------------------------------------------------


def test_ac_142_9_no_ffmpeg_fails_with_its_card_and_keeps_the_source(tmp_path: Path) -> None:
    media = RecordingMedia(error=lambda _i, _o: FFmpegNotFoundError("ffmpeg binary was not found"))
    stack = _stack(tmp_path, media)
    with capture_logs() as logs:
        job = _run(stack)
    assert len(media.calls) == 1
    assert job.status is DownloadStatus.Failed
    assert job.error_message == NOT_FOUND_CARD
    failed = _events(logs, "download.failed")
    assert len(failed) == 1
    assert failed[0]["error"] == NOT_FOUND_CARD
    assert _events(logs, "download.done") == []
    with stack.factory() as uow:
        assert uow.archive.list() == []
    assert (stack.folder / "a.m4a").read_bytes() == SOURCE_BYTES


# --- AC-142.10 CONVERT_FAIL --------------------------------------------------------------


@pytest.mark.parametrize(
    ("error", "card"),
    [
        (lambda _i, _o: FilesystemError("Conversion failed!"), CONVERT_CARD),
        (lambda _i, _o: PermissionError(13, "Permission denied"), WRITE_CARD),
    ],
    ids=["filesystem-error", "os-error"],
)
def test_ac_142_10_convert_failure_cards(
    tmp_path: Path, error: Callable[[Path, Path], BaseException], card: str
) -> None:
    media = RecordingMedia(error=error)
    stack = _stack(tmp_path, media)
    with capture_logs() as logs:
        job = _run(stack)
    assert len(media.calls) == 1
    assert (job.status, job.error_message) == (DownloadStatus.Failed, card)
    failed = _events(logs, "download.failed")
    assert len(failed) == 1
    assert failed[0]["error"] == card
    with stack.factory() as uow:
        assert uow.archive.list() == []


# --- AC-142.11 SOURCE_KEPT ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("error", "partial"),
    [
        (lambda _i, _o: FFmpegNotFoundError("ffmpeg binary was not found"), False),
        (lambda _i, _o: FilesystemError("Conversion failed!"), True),
        (lambda _i, _o: OSError(28, "No space left on device"), True),
    ],
    ids=["not-found", "fs-partial", "os-partial"],
)
def test_ac_142_11_failed_convert_keeps_source(
    tmp_path: Path, error: Callable[[Path, Path], BaseException], partial: bool
) -> None:
    media = RecordingMedia(error=error, partial=partial)
    stack = _stack(tmp_path, media)
    existing = stack.folder / "a.mp3"
    existing.write_bytes(b"a song that was here first")
    job = _run(stack)
    assert len(media.calls) == 1
    assert media.calls[0][1] == stack.folder / "a-2.mp3"
    assert job.status is DownloadStatus.Failed
    assert (stack.folder / "a.m4a").read_bytes() == SOURCE_BYTES
    assert not (stack.folder / "a-2.mp3").exists()
    assert existing.read_bytes() == b"a song that was here first"
    assert job.file_path is None or job.file_path != stack.folder / "a-2.mp3"


# --- AC-142.12 LAST_LINE -----------------------------------------------------------------

LAST_LINE_CASES: list[tuple[str, str]] = [
    ("first\r\nsecond", "second"),
    ("first\rsecond", "second"),
    ("first\nsecond", "second"),
    ("first\nsec ond", "sec ond"),
    ("first\nsec\x85ond", "sec\x85ond"),
    ("first\nsec\x0cond", "sec\x0cond"),
    ("real line\n\n   \n\x00\x01\x1b[0m\n", "real line"),
    ("first\nbad \ud800 byte", "bad \ud800 byte"),
    ("\x00\x01\n\x1b[0m", ""),
    ("", ""),
]


def test_ac_142_12_last_line_keeps_the_last_readable_line() -> None:
    raised = [text for text, _expected in LAST_LINE_CASES if _raised(lambda t=text: last_line(t))]
    assert raised == []
    got = [last_line(text) for text, _expected in LAST_LINE_CASES]
    assert got == [expected for _text, expected in LAST_LINE_CASES]
    surrogate = scrub_line(last_line("first\nbad \ud800 byte"))
    assert "\ud800" not in surrogate
    assert surrogate.startswith("bad")


# --- AC-142.13 FAIL_DETAIL ---------------------------------------------------------------

SECRET = "S67_SYNTHETIC_SECRET"
HOME_NAME = "S67HOMEMARKER"
BANNER = (
    "ffmpeg version n8.1.3 Copyright (c) 2000-2026 the FFmpeg developers\n"
    "  configuration: --enable-gpl --enable-libmp3lame"
)
ORDINARY_TAIL = "Error opening input files: Invalid data found when processing input"

#: Each case: the exception from (source, mp3, home), and the exact detail for a keep case.
DetailCase = tuple[Callable[[Path, Path, Path], BaseException], str | None]
DETAIL_CASES: dict[str, DetailCase] = {
    "lf_secret_tail": (
        lambda s, m, h: FilesystemError(f"{BANNER}\n{s}\nAuthorization: Bearer\n{SECRET}"),
        None,
    ),
    "cr_secret_tail": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nAuthorization: Bearer\r{SECRET}"),
        None,
    ),
    "crlf_secret_tail": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nAuthorization: Bearer\r\n{SECRET}"),
        None,
    ),
    "needle_split_across_lf": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nAuthor\nization: x\n{SECRET}"),
        None,
    ),
    "home_split_lf": (
        lambda s, m, h: FilesystemError(
            f"{BANNER}\n{str(h)[:-6]}\n{str(h)[-6:]}\\private\\note.txt"
        ),
        None,
    ),
    "forward_slash_path": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nCould not open {s.as_posix()}"),
        None,
    ),
    "mixed_separators": (
        lambda s, m, h: FilesystemError(
            f"{BANNER}\nCould not open " + str(s).replace("\\S67MUSIC\\", "/S67MUSIC\\")
        ),
        None,
    ),
    "escaped_oserror": (
        lambda s, m, h: PermissionError(13, "Permission denied", str(m)),
        None,
    ),
    "folder_only": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nCould not create {s.parent}\\tmp-0001.part"),
        None,
    ),
    "upper_case_path": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nCould not open {str(s).upper()}"),
        None,
    ),
    "ordinary": (
        lambda s, m, h: FilesystemError(
            f"{BANNER}\nInput #0, from '{s}':\n"
            "[in#0 @ 000001] Error opening input: Invalid data found when processing input\n"
            f"Error opening input file {s}.\n{ORDINARY_TAIL}\n"
        ),
        ORDINARY_TAIL,
    ),
    "ordinary_path_tail": (
        lambda s, m, h: FilesystemError(f"{BANNER}\nError opening output file {m}."),
        "Error opening output file [file].",
    ),
}


def _path_forms(path: Path) -> list[str]:
    text = str(path)
    return [text, path.as_posix(), text.replace("\\", "\\\\")]


@pytest.mark.parametrize("case", list(DETAIL_CASES), ids=list(DETAIL_CASES))
def test_ac_142_13_detail_never_leaks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    case: str,
) -> None:
    make_error, keep = DETAIL_CASES[case]
    home = tmp_path / HOME_NAME
    assert hasattr(health_module, "home_folder")
    assert hasattr(health_module, "HOME_IGNORES_CASE")
    monkeypatch.setattr(health_module, "home_folder", lambda: str(home))
    monkeypatch.setattr(health_module, "HOME_IGNORES_CASE", True)
    app = tmp_path / "app"
    health = _health(app)
    folder = home / "S67MUSIC" / "S67CLIPS"
    media = RecordingMedia(error=lambda source, mp3: make_error(source, mp3, home))
    stack = _stack(tmp_path, media, stem="s67clip", folder=folder)
    capsys.readouterr()

    job = _run(stack)
    assert len(media.calls) == 1
    source, mp3, _options = media.calls[0]
    card = WRITE_CARD if case == "escaped_oserror" else CONVERT_CARD
    assert (job.status, job.error_message) == (DownloadStatus.Failed, card)

    rows = [
        e.message for e in health.console_snapshot(0) if e.message.startswith("download.failed")
    ]
    assert len(rows) == 1
    stdout = capsys.readouterr().out
    assert "download.failed" in stdout
    log_path = app / "logs" / "console.log"
    assert log_path.is_file()
    persisted = log_path.read_text(encoding="utf-8")
    assert "download.failed" in persisted

    forbidden = [SECRET, HOME_NAME, "S67HOME", "MARKER", "s67clip", "S67CLIPS", "S67MUSIC"]
    for path in (home, source.parent, source, mp3, tmp_path):
        forbidden.extend(_path_forms(path))
    surfaces = {"console": rows[0], "stdout": stdout, "console.log": persisted, "card": card}
    leaks = sorted(
        (where, word)
        for where, text in surfaces.items()
        for word in forbidden
        if word.casefold() in text.casefold()
    )
    assert leaks == []
    if keep is not None:
        assert rows[0].endswith(f" detail={keep}"), rows[0]
        assert "[REDACTED]" not in rows[0]


@pytest.mark.parametrize("numbered", [False, True], ids=["first-name", "numbered-name"])
def test_ac_142_13_reserve_failure_never_leaks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    numbered: bool,
) -> None:
    """Execution review F1: `_reserve` failing on the name it tried (a folder of that name on
    Windows, or a denied create) keeps the source and any existing MP3, and the detail names
    neither the tried MP3 nor its folder on any surface."""
    home = tmp_path / HOME_NAME
    monkeypatch.setattr(health_module, "home_folder", lambda: str(home))
    monkeypatch.setattr(health_module, "HOME_IGNORES_CASE", True)
    app = tmp_path / "app"
    health = _health(app)
    folder = home / "S67MUSIC" / "S67CLIPS"
    media = RecordingMedia()
    stack = _stack(tmp_path, media, stem="s67clip", folder=folder)
    existing = folder / "s67clip.mp3"
    if numbered:
        existing.write_bytes(b"an mp3 that was here first")
    tried: list[Path] = []
    real_open = Path.open

    def denied_open(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> IO[Any]:
        if mode == "xb" and self.suffix == ".mp3" and not self.exists():
            tried.append(self)
            raise PermissionError(13, "Permission denied", str(self))
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied_open)
    capsys.readouterr()

    job = _run(stack)
    assert media.calls == []
    assert len(tried) == 1
    assert tried[0].name == ("s67clip-2.mp3" if numbered else "s67clip.mp3")
    assert (job.status, job.error_message) == (DownloadStatus.Failed, WRITE_CARD)
    assert (folder / "s67clip.m4a").read_bytes() == SOURCE_BYTES
    if numbered:
        assert existing.read_bytes() == b"an mp3 that was here first"

    rows = [
        e.message for e in health.console_snapshot(0) if e.message.startswith("download.failed")
    ]
    assert len(rows) == 1
    stdout = capsys.readouterr().out
    assert "download.failed" in stdout
    log_path = app / "logs" / "console.log"
    assert log_path.is_file()
    persisted = log_path.read_text(encoding="utf-8")
    assert "download.failed" in persisted

    forbidden = [HOME_NAME, "S67HOME", "MARKER", "s67clip", "S67CLIPS", "S67MUSIC"]
    for path in (home, folder, folder / "s67clip.m4a", tried[0], tmp_path):
        forbidden.extend(_path_forms(path))
    surfaces = {"console": rows[0], "stdout": stdout, "console.log": persisted}
    leaks = sorted(
        (where, word)
        for where, text in surfaces.items()
        for word in forbidden
        if word.casefold() in text.casefold()
    )
    assert leaks == []
    assert rows[0].endswith(" detail=[Errno 13] Permission denied: '[file]'"), rows[0]


# --- AC-142.14 ROW_GONE ------------------------------------------------------------------


@pytest.mark.parametrize("how", ["remove", "clear"])
def test_ac_142_14_row_gone_keeps_both_files(tmp_path: Path, how: str) -> None:
    holder: dict[str, Stack] = {}
    added: dict[str, str] = {}

    def remove_row(_source: Path, _mp3: Path) -> None:
        service = holder["stack"].service
        if how == "remove":
            service.remove_from_queue(added["id"])
        else:
            service.clear_queue()

    media = RecordingMedia(on_convert=remove_row)
    stack = _stack(tmp_path, media)
    holder["stack"] = stack
    added["id"] = _add(stack).id
    _drain(stack)
    assert len(media.calls) == 1
    assert _job(stack, added["id"]) is None
    assert stack.service.get_queue() == []
    assert (stack.folder / "a.m4a").read_bytes() == SOURCE_BYTES
    assert (stack.folder / "a.mp3").read_bytes() == MP3_BYTES


# --- AC-142.15 KEPT_LOGS -----------------------------------------------------------------


@pytest.fixture
def handles() -> Iterator[list[IO[bytes]]]:
    """Open files a fake holds; on Windows an open file cannot be unlinked (CI is Windows)."""
    held: list[IO[bytes]] = []
    yield held
    for handle in held:
        handle.close()


def _no_path(entry: dict[str, Any], folder: Path) -> bool:
    text = " ".join(str(value) for value in entry.values()).casefold()
    return all(form.casefold() not in text for form in _path_forms(folder)) and (
        "a.m4a" not in text and "a.mp3" not in text
    )


def test_ac_142_15_source_kept_is_logged(tmp_path: Path, handles: list[IO[bytes]]) -> None:
    media = RecordingMedia(on_convert=lambda source, _mp3: handles.append(source.open("rb")))
    stack = _stack(tmp_path, media)
    with capture_logs() as logs:
        job = _run(stack)
    assert len(media.calls) == 1
    assert (job.status, job.file_path) == (DownloadStatus.Done, stack.folder / "a.mp3")
    kept = _events(logs, "download.source_kept")
    assert len(kept) == 1
    assert kept[0]["log_level"] == "warning"
    assert (kept[0]["job_id"], kept[0]["video_id"]) == (job.id, "vid1")
    assert kept[0]["error"] == "PermissionError"
    assert _no_path(kept[0], stack.folder)
    assert (stack.folder / "a.m4a").exists()


def test_ac_142_15_partial_kept_is_logged(tmp_path: Path, handles: list[IO[bytes]]) -> None:
    def hold_partial(_source: Path, mp3: Path) -> None:
        mp3.write_bytes(b"partial mp3")
        handles.append(mp3.open("rb"))

    media = RecordingMedia(
        error=lambda _i, _o: FilesystemError("Conversion failed!"), on_convert=hold_partial
    )
    stack = _stack(tmp_path, media)
    with capture_logs() as logs:
        job = _run(stack)
    assert len(media.calls) == 1
    assert job.status is DownloadStatus.Failed
    kept = _events(logs, "download.partial_kept")
    assert len(kept) == 1
    assert kept[0]["log_level"] == "warning"
    assert (kept[0]["job_id"], kept[0]["video_id"]) == (job.id, "vid1")
    assert kept[0]["error"] == "PermissionError"
    assert _no_path(kept[0], stack.folder)
    assert _events(logs, "download.source_kept") == []


def test_ac_142_15_no_kept_warning_on_removal(tmp_path: Path) -> None:
    stack = _stack(tmp_path)
    with capture_logs() as logs:
        job = _run(stack)
    assert len(stack.media.calls) == 1
    assert job.status is DownloadStatus.Done
    assert _events(logs, "download.source_kept") == []
    assert _events(logs, "download.partial_kept") == []
    assert not (stack.folder / "a.m4a").exists()


# --- AC-142.16 CONVERT_CANCEL ------------------------------------------------------------


def test_ac_142_16_cancel_before_not_inside_convert(tmp_path: Path) -> None:
    # Guard, holds at baseline: a cancel during the download ends Cancelled, no convert.
    early = _stack(tmp_path / "early")
    early.youtube.on_download = early.service.cancel_processing
    cancelled = _run(early)
    assert cancelled.status is DownloadStatus.Cancelled
    assert early.media.calls == []

    holder: dict[str, Stack] = {}
    media = RecordingMedia(on_convert=lambda _s, _m: holder["stack"].service.cancel_processing())
    late = _stack(tmp_path / "late", media)
    holder["stack"] = late
    first = _add(late, "vid1")
    second = _add(late, "vid2")
    _drain(late)
    assert len(media.calls) == 1
    done = _job(late, first.id)
    waiting = _job(late, second.id)
    assert done is not None and waiting is not None
    assert (done.status, done.file_path) == (DownloadStatus.Done, late.folder / "a.mp3")
    assert waiting.status is DownloadStatus.Pending
    assert len(late.youtube.written) == 1
    assert late.service.get_processor_state().state is QueueProcessorState.Idle


# --- AC-142.18 the real adapter with no FFmpeg -------------------------------------------


def test_ac_142_18_real_adapter_no_ffmpeg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.media import adapter as media_adapter
    from avkit_infra.media.adapter import FFmpegAdapter

    assert media_adapter.shutil is shutil
    monkeypatch.setattr(media_adapter.shutil, "which", lambda _name: None)
    adapter = FFmpegAdapter(
        configured_source=lambda: None, bundle_path=tmp_path / "missing" / "ffmpeg.exe"
    )
    assert adapter.ffmpeg_binaries() is None
    stack = _stack(tmp_path, adapter)
    job = _run(stack)
    assert (job.status, job.error_message) == (DownloadStatus.Failed, NOT_FOUND_CARD)
    assert (stack.folder / "a.m4a").read_bytes() == SOURCE_BYTES
    assert not (stack.folder / "a.mp3").exists()
