"""MEU-168 YTDLP_LOCK and VARIANT_FALLBACK: the yt-dlp release the lock holds, and the
extractor arguments the adapter gives yt-dlp.

The lock test reads `uv.lock` and `packages/infrastructure/pyproject.toml` through one helper,
so the guard can feed the same helper an old lock text. The adapter test patches `YoutubeDL`
with the recording fake of the MEU-6 integration tests. Nothing reaches the network.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import pytest
from tests.integration.test_youtube_adapter import _options, _patch_ydl, _video_info_payload

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK = REPO_ROOT / "uv.lock"
INFRA_PYPROJECT = REPO_ROOT / "packages" / "infrastructure" / "pyproject.toml"
FIXED_RELEASE = (2026, 11, 23)
EJS_VERSION = "0.8.0"
FLOOR = "yt-dlp>=2026.11.23"
EJS_PIN = "yt-dlp-ejs==0.8.0"
URL = "https://youtu.be/vid12345678"


def _release(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


def _dependency_name(spec: str) -> str:
    name = spec.strip()
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<", "["):
        if separator in name:
            name = name.split(separator, 1)[0]
    return name.strip()


def _lock_problems(lock_text: str, pyproject_text: str) -> list[str]:
    """What keeps the lock and the infrastructure pyproject from `YTDLP_LOCK`; empty when held."""
    problems: list[str] = []
    packages = {
        str(p["name"]): str(p.get("version", "")) for p in tomllib.loads(lock_text)["package"]
    }
    ytdlp = packages.get("yt-dlp")
    if ytdlp is None:
        problems.append("the lock holds no yt-dlp")
    elif _release(ytdlp) < FIXED_RELEASE:
        problems.append(f"the lock holds yt-dlp {ytdlp}, before 2026.11.23")
    ejs = packages.get("yt-dlp-ejs")
    if ejs != EJS_VERSION:
        problems.append(f"the lock holds yt-dlp-ejs {ejs}, not {EJS_VERSION}")
    deps = [str(d).strip() for d in tomllib.loads(pyproject_text)["project"]["dependencies"]]
    ytdlp_specs = [d for d in deps if _dependency_name(d) == "yt-dlp"]
    if ytdlp_specs != [FLOOR]:
        problems.append(f"the infrastructure pyproject requires {ytdlp_specs}, not [{FLOOR!r}]")
    ejs_specs = [d for d in deps if _dependency_name(d) == "yt-dlp-ejs"]
    if ejs_specs != [EJS_PIN]:
        problems.append(f"the infrastructure pyproject requires {ejs_specs}, not [{EJS_PIN!r}]")
    return problems


def _read(path: Path) -> str:
    return path.read_bytes().decode("utf-8")


def test_ac_168_1_lock_holds_the_fixed_release() -> None:
    assert _lock_problems(_read(LOCK), _read(INFRA_PYPROJECT)) == []


def test_ac_168_1_helper_refuses_an_old_lock() -> None:
    old_lock = (
        'version = 1\n\n[[package]]\nname = "yt-dlp"\nversion = "2026.10.26"\n\n'
        '[[package]]\nname = "yt-dlp-ejs"\nversion = "0.8.0"\n'
    )
    no_floor = '[project]\nname = "avkit-infra"\ndependencies = ["yt-dlp", "yt-dlp-ejs==0.8.0"]\n'
    problems = _lock_problems(old_lock, no_floor)
    assert "the lock holds yt-dlp 2026.10.26, before 2026.11.23" in problems
    assert f"the infrastructure pyproject requires ['yt-dlp'], not [{FLOOR!r}]" in problems
    new_lock = old_lock.replace("2026.10.26", "2026.11.23")
    floor = no_floor.replace('"yt-dlp",', f'"{FLOOR}",')
    assert _lock_problems(new_lock, floor) == []


def _options_seen(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> dict[str, list[dict]]:
    """Every options dict the adapter gives yt-dlp, by the call that built it."""
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
    seen: dict[str, list[dict[str, Any]]] = {}

    captured = _patch_ydl(monkeypatch, info=info)
    for mode in ("none", "file", "browser"):
        extra: dict[str, object] = {"mode": mode}
        if mode == "file":
            extra["cookie_file"] = cookie
        if mode == "browser":
            extra["browser"] = "chrome"
        YouTubeAdapter().download(URL, _options(tmp_path, **extra))
    seen["download"] = list(captured)

    captured = _patch_ydl(monkeypatch, info=_video_info_payload())
    adapter = YouTubeAdapter()
    adapter.extract_info(URL)
    adapter.extract_info(URL, options=_options(tmp_path, mode="file", cookie_file=cookie))
    seen["metadata"] = list(captured)

    captured = _patch_ydl(monkeypatch, info=_video_info_payload())
    YouTubeAdapter().test_cookies("file", None, None, cookie)
    YouTubeAdapter().test_cookies("browser", "chrome", None, None)
    seen["cookie_test"] = list(captured)

    captured = _patch_ydl(monkeypatch, info=_video_info_payload())
    YouTubeAdapter().check_sabr_status()
    seen["sabr"] = list(captured)
    return seen


def _youtube_args(opts: dict[str, Any]) -> dict[str, Any]:
    args = opts.get("extractor_args") or {}
    return dict(args.get("youtube") or {})


def test_ac_168_6_adapter_sets_no_player_js_variant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube import adapter as adapter_module

    seen = _options_seen(monkeypatch, tmp_path)
    assert all(seen[call] for call in ("download", "metadata", "cookie_test", "sabr"))
    with_variant = [
        call
        for call, runs in seen.items()
        for opts in runs
        if "player_js_variant" in _youtube_args(opts)
    ]
    assert with_variant == []
    for name in ("COOKIE_EXTRACTOR_ARGS", "SABR_EXTRACTOR_ARGS"):
        assert "player_js_variant" not in getattr(adapter_module, name)["youtube"]
