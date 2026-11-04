"""Plan-local verifier for 2026-10-16-gui-mcp-setup-prompt (Session 31b).

``validate-task.ps1`` orchestrates the tools; this module holds every check that reads a report,
a plan file or git state. It writes nothing except its named outputs (``baseline-counts``,
``mcp-probe`` and ``pkg-result``), and the only product code it runs is the MCP server under
``mcp-probe``. ``static`` and ``selftest`` are stdlib-only and may run before plan approval (a
reviewer may run them). The state checks import ``yaml`` and run under ``uv run``.

Vitest runs come from two projects (``ui`` and ``mcp-server``). Where a command takes a Vitest
report it takes a comma-separated list of JSON files and a matching list of text receipts.

Usage (from the worktree root)::

    python plan_checks.py static
    python plan_checks.py selftest
    python plan_checks.py vitest <id> <json> <exit> <receipt>
    python plan_checks.py vitest-red <MEU-71|MEU-92> <json[,json]> <receipt[,receipt]>
    python plan_checks.py e2e <id> <json> <exit>
    python plan_checks.py e2e-red <MEU-71> <json>
    python plan_checks.py baseline-counts <ui-vitest.json> <mcp-vitest.json> <e2e.json>
    python plan_checks.py floors <ui-vitest.json> <mcp-vitest.json> <e2e.json> <ui-receipt,mcp-receipt>
    python plan_checks.py mcp-probe <out.json> <command> [args...]
    python plan_checks.py pkg-result <in-place.json> <hermetic.json>
    python plan_checks.py pkg-current
    python plan_checks.py task-state
    python plan_checks.py scope
    python plan_checks.py hub
    uv run python plan_checks.py prereq | ssot-review | post-review-state | decouple
    python plan_checks.py review-check <review-file> <plan|execution> <cap>
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

PLAN_DIR = Path("docs/execution/plans/2026-10-16-gui-mcp-setup-prompt")
PLAN = PLAN_DIR / "implementation-plan.md"
TASK = PLAN_DIR / "task.md"
PS1 = PLAN_DIR / "validate-task.ps1"
BASELINE_SHA = PLAN_DIR / "baseline.sha"
BASELINE_COUNTS = PLAN_DIR / "baseline-counts.json"
PKG_RESULT = PLAN_DIR / "pkg-probe-result.json"
# The work handoffs own the decisions made during execution (D-94 onward); static reads their ids too.
HANDOFFS = [Path(f".agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-{m}-handoff.md") for m in (71, 92)]
# PKG_EVIDENCE: the files whose current bytes a packaged proof is bound to. A consumer re-hashes every one and
# refuses the proof if any is missing or changed, so a later edit or a removed packaged entry needs a new row 8.
PKG_FILES = {
    "exe": "ui/dist/win-unpacked/av-kit.exe",
    "packaged_entry": "ui/dist/win-unpacked/resources/mcp-server/index.mjs",
    "packaged_licences": "ui/dist/win-unpacked/resources/mcp-server/LICENSES.txt",
    "bundle": "mcp-server/bundle/index.mjs",
    "bundle_licences": "mcp-server/bundle/LICENSES.txt",
    "electron_builder_yml": "ui/electron-builder.yml",
    "ui_package_json": "ui/package.json",
    "ui_package_lock": "ui/package-lock.json",
    "mcp_package_json": "mcp-server/package.json",
    "mcp_package_lock": "mcp-server/package-lock.json",
}
GROUPING = Path(".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md")
TARGET_PLAN = PLAN.as_posix()
MEUS = ("MEU-71", "MEU-92")

ALLOWED_STRATEGIES = {"shared", "compact_continue", "isolated"}
ALLOWED_BUILDERS = {"`avkit_builder`", "`avkit_coordinator`", "`avkit_verifier`", "—"}
TEST_DIRS = (Path("ui/tests/unit"), Path("mcp-server/tests"))

# Red: files that may fail to load, or fail on a missing symbol, because they import a module or
# export this MEU creates. Every other failure must be an assertion failure.
NEW_MODULE_FILES = {
    "MEU-71": ("mcp-setup-prompt.test.ts", "mcp-server-entry.test.ts", "mcp-spawn-electron.test.ts",
               "entry-guard.test.ts"),
    "MEU-92": ("bundle-licenses.test.ts",),
}
# TEST_AMENDMENTS TA-1/TA-2: the only pre-existing tests allowed to fail in Red (MEU-71 only).
TA_FILES = {
    "MEU-71": ("clipboard-image-main.test.ts", "ipc-strict-census.test.ts", "login-item-ipc.test.ts",
               "gui-actions-audit.test.ts"),
    "MEU-92": (),
}
MISSING_SYMBOL = re.compile(
    r"Failed to resolve import|Cannot find module|does not provide an export named|is not a function|is not defined"
)
FROZEN = ("packages", "tools", "native", "openapi.committed.json", "docs/build-plan/11-page-layout.md")
MAIN_ALLOWED = {
    "ui/src/main/ipc.ts", "ui/src/main/index.ts", "ui/src/main/preload.ts", "ui/src/main/mcp-setup-prompt.ts",
}
INDEX_ID = "settings:copy_mcp_prompt"

# Vitest's JSON reporter drops unhandled errors (they only set the exit code). Every Vitest run in this plan
# also uses the default reporter, whose text receipt prints this banner and summary line when they occur.
UNHANDLED = re.compile(r"Unhandled (?:Errors?|Rejection)|^\s*Errors\s+\d+ errors?\s*$", re.M)
ANSI = re.compile(r"\x1b\[[0-9;]*m")
# PRODUCT_SCOPE: besides the Files Modified rows, only this plan's own closeout outputs may change.
CLOSEOUT_PREFIXES = (
    PLAN_DIR.as_posix() + "/",
    ".agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-",
    "docs/execution/reflections/2026-10-16-gui-mcp-setup-prompt-",
)
CLOSEOUT_RENDERED = {".agent/context/meu-registry.md", ".agent/context/known-issues.md",
                     ".agent/context/known-issues-archive.md"}
AC_ANY = re.compile(r"AC-(?:71|92)\.\d")


def unhandled_errors(receipt_text: str) -> list[str]:
    text = ANSI.sub("", receipt_text)
    return [m.group(0).strip() for m in UNHANDLED.finditer(text)]


def receipt_unhandled(receipt: str) -> list[str]:
    path = Path(receipt)
    if not path.exists():
        return [f"receipt {receipt} missing"]
    return unhandled_errors(path.read_text(encoding="utf-8", errors="replace"))


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


def merge_vitest(paths: list[str]) -> dict:
    """One Vitest report from several (the ui and mcp-server projects)."""
    out: dict = {"testResults": [], "numPassedTests": 0, "numFailedTests": 0, "numTotalTests": 0,
                 "numPendingTests": 0, "numTodoTests": 0}
    for p in paths:
        j = load_json(p)
        out["testResults"] += j.get("testResults", [])
        for k in ("numPassedTests", "numFailedTests", "numTotalTests", "numPendingTests", "numTodoTests"):
            out[k] += j.get(k, 0) or 0
    return out


def split_list(arg: str) -> list[str]:
    return [a for a in arg.split(",") if a]


# ---------------------------------------------------------------- plan ACs


def plan_acs(plan: str) -> dict[str, str]:
    """AC id -> type cell, from the plan's AC tables."""
    out: dict[str, str] = {}
    for m in re.finditer(r"^\| (AC-(?:71|92)\.\d+) \| ([^|]+) \|", plan, re.M):
        out[m.group(1)] = m.group(2).strip()
    return out


def ac_pattern(ac: str) -> re.Pattern[str]:
    return re.compile(re.escape(ac) + r"(?![0-9])")


def electron_acs(plan: str) -> set[str]:
    return {a for a, t in plan_acs(plan).items() if "Electron" in t}


def runtime_acs(plan: str) -> set[str]:
    """Packaged-runtime ACs: proved by pkg-probe-result.json, never by Vitest or Playwright."""
    return {a for a, t in plan_acs(plan).items() if "runtime" in t}


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
    failed = _vitest_failed(j)
    if failed:
        return fail(f"{rid} failing tests: {[f[1][:90] for f in failed]}")
    if rc != 0:
        return fail(f"{rid} exit {rc} with no failed test (runner error)")
    print(f"PASS {rid}: {j.get('numPassedTests')} passed of {j.get('numTotalTests')}")
    return 0


def _base(name: str) -> str:
    return name.replace("\\", "/").rsplit("/", 1)[-1]


def vitest_red(meu: str, paths: str, receipts: str) -> int:
    for r in split_list(receipts):
        unhandled = receipt_unhandled(r)
        if unhandled:
            return fail(f"{meu} Red has unhandled errors (not assertion failures) in {r}: {unhandled[:3]}")
    j = merge_vitest(split_list(paths))
    tag = f"AC-{meu.split('-')[1]}."
    newf = NEW_MODULE_FILES[meu]
    tolerated_files: set[str] = set()
    for s in j.get("testResults", []):
        msg = s.get("message") or ""
        if not msg:
            continue
        if _base(s["name"]) in newf and MISSING_SYMBOL.search(msg):
            tolerated_files.add(_base(s["name"]))
            continue
        return fail(f"{meu} load/collection error in {s['name']}: {msg[:200]}")
    if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
        return fail(f"{meu} pending/todo tests present")
    decisive, tolerated, amended, bad = [], [], [], []
    for file, name, msgs in _vitest_failed(j):
        base = _base(file)
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
    if not decisive and not tolerated_files:
        return fail(f"{meu} no failing {tag} assertion")
    plan = read(PLAN)
    skip = electron_acs(plan) | runtime_acs(plan)
    want = {a for a in plan_acs(plan) if a.startswith(tag) and a not in skip}
    red_names = decisive + tolerated
    missing = sorted(a for a in want if not any(ac_pattern(a).search(n) for n in red_names)
                     and not any(_ac_in_file(a, f) for f in tolerated_files))
    if missing:
        return fail(f"{meu} ACs with no Red test: {missing}")
    print(f"PASS {meu} Vitest RED: {len(decisive)} assertion failures, {len(tolerated)} missing-symbol, "
          f"load-tolerated files {sorted(tolerated_files)}, TA pins failing {amended}")
    return 0


def _ac_in_file(ac: str, base: str) -> bool:
    for d in TEST_DIRS:
        path = d / base
        if path.exists() and ac_pattern(ac).search(read(path)):
            return True
    return False


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


def e2e_red(meu: str, path: str) -> int:
    j = load_json(path)
    if j.get("errors"):
        return fail(f"{meu} E2E top-level errors (collection/launch): {j['errors'][:1]}")
    want = {a for a in electron_acs(read(PLAN)) if a.startswith(f"AC-{meu.split('-')[1]}.")}
    if not want:
        return fail(f"{meu} has no Electron AC; its Red runs no Playwright")
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


def baseline_counts(ui_json: str, mcp_json: str, ejson: str) -> int:
    u, m, e = load_json(ui_json), load_json(mcp_json), load_json(ejson)
    counts = {
        "ui_vitest_passed": u.get("numPassedTests"), "ui_vitest_failed": u.get("numFailedTests"),
        "mcp_vitest_passed": m.get("numPassedTests"), "mcp_vitest_failed": m.get("numFailedTests"),
        "e2e_expected": e["stats"].get("expected"), "e2e_skipped": e["stats"].get("skipped"),
        "e2e_unexpected": e["stats"].get("unexpected"), "e2e_flaky": e["stats"].get("flaky"),
    }
    if counts["ui_vitest_failed"] or counts["mcp_vitest_failed"] or counts["e2e_unexpected"] or counts["e2e_flaky"]:
        return fail(f"baseline is not green: {counts}")
    BASELINE_COUNTS.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(f"PASS baseline counts {counts}")
    return 0


def _passed_names(j: dict) -> list[str]:
    return [a.get("fullName", "") for s in j.get("testResults", []) for a in s.get("assertionResults", [])
            if a.get("status") == "passed"]


def pkg_evidence_errors(result: Path = PKG_RESULT, files: dict[str, str] = PKG_FILES) -> list[str]:
    """PKG_EVIDENCE: why the saved packaged proof does not describe the current tree ([] = it does)."""
    if not result.exists():
        return [f"{result.as_posix()} missing (row 8)"]
    rec = json.loads(result.read_text(encoding="utf-8"))
    if rec.get("passed") is not True:
        return [f"{result.as_posix()} did not pass"]
    return identity_errors(rec.get("identity") or {}, files)


def floors(ui_json: str, mcp_json: str, ejson: str, receipts: str) -> int:
    if not BASELINE_COUNTS.exists():
        return fail("baseline-counts.json missing (row 0)")
    for r in split_list(receipts):
        unhandled = receipt_unhandled(r)
        if unhandled:
            return fail(f"vitest unhandled errors in {r}: {unhandled[:3]}")
    base = json.loads(read(BASELINE_COUNTS))
    u, m, e = load_json(ui_json), load_json(mcp_json), load_json(ejson)
    plan = read(PLAN)
    acs = plan_acs(plan)
    eacs, racs = electron_acs(plan), runtime_acs(plan)
    new_ui = [n for n in _passed_names(u) if AC_ANY.search(n)]
    new_mcp = [n for n in _passed_names(m) if AC_ANY.search(n)]
    spec_titles = [s.get("title", "") for t in e.get("suites", []) for _, s in _specs(t)
                   if _spec_status(s)[0] == "passed"]
    new_e2e = [t for t in spec_titles if AC_ANY.search(t)]
    errs = []
    for a in acs:
        if a in racs:
            stale = pkg_evidence_errors()
            if stale:
                errs.append(f"{a} packaged proof is not current (re-run row 8, -Check pkg-probe): {stale}")
            continue
        pool = new_e2e if a in eacs else new_ui + new_mcp
        if not any(ac_pattern(a).search(n) for n in pool):
            errs.append(f"{a} has no passing test")
    for label, j, key, new in (("ui", u, "ui_vitest_passed", new_ui), ("mcp", m, "mcp_vitest_passed", new_mcp)):
        if j.get("numFailedTests", 0):
            errs.append(f"{label} vitest failed {j.get('numFailedTests')}: {[f[1][:80] for f in _vitest_failed(j)]}")
        if [s["name"] for s in j.get("testResults", []) if s.get("message")]:
            errs.append(f"{label} vitest suite load errors")
        if j.get("numPassedTests", 0) < base[key] + len(new):
            errs.append(f"{label} vitest passed {j.get('numPassedTests')} < {base[key]} + {len(new)}")
    st = e.get("stats", {})
    if st.get("unexpected", 0) or st.get("flaky", 0):
        errs.append(f"e2e unexpected {st.get('unexpected')} flaky {st.get('flaky')}")
    if st.get("expected", 0) < base["e2e_expected"] + len(new_e2e):
        errs.append(f"e2e expected {st.get('expected')} < {base['e2e_expected']} + {len(new_e2e)}")
    if st.get("skipped", 0) > base["e2e_skipped"]:
        errs.append(f"e2e skipped {st.get('skipped')} > baseline {base['e2e_skipped']}")
    if errs:
        return fail(f"COUNT_FLOORS: {errs}")
    print(f"PASS COUNT_FLOORS: ui vitest {u.get('numPassedTests')} (baseline {base['ui_vitest_passed']}, +{len(new_ui)}), "
          f"mcp vitest {m.get('numPassedTests')} (baseline {base['mcp_vitest_passed']}, +{len(new_mcp)}), "
          f"e2e {st.get('expected')} (baseline {base['e2e_expected']}, +{len(new_e2e)}), packaged proof current")
    return 0


# ---------------------------------------------------------------- MCP_ENTRY_PROBE / PKG_PROBE


def probe_passed(rec: dict) -> bool:
    return rec.get("result") == "started" and '"name":"av-kit"' in rec.get("first_stdout", "")


def mcp_probe(out: str, argv: list[str]) -> int:
    """MCP_ENTRY_PROBE (Session 32 gate_lib.cmd_mcp_probe, now a pass condition): one initialize, 10 s."""
    rec: dict = {"argv": argv, "result": "unreachable", "exit_code": None, "stderr_tail": "",
                 "first_stdout": "", "seconds": None}
    entry = argv[-1] if argv else ""
    if not argv or not Path(argv[0]).exists() or not Path(entry).exists():
        rec["stderr_tail"] = "command or entry file missing"
    else:
        init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "s31b-mcp-probe", "version": "1"}}}
        env = dict(os.environ, ELECTRON_RUN_AS_NODE="1")
        # CreateProcess does not find a relative program path written with '/' (D-97); launch it absolute.
        command = [str(Path(argv[0]).resolve()), *argv[1:]]
        start = time.monotonic()
        proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", env=env)
        assert proc.stdin and proc.stdout
        proc.stdin.write(json.dumps(init) + "\n")
        proc.stdin.flush()
        lines: list[str] = []
        reader = threading.Thread(target=lambda: lines.extend(iter(proc.stdout.readline, "")), daemon=True)
        reader.start()
        deadline = start + 10
        while time.monotonic() < deadline and proc.poll() is None:
            if any('"jsonrpc"' in ln for ln in lines):
                rec["result"] = "started"
                break
            time.sleep(0.1)
        rec["seconds"] = round(time.monotonic() - start, 2)
        proc.kill()
        _, err = proc.communicate(timeout=5)
        reader.join(timeout=2)
        rec["exit_code"] = proc.returncode
        rec["stderr_tail"] = (err or "")[-800:]
        rec["first_stdout"] = lines[0][:300] if lines else ""
    rec["passed"] = probe_passed(rec)
    Path(out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    if not rec["passed"]:
        return fail(f"MCP_ENTRY_PROBE {rec['result']} (exit {rec['exit_code']}): {rec['stderr_tail'][-300:]}")
    print(f"PASS MCP_ENTRY_PROBE started in {rec['seconds']} s: {rec['first_stdout'][:120]}")
    return 0


def _sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).exists() else ""


def pkg_identity(files: dict[str, str]) -> dict[str, str]:
    return {k: _sha(p) for k, p in files.items()}


def identity_errors(recorded: dict[str, str], files: dict[str, str]) -> list[str]:
    errs = []
    for k, p in files.items():
        now = _sha(p)
        if not now:
            errs.append(f"{p} missing")
        elif recorded.get(k) != now:
            errs.append(f"{p} changed since the probe")
    return errs


def pkg_result(in_place: str, hermetic: str, files: dict[str, str] = PKG_FILES, out: Path = PKG_RESULT) -> int:
    a, b = load_json(in_place), load_json(hermetic)
    ident = pkg_identity(files)
    missing = sorted(files[k] for k, v in ident.items() if not v)
    res = {
        "schema": "s31b-pkg-probe.v2",
        "tested_commit": _git("rev-parse", "HEAD").strip(),
        "identity": ident,
        "byte_equal": not missing and ident["bundle"] == ident["packaged_entry"]
        and ident["bundle_licences"] == ident["packaged_licences"],
        "licences_present": bool(ident["packaged_licences"]) and Path(files["packaged_licences"]).stat().st_size > 0,
        "missing": missing,
        "in_place": a, "hermetic": b,
    }
    res["passed"] = res["byte_equal"] and res["licences_present"] and probe_passed(a) and probe_passed(b)
    out.write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    if not res["passed"]:
        return fail(f"PKG_PROBE: missing {missing}, byte_equal {res['byte_equal']}, licences {res['licences_present']}, "
                    f"in-place {a.get('result')}, hermetic {b.get('result')}")
    print(f"PASS PKG_PROBE: bundle and LICENSES.txt byte-equal in win-unpacked ({ident['bundle'][:12]}), both probes "
          f"started; proof bound to {len(files)} files")
    return 0


def pkg_current() -> int:
    errs = pkg_evidence_errors()
    if errs:
        return fail(f"PKG_EVIDENCE stale; re-run row 8 (-Check pkg-probe): {errs}")
    print(f"PASS PKG_EVIDENCE: {PKG_RESULT.as_posix()} passed and all {len(PKG_FILES)} bound files are unchanged")
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
             "mcp-probe", "pkg-result", "pkg-current", "task-state", "scope", "hub", "prereq", "ssot-review",
             "post-review-state", "review-check", "decouple"}
    for c in sorted(pc_cmds - known):
        errs.append(f"validate-task.ps1 calls unknown plan_checks command {c}")
    # Every plan AC is named in a task row, singly or inside an AC-n.a–n.b range.
    acs = plan_acs(plan)
    covered: set[str] = set()
    for m in re.finditer(r"AC-(71|92)\.(\d+)(?:[–-](?:(?:71|92)\.)?(\d+))?", task):
        lo = int(m.group(2))
        hi = int(m.group(3)) if m.group(3) else lo
        covered |= {f"AC-{m.group(1)}.{i}" for i in range(lo, hi + 1)}
    for a in sorted(set(acs) - covered):
        errs.append(f"{a} is not named in any task row")
    # Every D-n, TA-n, S-n referenced in task.md is defined in the plan, a work handoff's Decision Log (review F2),
    # or the grouping rows this session carries.
    owners = plan + "".join(read(h) for h in HANDOFFS if h.exists())
    defined_d = {int(x) for x in re.findall(r"^  - id: D-(\d+)$", owners, re.M)} | set(range(1, 8)) | {55, 56}
    for d in sorted({int(x) for x in re.findall(r"\bD-(\d+)\b", task)} - defined_d):
        errs.append(f"task.md cites D-{d}, which no decision defines")
    for ta in sorted(set(re.findall(r"\bTA-(\d+)\b", task)) - set(re.findall(r"\*\*TA-(\d+):\*\*", plan))):
        errs.append(f"task.md cites TA-{ta}, which TEST_AMENDMENTS does not define")
    for s in sorted(set(re.findall(r"\bS(\d)\b", task)) - set(re.findall(r"^\| S(\d) \|", plan, re.M))):
        errs.append(f"task.md cites S{s}, which Stop Conditions does not define")
    # Contract names used in task.md exist in the contracts table.
    contracts = set(re.findall(r"^\| `([A-Z][A-Z0-9_]*)` \|", plan, re.M))
    for name in sorted(set(re.findall(r"`([A-Z][A-Z0-9]*_[A-Z0-9_]+)`", task)) - contracts):
        errs.append(f"task.md names `{name}`, which the contracts table does not define")
    # Every Files Modified Action cell starts with new or modify (listed_files reads only those rows).
    for m in re.finditer(r"^\| (`[^|]+) \| ([^|]+) \|", plan, re.M):
        if m.group(1).startswith("`AC-") or re.match(r"`[A-Z][A-Z0-9_]*`$", m.group(1).strip()):
            continue
        if "/" in m.group(1) and not re.match(r"(new|modify)\b", m.group(2).strip()):
            errs.append(f"Files Modified row {m.group(1)[:60]} has action {m.group(2).strip()[:30]!r}")
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        return 1
    print(f"PASS static: {len(rows)} rows, {len(checks)} -Check names, {len(acs)} ACs covered")
    return 0


def task_state() -> int:
    rows = [r for r in task_rows(read(TASK)) if r[0].isdigit() or r[0] == "0a"]
    if len(rows) != 12:
        return fail(f"expected 12 implementation rows (0a, 0-10), got {len(rows)}")
    for r in rows:
        s = r[-1].strip("`")
        if s == "[x]" or (s == "[B]" and "follow-up" in r[1] and "B-" in r[1]):
            continue
        return fail(f"unfinished row {r[0]}: {s}")
    print("PASS implementation rows 0a and 0-10")
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


def is_listed(path: str, listed: set[str]) -> bool:
    """A listed path ending in '/' covers the files under it (the golden-fixture directory)."""
    return path in listed or any(entry.endswith("/") and path.startswith(entry) for entry in listed)


def scope_violations(paths: set[str], listed: set[str]) -> list[str]:
    """Every changed path in the repository must be a Files Modified row or this plan's closeout output."""
    errs = []
    frozen = sorted(p for p in paths if any(p == f or p.startswith(f + "/") for f in FROZEN))
    if frozen:
        errs.append(f"PRODUCT_SCOPE frozen paths changed: {frozen}")
    main = sorted(p for p in paths if p.startswith("ui/src/main/") and p not in MAIN_ALLOWED)
    if main:
        errs.append(f"ui/src/main files outside the four named: {main}")
    extra = sorted(p for p in paths if not is_listed(p, listed) and p not in CLOSEOUT_RENDERED
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
    g07 = read("docs/build-plan/07-distribution.md")
    if "resources/extra/mcp-server/" in g07 or "resources/mcp-server/" not in g07:
        errs.append("07 still names resources/extra/mcp-server/ or lacks resources/mcp-server/")
    if 'id="mcp-server-bundle-residual"' not in g07:
        errs.append("07 lacks the mcp-server-bundle-residual anchor")
    g06 = read("docs/build-plan/06-gui.md")
    if "getMcpSetupPrompt: (opts" not in g06:
        errs.append("06 preload listing lacks the getMcpSetupPrompt line")
    g05 = read("docs/build-plan/05-mcp-server.md")
    row05 = next((ln for ln in g05.splitlines() if ln.startswith("| **7 Dist** |")), "")
    if "bundle" not in row05 or "setup prompt" not in row05:
        errs.append("05 Phase 7 row does not name the bundle and the setup prompt")
    matrix = read("docs/build-plan/build-priority-matrix.md")
    for row in ("| 7.3 | MEU-71 | `gui-mcp-setup-prompt` |", "| 7.5 | MEU-92 | `dist-mcp-server-bundle` |"):
        if row not in matrix:
            errs.append(f"matrix lacks {row}")
    if f"| `{INDEX_ID}` |" not in read("docs/build-plan/gui-actions-index.md"):
        errs.append(f"gui-actions-index lacks {INDEX_ID}")
    if "AVKIT_API_TOKEN" in read("docs/distribution/mcp.json.example"):
        errs.append("mcp.json.example still names AVKIT_API_TOKEN")
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


def grouping_row(status: str) -> re.Pattern[str]:
    return re.compile(r"^\| 31b \| `gui-mcp-setup-prompt` \| MEU-71[^|]*\| P3 \| " + re.escape(status) + r" \|", re.M)


def prereq() -> int:
    d56 = re.search(r"^\| D-56 \|[^|]+\| ([^|]+) \|", read(GROUPING), re.M)
    if not d56 or d56.group(1).strip() == "open":
        return fail("grouping D-56 is still open: record Mat's ruling first (S1)")
    rows = _meus()
    want = {"MEU-23": "approved", "MEU-25": "approved", "MEU-71": "pending", "MEU-92": "pending"}
    bad = {k: rows.get(k, {}).get("status") for k, v in want.items() if rows.get(k, {}).get("status") != v}
    if bad:
        return fail(f"MEU state (S1): {bad}")
    for k in MEUS:
        if rows[k].get("execution_plan") != PLAN_DIR.as_posix():
            return fail(f"{k} execution_plan is {rows[k].get('execution_plan')!r}")
    print(f"PASS grouping D-56 ruled; MEU state {want}; execution_plan set")
    return 0


def ssot_review() -> int:
    rows = _meus()
    for k in MEUS:
        if rows[k]["status"] != "ready_for_review":
            return fail(f"{k} is {rows[k]['status']}")
    if not grouping_row("in review").search(read(GROUPING)):
        return fail("grouping Session 31b row is not 'in review'")
    focus = read(".agent/context/current-focus.md")
    if "gui-mcp-setup-prompt" not in focus or "ready_for_review" not in focus:
        return fail("current-focus.md does not record Session 31b ready_for_review")
    print("PASS SSOT review state")
    return 0


def post_review_state() -> int:
    import yaml  # noqa: PLC0415

    rows = _meus()
    for k in MEUS:
        if rows[k]["status"] != "approved":
            return fail(f"{k} is {rows[k]['status']}")
    issues = {i["id"]: i for i in yaml.safe_load(read(".agent/context/known-issues.yaml"))["issues"]}
    for i in ("MCP-SETUP-PROMPT", "MCP-PACKAGED-ENTRY-UNREACHABLE"):
        it = issues.get(i) or {}
        ev = (it.get("verification") or {}).get("evidence_file") or ""
        if it.get("status") != "resolved" or not ev.startswith(PLAN_DIR.as_posix()):
            return fail(f"{i} status {it.get('status')} evidence {ev!r}")
    if not grouping_row("approved").search(read(GROUPING)):
        return fail("grouping Session 31b row is not approved")
    if "2026-10-16-gui-mcp-setup-prompt" not in read("docs/execution/metrics.md"):
        return fail("metrics row missing")
    print("PASS POST_REVIEW_STATE")
    return 0


def same_target(value: str, root: Path) -> bool:
    """True if value names this checkout's plan, repo-relative or absolute."""
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


# ---------------------------------------------------------------- amendment A-1 (row 0a)

VENDOR_DIR = Path("_inspiration/zorivest")
# DECOUPLE_SCAN (D-91 A): the live code and canon that must not point at the Zorivest checkout. Closed plans,
# handoffs, reflections and decision records keep their citations as history and are not scanned.
DECOUPLE_SCAN = ("ui/src", "ui/tests", "mcp-server/src", "mcp-server/tests", "mcp-server/scripts", "tools",
                 "docs/build-plan", "docs/BUILD_PLAN.md", ".agent/docs", ".agent/workflows", ".agent/skills",
                 "AGENTS.md", "CLAUDE.md", "GUARDRAILS.md")
DECOUPLE_SKIP = {"node_modules", "dist", "out", "out-e2e", "bundle", "__pycache__"}
ZV_PATH = re.compile(r"p:[/\\]+zorivest", re.I)
# The one allowed mention: BUILD_PLAN principle 4 forbids consulting the checkout (D-91 A wording).
ZV_ALLOWED = "do not consult `P:/zorivest`"
PILL_SOURCE_LINE = "const PILL_TOKEN_SOURCE = resolve(repoRoot, '_inspiration/zorivest/globals.css')"
PROVENANCE_ROW = re.compile(
    r"^\| `([^`]+)` \| `[^`]+` \| `[0-9a-f]{40}` \| [\d-]+ \| `([0-9a-f]{40})` \| `([0-9a-f]{64})` \| (\d+) \|", re.M)


def git_blob(data: bytes) -> str:
    """The git object id of LF content, as `git hash-object` prints it."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()  # noqa: S324 - git's object id


def zorivest_refs(path: str, text: str) -> list[str]:
    return [f"{path}:{n}" for n, line in enumerate(text.splitlines(), 1)
            if ZV_PATH.search(line) and ZV_ALLOWED not in line]


def provenance_errors(root: Path = Path(".")) -> list[str]:
    """Every copy matches its PROVENANCE.md row (LF sha256, size, git blob id); nothing unlisted sits beside it."""
    vendor = root / VENDOR_DIR
    rows = PROVENANCE_ROW.findall((vendor / "PROVENANCE.md").read_text(encoding="utf-8"))
    errs = [] if rows else ["PROVENANCE.md lists no copies"]
    for name, blob, sha, size in rows:
        f = vendor / name
        if not f.is_file():
            errs.append(f"{name} missing")
            continue
        data = f.read_bytes().replace(b"\r\n", b"\n")
        if hashlib.sha256(data).hexdigest() != sha or len(data) != int(size) or git_blob(data) != blob:
            errs.append(f"{name} differs from its PROVENANCE.md row")
    listed = {r[0] for r in rows} | {"PROVENANCE.md"}
    extra = sorted(p.name for p in vendor.iterdir() if p.name not in listed)
    if extra:
        errs.append(f"files in {VENDOR_DIR.as_posix()} with no PROVENANCE.md row: {extra}")
    return errs


def decouple() -> int:
    import yaml  # noqa: PLC0415

    errs = provenance_errors()
    refs: list[str] = []
    scanned = 0
    for entry in DECOUPLE_SCAN:
        p = Path(entry)
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.is_file() and not DECOUPLE_SKIP & set(f.parts)]
        for f in files:
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            scanned += 1
            refs += zorivest_refs(f.as_posix(), text)
    if refs:
        errs.append(f"live Zorivest checkout paths: {refs}")
    if PILL_SOURCE_LINE not in read("ui/tests/unit/queue-canon.test.ts"):
        errs.append("AC-41.3 PILL_TOKEN_SOURCE is not the vendored copy")
    issues = {i["id"]: i for i in yaml.safe_load(read(".agent/context/known-issues.yaml"))["issues"]}
    it = issues.get("QUEUE-PILL-TOKEN-DRIFT") or {}
    ev = (it.get("verification") or {}).get("evidence_file") or ""
    if it.get("status") != "resolved" or not ev.startswith(PLAN_DIR.as_posix()):
        errs.append(f"QUEUE-PILL-TOKEN-DRIFT status {it.get('status')} evidence {ev!r}")
    if errs:
        return fail("; ".join(errs))
    print(f"PASS decouple: copies match PROVENANCE.md; no live Zorivest path in {scanned} files; "
          "AC-41.3 reads the copy; QUEUE-PILL-TOKEN-DRIFT resolved")
    return 0


def _selftest_decouple() -> None:
    import tempfile  # noqa: PLC0415

    assert git_blob(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    assert zorivest_refs("a", "x\nread P:/zorivest/ui/x\np:\\\\zorivest\\\\y\nP://Zorivest") == ["a:2", "a:3", "a:4"]
    assert zorivest_refs("a", "_inspiration/zorivest/globals.css\nZorivest MEU-389\nso do not consult `P:/zorivest`.") == []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        vendor = root / VENDOR_DIR
        vendor.mkdir(parents=True)
        body = b"a {\n  --x: #fff;\n}\n"
        (vendor / "g.css").write_bytes(body.replace(b"\n", b"\r\n"))
        row = (f"| `g.css` | `ui/g.css` | `{'1' * 40}` | 2026-10-16 | `{git_blob(body)}` | "
               f"`{hashlib.sha256(body).hexdigest()}` | {len(body)} |\n")
        (vendor / "PROVENANCE.md").write_text("| File |\n" + row, encoding="utf-8")
        assert provenance_errors(root) == [], provenance_errors(root)
        (vendor / "g.css").write_bytes(body.replace(b"#fff", b"#000"))
        assert provenance_errors(root) == ["g.css differs from its PROVENANCE.md row"]
        (vendor / "g.css").write_bytes(body)
        (vendor / "h.css").write_bytes(body)
        assert len(provenance_errors(root)) == 1 and "h.css" in provenance_errors(root)[0]
        (vendor / "h.css").unlink()
        (vendor / "g.css").unlink()
        assert provenance_errors(root) == ["g.css missing"]


# ---------------------------------------------------------------- selftest


def selftest() -> int:
    assert ac_pattern("AC-71.1").search("AC-71.1 golden") and not ac_pattern("AC-71.1").search("AC-71.12 instr")
    sample = ("| AC-71.1 | unit | x |\n| AC-71.15 | integration (Electron) | y |\n"
              "| AC-92.4 | runtime (packaged) | z |\n| AC-92.1 | integration (process) | w |\n")
    assert plan_acs(sample) == {"AC-71.1": "unit", "AC-71.15": "integration (Electron)",
                                "AC-92.4": "runtime (packaged)", "AC-92.1": "integration (process)"}
    assert electron_acs(sample) == {"AC-71.15"} and runtime_acs(sample) == {"AC-92.4"}
    rows = task_rows("| # | h |\n|---|---|\n| | **divider** | | | | | | | | |\n| 0 | a | b | c | d | — | shared | e | — | `[ ]` |\n")
    assert [r[0] for r in rows] == ["0"]
    lf = listed_files("| `ui/a.ts` | new | s |\n| `x.yaml`, `y.md` (rendered) | modify | s |\n| `ui/b.ts` | reuse | s |\n"
                      "| `ui/tests/unit/fixtures/mcp-setup-prompt/` | new | s |\n")
    assert lf == {"ui/a.ts", "x.yaml", "y.md", "ui/tests/unit/fixtures/mcp-setup-prompt/"}, lf
    # Unhandled errors must be caught even when every test assertion is tolerated.
    receipt = ("\x1b[31m\u23af\u23af Unhandled Rejection \u23af\u23af\x1b[39m\nError: boom\n Test Files  1 failed (1)\n"
               "      Tests  1 failed | 3 passed (4)\n     Errors  1 error\n")
    assert len(unhandled_errors(receipt)) == 2, unhandled_errors(receipt)
    assert unhandled_errors(" Test Files  1 failed (1)\n      Tests  1 failed | 3 passed (4)\n") == []
    # Scope negatives: root config, an unlisted test, a frozen path, a fifth main file, a stray fixture.
    listed = {"ui/a.ts", "mcp-server/src/entry-guard.ts", "ui/tests/unit/fixtures/mcp-setup-prompt/"}
    ok = {"ui/a.ts", "mcp-server/src/entry-guard.ts", "ui/tests/unit/fixtures/mcp-setup-prompt/codex-user.txt",
          PLAN_DIR.as_posix() + "/gate-result.json", PLAN_DIR.as_posix() + "/pkg-probe-result.json",
          ".agent/context/meu-registry.md", ".agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md"}
    assert scope_violations(ok, listed) == [], scope_violations(ok, listed)
    for bad in ("pyproject.toml", "uv.lock", "ui/tests/unit/other.test.ts", "packages/api/x.py", "tools/meu_status.py",
                "mcp-server/src/tools/tts.ts", "ui/tests/unit/fixtures/other.txt",
                "ui/src/main/tray.ts", ".agent/context/handoffs/2026-10-15-other-handoff.md"):
        assert scope_violations(ok | {bad}, listed | ({bad} if bad == "ui/src/main/tray.ts" else set())), bad
    # Relative and absolute targets in this checkout match; another checkout's plan does not.
    wt = Path("P:/av-kit-wt/s31b-gui-mcp-setup-prompt")
    assert same_target(TARGET_PLAN, wt)
    assert same_target((wt / PLAN).as_posix(), wt)
    assert not same_target((Path("P:/av-kit") / PLAN).as_posix(), wt)
    assert not same_target("", wt)
    # MCP_ENTRY_PROBE pass rule: started and the first line names the server.
    assert probe_passed({"result": "started", "first_stdout": '{"result":{"serverInfo":{"name":"av-kit","version":"0.1.0"}}}'})
    assert not probe_passed({"result": "started", "first_stdout": '{"error":{"code":-32600}}'})
    assert not probe_passed({"result": "unreachable", "first_stdout": ""})
    # Grouping row status regex accepts the MEU-92 cell and refuses another status.
    row = "| 31b | `gui-mcp-setup-prompt` | MEU-71, MEU-92 (MEU-71 moved from 31, D-55; MEU-92 D-56) | P3 | in review | x |"
    assert grouping_row("in review").search(row) and not grouping_row("approved").search(row)
    _selftest_pkg_evidence()
    _selftest_decouple()
    print("PASS selftest")


def _selftest_pkg_evidence() -> None:
    """PKG_EVIDENCE negatives: a removed packaged entry, a changed bundle and a changed config each refuse the proof."""
    import tempfile  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        files = {k: (root / k / Path(p).name).as_posix() for k, p in PKG_FILES.items()}
        for k, p in files.items():
            Path(p).parent.mkdir(parents=True, exist_ok=True)
            body = "entry" if k in ("bundle", "packaged_entry") else "lic" if "licences" in k else k
            Path(p).write_text(body, encoding="utf-8")
        ok = {"result": "started", "first_stdout": '{"result":{"serverInfo":{"name":"av-kit"}}}'}
        probe = (root / "probe.json").as_posix()
        Path(probe).write_text(json.dumps(ok), encoding="utf-8")
        result = root / "pkg-probe-result.json"
        assert pkg_result(probe, probe, files, result) == 0
        assert pkg_evidence_errors(result, files) == []
        Path(files["packaged_entry"]).unlink()
        assert any("missing" in e for e in pkg_evidence_errors(result, files))
        Path(files["packaged_entry"]).write_text("entry", encoding="utf-8")
        assert pkg_evidence_errors(result, files) == []
        Path(files["bundle"]).write_text("entry2", encoding="utf-8")
        assert any("changed" in e for e in pkg_evidence_errors(result, files))
        Path(files["bundle"]).write_text("entry", encoding="utf-8")
        Path(files["electron_builder_yml"]).write_text("- from: ../mcp-server/dist", encoding="utf-8")
        assert any("changed" in e for e in pkg_evidence_errors(result, files))
        # A proof that recorded no identity (the old record-only shape) is refused outright.
        result.write_text(json.dumps({"passed": True}), encoding="utf-8")
        assert len(pkg_evidence_errors(result, files)) == len(files)
        # A packaged entry that differs from the source bundle never passes.
        Path(files["packaged_entry"]).write_text("other", encoding="utf-8")
        assert pkg_result(probe, probe, files, result) == 1
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
        "vitest-red": lambda: vitest_red(args[0], args[1], args[2]),
        "e2e": lambda: e2e_ok(args[0], args[1], int(args[2])),
        "e2e-red": lambda: e2e_red(args[0], args[1]),
        "baseline-counts": lambda: baseline_counts(args[0], args[1], args[2]),
        "floors": lambda: floors(args[0], args[1], args[2], args[3]),
        "mcp-probe": lambda: mcp_probe(args[0], args[1:]),
        "pkg-result": lambda: pkg_result(args[0], args[1]),
        "pkg-current": lambda: pkg_current(),
        "task-state": lambda: task_state(),
        "scope": lambda: scope(),
        "hub": lambda: hub(),
        "prereq": lambda: prereq(),
        "ssot-review": lambda: ssot_review(),
        "post-review-state": lambda: post_review_state(),
        "review-check": lambda: review_check(args[0], args[1], int(args[2])),
        "decouple": lambda: decouple(),
    }
    if cmd not in table:
        print(f"unknown command {cmd}")
        return 2
    return table[cmd]()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
