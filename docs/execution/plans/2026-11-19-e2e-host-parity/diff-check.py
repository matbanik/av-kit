"""Session 97 (task rows 4 to 7, the gate; PINS_NAMED, D-1252): every edited test line is named.

    uv run --no-sync python <plan>/diff-check.py [--expect-changed PATH ...]
    uv run --no-sync python <plan>/diff-check.py --selftest

It compares each tracked test file this plan edits with its row-0 copy under
``C:/Temp/av-kit/e2e-host-parity/baseline-copies/<path>`` (baseline.ps1 writes the copies).
A file byte-identical to its copy passes. A changed file must equal, line for line, the file its
rules build from the copy (implementation-plan.md §Test pins); nothing else may differ:

* a replacement: inside the copy block that starts with a named line, the old text sits on exactly
  one line, and that line becomes the line with the old text replaced by the new;
* a removal: one line by its start, or the lines from one start up to (not including) another;
* an insertion (round 1 F1): a named hunk of exact lines, placed right after (or before) the one
  copy line equal to its anchor inside its named block; an inserted line that no hunk names, a
  hunk at another place and a missing hunk each fail;
* a wildcard block: the copy block (named start, up to the first later line at the same indent that
  starts with ``}``) is replaced by one file block with another named start;
* a new block: a block with a named start, placed after a named copy block and one blank line.

A wildcard or new block's own lines are new test code, not pins: it is proved by its Red (it fails
by assertion before the fix) and by the test hash recorded at that Red, which holds to the gate.
New test files are checked the same way (their Red and hash); this tool only allows their paths.

The line-ending kind of every line must match the copy's kind. Last, ``git status --porcelain
--untracked-files=all -- ui/tests tests tools/e2e_host`` may name only the allowed paths (the
edited and the new files). ``--expect-changed`` names files that must differ from their copies.
It reads only these files, prints ASCII and exits 0 when every check holds, 1 when one fails,
2 on a usage error. ``--selftest`` runs synthetic cases and, on the real files (each row-0 copy,
or the clean tracked file before row 0), the intended edit, the round 1 early-return mutant and an
unnamed insertion in every file that takes insertions.
"""

from __future__ import annotations

import argparse
import difflib
import pathlib
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field

COPIES = pathlib.Path("C:/Temp/av-kit/e2e-host-parity/baseline-copies")
REPO = pathlib.Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Replace:
    block: str | None  # the start of the copy block's first line; None = whole file
    old: str
    new: str


@dataclass(frozen=True)
class Remove:
    start: str
    until: str | None = None  # None = the one line that starts with `start`


@dataclass(frozen=True)
class Insert:
    block: str | None  # the start of the copy block's first line; None = whole file
    anchor: str  # the whole text of exactly one copy line inside the block
    lines: tuple[str, ...]  # the exact inserted lines, in order
    before: bool = False  # True: right before the anchor; False: right after it


@dataclass(frozen=True)
class Wildcard:
    old_start: str
    new_start: str


@dataclass(frozen=True)
class NewBlock:
    after: str  # the start of the copy block it follows, after one blank line
    start: str  # the start of the new block's first line


@dataclass(frozen=True)
class Rules:
    replace: tuple[Replace, ...] = ()
    remove: tuple[Remove, ...] = ()
    insert: tuple[Insert, ...] = ()
    wildcard: tuple[Wildcard, ...] = ()
    new_block: tuple[NewBlock, ...] = ()


UNIT = "ui/tests/unit/"
E2E = "ui/tests/e2e/"
LAUNCH_OLD = "async function launchApp() {"
LAUNCH_NEW = "async function launchApp(args: readonly string[] = []) {"
LAUNCH_ARGS = Insert(LAUNCH_OLD, "  return launchElectron({", ("    args,",))
AC_101_6 = "test('AC-101.6 a double-click reopens"
AC_126_8 = "test('AC-126.8 light accent paints the ruled colours'"
FIDELITY_NOTE = (
    "// FIDELITY_FRAME (Session 97, D-1245): the fidelity specs measure at a device scale of 1 on"
    " every host, the second host's native scale; at 2 the dev PC halves a pixel gap and hid the"
    " 2 px plate drift."
)
HOVER_NOTE = (
    "// HOVER_CAPABLE (Session 97, D-1246): AC-126.8 checks a hover colour, and Tailwind v4 applies"
    " hover: only under (hover: hover); this states a mouse-capable device so a host with no"
    " pointing device (the second host) runs the same rule."
)
HOVER_ARGS = (
    "const HOVER_CAPABLE_ARGS = ['--blink-settings=primaryHoverType=2,availableHoverTypes=2,"
    "primaryPointerType=4,availablePointerTypes=4'] as const"
)
HOVER_PRECONDITION = (
    "  expect(await page.evaluate(() => matchMedia('(hover: hover)').matches),"
    " 'HOVER_CAPABLE: (hover: hover) matches before the hover').toBe(true)"
)
ARGS_NOTE = (
    "  /** CHROMIUM_ARGS (Session 97): extra Chromium switches after the main entry;"
    " FIDELITY_FRAME and HOVER_CAPABLE use it. */"
)
PLATES_START = "  it('AC-102.10 textBackgroundBox equals each painted text_plates box"
HARNESS_START = "describe('Session 97 host parity'"

RULES: dict[str, Rules] = {
    UNIT + "capture-text-metrics.test.ts": Rules(
        replace=(
            Replace(
                "  it('AC-59.19",
                "{ x: 10, y: 26, width: 15, height: 12 }",
                "{ x: 10, y: 26, width: 16, height: 13 }",
            ),
        ),
    ),
    UNIT + "capture-transform.test.ts": Rules(
        replace=(
            Replace(
                "  it('AC-101.1",
                "{ x: 10, y: 6, width: 15, height: 12 }",
                "{ x: 10, y: 6, width: 16, height: 13 }",
            ),
            Replace("  it('AC-101.1", "at(40, 30)", "at(42, 32)"),
            Replace(
                "  it('AC-101.1",
                "{ x: 10, y: 6, width: 30, height: 24 }",
                "{ x: 10, y: 6, width: 32, height: 24 }",
            ),
        ),
    ),
    UNIT + "capture-page.behavior.test.ts": Rules(
        replace=(
            Replace("  it('AC-82.4 a loaded plate", "      '15',", "      '16',"),
            Replace("  it('AC-82.4 a loaded plate", "      '12',", "      '13',"),
            Replace(
                "  it('AC-82.4 a loaded plate", "x 50..125, y 130..190", "x 50..130, y 130..195"
            ),
            Replace(
                "  describe('MEU-101 text re-edit and scale'",
                "{1,2,5,1}: CSS (25,50)-(150,75)",
                "{1,3,4,2}: CSS (25,75)-(125,125)",
            ),
            Replace(
                "    it('AC-101.2 a double-click",
                "doubleClickAt(surface, 87, 62)",
                "doubleClickAt(surface, 75, 100)",
            ),
            Replace(
                "    it('AC-101.4 a selected",
                "image (6,3), CSS (150,75); CSS (175,100) is image (7,4): ratio max(6/5, 2/1)",
                "image (5,5), CSS (125,125); CSS (150,175) is image (6,7): ratio max(5/4, 4/2)",
            ),
            Replace(
                "    it('AC-101.4 a selected",
                "drag(surface, 150, 75, 175, 100)",
                "drag(surface, 125, 125, 150, 175)",
            ),
            Replace("    it('AC-101.4 a selected", "(3.5,2), CSS (87.5,50)", "(3,3), CSS (75,75)"),
            Replace("    it('AC-101.4 a selected", "cssX: 87.5,", "cssX: 75,"),
            Replace("    it('AC-101.4 a selected", "cssY: 50,", "cssY: 75,"),
            Replace(
                "    it('AC-101.4 after a corner",
                "drag(surface, 150, 75, 175, 100)",
                "drag(surface, 125, 125, 150, 175)",
            ),
            Replace("  it('AC-59.19 SVG text", "toBe('15')", "toBe('16')"),
            Replace("  it('AC-59.19 SVG text", "toBe('12')", "toBe('13')"),
        ),
    ),
    UNIT + "capture-text-lines.behavior.test.ts": Rules(
        remove=(
            Remove("import { SEGOE_LA_BASE_SIZE, SEGOE_LA_GLYPHS }"),
            Remove("const MATRIX_TEXTS", "type Shot"),
        ),
        wildcard=(
            Wildcard("  it('AC-102.10 textBackgroundBox equals each text_plates box", PLATES_START),
        ),
    ),
    UNIT + "e2e-harness.test.ts": Rules(
        new_block=(NewBlock("describe('Session 78 E2E harness'", HARNESS_START),),
    ),
    E2E + "electron-app.ts": Rules(
        replace=(
            Replace(
                None,
                "export async function launchElectron({ main, env = {}, pointerShield }",
                "export async function launchElectron({ main, env = {}, pointerShield, args }",
            ),
            Replace(
                None,
                "args: ['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN],",
                "args: ['-r', MAIN_ERROR_WATCH, main ?? DEFAULT_MAIN, ...(args ?? [])],",
            ),
        ),
        insert=(
            Insert(
                "export interface LaunchOptions",
                "  pointerShield?: false",
                (ARGS_NOTE, "  args?: readonly string[]"),
            ),
        ),
    ),
    E2E + "capture-inbox.test.ts": Rules(
        replace=(
            Replace(None, LAUNCH_OLD, LAUNCH_NEW),
            Replace(
                "test('AC-82.6 TEXT_PIXEL_ORACLE",
                "const app = await launchApp()",
                "const app = await launchApp(FIDELITY_ARGS)",
            ),
            Replace(
                "async function fidelityViews(",
                "const app = await launchApp()",
                "const app = await launchApp(FIDELITY_ARGS)",
            ),
            Replace(
                AC_101_6, "clickSampleImagePoint(page, 3, 6)", "clickSampleImagePoint(page, 3, 4)"
            ),
            Replace(
                AC_101_6,
                "from (3,6) has the plate {3,7,4,1}; its centre is image (5,7.5).",
                "from (3,4) has the plate {3,6,6,2}; its centre is image (6,7).",
            ),
            Replace(
                AC_101_6, "sampleImagePagePoint(page, 5, 7.5)", "sampleImagePagePoint(page, 6, 7)"
            ),
            Replace(
                AC_101_6, "'Done', x: 3, y: 6, font_size: 2", "'Done', x: 3, y: 4, font_size: 2"
            ),
            Replace(AC_101_6, "`Done` has the plate {3,7,5,1}", "`Done` has the plate {3,6,5,2}"),
            Replace(AC_101_6, "the nw corner (3,7) out", "the nw corner (3,6) out"),
        ),
        insert=(
            Insert(
                None,
                "import { pointerOn, settle, settledBox, windowSettled } from './pointer-settle'",
                (
                    "",
                    FIDELITY_NOTE,
                    "const FIDELITY_ARGS = ['--force-device-scale-factor=1'] as const",
                ),
            ),
            LAUNCH_ARGS,
        ),
    ),
    E2E + "settings.test.ts": Rules(
        replace=(
            Replace(None, LAUNCH_OLD, LAUNCH_NEW),
            Replace(
                AC_126_8,
                "const app = await launchApp()",
                "const app = await launchApp(HOVER_CAPABLE_ARGS)",
            ),
        ),
        insert=(
            Insert(None, "} from './theme-probe'", ("", HOVER_NOTE, HOVER_ARGS)),
            LAUNCH_ARGS,
            Insert(AC_126_8, "  await lightBtn.hover()", (HOVER_PRECONDITION,), before=True),
        ),
    ),
}

NEW_FILES = (
    E2E + "fixtures/capture-text-plates.json",
    UNIT + "capture-text-plates.test.ts",
    "tests/unit/test_capture_text_plates.py",
)
OTHER_ALLOWED = ("tools/e2e_host/known-failures.json", "tests/tooling/test_e2e_remote.py")
ALLOWED = frozenset(RULES) | frozenset(NEW_FILES) | frozenset(OTHER_ALLOWED)
TOKEN = "\x00block "  # stands for one wildcard or new block; never a line of source


@dataclass
class Result:
    problems: list[str] = field(default_factory=list)
    inserted: list[tuple[int, str]] = field(default_factory=list)


def split(data: bytes) -> list[tuple[str, str]]:
    """Each line as (text, ending), ending one of CRLF, LF or '' for an unterminated last line."""
    out: list[tuple[str, str]] = []
    for raw in data.split(b"\n"):
        out.append((raw.decode("utf-8"), "LF"))
    last_text, _ = out.pop()
    if last_text:
        out.append((last_text, ""))
    fixed: list[tuple[str, str]] = []
    for text, ending in out:
        if ending == "LF" and text.endswith("\r"):
            fixed.append((text[:-1], "CRLF"))
        else:
            fixed.append((text, ending))
    return fixed


def block_range(lines: list[str], start: str) -> tuple[int, int] | None:
    """[first, last] of the one block whose first line starts with `start`; else None."""
    heads = [i for i, line in enumerate(lines) if line.startswith(start)]
    if len(heads) != 1:
        return None
    head = heads[0]
    indent = len(lines[head]) - len(lines[head].lstrip(" "))
    for j in range(head + 1, len(lines)):
        line = lines[j]
        if line.startswith(" " * indent + "}") and len(line) - len(line.lstrip(" ")) == indent:
            return head, j
    return None


def find_one(lines: list[str], span: tuple[int, int], text: str) -> int | None:
    hits = [i for i in range(span[0], span[1] + 1) if text in lines[i]]
    return hits[0] if len(hits) == 1 else None


def span_of(lines: list[str], block: str | None) -> tuple[int, int] | None:
    return (0, len(lines) - 1) if block is None else block_range(lines, block)


def expected(old: list[str], rules: Rules, problems: list[str]) -> list[tuple[str, str]]:
    """The file the rules build from the copy, as (tag, text); tag keep, pin, insert or block."""
    replaced: dict[int, str] = {}
    drop: set[int] = set()
    before: dict[int, list[tuple[str, str]]] = {}
    after: dict[int, list[tuple[str, str]]] = {}
    blocks_at: dict[int, str] = {}
    for rule in rules.replace:
        span = span_of(old, rule.block)
        i = None if span is None else find_one(old, span, rule.old)
        if i is None:
            problems.append(f"replace: {rule.old!r} not on one line of block {rule.block!r}")
            continue
        replaced[i] = replaced.get(i, old[i]).replace(rule.old, rule.new, 1)
    for rule in rules.remove:
        heads = [i for i, line in enumerate(old) if line.startswith(rule.start)]
        if len(heads) != 1:
            problems.append(f"remove: {rule.start!r} starts {len(heads)} lines of the copy")
            continue
        if rule.until is None:
            drop.add(heads[0])
            continue
        ends = [i for i, line in enumerate(old) if i > heads[0] and line.startswith(rule.until)]
        if not ends:
            problems.append(f"remove: no {rule.until!r} after {rule.start!r}")
            continue
        drop.update(range(heads[0], ends[0]))
    for rule in rules.wildcard:
        span = block_range(old, rule.old_start)
        if span is None:
            problems.append(f"wildcard: copy block {rule.old_start!r} not found once")
            continue
        drop.update(range(span[0], span[1] + 1))
        blocks_at[span[0]] = TOKEN + rule.new_start
    for rule in rules.new_block:
        span = block_range(old, rule.after)
        if span is None:
            problems.append(f"new block: copy block {rule.after!r} not found once")
            continue
        after.setdefault(span[1], []).extend([("insert", ""), ("block", TOKEN + rule.start)])
    for rule in rules.insert:
        span = span_of(old, rule.block)
        hits = (
            []
            if span is None
            else [i for i in range(span[0], span[1] + 1) if old[i] == rule.anchor]
        )
        if len(hits) != 1:
            problems.append(
                f"insert: anchor {rule.anchor!r} is {len(hits)} lines of {rule.block!r}"
            )
            continue
        if hits[0] in drop:
            problems.append(f"insert: anchor {rule.anchor!r} is a removed line")
            continue
        side = before if rule.before else after
        side.setdefault(hits[0], []).extend(("insert", line) for line in rule.lines)
    plan: list[tuple[str, str]] = []
    for i, text in enumerate(old):
        plan.extend(before.get(i, []))
        if i in blocks_at:
            plan.append(("block", blocks_at[i]))
        if i not in drop:
            plan.append(("pin" if i in replaced else "keep", replaced.get(i, text)))
        plan.extend(after.get(i, []))
    return plan


def collapse(new: list[str], rules: Rules, problems: list[str]) -> list[tuple[str, int]]:
    """The file's lines as (text, line number), each named wildcard or new block one token."""
    starts = [w.new_start for w in rules.wildcard] + [b.start for b in rules.new_block]
    spans: dict[int, tuple[int, str]] = {}
    for start in starts:
        span = block_range(new, start)
        if span is None:
            problems.append(f"block: {start!r} does not start exactly one block of the file")
            continue
        spans[span[0]] = (span[1], TOKEN + start)
    out: list[tuple[str, int]] = []
    i = 0
    while i < len(new):
        if i in spans:
            end, token = spans[i]
            out.append((token, i + 1))
            i = end + 1
            continue
        out.append((new[i], i + 1))
        i += 1
    return out


def check(old_data: bytes, new_data: bytes, rules: Rules) -> Result:
    res = Result()
    old_rows = split(old_data)
    new_rows = split(new_data)
    old = [t for t, _ in old_rows]
    new = [t for t, _ in new_rows]
    kinds_old = {e for _, e in old_rows if e}
    kinds_new = {e for _, e in new_rows if e}
    if kinds_old != kinds_new:
        res.problems.append(f"line endings changed: {sorted(kinds_old)} -> {sorted(kinds_new)}")
    for rule in rules.remove:
        if any(line.startswith(rule.start) for line in new):
            res.problems.append(f"remove: {rule.start!r} is still in the file")
    for rule in rules.wildcard:
        if any(line.startswith(rule.old_start) for line in new):
            res.problems.append(f"wildcard: the old start {rule.old_start!r} is still in the file")
    plan = expected(old, rules, res.problems)
    actual = collapse(new, rules, res.problems)
    if res.problems:
        return res
    want = [text for _, text in plan]
    got = [text for text, _ in actual]
    if want == got:
        for (tag, text), (_, line_no) in zip(plan, actual, strict=True):
            if tag in ("insert", "block"):
                res.inserted.append((line_no, text.replace(TOKEN, "[block] ")))
        return res
    matcher = difflib.SequenceMatcher(a=want, b=got, autojunk=False)
    for op, a0, a1, b0, b1 in matcher.get_opcodes():
        if op == "equal":
            continue
        for k in range(a0, a1):
            res.problems.append(f"missing or edited: expected {ascii(want[k])[:160]}")
        for k in range(b0, b1):
            res.problems.append(
                f"unnamed line {actual[k][1]}: {ascii(got[k].replace(TOKEN, '[block] '))[:160]}"
            )
    return res


def render(old_data: bytes, rules: Rules, fills: dict[str, list[str]]) -> bytes:
    """The intended file: the rules applied to the copy, each block filled from `fills`."""
    problems: list[str] = []
    plan = expected([t for t, _ in split(old_data)], rules, problems)
    if problems:
        raise ValueError(problems)
    eol = "\r\n" if b"\r\n" in old_data else "\n"
    lines: list[str] = []
    for tag, text in plan:
        lines.extend(fills[text[len(TOKEN) :]] if tag == "block" else [text])
    return (eol.join(lines) + eol).encode("utf-8")


def porcelain_paths(root: pathlib.Path) -> list[str]:
    out = subprocess.run(
        [
            "git",
            "status",
            "--porcelain",
            "--untracked-files=all",
            "--",
            "ui/tests",
            "tests",
            "tools/e2e_host",
        ],
        cwd=root,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8", "replace")
    paths = []
    for row in out.splitlines():
        if len(row) > 3:
            paths.append(row[3:].split(" -> ")[-1].strip().strip('"'))
    return paths


def run(root: pathlib.Path, copies: pathlib.Path, expect_changed: list[str]) -> int:
    bad = 0
    for path, rules in RULES.items():
        copy = copies / path
        live = root / path
        if not copy.is_file() or not live.is_file():
            print("FAIL", path, "copy or file missing")
            bad += 1
            continue
        old_data = copy.read_bytes()
        new_data = live.read_bytes()
        if old_data == new_data:
            if path in expect_changed:
                print("FAIL", path, "expected changed, is byte-identical to its copy")
                bad += 1
                continue
            print("ok  ", path, "unchanged")
            continue
        res = check(old_data, new_data, rules)
        print("FAIL" if res.problems else "ok  ", path, "changed", f"named={len(res.inserted)}")
        for problem in res.problems:
            print("     problem:", ascii(problem)[1:-1])
        for line_no, text in res.inserted:
            print(f"     + {line_no}: {ascii(text)[1:-1][:200]}")
        bad += 1 if res.problems else 0
    for path in expect_changed:
        if path not in RULES:
            print("FAIL --expect-changed names a file with no rules:", ascii(path))
            bad += 1
    extra = sorted(p for p in porcelain_paths(root) if p not in ALLOWED)
    print("changed paths outside the allowed set:", extra if extra else "none")
    bad += len(extra)
    print("diff-check:", "PASS" if bad == 0 else f"FAIL ({bad})")
    return 0 if bad == 0 else 1


FILLS = {
    HARNESS_START: [
        HARNESS_START + ", () => {",
        "  it('AC-161.8 x', () => {",
        "    expect(1).toBe(1)",
        "  })",
        "})",
    ],
    PLATES_START: [
        PLATES_START + "; a trailing \\n reaches the empty line', () => {",
        "    expect(1).toBe(1)",
        "  })",
    ],
}
GUARD = (
    "  if (!await page.evaluate(() => matchMedia('(hover: hover)').matches)) {",
    "    await app.close()",
    "    return",
    "  }",
)


def real_base(path: str) -> bytes | None:
    """The row-0 copy, or before row 0 the tracked file when git shows it unchanged."""
    copy = COPIES / path
    if copy.is_file():
        return copy.read_bytes()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", path], cwd=REPO, capture_output=True, check=True
    ).stdout
    return None if dirty.strip() else (REPO / path).read_bytes()


def with_line(data: bytes, anchor: str, line: str, before: bool = True) -> bytes:
    """`data` with `line` added before (or after) the one line equal to `anchor`."""
    eol = "\r\n" if b"\r\n" in data else "\n"
    rows = data.decode("utf-8").split(eol)
    hits = [i for i, row in enumerate(rows) if row == anchor]
    assert len(hits) == 1, (anchor, len(hits))
    rows.insert(hits[0] if before else hits[0] + 1, line)
    return eol.join(rows).encode("utf-8")


def real_cases() -> list[tuple[str, bytes, bytes, Rules, bool]]:
    cases: list[tuple[str, bytes, bytes, Rules, bool]] = []
    for path, rules in RULES.items():
        base = real_base(path)
        if base is None:
            cases.append((f"{path}: no clean base", b"", b"x", Rules(), True))
            continue
        good = render(base, rules, FILLS)
        cases.append((f"{path}: the intended edit passes", base, good, rules, True))
        if rules.insert or rules.new_block or rules.wildcard:
            eol = "\r\n" if b"\r\n" in base else "\n"
            first = good.decode("utf-8").split(eol)[0]
            bad = with_line(good, first, "const UNNAMED = 1", before=False)
            cases.append((f"{path}: an unnamed inserted line fails", base, bad, rules, False))
    s = E2E + "settings.test.ts"
    base = real_base(s)
    if base is not None:
        rules = RULES[s]
        good = render(base, rules, FILLS)
        mutant = good
        for line in GUARD:
            mutant = with_line(mutant, HOVER_PRECONDITION, line)
        cases.append((f"{s}: the round 1 early-return mutant fails", base, mutant, rules, False))
        eol = "\r\n" if b"\r\n" in base else "\n"
        gone = good.replace((HOVER_PRECONDITION + eol).encode(), b"")
        cases.append((f"{s}: the precondition missing fails", base, gone, rules, False))
        moved = with_line(gone, "  await lightBtn.hover()", HOVER_PRECONDITION, before=False)
        cases.append((f"{s}: the precondition after the hover fails", base, moved, rules, False))
        skip = with_line(good, HOVER_PRECONDITION, "  test.skip()")
        cases.append((f"{s}: an inserted test.skip fails", base, skip, rules, False))
    h = UNIT + "e2e-harness.test.ts"
    base = real_base(h)
    if base is not None:
        good = render(base, RULES[h], FILLS)
        stray = with_line(good, "    expect(1).toBe(1)", "    return")
        cases.append((f"{h}: a line inside the new block passes", base, stray, RULES[h], True))
        out = with_line(good, "type Env = Record<string, string | undefined>", "// unnamed")
        cases.append((f"{h}: a line outside the new block fails", base, out, RULES[h], False))
    return cases


def selftest() -> int:
    crlf = Rules(replace=(Replace("  it('A", "w: 15", "w: 16"),))
    base = (
        b"x\r\n  it('A', () => {\r\n    a(w: 15)\r\n    b()\r\n  })\r\n"
        b"  it('B', () => {\r\n    a(w: 15)\r\n  })\r\n"
    )
    good = base.replace(b"    a(w: 15)\r\n    b()", b"    a(w: 16)\r\n    b()")
    cases = [
        ("pinned replace passes", base, good, crlf, True),
        (
            "replace in the other block fails",
            base,
            base.replace(b"a(w: 15)\r\n  })", b"a(w: 16)\r\n  })"),
            crlf,
            False,
        ),
        (
            "an extra edit on the pinned line fails",
            base,
            good.replace(b"a(w: 16)", b"c(w: 16)"),
            crlf,
            False,
        ),
        ("another line edited fails", base, good.replace(b"    b()", b"    b(1)"), crlf, False),
        (
            "an insertion where none is allowed fails",
            base,
            good.replace(b"x\r\n", b"x\r\ny\r\n"),
            crlf,
            False,
        ),
        ("line endings changed fails", base, good.replace(b"\r\n", b"\n"), crlf, False),
        ("unchanged pin text fails", base, base, crlf, False),
    ]
    lf = Rules(
        remove=(Remove("import S"), Remove("const M", "type T")),
        insert=(Insert(None, "const H = 1", ("const P = 3",)),),
        wildcard=(Wildcard("  it('C old", "  it('C new"),),
    )
    old = (
        b"import S\nimport t\nconst H = 1\nconst M = 2\nfunction o() {\n}\n\ntype T = 1\n"
        b"  it('C old', () => {\n    q()\n  })\nz\n"
    )
    new = (
        b"import t\nconst H = 1\nconst P = 3\ntype T = 1\n"
        b"  it('C new', () => {\n    r()\n    s()\n  })\nz\n"
    )
    cases += [
        ("removals, a wildcard block and a named insertion pass", old, new, lf, True),
        ("a removed line kept fails", old, b"import S\n" + new, lf, False),
        ("a kept line dropped fails", old, new.replace(b"const H = 1\n", b""), lf, False),
        (
            "the old wildcard start kept fails",
            old,
            new.replace(b"z\n", b"  it('C old', () => {\n  })\nz\n"),
            lf,
            False,
        ),
        ("an unnamed insertion fails", old, new.replace(b"z\n", b"z\nw\n"), lf, False),
        (
            "the named insertion at another place fails",
            old,
            new.replace(b"const P = 3\n", b"").replace(b"z\n", b"z\nconst P = 3\n"),
            lf,
            False,
        ),
        ("the named insertion missing fails", old, new.replace(b"const P = 3\n", b""), lf, False),
    ]
    cases += real_cases()
    failed = 0
    for name, a, b, rules, want in cases:
        got = not check(a, b, rules).problems
        mark = "ok  " if got == want else "FAIL"
        failed += got != want
        print(mark, name, "->", "pass" if got else "fail")
    with tempfile.TemporaryDirectory() as tmp:
        probe = pathlib.Path(tmp) / "t.txt"
        probe.write_bytes(b"a\r\nb\n")
        rows = split(probe.read_bytes())
        ok = rows == [("a", "CRLF"), ("b", "LF")]
        failed += not ok
        print("ok  " if ok else "FAIL", "split keeps each ending kind")
    for path in RULES:
        if any(ch in path for ch in ("\\", ":")):
            failed += 1
            print("FAIL rule path not repo-relative:", path)
    print("selftest:", "PASS" if failed == 0 else f"FAIL ({failed})", f"({len(cases) + 1} cases)")
    return 0 if failed == 0 else 1


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect-changed", nargs="*", default=[])
    parser.add_argument("--selftest", action="store_true")
    try:
        args = parser.parse_args(argv)
    except SystemExit:
        return 2
    if args.selftest:
        return selftest()
    root = pathlib.Path(
        subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, check=True)
        .stdout.decode()
        .strip()
    )
    return run(root, COPIES, list(args.expect_changed))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
