"""MEU-142 real-FFmpeg audio extract (AC-142.17): the pinned pair turns a `.m4a` into an MP3.

The 1 s clip is generated with lavfi in a temp folder and never committed. No test reaches
YouTube: the YouTube port is a fake that copies the generated clip into the output folder. CI
deselects this module, because the pinned binaries are fetched, not tracked (CI_DESELECT). The
module fails, never skips, when the pair is missing.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest
from tests.unit.test_services import FakeUnitOfWork, FakeYouTube, SharedFakeFactory

from avkit_core.domain.download import DownloadResult, VideoInfo
from avkit_core.domain.enums import AudioFormat, DownloadStatus, QualityPreset
from avkit_core.services.download import DownloadService
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.settings import SettingsService
from avkit_infra.media.adapter import FFmpegAdapter

pytestmark = pytest.mark.integration

REPO_ROOT = Path(__file__).resolve().parents[2]
FFMPEG = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg.exe"
FFPROBE = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffprobe.exe"


def _assert_pinned() -> None:
    for binary in (FFMPEG, FFPROBE):
        assert binary.is_file() and binary.stat().st_size > 1024, (
            f"packaging/ffmpeg-win64/{binary.name} is missing or a stub; "
            "run tools/fetch_ffmpeg_windows.ps1"
        )


class ClipYouTube(FakeYouTube):
    """Copies the generated clip into the output folder as the downloaded file."""

    def __init__(self, clip: Path, folder: Path) -> None:
        super().__init__()
        self.clip = clip
        self.folder = folder
        self.written: list[Path] = []

    def extract_info(self, url: str, flat: bool = False, options: object = None) -> VideoInfo:
        return VideoInfo(video_id="vid1", title="One", duration=1.0, formats=[])

    def download(self, url: str, options: object) -> DownloadResult:
        path = self.folder / "clip.m4a"
        shutil.copyfile(self.clip, path)
        self.written.append(path)
        return DownloadResult(
            file_path=path,
            file_size=path.stat().st_size,
            video_id="vid1",
            title="One",
            sabr_detected=False,
        )


def _clip(folder: Path) -> Path:
    clip = folder / "source.m4a"
    argv = [str(FFMPEG), "-hide_banner", "-nostdin", "-y"]
    argv += ["-f", "lavfi", "-i", "sine=frequency=440:duration=1"]
    argv += ["-vn", "-c:a", "aac", str(clip)]
    subprocess.run(argv, check=True, capture_output=True, timeout=60)
    assert clip.is_file()
    return clip


def test_ac_142_17_pinned_ffmpeg_makes_an_mp3(tmp_path: Path) -> None:
    _assert_pinned()
    clip = _clip(tmp_path)
    out = tmp_path / "out"
    out.mkdir()
    factory = SharedFakeFactory(FakeUnitOfWork())
    youtube = ClipYouTube(clip, out)
    service = DownloadService(
        factory,
        youtube=youtube,
        media=FFmpegAdapter(configured_source=lambda: None, bundle_path=FFMPEG),
        coordinator=ExtractCoordinator(youtube),
        settings=SettingsService(factory),
        sleep=lambda _seconds: None,
    )
    jobs = service.add_to_queue(
        "https://youtu.be/vid1", QualityPreset.P1080, True, AudioFormat.StandardMp3
    )
    assert len(jobs) == 1
    service.start_processing()
    thread = service._thread
    assert thread is not None
    thread.join(timeout=60)
    assert not thread.is_alive()

    with factory() as uow:
        job = uow.downloads.get(jobs[0].id)
    assert job is not None
    assert (job.status, job.error_message) == (DownloadStatus.Done, None)
    assert job.file_path == out / "clip.mp3"
    assert job.file_path.is_file()
    assert job.file_size == job.file_path.stat().st_size
    assert len(youtube.written) == 1
    assert not youtube.written[0].exists()

    probed = subprocess.run(
        [str(FFPROBE), "-v", "error", "-show_streams", "-of", "json", str(job.file_path)],
        check=True,
        capture_output=True,
        timeout=60,
    )
    streams = json.loads(probed.stdout)["streams"]
    assert [(s["codec_type"], s["codec_name"]) for s in streams] == [("audio", "mp3")]
