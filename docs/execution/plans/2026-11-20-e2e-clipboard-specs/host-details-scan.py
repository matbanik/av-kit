"""Scan this session's tracked files for the local config's host details (Session 98, AC-17).

Copied from Session 97's plan folder (`2026-11-19-e2e-host-parity/`, the newest ruff-clean copy;
Session 96 RULE-3), itself from Session 96's (its AC-21), with the file list set to Session 98's
new and edited files.

Usage: ``host-details-scan.py CONFIG [--allow-absent] [--file PATH]... [--grown PATH COPY]...``

``--allow-absent`` (task row 0 only, before rows 2 and 4 to 6 write them) skips the session's new
files that do not exist yet, printing each as ``absent:``; every other missing file is still
exit 2.

It reads ``host``, ``root``, ``task`` and ``user`` from CONFIG (the untracked local config) and
scans the session's new tracked files, every file in this plan folder and each ``--file`` for:
the host alias (any case); the root and the task with either slash, also JSON-escaped (any
case); and the account in the forms a path, a quote, a backtick or an assignment gives it
(``\\u``, ``/u``, ``"u"``, ``'u'``, ```u``, ``=u``, any case, not followed by a name
character). Each ``--grown PATH COPY`` pair must hold no more hits in PATH than in COPY (a
file that already named the host before this session). It prints key names and file paths
only, never a value.
Exit 0 with no hit; 1 on a hit or a grown count; 2 on usage or a missing file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
PLAN = Path(__file__).resolve().parent
NEW_FILES = [
    "ui/tests/e2e/capture-system-clipboard.test.ts",
    "ui/tests/e2e/capture-filmstrip-actions.test.ts",
    "ui/tests/e2e/capture-import.test.ts",
    "tools/e2e_remote.py",
    "tools/e2e_host/host-facts.ps1",
    "tools/e2e_host/run-e2e.ps1",
    "tools/e2e_host/host-status.ps1",
    "tools/e2e_host/known-failures.json",
    "tests/tooling/test_e2e_remote.py",
    ".agent/docs/e2e-remote-host.md",
]
CREATED = ("ui/tests/e2e/capture-system-clipboard.test.ts",)


def patterns(cfg: dict) -> dict[str, re.Pattern[str]]:
    host = str(cfg["host"])
    root = str(cfg["root"]).replace("/", "\\")
    user = str(cfg["user"])
    task = str(cfg["task"]).replace("/", "\\")
    root_rx = re.escape(root).replace(r"\\", r"(?:\\\\|\\|/)")
    task_rx = re.escape(task).replace(r"\\", r"(?:\\\\|\\|/)")
    return {
        "host": re.compile(re.escape(host), re.I),
        "root": re.compile(root_rx + r"(?![A-Za-z0-9_.-])", re.I),
        "task": re.compile(task_rx + r"(?![A-Za-z0-9_.-])", re.I),
        "user": re.compile(r"(?:\\|/|\"|'|`|=)" + re.escape(user) + r"(?![A-Za-z0-9_.-])", re.I),
    }


def hits(path: Path, pats: dict[str, re.Pattern[str]]) -> dict[str, int]:
    text = path.read_bytes().decode("utf-8", "replace")
    return {k: len(p.findall(text)) for k, p in pats.items()}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--file", action="append", default=[])
    ap.add_argument("--allow-absent", action="store_true")
    ap.add_argument("--grown", nargs=2, action="append", default=[], metavar=("PATH", "COPY"))
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    cfg_path = Path(a.config)
    if not cfg_path.is_file():
        print("missing: config")
        return 2
    pats = patterns(json.loads(cfg_path.read_text(encoding="utf-8")))
    files = [REPO / p for p in NEW_FILES]
    if a.allow_absent:
        for p in [f for f in files if f.relative_to(REPO).as_posix() in CREATED and not f.exists()]:
            print("absent:", ascii(p.relative_to(REPO).as_posix()))
            files.remove(p)
    files += sorted(p for p in PLAN.iterdir() if p.is_file() and p.suffix != ".pyc")
    files += [Path(p) for p in a.file]
    missing = [str(p) for p in files if not p.is_file()]
    missing += [p for pair in a.grown for p in pair if not Path(p).is_file()]
    if missing:
        print("missing:", [ascii(m) for m in missing])
        return 2
    bad = 0
    for f in files:
        got = {k: n for k, n in hits(f, pats).items() if n}
        if got:
            bad += 1
            print("hit:", ascii(str(f)), sorted(got.items()))
    for path, copy in a.grown:
        now, was = hits(Path(path), pats), hits(Path(copy), pats)
        grown = sorted(k for k in now if now[k] > was[k])
        print("grown check:", ascii(path), "keys grown:", grown)
        bad += bool(grown)
    print(f"host-details-scan: files={len(files)} grown_pairs={len(a.grown)} bad={bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
