"""MEU-122 transcript metadata: listed titles, the channel name and their text safety.

Each test that uses the new listing types asserts they exist first (Session 52 RULE-4), so a
missing name fails as an assertion. Module-level imports use only names that exist at the
baseline.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.unit.test_services import DownloadYouTube, _health, _transcript_stack

from avkit_core.domain import download as download_domain
from avkit_core.domain.download import PlaylistInfo
from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
from avkit_core.domain.errors import DomainError, ValidationError
from avkit_core.services.extract import ExtractCoordinator

URL = "https://youtube.com/@example"


def _require_listing() -> None:
    assert hasattr(download_domain, "VideoListing")
    assert hasattr(download_domain, "ListedVideo")


def _process(service: object, timeout: float = 5.0) -> None:
    service.start_processing()  # type: ignore[attr-defined]
    thread = service._thread  # type: ignore[attr-defined]
    if thread is not None:
        thread.join(timeout=timeout)


def _front(raw: str) -> dict[str, str]:
    head = raw.split("---\n", 2)[1]
    fields: dict[str, str] = {}
    for line in head.splitlines():
        key, _, value = line.partition(": ")
        fields[key] = json.loads(value) if value.startswith('"') else value
    return fields


def _listed_stack(tmp_path: Path, ids: list[str], titles: dict[str, str], channel: str | None):
    stack = _transcript_stack(tmp_path)
    yt = stack[2]
    yt.ids = list(ids)
    yt.titles = dict(titles)
    yt.channel = channel
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(ids))
    return stack


def test_ac_122_1_listing_types_frozen_and_refuse_bad_values() -> None:
    _require_listing()
    import dataclasses
    import typing

    from avkit_core.domain.download import ListedVideo, VideoListing
    from avkit_core.ports.youtube import YouTubePort

    video = ListedVideo(video_id="v1", title="A title")
    listing = VideoListing(videos=(video, ListedVideo(video_id="v2", title=None)), channel_name="C")
    assert listing.videos[1].title is None
    assert VideoListing(videos=(), channel_name=None).videos == ()
    with pytest.raises(dataclasses.FrozenInstanceError):
        video.title = "changed"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        listing.channel_name = "changed"  # type: ignore[misc]

    marker = "SYNTHETIC_LISTING_MARKER"
    unclean = (
        "",
        f" {marker}",
        f"{marker} ",
        f"two  {marker}",
        f"line\n{marker}",
        f"tab\t{marker}",
        f"bell\x07{marker}",
        7,
    )
    refused: list[str] = []
    for value in unclean:
        with pytest.raises(ValidationError) as caught:
            ListedVideo(video_id="v1", title=value)  # type: ignore[arg-type]
        refused.append(str(caught.value))
        with pytest.raises(ValidationError) as caught:
            VideoListing(videos=(), channel_name=value)  # type: ignore[arg-type]
        refused.append(str(caught.value))
    with pytest.raises(ValidationError) as caught:
        ListedVideo(video_id="", title=marker)
    refused.append(str(caught.value))
    with pytest.raises(ValidationError) as caught:
        VideoListing(
            videos=(
                ListedVideo(video_id=marker, title="One"),
                ListedVideo(video_id=marker, title="Two"),
            ),
            channel_name=None,
        )
    refused.append(str(caught.value))
    assert [message for message in refused if marker in message] == []

    hints = typing.get_type_hints(YouTubePort.extract_video_ids)
    assert hints["return"] is VideoListing


def test_ac_122_1_lone_surrogate_text_is_refused() -> None:
    _require_listing()
    from avkit_core.domain.download import ListedVideo, VideoListing

    marker = "SYNTHETIC_SURROGATE_MARKER"
    refused: list[str] = []
    for value in (f"{marker} \ud800 title", f"{marker}\udfff", "\ud800"):
        with pytest.raises(ValidationError) as caught:
            ListedVideo(video_id="v1", title=value)
        refused.append(str(caught.value))
        with pytest.raises(ValidationError) as caught:
            VideoListing(videos=(), channel_name=value)
        refused.append(str(caught.value))
    assert [message for message in refused if marker in message] == []
    kept = "Caf\u00e9 \u2014 \u65e5\u672c \U0001f600 zero\u200bwidth"
    assert ListedVideo(video_id="v1", title=kept).title == kept
    assert VideoListing(videos=(), channel_name=kept).channel_name == kept


def test_ac_122_6_playlist_info_and_extract_info_unchanged() -> None:
    import dataclasses
    import inspect
    import typing

    from avkit_core.domain.download import VideoInfo
    from avkit_core.ports.youtube import YouTubePort

    assert [field.name for field in dataclasses.fields(PlaylistInfo)] == [
        "playlist_id",
        "title",
        "video_ids",
    ]
    hints = typing.get_type_hints(YouTubePort.extract_info)
    assert hints == {"url": str, "flat": bool, "return": VideoInfo | PlaylistInfo}
    assert list(inspect.signature(YouTubePort.extract_info).parameters) == ["self", "url", "flat"]
    assert inspect.signature(YouTubePort.extract_info).parameters["flat"].default is False


def test_ac_122_7_coordinator_caches_the_listing() -> None:
    _require_listing()
    from avkit_core.domain.download import ListedVideo, VideoListing

    yt = DownloadYouTube()
    yt.ids = ["a", "b"]
    yt.titles = {"a": "Alpha"}
    yt.channel = "Chan"
    coordinator = ExtractCoordinator(yt)
    first = coordinator.extract_video_ids(URL)
    second = coordinator.extract_video_ids(URL)
    assert first == VideoListing(
        videos=(ListedVideo(video_id="a", title="Alpha"), ListedVideo(video_id="b", title=None)),
        channel_name="Chan",
    )
    assert second is first
    assert yt.ids_calls == 1


def test_ac_122_8_listed_titles_reach_items_files_and_volume(tmp_path: Path) -> None:
    _require_listing()
    titles = {"v1": "First talk", "v2": "Second talk"}
    service, _settings, _yt, uow, _fs, captions, _sleeps = _listed_stack(
        tmp_path, ["v1", "v2"], titles, "Real Channel"
    )
    job = service.add_channel(URL)
    items = uow.transcripts.list_items(job.id)
    assert [(item.video_id, item.title) for item in items] == list(titles.items())
    assert captions.fetch_calls == []

    _process(service)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Done
    for video_id, title in titles.items():
        front = _front((job.output_dir / "raw" / f"{video_id}.md").read_text(encoding="utf-8"))
        assert (front["video_id"], front["title"], front["channel"]) == (
            video_id,
            title,
            "Real Channel",
        )
    volume = (job.output_dir / "compiled" / "my-channel_vol1.md").read_text(encoding="utf-8")
    lines = volume.splitlines()
    assert lines[0] == "# Real Channel"
    assert "- [First talk](#first-talk)" in lines
    assert "- [Second talk](#second-talk)" in lines
    assert "## First talk" in lines
    assert "## Second talk" in lines


def test_ac_122_9_missing_title_falls_back_to_the_id(tmp_path: Path) -> None:
    _require_listing()
    service, _settings, _yt, uow, _fs, _captions, _sleeps = _listed_stack(
        tmp_path, ["v1", "v2"], {"v1": "First talk"}, "Real Channel"
    )
    job = service.add_channel(URL)
    assert [item.title for item in uow.transcripts.list_items(job.id)] == ["First talk", None]

    _process(service)
    front = _front((job.output_dir / "raw" / "v2.md").read_text(encoding="utf-8"))
    assert front["title"] == "v2"
    lines = (
        (job.output_dir / "compiled" / "my-channel_vol1.md").read_text(encoding="utf-8")
    ).splitlines()
    assert "- [v2](#v2)" in lines
    assert "## v2" in lines


def test_ac_122_10_channel_name_from_the_listing(tmp_path: Path) -> None:
    _require_listing()
    service, *_rest = _listed_stack(tmp_path / "none", ["v1"], {"v1": "One"}, None)
    assert service.add_channel(URL).channel_name == "My Channel"

    service, _settings, _yt, uow, _fs, _captions, _sleeps = _listed_stack(
        tmp_path / "listed", ["v1"], {"v1": "One"}, "Real Channel"
    )
    job = service.add_channel(URL)
    assert job.channel_name == "Real Channel"
    _process(service)
    front = _front((job.output_dir / "raw" / "v1.md").read_text(encoding="utf-8"))
    assert front["channel"] == "Real Channel"
    volume = (job.output_dir / "compiled" / "my-channel_vol1.md").read_text(encoding="utf-8")
    assert volume.splitlines()[0] == "# Real Channel"


@pytest.mark.parametrize("channel", ["Real Channel", None], ids=["listed", "info-title"])
def test_ac_122_11_folder_volume_and_zip_names_unchanged(
    tmp_path: Path, channel: str | None
) -> None:
    _require_listing()
    service, _settings, _yt, uow, _fs, _captions, _sleeps = _listed_stack(
        tmp_path, ["v1"], {"v1": "One"}, channel
    )
    job = service.add_channel(URL)
    assert job.channel_name == (channel or "My Channel")
    assert job.output_dir == tmp_path / "my-channel"
    _process(service)
    done = uow.transcripts.get_job(job.id)
    assert done.status is TranscriptStatus.Done
    assert sorted(path.name for path in (job.output_dir / "compiled").iterdir()) == [
        "my-channel_vol1.md"
    ]
    assert done.zip_path == job.output_dir / "my-channel_raw.zip"
    assert done.zip_path.is_file()


@pytest.mark.parametrize("count", [2, 50])
def test_ac_122_12_no_extra_request_per_video(tmp_path: Path, count: int) -> None:
    _require_listing()
    ids = [f"v{index}" for index in range(count)]
    service, _settings, yt, uow, _fs, captions, _sleeps = _listed_stack(
        tmp_path, ids, {video_id: f"Title {video_id}" for video_id in ids}, "Real Channel"
    )
    job = service.add_channel(URL)
    assert (yt.extract_calls, yt.ids_calls, yt.last_options) == (1, 1, None)
    _process(service, timeout=20.0)
    assert uow.transcripts.get_job(job.id).status is TranscriptStatus.Done
    assert len(captions.fetch_calls) == count
    assert (yt.extract_calls, yt.ids_calls, yt.last_options) == (1, 1, None)


def test_ac_122_13_fetch_keeps_the_stored_title(tmp_path: Path) -> None:
    _require_listing()
    from avkit_core.domain.transcript import TranscriptResult

    service, _settings, _yt, uow, _fs, captions, _sleeps = _listed_stack(
        tmp_path, ["v1", "v2"], {"v1": "First talk", "v2": "Second talk"}, "Real Channel"
    )
    captions.results["v1"] = TranscriptResult(
        video_id="v1", title="Other one", text="hello world", language="en"
    )
    captions.results["v2"] = DomainError("no")
    job = service.add_channel(URL)
    _process(service)
    items = {item.video_id: item for item in uow.transcripts.list_items(job.id)}
    assert items["v1"].status is TranscriptItemStatus.Done
    assert items["v1"].title == "First talk"
    assert _front(items["v1"].path.read_text(encoding="utf-8"))["title"] == "First talk"
    assert items["v2"].status is TranscriptItemStatus.Failed
    assert items["v2"].title == "Second talk"

    service.retry_failed_channel(job.id)
    captions.results["v2"] = TranscriptResult(
        video_id="v2", title="Other two", text="hello again", language="en"
    )
    _process(service)
    retried = {item.video_id: item for item in uow.transcripts.list_items(job.id)}["v2"]
    assert retried.status is TranscriptItemStatus.Done
    assert retried.title == "Second talk"
    assert _front(retried.path.read_text(encoding="utf-8"))["title"] == "Second talk"


def test_ac_122_14_title_text_is_quoted_and_escaped(tmp_path: Path) -> None:
    _require_listing()
    from avkit_core.services.transcript import _markdown_body, slugify

    title = 'Talk: "Quoted" [part 1] back\\slash'
    channel = 'Chan: "Name" [x]'
    service, _settings, _yt, _uow, _fs, _captions, _sleeps = _listed_stack(
        tmp_path, ["v1"], {"v1": title}, channel
    )
    job = service.add_channel(URL)
    _process(service)
    raw = (job.output_dir / "raw" / "v1.md").read_text(encoding="utf-8")
    fields = dict(line.partition(": ")[::2] for line in raw.split("---\n", 2)[1].splitlines())
    assert json.loads(fields["title"]) == title
    assert json.loads(fields["channel"]) == channel
    assert _markdown_body(raw) == "hello world"
    lines = (
        (job.output_dir / "compiled" / "my-channel_vol1.md").read_text(encoding="utf-8")
    ).splitlines()
    label = 'Talk: "Quoted" \\[part 1\\] back\\\\slash'
    assert f"- [{label}](#{slugify(title)})" in lines
    assert f"## {title}" in lines
    heading = lines.index(f"## {title}")
    assert lines[heading + 2] == "hello world"


def test_ac_122_16_titles_reach_files_not_the_console(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _require_listing()
    import structlog

    from avkit_infra.youtube.adapter import _YtDlpLogger

    title_marker = "SYNTHETIC_TITLE_MARKER"
    channel_marker = "SYNTHETIC_CHANNEL_MARKER"
    control_marker = "SYNTHETIC_CONTROL_MARKER"
    health = _health(tmp_path / "app", log_to_file=True)
    service, _settings, _yt, uow, _fs, captions, _sleeps = _listed_stack(
        tmp_path / "out",
        ["v1", "v2"],
        {"v1": f"Kept {title_marker}", "v2": f"Failing {title_marker}"},
        f"Chan {channel_marker}",
    )
    captions.results["v2"] = DomainError("caption gone")
    job = service.add_channel(URL)
    _process(service)
    statuses = [item.status for item in uow.transcripts.list_items(job.id)]
    assert statuses == [TranscriptItemStatus.Done, TranscriptItemStatus.Failed]
    raw = (job.output_dir / "raw" / "v1.md").read_text(encoding="utf-8")
    assert title_marker in raw
    assert channel_marker in raw

    structlog.get_logger().error("probe.control", detail=control_marker)
    last = health.console_snapshot(0)[-1].seq
    _YtDlpLogger(True).debug(f"debug {title_marker} {channel_marker}")
    assert [event.message for event in health.console_snapshot(last)] == ["yt-dlp"]

    surfaces = {
        "ring": " ".join(event.message for event in health.console_snapshot(0)),
        "stdout": capsys.readouterr().out,
        "file": (tmp_path / "app" / "logs" / "console.log").read_text(encoding="utf-8"),
    }
    found = {
        name: [m for m in (title_marker, channel_marker, control_marker) if m in text]
        for name, text in surfaces.items()
    }
    assert found == {"ring": [control_marker], "stdout": [control_marker], "file": [control_marker]}


def test_ac_122_17_sql_error_text_holds_no_bound_value(tmp_path: Path) -> None:
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    from avkit_core.services.health import console_field
    from avkit_infra.database.engine import create_sqlite_engine

    marker = "SYNTHETIC_SQL_MARKER"
    insert = text("INSERT INTO probe (title) VALUES (:title)")
    engine = create_sqlite_engine(tmp_path / "probe.db")
    try:
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE probe (title TEXT PRIMARY KEY)"))
            connection.execute(insert, {"title": marker})
        with pytest.raises(IntegrityError) as caught, engine.begin() as connection:
            connection.execute(insert, {"title": marker})
    finally:
        engine.dispose()
    assert marker not in str(caught.value)
    assert marker not in console_field(str(caught.value))
