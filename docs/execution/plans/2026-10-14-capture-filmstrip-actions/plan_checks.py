"""Plan-local verifier for 2026-10-14-capture-filmstrip-actions (Session 38).

``validate-task.ps1`` orchestrates the tools; this module holds every check that reads a report,
a plan file or git state. It writes nothing except ``baseline-counts`` (its named output), and it
never runs product code. ``static`` and ``selftest`` are stdlib-only and may run before plan
approval (a reviewer may run them). The state checks import ``yaml`` and run under ``uv run``.

Usage (from the worktree root)::

    python plan_checks.py static
    python plan_checks.py selftest
    python plan_checks.py vitest <id> <json> <exit> <receipt>
    python plan_checks.py vitest-red <MEU-88|MEU-89> <json> <receipt>
    python plan_checks.py e2e <id> <json> <exit>
    python plan_checks.py e2e-red <MEU-88|MEU-89> <json>
    python plan_checks.py baseline-counts <vitest.json> <e2e.json>
    python plan_checks.py floors <vitest.json> <e2e.json> <vitest-receipt>
    python plan_checks.py task-state
    python plan_checks.py scope
    python plan_checks.py hub
    uv run python plan_checks.py prereq | ssot-review | post-review-state
    python plan_checks.py review-check <review-file> <plan|execution> <cap>
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

PLAN_DIR = Path("docs/execution/plans/2026-10-14-capture-filmstrip-actions")
PLAN = PLAN_DIR / "implementation-plan.md"
TASK = PLAN_DIR / "task.md"
PS1 = PLAN_DIR / "validate-task.ps1"
BASELINE_SHA = PLAN_DIR / "baseline.sha"
BASELINE_COUNTS = PLAN_DIR / "baseline-counts.json"
GROUPING = Path(".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md")
TARGET_PLAN = PLAN.as_posix()

ALLOWED_STRATEGIES = {"shared", "compact_continue", "isolated"}
ALLOWED_BUILDERS = {"`avkit_builder`", "`avkit_coordinator`", "`avkit_verifier`", "—"}

# Red: files that may fail to load, or fail on a missing symbol, because they import a module or
# export this MEU creates. Every other failure must be an assertion failure.
NEW_MODULE_FILES = {
    "MEU-88": ("capture-clipboard.test.ts", "clipboard-image-main.test.ts"),
    "MEU-89": ("capture-filmstrip-select.test.ts", "capture-batch-delete.test.ts"),
}
# TEST_AMENDMENTS TA-1/TA-2: the only pre-existing tests allowed to fail in Red (MEU-88 only).
TA_FILES = {"MEU-88": ("ipc-strict-census.test.ts", "login-item-ipc.test.ts"), "MEU-89": ()}
MISSING_SYMBOL = re.compile(
    r"Failed to resolve import|Cannot find module|does not provide an export named|is not a function|is not defined"
)
FROZEN = ("packages", "mcp-server", "tools", "native", "openapi.committed.json", "docs/build-plan/11-page-layout.md")
MAIN_ALLOWED = {
    "ui/src/main/ipc.ts", "ui/src/main/index.ts", "ui/src/main/preload.ts", "ui/src/main/clipboard-image.ts",
}
ACTION_ROWS = ("capture:copy_path", "capture:copy_image", "capture:menu_delete", "capture:batch_delete")
# BASELINE_RED: the one test main fails before this plan. queue-canon reads P:/zorivest's live globals.css, whose
# light accent-cyan moved to #0e7490; Session 31 da1d111 (unmerged) ports it. It may fail (never must), only with
# this message; it stops failing once Session 31 merges and this branch takes it.
BASELINE_RED = ("queue-canon.test.ts", "AC-41.3", "--color-accent-cyan light diverges from PILL_TOKEN_SOURCE")


# Vitest's JSON reporter drops unhandled errors (they only set the exit code). Every Vitest run in this plan
# also uses the default reporter, whose text receipt prints this banner and summary line when they occur.
UNHANDLED = re.compile(r"Unhandled (?:Errors?|Rejection)|^\s*Errors\s+\d+ errors?\s*$", re.M)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
# PRODUCT_SCOPE: besides the Files Modified rows, only this plan's own closeout outputs may change.
CLOSEOUT_PREFIXES = (
    PLAN_DIR.as_posix() + "/",
    ".agent/context/handoffs/2026-10-14-capture-filmstrip-actions-",
    "docs/execution/reflections/2026-10-14-capture-filmstrip-actions-",
)
CLOSEOUT_RENDERED = {".agent/context/meu-registry.md", ".agent/context/known-issues.md",
                     ".agent/context/known-issues-archive.md"}


def unhandled_errors(receipt_text: str) -> list[str]:
    text = ANSI.sub("", receipt_text)
    return [m.group(0).strip() for m in UNHANDLED.finditer(text)]


def receipt_unhandled(receipt: str) -> list[str]:
    path = Path(receipt)
    if not path.exists():
        return [f"receipt {receipt} missing"]
    return unhandled_errors(path.read_text(encoding="utf-8", errors="replace"))


def is_baseline_red(file: str, name: str, msgs: list[str]) -> bool:
    base = file.replace("\\", "/").rsplit("/", 1)[-1]
    return base == BASELINE_RED[0] and BASELINE_RED[1] in name and any(BASELINE_RED[2] in m for m in msgs)


HELP_SENTENCE = (
    "Right-click a thumbnail (or press Shift+F10) to copy its path or image, or delete it; "
    "Shift-click selects a range to delete together."
)


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def read(path: Path | str) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        raise SystemExit(f"FAIL: report missing: {path}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


# ---------------------------------------------------------------- plan ACs


def plan_acs(plan: str) -> dict[str, str]:
    """AC id -> type cell, from the plan's AC tables."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^\| (AC-8[89]\.\d+) \| ([^|]+) \|", plan, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def ac_pattern(ac: str) -> re.Pattern[str]:
    return re.compile(re.escape(ac) + r"(?![0-9])")


def electron_acs(plan: str) -> set[str]:
    return {a for a, t in plan_acs(plan).items() if "Electron" in t}


# ---------------------------------------------------------------- Vitest


def _vitest_failed(j: dict) -> list[tuple[str, str, list[str]]]:
    out = []
    for suite in j.get("testResults", []):
        for a in suite.get("assertionResults", []):
            if a.get("status") == "failed":
                out.append((suite.get("name", ""), a.get("fullName", ""), a.get("failureMessages", [])))
    return out


def vitest_ok(rid: str, path: str, rc: int, receipt: str) -> int:
    j = load_json(path)
    unhandled = receipt_unhandled(receipt)
    if unhandled:
        return fail(f"{rid} unhandled errors in {receipt}: {unhandled[:3]}")
    loads = [s["name"] for s in j.get("testResults", []) if s.get("message")]
    if loads:
        return fail(f"{rid} suite load errors {loads}")
    if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
        return fail(f"{rid} pending/todo tests present")
    all_failed = _vitest_failed(j)
    known = [f for f in all_failed if is_baseline_red(*f)]
    failed = [f for f in all_failed if f not in known]
    if failed:
        return fail(f"{rid} failing tests: {[f[1][:90] for f in failed]}")
    if rc != 0 and not known:
        return fail(f"{rid} exit {rc} with no failed test (runner error)")
    note = f"; BASELINE_RED tolerated: {[f[1][:60] for f in known]}" if known else ""
    print(f"PASS {rid}: {j.get('numPassedTests')} passed of {j.get('numTotalTests')}{note}")
    return 0


def _since(ac: str, since: int) -> bool:
    """D-25 rework Red: only ACs numbered `since` or above must be red (the earlier ones are green)."""
    return int(ac.rsplit(".", 1)[1]) >= since


def vitest_red(meu: str, path: str, receipt: str, since: int = 0) -> int:
    j = load_json(path)
    unhandled = receipt_unhandled(receipt)
    if unhandled:
        return fail(f"{meu} Red has unhandled errors (not assertion failures) in {receipt}: {unhandled[:3]}")
    num = meu.split("-")[1]
    tag = f"AC-{num}."
    newf = NEW_MODULE_FILES[meu]
    tolerated_files: set[str] = set()
    for s in j.get("testResults", []):
        msg = s.get("message") or ""
        if not msg:
            continue
        if s["name"].replace("\\", "/").endswith(newf) and MISSING_SYMBOL.search(msg):
            tolerated_files.add(s["name"].replace("\\", "/").rsplit("/", 1)[-1])
            continue
        return fail(f"{meu} load/collection error in {s['name']}: {msg[:200]}")
    if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
        return fail(f"{meu} pending/todo tests present")
    decisive, tolerated, amended, bad = [], [], [], []
    for file, name, msgs in _vitest_failed(j):
        base = file.replace("\\", "/").rsplit("/", 1)[-1]
        text = " ".join(msgs)
        if base in newf and MISSING_SYMBOL.search(text):
            tolerated.append(name)
        elif tag in name and re.search(r"expected|AssertionError|assert", text, re.I):
            decisive.append(name)
        elif base in TA_FILES[meu] and re.search(r"expected|AssertionError", text, re.I):
            amended.append(name)
        else:
            bad.append(f"{name[:80]}: {text[:120]}")
    if bad:
        return fail(f"{meu} non-assertion or out-of-scope failures (S4): {bad[:5]}")
    if not decisive:
        return fail(f"{meu} no failing {tag} assertion")
    plan = read(PLAN)
    want = {a for a in plan_acs(plan) if a.startswith(tag) and a not in electron_acs(plan) and _since(a, since)}
    red_names = decisive + tolerated
    missing = sorted(a for a in want if not any(ac_pattern(a).search(n) for n in red_names)
                     and not any(f in tolerated_files for f in newf if _ac_in_file(a, f)))
    if missing:
        return fail(f"{meu} ACs with no Red test: {missing}")
    print(f"PASS {meu} Vitest RED: {len(decisive)} assertion failures, {len(tolerated)} missing-symbol, "
          f"load-tolerated files {sorted(tolerated_files)}, TA pins failing {amended}")
    return 0


def _ac_in_file(ac: str, base: str) -> bool:
    path = Path("ui/tests/unit") / base
    return path.exists() and bool(ac_pattern(ac).search(read(path)))


# ---------------------------------------------------------------- Playwright


def _specs(suite: dict, file: str = ""):
    file = suite.get("file", file)
    for spec in suite.get("specs", []):
        yield file, spec
    for child in suite.get("suites", []):
        yield from _specs(child, file)


def _spec_status(spec: dict) -> tuple[str, list[str]]:
    msgs, status = [], "passed"
    for test in spec.get("tests", []):
        if test.get("status") in ("unexpected", "flaky"):
            status = test["status"]
        elif test.get("status") == "skipped" and status == "passed":
            status = "skipped"
        for res in test.get("results", []):
            msgs += [e.get("message", "") for e in res.get("errors", [])]
            msgs.append((res.get("error") or {}).get("message", ""))
    return status, msgs


def e2e_ok(rid: str, path: str, rc: int) -> int:
    j = load_json(path)
    if j.get("errors"):
        return fail(f"{rid} top-level Playwright errors {j['errors'][:1]}")
    stats = j.get("stats", {})
    if stats.get("unexpected", 0) or stats.get("flaky", 0):
        bad = [f"{f}: {s.get('title')}" for t in j.get("suites", []) for f, s in _specs(t)
               if _spec_status(s)[0] in ("unexpected", "flaky")]
        return fail(f"{rid} unexpected/flaky specs (flaky counts as a failure): {bad}")
    if rc != 0:
        return fail(f"{rid} exit {rc} with no failed spec (runner error)")
    print(f"PASS {rid}: expected {stats.get('expected')} skipped {stats.get('skipped')}")
    return 0


def e2e_red(meu: str, path: str, since: int = 0) -> int:
    j = load_json(path)
    if j.get("errors"):
        return fail(f"{meu} E2E top-level errors (collection/launch): {j['errors'][:1]}")
    num = meu.split("-")[1]
    want = {a for a in electron_acs(read(PLAN)) if a.startswith(f"AC-{num}.") and _since(a, since)}
    red = set()
    for top in j.get("suites", []):
        for _, spec in _specs(top):
            status, msgs = _spec_status(spec)
            for a in want:
                if ac_pattern(a).search(spec.get("title", "")) and status == "unexpected" and any(
                        "expect(" in m or "Expected" in m for m in msgs):
                    red.add(a)
    if red != want:
        return fail(f"{meu} Electron ACs without an expect() Red: {sorted(want - red)}")
    print(f"PASS {meu} E2E RED: {sorted(red)}")
    return 0


# ---------------------------------------------------------------- COUNT_FLOORS


def baseline_counts(vjson: str, ejson: str) -> int:
    v, e = load_json(vjson), load_json(ejson)
    counts = {
        "vitest_passed": v.get("numPassedTests"), "vitest_failed": v.get("numFailedTests"),
        "e2e_expected": e["stats"].get("expected"), "e2e_skipped": e["stats"].get("skipped"),
        "e2e_unexpected": e["stats"].get("unexpected"), "e2e_flaky": e["stats"].get("flaky"),
    }
    counts["vitest_baseline_red"] = sum(1 for f in _vitest_failed(v) if is_baseline_red(*f))
    if counts["vitest_failed"] - counts["vitest_baseline_red"] or counts["e2e_unexpected"] or counts["e2e_flaky"]:
        return fail(f"baseline is not green: {counts}")
    BASELINE_COUNTS.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(f"PASS baseline counts {counts}")
    return 0


def floors(vjson: str, ejson: str, vreceipt: str) -> int:
    if not BASELINE_COUNTS.exists():
        return fail("baseline-counts.json missing (row 0)")
    unhandled = receipt_unhandled(vreceipt)
    if unhandled:
        return fail(f"vitest unhandled errors in {vreceipt}: {unhandled[:3]}")
    base = json.loads(read(BASELINE_COUNTS))
    v, e = load_json(vjson), load_json(ejson)
    plan = read(PLAN)
    acs = plan_acs(plan)
    eacs = electron_acs(plan)
    passed_names = [a.get("fullName", "") for s in v.get("testResults", []) for a in s.get("assertionResults", [])
                    if a.get("status") == "passed"]
    new_vitest = [n for n in passed_names if re.search(r"AC-8[89]\.\d", n)]
    spec_titles = [s.get("title", "") for t in e.get("suites", []) for _, s in _specs(t)
                   if _spec_status(s)[0] == "passed"]
    new_e2e = [t for t in spec_titles if re.search(r"AC-8[89]\.\d", t)]
    errs = []
    for a in acs:
        pool = new_e2e if a in eacs else new_vitest
        if not any(ac_pattern(a).search(n) for n in pool):
            errs.append(f"{a} has no passing test")
    real = [f[1][:80] for f in _vitest_failed(v) if not is_baseline_red(*f)]
    if real or v.get("numFailedTests", 0) > base.get("vitest_baseline_red", 0):
        errs.append(f"vitest failed {v.get('numFailedTests')} (BASELINE_RED allows {base.get('vitest_baseline_red', 0)}): {real}")
    if v.get("numPassedTests", 0) < base["vitest_passed"] + len(new_vitest):
        errs.append(f"vitest passed {v.get('numPassedTests')} < {base['vitest_passed']} + {len(new_vitest)}")
    st = e.get("stats", {})
    if st.get("unexpected", 0) or st.get("flaky", 0):
        errs.append(f"e2e unexpected {st.get('unexpected')} flaky {st.get('flaky')}")
    if st.get("expected", 0) < base["e2e_expected"] + len(new_e2e):
        errs.append(f"e2e expected {st.get('expected')} < {base['e2e_expected']} + {len(new_e2e)}")
    if st.get("skipped", 0) > base["e2e_skipped"]:
        errs.append(f"e2e skipped {st.get('skipped')} > baseline {base['e2e_skipped']}")
    if errs:
        return fail(f"COUNT_FLOORS: {errs}")
    print(f"PASS COUNT_FLOORS: vitest {v.get('numPassedTests')} (baseline {base['vitest_passed']}, "
          f"+{len(new_vitest)} AC tests), e2e {st.get('expected')} (baseline {base['e2e_expected']}, +{len(new_e2e)})")
    return 0


# ---------------------------------------------------------------- task.md


def task_rows(task: str) -> list[list[str]]:
    rows = []
    task = task.split("### Row Evidence", 1)[0]  # the Status Legend table is not a task row
    for line in task.splitlines():
        if not line.startswith("| ") or line.startswith("| #") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells[0]:
            continue  # phase divider
        rows.append(cells)
    return rows


def check_static() -> int:
    task, plan, ps1 = read(TASK), read(PLAN), read(PS1)
    errs: list[str] = []
    rows = task_rows(task)
    ids = [r[0].strip("`") for r in rows]
    if len(ids) != len(set(ids)):
        errs.append("duplicate row ids")
    for r in rows:
        if len(r) != 10:
            errs.append(f"row {r[0]} has {len(r)} cells")
            continue
        rid, deps, strat, durable, builder = r[0], r[5], r[6], r[7], r[8]
        for d in re.split(r",\s*", deps):
            if d not in ("—", "") and d not in ids:
                errs.append(f"row {rid} depends on unknown {d}")
        if strat not in ALLOWED_STRATEGIES:
            errs.append(f"row {rid} strategy {strat}")
        if strat != "shared" and not durable:
            errs.append(f"row {rid} non-shared without durable output")
        if strat == "isolated" and "compact_continue" not in durable:
            errs.append(f"row {rid} isolated without compact_continue fallback")
        if builder not in ALLOWED_BUILDERS:
            errs.append(f"row {rid} builder {builder}")
    graph = {r[0]: [d for d in re.split(r",\s*", r[5]) if d in ids] for r in rows if len(r) == 10}
    seen: set[str] = set()

    def visit(n: str, path: tuple[str, ...]) -> None:
        if n in path:
            errs.append(f"dependency cycle {path + (n,)}")
            return
        if n in seen:
            return
        seen.add(n)
        for d in graph.get(n, []):
            visit(d, path + (n,))

    for n in graph:
        visit(n, ())
    checks = set(re.findall(r"validate-task\.ps1 -Check ([a-z0-9-]+)", task))
    impl = set(re.findall(r"^\s*'([a-z0-9-]+)' \{", ps1, re.M))
    for c in sorted(checks - impl):
        errs.append(f"task.md invokes -Check {c}, which validate-task.ps1 does not implement")
    pc_cmds = set(re.findall(r"Invoke-PlanCheck '([a-z-]+)'", ps1)) | set(re.findall(r"python \$pc ([a-z-]+) ", ps1))
    known = {"static", "selftest", "vitest", "vitest-red", "e2e", "e2e-red", "baseline-counts", "floors",
             "task-state", "scope", "hub", "prereq", "ssot-review", "post-review-state", "review-check"}
    for c in sorted(pc_cmds - known):
        errs.append(f"validate-task.ps1 calls unknown plan_checks command {c}")
    # Every plan AC is named in a task row, singly or inside an AC-n.a–n.b range.
    acs = plan_acs(plan)
    covered: set[str] = set()
    for m in re.finditer(r"AC-(8[89])\.(\d+)(?:[–-](?:8[89]\.)?(\d+))?", task):
        lo = int(m.group(2))
        hi = int(m.group(3)) if m.group(3) else lo
        covered |= {f"AC-{m.group(1)}.{i}" for i in range(lo, hi + 1)}
    for a in sorted(set(acs) - covered):
        errs.append(f"{a} is not named in any task row")
    # Every D-n, TA-n, S-n referenced in task.md is defined in the plan (or grouping D-1..D-7).
    defined_d = {int(x) for x in re.findall(r"^  - id: D-(\d+)$", plan, re.M)} | set(range(1, 8))
    for d in sorted({int(x) for x in re.findall(r"\bD-(\d+)\b", task)} - defined_d):
        errs.append(f"task.md cites D-{d}, which no decision defines")
    for ta in sorted(set(re.findall(r"\bTA-(\d+)\b", task)) - set(re.findall(r"\*\*TA-(\d+):\*\*", plan))):
        errs.append(f"task.md cites TA-{ta}, which TEST_AMENDMENTS does not define")
    for s in sorted(set(re.findall(r"\bS(\d)\b", task)) - set(re.findall(r"^\| S(\d) \|", plan, re.M))):
        errs.append(f"task.md cites S{s}, which Stop Conditions does not define")
    # Contract names used in task.md exist in the contracts table.
    contracts = set(re.findall(r"^\| `([A-Z_]+|rangeBetween)` \|", plan, re.M))
    contracts |= {n for row in re.findall(r"^\| `([A-Z_]+)` / `([A-Z_]+)` / `([A-Z_]+)` \|", plan, re.M) for n in row}
    for name in sorted(set(re.findall(r"`([A-Z][A-Z0-9]*_[A-Z0-9_]+)`", task)) - contracts):
        errs.append(f"task.md names `{name}`, which the contracts table does not define")
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        return 1
    print(f"PASS static: {len(rows)} rows, {len(checks)} -Check names, {len(acs)} ACs covered")
    return 0


def task_state() -> int:
    rows = [r for r in task_rows(read(TASK)) if r[0].isdigit()]
    if len(rows) != 10:
        return fail(f"expected 10 implementation rows (0-9), got {len(rows)}")
    for r in rows:
        s = r[-1].strip("`")
        if s == "[x]" or (s == "[B]" and "follow-up" in r[1] and "B-" in r[1]):
            continue
        return fail(f"unfinished row {r[0]}: {s}")
    print("PASS implementation rows 0-9")
    return 0


# ---------------------------------------------------------------- scope / hub


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def changed(base: str, *paths: str) -> set[str]:
    out = set(_git("diff", "--name-only", base, "--", *paths).split())
    for line in _git("status", "--porcelain", "--untracked-files=all", "--", *paths).splitlines():
        out.add(line[3:].strip().strip('"'))
    return out


def listed_files(plan: str) -> set[str]:
    out: set[str] = set()
    for m in re.finditer(r"^\| ([^|]+) \| (?:new|modify)[^|]*\|", plan, re.M):
        out |= set(re.findall(r"`([^`]+)`", m.group(1)))
    return out


def scope_violations(paths: set[str], listed: set[str]) -> list[str]:
    """Every changed path in the repository must be a Files Modified row or this plan's closeout output."""
    errs = []
    frozen = sorted(p for p in paths if any(p == f or p.startswith(f + "/") for f in FROZEN))
    if frozen:
        errs.append(f"PRODUCT_SCOPE frozen paths changed: {frozen}")
    main = sorted(p for p in paths if p.startswith("ui/src/main/") and p not in MAIN_ALLOWED)
    if main:
        errs.append(f"ui/src/main files outside the four named: {main}")
    extra = sorted(p for p in paths if p not in listed and p not in CLOSEOUT_RENDERED
                   and not p.startswith(CLOSEOUT_PREFIXES))
    if extra:
        errs.append(f"changes outside the Files Modified tables and closeout outputs: {extra}")
    return errs


def scope() -> int:
    if not BASELINE_SHA.exists():
        return fail("baseline.sha missing (row 0)")
    base = read(BASELINE_SHA).strip()
    paths = changed(base)
    errs = scope_violations(paths, listed_files(read(PLAN)))
    if errs:
        return fail("; ".join(errs))
    print(f"PASS scope: {len(paths)} changed paths since {base[:8]}, all listed or closeout; frozen paths unchanged")
    return 0


def hub() -> int:
    errs = []
    g06 = read("docs/build-plan/06-gui.md")
    if "writeClipboardImage: (png: Uint8Array) => ipcRenderer.invoke('write-clipboard-image', { png })" not in g06:
        errs.append("06 preload listing lacks the writeClipboardImage line")
    g09 = read("docs/build-plan/09-screenshot-capture.md")
    menu = g09.split("Filmstrip context menu", 1)[-1].split("Filmstrip multi-select", 1)[0]
    multi = g09.split("Filmstrip multi-select", 1)[-1][:3000]
    for sect, text, needs in (("context menu", menu, ("Session 38 plan", "D-10", "D-11")),
                              ("multi-select", multi, ("Session 38 plan", "D-15", "D-18", "D-25"))):
        for n in needs:
            if n not in text:
                errs.append(f"09 §Filmstrip {sect} note lacks {n!r}")
    idx = read("docs/build-plan/gui-actions-index.md")
    for a in ACTION_ROWS:
        if f"| `{a}` |" not in idx:
            errs.append(f"gui-actions-index lacks {a}")
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        return 1
    print("PASS hub reconciliation")
    return 0


# ---------------------------------------------------------------- state (uv run; yaml)


def _meus() -> dict[str, dict]:
    import yaml  # noqa: PLC0415 - only the state checks need it

    return {r["id"]: r for r in yaml.safe_load(read(".agent/context/meu-status.yaml"))["meus"]}


def prereq() -> int:
    rows = _meus()
    want = {"MEU-57": "approved", "MEU-88": "pending", "MEU-89": "pending"}
    bad = {k: rows.get(k, {}).get("status") for k, v in want.items() if rows.get(k, {}).get("status") != v}
    if bad:
        return fail(f"MEU state (S1): {bad}")
    for k in ("MEU-88", "MEU-89"):
        if rows[k].get("execution_plan") != PLAN_DIR.as_posix():
            return fail(f"{k} execution_plan is {rows[k].get('execution_plan')!r}")
    print(f"PASS MEU state {want}; execution_plan set")
    return 0


def ssot_review() -> int:
    rows = _meus()
    for k in ("MEU-88", "MEU-89"):
        if rows[k]["status"] != "ready_for_review":
            return fail(f"{k} is {rows[k]['status']}")
    if not re.search(r"^\| 38 \| `capture-filmstrip-actions` \| MEU-88, MEU-89 \| P4 \| in review \|", read(GROUPING), re.M):
        return fail("grouping Session 38 row is not 'in review'")
    focus = read(".agent/context/current-focus.md")
    if "capture-filmstrip-actions" not in focus or "ready_for_review" not in focus:
        return fail("current-focus.md does not record Session 38 ready_for_review")
    print("PASS SSOT review state")
    return 0


def post_review_state() -> int:
    import yaml  # noqa: PLC0415

    rows = _meus()
    for k in ("MEU-88", "MEU-89"):
        if rows[k]["status"] != "approved":
            return fail(f"{k} is {rows[k]['status']}")
    issues = {i["id"]: i for i in yaml.safe_load(read(".agent/context/known-issues.yaml"))["issues"]}
    for i in ("CAPTURE-FILMSTRIP-CONTEXT-MENU", "CAPTURE-FILMSTRIP-MULTISELECT"):
        it = issues.get(i) or {}
        ev = (it.get("verification") or {}).get("evidence_file") or ""
        if it.get("status") != "resolved" or not ev.startswith(PLAN_DIR.as_posix()):
            return fail(f"{i} status {it.get('status')} evidence {ev!r}")
    if not re.search(r"^\| 38 \| `capture-filmstrip-actions` \| MEU-88, MEU-89 \| P4 \| approved \|", read(GROUPING), re.M):
        return fail("grouping Session 38 row is not approved")
    if "2026-10-14-capture-filmstrip-actions" not in read("docs/execution/metrics.md"):
        return fail("metrics row missing")
    print("PASS POST_REVIEW_STATE")
    return 0


def same_target(value: str, root: Path) -> bool:
    """True if value names this checkout's plan, repo-relative or absolute (review F6)."""
    if not value:
        return False
    v = Path(value)
    v = v if v.is_absolute() else root / v
    return os.path.normcase(os.path.normpath(v)) == os.path.normcase(os.path.normpath(root / PLAN))


def review_check(path: str, mode: str, cap: int) -> int:
    t = read(path)
    fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?$', t.split("---")[1], re.M))
    if not same_target(fm.get("target_plan", ""), Path.cwd().resolve()):
        return fail(f"target_plan {fm.get('target_plan')}")
    if fm.get("review_mode") != mode:
        return fail(f"review_mode {fm.get('review_mode')}")
    if int(fm.get("round", "0")) > cap:
        return fail(f"round {fm.get('round')} over cap {cap}")
    if fm.get("verdict") != "approved":
        return fail(f"verdict {fm.get('verdict')}")
    # Authorized route: Codex CLI, class avkit_independent_reviewer (implementation-plan.md §Harness).
    if not fm.get("agent", "").startswith("gpt-"):
        return fail(f"agent {fm.get('agent')} is not the Codex reviewer route")
    print(f"PASS {mode} review approved, round {fm['round']}, agent {fm['agent']}")
    return 0


# ---------------------------------------------------------------- selftest


def selftest() -> int:
    assert ac_pattern("AC-88.1").search("AC-88.1 menu") and not ac_pattern("AC-88.1").search("AC-88.12 e2e")
    sample = "| AC-88.1 | integration | x |\n| AC-88.12 | integration (Electron) | y |\n"
    assert plan_acs(sample) == {"AC-88.1": "integration", "AC-88.12": "integration (Electron)"}
    assert electron_acs(sample) == {"AC-88.12"}
    rows = task_rows("| # | h |\n|---|---|\n| | **divider** | | | | | | | | |\n| 0 | a | b | c | d | — | shared | e | — | `[ ]` |\n")
    assert [r[0] for r in rows] == ["0"]
    lf = listed_files("| `ui/a.ts` | new | s |\n| `x.yaml`, `y.md` (rendered) | modify | s |\n| `ui/b.ts` | reuse | s |\n")
    assert lf == {"ui/a.ts", "x.yaml", "y.md"}, lf
    assert is_baseline_red("C:/x/ui/tests/unit/queue-canon.test.ts", "Phase 10 > AC-41.3 both themes",
                           ["AssertionError: --color-accent-cyan light diverges from PILL_TOKEN_SOURCE: expected"])
    assert not is_baseline_red("C:/x/ui/tests/unit/queue-canon.test.ts", "AC-41.3 both themes", ["--color-accent-red dark"])
    # F3 negative: the tolerated assertion plus an unhandled rejection must still be caught.
    receipt = ("\x1b[31m\u23af\u23af Unhandled Rejection \u23af\u23af\x1b[39m\nError: boom\n Test Files  1 failed (1)\n"
               "      Tests  1 failed | 3 passed (4)\n     Errors  1 error\n")
    assert len(unhandled_errors(receipt)) == 2, unhandled_errors(receipt)
    assert unhandled_errors(" Test Files  1 failed (1)\n      Tests  1 failed | 3 passed (4)\n") == []
    # F4 negatives: root config, an unlisted test, a frozen path and a fifth main file are refused.
    listed = {"ui/a.ts", "docs/build-plan/09-screenshot-capture.md"}
    ok = {"ui/a.ts", PLAN_DIR.as_posix() + "/gate-result.json", ".agent/context/meu-registry.md",
          ".agent/context/handoffs/2026-10-14-capture-filmstrip-actions-MEU-88-handoff.md"}
    assert scope_violations(ok, listed) == [], scope_violations(ok, listed)
    for bad in ("pyproject.toml", "uv.lock", "ui/tests/unit/other.test.ts", "packages/api/x.py",
                "ui/src/main/tray.ts", ".agent/context/handoffs/2026-10-15-other-handoff.md"):
        assert scope_violations(ok | {bad}, listed | ({bad} if bad == "ui/src/main/tray.ts" else set())), bad
    # F6: relative and absolute targets in this checkout match; another checkout's plan does not.
    wt = Path("P:/av-kit-wt/s38-capture-filmstrip-actions")
    assert same_target(TARGET_PLAN, wt)
    assert same_target((wt / PLAN).as_posix(), wt)
    assert not same_target((Path("P:/av-kit") / PLAN).as_posix(), wt)
    assert not same_target("", wt)
    print("PASS selftest")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, args = argv[0], argv[1:]
    table = {
        "static": lambda: check_static(),
        "selftest": lambda: selftest(),
        "vitest": lambda: vitest_ok(args[0], args[1], int(args[2]), args[3]),
        "vitest-red": lambda: vitest_red(args[0], args[1], args[2], *(int(a) for a in args[3:4])),
        "e2e": lambda: e2e_ok(args[0], args[1], int(args[2])),
        "e2e-red": lambda: e2e_red(args[0], args[1], *(int(a) for a in args[2:3])),
        "baseline-counts": lambda: baseline_counts(args[0], args[1]),
        "floors": lambda: floors(args[0], args[1], args[2]),
        "task-state": lambda: task_state(),
        "scope": lambda: scope(),
        "hub": lambda: hub(),
        "prereq": lambda: prereq(),
        "ssot-review": lambda: ssot_review(),
        "post-review-state": lambda: post_review_state(),
        "review-check": lambda: review_check(args[0], args[1], int(args[2])),
    }
    if cmd not in table:
        print(f"unknown command {cmd}")
        return 2
    return table[cmd]()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
