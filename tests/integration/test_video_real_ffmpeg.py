"""MEU-133 and MEU-134 real-FFmpeg tests (Session 62): probe and frames on the pinned FFmpeg.

The clips are generated with lavfi in a module temp folder and never committed (D-584). CI
deselects this module, because the pinned binaries are fetched, not tracked. Every source
clip's SHA-256 is the same after the module's calls: the video is read in place, never changed.
"""

from __future__ import annotations

import dataclasses
import hashlib
import io
import shutil
import subprocess
from pathlib import Path

import pytest
from PIL import Image
from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

from avkit_core.domain.errors import ValidationError
from avkit_core.services.capture import CaptureService
from avkit_core.services.conversion import ConversionService
from avkit_core.services.settings import SettingsService
from avkit_infra.capture.adapter import CaptureAdapter
from avkit_infra.media.adapter import FFmpegAdapter

REPO_ROOT = Path(__file__).resolve().parents[2]
FFMPEG = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg.exe"
FFPROBE = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffprobe.exe"
#: In the clip folder's name, so a test can find any clip path that reaches a surface.
MARKER = "s62_video_marker"
MP4 = "mov,mp4,m4a,3gp,3g2,mj2"
COUNTER = ["-f", "lavfi", "-i", "testsrc2=size=320x240:rate=25:duration=3"]
SINE = ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=3.5"]
X264 = ["-c:v", "libx264", "-g", "250", "-pix_fmt", "yuv420p"]
#: The probe scripts' generators (D-584): each clip's lavfi inputs and encoder arguments.
CLIPS: dict[str, list[str]] = {
    # 25 fps CFR counter, 3 s of video; the 3.5 s sine is cut to the video by -shortest.
    "counter.mp4": [*COUNTER, *SINE, *X264, "-c:a", "aac", "-shortest"],
    # The same, with the audio running on to 3.5 s past the video's 3.0 s.
    "long_audio.mp4": [*COUNTER, *SINE, *X264, "-c:a", "aac"],
    "no_audio.mp4": [*COUNTER, *X264],
    # Variable frame rate: 25 frames at 0.04 s, then the rest at 0.1 s.
    "vfr.mkv": [
        *COUNTER,
        "-vf",
        "setpts='if(lt(N,25),N*0.04,1+(N-25)*0.1)/TB'",
        "-fps_mode",
        "passthrough",
        *X264,
    ],
    # A raw H.264 stream: no container, so no duration.
    "raw.h264": [*COUNTER, *X264, "-f", "h264"],
}
#: Under D-573 A: a path ffprobe's JSON echoes, and a tag, each outside cp1252.
L_STROKE_PATH = "Łodz.mp4"
L_STROKE_TAG = "tagged.mp4"


def _assert_pinned() -> None:
    for binary in (FFMPEG, FFPROBE):
        assert binary.is_file() and binary.stat().st_size > 1024, (
            f"packaging/ffmpeg-win64/{binary.name} is missing or a stub; "
            "run tools/fetch_ffmpeg_windows.ps1"
        )


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def clips(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    _assert_pinned()
    folder = tmp_path_factory.mktemp(MARKER)
    made: dict[str, Path] = {}
    for name, argv in CLIPS.items():
        made[name] = folder / name
        command = [str(FFMPEG), "-hide_banner", "-nostdin", "-y", *argv, str(made[name])]
        subprocess.run(command, check=True, capture_output=True, timeout=120)
    made[L_STROKE_PATH] = folder / L_STROKE_PATH
    shutil.copyfile(made["counter.mp4"], made[L_STROKE_PATH])
    made[L_STROKE_TAG] = folder / L_STROKE_TAG
    tag = ["-metadata", "title=Ł会\U0001f600", "-metadata:s:v:0", "handler_name=Łens"]
    command = [str(FFMPEG), "-hide_banner", "-nostdin", "-y", "-i", str(made["counter.mp4"])]
    command += ["-c", "copy", *tag, str(made[L_STROKE_TAG])]
    subprocess.run(command, check=True, capture_output=True, timeout=120)
    return made


@pytest.fixture(scope="module")
def hashes(clips: dict[str, Path]) -> dict[str, str]:
    return {name: _sha(path) for name, path in clips.items()}


def _service() -> ConversionService:
    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    media = FFmpegAdapter(configured_path=FFMPEG)
    return ConversionService(factory, media=media, settings=settings)


def _probe(path: Path) -> dict[str, object]:
    before = _sha(path)
    result = _service().probe_file(str(path))
    assert _sha(path) == before
    return dataclasses.asdict(result)


@pytest.mark.integration
def test_ac_133_7_counter_clip_with_audio(clips: dict[str, Path], hashes: dict[str, str]) -> None:
    clip = clips["counter.mp4"]
    assert _probe(clip) == {
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


@pytest.mark.integration
def test_ac_133_7_counter_clip_with_no_audio(
    clips: dict[str, Path], hashes: dict[str, str]
) -> None:
    probe = _probe(clips["no_audio.mp4"])
    assert (probe["duration_ms"], probe["width"], probe["height"]) == (3000, 320, 240)
    assert (probe["has_video"], probe["has_audio"], probe["audio_codec"]) == (True, False, None)


@pytest.mark.integration
def test_ac_133_7_raw_stream_has_no_duration(
    clips: dict[str, Path], hashes: dict[str, str]
) -> None:
    probe = _probe(clips["raw.h264"])
    assert (probe["duration_ms"], probe["timecode"]) == (None, None)
    assert (probe["container"], probe["video_codec"]) == ("h264", "h264")
    assert (probe["has_video"], probe["has_audio"]) == (True, False)
    assert (probe["width"], probe["height"]) == (320, 240)


@pytest.mark.integration
@pytest.mark.parametrize("name", [L_STROKE_PATH, L_STROKE_TAG], ids=["path", "tag"])
def test_ac_133_7_l_stroke_outside_cp1252(
    clips: dict[str, Path], hashes: dict[str, str], name: str
) -> None:
    clip = clips[name]
    probe = _probe(clip)
    assert probe["path"] == str(clip.resolve())
    assert (probe["duration_ms"], probe["timecode"]) == (3000, "00:00:03.000")
    assert (probe["has_video"], probe["has_audio"]) == (True, True)
    assert (probe["width"], probe["height"], probe["fps"]) == (320, 240, 25.0)


@pytest.mark.integration
def test_ac_133_7_every_clip_is_unchanged(clips: dict[str, Path], hashes: dict[str, str]) -> None:
    for path in clips.values():
        _probe(path)
    assert {name: _sha(path) for name, path in clips.items()} == hashes
    assert sorted(path.name for path in clips["counter.mp4"].parent.iterdir()) == sorted(clips)


# MEU-134 frames on the pinned FFmpeg (AC-134.10, AC-134.11) ----------------------------------


class RecordingFrames:
    """The real adapter, with each `grab_frame` call counted."""

    def __init__(self, real: FFmpegAdapter) -> None:
        self._real = real
        self.grabs: list[int] = []

    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> object:
        return self._real.probe(file_path, timeout_s=timeout_s)

    def grab_frame(self, path: Path, time_ms: int, *, seek: str, timeout_s: float) -> bytes:
        self.grabs.append(time_ms)
        return self._real.grab_frame(path, time_ms, seek=seek, timeout_s=timeout_s)  # type: ignore[arg-type]


def _frames_service(inbox: Path) -> tuple[CaptureService, RecordingFrames]:
    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    settings.set("capture", "inbox_dir", str(inbox))
    image = CaptureAdapter(mss_factory=lambda: None, platform="linux")
    frames = RecordingFrames(FFmpegAdapter(configured_path=FFMPEG))
    service = CaptureService(
        factory,
        capture=image,
        annotate=image,
        settings=settings,
        frames=frames,  # type: ignore[arg-type]
    )
    return service, frames


def _reference(clip: Path, index: int) -> bytes:
    """Frame `index` by a full decode: `select=eq(n\\,N)` counts every decoded frame."""
    command = [str(FFMPEG), "-hide_banner", "-nostdin", "-v", "error", "-i", str(clip)]
    command += ["-vf", f"select=eq(n\\,{index})", "-fps_mode", "passthrough"]
    command += ["-frames:v", "1", "-c:v", "png", "-f", "image2pipe", "pipe:1"]
    data = subprocess.run(command, check=True, capture_output=True, timeout=120).stdout
    assert data[:8] == bytes.fromhex("89504e470d0a1a0a")
    return data


def _pixels(data: bytes) -> tuple[tuple[int, int], bytes]:
    with Image.open(io.BytesIO(data)) as image:
        rgb = image.convert("RGB")
        return rgb.size, rgb.tobytes()


def _frame_pts(clip: Path) -> list[float]:
    """Each decoded frame's time, in output order, as ffprobe reads it."""
    command = [str(FFPROBE), "-v", "error", "-select_streams", "v:0"]
    command += ["-show_entries", "frame=pts_time", "-of", "csv=p=0", str(clip)]
    out = subprocess.run(command, check=True, capture_output=True, timeout=120).stdout
    items = (item.strip(",") for item in out.decode("ascii").split())
    return [float(item) for item in items if item]


def _shot_pixels(path: str) -> tuple[tuple[int, int], bytes]:
    return _pixels(Path(path).read_bytes())


@pytest.mark.integration
def test_ac_134_10_counter_clip_frames_match_a_full_decode(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    clip = clips["counter.mp4"]
    service, frames = _frames_service(tmp_path / "inbox")
    result = service.frames_from_video(str(clip), at=[0, 1.0, 1.02, 2.96, 2.999])
    assert len(result.frames) == 5
    assert [frame.time_ms for frame in result.frames] == [0, 1000, 1020, 2960, 2999]
    assert frames.grabs == [0, 1000, 1020, 2960, 2999]
    # The positive control: neighbouring frames differ, so equality picks out one frame.
    assert _pixels(_reference(clip, 25)) != _pixels(_reference(clip, 26))
    for frame, index in zip(result.frames, [0, 25, 26, 74, 74], strict=True):
        assert _shot_pixels(frame.path) == _pixels(_reference(clip, index)), frame.timecode
        assert (frame.width, frame.height) == (320, 240)
    assert Path(result.frames[4].path).name == "counter-t00h00m02.999s.png"


@pytest.mark.integration
@pytest.mark.parametrize(("seconds", "pts"), [(1.05, 1.08), (2.05, 2.08)], ids=["1.05", "2.05"])
def test_ac_134_10_vfr_frames_are_the_next_frame(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path, seconds: float, pts: float
) -> None:
    clip = clips["vfr.mkv"]
    service, _ = _frames_service(tmp_path / "inbox")
    result = service.frames_from_video(str(clip), at=[seconds])
    assert len(result.frames) == 1
    times = _frame_pts(clip)
    index = next(i for i, value in enumerate(times) if value >= seconds - 1e-9)
    assert times[index] == pytest.approx(pts, abs=1e-6)
    assert seconds <= times[index] <= seconds + 0.1
    assert _shot_pixels(result.frames[0].path) == _pixels(_reference(clip, index))


@pytest.mark.integration
def test_ac_134_10_long_audio_past_the_last_frame(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    clip = clips["long_audio.mp4"]
    service, _ = _frames_service(tmp_path / "inbox")
    result = service.frames_from_video(str(clip), at=[3.2])
    assert len(result.frames) == 1
    assert result.frames[0].time_ms == 3200
    assert _shot_pixels(result.frames[0].path) == _pixels(_reference(clip, 74))


@pytest.mark.integration
def test_ac_134_10_past_the_end_runs_no_grab(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    inbox = tmp_path / "inbox"
    service, frames = _frames_service(inbox)
    with pytest.raises(ValidationError) as caught:
        service.frames_from_video(str(clips["counter.mp4"]), at=[3.0])
    assert str(caught.value) == "time 00:00:03.000 is past the end (00:00:03.000)"
    assert frames.grabs == []
    assert not inbox.exists() or list(inbox.iterdir()) == []


@pytest.mark.integration
def test_ac_134_10_l_stroke_name_is_kept(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    service, _ = _frames_service(tmp_path / "inbox")
    result = service.frames_from_video(str(clips[L_STROKE_PATH]), at=[1.0])
    assert len(result.frames) == 1
    name = Path(result.frames[0].path).name
    assert name.startswith("Łodz-t")
    assert name == "Łodz-t00h00m01.000s.png"


@pytest.mark.integration
def test_ac_134_11_raw_stream_at_uses_output_seek(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    clip = clips["raw.h264"]
    service, frames = _frames_service(tmp_path / "inbox")
    result = service.frames_from_video(str(clip), at=[1.0])
    assert len(result.frames) == 1
    assert frames.grabs == [1000]
    assert result.video is not None
    assert result.video.duration_ms is None
    assert _shot_pixels(result.frames[0].path) == _pixels(_reference(clip, 25))


@pytest.mark.integration
def test_ac_134_11_raw_stream_count_is_refused(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    service, frames = _frames_service(tmp_path / "inbox")
    with pytest.raises(ValidationError) as caught:
        service.frames_from_video(str(clips["raw.h264"]), count=2)
    assert str(caught.value) == "count needs a duration; this video has none, so use at"
    assert frames.grabs == []


@pytest.mark.integration
def test_ac_134_10_every_clip_is_unchanged_after_frames(
    clips: dict[str, Path], hashes: dict[str, str], tmp_path: Path
) -> None:
    service, _ = _frames_service(tmp_path / "inbox")
    for name in ("counter.mp4", "vfr.mkv", "long_audio.mp4", L_STROKE_PATH):
        result = service.frames_from_video(str(clips[name]), at=[1.0])
        assert len(result.frames) == 1, name
    assert {name: _sha(path) for name, path in clips.items()} == hashes
    assert sorted(path.name for path in clips["counter.mp4"].parent.iterdir()) == sorted(clips)
