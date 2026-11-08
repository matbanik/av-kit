"""MEU-123 real-FFmpeg Extract tests (AC-123.9 to AC-123.13): audio positions, pinned FFmpeg.

The clips are generated with lavfi in a temp folder and never committed (D-371). CI deselects
this module, because the pinned binaries are fetched, not tracked (CI_DESELECT).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from tests.tts_asset_fakes import FakeAssets, idle_runtime
from tests.unit.test_services import FakeMedia, FakeUnitOfWork, FakeYouTube, SharedFakeFactory

from avkit_core.domain.enums import ConversionKind, ConversionStatus
from avkit_core.services.conversion import ConversionAddSpec, ConversionService
from avkit_core.services.health import HealthService
from avkit_core.services.settings import SettingsService
from avkit_infra.database.engine import create_session_factory, create_sqlite_engine, init_schema
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork
from avkit_infra.media.adapter import FFmpegAdapter

REPO_ROOT = Path(__file__).resolve().parents[2]
FFMPEG = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg.exe"
FFPROBE = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffprobe.exe"
#: In the clip folder's name, so AC-123.13 can find any clip path that reaches a surface.
MARKER = "s54_extract_marker"
#: Each clip's audio codecs, in stream order after the picture.
CLIPS: dict[str, tuple[str, ...]] = {
    "one_track": ("aac",),
    "two_track": ("aac", "ac3"),
    "no_audio": (),
}


def _assert_pinned() -> None:
    for binary in (FFMPEG, FFPROBE):
        assert binary.is_file() and binary.stat().st_size > 1024, (
            f"packaging/ffmpeg-win64/{binary.name} is missing or a stub; "
            "run tools/fetch_ffmpeg_windows.ps1"
        )


@pytest.fixture(scope="module")
def clips(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    _assert_pinned()
    folder = tmp_path_factory.mktemp(MARKER)
    made: dict[str, Path] = {}
    for name, codecs in CLIPS.items():
        argv = [str(FFMPEG), "-hide_banner", "-nostdin", "-y"]
        argv += ["-f", "lavfi", "-i", "testsrc=size=64x64:rate=10:duration=1"]
        for number in range(len(codecs)):
            argv += ["-f", "lavfi", "-i", f"sine=frequency={440 * (number + 1)}:duration=1"]
        argv += ["-map", "0:v"]
        for number in range(len(codecs)):
            argv += ["-map", f"{number + 1}:a"]
        argv += ["-c:v", "mpeg4", "-pix_fmt", "yuv420p"]
        for number, codec in enumerate(codecs):
            argv += [f"-c:a:{number}", codec]
        made[name] = folder / f"{name}.mp4"
        argv += ["-shortest", str(made[name])]
        subprocess.run(argv, check=True, capture_output=True, timeout=60)
    return made


class CountingAdapter(FFmpegAdapter):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.extract_calls = 0

    def extract_stream(self, *args: object, **kwargs: object) -> None:
        self.extract_calls += 1
        super().extract_stream(*args, **kwargs)  # type: ignore[arg-type]


def _stack(tmp_path: Path, media: FFmpegAdapter) -> tuple[ConversionService, HealthService]:
    """AC-115.19's HealthService first (D-376), then AC-30.12's real database stack."""
    fakes = SharedFakeFactory(FakeUnitOfWork())
    health_settings = SettingsService(fakes)
    health_settings.set("app", "log_to_file", True)
    health = HealthService(
        fakes,
        app_data=tmp_path / "app",
        settings=health_settings,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
    )
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    settings.set("converter", "output_dir", str(tmp_path / "out"))
    settings.set("converter", "skip_existing", False)
    return ConversionService(factory, media=media, settings=settings), health


def _process(service: ConversionService) -> None:
    service.start_processing()
    thread = service._thread
    if thread is not None:
        thread.join(timeout=60)
        assert not thread.is_alive()


def _streams(path: Path) -> list[tuple[int, str, str]]:
    info = FFmpegAdapter(configured_path=FFMPEG).probe(path)
    return [
        (stream.index, stream.codec_type, stream.codec_name)  # type: ignore[attr-defined]
        for stream in info.streams or []
    ]


def _console_text(app_data: Path) -> str:
    path = app_data / "logs" / "console.log"
    return path.read_text(encoding="utf-8") if path.exists() else ""


@pytest.mark.integration
def test_ac_123_9_pinned_ffmpeg_and_fixtures(clips: dict[str, Path]) -> None:
    _assert_pinned()
    binaries = FFmpegAdapter(configured_path=FFMPEG).ffmpeg_binaries()
    assert binaries is not None
    assert (binaries.ffmpeg, binaries.ffprobe) == (FFMPEG, FFPROBE)
    assert {name: _streams(path) for name, path in clips.items()} == {
        "one_track": [(0, "video", "mpeg4"), (1, "audio", "aac")],
        "two_track": [(0, "video", "mpeg4"), (1, "audio", "aac"), (2, "audio", "ac3")],
        "no_audio": [(0, "video", "mpeg4")],
    }


@pytest.mark.parametrize("name", ["one_track", "two_track"])
@pytest.mark.integration
def test_ac_123_10_first_mode_real_ffmpeg(
    name: str, clips: dict[str, Path], tmp_path: Path
) -> None:
    service, _health = _stack(tmp_path, FFmpegAdapter(configured_path=FFMPEG))
    jobs = service.add_to_queue([clips[name]], ConversionAddSpec(kind=ConversionKind.Extract))
    assert [(job.stream_index, job.output_path.name) for job in jobs] == [(0, f"{name}_a.m4a")]
    _process(service)
    done = service.get_queue()
    assert [(job.status, job.error_message, job.gpu_encoder) for job in done] == [
        (ConversionStatus.Done, None, None)
    ]
    assert _streams(done[0].output_path) == [(0, "audio", "aac")]


@pytest.mark.parametrize("name", ["one_track", "two_track"])
@pytest.mark.integration
def test_ac_123_11_all_mode_real_ffmpeg(name: str, clips: dict[str, Path], tmp_path: Path) -> None:
    expected = {
        "one_track": [(0, "one_track_a.m4a", "aac")],
        "two_track": [(0, "two_track_a0.m4a", "aac"), (1, "two_track_a1.ac3", "ac3")],
    }[name]
    service, _health = _stack(tmp_path, FFmpegAdapter(configured_path=FFMPEG))
    jobs = service.add_to_queue(
        [clips[name]], ConversionAddSpec(kind=ConversionKind.Extract, stream_mode="all")
    )
    assert [(job.stream_index, job.output_path.name) for job in jobs] == [
        (index, file_name) for index, file_name, _codec in expected
    ]
    _process(service)
    done = service.get_queue()
    assert [(job.status, job.error_message, job.gpu_encoder) for job in done] == [
        (ConversionStatus.Done, None, None) for _ in expected
    ]
    assert [_streams(job.output_path) for job in done] == [
        [(0, "audio", codec)] for _index, _name, codec in expected
    ]


@pytest.mark.parametrize("mode", ["first", "all"])
@pytest.mark.integration
def test_ac_123_12_no_audio_fails_at_add(mode: str, clips: dict[str, Path], tmp_path: Path) -> None:
    media = CountingAdapter(configured_path=FFMPEG)
    service, _health = _stack(tmp_path, media)
    jobs = service.add_to_queue(
        [clips["no_audio"]], ConversionAddSpec(kind=ConversionKind.Extract, stream_mode=mode)
    )
    assert [(job.status, job.error_message) for job in jobs] == [
        (ConversionStatus.Failed, "the file has no audio track")
    ]
    _process(service)
    assert [job.status for job in service.get_queue()] == [ConversionStatus.Failed]
    assert not jobs[0].output_path.exists()
    assert media.extract_calls == 0


@pytest.mark.integration
def test_ac_123_13_no_fixture_path_reaches_console(
    clips: dict[str, Path],
    tmp_path: Path,
    tmp_path_factory: pytest.TempPathFactory,
    capfd: pytest.CaptureFixture[str],
) -> None:
    service, health = _stack(tmp_path, FFmpegAdapter(configured_path=FFMPEG))
    service.add_to_queue([clips["one_track"]], ConversionAddSpec(kind=ConversionKind.Extract))
    _process(service)
    assert [job.status for job in service.get_queue()] == [ConversionStatus.Done]
    captured = capfd.readouterr()
    ring = [event.message for event in health.console_snapshot(0)]
    surfaces = {
        "stdout": captured.out,
        "stderr": captured.err,
        "ring": "\n".join(ring),
        "file": _console_text(tmp_path / "app"),
    }
    base = str(tmp_path_factory.getbasetemp())
    needles = (MARKER, base, base.replace("\\", "/"), json.dumps(base)[1:-1])
    leaks = {
        surface: sorted({needle for needle in needles if needle.lower() in text.lower()})
        for surface, text in surfaces.items()
    }
    assert leaks == {surface: [] for surface in surfaces}
    assert [
        any(message.startswith(event) for message in ring)
        for event in ("engine.created", "convert.finished")
    ] == [True, True]
