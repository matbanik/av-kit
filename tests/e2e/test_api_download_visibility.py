"""MEU-137 FAILURE_LOG, MEU-138 SABR_LOG and MEU-139 YTDLP_LINE on the real stack (S54 RULE-2).

`build_services` builds the real stack, HealthService first, and a fake YouTube port replaces
the download service's adapter, so nothing reaches the network. The home folder is a marker
path; neither it, a cookie value nor a URL reaches the ring, stdout or `GET /downloads`, in
plain form or split by a control or whitespace character (D-627).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from tests.unit.test_services import DownloadYouTube

from avkit_api.main import create_app
from avkit_api.wiring import build_services
from avkit_core.domain.download import SABRStatus, VideoInfo
from avkit_core.domain.enums import (
    AudioFormat,
    DownloadFailureCause,
    DownloadStatus,
    QualityPreset,
    SABRMode,
    SABRSource,
)
from avkit_core.domain.errors import DownloadFailedError, ExtractError
from avkit_core.services import health as health_module
from avkit_core.services.extract import ExtractCoordinator

pytestmark = pytest.mark.e2e

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
CONSOLE = "/api/v1/health/console"
DOWNLOADS = "/api/v1/downloads"

HOME = "C:\\Users\\S65HOMEMARKER"
HOME_ANSI = "C:\\Users\\S65HOME\x1b[0mMARKER"
HOME_X85 = "C:\\Users\\S65HOME\x85MARKER"
#: Every form of the user name starts with this, so its absence covers the split forms too.
HOME_STEM = "s65home"

#: (raw detail, the scrubbed detail) for AC-137.9's five jobs, in the AC's order.
TRACED = [
    (
        f"ERROR: x at {HOME}\\v.mp4 https://e.example/p cookie=SECRET",
        "ERROR: x at ~\\v.mp4 [link] [REDACTED]",
    ),
    (
        f"ERROR: x at {HOME_ANSI}\\v.mp4 https\x00://e.example/q co\x00okie=SECRET",
        "ERROR: x at ~\\v.mp4 [link] [REDACTED]",
    ),
    (
        f"ERROR: x at {HOME_X85}\\v.mp4 https:\u2028//e.example/r co\x85okie=SECRET",
        "ERROR: x at ~\\v.mp4 [link] [REDACTED]",
    ),
    ("ERROR: x co\u2028okie=SECRET", "ERROR: x [REDACTED]"),
    (f"ERROR: x at\t{HOME_X85}\\v.mp4 cookie=SECRET", "ERROR: x at~\\v.mp4 [REDACTED]"),
]


def _home(monkeypatch: pytest.MonkeyPatch) -> None:
    assert hasattr(health_module, "home_folder")
    assert hasattr(health_module, "HOME_IGNORES_CASE")
    monkeypatch.setattr(health_module, "home_folder", lambda: HOME)
    monkeypatch.setattr(health_module, "HOME_IGNORES_CASE", True)


@contextmanager
def _stack(tmp_path: Path) -> Iterator[tuple[TestClient, Any, DownloadYouTube]]:
    app_data = tmp_path / "app"
    app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        download = services.download
        assert hasattr(download, "_youtube") and hasattr(download, "_coordinator")
        fake = DownloadYouTube()
        fake.service = download
        download._youtube = fake
        download._coordinator = ExtractCoordinator(fake)
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield client, services, fake
    finally:
        dispose()


def _fail_one(services: Any, fake: DownloadYouTube, n: int, detail: str) -> str:
    """Queue one job whose port raises `DownloadFailedError(other, detail)`; its job id."""
    video_id = f"vid{n:08d}"
    fake.video = VideoInfo(video_id=video_id, title="T", duration=1.0, formats=[])
    fake.download_error = DownloadFailedError(DownloadFailureCause.other, detail)
    jobs = services.download.add_to_queue(
        f"https://youtu.be/{video_id}", QualityPreset.P1080, False, AudioFormat.Default
    )
    assert len(jobs) == 1
    services.download.start_processing()
    thread = services.download._thread
    if thread is not None:
        thread.join(timeout=5)
    job = services.download.get_job(jobs[0].id)
    assert job.status is DownloadStatus.Failed, job.status
    return jobs[0].id


def _ring(client: TestClient) -> list[str]:
    response = client.get(CONSOLE, headers=AUTH)
    assert response.status_code == 200
    return [item["message"] for item in response.json()["items"]]


def _served(client: TestClient) -> dict[str, str | None]:
    response = client.get(DOWNLOADS, headers=AUTH)
    assert response.status_code == 200, response.text
    return {item["id"]: item["error_message"] for item in response.json()["items"]}


def test_ac_137_9_console_and_card_hold_no_home_link_or_cookie(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    import structlog

    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    _home(monkeypatch)
    with _stack(tmp_path) as (client, services, fake):
        # The positive control: the marker home path does reach the ring, as "~".
        structlog.get_logger(module="download").info("probe.control", detail=f"{HOME}\\v.mp4")
        control = [m for m in _ring(client) if m.startswith("probe.control")]
        assert control == ["probe.control detail=~\\v.mp4"]
        capfd.readouterr()

        ids = [_fail_one(services, fake, n, raw) for n, (raw, _scrubbed) in enumerate(TRACED)]
        messages = _ring(client)
        served = _served(client)
        captured = capfd.readouterr()

    want_lines = []
    for n, (job_id, (_raw, scrubbed)) in enumerate(zip(ids, TRACED, strict=True)):
        stored = f"Download failed: {scrubbed}."
        assert served[job_id] == stored, n
        want_lines.append(
            f"download.failed job_id={job_id} video_id=vid{n:08d} error={stored} detail={scrubbed}"
        )
    assert [m for m in messages if m.startswith("download.failed")] == want_lines

    shown = [*messages, *(text or "" for text in served.values()), captured.out, captured.err]
    for needle in (HOME_STEM, "secret", "e.example"):
        assert [text for text in shown if needle in text.casefold()] == [], needle


def test_ac_137_11_surrogate_and_nul_are_dropped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    _home(monkeypatch)
    with _stack(tmp_path) as (client, services, fake):
        job_id = _fail_one(services, fake, 0, "bad\ud800 x\x00y")
        response = client.get(DOWNLOADS, headers=AUTH)
        messages = _ring(client)
    assert response.status_code == 200
    body = response.json()
    served = {item["id"]: item["error_message"] for item in body["items"]}
    assert served[job_id] == "Download failed: bad xy."
    failed = [m for m in messages if m.startswith("download.failed")]
    assert len(failed) == 1
    assert failed[0].endswith(" detail=bad xy")


# --- MEU-138: SABR_RESULT and SABR_LOG on the real stack --------------------------------------

SABR = "/api/v1/downloads/sabr"


REQUEST_ID = re.compile(r" request_id=[0-9a-f-]{36}$")


def _sabr_lines(client: TestClient) -> list[tuple[str, str]]:
    """The ring's `download.sabr_*` items as (level, message), in order.

    Each was logged inside its HTTP request, so the Console adds that request's
    ` request_id=<uuid>` last; it is checked and removed here.
    """
    response = client.get(CONSOLE, headers=AUTH)
    assert response.status_code == 200
    lines = []
    for item in response.json()["items"]:
        message = item["message"]
        if not message.startswith("download.sabr_"):
            continue
        assert REQUEST_ID.search(message), message
        lines.append((item["level"], REQUEST_ID.sub("", message)))
    return lines


def _check_returns(
    monkeypatch: pytest.MonkeyPatch, fake: DownloadYouTube, outcome: SABRStatus | Exception
) -> None:
    def check_sabr_status() -> SABRStatus:
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(fake, "check_sabr_status", check_sabr_status)


def _detected(mode: SABRMode, phrase: str | None) -> SABRStatus:
    from datetime import UTC, datetime

    return SABRStatus(mode, SABRSource.Detected, datetime.now(UTC), phrase)


def test_ac_138_5_check_stores_the_phrase_and_keeps_it_off_the_wire(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    with _stack(tmp_path) as (client, services, fake):
        _check_returns(monkeypatch, fake, _detected(SABRMode.Active, "missing a url"))
        checked = client.post(f"{SABR}/check", headers=AUTH)
        stored = services.download.get_sabr_status()
        got = client.get(SABR, headers=AUTH)
    assert checked.status_code == 200, checked.text
    assert (stored.mode, stored.source, getattr(stored, "matched_phrase", None)) == (
        SABRMode.Active,
        SABRSource.Detected,
        "missing a url",
    )
    assert got.status_code == 200
    assert sorted(got.json()) == ["checked_at", "mode", "source"]
    assert sorted(checked.json()) == ["checked_at", "mode", "source"]


def test_ac_138_6_each_sabr_call_logs_one_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    with _stack(tmp_path) as (client, _services, fake):
        statuses = []
        _check_returns(monkeypatch, fake, _detected(SABRMode.Active, "sabr"))
        statuses.append(client.post(f"{SABR}/check", headers=AUTH).status_code)
        _check_returns(monkeypatch, fake, _detected(SABRMode.Inactive, None))
        statuses.append(client.post(f"{SABR}/check", headers=AUTH).status_code)
        statuses.append(client.post(f"{SABR}/force", headers=AUTH).status_code)
        statuses.append(client.post(f"{SABR}/clear", headers=AUTH).status_code)
        lines = _sabr_lines(client)
    assert statuses == [200, 200, 200, 200]
    assert lines == [
        ("INFO", "download.sabr_check detail=Active, matched 'sabr'"),
        ("INFO", "download.sabr_check detail=Inactive, no phrase matched"),
        ("INFO", "download.sabr_force detail=Active, forced"),
        ("INFO", "download.sabr_clear detail=Inactive, cleared"),
    ]


def test_ac_138_7_a_failed_check_logs_and_keeps_the_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    with _stack(tmp_path) as (client, services, fake):
        before = services.download.get_sabr_status()
        _check_returns(monkeypatch, fake, ExtractError("x cookie=SECRET"))
        capfd.readouterr()
        response = client.post(f"{SABR}/check", headers=AUTH)
        after = services.download.get_sabr_status()
        lines = _sabr_lines(client)
        captured = capfd.readouterr()
    assert response.status_code == 422, response.text
    assert after == before
    assert lines == [("ERROR", "download.sabr_check error=x [REDACTED]")]
    for text in (*(message for _level, message in lines), captured.out, captured.err):
        assert "secret" not in text.casefold()


# --- MEU-139: YTDLP_LINE redaction on the real stack ------------------------------------------

HOME_2028 = "C:\\Users\\S65HOME\u2028MARKER"

#: (yt-dlp's warning, the Console line) for AC-139.5, in the AC's order.
WARNED = [
    (
        f"WARNING: x at {HOME}\\v.mp4 https://e.example/p cookie=SECRET",
        "yt-dlp detail=WARNING: x at ~\\v.mp4 [link] [REDACTED]",
    ),
    (
        f"WARNING: x at {HOME_2028}\\v.mp4 co\x85okie=SECRET",
        "yt-dlp detail=WARNING: x at ~\\v.mp4 [REDACTED]",
    ),
    (
        "WARNING: https:\x85//e.example/s co\u2028okie=SECRET",
        "yt-dlp detail=WARNING: [link] [REDACTED]",
    ),
    (
        f"WARNING: at\u2028{HOME}\\v.mp4 cookie=SECRET",
        "yt-dlp detail=WARNING: at~\\v.mp4 [REDACTED]",
    ),
]


def test_ac_139_5_ytdlp_warnings_reach_the_console_redacted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    import structlog

    from avkit_core.services.health import HealthService
    from avkit_infra.youtube.adapter import _YtDlpLogger

    monkeypatch.setattr(HealthService, "_active", None)
    _home(monkeypatch)
    with _stack(tmp_path) as (client, _services, _fake):
        # The positive control, as AC-137.9: the marker home path reaches the ring as "~".
        structlog.get_logger(module="download").info("probe.control", detail=f"{HOME}\\v.mp4")
        control = [m for m in _ring(client) if m.startswith("probe.control")]
        assert control == ["probe.control detail=~\\v.mp4"]
        capfd.readouterr()

        for raw, _shown in WARNED:
            _YtDlpLogger(False).warning(raw)
        messages = _ring(client)
        captured = capfd.readouterr()

    assert [m for m in messages if m.startswith("yt-dlp")] == [shown for _raw, shown in WARNED]
    seen = [*messages, captured.out, captured.err]
    for needle in (HOME_STEM, "secret", "e.example"):
        assert [text for text in seen if needle in text.casefold()] == [], needle
