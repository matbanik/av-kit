"""Session 57 version bump and notices line (task row 2; implementation-plan.md VERSION_ONE,
NOTICE_LINE, D-461, D-465).

Usage: ``python version-bump.py (--apply | --dry-run DIR | --check)``

``--apply`` replaces bytes in place in the work tree. Each edit names its exact old bytes and how
many times they must occur; if any count is off, nothing is written. Every file keeps its line
endings: an edit's new text uses the file's own line break, and after the edit the file must hold
only that break, with the line count the plan expects. ``--dry-run DIR`` does the same on copies
under DIR (which must sit under C:/Temp/av-kit) and leaves the work tree alone. ``--check`` writes
nothing: it exits 0 only when every surface reads rc.2 and the one rc.1 name left is the FFmpeg
source archive's (D-465 A).

The script prints file names, counts and line endings only, never file contents.
Exit 0 = done, 1 = refused, 2 = usage.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
SCRATCH = pathlib.Path("C:/Temp/av-kit")
OLD_NPM, NEW_NPM = b"0.1.0-rc.1", b"0.1.0-rc.2"
OLD_PY, NEW_PY = b"0.1.0rc1", b"0.1.0rc2"
ARCHIVE = b"av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz"
NOTICE_AFTER = b"  as subprocesses and never links them.{nl}"
NOTICE_LINE = (
    b"- **DVD libraries:** this build also links libdvdread and libdvdnav, and through them libdvdcss,{nl}"
    b"  into `ffmpeg.exe`. av-kit never uses DVD input.{nl}"
)

#: path -> (line break, lines before, lines after, [(old, new, count)]); {nl} is the file's break.
EDITS: dict[str, tuple[bytes, int, int, list[tuple[bytes, bytes, int]]]] = {
    "ui/package.json": (b"\r\n", 71, 71, [(OLD_NPM, NEW_NPM, 1)]),
    "ui/package-lock.json": (b"\r\n", 11338, 11338, [(OLD_NPM, NEW_NPM, 2)]),
    "mcp-server/package.json": (b"\r\n", 26, 26, [(OLD_NPM, NEW_NPM, 1)]),
    "mcp-server/package-lock.json": (b"\r\n", 2896, 2896, [(OLD_NPM, NEW_NPM, 2)]),
    "mcp-server/src/index.ts": (b"\r\n", 35, 35, [(OLD_NPM, NEW_NPM, 1)]),
    "pyproject.toml": (b"\n", 48, 48, [(OLD_PY, NEW_PY, 1)]),
    "packages/api/pyproject.toml": (b"\n", 25, 25, [(OLD_PY, NEW_PY, 1)]),
    "packages/core/pyproject.toml": (b"\n", 18, 18, [(OLD_PY, NEW_PY, 1)]),
    "packages/infrastructure/pyproject.toml": (b"\r\n", 30, 30, [(OLD_PY, NEW_PY, 1)]),
    "packages/api/src/avkit_api/__init__.py": (b"\n", 5, 5, [(OLD_PY, NEW_PY, 1)]),
    "uv.lock": (b"\n", 3361, 3361, [(b'version = "0.1.0rc1"', b'version = "0.1.0rc2"', 4)]),
    "openapi.committed.json": (b"\r\n", 6516, 6516, [(b'"version": "0.1.0rc1"', b'"version": "0.1.0rc2"', 1)]),
    "packaging/THIRD_PARTY_NOTICES.md": (
        b"\r\n",
        224,
        226,
        [
            (b"releases/tag/v0.1.0-rc.1", b"releases/tag/v0.1.0-rc.2", 1),
            (NOTICE_AFTER, NOTICE_AFTER + NOTICE_LINE, 1),
        ],
    ),
}


def _fill(text: bytes, nl: bytes) -> bytes:
    return text.replace(b"{nl}", nl)


def _endings(data: bytes) -> tuple[int, int]:
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf


def plan_edits(base: pathlib.Path) -> tuple[dict[str, bytes], list[str]]:
    """Return each file's new bytes, or the problems; nothing is written here."""
    out: dict[str, bytes] = {}
    problems: list[str] = []
    for rel, (nl, before, after, edits) in EDITS.items():
        path = base / rel
        if not path.is_file():
            problems.append(f"{rel}: missing")
            continue
        data = path.read_bytes()
        crlf, lf = _endings(data)
        want = (before, 0) if nl == b"\r\n" else (0, before)
        if (crlf, lf) != want:
            problems.append(f"{rel}: endings CRLF={crlf} LF={lf}, want CRLF={want[0]} LF={want[1]}")
            continue
        new = data
        for old, repl, count in edits:
            old_b, new_b = _fill(old, nl), _fill(repl, nl)
            seen = new.count(old_b)
            if seen != count:
                problems.append(f"{rel}: an edit's old bytes occur {seen} times, want {count}")
                break
            new = new.replace(old_b, new_b)
        else:
            crlf, lf = _endings(new)
            want = (after, 0) if nl == b"\r\n" else (0, after)
            if (crlf, lf) != want:
                problems.append(f"{rel}: after the edit CRLF={crlf} LF={lf}, want CRLF={want[0]} LF={want[1]}")
                continue
            out[rel] = new
    return out, problems


def check(base: pathlib.Path) -> list[str]:
    problems: list[str] = []
    for rel, (nl, _before, after, _edits) in EDITS.items():
        data = (base / rel).read_bytes()
        crlf, lf = _endings(data)
        want = (after, 0) if nl == b"\r\n" else (0, after)
        if (crlf, lf) != want:
            problems.append(f"{rel}: CRLF={crlf} LF={lf}, want CRLF={want[0]} LF={want[1]}")
        rest = data.replace(ARCHIVE, b"")
        for old in (OLD_NPM, OLD_PY):
            if old in rest:
                problems.append(f"{rel}: still holds {old.decode()}")
        if rel == "packaging/THIRD_PARTY_NOTICES.md":
            if data.count(ARCHIVE) != 1 or _fill(NOTICE_LINE, nl) not in data or b"releases/tag/v0.1.0-rc.2" not in data:
                problems.append(f"{rel}: the archive name, the tag URL or the DVD line is not as planned")
        elif NEW_NPM not in data and NEW_PY not in data:
            problems.append(f"{rel}: holds no rc.2 version")
    return problems


def write(base: pathlib.Path, new: dict[str, bytes]) -> None:
    for rel, data in new.items():
        path = base / rel
        path.write_bytes(data)
        if path.read_bytes() != data:
            raise SystemExit(f"{rel}: read back differs")
        crlf, lf = _endings(data)
        print(f"wrote {rel}: CRLF={crlf} LF={lf} sha256={hashlib.sha256(data).hexdigest()}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", type=pathlib.Path, metavar="DIR")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.check:
        problems = check(ROOT)
        for p in problems:
            print("problem:", p)
        print(f"version-bump --check: {len(problems)} problems")
        return 1 if problems else 0

    if args.dry_run:
        dest = args.dry_run.resolve()
        if not str(dest).lower().startswith(str(SCRATCH.resolve()).lower() + "\\"):
            print(f"refused: {dest} is outside {SCRATCH}")
            return 2
        if dest.exists():
            shutil.rmtree(dest)
        for rel in EDITS:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest / rel)
        base = dest
    else:
        base = ROOT

    new, problems = plan_edits(base)
    for p in problems:
        print("problem:", p)
    if problems:
        print(f"version-bump: refused, {len(problems)} problems, nothing written")
        return 1
    write(base, new)
    after = check(base)
    for p in after:
        print("problem:", p)
    print(f"version-bump: {len(new)} files written under {base}, {len(after)} problems after")
    return 1 if after else 0


if __name__ == "__main__":
    sys.exit(main())
