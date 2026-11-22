"""Session 101 Red proof (task rows 1, 2, 3 and 3a; implementation-plan.md Verification Plan
§2). A copy of Session 99's (2026-11-20-help-quick-start/red-check.py), itself from Session
94's, 90's, 89's, 88's, 82's and 87's, with this plan's DECLARED_NEW first, the boundary
fixtures renamed to AC-163 (AC-163.1 never matches AC-163.10 to AC-163.14), and two Session 101
changes to the pytest mode (Session 101 fixtures below):

* under ``--runner pytest`` each ``--require`` name must also appear on a ``FAILED`` line,
  ``FAILED <path>::<name>`` (the short summary) or ``<path>::<name> FAILED`` (``-v``), with
  the bare name exactly (a ``[param]`` suffix is allowed), so a block is tied to a test that
  pytest reported as failed. An ``AssertionError`` or ``Failed: DID NOT RAISE`` in that test's
  block counts; an ``ERROR``, an ``ImportError`` and a collection error still refuse;
* a long traceback's frame separator (``_ _ _ _``) is never a block header, so a default
  ``--tb=long`` receipt keeps one block per failed test.

Session 99 added three options:

* ``--runner pytest|vitest|playwright``: the receipt's failing-run summary must be that
  runner's. Under pytest an error count, an ``ERROR`` line, an ``ImportError`` or
  ``ModuleNotFoundError`` and a collection error each refuse the receipt, and every
  diagnostic must be an assertion (a declared-new name never excuses a pytest Red);
* ``--allow-pass ID`` (repeatable): the test may pass, but it must appear in the receipt (so
  it ran), and if it failed, its block holds assertions only;
* ``--refuse-target-failure JSON``: the step targets (non-null ``target`` test ids) of that
  quick start JSON. A failure block whose lines name one, outside the code frame, is refused
  as S8: the stage could not show the target.

The grammar is Session 94's unchanged, and the earlier sessions' fixtures are kept as grammar
regression.

Usage: ``python red-check.py [--runner R] [--require TITLE ...] [--allow-pass TITLE ...]
[--refuse-target-failure JSON] RECEIPT [RECEIPT ...]`` -- each a pytest,
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

import json
import pathlib
import re
import sys
import tempfile
from dataclasses import dataclass, field

#: Exports and modules the plan declares new; their absence is the expected Red reason.
DECLARED_NEW = (
    # Session 101's new names (implementation-plan.md §Project files, DECLARED_NEW). The Vitest
    # Red imports transcript-commands as a namespace and asserts typeof resumeTranscriptJob
    # first, so a required Red fails by assertion; these entries excuse a non-required block
    # only. Under --runner pytest a declared name never excuses a block.
    "resume-job",
    "resume-job-btn",
    "resumeTranscriptJob",
    "transcript:resume_job",
    "transcript_paused_fixture",
    "test_transcript_defaults",
    "transcript-defaults.test",
    "MEU_116_PACING",
    "test_ac_116_9_a_retry_makes_a_300_an_hour_cap_wait",
    # Session 99's new names (implementation-plan.md §Project files, DECLARED_NEW). The unit Red
    # reaches each new module through import.meta.glob and asserts that it and its export exist
    # first, so a required Red fails by assertion; these entries excuse a non-required block only.
    "QUICK_START",
    "validateQuickStart",
    "quickStartHash",
    "quickStartHashInput",
    "shotUrl",
    "shotSize",
    "STAGES",
    "launchIsolated",
    "findPrivatePath",
    "clipText",
    "gatherShotText",
    "shotClip",
    "SHOT_MASKS",
    "HELP_QUICK_START",
    "HELP_QUICK_START_STEP",
    "HELP_QUICK_START_INTRO",
    "HELP_QUICK_START_HINT",
    "HELP_SHOT",
    # Session 94's new names (implementation-plan.md §Project files, DECLARED_NEW). The unit
    # Reds import the modules as namespaces (or through a dynamic import) and assert existence
    # or ``typeof`` first, so a required Red fails by assertion; these entries excuse a
    # non-required block only.
    "createHeldRequest",
    "currentRoute",
    "takeHeldHelpToggle",
    "HELP_FEATURE_ROUTE",
    "PREVIEW_NOTICE",
    "previewArgs",
    "runElectronVite",
    # Session 90's names, kept for its grammar-regression fixtures.
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
#: Session 101: a long traceback's frame separator (``_ _ _ _``) is not a header.
PYTEST_HEADER = re.compile(r"^_+ ((?![_ ]+$).+?) _+\s*$")
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
#: Playwright 1.64 prints a locator expect's subject state as its own ``Error:`` line under the
#: ``Error: expect(`` line (Session 99 row 5 Red). It is part of that assertion only when an
#: assertion line came before it in the same block; alone it stays unattributed.
PLAYWRIGHT_EXPECT_DETAIL = re.compile(r"^\s*Error: element\(s\) not found\s*$")

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
                kind = _classify(line, JS_ASSERTION)
                if (
                    runner == "playwright"
                    and kind == "unattributed"
                    and PLAYWRIGHT_EXPECT_DETAIL.match(line)
                    and any(k == "assertion" for _, k in b.diagnostics)
                ):
                    kind = "assertion"
                b.diagnostics.append((line.strip(), kind))
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


#: Session 99. A code-frame line (``  12 |`` or ``> 12 |``) or its caret line (``     |``)
#: quotes the test source, never the failure; a step target named there is not S8.
CODE_FRAME = re.compile(r"^\s*(?:>\s*)?\d+\s*\||^\s*\|(?:\s|$)")
#: Under ``--runner pytest`` these lines refuse the receipt: an error is never a Red.
PYTEST_REFUSED = re.compile(
    r"^ERROR\b|\sERROR(?:\s|$)|\b(?:ImportError|ModuleNotFoundError)\b|"
    r"errors? during collection|ERROR collecting"
)
RUNNERS = ("pytest", "vitest", "playwright")


def load_targets(path: pathlib.Path) -> tuple[str, ...]:
    """The non-null step targets of a quick start JSON (``{"pages": {f: {"steps": [...]}}}``)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    found = {
        step["target"]
        for page in data["pages"].values()
        for step in page["steps"]
        if step.get("target")
    }
    if not found:
        raise ValueError(f"{path}: no step target")
    return tuple(sorted(found))


def runner_problems(path: pathlib.Path, text: str, blocks: list[Block], runner: str) -> list[str]:
    summaries = _summary_counts(text)
    if runner not in summaries:
        return [
            f"{path}: --runner {runner}, but the failing-run summary is "
            f"{sorted(summaries) or 'none'}"
        ]
    problems: list[str] = []
    if runner == "pytest":
        errors = summaries["pytest"][1]
        if errors:
            problems.append(f"{path}: pytest reports {errors} error(s); an error is never a Red")
        for line in text.splitlines():
            if PYTEST_REFUSED.search(line):
                problems.append(
                    f"{path}: pytest error line, not a Red reason: {line.strip()[:200]}"
                )
        for b in blocks:
            for content, kind in b.diagnostics:
                if kind != "assertion":
                    problems.append(
                        f"{path}: block '{b.titles[0].strip()[:120]}': {kind} diagnostic under "
                        f"--runner pytest: {content[:160]}"
                    )
    return problems


def target_problems(path: pathlib.Path, blocks: list[Block], targets: tuple[str, ...]) -> list[str]:
    problems: list[str] = []
    patterns = [(t, re.compile(r"(?<![\w-])" + re.escape(t) + r"(?![\w-])")) for t in targets]
    for b in blocks:
        name = b.titles[0].strip()[:120]
        for line in b.lines:
            if CODE_FRAME.match(line):
                continue
            for target, pattern in patterns:
                if pattern.search(line):
                    problems.append(
                        f"{path}: S8: block '{name}' names step target '{target}': "
                        f"{line.strip()[:160]}"
                    )
    return problems


def check_allowed(allowed: list[str], blocks: list[Block], text: str) -> list[str]:
    problems: list[str] = []
    lines = text.splitlines()
    for wanted in allowed:
        if not any(_title_matches(line, wanted) for line in lines):
            problems.append(
                f"allowed test {wanted} does not appear in the receipt (it did not run)"
            )
        for b in blocks:
            if not any(_title_matches(t, wanted) for t in b.titles):
                continue
            if not b.diagnostics or any(kind != "assertion" for _, kind in b.diagnostics):
                problems.append(
                    f"allowed test {wanted} failed by something other than an assertion: "
                    f"{[c[:80] for c, _ in b.diagnostics]}"
                )
    return problems


#: Session 101: a pytest FAILED line, short summary (``FAILED path::node - msg``) or ``-v``
#: (``path::node FAILED``). A parametrised node id may hold spaces.
PYTEST_FAILED_LINE = (
    re.compile(r"^FAILED \S+?::(.+?)(?: - .*)?\s*$"),
    re.compile(r"^\S+?::(.+?) FAILED"),
)


def _failed_node_matches(node: str, wanted: str) -> bool:
    """The bare test name equals ``wanted``, or ``wanted`` is an id inside its ``[param]``."""
    name, _, param = node.partition("[")
    if name == wanted:
        return True
    return bool(param) and _title_matches(param.removesuffix("]"), wanted)


def pytest_failed_problems(required: list[str], text: str) -> list[str]:
    """Session 101: under --runner pytest each required name is on a ``FAILED`` line."""
    nodes = [
        m.group(1)
        for line in text.splitlines()
        for pattern in PYTEST_FAILED_LINE
        if (m := pattern.match(line))
    ]
    return [
        f"required test {wanted} has no FAILED <path>::{wanted} line (pytest did not report it "
        "failed)"
        for wanted in required
        if not any(_failed_node_matches(node, wanted) for node in nodes)
    ]


def run(
    paths: list[pathlib.Path],
    required: list[str],
    runner: str | None = None,
    allowed: tuple[str, ...] | list[str] = (),
    targets: tuple[str, ...] = (),
) -> list[str]:
    problems: list[str] = []
    blocks: list[Block] = []
    texts: list[str] = []
    for p in paths:
        found, b = check(p)
        problems += found
        blocks += b
        text = ANSI_ESCAPE.sub("", p.read_text(encoding="utf-8", errors="replace"))
        texts.append(text)
        if runner is not None:
            problems += runner_problems(p, text, b, runner)
        if targets:
            problems += target_problems(p, b, targets)
    problems += check_required(required, blocks)
    if runner == "pytest":
        problems += pytest_failed_problems(required, "\n".join(texts))
    return problems + check_allowed(list(allowed), blocks, "\n".join(texts))


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
    # Session 94 (ids renamed by Session 99, then to AC-163 by Session 101): AC-163.1 is not
    # met by AC-163.10 to
    # AC-163.14 (Vitest and Playwright), nor AC-159.1 by AC-159.10; a Playwright `setup:`
    # error and a call to the missing createHeldRequest before its typeof assertion are
    # refused; AC-163.8 failing by expect, and the unit Red's typeof assertion with a code
    # frame quoting the new name, pass.
    *(
        (
            f"vitest-required-ac-158-1-boundary-ac-158-{n}",
            _vt([([f"AC-163.{n} not the required test"], [EXPECT[0]])], "1 failed | 2 passed (3)"),
            1,
            ("AC-163.1",),
            False,
        )
        for n in range(10, 15)
    ),
    *(
        (
            f"playwright-required-ac-158-1-boundary-ac-158-{n}",
            _pw([(f"AC-163.{n} not the required test", EXPECT)], 1),
            1,
            ("AC-163.1",),
            False,
        )
        for n in range(10, 15)
    ),
    (
        "playwright-required-ac-159-1-boundary-ac-159-10",
        _pw([("AC-159.10 not the required test", EXPECT)], 1),
        1,
        ("AC-159.1",),
        False,
    ),
    (
        "playwright-ac-158-8-setup-precondition",
        _pw(
            [
                (
                    "AC-163.8 F1 before the Convert chunk loads opens the card once",
                    ["Error: setup: convert-page already mounted"],
                )
            ],
            1,
        ),
        1,
        ("AC-163.8",),
        False,
    ),
    (
        "playwright-ac-158-8-by-expect",
        _pw(
            [
                (
                    "AC-163.8 F1 before the Convert chunk loads opens the card once",
                    [
                        "Error: expect(received).toBe(expected) // Object.is equality",
                        "",
                        "Expected: true",
                        "Received: false",
                    ],
                )
            ],
            1,
        ),
        1,
        ("AC-163.8",),
        True,
    ),
    (
        "vitest-ac-158-1-by-typeof-code-frame-quotes-name",
        _vt(
            [
                (
                    ["AC-163.1 a held request is taken once"],
                    [
                        "AssertionError: expected 'undefined' to be 'function' // Object.is "
                        "equality",
                        "",
                        "   14|   expect(typeof nav.createHeldRequest).toBe('function')",
                        "     |                                        ^",
                    ],
                )
            ],
            "1 failed | 1 passed (2)",
        ),
        1,
        ("AC-163.1",),
        True,
    ),
    (
        "vitest-create-held-request-not-a-function",
        _vt(
            [
                (
                    ["AC-163.1 a held request is taken once"],
                    ["TypeError: nav.createHeldRequest is not a function"],
                )
            ],
            "1 failed | 1 passed (2)",
        ),
        1,
        ("AC-163.1",),
        False,
    ),
    ("no-summary", "E   AssertionError: assert 2 == 3\n", 1, (), False),
    ("passing-run", _py([("test_ac_94_1", ASSERT_PY)], "1 failed in 0.1s"), 0, (), False),
    ("no-exit-file", _py([("test_ac_94_1", ASSERT_PY)], "1 failed in 0.1s"), None, (), False),
)


def _pyv(
    passed: list[str], failed: list[tuple[str, list[str]]], summary: str, errors: int = 0
) -> str:
    """pytest -v --tb=short output for tests/tooling/test_help_guide_ste.py."""
    f = "tests/tooling/test_help_guide_ste.py"
    out = ["=" * 20 + " test session starts " + "=" * 20, "collected 4 items", ""]
    out += [f"{f}::{t} PASSED{' ' * 8}[ 25%]" for t in passed]
    out += [f"{f}::{t} FAILED{' ' * 8}[ 50%]" for t, _ in failed]
    out += [f"{f}::test_x[AC-163.2 parser] ERROR{' ' * 8}[ 75%]" for _ in range(errors)]
    out += ["", "=" * 20 + " ERRORS " + "=" * 20] if errors else []
    for _ in range(errors):
        out += [
            "_" * 6 + " ERROR at setup of test_x[AC-163.2 parser] " + "_" * 6,
            "tests\\tooling\\test_help_guide_ste.py:12: in fixture",
            "    ...",
            "E   AssertionError: assert False",
        ]
    out += ["", "=" * 20 + " FAILURES " + "=" * 20]
    for title, body in failed:
        name = title.split("[")[0]
        out += ["_" * 12 + f" {title} " + "_" * 12, f"{f}:40: in {name}", "    ...", *body]
    out += ["=" * 10 + " short test summary info " + "=" * 10]
    out += [f"FAILED {f}::{t} - AssertionError" for t, _ in failed]
    out += [f"ERROR {f}::test_x[AC-163.2 parser] - AssertionError" for _ in range(errors)]
    return "\n".join(out + [summary]) + "\n"


S99_PASSED = [
    "test_ste_gate[AC-163.2 selftest]",
    "test_ste_gate[AC-163.2 negatives]",
    "test_ste_gate[AC-163.2 parser]",
]
S99_REPO = ("test_ste_gate[AC-163.2 repo]", ASSERT_PY)
S99_ALLOW_PY = ("AC-163.2 selftest", "AC-163.2 negatives", "AC-163.2 parser")
S99_OK_CLOSED = (
    "  ok 2 [electron] \u203a tests\\e2e\\help-quick-start.test.ts:12:1 \u203a "
    "AC-163.10 closed on the first visit (2.1s)\n"
)
S99_TARGET_NAMED = [
    "Error: expect(locator).toBeVisible() failed",
    "",
    "Locator: getByTestId('url-input').first()",
    "Expected: visible",
    "Received: <element(s) not found>",
]
#: Playwright 1.64's locator expect, as row 5's Red receipt printed it.
S99_PW164_NOT_FOUND = [
    "Error: expect(locator).toHaveText(expected) failed",
    "",
    "Locator: getByTestId('help-card').getByTestId('help-quick-start-hint')",
    'Expected: "Quick start \u00b7 0 steps"',
    "Timeout: 5000ms",
    "Error: element(s) not found",
]
S99_LONE_NOT_FOUND = ["Error: element(s) not found"]
S99_TARGET_IN_FRAME = [
    *EXPECT,
    "",
    "  10 |   for (const step of steps) {",
    "> 11 |     await expect(page.getByTestId('url-input')).toBeVisible()",
    "     |                                                ^",
]

#: Session 99: (name, receipt text, exit code, required, runner, allowed, targets, want_pass).
SELFTEST_S99: tuple[
    tuple[
        str, str, int | None, tuple[str, ...], str | None, tuple[str, ...], tuple[str, ...], bool
    ],
    ...,
] = (
    (
        "s99-pytest-red",
        _pyv(S99_PASSED, [S99_REPO], "1 failed, 3 passed in 0.40s"),
        1,
        ("AC-163.2 repo",),
        "pytest",
        S99_ALLOW_PY,
        (),
        True,
    ),
    (
        "s99-pytest-allowed-not-run",
        _pyv(S99_PASSED[:2], [S99_REPO], "1 failed, 2 passed in 0.40s"),
        1,
        ("AC-163.2 repo",),
        "pytest",
        S99_ALLOW_PY,
        (),
        False,
    ),
    (
        "s99-pytest-declared-import-error",
        _pyv(
            S99_PASSED,
            [("test_ste_gate[AC-163.2 repo]", ["E   ImportError: cannot import name 'STAGES'"])],
            "1 failed, 3 passed in 0.40s",
        ),
        1,
        (),
        "pytest",
        (),
        (),
        False,
    ),
    (
        "s99-pytest-declared-import-error-no-runner-control",
        _pyv(
            S99_PASSED,
            [("test_ste_gate[AC-163.2 repo]", ["E   ImportError: cannot import name 'STAGES'"])],
            "1 failed, 3 passed in 0.40s",
        ),
        1,
        (),
        None,
        (),
        (),
        True,
    ),
    (
        "s99-pytest-error-count",
        _pyv(S99_PASSED[:2], [S99_REPO], "1 failed, 2 passed, 1 error in 0.40s", errors=1),
        1,
        ("AC-163.2 repo",),
        "pytest",
        (),
        (),
        False,
    ),
    (
        "s99-pytest-error-count-no-runner-control",
        _pyv(S99_PASSED[:2], [S99_REPO], "1 failed, 2 passed, 1 error in 0.40s", errors=1),
        1,
        ("AC-163.2 repo",),
        None,
        (),
        (),
        True,
    ),
    (
        "s99-runner-mismatch",
        _vt(
            [(["AC-163.1 the data validates"], ["AssertionError: expected 1 to be 0"])],
            "1 failed (1)",
        ),
        1,
        ("AC-163.1",),
        "pytest",
        (),
        (),
        False,
    ),
    (
        "s99-vitest-ac-162-1-by-typeof",
        _vt(
            [
                (
                    ["AC-163.1 the quick start data validates"],
                    ["AssertionError: expected 'undefined' to be 'function' // Object.is equality"],
                )
            ],
            "1 failed | 9 passed (10)",
        ),
        1,
        ("AC-163.1",),
        "vitest",
        (),
        (),
        True,
    ),
    (
        "s99-vitest-ac-162-10-not-1",
        _vt([(["AC-163.10 not the required test"], [EXPECT[0]])], "1 failed | 2 passed (3)"),
        1,
        ("AC-163.1",),
        "vitest",
        (),
        (),
        False,
    ),
    (
        "s99-pw-closed-allowed",
        S99_OK_CLOSED + _pw([("AC-163.10 hint shows the step count", EXPECT)], 1),
        1,
        ("AC-163.10 hint",),
        "playwright",
        ("AC-163.10 closed",),
        ("url-input", "add-btn"),
        True,
    ),
    (
        "s99-pw-allowed-not-run",
        _pw([("AC-163.10 hint shows the step count", EXPECT)], 1),
        1,
        ("AC-163.10 hint",),
        "playwright",
        ("AC-163.10 closed",),
        (),
        False,
    ),
    (
        "s99-pw-allowed-fails-by-assertion",
        _pw(
            [
                ("AC-163.10 hint shows the step count", EXPECT),
                ("AC-163.10 closed on the first visit", EXPECT),
            ],
            2,
        ),
        1,
        ("AC-163.10 hint",),
        "playwright",
        ("AC-163.10 closed",),
        (),
        True,
    ),
    (
        "s99-pw-allowed-fails-by-typeerror",
        _pw(
            [
                ("AC-163.10 hint shows the step count", EXPECT),
                ("AC-163.10 closed on the first visit", NULL_BOX),
            ],
            2,
        ),
        1,
        ("AC-163.10 hint",),
        "playwright",
        ("AC-163.10 closed",),
        (),
        False,
    ),
    (
        "s99-pw164-not-found-detail-is-the-assertion",
        _pw([("AC-163.10 hint shows the step count", S99_PW164_NOT_FOUND)], 1),
        1,
        ("AC-163.10 hint",),
        "playwright",
        (),
        (),
        True,
    ),
    (
        "s99-pw-lone-not-found-is-unattributed",
        _pw([("AC-163.10 hint shows the step count", S99_LONE_NOT_FOUND)], 1),
        1,
        ("AC-163.10 hint",),
        "playwright",
        (),
        (),
        False,
    ),
    (
        "s99-pw-step-target-named-is-s8",
        _pw([("AC-163.11 downloader steps and figures", S99_TARGET_NAMED)], 1),
        1,
        ("AC-163.11 downloader",),
        "playwright",
        (),
        ("url-input",),
        False,
    ),
    (
        "s99-pw-step-target-named-no-targets-control",
        _pw([("AC-163.11 downloader steps and figures", S99_TARGET_NAMED)], 1),
        1,
        ("AC-163.11 downloader",),
        "playwright",
        (),
        (),
        True,
    ),
    (
        "s99-pw-step-target-in-code-frame",
        _pw([("AC-163.11 downloader steps and figures", S99_TARGET_IN_FRAME)], 1),
        1,
        ("AC-163.11 downloader",),
        "playwright",
        (),
        ("url-input",),
        True,
    ),
    (
        "s99-pw-target-is-a-whole-id",
        _pw(
            [
                (
                    "AC-163.11 transcript steps and figures",
                    [*EXPECT, "Locator: getByTestId('queue-add-btn-x')"],
                )
            ],
            1,
        ),
        1,
        ("AC-163.11 transcript",),
        "playwright",
        (),
        ("add-btn",),
        True,
    ),
    (
        "s99-runner-playwright-on-vitest",
        _vt([(["AC-163.3 the hint"], [EXPECT[0]])], "1 failed (1)"),
        1,
        ("AC-163.3",),
        "playwright",
        (),
        (),
        False,
    ),
)


def _pyl(passed: list[str], failed: list[tuple[str, list[str]]], summary: str) -> str:
    """Session 101: pytest -v output with the default long traceback, for test_services.py."""
    f = "tests/unit/test_services.py"
    out = ["=" * 20 + " test session starts " + "=" * 20, "collected 3 items", ""]
    out += [f"{f}::{t} PASSED{' ' * 8}[ 33%]" for t in passed]
    out += [f"{f}::{t} FAILED{' ' * 8}[ 66%]" for t, _ in failed]
    out += ["", "=" * 20 + " FAILURES " + "=" * 20]
    for title, body in failed:
        out += [
            "_" * 12 + f" {title} " + "_" * 12,
            "",
            "tmp_path = WindowsPath('C:/Temp/x')",
            "",
            f"    def {title.split('[')[0]}(tmp_path):",
            "        services, captions = _transcript_stack(tmp_path)",
            ">       with pytest.raises(ConflictError):",
            *body,
            "",
            f"{f}:1234: Failed",
        ]
    out += ["=" * 10 + " short test summary info " + "=" * 10]
    out += [f"FAILED {f}::{t} - {body[0][4:]}" for t, body in failed]
    return "\n".join(out + [summary]) + "\n"


S101_RAISE = ["E       Failed: DID NOT RAISE <class 'avkit_core.errors.ConflictError'>"]
S101_REQ = "test_ac_163_6_refused_while_processing"
S101_GUARD = "test_ac_163_6_idle_resume_done"
S101_SEPARATED = [
    "",
    "tests/unit/test_services.py:900: in _helper",
    "    assert sleeps == {0.0, 120.0, 500.0}",
    "_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _",
    "E       AssertionError: assert {0.0, 6.0, 300.0} == {0.0, 120.0, 500.0}",
]

#: Session 101: (name, receipt text, exit code, required, allowed, want_pass); runner pytest.
SELFTEST_S101: tuple[tuple[str, str, int | None, tuple[str, ...], tuple[str, ...], bool], ...] = (
    (
        "s101-did-not-raise",
        _pyl([S101_GUARD], [(S101_REQ, S101_RAISE)], "1 failed, 1 passed in 1.20s"),
        1,
        (S101_REQ,),
        (S101_GUARD,),
        True,
    ),
    (
        "s101-frame-separator-one-block",
        _pyl([], [(S101_REQ, S101_SEPARATED)], "1 failed in 1.20s"),
        1,
        (S101_REQ,),
        (),
        True,
    ),
    (
        "s101-no-failed-line",
        _pyl([S101_GUARD], [(S101_REQ, S101_RAISE)], "1 failed, 1 passed in 1.20s")
        .replace(f"FAILED tests/unit/test_services.py::{S101_REQ} -", "short:")
        .replace(f"::{S101_REQ} FAILED", f"::{S101_REQ} XFAIL"),
        1,
        (S101_REQ,),
        (),
        False,
    ),
    (
        "s101-failed-line-other-name",
        _pyl([], [(S101_REQ + "_x", S101_RAISE)], "1 failed in 1.20s"),
        1,
        (S101_REQ,),
        (),
        False,
    ),
    (
        "s101-required-passed",
        _pyl([S101_REQ], [(S101_GUARD, S101_RAISE)], "1 failed, 1 passed in 1.20s"),
        1,
        (S101_REQ,),
        (),
        False,
    ),
    (
        "s101-import-error",
        _pyl(
            [],
            [(S101_REQ, ["E   ImportError: cannot import name 'resume_guard'"])],
            "1 failed in 1.20s",
        ),
        1,
        (S101_REQ,),
        (),
        False,
    ),
    (
        "s101-error-line",
        _pyl([], [(S101_REQ, S101_RAISE)], "1 failed, 1 error in 1.20s")
        + f"ERROR tests/unit/test_services.py::{S101_GUARD} - RuntimeError\n",
        1,
        (S101_REQ,),
        (),
        False,
    ),
    (
        "s101-collection-error",
        "=" * 20
        + " ERRORS "
        + "=" * 20
        + "\n"
        + "_" * 6
        + " ERROR collecting tests/unit/test_services.py "
        + "_" * 6
        + "\n"
        + "E   SyntaxError: invalid syntax\n"
        + "Interrupted: 1 error during collection\n"
        + "=" * 10
        + " 1 error in 0.50s "
        + "=" * 10
        + "\n",
        2,
        (S101_REQ,),
        (),
        False,
    ),
    (
        "s101-guard-not-run",
        _pyl([], [(S101_REQ, S101_RAISE)], "1 failed in 1.20s"),
        1,
        (S101_REQ,),
        (S101_GUARD,),
        False,
    ),
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
        for name, text, code, required, runner, allowed, targets, want_pass in SELFTEST_S99:
            receipt = pathlib.Path(tmp) / f"{name}.txt"
            receipt.write_text(text, encoding="utf-8")
            if code is not None:
                receipt.with_name(receipt.name + ".exit").write_text(str(code), encoding="utf-8")
            problems = run([receipt], list(required), runner, allowed, targets)
            passed = not problems
            reason = "" if passed else f" -- {problems[0].split(': ', 1)[-1][:110]}"
            print(
                f"{name}: {'pass' if passed else 'refused'} (expected "
                f"{'pass' if want_pass else 'refused'}){reason}"
            )
            if passed != want_pass:
                failures.append(name)
        for name, text, code, required, allowed, want_pass in SELFTEST_S101:
            receipt = pathlib.Path(tmp) / f"{name}.txt"
            receipt.write_text(text, encoding="utf-8")
            if code is not None:
                receipt.with_name(receipt.name + ".exit").write_text(str(code), encoding="utf-8")
            problems = run([receipt], list(required), "pytest", allowed)
            passed = not problems
            reason = "" if passed else f" -- {problems[0].split(': ', 1)[-1][:110]}"
            print(
                f"{name}: {'pass' if passed else 'refused'} (expected "
                f"{'pass' if want_pass else 'refused'}){reason}"
            )
            if passed != want_pass:
                failures.append(name)
        draft = pathlib.Path(tmp) / "draft.json"
        draft.write_text(
            json.dumps(
                {
                    "pages": {
                        "a": {"steps": [{"target": None}, {"target": "url-input"}]},
                        "b": {"steps": [{"target": "add-btn"}, {"target": "url-input"}]},
                    }
                }
            ),
            encoding="utf-8",
        )
        if load_targets(draft) != ("add-btn", "url-input"):
            failures.append("load_targets")
        print(f"load_targets: {load_targets(draft)}")
    total = len(SELFTEST) + len(SELFTEST_S99) + len(SELFTEST_S101)
    positive = (
        sum(1 for f in SELFTEST if f[4])
        + sum(1 for f in SELFTEST_S99 if f[7])
        + sum(1 for f in SELFTEST_S101 if f[5])
    )
    print(
        f"red-check selftest: {total} fixture(s) ({positive} positive, "
        f"{total - positive} negative), "
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
    allowed: list[str] = []
    runner: str | None = None
    targets: tuple[str, ...] = ()
    paths: list[pathlib.Path] = []
    bad = False
    it = iter(argv)
    for arg in it:
        if arg == "--require":
            required.append(next(it, ""))
        elif arg == "--allow-pass":
            allowed.append(next(it, ""))
        elif arg == "--runner":
            runner = next(it, "")
            bad = bad or runner not in RUNNERS
        elif arg == "--refuse-target-failure":
            targets = load_targets(pathlib.Path(next(it, "")))
            print(f"step targets ({len(targets)}): {', '.join(targets)}")
        else:
            paths.append(pathlib.Path(arg))
    if bad or not paths or "" in required or "" in allowed:
        print(
            "usage: red-check.py [--runner pytest|vitest|playwright] [--require TITLE ...] "
            "[--allow-pass TITLE ...] [--refuse-target-failure JSON] RECEIPT [RECEIPT ...] "
            "| --selftest"
        )
        return 2
    problems = run(paths, required, runner, allowed, targets)
    for p in problems:
        print("RED-CHECK:", p)
    print(
        f"red-check: {len(paths)} receipt(s), runner {runner or 'any'}, {len(required)} "
        f"required test(s), {len(allowed)} allowed pass(es), {len(targets)} step target(s), "
        f"{len(problems)} problem(s)"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
