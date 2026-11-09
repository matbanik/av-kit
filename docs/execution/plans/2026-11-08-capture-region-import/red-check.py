"""Session 58 Red proof (task rows 2 and 4; implementation-plan.md Verification Plan §2). A copy of Session 55's, with this plan's DECLARED_NEW.

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
    # Session 58's names added in Green (implementation-plan.md Verification Plan §1). Row 1
    # adds the region names as stubs (D-422), so no region Red names a missing one. The import
    # Reds reach CaptureImportIn only over HTTP, and the service-level Reds assert
    # callable(getattr(service, "import_image", None)) first, so a missing name prints an
    # assertion line. These entries excuse a non-required block only.
    "CaptureImportIn",
    "read_image_view",
    "import_image",
    "inspect_import",
    "write_upright_png",
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

PYTEST_HEADER = re.compile(r"^_{3,} (.+?) _{3,}\s*$")
PYTEST_SECTION = re.compile(r"^={3,}")
PYTEST_SUMMARY = re.compile(r"^=*\s*(\d+ [a-z]+(?:, \d+ [a-z]+)*) in [\d.]+s\b")
#: A pytest ``E`` line that starts a diagnostic (not a diff or ``where`` continuation).
PYTEST_DIAGNOSTIC = re.compile(r"^E\s+((?:[A-Za-z_][\w.]*)?(?:Error|Exception|Exit|Interrupt)\b.*|assert\s.*|Failed: .*)$")
PYTEST_ASSERTION = re.compile(r"^((?:\w+\.)*AssertionError\b|assert\s|Failed: DID NOT RAISE\b)")

VITEST_HEADER = re.compile(r"^\s*FAIL\s+(\S.*)$")
VITEST_BOUNDARY = re.compile(r"\[\d+/\d+\]\S*\s*$|Failed (Tests|Suites) \d+|^\s*Test Files\s")
VITEST_SUMMARY = re.compile(r"^\s*Tests\s+(.*\d+ [a-z]+.*?)\s*(\(\d+\))?\s*$")

PLAYWRIGHT_HEADER = re.compile(r"^\s{1,4}\d+\) (\S.*)$")
PLAYWRIGHT_BOUNDARY = re.compile(r"^\s+\d+ (failed|passed|flaky|skipped|did not run|interrupted)\s*$")
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


def _split(lines: list[str], header: re.Pattern[str], boundary: re.Pattern[str], group: bool) -> list[Block]:
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


def _summary_counts(text: str) -> dict[str, tuple[int, int]]:
    """Runner -> (failed, errors) for every runner whose failing summary appears."""
    found: dict[str, tuple[int, int]] = {}
    for line in text.splitlines():
        m = PYTEST_SUMMARY.match(line)
        if m:
            counts = dict((word, int(n)) for n, word in re.findall(r"(\d+) ([a-z]+)", m.group(1)))
            failed, errors = counts.get("failed", 0), counts.get("error", 0) + counts.get("errors", 0)
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
                    b.diagnostics.append((m.group(1).strip(), _classify(m.group(1), PYTEST_ASSERTION)))
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
    for line in lines:
        if HARD_SETUP_FAILURE.search(line):
            problems.append(f"{path}: setup failure, not a Red reason: {line.strip()[:200]}")
    summaries = _summary_counts(text)
    if len(summaries) != 1:
        problems.append(f"{path}: expected exactly one runner's failing-run summary, found {sorted(summaries) or 'none'}")
        return problems, []
    runner, (failed, errors) = next(iter(summaries.items()))
    blocks = _blocks(runner, lines)
    if runner == "pytest":
        error_blocks = [b for b in blocks if b.titles[0].startswith("ERROR ")]
        test_blocks = [b for b in blocks if not b.titles[0].startswith("ERROR ")]
        if (len(test_blocks), len(error_blocks)) != (failed, errors):
            problems.append(
                f"{path}: summary says {failed} failed / {errors} error but the receipt has "
                f"{len(test_blocks)} failure and {len(error_blocks)} error block(s); every failure must be shown (--tb=short)"
            )
    else:
        suite = [t for b in blocks for t in b.titles if t.rstrip().endswith("]") and " [ " in t]
        tests = [t for b in blocks for t in b.titles if t not in suite]
        if len(tests) != failed:
            problems.append(f"{path}: summary says {failed} failed but the receipt has {len(tests)} failed-test header(s)")
    if not blocks:
        problems.append(f"{path}: no failure block found ({runner}); the Red cannot be attributed")
    for b in blocks:
        name = b.titles[0].strip()[:120]
        if not b.diagnostics:
            problems.append(f"{path}: block '{name}' has no diagnostic line")
        for content, kind in b.diagnostics:
            if kind not in ("assertion", "declared"):
                problems.append(f"{path}: block '{name}': {kind} diagnostic, not a Red reason: {content[:200]}")
    return problems, blocks


def check_required(required: list[str], blocks: list[Block]) -> list[str]:
    problems = []
    for wanted in required:
        hits = [b for b in blocks if any(_title_matches(t, wanted) for t in b.titles)]
        if not hits:
            problems.append(f"required test {wanted} has no failure block (it passed or did not run)")
        for b in hits:
            if not b.diagnostics or any(kind != "assertion" for _, kind in b.diagnostics):
                problems.append(f"required test {wanted} did not fail by assertion alone: {[c[:80] for c, _ in b.diagnostics]}")
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
        out += [*body, " \u0393\u00a5\u00bb tests/unit/tts-page.behavior.test.ts:812:33", "", f"{sep}[{i}/{len(blocks)}]{sep}", ""]
    out += [" Test Files  1 failed (2)", f"      Tests  {summary}"]
    return "\n".join(out) + "\n"


def _pw(blocks: list[tuple[str, list[str]]], failed: int) -> str:
    out = [f"Running {len(blocks) + 2} tests using 1 worker", ""]
    for i, (title, body) in enumerate(blocks, 1):
        out += [f"  {i}) tests\\e2e\\tts-generate.test.ts:{640 + i}:1 \u0393\u00c7\u2551 {title} ", ""]
        out += [f"    {line}" for line in body] + [""]
    out += [f"  {failed} failed"] + [f"    tests\\e2e\\tts-generate.test.ts:641:1 \u0393\u00c7\u2551 {t}" for t, _ in blocks]
    out += ["  2 passed (14.2s)"]
    return "\n".join(out) + "\n"


EXPECT = ["Error: expect(received).toBeLessThanOrEqual(expected)", "", "Expected: <= 1", "Received:    4"]
NULL_BOX = ["TypeError: Cannot read properties of null (reading 'height')"]
ASSERT_PY = ["E   AssertionError: assert 'cuda' == 'cpu'", "E     ", "E     - cpu", "E     + cuda"]

#: (name, receipt text, child exit, --require titles, expected to pass)
SELFTEST: tuple[tuple[str, str, int | None, tuple[str, ...], bool], ...] = (
    # positive
    ("pytest-assertion", _py([("test_ac_94_1", ASSERT_PY)], "FAILED tests/x.py::test_ac_94_1 - AssertionError\n1 failed in 0.1s"), 1, (), True),
    ("pytest-did-not-raise", _py([("test_ac_94_9", ["E   Failed: DID NOT RAISE ModelLoadError"])], "1 failed, 4 deselected in 0.2s"), 1, (), True),
    (
        "pytest-new-export-in-test",
        _py([("test_ac_94_2", ["E   ImportError: cannot import name 'resizeBox' from 'avkit_infra.tts.adapter' (P:\\x.py)"])], "1 failed in 0.2s"),
        1, (), True,
    ),
    (
        "pytest-new-kwarg",
        _py([("test_ac_94_3", ["E   TypeError: KokoroAdapter.__init__() got an unexpected keyword argument 'boxHandlePoints'"])], "1 failed in 0.2s"),
        1, (), True,
    ),
    (
        "pytest-new-port-method",
        _py([("test_ac_94_6", ["E   AttributeError: 'ModelService' object has no attribute 'hitResizeHandle'"])], "1 failed in 0.2s"),
        1, (), True,
    ),
    (
        "pytest-monkeypatch-new-module-attribute",
        _py([("test_ac_94_4", ["E   AttributeError: <module 'avkit_infra.tts.adapter'> has no attribute 'scaleTextMark'"])], "1 failed in 0.4s"),
        1, (), True,
    ),
    (
        "pytest-every-block-attributed",
        _py(
            [
                ("test_ac_94_1", ASSERT_PY),
                ("test_ac_94_2", ["E   ImportError: cannot import name 'resizeBox' from 'avkit_infra.tts.adapter'"]),
                ("test_ac_94_8", ["E   assert 500 == 422", "E    +  where 500 = <Response [500]>.status_code"]),
            ],
            "3 failed, 12 deselected in 0.6s",
        ),
        1, (), True,
    ),
    (
        "vitest-assertion",
        _vt([(["AC-100.3 device options come from the catalog row"], ["AssertionError: expected [ 'auto', 'cuda', 'cpu', 'mps' ] to deeply equal [ 'auto', 'cpu' ]"])], "1 failed | 39 skipped (40)"),
        1, (), True,
    ),
    (
        "vitest-grouped-headers",
        _vt([(["AC-100.5 segmented md height", "AC-100.5 segmented md text"], ["AssertionError: expected 'inline-flex rounded' to contain 'h-9'"])], "2 failed | 38 skipped (40)"),
        1, (), True,
    ),
    (
        "vitest-ansi-assertion",
        "\x1b[31m FAIL \x1b[39m tests/unit/layout-primitives.test.ts > AC-100.5 segmented control md size\n"
        "\x1b[31mAssertionError: expected 'inline-flex rounded' to contain 'h-9'\x1b[39m\n"
        "\x1b[2m      Tests \x1b[22m \x1b[1m\x1b[31m1 failed\x1b[39m\x1b[22m | 7 passed (8)\n",
        1, (), True,
    ),
    (
        "playwright-required-by-expect",
        _pw([("AC-100.7 model row controls share one height", EXPECT), ("AC-100.8 speed and format rows align", EXPECT), ("AC-100.10 grid columns", EXPECT)], 3),
        1, ("AC-100.7", "AC-100.8", "AC-100.10"), True,
    ),
    # negative
    ("electron-launch", _pw([("AC-100.7 model row geometry", ["Error: electron.launch: Process failed to launch!"])], 1), 1, (), False),
    ("locator-timeout", _pw([("AC-100.8 rows align", ["Error: locator.boundingBox: Timeout 30000ms exceeded."])], 1), 1, (), False),
    (
        "ansi-locator-timeout",
        "  1) tests\\e2e\\tts-generate.test.ts:641:1 > AC-100.9 x\n\x1b[31m    Error: locator.click: Timeout 30000ms exceeded.\x1b[39m\n\x1b[31m  1 failed\x1b[39m\n",
        1, (), False,
    ),
    ("pytest-unrelated-import", _py([("test_ac_94_2", ["E   ImportError: cannot import name 'foo' from 'avkit_infra.tts.adapter'"])], "1 failed in 0.1s"), 1, (), False),
    (
        "pytest-unrelated-kwarg",
        _py([("test_ac_94_3", ["E   TypeError: KokoroAdapter.__init__() got an unexpected keyword argument 'readBootThme'"])], "1 failed in 0.1s"),
        1, (), False,
    ),
    (
        "pytest-declared-prefix-is-not-declared",
        _py([("test_ac_94_2", ["E   ImportError: cannot import name 'resizeBox_typo' from 'avkit_infra.tts.adapter'"])], "1 failed in 0.2s"),
        1, (), False,
    ),
    (
        "pytest-declared-name-elsewhere-on-line",
        _py([("test_ac_94_2", ["E   ImportError: cannot import name 'resizeBxo' from 'avkit_infra.tts.adapter' (imported for resizeBox)"])], "1 failed in 0.2s"),
        1, (), False,
    ),
    (
        "pytest-undeclared-attribute",
        _py([("test_ac_94_4", ["E   AttributeError: <module 'avkit_infra.tts.adapter'> has no attribute 'InferenceSesion'"])], "1 failed in 0.4s"),
        1, (), False,
    ),
    ("pytest-bare-keyerror", _py([("test_ac_94_6", ["E   KeyError: 'devices'"])], "1 failed in 0.2s"), 1, (), False),
    (
        "pytest-missing-field-as-attribute",
        _py([("test_ac_94_7", ["E   AttributeError: 'NoneType' object has no attribute 'devices'"])], "1 failed in 0.2s"),
        1, (), False,
    ),
    (
        "pytest-collection-interrupted",
        "=" * 20 + " ERRORS " + "=" * 20 + "\n" + "_" * 10 + " ERROR collecting tests/integration/test_tts_device_resolution.py " + "_" * 10 + "\n"
        "ImportError while importing test module 'P:\\x\\test_tts_device_resolution.py'.\n"
        "E   ImportError: cannot import name 'resizeBox' from 'avkit_infra.tts.adapter'\n"
        + "=" * 10 + " short test summary info " + "=" * 10 + "\nERROR tests/integration/test_tts_device_resolution.py\n"
        "!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!\n1 error in 0.11s\n",
        2, (), False,
    ),
    (
        "pytest-valid-assertion-beside-unrelated-error",
        _py([("test_ac_94_1", ASSERT_PY), ("test_ac_94_5", ["E   TypeError: FakeSession.__init__() missing 1 required positional argument: 'path'"])], "2 failed in 0.3s"),
        1, (), False,
    ),
    (
        "pytest-chained-unrelated-in-same-block",
        _py([("test_ac_94_5", ["E   RuntimeError: CUDA session failed", "During handling of the above exception, another exception occurred:", *ASSERT_PY])], "1 failed in 0.3s"),
        1, (), False,
    ),
    ("pytest-failure-not-shown", _py([("test_ac_94_1", ASSERT_PY)], "2 failed in 0.3s"), 1, (), False),
    (
        "vitest-valid-assertion-beside-unrelated-error",
        _vt(
            [
                (["AC-100.3 device options come from the catalog row"], ["AssertionError: expected [ 'auto', 'cuda' ] to deeply equal [ 'auto', 'cpu' ]"]),
                (["AC-100.2 stored device the row lacks shows auto"], ["TypeError: Cannot read properties of undefined (reading 'map')"]),
            ],
            "2 failed | 38 skipped (40)",
        ),
        1, (), False,
    ),
    (
        "playwright-round1-scenario",
        _pw([("AC-100.7 model row controls share one height", NULL_BOX), ("AC-100.8 speed and format rows align", NULL_BOX), ("AC-100.10 grid columns", EXPECT)], 3),
        1, ("AC-100.7", "AC-100.8", "AC-100.10"), False,
    ),
    ("playwright-required-test-passed", _pw([("AC-100.10 grid columns", EXPECT)], 1), 1, ("AC-100.7",), False),
    ("playwright-required-prefix-only", _pw([("AC-100.70 another test", EXPECT)], 1), 1, ("AC-100.7",), False),
    (
        "playwright-required-by-declared-name",
        _pw([("AC-100.7 model row", ["Error: Cannot find module '../../src/renderer/src/boxHandlePoints'"])], 1),
        1, ("AC-100.7",), False,
    ),
    ("playwright-retry-unrelated", _pw([("AC-100.7 model row", [*EXPECT, "", "Retry #1 ---", "", *NULL_BOX])], 1), 1, ("AC-100.7",), False),
    (
        "vitest-unhandled-errors",
        _vt([(["AC-100.3 device options"], ["AssertionError: expected 1 to be 2"])], "1 failed | 39 skipped (40)") + "\u23af\u23af Unhandled Errors \u23af\u23af\nVitest caught 1 unhandled error during the test run.\n",
        1, (), False,
    ),
    (
        # A Red test that calls a missing export before asserting it exists (Verification Plan §2).
        "vitest-not-a-function-is-unattributed",
        _vt([(["AC-100.1 resizeBox follows the event"], ["TypeError: tx.resizeBox is not a function"])], "1 failed | 39 skipped (40)"),
        1, (), False,
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
            print(f"{name}: {'pass' if passed else 'refused'} (expected {'pass' if want_pass else 'refused'}){reason}")
            if passed != want_pass:
                failures.append(name)
    positive = sum(1 for f in SELFTEST if f[4])
    print(
        f"red-check selftest: {len(SELFTEST)} fixture(s) ({positive} positive, {len(SELFTEST) - positive} negative), "
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
    print(f"red-check: {len(paths)} receipt(s), {len(required)} required test(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
