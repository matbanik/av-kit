"""Session 76 live probe (AC-12, task row 7 and the gate's ``live-probe`` step; D-912).

Usage: ``python live-probe.py`` from the repository root, or ``python live-probe.py --selftest``.

It runs the real machine resolver, ``P:/.agent/tools/resolve_model.py``, against the real
machine registry and ``--project P:/av-kit``, with ``AGENT_MODEL_REGISTRY`` removed from the
child environment, so the resolver finds the registry beside itself:

* the 7 ``test_registry_contract_preserves_bindings`` cases, read by AST from ``BASE``'s
  parametrize list (``C:/Temp/av-kit/tth/base/test_framework_adoption.py``), each with
  ``--format json``: exit 0 and ``expected`` in stdout;
* ``resolve avkit_independent_reviewer --harness codex-cli --author-vendor anthropic``: exit 0
  and ``gpt-6.1-sol`` in stdout; with ``--author-vendor openai``: non-zero and
  ``vendor_diversity_violation`` in stderr;
* ``validate --overlay .agent/model-registry.local.yaml --check-compiled``: exit 0.

It writes nothing. A failure is Stop condition S6: only Mat changes the machine registry.
``--selftest`` checks the case reader: it reads 7 cases from a fixture and refuses a list of 6.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys

RESOLVER = "P:/.agent/tools/resolve_model.py"
PROJECT = "P:/av-kit"
BASE = "C:/Temp/av-kit/tth/base/test_framework_adoption.py"
TEST = "test_registry_contract_preserves_bindings"
MIN_CASES = 7


def cases(text: str) -> list[tuple[str, str, str]]:
    for f in ast.walk(ast.parse(text)):
        if isinstance(f, ast.FunctionDef) and f.name == TEST:
            for d in f.decorator_list:
                if isinstance(d, ast.Call) and getattr(d.func, "attr", "") == "parametrize":
                    found = ast.literal_eval(d.args[1])
                    if len(found) < MIN_CASES:
                        raise ValueError(f"{TEST} has {len(found)} cases, fewer than {MIN_CASES}")
                    return [tuple(c) for c in found]
    raise ValueError(f"{TEST}'s parametrize list not found")


def child_env() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k != "AGENT_MODEL_REGISTRY"}
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def resolver(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, RESOLVER, *args], capture_output=True, text=True, encoding="utf-8",
        env=child_env(), cwd=PROJECT, check=False,
    )


def main() -> int:
    problems: list[str] = []
    with open(BASE, encoding="utf-8") as fh:
        found = cases(fh.read())
    print(f"cases from BASE: {len(found)}")
    for class_name, harness, expected in found:
        r = resolver("resolve", class_name, "--harness", harness, "--project", PROJECT, "--format", "json")
        ok = r.returncode == 0 and expected in r.stdout
        print(f"{'ok  ' if ok else 'BAD '} resolve {class_name} --harness {harness}: exit {r.returncode}, {expected!r} in stdout={expected in r.stdout}")
        if not ok:
            problems.append(f"{class_name}/{harness}: {r.stderr.strip()[-300:]}")
    for vendor, refuse in (("anthropic", False), ("openai", True)):
        r = resolver("resolve", "avkit_independent_reviewer", "--harness", "codex-cli", "--project", PROJECT,
                     "--author-vendor", vendor, "--format", "json")
        if refuse:
            ok = r.returncode != 0 and "vendor_diversity_violation" in r.stderr
        else:
            ok = r.returncode == 0 and "gpt-6.1-sol" in r.stdout
        print(f"{'ok  ' if ok else 'BAD '} reviewer --author-vendor {vendor}: exit {r.returncode}")
        if not ok:
            problems.append(f"reviewer/{vendor}: {(r.stderr or r.stdout).strip()[-300:]}")
    r = resolver("validate", "--overlay", ".agent/model-registry.local.yaml", "--check-compiled")
    ok = r.returncode == 0
    print(f"{'ok  ' if ok else 'BAD '} validate --overlay --check-compiled: exit {r.returncode}; {(r.stdout + r.stderr).strip()[-200:]}")
    if not ok:
        problems.append(f"check-compiled: {(r.stdout + r.stderr).strip()[-300:]}")
    for p in problems:
        print("FAIL", p)
    print(f"live-probe: {'ok' if not problems else f'{len(problems)} problem(s); stop on S6'}")
    return 1 if problems else 0


def selftest() -> int:
    rows = ", ".join(f'("c{i}", "h{i}", "e{i}")' for i in range(7))
    good = f'@pytest.mark.parametrize(("class_name", "harness", "expected"), [{rows}])\ndef {TEST}(): pass\n'
    short = good.replace(', ("c6", "h6", "e6")', "")
    failures = []
    try:
        n = len(cases(good))
        print(f"{'ok  ' if n == 7 else 'BAD '} control: 7 cases read ({n})")
        if n != 7:
            failures.append("control")
    except ValueError as exc:
        print("BAD  control:", exc)
        failures.append("control")
    try:
        cases(short)
        print("BAD  a list of 6 was accepted")
        failures.append("short")
    except ValueError as exc:
        print("ok   a list of 6 refused:", exc)
    print(f"live-probe selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(selftest() if "--selftest" in sys.argv else main())
