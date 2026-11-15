"""Session 87 wiring check (AC-19; implementation-plan.md §Wiring into agent-commit.ps1, D-883).

Usage: ``python script-check.py`` (the live files against their row-0 copies in
``C:/Temp/av-kit/fs/base/``) or ``python script-check.py --selftest``. Run from the repository root.

It refuses unless all of these hold:

* ``COMMIT_SCRIPT`` and ``GIT_SKILL`` are add-only against ``BASE``: every ``BASE`` line is still
  there, in order, and both files are CRLF on every line;
* in ``COMMIT_SCRIPT`` the helper ``Invoke-CommitIdentityCheck`` is defined after
  ``Invoke-RtkGitExact`` and before ``Invoke-ExactScopeCommit`` and runs
  ``tools/check_commit_identity.py``; there is exactly one call of each kind, and
  - the exact-scope early call (``-AuthorEmail``) sits after the message-hash check and before
    the ``commit.gpgsign`` read,
  - the exact-scope late call (``-Commit $actualSha``) sits after ``verify-commit``,
  - the legacy pre-commit call (no ``-Commit``) sits in Step 1, before the Step 2 header and so
    before ``git add -A``,
  - the legacy post-commit call (``-Commit HEAD``) sits after ``Committed successfully`` and
    before ``git push``;
* ``--expected`` does not appear in ``COMMIT_SCRIPT``;
* ``GIT_SKILL`` names ``tools/check_commit_identity.py`` under ``### What the Script Does``, in the
  Agent Workflow Checklist, and the descriptor's ``author_email`` check under
  ``### Exact-Scope Signed Commit Mode``.

``--selftest`` builds its own fixture script and skill (not the repo files): a passing control,
then a copy with a removed ``BASE`` line, one with an LF line, one with the pre-commit call
moved after ``git add -A`` and one passing ``--expected``; each negative must be refused.
"""

from __future__ import annotations

import pathlib
import re
import sys

COMMIT_SCRIPT = ".agent/skills/git-workflow/scripts/agent-commit.ps1"
GIT_SKILL = ".agent/skills/git-workflow/SKILL.md"
BASE_DIR = "C:/Temp/av-kit/fs/base"
CHECKER = "tools/check_commit_identity.py"
CALL = re.compile(r"Invoke-CommitIdentityCheck\s+-Repo\b")


def crlf_problem(name: str, data: bytes) -> str | None:
    lines = data.count(b"\n")
    pairs = data.count(b"\r\n")
    if lines == 0 or pairs != lines or data.count(b"\r") != pairs or not data.endswith(b"\r\n"):
        return f"{name}: not CRLF on every line ({pairs} CRLF of {lines} lines)"
    return None


def add_only_problem(name: str, base: bytes, new: bytes) -> str | None:
    old_lines = base.decode("utf-8").split("\r\n")
    new_lines = new.decode("utf-8").split("\r\n")
    i = 0
    for line in new_lines:
        if i < len(old_lines) and line == old_lines[i]:
            i += 1
    if i != len(old_lines):
        return f"{name}: BASE line {i + 1} is missing or out of order: {old_lines[i][:100]!r}"
    return None


def first(lines: list[str], needle: str, start: int = 0) -> int:
    for n in range(start, len(lines)):
        if needle in lines[n]:
            return n
    return -1


def section(lines: list[str], heading: str) -> str:
    start = first(lines, heading)
    if start < 0:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    end = len(lines)
    for n in range(start + 1, len(lines)):
        m = re.match(r"^(#+)\s", lines[n])
        if m and len(m.group(1)) <= level:
            end = n
            break
    return "\n".join(lines[start:end])


def check(base_script: bytes, script: bytes, base_skill: bytes, skill: bytes) -> list[str]:
    problems: list[str] = []
    for name, base, new in ((COMMIT_SCRIPT, base_script, script), (GIT_SKILL, base_skill, skill)):
        if p := crlf_problem(name, new):
            problems.append(p)
        if p := add_only_problem(name, base, new):
            problems.append(p)
    lines = script.decode("utf-8").replace("\r\n", "\n").split("\n")
    if "--expected" in script.decode("utf-8"):
        problems.append(f"{COMMIT_SCRIPT}: passes --expected")
    rtk = first(lines, "function Invoke-RtkGitExact")
    helper = first(lines, "function Invoke-CommitIdentityCheck")
    exact = first(lines, "function Invoke-ExactScopeCommit")
    if not (0 <= rtk < helper < exact):
        problems.append(f"{COMMIT_SCRIPT}: the helper is not defined between Invoke-RtkGitExact and Invoke-ExactScopeCommit")
    elif CHECKER not in "\n".join(lines[helper:exact]):
        problems.append(f"{COMMIT_SCRIPT}: the helper does not run {CHECKER}")
    calls = [n for n, ln in enumerate(lines) if CALL.search(ln) and "function " not in ln]
    kinds = {
        "exact-early": [n for n in calls if "-AuthorEmail" in lines[n]],
        "exact-late": [n for n in calls if " -Commit $actualSha" in lines[n]],
        # A space before -Commit: the helper's own name holds "-Commit" too.
        "legacy-pre": [n for n in calls if not re.search(r"\s-Commit\b", lines[n]) and "-AuthorEmail" not in lines[n]],
        "legacy-post": [n for n in calls if re.search(r"-Commit\s+HEAD\b", lines[n])],
    }
    for kind, found in kinds.items():
        if len(found) != 1:
            problems.append(f"{COMMIT_SCRIPT}: {len(found)} {kind} call(s), expected 1")
    if len(calls) != 4:
        problems.append(f"{COMMIT_SCRIPT}: {len(calls)} helper calls, expected 4")
    anchors = {
        "message-hash": first(lines, "Message file hash does not match content descriptor"),
        "gpgsign": first(lines, '"config", "--get", "commit.gpgsign"'),
        "verify-commit": first(lines, '"verify-commit"'),
        "step1": first(lines, "[1/7] Checking signing config"),
        "step2": first(lines, "[2/7] Checking remote URL"),
        "add": next((n for n, ln in enumerate(lines) if ln.strip() == "git add -A"), -1),
        "committed": first(lines, "Committed successfully"),
        "push": first(lines, "git push origin $Branch"),
    }
    for name, n in anchors.items():
        if n < 0:
            problems.append(f"{COMMIT_SCRIPT}: anchor {name} not found")
    if all(len(v) == 1 for v in kinds.values()) and all(n >= 0 for n in anchors.values()):
        order = (
            ("exact-early", anchors["message-hash"] < kinds["exact-early"][0] < anchors["gpgsign"]),
            ("exact-late", anchors["verify-commit"] < kinds["exact-late"][0] < anchors["step1"]),
            ("legacy-pre", anchors["step1"] < kinds["legacy-pre"][0] < anchors["step2"] < anchors["add"]),
            ("legacy-post", anchors["committed"] < kinds["legacy-post"][0] < anchors["push"]),
        )
        for kind, ok in order:
            if not ok:
                problems.append(f"{COMMIT_SCRIPT}: the {kind} call is out of place")
            else:
                print(f"{COMMIT_SCRIPT}: {kind} call at line {kinds[kind][0] + 1} in place")
    skill_lines = skill.decode("utf-8").replace("\r\n", "\n").split("\n")
    for heading, needle in (
        ("### What the Script Does", CHECKER),
        ("## Agent Workflow Checklist", CHECKER),
        ("### Exact-Scope Signed Commit Mode", "author_email"),
    ):
        if needle not in section(skill_lines, heading):
            problems.append(f"{GIT_SKILL}: {heading} does not name {needle}")
        else:
            print(f"{GIT_SKILL}: {heading} names {needle}")
    return problems


FIX_BASE_SCRIPT = [
    "function Invoke-RtkGitExact {",
    "}",
    "function Invoke-ExactScopeCommit {",
    '        throw "Message file hash does not match content descriptor"',
    '    $signingEnabled = Invoke-RtkGitExact -Repo $repo -Arguments @("config", "--get", "commit.gpgsign")',
    '        $null = Invoke-RtkGitExact -Repo $repo -Arguments @("verify-commit", $actualSha)',
    "}",
    'Write-Host "`n[1/7] Checking signing config..."',
    'Write-Host "[2/7] Checking remote URL..."',
    "git add -A",
    'Write-Host "  Committed successfully"',
    "git push origin $Branch",
]
FIX_ADDED = {
    "}": ["function Invoke-CommitIdentityCheck {", "    & uv run python tools/check_commit_identity.py --repo $Repo", "}"],
    '        throw "Message file hash does not match content descriptor"': ["    $c = Invoke-CommitIdentityCheck -Repo $repo -AuthorEmail $e -CommitterEmail $e"],
    '        $null = Invoke-RtkGitExact -Repo $repo -Arguments @("verify-commit", $actualSha)': ["        $c = Invoke-CommitIdentityCheck -Repo $repo -Commit $actualSha"],
    'Write-Host "`n[1/7] Checking signing config..."': ["$c = Invoke-CommitIdentityCheck -Repo (Get-Location).Path"],
    'Write-Host "  Committed successfully"': ["$c = Invoke-CommitIdentityCheck -Repo (Get-Location).Path -Commit HEAD"],
}
FIX_BASE_SKILL = ["### Exact-Scope Signed Commit Mode", "Text.", "### What the Script Does", "1. a", "## Agent Workflow Checklist", "- [ ] Step 1"]
FIX_SKILL_ADDED = {
    "Text.": ["The descriptor's `author_email` is checked the same way."],
    "1. a": ["2b. Refuses (`tools/check_commit_identity.py`)"],
    "- [ ] Step 1": ["- [ ] Step 1b: `uv run python tools/check_commit_identity.py`"],
}


def _grow(base: list[str], added: dict[str, list[str]]) -> list[str]:
    out: list[str] = []
    done: set[str] = set()
    for line in base:
        out.append(line)
        if line in added and line not in done:
            out.extend(added[line])
            done.add(line)
    return out


def _crlf(lines: list[str]) -> bytes:
    return ("\r\n".join(lines) + "\r\n").encode()


def selftest() -> int:
    base_s, base_k = _crlf(FIX_BASE_SCRIPT), _crlf(FIX_BASE_SKILL)
    good = _grow(FIX_BASE_SCRIPT, FIX_ADDED)
    skill = _crlf(_grow(FIX_BASE_SKILL, FIX_SKILL_ADDED))
    removed = [ln for ln in good if ln != 'Write-Host "[2/7] Checking remote URL..."']
    pre = "$c = Invoke-CommitIdentityCheck -Repo (Get-Location).Path"
    moved = [ln for ln in good if ln != pre]
    moved.insert(moved.index("git add -A") + 1, pre)
    expected = [ln + " --expected x" if ln == pre else ln for ln in good]
    cases = (
        ("control", _crlf(good), False),
        ("removed-base-line", _crlf(removed), True),
        ("lf-line", _crlf(good).replace(b"git add -A\r\n", b"git add -A\n"), True),
        ("pre-call-after-git-add", _crlf(moved), True),
        ("passes-expected", _crlf(expected), True),
    )
    failures: list[str] = []
    for name, script, want in cases:
        problems = check(base_s, script, base_k, skill)
        refused = bool(problems)
        print(f"selftest {name}: refused={refused} problems={problems[:2]}")
        if refused != want:
            failures.append(f"{name}: refused={refused}, expected {want}")
    for f in failures:
        print("SELFTEST FAIL:", f)
    print(f"script-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    if argv:
        print("usage: script-check.py [--selftest]")
        return 2
    base = pathlib.Path(BASE_DIR)
    problems = check(
        (base / COMMIT_SCRIPT).read_bytes(),
        pathlib.Path(COMMIT_SCRIPT).read_bytes(),
        (base / GIT_SKILL).read_bytes(),
        pathlib.Path(GIT_SKILL).read_bytes(),
    )
    for p in problems:
        print("PROBLEM:", p)
    print(f"script-check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
