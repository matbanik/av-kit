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
    ("POST", "/api/v1/conversions/probe"),
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
    ("POST", "/api/v1/captures/frames"),  # FRAMES_ROUTE (Session 62, MEU-134)
    ("POST", "/api/v1/captures/sheet"),  # SHEET_ROUTE (Session 63, MEU-135)
    ("GET", "/api/v1/captures/{id}"),
    ("GET", "/api/v1/captures/{id}/image"),
    ("POST", "/api/v1/captures/{id}/annotate"),
    ("POST", "/api/v1/captures/{id}/flatten"),  # TA-8 (Session 30, MEU-67)
    ("POST", "/api/v1/captures/{id}/revert"),  # TA-8 (Session 30, MEU-67)
    ("POST", "/api/v1/captures/{id}/crop"),  # CROP_REQUEST (Session 59, MEU-130)
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
    # TA-8 (Session 30, MEU-67); MEU-130 + crop; MEU-133 + probe
    # MEU-134 (Session 62) + POST /captures/frames
    # MEU-135 (Session 63) + POST /captures/sheet
    assert len(ROUTE_INDEX) == 77


@pytest.mark.parametrize("method,path", ROUTE_INDEX)
def test_ac_16_6_each_route_index_row(method: str, path: str) -> None:
    client, _trx, _tts, _models = make_client()
    paths = client.app.openapi()["paths"]
    assert path in paths
    assert method.lower() in paths[path]


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

def test_ac_133_9_probe_route_in_committed_openapi_and_before_id() -> None:
    import json

    committed = json.loads((REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8"))
    operation = committed.get("paths", {}).get("/api/v1/conversions/probe", {}).get("post")
    assert operation is not None, "POST /api/v1/conversions/probe is not in openapi.committed.json"
    schemas = committed.get("components", {}).get("schemas", {})
    assert {"ConversionProbeIn", "ConversionProbeOut"} <= set(schemas)
    request = operation.get("requestBody", {}).get("content", {}).get("application/json", {})
    assert request.get("schema") == {"$ref": "#/components/schemas/ConversionProbeIn"}
    replies = operation.get("responses", {})
    reply = replies.get("200", {}).get("content", {}).get("application/json", {})
    assert reply.get("schema") == {"$ref": "#/components/schemas/ConversionProbeOut"}
    probe_in = schemas["ConversionProbeIn"]
    assert set(probe_in.get("properties", {})) == {"path"}
    assert probe_in.get("required") == ["path"]
    assert probe_in.get("additionalProperties") is False
    assert probe_in["properties"]["path"].get("minLength") == 1
    assert set(schemas["ConversionProbeOut"].get("properties", {})) == {
        "path",
        "duration_ms",
        "timecode",
        "container",
        "video_codec",
        "audio_codec",
        "width",
        "height",
        "fps",
        "has_video",
        "has_audio",
    }
    export = _load_export()
    drift: str | None = None
    try:
        export.check_openapi(REPO_ROOT / "openapi.committed.json")
    except SystemExit as exc:
        drift = str(exc)
    assert drift is None
    source = (REPO_ROOT / "packages/api/src/avkit_api/routes/conversions.py").read_text(
        encoding="utf-8"
    )
    probe_at = source.find('"/probe"')
    id_at = source.find('"/{id}"')
    assert probe_at != -1, "routes/conversions.py declares no /probe route"
    assert id_at != -1
    assert probe_at < id_at


def test_ac_134_17_frames_route_in_committed_openapi_and_before_id() -> None:
    import json

    committed = json.loads((REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8"))
    operation = committed.get("paths", {}).get("/api/v1/captures/frames", {}).get("post")
    assert operation is not None, "POST /api/v1/captures/frames is not in openapi.committed.json"
    operations = sum(
        1
        for item in committed.get("paths", {}).values()
        for method in item
        if method in {"get", "post", "put", "delete", "patch"}
    )
    assert operations == 77  # MEU-135 (Session 63): + POST /captures/sheet
    schemas = committed.get("components", {}).get("schemas", {})
    assert {"CaptureFramesIn", "CaptureFramesOut"} <= set(schemas)
    request = operation.get("requestBody", {}).get("content", {}).get("application/json", {})
    assert request.get("schema") == {"$ref": "#/components/schemas/CaptureFramesIn"}
    replies = operation.get("responses", {})
    reply = replies.get("201", {}).get("content", {}).get("application/json", {})
    assert reply.get("schema") == {"$ref": "#/components/schemas/CaptureFramesOut"}
    frames_in = schemas["CaptureFramesIn"]
    assert set(frames_in.get("properties", {})) == {"path", "at", "count", "start", "end"}
    assert frames_in.get("required") == ["path"]
    assert frames_in.get("additionalProperties") is False
    assert frames_in["properties"]["path"].get("minLength") == 1
    assert frames_in["properties"]["path"].get("maxLength") == 4096
    assert set(schemas["CaptureFramesOut"].get("properties", {})) == {"video", "frames"}
    export = _load_export()
    drift: str | None = None
    try:
        export.check_openapi(REPO_ROOT / "openapi.committed.json")
    except SystemExit as exc:
        drift = str(exc)
    assert drift is None
    source = (REPO_ROOT / "packages/api/src/avkit_api/routes/captures.py").read_text(
        encoding="utf-8"
    )
    frames_at = source.find('"/frames"')
    id_at = source.find('"/{id}"')
    assert frames_at != -1, "routes/captures.py declares no /frames route"
    assert id_at != -1
    assert frames_at < id_at


@pytest.mark.parametrize("ac_id", ["AC-135.20"], ids=["AC-135.20"])
def test_ac_135_20_openapi_has_sheet(ac_id: str) -> None:
    import json

    committed = json.loads((REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8"))
    operation = committed.get("paths", {}).get("/api/v1/captures/sheet", {}).get("post")
    assert operation is not None, "POST /api/v1/captures/sheet is not in openapi.committed.json"
    operations = sum(
        1
        for item in committed.get("paths", {}).values()
        for method in item
        if method in {"get", "post", "put", "delete", "patch"}
    )
    assert operations == 77
    schemas = committed.get("components", {}).get("schemas", {})
    assert {"CaptureSheetIn", "CaptureSheetOut"} <= set(schemas)
    request = operation.get("requestBody", {}).get("content", {}).get("application/json", {})
    assert request.get("schema") == {"$ref": "#/components/schemas/CaptureSheetIn"}
    replies = operation.get("responses", {})
    assert set(replies) >= {"201"}
    reply = replies.get("201", {}).get("content", {}).get("application/json", {})
    assert reply.get("schema") == {"$ref": "#/components/schemas/CaptureSheetOut"}
    sheet_in = schemas["CaptureSheetIn"]
    properties = sheet_in.get("properties", {})
    assert set(properties) == {"path", "start", "end", "grid", "max_edge"}
    assert sheet_in.get("required") == ["path"]
    assert sheet_in.get("additionalProperties") is False
    assert properties["path"].get("minLength") == 1
    assert properties["path"].get("maxLength") == 4096
    assert (properties["grid"].get("minimum"), properties["grid"].get("maximum")) == (2, 5)
    assert properties["grid"].get("default") == 3
    assert (properties["max_edge"].get("minimum"), properties["max_edge"].get("maximum")) == (
        64,
        2576,
    )
    assert properties["max_edge"].get("default") == 1568
    sheet_out = schemas["CaptureSheetOut"].get("properties", {})
    assert set(sheet_out) == {"video", "shot", "spacing_ms", "cells"}
    export = _load_export()
    drift: str | None = None
    try:
        export.check_openapi(REPO_ROOT / "openapi.committed.json")
    except SystemExit as exc:
        drift = str(exc)
    assert drift is None
    source = (REPO_ROOT / "packages/api/src/avkit_api/routes/captures.py").read_text(
        encoding="utf-8"
    )
    frames_at = source.find('"/frames"')
    sheet_at = source.find('"/sheet"')
    id_at = source.find('"/{id}"')
    assert sheet_at != -1, "routes/captures.py declares no /sheet route"
    assert frames_at != -1
    assert id_at != -1
    assert frames_at < sheet_at < id_at
