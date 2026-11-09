"""Session 56 row 5: file TTS-STATUS-PILL-BELOW-AA-CONTRAST, only if Mat chose B (D-455).

A copy of Session 58's plan-local filing script
(docs/execution/plans/2026-11-08-capture-region-import/issue-file.py), itself Session 55's, with
this issue's values and three guards that one lacks. `--expect-sha256` refuses unless the
register's bytes have that hash. `--quote` carries Mat's words for D-455's
human_message_reference and refuses an empty one. After the write, the validator's bounded
grammar reads the whole file and `issue_decision_log` reads the new issue's ids and stages, as
issue-resolve.py checks them. It copies the register first, adds the issue through
tools/issue_triage/model.py, and stops with exit 1 if any existing line was removed. Run from
the repository root; it writes only .agent/context/known-issues.yaml and the BEFORE copy under
C:/Temp/av-kit/s56.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "tools"))

import validate_closeout_artifacts as validator  # noqa: E402
from issue_triage import model  # noqa: E402

REGISTER = ROOT / ".agent/context/known-issues.yaml"
SCRATCH = Path("C:/Temp/av-kit/s56")
BEFORE = SCRATCH / "s56-ki-before-tts-pill.yaml"
ISSUE_ID = "TTS-STATUS-PILL-BELOW-AA-CONTRAST"
PLAN = "docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--expect-sha256", required=True)
    parser.add_argument("--quote", required=True, help="Mat's words choosing B, verbatim")
    args = parser.parse_args()
    quote = args.quote.strip()
    if not quote:
        print("refused: --quote is empty; D-455 needs Mat's words")
        return 1

    SCRATCH.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REGISTER, BEFORE)
    before = BEFORE.read_bytes()
    digest = hashlib.sha256(before).hexdigest()
    print("before", digest, len(before), "B")
    if digest != args.expect_sha256.lower():
        print(f"refused: the register is {digest}, not {args.expect_sha256} (S3)")
        return 1

    data = model.load(REGISTER)
    if model.get_issue(data, ISSUE_ID) is not None:
        print(f"{ISSUE_ID} is already in the register; nothing written")
        return 1
    model.add_issue(
        data,
        id=ISSUE_ID,
        title="The TTS job status pill puts its label below 4.5:1 contrast in both themes",
        severity="low",
        component="ui",
        status="open",
        discovered="2026-11-08",
        root_cause=(
            "Worked out from the token values while planning Session 56, not measured in the "
            "running app. ui/src/renderer/src/features/tts/TTSPage.tsx:721 draws the job status "
            "as text-xs text-fg on a solid fill from STATUS_COLORS "
            "(ui/src/renderer/src/features/tts/tts-controls.ts:14-21). Dark, the default theme, "
            "puts #f8f8f2 on Idle and Cancelled at 4.41:1, Failed 2.95, Pending 1.60, Generating "
            "1.30 and Done 1.29. Light puts #1e293b on Idle and Cancelled at 5.71, Done 4.44, "
            "Generating 3.97, Failed 3.03 and Pending 2.00. Session 56 (MEU-126) darkens the "
            "light accent to #155e75, which moves light Generating from 3.97 to 2.01; white on "
            "#155e75 would be 7.27. Labels are text-xs, so the 4.5:1 floor applies "
            "(C:/Temp/av-kit/s56-plan-tts-pill-dark.txt)."
        ),
        blast_radius=(
            "The TTS page's status pill only, in both themes; every status but light Idle and "
            "Cancelled is below 4.5:1. Nothing breaks and nobody has reported it. The transcript "
            "feature's STATUS_COLORS "
            "(ui/src/renderer/src/features/transcript/transcript-controls.ts:41) is exported but "
            "not rendered. Queue pills have their own tokens and floor "
            "(docs/build-plan/10-queue-card-ui.md:122)."
        ),
        verification={
            "last_checked": "2026-11-08",
            "method": (
                "WCAG 2.2 ratio of text-fg over each STATUS_COLORS fill, from the tokens in "
                "styles.css"
            ),
            "result": "10 of 12 theme and status pairs below 4.5:1",
        },
        category="TECH-DEBT",
        priority="P3",
        related=["LIGHT-ACCENT-BELOW-AA-CONTRAST", "QUEUE-PILL-TOKEN-DRIFT"],
        meu_links=[],
        notes=(
            "Found while planning Session 56 light-accent-contrast (MEU-126). Filed, not fixed: "
            "the fix (a per-status label colour, or the queue pill's tint and floor) changes the "
            "TTS page in both themes, which D-235 did not rule on."
        ),
        enrichment={
            "questions_asked": [
                "D-455: Session 56 makes light Generating's TTS pill 2.01:1. Widen the session "
                "to fix it, or keep the ruled scope and file the pill?"
            ],
            "answers": ["D-455: B, keep the scope and file the whole pill as its own issue"],
            "decided_by": "human",
            "decision_log": [
                {
                    "id": "D-455",
                    "stage": "planning",
                    "question": (
                        "Session 56's ruled light accent moves the TTS Generating pill's label "
                        "from 3.97:1 to 2.01:1, and the pill already fails 4.5:1 for most "
                        "statuses in both themes. Widen the session or keep its scope?"
                    ),
                    "resolution": "human",
                    "class": "product-preference",
                    "chosen": (
                        "B: keep MEU-126 to the two ruled light tokens and file the whole TTS "
                        "status pill as an open TECH-DEBT issue"
                    ),
                    "source_tag": "Human-approved",
                    "precedents": [
                        "ui/src/renderer/src/features/tts/TTSPage.tsx:721 — text-xs text-fg "
                        "on the STATUS_COLORS fill",
                        "C:/Temp/av-kit/s56-plan-tts-pill-dark.txt — both themes' ratios",
                        f"{PLAN} — the D-455 brief and its options",
                    ],
                    "research": {"engine": "none", "sources": []},
                    "reasoning": (
                        "The pill fails in the default dark theme for five of six statuses "
                        "before this session, so fixing Generating alone leaves the pill "
                        "failing, and fixing it whole changes the TTS page in both themes, "
                        "outside D-235's two tokens. Filing keeps the ruled scope and records "
                        "the probe. Two-way."
                    ),
                    "human_message_reference": f"USER_EXPLICIT 2026-11-08 '{quote}'",
                }
            ],
        },
    )
    model.save(data, REGISTER)
    after = REGISTER.read_bytes()
    after_digest = hashlib.sha256(after).hexdigest()
    print("after ", after_digest, len(after), "B", "CRLF", after.count(b"\r\n"))
    diff = difflib.unified_diff(
        before.decode("utf-8").splitlines(), after.decode("utf-8").splitlines(), lineterm="", n=0
    )
    changed = [ln for ln in diff if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    removed = [ln for ln in changed if ln.startswith("-")]
    print("added lines", len(changed) - len(removed), "removed lines", len(removed))
    for line in removed:
        print(line)

    problems = [f"removed: {line}" for line in removed]
    text = after.decode("utf-8")
    try:
        validator.check_yaml_subset(text, str(REGISTER))
    except validator.Refuse as exc:
        problems.append(f"bounded grammar over the whole file: {exc}")
    try:
        ids = validator.issue_decision_log(text, str(REGISTER), ISSUE_ID)
    except validator.Refuse as exc:
        problems.append(f"issue_decision_log refused: {exc}")
    else:
        if ids != [("D-455", "planning")]:
            problems.append(f"issue_decision_log read {ids}, expected D-455 at planning")
    issue = model.get_issue(model.load(REGISTER), ISSUE_ID)
    log_ids = [d["id"] for d in issue["enrichment"]["decision_log"]]
    print(ISSUE_ID, issue["status"], issue["priority"], log_ids)
    print(len(model.load(REGISTER)["issues"]), "issues")
    for problem in problems:
        print("problem:", problem)
    print(f"issue-file: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
