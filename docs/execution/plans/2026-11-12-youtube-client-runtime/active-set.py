"""Session 66's active MEU set (task.md §Split; plan §Plan-local scripts).

The split point after row 3 writes `active-meus.txt` in this folder: one LF line, either
`MEU-140 MEU-141` (both run here) or `MEU-140` (MEU-141 moves to Session 66b). Row 6, the
session gate, H1-3, H1-4, H1-6, H1-6a, H1-6b, H1-7 and H2-6 read the set through this script,
so every step agrees on one fact.

The file must agree with Mat's rulings in the plan's decision log:
  - D-640 D, D-642 D or D-641 B: only `MEU-140` (no solver, no fetch, or split now);
  - otherwise D-641 D: only `MEU-140 MEU-141` (no split point);
  - otherwise D-641 A: either (the coordinator's context reading after row 3).
An unruled decision, a missing file or any other content refuses (exit 1).

    active-set.py check     print the set, the issues and the deferred MEUs, and check task.md:
                            rows 1b, 4, 2b and 5 all `[B]` when MEU-141 moved, none otherwise
    active-set.py meus      print the active MEU ids, space-separated
    active-set.py issues    print the active issue ids, space-separated
    active-set.py deferred  print the deferred MEU ids (empty when none)
    active-set.py records   row 6's check: each active MEU ready_for_review and its issue
                            resolved, a deferred MEU pending and its issue open, tracker row 66
                            executed (plus one pending 66b row for a deferred MEU-141, none
                            otherwise), one `Delivered (Session 66)` note in 02 per active MEU
    active-set.py openapi BASE
                            H1-4's check: the committed snapshot against BASE's. With MEU-141:
                            JsRuntimeOut added, DependenciesOut gains only js_runtime,
                            SettingsPutIn gains only deno_path, nothing else changes. Without
                            it: no change at all.
    active-set.py --selftest
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
GROUPING = ".agent/context/grouping/2026-11-10-download-reliability-session-grouping.md"
PLAN_FOLDER = "docs/execution/plans/2026-11-12-youtube-client-runtime/"
NOTE = "Delivered (Session 66)"
FULL = ("MEU-140", "MEU-141")
SPLIT = ("MEU-140",)
ISSUES = {
    "MEU-140": "DOWNLOAD-CLIENT-PIN-MISSES-WORKING-CLIENT",
    "MEU-141": "YTDLP-NO-JS-RUNTIME",
}
LETTERS = {"D-640": "ABCD", "D-641": "ABD", "D-642": "ABD"}


class Refused(Exception):
    """The set can't be read, or it disagrees with the rulings."""


def rulings(plan_dir: Path) -> dict[str, str]:
    """Each decision's ruled letter, as baseline.ps1's rulings step reads it."""
    text = (plan_dir / "implementation-plan.md").read_text(encoding="utf-8")
    if "## Decision Log" not in text:
        raise Refused("the plan has no Decision Log")
    log = text[text.index("## Decision Log") :]
    found = {}
    for decision, letters in LETTERS.items():
        m = re.search(
            r"^  - id: " + decision + r"\n(.*?)(?=^  - id: |^```)", log, re.DOTALL | re.MULTILINE
        )
        if not m:
            raise Refused(f"{decision}: no entry in the decision log")
        chosen = re.search(r'^    chosen: "(.*)"$', m.group(1), re.MULTILINE)
        ref = re.search(r"^    human_message_reference: (.*)$", m.group(1), re.MULTILINE)
        head = chosen.group(1)[:2] if chosen else ""
        reference = ref.group(1).strip().strip("'\"") if ref else ""
        if not (len(head) == 2 and head[0] in letters and head[1] == ":"):
            raise Refused(f"{decision} is unruled (S14)")
        if not reference.startswith("USER_EXPLICIT "):
            raise Refused(f"{decision} has no USER_EXPLICIT reference (S14)")
        found[decision] = head[0]
    return found


def allowed(ruled: dict[str, str]) -> tuple[tuple[str, ...], ...]:
    """The sets the rulings permit."""
    if ruled["D-640"] == "D" or ruled["D-642"] == "D" or ruled["D-641"] == "B":
        return (SPLIT,)
    if ruled["D-641"] == "D":
        return (FULL,)
    return (FULL, SPLIT)


def active(plan_dir: Path) -> tuple[str, ...]:
    """The active set, checked against the rulings."""
    ruled = rulings(plan_dir)
    path = plan_dir / "active-meus.txt"
    if not path.is_file():
        raise Refused("active-meus.txt is absent; the split point (after row 3) writes it")
    raw = path.read_bytes()
    if raw not in (b"MEU-140 MEU-141\n", b"MEU-140\n"):
        raise Refused(f"active-meus.txt must be one LF line, 'MEU-140 MEU-141' or 'MEU-140'; it holds {raw[:60]!r}")
    meus = tuple(raw.decode("ascii").split())
    if meus not in allowed(ruled):
        raise Refused(f"active-meus.txt says {' '.join(meus)}, but rulings {ruled} allow only {[' '.join(s) for s in allowed(ruled)]}")
    return meus


DEFERRED_ROWS = ("1b", "4", "2b", "5")


def rows_problems(meus: tuple[str, ...], task: str) -> list[str]:
    """MEU-141's rows against the set: all `[B]` when it moved to 66b, none `[B]` otherwise."""
    status = {}
    for line in task.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) > 3 and cells[1] in DEFERRED_ROWS + ("3s",):
            if cells[1] in status:
                return [f"row {cells[1]} appears twice"]
            status[cells[1]] = cells[-2].strip("`")
    problems = [f"row {r} is missing" for r in DEFERRED_ROWS + ("3s",) if r not in status]
    blocked = "MEU-141" not in meus
    for row in DEFERRED_ROWS:
        if row in status and (status[row] == "[B]") != blocked:
            want = "[B]" if blocked else "not [B]"
            problems.append(f"row {row} is {status[row]}, want {want} for {' '.join(meus)}")
    return problems


def records_problems(
    meus: tuple[str, ...],
    meu_status: dict[str, str],
    issue_status: dict[str, str],
    grouping: str,
    notes: int,
) -> list[str]:
    """Row 6's records against the active set; an empty list passes."""
    problems = []
    for meu in FULL:
        want = "ready_for_review" if meu in meus else "pending"
        if meu_status.get(meu) != want:
            problems.append(f"{meu} is {meu_status.get(meu)!r}, want {want!r}")
        issue = ISSUES[meu]
        resolved = issue_status.get(issue) == "resolved"
        if resolved != (meu in meus):
            problems.append(f"{issue} is {issue_status.get(issue)!r}; resolved only when {meu} ran here")
    lines = grouping.splitlines()
    row66 = [ln for ln in lines if ln.startswith("| 66 |")]
    if len(row66) != 1 or "executed" not in row66[0] or PLAN_FOLDER not in row66[0]:
        problems.append(f"tracker row 66 must be one row, executed, naming {PLAN_FOLDER}: {row66}")
    row66b = [ln for ln in lines if ln.startswith("| 66b |")]
    if "MEU-141" in meus:
        if row66b:
            problems.append(f"no 66b row when MEU-141 ran here: {row66b}")
    elif len(row66b) != 1 or "MEU-141" not in row66b[0] or "pending" not in row66b[0]:
        problems.append(f"a deferred MEU-141 needs one pending 66b row naming it: {row66b}")
    if notes != len(meus):
        problems.append(f"02 holds {notes} '{NOTE}' note(s), want {len(meus)}")
    return problems


def records(meus: tuple[str, ...]) -> list[str]:
    """Read the records row 6 wrote and check them."""
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "tools"))
    from tools.issue_triage import model  # noqa: PLC0415
    from tools.meu_status.model import get_meu, load  # noqa: PLC0415

    data = load()
    meu_status = {m: get_meu(data, m)["status"] for m in FULL}
    register = model.load(ROOT / ".agent/context/known-issues.yaml")["issues"]
    issue_status = {i["id"]: i["status"] for i in register if i["id"] in ISSUES.values()}
    grouping = (ROOT / GROUPING).read_text(encoding="utf-8")
    notes = (ROOT / "docs/build-plan/02-infrastructure.md").read_text(encoding="utf-8").count(NOTE)
    print(f"meus: {meu_status} issues: {issue_status} 02 notes: {notes}")
    return records_problems(meus, meu_status, issue_status, grouping, notes)


def _without(schema: dict[str, Any], prop: str) -> dict[str, Any]:
    """SCHEMA with PROP taken out of its properties and its required list."""
    out = copy.deepcopy(schema)
    out.get("properties", {}).pop(prop, None)
    if prop in out.get("required", []):
        out["required"] = [r for r in out["required"] if r != prop]
    return out


def openapi_problems(meus: tuple[str, ...], base: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """The snapshot delta against the active set; an empty list passes."""
    if "MEU-141" not in meus:
        return [] if after == base else ["the snapshot changed, but MEU-141 did not run here"]
    problems = []
    bs, as_ = base["components"]["schemas"], after["components"]["schemas"]
    added = sorted(set(as_) - set(bs))
    removed = sorted(set(bs) - set(as_))
    changed = sorted(k for k in set(as_) & set(bs) if as_[k] != bs[k])
    if added != ["JsRuntimeOut"] or removed or changed != ["DependenciesOut", "SettingsPutIn"]:
        problems.append("schemas: want added ['JsRuntimeOut'], none removed, changed ['DependenciesOut', 'SettingsPutIn']")
    for name, prop in (("DependenciesOut", "js_runtime"), ("SettingsPutIn", "deno_path")):
        if name not in as_ or name not in bs:
            problems.append(f"{name} is missing")
            continue
        new = sorted(set(as_[name].get("properties", {})) - set(bs[name].get("properties", {})))
        if new != [prop]:
            problems.append(f"{name} gains {new}, want [{prop!r}]")
        if _without(as_[name], prop) != bs[name]:
            problems.append(f"{name} changed beyond {prop}")
    rest_after = {k: v for k, v in after.items() if k != "components"}
    rest_base = {k: v for k, v in base.items() if k != "components"}
    other_after = {k: v for k, v in after["components"].items() if k != "schemas"}
    other_base = {k: v for k, v in base["components"].items() if k != "schemas"}
    if rest_after != rest_base or other_after != other_base:
        problems.append("paths or other top-level parts changed")
    return problems


def openapi(meus: tuple[str, ...], base_sha: str) -> list[str]:
    """Read BASE's committed snapshot from git and the working one, and compare them."""
    shown = subprocess.run(
        ["git", "show", f"{base_sha}:openapi.committed.json"], cwd=ROOT, capture_output=True, check=True
    )
    base = json.loads(shown.stdout)
    after = json.loads((ROOT / "openapi.committed.json").read_text(encoding="utf-8"))
    names = (set(after["components"]["schemas"]) ^ set(base["components"]["schemas"]))
    print(f"schemas added or removed: {sorted(names)}")
    return openapi_problems(meus, base, after)


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    known = ("check", "meus", "issues", "deferred", "records")
    if not ((len(argv) == 1 and argv[0] in known) or (len(argv) == 2 and argv[0] == "openapi")):
        print(__doc__)
        return 2
    try:
        meus = active(HERE)
    except (Refused, OSError, UnicodeDecodeError) as exc:
        print(f"active-set refused: {exc}")
        return 1
    deferred = [m for m in FULL if m not in meus]
    issues = [ISSUES[m] for m in meus]
    if argv[0] in ("records", "openapi"):
        problems = records(meus) if argv[0] == "records" else openapi(meus, argv[1])
        print(f"active-set {argv[0]}: {' '.join(meus)}; {len(problems)} problem(s): {problems}")
        return 1 if problems else 0
    if argv[0] == "check":
        print(f"active-set: {' '.join(meus)}")
        print(f"issues: {' '.join(issues)}")
        print(f"deferred: {' '.join(deferred) or 'none'}")
        problems = rows_problems(meus, (HERE / "task.md").read_text(encoding="utf-8"))
        print(f"task rows: {len(problems)} problem(s): {problems}")
        if problems:
            return 1
    elif argv[0] == "meus":
        print(" ".join(meus))
    elif argv[0] == "issues":
        print(" ".join(issues))
    else:
        print(" ".join(deferred))
    return 0


def _plan(d640: str | None, d641: str | None, d642: str | None, ref: str = "USER_EXPLICIT 2026-11-12 'x'") -> str:
    out = ["## Decision Log", "", "```yaml", "decisions:"]
    for decision, letter in (("D-640", d640), ("D-641", d641), ("D-642", d642)):
        out.append(f"  - id: {decision}")
        out.append("    stage: planning")
        out.append(f'    chosen: "{letter}: words"' if letter else "    chosen: null")
        out.append(f'    human_message_reference: "{ref}"' if letter else "    human_message_reference: null")
    out.append("```")
    return "\n".join(out) + "\n"


def selftest() -> int:
    cases = [
        # (d640, d641, d642, file bytes or None, expected set or None for refused)
        ("A", "A", "A", b"MEU-140 MEU-141\n", FULL),
        ("A", "A", "A", b"MEU-140\n", SPLIT),
        ("B", "D", "A", b"MEU-140 MEU-141\n", FULL),
        ("A", "D", "B", b"MEU-140\n", None),
        ("A", "B", "A", b"MEU-140\n", SPLIT),
        ("A", "B", "A", b"MEU-140 MEU-141\n", None),
        ("D", "A", "A", b"MEU-140\n", SPLIT),
        ("D", "D", "A", b"MEU-140 MEU-141\n", None),
        ("A", "A", "D", b"MEU-140\n", SPLIT),
        ("A", "D", "D", b"MEU-140 MEU-141\n", None),
        ("C", "A", "B", b"MEU-140 MEU-141\n", FULL),
        ("A", "A", "A", None, None),
        ("A", "A", "A", b"MEU-140 MEU-141\r\n", None),
        ("A", "A", "A", b"MEU-140 MEU-141", None),
        ("A", "A", "A", b"MEU-141\n", None),
        ("A", "A", "A", b"", None),
        (None, "A", "A", b"MEU-140\n", None),
        ("A", "C", "A", b"MEU-140\n", None),
        ("E", "A", "A", b"MEU-140\n", None),
    ]
    wrong = []
    with tempfile.TemporaryDirectory(dir="C:/Temp/av-kit") as tmp:
        for index, (d640, d641, d642, data, want) in enumerate(cases):
            plan_dir = Path(tmp, str(index))
            plan_dir.mkdir()
            (plan_dir / "implementation-plan.md").write_text(_plan(d640, d641, d642), encoding="utf-8", newline="\n")
            if data is not None:
                (plan_dir / "active-meus.txt").write_bytes(data)
            try:
                got = active(plan_dir)
            except Refused:
                got = None
            if got != want:
                wrong.append((index, d640, d641, d642, data, want, got))
        plan_dir = Path(tmp, "noref")
        plan_dir.mkdir()
        (plan_dir / "implementation-plan.md").write_text(_plan("A", "A", "A", ref="said A"), encoding="utf-8", newline="\n")
        (plan_dir / "active-meus.txt").write_bytes(b"MEU-140\n")
        try:
            active(plan_dir)
            wrong.append(("noref", "accepted a reference without USER_EXPLICIT"))
        except Refused:
            pass
    count = len(cases) + 1
    count += _selftest_rows(wrong)
    count += _selftest_records(wrong)
    count += _selftest_openapi(wrong)
    print(f"active-set selftest: {count} fixture(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def _selftest_rows(wrong: list[Any]) -> int:
    def table(statuses: dict[str, str]) -> str:
        head = "| # | Task | Status |\n|---|---|---|\n| 3 | x | `[x]` |\n"
        return head + "".join(f"| {r} | x {r} | `{s}` |\n" for r, s in statuses.items())

    done = {"3s": "[x]", "4": "[x]", "1b": "[x]", "2b": "[x]", "5": "[x]"}
    held = {"3s": "[x]", "4": "[B]", "1b": "[B]", "2b": "[B]", "5": "[B]"}
    cases = [
        (FULL, table(done), True),
        (SPLIT, table(held), True),
        (FULL, table({**done, "5": "[ ]"}), True),
        (FULL, table(held), False),
        (SPLIT, table(done), False),
        (SPLIT, table({**held, "2b": "[x]"}), False),
        (FULL, table({**done, "1b": "[B]"}), False),
        (SPLIT, table({k: v for k, v in held.items() if k != "1b"}), False),
        (FULL, table({k: v for k, v in done.items() if k != "3s"}), False),
        (FULL, table(done) + "| 4 | again | `[x]` |\n", False),
    ]
    for index, (meus, task, ok) in enumerate(cases):
        got = not rows_problems(meus, task)
        if got != ok:
            wrong.append(("rows", index, ok, got))
    return len(cases)


def _selftest_records(wrong: list[Any]) -> int:
    done = {"MEU-140": "ready_for_review", "MEU-141": "ready_for_review"}
    split = {"MEU-140": "ready_for_review", "MEU-141": "pending"}
    both = {ISSUES["MEU-140"]: "resolved", ISSUES["MEU-141"]: "resolved"}
    one = {ISSUES["MEU-140"]: "resolved", ISSUES["MEU-141"]: "open"}
    row = f"| 66 | `youtube-client-runtime` | MEU-140, MEU-141 | P2 | executed | `{PLAN_FOLDER}` |"
    pend = "| 66 | `youtube-client-runtime` | MEU-140, MEU-141 | P2 | pending | — |"
    row_b = "| 66b | `ytdlp-js-runtime` | MEU-141 | P2 | pending | — |"
    g_full = f"| 65 | x |\n{row}\n| 67 | y |\n"
    g_split = f"| 65 | x |\n{row}\n{row_b}\n| 67 | y |\n"
    cases = [
        (FULL, done, both, g_full, 2, True),
        (SPLIT, split, one, g_split, 1, True),
        (FULL, split, both, g_full, 2, False),
        (SPLIT, done, one, g_split, 1, False),
        (FULL, done, one, g_full, 2, False),
        (SPLIT, split, both, g_split, 1, False),
        (FULL, done, both, g_split, 2, False),
        (SPLIT, split, one, g_full, 1, False),
        (FULL, done, both, g_full.replace(row, pend), 2, False),
        (FULL, done, both, g_full + row + "\n", 2, False),
        (FULL, done, both, g_full, 1, False),
        (SPLIT, split, one, g_split, 2, False),
        (SPLIT, split, one, g_split.replace("pending | — |\n| 67", "executed | — |\n| 67"), 1, False),
    ]
    for index, (meus, ms, iss, grouping, notes, ok) in enumerate(cases):
        got = not records_problems(meus, ms, iss, grouping, notes)
        if got != ok:
            wrong.append(("records", index, ok, got))
    return len(cases)


def _selftest_openapi(wrong: list[Any]) -> int:
    base = {
        "openapi": "3.1.0",
        "paths": {"/health/dependencies": {"get": {}}},
        "components": {
            "schemas": {
                "DependenciesOut": {"properties": {"ffmpeg": {}}, "required": ["ffmpeg"]},
                "SettingsPutIn": {"properties": {"ffmpeg_path": {}}},
                "Other": {"properties": {"a": {}}},
            },
            "securitySchemes": {"bearer": {}},
        },
    }
    good = copy.deepcopy(base)
    good["components"]["schemas"]["JsRuntimeOut"] = {"properties": {"available": {}}}
    good["components"]["schemas"]["DependenciesOut"]["properties"]["js_runtime"] = {}
    good["components"]["schemas"]["SettingsPutIn"]["properties"]["deno_path"] = {}

    def variant(fn: Any) -> dict[str, Any]:
        out = copy.deepcopy(good)
        fn(out)
        return out

    s = "components"
    cases = [
        (FULL, good, True),
        (SPLIT, base, True),
        (SPLIT, good, False),
        (FULL, base, False),
        (FULL, variant(lambda o: o[s]["schemas"]["SettingsPutIn"]["properties"].pop("deno_path")), False),
        (FULL, variant(lambda o: o[s]["schemas"]["Other"]["properties"].update(b={})), False),
        (FULL, variant(lambda o: o[s]["schemas"]["DependenciesOut"]["properties"].update(extra={})), False),
        (FULL, variant(lambda o: o[s]["schemas"]["DependenciesOut"].update(required=["ffmpeg", "js_runtime"])), True),
        (FULL, variant(lambda o: o[s]["schemas"]["DependenciesOut"].update(required=[])), False),
        (FULL, variant(lambda o: o["paths"].update({"/x": {}})), False),
        (FULL, variant(lambda o: o[s]["securitySchemes"].update(other={})), False),
        (FULL, variant(lambda o: o[s]["schemas"].update(Extra={})), False),
        (FULL, variant(lambda o: o[s]["schemas"].pop("Other")), False),
        (SPLIT, {**copy.deepcopy(base), "paths": {}}, False),
    ]
    for index, (meus, after, ok) in enumerate(cases):
        got = not openapi_problems(meus, base, after)
        if got != ok:
            wrong.append(("openapi", index, ok, got))
    return len(cases)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
