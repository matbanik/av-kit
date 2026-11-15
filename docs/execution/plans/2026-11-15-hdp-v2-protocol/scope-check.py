"""Session 85 scope guard (implementation-plan.md §Verification Plan 1 and §Stop Conditions S3, S4).

``--record`` (row 0) checks that every file this session edits still equals the base commit
(CRLF read as LF: the blobs are LF, the work tree CRLF), else exit 10 (S3). It then writes
``baseline-content.txt``: HEAD, the SHA-256 of every path that is already dirty (another
session's uncommitted work), and the SHA-256 of the closeout validator (AC-18).

``--check`` (each S4 check and the gate's ``scope-paths`` step) refuses, exit 1:

* HEAD differs from the recorded HEAD;
* a changed path that is neither in this session's scope nor dirty at row 0;
* a path dirty at row 0, outside this session's scope, whose content changed;
* a changed closeout validator.

``--selftest`` proves each refusal in a scratch git repository. Run from anywhere.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import importlib.util
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PLAN = "docs/execution/plans/2026-11-15-hdp-v2-protocol"
BASE = "6813232d8769be71eb6e72505b6f39c58c11bddd"
VALIDATOR = "tools/validate_closeout_artifacts.py"
RECORD = f"{PLAN}/baseline-content.txt"
#: The closeout artifacts this session writes, besides EDITED and its own plan folder.
ARTIFACTS = [
    f"{PLAN}/*",
    ".agent/context/handoffs/2026-11-15-hdp-v2-protocol-*",
    "docs/execution/reflections/2026-11-15-hdp-v2-protocol-*",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
]


def _edited() -> list[str]:
    spec = importlib.util.spec_from_file_location("hdp_check", HERE / "hdp-check.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return list(mod.EDITED)


def _git(root: pathlib.Path, *args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout


def _sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "absent"


def changed_paths(root: pathlib.Path) -> list[str]:
    raw = _git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    out, skip = [], False
    for item in raw:
        if skip:
            skip = False
            continue
        if len(item) < 4:
            continue
        status, path = item[:2].decode(), item[3:].decode("utf-8")
        out.append(path)
        skip = "R" in status or "C" in status
    return sorted(set(out))


def in_scope(path: str, scope: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pat) for pat in scope)


def record(root: pathlib.Path, base: str, edited: list[str], validator: str,
           scope: list[str]) -> tuple[list[str], list[str]]:
    bad = []
    for rel in edited:
        work = (root / rel).read_bytes().replace(b"\r\n", b"\n")
        blob = _git(root, "show", f"{base}:{rel}").replace(b"\r\n", b"\n")
        if work != blob:
            bad.append(rel)
    lines = [f"HEAD {_git(root, 'rev-parse', 'HEAD').decode().strip()}",
             f"VALIDATOR {validator} sha256 {_sha(root / validator)}"]
    for rel in changed_paths(root):
        if not in_scope(rel, scope):
            lines.append(f"DIRTY {rel} sha256 {_sha(root / rel)}")
    return lines, bad


def check(root: pathlib.Path, recorded: list[str], scope: list[str]) -> list[str]:
    head = _git(root, "rev-parse", "HEAD").decode().strip()
    bad, dirty = [], {}
    for line in recorded:
        kind, rest = line.split(" ", 1)
        if kind == "HEAD" and rest != head:
            bad.append(f"HEAD moved: {rest} -> {head} (S4)")
        elif kind == "VALIDATOR":
            rel, _, sha = rest.rsplit(" ", 2)
            if _sha(root / rel) != sha:
                bad.append(f"{rel} changed since row 0 (AC-18, S4)")
        elif kind == "DIRTY":
            rel, _, sha = rest.rsplit(" ", 2)
            dirty[rel] = sha
    for rel, sha in dirty.items():
        if _sha(root / rel) != sha:
            bad.append(f"{rel} is another session's dirty path and changed (S4)")
    for rel in changed_paths(root):
        if not in_scope(rel, scope) and rel not in dirty:
            bad.append(f"{rel} changed outside scope (S4)")
    return bad


def selftest() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        files = {"a.md": "a\r\n", "d.txt": "d\n", "v.py": "v\n", "plan/x.md": "x\n"}
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes(text.replace("\r\n", "\n").encode())
        _git(root, "init", "-q")
        _git(root, "-c", "user.email=s@t", "-c", "user.name=s", "add", "-A")
        _git(root, "-c", "user.email=s@t", "-c", "user.name=s",
             "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        base = _git(root, "rev-parse", "HEAD").decode().strip()
        (root / "a.md").write_bytes(b"a\r\n")  # CRLF in the work tree, LF blob: equal
        (root / "d.txt").write_text("d other session\n", encoding="utf-8")
        scope = ["a.md", "plan/*"]
        lines, bad = record(root, base, ["a.md"], "v.py", scope)
        if bad:
            failures.append(f"CRLF-only difference reported as S3: {bad}")
        if not any(ln.startswith("DIRTY d.txt ") for ln in lines):
            failures.append("dirty path not recorded")

        def expect(label: str, want: bool) -> None:
            got = bool(check(root, lines, scope))
            print(f"{'ok  ' if got == want else 'FAIL'} {label}: refused={got}")
            if got != want:
                failures.append(label)

        expect("clean tree accepted", False)
        (root / "a.md").write_bytes(b"a2\r\n")
        (root / "plan/new.json").write_text("{}", encoding="utf-8")
        expect("in-scope edits accepted", False)
        (root / "d.txt").write_text("d touched\n", encoding="utf-8")
        expect("dirty path changed refused", True)
        (root / "d.txt").write_text("d other session\n", encoding="utf-8")
        (root / "z.txt").write_text("z\n", encoding="utf-8")
        expect("out-of-scope new file refused", True)
        (root / "z.txt").unlink()
        (root / "v.py").write_text("v2\n", encoding="utf-8")
        expect("validator change refused", True)
        (root / "v.py").write_bytes(b"v\n")  # not git checkout: autocrlf would add CR
        expect("restored tree accepted", False)
        (root / "e.txt").write_text("e\n", encoding="utf-8")
        _git(root, "-c", "user.email=s@t", "-c", "user.name=s", "add", "e.txt")
        _git(root, "-c", "user.email=s@t", "-c", "user.name=s",
             "-c", "commit.gpgsign=false", "commit", "-qm", "move")
        expect("HEAD moved refused", True)
        (root / "a.md").write_bytes(b"a changed\r\n")
        _, bad = record(root, base, ["a.md"], "v.py", scope)
        print(f"{'ok  ' if bad == ['a.md'] else 'FAIL'} edited file differs from base: S3={bad}")
        if bad != ["a.md"]:
            failures.append("S3 not reported")
    print(f"scope-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    edited = _edited()
    scope = edited + ARTIFACTS
    if args.record:
        lines, bad = record(ROOT, BASE, edited, VALIDATOR, scope)
        (ROOT / RECORD).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        print("\n".join(lines))
        print(f"{len(edited)} edited file(s); differ from base {BASE[:7]}: {bad}")
        return 10 if bad else 0
    recorded = (ROOT / RECORD).read_text(encoding="utf-8").splitlines()
    bad = check(ROOT, recorded, scope)
    for line in bad:
        print("  ", line)
    print("scope-check: ok" if not bad else f"scope-check: {len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
