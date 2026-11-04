"""MEU-76 api-error-surface: CORS-safe 500s, one error event, ExtractError as 422.

Every request goes through `create_app` (CORSMiddleware -> request_id_middleware -> route);
no test calls a handler function directly. New symbols are imported inside the test bodies
after a presence assertion (`PY_SYMBOLS`).
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from structlog.testing import capture_logs
from tests.e2e.api_fakes import AUTH, TOKENS, VARIANT_ID, FakeHealth, FakeModels, make_bundle

import avkit_api.errors as api_errors
import avkit_core.domain.errors as domain_errors
from avkit_api.main import CORS_ORIGIN_REGEX, create_app
from avkit_core.domain.errors import (
    DomainError,
    FFmpegNotFoundError,
    ModelLoadError,
    ValidationError,
)
from avkit_core.services.download import DownloadService
from avkit_core.services.settings import SettingsService
from avkit_core.services.transcript import TranscriptService
from avkit_infra.database.engine import create_session_factory, create_sqlite_engine, init_schema
from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

ALLOWED_ORIGIN = "http://localhost:5173"
REJECTED_ORIGIN = "http://evil.example"
DEPS_ROUTE = "/api/v1/health/dependencies"
BOT_WALL = "ERROR: [youtube] x: Sign in to confirm you're not a bot"


class _RaisingHealth(FakeHealth):
    """The dependencies probe raises whatever the test hands it."""

    def __init__(self, error: BaseException) -> None:
        self.error = error

    def dependencies(self) -> object:
        raise self.error


def _client(error: BaseException) -> TestClient:
    base, _trx, _tts, _models = make_bundle()
    services = replace(base, health=_RaisingHealth(error))
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    # A 500 must come back as a response; the default re-raises it into the test.
    return TestClient(app, raise_server_exceptions=False)


def _error_events(logs: list[dict[str, object]]) -> list[dict[str, object]]:
    return [entry for entry in logs if entry.get("event") == "api.unhandled_error"]


def _require_extract_error() -> type[DomainError]:
    assert hasattr(domain_errors, "ExtractError"), (
        "avkit_core.domain.errors.ExtractError is missing"
    )
    from avkit_core.domain.errors import ExtractError  # type: ignore[attr-defined]

    return ExtractError


def test_ac_76_1_unhandled_error_is_cors_safe_masked_500() -> None:
    assert re.match(CORS_ORIGIN_REGEX, ALLOWED_ORIGIN)
    client = _client(RuntimeError("boom secret"))
    response = client.get(DEPS_ROUTE, headers={**AUTH, "Origin": ALLOWED_ORIGIN})
    assert response.status_code == 500
    assert response.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "Internal server error",
            "details": {"request_id": request_id},
        }
    }
    assert "boom secret" not in response.text
    assert "Traceback" not in response.text


def test_ac_76_1_rejected_origin_gets_no_cors_header_neg() -> None:
    assert re.match(CORS_ORIGIN_REGEX, REJECTED_ORIGIN) is None
    client = _client(RuntimeError("boom secret"))
    response = client.get(DEPS_ROUTE, headers={**AUTH, "Origin": REJECTED_ORIGIN})
    assert response.status_code == 500
    assert "access-control-allow-origin" not in response.headers
    assert "boom secret" not in response.text
    assert "Traceback" not in response.text


def test_ac_76_2_unhandled_error_emits_one_event() -> None:
    client = _client(RuntimeError("boom secret"))
    with capture_logs() as logs:
        response = client.get(DEPS_ROUTE, headers={**AUTH, "Origin": ALLOWED_ORIGIN})
    events = _error_events(logs)
    assert len(events) == 1, logs
    event = events[0]
    assert event["request_id"] == response.headers.get("X-Request-ID")
    assert event["route"] == DEPS_ROUTE
    assert event["method"] == "GET"
    assert event["error"] == "RuntimeError: boom secret"
    assert event["exc_info"]


def test_ac_76_2_not_found_and_request_validation_emit_no_event_neg() -> None:
    client = _client(RuntimeError("unused"))
    with capture_logs() as logs:
        missing = client.get("/api/v1/transcripts/no-such-job", headers=AUTH)
        invalid = client.post("/api/v1/downloads", headers=AUTH, json={})
    assert missing.status_code == 404
    assert invalid.status_code == 422
    assert _error_events(logs) == []


def test_ac_76_4_unmapped_domain_error_is_masked_and_logged() -> None:
    client = _client(DomainError("x"))
    with capture_logs() as logs:
        response = client.get(DEPS_ROUTE, headers=AUTH)
    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_error",
            "message": "Internal server error",
            "details": {"request_id": response.headers.get("X-Request-ID")},
        }
    }
    events = _error_events(logs)
    assert len(events) == 1, logs
    assert events[0]["error"] == "DomainError: x"


def test_ac_76_4_mapped_503_is_masked_and_not_logged_neg() -> None:
    client = _client(FFmpegNotFoundError("ffmpeg gone"))
    with capture_logs() as logs:
        response = client.get(DEPS_ROUTE, headers=AUTH)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "internal_error"
    assert "ffmpeg gone" not in response.text
    assert _error_events(logs) == []


def test_ac_76_5_extract_error_maps_to_422() -> None:
    extract_error = _require_extract_error()
    assert issubclass(extract_error, DomainError)
    assert api_errors.DOMAIN_HTTP_MAP.get(extract_error) == 422
    client = _client(extract_error("yt-dlp says no"))
    response = client.get(DEPS_ROUTE, headers=AUTH)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ExtractError"
    assert response.json()["error"]["message"] == "yt-dlp says no"


def test_ac_76_5_extract_error_is_not_a_validation_error_neg() -> None:
    extract_error = _require_extract_error()
    assert not issubclass(extract_error, ValidationError)


class _BotWallCoordinator:
    """The extract coordinator raises whatever the test sets, as `_run_extract` surfaces it."""

    def __init__(self) -> None:
        self.error: BaseException = AssertionError("the test did not set an error")

    def extract_info(self, url: str) -> object:
        del url
        raise self.error

    def extract_video_ids(self, url: str) -> list[str]:
        del url
        raise self.error


class _Unreached:
    """A port the add paths never reach before the extract fails."""

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"unexpected port call: {name}")


@pytest.fixture
def real_add_client(tmp_path: Path) -> Iterator[tuple[TestClient, _BotWallCoordinator]]:
    """Production DownloadService and TranscriptService over a temp SQLite file."""
    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def uow_factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(uow_factory)
    coordinator = _BotWallCoordinator()
    download = DownloadService(
        uow_factory, youtube=_Unreached(), coordinator=coordinator, settings=settings
    )
    transcript = TranscriptService(
        uow_factory,
        coordinator=coordinator,
        captions=_Unreached(),
        filesystem=_Unreached(),
        settings=settings,
    )
    base, _trx, _tts, _models = make_bundle()
    services = replace(base, download=download, transcript=transcript)
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    client = TestClient(app, raise_server_exceptions=False)
    try:
        yield client, coordinator
    finally:
        client.close()
        engine.dispose()


def test_ac_76_7_bot_wall_on_add_is_extract_error_422(
    real_add_client: tuple[TestClient, _BotWallCoordinator],
) -> None:
    extract_error = _require_extract_error()
    client, coordinator = real_add_client
    coordinator.error = extract_error(BOT_WALL)
    with capture_logs() as logs:
        download = client.post(
            "/api/v1/downloads",
            headers=AUTH,
            json={"url": "https://youtu.be/dQw4w9wgGc", "quality": "best"},
        )
        transcript = client.post(
            "/api/v1/transcripts",
            headers=AUTH,
            json={"channel_url": "https://www.youtube.com/@example"},
        )
    for response in (download, transcript):
        assert response.status_code == 422, response.text
        assert response.json()["error"]["code"] == "ExtractError"
        assert response.json()["error"]["message"] == BOT_WALL
        assert response.json()["error"]["code"] != "internal_error"
    assert _error_events(logs) == []


class _RaisingModels(FakeModels):
    """The model load raises whatever the test hands it (AC-75.9)."""

    def __init__(self, error: BaseException) -> None:
        super().__init__()
        self.error = error

    def load(self, variant_id: str, device: object) -> None:
        del variant_id, device
        raise self.error


def _load_client(error: BaseException) -> TestClient:
    base, _trx, _tts, _models = make_bundle(models=_RaisingModels(error))
    app = create_app(tokens=TOKENS, services=base, engine_dispose=None)
    return TestClient(app, raise_server_exceptions=False)


def _post_load(client: TestClient) -> object:
    return client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": VARIANT_ID, "device": "cuda"},
    )


def test_ac_75_9_model_load_error_maps_to_422() -> None:
    assert api_errors.DOMAIN_HTTP_MAP.get(ModelLoadError) == 422
    response = _post_load(_load_client(ModelLoadError("ONNX session failed")))
    assert response.status_code == 422, response.text
    assert response.json()["error"]["code"] == "ModelLoadError"
    assert response.json()["error"]["message"] == "ONNX session failed"


def test_ac_75_9_runtime_error_on_load_stays_masked_neg() -> None:
    client = _load_client(RuntimeError("cuda driver secret"))
    with capture_logs() as logs:
        response = _post_load(client)
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "cuda driver secret" not in response.text
    assert len(_error_events(logs)) == 1, logs
