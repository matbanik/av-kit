"""The home-path check (Session 83, AC-1 to AC-7, AC-22 and AC-23;
docs/execution/plans/2026-11-15-docs-path-hygiene).

Every case builds a temporary repository and runs ``CHECK`` against it with the fake home
``C:\\Users\\fixture`` (``/home/fixture`` for AC-7) and an allow-list of its own, kept outside the
repository. git runs with an environment built from scratch: ``GIT_CONFIG_GLOBAL`` points to an
empty temp file, ``GIT_CONFIG_NOSYSTEM=1`` and ``GIT_CEILING_DIRECTORIES`` stops git above the
temp folder. No case reads the real home folder. Each case asserts ``CHECK.is_file()`` first, and
every run's output must hold neither ``Users`` nor ``fixture`` nor a traceback: the check prints
``path:line`` only, so the scanned files are named without either word.
"""

from __future__ import annotations

import codecs
import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECK = ROOT / "tools/check_home_path.py"
PREFIX = "check_home_path:"
HOME = "C:\\Users\\fixture"
POSIX_HOME = "/home/fixture"
MARK = "QZMARK"

#: name -> (codec, byte-order mark)
ENCODINGS = {
    "utf8": ("utf-8", b""),
    "utf8-bom": ("utf-8", codecs.BOM_UTF8),
    "utf16le-bom": ("utf-16-le", codecs.BOM_UTF16_LE),
    "utf16be-bom": ("utf-16-be", codecs.BOM_UTF16_BE),
    "utf32le-bom": ("utf-32-le", codecs.BOM_UTF32_LE),
    "utf32be-bom": ("utf-32-be", codecs.BOM_UTF32_BE),
    "utf16le": ("utf-16-le", b""),
    "utf16be": ("utf-16-be", b""),
    "utf32le": ("utf-32-le", b""),
    "utf32be": ("utf-32-be", b""),
}

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PNG_HEAD = b"\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\x00\x00\x00\x1f\xf3\xffa"
PNG_TAIL = b"\x00\x00\x00\x00IEND\xaeB`\x82"


# --- helpers -------------------------------------------------------------------------------


def _env(tmp_path: Path) -> dict[str, str]:
    env = dict(os.environ)
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG", "GIT_CONFIG_COUNT"):
        env.pop(name, None)
    global_config = tmp_path / "global.gitconfig"
    global_config.touch()
    env["GIT_CONFIG_GLOBAL"] = str(global_config)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CEILING_DIRECTORIES"] = str(tmp_path)
    return env


def _git(repo: Path, env: dict[str, str], *args: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, f"fixture git {args[0]} failed with exit {result.returncode}"


def _repo(tmp_path: Path, files: dict[str, bytes] | None = None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, _env(tmp_path), "init", "-q")
    for name, raw in (files or {}).items():
        _write(repo, name, raw)
    return repo


def _write(repo: Path, name: str, raw: bytes) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def _encode(text: str, kind: str) -> bytes:
    codec, mark = ENCODINGS[kind]
    return mark + text.encode(codec)


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def _allowlist(tmp_path: Path, raw: bytes = b"# empty test allow-list\n") -> Path:
    path = tmp_path / "allowlist.txt"
    path.write_bytes(raw)
    return path


def _cli(tmp_path: Path, *argv: str) -> tuple[int, str]:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    result = subprocess.run(
        [sys.executable, str(CHECK), *argv],
        env=_env(tmp_path),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = result.stdout + result.stderr
    assert "Traceback" not in output, "the check raised"
    assert "users" not in output.lower(), "the output holds the home folder"
    assert "fixture" not in output.lower(), "the output holds the home folder"
    return result.returncode, output


def _run(
    tmp_path: Path,
    repo: Path,
    *args: str,
    home: str = HOME,
    allowlist: Path | None = None,
) -> tuple[int, str]:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    allow = allowlist if allowlist is not None else _allowlist(tmp_path)
    return _cli(tmp_path, "--repo", str(repo), "--home", home, "--allowlist", str(allow), *args)


def _lines(output: str) -> list[str]:
    return [line.strip() for line in output.splitlines() if line.startswith(PREFIX)]


def _found(output: str) -> list[str]:
    head = f"{PREFIX} found "
    return [line[len(head) :] for line in _lines(output) if line.startswith(head)]


def _load() -> ModuleType:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    spec = importlib.util.spec_from_file_location("check_home_path_under_test", CHECK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _in_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo: Path,
) -> tuple[int, str, list[str]]:
    """Run CHECK in this process with its file reader patched to record every path it reads."""
    module = _load()
    for name, value in _env(tmp_path).items():
        if name.startswith("GIT_"):
            monkeypatch.setenv(name, value)
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_CONFIG", "GIT_CONFIG_COUNT"):
        monkeypatch.delenv(name, raising=False)
    read: list[str] = []
    real = module._read_bytes
    top = repo.resolve()

    def reader(path: Path) -> bytes:
        read.append(Path(path).resolve().relative_to(top).as_posix())
        return real(path)

    monkeypatch.setattr(module, "_read_bytes", reader)
    allow = _allowlist(tmp_path)
    code = module.main(["--repo", str(repo), "--home", HOME, "--allowlist", str(allow)])
    captured = capsys.readouterr()
    output = captured.out + captured.err
    assert "Traceback" not in output, "the check raised"
    assert "users" not in output.lower(), "the output holds the home folder"
    assert "fixture" not in output.lower(), "the output holds the home folder"
    return code, output, read


# --- AC-1: every spelling is found, in every encoding ---------------------------------------

FOUND_FORMS = {
    "backslash": "C:\\Users\\fixture\\a",
    "slash": "C:/Users/fixture/a",
    "doubled": "C:\\\\Users\\\\fixture\\\\a",
    "case": "c:\\users\\FIXTURE\\a",
    "file-url": "file:///C:/Users/fixture/a",
    "git-bash": "/c/Users/fixture/a",
    "wsl": "/mnt/c/Users/fixture/a",
    "bare": "C:\\Users\\fixture",
    "sentence": "it ran in C:\\Users\\fixture.",
    "comma": "in C:\\Users\\fixture, then",
    "paren": "(C:\\Users\\fixture)",
    "quote": '"C:\\Users\\fixture"',
}


@pytest.mark.parametrize("form", sorted(FOUND_FORMS))
def test_ac_1_each_form_is_found_in_each_encoding(tmp_path: Path, form: str) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    text = f"first line\n{FOUND_FORMS[form]}\nlast line\n"
    repo = _repo(tmp_path, {f"enc-{kind}.txt": _encode(text, kind) for kind in ENCODINGS})
    code, output = _run(tmp_path, repo)
    assert code == 1, f"form {form}: exit {code}"
    assert sorted(_found(output)) == sorted(f"enc-{kind}.txt:2" for kind in ENCODINGS)
    assert _lines(output)[-1] == f"{PREFIX} refused found={len(ENCODINGS)} changed=0 stale=0"


# --- AC-2: longer names, other users and other drives are not found -------------------------

NOT_FOUND = (
    "C:\\Users\\fixtures\\a",
    "C:\\Users\\fixture.other\\a",
    "C:\\Users\\fixture-other\\a",
    "C:\\Users\\fixture_x\\a",
    "C:\\Users\\fixture\u00e9\\a",
    "C:\\Users\\YOU\\a",
    "D:\\Users\\fixture\\a",
    "fixture",
    "~/a",
    "%USERPROFILE%\\a",
)


def test_ac_2_near_misses_are_not_found(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"near.txt": ("\n".join(NOT_FOUND) + "\n").encode("utf-8")})
    code, output = _run(tmp_path, repo)
    assert _found(output) == []
    assert code == 0
    assert _lines(output) == [f"{PREFIX} ok files=1 allowlisted=0 nul=0"]


# --- AC-3: output form, order and line numbers ----------------------------------------------


def test_ac_3_output_is_path_and_line_only_sorted(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    hit = f"{MARK}-line C:\\Users\\fixture\\a"
    alpha = [f"plain {n}" for n in range(1, 11)]
    alpha[1] = hit
    alpha[9] = hit
    beta = [hit, "plain", hit, "plain"]
    repo = _repo(
        tmp_path,
        {
            "alpha.txt": ("\n".join(alpha) + "\n").encode(),
            "beta.txt": ("\r\n".join(beta) + "\r\n").encode(),
            "zeta/notes.md": b"nothing here\n",
        },
    )
    code, output = _run(tmp_path, repo)
    assert code == 1
    assert _lines(output) == [
        f"{PREFIX} found alpha.txt:2",
        f"{PREFIX} found alpha.txt:10",
        f"{PREFIX} found beta.txt:1",
        f"{PREFIX} found beta.txt:3",
        f"{PREFIX} refused found=4 changed=0 stale=0",
    ]
    assert MARK not in output, "the output holds a scanned line's text"


# --- AC-4: the allow-list --------------------------------------------------------------------

LISTED = b"ran in C:\\Users\\fixture\\work\n"
GOOD = "a" * 64


def test_ac_4_listed_file_with_its_digest_is_exempt(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"listed.md": LISTED})
    allow = _allowlist(
        tmp_path, f"# header {MARK}\n\n# another comment\n{_digest(LISTED)}  listed.md\n\n".encode()
    )
    code, output = _run(tmp_path, repo, allowlist=allow)
    assert code == 0
    assert _lines(output) == [f"{PREFIX} ok files=1 allowlisted=1 nul=0"]
    assert MARK not in output


def test_ac_4_listed_file_that_is_missing_is_stale(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"other.md": b"plain\n"})
    allow = _allowlist(tmp_path, f"# header\n{GOOD}  gone.md\n".encode())
    code, output = _run(tmp_path, repo, allowlist=allow)
    assert code == 1
    assert _lines(output) == [
        f"{PREFIX} stale gone.md",
        f"{PREFIX} refused found=0 changed=0 stale=1",
    ]


MALFORMED = {
    "digest-upper": ([f"{'A' * 64}  {MARK}.md"], 3),
    "digest-short": ([f"{'a' * 63}  {MARK}.md"], 3),
    "absolute": ([f"{GOOD}  /{MARK}.md"], 3),
    "drive": ([f"{GOOD}  C:/{MARK}.md"], 3),
    "backslash": ([f"{GOOD}  dir\\{MARK}.md"], 3),
    "dotdot": ([f"{GOOD}  ../{MARK}.md"], 3),
    "duplicate": ([f"{GOOD}  {MARK}.md", f"{GOOD}  {MARK}.md"], 4),
    "out-of-order": ([f"{GOOD}  z{MARK}.md", f"{GOOD}  a{MARK}.md"], 4),
    "hub": ([f"{GOOD}  .agent/fleet/hub/{MARK}.md"], 3),
}


@pytest.mark.parametrize("case", sorted(MALFORMED))
def test_ac_4_malformed_allowlist_line_exits_2(tmp_path: Path, case: str) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    entries, number = MALFORMED[case]
    repo = _repo(tmp_path, {"plain.md": b"plain\n"})
    allow = _allowlist(tmp_path, ("# header\n\n" + "\n".join(entries) + "\n").encode())
    code, output = _run(tmp_path, repo, allowlist=allow)
    assert code == 2, f"{case}: exit {code}"
    assert f"{PREFIX} usage error: allowlist line {number} is malformed" in output
    assert MARK not in output, "the output echoes the allow-list line"


def test_ac_4_missing_allowlist_exits_2(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"plain.md": b"plain\n"})
    code, _ = _run(tmp_path, repo, allowlist=tmp_path / "absent.txt")
    assert code == 2


# --- AC-5: which files are read --------------------------------------------------------------

HIT = b"C:\\Users\\fixture\\a\n"


def test_ac_5_untracked_ignored_and_deleted_files(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(
        tmp_path,
        {".gitignore": b"ignored.txt\n", "ignored.txt": HIT, "untracked.txt": HIT, "gone.txt": HIT},
    )
    _git(repo, _env(tmp_path), "add", "--", "gone.txt")
    (repo / "gone.txt").unlink()
    code, output = _run(tmp_path, repo)
    assert code == 1
    assert _lines(output) == [
        f"{PREFIX} found untracked.txt:1",
        f"{PREFIX} refused found=1 changed=0 stale=0",
    ]
    assert "cannot read" not in output


def test_ac_5_hub_files_are_never_opened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {".agent/fleet/hub/state.md": HIT, "plain.md": b"plain\n"})
    code, output, read = _in_process(tmp_path, monkeypatch, capsys, repo)
    assert "plain.md" in read, "the patched reader was not used"
    assert not [p for p in read if p.startswith(".agent/fleet/hub/")], "a hub file was read"
    assert "hub" not in output
    assert code == 0


SECRETS = (
    ".mcp.json",
    "mcp-token.txt",
    ".claude.json",
    ".env",
    ".env.local",
    "sub/.env",
    ".claude/settings.local.json",
)


def test_ac_5_secret_paths_never_opened(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {**{name: HIT for name in SECRETS}, "plain.md": b"plain\n"})
    code, output, read = _in_process(tmp_path, monkeypatch, capsys, repo)
    assert read == ["plain.md"], f"read {read}"
    assert code == 0
    assert _found(output) == []


# --- AC-6: usage errors ----------------------------------------------------------------------


def test_ac_6_unknown_flag_exits_2_without_echo(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"plain.md": b"plain\n"})
    code, output = _run(tmp_path, repo, f"--bogus-{MARK}")
    assert code == 2
    assert MARK not in output


@pytest.mark.parametrize("name", ["plain", "absent"])
def test_ac_6_repo_that_is_not_a_repo_exits_2(tmp_path: Path, name: str) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    target = tmp_path / f"{name}-{MARK}"
    if name == "plain":
        target.mkdir()
    code, output = _cli(
        tmp_path, "--repo", str(target), "--home", HOME, "--allowlist", str(_allowlist(tmp_path))
    )
    assert code == 2
    assert MARK not in output


@pytest.mark.parametrize("home", ["C:\\", "/home"])
def test_ac_6_short_home_exits_2(tmp_path: Path, home: str) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"plain.md": b"plain\n"})
    code, output = _run(tmp_path, repo, home=home)
    assert code == 2
    assert home not in output, "the output echoes --home"


# --- AC-7: a POSIX home ----------------------------------------------------------------------


def test_ac_7_posix_home_is_case_sensitive(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    lines = [
        "/home/fixture/a",
        "it ran in /home/fixture.",
        "/home/fixtures/a",
        "/home/fixture.other/a",
        "/home/fixture-other/a",
        "/home/Fixture/a",
        "C:\\Users\\fixture\\a",
    ]
    repo = _repo(tmp_path, {"posix.txt": ("\n".join(lines) + "\n").encode()})
    code, output = _run(tmp_path, repo, home=POSIX_HOME)
    assert code == 1
    assert _found(output) == ["posix.txt:1", "posix.txt:2"]


# --- AC-22: encodings ------------------------------------------------------------------------

AC22_KINDS = ("utf8-bom", "utf16le-bom", "utf16be-bom", "utf32le-bom", "utf16le", "utf32be")
EOLS = {"lf": "\n", "crlf": "\r\n"}


def test_ac_22_each_encoding_finds_line_3(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    files = {}
    for kind in AC22_KINDS:
        for eol_name, eol in EOLS.items():
            text = eol.join(["first", "second", "C:\\Users\\fixture\\a", "fourth"]) + eol
            files[f"enc-{kind}-{eol_name}.txt"] = _encode(text, kind)
    repo = _repo(tmp_path, files)
    code, output = _run(tmp_path, repo)
    assert code == 1
    assert sorted(_found(output)) == sorted(f"{name}:3" for name in files)


def test_ac_22_unmarked_utf16_with_cjk_text_is_found(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    files = {}
    for kind in ("utf16le", "utf16be"):
        for eol_name, eol in EOLS.items():
            text = eol.join(
                ["\u65e5\u672c\u8a9e\u306e\u8a18\u9332", "second", "C:/Users/fixture/a"]
            )
            files[f"r2-{kind}-{eol_name}.txt"] = _encode(text, kind)
    repo = _repo(tmp_path, files)
    code, output = _run(tmp_path, repo)
    assert code == 1
    assert sorted(_found(output)) == sorted(f"{name}:3" for name in files)


def test_ac_22_binary_with_nul_and_no_path_passes(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo = _repo(tmp_path, {"image.png": PNG_SIGNATURE + PNG_HEAD + PNG_TAIL})
    code, output = _run(tmp_path, repo)
    assert code == 0
    assert _lines(output) == [f"{PREFIX} ok files=1 allowlisted=0 nul=1"]


def test_ac_22_binary_with_ascii_path_is_found(tmp_path: Path) -> None:
    # The signature holds two LFs and the head ends with a third, so the path is on line 4.
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    raw = PNG_SIGNATURE + PNG_HEAD + b"\n" + b"C:\\Users\\fixture\\a\x00\x00" + PNG_TAIL
    assert raw.count(b"\n") == 3
    repo = _repo(tmp_path, {"image.png": raw})
    code, output = _run(tmp_path, repo)
    assert code == 1
    assert _found(output) == ["image.png:4"]


def test_ac_22_broken_utf16_gives_no_traceback(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    odd = codecs.BOM_UTF16_LE + "abc\n".encode("utf-16-le") + b"\x41"
    unpaired = codecs.BOM_UTF16_LE + b"\x00\xd8" + "x\n".encode("utf-16-le")
    repo = _repo(tmp_path, {"odd.txt": odd, "unpaired.txt": unpaired})
    code, output = _run(tmp_path, repo)
    assert code == 0
    assert _lines(output) == [f"{PREFIX} ok files=2 allowlisted=0 nul=0"]


# --- AC-23: digest binding and --prune -------------------------------------------------------

EVIDENCE = "evidence/review.md"
ORIGINAL = b"# Review\r\nran in C:\\Users\\fixture\\work\r\nverdict " + MARK.encode() + b"\r\n"
SIBLING = b"sibling evidence C:/Users/fixture/x\n"
HEADER = (
    b"# Test allow-list (D-817, D-997). A new entry or digest needs an HDP decision.\n"
    b"# Remove a stale entry with check_home_path.py --prune.\n"
    b"\n"
)
SIBLING_LINE = f"{_digest(SIBLING)}  evidence/aaa.md\n".encode()
EVIDENCE_LINE = f"{_digest(ORIGINAL)}  {EVIDENCE}\n".encode()

#: case -> (the evidence file's new bytes, expected exit, expected outcome lines)
AC23 = {
    "unchanged": (ORIGINAL, 0, [f"{PREFIX} ok files=2 allowlisted=2 nul=0"]),
    "appended": (
        ORIGINAL + b"again C:\\Users\\fixture\\b " + MARK.encode() + b"\r\n",
        1,
        [f"{PREFIX} changed {EVIDENCE}", f"{PREFIX} refused found=0 changed=1 stale=0"],
    ),
    "byte-edit": (
        ORIGINAL.replace(b"verdict", b"Verdict"),
        1,
        [f"{PREFIX} changed {EVIDENCE}", f"{PREFIX} refused found=0 changed=1 stale=0"],
    ),
    "crlf-to-lf": (
        ORIGINAL.replace(b"\r\n", b"\n"),
        0,
        [f"{PREFIX} ok files=2 allowlisted=2 nul=0"],
    ),
    "removed": (
        b"# Review\r\nran in ~\\work\r\nverdict " + MARK.encode() + b"\r\n",
        1,
        [f"{PREFIX} stale {EVIDENCE}", f"{PREFIX} refused found=0 changed=0 stale=1"],
    ),
}


def _evidence_repo(tmp_path: Path, raw: bytes) -> tuple[Path, Path, bytes]:
    repo = _repo(tmp_path, {"evidence/aaa.md": SIBLING, EVIDENCE: raw})
    before = HEADER + SIBLING_LINE + EVIDENCE_LINE
    return repo, _allowlist(tmp_path, before), before


@pytest.mark.parametrize("case", sorted(AC23))
def test_ac_23_listed_file_is_bound_to_its_digest(tmp_path: Path, case: str) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    raw, want_code, want_lines = AC23[case]
    repo, allow, before = _evidence_repo(tmp_path, raw)
    code, output = _run(tmp_path, repo, allowlist=allow)
    assert code == want_code, f"{case}: exit {code}"
    assert _lines(output) == want_lines
    assert _found(output) == []
    assert MARK not in output, "the output holds a scanned line's text"
    assert allow.read_bytes() == before, "the check changed the allow-list"


def test_ac_23_prune_removes_only_the_stale_entry(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo, allow, _ = _evidence_repo(tmp_path, AC23["removed"][0])
    code, output = _run(tmp_path, repo, "--prune", allowlist=allow)
    assert code == 0
    assert allow.read_bytes() == HEADER + SIBLING_LINE
    assert _lines(output)[-1] == f"{PREFIX} ok files=2 allowlisted=1 nul=0"


def test_ac_23_prune_keeps_a_changed_entry(tmp_path: Path) -> None:
    assert CHECK.is_file(), "missing tools/check_home_path.py"
    repo, allow, before = _evidence_repo(tmp_path, AC23["appended"][0])
    code, output = _run(tmp_path, repo, "--prune", allowlist=allow)
    assert code == 1
    assert allow.read_bytes() == before
    assert f"{PREFIX} changed {EVIDENCE}" in _lines(output)
