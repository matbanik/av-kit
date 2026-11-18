"""Session 74 Red proof (task row 4; implementation-plan.md Verification Plan §2). A copy of
Session 90's (2026-11-17-test-run-reliability), itself from Session 89's, 88's, 82's and 87's,
with this plan's DECLARED_NEW (phase_guard, guarded_model, splice, GuardSpec, KOKORO_FP16,
SpliceError) and this session's boundary fixtures (test_ac_144_1 never matches
test_ac_144_10 to test_ac_144_17; the find_spec Red by assertion). Session 90 change to the pytest
reading: an entry of pytest's ``warnings summary`` section that holds a
``PytestUnhandledThreadExceptionWarning`` (the YouTube Red's slowed worker runs on past
``:940`` into the next test) is neither a failure nor a setup failure, so its traceback lines
are not scanned for setup-failure words; every other line still is. The Session 82, 88 and 89
fixtures are kept as grammar regression.

Usage: ``python red-check.py [--require TITLE ...] RECEIPT [RECEIPT ...]`` -- each a pytest,
Vitest or Playwright receipt from the row's Red runs, with its child exit code beside it in
``RECEIPT.exit`` (the row writes it straight after ``$code=$LASTEXITCODE``). Each ``--require``
names a test (``AC-100.7``) that must fail by assertion in one of the receipts.
``python red-check.py --selftest`` runs the positive and negative receipt fixtures below.

A receipt passes only when all of these hold:

* its ``.exit`` file holds a non-zero integer (the Red run really failed);
* it carries exactly one runner's failing-run summary (pytest ``N failed`` / ``N error in``,
  Vitest ``Tests  N failed``, Playwright ``N failed``);
* the receipt splits into one failure block per failed test (pytest ``____ name ____``
  sections, Vitest ``FAIL`` headers, Playwright ``N)`` headers), and the block count equals the
  summary's count, so no failure goes unexamined (round 1 F1);
* **every** block is attributed: it has at least one diagnostic line, and every diagnostic line
  in it is an assertion (pytest ``E AssertionError``/``E assert``/``E Failed: DID NOT RAISE``,
  Vitest ``AssertionError:``, Playwright ``Error: expect(``) or an error whose missing subject
  is exactly a declared-new name. One unrelated ``TypeError`` refuses the receipt even when a
  valid assertion sits in the same or another block (round 1 F1);
* it shows no setup failure anywhere: an Electron launch failure, a test or action timeout, a
  refused connection, an unhandled error, or a pytest collection error (which interrupts the
  whole run and hides every other Red, so the Red tests import new names inside the test body).

The subject is the thing the error says is missing, taken from the error's own grammar
(``cannot import name 'X'``, ``No module named 'X'``, ``Cannot find module 'X'``,
``Failed to resolve import "X"``, ``does not provide an export named 'X'``,
``Failed to load url X``, ``has no attribute 'X'``, ``name 'X' is not defined``,
``unexpected keyword argument 'X'``). It is declared only when it *is* a declared name, or a
dotted or slash path whose last component is one: ``resizeBox_typo`` is not
``resizeBox`` (round 1 F1). A name anywhere else on the line never counts.

A ``--require`` title must match a failure block's title exactly up to a non-digit
(``AC-100.7`` never matches ``AC-100.70``), and every diagnostic in that block must be an
assertion: a required test that passed, was not run, or failed by a missing name is refused.

Anything else is a test-setup defect (Stop condition S3), so it exits 1.

ANSI colour escapes are stripped before matching (carried from Session 36 row 2). The block
markers used here are ASCII, so the mojibake that ``rtk proxy`` leaves in box-drawing and
arrow glyphs does not affect parsing. A new export is not an exception either: the Vitest Red
tests import the module as a namespace (``import * as tx from ...``) and assert
``typeof tx.resizeBox`` first, so its absence prints an assertion line, never a bare
``TypeError: ... is not a function`` (implementation-plan.md Verification Plan §2). Session 43
has no pytest Red; the pytest fixtures are kept as grammar regression.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile
from dataclasses import dataclass, field

#: Exports and modules the plan declares new; their absence is the expected Red reason.
DECLARED_NEW = (
    # Session 74's new names (implementation-plan.md §Single-statement contracts,
    # GUARD_IN_MEMORY). The Red tests assert find_spec(...) is not None first and import
    # inside the body, so a required Red fails by assertion; these excuse a non-required block.
    "phase_guard",
    "guarded_model",
    "splice",
    "GuardSpec",
    "KOKORO_FP16",
    "SpliceError",
    # Session 90's names, kept for its grammar-regression fixtures.
    # Session 90's new names (implementation-plan.md §Single-statement contracts): the dev
    # script's exports and electron-env.ts's MAIN_REJECTION_MARKER. The Red tests load the
    # modules through a dynamic import and assert existence or ``typeof`` first, so a required
    # Red fails by assertion; these entries excuse a non-required block only.
    "devEnv",
    "devArgs",
    "isEntry",
    "exitCodeFor",
    "DEV_NOTICE",
    "MAIN_REJECTION_MARKER",
    # Session 89's name, kept for its grammar-regression fixtures.
    "takeHeldBrowse",
    # The names the --selftest fixtures declare; nothing in this session uses them.
    "resizeBox",
    "hitResizeHandle",
    "capture-transform",
    "boxHandlePoints",
    "scaleTextMark",
)

#: Terminal colour/style escapes (CSI sequences); removed before any pattern is matched.
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")

#: Never excused, wherever it appears.
HARD_SETUP_FAILURE = re.compile(
    r"Process failed to launch|electron\.launch|Test timeout of \d+ms exceeded|TimeoutError|"
    r"\b(locator|page|frame|elementHandle)\.\w+: Timeout\b|ECONNREFUSED|EADDRINUSE|"
    r"Interrupted: \d+ errors? during collection|ERROR collecting|Unhandled (Errors?|Rejection)|"
    r"unhandled errors?\b"
)

# pytest frames a failure title with at least one underscore on each side; a title wider than
# the terminal gets exactly one (Session 76 row 1, D-919). Session 81 took that form (D-974);
# this copy takes it too (D-985), so a long test_ac_153_<n> title is still one block.
PYTEST_HEADER = re.compile(r"^_+ (.+?) _+\s*$")
PYTEST_SECTION = re.compile(r"^={3,}")
PYTEST_SUMMARY = re.compile(r"^=*\s*(\d+ [a-z]+(?:, \d+ [a-z]+)*) in [\d.]+s\b")
#: A pytest ``E`` line that starts a diagnostic (not a diff or ``where`` continuation).
PYTEST_DIAGNOSTIC = re.compile(
    r"^E\s+((?:[A-Za-z_][\w.]*)?(?:Error|Exception|Exit|Interrupt)\b.*|assert\s.*|Failed: .*)$"
)
PYTEST_ASSERTION = re.compile(r"^((?:\w+\.)*AssertionError\b|assert\s|Failed: DID NOT RAISE\b)")

VITEST_HEADER = re.compile(r"^\s*FAIL\s+(\S.*)$")
VITEST_BOUNDARY = re.compile(r"\[\d+/\d+\]\S*\s*$|Failed (Tests|Suites) \d+|^\s*Test Files\s")
VITEST_SUMMARY = re.compile(r"^\s*Tests\s+(.*\d+ [a-z]+.*?)\s*(\(\d+\))?\s*$")

PLAYWRIGHT_HEADER = re.compile(r"^\s{1,4}\d+\) (\S.*)$")
PLAYWRIGHT_BOUNDARY = re.compile(
    r"^\s+\d+ (failed|passed|flaky|skipped|did not run|interrupted)\s*$"
)
PLAYWRIGHT_SUMMARY = re.compile(r"^\s+(\d+) failed\s*$")

#: A Vitest or Playwright diagnostic line (``Error Context:`` and code frames never match).
JS_DIAGNOSTIC = re.compile(r"^\s*(?:Caused by: )?((?:[A-Za-z_$][\w$]*)?Error)(?::|\s*$)")
JS_ASSERTION = re.compile(r"^\s*(AssertionError\b|Error: expect\()")

#: The missing subject of a load/import error, by the error's grammar. Group 1 is the subject.
MISSING_SUBJECT = (
    re.compile(r"cannot import name ['\"]([^'\"]+)['\"]"),
    re.compile(r"No module named ['\"]([^'\"]+)['\"]"),
    re.compile(r"Cannot find module ['\"]([^'\"]+)['\"]"),
    re.compile(r"Cannot find module (\S+) imported from"),
    re.compile(r"Failed to resolve import ['\"]([^'\"]+)['\"]"),
    re.compile(r"does not provide an export named ['\"]([^'\"]+)['\"]"),
    re.compile(r"Failed to load url (\S+)"),
    re.compile(r"has no attribute ['\"]([^'\"]+)['\"]"),
    re.compile(r"name ['\"]([^'\"]+)['\"] is not defined"),
    re.compile(r"unexpected keyword argument ['\"]([^'\"]+)['\"]"),
)


@dataclass
class Block:
    titles: list[str]
    lines: list[str] = field(default_factory=list)
    #: Each diagnostic line with its class: assertion, declared, setup or unattributed.
    diagnostics: list[tuple[str, str]] = field(default_factory=list)


def _missing_subjects(line: str) -> list[str]:
    return [m.group(1) for pattern in MISSING_SUBJECT for m in pattern.finditer(line)]


def _is_declared(subject: str) -> bool:
    last = re.split(r"[./\\]", subject.rstrip("'\"").removesuffix(".ts").removesuffix(".tsx"))[-1]
    return subject in DECLARED_NEW or last in DECLARED_NEW


def _classify(content: str, assertion: re.Pattern[str]) -> str:
    if HARD_SETUP_FAILURE.search(content):
        return "setup"
    if assertion.search(content):
        return "assertion"
    subjects = _missing_subjects(content)
    if subjects and all(_is_declared(s) for s in subjects):
        return "declared"
    return "unattributed"


def _split(
    lines: list[str], header: re.Pattern[str], boundary: re.Pattern[str], group: bool
) -> list[Block]:
    """Blocks start at a header line and end at the next header or a boundary line.

    ``group``: consecutive header lines share one block (Vitest prints one error under several
    ``FAIL`` lines when the tests failed identically).
    """
    blocks: list[Block] = []
    current: Block | None = None
    for line in lines:
        m = header.match(line)
        if m:
            if group and current is not None and not current.lines:
                current.titles.append(m.group(1))
            else:
                current = Block([m.group(1)])
                blocks.append(current)
            continue
        if boundary.search(line):
            current = None
            continue
        if current is not None:
            current.lines.append(line)
    return blocks


PYTEST_WARNINGS_HEADER = re.compile(r"^=+ warnings summary =+\s*$")
THREAD_WARNING = "PytestUnhandledThreadExceptionWarning"


def _thread_warning_lines(lines: list[str]) -> set[int]:
    """Indexes of the lines of each ``warnings summary`` entry holding THREAD_WARNING.

    The section runs from its ``=== warnings summary ===`` header to the next ``===`` line or
    the ``-- Docs:`` line. An entry starts at an unindented line (a node id; several in a row
    share one entry) and runs to the next unindented line after an indented or blank one.
    """
    out: set[int] = set()
    i = 0
    while i < len(lines):
        if not PYTEST_WARNINGS_HEADER.match(lines[i]):
            i += 1
            continue
        end = i + 1
        while (
            end < len(lines)
            and not PYTEST_SECTION.match(lines[end])
            and not lines[end].startswith("-- Docs:")
        ):
            end += 1
        entries: list[list[int]] = []
        in_body = True
        for k in range(i + 1, end):
            line = lines[k]
            head = bool(line) and not line[0].isspace()
            if head and (in_body or not entries):
                entries.append([])
            in_body = not head
            if entries:
                entries[-1].append(k)
        for entry in entries:
            if any(THREAD_WARNING in lines[k] for k in entry):
                out.update(entry)
        i = end
    return out


def _summary_counts(text: str) -> dict[str, tuple[int, int]]:
    """Runner -> (failed, errors) for every runner whose failing summary appears."""
    found: dict[str, tuple[int, int]] = {}
    for line in text.splitlines():
        m = PYTEST_SUMMARY.match(line)
        if m:
            counts = dict((word, int(n)) for n, word in re.findall(r"(\d+) ([a-z]+)", m.group(1)))
            failed, errors = (
                counts.get("failed", 0),
                counts.get("error", 0) + counts.get("errors", 0),
            )
            if failed or errors:
                found["pytest"] = (failed, errors)
        m = VITEST_SUMMARY.match(line)
        if m and (n := re.search(r"(\d+) failed", m.group(1))):
            found["vitest"] = (int(n.group(1)), 0)
        m = PLAYWRIGHT_SUMMARY.match(line)
        if m:
            found["playwright"] = (int(m.group(1)), 0)
    return found


def _blocks(runner: str, lines: list[str]) -> list[Block]:
    if runner == "pytest":
        blocks = _split(lines, PYTEST_HEADER, PYTEST_SECTION, group=False)
        for b in blocks:
            for line in b.lines:
                m = PYTEST_DIAGNOSTIC.match(line)
                if m:
                    b.diagnostics.append(
                        (m.group(1).strip(), _classify(m.group(1), PYTEST_ASSERTION))
                    )
        return blocks
    if runner == "vitest":
        blocks = _split(lines, VITEST_HEADER, VITEST_BOUNDARY, group=True)
    else:
        blocks = _split(lines, PLAYWRIGHT_HEADER, PLAYWRIGHT_BOUNDARY, group=False)
    for b in blocks:
        for line in b.lines:
            if JS_DIAGNOSTIC.match(line):
                b.diagnostics.append((line.strip(), _classify(line, JS_ASSERTION)))
    return blocks


def _title_matches(title: str, wanted: str) -> bool:
    return re.search(r"(?<![\w.])" + re.escape(wanted) + r"(?![\d]|\.\d)", title) is not None


def check(path: pathlib.Path) -> tuple[list[str], list[Block]]:
    problems: list[str] = []
    exit_file = path.with_name(path.name + ".exit")
    try:
        code: int | None = int(exit_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        problems.append(f"{path}: no readable child exit code in {exit_file.name}")
        code = None
    if code == 0:
        problems.append(f"{path}: child exit 0 -- the Red run passed")
    text = ANSI_ESCAPE.sub("", path.read_text(encoding="utf-8", errors="replace"))
    lines = text.splitlines()
    thread_warning = _thread_warning_lines(lines)
    for k, line in enumerate(lines):
        if k in thread_warning:
            continue
        if HARD_SETUP_FAILURE.search(line):
            problems.append(f"{path}: setup failure, not a Red reason: {line.strip()[:200]}")
    summaries = _summary_counts(text)
    if len(summaries) != 1:
        problems.append(
            f"{path}: expected exactly one runner's failing-run summary, found "
            f"{sorted(summaries) or 'none'}"
        )
        return problems, []
    runner, (failed, errors) = next(iter(summaries.items()))
    blocks = _blocks(runner, lines)
    if runner == "pytest":
        error_blocks = [b for b in blocks if b.titles[0].startswith("ERROR ")]
        test_blocks = [b for b in blocks if not b.titles[0].startswith("ERROR ")]
        if (len(test_blocks), len(error_blocks)) != (failed, errors):
            problems.append(
                f"{path}: summary says {failed} failed / {errors} error but the receipt has "
                f"{len(test_blocks)} failure and {len(error_blocks)} error block(s); every failure "
                "must be shown (--tb=short)"
            )
    else:
        suite = [t for b in blocks for t in b.titles if t.rstrip().endswith("]") and " [ " in t]
        tests = [t for b in blocks for t in b.titles if t not in suite]
        if len(tests) != failed:
            problems.append(
                f"{path}: summary says {failed} failed but the receipt has {len(tests)} "
                "failed-test header(s)"
            )
    if not blocks:
        problems.append(f"{path}: no failure block found ({runner}); the Red cannot be attributed")
    for b in blocks:
        name = b.titles[0].strip()[:120]
        if not b.diagnostics:
            problems.append(f"{path}: block '{name}' has no diagnostic line")
        for content, kind in b.diagnostics:
            if kind not in ("assertion", "declared"):
                problems.append(
                    f"{path}: block '{name}': {kind} diagnostic, not a Red reason: {content[:200]}"
                )
    return problems, blocks


def check_required(required: list[str], blocks: list[Block]) -> list[str]:
    problems = []
    for wanted in required:
        hits = [b for b in blocks if any(_title_matches(t, wanted) for t in b.titles)]
        if not hits:
            problems.append(
                f"required test {wanted} has no failure block (it passed or did not run)"
            )
        for b in hits:
            if not b.diagnostics or any(kind != "assertion" for _, kind in b.diagnostics):
                problems.append(
                    f"required test {wanted} did not fail by assertion alone: "
                    f"{[c[:80] for c, _ in b.diagnostics]}"
                )
    return problems


def run(paths: list[pathlib.Path], required: list[str]) -> list[str]:
    problems: list[str] = []
    blocks: list[Block] = []
    for p in paths:
        found, b = check(p)
        problems += found
        blocks += b
    return problems + check_required(required, blocks)


# --- selftest receipts, shaped on real runner output (pytest 8 -q --tb=short; Vitest 3.2 and
# Playwright list output as captured through rtk proxy in C:/Temp/av-kit/s37-87-red-*.txt).


def _py(blocks: list[tuple[str, list[str]]], summary: str) -> str:
    out = ["F" * len(blocks) + "    [100%]", "=" * 20 + " FAILURES " + "=" * 20]
    for title, body in blocks:
        out += ["_" * 12 + f" {title} " + "_" * 12, f"tests/x.py:3: in {title}", "    ...", *body]
    out += ["=" * 10 + " short test summary info " + "=" * 10, summary]
    return "\n".join(out) + "\n"


def _vt(blocks: list[tuple[list[str], list[str]]], summary: str) -> str:
    sep = "\u0393\u00c4\u00bb" * 6  # the mojibake rtk leaves for the Vitest rule glyph
    out = [f"{sep} Failed Tests {sum(len(h) for h, _ in blocks)} {sep}", ""]
    for i, (headers, body) in enumerate(blocks, 1):
        out += [f" FAIL  tests/unit/tts-page.behavior.test.ts > TTSPage > {h}" for h in headers]
        out += [
            *body,
            " \u0393\u00a5\u00bb tests/unit/tts-page.behavior.test.ts:812:33",
            "",
            f"{sep}[{i}/{len(blocks)}]{sep}",
            "",
        ]
    out += [" Test Files  1 failed (2)", f"      Tests  {summary}"]
    return "\n".join(out) + "\n"


def _pw(blocks: list[tuple[str, list[str]]], failed: int) -> str:
    out = [f"Running {len(blocks) + 2} tests using 1 worker", ""]
    for i, (title, body) in enumerate(blocks, 1):
        out += [
            f"  {i}) tests\\e2e\\tts-generate.test.ts:{640 + i}:1 \u0393\u00c7\u2551 {title} ",
            "",
        ]
        out += [f"    {line}" for line in body] + [""]
    out += [f"  {failed} failed"] + [
        f"    tests\\e2e\\tts-generate.test.ts:641:1 \u0393\u00c7\u2551 {t}" for t, _ in blocks
    ]
    out += ["  2 passed (14.2s)"]
    return "\n".join(out) + "\n"


EXPECT = [
    "Error: expect(received).toBeLessThanOrEqual(expected)",
    "",
    "Expected: <= 1",
    "Received:    4",
]
NULL_BOX = ["TypeError: Cannot read properties of null (reading 'height')"]
S74_FIND_SPEC = [
    "E   AssertionError: assert None is not None",
    "E    +  where None = <function find_spec at 0x0000>('avkit_infra.tts.phase_guard')",
]
ASSERT_PY = ["E   AssertionError: assert 'cuda' == 'cpu'", "E     ", "E     - cpu", "E     + cuda"]

#: Session 90's pytest Red shape: two assertion failures (the YouTube target at :940, the TTS
#: target at :260 in _install_spacy) and a thread-exception warning from the slowed worker
#: that runs on past :940, beside a "2 failed, 1 warning" summary.
S90_PY_RED = (
    "\n".join(
        [
            "FF                                                                [100%]",
            "=" * 20 + " FAILURES " + "=" * 20,
            "_" * 12 + " test_ac_122_8_surrogate_title_survives_real_storage " + "_" * 12,
            "tests\\integration\\test_youtube_adapter.py:940: in "
            "test_ac_122_8_surrogate_title_survives_real_storage",
            "    assert service.get_job(job.id).status is TranscriptStatus.Done",
            "E   AssertionError: assert <TranscriptStatus.Processing: 'Processing'> is "
            "<TranscriptStatus.Done: 'Done'>",
            "_" * 12 + " test_ac_62_16_model_overshoot_is_clipped_not_failed " + "_" * 12,
            "tests\\integration\\test_tts_assets.py:700: in "
            "test_ac_62_16_model_overshoot_is_clipped_not_failed",
            "    _install_spacy(stack)",
            "tests\\integration\\test_tts_assets.py:260: in _install_spacy",
            '    assert stack.wait_idle()["state"] == "Idle"',
            "E   AssertionError: assert 'Downloading' == 'Idle'",
            "E     ",
            "E     - Idle",
            "E     + Downloading",
            "=" * 20 + " warnings summary " + "=" * 20,
            "tests/integration/test_tts_assets.py::test_ac_62_16_model_overshoot_is_clipped_not_failed",
            "  <venv>\\_pytest\\threadexception.py:58: PytestUnhandledThreadExceptionWarning: "
            "Exception in thread Thread-7 (_run)",
            "  ",
            "  Traceback (most recent call last):",
            '    File "<venv>\\threading.py", line 1043, in _bootstrap_inner',
            "  sqlite3.ProgrammingError: Cannot operate on a closed database.",
            "  TimeoutError: a word the setup scan would refuse outside this entry",
            "  ",
            "    warnings.warn(pytest.PytestUnhandledThreadExceptionWarning(msg))",
            "",
            "-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html",
            "=" * 10 + " short test summary info " + "=" * 10,
            "FAILED tests/integration/test_youtube_adapter.py::"
            "test_ac_122_8_surrogate_title_survives_real_storage - AssertionError",
            "FAILED tests/integration/test_tts_assets.py::"
            "test_ac_62_16_model_overshoot_is_clipped_not_failed - AssertionError",
            "2 failed, 1 warning in 31.20s",
        ]
    )
    + "\n"
)

#: (name, receipt text, child exit, --require titles, expected to pass)
SELFTEST: tuple[tuple[str, str, int | None, tuple[str, ...], bool], ...] = (
    # positive
    (
        "pytest-assertion",
        _py(
            [("test_ac_94_1", ASSERT_PY)],
            "FAILED tests/x.py::test_ac_94_1 - AssertionError\n1 failed in 0.1s",
        ),
        1,
        (),
        True,
    ),
    (
        "pytest-did-not-raise",
        _py(
            [("test_ac_94_9", ["E   Failed: DID NOT RAISE ModelLoadError"])],
            "1 failed, 4 deselected in 0.2s",
        ),
        1,
        (),
        True,
    ),
    (
        "pytest-new-export-in-test",
        _py(
            [
                (
                    "test_ac_94_2",
                    [
                        "E   ImportError: cannot import name 'resizeBox' from "
                        "'avkit_infra.tts.adapter' (P:\\x.py)"
                    ],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        (),
        True,
    ),
    (
        "pytest-new-kwarg",
        _py(
            [
                (
                    "test_ac_94_3",
                    [
                        "E   TypeError: KokoroAdapter.__init__() got an unexpected keyword "
                        "argument 'boxHandlePoints'"
                    ],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        (),
        True,
    ),
    (
        "pytest-new-port-method",
        _py(
            [
                (
                    "test_ac_94_6",
                    [
                        "E   AttributeError: 'ModelService' object has no attribute "
                        "'hitResizeHandle'"
                    ],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        (),
        True,
    ),
    (
        "pytest-monkeypatch-new-module-attribute",
        _py(
            [
                (
                    "test_ac_94_4",
                    [
                        "E   AttributeError: <module 'avkit_infra.tts.adapter'> has no attribute "
                        "'scaleTextMark'"
                    ],
                )
            ],
            "1 failed in 0.4s",
        ),
        1,
        (),
        True,
    ),
    (
        "pytest-every-block-attributed",
        _py(
            [
                ("test_ac_94_1", ASSERT_PY),
                (
                    "test_ac_94_2",
                    [
                        "E   ImportError: cannot import name 'resizeBox' from "
                        "'avkit_infra.tts.adapter'"
                    ],
                ),
                (
                    "test_ac_94_8",
                    ["E   assert 500 == 422", "E    +  where 500 = <Response [500]>.status_code"],
                ),
            ],
            "3 failed, 12 deselected in 0.6s",
        ),
        1,
        (),
        True,
    ),
    (
        "vitest-assertion",
        _vt(
            [
                (
                    ["AC-100.3 device options come from the catalog row"],
                    [
                        "AssertionError: expected [ 'auto', 'cuda', 'cpu', 'mps' ] to deeply equal "
                        "[ 'auto', 'cpu' ]"
                    ],
                )
            ],
            "1 failed | 39 skipped (40)",
        ),
        1,
        (),
        True,
    ),
    (
        "vitest-grouped-headers",
        _vt(
            [
                (
                    ["AC-100.5 segmented md height", "AC-100.5 segmented md text"],
                    ["AssertionError: expected 'inline-flex rounded' to contain 'h-9'"],
                )
            ],
            "2 failed | 38 skipped (40)",
        ),
        1,
        (),
        True,
    ),
    (
        "vitest-ansi-assertion",
        "\x1b[31m FAIL \x1b[39m tests/unit/layout-primitives.test.ts > AC-100.5 segmented control "
        "md size\n"
        "\x1b[31mAssertionError: expected 'inline-flex rounded' to contain 'h-9'\x1b[39m\n"
        "\x1b[2m      Tests \x1b[22m \x1b[1m\x1b[31m1 failed\x1b[39m\x1b[22m | 7 passed (8)\n",
        1,
        (),
        True,
    ),
    (
        "pytest-long-title-one-underscore",
        _py([("test_long[" + "x" * 90 + "]", ASSERT_PY)], "1 failed in 0.1s")
        .replace("_" * 12 + " ", "_ ")
        .replace(" " + "_" * 12, " _"),
        1,
        ("test_long[" + "x" * 90 + "]",),
        True,
    ),
    # Session 82: the row-2 pytest Red (AC-153.1 by assertion, AC-153.3 by a boolean assert) and
    # the row-5 Vitest Red, whose code frame quotes createReadyLineReader in source (Session 78
    # RULE-2): a quoted API name in a frame is not a setup failure.
    (
        "pytest-required-ac-153-1-and-3",
        _py(
            [
                (
                    "test_ac_153_1_socket_listens_before_descriptor_and_ready_line",
                    ["E   assert 0 == 1"],
                ),
                (
                    "test_ac_153_3_connect_on_ready_line_is_accepted_five_spawns",
                    [
                        "E   AssertionError: assert False",
                        "E    +  where False = all([False, True, False, False, False])",
                    ],
                ),
            ],
            "2 failed, 9 deselected in 6.2s",
        ),
        1,
        ("test_ac_153_1", "test_ac_153_3"),
        True,
    ),
    (
        "vitest-required-ac-154-1-code-frame-quotes-reader",
        _vt(
            [
                (
                    ["AC-154.1 a ready line split in two publishes once"],
                    [
                        "AssertionError: expected 'undefined' to be 'function' // Object.is "
                        "equality",
                        "",
                        "- Expected",
                        "+ Received",
                        "",
                        "   14|   expect(typeof pm.createReadyLineReader).toBe('function')",
                        "     |                                           ^",
                        "   15|   expect(pm.READY_LINE_MAX_LENGTH).toBe(4096)",
                    ],
                ),
                (
                    ["AC-154.8 a real pipe splits the ready line and it publishes once"],
                    ["AssertionError: expected undefined to be 4096 // Object.is equality"],
                ),
            ],
            "2 failed | 1 passed (3)",
        ),
        1,
        ("AC-154.1", "AC-154.8"),
        True,
    ),
    (
        "playwright-required-by-expect",
        _pw(
            [
                ("AC-100.7 model row controls share one height", EXPECT),
                ("AC-100.8 speed and format rows align", EXPECT),
                ("AC-100.10 grid columns", EXPECT),
            ],
            3,
        ),
        1,
        ("AC-100.7", "AC-100.8", "AC-100.10"),
        True,
    ),
    # negative
    (
        "electron-launch",
        _pw(
            [
                (
                    "AC-100.7 model row geometry",
                    ["Error: electron.launch: Process failed to launch!"],
                )
            ],
            1,
        ),
        1,
        (),
        False,
    ),
    (
        "locator-timeout",
        _pw(
            [("AC-100.8 rows align", ["Error: locator.boundingBox: Timeout 30000ms exceeded."])], 1
        ),
        1,
        (),
        False,
    ),
    (
        "ansi-locator-timeout",
        "  1) tests\\e2e\\tts-generate.test.ts:641:1 > AC-100.9 x\n\x1b[31m    Error: "
        "locator.click: Timeout 30000ms exceeded.\x1b[39m\n\x1b[31m  1 failed\x1b[39m\n",
        1,
        (),
        False,
    ),
    (
        "pytest-unrelated-import",
        _py(
            [
                (
                    "test_ac_94_2",
                    ["E   ImportError: cannot import name 'foo' from 'avkit_infra.tts.adapter'"],
                )
            ],
            "1 failed in 0.1s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-unrelated-kwarg",
        _py(
            [
                (
                    "test_ac_94_3",
                    [
                        "E   TypeError: KokoroAdapter.__init__() got an unexpected keyword "
                        "argument 'readBootThme'"
                    ],
                )
            ],
            "1 failed in 0.1s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-declared-prefix-is-not-declared",
        _py(
            [
                (
                    "test_ac_94_2",
                    [
                        "E   ImportError: cannot import name 'resizeBox_typo' from "
                        "'avkit_infra.tts.adapter'"
                    ],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-declared-name-elsewhere-on-line",
        _py(
            [
                (
                    "test_ac_94_2",
                    [
                        "E   ImportError: cannot import name 'resizeBxo' from "
                        "'avkit_infra.tts.adapter' (imported for resizeBox)"
                    ],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-undeclared-attribute",
        _py(
            [
                (
                    "test_ac_94_4",
                    [
                        "E   AttributeError: <module 'avkit_infra.tts.adapter'> has no attribute "
                        "'InferenceSesion'"
                    ],
                )
            ],
            "1 failed in 0.4s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-bare-keyerror",
        _py([("test_ac_94_6", ["E   KeyError: 'devices'"])], "1 failed in 0.2s"),
        1,
        (),
        False,
    ),
    (
        "pytest-missing-field-as-attribute",
        _py(
            [
                (
                    "test_ac_94_7",
                    ["E   AttributeError: 'NoneType' object has no attribute 'devices'"],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-collection-interrupted",
        "=" * 20
        + " ERRORS "
        + "=" * 20
        + "\n"
        + "_" * 10
        + " ERROR collecting tests/integration/test_tts_device_resolution.py "
        + "_" * 10
        + "\n"
        "ImportError while importing test module 'P:\\x\\test_tts_device_resolution.py'.\n"
        "E   ImportError: cannot import name 'resizeBox' from 'avkit_infra.tts.adapter'\n"
        + "=" * 10
        + " short test summary info "
        + "=" * 10
        + "\nERROR tests/integration/test_tts_device_resolution.py\n"
        "!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!\n1 error in 0.11s\n",
        2,
        (),
        False,
    ),
    (
        "pytest-valid-assertion-beside-unrelated-error",
        _py(
            [
                ("test_ac_94_1", ASSERT_PY),
                (
                    "test_ac_94_5",
                    [
                        "E   TypeError: FakeSession.__init__() missing 1 required positional "
                        "argument: 'path'"
                    ],
                ),
            ],
            "2 failed in 0.3s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-chained-unrelated-in-same-block",
        _py(
            [
                (
                    "test_ac_94_5",
                    [
                        "E   RuntimeError: CUDA session failed",
                        "During handling of the above exception, another exception occurred:",
                        *ASSERT_PY,
                    ],
                )
            ],
            "1 failed in 0.3s",
        ),
        1,
        (),
        False,
    ),
    (
        "pytest-failure-not-shown",
        _py([("test_ac_94_1", ASSERT_PY)], "2 failed in 0.3s"),
        1,
        (),
        False,
    ),
    (
        "vitest-valid-assertion-beside-unrelated-error",
        _vt(
            [
                (
                    ["AC-100.3 device options come from the catalog row"],
                    [
                        "AssertionError: expected [ 'auto', 'cuda' ] to deeply equal [ 'auto', "
                        "'cpu' ]"
                    ],
                ),
                (
                    ["AC-100.2 stored device the row lacks shows auto"],
                    ["TypeError: Cannot read properties of undefined (reading 'map')"],
                ),
            ],
            "2 failed | 38 skipped (40)",
        ),
        1,
        (),
        False,
    ),
    (
        "playwright-round1-scenario",
        _pw(
            [
                ("AC-100.7 model row controls share one height", NULL_BOX),
                ("AC-100.8 speed and format rows align", NULL_BOX),
                ("AC-100.10 grid columns", EXPECT),
            ],
            3,
        ),
        1,
        ("AC-100.7", "AC-100.8", "AC-100.10"),
        False,
    ),
    (
        "playwright-required-test-passed",
        _pw([("AC-100.10 grid columns", EXPECT)], 1),
        1,
        ("AC-100.7",),
        False,
    ),
    (
        "playwright-required-prefix-only",
        _pw([("AC-100.70 another test", EXPECT)], 1),
        1,
        ("AC-100.7",),
        False,
    ),
    (
        "playwright-required-by-declared-name",
        _pw(
            [
                (
                    "AC-100.7 model row",
                    ["Error: Cannot find module '../../src/renderer/src/boxHandlePoints'"],
                )
            ],
            1,
        ),
        1,
        ("AC-100.7",),
        False,
    ),
    (
        "playwright-retry-unrelated",
        _pw([("AC-100.7 model row", [*EXPECT, "", "Retry #1 ---", "", *NULL_BOX])], 1),
        1,
        ("AC-100.7",),
        False,
    ),
    (
        "vitest-unhandled-errors",
        _vt(
            [(["AC-100.3 device options"], ["AssertionError: expected 1 to be 2"])],
            "1 failed | 39 skipped (40)",
        )
        + "\u23af\u23af Unhandled Errors \u23af\u23af\nVitest caught 1 unhandled error during the "
        "test run.\n",
        1,
        (),
        False,
    ),
    (
        # A Red test that calls a missing export before asserting it exists (Verification Plan §2).
        "vitest-not-a-function-is-unattributed",
        _vt(
            [
                (
                    ["AC-100.1 resizeBox follows the event"],
                    ["TypeError: tx.resizeBox is not a function"],
                )
            ],
            "1 failed | 39 skipped (40)",
        ),
        1,
        (),
        False,
    ),
    # Session 82: test_ac_153_1 is not met by test_ac_153_10, AC-154.1 not by AC-154.10; a
    # required Red that calls the missing reader, or fails on a refused connect, is refused.
    (
        "pytest-required-ac-153-1-boundary",
        _py([("test_ac_153_10_not_a_real_test", ["E   assert 0 == 1"])], "1 failed in 0.2s"),
        1,
        ("test_ac_153_1",),
        False,
    ),
    (
        "vitest-required-ac-154-1-boundary",
        _vt(
            [(["AC-154.10 not a real test"], ["AssertionError: expected 1 to be 2"])],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-154.1",),
        False,
    ),
    (
        "vitest-reader-not-a-function",
        _vt(
            [
                (
                    ["AC-154.1 a ready line split in two publishes once"],
                    ["TypeError: pm.createReadyLineReader is not a function"],
                )
            ],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-154.1",),
        False,
    ),
    (
        "pytest-ac-153-3-refused-connect-in-receipt",
        _py(
            [
                (
                    "test_ac_153_3_connect_on_ready_line_is_accepted_five_spawns",
                    ["E   ConnectionRefusedError: [WinError 10061] ECONNREFUSED"],
                )
            ],
            "1 failed in 3.1s",
        ),
        1,
        ("test_ac_153_3",),
        False,
    ),
    # Session 88: AC-155.1 is not met by AC-155.10, test_ac_155_1 not by test_ac_155_16; a
    # required Red whose code frame quotes qt.PAUSE_PENDING_LABEL passes; one that calls a
    # missing export before asserting it is refused.
    (
        "vitest-required-ac-155-1-boundary",
        _vt(
            [(["AC-155.10 not a real test"], ["AssertionError: expected 1 to be 2"])],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-155.1",),
        False,
    ),
    (
        "pytest-required-ac-155-1-boundary",
        _py(
            [("test_ac_155_16_pause_during_delay_wait", ["E   assert 'Processing' == 'Paused'"])],
            "1 failed in 2.2s",
        ),
        1,
        ("test_ac_155_1",),
        False,
    ),
    (
        "pytest-required-ac-155-16-to-18",
        _py(
            [
                (
                    "test_ac_155_16_pause_during_each_wait_lands_within_two_seconds",
                    ["E   AssertionError: assert 'Processing' == 'Paused'"],
                ),
                (
                    "test_ac_155_17_stop_during_delay_wait_lands_within_two_seconds",
                    ["E   AssertionError: assert 'Processing' == 'Idle'"],
                ),
                ("test_ac_155_18_wait_ends_early_after_pause", ["E   assert 2.0 < 0.5"]),
            ],
            "3 failed in 9.1s",
        ),
        1,
        ("test_ac_155_16", "test_ac_155_17", "test_ac_155_18"),
        True,
    ),
    (
        "vitest-required-ac-155-2-code-frame-quotes-label",
        _vt(
            [
                (
                    ["AC-155.2 pausePending disables the toggle and reads Pausing"],
                    [
                        "AssertionError: expected undefined to be 'Pausing…' // Object.is equality",
                        "",
                        "   12|   expect(qt.PAUSE_PENDING_LABEL).toBe('Pausing…')",
                        "     |                                  ^",
                    ],
                ),
            ],
            "1 failed | 3 passed (4)",
        ),
        1,
        ("AC-155.2",),
        True,
    ),
    (
        "vitest-pause-request-not-a-function",
        _vt(
            [
                (
                    ["AC-155.3 isPausePending truth table"],
                    ["TypeError: pq.isPausePending is not a function"],
                )
            ],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-155.3",),
        False,
    ),
    # Session 89: AC-156.1 is not met by AC-156.10, AC-157.1 not by AC-157.14; a Red that calls
    # the missing takeHeldBrowse before asserting it is refused; an Electron Red that fails a
    # setup precondition is refused; AC-157.8 and AC-157.9 failing by expect pass.
    (
        "vitest-required-ac-156-1-boundary",
        _vt(
            [
                (
                    ["AC-156.10 Cancel confirm closes when Paused"],
                    ["AssertionError: expected 1 to be 0"],
                )
            ],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-156.1",),
        False,
    ),
    (
        "vitest-required-ac-157-1-boundary",
        _vt(
            [
                (
                    ["AC-157.14 StrictMode mount takes one browse"],
                    ["AssertionError: expected 2 to be 1"],
                )
            ],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-157.1",),
        False,
    ),
    (
        "vitest-take-held-browse-not-a-function",
        _vt(
            [
                (
                    ["AC-157.6 mount takes a held browse"],
                    ["TypeError: cc.takeHeldBrowse is not a function"],
                )
            ],
            "1 failed | 2 passed (3)",
        ),
        1,
        ("AC-157.6",),
        False,
    ),
    (
        "playwright-ac-157-8-setup-precondition",
        _pw(
            [
                (
                    "AC-157.8 browse before the chunk loads opens one picker",
                    ["Error: setup: convert-page already mounted"],
                )
            ],
            1,
        ),
        1,
        ("AC-157.8",),
        False,
    ),
    (
        "playwright-ac-157-8-and-9-by-expect",
        _pw(
            [
                (
                    "AC-157.8 browse before the chunk loads opens one picker",
                    [
                        "Error: expect(received).toBe(expected) // Object.is equality",
                        "",
                        "Expected: 1",
                        "Received: 0",
                    ],
                ),
                (
                    "AC-157.9 a second browse during the load opens no second picker",
                    [
                        "Error: expect(received).toBe(expected) // Object.is equality",
                        "",
                        "Expected: 1",
                        "Received: 0",
                    ],
                ),
            ],
            2,
        ),
        1,
        ("AC-157.8", "AC-157.9"),
        True,
    ),
    # Session 90: AC-1 is not met by AC-10 to AC-17 (Vitest and Playwright); the pytest Red's
    # two targets by function name, with a thread-exception warning beside a "2 failed"
    # summary passing; the same warning beside a collection error, or a setup word outside a
    # thread-exception entry, is still refused; the Vitest and Playwright Reds by assertion.
    *(
        (
            f"vitest-required-ac-1-boundary-ac-{n}",
            _vt([([f"AC-{n} not the required test"], [EXPECT[0]])], "1 failed | 2 passed (3)"),
            1,
            ("AC-1",),
            False,
        )
        for n in range(10, 18)
    ),
    *(
        (
            f"playwright-required-ac-1-boundary-ac-{n}",
            _pw([(f"AC-{n} not the required test", EXPECT)], 1),
            1,
            ("AC-1",),
            False,
        )
        for n in range(10, 18)
    ),
    (
        "pytest-red-two-targets-with-thread-warning",
        S90_PY_RED,
        1,
        (
            "test_ac_122_8_surrogate_title_survives_real_storage",
            "test_ac_62_16_model_overshoot_is_clipped_not_failed",
        ),
        True,
    ),
    (
        "pytest-thread-warning-beside-collection-error",
        S90_PY_RED.replace(
            "2 failed, 1 warning in 31.20s", "2 failed, 1 warning, 1 error in 31.20s"
        ).replace(
            "_" * 12 + " test_ac_62_16",
            "ERROR collecting tests/integration/x.py\n" + "_" * 12 + " test_ac_62_16",
        ),
        1,
        (
            "test_ac_122_8_surrogate_title_survives_real_storage",
            "test_ac_62_16_model_overshoot_is_clipped_not_failed",
        ),
        False,
    ),
    (
        "pytest-timeout-outside-thread-warning",
        S90_PY_RED.replace(
            "-- Docs:", "tests/integration/y.py::test_z\n  TimeoutError: worker hung\n\n-- Docs:"
        ),
        1,
        (
            "test_ac_122_8_surrogate_title_survives_real_storage",
            "test_ac_62_16_model_overshoot_is_clipped_not_failed",
        ),
        False,
    ),
    (
        "pytest-red-one-target-passed",
        S90_PY_RED,
        1,
        ("test_ac_122_8_surrogate_title_survives_real_storage", "test_ac_62_1"),
        False,
    ),
    (
        "vitest-ac-6-7-red-by-typeof-and-ac-13-14",
        _vt(
            [
                (
                    ["AC-6 an unhandled rejection is logged and kept alive"],
                    ["AssertionError: expected 'undefined' to be 'string' // Object.is equality"],
                ),
                (
                    ["AC-7 a non-Error reason is recorded with its text"],
                    ["AssertionError: expected 'undefined' to be 'string' // Object.is equality"],
                ),
                (
                    ["AC-13 devEnv drops the variable"],
                    ["AssertionError: expected false to be true // Object.is equality"],
                ),
            ],
            "3 failed | 1 passed (4)",
        ),
        1,
        ("AC-6", "AC-7", "AC-13"),
        True,
    ),
    (
        "vitest-dev-env-not-a-function",
        _vt(
            [(["AC-13 devEnv drops the variable"], ["TypeError: mod.devEnv is not a function"])],
            "1 failed | 1 passed (2)",
        ),
        1,
        ("AC-13",),
        False,
    ),
    (
        "playwright-ac-9-by-expect",
        _pw(
            [("AC-9 an unhandled rejection in main fails the close", EXPECT)],
            1,
        ),
        1,
        ("AC-9",),
        True,
    ),
    # Session 74: test_ac_144_1 is not met by test_ac_144_10 to test_ac_144_17; the find_spec
    # Red passes by assertion; a required Red that fails by the missing module is refused.
    *(
        (
            f"pytest-required-ac-144-1-boundary-{n}",
            _py([(f"test_ac_144_{n}_not_the_required_test", S74_FIND_SPEC)], "1 failed in 0.2s"),
            1,
            ("test_ac_144_1",),
            False,
        )
        for n in range(10, 18)
    ),
    (
        "pytest-ac-144-find-spec-red",
        _py(
            [
                ("test_ac_144_1_splice_synthetic_bytes", S74_FIND_SPEC),
                ("test_ac_144_9_both_sessions_get_one_bytes_object", S74_FIND_SPEC),
                ("test_ac_144_11_real_ort_through_adapter", S74_FIND_SPEC),
            ],
            "3 failed, 1 passed in 0.9s",
        ),
        1,
        ("test_ac_144_1", "test_ac_144_9", "test_ac_144_11"),
        True,
    ),
    (
        "pytest-ac-144-required-by-missing-module",
        _py(
            [
                (
                    "test_ac_144_2_ort_nan_and_finite",
                    ["E   ModuleNotFoundError: No module named 'avkit_infra.tts.phase_guard'"],
                )
            ],
            "1 failed in 0.2s",
        ),
        1,
        ("test_ac_144_2",),
        False,
    ),
    ("no-summary", "E   AssertionError: assert 2 == 3\n", 1, (), False),
    ("passing-run", _py([("test_ac_94_1", ASSERT_PY)], "1 failed in 0.1s"), 0, (), False),
    ("no-exit-file", _py([("test_ac_94_1", ASSERT_PY)], "1 failed in 0.1s"), None, (), False),
)


def selftest() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, text, code, required, want_pass in SELFTEST:
            receipt = pathlib.Path(tmp) / f"{name}.txt"
            receipt.write_text(text, encoding="utf-8")
            if code is not None:
                receipt.with_name(receipt.name + ".exit").write_text(str(code), encoding="utf-8")
            problems = run([receipt], list(required))
            passed = not problems
            reason = "" if passed else f" -- {problems[0].split(': ', 1)[-1][:110]}"
            print(
                f"{name}: {'pass' if passed else 'refused'} (expected "
                f"{'pass' if want_pass else 'refused'}){reason}"
            )
            if passed != want_pass:
                failures.append(name)
    positive = sum(1 for f in SELFTEST if f[4])
    print(
        f"red-check selftest: {len(SELFTEST)} fixture(s) ({positive} positive, "
        f"{len(SELFTEST) - positive} negative), "
        f"{len(failures)} wrong: {failures}"
    )
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    # Receipts carry rtk's mojibake glyphs; a cp1252 console must not crash on them.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="backslashreplace")
    if argv == ["--selftest"]:
        return selftest()
    required: list[str] = []
    paths: list[pathlib.Path] = []
    it = iter(argv)
    for arg in it:
        if arg == "--require":
            required.append(next(it, ""))
        else:
            paths.append(pathlib.Path(arg))
    if not paths or "" in required:
        print("usage: red-check.py [--require TITLE ...] RECEIPT [RECEIPT ...] | --selftest")
        return 2
    problems = run(paths, required)
    for p in problems:
        print("RED-CHECK:", p)
    print(
        f"red-check: {len(paths)} receipt(s), {len(required)} required test(s), {len(problems)} "
        "problem(s)"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
