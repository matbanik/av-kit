"""Session 64 description eval check (task row E-4; implementation-plan.md EVAL_RUN, D-608).

Reads D-608 from the plan's Decision Log with the rule look-check.py uses: a ruled entry's
`chosen` starts with `"A: `, `"B: ` or `"C: `, and its `human_message_reference` holds
`USER_EXPLICIT <date> '<words>'`. Unruled fails. Under C the eval was not run: the check prints
`not run under D-608 C` and exits 0. Under A the runs are real-t1..t3 and meta-t1..t3; under B,
real-t1..t3.

Each run has ROOT = BASE/<surface>-t<n>/root (its ledger.jsonl and inbox) and the agent's saved
final message at REPORTS/s64-eval-<surface>-t<n>-report.txt. The pass rules (EVAL_RUN):

- every run: no ledger entry outside the harness allowlist went through (refused attempts are
  listed, not counted), and the media files still have the SHA-256 in KEY/answers.json;
- t1: at least one successful frames or sheet call on meeting.mp4 and one successful image
  call; the report has a line `slide: <title>` equal (case and spacing aside) to the answer;
- t2: at least two successful sheet calls on driveway.mp4; the report has a line
  `arrival: <seconds or HH:MM:SS>` within 5 s of the answer;
- t3: the last successful export call has format jpeg, its source_id is ROOT/seed/source-id.txt,
  its shot.bytes is under 500,000 and its long edge is at least 1280, the file at shot.path
  exists with that size, sits directly in ROOT/inbox, decodes with Pillow as JPEG, and its
  decoded size equals the response's width and height (so the response can't vouch for a file
  that isn't the deliverable; round 1 F2), ROOT/inbox/dashboard-4k.png still has the answer's
  SHA-256, and the report has a line `new shot: <id>` naming that shot.

Exit 0 only when every line is PASS. `--selftest` runs the rules on fixture ledgers and files in a
temporary folder; the fixture "media" are plain bytes, since only their hashes are read, and the
t3 export files are real images made with Pillow (a JPEG positive control, a PNG, a 16x16 JPEG,
a 12-byte non-image, a JPEG outside the inbox and a JPEG padded to exactly 500,000 bytes).
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import tempfile
from pathlib import Path

from PIL import Image

PLAN = Path("docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md")
BASE = Path("C:/Temp/av-kit/s64/eval")
REPORTS = Path("C:/Temp/av-kit")
KEY = Path("C:/Temp/av-kit/s64/eval-key")  # outside BASE, so no run root sits beside the answers
ALLOWED = {
    "avkit_capture": {"list", "get", "image", "frames", "sheet", "export", "crop"},
    "avkit_convert": {"probe"},
}
JPEG_LIMIT = 500_000
MIN_LONG_EDGE = 1280
ARRIVAL_SLACK_S = 5
MIN_SHEETS = 2
DECISION = "D-608"


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


def _decode(path: Path) -> tuple[str | None, tuple[int, int] | None]:
    """The format and size Pillow decodes from `path`, or (None, None) when it can't."""
    try:
        with Image.open(path) as image:
            image.load()
            return image.format, image.size
    except Exception:
        return None, None


def _seconds(value: str) -> float | None:
    value = value.strip().rstrip(".").removesuffix("s").strip()
    if re.fullmatch(r"\d+(\.\d+)?", value):
        return float(value)
    m = re.fullmatch(r"(\d+):(\d\d):(\d\d(?:\.\d+)?)", value)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.fullmatch(r"(\d+):(\d\d(?:\.\d+)?)", value)
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    return None


def _field(report: str | None, name: str) -> str | None:
    if report is None:
        return None
    found = re.findall(rf"^\W*{name}\W*:\s*`?(.+?)`?\s*$", report, re.MULTILINE | re.IGNORECASE)
    return found[-1] if found else None


def _norm(text: str) -> str:
    return " ".join(text.strip().strip("\"'*`").split()).casefold()


def check_run(task: str, root: Path, report: str | None, key: dict, media: Path) -> list[tuple[bool, str]]:
    lines: list[tuple[bool, str]] = []
    ledger_path = root / "ledger.jsonl"
    if not ledger_path.is_file():
        return [(False, f"{ledger_path} is missing: the run made no call")]
    entries = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ok_calls: list[dict] = []
    outside: list[str] = []
    refused: list[str] = []
    for entry in entries:
        tool, action = str(entry.get("tool")), str(entry.get("args", {}).get("action"))
        if entry.get("refused"):
            refused.append(f"{tool} {action}")
            continue
        if action not in ALLOWED.get(tool, set()):
            outside.append(f"{tool} {action}")
        if not entry.get("isError"):
            ok_calls.append(entry)
    lines.append((not outside, f"calls outside the allowlist that went through: {outside or 'none'}"))
    if refused:
        print(f"note: the harness refused {refused} (recorded, not counted)")
    changed = [name for name, sha in key["media_sha256"].items() if _sha(media / name) != sha]
    lines.append((not changed, f"media files changed: {changed or 'none'}"))

    def calls(tool: str, action: str, video: str | None = None) -> list[dict]:
        return [
            e for e in ok_calls
            if e.get("tool") == tool and e.get("args", {}).get("action") == action
            and (video is None or Path(str(e["args"].get("path", ""))).name == video)
        ]

    if task == "t1":
        looks = calls("avkit_capture", "frames", "meeting.mp4") + calls("avkit_capture", "sheet", "meeting.mp4")
        lines.append((bool(looks), f"successful frames or sheet calls on meeting.mp4: {len(looks)}"))
        views = calls("avkit_capture", "image")
        lines.append((bool(views), f"successful image calls: {len(views)}"))
        said = _field(report, "slide")
        want = key["meeting"]["title"]
        lines.append((said is not None and _norm(said) == _norm(want), f"reported slide {said!r}, answer {want!r}"))
    elif task == "t2":
        sheets = calls("avkit_capture", "sheet", "driveway.mp4")
        lines.append((len(sheets) >= MIN_SHEETS, f"successful sheet calls on driveway.mp4: {len(sheets)} (needs {MIN_SHEETS})"))
        said = _field(report, "arrival")
        got = _seconds(said) if said is not None else None
        want = key["driveway"]["arrive_s"]
        near = got is not None and abs(got - want) <= ARRIVAL_SLACK_S
        lines.append((near, f"reported arrival {said!r} ({got} s), answer {want} s, slack {ARRIVAL_SLACK_S} s"))
    elif task == "t3":
        exports = [b for b in (_body(e.get("text", "")) for e in calls("avkit_capture", "export")) if b is not None]
        export_args = [e["args"] for e in calls("avkit_capture", "export")]
        lines.append((bool(exports), f"successful export calls: {len(exports)}"))
        if not exports:
            return lines
        last, last_args = exports[-1], export_args[-1]
        lines.append((last_args.get("format") == "jpeg", f"the last export's format is {last_args.get('format')!r}"))
        id_path = root / "seed" / "source-id.txt"
        source_id = id_path.read_text(encoding="utf-8").strip() if id_path.is_file() else None
        got_source = last.get("source_id")
        lines.append((source_id is not None and got_source == source_id, f"the export's source_id {got_source!r} is dashboard-4k's id {source_id!r}"))
        shot = last.get("shot") if isinstance(last.get("shot"), dict) else {}
        size, width, height = shot.get("bytes"), shot.get("width"), shot.get("height")
        lines.append((isinstance(size, int) and size < JPEG_LIMIT, f"shot.bytes {size!r} is under {JPEG_LIMIT}"))
        long_edge = max(width, height) if isinstance(width, int) and isinstance(height, int) else None
        lines.append((long_edge is not None and long_edge >= MIN_LONG_EDGE, f"long edge {long_edge!r} is at least {MIN_LONG_EDGE}"))
        out = Path(str(shot.get("path", "")))
        on_disk = out.stat().st_size if out.is_file() else None
        lines.append((on_disk is not None and on_disk == size, f"{out.name or '(no path)'} exists with {on_disk!r} bytes"))
        inside = on_disk is not None and out.resolve().parent == (root / "inbox").resolve()
        lines.append((inside, f"{out.name or '(no path)'} sits directly in the run's inbox"))
        decoded_format, decoded_size = _decode(out) if on_disk is not None else (None, None)
        lines.append((decoded_format == "JPEG", f"the file decodes as {decoded_format!r}"))
        lines.append((
            decoded_size is not None and decoded_size == (width, height) and max(decoded_size) >= MIN_LONG_EDGE,
            f"decoded size {decoded_size!r} equals the response's {(width, height)!r} and reaches {MIN_LONG_EDGE}",
        ))
        source_sha = _sha(root / "inbox" / "dashboard-4k.png")
        lines.append((source_sha == key["screenshot"]["sha256"], "inbox/dashboard-4k.png is byte-identical to the media file"))
        said = _field(report, "new shot")
        shot_id = str(shot.get("id", ""))
        lines.append((bool(shot_id) and said is not None and said.strip() == shot_id, f"reported new shot {said!r}, export's id {shot_id!r}"))
    return lines


def check(plan_text: str, base: Path, reports: Path, answers: Path, media: Path) -> list[tuple[bool, str]]:
    letter, why = ruling(plan_text, DECISION)
    if letter == "C":
        return [(True, f"{why}: not run under {DECISION} C")]
    if letter not in ("A", "B"):
        return [(False, why if letter is None else f"{DECISION}: unknown option {letter}")]
    lines: list[tuple[bool, str]] = [(True, why)]
    if not answers.is_file():
        return [*lines, (False, f"{answers} is missing; run eval-seed.py first")]
    key = json.loads(answers.read_text(encoding="utf-8"))
    surfaces = ("real", "meta") if letter == "A" else ("real",)
    for surface in surfaces:
        for task in ("t1", "t2", "t3"):
            name = f"{surface}-{task}"
            report_path = reports / f"s64-eval-{name}-report.txt"
            report = report_path.read_text(encoding="utf-8") if report_path.is_file() else None
            run_lines = check_run(task, base / name / "root", report, key, media)
            passed = all(ok for ok, _ in run_lines)
            lines.extend((ok, f"{name}: {line}") for ok, line in run_lines)
            print(f"run {name}: {'pass' if passed else 'fail'}")
    return lines


def selftest() -> int:
    def plan(chosen: str, ref: str = "\"USER_EXPLICIT 2026-11-11 'run it'\"") -> str:
        return (
            f"```yaml\n  - id: {DECISION}\n    stage: planning\n    chosen: \"{chosen}\"\n    human_message_reference: {ref}\n"
            "  - id: D-609\n    chosen: \"A: refuse\"\n```\n"
        )

    def entry(tool: str, args: dict, text: str = "{}", is_error: bool = False, refused: bool = False) -> dict:
        return {"tool": tool, "args": args, "refused": refused, "isError": is_error, "text": text}

    key = {
        "meeting": {"ask_s": 2409, "title": "Copper Hiring 42", "previous_title": "Orbit Churn 17"},
        "driveway": {"arrive_s": 3954},
        "screenshot": {"sha256": hashlib.sha256(b"png-bytes").hexdigest()},
        "media_sha256": {"meeting.mp4": hashlib.sha256(b"meet").hexdigest(), "driveway.mp4": hashlib.sha256(b"drive").hexdigest()},
    }
    sheet_m = entry("avkit_capture", {"action": "sheet", "path": "C:/m/meeting.mp4"})
    frames_m = entry("avkit_capture", {"action": "frames", "path": "C:/m/meeting.mp4", "at": [2409]})
    image = entry("avkit_capture", {"action": "image", "id": "cap-f"})
    sheet_d = entry("avkit_capture", {"action": "sheet", "path": "C:/m/driveway.mp4"})
    sheet_d_bad = entry("avkit_capture", {"action": "sheet", "path": "C:/m/driveway.mp4"}, is_error=True)
    remove_ok = entry("avkit_capture", {"action": "remove", "id": "cap-src", "confirm": True})
    remove_refused = entry("avkit_capture", {"action": "remove", "id": "cap-src"}, refused=True, is_error=True)

    def export(fmt: str = "jpeg", size: int | str = "SIZE", w: int = 1280, h: int = 720, src: str = "cap-src", path: str = "OUT") -> dict:
        # "SIZE" is replaced with the fixture file's real byte count when the ledger is written.
        body = {"shot": {"id": "cap-new", "path": path, "width": w, "height": h, "bytes": size}, "source_id": src}
        return entry("avkit_capture", {"action": "export", "id": src, "format": fmt}, json.dumps(body))

    def image_bytes(kind: str, w: int, h: int) -> bytes:
        buffer = io.BytesIO()
        Image.new("RGB", (w, h), (40, 90, 160)).save(buffer, format=kind)
        return buffer.getvalue()

    def make_file(spec: str | None, root: Path) -> Path | None:
        """Write the t3 fixture file named by `spec` and return its path.

        Specs: "jpeg WxH", "png WxH", "junk", with optional " pad N" (append zero bytes after the
        JPEG end marker until the file is N bytes) and " outside" (write it under ROOT/elsewhere)."""
        if spec is None:
            return None
        words = spec.split()
        folder = root / ("elsewhere" if "outside" in words else "inbox")
        folder.mkdir(exist_ok=True)
        out = folder / "dashboard-4k-export.jpg"
        if words[0] == "junk":
            data = b"not an image"
        else:
            w, h = (int(n) for n in words[1].split("x"))
            data = image_bytes(words[0].upper(), w, h)
        if "pad" in words:
            data += b"\0" * (int(words[words.index("pad") + 1]) - len(data))
        out.write_bytes(data)
        return out

    good = "jpeg 1280x720"
    # (label, plan, task, ledger, report, t3 file spec or None, source changed, media changed, want)
    cases = [
        ("t1 good", "A: Haiku", "t1", [sheet_m, frames_m, image], "slide: Copper Hiring 42", None, False, False, True),
        ("t1 spacing and case", "A: Haiku", "t1", [frames_m, image], "Slide: `copper  hiring 42`", None, False, False, True),
        ("t1 previous slide", "A: Haiku", "t1", [frames_m, image], "slide: Orbit Churn 17", None, False, False, False),
        ("t1 no image call", "A: Haiku", "t1", [frames_m], "slide: Copper Hiring 42", None, False, False, False),
        ("t1 no frames or sheet", "A: Haiku", "t1", [image], "slide: Copper Hiring 42", None, False, False, False),
        ("t1 no report", "A: Haiku", "t1", [frames_m, image], None, None, False, False, False),
        ("t1 media changed", "A: Haiku", "t1", [frames_m, image], "slide: Copper Hiring 42", None, False, True, False),
        ("t2 good seconds", "B: Sonnet", "t2", [sheet_d, sheet_d], "arrival: 3956", None, False, False, True),
        ("t2 good clock", "A: Haiku", "t2", [sheet_d, sheet_d], "arrival: 01:05:50", None, False, False, True),
        ("t2 just past slack", "A: Haiku", "t2", [sheet_d, sheet_d], "arrival: 3960", None, False, False, False),
        ("t2 one sheet", "A: Haiku", "t2", [sheet_d], "arrival: 3954", None, False, False, False),
        ("t2 failed sheet not counted", "A: Haiku", "t2", [sheet_d, sheet_d_bad], "arrival: 3954", None, False, False, False),
        ("t3 good", "A: Haiku", "t3", [export()], "new shot: cap-new", good, False, False, True),
        ("t3 padded just under the limit", "A: Haiku", "t3", [export()], "new shot: cap-new", f"{good} pad 499999", False, False, True),
        ("t3 padded to the limit", "A: Haiku", "t3", [export()], "new shot: cap-new", f"{good} pad 500000", False, False, False),
        ("t3 png format asked", "A: Haiku", "t3", [export(fmt="png")], "new shot: cap-new", good, False, False, False),
        ("t3 png bytes claiming jpeg", "A: Haiku", "t3", [export()], "new shot: cap-new", "png 1280x720", False, False, False),
        ("t3 16x16 jpeg claiming 1280x720", "A: Haiku", "t3", [export()], "new shot: cap-new", "jpeg 16x16", False, False, False),
        ("t3 non-image claiming 1280x720", "A: Haiku", "t3", [export()], "new shot: cap-new", "junk", False, False, False),
        ("t3 file outside the inbox", "A: Haiku", "t3", [export()], "new shot: cap-new", f"{good} outside", False, False, False),
        ("t3 too small edge", "A: Haiku", "t3", [export(w=1279, h=719)], "new shot: cap-new", "jpeg 1279x719", False, False, False),
        ("t3 size mismatch", "A: Haiku", "t3", [export(size=1234)], "new shot: cap-new", good, False, False, False),
        ("t3 no file", "A: Haiku", "t3", [export(size=340450)], "new shot: cap-new", None, False, False, False),
        ("t3 source changed", "A: Haiku", "t3", [export()], "new shot: cap-new", good, True, False, False),
        ("t3 other source", "A: Haiku", "t3", [export(src="cap-other")], "new shot: cap-new", good, False, False, False),
        ("t3 report lacks id", "A: Haiku", "t3", [export()], "done", good, False, False, False),
        ("t3 remove went through", "A: Haiku", "t3", [export(), remove_ok], "new shot: cap-new", good, False, False, False),
        ("t3 refused remove not counted", "A: Haiku", "t3", [remove_refused, export()], "new shot: cap-new", good, False, False, True),
        ("no ledger", "A: Haiku", "t1", None, "slide: Copper Hiring 42", None, False, False, False),
    ]
    wrong = 0
    with tempfile.TemporaryDirectory(prefix="s64-evalcheck-") as tmp:
        for n, (label, chosen, task, ledger, report, spec, source_changed, media_changed, want) in enumerate(cases):
            case = Path(tmp) / f"case{n}"
            root, media = case / "root", case / "media"
            (root / "seed").mkdir(parents=True)
            (root / "inbox").mkdir()
            media.mkdir()
            (media / "meeting.mp4").write_bytes(b"meet")
            (media / "driveway.mp4").write_bytes(b"x" if media_changed else b"drive")
            (root / "seed" / "source-id.txt").write_text("cap-src\n", encoding="utf-8")
            (root / "inbox" / "dashboard-4k.png").write_bytes(b"changed" if source_changed else b"png-bytes")
            out = make_file(spec, root) or root / "inbox" / "dashboard-4k-export.jpg"
            real_size = str(out.stat().st_size) if out.is_file() else "0"
            if ledger is not None:
                text = "".join(
                    # The body is a JSON string inside the entry, so its quotes arrive escaped.
                    json.dumps(e).replace("OUT", out.as_posix()).replace('\\"SIZE\\"', real_size) + "\n" for e in ledger
                )
                (root / "ledger.jsonl").write_text(text, encoding="utf-8")
            lines = check_run(task, root, report, key, media)
            letter, _ = ruling(plan(chosen), DECISION)
            got = letter in ("A", "B") and all(ok for ok, _ in lines)
            print(f"{'ok' if got == want else 'WRONG'} {label}: pass={got} want={want}")
            if got != want:
                wrong += 1
                for ok, line in lines:
                    print(f"    {'PASS' if ok else 'FAIL'} {line}")
            elif not want:
                # Name the rule that refused a negative, so the receipt shows it failed for its reason.
                for line in (line for ok, line in lines if not ok):
                    print(f"    refused by: {line}")
        # The ruling rule on its own.
        for label, text, want_letter in (
            ("ruled C", plan("C: do nothing"), "C"),
            ("unruled", plan("Pending Mat's ruling. Recommended A: Haiku", "null"), None),
            ("ruled without words", plan("A: Haiku", "null"), None),
            ("no entry", "```yaml\n  - id: D-609\n```\n", None),
        ):
            letter, why = ruling(text, DECISION)
            ok = letter == want_letter
            wrong += 0 if ok else 1
            print(f"{'ok' if ok else 'WRONG'} {label}: {why}")
        c_lines = check(plan("C: do nothing"), Path(tmp) / "none", Path(tmp), Path(tmp) / "none.json", Path(tmp))
        c_ok = len(c_lines) == 1 and c_lines[0][0] and "not run" in c_lines[0][1]
        wrong += 0 if c_ok else 1
        print(f"{'ok' if c_ok else 'WRONG'} C skips every run")
    print(f"eval-check selftest: {wrong} wrong")
    return 1 if wrong else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", default=str(PLAN))
    parser.add_argument("--base", default=str(BASE))
    parser.add_argument("--reports", default=str(REPORTS))
    parser.add_argument("--key", default=str(KEY))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    base = Path(args.base)
    plan_text = Path(args.plan).read_text(encoding="utf-8")
    lines = check(plan_text, base, Path(args.reports), Path(args.key) / "answers.json", base / "media")
    for ok, line in lines:
        print(f"{'PASS' if ok else 'FAIL'} {line}")
    ok = all(ok for ok, _ in lines)
    print("eval-check: ok" if ok else "eval-check: failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
