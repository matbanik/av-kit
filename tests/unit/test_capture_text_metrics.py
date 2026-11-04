"""MEU-82 Segoe UI text metrics vs ``GEOMETRY_FIXTURE``.

Imports stay inside tests so collection cannot ERROR.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GEOMETRY_FIXTURE = REPO_ROOT / "ui" / "tests" / "e2e" / "fixtures" / "capture-geometry.json"
SEGOE_UI = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts" / "segoeui.ttf"


def _segoe_ascent_fixture() -> dict[int, int]:
    data = json.loads(GEOMETRY_FIXTURE.read_text(encoding="utf-8"))
    return {int(size): int(ascent) for size, ascent in data["segoe_ascent"].items()}


def _ascent_mismatches(expected: dict[int, int]) -> list[tuple[int, int, int]]:
    """Return ``(size, expected, pillow)`` for every size where Pillow disagrees."""
    from PIL import ImageFont

    mismatches = []
    for size, ascent in sorted(expected.items()):
        pillow = ImageFont.truetype(str(SEGOE_UI), size).getmetrics()[0]
        if pillow != ascent:
            mismatches.append((size, ascent, pillow))
    return mismatches


@pytest.mark.parametrize("ac_id", ["AC-82.2"], ids=["AC-82.2"])
@pytest.mark.unit
def test_ac_82_2_pillow_ascent_matches_geometry_fixture(ac_id: str) -> None:
    assert ac_id == "AC-82.2"
    expected = _segoe_ascent_fixture()
    sizes = [1, 8, 12, 16, 20, 24, 32, 38, 48, 64, 72, 96, 128, 177, 215, 354, 500]
    assert sorted(expected) == sizes
    assert SEGOE_UI.is_file()
    assert _ascent_mismatches(expected) == []


@pytest.mark.parametrize("size", [38, 177, 215, 354], ids=lambda s: f"AC-82.2-off-by-one-{s}")
@pytest.mark.unit
def test_ac_82_2_comparator_detects_a_fixture_edited_by_one(size: int) -> None:
    edited = _segoe_ascent_fixture()
    edited[size] += 1
    assert _ascent_mismatches(edited) == [(size, edited[size], edited[size] - 1)]


@pytest.mark.parametrize("ac_id", ["AC-82.2"], ids=["AC-82.2-baseline"])
@pytest.mark.unit
def test_ac_82_2_la_to_ls_offset_is_the_ascent(ac_id: str) -> None:
    assert ac_id == "AC-82.2"
    from PIL import Image, ImageDraw, ImageFont

    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    x, y = 10, 20
    for size, ascent in sorted(_segoe_ascent_fixture().items()):
        font = ImageFont.truetype(str(SEGOE_UI), size)
        la_bottom = draw.textbbox((x, y), "Hi", font=font, anchor="la")[3]
        ls_bottom = draw.textbbox((x, y), "Hi", font=font, anchor="ls")[3]
        assert la_bottom - ls_bottom == ascent, size
