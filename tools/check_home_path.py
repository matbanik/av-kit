"""Refuse a tracked or untracked file that holds the home folder's full path.

Usage::

    uv run python tools/check_home_path.py [--repo PATH] [--home PATH] [--allowlist PATH] [--prune]

The files are those ``git ls-files -z --cached --others --exclude-standard`` lists: tracked
files and untracked files that are not ignored. A path under ``.agent/fleet/hub/`` and the secret
files (``.mcp.json``, ``mcp-token.txt``, ``.claude.json``, ``.env``, ``.env.*`` and
``.claude/settings.local.json``) are dropped before anything is read. A listed path that is
missing or is not a regular file is skipped.

Each file is decoded without raising. A byte-order mark sets the encoding (UTF-32LE, UTF-32BE,
UTF-16LE, UTF-16BE, then UTF-8, in that order). A file with no mark and a NUL byte is read in five
views: its bytes as UTF-8 and as UTF-16LE, UTF-16BE, UTF-32LE and UTF-32BE; such a file counts in
``nul=``. Any other file is UTF-8. Lines are numbered by ``\\n`` in each view.

The pattern is built from ``--home`` (default: the user's home folder). A home with a drive letter
is a Windows path, matched case-insensitively in its drive form and its Git Bash form (``/c/...``,
``/mnt/c/...``); any other home is a POSIX path, matched case-sensitively. The last segment must
end at a boundary: the end of the line, a separator, a character Windows forbids in a name,
whitespace, a quote or a backtick, or a run of ``.,;!)]}`` followed by one of those. A home with
fewer than two segments below the root is a usage error.

The allow-list (default ``<repo>/tools/home_path_allowlist.txt``) holds ``<sha256>  <path>``
lines, sorted and unique, with ``#`` comments and blank lines. The digest is the SHA-256 of the
file's bytes with each CRLF read as LF. A listed file whose digest matches is exempt; a listed
file whose digest differs prints ``changed <path>`` if it holds the path and ``stale <path>`` if
not; a listed path that is not read prints ``stale <path>``. ``--prune`` removes the stale
entries from the allow-list and keeps every other line byte for byte; it never adds an entry or
writes a digest.

Output: ``check_home_path: found <path>:<line>`` per instance, sorted, then the ``changed`` and
``stale`` lines, then ``check_home_path: refused found=<n> changed=<c> stale=<m>`` and exit 1; or
``check_home_path: ok files=<n> allowlisted=<m> nul=<k>`` and exit 0. A usage error, a path that
is not a git work tree, a home that is too short, a missing or malformed allow-list, a file that
cannot be read, or git that cannot run exits 2. Nothing this tool prints holds the home folder,
a line of a scanned file, or a line of the allow-list.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import NoReturn

PREFIX = "check_home_path:"
USAGE = "usage: check_home_path.py [--repo PATH] [--home PATH] [--allowlist PATH] [--prune]"
ALLOWLIST = "tools/home_path_allowlist.txt"
HUB = ".agent/fleet/hub/"
SECRET_NAMES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")

# The boundary after the last segment: a stop character or the end of the line, either at once
# or after a run of sentence punctuation.
_STOP = r"""[\\/<>:"|?*\x00-\x1f\s'`]"""
_BOUNDARY = rf"(?=$|{_STOP}|[.,;!)\]}}]+(?:$|{_STOP}))"
_ENTRY = re.compile(r"([0-9a-f]{64})  (.+)")
_BOMS = (
    (b"\xff\xfe\x00\x00", "utf-32-le"),
    (b"\x00\x00\xfe\xff", "utf-32-be"),
    (b"\xff\xfe", "utf-16-le"),
    (b"\xfe\xff", "utf-16-be"),
    (b"\xef\xbb\xbf", "utf-8"),
)
_NUL_VIEWS = ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be")


class _Usage(Exception):
    """Raised for any usage error; carries a fixed reason that holds no argument text."""


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:  # argparse would echo the bad argument
        raise _Usage("unrecognised or malformed arguments")


class _GitMissing(Exception):
    pass


class _Unreadable(Exception):
    pass


def _git(repo: str, *args: str) -> tuple[int, bytes]:
    """Run git in ``repo``; return its exit code and stdout bytes. Its stderr is always dropped."""
    try:
        result = subprocess.run(
            ["git", "-C", repo, *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise _GitMissing from exc
    return result.returncode, result.stdout


def home_pattern(home: str) -> re.Pattern[str]:
    """The pattern for HOME's full path; raises _Usage for a home with fewer than two segments."""
    if re.match(r"[A-Za-z]:", home):
        win = PureWindowsPath(home)
        segments = [s for s in win.parts[1:] if s not in ("\\", "/")]
        if len(segments) < 2:
            raise _Usage("--home has fewer than two segments below the root")
        drive = re.escape(win.drive[0])
        tail = "".join(r"[\\/]+" + re.escape(s) for s in segments)
        body = rf"(?:(?<![A-Za-z]){drive}:{tail}|[\\/]{drive}{tail})"
        return re.compile(body + _BOUNDARY, re.IGNORECASE)
    posix = PurePosixPath(home)
    segments = list(posix.parts[1:]) if posix.is_absolute() else []
    if len(segments) < 2:
        raise _Usage("--home has fewer than two segments below the root")
    return re.compile(r"(?<![A-Za-z0-9_])" + "/+".join(re.escape(s) for s in segments) + _BOUNDARY)


def _excluded(path: str) -> bool:
    """The hub and the secret files: never statted, opened or read."""
    if path.startswith(HUB):
        return True
    name = path.rsplit("/", 1)[-1].lower()
    return (
        name in SECRET_NAMES
        or name.startswith(".env.")
        or path.lower().endswith(".claude/settings.local.json")
    )


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _views(raw: bytes) -> tuple[list[str], bool]:
    """The decoded views of RAW, and whether RAW has no mark and a NUL byte."""
    for mark, codec in _BOMS:
        if raw.startswith(mark):
            errors = "surrogateescape" if codec == "utf-8" else "replace"
            return [raw[len(mark) :].decode(codec, errors)], False
    if b"\x00" in raw:
        views = [raw.decode("utf-8", "surrogateescape")]
        views += [raw.decode(codec, "replace") for codec in _NUL_VIEWS]
        return views, True
    return [raw.decode("utf-8", "surrogateescape")], False


def _instances(raw: bytes, pattern: re.Pattern[str]) -> tuple[list[int], bool]:
    views, nul = _views(raw)
    lines: set[int] = set()
    for view in views:
        for number, line in enumerate(view.split("\n"), start=1):
            if pattern.search(line):
                lines.add(number)
    return sorted(lines), nul


def digest(raw: bytes) -> str:
    """The SHA-256, lowercase hex, of RAW with each CRLF read as LF."""
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def _bad_path(path: str) -> bool:
    parts = path.split("/")
    return (
        path != path.strip()
        or path.startswith("/")
        or re.match(r"[A-Za-z]:", path) is not None
        or "\\" in path
        or any(part in ("", ".", "..") for part in parts)
        or path.startswith(HUB)
    )


def _read_allowlist(raw: bytes) -> tuple[list[str], dict[str, tuple[str, int]]]:
    """The allow-list's lines (each with its ending) and its entries: path -> (digest, index)."""
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _Usage("the allowlist is not UTF-8") from exc
    lines = text.splitlines(keepends=True)
    entries: dict[str, tuple[str, int]] = {}
    previous = ""
    for index, line in enumerate(lines):
        content = line.rstrip("\n")
        content = content[:-1] if content.endswith("\r") else content
        if not content.strip() or content.startswith("#"):
            continue
        match = _ENTRY.fullmatch(content)
        path = match.group(2) if match else ""
        if not match or _bad_path(path) or path in entries or path < previous:
            raise _Usage(f"allowlist line {index + 1} is malformed")
        entries[path] = (match.group(1), index)
        previous = path
    return lines, entries


def _listed(top: str) -> list[str]:
    code, out = _git(top, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if code != 0:
        raise _GitMissing
    names = {name.decode("utf-8", "surrogateescape") for name in out.split(b"\x00") if name}
    return sorted(name for name in names if not _excluded(name))


def _fail_usage(reason: str) -> int:
    print(USAGE, file=sys.stderr)
    print(f"{PREFIX} usage error: {reason}", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    parser = _Parser(prog="check_home_path.py", allow_abbrev=False)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--home")
    parser.add_argument("--allowlist")
    parser.add_argument("--prune", action="store_true")
    try:
        args = parser.parse_args(argv)
        if not args.repo or args.home == "" or args.allowlist == "":
            raise _Usage("an argument is empty")
        pattern = home_pattern(args.home if args.home is not None else str(Path.home()))
    except _Usage as exc:
        return _fail_usage(str(exc))
    try:
        code, out = _git(args.repo, "rev-parse", "--show-toplevel")
        top = out.decode("utf-8", "surrogateescape").strip()
        if code != 0 or not top:
            print(f"{PREFIX} error: --repo is not a git work tree", file=sys.stderr)
            return 2
        allow_path = Path(args.allowlist) if args.allowlist else Path(top) / ALLOWLIST
        if not allow_path.is_file():
            return _fail_usage("the allowlist is missing")
        try:
            allow_raw = allow_path.read_bytes()
        except OSError:
            return _fail_usage("the allowlist cannot be read")
        lines, entries = _read_allowlist(allow_raw)
        files = _listed(top)
        return _check(top, files, pattern, allow_path, allow_raw, lines, entries, args.prune)
    except _Usage as exc:
        return _fail_usage(str(exc))
    except _GitMissing:
        print(f"{PREFIX} error: git could not be run", file=sys.stderr)
        return 2
    except _Unreadable as exc:
        print(f"{PREFIX} cannot read {exc}", file=sys.stderr)
        return 2


def _check(
    top: str,
    files: list[str],
    pattern: re.Pattern[str],
    allow_path: Path,
    allow_raw: bytes,
    lines: list[str],
    entries: dict[str, tuple[str, int]],
    prune: bool,
) -> int:
    found: list[tuple[str, int]] = []
    changed: list[str] = []
    stale: list[str] = []
    read = allowlisted = nul = 0
    seen: set[str] = set()
    for path in files:
        full = Path(top) / path
        try:
            mode = os.lstat(full).st_mode
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise _Unreadable(path) from exc
        if not stat.S_ISREG(mode):
            continue
        try:
            raw = _read_bytes(full)
        except OSError as exc:
            raise _Unreadable(path) from exc
        read += 1
        seen.add(path)
        entry = entries.get(path)
        if entry is not None and digest(raw) == entry[0]:
            allowlisted += 1
            continue
        numbers, has_nul = _instances(raw, pattern)
        nul += has_nul
        if entry is not None:
            (changed if numbers else stale).append(path)
        else:
            found.extend((path, n) for n in numbers)
    stale.extend(path for path in entries if path not in seen)
    stale.sort()
    if prune and stale:
        drop = {entries[path][1] for path in stale}
        kept = "".join(line for index, line in enumerate(lines) if index not in drop)
        allow_path.write_bytes(kept.encode("utf-8"))
        print(f"{PREFIX} pruned {len(stale)} stale entr{'y' if len(stale) == 1 else 'ies'}")
        stale = []
    for path, number in sorted(found):
        print(f"{PREFIX} found {path}:{number}")
    for path in sorted(changed):
        print(f"{PREFIX} changed {path}")
    for path in stale:
        print(f"{PREFIX} stale {path}")
    if found or changed or stale:
        print(f"{PREFIX} refused found={len(found)} changed={len(changed)} stale={len(stale)}")
        return 1
    print(f"{PREFIX} ok files={read} allowlisted={allowlisted} nul={nul}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
