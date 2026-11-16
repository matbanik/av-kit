"""Session 76 scope check: the S4 check before each row and the session gate's ``scope-paths``
step (implementation-plan.md §Session gate, §Stop Conditions S4). A copy of Session 87's
(2026-11-15-framework-small-syncs) with the plan's two changes (§Project files, D-918): the
content-bound ``HEAD`` rule and the ``--subtree`` mode.

Usage: ``python scope-check.py`` from the repository root. It refuses unless all of these hold:

* ``HEAD`` equals ``baseline.sha``, or moved only by commits whose changed paths
  (``git diff --name-only <baseline.sha> HEAD``) are all in ``baseline-dirty.txt`` and whose
  blob at ``HEAD`` is the one row 0 recorded for that path's working bytes
  (``baseline-dirty-blobs.json``, ``git hash-object`` with the repository's filters; ``deleted``
  means the path must be gone from ``HEAD``): an earlier session's work committed unchanged. No
  scoped file's current bytes are compared with ``HEAD``;
* every path ``git status --porcelain --untracked-files=all`` lists is in ``baseline-scope.json``
  (§Files Modified), in this plan folder, one of this session's closeout artifacts, one of the
  two shared state files, a new plan folder another session's planner writes (absent from
  ``baseline.sha``'s tree), or in ``baseline-dirty.txt``;
* every ``baseline-dirty-hashes.json`` path still has its row-0 SHA-256 (or is still deleted).

``python scope-check.py --subtree packages/api`` instead hashes every file under that path that
``git ls-files --cached --others --exclude-standard`` lists (a listed but missing file counts as
``deleted``) and compares the whole map with row 0's ``baseline-api.json`` (H1-4's OpenAPI skip
basis).

It prints the paths it saw by class and ends with ``scope-check: ok`` or the problem count.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

PLAN = "docs/execution/plans/2026-11-15-tooling-test-hermeticity"
SCOPE_PREFIXES = (
    PLAN + "/",
    ".agent/context/handoffs/2026-11-15-tooling-test-hermeticity-",
    "docs/execution/reflections/2026-11-15-tooling-test-hermeticity-",
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
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "deleted"


def subtree_hashes(prefix: str) -> dict[str, str]:
    listed = git("ls-files", "--cached", "--others", "--exclude-standard", "--", prefix).splitlines()
    return {p: sha(p) for p in sorted(set(listed)) if p.strip()}


def subtree(prefix: str) -> int:
    plan = pathlib.Path(PLAN)
    want = json.loads((plan / "baseline-api.json").read_text(encoding="utf-8"))
    got = subtree_hashes(prefix)
    problems = []
    for p in sorted(set(want) | set(got)):
        if want.get(p) != got.get(p):
            problems.append(f"{p}: row 0 {want.get(p, 'unlisted')} now {got.get(p, 'unlisted')}")
    print(f"subtree {prefix}: {len(got)} files now, {len(want)} at row 0")
    for p in problems:
        print("PROBLEM:", p)
    print(f"scope-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


def main() -> int:
    if "--subtree" in sys.argv:
        return subtree(sys.argv[sys.argv.index("--subtree") + 1])
    plan = pathlib.Path(PLAN)
    problems: list[str] = []
    base = (plan / "baseline.sha").read_text(encoding="utf-8").strip()
    head = git("rev-parse", "HEAD").strip()
    scope = json.loads((plan / "baseline-scope.json").read_text(encoding="utf-8"))
    dirty = set(paths((plan / "baseline-dirty.txt").read_text(encoding="utf-8")))
    hashes = json.loads((plan / "baseline-dirty-hashes.json").read_text(encoding="utf-8"))
    blobs = json.loads((plan / "baseline-dirty-blobs.json").read_text(encoding="utf-8"))
    print("HEAD", head, "baseline.sha", base)
    if head != base:
        moved = [p for p in git("diff", "--name-only", base, head).splitlines() if p.strip()]
        print(f"HEAD moved; {len(moved)} path(s) changed since baseline.sha")
        for p in moved:
            row0 = blobs.get(p)
            listed = git("ls-tree", head, "--", p).split()
            committed = listed[2] if len(listed) >= 3 else "deleted"
            if p not in dirty:
                problems.append(f"HEAD moved by a path not in baseline-dirty.txt: {p}")
            elif row0 is None:
                problems.append(f"HEAD moved by a path with no row-0 blob: {p}")
            elif committed != row0:
                problems.append(f"HEAD moved by a path whose committed blob {committed} is not row 0's {row0}: {p}")
            else:
                print("   committed unchanged:", p)
    base_plans = set(git("ls-tree", "--name-only", base, "docs/execution/plans/").splitlines())
    seen: dict[str, list[str]] = {}
    for p in paths(git("status", "--porcelain", "--untracked-files=all")):
        folder = "/".join(p.split("/")[:4])
        if p in scope:
            kind = "files-modified"
        elif p.startswith(SCOPE_PREFIXES):
            kind = "plan-or-closeout"
        elif p in SHARED:
            kind = "shared-state"
        elif p.startswith(OTHER_PLAN_PREFIX) and folder != p and folder not in base_plans:
            kind = "other-session-plan"
        elif p in dirty:
            kind = "baseline-dirty"
        else:
            kind = "outside scope"
            problems.append(f"outside scope: {p}")
        seen.setdefault(kind, []).append(p)
    for kind, names in sorted(seen.items()):
        print(f"{kind}: {len(names)}")
        if kind in ("files-modified", "outside scope"):
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
