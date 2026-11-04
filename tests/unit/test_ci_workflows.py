"""GitHub workflow rules that a passing run can't show: pins, limits and no installer upload."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
FULL_SHA = re.compile(r"^[^@]+@[0-9a-f]{40}$")
LOCAL_NODE = (REPO_ROOT / ".node-version").read_text(encoding="utf-8").strip()


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _steps(path: Path) -> list[dict]:
    return [step for job in _load(path)["jobs"].values() for step in job["steps"]]


def _uses(path: Path) -> list[str]:
    return [step["uses"] for step in _steps(path) if "uses" in step]


def test_the_expected_workflows_exist() -> None:
    assert [path.name for path in WORKFLOWS] == ["build-windows.yml", "ci.yml", "deps-check.yml"]


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_every_action_is_pinned_to_a_full_commit(path: Path) -> None:
    uses = _uses(path)
    assert uses
    assert [action for action in uses if not FULL_SHA.match(action)] == []


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_every_job_has_a_timeout(path: Path) -> None:
    jobs = _load(path)["jobs"]
    assert [name for name, job in jobs.items() if "timeout-minutes" not in job] == []


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_the_workflow_token_starts_read_only(path: Path) -> None:
    assert _load(path)["permissions"] == {"contents": "read"}


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_checkout_keeps_no_token(path: Path) -> None:
    checkouts = [s for s in _steps(path) if s.get("uses", "").startswith("actions/checkout@")]
    assert checkouts
    assert all(s["with"]["persist-credentials"] is False for s in checkouts)


@pytest.mark.parametrize("path", WORKFLOWS, ids=lambda path: path.name)
def test_uv_version_is_pinned(path: Path) -> None:
    for step in _steps(path):
        if step.get("uses", "").startswith("astral-sh/setup-uv@"):
            assert re.fullmatch(r"\d+\.\d+\.\d+", step["with"]["version"])


def test_only_the_dependency_report_can_write_issues() -> None:
    for path in WORKFLOWS:
        for name, job in _load(path)["jobs"].items():
            permissions = job.get("permissions", {})
            expected = (path.name, name) == ("deps-check.yml", "report")
            assert (permissions.get("issues") == "write") is expected


def test_the_windows_build_uploads_and_publishes_nothing() -> None:
    """D-101: no installer holding FFmpeg leaves CI until Mat rules on its licence posture."""
    path = REPO_ROOT / ".github" / "workflows" / "build-windows.yml"
    assert [a for a in _uses(path) if "upload-artifact" in a or "release" in a] == []
    commands = "\n".join(step.get("run", "") for step in _steps(path))
    assert "--publish never" in commands
    assert "gh release" not in commands
    assert "fetch_ffmpeg" not in commands
    assert _load(path)["permissions"] == {"contents": "read"}


def test_node_and_python_pins_are_exact() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", LOCAL_NODE)
    python = (REPO_ROOT / ".python-version").read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"3\.\d+", python)
