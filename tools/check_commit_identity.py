"""Refuse a commit identity other than the repository's noreply address.

Usage::

    uv run python tools/check_commit_identity.py [--repo PATH] [--commit REV] [--expected ADDRESS]

Identity mode (no ``--commit``) checks what ``git commit`` would record now: the author and
committer addresses from ``git var GIT_AUTHOR_IDENT`` and ``git var GIT_COMMITTER_IDENT`` (which
resolve ``user.email``, ``author.email``, ``committer.email``, the ``GIT_AUTHOR_*`` and
``GIT_COMMITTER_*`` variables and ``EMAIL``), the two email variables themselves, and
``git config --get user.email``. Commit mode (``--commit REV``) checks the author and committer
addresses stored in that commit (``%ae`` and ``%ce``, without the mailmap), which is what a push
publishes.

Output: ``check_commit_identity: ok`` and exit 0, or one ``check_commit_identity: refused
<reason>`` line per reason and exit 1. The reasons, in order: ``identity_env:GIT_AUTHOR_EMAIL``,
``identity_env:GIT_COMMITTER_EMAIL``, ``author_not_noreply``, ``committer_not_noreply``,
``config_mismatch``, ``unconfigured``. A usage error, a path that is not a git work tree, or a
rev that does not resolve exits 2.

Nothing this tool prints holds an address or any git stderr: git's message for a missing
identity names the user and the host, so stderr is captured and dropped, and a usage error does
not echo the arguments. ``--expected`` exists for tests only; the commit script never passes it.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import NoReturn

EXPECTED_EMAIL = "219344396+matbanik@users.noreply.github.com"
PREFIX = "check_commit_identity:"
USAGE = "usage: check_commit_identity.py [--repo PATH] [--commit REV] [--expected ADDRESS]"


class _Usage(Exception):
    """Raised for any usage error; carries a fixed reason that holds no argument text."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:  # argparse would echo the bad argument
        raise _Usage("unrecognised or malformed arguments")


class _GitMissing(Exception):
    pass


def _git(repo: str, *args: str) -> tuple[int, str]:
    """Run git in ``repo``; return its exit code and stdout. Its stderr is always dropped."""
    try:
        result = subprocess.run(
            ["git", "-C", repo, *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise _GitMissing from exc
    return result.returncode, result.stdout


def _address(ident: str) -> str | None:
    start = ident.find("<")
    end = ident.find(">", start + 1)
    if start < 0 or end < 0:
        return None
    return ident[start + 1 : end]


def _identity_reasons(repo: str, expected: str) -> list[str]:
    reasons: list[str] = []
    for name in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
        value = os.environ.get(name)
        if value is not None and value != expected:
            reasons.append(f"identity_env:{name}")
    unconfigured = False
    for kind, var in (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT")):
        code, out = _git(repo, "var", var)
        if code != 0:
            unconfigured = True
            continue
        if _address(out.strip()) != expected:
            reasons.append(f"{kind}_not_noreply")
    code, out = _git(repo, "config", "--get", "user.email")
    configured = out.strip()
    if code == 0 and configured:
        if configured != expected:
            reasons.append("config_mismatch")
    else:
        unconfigured = True
    if unconfigured:
        reasons.append("unconfigured")
    return reasons


def _commit_reasons(repo: str, rev: str, expected: str) -> list[str] | None:
    code, out = _git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    sha = out.strip()
    if code != 0 or not sha:
        return None
    code, out = _git(repo, "show", "-s", "--no-mailmap", "--format=%ae%x00%ce", sha)
    if code != 0:
        return None
    author, _, committer = out.strip("\r\n").partition("\x00")
    reasons: list[str] = []
    if author != expected:
        reasons.append("author_not_noreply")
    if committer != expected:
        reasons.append("committer_not_noreply")
    return reasons


def _fail_usage(reason: str) -> int:
    print(USAGE, file=sys.stderr)
    print(f"{PREFIX} usage error: {reason}", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    parser = _Parser(prog="check_commit_identity.py", allow_abbrev=False)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--commit")
    parser.add_argument("--expected", default=EXPECTED_EMAIL)
    try:
        args = parser.parse_args(argv)
    except _Usage as exc:
        return _fail_usage(str(exc))
    if not args.expected or not args.repo or (args.commit is not None and not args.commit):
        return _fail_usage("an argument is empty")
    try:
        code, _ = _git(args.repo, "rev-parse", "--git-dir")
        if code != 0:
            print(f"{PREFIX} error: --repo is not a git work tree", file=sys.stderr)
            return 2
        if args.commit is None:
            reasons = _identity_reasons(args.repo, args.expected)
        else:
            found = _commit_reasons(args.repo, args.commit, args.expected)
            if found is None:
                print(f"{PREFIX} error: --commit does not name a commit", file=sys.stderr)
                return 2
            reasons = found
    except _GitMissing:
        print(f"{PREFIX} error: git could not be run", file=sys.stderr)
        return 2
    if not reasons:
        print(f"{PREFIX} ok")
        return 0
    for reason in reasons:
        print(f"{PREFIX} refused {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
