"""MEU-73 voice-pack service tests (AC-73.1, AC-73.4, AC-73.6). Fakes only; no network."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest
from tests import tts_asset_fakes
from tests.unit import test_services
from tests.unit.test_services import _tts_stack

from avkit_core.domain.enums import MediaFormat, ModelFormat, TTSSourceKind
from avkit_core.domain.errors import ConflictError, ModelDownloadError
from avkit_core.domain.tts import AssetState, ModelDownloadRuntime, TtsAsset, required_tts_assets

ENGLISH_VOICES = ("af_heart", "am_eric", "bf_alice", "bm_george")
OTHER_VOICES = ("ef_dora", "ff_siwis", "hf_alpha", "if_sara", "jf_alpha", "pf_dora", "zf_xiaobei")


class HoldingAssets(tts_asset_fakes.FakeAssets):
    """`FakeAssets` whose voice-pack download blocks until released, then may fail."""

    def __init__(self) -> None:
        super().__init__()
        self.entered = threading.Event()
        self.release = threading.Event()
        self.pack_error: Exception | None = None

    def download(self, asset: TtsAsset, models_dir: Path, on_progress) -> Path:  # type: ignore[no-untyped-def]
        if asset is TtsAsset.VOICE_PACKS:
            on_progress(0.5)
            self.entered.set()
            self.release.wait(timeout=5)
            if self.pack_error is not None:
                self.downloads.append(asset)
                raise self.pack_error
        return super().download(asset, models_dir, on_progress)


def _stack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, packs: AssetState):
    """`_tts_stack` with one shared `HoldingAssets` behind both services."""
    assets = HoldingAssets()
    assets.states[TtsAsset.VOICE_PACKS] = packs
    monkeypatch.setattr(test_services, "FakeAssets", lambda: assets)
    service, models, tts_port, catalog, _fs, _media, uow = _tts_stack(tmp_path)
    return service, models, tts_port, catalog, uow, assets


def _settled(models) -> ModelDownloadRuntime:  # type: ignore[no-untyped-def]
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        runtime = models.get_download_runtime()
        if runtime.state != "Downloading":
            return runtime
        time.sleep(0.01)
    raise AssertionError("download runtime never settled")


def test_ac_73_1_voice_packs_is_declared_last() -> None:
    assert TtsAsset.VOICE_PACKS.value == "tts_voice_packs"
    assert list(TtsAsset) == [TtsAsset.ONNX_VOCAB, TtsAsset.SPACY_MODEL, TtsAsset.VOICE_PACKS]


@pytest.mark.parametrize("variant_format", list(ModelFormat))
def test_ac_73_1_required_assets_include_voice_packs(variant_format: ModelFormat) -> None:
    packs = TtsAsset.VOICE_PACKS
    vocab, spacy = TtsAsset.ONNX_VOCAB, TtsAsset.SPACY_MODEL
    for voice in ENGLISH_VOICES:
        assert required_tts_assets(variant_format, voice, []) == (vocab, spacy, packs), voice
    for voice in OTHER_VOICES:
        assert required_tts_assets(variant_format, voice, []) == (vocab, packs), voice
        assert required_tts_assets(variant_format, voice, ["chunk"]) == (vocab, spacy, packs), voice


def test_ac_73_4_missing_voice_packs_is_409_before_any_job_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _models, tts_port, _catalog, uow, _assets = _stack(
        tmp_path, monkeypatch, AssetState.MISSING
    )
    with pytest.raises(ConflictError, match="^tts asset missing: tts_voice_packs$"):
        service.generate(
            "hello world", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None
        )
    assert uow.tts_jobs._rows == {}
    assert tts_port.generate_calls == 0


def test_ac_73_4_vocab_409_still_comes_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service, _models, _tts_port, _catalog, uow, assets = _stack(
        tmp_path, monkeypatch, AssetState.MISSING
    )
    assets.states[TtsAsset.ONNX_VOCAB] = AssetState.MISSING
    with pytest.raises(ConflictError, match="^tts asset missing: tts_onnx_vocab$"):
        service.generate(
            "hello world", "am_eric", 1.0, MediaFormat.WAV, [], TTSSourceKind.Inline, None
        )
    assert uow.tts_jobs._rows == {}


def test_ac_73_6_variant_download_chains_the_missing_packs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _service, models, _tts_port, _catalog, uow, assets = _stack(
        tmp_path, monkeypatch, AssetState.MISSING
    )
    models.download("kokoro-pt-fp32")
    assert assets.entered.wait(timeout=5), "the voice-pack download never started"
    runtime = models.get_download_runtime()
    assert runtime.state == "Downloading"
    assert runtime.asset is TtsAsset.VOICE_PACKS
    assert runtime.variant_id is None
    assert uow.models.get("kokoro-pt-fp32").is_downloaded is True
    assets.release.set()
    assert _settled(models).state == "Idle"
    assert assets.downloads == [TtsAsset.VOICE_PACKS]
    assert assets.states[TtsAsset.VOICE_PACKS] is AssetState.READY


def test_ac_73_6_present_packs_are_not_fetched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _service, models, _tts_port, _catalog, uow, assets = _stack(
        tmp_path, monkeypatch, AssetState.READY
    )
    models.download("kokoro-pt-fp32")
    assert _settled(models).state == "Idle"
    assert assets.downloads == []
    assert not assets.entered.is_set()
    assert uow.models.get("kokoro-pt-fp32").is_downloaded is True


def test_ac_73_6_pack_failure_keeps_the_variant_and_fails_the_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _service, models, _tts_port, _catalog, uow, assets = _stack(
        tmp_path, monkeypatch, AssetState.MISSING
    )
    assets.pack_error = ModelDownloadError("voice pack af_heart has the wrong size")
    assets.release.set()
    models.download("kokoro-pt-fp32")
    runtime = _settled(models)
    assert runtime.state == "Failed"
    assert runtime.asset is TtsAsset.VOICE_PACKS
    assert runtime.error_message is not None
    assert "tts_voice_packs" in runtime.error_message
    assert "af_heart" in runtime.error_message
    assert uow.models.get("kokoro-pt-fp32").is_downloaded is True
