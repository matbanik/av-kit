"""Session 60 look seed (task row 6, under D-522 A; implementation-plan.md LOOK_LAUNCH).

Builds the app data the dev app opens for Mat's look, on the real stack and without the
network: `build_services` and `create_app` on ROOT/app-data, a `TestClient`, a
`PUT /api/v1/settings/capture` that points the inbox at ROOT/inbox, two Pillow images in that
inbox, `GET /captures` to register them, and `POST /captures/{id}/annotate` with a rect, an
arrow and a text on the landscape shot, so the look has a marked shot to crop.

ROOT is C:/Temp/av-kit/s60/look unless `--root` says otherwise. The seed refuses a ROOT that
already holds files, so a look never opens on an earlier run's state; nothing is deleted here.
It prints each shot's id, name and size. No image leaves the machine.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

GUI_TOKEN = "look-seed-token"
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"
LANDSCAPE = ("look-landscape.png", (1600, 900))
PORTRAIT = ("look-portrait.png", (600, 1000))


def _image(path: Path, size: tuple[int, int], title: str) -> None:
    from PIL import Image, ImageDraw

    width, height = size
    image = Image.new("RGB", size, (236, 240, 244))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height // 9), fill=(32, 64, 96))
    draw.text((24, height // 36), title, fill=(255, 255, 255))
    step = max(40, width // 16)
    for left in range(0, width, step):
        draw.line((left, height // 9, left, height), fill=(200, 208, 216))
    for top in range(height // 9, height, step):
        draw.line((0, top, width, top), fill=(200, 208, 216))
    panel = (width // 2 + 40, height // 9 + 40, width - 40, height // 2)
    draw.rectangle(panel, fill=(14, 116, 144))
    draw.text((panel[0] + 16, panel[1] + 16), "Panel", fill=(255, 255, 255))
    image.save(path, format="PNG")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default="C:/Temp/av-kit/s60/look")
    args = parser.parse_args()
    root = Path(args.root)
    if root.exists() and any(root.iterdir()):
        print(f"look-seed: {root} already holds files; the look needs a fresh root (not deleted here)")
        return 1
    app_data, inbox = root / "app-data", root / "inbox"
    app_data.mkdir(parents=True)
    inbox.mkdir()
    for name, size in (LANDSCAPE, PORTRAIT):
        _image(inbox / name, size, f"Session 60 look: {name}")

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
            missing = [name for name, _ in (LANDSCAPE, PORTRAIT) if name not in by_name]
            if missing:
                print(f"look-seed: not listed {missing}")
                return 1
            landscape = by_name[LANDSCAPE[0]]
            marks = {
                "annotations": [
                    {"type": "rect", "x": 120, "y": 200, "width": 420, "height": 260, "color": "#dc2626", "stroke_width": 4},
                    {"type": "arrow", "from": [700, 700], "to": [900, 480], "color": "#dc2626", "stroke_width": 4},
                    {"type": "text", "x": 140, "y": 520, "text": "Crop me", "color": "#111827", "font_size": 32},
                ]
            }
            ann = client.post(f"{PREFIX}/{landscape['id']}/annotate", headers=AUTH, json=marks)
            if ann.status_code != 200:
                print(f"look-seed: annotate {ann.status_code} {ann.text}")
                return 1
            for name, size in (LANDSCAPE, PORTRAIT):
                print(f"shot {by_name[name]['id']} {name} {size[0]}x{size[1]}")
            print(f"marked {landscape['id']}: rect, arrow, text")
    finally:
        dispose()
    print(f"look-seed: app data {app_data}, inbox {inbox}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
