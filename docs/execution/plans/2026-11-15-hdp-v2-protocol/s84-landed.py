"""Session 85 gate S2: Session 84 (closeout-record-once) has landed and is closed. Read-only.

Usage::

    python s84-landed.py            # task row 0: exit 0 when Session 84 is closed, else 12
    python s84-landed.py --selftest

Session 84's own port contract is the proof, not names chosen here. The check imports Session
84's read-only ``port-check.py`` (never edits it) and requires, on the live tree:

- ``port-check.run(VALIDATOR)`` reports no problem: the three removed names are gone, the four
  new names exist (``decision_field_text``, ``_NON_TEXT_SCALAR``, ``_quoted_scalar_text``,
  ``grouping_row_problems``), ``decision_field_text`` reads quoted values with
  ``_quoted_scalar_text`` and never ``_unquote``, ``grouping_decisions`` calls
  ``grouping_row_problems``, and every other ``PORT_SHAPE`` point and line-ending rule holds;
- every row of Session 84's ``task.md`` task table has status ``[x]`` (a reflection's
  existence alone is not proof of a completed session);
- Session 84's handoff and reflection exist.

The fresh closeout selftest and the Session 84 ``pytest -v`` receipts are separate baseline
steps (``baseline.ps1``). ``--selftest`` proves that port-check's ``PORTED`` fixture passes,
that ``PRE_PORT`` and each half-port are refused, and that an open task row or a missing
closeout artifact is refused.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
import tempfile
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[4]
S84_PLAN = "docs/execution/plans/2026-11-15-closeout-record-once"
PORT_CHECK = f"{S84_PLAN}/port-check.py"
S84_TASK = f"{S84_PLAN}/task.md"
VALIDATOR = "tools/validate_closeout_artifacts.py"
CLOSEOUT = (
    ".agent/context/handoffs/2026-11-15-closeout-record-once-handoff.md",
    "docs/execution/reflections/2026-11-15-closeout-record-once-reflection.md",
)
NOT_CLOSED = 12
STATUS = re.compile(r"^`?\[(.)\]`?$")


def load_port_check(root: Path = ROOT) -> ModuleType:
    path = root / PORT_CHECK
    spec = importlib.util.spec_from_file_location("s84_port_check", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(module)
    return module


def task_problems(text: str) -> list[str]:
    """Every task-table row (a row whose last cell is a status box) must be ``[x]``."""
    rows = 0
    bad = []
    for line in text.replace("\r\n", "\n").split("\n"):
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        m = STATUS.match(cells[-1]) if cells else None
        if not m:
            continue
        rows += 1
        if m.group(1) != "x":
            bad.append(f"S84 task row {cells[0] or '?'} is [{m.group(1)}], not [x]")
    if not rows:
        bad.append("S84 task.md has no task-table status cells")
    return bad


def artifact_problems(root: Path) -> list[str]:
    return [f"S84 closeout artifact missing: {p}" for p in CLOSEOUT if not (root / p).is_file()]


def landed_problems(root: Path = ROOT) -> list[str]:
    port = load_port_check(root)
    bad = [f"S84 port-check: {p}" for p in port.run(root / VALIDATOR)]
    task = root / S84_TASK
    bad += task_problems(task.read_text(encoding="utf-8")) if task.is_file() else [
        f"S84 task missing: {S84_TASK}"]
    return bad + artifact_problems(root)


def _def_span(text: str, func: str) -> tuple[int, int]:
    """Character span of the module-level ``def func`` block in text (found with ast)."""
    lines = text.splitlines(keepends=True)
    for node in ast.parse(text).body:
        if isinstance(node, ast.FunctionDef) and node.name == func:
            start = sum(len(ln) for ln in lines[: node.lineno - 1])
            return start, sum(len(ln) for ln in lines[: node.end_lineno])
    raise AssertionError(f"selftest fixture PORTED has no def {func}")


def _rename_def(text: str, func: str) -> str:
    """Rename ``def func`` to ``def func_removed``, whatever its body."""
    start, end = _def_span(text, func)
    block = text[start:end].replace(f"def {func}(", f"def {func}_removed(", 1)
    return text[:start] + block + text[end:]


def _edit_def(text: str, func: str, old: str, new: str) -> str:
    """Replace ``old`` with ``new`` inside the ``def func`` block only."""
    start, end = _def_span(text, func)
    return text[:start] + text[start:end].replace(old, new) + text[end:]


def selftest() -> int:
    port = load_port_check()
    ok = True

    def arm(name: str, problems: list[str], want_refused: bool) -> None:
        nonlocal ok
        right = bool(problems) == want_refused
        print(f"{'ok  ' if right else 'MISS'} {name}: {'refused' if problems else 'accepted'}")
        ok &= right

    shape = port.shape_problems
    ported = port.PORTED
    arm("port-check PORTED fixture passes", shape(ported), False)
    arm("port-check PRE_PORT fixture refused", shape(port.PRE_PORT), True)
    # Each half-port edits PORTED by function name, whatever the function bodies are (plan
    # review R2, F3), and must actually change it.
    half_ports = [
        ("half-port without _quoted_scalar_text refused",
         _rename_def(ported, "_quoted_scalar_text")),
        ("half-port with upstream _unquote refused",
         _edit_def(ported, "decision_field_text", "_quoted_scalar_text(", "_unquote(")),
        ("half-port keeping DECISIONS_LOG_HEADERS refused",
         ported + "DECISIONS_LOG_HEADERS = []\n"),
        ("half-port whose grouping_decisions skips grouping_row_problems refused",
         _edit_def(ported, "grouping_decisions", "grouping_row_problems(",
                   "grouping_row_skipped(")),
    ]
    for name, specimen in half_ports:
        if specimen == ported:
            raise AssertionError(f"selftest fault did not change PORTED: {name}")
        arm(name, shape(specimen), True)
    head = "| # | Task | Status |\n|---|---|---|\n"
    arm("S84 task with every row [x] accepted",
        task_problems(head + "| 0 | a | `[x]` |\n| |  |  |\n| H2-1 | b | `[x]` |\n"), False)
    arm("S84 task with an open row refused",
        task_problems(head + "| 0 | a | `[x]` |\n| H2-1 | b | `[ ]` |\n"), True)
    arm("S84 task with a blocked row refused", task_problems(head + "| 0 | a | `[B]` |\n"), True)
    arm("S84 task with no status cells refused", task_problems(head), True)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for rel in CLOSEOUT:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("x\n", encoding="utf-8")
        arm("S84 handoff and reflection present accepted", artifact_problems(root), False)
        (root / CLOSEOUT[1]).unlink()
        arm("S84 reflection missing refused", artifact_problems(root), True)
    print("s84-landed selftest:", "0 failures" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    if sys.argv[1:] == ["--selftest"]:
        return selftest()
    if sys.argv[1:]:
        print("usage: s84-landed.py [--selftest]")
        return 2
    problems = landed_problems()
    for p in problems:
        print("FAIL", p)
    print("s84-landed:", "Session 84 is closed" if not problems else
          f"{len(problems)} problem(s); Session 84 is not closed (S2)")
    return NOT_CLOSED if problems else 0


if __name__ == "__main__":
    sys.exit(main())
