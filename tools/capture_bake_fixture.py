"""Write the capture fidelity fixture PNGs (Session 36 ``TEXT_FIXTURE``, D-18).

Usage: ``python tools/capture_bake_fixture.py --out ui/tests/e2e/fixtures``
(``--region`` writes only the Session 39 region set).

``capture-fidelity-original.png`` is a 240x120 all-white RGB image.
``capture-fidelity-annotated.png`` is the real ``CaptureAdapter.bake`` of it with
``TEXT_FIXTURE_MARK``. ``tests/unit/test_capture_bake_fixture.py`` re-bakes the mark and
compares pixels, so the committed PNGs cannot go stale.

``write_region_fixture`` writes the Session 39 region set (``REGION_FIXTURE`` and
``REGION_IMAGE_FIXTURE``): ``capture-region-pass.json`` holds ``REGION_CASES``, each input
with the RGB of its real bake, and ``capture-region-original.png`` /
``capture-region-annotated.png`` are the Electron oracle's image pair.
"""

from __future__ import annotations

import argparse
import json
import random
import tempfile
from collections.abc import Sequence
from pathlib import Path

from PIL import Image

from avkit_core.domain.capture import Annotation, TextAnnotation, clip_mark
from avkit_core.services.capture import (
    SIDECAR_VERSION,
    annotations_from_sidecar,
    annotations_to_wire,
)
from avkit_infra.capture.adapter import CaptureAdapter

ORIGINAL_NAME = "capture-fidelity-original.png"
ANNOTATED_NAME = "capture-fidelity-annotated.png"
ORIGINAL_SIZE = (240, 120)
TEXT_FIXTURE_MARK = TextAnnotation(
    x=20, y=30, text="Hi", color="#000000", font_size=32, bg_color="#FFD400"
)


def write_original(path: Path, size: tuple[int, int] = ORIGINAL_SIZE) -> Path:
    """Write an all-white RGB PNG of ``size``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (255, 255, 255)).save(path, format="PNG")
    return path


def bake(original: Path, annotations: Sequence[Annotation], output: Path) -> Path:
    """Bake ``annotations`` onto ``original`` with the production adapter."""
    CaptureAdapter().bake(original, annotations, output)
    return output


def write_fixture(out_dir: Path) -> tuple[Path, Path]:
    """Write the original and the annotated fixture PNGs into ``out_dir``."""
    original = write_original(out_dir / ORIGINAL_NAME)
    annotated = bake(original, [TEXT_FIXTURE_MARK], out_dir / ANNOTATED_NAME)
    return original, annotated


REGION_FIXTURE_NAME = "capture-region-pass.json"
REGION_ORIGINAL_NAME = "capture-region-original.png"
REGION_ANNOTATED_NAME = "capture-region-annotated.png"
REGION_ORIGINAL_SIZE = (240, 160)
REGION_SEED = 39
REGION_BG = (240, 240, 240)
REGION_INK = (20, 20, 20)
# REGION_IMAGE_MARKS, in REGION_DTO (wire) form: the detail the Electron seam serves.
REGION_IMAGE_MARKS: tuple[dict[str, object], ...] = (
    {"type": "pixelate", "x": 10, "y": 10, "width": 100, "height": 70, "block_size": 10},
    {"type": "eraser", "x": 140, "y": 40, "width": 40, "height": 30},
)
# R-1 `composed`: neighbouring colours one step apart on every band, so 2x2 and 3x3 block
# sums land on .25, .5 and .75 (the rounding boundaries).
_BOUNDARY_PAIRS = (
    ((10, 101, 200), (11, 102, 201)),
    ((0, 255, 7), (1, 254, 8)),
    ((127, 128, 3), (128, 127, 4)),
)

RegionCase = tuple[str, int, int, list[int], list[dict[str, object]]]


def _noise(rng: random.Random, width: int, height: int) -> list[int]:
    return [rng.randrange(256) for _ in range(width * height * 3)]


def _boundary_pattern(width: int, height: int) -> list[int]:
    pixels: list[int] = []
    for y in range(height):
        for x in range(width):
            a, b = _BOUNDARY_PAIRS[((x // 2) + (y // 2)) % len(_BOUNDARY_PAIRS)]
            pixels.extend(a if (x + y) % 4 == 0 else b)
    return pixels


def _pixelate(x: int, y: int, width: int, height: int, block: int) -> dict[str, object]:
    return {"type": "pixelate", "x": x, "y": y, "width": width, "height": height} | {
        "block_size": block
    }


def _eraser(x: int, y: int, width: int, height: int) -> dict[str, object]:
    return {"type": "eraser", "x": x, "y": y, "width": width, "height": height}


_Rgb = tuple[int, int, int]


def _stems_pattern(width: int, height: int) -> list[int]:
    """Flat ``REGION_BG`` with two ink stems crossing an eraser's top and bottom border."""
    pixels: list[int] = []
    for y in range(height):
        for x in range(width):
            pixels.extend(REGION_INK if x in (7, 9) and 2 <= y <= 10 else REGION_BG)
    return pixels


def _checker(width: int, height: int, even: _Rgb, odd: _Rgb) -> list[int]:
    pixels: list[int] = []
    for y in range(height):
        for x in range(width):
            pixels.extend(even if (x + y) % 2 == 0 else odd)
    return pixels


def _crop_case(
    name: str,
    size: tuple[int, int],
    pixels: Sequence[int],
    mark: dict[str, object],
    box: tuple[int, int, int, int],
) -> RegionCase:
    """A crop case (MEU-130, D-493): the crop's own pixels and the mark `clip_mark` returns."""
    width = size[0]
    left, top, crop_width, crop_height = box
    cut: list[int] = []
    for y in range(top, top + crop_height):
        start = (y * width + left) * 3
        cut.extend(pixels[start : start + crop_width * 3])
    clipped, _ = clip_mark(region_annotations([mark])[0], left, top, crop_width, crop_height)
    if clipped is None:
        raise ValueError(f"{name}: the mark misses the crop")
    return (name, crop_width, crop_height, cut, annotations_to_wire([clipped]))


def crop_cases() -> list[RegionCase]:
    """The crop cases, appended to ``REGION_CASES``; their own seed keeps the others' bytes."""
    rng = random.Random(REGION_SEED + 1)
    return [
        # The crop keeps a 3 px sliver of a block-4 pixelate mark at its left edge.
        _crop_case(
            "crop-pixelate-sliver",
            (24, 16),
            _noise(rng, 24, 16),
            _pixelate(2, 2, 18, 10, 4),
            (17, 3, 6, 8),
        ),
        # The mark covers the crop's top-left corner from outside it.
        _crop_case(
            "crop-pixelate-corner",
            (16, 12),
            _noise(rng, 16, 12),
            _pixelate(0, 0, 10, 8, 3),
            (6, 4, 10, 8),
        ),
        # The eraser is cut at the crop's right edge, so its ring has no right side.
        _crop_case(
            "crop-eraser-edge", (16, 12), _noise(rng, 16, 12), _eraser(8, 3, 8, 6), (0, 0, 12, 12)
        ),
        # The eraser sits inside the crop with its whole ring, which the stems cross.
        _crop_case(
            "crop-eraser-ring",
            (20, 14),
            _stems_pattern(20, 14),
            _eraser(6, 4, 5, 5),
            (3, 1, 12, 12),
        ),
    ]


def region_cases() -> list[RegionCase]:
    """``REGION_CASES`` inputs ``(name, width, height, pixels, marks)``; marks in wire form."""
    rng = random.Random(REGION_SEED)
    return [
        ("pixelate-interior", 16, 12, _noise(rng, 16, 12), [_pixelate(2, 1, 11, 8, 3)]),
        ("pixelate-clipped", 16, 12, _noise(rng, 16, 12), [_pixelate(9, 6, 12, 10, 4)]),
        ("pixelate-negative-origin", 16, 12, _noise(rng, 16, 12), [_pixelate(-3, 2, 9, 7, 3)]),
        ("pixelate-big-block", 16, 12, _noise(rng, 16, 12), [_pixelate(4, 3, 7, 5, 100)]),
        ("pixelate-empty", 16, 12, _noise(rng, 16, 12), [_pixelate(5, 5, 0, 6, 2)]),
        (
            "pixelate-repeat-overlap",
            32,
            24,
            _boundary_pattern(32, 24),
            [
                _pixelate(2, 2, 17, 13, 4),
                _pixelate(7, 5, 19, 16, 3),
                _pixelate(0, 0, 32, 24, 5),
            ],
        ),
        # ERASER_SAMPLE cases (MEU-91). The stems put 4 ink pixels in a 24-pixel ring: the mode is
        # REGION_BG, the mean is not.
        ("eraser-stems", 20, 14, _stems_pattern(20, 14), [_eraser(6, 4, 5, 5)]),
        # A 6/6 tie in the ring between (9, 9, 9) and (0, 0, 0): the smaller packed value wins.
        ("eraser-tie", 4, 4, _checker(4, 4, (9, 9, 9), (0, 0, 0)), [_eraser(1, 1, 2, 2)]),
        ("eraser-clipped", 16, 12, _noise(rng, 16, 12), [_eraser(-3, 2, 6, 3)]),
        # The rectangle covers the image, so the outer ring is empty: the inner ring gives 1, 2, 3.
        ("eraser-cover", 6, 5, [200, 0, 0] + [1, 2, 3] * 29, [_eraser(-2, -2, 20, 20)]),
        # Block 3 makes the pixelated ring's mode a colour the original does not have.
        (
            "pixelate-then-eraser",
            32,
            24,
            _boundary_pattern(32, 24),
            [_pixelate(0, 0, 32, 24, 3), _eraser(10, 7, 6, 5)],
        ),
        *crop_cases(),
    ]


def region_annotations(marks: Sequence[dict[str, object]]) -> list[Annotation]:
    """Wire marks to domain annotations through the sidecar reader."""
    return annotations_from_sidecar({"version": SIDECAR_VERSION, "annotations": list(marks)})


def _rgb_png(path: Path, width: int, height: int, pixels: Sequence[int]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.frombytes("RGB", (width, height), bytes(pixels)).save(path, format="PNG")
    return path


def _rgb(path: Path) -> list[int]:
    with Image.open(path) as image:
        return list(image.convert("RGB").tobytes())


def write_region_original(path: Path) -> Path:
    """``REGION_IMAGE_FIXTURE`` original: gradient left, flat ``REGION_BG`` and stems right."""
    width, height = REGION_ORIGINAL_SIZE
    image = Image.new("RGB", (width, height), REGION_BG)
    for y in range(height):
        for x in range(width // 2):
            image.putpixel((x, y), (2 * x, y, (x + y) % 256))
    for x in (150, 162):  # two dark stems crossing the eraser's top and bottom border
        for y in range(30, 81):
            image.putpixel((x, y), REGION_INK)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
    return path


def write_region_fixture(out_dir: Path) -> tuple[Path, Path, Path]:
    """Write ``REGION_FIXTURE`` and the ``REGION_IMAGE_FIXTURE`` pair into ``out_dir``."""
    cases: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name, width, height, pixels, marks in region_cases():
            source = _rgb_png(work / f"{name}.png", width, height, pixels)
            baked = bake(source, region_annotations(marks), work / f"{name}.baked.png")
            cases.append(
                {
                    "name": name,
                    "width": width,
                    "height": height,
                    "pixels": pixels,
                    "marks": marks,
                    "expected": _rgb(baked),
                }
            )
    out_dir.mkdir(parents=True, exist_ok=True)
    fixture = out_dir / REGION_FIXTURE_NAME
    body = ",\n".join(json.dumps(case) for case in cases)
    fixture.write_text('{"cases": [\n' + body + "\n]}\n", encoding="utf-8", newline="\n")
    original = write_region_original(out_dir / REGION_ORIGINAL_NAME)
    marks = region_annotations(REGION_IMAGE_MARKS)
    annotated = bake(original, marks, out_dir / REGION_ANNOTATED_NAME)
    return fixture, original, annotated


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="directory for the fixtures")
    parser.add_argument(
        "--region", action="store_true", help="write only the region set (REGION_FIXTURE)"
    )
    args = parser.parse_args(argv)
    paths = write_region_fixture(args.out) if args.region else write_fixture(args.out)
    for path in paths:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
