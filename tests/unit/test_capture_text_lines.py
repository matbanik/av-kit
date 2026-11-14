"""MEU-102 multi-line text marks: the domain, the bake and the geometry fixture (Session 70).

Imports of new names stay inside tests so collection cannot ERROR. Every image is built with
Pillow under tmp_path; nothing reaches the network or a user's capture inbox.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import get_type_hints

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GEOMETRY_FIXTURE = REPO_ROOT / "ui" / "tests" / "e2e" / "fixtures" / "capture-geometry.json"
SIZES = [1, 8, 12, 16, 20, 24, 32, 38, 48, 64, 72, 96, 128, 177, 215, 354, 500]


def _ac102(n: int, suffix: str = ""):
    label = f"AC-102.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label + suffix])


def _text(text: object, **extra: object):
    from avkit_core.domain.capture import TextAnnotation

    fields: dict[str, object] = {
        "x": 10,
        "y": 20,
        "text": text,
        "color": "#000000",
        "font_size": 16,
        "bg_color": None,
    }
    fields.update(extra)
    return TextAnnotation(**fields)  # type: ignore[arg-type]


def _accepted(make: Callable[[], object]) -> bool:
    from pydantic import ValidationError

    from avkit_core.domain.errors import AnnotationValidationError

    try:
        make()
    except (AnnotationValidationError, ValidationError):
        return False
    return True


def _pixels(path: Path) -> tuple[str, tuple[int, int], bytes]:
    from PIL import Image

    with Image.open(path) as image:
        return image.mode, image.size, image.tobytes()


def _geometry() -> dict[str, object]:
    return json.loads(GEOMETRY_FIXTURE.read_text(encoding="utf-8"))


@_ac102(1, "-py")
@pytest.mark.unit
def test_ac_102_1_python_signatures(ac_id: str) -> None:
    assert ac_id == "AC-102.1"
    from tools import capture_bake_fixture as fixture

    from avkit_core.domain import capture
    from avkit_infra.capture import adapter

    assert get_type_hints(capture.normalize_text_newlines) == {"text": str, "return": str}
    assert adapter.TEXT_LINE_GAP == 4
    assert get_type_hints(fixture.write_multiline_fixture) == {
        "out_dir": Path,
        "return": tuple[Path, Path],
    }


@pytest.mark.parametrize(
    ("sent", "stored"),
    [("Hi\r\nHi", "Hi\nHi"), ("Hi\rHi", "Hi\nHi"), ("Hi\r\n\r\nHi", "Hi\n\nHi")],
    ids=["AC-102.2-crlf", "AC-102.2-lone-cr", "AC-102.2-two-crlf"],
)
@pytest.mark.unit
def test_ac_102_2_text_annotation_folds_cr(sent: str, stored: str) -> None:
    mark = _text(sent)
    assert mark.text == stored
    assert "\r" not in mark.text


@_ac102(3)
@pytest.mark.unit
def test_ac_102_3_lf_tab_and_controls_are_stored_as_given(ac_id: str) -> None:
    assert ac_id == "AC-102.3"
    from avkit_core.domain.capture import normalize_text_newlines
    from avkit_core.domain.errors import AnnotationValidationError

    for text in ("Hi\nHi", "a\tb", "a\x01b\x0bc\x0cd\x7f", "\n", "Hi\n\nHi\n"):
        assert _text(text).text == text
        assert normalize_text_newlines(text) == text
    with pytest.raises(AnnotationValidationError):
        _text(12)
    with pytest.raises(AnnotationValidationError):
        _text("")


@pytest.mark.parametrize(
    ("pairs", "accepted"),
    [(250, True), (251, False)],
    ids=["AC-102.4-250-pairs", "AC-102.4-251-pairs"],
)
@pytest.mark.unit
def test_ac_102_4_length_counts_the_folded_text(pairs: int, accepted: bool) -> None:
    from avkit_api.schemas.captures import TextAnnotationIn

    sent = "a\r\n" * pairs
    assert len(sent) == 3 * pairs
    body = {"type": "text", "x": 1, "y": 2, "text": sent, "color": "red", "font_size": 12}
    assert _accepted(lambda: _text(sent)) is accepted
    assert _accepted(lambda: TextAnnotationIn.model_validate(body)) is accepted
    if accepted:
        assert len(_text(sent).text) == 2 * pairs == 500
        assert TextAnnotationIn.model_validate(body).text == "a\n" * pairs


@pytest.mark.parametrize(
    ("sent", "size", "bg"),
    [
        (sent, size, bg)
        for sent in ("Hi\r\nHi", "Hi\rHi")
        for size in (16, 32)
        for bg in (None, "#FFD400")
    ],
    ids=[
        f"AC-102.6-{name}-{size}-{bg}"
        for name in ("crlf", "lone-cr")
        for size in (16, 32)
        for bg in ("plain", "plate")
    ],
)
@pytest.mark.unit
def test_ac_102_6_bake_of_cr_equals_bake_of_lf(
    sent: str, size: int, bg: str | None, tmp_path: Path
) -> None:
    from PIL import Image

    from avkit_infra.capture.adapter import CaptureAdapter

    original = tmp_path / "white.png"
    Image.new("RGB", (160, 120), (255, 255, 255)).save(original, format="PNG")
    adapter = CaptureAdapter()
    folded, lf, one = tmp_path / "folded.png", tmp_path / "lf.png", tmp_path / "one.png"
    adapter.bake(original, [_text(sent, font_size=size, bg_color=bg)], folded)
    adapter.bake(original, [_text("Hi\nHi", font_size=size, bg_color=bg)], lf)
    adapter.bake(original, [_text("Hi", font_size=size, bg_color=bg)], one)
    assert _pixels(lf) != _pixels(one)
    assert _pixels(folded) == _pixels(lf)


@_ac102(7)
@pytest.mark.unit
def test_ac_102_7_geometry_fixture_matches_pillow(ac_id: str) -> None:
    assert ac_id == "AC-102.7"
    from avkit_infra.capture import adapter

    data = _geometry()
    pitch = data["segoe_line_pitch"]
    assert isinstance(pitch, dict)
    assert [int(size) for size in pitch] == SIZES
    for size in SIZES:
        font = adapter._load_font(size)  # pyright: ignore[reportPrivateUsage]
        expected = int(font.getbbox("A")[3]) + adapter.TEXT_LINE_GAP
        assert pitch[str(size)] == expected, size
    plates = data["text_plates"]
    assert isinstance(plates, list) and len(plates) == 16
    for case in plates:
        assert set(case) == {"x", "y", "text", "font_size", "box"}
        box = adapter.text_plate_box(case["x"], case["y"], case["text"], case["font_size"])
        assert list(box) == case["box"], case
    assert any("\n" in case["text"] for case in plates)


@_ac102(23)
@pytest.mark.unit
def test_ac_102_23_crop_keeps_or_drops_a_multiline_mark(ac_id: str) -> None:
    assert ac_id == "AC-102.23"
    from avkit_core.domain.capture import clip_mark

    mark = _text("Hi\n\nHi\n", x=30, y=40, font_size=32)
    kept, how = clip_mark(mark, 10, 15, 100, 100)
    assert how == "kept"
    assert kept == _text("Hi\n\nHi\n", x=20, y=25, font_size=32)
    dropped, how = clip_mark(mark, 31, 0, 100, 100)
    assert (dropped, how) == (None, "dropped")
    dropped, how = clip_mark(mark, 0, 41, 100, 100)
    assert (dropped, how) == (None, "dropped")
