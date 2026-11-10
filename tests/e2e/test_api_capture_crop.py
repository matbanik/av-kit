"""MEU-130 capture crop on the real stack (Session 59).

`POST /captures/{id}/crop` cuts a region of a shot into a new PNG shot with source `Crop`.
Every test builds its images with Pillow under tmp_path; nothing reaches the network.
"""

from __future__ import annotations

import io
import json
import struct
import threading
import zlib
from collections.abc import Iterator
from contextlib import contextmanager
from functools import cache
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
CHANGED_MESSAGE = "the image file changed since the captures were listed; list them again and retry"
NO_MARKS = {"kept": 0, "clipped": 0, "dropped": 0}
RESPONSE_KEYS = {"item", "source_id", "requested", "applied", "clamped", "marks"}
NAME_LENGTH = "name must be 1 to 80 characters"
NAME_UNUSABLE = (
    "name has no usable characters; use letters, digits, space, dot, underscore or hyphen"
)
NAME_ANNOTATED = "name may not end in .annotated"
PX_WHOLE = (
    "with unit px, x, y, width and height are whole pixels; "
    'use unit: "fraction" for parts of the image'
)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
MAGENTA = (255, 0, 255)
BLUE = (0, 120, 255)


def _ac130(n: int):
    label = f"AC-130.{n}"
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


def _inbox(tmp_path: Path) -> Path:
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    return inbox


def _patterned(size: tuple[int, int]) -> Any:
    from PIL import Image, ImageDraw

    width, height = size
    image = Image.new("RGB", size, (40, 90, 140))
    draw = ImageDraw.Draw(image)
    step = max(8, width // 25)
    for left in range(0, width, step):
        shade = (left * 7) % 256
        draw.rectangle((left, 0, left + step // 2, height), fill=(shade, 255 - shade, 60))
    return image


@cache
def _distinct_png(width: int, height: int) -> bytes:
    """A PNG whose every pixel differs: (x % 256, y % 256, (x // 256) * 8 + y // 256)."""
    from PIL import Image

    assert height <= 8 * 256
    red = bytes(x % 256 for x in range(width)) * height
    green = b"".join(bytes([y % 256]) * width for y in range(height))
    blues = [bytes((x // 256) * 8 + band for x in range(width)) for band in range(8)]
    blue = b"".join(blues[y // 256] for y in range(height))
    planes = [Image.frombytes("L", (width, height), plane) for plane in (red, green, blue)]
    buffer = io.BytesIO()
    Image.merge("RGB", planes).save(buffer, format="PNG")
    return buffer.getvalue()


def _checkerboard(size: tuple[int, int]) -> Any:
    from PIL import Image

    width, height = size
    image = Image.new("RGB", size)
    image.putdata(
        [(0, 0, 0) if (x + y) % 2 else WHITE for y in range(height) for x in range(width)]
    )
    return image


def _shot_id(client: TestClient, name: str) -> str:
    items = client.get(PREFIX, headers=AUTH).json()["items"]
    ids = [item["id"] for item in items if Path(item["original_path"]).name == name]
    assert len(ids) == 1, items
    return ids[0]


def _crop(client: TestClient, shot_id: str, body: dict[str, Any]) -> Any:
    return client.post(f"{PREFIX}/{shot_id}/crop", headers=AUTH, json=body)


def _annotate(client: TestClient, shot_id: str, marks: list[dict[str, Any]]) -> None:
    response = client.post(
        f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": marks}
    )
    assert response.status_code == 200, response.text


def _error(response: Any) -> tuple[str, str]:
    error = response.json()["error"]
    return error["code"], error["message"]


def _same(left: Path | str, right: Path) -> bool:
    import os

    return os.path.normcase(Path(left).resolve()) == os.path.normcase(right.resolve())


def _no_path_in(text: str, *paths: Path) -> None:
    for path in paths:
        for part in (str(path), path.name):
            assert part not in text, part


def _names(folder: Path) -> list[str]:
    return sorted(child.name for child in folder.iterdir())


def _rgb(path: Path | str) -> Any:
    from PIL import Image

    with Image.open(path) as opened:
        opened.load()
        return opened.convert("RGB")


def _decoded(data: bytes) -> Any:
    from PIL import Image

    image = Image.open(io.BytesIO(data))
    image.load()
    return image


def _rect(x: int, y: int, width: int, height: int, stroke: int = 2) -> dict[str, Any]:
    mark: dict[str, Any] = {"type": "rect", "x": x, "y": y, "width": width, "height": height}
    return mark | {"color": "red", "stroke_width": stroke}


def _arrow(start: tuple[int, int], end: tuple[int, int], stroke: int = 4) -> dict[str, Any]:
    mark: dict[str, Any] = {"type": "arrow", "from": list(start), "to": list(end)}
    return mark | {"color": "red", "stroke_width": stroke}


def _text(x: int, y: int, text: str = "HELLO") -> dict[str, Any]:
    return {"type": "text", "x": x, "y": y, "text": text, "color": "red", "font_size": 20}


def _box(kind: str, x: int, y: int, width: int, height: int, **extra: Any) -> dict[str, Any]:
    return {"type": kind, "x": x, "y": y, "width": width, "height": height, **extra}


def _annotated_of(client: TestClient, name: str) -> str:
    items = client.get(PREFIX, headers=AUTH).json()["items"]
    paths = [item["annotated_path"] for item in items if Path(item["original_path"]).name == name]
    assert len(paths) == 1 and paths[0], items
    return paths[0]


def _reddish(pixel: tuple[int, ...]) -> bool:
    return pixel[0] > 150 and pixel[1] < 110 and pixel[2] < 110


@_ac130(12)
def test_ac_130_12_crop_returns_a_new_crop_shot(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.12"
    inbox = _inbox(tmp_path)
    source = inbox / "shot.png"
    _patterned((200, 100)).save(source)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        detail = f"{PREFIX}/{shot_id}"
        before_row = client.get(detail, headers=AUTH).json()
        before_bytes = source.read_bytes()
        before_mtime = source.stat().st_mtime_ns
        body = {"x": 10, "y": 20, "width": 50, "height": 40}
        response = _crop(client, shot_id, body)
        assert response.status_code == 201, response.text
        payload = response.json()
        assert set(payload) == RESPONSE_KEYS
        item = payload["item"]
        assert item["source"] == "Crop"
        assert item["id"] != shot_id
        assert (item["width"], item["height"]) == (50, 40)
        assert Path(item["original_path"]).name == "shot-crop.png"
        assert payload["source_id"] == shot_id
        assert payload["requested"] == body | {"unit": "px"}
        assert payload["applied"] == body
        assert payload["clamped"] is False
        assert payload["marks"] == NO_MARKS
        assert source.read_bytes() == before_bytes
        assert source.stat().st_mtime_ns == before_mtime
        assert not (inbox / "shot.ann.json").exists()
        assert client.get(detail, headers=AUTH).json() == before_row
        items = client.get(PREFIX, headers=AUTH).json()["items"]
        ids = [listed["id"] for listed in items]
        assert sorted(ids) == sorted([shot_id, item["id"]])


AC_130_13_BOXES = {
    "px": {"x": 100, "y": 200, "width": 1600, "height": 900},
    "fraction": {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4, "unit": "fraction"},
    "clamped": {"x": 2400, "y": 300, "width": 1000, "height": 500},
    "eight": {"x": 50, "y": 60, "width": 8, "height": 8},
    "large": {"x": 100, "y": 50, "width": 2800, "height": 1400},
}


@pytest.mark.parametrize("case", list(AC_130_13_BOXES), ids=list(AC_130_13_BOXES))
@_ac130(13)
def test_ac_130_13_crop_matches_the_region_view(ac_id: str, case: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.13"
    inbox = _inbox(tmp_path)
    source = inbox / "big.png"
    source.write_bytes(_distinct_png(3000, 1500))
    box = AC_130_13_BOXES[case]
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "big.png")
        response = _crop(client, shot_id, box)
        assert response.status_code == 201, response.text
        applied = response.json()["applied"]
        image = f"{PREFIX}/{shot_id}/image"
        view = client.get(image, headers=AUTH, params=box)
        assert view.status_code == 200, view.text
        region = (applied["x"], applied["y"], applied["width"], applied["height"])
        assert view.headers["x-capture-region"] == ",".join(str(value) for value in region)
        crop = _rgb(response.json()["item"]["original_path"])
        assert crop.size == region[2:]
        long_edge = max(region[2:])
        if 64 <= long_edge <= 2576:
            assert case in ("px", "fraction", "clamped")
            sized = client.get(image, headers=AUTH, params=box | {"max_edge": long_edge})
            assert sized.status_code == 200, sized.text
            assert sized.headers["x-capture-returned"] == f"{region[2]},{region[3]}"
            assert crop.tobytes() == _decoded(sized.content).convert("RGB").tobytes()
        else:
            assert case in ("eight", "large")
            left, top, width, height = region
            want = _rgb(source).crop((left, top, left + width, top + height))
            assert crop.tobytes() == want.tobytes()


AC_130_14_BOXES = {
    "right": {"x": 100, "y": 10, "width": 50, "height": 20},
    "bottom": {"x": 10, "y": 60, "width": 20, "height": 50},
    "corner": {"x": 100, "y": 60, "width": 50, "height": 50},
    "fraction": {"x": 0.9, "y": 0.5, "width": 0.5, "height": 0.9, "unit": "fraction"},
}


@_ac130(14)
def test_ac_130_14_crop_past_an_edge_is_clamped(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.14"
    from PIL import Image

    inbox = _inbox(tmp_path)
    Image.new("RGB", (120, 80), WHITE).save(inbox / "white.png")
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "white.png")
        for case, box in AC_130_14_BOXES.items():
            response = _crop(client, shot_id, box)
            assert response.status_code == 201, (case, response.text)
            payload = response.json()
            assert payload["clamped"] is True, case
            applied = payload["applied"]
            assert applied["x"] + applied["width"] <= 120, case
            assert applied["y"] + applied["height"] <= 80, case
            crop = _rgb(payload["item"]["original_path"])
            assert crop.size == (applied["width"], applied["height"]), case
            assert crop.getextrema() == ((255, 255), (255, 255), (255, 255)), case


@_ac130(15)
def test_ac_130_15_crop_names(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.15"
    inbox = _inbox(tmp_path)
    _patterned((60, 40)).save(inbox / "shot.png")
    _patterned((60, 40)).save(inbox / "pic.png")
    long_stem = "abcdefghij" * 24
    _patterned((60, 40)).save(inbox / f"{long_stem}.png")
    box = {"x": 0, "y": 0, "width": 20, "height": 20}
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")

        def crop_name(shot: str, extra: dict[str, Any]) -> str:
            response = _crop(client, shot, box | extra)
            assert response.status_code == 201, (extra, response.text)
            return Path(response.json()["item"]["original_path"]).name

        assert crop_name(shot_id, {}) == "shot-crop.png"
        assert crop_name(shot_id, {}) == "shot-crop_2.png"
        # A sidecar name and another writer's temporary file each take their name, case-folded.
        (inbox / "pic-crop.ANN.JSON").write_text("{}", encoding="utf-8")
        (inbox / "pic-crop_2.PNG.AVKIT-TMP").write_bytes(b"another writer's bytes")
        assert crop_name(_shot_id(client, "pic.png"), {}) == "pic-crop_3.png"
        assert crop_name(shot_id, {"name": "a/b c#!.PNG"}) == "ab c.png"
        assert crop_name(shot_id, {"name": "CON"}) == "crop_CON.png"
        refusals = (
            ("#!", NAME_UNUSABLE),
            ("n" * 81, NAME_LENGTH),
            ("x.annotated", NAME_ANNOTATED),
        )
        for name, message in refusals:
            response = _crop(client, shot_id, box | {"name": name})
            assert response.status_code == 422, (name, response.text)
            assert _error(response) == ("ValidationError", message), name
        assert crop_name(_shot_id(client, f"{long_stem}.png"), {}) == f"{long_stem[:100]}-crop.png"


@_ac130(16)
def test_ac_130_16_crop_errors_use_the_envelope(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.16"
    inbox = _inbox(tmp_path)
    source = inbox / "shot.png"
    _patterned((400, 300)).save(source)
    _patterned((400, 300)).save(inbox / "marked.png")
    box = {"x": 0, "y": 0, "width": 20, "height": 20}
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        before = _names(inbox)
        unknown = _crop(client, "no-such-shot", box)
        assert unknown.status_code == 404, unknown.text
        extra = _crop(client, shot_id, box | {"nope": True})
        assert extra.status_code == 422
        assert _error(extra)[0] == "validation_error"
        missing = _crop(client, shot_id, {"x": 0, "y": 0, "width": 20})
        assert missing.status_code == 422
        assert _error(missing)[0] == "validation_error"
        regions = (
            (
                {"x": 400, "y": 0, "width": 10, "height": 10},
                "region starts outside the image, which is 400x300 px",
            ),
            (
                {"x": 396, "y": 0, "width": 10, "height": 10},
                "region is 4x10 px after clamping to the image; each edge must be at least 8 px",
            ),
            ({"x": 1.5, "y": 0, "width": 10, "height": 10}, PX_WHOLE),
        )
        for body, message in regions:
            response = _crop(client, shot_id, body)
            assert response.status_code == 422, (body, response.text)
            assert _error(response) == ("ValidationError", message), body
        assert _names(inbox) == before
        marked_id = _shot_id(client, "marked.png")
        (inbox / "marked.ann.json").write_text("{not json", encoding="utf-8")
        malformed = _crop(client, marked_id, box)
        assert malformed.status_code == 422, malformed.text
        assert _error(malformed) == ("AnnotationValidationError", "sidecar is malformed")
        _patterned((320, 240)).save(source)
        changed = _crop(client, shot_id, box)
        assert changed.status_code == 409, changed.text
        assert _error(changed) == ("ConflictError", CHANGED_MESSAGE)
        _no_path_in(changed.text, source, inbox, tmp_path)
        assert _names(inbox) == sorted([*before, "marked.ann.json"])


@_ac130(17)
def test_ac_130_17_crop_carries_and_bakes_the_marks(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.17"
    from avkit_core.domain.capture import clip_mark
    from avkit_core.services.capture import annotations_from_sidecar, annotations_to_wire

    inbox = _inbox(tmp_path)
    _patterned((200, 100)).save(inbox / "shot.png")
    _patterned((200, 100)).save(inbox / "plain.png")
    marks = [_rect(60, 30, 20, 10), _arrow((70, 40), (180, 40)), _text(10, 10)]
    left, top, width, height = 50, 20, 100, 60
    box = {"x": left, "y": top, "width": width, "height": height}
    with _stack(tmp_path, inbox) as (client, _services):
        put = client.put(SETTINGS, headers=AUTH, json={"annotated_format": "webp"})
        assert put.status_code == 200, put.text
        shot_id = _shot_id(client, "shot.png")
        _annotate(client, shot_id, marks)
        response = _crop(client, shot_id, box)
        assert response.status_code == 201, response.text
        payload = response.json()
        assert payload["marks"] == {"kept": 1, "clipped": 1, "dropped": 1}
        item = payload["item"]
        carried = [
            clip_mark(mark, left, top, width, height)[0]
            for mark in annotations_from_sidecar({"annotations": marks})
        ]
        want = annotations_to_wire([mark for mark in carried if mark is not None])
        assert len(want) == 2
        crop = Path(item["original_path"])
        sidecar = Path(item["sidecar_path"])
        assert sidecar == crop.with_name(f"{crop.stem}.ann.json")
        document = json.loads(sidecar.read_text(encoding="utf-8"))
        assert document["annotations"] == want
        assert "version" in document
        bake = Path(item["annotated_path"])
        assert bake.name == f"{crop.stem}.annotated.webp"
        assert bake.is_file()
        shown = client.get(
            f"{PREFIX}/{item['id']}/image", headers=AUTH, params={"variant": "annotated"}
        )
        assert shown.status_code == 200, shown.text
        assert shown.content == bake.read_bytes()
        detail = client.get(f"{PREFIX}/{item['id']}", headers=AUTH).json()
        assert detail["annotations"] == want

        plain = _crop(client, _shot_id(client, "plain.png"), box)
        assert plain.status_code == 201, plain.text
        plain_item = plain.json()["item"]
        assert plain.json()["marks"] == NO_MARKS
        assert (plain_item["sidecar_path"], plain_item["annotated_path"]) == (None, None)
        plain_stem = Path(plain_item["original_path"]).stem
        assert [name for name in _names(inbox) if name.startswith(plain_stem)] == [
            f"{plain_stem}.png"
        ]


@_ac130(18)
def test_ac_130_18_crop_bake_differences(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.18"
    from PIL import Image, ImageDraw

    inbox = _inbox(tmp_path)
    for name in ("rect", "arrow", "text"):
        Image.new("RGB", (200, 100), WHITE).save(inbox / f"{name}.png")
    gradient = Image.new("RGB", (200, 100))
    gradient.putdata(
        [
            ((x * 9) % 256, (y * 13) % 256, (x * 5 + y * 3) % 256)
            for y in range(100)
            for x in range(200)
        ]
    )
    gradient.save(inbox / "pix.png")
    erase = Image.new("RGB", (200, 100), GREEN)
    ImageDraw.Draw(erase).rectangle((160, 0, 199, 99), fill=MAGENTA)
    erase.paste(_checkerboard((40, 40)), (150, 30))
    erase.save(inbox / "erase.png")
    with _stack(tmp_path, inbox) as (client, _services):

        def crop_bake(name: str, marks: list[dict[str, Any]], box: dict[str, int]) -> Any:
            shot_id = _shot_id(client, f"{name}.png")
            _annotate(client, shot_id, marks)
            response = _crop(client, shot_id, box)
            assert response.status_code == 201, (name, response.text)
            return _rgb(response.json()["item"]["annotated_path"])

        # A rect cut on each side draws its stroke along that crop edge.
        sides = {
            "left": ({"x": 40, "y": 0, "width": 100, "height": 100}, "column", 0),
            "right": ({"x": 0, "y": 0, "width": 150, "height": 100}, "column", 149),
            "top": ({"x": 0, "y": 40, "width": 200, "height": 60}, "row", 0),
            "bottom": ({"x": 0, "y": 0, "width": 200, "height": 60}, "row", 59),
        }
        for side, (box, axis, index) in sides.items():
            bake = crop_bake("rect", [_rect(20, 20, 160, 60)], box)
            if axis == "column":
                span = range(max(0, 20 - box["y"]) + 3, min(bake.height, 80 - box["y"]) - 3)
                edge = [bake.getpixel((index, y)) for y in span]
            else:
                span = range(max(0, 20 - box["x"]) + 3, min(bake.width, 180 - box["x"]) - 3)
                edge = [bake.getpixel((x, index)) for x in span]
            assert edge and all(_reddish(pixel) for pixel in edge), side

        # A pixelate cut on its left re-aligns its block grid to the crop's left edge.
        pix_box = {"x": 45, "y": 0, "width": 100, "height": 100}
        pix = crop_bake("pix", [_box("pixelate", 30, 20, 60, 40, block_size=10)], pix_box)
        for bx in range(0, 40, 10):
            for by in range(20, 60, 10):
                block = pix.crop((bx, by, bx + 10, by + 10))
                assert len(set(block.get_flattened_data())) == 1, (bx, by)
        source_bake = _rgb(_annotated_of(client, "pix.png"))
        shifted = source_bake.crop((45, 20, 85, 60)).tobytes()
        assert pix.crop((0, 20, 40, 60)).tobytes() != shifted

        # An eraser cut by the crop samples its ring inside the crop only.
        erase_box = {"x": 0, "y": 0, "width": 160, "height": 100}
        erased = crop_bake("erase", [_box("eraser", 150, 30, 40, 40)], erase_box)
        assert set(erased.crop((150, 30, 160, 70)).get_flattened_data()) == {GREEN}
        erase_source = _annotated_of(client, "erase.png")
        assert set(_rgb(erase_source).crop((150, 30, 190, 70)).get_flattened_data()) == {MAGENTA}

        # A clipped arrow ends at the crop edge, so its head is drawn there.
        arrow_box = {"x": 0, "y": 0, "width": 120, "height": 100}
        arrow = crop_bake("arrow", [_arrow((20, 50), (180, 50))], arrow_box)

        def red_rows(x: int) -> int:
            return sum(_reddish(arrow.getpixel((x, y))) for y in range(arrow.height))

        assert red_rows(119) >= 1
        assert red_rows(112) > red_rows(40) > 0

        # A text mark whose anchor is outside the crop is dropped, so it leaves no pixels.
        text_box = {"x": 20, "y": 0, "width": 100, "height": 100}
        text_id = _shot_id(client, "text.png")
        _annotate(client, text_id, [_text(5, 5)])
        dropped = _crop(client, text_id, text_box)
        assert dropped.status_code == 201, dropped.text
        assert dropped.json()["marks"] == {"kept": 0, "clipped": 0, "dropped": 1}
        text_source = _annotated_of(client, "text.png")
        text_pixels = _rgb(text_source).crop((20, 0, 120, 40)).get_flattened_data()
        assert any(_reddish(p) for p in text_pixels)
        text_crop = _rgb(dropped.json()["item"]["original_path"])
        assert set(text_crop.crop((0, 0, 100, 40)).get_flattened_data()) == {WHITE}
        assert dropped.json()["item"]["annotated_path"] is None


@_ac130(19)
def test_ac_130_19_redaction_survives_the_crop(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.19"
    from PIL import Image

    inbox = _inbox(tmp_path)
    _checkerboard((200, 100)).save(inbox / "pix.png")
    ring = Image.new("RGB", (200, 100), BLUE)
    ring.paste(_checkerboard((40, 40)), (150, 30))
    ring.save(inbox / "erase.png")
    with _stack(tmp_path, inbox) as (client, _services):
        # Pixelate (30, 20, 60, 40) at block 4 under a crop at x = 44: the clipped box is
        # (0, 20, 46, 40) and its last column of blocks is 2 px wide, so no block is 1 px.
        pix_id = _shot_id(client, "pix.png")
        _annotate(client, pix_id, [_box("pixelate", 30, 20, 60, 40, block_size=4)])
        pixelated = _crop(client, pix_id, {"x": 44, "y": 0, "width": 100, "height": 100})
        assert pixelated.status_code == 201, pixelated.text
        item = pixelated.json()["item"]
        original = _rgb(item["original_path"])
        bake = _rgb(item["annotated_path"])
        for y in range(20, 60):
            for x in range(0, 46):
                assert bake.getpixel((x, y)) != original.getpixel((x, y)), (x, y)

        erase_id = _shot_id(client, "erase.png")
        _annotate(client, erase_id, [_box("eraser", 150, 30, 40, 40)])
        erased = _crop(client, erase_id, {"x": 0, "y": 0, "width": 170, "height": 100})
        assert erased.status_code == 201, erased.text
        erased_bake = _rgb(erased.json()["item"]["annotated_path"])
        assert set(erased_bake.crop((150, 30, 170, 70)).get_flattened_data()) == {BLUE}


@_ac130(20)
def test_ac_130_20_crop_races_a_scan(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.20"
    inbox = _inbox(tmp_path)
    _patterned((200, 100)).save(inbox / "shot.png")
    with _stack(tmp_path, inbox) as (client, services):
        shot_id = _shot_id(client, "shot.png")
        stop = threading.Event()
        faults: list[BaseException] = []

        def scan() -> None:
            while not stop.is_set():
                try:
                    services.capture.scan_inbox()
                except BaseException as exc:  # noqa: BLE001 - reported below
                    faults.append(exc)
                    return

        scanner = threading.Thread(target=scan, daemon=True)
        scanner.start()
        crop_ids: list[str] = []
        try:
            for index in range(10):
                body = {"x": index, "y": index, "width": 40, "height": 30}
                response = _crop(client, shot_id, body)
                assert response.status_code == 201, (index, response.text)
                assert response.json()["item"]["source"] == "Crop"
                crop_ids.append(response.json()["item"]["id"])
        finally:
            stop.set()
            scanner.join(timeout=30)
        assert not scanner.is_alive()
        assert faults == []
        items = client.get(PREFIX, headers=AUTH).json()["items"]
        assert not [item for item in items if item["original_path"].endswith(".avkit-tmp")]
        by_id = {item["id"]: item for item in items}
        assert len(items) == len(by_id) == 11
        for crop_id in crop_ids:
            assert by_id[crop_id]["source"] == "Crop"
        assert not [name for name in _names(inbox) if name.endswith(".avkit-tmp")]


@pytest.mark.parametrize("fault", ["replace", "probe", "bake", "commit"])
@_ac130(21)
def test_ac_130_21_failed_crop_cleans_up(
    ac_id: str, fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-130.21"
    import os

    from avkit_core.domain.errors import InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    inbox = _inbox(tmp_path)
    source = inbox / "shot.png"
    _patterned((40, 30)).save(source)
    crop = inbox / "shot-crop.png"
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        _annotate(client, shot_id, [_rect(2, 2, 8, 8)])
        before = _names(inbox)
        before_bytes = source.read_bytes()
        before_items = client.get(PREFIX, headers=AUTH).json()["items"]
        with monkeypatch.context() as patch:
            if fault == "replace":
                real_replace = os.replace

                def broken_replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
                    if _same(dst, crop):
                        raise OSError(f"cannot move {src} to {dst}")
                    real_replace(src, dst, *args, **kwargs)

                patch.setattr(os, "replace", broken_replace)
            elif fault == "probe":
                real_probe = CaptureAdapter.probe

                def broken_probe(self: Any, path: Path) -> Any:
                    if _same(path, crop):
                        raise InboxPathError(f"{path} is not an image")
                    return real_probe(self, path)

                patch.setattr(CaptureAdapter, "probe", broken_probe)
            elif fault == "bake":
                real_bake = CaptureAdapter.bake

                def broken_bake(
                    self: Any,
                    original_path: Path,
                    annotations: Any,
                    output_path: Path,
                    output_format: str = "png",
                ) -> Any:
                    if _same(original_path, crop):
                        raise OSError(f"cannot write {output_path}")
                    return real_bake(self, original_path, annotations, output_path, output_format)

                patch.setattr(CaptureAdapter, "bake", broken_bake)
            else:
                real_commit = SqlAlchemyUnitOfWork.commit

                def broken_commit(self: Any) -> None:
                    if crop.exists():
                        raise RuntimeError(f"commit failed beside {crop}")
                    real_commit(self)

                patch.setattr(SqlAlchemyUnitOfWork, "commit", broken_commit)
            response = _crop(client, shot_id, {"x": 0, "y": 0, "width": 20, "height": 20})
        assert response.status_code == 503, (fault, response.text)
        assert response.json()["error"]["code"] == "internal_error"
        _no_path_in(response.text, crop, inbox, tmp_path)
        assert _names(inbox) == before
        assert source.read_bytes() == before_bytes
        listed = client.get(PREFIX, headers=AUTH)
        assert listed.status_code == 200
        assert listed.json()["items"] == before_items


@pytest.mark.parametrize("fault", ["none", "race", "replace", "commit"])
@_ac130(21)
def test_ac_130_21_keeps_a_temp_file_it_did_not_write(
    ac_id: str, fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-130.21"
    import os

    from avkit_core.services.capture import CaptureService
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    inbox = _inbox(tmp_path)
    _patterned((40, 30)).save(inbox / "shot.png")
    theirs = inbox / "shot-crop.png.avkit-tmp"
    theirs.write_bytes(b"another writer's bytes")
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        before = _names(inbox)
        before_items = client.get(PREFIX, headers=AUTH).json()["items"]
        with monkeypatch.context() as patch:
            if fault == "race":
                # The other writer's temporary file appears after the names were listed.
                patch.setattr(
                    CaptureService,
                    "_crop_dest",
                    staticmethod(lambda uow, folder, stem: folder / "shot-crop.png"),
                    raising=False,
                )
            elif fault == "replace":
                real_replace = os.replace

                def broken_replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
                    if Path(dst).name.startswith("shot-crop") and _same(Path(dst).parent, inbox):
                        raise OSError(f"cannot move {src} to {dst}")
                    real_replace(src, dst, *args, **kwargs)

                patch.setattr(os, "replace", broken_replace)
            elif fault == "commit":
                real_commit = SqlAlchemyUnitOfWork.commit

                def broken_commit(self: Any) -> None:
                    if (inbox / "shot-crop_2.png").exists():
                        raise RuntimeError(f"commit failed in {inbox}")
                    real_commit(self)

                patch.setattr(SqlAlchemyUnitOfWork, "commit", broken_commit)
            response = _crop(client, shot_id, {"x": 0, "y": 0, "width": 20, "height": 20})
        if fault == "none":
            assert response.status_code == 201, response.text
            assert Path(response.json()["item"]["original_path"]).name == "shot-crop_2.png"
        else:
            assert response.status_code == 503, (fault, response.text)
            assert response.json()["error"]["code"] == "internal_error"
            _no_path_in(response.text, theirs, inbox, tmp_path)
            assert _names(inbox) == before
            assert client.get(PREFIX, headers=AUTH).json()["items"] == before_items
    assert theirs.read_bytes() == b"another writer's bytes"


def _damage_idat_in_place(path: Path) -> None:
    """Split the IDAT into a 4-byte IDAT and a BAD! chunk: same size and header, SyntaxError."""
    data = path.read_bytes()
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
    path.write_bytes(damaged)


@_ac130(21)
def test_ac_130_21_damaged_source_is_422(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-130.21"
    inbox = _inbox(tmp_path)
    source = inbox / "shot.png"
    _patterned((40, 30)).save(source)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        before_items = client.get(PREFIX, headers=AUTH).json()["items"]
        intact = source.read_bytes()
        _damage_idat_in_place(source)
        before = _names(inbox)
        response = _crop(client, shot_id, {"x": 0, "y": 0, "width": 20, "height": 20})
        assert response.status_code == 422, response.text
        assert _error(response) == ("InboxPathError", "the image could not be opened")
        _no_path_in(response.text, source, inbox, tmp_path)
        assert _names(inbox) == before
        # The list scans every inbox file, and the scan's probe doesn't read a damaged PNG,
        # so the source gets its bytes back before the list checks that no row was added.
        source.write_bytes(intact)
        listed = client.get(PREFIX, headers=AUTH)
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()["items"]] == [
            item["id"] for item in before_items
        ]


@_ac130(22)
def test_ac_130_22_no_path_or_marker_reaches_the_console(
    ac_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    assert ac_id == "AC-130.22"
    from uuid import uuid4

    from avkit_core.services.health import CONSOLE_FIELDS, HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    fields_before = tuple(CONSOLE_FIELDS)
    marker = f"s59MARKER{uuid4().hex}"
    app_data = tmp_path / f"app-{marker}"
    inbox = app_data / f"inbox-{marker}"
    inbox.mkdir(parents=True)
    registered = inbox / f"reg-{marker}.png"
    _patterned((200, 100)).save(registered)
    box = {"x": 10, "y": 10, "width": 60, "height": 40}
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            body = {"mode": "register", "path": str(registered), "source": "gui"}
            register = client.post(PREFIX, headers=AUTH, json=body)
            assert register.status_code == 201, register.text
            shot_id = register.json()["item"]["id"]
            _annotate(client, shot_id, [_rect(20, 20, 20, 10), _arrow((15, 15), (190, 90))])
            ring_before = services.health.console_snapshot(0)
            last_seq = ring_before[-1].seq if ring_before else 0
            crops = [_crop(client, shot_id, box), _crop(client, shot_id, box | {"name": "named"})]
            bad_name = _crop(client, shot_id, box | {"name": "#!"})
            bad_box = _crop(client, shot_id, {"x": 500, "y": 0, "width": 10, "height": 10})
            ring_after = services.health.console_snapshot(last_seq)
            assert [response.status_code for response in crops] == [201, 201]
            assert [response.json()["item"]["source"] for response in crops] == ["Crop", "Crop"]
            assert (bad_name.status_code, bad_box.status_code) == (422, 422)
            messages = [_error(response)[1] for response in (bad_name, bad_box)]
            ring = [event.message for event in services.health.console_snapshot(0)]
            new_ring = [event.message for event in ring_after]
        captured = capfd.readouterr()
    finally:
        dispose()
    assert tuple(CONSOLE_FIELDS) == fields_before
    stdout = captured.out.splitlines()
    assert any("engine.created" in line for line in stdout)
    assert sum("capture.registered" in message for message in new_ring) >= 1
    folded = marker.casefold()
    lines = (captured.out + captured.err).splitlines()
    assert [line for line in lines if folded in line.casefold()] == []
    assert [message for message in ring if folded in message.casefold()] == []
    assert [message for message in messages if folded in message.casefold()] == []
    console_log = app_data / "logs" / "console.log"
    if console_log.exists():
        assert folded not in console_log.read_text(encoding="utf-8").casefold()
