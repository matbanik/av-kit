"""Session 77 scope check: the S4 check before each row (task.md S4) and the session gate's
``scope-paths`` and ``line-endings`` steps (implementation-plan.md §Session gate, §Stop
Conditions S4). Adapted from Session 76's (2026-11-15-tooling-test-hermeticity) without its
content-bound ``HEAD`` rule: the executor brief says a ``HEAD`` move mid-session is a stop, so
``HEAD`` must equal ``baseline.sha``.

Usage, from the repository root:

* ``python scope-check.py [--row N]`` refuses unless all of these hold:

  - ``HEAD`` equals ``baseline.sha``;
  - every path ``git status --porcelain --untracked-files=all`` lists is in
    ``baseline-scope.json`` (§Files Modified), in this plan folder, one of this session's
    closeout artifacts, one of the two shared state files, a new plan folder another session's
    planner writes (absent from ``baseline.sha``'s tree), or in ``baseline-dirty.txt``;
  - every ``baseline-dirty-hashes.json`` path still has its row-0 SHA-256 (or is still deleted);
  - with ``--row N``: every §Files Modified path that no row before N writes (``WRITTEN_BY``)
    still has its ``baseline-scope.json`` SHA-256 (or is still absent).

* ``python scope-check.py --eol`` refuses unless every §Files Modified path that exists has the
  line-ending kind row 0 recorded in ``baseline-eol.json`` (a new file: ``lf``), with no BOM.

It prints the paths it saw by class and ends with ``scope-check: ok`` or the problem count.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

PLAN = "docs/execution/plans/2026-11-15-text-scrub-residuals"
SCOPE_PREFIXES = (
    PLAN + "/",
    ".agent/context/handoffs/2026-11-15-text-scrub-residuals-",
    "docs/execution/reflections/2026-11-15-text-scrub-residuals-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
OTHER_PLAN_PREFIX = "docs/execution/plans/2026-11-15-"
#: The first task row that writes each §Files Modified path.
WRITTEN_BY = {
    "tests/unit/test_transcript_title_cleaning.py": 1,
    "packages/core/src/avkit_core/domain/download.py": 2,
    "packages/infrastructure/src/avkit_infra/youtube/adapter.py": 2,
    "packages/core/src/avkit_core/services/transcript.py": 2,
    "tests/unit/test_console_home_short_form.py": 3,
    "packages/core/src/avkit_core/services/health.py": 4,
    "packages/core/src/avkit_core/services/download.py": 4,
    "docs/build-plan/03-service-layer.md": 5,
    ".agent/context/known-issues.yaml": 5,
    ".agent/context/known-issues.md": 5,
    ".agent/context/meu-status.yaml": 5,
    ".agent/context/meu-registry.md": 5,
    "docs/BUILD_PLAN.md": 5,
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md": 5,
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
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "deleted"


def eol_kind(data: bytes) -> str:
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    if crlf and not lf and not cr:
        return "crlf"
    if lf and not crlf and not cr:
        return "lf"
    return f"mixed crlf={crlf} lf={lf} cr={cr}"


def eol() -> int:
    plan = pathlib.Path(PLAN)
    want = json.loads((plan / "baseline-eol.json").read_text(encoding="utf-8"))
    problems = []
    for p, kind in sorted(want.items()):
        path = pathlib.Path(p)
        if not path.is_file():
            if kind != "absent-new-lf":
                problems.append(f"{p}: missing (row 0 {kind})")
            print(f"{p}: absent (row 0 {kind})")
            continue
        data = path.read_bytes()
        got = eol_kind(data)
        expected = "lf" if kind == "absent-new-lf" else kind
        bom = data.startswith(b"\xef\xbb\xbf")
        print(f"{p}: {got} bom={bom} (row 0 {kind})")
        if got != expected or bom:
            problems.append(f"{p}: {got} bom={bom}, row 0 {kind}")
    for p in problems:
        print("PROBLEM:", p)
    print(f"scope-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


def main() -> int:
    if "--eol" in sys.argv:
        return eol()
    row = int(sys.argv[sys.argv.index("--row") + 1]) if "--row" in sys.argv else None
    plan = pathlib.Path(PLAN)
    problems: list[str] = []
    base = (plan / "baseline.sha").read_text(encoding="utf-8").strip()
    head = git("rev-parse", "HEAD").strip()
    scope = json.loads((plan / "baseline-scope.json").read_text(encoding="utf-8"))
    dirty = set(paths((plan / "baseline-dirty.txt").read_text(encoding="utf-8")))
    hashes = json.loads((plan / "baseline-dirty-hashes.json").read_text(encoding="utf-8"))
    print("HEAD", head, "baseline.sha", base)
    if head != base:
        problems.append(f"HEAD moved from baseline.sha {base} to {head}: stop and report (executor brief)")
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
        if sha(p) != want:
            problems.append(f"baseline-dirty content mismatch: {p}")
    print("baseline-dirty-hashes checked:", len(hashes))
    if row is not None:
        unwritten = sorted(p for p in scope if WRITTEN_BY.get(p, 99) >= row)
        for p in unwritten:
            got = sha(p)
            got = "absent" if got == "deleted" else got
            if got != scope[p]:
                problems.append(f"row {row}: {p} is not yet written by this plan and differs from row 0")
        print(f"row {row}: {len(unwritten)} unwritten Files Modified path(s) match row 0 unless listed below")
    for p in problems:
        print("PROBLEM:", p)
    print(f"scope-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
