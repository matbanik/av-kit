"""Review-limits survey of the live review ledgers (row 8; implementation-plan.md §Verification Plan 4).

Usage::

    python ledger-survey.py

Copies every ``C:/Temp/av-kit/review-ledger/*.json`` to ``C:/Temp/av-kit/rl/survey/review-ledger/``
(the survey copy is replaced each run), then runs ``tools/review_ledger.py state --loop-id <id>``
on each copy with ``RECEIPTS_DIR=C:/Temp/av-kit/rl/survey``. The live ledgers are only read.
There is no fixed count: whatever ``*.json`` files are there are surveyed, and at least one must be.
Exit 0 only when every ``state`` exits 0; otherwise 1 (S6: an open loop no longer loads).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
LEDGER = REPO / "tools" / "review_ledger.py"
LIVE = Path("C:/Temp/av-kit/review-ledger")
SURVEY = Path("C:/Temp/av-kit/rl/survey")


def main() -> int:
    live = sorted(LIVE.glob("*.json"))
    if not live:
        print(f"ledger-survey: no ledgers under {LIVE}; nothing to survey is a failure")
        return 1
    copies = SURVEY / "review-ledger"
    if copies.exists():
        shutil.rmtree(copies)
    copies.mkdir(parents=True)
    for src in live:
        shutil.copy2(src, copies / src.name)
    env = dict(os.environ, RECEIPTS_DIR=str(SURVEY), PYTHONIOENCODING="utf-8")
    failed = []
    pre = 0
    for src in live:
        loop_id = src.stem
        run = subprocess.run(
            [sys.executable, str(LEDGER), "state", "--loop-id", loop_id],
            capture_output=True, text=True, encoding="utf-8", env=env, cwd=REPO,
        )
        said = (run.stdout + run.stderr).strip().splitlines()
        if run.returncode != 0:
            failed.append(loop_id)
            print(f"FAIL {loop_id}: exit {run.returncode}: {said[-1] if said else '(no output)'}")
            continue
        limits = next((line.strip() for line in said if line.strip().startswith("limits:")), "limits: ?")
        pre += "pre-review-limits" in limits
        print(f"ok   {loop_id}: {limits}")
    print(f"ledger-survey: {len(live)} ledger(s), {len(live) - len(failed)} loaded, "
          f"{len(failed)} failed; {pre} pre-review-limits")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
