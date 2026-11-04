"""Plan-local read-only verifier for 2026-10-14-tts-engine-runtime (GUARDRAILS SIGN 1, verification-principles V4).

Stdlib only. It reads plan files and writes nothing except what the caller redirects. It runs no
product code, so it can run before plan approval. Adapted from Session 31's verifier; this plan has
only the Windows runner (validate-task.ps1, with its parsers in gate_lib.py). ``static`` checks:

1. ``task.md`` table structure:
   - row ids are unique;
   - ``Depends on`` names existing rows and the graph is acyclic;
   - ``context_strategy`` is in {shared, compact_continue, isolated};
   - non-shared rows name a durable output;
   - ``builder_model`` is in the allowed classes.
2. Every ``validate-task.ps1 -Check <name>`` in ``task.md`` is a switch label in the script.
3. ``gate_lib.py`` ``ORDER`` equals the ``.ps1`` ``$stages`` ids (windows-gate-check reads ORDER).
4. Every ``D-n`` and ``AC-72.n``/``AC-73.n``/``AC-74.n`` that ``task.md`` references has a definition site: an AC
   table row, a ``decision_log`` ``- id:`` entry, a ``### D-n`` heading, or a grouping §8 row.
5. ``GATED_PATHS`` and ``COUNT_FLOORS`` in the plan equal their executable copies in ``validate-task.ps1``.
6. Files Modified rows: each names one exact path (no braces or globs); ``modify`` targets exist unless a
   ``new`` row of this plan creates them; ``new`` targets do not exist yet (checked only while
   ``baseline.sha`` is absent, i.e. before execution).
7. Every AC whose Test cell names a ``.py``/``.ts``/``.tsx`` file is run by a ``validate-task.ps1`` test set, so the
   per-AC Red coverage in gate_lib.py is never vacuous; every TEST_AMENDMENTS file is a Files Modified row.
8. The plan's goal anchor appears verbatim (normalized) in ``review-prompt-plan.md`` (ledger INTENT_BINDING).

``selftest`` proves the negative cases on in-memory copies and requires each one to be reported.

Usage::

    python plan_checks.py static [--plan-dir DIR]
    python plan_checks.py selftest [--plan-dir DIR]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_STRATEGIES = {"shared", "compact_continue", "isolated"}
ALLOWED_BUILDERS = {"`avkit_builder`", "`avkit_coordinator`", "`avkit_verifier`", "—"}
GROUPING = ".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md"
FILE_ROW = re.compile(r"^\| `([^`]+)` \| (new|modify \(append\)|modify) \|", re.M)


def _rows(task: str) -> list[list[str]]:
    """Return the 10-column task-table rows (id first), skipping dividers and the header."""
    rows = []
    for line in task.splitlines():
        if not line.startswith("| ") or line.startswith("| #") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 10 or not cells[0]:
            continue
        rows.append(cells)
    return rows


def check_task(task: str) -> list[str]:
    """Structural checks over the task table."""
    errors: list[str] = []
    rows = _rows(task)
    ids = [r[0] for r in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate row ids: {ids}")
    deps: dict[str, list[str]] = {}
    for r in rows:
        rid, dep, strategy, durable, builder = r[0], r[5], r[6], r[7], r[8]
        deps[rid] = [] if dep in ("—", "-", "") else [d.strip() for d in dep.split(",")]
        for d in deps[rid]:
            if d not in ids:
                errors.append(f"row {rid}: depends on unknown row {d!r}")
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


def _ps1_stages(ps1: str) -> list[str]:
    m = re.search(r"\$stages = @\((.*?)\n\s*# A run must never report", ps1, re.S)
    return re.findall(r"^\s*@\('([a-z0-9-]+)',\s", m.group(1), re.M) if m else []


def _ps1_gated(ps1: str) -> list[str]:
    m = re.search(r"^\$gated = @\((.*?)\)$", ps1, re.S | re.M)
    return re.findall(r"'([^']+)'", m.group(1)) if m else []


def check_scripts(task: str, ps1: str, lib: str, plan: str, grouping_text: str) -> list[str]:
    """Cross-file checks: invoked checks exist; stage order, gated paths and floors agree; refs are defined."""
    errors: list[str] = []
    labels = set(re.findall(r"^    '([a-z0-9-]+)' \{$", ps1, re.M))
    for check in sorted(set(re.findall(r"validate-task\.ps1 -Check ([a-z0-9-]+)", task))):
        if check not in labels:
            errors.append(f"task.md invokes validate-task.ps1 -Check {check!r}, not a switch label")
    m = re.search(r"^ORDER = \[(.*?)\]", lib, re.S | re.M)
    lib_order = re.findall(r'"([a-z0-9-]+)"', m.group(1)) if m else []
    ps_order = _ps1_stages(ps1)
    if not lib_order or lib_order != ps_order:
        errors.append(f"stage order differs: gate_lib ORDER={lib_order} ps1 $stages={ps_order}")
    # GATED_PATHS: the plan's list equals the executable copy in validate-task.ps1.
    pm = re.search(r"`plan_checks.py static` asserts it equals this list: `([^`]+)`", plan)
    plan_gated = pm.group(1).split() if pm else []
    if not plan_gated or plan_gated != _ps1_gated(ps1):
        errors.append(f"GATED_PATHS differ: plan={plan_gated} ps1={_ps1_gated(ps1)}")
    # COUNT_FLOORS: the plan's values equal the windows-gate-check literals.
    fm = re.search(r"Vitest `numTotalTests` ≥ (\d+).*?Playwright `stats\.expected` ≥ (\d+).*?pytest passed ≥ (\d+)", plan)
    ps = tuple(re.search(rf"'--floor-{k}', '(\d+)'", ps1).group(1) if re.search(rf"'--floor-{k}', '(\d+)'", ps1) else None
               for k in ("vitest", "e2e", "pytest"))
    if not fm or fm.groups() != ps:
        errors.append(f"COUNT_FLOORS differ: plan={fm.groups() if fm else None} ps1={ps}")
    # A reference counts as defined only at a definition site, never by a prose mention.
    for ref in sorted(set(re.findall(r"\b(D-\d+|AC-(?:72|73|74)\.\d+)\b", task))):
        if ref.startswith("AC-"):
            defined = re.search(rf"^\| {re.escape(ref)} \|", plan, re.M) is not None
        else:
            defined = (re.search(rf"^\s*- id: {re.escape(ref)}$", plan, re.M) is not None
                       or re.search(rf"^### {re.escape(ref)}\b", plan, re.M) is not None
                       or re.search(rf"^\| {re.escape(ref)} \|", grouping_text, re.M) is not None)
        if not defined:
            errors.append(f"task.md references {ref}, which has no definition site (AC table row, decision_log id, ### heading, or grouping §8 row)")
    return errors


def check_files(plan: str, root: Path, before_execution: bool) -> list[str]:
    """Files Modified rows name exact paths; ``modify`` targets exist (or are created by a ``new`` row); ``new`` targets do not yet."""
    errors: list[str] = []
    rows = FILE_ROW.findall(plan)
    if not rows:
        errors.append("no Files Modified rows found")
    created = {p for p, a in rows if a == "new"}
    for path, action in rows:
        if re.search(r"[{}*?\[\]]", path):
            errors.append(f"Files Modified row uses a brace or glob pattern: {path}")
            continue
        exists = (root / path).exists()
        if action.startswith("modify") and not exists and path not in created:
            errors.append(f"Files Modified '{action}' row names a missing file: {path}")
        if action == "new" and exists and before_execution:
            errors.append(f"Files Modified 'new' row names a file that already exists: {path}")
    return errors


def check_coverage(plan: str, ps1: str) -> list[str]:
    """Every AC test file is in a ps1 test set; every TEST_AMENDMENTS file is a Files Modified row."""
    errors: list[str] = []
    listed = {p for p, _ in FILE_ROW.findall(plan)}
    for line in plan.splitlines():
        m = re.match(r"^\| (AC-\d+\.\d+) \|", line)
        if not m:
            continue
        p = re.search(r"`([^`\s]+\.(?:py|ts|tsx))`", line.rstrip().rstrip("|").split("|")[-1])
        if not p:
            continue
        rel = re.sub(r"^(ui|mcp-server)/", "", p.group(1))
        if f"'{rel}'" not in ps1:
            errors.append(f"{m.group(1)} test file {p.group(1)} is in no validate-task.ps1 test set")
    for line in plan.splitlines():
        if re.match(r"^\| TA-\d+[a-z]? \|", line):
            for item in re.findall(r"`([^`]+)`", line.split("|")[2]):
                path = item.partition(":")[0]
                if path not in listed:
                    errors.append(f"TEST_AMENDMENTS file {path} is not a Files Modified row")
    return errors


def check_goal_anchor(plan: str, prompt: str) -> list[str]:
    """The plan's goal anchor (the ledger --goal-anchor) must appear verbatim in the review prompt."""
    m = re.search(r"^> \*\*Goal anchor:\*\* `([^`]+)`", plan, re.M)
    if not m:
        return ["implementation-plan.md has no goal anchor line"]
    norm = lambda s: " ".join(s.casefold().split())  # noqa: E731
    if norm(m.group(1)) not in norm(prompt):
        return ["review-prompt-plan.md does not contain the goal anchor (INTENT_BINDING)"]
    return []


def _repo_root() -> Path:
    """The repository that holds this file (plan dir is docs/execution/plans/<plan>)."""
    return Path(__file__).resolve().parents[4]


def _load(d: Path, root: Path) -> dict[str, str]:
    grouping = Path(GROUPING) if Path(GROUPING).exists() else root / GROUPING
    return {
        "task": (d / "task.md").read_text(encoding="utf-8"),
        "plan": (d / "implementation-plan.md").read_text(encoding="utf-8"),
        "ps1": (d / "validate-task.ps1").read_text(encoding="utf-8"),
        "lib": (d / "gate_lib.py").read_text(encoding="utf-8"),
        "prompt": (d / "review-prompt-plan.md").read_text(encoding="utf-8"),
        "grouping": grouping.read_text(encoding="utf-8") if grouping.exists() else "",
    }


def run_static(d: Path, root: Path) -> list[str]:
    """All static checks over the plan folder ``d``."""
    f = _load(d, root)
    return (check_task(f["task"])
            + check_scripts(f["task"], f["ps1"], f["lib"], f["plan"], f["grouping"])
            + check_files(f["plan"], root, not (d / "baseline.sha").exists())
            + check_coverage(f["plan"], f["ps1"])
            + check_goal_anchor(f["plan"], f["prompt"]))


def selftest(d: Path, root: Path) -> list[str]:
    """Each injected defect must be reported by the matching check (the verifier's negative cases)."""
    f = _load(d, root)
    task, ps1, lib, plan, grp = f["task"], f["ps1"], f["lib"], f["plan"], f["grouping"]
    failures: list[str] = []
    first_row = next(line for line in task.splitlines() if line.startswith("| 0 |"))
    cases = [
        ("duplicate row id", lambda: check_task(task.replace(first_row, first_row + "\n" + first_row)), "duplicate row ids"),
        ("unknown check", lambda: check_scripts(task + "\nvalidate-task.ps1 -Check no-such-check\n", ps1, lib, plan, grp), "not a switch label"),
        ("swapped stage", lambda: check_scripts(task, ps1, lib.replace('"py-types", "py-lint"', '"py-lint", "py-types"'), plan, grp), "stage order differs"),
        ("changed floor", lambda: check_scripts(task, ps1.replace("'--floor-vitest', '800'", "'--floor-vitest', '700'"), lib, plan, grp), "COUNT_FLOORS differ"),
        ("dropped GATED path", lambda: check_scripts(task, ps1.replace("'packaging', 'pyproject.toml'", "'pyproject.toml'"), lib, plan, grp), "GATED_PATHS differ"),
        ("undefined AC", lambda: check_scripts(task + "\nAC-73.99\n", ps1, lib, plan, grp), "AC-73.99"),
        ("undefined decision", lambda: check_scripts(task + "\nD-999\n", ps1, lib, plan, grp), "D-999"),
        ("missing modify target", lambda: check_files(plan + "\n| `ui/no/such/file.ts` | modify | x |\n", root, True), "missing file"),
        ("existing new target", lambda: check_files(plan + "\n| `pyproject.toml` | new | x |\n", root, True), "already exists"),
        ("glob row", lambda: check_files(plan + "\n| `tests/unit/test_*.py` | new | x |\n", root, True), "brace or glob"),
        ("AC test outside every set", lambda: check_coverage(plan + "\n| AC-73.98 | x | s | unit | `tests/unit/test_nowhere.py` |\n", ps1), "AC-73.98"),
        ("missing goal anchor", lambda: check_goal_anchor(plan, "no goal here"), "goal anchor"),
    ]
    for name, fn, needle in cases:
        found = [e for e in fn() if needle in e]
        print(f"{'PASS' if found else 'FAIL'} selftest {name}: {found[:1] if found else 'not reported'}")
        if not found:
            failures.append(name)
    return failures


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["static", "selftest"])
    parser.add_argument("--plan-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    d, root = args.plan_dir, _repo_root()
    if args.command == "selftest":
        failed = selftest(d, root)
        if failed:
            print(f"FAIL: selftest cases not reported: {failed}")
            return 1
        print("PASS selftest: every injected defect was reported")
        return 0
    errors = run_static(d, root)
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        return 1
    print(f"PASS static: {len(_rows(_load(d, root)['task']))} task rows; scripts, plan cross-references and file targets agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
