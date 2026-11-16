"""Session 78 scope check (a copy of Session 87's, with this plan's PLAN): the S4 check before
each row and the session gate's ``scope-paths`` step (implementation-plan.md §Session gate, §Stop Conditions S4).

Usage: ``python scope-check.py --before-row N`` from the repository root, where N is the task
row about to run (0 to 12) or 13 after the last row (the H1 rows and the gate); ``--selftest``
runs the pure S2 fixtures. It refuses unless all of these hold:

* ``git rev-parse HEAD`` equals ``baseline.sha``, or every path that changed between them is one
  of ``baseline-dirty.txt``'s, a shared state file or another session's new plan folder: a commit
  by Mat of earlier sessions' work is not a stop, because the check binds to content, not ``HEAD``;
* every path ``git status --porcelain --untracked-files=all`` lists is in ``baseline-scope.json``
  (§Files Modified), in this plan folder, one of this session's closeout artifacts, one of the
  two shared state files, a new plan folder another session's planner writes (coordinator,
  2026-11-15; the same rule as ``identity.py`` ``OTHER_PLAN_PREFIX``), or in ``baseline-dirty.txt``;
* every ``baseline-dirty-hashes.json`` path still has its row-0 SHA-256 (or is still deleted);
* S2: every ``baseline-scope.json`` path that no row before N writes (``ROW_WRITES``) still has
  its row-0 SHA-256, or is still ``absent`` for a new path. ``CapturePage.tsx`` is in no row's
  writes (rows 9 and 10 restore the mutant in the same row), so it is checked before every row.

It prints the paths it saw by class and ends with ``scope-check: ok`` or the problem count.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

PLAN = "docs/execution/plans/2026-11-15-e2e-harness-hardening"
SCOPE_PREFIXES = (
    PLAN + "/",
    ".agent/context/handoffs/2026-11-15-e2e-harness-hardening-",
    "docs/execution/reflections/2026-11-15-e2e-harness-hardening-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
OTHER_PLAN_PREFIX = "docs/execution/plans/2026-11-15-"
REGISTER = (".agent/context/known-issues.yaml", ".agent/context/known-issues.md")
REBIND = pathlib.Path("C:/Temp/av-kit/e2e-harness-hardening/ehh-register-rebind.txt")
#: The scoped paths each task row writes (implementation-plan.md §Files Modified; task.md rows).
#: Row 5 writes every site file of baseline-sites.json, added in row_writes(). Row 6 writes the
#: register only on the NEW_FAILURE_RULE product path, which leaves ehh-register-rebind.txt.
ROW_WRITES: dict[int, tuple[str, ...]] = {
    1: ("ui/tests/unit/e2e-harness.test.ts",),
    2: ("ui/tests/e2e/electron-harness.test.ts", "ui/tests/e2e/fixtures/startup-throw-main.mjs"),
    3: ("ui/tests/e2e/electron-env.ts", "ui/tests/e2e/main-error-watch.cjs", "ui/tests/e2e/electron-app.ts"),
    4: ("ui/tests/unit/layout-primitives.test.ts",),
    7: ("ui/tests/unit/vitest-global-setup.test.ts",),
    8: ("ui/tests/unit/global-setup.ts", "ui/vitest.config.ts"),
    10: ("ui/tests/unit/capture-page.test.ts", "ui/tests/unit/capture-page.behavior.test.ts"),
    12: REGISTER + (".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md",),
}


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


def row_writes(sites: list[str], rebind: bool) -> dict[int, tuple[str, ...]]:
    writes = dict(ROW_WRITES)
    writes[5] = tuple("ui/tests/e2e/" + s for s in sites)
    if rebind:
        writes[6] = REGISTER
    return writes


def stale_scope(scope: dict[str, str], writes: dict[int, tuple[str, ...]], before_row: int, current) -> list[str]:
    """Pure: the scoped paths that no row before ``before_row`` writes and whose content moved."""
    written = {p for row, names in writes.items() if row < before_row for p in names}
    out = []
    for p, want in sorted(scope.items()):
        if p in written:
            continue
        got = current(p)
        if got != want:
            out.append(f"S2: {p} is not written by any row before {before_row} and moved from its row-0 content ({want[:12]} -> {got[:12]})")
    return out


def selftest() -> int:
    scope = {"a.ts": "h-a", "b.ts": "h-b", "new.ts": "absent", "CapturePage.tsx": "h-c"}
    writes = {1: ("a.ts",), 2: ("new.ts",), 5: ("b.ts",)}
    cases = [
        ("before row 1, nothing written, all at row 0", 1, {"a.ts": "h-a", "b.ts": "h-b", "new.ts": "absent", "CapturePage.tsx": "h-c"}, 0),
        ("before row 2, row 1 wrote a.ts", 2, {"a.ts": "h-a2", "b.ts": "h-b", "new.ts": "absent", "CapturePage.tsx": "h-c"}, 0),
        ("before row 2, a sibling changed b.ts, which only row 5 writes", 2, {"a.ts": "h-a2", "b.ts": "h-sib", "new.ts": "absent", "CapturePage.tsx": "h-c"}, 1),
        ("before row 2, a new path already exists", 2, {"a.ts": "h-a2", "b.ts": "h-b", "new.ts": "h-n", "CapturePage.tsx": "h-c"}, 1),
        ("after every row, a mutant left in CapturePage.tsx", 13, {"a.ts": "x", "b.ts": "y", "new.ts": "z", "CapturePage.tsx": "h-mut"}, 1),
        ("after every row, everything written and CapturePage.tsx restored", 13, {"a.ts": "x", "b.ts": "y", "new.ts": "z", "CapturePage.tsx": "h-c"}, 0),
    ]
    failures = 0
    for name, row, now, want in cases:
        got = len(stale_scope(scope, writes, row, now.__getitem__))
        ok = got == want
        failures += not ok
        print(("ok  " if ok else "FAIL"), name, f"problems={got} want={want}")
    print(f"scope-check selftest: {len(cases) - failures} of {len(cases)} passed")
    return 1 if failures else 0


def scope_sha(path: str) -> str:
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")


def main(before_row: int) -> int:
    plan = pathlib.Path(PLAN)
    problems: list[str] = []
    base = (plan / "baseline.sha").read_text(encoding="utf-8").strip()
    head = git("rev-parse", "HEAD").strip()
    print("HEAD", head, "baseline.sha", base)
    scope = json.loads((plan / "baseline-scope.json").read_text(encoding="utf-8"))
    dirty = set(paths((plan / "baseline-dirty.txt").read_text(encoding="utf-8")))
    if head != base:
        moved = [p for p in git("diff", "--name-only", base, head).splitlines() if p]
        print("HEAD moved since baseline.sha; committed paths:", len(moved))
        for p in moved:
            if not (p in dirty or p in SHARED or p.startswith(OTHER_PLAN_PREFIX)):
                problems.append(f"committed since baseline.sha and not in baseline-dirty.txt: {p}")
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
    sites = sorted(json.loads((plan / "baseline-sites.json").read_text(encoding="utf-8")))
    stale = stale_scope(scope, row_writes(sites, REBIND.exists()), before_row, scope_sha)
    problems.extend(stale)
    print(f"baseline-scope checked before row {before_row}: {len(scope)} paths, {len(stale)} moved")
    for p in problems:
        print("PROBLEM:", p)
    print(f"scope-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        raise SystemExit(selftest())
    if len(args) != 2 or args[0] != "--before-row" or not args[1].isdigit() or not 0 <= int(args[1]) <= 13:
        print("usage: scope-check.py --before-row N (0 to 13) | --selftest")
        raise SystemExit(2)
    raise SystemExit(main(int(args[1])))
