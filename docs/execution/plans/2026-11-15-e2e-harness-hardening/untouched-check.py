"""Session 78 skip-basis check (task rows 0 and H1-4; the session gate's ``untouched`` step;
implementation-plan.md §Session gate "Skipped, with reason").

The gate skips ``openapi``, ``py-*`` and ``mcp-*`` because this session changes nothing under
``ROOTS``. That claim is bound to the content row 0 saw, never to ``HEAD``: an earlier session of
the grouping (Sessions 75 to 77) may have left files under ``packages/``, ``tests/`` or ``ui/src``
changed and uncommitted, and ``git diff <baseline.sha> -- packages/api`` would report their work
as this session's (the sibling plan reviews' finding, 2026-11-15).

Usage, from the repository root:

* ``python untouched-check.py --record`` (row 0) writes ``baseline-untouched.json``: the SHA-256 of
  every tracked or untracked, not ignored, file under ``ROOTS`` as it is on disk now.
* ``python untouched-check.py`` exits 0 only when the same file set exists with the same hashes;
  it prints each added, removed or changed path.
* ``python untouched-check.py --selftest`` runs the fixtures below in a scratch git repository,
  including the case that a HEAD-bound check gets wrong: a file a sibling left changed before row 0
  (a HEAD diff reports it; this check passes it).

Read-only, apart from ``--record`` writing the one manifest in this plan folder.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-e2e-harness-hardening")
MANIFEST = "baseline-untouched.json"
ROOTS = ("packages", "tests", "mcp-server/src", "mcp-server/tests", "ui/src", "tools")


def _files(repo: pathlib.Path, roots: tuple[str, ...]) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", *roots],
        cwd=repo, capture_output=True, check=True,
    ).stdout.decode("utf-8")
    return sorted({p for p in out.split("\0") if p and (repo / p).is_file()})


def snapshot(repo: pathlib.Path, roots: tuple[str, ...] = ROOTS) -> dict[str, str]:
    return {p: hashlib.sha256((repo / p).read_bytes()).hexdigest() for p in _files(repo, roots)}


def compare(before: dict[str, str], after: dict[str, str]) -> list[str]:
    problems = [f"added since row 0: {p}" for p in sorted(set(after) - set(before))]
    problems += [f"removed since row 0: {p}" for p in sorted(set(before) - set(after))]
    problems += [f"changed since row 0: {p}" for p in sorted(set(before) & set(after)) if before[p] != after[p]]
    return problems


def selftest() -> int:
    failures = 0
    with tempfile.TemporaryDirectory(dir="C:/Temp/av-kit/e2e-harness-hardening/tmp") as tmp:
        repo = pathlib.Path(tmp)
        run = lambda *a: subprocess.run(["git", *a], cwd=repo, capture_output=True, check=True)  # noqa: E731
        run("init", "-q")
        run("config", "user.email", "selftest@example.invalid")
        run("config", "user.name", "selftest")
        (repo / "packages").mkdir()
        (repo / "packages/api.py").write_bytes(b"a = 1\n")
        (repo / "packages/other.py").write_bytes(b"b = 1\n")
        run("add", "-A")
        run("commit", "-q", "-m", "base")
        # A sibling session's uncommitted change before row 0: HEAD differs, the content is bound.
        (repo / "packages/api.py").write_bytes(b"a = 2\n")
        (repo / "packages/sibling_new.py").write_bytes(b"c = 1\n")
        roots = ("packages",)
        before = snapshot(repo, roots)
        head_diff = run("diff", "--name-only", "HEAD", "--", "packages").stdout.decode().split()
        cases = []
        cases.append(("sibling-change-before-row-0", compare(before, snapshot(repo, roots)) == [] and head_diff != []))
        (repo / "packages/other.py").write_bytes(b"b = 2\n")
        cases.append(("change-after-row-0", compare(before, snapshot(repo, roots)) == ["changed since row 0: packages/other.py"]))
        (repo / "packages/other.py").write_bytes(b"b = 1\n")
        (repo / "packages/added.py").write_bytes(b"d = 1\n")
        cases.append(("added-after-row-0", compare(before, snapshot(repo, roots)) == ["added since row 0: packages/added.py"]))
        (repo / "packages/added.py").unlink()
        (repo / "packages/sibling_new.py").unlink()
        cases.append(("removed-after-row-0", compare(before, snapshot(repo, roots)) == ["removed since row 0: packages/sibling_new.py"]))
        (repo / ".gitignore").write_bytes(b"packages/ignored.log\n")
        (repo / "packages/sibling_new.py").write_bytes(b"c = 1\n")
        (repo / "packages/ignored.log").write_bytes(b"noise\n")
        cases.append(("ignored-file-not-bound", compare(before, snapshot(repo, roots)) == []))
        # A content-equal restore (the mutant pattern) is not a change.
        (repo / "packages/api.py").write_bytes(b"a = 9\n")
        (repo / "packages/api.py").write_bytes(b"a = 2\n")
        cases.append(("restored-bytes-equal", compare(before, snapshot(repo, roots)) == []))
    for name, ok in cases:
        print("selftest", name, "ok" if ok else "FAILED")
        failures += not ok
    print(f"untouched-check selftest: {len(cases) - failures} of {len(cases)}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    repo = pathlib.Path.cwd()
    if argv == ["--record"]:
        snap = snapshot(repo)
        (PLAN / MANIFEST).write_bytes((json.dumps(snap, indent=1, sort_keys=True) + "\n").encode("utf-8"))
        print(f"{MANIFEST}: {len(snap)} files under {', '.join(ROOTS)}")
        return 0
    if argv:
        print(__doc__)
        return 2
    path = PLAN / MANIFEST
    if not path.is_file():
        print(f"PROBLEM: {path} is missing; run row 0 first")
        return 1
    problems = compare(json.loads(path.read_text(encoding="utf-8")), snapshot(repo))
    for p in problems:
        print("PROBLEM:", p)
    print("untouched-check:", "ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
