"""Session 84 selftest arm check (task rows 0 and 6; implementation-plan.md AC-11).

Usage::

    python selftest-arms-check.py --write-before OUT RECEIPT   # row 0: record today's arms
    python selftest-arms-check.py --before BEFORE RECEIPT      # row 6 and the gate
    python selftest-arms-check.py --selftest

``RECEIPT`` is a ``tools/validate_closeout_artifacts.py --selftest`` receipt. Its arm lines are
``  ok   <label> want=<code>/<NAME> got=...`` or ``  FAIL <label> ...`` and it ends with
``RESULT: N arm(s), F failure(s) [M must-OK arms, ...]``. ``BEFORE`` holds one
``<label> <want>`` line per arm, sorted.

The check accepts only when the receipt has one ``RESULT`` line, F is 0, no arm line says
``FAIL``, the number of arm lines equals N, and no label repeats. Then, against ``BEFORE``:

- every label in ``REMOVED`` (upstream ``a73d6df``'s removed arms, the reflection
  comparison) is gone;
- every other label in ``BEFORE`` is still present; its ``want`` is unchanged, except the
  labels in ``FLIPPED``, which must now want ``0/OK`` (the plan's §Selftest arm changes);
- every label in ``ADDED`` is present with the ``want`` given there (upstream ``a73d6df``'s
  new arms, ``ec3857a``'s three repository-boundary arms, the six av-kit arms added
  after plan review R1 for CRO-P1 and CRO-P2, and the five added after the R1 recheck for
  CRO-R1-1).

This replaces the peer's "a selftest must not shrink" rule with an exact list: the removal
is the ruling of D-826, so each arm that goes is named here and nowhere else.
``--write-before`` refuses a receipt that fails the shape checks.
"""

from __future__ import annotations

import pathlib
import re
import sys
import tempfile

ARM = re.compile(r"^\s+(ok|FAIL)\s+(\S+)(?:\s+want=(\S+))?")
RESULT = re.compile(r"^RESULT: (\d+) arm\(s\), (\d+) failure\(s\)")

REMOVED = (
    "decision-blank-reasoning-refused",
    "decision-duplicate-id-refused",
    "decision-indented-fence-reconciled",
    "decision-indented-root-reconciled",
    "decision-invalid-resolution-refused",
    "decision-issue-indented-4-missing-refused",
    "decision-issue-missing-from-reflection-refused",
    "decision-missing-from-reflection-refused",
    "decision-stage-before-id-refused",
    "decision-stage-mismatch-refused",
    "decision-two-column-table-refused",
    "grouping-decision-missing-refused",
    "grouping-fenced-heading-declared-unreconciled-refused",
    "handoff-indented-root-reconciled",
)

FLIPPED = (
    "decision-log-inline-comment-read",
    "decision-quoted-root-key-read",
    "decision-tilde-yaml-fence-read",
    "enrichment-inline-comment-read",
    "issues-inline-comment-read",
    "grouping-any-filename-read",
    "grouping-declared-basename-beside-plan-read",
    "grouping-declared-root-resolved-read",
    "grouping-fenced-example-before-real-section-read",
    "grouping-tilde-fenced-example-before-real-section-read",
    "grouping-named-handoff-read-as-handoff",
    "grouping-named-plan-read-as-plan",
    "grouping-plan-source-null-read-as-grouping",
    "plan-commented-heading-read-as-plan",
    "plan-fenced-heading-read-as-plan",
    "plan-tilde-fenced-heading-read-as-plan",
)

ADDED = {
    "decision-blank-reasoning-in-log-refused": "1/REFUSE",
    "decision-block-scalar-reasoning-ok": "0/OK",
    "decision-indented-fence-read": "0/OK",
    "decision-indented-root-read": "0/OK",
    "decision-non-text-chosen-refused": "1/REFUSE",
    "decision-pending-chosen-refused": "1/REFUSE",
    "decision-stage-before-id-read": "0/OK",
    "grouping-decisions-read": "0/OK",
    "grouping-fenced-heading-declared-read": "0/OK",
    "handoff-indented-root-read": "0/OK",
    "reflection-decisions-log-example-refused": "1/REFUSE",
    "reflection-decisions-log-link-list-ok": "0/OK",
    "grouping-declared-repo-boundary-read": "0/OK",
    "grouping-declared-repo-boundary-gitfile-read": "0/OK",
    "grouping-declared-repo-boundary-outer-decoy-refused": "1/REFUSE",
    # amended after plan review R1: CRO-P1 (D-831) and CRO-P2 (D-829)
    "decision-commented-pending-chosen-refused": "1/REFUSE",
    "decision-commented-empty-chosen-refused": "1/REFUSE",
    "decision-quoted-hash-text-ok": "0/OK",
    "grouping-blank-chosen-refused": "1/REFUSE",
    "grouping-pending-chosen-refused": "1/REFUSE",
    "grouping-open-row-read": "0/OK",
    # amended after the R1 recheck: CRO-R1-1 (D-831), a double-quoted value's YAML escapes
    "decision-escaped-newline-reasoning-refused": "1/REFUSE",
    "decision-escaped-pending-chosen-refused": "1/REFUSE",
    "decision-escaped-blank-question-refused": "1/REFUSE",
    "decision-escaped-blank-chosen-refused": "1/REFUSE",
    "decision-escaped-text-ok": "0/OK",
}


def parse(text: str) -> tuple[dict[str, str], list[str]]:
    """Return ({label: want}, shape problems)."""
    arms: dict[str, str] = {}
    labels: list[str] = []
    failed: list[str] = []
    results: list[tuple[int, int]] = []
    for line in text.splitlines():
        arm = ARM.match(line)
        if arm:
            labels.append(arm.group(2))
            arms[arm.group(2)] = arm.group(3) or "?"
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
    missing_want = sorted(label for label, want in arms.items() if want == "?")
    if missing_want:
        problems.append(f"arm lines without want=: {missing_want}")
    return arms, problems


def read_before(text: str) -> dict[str, str]:
    before: dict[str, str] = {}
    for line in text.splitlines():
        if line.strip():
            label, want = line.split()
            before[label] = want
    return before


def check(before_text: str, receipt_text: str) -> list[str]:
    after, problems = parse(receipt_text)
    before = read_before(before_text)
    kept = [label for label in REMOVED if label in after]
    if kept:
        problems.append(f"{len(kept)} removed arm(s) still present: {kept}")
    unknown_removed = [label for label in REMOVED if label not in before]
    if unknown_removed:
        problems.append(f"REMOVED names arm(s) the base selftest lacks: {unknown_removed}")
    for label, want in before.items():
        if label in REMOVED:
            continue
        if label not in after:
            problems.append(f"prior arm missing: {label}")
            continue
        expected = "0/OK" if label in FLIPPED else want
        if after[label] != expected:
            problems.append(f"{label} wants {after[label]}, expected {expected}")
    unknown_flipped = [label for label in FLIPPED if label not in before]
    if unknown_flipped:
        problems.append(f"FLIPPED names arm(s) the base selftest lacks: {unknown_flipped}")
    for label, want in ADDED.items():
        if label not in after:
            problems.append(f"added arm missing: {label}")
        elif after[label] != want:
            problems.append(f"added arm {label} wants {after[label]}, expected {want}")
    extra = sorted(set(after) - set(before) - set(ADDED))
    if extra:
        problems.append(f"arm(s) neither in the base nor in ADDED: {extra}")
    must_ok = sum(1 for want in after.values() if want == "0/OK")
    print(
        f"arms: {len(after)} in the receipt ({must_ok} want 0/OK), {len(before)} before, "
        f"{len(REMOVED)} removed, {len(FLIPPED)} flipped, {len(ADDED)} added"
    )
    return problems


def receipt(arms: dict[str, str], fail: str | None = None, total: int | None = None, failures: int = 0) -> str:
    lines = ["[rtk] banner"]
    for label, want in arms.items():
        state = "FAIL" if label == fail else "ok  "
        lines.append(f"  {state} {label} want={want} got={want}")
    lines += ["", f"RESULT: {len(arms) if total is None else total} arm(s), {failures} failure(s) [x]"]
    return "\n".join(lines) + "\n"


def selftest() -> int:
    failures: list[str] = []
    prior = {"reflection-ok": "0/OK", "no-artifact-is-usage": "2/USAGE"}
    prior.update({label: "1/REFUSE" for label in REMOVED})
    prior.update({label: "1/REFUSE" for label in FLIPPED})
    before = "".join(f"{label} {want}\n" for label, want in sorted(prior.items()))
    after = {label: want for label, want in prior.items() if label not in REMOVED}
    after.update({label: "0/OK" for label in FLIPPED})
    after.update(ADDED)

    def without(label: str) -> dict[str, str]:
        return {k: v for k, v in after.items() if k != label}

    cases = (
        ("control: removed gone, flipped OK, added present, 0 failures", receipt(after), True),
        ("a removed arm is still present", receipt({**after, REMOVED[0]: "1/REFUSE"}), False),
        ("a kept prior arm is missing", receipt(without("reflection-ok")), False),
        ("a kept prior arm changed its want", receipt({**after, "no-artifact-is-usage": "1/REFUSE"}), False),
        ("a flipped arm still wants REFUSE", receipt({**after, FLIPPED[0]: "1/REFUSE"}), False),
        ("an added arm is missing", receipt(without("grouping-declared-repo-boundary-read")), False),
        ("an added arm has the wrong want", receipt({**after, "decision-pending-chosen-refused": "0/OK"}), False),
        ("an unlisted new arm", receipt({**after, "surprise-ok": "0/OK"}), False),
        ("an arm says FAIL", receipt(after, fail="reflection-ok", failures=1), False),
        ("RESULT reports a failure", receipt(after, failures=1), False),
        ("RESULT count disagrees with the arm lines", receipt(after, total=len(after) + 1), False),
        ("no RESULT line", "  ok   reflection-ok want=0/OK got=0/OK\n", False),
    )
    for name, text, accept in cases:
        problems = check(before, text)
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} {name}: {'accepted' if ok else problems[:2]}")
        if ok != accept:
            failures.append(name)
    with tempfile.TemporaryDirectory(dir="C:/Temp/av-kit") as tmp:
        out = pathlib.Path(tmp) / "before.txt"
        if write_before(receipt(prior), out) != 0 or out.read_text(encoding="utf-8") != before:
            failures.append("control: --write-before did not write the sorted label and want lines")
        if write_before(receipt(prior, failures=1), pathlib.Path(tmp) / "bad.txt") == 0:
            failures.append("--write-before accepted a receipt with a failure")
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"selftest-arms-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def write_before(text: str, out: pathlib.Path) -> int:
    arms, problems = parse(text)
    if problems:
        for problem in problems:
            print("FAIL", problem)
        return 1
    out.write_text("".join(f"{label} {want}\n" for label, want in sorted(arms.items())), encoding="utf-8", newline="\n")
    print(f"wrote {len(arms)} arm(s) to {out}")
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
