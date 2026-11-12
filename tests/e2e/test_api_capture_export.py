"""MEU-136 capture export on the real stack (Session 64). AC-136.13 to AC-136.15.

`POST /captures/{id}/export` writes a resized or re-encoded copy as a new shot with source
`Export`. Every test builds its images with Pillow under tmp_path; nothing reaches the network.
Each test asserts the status code first, so a Red fails by an assertion.
"""

from __future__ import annotations

import json
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

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
JSON_AUTH = AUTH | {"Content-Type": "application/json"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"
CONSOLE = "/api/v1/health/console"
TMP = ".avkit-tmp"
VALIDATION = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
MASKED = ("internal_error", "Internal server error")
QUALITY_PNG = "quality applies to jpeg and webp only"
NO_BAKE = "annotated image is missing"
NOT_OPENED = "the image could not be opened"
RESPONSE_KEYS = {"shot", "source_id"}
SHOT_KEYS = {"id", "path", "width", "height", "bytes"}
PIL_FORMAT = {"png": "PNG", "jpeg": "JPEG", "webp": "WEBP"}
BASE = (40, 90, 140)


def _ac(label: str) -> pytest.MarkDecorator:
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@contextmanager
def _stack(app_data: Path, inbox: Path) -> Iterator[tuple[TestClient, Any]]:
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            yield client, services
    finally:
        dispose()


def _inbox(root: Path) -> Path:
    inbox = root / "inbox"
    inbox.mkdir(parents=True)
    return inbox


def _source(path: Path, size: tuple[int, int] = (300, 200)) -> Path:
    image = Image.new("RGB", size, BASE)
    image.paste((230, 200, 30), (size[0] // 2, 0, size[0], size[1] // 2))
    image.save(path, format="PNG")
    return path


def _shot_id(client: TestClient, name: str) -> str:
    listed = client.get(PREFIX, headers=AUTH)
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    ids = [item["id"] for item in items if Path(item["original_path"]).name == name]
    assert len(ids) == 1, items
    return ids[0]


def _export(client: TestClient, shot_id: str, body: dict[str, Any]) -> Any:
    return client.post(f"{PREFIX}/{shot_id}/export", headers=AUTH, json=body)


def _export_text(client: TestClient, shot_id: str, text: str) -> Any:
    """A raw JSON body, so `64.0` reaches the API as a JSON float (round 1 F3)."""
    return client.post(f"{PREFIX}/{shot_id}/export", headers=JSON_AUTH, content=text)


def _annotate(client: TestClient, shot_id: str, marks: list[dict[str, Any]]) -> None:
    response = client.post(
        f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": marks}
    )
    assert response.status_code == 200, response.text


def _rect(x: int, y: int, width: int, height: int, stroke: int = 6) -> dict[str, Any]:
    mark: dict[str, Any] = {"type": "rect", "x": x, "y": y, "width": width, "height": height}
    return mark | {"color": "red", "stroke_width": stroke}


def _error(response: Any) -> tuple[Any, Any]:
    body = response.json()
    error = body.get("error") if isinstance(body, dict) else None
    if not isinstance(error, dict):
        return ("no error envelope", body)
    return error.get("code"), error.get("message")


def _names(folder: Path) -> list[str]:
    return sorted(child.name for child in folder.iterdir())


def _items(client: TestClient) -> dict[str, dict[str, Any]]:
    listed = client.get(PREFIX, headers=AUTH)
    assert listed.status_code == 200, listed.text
    return {item["id"]: item for item in listed.json()["items"]}


def _opened(path: str | Path) -> tuple[str | None, tuple[int, int], dict[str, Any], int]:
    with Image.open(path) as image:
        image.load()
        return image.format, image.size, dict(image.info), len(image.getexif())


# --- AC-136.13: the 201 and the new shot -------------------------------------------------------


@_ac("AC-136.13")
@pytest.mark.e2e
def test_ac_136_13_export_answers_201_with_a_new_shot(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.13"
    inbox = _inbox(tmp_path)
    source = _source(inbox / "shot.png")
    source_bytes = source.read_bytes()
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        made: list[tuple[str, dict[str, Any]]] = []
        for fmt in ("png", "jpeg", "webp"):
            response = _export(client, shot_id, {"format": fmt})
            assert response.status_code == 201, response.text
            body = response.json()
            assert set(body) == RESPONSE_KEYS
            assert set(body["shot"]) == SHOT_KEYS
            assert body["source_id"] == shot_id
            made.append((fmt, body["shot"]))
        assert [Path(shot["path"]).name for _, shot in made] == [
            "shot-export.png",
            "shot-export_2.jpg",
            "shot-export_3.webp",
        ]
        for fmt, shot in made:
            path = Path(shot["path"])
            assert path.parent == inbox.resolve()
            image_format, size, info, exif_count = _opened(path)
            assert (image_format, size) == (PIL_FORMAT[fmt], (300, 200))
            assert (shot["width"], shot["height"]) == (300, 200)
            assert shot["bytes"] == path.stat().st_size
            assert "exif" not in info
            assert exif_count == 0
        small = _export(client, shot_id, {"format": "jpeg", "max_edge": 64, "quality": 50})
        assert small.status_code == 201, small.text
        assert (small.json()["shot"]["width"], small.json()["shot"]["height"]) == (64, 43)
        assert _opened(small.json()["shot"]["path"])[1] == (64, 43)
        same = _export(client, shot_id, {"format": "webp", "max_edge": 1000})
        assert same.status_code == 201, same.text
        assert (same.json()["shot"]["width"], same.json()["shot"]["height"]) == (300, 200)
        assert source.read_bytes() == source_bytes
        export_id = made[0][1]["id"]
        detail = client.get(f"{PREFIX}/{export_id}", headers=AUTH)
        assert detail.status_code == 200, detail.text
        assert detail.json()["source"] == "Export"
        assert detail.json()["original_path"] == made[0][1]["path"]
        assert detail.json()["annotated_path"] is None
        Image.new("RGB", (4, 4), (0, 0, 0)).save(inbox / "dropped.png")
        items = _items(client)
        assert items[export_id]["source"] == "Export"
        assert sorted(item["source"] for item in items.values()).count("Export") == 5
        assert not [name for name in _names(inbox) if name.endswith(TMP)]


@_ac("AC-136.13")
@pytest.mark.e2e
def test_ac_136_13_a_marked_shot_exports_its_bake(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.13"
    inbox = _inbox(tmp_path)
    source = _source(inbox / "marked.png")
    source_bytes = source.read_bytes()
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "marked.png")
        _annotate(client, shot_id, [_rect(20, 20, 60, 40)])
        response = _export(client, shot_id, {"format": "png"})
        assert response.status_code == 201, response.text
        path = Path(response.json()["shot"]["path"])
        assert path.name == "marked-export.png"
        with Image.open(path) as exported, Image.open(source) as original:
            under = exported.convert("RGB").getpixel((20, 40))
            plain = original.convert("RGB").getpixel((20, 40))
        assert plain == BASE
        assert isinstance(under, tuple)
        assert under[0] > 200 and under[1] < 60 and under[2] < 60, under
        assert source.read_bytes() == source_bytes
        again = _export(client, shot_id, {"format": "png"})
        assert again.status_code == 201, again.text
        assert Path(again.json()["shot"]["path"]).name == "marked-export_2.png"


# --- AC-136.14: route validation ---------------------------------------------------------------

SCHEMA_REFUSALS: tuple[tuple[str, str], ...] = (
    ("extra-key", '{"format": "png", "nope": true}'),
    ("missing-format", "{}"),
    ("format-gif", '{"format": "gif"}'),
    ("edge-63", '{"format": "png", "max_edge": 63}'),
    ("edge-16384", '{"format": "png", "max_edge": 16384}'),
    ("edge-null", '{"format": "png", "max_edge": null}'),
    ("edge-true", '{"format": "png", "max_edge": true}'),
    ("edge-64.0", '{"format": "png", "max_edge": 64.0}'),
    ("edge-64.5", '{"format": "png", "max_edge": 64.5}'),
    ("edge-1e18", '{"format": "png", "max_edge": 1000000000000000000}'),
    ("edge-1e308", '{"format": "png", "max_edge": 1e308}'),
    ("quality-0", '{"format": "jpeg", "quality": 0}'),
    ("quality-101", '{"format": "jpeg", "quality": 101}'),
    ("quality-null", '{"format": "jpeg", "quality": null}'),
    ("quality-true", '{"format": "jpeg", "quality": true}'),
    ("quality-80.0", '{"format": "jpeg", "quality": 80.0}'),
    ("quality-1e18", '{"format": "jpeg", "quality": 1000000000000000000}'),
)


@_ac("AC-136.14")
@pytest.mark.e2e
def test_ac_136_14_route_validation(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-136.14"
    inbox = _inbox(tmp_path)
    _source(inbox / "shot.png")
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        before_names, before_items = _names(inbox), _items(client)
        # The route exists: a valid body is not refused by the schema.
        probe = _export(client, "no-such-shot", {"format": "png"})
        assert probe.status_code == 404, probe.text
        assert _error(probe) == ("NotFoundError", "capture shot no-such-shot not found")
        statuses = {label: _export_text(client, shot_id, text) for label, text in SCHEMA_REFUSALS}
        assert {label: r.status_code for label, r in statuses.items()} == {
            label: 422 for label, _ in SCHEMA_REFUSALS
        }
        assert {label: r.json() for label, r in statuses.items()} == {
            label: VALIDATION for label, _ in SCHEMA_REFUSALS
        }
        # Each body is valid JSON, so every refusal is the schema's, not the parser's.
        assert all(isinstance(json.loads(text), dict) for _, text in SCHEMA_REFUSALS)
        png_quality = _export(client, shot_id, {"format": "png", "quality": 50})
        assert png_quality.status_code == 422, png_quality.text
        assert _error(png_quality) == ("ValidationError", QUALITY_PNG)
        assert _names(inbox) == before_names
        assert _items(client) == before_items


# --- AC-136.15: errors name no path ------------------------------------------------------------


class _OsProxy:
    """The capture module's `os`, with `replace` raising an error that names a marker."""

    def __init__(self, marker: str) -> None:
        self._marker = marker

    def replace(self, source: Any, dest: Any) -> None:
        raise OSError(f"{dest}: access denied {self._marker}")

    def __getattr__(self, name: str) -> object:
        return getattr(os, name)


@_ac("AC-136.15")
@pytest.mark.e2e
def test_ac_136_15_errors_name_no_path(
    ac_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    assert ac_id == "AC-136.15"
    import structlog

    from avkit_core.services import capture as capture_mod
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    marker = f"s64MARKER{uuid4().hex}"
    app_data = tmp_path / f"app-{marker}"
    inbox = _inbox(app_data / f"inbox-{marker}")
    marked = _source(inbox / f"marked-{marker}.png")
    broken = _source(inbox / f"broken-{marker}.png")
    plain = _source(inbox / f"plain-{marker}.png")
    responses: list[Any] = []
    with _stack(app_data, inbox) as (client, _services):
        ids = {path.name: _shot_id(client, path.name) for path in (marked, broken, plain)}
        _annotate(client, ids[marked.name], [_rect(20, 20, 60, 40)])
        bakes = [path for path in inbox.iterdir() if ".annotated." in path.name]
        assert len(bakes) == 1, _names(inbox)
        bakes[0].unlink()
        no_bake = _export(client, ids[marked.name], {"format": "png"})
        broken.write_bytes(b"\x89PNG\r\n\x1a\nnot really an image " + marker.encode())
        undecodable = _export(client, ids[broken.name], {"format": "jpeg"})
        before_names = _names(inbox)
        with monkeypatch.context() as patch:
            assert hasattr(capture_mod, "os")
            patch.setattr(capture_mod, "os", _OsProxy(marker))
            unwritten = _export(client, ids[plain.name], {"format": "webp"})
        responses = [no_bake, undecodable, unwritten]
        assert [response.status_code for response in responses] == [404, 422, 503]
        assert [_error(response) for response in responses] == [
            ("NotFoundError", NO_BAKE),
            ("InboxPathError", NOT_OPENED),
            MASKED,
        ]
        assert _names(inbox) == before_names
        ring = client.get(CONSOLE, headers=AUTH)
        assert ring.status_code == 200
        messages = [item["message"] for item in ring.json()["items"]]
        captured = capfd.readouterr()
        # The positive control: one line that does hold the marker reaches the ring and stdout.
        structlog.get_logger(module="capture").info("export.control", detail=marker)
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
