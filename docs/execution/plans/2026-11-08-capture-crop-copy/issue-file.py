"""Session 59 row 6: file MCP-AUDIT-BASELINE-PENDING-CROP (D-499 A; implementation-plan.md §Plan-local scripts).

A copy of Session 58's issue-file.py with this issue's values. It runs only under D-499 A: it
first reads the D-499 section of human-gate-decision.md and stops with exit 2 unless a
"**Mat's ruling" line there accepts A. It copies the register first, adds the issue through
tools/issue_triage/model.py, and stops with exit 1 if any existing line was removed. Run from
the repository root; it writes only .agent/context/known-issues.yaml and the BEFORE copy under
C:/Temp/av-kit/s59.

``--probe REGISTER_COPY`` is the plan-time dry run: it skips the ruling check, records D-499 as
still pending, writes the issue into REGISTER_COPY instead of the register, and keeps its BEFORE
copy beside it.
"""

from __future__ import annotations

import difflib
import hashlib
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, check=True, text=True
    ).stdout.strip()
)
sys.path.insert(0, str(ROOT / "tools"))

from issue_triage import model  # noqa: E402

PLAN = ROOT / "docs/execution/plans/2026-11-08-capture-crop-copy"
ISSUE_ID = "MCP-AUDIT-BASELINE-PENDING-CROP"

probe = sys.argv[1:2] == ["--probe"]
if probe:
    if len(sys.argv) != 3:
        print("usage: issue-file.py [--probe REGISTER_COPY]")
        sys.exit(2)
    REGISTER = pathlib.Path(sys.argv[2])
    SCRATCH = REGISTER.parent
    BEFORE = SCRATCH / "s59-ki-before-baseline-probe.yaml"
    chosen = "Pending Mat: A recommended (BASELINE_PENDING in coverage.test.ts and a filed issue)"
    message = None
else:
    REGISTER = ROOT / ".agent/context/known-issues.yaml"
    SCRATCH = pathlib.Path("C:/Temp/av-kit/s59")
    BEFORE = SCRATCH / "s59-ki-before-baseline.yaml"
    text = (PLAN / "human-gate-decision.md").read_text(encoding="utf-8")
    section = re.search(r"^## D-499\b.*?(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    rulings = [
        ln for ln in (section.group(0).splitlines() if section else []) if ln.startswith("**Mat's ruling")
    ]
    accepts_a = bool(rulings) and re.search(r"as recommended|option A\b", rulings[-1]) is not None
    if not accepts_a or re.search(r"option [BCD]\b", rulings[-1]):
        print("D-499 is not ruled A in human-gate-decision.md; this script runs only under A")
        for ln in rulings:
            print(ln)
        sys.exit(2)
    message = rulings[-1]
    chosen = (
        "A: BASELINE_PENDING = ['avkit_capture.crop'] in mcp-server/tests/audit/coverage.test.ts, "
        "AC-68.5's committed-baseline clause amended, and this issue filed"
    )
    print("D-499 ruling:", message)

SCRATCH.mkdir(parents=True, exist_ok=True)
shutil.copyfile(REGISTER, BEFORE)
before = BEFORE.read_bytes()
print("before", hashlib.sha256(before).hexdigest()[:16], len(before))

data = model.load(REGISTER)
if model.get_issue(data, ISSUE_ID) is not None:
    print(f"{ISSUE_ID} is already in the register; nothing written")
    sys.exit(1)
if model.get_issue(data, "YOUTUBE-CAPTIONS-IP-BLOCK") is None:
    print("YOUTUBE-CAPTIONS-IP-BLOCK is not in the register; the link would dangle")
    sys.exit(1)
decision = {
    "id": "D-499",
    "stage": "planning",
    "question": "How does the MCP audit baseline meet the new crop action?",
    "resolution": "human",
    "class": "governance-value",
    "chosen": chosen,
    "source_tag": "Human",
    "precedents": [
        "mcp-server/tests/audit/coverage.test.ts:78-85 — AC-68.5 at 8bcb4a6",
        ".agent/skills/mcp-tool-audit/SKILL.md:45-51 — BASELINE_UPDATE_RULE and BASELINE_ANNOTATION_RULE",
        ".agent/context/known-issues.yaml — YOUTUBE-CAPTIONS-IP-BLOCK, open; do not refresh the audit baseline to hide it",
        "docs/execution/plans/2026-10-02-capture-flatten-backup/implementation-plan.md:200 — D-20, a gate-only tolerance",
    ],
    "research": {
        "engine": "exa",
        "sources": [
            "https://contribute.qt-project.org/quips/24/",
            "https://handbook.gitlab.com/handbook/engineering/testing/quarantine-process/",
            "https://www.rad-ui.com/docs/contributing/flaky-test-quarantine",
            "https://sysroot.io/blog/flaky-tests-quarantine-strategy-ci-cd-reliability",
        ],
    },
    "reasoning": (
        "The baseline is a governed snapshot that only an authoritative run updates, and that run "
        "is blocked while the caption block holds. Naming the one gap in the test and here keeps "
        "main green and tells the next release audit what to accept. Two-way."
    ),
}
if message is not None:
    decision["human_message_reference"] = message
model.add_issue(
    data,
    id=ISSUE_ID,
    title="The committed MCP audit baseline has no avkit_capture.crop entry",
    severity="low",
    component="mcp-server",
    status="open",
    discovered="2026-11-08",
    root_cause=(
        "MEU-130 adds avkit_capture.crop to ACTION_INDEX. The committed baseline "
        "(.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json, authoritative, recorded "
        "at ddd1117 on 2026-10-16) can only gain an entry from an authoritative --update-baseline "
        "run, and BASELINE_UPDATE_RULE refuses that run while YOUTUBE-CAPTIONS-IP-BLOCK makes the "
        "transcript actions REGRESSION. Hand-adding the entry is forbidden by "
        "BASELINE_ANNOTATION_RULE."
    ),
    blast_radius=(
        "The audit coverage test (mcp-server/tests/audit/coverage.test.ts, AC-68.5) accepts the "
        "baseline missing exactly the keys in BASELINE_PENDING, which holds only "
        "avkit_capture.crop. Every other key still has to match, so a second missing action still "
        "fails. The next release audit reports avkit_capture.crop as NEW, and that audit's rule "
        "has to accept it."
    ),
    verification={
        "last_checked": "2026-11-08",
        "method": "coverage.test.ts AC-68.5 and AC-130.28 at the Session 59 gate",
        "result": "the baseline misses only avkit_capture.crop and has no extra key",
    },
    category="TECH-DEBT",
    priority="P3",
    related=["YOUTUBE-CAPTIONS-IP-BLOCK"],
    meu_links=["MEU-130"],
    notes=(
        "Filed by Session 59 capture-crop-copy under D-499 A. Closed by the next authoritative "
        "baseline update, which records avkit_capture.crop and empties BASELINE_PENDING in the "
        "same change; AC-130.28 fails once the baseline holds a pending key, so the list can't "
        "outlive its reason. The next release audit is where avkit_capture.crop is accepted as NEW."
    ),
    enrichment={
        "questions_asked": [],
        "answers": [],
        "decided_by": "human",
        "decision_log": [decision],
    },
)
model.save(data, REGISTER)
after = REGISTER.read_bytes()
print("after ", hashlib.sha256(after).hexdigest()[:16], len(after), "CRLF", after.count(b"\r\n"))
diff = list(
    difflib.unified_diff(
        before.decode("utf-8").splitlines(), after.decode("utf-8").splitlines(), lineterm="", n=0
    )
)
changed = [line for line in diff if line[:1] in "+-" and not line.startswith(("+++", "---"))]
removed = [line for line in changed if line.startswith("-")]
print("added lines", len(changed) - len(removed), "removed lines", len(removed))
for line in removed:
    print(line)
issue = model.get_issue(model.load(REGISTER), ISSUE_ID)
print(ISSUE_ID, issue["status"], issue["priority"], [d["id"] for d in issue["enrichment"]["decision_log"]])
print(len(model.load(REGISTER)["issues"]), "issues")
sys.exit(1 if removed else 0)
