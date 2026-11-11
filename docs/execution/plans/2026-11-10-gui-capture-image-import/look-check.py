"""Session 61 look check (task row 6; implementation-plan.md §Plan-local scripts, LOOK_LAUNCH, D-561).

Reads D-561 from the plan's §Decision Log. A ruled entry's `chosen` starts with the option
Mat picked (`"A: ...` or `"B: ...`), and its `human_message_reference` holds
`USER_EXPLICIT <date> '<words>'`; `Pending Mat's ruling` or a null reference is unruled, and
the check fails.

- Under A, `human-check.md` must hold `decision: approve`, `decision: no` or
  `decision: do-nothing`, and a `human_message_reference: USER_EXPLICIT <date> '<words>'`
  line; and `dev-app-procs.py check --record <launch record>` must exit 0 (none of this
  launch's processes left). A `no` passes this check: row 6 turns each finding into a fix row.
- Under B, `human-check.md` must hold `decision: not-run` and the same reference line quoting
  Mat's ruling, and no launch record may exist (nothing was launched).

Exit 0 only when every line above is PASS. `--selftest` runs the rules on fixture plans and
human checks with a fake process check.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

PLAN_DIR = Path("docs/execution/plans/2026-11-10-gui-capture-image-import")
RECORD = Path("C:/Temp/av-kit/s61/dev-app-launch.json")
REFERENCE = re.compile(r"^human_message_reference: USER_EXPLICIT 20\d\d-\d\d-\d\d '.+'\s*$", re.MULTILINE)


def ruling(plan_text: str, decision: str) -> tuple[str | None, str]:
    """The option letter Mat ruled for DECISION, or None, and a line that says why."""
    block = re.search(rf"^  - id: {re.escape(decision)}\n(.*?)(?=^  - id: |^```)", plan_text, re.MULTILINE | re.DOTALL)
    if block is None:
        return None, f"{decision}: no entry in the Decision Log"
    body = block.group(1)
    chosen = re.search(r'^    chosen: "(.*)"\s*$', body, re.MULTILINE)
    ref = re.search(r"^    human_message_reference: (.*)$", body, re.MULTILINE)
    if chosen is None:
        return None, f"{decision}: no chosen line"
    letter = re.match(r"([A-Z]): ", chosen.group(1))
    if letter is None:
        return None, f"{decision}: unruled (chosen is {chosen.group(1)[:40]!r})"
    if ref is None or not re.match(r"[\"']?USER_EXPLICIT 20\d\d-\d\d-\d\d '.+'", ref.group(1).strip()):
        return None, f"{decision}: chosen {letter.group(1)} without Mat's quoted words in human_message_reference"
    return letter.group(1), f"{decision}: ruled {letter.group(1)}"


def check(plan_text: str, human: str | None, record_exists: bool, procs_check: Callable[[], int]) -> list[tuple[bool, str]]:
    letter, why = ruling(plan_text, "D-561")
    lines = [(letter in ("A", "B"), why if letter in ("A", "B") or letter is None else f"D-561: unknown option {letter}")]
    if letter not in ("A", "B"):
        return lines
    if human is None:
        return [*lines, (False, "human-check.md is missing")]
    decision = re.search(r"^decision: (\S+)\s*$", human, re.MULTILINE)
    got = decision.group(1) if decision else None
    lines.append((REFERENCE.search(human) is not None, "human_message_reference quotes Mat (USER_EXPLICIT <date> '<words>')"))
    if letter == "A":
        lines.append((got in ("approve", "no", "do-nothing"), f"decision under A: {got}"))
        if not record_exists:
            lines.append((False, "no launch record: look-launch.ps1 didn't run"))
        else:
            code = procs_check()
            lines.append((code == 0, f"dev-app-procs.py check --record exit {code} (0: none of this launch's processes left)"))
    else:
        lines.append((got == "not-run", f"decision under B: {got}"))
        lines.append((not record_exists, "no launch record under B"))
    return lines


def _procs_check() -> int:
    return subprocess.run(
        [sys.executable, str(PLAN_DIR / "dev-app-procs.py"), "check", "--record", str(RECORD)], check=False
    ).returncode


def selftest() -> int:
    def plan(chosen: str, ref: str = "null") -> str:
        return (
            "```yaml\n  - id: D-560\n    chosen: \"A: x\"\n    human_message_reference: null\n"
            f"  - id: D-561\n    stage: planning\n    chosen: \"{chosen}\"\n    human_message_reference: {ref}\n"
            "  - id: D-562\n    chosen: \"y\"\n```\n"
        )

    quote = "\"USER_EXPLICIT 2026-11-10 'look first'\""
    good_ref = "human_message_reference: USER_EXPLICIT 2026-11-11 'yes, approved'\n"
    cases = [
        ("A approve, app quit", plan("A: look", quote), f"decision: approve\n{good_ref}", True, 0, True),
        ("A no passes the check", plan("A: look", quote), f"decision: no\n{good_ref}", True, 0, True),
        ("A do-nothing", plan("A: look", quote), f"decision: do-nothing\n{good_ref}", True, 0, True),
        ("B not-run", plan("B: none", quote), f"decision: not-run\n{good_ref}", False, 0, True),
        ("unruled", plan("Pending Mat's ruling. Recommended A: look"), f"decision: approve\n{good_ref}", True, 0, False),
        ("ruled without words", plan("A: look"), f"decision: approve\n{good_ref}", True, 0, False),
        ("A app still up", plan("A: look", quote), f"decision: approve\n{good_ref}", True, 1, False),
        ("A no record", plan("A: look", quote), f"decision: approve\n{good_ref}", False, 0, False),
        ("A not-run", plan("A: look", quote), f"decision: not-run\n{good_ref}", True, 0, False),
        ("A no quote", plan("A: look", quote), "decision: approve\nhuman_message_reference: null\n", True, 0, False),
        ("A paraphrase", plan("A: look", quote), "decision: approve\nhuman_message_reference: USER_EXPLICIT 2026-11-11 approved\n", True, 0, False),
        ("B approve", plan("B: none", quote), f"decision: approve\n{good_ref}", False, 0, False),
        ("B launched", plan("B: none", quote), f"decision: not-run\n{good_ref}", True, 0, False),
        ("missing file", plan("A: look", quote), None, True, 0, False),
        ("C unknown", plan("C: other", quote), f"decision: approve\n{good_ref}", True, 0, False),
    ]
    wrong = 0
    for label, plan_text, human, record, code, want in cases:
        lines = check(plan_text, human, record, lambda code=code: code)
        got = all(ok for ok, _ in lines)
        if got != want:
            wrong += 1
        print(f"{'ok' if got == want else 'WRONG'} {label}: pass={got} want={want}")
    print(f"look-check selftest: {wrong} wrong")
    return 1 if wrong else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    plan_text = (PLAN_DIR / "implementation-plan.md").read_text(encoding="utf-8")
    human_path = PLAN_DIR / "human-check.md"
    human = human_path.read_text(encoding="utf-8") if human_path.is_file() else None
    lines = check(plan_text, human, RECORD.is_file(), _procs_check)
    for ok, line in lines:
        print(f"{'PASS' if ok else 'FAIL'} {line}")
    ok = all(ok for ok, _ in lines)
    print("look-check: ok" if ok else "look-check: failed")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
