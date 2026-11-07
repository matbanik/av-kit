"""MEU-119 AC-119.9 `LOAD_KEEPS` over HTTP, through a real `ModelService` and `KokoroAdapter`.

The service runs over the unit-test fakes: `FakeUnitOfWork` seeded with the four catalog rows,
`FakeCatalog` and `FakeAssets` (every asset ready). The port is a real `KokoroAdapter` whose
`InferenceSession` is a fake and whose device probe is injected. The models folder is under
`tmp_path` and holds a stub INT8 file; the FP32 row holds a path whose file is gone.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from tests.e2e.api_fakes import AUTH, make_client
from tests.tts_asset_fakes import FakeAssets
from tests.unit.test_services import FakeCatalog, FakeUnitOfWork, SharedFakeFactory

from avkit_core.domain.enums import DeviceType, ModelFormat, ModelPrecision
from avkit_core.domain.tts import ModelVariant
from avkit_core.services.models import ModelService
from avkit_core.services.settings import SettingsService
from avkit_infra.database.engine import SEED_VARIANTS

INT8_ID = "kokoro-onnx-int8"
FP32_ID = "kokoro-onnx-fp32"


def _client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[TestClient, list[str]]:
    from avkit_infra.tts.adapter import KokoroAdapter

    sessions: list[str] = []

    class Session:
        """`InferenceSession` stand-in: records the file name it was built on, reads nothing."""

        def __init__(self, path: object, providers: object = None, **kwargs: object) -> None:
            sessions.append(Path(str(path)).name)

        def get_providers(self) -> list[str]:
            return ["CPUExecutionProvider"]

    monkeypatch.setattr("avkit_infra.tts.adapter.InferenceSession", Session)
    models_dir = tmp_path / "models"
    weights = models_dir / "kokoro-v1.0-onnx" / "onnx"
    weights.mkdir(parents=True)
    int8 = weights / "model_quantized.onnx"
    int8.write_bytes(bytes(16))
    # The FP32 row's file is gone: the row still holds its path.
    paths = {INT8_ID: int8, FP32_ID: weights / "model.onnx"}
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("tts", "models_directory", str(models_dir))
    for variant_id, name, fmt, precision, size in SEED_VARIANTS:
        path = paths.get(variant_id)
        uow.models._rows[variant_id] = ModelVariant(
            id=variant_id,
            name=name,
            format=ModelFormat(fmt),
            precision=ModelPrecision(precision),
            size_bytes=size,
            path=path,
            is_downloaded=path is not None,
        )
    adapter = KokoroAdapter(
        onnx_vocab_path=models_dir / "config.json",
        device_probe=lambda _fmt: (DeviceType.Auto, DeviceType.CPU),
    )
    service = ModelService(
        factory, catalog=FakeCatalog(), tts=adapter, settings=settings, assets=FakeAssets()
    )
    client, _trx, _tts, _models = make_client(models=service)  # type: ignore[arg-type]
    return client, sessions


def test_ac_119_9_failed_load_keeps_the_loaded_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    client, sessions = _client(tmp_path, monkeypatch)
    loaded = client.post(
        "/api/v1/models/load", headers=AUTH, json={"variant_id": INT8_ID, "device": "cpu"}
    )
    assert loaded.status_code == 200, loaded.text
    assert sessions == ["model_quantized.onnx"]

    refused = client.post(
        "/api/v1/models/load", headers=AUTH, json={"variant_id": FP32_ID, "device": "cpu"}
    )
    assert refused.status_code == 422, refused.text
    error = refused.json()["error"]
    assert (error["code"], error["message"]) == ("ModelLoadError", "model weight file is missing")
    assert sessions == ["model_quantized.onnx"]

    status = client.get("/api/v1/models/status", headers=AUTH)
    assert status.status_code == 200, status.text
    body = status.json()
    assert (body["is_loaded"], body["variant_id"], body["device"]) == (True, INT8_ID, "cpu")
