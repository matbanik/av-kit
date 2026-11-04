"""Session 37 planning receipt R-2 (implementation-plan.md ``CONTRAST_TEXT``).

Computes the WCAG 2.1 relative luminance and contrast ratio for every ``NAMED_COLOR_HEX`` entry
against black and white text, applies the ``CONTRAST_TEXT`` rule (black when its ratio is at
least white's, else white), and checks that every pick reaches 4.5:1 (WCAG 1.4.3 AA, normal
text). The table is the expected output of AC-86.1. Exit 1 if any pick is below 4.5.
"""

from __future__ import annotations

import sys

#: Copied from ui/src/renderer/src/features/capture/capture-color.ts NAMED_COLOR_HEX (90bb409).
NAMED_COLOR_HEX = {
    "red": "#FF0000",
    "orange": "#FFA500",
    "yellow": "#FFFF00",
    "green": "#008000",
    "blue": "#0000FF",
    "white": "#FFFFFF",
    "black": "#000000",
}


def _channel(c8: int) -> float:
    c = c8 / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_: str) -> float:
    r, g, b = (int(hex_[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _channel(r) + 0.7152 * _channel(g) + 0.0722 * _channel(b)


def ratio(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def contrast_text(hex_: str) -> str:
    lum = luminance(hex_)
    return "#000000" if ratio(lum, 0.0) >= ratio(lum, 1.0) else "#FFFFFF"


def main() -> int:
    low = []
    for name, hex_ in NAMED_COLOR_HEX.items():
        lum = luminance(hex_)
        pick = contrast_text(hex_)
        r_black, r_white = ratio(lum, 0.0), ratio(lum, 1.0)
        chosen = r_black if pick == "#000000" else r_white
        print(f"{name:7} {hex_} L={lum:.4f} black={r_black:.2f} white={r_white:.2f} pick={pick} ratio={chosen:.2f}")
        if chosen < 4.5:
            low.append(name)
    # The decision boundary: luminance where the two ratios are equal, sqrt(1.05*0.05)-0.05.
    print(f"boundary L={(1.05 * 0.05) ** 0.5 - 0.05:.4f}")
    print(f"contrast-probe: {len(NAMED_COLOR_HEX)} colours, below 4.5: {low}")
    return 1 if low else 0


if __name__ == "__main__":
    raise SystemExit(main())
