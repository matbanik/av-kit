"""MEU-110 source tool: AC-110.20 and AC-110.21 on small fixtures.

Each refusal is proved with a bad input, because the tool came before these tests (ECN-6). Nothing
here reaches the network. The real run and its receipts are the plan's row 9f.
"""

from __future__ import annotations

import hashlib
import io
import subprocess
import tarfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = """#!/bin/bash

SCRIPT_REPO="https://example.invalid/lib.git"
SCRIPT_COMMIT="0123456789abcdef0123456789abcdef01234567"

ffbuild_enabled() {
    [[ $TARGET == linux* ]] && return -1
    return 0
}

ffbuild_dockerdl() {
    default_dl .
    echo "git submodule update --init --recursive --depth=1 third_party/a third_party/b"
}

ffbuild_dockerbuild() {
    make -j$(nproc)
}

ffbuild_configure() {
    echo --enable-libfixture
}

ffbuild_unconfigure() {
    echo --disable-libfixture
}
"""
OFF_SCRIPT = SCRIPT.replace("[[ $TARGET == linux* ]] && return -1", "return -1").replace(
    "lib.git", "off.git"
)
TREE = {
    ".gitattributes": b"ignored.txt export-ignore\nsubst.txt export-subst\n",
    "ignored.txt": b"kept\n",
    "subst.txt": b"$Format:%H$\n",
    "lf.txt": b"one\ntwo\n",
    "crlf.txt": b"one\r\ntwo\r\n",
    "folder/binary.dat": bytes(range(256)),
}
# Too long for a tar name field, so git writes it as a pax header.
LONG_NAME = "f" * 120 + ".txt"


def _tool():
    from tools import assemble_ffmpeg_source

    return assemble_ffmpeg_source


def _git(where: Path, *args: str) -> str:
    done = subprocess.run(
        [
            "git", "-C", str(where),
            "-c", "core.autocrlf=false", "-c", "commit.gpgsign=false",
            "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
            *args,
        ],
        capture_output=True,
        check=True,
    )  # fmt: skip
    return done.stdout.decode().strip()


def _store(
    tmp_path: Path, files: dict[str, bytes], *, gitlink: str = "", at: Path | None = None
) -> tuple[Path, str]:
    """A bare store with one commit. Returns (store, commit)."""
    repo = tmp_path / f"repo-{len(list(tmp_path.iterdir()))}"
    repo.mkdir()
    _git(repo, "init", "--quiet", "--template=")
    for name, data in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    _git(repo, "add", "-A")
    if gitlink:
        _git(repo, "update-index", "--add", "--cacheinfo", f"160000,{'a' * 40},{gitlink}")
    _git(repo, "commit", "--quiet", "-m", "fixture")
    commit = _git(repo, "rev-parse", "HEAD")
    store = at or tmp_path / f"{repo.name}.git"
    store.parent.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "clone", "--quiet", "--bare", str(repo), str(store))
    return store, commit


def _tar_files(path: Path, mode: str = "r") -> dict[str, bytes]:
    with tarfile.open(path, mode) as tar:
        return {member.name: tar.extractfile(member).read() for member in tar if member.isreg()}


# Which scripts are on


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("return 0", True),
        ("return -1", False),
        ("[[ $TARGET == win* ]] && return 0\n    return -1", True),
        ("[[ $TARGET == linux* ]] && return 0\n    return -1", False),
        ("[[ $TARGET != win64 ]] && return -1\n    return 0", True),
        ("[[ $VARIANT == lgpl* ]] && return -1\n    return 0", True),
        ("[[ $VARIANT == gpl* ]] && return -1\n    return 0", False),
        ("[[ $ADDINS_STR == *4.4* ]] && return -1\n    return 0", True),
        ("(( $(ffbuild_ffver) >= 900 )) || return -1\n    return 0", False),
        ("(( $(ffbuild_ffver) >= 800 )) || return -1\n    return 0", True),
        ("(( $(ffbuild_ffver) < 800 )) && return -1\n    return 0", True),
        ("# A note.\n    return 0", True),
    ],
)
def test_ac_110_20_reads_when_a_script_is_on(body: str, expected: bool) -> None:
    text = f"ffbuild_enabled() {{\n    {body}\n}}\n"
    assert _tool().enabled_for_build(text) is expected


@pytest.mark.parametrize(
    "text",
    [
        "no function here\n",
        "ffbuild_enabled() {\n    some_check && return -1\n    return 0\n}\n",
        "ffbuild_enabled() {\n    if something; then\n        return -1\n    fi\n}\n",
    ],
)
def test_ac_110_20_a_condition_it_cant_read_counts_as_on(text: str) -> None:
    assert _tool().enabled_for_build(text) is True


# What a script fetches


def test_ac_110_20_reads_a_known_fetch_step() -> None:
    plan = _tool().fetch_plan("50-lib.sh", SCRIPT)
    assert plan.submodules == ("third_party/a", "third_party/b")
    assert plan.cargo is False


@pytest.mark.parametrize(
    ("step", "field", "expected"),
    [
        ('echo "git submodule update --init --recursive"', "submodules", ()),
        (
            'echo "git submodule update --init --depth 1 third_party/a"',
            "submodules",
            ("third_party/a",),
        ),
        ('echo "cd lib && ./utils/git-sync-deps"', "sync_deps", True),
        ('echo "cargo vendor"', "cargo", True),
        ('echo "meson subprojects download proxy-libintl"', "wraps", ("proxy-libintl",)),
        ('echo "./autogen.sh"', "opus_model", True),
    ],
)
def test_ac_110_20_reads_each_fetch_kind(step: str, field: str, expected: object) -> None:
    text = f"ffbuild_dockerdl() {{\n    {step}\n}}\n"
    assert getattr(_tool().fetch_plan("50-lib.sh", text), field) == expected


@pytest.mark.parametrize(
    "step",
    ['echo "curl -L https://example.invalid/x.tar.gz | tar xz"', "mystery_helper", 'echo "wget x"'],
)
def test_ac_110_20_an_unknown_fetch_step_stops_the_run(step: str) -> None:
    tool = _tool()
    text = f"ffbuild_dockerdl() {{\n    {step}\n}}\n"
    with pytest.raises(tool.SourceSetError, match="unknown fetch step"):
        tool.fetch_plan("50-lib.sh", text)


@pytest.mark.parametrize(
    "step",
    [
        "git clone https://example.invalid/x.git",
        "curl -L https://example.invalid/x",
        "cargo fetch",
        "pip install x",
        "meson subprojects download",
    ],
)
def test_ac_110_20_a_build_step_that_fetches_stops_the_run(step: str) -> None:
    tool = _tool()
    text = f"ffbuild_dockerbuild() {{\n    {step}\n}}\n"
    with pytest.raises(tool.SourceSetError, match="a build step fetches more"):
        tool.fetch_plan("50-lib.sh", text)


def test_ac_110_20_only_the_named_script_may_use_cargo_while_building() -> None:
    plan = _tool().fetch_plan("50-rav1e.sh", "ffbuild_dockerbuild() {\n    cargo update cc\n}\n")
    assert plan.cargo is True


def test_ac_110_20_reads_every_pin_a_script_names() -> None:
    text = (
        'SCRIPT_REPO="https://example.invalid/a.git"\n'
        'SCRIPT_COMMIT="abc1234"\n'
        'SCRIPT_MIRROR="https://mirror.invalid/a.git"\n'
        'SCRIPT_REPO2="https://example.invalid/svn"\n'
        "SCRIPT_REV2=1234\n"
    )
    assert _tool().script_sources(text) == [
        {
            "url": "https://example.invalid/a.git",
            "suffix": "",
            "ref": "abc1234",
            "mirror": "https://mirror.invalid/a.git",
        },
        {"url": "https://example.invalid/svn", "suffix": "2", "rev": "1234"},
    ]


def test_ac_110_20_a_source_without_a_pin_stops_the_run() -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError, match="no pin"):
        tool.script_sources('SCRIPT_REPO="https://example.invalid/a.git"\n')


# Lists a repository brings with it


def test_ac_110_20_reads_gitmodules() -> None:
    text = (
        '[submodule "a"]\n\tpath = third_party/a\n\turl = https://example.invalid/a.git\n'
        '[submodule "b"]\n\tpath = third_party/b\n\turl = ../b.git\n'
    )
    assert _tool().parse_gitmodules(text) == {
        "third_party/a": "https://example.invalid/a.git",
        "third_party/b": "../b.git",
    }


def test_ac_110_20_resolves_a_relative_submodule_url() -> None:
    assert (
        _tool().resolve_url("https://example.invalid/org/parent.git", "../b.git")
        == "https://example.invalid/org/b.git"
    )


@pytest.mark.parametrize(
    "url",
    ["http://example.invalid/a.git", "git://example.invalid/a.git", "git@example.invalid:a.git"],
)
def test_ac_110_20_refuses_a_source_that_isnt_https(url: str) -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError, match="not an https source"):
        tool.resolve_url("https://example.invalid/parent.git", url)


def test_ac_110_20_git_itself_refuses_another_protocol(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    monkeypatch.setattr(tool.time, "sleep", lambda _delay: None)
    source, commit = _store(tmp_path, {"a.txt": b"a\n"})
    with pytest.raises(tool.SourceSetError):
        tool.fetch_commit(tmp_path / "store.git", source.as_uri(), commit)


def test_ac_110_20_reads_deps_without_running_it() -> None:
    text = """
vars = {
  'chromium_git': 'https://chromium.googlesource.com',
  'abseil_revision': 'aaaa',
}
deps = {
  'third_party/abseil': Var('chromium_git') + '/abseil/abseil-cpp@' + Var('abseil_revision'),
}
"""
    assert _tool().parse_deps(text) == {
        "third_party/abseil": ("https://chromium.googlesource.com/abseil/abseil-cpp", "aaaa")
    }


def test_ac_110_20_an_empty_deps_stops_the_run() -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError, match="no dependency"):
        tool.parse_deps("vars = {}\ndeps = {}\n")


def test_ac_110_20_reads_registry_crates_and_skips_the_project_itself() -> None:
    text = (
        '[[package]]\nname = "a"\nversion = "1.0.0"\n'
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n'
        'checksum = "abc"\n\n'
        '[[package]]\nname = "local"\nversion = "0.1.0"\n'
    )
    assert _tool().parse_cargo_lock(text) == [("a", "1.0.0", "abc")]


@pytest.mark.parametrize(
    "fields",
    [
        'source = "git+https://github.com/example/a#deadbeef"\nchecksum = "abc"\n',
        'source = "registry+https://github.com/rust-lang/crates.io-index"\n',
    ],
)
def test_ac_110_20_a_crate_from_outside_the_registry_stops_the_run(fields: str) -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError, match="isn't a checked registry crate"):
        tool.parse_cargo_lock(f'[[package]]\nname = "a"\nversion = "1.0.0"\n{fields}')


def test_ac_110_20_reads_a_toolchain_checksum_and_refuses_when_absent() -> None:
    tool = _tool()
    digest = "a" * 64
    text = f"md5  gcc.tar.xz  {'b' * 32}\nsha256  gcc.tar.xz  {digest}\n"
    assert tool.parse_chksum(text, "gcc.tar.xz") == digest
    with pytest.raises(tool.SourceSetError, match="no sha256"):
        tool.parse_chksum(text, "other.tar.xz")


def test_ac_110_20_a_download_with_the_wrong_checksum_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    monkeypatch.setattr(tool.time, "sleep", lambda _delay: None)
    source = tmp_path / "source.bin"
    source.write_bytes(b"data")
    good = hashlib.sha256(b"data").hexdigest()
    out = tmp_path / "out.bin"
    with pytest.raises(tool.SourceSetError, match="sha256"):
        tool._download((source.as_uri(),), "0" * 64, out)
    assert not out.exists()
    assert tool._download((source.as_uri(),), good, out) == 4
    assert out.read_bytes() == b"data"


def test_ac_110_20_an_unnamed_subversion_source_stops_the_run(tmp_path: Path) -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError, match="unknown Subversion source"):
        tool.svn_export("https://example.invalid/svn", "1", "deps/x", tmp_path / "x.tar")


# The whole walk


def test_ac_110_20_collects_enabled_scripts_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    assembly = tool.Assembly(tmp_path)
    fetched: list[tuple[str, tuple[str, ...] | None]] = []

    def tree(url, _ref, _path, _scripts, *, submodules=None, **_kwargs):
        fetched.append((url, submodules))
        return "0" * 40

    monkeypatch.setattr(assembly, "tree", tree)
    monkeypatch.setattr(assembly, "toolchain", lambda: None)
    monkeypatch.setattr(
        assembly, "recipe_scripts", lambda: {"50-lib.sh": SCRIPT, "50-off.sh": OFF_SCRIPT}
    )
    assembly.collect(jobs=1)
    urls = [url for url, _submodules in fetched]
    assert urls == [tool.BUILDS_REPO, tool.FFMPEG_REPO, "https://example.invalid/lib.git"]
    assert fetched[-1][1] == ("third_party/a", "third_party/b")


def test_ac_110_20_an_unknown_step_stops_the_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    assembly = tool.Assembly(tmp_path)
    bad = SCRIPT.replace("default_dl .", 'echo "curl https://example.invalid/x"')
    monkeypatch.setattr(assembly, "tree", lambda *_args, **_kwargs: "0" * 40)
    monkeypatch.setattr(assembly, "toolchain", lambda: None)
    monkeypatch.setattr(assembly, "recipe_scripts", lambda: {"50-lib.sh": bad})
    with pytest.raises(tool.SourceSetError, match="unknown fetch step"):
        assembly.collect(jobs=1)


def test_ac_110_20_a_source_that_fails_stops_the_walk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    assembly = tool.Assembly(tmp_path)

    def tree(url, *_args, **_kwargs):
        if url == "https://example.invalid/lib.git":
            raise tool.SourceSetError("the source is gone")
        return "0" * 40

    monkeypatch.setattr(assembly, "tree", tree)
    monkeypatch.setattr(assembly, "toolchain", lambda: None)
    monkeypatch.setattr(assembly, "recipe_scripts", lambda: {"50-lib.sh": SCRIPT})
    with pytest.raises(tool.SourceSetError, match="the source is gone"):
        assembly.collect(jobs=1)


@pytest.mark.parametrize(
    ("config", "message"),
    [
        ('CT_VERSION="9.9"\n', "crosstool-NG config moved"),
        (None, "CT_GCC_VERSION is 1"),
    ],
)
def test_ac_110_20_a_toolchain_that_moved_stops_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config: str | None, message: str
) -> None:
    tool = _tool()
    assembly = tool.Assembly(tmp_path / "work")
    text = config or f'CT_VERSION="{tool.CROSSTOOL_VERSION}"\nCT_GCC_VERSION="1"\n'
    (tmp_path / "fixture").mkdir()
    _store_at, commit = _store(
        tmp_path / "fixture",
        {"images/base-win64/ct-ng-config": text.encode()},
        at=assembly.store(tool.BUILDS_REPO),
    )
    monkeypatch.setattr(tool, "BUILDS_COMMIT", commit)
    monkeypatch.setattr(assembly, "tree", lambda *_args, **_kwargs: "0" * 40)
    with pytest.raises(tool.SourceSetError, match=message):
        assembly.toolchain()


# The tree and the archive


def test_ac_110_20_archive_keeps_every_tracked_file_byte_for_byte(tmp_path: Path) -> None:
    tool = _tool()
    store, commit = _store(tmp_path, TREE, gitlink="third_party/sub")
    out = tmp_path / "tree.tar"
    entries, size = tool.archive_tree(store, commit, "deps/x", out)
    files = _tar_files(out)
    assert files == {f"deps/x/{name}": data for name, data in TREE.items()}
    assert entries == len(TREE)
    assert size == out.stat().st_size


def test_ac_110_20_archive_leaves_out_only_what_the_recipe_deletes(tmp_path: Path) -> None:
    tool = _tool()
    store, commit = _store(tmp_path, {"keep.txt": b"k\n", "Thirdparty/gone.txt": b"g\n"})
    out = tmp_path / "tree.tar"
    entries, _size = tool.archive_tree(store, commit, "deps/x", out, ("Thirdparty",))
    assert entries == 1
    assert list(_tar_files(out)) == ["deps/x/keep.txt"]


def test_ac_110_20_a_tree_that_loses_a_file_stops_the_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    store, commit = _store(tmp_path, {"a.txt": b"a\n"})
    real = tool._git

    def with_one_more(where, *args, **kwargs):
        output = real(where, *args, **kwargs)
        if args[0] == "ls-tree":
            output += b"100644 blob " + b"0" * 40 + b"\tmissing.txt\0"
        return output

    monkeypatch.setattr(tool, "_git", with_one_more)
    out = tmp_path / "tree.tar"
    with pytest.raises(tool.SourceSetError, match="tar holds 1 files, the tree has 2"):
        tool.archive_tree(store, commit, "deps/x", out)
    assert not out.exists()


def _assembly_with_one_tree(tmp_path: Path):
    tool = _tool()
    work = tmp_path / "work"
    assembly = tool.Assembly(work)
    url = "https://example.invalid/lib.git"
    fixture = tmp_path / "fixture"
    fixture.mkdir()
    files = {**TREE, LONG_NAME: b"long\n", "subprojects/x.wrap": b"[wrap-file]\n"}
    store, commit = _store(fixture, files, at=assembly.store(url))
    tar = work / "tars" / "deps_lib.tar"
    entries, size = tool.archive_tree(store, commit, "deps/lib", tar)
    assembly.rows.append(
        tool.Row("git", "deps/lib", url, commit, commit, entries, size, ["50-lib.sh"], str(tar))
    )
    crate = work / "files" / "crate"
    crate.write_bytes(b"crate bytes")
    assembly.rows.append(
        tool.Row("crate", "crates/a-1.crate", "https://x.invalid", "1", "0", 1, 11, [], str(crate))
    )
    return tool, assembly, files


def test_ac_110_20_the_archive_holds_every_source_under_its_root(tmp_path: Path) -> None:
    tool, assembly, files = _assembly_with_one_tree(tmp_path)
    out = tmp_path / f"{tool.ARCHIVE_NAME}.tar.xz"
    size, digest = assembly.pack(out)
    assert (size, digest) == (out.stat().st_size, hashlib.sha256(out.read_bytes()).hexdigest())
    packed = _tar_files(out, "r:xz")
    root = tool.ARCHIVE_NAME
    for name, data in files.items():
        assert packed[f"{root}/deps/lib/{name}"] == data
    assert packed[f"{root}/crates/a-1.crate"] == b"crate bytes"
    assert all(name.startswith(f"{root}/") for name in packed)
    assert not out.with_suffix(".part").exists()


def test_ac_110_20_the_archive_says_what_it_holds_and_lacks(tmp_path: Path) -> None:
    tool, assembly, _files = _assembly_with_one_tree(tmp_path)
    out = tmp_path / f"{tool.ARCHIVE_NAME}.tar.xz"
    assembly.pack(out)
    packed = _tar_files(out, "r:xz")
    root = tool.ARCHIVE_NAME
    readme = packed[f"{root}/README.md"].decode()
    pins = (
        tool.FFMPEG_COMMIT,
        tool.BUILDS_COMMIT,
        tool.BUILD_ASSET,
        tool.BUILD_TAG,
        tool.BUILD_SHA256,
    )
    for pin in pins:
        assert pin in readme
    for tool_name in ("Rust", "cargo-c", "Meson", "Ubuntu", "crosstool-NG", "`cc`", "checkasm"):
        assert tool_name in readme
    manifest = packed[f"{root}/MANIFEST.tsv"].decode()
    assert "deps/lib\thttps://example.invalid/lib.git" in manifest
    assert packed[f"{root}/FETCH-HINTS.tsv"].decode().splitlines() == [
        "path\tfile",
        "deps/lib\tsubprojects/x.wrap",
    ]


def test_ac_110_20_an_archive_that_disagrees_with_the_manifest_is_refused(tmp_path: Path) -> None:
    tool, assembly, _files = _assembly_with_one_tree(tmp_path)
    assembly.rows[0].entries += 1
    out = tmp_path / f"{tool.ARCHIVE_NAME}.tar.xz"
    with pytest.raises(tool.SourceSetError, match="deps/lib: "):
        assembly.pack(out)
    assert not out.exists()


@pytest.mark.parametrize(
    "name",
    ["outside/file.txt", f"{_tool().ARCHIVE_NAME}/unlisted.txt"],
)
def test_ac_110_20_a_file_the_manifest_doesnt_list_is_refused(tmp_path: Path, name: str) -> None:
    tool = _tool()
    assembly = tool.Assembly(tmp_path / "work")
    path = tmp_path / "bad.tar.xz"
    with tarfile.open(path, "w:xz") as tar:
        for member in (*(f"{tool.ARCHIVE_NAME}/{doc}" for doc in tool.DOCUMENTS), name):
            info = tarfile.TarInfo(member)
            info.size = 1
            tar.addfile(info, io.BytesIO(b"x"))
    with pytest.raises(tool.SourceSetError, match="not in the manifest"):
        assembly.verify(path)


def test_ac_110_20_an_archive_missing_a_document_is_refused(tmp_path: Path) -> None:
    tool = _tool()
    assembly = tool.Assembly(tmp_path / "work")
    path = tmp_path / "bad.tar.xz"
    with tarfile.open(path, "w:xz"):
        pass
    with pytest.raises(tool.SourceSetError, match="missing README.md"):
        assembly.verify(path)


def test_ac_110_20_lists_what_can_fetch_more_while_building(tmp_path: Path) -> None:
    tool = _tool()
    store, commit = _store(
        tmp_path,
        {
            "subprojects/x.wrap": b"[wrap-file]\n",
            "CMakeLists.txt": b"FetchContent_Declare(x)\n",
            "cmake/more.cmake": b"ExternalProject_Add(y)\n",
            "plain.txt": b"nothing\n",
        },
    )
    assert tool.fetch_hints(store, commit) == [
        "CMakeLists.txt",
        "cmake/more.cmake",
        "subprojects/x.wrap",
    ]
    empty, commit = _store(tmp_path, {"plain.txt": b"nothing\n"})
    assert tool.fetch_hints(empty, commit) == []


# The binary against the recipe


def test_ac_110_21_the_pin_is_one_fact() -> None:
    tool = _tool()
    fetch = (REPO_ROOT / "tools" / "fetch_ffmpeg_windows.ps1").read_text(encoding="utf-8")
    notices = (REPO_ROOT / "packaging" / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    build = tool.BUILD_ASSET.removeprefix("ffmpeg-").removesuffix("-win64-gpl-8.1.zip")
    assert build.endswith(f"-g{tool.FFMPEG_COMMIT[:10]}")
    assert f"# Pin: BtbN {tool.BUILD_TAG} win64 gpl" in fetch
    assert f"releases/download/{tool.BUILD_TAG}/{tool.BUILD_ASSET}" in fetch
    assert tool.BUILD_SHA256.upper() in fetch
    for needle in (build, tool.BUILD_TAG, tool.FFMPEG_COMMIT, f"{tool.ARCHIVE_NAME}.tar.xz"):
        assert needle in notices, needle
    assert build in readme


def _version_output(*flags: str) -> str:
    commit = _tool().FFMPEG_COMMIT[:10]
    return (
        f"ffmpeg version n8.1.3-27-g{commit}-20261031 Copyright (c) 2000-2026 the developers\n"
        "built with gcc 16.2.0\n"
        f"configuration: --prefix=/ffbuild/prefix {' '.join(flags)} --extra-version=20261031\n"
    )


def test_ac_110_21_every_flag_in_the_binary_comes_from_the_source_set() -> None:
    output = _version_output(
        "--enable-gpl", "--enable-version3", "--enable-libfixture", "--disable-x"
    )
    assert _tool().check_configuration(output, {"50-lib.sh": SCRIPT}) == []


def test_ac_110_21_a_flag_the_binary_doesnt_use_is_only_reported() -> None:
    output = _version_output("--enable-gpl")
    assert _tool().check_configuration(output, {"50-lib.sh": SCRIPT}) == ["--enable-libfixture"]


@pytest.mark.parametrize(
    ("output", "scripts", "message"),
    [
        (_version_output("--enable-libother"), {"50-lib.sh": SCRIPT}, "--enable-libother"),
        (_version_output("--enable-libfixture"), {"50-off.sh": OFF_SCRIPT}, "--enable-libfixture"),
        (
            _version_output("--enable-libfixture").replace(_tool().FFMPEG_COMMIT[:10], "0" * 10),
            {"50-lib.sh": SCRIPT},
            "not the pinned build",
        ),
        ("", {"50-lib.sh": SCRIPT}, "not the pinned build"),
        (
            _version_output("--enable-libfixture").split("configuration:")[0],
            {"50-lib.sh": SCRIPT},
            "no configuration line",
        ),
    ],
    ids=["no-script", "script-off", "other-build", "no-output", "no-configuration"],
)
def test_ac_110_21_a_binary_the_source_set_doesnt_explain_is_refused(
    output: str, scripts: dict[str, str], message: str
) -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError, match=message):
        tool.check_configuration(output, scripts)


def test_ac_110_21_a_binary_that_wont_run_is_refused(tmp_path: Path) -> None:
    tool = _tool()
    with pytest.raises(tool.SourceSetError):
        tool._version_output(tmp_path / "missing.exe")


# Exit codes


class _Stub:
    """An assembly whose steps do what each test says."""

    pack_result: tuple[int, str] = (1, "digest")
    collect_error = pack_error = None
    packed = False

    def __init__(self, work: Path) -> None:
        self.work = work

    def recipe_scripts(self) -> dict[str, str]:
        return {"50-lib.sh": SCRIPT}

    def collect(self, jobs: int) -> None:
        if self.collect_error:
            raise _tool().SourceSetError(self.collect_error)

    def report(self) -> None:
        pass

    def pack(self, out: Path) -> tuple[int, str]:
        type(self).packed = True
        if self.pack_error:
            raise _tool().SourceSetError(self.pack_error)
        return self.pack_result


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> type[_Stub]:
    tool = _tool()

    class Stub(_Stub):
        pass

    monkeypatch.setattr(tool, "Assembly", Stub)
    monkeypatch.setattr(tool, "_version_output", lambda _exe: _version_output("--enable-gpl"))
    return Stub


def test_ac_110_21_an_archive_needs_the_binary_it_is_for(tmp_path: Path, stub) -> None:
    with pytest.raises(SystemExit) as raised:
        _tool().main(["--work", str(tmp_path)])
    assert raised.value.code == 2
    assert stub.packed is False


def test_ac_110_21_a_binary_mismatch_exits_before_any_work(
    tmp_path: Path, stub, monkeypatch: pytest.MonkeyPatch
) -> None:
    tool = _tool()
    monkeypatch.setattr(tool, "_version_output", lambda _exe: _version_output("--enable-libother"))
    assert tool.main(["--work", str(tmp_path), "--ffmpeg-exe", "ffmpeg.exe"]) == 5
    assert stub.packed is False


def test_ac_110_20_measure_only_writes_no_archive(tmp_path: Path, stub) -> None:
    assert _tool().main(["--work", str(tmp_path), "--measure-only"]) == 0
    assert stub.packed is False


def test_ac_110_20_an_incomplete_set_exits_before_packing(tmp_path: Path, stub) -> None:
    stub.collect_error = "a source is gone"
    assert _tool().main(["--work", str(tmp_path), "--ffmpeg-exe", "ffmpeg.exe"]) == 2
    assert stub.packed is False


def test_ac_110_20_a_failed_read_back_exits(tmp_path: Path, stub) -> None:
    stub.pack_error = "archive disagrees"
    assert _tool().main(["--work", str(tmp_path), "--ffmpeg-exe", "ffmpeg.exe"]) == 3


def test_ac_110_22_an_archive_over_githubs_limit_exits(tmp_path: Path, stub) -> None:
    tool = _tool()
    stub.pack_result = (tool.ASSET_LIMIT + 1, "digest")
    assert tool.main(["--work", str(tmp_path), "--ffmpeg-exe", "ffmpeg.exe"]) == 4


def test_ac_110_22_an_archive_at_the_limit_passes(tmp_path: Path, stub) -> None:
    tool = _tool()
    stub.pack_result = (tool.ASSET_LIMIT, "digest")
    assert tool.main(["--work", str(tmp_path), "--ffmpeg-exe", "ffmpeg.exe"]) == 0
