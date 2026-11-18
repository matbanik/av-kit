"""Session 93 diff check (AC-160.2, AC-160.3, AC-160.7; D-1166, D-1167): the product and test
change is exactly the plan's.

    uv run --no-sync python <plan>/diff-check.py
    uv run --no-sync python <plan>/diff-check.py --selftest

Each file is compared with its row-0 bytes, which row 0 copied to
`C:/Temp/av-kit/video-tail-frame/baseline-copies/<path>`:

- `packages/infrastructure/src/avkit_infra/media/adapter.py` (CRLF): no bare LF; every line
  outside `FFmpegAdapter._last_video_ms` (its AST span, decorators included) is byte-identical;
  inside it, with the docstring's lines left out of both, the code equals the row-0 code with
  only the one line OLD_ADAPTER replaced by NEW_ADAPTER (D-1166). The docstring may change.
- `tests/unit/test_media_adapter_frames.py` (LF): no CR; the row-0 file with the two named
  replacements UNIT_REPLACEMENTS (D-1167), each found exactly once, is a subsequence of the
  file now, so every other change is an inserted line.
- `tests/integration/test_video_real_ffmpeg.py` (LF): no CR; insertions only.
- Every path changed under `packages/` or `tests/` since `baseline.sha` (tracked diff and
  untracked files) is one of these three or was already dirty at row 0 (`baseline-dirty.txt`).

Exit 0 when every check holds, 1 when one fails, 2 when an input is missing. `--selftest`
runs each rule on fixtures in a scratch folder, and checks that each named old line occurs
exactly once in the row-0 copy (or, before row 0, in the repository file).
"""

from __future__ import annotations

import ast
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path("P:/av-kit")
PLAN = pathlib.Path(__file__).resolve().parent
COPIES = pathlib.Path("C:/Temp/av-kit/video-tail-frame/baseline-copies")
ADAPTER = "packages/infrastructure/src/avkit_infra/media/adapter.py"
UNIT = "tests/unit/test_media_adapter_frames.py"
INTEGRATION = "tests/integration/test_video_real_ffmpeg.py"
FUNCTION = "_last_video_ms"
OLD_ADAPTER = b'            f"{_seek_text(start)}%",'
NEW_ADAPTER = b'            f"{_seek_text(start)}%+{_seek_text(time_ms + END_GAP_LOOKBACK_MS)}",'
UNIT_REPLACEMENTS = (
    (b'        "0.000%",', b'        "0.000%+62.999",'),
    (
        b'    assert packet[packet.index("-read_intervals") + 1] == "7140.021%"',
        b'    assert packet[packet.index("-read_intervals") + 1] == "7140.021%+7260.021"',
    ),
)


def lines_of(raw: bytes) -> list[bytes]:
    """Lines without their endings (CRLF or LF)."""
    return [line.rstrip(b"\r") for line in raw.split(b"\n")]


def function_span(raw: bytes, name: str) -> tuple[int, int, int, int]:
    """(start, end, doc start, doc end) 0-based line indexes, end exclusive, of method NAME."""
    tree = ast.parse(raw.decode("utf-8"))
    found = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == name
    ]
    if len(found) != 1:
        raise ValueError(f"{len(found)} definitions of {name}")
    node = found[0]
    start = min([node.lineno, *(d.lineno for d in node.decorator_list)]) - 1
    first = node.body[0]
    if not (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    ):
        raise ValueError(f"{name} has no docstring")
    return start, node.end_lineno or node.lineno, first.lineno - 1, first.end_lineno or first.lineno


def check_adapter(base: bytes, now: bytes) -> list[str]:
    problems: list[str] = []
    if now.count(b"\n") != now.count(b"\r\n"):
        problems.append(f"{ADAPTER}: a bare LF in a CRLF file")
    try:
        b0, b1, bd0, bd1 = function_span(base, FUNCTION)
        n0, n1, nd0, nd1 = function_span(now, FUNCTION)
    except (ValueError, SyntaxError) as exc:
        return [*problems, f"{ADAPTER}: {exc}"]
    bl, nl = lines_of(base), lines_of(now)
    if bl[:b0] != nl[:n0]:
        problems.append(f"{ADAPTER}: a change before {FUNCTION}")
    if bl[b1:] != nl[n1:]:
        problems.append(f"{ADAPTER}: a change after {FUNCTION}")
    base_code = bl[b0:bd0] + bl[bd1:b1]
    now_code = nl[n0:nd0] + nl[nd1:n1]
    if base_code.count(OLD_ADAPTER) != 1:
        return [*problems, f"{ADAPTER}: the named old line is not once in the row-0 {FUNCTION}"]
    wanted = [NEW_ADAPTER if line == OLD_ADAPTER else line for line in base_code]
    if now_code != wanted:
        problems.append(
            f"{ADAPTER}: {FUNCTION} code is not the row-0 code with only the named line replaced"
        )
    return problems


def is_subsequence(small: list[bytes], big: list[bytes]) -> bool:
    it = iter(big)
    return all(any(line == other for other in it) for line in small)


def check_insertions(
    path: str, base: bytes, now: bytes, replacements: tuple[tuple[bytes, bytes], ...]
) -> list[str]:
    problems: list[str] = []
    if b"\r" in now:
        problems.append(f"{path}: a CR in an LF file")
    lines = lines_of(base)
    for old, new in replacements:
        if lines.count(old) != 1:
            problems.append(f"{path}: the named old line {old!r} is not once at row 0")
            continue
        lines[lines.index(old)] = new
    if not is_subsequence(lines, lines_of(now)):
        problems.append(f"{path}: a change other than the named replacements and insertions")
    return problems


def changed_paths(repo: pathlib.Path, base_sha: str) -> list[str]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, check=True
        ).stdout.decode("utf-8")

    tracked = git("diff", "--name-only", base_sha, "--", "packages", "tests").splitlines()
    untracked = git(
        "ls-files", "--others", "--exclude-standard", "--", "packages", "tests"
    ).splitlines()
    return sorted({p for p in (*tracked, *untracked) if p})


def check_scope(changed: list[str], dirty_at_row0: set[str]) -> list[str]:
    allowed = {ADAPTER, UNIT, INTEGRATION} | dirty_at_row0
    return [f"out of scope: {p}" for p in changed if p not in allowed]


def dirty_paths(porcelain: str) -> set[str]:
    return {line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()}


def run_checks(repo: pathlib.Path, copies: pathlib.Path, plan: pathlib.Path) -> int:
    needed = [copies / ADAPTER, copies / UNIT, copies / INTEGRATION, plan / "baseline.sha"]
    needed.append(plan / "baseline-dirty.txt")
    missing = [p.name for p in needed if not p.is_file()]
    if missing:
        print(f"INPUT missing: {missing}")
        return 2
    problems = check_adapter((copies / ADAPTER).read_bytes(), (repo / ADAPTER).read_bytes())
    problems += check_insertions(
        UNIT, (copies / UNIT).read_bytes(), (repo / UNIT).read_bytes(), UNIT_REPLACEMENTS
    )
    problems += check_insertions(
        INTEGRATION, (copies / INTEGRATION).read_bytes(), (repo / INTEGRATION).read_bytes(), ()
    )
    base_sha = (plan / "baseline.sha").read_bytes().decode("ascii").strip()
    dirty = dirty_paths((plan / "baseline-dirty.txt").read_bytes().decode("utf-8"))
    changed = changed_paths(repo, base_sha)
    print(f"changed under packages/ and tests/ since row 0: {changed}")
    problems += check_scope(changed, dirty)
    for problem in problems:
        print(f"PROBLEM: {problem}")
    print(f"diff-check: {len(problems)} problem(s)")
    return 1 if problems else 0


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    base_text = (
        "import x\n\n\nclass A:\n    def _last_video_ms(self, ffmpeg, path, time_ms, deadline):\n"
        '        """END_GAP: read from 60 s before.\n\n        More.\n        """\n'
        "        start = max(0, time_ms - END_GAP_LOOKBACK_MS)\n        command = [\n"
        + OLD_ADAPTER.decode()
        + "\n        ]\n        return command\n\n    def other(self):\n        return 1\n"
    )
    base = base_text.replace("\n", "\r\n").encode()
    good = base.replace(OLD_ADAPTER, NEW_ADAPTER)
    check("adapter: the named line only passes", check_adapter(base, good) == [])
    doc = good.replace(b"read from 60 s before.", b"read from 60 s before to 60 s after.")
    doc = doc.replace(b"        More.\r\n", b"        More.\r\n        Bounded.\r\n")
    check("adapter: a docstring change passes", check_adapter(base, doc) == [])
    check("adapter: no change fails", check_adapter(base, base) != [])
    other = good.replace(b"time_ms - END_GAP", b"time_ms - 2 * END_GAP")
    check("adapter: another line in the function fails", check_adapter(base, other) != [])
    after = good.replace(b"return 1", b"return 2")
    check("adapter: a change after the function fails", check_adapter(base, after) != [])
    before = good.replace(b"import x", b"import y")
    check("adapter: a change before the function fails", check_adapter(base, before) != [])
    bare = good.replace(b"return 1\r\n", b"return 1\n")
    check("adapter: a bare LF fails", any("bare LF" in p for p in check_adapter(base, bare)))
    added = good.replace(b"        return command", b"        x = 1\r\n        return command")
    check("adapter: an added line in the function fails", check_adapter(base, added) != [])

    unit_base = b"\n".join(
        [b"def t():", UNIT_REPLACEMENTS[0][0], b"    x = 1", UNIT_REPLACEMENTS[1][0], b""]
    )
    unit_good = b"\n".join(
        [
            b"def t():",
            UNIT_REPLACEMENTS[0][1],
            b"    x = 1",
            UNIT_REPLACEMENTS[1][1],
            b"",
            b"def new():",
            b"    pass",
            b"",
        ]
    )
    check(
        "unit: the two replacements and insertions pass",
        check_insertions(UNIT, unit_base, unit_good, UNIT_REPLACEMENTS) == [],
    )
    unit_bad = unit_good.replace(b"    x = 1", b"    x = 2")
    check(
        "unit: another changed line fails",
        check_insertions(UNIT, unit_base, unit_bad, UNIT_REPLACEMENTS) != [],
    )
    unit_half = unit_good.replace(UNIT_REPLACEMENTS[1][1], UNIT_REPLACEMENTS[1][0])
    check(
        "unit: a named line left unchanged fails",
        check_insertions(UNIT, unit_base, unit_half, UNIT_REPLACEMENTS) != [],
    )
    twice = unit_base + UNIT_REPLACEMENTS[0][0] + b"\n"
    check(
        "unit: a named old line twice fails",
        check_insertions(UNIT, twice, unit_good, UNIT_REPLACEMENTS) != [],
    )
    check(
        "unit: a CR fails",
        check_insertions(UNIT, unit_base, unit_good.replace(b"\n", b"\r\n"), UNIT_REPLACEMENTS)
        != [],
    )
    integ = b"a\nb\nc\n"
    check(
        "integration: insertions pass",
        check_insertions(INTEGRATION, integ, b"a\nnew\nb\nc\nd\n", ()) == [],
    )
    check(
        "integration: a deletion fails", check_insertions(INTEGRATION, integ, b"a\nc\n", ()) != []
    )
    check("scope: the three files pass", check_scope([ADAPTER, UNIT, INTEGRATION], set()) == [])
    check("scope: another file fails", check_scope(["packages/core/x.py"], set()) != [])
    check("scope: a row-0 dirty file passes", check_scope(["tests/x.py"], {"tests/x.py"}) == [])
    check(
        "porcelain paths",
        dirty_paths(" M tests/a.py\n?? tests/b.py\n") == {"tests/a.py", "tests/b.py"},
    )

    with tempfile.TemporaryDirectory() as scratch:
        folder = pathlib.Path(scratch)
        (folder / "baseline.sha").write_bytes(b"0\n")
        check("missing copies is exit 2", run_checks(folder, folder / "none", folder) == 2)

    for path, olds in (
        (ADAPTER, (OLD_ADAPTER,)),
        (UNIT, tuple(old for old, _ in UNIT_REPLACEMENTS)),
    ):
        source = COPIES / path if (COPIES / path).is_file() else REPO / path
        lines = lines_of(source.read_bytes())
        where = "row-0 copy" if source.is_relative_to(COPIES) else "repository file"
        for old in olds:
            check(f"{path}: named old line once in the {where}", lines.count(old) == 1)
    adapter_source = COPIES / ADAPTER if (COPIES / ADAPTER).is_file() else REPO / ADAPTER
    b0, b1, _, _ = function_span(adapter_source.read_bytes(), FUNCTION)
    inside = lines_of(adapter_source.read_bytes())[b0:b1]
    check("the named adapter line sits inside _last_video_ms", inside.count(OLD_ADAPTER) == 1)
    check("the new adapter line fits in 100 columns", len(NEW_ADAPTER) <= 100)
    print(f"diff-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print(__doc__)
        return 2
    return run_checks(REPO, COPIES, PLAN)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
