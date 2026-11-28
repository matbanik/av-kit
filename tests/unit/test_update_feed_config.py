"""The update feed's builder config, the never-publish rule and the publish checklist (MEU-173).

AC-173.1 reads ``ui/electron-builder.yml``; AC-173.2 reads every ``electron-builder`` call in
``ui/package.json`` scripts and the workflows; AC-173.5 reads the feed publish checklist and the
feed check tool. Each test holds its positive and its negative in one function.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILDER_YML = REPO_ROOT / "ui" / "electron-builder.yml"
UI_PACKAGE = REPO_ROOT / "ui" / "package.json"
WORKFLOWS = sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
CHECKLIST = REPO_ROOT / "docs" / "releases" / "publish-checklist-update-feed.md"
FEED_TOOL = REPO_ROOT / "tools" / "check_update_feed.py"
FEED = {"provider": "github", "owner": "matbanik", "repo": "av-kit"}
BUILDER_CALL = re.compile(r"\belectron-builder\b(?P<args>[^&|;\n]*)")
TOKENS = ("GH_TOKEN", "GITHUB_TOKEN")


def _feed_problems(config: dict) -> list[str]:
    """What keeps ``config`` from naming only the public GitHub feed (FEED_BLOCK)."""
    publish = config.get("publish")
    if publish is None:
        return ["no publish block"]
    entries = publish if isinstance(publish, list) else [publish]
    if len(entries) != 1:
        return [f"{len(entries)} publish entries, not 1"]
    entry = entries[0]
    if not isinstance(entry, dict):
        return [f"the publish entry is {entry!r}, not a mapping"]
    problems = [
        f"publish.{key} is {entry.get(key)!r}"
        for key, want in FEED.items()
        if entry.get(key) != want
    ]
    problems += [f"publish has the extra key {key!r}" for key in sorted(set(entry) - set(FEED))]
    return problems


def _call_problems(text: str) -> list[str]:
    """Every ``electron-builder`` call in ``text`` that may publish."""
    problems = []
    for match in BUILDER_CALL.finditer(text):
        args = match.group("args").split()
        flags = [args[i + 1] for i, arg in enumerate(args[:-1]) if arg == "--publish"]
        flags += [arg.split("=", 1)[1] for arg in args if arg.startswith("--publish=")]
        if flags != ["never"]:
            problems.append(
                f"{match.group(0).strip()!r} publishes with {flags or 'no --publish flag'}"
            )
    return problems


def _workflow_problems(path: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    problems = []
    top_env = set(data.get("env") or {})
    for job_name, job in (data.get("jobs") or {}).items():
        job_env = set(job.get("env") or {})
        for step in job.get("steps") or []:
            run = step.get("run") or ""
            if "electron-builder" not in run:
                continue
            problems += [f"{path.name} {job_name}: {p}" for p in _call_problems(run)]
            given = (top_env | job_env | set(step.get("env") or {})) & set(TOKENS)
            if given:
                problems.append(f"{path.name} {job_name}: a builder step is given {sorted(given)}")
    return problems


def test_ac_173_1_builder_names_only_the_github_feed() -> None:
    config = yaml.safe_load(BUILDER_YML.read_text(encoding="utf-8"))
    assert _feed_problems(config) == []
    text = BUILDER_YML.read_text(encoding="utf-8")
    assert "UPDATE_FEED (MEU-173, D-1540)" in text
    assert list(config).index("publish") == list(config).index("nsis") + 1

    other = copy.deepcopy(config)
    other["publish"] = [{"provider": "generic", "url": "https://example.invalid/"}]
    assert _feed_problems(other) != []
    second = copy.deepcopy(config)
    second["publish"] = [dict(FEED), dict(FEED)]
    assert _feed_problems(second) != []
    token = copy.deepcopy(config)
    token["publish"] = [{**FEED, "token": "x"}]
    assert _feed_problems(token) != []


def test_ac_173_2_every_builder_call_never_publishes() -> None:
    scripts = json.loads(UI_PACKAGE.read_text(encoding="utf-8"))["scripts"]
    calls = {name: text for name, text in scripts.items() if "electron-builder" in text}
    assert "dist" in calls
    assert scripts["dist"].endswith("electron-builder --win nsis --x64 --publish never")
    assert [p for text in calls.values() for p in _call_problems(text)] == []
    assert [p for path in WORKFLOWS for p in _workflow_problems(path)] == []
    assert any("electron-builder" in path.read_text(encoding="utf-8") for path in WORKFLOWS)

    assert _call_problems("npm run dist:prep && electron-builder --win nsis --x64") != []
    assert _call_problems("electron-builder --win nsis --x64 --publish always") != []
    assert _call_problems("electron-builder --publish=onTag") != []
    assert _call_problems("electron-builder --win nsis --x64 --publish never") == []


def _checklist_problems(text: str) -> list[str]:
    problems = []
    upload = [line for line in text.splitlines() if "gh release upload" in line]
    if not upload:
        problems.append("no upload line")
    for line in upload:
        for name in ("av-kit-Setup-", "latest.yml", ".exe.blockmap"):
            if name not in line:
                problems.append(f"the upload line lacks {name}: {line.strip()[:80]}")
    wanted = {
        "latest.yml": "the feed file",
        ".exe.blockmap": "the blockmap",
        "tools/check_update_feed.py --dist": "the FEED_CHECK command",
        "feed-ok": "the FEED_CHECK result",
        "Mat's step": "the upload is Mat's step",
        "pre-release": "the pre-release rule",
        "Latest": "the Latest rule",
        "one-time manual install": "the one-time manual install",
        "Start at sign-in": "the sign-in note",
    }
    problems += [f"no {what} ({needle!r})" for needle, what in wanted.items() if needle not in text]
    check_at = text.find("tools/check_update_feed.py --dist")
    upload_at = text.find("gh release upload")
    if check_at < 0 or upload_at < 0 or check_at > upload_at:
        problems.append("the FEED_CHECK command does not come before the upload")
    return problems


def test_ac_173_5_checklist_holds_the_upload_rules() -> None:
    assert CHECKLIST.is_file(), f"{CHECKLIST} is missing"
    assert FEED_TOOL.is_file(), f"{FEED_TOOL} is missing"
    text = CHECKLIST.read_text(encoding="utf-8")
    assert _checklist_problems(text) == []

    no_feed = text.replace("latest.yml", "feed.yml")
    assert _checklist_problems(no_feed) != []
    no_blockmap = "\n".join(
        line.replace(".exe.blockmap", "") if "gh release upload" in line else line
        for line in text.splitlines()
    )
    assert _checklist_problems(no_blockmap) != []


def _agent_command_problems(name: str, text: str, marked_only: bool) -> list[str]:
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        has = re.search(r"\bgh |\bgit push\b|\bgit tag\b", line)
        if not has:
            continue
        if marked_only and "Mat's step" in line:
            continue
        problems.append(f"{name}:{n}: {line.strip()[:80]}")
    return problems


def test_ac_173_5_no_upload_command_for_an_agent() -> None:
    assert CHECKLIST.is_file(), f"{CHECKLIST} is missing"
    assert FEED_TOOL.is_file(), f"{FEED_TOOL} is missing"
    checklist = CHECKLIST.read_text(encoding="utf-8")
    tool = FEED_TOOL.read_text(encoding="utf-8")
    assert _agent_command_problems("checklist", checklist, marked_only=True) == []
    assert _agent_command_problems("tool", tool, marked_only=False) == []
    assert "gh release" in checklist

    assert (
        _agent_command_problems("tool", tool + '\nsubprocess.run(["gh ", "release"])\n', False)
        != []
    )
    assert _agent_command_problems("checklist", "gh release upload v1 x\n", True) != []
