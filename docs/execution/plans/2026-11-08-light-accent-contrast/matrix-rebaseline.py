"""Session 56 row 3: re-baseline AC-43.3's pinned contrast matrix for the light accent.

MATRIX_REBASELINE (implementation-plan.md §Single-statement contracts, D-456). AC-43.3
(ui/tests/unit/queue-primitives.test.ts:419-454) recomputes the queue pill contrast matrix from
styles.css and requires it to equal contrast-matrix.json. Two of its four backdrops are the accent
composited over the page (`checkbox-selected` is bg-accent/5, `detail-open` is bg-accent/10), so the
light accent change moves 40 pinned values: the label and the icon ratio of each of the 10 statuses
on those two backdrops, in the light theme only.

This script recomputes the matrix with AC-43.3's algorithm (WCAG 2.0 threshold 0.03928, composite
channels and the ratio rounded half-up, as JS Math.round). It refuses unless the values that move
are exactly EXPECTED_MOVES, every label is at 4.5 or more, `_meta` still describes the matrix, and
AC-43.3's three negative controls still move it. Then it replaces only those 40 numbers in place,
so every other byte, the CRLF endings and `_meta` stay as they are.

Modes (run from the repository root):
  --check-shipped   the replica, from the tokens in --css, equals the pinned matrix (row 0's control)
  (default)         re-baseline --matrix into --out (default: --matrix itself, which needs
                    --expect-sha256); the tokens in --css must be the ruled ones
  --selftest        the refusal cases and a CRLF round trip, on matrices built in memory
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CSS = ROOT / "ui/src/renderer/src/styles.css"
TOKENS_TS = ROOT / "ui/src/renderer/src/lib/queue/status-tokens.ts"
FOUNDATIONS = ROOT / "docs/execution/plans/2026-08-28-p10-queue-card-foundations"
MATRIX = FOUNDATIONS / "contrast-matrix.json"
SETS = json.loads((FOUNDATIONS / "named-sets.json").read_text(encoding="utf-8"))

DARK_OPENER = "@theme {"
LIGHT_OPENER = ":root:not(.dark) {"
SHIPPED = {"--color-accent": "#0891b2", "--color-accent-hover": "#0e7490"}
RULED = {"--color-accent": "#155e75", "--color-accent-hover": "#164e63"}
BACKDROP_NAME = {"default": "card"}
ROW_KEYS = ("theme", "status", "backdrop", "token")
CRLF = b"\r\n"

# (kind, status, backdrop, pinned, re-baselined): every value that moves, all light theme.
# implementation-plan.md §MATRIX_REBASELINE lists the same 40 (C:/Temp/av-kit/s56/matrix-probe.txt).
EXPECTED_MOVES = [
    ("label", "Pending", "checkbox-selected", 10.95, 10.74),
    ("label", "Pending", "detail-open", 10.4, 10.04),
    ("label", "Processing", "checkbox-selected", 11.04, 10.89),
    ("label", "Processing", "detail-open", 10.5, 10.14),
    ("label", "Downloading", "checkbox-selected", 11.04, 10.89),
    ("label", "Downloading", "detail-open", 10.5, 10.14),
    ("label", "Paused", "checkbox-selected", 11.13, 10.9),
    ("label", "Paused", "detail-open", 10.5, 10.21),
    ("label", "Done", "checkbox-selected", 11.07, 10.84),
    ("label", "Done", "detail-open", 10.53, 10.16),
    ("label", "Failed", "checkbox-selected", 10.81, 10.59),
    ("label", "Failed", "detail-open", 10.19, 9.91),
    ("label", "Skipped", "checkbox-selected", 10.94, 10.72),
    ("label", "Skipped", "detail-open", 10.32, 10.04),
    ("label", "Cancelled", "checkbox-selected", 11.46, 11.24),
    ("label", "Cancelled", "detail-open", 10.83, 10.53),
    ("label", "QualityBlocked", "checkbox-selected", 10.95, 10.74),
    ("label", "QualityBlocked", "detail-open", 10.4, 10.04),
    ("label", "AgeRestricted", "checkbox-selected", 10.81, 10.59),
    ("label", "AgeRestricted", "detail-open", 10.19, 9.91),
    ("icon", "Pending", "checkbox-selected", 6.39, 6.27),
    ("icon", "Pending", "detail-open", 6.04, 5.84),
    ("icon", "Processing", "checkbox-selected", 6.36, 6.24),
    ("icon", "Processing", "detail-open", 6.01, 5.81),
    ("icon", "Downloading", "checkbox-selected", 6.36, 6.24),
    ("icon", "Downloading", "detail-open", 6.01, 5.81),
    ("icon", "Paused", "checkbox-selected", 6.0, 5.88),
    ("icon", "Paused", "detail-open", 5.67, 5.48),
    ("icon", "Done", "checkbox-selected", 6.24, 6.12),
    ("icon", "Done", "detail-open", 5.9, 5.7),
    ("icon", "Failed", "checkbox-selected", 7.27, 7.13),
    ("icon", "Failed", "detail-open", 6.87, 6.64),
    ("icon", "Skipped", "checkbox-selected", 6.22, 6.1),
    ("icon", "Skipped", "detail-open", 5.88, 5.68),
    ("icon", "Cancelled", "checkbox-selected", 4.16, 4.08),
    ("icon", "Cancelled", "detail-open", 3.94, 3.8),
    ("icon", "QualityBlocked", "checkbox-selected", 6.39, 6.27),
    ("icon", "QualityBlocked", "detail-open", 6.04, 5.84),
    ("icon", "AgeRestricted", "checkbox-selected", 7.27, 7.13),
    ("icon", "AgeRestricted", "detail-open", 6.87, 6.64),
]


def theme_block(css: str, opener: str) -> dict[str, str]:
    """parseThemeBlock (queue-primitives.test.ts:202-216): the opener to the first `\\n}`."""
    start = css.index(opener)
    end = css.index("\n}", start)
    body = css[start + len(opener) : end]
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body)}


def to_rgb(tokens: dict[str, str], token: str) -> tuple[int, int, int]:
    value = tokens[token]
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError(f"token {token} is not a plain 6-digit hex: {value}")
    n = int(value[1:], 16)
    return ((n >> 16) & 255, (n >> 8) & 255, n & 255)


def over(fg, alpha: float, bg) -> tuple[int, int, int]:
    return tuple(math.floor(f * alpha + b * (1 - alpha) + 0.5) for f, b in zip(fg, bg))


def luminance(rgb) -> float:
    def channel(raw: int) -> float:
        c = raw / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2])


def ratio(a, b) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return math.floor((hi + 0.05) / (lo + 0.05) * 100 + 0.5) / 100


def backdrop(tokens: dict[str, str], expr: str):
    composed = re.fullmatch(r"(--[\w-]+)\s*@\s*([\d.]+)\s*over\s*(--[\w-]+)", expr.strip())
    if composed:
        return over(to_rgb(tokens, composed.group(1)), float(composed.group(2)), to_rgb(tokens, composed.group(3)))
    return to_rgb(tokens, expr.strip())


def status_table() -> list[tuple[str, str, float]]:
    """STATUS_PILL_TOKENS in source order: the status, its token and fillAlpha."""
    text = TOKENS_TS.read_text(encoding="utf-8")
    table = [(s, t, float(a)) for s, t, a in re.findall(r"(\w+): \{\s*slug: '[^']+',\s*token: '([^']+)',\s*fillAlpha: ([\d.]+)", text)]
    if len(table) != 10:
        raise ValueError(f"expected 10 statuses in status-tokens.ts, parsed {len(table)}")
    return table


def compute(maps: dict[str, dict[str, str]], *, alpha=None, backdrop_map=None, label_token=None) -> dict:
    """computeMatrix (queue-primitives.test.ts:265-292), with its three option hooks."""
    label, icon = [], []
    for theme in ("dark", "light"):
        hues = maps[theme]
        source = maps[backdrop_map] if backdrop_map else hues
        for status, token, fill_alpha in status_table():
            for key, entry in SETS["CONTRAST_BACKDROPS"].items():
                base = backdrop(source, entry["expr"])
                fill = over(to_rgb(hues, token), fill_alpha if alpha is None else alpha, base)
                row = {"theme": theme, "status": status, "backdrop": BACKDROP_NAME.get(key, key), "token": token}
                label.append({**row, "ratio": ratio(to_rgb(hues, token if label_token else "--color-fg"), fill)})
                icon.append({**row, "ratio": ratio(to_rgb(hues, token), base)})
    return {"label": label, "icon": icon}


def theme_maps(css: str) -> dict[str, dict[str, str]]:
    return {"dark": theme_block(css, DARK_OPENER), "light": theme_block(css, LIGHT_OPENER)}


def with_light(css: str, values: dict[str, str]) -> str:
    """The CSS with the light block's accent pair set to `values`; nothing else changes."""
    start = css.index(LIGHT_OPENER)
    end = css.index("\n}", start)
    body = css[start:end]
    for token, value in values.items():
        body, n = re.subn(rf"({re.escape(token)}\s*:\s*)#[0-9a-fA-F]{{6}}(;)", rf"\g<1>{value}\g<2>", body)
        if n != 1:
            raise ValueError(f"{token} appears {n} times in the light block")
    return css[:start] + body + css[end:]


def moves(pinned: dict, computed: dict) -> dict:
    """Every row whose ratio differs: (kind, theme, status, backdrop) -> (index, pinned, computed)."""
    out = {}
    for kind in ("label", "icon"):
        if len(pinned[kind]) != len(computed[kind]):
            raise ValueError(f"{kind}: {len(pinned[kind])} pinned rows, {len(computed[kind])} computed")
        for i, (p, c) in enumerate(zip(pinned[kind], computed[kind])):
            if any(p[k] != c[k] for k in ROW_KEYS):
                raise ValueError(f"{kind}[{i}] row identity differs: {[p[k] for k in ROW_KEYS]} vs {[c[k] for k in ROW_KEYS]}")
            if p["ratio"] != c["ratio"]:
                out[(kind, p["theme"], p["status"], p["backdrop"])] = (i, p["ratio"], c["ratio"])
    return out


def meta_of(matrix: dict) -> dict:
    labels = [r["ratio"] for r in matrix["label"]]
    icons = [r["ratio"] for r in matrix["icon"]]
    floor = SETS["CONTRAST_MIN"]
    return {
        "pairings": len(labels),
        "label_pass": sum(r >= floor for r in labels),
        "label_fail": sum(r < floor for r in labels),
        "label_worst": min(labels),
        "icon_below_advisory": sum(r < 3.0 for r in icons),
        "icon_worst": min(icons),
    }


def problems(pinned: dict, computed: dict, maps: dict | None = None) -> list[str]:
    found = []
    got = moves(pinned, computed)
    want = {(k, "light", s, b): (old, new) for k, s, b, old, new in EXPECTED_MOVES}
    for key in sorted(set(got) | set(want)):
        if key[1] == "dark" and key in got:
            found.append(f"dark row moved: {key} {got[key][1]} -> {got[key][2]}")
        elif key not in want:
            found.append(f"unplanned move: {key} {got[key][1]} -> {got[key][2]}")
        elif key not in got:
            found.append(f"planned move absent: {key} stays {want[key][0]}, plan says {want[key][1]}")
        elif got[key][1:] != want[key]:
            found.append(f"move differs from the plan: {key} {got[key][1]} -> {got[key][2]}, plan {want[key][0]} -> {want[key][1]}")
    for row in computed["label"]:
        if row["ratio"] < SETS["CONTRAST_MIN"]:
            found.append(f"label under {SETS['CONTRAST_MIN']}: {row['theme']}/{row['status']}/{row['backdrop']} {row['ratio']}")
    pinned_meta = {k: pinned["_meta"][k] for k in meta_of(computed)} if "_meta" in pinned else meta_of(pinned)
    if meta_of(computed) != pinned_meta:
        found.append(f"_meta no longer describes the matrix: pinned {pinned_meta}, computed {meta_of(computed)}")
    if maps is not None:
        if compute(maps, alpha=0.6)["label"] == computed["label"]:
            found.append("AC-43.3 negative alphaRaised no longer moves the matrix")
        if compute(maps, backdrop_map="light")["label"] == computed["label"]:
            found.append("AC-43.3 negative crossTheme no longer moves the matrix")
        same = [r["ratio"] for r in compute(maps, label_token=True)["label"] if r["theme"] == "light" and r["status"] == "Cancelled"]
        if len(same) != 4 or min(same) >= SETS["CONTRAST_MIN"]:
            found.append(f"AC-43.3 negative sameTokenLabel light Cancelled no longer under the floor: {same}")
    return found


def rewrite(raw: bytes, pinned: dict, computed: dict) -> bytes:
    """Replace only the moved ratio numbers in the file's own text."""
    text = raw.decode("utf-8")
    icon_at = text.index('"icon": [')
    label_at = text.index('"label": [')
    spans = list(re.finditer(r'"ratio": ([0-9.]+)(?=\r\n)', text))
    by_kind = {
        "label": [m for m in spans if label_at < m.start() < icon_at],
        "icon": [m for m in spans if m.start() > icon_at],
    }
    for kind, found in by_kind.items():
        if len(found) != len(pinned[kind]):
            raise ValueError(f"{kind}: {len(found)} ratio lines, {len(pinned[kind])} rows")
    edits = []
    for (kind, _theme, _status, _backdrop), (i, old, new) in moves(pinned, computed).items():
        m = by_kind[kind][i]
        if json.loads(m.group(1)) != old:
            raise ValueError(f"{kind}[{i}] reads {m.group(1)} in the file, {old} parsed")
        edits.append((m.start(1), m.end(1), json.dumps(new)))
    for start, end, value in sorted(edits, reverse=True):
        text = text[:start] + value + text[end:]
    return text.encode("utf-8")


def verify_written(before: bytes, after: bytes, computed: dict) -> list[str]:
    found = []
    old, new = json.loads(before), json.loads(after)
    if new["_meta"] != old["_meta"]:
        found.append("_meta changed")
    for kind in ("label", "icon"):
        if new[kind] != computed[kind]:
            found.append(f"written {kind} differs from the computed matrix")
    lf = after.count(b"\n")
    if before.count(CRLF) != after.count(CRLF) or lf != after.count(CRLF):
        found.append(f"line endings changed: CRLF {before.count(CRLF)} -> {after.count(CRLF)}, LF {lf}")
    changed = [(a, b) for a, b in zip(before.split(CRLF), after.split(CRLF)) if a != b]
    if len(changed) != len(EXPECTED_MOVES) or not all(b'"ratio": ' in a and b'"ratio": ' in b for a, b in changed):
        found.append(f"{len(changed)} lines changed, expected {len(EXPECTED_MOVES)} ratio lines")
    return found


def dump(matrix: dict) -> bytes:
    """The file's own format: json indent 2, CRLF, a final CRLF."""
    return (json.dumps(matrix, indent=2, ensure_ascii=False).replace("\n", "\r\n") + "\r\n").encode("utf-8")


def check_shipped(css_path: Path, matrix_path: Path) -> int:
    pinned = json.loads(matrix_path.read_bytes())
    computed = compute(theme_maps(css_path.read_text(encoding="utf-8")))
    got = moves(pinned, computed)
    for key, (i, old, new) in got.items():
        print(f"differs: {key} pinned {old}, replica {new}")
    print(f"matrix-rebaseline --check-shipped: {len(got)} of {len(pinned['label']) + len(pinned['icon'])} rows differ")
    return 1 if got else 0


def rebaseline(css_path: Path, matrix_path: Path, out: Path, expect: str | None) -> int:
    css = css_path.read_text(encoding="utf-8")
    maps = theme_maps(css)
    light = {k: maps["light"][k] for k in RULED}
    if light != RULED:
        print(f"refused: the light accent pair in {css_path.name} is {light}, not the ruled {RULED}")
        return 1
    before = matrix_path.read_bytes()
    digest = hashlib.sha256(before).hexdigest()
    print(f"before {digest} {len(before)} B")
    if out.resolve() == matrix_path.resolve() and expect != digest:
        print(f"refused: writing in place needs --expect-sha256 {digest}; got {expect}")
        return 1
    pinned = json.loads(before)
    computed = compute(maps)
    found = problems(pinned, computed, maps)
    for line in found:
        print("problem:", line)
    if found:
        print(f"matrix-rebaseline: {len(found)} problem(s); nothing written")
        return 1
    after = rewrite(before, pinned, computed)
    found = verify_written(before, after, computed)
    for line in found:
        print("problem:", line)
    if found:
        print(f"matrix-rebaseline: {len(found)} problem(s); nothing written")
        return 1
    out.write_bytes(after)
    for key, (i, old, new) in sorted(moves(pinned, computed).items(), key=lambda kv: (kv[0][0] != "label", kv[1][0])):
        print(f"  {key[0]} {key[1]}/{key[2]}/{key[3]}: {old} -> {new}")
    print(f"after  {hashlib.sha256(after).hexdigest()} {len(after)} B, CRLF {after.count(CRLF)}, label_worst {meta_of(computed)['label_worst']}")
    print(f"matrix-rebaseline: 0 problems, {len(EXPECTED_MOVES)} values written to {out.as_posix()}")
    return 0


def selftest() -> int:
    css = CSS.read_text(encoding="utf-8")
    shipped_maps = theme_maps(with_light(css, SHIPPED))
    ruled_maps = theme_maps(with_light(css, RULED))
    base = compute(shipped_maps)
    base["_meta"] = json.loads(MATRIX.read_bytes())["_meta"]
    ruled = compute(ruled_maps)
    failures = []

    def case(name: str, found: list[str], expect: str | None) -> None:
        ok = (not found) if expect is None else any(expect in line for line in found)
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {found[:2]}")
        if not ok:
            failures.append(name)

    case("ruled tokens move exactly the planned 40", problems(base, ruled, ruled_maps), None)
    case("shipped tokens move nothing the plan names", problems(base, base), "planned move absent")
    dark = copy.deepcopy(ruled)
    dark["label"][0]["ratio"] += 0.01
    case("a dark row that moves is refused", problems(base, dark), "dark row moved")
    stray = copy.deepcopy(ruled)
    card = next(i for i, r in enumerate(stray["label"]) if (r["theme"], r["backdrop"]) == ("light", "card"))
    stray["label"][card]["ratio"] += 0.01
    case("an unplanned light move is refused", problems(base, stray), "unplanned move")
    wrong = copy.deepcopy(ruled)
    i = moves(base, ruled)[("label", "light", "Failed", "detail-open")][0]
    wrong["label"][i]["ratio"] = 9.9
    case("a value other than the plan's is refused", problems(base, wrong), "move differs from the plan")
    low = copy.deepcopy(ruled)
    low["label"][i]["ratio"] = 4.49
    case("a label under 4.5 is refused", problems(base, low), "label under 4.5")
    raw = dump(base)
    after = rewrite(raw, base, ruled)
    case("the CRLF round trip writes only the 40 ratio lines", verify_written(raw, after, ruled), None)
    lf = raw.replace(b"\r\n", b"\n")
    try:
        rewrite(lf, base, ruled)
        case("an LF file is refused", [], "ratio lines")
    except ValueError as exc:
        case("an LF file is refused", [str(exc)], "ratio lines")
    pairs = list(zip(with_light(css, SHIPPED).splitlines(), with_light(css, RULED).splitlines()))
    changed = [b for a, b in pairs if a != b]
    case("the ruled CSS differs from the shipped CSS by two lines", [] if len(changed) == 2 else [f"{len(changed)} lines"], None)
    print(f"matrix-rebaseline selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--css", type=Path, default=CSS)
    parser.add_argument("--matrix", type=Path, default=MATRIX)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expect-sha256")
    parser.add_argument("--check-shipped", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.check_shipped:
        return check_shipped(args.css, args.matrix)
    return rebaseline(args.css, args.matrix, args.out or args.matrix, args.expect_sha256)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
