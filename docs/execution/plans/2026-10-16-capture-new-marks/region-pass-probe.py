"""Session 39 planning receipt R-1 (implementation-plan.md §Planning receipts).

Usage: ``python region-pass-probe.py`` with any Python that has Pillow (planning used
``P:/av-kit/.venv``, Pillow 12.3.0). Read-only: it writes nothing and prints its verdicts.
Exit 0 when every check holds.

It transcribes the plan's ``REGION_RECT``, ``PIXELATE_QUANT``, ``PIXELATE_BAKE`` and
``ERASER_SAMPLE`` literally, in two forms:

* a pure-Python reference over a flat RGBA list (the form ``capture-region-pass.ts`` takes);
* the Pillow form the adapter will use (per-band ``Image.reduce`` on the clipped box, NEAREST
  upscale by the block size, crop).

Checks:

1. ``reduce-bands``: per-band ``reduce`` equals ``PIXELATE_QUANT`` exactly (diff 0) on every
   channel, partial edge blocks included, over random cases; and ``PIXELATE_QUANT`` stays
   within ``REGION_TOLERANCE`` (1) of the exact round-half-up mean (the goal's bound).
2. ``reduce-rgba``: ``reduce`` straight on an RGBA image is *not* within the tolerance (its
   colour channels are alpha-weighted), which is why ``PIXELATE_BAKE`` splits the bands first.
3. ``bake-vs-reference``: the Pillow form and the reference are byte-identical for clipped,
   partial and oversized blocks, and the Pillow form writes nothing outside the clipped
   rectangle.
4. ``eraser``: the ring mode ignores text crossing the border, breaks a tie by the smallest
   packed RGB, clips the ring at the image edge, falls back to the inner edge ring when the
   rectangle covers the image, and the Pillow form equals the reference exactly.
5. ``order``: an eraser after an overlapping pixelate samples the pixelated ring, so list
   order inside the region pass changes the result.
6. ``composed``: whole region passes (pixelate then an eraser whose ring is pixelated, over
   colours placed on rounding boundaries; repeated overlapping pixelates) are byte-identical
   between the Pillow form and the reference, so unit parity of a composed pass is exact.
"""

from __future__ import annotations

import random
import sys
from collections import Counter

import PIL
from PIL import Image

REGION_TOLERANCE = 1


def quant(total: int, n: int) -> int:
    """PIXELATE_QUANT: Pillow's integer reduce for one band of one (possibly partial) block."""
    if EXACT_MEAN:  # sensitivity control only (check_composed)
        return (2 * total + n) // (2 * n)
    return ((total + n // 2) * ((1 << 24) // n)) >> 24


EXACT_MEAN = False


# ---------------------------------------------------------------- reference (flat RGBA list)
def clip(mark: dict, w: int, h: int) -> tuple[int, int, int, int] | None:
    x0, y0 = max(0, mark["x"]), max(0, mark["y"])
    x1, y1 = min(w, mark["x"] + mark["width"]), min(h, mark["y"] + mark["height"])
    return (x0, y0, x1, y1) if x0 < x1 and y0 < y1 else None


def ref_pixelate(px: list[int], w: int, h: int, mark: dict) -> list[int]:
    out = list(px)
    box = clip(mark, w, h)
    if box is None:
        return out
    x0, y0, x1, y1 = box
    b = mark["block_size"]
    for by in range(y0, y1, b):
        for bx in range(x0, x1, b):
            xs, ys = range(bx, min(bx + b, x1)), range(by, min(by + b, y1))
            n = len(xs) * len(ys)
            for c in range(4):
                s = sum(px[(y * w + x) * 4 + c] for y in ys for x in xs)
                mean = quant(s, n)
                for y in ys:
                    for x in xs:
                        out[(y * w + x) * 4 + c] = mean
    return out


def ring(box: tuple[int, int, int, int], w: int, h: int) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    pts = [(x, y) for x in range(x0 - 1, x1 + 1) for y in (y0 - 1, y1)]
    pts += [(x, y) for y in range(y0, y1) for x in (x0 - 1, x1)]
    return [(x, y) for x, y in pts if 0 <= x < w and 0 <= y < h]


def inner_ring(box: tuple[int, int, int, int]) -> list[tuple[int, int]]:
    x0, y0, x1, y1 = box
    return [(x, y) for y in range(y0, y1) for x in range(x0, x1) if x in (x0, x1 - 1) or y in (y0, y1 - 1)]


def ref_eraser_colour(px: list[int], w: int, h: int, mark: dict) -> tuple[int, int, int] | None:
    box = clip(mark, w, h)
    if box is None:
        return None
    pts = ring(box, w, h) or inner_ring(box)
    counts = Counter(tuple(px[(y * w + x) * 4 : (y * w + x) * 4 + 3]) for x, y in pts)
    top = max(counts.values())
    return min((c for c, k in counts.items() if k == top), key=lambda c: (c[0] << 16) | (c[1] << 8) | c[2])


def ref_eraser(px: list[int], w: int, h: int, mark: dict) -> list[int]:
    out = list(px)
    colour = ref_eraser_colour(px, w, h, mark)
    box = clip(mark, w, h)
    if colour is None or box is None:
        return out
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            out[(y * w + x) * 4 : (y * w + x) * 4 + 4] = [*colour, 255]
    return out


def ref_pass(px: list[int], w: int, h: int, marks: list[dict]) -> list[int]:
    for mark in marks:
        px = ref_pixelate(px, w, h, mark) if mark["type"] == "pixelate" else ref_eraser(px, w, h, mark)
    return px


# ---------------------------------------------------------------- Pillow form (the adapter)
def pil_pixelate(canvas: Image.Image, mark: dict) -> None:
    box = clip(mark, *canvas.size)
    if box is None:
        return
    b = mark["block_size"]
    region = canvas.crop(box)
    small = Image.merge(region.mode, [band.reduce(b) for band in region.split()])
    big = small.resize((small.width * b, small.height * b), Image.Resampling.NEAREST)
    canvas.paste(big.crop((0, 0, region.width, region.height)), box[:2])


def pil_eraser(canvas: Image.Image, mark: dict) -> None:
    box = clip(mark, *canvas.size)
    if box is None:
        return
    w, h = canvas.size
    pts = ring(box, w, h) or inner_ring(box)
    load = canvas.load()
    counts = Counter(load[x, y][:3] for x, y in pts)
    top = max(counts.values())
    colour = min((c for c, k in counts.items() if k == top), key=lambda c: (c[0] << 16) | (c[1] << 8) | c[2])
    canvas.paste((*colour, 255), box)


def pil_pass(canvas: Image.Image, marks: list[dict]) -> Image.Image:
    canvas = canvas.copy()
    for mark in marks:
        (pil_pixelate if mark["type"] == "pixelate" else pil_eraser)(canvas, mark)
    return canvas


def flat(image: Image.Image) -> list[int]:
    return list(image.convert("RGBA").tobytes())


# ---------------------------------------------------------------- checks
def exact_mean_diff(src: list[int], got: list[int], w: int, h: int, b: int) -> int:
    worst = 0
    for by in range(0, h, b):
        for bx in range(0, w, b):
            xs, ys = range(bx, min(bx + b, w)), range(by, min(by + b, h))
            n = len(xs) * len(ys)
            for c in range(4):
                s = sum(src[(y * w + x) * 4 + c] for y in ys for x in xs)
                worst = max(worst, abs(got[(by * w + bx) * 4 + c] - (2 * s + n) // (2 * n)))
    return worst


def check_reduce(rng: random.Random) -> list[str]:
    bands_max = rgba_max = goal_max = 0
    partial_seen = 0
    for _ in range(400):
        w, h, b = rng.randint(1, 37), rng.randint(1, 37), rng.randint(2, 15)
        im = Image.frombytes("RGBA", (w, h), bytes(rng.randrange(256) for _ in range(w * h * 4)))
        exp = ref_pixelate(flat(im), w, h, {"x": 0, "y": 0, "width": w, "height": h, "block_size": b})
        got = flat(Image.merge("RGBA", [band.reduce(b) for band in im.split()]).resize(
            (-(-w // b) * b, -(-h // b) * b), Image.Resampling.NEAREST).crop((0, 0, w, h)))
        bands_max = max(bands_max, max(abs(a - c) for a, c in zip(got, exp)))
        goal_max = max(goal_max, exact_mean_diff(flat(im), exp, w, h, b))
        partial_seen += (w % b != 0) or (h % b != 0)
        direct = flat(im.reduce(b).resize((-(-w // b) * b, -(-h // b) * b), Image.Resampling.NEAREST).crop((0, 0, w, h)))
        rgb_only = [i for i in range(len(exp)) if i % 4 != 3]
        rgba_max = max(rgba_max, max(abs(direct[i] - exp[i]) for i in rgb_only))
    print(f"reduce-bands: 400 cases ({partial_seen} with partial edge blocks), max channel diff vs PIXELATE_QUANT {bands_max}")
    print(f"reduce-bands: PIXELATE_QUANT vs the exact round-half-up mean, max channel diff {goal_max}")
    print(f"reduce-rgba: direct RGBA reduce, max colour-channel diff {rgba_max}")
    problems = []
    if bands_max:
        problems.append(f"per-band reduce differs from PIXELATE_QUANT by {bands_max}")
    if goal_max > REGION_TOLERANCE:
        problems.append(f"PIXELATE_QUANT is {goal_max} from the exact mean, beyond the tolerance")
    if rgba_max <= REGION_TOLERANCE:
        problems.append("direct RGBA reduce unexpectedly within tolerance; the band split is not needed")
    return problems


def check_bake_vs_reference(rng: random.Random) -> list[str]:
    problems, worst, outside = [], 0, 0
    w, h = 40, 30
    im = Image.frombytes("RGBA", (w, h), bytes(v for _ in range(w * h) for v in (*(rng.randrange(256) for _ in range(3)), 255)))
    cases = [
        {"type": "pixelate", "x": 3, "y": 2, "width": 13, "height": 9, "block_size": 4},
        {"type": "pixelate", "x": -5, "y": 25, "width": 20, "height": 20, "block_size": 3},
        {"type": "pixelate", "x": 30, "y": 0, "width": 25, "height": 7, "block_size": 100},
        {"type": "pixelate", "x": 50, "y": 50, "width": 5, "height": 5, "block_size": 10},
        {"type": "pixelate", "x": 4, "y": 4, "width": 0, "height": 9, "block_size": 2},
    ]
    for mark in cases:
        exp = ref_pass(flat(im), w, h, [mark])
        got = flat(pil_pass(im, [mark]))
        worst = max(worst, max(abs(a - c) for a, c in zip(got, exp)))
        box = clip(mark, w, h)
        base = flat(im)
        for i in range(0, len(got), 4):
            x, y = (i // 4) % w, (i // 4) // w
            inside = box is not None and box[0] <= x < box[2] and box[1] <= y < box[3]
            if not inside and got[i : i + 4] != base[i : i + 4]:
                outside += 1
    print(f"bake-vs-reference: {len(cases)} pixelate cases, max channel diff {worst}, pixels changed outside the clipped rect {outside}")
    if worst:
        problems.append(f"Pillow pixelate differs from the reference by {worst}")
    if outside:
        problems.append(f"Pillow pixelate wrote {outside} pixels outside the clipped rectangle")
    return problems


def check_eraser() -> list[str]:
    problems: list[str] = []
    w, h = 20, 14
    bg, ink = (240, 240, 240), (20, 20, 20)
    im = Image.new("RGBA", (w, h), (*bg, 255))
    for x in (7, 9):  # two glyph stems crossing the top and bottom border of the mark
        for y in range(2, 11):
            im.putpixel((x, y), (*ink, 255))
    mark = {"type": "eraser", "x": 6, "y": 4, "width": 5, "height": 5}
    colour = ref_eraser_colour(flat(im), w, h, mark)
    print(f"eraser: text-crossing ring -> {colour}")
    if colour != bg:
        problems.append(f"ring mode picked {colour}, not the background {bg}")
    tie = Image.new("RGBA", (4, 4), (0, 0, 0, 255))
    for x, y in ring((1, 1, 3, 3), 4, 4)[::2]:
        tie.putpixel((x, y), (9, 9, 9, 255))
    tie_colour = ref_eraser_colour(flat(tie), 4, 4, {"x": 1, "y": 1, "width": 2, "height": 2})
    print(f"eraser: 6/6 tie between (0,0,0) and (9,9,9) -> {tie_colour}")
    if tie_colour != (0, 0, 0):
        problems.append(f"tie broke to {tie_colour}")
    edge = ring(clip({"x": -3, "y": 2, "width": 6, "height": 3}, w, h) or (0, 0, 0, 0), w, h)
    print(f"eraser: ring of a rect clipped at the left edge has {len(edge)} pixels, min x {min(x for x, _ in edge)}")
    if min(x for x, _ in edge) < 0:
        problems.append("ring not clipped to the image")
    full = Image.new("RGBA", (6, 5), (1, 2, 3, 255))
    full.putpixel((0, 0), (200, 0, 0, 255))
    full_colour = ref_eraser_colour(flat(full), 6, 5, {"x": -2, "y": -2, "width": 20, "height": 20})
    print(f"eraser: rect covering the image -> inner ring, colour {full_colour}")
    if full_colour != (1, 2, 3):
        problems.append(f"inner-ring fallback gave {full_colour}")
    for case in (mark, {"type": "eraser", "x": -3, "y": 2, "width": 6, "height": 3}, {"type": "eraser", "x": -2, "y": -2, "width": 30, "height": 30}):
        if flat(pil_pass(im, [case])) != ref_pass(flat(im), w, h, [case]):
            problems.append(f"Pillow eraser differs from the reference for {case}")
    print(f"eraser: Pillow form equals the reference exactly on 3 cases: {not any('Pillow eraser' in p for p in problems)}")
    return problems


def check_order(rng: random.Random) -> list[str]:
    w, h = 24, 18
    im = Image.frombytes("RGBA", (w, h), bytes(v for _ in range(w * h) for v in (*(rng.randrange(256) for _ in range(3)), 255)))
    pix = {"type": "pixelate", "x": 0, "y": 0, "width": 24, "height": 18, "block_size": 6}
    era = {"type": "eraser", "x": 7, "y": 7, "width": 4, "height": 4}
    a, b = flat(pil_pass(im, [pix, era])), flat(pil_pass(im, [era, pix]))
    print(f"order: pixelate-then-eraser differs from eraser-then-pixelate: {a != b}")
    return [] if a != b else ["list order had no effect; the order contract would be untestable"]


def check_composed(rng: random.Random) -> list[str]:
    w, h = 32, 24
    # Neighbouring colours one step apart on every band, so 2x2 / 3x3 block sums land on .5,
    # .25 and .75: the cases where an exact mean and PIXELATE_QUANT could round apart, and an
    # eraser ring sampled from pixelated blocks would then pick a different colour.
    pairs = [((10, 101, 200), (11, 102, 201)), ((0, 255, 7), (1, 254, 8)), ((127, 128, 3), (128, 127, 4))]
    im = Image.new("RGBA", (w, h))
    for y in range(h):
        for x in range(w):
            a, b = pairs[((x // 2) + (y // 2)) % len(pairs)]
            im.putpixel((x, y), (*(a if (x + y) % 4 == 0 else b), 255))
    noise = Image.frombytes("RGBA", (w, h), bytes(v for _ in range(w * h) for v in (*(rng.randrange(256) for _ in range(3)), 255)))
    passes = [
        [{"type": "pixelate", "x": 0, "y": 0, "width": 32, "height": 24, "block_size": 2},
         {"type": "eraser", "x": 9, "y": 7, "width": 6, "height": 5}],
        [{"type": "pixelate", "x": 3, "y": 1, "width": 20, "height": 15, "block_size": 3},
         {"type": "eraser", "x": 10, "y": 5, "width": 5, "height": 4}],
        [{"type": "pixelate", "x": 2, "y": 2, "width": 17, "height": 13, "block_size": 4},
         {"type": "pixelate", "x": 7, "y": 5, "width": 19, "height": 16, "block_size": 3},
         {"type": "pixelate", "x": 0, "y": 0, "width": 32, "height": 24, "block_size": 5}],
        [{"type": "pixelate", "x": -4, "y": 6, "width": 15, "height": 30, "block_size": 7},
         {"type": "eraser", "x": 1, "y": 9, "width": 4, "height": 4},
         {"type": "pixelate", "x": 0, "y": 0, "width": 9, "height": 24, "block_size": 2}],
    ]
    diffs = 0
    for base in (im, noise):
        for marks in passes:
            diffs += flat(pil_pass(base, marks)) != ref_pass(flat(base), w, h, marks)
    global EXACT_MEAN
    EXACT_MEAN = True
    try:
        drift = sum(flat(pil_pass(base, marks)) != ref_pass(flat(base), w, h, marks) for base in (im, noise) for marks in passes)
    finally:
        EXACT_MEAN = False
    print(f"composed: {2 * len(passes)} whole passes (rounding-boundary and noise images), Pillow form != reference in {diffs}")
    print(f"composed: sensitivity control, an exact-mean reference differs from the Pillow form in {drift} pass(es)")
    problems = [f"{diffs} composed pass(es) not byte-identical"] if diffs else []
    if not drift:
        problems.append("the composed cases cannot tell PIXELATE_QUANT from the exact mean; they prove nothing")
    return problems


def main() -> int:
    print("pillow", PIL.__version__)
    rng = random.Random(39)
    problems = check_reduce(rng) + check_bake_vs_reference(rng) + check_eraser() + check_order(rng) + check_composed(rng)
    for p in problems:
        print("PROBE FAIL:", p)
    print(f"region-pass-probe: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
