"""MEU-146 (Session 75) on the real stack: a tagged shot has one frame through the API.

AC-146.15 to AC-146.18, AC-146.27 and AC-146.28. Each test writes 400x300 images with
Pillow under tmp_path (blue, a red 40x40 block at the top left) tagged with an EXIF
orientation. The client is `TestClient(app, raise_server_exceptions=False)`, so a 500 is
an answer, not a raise.
"""

from __future__ import annotations

import io
import json
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
SIZE = (400, 300)
TURNED = (300, 400)
BLUE = (20, 20, 200)
RED = (230, 20, 20)
TAG = 0x0112
PIL_FORMAT = {".jpg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
GREEN_MARK = {"type": "redact", "x": 100, "y": 330, "width": 40, "height": 40, "color": "#00FF00"}


def _ac146(n: int) -> pytest.MarkDecorator:
    label = f"AC-146.{n}"
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
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    return inbox


def _tagged(suffix: str, tag: int | None) -> bytes:
    """The 400x300 frame in the format `suffix` names, tagged `tag` (None: no EXIF block)."""
    from PIL import Image

    image = Image.new("RGB", SIZE, BLUE)
    image.paste(RED, (0, 0, 40, 40))
    params: dict[str, object] = {}
    if suffix != ".png":
        params["quality"] = 95
    if tag is not None:
        exif = Image.Exif()
        exif[TAG] = tag
        params["exif"] = exif.tobytes()
    buffer = io.BytesIO()
    image.save(buffer, format=PIL_FORMAT[suffix], **params)
    return buffer.getvalue()


def _look(data: bytes) -> tuple[str | None, tuple[int, int], Any, object]:
    """Decode `data`: format, size, RGB pixels and the orientation tag."""
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        fmt = image.format
        image.load()
        tag = image.getexif().get(TAG)
        rgb = image.convert("RGB")
    return fmt, rgb.size, rgb, tag


def _red(pixel: tuple[int, ...]) -> bool:
    return pixel[0] > 200 and pixel[1] < 60 and pixel[2] < 60


def _green(pixel: tuple[int, ...]) -> bool:
    return pixel[1] > 200 and pixel[0] < 60 and pixel[2] < 60


def _items(client: TestClient) -> dict[str, dict[str, Any]]:
    response = client.get(PREFIX, headers=AUTH)
    assert response.status_code == 200, f"list answered {response.status_code}"
    return {Path(item["original_path"]).name: item for item in response.json()["items"]}


@_ac146(15)
@pytest.mark.unit
def test_ac_146_15_list_gives_the_shown_size(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.15"
    inbox = _inbox(tmp_path)
    expected: dict[str, tuple[int, int]] = {}
    for suffix in (".jpg", ".png"):
        for tag in range(1, 9):
            name = f"t{tag}{suffix}"
            (inbox / name).write_bytes(_tagged(suffix, tag))
            expected[name] = TURNED if tag >= 5 else SIZE
    (inbox / "t6.webp").write_bytes(_tagged(".webp", 6))
    expected["t6.webp"] = SIZE
    with _stack(tmp_path, inbox) as client:
        items = _items(client)
    listed = {name: (item["width"], item["height"]) for name, item in items.items()}
    assert listed == expected


@_ac146(16)
@pytest.mark.unit
def test_ac_146_16_region_view_is_cut_from_the_shown_frame(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.16"
    inbox = _inbox(tmp_path)
    (inbox / "t6.jpg").write_bytes(_tagged(".jpg", 6))
    with _stack(tmp_path, inbox) as client:
        shot_id = _items(client)["t6.jpg"]["id"]
        response = client.get(
            f"{PREFIX}/{shot_id}/image",
            headers=AUTH,
            params={"x": 260, "y": 0, "width": 40, "height": 40},
        )
    assert response.status_code == 200, f"the region answered {response.status_code}"
    _fmt, size, rgb, _tag = _look(response.content)
    assert size == (160, 160)
    assert _red(rgb.getpixel((20, 20))), "the region centre is not red"
    assert response.headers["X-Capture-Source"] == "300,400"


@_ac146(17)
@pytest.mark.unit
def test_ac_146_17_plain_image_of_a_tagged_jpeg_is_upright(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.17"
    inbox = _inbox(tmp_path)
    (inbox / "t6.jpg").write_bytes(_tagged(".jpg", 6))
    with _stack(tmp_path, inbox) as client:
        shot_id = _items(client)["t6.jpg"]["id"]
        response = client.get(f"{PREFIX}/{shot_id}/image", headers=AUTH)
    assert response.status_code == 200, f"the image answered {response.status_code}"
    fmt, size, rgb, tag = _look(response.content)
    assert (fmt, size) == ("JPEG", TURNED)
    assert _red(rgb.getpixel((290, 10))), "red is not at the shown corner"
    assert tag is None, "the answer carries an orientation tag"
    assert response.headers["X-Capture-Source"] == "300,400"


@_ac146(18)
@pytest.mark.unit
def test_ac_146_18_flatten_writes_an_upright_png(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.18"
    inbox = _inbox(tmp_path)
    original = inbox / "t6.png"
    tagged = _tagged(".png", 6)
    original.write_bytes(tagged)
    with _stack(tmp_path, inbox) as client:
        shot_id = _items(client)["t6.png"]["id"]
        saved = client.post(
            f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": [GREEN_MARK]}
        )
        assert saved.status_code == 200, f"annotate answered {saved.status_code}"
        flat = client.post(f"{PREFIX}/{shot_id}/flatten", headers=AUTH)
    assert flat.status_code == 200, f"flatten answered {flat.status_code}"
    detail = flat.json()
    fmt, size, _rgb, tag = _look(original.read_bytes())
    assert (fmt, size) == ("PNG", TURNED), f"the flattened file is {(fmt, size)}"
    assert tag is None, "the flattened file carries an orientation tag"
    assert detail["id"] == shot_id
    assert detail["backup_path"] is not None
    assert Path(detail["backup_path"]).read_bytes() == tagged, "the backup is not the tagged file"


@_ac146(27)
@pytest.mark.unit
def test_ac_146_27_list_rebakes_a_copy_saved_in_the_old_frame(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.27"
    from PIL import Image, ImageDraw

    inbox = _inbox(tmp_path)
    original = inbox / "t6.jpg"
    original.write_bytes(_tagged(".jpg", 6))
    with _stack(tmp_path, inbox) as client:
        shot_id = _items(client)["t6.jpg"]["id"]
        saved = client.post(
            f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": [GREEN_MARK]}
        )
        assert saved.status_code == 200, f"annotate answered {saved.status_code}"
        copy = Path(saved.json()["annotated_path"])
        sidecar = Path(saved.json()["sidecar_path"])
        # Today's state: the copy baked onto the stored 400x300 frame, the key never written.
        with Image.open(original) as opened:
            stored = opened.convert("RGB")
        ImageDraw.Draw(stored).rectangle((100, 330, 139, 369), fill=(0, 255, 0))
        stored.save(copy, format=PIL_FORMAT[copy.suffix])
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        payload.pop("baked_orientation", None)
        sidecar.write_text(json.dumps(payload), encoding="utf-8")
        assert _look(copy.read_bytes())[1] == SIZE
        _items(client)
        fmt, size, rgb, _tag = _look(copy.read_bytes())
        assert size == TURNED, f"the copy is still {size}"
        assert _green(rgb.getpixel((120, 350))), "the mark is not at its shown centre"
        assert json.loads(sidecar.read_text(encoding="utf-8")).get("baked_orientation") == 6
        exported = client.post(f"{PREFIX}/{shot_id}/export", headers=AUTH, json={"format": "png"})
    # The export route answers 201 Created (`routes/captures.py`, `status_code=201`).
    assert exported.status_code == 201, f"export answered {exported.status_code}"
    shot = exported.json()["shot"]
    assert (shot["width"], shot["height"]) == TURNED
    assert _look(Path(shot["path"]).read_bytes())[1] == TURNED


@_ac146(28)
@pytest.mark.unit
def test_ac_146_28_plain_image_of_an_untagged_file_is_the_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-146.28"
    inbox = _inbox(tmp_path)
    files = {
        "none.png": _tagged(".png", None),
        "t1.jpg": _tagged(".jpg", 1),
        "t6.webp": _tagged(".webp", 6),
    }
    for name, data in files.items():
        (inbox / name).write_bytes(data)
    with _stack(tmp_path, inbox) as client:
        items = _items(client)
        for name, data in files.items():
            response = client.get(f"{PREFIX}/{items[name]['id']}/image", headers=AUTH)
            assert response.status_code == 200, f"{name}: answered {response.status_code}"
            assert response.content == data, f"{name}: the bytes changed"
