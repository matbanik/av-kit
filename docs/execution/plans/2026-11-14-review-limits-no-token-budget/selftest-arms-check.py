"""Review-limits selftest arm check (task rows 0 and 4; implementation-plan.md AC-12).

Usage::

    python selftest-arms-check.py --write-before OUT RECEIPT   # row 0: record today's arm names
    python selftest-arms-check.py --before BEFORE RECEIPT      # row 4 and the gate
    python selftest-arms-check.py --selftest

``RECEIPT`` is a ``tools/review_ledger.py selftest`` receipt. Its arm lines are
``PASS <label> <got>`` or ``FAIL <label> <got>`` and it ends with
``RESULT: N arm(s), F failure(s) ...``. The check accepts only when the receipt has that
``RESULT`` line, F is 0, no arm line says ``FAIL``, the number of arm lines equals N, no label
repeats, every label in ``BEFORE`` is still present (V31: a selftest must not shrink), and every
label in ``REQUIRED_NEW`` (upstream 6dd76b7's ``limits-*`` arms and D-733's new arm) is present.
``--write-before`` refuses a receipt that fails the same shape checks.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile

ARM = re.compile(r"^(PASS|FAIL) (\S+)")
RESULT = re.compile(r"^RESULT: (\d+) arm\(s\), (\d+) failure\(s\)")

REQUIRED_NEW = (
    "limits-no-repo-file-is-constants",
    "limits-repo-file-is-read",
    "limits-malformed-repo-file-fails-closed",
    "limits-plan-block-tightens",
    "limits-plan-basis-mismatch-fails-closed",
    "limits-task-block-differs-refused",
    "limits-loosened-needs-limits-check",
    "limits-loosened-other-block-refused",
    "limits-round-flag-tightens",
    "limits-round-flag-loosening-refused",
    "limits-token-off-flag-against-number-refused",
    "limits-repo-off-opens-unbudgeted",
    "limits-off-loop-has-no-tokens-stop",
    "limits-off-state-says-not-budgeted",
    "limits-off-continue-tokens-refused",
    "limits-budget-of-one-opens",
    "limits-budget-of-one-still-stops",
    "limits-zero-budget-fails-closed",
    "limits-null-budget-fails-closed",
    "limits-legacy-ledger-state",
    "limits-loosened-without-run-parameters",
)


def parse(text: str) -> tuple[list[str], list[str], list[str]]:
    """Return (labels, failed labels, shape problems)."""
    labels: list[str] = []
    failed: list[str] = []
    results: list[tuple[int, int]] = []
    for line in text.splitlines():
        arm = ARM.match(line)
        if arm:
            labels.append(arm.group(2))
            if arm.group(1) == "FAIL":
                failed.append(arm.group(2))
        result = RESULT.match(line)
        if result:
            results.append((int(result.group(1)), int(result.group(2))))
    problems: list[str] = []
    if len(results) != 1:
        problems.append(f"expected one RESULT line, found {len(results)}")
    else:
        total, failures = results[0]
        if failures:
            problems.append(f"RESULT reports {failures} failure(s)")
        if total != len(labels):
            problems.append(f"RESULT says {total} arm(s) but the receipt has {len(labels)} arm line(s)")
    if failed:
        problems.append(f"FAIL arms: {failed}")
    repeated = sorted({label for label in labels if labels.count(label) > 1})
    if repeated:
        problems.append(f"repeated labels: {repeated}")
    return labels, failed, problems


def check(before_text: str, receipt_text: str) -> list[str]:
    labels, _, problems = parse(receipt_text)
    have = set(labels)
    before = [line.strip() for line in before_text.splitlines() if line.strip()]
    lost = [label for label in before if label not in have]
    if lost:
        problems.append(f"{len(lost)} prior arm(s) missing: {lost}")
    absent = [label for label in REQUIRED_NEW if label not in have]
    if absent:
        problems.append(f"{len(absent)} required new arm(s) missing: {absent}")
    print(f"arms: {len(labels)} in the receipt, {len(before)} before, {len(REQUIRED_NEW)} required new")
    return problems


def receipt(labels: list[str], fail: str | None = None, total: int | None = None, failures: int = 0) -> str:
    lines = ["[rtk] banner"]
    for label in labels:
        lines.append(f"{'FAIL' if label == fail else 'PASS'} {label:<38} OK")
    lines += ["", f"RESULT: {len(labels) if total is None else total} arm(s), {failures} failure(s) [x]"]
    return "\n".join(lines) + "\n"


def selftest() -> int:
    failures: list[str] = []
    prior = ["begin-ok", "begin-duplicate-refused"]
    after = prior + list(REQUIRED_NEW)
    before = "\n".join(prior) + "\n"
    cases = (
        ("control: every prior and new arm, 0 failures", receipt(after), True),
        ("a prior arm is missing", receipt(after[1:]), False),
        ("a required new arm is missing", receipt(after[:-1]), False),
        ("an arm says FAIL", receipt(after, fail="begin-ok", failures=1), False),
        ("RESULT reports a failure", receipt(after, failures=1), False),
        ("RESULT count disagrees with the arm lines", receipt(after, total=len(after) + 1), False),
        ("no RESULT line", "PASS begin-ok OK\n", False),
        ("a label repeats", receipt(after + ["begin-ok"]), False),
    )
    for name, text, accept in cases:
        problems = check(before, text)
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} {name}: {'accepted' if ok else problems}")
        if ok != accept:
            failures.append(name)
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "before.txt"
        if write_before(receipt(prior), out) != 0 or out.read_text(encoding="utf-8").split() != sorted(prior):
            failures.append("control: --write-before did not write the sorted labels")
        if write_before(receipt(prior, failures=1), pathlib.Path(tmp) / "bad.txt") == 0:
            failures.append("--write-before accepted a receipt with a failure")
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"selftest-arms-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def write_before(text: str, out: pathlib.Path) -> int:
    labels, _, problems = parse(text)
    if problems:
        for problem in problems:
            print("FAIL", problem)
        return 1
    out.write_text("\n".join(sorted(labels)) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {len(labels)} arm name(s) to {out}")
    return 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    if len(argv) == 3 and argv[0] == "--write-before":
        return write_before(pathlib.Path(argv[2]).read_text(encoding="utf-8", errors="replace"), pathlib.Path(argv[1]))
    if len(argv) == 3 and argv[0] == "--before":
        problems = check(
            pathlib.Path(argv[1]).read_text(encoding="utf-8"),
            pathlib.Path(argv[2]).read_text(encoding="utf-8", errors="replace"),
        )
        for problem in problems:
            print("FAIL", problem)
        print(f"selftest-arms-check: {len(problems)} problem(s)")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
