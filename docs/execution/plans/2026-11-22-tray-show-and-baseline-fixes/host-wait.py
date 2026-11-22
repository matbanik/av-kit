"""Session 102 host-load gate (S12 runs; implementation-plan.md §Project files). Every Electron step
in the rows and the gate runs this first.

    uv run --no-sync python <PLAN>/host-wait.py
    uv run --no-sync python <PLAN>/host-wait.py --selftest

``<PLAN>`` is ``docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes``. It loads the copied
``load-run.py`` beside it (Session 101's copy, itself Session 99's and 94's copy of Session
90's, with
``host_load_wait``'s limit at 50 %) by file path and calls ``host_load_wait()``: five samples two
seconds apart, then while the mean is above 50 % a 30 s wait and a new sample, for up to 10
minutes. The load it ran at is printed. When that load is still above LIMIT, the step must not
run: this script exits 1 (``host-wait: above the limit``). Otherwise it exits 0
(``host-wait: ok``). ``--selftest`` checks the verdict on fixed loads and that the copied
function is importable; it samples nothing and starts no process.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
LOAD_RUN = HERE / "load-run.py"
LIMIT = 50.0


def load_run_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("load_run", LOAD_RUN)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verdict(load: float) -> int:
    return 1 if load > LIMIT else 0


def selftest() -> int:
    failures: list[str] = []
    for load, want in ((0.0, 0), (49.9, 0), (50.0, 0), (50.1, 1), (97.0, 1)):
        got = verdict(load)
        print(f"load {load}: exit {got} (expected {want})")
        if got != want:
            failures.append(f"load {load}")
    if not callable(getattr(load_run_module(), "host_load_wait", None)):
        failures.append("host_load_wait is not importable from load-run.py")
    print(f"host-wait selftest: {len(failures)} failure(s) {failures}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print("usage: host-wait.py [--selftest]")
        return 2
    load = load_run_module().host_load_wait()
    code = verdict(load)
    print(f"host-wait: {'above the limit' if code else 'ok'} ({load} %, limit {LIMIT:g} %)")
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
