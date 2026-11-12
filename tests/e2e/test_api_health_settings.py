"""MEU-15 settings and remaining health tests (AC-15.10–15.13)."""

from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import AppServices
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.settings import SETTING_NAMESPACES
from avkit_core.domain.tts import AssetState

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}

DEFAULTS = {
    "downloader": {"quality": "1080p", "audio_only": False, "path": "~/Downloads/av-kit"},
    "ui": {"theme": "dark"},
    "app": {"log_level": "INFO", "log_to_file": False},
    "tts": {"input_text": "", "speed": 1.0},
    "transcript": {"output_dir": "~/Documents/Transcripts"},
}


class _Lifecycle:
    def recover_stale_processing(self) -> None:
        return None

    def stop_processing(self) -> None:
        return None

    def unload(self) -> None:
        return None

    def cancel_processing(self) -> None:
        return None

    def liveness(self) -> SimpleNamespace:
        return SimpleNamespace(ok=True)

    def dependencies(self) -> SimpleNamespace:
        return SimpleNamespace(
            ffmpeg_version="6.1",
            ytdlp_version="2024.12",
            tts_onnx_vocab=AssetState.READY,
            tts_spacy_model=AssetState.MISSING,
            tts_spacy_version=None,
            tts_voice_packs=AssetState.READY,
            tts_espeak=SimpleNamespace(available=False, version=None, path=None),
            # FIXTURE_REPAIRS (d) (Session 33, MEU-78): the DEPS_FFMPEG fields.
            ffmpeg_path=None,
            ffprobe_available=False,
            # FIXTURE_REPAIRS (Session 66, MEU-141): the RUNTIME_HEALTH field.
            js_runtime=SimpleNamespace(
                available=False, name=None, path=None, version=None, source=None, solver=False
            ),
        )


class FakeSettings:
    def __init__(self) -> None:
        self.data = {ns: dict(values) for ns, values in DEFAULTS.items()}
        self.commit_count = 0

    def get(self, namespace: str, key: str) -> object:
        return self.data.get(namespace, {}).get(key)

    def get_namespace(self, namespace: str) -> dict[str, object]:
        if namespace not in SETTING_NAMESPACES:
            raise ValidationError("unknown settings namespace")
        return dict(self.data.get(namespace, {}))

    def set_namespace(self, namespace: str, mapping: dict[str, object]) -> None:
        if namespace not in SETTING_NAMESPACES:
            raise ValidationError("unknown settings namespace")
        known = set(self.data.get(namespace, {}))
        extra = set(mapping) - known
        if extra:
            raise ValidationError("unknown settings key")
        if any("." in key for key in mapping):
            raise ValidationError("key must be a leaf name without '.'")
        self.data[namespace].update(mapping)
        self.commit_count += 1


class FakeHealth(_Lifecycle):
    def __init__(self) -> None:
        now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        self.events = [
            SimpleNamespace(
                seq=1,
                message="warn-msg",
                module="health",
                timestamp=now,
                level="WARNING",
            ),
            SimpleNamespace(
                seq=2,
                message="unknown-msg",
                module="health",
                timestamp=now,
                level="INFO",
            ),
        ]
        self.metrics: list[tuple[str, object]] = []

    def console_snapshot(self, after_seq: object) -> list[SimpleNamespace]:
        if isinstance(after_seq, bool) or not isinstance(after_seq, int) or after_seq < 0:
            raise ValidationError("after_seq must be an int >= 0")
        return [event for event in self.events if event.seq > after_seq]

    def record_startup_metric(self, name: str, value: object) -> None:
        self.metrics.append((name, value))


def _client() -> tuple[TestClient, FakeSettings, FakeHealth]:
    settings = FakeSettings()
    health = FakeHealth()
    life = _Lifecycle()
    services = AppServices(
        download=life,
        transcript=life,
        tts=life,
        models=life,
        settings=settings,
        health=health,
        conversion=life,
        capture=life,
    )
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    return TestClient(app), settings, health


def test_ac_15_10_settings_boundary() -> None:
    client, settings, _health = _client()
    unknown_ns = client.put("/api/v1/settings/not-a-ns", headers=AUTH, json={"theme": "dark"})
    rail = client.put(
        "/api/v1/settings/ui",
        headers=AUTH,
        json={"theme": "light", "rail.collapsed": True},
    )
    extra = client.put("/api/v1/settings/ui", headers=AUTH, json={"theme": "light", "nope": 1})
    unknown_key = client.put("/api/v1/settings/ui", headers=AUTH, json={"rail": True})
    assert unknown_ns.status_code == 404
    assert rail.status_code == 422
    assert extra.status_code == 422
    assert unknown_key.status_code == 422
    assert settings.commit_count == 0
    ok = client.put("/api/v1/settings/ui", headers=AUTH, json={"theme": "light"})
    assert ok.status_code == 200
    assert settings.commit_count == 1


def test_ac_15_11_get_namespace_defaults() -> None:
    client, _settings, _health = _client()
    response = client.get("/api/v1/settings/ui", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["theme"] == "dark"


def test_ac_15_12_health_deps_console_metrics() -> None:
    client, _settings, health = _client()
    deps = client.get("/api/v1/health/dependencies", headers=AUTH)
    console = client.get("/api/v1/health/console", headers=AUTH)
    after = client.get("/api/v1/health/console", headers=AUTH, params={"after_seq": 1})
    bad = client.get("/api/v1/health/console", headers=AUTH, params={"after_seq": -1})
    metric = client.post(
        "/api/v1/health/startup-metrics",
        headers=AUTH,
        json={"key": "startup.window_show_ms", "value_ms": 640},
    )
    assert deps.status_code == 200
    body = deps.json()
    assert body["yt_dlp"]["available"] is True
    assert body["ffmpeg"]["available"] is True
    assert "path" in body["ffmpeg"]
    assert console.status_code == 200
    assert "items" in console.json()
    assert after.json()["items"][0]["seq"] == 2
    assert bad.status_code == 422
    assert metric.status_code == 204
    assert health.metrics == [("startup.window_show_ms", 640)]


def test_ac_15_13_http_console_level() -> None:
    client, _settings, _health = _client()
    response = client.get("/api/v1/health/console", headers=AUTH)
    items = {item["message"]: item["level"] for item in response.json()["items"]}
    assert items["warn-msg"] == "WARNING"
    assert items["warn-msg"] != "INFO"
    assert items["unknown-msg"] == "INFO"
