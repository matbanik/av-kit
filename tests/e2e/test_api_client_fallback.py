"""MEU-140 on the real stack: ATTEMPT_LOG in the Console, and the add-time cookie check.

`build_services` builds the real stack with the real `YouTubeAdapter`, `DownloadService` and
Console store; only `YoutubeDL` is a scripted fake, so nothing reaches the network. Run 0 is the
add-time extract and runs 1 and 2 are the download's attempts. The home folder is a marker path;
neither it, a cookie value nor a link reaches the ring or stdout (D-627, D-639).
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from structlog.testing import capture_logs
from tests.e2e.test_api_download_visibility import (
    AUTH,
    CONSOLE,
    DOWNLOADS,
    HOME,
    HOME_ANSI,
    HOME_STEM,
    HOME_X85,
    TOKENS,
    _home,
    _served,
)
from tests.integration.test_youtube_adapter import _download_error
from tests.integration.test_youtube_client_fallback import (
    NO_FORMAT,
    RELOAD,
    SABR_LINE,
    _info,
    _script,
)

from avkit_api.main import create_app
from avkit_api.wiring import build_services
from avkit_core.domain.download import download_failure_message
from avkit_core.domain.enums import AudioFormat, DownloadFailureCause, DownloadStatus, QualityPreset

pytestmark = pytest.mark.e2e

URL = "https://youtu.be/vid12345678"
ATTEMPT_FAILED = "youtube.attempt_failed"


@contextmanager
def _real_stack(tmp_path: Path) -> Iterator[tuple[TestClient, Any]]:
    app_data = tmp_path / "app"
    app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        services.settings.set("downloader", "path", str(tmp_path / "out"))
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield client, services
    finally:
        dispose()


def _add_and_run(services: Any) -> str:
    """Queue `URL` through the real service and run the queue; the job's id."""
    jobs = services.download.add_to_queue(URL, QualityPreset.P720, False, AudioFormat.Default)
    assert len(jobs) == 1
    services.download.start_processing()
    thread = services.download._thread
    if thread is not None:
        thread.join(timeout=5)
    return jobs[0].id


def _items(client: TestClient) -> list[dict[str, Any]]:
    response = client.get(CONSOLE, headers=AUTH)
    assert response.status_code == 200
    return list(response.json()["items"])


def _status(services: Any, job_id: str) -> DownloadStatus:
    return services.download.get_job(job_id).status


# --- AC-140.6: ATTEMPT_LOG traced from the port call to the Console --------------------------


def test_ac_140_6_a_failed_attempt_one_is_traced_to_the_console(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    _home(monkeypatch)
    info, _outfile = _info(tmp_path)
    seen = _script(
        monkeypatch,
        [None, _download_error(RELOAD), _download_error(NO_FORMAT), None],
        info=info,
    )
    with _real_stack(tmp_path) as (client, services):
        job_id = _add_and_run(services)
        items = _items(client)
        served = _served(client)
        status = _status(services, job_id)

    assert [run["download"] for run in seen.runs] == [False, True, True]
    stored = download_failure_message(DownloadFailureCause.no_format, None)
    rows = [
        item for item in items if item["message"].startswith((ATTEMPT_FAILED, "download.failed"))
    ]
    assert [item["message"] for item in rows] == [
        f"{ATTEMPT_FAILED} detail=[youtube] vid12345678: The page needs to be reloaded.",
        f"download.failed job_id={job_id} video_id=vid12345678 error={stored} "
        f"detail={NO_FORMAT.removeprefix('ERROR: ')}",
    ]
    assert (rows[0]["level"], rows[0]["module"]) == ("WARNING", "youtube")
    assert served[job_id] == stored
    assert status is DownloadStatus.Failed


def test_ac_140_6_attempt_failed_carries_attempt_clients_and_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    info, _outfile = _info(tmp_path)
    _script(monkeypatch, [None, _download_error(RELOAD), None], info=info)
    with _real_stack(tmp_path) as (_client, services):
        services.settings.set("downloader", "cookie_mode", "browser")
        services.settings.set("downloader", "cookie_browser", "firefox")
        with capture_logs() as logs:
            job_id = _add_and_run(services)
        status = _status(services, job_id)

    failed = [event for event in logs if event.get("event") == ATTEMPT_FAILED]
    assert [
        {key: event.get(key) for key in ("log_level", "attempt", "clients", "cause", "detail")}
        for event in failed
    ] == [
        {
            "log_level": "warning",
            "attempt": 1,
            "clients": "default",
            "cause": DownloadFailureCause.refused,
            "detail": "[youtube] vid12345678: The page needs to be reloaded.",
        }
    ]
    done = [event for event in logs if event.get("event") == "youtube.download"]
    assert [event.get("attempt") for event in done] == [2]
    assert [event for event in logs if event.get("event") == "download.failed"] == []
    assert status is DownloadStatus.Done


def test_ac_140_6_no_attempt_failed_line_when_attempt_one_passes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    info, _outfile = _info(tmp_path)
    seen = _script(monkeypatch, [None, None, None], info=info)
    with _real_stack(tmp_path) as (client, services):
        job_id = _add_and_run(services)
        items = _items(client)
        status = _status(services, job_id)
    assert [run["download"] for run in seen.runs] == [False, True]
    assert [item for item in items if item["message"].startswith(ATTEMPT_FAILED)] == []
    assert status is DownloadStatus.Done


# --- AC-140.7: attempt 1's text reaches the Console only through scrub_line ------------------

#: (id, attempt 1's error text, the SABR line attempt 1's log holds or None, the Console row).
SCRUBBED = [
    (
        "split_home_and_cookie",
        f"ERROR: [youtube] x: Requested format is not available at {HOME_X85}\\v.mp4 "
        "co\tokie=SECRET",
        None,
        f"{ATTEMPT_FAILED} detail=[youtube] x: Requested format is not available at ~\\v.mp4 "
        "[REDACTED]",
    ),
    (
        "split_link",
        "ERROR: [youtube] x: Requested format is not available https:\t//e.example/private",
        None,
        f"{ATTEMPT_FAILED} detail=[youtube] x: Requested format is not available [link]",
    ),
    (
        "nul_before_home",
        f"ERROR: [youtube] x: The page needs to be reloaded. at\x00{HOME}\\v.mp4 cookie=SECRET",
        None,
        f"{ATTEMPT_FAILED} detail=[youtube] x: The page needs to be reloaded. at~\\v.mp4 "
        "[REDACTED]",
    ),
    (
        "ansi_prefix_and_home",
        f"\x1b[0;31mERROR:\x1b[0m [youtube] x: No video formats found at {HOME_ANSI}\\v.mp4\n"
        "second cookie=SECRET",
        None,
        f"{ATTEMPT_FAILED} detail=[youtube] x: No video formats found at ~\\v.mp4",
    ),
    (
        "lone_surrogate_and_nul",
        "ERROR: [youtube] x: Requested format is not available\ud800 x\x00y",
        None,
        f"{ATTEMPT_FAILED} detail=[youtube] x: Requested format is not available xy",
    ),
    (
        "control_characters",
        "ERROR: [youtube] x: Only images are available\x07 \x1b[31mred\x1b[0m\x0b end\x7f",
        None,
        f"{ATTEMPT_FAILED} detail=[youtube] x: Only images are available red end",
    ),
    ("empty_text", "", SABR_LINE, f"{ATTEMPT_FAILED} detail="),
]


@pytest.mark.parametrize(
    ("text", "line", "row"),
    [(text, line, row) for _id, text, line, row in SCRUBBED],
    ids=[case[0] for case in SCRUBBED],
)
def test_ac_140_7_console_scrubbed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    text: str,
    line: str | None,
    row: str,
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    _home(monkeypatch)
    info, _outfile = _info(tmp_path)
    sabr_lines = {1: line} if line is not None else None
    _script(monkeypatch, [None, _download_error(text), None], info=info, sabr_lines=sabr_lines)
    with _real_stack(tmp_path) as (client, services):
        capfd.readouterr()
        job_id = _add_and_run(services)
        items = _items(client)
        served = _served(client)
        status = _status(services, job_id)
        captured = capfd.readouterr()

    messages = [item["message"] for item in items]
    assert [m for m in messages if m.startswith(ATTEMPT_FAILED)] == [row]
    assert [m for m in messages if m.startswith("download.failed")] == []
    assert status is DownloadStatus.Done
    assert served[job_id] is None
    seen = [*messages, captured.out, captured.err]
    for needle in (HOME_STEM, "secret", "e.example"):
        assert [shown for shown in seen if needle in shown.casefold()] == [], needle


# --- AC-140.11: a missing cookie file fails the add with 422 ---------------------------------


def _post(client: TestClient) -> Any:
    return client.post(
        DOWNLOADS,
        headers=AUTH,
        json={"url": URL, "quality": "720p", "audio_only": False, "audio_format": "default"},
    )


def test_ac_140_11_a_missing_cookie_file_fails_the_add_with_422(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    seen = _script(monkeypatch, [None])
    with _real_stack(tmp_path) as (client, services):
        services.settings.set("downloader", "cookie_mode", "file")
        services.settings.set("downloader", "cookie_file_path", str(tmp_path / "absent.txt"))
        response = _post(client)
        served = _served(client)
    assert response.status_code == 422, response.text
    assert response.json() == {
        "error": {
            "code": "CookieTestError",
            "message": "cookie file is missing or unreadable",
            "details": None,
        }
    }
    assert served == {}
    assert seen.inits == 0
    assert seen.runs == []


def test_ac_140_11_the_same_add_in_mode_none_creates_the_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    seen = _script(monkeypatch, [None])
    with _real_stack(tmp_path) as (client, _services):
        response = _post(client)
        served = _served(client)
    assert response.status_code == 201, response.text
    assert list(served.values()) == [None]
    assert [run["download"] for run in seen.runs] == [False]
