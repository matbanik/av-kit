"""MEU-145 (Session 75) on the real stack: `GET /captures` lists past an unreadable file.

AC-145.12 and AC-145.13. Each test builds its images with Pillow under tmp_path, in an
inbox folder whose name holds `s75mark`, so a path in a body would match. The client is
`TestClient(app, raise_server_exceptions=False)`, so a 500 is an answer, not a raise.
"""

from __future__ import annotations

import io
import json
import random
import struct
import zlib
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"
MARK = "s75mark"


def _ac145(n: int) -> pytest.MarkDecorator:
    label = f"AC-145.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@contextmanager
def _stack(app_data: Path, inbox: Path) -> Iterator[TestClient]:
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app, raise_server_exceptions=False) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200, put.text
            yield client
    finally:
        dispose()


def _inbox(tmp_path: Path) -> Path:
    inbox = tmp_path / f"{MARK}-inbox"
    inbox.mkdir()
    return inbox


def _png(seed: int, size: tuple[int, int] = (40, 30)) -> bytes:
    """A PNG of random pixels, so its IDAT is long enough to split in place."""
    from PIL import Image

    rng = random.Random(seed)
    pixels = bytes(rng.randrange(256) for _ in range(size[0] * size[1] * 3))
    buffer = io.BytesIO()
    Image.frombytes("RGB", size, pixels).save(buffer, format="PNG")
    return buffer.getvalue()


def _damaged(data: bytes) -> bytes:
    """The IDAT split into a 4-byte IDAT and a BAD! chunk, as AC-130.21 damages a source."""
    at = data.index(b"IDAT") - 4
    (length,) = struct.unpack(">I", data[at : at + 4])
    end = at + 12 + length
    body = data[at + 8 : at + 12]
    idat = struct.pack(">I", 4) + b"IDAT" + body + struct.pack(">I", zlib.crc32(b"IDAT" + body))
    filler = b"\0" * (length - 16)
    bad = struct.pack(">I", len(filler)) + b"BAD!" + filler
    bad += struct.pack(">I", zlib.crc32(b"BAD!" + filler))
    damaged = data[:at] + idat + bad + data[end:]
    assert len(damaged) == len(data)
    return damaged


def _listed(response: Any) -> list[str]:
    assert response.status_code == 200, f"list answered {response.status_code}"
    return sorted(Path(item["original_path"]).name for item in response.json()["items"])


@_ac145(12)
@pytest.mark.unit
def test_ac_145_12_list_skips_non_image_and_damaged_png(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.12"
    inbox = _inbox(tmp_path)
    (inbox / "a.png").write_bytes(_png(1))
    (inbox / "b.png").write_bytes(_png(2))
    (inbox / "fake.png").write_bytes(f"not an image {MARK}".encode())
    (inbox / "broken.png").write_bytes(_damaged(_png(3)))
    with _stack(tmp_path, inbox) as client:
        response = client.get(PREFIX, headers=AUTH)
        assert _listed(response) == ["a.png", "b.png"]
        text = response.text
        # The two listed shots' own paths hold the marker; nothing else in the body may.
        assert MARK in text, "the marker check cannot see the listed paths"
        rest = text
        for item in response.json()["items"]:
            rest = rest.replace(json.dumps(item["original_path"])[1:-1], "")
        for part in (MARK, "fake.png", "broken.png", "not an image", "BAD!"):
            assert part not in rest, "the body names an unreadable file"


@_ac145(13)
@pytest.mark.unit
def test_ac_145_13_list_picks_up_a_file_once_it_reads(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-145.13"
    inbox = _inbox(tmp_path)
    (inbox / "a.png").write_bytes(_png(1))
    late = inbox / "late.png"
    late.write_bytes(b"half-written, not yet an image")
    with _stack(tmp_path, inbox) as client:
        assert _listed(client.get(PREFIX, headers=AUTH)) == ["a.png"]
        late.write_bytes(_png(4))
        assert _listed(client.get(PREFIX, headers=AUTH)) == ["a.png", "late.png"]
