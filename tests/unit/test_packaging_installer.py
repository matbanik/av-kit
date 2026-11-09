"""MEU-25 installer contract — AC-25.1, 25.2, 25.3, 25.6–25.10."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_CONFIG = REPO_ROOT / "ui" / "electron-builder.yml"
MCP_SNIPPET = REPO_ROOT / "docs" / "distribution" / "mcp.json.example"
SPAWN_TEST = REPO_ROOT / "ui" / "tests" / "unit" / "dev-spawn.test.ts"
MCP_TEST = REPO_ROOT / "ui" / "tests" / "unit" / "copy-mcp-config.test.ts"
PACK_DIST_DIR = "packaging/dist/avkit-backend"


def _yml() -> str:
    assert BUILD_CONFIG.is_file(), f"missing BUILD_CONFIG {BUILD_CONFIG}"
    return BUILD_CONFIG.read_text(encoding="utf-8")


@pytest.mark.parametrize("ac_id", ["AC-25.1"], ids=["AC-25.1"])
def test_nsis_target(ac_id: str) -> None:
    """AC-25.1 NSIS_TARGET win nsis x64."""
    assert ac_id == "AC-25.1"
    text = _yml()
    assert "nsis" in text
    assert "x64" in text


@pytest.mark.parametrize("ac_id", ["AC-25.2"], ids=["AC-25.2"])
def test_extra_resources_from_dir(ac_id: str) -> None:
    """AC-25.2 EXTRA_RESOURCES from PACK_DIST_DIR, not exe-only."""
    assert ac_id == "AC-25.2"
    text = _yml()
    assert "to: avkit-backend" in text or "to: avkit-backend" in text.replace('"', "")
    assert PACK_DIST_DIR.replace("\\", "/") in text.replace("\\", "/")
    assert "extra/avkit-backend" not in text
    from_block = text.split("from:")[1].split("to:")[0] if "from:" in text else ""
    assert "avkit-backend.exe" not in from_block


@pytest.mark.parametrize("ac_id", ["AC-25.3"], ids=["AC-25.3"])
def test_resources_backend_vitest_scheduled(ac_id: str) -> None:
    """AC-25.3 RESOURCES_BACKEND parity is scheduled in VITEST_MEU25."""
    assert ac_id == "AC-25.3"
    body = SPAWN_TEST.read_text(encoding="utf-8")
    assert "AC-25.3" in body
    assert "packagedBackendPath" in body
    assert "extra/" in body


@pytest.mark.parametrize("ac_id", ["AC-25.6"], ids=["AC-25.6"])
def test_nsis_keep_appdata(ac_id: str) -> None:
    """AC-25.6 NSIS_KEEP_APPDATA deleteAppDataOnUninstall false."""
    assert ac_id == "AC-25.6"
    text = _yml()
    assert "deleteAppDataOnUninstall" in text
    assert "false" in text


@pytest.mark.parametrize("ac_id", ["AC-25.7"], ids=["AC-25.7"])
def test_mcp_snippet_keys(ac_id: str) -> None:
    """AC-25.7 MCP_SNIPPET names the app data folder, with no token or API base."""
    assert ac_id == "AC-25.7"
    assert MCP_SNIPPET.is_file()
    text = MCP_SNIPPET.read_text(encoding="utf-8")
    assert "AVKIT_API_TOKEN" not in text
    assert "AVKIT_APP_DATA" in text
    assert "AVKIT_API_BASE" not in text


@pytest.mark.parametrize("ac_id", ["AC-25.8"], ids=["AC-25.8"])
def test_mcp_copy_default_vitest_scheduled(ac_id: str) -> None:
    """AC-25.8 MCP_COPY_DEFAULT scheduled in copy-mcp-config.test.ts."""
    assert ac_id == "AC-25.8"
    body = MCP_TEST.read_text(encoding="utf-8")
    assert "AC-25.8" in body
    assert "pinEndpoint: false" in body


@pytest.mark.parametrize("ac_id", ["AC-25.9"], ids=["AC-25.9"])
def test_no_torch_in_builder(ac_id: str) -> None:
    """AC-25.9 NO_TORCH_NSIS extraResources do not ship weights."""
    assert ac_id == "AC-25.9"
    text = _yml()
    assert ".onnx" not in text
    assert ".pth" not in text
    assert "cuda" not in text.lower()


@pytest.mark.parametrize("ac_id", ["AC-25.10"], ids=["AC-25.10"])
def test_nsis_pack_check_script(ac_id: str) -> None:
    """AC-25.10 NSIS_PACK_CHECK script exists and fail-closes missing artifacts."""
    assert ac_id == "AC-25.10"
    script = (
        REPO_ROOT
        / "docs"
        / "execution"
        / "plans"
        / "2026-08-24-p7-distribution"
        / "assert-nsis-pack.ps1"
    )
    text = script.read_text(encoding="utf-8")
    assert "SIZE_CAP" in text or "SIZE_CAP_BYTES" in text
    assert "exit 1" in text
    assert "never" in text.lower() or "FAIL" in text
    fetch = REPO_ROOT / "tools" / "fetch_ffmpeg_windows.ps1"
    assert fetch.is_file(), "FETCH_FFMPEG missing"
    ffmpeg = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg.exe"
    ffprobe = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffprobe.exe"
    assert ffmpeg.is_file() and ffprobe.is_file()
    assert ffmpeg.stat().st_size > 1024, "ffmpeg.exe is a layout stub"
    assert ffprobe.stat().st_size > 1024, "ffprobe.exe is a layout stub"


def _run_fetch(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    script = REPO_ROOT / "tools" / "fetch_ffmpeg_windows.ps1"
    return subprocess.run(
        [
            "pwsh",
            "-NoProfile",
            "-File",
            str(script),
            *args,
        ],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def test_fetch_ffmpeg_rejects_blank_sha(tmp_path: Path) -> None:
    """F2: FETCH_FFMPEG must reject a blank SHA256 before extract."""
    archive = tmp_path / "ffmpeg-pin.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("ffmpeg.exe", "not-a-binary")
        zf.writestr("ffprobe.exe", "not-a-binary")
    result = _run_fetch(
        "-OutDir",
        str(tmp_path),
        "-Url",
        "https://example.invalid/ffmpeg.zip",
        "-Sha256",
        "",
        "-ExtractOnly",
        cwd=tmp_path,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "PASS: FETCH_FFMPEG" not in (result.stdout + result.stderr)


def test_fetch_ffmpeg_rejects_sha_mismatch(tmp_path: Path) -> None:
    """F2: FETCH_FFMPEG must compare SHA256 before copying binaries."""
    archive = tmp_path / "ffmpeg-pin.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("ffmpeg.exe", "not-a-binary")
        zf.writestr("ffprobe.exe", "not-a-binary")
    result = _run_fetch(
        "-OutDir",
        str(tmp_path),
        "-Url",
        "https://example.invalid/ffmpeg.zip",
        "-Sha256",
        "0" * 64,
        "-ExtractOnly",
        cwd=tmp_path,
    )
    assert result.returncode == 3, result.stdout + result.stderr
    assert "PASS: FETCH_FFMPEG" not in (result.stdout + result.stderr)


# --- MEU-72 AC-72.7 NOTICES and the FFmpeg LICENSE.txt ----------------------------------------

NOTICES_FILE = REPO_ROOT / "packaging" / "THIRD_PARTY_NOTICES.md"
NOTICES_COMPONENTS_72 = {
    "misaki": "Apache-2.0",
    "num2words": "LGPL-2.1",
    "spaCy": "MIT",
    "onnxruntime": "MIT",
    "Kokoro": "Apache-2.0",
    "FFmpeg": "GPL-3.0",
}


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


def _section(sections: dict[str, str], component: str) -> str:
    hits = [body for title, body in sections.items() if component.lower() in title.lower()]
    assert len(hits) == 1, f"one `## {component}` section expected, got {len(hits)}"
    return hits[0]


def test_ac_72_7_third_party_notices() -> None:
    """AC-72.7 NOTICES: six components, licences, LGPL text, FFmpeg source, no espeak-ng."""
    from importlib.metadata import distribution

    assert NOTICES_FILE.is_file(), f"missing {NOTICES_FILE}"
    text = NOTICES_FILE.read_text(encoding="utf-8")
    sections = _notice_sections(text)
    for component, licence in NOTICES_COMPONENTS_72.items():
        body = _section(sections, component)
        assert licence in body, component
        assert "https://" in body, component
    assert "MULTI_E2M" in _section(sections, "misaki")
    assert "EN_E2M" in _section(sections, "misaki")
    assert "replace" in _section(sections, "num2words").lower()
    assert "not shipped" in _section(sections, "Kokoro").lower()
    ffmpeg = _section(sections, "FFmpeg")
    for needle in (
        "n8.1.3-27-g8dca1586f4",
        "8dca1586f468bfcbb78ae3ed618af1361d9f140a",
        "autobuild-2026-10-31-12-59",
        "https://github.com/BtbN/FFmpeg-Builds",
        "av-kit-0.1.0-rc.1-ffmpeg-source.tar.xz",
        "https://github.com/matbanik/av-kit/releases/tag/v0.1.0-rc.2",
        "resources/ffmpeg/LICENSE.txt",
        "ffmpeg.exe",
        "ffprobe.exe",
        "libdvdcss",
        "av-kit never uses DVD input",
    ):
        assert needle in ffmpeg, needle
    assert any(
        "espeak-ng" in line.lower() and "not shipped" in line.lower() for line in text.splitlines()
    )
    copying = distribution("num2words").read_text("COPYING")
    assert copying
    assert " ".join(copying.split()) in " ".join(text.split())
    builder = _yml().replace('"', "")
    assert "from: ../packaging/THIRD_PARTY_NOTICES.md" in builder
    assert "to: THIRD_PARTY_NOTICES.md" in builder


def _ffmpeg_zip(archive: Path, *, with_license: bool) -> str:
    import hashlib

    root = "ffmpeg-n8.1.3-27-g8dca1586f4-win64-gpl-8.1"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(f"{root}/bin/ffmpeg.exe", b"M" * 2048)
        zf.writestr(f"{root}/bin/ffprobe.exe", b"P" * 2048)
        if with_license:
            zf.writestr(f"{root}/LICENSE.txt", "GNU GENERAL PUBLIC LICENSE Version 3\n")
    return hashlib.sha256(archive.read_bytes()).hexdigest()


def _fetch_pinned(out_dir: Path, sha: str) -> subprocess.CompletedProcess[str]:
    return _run_fetch(
        "-OutDir",
        str(out_dir),
        "-Url",
        "https://example.invalid/ffmpeg.zip",
        "-Sha256",
        sha,
        "-ExtractOnly",
        cwd=out_dir,
    )


def test_ac_72_7_fetch_ffmpeg_requires_license_txt(tmp_path: Path) -> None:
    """AC-72.7: a pinned archive without LICENSE.txt exits 6."""
    sha = _ffmpeg_zip(tmp_path / "ffmpeg-pin.zip", with_license=False)
    result = _fetch_pinned(tmp_path, sha)
    assert result.returncode == 6, result.stdout + result.stderr
    assert not (tmp_path / "LICENSE.txt").exists()


def test_ac_72_7_fetch_ffmpeg_copies_license_txt(tmp_path: Path) -> None:
    """AC-72.7: LICENSE.txt from the archive lands in -OutDir next to the binaries."""
    sha = _ffmpeg_zip(tmp_path / "ffmpeg-pin.zip", with_license=True)
    result = _fetch_pinned(tmp_path, sha)
    assert result.returncode == 0, result.stdout + result.stderr
    license_txt = tmp_path / "LICENSE.txt"
    assert license_txt.is_file()
    assert "GNU GENERAL PUBLIC LICENSE" in license_txt.read_text(encoding="utf-8")
    assert (tmp_path / "ffmpeg.exe").is_file()
    assert (tmp_path / "ffprobe.exe").is_file()


# --- MEU-113 AC-113.1 to AC-113.5 the fetch script's documented exit codes --------------------

FETCH_SCRIPT = REPO_ROOT / "tools" / "fetch_ffmpeg_windows.ps1"


def _fetch(
    out_dir: Path, *, url: str = "https://example.invalid/ffmpeg.zip", sha: str
) -> subprocess.CompletedProcess[str]:
    return _run_fetch(
        "-OutDir", str(out_dir), "-Url", url, "-Sha256", sha, "-ExtractOnly", cwd=out_dir
    )


def _zip(archive: Path, members: dict[str, bytes]) -> str:
    import hashlib

    with zipfile.ZipFile(archive, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)
    return hashlib.sha256(archive.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("blank-url", "requires a pinned URL"),
        ("malformed-sha", "requires a nonempty 64-hex SHA256"),
        ("missing-archive", "missing archive"),
    ],
    ids=["blank-url", "malformed-sha", "missing-archive"],
)
def test_ac_113_1_fetch_exits_2_with_message_on_stderr(
    tmp_path: Path, case: str, message: str
) -> None:
    """AC-113.1: a blank URL, a malformed SHA and a missing archive exit 2, message on stderr."""
    if case == "blank-url":
        result = _fetch(tmp_path, url="", sha="0" * 64)
    elif case == "malformed-sha":
        result = _fetch(tmp_path, sha="not-hex")
    else:
        result = _fetch(tmp_path, sha="0" * 64)
    assert result.returncode == 2, result.stdout + result.stderr
    assert message in result.stderr


def test_ac_113_2_fetch_exits_3_on_sha_mismatch(tmp_path: Path) -> None:
    """AC-113.2: a SHA-256 mismatch exits 3."""
    _zip(tmp_path / "ffmpeg-pin.zip", {"ffmpeg.exe": b"M" * 2048, "ffprobe.exe": b"P" * 2048})
    result = _fetch(tmp_path, sha="0" * 64)
    assert result.returncode == 3, result.stdout + result.stderr
    assert "SHA256 mismatch" in result.stderr


def test_ac_113_3_fetch_exits_4_without_both_binaries(tmp_path: Path) -> None:
    """AC-113.3: an archive with no ffmpeg.exe exits 4."""
    sha = _zip(tmp_path / "ffmpeg-pin.zip", {"bin/ffprobe.exe": b"P" * 2048, "LICENSE.txt": b"GPL"})
    result = _fetch(tmp_path, sha=sha)
    assert result.returncode == 4, result.stdout + result.stderr
    assert "archive missing ffmpeg.exe or ffprobe.exe" in result.stderr


def test_ac_113_4_fetch_exits_5_on_stub_binary(tmp_path: Path) -> None:
    """AC-113.4: a 1024 B ffmpeg.exe exits 5.

    Both binaries and LICENSE.txt are present, because exit 6 is checked first.
    """
    sha = _zip(
        tmp_path / "ffmpeg-pin.zip",
        {"bin/ffmpeg.exe": b"M" * 1024, "bin/ffprobe.exe": b"P" * 2048, "LICENSE.txt": b"GPL"},
    )
    result = _fetch(tmp_path, sha=sha)
    assert result.returncode == 5, result.stdout + result.stderr
    assert "refusing stub payload" in result.stderr


def test_ac_113_5_fetch_script_has_no_write_error() -> None:
    """AC-113.5: no Write-Error is left in the script, comments included."""
    assert "Write-Error" not in FETCH_SCRIPT.read_text(encoding="utf-8")
