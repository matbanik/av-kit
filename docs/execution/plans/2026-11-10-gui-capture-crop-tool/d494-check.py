"""Session 60 D-494 check (task row 7; implementation-plan.md §Plan-local scripts, D494_RUN, D-521).

Reads D-521 from the plan's §Decision Log with the rule look-check.py uses: a ruled entry's
`chosen` starts with `"A: `, `"B: ` or `"C: `, and its `human_message_reference` holds
`USER_EXPLICIT <date> '<words>'`. Unruled fails. Under C the run was not made: the check prints
`not run under D-521 C` and exits 0.

Under A or B, every D494_RUN criterion must hold on ROOT and the agent's saved report:

- a crop call went through and succeeded: in ROOT/ledger.jsonl, not refused, not isError, and
  the text from its first `{` to its last `}` parses as JSON with an `item`;
- no remove, flatten, revert or image call went through (attempts the harness refused are
  listed, not counted against the run);
- the last successful crop's `source_id` is ROOT/seed/source-id.txt, chart-source's id, which
  `d494-harness.ts seed` writes (a crop of an earlier crop reports another frame), and its
  `applied` box overlaps ROOT/seed/panel.json `panel_px` with IoU >= 0.9;
- ROOT/inbox/chart-source.png has the same SHA-256 as ROOT/seed/chart-source.png (the source
  is unchanged);
- ROOT/inbox/chart.png exists and is the basename of that crop's `item.original_path`;
- the agent's report names that crop's `item.id`.

Exit 0 only when every line is PASS. `--selftest` runs the rules on fixture ledgers and files in
a temporary folder; the fixture "images" are plain bytes, since only hashes and names are read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

PLAN = Path("docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md")
ROOT = Path("C:/Temp/av-kit/s60/d494/root")
REPORT = Path("C:/Temp/av-kit/s60-d494-report.txt")
FORBIDDEN = ("remove", "flatten", "revert", "image")
MIN_IOU = 0.9


def ruling(plan_text: str, decision: str) -> tuple[str | None, str]:
    """The option letter Mat ruled for DECISION, or None, and a line that says why."""
    block = re.search(rf"^  - id: {re.escape(decision)}\n(.*?)(?=^  - id: |^```)", plan_text, re.MULTILINE | re.DOTALL)
    if block is None:
        return None, f"{decision}: no entry in the Decision Log"
    body = block.group(1)
    chosen = re.search(r'^    chosen: "(.*)"\s*$', body, re.MULTILINE)
    ref = re.search(r"^    human_message_reference: (.*)$", body, re.MULTILINE)
    if chosen is None:
        return None, f"{decision}: no chosen line"
    letter = re.match(r"([A-Z]): ", chosen.group(1))
    if letter is None:
        return None, f"{decision}: unruled (chosen is {chosen.group(1)[:40]!r})"
    if ref is None or not re.match(r"[\"']?USER_EXPLICIT 20\d\d-\d\d-\d\d '.+'", ref.group(1).strip()):
        return None, f"{decision}: chosen {letter.group(1)} without Mat's quoted words in human_message_reference"
    return letter.group(1), f"{decision}: ruled {letter.group(1)}"


def iou(a: dict, b: dict) -> float:
    ax2, ay2 = a["x"] + a["width"], a["y"] + a["height"]
    bx2, by2 = b["x"] + b["width"], b["y"] + b["height"]
    w = max(0, min(ax2, bx2) - max(a["x"], b["x"]))
    h = max(0, min(ay2, by2) - max(a["y"], b["y"]))
    inter = w * h
    union = a["width"] * a["height"] + b["width"] * b["height"] - inter
    return inter / union if union > 0 else 0.0


def _body(text: str) -> dict | None:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        body = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return body if isinstance(body, dict) else None


def _sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def check(plan_text: str, root: Path, report: str | None) -> list[tuple[bool, str]]:
    letter, why = ruling(plan_text, "D-521")
    if letter == "C":
        return [(True, f"{why}: not run under D-521 C")]
    if letter not in ("A", "B"):
        return [(False, why if letter is None else f"D-521: unknown option {letter}")]
    lines: list[tuple[bool, str]] = [(True, why)]
    ledger_path = root / "ledger.jsonl"
    if not ledger_path.is_file():
        return [*lines, (False, f"{ledger_path} is missing: the run made no call")]
    entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    crops: list[dict] = []
    went_through: list[str] = []
    refused: list[str] = []
    for entry in entries:
        action = entry.get("args", {}).get("action")
        if entry.get("refused"):
            refused.append(str(action))
            continue
        if action in FORBIDDEN:
            went_through.append(str(action))
        if action == "crop" and not entry.get("isError"):
            body = _body(entry.get("text", ""))
            if body is not None and isinstance(body.get("item"), dict):
                crops.append(body)
    lines.append((bool(crops), f"successful crop calls: {len(crops)} of {len(entries)} ledger entries"))
    lines.append((not went_through, f"remove/flatten/revert/image calls that went through: {went_through or 'none'}"))
    if refused:
        print(f"note: the harness refused {refused} (recorded, not counted)")
    if not crops:
        return lines
    last = crops[-1]
    # A crop of an earlier crop reports its box in that crop's frame, so the measured crop must be of chart-source.
    id_path = root / "seed" / "source-id.txt"
    source_id = id_path.read_text(encoding="utf-8").strip() if id_path.is_file() else None
    got_source = last.get("source_id")
    lines.append((source_id is not None and got_source == source_id, f"the measured crop's source_id {got_source!r} is chart-source's id {source_id!r}"))
    panel_path = root / "seed" / "panel.json"
    panel = json.loads(panel_path.read_text(encoding="utf-8"))["panel_px"] if panel_path.is_file() else None
    applied = last.get("applied")
    if panel is None or not isinstance(applied, dict):
        lines.append((False, f"IoU not computable (panel.json {'present' if panel else 'missing'}, applied {applied!r})"))
    else:
        score = iou(applied, panel)
        lines.append((score >= MIN_IOU, f"IoU of applied {applied} with panel {panel}: {score:.3f} (needs {MIN_IOU})"))
    seed_sha, inbox_sha = _sha(root / "seed" / "chart-source.png"), _sha(root / "inbox" / "chart-source.png")
    lines.append((seed_sha is not None and seed_sha == inbox_sha, "inbox/chart-source.png is byte-identical to the seed"))
    item = last["item"]
    name = Path(str(item.get("original_path", ""))).name
    chart = root / "inbox" / "chart.png"
    lines.append((chart.is_file() and name == "chart.png", f"inbox/chart.png exists and is the new shot's file (got {name!r})"))
    item_id = str(item.get("id", ""))
    lines.append((bool(item_id) and report is not None and item_id in report, f"the report names the new shot id {item_id!r}"))
    return lines


def selftest() -> int:
    def plan(chosen: str, ref: str = "\"USER_EXPLICIT 2026-11-10 'run it'\"") -> str:
        return (
            f"```yaml\n  - id: D-521\n    stage: planning\n    chosen: \"{chosen}\"\n    human_message_reference: {ref}\n"
            "  - id: D-522\n    chosen: \"A: look\"\n```\n"
        )

    panel = {"x": 640, "y": 120, "width": 520, "height": 320}

    def crop(
        applied: dict, name: str = "chart.png", item_id: str = "cap-new", is_error: bool = False, source_id: str = "cap-src"
    ) -> dict:
        body = {
            "item": {"id": item_id, "original_path": f"C:/x/inbox/{name}", "annotated_path": None},
            "source_id": source_id,
            "applied": applied,
            "clamped": False,
        }
        return {"args": {"action": "crop", "id": source_id}, "refused": False, "isError": is_error, "text": json.dumps(body)}

    good = crop(panel)
    near = crop({"x": 645, "y": 125, "width": 510, "height": 310})
    far = crop({"x": 0, "y": 0, "width": 600, "height": 400})
    first = crop({"x": 0, "y": 0, "width": 1600, "height": 900}, name="chart-1.png", item_id="cap-mid")
    chained = crop(panel, source_id="cap-mid")
    refused_image = {"args": {"action": "image", "id": "cap-src"}, "refused": True, "isError": True, "text": ""}
    flatten = {"args": {"action": "flatten", "id": "cap-src"}, "refused": False, "isError": False, "text": "{}"}
    listed = {"args": {"action": "list"}, "refused": False, "isError": False, "text": "{\"items\": []}"}
    cases = [
        ("A good run", plan("A: Haiku"), [listed, good], True, True, True, "new shot cap-new", True),
        ("B near box", plan("B: Sonnet"), [near], True, True, True, "id cap-new", True),
        ("C not run", plan("C: do nothing"), None, False, False, False, None, True),
        ("refused image is not counted", plan("A: Haiku"), [refused_image, good], True, True, True, "cap-new", True),
        ("unruled", plan("Pending Mat's ruling. Recommended A: Haiku", "null"), [good], True, True, True, "cap-new", False),
        ("ruled without words", plan("A: Haiku", "null"), [good], True, True, True, "cap-new", False),
        ("no ledger", plan("A: Haiku"), None, True, True, True, "cap-new", False),
        ("crop failed", plan("A: Haiku"), [crop(panel, is_error=True)], True, True, True, "cap-new", False),
        ("wrong box", plan("A: Haiku"), [far], True, True, True, "cap-new", False),
        ("last crop wins", plan("A: Haiku"), [good, far], True, True, True, "cap-new", False),
        ("flatten went through", plan("A: Haiku"), [good, flatten], True, True, True, "cap-new", False),
        ("source changed", plan("A: Haiku"), [good], False, True, True, "cap-new", False),
        ("no chart.png", plan("A: Haiku"), [good], True, False, True, "cap-new", False),
        ("other name", plan("A: Haiku"), [crop(panel, name="crop-1.png")], True, True, True, "cap-new", False),
        ("report lacks id", plan("A: Haiku"), [good], True, True, True, "done", False),
        ("no report", plan("A: Haiku"), [good], True, True, True, None, False),
        ("no panel.json", plan("A: Haiku"), [good], True, True, False, "cap-new", False),
        ("crop of a crop, wrong frame", plan("A: Haiku"), [first, chained], True, True, True, "cap-new", False),
        ("no source-id.txt", plan("A: Haiku"), [good], True, True, True, "cap-new", False),
    ]
    wrong = 0
    with tempfile.TemporaryDirectory(prefix="s60-d494check-") as tmp:
        for n, (label, plan_text, ledger, same_source, chart, panel_file, report, want) in enumerate(cases):
            root = Path(tmp) / f"case{n}"
            (root / "seed").mkdir(parents=True)
            (root / "inbox").mkdir()
            (root / "seed" / "chart-source.png").write_bytes(b"seed-bytes")
            if label != "no source-id.txt":
                (root / "seed" / "source-id.txt").write_text("cap-src\n", encoding="utf-8")
            (root / "inbox" / "chart-source.png").write_bytes(b"seed-bytes" if same_source else b"changed")
            if chart:
                (root / "inbox" / "chart.png").write_bytes(b"crop-bytes")
            if panel_file:
                (root / "seed" / "panel.json").write_text(json.dumps({"panel_px": panel}), encoding="utf-8")
            if ledger is not None:
                (root / "ledger.jsonl").write_text("".join(json.dumps(e) + "\n" for e in ledger), encoding="utf-8")
            lines = check(plan_text, root, report)
            got = all(ok for ok, _ in lines)
            if got != want:
                wrong += 1
                for ok, line in lines:
                    print(f"    {'PASS' if ok else 'FAIL'} {line}")
            print(f"{'ok' if got == want else 'WRONG'} {label}: pass={got} want={want}")
    print(f"d494-check selftest: {wrong} wrong")
    return 1 if wrong else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", default=str(PLAN))
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    plan_text = Path(args.plan).read_text(encoding="utf-8")
    report_path = Path(args.report)
    report = report_path.read_text(encoding="utf-8") if report_path.is_file() else None
    lines = check(plan_text, Path(args.root), report)
    for ok, line in lines:
        print(f"{'PASS' if ok else 'FAIL'} {line}")
    ok = all(ok for ok, _ in lines)
    print("d494-check: ok" if ok else "d494-check: failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
