"""MEU-16 OpenAPI census and STATIC_BEFORE_ID (AC-16.6, AC-16.8)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from tests.e2e.api_fakes import AUTH, make_client

from avkit_api import __version__
from avkit_api.routes.tts import router as tts_router

ROUTE_INDEX: tuple[tuple[str, str], ...] = (
    ("POST", "/api/v1/downloads"),
    ("GET", "/api/v1/downloads"),
    ("GET", "/api/v1/downloads/sabr"),
    ("POST", "/api/v1/downloads/sabr/check"),
    ("POST", "/api/v1/downloads/sabr/force"),
    ("POST", "/api/v1/downloads/sabr/clear"),
    ("POST", "/api/v1/downloads/cookies/test"),
    ("POST", "/api/v1/downloads/start"),
    ("POST", "/api/v1/downloads/pause"),
    ("POST", "/api/v1/downloads/resume"),
    ("POST", "/api/v1/downloads/cancel"),
    ("POST", "/api/v1/downloads/stop"),
    ("POST", "/api/v1/downloads/apply-defaults"),
    ("PUT", "/api/v1/downloads/reorder"),
    ("DELETE", "/api/v1/downloads"),
    ("GET", "/api/v1/downloads/{id}"),
    ("POST", "/api/v1/downloads/{id}/reset"),
    ("DELETE", "/api/v1/downloads/{id}"),
    ("POST", "/api/v1/conversions"),
    ("GET", "/api/v1/conversions"),
    ("GET", "/api/v1/conversions/gpu"),
    ("POST", "/api/v1/conversions/gpu/refresh"),
    ("POST", "/api/v1/conversions/start"),
    ("POST", "/api/v1/conversions/pause"),
    ("POST", "/api/v1/conversions/resume"),
    ("POST", "/api/v1/conversions/cancel"),
    ("PUT", "/api/v1/conversions/reorder"),
    ("DELETE", "/api/v1/conversions"),
    ("GET", "/api/v1/conversions/{id}"),
    ("POST", "/api/v1/conversions/{id}/reset"),
    ("DELETE", "/api/v1/conversions/{id}"),
    ("GET", "/api/v1/captures"),
    ("POST", "/api/v1/captures"),
    ("GET", "/api/v1/captures/requests"),
    ("POST", "/api/v1/captures/requests"),
    ("POST", "/api/v1/captures/requests/{id}/complete"),
    ("POST", "/api/v1/captures/requests/{id}/cancel"),
    ("GET", "/api/v1/captures/{id}"),
    ("GET", "/api/v1/captures/{id}/image"),
    ("POST", "/api/v1/captures/{id}/annotate"),
    ("POST", "/api/v1/captures/{id}/flatten"),  # TA-8 (Session 30, MEU-67)
    ("POST", "/api/v1/captures/{id}/revert"),  # TA-8 (Session 30, MEU-67)
    ("DELETE", "/api/v1/captures/{id}"),
    ("POST", "/api/v1/transcripts"),
    ("GET", "/api/v1/transcripts"),
    ("POST", "/api/v1/transcripts/start"),
    ("POST", "/api/v1/transcripts/pause"),
    ("POST", "/api/v1/transcripts/resume"),
    ("POST", "/api/v1/transcripts/stop"),
    ("PUT", "/api/v1/transcripts/reorder"),
    ("GET", "/api/v1/transcripts/{id}"),
    ("DELETE", "/api/v1/transcripts/{id}"),
    ("POST", "/api/v1/transcripts/{id}/compile"),
    ("POST", "/api/v1/transcripts/{id}/requeue"),
    ("POST", "/api/v1/transcripts/{id}/retry"),
    ("POST", "/api/v1/tts/prepare"),
    ("POST", "/api/v1/tts/generate"),
    ("GET", "/api/v1/tts/voices"),
    ("GET", "/api/v1/tts/{id}"),
    ("DELETE", "/api/v1/tts/{id}"),
    ("GET", "/api/v1/models/available"),
    ("GET", "/api/v1/models/downloaded"),
    ("POST", "/api/v1/models/download"),
    ("POST", "/api/v1/models/load"),
    ("POST", "/api/v1/models/unload"),
    ("GET", "/api/v1/models/status"),
    ("GET", "/api/v1/models/download-runtime"),
    ("GET", "/api/v1/settings/{namespace}"),
    ("PUT", "/api/v1/settings/{namespace}"),
    ("GET", "/api/v1/health"),
    ("GET", "/api/v1/health/dependencies"),
    ("GET", "/api/v1/health/console"),
    ("POST", "/api/v1/health/startup-metrics"),
)

ROUTE_PATHS = frozenset(path for _method, path in ROUTE_INDEX)
REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_export() -> object:
    spec = importlib.util.spec_from_file_location(
        "export_openapi",
        REPO_ROOT / "tools" / "export_openapi.py",
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load export_openapi.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ac_16_6_openapi_path_census() -> None:
    client, _trx, _tts, _models = make_client()
    schema = client.app.openapi()
    assert schema["info"]["title"] == "av-kit"
    assert schema["info"]["version"] == __version__
    paths = set(schema["paths"])
    assert paths == ROUTE_PATHS
    assert len(ROUTE_INDEX) == 73  # TA-8 (Session 30, MEU-67)


@pytest.mark.parametrize("method,path", ROUTE_INDEX)
def test_ac_16_6_each_route_index_row(method: str, path: str) -> None:
    client, _trx, _tts, _models = make_client()
    operations = client.app.openapi()["paths"][path]
    assert method.lower() in operations


def test_ac_16_8_export_check_and_static_before_id(tmp_path: Path) -> None:
    client, _trx, _tts, _models = make_client()
    voices = client.get("/api/v1/tts/voices", headers=AUTH)
    stolen = client.get("/api/v1/tts/voices", headers=AUTH)
    assert voices.status_code == 200
    assert stolen.json()["items"][0]["voice_id"] == "am_eric"
    tts_paths = [getattr(route, "path", "") for route in tts_router.routes]
    voices = next(path for path in tts_paths if path.endswith("/voices"))
    job_id = next(path for path in tts_paths if path.endswith("/{id}"))
    assert tts_paths.index(voices) < tts_paths.index(job_id), tts_paths
    export = _load_export()
    out = tmp_path / "openapi.json"
    export.write_openapi(out)
    export.check_openapi(out)
