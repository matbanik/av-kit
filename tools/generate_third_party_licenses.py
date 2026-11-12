#!/usr/bin/env python3
"""Write the installer's third-party licence list from the real build (MEU-110).

Reads PyInstaller's COLLECT and PYZ tables of contents, so the list covers what shipped and not
what happens to be installed. Every file and module must be owned by a distribution or fall in a
named class, and anything else is refused: an unowned payload, a missing licence text, a GPL-class
licence off the allow list, or tables of contents that disagree with the build on disk.

A refusal leaves no list behind. electron-builder only warns about a missing source, so the caller
has to stop on this tool's exit code.

Runs after `tools/package_backend.py` and `npm run build:picker`, with the Python that built the
backend, because its metadata and native library versions are the ones that shipped.

Usage:
    uv run python tools/generate_third_party_licenses.py [--repo-root DIR] [--out FILE]
"""

from __future__ import annotations

import argparse
import ast
import csv
import importlib.metadata as md
import json
import os
import platform
import re
import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path, PureWindowsPath

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_NAME = "avkit-backend"
NAMESPACE_SOURCE = "-"  # PyInstaller's source for a namespace package, which has no file.
NOTICE_FILE = re.compile(
    r"(^|/)(licen[cs]e|copying|notice|thirdpartynotices|third[-_]party|authors)[^/]*$",
    re.IGNORECASE,
)
# PEP 639 says everything here is licence text, whatever it is called: numpy's dragon4_LICENSE.txt.
LICENCE_FOLDER = re.compile(r"\.dist-info/licenses/", re.IGNORECASE)
GPL_CLASS = re.compile(r"\b[la]?gpl|general public", re.IGNORECASE)
GPL_ALLOWED = frozenset({"num2words"})  # LGPL, covered by AC-72.7's appendix.
WINDOWS_RUNTIME = re.compile(
    r"^(api-ms-win-.*|ucrtbase|vcruntime140.*|msvcp140.*)\.dll$", re.IGNORECASE
)
CPYTHON_LIBRARIES = frozenset(
    {"libcrypto-3-x64.dll", "libssl-3-x64.dll", "libffi-8.dll", "sqlite3.dll"}
)
REQUIRED_OVERRIDES = (
    "cpython-incorporated",
    "openssl",
    "libffi",
    "sqlite",
    "xz",
    "expat",
    "libmpdec",
    "zlib",
    "hacl-star",
)
DOTNET_PACK_FILES = {
    "microsoft.netcore.app.runtime.win-x64": ("LICENSE.TXT", "THIRD-PARTY-NOTICES.TXT"),
    "microsoft.windowsdesktop.app.runtime.win-x64": ("LICENSE",),
}
RULE = "=" * 78
OTHER_LISTS = """\
These licence files are installed alongside this one:
  LICENSE.electron.txt and LICENSES.chromium.html, in the install folder: Electron and Chromium
  resources/LICENSE: av-kit itself
  resources/THIRD_PARTY_NOTICES.md: where the main components come from
  resources/ffmpeg/LICENSE.txt: FFmpeg
  resources/deno/LICENSE.md: Deno
  resources/mcp-server/LICENSES.txt: the packages bundled into the MCP server
"""

Entry = tuple[str, str, str]


class Refused(Exception):
    """The build cannot be listed; ``problems`` says why, one line each."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__(f"{len(problems)} problem(s)")
        self.problems = problems


@dataclass(frozen=True)
class Override:
    component: str
    version: str
    licence: str
    source: str
    text: str


def read_override(path: Path) -> Override:
    """A reviewed licence file: four header fields, a `---` line, then upstream's text."""
    head, separator, text = path.read_text(encoding="utf-8").partition("\n---\n")
    fields = dict(line.split(": ", 1) for line in head.splitlines() if ": " in line)
    missing = [
        name
        for name in ("Component", "Version", "Licence", "Source")
        if not fields.get(name, "").strip()
    ]
    if missing or not separator or not text.strip():
        raise ValueError(
            f"{path.name}: needs {', '.join(missing) or 'a --- line and the upstream text'}"
        )
    if not fields["Source"].startswith("https://"):
        raise ValueError(f"{path.name}: Source must be an https URL")
    return Override(
        fields["Component"], fields["Version"], fields["Licence"], fields["Source"], text
    )


def read_exe_modules(exe: Path) -> set[str]:
    """The module names really inside the exe's archive."""
    from PyInstaller.archive.readers import CArchiveReader  # Only here: CI's unit tests lack it.

    archive = CArchiveReader(str(exe))
    pyz = next(name for name in archive.toc if name.endswith(".pyz"))
    return set(archive.open_embedded_archive(pyz).toc)


def runtime_versions() -> dict[str, str]:
    """Native versions this Python carries, so a Python bump cannot leave a stale statement."""
    import decimal
    import pyexpat
    import sqlite3
    import ssl
    import zlib

    return {
        "cpython-incorporated": platform.python_version(),
        "openssl": ssl.OPENSSL_VERSION.split()[1],  # OPENSSL_VERSION_INFO says 3.5.0 for 3.5.4.
        "sqlite": sqlite3.sqlite_version,
        "expat": pyexpat.EXPAT_VERSION.removeprefix("expat_"),
        "zlib": zlib.ZLIB_RUNTIME_VERSION,
        "libmpdec": decimal.__libmpdec_version__,
    }


@dataclass(frozen=True)
class Build:
    work_dir: Path
    dist_dir: Path
    repo_root: Path
    base_prefix: Path
    nuget_root: Path
    distributions: Callable[[], Iterable[md.Distribution]] = md.distributions
    read_exe_modules: Callable[[Path], set[str]] = read_exe_modules
    runtime_versions: Mapping[str, str] = field(default_factory=dict)
    python_version: str = field(default_factory=platform.python_version)
    gpl_allowed: frozenset[str] = GPL_ALLOWED


def _heading(title: str) -> str:
    return f"\n{RULE}\n{title}\n{RULE}\n\n"


def _normal(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _path_key(path: object) -> str:
    return os.path.normcase(os.path.normpath(str(path)))


def _read_notice(path: Path) -> str:
    raw = path.read_bytes()
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def _block(title: str, licence: str, texts: list[tuple[str, str]]) -> str:
    parts = [f"{title}\nLicence: {licence}\n"]
    parts += [f"\n--- {label} ---\n{text.rstrip()}\n" for label, text in texts]
    return "".join(parts) + "\n"


def _read_toc(path: Path, problems: list[str]) -> list[Entry] | None:
    try:
        data = ast.literal_eval(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.append(f"{path.name}: not found in {path.parent}; build the backend first")
        return None
    except (OSError, ValueError, SyntaxError) as error:
        problems.append(f"{path.name}: unreadable: {error}")
        return None
    entries = data[-1] if isinstance(data, tuple | list) and data else None
    if not isinstance(entries, list) or not all(
        isinstance(entry, tuple | list)
        and len(entry) == 3
        and all(isinstance(part, str) for part in entry)
        for entry in entries
    ):
        problems.append(f"{path.name}: unreadable: not a list of (name, source, kind)")
        return None
    return [tuple(entry) for entry in entries]


def _check_collect_matches_disk(build: Build, collect: list[Entry], problems: list[str]) -> None:
    internal = build.dist_dir / "_internal"
    if not internal.is_dir():
        problems.append(f"stale build: {internal} does not exist")
        return
    listed = {dest.replace("\\", "/").lower() for dest, _, kind in collect if kind != "EXECUTABLE"}
    on_disk = {
        path.relative_to(internal).as_posix().lower()
        for path in internal.rglob("*")
        if path.is_file()
    }
    problems += [
        f"stale build: {name} is in _internal but not in COLLECT-00.toc"
        for name in sorted(on_disk - listed)
    ]
    problems += [
        f"stale build: {name} is in COLLECT-00.toc but not in _internal"
        for name in sorted(listed - on_disk)
    ]


def _check_pyz_matches_exe(build: Build, pyz: list[Entry], problems: list[str]) -> None:
    exe = build.dist_dir / f"{BACKEND_NAME}.exe"
    if not exe.is_file():
        problems.append(f"stale build: {exe} does not exist")
        return
    listed = {name for name, _, _ in pyz}
    inside = build.read_exe_modules(exe)
    problems += [
        f"stale build: module {name} is in the exe but not in PYZ-00.toc"
        for name in sorted(inside - listed)
    ]
    problems += [
        f"stale build: module {name} is in PYZ-00.toc but not in the exe"
        for name in sorted(listed - inside)
    ]


class _Environment:
    """Which distribution owns each installed file, and which provide each top-level name."""

    def __init__(self, distributions: Iterable[md.Distribution]) -> None:
        self.by_name: dict[str, md.Distribution] = {}
        self.by_path: dict[str, list[md.Distribution]] = {}
        self.by_top_level: dict[str, list[md.Distribution]] = {}
        for dist in distributions:
            name = dist.metadata.get("Name")
            if not name:  # A leftover dist-info folder with no METADATA.
                continue
            self.by_name[_normal(name)] = dist
            for top in {file.parts[0] for file in dist.files or []}:
                self.by_top_level.setdefault(top, []).append(dist)
            for file in dist.files or []:
                self.by_path.setdefault(_path_key(dist.locate_file(file)), []).append(dist)


@dataclass
class _Payload:
    owners: dict[str, md.Distribution] = field(default_factory=dict)
    windows_files: set[str] = field(default_factory=set)
    namespaces: list[str] = field(default_factory=list)

    def own(self, dists: Iterable[md.Distribution]) -> None:
        for dist in dists:
            self.owners[_normal(dist.metadata["Name"])] = dist


def _inside_python(source: str, base_prefix: Path) -> str | None:
    """``source`` relative to CPython's own folder, lowercase with forward slashes, or None."""
    resolved = base_prefix.resolve()
    for candidate in (_path_key(source), _path_key(Path(source).resolve())):
        for base in (_path_key(base_prefix), _path_key(resolved)):
            if candidate.startswith(base + os.sep):
                return candidate[len(base) + 1 :].replace("\\", "/").lower()
    return None


def _is_cpython(source: str, build: Build) -> bool:
    relative = _inside_python(source, build.base_prefix)
    if relative is None:
        return False
    folder, _, name = relative.rpartition("/")
    if relative.startswith("lib/"):
        return not relative.startswith("lib/site-packages/")
    if folder == "dlls":
        return name.endswith(".pyd") or name in CPYTHON_LIBRARIES
    return folder == "" and re.fullmatch(r"python3\d*\.dll", name) is not None


def _classify(
    entry: Entry, build: Build, env: _Environment, payload: _Payload, problems: list[str]
) -> None:
    name, source, kind = entry
    if source == NAMESPACE_SOURCE:
        payload.namespaces.append(name)
        return
    dists = env.by_path.get(_path_key(source))
    if dists:
        payload.own(dists)
        return
    source_name = PureWindowsPath(source).name
    first_party = _path_key(build.repo_root / "packages") + os.sep
    built_here = _path_key(Path(source).parent) == _path_key(build.work_dir)
    if _path_key(source).startswith(first_party) or (
        built_here and source_name == "base_library.zip"
    ):
        return
    if _is_cpython(source, build):
        return
    if WINDOWS_RUNTIME.match(source_name):
        payload.windows_files.add(PureWindowsPath(name).name)
        return
    problems.append(f"unowned {kind}: {name} from {source}")


def _attribute_namespaces(env: _Environment, payload: _Payload, problems: list[str]) -> None:
    """A namespace with a shipped owner needs nothing more; siblings that did not ship stay off."""
    for name in payload.namespaces:
        candidates = env.by_top_level.get(name.split(".")[0], [])
        if not candidates:
            problems.append(f"unowned namespace package: {name}")
        elif not any(_normal(dist.metadata["Name"]) in payload.owners for dist in candidates):
            payload.own(candidates)


def _licence_label(metadata: md.PackageMetadata) -> str:
    if metadata.get("License-Expression"):
        return metadata["License-Expression"]
    classifiers = [
        classifier.split(" :: ")[-1]
        for classifier in metadata.get_all("Classifier") or []
        if classifier.startswith("License ::")
    ]
    if classifiers:
        return ", ".join(classifiers)
    field_lines = (metadata.get("License") or "").strip().splitlines()
    if field_lines and field_lines[0].upper() != "UNKNOWN" and len(field_lines[0]) <= 78:
        return field_lines[0]
    return "see the text below"


def _is_gpl_class(metadata: md.PackageMetadata) -> bool:
    fields = [metadata.get("License-Expression") or "", metadata.get("License") or ""]
    fields += [
        classifier
        for classifier in metadata.get_all("Classifier") or []
        if classifier.startswith("License ::")
    ]
    return any(GPL_CLASS.search(value) for value in fields)


def _record_paths(dist: md.Distribution) -> list[str]:
    """RECORD as written: ``Distribution.files`` quietly drops what is missing on disk."""
    rows = csv.reader((dist.read_text("RECORD") or "").splitlines())
    return [row[0].replace("\\", "/") for row in rows if row]


def _notice_texts(dist: md.Distribution, title: str, problems: list[str]) -> list[tuple[str, str]]:
    """Every licence or notice file in RECORD, shipped or not; some sit outside dist-info."""
    texts = []
    notices = [
        file
        for file in _record_paths(dist)
        if NOTICE_FILE.search(file) or LICENCE_FOLDER.search(file)
    ]
    for file in sorted(notices):
        path = Path(str(dist.locate_file(file)))
        if path.is_file():
            texts.append((file, _read_notice(path)))
        else:
            problems.append(f"{title}: {file} is in RECORD but not on disk")
    if not notices:
        problems.append(f"{title}: no licence or notice file in RECORD")
    return texts


def _python_section(build: Build, payload: _Payload, problems: list[str]) -> str:
    blocks = []
    for key in sorted(payload.owners):
        dist = payload.owners[key]
        title = f"{dist.metadata['Name']} {dist.version}"
        if _is_gpl_class(dist.metadata) and key not in build.gpl_allowed:
            problems.append(f"{title}: GPL-class licence, not on the allow list")
        texts = _notice_texts(dist, title, problems)
        blocks.append(_block(title, _licence_label(dist.metadata), texts))
    return _heading(f"Python packages in the backend ({len(blocks)})") + "".join(blocks)


def _override_block(path: Path, expected_version: str | None, problems: list[str]) -> str:
    try:
        override = read_override(path)
    except OSError:
        problems.append(f"{path.name}: reviewed licence text not found in {path.parent}")
        return ""
    except ValueError as error:
        problems.append(str(error))
        return ""
    if expected_version is not None and expected_version != override.version:
        problems.append(
            f"{path.name}: says version {override.version}, but this build has {expected_version}"
        )
    return _block(
        f"{override.component} {override.version}",
        override.licence,
        [(override.source, override.text)],
    )


def _cpython_section(build: Build, problems: list[str]) -> str:
    licence = build.base_prefix / "LICENSE.txt"
    if not licence.is_file():
        problems.append(f"CPython: {licence.name} not found in {build.base_prefix}")
    parts = [_heading(f"CPython {build.python_version}")]
    if licence.is_file():
        parts.append(f"{_read_notice(licence).rstrip()}\n\n")
    parts.append("The native libraries CPython ships, and the software it incorporates:\n\n")
    overrides = build.repo_root / "packaging" / "licence-overrides"
    parts += [
        _override_block(overrides / f"{slug}.txt", build.runtime_versions.get(slug), problems)
        for slug in REQUIRED_OVERRIDES
    ]
    return "".join(parts)


def _bootloader_section(env: _Environment, problems: list[str]) -> str:
    dist = env.by_name.get("pyinstaller")
    if dist is None:
        problems.append("pyinstaller: not installed, so the bootloader's terms cannot be stated")
        return ""
    title = f"PyInstaller {dist.version}"
    statement = (
        f"{BACKEND_NAME}.exe starts through the PyInstaller bootloader. PyInstaller is under\n"
        "the GPL with a special exception that allows distributing programs built with it on\n"
        "their own terms. Its licence, with that exception, follows.\n\n"
    )
    texts = _notice_texts(dist, title, problems)
    return (
        _heading("PyInstaller bootloader")
        + statement
        + _block(title, "GPL with a special exception", texts)
    )


def _windows_section(payload: _Payload) -> str:
    statement = (
        "These files are the Microsoft Universal C Runtime and Visual C++ runtime. They are\n"
        "copyright Microsoft and redistributed on Microsoft's terms.\n\n"
    )
    names = "".join(f"  {name}\n" for name in sorted(payload.windows_files, key=str.lower))
    return _heading("Windows runtime files") + statement + names


def _npm_block(
    name: str, package: dict[str, object], folder: Path, build: Build, problems: list[str]
) -> str:
    version, licence = str(package.get("version")), str(package.get("license"))
    title = f"{name} {version}"
    if GPL_CLASS.search(licence) and _normal(name) not in build.gpl_allowed:
        problems.append(f"{title}: GPL-class licence, not on the allow list")
    notices = [
        path
        for path in sorted(folder.iterdir())
        if path.is_file() and NOTICE_FILE.search(path.name)
    ]
    if notices:
        return _block(title, licence, [(path.name, _read_notice(path)) for path in notices])
    override = (
        build.repo_root / "packaging" / "licence-overrides" / f"npm-{name.replace('/', '-')}.txt"
    )
    if not override.is_file():
        problems.append(f"{title}: no licence file and no {override.name}")
        return ""
    return _override_block(override, version, problems)


def _npm_section(build: Build, problems: list[str]) -> str:
    ui = build.repo_root / "ui"
    lock = ui / "package-lock.json"
    if not lock.is_file():
        problems.append(f"npm: {lock} not found")
        return ""
    packages: dict[str, dict[str, object]] = json.loads(lock.read_text(encoding="utf-8"))[
        "packages"
    ]
    blocks: dict[tuple[str, str], str] = {}
    for key, package in sorted(packages.items()):
        if not key or package.get("dev"):
            continue
        name = key.split("node_modules/")[-1]
        if (name, str(package.get("version"))) in blocks:
            continue
        folder = ui / key
        if not folder.is_dir():
            if not (package.get("optional") or package.get("devOptional")):
                problems.append(
                    f"{name} {package.get('version')}: not installed in ui/node_modules"
                )
            continue
        blocks[(name, str(package.get("version")))] = _npm_block(
            name, package, folder, build, problems
        )
    return _heading(f"npm packages in the desktop app ({len(blocks)})") + "".join(blocks.values())


def _dotnet_section(build: Build, problems: list[str]) -> str:
    publish = build.repo_root / "native" / "region-picker" / "publish"
    manifests = sorted(publish.glob("*.deps.json"))
    if not manifests:
        problems.append(f".NET: no *.deps.json in {publish}; run build:picker first")
    blocks = {}
    for manifest in manifests:
        libraries = json.loads(manifest.read_text(encoding="utf-8")).get("libraries", {})
        for key, library in sorted(libraries.items()):
            if library.get("type") == "project":
                continue
            pack, _, version = key.partition("/")
            pack = pack.removeprefix("runtimepack.")
            files = (
                DOTNET_PACK_FILES.get(pack.lower())
                if library.get("type") == "runtimepack"
                else None
            )
            if files is None:
                problems.append(f".NET: {key} is not a runtime pack this tool knows the licence of")
                continue
            texts = []
            for name in files:
                path = build.nuget_root / pack.lower() / version / name
                if path.is_file():
                    texts.append((name, _read_notice(path)))
                else:
                    problems.append(f".NET: {name} not found in {path.parent}")
            blocks[key] = _block(f"{pack} {version}", "see the text below", texts)
    return _heading("The .NET runtime in the region picker") + "".join(blocks.values())


def generate(build: Build) -> str:
    """The whole list, or Refused with every problem found, so one run shows them all."""
    problems: list[str] = []
    collect = _read_toc(build.work_dir / "COLLECT-00.toc", problems)
    pyz = _read_toc(build.work_dir / "PYZ-00.toc", problems)
    if collect is not None:
        _check_collect_matches_disk(build, collect, problems)
    if pyz is not None:
        _check_pyz_matches_exe(build, pyz, problems)

    env = _Environment(build.distributions())
    payload = _Payload()
    for entry in [*(collect or []), *(pyz or [])]:
        if entry[2] != "EXECUTABLE":
            _classify(entry, build, env, payload, problems)
    _attribute_namespaces(env, payload, problems)

    text = "".join(
        [
            "Third-party licences for av-kit\n\n"
            "Generated from the build this file shipped with. av-kit itself is MIT licensed.\n",
            _python_section(build, payload, problems),
            _cpython_section(build, problems),
            _bootloader_section(env, problems),
            _windows_section(payload),
            _npm_section(build, problems),
            _dotnet_section(build, problems),
            _heading("Other licence files"),
            OTHER_LISTS,
        ]
    )
    if problems:
        raise Refused(problems)
    return text


def write_list(build: Build, out: Path) -> int:
    """Write the list and return 0, or print each problem to stderr and return 1."""
    out.unlink(missing_ok=True)  # First, so that even a crash cannot leave an older build's list.
    try:
        data = generate(build).encode("utf-8")
    except Refused as refused:
        for problem in refused.problems:
            print(problem, file=sys.stderr)
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print(f"{out}: {len(data)} bytes")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out", type=Path, help="default: packaging/dist/THIRD_PARTY_LICENSES.txt")
    args = parser.parse_args(argv)
    packaging = args.repo_root / "packaging"
    build = Build(
        work_dir=packaging / "build" / BACKEND_NAME,
        dist_dir=packaging / "dist" / BACKEND_NAME,
        repo_root=args.repo_root,
        base_prefix=Path(sys.base_prefix),
        nuget_root=Path(os.environ.get("NUGET_PACKAGES") or Path.home() / ".nuget" / "packages"),
        runtime_versions=runtime_versions(),
    )
    return write_list(build, args.out or packaging / "dist" / "THIRD_PARTY_LICENSES.txt")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
