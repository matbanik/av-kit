"""Scan this session's tracked files for the local config's host details (Session 96, AC-21).

Usage: ``host-details-scan.py CONFIG [--file PATH]... [--grown PATH COPY]...``

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
    "tools/e2e_remote.py",
    "tools/e2e_host/e2e-host.example.json",
    "tools/e2e_host/known-failures.json",
    "tools/e2e_host/host-facts.ps1",
    "tools/e2e_host/host-lock.ps1",
    "tools/e2e_host/host-prepare.ps1",
    "tools/e2e_host/host-start.ps1",
    "tools/e2e_host/host-status.ps1",
    "tools/e2e_host/host-release.ps1",
    "tools/e2e_host/run-e2e.ps1",
    "tests/tooling/test_e2e_remote.py",
    ".agent/docs/e2e-remote-host.md",
    ".agent/docs/commands.md",
]


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
