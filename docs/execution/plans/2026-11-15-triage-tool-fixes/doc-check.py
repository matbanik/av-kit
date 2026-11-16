"""Session 79 doc check (task row 9, AC-12; plan §The docs, D-950).

The five docs that describe `issue_triage.py verify --deep` are edited by a fixed table of line
replacements. This script holds that table. `--check` (the default) applies it to the row-0 copies
in C:/Temp/av-kit/triage-tool-fixes/base/ and requires the result to equal the live file byte for
byte, with the copy's line endings kept. It also requires that no live doc still claims the
removed checks. Each old block must occur exactly once in its copy; otherwise the doc changed
before row 0 in a way this table does not expect (S2), and the script exits 2.

`--selftest` runs the same logic on synthetic files in a temporary folder.

Exit codes: 0 pass; 1 a live file differs from copy-plus-table, or a claim remains; 2 a table
anchor is missing or repeated in a copy, or a copy is missing.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

BASE = Path("C:/Temp/av-kit/triage-tool-fixes/base")

_BOX_OLD = "\u2502      File checks, test coverage, fix indicators, staleness      \u2502"
_BOX_NEW = "\u2502" + "      Path-shaped file checks; read-only".ljust(len(_BOX_OLD) - 2) + "\u2502"

# (path, old consecutive lines, new lines). Lines carry no line ending.
TABLE: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    (
        ".agent/workflows/issue-triage.md",
        ("> This runs file-existence checks, test-coverage scans, and updates `verification.last_checked`.",),
        (
            "> It checks that each path-shaped `resolution_path` still exists, and it only reads the register."
            " When the triaging agent really re-checks an issue, it sets `verification.last_checked`, `method`,"
            " `result` and `evidence_file` together by hand in the YAML, then runs `render`.",
        ),
    ),
    (
        ".agent/workflows/issue-triage.md",
        (
            "- **`file_missing`**: Resolution path no longer exists \u2014 issue may be stale or file was renamed",
            "- **`no_test_coverage`**: No test references the issue ID \u2014 may need regression test",
            "- **`fix_indicator_found`**: Code matching the fix pattern was found \u2014 issue may be resolved",
        ),
        ("- **`file_missing`**: Resolution path no longer exists \u2014 issue may be stale or file was renamed",),
    ),
    (
        ".agent/workflows/issue-triage.md",
        ("- `archived`: resolved issues",),
        ("- `archived`: resolved and dismissed issues",),
    ),
    (
        ".agent/skills/issue-triage/SKILL.md",
        (
            "uv run python tools/issue_triage.py verify --deep                  "
            "# Deep verify: file checks, test coverage, updates last_checked",
        ),
        (
            "uv run python tools/issue_triage.py verify --deep                  "
            "# Deep verify: path-shaped file checks; read-only",
        ),
    ),
    (
        ".agent/docs/issue-lifecycle-guide.md",
        (
            "- \u2705 Checks if referenced files still exist",
            "- \u2705 Scans for test coverage (does any test reference this issue ID?)",
            "- \u2705 Searches for fix indicators (has the code been patched?)",
            "- \u2705 Flags stale issues (not verified in 30+ days)",
            "- \u2705 Updates `verification.last_checked` timestamps",
        ),
        (
            "- \u2705 Checks that each path-shaped `resolution_path` still exists",
            "- \u2705 Reads the register only; it never writes `verification.last_checked`",
        ),
    ),
    (
        ".agent/docs/issue-lifecycle-guide.md",
        ("uv run python tools/issue_triage.py verify --deep    # Also check file existence, test coverage",),
        ("uv run python tools/issue_triage.py verify --deep    # Also check that path-shaped references exist",),
    ),
    (
        ".agent/docs/issue-lifecycle-guide.md",
        (_BOX_OLD,),
        (_BOX_NEW,),
    ),
    (
        ".agent/docs/issue-lifecycle-guide.md",
        ('| *"Check if issues are stale"* | Runs `issue_triage.py verify --deep` |',),
        ('| *"Check if issues are stale"* | Runs `issue_triage.py verify` |',),
    ),
    (
        ".agent/docs/commands.md",
        (
            "uv run python tools/issue_triage.py verify --deep                    "
            "# Deep verify: file checks, test coverage",
        ),
        (
            "uv run python tools/issue_triage.py verify --deep                    "
            "# Deep verify: path-shaped file checks; read-only",
        ),
    ),
    (
        ".agent/docs/cloud-local-collaboration.md",
        ("split. `issue_triage.py verify --deep` (file existence, test references) runs in",),
        ("split. `issue_triage.py verify --deep` (path-shaped file checks) runs in",),
    ),
)

DOCS = tuple(dict.fromkeys(path for path, _, _ in TABLE))

# D-947: the workflow note names the four verification fields together (cloud-local-collaboration.md:316)
# and says the triaging agent sets them by hand.
TRIAGE_NOTE_TERMS = ("`verification.last_checked`", "`method`", "`result`", "`evidence_file`", "by hand")

# Claims the edited docs must no longer make about verify --deep.
GONE = (
    "no_test_coverage",
    "fix_indicator",
    "fix indicators",
    "test coverage",
    "test-coverage",
    "test references",
    "Updates `verification.last_checked`",
    "updates `verification.last_checked`",
    "updates last_checked",
)


class AnchorError(Exception):
    pass


def _eol(data: bytes) -> bytes:
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n")
    if crlf and crlf == lf:
        return b"\r\n"
    if crlf == 0:
        return b"\n"
    raise AnchorError(f"mixed line endings ({crlf} CRLF of {lf} LF)")


def apply(path: str, data: bytes, table=TABLE) -> bytes:
    eol = _eol(data)
    lines = data.decode("utf-8").split(eol.decode())
    for rel, old, new in table:
        if rel != path:
            continue
        hits = [i for i in range(len(lines) - len(old) + 1) if tuple(lines[i : i + len(old)]) == old]
        if len(hits) != 1:
            raise AnchorError(f"{path}: block starting {old[0][:60]!r} found {len(hits)} times, expected 1")
        i = hits[0]
        lines[i : i + len(old)] = list(new)
    return eol.decode().join(lines).encode("utf-8")


def check(base: Path, live_root: Path, table=TABLE, docs=DOCS, gone=GONE) -> int:
    worst = 0
    for rel in docs:
        src = base / rel
        if not src.is_file():
            print(f"MISSING base copy: {src}")
            worst = max(worst, 2)
            continue
        try:
            want = apply(rel, src.read_bytes(), table)
        except AnchorError as exc:
            print(f"ANCHOR {exc}")
            worst = max(worst, 2)
            continue
        live = (live_root / rel).read_bytes()
        eol = "CRLF" if b"\r\n" in want else "LF"
        if live != want:
            print(f"DIFF {rel}: live {len(live)} bytes, base+table {len(want)} bytes ({eol})")
            worst = max(worst, 1)
        else:
            print(f"ok {rel}: {len(live)} bytes, {eol} kept")
        text = live.decode("utf-8", errors="replace")
        for claim in gone:
            if claim in text:
                print(f"CLAIM {rel}: still holds {claim!r}")
                worst = max(worst, 1)
    print(f"doc-check: exit {worst}")
    return worst


def selftest() -> int:
    table = (
        ("a.md", ("old one", "old two"), ("new",)),
        ("a.md", ("keep \u2502 box",), ("kept \u2502 box",)),
        ("b.md", ("x test coverage",), ("x path checks",)),
    )
    docs = ("a.md", "b.md")
    gone = ("test coverage",)
    a_base = "head\r\nold one\r\nold two\r\nkeep \u2502 box\r\ntail\r\n".encode()
    a_live = "head\r\nnew\r\nkept \u2502 box\r\ntail\r\n".encode()
    b_base = b"x test coverage\n"
    b_live = b"x path checks\n"
    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        def write(base_a, base_b, live_a, live_b):
            for sub, a, b in (("base", base_a, base_b), ("live", live_a, live_b)):
                (root / sub).mkdir(exist_ok=True)
                (root / sub / "a.md").write_bytes(a)
                (root / sub / "b.md").write_bytes(b)

        def run(name, expect, *files):
            write(*files)
            got = check(root / "base", root / "live", table, docs, gone)
            cases.append((name, got == expect, got, expect))

        run("pass", 0, a_base, b_base, a_live, b_live)
        run("live CRLF written as LF", 1, a_base, b_base, a_live.replace(b"\r\n", b"\n"), b_live)
        run("extra live edit", 1, a_base, b_base, a_live + b"more\r\n", b_live)
        run("claim left in live", 1, a_base, b_base, a_live, b_live + b"test coverage\n")
        run("anchor repeated in base", 2, a_base + b"old one\r\nold two\r\n", b_base, a_live, b_live)
        run("anchor missing in base", 2, a_base.replace(b"old two", b"old 2"), b_base, a_live, b_live)
        run("mixed endings in base", 2, a_base + b"lf only\n", b_base, a_live, b_live)
    box_ok = len(_BOX_NEW) == len(_BOX_OLD) and _BOX_NEW.endswith("\u2502")
    cases.append(("box width kept", box_ok, len(_BOX_NEW), len(_BOX_OLD)))
    note = TABLE[0][2][0]
    missing = [t for t in TRIAGE_NOTE_TERMS if t not in note]
    cases.append(("triage note names the four fields", not missing, missing, []))
    bad = [c for c in cases if not c[1]]
    for name, ok, got, expect in cases:
        print(f"selftest {name}: {'ok' if ok else 'FAIL'} (got {got}, expected {expect})")
    print(f"doc-check selftest: {len(cases) - len(bad)}/{len(cases)} ok")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="compare base copies plus the table with the live docs (default)")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--base", type=Path, default=BASE)
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    return check(args.base, Path.cwd())


if __name__ == "__main__":
    sys.exit(main())
