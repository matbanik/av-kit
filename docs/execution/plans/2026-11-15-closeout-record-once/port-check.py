"""Session 84 port check (task row 5 and the session gate; implementation-plan.md AC-15, AC-16).

Usage::

    python port-check.py [--validator PATH]
    python port-check.py --selftest

Reads the closeout validator as text and as a syntax tree (it never imports it) and exits 1
unless the port's static shape holds (``PORT_SHAPE`` in the plan):

- ``DECISION_RESOLUTIONS``, ``DECISIONS_LOG_HEADERS`` and ``reflection_decision_rows`` are
  gone; ``decision_field_text``, ``_NON_TEXT_SCALAR``, ``_quoted_scalar_text`` and
  ``grouping_row_problems`` exist, and so does ``DQ_ESCAPE_VALUES``;
- the av-kit deviation from upstream is expected, not flagged (D-831, amended after plan
  review R1, CRO-P1): ``decision_field_text`` reads a quoted value with
  ``_quoted_scalar_text(`` and never calls ``_unquote(``;
- ``_quoted_scalar_text`` gives each ``QUOTED_PROBES`` answer (amended after the R1 recheck,
  CRO-R1-1): a double-quoted body's YAML escapes are decoded, so ``"\\n"`` is a newline and
  ``"\\u0070ending Mat"`` is pending; a single-quoted body is literal; a quoted ``#`` is
  text. Only that function and the constants it reads are executed, never the validator;
- ``grouping_decisions`` judges each row with ``grouping_row_problems(`` (D-829, amended
  after R1, CRO-P2);
- ``GROUPING_DECISION_HEADERS`` is a literal list of the seven grouping columns, with no
  ``Stage``, and ``GROUPING_RESOLUTIONS`` is still ``("autonomous", "human", "open")``;
- ``check_decisions_log`` takes exactly ``(sources, issues)``: no reflection text, and the
  repeatable ``--decision-issue`` kept (D-828);
- ``project_root`` stops at a ``.git`` directory or file (``ec3857a``);
- no line above the selftest fixtures (the first ``_GOOD_REFLECTION_TEMPLATE =`` line) says
  ``reconcil`` in any case, and the file nowhere says ``must each have a row`` or
  ``matched to a reflection row`` (D-827, D-833);
- the module docstring says ``stated in full`` and ``holds no template example``;
- line endings (AC-16): each ``CRLF_FILES`` path has only CRLF line ends, and each
  ``LF_FILES`` path that exists has none.

Read-only. ``--selftest`` exits 1 unless a pre-port source is refused on each point and a
ported source passes.
"""

from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
DEFAULT_VALIDATOR = ROOT / "tools" / "validate_closeout_artifacts.py"
CRLF_FILES = ("tools/validate_closeout_artifacts.py", "tests/tooling/test_closeout_register_grammar.py")
LF_FILES = (
    "tests/tooling/test_closeout_record_once.py",
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
)
GONE = ("DECISION_RESOLUTIONS", "DECISIONS_LOG_HEADERS", "reflection_decision_rows")
PRESENT = (
    "decision_field_text",
    "_NON_TEXT_SCALAR",
    "_quoted_scalar_text",
    "DQ_ESCAPE_VALUES",
    "grouping_row_problems",
)
GROUPING_HEADERS = [
    "ID",
    "Question",
    "Resolution",
    "Chosen",
    "Source tag",
    "Reasoning (why this; why the alternatives lost)",
    "Human ref",
]
STALE_PHRASES = ("must each have a row", "matched to a reflection row")
BS = "\\"
# What _quoted_scalar_text must return (D-831, amended after the R1 recheck, CRO-R1-1): a
# double-quoted body's YAML escapes decoded, a single-quoted body literal, a quoted # kept.
QUOTED_PROBES = (
    ('"' + BS + 'n"', "\n"),  # tools/issue_triage/model.py's newline-only value
    ('"' + BS + "u0070ending Mat" + '"', "pending Mat"),
    ('"' + BS + 't"', "\t"),
    ('"' + BS + "x20" + BS + 'L"', " " + chr(0x2028)),
    ('"say ' + BS + '"x' + BS + '" ' + BS + BS + " " + BS + "x7Bid" + BS + 'x7D"', 'say "x" ' + BS + " {id}"),
    ('"' + BS + "U0001F600" + '"', chr(0x1F600)),
    ('"Keep # 3" # note', "Keep # 3"),
    ("'it''s " + BS + "n'", "it's " + BS + "n"),
    ('"' + BS + 'q"', None),
    ('"' + BS + 'u00G0"', None),
    ('"a" b', None),
)
FIXTURE_START = re.compile(r"^_GOOD_REFLECTION_TEMPLATE = ", re.MULTILINE)


def module_names(tree: ast.Module) -> tuple[dict[str, ast.AST], dict[str, ast.FunctionDef]]:
    assigned: dict[str, ast.AST] = {}
    functions: dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = node
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            assigned[node.target.id] = node.value
    return assigned, functions


def quoted_probe_problems(text: str, assigned: dict[str, ast.AST], functions: dict[str, ast.FunctionDef]) -> list[str]:
    """Run ``_quoted_scalar_text`` alone on ``QUOTED_PROBES``.

    Only that function and the module constants it reads, directly or through another
    constant, are executed, with ``re`` in scope; the validator itself is never imported.
    """
    function = functions.get("_quoted_scalar_text")
    if function is None:
        return []
    needed: list[str] = []
    pending = [n.id for n in ast.walk(function) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)]
    while pending:
        name = pending.pop()
        if name in assigned and name not in needed:
            needed.append(name)
            pending += [n.id for n in ast.walk(assigned[name]) if isinstance(n, ast.Name)]
    order = [name for name in assigned if name in needed]  # module order
    source = "\n".join(f"{name} = {ast.get_source_segment(text, assigned[name])}" for name in order)
    namespace: dict[str, object] = {"re": re}
    try:
        exec(compile(source + "\n" + ast.get_source_segment(text, function), "<quoted>", "exec"), namespace)
    except Exception as exc:  # noqa: BLE001 - any failure is a refusal
        return [f"_quoted_scalar_text could not be run alone: {exc!r}"]
    problems = []
    for raw, want in QUOTED_PROBES:
        try:
            got = namespace["_quoted_scalar_text"](raw)
        except Exception as exc:  # noqa: BLE001
            got = f"raised {exc!r}"
        if got != want:
            problems.append(f"_quoted_scalar_text({raw!r}) gave {got!r}, expected {want!r}")
    return problems


def shape_problems(text: str) -> list[str]:
    problems: list[str] = []
    tree = ast.parse(text)
    assigned, functions = module_names(tree)
    names = set(assigned) | set(functions)
    for name in GONE:
        if name in names:
            problems.append(f"{name} is still defined")
    for name in PRESENT:
        if name not in names:
            problems.append(f"{name} is not defined")
    headers = assigned.get("GROUPING_DECISION_HEADERS")
    try:
        value = ast.literal_eval(headers) if headers is not None else None
    except ValueError:
        value = None
    if value != GROUPING_HEADERS:
        problems.append(f"GROUPING_DECISION_HEADERS is not the literal seven-column list: {value!r}")
    resolutions = assigned.get("GROUPING_RESOLUTIONS")
    try:
        resolutions_value = ast.literal_eval(resolutions) if resolutions is not None else None
    except ValueError:
        resolutions_value = None
    if resolutions_value != ("autonomous", "human", "open"):
        problems.append(f"GROUPING_RESOLUTIONS changed: {resolutions_value!r}")
    field = functions.get("decision_field_text")
    field_source = (ast.get_source_segment(text, field) if field else "") or ""
    if "_quoted_scalar_text(" not in field_source:
        problems.append("decision_field_text does not read quoted values with _quoted_scalar_text")
    if "_unquote(" in field_source:
        problems.append("decision_field_text still calls _unquote (the upstream quoted-comment bug)")
    problems += quoted_probe_problems(text, assigned, functions)
    grouping = functions.get("grouping_decisions")
    grouping_source = (ast.get_source_segment(text, grouping) if grouping else "") or ""
    if "grouping_row_problems(" not in grouping_source:
        problems.append("grouping_decisions does not judge its rows with grouping_row_problems")
    check = functions.get("check_decisions_log")
    params = [a.arg for a in check.args.args] if check else None
    if params != ["sources", "issues"]:
        problems.append(f"check_decisions_log takes {params}, expected ['sources', 'issues']")
    root = functions.get("project_root")
    root_source = ast.get_source_segment(text, root) if root else ""
    if '(ancestor / ".git").exists()' not in (root_source or ""):
        problems.append("project_root does not stop at a .git directory or file")
    fixtures = FIXTURE_START.search(text)
    head = text[: fixtures.start()] if fixtures else text
    stale = [n for n, line in enumerate(head.splitlines(), 1) if "reconcil" in line.lower()]
    if stale:
        problems.append(f"'reconcil' above the selftest fixtures at line(s) {stale}")
    for phrase in STALE_PHRASES:
        if phrase in text:
            problems.append(f"the file still says {phrase!r}")
    doc = ast.get_docstring(tree) or ""
    flat = " ".join(doc.split())
    for phrase in ("stated in full", "holds no template example"):
        if phrase not in flat:
            problems.append(f"the module docstring lacks {phrase!r}")
    return problems


def ending_problems(paths: dict[str, bytes], crlf: tuple[str, ...], lf: tuple[str, ...]) -> list[str]:
    problems: list[str] = []
    for rel, data in paths.items():
        pairs = data.count(b"\r\n")
        bare = data.count(b"\n") - pairs
        if rel in crlf and (bare or not pairs):
            problems.append(f"{rel} is no longer CRLF: crlf {pairs} bare-lf {bare}")
        if rel in lf and pairs:
            problems.append(f"{rel} gained CRLF line ends: crlf {pairs} bare-lf {bare}")
    return problems


def run(validator: pathlib.Path) -> list[str]:
    problems = shape_problems(validator.read_bytes().decode("utf-8").replace("\r\n", "\n"))
    data = {rel: (ROOT / rel).read_bytes() for rel in CRLF_FILES + LF_FILES if (ROOT / rel).exists()}
    missing = [rel for rel in CRLF_FILES if rel not in data]
    if missing:
        problems.append(f"missing file(s): {missing}")
    problems += ending_problems(data, CRLF_FILES, LF_FILES)
    print(f"port-check: {validator}: line ends read for {sorted(data)}")
    return problems


PRE_PORT = '''"""Closeout validator.

handoff or issue has a Decisions Log row
"""
DECISION_RESOLUTIONS = ("autonomous", "human")
DECISIONS_LOG_HEADERS = ["ID", "Stage", "Question", "Resolution", "Chosen", "Source tag",
    "Reasoning (why this; why the alternatives lost)", "Human ref"]
GROUPING_DECISION_HEADERS = [h for h in DECISIONS_LOG_HEADERS if h != "Stage"]
GROUPING_RESOLUTIONS = ("autonomous", "human", "open")


def reflection_decision_rows(text, path):
    return {}


def decision_field_text(item, key):
    return _unquote(item)


def grouping_decisions(text, name):
    return []


def check_decisions_log(text, path, sources, issues):
    return "recorded decision(s) reconciled against rows"


def project_root(plan_path):
    for ancestor in plan_path.parents:
        if (ancestor / ".agent").is_dir():
            return ancestor
    return plan_path.parent


HELP = "decisions must each have a row in the reflection's Decisions Log"
_GOOD_REFLECTION_TEMPLATE = "x"
'''

PORTED = r'''"""Closeout validator.

plus: every decision recorded in the plan, handoff or issue is stated in full, and the
reflection's Decisions Log holds no template example
"""
import re

DQ_ESCAPES = '0abt\tnvfre "/\\N_LP'
DQ_HEX_ESCAPES = {"x": 2, "u": 4, "U": 8}
DQ_ESCAPE_VALUES = dict(
    zip(DQ_ESCAPES, "\0\a\b\t\t\n\v\f\r\x1b \"/\\\x85\xa0" + chr(0x2028) + chr(0x2029))
)
_QUOTED_SCALAR = re.compile(
    r"""^(?:"(?P<double>(?:[^"\\]|\\.)*)"|'(?P<single>(?:[^']|'')*)')[ \t]*(?:#.*)?$"""
)
GROUPING_DECISION_HEADERS = [
    "ID",
    "Question",
    "Resolution",
    "Chosen",
    "Source tag",
    "Reasoning (why this; why the alternatives lost)",
    "Human ref",
]
GROUPING_RESOLUTIONS = ("autonomous", "human", "open")
_NON_TEXT_SCALAR = None


def _quoted_scalar_text(raw):
    match = _QUOTED_SCALAR.match(raw)
    if match is None:
        return None
    if match.group("single") is not None:
        return match.group("single").replace("''", "'")
    body = match.group("double")
    out, n = [], 0
    while n < len(body):
        if body[n] != "\\":
            out.append(body[n])
            n += 1
            continue
        esc = body[n + 1]
        if esc in DQ_HEX_ESCAPES:
            width = DQ_HEX_ESCAPES[esc]
            digits = body[n + 2 : n + 2 + width]
            if (
                len(digits) != width
                or any(d not in "0123456789abcdefABCDEF" for d in digits)
                or int(digits, 16) > 0x10FFFF
            ):
                return None
            out.append(chr(int(digits, 16)))
            n += 2 + len(digits)
            continue
        if esc not in DQ_ESCAPE_VALUES:
            return None
        out.append(DQ_ESCAPE_VALUES[esc])
        n += 2
    return "".join(out)


def decision_field_text(item, key):
    return _quoted_scalar_text(item)


def grouping_row_problems(cells):
    return []


def grouping_decisions(text, name):
    for cells in []:
        grouping_row_problems(cells)
    return []


def check_decisions_log(sources, issues):
    return "stage-log decision(s) read, each stated in full"


def project_root(plan_path):
    for ancestor in plan_path.parents:
        if (ancestor / ".agent").is_dir():
            return ancestor
        if (ancestor / ".git").exists():
            return plan_path.parent
    return plan_path.parent


HELP = "the stage logs whose decisions are read at closeout"
_GOOD_REFLECTION_TEMPLATE = "x"
ARM = "decision-issue-repeated-reconciled-ok"
'''


def selftest() -> int:
    failures: list[str] = []
    ported = shape_problems(PORTED)
    if ported:
        failures.append(f"control: the ported source was refused: {ported}")
    before = " | ".join(shape_problems(PRE_PORT))
    for expected in (
        "DECISION_RESOLUTIONS is still defined",
        "DECISIONS_LOG_HEADERS is still defined",
        "reflection_decision_rows is still defined",
        "_NON_TEXT_SCALAR is not defined",
        "_quoted_scalar_text is not defined",
        "DQ_ESCAPE_VALUES is not defined",
        "grouping_row_problems is not defined",
        "decision_field_text does not read quoted values",
        "decision_field_text still calls _unquote",
        "grouping_decisions does not judge its rows",
        "GROUPING_DECISION_HEADERS is not the literal",
        "check_decisions_log takes",
        "project_root does not stop",
        "'reconcil' above the selftest fixtures",
        "must each have a row",
        "lacks 'stated in full'",
    ):
        if expected not in before:
            failures.append(f"the pre-port source was not refused for: {expected}")
    single = PORTED.replace("def check_decisions_log(sources, issues)", "def check_decisions_log(sources, issue)")
    if not any("check_decisions_log takes" in p for p in shape_problems(single)):
        failures.append("a single --decision-issue signature was accepted")
    upstream_quote = PORTED.replace("return _quoted_scalar_text(item)", "return _unquote(item)")
    if not any("still calls _unquote" in p for p in shape_problems(upstream_quote)):
        failures.append("a decision_field_text that keeps upstream's _unquote was accepted")
    raw_escapes = PORTED.replace('    body = match.group("double")', '    return match.group("double")')
    if not any("expected 'pending Mat'" in p for p in shape_problems(raw_escapes)):
        failures.append("a _quoted_scalar_text that returns the raw escape spelling was accepted")
    no_hex = PORTED.replace("        if esc in DQ_HEX_ESCAPES:", "        if False:")
    if not any("expected 'pending Mat'" in p for p in shape_problems(no_hex)):
        failures.append("a _quoted_scalar_text that skips the hex escapes was accepted")
    unchecked = PORTED.replace("        grouping_row_problems(cells)\n", "        pass\n")
    if not any("grouping_decisions does not judge" in p for p in shape_problems(unchecked)):
        failures.append("a grouping_decisions that skips grouping_row_problems was accepted")
    endings = ending_problems(
        {"a.py": b"x\r\ny\n", "b.py": b"x\r\n", "c.yaml": b"x\r\n", "d.md": b"x\n"},
        ("a.py", "b.py"),
        ("c.yaml", "d.md"),
    )
    if [p.split(" ")[0] for p in endings] != ["a.py", "c.yaml"]:
        failures.append(f"line-ending check wrong: {endings}")
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"port-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--validator", type=pathlib.Path, default=DEFAULT_VALIDATOR)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    problems = run(args.validator)
    for problem in problems:
        print("FAIL", problem)
    print(f"port-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
