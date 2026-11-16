"""Issue Triage — verification checks.

Checks issues for:
- Staleness: verification.last_checked > 30 days ago (or missing)
- MEU status cross-reference: linked MEUs that are completed → flag for resolution

Skips resolved issues.
"""

from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path, PurePosixPath
from typing import Any

from tools.issue_triage.model import DEFAULT_SSOT_PATH, load

# Issues older than this threshold are flagged as stale
STALE_THRESHOLD_DAYS = 30


def _is_path_like(value: object) -> bool:
    """Whether VALUE is one path-shaped token, not prose, a URL or an id (D-945)."""
    if not isinstance(value, str):
        return False
    s = value.strip()
    if not s or any(c.isspace() for c in s) or "://" in s:
        return False
    return "/" in s or "\\" in s or bool(PurePosixPath(s).suffix)


def _strip_location(s: str) -> str:
    """S without a trailing `:line` or `:line:col`; S itself when nothing else would remain.

    A drive colon (`C:\\`, `C:/`) is never followed by digits up to the end, so it stays.
    """
    stripped = re.sub(r"(?::\d+){1,2}$", "", s)
    return stripped or s


def verify_issues(
    data: dict[str, Any],
    *,
    stale_days: int = STALE_THRESHOLD_DAYS,
) -> list[dict[str, Any]]:
    """Verify all non-resolved issues.

    Returns a list of findings, each with:
      - issue_id: str
      - type: "stale" | "never_verified" | "meu_completed"
      - message: str
    """
    findings: list[dict[str, Any]] = []
    today = date.today()
    threshold = today - timedelta(days=stale_days)

    for issue in data.get("issues", []):
        # Skip resolved, candidate, and dismissed issues
        if issue.get("status") in ("resolved", "candidate", "dismissed"):
            continue

        issue_id = issue.get("id", "unknown")

        # Check verification metadata
        verification = issue.get("verification")
        if verification is None:
            findings.append(
                {
                    "issue_id": issue_id,
                    "type": "never_verified",
                    "message": f"Issue '{issue_id}' has never been verified (no verification metadata)",
                }
            )
        else:
            last_checked_str = verification.get("last_checked")
            if last_checked_str is not None:
                try:
                    last_checked = date.fromisoformat(last_checked_str)
                    if last_checked < threshold:
                        days_ago = (today - last_checked).days
                        findings.append(
                            {
                                "issue_id": issue_id,
                                "type": "stale",
                                "message": (
                                    f"Issue '{issue_id}' last verified {days_ago} days ago "
                                    f"(threshold: {stale_days}d)"
                                ),
                            }
                        )
                except ValueError:
                    findings.append(
                        {
                            "issue_id": issue_id,
                            "type": "stale",
                            "message": (
                                f"Issue '{issue_id}' has invalid verification.last_checked: "
                                f"'{last_checked_str}'"
                            ),
                        }
                    )
            else:
                findings.append(
                    {
                        "issue_id": issue_id,
                        "type": "never_verified",
                        "message": (
                            f"Issue '{issue_id}' has verification block but no last_checked date"
                        ),
                    }
                )

        # Check MEU links for completed MEUs
        meu_links = issue.get("meu_links", [])
        if meu_links:
            completed_meus = _check_meu_completion(meu_links)
            if completed_meus:
                findings.append(
                    {
                        "issue_id": issue_id,
                        "type": "meu_completed",
                        "message": (
                            f"Issue '{issue_id}' links to completed MEU(s): "
                            f"{', '.join(completed_meus)}. Consider resolving."
                        ),
                    }
                )

    return findings


def verify_all(path: Path | None = None) -> int:
    """Run verification and print results.

    Returns 0 if no findings, 1 if findings exist.
    """
    yaml_path = path or DEFAULT_SSOT_PATH
    data = load(yaml_path)
    findings = verify_issues(data)

    if not findings:
        print("OK: All issues verified -- no stale or unverified issues found.")
        return 0

    print(f"WARNING: Found {len(findings)} verification finding(s):\n")

    for finding in findings:
        icon = {
            "stale": "[STALE]",
            "never_verified": "[?]",
            "meu_completed": "[MEU-OK]",
        }.get(finding["type"], "?")
        print(f"  {icon} [{finding['type']}] {finding['message']}")

    return 1


def _check_meu_completion(meu_links: list[str]) -> list[str]:
    """Check which linked MEUs are completed.

    Best-effort: tries to import meu_status module. Returns empty list
    if the module is unavailable.
    """
    try:
        from tools.meu_status.model import COMPLETED_STATUSES, load as meu_load

        meu_data = meu_load()
        completed: list[str] = []
        for meu_id in meu_links:
            for meu in meu_data.get("meus", []):
                if meu["row_key"] == meu_id and meu["status"] in COMPLETED_STATUSES:
                    completed.append(meu_id)
                    break
        return completed
    except (ImportError, FileNotFoundError):
        return []


def verify_deep(
    data: dict[str, Any],
    *,
    project_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Deep verification of all non-resolved issues; read-only, DATA is never changed.

    Checks that a path-shaped ``resolution_path`` exists under the project root, a
    trailing ``:line`` or ``:line:col`` ignored. A value that is not path-shaped (prose,
    a URL, an id) is not checked.

    Returns a list of findings, each with:
      - issue_id: str
      - type: "file_missing"
      - message: str
      - evidence_path: str (the path checked, without its line and column)
    """
    findings: list[dict[str, Any]] = []
    root = project_root or Path.cwd()

    for issue in data.get("issues", []):
        # Skip resolved, candidate, and dismissed issues
        if issue.get("status") in ("resolved", "candidate", "dismissed"):
            continue

        issue_id = issue.get("id", "unknown")

        # Check a path-shaped resolution_path only (D-945)
        resolution_path = issue.get("resolution_path")
        if not _is_path_like(resolution_path):
            continue
        full_path = root / _strip_location(resolution_path.strip())
        try:
            exists = full_path.exists()
        except (OSError, ValueError):
            # Not a usable path on this system: report, don't crash.
            exists = False
        if not exists:
            findings.append(
                {
                    "issue_id": issue_id,
                    "type": "file_missing",
                    "message": (
                        f"Issue '{issue_id}' references file "
                        f"'{resolution_path}' which does not exist"
                    ),
                    "evidence_path": str(full_path),
                }
            )

    return findings
