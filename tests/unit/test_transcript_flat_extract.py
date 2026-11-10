"""rc.3 F2: adding a channel never asks yt-dlp to resolve every video.

A non-flat extract opens each video of each channel tab (about one second apiece) before the
job exists; the folder title and the video IDs read the same from a flat extract.
"""

from __future__ import annotations

from pathlib import Path

from tests.unit.test_services import DownloadYouTube, _transcript_stack

from avkit_core.domain.download import PlaylistInfo, VideoInfo
from avkit_core.services.extract import ExtractCoordinator

URL = "https://youtube.com/@example"


class FlatRecordingYouTube(DownloadYouTube):
    def __init__(self) -> None:
        super().__init__()
        self.flat_args: list[bool] = []

    def extract_info(self, url: str, flat: bool = False) -> VideoInfo | PlaylistInfo:
        self.flat_args.append(flat)
        return super().extract_info(url, flat)


def test_add_channel_extracts_flat(tmp_path: Path) -> None:
    yt = FlatRecordingYouTube()
    service, _settings, _yt, uow, _fs, _captions, _sleeps = _transcript_stack(tmp_path, youtube=yt)
    job = service.add_channel(URL)
    assert yt.flat_args == [True]
    assert job.video_count == 2
    assert job.output_dir.name == "my-channel"
    assert [item.video_id for item in uow.transcripts.list_items(job.id)] == ["v1", "v2"]


def test_coordinator_caches_flat_and_full_extracts_apart() -> None:
    yt = FlatRecordingYouTube()
    coordinator = ExtractCoordinator(yt)
    coordinator.extract_info(URL, flat=True)
    coordinator.extract_info(URL, flat=True)
    coordinator.extract_info(URL)
    coordinator.extract_info(URL)
    assert yt.flat_args == [True, False]
