"""Plan-local read-only verifier for 2026-10-10-gui-polish-residuals (GUARDRAILS SIGN 1, verification-principles V4).

Stdlib only. It reads plan files and writes nothing except what the caller redirects. It runs no
product code, so it can run before plan approval. Adapted from Session 29's verifier. ``static`` checks:

1. ``task.md`` table structure:
   - row ids are unique;
   - ``Depends on`` names existing rows and the graph is acyclic;
   - ``context_strategy`` is in {shared, compact_continue, isolated};
   - non-shared rows name a durable output;
   - ``builder_model`` is in the allowed classes.
2. Every ``validate-task.sh <check>`` invoked from ``task.md`` exists as a case label in the script.
3. The ``windows-gate-check`` stage order in ``validate-task.sh`` equals the ``.ps1`` ``$stages`` ids.
4. ``AUDIT_SRC`` and the audit pattern are identical in ``.sh`` and ``.ps1``.
5. Every ``D-n`` and ``AC-69.n``/``AC-70.n`` that ``task.md`` references has a definition site: an AC
   table row, a ``decision_log`` ``- id:`` entry, a ``### D-n`` heading, or a grouping §8 row (D-1..D-7).
6. ``GATED_PATHS`` and ``COUNT_FLOORS`` in the plan equal their executable copies in ``validate-task.sh``.
7. Every Files Modified row marked ``modify`` names a file that exists, and every ``new`` row names one
   that does not exist yet (checked only before execution, i.e. while ``baseline.sha`` is absent).
8. The ledger ``--goal-anchor`` in ``local-requests.md`` appears verbatim (normalized) in ``review-prompt-plan.md``.
9. ``EMPHASIS_TESTS`` stays out of the rail stage: ``settings-emphasis.test.tsx`` is the only member of ``UNIT70E``;
   it is in no other test array and not in the ``green70-rail`` case; ``red70``, ``green70`` and ``gate70``
   include it (Review R1 F1).

``selftest`` proves the negative cases: it corrupts in-memory copies (a duplicate row id, an unknown
``validate-task.sh`` check, a swapped stage, an undefined ``AC-70.99``, a changed floor, a missing
ledger goal anchor, a ``modify`` row for a missing file, the emphasis suite added to the rail stage) and requires each one to be reported.

Usage::

    python3 plan_checks.py static [--plan-dir DIR]
    python3 plan_checks.py selftest [--plan-dir DIR]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ALLOWED_STRATEGIES = {"shared", "compact_continue", "isolated"}
ALLOWED_BUILDERS = {"`avkit_builder`", "`avkit_coordinator`", "`avkit_verifier`", "—"}


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


def check_scripts(task: str, sh: str, ps1: str, plan: str) -> list[str]:
    """Cross-file checks: invoked checks exist; stage orders and audit lists agree."""
    errors: list[str] = []
    labels = set(re.findall(r"^  ([a-z0-9-]+)\)$", sh, re.M))
    for check in sorted(set(re.findall(r"validate-task\.sh ([a-z0-9-]+)", task))):
        if check not in labels:
            errors.append(f"task.md invokes validate-task.sh {check!r}, not a case label")
    m = re.search(r"order = \[(.*?)\]", sh, re.S)
    sh_order = re.findall(r'"([a-z0-9-]+)"', m.group(1)) if m else []
    ps_order = re.findall(r"^\s*@\('([a-z0-9-]+)',\s", ps1, re.M)
    if not sh_order or sh_order != ps_order:
        errors.append(f"stage order differs: sh={sh_order} ps1={ps_order}")
    sh_audit = re.findall(r"(\S+\.(?:py|tsx|ts))", re.search(r"AUDIT_SRC=\((.*?)\)", sh, re.S).group(1))
    ps_audit = re.findall(r"'([^']+\.(?:py|tsx|ts))'", re.search(r"\$auditSrc = @\((.*?)\)", ps1, re.S).group(1))
    if sh_audit != ps_audit:
        errors.append(f"AUDIT_SRC differs: sh-only={set(sh_audit) - set(ps_audit)} ps1-only={set(ps_audit) - set(sh_audit)}")
    sh_pat = re.search(r"^PREFIX_AUDIT='(.*)'$", sh, re.M)
    ps_pat = re.search(r"^\s*\$auditPattern = '(.*)'$", ps1, re.M)
    if not sh_pat or not ps_pat or sh_pat.group(1) != ps_pat.group(1):
        errors.append("audit pattern differs between .sh and .ps1")
    # GATED_PATHS: the plan's list equals the executable copy in windows-gate-check.
    pm = re.search(r"`plan_checks.py static` asserts it equals this list: `([^`]+)`", plan)
    sm = re.search(r"^gated = \[(.*?)\]", sh, re.S | re.M)
    plan_gated = pm.group(1).split() if pm else []
    sh_gated = [g.replace("{plan}", "docs/execution/plans/2026-10-10-gui-polish-residuals")
                for g in re.findall(r'f?"([^"]+)"', sm.group(1))] if sm else []
    if not plan_gated or plan_gated != sh_gated:
        errors.append(f"GATED_PATHS differ: plan={plan_gated} sh={sh_gated}")
    # COUNT_FLOORS: the plan's values equal the literals in windows-gate-check.
    fm = re.search(r"Vitest total ≥ (\d+) and Electron expected ≥ (\d+)", plan)
    sv = re.search(r'\(v\.get\("total"\) or 0\) < (\d+)', sh)
    se = re.search(r'\(e\.get\("expected"\) or 0\) < (\d+)', sh)
    if not (fm and sv and se and fm.group(1) == sv.group(1) and fm.group(2) == se.group(1)):
        errors.append(f"COUNT_FLOORS differ: plan={fm.groups() if fm else None} sh={(sv and sv.group(1), se and se.group(1))}")
    # A reference counts as defined only at a definition site, never by a prose mention
    # (Round 1 corrections: the receipt prose itself names the negative-case tokens).
    rel = ".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md"
    # Run from the repo root (task.md convention); fall back to the repo that holds this file.
    grouping = Path(rel) if Path(rel).exists() else Path(__file__).resolve().parents[4] / rel
    grouping_text = grouping.read_text(encoding="utf-8") if grouping.exists() else ""
    for ref in sorted(set(re.findall(r"\b(D-\d+|AC-(?:69|70)\.\d+)\b", task))):
        if ref.startswith("AC-"):
            defined = re.search(rf"^\| {re.escape(ref)} \|", plan, re.M) is not None
        else:
            defined = (re.search(rf"^\s*- id: {re.escape(ref)}$", plan, re.M) is not None
                       or re.search(rf"^### {re.escape(ref)}\b", plan, re.M) is not None
                       or re.search(rf"^\| {re.escape(ref)} \|", grouping_text, re.M) is not None)
        if not defined:
            errors.append(f"task.md references {ref}, which has no definition site (AC table row, decision_log id, ### heading, or grouping §8 row)")
    return errors


def _repo_root() -> Path:
    """The repository that holds this file (plan dir is docs/execution/plans/<plan>)."""
    return Path(__file__).resolve().parents[4]


def check_files(plan: str, root: Path, before_execution: bool) -> list[str]:
    """Files Modified rows: ``modify`` targets exist; ``new`` targets do not exist yet (before execution)."""
    errors: list[str] = []
    rows = re.findall(r"^\| `((?:ui|docs)/[^`]+)` \| (new|modify[^|]*?) \|", plan, re.M)
    if not rows:
        errors.append("no Files Modified rows found")
    for path, action in rows:
        exists = (root / path).exists()
        if action.startswith("modify") and not exists:
            errors.append(f"Files Modified 'modify' row names a missing file: {path}")
        if action == "new" and exists and before_execution:
            errors.append(f"Files Modified 'new' row names a file that already exists: {path}")
    return errors


def check_goal_anchor(requests: str, prompt: str) -> list[str]:
    """The ledger's --goal-anchor in local-requests.md must appear verbatim in the review prompt
    (review_ledger.py INTENT_BINDING; round 1 was refused before dispatch for lacking it)."""
    m = re.search(r'--goal-anchor "([^"]+)"', requests)
    if not m:
        return ["local-requests.md has no --goal-anchor"]
    norm = lambda s: " ".join(s.casefold().split())
    if norm(m.group(1)) not in norm(prompt):
        return ["review-prompt-plan.md does not contain the ledger goal anchor (INTENT_BINDING)"]
    return []


EMPHASIS_SUITE = "tests/unit/settings-emphasis.test.tsx"


def check_stage_split(sh: str) -> list[str]:
    """Item 9: EMPHASIS_TESTS never run in the rail-only stage, and always in Red, Green and the gate."""
    errors: list[str] = []
    arrays = {m.group(1): m.group(2) for m in re.finditer(r"^([A-Z0-9_]+)=\((.*?)\)", sh, re.M | re.S)}
    if arrays.get("UNIT70E", "").split() != [EMPHASIS_SUITE]:
        errors.append(f"UNIT70E must be exactly [{EMPHASIS_SUITE}], got {arrays.get('UNIT70E')!r}")
    for name, body in arrays.items():
        if name != "UNIT70E" and "settings-emphasis" in body:
            errors.append(f"EMPHASIS_TESTS member found in test array {name} (Review R1 F1)")

    def case(label: str) -> str:
        m = re.search(rf"^  {re.escape(label)}\)\n(.*?)^    ;;", sh, re.M | re.S)
        return m.group(1) if m else ""

    rail = case("green70-rail")
    if not rail:
        errors.append("validate-task.sh has no green70-rail case")
    elif "UNIT70E" in rail or "settings-emphasis" in rail or "AC-70.6" in rail or "UNIT70[" in rail:
        errors.append("green70-rail runs an EMPHASIS_TESTS member (Review R1 F1)")
    for label in ("red70", "green70", "gate70"):
        if "${UNIT70E[@]}" not in case(label):
            errors.append(f"{label} does not run EMPHASIS_TESTS (UNIT70E)")
    return errors


def run_static(d: Path, root: Path) -> list[str]:
    """All static checks over the plan folder ``d``."""
    task = (d / "task.md").read_text(encoding="utf-8")
    plan = (d / "implementation-plan.md").read_text(encoding="utf-8")
    return (check_task(task)
            + check_scripts(task, (d / "validate-task.sh").read_text(encoding="utf-8"),
                            (d / "validate-task.ps1").read_text(encoding="utf-8"), plan)
            + check_files(plan, root, not (d / "baseline.sha").exists())
            + check_goal_anchor((d / "local-requests.md").read_text(encoding="utf-8"),
                                (d / "review-prompt-plan.md").read_text(encoding="utf-8"))
            + check_stage_split((d / "validate-task.sh").read_text(encoding="utf-8")))


def selftest(d: Path, root: Path) -> list[str]:
    """Each injected defect must be reported by the matching check (the verifier's negative cases)."""
    task = (d / "task.md").read_text(encoding="utf-8")
    sh = (d / "validate-task.sh").read_text(encoding="utf-8")
    ps1 = (d / "validate-task.ps1").read_text(encoding="utf-8")
    plan = (d / "implementation-plan.md").read_text(encoding="utf-8")
    failures: list[str] = []
    first_row = next(line for line in task.splitlines() if line.startswith("| 0 |"))
    cases = [
        ("duplicate row id", lambda: check_task(task.replace(first_row, first_row + "\n" + first_row)), "duplicate row ids"),
        ("unknown check", lambda: check_scripts(task + "\nvalidate-task.sh no-such-check\n", sh, ps1, plan), "not a case label"),
        ("swapped stage", lambda: check_scripts(task, sh.replace('"py-types", "py-lint"', '"py-lint", "py-types"'), ps1, plan), "stage order differs"),
        ("undefined AC", lambda: check_scripts(task + "\nAC-70.99\n", sh, ps1, plan), "AC-70.99"),
        ("changed floor", lambda: check_scripts(task, sh.replace("< 748", "< 700"), ps1, plan), "COUNT_FLOORS differ"),
        ("missing goal anchor", lambda: check_goal_anchor((d / "local-requests.md").read_text(encoding="utf-8"), "no goal here"), "goal anchor"),
        ("emphasis suite in rail stage", lambda: check_stage_split(sh.replace(
            'vitest_env_ok s31-70-green-rail tests/unit/settings-tail-spacer.test.ts',
            'vitest_env_ok s31-70-green-rail tests/unit/settings-tail-spacer.test.ts "${UNIT70E[@]}"')), "green70-rail runs"),
        ("emphasis suite in REGSET", lambda: check_stage_split(sh.replace(
            "REGSET=(tests/unit/settings-page.test.ts", "REGSET=(tests/unit/settings-emphasis.test.tsx tests/unit/settings-page.test.ts")), "test array REGSET"),
        ("missing modify target", lambda: check_files(plan + "\n| `ui/no/such/file.ts` | modify | x |\n", root, True), "missing file"),
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
    task = (d / "task.md").read_text(encoding="utf-8")
    print(f"PASS static: {len(_rows(task))} task rows; scripts, plan cross-references and file targets agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
