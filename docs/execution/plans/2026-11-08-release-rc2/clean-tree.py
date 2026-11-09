"""Session 57 clean-tree check before the build (task row 3; implementation-plan.md CLEAN_TREE,
D-462, stop condition S10).

Usage: ``python clean-tree.py [--selftest]``

The tree is clean when HEAD is still the commit row 0 recorded in ``baseline.sha`` and every
changed, deleted or untracked path is one this session's rows 0 to 2 own: the plan folder, this
session's handoff-set files under ``.agent/context/handoffs/``, the version surfaces row 2 bumps, the two test files row 1 edits, and the watch-item test file
(D-470). A path another session left uncommitted is not allowed even when the baseline recorded
it: the build must not carry it, so it goes to Mat as an HDP (the session prompt's clean-tree rule).

That includes an allowed path (round-1 F2): if ``baseline-dirty.txt`` lists a path outside the plan
folder and it is still changed now, it is refused, because row 2's edit would sit on top of
another session's. A baseline line whose path can't be read back exactly (git quoted it, or it is
a rename) is refused as it stands, without being matched.

``--leave-out PATH`` (repeatable) passes one named path of another session's that Mat ruled may
stay out of the build check (Session 57 S10 ruling B). It is refused when the path is a build
input by ``build-identity.py``'s own ``in_identity``, so only paths the build never reads can be
left out; each one that is present is printed.

Renames are not paired (``--no-renames``), so a file renamed into an allowed path still shows its
old path as deleted. Paths come from git NUL-separated, so a space or a quote in a name is read
as it is. The script prints paths and counts only, never file contents.
Exit 0 = clean, 1 = dirty or HEAD moved, 2 = git, ``baseline.sha`` or ``baseline-dirty.txt``
unreadable.
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

PLAN = "docs/execution/plans/2026-11-08-release-rc2"
# This session's handoff-set files (the canonical plan review exists from the gate on), the
# same prefix identity.py's PROJECT_ARTIFACTS and session-gate.ps1's scope use. `.agent/` is
# outside build-identity.py's build inputs.
HANDOFFS = ".agent/context/handoffs/2026-11-08-release-rc2-"
ALLOWED_PREFIXES = (f"{PLAN}/", HANDOFFS)
ALLOWED = frozenset(
    {
        # Row 2's version surfaces (version-bump.py EDITS).
        "ui/package.json",
        "ui/package-lock.json",
        "mcp-server/package.json",
        "mcp-server/package-lock.json",
        "mcp-server/src/index.ts",
        "pyproject.toml",
        "packages/api/pyproject.toml",
        "packages/core/pyproject.toml",
        "packages/infrastructure/pyproject.toml",
        "packages/api/src/avkit_api/__init__.py",
        "uv.lock",
        "openapi.committed.json",
        "packaging/THIRD_PARTY_NOTICES.md",
        # Row 1's Red.
        "tests/unit/test_release_packaging.py",
        "tests/unit/test_packaging_installer.py",
        # Only if the watch item fails again (D-470).
        "ui/tests/e2e/transcript-queue.test.ts",
    }
)


class GitError(Exception):
    pass


def _in_identity():
    spec = importlib.util.spec_from_file_location(
        "build_identity", pathlib.Path(__file__).with_name("build-identity.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.in_identity


def _git(repo: pathlib.Path, *args: str) -> bytes:
    run = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if run.returncode != 0:
        raise GitError(f"git {args[0]} exited {run.returncode}")
    return run.stdout


def _split(out: bytes) -> list[str]:
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]


def baseline_foreign(dirty: bytes) -> tuple[list[str], list[str]]:
    """Split ``baseline-dirty.txt`` into (paths outside the plan folder, unreadable lines).

    Each line is the porcelain line, a tab, then a SHA-256 (``baseline.ps1``); the path is the
    text between column 3 and the last tab.
    """
    paths: list[str] = []
    unreadable: list[str] = []
    for line in dirty.decode("utf-8", "surrogateescape").splitlines():
        if not line.strip():
            continue
        entry, sep, _digest = line.rpartition("\t")
        path = entry[3:] if sep else ""
        if not path or path.startswith('"') or " -> " in path:
            unreadable.append(line)
        elif not path.startswith(ALLOWED_PREFIXES):
            paths.append(path)
    return paths, unreadable


def inspect(
    repo: pathlib.Path, dirty: bytes, leave_out: frozenset[str] = frozenset()
) -> tuple[str, list[str], list[str], list[str], list[str]]:
    """Return (HEAD, paths no row owns, baseline paths still changed, unreadable baseline lines,
    left-out paths present)."""
    head = _git(repo, "rev-parse", "HEAD").decode().strip()
    changed = _split(_git(repo, "diff", "--no-renames", "--name-only", "-z", "HEAD"))
    untracked = _split(_git(repo, "ls-files", "--others", "--exclude-standard", "-z"))
    now = set(changed + untracked)
    left = sorted(now & leave_out)
    now -= leave_out
    outside = sorted({p for p in now if p not in ALLOWED and not p.startswith(ALLOWED_PREFIXES)})
    foreign, unreadable = baseline_foreign(dirty)
    carried = sorted({p for p in foreign if p in now and p not in outside})
    return head, outside, carried, unreadable, left


def verdict(
    repo: pathlib.Path, base_sha: str, dirty: bytes, leave_out: frozenset[str] = frozenset()
) -> int:
    inputs = sorted(p for p in leave_out if _in_identity()(p))
    for p in inputs:
        print(f"clean-tree: refused: {p!r} is a build input and can't be left out")
    if inputs:
        return 1
    try:
        head, outside, carried, unreadable, left = inspect(repo, dirty, leave_out)
    except (GitError, OSError) as exc:
        print(f"clean-tree: unreadable: {exc}")
        return 2
    for p in left:
        print(f"clean-tree: left out by Mat's ruling: {p!r}")
    code = 0
    if head != base_sha:
        print(f"clean-tree: HEAD is {head}, baseline.sha says {base_sha}")
        code = 1
    for p in outside:
        print(f"clean-tree: not this session's: {p!r}")
    for p in carried:
        print(f"clean-tree: changed before row 0 and still changed: {p!r}")
    for line in unreadable:
        print(f"clean-tree: baseline line not read back exactly: {line.split(chr(9))[0]!r}")
    if outside or carried or unreadable:
        code = 1
    print(
        f"clean-tree: {len(outside)} paths outside rows 0 to 2, {len(carried)} carried from the"
        f" baseline, {len(unreadable)} unreadable baseline lines, exit {code}"
    )
    return code


def _selftest() -> int:
    cases = 0
    failures = 0

    def expect(
        name: str,
        repo: pathlib.Path,
        sha: str,
        want: int,
        dirty: bytes = b"",
        leave_out: frozenset[str] = frozenset(),
    ) -> None:
        nonlocal cases, failures
        cases += 1
        got = verdict(repo, sha, dirty, leave_out)
        ok = got == want
        failures += 0 if ok else 1
        print(f"selftest {name}: exit {got}, want {want}: {'ok' if ok else 'FAIL'}")

    with tempfile.TemporaryDirectory(dir="C:/Temp/av-kit") as tmp:
        repo = pathlib.Path(tmp) / "repo"
        repo.mkdir()
        for args in (
            ("init", "-q", "-b", "main"),
            ("config", "user.email", "selftest@example.invalid"),
            ("config", "user.name", "selftest"),
            ("config", "core.autocrlf", "false"),
        ):
            _git(repo, *args)
        for rel in ("ui/package.json", "README.md", "old name.txt"):
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_bytes(b"x\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "base")
        sha = _git(repo, "rev-parse", "HEAD").decode().strip()

        expect("clean", repo, sha, 0)

        (repo / "ui/package.json").write_bytes(b"y\n")
        (repo / PLAN).mkdir(parents=True)
        (repo / PLAN / "task.md").write_bytes(b"t\n")
        expect("allowed modified and plan untracked", repo, sha, 0)

        (repo / HANDOFFS).parent.mkdir(parents=True)
        (repo / f"{HANDOFFS}plan-critical-review.md").write_bytes(b"r\n")
        expect("this session's handoff untracked", repo, sha, 0)
        other = repo / ".agent/context/handoffs/2026-11-08-capture-crop-handoff.md"
        other.write_bytes(b"o\n")
        expect("another session's handoff untracked", repo, sha, 1)
        named = frozenset({other.relative_to(repo).as_posix()})
        expect("another session's handoff left out", repo, sha, 0, leave_out=named)
        other_line = f"?? {other.relative_to(repo).as_posix()}\t{'d' * 64}\n".encode()
        expect("left out though the baseline lists it", repo, sha, 0, other_line, named)
        (repo / "stray.txt").write_bytes(b"s\n")
        expect("left out a build input", repo, sha, 1, leave_out=named | {"stray.txt"})
        expect("left out but another path stays", repo, sha, 1, leave_out=named)
        (repo / "stray.txt").unlink()
        other.unlink()

        (repo / "stray.txt").write_bytes(b"s\n")
        expect("untracked outside", repo, sha, 1)
        (repo / "stray.txt").unlink()

        (repo / "README.md").unlink()
        expect("deleted outside", repo, sha, 1)
        _git(repo, "checkout", "--", "README.md")

        _git(repo, "mv", "old name.txt", "uv.lock")
        expect("rename into an allowed path", repo, sha, 1)
        _git(repo, "mv", "uv.lock", "old name.txt")

        (repo / "old name.txt").write_bytes(b"z\n")
        expect("path with a space", repo, sha, 1)
        _git(repo, "checkout", "--", "old name.txt")

        expect("back to allowed only", repo, sha, 0)
        plan_only = f"?? {PLAN}/task.md\t{'a' * 64}\n".encode()
        expect("baseline lists the plan folder only", repo, sha, 0, plan_only)
        foreign = f" M ui/package.json\t{'b' * 64}\n".encode()
        expect("allowed path changed before row 0", repo, sha, 1, plan_only + foreign)
        expect("baseline line git quoted", repo, sha, 1, f'?? "odd\\tname"\t{"c" * 64}\n'.encode())
        (repo / "ui/package.json").write_bytes(b"x\n")
        expect("baseline path since reverted", repo, sha, 0, foreign)
        expect("HEAD moved", repo, "0" * 40, 1)
        expect("unreadable repo", pathlib.Path(tmp) / "missing", sha, 2)

    print(f"clean-tree selftest: {cases - failures}/{cases} passed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--leave-out", action="append", default=[], metavar="PATH")
    args = parser.parse_args()
    if args.selftest:
        return _selftest()
    root = pathlib.Path(__file__).resolve().parents[4]
    sha_file = root / PLAN / "baseline.sha"
    dirty_file = root / PLAN / "baseline-dirty.txt"
    for f in (sha_file, dirty_file):
        if not f.is_file():
            print(f"clean-tree: unreadable: {PLAN}/{f.name} is missing (row 0 writes it)")
            return 2
    return verdict(
        root,
        sha_file.read_text(encoding="ascii").strip(),
        dirty_file.read_bytes(),
        frozenset(args.leave_out),
    )


if __name__ == "__main__":
    sys.exit(main())
