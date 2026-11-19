"""Session 97 generator (task row 6; AC-161.4; D-1251): the Pillow text-plate fixture.

    uv run --no-sync python <plan>/plate-fixture.py --out <file>     # write the fixture elsewhere
    uv run --no-sync python <plan>/plate-fixture.py --write          # write the tracked fixture
    uv run --no-sync python <plan>/plate-fixture.py --check          # exit 0 when it matches

It writes `ui/tests/e2e/fixtures/capture-text-plates.json` (LF, UTF-8, no BOM, one final LF).
Each box is what the bake paints for a text mark's plate: `adapter.text_plate_box(x, y, text,
size)` gives Pillow's inclusive `(l, t, r, b)`, and `_apply_text` fills `draw.rectangle` over it,
so the painted box is `[l, t, r - l + 1, b - t + 1]` as `[x, y, width, height]`. An empty text
is measured as one space, the rule the preview uses (Pillow's empty box is degenerate).

Two sections:

* `breadth`: 18 texts at (20, 30), sizes 1 to 128 and 160, 177, 200, 215, 256, 354, 400, 500
  (2448 cases); the last four are dense in kerning pairs (expert pass M1). The Vitest counts
  how many the preview matches exactly and how far the rest are.
* `matrix`: 10 multi-line texts at (10, 20), sizes 8, 16, 32 and 64 (40 cases). It replaces the
  line-union oracle of AC-102.10.

The head names the font's SHA-256, the Pillow version and whether Pillow has raqm (the bake's
layout, and so its kerning, differs with it), so a different font or Pillow shows up
as a `--check` failure rather than a quiet drift.

Every write leaves no partial file (`write_new`; Session 95 RULE-1): `--out` creates its file
exclusively and removes it on a write error; `--write` writes `<file>.ehp-tmp` and replaces the
tracked file in one `os.replace`, so an error keeps the old bytes. `EHP_WRITE_FAULT=1` injects
that error after the create (task row 0 and the write rows test it).

Exit 0 on success (or a match with `--check`), 1 on a mismatch or a refused precondition, 2 on
an argument problem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FIXTURE = REPO / "ui/tests/e2e/fixtures/capture-text-plates.json"
FONT = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "segoeui.ttf"
GENERATOR = "docs/execution/plans/2026-11-19-e2e-host-parity/plate-fixture.py"
BREADTH_ORIGIN = (20, 30)
BREADTH_SIZES = [*range(1, 129), 160, 177, 200, 215, 256, 354, 400, 500]
BREADTH_TEXTS = [
    "Hi",
    "Hello world",
    "The quick brown fox",
    "WWW",
    "iiii",
    "0123456789",
    "Capture 100%",
    "AV To",
    "Hi\n\nHi\n",
    "A\nBB",
    "#$%&@",
    "gjpqy",
    "  \n  ",
    "",
    "AVAVAVAVAVAV",
    "Yo, To Ta Te Va We",
    "WAVE TOYOTA LTA",
    "Tomorrow, Wednesday: AVATAR",
]
MATRIX_ORIGIN = (10, 20)
MATRIX_SIZES = [8, 16, 32, 64]
MATRIX_TEXTS = [
    "Hi\nHi",
    "Hi\n\nHi",
    "Hi\n",
    "\nHi",
    "\n",
    "Hello\nW\ngy",
    "Hi\n\nHello\n",
    "i\nWWWW",
    "  \n  ",
    "Hello",
]


def painted(x: int, y: int, text: str, size: int) -> list[int]:
    sys.path.insert(0, str(REPO / "packages/infrastructure/src"))
    from avkit_infra.capture.adapter import text_plate_box

    left, top, right, bottom = text_plate_box(x, y, text or " ", size)
    return [left, top, right - left + 1, bottom - top + 1]


def section(origin: tuple[int, int], sizes: list[int], texts: list[str]) -> dict[str, object]:
    x, y = origin
    cases = [
        {"text": text, "boxes": [painted(x, y, text, size) for size in sizes]} for text in texts
    ]
    return {"x": x, "y": y, "sizes": sizes, "cases": cases}


def render(doc: dict[str, object]) -> bytes:
    """One case per line, so a diff names the text that moved."""
    head = {k: v for k, v in doc.items() if k not in ("breadth", "matrix")}
    out = ["{"]
    for key, value in head.items():
        out.append(f"  {json.dumps(key)}: {json.dumps(value, ensure_ascii=False)},")
    for name in ("breadth", "matrix"):
        sec = doc[name]
        assert isinstance(sec, dict)
        out.append(f'  "{name}": {{')
        out.append(f'    "x": {sec["x"]},')
        out.append(f'    "y": {sec["y"]},')
        out.append(f'    "sizes": {json.dumps(sec["sizes"])},')
        out.append('    "cases": [')
        cases = sec["cases"]
        assert isinstance(cases, list)
        for i, case in enumerate(cases):
            comma = "," if i < len(cases) - 1 else ""
            out.append(
                f"      {json.dumps(case, ensure_ascii=False, separators=(',', ':'))}{comma}"
            )
        out.append("    ]")
        out.append("  }," if name == "breadth" else "  }")
    out.append("}")
    data = ("\n".join(out) + "\n").encode("utf-8")
    json.loads(data)
    return data


def build() -> bytes:
    import PIL
    from PIL import features

    if not FONT.is_file():
        raise ValueError(f"the font is missing: {FONT.name}")
    doc: dict[str, object] = {
        "generator": GENERATOR,
        "font": "segoeui.ttf",
        "font_sha256": hashlib.sha256(FONT.read_bytes()).hexdigest(),
        "pillow": PIL.__version__,
        "raqm": bool(features.check("raqm")),
        "box": "[x, y, width, height] painted by the bake: adapter.text_plate_box (l, t, r, b)"
        " as [l, t, r - l + 1, b - t + 1]; an empty text is measured as one space",
        "breadth": section(BREADTH_ORIGIN, BREADTH_SIZES, BREADTH_TEXTS),
        "matrix": section(MATRIX_ORIGIN, MATRIX_SIZES, MATRIX_TEXTS),
    }
    return render(doc)


FAULT_ENV = "EHP_WRITE_FAULT"


def write_new(target: Path, data: bytes, *, replace: bool) -> str | None:
    """Write `data` with no partial file left (Session 95 RULE-1); return an error or None.

    With `replace` the bytes go to `<target>.ehp-tmp` (created exclusively) and then replace
    `target` in one `os.replace`; without it `target` itself is created exclusively. A write,
    flush or close error removes the file this call created, so `target` keeps its old bytes
    (or stays absent). `EHP_WRITE_FAULT=1` raises that error after the create, for the test.
    """
    made = target.with_name(target.name + ".ehp-tmp") if replace else target
    try:
        fh = made.open("xb")
    except FileExistsError:
        return f"{made.name} exists"
    except OSError as exc:
        return f"create {made.name}: {type(exc).__name__}"
    try:
        with fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
            if os.environ.get(FAULT_ENV) == "1":
                raise OSError("injected write fault")
        if replace:
            os.replace(made, target)
    except OSError as exc:
        made.unlink(missing_ok=True)
        return f"write {made.name}: {exc}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path, help="write the fixture to this new file")
    mode.add_argument("--write", action="store_true", help="write the tracked fixture")
    mode.add_argument("--check", action="store_true", help="compare the tracked fixture")
    args = parser.parse_args()
    try:
        data = build()
    except (OSError, ValueError) as exc:
        print(f"REFUSED: {exc}")
        return 1
    digest = hashlib.sha256(data).hexdigest()
    cases = len(BREADTH_TEXTS) * len(BREADTH_SIZES) + len(MATRIX_TEXTS) * len(MATRIX_SIZES)
    if args.check:
        now = FIXTURE.read_bytes() if FIXTURE.is_file() else b""
        same = now == data
        print(
            f"plate-fixture check: fixture {len(now)} bytes, generated {len(data)} bytes,"
            f" {cases} cases, sha256 {digest[:16]}, {'match' if same else 'MISMATCH'}"
        )
        return 0 if same else 1
    if args.out is not None:
        problem = write_new(args.out, data, replace=False)
        if problem is not None:
            print(f"REFUSED: {problem}")
            return 1
        print(f"plate-fixture: wrote {len(data)} bytes, {cases} cases, sha256 {digest[:16]}")
        return 0
    problem = write_new(FIXTURE, data, replace=True)
    if problem is not None:
        print(f"REFUSED: {problem}; the tracked fixture keeps its bytes")
        return 1
    print(f"plate-fixture: wrote {FIXTURE.name}, {len(data)} bytes, {cases} cases, {digest[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
