"""Session 98 session-probe checks (task rows 0, 5 and 7 and the gate's ``probe-block`` and
``probe-local`` steps; implementation-plan.md §The session probe; AC-6, AC-7, AC-12 and AC-18;
D-1270, D-1271, D-1273, D-1274, D-1280, D-1281).

The probe is one PowerShell block between ``# begin session-probe`` and ``# end session-probe``,
the same bytes in each of ``PROBE_COPIES`` under ``tools/e2e_host/``. It defines
``AvProbeFacts`` (live reads), ``AvProbeClassify`` (a pure function of the facts) and
``AvSessionProbe`` (both). This script never runs ``ssh`` or ``scp`` and writes nothing on any
host. Usage, from the repository root::

    python probe-check.py --block            # the block exists, is identical in every copy
    python probe-check.py --local OUT.json   # run the block on this PC (limited view), write OUT
    python probe-check.py --judge RECEIPT    # read the check receipt's session-probe line
    python probe-check.py --judge-gate SUMMARY   # read the row-8 run's gated probes (D-1280)
    python probe-check.py --selftest         # extraction and judging on fixtures

``--local`` runs Windows PowerShell 5.1 with ``-EncodedCommand`` (the block plus one
``ConvertTo-Json`` line), so nothing is copied anywhere; OUT is created exclusively. Its JSON
must hold a state in ``PROBE_STATES`` and a reason that belongs to that state; any state passes,
because the dev PC is not the host the gate protects (its value is recorded, not judged).

``--judge`` reads the ``session-probe:`` line ``tools/e2e_remote.py check`` prints from
``host-facts.ps1`` (the elevated SSH view of the mini-air) and decides the split flag (D-1274):

* exit 0: the probe read the host (``none``, ``connected-*`` or ``undecided-rustdesk-other``);
* exit 3: the fallback fires (``undecided-probe-failed`` or ``undecided-unreadable``: the
  elevated view must read every command line);
* exit 1: no line, two lines, or a state or reason outside the closed lists.

That view is provisional (D-1280): the probe that gates the stage runs inside the scheduled
task, at run level Limited in the desktop session, and may see less than the elevated view.
``--judge-gate`` reads the row-8 ``summary.json``'s ``gated.probe_before`` and
``gated.probe_after`` (the full objects the launcher wrote, each proc carrying ``started``,
D-1281) and its ``gated.outcome``:

* exit 3: either probe's reason is ``undecided-probe-failed`` or ``undecided-unreadable``. The
  flag flips to ``fallback`` (trigger ``limited-unreadable``), and row 8 reruns once in the
  fallback form;
* exit 0: the flag is confirmed. It prints ``ungated: resolve`` for ``run``,
  ``skipped-connected`` and ``voided-connected-during``, and ``ungated: open`` for
  ``skipped-undecided`` and ``voided-undecided-during`` (D-1280: UNGATED stays open, with the
  receipt cited and the reason named);
* exit 1: no ``gated`` object, an outcome outside ``GATED_OUTCOMES``, a probe that is not a
  valid object, a proc without the five keys, or an outcome its before probe contradicts (S11).
"""

from __future__ import annotations

import base64
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HOST = pathlib.Path("tools/e2e_host")
PROBE_COPIES = ("host-facts.ps1", "host-status.ps1", "run-e2e.ps1")
BEGIN = "# begin session-probe\n"
END = "# end session-probe\n"
PROBE_STATES = ("none", "connected", "undecided")
PROBE_REASONS = {
    "none": ("no-remote-session",),
    "connected": ("connected-rustdesk-cm", "connected-rdp"),
    "undecided": ("undecided-probe-failed", "undecided-unreadable", "undecided-rustdesk-other"),
}
FALLBACK = ("undecided-probe-failed", "undecided-unreadable")
GATED_OUTCOMES = (
    "run",
    "skipped-connected",
    "skipped-undecided",
    "voided-connected-during",
    "voided-undecided-during",
)
RESOLVES = ("run", "skipped-connected", "voided-connected-during")
PROC_KEYS = ("name", "readable", "session", "started", "switches")
#: The before probe's state each outcome requires.
OUTCOME_BEFORE = {
    "run": "none",
    "skipped-connected": "connected",
    "skipped-undecided": "undecided",
    "voided-connected-during": "none",
    "voided-undecided-during": "none",
}
LINE = re.compile(r"^session-probe: state=(\S+) reason=(\S+)(?: .*)?$", re.M)


def block_of(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("needs exactly one begin and one end marker")
    start = text.index(BEGIN)
    end = text.index(END)
    if end < start:
        raise ValueError("end marker before begin marker")
    return text[start : end + len(END)]


def check_blocks(folder: pathlib.Path) -> list[str]:
    problems: list[str] = []
    blocks: dict[str, str] = {}
    for name in PROBE_COPIES:
        path = folder / name
        if not path.is_file():
            problems.append(f"{name}: missing")
            continue
        raw = path.read_bytes()
        if b"\r" in raw or any(b > 127 for b in raw):
            problems.append(f"{name}: not ASCII LF")
            continue
        try:
            blocks[name] = block_of(raw.decode("ascii"))
        except ValueError as exc:
            problems.append(f"{name}: {exc}")
    for fn in ("function AvProbeFacts", "function AvProbeClassify", "function AvSessionProbe"):
        for name, text in blocks.items():
            if fn not in text:
                problems.append(f"{name}: the block does not define {fn.split()[1]}")
    if len(set(blocks.values())) > 1:
        problems.append("the block differs between " + ", ".join(sorted(blocks)))
    return problems


def shape_problems(obj: object) -> list[str]:
    if not isinstance(obj, dict):
        return ["not a JSON object"]
    state, reason = obj.get("state"), obj.get("reason")
    if state not in PROBE_STATES:
        return [f"state {state!r} not in {PROBE_STATES}"]
    if reason not in PROBE_REASONS[state]:
        return [f"reason {reason!r} does not belong to state {state}"]
    return []


def probe_problems(obj: object, label: str) -> list[str]:
    """A full probe object: a valid state and reason, and procs that each hold the five keys."""
    problems = [f"{label}: {p}" for p in shape_problems(obj)]
    if problems or not isinstance(obj, dict):
        return problems
    procs = obj.get("procs")
    if not isinstance(procs, list):
        return [f"{label}: procs is not a list"]
    for i, proc in enumerate(procs):
        if not isinstance(proc, dict) or tuple(sorted(proc)) != PROC_KEYS:
            problems.append(f"{label}: proc {i} does not hold exactly {PROC_KEYS}")
    return problems


def judge_gate(summary: object) -> tuple[int, str]:
    gated = summary.get("gated") if isinstance(summary, dict) else None
    if not isinstance(gated, dict):
        return 1, "no gated object in the summary"
    outcome = gated.get("outcome")
    if outcome not in GATED_OUTCOMES:
        return 1, f"outcome {outcome!r} not in {GATED_OUTCOMES}"
    before, after = gated.get("probe_before"), gated.get("probe_after")
    problems = probe_problems(before, "probe_before")
    ran = OUTCOME_BEFORE[outcome] == "none"
    if ran:
        problems += probe_problems(after, "probe_after")
    elif after is not None:
        problems.append("probe_after: present although the stage did not run")
    if problems:
        return 1, problems[0]
    reasons = [p["reason"] for p in (before, after) if isinstance(p, dict)]
    flip = [r for r in reasons if r in FALLBACK]
    if flip:
        return 3, f"fallback: the gating probe returned {flip[0]} (trigger limited-unreadable)"
    if before["state"] != OUTCOME_BEFORE[outcome]:
        return 1, f"outcome {outcome} contradicts the before probe's state {before['state']}"
    word = "resolve" if outcome in RESOLVES else "open"
    return 0, f"ungated: {word} (outcome {outcome}, reason {gated.get('reason')})"


def judge(text: str) -> tuple[int, str]:
    hits = LINE.findall(text)
    if len(hits) != 1:
        return 1, f"{len(hits)} session-probe line(s); exactly one expected"
    state, reason = hits[0]
    problems = shape_problems({"state": state, "reason": reason})
    if problems:
        return 1, problems[0]
    if reason in FALLBACK:
        return 3, f"fallback: the elevated probe returned {reason} (D-1274)"
    return 0, f"probe read the host: {state} {reason}"


def run_local(out: pathlib.Path) -> int:
    problems = check_blocks(HOST)
    if problems:
        print("probe-check: block:", "; ".join(problems))
        return 1
    block = block_of((HOST / PROBE_COPIES[0]).read_text(encoding="ascii"))
    script = (
        "$ErrorActionPreference = 'Continue'\n$ProgressPreference = 'SilentlyContinue'\n"
        + block
        + "ConvertTo-Json -InputObject (AvSessionProbe) -Depth 8 -Compress\n"
    )
    enc = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    r = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-EncodedCommand", enc],
        capture_output=True,
        text=True,
        stdin=subprocess.DEVNULL,
        timeout=180,
    )
    lines = [ln for ln in r.stdout.splitlines() if ln.startswith("{")]
    if r.returncode != 0 or not lines:
        print(f"probe-check: local run exit {r.returncode}, no JSON line")
        return 1
    obj = json.loads(lines[-1])
    with out.open("x", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    problems = probe_problems(obj, "local")
    print(f"probe-check: local state={obj.get('state')} reason={obj.get('reason')}")
    for p in problems:
        print("probe-check:", p)
    return 1 if problems else 0


JUDGE_CASES = (
    ("none", "session-probe: state=none reason=no-remote-session rustdesk=1.4.5\n", 0),
    ("cm", "x\nsession-probe: state=connected reason=connected-rustdesk-cm rustdesk=1.4.5\n", 0),
    ("rdp", "session-probe: state=connected reason=connected-rdp\n", 0),
    ("other", "session-probe: state=undecided reason=undecided-rustdesk-other\n", 0),
    ("failed", "session-probe: state=undecided reason=undecided-probe-failed\n", 3),
    ("unreadable", "session-probe: state=undecided reason=undecided-unreadable\n", 3),
    ("absent", "facts: ps=5.1\n", 1),
    ("two", "session-probe: state=none reason=no-remote-session\n" * 2, 1),
    ("wrong-pair", "session-probe: state=none reason=connected-rdp\n", 1),
    ("unknown-state", "session-probe: state=maybe reason=no-remote-session\n", 1),
)


def _probe(reason: str, procs: list | None = None) -> dict:
    state = reason.split("-")[0] if reason != "no-remote-session" else "none"
    tray = {
        "name": "rustdesk.exe",
        "session": 1,
        "switches": "--tray",
        "readable": True,
        "started": "2026-11-20T08:00:00Z",
    }
    return {
        "state": state,
        "reason": reason,
        "rustdesk_version": "1.4.5",
        "utc": "2026-11-21T00:00:00Z",
        "procs": procs if procs is not None else [tray],
    }


def _gate(outcome: str, before: str, after: str | None) -> dict:
    gated = {"outcome": outcome, "reason": before, "probe_before": _probe(before)}
    gated["probe_after"] = _probe(after) if after else None
    return {"gated": gated}


GATE_CASES = (
    ("run", _gate("run", "no-remote-session", "no-remote-session"), 0, "resolve"),
    ("skip-cm", _gate("skipped-connected", "connected-rustdesk-cm", None), 0, "resolve"),
    ("skip-other", _gate("skipped-undecided", "undecided-rustdesk-other", None), 0, "open"),
    (
        "void-cm",
        _gate("voided-connected-during", "no-remote-session", "connected-rustdesk-cm"),
        0,
        "resolve",
    ),
    (
        "void-other",
        _gate("voided-undecided-during", "no-remote-session", "undecided-rustdesk-other"),
        0,
        "open",
    ),
    ("limited-before", _gate("skipped-undecided", "undecided-unreadable", None), 3, ""),
    ("failed-before", _gate("skipped-undecided", "undecided-probe-failed", None), 3, ""),
    (
        "limited-after",
        _gate("voided-undecided-during", "no-remote-session", "undecided-unreadable"),
        3,
        "",
    ),
    ("no-gated", {"tests": 237}, 1, ""),
    ("bad-outcome", _gate("passed", "no-remote-session", "no-remote-session"), 1, ""),
    ("no-after", _gate("run", "no-remote-session", None), 1, ""),
    ("contradicts", _gate("skipped-connected", "undecided-rustdesk-other", None), 1, ""),
)


def selftest() -> int:
    wrong: list[str] = []
    for name, summary, want, word in GATE_CASES:
        got, why = judge_gate(summary)
        print(f"judge-gate {name}: exit {got} (expected {want}) {why}")
        if got != want or (word and f"ungated: {word} " not in why):
            wrong.append(f"judge-gate-{name}")
    no_started = _gate("run", "no-remote-session", "no-remote-session")
    del no_started["gated"]["probe_before"]["procs"][0]["started"]
    got, why = judge_gate(no_started)
    print(f"judge-gate no-started: exit {got} (expected 1) {why}")
    if got != 1:
        wrong.append("judge-gate-no-started")
    for name, text, want in JUDGE_CASES:
        got, why = judge(text)
        print(f"judge {name}: exit {got} (expected {want}) {why}")
        if got != want:
            wrong.append(f"judge-{name}")
    body = (
        BEGIN
        + "function AvProbeFacts { }\nfunction AvProbeClassify($f) { }\n"
        + "function AvSessionProbe { }\n"
        + END
    )
    with tempfile.TemporaryDirectory() as tmp:
        folder = pathlib.Path(tmp)
        for n in PROBE_COPIES:
            (folder / n).write_bytes(("# head\n" + body + "# tail\n").encode("ascii"))
        cases = [("identical", [], True)]
        cases.append(("one-differs", [(PROBE_COPIES[2], body.replace("{ }", "{ 1 }", 1))], False))
        cases.append(("no-marker", [(PROBE_COPIES[1], "# nothing\n")], False))
        cases.append(("crlf", [(PROBE_COPIES[0], body.replace("\n", "\r\n"))], False))
        cases.append(
            ("no-classify", [(PROBE_COPIES[0], body.replace("AvProbeClassify", "X"))], False)
        )
        for name, edits, want in cases:
            for n in PROBE_COPIES:
                (folder / n).write_bytes(("# head\n" + body + "# tail\n").encode("ascii"))
            for n, text in edits:
                (folder / n).write_bytes(text.encode("ascii"))
            problems = check_blocks(folder)
            passed = not problems
            print(f"block {name}: {'pass' if passed else 'refused'} {problems[:1]}")
            if passed != want:
                wrong.append(f"block-{name}")
    total = len(JUDGE_CASES) + 5 + len(GATE_CASES) + 1
    print(f"probe-check selftest: {total} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv == ["--block"]:
        problems = check_blocks(HOST)
        for p in problems:
            print("probe-check:", p)
        print(f"probe-check: {len(PROBE_COPIES)} copies, {len(problems)} problem(s)")
        return 1 if problems else 0
    if len(argv) == 2 and argv[0] == "--local":
        return run_local(pathlib.Path(argv[1]))
    if len(argv) == 2 and argv[0] == "--judge":
        code, why = judge(pathlib.Path(argv[1]).read_text(encoding="utf-8", errors="replace"))
        print("probe-check:", why)
        return code
    if len(argv) == 2 and argv[0] == "--judge-gate":
        try:
            summary = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            print(f"probe-check: cannot read {argv[1]}: {exc}")
            return 1
        code, why = judge_gate(summary)
        print("probe-check:", why)
        return code
    print(
        "usage: probe-check.py --block | --local OUT | --judge RECEIPT | --judge-gate SUMMARY"
        " | --selftest"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
