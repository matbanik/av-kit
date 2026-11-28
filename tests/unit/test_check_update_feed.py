"""``tools/check_update_feed.py`` (FEED_CHECK, MEU-173 AC-173.4) on fixture folders.

Each fixture is a build output folder under ``tmp_path``: ``latest.yml``, the one
``av-kit-Setup-<v>.exe``, its ``.blockmap`` and ``win-unpacked/resources/app-update.yml``. The tool
runs through ``subprocess``, so a missing script is an assertion on the exit code and the last line.
"""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL = REPO_ROOT / "tools" / "check_update_feed.py"
VERSION = "0.1.0"
INSTALLER = f"av-kit-Setup-{VERSION}.exe"


def _run(*args: str) -> tuple[int, str]:
    run = subprocess.run(
        [sys.executable, str(TOOL), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPO_ROOT,
    )
    lines = [line for line in run.stdout.splitlines() if line.strip()]
    return run.returncode, lines[-1] if lines else ""


def _feed(dist: Path) -> dict:
    return yaml.safe_load((dist / "latest.yml").read_text(encoding="utf-8"))


def _write_feed(dist: Path, feed: dict) -> None:
    (dist / "latest.yml").write_text(yaml.safe_dump(feed, sort_keys=False), encoding="utf-8")


def make_dist(root: Path) -> Path:
    dist = root / "dist"
    (dist / "win-unpacked" / "resources").mkdir(parents=True)
    body = b"MZ" + bytes(range(256)) * 8
    (dist / INSTALLER).write_bytes(body)
    (dist / f"{INSTALLER}.blockmap").write_bytes(b"\x1f\x8b blockmap")
    digest = base64.b64encode(hashlib.sha512(body).digest()).decode()
    _write_feed(
        dist,
        {
            "version": VERSION,
            "files": [{"url": INSTALLER, "sha512": digest, "size": len(body)}],
            "path": INSTALLER,
            "sha512": digest,
            "releaseDate": "2026-11-26T00:00:00.000Z",
        },
    )
    (dist / "win-unpacked" / "resources" / "app-update.yml").write_text(
        "owner: matbanik\nrepo: av-kit\nprovider: github\nupdaterCacheDirName: av-kit-ui-updater\n",
        encoding="utf-8",
    )
    return dist


def _no_feed(dist: Path) -> None:
    (dist / "latest.yml").unlink()


def _no_installer(dist: Path) -> None:
    (dist / INSTALLER).unlink()


def _two_installers(dist: Path) -> None:
    (dist / "av-kit-Setup-0.0.9.exe").write_bytes(b"MZ old")


def _other_version(dist: Path) -> None:
    feed = _feed(dist)
    feed["version"] = "0.0.9"
    _write_feed(dist, feed)


def _other_name(dist: Path) -> None:
    feed = _feed(dist)
    feed["path"] = "av-kit-Setup-0.0.9.exe"
    _write_feed(dist, feed)


def _name_with_a_space(dist: Path) -> None:
    feed = _feed(dist)
    feed["files"][0]["url"] = f"av-kit Setup {VERSION}.exe"
    _write_feed(dist, feed)


def _one_byte_changed(dist: Path) -> None:
    body = bytearray((dist / INSTALLER).read_bytes())
    body[10] ^= 0xFF
    (dist / INSTALLER).write_bytes(bytes(body))


def _other_size(dist: Path) -> None:
    feed = _feed(dist)
    feed["files"][0]["size"] += 1
    _write_feed(dist, feed)


def _empty_blockmap(dist: Path) -> None:
    (dist / f"{INSTALLER}.blockmap").write_bytes(b"")


def _other_owner(dist: Path) -> None:
    path = dist / "win-unpacked" / "resources" / "app-update.yml"
    path.write_text(
        path.read_text(encoding="utf-8").replace("matbanik", "someone"), encoding="utf-8"
    )


MISMATCHES: list[tuple[str, int, Callable[[Path], None]]] = [
    ("feed-missing", 10, _no_feed),
    ("installer-missing", 11, _no_installer),
    ("installer-ambiguous", 12, _two_installers),
    ("version-mismatch", 13, _other_version),
    ("name-mismatch", 14, _other_name),
    ("name-mismatch", 14, _name_with_a_space),
    ("sha512-mismatch", 15, _one_byte_changed),
    ("size-mismatch", 16, _other_size),
    ("blockmap-missing", 17, _empty_blockmap),
    ("app-config-mismatch", 18, _other_owner),
]


def test_ac_173_4_feed_ok_on_a_correct_folder(tmp_path: Path) -> None:
    dist = make_dist(tmp_path)
    out = tmp_path / "feed.json"
    code, last = _run("--dist", str(dist), "--version", VERSION, "--out", str(out))
    assert (code, last) == (0, "check-update-feed: feed-ok exit=0")
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["reason"] == "feed-ok"
    assert record["installer"] == INSTALLER

    code, last = _run("--dist", str(dist), "--version", "0.2.0")
    assert (code, last) == (13, "check-update-feed: version-mismatch exit=13")


@pytest.mark.parametrize(
    ("reason", "exit_code", "break_it"),
    MISMATCHES,
    ids=[f"{reason}-{fn.__name__.strip('_')}" for reason, _, fn in MISMATCHES],
)
def test_ac_173_4_each_mismatch_has_its_reason(
    tmp_path: Path, reason: str, exit_code: int, break_it: Callable[[Path], None]
) -> None:
    dist = make_dist(tmp_path)
    code, last = _run("--dist", str(dist), "--version", VERSION)
    assert (code, last) == (0, "check-update-feed: feed-ok exit=0")
    break_it(dist)
    code, last = _run("--dist", str(dist), "--version", VERSION)
    assert (code, last) == (exit_code, f"check-update-feed: {reason} exit={exit_code}")


def test_ac_173_4_selftest_passes(tmp_path: Path) -> None:
    code, last = _run("--selftest")
    assert code == 0, last
    assert last.startswith("check-update-feed selftest:")

    generic = make_dist(tmp_path)
    code, last = _run(
        "--dist",
        str(generic),
        "--version",
        VERSION,
        "--provider",
        "generic",
        "--feed-url",
        "https://x.invalid/",
    )
    assert (code, last) == (18, "check-update-feed: app-config-mismatch exit=18")
    code, last = _run("--dist", str(generic))
    assert code == 2
