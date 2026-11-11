"""MEU-132 AC-132.21: a dropped or chosen file's name through the real import route (Session 61).

A characterisation guard for the names the GUI import hands MEU-129's route, written from the
plan-time `name-probe.py`. The body travels as raw JSON text, so a lone surrogate arrives as the
`\\ud800` escape a renderer's `JSON.stringify` writes. Every image is a Pillow image under
tmp_path; nothing reaches the network.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from avkit_api.main import create_app
from avkit_api.wiring import build_services

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN})
HEADERS = {"Authorization": f"Bearer {GUI_TOKEN}", "Content-Type": "application/json"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"


@contextmanager
def _stack(tmp_path: Path, inbox: Path) -> Iterator[TestClient]:
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=HEADERS, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            yield client
    finally:
        dispose()


def _import(client: TestClient, path: str):
    # ensure_ascii writes a lone surrogate as its escape, as the renderer's JSON.stringify does.
    body = json.dumps({"mode": "import", "path": path})
    return client.post(PREFIX, headers=HEADERS, content=body.encode("ascii"))


def _message(response) -> str:
    error = response.json().get("error", {})
    return str(error.get("message")) if isinstance(error, dict) else str(error)


@pytest.mark.parametrize("ac_id", ["AC-132.21"], ids=["AC-132.21"])
def test_ac_132_21_import_names(
    ac_id: str, tmp_path: Path, capfd: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-132.21"
    marker = f"s61NAME{uuid4().hex}"
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    outside = tmp_path / f"outside-{marker}"
    outside.mkdir()
    lone = outside / "snip\ud800x.png"
    Image.new("RGB", (5, 4), (9, 9, 9)).save(str(lone))

    # The positive control: the search below finds the folder in a body built to hold it.
    built = json.dumps({"error": {"message": str(outside)}})
    assert marker in built

    with _stack(tmp_path, inbox) as client:
        stored = _import(client, str(lone))
        assert stored.status_code == 201, stored.text
        item = stored.json().get("item", stored.json())
        assert item["display_name"] == "snip_x.png"
        assert Path(item["original_path"]).name == "snip_x.png"

        bell = _import(client, str(outside / "snip\x07.png"))
        assert bell.status_code == 422, bell.text
        assert _message(bell) == "no file at that path"
        assert marker not in bell.text

        empty = _import(client, "")
        assert empty.status_code == 422, empty.text
        assert _message(empty) == "path must be absolute"
        assert marker not in empty.text

    captured = capfd.readouterr()
    assert marker not in captured.out + captured.err
