"""MEU-134 `POST /captures/frames` on the real stack (Session 62): FRAMES_ROUTE, FRAME_CHECKS.

`build_services` builds the real stack, HealthService first (Session 54 RULE-2), and a recording
fake `FramePort` replaces the capture service's FFmpeg adapter, so no FFmpeg runs here. The
annotate port is the real Pillow adapter and the rows are in the real SQLite file.
"""

from __future__ import annotations

import io
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from avkit_api.main import create_app
from avkit_api.wiring import build_services
from avkit_core.domain.errors import FFmpegNotFoundError, MediaProbeError
from avkit_core.domain.progress import MediaInfo

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
CAPTURES = "/api/v1/captures"
FRAMES = "/api/v1/captures/frames"
SETTINGS = "/api/v1/settings/capture"
CONSOLE = "/api/v1/health/console"
VIDEO_KEYS = {"path", "duration_ms", "width", "height", "fps"}
FRAME_KEYS = {"id", "path", "time_ms", "timecode", "width", "height"}
SCHEMA_REFUSAL = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
MASKED = ("internal_error", "Internal server error")
NOT_FOUND = "video file not found"
LOCAL = "path must be a local absolute file path"
NOT_PROBED = "the file could not be probed"
TMP = ".avkit-tmp"


def _png(colour: tuple[int, int, int] = (200, 10, 10)) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (8, 6), colour).save(buffer, format="PNG")
    return buffer.getvalue()


class FakeFrames:
    """A recording `FramePort`: answers with a small PNG, or `b""`, or raises as told."""

    def __init__(self) -> None:
        self.info = MediaInfo(
            duration=3.0,
            container="mov,mp4,m4a,3gp,3g2,mj2",
            video_codec="h264",
            audio_codec="aac",
            sample_rate=48000,
            channels=2,
            width=320,
            height=240,
            fps=25.0,
        )
        self.probe_error: Exception | None = None
        self.grab_error: Exception | None = None
        self.answer: bytes | None = None
        self.probes: list[Path] = []
        self.grabs: list[int] = []

    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo:
        del timeout_s
        self.probes.append(file_path)
        if self.probe_error is not None:
            raise self.probe_error
        return self.info

    def grab_frame(self, path: Path, time_ms: int, *, seek: str, timeout_s: float) -> bytes:
        del path, seek, timeout_s
        self.grabs.append(time_ms)
        if self.grab_error is not None:
            raise self.grab_error
        if self.answer is not None:
            return self.answer
        return _png((time_ms % 256, 10, 10))


@contextmanager
def _stack(
    tmp_path: Path, folder: str = "app"
) -> Iterator[tuple[TestClient, Any, FakeFrames, Path]]:
    app_data = tmp_path / folder
    app_data.mkdir(parents=True, exist_ok=True)
    inbox = tmp_path / f"{folder}-inbox"
    inbox.mkdir()
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        fake = FakeFrames()
        services.capture._frames = fake
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200, put.text
            yield client, services, fake, inbox
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


def _rows(services: Any) -> list[Any]:
    with services.capture._uow_factory() as uow:
        return list(uow.capture_shots.list())


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


class _OsProxy:
    """The capture module's `os`, with `replace` raising an error that names a marker."""

    def __init__(self, marker: str) -> None:
        self._marker = marker

    def replace(self, source: Any, dest: Any) -> None:
        raise OSError(f"{dest}: access denied {self._marker}")

    def __getattr__(self, name: str) -> object:
        return getattr(os, name)


# AC-134.12 request and response --------------------------------------------------------------


@pytest.mark.parametrize(
    ("body", "times"),
    [
        ({"at": [2, "0:01"]}, [1000, 2000]),
        ({"count": 3}, [500, 1500, 2500]),
        ({"count": 2, "start": "0:01", "end": 3}, [1500, 2500]),
    ],
    ids=["at", "count", "range"],
)
def test_ac_134_12_frames_answers_201_with_video_and_frames(
    tmp_path: Path, body: dict[str, object], times: list[int]
) -> None:
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(FRAMES, headers=AUTH, json={"path": str(clip), **body})
        assert response.status_code == 201, response.text
        payload = response.json()
        assert set(payload) == {"video", "frames"}
        assert set(payload["video"]) == VIDEO_KEYS
        assert payload["video"] == {
            "path": str(clip.resolve()),
            "duration_ms": 3000,
            "width": 320,
            "height": 240,
            "fps": 25.0,
        }
        assert [set(frame) for frame in payload["frames"]] == [FRAME_KEYS] * len(times)
        assert [frame["time_ms"] for frame in payload["frames"]] == times
        assert fake.grabs == times
        for frame in payload["frames"]:
            path = Path(frame["path"])
            assert path.parent == inbox.resolve()
            assert path.is_file()
            assert path.read_bytes() == _png((frame["time_ms"] % 256, 10, 10))
            assert (frame["width"], frame["height"]) == (8, 6)
        first = times[0]
        assert payload["frames"][0]["timecode"] == f"00:00:0{first // 1000}.{first % 1000:03d}"
        assert sorted(row.id for row in _rows(services)) == sorted(
            frame["id"] for frame in payload["frames"]
        )
    assert clip.read_bytes() == b"video"


REFUSALS: list[tuple[str, dict[str, object]]] = [
    ("both", {"at": [1], "count": 2}),
    ("neither", {}),
    ("start-with-at", {"at": [1], "start": 0}),
    ("end-with-at", {"at": [1], "end": 2}),
    ("21-times", {"at": list(range(21))}),
    ("empty-at", {"at": []}),
    ("count-0", {"count": 0}),
    ("count-21", {"count": 21}),
    ("count-true", {"count": True}),
    ("count-1.5", {"count": 1.5}),
    ("time-true", {"at": [True]}),
    ("time-null", {"at": [None]}),
    ("time-object", {"at": [{"s": 1}]}),
    ("start-object", {"count": 2, "start": {"s": 1}}),
    ("extra-key", {"at": [1], "extra": 1}),
]


@pytest.mark.parametrize(("case", "body"), REFUSALS, ids=[case for case, _ in REFUSALS])
def test_ac_134_12_schema_refusals(tmp_path: Path, case: str, body: dict[str, object]) -> None:
    del case
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(FRAMES, headers=AUTH, json={"path": str(clip), **body})
        assert response.status_code == 422, response.text
        assert response.json() == SCHEMA_REFUSAL
        assert fake.probes == []
        assert fake.grabs == []
        assert list(inbox.iterdir()) == []
        assert _rows(services) == []


@pytest.mark.parametrize(
    "path", ["", 123, "x" * 4097], ids=["empty-path", "non-string-path", "long-path"]
)
def test_ac_134_12_path_schema_refusals(tmp_path: Path, path: object) -> None:
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(FRAMES, headers=AUTH, json={"path": path, "count": 2})
        assert response.status_code == 422, response.text
        assert response.json() == SCHEMA_REFUSAL
        assert fake.probes == []
        missing = client.post(FRAMES, headers=AUTH, json={"count": 2})
        assert missing.status_code == 422, missing.text
        assert missing.json() == SCHEMA_REFUSAL


def test_ac_134_1_register_refuses_the_video_source(tmp_path: Path) -> None:
    with _stack(tmp_path) as (client, services, fake, inbox):
        shot = inbox / "shot.png"
        shot.write_bytes(_png())
        for source in ("video", "Video"):
            body = {"mode": "register", "path": str(shot), "source": source}
            response = client.post(CAPTURES, headers=AUTH, json=body)
            assert response.status_code == 422, response.text
            assert response.json() == SCHEMA_REFUSAL
        assert _rows(services) == []


# AC-134.13 errors name no path ----------------------------------------------------------------


def test_ac_134_13_errors_name_no_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    import structlog

    from avkit_core.services import capture as capture_mod
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    marker = f"s62MARKER{uuid4().hex}"
    folder = tmp_path / f"videos-{marker}"
    clip = _clip(folder, f"clip-{marker}.mp4")
    link = folder / f"loop-{marker}.mp4"
    responses: list[Any] = []
    with _stack(tmp_path, f"app-{marker}") as (client, services, fake, inbox):
        gone = folder / f"gone-{marker}.mp4"
        missing = client.post(FRAMES, headers=AUTH, json={"path": str(gone), "at": [1]})
        with _looping(link):
            loop = client.post(FRAMES, headers=AUTH, json={"path": str(link), "at": [1]})
        url = client.post(FRAMES, headers=AUTH, json={"path": f"http://x/{marker}.mp4", "at": [1]})
        assert fake.probes == []
        assert fake.grabs == []
        past = client.post(FRAMES, headers=AUTH, json={"path": str(clip), "at": [3]})
        fake.probe_error = MediaProbeError(f"{clip}: Invalid data found {marker}")
        unprobed = client.post(FRAMES, headers=AUTH, json={"path": str(clip), "at": [1]})
        fake.probe_error = None
        assert fake.grabs == []
        fake.answer = b""
        empty = client.post(FRAMES, headers=AUTH, json={"path": str(clip), "at": [1]})
        fake.answer = None
        fake.grab_error = FFmpegNotFoundError(f"ffmpeg binary was not found {marker}")
        unavailable = client.post(FRAMES, headers=AUTH, json={"path": str(clip), "at": [1]})
        fake.grab_error = None
        with monkeypatch.context() as patch:
            patch.setattr(capture_mod, "os", _OsProxy(marker))
            unwritten = client.post(FRAMES, headers=AUTH, json={"path": str(clip), "at": [1]})
        responses = [missing, loop, url, past, unprobed, empty, unavailable, unwritten]
        assert [response.status_code for response in responses] == [
            422,
            422,
            422,
            422,
            422,
            422,
            503,
            503,
        ]
        assert [_error(response) for response in responses[:6]] == [
            ("ValidationError", NOT_FOUND),
            ("ValidationError", NOT_FOUND),
            ("ValidationError", LOCAL),
            ("ValidationError", "time 00:00:03.000 is past the end (00:00:03.000)"),
            ("ValidationError", NOT_PROBED),
            ("ValidationError", "frame grab failed at 00:00:01.000"),
        ]
        assert [_error(response) for response in responses[6:]] == [MASKED, MASKED]
        assert fake.grabs == [1000, 1000, 1000]
        assert list(inbox.iterdir()) == []
        assert _rows(services) == []
        ring = client.get(CONSOLE, headers=AUTH)
        assert ring.status_code == 200
        messages = [item["message"] for item in ring.json()["items"]]
        captured = capfd.readouterr()
        # The positive control: one line that does hold the marker reaches the ring and stdout.
        structlog.get_logger(module="capture").info("frames.control", detail=marker)
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


@pytest.mark.parametrize(
    "body",
    [
        {"at": [1e25]},
        {"at": [1, 1e308]},
        {"count": 2, "start": 1e25},
        {"count": 2, "start": 0, "end": 1e25},
    ],
    ids=["at-1e25", "at-1e308", "start-1e25", "end-1e25"],
)
def test_ac_134_13_huge_finite_times_get_the_fixed_refusal(
    tmp_path: Path, body: dict[str, object]
) -> None:
    # D-592 (execution review round 1, F1): the fixed 422, not the masked 500.
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(FRAMES, headers=AUTH, json={"path": str(clip), **body})
        assert response.status_code == 422, response.text
        assert _error(response) == ("ValidationError", "a time must be seconds or HH:MM:SS.mmm")
        assert fake.grabs == []
        assert list(inbox.iterdir()) == []
        assert _rows(services) == []
    assert clip.read_bytes() == b"video"


# AC-134.14 frames are shots with source Video ------------------------------------------------


def test_ac_134_14_frames_are_video_shots_and_a_scan_keeps_them(tmp_path: Path) -> None:
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(FRAMES, headers=AUTH, json={"path": str(clip), "at": [1, 2]})
        assert response.status_code == 201, response.text
        frames = response.json()["frames"]
        ids = [frame["id"] for frame in frames]
        assert len(ids) == 2
        listed = client.get(CAPTURES, headers=AUTH)
        assert listed.status_code == 200
        items = {item["id"]: item for item in listed.json()["items"]}
        assert [items[shot_id]["source"] for shot_id in ids] == ["Video", "Video"]
        assert [(items[i]["width"], items[i]["height"]) for i in ids] == [(8, 6), (8, 6)]
        for frame in frames:
            detail = client.get(f"{CAPTURES}/{frame['id']}", headers=AUTH)
            assert detail.status_code == 200, detail.text
            assert detail.json()["source"] == "Video"
            assert detail.json()["original_path"] == frame["path"]
            image = client.get(f"{CAPTURES}/{frame['id']}/image", headers=AUTH)
            assert image.status_code == 200
            assert image.content == Path(frame["path"]).read_bytes()
        Image.new("RGB", (4, 4), (0, 0, 0)).save(inbox / "dropped.png")
        rescanned = client.get(CAPTURES, headers=AUTH)
        assert rescanned.status_code == 200
        sources = {
            Path(item["original_path"]).name: item["source"] for item in rescanned.json()["items"]
        }
        assert sources == {
            "clip-t00h00m01.000s.png": "Video",
            "clip-t00h00m02.000s.png": "Video",
            "dropped.png": "Scan",
        }
        assert not [path for path in inbox.iterdir() if path.name.endswith(TMP)]
