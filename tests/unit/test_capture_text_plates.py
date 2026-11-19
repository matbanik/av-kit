"""MEU-161 text plate metrics: the Pillow plate fixture against the bake (Session 97, AC-161.6).

`ui/tests/e2e/fixtures/capture-text-plates.json` holds the box the bake paints for each case,
`adapter.text_plate_box` (l, t, r, b) as [l, t, r - l + 1, b - t + 1]; the Vitest
`capture-text-plates.test.ts` reads it to pin the preview. This guard keeps the fixture honest:
with the fixture's font every case must equal the live bake; with another font build (a CI
runner) only the fixture's own recorded values are checked, because another font paints other
boxes. It never skips.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PLATE_FIXTURE = REPO_ROOT / "ui" / "tests" / "e2e" / "fixtures" / "capture-text-plates.json"
FONT = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeui.ttf"
HEAD_KEYS = {"generator", "font", "font_sha256", "pillow", "raqm", "box", "breadth", "matrix"}
SECTIONS = {"breadth": 2448, "matrix": 40}


def _load(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _cases(data: dict[str, object]):
    """Each case as (section, x, y, text, size, recorded box)."""
    for name in SECTIONS:
        section = data[name]
        assert isinstance(section, dict)
        x, y, sizes = section["x"], section["y"], section["sizes"]
        for case in section["cases"]:
            assert len(case["boxes"]) == len(sizes), (name, case["text"])
            for size, box in zip(sizes, case["boxes"], strict=True):
                yield name, x, y, case["text"], size, box


def fixture_mismatches(path: Path) -> list[tuple[str, str, int, list[int], list[int]]]:
    """Every case of the fixture at `path` whose box differs from what the bake paints."""
    from avkit_infra.capture import adapter

    out: list[tuple[str, str, int, list[int], list[int]]] = []
    for name, x, y, text, size, box in _cases(_load(Path(path))):
        left, top, right, bottom = adapter.text_plate_box(x, y, text or " ", size)
        painted = [left, top, right - left + 1, bottom - top + 1]
        if list(box) != painted:
            out.append((name, text, size, list(box), painted))
    return out


def _local_font_sha() -> str | None:
    return hashlib.sha256(FONT.read_bytes()).hexdigest() if FONT.is_file() else None


@pytest.mark.unit
def test_ac_161_6_plate_fixture_matches_pillow() -> None:
    data = _load(PLATE_FIXTURE)
    assert set(data) == HEAD_KEYS
    for name, count in SECTIONS.items():
        boxes = [box for sec, *_, box in _cases(data) if sec == name]
        assert len(boxes) == count, name
        for box in boxes:
            assert len(box) == 4 and all(type(v) is int for v in box), (name, box)
    if _local_font_sha() == data["font_sha256"]:
        bad = fixture_mismatches(PLATE_FIXTURE)
        assert bad == [], bad[:10]
        return
    print("AC-161.6: the local segoeui.ttf differs from the fixture's font; recorded values only")
    breadth = data["breadth"]
    assert isinstance(breadth, dict)
    assert (breadth["x"], breadth["y"]) == (20, 30)
    hi = next(case for case in breadth["cases"] if case["text"] == "Hi")
    assert hi["boxes"][breadth["sizes"].index(16)] == [20, 36, 16, 13]
