"""Session 91 line-ending check (task rows 2, 4, 5, 6, 7 and 9, and the gate's ``line-endings``
step; implementation-plan.md §Verification Plan 1, §Files Modified). A copy of Session 90's
(2026-11-17-test-run-reliability/eol-check.py) with this plan's scope and copies. The
conditional ``docs/build-plan/<area>.md`` (row 7 under ``product-race`` only) has no name until
row 7 and is not in SCOPE; ``meu-register.py`` checks its own anchored write.

For each scope path the file now is compared with its row-0 bytes, which row 0 copied to
``C:/Temp/av-kit/e2e-pointer-flakes/baseline-copies/<path>``. The row-0 kind is measured from
those bytes (Python bytes, never grep) and must equal the kind the plan names:

* a CRLF file must have no bare LF;
* an LF file must have no CR;
* a new file (absent at row 0) must have no CR; a new file not yet written is reported, not
  failed;
* in a MIXED file every line inserted or changed since row 0 (``difflib`` opcodes over the lines
  without their endings) must end like the line before it, or like the line after it when it is
  the first line of the file; a line whose text did not change must keep its row-0 ending.

A modified path that is missing now fails. Usage, from the repository root::

    python eol-check.py            # check every scope path
    python eol-check.py --selftest # each rule, on fixtures in a scratch folder
"""

from __future__ import annotations

import difflib
import pathlib
import sys
import tempfile

COPIES = pathlib.Path("C:/Temp/av-kit/e2e-pointer-flakes/baseline-copies")
PLAN = "docs/execution/plans/2026-11-17-e2e-pointer-flakes"
HANDOFF = ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-handoff.md"
CR = b"\r"
CRLF = b"\r\n"
LF = b"\n"

#: Every scope path with the kind the plan names (§Files Modified, §Project files).
SCOPE = {
    "ui/tests/e2e/download-queue.test.ts": "LF",
    "ui/tests/e2e/convert-queue.test.ts": "LF",
    "ui/tests/e2e/capture-inbox.test.ts": "LF",
    "ui/tests/e2e/electron-app.ts": "LF",
    "ui/tests/e2e/electron-env.ts": "LF",
    "ui/tests/e2e/main-error-watch.cjs": "LF",
    "ui/tests/e2e/electron-harness.test.ts": "LF",
    "ui/tests/e2e/main-rejection-watch.test.ts": "LF",
    "ui/tests/e2e/transcript-queue.test.ts": "LF",
    "ui/tests/unit/e2e-harness.test.ts": "LF",
    "ui/tests/unit/rejection-watch.test.ts": "LF",
    "ui/playwright.config.ts": "LF",
    "ui/package.json": "CRLF",
    "ui/src/renderer/src/components/queue/QueueList.tsx": "CRLF",
    "ui/src/renderer/src/components/queue/queue-dnd.ts": "CRLF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/context/known-issues.md": "LF",
    ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md": "LF",
    ".agent/context/meu-status.yaml": "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    "docs/build-plan/build-priority-matrix.md": "CRLF",
    "docs/execution/metrics.md": "CRLF",
    ".agent/context/current-focus.md": "CRLF",
    f"{PLAN}/implementation-plan.md": "LF",
    f"{PLAN}/task.md": "LF",
    f"{PLAN}/flake-run.py": "LF",
    f"{PLAN}/assert-check.py": "LF",
    "ui/tests/e2e/pointer-settle.ts": "NEW",
    "ui/tests/e2e/e2e-diag.ts": "NEW",
    "ui/tests/e2e/e2e-diag.test.ts": "NEW",
    "ui/tests/unit/e2e-pointer.test.ts": "NEW",
    f"{PLAN}/meu-register.py": "NEW",
    HANDOFF: "NEW",
}


def kind_of(raw: bytes) -> str:
    crlf = raw.count(CRLF)
    bare = raw.count(LF) - crlf
    if crlf and bare:
        return "MIXED"
    if crlf:
        return "CRLF"
    if bare:
        return "LF"
    return "none"


def split_lines(raw: bytes) -> list[tuple[bytes, bytes]]:
    """Each line as (text, ending), ending one of CRLF, LF, CR or empty for a last line."""
    out: list[tuple[bytes, bytes]] = []
    for line in raw.splitlines(keepends=True):
        if line.endswith(CRLF):
            out.append((line[:-2], CRLF))
        elif line.endswith((LF, CR)):
            out.append((line[:-1], line[-1:]))
        else:
            out.append((line, b""))
    return out


def _name(ending: bytes) -> str:
    return {CRLF: "CRLF", LF: "LF", CR: "CR", b"": "none"}[ending]


def mixed_problems(old: bytes, new: bytes, path: str) -> list[str]:
    a, b = split_lines(old), split_lines(new)
    problems: list[str] = []
    matcher = difflib.SequenceMatcher(None, [t for t, _ in a], [t for t, _ in b], autojunk=False)
    last = len(b) - 1
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                if a[i][1] != b[j][1] and not (j == last and b[j][1] == b""):
                    moved = f"{_name(a[i][1])} -> {_name(b[j][1])}"
                    problems.append(f"{path}:{j + 1}: unchanged line's ending moved {moved}")
        elif tag in ("replace", "insert"):
            for j in range(j1, j2):
                ending = b[j][1]
                if j == last and ending == b"":
                    continue
                if j > 0:
                    want, where = b[j - 1][1], "before"
                elif len(b) > 1:
                    want, where = b[1][1], "after"
                else:
                    continue
                if ending != want:
                    problems.append(
                        f"{path}:{j + 1}: new or changed line ends {_name(ending)}, "
                        f"the line {where} it ends {_name(want)}"
                    )
    return problems


def check(
    root: pathlib.Path, copies: pathlib.Path, scope: dict[str, str]
) -> tuple[list[str], list[str]]:
    problems: list[str] = []
    notes: list[str] = []
    for path, expected in scope.items():
        base = copies / path
        now = root / path
        old = base.read_bytes() if base.is_file() else None
        if expected == "NEW":
            if old is not None:
                problems.append(f"{path}: the plan names it new, but row 0 copied it")
                continue
            if not now.is_file():
                notes.append(f"{path}: new, not written yet")
                continue
            raw = now.read_bytes()
            cr = raw.count(CR)
            if cr:
                problems.append(f"{path}: a new file holds {cr} CR byte(s)")
            notes.append(f"{path}: new, {kind_of(raw)}, CR {cr}")
            continue
        if old is None:
            problems.append(f"{path}: no row-0 copy under {copies.as_posix()}")
            continue
        base_kind = kind_of(old)
        if base_kind != expected:
            problems.append(f"{path}: row-0 kind {base_kind}, the plan names {expected}")
            continue
        if not now.is_file():
            problems.append(f"{path}: missing now")
            continue
        raw = now.read_bytes()
        crlf = raw.count(CRLF)
        bare = raw.count(LF) - crlf
        lone_cr = raw.count(CR) - crlf
        if expected == "CRLF" and (bare or lone_cr):
            problems.append(f"{path}: CRLF file holds {bare} bare LF and {lone_cr} lone CR")
        elif expected == "LF" and raw.count(CR):
            problems.append(f"{path}: LF file holds {raw.count(CR)} CR byte(s)")
        elif expected == "MIXED":
            if lone_cr:
                problems.append(f"{path}: MIXED file holds {lone_cr} lone CR")
            problems += mixed_problems(old, raw, path)
        changed = "changed" if raw != old else "unchanged"
        notes.append(f"{path}: {expected}, crlf {crlf}, bare_lf {bare}, {changed} since row 0")
    return problems, notes


#: name, kind, row-0 bytes (None: new), bytes now (None: absent), whether it should pass.
CASES: tuple[tuple[str, str, bytes | None, bytes | None, bool], ...] = (
    ("crlf-kept", "CRLF", b"a\r\nb\r\n", b"a\r\nx\r\nb\r\n", True),
    ("crlf-bare-lf", "CRLF", b"a\r\nb\r\n", b"a\r\nx\nb\r\n", False),
    ("crlf-missing", "CRLF", b"a\r\n", None, False),
    ("lf-kept", "LF", b"a\nb\n", b"a\nx\nb\n", True),
    ("lf-cr", "LF", b"a\nb\n", b"a\r\nb\n", False),
    ("new-lf", "NEW", None, b"a\nb\n", True),
    ("new-cr", "NEW", None, b"a\r\nb\n", False),
    ("new-absent", "NEW", None, None, True),
    ("new-but-copied", "NEW", b"a\n", b"a\n", False),
    ("kind-drift", "CRLF", b"a\nb\n", b"a\nb\n", False),
    ("mixed-insert-after-crlf", "MIXED", b"a\r\nb\nc\n", b"a\r\nx\r\nb\nc\n", True),
    ("mixed-insert-after-lf", "MIXED", b"a\r\nb\nc\n", b"a\r\nb\nx\nc\n", True),
    ("mixed-insert-wrong", "MIXED", b"a\r\nb\nc\n", b"a\r\nb\nx\r\nc\n", False),
    ("mixed-change-follows-before", "MIXED", b"a\r\nb\nc\n", b"a\r\nB\r\nc\n", True),
    ("mixed-change-wrong", "MIXED", b"a\r\nb\nc\n", b"a\r\nb\nC\r\n", False),
    ("mixed-top-follows-next", "MIXED", b"a\r\nb\n", b"x\r\na\r\nb\n", True),
    ("mixed-top-wrong", "MIXED", b"a\r\nb\n", b"x\na\r\nb\n", False),
    ("mixed-unchanged-moved", "MIXED", b"a\r\nb\nc\n", b"a\nb\nc\n", False),
    ("mixed-lone-cr", "MIXED", b"a\r\nb\n", b"a\r\nb\rc\n", False),
)


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp) / "work"
        copies = pathlib.Path(tmp) / "copies"
        for name, kind, old, new, want in CASES:
            path = f"{name}.txt"
            if old is not None:
                (copies / path).parent.mkdir(parents=True, exist_ok=True)
                (copies / path).write_bytes(old)
            if new is not None:
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_bytes(new)
            problems, _ = check(root, copies, {path: kind})
            passed = not problems
            got, expected = ("pass" if passed else "refused"), ("pass" if want else "refused")
            reason = " -- " + problems[0] if problems else ""
            print(f"{name}: {got} (expected {expected}){reason}")
            if passed != want:
                failures.append(name)
    print(f"eol-check selftest: {len(CASES)} case(s), {len(failures)} wrong: {failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print("usage: eol-check.py [--selftest]")
        return 2
    problems, notes = check(pathlib.Path.cwd(), COPIES, SCOPE)
    for n in notes:
        print("eol", n)
    for p in problems:
        print("EOL-CHECK:", p)
    print(f"eol-check: {len(SCOPE)} scope path(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
