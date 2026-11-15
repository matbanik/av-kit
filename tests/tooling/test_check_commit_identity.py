"""The commit-identity check and its wiring into agent-commit.ps1 (Session 87, AC-11 to AC-18;
docs/execution/plans/2026-11-15-framework-small-syncs).

Every case builds a temporary repository and runs git, ``CHECKER`` or ``COMMIT_SCRIPT`` with an
environment built from scratch: ``GIT_CONFIG_GLOBAL`` points to an empty temp file,
``GIT_CONFIG_NOSYSTEM=1``, ``GIT_CEILING_DIRECTORIES`` stops git above the temp folder, and
``EMAIL``, ``GIT_AUTHOR_*`` and ``GIT_COMMITTER_*`` are removed unless the case sets them. Every
address here is synthetic; the production address is read from the loaded ``CHECKER`` module
and only ever compared, never printed. Each ``CHECKER`` test asserts ``CHECKER.is_file()``
first and asserts that the output holds no ``@``.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "tools/check_commit_identity.py"
COMMIT_SCRIPT = ROOT / ".agent/skills/git-workflow/scripts/agent-commit.ps1"

EXPECTED = "100+fixture@users.noreply.github.com"
OTHER = "200+other@users.noreply.github.com"
INVALID = "fixture@example.invalid"
IDENTITY_VARS = ("EMAIL",)
IDENTITY_PREFIXES = ("GIT_AUTHOR_", "GIT_COMMITTER_")


def _env(tmp_path: Path, **extra: str) -> dict[str, str]:
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in IDENTITY_VARS and not k.startswith(IDENTITY_PREFIXES)
    }
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG", "GIT_CONFIG_COUNT"):
        env.pop(name, None)
    global_config = tmp_path / "global.gitconfig"
    global_config.touch()
    env["GIT_CONFIG_GLOBAL"] = str(global_config)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CEILING_DIRECTORIES"] = str(tmp_path)
    env.update(extra)
    return env


def _git(repo: Path, env: dict[str, str], *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, f"fixture git {args[0]} failed with exit {result.returncode}"
    return result.stdout.strip()


def _repo(tmp_path: Path, email: str | None = EXPECTED) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    env = _env(tmp_path)
    _git(repo, env, "init", "-q", "-b", "main")
    _git(repo, env, "config", "user.name", "Fixture")
    _git(repo, env, "config", "commit.gpgsign", "false")
    if email is not None:
        _git(repo, env, "config", "user.email", email)
    return repo


def _commit(repo: Path, tmp_path: Path, name: str, author: str, committer: str) -> str:
    (repo / name).write_text(name + "\n", encoding="utf-8", newline="\n")
    env = _env(
        tmp_path,
        GIT_AUTHOR_NAME="Fixture",
        GIT_AUTHOR_EMAIL=author,
        GIT_COMMITTER_NAME="Fixture",
        GIT_COMMITTER_EMAIL=committer,
    )
    _git(repo, env, "add", "--", name)
    _git(repo, env, "commit", "-q", "--no-gpg-sign", "-m", f"test: {name}")
    return _git(repo, env, "rev-parse", "HEAD")


def _check(tmp_path: Path, repo: Path, *args: str, **extra: str) -> tuple[int, str]:
    assert CHECKER.is_file(), "missing tools/check_commit_identity.py"
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--repo", str(repo), *args],
        env=_env(tmp_path, **extra),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    output = result.stdout + result.stderr
    assert "@" not in output, "the checker printed an address"
    assert "Traceback" not in output, "the checker raised"
    return result.returncode, output


def _reasons(output: str) -> set[str]:
    prefix = "check_commit_identity: refused "
    return {line[len(prefix) :].strip() for line in output.splitlines() if line.startswith(prefix)}


def _production_address() -> str:
    assert CHECKER.is_file(), "missing tools/check_commit_identity.py"
    spec = importlib.util.spec_from_file_location("check_commit_identity", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    address = module.EXPECTED_EMAIL
    assert isinstance(address, str) and address.endswith("@users.noreply.github.com")
    return address


# AC-11: the configured address.


def test_ac_11_expected_user_email_is_ok(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED)
    assert code == 0
    assert output.strip() == "check_commit_identity: ok"


def test_ac_11_other_user_email_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, OTHER)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED)
    assert code == 1
    assert _reasons(output) == {"author_not_noreply", "committer_not_noreply", "config_mismatch"}
    assert "check_commit_identity: ok" not in output


# AC-12: the email variables, which git uses ahead of the config.


def test_ac_12_author_email_variable_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, GIT_AUTHOR_EMAIL=OTHER)
    assert code == 1
    assert _reasons(output) == {"identity_env:GIT_AUTHOR_EMAIL", "author_not_noreply"}


def test_ac_12_committer_email_variable_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, GIT_COMMITTER_EMAIL=OTHER)
    assert code == 1
    assert _reasons(output) == {"identity_env:GIT_COMMITTER_EMAIL", "committer_not_noreply"}


def test_ac_12_name_variable_alone_is_ok(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, GIT_AUTHOR_NAME="Someone Else")
    assert code == 0
    assert output.strip() == "check_commit_identity: ok"


def test_ac_12_good_variables_do_not_hide_a_bad_config(tmp_path: Path) -> None:
    repo = _repo(tmp_path, OTHER)
    code, output = _check(
        tmp_path,
        repo,
        "--expected",
        EXPECTED,
        GIT_AUTHOR_EMAIL=EXPECTED,
        GIT_COMMITTER_EMAIL=EXPECTED,
    )
    assert code == 1
    assert _reasons(output) == {"config_mismatch"}


# AC-13: author.email, committer.email and EMAIL.


def test_ac_13_author_email_config_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    _git(repo, _env(tmp_path), "config", "author.email", OTHER)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED)
    assert code == 1
    assert _reasons(output) == {"author_not_noreply"}


def test_ac_13_committer_email_config_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    _git(repo, _env(tmp_path), "config", "committer.email", OTHER)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED)
    assert code == 1
    assert _reasons(output) == {"committer_not_noreply"}


def test_ac_13_email_variable_without_user_email_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, None)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, EMAIL=OTHER)
    assert code == 1
    assert _reasons(output) == {"author_not_noreply", "committer_not_noreply", "unconfigured"}


def test_ac_13_email_variable_is_ignored_when_user_email_is_set(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, EMAIL=OTHER)
    assert code == 0
    assert output.strip() == "check_commit_identity: ok"


# AC-14: no identity at all.


def test_ac_14_no_identity_is_unconfigured_and_names_no_host(tmp_path: Path) -> None:
    repo = _repo(tmp_path, None)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED)
    assert code == 1
    assert "unconfigured" in _reasons(output)
    assert "(none)" not in output
    host = socket.gethostname().lower()
    host_found = bool(host) and host in output.lower()
    assert not host_found, "the checker printed the host name"


# AC-15: bad invocations exit 2 without a traceback or an echoed argument.


@pytest.mark.parametrize(
    "case",
    ["unknown-flag", "unknown-flag-with-address", "not-a-repo", "bad-commit"],
)
def test_ac_15_bad_invocation_exits_2(tmp_path: Path, case: str) -> None:
    repo = _repo(tmp_path, EXPECTED)
    _commit(repo, tmp_path, "base.txt", EXPECTED, EXPECTED)
    plain = tmp_path / "plain"
    plain.mkdir()
    args = {
        "unknown-flag": (repo, ["--unknown"]),
        "unknown-flag-with-address": (repo, ["--unknown", INVALID]),
        "not-a-repo": (plain, []),
        "bad-commit": (repo, ["--commit", "no-such-rev"]),
    }[case]
    code, output = _check(tmp_path, args[0], "--expected", EXPECTED, *args[1])
    assert code == 2
    assert "check_commit_identity:" in output
    assert "check_commit_identity: ok" not in output


# AC-16: the addresses stored in a commit.


def test_ac_16_commit_with_the_expected_address_is_ok(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    sha = _commit(repo, tmp_path, "a.txt", EXPECTED, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, "--commit", sha)
    assert code == 0
    assert output.strip() == "check_commit_identity: ok"


def test_ac_16_commit_with_another_author_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    _commit(repo, tmp_path, "a.txt", OTHER, EXPECTED)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, "--commit", "HEAD")
    assert code == 1
    assert _reasons(output) == {"author_not_noreply"}


def test_ac_16_commit_with_another_committer_is_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    _commit(repo, tmp_path, "a.txt", EXPECTED, OTHER)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, "--commit", "HEAD")
    assert code == 1
    assert _reasons(output) == {"committer_not_noreply"}


def test_ac_16_mailmap_does_not_hide_another_author(tmp_path: Path) -> None:
    repo = _repo(tmp_path, EXPECTED)
    (repo / ".mailmap").write_text(
        f"Fixture <{EXPECTED}> <{OTHER}>\n", encoding="utf-8", newline="\n"
    )
    _commit(repo, tmp_path, "a.txt", OTHER, OTHER)
    code, output = _check(tmp_path, repo, "--expected", EXPECTED, "--commit", "HEAD")
    assert code == 1
    assert _reasons(output) == {"author_not_noreply", "committer_not_noreply"}


# AC-17: legacy mode of COMMIT_SCRIPT refuses before staging, and commits when the identity holds.


def _run_script(repo: Path, env: dict[str, str], *args: str) -> tuple[int, str]:
    result = subprocess.run(
        ["pwsh", "-NoProfile", "-File", str(COMMIT_SCRIPT), *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def _legacy_repo(tmp_path: Path, email: str) -> tuple[Path, str]:
    repo = _repo(tmp_path, email)
    base = _commit(repo, tmp_path, "base.txt", INVALID, INVALID)
    (repo / "fixture.txt").write_text("fixture\n", encoding="utf-8", newline="\n")
    return repo, base


def _untracked(repo: Path, env: dict[str, str]) -> bool:
    return _git(repo, env, "status", "--porcelain", "--", "fixture.txt") == "?? fixture.txt"


def test_ac_17_legacy_mode_refuses_another_user_email(tmp_path: Path) -> None:
    _production_address()
    repo, base = _legacy_repo(tmp_path, OTHER)
    env = _env(tmp_path)
    code, output = _run_script(repo, env, "-Message", "test: fixture", "-SkipTests", "-NoPush")
    assert code == 1
    assert "author_not_noreply" in output
    assert "[3/7]" not in output
    assert _git(repo, env, "rev-parse", "HEAD") == base
    assert _untracked(repo, env)


def test_ac_17_legacy_mode_commits_with_the_production_address(tmp_path: Path) -> None:
    address = _production_address()
    repo, base = _legacy_repo(tmp_path, address)
    env = _env(tmp_path)
    code, output = _run_script(repo, env, "-Message", "test: fixture", "-SkipTests", "-NoPush")
    assert code == 0, "the commit script refused the production address"
    assert "Committed successfully" in output
    head = _git(repo, env, "rev-parse", "HEAD")
    assert head != base
    stored = _git(repo, env, "show", "-s", "--no-mailmap", "--format=%ae%x00%ce", "HEAD").split(
        "\x00"
    )
    same = stored == [address, address]
    assert same, "the new commit does not carry the production address"


def test_ac_17_legacy_mode_refuses_another_committer_variable(tmp_path: Path) -> None:
    address = _production_address()
    repo, base = _legacy_repo(tmp_path, address)
    env = _env(tmp_path, GIT_COMMITTER_EMAIL=OTHER)
    code, output = _run_script(repo, env, "-Message", "test: fixture", "-SkipTests", "-NoPush")
    assert code == 1
    assert "identity_env:GIT_COMMITTER_EMAIL" in output
    assert _git(repo, env, "rev-parse", "HEAD") == base
    assert _untracked(repo, env)


# AC-18: exact-scope mode checks the descriptor's address before it reads the signing config.


def test_ac_18_exact_scope_refuses_the_descriptor_address_before_signing(tmp_path: Path) -> None:
    if shutil.which("rtk") is None:
        pytest.skip("rtk is not on PATH (CI); the session gate refuses this skip")
    address = _production_address()
    repo = _repo(tmp_path, address)
    base = _commit(repo, tmp_path, "base.txt", address, address)
    (repo / "scoped.txt").write_text("scoped\n", encoding="utf-8", newline="\n")
    index = tmp_path / "exact-index"
    env_index = _env(tmp_path, GIT_INDEX_FILE=str(index))
    _git(repo, env_index, "read-tree", base)
    _git(repo, env_index, "add", "--", "scoped.txt")
    tree = _git(repo, env_index, "write-tree")
    manifest = tmp_path / "scope.txt"
    manifest.write_text("scoped.txt\n", encoding="utf-8", newline="\n")
    message = tmp_path / "message.txt"
    message.write_text("test: fixture\n", encoding="utf-8", newline="\n")
    descriptor = tmp_path / "descriptor.json"
    descriptor.write_text(
        json.dumps(
            {
                "parent": base,
                "tree": tree,
                "message_sha256": hashlib.sha256(message.read_bytes()).hexdigest(),
                "author_name": "Fixture",
                "author_email": INVALID,
                "signing_fingerprint": "SHA256:fixture",
            }
        ),
        encoding="utf-8",
    )
    env = _env(tmp_path)
    code, output = _run_script(
        repo,
        env,
        "-RepositoryPath",
        str(repo),
        "-ScopeManifest",
        str(manifest),
        "-ExpectedBase",
        base,
        "-ExpectedTree",
        tree,
        "-ContentDescriptor",
        str(descriptor),
        "-MessageFile",
        str(message),
        "-OutputState",
        str(tmp_path / "state.json"),
        "-NoPush",
    )
    assert "author_not_noreply" in output
    assert code != 0
    assert "SSH commit-signing" not in output
    assert "commit.gpgsign" not in output
    assert _git(repo, env, "rev-parse", "HEAD") == base
    assert INVALID not in output
