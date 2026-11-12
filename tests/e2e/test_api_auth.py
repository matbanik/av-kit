"""MEU-14 auth, envelope, CORS, request-id, and factory tests (AC-14.1–14.8)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError as PydanticValidationError
from starlette.requests import Request

from avkit_api.dependencies import (
    get_download_service,
    get_health_service,
    get_model_service,
    get_settings_service,
    get_transcript_service,
    get_tts_service,
)
from avkit_api.main import create_app
from avkit_api.schemas.common import ApiModel
from avkit_api.wiring import AppServices
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.tts import AssetState

GUI_TOKEN = "gui-nonce-token"
MCP_TOKEN = "mcp-api-key"
TOKENS = frozenset({GUI_TOKEN, MCP_TOKEN})


class _Spy:
    def __init__(self) -> None:
        self.recover_calls = 0
        self.cancel_calls = 0
        self.stop_calls = 0
        self.unload_calls = 0
        self.dependencies_error: BaseException | None = None

    def recover_stale_processing(self) -> None:
        self.recover_calls += 1

    def cancel_processing(self) -> None:
        self.cancel_calls += 1

    def stop_processing(self) -> None:
        self.stop_calls += 1

    def unload(self) -> None:
        self.unload_calls += 1

    def liveness(self) -> SimpleNamespace:
        return SimpleNamespace(ok=True)

    def dependencies(self) -> SimpleNamespace:
        if self.dependencies_error is not None:
            raise self.dependencies_error
        # FIXTURE_REPAIRS (Session 27, MEU-62): the fake gains the new TTS asset fields.
        return SimpleNamespace(
            ffmpeg_version="6.0",
            ytdlp_version="2024.12",
            tts_onnx_vocab=AssetState.READY,
            tts_spacy_model=AssetState.READY,
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


class _IdleTTS:
    # FIXTURE_REPAIRS (e) / A-7 (Session 33, MEU-77): a TTS runtime that is always idle.
    def recover_stale_processing(self) -> None:
        pass

    def stop_processing(self, timeout: float = 10.0) -> bool:
        return True


def _services() -> tuple[AppServices, _Spy, list[int], Any]:
    spy = _Spy()
    dispose_calls: list[int] = []

    def engine_dispose() -> None:
        dispose_calls.append(1)

    conversion = _Spy()
    services = AppServices(
        download=spy,
        transcript=spy,
        tts=_IdleTTS(),
        models=spy,
        settings=spy,
        health=spy,
        conversion=conversion,
        capture=spy,
    )
    return services, spy, dispose_calls, engine_dispose


def _request_for(app: Any) -> Request:
    return Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "headers": [],
            "client": ("test", 50000),
            "server": ("test", 80),
            "app": app,
        }
    )


def _envelope_keys(body: dict[str, Any]) -> None:
    assert "detail" not in body
    error = body["error"]
    assert set(error) == {"code", "message", "details"}
    assert isinstance(error["code"], str) and error["code"]
    assert isinstance(error["message"], str) and error["message"]


def test_ac_14_1_factory_prefix_title_and_getters() -> None:
    services, _spy, _dispose, engine_dispose = _services()
    app = create_app(tokens=TOKENS, services=services, engine_dispose=engine_dispose)
    assert app.title == "av-kit"
    assert app.state.services is services
    request = _request_for(app)
    assert get_download_service(request) is services.download
    assert get_transcript_service(request) is services.transcript
    assert get_tts_service(request) is services.tts
    assert get_model_service(request) is services.models
    assert get_settings_service(request) is services.settings
    assert get_health_service(request) is services.health
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ac_14_2_auth_tokens_and_health_exempt() -> None:
    services, _spy, _dispose, engine_dispose = _services()
    app = create_app(tokens=TOKENS, services=services, engine_dispose=engine_dispose)
    with TestClient(app) as client:
        missing = client.get("/api/v1/health/dependencies")
        wrong = client.get(
            "/api/v1/health/dependencies",
            headers={"Authorization": "Bearer not-a-token"},
        )
        live = client.get("/api/v1/health")
        ok = client.get(
            "/api/v1/health/dependencies",
            headers={"Authorization": f"Bearer {GUI_TOKEN}"},
        )
        mcp = client.get(
            "/api/v1/health/dependencies",
            headers={"Authorization": f"Bearer {MCP_TOKEN}"},
        )
    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert missing.headers.get("www-authenticate") == "Bearer"
    _envelope_keys(missing.json())
    _envelope_keys(wrong.json())
    assert GUI_TOKEN not in missing.text
    assert MCP_TOKEN not in wrong.text
    assert "not-a-token" not in wrong.text
    assert live.status_code == 200
    assert live.json() == {"status": "ok"}
    assert ok.status_code == 200
    assert mcp.status_code == 200


def test_ac_14_3_error_envelope_on_401_422_500() -> None:
    services, spy, _dispose, engine_dispose = _services()
    app = create_app(tokens=TOKENS, services=services, engine_dispose=engine_dispose)
    with TestClient(app, raise_server_exceptions=False) as client:
        unauthorized = client.get("/api/v1/health/dependencies")
        spy.dependencies_error = ValidationError("bad deps")
        unprocessable = client.get(
            "/api/v1/health/dependencies",
            headers={"Authorization": f"Bearer {GUI_TOKEN}"},
        )
        spy.dependencies_error = RuntimeError("boom")
        internal = client.get(
            "/api/v1/health/dependencies",
            headers={"Authorization": f"Bearer {GUI_TOKEN}"},
        )
    assert unauthorized.status_code == 401
    _envelope_keys(unauthorized.json())
    assert unauthorized.status_code == 401
    assert unprocessable.status_code == 422
    _envelope_keys(unprocessable.json())
    assert internal.status_code == 500
    _envelope_keys(internal.json())
    details = internal.json()["error"]["details"]
    assert details is None or set(details) <= {"request_id"}


def test_ac_14_4_request_id_echo_or_uuid4() -> None:
    services, _spy, _dispose, engine_dispose = _services()
    app = create_app(tokens=TOKENS, services=services, engine_dispose=engine_dispose)
    supplied = "req-supplied-1"
    with TestClient(app) as client:
        echoed = client.get("/api/v1/health", headers={"X-Request-ID": supplied})
        minted = client.get("/api/v1/health")
    assert echoed.headers["x-request-id"] == supplied
    minted_id = minted.headers["x-request-id"]
    uuid.UUID(minted_id)


def test_ac_14_5_cors_localhost_not_wildcard() -> None:
    services, _spy, _dispose, engine_dispose = _services()
    app = create_app(tokens=TOKENS, services=services, engine_dispose=engine_dispose)
    with TestClient(app) as client:
        allowed = client.options(
            "/api/v1/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        denied = client.options(
            "/api/v1/health",
            headers={
                "Origin": "https://evil.example",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert denied.headers.get("access-control-allow-origin") != "*"
    assert denied.headers.get("access-control-allow-origin") != "https://evil.example"


def test_ac_14_6_factory_rejects_empty_or_blank_tokens() -> None:
    services, _spy, _dispose, engine_dispose = _services()
    with pytest.raises(ValueError):
        create_app(tokens=frozenset(), services=services, engine_dispose=engine_dispose)
    with pytest.raises(ValueError):
        create_app(tokens=frozenset({" "}), services=services, engine_dispose=engine_dispose)
    with pytest.raises(ValueError):
        create_app(
            tokens=frozenset({GUI_TOKEN, ""}),
            services=services,
            engine_dispose=engine_dispose,
        )


def test_ac_14_7_lifespan_startup_and_shutdown_spies() -> None:
    services, spy, dispose_calls, engine_dispose = _services()
    app = create_app(tokens=TOKENS, services=services, engine_dispose=engine_dispose)
    with TestClient(app) as client:
        assert spy.recover_calls == 1
        client.get("/api/v1/health")
    assert spy.cancel_calls == 1
    assert spy.stop_calls == 1
    assert spy.unload_calls == 1
    assert dispose_calls == [1]


def test_ac_14_8_api_model_forbids_extra() -> None:
    class Sample(ApiModel):
        name: str

    Sample(name="ok")
    with pytest.raises(PydanticValidationError):
        Sample(name="ok", extra_field=1)  # type: ignore[call-arg]
