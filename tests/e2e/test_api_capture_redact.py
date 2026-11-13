"""MEU-103 capture redact mark through the API (Session 68). AC-103.11, .12 and .25.

Every image is generated under tmp_path; nothing reaches the network. A good redact is proved
first in each refusal case, so the Red reason is the missing type, not the bad value.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tests.e2e.test_api_capture_crop import (
    AUTH,
    PREFIX,
    WHITE,
    _annotated_of,
    _crop,
    _inbox,
    _rgb,
    _shot_id,
    _stack,
)

BLACK = "#000000"
RED = (255, 0, 0)
GOOD = {"type": "redact", "x": 4, "y": 6, "width": 20, "height": 10}
# The input matrix (implementation-plan.md MEU-103), API column: each of these is 422.
BAD = (
    ("color-empty", {**GOOD, "color": ""}),
    ("color-short-hex", {**GOOD, "color": "#000"}),
    ("color-trailing-space", {**GOOD, "color": "#000000 "}),
    ("color-nul", {**GOOD, "color": "\x00"}),
    ("color-lone-surrogate", {**GOOD, "color": "\ud800"}),
    ("color-not-str", {**GOOD, "color": 5}),
    ("neg-width", {**GOOD, "width": -1}),
    ("float-x", {**GOOD, "x": 1.5}),
    ("str-x", {**GOOD, "x": "1"}),
    ("extra-block-size", {**GOOD, "block_size": 10}),
    ("missing-height", {k: v for k, v in GOOD.items() if k != "height"}),
)


def _ac(n: int):
    label = f"AC-103.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _post(client: Any, shot_id: str, marks: list[dict[str, Any]]) -> Any:
    # ASCII-escaped JSON text: a lone surrogate reaches the server as `\ud800` instead of
    # failing UTF-8 encoding in the client.
    return client.post(
        f"{PREFIX}/{shot_id}/annotate",
        headers={**AUTH, "Content-Type": "application/json"},
        content=json.dumps({"annotations": marks}, ensure_ascii=True),
    )


def _sidecar_marks(path: str | None) -> list[dict[str, Any]]:
    assert path is not None
    return json.loads(Path(path).read_text(encoding="utf-8"))["annotations"]


def _plain_shot(tmp_path: Path, size: tuple[int, int] = (64, 48)) -> Path:
    from PIL import Image

    inbox = _inbox(tmp_path)
    Image.new("RGB", size, WHITE).save(inbox / "shot.png")
    return inbox


# ------------------------------------------------------------ AC-103.11 annotate


@pytest.mark.parametrize(
    ("case", "body", "stored"),
    [
        ("no-color", GOOD, {**GOOD, "color": BLACK}),
        ("hex", {**GOOD, "color": "#FF0000"}, {**GOOD, "color": "#FF0000"}),
        ("lower-hex", {**GOOD, "color": "#ff0000"}, {**GOOD, "color": "#ff0000"}),
        ("named", {**GOOD, "color": "red"}, {**GOOD, "color": "red"}),
        ("zero-width", {**GOOD, "width": 0}, {**GOOD, "width": 0, "color": BLACK}),
    ],
    ids=["no-color", "hex", "lower-hex", "named", "zero-width"],
)
@pytest.mark.e2e
def test_ac_103_11_annotate_accepts_redact(
    case: str, body: dict[str, Any], stored: dict[str, Any], tmp_path: Path
) -> None:
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        response = _post(client, shot_id, [body])
        assert response.status_code == 200, f"{case}: {response.text}"
        assert _sidecar_marks(response.json()["sidecar_path"]) == [stored]
        detail = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
        assert detail.json()["annotations"] == [stored]


@pytest.mark.parametrize(("case", "body"), BAD, ids=[name for name, _ in BAD])
@pytest.mark.e2e
def test_ac_103_11_annotate_refuses_bad_redact(
    case: str, body: dict[str, Any], tmp_path: Path
) -> None:
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        good = _post(client, shot_id, [GOOD])
        assert good.status_code == 200, good.text
        before = _sidecar_marks(good.json()["sidecar_path"])
        refused = _post(client, shot_id, [body])
        assert refused.status_code == 422, f"{case}: {refused.text}"
        assert set(refused.json()) == {"error"}, case
        # The refusal leaves the saved marks as they were.
        assert _sidecar_marks(good.json()["sidecar_path"]) == before


# ------------------------------------------------------------ AC-103.12 guard


@_ac(12)
@pytest.mark.e2e
def test_ac_103_12_unknown_type_is_refused(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-103.12"
    from avkit_core.domain.errors import AnnotationValidationError
    from avkit_core.services.capture import annotations_from_sidecar

    blur = {"type": "blur", "x": 1, "y": 1, "width": 4, "height": 4}
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        refused = _post(client, _shot_id(client, "shot.png"), [blur])
        assert refused.status_code == 422, refused.text
        assert set(refused.json()) == {"error"}
    with pytest.raises(AnnotationValidationError):
        annotations_from_sidecar({"version": 1, "annotations": [blur]})


# ------------------------------------------------------------ AC-103.25 crop and export


@_ac(25)
@pytest.mark.e2e
def test_ac_103_25_crop_and_export_carry_the_redact(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-103.25"
    from PIL import Image

    inbox = _inbox(tmp_path)
    Image.new("RGB", (160, 100), WHITE).save(inbox / "shot.png")
    Image.new("RGB", (160, 100), WHITE).save(inbox / "away.png")
    straddle = {"type": "redact", "x": 30, "y": 20, "width": 60, "height": 40, "color": "#FF0000"}
    clipped = {"type": "redact", "x": 0, "y": 20, "width": 46, "height": 40, "color": "#FF0000"}
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        saved = _post(client, shot_id, [straddle])
        assert saved.status_code == 200, saved.text
        source = _rgb(_annotated_of(client, "shot.png"))
        assert source.getpixel((30, 20)) == RED
        assert source.getpixel((29, 20)) == WHITE

        response = _crop(client, shot_id, {"x": 44, "y": 0, "width": 100, "height": 100})
        assert response.status_code == 201, response.text
        payload = response.json()
        assert payload["marks"] == {"kept": 0, "clipped": 1, "dropped": 0}
        item = payload["item"]
        assert _sidecar_marks(item["sidecar_path"]) == [clipped]
        baked = _rgb(item["annotated_path"])
        assert baked.size == (100, 100)
        box = {baked.getpixel((x, y)) for x in range(0, 46) for y in range(20, 60)}
        assert box == {RED}
        assert baked.getpixel((46, 20)) == WHITE
        assert baked.getpixel((0, 19)) == WHITE

        exported = client.post(
            f"{PREFIX}/{item['id']}/export", headers=AUTH, json={"format": "png"}
        )
        assert exported.status_code == 201, exported.text
        copy = _rgb(exported.json()["shot"]["path"])
        assert {copy.getpixel((x, y)) for x in range(0, 46) for y in range(20, 60)} == {RED}
        assert copy.getpixel((46, 20)) == WHITE

        # A redact wholly outside the crop is dropped: no redact in the crop's sidecar.
        away_id = _shot_id(client, "away.png")
        away = _post(client, away_id, [{**straddle, "x": 120, "width": 30}])
        assert away.status_code == 200, away.text
        dropped = _crop(client, away_id, {"x": 0, "y": 0, "width": 100, "height": 100})
        assert dropped.status_code == 201, dropped.text
        assert dropped.json()["marks"] == {"kept": 0, "clipped": 0, "dropped": 1}
        assert dropped.json()["item"]["sidecar_path"] is None
        crop_image = _rgb(dropped.json()["item"]["original_path"])
        assert set(crop_image.get_flattened_data()) == {WHITE}
