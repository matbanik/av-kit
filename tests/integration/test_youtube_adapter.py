"""MEU-6 YouTube adapter integration tests. Mocked yt-dlp only."""

from __future__ import annotations

import inspect
import math
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from avkit_core.domain.download import (
    CookieTestResult,
    DownloadOptions,
    DownloadResult,
    FormatInfo,
    PlaylistInfo,
    SABRStatus,
    VideoInfo,
)
from avkit_core.domain.enums import AudioFormat, QualityPreset, SABRMode, SABRSource
from avkit_core.domain.errors import (
    AgeRestrictedError,
    CookieTestError,
    DomainError,
    DownloadCancelledError,
    ValidationError,
)
from avkit_core.ports.youtube import YouTubePort

REPO_ROOT = Path(__file__).resolve().parents[2]
INFRA_PYPROJECT = REPO_ROOT / "packages" / "infrastructure" / "pyproject.toml"
ADAPTER_PATH = (
    REPO_ROOT / "packages" / "infrastructure" / "src" / "avkit_infra" / "youtube" / "adapter.py"
)
YOUTUBE_PORT_METHODS = (
    "extract_info",
    "extract_video_ids",
    "download",
    "get_formats",
    "check_sabr_status",
    "test_cookies",
    "ytdlp_version",
)
QUALITY_HEIGHT = {
    QualityPreset.P2160: 2160,
    QualityPreset.P1440: 1440,
    QualityPreset.P1080: 1080,
    QualityPreset.P720: 720,
    QualityPreset.P480: 480,
    QualityPreset.P360: 360,
    QualityPreset.P240: 240,
    QualityPreset.P144: 144,
}
QUALITY_SELECTOR_BEST = "bestvideo+bestaudio/best"
QUALITY_SELECTOR_LOWEST = "worstvideo+worstaudio/worst"
AUDIO_FORMAT_SELECTORS = {
    AudioFormat.Default: "bestaudio/best[height<=480]/best",
    AudioFormat.Lowest: "worstaudio/bestaudio/best[height<=360]/best",
    AudioFormat.Best: "bestaudio/best[height<=720]/best",
    AudioFormat.LowWebm: "bestaudio[ext=webm]/bestaudio/best[height<=360]/best",
    AudioFormat.MediumWebm: "bestaudio[ext=webm]/bestaudio/best[height<=480]/best",
    AudioFormat.StandardWebm: "bestaudio[ext=webm]/bestaudio/best[height<=480]/best",
    AudioFormat.StandardM4a: "bestaudio[ext=m4a]/bestaudio/best[height<=480]/best",
    AudioFormat.StandardMp3: "bestaudio/best[height<=480]/best",
    AudioFormat.HighM4a: "bestaudio[ext=m4a]/bestaudio/best[height<=720]/best",
}
COOKIE_AUDIO_SELECTOR = (
    "bestaudio[protocol=m3u8_native]/bestaudio[protocol=m3u8]/bestaudio/worst"
)
COOKIE_EXTRACTOR_ARGS = {
    "youtube": {
        "player_client": ["tv", "web_safari", "web"],
    }
}
SABR_EXTRACTOR_ARGS = {
    "youtube": {
        "player_client": ["android", "tv", "ios"],
        "player_skip": ["webpage", "configs"],
        "skip": ["hls", "dash"],
        "include_hls_manifest": False,
        "include_dash_manifest": False,
    }
}
SABR_LOG_NEEDLES = (
    "require a gvs po token",
    "android client sabr formats require",
    "ios client sabr formats require",
)
SABR_PROBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
PROGRESS_MIN_INTERVAL_S = 0.25


def _dependency_name(spec: str) -> str:
    name = spec.strip()
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if separator in name:
            name = name.split(separator, 1)[0]
    return name.strip()


def _download_error(message: str) -> Exception:
    try:
        from yt_dlp.utils import DownloadError
    except ImportError:
        return RuntimeError(message)
    return DownloadError(message)


def _video_info_payload() -> dict[str, Any]:
    return {
        "id": "vid12345678",
        "title": "Example",
        "duration": 12.5,
        "formats": [
            {
                "format_id": "18",
                "ext": "mp4",
                "height": 360,
                "abr": 128.0,
                "vcodec": "avc1",
                "acodec": "mp4a",
            }
        ],
    }


def _options(tmp_path: Path, **overrides: object) -> DownloadOptions:
    cookie_file = overrides.pop("cookie_file", None)
    payload: dict[str, object] = {
        "quality": QualityPreset.P360,
        "audio_only": False,
        "audio_format": AudioFormat.Default,
        "output_dir": tmp_path,
        "mode": "none",
        "browser": None,
        "profile": None,
        "cookie_file": cookie_file,
    }
    payload.update(overrides)
    return DownloadOptions(**payload)  # type: ignore[arg-type]


def _patch_ydl(
    monkeypatch: pytest.MonkeyPatch,
    *,
    info: dict[str, Any] | None = None,
    error: BaseException | None = None,
    sabr_msg: str | None = None,
    hook_payloads: list[dict[str, Any]] | None = None,
    raise_on_init: BaseException | None = None,
    urls: list[str] | None = None,
) -> list[dict[str, Any]]:
    captured: list[dict[str, Any]] = []
    seen_urls = urls if urls is not None else []

    class FakeYDL:
        def __init__(self, opts: dict[str, Any]) -> None:
            captured.append(opts)
            self.opts = opts
            logger = opts.get("logger")
            if sabr_msg is not None and logger is not None:
                logger.warning(sabr_msg)
            if raise_on_init is not None:
                raise raise_on_init

        def __enter__(self) -> FakeYDL:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

        def extract_info(self, url: str, download: bool = False) -> dict[str, Any]:
            seen_urls.append(url)
            if error is not None:
                raise error
            payloads = hook_payloads
            if payloads is None and download:
                payloads = [
                    {
                        "status": "downloading",
                        "downloaded_bytes": 10,
                        "total_bytes": 100,
                        "speed": 1.0,
                    }
                ]
            if payloads:
                for hook in self.opts.get("progress_hooks") or []:
                    for payload in payloads:
                        hook(payload)
            return info if info is not None else _video_info_payload()

        def prepare_filename(self, extracted: dict[str, Any]) -> str:
            return str(extracted.get("_filename") or "prepared.mp4")

    monkeypatch.setattr("avkit_infra.youtube.adapter.YoutubeDL", FakeYDL)
    return captured


@pytest.mark.integration
def test_ac_6_1_youtube_module_and_ytdlp_dependency() -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    assert YouTubeAdapter is not None
    data = tomllib.loads(INFRA_PYPROJECT.read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]
    declared = {_dependency_name(str(item)) for item in dependencies}
    assert "yt-dlp" in declared


@pytest.mark.integration
def test_ac_6_2_youtube_port_signatures_match() -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    for name in YOUTUBE_PORT_METHODS:
        proto = inspect.signature(getattr(YouTubePort, name))
        impl = inspect.signature(getattr(YouTubeAdapter, name))
        proto_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in proto.parameters.items()
        ]
        impl_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in impl.parameters.items()
        ]
        assert impl_params == proto_params, name
        assert impl.return_annotation == proto.return_annotation


@pytest.mark.integration
def test_ac_6_3_extract_info_video_and_unique_preserve_playlist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _patch_ydl(monkeypatch, info=_video_info_payload())
    video = YouTubeAdapter().extract_info("https://www.youtube.com/watch?v=vid12345678")
    assert isinstance(video, VideoInfo)
    assert video.video_id == "vid12345678"
    assert video.title == "Example"
    assert video.duration == 12.5
    assert video.formats[0].format_id == "18"

    playlist_payload = {
        "_type": "playlist",
        "id": "PL123",
        "title": "Channel",
        "entries": [
            {"id": "aaa"},
            {"id": "bbb"},
            None,
            {"id": "aaa"},
            {"id": ""},
        ],
    }
    _patch_ydl(monkeypatch, info=playlist_payload)
    playlist = YouTubeAdapter().extract_info(
        "https://www.youtube.com/playlist?list=PL123", flat=True
    )
    assert isinstance(playlist, PlaylistInfo)
    assert playlist.playlist_id == "PL123"
    assert playlist.video_ids == ["aaa", "bbb"]
    with pytest.raises(ValidationError):
        PlaylistInfo(playlist_id="PL123", title="Channel", video_ids=["aaa", ""])


@pytest.mark.integration
def test_ac_6_4_extract_video_ids_playlistend_ctor(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    with pytest.raises(ValidationError):
        YouTubeAdapter(playlist_end=-1)

    captured = _patch_ydl(
        monkeypatch,
        info={"_type": "playlist", "id": "PL", "title": "T", "entries": [{"id": "a"}]},
    )
    ids = YouTubeAdapter(playlist_end=0).extract_video_ids("https://www.youtube.com/@chan")
    assert ids == ["a"]
    assert captured[0].get("extract_flat") is True
    assert "playlistend" not in captured[0]

    captured = _patch_ydl(
        monkeypatch,
        info={
            "_type": "playlist",
            "id": "PL",
            "title": "T",
            "entries": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        },
    )
    YouTubeAdapter(playlist_end=3).extract_video_ids("https://www.youtube.com/@chan")
    assert captured[0]["playlistend"] == 3


@pytest.mark.integration
def test_ac_6_5_get_formats_maps_and_rejects_incomplete_rows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _patch_ydl(monkeypatch, info=_video_info_payload())
    formats = YouTubeAdapter().get_formats("vid12345678")
    assert formats == [
        FormatInfo(
            format_id="18",
            ext="mp4",
            height=360,
            abr=128.0,
            vcodec="avc1",
            acodec="mp4a",
        )
    ]

    _patch_ydl(
        monkeypatch,
        info={"id": "vid12345678", "title": "Example", "formats": [{"ext": "mp4"}]},
    )
    with pytest.raises(ValidationError):
        YouTubeAdapter().get_formats("vid12345678")


@pytest.mark.integration
def test_ac_6_6_quality_selectors_exhaustive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    expected = {
        QualityPreset.Best: QUALITY_SELECTOR_BEST,
        QualityPreset.Lowest: QUALITY_SELECTOR_LOWEST,
    }
    for preset, height in QUALITY_HEIGHT.items():
        expected[preset] = f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"
    assert set(expected) == set(QualityPreset)

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {
        **_video_info_payload(),
        "requested_downloads": [{"filepath": str(outfile)}],
    }
    for preset, selector in expected.items():
        captured = _patch_ydl(monkeypatch, info=info)
        YouTubeAdapter().download(
            "https://youtu.be/vid12345678", _options(tmp_path, quality=preset)
        )
        assert captured[0]["format"] == selector


@pytest.mark.integration
def test_ac_6_7_audio_selectors_and_cookie_hls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    assert set(AUDIO_FORMAT_SELECTORS) == set(AudioFormat)
    outfile = tmp_path / "audio.m4a"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    for audio_format, selector in AUDIO_FORMAT_SELECTORS.items():
        captured = _patch_ydl(monkeypatch, info=info)
        YouTubeAdapter().download(
            "https://youtu.be/vid12345678",
            _options(tmp_path, audio_only=True, audio_format=audio_format),
        )
        assert captured[0]["format"] == selector

    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape", encoding="utf-8")
    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download(
        "https://youtu.be/vid12345678",
        _options(tmp_path, audio_only=True, mode="file", cookie_file=cookie),
    )
    assert captured[0]["format"] == COOKIE_AUDIO_SELECTOR
    assert captured[0]["format"] != AUDIO_FORMAT_SELECTORS[AudioFormat.Default]


@pytest.mark.integration
def test_ac_6_8_cookie_opts_and_unknown_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}

    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path, mode="none"))
    assert "cookiesfrombrowser" not in captured[0]
    assert "cookiefile" not in captured[0]
    dumped = repr(captured[0])
    assert "b'" not in dumped or "cookie" not in dumped.lower()

    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download(
        "https://youtu.be/vid12345678",
        _options(tmp_path, mode="browser", browser="chrome", profile="Default"),
    )
    assert captured[0]["cookiesfrombrowser"] == ("chrome", "Default")

    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape", encoding="utf-8")
    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download(
        "https://youtu.be/vid12345678",
        _options(tmp_path, mode="file", cookie_file=cookie),
    )
    assert captured[0]["cookiefile"] == str(cookie)
    assert not isinstance(captured[0]["cookiefile"], bytes)

    with pytest.raises(ValidationError):
        YouTubeAdapter().download(
            "https://youtu.be/vid12345678",
            _options(tmp_path, mode="ftp"),
        )


@pytest.mark.integration
def test_ac_6_9_cancel_raises_and_continue_returns_result(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    _patch_ydl(monkeypatch, info=info)
    adapter = YouTubeAdapter(should_stop=lambda: True)
    with pytest.raises(DownloadCancelledError) as cancelled:
        adapter.download("https://youtu.be/vid12345678", _options(tmp_path))
    assert not isinstance(cancelled.value, type(_download_error("x")))
    assert cancelled.value.__class__ is DownloadCancelledError

    _patch_ydl(monkeypatch, info=info)
    result = YouTubeAdapter(should_stop=lambda: False).download(
        "https://youtu.be/vid12345678",
        _options(tmp_path),
    )
    assert isinstance(result, DownloadResult)
    assert result.file_path == outfile


@pytest.mark.integration
def test_ac_6_10_age_gate_and_unmapped_download_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    age = _download_error("Sign in to confirm your age")
    _patch_ydl(monkeypatch, error=age)
    with pytest.raises(AgeRestrictedError) as age_err:
        YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path))
    assert age_err.value.__cause__ is age

    other = _download_error("boom")
    _patch_ydl(monkeypatch, error=other)
    with pytest.raises(DomainError) as domain_err:
        YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path))
    assert type(domain_err.value) is DomainError
    assert not isinstance(domain_err.value, AgeRestrictedError)
    assert domain_err.value.__cause__ is other
    assert not isinstance(domain_err.value, type(other))


@pytest.mark.integration
def test_ac_6_11_sabr_needles_set_flag_without_raising(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    for needle in SABR_LOG_NEEDLES:
        _patch_ydl(monkeypatch, info=info, sabr_msg=f"WARN: {needle} extra")
        result = YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path))
        assert result.sabr_detected is True
    _patch_ydl(monkeypatch, info=info, sabr_msg="plain progress")
    clean = YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path))
    assert clean.sabr_detected is False
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "SABRDetectedError" not in source
    assert "SqlAlchemyUnitOfWork" not in source


@pytest.mark.integration
def test_ac_6_12_no_download_archive(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path))
    opts = captured[0]
    assert "download_archive" not in opts
    assert "--download-archive" not in opts
    assert "--download-archive" not in repr(opts)


@pytest.mark.integration
def test_ac_6_13_test_cookies_never_raises_cookie_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    missing = YouTubeAdapter().test_cookies("file", None, None, tmp_path / "missing.txt")
    assert missing == CookieTestResult(ok=False, error_message=missing.error_message)
    assert missing.error_message
    assert "Netscape" not in (missing.error_message or "")

    _patch_ydl(monkeypatch, raise_on_init=OSError("browser locked"))
    locked = YouTubeAdapter().test_cookies("browser", "chrome", None, None)
    assert locked.ok is False
    assert locked.error_message

    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape HTTP Cookie File\nsecret=1\n", encoding="utf-8")
    _patch_ydl(monkeypatch, info=_video_info_payload())
    ok = YouTubeAdapter().test_cookies("file", None, None, cookie)
    assert ok == CookieTestResult(ok=True, error_message=None)
    none_mode = YouTubeAdapter().test_cookies("none", None, None, None)
    assert none_mode == CookieTestResult(ok=True, error_message=None)


@pytest.mark.integration
def test_ac_6_14_check_sabr_status_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    urls: list[str] = []
    _patch_ydl(
        monkeypatch,
        info=_video_info_payload(),
        sabr_msg="android client sabr formats require",
        urls=urls,
    )
    active = YouTubeAdapter().check_sabr_status()
    assert urls == [SABR_PROBE_URL]
    assert isinstance(active, SABRStatus)
    assert active.mode is SABRMode.Active
    assert active.source is SABRSource.Detected
    assert isinstance(active.checked_at, datetime)

    urls.clear()
    _patch_ydl(monkeypatch, info=_video_info_payload(), sabr_msg="ok", urls=urls)
    inactive = YouTubeAdapter().check_sabr_status()
    assert inactive.mode is SABRMode.Inactive
    assert inactive.source is SABRSource.Detected
    assert isinstance(inactive.checked_at, datetime)
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "SqlAlchemyUnitOfWork" not in source


@pytest.mark.integration
def test_ac_6_15_ytdlp_version_uses_library_not_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    import yt_dlp.version as ytdlp_version

    from avkit_infra.youtube.adapter import YouTubeAdapter, _read_ytdlp_version

    monkeypatch.setattr(ytdlp_version, "__version__", "2024.08.01")
    assert YouTubeAdapter().ytdlp_version() == "2024.08.01"
    assert _read_ytdlp_version() == "2024.08.01"
    monkeypatch.setattr(ytdlp_version, "__version__", "")
    assert YouTubeAdapter().ytdlp_version() is None
    assert _read_ytdlp_version() is None
    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in source
    assert "Popen" not in source
    assert "from yt_dlp.version import __version__" in source


@pytest.mark.integration
def test_ac_6_16_extractor_args_cookie_vs_sabr(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path, mode="none"))
    assert captured[0]["extractor_args"] == SABR_EXTRACTOR_ARGS
    assert "android" in captured[0]["extractor_args"]["youtube"]["player_client"]

    cookie = tmp_path / "cookies.txt"
    cookie.write_text("# Netscape", encoding="utf-8")
    captured = _patch_ydl(monkeypatch, info=info)
    YouTubeAdapter().download(
        "https://youtu.be/vid12345678",
        _options(tmp_path, mode="file", cookie_file=cookie),
    )
    assert captured[0]["extractor_args"] == COOKIE_EXTRACTOR_ARGS
    assert "android" not in captured[0]["extractor_args"]["youtube"]["player_client"]


@pytest.mark.integration
def test_ac_6_17_progress_skips_nan_and_throttles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    outfile = tmp_path / "clip.mp4"
    outfile.write_bytes(b"x")
    info = {**_video_info_payload(), "requested_downloads": [{"filepath": str(outfile)}]}
    ticks = [
        {"status": "downloading", "downloaded_bytes": 1, "total_bytes": 100, "speed": float("nan")},
        {
            "status": "downloading",
            "downloaded_bytes": float("nan"),
            "total_bytes": 100,
            "speed": 1.0,
        },
        {
            "status": "downloading",
            "downloaded_bytes": 1,
            "total_bytes": float("inf"),
            "speed": 1.0,
        },
        {"status": "downloading", "downloaded_bytes": 2, "total_bytes": 100, "speed": 1.0},
        {"status": "downloading", "downloaded_bytes": 3, "total_bytes": 100, "speed": 2.0},
        {"status": "downloading", "downloaded_bytes": 4, "total_bytes": 100, "speed": 3.0},
    ]
    times = iter([0.0, 0.0, 0.0, 0.0, 0.1, 0.1 + PROGRESS_MIN_INTERVAL_S])
    monkeypatch.setattr("avkit_infra.youtube.adapter.time.monotonic", lambda: next(times))
    seen: list[tuple[int, int | None, float | None]] = []

    def on_progress(downloaded: int, total: int | None, speed: float | None) -> None:
        seen.append((downloaded, total, speed))
        if speed is not None:
            assert math.isfinite(speed)

    _patch_ydl(monkeypatch, info=info, hook_payloads=ticks)
    YouTubeAdapter(on_progress=on_progress).download(
        "https://youtu.be/vid12345678",
        _options(tmp_path),
    )
    assert seen
    assert all(item[2] is None or math.isfinite(item[2]) for item in seen)
    assert all(math.isfinite(float(item[0])) for item in seen)
    assert all(item[1] is None or math.isfinite(float(item[1])) for item in seen)
    assert len(seen) == 2
    assert seen[0][0] == 2
    assert seen[1][0] == 4


@pytest.mark.integration
def test_ac_6_18_no_uow_and_missing_cookie_file_cause(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    source = ADAPTER_PATH.read_text(encoding="utf-8")
    assert "SqlAlchemyUnitOfWork" not in source
    assert "avkit_infra.database" not in source
    missing = tmp_path / "no-cookies.txt"
    with pytest.raises(CookieTestError) as err:
        YouTubeAdapter().download(
            "https://youtu.be/vid12345678",
            _options(tmp_path, mode="file", cookie_file=missing),
        )
    assert isinstance(err.value.__cause__, FileNotFoundError)

    cookie = tmp_path / "locked-cookies.txt"
    cookie.write_text("# Netscape", encoding="utf-8")
    _patch_ydl(monkeypatch, info=_video_info_payload(), error=PermissionError("denied"))
    with pytest.raises(CookieTestError) as unread:
        YouTubeAdapter().download(
            "https://youtu.be/vid12345678",
            _options(tmp_path, mode="file", cookie_file=cookie),
        )
    assert isinstance(unread.value.__cause__, OSError)


def _require_extract_error() -> type[DomainError]:
    import avkit_core.domain.errors as domain_errors

    assert hasattr(domain_errors, "ExtractError"), (
        "avkit_core.domain.errors.ExtractError is missing"
    )
    from avkit_core.domain.errors import ExtractError  # type: ignore[attr-defined]

    return ExtractError


@pytest.mark.integration
def test_ac_76_6_extract_failures_raise_extract_error(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    extract_error = _require_extract_error()
    url = "https://youtu.be/vid12345678"
    wall = _download_error("ERROR: [youtube] x: Sign in to confirm you're not a bot")
    _patch_ydl(monkeypatch, error=wall)
    with pytest.raises(extract_error) as walled:
        YouTubeAdapter().extract_info(url)
    assert str(walled.value) == str(wall)
    assert walled.value.__cause__ is wall

    _patch_ydl(monkeypatch, error=OSError("disk"))
    with pytest.raises(extract_error) as io_failed:
        YouTubeAdapter().extract_info(url)
    assert str(io_failed.value) == "yt-dlp IO failed"

    _patch_ydl(monkeypatch, info=["not", "a", "dict"])  # type: ignore[arg-type]
    with pytest.raises(extract_error) as no_info:
        YouTubeAdapter().extract_info(url)
    assert str(no_info.value) == "yt-dlp returned no info"


@pytest.mark.integration
def test_ac_76_6_age_gate_and_media_download_keep_their_types_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _patch_ydl(monkeypatch, error=_download_error("Sign in to confirm your age"))
    with pytest.raises(AgeRestrictedError):
        YouTubeAdapter().extract_info("https://youtu.be/vid12345678")

    _patch_ydl(monkeypatch, error=_download_error("boom"))
    with pytest.raises(DomainError) as failed:
        YouTubeAdapter().download("https://youtu.be/vid12345678", _options(tmp_path))
    assert type(failed.value) is DomainError


def _require_ffmpeg_location() -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    assert "ffmpeg_location" in inspect.signature(YouTubeAdapter).parameters, (
        "YouTubeAdapter(ffmpeg_location=...) is missing"
    )


@pytest.mark.integration
def test_ac_78_5_base_opts_ffmpeg_location_rereads_the_callable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _require_ffmpeg_location()
    current = {"path": tmp_path / "one" / "ffmpeg.exe"}
    reads: list[Path] = []

    def location() -> Path:
        reads.append(current["path"])
        return current["path"]

    adapter = YouTubeAdapter(ffmpeg_location=location)  # type: ignore[call-arg]
    captured = _patch_ydl(monkeypatch, info=_video_info_payload())
    adapter.extract_info("https://youtu.be/vid12345678")
    current["path"] = tmp_path / "two" / "ffmpeg.exe"
    adapter.extract_info("https://youtu.be/vid12345678")
    assert [opts.get("ffmpeg_location") for opts in captured] == [
        str(tmp_path / "one"),
        str(tmp_path / "two"),
    ]
    assert len(reads) == len(captured)


@pytest.mark.integration
def test_ac_78_5_no_location_leaves_the_key_absent_neg(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.youtube.adapter import YouTubeAdapter

    _require_ffmpeg_location()
    captured = _patch_ydl(monkeypatch, info=_video_info_payload())
    YouTubeAdapter(ffmpeg_location=lambda: None).extract_info(  # type: ignore[call-arg]
        "https://youtu.be/vid12345678"
    )
    YouTubeAdapter().extract_info("https://youtu.be/vid12345678")
    assert len(captured) == 2
    assert all("ffmpeg_location" not in opts for opts in captured)
