# ruff: noqa: E501 -- one-shot edit script; its long lines are byte-exact edit literals.
"""Plan review round 2 note (M-4 wording) and the execution approval.

Edits implementation-plan.md by bytes; refuses unless each old text occurs exactly once; keeps LF.
"""

import sys
from pathlib import Path

CR, LF, CRLF = b"\r", b"\n", b"\r\n"

HERE = Path(__file__).resolve().parent
PLAN = HERE / "implementation-plan.md"

D1369 = """  - id: D-1369
    stage: execution
    question: "How does the M-4 note describe where the E2E hook exists?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the M-4 note and the tray-start fact say the hook exists only in a launch with AVKIT_E2E=1, as the plan review's round 2 note asked; there is no separate E2E build."
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/tsb-plan-review-round-2.md — the M-4 introduction still said 'only in the E2E build'"
      - "ui/src/main/e2e-shell.ts — the E2E surface reads AVKIT_E2E at run time"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) apply the reviewer's wording; (B) do nothing and keep 'only in the E2E build'. B leaves a sentence that contradicts TRAY_E2E_HOOK. The reviewer approved with no further round, and no contract changes."
open_decisions: []
"""

PLAN_EDITS = [
    (
        "The E2E hook exists only in the E2E build.",
        "The E2E hook exists only in a launch with `AVKIT_E2E=1`; it is a main-process global, not an IPC surface (D-1369).",
    ),
    (
        "in every build, the E2E build included.",
        "in every launch, an E2E launch included.",
    ),
    (
        "is the execution approval once the Codex plan review approves and no stop item is open (precedent D-1351). "
        "Nothing commits or pushes without Mat's words.",
        "is the execution approval once the Codex plan review approves and no stop item is open (precedent D-1351). "
        "The plan review approved at round 2 of loop `tsb-plan-2026-11-22-tray-show-and-baseline-fixes` with no "
        "findings open (2026-11-22; F1 to F3 fixed), and no stop item is open, so execution is approved. Its one "
        "wording note is applied as D-1369. Nothing commits or pushes without Mat's words.",
    ),
    ("open_decisions: []\n", D1369),
]


def main() -> None:
    raw = PLAN.read_bytes()
    if b"\r" in raw:
        sys.exit("implementation-plan.md: not LF")
    text = raw.decode("utf-8")
    for old, new in PLAN_EDITS:
        n = text.count(old)
        if n != 1:
            sys.exit(f"anchor found {n} times: {old[:60]!r}")
    for old, new in PLAN_EDITS:
        text = text.replace(old, new)
    PLAN.write_bytes(text.encode("utf-8"))
    print(f"implementation-plan.md: {len(PLAN_EDITS)} edits; LF only: {CR not in text.encode()}")


main()
