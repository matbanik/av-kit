"""MEU-78 DEPS_FFMPEG: `/health/dependencies` reports the resolved ffmpeg and its ffprobe.

The stack is `build_services` over a tmp SQLite database behind `create_app`, so the setting,
the resolver and the route are all real. `shutil.which` and `subprocess.run` are patched on
the media adapter module; the binaries are empty temp files and never run.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import AppServices, build_services

TOKEN = "meu78-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    return path


def _fake_tools(monkeypatch: pytest.MonkeyPatch, table: dict[str, Path]) -> None:
    def fake_which(name: str) -> str | None:
        found = table.get(name)
        return str(found) if found is not None else None

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del kwargs
        return subprocess.CompletedProcess(command, 0, "ffmpeg version 7.1-test\n", "")

    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", fake_which)
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", fake_run)


@pytest.fixture
def stack(tmp_path: Path) -> Iterator[tuple[AppServices, TestClient]]:
    services, dispose = build_services(app_data=tmp_path / "data")
    try:
        app = create_app(tokens=frozenset({TOKEN}), services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield services, client
    finally:
        dispose()


def _ffmpeg_out(client: TestClient) -> dict[str, Any]:
    response = client.get("/api/v1/health/dependencies", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    ffmpeg = body["ffmpeg"]
    assert isinstance(ffmpeg, dict)
    assert "ffprobe_available" in ffmpeg, "ffmpeg.ffprobe_available is missing"
    return ffmpeg


def test_ac_78_7_dependencies_report_resolved_ffmpeg_and_ffprobe(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stack: tuple[AppServices, TestClient]
) -> None:
    services, client = stack
    chosen = _touch(tmp_path / "chosen" / "ffmpeg.exe")
    _touch(tmp_path / "chosen" / "ffprobe.exe")
    _fake_tools(monkeypatch, {})
    services.settings.set("downloader", "ffmpeg_path", str(chosen))
    with_probe = _ffmpeg_out(client)
    assert with_probe["path"] == str(chosen)
    assert with_probe["available"] is True
    assert with_probe["ffprobe_available"] is True

    lone = _touch(tmp_path / "lone" / "ffmpeg.exe")
    services.settings.set("downloader", "ffmpeg_path", str(lone))
    without_probe = _ffmpeg_out(client)
    assert without_probe["path"] == str(lone)
    assert without_probe["ffprobe_available"] is False


def test_ac_78_7_missing_setting_reports_the_path_binary_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stack: tuple[AppServices, TestClient]
) -> None:
    services, client = stack
    on_path = _touch(tmp_path / "path-bin" / "ffmpeg.exe")
    missing = tmp_path / "gone" / "ffmpeg.exe"
    _fake_tools(monkeypatch, {"ffmpeg": on_path})
    services.settings.set("downloader", "ffmpeg_path", str(missing))
    ffmpeg = _ffmpeg_out(client)
    assert ffmpeg["path"] == str(on_path)
    assert ffmpeg["path"] != str(missing)
