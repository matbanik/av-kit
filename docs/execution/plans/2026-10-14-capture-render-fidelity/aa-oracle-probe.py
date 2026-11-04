"""Session 36 planning receipt R-3: calibrate the MEU-83 arrow oracles (review F1).

Transcribes the plan's ``BAKE_AA`` literally on Pillow and measures three variants:

* ``positive``  -- BAKE_AA with the shaft ending at ``SHAFT_END`` (what row 5 builds);
* ``full_aa``   -- BAKE_AA with the shaft running to the tip (negative: AA but no fix);
* ``baseline``  -- the current adapter drawing (no AA, full shaft, head 4 / 0.40).

Coordinate convention: Pillow puts an integer coordinate on a pixel *centre*, so the pixel
at index ``(x, y)`` is sampled at mark coordinate ``(x, y)``, not ``(x + .5, y + .5)``.
The probe prints every metric the oracles use so the thresholds in the plan are read off
this output rather than guessed. Planning-only; it does not import or test product code.

Usage: ``python aa-oracle-probe.py [--pad N]``. Exit 0 when the chosen oracles pass on
``positive`` and fail on both negatives; exit 1 otherwise.
"""

from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw

SUPERSAMPLE = 4
NEW = (5.0, 0.45, 10.0)  # ARROW_HEAD: factor, angle, min
OLD = (4.0, 0.40, 10.0)  # baseline adapter constants
OVERLAP = 1.0

# The thresholds the plan freezes (ARROW_TIP_ORACLE, EDGE_ORACLE, AC-83.7).
HALO_PX = 3.0  # LANCZOS support at a 4x downscale: 3 output px
WHITE_TOL = 8  # per-channel tolerance for "equals white" / "equals the mark"
LEAK_PX = 1.0  # a leak pixel is one this far outside the head, beyond the base
LEAK_COVERAGE = 0.5  # ... with at least this coverage
INTERIOR_PX = 1.5  # interior = this far inside the shaft edge
BLEND_MIN = 0.40


def head_geometry(frm, to, stroke, consts):
    factor, angle, minimum = consts
    theta = math.atan2(to[1] - frm[1], to[0] - frm[0])
    head = max(minimum, factor * stroke)
    left = (to[0] - head * math.cos(theta - angle), to[1] - head * math.sin(theta - angle))
    right = (to[0] - head * math.cos(theta + angle), to[1] - head * math.sin(theta + angle))
    return head, (float(to[0]), float(to[1])), left, right


def shaft_end(frm, to, stroke, consts):
    head, *_ = head_geometry(frm, to, stroke, consts)
    length = math.hypot(to[0] - frm[0], to[1] - frm[1])
    back = head * math.cos(consts[1]) - OVERLAP
    if length <= back:
        return None
    ux, uy = (to[0] - frm[0]) / length, (to[1] - frm[1]) / length
    return (to[0] - ux * back, to[1] - uy * back)


def bake_aa(img, frm, to, stroke, color, *, full_shaft, pad_extra):
    """Literal BAKE_AA steps (1)-(5)."""
    _, tip, left, right = head_geometry(frm, to, stroke, NEW)
    end = (float(to[0]), float(to[1])) if full_shaft else shaft_end(frm, to, stroke, NEW)
    pts = [tuple(map(float, frm)), tip, left, right] + ([end] if end else [])
    pad = stroke / 2 + pad_extra
    w, h = img.size
    x0 = max(0, math.floor(min(p[0] for p in pts) - pad))
    y0 = max(0, math.floor(min(p[1] for p in pts) - pad))
    x1 = min(w, math.ceil(max(p[0] for p in pts) + pad) + 1)
    y1 = min(h, math.ceil(max(p[1] for p in pts) + pad) + 1)
    if x1 <= x0 or y1 <= y0:
        return img, (x0, y0, x0, y0)
    tw, th = x1 - x0, y1 - y0
    mask = Image.new("L", (tw * SUPERSAMPLE, th * SUPERSAMPLE), 0)
    d = ImageDraw.Draw(mask)

    def big(p):
        return (SUPERSAMPLE * (p[0] - x0) + 1.5, SUPERSAMPLE * (p[1] - y0) + 1.5)

    if end:
        d.line([big(frm), big(end)], fill=255, width=SUPERSAMPLE * max(1, stroke))
    d.polygon([big(tip), big(left), big(right)], fill=255)
    mask = mask.resize((tw, th), Image.Resampling.LANCZOS)
    out = img.copy()
    tile = out.crop((x0, y0, x1, y1))
    tile = Image.composite(Image.new("RGB", (tw, th), color), tile, mask)
    out.paste(tile, (x0, y0))
    return out, (x0, y0, x1, y1)


def bake_baseline(img, frm, to, stroke, color):
    out = img.copy()
    d = ImageDraw.Draw(out)
    d.line([frm, to], fill=color, width=max(1, stroke))
    _, tip, left, right = head_geometry(frm, to, stroke, OLD)
    d.polygon([tip, left, right], fill=color)
    return out


def outside_triangle(p, tri):
    """Distance outside the triangle (0 inside): max signed distance to its edges."""
    worst = -math.inf
    cx = sum(v[0] for v in tri) / 3
    cy = sum(v[1] for v in tri) / 3
    for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
        nx, ny = b[1] - a[1], a[0] - b[0]
        n = math.hypot(nx, ny)
        nx, ny = nx / n, ny / n
        if (cx - a[0]) * nx + (cy - a[1]) * ny > 0:
            nx, ny = -nx, -ny
        worst = max(worst, (p[0] - a[0]) * nx + (p[1] - a[1]) * ny)
    return max(0.0, worst)


def coverage(px, color):
    """Fraction of the mark colour at a pixel composited on white."""
    ch = [i for i in range(3) if color[i] == 0]
    return max((255 - px[i]) / 255 for i in ch)


def tip_metrics(img):
    frm, to, stroke, color = (20, 60), (200, 60), 12, (255, 0, 0)
    head, tip, left, right = head_geometry(frm, to, stroke, NEW)
    base_x = to[0] - head * math.cos(NEW[1])
    tri = (tip, left, right)
    halo_dev, leaks = 0, 0
    for y in range(img.height):
        for x in range(math.floor(base_x) + 1, img.width):
            if x <= base_x:
                continue
            out = outside_triangle((x, y), tri)
            px = img.getpixel((x, y))
            if out > HALO_PX:
                halo_dev = max(halo_dev, max(255 - c for c in px))
            if out > LEAK_PX and coverage(px, color) >= LEAK_COVERAGE:
                leaks += 1
    return {"halo_max_dev": halo_dev, "leak_pixels": leaks}


def edge_metrics(img, original, tile):
    frm, to, stroke, color = (20, 100), (200, 20), 6, (0, 0, 255)
    length = math.hypot(to[0] - frm[0], to[1] - frm[1])
    ux, uy = (to[0] - frm[0]) / length, (to[1] - frm[1]) / length
    head, *_ = head_geometry(frm, to, stroke, NEW)
    half = stroke / 2
    edge, blends, interior_dev = 0, 0, 0
    for y in range(img.height):
        for x in range(img.width):
            rx, ry = x - frm[0], y - frm[1]
            t = rx * ux + ry * uy
            if not (half + 3 <= t <= length - head - 3):
                continue
            dist = abs(rx * uy - ry * ux)
            px = img.getpixel((x, y))
            if abs(dist - half) <= 1:
                edge += 1
                white = all(c >= 255 - WHITE_TOL for c in px)
                mark = all(abs(c - m) <= WHITE_TOL for c, m in zip(px, color, strict=True))
                blends += not white and not mark
            if dist <= half - INTERIOR_PX:
                interior_dev = max(
                    interior_dev, max(abs(c - m) for c, m in zip(px, color, strict=True))
                )
    x0, y0, x1, y1 = tile
    outside_changed = sum(
        1
        for y in range(img.height)
        for x in range(img.width)
        if not (x0 <= x < x1 and y0 <= y < y1) and img.getpixel((x, y)) != original.getpixel((x, y))
    )
    return {
        "edge_pixels": edge,
        "blend_fraction": round(blends / edge, 4) if edge else 0.0,
        "interior_max_dev": interior_dev,
        "outside_tile_changed": outside_changed,
    }


def clip_metrics(pad_extra):
    frm, to, stroke, color = (20, 60), (119, 60), 3, (255, 0, 0)
    img = Image.new("RGB", (120, 120), "white")
    out, tile = bake_aa(img, frm, to, stroke, color, full_shaft=False, pad_extra=pad_extra)
    axis = {d: round(coverage(out.getpixel((119 - d, 60)), color), 3) for d in range(0, 9)}
    head = max(NEW[2], NEW[0] * stroke)
    probe_d = round(head / 2)
    probe = out.getpixel((119 - probe_d, 60))
    probe_ok = all(abs(c - m) <= WHITE_TOL for c, m in zip(probe, color, strict=True))
    far = Image.new("RGB", (120, 120), "white")
    far_out, far_tile = bake_aa(
        far, (300, 300), (400, 300), stroke, color, full_shaft=False, pad_extra=pad_extra
    )
    return {
        "tile": tile,
        "axis_coverage_by_d": axis,
        "probe_d": probe_d,
        "probe_pixel": probe,
        "probe_is_mark": probe_ok,
        "outside_image_tile": far_tile,
        "outside_image_unchanged": far_out.tobytes() == far.tobytes(),
    }


def main(argv):
    pad_extra = 4.0
    if "--pad" in argv:
        pad_extra = float(argv[argv.index("--pad") + 1])
    base = Image.new("RGB", (240, 120), "white")
    results = {}
    for name in ("positive", "full_aa", "baseline"):
        if name == "baseline":
            tip_img = bake_baseline(base, (20, 60), (200, 60), 12, (255, 0, 0))
            edge_img = bake_baseline(base, (20, 100), (200, 20), 6, (0, 0, 255))
            tile = (0, 0, 240, 120)
        else:
            full = name == "full_aa"
            tip_img, _ = bake_aa(
                base, (20, 60), (200, 60), 12, (255, 0, 0), full_shaft=full, pad_extra=pad_extra
            )
            edge_img, tile = bake_aa(
                base, (20, 100), (200, 20), 6, (0, 0, 255), full_shaft=full, pad_extra=pad_extra
            )
        results[name] = {**tip_metrics(tip_img), **edge_metrics(edge_img, base, tile)}
        print(name, results[name])
    clip = clip_metrics(pad_extra)
    print("clipped", clip)

    def tip_ok(r):
        return r["leak_pixels"] == 0 and r["halo_max_dev"] <= WHITE_TOL

    def edge_ok(r):
        return (
            r["blend_fraction"] >= BLEND_MIN
            and r["interior_max_dev"] <= WHITE_TOL
            and r["outside_tile_changed"] == 0
        )

    verdict = {
        "positive_tip": tip_ok(results["positive"]),
        "positive_edge": edge_ok(results["positive"]),
        "full_aa_tip_refused": not tip_ok(results["full_aa"]),
        "baseline_tip_refused": not tip_ok(results["baseline"]),
        "baseline_edge_refused": not edge_ok(results["baseline"]),
        "clip_probe_is_mark": clip["probe_is_mark"],
        "outside_image_unchanged": clip["outside_image_unchanged"],
    }
    print("verdict", verdict, "pad_extra", pad_extra)
    return 0 if all(verdict.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
