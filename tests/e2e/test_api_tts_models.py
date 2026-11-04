"""MEU-16 TTS, voices facade, and model runtime tests (AC-16.3–16.5, AC-16.7)."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from tests.e2e.api_fakes import AUTH, VARIANT_ID, FakeModels, FakeTTS, make_client

from avkit_core.domain.enums import DeviceType, ModelFormat

OPENAPI = Path(__file__).resolve().parents[2] / "openapi.committed.json"
WIRE_DEVICES = ["auto", "cuda", "cpu", "mps"]


def _assert_envelope(body: dict[str, object]) -> None:
    error = body["error"]
    assert set(error) == {"code", "message", "details"}


def test_ac_16_3_prepare_generate_preview_and_unread_source() -> None:
    client, _trx, tts, _models = make_client()
    unknown = client.post(
        "/api/v1/tts/prepare",
        headers=AUTH,
        json={"text": "Hello", "enabled_steps": ["not-a-step"]},
    )
    prepared = client.post(
        "/api/v1/tts/prepare",
        headers=AUTH,
        json={"text": "Hello", "enabled_steps": ["whitespace"]},
    )
    generated = client.post(
        "/api/v1/tts/generate",
        headers=AUTH,
        json={
            "text": "Hello world",
            "voice": "am_eric",
            "speed": 1.0,
            "format": "MP3",
            "enabled_steps": ["whitespace"],
            "source_kind": "file",
            "source_path": "C:/tmp/source.txt",
        },
    )
    assert unknown.status_code == 422
    _assert_envelope(unknown.json())
    assert prepared.status_code == 200
    assert prepared.json() == {"cleaned_text": "Hello"}
    assert generated.status_code == 201
    body = generated.json()
    assert "text" not in body
    assert body["text_preview"] == "Hello world"
    assert body["source_path"] in {"C:/tmp/source.txt", "C:\\tmp\\source.txt"}
    assert tts.filesystem.read_text_calls == 0


def test_ac_16_4_no_model_and_overlap_are_409() -> None:
    unloaded = FakeTTS()
    unloaded.model_loaded = False
    client, _trx, _tts, _models = make_client(tts=unloaded)
    missing = client.post(
        "/api/v1/tts/generate",
        headers=AUTH,
        json={
            "text": "Hello",
            "voice": "am_eric",
            "speed": 1.0,
            "format": "WAV",
            "enabled_steps": [],
        },
    )
    assert missing.status_code == 409
    _assert_envelope(missing.json())
    assert missing.json()["error"]["code"] == "ConflictError"

    busy = FakeTTS()
    busy.busy = True
    client_busy, _trx2, _tts2, _models2 = make_client(tts=busy)
    overlap = client_busy.post(
        "/api/v1/tts/generate",
        headers=AUTH,
        json={
            "text": "Hello",
            "voice": "am_eric",
            "speed": 1.0,
            "format": "WAV",
            "enabled_steps": [],
        },
    )
    assert overlap.status_code == 409
    _assert_envelope(overlap.json())


def test_ac_16_5_model_download_runtime_and_load() -> None:
    client, _trx, _tts, models = make_client()
    first = client.post(
        "/api/v1/models/download",
        headers=AUTH,
        json={"variant_id": VARIANT_ID},
    )
    second = client.post(
        "/api/v1/models/download",
        headers=AUTH,
        json={"variant_id": VARIANT_ID},
    )
    runtime = client.get("/api/v1/models/download-runtime", headers=AUTH)
    loaded = client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": VARIANT_ID, "device": "cpu"},
    )
    status = client.get("/api/v1/models/status", headers=AUTH)
    unloaded = client.post("/api/v1/models/unload", headers=AUTH)
    after = client.get("/api/v1/models/status", headers=AUTH)
    available = client.get("/api/v1/models/available", headers=AUTH)
    downloaded = client.get("/api/v1/models/downloaded", headers=AUTH)

    assert first.status_code == 202
    assert "variant" in first.json()
    assert first.json()["variant"]["id"] == VARIANT_ID
    assert second.status_code == 409
    _assert_envelope(second.json())
    assert runtime.status_code == 200
    assert runtime.json()["state"] == "Downloading"
    assert models.downloading is True
    assert loaded.status_code == 200
    assert status.json()["is_loaded"] is True
    assert unloaded.status_code == 204
    assert after.json()["is_loaded"] is False
    assert available.status_code == 200
    assert downloaded.status_code == 200


def test_ac_16_5_empty_variant_id_is_422() -> None:
    client, _trx, _tts, models = make_client()
    empty_download = client.post(
        "/api/v1/models/download",
        headers=AUTH,
        json={"variant_id": ""},
    )
    empty_load = client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "", "device": "cpu"},
    )
    assert empty_download.status_code == 422
    assert empty_load.status_code == 422
    _assert_envelope(empty_download.json())
    _assert_envelope(empty_load.json())
    assert "detail" not in empty_download.json()
    assert "detail" not in empty_load.json()
    assert models.downloading is False


def test_ac_16_7_voices_facade_calls_public_list_voices() -> None:
    client, _trx, tts, _models = make_client()
    response = client.get("/api/v1/tts/voices", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items"}
    assert body["items"][0] == {
        "voice_id": "am_eric",
        "language": "American English",
        "gender": "male",
        "style_description": "Eric",
        "available": True,
        "reason": None,
    }
    assert "lang_code" not in body["items"][0]
    assert tts.list_voices_calls >= 1
    source = Path("packages/api/src/avkit_api/routes/tts.py").read_text(encoding="utf-8")
    assert "._tts" not in source
    assert "read_text" not in source
    assert "lang_code" not in source


class _CudaModels(FakeModels):
    def available_devices(self, fmt: ModelFormat) -> tuple[DeviceType, ...]:
        del fmt
        return (DeviceType.Auto, DeviceType.CUDA, DeviceType.CPU)


def _variant_payloads(models: FakeModels) -> list[dict[str, object]]:
    models.variant = replace(models.variant, is_downloaded=True)
    client, _trx, _tts, _models = make_client(models=models)
    available = client.get("/api/v1/models/available", headers=AUTH)
    downloaded = client.get("/api/v1/models/downloaded", headers=AUTH)
    download = client.post("/api/v1/models/download", headers=AUTH, json={"variant_id": VARIANT_ID})
    assert available.status_code == 200, available.text
    assert downloaded.status_code == 200, downloaded.text
    assert download.status_code == 202, download.text
    items = [*available.json()["items"], *downloaded.json()["items"], download.json()["variant"]]
    assert len(items) == 3
    return items


def test_ac_75_8_variant_payloads_carry_devices() -> None:
    for item in _variant_payloads(FakeModels()):
        assert item.get("devices") == ["auto", "cpu"], item
    for item in _variant_payloads(_CudaModels()):
        assert item.get("devices") == ["auto", "cuda", "cpu"], item


def test_ac_75_8_openapi_requires_devices() -> None:
    schemas = json.loads(OPENAPI.read_text(encoding="utf-8"))["components"]["schemas"]
    schema = schemas["ModelVariantOut"]
    assert "devices" in schema.get("required", []), schema
    devices = schema["properties"].get("devices", {})
    assert devices.get("type") == "array", devices
    assert sorted(devices.get("items", {}).get("enum", [])) == sorted(WIRE_DEVICES), devices


def test_ac_75_8_unknown_device_is_422_neg() -> None:
    client, _trx, _tts, _models = make_client()
    response = client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": VARIANT_ID, "device": "tpu"},
    )
    assert response.status_code == 422
    _assert_envelope(response.json())
