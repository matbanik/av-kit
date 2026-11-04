"""MEU-110 licence list: AC-110.5 to AC-110.7, AC-110.17 and AC-110.18 on a fixture build.

The fixture is a complete, clean build. Each refusal test adds one fault and requires exactly
one problem, so a refusal can only come from that fault.
"""

from __future__ import annotations

import importlib.metadata as md
import json
import ssl
from pathlib import Path

import pytest

GPL_FIELDS = {
    "expression": "License-Expression: GPL-3.0-or-later",
    "field": "License: GPLv3+",
    "classifier": "Classifier: License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "lgpl": "Classifier: License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
}
RUNTIME_LIBRARIES = ("libcrypto-3-x64.dll", "libssl-3-x64.dll", "libffi-8.dll", "sqlite3.dll")
WINDOWS_RUNTIME = (
    "api-ms-win-core-file-l1-1-0.dll",
    "ucrtbase.dll",
    "VCRUNTIME140.dll",
    "MSVCP140_1.dll",
)
OVERRIDES = {
    "cpython-incorporated": "CPython incorporated software",
    "openssl": "OpenSSL",
    "libffi": "libffi",
    "sqlite": "SQLite",
    "xz": "xz",
    "expat": "expat",
    "libmpdec": "libmpdec",
    "zlib": "zlib",
    "hacl-star": "HACL*",
}
REPO_ROOT = Path(__file__).resolve().parents[2]


def _tool():
    from tools import generate_third_party_licenses

    return generate_third_party_licenses


def _write(path: Path, text: str = "fixture") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return path


def _override_text(
    component: str, version: str = "1.0", source: str = "https://example.org/x"
) -> str:
    head = f"Component: {component}\nVersion: {version}\nLicence: Example\n"
    if source:
        head += f"Source: {source}\n"
    return f"{head}---\n{component.upper()} UPSTREAM TEXT\n"


class _Fixture:
    def __init__(self, root: Path) -> None:
        self.repo = root / "repo"
        self.site = root / "site"
        self.base = root / "base"
        self.nuget = root / "nuget"
        self.work = self.repo / "packaging" / "build" / "avkit-backend"
        self.dist = self.repo / "packaging" / "dist" / "avkit-backend"
        self.internal = self.dist / "_internal"
        self.overrides = self.repo / "packaging" / "licence-overrides"
        self.out = self.repo / "packaging" / "dist" / "THIRD_PARTY_LICENSES.txt"
        self.collect: list[tuple[str, str, str]] = [
            ("avkit-backend.exe", str(self.work / "avkit-backend.exe"), "EXECUTABLE")
        ]
        self.pyz: list[tuple[str, str, str]] = []
        self.extra_exe_modules: set[str] = set()
        self.dropped_exe_modules: set[str] = set()
        self.runtime_versions: dict[str, str] = {}
        self.lock: dict[str, dict[str, object]] = {"": {"name": "av-kit-ui"}}
        self.deps_libraries: dict[str, dict[str, str]] = {
            "avkit-region-picker/1.0.0": {"type": "project"},
            "runtimepack.Microsoft.NETCore.App.Runtime.win-x64/8.0.1": {"type": "runtimepack"},
            "runtimepack.Microsoft.WindowsDesktop.App.Runtime.win-x64/8.0.1": {
                "type": "runtimepack"
            },
        }
        self._clean_build()

    def distribution(
        self,
        name: str,
        version: str = "1.0",
        metadata: str = "License-Expression: MIT",
        notices: dict[str, str] | None = None,
        modules: tuple[str, ...] = (),
        record_only: tuple[str, ...] = (),
    ) -> None:
        """A dist-info folder with its RECORD; ``record_only`` paths are not on disk."""
        info = f"{name}-{version}.dist-info"
        if notices is None:
            notices = {f"{info}/licenses/LICENSE": f"{name.upper()} LICENCE TEXT"}
        for relative, text in notices.items():
            _write(self.site / relative, text)
        for relative in modules:
            _write(self.site / relative)
        _write(
            self.site / info / "METADATA",
            f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}\n{metadata}\n",
        )
        listed = [*notices, *modules, *record_only, f"{info}/METADATA", f"{info}/RECORD"]
        _write(self.site / info / "RECORD", "".join(f"{relative},,\n" for relative in listed))

    def ship_file(self, dest: str, source: Path | str, kind: str = "BINARY") -> None:
        _write(self.internal / dest)
        self.collect.append((dest, str(source), kind))

    def ship_module(self, name: str, source: Path | str) -> None:
        self.pyz.append((name, str(source), "PYMODULE"))

    def npm_package(
        self, name: str, version: str = "1.0.0", licence: str = "MIT", text: str | None = ""
    ) -> None:
        self.lock[f"node_modules/{name}"] = {"version": version, "license": licence}
        folder = self.repo / "ui" / "node_modules" / name
        folder.mkdir(parents=True, exist_ok=True)
        if text is not None:
            _write(folder / "LICENSE", text or f"{name.upper()} NPM TEXT")

    def _clean_build(self) -> None:
        self.distribution("alpha", modules=("alpha/__init__.py", "alpha/_native.pyd"))
        self.ship_file("alpha/_native.pyd", self.site / "alpha" / "_native.pyd", "EXTENSION")
        self.ship_module("alpha", self.site / "alpha" / "__init__.py")
        self.distribution(
            "pyinstaller",
            notices={"pyinstaller-1.0.dist-info/licenses/COPYING.txt": "BOOTLOADER EXCEPTION"},
        )

        _write(self.base / "LICENSE.txt", "PSF TERMS AND BZIP2")
        self.ship_module("abc", _write(self.base / "Lib" / "abc.py"))
        self.ship_file("_socket.pyd", _write(self.base / "DLLs" / "_socket.pyd"), "EXTENSION")
        for name in ("python3.dll", "python312.dll"):
            self.ship_file(name, _write(self.base / name))
        for name in RUNTIME_LIBRARIES:
            self.ship_file(name, _write(self.base / "DLLs" / name))
        self.ship_file("base_library.zip", _write(self.work / "base_library.zip"), "DATA")

        self.ship_module(
            "avkit_core",
            _write(self.repo / "packages" / "core" / "src" / "avkit_core" / "__init__.py"),
        )
        for name in WINDOWS_RUNTIME:
            self.ship_file(name, Path("C:/jdk/bin") / name)
        for slug, component in OVERRIDES.items():
            _write(self.overrides / f"{slug}.txt", _override_text(component))

        self.npm_package("react")
        self.lock["node_modules/vitest"] = {"version": "5.0.0", "license": "MIT", "dev": True}

        netcore = self.nuget / "microsoft.netcore.app.runtime.win-x64" / "8.0.1"
        _write(netcore / "LICENSE.TXT", "NETCORE LICENCE")
        _write(netcore / "THIRD-PARTY-NOTICES.TXT", "NETCORE NOTICES")
        desktop = self.nuget / "microsoft.windowsdesktop.app.runtime.win-x64" / "8.0.1"
        _write(desktop / "LICENSE", "DESKTOP LICENCE")
        _write(self.dist / "avkit-backend.exe")

    def build(self):
        tool = _tool()
        _write(self.work / "COLLECT-00.toc", f"# fixture\n{(self.collect,)!r}\n")
        _write(self.work / "PYZ-00.toc", f"{(str(self.work / 'PYZ-00.pyz'), self.pyz)!r}\n")
        _write(
            self.repo / "ui" / "package-lock.json",
            json.dumps({"lockfileVersion": 3, "packages": self.lock}),
        )
        publish = self.repo / "native" / "region-picker" / "publish"
        _write(
            publish / "avkit-region-picker.deps.json",
            json.dumps({"libraries": self.deps_libraries}),
        )
        real_modules = {name for name, _, _ in self.pyz}
        modules = (real_modules | self.extra_exe_modules) - self.dropped_exe_modules
        return tool.Build(
            work_dir=self.work,
            dist_dir=self.dist,
            repo_root=self.repo,
            base_prefix=self.base,
            nuget_root=self.nuget,
            distributions=lambda: md.distributions(path=[str(self.site)]),
            read_exe_modules=lambda _exe: modules,
            runtime_versions=self.runtime_versions,
            python_version="3.12.12",
        )

    def listed(self) -> str:
        """The written list; a refusal here fails the test with the problems it printed."""
        code = _tool().write_list(self.build(), self.out)
        assert code == 0
        return self.out.read_text(encoding="utf-8")

    def refusal(self, capsys: pytest.CaptureFixture[str]) -> str:
        """The one problem this build is refused for; more than one means the fixture is wrong."""
        code = _tool().write_list(self.build(), self.out)
        problems = capsys.readouterr().err.strip().splitlines()
        assert code == 1
        assert len(problems) == 1, problems
        return problems[0]


@pytest.fixture
def fx(tmp_path: Path) -> _Fixture:
    return _Fixture(tmp_path)


# AC-110.5: what shipped is listed, with its full text.


@pytest.mark.parametrize("ac_id", ["AC-110.5"], ids=["AC-110.5"])
def test_owner_listed_with_version_and_text(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.5"
    text = fx.listed()
    assert "alpha 1.0" in text
    assert "Licence: MIT" in text
    assert "ALPHA LICENCE TEXT" in text


@pytest.mark.parametrize("ac_id", ["AC-110.5"], ids=["AC-110.5"])
def test_pyz_only_distribution_listed(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.5"
    fx.distribution("pyzonly", "2.0", modules=("pyzonly/__init__.py",))
    fx.ship_module("pyzonly", fx.site / "pyzonly" / "__init__.py")
    text = fx.listed()
    assert "pyzonly 2.0" in text
    assert "PYZONLY LICENCE TEXT" in text


@pytest.mark.parametrize("ac_id", ["AC-110.5"], ids=["AC-110.5"])
def test_unshipped_distribution_left_off(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.5"
    fx.distribution("devonly", modules=("devonly/__init__.py",))
    text = fx.listed()
    assert "devonly" not in text
    assert "DEVONLY LICENCE TEXT" not in text


@pytest.mark.parametrize(
    "notice",
    [
        "alpha/vendor/COPYING.bsd",
        "alpha/AUTHORS",
        "alpha/third_party/THIRD-PARTY.txt",
        "alpha/notice.md",
        "alpha-1.0.dist-info/licenses/alpha/src/dragon4_LICENSE.txt",
    ],
    ids=["copying", "authors", "third-party", "notice", "licenses-folder"],
)
def test_every_notice_in_record_listed(fx: _Fixture, notice: str) -> None:
    """numpy's dragon4 licence is in its licenses folder under a name the pattern misses."""
    fx.distribution(
        "alpha",
        modules=("alpha/__init__.py", "alpha/_native.pyd"),
        notices={
            "alpha-1.0.dist-info/licenses/LICENSE": "ALPHA LICENCE TEXT",
            notice: "THE EXTRA NOTICE",
        },
    )
    assert "THE EXTRA NOTICE" in fx.listed()


# AC-110.6: a missing text refuses.


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_owner_without_notice_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.6"
    fx.distribution("bare", notices={}, modules=("bare/__init__.py",))
    fx.ship_module("bare", fx.site / "bare" / "__init__.py")
    assert "bare" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_record_notice_missing_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.6"
    fx.distribution(
        "alpha",
        modules=("alpha/__init__.py", "alpha/_native.pyd"),
        record_only=("alpha/ThirdPartyNotices.txt",),
    )
    assert "alpha/ThirdPartyNotices.txt" in fx.refusal(capsys)


# AC-110.7: GPL-class licences need the allow list.


@pytest.mark.parametrize("metadata", GPL_FIELDS.values(), ids=GPL_FIELDS.keys())
def test_gpl_class_refuses(fx: _Fixture, metadata: str, capsys: pytest.CaptureFixture[str]) -> None:
    fx.distribution("copyleft", metadata=metadata, modules=("copyleft/__init__.py",))
    fx.ship_module("copyleft", fx.site / "copyleft" / "__init__.py")
    assert "copyleft" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.7"], ids=["AC-110.7"])
def test_allow_listed_gpl_passes(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.7"
    fx.distribution("num2words", metadata=GPL_FIELDS["lgpl"], modules=("num2words/__init__.py",))
    fx.ship_module("num2words", fx.site / "num2words" / "__init__.py")
    assert "NUM2WORDS LICENCE TEXT" in fx.listed()


@pytest.mark.parametrize("ac_id", ["AC-110.7"], ids=["AC-110.7"])
def test_unshipped_gpl_is_no_problem(fx: _Fixture, ac_id: str) -> None:
    """phonemizer-fork sits in .venv; only its reaching the build may fail."""
    assert ac_id == "AC-110.7"
    fx.distribution(
        "phonemizer-fork", metadata=GPL_FIELDS["field"], modules=("phonemizer/__init__.py",)
    )
    assert "phonemizer" not in fx.listed()


@pytest.mark.parametrize("ac_id", ["AC-110.7"], ids=["AC-110.7"])
def test_gpl_npm_package_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.7"
    fx.npm_package("copyleft-js", licence="GPL-3.0-only")
    assert "copyleft-js" in fx.refusal(capsys)


# AC-110.17: the fixture half; row 11 checks the real build.


@pytest.mark.parametrize("ac_id", ["AC-110.17"], ids=["AC-110.17"])
def test_notice_outside_dist_info_and_toc_listed(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.17"
    fx.distribution(
        "alpha",
        modules=("alpha/__init__.py", "alpha/_native.pyd"),
        notices={
            "alpha-1.0.dist-info/licenses/LICENSE": "ALPHA LICENCE TEXT",
            "alpha/ThirdPartyNotices.txt": "NOTICE FROM NO TOC",
        },
    )
    assert "alpha/ThirdPartyNotices.txt" not in {dest for dest, _, _ in fx.collect}
    assert "NOTICE FROM NO TOC" in fx.listed()


# AC-110.18: everything is owned or in a named class, and the TOCs match the build.


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_named_classes_are_accepted(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.18"
    text = fx.listed()
    assert "CPython 3.12.12" in text
    assert "PSF TERMS AND BZIP2" in text
    for component in OVERRIDES.values():
        assert f"{component.upper()} UPSTREAM TEXT" in text
    for name in WINDOWS_RUNTIME:
        assert name in text


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_first_party_left_off(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.18"
    assert "avkit_core" not in fx.listed()


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_unowned_native_payload_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.ship_file("mystery.dll", "C:/elsewhere/mystery.dll")
    assert "mystery.dll" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_unowned_module_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.ship_module("ghostmod", _write(fx.site / "ghostmod.py"))
    assert "ghostmod" in fx.refusal(capsys)


@pytest.mark.parametrize(
    "name",
    ["ucrtbase_extra.dll", "vcruntime.dll", "api-ms-win.dll", "msvcp.dll"],
    ids=["ucrtbase", "vcruntime", "api-ms", "msvcp"],
)
def test_runtime_lookalike_refuses(
    fx: _Fixture, name: str, capsys: pytest.CaptureFixture[str]
) -> None:
    fx.ship_file(name, f"C:/elsewhere/{name}")
    assert name in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_uncovered_cpython_library_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """tcl86t.dll sits beside the libraries with reviewed texts but has none of its own."""
    assert ac_id == "AC-110.18"
    fx.ship_file("tcl86t.dll", _write(fx.base / "DLLs" / "tcl86t.dll"))
    assert "tcl86t.dll" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_base_site_packages_is_not_cpython(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.ship_module("stray", _write(fx.base / "Lib" / "site-packages" / "stray.py"))
    assert "stray" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_namespace_goes_to_top_level_owner(fx: _Fixture, ac_id: str) -> None:
    """Namespace packages have no source file: PyInstaller's TOC source is the literal '-'."""
    assert ac_id == "AC-110.18"
    fx.distribution("nsdist", modules=("nsroot/thing.py",))
    fx.ship_module("nsroot", "-")
    assert "NSDIST LICENCE TEXT" in fx.listed()


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_ownerless_namespace_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.ship_module("ghostns.sub", "-")
    assert "ghostns.sub" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_file_on_disk_not_in_collect_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    _write(fx.internal / "left_behind.dll")
    assert "left_behind.dll" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_collect_file_not_on_disk_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    (fx.internal / "alpha" / "_native.pyd").unlink()
    assert "alpha/_native.pyd" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_exe_module_not_in_pyz_toc_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.extra_exe_modules.add("phonemizer")
    assert "phonemizer" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_pyz_toc_module_not_in_exe_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.dropped_exe_modules.add("alpha")
    assert "alpha" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_unreadable_toc_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.build()
    _write(fx.work / "PYZ-00.toc", "not a toc (")
    build = _tool().Build(
        work_dir=fx.work,
        dist_dir=fx.dist,
        repo_root=fx.repo,
        base_prefix=fx.base,
        nuget_root=fx.nuget,
        distributions=lambda: md.distributions(path=[str(fx.site)]),
        read_exe_modules=lambda _exe: set(),
        runtime_versions={},
        python_version="3.12.12",
    )
    assert _tool().write_list(build, fx.out) == 1
    assert "PYZ-00.toc" in capsys.readouterr().err


# The runtime texts come from reviewed files, so they are checked like any other input.


@pytest.mark.parametrize("slug", OVERRIDES, ids=OVERRIDES)
def test_missing_override_refuses(
    fx: _Fixture, slug: str, capsys: pytest.CaptureFixture[str]
) -> None:
    (fx.overrides / f"{slug}.txt").unlink()
    assert f"{slug}.txt" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_override_without_source_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    _write(fx.overrides / "zlib.txt", _override_text("zlib", source=""))
    assert "zlib.txt" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_override_for_other_version_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    fx.runtime_versions["openssl"] = "3.5.4"
    assert "openssl.txt" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_cpython_licence_missing_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    (fx.base / "LICENSE.txt").unlink()
    assert "LICENSE.txt" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_committed_overrides_are_complete(ac_id: str) -> None:
    tool = _tool()
    assert ac_id == "AC-110.18"
    folder = REPO_ROOT / "packaging" / "licence-overrides"
    for slug in (*tool.REQUIRED_OVERRIDES, "npm-type-fest"):
        override = tool.read_override(folder / f"{slug}.txt")
        assert override.version
        assert override.source.startswith("https://")
        assert len(override.text) > 100


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_openssl_version_is_the_real_one(ac_id: str) -> None:
    """The fixtures inject these versions, so this one runs on the real runtime."""
    assert ac_id == "AC-110.18"
    version = _tool().runtime_versions()["openssl"]
    assert f"OpenSSL {version} " in ssl.OPENSSL_VERSION


# npm: the non-dev closure of the lockfile.


@pytest.mark.parametrize("ac_id", ["AC-110.5"], ids=["AC-110.5"])
def test_npm_closure_listed_without_dev(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.5"
    text = fx.listed()
    assert "react 1.0.0" in text
    assert "REACT NPM TEXT" in text
    assert "vitest" not in text


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_npm_package_without_text_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.6"
    fx.npm_package("no-text", text=None)
    assert "no-text" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_npm_package_not_installed_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.6"
    fx.lock["node_modules/absent"] = {"version": "1.0.0", "license": "MIT"}
    assert "absent" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_npm_override_supplies_text(fx: _Fixture, ac_id: str) -> None:
    """type-fest 2.19.0 publishes no licence file."""
    assert ac_id == "AC-110.6"
    fx.npm_package("no-text", "2.0.0", text=None)
    _write(fx.overrides / "npm-no-text.txt", _override_text("no-text", "2.0.0"))
    assert "NO-TEXT UPSTREAM TEXT" in fx.listed()


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_npm_override_other_version_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.6"
    fx.npm_package("no-text", "2.0.0", text=None)
    _write(fx.overrides / "npm-no-text.txt", _override_text("no-text", "1.9.0"))
    assert "npm-no-text.txt" in fx.refusal(capsys)


# .NET: the runtime packs the region picker was published with.


@pytest.mark.parametrize("ac_id", ["AC-110.5"], ids=["AC-110.5"])
def test_dotnet_pack_texts_listed(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.5"
    text = fx.listed()
    for expected in ("8.0.1", "NETCORE LICENCE", "NETCORE NOTICES", "DESKTOP LICENCE"):
        assert expected in text


@pytest.mark.parametrize(
    "relative",
    [
        "microsoft.netcore.app.runtime.win-x64/8.0.1/LICENSE.TXT",
        "microsoft.netcore.app.runtime.win-x64/8.0.1/THIRD-PARTY-NOTICES.TXT",
        "microsoft.windowsdesktop.app.runtime.win-x64/8.0.1/LICENSE",
    ],
    ids=["netcore-licence", "netcore-notices", "desktop-licence"],
)
def test_dotnet_text_missing_refuses(
    fx: _Fixture, relative: str, capsys: pytest.CaptureFixture[str]
) -> None:
    (fx.nuget / relative).unlink()
    assert Path(relative).name in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_dotnet_unknown_library_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.6"
    fx.deps_libraries["Some.Nuget.Package/1.0.0"] = {"type": "package"}
    assert "Some.Nuget.Package" in fx.refusal(capsys)


@pytest.mark.parametrize("ac_id", ["AC-110.6"], ids=["AC-110.6"])
def test_picker_not_published_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """The generator has to run after build:picker, so a missing publish folder is a refusal."""
    assert ac_id == "AC-110.6"
    build = fx.build()
    (fx.repo / "native" / "region-picker" / "publish" / "avkit-region-picker.deps.json").unlink()
    assert _tool().write_list(build, fx.out) == 1
    assert "deps.json" in capsys.readouterr().err


# The rest of the file a user reads.


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_bootloader_terms_stated(fx: _Fixture, ac_id: str) -> None:
    assert ac_id == "AC-110.18"
    assert "BOOTLOADER EXCEPTION" in fx.listed()


@pytest.mark.parametrize("ac_id", ["AC-110.18"], ids=["AC-110.18"])
def test_bootloader_terms_missing_refuses(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.18"
    (fx.site / "pyinstaller-1.0.dist-info" / "RECORD").unlink()
    (fx.site / "pyinstaller-1.0.dist-info" / "METADATA").unlink()
    assert "pyinstaller" in fx.refusal(capsys).lower()


@pytest.mark.parametrize("ac_id", ["AC-110.8"], ids=["AC-110.8"])
def test_refusal_removes_stale_list(
    fx: _Fixture, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """electron-builder only warns about a missing list, but it would ship a stale one."""
    assert ac_id == "AC-110.8"
    _write(fx.out, "from an older build")
    fx.ship_file("mystery.dll", "C:/elsewhere/mystery.dll")
    fx.refusal(capsys)
    assert not fx.out.exists()


@pytest.mark.parametrize("ac_id", ["AC-110.8"], ids=["AC-110.8"])
def test_cli_refuses_a_missing_build(
    tmp_path: Path, ac_id: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert ac_id == "AC-110.8"
    assert _tool().main(["--repo-root", str(tmp_path)]) == 1
    assert "COLLECT-00.toc" in capsys.readouterr().err
    assert not (tmp_path / "packaging" / "dist" / "THIRD_PARTY_LICENSES.txt").exists()
