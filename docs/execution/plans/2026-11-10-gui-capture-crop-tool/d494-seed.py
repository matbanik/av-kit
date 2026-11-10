"""Session 60 D-494 seed (task row 7, under D-521 A or B; implementation-plan.md D494_RUN).

Writes ROOT/seed/chart-source.png, 1200x800, with Pillow: a light background, a title band, and
four panels in a 2x2 grid. The top-right panel (PANEL: x 640, y 120, 520x320) is filled with
one solid colour and labelled "Revenue". It also writes ROOT/seed/panel.json with the panel box
in px and as fractions, which d494-check.py reads, and prints both.

ROOT is C:/Temp/av-kit/s60/d494/root unless `--root` says otherwise. The seed refuses a ROOT
that already holds files, so a run never mixes with an earlier one; nothing is deleted here.
No image leaves the machine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SIZE = (1200, 800)
PANEL = {"x": 640, "y": 120, "width": 520, "height": 320}
OTHERS = (
    {"x": 40, "y": 120, "width": 560, "height": 320},
    {"x": 40, "y": 460, "width": 560, "height": 300},
    {"x": 640, "y": 460, "width": 520, "height": 300},
)


def draw(path: Path) -> None:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", SIZE, (245, 246, 248))
    pen = ImageDraw.Draw(image)
    pen.rectangle((0, 0, SIZE[0], 90), fill=(30, 41, 59))
    pen.text((40, 36), "Quarterly dashboard", fill=(255, 255, 255))
    for n, box in enumerate(OTHERS):
        right, bottom = box["x"] + box["width"] - 1, box["y"] + box["height"] - 1
        pen.rectangle((box["x"], box["y"], right, bottom), fill=(255, 255, 255), outline=(203, 213, 225), width=2)
        for bar in range(6):
            left = box["x"] + 30 + bar * 80
            pen.rectangle((left, bottom - 40 - (bar + n) * 25 % 200, left + 40, bottom - 20), fill=(148, 163, 184))
    right, bottom = PANEL["x"] + PANEL["width"] - 1, PANEL["y"] + PANEL["height"] - 1
    pen.rectangle((PANEL["x"], PANEL["y"], right, bottom), fill=(14, 116, 144))
    pen.text((PANEL["x"] + 24, PANEL["y"] + 20), "Revenue", fill=(255, 255, 255))
    image.save(path, format="PNG")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default="C:/Temp/av-kit/s60/d494/root")
    args = parser.parse_args()
    root = Path(args.root)
    if root.exists() and any(root.iterdir()):
        print(f"d494-seed: {root} already holds files; the run needs a fresh root (not deleted here)")
        return 1
    seed = root / "seed"
    seed.mkdir(parents=True)
    draw(seed / "chart-source.png")
    fractions = {
        "x": PANEL["x"] / SIZE[0],
        "y": PANEL["y"] / SIZE[1],
        "width": PANEL["width"] / SIZE[0],
        "height": PANEL["height"] / SIZE[1],
    }
    record = {"image": {"width": SIZE[0], "height": SIZE[1]}, "panel_px": PANEL, "panel_fraction": fractions}
    (seed / "panel.json").write_bytes((json.dumps(record, indent=2) + "\n").encode("utf-8"))
    print(f"d494-seed: {seed / 'chart-source.png'} {SIZE[0]}x{SIZE[1]}")
    print(f"panel px {PANEL}")
    print(f"panel fraction {fractions}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
