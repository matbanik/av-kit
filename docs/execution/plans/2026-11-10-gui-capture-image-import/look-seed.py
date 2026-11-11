"""Session 61 look seed (task row 6, under D-561 A; implementation-plan.md LOOK_LAUNCH).

Builds the app data the dev app opens for Mat's look, on the real stack and without the
network: `build_services` and `create_app` on ROOT/app-data, a `TestClient`, a
`PUT /api/v1/settings/capture` that points the inbox at ROOT/inbox, one Pillow image in that
inbox, `GET /captures` to register it, and `POST /captures/{id}/annotate` with a rect and a
text, so the look starts on a selected, marked shot that an import must leave alone
(SELECTION_EFFECTS).

It also fills ROOT/drop, outside the inbox, with the files Mat brings in: `red.png` and
`green.png` to drop, `notes.txt` to drop beside them (the not-an-image toast), and `blue.jpg`
to choose through **Import image…**. None of these is registered here.

ROOT is C:/Temp/av-kit/s61/look unless `--root` says otherwise. The seed refuses a ROOT that
already holds files, so a look never opens on an earlier run's state; nothing is deleted here.
It prints each file's name and size. No image leaves the machine.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

GUI_TOKEN = "look-seed-token"
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"
SEEDED = ("look-seeded.png", (1200, 800))
#: (name, size, fill, Pillow format) of each file Mat brings in from ROOT/drop.
DROP_IMAGES = (
    ("red.png", (640, 400), (200, 40, 40), "PNG"),
    ("green.png", (400, 640), (40, 160, 72), "PNG"),
    ("blue.jpg", (800, 450), (40, 80, 200), "JPEG"),
)
NOTES = ("notes.txt", "Session 61 look: this file is not an image, so the toast names it.\n")


def _image(path: Path, size: tuple[int, int], fill: tuple[int, int, int], fmt: str, title: str) -> None:
    from PIL import Image, ImageDraw

    width, height = size
    image = Image.new("RGB", size, (236, 240, 244))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height // 8), fill=fill)
    draw.text((20, height // 32), title, fill=(255, 255, 255))
    step = max(40, width // 12)
    for left in range(0, width, step):
        draw.line((left, height // 8, left, height), fill=(200, 208, 216))
    for top in range(height // 8, height, step):
        draw.line((0, top, width, top), fill=(200, 208, 216))
    draw.rectangle((width // 4, height // 3, 3 * width // 4, 2 * height // 3), fill=fill)
    image.save(path, format=fmt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default="C:/Temp/av-kit/s61/look")
    args = parser.parse_args()
    root = Path(args.root)
    if root.exists() and any(root.iterdir()):
        print(f"look-seed: {root} already holds files; the look needs a fresh root (not deleted here)")
        return 1
    app_data, inbox, drop = root / "app-data", root / "inbox", root / "drop"
    app_data.mkdir(parents=True)
    inbox.mkdir()
    drop.mkdir()
    _image(inbox / SEEDED[0], SEEDED[1], (32, 64, 96), "PNG", f"Session 61 look: {SEEDED[0]}")
    for name, size, fill, fmt in DROP_IMAGES:
        _image(drop / name, size, fill, fmt, f"Session 61 look: {name}")
    (drop / NOTES[0]).write_text(NOTES[1], encoding="utf-8")

    from fastapi.testclient import TestClient

    from avkit_api.main import create_app
    from avkit_api.wiring import build_services

    services, dispose = build_services(app_data=app_data)
    try:
        app = create_app(tokens=frozenset({GUI_TOKEN}), services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            if put.status_code != 200:
                print(f"look-seed: settings PUT {put.status_code} {put.text}")
                return 1
            items = client.get(PREFIX, headers=AUTH).json()["items"]
            by_name = {Path(item["original_path"]).name: item for item in items}
            if SEEDED[0] not in by_name or len(items) != 1:
                print(f"look-seed: expected only {SEEDED[0]} listed, got {sorted(by_name)}")
                return 1
            seeded = by_name[SEEDED[0]]
            marks = {
                "annotations": [
                    {"type": "rect", "x": 100, "y": 160, "width": 360, "height": 220, "color": "#dc2626", "stroke_width": 4},
                    {"type": "text", "x": 120, "y": 440, "text": "Keep me selected", "color": "#111827", "font_size": 32},
                ]
            }
            ann = client.post(f"{PREFIX}/{seeded['id']}/annotate", headers=AUTH, json=marks)
            if ann.status_code != 200:
                print(f"look-seed: annotate {ann.status_code} {ann.text}")
                return 1
            print(f"shot {seeded['id']} {SEEDED[0]} {SEEDED[1][0]}x{SEEDED[1][1]}, marked: rect, text")
    finally:
        dispose()
    for name, size, _, fmt in DROP_IMAGES:
        print(f"drop {name} {size[0]}x{size[1]} {fmt}")
    print(f"drop {NOTES[0]} text")
    print(f"look-seed: app data {app_data}, inbox {inbox}, drop {drop}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
