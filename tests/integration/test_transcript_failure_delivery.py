"""MEU-115 delivery tests (AC-115.18, AC-115.19): a failure's reason reaches every surface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.tts_asset_fakes import FakeAssets, idle_runtime
from tests.unit.test_services import (
    DownloadYouTube,
    FakeCaptions,
    FakeFilesystem,
    FakeMedia,
    FakeUnitOfWork,
    FakeYouTube,
    SharedFakeFactory,
)

from avkit_core.domain.download import PlaylistInfo
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.health import HealthService
from avkit_core.services.settings import SettingsService

API_TEXT = "connection reset at https://example.invalid/caption?token=SYNTHETIC_API_MARKER"
DOMAIN_TEXT = (
    "fetch failed at https://example.invalid/x?token=SYNTHETIC_DOMAIN_MARKER\n"
    "Authorization: Bearer SYNTHETIC_BEARER_MARKER"
)
MARKERS = ("SYNTHETIC_API_MARKER", "SYNTHETIC_DOMAIN_MARKER", "SYNTHETIC_BEARER_MARKER")


def _run(tmp_path: Path, ids: list[str], captions: object):
    from avkit_core.services.transcript import TranscriptService

    factory = SharedFakeFactory(FakeUnitOfWork())
    settings = SettingsService(factory)
    settings.set("transcript", "output_dir", str(tmp_path / "out"))
    settings.set("transcript", "max_retries", 0)
    settings.set("app", "log_to_file", False)
    health = HealthService(
        factory,
        app_data=tmp_path / "app",
        settings=settings,
        media=FakeMedia(),
        youtube=FakeYouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
    )
    youtube = DownloadYouTube()
    youtube.ids = list(ids)
    youtube.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(ids))
    service = TranscriptService(
        factory,
        coordinator=ExtractCoordinator(youtube),
        captions=captions,
        filesystem=FakeFilesystem(),
        settings=settings,
        sleep=lambda _seconds: None,
    )
    job = service.add_channel("https://youtube.com/@delivery")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    return service, health, job


def _console_text(app_data: Path) -> str:
    path = app_data / "logs" / "console.log"
    return path.read_text(encoding="utf-8") if path.exists() else ""


class _RaisingApi:
    def fetch(self, video_id: str, languages: list[str] | None = None) -> object:
        import requests

        raise requests.ConnectionError(API_TEXT)

    def list(self, video_id: str) -> list[object]:
        import requests

        raise requests.ConnectionError(API_TEXT)


class _RoutedCaptions:
    """The real adapter answers video "api"; the fake answers every other video."""

    def __init__(self, adapter: object, fake: FakeCaptions) -> None:
        self._adapter = adapter
        self._fake = fake

    def get_transcript(self, video_id: str, languages: list[str]) -> object:
        if video_id == "api":
            return self._adapter.get_transcript(video_id, languages)  # type: ignore[attr-defined]
        return self._fake.get_transcript(video_id, languages)


@pytest.mark.integration
def test_ac_115_18_skipped_video_reaches_card_console_and_file(tmp_path: Path) -> None:
    from avkit_api.routes.transcripts import _job_out
    from avkit_core.domain.transcript import TranscriptFailureCause, TranscriptSkip

    captions = FakeCaptions()
    captions.results["only"] = TranscriptSkip(TranscriptFailureCause.no_captions)
    service, health, job = _run(tmp_path, ["only"], captions)
    out = _job_out(service, service.get_job(job.id)).model_dump()
    assert (out["status"], out["error_message"], out.get("last_item_message")) == (
        "Done",
        "1 of 1 videos had no transcript. Last: No captions for this video.",
        "No captions for this video.",
    )
    skipped = [
        event
        for event in health.console_snapshot(0)
        if event.message.startswith("transcript.item_skipped")
    ]
    assert [(event.level, "No captions for this video." in event.message) for event in skipped] == [
        ("WARNING", True)
    ]
    filed = [json.loads(line)["message"] for line in _console_text(tmp_path / "app").splitlines()]
    assert skipped[0].message in filed


@pytest.mark.integration
def test_ac_115_19_no_secret_reaches_any_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_api.routes.transcripts import _job_out
    from avkit_core.domain.errors import DomainError
    from avkit_infra.transcript.adapter import TranscriptAdapter

    monkeypatch.setattr("avkit_infra.transcript.adapter.YouTubeTranscriptApi", _RaisingApi)
    fake = FakeCaptions()
    fake.results["domain"] = DomainError(DOMAIN_TEXT)
    service, health, job = _run(
        tmp_path, ["api", "domain"], _RoutedCaptions(TranscriptAdapter(), fake)
    )
    items = {item.video_id: item for item in service.list_items(job.id)}
    surfaces = {
        "items": " ".join(str(item.error_message) for item in items.values()),
        "api": _job_out(service, service.get_job(job.id)).model_dump_json(),
        "ring": " ".join(event.message for event in health.console_snapshot(0)),
        "stdout": capsys.readouterr().out,
        "file": _console_text(tmp_path / "app"),
    }
    leaks = {
        name: [marker for marker in MARKERS if marker in text] for name, text in surfaces.items()
    }
    assert leaks == {name: [] for name in surfaces}
    assert {key: item.error_message for key, item in items.items()} == {
        "api": "Couldn't get captions: ConnectionError.",
        "domain": "Couldn't get captions: fetch failed at [link] [REDACTED].",
    }


@pytest.mark.integration
def test_ac_115_19_case_folding_prefix_reaches_no_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    from avkit_api.routes.transcripts import _job_out
    from avkit_core.domain.errors import DomainError

    prefix = "\u00df" * 64
    fake = FakeCaptions()
    fake.results["fold"] = DomainError(prefix + " Bearer SYNTHETIC_FOLD_MARKER")
    service, health, job = _run(tmp_path, ["fold"], fake)
    items = service.list_items(job.id)
    surfaces = {
        "items": " ".join(str(item.error_message) for item in items),
        "api": _job_out(service, service.get_job(job.id)).model_dump_json(),
        "ring": " ".join(event.message for event in health.console_snapshot(0)),
        "stdout": capsys.readouterr().out,
        "file": _console_text(tmp_path / "app"),
    }
    assert [name for name, text in surfaces.items() if "SYNTHETIC" in text] == []
    assert [item.error_message for item in items] == [
        f"Couldn't get captions: {prefix} [REDACTED]."
    ]
