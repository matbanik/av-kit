"""Session 100 guard-log check: the clipboard guard's verdict without app.close() (D-1321, AC-21).

The guard preload (``ui/tests/e2e/clipboard-guard.cjs``) appends each recorded call to its launch's
log at call time. With a diag folder set (``AVKIT_E2E_DIAG_DIR``: flake-run's
``<out>/epf-<label>-<i>-diag-<inv>``, or the host's ``<results>/diag``, which comes back as
``<run dir>/host/diag``), that log is ``<diag>/clipboard-<launch>.jsonl``, beside the
``phases.jsonl`` rows of the same launch (``clipboardGuardLogPath``, electron-env.ts). This check
reads only the folders it is named::

    python guard-logs.py --diag DIR                  # one folder (row 8's host/diag)
    python guard-logs.py --receipt FILE [--out DIR]  # every run and rerun folder a flake-run
                                                     # receipt names, under --out
    python guard-logs.py --selftest

For each folder it takes the launches from the ``launch-start`` rows of ``phases.jsonl`` and fails
on any of:

- a recorded-call line (``{"call": ...}``) in any launch's log, but the AC-10 launch's;
- a ``failed`` line (the guard could not replace or check a name, and the launch failed closed);
- a launch that reached ``launch-end`` without exactly one ``installed`` line, unless its file is
  a gated file (``tools/e2e_host/known-failures.json``, or ``--gated``) with no log at all, as the
  gated stage runs unguarded (``AVKIT_E2E_CLIPBOARD_GATED=1``);
- a line that is not a JSON object, or a log no ``launch-start`` row names (an orphan);
- the AC-10 launch (file ``clipboard-guard.test.ts``, title starting ``S100 AC-10``) not holding
  exactly ``main writeText``, ``renderer writeText`` and ``webContents copy``, once each;
- no AC-10 launch in a run folder or a ``--diag`` folder (a rerun folder may hold none).

It counts and prints the launches with no ``installed`` line (unfinished launches, gated ones and
failures apart). Exit 0 when no folder fails, 1 when one does, 2 on a setup failure (a missing
receipt, no run line in it, an unreadable known list). It writes nothing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import tempfile

ROOT = pathlib.Path("P:/av-kit")
KNOWN = ROOT / "tools/e2e_host/known-failures.json"
OUT = pathlib.Path("C:/Temp/av-kit/e2e-devpc-clipboard/flake")
AC10_FILE = "clipboard-guard.test.ts"
AC10_TITLE = "S100 AC-10"
AC10_CALLS = ["main writeText", "renderer writeText", "webContents copy"]
LOG = re.compile(r"^clipboard-(\d+)\.jsonl$")
RUN_LINE = re.compile(r"^\s*(run \d+|rerun) files: receipt \S+ diag (\S+) run_id \S+\s*$")


def gated_files(known_text: str) -> list[str]:
    data = json.loads(known_text)
    return sorted({str(row["file"]) for row in data.get("gated", [])})


def read_rows(path: pathlib.Path) -> tuple[list[dict], list[str]]:
    """The JSON-object lines of a file, and a problem per line that is not one."""
    rows: list[dict] = []
    bad: list[str] = []
    text = path.read_bytes().decode("utf-8", errors="replace")
    for n, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            row = None
        if isinstance(row, dict):
            rows.append(row)
        else:
            bad.append(f"{path.name}:{n}: not a JSON object")
    return rows, bad


def check_folder(diag: pathlib.Path, gated: list[str], need_ac10: bool) -> tuple[list[str], str]:
    """The problems in one diag folder, and its count line."""
    if not diag.is_dir():
        return [f"{diag.name}: the diag folder is missing"], f"folder {diag.name}: missing"
    problems: list[str] = []
    starts: dict[int, dict] = {}
    ended: set[int] = set()
    phases = diag / "phases.jsonl"
    if phases.is_file():
        rows, bad = read_rows(phases)
        problems += bad
        for row in rows:
            launch = row.get("launch")
            if not isinstance(launch, int):
                continue
            if row.get("phase") == "launch-start":
                starts.setdefault(launch, row)
            elif row.get("phase") == "launch-end":
                ended.add(launch)
    logs: dict[int, pathlib.Path] = {}
    for path in sorted(diag.iterdir()):
        m = LOG.match(path.name)
        if m:
            logs[int(m.group(1))] = path
    for launch in sorted(set(logs) - set(starts)):
        problems.append(f"{logs[launch].name}: no launch-start row names launch {launch}")
    calls = ac10 = unfinished = gated_n = 0
    for launch, start in sorted(starts.items()):
        where = f"launch {launch} ({start.get('file', '')}: {start.get('title', '')})"
        is_ac10 = start.get("file") == AC10_FILE and str(start.get("title", "")).startswith(
            AC10_TITLE
        )
        ac10 += is_ac10
        path = logs.get(launch)
        if path is None:
            if launch not in ended:
                unfinished += 1
            elif start.get("file") in gated:
                gated_n += 1
            else:
                problems.append(f"{where}: no guard log, so no installed line")
            continue
        rows, bad = read_rows(path)
        problems += bad
        installed = sum(1 for r in rows if r.get("installed") is True)
        failed = [r for r in rows if "failed" in r]
        seen = [str(r["call"]) for r in rows if "call" in r]
        calls += len(seen)
        for r in failed:
            problems.append(f"{where}: the guard failed closed: {r.get('failed')}")
        if installed == 0 and launch not in ended:
            unfinished += 1
        elif installed != 1 and not failed:
            problems.append(f"{where}: {installed} installed lines, not 1")
        if is_ac10:
            if sorted(seen) != sorted(AC10_CALLS):
                problems.append(f"{where}: the AC-10 calls are {seen}, not {AC10_CALLS}")
        elif seen:
            problems.append(f"{where}: clipboard call(s) recorded: {', '.join(seen)}")
    if need_ac10 and ac10 == 0:
        problems.append(f"{diag.name}: no AC-10 launch")
    count = (
        f"folder {diag.name}: launches {len(starts)}, logs {len(logs)}, call lines {calls},"
        f" AC-10 launches {ac10}, without an installed line {unfinished + gated_n}"
        f" (unfinished {unfinished}, gated {gated_n})"
    )
    return problems, count


def receipt_folders(text: str, out: pathlib.Path) -> list[tuple[pathlib.Path, bool]]:
    """Each diag folder a flake-run receipt names, and whether it must hold an AC-10 launch."""
    folders = []
    for line in text.splitlines():
        m = RUN_LINE.match(line)
        if m:
            folders.append((out / m.group(2), m.group(1) != "rerun"))
    return folders


def run(folders: list[tuple[pathlib.Path, bool]], gated: list[str]) -> int:
    failed = 0
    for diag, need in folders:
        problems, count = check_folder(diag, gated, need)
        print(count)
        for p in problems:
            print("FAIL", p)
        failed += bool(problems)
    print(f"guard-logs: {len(folders)} folder(s), {failed} failing")
    return 1 if failed else 0


def selftest() -> int:
    bad: list[str] = []
    ok = '{"installed": true, "names": ["writeText"]}'
    gated = ["g.test.ts"]

    def start(launch: int, file: str = "a.test.ts", title: str = "t") -> str:
        return json.dumps(dict(phase="launch-start", launch=launch, file=file, title=title))

    def end(launch: int) -> str:
        return json.dumps(dict(phase="launch-end", launch=launch))

    ac10 = [start(9, AC10_FILE, AC10_TITLE + " x"), end(9)]
    ac10_log = [ok] + [json.dumps(dict(call=c, kind="write")) for c in AC10_CALLS]
    cases = [
        (
            "two clean launches and AC-10",
            ac10 + [start(1), end(1), start(2), end(2)],
            {1: [ok], 2: [ok], 9: ac10_log},
            True,
            True,
        ),
        (
            "a call line",
            ac10 + [start(1), end(1)],
            {1: [ok, '{"call": "main writeText", "kind": "write"}'], 9: ac10_log},
            True,
            False,
        ),
        (
            "an input chord line",
            ac10 + [start(1), end(1)],
            {1: [ok, '{"call": "input Control+C", "kind": "write"}'], 9: ac10_log},
            True,
            False,
        ),
        ("a launch without a log", ac10 + [start(1), end(1)], {9: ac10_log}, True, False),
        (
            "a failed line",
            ac10 + [start(1)],
            {1: ['{"failed": "readHTML missing"}'], 9: ac10_log},
            True,
            False,
        ),
        ("two installed lines", ac10 + [start(1), end(1)], {1: [ok, ok], 9: ac10_log}, True, False),
        ("an orphan log", ac10, {5: [ok], 9: ac10_log}, True, False),
        ("an invalid line", ac10 + [start(1), end(1)], {1: [ok, "[1]"], 9: ac10_log}, True, False),
        (
            "AC-10 without its renderer call",
            ac10,
            {9: [ok] + ac10_log[1:2] + ac10_log[3:]},
            True,
            False,
        ),
        ("AC-10 with an extra call", ac10, {9: ac10_log + [ac10_log[1]]}, True, False),
        ("a run folder without AC-10", [start(1), end(1)], {1: [ok]}, True, False),
        ("a rerun folder without AC-10", [start(1), end(1)], {1: [ok]}, False, True),
        ("an unfinished launch without a log", ac10 + [start(1)], {9: ac10_log}, True, True),
        (
            "a gated launch without a log",
            ac10 + [start(1, "g.test.ts"), end(1)],
            {9: ac10_log},
            True,
            True,
        ),
        (
            "a gated launch with a call",
            ac10 + [start(1, "g.test.ts"), end(1)],
            {1: [ok, '{"call": "main writeText"}'], 9: ac10_log},
            True,
            False,
        ),
    ]
    with tempfile.TemporaryDirectory(prefix="edc-guard-logs-") as tmp:
        base = pathlib.Path(tmp)
        for i, (name, phases, logs, need, want_ok) in enumerate(cases):
            diag = base / f"case-{i}"
            diag.mkdir()
            (diag / "phases.jsonl").write_text("\n".join(phases) + "\n", encoding="utf-8")
            for launch, lines in logs.items():
                (diag / f"clipboard-{launch}.jsonl").write_text(
                    "\n".join(lines) + "\n", encoding="utf-8"
                )
            problems, _count = check_folder(diag, gated, need)
            if (not problems) != want_ok:
                bad.append(f"{name}: problems {problems}")
        _p, count = check_folder(base / "case-12", gated, True)
        if "unfinished 1, gated 0" not in count:
            bad.append(f"the unfinished count: {count}")
        receipt = (
            "load before the runs: 0\n"
            "run 1 files: receipt epf-g-1-X.txt diag epf-g-1-diag-X run_id X-1\n"
            "  rerun files: receipt epf-g-1-rerun-a-3-X.txt diag epf-g-1-rerun-a-3-diag-X"
            " run_id X-g-1-rerun-a-3\n"
        )
        got = receipt_folders(receipt, base)
        want = [(base / "epf-g-1-diag-X", True), (base / "epf-g-1-rerun-a-3-diag-X", False)]
        if got != want:
            bad.append(f"receipt_folders: {got}")
        problems, _count = check_folder(base / "absent", gated, True)
        if not problems:
            bad.append("a missing folder passed")
    known = '{"known": [], "skip": [], "gated": [{"label": "mini-air", "file": "b.test.ts"}]}'
    if gated_files(known) != ["b.test.ts"]:
        bad.append("gated_files")
    for row in bad:
        print("selftest FAIL:", row)
    total = len(cases) + 4
    print(f"guard-logs selftest: {total - len(bad)} of {total} cases pass")
    return 1 if bad else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--diag", type=pathlib.Path)
    mode.add_argument("--receipt", type=pathlib.Path)
    mode.add_argument("--selftest", action="store_true")
    parser.add_argument("--out", type=pathlib.Path, default=OUT)
    parser.add_argument("--gated", action="append", default=None)
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    try:
        gated = (
            args.gated
            if args.gated is not None
            else gated_files(KNOWN.read_bytes().decode("utf-8"))
        )
        if args.diag is not None:
            folders = [(args.diag, True)]
        else:
            folders = receipt_folders(
                args.receipt.read_bytes().decode("utf-8", "replace"), args.out
            )
            if not folders:
                raise ValueError(f"{args.receipt.name} names no run or rerun folder")
    except (OSError, ValueError, KeyError) as error:
        print(f"guard-logs: setup failure: {error}")
        return 2
    print("gated files:", gated)
    return run(folders, gated)


if __name__ == "__main__":
    sys.exit(main())
