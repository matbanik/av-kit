"""MEU-14 CONSOLE_LEVEL_FROM_METHOD processor tests (AC-14.9)."""

from __future__ import annotations

from pathlib import Path

from tests.tts_asset_fakes import FakeAssets, idle_runtime

from avkit_core.services.health import HealthService


class _Settings:
    def get(self, namespace: str, key: str) -> object:
        del namespace, key
        return False


class _Media:
    def ffmpeg_version(self) -> str | None:
        return None


class _YouTube:
    def ytdlp_version(self) -> str | None:
        return None


def _health(tmp_path: Path) -> HealthService:
    return HealthService(
        lambda: None,
        app_data=tmp_path,
        settings=_Settings(),
        media=_Media(),
        youtube=_YouTube(),
        assets=FakeAssets(),
        download_runtime=idle_runtime,
        ring_capacity=16,
    )


def test_ac_14_9_console_level_from_method(tmp_path: Path) -> None:
    health = _health(tmp_path)
    health._process(None, "warning", {"event": "warn-msg", "module": "health"})
    health._process(None, "debug", {"event": "dbg", "module": "health"})
    health._process(None, "error", {"event": "err", "module": "health"})
    health._process(None, "critical", {"event": "crit", "module": "health"})
    health._process(None, "info", {"event": "info-msg", "module": "health"})
    health._process(None, "not-a-level", {"event": "unknown", "module": "health"})
    health._process(None, "", {"event": "omitted", "module": "health"})
    events = health.console_snapshot(0)
    by_message = {event.message: event.level for event in events}
    assert by_message["warn-msg"] == "WARNING"
    assert by_message["dbg"] == "DEBUG"
    assert by_message["err"] == "ERROR"
    assert by_message["crit"] == "CRITICAL"
    assert by_message["info-msg"] == "INFO"
    assert by_message["unknown"] == "INFO"
    assert by_message["omitted"] == "INFO"
    assert all(
        level != "INFO" or message in {"info-msg", "unknown", "omitted"}
        for message, level in by_message.items()
        if message == "warn-msg" or True
    )
    assert by_message["warn-msg"] != "INFO"


def test_ac_76_3_console_shows_request_id_and_route(tmp_path: Path) -> None:
    health = _health(tmp_path)
    health._process(
        None,
        "error",
        {
            "event": "api.unhandled_error",
            "module": "api",
            "request_id": "rid-1",
            "route": "/api/v1/health/dependencies",
            "method": "GET",
            "error": "RuntimeError: boom",
        },
    )
    [event] = health.console_snapshot(0)
    assert event.message == (
        "api.unhandled_error error=RuntimeError: boom request_id=rid-1"
        " route=/api/v1/health/dependencies"
    )


def test_ac_76_3_record_without_the_keys_renders_as_today_neg(tmp_path: Path) -> None:
    health = _health(tmp_path)
    health._process(None, "info", {"event": "plain", "module": "health"})
    [event] = health.console_snapshot(0)
    assert event.message == "plain"
    assert "request_id=" not in event.message
    assert "route=" not in event.message
