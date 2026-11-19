"""Session 97 (task row 1; AC-161.1): the fidelity boxes the E2E specs logged, from both hosts.

    uv run --no-sync python <plan>/boxes-report.py REPORT [REPORT ...]

Each REPORT is a Playwright JSON report (the second host's `host/report.json` under the
`tools/e2e_remote.py` receipts, or a dev-PC `--reporter=json` run). For AC-82.6, AC-102.19 and
AC-102.20 it prints each result's status and the `boxes` line the spec logs (preview and bake ink
and plate, the device scale and the image's on-screen origin), then the plate gap per side
(left, top, right, bottom) and whether the spec's 1 px rule holds. It reads only the named files
and prints ASCII. Exit 0 when every named report was read, 1 when one is missing or unreadable.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

WANT = ("AC-82.6", "AC-102.19", "AC-102.20")
SIDES = ("left", "top", "right", "bottom")


def walk(suite: dict, out: list[tuple[str, str, str]]) -> None:
    for spec in suite.get("specs", []):
        words = str(spec.get("title", "")).split()
        head = words[0] if words else ""
        if head not in WANT:
            continue
        for test in spec.get("tests", []):
            for result in test.get("results", []):
                for chunk in result.get("stdout", []):
                    text = chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
                    if "boxes" in text:
                        out.append((head, str(result.get("status")), text.strip()))
    for child in suite.get("suites", []):
        walk(child, out)


def gap(text: str) -> str:
    try:
        boxes = json.loads(text.split("boxes", 1)[1])
        preview = boxes["preview"]["plate"]
        bake = boxes["bake"]["plate"]
        sides = [abs(int(preview[s]) - int(bake[s])) for s in SIDES]
    except (ValueError, KeyError, TypeError, IndexError):
        return "plate gap: unreadable"
    dpr = boxes["preview"].get("dpr", "?")
    rect = boxes["preview"].get("rect")
    return f"plate gap l,t,r,b {sides} dpr {dpr} origin {rect} 1px-rule {max(sides) <= 1}"


def main(argv: list[str]) -> int:
    bad = 0
    for arg in argv:
        path = Path(arg)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print("unreadable:", ascii(arg), type(exc).__name__)
            bad += 1
            continue
        rows: list[tuple[str, str, str]] = []
        for suite in data.get("suites", []):
            walk(suite, rows)
        print("report:", ascii(arg), "rows:", len(rows))
        for head, status, text in rows:
            print(" ", head, status, ascii(text)[1:-1][:1200])
            print("   ", gap(text))
    return 1 if bad or not argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
