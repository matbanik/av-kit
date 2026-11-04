"""Session 36 Red proof (task rows 2, 4, 6; implementation-plan.md Verification Plan §2, ``RED_PROOF``).

Usage: ``python red-check.py RECEIPT [RECEIPT ...]`` -- each a pytest, Vitest or Playwright
receipt from the row's Red runs, with its child exit code beside it in ``RECEIPT.exit``
(the row writes it straight after ``$code=$LASTEXITCODE``). ``python red-check.py --selftest``
runs the positive and negative receipt fixtures below.

A receipt passes only when all of these hold:

* its ``.exit`` file holds a non-zero integer (the Red run really failed);
* it carries a failing-run summary (``N failed`` / ``N error``);
* every failure is attributed on a *diagnostic* line -- a pytest ``E`` line, a Vitest or
  Playwright ``AssertionError:``/``Error: expect(`` line, or an error line that names a
  declared-new export -- never a source-context or test-title line;
* it shows no setup failure: an Electron launch failure, a test or action timeout, a
  refused connection, or a load/collection error that names no declared-new export.

Anything else is a test-setup defect (Stop condition S3), so it exits 1.

ANSI colour escapes are stripped before matching (row 2 S3 fix, 2026-10-16): Vitest colours its
summary and ``AssertionError`` lines, and ``ESC[31m6 failed`` has no word boundary before the digit.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile

#: Exports and modules the plan declares new; their absence is the expected Red reason.
DECLARED_NEW = (
    "segoeAscentPx",
    "svgTextBaselineY",
    "SEGOE_UI_UNITS_PER_EM",
    "SEGOE_UI_ASCENDER",
    "arrowShaftEnd",
    "ARROW_SHAFT_OVERLAP_PX",
    "arrow_shaft_end",
    "SUPERSAMPLE",
    "viewedFilePath",
    "capture-viewed-file",
    "recordE2eShell",
    "e2eShellLog",
    "e2e-shell",
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


def _names_declared(line: str) -> bool:
    return any(name in line for name in DECLARED_NEW)


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
        "E   ImportError: cannot import name 'arrow_shaft_end' from 'avkit_infra.capture.adapter'\n1 error in 0.2s\n",
        2,
        True,
    ),
    (
        "vitest-new-export",
        " FAIL  tests/unit/capture-viewed-file.test.ts\nError: Failed to resolve import \"../src/capture-viewed-file\"\n Test Files  1 failed (1)\n",
        1,
        True,
    ),
    (
        "playwright-assertion",
        "  1) AC-82.6 preview ink matches bake\n    Error: expect(received).toBeLessThanOrEqual(expected)\n  1 failed\n",
        1,
        True,
    ),
    (
        "electron-launch",
        "1 failed\nError: electron.launch: Process failed to launch!\n  at test('AC-84.5 viewedFilePath opens the selected image')\n",
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
        "\x1b[31m   \x1b[31m×\x1b[31m AC-82.1 segoeAscentPx\x1b[39m\n"
        "\x1b[31mAssertionError: expected 'hanging' to be 'alphabetic'\x1b[39m\n"
        "\x1b[2m      Tests \x1b[22m \x1b[1m\x1b[31m6 failed\x1b[39m\x1b[22m\n",
        1,
        True,
    ),
    (
        "ansi-locator-timeout",
        "\x1b[31mError: locator.click: Timeout 30000ms exceeded.\x1b[39m\n\x1b[31m1 failed\x1b[39m\n",
        1,
        False,
    ),
    ("unrelated-import","E   ImportError: cannot import name 'foo'\n1 error\n", 2, False),
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
