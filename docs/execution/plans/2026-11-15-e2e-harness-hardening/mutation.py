"""Session 78 hint mutant (task rows 9 to 11; implementation-plan.md §The hint tests, AC-16).

Usage, from the repository root:

* ``python mutation.py apply`` -- binds Capture's Save and Region hints to the wrong chord
  (``Ctrl+O``), the in-memory probe of CAPTURE-HINT-TEST-PRESENCE-ONLY made real. Each anchor in
  ``EDITS`` must occur exactly once. The original bytes, their SHA-256 and the file's
  ``st_atime_ns``/``st_mtime_ns`` are kept in ``STATE_DIR`` first. Refused while a mutant is
  already applied.
* ``python mutation.py restore`` -- writes the kept bytes back, resets both timestamps to the
  kept nanoseconds (``ui/tests/e2e/global-setup.ts`` refuses an ``out/`` older than any source
  file, so a restored file must not look newer), then checks the SHA-256 and ``st_mtime_ns``
  and removes the state. Refused when no mutant is applied.
* ``python mutation.py status`` -- exits 0 only when no mutant is applied and the file's SHA-256
  equals its entry in this plan's ``baseline-scope.json`` (row 0), so the file Session 78 never
  edits is byte for byte the file row 0 saw.
* ``python mutation.py --selftest`` -- runs apply, restore and the refusals on a scratch copy.

The edits change bytes inside single lines only, so the file's CRLF line endings are kept.
Nothing here touches git.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import sys
import tempfile

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-e2e-harness-hardening")
TARGET = pathlib.Path("ui/src/renderer/src/features/capture/CapturePage.tsx")
STATE_DIR = pathlib.Path("C:/Temp/av-kit/e2e-harness-hardening/mutation")
EDITS = (
    (b'shortcut="Ctrl+S"', b'shortcut="Ctrl+O"'),
    (b"aria-keyshortcuts={ariaKeyshortcuts('Ctrl+Enter')}", b"aria-keyshortcuts={ariaKeyshortcuts('Ctrl+O')}"),
    (b'title="Capture region (Ctrl+Enter)"', b'title="Capture region (Ctrl+O)"'),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def apply(target: pathlib.Path, state_dir: pathlib.Path) -> list[str]:
    meta = state_dir / "state.json"
    if meta.exists():
        return [f"a mutant is already applied ({meta}); restore it first"]
    data = target.read_bytes()
    problems = []
    for old, _new in EDITS:
        n = data.count(old)
        if n != 1:
            problems.append(f"anchor {old!r} occurs {n} time(s) in {target}, expected 1")
    if problems:
        return problems
    st = os.stat(target)
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "original.bytes").write_bytes(data)
    meta.write_text(
        json.dumps({"target": str(target), "sha256": sha(data), "atime_ns": st.st_atime_ns, "mtime_ns": st.st_mtime_ns}, indent=2),
        encoding="utf-8",
    )
    mutated = data
    for old, new in EDITS:
        mutated = mutated.replace(old, new, 1)
    target.write_bytes(mutated)
    print("mutation applied", target, "original sha256", sha(data), "mutant sha256", sha(mutated))
    return []


def restore(target: pathlib.Path, state_dir: pathlib.Path) -> list[str]:
    meta = state_dir / "state.json"
    if not meta.exists():
        return [f"no mutant is applied ({meta} absent)"]
    state = json.loads(meta.read_text(encoding="utf-8"))
    data = (state_dir / "original.bytes").read_bytes()
    if sha(data) != state["sha256"]:
        return ["the kept original bytes do not match their recorded SHA-256; nothing written"]
    target.write_bytes(data)
    os.utime(target, ns=(state["atime_ns"], state["mtime_ns"]))
    problems = []
    if sha(target.read_bytes()) != state["sha256"]:
        problems.append(f"{target} SHA-256 differs after restore")
    if os.stat(target).st_mtime_ns != state["mtime_ns"]:
        problems.append(f"{target} st_mtime_ns differs after restore")
    if not problems:
        shutil.rmtree(state_dir)
        print("mutation restored", target, "sha256", state["sha256"], "mtime_ns", state["mtime_ns"])
    return problems


def status(target: pathlib.Path, state_dir: pathlib.Path, scope_file: pathlib.Path) -> list[str]:
    problems = []
    if (state_dir / "state.json").exists():
        problems.append("a mutant is applied; run restore")
    got = sha(target.read_bytes())
    want = json.loads(scope_file.read_text(encoding="utf-8")).get(target.as_posix())
    print("status", target, "sha256", got, "baseline-scope", want)
    if got != want:
        problems.append(f"{target} SHA-256 differs from baseline-scope.json")
    return problems


def selftest() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        target = root / "CapturePage.tsx"
        clean = b"a\r\n" + b"\r\n".join(old for old, _ in EDITS) + b"\r\nz\r\n"
        target.write_bytes(clean)
        os.utime(target, ns=(1_600_000_000_000_000_000, 1_600_000_000_123_456_700))
        state = root / "state"
        scope = root / "scope.json"
        scope.write_text(json.dumps({target.as_posix(): sha(clean)}), encoding="utf-8")
        cases = [
            ("status-clean", status(target, state, scope), False),
            ("apply", apply(target, state), False),
            ("mutant-has-no-anchor", [] if all(old not in target.read_bytes() for old, _ in EDITS) else ["anchor left"], False),
            ("mutant-keeps-crlf", [] if target.read_bytes().count(b"\n") == target.read_bytes().count(b"\r\n") else ["LF"], False),
            ("status-while-applied", status(target, state, scope), True),
            ("apply-twice", apply(target, state), True),
            ("restore", restore(target, state), False),
            ("restored-bytes", [] if target.read_bytes() == clean else ["bytes differ"], False),
            ("restored-mtime", [] if os.stat(target).st_mtime_ns == 1_600_000_000_123_456_700 else ["mtime differs"], False),
            ("restore-twice", restore(target, state), True),
        ]
        target.write_bytes(clean + EDITS[0][0])
        cases.append(("duplicate-anchor", apply(target, state), True))
        target.write_bytes(b"nothing here\r\n")
        cases.append(("missing-anchor", apply(target, state), True))
        cases.append(("status-other-bytes", status(target, state, scope), True))
        for name, problems, expect_refused in cases:
            ok = bool(problems) == expect_refused
            print(f"{name}: {'refused' if problems else 'ok'} (expected {'refused' if expect_refused else 'ok'}) {problems[:1]}")
            if not ok:
                failures.append(name)
    print(f"mutation selftest: {len(failures)} failure(s) {failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv == ["apply"]:
        problems = apply(TARGET, STATE_DIR)
    elif argv == ["restore"]:
        problems = restore(TARGET, STATE_DIR)
    elif argv == ["status"]:
        problems = status(TARGET, STATE_DIR, PLAN / "baseline-scope.json")
    else:
        print(__doc__)
        return 2
    for p in problems:
        print("PROBLEM:", p)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
