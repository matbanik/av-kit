"""Session 39 Red proof (task rows 2, 4; implementation-plan.md Verification Plan §2, ``RED_PROOF``).

Usage: ``python red-check.py RECEIPT [RECEIPT ...]`` -- each a pytest, Vitest or Playwright
receipt from the row's Red runs, with its child exit code beside it in ``RECEIPT.exit``
(the row writes it straight after ``$code=$LASTEXITCODE``). ``python red-check.py --selftest``
runs the positive and negative receipt fixtures below.

A receipt passes only when all of these hold:

* its ``.exit`` file holds a non-zero integer (the Red run really failed);
* it carries a failing-run summary (``N failed`` / ``N error``);
* every failure is attributed on a *diagnostic* line -- a pytest ``E`` line, a Vitest or
  Playwright ``AssertionError:``/``Error: expect(`` line, or an error line whose missing
  *subject* is a declared-new export or module -- never a source-context or test-title line;
* it shows no setup failure: an Electron launch failure, a test or action timeout, a
  refused connection, or a load/collection error whose missing subject is not declared-new.

The subject is the thing the error says is missing, taken from the error's own grammar
(``cannot import name 'X'``, ``No module named 'X'``, ``Cannot find module 'X'``,
``Failed to resolve import "X"``, ``does not provide an export named 'X'``,
``Failed to load url X``, ``has no attribute 'X'``, ``name 'X' is not defined``). A declared
name anywhere else on the line -- the importing test file in ``imported from ...``, a
``from 'module'`` clause, a stack frame -- does not count (round 1 F3). A line whose subject
cannot be extracted is never declared, and timeouts and launch failures are never excused.

Anything else is a test-setup defect (Stop condition S3), so it exits 1.

ANSI colour escapes are stripped before matching (carried from Session 36 row 2): Vitest colours
its summary and ``AssertionError`` lines, and ``ESC[31m6 failed`` has no word boundary before the digit.
A Zod schema that rejects a new mark type is not an exception: the Red tests assert
``expect(schema.safeParse(body).success).toBe(true)`` so the rejection prints an ``AssertionError``.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile

#: Exports and modules the plan declares new; their absence is the expected Red reason.
DECLARED_NEW = (
    "PixelateAnnotation",
    "EraserAnnotation",
    "PixelateAnnotationIn",
    "EraserAnnotationIn",
    "PIXELATE_BLOCK_MIN",
    "PIXELATE_BLOCK_MAX",
    "PIXELATE_BLOCK_DEFAULT",
    "apply_region_pass",
    "region_clip",
    "eraser_fill",
    "applyRegionPass",
    "regionClip",
    "eraserFill",
    "isRegionMark",
    "capture-region-pass",
)

#: Terminal colour/style escapes (CSI sequences); removed before any pattern is matched.
ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
FAILED_SUMMARY = re.compile(r"\b\d+ (failed|error|errors)\b")
#: Diagnostic lines only. A pytest failure line starts with ``E``; Vitest and Playwright
#: print ``AssertionError:`` or ``Error: expect(``. Source context (``>`` lines, test
#: titles, code excerpts) never matches.
ASSERTION_LINE = re.compile(
    r"^\s*E\s+(AssertionError|assert\s)|^\s*(AssertionError:|Error: expect\(|"
    r"(×|✗|FAIL).*AssertionError)"
)
ERROR_LINE = re.compile(
    r"^\s*(E\s+)?(ImportError|ModuleNotFoundError|AttributeError|NameError|TypeError|"
    r"SyntaxError|Error):|Failed to resolve import|does not provide an export named|"
    r"Failed to load url|Cannot find module"
)
SETUP_FAILURE = re.compile(
    r"Process failed to launch|electron\.launch|Test timeout of \d+ms exceeded|TimeoutError|"
    r"\b(locator|page|frame|elementHandle)\.\w+: Timeout\b|ECONNREFUSED|EADDRINUSE|"
    r"ERROR collecting|Failed to load url|Failed to resolve import|Cannot find module"
)


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
)
#: Never excused, whatever the line names.
HARD_SETUP_FAILURE = re.compile(
    r"Process failed to launch|electron\.launch|Test timeout of \d+ms exceeded|TimeoutError|"
    r"\b(locator|page|frame|elementHandle)\.\w+: Timeout\b|ECONNREFUSED|EADDRINUSE"
)


def _missing_subjects(line: str) -> list[str]:
    return [m.group(1) for pattern in MISSING_SUBJECT for m in pattern.finditer(line)]


def _names_declared(line: str) -> bool:
    """True only when every missing subject on the line is (or ends in) a declared-new name."""
    if HARD_SETUP_FAILURE.search(line):
        return False
    subjects = _missing_subjects(line)
    return bool(subjects) and all(any(name in subject for name in DECLARED_NEW) for subject in subjects)


def check(path: pathlib.Path) -> list[str]:
    problems: list[str] = []
    exit_file = path.with_name(path.name + ".exit")
    try:
        code = int(exit_file.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        problems.append(f"{path}: no readable child exit code in {exit_file.name}")
        code = None
    if code == 0:
        problems.append(f"{path}: child exit 0 -- the Red run passed")
    text = ANSI_ESCAPE.sub("", path.read_text(encoding="utf-8", errors="replace"))
    if not FAILED_SUMMARY.search(text):
        problems.append(f"{path}: no failing-run summary (Red needs failing tests)")
    attributed = False
    for line in text.splitlines():
        if SETUP_FAILURE.search(line) and not _names_declared(line):
            problems.append(f"{path}: setup failure, not a Red reason: {line.strip()[:200]}")
        if ASSERTION_LINE.search(line):
            attributed = True
        elif ERROR_LINE.search(line) and _names_declared(line):
            attributed = True
    if not attributed:
        problems.append(f"{path}: no diagnostic line attributes the failure to an assertion or a declared-new export")
    return problems


#: (name, receipt text, child exit, expected to pass)
SELFTEST = (
    ("pytest-assertion", ">       assert result == 3\nE       assert 2 == 3\n1 failed in 0.1s\n", 1, True),
    (
        "pytest-new-export",
        "E   ImportError: cannot import name 'PixelateAnnotation' from 'avkit_core.domain.capture'\n1 error in 0.2s\n",
        2,
        True,
    ),
    (
        "pytest-new-adapter-export",
        "E   ImportError: cannot import name 'apply_region_pass' from 'avkit_infra.capture.adapter'\n1 error in 0.2s\n",
        2,
        True,
    ),
    (
        "vitest-new-module",
        " FAIL  tests/unit/capture-region-pass.test.ts\nError: Failed to resolve import \"../src/capture-region-pass\"\n Test Files  1 failed (1)\n",
        1,
        True,
    ),
    (
        "vitest-zod-assertion",
        " FAIL  tests/capture.test.ts > AC-90.4 annotate accepts pixelate\n"
        "AssertionError: expected false to be true // Object.is equality\n Tests  1 failed (4)\n",
        1,
        True,
    ),
    (
        "playwright-assertion",
        "  1) AC-90.12 region layer matches the bake\n    Error: expect(received).toBeLessThanOrEqual(expected)\n  1 failed\n",
        1,
        True,
    ),
    (
        "electron-launch",
        "1 failed\nError: electron.launch: Process failed to launch!\n  at test('AC-90.12 region layer matches the bake')\n",
        1,
        False,
    ),
    (
        "locator-timeout",
        "    assert visible\nError: locator.click: Timeout 30000ms exceeded.\n1 failed\n",
        1,
        False,
    ),
    (
        "vitest-ansi-assertion",
        "\x1b[31m   \x1b[31m×\x1b[31m AC-90.9 pixelate option groups\x1b[39m\n"
        "\x1b[31mAssertionError: expected [ 'color', 'stroke' ] to deeply equal [ 'block' ]\x1b[39m\n"
        "\x1b[2m      Tests \x1b[22m \x1b[1m\x1b[31m3 failed\x1b[39m\x1b[22m\n",
        1,
        True,
    ),
    (
        "ansi-locator-timeout",
        "\x1b[31mError: locator.click: Timeout 30000ms exceeded.\x1b[39m\n\x1b[31m1 failed\x1b[39m\n",
        1,
        False,
    ),
    ("unrelated-import", "E   ImportError: cannot import name 'foo'\n1 error\n", 2, False),
    (
        # round 1 F3: a declared name only in the importing file's path must not excuse the miss
        "unrelated-module-from-new-test",
        "Error: Cannot find module ./typo-fixture imported from /ui/tests/unit/capture-region-pass.test.ts\n"
        " Test Files  1 failed (1)\n",
        1,
        False,
    ),
    (
        "unrelated-name-from-declared-module",
        "E   ImportError: cannot import name 'regoin_clip' from 'avkit_infra.capture.adapter' "
        "(imported for apply_region_pass)\n1 error in 0.2s\n",
        2,
        False,
    ),
    (
        "assertion-plus-unrelated-import",
        "AssertionError: expected false to be true\n"
        "Error: Failed to resolve import \"./capture-regoin-fixture\" from \"tests/unit/capture-region-pass.test.ts\"\n"
        " Tests  2 failed (4)\n",
        1,
        False,
    ),
    (
        "vitest-new-module-imported-from",
        "Error: Cannot find module '../src/renderer/src/features/capture/capture-region-pass' "
        "imported from /ui/tests/unit/capture-region-pass.test.ts\n Test Files  1 failed (1)\n",
        1,
        True,
    ),
    ("collection-error", "ERROR collecting tests/unit/test_capture_adapter.py\n1 error\n", 2, False),
    ("passing-run", "E       assert 2 == 3\n1 failed\n", 0, False),
    ("no-exit-file", "E       assert 2 == 3\n1 failed\n", None, False),
)


def selftest() -> int:
    failures = []
    with tempfile.TemporaryDirectory() as tmp:
        for name, text, code, want_pass in SELFTEST:
            receipt = pathlib.Path(tmp) / f"{name}.txt"
            receipt.write_text(text, encoding="utf-8")
            if code is not None:
                receipt.with_name(receipt.name + ".exit").write_text(str(code), encoding="utf-8")
            passed = not check(receipt)
            print(f"{name}: {'pass' if passed else 'refused'} (expected {'pass' if want_pass else 'refused'})")
            if passed != want_pass:
                failures.append(name)
    print(f"red-check selftest: {len(SELFTEST)} fixture(s), {len(failures)} wrong: {failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if not argv:
        print("usage: red-check.py RECEIPT [RECEIPT ...] | --selftest")
        return 2
    problems = [p for arg in argv for p in check(pathlib.Path(arg))]
    for p in problems:
        print("RED-CHECK:", p)
    print(f"red-check: {len(argv)} receipt(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
