"""MEU-16 extra-field oracle for every POST/PUT in ROUTE_INDEX (AC-16.9)."""

from __future__ import annotations

import pytest
from tests.e2e.api_fakes import AUTH, JOB_A, VARIANT_ID, make_client
from tests.e2e.test_api_openapi import ROUTE_INDEX

BODY_ROUTES = tuple((method, path) for method, path in ROUTE_INDEX if method in {"POST", "PUT"})
SAMPLE_ID = JOB_A


def _valid_body(path: str) -> dict[str, object]:
    if path == "/api/v1/downloads":
        return {"url": "https://youtu.be/aaaaaaaaaaa", "quality": "1080p"}
    if path == "/api/v1/downloads/cookies/test":
        return {"mode": "none"}
    if path == "/api/v1/downloads/reorder":
        return {"job_ids": [SAMPLE_ID]}
    if path == "/api/v1/conversions":
        return {"paths": ["C:/tmp/clip.mp4"], "kind": "compress"}
    if path == "/api/v1/conversions/reorder":
        return {"job_ids": [SAMPLE_ID]}
    if path == "/api/v1/transcripts":
        return {"channel_url": "https://www.youtube.com/@demo"}
    if path == "/api/v1/transcripts/reorder":
        return {"job_ids": [SAMPLE_ID]}
    if path == "/api/v1/tts/prepare":
        return {"text": "Hello", "enabled_steps": ["whitespace"]}
    if path == "/api/v1/tts/generate":
        return {
            "text": "Hello",
            "voice": "am_eric",
            "speed": 1.0,
            "format": "MP3",
            "enabled_steps": [],
        }
    if path == "/api/v1/models/download":
        return {"variant_id": VARIANT_ID}
    if path == "/api/v1/models/load":
        return {"variant_id": VARIANT_ID, "device": "cpu"}
    if path == "/api/v1/settings/{namespace}":
        return {"theme": "dark"}
    if path == "/api/v1/health/startup-metrics":
        return {"key": "boot", "value_ms": 12}
    if path == "/api/v1/captures/{id}/crop":
        return {"x": 0, "y": 0, "width": 8, "height": 8}
    return {}


def _url(path: str) -> str:
    return path.replace("{id}", SAMPLE_ID).replace("{namespace}", "ui")


@pytest.mark.parametrize("method,path", BODY_ROUTES)
def test_ac_16_9_extra_field_is_422(method: str, path: str) -> None:
    client, _trx, _tts, _models = make_client()
    payload = dict(_valid_body(path))
    payload["nope"] = True
    response = client.request(method, _url(path), headers=AUTH, json=payload)
    assert response.status_code == 422, (path, response.status_code, response.text)
    body = response.json()
    assert "detail" not in body
    error = body["error"]
    assert set(error) == {"code", "message", "details"}
    assert error["code"]
    assert error["message"]
