"""MEU-133 ConversionService.probe_file (Session 62): PROBE_MAP with a recording fake MediaPort.

Imports of the new names stay inside the tests, so a missing name fails one test, never the
collection. The probe writes no job and starts nothing.
"""

from __future__ import annotations

import dataclasses
import traceback
from pathlib import Path

import pytest
from tests.unit.test_conversion_service import FakeUnitOfWork, SharedFakeFactory

from avkit_core.domain.errors import FFmpegNotFoundError, MediaProbeError, ValidationError
from avkit_core.domain.progress import MediaInfo

MARKER = "s62PROBEMARKER"
MP4 = "mov,mp4,m4a,3gp,3g2,mj2"
FIELDS = (
    "path",
    "duration_ms",
    "timecode",
    "container",
    "video_codec",
    "audio_codec",
    "width",
    "height",
    "fps",
    "has_video",
    "has_audio",
)


def _info(**changes: object) -> MediaInfo:
    base = MediaInfo(
        duration=3.0,
        container=MP4,
        video_codec="h264",
        audio_codec="aac",
        sample_rate=48000,
        channels=2,
        width=320,
        height=240,
        fps=25.0,
    )
    return dataclasses.replace(base, **changes)  # type: ignore[arg-type]


class RecordingProbeMedia:
    """A MediaPort whose probe records each call and answers or raises as told."""

    def __init__(self, *, info: MediaInfo | None = None, error: Exception | None = None) -> None:
        self.info = info or _info()
        self.error = error
        self.calls: list[tuple[Path, dict[str, object]]] = []
        self.other_calls: list[str] = []

    def probe(self, file_path: Path, **kwargs: object) -> MediaInfo:
        self.calls.append((file_path, dict(kwargs)))
        if self.error is not None:
            raise self.error
        return self.info

    def __getattr__(self, name: str) -> object:
        self.other_calls.append(name)
        raise AttributeError(name)


def _service(media: RecordingProbeMedia) -> tuple[object, FakeUnitOfWork]:
    from avkit_core.services.conversion import ConversionService
    from avkit_core.services.settings import SettingsService

    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    return ConversionService(factory, media=media, settings=settings), uow  # type: ignore[arg-type]


def _clip(tmp_path: Path, name: str = "clip.mp4") -> Path:
    clip = tmp_path / name
    clip.write_bytes(b"video")
    return clip


def test_ac_133_3_the_eleven_fields_come_from_the_probe(tmp_path: Path) -> None:
    media = RecordingProbeMedia()
    service, _uow = _service(media)
    clip = _clip(tmp_path)
    (tmp_path / "sub").mkdir()
    result = service.probe_file(str(tmp_path / "sub" / ".." / "clip.mp4"))  # type: ignore[attr-defined]
    assert tuple(field.name for field in dataclasses.fields(result)) == FIELDS
    assert dataclasses.asdict(result) == {
        "path": str(clip.resolve()),
        "duration_ms": 3000,
        "timecode": "00:00:03.000",
        "container": MP4,
        "video_codec": "h264",
        "audio_codec": "aac",
        "width": 320,
        "height": 240,
        "fps": 25.0,
        "has_video": True,
        "has_audio": True,
    }
    assert media.calls == [(clip.resolve(), {})]


@pytest.mark.parametrize(
    "video,audio,has_video,has_audio",
    [
        ("h264", None, True, False),
        (None, "aac", False, True),
        (None, None, False, False),
        ("hevc", "opus", True, True),
    ],
    ids=["video-only", "audio-only", "neither", "both"],
)
def test_ac_133_3_streams_follow_the_codecs(
    tmp_path: Path, video: str | None, audio: str | None, has_video: bool, has_audio: bool
) -> None:
    media = RecordingProbeMedia(info=_info(video_codec=video, audio_codec=audio))
    service, _uow = _service(media)
    clip = _clip(tmp_path)
    result = service.probe_file(str(clip))  # type: ignore[attr-defined]
    assert (result.video_codec, result.audio_codec) == (video, audio)
    assert (result.has_video, result.has_audio) == (has_video, has_audio)
    assert len(media.calls) == 1


def test_ac_133_3_no_duration_gives_null_duration_and_timecode(tmp_path: Path) -> None:
    media = RecordingProbeMedia(info=_info(duration=None, container="h264", audio_codec=None))
    service, _uow = _service(media)
    clip = _clip(tmp_path, "raw.h264")
    result = service.probe_file(str(clip))  # type: ignore[attr-defined]
    assert (result.duration_ms, result.timecode) == (None, None)
    assert (result.container, result.has_video, result.has_audio) == ("h264", True, False)
    assert result.path == str(clip.resolve())


def test_ac_133_3_a_probe_failure_names_nothing(tmp_path: Path) -> None:
    media = RecordingProbeMedia(error=MediaProbeError(f"{MARKER}: Invalid data found"))
    service, _uow = _service(media)
    clip = _clip(tmp_path)
    with pytest.raises(ValidationError) as caught:
        service.probe_file(str(clip))  # type: ignore[attr-defined]
    error = caught.value
    assert str(error) == "the file could not be probed"
    assert error.__cause__ is None
    assert error.__context__ is None
    assert MARKER not in "".join(traceback.format_exception(error))
    assert len(media.calls) == 1


def test_ac_133_3_ffmpeg_not_found_passes_through(tmp_path: Path) -> None:
    missing = FFmpegNotFoundError("ffprobe binary was not found")
    media = RecordingProbeMedia(error=missing)
    service, _uow = _service(media)
    clip = _clip(tmp_path)
    with pytest.raises(FFmpegNotFoundError) as caught:
        service.probe_file(str(clip))  # type: ignore[attr-defined]
    assert caught.value is missing


def test_ac_133_3_no_job_is_written_and_the_queue_is_unchanged(tmp_path: Path) -> None:
    media = RecordingProbeMedia()
    service, uow = _service(media)
    clip = _clip(tmp_path)
    commits = uow.commits
    result = service.probe_file(str(clip))  # type: ignore[attr-defined]
    assert result.has_video is True
    assert uow.conversion_jobs.rows == {}
    assert service.get_queue() == []  # type: ignore[attr-defined]
    assert uow.commits == commits
    assert getattr(service, "_thread", None) is None
    assert media.other_calls == []
    assert clip.read_bytes() == b"video"


def test_ac_133_3_a_refused_path_is_never_probed(tmp_path: Path) -> None:
    media = RecordingProbeMedia()
    service, _uow = _service(media)
    with pytest.raises(ValidationError) as caught:
        service.probe_file(str(tmp_path / f"missing-{MARKER}.mp4"))  # type: ignore[attr-defined]
    assert str(caught.value) == "video file not found"
    assert media.calls == []
