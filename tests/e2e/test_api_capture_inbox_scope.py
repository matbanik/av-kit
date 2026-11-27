"""MEU-166 (Session 103): `GET /captures` follows the inbox folder (AC-166.4), real stack.

`build_services` on a tmp_path profile, as tests/e2e/test_api_capture_import_names.py builds
it. Folders A (two PNG files) and B (one) are tmp_path folders; nothing reaches the network.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from avkit_api.main import create_app
from avkit_api.wiring import build_services

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN})
HEADERS = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"
UNKNOWN_ID = "00000000-0000-4000-8000-000000000000"


@contextmanager
def _client(root: Path) -> Iterator[TestClient]:
    services, dispose = build_services(app_data=root, database_path=root / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield client
    finally:
        dispose()


def _png(path: Path, colour: tuple[int, int, int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (64, 48), colour).save(path, format="PNG")
    return path.resolve()


def _use(client: TestClient, folder: Path) -> None:
    put = client.put(SETTINGS, headers=HEADERS, json={"inbox_dir": str(folder)})
    assert put.status_code == 200, put.text


def _shape(response: Any, shot_id: str) -> object:
    return json.loads(response.text.replace(shot_id, "<id>"))


def _digests(folder: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(folder.iterdir())
        if path.is_file()
    }


@pytest.mark.parametrize("ac_id", ["AC-166.4"], ids=["AC-166.4"])
def test_ac_166_4_api_list_follows_inbox(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-166.4"
    root = tmp_path.resolve()
    profile = root / "profile"
    profile.mkdir()
    a = root / "inbox-a"
    b = root / "inbox-b"
    _png(a / "a-1.png", (200, 30, 30))
    _png(a / "a-2.png", (30, 200, 30))
    _png(b / "b-1.png", (30, 30, 200))
    with _client(profile) as client:
        _use(client, a)
        listed_a = client.get(PREFIX, headers=HEADERS)
        assert listed_a.status_code == 200
        reply_a = listed_a.json()
        items_a = reply_a["items"]
        assert sorted(item["display_name"] for item in items_a) == ["a-1.png", "a-2.png"]
        reply_keys = set(reply_a)
        item_keys = set(items_a[0])
        a_id = str(items_a[0]["id"])
        a_files = _digests(a)

        _use(client, b)
        listed_b = client.get(PREFIX, headers=HEADERS)
        assert listed_b.status_code == 200
        reply_b = listed_b.json()
        assert set(reply_b) == reply_keys, "the reply keeps its key set"
        names_b = [item["display_name"] for item in reply_b["items"]]
        assert names_b == ["b-1.png"], "inbox B lists only B's shot"
        assert all(set(item) == item_keys for item in reply_b["items"])

        unknown_read = client.get(f"{PREFIX}/{UNKNOWN_ID}", headers=HEADERS)
        outside_read = client.get(f"{PREFIX}/{a_id}", headers=HEADERS)
        assert unknown_read.status_code == 404
        assert outside_read.status_code == 404, "an A id on inbox B reads as unknown"
        assert _shape(outside_read, a_id) == _shape(unknown_read, UNKNOWN_ID)

        body = {"annotations": []}
        unknown_write = client.post(f"{PREFIX}/{UNKNOWN_ID}/annotate", headers=HEADERS, json=body)
        outside_write = client.post(f"{PREFIX}/{a_id}/annotate", headers=HEADERS, json=body)
        assert unknown_write.status_code == 404
        assert outside_write.status_code == 404, "a write to an A id on inbox B is refused"
        assert _shape(outside_write, a_id) == _shape(unknown_write, UNKNOWN_ID)
        assert _digests(a) == a_files, "A's files are kept and unchanged"

        _use(client, a)
        again = client.get(f"{PREFIX}/{a_id}", headers=HEADERS)
        assert again.status_code == 200, "back on A the same id answers"
