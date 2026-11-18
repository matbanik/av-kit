"""Session 90 wait check (AC-3; implementation-plan.md WORKER_WAIT, WAITS_NAMED, WAIT_SIGNALS_KEPT).

    uv run --no-sync python <plan>/wait-check.py            # check both test files
    uv run --no-sync python <plan>/wait-check.py --selftest # each rule, on synthetic text

For each of the two test files, the file now is compared with its row-0 bytes, which row 0
copied to C:/Temp/av-kit/test-run-reliability/baseline-copies/<path>. It passes when:

1. no 5-second worker wait is left (TIMEOUT_RE has no hit);
2. `WORKER_WAIT_S = 60.0` is defined exactly once, and the name is used USES times besides;
3. the line diff against row 0 (difflib opcodes over the lines with their endings) holds only:
   - one insert: CONSTANT_BLOCK, right after the file's ANCHOR line;
   - replaced lines, one for one, each equal to its row-0 line with the 5-second literal
     swapped for WORKER_WAIT_S (`swap`), USES of them;
   and nothing deleted or changed otherwise;
4. the assertion lines among the replaced ones are exactly NAMED (row-0 line numbers);
5. every line still ends in CRLF.

It prints, per file: the hits, the definition and use counts, the inserted and replaced row-0
line numbers, the assertion lines changed and the CRLF result; then `wait-check: PASS` or
`wait-check: FAIL: <reasons>`. Exit 0 or 1.
"""

from __future__ import annotations

import difflib
import pathlib
import re
import sys

REPO = pathlib.Path("P:/av-kit")
COPIES = pathlib.Path("C:/Temp/av-kit/test-run-reliability/baseline-copies")

TIMEOUT_RE = re.compile(
    r"(wait\(\s*(timeout=)?5(\.0)?\s*\)|join\(timeout=5\)|timeout: float = 5\.0|wait_idle\(5\.0\))"
)
SWAP_RE = re.compile(r"(timeout=|wait\(|wait_idle\(|float = )5(?:\.0)?(?=\s*\))|(float = )5\.0\b")
DEFINITION_RE = re.compile(r"^WORKER_WAIT_S = 60\.0\r\n$")
NAME_RE = re.compile(r"\bWORKER_WAIT_S\b")

CONSTANT_BLOCK = (
    "# Upper bound for a fake worker's signal. Each wait returns as soon as its signal"
    " arrives,\r\n",
    "# so the bound only matters on a loaded host"
    " (PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD, Session 90).\r\n",
    "WORKER_WAIT_S = 60.0\r\n",
)

#: path -> (anchor line text, uses besides the definition, row-0 assertion line numbers changed)
FILES = {
    "tests/integration/test_tts_assets.py": (
        'VOCAB = {"vocab": {"a": 1, "b": 2}, "n_token": 3}',
        11,
        (955, 963, 977, 984),
    ),
    "tests/integration/test_youtube_adapter.py": ("PROGRESS_MIN_INTERVAL_S = 0.25", 1, ()),
}


def swap(line: str) -> str:
    """The row-0 line with its 5-second literal swapped for WORKER_WAIT_S."""

    def repl(match: re.Match[str]) -> str:
        return (match.group(1) or match.group(2)) + "WORKER_WAIT_S"

    return SWAP_RE.sub(repl, line, count=1)


def check_text(
    base: str, now: str, anchor: str, uses: int, named: tuple[int, ...]
) -> tuple[list[str], dict[str, object]]:
    """(problems, facts) for one file's row-0 text and current text, both with CRLF endings."""
    problems: list[str] = []
    old = base.splitlines(keepends=True)
    new = now.splitlines(keepends=True)
    hits = [i for i, ln in enumerate(new, 1) if TIMEOUT_RE.search(ln)]
    if hits:
        problems.append(f"5-second waits left at {hits}")
    definitions = [i for i, ln in enumerate(new, 1) if DEFINITION_RE.match(ln)]
    total = sum(len(NAME_RE.findall(ln)) for ln in new)
    if len(definitions) != 1:
        problems.append(f"{len(definitions)} definitions of WORKER_WAIT_S, expected 1")
    if total - len(definitions) != uses:
        problems.append(f"{total - len(definitions)} uses of WORKER_WAIT_S, expected {uses}")
    inserted: list[int] = []
    replaced: list[int] = []
    asserts: list[int] = []
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            block = tuple(new[j1:j2])
            if block != CONSTANT_BLOCK or i1 == 0 or old[i1 - 1].rstrip("\r\n") != anchor:
                problems.append(f"unexpected insert before row-0 line {i1 + 1}")
            else:
                inserted.append(i1 + 1)
            continue
        if tag == "replace" and i2 - i1 == j2 - j1:
            for k in range(i2 - i1):
                before, after = old[i1 + k], new[j1 + k]
                if TIMEOUT_RE.search(before) and after == swap(before) and after != before:
                    replaced.append(i1 + k + 1)
                    if before.lstrip().startswith("assert "):
                        asserts.append(i1 + k + 1)
                else:
                    problems.append(f"row-0 line {i1 + k + 1} changed beyond its wait")
            continue
        problems.append(f"{tag} at row-0 lines {i1 + 1}-{i2}")
    if len(inserted) != 1:
        problems.append(f"{len(inserted)} constant blocks inserted, expected 1")
    if len(replaced) != uses:
        problems.append(f"{len(replaced)} wait lines replaced, expected {uses}")
    if tuple(asserts) != named:
        problems.append(f"assertion lines changed {asserts}, expected {list(named)}")
    raw_lf = now.count("\n")
    crlf_ok = raw_lf == now.count("\r\n") and "\r\r" not in now
    if not crlf_ok:
        problems.append("a line does not end in CRLF")
    facts: dict[str, object] = {
        "hits": hits,
        "definitions": definitions,
        "uses": total - len(definitions),
        "inserted_after_row0_line": [i - 1 for i in inserted],
        "replaced_row0_lines": replaced,
        "assert_lines_changed": asserts,
        "crlf": crlf_ok,
    }
    return problems, facts


def read(path: pathlib.Path) -> str:
    return path.read_bytes().decode("utf-8")


def run() -> int:
    problems: list[str] = []
    for rel, (anchor, uses, named) in FILES.items():
        copy = COPIES / rel
        if not copy.is_file():
            problems.append(f"{rel}: no row-0 copy")
            continue
        found, facts = check_text(read(copy), read(REPO / rel), anchor, uses, named)
        print(f"{rel}: {facts}")
        problems.extend(f"{rel}: {p}" for p in found)
    if problems:
        print("wait-check: FAIL: " + "; ".join(problems))
        return 1
    print("wait-check: PASS")
    return 0


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    anchor = "ANCHOR = 1"
    base = "".join(
        ln + "\r\n"
        for ln in (
            "import x",
            anchor,
            "",
            "def f(timeout: float = 5.0):",
            "    ev.wait(timeout=5)",
            "    assert ev.wait(5.0)",
            "    t.join(timeout=5)",
            "    s.wait_idle(5.0)",
            "    assert s.wait_idle(5.0) is True",
            "    other(5.0)",
        )
    )
    block = "".join(CONSTANT_BLOCK)
    good = base.replace(anchor + "\r\n", anchor + "\r\n" + block)
    for old in (
        "timeout: float = 5.0",
        "wait(timeout=5)",
        "ev.wait(5.0)",
        "join(timeout=5)",
        "s.wait_idle(5.0)\r\n",
        "s.wait_idle(5.0) is",
    ):
        good = good.replace(old, swap(old), 1)
    check(
        "swap keeps the rest of the line",
        swap("    ev.wait(5.0)\r\n") == "    ev.wait(WORKER_WAIT_S)\r\n",
    )
    check(
        "swap of a default",
        swap("def f(timeout: float = 5.0):") == "def f(timeout: float = WORKER_WAIT_S):",
    )
    check("swap of join", swap("t.join(timeout=5)") == "t.join(timeout=WORKER_WAIT_S)")
    check("other literals stay", swap("    other(5.0)\r\n") == "    other(5.0)\r\n")
    problems, facts = check_text(base, good, anchor, 6, (6, 9))
    check("the planned edit passes", problems == [])
    check("asserts are reported", facts["assert_lines_changed"] == [6, 9])
    check(
        "a left wait fails",
        bool(
            check_text(
                base,
                good.replace("t.join(timeout=WORKER_WAIT_S)", "t.join(timeout=5)"),
                anchor,
                6,
                (6, 9),
            )[0]
        ),
    )
    check(
        "an assertion edit fails",
        bool(check_text(base, good.replace("is True", "is False"), anchor, 6, (6, 9))[0]),
    )
    check(
        "a deleted line fails",
        bool(check_text(base, good.replace("import x\r\n", ""), anchor, 6, (6, 9))[0]),
    )
    check(
        "a moved block fails",
        bool(
            check_text(
                base,
                good.replace(block, "").replace("import x\r\n", "import x\r\n" + block),
                anchor,
                6,
                (6, 9),
            )[0]
        ),
    )
    check(
        "a bare LF fails",
        bool(check_text(base, good.replace("import x\r\n", "import x\n"), anchor, 6, (6, 9))[0]),
    )
    check("an unnamed assert fails", bool(check_text(base, good, anchor, 6, (6,))[0]))
    check(
        "a second definition fails",
        bool(check_text(base, good + "WORKER_WAIT_S = 60.0\r\n", anchor, 6, (6, 9))[0]),
    )
    print(f"wait-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["--selftest"] else run())
