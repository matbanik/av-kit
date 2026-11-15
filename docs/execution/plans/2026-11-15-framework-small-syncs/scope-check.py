"""Session 87 scope check: the S4 check before each row and the session gate's ``scope-paths``
step (implementation-plan.md §Session gate, §Stop Conditions S4).

Usage: ``python scope-check.py`` from the repository root. It refuses unless all of these hold:

* ``git rev-parse HEAD`` equals ``baseline.sha``;
* every path ``git status --porcelain --untracked-files=all`` lists is in ``baseline-scope.json``
  (§Files Modified), in this plan folder, one of this session's closeout artifacts, one of the
  two shared state files, a new plan folder another session's planner writes (coordinator,
  2026-11-15; the same rule as ``identity.py`` ``OTHER_PLAN_PREFIX``), or in ``baseline-dirty.txt``;
* every ``baseline-dirty-hashes.json`` path still has its row-0 SHA-256 (or is still deleted).

It prints the paths it saw by class and ends with ``scope-check: ok`` or the problem count.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

PLAN = "docs/execution/plans/2026-11-15-framework-small-syncs"
SCOPE_PREFIXES = (
    PLAN + "/",
    ".agent/context/handoffs/2026-11-15-framework-small-syncs-",
    "docs/execution/reflections/2026-11-15-framework-small-syncs-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
OTHER_PLAN_PREFIX = "docs/execution/plans/2026-11-15-"


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
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "deleted"


def main() -> int:
    plan = pathlib.Path(PLAN)
    problems: list[str] = []
    base = (plan / "baseline.sha").read_text(encoding="utf-8").strip()
    head = git("rev-parse", "HEAD").strip()
    print("HEAD", head, "baseline.sha", base)
    if head != base:
        problems.append(f"HEAD {head} differs from baseline.sha {base}")
    scope = json.loads((plan / "baseline-scope.json").read_text(encoding="utf-8"))
    dirty = set(paths((plan / "baseline-dirty.txt").read_text(encoding="utf-8")))
    hashes = json.loads((plan / "baseline-dirty-hashes.json").read_text(encoding="utf-8"))
    head_plans = set(git("ls-tree", "--name-only", "HEAD", "docs/execution/plans/").splitlines())
    seen: dict[str, list[str]] = {}
    for p in paths(git("status", "--porcelain", "--untracked-files=all")):
        folder = "/".join(p.split("/")[:4])
        if p in scope:
            kind = "files-modified"
        elif p.startswith(SCOPE_PREFIXES):
            kind = "plan-or-closeout"
        elif p in SHARED:
            kind = "shared-state"
        elif p.startswith(OTHER_PLAN_PREFIX) and folder != p and folder not in head_plans:
            kind = "other-session-plan"
        elif p in dirty:
            kind = "baseline-dirty"
        else:
            kind = "outside scope"
            problems.append(f"outside scope: {p}")
        seen.setdefault(kind, []).append(p)
    for kind, names in sorted(seen.items()):
        print(f"{kind}: {len(names)}")
        if kind in ("files-modified", "outside scope", "baseline-dirty"):
            for n in names:
                print("  ", n)
    for p, want in sorted(hashes.items()):
        got = sha(p)
        if got != want:
            problems.append(f"baseline-dirty content mismatch: {p}")
    print("baseline-dirty-hashes checked:", len(hashes))
    for p in problems:
        print("PROBLEM:", p)
    print(f"scope-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
