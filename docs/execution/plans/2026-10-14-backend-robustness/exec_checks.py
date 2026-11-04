"""Evaluator for 2026-10-14-backend-robustness (Session 33).

``validate-task.ps1`` runs every tool through ``rtk proxy`` into ``C:/Temp/av-kit/s33-*`` receipts and
reports; this script reads those files and decides. It runs no product code and never edits a product file.
Run from the repository root with ``uv run python`` (PyYAML is imported lazily, only by the SSOT verbs).

This file holds the executable copies of the plan's named sets (implementation-plan.md §Single-statement
contracts). ``plan_checks.py static`` asserts each one equals the plan: ``GATE_EXCLUDED`` (``GATED_PATHS``), ``FLOORS``
(``COUNT_FLOORS``), ``STAGES`` (the ``WINDOWS_GATE`` order, also in ``validate-task.ps1``), ``ACS``/``PINS``
(the AC table's Type column) and ``TA_SITES`` (``TEST_AMENDMENTS``).

Verbs (each exits 0 on PASS, 1 on FAIL)::

    red|green   --tier pytest|vitest|mcp|electron --meu 76|78|77 --report <file> --exit <code>
    suite       --tier ... --report <file> --exit <code>          whole-suite run: zero failures
    fingerprint --out <file> [--exclude <path>]                  GATE_FINGERPRINT / AUDIT_FINGERPRINT
    audit-fp --before <file> --after <file> --out <json>         AUDIT_FINGERPRINT: before == after, recorded
    meu-state --expect <status> | prereq-auth | baseline-counts --report <mcp.json>
    review-check --target <file> --mode plan|execution --cap <n>
    overlap --planning-head <sha> --out <file>                   S4 refusal and the D-10 overlap list
    red-guard --meu NN [--snapshot <file>] | snapshot --out <file>  Red precedes any production edit
    audit-check --summary <file> | gate-check | task-state | ssot-review | api-scope | handoff-ac | hub
    post-review-state | selftest
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import os
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

PLAN = "docs/execution/plans/2026-10-14-backend-robustness"
MEUS = ("MEU-76", "MEU-78", "MEU-77")
SLUG = "backend-robustness"
GROUPING = ".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md"
BASELINE = ".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json"
REVIEW_AGENT = "gpt-6.1-sol"

# GATED_PATHS is the whole working tree minus GATE_EXCLUDED (plan §Single-statement contracts: fnmatch patterns,
# `*` also crosses `/`); plan_checks.py asserts this list equals the plan's.
GATE_EXCLUDED = [
    ".agent/context/meu-status.yaml", ".agent/context/meu-registry.md", ".agent/context/current-focus.md",
    ".agent/context/known-issues.yaml", ".agent/context/known-issues.md", GROUPING,
    ".agent/context/handoffs/2026-10-14-backend-robustness-*", ".agent/context/MCP/mcp-tool-audit-report.md",
    "docs/BUILD_PLAN.md", "docs/execution/metrics.md", "docs/execution/reflections/2026-10-14-backend-robustness-*",
    f"{PLAN}/task.md", f"{PLAN}/walkthrough.md", f"{PLAN}/baseline.sha", f"{PLAN}/*.json", f"{PLAN}/*.txt",
]
# COUNT_FLOORS (Session 30 windows-gate-result.json, attempt of record).
FLOORS = {"pytest": 655, "vitest": 773, "e2e": 133}
# WINDOWS_GATE stage order; validate-task.ps1 carries the argv, plan_checks.py asserts the same ids and order.
STAGES = [
    "npm-ci", "mcp-npm-ci", "py-types", "py-lint", "ui-types", "ui-lint", "mcp-types", "py-tests", "ui-tests",
    "ui-build", "ui-harness-build", "mcp-build", "mcp-tests", "openapi", "state-render", "ui-electron",
    "source-audit",
]
# The AC table's Type column, per MEU: AC -> test tier. PINS are the ACs typed **pin** (RED_RULE item 5).
ACS = {
    "76": {**{f"76.{n}": "pytest" for n in range(1, 8)}, "76.8": "vitest", "76.9": "mcp"},
    "78": {**{f"78.{n}": "pytest" for n in range(1, 8)}, "78.8": "vitest", "78.9": "electron"},
    "77": {**{f"77.{n}": "pytest" for n in range(1, 12)}, "77.12": "mcp", "77.13": "mcp", "77.14": "electron"},
}
PINS = {"77.14"}
# TEST_AMENDMENTS: TA id -> the file whose edit carries "TA-n (Session 33".
TA_SITES = {
    1: "tests/unit/test_domain.py", 2: "tests/integration/test_filesystem_media.py",
    3: "tests/unit/test_domain.py", 4: "tests/integration/test_filesystem_media.py",
    5: "tests/unit/test_domain.py", 6: "tests/integration/test_sqlite_uow.py",
    7: "tests/unit/test_services.py", 8: "tests/unit/test_services.py",
    9: "tests/integration/test_tts_assets.py", 10: "tests/integration/test_tts_assets.py",
    11: "tests/unit/test_domain_conversion.py",  # A-10
}
# OPENAPI_DIFF allow-lists.
OPENAPI_PATHS = {"/api/v1/tts/generate", "/api/v1/tts/{id}"}
OPENAPI_SCHEMAS = {"FfmpegDependencyOut", "TTSJobOut"}
ISSUES = ("API-UNHANDLED-ERROR-OPAQUE", "FFMPEG-RESOLUTION-DIVERGENCE", "MCP-TTS-GENERATE-SYNCHRONOUS")


class Fail(Exception):
    """A check failed; the message is printed after FAIL:."""


# --------------------------------------------------------------------------- report parsing


def _first_line(text: str) -> str:
    return (text or "").strip().splitlines()[0] if (text or "").strip() else ""


def parse_junit(path: Path) -> tuple[list[dict], list[str]]:
    """pytest --junitxml -> records {name, tag_text, status, message}, load errors."""
    records, load = [], []
    for case in ET.parse(path).getroot().iter("testcase"):
        name = case.get("name") or ""
        full = f"{case.get('classname')}::{name}"
        status, message = "passed", ""
        if (el := case.find("error")) is not None:
            status, message = "error", (el.get("message") or "") + "\n" + (el.text or "")
        elif (el := case.find("failure")) is not None:
            status, message = "failed", (el.get("message") or "") + "\n" + (el.text or "")
        elif case.find("skipped") is not None:
            status = "skipped"
        if not case.get("classname") and status == "error":
            load.append(f"collection error {full}: {_first_line(message)[:160]}")
            continue
        records.append({"name": full, "tag_text": name, "status": status, "message": message})
    return records, load


def parse_vitest(path: Path) -> tuple[list[dict], list[str]]:
    """Vitest --reporter=json -> records, load errors (a file that failed to load or collect)."""
    j = json.loads(path.read_text(encoding="utf-8"))
    records, load = [], []
    for suite in j.get("testResults", []):
        asserts = suite.get("assertionResults", [])
        if suite.get("message"):  # a file-level error (import, collect, hook), never a test's own assertion
            load.append(f"load error {suite.get('name')}: {_first_line(suite['message'])[:160]}")
        for a in asserts:
            st = a.get("status")
            status = "passed" if st == "passed" else "failed" if st == "failed" else "skipped"
            records.append({"name": a.get("fullName", ""), "tag_text": a.get("fullName", ""), "status": status,
                            "message": "\n".join(a.get("failureMessages") or [])})
    return records, load


def parse_playwright(path: Path) -> tuple[list[dict], list[str]]:
    """Playwright --reporter=json -> records (one per test x repeat), load errors (top-level errors)."""
    j = json.loads(path.read_text(encoding="utf-8"))
    load = [f"top-level error: {_first_line(e.get('message', ''))[:160]}" for e in j.get("errors", [])]
    records: list[dict] = []

    def walk(suite: dict, trail: list[str]) -> None:
        here = trail + ([suite["title"]] if suite.get("title") else [])
        for spec in suite.get("specs", []):
            title = " > ".join(here + [spec.get("title", "")])
            for test in spec.get("tests", []):
                st = test.get("status")
                status = {"expected": "passed", "unexpected": "failed", "flaky": "flaky"}.get(st, "skipped")
                results = test.get("results") or [{}]
                errs = [e.get("message", "") for e in results[-1].get("errors", [])]
                errs.append((results[-1].get("error") or {}).get("message", ""))
                records.append({"name": title, "tag_text": title, "status": status,
                                "message": "\n".join(m for m in errs if m)})
        for child in suite.get("suites", []):
            walk(child, here)

    for s in j.get("suites", []):
        walk(s, [])
    return records, load


PARSERS = {"pytest": parse_junit, "vitest": parse_vitest, "mcp": parse_vitest, "electron": parse_playwright}


def is_assertion(tier: str, message: str) -> bool:
    """RED_RULE item 2: the failure is the test's own assertion, not setup, import or a timeout."""
    first = _first_line(message)
    if tier == "pytest":
        return first.startswith(("AssertionError", "assert ", "Failed: DID NOT RAISE"))
    if tier in ("vitest", "mcp"):
        return re.match(r"(AssertionError\b|Error: expect\()", first) is not None
    errors = [m for m in message.split("\n") if m.strip()]
    return bool(errors) and not errors[0].startswith("Test timeout") and "expect(" in message


def tags_of(tier: str, text: str) -> list[str]:
    if tier == "pytest":
        return [f"{a}.{b}" for a, b in re.findall(r"ac_(\d+)_(\d+)_", text.lower())]
    return [f"{a}.{b}" for a, b in re.findall(r"AC-(\d+)\.(\d+)(?!\d)", text)]


def is_neg(tier: str, text: str) -> bool:
    return "_neg" in text if tier == "pytest" else "[neg]" in text


# --------------------------------------------------------------------------- RED_RULE / green / suite


def evaluate_red(records: list[dict], load: list[str], tier: str, meu: str, exit_code: int) -> list[str]:
    """RED_RULE items 1-5 for one tier of one MEU; returns the problems (empty = PASS)."""
    problems = list(load)
    table = ACS[meu]
    in_tier = {ac for ac, t in table.items() if t == tier}
    pins = in_tier & PINS
    red_acs = in_tier - pins
    decisive = {ac: 0 for ac in red_acs}
    pin_pass = {ac: 0 for ac in pins}
    if not records:
        problems.append("the run reported no tests")
    for r in records:
        tags = [t for t in tags_of(tier, r["tag_text"]) if t.split(".")[0] == meu]
        for t in tags:
            if t not in table:
                problems.append(f"{r['name']}: AC-{t} is not an AC of MEU-{meu}")
            elif table[t] != tier:
                problems.append(f"{r['name']}: AC-{t} is typed {table[t]}, not {tier}")
        tags = [t for t in tags if table.get(t) == tier]
        if not tags:
            if r["status"] in ("failed", "error", "flaky"):
                problems.append(f"untagged test did not pass ({r['status']}): {r['name']}")
            continue
        if any(t in pins for t in tags):
            if any(t not in pins for t in tags):
                problems.append(f"{r['name']}: mixes a pin AC with a Red AC")
            elif r["status"] != "passed":
                problems.append(f"pin test must pass in Red ({r['status']}): {r['name']}")
            else:
                for t in tags:
                    pin_pass[t] += 1
            continue
        if r["status"] == "skipped" or r["status"] == "flaky" or r["status"] == "error":
            problems.append(f"tagged test {r['status']}: {r['name']}: {_first_line(r['message'])[:120]}")
        elif r["status"] == "failed" and not is_assertion(tier, r["message"]):
            problems.append(f"non-assertion failure: {r['name']}: {_first_line(r['message'])[:160]}")
        elif r["status"] == "passed" and not is_neg(tier, r["tag_text"]):
            problems.append(f"tagged test passed in Red (no NEG_MARK): {r['name']}")
        elif r["status"] == "failed" and not is_neg(tier, r["tag_text"]):
            for t in tags:
                decisive[t] += 1
    problems += [f"AC-{ac} has no decisive assertion failure in {tier}" for ac, n in sorted(decisive.items()) if n == 0]
    problems += [f"pin AC-{ac} has no passing test in {tier}" for ac, n in sorted(pin_pass.items()) if n == 0]
    if red_acs and exit_code == 0:
        problems.append("Red run exited 0")
    if not red_acs and exit_code != 0:
        problems.append(f"pin-only run exited {exit_code}")
    return problems


def evaluate_green(records: list[dict], load: list[str], tier: str, meu: str, exit_code: int) -> list[str]:
    problems = evaluate_suite(records, load, exit_code)
    in_tier = {ac for ac, t in ACS[meu].items() if t == tier}
    passing = {ac: 0 for ac in in_tier}
    for r in records:
        for t in tags_of(tier, r["tag_text"]):
            if t in passing:
                if r["status"] == "skipped":
                    problems.append(f"tagged test skipped: {r['name']}")
                elif r["status"] == "passed":
                    passing[t] += 1
    problems += [f"AC-{ac} has no passing test in {tier}" for ac, n in sorted(passing.items()) if n == 0]
    return problems


def evaluate_suite(records: list[dict], load: list[str], exit_code: int) -> list[str]:
    problems = list(load)
    if exit_code != 0:
        problems.append(f"exit {exit_code}")
    if not records:
        problems.append("the run reported no tests")
    problems += [f"{r['status']}: {r['name']}: {_first_line(r['message'])[:120]}"
                 for r in records if r["status"] in ("failed", "error", "flaky")]
    return problems


def _counts(records: list[dict]) -> str:
    c: dict[str, int] = {}
    for r in records:
        c[r["status"]] = c.get(r["status"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items()))


# --------------------------------------------------------------------------- git / fingerprints


def git(*args: str) -> str:
    return subprocess.run(["git", "-c", "core.quotepath=off", *args], capture_output=True, text=True,
                          check=True, encoding="utf-8").stdout


def baseline_sha() -> str:
    p = Path(PLAN) / "baseline.sha"
    if not p.is_file():
        raise Fail(f"{p} missing (row 0 writes it)")
    return p.read_text(encoding="utf-8").strip()


def changed_paths(base: str, paths: list[str] | None = None) -> set[str]:
    """Working-tree paths (under `paths`, or the whole tree) that differ from `base`, plus untracked (not ignored)."""
    spec = ["--", *paths] if paths else []
    diff = git("diff", "--name-only", "-z", base, *spec).split("\0")
    untracked = git("ls-files", "--others", "--exclude-standard", "-z", *spec).split("\0")
    return {p for p in diff + untracked if p}


def is_gated(path: str) -> bool:
    """GATED_PATHS membership: every path except a GATE_EXCLUDED match."""
    return not any(fnmatch.fnmatchcase(path, pattern) for pattern in GATE_EXCLUDED)


def fingerprint_lines(paths: list[str], root: Path) -> list[str]:
    lines = []
    for p in sorted(set(paths)):
        f = root / p
        lines.append(f"{p}\t{hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else 'deleted'}")
    return lines


def fingerprint(exclude: tuple[str, ...] = ()) -> tuple[str, int]:
    """GATE_FINGERPRINT (AUDIT_FINGERPRINT with exclude=(BASELINE,))."""
    paths = [p for p in changed_paths(baseline_sha()) if is_gated(p) and p not in exclude]
    lines = fingerprint_lines(paths, Path("."))
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest(), len(lines)


# --------------------------------------------------------------------------- SSOT helpers


def _yaml(path: str):
    import yaml  # PyYAML is in uv.lock; imported here so the evaluator verbs stay stdlib-only

    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def meu_states() -> dict[str, str]:
    return {r["id"]: r.get("status") for r in _yaml(".agent/context/meu-status.yaml")["meus"]}


def frontmatter(text: str) -> dict[str, str]:
    parts = text.split("---")
    if len(parts) < 3 or text.strip()[:3] != "---":
        raise Fail("no YAML frontmatter")
    return dict(re.findall(r'^(\w+):\s*"?([^"\n]*?)"?\s*$', parts[1], re.M))


def same_file(value: str, root: Path) -> bool:
    """`value` (relative to `root`, or absolute) names this checkout's implementation-plan.md."""
    want = (root / PLAN / "implementation-plan.md").resolve()
    got = Path(value) if Path(value).is_absolute() else root / value
    return os.path.normcase(str(got.resolve())) == os.path.normcase(str(want))


def check_review(text: str, mode: str, cap: int, root: Path | None = None) -> str:
    fm = frontmatter(text)
    target = fm.get("target_plan") or ""
    if not target or not same_file(target, root or Path.cwd()):
        raise Fail(f"target_plan {target!r} is not this checkout's {PLAN}/implementation-plan.md")
    if fm.get("review_mode") != mode:
        raise Fail(f"review_mode {fm.get('review_mode')!r} != {mode}")
    if not fm.get("round", "").isdigit() or not 1 <= int(fm["round"]) <= cap:
        raise Fail(f"round {fm.get('round')!r} outside 1..{cap}")
    if fm.get("verdict") != "approved":
        raise Fail(f"verdict {fm.get('verdict')!r}")
    if fm.get("agent") != REVIEW_AGENT:
        raise Fail(f"agent {fm.get('agent')!r} is not the authorized reviewer {REVIEW_AGENT}")
    return f"{mode} review approved, round {fm['round']}, agent {fm['agent']}"


def grouping_row(state: str) -> str:
    return f"| 33 | `{SLUG}` | MEU-76, MEU-78, MEU-77 | P2 | {state} |"


def section(text: str, heading: str) -> str:
    parts = re.split(rf"^## {re.escape(heading)}[^\n]*$", text, maxsplit=1, flags=re.M)
    if len(parts) < 2:
        raise Fail(f"no '## {heading}' section")
    return parts[1].split("\n## ", 1)[0]


# --------------------------------------------------------------------------- audit / gate


def check_audit(summary: dict, baseline: dict, registry_src: str) -> str:
    """AUDIT_EXPECT over the summary and the rewritten baseline."""
    if summary.get("schema") != "mcp-audit-summary.v1" or summary.get("mode") != "authoritative":
        raise Fail(f"summary schema/mode {summary.get('schema')} {summary.get('mode')}")
    if summary.get("exit_code") != 0:
        raise Fail(f"audit exit_code {summary.get('exit_code')}")
    bad_steps = [s.get("id") for s in summary.get("steps", []) if s.get("verdict") != "pass"]
    if bad_steps or not summary.get("steps"):
        raise Fail(f"audit steps not pass: {bad_steps or 'none recorded'}")
    deltas = {d["key"]: d.get("delta") for d in summary.get("deltas", [])}
    if deltas.get("avkit_tts.cancel") != "FIXED":
        raise Fail(f"avkit_tts.cancel delta {deltas.get('avkit_tts.cancel')!r} != FIXED")
    bad = sorted(k for k, d in deltas.items() if d in ("REGRESSION", "REMOVED"))
    if bad:
        raise Fail(f"audit REGRESSION/REMOVED {bad} (S5)")
    if not (summary.get("cleanup") or {}).get("ok"):
        raise Fail(f"cleanup {summary.get('cleanup')}")
    if (summary.get("discovery") or {}).get("findings"):
        raise Fail(f"discovery findings {summary['discovery']['findings']}")
    if baseline.get("schema") != "mcp-audit-baseline.v1" or baseline.get("mode") != "authoritative":
        raise Fail("baseline is not an authoritative mcp-audit-baseline.v1")
    served = {f"{t}.{a}" for t, a in re.findall(r'\{ tool: "(\w+)", action: "(\w+)", method:', registry_src)}
    entries = {f"{e['tool']}.{e['action']}" for e in baseline.get("entries", [])}
    if entries != served:
        raise Fail(f"baseline coverage missing {sorted(served - entries)} extra {sorted(entries - served)}")
    non_pass = [f"{e['tool']}.{e['action']}" for e in baseline["entries"] if e.get("status") != "pass"]
    if non_pass or baseline.get("findings"):
        raise Fail(f"baseline non-pass entries {non_pass} findings {baseline.get('findings')}")
    if baseline.get("recorded_commit") != summary.get("commit"):
        raise Fail(f"baseline recorded_commit {baseline.get('recorded_commit')} != summary {summary.get('commit')}")
    return f"{len(entries)} actions pass, tts.cancel FIXED, cleanup ok"


def check_gate(r: dict, mcp_floor: int, now_fp: str) -> str:
    if r.get("schema") != "s33-windows-gate.v1":
        raise Fail(f"schema {r.get('schema')}")
    pre = r.get("preflight") or {}
    if not pre.get("agentic_framework_head") or not pre.get("agent_registry_sha256") or pre.get("drift") is not False:
        raise Fail(f"preflight {pre}")
    got = [s.get("id") for s in r.get("stages", [])]
    if got != STAGES:
        raise Fail(f"stages {got} != {STAGES}")
    bad = [s["id"] for s in r["stages"] if s.get("exit") != 0]
    if bad:
        raise Fail(f"stages failed: {bad}")
    py, v, e, m = (r.get(k) or {} for k in ("pytest", "vitest", "e2e", "mcp"))
    py_floor = max(FLOORS["pytest"], r.get("pytest_floor") or 0)
    if py.get("failed") != 0 or (py.get("passed") or 0) < py_floor:
        raise Fail(f"pytest {py} (floor {py_floor})")
    if v.get("failed") != 0 or (v.get("total") or 0) < FLOORS["vitest"]:
        raise Fail(f"vitest {v}")
    if e.get("unexpected") != 0 or e.get("flaky") != 0 or (e.get("expected") or 0) < FLOORS["e2e"]:
        raise Fail(f"e2e {e}")
    if m.get("failed") != 0 or (m.get("passed") or 0) < mcp_floor:
        raise Fail(f"mcp {m} (floor {mcp_floor})")
    fb, fa = r.get("fingerprint_before"), r.get("fingerprint_after")
    if not fb or fb != fa:
        raise Fail(f"GATE_FINGERPRINT changed during the run: {fb} -> {fa}")
    if fa != now_fp:
        raise Fail(f"GATE_FINGERPRINT {fa} != current tree {now_fp}: a GATED_PATHS file changed after the gate")
    return f"pytest {py} vitest {v} e2e {e} mcp {m}"


def openapi_diff(old: dict, new: dict) -> list[str]:
    problems = []
    op, np_ = old.get("paths", {}), new.get("paths", {})
    if set(op) != set(np_):
        problems.append(f"paths added {sorted(set(np_) - set(op))} removed {sorted(set(op) - set(np_))}")
    changed = {p for p in set(op) & set(np_) if op[p] != np_[p]}
    if changed - OPENAPI_PATHS:
        problems.append(f"paths changed outside OPENAPI_DIFF: {sorted(changed - OPENAPI_PATHS)}")
    os_, ns = (d.get("components", {}).get("schemas", {}) for d in (old, new))
    schemas = {k for k in set(os_) | set(ns) if os_.get(k) != ns.get(k)}
    if schemas - OPENAPI_SCHEMAS:
        problems.append(f"schemas changed outside OPENAPI_DIFF: {sorted(schemas - OPENAPI_SCHEMAS)}")
    rest = {k: v for k, v in old.items() if k not in ("paths", "components")}
    if rest != {k: v for k, v in new.items() if k not in ("paths", "components")}:
        problems.append("top-level OpenAPI keys outside paths/components changed")
    return problems


# --------------------------------------------------------------------------- verbs


def v_tier(args: argparse.Namespace, kind: str) -> str:
    report = Path(args.report)
    if not report.is_file():
        raise Fail(f"report {report} missing (exit {args.exit})")
    records, load = PARSERS[args.tier](report)
    if kind == "red":
        problems = evaluate_red(records, load, args.tier, args.meu, args.exit)
    elif kind == "green":
        problems = evaluate_green(records, load, args.tier, args.meu, args.exit)
    else:
        problems = evaluate_suite(records, load, args.exit)
    if problems:
        raise Fail(f"{kind} {args.tier}{' MEU-' + args.meu if args.meu else ''}: " + "; ".join(problems[:12]))
    return f"{kind} {args.tier}{' MEU-' + args.meu if args.meu else ''}: {_counts(records)}"


def v_fingerprint(args: argparse.Namespace) -> str:
    fp, n = fingerprint(tuple(args.exclude))
    Path(args.out).write_text(fp + "\n", encoding="utf-8")
    return f"fingerprint {fp} over {n} changed paths -> {args.out}"


def v_meu_state(args: argparse.Namespace) -> str:
    rows = meu_states()
    bad = {m: rows.get(m) for m in MEUS if rows.get(m) != args.expect}
    if bad:
        raise Fail(f"MEU state {bad} != {args.expect}")
    return f"{', '.join(MEUS)} {args.expect}"


def v_prereq_auth(_: argparse.Namespace) -> str:
    p = Path(PLAN) / "walkthrough.md"
    if not p.is_file():
        raise Fail(f"{p} missing")
    body = section(p.read_text(encoding="utf-8"), "Execution authorization")
    if not re.search(r"^> \S", body, re.M) or not re.search(r"\b20\d\d-\d\d-\d\d\b", body):
        raise Fail("§Execution authorization has no quoted user message with a date")
    return "execution authorization recorded"


def v_baseline_counts(args: argparse.Namespace) -> str:
    out = Path(PLAN) / "baseline-counts.json"
    records, load = parse_vitest(Path(args.report))
    problems = evaluate_suite(records, load, args.exit)
    if problems:
        raise Fail("baseline MCP suite is not green: " + "; ".join(problems[:8]))
    passed = sum(1 for r in records if r["status"] == "passed")
    if out.is_file():
        prior = json.loads(out.read_text(encoding="utf-8"))
        return f"baseline-counts.json kept (first measurement): {prior} (this run: {passed})"
    out.write_text(json.dumps({"mcp_passed": passed, "mcp_total": len(records), "commit": baseline_sha(),
                               "measured_at": datetime.now(timezone.utc).isoformat()}, indent=2) + "\n",
                   encoding="utf-8")
    return f"baseline-counts.json mcp_passed {passed}"


def v_review_check(args: argparse.Namespace) -> str:
    return check_review(Path(args.target).read_text(encoding="utf-8"), args.mode, args.cap)


def v_audit_check(args: argparse.Namespace) -> str:
    summary = json.loads(Path(args.summary).read_text(encoding="utf-8-sig"))
    baseline = json.loads(Path(BASELINE).read_text(encoding="utf-8"))
    return check_audit(summary, baseline, Path("mcp-server/src/toolsets/registry.ts").read_text(encoding="utf-8"))


def check_audit_fp(rec: dict, now: str) -> str:
    """AUDIT_FINGERPRINT: measured before the audit prep and after baseline_carry, equal, and equal to `now`."""
    before, after = rec.get("before"), rec.get("after")
    if not before or before != after:
        raise Fail(f"AUDIT_FINGERPRINT changed during the audit: {before} -> {after}")
    if after != now:
        raise Fail(f"AUDIT_FINGERPRINT {after} != current {now}: the code changed after the audit")
    return after


def v_audit_fp(args: argparse.Namespace) -> str:
    rec = {"before": Path(args.before).read_text(encoding="utf-8").strip(),
           "after": Path(args.after).read_text(encoding="utf-8").strip()}
    check_audit_fp(rec, rec["after"])
    Path(args.out).write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return f"AUDIT_FINGERPRINT {rec['after']} before and after the audit -> {args.out}"


def v_gate_check(_: argparse.Namespace) -> str:
    plan = Path(PLAN)
    r = json.loads((plan / "windows-gate-result.json").read_text(encoding="utf-8-sig"))
    counts = json.loads((plan / "baseline-counts.json").read_text(encoding="utf-8"))
    gate_now, _n = fingerprint()
    msg = check_gate(r, int(counts["mcp_passed"]), gate_now)
    audit_now, _n = fingerprint((BASELINE,))
    check_audit_fp(json.loads((plan / "audit-fingerprint.json").read_text(encoding="utf-8")), audit_now)
    summary = json.loads((plan / "mcp-audit-summary.json").read_text(encoding="utf-8-sig"))
    baseline = json.loads(Path(BASELINE).read_text(encoding="utf-8"))
    audit = check_audit(summary, baseline, Path("mcp-server/src/toolsets/registry.ts").read_text(encoding="utf-8"))
    return f"gate {msg}; fingerprint {gate_now}; audit {audit}"


def v_task_state(_: argparse.Namespace) -> str:
    rows = [l for l in (Path(PLAN) / "task.md").read_text(encoding="utf-8").splitlines() if re.match(r"^\| [0-9]+ \|", l)]
    if len(rows) != 13:
        raise Fail(f"expected 13 implementation rows (0-12), got {len(rows)}")
    for l in rows:
        s = l.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
        if s == "[x]" or (s == "[B]" and "follow-up" in l and "B-" in l):
            continue
        raise Fail(f"unfinished row: {l[:60]}")
    return "implementation rows 0-12 done"


def v_ssot_review(_: argparse.Namespace) -> str:
    v_meu_state(argparse.Namespace(expect="ready_for_review"))
    g = Path(GROUPING).read_text(encoding="utf-8")
    if grouping_row("in review") not in g:
        raise Fail(f"grouping row missing: {grouping_row('in review')}")
    focus = Path(".agent/context/current-focus.md").read_text(encoding="utf-8")
    if SLUG not in focus or "ready_for_review" not in focus:
        raise Fail("current-focus.md does not record Session 33 ready_for_review")
    return "SSOT review state"


def v_api_scope(_: argparse.Namespace) -> str:
    base = baseline_sha()
    plan_text = (Path(PLAN) / "implementation-plan.md").read_text(encoding="utf-8")
    frozen = sorted(changed_paths(base, ["ui/src/main", "tools"]))
    if frozen:
        raise Fail(f"PRODUCT_SCOPE frozen paths changed: {frozen}")
    rows = re.findall(r"^\| `((?:ui|packages|mcp-server|tests)/[^`]+|openapi\.committed\.json|"
                      r"\.agent/skills/mcp-tool-audit/resources/baseline-snapshot\.json)` \| (modify|create) \|",
                      plan_text, re.M)
    listed = {p for p, _a in rows}
    missing = sorted(p for p, a in rows if a == "create" and not Path(p).is_file())
    if missing:
        raise Fail(f"Files Modified 'create' rows that do not exist: {missing}")
    census = section((Path(PLAN) / "walkthrough.md").read_text(encoding="utf-8"), "Census")
    repair_sites = {p for line in census.splitlines() if "repair (" in line for p in re.findall(r"`(tests/[^`]+)`", line)}
    product = changed_paths(base, ["ui", "packages", "mcp-server", "tests", "openapi.committed.json",
                                   ".agent/skills/mcp-tool-audit", "pyproject.toml", "uv.lock"])
    extra = sorted(product - listed - repair_sites)
    if extra:
        raise Fail(f"changes outside Files Modified and the §Census repair sites: {extra}")
    for n, f in TA_SITES.items():
        if f"TA-{n} (Session 33" not in Path(f).read_text(encoding="utf-8"):
            raise Fail(f"TA-{n} site {f} carries no 'TA-{n} (Session 33' comment")
    stray = set()
    for f in sorted(p for p in product if p.startswith(("tests/", "ui/tests/", "mcp-server/tests/")) and Path(p).is_file()):
        stray |= {int(n) for n in re.findall(r"TA-(\d+) \(Session 33", Path(f).read_text(encoding="utf-8"))
                  if int(n) not in TA_SITES or TA_SITES[int(n)] != f}
    if stray:
        raise Fail(f"TA comments outside TEST_AMENDMENTS sites: {sorted(stray)}")
    old = json.loads(git("show", f"{base}:openapi.committed.json"))
    new = json.loads(Path("openapi.committed.json").read_text(encoding="utf-8"))
    problems = openapi_diff(old, new)
    if problems:
        raise Fail("OPENAPI_DIFF: " + "; ".join(problems))
    return f"product scope: {len(product)} changed files, all listed; TA-1..TA-11 marked; OPENAPI_DIFF holds"


FILES_MODIFIED_ROW = re.compile(r"^\| `([^`]+)` \| (modify|create) \|", re.M)
OTHER_WORKTREE = "P:/av-kit"


def files_modified(plan_text: str) -> list[str]:
    return sorted({p for p, _a in FILES_MODIFIED_ROW.findall(plan_text)})


def v_overlap(args: argparse.Namespace) -> str:
    """S4: nothing merged since planning touched a Files Modified path. D-10: record P:/av-kit's overlap."""
    files = files_modified((Path(PLAN) / "implementation-plan.md").read_text(encoding="utf-8"))
    moved = [p for p in git("diff", "--name-only", args.planning_head, "HEAD", "--", *files).splitlines() if p]
    if moved:
        raise Fail(f"S4: Files Modified paths changed since planning ({args.planning_head[:10]}..HEAD): {moved}")
    head = git("rev-parse", "HEAD").strip()
    other = ["git", "-C", OTHER_WORKTREE, "-c", "core.quotepath=off"]
    run = lambda *a: subprocess.run([*other, *a], capture_output=True, text=True, check=True, encoding="utf-8").stdout
    base = run("merge-base", "HEAD", head).strip()
    touched = set(run("diff", "--name-only", "HEAD").splitlines()) | set(run("diff", "--name-only", "--cached").splitlines())
    touched |= set(run("log", "--name-only", "--format=", f"{base}..HEAD").splitlines())
    branch = run("rev-parse", "--abbrev-ref", "HEAD").strip()
    overlap = sorted(p for p in touched if p in files)
    lines = [f"{OTHER_WORKTREE} branch {branch}, merge-base {base}", f"overlapping Files Modified paths: {len(overlap)}"]
    Path(args.out).write_text("\n".join(lines + overlap) + "\n", encoding="utf-8")
    return f"no Files Modified path moved since planning; {len(overlap)} overlap(s) with {OTHER_WORKTREE} -> {args.out}"


TEST_PREFIXES = ("tests/", "ui/tests/", "mcp-server/tests/")


def product_files(plan_text: str) -> dict[str, list[str]]:
    """MEU -> the non-test Files Modified paths of its section (openapi and the audit baseline excluded)."""
    out: dict[str, list[str]] = {}
    for meu, body in re.findall(r"^### MEU-(\d+) [^\n]*\n(.*?)(?=^### |^## )", plan_text, re.M | re.S):
        out[meu] = sorted({p for p in files_modified(body) if not p.startswith(TEST_PREFIXES)
                           and p not in ("openapi.committed.json", BASELINE)})
    return out


def v_snapshot(args: argparse.Namespace) -> str:
    """Hash every product Files Modified path; a gate writes it on PASS for the next MEU's red-guard."""
    files = sorted({p for ps in product_files((Path(PLAN) / "implementation-plan.md").read_text(encoding="utf-8")).values()
                    for p in ps})
    Path(args.out).write_text(json.dumps(dict(l.split("\t") for l in fingerprint_lines(files, Path("."))), indent=2) + "\n",
                              encoding="utf-8")
    return f"snapshot of {len(files)} product files -> {args.out}"


def v_red_guard(args: argparse.Namespace) -> str:
    """Red runs before any production edit of the MEU: its product files equal the previous gate's snapshot
    (or baseline.sha for the first MEU)."""
    files = product_files((Path(PLAN) / "implementation-plan.md").read_text(encoding="utf-8")).get(args.meu)
    if not files:
        raise Fail(f"no product Files Modified rows for MEU-{args.meu}")
    if args.snapshot:
        snap = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
        now = dict(l.split("\t") for l in fingerprint_lines(files, Path(".")))
        moved = sorted(p for p in files if snap.get(p) != now[p])
        basis = f"the snapshot {args.snapshot}"
    else:
        # A created file is untracked until committed, so `git diff` alone would not see it.
        moved = sorted({p for p in (git("diff", "--name-only", baseline_sha(), "--", *files)
                                    + "\n" + git("ls-files", "--others", "--exclude-standard", "--", *files)).splitlines()
                        if p})
        basis = "baseline.sha"
    if moved:
        raise Fail(f"MEU-{args.meu} product files changed before Red (vs {basis}): {moved}")
    return f"MEU-{args.meu}: {len(files)} product files unchanged vs {basis}"


def v_handoff_ac(_: argparse.Namespace) -> str:
    """Each MEU handoff names every one of its own ACs by full id (the closeout tool matches only AC-<n>)."""
    for meu in ACS:
        path = Path(f".agent/context/handoffs/2026-10-14-{SLUG}-MEU-{meu}-handoff.md")
        text = path.read_text(encoding="utf-8")
        missing = [ac for ac in ACS[meu] if not re.search(rf"AC-{re.escape(ac)}(?!\d)", text)]
        if missing:
            raise Fail(f"{path} does not name AC-{', AC-'.join(missing)}")
    return "each handoff names all of its MEU's ACs"


HUB = [
    ("docs/build-plan/04-rest-api.md", ["ExtractError", "Session 33 plan D-15"], []),
    ("docs/build-plan/03-service-layer.md",
     ["nothing is re-raised (Session 33 plan D-19)", "Session 33 plan D-18", "Session 33 plan D-16",
      "interrupted by restart"], ["is then re-raised (500)"]),
    ("docs/build-plan/02-infrastructure.md",
     ["Resolve on every use; no cache (Session 33 plan D-16)", "resources/ffmpeg/ffmpeg.exe"], ["Probe binary once; cache"]),
    ("docs/build-plan/07-distribution.md", ["resources/ffmpeg"], ["resources/extra/ffmpeg"]),
    ("docs/build-plan/05-mcp-server.md",
     ["(stops a running job; its partial output is removed)", "generate returns the job at once"],
     ["files already written stay", "generate is one job"]),
]


def v_hub(_: argparse.Namespace) -> str:
    for path, need, gone in HUB:
        t = Path(path).read_text(encoding="utf-8")
        miss = [s for s in need if s not in t]
        left = [s for s in gone if s in t]
        if miss or left:
            raise Fail(f"{path}: missing {miss} still present {left}")
    return f"hub strings in {len(HUB)} files"


def v_post_review_state(_: argparse.Namespace) -> str:
    v_meu_state(argparse.Namespace(expect="approved"))
    issues = {i["id"]: i for i in _yaml(".agent/context/known-issues.yaml")["issues"]}
    for i in ISSUES:
        it = issues.get(i) or {}
        ev = (it.get("verification") or {}).get("evidence_file") or ""
        if it.get("status") != "resolved" or not ev.startswith(f"{PLAN}/"):
            raise Fail(f"{i} status {it.get('status')} evidence {ev!r}")
    if grouping_row("approved") not in Path(GROUPING).read_text(encoding="utf-8"):
        raise Fail("grouping Session 33 not approved")
    if "2026-10-14-backend-robustness" not in Path("docs/execution/metrics.md").read_text(encoding="utf-8"):
        raise Fail("metrics row missing")
    return "POST_REVIEW_STATE"


# --------------------------------------------------------------------------- selftest


def _junit(cases: list[tuple[str, str, str]]) -> str:
    body = []
    for name, kind, msg in cases:
        inner = f'<{kind} message="{msg}">{msg}</{kind}>' if kind in ("failure", "error") else (
            "<skipped/>" if kind == "skipped" else "")
        cls = "" if kind == "collect" else "tests.unit.test_x"
        if kind == "collect":
            inner = f'<error message="{msg}">{msg}</error>'
        body.append(f'<testcase classname="{cls}" name="{name}">{inner}</testcase>')
    return f'<testsuites><testsuite name="pytest">{"".join(body)}</testsuite></testsuites>'


def _vitest(tests: list[tuple[str, str, str]], load: str = "") -> str:
    res = [{"fullName": n, "status": s, "failureMessages": [m] if m else []} for n, s, m in tests]
    return json.dumps({"testResults": [{"name": "x.test.ts", "message": load, "assertionResults": res}]})


def _pw(tests: list[tuple[str, str, str]], errors: list[str] | None = None) -> str:
    specs = [{"title": n, "tests": [{"status": s, "results": [{"errors": [{"message": m}] if m else []}]}]}
             for n, s, m in tests]
    return json.dumps({"errors": [{"message": e} for e in (errors or [])], "suites": [{"title": "f.ts", "specs": specs}]})


def selftest() -> int:
    ok = True
    tmp = Path(tempfile.mkdtemp(prefix="s33-selftest-"))

    def run(label: str, tier: str, kind: str, text: str, meu: str, exit_code: int, expect_pass: bool) -> None:
        nonlocal ok
        f = tmp / f"{label}.{'xml' if tier == 'pytest' else 'json'}"
        f.write_text(text, encoding="utf-8")
        records, load = PARSERS[tier](f)
        fn = {"red": evaluate_red, "green": evaluate_green}[kind]
        problems = fn(records, load, tier, meu, exit_code) if kind != "suite" else evaluate_suite(records, load, exit_code)
        passed = not problems
        mark = "ok " if passed == expect_pass else "BAD"
        ok &= passed == expect_pass
        print(f"  {mark} {label}: {'PASS' if passed else 'FAIL'} (expected {'PASS' if expect_pass else 'FAIL'})"
              + ("" if passed else f" - {problems[0][:90]}"))

    a = "AssertionError: assert 500 == 422"
    py76 = [(f"test_ac_76_{n}_x", "failure", a) for n in range(1, 8)] + [("test_old_passes", "", "")]
    run("pytest red76 good", "pytest", "red", _junit(py76), "76", 1, True)
    run("pytest red76 with a NEG_MARK pass", "pytest", "red", _junit(py76 + [("test_ac_76_2_zero_events_neg", "", "")]), "76", 1, True)
    run("pytest red76 TypeError (non-assertion)", "pytest", "red",
        _junit(py76[:-2] + [("test_ac_76_7_x", "failure", "TypeError: unexpected keyword 'spawn'")]), "76", 1, False)
    run("pytest red76 missing AC-76.7", "pytest", "red", _junit(py76[:6]), "76", 1, False)
    run("pytest red76 tagged pass without NEG_MARK", "pytest", "red", _junit(py76 + [("test_ac_76_1_extra", "", "")]), "76", 1, False)
    run("pytest red76 untagged failure", "pytest", "red", _junit(py76 + [("test_old_breaks", "failure", a)]), "76", 1, False)
    run("pytest red76 collection error", "pytest", "red", _junit(py76 + [("tests.unit.test_x", "collect", "ImportError: x")]), "76", 1, False)
    run("pytest red76 ac_76_10 is not AC-76.1", "pytest", "red", _junit(py76 + [("test_ac_76_10_x", "failure", a)]), "76", 1, False)
    run("pytest red76 exit 0", "pytest", "red", _junit(py76), "76", 0, False)
    run("pytest red76 DID NOT RAISE counts", "pytest", "red",
        _junit(py76[:6] + [("test_ac_76_7_x", "failure", "Failed: DID NOT RAISE &lt;class 'X'&gt;")]), "76", 1, True)
    v_ok = [("api AC-76.8 throws request id", "failed", "AssertionError: expected 'a' to be 'b'"), ("old", "passed", "")]
    run("vitest red76 good", "vitest", "red", _vitest(v_ok), "76", 1, True)
    run("vitest red76 load error", "vitest", "red", _vitest(v_ok, load="Failed to resolve import"), "76", 1, False)
    run("vitest red76 TypeError", "vitest", "red",
        _vitest([("api AC-76.8 x", "failed", "TypeError: Cannot read properties of undefined")]), "76", 1, False)
    run("vitest red76 AC-76.80 not AC-76.8", "vitest", "red",
        _vitest([("AC-76.80 x", "failed", "AssertionError: expected 1")]), "76", 1, False)
    run("mcp red76 jest-dom style expect", "mcp", "red",
        _vitest([("census AC-76.9 bot wall", "failed", "Error: expect(received).toMatch(expected)")]), "76", 1, True)
    e_ok = [("AC-78.9 deps ffprobe row", "unexpected", "Error: expect(locator).toBeVisible() failed")]
    run("electron red78 good", "electron", "red", _pw(e_ok), "78", 1, True)
    run("electron red78 test timeout", "electron", "red",
        _pw([("AC-78.9 x", "unexpected", "Test timeout of 30000ms exceeded.")]), "78", 1, False)
    run("electron red78 top-level error", "electron", "red", _pw(e_ok, errors=["Error: launch failed"]), "78", 1, False)
    pin = [("AC-77.14 run bar polls", "expected", "")]
    run("electron red77 pin passes", "electron", "red", _pw(pin), "77", 0, True)
    run("electron red77 pin fails", "electron", "red", _pw([("AC-77.14 x", "unexpected", "Error: expect(x)")]), "77", 1, False)
    run("electron red77 pin flaky", "electron", "red", _pw([("AC-77.14 x", "flaky", "")]), "77", 0, False)
    run("pytest green77 needs every AC", "pytest", "green", _junit([("test_ac_77_1_x", "", "")]), "77", 0, False)
    run("pytest green77 good", "pytest", "green", _junit([(f"test_ac_77_{n}_x", "", "") for n in range(1, 12)]), "77", 0, True)
    run("pytest green77 a failure", "pytest", "green",
        _junit([(f"test_ac_77_{n}_x", "", "") for n in range(1, 12)] + [("test_old", "failure", a)]), "77", 1, False)

    # Fingerprint: order-independent and content-sensitive.
    (tmp / "a.txt").write_text("1", encoding="utf-8")
    (tmp / "b.txt").write_text("2", encoding="utf-8")
    l1 = fingerprint_lines(["b.txt", "a.txt", "gone.txt"], tmp)
    l2 = fingerprint_lines(["a.txt", "gone.txt", "b.txt"], tmp)
    (tmp / "a.txt").write_text("3", encoding="utf-8")
    l3 = fingerprint_lines(["a.txt", "b.txt", "gone.txt"], tmp)
    fp_ok = l1 == l2 and l1 != l3 and l1[-1].endswith("\tdeleted")
    print(f"  {'ok ' if fp_ok else 'BAD'} fingerprint lines sorted, content-bound, deletions recorded")
    ok &= fp_ok
    # GATED_PATHS: the whole tree minus GATE_EXCLUDED (gate inputs outside code dirs are gated).
    gated_cases = [("ui/src/x.ts", True), (".agent/workflows/mcp-audit.md", True), (".agent/docs/commands.md", True),
                   ("docs/execution/plans/TASK-TEMPLATE.md", True), (f"{PLAN}/implementation-plan.md", True),
                   (f"{PLAN}/baseline_carry.py", True), (BASELINE, True), (".agent/context/meu-status.yaml", False),
                   (f"{PLAN}/windows-gate-result.json", False), (f"{PLAN}/task.md", False),
                   (".agent/context/handoffs/2026-10-14-backend-robustness-MEU-77-handoff.md", False),
                   (".agent/context/handoffs/2026-09-26-framework-update-adoption-implementation-critical-review.md", True)]
    for path, expect in gated_cases:
        good_gate = is_gated(path) == expect
        print(f"  {'ok ' if good_gate else 'BAD'} GATED_PATHS {path}: {'gated' if is_gated(path) else 'excluded'}")
        ok &= good_gate
    for label, rec, now, expect in [("audit fp good", {"before": "f", "after": "f"}, "f", True),
                                    ("audit fp moved during the audit", {"before": "e", "after": "f"}, "f", False),
                                    ("audit fp tree changed after", {"before": "f", "after": "f"}, "g", False),
                                    ("audit fp missing before", {"after": "f"}, "f", False)]:
        try:
            check_audit_fp(rec, now)
            passed = True
        except Fail:
            passed = False
        print(f"  {'ok ' if passed == expect else 'BAD'} {label}: {'PASS' if passed else 'FAIL'}")
        ok &= passed == expect

    # OPENAPI_DIFF.
    old = {"openapi": "3.1.0", "paths": {"/api/v1/tts/generate": {"post": 1}, "/api/v1/tts/{id}": {"get": 1},
                                         "/api/v1/health": {"get": 1}},
           "components": {"schemas": {"TTSJobOut": {"a": 1}, "Other": {"b": 1}}}}
    cases = [
        ("openapi allowed change", {**old, "paths": {**old["paths"], "/api/v1/tts/generate": {"post": 2}},
                                    "components": {"schemas": {"TTSJobOut": {"a": 2}, "Other": {"b": 1}}}}, True),
        ("openapi added path", {**old, "paths": {**old["paths"], "/api/v1/new": {}}}, False),
        ("openapi other schema", {**old, "components": {"schemas": {"TTSJobOut": {"a": 1}, "Other": {"b": 2}}}}, False),
        ("openapi other path", {**old, "paths": {**old["paths"], "/api/v1/health": {"get": 2}}}, False),
        ("openapi job route by its committed template {id}", {**old, "paths": {**old["paths"],
                                                                                "/api/v1/tts/{id}": {"get": 2}}}, True),
    ]
    for label, new, expect in cases:
        passed = not openapi_diff(old, new)
        print(f"  {'ok ' if passed == expect else 'BAD'} {label}: {'PASS' if passed else 'FAIL'}")
        ok &= passed == expect

    # AUDIT_EXPECT.
    reg = '{ tool: "avkit_tts", action: "cancel", method: "DELETE" }\n{ tool: "avkit_tts", action: "get", method: "GET" }'
    base_ok = {"schema": "mcp-audit-baseline.v1", "mode": "authoritative", "recorded_commit": "c1",
               "entries": [{"tool": "avkit_tts", "action": "cancel", "status": "pass"},
                           {"tool": "avkit_tts", "action": "get", "status": "pass"}], "findings": []}
    summ_ok = {"schema": "mcp-audit-summary.v1", "mode": "authoritative", "exit_code": 0, "commit": "c1",
               "steps": [{"id": "tts.cancel", "verdict": "pass"}], "deltas": [{"key": "avkit_tts.cancel", "delta": "FIXED"}],
               "cleanup": {"ok": True}, "discovery": {"findings": []}}
    audit_cases = [
        ("audit good", summ_ok, base_ok, True),
        ("audit cancel not FIXED", {**summ_ok, "deltas": [{"key": "avkit_tts.cancel", "delta": "UNCHANGED"}]}, base_ok, False),
        ("audit regression", {**summ_ok, "deltas": summ_ok["deltas"] + [{"key": "avkit_tts.get", "delta": "REGRESSION"}]}, base_ok, False),
        ("audit cleanup failed", {**summ_ok, "cleanup": {"ok": False}}, base_ok, False),
        ("audit baseline misses an action", summ_ok, {**base_ok, "entries": base_ok["entries"][:1]}, False),
        ("audit baseline commit drift", summ_ok, {**base_ok, "recorded_commit": "c0"}, False),
    ]
    for label, s, b, expect in audit_cases:
        try:
            check_audit(s, b, reg)
            passed = True
        except Fail:
            passed = False
        print(f"  {'ok ' if passed == expect else 'BAD'} {label}: {'PASS' if passed else 'FAIL'}")
        ok &= passed == expect

    # gate-check counts and fingerprints.
    gate_ok = {"schema": "s33-windows-gate.v1", "preflight": {"agentic_framework_head": "h", "agent_registry_sha256": "r", "drift": False},
               "stages": [{"id": s, "exit": 0} for s in STAGES], "pytest": {"passed": 700, "failed": 0},
               "vitest": {"total": 800, "failed": 0}, "e2e": {"expected": 140, "unexpected": 0, "flaky": 0},
               "mcp": {"passed": 400, "failed": 0}, "fingerprint_before": "f", "fingerprint_after": "f", "pytest_floor": 690}
    gate_cases = [
        ("gate good", gate_ok, "f", True),
        ("gate tree changed after", gate_ok, "g", False),
        ("gate stage order", {**gate_ok, "stages": list(reversed(gate_ok["stages"]))}, "f", False),
        ("gate e2e flaky", {**gate_ok, "e2e": {"expected": 140, "unexpected": 0, "flaky": 1}}, "f", False),
        ("gate pytest under carried floor", {**gate_ok, "pytest_floor": 701}, "f", False),
        ("gate mcp under row-0 floor", {**gate_ok, "mcp": {"passed": 399, "failed": 0}}, "f", False),
        ("gate fingerprint moved in run", {**gate_ok, "fingerprint_after": "g"}, "g", False),
    ]
    for label, r, now, expect in gate_cases:
        try:
            check_gate(r, 400, now)
            passed = True
        except Fail:
            passed = False
        print(f"  {'ok ' if passed == expect else 'BAD'} {label}: {'PASS' if passed else 'FAIL'}")
        ok &= passed == expect

    # review-check frontmatter.
    good = (f'---\ndate: "2026-10-15"\nreview_mode: plan\ntarget_plan: {PLAN}/implementation-plan.md\n'
            f'verdict: approved\nfindings_count: 0\nround: 2\nagent: {REVIEW_AGENT}\n---\nbody')
    root = tmp / "wt"
    (root / PLAN).mkdir(parents=True)
    (root / PLAN / "implementation-plan.md").write_text("plan", encoding="utf-8")
    absolute = good.replace(f"target_plan: {PLAN}/", f"target_plan: {root.as_posix()}/{PLAN}/")
    other = good.replace(f"target_plan: {PLAN}/", f"target_plan: {(tmp / 'other').as_posix()}/{PLAN}/")
    review_cases = [("review good", good, True), ("review absolute worktree target", absolute, True),
                    ("review other checkout target", other, False),
                    ("review self-authored agent", good.replace(REVIEW_AGENT, "claude-opus-5-5"), False),
                    ("review changes_required", good.replace("approved", "changes_required"), False),
                    ("review over cap", good.replace("round: 2", "round: 4"), False)]
    for label, text, expect in review_cases:
        try:
            check_review(text, "plan", 3, root)
            passed = True
        except Fail:
            passed = False
        print(f"  {'ok ' if passed == expect else 'BAD'} {label}: {'PASS' if passed else 'FAIL'}")
        ok &= passed == expect

    print("PASS selftest" if ok else "FAIL selftest")
    return 0 if ok else 1


# --------------------------------------------------------------------------- CLI


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    for kind in ("red", "green", "suite"):
        p = sub.add_parser(kind)
        p.add_argument("--tier", choices=sorted(PARSERS), required=True)
        p.add_argument("--meu", choices=sorted(ACS), required=kind != "suite")
        p.add_argument("--report", required=True)
        p.add_argument("--exit", type=int, required=True)
    p = sub.add_parser("fingerprint")
    p.add_argument("--out", required=True)
    p.add_argument("--exclude", action="append", default=[])
    sub.add_parser("meu-state").add_argument("--expect", required=True)
    p = sub.add_parser("baseline-counts")
    p.add_argument("--report", required=True)
    p.add_argument("--exit", type=int, required=True)
    p = sub.add_parser("review-check")
    p.add_argument("--target", required=True)
    p.add_argument("--mode", choices=("plan", "execution"), required=True)
    p.add_argument("--cap", type=int, required=True)
    sub.add_parser("audit-check").add_argument("--summary", required=True)
    p = sub.add_parser("audit-fp")
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--out", required=True)
    sub.add_parser("snapshot").add_argument("--out", required=True)
    p = sub.add_parser("red-guard")
    p.add_argument("--meu", choices=sorted(ACS), required=True)
    p.add_argument("--snapshot", default="")
    p = sub.add_parser("overlap")
    p.add_argument("--planning-head", required=True)
    p.add_argument("--out", required=True)
    for verb in ("prereq-auth", "gate-check", "task-state", "ssot-review", "api-scope", "handoff-ac", "hub",
                 "post-review-state", "selftest"):
        sub.add_parser(verb)
    args = ap.parse_args()
    if args.verb == "selftest":
        return selftest()
    handlers = {
        "red": lambda a: v_tier(a, "red"), "green": lambda a: v_tier(a, "green"), "suite": lambda a: v_tier(a, "suite"),
        "fingerprint": v_fingerprint, "meu-state": v_meu_state, "prereq-auth": v_prereq_auth,
        "baseline-counts": v_baseline_counts, "review-check": v_review_check, "audit-check": v_audit_check, "audit-fp": v_audit_fp,
        "gate-check": v_gate_check, "task-state": v_task_state, "ssot-review": v_ssot_review,
        "api-scope": v_api_scope, "hub": v_hub, "overlap": v_overlap, "handoff-ac": v_handoff_ac,
        "snapshot": v_snapshot, "red-guard": v_red_guard, "post-review-state": v_post_review_state,
    }
    try:
        print(f"PASS {handlers[args.verb](args)}")
        return 0
    except Fail as err:
        print(f"FAIL: {err}")
        return 1
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, ET.ParseError, KeyError) as err:
        print(f"FAIL: {type(err).__name__}: {err}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
