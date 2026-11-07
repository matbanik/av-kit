"""MEU-117 AC-117.8 `MODEL_FIELDS` and `MODEL_REFUSAL` over HTTP, through a real `ModelService`.

The service runs over the unit-test fakes: `FakeUnitOfWork` seeded with the four catalog rows,
`FakeCatalog`, `FakeTTSPort` (PyTorch absent unless a test says otherwise) and `FakeAssets`
(every asset ready). The models folder is under `tmp_path` and holds a stub `kokoro-v1_0.pth`,
so the PyTorch row reads downloaded.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from tests.e2e.api_fakes import AUTH, make_client
from tests.tts_asset_fakes import FakeAssets
from tests.unit.test_services import FakeCatalog, FakeTTSPort, FakeUnitOfWork, SharedFakeFactory

from avkit_core.domain.enums import ModelFormat, ModelPrecision
from avkit_core.domain.tts import MODEL_REASONS, ModelVariant
from avkit_core.services.models import ModelService
from avkit_core.services.settings import SettingsService
from avkit_infra.database.engine import SEED_VARIANTS

PYTORCH_ID = "kokoro-pt-fp32"


class _CountingCatalog(FakeCatalog):
    """`FakeCatalog` that records each variant it is asked to download."""

    def __init__(self) -> None:
        super().__init__()
        self.downloads: list[str] = []

    def download(self, variant: object, dest_dir: Path, on_progress: object) -> Path:
        self.downloads.append(variant.id)  # type: ignore[attr-defined]
        return super().download(variant, dest_dir, on_progress)


def _client(
    tmp_path: Path, *, pytorch_present: bool
) -> tuple[TestClient, ModelService, _CountingCatalog, Path]:
    models_dir = tmp_path / "models"
    models_dir.mkdir()
    stub = models_dir / "kokoro-v1_0.pth"
    stub.write_bytes(bytes(16))
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("tts", "models_directory", str(models_dir))
    for variant_id, name, fmt, precision, size in SEED_VARIANTS:
        on_disk = variant_id == PYTORCH_ID
        uow.models._rows[variant_id] = ModelVariant(
            id=variant_id,
            name=name,
            format=ModelFormat(fmt),
            precision=ModelPrecision(precision),
            size_bytes=size,
            path=stub if on_disk else None,
            is_downloaded=on_disk,
        )
    tts_port = FakeTTSPort()
    if not pytorch_present:
        tts_port.absent = {ModelFormat.PyTorch}
    catalog = _CountingCatalog()
    service = ModelService(
        factory, catalog=catalog, tts=tts_port, settings=settings, assets=FakeAssets()
    )
    client, _trx, _tts, _models = make_client(models=service)  # type: ignore[arg-type]
    return client, service, catalog, models_dir


def _rows(client: TestClient, route: str) -> dict[str, dict[str, object]]:
    response = client.get(f"/api/v1/models/{route}", headers=AUTH)
    assert response.status_code == 200, response.text
    rows = {item["id"]: item for item in response.json()["items"]}
    for variant_id, item in rows.items():
        assert "available" in item and "reason" in item, f"{route} {variant_id}: {sorted(item)}"
    return rows


def _listing(models_dir: Path) -> list[str]:
    return sorted(path.name for path in models_dir.iterdir())


def test_ac_117_8_unavailable_variant_is_listed_and_refused(tmp_path: Path) -> None:
    client, service, catalog, models_dir = _client(tmp_path, pytorch_present=False)
    reason = MODEL_REASONS[ModelFormat.PyTorch]
    available = _rows(client, "available")
    assert sorted(available) == sorted(row[0] for row in SEED_VARIANTS)
    pytorch = available[PYTORCH_ID]
    assert (pytorch["available"], pytorch["reason"], pytorch["is_downloaded"]) == (
        False,
        reason,
        True,
    )
    for variant_id, item in available.items():
        if variant_id != PYTORCH_ID:
            assert (item["available"], item["reason"]) == (True, None), variant_id
    downloaded = _rows(client, "downloaded")
    assert {key: (item["available"], item["reason"]) for key, item in downloaded.items()} == {
        PYTORCH_ID: (False, reason)
    }

    before = _listing(models_dir)
    refused = client.post("/api/v1/models/download", headers=AUTH, json={"variant_id": PYTORCH_ID})
    assert refused.status_code == 409, refused.text
    error = refused.json()["error"]
    assert (error["code"], error["message"]) == ("ConflictError", reason)
    runtime = client.get("/api/v1/models/download-runtime", headers=AUTH)
    assert runtime.status_code == 200, runtime.text
    assert runtime.json()["state"] == "Idle"
    assert service._thread is None
    assert catalog.downloads == []
    assert not catalog.entered.is_set()
    assert _listing(models_dir) == before

    loaded = client.post(
        "/api/v1/models/load", headers=AUTH, json={"variant_id": PYTORCH_ID, "device": "cpu"}
    )
    assert loaded.status_code == 422, loaded.text
    error = loaded.json()["error"]
    assert (error["code"], error["message"]) == ("ModelLoadError", reason)
    assert _listing(models_dir) == before
    assert _rows(client, "available")[PYTORCH_ID]["is_downloaded"] is True


def test_ac_117_8_available_variant_downloads_as_today(tmp_path: Path) -> None:
    client, service, catalog, _models_dir = _client(tmp_path, pytorch_present=True)
    response = client.post("/api/v1/models/download", headers=AUTH, json={"variant_id": PYTORCH_ID})
    assert response.status_code == 202, response.text
    variant = response.json()["variant"]
    assert "available" in variant and "reason" in variant, sorted(variant)
    assert (variant["id"], variant["available"], variant["reason"]) == (PYTORCH_ID, True, None)
    if service._thread is not None:
        service._thread.join(timeout=5)
    assert catalog.downloads == [PYTORCH_ID]
    assert service.get_download_runtime().state == "Idle"
