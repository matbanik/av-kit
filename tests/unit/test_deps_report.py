"""Weekly dependency report: a failed scanner must never read as zero findings."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from tools import deps_report as dr

NOW = datetime(2026, 11, 3, tzinfo=UTC)


def _uv_item(name: str, version: str, fixes: list[str]) -> dict:
    return {"dependency": {"name": name, "version": version}, "fix_versions": fixes}


def _uv_audit(items: list[dict], audited: int = 135) -> str:
    summary = {"audited_packages": audited, "vulnerabilities": len(items)}
    return json.dumps({"summary": summary, "vulnerabilities": items})


def _npm_audit(packages: dict | None = None, total: int = 0) -> str:
    return json.dumps(
        {"metadata": {"vulnerabilities": {"total": total}}, "vulnerabilities": packages or {}}
    )


NPM_FAILURE = json.dumps({"message": "connect ECONNREFUSED", "error": {"summary": ""}})


class FakeTools:
    """Answers each scanner command; a test replaces the answers it cares about."""

    def __init__(self) -> None:
        self.uv_audit = (0, _uv_audit([]), "")
        self.uv_upgrade = (0, "", "Resolved 139 packages in 1s\n")
        self.npm_audit = (0, _npm_audit(), "")
        self.npm_ci = (0, "", "")
        self.npm_outdated = (0, "{}", "")
        self.calls: list[tuple[list[str], Path]] = []

    def __call__(self, args: list[str], cwd: Path) -> tuple[int, str, str]:
        self.calls.append((args, cwd))
        if args[:2] == ["uv", "audit"]:
            return self.uv_audit
        if args[:2] == ["uv", "lock"]:
            return self.uv_upgrade
        if args[:2] == ["npm", "audit"]:
            return self.npm_audit
        if args[:2] == ["npm", "ci"]:
            return self.npm_ci
        if args[:2] == ["npm", "outdated"]:
            return self.npm_outdated
        raise AssertionError(f"unexpected command: {args}")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    script = tmp_path / dr.FFMPEG_SCRIPT
    script.parent.mkdir(parents=True)
    script.write_text(
        "[string]$Url = 'https://github.com/BtbN/FFmpeg-Builds/releases/download/a/b.zip'\n",
        encoding="utf-8",
    )
    return tmp_path


def test_uv_audit_groups_advisories_by_package() -> None:
    result = dr.parse_uv_audit(
        _uv_audit(
            [
                _uv_item("pillow", "12.3.0", ["12.3.1"]),
                _uv_item("pillow", "12.3.0", ["13.0.0"]),
                _uv_item("filelock", "3.32.3", []),
            ]
        )
    )
    assert result["total"] == 3
    assert [row["name"] for row in result["rows"]] == ["pillow", "filelock"]
    assert result["rows"][0]["count"] == 2
    assert result["rows"][1]["unfixed"] == 1


@pytest.mark.parametrize(
    "stdout",
    [
        "",
        "not json",
        "[]",
        json.dumps({"summary": {"audited_packages": 135}}),
        _uv_audit([], audited=0),
        json.dumps(
            {"summary": {"audited_packages": 1, "vulnerabilities": 5}, "vulnerabilities": []}
        ),
        _uv_audit([{"dependency": {"name": "x"}}]),
    ],
)
def test_uv_audit_refuses_output_it_cannot_trust(stdout: str) -> None:
    with pytest.raises(dr.ScannerError):
        dr.parse_uv_audit(stdout)


@pytest.mark.parametrize("stdout", ["", "oops", NPM_FAILURE, json.dumps({"metadata": {}})])
def test_npm_audit_refuses_output_it_cannot_trust(stdout: str) -> None:
    with pytest.raises(dr.ScannerError):
        dr.parse_npm_audit(stdout)


def test_shipped_view_adds_electron_but_no_other_dev_dependency() -> None:
    shipped = dr.parse_npm_audit(
        _npm_audit({"zod": {"severity": "high", "range": "<4", "fixAvailable": True}}, 1)
    )
    full = dr.parse_npm_audit(
        _npm_audit(
            {
                "zod": {"severity": "high", "range": "<4", "fixAvailable": True},
                "electron": {"severity": "critical", "range": "<=42", "fixAvailable": True},
                "vitest": {"severity": "critical", "range": "<5", "fixAvailable": False},
            },
            3,
        )
    )
    rows = dr.shipped_rows(shipped, full)
    assert [row["name"] for row in rows] == ["electron", "zod"]


def test_outdated_marks_majors_and_lists_them_first() -> None:
    rows = dr.parse_npm_outdated(
        json.dumps(
            {
                "react": {"current": "19.2.8", "wanted": "19.2.9", "latest": "19.2.9"},
                "zod": {"current": "3.25.0", "wanted": "3.25.0", "latest": "4.1.0"},
            }
        )
    )
    assert [(row["name"], row["major"]) for row in rows] == [("zod", True), ("react", False)]


def test_outdated_refuses_a_package_that_is_not_installed() -> None:
    with pytest.raises(dr.ScannerError):
        dr.parse_npm_outdated(json.dumps({"zod": {"wanted": "3.25.0", "latest": "4.1.0"}}))


def test_uv_upgrade_needs_a_finished_resolve() -> None:
    assert dr.parse_uv_upgrade("Resolved 2 packages in 1s\nUpdate a v1 -> v2\n") == [
        "Update a v1 -> v2"
    ]
    with pytest.raises(dr.ScannerError):
        dr.parse_uv_upgrade("error: failed to fetch\n")


def test_ffmpeg_url_must_appear_exactly_once() -> None:
    url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/a/b.zip"
    assert dr.find_ffmpeg_url(f"'{url}' and again '{url}'") == url
    with pytest.raises(dr.ScannerError):
        dr.find_ffmpeg_url("no url here")
    with pytest.raises(dr.ScannerError):
        dr.find_ffmpeg_url(f"'{url}' '{url}2'")


def test_findings_alone_do_not_mark_the_report_incomplete(repo: Path) -> None:
    tools = FakeTools()
    tools.uv_audit = (1, _uv_audit([_uv_item("pillow", "12.3.0", ["13.0.0"])]), "")
    tools.npm_audit = (
        1,
        _npm_audit({"zod": {"severity": "high", "range": "<4", "fixAvailable": False}}, 1),
        "",
    )
    report = dr.collect(tools, lambda _url: 200, repo)
    text = dr.render(report, None, NOW)
    assert report.failed == []
    assert "Incomplete" not in text
    assert "pillow" in text and "13.0.0" in text
    assert "zod" in text


def test_a_dead_ffmpeg_url_is_a_finding_not_a_scanner_failure(repo: Path) -> None:
    report = dr.collect(FakeTools(), lambda _url: 404, repo)
    assert report.failed == []
    assert "HTTP 404" in dr.render(report, None, NOW)


@pytest.mark.parametrize("status", [403, 500, 503])
def test_an_unclear_ffmpeg_answer_is_a_scanner_failure(repo: Path, status: int) -> None:
    report = dr.collect(FakeTools(), lambda _url: status, repo)
    assert report.failed == ["FFmpeg pin"]


def test_an_unreachable_ffmpeg_host_is_a_scanner_failure(repo: Path) -> None:
    def refuse(_url: str) -> int:
        raise OSError("no route to host")

    report = dr.collect(FakeTools(), refuse, repo)
    assert report.failed == ["FFmpeg pin"]


@pytest.mark.parametrize(
    ("attribute", "answer", "scanner"),
    [
        ("uv_audit", (1, "", "network error"), "uv audit"),
        ("uv_audit", (2, _uv_audit([]), "panic"), "uv audit"),
        ("npm_audit", (1, NPM_FAILURE, ""), "npm audit (ui)"),
        ("uv_upgrade", (1, "", "error: boom"), "uv lock --upgrade"),
        ("npm_ci", (1, "", "EUSAGE"), "npm outdated (ui)"),
        ("npm_outdated", (1, json.dumps({"error": {"code": "E500"}}), ""), "npm outdated (ui)"),
    ],
)
def test_a_failed_scanner_is_named_and_never_counted_as_zero(
    repo: Path, attribute: str, answer: tuple[int, str, str], scanner: str
) -> None:
    tools = FakeTools()
    setattr(tools, attribute, answer)
    report = dr.collect(tools, lambda _url: 200, repo)
    text = dr.render(report, None, NOW)
    assert scanner in report.failed
    assert "Incomplete" in text
    row = next(line for line in text.splitlines() if line.startswith(f"| {scanner} |"))
    assert "**FAILED**" in row
    assert "ok:" not in row


def test_one_failed_scanner_does_not_stop_the_others(repo: Path) -> None:
    tools = FakeTools()
    tools.uv_audit = (1, "", "network error")
    report = dr.collect(tools, lambda _url: 200, repo)
    assert report.failed == ["uv audit"]
    assert len(report.status) == 7
    assert ["npm", "outdated", "--json"] in [args for args, _cwd in tools.calls]


def test_outdated_installs_first_without_running_install_scripts(repo: Path) -> None:
    tools = FakeTools()
    dr.collect(tools, lambda _url: 200, repo)
    commands = [args for args, cwd in tools.calls if cwd == repo / "ui"]
    assert commands.index(["npm", "ci", "--ignore-scripts"]) < commands.index(
        ["npm", "outdated", "--json"]
    )


def test_outdated_keeps_an_existing_install(repo: Path) -> None:
    """A local run must not replace node_modules: that deletes the dev Electron binary."""
    (repo / "ui" / "node_modules").mkdir(parents=True)
    tools = FakeTools()
    dr.collect(tools, lambda _url: 200, repo)
    commands = [args for args, cwd in tools.calls if cwd == repo / "ui"]
    assert ["npm", "ci", "--ignore-scripts"] not in commands
    assert ["npm", "outdated", "--json"] in commands


def test_huge_update_lists_are_dropped_so_the_body_fits_an_issue(repo: Path) -> None:
    tools = FakeTools()
    changes = "".join(f"Update package-{n:05} v1.0.0 -> v2.0.0\n" for n in range(5000))
    tools.uv_upgrade = (0, "", f"Resolved 5000 packages in 1s\n{changes}")
    text = dr.render(dr.collect(tools, lambda _url: 200, repo), None, NOW)
    assert len(text) <= dr.MAX_BODY_CHARS
    assert "too long" in text
    assert "Updates available" not in text


def test_the_report_stays_inside_the_issue_limit_with_every_section_full() -> None:
    report = dr.Report()
    report.ok("scanner", "note")
    report.sections.append("x" * (dr.MAX_BODY_CHARS * 2))
    assert len(dr.render(report, None, NOW)) <= dr.MAX_BODY_CHARS


def test_main_writes_the_report_and_returns_1_on_a_failed_scanner(
    repo: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tools = FakeTools()
    tools.uv_audit = (1, "", "network error")
    monkeypatch.setattr(dr, "run_command", tools)
    monkeypatch.setattr(dr, "probe_url", lambda _url: 200)
    monkeypatch.setattr(dr, "REPO_ROOT", repo)
    out = tmp_path / "report.md"
    assert dr.main(["--out", str(out), "--run-url", "https://example.test/run"]) == 1
    text = out.read_text(encoding="utf-8")
    assert "Incomplete" in text
    assert "https://example.test/run" in text
