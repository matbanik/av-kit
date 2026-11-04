"""Plan-local checks for Session 26 `2026-09-28-p11-capture-settings`.

Read-only helper. It never edits repository files; it reads a test-reporter JSON file,
this project's `task.md`, or `.agent/context/meu-status.yaml` and exits non-zero when the
named predicate does not hold. `self-test` builds its fixtures in a temporary directory.

Subcommands
-----------
red          Assertion-Red oracle for a Vitest or Playwright JSON report (RED_ORACLE).
rows         Every numbered task row is `[x]` or `[B]` (TASK_ROWS_DONE).
meu-state    Named MEUs carry the expected status (and, optionally, plan binding).
counts       Vitest/Playwright JSON totals meet floors with zero failures (COUNT_FLOORS).
post-review  POST_REVIEW_STATE documents agree with the SSOT next MEU.
self-test    Proves each predicate passes on a good fixture and fails on its adversary.

Exit codes: 0 predicate holds, 1 predicate refused, 2 input unreadable (fail closed).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

#: A failure counts as assertion Red only when its message comes from an assertion.
#: Launch, build, import and collection failures carry none of these markers.
ASSERTION_MARKERS = re.compile(r"AssertionError|expect\(|Expected[: ]|toBe|toHave|toContain|toMatch")
#: Numbered implementation rows and H1/H2 rows in task.md; divider rows have an empty id.
ROW_ID = re.compile(r"^(?:\d+|H[12]-\d+[a-z]?)$")
STATUS_CELL = re.compile(r"`?\[(?P<mark>[ x/B])\]`?")
#: A new test file whose module under test does not exist yet fails to collect with one of
#: these messages. That is Red for the file (the module is absent), never for a syntax error.
MODULE_MISSING = re.compile(r"Failed to resolve import|Cannot find module|Failed to load url|does not provide an export")
#: The MEUs this plan binds; `--plan` checks their execution_plan field.
SESSION_MEUS = frozenset({"MEU-57", "MEU-58"})


class Refused(Exception):
    """Predicate evaluated and does not hold."""


class Unreadable(Exception):
    """Predicate could not be evaluated. Never reported as a pass."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Unreadable(f"cannot read JSON report {path}: {exc}") from exc


def _vitest_failures(
    report: dict[str, Any], new_files: list[str]
) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (failed assertion (title, message) pairs, disallowed collection errors).

    A collection failure is allowed only for a declared NEW test file whose message names a
    missing module; every declared new file must show exactly that failure.
    """
    failures: list[tuple[str, str]] = []
    collection: list[str] = []
    new_seen: set[str] = set()
    results = report.get("testResults")
    if not isinstance(results, list):
        raise Unreadable("Vitest report has no testResults array")
    for file_result in results:
        assertions = file_result.get("assertionResults") or []
        name = str(file_result.get("name", "?")).replace("\\", "/")
        if file_result.get("status") == "failed" and not assertions:
            declared = next((n for n in new_files if name.endswith(n)), None)
            if declared is not None and MODULE_MISSING.search(str(file_result.get("message", ""))):
                new_seen.add(declared)
            else:
                collection.append(name)
        for case in assertions:
            if case.get("status") == "failed":
                title = str(case.get("fullName") or case.get("title") or "")
                message = "\n".join(str(m) for m in case.get("failureMessages") or [])
                failures.append((title, message))
    collection.extend(f"declared new file without missing-module failure: {n}" for n in new_files
                      if n not in new_seen)
    return failures, collection


def _walk_playwright(suite: dict[str, Any], prefix: str, out: list[tuple[str, str]]) -> None:
    title = f"{prefix} {suite.get('title', '')}".strip()
    for spec in suite.get("specs") or []:
        spec_title = f"{title} {spec.get('title', '')}".strip()
        for test in spec.get("tests") or []:
            for result in test.get("results") or []:
                if result.get("status") in {"failed", "timedOut"}:
                    errors = result.get("errors") or []
                    if result.get("error"):
                        errors = [result["error"], *errors]
                    message = "\n".join(str(e.get("message", "")) for e in errors if isinstance(e, dict))
                    out.append((spec_title, message))
    for child in suite.get("suites") or []:
        _walk_playwright(child, title, out)


def _playwright_failures(report: dict[str, Any]) -> tuple[list[tuple[str, str]], list[str]]:
    if not isinstance(report.get("suites"), list):
        raise Unreadable("Playwright report has no suites array")
    failures: list[tuple[str, str]] = []
    for suite in report["suites"]:
        _walk_playwright(suite, "", failures)
    global_errors = [str(e.get("message", e)) for e in report.get("errors") or [] if e]
    return failures, global_errors


def check_red(kind: str, report_path: Path, prefixes: list[str], new_files: list[str] | None = None) -> str:
    """RED_ORACLE: at least one collected test titled with each prefix fails on an assertion.

    Refuses when the run passed, when only non-assertion failures exist, when any file
    failed to collect, or when a prefix has no failing assertion of its own.
    """
    report = _load_json(report_path)
    if kind == "vitest":
        failures, collection = _vitest_failures(report, new_files or [])
    else:
        failures, collection = _playwright_failures(report)
    if collection:
        raise Refused(f"collection/global errors present, not assertion Red: {collection[:5]}")
    missing = []
    for prefix in prefixes:
        hits = [t for t, m in failures if prefix in t and ASSERTION_MARKERS.search(m)]
        if not hits:
            missing.append(prefix)
    if missing:
        raise Refused(f"no failing assertion titled with {missing}; failures seen: {len(failures)}")
    return f"PASS RED {kind}: {len(failures)} failing assertions cover {prefixes}"


def check_rows(task_path: Path) -> str:
    """TASK_ROWS_DONE: every row with a numeric or H1/H2 id is `[x]` or `[B]`."""
    try:
        lines = task_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise Unreadable(f"cannot read {task_path}: {exc}") from exc
    open_rows: list[str] = []
    seen = 0
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not ROW_ID.match(cells[0]):
            continue
        seen += 1
        mark = STATUS_CELL.search(cells[-1])
        if mark is None or mark.group("mark") not in {"x", "B"}:
            open_rows.append(cells[0])
    if seen == 0:
        raise Unreadable(f"no task rows found in {task_path}")
    if open_rows:
        raise Refused(f"rows not [x]/[B]: {open_rows}")
    return f"PASS ROWS: {seen} rows all [x] or [B]"


def _expand(spec: str) -> list[str]:
    """`MEU-50..58` expands to MEU-50 … MEU-58; `MEU-57` stays one id."""
    match = re.fullmatch(r"MEU-(\d+)\.\.(\d+)", spec)
    if match is None:
        return [spec]
    low, high = int(match.group(1)), int(match.group(2))
    return [f"MEU-{n}" for n in range(low, high + 1)]


def check_meu_state(status_path: Path, expectations: list[str], plan: str | None) -> str:
    """Each `ID[..N]=status` expectation holds in meu-status.yaml; optional plan binding."""
    try:
        data = yaml.safe_load(status_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise Unreadable(f"cannot read {status_path}: {exc}") from exc
    rows = {str(m.get("id")): m for m in (data or {}).get("meus") or [] if isinstance(m, dict)}
    problems: list[str] = []
    checked = 0
    for expectation in expectations:
        ids, _, status = expectation.partition("=")
        if not status:
            raise Unreadable(f"expectation {expectation!r} lacks '=status'")
        for meu in _expand(ids):
            checked += 1
            row = rows.get(meu)
            if row is None:
                problems.append(f"{meu}: absent")
                continue
            if row.get("status") != status:
                problems.append(f"{meu}: status {row.get('status')!r} != {status!r}")
            if plan is not None and meu in SESSION_MEUS:
                bound = str(row.get("execution_plan") or "").rstrip("/")
                if bound != plan.rstrip("/"):
                    problems.append(f"{meu}: execution_plan {bound!r} != {plan!r}")
    if problems:
        raise Refused("; ".join(problems))
    return f"PASS MEU STATE: {checked} MEU expectations hold"


def _vitest_total(report: dict[str, Any]) -> tuple[int, int]:
    results = report.get("testResults")
    if not isinstance(results, list):
        raise Unreadable("Vitest report has no testResults array")
    total = failed = 0
    for file_result in results:
        assertions = file_result.get("assertionResults") or []
        if file_result.get("status") == "failed" and not assertions:
            failed += 1
        for case in assertions:
            if case.get("status") in {"passed", "failed"}:
                total += 1
                failed += case.get("status") == "failed"
    return total, failed


def check_counts(vitest: Path, playwright: Path, min_vitest: int, min_e2e: int) -> str:
    """COUNT_FLOORS: executed totals meet the floors and nothing failed or was unexpected."""
    v_total, v_failed = _vitest_total(_load_json(vitest))
    pw = _load_json(playwright)
    stats = pw.get("stats")
    if not isinstance(stats, dict):
        raise Unreadable("Playwright report has no stats object")
    e_pass, e_bad = int(stats.get("expected", 0)), int(stats.get("unexpected", 0)) + int(stats.get("flaky", 0))
    problems = []
    if v_failed or v_total < min_vitest:
        problems.append(f"vitest {v_total} executed, {v_failed} failed (floor {min_vitest})")
    if e_bad or e_pass < min_e2e or pw.get("errors"):
        problems.append(f"electron {e_pass} passed, {e_bad} unexpected/flaky (floor {min_e2e})")
    if problems:
        raise Refused("; ".join(problems))
    return f"PASS COUNTS: vitest {v_total} >= {min_vitest}; electron {e_pass} >= {min_e2e}"


def check_post_review(root: Path, plan_folder: str, next_meu: str) -> str:
    """POST_REVIEW_STATE: grouping, hub, focus and metrics reflect approval and the next MEU."""
    def read(rel: str) -> str:
        try:
            return (root / rel).read_text(encoding="utf-8")
        except OSError as exc:
            raise Unreadable(f"cannot read {rel}: {exc}") from exc

    problems = []
    grouping = read(".agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md")
    row = next((ln for ln in grouping.splitlines() if ln.startswith("| 26 |")), "")
    if "approved" not in row or plan_folder.rstrip("/") not in row:
        problems.append("grouping Session 26 row lacks approved + plan folder")
    hub = read("docs/BUILD_PLAN.md")
    phase = next((ln for ln in hub.splitlines() if ln.startswith("| 11 — Page layout")), "")
    if "✅" not in phase:
        problems.append("hub Phase 11 row not completed")
    # A18: when the SSOT queue is empty (every MEU complete), "next" is NO_PENDING and both
    # documents must say so explicitly instead of naming an MEU.
    token = NO_PENDING_TEXT if next_meu == NO_PENDING else next_meu
    if not re.search(rf"Next:[^\n]*\b{re.escape(token)}\b", hub):
        problems.append(f"hub Next line does not name {token}")
    if not re.search(rf"\b{re.escape(token)}\b", read(".agent/context/current-focus.md")):
        problems.append(f"current focus does not name {token}")
    if "p11-capture-settings" not in read("docs/execution/metrics.md"):
        problems.append("metrics has no p11-capture-settings row")
    if problems:
        raise Refused("; ".join(problems))
    return f"PASS POST-REVIEW: grouping, hub, focus and metrics agree on {next_meu}"


NO_PENDING = "none"
NO_PENDING_TEXT = "No pending MEU"


def _ssot_next(root: Path) -> str:
    """Head of `tools/meu_status.py next`, read from the tool itself, not re-derived.

    A18: an empty queue is accepted only when the tool says so AND `stats` reports zero pending.
    """
    import subprocess

    done = subprocess.run([sys.executable, "tools/meu_status.py", "next", "--limit", "1"],
                          cwd=root, capture_output=True, text=True, check=False)
    match = re.search(r"\bMEU-\d+[a-z]?\b", done.stdout)
    if done.returncode == 0 and match is None and "No pending+unblocked MEUs found" in done.stdout:
        stats = subprocess.run([sys.executable, "tools/meu_status.py", "stats"],
                               cwd=root, capture_output=True, text=True, check=False)
        if stats.returncode == 0 and re.search(r"^Pending:\s*0\s*$", stats.stdout, re.M):
            return NO_PENDING
    if done.returncode != 0 or match is None:
        raise Unreadable(f"meu_status.py next gave no MEU (exit {done.returncode}): {done.stdout[-200:]}")
    return match.group(0)


def _self_test() -> str:
    cases = 0
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        def write(name: str, payload: Any) -> Path:
            path = root / name
            text = payload if isinstance(payload, str) else json.dumps(payload)
            path.write_text(text, encoding="utf-8")
            return path

        def expect(ok: bool, fn: Any, *args: Any) -> None:
            nonlocal cases
            cases += 1
            try:
                fn(*args)
            except (Refused, Unreadable):
                if ok:
                    raise AssertionError(f"case {cases} should pass: {fn.__name__}{args[1:]}")
                return
            if not ok:
                raise AssertionError(f"case {cases} should refuse: {fn.__name__}{args[1:]}")

        vt_red = {"testResults": [{"name": "a.test.ts", "status": "failed", "assertionResults": [
            {"fullName": "AC-57.1 header", "status": "failed", "failureMessages": ["AssertionError: expected 1"]},
            {"fullName": "AC-58.2 rail", "status": "failed", "failureMessages": ["expect(received).toBe(expected)"]}]}]}
        vt_green = {"testResults": [{"name": "a.test.ts", "status": "passed", "assertionResults": [
            {"fullName": "AC-57.1 header", "status": "passed", "failureMessages": []}]}]}
        vt_collect = {"testResults": [{"name": "b.test.ts", "status": "failed", "message": "SyntaxError",
                                       "assertionResults": []}, *vt_red["testResults"]]}
        vt_nonassert = {"testResults": [{"name": "a.test.ts", "status": "failed", "assertionResults": [
            {"fullName": "AC-57.1 header", "status": "failed", "failureMessages": ["TypeError: x is undefined"]}]}]}
        expect(True, check_red, "vitest", write("v1.json", vt_red), ["AC-57", "AC-58"])
        expect(False, check_red, "vitest", write("v2.json", vt_green), ["AC-57"])
        expect(False, check_red, "vitest", write("v3.json", vt_collect), ["AC-57"])
        expect(False, check_red, "vitest", write("v4.json", vt_nonassert), ["AC-57"])
        expect(False, check_red, "vitest", write("v5.json", vt_red), ["AC-99"])
        expect(False, check_red, "vitest", write("v6.json", "not json"), ["AC-57"])
        missing_mod = {"name": "/r/ui/tests/unit/capture-filmstrip-label.test.ts", "status": "failed",
                       "message": "Failed to resolve import \"../../src/x\"", "assertionResults": []}
        syntax_new = {**missing_mod, "message": "SyntaxError: Unexpected token"}
        new = ["tests/unit/capture-filmstrip-label.test.ts"]
        expect(True, check_red, "vitest", write("v7.json", {"testResults": [missing_mod, *vt_red["testResults"]]}),
               ["AC-57"], new)
        expect(False, check_red, "vitest", write("v8.json", {"testResults": [syntax_new, *vt_red["testResults"]]}),
               ["AC-57"], new)
        expect(False, check_red, "vitest", write("v9.json", vt_red), ["AC-57"], new)
        expect(False, check_red, "vitest", write("v10.json", {"testResults": [missing_mod]}), ["AC-57"], new)

        pw_red = {"errors": [], "suites": [{"title": "capture-inbox.test.ts", "specs": [
            {"title": "AC-57.5 tool segment", "tests": [{"results": [
                {"status": "failed", "error": {"message": "Error: expect(locator).toBeDisabled() failed"}}]}]}]}]}
        pw_launch = {"errors": [], "suites": [{"title": "s", "specs": [{"title": "AC-57.5 x", "tests": [
            {"results": [{"status": "failed", "error": {"message": "electron: bad option: --remote-debugging-port=0"}}]}]}]}]}
        pw_global = {"errors": [{"message": "Error: No tests found"}], "suites": []}
        expect(True, check_red, "playwright", write("p1.json", pw_red), ["AC-57"])
        expect(False, check_red, "playwright", write("p2.json", pw_launch), ["AC-57"])
        expect(False, check_red, "playwright", write("p3.json", pw_global), ["AC-57"])

        header = "| # | Task | Status |\n|---|---|---|\n"
        expect(True, check_rows, write("t1.md", header + "| 1 | a | `[x]` |\n| H1-1 | b | `[B]` |\n| | divider | |\n"))
        expect(False, check_rows, write("t2.md", header + "| 1 | a | `[x]` |\n| H2-3 | b | `[ ]` |\n"))
        expect(False, check_rows, write("t3.md", "no table\n"))

        plan = "docs/execution/plans/2026-09-28-p11-capture-settings"
        good = {"meus": [{"id": f"MEU-{n}", "status": "approved", "execution_plan": plan if n > 56 else "x"}
                         for n in range(50, 59)]}
        bad = {"meus": [{"id": f"MEU-{n}", "status": "approved" if n < 55 else "pending"} for n in range(50, 59)]}
        expect(True, check_meu_state, write("m1.yaml", yaml.safe_dump(good)), ["MEU-50..58=approved"], plan)
        expect(False, check_meu_state, write("m2.yaml", yaml.safe_dump(bad)), ["MEU-50..56=approved"], None)
        unbound = {"meus": [{"id": "MEU-57", "status": "approved", "execution_plan": "other"}]}
        expect(False, check_meu_state, write("m3.yaml", yaml.safe_dump(unbound)), ["MEU-57=approved"], plan)
        vt_many = {"testResults": [{"name": "a", "status": "passed", "assertionResults": [
            {"fullName": f"t{i}", "status": "passed"} for i in range(3)]}]}
        pw_ok = {"errors": [], "suites": [], "stats": {"expected": 2, "unexpected": 0, "flaky": 0}}
        pw_bad = {"errors": [], "suites": [], "stats": {"expected": 2, "unexpected": 1, "flaky": 0}}
        expect(True, check_counts, write("c1.json", vt_many), write("c2.json", pw_ok), 3, 2)
        expect(False, check_counts, write("c3.json", vt_many), write("c4.json", pw_ok), 4, 2)
        expect(False, check_counts, write("c5.json", vt_many), write("c6.json", pw_bad), 3, 2)
        expect(False, check_counts, write("c7.json", vt_red), write("c8.json", pw_ok), 1, 2)

        docs = root / "repo"
        for rel, text in {
            ".agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md":
                f"| 26 | `p11-capture-settings` | approved | `{plan}/` | x |\n",
            "docs/BUILD_PLAN.md": "| 11 — Page layout | ✅ Completed |\nNext: Phase 7 (MEU-24).\n",
            ".agent/context/current-focus.md": "Current priority: MEU-24.\n",
            "docs/execution/metrics.md": "| 2026-09-28 | p11-capture-settings |\n",
        }.items():
            (docs / rel).parent.mkdir(parents=True, exist_ok=True)
            (docs / rel).write_text(text, encoding="utf-8")
        expect(True, check_post_review, docs, plan, "MEU-24")
        expect(False, check_post_review, docs, plan, "MEU-99")
        (docs / "docs/BUILD_PLAN.md").write_text("| 11 — Page layout | 🟡 In Progress |\nNext: MEU-24\n",
                                                 encoding="utf-8")
        expect(False, check_post_review, docs, plan, "MEU-24")
        # A18: an empty queue must be stated explicitly in both documents.
        (docs / "docs/BUILD_PLAN.md").write_text(
            f"| 11 — Page layout | ✅ Completed |\nNext: {NO_PENDING_TEXT}; all MEUs complete.\n", encoding="utf-8")
        (docs / ".agent/context/current-focus.md").write_text(f"{NO_PENDING_TEXT}.\n", encoding="utf-8")
        expect(True, check_post_review, docs, plan, NO_PENDING)
        (docs / ".agent/context/current-focus.md").write_text("Current priority: MEU-24.\n", encoding="utf-8")
        expect(False, check_post_review, docs, plan, NO_PENDING)
    return f"PASS SELF-TEST: {cases} cases (positive and adversarial) behaved as specified"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    red = sub.add_parser("red")
    red.add_argument("--kind", choices=["vitest", "playwright"], required=True)
    red.add_argument("--json", type=Path, required=True)
    red.add_argument("--ac", action="append", required=True, help="AC title prefix; repeatable")
    red.add_argument("--new-file", action="append", default=[],
                     help="new test file (suffix) whose module does not exist yet; repeatable")
    counts = sub.add_parser("counts")
    counts.add_argument("--vitest-json", type=Path, required=True)
    counts.add_argument("--playwright-json", type=Path, required=True)
    counts.add_argument("--min-vitest", type=int, required=True)
    counts.add_argument("--min-e2e", type=int, required=True)
    post = sub.add_parser("post-review")
    post.add_argument("--plan", required=True)
    rows = sub.add_parser("rows")
    rows.add_argument("--task", type=Path, required=True)
    meu = sub.add_parser("meu-state")
    meu.add_argument("--status-file", type=Path, default=Path(".agent/context/meu-status.yaml"))
    meu.add_argument("--expect", action="append", required=True, help="e.g. MEU-50..56=approved")
    meu.add_argument("--plan", default=None, help="required execution_plan for MEU-57/58 when approved")
    sub.add_parser("self-test")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "red":
            print(check_red(args.kind, args.json, args.ac, args.new_file))
        elif args.cmd == "counts":
            print(check_counts(args.vitest_json, args.playwright_json, args.min_vitest, args.min_e2e))
        elif args.cmd == "post-review":
            root = Path.cwd()
            print(check_post_review(root, args.plan, _ssot_next(root)))
        elif args.cmd == "rows":
            print(check_rows(args.task))
        elif args.cmd == "meu-state":
            print(check_meu_state(args.status_file, args.expect, args.plan))
        else:
            print(_self_test())
    except Refused as exc:
        print(f"REFUSED: {exc}")
        return 1
    except Unreadable as exc:
        print(f"FAIL-CLOSED: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
