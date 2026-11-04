"""MEU-73 voice packs and the v1.0 ONNX layout (AC-73.2, 73.3, 73.5, 73.9, 73.15, 73.16).

Fakes stand in for Hugging Face and the engines: no network, no model weights. The API
cases (AC-73.15, AC-73.16) run on the production composition root with a real SQLite file
created through the normal migrations.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from tests.integration.test_tts_assets import AUTH, Stack
from tests.integration.test_tts_models import FakeSession, _variant, _voice
from tests.tts_g2p_fakes import (
    PACK_BYTES,
    G2pSeam,
    ramp_pack,
    tts_g2p_seam,  # noqa: F401 — the G2P_SEAM fixture
    voice_pack_file,
    write_voice_pack,
    write_voice_packs,
)

from avkit_core.domain.enums import DeviceType
from avkit_core.domain.errors import ModelDownloadError
from avkit_core.domain.tts import AssetState, TtsAsset

REPO_ROOT = Path(__file__).resolve().parents[2]
TTS_DIR = REPO_ROOT / "packages" / "infrastructure" / "src" / "avkit_infra" / "tts"
ONNX_REPO_EXPECTED = "onnx-community/Kokoro-82M-v1.0-ONNX"
ONNX_REVISION_EXPECTED = "1939ad2a8e416c0acfeecc08a694d14ef25f2231"
VOCAB = {"vocab": {"a": 1, "b": 2}}


class PackFetch:
    """Stands in for `fetch_voice_pack`; writes `sizes[voice]` bytes (default: a full pack)."""

    def __init__(self, sizes: dict[str, int] | None = None) -> None:
        self.sizes = sizes or {}
        self.calls: list[str] = []

    def __call__(self, voice_id: str, models_dir: Path) -> Path:
        self.calls.append(voice_id)
        path = voice_pack_file(models_dir, voice_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"\0" * self.sizes.get(voice_id, PACK_BYTES))
        return path


def _no_vocab(models_dir: Path, on_progress: Any) -> Path:
    raise AssertionError("the vocab fetch must not run in a voice-pack test")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- AC-73.2 ------------------------------------------------------------------------------


def test_ac_73_2_state_follows_voice_packs_ready(tmp_path: Path) -> None:
    from avkit_infra.tts.assets import TtsAssetAdapter
    from avkit_infra.tts.voices import KOKORO_VOICE_IDS

    asset = TtsAsset.VOICE_PACKS
    adapter = TtsAssetAdapter(fetch_vocab=_no_vocab)
    assert len(KOKORO_VOICE_IDS) == 54
    assert adapter.state(asset, tmp_path) is AssetState.MISSING
    write_voice_packs(tmp_path, KOKORO_VOICE_IDS[:-1])
    assert adapter.state(asset, tmp_path) is AssetState.MISSING
    write_voice_pack(tmp_path, KOKORO_VOICE_IDS[-1])
    assert adapter.state(asset, tmp_path) is AssetState.READY
    assert adapter.version(asset, tmp_path) is None
    with voice_pack_file(tmp_path, "af_heart").open("r+b") as handle:
        handle.truncate(PACK_BYTES - 1)
    assert adapter.state(asset, tmp_path) is AssetState.MISSING
    write_voice_pack(tmp_path, "af_heart")
    assert adapter.state(asset, tmp_path) is AssetState.READY


# --- AC-73.3 ------------------------------------------------------------------------------


def test_ac_73_3_download_fetches_only_missing_or_wrong_size_packs(tmp_path: Path) -> None:
    from avkit_infra.tts.assets import TtsAssetAdapter

    asset = TtsAsset.VOICE_PACKS
    write_voice_packs(tmp_path)
    for voice_id in ("bf_lily", "af_bella", "zm_yunyang"):
        voice_pack_file(tmp_path, voice_id).unlink()
    with voice_pack_file(tmp_path, "ef_dora").open("r+b") as handle:
        handle.truncate(PACK_BYTES - 1)
    fetch = PackFetch()
    adapter = TtsAssetAdapter(fetch_vocab=_no_vocab, fetch_pack=fetch)
    seen: list[float] = []
    adapter.download(asset, tmp_path, seen.append)
    assert fetch.calls == ["af_bella", "bf_lily", "zm_yunyang", "ef_dora"]
    assert seen, "no progress was reported"
    assert all(0.0 <= value <= 1.0 for value in seen)
    assert seen == sorted(seen), f"progress went backwards: {seen}"
    assert seen[-1] == 1.0
    assert adapter.state(asset, tmp_path) is AssetState.READY

    fetch.calls.clear()
    seen.clear()
    adapter.download(asset, tmp_path, seen.append)
    assert fetch.calls == []
    assert seen[-1] == 1.0


def test_ac_73_3_wrong_size_pack_is_deleted_and_names_the_voice(tmp_path: Path) -> None:
    from avkit_infra.tts.assets import TtsAssetAdapter

    asset = TtsAsset.VOICE_PACKS
    fetch = PackFetch(sizes={"bf_emma": 100})
    adapter = TtsAssetAdapter(fetch_vocab=_no_vocab, fetch_pack=fetch)
    with pytest.raises(ModelDownloadError, match="bf_emma"):
        adapter.download(asset, tmp_path, lambda _fraction: None)
    assert not voice_pack_file(tmp_path, "bf_emma").exists()
    assert adapter.state(asset, tmp_path) is AssetState.MISSING


def test_ac_73_3_fetch_voice_pack_pins_the_v1_repo_and_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.model_manager import voice_packs
    from avkit_infra.model_manager.voice_packs import fetch_voice_pack
    from avkit_infra.tts.voices import ONNX_LOCAL_DIR, ONNX_REPO, ONNX_REVISION

    assert ONNX_REPO == ONNX_REPO_EXPECTED
    assert ONNX_REVISION == ONNX_REVISION_EXPECTED
    assert ONNX_LOCAL_DIR == "kokoro-v1.0-onnx"
    calls: list[dict[str, Any]] = []

    def hub(**kwargs: Any) -> str:
        calls.append(kwargs)
        local = Path(kwargs["local_dir"]) / kwargs["filename"]
        local.parent.mkdir(parents=True, exist_ok=True)
        local.write_bytes(b"\0" * PACK_BYTES)
        return str(local)

    monkeypatch.setattr(voice_packs, "hf_hub_download", hub)
    got = fetch_voice_pack("af_heart", tmp_path)
    assert calls == [
        {
            "repo_id": ONNX_REPO_EXPECTED,
            "filename": "voices/af_heart.bin",
            "revision": ONNX_REVISION_EXPECTED,
            "local_dir": str(tmp_path / "kokoro-v1.0-onnx"),
        }
    ]
    assert got == voice_pack_file(tmp_path, "af_heart")
    tts_text = "\n".join(path.read_text(encoding="utf-8") for path in TTS_DIR.rglob("*.py"))
    assert "huggingface_hub" not in tts_text


# --- AC-73.5 ------------------------------------------------------------------------------


def test_ac_73_5_onnx_style_row_is_read_from_the_voice_pack(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tts_g2p_seam: G2pSeam,  # noqa: F811
) -> None:
    import huggingface_hub

    def no_network(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("generate fetched from Hugging Face")

    monkeypatch.setattr(huggingface_hub, "hf_hub_download", no_network)
    monkeypatch.setattr("huggingface_hub.file_download.hf_hub_download", no_network)
    vocab = tmp_path / "config.json"
    vocab.write_text(json.dumps(VOCAB), encoding="utf-8")
    write_voice_packs(tmp_path)
    write_voice_pack(tmp_path, "af_heart", ramp_pack())
    weights = tmp_path / "kokoro-v1.0-onnx" / "onnx" / "model_quantized.onnx"
    weights.parent.mkdir(parents=True, exist_ok=True)
    weights.write_bytes(b"weights")
    adapter = tts_g2p_seam.adapter(onnx_vocab_path=vocab)
    adapter.load_model(_variant("kokoro-onnx-int8", weights), DeviceType.CPU)

    # ONNX_FEEDS: style = pack[min(len(ids), 510) - 1]; unknown symbols are dropped first.
    for phonemes, ids, row in (("ab", [1, 2], 1), ("axb", [1, 2], 1), ("xx", [], 0)):
        tts_g2p_seam.set_phonemes(phonemes)
        pcm = adapter.generate("hello", _voice("af_heart"), 1.0, lambda _fraction: None)
        assert pcm.size > 0
        assert bool(np.all(np.isfinite(pcm)))
        feed = FakeSession.runs[-1]
        np.testing.assert_array_equal(feed["input_ids"], np.array([[0, *ids, 0]], dtype=np.int64))
        np.testing.assert_allclose(
            feed["style"], np.full((1, 256), row / 1000.0, dtype=np.float32), err_msg=phonemes
        )


# --- AC-73.9 ------------------------------------------------------------------------------


def test_ac_73_9_sideload_ignores_the_legacy_onnx_dir(tmp_path: Path) -> None:
    from structlog.testing import capture_logs

    from avkit_infra.model_manager.manager import ModelCatalogAdapter

    legacy_dir = tmp_path / "onnx"
    legacy_dir.mkdir()
    (legacy_dir / "model.onnx").write_bytes(b"v0.19 fp32")
    (legacy_dir / "model_quantized.onnx").write_bytes(b"v0.19 int8")
    before = {path.name: _sha(path) for path in legacy_dir.iterdir()}
    local = tmp_path / "kokoro-v1.0-onnx" / "onnx" / "model_quantized.onnx"
    local.parent.mkdir(parents=True)
    local.write_bytes(b"v1.0 int8")
    elsewhere = tmp_path / "x" / "model_fp16.onnx"
    elsewhere.parent.mkdir()
    elsewhere.write_bytes(b"user fp16")
    with capture_logs() as logs:
        variants = ModelCatalogAdapter().sideload(tmp_path)
    by_id = {variant.id: variant for variant in variants}
    assert set(by_id) == {"kokoro-onnx-int8", "kokoro-onnx-fp16"}
    assert by_id["kokoro-onnx-int8"].path == local
    assert by_id["kokoro-onnx-fp16"].path == elsewhere
    ignored = [entry for entry in logs if entry["event"] == "model.legacy_onnx_ignored"]
    assert len(ignored) == 1
    assert {path.name: _sha(path) for path in legacy_dir.iterdir()} == before


# --- AC-73.15 / 73.16 ---------------------------------------------------------------------


@pytest.fixture
def stack(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Stack]:
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setattr(sys, "path", list(sys.path))
    before = set(sys.modules)
    built = Stack(tmp_path, monkeypatch)
    try:
        yield built
    finally:
        # A load starts the spaCy download in the background (AC-62.7). Wait for it, so its
        # install dir lands on this test's sys.path copy, not on the restored process-wide one.
        built.wait_idle()
        built.client.close()
        built.dispose()
        for name in set(sys.modules) - before:
            if name.startswith("en_core_web_sm"):
                del sys.modules[name]


def _legacy_int8_row(stack: Stack) -> Path:
    """Persist `kokoro-onnx-int8` at its v0.19 place, the way a v0.19 download left it."""
    legacy = stack.models_dir / "onnx" / "model_quantized.onnx"
    legacy.parent.mkdir(parents=True, exist_ok=True)
    legacy.write_bytes(b"v0.19 int8 weights")
    with stack.services.models._uow_factory() as uow:  # type: ignore[attr-defined]
        uow.models.mark_downloaded("kokoro-onnx-int8", legacy)
        uow.commit()
    stack.put_vocab()
    return legacy


def _int8_downloaded(stack: Stack) -> bool:
    items = stack.client.get("/api/v1/models/available", headers=AUTH).json()["items"]
    return next(item for item in items if item["id"] == "kokoro-onnx-int8")["is_downloaded"]


def test_ac_73_15_is_legacy_onnx_path_table(tmp_path: Path) -> None:
    from avkit_core.domain.tts import is_legacy_onnx_path

    models = tmp_path / "models"
    cases = [
        (models / "onnx" / "model.onnx", True),
        (models / "onnx" / "model_quantized.onnx", True),
        (models / "onnx" / "MODEL_FP16.ONNX", True),
        (models / "kokoro-v1.0-onnx" / "onnx" / "model.onnx", False),
        (models / "kokoro-v1_0.pth", False),
        (models / "onnx" / "kokoro-v1_0.pth", False),
        (models / "x" / "model_fp16.onnx", False),
        (models / "onnx" / "nested" / "model.onnx", False),
        (tmp_path / "other" / "onnx" / "model.onnx", False),
    ]
    for path, expected in cases:
        assert is_legacy_onnx_path(path, models) is expected, path


def test_ac_73_15_legacy_row_reads_not_downloaded_and_load_is_refused(stack: Stack) -> None:
    legacy = _legacy_int8_row(stack)
    digest = _sha(legacy)
    assert _int8_downloaded(stack) is False
    response = stack.client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
    )
    assert response.status_code == 409, response.text
    assert response.json()["error"]["message"] == (
        "model variant kokoro-onnx-int8 needs a re-download (v0.19 file)"
    )
    assert FakeSession.calls == []
    assert stack.client.get("/api/v1/models/status", headers=AUTH).json()["is_loaded"] is False
    assert _sha(legacy) == digest


def test_ac_73_16_redownload_over_a_legacy_row_fetches_v1(stack: Stack) -> None:
    from avkit_infra.tts.voices import ONNX_LOCAL_DIR, ONNX_REPO, ONNX_REVISION, variant_local_path

    legacy = _legacy_int8_row(stack)
    digest = _sha(legacy)
    started = stack.client.post(
        "/api/v1/models/download", headers=AUTH, json={"variant_id": "kokoro-onnx-int8"}
    )
    assert started.status_code == 202, started.text
    assert stack.wait_idle()["state"] == "Idle"
    weights = [call for call in stack.hub.calls if call["filename"] != "config.json"]
    assert len(weights) == 1, weights
    assert weights[0]["repo_id"] == ONNX_REPO
    assert weights[0]["filename"] == "onnx/model_quantized.onnx"
    assert weights[0]["revision"] == ONNX_REVISION
    assert Path(weights[0]["local_dir"]) == stack.models_dir / ONNX_LOCAL_DIR
    with stack.services.models._uow_factory() as uow:  # type: ignore[attr-defined]
        row = uow.models.get("kokoro-onnx-int8")
    assert row is not None
    assert row.path == variant_local_path("kokoro-onnx-int8", stack.models_dir)
    assert _int8_downloaded(stack) is True
    loaded = stack.client.post(
        "/api/v1/models/load",
        headers=AUTH,
        json={"variant_id": "kokoro-onnx-int8", "device": "cpu"},
    )
    assert loaded.status_code == 200, loaded.text
    assert _sha(legacy) == digest
