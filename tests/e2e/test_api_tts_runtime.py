"""MEU-73 REST contract for the `tts_voice_packs` asset (AC-73.7), and MEU-74 voice
availability and eSpeak NG detection (AC-74.3, AC-74.4, AC-74.5). Fakes only."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from tests.e2e.api_fakes import AUTH, TOKENS, FakeModels, make_bundle
from tests.tts_asset_fakes import FakeAssets, idle_runtime

from avkit_api.main import create_app
from avkit_core.domain.tts import AssetState, TtsAsset


class AssetModels(FakeModels):
    """`FakeModels` that records `download_asset` calls."""

    def __init__(self) -> None:
        super().__init__()
        self.assets: list[TtsAsset] = []

    def download_asset(self, asset: TtsAsset) -> None:
        self.assets.append(asset)


def _client(packs: AssetState = AssetState.READY) -> tuple[TestClient, AssetModels]:
    models = AssetModels()
    services, _trx, _tts, _models = make_bundle(models=models)
    base = services.health.dependencies()

    def dependencies() -> SimpleNamespace:
        return SimpleNamespace(**{**vars(base), "tts_voice_packs": packs})

    services.health.dependencies = dependencies  # type: ignore[method-assign]
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    return TestClient(app), models


def test_ac_73_7_download_accepts_the_voice_packs_asset() -> None:
    client, models = _client()
    response = client.post(
        "/api/v1/models/download", headers=AUTH, json={"asset": "tts_voice_packs"}
    )
    assert response.status_code == 202, response.text
    assert response.json() == {"variant": None, "asset": "tts_voice_packs"}
    assert models.assets == [TtsAsset.VOICE_PACKS]


@pytest.mark.parametrize("state", ["ready", "missing", "downloading"])
def test_ac_73_7_health_dependencies_reports_voice_packs(state: str) -> None:
    client, _models = _client(AssetState(state))
    response = client.get("/api/v1/health/dependencies", headers=AUTH)
    assert response.status_code == 200, response.text
    deps = response.json()
    assert deps.get("tts_voice_packs") == {
        "available": state == "ready",
        "version": None,
        "state": state,
    }


def test_ac_73_7_unknown_asset_wire_is_422() -> None:
    client, models = _client()
    response = client.post(
        "/api/v1/models/download", headers=AUTH, json={"asset": "tts_voice_pack"}
    )
    assert response.status_code == 422, response.text
    assert models.assets == []


# --- MEU-74 voice availability and eSpeak NG detection (AC-74.3, AC-74.4, AC-74.5) -----------

ESPEAK_VERSION = (
    "eSpeak NG text-to-speech: 1.52.0  Data at: C:\\Program Files\\eSpeak NG\\espeak-ng-data"
)
ESPEAK_EXE = Path("C:/Program Files/eSpeak NG/espeak-ng.exe")
ONNX_VARIANT = "kokoro-onnx-fp32"


class FakeEspeak:
    """`EspeakPort` fake: a fixed `status()`; `phonemize` is never reached by these routes."""

    def __init__(self, available: bool) -> None:
        from avkit_core.domain.tts import EspeakStatus

        self.result = (
            EspeakStatus(available=True, version=ESPEAK_VERSION, path=ESPEAK_EXE)
            if available
            else EspeakStatus(available=False, version=None, path=None)
        )

    def status(self) -> object:
        return self.result

    def phonemize(self, text: str, lang_code: str) -> str:
        raise AssertionError(f"phonemize must not run: {text!r} {lang_code!r}")


class VoicePort:
    """`TTSPort` fake with one voice per availability class and a loaded ONNX model."""

    def list_voices(self) -> list[object]:
        from avkit_core.domain.tts import VoiceConfig

        rows = [
            ("af_heart", "a", "American English", "female", "Heart"),
            ("ef_dora", "e", "Spanish", "female", "Dora"),
            ("jf_alpha", "j", "Japanese", "female", "Alpha"),
            ("zf_xiaobei", "z", "Mandarin Chinese", "female", "Xiaobei"),
        ]
        return [VoiceConfig(*row) for row in rows]

    def get_model_status(self) -> object:
        from avkit_core.domain.tts import ModelStatus

        return ModelStatus(
            variant_id=ONNX_VARIANT,
            name="Kokoro ONNX",
            device="cpu",
            memory_bytes=0,
            is_loaded=True,
        )

    def generate(self, *args: object) -> object:
        raise AssertionError("generate must not run behind a 409")


class RecordingUow:
    """Counts every unit of work opened; the asset check and the job row each open one."""

    def __init__(self) -> None:
        from avkit_core.domain.enums import ModelFormat, ModelPrecision
        from avkit_core.domain.tts import ModelVariant

        self.opened = 0
        variant = ModelVariant(
            id=ONNX_VARIANT,
            name="Kokoro ONNX",
            format=ModelFormat.ONNX,
            precision=ModelPrecision.FP32,
            size_bytes=1,
            path=None,
            is_downloaded=True,
        )
        self.models = SimpleNamespace(
            get=lambda variant_id: variant if variant_id == ONNX_VARIANT else None
        )

    def __call__(self) -> RecordingUow:
        self.opened += 1
        return self

    def __enter__(self) -> RecordingUow:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


class RecordingAssets(FakeAssets):
    """`FakeAssets` that records every `state` call."""

    def __init__(self) -> None:
        super().__init__()
        self.state_calls: list[TtsAsset] = []

    def state(self, asset: TtsAsset, models_dir: Path) -> AssetState:
        self.state_calls.append(asset)
        return super().state(asset, models_dir)


def _settings(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(get=lambda namespace, key: str(tmp_path / "models"))


def _tts_client(
    tmp_path: Path, *, espeak: bool
) -> tuple[TestClient, RecordingUow, RecordingAssets]:
    from avkit_core.services.tts import TTSService

    uow = RecordingUow()
    assets = RecordingAssets()
    service = TTSService(
        uow,  # type: ignore[arg-type]
        tts=VoicePort(),  # type: ignore[arg-type]
        filesystem=None,  # type: ignore[arg-type]
        media=None,  # type: ignore[arg-type]
        settings=_settings(tmp_path),  # type: ignore[arg-type]
        prepare=None,  # type: ignore[arg-type]
        assets=assets,
        espeak=FakeEspeak(espeak),  # type: ignore[arg-type]
    )
    services, _trx, _tts, _models = make_bundle()
    app = create_app(tokens=TOKENS, services=replace(services, tts=service), engine_dispose=None)
    return TestClient(app), uow, assets


def _voices(client: TestClient) -> dict[str, dict[str, object]]:
    response = client.get("/api/v1/tts/voices", headers=AUTH)
    assert response.status_code == 200, response.text
    return {row["voice_id"]: row for row in response.json()["items"]}


def _generate(client: TestClient, voice: str) -> Response:
    return client.post(
        "/api/v1/tts/generate",
        headers=AUTH,
        json={"text": "Hola", "voice": voice, "speed": 1.0, "format": "WAV", "enabled_steps": []},
    )


def _pair(row: dict[str, object]) -> tuple[object, object]:
    return row["available"], row["reason"]


def test_ac_74_3_voices_without_espeak(tmp_path: Path) -> None:
    client, _uow, _assets = _tts_client(tmp_path, espeak=False)
    rows = _voices(client)
    assert rows["af_heart"] == {
        "voice_id": "af_heart",
        "language": "American English",
        "gender": "female",
        "style_description": "Heart",
        "available": True,
        "reason": None,
    }
    assert _pair(rows["ef_dora"]) == (False, "espeak_missing")
    assert _pair(rows["jf_alpha"]) == (False, "language_unsupported")
    assert _pair(rows["zf_xiaobei"]) == (False, "language_unsupported")


def test_ac_74_3_voices_with_espeak(tmp_path: Path) -> None:
    client, _uow, _assets = _tts_client(tmp_path, espeak=True)
    rows = _voices(client)
    assert _pair(rows["af_heart"]) == (True, None)
    assert _pair(rows["ef_dora"]) == (True, None)
    assert _pair(rows["jf_alpha"]) == (False, "language_unsupported")
    assert _pair(rows["zf_xiaobei"]) == (False, "language_unsupported")


@pytest.mark.parametrize(
    ("espeak", "voice", "reason"),
    [
        (False, "ef_dora", "espeak_missing"),
        (False, "jf_alpha", "language_unsupported"),
        (False, "zf_xiaobei", "language_unsupported"),
        (True, "jf_alpha", "language_unsupported"),
        (True, "zf_xiaobei", "language_unsupported"),
    ],
)
def test_ac_74_4_unavailable_voice_is_409_before_assets_and_job_row(
    tmp_path: Path, espeak: bool, voice: str, reason: str
) -> None:
    client, uow, assets = _tts_client(tmp_path, espeak=espeak)
    response = _generate(client, voice)
    assert response.status_code == 409, response.text
    assert response.json()["error"]["message"] == f"voice unavailable: {voice} ({reason})"
    assert assets.state_calls == []
    assert uow.opened == 0


def test_ac_74_4_available_voice_reaches_the_asset_check(tmp_path: Path) -> None:
    client, uow, assets = _tts_client(tmp_path, espeak=True)
    assets.states[TtsAsset.VOICE_PACKS] = AssetState.MISSING
    response = _generate(client, "ef_dora")
    assert response.status_code == 409, response.text
    assert response.json()["error"]["message"] == "tts asset missing: tts_voice_packs"
    assert TtsAsset.VOICE_PACKS in assets.state_calls
    assert uow.opened == 1


def _health_client(tmp_path: Path, *, espeak: bool) -> TestClient:
    from avkit_core.services.health import HealthService

    health = HealthService(
        RecordingUow(),  # type: ignore[arg-type]
        app_data=tmp_path,
        settings=_settings(tmp_path),  # type: ignore[arg-type]
        media=SimpleNamespace(ffmpeg_version=lambda: "7.1", ffmpeg_binaries=lambda: None),  # type: ignore[arg-type]
        youtube=SimpleNamespace(ytdlp_version=lambda: "2026.08.30"),  # type: ignore[arg-type]
        assets=FakeAssets(),
        download_runtime=idle_runtime,
        espeak=FakeEspeak(espeak),  # type: ignore[arg-type]
    )
    services, _trx, _tts, _models = make_bundle()
    app = create_app(tokens=TOKENS, services=replace(services, health=health), engine_dispose=None)
    return TestClient(app)


def _dependencies(client: TestClient) -> dict[str, object]:
    response = client.get("/api/v1/health/dependencies", headers=AUTH)
    assert response.status_code == 200, response.text
    return response.json()


def test_ac_74_5_health_reports_espeak_when_present(tmp_path: Path) -> None:
    deps = _dependencies(_health_client(tmp_path, espeak=True))
    assert deps.get("tts_espeak") == {
        "available": True,
        "version": ESPEAK_VERSION,
        "path": str(ESPEAK_EXE),
    }


def test_ac_74_5_health_reports_nulls_when_absent(tmp_path: Path) -> None:
    deps = _dependencies(_health_client(tmp_path, espeak=False))
    assert deps.get("tts_espeak") == {"available": False, "version": None, "path": None}
