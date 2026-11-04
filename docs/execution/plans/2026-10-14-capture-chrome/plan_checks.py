"""Plan-local verifier for 2026-10-14-capture-chrome (GUARDRAILS SIGN 1, verification-principles V4).

Stdlib only (PyYAML is imported lazily by the SSOT subcommands, which run under ``uv run``). It reads
plan, repo and receipt files and writes nothing; the caller redirects its output into a receipt. It runs
no product code. ``validate-task.ps1`` runs the tools; this file evaluates their outputs.

Every completion predicate is a pure evaluator (``eval_*``) that takes parsed inputs and returns a list of
errors; the ``cmd_*`` wrappers load the files and print the verdict. ``selftest`` feeds the evaluators
synthetic inputs and requires each refusal the plan names (§Verification Plan 0) to refuse, and each
well-formed input to pass.

``CASE_EVIDENCE`` (plan §Verification Plan 3–6): Red, Green and the gate read named cases from the raw
reports, never counts. ``AC_CASES`` names each AC's runner, file and Red class; ``ASSERTION_FAILURE`` decides
what a Red failure is; ``SETUP_SENTINEL`` proves each new loading file mounts; ``TA_TAGS`` scope the amended
tests to the task row that applies them; ``BASELINE_RED`` is the only failure every run tolerates and
``FIXTURE_RED`` the only extra one row 3's Red tolerates.

``static`` (planning time, read-only) checks:

1. ``task.md`` table structure: unique row ids; ``Depends on`` names existing rows, acyclic;
   ``context_strategy`` in {shared, compact_continue, isolated}; non-shared rows name a durable output;
   ``builder_model`` in the allowed classes.
2. Every ``-Check <name>`` that ``task.md`` or the plan names is a case in the script, and every
   ``PlanCheck '<sub>'`` the script calls is a subcommand here.
3. ``GATE``'s stage order in the plan equals the ``.ps1`` ``$stages`` ids.
4. ``COUNT_FLOORS``, ``AUDIT_SRC`` (and its pattern), the frozen paths, ``ADMIN_PATHS``, ``IDENTITY_EXCLUDE``,
   ``BASELINE_RED``, ``FIXTURE_RED``, ``SETUP_SENTINEL``, ``RETIRED_TESTIDS`` and ``NEW_TESTIDS`` equal their
   executable copies here and in the ``.ps1``.
5. ``AC_CASES`` covers exactly the plan's unit and integration AC rows (AC-80.12 is the probe), each with the
   runner its type implies, the file §NEW files names, and the red-import and guard classes the plan names.
6. ``TA_FILE`` equals the TEST_AMENDMENTS file column; the deleting rows are exactly ``TA_DELETED``; every
   other TA is applied by exactly one of rows 3 and 6 (``TA_ROW``), except ``TA_LATE``, which H1-3 applies (A-9).
7. Every ``D-n``, ``TA-n`` and ``AC-8x.n`` that ``task.md`` or the plan names has a definition site; every AC
   falls inside a range, or is named singly, in a task row; TEST_AMENDMENTS is contiguous (TA-1…TA-28) and
   every TA is cited by a task row.

Usage::

    python plan_checks.py static
    python plan_checks.py selftest
    python plan_checks.py <subcommand> --help
"""

from __future__ import annotations

import argparse
import copy
import datetime
import hashlib
import json
import os
import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path

PLAN_DIR = Path(__file__).resolve().parent
REPO = PLAN_DIR.parents[3]
PLAN_REL = "docs/execution/plans/2026-10-14-capture-chrome"
GROUPING = ".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md"
KNOWN_ISSUES = ".agent/context/known-issues.yaml"
REGISTRY = "ui/tests/e2e/test-ids.ts"
REGISTRY_MARKER = "// MEU-51 primitive harness IDs."
MEU67_MARKER = "// MEU-67 Capture flatten and revert (additive IDs)."
NEW_MARKER = "// MEU-80/81 icon hints and the Capture action row (additive IDs)."
OLD_PREFIX_HASH = "819760B9840EE4BF38633B3628DC2E7820D4B87E05A0EC720B75B61C89D28A73"
FIXTURE = "ui/tests/unit/fixtures/queue-slot-baseline.json"
HANDOFFS = {
    "80": ".agent/context/handoffs/2026-10-14-capture-chrome-MEU-80-handoff.md",
    "81": ".agent/context/handoffs/2026-10-14-capture-chrome-MEU-81-handoff.md",
}

ALLOWED_STRATEGIES = {"shared", "compact_continue", "isolated"}
ALLOWED_BUILDERS = {"`avkit_builder`", "`avkit_coordinator`", "`avkit_verifier`", "—"}

COUNT_FLOORS = {"vitest_total": 773, "e2e_expected": 133, "pytest_passed": 655}
FROZEN = ["ui/src/main/", "ui/src/preload/", "packages/", "mcp-server/", "tools/", "native/"]
# D-39 (Mat, 2026-10-15, "Fix the validator"): the one frozen file this plan may change, and only while it is a
# Files Modified row. The plan's PRODUCT_SCOPE row names the same exception.
FROZEN_EXCEPT = ["tools/validate_closeout_artifacts.py"]
# Administrative files the rows may change (PRODUCT_SCOPE); the plan's ADMIN_PATHS row lists the same, in order.
ADMIN_FILES = [
    "docs/build-plan/09-screenshot-capture.md", "docs/build-plan/11-page-layout.md",
    "docs/build-plan/build-priority-matrix.md", "docs/BUILD_PLAN.md", ".agent/context/meu-registry.md",
    ".agent/context/meu-status.yaml", GROUPING, ".agent/context/current-focus.md", KNOWN_ISSUES,
    ".agent/context/known-issues.md", "docs/execution/metrics.md",
]
ADMIN_PREFIXES = [".agent/context/handoffs/2026-10-14-capture-chrome-", "docs/execution/reflections/2026-10-14-capture-chrome-"]
# IDENTITY_SCOPE: every git-visible file except these (plan-folder files, then repo prefixes).
IDENTITY_EXCLUDE_FILES = ["walkthrough.md", "gate-result.json", "task.md"]
IDENTITY_EXCLUDE_PREFIXES = [".agent/context/handoffs/", "docs/execution/reflections/"]
# What may be dirty when row 0 takes the baseline and when the probe runs: this plan's own files.
CLEAN_EXCLUDE = (f"{PLAN_REL}/", ADMIN_PREFIXES[0])
AUDIT_SRC = [
    "ui/src/renderer/src/components/ui/Tooltip.tsx",
    "ui/src/renderer/src/features/capture/ToolbarIconButton.tsx",
    "ui/src/renderer/src/features/capture/CaptureViewport.tsx",
    "ui/src/renderer/src/features/capture/CapturePage.tsx",
    "ui/src/renderer/src/features/capture/capture-toolbar.ts",
    "ui/src/renderer/src/components/layout/ConsolePanel.tsx",
    "ui/src/renderer/src/components/queue/BulkResultToast.tsx",
    "ui/src/renderer/src/components/queue/QueueCard.tsx",
    "ui/src/renderer/src/components/queue/QueueCardMenu.tsx",
    "ui/src/renderer/src/features/transcript/TranscriptPage.tsx",
    "ui/src/renderer/src/features/converter/ConvertPage.tsx",
]
AUDIT_PATTERN = r"TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b"
RETIRED_TESTIDS = [
    "CAPTURE_COLOR_SAMPLE", "CAPTURE_NUDGE_BODY", "CAPTURE_NUDGE_TAIL", "CAPTURE_NUDGE_HEAD",
    "CAPTURE_NUDGE_LEFT", "CAPTURE_NUDGE_RIGHT", "CAPTURE_NUDGE_UP", "CAPTURE_NUDGE_DOWN",
]
NEW_TESTIDS = {
    "CAPTURE_HEADER": "capture-header",
    "CAPTURE_ACTIONS_SEPARATOR": "capture-actions-separator",
    "CAPTURE_REMOVE_MARK_TIP": "capture-remove-mark-tip",
    "CAPTURE_TOOL_ARROW_HINT": "capture-tool-arrow-hint",
    "CAPTURE_UNDO_TIP": "capture-undo-tip",
    "CAPTURE_UNDO_HINT": "capture-undo-hint",
    "CAPTURE_APPLY_IMAGE_TIP": "capture-apply-image-tip",
    "CAPTURE_APPLY_IMAGE_HINT": "capture-apply-image-hint",
    "CAPTURE_DELETE_TIP": "capture-delete-tip",
    "CONSOLE_CLOSE_HINT": "console-close-hint",
}
ISSUES = [
    "CAPTURE-TOOLTIPS-NOT-SHOWN", "CAPTURE-ACTION-ROW-ICONS", "CAPTURE-MARKS-ROW-SQUEEZED",
    "CAPTURE-SAMPLE-ORIGINAL-UNLABELED", "CAPTURE-HOTKEY-BANNER-GAP",
]
REVIEW_AGENT = "codex-cli-gpt-6.1-sol"
# The trailing \b sits on the word-ending alternatives only: after "fixture (a)" a \b would need a word
# character right after the ")", so that disposition never matched (Session 34 row 1).
CENSUS_DISPOSITION = re.compile(r"\b(TA-\d+\b|fixture \(a\)|unaffected\b|new-contradiction\b)")

# --- CASE_EVIDENCE -----------------------------------------------------------------------------------------


def _cases(meu: str, runner: str, file: str, cls: str, nums: tuple[int, ...]) -> dict[str, tuple[str, str, str, str]]:
    return {f"AC-{meu}.{n}": (runner, file, cls, meu) for n in nums}


# AC id -> (runner, test file basename, Red class, MEU).
AC_CASES = {
    **_cases("80", "vitest", "tooltip.test.tsx", "red-import", (1, 2, 3, 4, 5, 6, 7, 13)),
    **_cases("80", "vitest", "icon-hints.test.ts", "red", (8, 9)),
    **_cases("80", "e2e", "capture-inbox.test.ts", "red", (10,)),
    **_cases("80", "e2e", "console-chrome.test.ts", "red", (11,)),
    **_cases("81", "vitest", "capture-action-row.test.ts", "red", (1, 2, 4, 6, 8, 10, 12, 13)),
    **_cases("81", "vitest", "capture-action-row.test.ts", "guard", (3, 5, 7, 15)),
    **_cases("81", "e2e", "capture-inbox.test.ts", "red", (9, 11, 14)),
}
AC_MAX = {"80": 13, "81": 15}
RED_IMPORT_MODULE = "components/ui/Tooltip"
IMPORT_ERRORS = ("Failed to resolve import", "Cannot find module", "Failed to load url")
SENTINEL_TITLE = "setup sentinel"
SENTINEL_FILES = {"80": ["icon-hints.test.ts"], "81": ["capture-action-row.test.ts"]}
VITEST_ASSERT = ("AssertionError", "Error: expect(", "TestingLibraryElementError")
E2E_NOT_ASSERT = ("TypeError", "ReferenceError", "SyntaxError")
SKIPPED = {"skipped", "pending", "todo", "disabled"}
# TEST_AMENDMENTS: the file each row changes, the rows that delete, and the task row (by MEU) that applies each.
TA_FILE = {
    **{n: "capture-page.behavior.test.ts" for n in range(1, 16)},
    16: "capture-help-content.test.ts", 17: "capture-sample.test.ts",
    **{n: "capture-inbox.test.ts" for n in range(18, 25)},
    25: "queue-card.test.ts", 26: "layout-primitives.test.ts",
    27: "download-queue.test.ts", 28: "convert-queue.test.ts",
}
TA_DELETED = {4, 17}
TA_ROW = {"80": {8, 11, 12, 14, 15, 22, 23, 24, 25}, "81": {1, 2, 3, 5, 6, 7, 9, 10, 13, 16, 18, 19, 20, 21, 26}}
# A-9 (Mat, 2026-10-15, option 1; D-37): TA-27 and TA-28 came after rows 3 and 6, from the H1-3 GATE. H1-3 applies
# them, and only gate-check reads their tags, because no row's targeted run covers those two Electron files.
TA_LATE = {27, 28}
E2E_FILES = {"capture-inbox.test.ts", "console-chrome.test.ts"}
BASELINE_RED = ("queue-canon.test.ts", "AC-41.3", "--color-accent-cyan light diverges from PILL_TOKEN_SOURCE")
# FIXTURE_REPAIRS (a) changes the fixture before QueueCard.tsx changes, so its one consumer case fails at row 3's Red.
FIXTURE_RED = ("queue-card-slots.test.tsx", "AC-55.1 a card with no slot renders the exact pre-change markup", "80")
UNHANDLED = re.compile(r"Unhandled (?:Errors?|Rejection)|^\s*Errors\s+\d+ errors?\s*$", re.M)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PROBE_TARGETS = ("nav-capture", "capture-tool-arrow")
PNG_SIG = b"\x89PNG\r\n\x1a\n"
#: PROBE_RUN producer binding (D-31): the files whose current bytes the record's hashes must equal, the
#: receipt line the probe prints last, and the longest plausible run.
PROBE_BUILD = "ui/out/main/index.js"
PROBE_SCRIPT = f"{PLAN_REL}/tooltip-probe.mjs"
PROBE_RECEIPT = "s34-probe-run.txt"
PROBE_DONE = "PROBE-DONE"
PROBE_MAX_SECONDS = 15 * 60
PROBE_MTIME_SLACK = 2.0
HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


def meus_for(meu: str | None) -> list[str]:
    """The MEUs whose cases a run must hold: MEU-81's runs also carry MEU-80's."""
    return [] if not meu else ["80"] if meu == "80" else ["80", "81"]


def fail(msg: str) -> None:
    """Print a refusal and exit 1."""
    print(f"FAIL: {msg}")
    sys.exit(1)


def report(errors: list[str], ok: str) -> None:
    """Print every error and exit 1, or print the PASS line."""
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        sys.exit(1)
    print(f"PASS {ok}")


def read(rel: str | Path) -> str:
    """Read a repo-relative (or absolute) text file as UTF-8."""
    return (REPO / rel).read_text(encoding="utf-8")


def git(*args: str) -> str:
    """Run git in the repo root and return stdout (raises on a nonzero exit)."""
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True,
                          encoding="utf-8").stdout


def git_bytes(*args: str) -> bytes:
    """Run git and return raw stdout bytes."""
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, check=True).stdout


def section(text: str, heading: str) -> str:
    """Body of the ``## heading`` section (up to the next ``## ``), or '' when absent."""
    parts = re.split(rf"^## {re.escape(heading)}[ \t]*$", text, maxsplit=1, flags=re.M)
    return parts[1].split("\n## ", 1)[0] if len(parts) == 2 else ""


def ac_in(ac: str, text: str) -> bool:
    """True when ``text`` names ``ac`` exactly (``AC-81.6`` never matches ``AC-81.60``)."""
    return re.search(rf"(?<![\w.]){re.escape(ac)}(?!\d)", text) is not None


def tag_ids(title: str) -> set[int]:
    return {int(n) for n in re.findall(r"\[TA-(\d+)\]", title)}


def basename(path: str) -> str:
    return path.replace("\\", "/").rsplit("/", 1)[-1]


# ---------------------------------------------------------------------------------------------------------
# static
# ---------------------------------------------------------------------------------------------------------

def task_rows(task: str) -> list[list[str]]:
    """The 10-column task-table rows (id first), skipping dividers and the header."""
    rows = []
    for line in task.splitlines():
        if not line.startswith("| ") or line.startswith("| #") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 10 and cells[0]:
            rows.append(cells)
    return rows


def check_task(task: str) -> list[str]:
    """Structural checks over the task table."""
    errors: list[str] = []
    rows = task_rows(task)
    ids = [r[0] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate row ids: {ids}")
    deps: dict[str, list[str]] = {}
    for r in rows:
        rid, dep, strategy, durable, builder = r[0], r[5], r[6], r[7], r[8]
        deps[rid] = [] if dep in ("—", "-", "") else [d.strip() for d in dep.split(",")]
        errors += [f"row {rid}: depends on unknown row {d!r}" for d in deps[rid] if d not in ids]
        if strategy not in ALLOWED_STRATEGIES:
            errors.append(f"row {rid}: context_strategy {strategy!r}")
        if strategy != "shared" and not durable:
            errors.append(f"row {rid}: non-shared row without durable output")
        if builder not in ALLOWED_BUILDERS:
            errors.append(f"row {rid}: builder_model {builder!r}")
    state: dict[str, int] = {}

    def visit(node: str, path: list[str]) -> None:
        if state.get(node) == 1:
            errors.append(f"dependency cycle: {' -> '.join(path + [node])}")
            return
        if state.get(node) == 2:
            return
        state[node] = 1
        for nxt in deps.get(node, []):
            visit(nxt, path + [node])
        state[node] = 2

    for rid in ids:
        visit(rid, [])
    return errors


def contract_row(plan: str, name: str) -> str:
    """The Definition cell of a §Single-statement contracts row."""
    m = re.search(rf"^\| `{re.escape(name)}` \| (.*?) \| [^|]*\|$", plan, re.M)
    return m.group(1) if m else ""


def ps1_stage_ids(ps1: str) -> list[str]:
    """The ``$stages`` ids of the gate, in order."""
    return re.findall(r"^\s*@\('([a-z0-9-]+)',\s", ps1, re.M)


def expand_acs(text: str) -> list[str]:
    """``AC-80.1–80.7, AC-80.13`` -> the dotted ids, ranges expanded."""
    out = []
    for meu, a, b in re.findall(r"AC-(8[01])\.(\d+)(?:[–-](?:8[01]\.)?(\d+))?", text):
        out += [f"AC-{meu}.{n}" for n in range(int(a), int(b or a) + 1)]
    return out


def cited_tas(text: str) -> set[int]:
    """TA numbers a text cites, ``TA-a–TA-b`` ranges expanded."""
    cited: set[int] = set()
    for a, b in re.findall(r"TA-(\d+)[–-]TA-(\d+)", text):
        cited |= set(range(int(a), int(b) + 1))
    return cited | {int(n) for n in re.findall(r"TA-(\d+)", text)}


def check_scripts(task: str, plan: str, ps1: str, choices: list[str]) -> list[str]:
    """Cross-file checks between task.md, the plan, the .ps1 and this file's constants."""
    errors: list[str] = []
    labels = set(re.findall(r"^    '([a-z0-9-]+)' \{$", ps1, re.M))
    for src_name, text in (("task.md", task), ("implementation-plan.md", plan)):
        for check in sorted(set(re.findall(r"-Check ([a-z0-9-]+)", text))):
            if check not in labels:
                errors.append(f"{src_name} names -Check {check!r}, which validate-task.ps1 does not implement")
    for sub in sorted(set(re.findall(r"PlanCheck '([a-z0-9-]+)'", ps1))):
        if sub not in choices:
            errors.append(f"validate-task.ps1 calls PlanCheck {sub!r}, not a plan_checks.py subcommand")
    gate = contract_row(plan, "GATE")
    om = re.search(r"in this order: (.*?)\.<br>", gate)
    plan_order = re.findall(r"`([a-z0-9-]+)`", om.group(1)) if om else []
    if not plan_order or plan_order != ps1_stage_ids(ps1):
        errors.append(f"GATE stage order differs: plan={plan_order} ps1={ps1_stage_ids(ps1)}")
    if "s34-gate.v2" not in gate or "'s34-gate.v2'" not in ps1:
        errors.append("GATE schema is not s34-gate.v2 in both the plan and the .ps1")
    fm = re.search(r"Vitest total ≥ (\d+) and Electron expected ≥ (\d+)", plan)
    fp = re.search(r"pytest failed 0 and passed ≥ (\d+)", plan)
    plan_floors = {"vitest_total": int(fm.group(1)), "e2e_expected": int(fm.group(2)),
                   "pytest_passed": int(fp.group(1))} if fm and fp else {}
    if plan_floors != COUNT_FLOORS:
        errors.append(f"COUNT_FLOORS differ: plan={plan_floors} constant={COUNT_FLOORS}")
    audit = contract_row(plan, "AUDIT_SRC")
    plan_src = re.findall(r"`(ui/[^`]+\.tsx?)`", audit)
    pm = re.search(r"Pattern: `(.*)`\.", audit)
    plan_pat = pm.group(1).replace(r"\|", "|") if pm else ""
    psm = re.search(r"\$auditSrc = @\((.*?)\)", ps1, re.S)
    ps_src = re.findall(r"'([^']+\.tsx?)'", psm.group(1)) if psm else []
    ppm = re.search(r"^\s*\$auditPattern = '(.*)'$", ps1, re.M)
    if not (plan_src == AUDIT_SRC == ps_src):
        errors.append(f"AUDIT_SRC differs: plan={plan_src} ps1={ps_src}")
    if not (plan_pat == AUDIT_PATTERN == (ppm and ppm.group(1))):
        errors.append(f"audit pattern differs: plan={plan_pat!r} ps1={ppm and ppm.group(1)!r} constant={AUDIT_PATTERN!r}")
    scope = contract_row(plan, "PRODUCT_SCOPE")
    sm = re.search(r"Files Modified rows below\. (.*?) stay byte-identical", scope)
    plan_frozen = re.findall(r"`([^`]+/)`", sm.group(1)) if sm else []
    if plan_frozen != FROZEN:
        errors.append(f"frozen paths differ: plan={plan_frozen} constant={FROZEN}")
    plan_except = re.findall(r"except `([^`]+)`", sm.group(1)) if sm else []
    if plan_except != FROZEN_EXCEPT:
        errors.append(f"frozen exceptions differ: plan={plan_except} constant={FROZEN_EXCEPT}")
    if not set(FROZEN_EXCEPT) <= files_modified(plan):
        errors.append(f"frozen exceptions not in Files Modified: {sorted(set(FROZEN_EXCEPT) - files_modified(plan))}")
    admin = [p for p in re.findall(r"`([^`]+)`", contract_row(plan, "ADMIN_PATHS")) if "/" in p]
    if admin != ADMIN_FILES + ADMIN_PREFIXES:
        errors.append(f"ADMIN_PATHS differ: plan={admin} constant={ADMIN_FILES + ADMIN_PREFIXES}")
    im = re.search(r"except `IDENTITY_EXCLUDE`:(.*?)\. That covers", contract_row(plan, "IDENTITY_SCOPE"))
    excl = re.findall(r"`([^`]+)`", im.group(1)) if im else []
    if excl != IDENTITY_EXCLUDE_FILES + IDENTITY_EXCLUDE_PREFIXES:
        errors.append(f"IDENTITY_EXCLUDE differs: plan={excl}")
    br = contract_row(plan, "BASELINE_RED")
    if not all(f"`{s}`" in br or f" {s}," in br for s in BASELINE_RED):
        errors.append("BASELINE_RED's file, AC id or message differs from the plan row")
    if f"`{FIXTURE_RED[0]}` `{FIXTURE_RED[1]}`" not in plan or "`FIXTURE_RED`" not in plan:
        errors.append("FIXTURE_RED (file and case title) is not named in the plan")
    sentinel = re.findall(r"`([\w.-]+\.test\.tsx?)`", contract_row(plan, "SETUP_SENTINEL"))
    if sentinel != SENTINEL_FILES["80"] + SENTINEL_FILES["81"]:
        errors.append(f"SETUP_SENTINEL files differ: plan={sentinel}")
    retired_row = contract_row(plan, "RETIRED_TESTIDS")
    retired: list[str] = []
    for tok in re.findall(r"`(_?[A-Z][A-Z_]*)`", retired_row):
        retired.append("CAPTURE_NUDGE" + tok if tok.startswith("_") else tok)
    if retired != RETIRED_TESTIDS:
        errors.append(f"RETIRED_TESTIDS differ: plan={retired} constant={RETIRED_TESTIDS}")
    new_row = contract_row(plan, "NEW_TESTIDS")
    new = dict(re.findall(r"`([A-Z_]+) = '([a-z-]+)'`", new_row))
    if new != NEW_TESTIDS or NEW_MARKER not in new_row:
        errors.append(f"NEW_TESTIDS differ (or the block comment): plan={new}")
    return errors


def check_cases(task: str, plan: str) -> list[str]:
    """AC_CASES against the AC tables and §NEW files; TA_FILE, TA_DELETED and TA_ROW against the plan and rows."""
    errors: list[str] = []
    rows = {(m.group(1)): m.group(2) for m in re.finditer(r"^\| (AC-8[01]\.\d+) \| (unit|integration) \|", plan, re.M)}
    rows.pop("AC-80.12", None)
    if set(rows) != set(AC_CASES):
        errors.append(f"AC_CASES differ from the AC rows: missing {sorted(set(rows) - set(AC_CASES))}, "
                      f"extra {sorted(set(AC_CASES) - set(rows))}")
    for ac, kind in rows.items():
        want = "vitest" if kind == "unit" else "e2e"
        if ac in AC_CASES and AC_CASES[ac][0] != want:
            errors.append(f"{ac} is {kind} in the plan but runs under {AC_CASES[ac][0]}")
    new = plan.split("### NEW Vitest and Electron files", 1)[-1].split("\n### ", 1)[0]
    named: dict[str, str] = {}
    for f, acs in re.findall(r"`ui/tests/(?:unit|e2e)/([^`]+)` \(([^)]*)\)", new):
        for ac in expand_acs(acs):
            named[ac] = f
    for ac, (_runner, f, _cls, _meu) in AC_CASES.items():
        if named.get(ac) != f:
            errors.append(f"{ac}: AC_CASES file {f}, §NEW files names {named.get(ac)}")
    row = contract_row(plan, "AC_CASES")
    imports = sorted({c[1] for c in AC_CASES.values() if c[2] == "red-import"})
    if imports != ["tooltip.test.tsx"] or f"(only `tooltip.test.tsx`, on `{RED_IMPORT_MODULE}`)" not in row:
        errors.append(f"red-import files {imports} differ from the AC_CASES row")
    gm = re.search(r"The `guard` cases are (.*?);", row)
    guards = sorted(ac for ac, c in AC_CASES.items() if c[2] == "guard")
    if not gm or sorted(expand_acs(gm.group(1))) != guards:
        errors.append(f"guard cases {guards} differ from the AC_CASES row ({gm and gm.group(1)})")
    plan_files: dict[int, str] = {}
    deleting: set[int] = set()
    for line in plan.splitlines():
        m = re.match(r"^\| TA-(\d+) \| `(?:unit|e2e)/([^`:]+)", line)
        if m:
            n = int(m.group(1))
            plan_files[n] = m.group(2)
            cells = re.split(r"(?<!\\)\|", line)
            if "deleted" in cells[4]:
                deleting.add(n)
    if plan_files != TA_FILE:
        errors.append(f"TA_FILE differs from the TEST_AMENDMENTS file column: "
                      f"{sorted(n for n in set(plan_files) | set(TA_FILE) if plan_files.get(n) != TA_FILE.get(n))}")
    if deleting != TA_DELETED:
        errors.append(f"deleting TA rows {sorted(deleting)} differ from TA_DELETED {sorted(TA_DELETED)}")
    by_id = {r[0]: "|".join(r) for r in task_rows(task)}
    row3, row6 = cited_tas(by_id.get("3", "")), cited_tas(by_id.get("6", ""))
    if row3 != TA_ROW["80"]:
        errors.append(f"row 3 applies {sorted(row3)}, TA_ROW['80'] is {sorted(TA_ROW['80'])}")
    if row6 != TA_ROW["81"] | TA_DELETED:
        errors.append(f"row 6 applies {sorted(row6)}, TA_ROW['81'] plus the deletions is "
                      f"{sorted(TA_ROW['81'] | TA_DELETED)}")
    if TA_ROW["80"] & TA_ROW["81"] or TA_ROW["80"] | TA_ROW["81"] | TA_DELETED != set(range(1, 27)):
        errors.append("TA_ROW does not split TA-1..TA-26 (minus the deletions) between rows 3 and 6")
    late = cited_tas(by_id.get("H1-3", ""))
    if late != TA_LATE or TA_LATE & (row3 | row6) or TA_LATE != set(range(27, len(TA_FILE) + 1)):
        errors.append(f"row H1-3 applies {sorted(late)}, TA_LATE is {sorted(TA_LATE)} (A-9)")
    return errors


def check_refs(task: str, plan: str) -> list[str]:
    """Definition sites, AC coverage and TA contiguity/citation."""
    errors: list[str] = []
    grouping = read(GROUPING) if (REPO / GROUPING).exists() else ""
    issues = read(KNOWN_ISSUES) if (REPO / KNOWN_ISSUES).exists() else ""
    refs = set(re.findall(r"\b(D-\d+|TA-\d+|AC-8[01]\.\d+)\b", task))
    refs |= set(re.findall(r"\b(D-\d+)\b", plan))
    for ref in sorted(refs):
        if ref.startswith(("AC-", "TA-")):
            defined = re.search(rf"^\| {re.escape(ref)} \|", plan, re.M) is not None
        else:
            defined = (re.search(rf"^\s*- id: {re.escape(ref)}$", plan, re.M) is not None
                       or re.search(rf"^\| {re.escape(ref)} \|", grouping, re.M) is not None
                       or re.search(rf"^\s*- id: {re.escape(ref)}$", issues, re.M) is not None)
        if not defined:
            errors.append(f"{ref} has no definition site (AC/TA table row, decision_log id, grouping §8 row, "
                          "or known-issues decision id)")
    rows_text = "\n".join("|".join(r) for r in task_rows(task))
    for meu in ("80", "81"):
        table = {int(n) for n in re.findall(rf"^\| AC-{meu}\.(\d+) \|", plan, re.M)}
        covered: set[int] = set()
        for a, b in re.findall(rf"AC-{meu}\.(\d+)[–-](?:{meu}\.)?(\d+)", rows_text):
            covered |= set(range(int(a), int(b) + 1))
        covered |= {int(n) for n in re.findall(rf"AC-{meu}\.(\d+)(?![–\d-])", rows_text)}
        if not table or table - covered or max(table) != AC_MAX[meu]:
            errors.append(f"MEU-{meu} ACs not covered by any task row: {sorted(table - covered)}")
    tas = [int(n) for n in re.findall(r"^\| TA-(\d+) \|", plan, re.M)]
    if tas != list(range(1, len(tas) + 1)) or len(tas) != len(TA_FILE):
        errors.append(f"TEST_AMENDMENTS not contiguous TA-1..TA-{len(TA_FILE)}: {tas}")
    cited = cited_tas(rows_text)
    if set(tas) - cited:
        errors.append(f"TA rows cited by no task row: {sorted(set(tas) - cited)}")
    return errors


def cmd_static(args: argparse.Namespace, choices: list[str]) -> None:
    task = read(f"{PLAN_REL}/task.md")
    plan = read(f"{PLAN_REL}/implementation-plan.md")
    ps1 = read(f"{PLAN_REL}/validate-task.ps1")
    errors = check_task(task) + check_scripts(task, plan, ps1, choices) + check_cases(task, plan) + check_refs(task, plan)
    report(errors, f"static: {len(task_rows(task))} task rows; {len(ps1_stage_ids(ps1))} GATE stages; "
                   f"{len(AC_CASES)} AC_CASES; scripts, constants and cross-references agree")


# ---------------------------------------------------------------------------------------------------------
# identity, clean, registry, fixture, scope
# ---------------------------------------------------------------------------------------------------------

def identity_excluded(path: str) -> bool:
    return (path in {f"{PLAN_REL}/{f}" for f in IDENTITY_EXCLUDE_FILES}
            or path.startswith(tuple(IDENTITY_EXCLUDE_PREFIXES)))


def identity() -> str:
    """SHA-256 over the sorted (path, sha256) pairs of every git-visible file outside IDENTITY_EXCLUDE."""
    out = git_bytes("ls-files", "-co", "--exclude-standard", "-z")
    paths = sorted({p.decode("utf-8") for p in out.split(b"\0") if p})
    h = hashlib.sha256()
    for p in paths:
        f = REPO / p
        if f.is_file() and not identity_excluded(p):
            h.update(f"{p}\0{hashlib.sha256(f.read_bytes()).hexdigest()}\n".encode("utf-8"))
    return h.hexdigest().upper()


def cmd_identity(args: argparse.Namespace) -> None:
    print(identity())


def porcelain_paths(text: str) -> list[str]:
    """Paths of ``git status --porcelain`` lines (the target of a rename)."""
    return [ln[3:].split(" -> ")[-1].strip('"') for ln in text.splitlines() if len(ln) > 3]


def eval_clean(paths: list[str]) -> list[str]:
    dirty = [p for p in paths if not p.startswith(CLEAN_EXCLUDE)]
    return [f"changed outside this plan's own files: {dirty[:10]}"] if dirty else []


def cmd_clean(args: argparse.Namespace) -> None:
    paths = porcelain_paths(git("status", "--porcelain", "--untracked-files=all"))
    report(eval_clean(paths), f"clean: nothing changed outside {', '.join(CLEAN_EXCLUDE)}")


def cmd_registry(args: argparse.Namespace) -> None:
    base = git_bytes("show", f"{args.baseline}:{REGISTRY}").decode("utf-8").replace("\r\n", "\n")
    if REGISTRY_MARKER not in base:
        fail("baseline registry has no MEU-51 marker")
    base_prefix = base.split(REGISTRY_MARKER)[0]
    selftest = hashlib.sha256(base_prefix.replace("\n", "\r\n").encode("utf-8")).hexdigest().upper()
    if selftest != OLD_PREFIX_HASH:
        fail(f"self-test: the baseline prefix (CRLF) hashes to {selftest}, not the AC-51.6 pin")
    raw = (REPO / REGISTRY).read_bytes()
    if REGISTRY_MARKER.encode() not in raw:
        fail("registry has no MEU-51 marker")
    new_prefix_raw = raw.split(REGISTRY_MARKER.encode())[0]
    new_prefix = new_prefix_raw.decode("utf-8").replace("\r\n", "\n")
    retired = re.compile(rf"^export const ({'|'.join(RETIRED_TESTIDS)}) = '[^']+'$")
    kept = [ln for ln in base_prefix.split("\n") if not retired.match(ln)]
    removed = len(base_prefix.split("\n")) - len(kept)
    if removed != len(RETIRED_TESTIDS):
        fail(f"baseline prefix holds {removed} retired lines, expected {len(RETIRED_TESTIDS)}")
    if "\n".join(kept) != new_prefix:
        fail("the new prefix is not the baseline prefix minus exactly the RETIRED_TESTIDS lines")
    new_hash = hashlib.sha256(new_prefix_raw).hexdigest().upper()
    pins = re.findall(r"expect\(hash\)\.toBe\('([0-9A-F]{64})'\)", read("ui/tests/unit/layout-primitives.test.ts"))
    if pins != [new_hash] or new_hash == OLD_PREFIX_HASH:
        fail(f"AC-51.6 pin {pins} does not equal the new prefix hash {new_hash} (TA-26)")
    text = raw.decode("utf-8").replace("\r\n", "\n")
    if text.count(NEW_MARKER) != 1 or text.find(MEU67_MARKER) < 0 or text.find(NEW_MARKER) < text.find(MEU67_MARKER):
        fail("the NEW_TESTIDS comment is missing, duplicated, or not after the MEU-67 block")
    tail = text.split(NEW_MARKER, 1)[1]
    for name, value in NEW_TESTIDS.items():
        line = f"export const {name} = '{value}'"
        if text.count(line) != 1 or line not in tail:
            fail(f"{line} is not registered exactly once after the MEU-80/81 comment")
    for name in RETIRED_TESTIDS:
        if re.search(rf"\b{name}\b", text):
            fail(f"retired constant {name} is still in the registry")
    print(f"PASS registry: prefix lost exactly {len(RETIRED_TESTIDS)} lines; pin {new_hash[:12]}…; "
          f"{len(NEW_TESTIDS)} new ids after the MEU-67 block")


def cmd_fixture(args: argparse.Namespace) -> None:
    base = json.loads(git_bytes("show", f"{args.baseline}:{FIXTURE}").decode("utf-8"))
    new = json.loads(read(FIXTURE))
    if sorted(base) != sorted(new):
        fail(f"fixture keys changed: {sorted(base)} -> {sorted(new)}")
    for key in base:
        if key != "doneWithMenu" and base[key] != new[key]:
            fail(f"fixture key {key!r} changed (only doneWithMenu may)")
    pat = re.compile(r'<button[^>]*data-testid="queue-card-kebab"[^>]*>.*?</button>', re.S)
    src = base["doneWithMenu"]
    hits = pat.findall(src)
    if len(hits) != 1 or hits[0].count(' title="Actions for Done job"') != 1:
        fail("baseline doneWithMenu does not hold exactly one titled kebab button")
    button = hits[0].replace(' title="Actions for Done job"', "", 1)
    expected = pat.sub(lambda _m: f'<span data-testid="queue-card-kebab-tip" class="inline-flex">{button}</span>', src)
    if new["doneWithMenu"] != expected:
        fail("doneWithMenu is not exactly FIXTURE_REPAIRS (a) applied to the baseline")
    print("PASS fixture: FIXTURE_REPAIRS (a) exactly; the other three keys byte-identical")


def files_modified(plan: str) -> set[str]:
    """Every product path listed in the plan's Files Modified tables (tools/ only matters for FROZEN_EXCEPT)."""
    return set(re.findall(r"^\| `((?:ui|packages|mcp-server|tests|tools)/[^`]+)` \|", plan, re.M))


def excepted(p: str, listed: set[str]) -> bool:
    """A frozen path this plan may change: named in FROZEN_EXCEPT (D-39) and a Files Modified row."""
    return p in FROZEN_EXCEPT and p in listed


def eval_scope(changed: set[str], frozen_changed: list[str], listed: set[str]) -> list[str]:
    """PRODUCT_SCOPE: frozen paths untouched; every changed path is listed, in the plan folder, or administrative."""
    frozen_changed = [p for p in frozen_changed if not excepted(p, listed)]
    errors = [f"frozen paths changed: {frozen_changed[:10]}"] if frozen_changed else []
    unclassified = []
    for p in sorted(changed):
        if p.startswith(tuple(FROZEN)) and not excepted(p, listed):
            errors.append(f"frozen path changed: {p}")
        elif not (p in listed or p.startswith(f"{PLAN_REL}/") or p in ADMIN_FILES or p.startswith(tuple(ADMIN_PREFIXES))):
            unclassified.append(p)
    if unclassified:
        errors.append(f"changed paths outside Files Modified, the plan folder and ADMIN_PATHS: {unclassified[:10]}")
    return errors


def cmd_scope(args: argparse.Namespace) -> None:
    committed = git("diff", "--name-only", f"{args.baseline}..HEAD", "--", *FROZEN).split()
    working = porcelain_paths(git("status", "--porcelain", "--untracked-files=all", "--", *FROZEN))
    changed = set(git("diff", "--name-only", args.baseline).split())
    changed |= set(git("ls-files", "-o", "--exclude-standard").split())
    listed = files_modified(read(f"{PLAN_REL}/implementation-plan.md"))
    report(eval_scope(changed, committed + working, listed),
           f"scope: frozen paths unchanged; {len(changed)} changed paths, all listed, plan-local or administrative")


# ---------------------------------------------------------------------------------------------------------
# CASE_EVIDENCE evaluators (Vitest and Playwright JSON)
# ---------------------------------------------------------------------------------------------------------

def load_json(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as err:
        fail(f"cannot read JSON report {path}: {err}")
        raise


def load_text(path: str | None) -> str | None:
    if not path:
        return None
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def vitest_cases(j: dict) -> list[dict]:
    """Every Vitest case, in report order: file basename, title, status, failure messages (ANSI stripped)."""
    out = []
    for s in j.get("testResults", []):
        for a in s.get("assertionResults", []):
            out.append({"file": basename(s.get("name", "")), "title": a.get("title", ""),
                        "full": a.get("fullName", "") or a.get("title", ""), "status": a.get("status"),
                        "msgs": [ANSI.sub("", m) for m in a.get("failureMessages") or []]})
    return out


def vitest_suite_errors(j: dict) -> dict[str, str]:
    return {basename(s.get("name", "")): ANSI.sub("", s["message"]) for s in j.get("testResults", []) if s.get("message")}


def is_vitest_assertion(msgs: list[str]) -> bool:
    return bool(msgs) and msgs[0].lstrip().startswith(VITEST_ASSERT)


def is_baseline_red(c: dict) -> bool:
    return (c["file"] == BASELINE_RED[0] and ac_in(BASELINE_RED[1], c["full"])
            and any(BASELINE_RED[2] in m for m in c["msgs"]))


def common_vitest(j: dict, txt: str | None) -> list[str]:
    errors = []
    if txt is None:
        errors.append("the Vitest text receipt is missing (unhandled errors cannot be ruled out)")
    elif UNHANDLED.search(ANSI.sub("", txt)):
        errors.append("the Vitest text receipt reports unhandled errors")
    if j.get("numPendingTests") or j.get("numTodoTests"):
        errors.append(f"pending {j.get('numPendingTests')} / todo {j.get('numTodoTests')} tests present")
    skipped = [f"{c['file']}: {c['title'][:60]}" for c in vitest_cases(j) if c["status"] in SKIPPED]
    if skipped:
        errors.append(f"skipped cases: {skipped[:5]}")
    return errors


def find_case(cases: list[dict], file: str, ac: str) -> tuple[list[int], str | None]:
    hits = [i for i, c in enumerate(cases) if c["file"] == file and ac_in(ac, c["title"])]
    return hits, (None if len(hits) == 1 else f"{ac}: {len(hits)} cases in {file} carry it in their title (need 1)")


def check_sentinels(cases: list[dict], meus: list[str], claimed: set[int]) -> list[str]:
    errors = []
    for meu in meus:
        for f in SENTINEL_FILES[meu]:
            idx = [i for i, c in enumerate(cases) if c["file"] == f]
            if not idx or cases[idx[0]]["title"] != SENTINEL_TITLE or cases[idx[0]]["status"] != "passed":
                errors.append(f"{f}: the first case is not a passing '{SENTINEL_TITLE}' (SETUP_SENTINEL)")
            else:
                claimed.add(idx[0])
    return errors


def eval_vitest_red(j: dict, txt: str | None, rc: int, meu: str, sources: dict[str, str]) -> list[str]:
    """CASE_EVIDENCE, Red mode, for one MEU's targeted Vitest run."""
    errors = [] if rc != 0 else ["Red expected a failing run, got exit 0"]
    errors += common_vitest(j, txt)
    cases, suites = vitest_cases(j), vitest_suite_errors(j)
    mine = {ac: c for ac, c in AC_CASES.items() if c[3] == meu and c[0] == "vitest"}
    imports = {c[1] for c in mine.values() if c[2] == "red-import"}
    for f, msg in suites.items():
        if not (f in imports and RED_IMPORT_MODULE in msg and any(k in msg for k in IMPORT_ERRORS)):
            errors.append(f"suite load error in {f}: {msg[:160]}")
    errors += [f"{f} loaded at Red: its red-import module already exists" for f in sorted(imports) if f not in suites]
    claimed: set[int] = set()
    for ac, (_runner, f, cls, _meu) in mine.items():
        if cls == "red-import":
            n = len(re.findall(rf"\b(?:it|test)\(\s*['\"`][^'\"`\n]*{re.escape(ac)}(?!\d)", sources.get(f, "")))
            if n != 1:
                errors.append(f"{ac}: {n} cases carry it in their title in the {f} source (need 1)")
            continue
        hits, err = find_case(cases, f, ac)
        if err:
            errors.append(err)
            continue
        c = cases[hits[0]]
        claimed.add(hits[0])
        if c["status"] in SKIPPED:
            errors.append(f"{ac} is {c['status']}")
        elif cls == "red" and not (c["status"] == "failed" and is_vitest_assertion(c["msgs"])):
            errors.append(f"{ac} is not an assertion Red: {c['status']} {(c['msgs'] or [''])[0][:100]!r}")
        elif cls == "guard" and c["status"] == "failed" and not is_vitest_assertion(c["msgs"]):
            errors.append(f"{ac} (guard) failed by a non-assertion: {(c['msgs'] or [''])[0][:100]!r}")
    errors += check_sentinels(cases, [meu], claimed)
    for i, c in enumerate(cases):
        if i in claimed or c["status"] != "failed" or is_baseline_red(c):
            continue
        assertion = is_vitest_assertion(c["msgs"])
        tagged = any(n in TA_ROW[meu] and TA_FILE[n] == c["file"] for n in tag_ids(c["title"]))
        fixture = meu == FIXTURE_RED[2] and c["file"] == FIXTURE_RED[0] and c["title"] == FIXTURE_RED[1]
        if not ((tagged or fixture) and assertion):
            errors.append(f"untolerated Red failure (S2/S3) {c['file']}: {c['title'][:90]}")
    return errors


def eval_vitest_ok(j: dict, txt: str | None, rc: int, meu: str | None) -> list[str]:
    """CASE_EVIDENCE, Green/gate mode: the MEU's cases and applied tags passed; no failure but BASELINE_RED."""
    errors = common_vitest(j, txt)
    cases = vitest_cases(j)
    if not cases:
        errors.append("the report holds no cases")
    errors += [f"suite load error in {f}: {m[:160]}" for f, m in vitest_suite_errors(j).items()]
    meus = meus_for(meu)
    for ac, (runner, f, _cls, m) in AC_CASES.items():
        if runner != "vitest" or m not in meus:
            continue
        hits, err = find_case(cases, f, ac)
        if err:
            errors.append(err)
        elif cases[hits[0]]["status"] != "passed":
            errors.append(f"{ac} is {cases[hits[0]]['status']}")
    errors += check_sentinels(cases, meus, set())
    for m in meus:
        for n in sorted(TA_ROW[m]):
            if TA_FILE[n] in E2E_FILES:
                continue
            tagged = [c for c in cases if c["file"] == TA_FILE[n] and n in tag_ids(c["title"])]
            if not tagged or any(c["status"] != "passed" for c in tagged):
                errors.append(f"TA-{n}: {len(tagged)} tagged cases in {TA_FILE[n]}, not all passed (TA_TAGS)")
    failed = [c for c in cases if c["status"] == "failed"]
    errors += [f"failed: {c['file']}: {c['title'][:90]}" for c in failed if not is_baseline_red(c)]
    if rc != 0 and not failed:
        errors.append(f"Vitest exit {rc} with no failing case (an unhandled error or a crash)")
    return errors


def e2e_specs(suite: dict):
    yield from suite.get("specs", [])
    for child in suite.get("suites", []):
        yield from e2e_specs(child)


def e2e_cases(j: dict) -> list[dict]:
    """Every Playwright spec: file basename, title, its tests' statuses and first failure messages."""
    out = []
    for suite in j.get("suites", []):
        for spec in e2e_specs(suite):
            statuses, msgs = [], []
            for t in spec.get("tests", []):
                statuses.append(t.get("status"))
                for r in t.get("results", []):
                    if r.get("status") not in ("passed", "skipped"):
                        m = (r.get("error") or {}).get("message") or next(
                            (e.get("message", "") for e in r.get("errors", [])), "")
                        msgs.append(ANSI.sub("", m))
            out.append({"file": basename(spec.get("file") or suite.get("file", "")), "title": spec.get("title", ""),
                        "statuses": statuses, "msgs": msgs})
    return out


def is_e2e_assertion(msg: str) -> bool:
    return "expect(" in msg and not any(k in msg for k in E2E_NOT_ASSERT)


def eval_e2e_red(j: dict, rc: int, meu: str) -> list[str]:
    """CASE_EVIDENCE, Red mode, for one MEU's Electron run: every AC case collected and failed by an assertion."""
    errors = [] if rc != 0 else ["Electron Red expected a failing run, got exit 0"]
    if j.get("errors"):
        errors.append(f"top-level Playwright errors (collection or launch): {str(j['errors'][:1])[:160]}")
    cases = e2e_cases(j)
    claimed: set[int] = set()
    for ac, (runner, f, _cls, m) in AC_CASES.items():
        if runner != "e2e" or m != meu:
            continue
        hits, err = find_case(cases, f, ac)
        if err:
            errors.append(err)
            continue
        claimed.add(hits[0])
        c = cases[hits[0]]
        if not c["statuses"] or any(s != "unexpected" for s in c["statuses"]):
            errors.append(f"{ac} statuses {c['statuses']} (need failed, never skipped)")
        elif not c["msgs"] or not all(is_e2e_assertion(msg) for msg in c["msgs"]):
            errors.append(f"{ac} did not fail by an expect() assertion: {(c['msgs'] or [''])[0][:100]!r}")
    for i, c in enumerate(cases):
        if i not in claimed and any(s != "expected" for s in c["statuses"]):
            errors.append(f"untolerated Electron result {c['statuses']} {c['file']}: {c['title'][:80]}")
    return errors


def eval_e2e_ok(j: dict, rc: int, meu: str | None, tags: bool, acs: list[str]) -> list[str]:
    """CASE_EVIDENCE, Green/gate mode, for Electron: named cases (and, with ``tags``, TA_TAGS specs) all expected."""
    st = j.get("stats", {})
    errors = []
    if rc != 0 or j.get("errors"):
        errors.append(f"exit {rc}, top-level errors {str(j.get('errors', [])[:1])[:120]}")
    if st.get("unexpected", 1) or st.get("flaky", 1) or st.get("skipped", 1) or not st.get("expected"):
        errors.append(f"stats {st} (need unexpected = flaky = skipped = 0, expected > 0)")
    cases = e2e_cases(j)
    meus = meus_for(meu)
    want = list(acs) + [ac for ac, c in AC_CASES.items() if c[0] == "e2e" and c[3] in meus and ac not in acs]
    for ac in want:
        f = AC_CASES[ac][1]
        hits, err = find_case(cases, f, ac)
        if ac in acs and len(hits) > 1:
            # A-1: --repeat-each reports each repeat as its own spec with the same title; every repeat must have
            # run (one per expected result of the run) and passed.
            if len({cases[i]["title"] for i in hits}) != 1:
                err = f"{ac}: {len(hits)} differently titled cases in {f} carry it (need one repeated case)"
            elif len(hits) != st.get("expected"):
                err = f"{ac}: {len(hits)} repeats, but the run has {st.get('expected')} expected results"
            else:
                err = None
        if err:
            errors.append(err)
        elif any(not cases[i]["statuses"] or any(s != "expected" for s in cases[i]["statuses"]) for i in hits):
            errors.append(f"{ac} statuses {[cases[i]['statuses'] for i in hits]}")
    for m in meus if tags else []:
        for n in sorted(TA_ROW[m]):
            if TA_FILE[n] not in E2E_FILES:
                continue
            tagged = [c for c in cases if c["file"] == TA_FILE[n] and n in tag_ids(c["title"])]
            if not tagged or any(s != "expected" for c in tagged for s in c["statuses"]):
                errors.append(f"TA-{n}: {len(tagged)} tagged specs in {TA_FILE[n]}, not all expected (TA_TAGS)")
    return errors


def red_sources(meu: str) -> dict[str, str]:
    out = {}
    for _ac, (runner, f, cls, m) in AC_CASES.items():
        p = REPO / "ui/tests/unit" / f
        if runner == "vitest" and m == meu and cls == "red-import":
            out[f] = p.read_text(encoding="utf-8") if p.is_file() else ""
    return out


def cmd_vitest_red(args: argparse.Namespace) -> None:
    j = load_json(args.json)
    report(eval_vitest_red(j, load_text(args.txt), args.rc, args.meu, red_sources(args.meu)),
           f"AC-{args.meu} Vitest RED: every AC case collected and Red by assertion (or red-import), sentinels "
           f"passed, other failures tagged, FIXTURE_RED or BASELINE_RED; {j.get('numPassedTests')} passing")


def cmd_vitest_ok(args: argparse.Namespace) -> None:
    j = load_json(args.json)
    report(eval_vitest_ok(j, load_text(args.txt), args.rc, args.meu),
           f"Vitest: {j.get('numPassedTests')}/{j.get('numTotalTests')} passed"
           f"{'; MEU ' + ', '.join(meus_for(args.meu)) + ' cases and tags passed' if args.meu else ''}")


def cmd_e2e_red(args: argparse.Namespace) -> None:
    report(eval_e2e_red(load_json(args.json), args.rc, args.meu), f"AC-{args.meu} Electron RED: every AC case failed by expect()")


def cmd_e2e_ok(args: argparse.Namespace) -> None:
    j = load_json(args.json)
    report(eval_e2e_ok(j, args.rc, args.meu, args.tags, args.ac or []),
           f"Electron: expected {j.get('stats', {}).get('expected')}, unexpected = flaky = skipped = 0; named cases passed")


# ---------------------------------------------------------------------------------------------------------
# gate, row state, look, review
# ---------------------------------------------------------------------------------------------------------

GATE_REPORTS = ("vitest_json", "vitest_txt", "e2e_json")


def gate_report_shas(g: dict) -> dict[str, str | None]:
    """The sha256 of each raw report gate-result.json names, as it is on disk now."""
    return {k: file_sha(Path(str(g.get(k)))) if g.get(k) else None for k in GATE_REPORTS}


def eval_gate_binding(g: dict, current: dict[str, str | None]) -> list[str]:
    """gate-result.json was written by -Check gate over these exact reports (D-31). Every reader of the
    record (gate-check, look-check, handoff-cases) applies it."""
    errors = []
    if g.get("check") != "gate":
        errors.append(f"check {g.get('check')!r}: gate-result.json was not written by validate-task.ps1 -Check gate")
    for key in GATE_REPORTS:
        want = str(g.get(f"{key}_sha256") or "")
        if not HEX64.match(want):
            errors.append(f"{key}_sha256 {want!r} is not a sha256")
        elif current.get(key) is None or want.lower() != str(current[key]).lower():
            errors.append(f"{key} {g.get(key)!r} is missing or is not the report -Check gate recorded")
    return errors


def eval_gate(g: dict, order: list[str], vj: dict | None, vtxt: str | None, ej: dict | None, fresh: str,
              current: dict[str, str | None]) -> list[str]:
    """GATE over gate-result.json and the raw reports it names. ``current`` holds the sha256 of each named
    report as it is on disk now, which must equal the hash -Check gate recorded (D-31)."""
    errors = eval_gate_binding(g, current)
    ran = [s.get("id") for s in g.get("stages", [])]
    if g.get("schema") != "s34-gate.v2" or ran != order:
        errors.append(f"stages ran {ran}, expected {order} (schema {g.get('schema')})")
    errors += [f"stage {s.get('id')} exit {s.get('exit')}" for s in g.get("stages", []) if s.get("exit") != 0]
    py = g.get("pytest") or {}
    if py.get("failed") != 0 or (py.get("passed") or 0) < COUNT_FLOORS["pytest_passed"]:
        errors.append(f"pytest {py} (failed 0 and passed ≥ {COUNT_FLOORS['pytest_passed']})")
    stage = {s.get("id"): s for s in g.get("stages", [])}
    if vj is None:
        errors.append("no Vitest JSON report")
    else:
        rc = stage.get("ui-tests", {}).get("raw_exit", stage.get("ui-tests", {}).get("exit", 1))
        errors += [f"Vitest: {e}" for e in eval_vitest_ok(vj, vtxt, rc, "81")]
        if (vj.get("numTotalTests") or 0) < COUNT_FLOORS["vitest_total"]:
            errors.append(f"Vitest total {vj.get('numTotalTests')} < {COUNT_FLOORS['vitest_total']} (COUNT_FLOORS)")
    if ej is None:
        errors.append("no Playwright JSON report")
    else:
        errors += [f"Electron: {e}" for e in eval_e2e_ok(ej, stage.get("ui-electron", {}).get("exit", 1), "81", True, [])]
        cases = e2e_cases(ej)
        for n in sorted(TA_LATE):
            tagged = [c for c in cases if c["file"] == TA_FILE[n] and n in tag_ids(c["title"])]
            if not tagged or any(s != "expected" for c in tagged for s in c["statuses"]):
                errors.append(f"Electron: TA-{n}: {len(tagged)} tagged specs in {TA_FILE[n]}, not all expected (TA_LATE)")
        if (ej.get("stats", {}).get("expected") or 0) < COUNT_FLOORS["e2e_expected"]:
            errors.append(f"Electron expected {ej.get('stats', {}).get('expected')} < {COUNT_FLOORS['e2e_expected']}")
    if not (g.get("identity_before") == g.get("identity_after") == fresh):
        errors.append(f"identity mismatch: before {g.get('identity_before')} after {g.get('identity_after')} fresh {fresh}")
    return errors


def cmd_gate_check(args: argparse.Namespace) -> None:
    g = load_json(args.result)
    vj = load_json(g["vitest_json"]) if g.get("vitest_json") and Path(g["vitest_json"]).is_file() else None
    ej = load_json(g["e2e_json"]) if g.get("e2e_json") and Path(g["e2e_json"]).is_file() else None
    fresh = identity()
    current = gate_report_shas(g)
    report(eval_gate(g, ps1_stage_ids(read(f"{PLAN_REL}/validate-task.ps1")), vj, load_text(g.get("vitest_txt")), ej, fresh,
                     current),
           f"GATE @ {str(g.get('tested_commit'))[:7]}: CASE_EVIDENCE over the raw reports; floors; identity {fresh[:12]}…")


def cmd_task_state(args: argparse.Namespace) -> None:
    rows = [ln for ln in read(f"{PLAN_REL}/task.md").splitlines() if re.match(r"^\| [0-9]+ \|", ln)]
    if len(rows) != 11:
        fail(f"expected 11 implementation rows (0-10), got {len(rows)}")
    for ln in rows:
        s = ln.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
        if not (s == "[x]" or (s == "[B]" and "follow-up" in ln and "B-" in ln)):
            fail(f"unfinished row: {ln[:60]}")
    print("PASS implementation rows 0-10")


def cmd_look_check(args: argparse.Namespace) -> None:
    body = section(read(f"{PLAN_REL}/walkthrough.md"), "CHROME_LOOK")
    g = load_json(args.result)
    unbound = eval_gate_binding(g, gate_report_shas(g))
    if unbound:
        fail(f"gate-result.json: {unbound[0]}")
    if not body:
        fail("walkthrough.md has no ## CHROME_LOOK section")
    for item in (f"L{n}" for n in range(1, 9)):
        if re.search(rf"^\|?\s*{item}\b.*pass\|fail", body, re.M):
            fail(f"{item} still carries the template token 'pass|fail'")
        m = re.search(rf"^\|?\s*{item}\b[^a-z]*(pass|fail)\b", body, re.M)
        if not m:
            fail(f"{item} has no recorded pass/fail")
        if m.group(1) != "pass":
            fail(f"{item} recorded fail (Decision Brief before the review)")
    if "USER_EXPLICIT" not in body:
        fail("CHROME_LOOK carries no USER_EXPLICIT provenance")
    sha = str(g.get("tested_commit") or "")[:7]
    if not sha or sha not in body:
        fail(f"CHROME_LOOK does not name the gate's tested commit {sha!r}")
    if g.get("identity_after") != identity():
        fail("the tree changed since GATE; re-run GATE before the look is bound to it")
    print(f"PASS CHROME_LOOK L1-L8 on {sha}")


def cmd_review_check(args: argparse.Namespace) -> None:
    t = read(args.review)
    parts = t.split("---")
    fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', parts[1], re.M)) if len(parts) > 2 else {}
    if fm.get("agent", "").lower() != REVIEW_AGENT:
        fail(f"review agent {fm.get('agent')!r} is not {REVIEW_AGENT}")
    if (fm.get("verdict") != "approved" or fm.get("review_mode") != "execution"
            or fm.get("target_plan") != f"{PLAN_REL}/implementation-plan.md"):
        fail(f"review frontmatter verdict {fm.get('verdict')} mode {fm.get('review_mode')} target {fm.get('target_plan')}")
    ledger = Path(os.environ.get("RECEIPTS_DIR", "C:/Temp/av-kit")) / "review-ledger" / f"{args.loop_id}.json"
    j = load_json(str(ledger))
    rounds = j.get("rounds") or []
    if not rounds:
        fail(f"ledger {args.loop_id} has no rounds")
    last = rounds[-1]
    if (j.get("review_mode") != "execution" or last.get("verdict") != "approved"
            or "gpt-6.1-sol" not in str(last.get("agent")) or int(last.get("round", 99)) > 6):
        fail(f"ledger last round {last.get('round')} verdict {last.get('verdict')} agent {last.get('agent')} "
             f"mode {j.get('review_mode')}")
    print(f"PASS execution review approved, round {last['round']} by {last['agent']}")


def eval_handoff(text: str, meu: str, identity_after: str | None) -> list[str]:
    """Each handoff names every dotted AC id of its MEU and quotes the gate's identity_after."""
    missing = [f"AC-{meu}.{n}" for n in range(1, AC_MAX[meu] + 1) if not ac_in(f"AC-{meu}.{n}", text)]
    errors = [f"MEU-{meu} handoff does not name {missing}"] if missing else []
    if not identity_after or identity_after not in text:
        errors.append(f"MEU-{meu} handoff does not quote gate-result.json identity_after {identity_after!r}")
    return errors


def cmd_handoff_cases(args: argparse.Namespace) -> None:
    g = load_json(str(REPO / PLAN_REL / "gate-result.json"))
    after = g.get("identity_after")
    errors = [f"gate-result.json: {e}" for e in eval_gate_binding(g, gate_report_shas(g))]
    for meu, h in HANDOFFS.items():
        errors += eval_handoff(read(h) if (REPO / h).is_file() else "", meu, after)
    report(errors, f"handoff-cases: both handoffs name every dotted AC id and identity {str(after)[:12]}…")


# ---------------------------------------------------------------------------------------------------------
# root cause, census, hub, SSOT
# ---------------------------------------------------------------------------------------------------------

def png_decode(data: bytes | None) -> tuple[int, int] | str:
    """A real decode, not a header sniff: every chunk's CRC, IHDR first, IDAT present, IEND last, 8-bit RGB or
    RGBA non-interlaced (what GDI+ writes for a screen capture), and the inflated image data exactly
    h * (1 + w * bpp) bytes. Returns (width, height) or the reason it is not a capture."""
    if data is None:
        return "missing"
    if not data.startswith(PNG_SIG):
        return "no PNG signature"
    pos, chunks = len(PNG_SIG), []
    while pos < len(data):
        if pos + 12 > len(data):
            return "truncated chunk header"
        (n,) = struct.unpack(">I", data[pos:pos + 4])
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + n]
        if len(body) != n or pos + 12 + n > len(data):
            return f"truncated {kind!r} chunk"
        (crc,) = struct.unpack(">I", data[pos + 8 + n:pos + 12 + n])
        if zlib.crc32(kind + body) & 0xFFFFFFFF != crc:
            return f"bad CRC in {kind!r}"
        chunks.append((kind, body))
        pos += 12 + n
    kinds = [k for k, _ in chunks]
    if not kinds or kinds[0] != b"IHDR" or kinds[-1] != b"IEND" or b"IDAT" not in kinds or len(chunks[0][1]) != 13:
        return f"chunks {[k.decode('latin-1') for k in kinds]} (need IHDR first, IDAT, IEND last)"
    w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunks[0][1])
    bpp = {2: 3, 6: 4}.get(ctype)
    if depth != 8 or bpp is None or interlace != 0:
        return f"format depth {depth} colour {ctype} interlace {interlace} (need 8-bit RGB/RGBA, non-interlaced)"
    try:
        raw = zlib.decompress(b"".join(b for k, b in chunks if k == b"IDAT"))
    except zlib.error as exc:
        return f"image data does not inflate ({exc})"
    if len(raw) != h * (1 + w * bpp):
        return f"image data is {len(raw)} bytes (need {h * (1 + w * bpp)} for {w}x{h})"
    return w, h


def iso(value: object) -> datetime.datetime | None:
    try:
        stamp = datetime.datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return stamp if stamp.tzinfo is not None else None


def inside(point: dict, box: dict) -> bool:
    try:
        return (box["width"] > 0 and box["height"] > 0 and box["x"] <= point["x"] <= box["x"] + box["width"]
                and box["y"] <= point["y"] <= box["y"] + box["height"])
    except (KeyError, TypeError):
        return False


def box_inside(inner: dict, outer: dict) -> bool:
    try:
        return (inside({"x": inner["x"], "y": inner["y"]}, outer)
                and inside({"x": inner["x"] + inner["width"], "y": inner["y"] + inner["height"]}, outer))
    except (KeyError, TypeError):
        return False


def eval_probe(run: dict, baseline: str, body: str, pngs: dict[str, bytes | None], mtimes: dict[str, float | None],
               receipt: str | None, current: dict[str, str | None]) -> list[str]:
    """ROOT_CAUSE_PROBE over the PROBE_RUN record, bound to its producer (D-28, D-31).

    ``current`` holds the sha256 of the files the record must still match: the build the probe launched
    (``build``), the probe script that ran (``probe``) and the probe's own receipt (``receipt``)."""
    errors = []
    if run.get("check") != "probe":
        errors.append(f"check {run.get('check')!r}: the record was not written by validate-task.ps1 -Check probe")
    if run.get("exit") != 0 or run.get("head") != baseline or run.get("gated_clean") is not True:
        errors.append(f"run exit {run.get('exit')} head {run.get('head')} gated_clean {run.get('gated_clean')} "
                      f"(need 0, baseline {baseline}, true)")
    for key, label in (("build_sha256", "build"), ("probe_sha256", "probe"), ("receipt_sha256", "receipt")):
        value = str(run.get(key) or "")
        if not HEX64.match(value):
            errors.append(f"{key} {value!r} is not a sha256")
        elif current.get(label) is None:
            errors.append(f"{key}: the {label} file it binds is missing")
        elif value.lower() != str(current[label]).lower():
            errors.append(f"{key} does not match the current {label} file")
    start, end = iso(run.get("started")), iso(run.get("finished"))
    if start is None or end is None or not start < end or (end - start).total_seconds() > PROBE_MAX_SECONDS:
        errors.append(f"started {run.get('started')!r} finished {run.get('finished')!r} (need two zoned ISO times, "
                      f"in order, at most {PROBE_MAX_SECONDS // 60} minutes apart)")
        start = end = None
    want = sorted((n, t) for n in (1, 2, 3) for t in PROBE_TARGETS)
    obs = run.get("observations") or []
    got = sorted((o.get("hypothesis"), o.get("target")) for o in obs)
    if got != want:
        errors.append(f"observations {got} (need H1-H3 x {PROBE_TARGETS})")
    for o in obs:
        n, t = o.get("hypothesis"), o.get("target")
        c, r, win = o.get("cursor") or {}, o.get("rect") or {}, o.get("window") or {}
        if not inside(c, r):
            errors.append(f"H{n} {t}: cursor {c} is not inside the target rect {r}")
        if not box_inside(r, win):
            errors.append(f"H{n} {t}: target rect {r} is not inside the captured window {win}")
        at = iso(o.get("at"))
        if at is None or start is None or not start <= at <= end:
            errors.append(f"H{n} {t}: observed at {o.get('at')!r}, outside the run")
        if not str(o.get("title") or "").strip():
            errors.append(f"H{n} {t}: the target had no title attribute")
        name, key = f"s34-probe-h{n}-{t}.png", str(o.get("png"))
        if basename(key) != name:
            errors.append(f"H{n} {t}: png {o.get('png')!r} is not {name}")
        data = pngs.get(key)
        decoded = png_decode(data)
        if isinstance(decoded, str):
            errors.append(f"{name} is not a capture: {decoded}")
        elif decoded != (win.get("width"), win.get("height")) or decoded[0] < 320 or decoded[1] < 200:
            errors.append(f"{name} is {decoded[0]}x{decoded[1]}; the captured window is "
                          f"{win.get('width')}x{win.get('height')} (need equal, at least 320x200)")
        if data is not None and hashlib.sha256(data).hexdigest().lower() != str(o.get("sha256")).lower():
            errors.append(f"{name} does not match its recorded sha256")
        mtime = mtimes.get(key)
        if mtime is None or start is None or not (start.timestamp() - PROBE_MTIME_SLACK <= mtime
                                                  <= end.timestamp() + PROBE_MTIME_SLACK):
            errors.append(f"{name} was not written during the run (mtime {mtime})")
    order = sorted(obs, key=lambda o: (o.get("hypothesis") if isinstance(o.get("hypothesis"), int) else 99,
                                       PROBE_TARGETS.index(o["target"]) if o.get("target") in PROBE_TARGETS else 99))
    done = f"{PROBE_DONE} " + ",".join(str(o.get("sha256")).lower() for o in order)
    lines = [] if receipt is None else [ln.strip() for ln in receipt.splitlines() if ln.strip().startswith(PROBE_DONE)]
    if lines != [done]:
        errors.append(f"the probe receipt {PROBE_RECEIPT} needs exactly one line '{PROBE_DONE} <the 6 PNG sha256, "
                      f"H1-H3 x {PROBE_TARGETS} order>'; found {lines[:2] if receipt is not None else 'no receipt'}")
    lines = [ln for ln in body.splitlines() if re.match(r"^\s*-?\s*H\d", ln)]
    good = [re.match(r"^\s*-?\s*H([1-3]) (nav-capture|capture-tool-arrow): tooltip-visible (yes|no) — "
                     r"s34-probe-h\1-\2\.png\s*$", ln) for ln in lines]
    if len(lines) != 6 or not all(good) or sorted((int(m.group(1)), m.group(2)) for m in good if m) != want:
        errors.append(f"§Root cause needs exactly the 6 observation lines; found {len(lines)}: {lines[:6]}")
    findings = re.findall(r"^\s*-?\s*finding:\s*(.*?)\s*$", body, re.M)
    if len(findings) != 1 or not (findings[0] == "not found" or len(findings[0]) > 10):
        errors.append(f"§Root cause needs one finding: line (a cause and fix longer than 10 characters, or "
                      f"'not found'); found {findings}")
    return errors


def file_sha(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def cmd_root_cause(args: argparse.Namespace) -> None:
    base = REPO / PLAN_REL / "baseline.sha"
    if not base.is_file():
        fail("baseline.sha is missing (row 0)")
    baseline = base.read_text(encoding="utf-8").strip()
    if git("rev-parse", "HEAD").strip() != baseline:
        fail("HEAD is not baseline.sha: row 2 closes before any product change, while the probed build is on disk")
    dirty = eval_clean(porcelain_paths(git("status", "--porcelain", "--untracked-files=all")))
    if dirty:
        fail(f"row 2 closes on the probed baseline tree; {dirty[0]}")
    run = load_json(args.run)
    pngs, mtimes = {}, {}
    for o in run.get("observations") or []:
        p = Path(str(o.get("png", "")))
        pngs[str(o.get("png"))] = p.read_bytes() if p.is_file() else None
        mtimes[str(o.get("png"))] = p.stat().st_mtime if p.is_file() else None
    receipt_path = Path(args.run).parent / PROBE_RECEIPT
    receipt = receipt_path.read_text(encoding="utf-8", errors="replace") if receipt_path.is_file() else None
    current = {"build": file_sha(REPO / PROBE_BUILD), "probe": file_sha(REPO / PROBE_SCRIPT),
               "receipt": file_sha(receipt_path)}
    body = section(read(f"{PLAN_REL}/walkthrough.md"), "Root cause")
    report(eval_probe(run, baseline, body, pngs, mtimes, receipt, current),
           "ROOT_CAUSE_PROBE: the -Check probe record is bound to baseline.sha, this build, this probe script and its "
           "receipt; 6 on-target observations inside the run; 6 decodable window captures; 6 lines and a finding")


def census_hits(text: str) -> list[tuple[str, int]]:
    hits = []
    for ln in text.splitlines():
        m = re.match(r"^(ui/[^:]+):(\d+):", ln.replace("\\", "/"))
        if m:
            hits.append((m.group(1), int(m.group(2))))
    return hits


def eval_census(hits: list[tuple[str, int]], body: str) -> list[str]:
    errors = [] if hits else ["census receipt has no hits"]
    entries = []
    for ln in body.splitlines():
        if re.search(r"ui/[\w./-]+:\*", ln):
            errors.append(f"§Census uses a wildcard: {ln.strip()[:80]}")
        d = CENSUS_DISPOSITION.search(ln)
        for path, a, b in re.findall(r"(ui/[\w./-]+):(\d+)(?:[–-](\d+))?", ln):
            if d:
                entries.append((path, int(a), int(b or a), d.group(1)))
    if any(e[3] == "new-contradiction" for e in entries):
        errors.append("§Census records a new-contradiction: Stop condition S2 (Decision Brief, no test edit)")
    missing = [f"{p}:{n}" for p, n in hits if not any(e[0] == p and e[1] <= n <= e[2] for e in entries)]
    if missing:
        errors.append(f"{len(missing)} census hits have no disposition: {missing[:8]}")
    return errors


def cmd_census_check(args: argparse.Namespace) -> None:
    hits = census_hits(Path(args.census).read_text(encoding="utf-8"))
    report(eval_census(hits, section(read(f"{PLAN_REL}/walkthrough.md"), "Census")),
           f"census: {len(hits)} hits, all dispositioned by path:line; no new-contradiction")


def cmd_hub(args: argparse.Namespace) -> None:
    s09 = read("docs/build-plan/09-screenshot-capture.md")
    rows = {m.group(1): m.group(0) for m in re.finditer(r"^\| (Hotkey|History|Pointer|Sampler|Keyboard) \|.*$", s09, re.M)}
    checks = [
        ("09 Hotkey row", "inline in the Capture header row (MEU-81, Human-approved triage D-64)" in rows.get("Hotkey", "")),
        ("09 History row", "sampling" not in rows.get("History", "x sampling")),
        ("09 Pointer row", "`sampling`" not in rows.get("Pointer", "`sampling`")),
        ("09 Sampler row", "Removed by MEU-81 (Human-approved 2026-10-03, triage D-51)" in rows.get("Sampler", "")),
        ("09 Keyboard row", "cancel sampling" not in rows.get("Keyboard", "cancel sampling")
         and "triage D-49" in rows.get("Keyboard", "") and "Session 34 plan D-17" in rows.get("Keyboard", "")),
        ("09 Sample annotations", s09.count("(Sample removed by MEU-81)") >= 3),
    ]
    hints = re.split(r"^### Icon-button hints$", s09, flags=re.M)[-1].split("\n### ", 1)[0]
    actions = re.split(r"^### Capture action row$", s09, flags=re.M)[-1].split("\n### ", 1)[0]
    checks += [
        ("09 §Icon-button hints rows", all(s in hints for s in (
            "Hint text and timing", "Session 34 plan D-9, D-10", "Root-cause finding", "Session 34 plan D-14"))),
        ("09 §Capture action row rows", all(s in actions for s in (
            "Endpoint nudge", "Session 34 plan D-17", "Marks row layout", "Session 34 plan D-18"))),
    ]
    sentence = ("Since MEU-81 the per-shot and per-mark actions are icon buttons with MEU-80 hints, Delete sits red at "
                "the far right after a separator, and the hotkey status shows inline in the header instead of a "
                "reserved band; see [09 §Capture action row](09-screenshot-capture.md#capture-action-row).")
    s11 = read("docs/build-plan/11-page-layout.md")
    base11 = git("show", f"{args.baseline}:docs/build-plan/11-page-layout.md")
    cp = re.compile(r"^\| CP \|.*$", re.M)
    checks += [
        ("11 prose sentence", s11.count(sentence) == 1),
        ("11 CP rows untouched", cp.findall(s11) == cp.findall(base11) and cp.findall(s11)),
    ]
    matrix = read("docs/build-plan/build-priority-matrix.md")
    r13 = ("| 9.13 | MEU-80 | `gui-icon-button-hints` | [09 §Icon-button hints](09-screenshot-capture.md#icon-button-hints)"
           " | MEU-65, MEU-67 |")
    r14 = ("| 9.14 | MEU-81 | `gui-capture-action-row` | [09 §Capture action row](09-screenshot-capture.md#capture-action-row)"
           " | MEU-80, MEU-67 |")
    lines = matrix.splitlines()
    checks.append(("matrix 9.13/9.14 after 9.12", lines.count(r13) == 1 and lines.count(r14) == 1
                   and any(ln.startswith("| 9.12 |") for ln in lines)
                   and lines.index(r13) == next(i for i, ln in enumerate(lines) if ln.startswith("| 9.12 |")) + 1
                   and lines.index(r14) == lines.index(r13) + 1))
    bad = [name for name, ok in checks if not ok]
    if bad:
        fail(f"HUB_EDITS not as planned: {bad}")
    print(f"PASS hub: {len(checks)} HUB_EDITS checks")


def _yaml():
    import yaml  # noqa: PLC0415 - lazy: static must stay stdlib-only
    return yaml


def meu_statuses() -> dict[str, str]:
    data = _yaml().safe_load(read(".agent/context/meu-status.yaml"))
    return {r["id"]: r.get("status") for r in data["meus"]}


def cmd_meu_state(args: argparse.Namespace) -> None:
    rows = meu_statuses()
    for want in args.want:
        meu, status = want.split("=")
        if rows.get(meu) != status:
            fail(f"{meu} is {rows.get(meu)!r}, expected {status!r}")
    print(f"PASS MEU state: {', '.join(args.want)}")


def cmd_ssot_review_state(args: argparse.Namespace) -> None:
    if "| 34 | `capture-chrome` | MEU-80, MEU-81 | P2 | in review |" not in read(GROUPING):
        fail("grouping Session 34 is not in review")
    focus = read(".agent/context/current-focus.md")
    if "capture-chrome" not in focus or "ready_for_review" not in focus:
        fail("current-focus.md does not record Session 34 ready_for_review")
    print("PASS SSOT review state (grouping, focus)")


def cmd_post_review(args: argparse.Namespace) -> None:
    rows = meu_statuses()
    for meu in ("MEU-80", "MEU-81"):
        if rows.get(meu) != "approved":
            fail(f"{meu} is {rows.get(meu)!r}")
    issues = {i["id"]: i for i in _yaml().safe_load(read(KNOWN_ISSUES))["issues"]}
    for iid in ISSUES:
        it = issues.get(iid) or {}
        ev = (it.get("verification") or {}).get("evidence_file") or ""
        if it.get("status") != "resolved" or not ev.startswith(f"{PLAN_REL}/"):
            fail(f"{iid} status {it.get('status')} evidence {ev!r}")
    if "| 34 | `capture-chrome` | MEU-80, MEU-81 | P2 | approved |" not in read(GROUPING):
        fail("grouping Session 34 is not approved")
    if "2026-10-14-capture-chrome" not in read("docs/execution/metrics.md"):
        fail("metrics row missing")
    print("PASS POST_REVIEW_STATE")


# ---------------------------------------------------------------------------------------------------------
# selftest: every refusal named in plan §Verification Plan 0 refuses; every well-formed input passes
# ---------------------------------------------------------------------------------------------------------

ASSERT_MSG = "AssertionError: expected null not to be null"
DOM_MSG = "Error: expect(element).toBeInTheDocument()"
E2E_MSG = "Error: expect(locator).toBeVisible() failed"
BASE_MSG = f"AssertionError: {BASELINE_RED[2]}: expected '#0891b2' to be '#0e7490'"


def _vjson(cases: list[tuple], suite_errors: dict[str, str] | None = None, total: int | None = None) -> dict:
    files: dict[str, list[dict]] = {}
    for f, title, status, msg in cases:
        files.setdefault(f, []).append({"title": title, "fullName": f"suite {title}", "status": status,
                                        "failureMessages": [msg] if msg else []})
    res = [{"name": f"P:/wt/ui/tests/unit/{f}", "message": "", "assertionResults": a} for f, a in files.items()]
    res += [{"name": f"P:/wt/ui/tests/unit/{f}", "message": m, "assertionResults": []} for f, m in (suite_errors or {}).items()]
    return {"numPendingTests": 0, "numTodoTests": 0, "numTotalTests": total or len(cases),
            "numPassedTests": sum(c[2] == "passed" for c in cases), "testResults": res}


def _ejson(specs: list[tuple], expected: int | None = None) -> dict:
    files: dict[str, list[dict]] = {}
    for f, title, status, msg in specs:
        res = {"status": "failed" if status == "unexpected" else "skipped" if status == "skipped" else "passed",
               "error": {"message": msg} if msg else None, "errors": [{"message": msg}] if msg else []}
        files.setdefault(f, []).append({"title": title, "file": f, "tests": [{"status": status, "results": [res]}]})
    stats = {"expected": expected or sum(s[2] == "expected" for s in specs),
             "unexpected": sum(s[2] == "unexpected" for s in specs), "flaky": sum(s[2] == "flaky" for s in specs),
             "skipped": sum(s[2] == "skipped" for s in specs)}
    return {"errors": [], "stats": stats,
            "suites": [{"title": f, "file": f, "specs": [], "suites": [{"title": "d", "file": f, "specs": s}]}
                       for f, s in files.items()]}


def _tagged(meu: str, status: str, msg: str | None, runner: str) -> list[tuple]:
    out = []
    for n in sorted(TA_ROW[meu]):
        if (TA_FILE[n] in E2E_FILES) == (runner == "e2e"):
            out.append((TA_FILE[n], f"amended case [TA-{n}]", status, msg))
    return out


def _png(w: int, h: int, seed: int = 0) -> bytes:
    """A complete, decodable 8-bit RGBA PNG (the selftest's stand-in for a GDI+ screen capture)."""
    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    row = b"\0" + bytes([seed % 256]) * (w * 4)
    return (PNG_SIG + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row * h)) + chunk(b"IEND", b""))


def _png_header_only(w: int, h: int) -> bytes:
    """Round 2's accepted fixture: a signature and an IHDR with no image data (R2 F4 negative)."""
    return PNG_SIG + struct.pack(">I", 13) + b"IHDR" + struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0) + b"\0" * 4


def selftest_cases() -> list[tuple[str, bool, list[str]]]:
    """(name, must_refuse, errors) for every synthetic input."""
    out: list[tuple[str, bool, list[str]]] = []

    def case(name: str, refuse: bool, errors: list[str]) -> None:
        out.append((name, refuse, errors))

    txt = " Test Files  3 failed | 4 passed (7)\n      Tests  9 failed | 30 passed (39)\n"
    tooltip_src = "\n".join(f"it('AC-80.{n}: behaviour', () => {{}})" for n in (1, 2, 3, 4, 5, 6, 7, 13))
    import_err = 'Failed to resolve import "../../src/renderer/src/components/ui/Tooltip" from "tests/unit/tooltip.test.tsx". Does the file exist?'
    red80 = [("icon-hints.test.ts", SENTINEL_TITLE, "passed", None),
             ("icon-hints.test.ts", "AC-80.8: capture inventory", "failed", ASSERT_MSG),
             ("icon-hints.test.ts", "AC-80.9: other inventory", "failed", DOM_MSG),
             ("capture-page.behavior.test.ts", "AC-57.5 disabled box [TA-8]", "failed", ASSERT_MSG),
             ("queue-card.test.ts", "handle leads the row [TA-25]", "failed", ASSERT_MSG),
             (FIXTURE_RED[0], FIXTURE_RED[1], "failed", ASSERT_MSG),
             (BASELINE_RED[0], f"{BASELINE_RED[1]} accent tokens", "failed", BASE_MSG),
             ("capture-page.behavior.test.ts", "unchanged case", "passed", None)]
    sup = {"tooltip.test.tsx": import_err}

    def red(cases: list[tuple], suites: dict | None = None, t: str | None = txt, rc: int = 1,
            src: str = tooltip_src, meu: str = "80") -> list[str]:
        return eval_vitest_red(_vjson(cases, sup if suites is None else suites), t, rc, meu, {"tooltip.test.tsx": src})

    def swap(cases: list[tuple], i: int, **kw) -> list[tuple]:
        c = list(cases[i])
        for k, v in kw.items():
            c[("file", "title", "status", "msg").index(k)] = v
        return cases[:i] + [tuple(c)] + cases[i + 1:]

    case("vitest-red 80: well-formed", False, red(red80))
    case("vitest-red 80: a missing AC case", True, red(red80[:2] + red80[3:]))
    case("vitest-red 80: a skipped AC case", True, red(swap(red80, 2, status="skipped", msg=None)))
    case("vitest-red 80: a TypeError Red", True, red(swap(red80, 1, msg="TypeError: x is not a function")))
    case("vitest-red 80: a failed SETUP_SENTINEL", True, red(swap(red80, 0, status="failed", msg=ASSERT_MSG)))
    case("vitest-red 80: a failure with no TA tag", True, red(swap(red80, 3, title="AC-57.5 disabled box")))
    case("vitest-red 80: another row's tag", True, red(swap(red80, 3, title="AC-57.5 disabled box [TA-1]")))
    case("vitest-red 80: a tag in the wrong file", True, red(swap(red80, 4, title="handle [TA-8]")))
    case("vitest-red 80: a tagged TypeError", True, red(swap(red80, 3, msg="TypeError: boom")))
    case("vitest-red 80: a BASELINE_RED look-alike", True, red(swap(red80, 6, msg="AssertionError: another message")))
    case("vitest-red 80: FIXTURE_RED at row 6", True, red([c for c in red80 if c[0] != "icon-hints.test.ts"]
                                                          + [("capture-action-row.test.ts", SENTINEL_TITLE, "passed", None)],
                                                          suites={}, meu="81"))
    case("vitest-red 80: unhandled errors", True, red(red80, t=txt + "⎯⎯ Unhandled Errors ⎯⎯\n"))
    case("vitest-red 80: no text receipt", True, red(red80, t=None))
    case("vitest-red 80: exit 0", True, red(red80, rc=0))
    case("vitest-red 80: the red-import file loaded", True, red(red80, suites={}))
    case("vitest-red 80: another suite fails to load", True,
         red(red80, suites={**sup, "icon-hints.test.ts": "SyntaxError: Unexpected token"}))
    case("vitest-red 80: a red-import title missing", True, red(red80, src=tooltip_src.replace("AC-80.13", "AC-80.x")))

    red81 = [("capture-action-row.test.ts", SENTINEL_TITLE, "passed", None)]
    red81 += [("capture-action-row.test.ts", f"AC-81.{n}: case", "failed", DOM_MSG) for n in (1, 2, 4, 6, 8, 10, 12, 13)]
    red81 += [("capture-action-row.test.ts", f"AC-81.{n}: guard", "passed", None) for n in (3, 5, 15)]
    red81 += [("capture-action-row.test.ts", "AC-81.7: guard", "failed", ASSERT_MSG),
              ("capture-page.behavior.test.ts", "AC-60.10 burst [TA-1]", "failed", ASSERT_MSG),
              ("capture-help-content.test.ts", "help sentence [TA-16]", "failed", ASSERT_MSG)]
    case("vitest-red 81: well-formed", False, red(red81, suites={}, meu="81"))
    case("vitest-red 81: a guard failing by TypeError", True,
         red(swap(red81, 12, msg="TypeError: cannot read"), suites={}, meu="81"))
    case("vitest-red 81: a red case passing", True, red(swap(red81, 1, status="passed", msg=None), suites={}, meu="81"))
    case("vitest-red 81: AC-81.6 matched by AC-81.60", True,
         red(swap(red81, 4, title="AC-81.60: case"), suites={}, meu="81"))

    green = [("icon-hints.test.ts", SENTINEL_TITLE, "passed", None),
             ("capture-action-row.test.ts", SENTINEL_TITLE, "passed", None)]
    green += [(c[1], ac, "passed", None) for ac, c in AC_CASES.items() if c[0] == "vitest"]
    green += _tagged("80", "passed", None, "vitest") + _tagged("81", "passed", None, "vitest")
    green += [(BASELINE_RED[0], f"{BASELINE_RED[1]} accent tokens", "failed", BASE_MSG)]
    gtxt = " Tests  1 failed | 40 passed (41)\n"
    case("vitest-ok 81: well-formed (BASELINE_RED tolerated)", False, eval_vitest_ok(_vjson(green), gtxt, 1, "81"))
    case("vitest-ok 81: a missing tag", True, eval_vitest_ok(_vjson([c for c in green if "[TA-26]" not in c[1]]), gtxt, 1, "81"))
    case("vitest-ok 81: an AC case failed", True, eval_vitest_ok(_vjson(swap(green, 3, status="failed", msg=ASSERT_MSG)), gtxt, 1, "81"))
    case("vitest-ok 81: another failure", True,
         eval_vitest_ok(_vjson(green + [("x.test.ts", "other", "failed", ASSERT_MSG)]), gtxt, 1, "81"))
    case("vitest-ok 81: a skipped case", True,
         eval_vitest_ok(_vjson(green + [("x.test.ts", "other", "skipped", None)]), gtxt, 1, "81"))
    case("vitest-ok: exit 1 with no failing case", True,
         eval_vitest_ok(_vjson([("x.test.ts", "a", "passed", None)]), gtxt, 1, None))
    case("vitest-ok: unhandled errors", True,
         eval_vitest_ok(_vjson([("x.test.ts", "a", "passed", None)]), gtxt + " Errors  1 error\n", 0, None))
    case("vitest-ok: baseline well-formed", False, eval_vitest_ok(_vjson([("x.test.ts", "a", "passed", None)]), gtxt, 0, None))

    e_red = [("capture-inbox.test.ts", "AC-80.10: hover", "unexpected", E2E_MSG),
             ("console-chrome.test.ts", "AC-80.11: close hint", "unexpected", E2E_MSG)]
    case("e2e-red 80: well-formed", False, eval_e2e_red(_ejson(e_red), 1, "80"))
    case("e2e-red 80: a TypeError Red", True,
         eval_e2e_red(_ejson(swap(e_red, 0, msg="TypeError: x is undefined at expect(")), 1, "80"))
    case("e2e-red 80: a skipped AC case", True, eval_e2e_red(_ejson(swap(e_red, 1, status="skipped", msg=None)), 1, "80"))
    case("e2e-red 80: a missing AC case", True, eval_e2e_red(_ejson(e_red[:1]), 1, "80"))
    e_ok = [(c[1], ac, "expected", None) for ac, c in AC_CASES.items() if c[0] == "e2e"]
    e_ok += _tagged("80", "expected", None, "e2e") + _tagged("81", "expected", None, "e2e")
    case("e2e-ok 81 with tags: well-formed", False, eval_e2e_ok(_ejson(e_ok), 0, "81", True, []))
    case("e2e-ok 81: a skipped spec", True,
         eval_e2e_ok(_ejson(e_ok + [("capture-inbox.test.ts", "x", "skipped", None)]), 0, "81", True, []))
    case("e2e-ok 81: a missing tag", True, eval_e2e_ok(_ejson([c for c in e_ok if "[TA-19]" not in c[1]]), 0, "81", True, []))
    case("e2e-ok --ac: the repeated case absent", True, eval_e2e_ok(_ejson(e_ok[1:2]), 0, None, False, ["AC-80.10"]))
    rep10 = [("capture-inbox.test.ts", "AC-80.10: hover", "expected", None)] * 10
    case("e2e-ok --ac: ten repeats, one spec each (well-formed)", False,
         eval_e2e_ok(_ejson(rep10), 0, None, False, ["AC-80.10"]))
    case("e2e-ok --ac: a repeat that did not run", True,
         eval_e2e_ok(_ejson(rep10 + [("capture-inbox.test.ts", "other", "expected", None)]), 0, None, False,
                     ["AC-80.10"]))
    case("e2e-ok --ac: two different cases carry the AC", True,
         eval_e2e_ok(_ejson(rep10[:9] + [("capture-inbox.test.ts", "AC-80.10: other", "expected", None)]), 0, None,
                     False, ["AC-80.10"]))

    listed = {"ui/src/renderer/src/components/ui/Tooltip.tsx"}
    good = {"ui/src/renderer/src/components/ui/Tooltip.tsx", f"{PLAN_REL}/walkthrough.md", ADMIN_FILES[0],
            ADMIN_PREFIXES[0] + "MEU-80-handoff.md"}
    case("scope: well-formed", False, eval_scope(good, [], listed))
    case("scope: a native/ change", True, eval_scope(good | {"native/region-picker-stub/Program.cs"}, [], listed))
    case("scope: an unlisted docs/ change", True, eval_scope(good | {"docs/build-plan/04-rest-api.md"}, [], listed))
    case("scope: a frozen path changed in a commit", True, eval_scope(good, ["tools/review_ledger.py"], listed))
    exc = "tools/validate_closeout_artifacts.py"
    case("scope: the D-39 exception, listed", False, eval_scope(good | {exc}, [exc], listed | {exc}))
    case("scope: the D-39 exception, not listed", True, eval_scope(good | {exc}, [exc], listed))
    case("scope: another tools/ file, even listed", True,
         eval_scope(good | {"tools/review_ledger.py"}, ["tools/review_ledger.py"],
                    listed | {exc, "tools/review_ledger.py"}))
    case("clean: plan files only", False, eval_clean([f"{PLAN_REL}/task.md", ADMIN_PREFIXES[0] + "plan-critical-review.md"]))
    case("clean: a product edit", True, eval_clean([f"{PLAN_REL}/task.md", "ui/src/renderer/src/App.tsx"]))

    base = "a" * 40
    t0 = datetime.datetime(2026, 10, 15, 5, 0, 0, tzinfo=datetime.timezone.utc)
    names = [(n, t) for n in (1, 2, 3) for t in PROBE_TARGETS]
    lines = [f"- H{n} {t}: tooltip-visible no — s34-probe-h{n}-{t}.png" for n, t in names]
    body = "\n".join(lines) + "\n- finding: the window never had focus; call win.focus() before hover\n"
    window = {"x": 100, "y": 100, "width": 320, "height": 200}

    def fixture(imgs: list[bytes] | None = None, win: dict = window, rect: dict | None = None,
                cursor: dict | None = None) -> tuple:
        """A self-consistent -Check probe bundle (run, pngs, mtimes, receipt, current), so each negative below
        differs from the positive in exactly one property."""
        obs, pngs, mtimes = [], {}, {}
        for i, (n, t) in enumerate(names):
            p = f"C:/Temp/av-kit/s34-probe-h{n}-{t}.png"
            img = imgs[i] if imgs else _png(win["width"], win["height"], seed=i)
            obs.append({"hypothesis": n, "target": t, "cursor": dict(cursor or {"x": 160, "y": 160}),
                        "rect": dict(rect or {"x": 150, "y": 150, "width": 40, "height": 30}), "window": dict(win),
                        "at": (t0 + datetime.timedelta(seconds=20 + 10 * i)).isoformat(), "title": "Capture",
                        "png": p, "sha256": hashlib.sha256(img).hexdigest()})
            pngs[p] = img
            mtimes[p] = (t0 + datetime.timedelta(seconds=21 + 10 * i)).timestamp()
        receipt = "launching\n" + f"{PROBE_DONE} " + ",".join(o["sha256"] for o in obs) + "\n"
        cur = {"build": "b" * 64, "probe": "c" * 64, "receipt": hashlib.sha256(receipt.encode()).hexdigest()}
        run = {"check": "probe", "exit": 0, "head": base, "gated_clean": True, "build_sha256": "B" * 64,
               "probe_sha256": "c" * 64, "receipt_sha256": cur["receipt"].upper(), "started": t0.isoformat(),
               "finished": (t0 + datetime.timedelta(minutes=3)).isoformat(), "observations": obs}
        return run, pngs, mtimes, receipt, cur

    def first(data: bytes) -> tuple:
        return fixture(imgs=[data] + [_png(320, 200, seed=i) for i in range(1, 6)])

    run, pngs, mtimes, receipt, cur = fixture()
    obs, p0 = run["observations"], run["observations"][0]["png"]

    def probe(want: str | None, bundle: tuple | None = None, **over) -> list[str]:
        """eval_probe over a bundle with overrides. A negative names the reason it must refuse for: when that
        reason is absent the errors are dropped, so the selftest reports the case as not refused."""
        a = dict(zip(("run", "pngs", "mtimes", "receipt", "current"), bundle or (run, pngs, mtimes, receipt, cur)))
        a["body"] = body
        a.update(over)
        errors = eval_probe(a["run"], base, a["body"], a["pngs"], a["mtimes"], a["receipt"], a["current"])
        return errors if want is None or any(want in e for e in errors) else []

    case("root-cause: well-formed", False, probe(None))
    legacy = {"exit": 0, "head": base, "gated_clean": True,
              "observations": [{k: v for k, v in o.items() if k not in ("window", "at")} for o in obs]}
    flat = {o["png"]: _png_header_only(1280, 800) for o in obs}
    for o in legacy["observations"]:
        o["sha256"] = hashlib.sha256(flat[o["png"]]).hexdigest()
    case("root-cause: round 2's metadata-free record with header-only PNGs", True,
         probe("-Check probe", run=legacy, pngs=flat, receipt=None,
               current={"build": None, "probe": None, "receipt": None}))
    case("root-cause: no producer (record not from -Check probe)", True, probe("-Check probe", run={**run, "check": None}))
    case("root-cause: no receipt", True, probe("receipt file it binds is missing", receipt=None, current={**cur, "receipt": None}))
    case("root-cause: a receipt that is not the recorded one", True,
         probe("does not match the current receipt", current={**cur, "receipt": "d" * 64}))
    case("root-cause: a receipt without PROBE-DONE", True, probe(f"one line '{PROBE_DONE}", receipt="launching\n"))
    case("root-cause: PROBE-DONE names other PNGs", True,
         probe(f"one line '{PROBE_DONE}", receipt=receipt.replace(obs[0]["sha256"], "e" * 64)))
    case("root-cause: no build_sha256", True,
         probe("build_sha256 '' is not a sha256", run={k: v for k, v in run.items() if k != "build_sha256"}))
    case("root-cause: a different build on disk", True, probe("does not match the current build", current={**cur, "build": "f" * 64}))
    case("root-cause: the probe script changed since the run", True,
         probe("does not match the current probe", current={**cur, "probe": "f" * 64}))
    case("root-cause: no start or finish", True,
         probe("two zoned ISO times", run={k: v for k, v in run.items() if k not in ("started", "finished")}))
    case("root-cause: an unzoned start", True, probe("two zoned ISO times", run={**run, "started": "2026-10-15T05:00:00"}))
    case("root-cause: finished before started", True,
         probe("two zoned ISO times", run={**run, "finished": (t0 - datetime.timedelta(days=1)).isoformat()}))
    case("root-cause: a run longer than the limit", True,
         probe("two zoned ISO times", run={**run, "finished": (t0 + datetime.timedelta(hours=2)).isoformat()}))
    late = copy.deepcopy(run)
    late["observations"][0]["at"] = (t0 + datetime.timedelta(hours=1)).isoformat()
    case("root-cause: an observation outside the run", True, probe("outside the run", run=late))
    case("root-cause: a PNG written outside the run", True,
         probe("not written during the run", mtimes={**mtimes, p0: t0.timestamp() - 3600}))
    case("root-cause: a missing PNG", True, probe("is not a capture: missing", pngs={**pngs, p0: None}))
    case("root-cause: a header-only PNG", True, probe("is not a capture", first(_png_header_only(320, 200))))
    bad = bytearray(_png(320, 200))
    bad[-20] ^= 0xFF
    case("root-cause: a PNG with a bad CRC", True, probe("bad CRC", first(bytes(bad))))
    short = _png(320, 100)
    ihdr = struct.pack(">IIBBBBB", 320, 200, 8, 6, 0, 0, 0)
    short = short[:16] + ihdr + struct.pack(">I", zlib.crc32(b"IHDR" + ihdr) & 0xFFFFFFFF) + short[33:]
    case("root-cause: image data shorter than IHDR declares", True, probe("image data is", first(short)))
    case("root-cause: a capture not the window's size", True, probe("the captured window is", first(_png(640, 400))))
    case("root-cause: a one-byte PNG", True, probe("no PNG signature", first(b"x")))
    case("root-cause: a wrong-hash PNG", True,
         probe("does not match its recorded sha256", pngs={**pngs, p0: _png(320, 200, seed=99)}))
    case("root-cause: 16x16 window captures", True,
         probe("at least 320x200", fixture(win={"x": 100, "y": 100, "width": 16, "height": 16},
                                           rect={"x": 101, "y": 101, "width": 4, "height": 4}, cursor={"x": 102, "y": 102})))
    outside = copy.deepcopy(run)
    outside["observations"][0]["rect"] = {"x": 900, "y": 900, "width": 40, "height": 30}
    outside["observations"][0]["cursor"] = {"x": 910, "y": 910}
    case("root-cause: a target outside the captured window", True, probe("not inside the captured window", run=outside))
    case("root-cause: a run on another head", True, probe("(need 0, baseline", run={**run, "head": "b" * 40}))
    case("root-cause: a dirty tree at probe time", True, probe("(need 0, baseline", run={**run, "gated_clean": False}))
    case("root-cause: a failed probe", True, probe("(need 0, baseline", run={**run, "exit": 1}))
    off = copy.deepcopy(run)
    off["observations"][0]["cursor"] = {"x": 10, "y": 10}
    case("root-cause: the cursor off target", True, probe("not inside the target rect", run=off))
    untitled = copy.deepcopy(run)
    untitled["observations"][1]["title"] = ""
    case("root-cause: a target with no title", True, probe("had no title attribute", run=untitled))
    case("root-cause: five observations", True, probe("(need H1-H3", run={**run, "observations": obs[:5]}))
    case("root-cause: a placeholder observation line", True,
         probe("6 observation lines",
               body=body.replace("tooltip-visible no — s34-probe-h1-nav", "tooltip-visible yes|no — s34-probe-h1-nav")))
    case("root-cause: no finding line", True, probe("one finding", body="\n".join(lines)))
    case("root-cause: a placeholder finding", True, probe("one finding", body="\n".join(lines) + "\n- finding: tbd\n"))

    ident = "F" * 64
    full = " ".join(f"AC-80.{n}" for n in range(1, 14)) + f" identity {ident}"
    case("handoff-cases: well-formed", False, eval_handoff(full, "80", ident))
    case("handoff-cases: only AC-80", True, eval_handoff(f"AC-80 all covered; identity {ident}", "80", ident))
    case("handoff-cases: a range instead of ids", True, eval_handoff(f"AC-80.1–80.13 {ident}", "80", ident))
    case("handoff-cases: no identity", True, eval_handoff(full.replace(ident, ""), "80", ident))

    hits = [("ui/tests/unit/a.test.ts", 12), ("ui/tests/unit/a.test.ts", 40)]
    case("census: well-formed", False, eval_census(hits, "- ui/tests/unit/a.test.ts:10-45 — TA-3\n"))
    case("census: a fixture (a) disposition", False, eval_census(
        [("ui/tests/unit/f.json", 3)], "- `ui/tests/unit/f.json:3` → fixture (a) (the kebab title).\n"))
    case("census: a wildcard", True, eval_census(hits, "- ui/tests/unit/a.test.ts:* — unaffected, ids only\n"))
    case("census: an uncovered hit", True, eval_census(hits, "- ui/tests/unit/a.test.ts:12 — TA-3\n"))
    case("census: a new-contradiction", True, eval_census(hits, "- ui/tests/unit/a.test.ts:10-45 — new-contradiction\n"))

    order = ["ui-tests", "ui-electron"]
    g = {"schema": "s34-gate.v2", "identity_before": ident, "identity_after": ident, "pytest": {"passed": 700, "failed": 0},
         "stages": [{"id": "ui-tests", "exit": 0, "raw_exit": 1}, {"id": "ui-electron", "exit": 0}]}
    late = [(TA_FILE[n], f"amended case [TA-{n}]", "expected", None) for n in sorted(TA_LATE)]
    vj, ej = _vjson(green, total=800), _ejson(e_ok + late, expected=140)
    reports = {"vitest_json": "1" * 64, "vitest_txt": "2" * 64, "e2e_json": "3" * 64}
    g = {**g, "check": "gate", **{f"{k}_sha256": v.upper() for k, v in reports.items()}}

    def gate(g, order, vj, vtxt, ej, fresh, current=reports):
        return eval_gate(g, order, vj, vtxt, ej, fresh, current)

    case("gate-check: well-formed", False, gate(g, order, vj, gtxt, ej, ident))
    case("gate-check: no producer (not written by -Check gate)", True,
         gate({k: v for k, v in g.items() if k != "check"}, order, vj, gtxt, ej, ident))
    case("gate-check: a report replaced after the gate", True,
         gate(g, order, vj, gtxt, ej, ident, {**reports, "vitest_json": "4" * 64}))
    case("gate-check: a named report missing", True, gate(g, order, vj, gtxt, ej, ident, {**reports, "e2e_json": None}))
    case("gate-check: no recorded report hash", True,
         gate({k: v for k, v in g.items() if k != "vitest_txt_sha256"}, order, vj, gtxt, ej, ident))
    case("gate-check: a stage out of order", True, gate({**g, "stages": g["stages"][::-1]}, order, vj, gtxt, ej, ident))
    case("gate-check: the tree changed after the gate", True, gate(g, order, vj, gtxt, ej, "0" * 64))
    case("look-check/handoff-cases: the bound gate record", False, eval_gate_binding(g, reports))
    case("look-check/handoff-cases: a gate record with no producer", True,
         eval_gate_binding({k: v for k, v in g.items() if k != "check"}, reports))
    case("gate-check: an AC case missing from the raw report", True,
         gate(g, order, _vjson(green[:2] + green[3:], total=800), gtxt, ej, ident))
    case("gate-check: below COUNT_FLOORS", True, gate(g, order, _vjson(green, total=10), gtxt, ej, ident))
    case("gate-check: v1 schema", True, gate({**g, "schema": "s34-gate.v1"}, order, vj, gtxt, ej, ident))
    case("gate-check: a TA_LATE tag missing (A-9)", True,
         gate(g, order, vj, gtxt, _ejson(e_ok + late[:1], expected=140), ident))
    return out


def cmd_selftest(args: argparse.Namespace) -> None:
    bad = []
    results = selftest_cases()
    for name, refuse, errors in results:
        ok = bool(errors) == refuse
        verdict = "refuses" if errors else "passes"
        print(f"{'ok ' if ok else 'BAD'} {name}: {verdict}{' — ' + errors[0][:110] if errors else ''}")
        if not ok:
            bad.append(f"{name}: expected {'a refusal' if refuse else 'a pass'}, got {errors[:2]}")
    refusals = sum(r for _n, r, _e in results)
    report(bad, f"selftest: {len(results)} synthetic inputs; {refusals} refusals refused; "
                f"{len(results) - refusals} well-formed inputs passed")


# ---------------------------------------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("static", "selftest", "identity", "clean", "task-state", "ssot-review-state", "post-review",
                 "handoff-cases"):
        sub.add_parser(name)
    for name in ("registry", "fixture", "scope", "hub"):
        sub.add_parser(name).add_argument("--baseline", required=True)
    for name in ("vitest-red", "vitest-ok", "e2e-red", "e2e-ok"):
        p = sub.add_parser(name)
        p.add_argument("--json", required=True)
        p.add_argument("--rc", type=int, required=True)
        p.add_argument("--meu", choices=("80", "81"), required=name.endswith("-red"))
        if name.startswith("vitest"):
            p.add_argument("--txt", required=True, help="the default-reporter text receipt")
        if name == "e2e-ok":
            p.add_argument("--tags", action="store_true", help="also require the MEUs' Electron TA_TAGS specs")
            p.add_argument("--ac", action="append", help="an AC case the run must hold (repeat runs)")
    for name in ("gate-check", "look-check"):
        sub.add_parser(name).add_argument("--result", required=True)
    p = sub.add_parser("review-check")
    p.add_argument("--review", required=True)
    p.add_argument("--loop-id", required=True)
    sub.add_parser("root-cause").add_argument("--run", default="C:/Temp/av-kit/s34-probe-run.json")
    sub.add_parser("census-check").add_argument("--census", required=True)
    sub.add_parser("meu-state").add_argument("--want", action="append", required=True)
    choices = list(sub.choices)
    args = parser.parse_args()
    if args.command == "static":
        cmd_static(args, choices)
    else:
        globals()["cmd_" + args.command.replace("-", "_")](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
