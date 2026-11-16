"""Session 76 hermeticity check (AC-5, AC-11; implementation-plan.md §Plan-local checkers).

Usage::

    python hermetic-check.py [--file TEST] [--asserts] [--eol]
    python hermetic-check.py --count RECEIPT
    python hermetic-check.py --selftest

The default checks run on ``TEST_FILE`` (or ``--file``) every time:

* every line ends in CRLF and there is no BOM;
* ``P:/.agent`` occurs exactly once (the ``MACHINE_TOOLS`` constant);
* no line holds both ``AGENT_MODEL_REGISTRY_HOME`` and ``P:/``;
* no call passes the constant ``"--project"`` followed by the name ``ROOT`` (AST);
* the string ``tools/Invoke-CodexDispatch.ps1`` occurs only inside ``fixture_wrapper``.

``--asserts`` compares, for each test in ``TOUCHED`` (§The rewired registry tests and §The
governance fixture), the AST dumps of its ``assert`` statements and of its decorator list with
``BASE`` (``C:/Temp/av-kit/tth/base/test_framework_adoption.py``, row 0's copy).

``--eol`` checks the line endings of every §Files Modified path: CRLF and no BOM for
``TEST_FILE``; BOM and CRLF for ``DISPATCH_TEST``; LF with no CR (and no BOM) for the other four.

``--count RECEIPT`` is the gate's ``adoption-check`` (AC-11): the receipt's pytest summary must
show 0 failed, 0 errors and exactly the passed count of ``tth-base-adoption.txt`` plus 5.

``--selftest`` runs every check on its own fixtures (no repo file): it must accept a good pair
and refuse an extra ``P:/.agent``, a ``--project ROOT`` call, a changed assert, a changed
parametrize list, an LF line, and the count summaries with a failure or the wrong passed count.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

TEST_FILE = "tests/tooling/test_framework_adoption.py"
BASE = "C:/Temp/av-kit/tth/base/test_framework_adoption.py"
BASE_ADOPTION = "C:/Temp/av-kit/tth/tth-base-adoption.txt"
NEW_TESTS = 5
TOUCHED = (
    "test_registry_contract_preserves_bindings",
    "test_registry_contract_vendor_independence",
    "test_registry_contract_unsupported_harness_refused",
    "test_registry_contract_bad_configuration_refused",
    "test_review_pipeline_wrapper_refuses_before_provider",
    "test_review_pipeline_governance_static_oracles",
    "test_governance_preservation_and_routing_inventory",
    "test_registry_contract_generic_class_census",
)
EOL = (
    (TEST_FILE, "crlf"),
    (".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1", "bom-crlf"),
    ("tests/tooling/fixtures/registry-home/model-registry.json", "lf"),
    ("tests/tooling/fixtures/registry-home/make_fixture.py", "lf"),
    (".agent/context/known-issues.yaml", "lf"),
    (".agent/context/known-issues.md", "lf"),
)
WRAPPER = "tools/Invoke-CodexDispatch.ps1"
BOM = b"\xef\xbb\xbf"
SUMMARY = re.compile(r"^=*\s*(\d+ [a-z]+(?:, \d+ [a-z]+)*) in [\d.]+s\b")


def eol(data: bytes, kind: str) -> list[str]:
    problems = []
    has_bom = data.startswith(BOM)
    crlf, lf, cr = data.count(b"\r\n"), data.count(b"\n"), data.count(b"\r")
    if kind in ("crlf", "lf") and has_bom:
        problems.append("has a BOM")
    if kind == "bom-crlf" and not has_bom:
        problems.append("lacks the BOM")
    if kind in ("crlf", "bom-crlf") and (crlf != lf or cr != crlf or not data.endswith(b"\r\n")):
        problems.append(f"not CRLF on every line ({crlf} CRLF, {lf - crlf} bare LF, {cr - crlf} bare CR)")
    if kind == "lf" and (cr or not data.endswith(b"\n")):
        problems.append(f"not LF ({cr} CR, trailing newline={data.endswith(b'\n')})")
    return problems


def default_checks(data: bytes) -> list[str]:
    problems = eol(data, "crlf")
    text = data.decode("utf-8")
    count = text.count("P:/.agent")
    if count != 1:
        problems.append(f"'P:/.agent' occurs {count} times, not once (MACHINE_TOOLS)")
    for n, line in enumerate(text.splitlines(), 1):
        if "AGENT_MODEL_REGISTRY_HOME" in line and "P:/" in line:
            problems.append(f"line {n} holds both AGENT_MODEL_REGISTRY_HOME and 'P:/'")
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            args = node.args
            for a, b in zip(args, args[1:]):
                if isinstance(a, ast.Constant) and a.value == "--project" and isinstance(b, ast.Name) and b.id == "ROOT":
                    problems.append(f"line {a.lineno} passes '--project' ROOT")
    spans = [
        (f.lineno, f.end_lineno or f.lineno)
        for f in ast.walk(tree)
        if isinstance(f, ast.FunctionDef) and f.name == "fixture_wrapper"
    ]
    for n, line in enumerate(text.splitlines(), 1):
        if WRAPPER in line and not any(a <= n <= b for a, b in spans):
            problems.append(f"line {n} names {WRAPPER} outside fixture_wrapper")
    return problems


def _functions(text: str) -> dict[str, ast.FunctionDef]:
    return {f.name: f for f in ast.walk(ast.parse(text)) if isinstance(f, ast.FunctionDef)}


def asserts(new: str, base: str, names: tuple[str, ...] = TOUCHED) -> list[str]:
    problems = []
    nf, bf = _functions(new), _functions(base)
    for name in names:
        if name not in nf or name not in bf:
            problems.append(f"{name}: missing (new={name in nf}, base={name in bf})")
            continue
        for label, pick in (
            ("assert statements", lambda f: [ast.dump(n) for n in ast.walk(f) if isinstance(n, ast.Assert)]),
            ("decorator list", lambda f: [ast.dump(d) for d in f.decorator_list]),
        ):
            if pick(nf[name]) != pick(bf[name]):
                problems.append(f"{name}: {label} differ from BASE")
        print(f"   {name}: {sum(isinstance(n, ast.Assert) for n in ast.walk(nf[name]))} assert(s), "
              f"{len(nf[name].decorator_list)} decorator(s)")
    return problems


def _summary(text: str) -> dict[str, int] | None:
    found = None
    for line in text.splitlines():
        m = SUMMARY.match(line.strip())
        if m:
            found = {word: int(n) for n, word in re.findall(r"(\d+) ([a-z]+)", m.group(1))}
    return found


def count(receipt: str, base: str) -> list[str]:
    r, b = _summary(receipt), _summary(base)
    if r is None or b is None:
        return [f"no pytest summary line (receipt={r is not None}, base={b is not None})"]
    problems = []
    failed, errors = r.get("failed", 0), r.get("error", 0) + r.get("errors", 0)
    want = b.get("passed", 0) + NEW_TESTS
    print(f"adoption receipt {r}; base {b}; want passed {want}")
    if failed or errors:
        problems.append(f"{failed} failed, {errors} error(s)")
    if r.get("passed", 0) != want:
        problems.append(f"passed {r.get('passed', 0)}, want base {b.get('passed', 0)} + {NEW_TESTS} = {want}")
    return problems


SELF_GOOD = (
    "import ast\r\n"
    "from pathlib import Path\r\n"
    "import pytest\r\n"
    "ROOT = Path('.')\r\n"
    'MACHINE_TOOLS = Path("P:/.agent")\r\n'
    "def run(*a, env=None):\r\n"
    "    return a\r\n"
    "def fixture_wrapper(dest, project):\r\n"
    '    return ROOT / "tools/Invoke-CodexDispatch.ps1"\r\n'
    '@pytest.mark.parametrize("x", ["a", "b"])\r\n'
    "def test_sample(x, registry_home):\r\n"
    '    result = run("resolve", "--project", registry_home["project"], env=registry_home["env"])\r\n'
    "    assert result, x\r\n"
)
SELF_BASE = SELF_GOOD.replace('registry_home["project"]', "ROOT").replace(", registry_home)", ")").replace(
    'env=registry_home["env"]', 'env={"AGENT_MODEL_REGISTRY_HOME": "P:/.agent"}').replace(
    'MACHINE_TOOLS = Path("P:/.agent")\r\n', "").replace(
    'def fixture_wrapper(dest, project):\r\n    return ROOT / "tools/Invoke-CodexDispatch.ps1"\r\n', "")


def selftest() -> int:
    failures = []

    def expect(name: str, problems: list[str], accept: bool) -> None:
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} {name}: {'accepted' if ok else problems}")
        if ok != accept:
            failures.append(name)

    good = SELF_GOOD.encode()
    expect("control: the good file", default_checks(good), True)
    expect("control: asserts equal", asserts(SELF_GOOD, SELF_GOOD, ("test_sample",)), True)
    expect("the base file (live inputs)", default_checks(SELF_BASE.encode()), False)
    expect("an extra P:/.agent", default_checks(good + b'OTHER = "P:/.agent/x"\r\n'), False)
    expect("a --project ROOT call", default_checks(good.replace(b'registry_home["project"]', b"ROOT")), False)
    expect("the wrapper named outside fixture_wrapper", default_checks(good + b'W = "tools/Invoke-CodexDispatch.ps1"\r\n'), False)
    expect("an LF line", default_checks(good.replace(b"import ast\r\n", b"import ast\n")), False)
    expect("a changed assert", asserts(SELF_GOOD.replace("assert result, x", "assert result or True, x"), SELF_GOOD, ("test_sample",)), False)
    expect("a changed parametrize list", asserts(SELF_GOOD.replace('["a", "b"]', '["a"]'), SELF_GOOD, ("test_sample",)), False)
    expect("control: eol lf", eol(b"a\nb\n", "lf"), True)
    expect("eol lf with a CR", eol(b"a\r\nb\n", "lf"), False)
    expect("control: eol bom-crlf", eol(BOM + b"a\r\nb\r\n", "bom-crlf"), True)
    expect("eol bom-crlf without the BOM", eol(b"a\r\nb\r\n", "bom-crlf"), False)
    base_summary = "===== 60 passed in 12.3s =====\n"
    expect("control: count base + 5", count("== 65 passed in 13.0s ==\n", base_summary), True)
    expect("count with a failure", count("== 1 failed, 64 passed in 13.0s ==\n", base_summary), False)
    expect("count base + 4", count("== 64 passed in 13.0s ==\n", base_summary), False)
    expect("count with an error", count("== 65 passed, 1 error in 13.0s ==\n", base_summary), False)
    expect("count without a summary", count("nothing here\n", base_summary), False)
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"hermetic-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def _opt(argv: list[str], name: str, default: str) -> str:
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    if "--count" in argv:
        receipt = pathlib.Path(_opt(argv, "--count", ""))
        problems = count(
            receipt.read_text(encoding="utf-8", errors="replace"),
            pathlib.Path(BASE_ADOPTION).read_text(encoding="utf-8", errors="replace"),
        )
    else:
        target = pathlib.Path(_opt(argv, "--file", TEST_FILE))
        print(f"default checks: {target.as_posix()}")
        problems = default_checks(target.read_bytes())
        if "--asserts" in argv:
            print(f"asserts: {target.as_posix()} against {BASE}")
            problems += asserts(target.read_text(encoding="utf-8"), pathlib.Path(BASE).read_text(encoding="utf-8"))
        if "--eol" in argv:
            for path, kind in EOL:
                p = pathlib.Path(path)
                if not p.is_file():
                    problems.append(f"eol: {path} is absent")
                    continue
                found = eol(p.read_bytes(), kind)
                print(f"   eol {kind}: {path}: {'ok' if not found else found}")
                problems += [f"eol: {path}: {f}" for f in found]
    for problem in problems:
        print("FAIL", problem)
    print(f"hermetic-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
