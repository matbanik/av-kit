"""Session 57 build identity and build record (implementation-plan.md BUILD_RECORD, D-184, D-462).

A copy of Session 44's with ``BUILD_SCRIPT`` pointing at this plan's build script.

Prints one ``build_inputs <sha256>`` line over the mode, blob and path of every tracked file except
a short exclude list, so a new build input cannot fall outside the identity by being forgotten. The
exclusions are files that never reach the installer: docs, tests, agent files and the smoke tools.

Default mode hashes the work tree as it would be committed, using a temporary index (the real index
is untouched). ``--ref <rev>`` hashes a committed tree instead. The two agree when the commit holds
the same inputs, whatever else it changed.

The tree alone cannot prove what was built, so ``--write-record`` also stores the installer's name,
size and SHA-256, the FFmpeg hashes and the toolchain versions. ``--verify-record`` recomputes the
identity, rehashes the installer and prints every mismatch. ``--selftest`` runs in a scratch
repository and never touches this one.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import importlib.metadata
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import Any

EXCLUDED_PREFIXES = (
    ".agent/",
    ".claude/",
    ".cursor/",
    ".serena/",
    "_inspiration/",
    "docs/",
    "tests/",
    "tools/tests/",
    "ui/tests/",
    "mcp-server/tests/",
    "native/region-picker-tests/",
)
EXCLUDED_FILES = frozenset(
    {
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "GUARDRAILS.md",
        "PROJECT-PROFILE.md",
        "framework.vars",
        "rottiboo.png",
        "tools/smoke_packaged_rc.py",
        "tools/smoke_packaged_tts.py",
    }
)
# The build script lives in the plan folder but decides what gets built.
BUILD_SCRIPT = "docs/execution/plans/2026-11-08-release-rc2/build-rc.ps1"
REINCLUDED = frozenset({BUILD_SCRIPT})

FFMPEG_DIR = "packaging/ffmpeg-win64"
PICKER_DEPS_GLOB = "native/region-picker/publish/*.deps.json"
BACKEND_INTERNAL = "packaging/dist/avkit-backend/_internal"
MS_RUNTIME_PATTERNS = ("api-ms-win-*.dll", "ucrtbase*.dll", "vcruntime140*.dll", "msvcp140*.dll")


def _git(*args: str, cwd: pathlib.Path | None = None, env: dict[str, str] | None = None) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, encoding="utf-8", check=True, cwd=cwd, env=env
    ).stdout.strip()


def in_identity(path: str) -> bool:
    if path in REINCLUDED:
        return True
    if path in EXCLUDED_FILES:
        return False
    return not path.startswith(EXCLUDED_PREFIXES)


def worktree_tree(cwd: pathlib.Path | None = None, env: dict[str, str] | None = None) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        index_env = {**(os.environ if env is None else env), "GIT_INDEX_FILE": str(pathlib.Path(tmp) / "index")}
        _git("read-tree", "HEAD", cwd=cwd, env=index_env)
        _git("add", "-A", cwd=cwd, env=index_env)
        return _git("write-tree", cwd=cwd, env=index_env)


def tree_identity(
    tree: str, cwd: pathlib.Path | None = None, env: dict[str, str] | None = None, verbose: bool = False
) -> str:
    rows: list[tuple[str, str]] = []
    for entry in _git("ls-tree", "-r", "-z", tree, cwd=cwd, env=env).split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode, _kind, sha = meta.split()
        if in_identity(path):
            rows.append((path, f"{mode} {sha} {path}\n"))
    digest = hashlib.sha256()
    for _path, row in sorted(rows):
        digest.update(row.encode("utf-8"))
        if verbose:
            print(row, end="")
    return digest.hexdigest()


def _sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _tool_version(*argv: str) -> str:
    executable = shutil.which(argv[0])
    if executable is None:
        raise SystemExit(f"--write-record: {argv[0]} is not on PATH")
    return subprocess.run(
        [executable, *argv[1:]], capture_output=True, encoding="utf-8", check=True
    ).stdout.strip()


def _npm_package_version(root: pathlib.Path, name: str) -> str:
    manifest = root / "ui" / "node_modules" / name / "package.json"
    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def _dotnet_runtime_packs(root: pathlib.Path) -> list[str]:
    deps = glob.glob(str(root / PICKER_DEPS_GLOB))
    if len(deps) != 1:
        raise SystemExit(f"--write-record: expected one picker .deps.json, found {len(deps)}")
    libraries = json.loads(pathlib.Path(deps[0]).read_text(encoding="utf-8"))["libraries"]
    packs = sorted(name for name in libraries if name.startswith("runtimepack."))
    if not packs:
        raise SystemExit(f"--write-record: {deps[0]} names no runtime pack")
    return packs


def _ms_runtime_hashes(root: pathlib.Path) -> dict[str, str]:
    # PyInstaller takes these from whichever folder on PATH has them first, so they depend on the
    # build machine rather than the tree.
    internal = root / BACKEND_INTERNAL
    found = {
        path.name: _sha256(path)
        for pattern in MS_RUNTIME_PATTERNS
        for path in internal.glob(pattern)
    }
    if not any(name.lower().startswith("vcruntime140") for name in found):
        raise SystemExit(f"--write-record: no vcruntime140 under {internal}")
    return dict(sorted(found.items()))


def write_record(
    out: pathlib.Path, installer: pathlib.Path, ffmpeg_archive: pathlib.Path, expect_inputs: str | None
) -> int:
    root = pathlib.Path(_git("rev-parse", "--show-toplevel"))
    inputs = tree_identity(worktree_tree())
    if expect_inputs is not None and inputs != expect_inputs:
        print(f"inputs changed during the build: started {expect_inputs}, now {inputs}")
        return 1
    installer_abs = installer if installer.is_absolute() else root / installer
    record: dict[str, Any] = {
        "schema": "s44.build-record.v1",
        "build_inputs": inputs,
        "installer": {
            "path": installer_abs.relative_to(root).as_posix(),
            "size": installer_abs.stat().st_size,
            "sha256": _sha256(installer_abs),
        },
        "ffmpeg": {
            "archive_sha256": _sha256(ffmpeg_archive),
            "ffmpeg_sha256": _sha256(root / FFMPEG_DIR / "ffmpeg.exe"),
            "ffprobe_sha256": _sha256(root / FFMPEG_DIR / "ffprobe.exe"),
        },
        "dotnet_runtime_packs": _dotnet_runtime_packs(root),
        "ms_runtime_dlls": _ms_runtime_hashes(root),
        "tools": {
            "node": _tool_version("node", "--version"),
            "npm": _tool_version("npm", "--version"),
            "uv": _tool_version("uv", "--version"),
            "python": sys.version.split()[0],
            "dotnet": _tool_version("dotnet", "--version"),
            "electron": _npm_package_version(root, "electron"),
            "electron_builder": _npm_package_version(root, "electron-builder"),
            "pyinstaller": importlib.metadata.version("pyinstaller"),
        },
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("build_inputs", inputs)
    print("installer", record["installer"]["path"], record["installer"]["size"], record["installer"]["sha256"])
    print("record written:", out)
    return 0


def record_mismatches(
    record: dict[str, Any],
    root: pathlib.Path,
    ref: str | None = None,
    env: dict[str, str] | None = None,
) -> list[str]:
    problems: list[str] = []
    tree = ref if ref is not None else worktree_tree(cwd=root, env=env)
    inputs = tree_identity(tree, cwd=root, env=env)
    print("build_inputs", inputs)
    if inputs != record["build_inputs"]:
        problems.append(f"build_inputs: record {record['build_inputs']}, now {inputs}")
    expected = record["installer"]
    installer = root / expected["path"]
    if not installer.is_file():
        problems.append(f"installer missing: {expected['path']}")
        return problems
    size = installer.stat().st_size
    if size != expected["size"]:
        problems.append(f"installer size: record {expected['size']}, now {size}")
    sha = _sha256(installer)
    if sha != expected["sha256"]:
        problems.append(f"installer sha256: record {expected['sha256']}, now {sha}")
    return problems


def verify_record(path: pathlib.Path, ref: str | None) -> int:
    root = pathlib.Path(_git("rev-parse", "--show-toplevel"))
    problems = record_mismatches(json.loads(path.read_text(encoding="utf-8")), root, ref)
    for problem in problems:
        print("mismatch:", problem)
    print("build record:", "MISMATCH" if problems else "matches", path)
    return 1 if problems else 0


def selftest() -> int:
    failures: list[str] = []

    def check(label: str, passed: bool) -> None:
        print(("ok   " if passed else "FAIL ") + label)
        if not passed:
            failures.append(label)

    with tempfile.TemporaryDirectory() as tmp:
        scratch = pathlib.Path(tmp) / "repo"
        scratch.mkdir()
        empty_config = pathlib.Path(tmp) / "empty-gitconfig"
        empty_config.write_text("", encoding="utf-8")
        # No user or system config, so hooks, autocrlf and excludes cannot change the result.
        env = {**os.environ, "GIT_CONFIG_GLOBAL": str(empty_config), "GIT_CONFIG_NOSYSTEM": "1"}
        env.pop("GIT_INDEX_FILE", None)

        product = (
            "packaging/avkit-backend.spec",
            "ui/electron.vite.config.ts",
            "mcp-server/scripts/bundle.ts",
            "global.json",
            BUILD_SCRIPT,
        )
        non_inputs = ("docs/x.md", "tests/test_x.py", ".agent/y.md", "README.md")
        for name in (*product, *non_inputs):
            target = scratch / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("v1\n", encoding="utf-8")
        installer = scratch / "ui/dist/setup.exe"
        (scratch / ".gitignore").write_text("ui/dist/\n", encoding="utf-8")
        installer.parent.mkdir(parents=True)
        installer.write_bytes(b"installer-v1")

        def commit(message: str) -> None:
            _git("add", "-A", cwd=scratch, env=env)
            _git(
                "-c", "user.name=selftest", "-c", "user.email=selftest@example.invalid",
                "commit", "-q", "-m", message,
                cwd=scratch, env=env,
            )

        def current() -> str:
            return tree_identity(worktree_tree(cwd=scratch, env=env), cwd=scratch, env=env)

        _git("init", "-q", cwd=scratch, env=env)
        commit("base")
        base = current()

        for name in product:
            target = scratch / name
            target.write_text("v2\n", encoding="utf-8")
            check(f"changes identity: {name}", current() != base)
            target.write_text("v1\n", encoding="utf-8")
        check("restored files restore the identity", current() == base)

        for name in non_inputs:
            target = scratch / name
            target.write_text("v2\n", encoding="utf-8")
            check(f"does not change identity: {name}", current() == base)
            target.write_text("v1\n", encoding="utf-8")

        new_config = scratch / "ui/brand-new.config.ts"
        new_config.write_text("v1\n", encoding="utf-8")
        check("a new tracked file changes identity", current() != base)
        new_config.unlink()

        (scratch / "docs/x.md").write_text("v3\n", encoding="utf-8")
        before_commit = current()
        commit("docs only")
        check("--ref HEAD equals the work tree after commit", tree_identity("HEAD", cwd=scratch, env=env) == before_commit)
        check("a docs-only commit keeps the identity", before_commit == base)

        record = {
            "build_inputs": base,
            "installer": {
                "path": "ui/dist/setup.exe",
                "size": installer.stat().st_size,
                "sha256": _sha256(installer),
            },
        }
        check("verify passes on a matching tree and installer", record_mismatches(record, scratch, env=env) == [])
        check("verify passes against --ref HEAD", record_mismatches(record, scratch, "HEAD", env) == [])

        installer.write_bytes(b"installer-v2")
        problems = record_mismatches(record, scratch, env=env)
        check("verify reports a changed installer", any("installer" in p for p in problems))
        installer.write_bytes(b"installer-v1")

        (scratch / "global.json").write_text("v2\n", encoding="utf-8")
        problems = record_mismatches(record, scratch, env=env)
        check("verify reports a changed product file", any("build_inputs" in p for p in problems))
        (scratch / "global.json").write_text("v1\n", encoding="utf-8")

        installer.unlink()
        problems = record_mismatches(record, scratch, env=env)
        check("verify reports a missing installer", any("missing" in p for p in problems))

    print("selftest:", f"FAILED {len(failures)}" if failures else "passed")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", help="hash this committed tree instead of the work tree")
    parser.add_argument("--verbose", action="store_true", help="print every hashed row")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--write-record", type=pathlib.Path, metavar="OUT")
    parser.add_argument("--installer", type=pathlib.Path)
    parser.add_argument("--ffmpeg-archive", type=pathlib.Path)
    parser.add_argument("--expect-inputs", help="refuse the record unless the identity still equals this")
    parser.add_argument("--verify-record", type=pathlib.Path, metavar="PATH")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.verify_record is not None:
        return verify_record(args.verify_record, args.ref)
    if args.write_record is not None:
        if args.installer is None or args.ffmpeg_archive is None:
            parser.error("--write-record needs --installer and --ffmpeg-archive")
        return write_record(args.write_record, args.installer, args.ffmpeg_archive, args.expect_inputs)
    tree = args.ref if args.ref is not None else worktree_tree()
    print("build_inputs", tree_identity(tree, verbose=args.verbose))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
