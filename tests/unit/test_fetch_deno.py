"""MEU-141 packaging: the solver (`SOLVER_DEP`, `SOLVER_SPEC`), Deno's bundle and licence
(`DENO_BUNDLE`, `DENO_LICENCE`) and the onedir smoke's verdict (`RUNTIME_SMOKE`).

The fetch script runs offline with `-ExtractOnly` on fixture files; nothing reaches the network.
Every check asserts a file or name exists before reading it, so a failure is an assertion.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.metadata as md
import re
import subprocess
import zipfile
from pathlib import Path

import pytest
import yaml
from tests.unit.test_generate_third_party_licenses import GPL_FIELDS, _Fixture
from tests.unit.test_packaging_backend import SPEC_FILE, _calls_named, _first_str_arg

REPO_ROOT = Path(__file__).resolve().parents[2]
FETCH_SCRIPT = REPO_ROOT / "tools" / "fetch_deno_windows.ps1"
BUILD_CONFIG = REPO_ROOT / "ui" / "electron-builder.yml"
NOTICES = REPO_ROOT / "packaging" / "THIRD_PARTY_NOTICES.md"
DENO_VERSION = "2.9.8"
DENO_SOURCE = "https://github.com/denoland/deno"
LICENCE_TEXT = b"MIT License\n\nCopyright 2018-2026 the Deno authors\n"
PIN_RE = re.compile(r"^yt-dlp-ejs\s*==\s*([^;\s]+)\s*;\s*extra\s*==\s*['\"]default['\"]\s*$")


# --- AC-141.11: SOLVER_DEP (guard) ----------------------------------------------------------------


def _default_extra_pin(requirements: list[str]) -> str | None:
    """The `yt-dlp-ejs` version yt-dlp's `default` extra pins, or None when it pins none."""
    pins = [m.group(1) for line in requirements if (m := PIN_RE.match(line.strip()))]
    return pins[0] if len(pins) == 1 else None


def _pin_problem(requirements: list[str], installed: str) -> str | None:
    """Why the installed solver is not the one the requirement list pins, or None."""
    pinned = _default_extra_pin(requirements)
    if pinned is None:
        return "yt-dlp's default extra pins no single yt-dlp-ejs version"
    if pinned != installed:
        return f"yt-dlp-ejs {installed} is installed, the default extra pins {pinned}"
    return None


def test_ac_141_11_solver_imports_at_the_pinned_version() -> None:
    import yt_dlp_ejs

    assert yt_dlp_ejs.__name__ == "yt_dlp_ejs"
    requirements = md.requires("yt-dlp") or []
    installed = md.version("yt-dlp-ejs")
    assert _pin_problem(requirements, installed) is None


def test_ac_141_11_pin_reader_refuses_a_differing_pin_neg() -> None:
    installed = md.version("yt-dlp-ejs")
    fixture = [
        "requests",
        "yt-dlp-ejs==0.0.1; extra == 'default'",
        "yt-dlp-ejs==0.0.1; extra == 'pin'",
    ]
    assert (
        _pin_problem(fixture, installed)
        == f"yt-dlp-ejs {installed} is installed, the default extra pins 0.0.1"
    )
    assert _pin_problem(["requests"], installed) is not None


# --- AC-141.12: SOLVER_SPEC and the smoke verdict -------------------------------------------------


def _assigned(tree: ast.Module, name: str) -> ast.expr:
    values = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
    ]
    assert len(values) == 1, (name, len(values))
    return values[0]


def test_ac_141_12_spec_collects_the_solver() -> None:
    assert SPEC_FILE.is_file()
    tree = ast.parse(SPEC_FILE.read_text(encoding="utf-8"))
    hidden = _assigned(tree, "hiddenimports")
    datas = _assigned(tree, "datas")
    hidden_strings = [n.value for n in ast.walk(hidden) if isinstance(n, ast.Constant)]
    assert "yt_dlp_ejs" in hidden_strings
    submodules = [_first_str_arg(c) for c in _calls_named(hidden, "collect_submodules")]
    assert "yt_dlp_ejs" in submodules
    collected = [_first_str_arg(c) for c in _calls_named(datas, "collect_data_files")]
    assert "yt_dlp_ejs" in collected


VERDICTS = [
    pytest.param({}, "js_runtime", id="no_field"),
    pytest.param({"js_runtime": None}, "js_runtime", id="null_field"),
    pytest.param({"js_runtime": {"available": False}}, "js_runtime.available", id="unavailable"),
    pytest.param(
        {"js_runtime": {"available": True, "source": "path", "version": "2.9.8", "solver": True}},
        "js_runtime.source",
        id="from_path",
    ),
    pytest.param(
        {"js_runtime": {"available": True, "source": "bundled", "version": None, "solver": True}},
        "js_runtime.version",
        id="no_version",
    ),
    pytest.param(
        {"js_runtime": {"available": True, "source": "bundled", "version": "2.9", "solver": True}},
        "js_runtime.version",
        id="short_version",
    ),
    pytest.param(
        {
            "js_runtime": {
                "available": True,
                "source": "bundled",
                "version": "2.9.8",
                "solver": False,
            }
        },
        "js_runtime.solver",
        id="no_solver",
    ),
    pytest.param(
        {
            "js_runtime": {
                "available": True,
                "source": "bundled",
                "version": "2.9.8",
                "solver": True,
            }
        },
        None,
        id="all_hold",
    ),
]


@pytest.mark.parametrize(("body", "missing"), VERDICTS)
def test_ac_141_12_smoke_names_the_first_missing_field(
    body: dict[str, object], missing: str | None
) -> None:
    from tools.smoke_packaged_runtime import verdict

    assert verdict(body) == missing


# --- AC-141.13: DENO_LICENCE and DENO_BUNDLE ------------------------------------------------------


def test_ac_141_13_other_lists_names_the_deno_licence() -> None:
    from tools import generate_third_party_licenses

    assert "  resources/deno/LICENSE.md: Deno\n" in generate_third_party_licenses.OTHER_LISTS


def _notice_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    heading = ""
    for line in text.splitlines():
        if line.startswith("## "):
            heading = line[3:].strip()
            sections[heading] = ""
        elif heading:
            sections[heading] += line + "\n"
    return sections


def test_ac_141_13_notices_have_the_deno_row() -> None:
    assert NOTICES.is_file()
    sections = _notice_sections(NOTICES.read_text(encoding="utf-8"))
    deno = [body for title, body in sections.items() if title.split()[:1] == ["Deno"]]
    assert len(deno) == 1, sorted(sections)
    for part in ("MIT", DENO_VERSION, DENO_SOURCE, "resources/deno/LICENSE.md"):
        assert part in deno[0], part


def test_ac_141_13_builder_copies_deno_without_the_zip() -> None:
    entries = yaml.safe_load(BUILD_CONFIG.read_text(encoding="utf-8")).get("extraResources")
    assert isinstance(entries, list)
    found = [entry for entry in entries if isinstance(entry, dict) and entry.get("to") == "deno"]
    assert len(found) == 1, len(found)
    assert found[0].get("from") == "../packaging/deno-win64"
    assert "!*.zip" in (found[0].get("filter") or [])


def test_ac_141_13_bundled_deno_is_the_frozen_sibling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import avkit_api.wiring as wiring

    assert hasattr(wiring, "bundled_deno")
    exe = tmp_path / "resources" / "avkit-backend" / "avkit-backend.exe"
    exe.parent.mkdir(parents=True)
    exe.write_bytes(b"MZ")
    monkeypatch.setattr(wiring.sys, "frozen", True, raising=False)
    monkeypatch.setattr(wiring.sys, "executable", str(exe))
    assert wiring.bundled_deno() == (tmp_path / "resources" / "deno" / "deno.exe").resolve()


def test_ac_141_13_bundled_deno_is_none_when_not_frozen(monkeypatch: pytest.MonkeyPatch) -> None:
    import avkit_api.wiring as wiring

    assert hasattr(wiring, "bundled_deno")
    monkeypatch.delattr(wiring.sys, "frozen", raising=False)
    assert wiring.bundled_deno() is None


def test_ac_141_13_generator_still_refuses_gpl_neg(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    fx = _Fixture(tmp_path)
    fx.distribution(
        "copyleft", metadata=GPL_FIELDS["expression"], modules=("copyleft/__init__.py",)
    )
    fx.ship_module("copyleft", fx.site / "copyleft" / "__init__.py")
    assert "copyleft" in fx.refusal(capsys)


# --- AC-141.14: the fetch script, offline ---------------------------------------------------------


def _fixture_files(out_dir: Path, members: dict[str, bytes]) -> tuple[str, str]:
    """`deno-pin.zip` and `LICENSE.md` in `out_dir`; their SHA-256 values."""
    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / "deno-pin.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    (out_dir / "LICENSE.md").write_bytes(LICENCE_TEXT)
    return hashlib.sha256(archive.read_bytes()).hexdigest(), hashlib.sha256(
        LICENCE_TEXT
    ).hexdigest()


def _fetch(
    out_dir: Path, *, url: str = "https://example.invalid/deno.zip", sha: str, licence_sha: str
) -> subprocess.CompletedProcess[str]:
    assert FETCH_SCRIPT.is_file(), f"missing {FETCH_SCRIPT.name}"
    return subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(FETCH_SCRIPT),
            "-OutDir",
            str(out_dir),
            "-Url",
            url,
            "-Sha256",
            sha,
            "-LicenseUrl",
            "https://example.invalid/LICENSE.md",
            "-LicenseSha256",
            licence_sha,
            "-ExtractOnly",
        ],
        cwd=str(out_dir),
        capture_output=True,
        text=True,
        check=False,
    )


def test_ac_141_14_empty_url_exits_2(tmp_path: Path) -> None:
    _sha, licence_sha = _fixture_files(tmp_path, {"deno.exe": b"M" * 2048})
    result = _fetch(tmp_path, url="", sha="0" * 64, licence_sha=licence_sha)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "requires a pinned URL" in result.stderr


def test_ac_141_14_non_hex_sha_exits_2(tmp_path: Path) -> None:
    _sha, licence_sha = _fixture_files(tmp_path, {"deno.exe": b"M" * 2048})
    result = _fetch(tmp_path, sha="not-hex", licence_sha=licence_sha)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "requires a nonempty 64-hex SHA256" in result.stderr


def test_ac_141_14_mismatch_exits_3_without_deno_neg(tmp_path: Path) -> None:
    _sha, licence_sha = _fixture_files(tmp_path, {"deno.exe": b"M" * 2048})
    result = _fetch(tmp_path, sha="0" * 64, licence_sha=licence_sha)
    assert result.returncode == 3, result.stdout + result.stderr
    assert "SHA256 mismatch" in result.stderr
    assert not (tmp_path / "deno.exe").exists()


def test_ac_141_14_licence_mismatch_exits_3(tmp_path: Path) -> None:
    sha, _licence_sha = _fixture_files(tmp_path, {"deno.exe": b"M" * 2048})
    result = _fetch(tmp_path, sha=sha, licence_sha="0" * 64)
    assert result.returncode == 3, result.stdout + result.stderr
    assert not (tmp_path / "deno.exe").exists()


def test_ac_141_14_matching_archive_extracts_deno(tmp_path: Path) -> None:
    sha, licence_sha = _fixture_files(tmp_path, {"deno.exe": b"M" * 2048})
    result = _fetch(tmp_path, sha=sha, licence_sha=licence_sha)
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "deno.exe").read_bytes() == b"M" * 2048
    assert (tmp_path / "LICENSE.md").read_bytes() == LICENCE_TEXT
