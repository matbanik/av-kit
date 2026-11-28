"""Session 106 remote run check (task rows 7 and 17; implementation-plan.md §Verification Plan 3,
``HOST_PAYLOAD``).

Usage: ``run-check.py CONSOLE (--expect-red ID ... | --expect-green) [--require-main ID ...]
[--install passed] [--require-install ID ...]`` or ``--selftest``.

``CONSOLE`` is the console receipt of ``tools/e2e_remote.py run``. Its last
``e2e-remote: <reason> exit=<n> run=<id> receipts=<dir>`` line names the receipts folder, which
holds ``summary.json`` and the main stage's ``host/report.json``. Exit 22 (``host-busy``) and 23
(``host-locked``) are never accepted: they mean wait and run the cell again.

* ``--expect-red ID``: the reason is ``new-failures`` (exit 40), the AC ids of the new failures
  are exactly the IDs given, and each of their tests fails with an assertion message
  (``expect``), or is skipped in a serial file after such a failure in the same file (D-1574:
  Playwright's serial mode does not run the rest of the file after its first failure).
* ``--expect-green``: the reason is ``ok`` and the exit 0.
* ``--require-main ID``: the main stage's report holds a test with that AC id, and every such
  test passed.
* ``--install passed``: the summary's ``install`` block has ``state: ran`` (the shape
  ``tools/e2e_remote.py`` writes, D-1574), with every test passed, none skipped, unexpected or
  flaky.
* ``--require-install ID``: the install stage's ``host/install/report.json`` holds a test with
  that AC id, and every such test passed.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import tempfile

LINE = re.compile(
    r"^e2e-remote: (?P<reason>[a-z-]+) exit=(?P<exit>\d+) run=(?P<run>\S+)"
    r" receipts=(?P<dir>.+?)\s*$"
)
AC = re.compile(r"^AC-\d+\.\d+$")
WAIT = {22: "host-busy", 23: "host-locked"}


def last_line(console: pathlib.Path) -> re.Match[str] | None:
    text = console.read_bytes().decode("utf-8", "replace").lstrip("﻿")
    found = None
    for line in text.splitlines():
        m = LINE.match(line.strip())
        if m:
            found = m
    return found


def report_rows(report: pathlib.Path) -> list[dict]:
    rows: list[dict] = []

    def walk(suites: list, file: str = "") -> None:
        for s in suites:
            here = str(s.get("file") or file)
            for spec in s.get("specs") or []:
                title = str(spec.get("title", ""))
                first = title.split(maxsplit=1)[0] if title.split() else ""
                for t in spec.get("tests") or []:
                    msgs = [
                        str((r.get("error") or {}).get("message", ""))
                        for r in t.get("results") or []
                    ]
                    rows.append(
                        {
                            "ac": first if AC.fullmatch(first) else None,
                            "title": title,
                            "status": t.get("status"),
                            "message": next((m for m in msgs if m), ""),
                            "file": str(spec.get("file") or here),
                        }
                    )
            walk(s.get("suites") or [], here)

    walk(json.loads(report.read_text(encoding="utf-8-sig")).get("suites") or [])
    return rows


def check(console: pathlib.Path, opts: dict) -> list[str]:
    m = last_line(console)
    if m is None:
        return [f"run-check: no e2e-remote line in {console}"]
    reason, code, folder = m["reason"], int(m["exit"]), pathlib.Path(m["dir"])
    print(f"run-check: reason={reason} exit={code} run={m['run']} receipts={folder}")
    if code in WAIT:
        return [
            f"run-check: exit {code} ({WAIT[code]}) is never a pass; wait and run the cell again"
        ]
    summary_p = folder / "summary.json"
    if not summary_p.is_file():
        return [f"run-check: {summary_p} missing"]
    summary = json.loads(summary_p.read_text(encoding="utf-8-sig"))
    problems: list[str] = []
    if summary.get("exit") != code or summary.get("result", reason) != reason:
        said = f"{summary.get('result')} exit={summary.get('exit')}"
        problems.append(f"run-check: summary says {said}, console says {reason} exit={code}")
    report_p = folder / "host" / "report.json"
    rows = report_rows(report_p) if report_p.is_file() else []
    if opts["red"]:
        if (reason, code) != ("new-failures", 40):
            problems.append(f"run-check: expected new-failures exit=40, got {reason} exit={code}")
        new = summary.get("new") or []
        got = sorted({str(n.get("ac")) for n in new})
        if got != sorted(set(opts["red"])):
            problems.append(
                f"run-check: new failures are {got}, expected exactly {sorted(set(opts['red']))}"
            )
        asserted = {
            r["file"]
            for r in rows
            if r["status"] == "unexpected" and re.search(r"expect", r["message"], re.IGNORECASE)
        }
        for ac in sorted(set(opts["red"])):
            mine = [r for r in rows if r["ac"] == ac]
            if not mine:
                problems.append(f"run-check: {ac} has no test in {report_p}")
            for r in mine:
                if r["status"] == "unexpected":
                    if not re.search(r"expect", r["message"], re.IGNORECASE):
                        msg = r["message"][:120]
                        problems.append(
                            f"run-check: {ac} failed without an assertion message: {msg!r}"
                        )
                    else:
                        first = r["message"].splitlines()[0][:120] if r["message"] else ""
                        print(f"run-check red {ac}: {first}")
                elif r["status"] == "skipped" and r["file"] in asserted:
                    print(f"run-check red {ac}: not run (serial, after an assertion failure)")
                else:
                    problems.append(f"run-check: {ac} test is {r['status']}: {r['title'][:90]}")
    if opts["green"] and (reason, code) != ("ok", 0):
        problems.append(f"run-check: expected ok exit=0, got {reason} exit={code}")
    for ac in opts["main"]:
        hits = [r for r in rows if r["ac"] == ac]
        if not hits or any(r["status"] != "expected" for r in hits):
            problems.append(
                f"run-check: main stage {ac} is {[r['status'] for r in hits] or 'absent'}"
            )
        else:
            print(f"run-check main {ac}: passed ({len(hits)})")
    inst = summary.get("install")
    if opts["install"] == "passed":
        if not isinstance(inst, dict) or inst.get("state") != "ran":
            state = inst.get("state") if isinstance(inst, dict) else inst
            problems.append(f"run-check: install stage is {state}")
        else:
            bad = {k: inst.get(k) for k in ("unexpected", "skipped", "flaky") if inst.get(k)}
            if bad or not inst.get("expected") or inst.get("expected") != inst.get("tests"):
                problems.append(f"run-check: install stage counts {inst}")
            else:
                print(f"run-check install: {inst.get('expected')} passed")
    inst_p = folder / "host" / "install" / "report.json"
    inst_rows = report_rows(inst_p) if inst_p.is_file() else []
    for ac in opts["install_req"]:
        hits = [r for r in inst_rows if r["ac"] == ac]
        if not hits or any(r["status"] != "expected" for r in hits):
            problems.append(
                f"run-check: install stage {ac} is {[r['status'] for r in hits] or 'absent'}"
            )
        else:
            print(f"run-check install {ac}: passed")
    return problems


def parse(argv: list[str]) -> tuple[pathlib.Path, dict]:
    if not argv or argv[0].startswith("--"):
        raise ValueError("CONSOLE first")
    opts: dict = {"red": [], "green": False, "main": [], "install": None, "install_req": []}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--expect-green":
            opts["green"] = True
            i += 1
            continue
        if i + 1 >= len(argv):
            raise ValueError(f"{a} needs a value")
        v = argv[i + 1]
        key = {
            "--expect-red": "red",
            "--require-main": "main",
            "--require-install": "install_req",
        }.get(a)
        if key:
            if not AC.fullmatch(v):
                raise ValueError(f"{a} {v}: not an AC id")
            opts[key].append(v)
        elif a == "--install" and v == "passed":
            opts["install"] = v
        else:
            raise ValueError(f"unknown option {a} {v}")
        i += 2
    if bool(opts["red"]) == opts["green"]:
        raise ValueError("exactly one of --expect-red and --expect-green")
    return pathlib.Path(argv[0]), opts


def _spec(ac: str, status: str, message: str = "", file: str = "a.test.ts") -> dict:
    res = [{"error": {"message": message}}] if message else [{}]
    return {"title": f"{ac} a test", "file": file, "tests": [{"status": status, "results": res}]}


def selftest() -> int:
    def fixture(
        tmp: pathlib.Path,
        tag: str,
        reason: str,
        code: int,
        specs: list[dict],
        new: list[str],
        install,
    ) -> pathlib.Path:
        folder = tmp / tag
        (folder / "host" / "install").mkdir(parents=True)
        summary = {"result": reason, "exit": code, "new": [{"ac": a} for a in new]}
        if isinstance(install, dict):
            items = install.get("items") or []
            install = {k: v for k, v in install.items() if k != "items"}
            ispecs = [_spec(i["ac"], i["status"], file="i.test.ts") for i in items]
            (folder / "host" / "install" / "report.json").write_text(
                json.dumps({"suites": [{"specs": ispecs}]}), encoding="utf-8"
            )
        if install is not None:
            summary["install"] = install
        (folder / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
        (folder / "host" / "report.json").write_text(
            json.dumps({"suites": [{"specs": specs}]}), encoding="utf-8"
        )
        console = tmp / f"{tag}.txt"
        console.write_text(
            f"noise\ne2e-remote: {reason} exit={code} run=r1 receipts={folder}\n", encoding="utf-8"
        )
        return console

    passed = {
        "state": "ran",
        "tests": 1,
        "expected": 1,
        "unexpected": 0,
        "skipped": 0,
        "flaky": 0,
        "items": [{"ac": "AC-174.19", "status": "expected"}],
    }
    skipped = dict(passed, skipped=1, tests=2)
    red_specs = [
        _spec("AC-174.15", "unexpected", "Error: expect(received).toBe(expected)"),
        _spec("AC-174.16", "unexpected", "Error: expect(locator).toBeVisible() failed"),
        _spec("AC-1.1", "expected"),
    ]
    green_specs = [_spec("AC-174.15", "expected"), _spec("AC-174.16", "expected")]
    red = ["AC-174.15", "AC-174.16"]
    serial_specs = [
        _spec("AC-174.15", "unexpected", "Error: expect(locator).toBeVisible() failed"),
        _spec("AC-174.15", "skipped"),
        _spec("AC-174.16", "skipped"),
    ]
    cases = [
        (
            "red with serial skips after an assertion failure passes",
            "new-failures",
            40,
            serial_specs,
            ["AC-174.15", "AC-174.15", "AC-174.16"],
            passed,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16", "--install", "passed"],
            True,
        ),
        (
            "red with skips in another file fails",
            "new-failures",
            40,
            [serial_specs[0], _spec("AC-174.16", "skipped", file="b.test.ts")],
            red,
            passed,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16"],
            False,
        ),
        (
            "red with install passed passes",
            "new-failures",
            40,
            red_specs,
            red,
            passed,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16", "--install", "passed"],
            True,
        ),
        (
            "red with an extra new failure fails",
            "new-failures",
            40,
            red_specs,
            red + ["AC-1.1"],
            passed,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16"],
            False,
        ),
        (
            "red failing for setup fails",
            "new-failures",
            40,
            [_spec("AC-174.15", "unexpected", "Error: launch timed out"), red_specs[1]],
            red,
            passed,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16"],
            False,
        ),
        (
            "red with install skipped fails",
            "new-failures",
            40,
            red_specs,
            red,
            skipped,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16", "--install", "passed"],
            False,
        ),
        (
            "host-busy is never a pass",
            "host-busy",
            22,
            red_specs,
            red,
            passed,
            ["--expect-red", "AC-174.15", "--expect-red", "AC-174.16"],
            False,
        ),
        (
            "host-locked is never a pass",
            "host-locked",
            23,
            green_specs,
            [],
            passed,
            ["--expect-green"],
            False,
        ),
        (
            "green with required tests passes",
            "ok",
            0,
            green_specs,
            [],
            passed,
            [
                "--expect-green",
                "--require-main",
                "AC-174.15",
                "--install",
                "passed",
                "--require-install",
                "AC-174.19",
            ],
            True,
        ),
        (
            "green missing a main test fails",
            "ok",
            0,
            green_specs[:1],
            [],
            passed,
            ["--expect-green", "--require-main", "AC-174.16"],
            False,
        ),
        (
            "green missing an install test fails",
            "ok",
            0,
            green_specs,
            [],
            passed,
            ["--expect-green", "--require-install", "AC-174.20"],
            False,
        ),
        (
            "install-failures exit 41 fails green",
            "install-failures",
            41,
            green_specs,
            [],
            dict(passed, state="ran", unexpected=1, expected=0),
            ["--expect-green", "--install", "passed"],
            False,
        ),
        (
            "install not run fails",
            "ok",
            0,
            green_specs,
            [],
            "not-run",
            ["--expect-green", "--install", "passed"],
            False,
        ),
    ]
    bad = 0
    with tempfile.TemporaryDirectory() as d:
        tmp = pathlib.Path(d)
        for n, (name, reason, code, specs, new, install, args, want) in enumerate(cases):
            console = fixture(tmp, f"c{n}", reason, code, specs, new, install)
            _, opts = parse([str(console), *args])
            got = check(console, opts)
            ok = (not got) == want
            bad += 0 if ok else 1
            print(f"selftest {'ok ' if ok else 'BAD'} {name}: {got}")
    for name, args in (
        ("both modes refused", ["x", "--expect-green", "--expect-red", "AC-1.1"]),
        ("bad AC refused", ["x", "--expect-red", "AC-x"]),
    ):
        try:
            parse(args)
            ok = False
        except ValueError:
            ok = True
        bad += 0 if ok else 1
        print(f"selftest {'ok ' if ok else 'BAD'} {name}")
    total = len(cases) + 2
    print(f"run-check selftest: {total - bad}/{total} ok")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    try:
        console, opts = parse(argv)
    except ValueError as exc:
        print(f"usage: {exc}\n{__doc__}")
        return 2
    problems = check(console, opts)
    for p in problems:
        print("PROBLEM:", p)
    print(f"run-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
