# ruff: noqa: E501 -- one-shot edit script; its long lines are byte-exact edit literals.
"""Record execution decision D-1370 (the baseline's free-id range-end filter) in the plan YAML.

A byte edit on the LF plan file: the new decision goes just before ``open_decisions: []``, which
must occur once, or nothing is written.
"""

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE / "implementation-plan.md"
ANCHOR = "open_decisions: []\n"
D1370 = """  - id: D-1370
    stage: execution
    question: "Does a D-1365..D-1399 match that only closes another session's claimed range count as a use in the row-0 free-id check?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a match preceded by 'to ' or '..' is the upper end of another session's claimed range and is printed as a range end, not a use; every other match outside this session's files stays S2."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-21-transcript-job-resume-session-grouping.md:12 and :85 — 'claims D-1350 to D-1399', 'D-1352 to D-1399'"
      - "docs/execution/plans/2026-11-21-transcript-job-resume/ (baseline.ps1, implementation-plan.md, task.md) — 'D-1358 to D-1399', Session 101's range statement"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) skip only range-end matches; (B) list each Session 101 line as an exception; (C) count every match, so row 0 fails on text that uses no id. B breaks on the next session that states a range; C blocks a sound baseline. A still catches any real use, including one on the same line as a range end, since a line counts as a use whenever it holds more matches than range ends."
"""

text = PLAN.read_bytes().decode("utf-8")
problems = []
if "\r" in text:
    problems.append("implementation-plan.md has CR; expected LF")
if text.count(ANCHOR) != 1:
    problems.append(f"anchor found {text.count(ANCHOR)} time(s)")
if "id: D-1370" in text:
    problems.append("D-1370 already recorded")
for p in problems:
    print("PROBLEM:", p)
if problems:
    sys.exit(1)
text = text.replace(ANCHOR, D1370 + ANCHOR, 1)
PLAN.write_bytes(text.encode("utf-8"))
print("implementation-plan.md: D-1370 recorded; LF only:", "\r" not in text)
