"""Assemble the complete corresponding source of the FFmpeg build the installer ships (D-101).

It reads what it downloads and never runs it: no checkout, no script, no hook, no build step. A
repository goes into a bare store and leaves through `git archive`. A step in the recipe this file
doesn't know about stops the run, so a new pin can't lose a source quietly. The one program it
starts is the ffmpeg.exe the installer ships, for `-version`, because that binary's own
configuration line is the independent check on the recipe reading. Change the pins below together
with tools/fetch_ffmpeg_windows.ps1.

    python -I -B tools/assemble_ffmpeg_source.py --work DIR --ffmpeg-exe FILE
    python -I -B tools/assemble_ffmpeg_source.py --work DIR --measure-only
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time
import tomllib
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from pathlib import Path

# The build, its recipe and the FFmpeg commit it was made from.
BUILD_TAG = "autobuild-2026-10-31-12-59"
BUILD_ASSET = "ffmpeg-n8.1.3-27-g8dca1586f4-win64-gpl-8.1.zip"
BUILD_SHA256 = "401dffcf14c301082e1fc03b0bc876b92ea676bfc521fc56e80a1537d137034f"
BUILDS_REPO = "https://github.com/BtbN/FFmpeg-Builds.git"
BUILDS_COMMIT = "5031c6f1082414e53688d39e521849905071070d"
FFMPEG_REPO = "https://github.com/FFmpeg/FFmpeg.git"
FFMPEG_COMMIT = "8dca1586f468bfcbb78ae3ed618af1361d9f140a"
ARCHIVE_NAME = "av-kit-0.1.0-rc.1-ffmpeg-source"
# The recipe's FFmpeg 8.1 add-in (`ffbuild_ffver` is 801) for this build's target and variant.
TARGET, VARIANT, ADDINS, FFVER = "win64", "gpl", "8.1", 801
# GitHub's limit for one release asset.
ASSET_LIMIT = 2 * 1024**3
# What the archive holds beside the sources.
DOCUMENTS = ("README.md", "MANIFEST.tsv", "FETCH-HINTS.tsv")

# The recipe's compiler. BtbN's Dockerfile clones crosstool-NG's newest commit when the image is
# built; this is the commit its config was saved with. crosstool-NG's own chksum files verify each
# archive. `file` is the name those chksum files use.
CROSSTOOL_REPO = "https://github.com/crosstool-ng/crosstool-ng.git"
CROSSTOOL_COMMIT = "b1a94f65c5187d99037a4e2f57aefbdf995a9677"
CROSSTOOL_VERSION = "1.29.0.7_b1a94f6"
GNU = ("https://ftpmirror.gnu.org", "https://ftp.gnu.org/gnu")


@dataclass(frozen=True)
class Tool:
    config: str
    version: str
    package: str
    file: str
    urls: tuple[str, ...]


TOOLCHAIN = (
    Tool(
        "CT_GCC_VERSION",
        "16.2.0",
        "gcc",
        "gcc-16.2.0.tar.xz",
        tuple(f"{g}/gcc/gcc-16.2.0/gcc-16.2.0.tar.xz" for g in GNU),
    ),
    Tool(
        "CT_BINUTILS_VERSION",
        "2.47",
        "binutils",
        "binutils-2.47.tar.xz",
        tuple(f"{g}/binutils/binutils-2.47.tar.xz" for g in GNU),
    ),
    Tool(
        "CT_GMP_VERSION",
        "6.3.0",
        "gmp",
        "gmp-6.3.0.tar.xz",
        tuple(f"{g}/gmp/gmp-6.3.0.tar.xz" for g in GNU),
    ),
    Tool(
        "CT_MPFR_VERSION",
        "4.2.2",
        "mpfr",
        "mpfr-4.2.2.tar.xz",
        tuple(f"{g}/mpfr/mpfr-4.2.2.tar.xz" for g in GNU),
    ),
    Tool(
        "CT_MPC_VERSION",
        "1.3.1",
        "mpc",
        "mpc-1.3.1.tar.gz",
        tuple(f"{g}/mpc/mpc-1.3.1.tar.gz" for g in GNU),
    ),
    Tool(
        "CT_GETTEXT_VERSION",
        "0.26",
        "gettext",
        "gettext-0.26.tar.xz",
        tuple(f"{g}/gettext/gettext-0.26.tar.xz" for g in GNU),
    ),
    Tool(
        "CT_ISL_VERSION",
        "0.27",
        "isl",
        "isl-0.27.tar.xz",
        ("https://libisl.sourceforge.io/isl-0.27.tar.xz",),
    ),
    Tool(
        "CT_ZLIB_VERSION",
        "1.3.1",
        "zlib",
        "zlib-1.3.1.tar.xz",
        ("https://github.com/madler/zlib/releases/download/v1.3.1/zlib-1.3.1.tar.xz",),
    ),
    Tool(
        "CT_ZSTD_VERSION",
        "1.5.7",
        "zstd",
        "zstd-1.5.7.tar.gz",
        ("https://github.com/facebook/zstd/releases/download/v1.5.7/zstd-1.5.7.tar.gz",),
    ),
    Tool(
        "CT_MOLD_VERSION",
        "2.42.0",
        "mold",
        "v2.42.0.tar.gz",
        ("https://github.com/rui314/mold/archive/refs/tags/v2.42.0.tar.gz",),
    ),
    Tool(
        "CT_MINGW_W64_VERSION",
        "v14.0.0",
        "mingw-w64",
        "mingw-w64-v14.0.0.tar.bz2",
        (
            "https://downloads.sourceforge.net/project/mingw-w64/mingw-w64/mingw-w64-release/mingw-w64-v14.0.0.tar.bz2",
        ),
    ),
)

# Subversion has no bare store here, so each repository's root is named and walked over HTTP.
SVN_ROOTS = {
    "https://svn.code.sf.net/p/lame/svn/trunk/lame": (
        "https://svn.code.sf.net/p/lame/svn",
        "trunk/lame",
        None,
    ),
    "https://svn.xvid.org/trunk/xvidcore": (
        "https://svn.xvid.org",
        "trunk/xvidcore",
        ("anonymous", ""),
    ),
}
# Only these scripts fetch more while building, and only what their own Cargo.lock names (plus `cc`,
# a build tool that doesn't reach the binary).
BUILD_STEP_CARGO = {"50-rav1e.sh"}
# A path the recipe deletes straight after fetching it.
ARCHIVE_EXCLUDES = {"50-amf.sh": ("Thirdparty",)}
# The configure flags the recipe's variant sets itself. They switch on no library, so no source
# stands behind them.
VARIANT_FLAGS = frozenset({"--enable-gpl", "--enable-version3"})

_VAR = re.compile(r'^(SCRIPT_[A-Z0-9_]+)="?([^"\n]*)"?', re.M)
_ENABLED = re.compile(r"ffbuild_enabled\(\)\s*\{(.*?)\n\}", re.S)
_DOCKERDL = re.compile(r"ffbuild_dockerdl\(\)\s*\{(.*?)\n\}", re.S)
_PLAIN_DL = re.compile(
    r"""^(?:
        \#.* | true | return\ 0 | default_dl\ \S+ |
        echo\ "git\ clone\ .*" | echo\ "retry-tool\ .*" | echo\ "cd\ iconv\ .*" |
        echo\ "git-mini-clone\ .*" | echo\ "git\ fetch\ --unshallow.*" |
        echo\ "rm\ -rf\ \.git\ Thirdparty" | echo\ "autoreconf\ -i"
    )$""",
    re.X,
)
_BUILD_FETCH = re.compile(
    r"(?:^|[\s;&|(\"'])(?:curl\s+-|wget\s|git\s+clone\s|git-mini-clone\s|svn\s|hg\s+clone\s|cargo\s|rustup\s|meson\s+subprojects\s|pip3?\s+install\s)"
)
_HEX = re.compile(r"[0-9a-f]{7,64}")
_DEPS_ENTRY = re.compile(
    r"'([^']+)':\s*Var\('(\w+)'\)\s*\+\s*'([^'@]+)@'\s*\+\s*Var\('(\w+)'\)", re.S
)
_DEPS_VAR = re.compile(r"'(\w+)':\s*'([^']+)'")
_OPUS_MODEL = re.compile(r'dnn/download_model\.sh\s+"([0-9a-f]{64})"')
_LISTING_HREF = re.compile(r'<(?:li><a|dir name="[^"]*"|file name="[^"]*")[^>]*href="([^"]+)"')
_CONFIGURE = re.compile(r"ffbuild_configure\(\)\s*\{(.*?)\n\}", re.S)
_ENABLE_FLAG = re.compile(r"--enable-[A-Za-z0-9_-]+")
_FETCH_HINT = "FetchContent_Declare|ExternalProject_Add"


class SourceSetError(RuntimeError):
    """The source set can't be proved complete."""


def enabled_for_build(text: str) -> bool:
    """Whether a script is on for this build.

    A condition it can't read counts as on: a spare source does no harm, a missing one breaks the
    licence.
    """
    found = _ENABLED.search(text)
    if found is None:
        return True

    def atom(raw: str) -> bool:
        raw = raw.strip()
        match = re.fullmatch(r"\[\[\s*\$(TARGET|VARIANT|ADDINS_STR)\s*(==|!=)\s*(\S+)\s*\]\]", raw)
        if match:
            value = {"TARGET": TARGET, "VARIANT": VARIANT, "ADDINS_STR": ADDINS}[match[1]]
            pattern = ".*".join(re.escape(part) for part in match[3].strip("'\"").split("*"))
            hit = re.fullmatch(pattern, value) is not None
            return hit if match[2] == "==" else not hit
        match = re.fullmatch(r"\(\(\s*\$\(ffbuild_ffver\)\s*(>=|<=|>|<|==)\s*(\d+)\s*\)\)", raw)
        if match:
            number = int(match[2])
            return {
                ">=": FFVER >= number,
                "<=": FFVER <= number,
                ">": FFVER > number,
                "<": FFVER < number,
                "==": FFVER == number,
            }[match[1]]
        raise ValueError(raw)

    try:
        for line in found[1].splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.fullmatch(r"return\s+(-?\d+)", line)
            if match:
                return match[1] == "0"
            match = re.fullmatch(r"(.+?)\s*(&&|\|\|)\s*return\s+(-?\d+)", line)
            if not match:
                raise ValueError(line)
            value = all(atom(part) for part in re.split(r"\s*&&\s*", match[1]))
            if (match[2] == "&&" and value) or (match[2] == "||" and not value):
                return match[3] == "0"
    except ValueError:
        return True
    return True


@dataclass
class FetchPlan:
    """What a script fetches beyond its pinned repository. `submodules`: None is none, () is all."""

    submodules: tuple[str, ...] | None = None
    sync_deps: bool = False
    cargo: bool = False
    wraps: tuple[str, ...] = ()
    opus_model: bool = False


def _submodule_paths(line: str) -> tuple[str, ...]:
    tokens = line.split('"')[1].split()[3:]
    paths, skip = [], False
    for token in tokens:
        if skip:
            skip = False
        elif token == "--depth":
            skip = True
        elif not token.startswith("-"):
            paths.append(token)
    return tuple(paths)


def fetch_plan(name: str, text: str) -> FetchPlan:
    """Read a script's fetch step. An unknown step raises, so a new pin stops the run."""
    plan = FetchPlan()
    found = _DOCKERDL.search(text)
    body = "" if found is None else found[1]
    for raw in body.splitlines():
        line = raw.strip()
        if not line or _PLAIN_DL.match(line):
            continue
        if "git submodule update" in line:
            plan.submodules = _submodule_paths(line)
        elif "./utils/git-sync-deps" in line:
            plan.sync_deps = True
        elif "cargo vendor" in line:
            plan.cargo = True
        elif "meson subprojects download" in line:
            plan.wraps = tuple(line.split("meson subprojects download", 1)[1].split('"')[0].split())
        elif './autogen.sh"' in line:
            plan.opus_model = True
        else:
            raise SourceSetError(f"{name}: unknown fetch step: {line}")
    outside = text.replace(body, "")
    if _BUILD_FETCH.search(outside) and name not in BUILD_STEP_CARGO:
        raise SourceSetError(
            f"{name}: a build step fetches more: {_BUILD_FETCH.search(outside)[0].strip()}"
        )
    if name in BUILD_STEP_CARGO:
        plan.cargo = True
    return plan


def script_sources(text: str) -> list[dict[str, str]]:
    """Every pinned source a script names."""
    variables = dict(_VAR.findall(text))
    sources = []
    for suffix in ("", "2", "3"):
        repo = variables.get(f"SCRIPT_REPO{suffix}")
        if repo is None:
            continue
        commit = variables.get(f"SCRIPT_COMMIT{suffix}")
        rev = variables.get(f"SCRIPT_REV{suffix}")
        if not commit and not rev:
            raise SourceSetError(f"no pin for {repo}")
        source = {"url": repo, "suffix": suffix}
        if commit:
            source["ref"] = commit
            mirror = variables.get(f"SCRIPT_MIRROR{suffix}")
            if mirror:
                source["mirror"] = mirror
        else:
            source["rev"] = rev
        sources.append(source)
    return sources


def parse_gitmodules(text: str) -> dict[str, str]:
    """Map each submodule's path to its URL."""
    modules: dict[str, str] = {}
    for block in re.split(r"^\s*\[submodule\b[^\]]*\]\s*$", text, flags=re.M)[1:]:
        path = re.search(r"^\s*path\s*=\s*(\S.*?)\s*$", block, re.M)
        url = re.search(r"^\s*url\s*=\s*(\S.*?)\s*$", block, re.M)
        if path and url:
            modules[path[1]] = url[1]
    return modules


def resolve_url(parent: str, url: str) -> str:
    """Resolve a submodule URL the way git does. Anything but https raises."""
    if url.startswith(("./", "../")):
        url = urllib.parse.urljoin(parent.rstrip("/") + "/", url)
    if not url.startswith("https://"):
        raise SourceSetError(f"not an https source: {url}")
    return url


def parse_deps(text: str) -> dict[str, tuple[str, str]]:
    """Read a gclient DEPS file as `utils/git-sync-deps` would, without running it."""
    variables = dict(_DEPS_VAR.findall(text))
    deps = {}
    for path, base, tail, rev in _DEPS_ENTRY.findall(text):
        deps[path] = (variables[base] + tail, variables[rev])
    if not deps:
        raise SourceSetError("DEPS names no dependency")
    return deps


def parse_cargo_lock(text: str) -> list[tuple[str, str, str]]:
    """Every registry crate as (name, version, sha256). Any other source raises."""
    crates = []
    for package in tomllib.loads(text).get("package", []):
        source = package.get("source")
        if source is None:
            continue
        if not source.startswith("registry+") or "checksum" not in package:
            raise SourceSetError(
                f"crate {package['name']} isn't a checked registry crate: {source}"
            )
        crates.append((package["name"], package["version"], package["checksum"]))
    return crates


def parse_chksum(text: str, file: str) -> str:
    """The sha256 crosstool-NG records for an archive."""
    found = re.search(rf"^sha256\s+{re.escape(file)}\s+([0-9a-f]{{64}})\s*$", text, re.M)
    if found is None:
        raise SourceSetError(f"no sha256 for {file}")
    return found[1]


def configure_flags(text: str) -> set[str]:
    """The `--enable-*` flags a recipe script hands to FFmpeg's configure."""
    found = _CONFIGURE.search(text)
    return set(_ENABLE_FLAG.findall(found[1])) if found else set()


def check_configuration(version_output: str, scripts: dict[str, str]) -> list[str]:
    """Hold the recipe reading against the binary itself and return the flags it didn't use.

    A flag in the binary with no enabled script behind it is a library this set has no source for.
    A flag the binary lacks only means a spare source, so it's reported and allowed.
    """
    lines = version_output.splitlines()
    if not lines or f"-g{FFMPEG_COMMIT[:10]}-" not in lines[0]:
        raise SourceSetError(f"not the pinned build: {lines[0] if lines else 'no output'}")
    configuration = next((line for line in lines if line.startswith("configuration:")), None)
    if configuration is None:
        raise SourceSetError("the binary printed no configuration line")
    binary = set(_ENABLE_FLAG.findall(configuration))
    explained: set[str] = set()
    for text in scripts.values():
        if enabled_for_build(text):
            explained |= configure_flags(text)
    unexplained = sorted(binary - explained - VARIANT_FLAGS)
    if unexplained:
        raise SourceSetError(f"no enabled script produces: {' '.join(unexplained)}")
    return sorted(explained - binary)


def _version_output(exe: Path) -> str:
    try:
        done = subprocess.run([str(exe), "-version"], capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise SourceSetError(f"{exe}: {exc}") from exc
    if done.returncode != 0:
        raise SourceSetError(f"{exe} -version exited {done.returncode}")
    return done.stdout.decode("utf-8", "replace")


def _git(
    store: Path | None, *args: str, timeout: int = 3600, allow: tuple[int, ...] = (0,)
) -> bytes:
    command = ["git"]
    if store is not None:
        command += ["-C", str(store)]
    command += [
        "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-c", "credential.helper=",
        "-c", "protocol.allow=never", "-c", "protocol.https.allow=always", *args,
    ]  # fmt: skip
    env = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1"}
    done = subprocess.run(command, capture_output=True, timeout=timeout, env=env, check=False)
    if done.returncode not in allow:
        raise SourceSetError(
            f"git {' '.join(args)[:160]}: {done.stderr.decode('utf-8', 'replace')[-300:]}"
        )
    return done.stdout


def fetch_hints(store: Path, commit: str) -> list[str]:
    """Files in a tree that can fetch more source while it builds: a Meson wrap or CMake step."""
    names = _git(store, "ls-tree", "-r", "--name-only", commit).decode("utf-8", "replace")
    hints = {name for name in names.splitlines() if name.endswith(".wrap")}
    # `git grep` exits 1 when nothing matches.
    found = _git(store, "grep", "-l", "-E", _FETCH_HINT, commit, "--", allow=(0, 1))
    for line in found.decode("utf-8", "replace").splitlines():
        hints.add(line.removeprefix(f"{commit}:"))
    return sorted(hints)


def _slug(url: str) -> str:
    parts = urllib.parse.urlparse(url)
    name = re.sub(r"\.git$", "", parts.path.rstrip("/")).strip("/")
    return re.sub(r"[^A-Za-z0-9._-]+", "_", f"{parts.netloc}_{name}")


def _repo_name(url: str) -> str:
    return re.sub(r"\.git$", "", url.rstrip("/").rsplit("/", 1)[-1])


def fetch_commit(store: Path, url: str, ref: str, mirror: str | None = None) -> str:
    """Bring one commit into a bare store and return its full id."""
    if not (store / "HEAD").exists():
        store.mkdir(parents=True, exist_ok=True)
        _git(store, "init", "--quiet", "--bare", "--template=")
    is_hash = _HEX.fullmatch(ref) is not None
    urls = [url] + ([mirror] if mirror and mirror.startswith("https://") else [])
    target = ref if is_hash else f"refs/tags/{ref}"
    failures = []
    for candidate in urls:
        for delay in (0, 20):
            time.sleep(delay)
            try:
                _git(store, "fetch", "--quiet", "--depth=1", "--no-tags", candidate, target)
                resolved = _git(store, "rev-parse", "FETCH_HEAD^{commit}").decode().strip()
                if is_hash and not resolved.startswith(ref):
                    raise SourceSetError(f"{candidate}: asked for {ref}, got {resolved}")
                return resolved
            except (SourceSetError, subprocess.TimeoutExpired) as exc:
                failures.append(str(exc))
        try:
            _git(
                store,
                "fetch",
                "--quiet",
                "--no-tags",
                candidate,
                "+refs/heads/*:refs/remotes/o/*",
                "+refs/tags/*:refs/tags/*",
            )
            return _git(store, "rev-parse", f"{ref}^{{commit}}").decode().strip()
        except (SourceSetError, subprocess.TimeoutExpired) as exc:
            failures.append(str(exc))
    raise SourceSetError(f"{url} {ref}: " + " | ".join(failures)[-500:])


def archive_tree(
    store: Path, commit: str, prefix: str, out: Path, exclude: tuple[str, ...] = ()
) -> tuple[int, int]:
    """Write a tree as a tar with every tracked file byte for byte. Returns (entries, bytes)."""
    (store / "info").mkdir(exist_ok=True)
    # This file outranks a repository's own .gitattributes, which can drop or rewrite files.
    (store / "info" / "attributes").write_text("* -export-ignore -export-subst\n", encoding="ascii")
    listing = _git(store, "ls-tree", "-r", "-z", commit).split(b"\0")
    expected = 0
    for line in listing:
        if not line:
            continue
        meta, _, path = line.partition(b"\t")
        if meta.startswith(b"160000"):
            continue
        name = path.decode("utf-8", "replace")
        if any(name == item or name.startswith(item + "/") for item in exclude):
            continue
        expected += 1
    temp = out.with_suffix(".part")
    args = ["archive", "--format=tar", f"--prefix={prefix}/", f"--output={temp}", commit]
    if exclude:
        args += ["--", ".", *[f":(exclude){item}" for item in exclude]]
    _git(store, *args)
    with tarfile.open(temp) as tar:
        found = sum(1 for member in tar if not member.isdir())
    if found != expected:
        raise SourceSetError(f"{prefix}: tar holds {found} files, the tree has {expected}")
    temp.replace(out)
    return expected, out.stat().st_size


def _download(
    urls: tuple[str, ...], sha256: str, out: Path, auth: tuple[str, str] | None = None
) -> int:
    if out.exists() and hashlib.sha256(out.read_bytes()).hexdigest() == sha256:
        return out.stat().st_size
    failures = []
    for url in urls:
        for delay in (0, 20):
            time.sleep(delay)
            try:
                digest = hashlib.sha256()
                temp = out.with_suffix(out.suffix + ".part")
                with _open(url, auth) as response, open(temp, "wb") as handle:
                    while chunk := response.read(1024 * 1024):
                        digest.update(chunk)
                        handle.write(chunk)
                if digest.hexdigest() != sha256:
                    raise SourceSetError(f"{url}: sha256 {digest.hexdigest()}, expected {sha256}")
                temp.replace(out)
                return out.stat().st_size
            except (OSError, SourceSetError) as exc:
                failures.append(f"{url}: {exc}")
    raise SourceSetError(" | ".join(failures)[-500:])


def _open(url: str, auth: tuple[str, str] | None = None):
    request = urllib.request.Request(url, headers={"User-Agent": "av-kit-source-assembly"})
    if auth is not None:
        import base64

        token = base64.b64encode(f"{auth[0]}:{auth[1]}".encode()).decode()
        request.add_header("Authorization", f"Basic {token}")
    return urllib.request.urlopen(request, timeout=120)


def svn_export(url: str, rev: str, prefix: str, out: Path) -> tuple[int, int]:
    """Walk one Subversion revision over HTTP into a tar. Returns (entries, bytes)."""
    if url not in SVN_ROOTS:
        raise SourceSetError(f"unknown Subversion source: {url}")
    root, path, auth = SVN_ROOTS[url]
    base = f"{root}/!svn/bc/{rev}/{path}"
    temp = out.with_suffix(".part")
    count = 0
    with tarfile.open(temp, "w") as tar:
        pending = [""]
        while pending:
            folder = pending.pop()
            with _open(f"{base}/{folder}", auth) as response:
                listing = response.read().decode("utf-8", "replace")
            for href in _LISTING_HREF.findall(listing):
                if href.startswith(("/", "..", "http:", "https:")) or "?" in href:
                    continue
                if href.endswith("/"):
                    pending.append(folder + href)
                    continue
                with _open(f"{base}/{folder}{href}", auth) as response:
                    data = response.read()
                info = tarfile.TarInfo(f"{prefix}/{urllib.parse.unquote(folder + href)}")
                info.size = len(data)
                info.mode = 0o755 if href.endswith(".sh") or href == "configure" else 0o644
                tar.addfile(info, io.BytesIO(data))
                count += 1
    if count == 0:
        raise SourceSetError(f"{url}@{rev}: empty listing")
    temp.replace(out)
    return count, out.stat().st_size


@dataclass
class Row:
    """One source in the archive."""

    kind: str
    path: str
    url: str
    ref: str
    resolved: str
    entries: int
    bytes: int
    scripts: list[str] = field(default_factory=list)
    file: str = ""


class Assembly:
    def __init__(self, work: Path) -> None:
        self.work = work
        self.rows: list[Row] = []
        for folder in ("git", "tars", "files", "receipts"):
            (work / folder).mkdir(parents=True, exist_ok=True)

    def store(self, url: str) -> Path:
        return self.work / "git" / f"{_slug(url)}.git"

    def tree(
        self,
        url: str,
        ref: str,
        path: str,
        scripts: list[str],
        *,
        mirror: str | None = None,
        submodules: tuple[str, ...] | None = None,
        exclude: tuple[str, ...] = (),
    ) -> str:
        """Fetch a tree and its requested submodules. Returns the commit."""
        store = self.store(url)
        commit = fetch_commit(store, url, ref, mirror)
        out = self.work / "tars" / (re.sub(r"[^A-Za-z0-9._-]+", "_", path) + ".tar")
        entries, size = archive_tree(store, commit, path, out, exclude)
        self.rows.append(Row("git", path, url, ref, commit, entries, size, scripts, str(out)))
        if submodules is None:
            return commit
        try:
            text = _git(store, "show", f"{commit}:.gitmodules").decode("utf-8", "replace")
        except SourceSetError:
            return commit
        for sub, sub_url in parse_gitmodules(text).items():
            if submodules and sub not in submodules:
                continue
            line = _git(store, "ls-tree", commit, sub).decode().strip()
            if not line.startswith("160000"):
                continue
            self.tree(
                resolve_url(url, sub_url), line.split()[2], f"{path}/{sub}", scripts, submodules=()
            )
        return commit

    def file(
        self,
        urls: tuple[str, ...],
        sha256: str,
        path: str,
        scripts: list[str],
        kind: str,
        ref: str,
        auth: tuple[str, str] | None = None,
    ) -> None:
        out = self.work / "files" / (re.sub(r"[^A-Za-z0-9._-]+", "_", path))
        size = _download(urls, sha256, out, auth)
        self.rows.append(Row(kind, path, urls[0], ref, sha256, 1, size, scripts, str(out)))

    def crates(self, store: Path, commit: str, scripts: list[str]) -> None:
        text = _git(store, "show", f"{commit}:Cargo.lock").decode("utf-8", "replace")
        for name, version, sha256 in parse_cargo_lock(text):
            url = f"https://static.crates.io/crates/{name}/{name}-{version}.crate"
            path = f"crates/{name}-{version}.crate"
            if path not in {row.path for row in self.rows}:
                self.file((url,), sha256, path, scripts, "crate", version)

    def recipe_scripts(self) -> dict[str, str]:
        store = self.store(BUILDS_REPO)
        commit = fetch_commit(store, BUILDS_REPO, BUILDS_COMMIT)
        names = (
            _git(store, "ls-tree", "-r", "--name-only", commit, "scripts.d").decode().split("\n")
        )
        scripts = {}
        for name in names:
            if name.endswith(".sh"):
                scripts[name.removeprefix("scripts.d/")] = _git(
                    store, "show", f"{commit}:{name}"
                ).decode("utf-8", "replace")
        if not scripts:
            raise SourceSetError("the recipe has no scripts")
        return scripts

    def collect(self, jobs: int = 6) -> None:
        self.tree(BUILDS_REPO, BUILDS_COMMIT, "ffmpeg-builds", ["recipe"])
        self.tree(FFMPEG_REPO, FFMPEG_COMMIT, "ffmpeg", ["ffmpeg"])
        wanted: dict[tuple[str, str], dict] = {}
        for name, text in sorted(self.recipe_scripts().items()):
            if not enabled_for_build(text):
                continue
            plan = fetch_plan(name, text)
            for source in script_sources(text):
                key = (source["url"], source.get("ref") or source["rev"])
                entry = wanted.setdefault(
                    key, {"source": source, "scripts": [], "plan": FetchPlan(), "exclude": ()}
                )
                entry["scripts"].append(name)
                if not source["suffix"]:
                    entry["plan"] = plan
                    entry["exclude"] = ARCHIVE_EXCLUDES.get(name, ())

        def one(item: tuple[tuple[str, str], dict]) -> None:
            (url, ref), entry = item
            source, plan, scripts = entry["source"], entry["plan"], entry["scripts"]
            path = f"deps/{_repo_name(url)}-{ref[:12]}"
            if "rev" in source:
                out = self.work / "tars" / (re.sub(r"[^A-Za-z0-9._-]+", "_", path) + ".tar")
                entries, size = svn_export(url, ref, path, out)
                self.rows.append(Row("svn", path, url, ref, ref, entries, size, scripts, str(out)))
                return
            commit = self.tree(
                url,
                ref,
                path,
                scripts,
                mirror=source.get("mirror"),
                submodules=plan.submodules,
                exclude=entry["exclude"],
            )
            store = self.store(url)
            if plan.sync_deps:
                deps = parse_deps(_git(store, "show", f"{commit}:DEPS").decode("utf-8", "replace"))
                for sub, (sub_url, rev) in deps.items():
                    self.tree(sub_url, rev, f"{path}/{sub}", scripts)
            if plan.cargo:
                self.crates(store, commit, scripts)
            for wrap in plan.wraps:
                text = _git(store, "show", f"{commit}:subprojects/{wrap}.wrap").decode(
                    "utf-8", "replace"
                )
                urls = tuple(re.findall(r"^source(?:_fallback)?_url\s*=\s*(\S+)", text, re.M))
                digest = re.search(r"^source_hash\s*=\s*(\S+)", text, re.M)[1]
                filename = re.search(r"^source_filename\s*=\s*(\S+)", text, re.M)[1]
                self.file(
                    urls,
                    digest,
                    f"{path}/subprojects/packagecache/{filename}",
                    scripts,
                    "wrap",
                    wrap,
                )
            if plan.opus_model:
                digest = _OPUS_MODEL.search(
                    _git(store, "show", f"{commit}:autogen.sh").decode("utf-8", "replace")
                )[1]
                filename = f"opus_data-{digest}.tar.gz"
                self.file(
                    (f"https://media.xiph.org/opus/models/{filename}",),
                    digest,
                    f"{path}/{filename}",
                    scripts,
                    "model",
                    digest,
                )

        with ThreadPoolExecutor(max_workers=jobs) as pool:
            failures = [
                exc for exc in pool.map(lambda item: _guard(one, item), wanted.items()) if exc
            ]
        if failures:
            raise SourceSetError("\n".join(failures))
        self.toolchain()

    def toolchain(self) -> None:
        store = self.store(BUILDS_REPO)
        config = _git(store, "show", f"{BUILDS_COMMIT}:images/base-win64/ct-ng-config").decode(
            "utf-8", "replace"
        )
        recorded = dict(re.findall(r'^(CT_[A-Z0-9_]+)="([^"]*)"', config, re.M))
        if recorded.get("CT_VERSION") != CROSSTOOL_VERSION:
            raise SourceSetError(f"crosstool-NG config moved: {recorded.get('CT_VERSION')}")
        self.tree(
            CROSSTOOL_REPO,
            CROSSTOOL_COMMIT,
            f"toolchain/crosstool-ng-{CROSSTOOL_COMMIT[:12]}",
            ["toolchain"],
        )
        crosstool = self.store(CROSSTOOL_REPO)
        for tool in TOOLCHAIN:
            if recorded.get(tool.config) != tool.version:
                raise SourceSetError(
                    f"{tool.config} is {recorded.get(tool.config)}, this file has {tool.version}"
                )
            chksum = _git(
                crosstool,
                "show",
                f"{CROSSTOOL_COMMIT}:packages/{tool.package}/{tool.version}/chksum",
            ).decode("utf-8", "replace")
            self.file(
                tool.urls,
                parse_chksum(chksum, tool.file),
                f"toolchain/{tool.package}-{tool.version}-{tool.file}",
                ["toolchain"],
                "toolchain",
                tool.version,
            )

    def readme(self) -> str:
        return f"""# Complete corresponding source for av-kit's bundled FFmpeg

av-kit's installer ships `ffmpeg.exe` and `ffprobe.exe` from BtbN's build `{BUILD_ASSET}`
(release `{BUILD_TAG}`, SHA-256 `{BUILD_SHA256}`), licensed under the GPL, version 3. This
archive holds its source.

- `ffmpeg/`: FFmpeg at commit `{FFMPEG_COMMIT}`.
- `ffmpeg-builds/`: BtbN's build recipe at commit `{BUILDS_COMMIT}`, with its patches. Each
  script in `scripts.d/` names the dependency it builds and how.
- `deps/`: every dependency that recipe enables for this build, at the commit or revision it pins,
  with the submodules, model data and Meson subprojects its fetch steps add.
- `crates/`: the Rust crates that `Cargo.lock` pins for rav1e and librsvg.
- `toolchain/`: crosstool-NG at the commit recorded in the recipe's config, and the GCC, binutils,
  MinGW-w64, mold and support library versions that config selects.
- `MANIFEST.tsv`: each item, where it came from, the exact commit or checksum and which script
  uses it.
- `FETCH-HINTS.tsv`: files inside those trees that could fetch more while building.

The recipe does not pin everything it uses, so these are not in the archive or are not exact:

- crosstool-NG's commit: the Dockerfile clones its newest commit when the image is built, so the
  commit here is the one the config was saved with.
- The Rust compiler and cargo-c (installed from rustup and crates.io without a version), Meson
  (installed with pip), the Ubuntu 26.04 base image and its packages. These are general-purpose
  tools used unmodified.
- rav1e's `cc` crate: the recipe runs `cargo update cc` while building. `cc` is a build tool and
  doesn't reach the binary. The archive holds the version in rav1e's `Cargo.lock`.
- Meson wraps and CMake download steps inside the dependency trees. None adds code to the binary:
  the recipe's options turn them off, its other dependencies satisfy them, or they serve tests and
  documentation. dav1d's test tool `checkasm` is one Meson can fetch while building.

To build it, follow BtbN's `README.md` with target `win64`, variant `gpl` and add-in `8.1`.
"""

    def manifest(self) -> str:
        lines = ["kind\tpath\turl\trequested\tresolved\tentries\tbytes\tused_by"]
        for row in sorted(self.rows, key=lambda item: item.path):
            lines.append(
                "\t".join(
                    (
                        row.kind,
                        row.path,
                        row.url,
                        row.ref,
                        row.resolved,
                        str(row.entries),
                        str(row.bytes),
                        ",".join(row.scripts),
                    )
                )
            )
        return "\n".join(lines) + "\n"

    def hint_table(self) -> str:
        lines = ["path\tfile"]
        for row in sorted(self.rows, key=lambda item: item.path):
            if row.kind == "git":
                hints = fetch_hints(self.store(row.url), row.resolved)
                lines += [f"{row.path}\t{name}" for name in hints]
        return "\n".join(lines) + "\n"

    def report(self) -> None:
        total = sum(row.bytes for row in self.rows)
        print(f"sources {len(self.rows)}; bytes before compression {total:,}")
        by_kind: dict[str, list[int]] = {}
        for row in self.rows:
            by_kind.setdefault(row.kind, []).append(row.bytes)
        for kind, sizes in sorted(by_kind.items()):
            print(f"  {kind}: {len(sizes)} items, {sum(sizes):,} bytes")
        print("largest:")
        for row in sorted(self.rows, key=lambda item: -item.bytes)[:20]:
            print(f"  {row.bytes:>13,}  {row.path}")
        (self.work / "manifest.json").write_text(
            json.dumps([asdict(row) for row in self.rows], indent=1), encoding="utf-8"
        )
        hints = self.hint_table()
        (self.work / "receipts" / "fetch-hints.txt").write_text(hints, encoding="utf-8")
        print(f"files that can fetch more while building: {hints.count(chr(10)) - 1}")

    def pack(self, out: Path) -> tuple[int, str]:
        """Write the one archive and read it back against the manifest. Returns (bytes, sha256)."""
        temp = out.with_suffix(".part")
        root = ARCHIVE_NAME
        with tarfile.open(temp, "w:xz", preset=6) as tar:
            documents = (self.readme(), self.manifest(), self.hint_table())
            for name, text in zip(DOCUMENTS, documents, strict=True):
                data = text.encode("utf-8")
                info = tarfile.TarInfo(f"{root}/{name}")
                info.size, info.mode = len(data), 0o644
                tar.addfile(info, io.BytesIO(data))
            for row in sorted(self.rows, key=lambda item: item.path):
                if row.kind in {"git", "svn"}:
                    with tarfile.open(row.file) as inner:
                        for member in inner:
                            # A pax header outranks the name, and git's holds the path without
                            # this archive's root.
                            member.pax_headers = {}
                            member.name = f"{root}/{member.name}"
                            if member.islnk():
                                member.linkname = f"{root}/{member.linkname}"
                            tar.addfile(
                                member, inner.extractfile(member) if member.isreg() else None
                            )
                else:
                    info = tarfile.TarInfo(f"{root}/{row.path}")
                    info.size, info.mode = row.bytes, 0o644
                    with open(row.file, "rb") as handle:
                        tar.addfile(info, handle)
        self.verify(temp)
        temp.replace(out)
        digest = hashlib.sha256()
        with open(out, "rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        return out.stat().st_size, digest.hexdigest()

    def verify(self, out: Path) -> None:
        found: dict[str, int] = {}
        documents: set[str] = set()
        stray: list[str] = []
        roots = sorted((row.path for row in self.rows), key=len, reverse=True)
        with tarfile.open(out, "r:xz") as tar:
            for member in tar:
                if member.isdir():
                    continue
                if not member.name.startswith(f"{ARCHIVE_NAME}/"):
                    stray.append(member.name)
                    continue
                name = member.name.split("/", 1)[1]
                owner = next(
                    (path for path in roots if name == path or name.startswith(path + "/")), None
                )
                if owner is not None:
                    found[owner] = found.get(owner, 0) + 1
                elif name in DOCUMENTS:
                    documents.add(name)
                else:
                    stray.append(member.name)
        problems = [
            f"{row.path}: {found.get(row.path, 0)} of {row.entries}"
            for row in self.rows
            if found.get(row.path, 0) != row.entries
        ]
        problems += [f"missing {name}" for name in DOCUMENTS if name not in documents]
        problems += [f"not in the manifest: {name}" for name in stray[:20]]
        if problems:
            raise SourceSetError("archive disagrees with the manifest:\n" + "\n".join(problems))


def _guard(function, item) -> str | None:
    try:
        function(item)
    except Exception as exc:  # noqa: BLE001  every failure is reported together and stops the run
        return f"{item[0]}: {exc}"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--measure-only", action="store_true")
    parser.add_argument("--jobs", type=int, default=6)
    parser.add_argument("--ffmpeg-exe", type=Path, help="the ffmpeg.exe the installer ships")
    args = parser.parse_args(argv)
    if args.ffmpeg_exe is None and not args.measure_only:
        parser.error("an archive needs --ffmpeg-exe, to check it against the binary it's for")
    assembly = Assembly(args.work)
    if args.ffmpeg_exe is not None:
        try:
            unused = check_configuration(
                _version_output(args.ffmpeg_exe), assembly.recipe_scripts()
            )
        except SourceSetError as exc:
            print(f"the binary doesn't match the source set:\n{exc}", file=sys.stderr)
            return 5
        print("configuration line explained; flags the binary doesn't use:", *unused or ["none"])
    try:
        assembly.collect(args.jobs)
    except SourceSetError as exc:
        print(f"source set incomplete:\n{exc}", file=sys.stderr)
        return 2
    assembly.report()
    if args.measure_only:
        return 0
    out = args.work / f"{ARCHIVE_NAME}.tar.xz"
    try:
        size, digest = assembly.pack(out)
    except SourceSetError as exc:
        print(f"source archive failed its check:\n{exc}", file=sys.stderr)
        return 3
    print(f"archive {out} {size:,} bytes sha256 {digest}")
    if size > ASSET_LIMIT:
        print(f"over GitHub's release asset limit of {ASSET_LIMIT:,} bytes", file=sys.stderr)
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
