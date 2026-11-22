"""The closeout validator names a plan by the plan's own folder only (AC-164.9, D-1362).

``plan_slug`` once walked every folder of a plan path, so a dated ancestor such as a dated
TEMP folder named a loose plan, and ``--selftest`` failed its ``unslugged-plan-path-is-usage``
case whenever TEMP was dated (TOOLING-PLAN-SLUG-ANCESTOR-MATCH).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_closeout_artifacts.py"
sys.path.insert(0, str(ROOT / "tools"))

import validate_closeout_artifacts as v  # noqa: E402

SLUG = "2026-11-22-tray-show-and-baseline-fixes"


@pytest.mark.unit
def test_ac_164_9_loose_plan_under_dated_ancestor_is_usage() -> None:
    """A loose plan under a dated folder names no plan."""
    with pytest.raises(v.Usage, match="cannot derive a plan slug"):
        v.plan_slug("C:/Temp/av-kit/2026-11-22-x/tmp/closeout-selftest-ab/loose-plan.md")


@pytest.mark.unit
def test_ac_164_9_plan_path_gives_its_slug() -> None:
    """Guard: a plan file or its folder gives the folder's slug; a bare file name gives none."""
    folder = f"docs/execution/plans/{SLUG}"
    assert v.plan_slug(f"{folder}/implementation-plan.md") == SLUG
    assert v.plan_slug(folder) == SLUG
    with pytest.raises(v.Usage):
        v.plan_slug("loose-plan.md")


@pytest.mark.unit
def test_ac_164_9_selftest_under_dated_temp(tmp_path: Path) -> None:
    """The validator's own selftest passes when TEMP and TMP sit under a dated folder."""
    dated = tmp_path / "2026-11-22-dated-temp"
    dated.mkdir()
    env = {**os.environ, "TEMP": str(dated), "TMP": str(dated)}
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), "--selftest"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-2000:]
