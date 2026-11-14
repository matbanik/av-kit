"""Review-limits dispatch-suite check (rows 0 and 8, the gate's dispatch-tests step; AC-13).

Usage::

    python dispatch-check.py [--exact-baseline] --exit-file RECEIPT.exit RECEIPT
    python dispatch-check.py --selftest [--base RECEIPT]

``RECEIPT`` is a ``Test-CliDispatch.ps1`` receipt; ``RECEIPT.exit`` holds the suite's exit,
saved straight after the run. ANSI colour codes are stripped first. The check accepts only when
all of these hold (implementation-plan.md §Verification Plan 1):

* the receipt has exactly one ``Total: N | PASS: p FAIL: f SKIP: s`` line;
* the bracketed records agree with those counts: ``[PASS] name (Ns) - msg`` and
  ``[FAIL] name (Ns) - msg``, and ``[SKIP] name - reason`` (``Write-TestSkip`` prints no
  duration, D-741). The summary table's unbracketed rows are not records;
* N is at least ``MIN_TOTAL``, the plan-time total;
* every FAIL name is one of ``BASELINE_FAILS``; with ``--exact-baseline`` the FAIL set must be
  that pair exactly;
* the exit is 0 when f is 0 and 1 when f is above 0, which is how the suite ends
  (``Test-CliDispatch.ps1:1133``). Any other exit, such as a startup failure, is refused.

``--selftest`` builds its fixtures from row 0's receipt (``--base``, default
``C:/Temp/av-kit/rl/rl-base-dispatch.txt``): it must accept that receipt with exit 1 and refuse
the receipt plus an added ``[FAIL]`` record, an empty receipt with exit 64, and the receipt with a
``Total:`` line that disagrees with its records.
"""

from __future__ import annotations

import pathlib
import re
import sys

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
RUN = re.compile(r"^\s*\[(PASS|FAIL)\] (.+?) \([0-9.]+s\) - ")
SKIP = re.compile(r"^\s*\[SKIP\] (.+?) - ")
TOTAL = re.compile(r"^\s*Total: (\d+) \| PASS: (\d+) FAIL: (\d+) SKIP: (\d+)\s*$")
MIN_TOTAL = 31
BASELINE_FAILS = frozenset({"placeholder receipts dir refused", "refusal created no placeholder dir"})
DEFAULT_BASE = "C:/Temp/av-kit/rl/rl-base-dispatch.txt"


def check(text: str, exit_text: str, exact: bool) -> list[str]:
    text = ANSI.sub("", text).replace("\r\n", "\n").replace("\r", "\n")
    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    fails: list[str] = []
    totals: list[tuple[int, int, int, int]] = []
    for line in text.split("\n"):
        run = RUN.match(line)
        if run:
            counts[run.group(1)] += 1
            if run.group(1) == "FAIL":
                fails.append(run.group(2))
            continue
        skip = SKIP.match(line)
        if skip:
            counts["SKIP"] += 1
            continue
        total = TOTAL.match(line)
        if total:
            totals.append(tuple(int(g) for g in total.groups()))  # type: ignore[arg-type]
    problems: list[str] = []
    try:
        code = int(exit_text.strip().lstrip("\ufeff"))
    except ValueError:
        problems.append(f"the exit file holds {exit_text.strip()!r}, not an integer")
        code = None
    if len(totals) != 1:
        problems.append(f"expected one 'Total: N | PASS: p FAIL: f SKIP: s' line, found {len(totals)}")
        return problems
    n, p, f, s = totals[0]
    if (p, f, s) != (counts["PASS"], counts["FAIL"], counts["SKIP"]) or n != p + f + s:
        problems.append(
            f"Total line says {n} = PASS {p} + FAIL {f} + SKIP {s}, records say "
            f"PASS {counts['PASS']} FAIL {counts['FAIL']} SKIP {counts['SKIP']}"
        )
    if n < MIN_TOTAL:
        problems.append(f"Total {n} is below the plan-time {MIN_TOTAL}")
    unknown = [name for name in fails if name not in BASELINE_FAILS]
    if unknown:
        problems.append(f"FAIL record(s) outside the baseline pair: {unknown}")
    if exact and set(fails) != BASELINE_FAILS:
        problems.append(f"--exact-baseline: FAIL set {sorted(set(fails))} is not {sorted(BASELINE_FAILS)}")
    if code is not None:
        expected = 1 if f else 0
        if code != expected:
            problems.append(f"exit {code}, but a suite with {f} FAIL(s) ends with exit {expected}")
    print(f"dispatch receipt: Total {n} PASS {p} FAIL {f} SKIP {s}; exit {code}; FAIL names {fails}")
    return problems


def selftest(base_path: str) -> int:
    base = pathlib.Path(base_path).read_text(encoding="utf-8", errors="replace")
    failures: list[str] = []
    lines = base.replace("\r\n", "\n").split("\n")
    last_fail = max(n for n, ln in enumerate(lines) if RUN.match(ANSI.sub("", ln)) and "[FAIL]" in ln)
    added = lines[: last_fail + 1] + ["  [FAIL] an added failure (0s) - injected"] + lines[last_fail + 1 :]
    mismatched = [TOTAL.sub("  Total: 31 | PASS: 30 FAIL: 1 SKIP: 0", ANSI.sub("", ln)) for ln in lines]
    cases = (
        ("control: the baseline receipt with exit 1 (--exact-baseline)", base, "1", True, True),
        ("control: the baseline receipt with exit 1", base, "1", False, True),
        ("the baseline receipt with exit 0", base, "0", False, False),
        ("an added [FAIL] record", "\n".join(added), "1", False, False),
        ("an empty receipt with exit 64", "", "64", False, False),
        ("a Total line that disagrees with the records", "\n".join(mismatched), "1", False, False),
    )
    for name, text, code, exact, accept in cases:
        problems = check(text, code, exact)
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} {name}: {'accepted' if ok else problems}")
        if ok != accept:
            failures.append(name)
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"dispatch-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        base = argv[argv.index("--base") + 1] if "--base" in argv else DEFAULT_BASE
        return selftest(base)
    exact = "--exact-baseline" in argv
    args = [a for a in argv if a != "--exact-baseline"]
    if len(args) != 3 or args[0] != "--exit-file":
        print(__doc__)
        return 2
    exit_file, receipt = pathlib.Path(args[1]), pathlib.Path(args[2])
    problems = check(
        receipt.read_text(encoding="utf-8", errors="replace"),
        exit_file.read_text(encoding="utf-8", errors="replace"),
        exact,
    )
    for problem in problems:
        print("FAIL", problem)
    print(f"dispatch-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
