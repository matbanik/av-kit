"""MEU-133 `POST /conversions/probe` on the real stack (Session 62): PROBE_ROUTE, PROBE_MAP.

`build_services` builds the real stack, HealthService first (Session 54 RULE-2), and a
recording fake MediaPort replaces the conversion service's adapter, so no FFmpeg runs here.
The probe answers 200 and writes no conversion row; its errors name no part of the path.
"""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services
from avkit_core.domain.errors import FFmpegNotFoundError, MediaProbeError
from avkit_core.domain.progress import MediaInfo

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PROBE = "/api/v1/conversions/probe"
CONSOLE = "/api/v1/health/console"
MP4 = "mov,mp4,m4a,3gp,3g2,mj2"
KEYS = {
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
}
SCHEMA_REFUSAL = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
NOT_FOUND = "video file not found"
LOCAL = "path must be a local absolute file path"
NOT_PROBED = "the file could not be probed"


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


class FakeProbeMedia:
    """Records each probe and answers or raises as told; anything else goes to the real one."""

    def __init__(self, real: object) -> None:
        self._real = real
        self.info = _info()
        self.error: Exception | None = None
        self.calls: list[Path] = []

    def probe(self, file_path: Path, **kwargs: object) -> MediaInfo:
        del kwargs
        self.calls.append(file_path)
        if self.error is not None:
            raise self.error
        return self.info

    def __getattr__(self, name: str) -> object:
        return getattr(self._real, name)


@contextmanager
def _stack(tmp_path: Path, folder: str = "app") -> Iterator[tuple[TestClient, Any, FakeProbeMedia]]:
    app_data = tmp_path / folder
    app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        fake = FakeProbeMedia(services.conversion._media)
        services.conversion._media = fake
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield client, services, fake
    finally:
        dispose()


def _clip(folder: Path, name: str = "clip.mp4") -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    clip = folder / name
    clip.write_bytes(b"video")
    return clip


def _error(response: Any) -> tuple[str, str]:
    body = response.json()
    return body["error"]["code"], body["error"]["message"]


@contextmanager
def _looping(link: Path) -> Iterator[None]:
    """A self-loop symlink at `link`, or, where `os.symlink` is refused, a `Path.resolve` that
    raises as Python 3.12 does on a loop, for that one path only."""
    try:
        os.symlink(link, link)
    except OSError:
        original = Path.resolve

        def _resolve(self: Path, strict: bool = False) -> Path:
            if str(self) == str(link):
                raise RuntimeError(f"Symlink loop from {self}")
            return original(self, strict=strict)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(Path, "resolve", _resolve)
            yield
        return
    try:
        yield
    finally:
        link.unlink()


def test_ac_133_4_probe_returns_the_eleven_fields(tmp_path: Path) -> None:
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake):
        response = client.post(PROBE, headers=AUTH, json={"path": str(clip)})
        assert response.status_code == 200, response.text
        body = response.json()
        assert set(body) == KEYS
        assert body == {
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
        assert fake.calls == [clip.resolve()]
        assert services.conversion.get_queue() == []
    assert clip.read_bytes() == b"video"


def test_ac_133_4_no_duration_gives_nulls(tmp_path: Path) -> None:
    clip = _clip(tmp_path / "videos", "raw.h264")
    with _stack(tmp_path) as (client, services, fake):
        fake.info = _info(duration=None, container="h264", audio_codec=None)
        response = client.post(PROBE, headers=AUTH, json={"path": str(clip)})
        assert response.status_code == 200, response.text
        body = response.json()
        assert set(body) == KEYS
        assert (body["duration_ms"], body["timecode"]) == (None, None)
        assert (body["container"], body["has_video"], body["has_audio"]) == ("h264", True, False)
        assert services.conversion.get_queue() == []


@pytest.mark.parametrize(
    "body",
    [
        {"path": "C:/tmp/clip.mp4", "extra": 1},
        {},
        {"path": ""},
        {"path": 123},
    ],
    ids=["extra-key", "missing-path", "empty-path", "non-string-path"],
)
def test_ac_133_4_schema_refusals(tmp_path: Path, body: dict[str, object]) -> None:
    with _stack(tmp_path) as (client, services, fake):
        response = client.post(PROBE, headers=AUTH, json=body)
        assert response.status_code == 422, response.text
        assert response.json() == SCHEMA_REFUSAL
        assert fake.calls == []
        assert services.conversion.get_queue() == []


def test_ac_133_5_errors_name_no_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    import structlog

    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    marker = f"s62MARKER{uuid4().hex}"
    folder = tmp_path / f"videos-{marker}"
    clip = _clip(folder, f"clip-{marker}.mp4")
    link = folder / f"loop-{marker}.mp4"
    responses: list[Any] = []
    with _stack(tmp_path, f"app-{marker}") as (client, services, fake):
        gone = folder / f"gone-{marker}.mp4"
        missing = client.post(PROBE, headers=AUTH, json={"path": str(gone)})
        with _looping(link):
            loop = client.post(PROBE, headers=AUTH, json={"path": str(link)})
        url = client.post(PROBE, headers=AUTH, json={"path": f"http://x/{marker}.mp4"})
        assert fake.calls == []
        fake.error = MediaProbeError(f"{clip}: Invalid data found when processing input {marker}")
        unprobed = client.post(PROBE, headers=AUTH, json={"path": str(clip)})
        fake.error = FFmpegNotFoundError(f"ffprobe binary was not found {marker}")
        unavailable = client.post(PROBE, headers=AUTH, json={"path": str(clip)})
        responses = [missing, loop, url, unprobed, unavailable]
        assert [response.status_code for response in responses] == [422, 422, 422, 422, 503]
        assert [_error(response) for response in responses[:4]] == [
            ("ValidationError", NOT_FOUND),
            ("ValidationError", NOT_FOUND),
            ("ValidationError", LOCAL),
            ("ValidationError", NOT_PROBED),
        ]
        assert _error(unavailable) == ("internal_error", "Internal server error")
        assert fake.calls == [clip.resolve(), clip.resolve()]
        assert services.conversion.get_queue() == []
        ring = client.get(CONSOLE, headers=AUTH)
        assert ring.status_code == 200
        messages = [item["message"] for item in ring.json()["items"]]
        captured = capfd.readouterr()
        # The positive control: one line that does hold the marker reaches the ring and stdout.
        structlog.get_logger(module="convert").info("probe.control", detail=marker)
        control_ring = client.get(CONSOLE, headers=AUTH)
        control_messages = [item["message"] for item in control_ring.json()["items"]]
        control = capfd.readouterr()
    folded = marker.casefold()
    assert [response.text for response in responses if folded in response.text.casefold()] == []
    assert [message for message in messages if folded in message.casefold()] == []
    lines = (captured.out + captured.err).splitlines()
    assert [line for line in lines if folded in line.casefold()] == []
    assert sum(folded in message.casefold() for message in control_messages) == 1
    # D-590: one event is two stdout lines. HealthService._process prints the JSON payload
    # (health.py:230) and the structlog console renderer prints the message again.
    assert sum(folded in line.casefold() for line in control.out.splitlines()) >= 1
