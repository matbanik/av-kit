"""Plan-local read-only verifier for 2026-10-14-backend-robustness (GUARDRAILS SIGN 1, verification-principles V4).

Stdlib only. It reads plan files (and imports ``exec_checks.py`` for its constants, which runs nothing) and
writes nothing. It runs no product code, so it can run before plan approval. Adapted from Session 31.
``static`` checks:

1. ``task.md`` table structure:
   - row ids are unique;
   - ``Depends on`` names existing rows and the graph is acyclic;
   - ``context_strategy`` is in {shared, compact_continue, isolated};
   - non-shared rows name a durable output;
   - ``builder_model`` is in the allowed classes.
2. Every ``validate-task.ps1 -Check <name>`` in ``task.md`` has a ``$Check -eq '<name>'`` block in the script.
3. The ``windows-gate`` ``$stages`` ids in ``validate-task.ps1`` equal ``exec_checks.STAGES`` (same order).
4. ``GATED_PATHS``: the plan's ``GATE_EXCLUDED`` list equals ``exec_checks.GATE_EXCLUDED``, and the script holds no
   copy of its own (no ``$gated``).
5. ``COUNT_FLOORS``: the plan's 655 / 773 / 133 equal ``exec_checks.FLOORS``.
6. The plan's AC tables equal ``exec_checks.ACS`` (id -> tier; a "same file" row inherits the row above's tier)
   and ``exec_checks.PINS`` (rows typed ``**pin**``).
7. ``TEST_AMENDMENTS`` in the plan names TA-1..TA-11 (TA-11 by A-10) with the files in ``exec_checks.TA_SITES``.
8. ``$SRC76`` / ``$SRC78`` / ``$SRC77`` in the script equal ``exec_checks.product_files()`` for each MEU, so the
   targeted source audit and the red-guard cover the same files.
9. Red checks: each starts with ``red-guard`` and runs no TEST_AMENDMENTS array (TAs apply only in Green).
10. Every ``D-n``, ``TA-n`` and ``AC-n.m`` that ``task.md`` or the plan references has a definition site: an AC
    table row, a ``decision_log`` ``- id:`` entry, a grouping §8 row (D-1..D-7), a ``**TA-n**`` entry, or the
    plan's declared triage-decision list (foreign ids).
11. Files Modified: every ``modify`` row names a file that exists; every ``create`` row names one that does not
    exist yet (checked only while ``baseline.sha`` is absent, i.e. before execution).
12. The plan's Goal sentence (the ledger goal anchor) appears verbatim (normalized) in ``review-prompt-plan.md``.

``selftest`` corrupts in-memory copies and requires each defect to be reported.

Usage::

    python plan_checks.py static [--plan-dir DIR]
    python plan_checks.py selftest [--plan-dir DIR]
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType

PLAN_REL = "docs/execution/plans/2026-10-14-backend-robustness"
GROUPING = ".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md"
ALLOWED_STRATEGIES = {"shared", "compact_continue", "isolated"}
ALLOWED_BUILDERS = {"`avkit_builder`", "`avkit_coordinator`", "`avkit_verifier`", "—"}
TIER_WORDS = [("MCP Vitest", "mcp"), ("Vitest", "vitest"), ("Electron", "electron"), ("pytest", "pytest")]


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
    """Item 1: structural checks over the task table."""
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


def _ps_list(ps1: str, name: str) -> list[str]:
    """The single-quoted items of ``$name = @(...)`` (first occurrence), with ``$plan`` expanded."""
    m = re.search(rf"^\s*\${re.escape(name)} = @\((.*?)\)\s*$", ps1, re.M | re.S)
    if not m:
        return []
    return [s.replace("$plan", PLAN_REL) for s in re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))]


def _check_block(ps1: str, name: str) -> str:
    """The body of ``if ($Check -eq '<name>') { ... }`` up to the next top-level check."""
    m = re.search(rf"^if \(\$Check -eq '{re.escape(name)}'\) \{{\n(.*?)^\}}$", ps1, re.M | re.S)
    return m.group(1) if m else ""


def check_scripts(task: str, ps1: str, ec: ModuleType) -> list[str]:
    """Items 2, 3, 8 and 9: the script matches task.md and exec_checks."""
    errors: list[str] = []
    blocks = set(re.findall(r"^if \(\$Check -eq '([a-z0-9-]+)'\)", ps1, re.M))
    for check in sorted(set(re.findall(r"validate-task\.ps1 -Check ([a-z0-9-]+)", task))):
        if check not in blocks:
            errors.append(f"task.md invokes -Check {check!r}, which validate-task.ps1 does not define")
    m = re.search(r"^\s*\$stages = @\((.*?)^\s*\)$", ps1, re.M | re.S)
    order = re.findall(r"^\s*@\('([a-z0-9-]+)',\s", m.group(1), re.M) if m else []
    if order != list(ec.STAGES):
        errors.append(f"stage order differs: ps1={order} exec_checks={list(ec.STAGES)}")
    plan_text = (Path(ec.PLAN) / "implementation-plan.md").read_text(encoding="utf-8") if Path(ec.PLAN).exists() else ""
    return errors + check_src(ps1, ec.product_files(plan_text) if plan_text else {}) + check_red(ps1)


def check_src(ps1: str, product: dict[str, list[str]]) -> list[str]:
    """Item 8: each MEU's source-audit list equals its product Files Modified rows."""
    errors = []
    for meu in ("76", "78", "77"):
        if sorted(_ps_list(ps1, f"SRC{meu}")) != sorted(product.get(meu, [])):
            errors.append(f"$SRC{meu} differs from product_files: ps1-only={set(_ps_list(ps1, f'SRC{meu}')) - set(product.get(meu, []))} "
                          f"plan-only={set(product.get(meu, [])) - set(_ps_list(ps1, f'SRC{meu}'))}")
    return errors


def check_red(ps1: str) -> list[str]:
    """Item 9: Red checks begin with the red-guard and never run a TEST_AMENDMENTS array."""
    errors = []
    for meu in ("76", "78", "77"):
        body = _check_block(ps1, f"red{meu}")
        first = next((line for line in body.splitlines() if line.strip()), "")
        if f"'red-guard', '--meu', '{meu}'" not in first:
            errors.append(f"red{meu} does not start with the red-guard")
        if re.search(r"\$TA\d\d", body):
            errors.append(f"red{meu} runs a TEST_AMENDMENTS array (TAs apply only in Green)")
    return errors


def check_constants(plan: str, ps1: str, ec: ModuleType) -> list[str]:
    """Items 4-7: GATED_PATHS, COUNT_FLOORS, the AC table and TEST_AMENDMENTS equal their executable copies."""
    errors: list[str] = []
    pm = re.search(r"`plan_checks.py static` asserts the executable copy \(`GATE_EXCLUDED` in `exec_checks.py`\) equals this list: `([^`]+)`", plan)
    plan_excluded = pm.group(1).split() if pm else []
    if not plan_excluded or plan_excluded != list(ec.GATE_EXCLUDED):
        errors.append(f"GATED_PATHS differ: plan GATE_EXCLUDED={plan_excluded} exec_checks={list(ec.GATE_EXCLUDED)}")
    if re.search(r"^\s*\$gated\s*=", ps1, re.M):
        errors.append("GATED_PATHS differ: validate-task.ps1 holds its own $gated copy")
    fm = re.search(r"passed ≥ (\d+); Vitest total ≥ (\d+) and failed 0; Electron expected ≥ (\d+)", plan)
    want = {"pytest": int(fm.group(1)), "vitest": int(fm.group(2)), "e2e": int(fm.group(3))} if fm else None
    if want != dict(ec.FLOORS) or want != {"pytest": 655, "vitest": 773, "e2e": 133}:
        errors.append(f"COUNT_FLOORS differ: plan={want} exec_checks={dict(ec.FLOORS)}")
    acs: dict[str, dict[str, str]] = {}
    pins: set[str] = set()
    tier = ""
    for ac, typ in re.findall(r"^\| AC-(\d+\.\d+) \| ([^|]+) \|", plan, re.M):
        if "same file" in typ and not any(w in typ for w, _ in TIER_WORDS):
            pass  # inherits the previous row's tier
        else:
            tier = next((t for w, t in TIER_WORDS if w in typ), "?")
        acs.setdefault(ac.split(".")[0], {})[ac] = tier
        if "**pin**" in typ:
            pins.add(ac)
    if acs != {k: dict(v) for k, v in ec.ACS.items()}:
        errors.append(f"AC tables differ from exec_checks.ACS: plan={acs}")
    if pins != set(ec.PINS):
        errors.append(f"pins differ: plan={pins} exec_checks={set(ec.PINS)}")
    tm = re.search(r"^\| `TEST_AMENDMENTS` \|(.*)$", plan, re.M)
    sites: dict[int, str] = {}
    last = ""
    for n, body in re.findall(r"\*\*TA-(\d+)\*\* (.*?)(?=\*\*TA-\d+\*\*|Nothing else)", tm.group(1) if tm else ""):
        f = re.search(r"`((?:tests/)?[\w/]*test_\w+\.py)", body)
        name = f.group(1) if f else last
        last = name
        sites[int(n)] = next((p for p in ec.TA_SITES.values() if p == name or p.endswith("/" + name)), name)
    if sites != dict(ec.TA_SITES) or sorted(sites) != list(range(1, 12)):
        errors.append(f"TEST_AMENDMENTS differ: plan={sites} exec_checks={dict(ec.TA_SITES)}")
    return errors


def check_refs(task: str, plan: str, grouping: str) -> list[str]:
    """Item 10: every referenced D-, TA- and AC id has a definition site."""
    errors: list[str] = []
    fm = re.search(r"The triage decisions \(([^)]*)\)", plan)
    foreign = set(re.findall(r"D-\d+", fm.group(1))) if fm else set()
    for where, text in (("task.md", task), ("implementation-plan.md", plan)):
        for ref in sorted(set(re.findall(r"\b(D-\d+|TA-\d+|AC-\d+\.\d+)(?!\d)", text))):
            if ref.startswith("AC-"):
                ok = re.search(rf"^\| {re.escape(ref)} \|", plan, re.M) is not None
            elif ref.startswith("TA-"):
                ok = f"**{ref}**" in plan
            else:
                ok = (re.search(rf"^\s*- id: {re.escape(ref)}$", plan, re.M) is not None
                      or re.search(rf"^\| {re.escape(ref)} \|", grouping, re.M) is not None or ref in foreign)
            if not ok:
                errors.append(f"{where} references {ref}, which has no definition site")
    return errors


def check_files(plan: str, root: Path, before_execution: bool) -> list[str]:
    """Item 11: ``modify`` targets exist; ``create`` targets do not exist yet (before execution)."""
    errors: list[str] = []
    rows = re.findall(r"^\| `([^`]+)` \| (modify|create) \|", plan, re.M)
    if not rows:
        errors.append("no Files Modified rows found")
    for path, action in rows:
        exists = (root / path).exists()
        if action == "modify" and not exists:
            errors.append(f"Files Modified 'modify' row names a missing file: {path}")
        if action == "create" and exists and before_execution:
            errors.append(f"Files Modified 'create' row names a file that already exists: {path}")
    return errors


def check_goal_anchor(plan: str, prompt: str) -> list[str]:
    """Item 12: the Goal sentence (the ledger --goal-anchor) appears in the review prompt (INTENT_BINDING)."""
    m = re.search(r"^## Goal\n\n(?:.*\n)*?(Session 33 delivers [^\n]+)$", plan, re.M)
    if not m:
        return ["implementation-plan.md §Goal has no 'Session 33 delivers' sentence"]
    norm = lambda s: " ".join(s.casefold().split())  # noqa: E731
    if norm(m.group(1)) not in norm(prompt):
        return ["review-prompt-plan.md does not contain the Goal sentence (INTENT_BINDING)"]
    return []


def _load_exec_checks(d: Path) -> ModuleType:
    sys.dont_write_bytecode = True  # importing exec_checks must not leave __pycache__ in the plan folder
    spec = importlib.util.spec_from_file_location("exec_checks", d / "exec_checks.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _inputs(d: Path, root: Path) -> dict[str, str]:
    g = root / GROUPING
    return {
        "task": (d / "task.md").read_text(encoding="utf-8"),
        "plan": (d / "implementation-plan.md").read_text(encoding="utf-8"),
        "ps1": (d / "validate-task.ps1").read_text(encoding="utf-8"),
        "prompt": (d / "review-prompt-plan.md").read_text(encoding="utf-8") if (d / "review-prompt-plan.md").exists() else "",
        "grouping": g.read_text(encoding="utf-8") if g.exists() else "",
    }


def run_static(d: Path, root: Path, ec: ModuleType) -> list[str]:
    i = _inputs(d, root)
    return (check_task(i["task"]) + check_scripts(i["task"], i["ps1"], ec) + check_constants(i["plan"], i["ps1"], ec)
            + check_refs(i["task"], i["plan"], i["grouping"])
            + check_files(i["plan"], root, not (d / "baseline.sha").exists())
            + check_goal_anchor(i["plan"], i["prompt"]))


def selftest(d: Path, root: Path, ec: ModuleType) -> list[str]:
    """Each injected defect must be reported by the matching check."""
    i = _inputs(d, root)
    task, plan, ps1 = i["task"], i["plan"], i["ps1"]
    product = ec.product_files(plan)
    first_row = next(line for line in task.splitlines() if line.startswith("| 0 |"))
    cases = [
        ("duplicate row id", lambda: check_task(task.replace(first_row, first_row + "\n" + first_row)), "duplicate row ids"),
        ("unknown check", lambda: check_scripts(task + "\nvalidate-task.ps1 -Check no-such-check\n", ps1, ec), "does not define"),
        ("swapped stage", lambda: check_scripts(task, ps1.replace("@('py-types',", "@('py-tmp',").replace("@('py-lint',", "@('py-types',")
                                                .replace("@('py-tmp',", "@('py-lint',"), ec), "stage order differs"),
        ("gate exclusion added", lambda: check_constants(plan.replace(" docs/BUILD_PLAN.md docs/execution/metrics.md ",
                                                                      " docs/BUILD_PLAN.md docs/proposals/* docs/execution/metrics.md "),
                                                         ps1, ec), "GATED_PATHS differ"),
        ("ps1 gated copy", lambda: check_constants(plan, ps1 + "\n$gated = @('ui')\n", ec), "GATED_PATHS differ"),
        ("changed floor", lambda: check_constants(plan.replace("passed ≥ 655", "passed ≥ 600"), ps1, ec), "COUNT_FLOORS differ"),
        ("AC tier changed", lambda: check_constants(plan.replace("| AC-76.8 | unit (Vitest,", "| AC-76.8 | unit (pytest,"), ps1, ec), "AC tables differ"),
        ("AC row dropped", lambda: check_constants(re.sub(r"^\| AC-77\.13 \|.*\n", "", plan, flags=re.M), ps1, ec), "AC tables differ"),
        ("pin dropped", lambda: check_constants(plan.replace("| AC-77.14 | **pin** — ", "| AC-77.14 | "), ps1, ec), "pins differ"),
        ("TA file changed", lambda: check_constants(plan.replace("**TA-6** `tests/integration/test_sqlite_uow.py",
                                                                 "**TA-6** `tests/integration/test_other.py"), ps1, ec), "TEST_AMENDMENTS differ"),
        ("source audit file dropped", lambda: check_src(ps1.replace("'ui/src/renderer/src/lib/api.ts')", "'x.ts')"), product), "$SRC76 differs"),
        ("red without guard", lambda: check_red(ps1.replace("Ev 'red78-guard' @('red-guard', '--meu', '78'", "Ev 'red78-guard' @('meu-state'")), "red78 does not start"),
        ("TA in red", lambda: check_red(ps1.replace("(Tier 'red' 'pytest' '77' 'red77-py' $PY77)", "(Tier 'red' 'pytest' '77' 'red77-py' ($PY77 + $TA77))")),
         "red77 runs a TEST_AMENDMENTS"),
        ("undefined AC", lambda: check_refs(task + "\nAC-78.99\n", plan, i["grouping"]), "AC-78.99"),
        ("undefined D", lambda: check_refs(task + "\nD-99\n", plan, i["grouping"]), "D-99"),
        # A-10 defined TA-11, so the undefined-TA probe names TA-12.
        ("undefined TA", lambda: check_refs(task + "\nTA-12\n", plan, i["grouping"]), "TA-12"),
        ("missing modify target", lambda: check_files(plan + "\n| `ui/no/such/file.ts` | modify | x |\n", root, True), "missing file"),
        ("existing create target", lambda: check_files(plan + "\n| `pyproject.toml` | create | x |\n", root, True), "already exists"),
        ("missing goal anchor", lambda: check_goal_anchor(plan, "no goal here"), "Goal sentence"),
    ]
    failures: list[str] = []
    for name, fn, needle in cases:
        found = [e for e in fn() if needle in e]
        print(f"{'PASS' if found else 'FAIL'} selftest {name}: {found[0][:140] if found else 'not reported'}")
        if not found:
            failures.append(name)
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["static", "selftest"])
    parser.add_argument("--plan-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    d = args.plan_dir.resolve()
    root = d.parents[3]
    ec = _load_exec_checks(d)
    if Path.cwd().resolve() != root:
        print(f"FAIL: run from the worktree root {root}")
        return 1
    if args.command == "selftest":
        failed = selftest(d, root, ec)
        if failed:
            print(f"FAIL: selftest cases not reported: {failed}")
            return 1
        print("PASS selftest: every injected defect was reported")
        return 0
    errors = run_static(d, root, ec)
    for e in errors:
        print(f"FAIL: {e}")
    if errors:
        return 1
    print(f"PASS static: {len(_rows((d / 'task.md').read_text(encoding='utf-8')))} task rows; script, exec_checks, "
          "plan contracts, references and file targets agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
