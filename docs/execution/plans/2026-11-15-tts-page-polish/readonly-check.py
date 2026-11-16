"""Session 80 read-only check (closeout row H1-4; implementation-plan.md AC-150.8, AC-149.6).

Usage: ``python readonly-check.py [--plan-dir DIR]`` from the repository root. ``--plan-dir``
names where row 0 wrote its data (default: this plan folder; the plan-time dry run passes
``C:/Temp/av-kit/tts-page-polish/dry``).

Nothing here is compared with ``HEAD``. Sessions 75 to 79 may leave these files changed and
uncommitted, so the baseline is the content row 0 recorded. It refuses unless all of these hold:

* every path in ``baseline-readonly.json`` still has its row-0 SHA-256;
* every path under ``packages/`` or ``mcp-server/`` that ``git status --porcelain
  --untracked-files=all`` lists now was listed at row 0 and still has its row-0 SHA-256 in
  ``baseline-dirty-hashes.json`` (or is still deleted);
* every ``baseline-dirty-hashes.json`` path under those folders still has that content, listed
  or not.

It prints what it checked and ends with ``readonly-check: ok`` or the problem count.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys

PLAN = "docs/execution/plans/2026-11-15-tts-page-polish"
API_PREFIXES = ("packages/", "mcp-server/")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout.decode("utf-8")


def paths(porcelain: str) -> list[str]:
    out = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        name = line[3:].strip()
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        out.append(name.strip('"'))
    return out


def sha(path: str) -> str:
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "deleted"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan-dir", default=PLAN)
    args = parser.parse_args()
    plan = pathlib.Path(args.plan_dir)
    problems: list[str] = []
    readonly = json.loads((plan / "baseline-readonly.json").read_text(encoding="utf-8"))
    hashes = json.loads((plan / "baseline-dirty-hashes.json").read_text(encoding="utf-8"))
    for p, want in sorted(readonly.items()):
        got = sha(p)
        print("read-only", p, "row-0 content" if got == want else "CHANGED")
        if got != want:
            problems.append(f"read-only file changed since row 0: {p}")
    listed = [
        p
        for p in paths(git("status", "--porcelain", "--untracked-files=all"))
        if p.startswith(API_PREFIXES)
    ]
    for p in listed:
        if p not in hashes:
            problems.append(f"changed since row 0 (clean then): {p}")
    held = {p: want for p, want in hashes.items() if p.startswith(API_PREFIXES)}
    for p, want in sorted(held.items()):
        if sha(p) != want:
            problems.append(f"changed since row 0 (dirty then): {p}")
    print("packages/ and mcp-server/:", len(listed), "listed now,", len(held), "held from row 0")
    for p in problems:
        print("PROBLEM:", p)
    print(f"readonly-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
