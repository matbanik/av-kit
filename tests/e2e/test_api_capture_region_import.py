"""MEU-128 region view and MEU-129 image import on the real stack (Session 58).

Every test builds its images with Pillow under tmp_path; nothing reaches the network.
"""

from __future__ import annotations

import io
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
FRAME_HEADERS = (
    "x-capture-source",
    "x-capture-region",
    "x-capture-returned",
    "x-capture-scale",
    "x-capture-clamped",
)
OVERSIZE_DETAIL = (
    "image exceeds IMAGE_MAX_BYTES; pass max_edge (64 to 2576) or a region for a smaller image"
)
CHANGED_MESSAGE = "the image file changed since the captures were listed; list them again and retry"


def _ac128(n: int):
    label = f"AC-128.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@contextmanager
def _stack(tmp_path: Path, inbox: Path) -> Iterator[TestClient]:
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            yield client
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


def _shot_id(client: TestClient, name: str) -> str:
    items = client.get(PREFIX, headers=AUTH).json()["items"]
    ids = [item["id"] for item in items if Path(item["original_path"]).name == name]
    assert len(ids) == 1, items
    return ids[0]


def _frame(response: Any) -> tuple[str | None, ...]:
    return tuple(response.headers.get(name) for name in FRAME_HEADERS)


def _decoded(data: bytes) -> Any:
    from PIL import Image

    image = Image.open(io.BytesIO(data))
    image.load()
    return image


@_ac128(11)
def test_ac_128_11_no_fields_keeps_the_bytes(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.11"
    inbox = _inbox(tmp_path)
    _patterned((40, 30)).save(inbox / "shot.png")
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client, "shot.png")
        response = client.get(f"{PREFIX}/{shot_id}/image", headers=AUTH)
        assert response.status_code == 200
        assert response.content == (inbox / "shot.png").read_bytes()
        assert response.headers["content-type"].startswith("image/png")
        assert _frame(response) == ("40,30", "0,0,40,30", "40,30", "1.000000", "false")


@_ac128(12)
def test_ac_128_12_px_region_view(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.12"
    from PIL import Image

    inbox = _inbox(tmp_path)
    _patterned((2000, 1500)).save(inbox / "wide.png")
    region = {"x": 100, "y": 200, "width": 800, "height": 600}
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client, "wide.png")
        image = f"{PREFIX}/{shot_id}/image"
        default = client.get(image, headers=AUTH, params=region)
        assert default.status_code == 200
        assert _frame(default) == ("2000,1500", "100,200,800,600", "1568,1176", "1.960000", "false")
        assert _decoded(default.content).size == (1568, 1176)
        largest = client.get(image, headers=AUTH, params=region | {"max_edge": 2576})
        assert largest.status_code == 200
        assert _frame(largest) == ("2000,1500", "100,200,800,600", "2576,1932", "3.220000", "false")
        assert _decoded(largest.content).size == (2576, 1932)

        rect = {"type": "rect", "x": 150, "y": 250, "width": 50, "height": 50}
        rect |= {"color": "red", "stroke_width": 4}
        marked = client.post(
            f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": [rect]}
        )
        assert marked.status_code == 200
        annotated_path = Path(client.get(PREFIX, headers=AUTH).json()["items"][0]["annotated_path"])
        params = region | {"max_edge": 800, "variant": "annotated"}
        cropped = client.get(image, headers=AUTH, params=params)
        assert cropped.status_code == 200
        assert _frame(cropped) == ("2000,1500", "100,200,800,600", "800,600", "1.000000", "false")
        box = (100, 200, 900, 800)
        with Image.open(annotated_path) as annotated, Image.open(inbox / "wide.png") as original:
            want = annotated.convert("RGB").crop(box).tobytes()
            plain = original.convert("RGB").crop(box).tobytes()
        got = _decoded(cropped.content).convert("RGB").tobytes()
        assert got == want
        assert got != plain


@_ac128(13)
def test_ac_128_13_fraction_region_clamps(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.13"
    inbox = _inbox(tmp_path)
    _patterned((400, 300)).save(inbox / "shot.png")
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client, "shot.png")
        params = {"x": 0.5, "y": 0.5, "width": 0.7, "height": 0.7, "unit": "fraction"}
        response = client.get(f"{PREFIX}/{shot_id}/image", headers=AUTH, params=params)
        assert response.status_code == 200
        assert response.headers.get("x-capture-region") == "200,150,200,150"
        assert response.headers.get("x-capture-clamped") == "true"
        assert response.headers.get("x-capture-returned") == "800,600"
        assert _decoded(response.content).size == (800, 600)


@_ac128(14)
def test_ac_128_14_max_edge_alone_shrinks_only(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.14"
    inbox = _inbox(tmp_path)
    _patterned((2000, 1000)).save(inbox / "wide.png")
    with _stack(tmp_path, inbox) as client:
        image = f"{PREFIX}/{_shot_id(client, 'wide.png')}/image"
        small = client.get(image, headers=AUTH, params={"max_edge": 500})
        assert small.status_code == 200
        assert _frame(small) == ("2000,1000", "0,0,2000,1000", "500,250", "0.250000", "false")
        assert _decoded(small.content).size == (500, 250)
        same = client.get(image, headers=AUTH, params={"max_edge": 2576})
        assert same.status_code == 200
        assert same.content == (inbox / "wide.png").read_bytes()
        assert _frame(same) == ("2000,1000", "0,0,2000,1000", "2000,1000", "1.000000", "false")


@_ac128(15)
def test_ac_128_15_bad_region_is_422(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.15"
    inbox = _inbox(tmp_path)
    _patterned((400, 300)).save(inbox / "shot.png")
    cases = (
        (
            "partial",
            {"x": 1, "y": 1, "width": 10},
            "x, y, width and height go together: give all four or none",
        ),
        ("unit-alone", {"unit": "px"}, "unit needs x, y, width and height"),
        ("max-edge-low", {"max_edge": 63}, "max_edge must be between 64 and 2576"),
        (
            "outside",
            {"x": 400, "y": 0, "width": 10, "height": 10},
            "region starts outside the image, which is 400x300 px",
        ),
    )
    with _stack(tmp_path, inbox) as client:
        image = f"{PREFIX}/{_shot_id(client, 'shot.png')}/image"
        for case, params, message in cases:
            response = client.get(image, headers=AUTH, params=params)
            assert response.status_code == 422, case
            error = response.json()["error"]
            assert (error["code"], error["message"]) == ("ValidationError", message), case
        inch = client.get(image, headers=AUTH, params={"unit": "inch"})
        assert inch.status_code == 422
        assert inch.json()["error"]["code"] == "validation_error"


@_ac128(16)
def test_ac_128_16_oversize_names_max_edge(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-128.16"
    import avkit_api.routes.captures as captures_route

    inbox = _inbox(tmp_path)
    _patterned((400, 300)).save(inbox / "shot.png")
    with _stack(tmp_path, inbox) as client:
        image = f"{PREFIX}/{_shot_id(client, 'shot.png')}/image"
        monkeypatch.setattr(captures_route, "IMAGE_MAX_BYTES", 10)
        for params in ({}, {"x": 10, "y": 10, "width": 200, "height": 100}):
            response = client.get(image, headers=AUTH, params=params)
            assert response.status_code == 413, params
            assert response.json()["error"]["message"] == OVERSIZE_DETAIL, params


@_ac128(17)
def test_ac_128_17_changed_file_is_409_until_listed(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-128.17"
    inbox = _inbox(tmp_path)
    path = inbox / "shot.png"
    _patterned((400, 300)).save(path)
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client, "shot.png")
        before = path.read_bytes()
        _patterned((320, 240)).save(path)
        assert len(path.read_bytes()) != len(before)
        params = {"x": 10, "y": 10, "width": 100, "height": 100}
        image = f"{PREFIX}/{shot_id}/image"
        stale = client.get(image, headers=AUTH, params=params)
        assert stale.status_code == 409
        error = stale.json()["error"]
        assert (error["code"], error["message"]) == ("ConflictError", CHANGED_MESSAGE)
        for part in (str(inbox), str(tmp_path), "shot.png", tmp_path.name):
            assert part not in stale.text
        assert client.get(PREFIX, headers=AUTH).status_code == 200
        fresh = client.get(image, headers=AUTH, params=params)
        assert fresh.status_code == 200
        assert fresh.headers.get("x-capture-source") == "320,240"


# MEU-129 capture-image-import (Session 58): IMPORT_MODE, IMPORT_ACCEPT, IMPORT_COPY,
# IMPORT_UPRIGHT, IMPORT_IN_PLACE, IMPORT_NAME and NO_RAW_CONSOLE.
IMPORT_OPEN = "not an image av-kit can open (png, jpg, jpeg, webp)"
PIXEL_LIMIT = "image is larger than the 89478485-pixel limit"
ANNOTATED_COPY = "this file is an annotated copy; import its original instead"


def _ac129(n: int):
    label = f"AC-129.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@contextmanager
def _import_stack(app_data: Path, inbox: Path) -> Iterator[tuple[TestClient, Any]]:
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            yield client, services
    finally:
        dispose()


def _outside(tmp_path: Path, *parts: str) -> Path:
    folder = tmp_path.joinpath("outside", *parts)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _import(client: TestClient, path: Path | str) -> Any:
    return client.post(PREFIX, headers=AUTH, json={"mode": "import", "path": str(path)})


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


@_ac129(2)
def test_ac_129_2_import_body_is_strict(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-129.2"
    inbox = _inbox(tmp_path)
    source = _outside(tmp_path) / "shot.png"
    _patterned((40, 30)).save(source)
    with _stack(tmp_path, inbox) as client:
        extra = client.post(
            PREFIX, headers=AUTH, json={"mode": "import", "path": str(source), "nope": 1}
        )
        missing = client.post(PREFIX, headers=AUTH, json={"mode": "import"})
        for response in (extra, missing):
            assert response.status_code == 422
            assert response.json()["error"]["code"] == "validation_error"
    assert list(inbox.iterdir()) == []


@_ac129(3)
def test_ac_129_3_import_copies_an_outside_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-129.3"
    inbox = _inbox(tmp_path)
    source = _outside(tmp_path) / "shot.png"
    _patterned((40, 30)).save(source)
    before = source.read_bytes()
    mtime = source.stat().st_mtime_ns
    with _stack(tmp_path, inbox) as client:
        response = _import(client, source)
        assert response.status_code == 201, response.text
        item = response.json()["item"]
        assert item["source"] == "Import"
        copy = Path(item["original_path"])
        assert _same(copy.parent, inbox)
        assert copy.read_bytes() == before
        items = client.get(PREFIX, headers=AUTH).json()["items"]
        assert [(row["id"], row["source"]) for row in items] == [(item["id"], "Import")]
    assert source.read_bytes() == before
    assert source.stat().st_mtime_ns == mtime


@_ac129(4)
def test_ac_129_4_import_names_the_copy(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-129.4"
    out = _outside(tmp_path)
    shot = out / "shot.png"
    _patterned((40, 30)).save(shot)
    other = _outside(tmp_path, "other") / "Shot.PNG"
    _patterned((40, 30)).save(other, format="PNG")
    dots = out / "...png"
    _patterned((40, 30)).save(dots, format="PNG")
    odd = out / "a.b c#!.jpg"
    _patterned((40, 30)).save(odd, format="JPEG", quality=90)
    reserved = out / "CON!.png"
    _patterned((40, 30)).save(reserved, format="PNG")
    expected = (
        (shot, "shot.png"),
        (shot, "shot_2.png"),
        (other, "Shot_3.png"),
        (dots, "import.png"),
        (odd, "a_b c.jpg"),
        (reserved, "import_CON.png"),
    )
    inbox = _inbox(tmp_path)
    with _stack(tmp_path, inbox) as client:
        for source, name in expected:
            response = _import(client, source)
            assert response.status_code == 201, (name, response.text)
            item = response.json()["item"]
            assert (Path(item["original_path"]).name, item["display_name"]) == (name, name)
    assert sorted(path.name for path in inbox.iterdir()) == sorted(name for _, name in expected)


@pytest.mark.parametrize(
    "orientation",
    [None, 1, 2, 3, 4, 5, 6, 7, 8],
    ids=["none", "o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"],
)
@_ac129(5)
def test_ac_129_5_import_turns_exif_upright(
    ac_id: str, orientation: int | None, tmp_path: Path
) -> None:
    assert ac_id == "AC-129.5"
    from PIL import Image, ImageOps

    source = _outside(tmp_path) / "photo.jpg"
    image = _patterned((40, 30))
    if orientation is None:
        image.save(source, format="JPEG", quality=90)
    else:
        exif = Image.Exif()
        exif[0x0112] = orientation
        image.save(source, format="JPEG", quality=90, exif=exif)
    inbox = _inbox(tmp_path)
    with _stack(tmp_path, inbox) as client:
        response = _import(client, source)
        assert response.status_code == 201, response.text
        item = response.json()["item"]
    copy = Path(item["original_path"])
    if orientation in (None, 1):
        assert copy.name == "photo.jpg"
        assert copy.read_bytes() == source.read_bytes()
        assert (item["width"], item["height"]) == (40, 30)
        return
    assert copy.name == "photo.png"
    with Image.open(source) as opened:
        want = ImageOps.exif_transpose(opened).convert("RGB")
    got = _decoded(copy.read_bytes()).convert("RGB")
    assert got.size == want.size
    assert got.tobytes() == want.tobytes()
    assert (item["width"], item["height"]) == want.size


@_ac129(6)
def test_ac_129_6_import_in_place(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-129.6"
    inbox = _inbox(tmp_path)
    listed = inbox / "a.png"
    _patterned((40, 30)).save(listed)
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client, "a.png")
        for _ in range(2):
            response = _import(client, listed)
            assert response.status_code == 201, response.text
            item = response.json()["item"]
            assert (item["id"], item["source"]) == (shot_id, "Scan")
        fresh = inbox / "b.png"
        _patterned((48, 36)).save(fresh)
        response = _import(client, fresh)
        assert response.status_code == 201, response.text
        item = response.json()["item"]
        assert item["source"] == "Import"
        assert _same(item["original_path"], fresh)
    assert sorted(path.name for path in inbox.iterdir()) == ["a.png", "b.png"]


@_ac129(7)
def test_ac_129_7_annotated_refused_subfolder_copied(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-129.7"
    inbox = _inbox(tmp_path)
    marked = inbox / "x.annotated.png"
    _patterned((40, 30)).save(marked)
    nested = inbox / "sub" / "y.png"
    nested.parent.mkdir()
    _patterned((40, 30)).save(nested)
    with _stack(tmp_path, inbox) as client:
        refused = _import(client, marked)
        assert refused.status_code == 422
        assert _error(refused) == ("InboxPathError", ANNOTATED_COPY)
        copied = _import(client, nested)
        assert copied.status_code == 201, copied.text
        item = copied.json()["item"]
        assert item["source"] == "Import"
        assert _same(item["original_path"], inbox / "y.png")
    assert (inbox / "y.png").read_bytes() == nested.read_bytes()


IMPORT_REFUSALS = {
    "relative": ("InboxPathError", "path must be absolute"),
    "missing": ("InboxPathError", "no file at that path"),
    "folder": ("InboxPathError", "path is not a regular file"),
    "gif": ("InboxPathError", IMPORT_OPEN),
    "text-png": ("ValidationError", IMPORT_OPEN),
    "over-cap": ("InboxPathError", "file is 2 MB; the import limit is 1 MB"),
    "bomb-warn": ("ValidationError", PIXEL_LIMIT),
    "bomb-error": ("ValidationError", PIXEL_LIMIT),
    "bad-idat": ("ValidationError", IMPORT_OPEN),
    "half-jpeg": ("ValidationError", IMPORT_OPEN),
}


def _refused_source(case: str, out: Path) -> Path | str:
    import os

    from PIL import Image

    if case == "relative":
        return "shot.png"
    names = {
        "missing": "gone.png",
        "folder": "folder",
        "gif": "anim.gif",
        "text-png": "note.png",
        "over-cap": "noise.png",
        "bomb-warn": "wide.png",
        "bomb-error": "huge.png",
        "bad-idat": "damaged.png",
        "half-jpeg": "cut.jpg",
    }
    path = out / names[case]
    if case == "folder":
        path.mkdir()
    elif case == "gif":
        Image.new("RGB", (16, 16), (200, 10, 10)).save(path, format="GIF")
    elif case == "text-png":
        path.write_text("not an image", encoding="utf-8")
    elif case == "over-cap":
        noise = Image.frombytes("RGB", (600, 600), os.urandom(600 * 600 * 3))
        noise.save(path, format="PNG")
        assert 1_000_000 < path.stat().st_size <= 2_000_000
    elif case == "bomb-warn":
        Image.new("1", (10000, 10000)).save(path, format="PNG")
    elif case == "bomb-error":
        Image.new("1", (14000, 14000)).save(path, format="PNG")
    elif case == "bad-idat":
        _patterned((64, 48)).save(path, format="PNG")
        data = bytearray(path.read_bytes())
        start = data.index(b"IDAT") + 4 + 10
        data[start : start + 10] = bytes(byte ^ 0xFF for byte in data[start : start + 10])
        path.write_bytes(bytes(data))
    elif case == "half-jpeg":
        _patterned((400, 300)).save(path, format="JPEG", quality=90)
        whole = path.read_bytes()
        path.write_bytes(whole[: len(whole) // 2])
    return path


@pytest.mark.parametrize("case", list(IMPORT_REFUSALS), ids=list(IMPORT_REFUSALS))
@_ac129(8)
def test_ac_129_8_import_refusal_is_path_free(
    ac_id: str, case: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-129.8"
    import avkit_core.services.capture as capture_service

    monkeypatch.setattr(capture_service, "IMPORT_MAX_BYTES", 1_000_000, raising=False)
    out = _outside(tmp_path)
    source = _refused_source(case, out)
    inbox = _inbox(tmp_path)
    with _stack(tmp_path, inbox) as client:
        response = _import(client, source)
        assert response.status_code == 422, response.text
        assert _error(response) == IMPORT_REFUSALS[case]
        _no_path_in(response.text, Path(source), out, tmp_path)
        assert list(inbox.iterdir()) == []
        assert client.get(PREFIX, headers=AUTH).status_code == 200


@pytest.mark.parametrize("fault", ["replace", "probe", "commit"])
@_ac129(9)
def test_ac_129_9_failed_write_cleans_up(
    ac_id: str, fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-129.9"
    import os

    from avkit_core.domain.errors import InboxPathError
    from avkit_infra.capture.adapter import CaptureAdapter
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    inbox = _inbox(tmp_path)
    source = _outside(tmp_path) / "shot.png"
    _patterned((40, 30)).save(source)
    copy = inbox / "shot.png"
    with _import_stack(tmp_path, inbox) as (client, services):
        assert callable(getattr(services.capture, "import_image", None))
        with monkeypatch.context() as patch:
            if fault == "replace":
                real_replace = os.replace

                def broken_replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
                    if _same(dst, copy):
                        raise OSError(f"cannot move {src} to {dst}")
                    real_replace(src, dst, *args, **kwargs)

                patch.setattr(os, "replace", broken_replace)
            elif fault == "probe":
                real_probe = CaptureAdapter.probe

                def broken_probe(self: Any, path: Path) -> Any:
                    if _same(path, copy):
                        raise InboxPathError(f"{path} is not an image")
                    return real_probe(self, path)

                patch.setattr(CaptureAdapter, "probe", broken_probe)
            else:
                real_commit = SqlAlchemyUnitOfWork.commit

                def broken_commit(self: Any) -> None:
                    if copy.exists():
                        raise RuntimeError(f"commit failed beside {copy}")
                    real_commit(self)

                patch.setattr(SqlAlchemyUnitOfWork, "commit", broken_commit)
            response = _import(client, source)
        assert response.status_code == 503, (fault, response.text)
        assert response.json()["error"]["code"] == "internal_error"
        _no_path_in(response.text, source, inbox, tmp_path)
        assert list(inbox.iterdir()) == []
        listed = client.get(PREFIX, headers=AUTH)
        assert listed.status_code == 200
        assert listed.json()["items"] == []


@_ac129(10)
def test_ac_129_10_unreadable_source_is_422(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-129.10"
    inbox = _inbox(tmp_path)
    source = _outside(tmp_path) / "shot.png"
    _patterned((40, 30)).save(source)
    with _import_stack(tmp_path, inbox) as (client, services):
        assert callable(getattr(services.capture, "import_image", None))
        real_read = Path.read_bytes

        def broken_read(self: Path) -> bytes:
            if _same(self, source):
                raise OSError(f"cannot read {self}")
            return real_read(self)

        monkeypatch.setattr(Path, "read_bytes", broken_read)
        response = _import(client, source)
        monkeypatch.undo()
        assert response.status_code == 422
        assert _error(response) == ("InboxPathError", "the file could not be read")
        _no_path_in(response.text, source, tmp_path)
    assert list(inbox.iterdir()) == []


@pytest.mark.parametrize("fault", ["none", "race", "replace", "commit"])
@_ac129(9)
def test_ac_129_9_keeps_a_temporary_file_it_did_not_write(
    ac_id: str, fault: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-129.9"
    import os

    from avkit_core.services.capture import CaptureService
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    inbox = _inbox(tmp_path)
    source = _outside(tmp_path) / "shot.png"
    _patterned((40, 30)).save(source)
    theirs = inbox / "shot.png.avkit-tmp"
    theirs.write_bytes(b"another writer's bytes")
    with _import_stack(tmp_path, inbox) as (client, _services):
        with monkeypatch.context() as patch:
            if fault == "race":
                # The temporary name appears after the names were listed.
                patch.setattr(
                    CaptureService,
                    "_import_dest",
                    staticmethod(lambda uow, folder, stem, suffix: folder / f"{stem}{suffix}"),
                )
            elif fault == "replace":
                real_replace = os.replace

                def broken_replace(src: Any, dst: Any, *args: Any, **kwargs: Any) -> None:
                    if Path(dst).suffix == ".png" and _same(Path(dst).parent, inbox):
                        raise OSError(f"cannot move {src} to {dst}")
                    real_replace(src, dst, *args, **kwargs)

                patch.setattr(os, "replace", broken_replace)
            elif fault == "commit":
                real_commit = SqlAlchemyUnitOfWork.commit

                def broken_commit(self: Any) -> None:
                    if any(child.suffix == ".png" for child in inbox.iterdir()):
                        raise RuntimeError(f"commit failed in {inbox}")
                    real_commit(self)

                patch.setattr(SqlAlchemyUnitOfWork, "commit", broken_commit)
            response = _import(client, source)
        if fault == "none":
            assert response.status_code == 201, response.text
            assert Path(response.json()["item"]["original_path"]).name == "shot_2.png"
        else:
            assert response.status_code == 503, (fault, response.text)
            assert response.json()["error"]["code"] == "internal_error"
            _no_path_in(response.text, source, inbox, tmp_path)
            assert [child.name for child in inbox.iterdir()] == [theirs.name]
    assert theirs.read_bytes() == b"another writer's bytes"


@pytest.mark.parametrize("fault", ["exists", "is_file", "stat", "resolve"])
@_ac129(10)
def test_ac_129_10_metadata_fault_is_422(
    ac_id: str,
    fault: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    assert ac_id == "AC-129.10"
    from uuid import uuid4

    marker = f"s58META{uuid4().hex}"
    inbox = _inbox(tmp_path)
    source = _outside(tmp_path, f"private-{marker}") / f"src-{marker}.png"
    _patterned((40, 30)).save(source)
    with _import_stack(tmp_path, inbox) as (client, _services):
        real = getattr(Path, fault)

        def broken(self: Path, *args: Any, **kwargs: Any) -> Any:
            if str(self) == str(source):
                raise PermissionError(13, "Permission denied", str(self))
            return real(self, *args, **kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(Path, fault, broken)
            response = _import(client, source)
        assert response.status_code == 422, (fault, response.text)
        assert _error(response) == ("InboxPathError", "the file could not be read")
        assert marker not in response.text
    captured = capfd.readouterr()
    assert marker not in captured.out + captured.err
    assert list(inbox.iterdir()) == []


@_ac129(10)
def test_ac_129_10_in_place_probe_fault_is_422(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-129.10"
    from avkit_infra.capture.adapter import CaptureAdapter

    inbox = _inbox(tmp_path)
    shot = inbox / "root.png"
    _patterned((40, 30)).save(shot)
    before = shot.read_bytes()
    with _import_stack(tmp_path, inbox) as (client, _services):
        real_probe = CaptureAdapter.probe

        def broken_probe(self: Any, path: Path) -> Any:
            if Path(path).name == shot.name:
                raise PermissionError(13, "Permission denied", str(path))
            return real_probe(self, path)

        with monkeypatch.context() as patch:
            patch.setattr(CaptureAdapter, "probe", broken_probe)
            response = _import(client, shot)
        assert response.status_code == 422, response.text
        assert _error(response) == ("InboxPathError", "the image could not be opened")
        _no_path_in(response.text, shot, inbox, tmp_path)
    assert shot.read_bytes() == before


@_ac129(11)
def test_ac_129_11_no_path_or_marker_reaches_the_console(
    ac_id: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
) -> None:
    assert ac_id == "AC-129.11"
    from uuid import uuid4

    from PIL import Image

    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    marker = f"s58MARKER{uuid4().hex}"
    app_data = tmp_path / f"app-{marker}"
    inbox = app_data / f"inbox-{marker}"
    inbox.mkdir(parents=True)
    outside = tmp_path / f"outside-{marker}"
    outside.mkdir()
    registered = inbox / f"reg-{marker}.png"
    _patterned((40, 30)).save(registered)
    source = outside / f"src-{marker}.png"
    _patterned((400, 300)).save(source)
    refused = outside / f"bad-{marker}.gif"
    Image.new("RGB", (16, 16)).save(refused, format="GIF")
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            body = {"mode": "register", "path": str(registered), "source": "gui"}
            register = client.post(PREFIX, headers=AUTH, json=body)
            assert register.status_code == 201, register.text
            image = f"{PREFIX}/{register.json()['item']['id']}/image"
            _import(client, source)
            region = {"x": 0, "y": 0, "width": 16, "height": 16}
            assert client.get(image, headers=AUTH, params=region).status_code == 200
            bad_import = _import(client, refused)
            bad_view = client.get(image, headers=AUTH, params={"x": 1, "y": 1, "width": 10})
            assert (bad_import.status_code, bad_view.status_code) == (422, 422)
            messages = [_error(response)[1] for response in (bad_import, bad_view)]
            ring = [event.message for event in services.health.console_snapshot(0)]
        captured = capfd.readouterr()
    finally:
        dispose()
    stdout = captured.out.splitlines()
    assert any("engine.created" in line for line in stdout)
    assert sum("capture.registered" in message for message in ring) >= 2
    folded = marker.casefold()
    lines = (captured.out + captured.err).splitlines()
    assert [line for line in lines if folded in line.casefold()] == []
    assert [message for message in ring if folded in message.casefold()] == []
    assert [message for message in messages if folded in message.casefold()] == []
    console_log = app_data / "logs" / "console.log"
    if console_log.exists():
        assert folded not in console_log.read_text(encoding="utf-8").casefold()
