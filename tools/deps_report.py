#!/usr/bin/env python3
"""Weekly dependency report: run the read-only scanners and write one Markdown file.

Findings do not fail the run; they are what the report is for. A scanner that fails is
shown as failed and makes the exit code 1, so a broken scanner never reads as "0 findings".
Standard library only, so the workflow needs no `uv sync`.

Usage:
    python tools/deps_report.py --out report.md [--run-url URL]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NPM_ROOTS = ("ui", "mcp-server")
# Dev dependencies that still reach users. `npm audit --omit=dev` cannot see these.
SHIPPED_DEV_DEPENDENCIES = {"electron"}
FFMPEG_SCRIPT = Path("tools/fetch_ffmpeg_windows.ps1")
FFMPEG_URL_PATTERN = re.compile(r"https://github\.com/BtbN/[^'\"\s]+")
SEVERITY_ORDER = ("critical", "high", "moderate", "low", "info")
# GitHub refuses an issue body over 65,536 characters.
MAX_BODY_CHARS = 60_000
COMMAND_TIMEOUT_SECONDS = 600

Runner = Callable[[list[str], Path], "tuple[int, str, str]"]
UrlProbe = Callable[[str], int]


class ScannerError(Exception):
    """A scanner did not produce a result this report can trust."""


def _load_object(stdout: str) -> dict:
    """Parse a scanner's JSON output, which must be one object."""
    try:
        data = json.loads(stdout)
    except ValueError as exc:
        raise ScannerError(f"output is not JSON: {stdout[:120]!r}") from exc
    if not isinstance(data, dict):
        raise ScannerError("output is not a JSON object")
    return data


def _version_key(version: str) -> list[tuple[int, int, str]]:
    """Sort version strings numerically where they are numeric."""
    parts = re.findall(r"\d+|[^\d.]+", version)
    return [(1, int(part), "") if part.isdigit() else (0, 0, part) for part in parts]


def parse_uv_audit(stdout: str) -> dict:
    """Return audited count and one row per vulnerable Python package."""
    data = _load_object(stdout)
    summary = data.get("summary")
    vulnerabilities = data.get("vulnerabilities")
    if not isinstance(summary, dict) or not isinstance(vulnerabilities, list):
        raise ScannerError("uv audit output has no summary or vulnerabilities")
    audited = summary.get("audited_packages")
    if not isinstance(audited, int) or audited <= 0:
        raise ScannerError(f"uv audit checked no packages: {audited!r}")
    if summary.get("vulnerabilities") != len(vulnerabilities):
        raise ScannerError("uv audit summary disagrees with its list")
    rows: dict[str, dict] = {}
    for item in vulnerabilities:
        try:
            name = item["dependency"]["name"]
            version = item["dependency"]["version"]
            fixes = item["fix_versions"]
        except (KeyError, TypeError) as exc:
            raise ScannerError(f"uv audit item has an unknown shape: {exc!r}") from exc
        row = rows.setdefault(
            name, {"name": name, "version": version, "count": 0, "unfixed": 0, "fixes": set()}
        )
        row["count"] += 1
        if fixes:
            row["fixes"].update(fixes)
        else:
            row["unfixed"] += 1
    return {
        "audited": audited,
        "total": len(vulnerabilities),
        "rows": sorted(rows.values(), key=lambda row: (-row["count"], row["name"])),
    }


def parse_npm_audit(stdout: str) -> dict:
    """Return severity counts and the package map from `npm audit --json`."""
    data = _load_object(stdout)
    metadata = data.get("metadata")
    counts = metadata.get("vulnerabilities") if isinstance(metadata, dict) else None
    packages = data.get("vulnerabilities")
    if (
        "error" in data
        or not isinstance(counts, dict)
        or not isinstance(counts.get("total"), int)
        or not isinstance(packages, dict)
    ):
        message = data.get("message") or data.get("error") or "no vulnerability counts"
        raise ScannerError(f"npm audit failed: {str(message)[:200]}")
    return {"counts": counts, "packages": packages}


def shipped_rows(shipped: dict, full: dict) -> list[dict]:
    """Rows for what reaches users: production packages plus shipped dev dependencies."""
    packages = dict(shipped["packages"])
    for name in SHIPPED_DEV_DEPENDENCIES:
        if name in full["packages"]:
            packages[name] = full["packages"][name]
    rows = [
        {
            "name": name,
            "severity": entry.get("severity", "unknown"),
            "range": entry.get("range", "?"),
            "fix": _render_npm_fix(entry.get("fixAvailable")),
        }
        for name, entry in packages.items()
    ]
    return sorted(rows, key=lambda row: (_severity_rank(row["severity"]), row["name"]))


def _severity_rank(severity: str) -> int:
    return SEVERITY_ORDER.index(severity) if severity in SEVERITY_ORDER else len(SEVERITY_ORDER)


def _render_npm_fix(fix: object) -> str:
    if isinstance(fix, dict):
        major = " (major)" if fix.get("isSemVerMajor") else ""
        return f"{fix.get('name')} {fix.get('version')}{major}"
    return "yes" if fix else "no"


def parse_npm_outdated(stdout: str) -> list[dict]:
    """Return one row per outdated direct dependency, majors first."""
    data = _load_object(stdout) if stdout.strip() else {}
    if "error" in data:
        raise ScannerError(f"npm outdated failed: {str(data['error'])[:200]}")
    rows = []
    for name, entry in data.items():
        if not isinstance(entry, dict) or "current" not in entry or "latest" not in entry:
            raise ScannerError(f"npm outdated could not read the installed {name}")
        rows.append(
            {
                "name": name,
                "current": entry["current"],
                "latest": entry["latest"],
                "major": entry["current"].split(".")[0] != entry["latest"].split(".")[0],
            }
        )
    return sorted(rows, key=lambda row: (not row["major"], row["name"]))


def parse_uv_upgrade(output: str) -> list[str]:
    """Return the lines `uv lock --upgrade --dry-run` would change."""
    if not re.search(r"^Resolved \d+ packages", output, re.MULTILINE):
        raise ScannerError(f"uv lock did not resolve: {output.strip()[-200:]!r}")
    return re.findall(r"^(?:Update|Add|Remove) .+$", output, re.MULTILINE)


def find_ffmpeg_url(script_text: str) -> str:
    """Return the one pinned FFmpeg URL in the fetch script."""
    urls = set(FFMPEG_URL_PATTERN.findall(script_text))
    if len(urls) != 1:
        raise ScannerError(f"expected one pinned FFmpeg URL, found {len(urls)}")
    return urls.pop()


def probe_url(url: str) -> int:
    """Return the HTTP status of a HEAD request, following redirects."""
    request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            return int(response.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def run_command(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run a scanner and capture its output. `which` resolves npm.cmd on Windows."""
    executable = shutil.which(args[0])
    if executable is None:
        raise ScannerError(f"{args[0]} is not installed")
    done = subprocess.run(
        [executable, *args[1:]],
        cwd=cwd,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=COMMAND_TIMEOUT_SECONDS,
        check=False,
    )
    return done.returncode, done.stdout, done.stderr


@dataclass
class Report:
    """Scanner results, in the order they ran."""

    status: list[tuple[str, str]] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    sections: list[str] = field(default_factory=list)
    details: list[str] = field(default_factory=list)

    def ok(self, scanner: str, note: str) -> None:
        self.status.append((scanner, f"ok: {note}"))

    def fail(self, scanner: str, reason: str) -> None:
        self.failed.append(scanner)
        self.status.append((scanner, f"**FAILED**: {_cell(reason)}"))


def _cell(text: object) -> str:
    """Keep a value on one table row."""
    return " ".join(str(text).split()).replace("|", "\\|")


def _table(headers: tuple[str, ...], rows: list[tuple[object, ...]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(_cell(value) for value in row) + " |" for row in rows]
    return "\n".join(lines)


def _details(summary: str, body: str) -> str:
    return f"<details><summary>{summary}</summary>\n\n{body}\n\n</details>"


def _scan_python_audit(report: Report, run: Runner, root: Path) -> None:
    scanner = "uv audit"
    try:
        code, stdout, stderr = run(["uv", "audit", "--locked", "--output-format", "json"], root)
        if code not in (0, 1):
            raise ScannerError(f"exit {code}: {stderr.strip()[-200:]}")
        result = parse_uv_audit(stdout)
    except (ScannerError, OSError, subprocess.SubprocessError) as exc:
        report.fail(scanner, str(exc))
        return
    report.ok(scanner, f"{result['total']} advisories, {result['audited']} packages audited")
    if result["rows"]:
        rows = [
            (
                row["name"],
                row["version"],
                row["count"],
                row["unfixed"],
                max(row["fixes"], key=_version_key) if row["fixes"] else "none",
            )
            for row in result["rows"]
        ]
        headers = ("Package", "Locked", "Advisories", "No fix yet", "Newest fix")
        report.sections.append("### Python (`uv.lock`)\n\n" + _table(headers, rows))


def _scan_npm_audit(report: Report, run: Runner, root: Path, npm_root: str) -> None:
    scanner = f"npm audit ({npm_root})"
    try:
        _, full_out, _ = run(["npm", "audit", "--json"], root / npm_root)
        _, shipped_out, _ = run(["npm", "audit", "--omit=dev", "--json"], root / npm_root)
        full = parse_npm_audit(full_out)
        shipped = parse_npm_audit(shipped_out)
    except (ScannerError, OSError, subprocess.SubprocessError) as exc:
        report.fail(scanner, str(exc))
        return
    rows = shipped_rows(shipped, full)
    report.ok(scanner, f"{len(rows)} shipped, {full['counts']['total']} including dev tools")
    text = f"### npm: `{npm_root}`, what ships\n\n"
    if rows:
        table_rows = [(r["name"], r["severity"], r["range"], r["fix"]) for r in rows]
        text += _table(("Package", "Severity", "Affected", "Fix"), table_rows)
    else:
        text += "None."
    counts = full["counts"]
    summary = ", ".join(f"{counts.get(level, 0)} {level}" for level in SEVERITY_ORDER)
    report.sections.append(f"{text}\n\nAll packages including dev tools: {summary}.")


def _scan_npm_outdated(report: Report, run: Runner, root: Path, npm_root: str) -> None:
    scanner = f"npm outdated ({npm_root})"
    try:
        # A clean CI checkout installs; a dev checkout keeps its Electron binary.
        if not (root / npm_root / "node_modules").is_dir():
            code, _, stderr = run(["npm", "ci", "--ignore-scripts"], root / npm_root)
            if code != 0:
                raise ScannerError(f"npm ci exit {code}: {stderr.strip()[-200:]}")
        _, stdout, _ = run(["npm", "outdated", "--json"], root / npm_root)
        rows = parse_npm_outdated(stdout)
    except (ScannerError, OSError, subprocess.SubprocessError) as exc:
        report.fail(scanner, str(exc))
        return
    majors = sum(row["major"] for row in rows)
    report.ok(scanner, f"{len(rows)} outdated, {majors} across a major version")
    if rows:
        table_rows = [
            (r["name"], r["current"], r["latest"], "yes" if r["major"] else "") for r in rows
        ]
        body = _table(("Package", "Installed", "Latest", "Major"), table_rows)
        report.details.append(_details(f"npm updates: {npm_root} ({len(rows)})", body))


def _scan_python_updates(report: Report, run: Runner, root: Path) -> None:
    scanner = "uv lock --upgrade"
    try:
        code, stdout, stderr = run(["uv", "lock", "--upgrade", "--dry-run"], root)
        if code != 0:
            raise ScannerError(f"exit {code}: {stderr.strip()[-200:]}")
        changes = parse_uv_upgrade(f"{stdout}\n{stderr}")
    except (ScannerError, OSError, subprocess.SubprocessError) as exc:
        report.fail(scanner, str(exc))
        return
    report.ok(scanner, f"{len(changes)} changes available past the 7-day hold")
    if changes:
        body = "```text\n" + "\n".join(changes) + "\n```"
        report.details.append(_details(f"Python updates ({len(changes)})", body))


def _scan_ffmpeg(report: Report, probe: UrlProbe, root: Path) -> None:
    scanner = "FFmpeg pin"
    try:
        url = find_ffmpeg_url((root / FFMPEG_SCRIPT).read_text(encoding="utf-8"))
        status = probe(url)
    except (ScannerError, OSError) as exc:
        report.fail(scanner, str(exc))
        return
    if status in (404, 410):
        report.ok(scanner, f"pinned URL is gone (HTTP {status})")
        report.sections.append(
            f"### FFmpeg pin\n\nThe pinned URL returns HTTP {status}, so a clean build "
            f"cannot fetch it:\n{url}"
        )
    elif 200 <= status < 400:
        report.ok(scanner, f"pinned URL answers (HTTP {status})")
    else:
        report.fail(scanner, f"HTTP {status} from {url}")


def collect(run: Runner, probe: UrlProbe, root: Path) -> Report:
    """Run every scanner. One failing scanner does not stop the others."""
    report = Report()
    _scan_python_audit(report, run, root)
    for npm_root in NPM_ROOTS:
        _scan_npm_audit(report, run, root, npm_root)
    _scan_python_updates(report, run, root)
    for npm_root in NPM_ROOTS:
        _scan_npm_outdated(report, run, root, npm_root)
    _scan_ffmpeg(report, probe, root)
    return report


def render(report: Report, run_url: str | None, now: datetime) -> str:
    """Write the report as Markdown that fits in an issue body."""
    lines = [f"# Dependency report, {now:%Y-%m-%d}", ""]
    if report.failed:
        names = ", ".join(report.failed)
        lines += [
            f"> **Incomplete: {len(report.failed)} scanner(s) failed ({names}).** Their results "
            "are missing below, which doesn't mean they found nothing.",
            "",
        ]
    if run_url:
        lines += [f"Run: {run_url}", ""]
    lines += ["## Scanners", "", _table(("Scanner", "Result"), report.status), ""]
    if report.sections:
        lines += ["## Findings", "", "\n\n".join(report.sections), ""]
    head = "\n".join(lines)
    if report.details:
        details = "## Updates available\n\n" + "\n\n".join(report.details) + "\n"
        if len(head) + len(details) <= MAX_BODY_CHARS:
            return head + "\n" + details
        head += "\nThe update lists were too long for an issue; see the run's summary.\n"
    return head[:MAX_BODY_CHARS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the weekly dependency report")
    parser.add_argument("--out", type=Path, required=True, help="Markdown file to write")
    parser.add_argument("--run-url", help="Link to this run, shown in the report")
    args = parser.parse_args(argv)
    report = collect(run_command, probe_url, REPO_ROOT)
    args.out.write_text(
        render(report, args.run_url, datetime.now(UTC)), encoding="utf-8", newline="\n"
    )
    for scanner, result in report.status:
        print(f"{scanner}: {result}")
    return 1 if report.failed else 0


if __name__ == "__main__":
    sys.exit(main())
