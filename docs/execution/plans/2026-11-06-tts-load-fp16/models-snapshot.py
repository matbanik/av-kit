"""Session 52 `MODELS_SNAPSHOT` (implementation-plan.md §Packaged and dev checks; Verification Plan §3).

Usage: ``python models-snapshot.py --record OUT.json`` | ``--compare BEFORE.json`` | ``--selftest``.

The snapshot is the relative POSIX name, size and ``mtime_ns`` of every file under the real
models folder (``~/.avkit/models``). It leaves out ``*.lock`` files and the interpreter caches
(``__pycache__`` folders and ``*.pyc``), which an import of the folder's spaCy install can write.
``--record`` refuses to overwrite an existing snapshot, so a later run can't hide a change (S4).
``--compare`` prints every added, removed, resized or rewritten file and exits 1 on any change.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

MODELS_DIR = pathlib.Path.home() / ".avkit" / "models"


def _excluded(rel: pathlib.PurePosixPath) -> bool:
    return rel.suffix in (".lock", ".pyc") or "__pycache__" in rel.parts


def snapshot(root: pathlib.Path) -> dict[str, list[int]]:
    if not root.is_dir():
        raise SystemExit(f"models folder {root} is missing")
    files: dict[str, list[int]] = {}
    for path in sorted(root.rglob("*")):
        rel = pathlib.PurePosixPath(path.relative_to(root).as_posix())
        if path.is_file() and not _excluded(rel):
            stat = path.stat()
            files[str(rel)] = [stat.st_size, stat.st_mtime_ns]
    return files


def diff(before: dict[str, list[int]], after: dict[str, list[int]]) -> list[str]:
    changes = [f"added {name}" for name in sorted(after.keys() - before.keys())]
    changes += [f"removed {name}" for name in sorted(before.keys() - after.keys())]
    for name in sorted(before.keys() & after.keys()):
        (size0, mtime0), (size1, mtime1) = before[name], after[name]
        if size0 != size1:
            changes.append(f"resized {name}: {size0} -> {size1}")
        elif mtime0 != mtime1:
            changes.append(f"rewritten {name}: mtime_ns {mtime0} -> {mtime1}")
    return changes


def record(root: pathlib.Path, out: pathlib.Path) -> int:
    if out.exists():
        print(f"models-snapshot: {out} already exists; refusing to overwrite it (run --compare)")
        return 1
    files = snapshot(root)
    out.write_text(json.dumps({"root": str(root), "files": files}, indent=1) + "\n", encoding="utf-8")
    print(f"models-snapshot: recorded {len(files)} file(s) under {root} -> {out}")
    return 0


def compare(root: pathlib.Path, before_path: pathlib.Path) -> int:
    before = json.loads(before_path.read_text(encoding="utf-8"))
    if before["root"] != str(root):
        print(f"models-snapshot: {before_path} is about {before['root']}, not {root}")
        return 1
    changes = diff(before["files"], snapshot(root))
    for change in changes:
        print("models-snapshot:", change)
    print(f"models-snapshot: {len(before['files'])} file(s) recorded, {len(changes)} change(s)")
    return 1 if changes else 0


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "models"
        (root / "spacy" / "__pycache__").mkdir(parents=True)
        (root / "a.pth").write_bytes(b"x" * 16)
        (root / "spacy" / "m.py").write_text("v1\n", encoding="utf-8")
        out = pathlib.Path(tmp) / "before.json"
        if record(root, out) != 0:
            failures.append("record failed")
        if record(root, out) == 0:
            failures.append("record overwrote an existing snapshot")
        if compare(root, out) != 0:
            failures.append("control: an unchanged folder reported a change")
        (root / "spacy" / "__pycache__" / "m.cpython-312.pyc").write_bytes(b"c")
        (root / "spacy" / "x.pyc").write_bytes(b"c")
        (root / "a.pth.lock").write_bytes(b"")
        if compare(root, out) != 0:
            failures.append("an excluded cache or lock file counted as a change")
        mutations = (
            ("added", lambda: (root / "b.pth").write_bytes(b"y")),
            ("resized", lambda: (root / "a.pth").write_bytes(b"x" * 17)),
            ("removed", lambda: (root / "spacy" / "m.py").unlink()),
        )
        for name, mutate in mutations:
            mutate()
            if compare(root, out) == 0:
                failures.append(f"{name} file not detected")
            out.unlink()
            record(root, out)
        path = root / "a.pth"
        stat = path.stat()
        os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))
        if compare(root, out) == 0:
            failures.append("rewritten file (same size, new mtime) not detected")
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"models-snapshot selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) == 2 and argv[0] == "--record":
        return record(MODELS_DIR, pathlib.Path(argv[1]))
    if len(argv) == 2 and argv[0] == "--compare":
        return compare(MODELS_DIR, pathlib.Path(argv[1]))
    print("usage: models-snapshot.py --record OUT.json | --compare BEFORE.json | --selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
