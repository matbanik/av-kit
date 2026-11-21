"""Session 98 test-pin check (task rows 3 and 7 and the gate's ``pins`` step;
implementation-plan.md §Test pins; AC-11; D-1275).

``tests/tooling/test_e2e_remote.py`` is compared, top-level statement by top-level statement
(``ast``), with its row-0 copy under ``C:/Temp/av-kit/e2e-clipboard-specs/baseline-copies/``:

* every row-0 statement is still there, with the same source text, except the ones in
  ``MAY_CHANGE`` (named in §Test pins with their old and new values);
* no row-0 statement is removed;
* a new statement is a function whose name starts ``test_s98_`` or ``_s98_``, or an assignment
  to a name in ``NEW_NAMES``; nothing else may be added (no import, no class);
* the file stays LF, ASCII-only where row 0 was, with one final LF.

Usage, from the repository root::

    python pins-check.py              # the real file against its row-0 copy
    python pins-check.py --selftest   # each rule, on fixtures
"""

from __future__ import annotations

import ast
import pathlib
import sys
import tempfile

PATH = "tests/tooling/test_e2e_remote.py"
COPIES = pathlib.Path("C:/Temp/av-kit/e2e-clipboard-specs/baseline-copies")
#: The row-0 statements §Test pins names (the module docstring gains its Session 98 line).
MAY_CHANGE = frozenset({"<docstring>", "test_ac_11_known_tracked_list"})
#: Module-level names this plan adds.
NEW_NAMES = frozenset({"PROBE_COPIES", "PROBE_STATES_T", "GATED_OUTCOMES_T"})
NEW_PREFIXES = ("test_s98_", "_s98_")


def _key(node: ast.stmt, index: int) -> str:
    if index == 0 and isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
        return "<docstring>"
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        t = node.targets[0]
        if isinstance(t, ast.Name):
            return t.id
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return node.target.id
    return f"<{type(node).__name__}:{ast.dump(node)[:80]}>"


def statements(text: str) -> dict[str, str]:
    tree = ast.parse(text)
    out: dict[str, str] = {}
    for i, node in enumerate(tree.body):
        key = _key(node, i)
        start = node.lineno
        if getattr(node, "decorator_list", None):
            start = min(d.lineno for d in node.decorator_list)
        lines = text.splitlines()[start - 1 : node.end_lineno]
        out[key] = "\n".join(lines)
    return out


def check(old_raw: bytes, new_raw: bytes) -> list[str]:
    problems: list[str] = []
    if b"\r" in new_raw:
        problems.append("the file holds CR bytes; LF expected")
    if not new_raw.endswith(b"\n") or new_raw.endswith(b"\n\n"):
        problems.append("the file must end with exactly one LF")
    if all(b < 128 for b in old_raw) and any(b > 127 for b in new_raw):
        problems.append("a non-ASCII byte was added")
    old = statements(old_raw.decode("utf-8"))
    new = statements(new_raw.decode("utf-8"))
    for key, src in old.items():
        if key not in new:
            problems.append(f"{key}: removed")
        elif new[key] != src and key not in MAY_CHANGE:
            problems.append(f"{key}: changed, and Test pins does not name it")
    for key in new:
        if key in old:
            continue
        if key.startswith(NEW_PREFIXES) or key in NEW_NAMES:
            continue
        problems.append(
            f"{key}: added, and it is not a test_s98_/_s98_ function or a named constant"
        )
    return problems


BASE = '''"""doc."""

import json

X = 1


def test_ac_11_known_tracked_list():
    assert X == 1


def test_ac_7_other():
    assert json
'''

CASES: tuple[tuple[str, str, bool], ...] = (
    ("unchanged", BASE, True),
    ("named-pin", BASE.replace("X == 1", "X == 2", 1), True),
    ("docstring", BASE.replace("doc.", "doc, Session 98."), True),
    ("new-test", BASE + "\n\ndef test_s98_ac_6_probe():\n    assert True\n", True),
    ("new-helper", BASE + "\n\ndef _s98_status():\n    return {}\n", True),
    ("new-const", BASE + "\nPROBE_COPIES = ('a',)\n", True),
    ("unnamed-change", BASE.replace("assert json", "assert not json"), False),
    ("removed", BASE.split("\n\ndef test_ac_7_other")[0] + "\n", False),
    ("unnamed-add", BASE + "\n\ndef test_ac_99_new():\n    assert True\n", False),
    ("new-import", BASE.replace("import json\n", "import json\nimport os\n"), False),
    ("crlf", BASE.replace("\n", "\r\n"), False),
    ("const-changed", BASE.replace("X = 1", "X = 2"), False),
)


def selftest() -> int:
    wrong: list[str] = []
    for name, text, want in CASES:
        problems = check(BASE.encode("ascii"), text.encode("ascii"))
        passed = not problems
        print(f"{name}: {'pass' if passed else 'refused'} (expected {want}) {problems[:1]}")
        if passed != want:
            wrong.append(name)
    with tempfile.TemporaryDirectory() as tmp:
        p = pathlib.Path(tmp) / "x.py"
        p.write_bytes(BASE.encode("ascii"))
        if check(p.read_bytes(), p.read_bytes()):
            wrong.append("file-roundtrip")
    print(f"pins-check selftest: {len(CASES) + 1} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print("usage: pins-check.py [--selftest]")
        return 2
    base = COPIES / PATH
    if not base.is_file():
        print(f"pins-check: no row-0 copy at {base.as_posix()}")
        return 1
    problems = check(base.read_bytes(), pathlib.Path(PATH).read_bytes())
    for p in problems:
        print("PINS-CHECK:", p)
    print(f"pins-check: {PATH}, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
