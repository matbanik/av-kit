"""Check a build output folder's update feed files before they are uploaded (FEED_CHECK, MEU-173).

Usage: ``check_update_feed.py --dist <dir> --version <v> [--provider github|generic]
[--feed-url <url>] [--out <json>]`` or ``--selftest``.

It reads ``<dir>/latest.yml``, the one ``av-kit-Setup-<v>.exe`` in ``<dir>``, its ``.blockmap`` and
``<dir>/win-unpacked/resources/app-update.yml``, and compares them: the feed's ``version`` with
``<v>``; ``path`` and ``files[0].url`` with the installer's file name (no space, no path part);
``sha512`` and ``files[0].sha512`` with the base64 SHA-512 of the installer's bytes;
``files[0].size`` with its byte length; the blockmap present and not empty; and ``app-update.yml``
naming provider ``github``, owner ``matbanik`` and repo ``av-kit`` (or, with ``--provider
generic``, the given ``--feed-url``).

The last stdout line is ``check-update-feed: <reason> exit=<n>``. It reads files only: no
network, no upload, and no write outside ``--out``. The upload itself is Mat's step, in
``docs/releases/publish-checklist-update-feed.md``.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import yaml

REASONS = {
    "feed-ok": 0,
    "usage": 2,
    "feed-missing": 10,
    "installer-missing": 11,
    "installer-ambiguous": 12,
    "version-mismatch": 13,
    "name-mismatch": 14,
    "sha512-mismatch": 15,
    "size-mismatch": 16,
    "blockmap-missing": 17,
    "app-config-mismatch": 18,
}
GITHUB_FEED = {"provider": "github", "owner": "matbanik", "repo": "av-kit"}
INSTALLER_GLOB = "av-kit-Setup-*.exe"


class Mismatch(Exception):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(detail)
        self.reason = reason


def _load_yaml(path: Path, reason: str) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise Mismatch(reason, f"{path.name} unreadable: {exc}") from exc
    if not isinstance(data, dict):
        raise Mismatch(reason, f"{path.name} is not a mapping")
    return data


def _plain_name(name: object, installer: str) -> bool:
    return isinstance(name, str) and name == installer and " " not in name and "/" not in name


def check(dist: Path, version: str, provider: str = "github", feed_url: str | None = None) -> dict:
    """Return the record of a correct folder, or raise ``Mismatch`` with the first reason."""
    feed_path = dist / "latest.yml"
    if not feed_path.is_file():
        raise Mismatch("feed-missing", f"{feed_path} is missing")
    feed = _load_yaml(feed_path, "feed-missing")

    installers = sorted(p for p in dist.glob(INSTALLER_GLOB) if p.is_file())
    if not installers:
        raise Mismatch("installer-missing", f"no {INSTALLER_GLOB} in {dist}")
    if len(installers) > 1:
        raise Mismatch("installer-ambiguous", ", ".join(p.name for p in installers))
    installer = installers[0]
    expected = f"av-kit-Setup-{version}.exe"
    if str(feed.get("version")) != version:
        raise Mismatch(
            "version-mismatch", f"latest.yml version {feed.get('version')!r}, not {version!r}"
        )

    files = feed.get("files")
    first = files[0] if isinstance(files, list) and files and isinstance(files[0], dict) else {}
    for where, name in (("path", feed.get("path")), ("files[0].url", first.get("url"))):
        if not _plain_name(name, installer.name) or installer.name != expected:
            raise Mismatch(
                "name-mismatch", f"latest.yml {where} {name!r}, installer {installer.name!r}"
            )

    body = installer.read_bytes()
    digest = base64.b64encode(hashlib.sha512(body).digest()).decode("ascii")
    for where, value in (("sha512", feed.get("sha512")), ("files[0].sha512", first.get("sha512"))):
        if value != digest:
            raise Mismatch(
                "sha512-mismatch", f"latest.yml {where} does not match the installer's bytes"
            )
    if first.get("size") != len(body):
        raise Mismatch(
            "size-mismatch",
            f"latest.yml files[0].size {first.get('size')!r}, installer {len(body)}",
        )

    blockmap = dist / f"{installer.name}.blockmap"
    if not blockmap.is_file() or blockmap.stat().st_size == 0:
        raise Mismatch("blockmap-missing", f"{blockmap.name} is missing or empty")

    app_path = dist / "win-unpacked" / "resources" / "app-update.yml"
    if not app_path.is_file():
        raise Mismatch("app-config-mismatch", f"{app_path} is missing")
    app = _load_yaml(app_path, "app-config-mismatch")
    if provider == "github":
        wrong = {k: app.get(k) for k, v in GITHUB_FEED.items() if app.get(k) != v}
    else:
        wrong = {
            k: app.get(k)
            for k, v in {"provider": "generic", "url": feed_url}.items()
            if app.get(k) != v
        }
    if wrong:
        raise Mismatch("app-config-mismatch", f"app-update.yml {wrong}")

    return {
        "reason": "feed-ok",
        "version": version,
        "installer": installer.name,
        "size": len(body),
        "sha512": digest,
        "blockmap_bytes": blockmap.stat().st_size,
        "app_update": app,
    }


def _finish(reason: str, detail: str = "") -> int:
    if detail:
        print(f"check-update-feed: {detail}")
    code = REASONS[reason]
    print(f"check-update-feed: {reason} exit={code}")
    return code


def run(args: argparse.Namespace) -> int:
    if args.provider == "generic" and not args.feed_url:
        return _finish("usage", "--provider generic needs --feed-url")
    try:
        record = check(Path(args.dist), args.version, args.provider, args.feed_url)
    except Mismatch as exc:
        record = {"reason": exc.reason, "detail": str(exc)}
        code = _finish(exc.reason, str(exc))
    else:
        print(
            f"check-update-feed: {record['installer']} {record['size']} bytes, feed {args.provider}"
        )
        code = _finish("feed-ok")
    if args.out:
        record["exit"] = code
        Path(args.out).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return code


def _fixture(root: Path, version: str = "1.2.3") -> Path:
    dist = root / "dist"
    (dist / "win-unpacked" / "resources").mkdir(parents=True)
    name = f"av-kit-Setup-{version}.exe"
    body = b"MZ" + bytes(range(256)) * 4
    (dist / name).write_bytes(body)
    (dist / f"{name}.blockmap").write_bytes(b"blockmap")
    digest = base64.b64encode(hashlib.sha512(body).digest()).decode("ascii")
    feed = {
        "version": version,
        "files": [{"url": name, "sha512": digest, "size": len(body)}],
        "path": name,
        "sha512": digest,
    }
    (dist / "latest.yml").write_text(yaml.safe_dump(feed, sort_keys=False), encoding="utf-8")
    (dist / "win-unpacked" / "resources" / "app-update.yml").write_text(
        "owner: matbanik\nrepo: av-kit\nprovider: github\n", encoding="utf-8"
    )
    return dist


def selftest() -> int:
    def edit_feed(dist: Path, fn) -> None:
        feed = yaml.safe_load((dist / "latest.yml").read_text(encoding="utf-8"))
        fn(feed)
        (dist / "latest.yml").write_text(yaml.safe_dump(feed, sort_keys=False), encoding="utf-8")

    def flip(dist: Path) -> None:
        exe = dist / "av-kit-Setup-1.2.3.exe"
        body = bytearray(exe.read_bytes())
        body[5] ^= 1
        exe.write_bytes(bytes(body))

    cases = [
        ("feed-ok", lambda d: None),
        ("feed-missing", lambda d: (d / "latest.yml").unlink()),
        ("installer-missing", lambda d: (d / "av-kit-Setup-1.2.3.exe").unlink()),
        ("installer-ambiguous", lambda d: (d / "av-kit-Setup-1.2.2.exe").write_bytes(b"MZ")),
        ("version-mismatch", lambda d: edit_feed(d, lambda f: f.update(version="1.2.2"))),
        (
            "name-mismatch",
            lambda d: edit_feed(d, lambda f: f.update(path="av-kit Setup 1.2.3.exe")),
        ),
        ("sha512-mismatch", flip),
        ("size-mismatch", lambda d: edit_feed(d, lambda f: f["files"][0].update(size=1))),
        ("blockmap-missing", lambda d: (d / "av-kit-Setup-1.2.3.exe.blockmap").unlink()),
        (
            "app-config-mismatch",
            lambda d: (d / "win-unpacked" / "resources" / "app-update.yml").write_text(
                "provider: s3\n", encoding="utf-8"
            ),
        ),
    ]
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for n, (want, breaker) in enumerate(cases):
            dist = _fixture(Path(tmp) / f"c{n}")
            breaker(dist)
            try:
                got = check(dist, "1.2.3")["reason"]
            except Mismatch as exc:
                got = exc.reason
            ok = got == want
            bad += 0 if ok else 1
            print(f"selftest {'ok ' if ok else 'BAD'} {want}: got {got}")
    print(f"check-update-feed selftest: {len(cases) - bad}/{len(cases)} ok")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], exit_on_error=False)
    parser.add_argument("--dist", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--provider", choices=("github", "generic"), default="github")
    parser.add_argument("--feed-url")
    parser.add_argument("--out")
    try:
        args = parser.parse_args(argv)
    except (argparse.ArgumentError, SystemExit) as exc:
        return _finish("usage", f"usage: {exc}")
    return run(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
