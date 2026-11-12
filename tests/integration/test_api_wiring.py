"""G29 composition-root smoke: real tmp SQLite, no live YouTube/HF/Kokoro (AC-16.10)."""

from __future__ import annotations

import inspect
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services


def test_ac_16_10_build_services_health(tmp_path: Path) -> None:
    db_path = tmp_path / "avkit.db"
    services, dispose = build_services(app_data=tmp_path, database_path=db_path)
    try:
        app = create_app(
            tokens=frozenset({"g29-token"}),
            services=services,
            engine_dispose=dispose,
        )
        with TestClient(app) as client:
            response = client.get("/api/v1/health")
            listed = client.get(
                "/api/v1/conversions",
                headers={"Authorization": "Bearer g29-token"},
            )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert listed.status_code == 200
        assert "items" in listed.json()
        captures = client.get(
            "/api/v1/captures",
            headers={"Authorization": "Bearer g29-token"},
        )
        assert captures.status_code == 200
        assert "items" in captures.json()
        assert "processor" not in captures.json()
        assert db_path.is_file()
    finally:
        dispose()


def _fake_ffmpeg_tools(monkeypatch: pytest.MonkeyPatch, on_path: Path) -> None:
    """`shutil.which` finds only `on_path`; no real binary runs."""

    def fake_which(name: str) -> str | None:
        return str(on_path) if name == "ffmpeg" else None

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 0, "ffmpeg version 7.1-test\n", "")

    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", fake_which)
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", fake_run)


def _live_location(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    """Presence-assert the MEU-78 seams, then spy on `YouTubeAdapter.__init__` kwargs."""
    from avkit_core.domain.health import DependencyHealth
    from avkit_infra.youtube.adapter import YouTubeAdapter

    assert "ffmpeg_location" in inspect.signature(YouTubeAdapter).parameters, (
        "YouTubeAdapter(ffmpeg_location=...) is missing"
    )
    assert "ffmpeg_path" in inspect.signature(DependencyHealth).parameters, (
        "DependencyHealth.ffmpeg_path is missing"
    )
    captured: list[dict[str, object]] = []
    original = YouTubeAdapter.__init__

    def spy(self: YouTubeAdapter, *args: Any, **kwargs: Any) -> None:
        captured.append(dict(kwargs))
        original(self, *args, **kwargs)

    monkeypatch.setattr(YouTubeAdapter, "__init__", spy)
    return captured


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    return path


def test_ac_78_6_ffmpeg_setting_applies_without_rebuild(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _live_location(monkeypatch)
    on_path = _touch(tmp_path / "path-bin" / "ffmpeg.exe")
    chosen = _touch(tmp_path / "chosen" / "ffmpeg.exe")
    _fake_ffmpeg_tools(monkeypatch, on_path)
    services, dispose = build_services(app_data=tmp_path)
    try:
        assert len(captured) == 1
        location = captured[0].get("ffmpeg_location")
        assert callable(location)
        services.settings.set("downloader", "ffmpeg_path", str(chosen))
        assert services.health.dependencies().ffmpeg_path == str(chosen)
        assert location() == chosen
    finally:
        dispose()


def test_ac_78_6_cleared_setting_falls_back_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured = _live_location(monkeypatch)
    on_path = _touch(tmp_path / "path-bin" / "ffmpeg.exe")
    chosen = _touch(tmp_path / "chosen" / "ffmpeg.exe")
    _fake_ffmpeg_tools(monkeypatch, on_path)
    services, dispose = build_services(app_data=tmp_path)
    try:
        location = captured[0].get("ffmpeg_location")
        assert callable(location)
        resolve: Callable[[], object] = location
        services.settings.set("downloader", "ffmpeg_path", str(chosen))
        assert resolve() == chosen
        services.settings.set("downloader", "ffmpeg_path", "")
        assert services.health.dependencies().ffmpeg_path == str(on_path)
        assert resolve() == on_path
    finally:
        dispose()


def test_ac_139_4_debug_source_follows_a_settings_put(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """YTDLP_LIVE: the adapter's debug source reads the setting a `PUT /settings` wrote."""
    from avkit_core.services.health import HealthService

    monkeypatch.setattr(HealthService, "_active", None)
    captured = _live_location(monkeypatch)
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        assert len(captured) == 1
        source = captured[0].get("yt_dlp_debug")
        assert callable(source)
        app = create_app(
            tokens=frozenset({"s65-token"}),
            services=services,
            engine_dispose=dispose,
        )
        auth = {"Authorization": "Bearer s65-token"}
        path = "/api/v1/settings/downloader"
        with TestClient(app) as client:
            seen: list[object] = [source()]
            seen.append(client.put(path, headers=auth, json={"yt_dlp_debug": True}).status_code)
            seen.append(source())
            seen.append(client.put(path, headers=auth, json={"yt_dlp_debug": False}).status_code)
            seen.append(source())
        assert seen == [False, 200, True, 200, False]
    finally:
        dispose()
