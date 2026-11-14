"""MEU-82 ``TEXT_FIXTURE``: the committed PNGs equal a fresh bake.

Imports stay inside tests so collection cannot ERROR.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "ui" / "tests" / "e2e" / "fixtures"


def _pixels(path: Path) -> tuple[str, tuple[int, int], bytes]:
    from PIL import Image

    with Image.open(path) as image:
        return image.mode, image.size, image.tobytes()


@pytest.mark.parametrize("ac_id", ["AC-82.5"], ids=["AC-82.5"])
@pytest.mark.unit
def test_ac_82_5_committed_annotated_png_equals_a_fresh_bake(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-82.5"
    from tools import capture_bake_fixture as fixture

    original = FIXTURES / fixture.ORIGINAL_NAME
    mode, size, data = _pixels(original)
    assert (mode, size) == ("RGB", (240, 120))
    assert data == b"\xff" * (240 * 120 * 3)
    fresh = fixture.bake(original, [fixture.TEXT_FIXTURE_MARK], tmp_path / "fresh.png")
    assert _pixels(FIXTURES / fixture.ANNOTATED_NAME) == _pixels(fresh)


@pytest.mark.parametrize("ac_id", ["AC-82.5"], ids=["AC-82.5-moved"])
@pytest.mark.unit
def test_ac_82_5_bake_one_px_lower_differs(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-82.5"
    from tools import capture_bake_fixture as fixture

    mark = fixture.TEXT_FIXTURE_MARK
    moved = dataclasses.replace(mark, y=mark.y + 1)
    lower = fixture.bake(FIXTURES / fixture.ORIGINAL_NAME, [moved], tmp_path / "lower.png")
    assert _pixels(FIXTURES / fixture.ANNOTATED_NAME) != _pixels(lower)


@pytest.mark.parametrize("ac_id", ["AC-82.5"], ids=["AC-82.5-writer"])
@pytest.mark.unit
def test_ac_82_5_writer_reproduces_the_committed_pngs(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-82.5"
    from tools import capture_bake_fixture as fixture

    assert fixture.main(["--out", str(tmp_path)]) == 0
    for name in (fixture.ORIGINAL_NAME, fixture.ANNOTATED_NAME):
        assert _pixels(tmp_path / name) == _pixels(FIXTURES / name), name


# ------------------------------------------------------------ MEU-90 region fixture (Session 39)
REGION_NAMES = (
    "capture-region-pass.json",
    "capture-region-original.png",
    "capture-region-annotated.png",
)
COLOUR_CHUNKS = (b"gAMA", b"iCCP", b"sRGB")


def _ac90(n: int, suffix: str = ""):
    label = f"AC-90.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label + suffix])


def _png_chunks(path: Path) -> list[bytes]:
    data = path.read_bytes()
    chunks, i = [], 8
    while i < len(data):
        length = int.from_bytes(data[i : i + 4], "big")
        chunks.append(data[i + 4 : i + 8])
        i += 12 + length
    return chunks


@_ac90(8)
@pytest.mark.unit
def test_ac_90_8_region_fixture_reproduces_the_committed_set(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-90.8"
    import json

    from tools import capture_bake_fixture as fixture

    from avkit_core.domain.capture import PixelateAnnotation

    assert (
        fixture.REGION_FIXTURE_NAME,
        fixture.REGION_ORIGINAL_NAME,
        fixture.REGION_ANNOTATED_NAME,
    ) == REGION_NAMES
    fixture.write_region_fixture(tmp_path)
    committed = json.loads((FIXTURES / fixture.REGION_FIXTURE_NAME).read_text(encoding="utf-8"))
    fresh = json.loads((tmp_path / fixture.REGION_FIXTURE_NAME).read_text(encoding="utf-8"))
    assert fresh == committed
    for case in committed["cases"]:
        assert set(case) == {"name", "width", "height", "pixels", "marks", "expected"}
        assert len(case["pixels"]) == len(case["expected"]) == case["width"] * case["height"] * 3
    for name in (fixture.REGION_ORIGINAL_NAME, fixture.REGION_ANNOTATED_NAME):
        assert _pixels(tmp_path / name) == _pixels(FIXTURES / name), name
        assert not set(_png_chunks(FIXTURES / name)) & set(COLOUR_CHUNKS), name
    original = FIXTURES / fixture.REGION_ORIGINAL_NAME
    assert _pixels(original)[:2] == ("RGB", (240, 160))
    marks = fixture.region_annotations(fixture.REGION_IMAGE_MARKS)
    assert any(isinstance(mark, PixelateAnnotation) for mark in marks)
    rebaked = fixture.bake(original, marks, tmp_path / "rebaked.png")
    assert _pixels(FIXTURES / fixture.REGION_ANNOTATED_NAME) == _pixels(rebaked)
    coarser = [
        dataclasses.replace(mark, block_size=11) if isinstance(mark, PixelateAnnotation) else mark
        for mark in marks
    ]
    other = fixture.bake(original, coarser, tmp_path / "block-11.png")
    assert _pixels(FIXTURES / fixture.REGION_ANNOTATED_NAME) != _pixels(other)


@_ac90(8, "-main")
@pytest.mark.unit
def test_ac_90_8_main_region_writes_only_the_region_set(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-90.8"
    from tools import capture_bake_fixture as fixture

    from avkit_core.domain.capture import PixelateAnnotation

    assert PixelateAnnotation.__name__ == "PixelateAnnotation"
    assert fixture.main(["--region", "--out", str(tmp_path)]) == 0
    assert sorted(path.name for path in tmp_path.iterdir()) == sorted(REGION_NAMES)


# ------------------------------------------------- MEU-102 multi-line text fixture (Session 70)
MULTILINE_NAMES = (
    "capture-fidelity-multiline-original.png",
    "capture-fidelity-multiline-annotated.png",
)


def _ac102(n: int, suffix: str = ""):
    label = f"AC-102.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label + suffix])


@_ac102(8)
@pytest.mark.unit
def test_ac_102_8_multiline_fixture_equals_a_fresh_bake(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-102.8"
    from tools import capture_bake_fixture as fixture

    assert (fixture.MULTILINE_ORIGINAL_NAME, fixture.MULTILINE_ANNOTATED_NAME) == MULTILINE_NAMES
    assert fixture.MULTILINE_ORIGINAL_SIZE == (240, 160)
    mark = fixture.MULTILINE_FIXTURE_MARK
    assert (mark.x, mark.y, mark.text, mark.font_size) == (20, 16, "Hi\n\nHi\n", 32)
    assert fixture.write_multiline_fixture(tmp_path) == tuple(tmp_path / n for n in MULTILINE_NAMES)
    mode, size, data = _pixels(tmp_path / fixture.MULTILINE_ORIGINAL_NAME)
    assert (mode, size) == ("RGB", (240, 160))
    assert data == b"\xff" * (240 * 160 * 3)
    for name in MULTILINE_NAMES:
        assert _pixels(tmp_path / name) == _pixels(FIXTURES / name), name
    one_line = fixture.bake(
        FIXTURES / fixture.MULTILINE_ORIGINAL_NAME,
        [dataclasses.replace(mark, text="Hi")],
        tmp_path / "one-line.png",
    )
    assert _pixels(FIXTURES / fixture.MULTILINE_ANNOTATED_NAME) != _pixels(one_line)


@_ac102(8, "-main")
@pytest.mark.unit
def test_ac_102_8_main_multiline_writes_only_the_pair(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-102.8"
    from tools import capture_bake_fixture as fixture

    multi, default, region = tmp_path / "multi", tmp_path / "default", tmp_path / "region"
    assert fixture.main(["--multiline", "--out", str(multi)]) == 0
    assert sorted(path.name for path in multi.iterdir()) == sorted(MULTILINE_NAMES)
    assert fixture.main(["--out", str(default)]) == 0
    assert sorted(path.name for path in default.iterdir()) == sorted(
        (fixture.ORIGINAL_NAME, fixture.ANNOTATED_NAME)
    )
    assert fixture.main(["--region", "--out", str(region)]) == 0
    assert sorted(path.name for path in region.iterdir()) == sorted(REGION_NAMES)
    with pytest.raises(SystemExit):
        fixture.main(["--multiline", "--region", "--out", str(tmp_path / "both")])
