"""MEU-110 release metadata contract: AC-110.1 to AC-110.4, AC-110.8's builder entry, AC-110.9."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_CONFIG = REPO_ROOT / "ui" / "electron-builder.yml"
LICENSE_FILE = REPO_ROOT / "LICENSE"
NOTICES = REPO_ROOT / "packaging" / "THIRD_PARTY_NOTICES.md"
README = REPO_ROOT / "README.md"
REPO_URL = "https://github.com/matbanik/av-kit"
NPM_MANIFESTS = ("ui/package.json", "mcp-server/package.json")
PY_MANIFESTS = (
    "pyproject.toml",
    "packages/api/pyproject.toml",
    "packages/core/pyproject.toml",
    "packages/infrastructure/pyproject.toml",
)
INSTALLER_NAME = "${productName}-Setup-${version}.${ext}"
RC_NPM = "0.1.0-rc.3"
RC_PY = "0.1.0rc3"
NPM_LOCKS = ("ui/package-lock.json", "mcp-server/package-lock.json")
UV_MEMBERS = ("av-kit", "avkit-api", "avkit-core", "avkit-infra")


def _builder() -> dict[str, object]:
    return yaml.safe_load(BUILD_CONFIG.read_text(encoding="utf-8"))


def _resource(to: str) -> dict[str, object]:
    """The extraResources entry installed at ``to``, or empty when there is none."""
    entries = _builder()["extraResources"]
    assert isinstance(entries, list)
    found = [entry for entry in entries if entry.get("to") == to]
    assert len(found) <= 1, f"{to} is installed by {len(found)} entries"
    return found[0] if found else {}


def _npm(relative: str) -> dict[str, object]:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


def _readme_words() -> str:
    return " ".join(README.read_text(encoding="utf-8").split())


@pytest.mark.parametrize("ac_id", ["AC-110.1"], ids=["AC-110.1"])
def test_licence_file_is_mit(ac_id: str) -> None:
    assert ac_id == "AC-110.1"
    text = LICENSE_FILE.read_text(encoding="utf-8")
    assert text.startswith("MIT License")
    assert "Mat Banik" in text


@pytest.mark.parametrize("ac_id", ["AC-110.1"], ids=["AC-110.1"])
def test_builder_installs_licence(ac_id: str) -> None:
    assert ac_id == "AC-110.1"
    assert _resource("LICENSE").get("from") == "../LICENSE"


@pytest.mark.parametrize("ac_id", ["AC-110.1"], ids=["AC-110.1"])
def test_npm_manifests_declare_mit(ac_id: str) -> None:
    assert ac_id == "AC-110.1"
    declared = {name: _npm(name).get("license") for name in NPM_MANIFESTS}
    assert declared == dict.fromkeys(NPM_MANIFESTS, "MIT")


@pytest.mark.parametrize("ac_id", ["AC-110.1"], ids=["AC-110.1"])
def test_python_manifests_declare_mit(ac_id: str) -> None:
    assert ac_id == "AC-110.1"
    declared = {
        name: tomllib.loads((REPO_ROOT / name).read_text(encoding="utf-8"))["project"].get(
            "license"
        )
        for name in PY_MANIFESTS
    }
    assert declared == dict.fromkeys(PY_MANIFESTS, "MIT")


@pytest.mark.parametrize("ac_id", ["AC-110.1"], ids=["AC-110.1"])
def test_ui_manifest_identifies_project(ac_id: str) -> None:
    """These fields feed the installer's file properties, which a user sees."""
    assert ac_id == "AC-110.1"
    manifest = _npm("ui/package.json")
    assert "MEU" not in str(manifest.get("description"))
    # Mat, 2026-11-09: "can we change the publisher in the installer to focalia.ai?" The author
    # is the installer's Publisher and the exe's CompanyName.
    assert manifest.get("author") == "focalia.ai"
    assert manifest.get("homepage") == REPO_URL
    assert REPO_URL in str(manifest.get("repository"))


@pytest.mark.parametrize("ac_id", ["AC-110.1"], ids=["AC-110.1"])
def test_exe_copyright_names_the_licence_holder(ac_id: str) -> None:
    """electron-builder's default copyright names the author; the licence holder stays Mat Banik."""
    assert ac_id == "AC-110.1"
    config = (REPO_ROOT / "ui/electron-builder.yml").read_text(encoding="utf-8")
    lines = config.splitlines()
    assert "copyright: Copyright © 2026 Mat Banik" in lines
    assert "Copyright (c) 2026 Mat Banik" in LICENSE_FILE.read_text(encoding="utf-8")


@pytest.mark.parametrize("ac_id", ["AC-110.2"], ids=["AC-110.2"])
def test_readme_states_licence(ac_id: str) -> None:
    assert ac_id == "AC-110.2"
    words = _readme_words()
    assert "[MIT License](LICENSE)" in words
    assert "Bundled components keep their own licenses" in words


@pytest.mark.parametrize("ac_id", ["AC-110.2"], ids=["AC-110.2"])
def test_readme_links_reach_prereleases(ac_id: str) -> None:
    """GitHub's /releases/latest skips prereleases, so a link to it would miss the RC."""
    assert ac_id == "AC-110.2"
    links = re.findall(
        re.escape(REPO_URL) + r"/releases[^\s)\"]*", README.read_text(encoding="utf-8")
    )
    assert links
    assert [link for link in links if "latest" in link] == []


@pytest.mark.parametrize("ac_id", ["AC-110.3"], ids=["AC-110.3"])
def test_ffmpeg_entry_filters_zips(ac_id: str) -> None:
    assert ac_id == "AC-110.3"
    entry = _resource("ffmpeg")
    assert entry.get("from") == "../packaging/ffmpeg-win64"
    assert "!*.zip" in (entry.get("filter") or [])


@pytest.mark.parametrize("ac_id", ["AC-110.4"], ids=["AC-110.4"])
def test_installer_name_has_no_spaces(ac_id: str) -> None:
    """GitHub rewrites a space in an asset name, so the built name would differ from the link."""
    assert ac_id == "AC-110.4"
    nsis = _builder()["nsis"]
    assert isinstance(nsis, dict)
    assert nsis.get("artifactName") == INSTALLER_NAME


@pytest.mark.parametrize("ac_id", ["AC-110.4"], ids=["AC-110.4"])
def test_readme_names_built_installer(ac_id: str) -> None:
    assert ac_id == "AC-110.4"
    text = README.read_text(encoding="utf-8")
    assert "av-kit Setup" not in text
    assert text.count("av-kit-Setup-<version>.exe") == 2


@pytest.mark.parametrize("ac_id", ["AC-110.8"], ids=["AC-110.8"])
def test_builder_installs_generated_list(ac_id: str) -> None:
    assert ac_id == "AC-110.8"
    entry = _resource("THIRD_PARTY_LICENSES.txt")
    assert entry.get("from") == "../packaging/dist/THIRD_PARTY_LICENSES.txt"


@pytest.mark.parametrize("ac_id", ["AC-110.8"], ids=["AC-110.8"])
def test_notices_point_at_generated_list(ac_id: str) -> None:
    assert ac_id == "AC-110.8"
    assert "THIRD_PARTY_LICENSES.txt" in NOTICES.read_text(encoding="utf-8")


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_npm_manifests_carry_version(ac_id: str) -> None:
    assert ac_id == "AC-110.9"
    found = {name: _npm(name).get("version") for name in NPM_MANIFESTS}
    assert found == dict.fromkeys(NPM_MANIFESTS, RC_NPM)


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_npm_locks_carry_version(ac_id: str) -> None:
    assert ac_id == "AC-110.9"
    locks = {name: _npm(name) for name in NPM_LOCKS}
    found = {
        name: (lock["version"], lock["packages"][""]["version"]) for name, lock in locks.items()
    }
    assert found == dict.fromkeys(NPM_LOCKS, (RC_NPM, RC_NPM))


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_mcp_server_reports_version(ac_id: str) -> None:
    assert ac_id == "AC-110.9"
    text = (REPO_ROOT / "mcp-server" / "src" / "index.ts").read_text(encoding="utf-8")
    assert f'{{ name: "av-kit", version: "{RC_NPM}" }}' in text


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_python_manifests_carry_version(ac_id: str) -> None:
    assert ac_id == "AC-110.9"
    found = {
        name: tomllib.loads((REPO_ROOT / name).read_text(encoding="utf-8"))["project"]["version"]
        for name in PY_MANIFESTS
    }
    assert found == dict.fromkeys(PY_MANIFESTS, RC_PY)


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_api_package_carries_version(ac_id: str) -> None:
    from avkit_api import __version__

    assert ac_id == "AC-110.9"
    assert __version__ == RC_PY


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_uv_lock_carries_version(ac_id: str) -> None:
    assert ac_id == "AC-110.9"
    lock = tomllib.loads((REPO_ROOT / "uv.lock").read_text(encoding="utf-8"))
    found = {
        package["name"]: package["version"]
        for package in lock["package"]
        if {"editable", "virtual"} & set(package["source"])
    }
    assert found == dict.fromkeys(UV_MEMBERS, RC_PY)


@pytest.mark.parametrize("ac_id", ["AC-110.9"], ids=["AC-110.9"])
def test_openapi_carries_version(ac_id: str) -> None:
    assert ac_id == "AC-110.9"
    assert _npm("openapi.committed.json")["info"]["version"] == RC_PY
