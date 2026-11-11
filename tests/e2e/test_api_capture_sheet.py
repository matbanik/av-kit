"""MEU-135 `POST /captures/sheet` on the real stack (Session 63): SHEET_ROUTE, AC-135.15 to .17.

`build_services` builds the real stack, HealthService first (Session 54 RULE-2), and a recording
fake `FramePort` replaces the capture service's FFmpeg adapter, so no FFmpeg runs here. The
tiling and the annotate probe are the real Pillow `CaptureAdapter`, and the rows are in the real
SQLite file.
"""

from __future__ import annotations

import dataclasses
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
SHEET = "/api/v1/captures/sheet"
SETTINGS = "/api/v1/settings/capture"
CONSOLE = "/api/v1/health/console"
PNG_SIGNATURE = bytes.fromhex("89504e470d0a1a0a")
SHEET_KEYS = {"video", "shot", "spacing_ms", "cells"}
VIDEO_KEYS = {"path", "duration_ms", "width", "height", "fps"}
SHOT_KEYS = {"id", "path", "width", "height"}
CELL_KEYS = {"cell", "time_ms", "timecode"}
SCHEMA_REFUSAL = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
MASKED = ("internal_error", "Internal server error")
NOT_FOUND = "video file not found"
LOCAL = "path must be a local absolute file path"
NOT_PROBED = "the file could not be probed"
NO_DURATION = "sheet needs a duration; this video has none"
TIME_TEXT = "a time must be seconds or HH:MM:SS.mmm"
SHEET_NAME = "clip-sheet-00h00m00s-00h00m03s.png"
TMP = ".avkit-tmp"
#: FRAME_TIMES of [0, 3000) in 9 and 4 parts: the default grid's and grid 2's cells.
TIMES_9 = [167, 500, 833, 1167, 1500, 1833, 2167, 2500, 2833]
TIMES_4 = [375, 1125, 1875, 2625]
#: A 320x240 source at grid 3 and max_edge 1568 (the defaults), from the planning probe.
CELL_DEFAULT = (417, 313)


def _png(colour: tuple[int, int, int], size: tuple[int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


class FakeFrames:
    """A recording `FramePort`: a solid PNG of the box size, or `b""`, or raises as told."""

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
        self.boxes: list[tuple[int, int] | None] = []

    def probe(self, file_path: Path, *, timeout_s: float | None = None) -> MediaInfo:
        del timeout_s
        self.probes.append(file_path)
        if self.probe_error is not None:
            raise self.probe_error
        return self.info

    def grab_frame(
        self,
        path: Path,
        time_ms: int,
        *,
        seek: str,
        timeout_s: float,
        box: tuple[int, int] | None = None,
    ) -> bytes:
        del path, seek, timeout_s
        self.grabs.append(time_ms)
        self.boxes.append(box)
        if self.grab_error is not None:
            raise self.grab_error
        if self.answer is not None:
            return self.answer
        return _png((time_ms % 256, 90, 160), box or (8, 6))


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


# AC-135.15 request and response ----------------------------------------------------------------


def test_ac_135_15_sheet_answers_201_with_its_four_keys(tmp_path: Path) -> None:
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(SHEET, headers=AUTH, json={"path": str(clip)})
        assert response.status_code == 201, response.text
        payload = response.json()
        assert set(payload) == SHEET_KEYS
        assert set(payload["video"]) == VIDEO_KEYS
        assert payload["video"] == {
            "path": str(clip.resolve()),
            "duration_ms": 3000,
            "width": 320,
            "height": 240,
            "fps": 25.0,
        }
        assert set(payload["shot"]) == SHOT_KEYS
        # The defaults: grid 3, so 9 cells, and max_edge 1568.
        assert [set(cell) for cell in payload["cells"]] == [CELL_KEYS] * 9
        assert [cell["cell"] for cell in payload["cells"]] == list(range(1, 10))
        assert [cell["time_ms"] for cell in payload["cells"]] == TIMES_9
        assert payload["cells"][0]["timecode"] == "00:00:00.167"
        assert payload["cells"][-1]["timecode"] == "00:00:02.833"
        assert payload["spacing_ms"] == 333
        assert fake.grabs == TIMES_9
        assert set(fake.boxes) == {CELL_DEFAULT}
        shot = payload["shot"]
        path = Path(shot["path"])
        assert path.parent == inbox.resolve()
        assert path.name == SHEET_NAME
        data = path.read_bytes()
        assert data.startswith(PNG_SIGNATURE)
        with Image.open(io.BytesIO(data)) as image:
            assert image.size == (3 * 417, 3 * 313)
        assert (shot["width"], shot["height"]) == (1251, 939)
        assert [row.id for row in _rows(services)] == [shot["id"]]
        assert sorted(child.name for child in inbox.iterdir()) == [SHEET_NAME]
    assert clip.read_bytes() == b"video"


def test_ac_135_15_grid_max_edge_and_a_span(tmp_path: Path) -> None:
    clip = _clip(tmp_path / "videos")
    body = {"path": str(clip), "grid": 2, "max_edge": 64, "start": 0, "end": "00:00:03"}
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(SHEET, headers=AUTH, json=body)
        assert response.status_code == 201, response.text
        payload = response.json()
        assert set(payload) == SHEET_KEYS
        assert [cell["time_ms"] for cell in payload["cells"]] == TIMES_4
        assert payload["spacing_ms"] == 750
        assert set(fake.boxes) == {(32, 24)}
        assert (payload["shot"]["width"], payload["shot"]["height"]) == (64, 48)


REFUSALS: list[tuple[str, dict[str, object]]] = [
    ("extra-key", {"extra": 1}),
    ("grid-1", {"grid": 1}),
    ("grid-6", {"grid": 6}),
    ("grid-null", {"grid": None}),
    ("grid-true", {"grid": True}),
    ("grid-2.5", {"grid": 2.5}),
    ("grid-huge", {"grid": 10**18}),
    ("edge-63", {"max_edge": 63}),
    ("edge-2577", {"max_edge": 2577}),
    ("edge-null", {"max_edge": None}),
    ("edge-huge", {"max_edge": 10**18}),
    ("start-true", {"start": True}),
    ("end-true", {"end": True}),
    ("start-null-in-a-list", {"start": [None]}),
    ("start-null-in-an-object", {"start": {"s": None}}),
    ("end-null-in-a-list", {"end": [None]}),
]


@pytest.mark.parametrize(("case", "body"), REFUSALS, ids=[case for case, _ in REFUSALS])
def test_ac_135_15_schema_refusals(tmp_path: Path, case: str, body: dict[str, object]) -> None:
    del case
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(SHEET, headers=AUTH, json={"path": str(clip), **body})
        assert response.status_code == 422, response.text
        assert response.json() == SCHEMA_REFUSAL
        assert fake.probes == []
        assert fake.grabs == []
        assert list(inbox.iterdir()) == []
        assert _rows(services) == []


@pytest.mark.parametrize(
    "path", ["", 123, "x" * 4097], ids=["empty-path", "non-string-path", "long-path"]
)
def test_ac_135_15_path_schema_refusals(tmp_path: Path, path: object) -> None:
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(SHEET, headers=AUTH, json={"path": path})
        assert response.status_code == 422, response.text
        assert response.json() == SCHEMA_REFUSAL
        missing = client.post(SHEET, headers=AUTH, json={"grid": 2})
        assert missing.status_code == 422, missing.text
        assert missing.json() == SCHEMA_REFUSAL
        assert fake.probes == []
        assert fake.grabs == []


@pytest.mark.parametrize(
    "body",
    [{"start": 1e308}, {"start": 1e25}, {"end": 1e308}, {"start": 0, "end": 1e25}],
    ids=["start-1e308", "start-1e25", "end-1e308", "end-1e25"],
)
def test_ac_135_15_huge_finite_times_get_the_fixed_refusal(
    tmp_path: Path, body: dict[str, object]
) -> None:
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(SHEET, headers=AUTH, json={"path": str(clip), **body})
        assert response.status_code == 422, response.text
        assert _error(response) == ("ValidationError", TIME_TEXT)
        assert fake.probes == []
        assert fake.grabs == []
        assert list(inbox.iterdir()) == []
        assert _rows(services) == []
    assert clip.read_bytes() == b"video"


# AC-135.16 errors name no path -----------------------------------------------------------------


def test_ac_135_16_errors_name_no_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    import structlog

    from avkit_core.services import capture as capture_mod
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    marker = f"s63MARKER{uuid4().hex}"
    folder = tmp_path / f"videos-{marker}"
    clip = _clip(folder, f"clip-{marker}.mp4")
    link = folder / f"loop-{marker}.mp4"
    responses: list[Any] = []
    with _stack(tmp_path, f"app-{marker}") as (client, services, fake, inbox):

        def post(**body: object) -> Any:
            return client.post(SHEET, headers=AUTH, json={"path": str(clip), "grid": 2, **body})

        gone = folder / f"gone-{marker}.mp4"
        missing = client.post(SHEET, headers=AUTH, json={"path": str(gone)})
        with _looping(link):
            loop = client.post(SHEET, headers=AUTH, json={"path": str(link)})
        url = client.post(SHEET, headers=AUTH, json={"path": f"http://x/{marker}.mp4"})
        assert fake.probes == []
        assert fake.grabs == []
        past = post(start=3)
        fake.probe_error = MediaProbeError(f"{clip}: Invalid data found {marker}")
        unprobed = post()
        fake.probe_error = None
        original = fake.info
        fake.info = dataclasses.replace(original, duration=None, container="h264")
        undated = post()
        fake.info = original
        assert fake.grabs == []
        fake.answer = b""
        empty = post()
        fake.answer = None
        fake.grab_error = FFmpegNotFoundError(f"ffmpeg binary was not found {marker}")
        unavailable = post()
        fake.grab_error = None
        with monkeypatch.context() as patch:
            patch.setattr(capture_mod, "os", _OsProxy(marker))
            unwritten = post()
        responses = [missing, loop, url, past, unprobed, undated, empty, unavailable, unwritten]
        assert [response.status_code for response in responses] == [
            422,
            422,
            422,
            422,
            422,
            422,
            422,
            503,
            503,
        ]
        assert [_error(response) for response in responses[:7]] == [
            ("ValidationError", NOT_FOUND),
            ("ValidationError", NOT_FOUND),
            ("ValidationError", LOCAL),
            ("ValidationError", "time 00:00:03.000 is past the end (00:00:03.000)"),
            ("ValidationError", NOT_PROBED),
            ("ValidationError", NO_DURATION),
            ("ValidationError", "frame grab failed at 00:00:00.375"),
        ]
        assert [_error(response) for response in responses[7:]] == [MASKED, MASKED]
        assert fake.grabs == [375, 375, *TIMES_4]
        assert list(inbox.iterdir()) == []
        assert _rows(services) == []
        ring = client.get(CONSOLE, headers=AUTH)
        assert ring.status_code == 200
        messages = [item["message"] for item in ring.json()["items"]]
        captured = capfd.readouterr()
        # The positive control: one line that does hold the marker reaches the ring and stdout.
        structlog.get_logger(module="capture").info("sheet.control", detail=marker)
        control_ring = client.get(CONSOLE, headers=AUTH)
        control_messages = [item["message"] for item in control_ring.json()["items"]]
        control = capfd.readouterr()
    folded = marker.casefold()
    assert [response.text for response in responses if folded in response.text.casefold()] == []
    assert [message for message in messages if folded in message.casefold()] == []
    lines = (captured.out + captured.err).splitlines()
    assert [line for line in lines if folded in line.casefold()] == []
    assert sum(folded in message.casefold() for message in control_messages) == 1
    assert sum(folded in line.casefold() for line in control.out.splitlines()) >= 1


# AC-135.17 the sheet is a shot with source Video ----------------------------------------------


def test_ac_135_17_the_sheet_is_a_video_shot_and_a_scan_keeps_it(tmp_path: Path) -> None:
    clip = _clip(tmp_path / "videos")
    with _stack(tmp_path) as (client, services, fake, inbox):
        response = client.post(SHEET, headers=AUTH, json={"path": str(clip), "grid": 2})
        assert response.status_code == 201, response.text
        shot = response.json()["shot"]
        assert set(shot) == SHOT_KEYS
        listed = client.get(CAPTURES, headers=AUTH)
        assert listed.status_code == 200
        items = {item["id"]: item for item in listed.json()["items"]}
        assert shot["id"] in items
        assert items[shot["id"]]["source"] == "Video"
        assert (items[shot["id"]]["width"], items[shot["id"]]["height"]) == (1250, 938)
        detail = client.get(f"{CAPTURES}/{shot['id']}", headers=AUTH)
        assert detail.status_code == 200, detail.text
        assert detail.json()["source"] == "Video"
        assert detail.json()["original_path"] == shot["path"]
        image = client.get(f"{CAPTURES}/{shot['id']}/image", headers=AUTH)
        assert image.status_code == 200
        assert image.content == Path(shot["path"]).read_bytes()
        Image.new("RGB", (4, 4), (0, 0, 0)).save(inbox / "dropped.png")
        rescanned = client.get(CAPTURES, headers=AUTH)
        assert rescanned.status_code == 200
        sources = {
            Path(item["original_path"]).name: item["source"] for item in rescanned.json()["items"]
        }
        assert sources == {SHEET_NAME: "Video", "dropped.png": "Scan"}
        assert not [path for path in inbox.iterdir() if path.name.endswith(TMP)]
