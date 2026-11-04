"""Plan-local read-only verifier for 2026-09-30-tts-repair (GUARDRAILS SIGN 1, verification-principles V4).

Stdlib only. It reads plan files and writes nothing except what the caller redirects. It runs no
product code, so it can run before plan approval. ``static`` checks five things:

1. ``task.md`` table structure:
   - row ids are unique;
   - ``Depends on`` names existing rows and the graph is acyclic;
   - ``context_strategy`` is in {shared, compact_continue, isolated};
   - non-shared rows name a durable output;
   - ``builder_model`` is in the allowed classes.
2. Every ``validate-task.sh <check>`` invoked from ``task.md`` exists as a case label in the script.
3. The ``windows-gate-check`` stage order in ``validate-task.sh`` equals the ``.ps1`` ``$stages`` ids.
4. ``AUDIT_SRC`` and the audit pattern are identical in ``.sh`` and ``.ps1``.
5. Every ``TA-n`` and ``D-n`` that ``task.md`` references is defined in ``implementation-plan.md``.
6. ``GATED_PATHS`` and ``COUNT_FLOORS`` in the plan equal their executable copies in ``validate-task.sh``,
   and ``validate-task.sh`` imports ``TTS_LIVE_STEPS`` (``STEP_IDS``) instead of restating them.

Usage::

    python3 plan_checks.py static [--plan-dir DIR]
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
    sh_gated = [g.replace("{plan}", "docs/execution/plans/2026-09-30-tts-repair")
                for g in re.findall(r'f?"([^"]+)"', sm.group(1))] if sm else []
    if not plan_gated or plan_gated != sh_gated:
        errors.append(f"GATED_PATHS differ: plan={plan_gated} sh={sh_gated}")
    # COUNT_FLOORS: the plan's values equal the literals in windows-gate-check.
    fm = re.search(r"Vitest total ≥ (\d+) and Electron expected ≥ (\d+)", plan)
    sv = re.search(r'\(v\.get\("total"\) or 0\) < (\d+)', sh)
    se = re.search(r'\(e\.get\("expected"\) or 0\) < (\d+)', sh)
    if not (fm and sv and se and fm.group(1) == sv.group(1) and fm.group(2) == se.group(1)):
        errors.append(f"COUNT_FLOORS differ: plan={fm.groups() if fm else None} sh={(sv and sv.group(1), se and se.group(1))}")
    # TTS_LIVE_STEPS: the .sh imports STEP_IDS instead of restating the ids.
    if sh.count("from tts_live_check import STEP_IDS") != 2 or '"fresh-rows", "variant-download"' in sh:
        errors.append("TTS_LIVE_STEPS restated in validate-task.sh instead of imported from tts_live_check.STEP_IDS")
    for ref in sorted(set(re.findall(r"\b(TA-\d+|D-\d+)\b", task))):
        if ref not in plan:
            errors.append(f"task.md references {ref}, undefined in implementation-plan.md")
    return errors


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["static"])
    parser.add_argument("--plan-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    d = args.plan_dir
    task = (d / "task.md").read_text(encoding="utf-8")
    errors = check_task(task) + check_scripts(
        task,
        (d / "validate-task.sh").read_text(encoding="utf-8"),
        (d / "validate-task.ps1").read_text(encoding="utf-8"),
        (d / "implementation-plan.md").read_text(encoding="utf-8"),
    )
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        return 1
    print(f"PASS static: {len(_rows(task))} task rows; scripts and plan cross-references agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
