"""Session 97 (task row 1; AC-161.1, AC-161.2): the diagnosis from receipts, before any change.

    uv run --no-sync python <plan>/diagnosis.py

It reads the row-1 receipts under D (C:/Temp/av-kit/e2e-host-parity): the second host's two
`a43cdb2` Playwright reports (through `tools/e2e_remote.py`'s run folders), the dev PC's native
fidelity report (`ehp-fidelity-native-1.json`), the fidelity and hover probes (`ehp-fidprobe-1.txt`,
`ehp-hovprobe-1.txt`), `ehp-hover-spec-red-1.txt`, the second host's plan-time font facts and
`baseline-scope.json`; it computes the bake's plate for 'Hi' at 32 with `avkit_infra` and Pillow,
and reads the dev PC's font. It writes `D/ehp-diagnosis-1.txt` itself (Session 95 RULE-3), one
section per host and cause, each with its numbers. When every number holds, the last line is
exactly `moving side: preview plate width (textBackgroundBox); hover: the host's pointer
capability` and the exit is 0; otherwise the receipt names the first number that does not hold,
writes no such line, and the exit is 1 (S5). It prints ASCII, names no host alias, account or
host folder, and writes only the one receipt.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

from avkit_infra.capture.adapter import text_plate_box

ROOT = Path(__file__).resolve().parents[4]
PLAN = Path(__file__).resolve().parent
D = Path("C:/Temp/av-kit/e2e-host-parity")
OUT = D / "ehp-diagnosis-1.txt"
MINIAIR = (
    Path("C:/Temp/av-kit/e2e-remote/r20261119T074154Z-a43cdb2/host/report.json"),
    Path("C:/Temp/av-kit/e2e-remote/r20261119T084412Z-a43cdb2/host/report.json"),
)
NATIVE = D / "ehp-fidelity-native-1.json"
FIDPROBE = D / "ehp-fidprobe-1.txt"
HOVPROBE = D / "ehp-hovprobe-1.txt"
SPEC_RED = D / "ehp-hover-spec-red-1.txt"
BOXES = (D / "ehp-boxes-miniair-1.txt", D / "ehp-boxes-native-1.txt")
FONT_MINIAIR = D / "ehp-plan-font-facts-miniair.txt"
FONT = Path("C:/Windows/Fonts/segoeui.ttf")
FONT_SHA = "704eada12961a27fd271f7d3b09e2066520e758390c1776744eff430fee30f6e"
FIDELITY = ("AC-82.6", "AC-102.19", "AC-102.20")
SIDES = ("left", "top", "right", "bottom")
MINIAIR_GAP = {"AC-82.6": [0, 0, 2, 0], "AC-102.19": [0, 0, 2, 1], "AC-102.20": [0, 0, 2, 0]}
MINIAIR_ORIGIN = {
    "AC-82.6": (718, 442.5),
    "AC-102.19": (718, 422.5),
    "AC-102.20": (718, 442.5),
}
REST = "rgb(21, 94, 117)"
HOVERED = "rgb(22, 78, 99)"
LAST = "moving side: preview plate width (textBackgroundBox); hover: the host's pointer capability"
ANSI = re.compile(r"\x1b\[[0-9;]*m")


class Miss(Exception):
    """A number that does not hold (S5)."""


lines: list[str] = []


def say(text: str) -> None:
    lines.append(text)


def need(ok: bool, what: str) -> None:
    if not ok:
        raise Miss(what)


def text_of(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig", "replace")


def json_lines(path: Path) -> list[dict]:
    out = []
    for line in text_of(path).splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                continue
    return out


def specs(report: dict) -> list[tuple[str, str, str, dict, list]]:
    """(file, title, test status, first result, stdout texts) for every spec in a report."""
    rows = []

    def walk(suite: dict, file: str) -> None:
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                results = test.get("results", [])
                first = results[0] if results else {}
                texts = []
                for result in results:
                    for chunk in result.get("stdout", []):
                        texts.append(
                            chunk.get("text", "") if isinstance(chunk, dict) else str(chunk)
                        )
                rows.append(
                    (file, str(spec.get("title", "")), str(test.get("status")), first, texts)
                )
        for child in suite.get("suites", []):
            walk(child, child.get("file", file))

    for suite in report.get("suites", []):
        walk(suite, suite.get("file", ""))
    return rows


def boxes_of(texts: list[str]) -> dict:
    for text in texts:
        if "boxes" in text:
            return json.loads(text.split("boxes", 1)[1])
    raise Miss("a fidelity spec logged no boxes line")


def gap(boxes: dict) -> list[int]:
    return [abs(int(boxes["preview"]["plate"][s]) - int(boxes["bake"]["plate"][s])) for s in SIDES]


def ltrb(box: dict) -> list[int]:
    return [int(box[s]) for s in SIDES]


def miniair() -> None:
    say("== the mini-air (second host): both a43cdb2 tool runs ==")
    for path in MINIAIR:
        report = json.loads(path.read_bytes().decode("utf-8"))
        rows = specs(report)
        st = report.get("stats", {})
        run = path.parent.parent.name
        say(f"report {run}: expected {st.get('expected')} unexpected {st.get('unexpected')}")
        for ac in FIDELITY:
            hits = [r for r in rows if r[1].split()[:1] == [ac]]
            need(
                len(hits) == 1, f"mini-air {path.parent.parent.name}: {ac} found {len(hits)} times"
            )
            _file, _title, status, first, texts = hits[0]
            b = boxes_of(texts)
            g = gap(b)
            o = (b["preview"]["rect"]["left"], b["preview"]["rect"]["top"])
            pw = b["preview"]["plate"]["right"] - b["preview"]["plate"]["left"] + 1
            bw = b["bake"]["plate"]["right"] - b["bake"]["plate"]["left"] + 1
            pp, bp = b["preview"]["plate"], b["bake"]["plate"]
            say(
                f"  {ac}: result {first.get('status')} (test {status});"
                f" preview plate {ltrb(pp)} ink {ltrb(b['preview']['ink'])};"
                f" bake plate {ltrb(bp)} ink {ltrb(b['bake']['ink'])}; gap l,t,r,b {g};"
                f" origin {list(o)}; plate width preview {pw} ({pp['left']} to {pp['right']})"
                f" bake {bw} ({bp['left']} to {bp['right']})"
            )
            need(
                first.get("status") == "failed",
                f"mini-air {ac} result is {first.get('status')}, not failed",
            )
            need(g == MINIAIR_GAP[ac], f"mini-air {ac} gap {g}, not {MINIAIR_GAP[ac]}")
            need(
                o == MINIAIR_ORIGIN[ac],
                f"mini-air {ac} origin {list(o)}, not {list(MINIAIR_ORIGIN[ac])}",
            )
            need((pw, bw) == (30, 32), f"mini-air {ac} plate widths {pw} and {bw}, not 30 and 32")
            need(
                (b["preview"]["plate"]["left"], b["preview"]["plate"]["right"]) == (20, 49)
                and (b["bake"]["plate"]["left"], b["bake"]["plate"]["right"]) == (20, 51),
                f"mini-air {ac} plate columns are not 20 to 49 against 20 to 51",
            )
        hits = [r for r in rows if r[1].startswith("AC-126.8 ")]
        need(
            len(hits) == 1, f"mini-air {path.parent.parent.name}: AC-126.8 found {len(hits)} times"
        )
        _file, _title, status, first, _texts = hits[0]
        error = ANSI.sub("", str((first.get("error") or {}).get("message", "")))
        received = re.findall(r'Received:\s+"([^"]+)"', error)
        say(f"  AC-126.8: test {status}; result {first.get('status')}; received {received}")
        need(status == "unexpected", f"mini-air AC-126.8 is {status}, not unexpected")
        need(REST in error and received == [REST], f"mini-air AC-126.8 error does not carry {REST}")
    for path in BOXES:
        rows = re.findall(r"rows: (\d+)", text_of(path))
        say(f"boxes-report receipt {path.name}: rows per report {rows}")
        need(
            rows and all(r == "3" for r in rows), f"{path.name} does not list three rows per report"
        )


def devpc_native(probe: list[dict]) -> None:
    say("== the dev PC natively ==")
    report = json.loads(NATIVE.read_bytes().decode("utf-8"))
    st = report.get("stats", {})
    say(
        f"report {NATIVE.name}: expected {st.get('expected')}"
        f" unexpected {st.get('unexpected')} flaky {st.get('flaky')}"
    )
    rows = specs(report)
    for ac in FIDELITY:
        hits = [r for r in rows if r[1].split()[:1] == [ac]]
        need(len(hits) == 1, f"dev PC native: {ac} found {len(hits)} times")
        _file, _title, status, first, texts = hits[0]
        b = boxes_of(texts)
        g = gap(b)
        say(
            f"  {ac}: result {first.get('status')} (test {status});"
            f" preview plate {ltrb(b['preview']['plate'])}; bake plate {ltrb(b['bake']['plate'])};"
            f" gap l,t,r,b {g}; origin {[b['preview']['rect'][k] for k in ('left', 'top')]}"
        )
        need(
            first.get("status") == "passed",
            f"dev PC native {ac} result is {first.get('status')}, not passed",
        )
        need(max(g) <= 1, f"dev PC native {ac} gap {g} has a side above 1")
    native = [p for p in probe if p.get("launch") == "native"]
    scales = sorted({p["preview"]["dpr"] for p in native} | {p["bake"]["dpr"] for p in native})
    say(f"  the spec logs no device scale; the fidelity probe's native launch prints dpr {scales}")
    need(len(scales) == 1, f"the native probe printed scales {scales}")
    for p in native:
        say(
            f"  native probe origin {p['origin']} plate width {p.get('plate_width')}:"
            f" dpr {p['preview']['dpr']} gap {p['plate_gap_ltrb']}"
        )


def devpc_scale1(probe: list[dict]) -> None:
    say("== the dev PC at a device scale of 1 (fidelity probe, dpr1 launch) ==")
    dpr1 = [p for p in probe if p.get("launch") == "dpr1"]
    for p in dpr1:
        say(
            f"  origin {p['origin']} plate width {p['plate_width']}:"
            f" preview plate {ltrb(p['preview']['plate'])}, bake plate {ltrb(p['bake']['plate'])},"
            f" dpr {p['preview']['dpr']}, gap l,t,r,b {p['plate_gap_ltrb']}"
        )
        need(
            p["preview"]["dpr"] == 1 and p["bake"]["dpr"] == 1,
            f"dpr1 line at {p['origin']} has dpr {p['preview']['dpr']}",
        )
    w30 = [p for p in dpr1 if p.get("plate_width") == 30]
    w32 = [p for p in dpr1 if p.get("plate_width") == 32]
    o30 = {tuple(p["origin"]) for p in w30}
    o32 = {tuple(p["origin"]) for p in w32}
    need(
        len(w30) == 3 and len(o30) == 3,
        f"dpr1 width-30 lines {len(w30)} at {len(o30)} origins, not 3 and 3",
    )
    need(
        len(w32) == 3 and o32 == o30,
        f"dpr1 width-32 lines {len(w32)} not at the same three origins",
    )
    need(
        all(p["plate_gap_ltrb"][2] == 2 for p in w30), "a dpr1 width-30 line has no right gap of 2"
    )
    at = [p for p in w30 if tuple(p["origin"]) == (718, 442.5)]
    need(
        len(at) == 1 and at[0]["plate_gap_ltrb"] == [0, 0, 2, 0],
        "dpr1 width 30 at [718, 442.5] is not [0, 0, 2, 0]",
    )
    need(
        all(p["plate_gap_ltrb"] == [0, 0, 0, 0] for p in w32),
        "a dpr1 width-32 line is not [0, 0, 0, 0]",
    )
    say(
        f"  width 30: right gap 2 at all {len(o30)} origins; at the mini-air's origin [718, 442.5]"
        f" {at[0]['plate_gap_ltrb']}; width 32: [0, 0, 0, 0] at all {len(o32)} origins"
    )


def launched(probe: list[dict], name: str) -> None:
    done = [p for p in probe if p.get("step") == "done"]
    need(len(done) == 1, f"{name} printed no launched_pids line")
    pids = done[0].get("launched_pids", [])
    alive = []
    for pid in pids:
        run = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/FO", "CSV", "/NH"],
            capture_output=True,
            check=False,
        )
        if b"electron" in run.stdout.lower():
            alive.append(pid)
    say(f"  {name} launched_pids {pids}; still running as electron: {alive}")
    need(not alive, f"{name} left launched pids running: {alive}")


def bake() -> None:
    say("== the bake (adapter.text_plate_box and draw.rectangle) ==")
    box = text_plate_box(20, 30, "Hi", 32)
    image = Image.new("RGB", (120, 120), (0, 0, 0))
    ImageDraw.Draw(image).rectangle(box, fill=(255, 212, 0))
    painted = image.getbbox()
    width = painted[2] - painted[0] if painted else 0
    height = painted[3] - painted[1] if painted else 0
    say(
        f"  text_plate_box(20, 30, 'Hi', 32) = {box} (inclusive);"
        f" draw.rectangle paints {width} by {height}"
    )
    say(
        "  the preview today: x 20, y 42, width 30, height 24"
        " (Math.round(right) - Math.round(left))"
    )
    need(box == (20, 42, 51, 65), f"text_plate_box gives {box}, not (20, 42, 51, 65)")
    need((width, height) == (32, 24), f"draw.rectangle paints {width} by {height}, not 32 by 24")


def hover(probe: list[dict]) -> None:
    say("== the hover cause (hover probe and the real AC-126.8) ==")
    steps = {p.get("step"): p for p in probe}
    for step in (
        "versions",
        "native",
        "blink-settings-hover-none",
        "blink-settings-hover-capable",
        "hover-none-then-capable",
    ):
        p = steps.get(step, {})
        say(f"  {step}: " + json.dumps({k: p.get(k) for k in p if k != "step"}, sort_keys=True))
    want = {
        "native": (True, HOVERED),
        "blink-settings-hover-none": (False, REST),
        "blink-settings-hover-capable": (True, HOVERED),
    }
    for step, (hov, colour) in want.items():
        p = steps.get(step)
        need(p is not None, f"the hover probe printed no {step} step")
        need(
            p.get("hover") is hov and p.get("hovered") == colour,
            f"hover probe {step}: hover {p.get('hover')} hovered {p.get('hovered')},"
            f" not {hov} and {colour}",
        )
    launched(probe, "hover probe")
    text = text_of(SPEC_RED)
    native = re.search(r"native: (\S+) expected, (\S+) unexpected", text)
    none = re.search(r"hover-none: (\S+) expected, (\S+) unexpected; received (\[[^\]]*\])", text)
    verdict = f"hover-none fails at the hover expectation with {REST}: True" in text
    say(
        f"  hover-spec-red: native {native.groups() if native else None};"
        f" hover-none {none.groups() if none else None}; at the hover expectation {verdict}"
    )
    need(
        native is not None and native.groups() == ("1", "0"),
        "the real AC-126.8 did not pass natively",
    )
    need(
        none is not None and none.group(2) == "1" and none.group(3) == f"['{REST}']" and verdict,
        f"the real AC-126.8 under hover-none did not fail at the hover expectation with {REST}",
    )


def font() -> None:
    say("== the font ==")
    here = hashlib.sha256(FONT.read_bytes()).hexdigest()
    there = None
    for line in text_of(FONT_MINIAIR).splitlines():
        if line.strip().startswith("{"):
            facts = json.loads(line)
            there = next(
                (f["sha256"] for f in facts.get("fonts", []) if f.get("name") == "segoeui.ttf"),
                None,
            )
    say(f"  dev PC segoeui.ttf (read now) {here}")
    say(f"  mini-air segoeui.ttf ({FONT_MINIAIR.name}) {there}")
    need(here == FONT_SHA, f"the dev PC font is {here}, not the plan's (S2)")
    need(there == FONT_SHA, f"the mini-air font is {there}, not the plan's (S2)")


def tree() -> None:
    say("== the tree (AC-161.1's negative) ==")
    scope = json.loads((PLAN / "baseline-scope.json").read_bytes().decode("utf-8"))
    moved = []
    for rel, want in scope.items():
        p = ROOT / rel
        got = (
            hashlib.sha256(p.read_bytes()).hexdigest()
            if p.is_file()
            else ("absent" if not p.exists() else "not-a-file")
        )
        if got != want:
            moved.append(rel)
    say(f"  baseline-scope.json paths {len(scope)}; differing from row 0: {moved}")
    need(not moved, f"scope files differ from row 0: {moved}")


def main() -> int:
    say("ehp-diagnosis-1: Session 97 row 1, built by diagnosis.py from receipts before any change")
    try:
        fid = json_lines(FIDPROBE)
        hov = json_lines(HOVPROBE)
        miniair()
        devpc_native(fid)
        devpc_scale1(fid)
        say("== the fidelity probe's launches ==")
        launched(fid, "fidelity probe")
        bake()
        hover(hov)
        font()
        tree()
    except Miss as miss:
        say(f"S5: does not hold: {miss}")
        code = 1
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        say(f"S5: a receipt is missing or unreadable: {type(exc).__name__}: {exc}")
        code = 1
    else:
        say(LAST)
        code = 0
    text = "\n".join(lines) + "\n"
    OUT.write_bytes(text.encode("ascii", "replace"))
    print(text, end="")
    print(f"diagnosis: wrote {OUT.as_posix()} exit={code}")
    return code


if __name__ == "__main__":
    sys.exit(main())
