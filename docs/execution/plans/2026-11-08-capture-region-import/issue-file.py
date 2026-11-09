"""Session 58 row 6: file CAPTURE-EXIF-SCANNED-ORIENTATION (D-424; implementation-plan.md §Project files).

A copy of the Session 55 plan-time filing script (C:/Temp/av-kit/s55/register_file_f1.py) with this
issue's values. It copies the register first, adds the issue through tools/issue_triage/model.py,
and stops with exit 1 if any existing line was removed. Run from the repository root; it writes
only .agent/context/known-issues.yaml and the BEFORE copy under C:/Temp/av-kit/s58.
"""

from __future__ import annotations

import difflib
import hashlib
import pathlib
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

REGISTER = ROOT / ".agent/context/known-issues.yaml"
SCRATCH = pathlib.Path("C:/Temp/av-kit/s58")
BEFORE = SCRATCH / "s58-ki-before-exif.yaml"
ISSUE_ID = "CAPTURE-EXIF-SCANNED-ORIENTATION"

SCRATCH.mkdir(parents=True, exist_ok=True)
shutil.copyfile(REGISTER, BEFORE)
before = BEFORE.read_bytes()
print("before", hashlib.sha256(before).hexdigest()[:16], len(before))

data = model.load(REGISTER)
if model.get_issue(data, ISSUE_ID) is not None:
    print(f"{ISSUE_ID} is already in the register; nothing written")
    sys.exit(1)
model.add_issue(
    data,
    id=ISSUE_ID,
    title="A scanned JPEG or WebP with EXIF orientation 5 to 8 is sized and marked sideways",
    severity="medium",
    component="infrastructure",
    status="open",
    discovered="2026-11-08",
    root_cause=(
        "The capture adapter's probe reads image.size after Image.open without applying the EXIF "
        "orientation (packages/infrastructure/src/avkit_infra/capture/adapter.py:253-263 at "
        "2963efe), and bake and the region view open the stored pixels the same way. A JPEG or "
        "WebP that the inbox scan registers with orientation 5, 6, 7 or 8 is therefore recorded "
        "at its stored width and height, while Chromium, which honours the tag, shows the turned "
        "frame. Plan-time probe on Pillow 13.0.0: a 400x300 file tagged 5 to 8 probes 400x300, "
        "and ImageOps.exif_transpose gives 300x400 (C:/Temp/av-kit/s58-plan-exif-probe.txt)."
    ),
    blast_radius=(
        "Read from the probe; the GUI was not run. Only files that reach the inbox by the scan or "
        "by register mode with a turning tag (phone and camera photos, mostly). For those, the "
        "row's width and height are swapped against what the GUI shows, marks drawn in the GUI "
        "land in the stored frame, and a region asked in the shown frame is clamped or refused. "
        "Screenshots carry no tag. MEU-129's import mode avoids it by writing an upright PNG "
        "(D-417), so this issue covers the scan and register paths only."
    ),
    verification={
        "last_checked": "2026-11-08",
        "method": "Pillow probe of orientations 1 to 8 against the adapter's probe",
        "result": "orientations 5 to 8 differ: probe 400x300, exif_transpose 300x400",
    },
    category="TECH-DEBT",
    priority="P3",
    related=[],
    meu_links=["MEU-129"],
    notes=(
        "Found while planning Session 58 capture-region-import (MEU-129 import). Filed, not fixed: "
        "the fix (transpose at scan and register, or record the shown frame) changes rows already "
        "stored and wants its own plan."
    ),
    enrichment={
        "questions_asked": [],
        "answers": [],
        "decided_by": "agent",
        "decision_log": [
            {
                "id": "D-424",
                "stage": "planning",
                "question": (
                    "The import design turns EXIF-oriented images upright, but scanned and "
                    "registered files keep their stored frame. Fix the scan path in Session 58, "
                    "file it, or leave it?"
                ),
                "resolution": "autonomous",
                "class": "two-way",
                "chosen": (
                    "File it as an open TECH-DEBT issue linked to MEU-129 and fix only the import "
                    "path in Session 58"
                ),
                "source_tag": "Local Canon",
                "precedents": [
                    "packages/infrastructure/src/avkit_infra/capture/adapter.py:253-263 — probe reads the stored size",
                    "docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md — D-417 upright PNG",
                    "AGENTS.md — out-of-scope findings go to the known-issues register",
                ],
                "research": {"engine": "none", "sources": []},
                "reasoning": (
                    "Changing the scan path rewrites the frame of rows already stored, which the "
                    "MEU-128 and MEU-129 ACs do not cover. Leaving it unrecorded hides a defect the "
                    "plan found. Filing keeps the session's scope and records the probe. Two-way."
                ),
            }
        ],
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
