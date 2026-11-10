"""MEU-9 TTS and model-manager integration tests. Mocked Kokoro/ONNX/HF only."""

from __future__ import annotations

import ast
import inspect
import json
import math
import re
import sys
import tomllib
import types
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from tests.tts_g2p_fakes import (
    FakeG2p,
    G2pSeam,
    g2p_lang_codes,
    ramp_pack,
    set_phonemes,
    tts_g2p_seam,  # noqa: F401 — the G2P_SEAM fixture
    voice_pack_file,
    write_voice_pack,
    write_voice_packs,
)

from avkit_core.domain.enums import DeviceType, ModelFormat, ModelPrecision
from avkit_core.domain.errors import ModelDownloadError, ModelLoadError, ValidationError
from avkit_core.domain.tts import ModelVariant, VoiceConfig
from avkit_core.ports.models import ModelCatalogPort
from avkit_core.ports.tts import TTSPort

REPO_ROOT = Path(__file__).resolve().parents[2]
INFRA_SRC = REPO_ROOT / "packages" / "infrastructure" / "src"
INFRA_PYPROJECT = REPO_ROOT / "packages" / "infrastructure" / "pyproject.toml"
TTS_ADAPTER = INFRA_SRC / "avkit_infra" / "tts" / "adapter.py"
VOICES_PATH = INFRA_SRC / "avkit_infra" / "tts" / "voices.py"
CATALOG_PATH = INFRA_SRC / "avkit_infra" / "model_manager" / "catalog.py"
MANAGER_PATH = INFRA_SRC / "avkit_infra" / "model_manager" / "manager.py"
TTS_PORT_METHODS = ("load_model", "unload_model", "generate", "list_voices", "get_model_status")
MODEL_CATALOG_PORT_METHODS = ("download", "sideload")
SEED_VARIANT_IDS = (
    "kokoro-pt-fp32",
    "kokoro-onnx-fp32",
    "kokoro-onnx-fp16",
    "kokoro-onnx-int8",
)
CATALOG_METADATA_EXPECTED = {
    "kokoro-pt-fp32": {
        "name": "PyTorch FP32",
        "format": ModelFormat.PyTorch,
        "precision": ModelPrecision.FP32,
        "catalog_size_bytes": 326 * 1024 * 1024,
    },
    "kokoro-onnx-fp32": {
        "name": "ONNX FP32",
        "format": ModelFormat.ONNX,
        "precision": ModelPrecision.FP32,
        "catalog_size_bytes": 326 * 1024 * 1024,
    },
    "kokoro-onnx-fp16": {
        "name": "ONNX FP16",
        "format": ModelFormat.ONNX,
        "precision": ModelPrecision.FP16,
        "catalog_size_bytes": 163 * 1024 * 1024,
    },
    "kokoro-onnx-int8": {
        "name": "ONNX INT8",
        "format": ModelFormat.ONNX,
        "precision": ModelPrecision.INT8,
        "catalog_size_bytes": 87 * 1024 * 1024,
    },
}
HF_FILE_MAP_EXPECTED = {
    "kokoro-pt-fp32": ("hexgrad/Kokoro-82M", "kokoro-v1_0.pth"),
    "kokoro-onnx-fp32": ("onnx-community/Kokoro-82M-v1.0-ONNX", "onnx/model.onnx"),
    "kokoro-onnx-fp16": ("onnx-community/Kokoro-82M-v1.0-ONNX", "onnx/model_fp16.onnx"),
    "kokoro-onnx-int8": ("onnx-community/Kokoro-82M-v1.0-ONNX", "onnx/model_quantized.onnx"),
}
KOKORO_VOICE_IDS_EXPECTED = (
    "af_heart",
    "af_alloy",
    "af_aoede",
    "af_bella",
    "af_jessica",
    "af_kore",
    "af_nicole",
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    "am_adam",
    "am_echo",
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa",
    "bf_alice",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    "bm_daniel",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    "jm_kumo",
    "zf_xiaobei",
    "zf_xiaoni",
    "zf_xiaoxiao",
    "zf_xiaoyi",
    "zm_yunjian",
    "zm_yunxi",
    "zm_yunxia",
    "zm_yunyang",
    "ef_dora",
    "em_alex",
    "em_santa",
    "ff_siwis",
    "hf_alpha",
    "hf_beta",
    "hm_omega",
    "hm_psi",
    "if_sara",
    "im_nicola",
    "pf_dora",
    "pm_alex",
    "pm_santa",
)
LANG_BY_PREFIX_EXPECTED = {
    "a": "American English",
    "b": "British English",
    "e": "Spanish",
    "f": "French",
    "h": "Hindi",
    "i": "Italian",
    "j": "Japanese",
    "p": "Brazilian Portuguese",
    "z": "Mandarin Chinese",
}
VOICE_COUNT = 54


def _dependency_name(spec: str) -> str:
    name = spec.strip()
    for separator in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if separator in name:
            name = name.split(separator, 1)[0]
    return name.strip()


def _floor_major(spec: str) -> int:
    match = re.search(r">=\s*(\d+)", spec)
    if match is None:
        raise AssertionError(f"spec {spec!r} has no >= major floor")
    return int(match.group(1))


def _onnxruntime_floor(spec: str) -> tuple[int, int]:
    match = re.search(r">=\s*(\d+)\.(\d+)", spec)
    if match is None:
        raise AssertionError(f"spec {spec!r} has no >= minor floor")
    return int(match.group(1)), int(match.group(2))


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".", 1)[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".", 1)[0])
    return names


def _import_hits_outside(root: Path, module: str, allow: str | None) -> list[str]:
    hits: list[str] = []
    for path in root.rglob("*.py"):
        if module not in _top_level_imports(path):
            continue
        rel = path.relative_to(root)
        if allow is not None and allow in rel.parts:
            continue
        hits.append(str(rel).replace("\\", "/"))
    return hits


def _variant(variant_id: str, path: Path | None = None, *, downloaded: bool = True) -> ModelVariant:
    meta = CATALOG_METADATA_EXPECTED[variant_id]
    return ModelVariant(
        id=variant_id,
        name=str(meta["name"]),
        format=meta["format"],  # type: ignore[arg-type]
        precision=meta["precision"],  # type: ignore[arg-type]
        size_bytes=int(meta["catalog_size_bytes"]),
        path=path,
        is_downloaded=downloaded,
    )


def _voice(voice_id: str = "af_heart") -> VoiceConfig:
    return VoiceConfig(
        voice_id=voice_id,
        lang_code=voice_id[0],
        language=LANG_BY_PREFIX_EXPECTED[voice_id[0]],
        gender="Female" if voice_id[1] == "f" else "Male",
        style_description=voice_id.split("_", 1)[1],
    )


class FakeKModel:
    calls: list[dict[str, Any]] = []
    to_calls: list[object] = []
    eval_calls: list[bool] = []
    forward_calls: list[dict[str, Any]] = []

    def __init__(self, *args: object, **kwargs: object) -> None:
        type(self).calls.append({"args": args, "kwargs": kwargs})

    def to(self, device: object) -> FakeKModel:
        type(self).to_calls.append(device)
        return self

    def __call__(self, phonemes: str, ref_s: object, speed: object = 1.0) -> np.ndarray:
        type(self).forward_calls.append({"phonemes": phonemes, "speed": speed})
        return np.array([0.1, 0.2], dtype=np.float32)

    def eval(self) -> FakeKModel:
        type(self).eval_calls.append(True)
        return self


class FakeSession:
    calls: list[dict[str, Any]] = []
    runs: list[dict[str, Any]] = []
    audio = np.array([[0.25, -0.25]], dtype=np.float32)

    def __init__(self, path: object, providers: object = None, **kwargs: object) -> None:
        type(self).calls.append({"path": path, "providers": providers, "kwargs": kwargs})
        self.path = path
        self.providers = providers

    def run(self, _outputs: object, feed: dict[str, Any]) -> list[np.ndarray]:
        type(self).runs.append(feed)
        return [self.audio]


def _reset_fakes() -> None:
    FakeKModel.calls = []
    FakeKModel.to_calls = []
    FakeKModel.eval_calls = []
    FakeKModel.forward_calls = []
    FakeG2p.calls = []
    FakeG2p.phonemes = "ab"
    FakeSession.calls = []
    FakeSession.runs = []
    FakeSession.audio = np.array([[0.25, -0.25]], dtype=np.float32)


def _patch_engines(monkeypatch: pytest.MonkeyPatch) -> None:
    _reset_fakes()
    # TORCH_PATH imports `KModel` from `kokoro` inside `load_model`.
    kokoro_stub = types.ModuleType("kokoro")
    kokoro_stub.KModel = FakeKModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "kokoro", kokoro_stub)
    monkeypatch.setattr("avkit_infra.tts.adapter.KokoroG2p", FakeG2p)
    monkeypatch.setattr("avkit_infra.tts.adapter.InferenceSession", FakeSession)


@pytest.mark.integration
def test_ac_9_1_layout_deps_and_kokoro_adapter_name() -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    assert KokoroAdapter.__name__ == "KokoroAdapter"
    source = TTS_ADAPTER.read_text(encoding="utf-8")
    assert "class TTSAdapter" not in source
    data = tomllib.loads(INFRA_PYPROJECT.read_text(encoding="utf-8"))
    declared = {_dependency_name(str(item)) for item in data["project"]["dependencies"]}
    assert "kokoro" in declared
    assert "huggingface_hub" in declared
    onnx_specs = [
        str(item)
        for item in data["project"]["dependencies"]
        if _dependency_name(str(item)) == "onnxruntime"
    ]
    assert onnx_specs
    assert any(_floor_major(spec) >= 1 for spec in onnx_specs)
    assert any(_onnxruntime_floor(spec) >= (1, 16) for spec in onnx_specs)
    assert "soundfile" not in declared
    infra_text = "\n".join(path.read_text(encoding="utf-8") for path in INFRA_SRC.rglob("*.py"))
    assert "soundfile" not in infra_text
    assert (INFRA_SRC / "avkit_infra" / "tts" / "voices.py").is_file()
    assert (INFRA_SRC / "avkit_infra" / "model_manager" / "catalog.py").is_file()
    assert (INFRA_SRC / "avkit_infra" / "model_manager" / "manager.py").is_file()


@pytest.mark.integration
def test_ac_9_2_port_signatures_match() -> None:
    from avkit_infra.model_manager.manager import ModelCatalogAdapter
    from avkit_infra.tts.adapter import KokoroAdapter

    for name in TTS_PORT_METHODS:
        proto = inspect.signature(getattr(TTSPort, name))
        impl = inspect.signature(getattr(KokoroAdapter, name))
        proto_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in proto.parameters.items()
        ]
        impl_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in impl.parameters.items()
        ]
        assert impl_params == proto_params, name
        assert impl.return_annotation == proto.return_annotation
    for name in MODEL_CATALOG_PORT_METHODS:
        proto = inspect.signature(getattr(ModelCatalogPort, name))
        impl = inspect.signature(getattr(ModelCatalogAdapter, name))
        proto_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in proto.parameters.items()
        ]
        impl_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in impl.parameters.items()
        ]
        assert impl_params == proto_params, name
        assert impl.return_annotation == proto.return_annotation


@pytest.mark.integration
def test_ac_9_3_list_voices_official_catalog() -> None:
    from avkit_infra.tts.adapter import KokoroAdapter
    from avkit_infra.tts.voices import KOKORO_VOICE_IDS

    voices = KokoroAdapter().list_voices()
    assert len(voices) == VOICE_COUNT
    assert len(KOKORO_VOICE_IDS_EXPECTED) == VOICE_COUNT
    assert KOKORO_VOICE_IDS == KOKORO_VOICE_IDS_EXPECTED
    assert [voice.voice_id for voice in voices] == list(KOKORO_VOICE_IDS_EXPECTED)
    for voice in voices:
        assert voice.lang_code == voice.voice_id[0]
        assert voice.language == LANG_BY_PREFIX_EXPECTED[voice.voice_id[0]]
        assert isinstance(voice, VoiceConfig)
    source = VOICES_PATH.read_text(encoding="utf-8")
    assert "SqlAlchemyUnitOfWork" not in source
    assert "avkit_infra.database" not in source


@pytest.mark.integration
def test_ac_9_4_load_model_engine_split_every_seed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    _patch_engines(monkeypatch)
    adapter = KokoroAdapter(onnx_vocab_path=tmp_path / "config.json")
    for variant_id in SEED_VARIANT_IDS:
        _reset_fakes()
        weight = tmp_path / f"{variant_id}.bin"
        weight.write_bytes(b"weights")
        variant = _variant(variant_id, weight)
        adapter.load_model(variant, DeviceType.CPU)
        if variant.format is ModelFormat.PyTorch:
            assert FakeKModel.calls, variant_id
            assert FakeKModel.to_calls == [adapter.get_model_status().device], variant_id
            assert FakeKModel.eval_calls, variant_id
            assert FakeSession.calls == []
        else:
            assert FakeKModel.calls == [], variant_id
            assert FakeKModel.to_calls == [], variant_id
            assert FakeSession.calls, variant_id
            assert FakeSession.calls[0]["providers"] == ["CPUExecutionProvider"]
        adapter.unload_model()

    missing = _variant("kokoro-pt-fp32", tmp_path / "absent.pth")
    with pytest.raises(ModelLoadError) as err:
        adapter.load_model(missing, DeviceType.CPU)
    assert isinstance(err.value.__cause__, FileNotFoundError)

    first = _variant("kokoro-pt-fp32", tmp_path / "kokoro-pt-fp32.bin")
    (tmp_path / "kokoro-pt-fp32.bin").write_bytes(b"weights")
    second = _variant("kokoro-onnx-fp32", tmp_path / "kokoro-onnx-fp32.bin")
    (tmp_path / "kokoro-onnx-fp32.bin").write_bytes(b"weights")
    adapter.load_model(first, DeviceType.CPU)
    adapter.load_model(second, DeviceType.CPU)
    assert adapter.get_model_status().variant_id == "kokoro-onnx-fp32"
    _reset_fakes()
    monkeypatch.setattr(
        "avkit_infra.tts.adapter.torch.cuda.is_available",
        lambda: False,
        raising=False,
    )
    adapter.load_model(second, DeviceType.Auto)
    assert FakeSession.calls[-1]["providers"] == ["CPUExecutionProvider"]

    pt_weight = tmp_path / "kokoro-pt-fp32.bin"
    pt_weight.write_bytes(b"weights")
    _reset_fakes()
    monkeypatch.setattr(
        "avkit_infra.tts.adapter.torch.cuda.is_available",
        lambda: True,
        raising=False,
    )
    adapter.load_model(_variant("kokoro-pt-fp32", pt_weight), DeviceType.Auto)
    assert adapter.get_model_status().device == "cuda"
    assert FakeKModel.to_calls == ["cuda"]
    assert FakeKModel.eval_calls
    _reset_fakes()
    monkeypatch.setattr(
        "avkit_infra.tts.adapter.torch.cuda.is_available",
        lambda: False,
        raising=False,
    )

    class _Mps:
        @staticmethod
        def is_available() -> bool:
            return True

    monkeypatch.setattr("avkit_infra.tts.adapter.torch.backends.mps", _Mps, raising=False)
    adapter.load_model(_variant("kokoro-pt-fp32", pt_weight), DeviceType.Auto)
    assert adapter.get_model_status().device == "mps"
    assert FakeKModel.to_calls == ["mps"]
    _reset_fakes()
    # TA-1 (Session 35, MEU-75): an explicit CUDA load needs a probe that reports CUDA;
    # `:421` patched it away, and `DEVICE_RESOLVE` would now fall back to CPU.
    with monkeypatch.context() as m:
        m.setattr("avkit_infra.tts.adapter.torch.cuda.is_available", lambda: True, raising=False)
        adapter.load_model(_variant("kokoro-pt-fp32", pt_weight), DeviceType.CUDA)
    assert adapter.get_model_status().device == "cuda"
    assert FakeKModel.to_calls == ["cuda"]
    _reset_fakes()
    adapter.load_model(_variant("kokoro-pt-fp32", pt_weight), DeviceType.CPU)
    assert adapter.get_model_status().device == "cpu"
    assert FakeKModel.to_calls == ["cpu"]


@pytest.mark.integration
def test_ac_9_5_unload_clears_loaded_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    _patch_engines(monkeypatch)
    weight = tmp_path / "model.pth"
    weight.write_bytes(b"weights")
    adapter = KokoroAdapter()
    adapter.load_model(_variant("kokoro-pt-fp32", weight), DeviceType.CPU)
    assert adapter.get_model_status().is_loaded is True
    adapter.unload_model()
    status = adapter.get_model_status()
    assert status.is_loaded is False
    assert status.variant_id is None


@pytest.mark.integration
def test_ac_9_6_generate_pytorch_and_onnx_preprocess(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    _patch_engines(monkeypatch)
    vocab_path = tmp_path / "config.json"
    vocab_path.write_text(json.dumps({"vocab": {"a": 1, "b": 2}}), encoding="utf-8")
    write_voice_packs(tmp_path)
    before = {path: path.stat().st_mtime_ns for path in tmp_path.rglob("*") if path.is_file()}
    adapter = KokoroAdapter(onnx_vocab_path=vocab_path)

    pt = tmp_path / "pt.pth"
    pt.write_bytes(b"weights")
    adapter.load_model(_variant("kokoro-pt-fp32", pt), DeviceType.CPU)
    seen: list[float] = []
    pcm = adapter.generate("hello", _voice(), 1.0, seen.append)
    assert isinstance(pcm, np.ndarray)
    assert math.isfinite(float(pcm.sum()))
    assert seen
    assert all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in seen)
    assert FakeSession.runs == []

    onnx = tmp_path / "model.onnx"
    onnx.write_bytes(b"weights")
    FakeKModel.calls = []
    FakeSession.runs = []
    adapter.load_model(_variant("kokoro-onnx-fp32", onnx), DeviceType.CPU)
    assert FakeKModel.calls == []
    seen.clear()
    set_phonemes("ab")
    pcm = adapter.generate("hello", _voice(), 1.25, seen.append)
    assert FakeSession.runs, "session.run must be called with adapter-built feed"
    feed = FakeSession.runs[0]
    np.testing.assert_array_equal(feed["input_ids"], np.array([[0, 1, 2, 0]], dtype=np.int64))
    assert feed["input_ids"].dtype == np.int64
    assert feed["input_ids"].shape[0] == 1
    assert feed["input_ids"].shape[1] <= 512
    assert feed["style"].dtype == np.float32
    assert feed["style"].shape == (1, 256)
    assert feed["speed"].dtype == np.float32
    assert feed["speed"].shape == (1,)
    np.testing.assert_allclose(feed["speed"], np.array([1.25], dtype=np.float32))
    assert all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in seen)
    after = {path: path.stat().st_mtime_ns for path in tmp_path.rglob("*") if path.is_file()}
    audio_files = [path for path in tmp_path.rglob("*") if path.suffix.lower() in {".wav", ".mp3"}]
    assert audio_files == []
    assert after[vocab_path] == before[vocab_path]


@pytest.mark.integration
def test_ac_9_7_lang_code_from_voice_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    _patch_engines(monkeypatch)
    vocab_path = tmp_path / "config.json"
    vocab_path.write_text(json.dumps({"vocab": {"a": 1, "b": 2}}), encoding="utf-8")
    onnx = tmp_path / "model.onnx"
    onnx.write_bytes(b"weights")
    write_voice_packs(tmp_path)
    adapter = KokoroAdapter(onnx_vocab_path=vocab_path)
    adapter.load_model(_variant("kokoro-onnx-fp32", onnx), DeviceType.CPU)
    # TA-2 (MEU-72): the G2P, not a KPipeline, receives the lang code of `bf_alice`.
    before = len(g2p_lang_codes())
    adapter.generate("hello", _voice("bf_alice"), 1.0, lambda _frac: None)
    codes = g2p_lang_codes()[before:]
    assert codes
    assert set(codes) == {"b"}


@pytest.mark.integration
def test_ac_9_8_download_hf_map_returns_path_no_uow(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.model_manager.catalog import HF_FILE_MAP
    from avkit_infra.model_manager.manager import ModelCatalogAdapter

    assert HF_FILE_MAP == HF_FILE_MAP_EXPECTED
    calls: list[dict[str, object]] = []

    def fake_download(**kwargs: object) -> str:
        calls.append(kwargs)
        dest = tmp_path / "kokoro-v1_0.pth"
        dest.write_bytes(b"model")
        return str(dest)

    monkeypatch.setattr("avkit_infra.model_manager.manager.hf_hub_download", fake_download)
    seen: list[float] = []
    path = ModelCatalogAdapter().download(_variant("kokoro-pt-fp32"), tmp_path, seen.append)
    assert path == tmp_path / "kokoro-v1_0.pth"
    assert calls[0]["repo_id"] == "hexgrad/Kokoro-82M"
    assert calls[0]["filename"] == "kokoro-v1_0.pth"
    assert seen
    assert all(math.isfinite(item) and 0.0 <= item <= 1.0 for item in seen)
    assert seen[-1] == 1.0
    source = MANAGER_PATH.read_text(encoding="utf-8")
    assert "mark_downloaded" not in source
    assert "SqlAlchemyUnitOfWork" not in source
    assert ".bin" not in "".join(filename for _repo, filename in HF_FILE_MAP.values())


@pytest.mark.integration
def test_ac_9_9_offline_skips_hf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.model_manager.manager import ModelCatalogAdapter

    calls: list[object] = []
    monkeypatch.setattr(
        "avkit_infra.model_manager.manager.hf_hub_download",
        lambda **kwargs: calls.append(kwargs) or "unused",
    )
    existing = tmp_path / "local.pth"
    existing.write_bytes(b"x")
    adapter = ModelCatalogAdapter()
    got = adapter.download(_variant("kokoro-pt-fp32", existing), tmp_path, lambda _frac: None)
    assert got == existing
    assert calls == []

    from avkit_infra.tts.voices import variant_local_path

    dest = variant_local_path("kokoro-onnx-fp32", tmp_path)
    dest.parent.mkdir(parents=True)
    dest.write_bytes(b"onnx")
    got = adapter.download(_variant("kokoro-onnx-fp32"), tmp_path, lambda _frac: None)
    assert got == dest
    assert calls == []


@pytest.mark.integration
def test_ac_9_10_sideload_catalog_metadata_and_stat(tmp_path: Path) -> None:
    from avkit_infra.model_manager.catalog import CATALOG_METADATA
    from avkit_infra.model_manager.manager import ModelCatalogAdapter

    assert CATALOG_METADATA == CATALOG_METADATA_EXPECTED
    (tmp_path / "kokoro-v1_0.pth").write_bytes(b"abcdefgh")
    (tmp_path / "kokoro-v1.0-onnx" / "onnx").mkdir(parents=True)
    (tmp_path / "kokoro-v1.0-onnx" / "onnx" / "model.onnx").write_bytes(b"fp32")
    (tmp_path / "kokoro-v1.0-onnx" / "onnx" / "model_fp16.onnx").write_bytes(b"fp16x")
    (tmp_path / "kokoro-v1.0-onnx" / "onnx" / "model_quantized.onnx").write_bytes(b"int8xx")
    (tmp_path / "notes.txt").write_text("nope", encoding="utf-8")
    variants = ModelCatalogAdapter().sideload(tmp_path)
    by_id = {item.id: item for item in variants}
    assert set(by_id) == set(SEED_VARIANT_IDS)
    for variant_id, variant in by_id.items():
        meta = CATALOG_METADATA_EXPECTED[variant_id]
        assert variant.name == meta["name"]
        assert variant.format == meta["format"]
        assert variant.precision == meta["precision"]
        assert variant.is_downloaded is True
        assert variant.path is not None and variant.path.is_file()
        assert variant.size_bytes == variant.path.stat().st_size
    source = CATALOG_PATH.read_text(encoding="utf-8") + MANAGER_PATH.read_text(encoding="utf-8")
    assert "avkit_infra.database" not in source


@pytest.mark.integration
def test_ac_9_11_download_oserror_is_model_download_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.model_manager.manager import ModelCatalogAdapter

    boom = OSError("hf down")
    monkeypatch.setattr(
        "avkit_infra.model_manager.manager.hf_hub_download",
        lambda **kwargs: (_ for _ in ()).throw(boom),
    )
    with pytest.raises(ModelDownloadError) as err:
        ModelCatalogAdapter().download(_variant("kokoro-pt-fp32"), tmp_path, lambda _frac: None)
    assert err.value.__cause__ is boom


@pytest.mark.integration
def test_ac_9_12_library_confinement() -> None:
    infra_src = INFRA_SRC
    core_src = REPO_ROOT / "packages" / "core" / "src"
    tts_dir = INFRA_SRC / "avkit_infra" / "tts"
    mm_dir = INFRA_SRC / "avkit_infra" / "model_manager"
    tts_text = "\n".join(path.read_text(encoding="utf-8") for path in tts_dir.rglob("*.py"))
    mm_text = "\n".join(path.read_text(encoding="utf-8") for path in mm_dir.rglob("*.py"))
    assert "from huggingface_hub" not in tts_text
    assert "import huggingface_hub" not in tts_text
    assert "from huggingface_hub" in mm_text or "huggingface_hub" in mm_text
    assert "from kokoro" in tts_text or "import kokoro" in tts_text
    assert "onnxruntime" in tts_text
    assert _import_hits_outside(infra_src, "yt_dlp", "youtube") == []
    assert _import_hits_outside(infra_src, "youtube_transcript_api", "transcript") == []
    assert _import_hits_outside(infra_src, "huggingface_hub", "model_manager") == []
    assert _import_hits_outside(infra_src, "kokoro", "tts") == []
    assert _import_hits_outside(infra_src, "onnxruntime", "tts") == []
    for module in ("yt_dlp", "youtube_transcript_api", "huggingface_hub", "kokoro", "onnxruntime"):
        assert _import_hits_outside(core_src, module, None) == []


@pytest.mark.integration
def test_ac_9_13_missing_vocab_voice_and_input_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    _patch_engines(monkeypatch)
    onnx = tmp_path / "model.onnx"
    onnx.write_bytes(b"weights")
    adapter = KokoroAdapter(onnx_vocab_path=tmp_path / "missing.json")
    adapter.load_model(_variant("kokoro-onnx-fp32", onnx), DeviceType.CPU)
    with pytest.raises(ModelLoadError) as vocab_err:
        adapter.generate("hello", _voice(), 1.0, lambda _frac: None)
    assert isinstance(vocab_err.value.__cause__, FileNotFoundError)

    vocab_path = tmp_path / "config.json"
    vocab_path.write_text(json.dumps({"vocab": {"a": 1, "b": 2}}), encoding="utf-8")
    adapter = KokoroAdapter(onnx_vocab_path=vocab_path)
    adapter.load_model(_variant("kokoro-onnx-fp32", onnx), DeviceType.CPU)
    write_voice_packs(tmp_path)
    voice_pack_file(tmp_path, "af_heart").unlink()
    with pytest.raises(ModelLoadError) as voice_err:
        adapter.generate("hello", _voice(), 1.0, lambda _frac: None)
    assert isinstance(voice_err.value.__cause__, FileNotFoundError)

    # TA-2 (MEU-72): CHUNK_RULE cuts 511 symbols into two chunks, one `session.run` each.
    write_voice_pack(tmp_path, "af_heart")
    set_phonemes("a" * 511)
    vocab_path.write_text(json.dumps({"vocab": {"a": 1}}), encoding="utf-8")
    FakeSession.runs = []
    adapter.generate("hello", _voice(), 1.0, lambda _frac: None)
    assert [feed["input_ids"].shape[1] - 2 for feed in FakeSession.runs] == [510, 1]
    mm_source = CATALOG_PATH.read_text(encoding="utf-8")
    assert "voices/" not in mm_source or ".bin" not in mm_source
    pyproject = INFRA_PYPROJECT.read_text(encoding="utf-8")
    assert "kokoro-onnx" not in pyproject
    assert "pykokoro" not in pyproject


@pytest.mark.integration
def test_ac_72_4_onnx_feeds_on_a_recording_session(
    tmp_path: Path,
    tts_g2p_seam: G2pSeam,  # noqa: F811
) -> None:
    from avkit_infra.tts.g2p import split_phonemes

    vocab = {"a": 1, "b": 2, ".": 4, " ": 16}
    vocab_path = tmp_path / "config.json"
    vocab_path.write_text(json.dumps({"vocab": vocab}), encoding="utf-8")
    pack = ramp_pack()
    write_voice_pack(tmp_path, "af_heart", pack)
    onnx = tmp_path / "model.onnx"
    onnx.write_bytes(b"weights")
    adapter = tts_g2p_seam.adapter(onnx_vocab_path=vocab_path)
    adapter.load_model(_variant("kokoro-onnx-fp32", onnx), DeviceType.CPU)

    session = tts_g2p_seam.session

    def feeds(phonemes: str, speed: float = 1.0) -> list[dict[str, Any]]:
        tts_g2p_seam.set_phonemes(phonemes)
        session.runs = []
        adapter.generate("text", _voice(), speed, lambda _frac: None)
        return list(session.runs)

    # Real phoneme ids reach the model, not pad tokens only (the deleted AC-62.16 intent);
    # the unknown `?` is dropped and the style row is the id count minus one.
    [feed] = feeds("ab?ba", 1.5)
    np.testing.assert_array_equal(feed["input_ids"], np.array([[0, 1, 2, 2, 1, 0]], dtype=np.int64))
    assert feed["input_ids"].dtype == np.int64
    assert feed["style"].dtype == np.float32
    assert feed["style"].shape == (1, 256)
    np.testing.assert_array_equal(feed["style"][0], pack[3])
    assert feed["speed"].dtype == np.float32
    assert feed["speed"].shape == (1,)
    np.testing.assert_allclose(feed["speed"], np.array([1.5], dtype=np.float32))

    [feed] = feeds("??")
    np.testing.assert_array_equal(feed["input_ids"], np.array([[0, 0]], dtype=np.int64))
    np.testing.assert_array_equal(feed["style"][0], pack[0])

    [feed] = feeds("a" * 510)
    assert feed["input_ids"].shape == (1, 512)
    np.testing.assert_array_equal(feed["style"][0], pack[509])

    phonemes = "a" * 300 + ". " + "b" * 300
    chunks = split_phonemes(phonemes)
    assert len(chunks) == 2
    runs = feeds(phonemes)
    assert len(runs) == len(chunks)
    for chunk, run in zip(chunks, runs, strict=True):
        ids = [vocab[symbol] for symbol in chunk if symbol in vocab]
        np.testing.assert_array_equal(run["input_ids"], np.array([[0, *ids, 0]], dtype=np.int64))
        np.testing.assert_array_equal(run["style"][0], pack[min(len(ids), 510) - 1])

    # The 510-id guard stays as a defence behind CHUNK_RULE.
    with pytest.raises(ValidationError):
        adapter._onnx_chunk("a" * 511, _voice(), 1.0, session(onnx))


@pytest.mark.integration
def test_ac_72_5_torch_path_calls_kmodel_per_chunk_without_kpipeline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tts_g2p_seam: G2pSeam,  # noqa: F811
) -> None:
    import torch

    from avkit_infra.tts.g2p import split_phonemes

    calls: list[tuple[str, Any, float]] = []

    class StubKModel:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def to(self, device: object) -> StubKModel:
            return self

        def eval(self) -> StubKModel:
            return self

        def __call__(self, phonemes: str, ref_s: Any, speed: float = 1.0) -> Any:
            calls.append((phonemes, ref_s, speed))
            return torch.full((4,), 0.5)

    stub = types.ModuleType("kokoro")
    stub.KModel = StubKModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "kokoro", stub)
    monkeypatch.delitem(sys.modules, "kokoro.pipeline", raising=False)

    vocab_path = tmp_path / "config.json"
    vocab_path.write_text(json.dumps({"vocab": {"a": 1, "b": 2}}), encoding="utf-8")
    pack = ramp_pack()
    write_voice_pack(tmp_path, "af_heart", pack)
    pt = tmp_path / "pt.pth"
    pt.write_bytes(b"weights")
    adapter = tts_g2p_seam.adapter(onnx_vocab_path=vocab_path)
    adapter.load_model(_variant("kokoro-pt-fp32", pt), DeviceType.CPU)
    phonemes = "a" * 300 + ". " + "b" * 300
    tts_g2p_seam.set_phonemes(phonemes)
    pcm = adapter.generate("text", _voice(), 1.25, lambda _frac: None)

    chunks = split_phonemes(phonemes)
    assert len(chunks) == 2
    assert [call[0] for call in calls] == chunks
    for chunk, (_ps, ref_s, speed) in zip(chunks, calls, strict=True):
        assert tuple(ref_s.shape) == (1, 256)
        np.testing.assert_array_equal(ref_s.cpu().numpy()[0], pack[len(chunk) - 1])
        assert speed == pytest.approx(1.25)
    assert pcm.dtype == np.float32
    assert pcm.size == 8
    assert "kokoro.pipeline" not in sys.modules


@pytest.mark.integration
def test_ac_73_8_onnx_download_pins_revision_and_local_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.model_manager.manager import ModelCatalogAdapter
    from avkit_infra.tts.voices import ONNX_LOCAL_DIR, ONNX_REPO, ONNX_REVISION

    calls: list[dict[str, object]] = []

    def fake_download(**kwargs: Any) -> str:
        # The byte-progress bar (rc.3 F4) is checked on its own; the pins are the rest.
        assert isinstance(kwargs.pop("tqdm_class"), type)
        calls.append(kwargs)
        dest = Path(kwargs["local_dir"]) / kwargs["filename"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"weights")
        return str(dest)

    monkeypatch.setattr("avkit_infra.model_manager.manager.hf_hub_download", fake_download)
    adapter = ModelCatalogAdapter()
    got = adapter.download(_variant("kokoro-onnx-int8"), tmp_path, lambda _frac: None)
    assert calls == [
        {
            "repo_id": ONNX_REPO,
            "filename": "onnx/model_quantized.onnx",
            "revision": ONNX_REVISION,
            "local_dir": str(tmp_path / ONNX_LOCAL_DIR),
        }
    ]
    assert got == tmp_path / ONNX_LOCAL_DIR / "onnx" / "model_quantized.onnx"

    calls.clear()
    adapter.download(_variant("kokoro-pt-fp32"), tmp_path, lambda _frac: None)
    assert calls == [
        {"repo_id": "hexgrad/Kokoro-82M", "filename": "kokoro-v1_0.pth", "local_dir": str(tmp_path)}
    ]


@pytest.mark.integration
def test_ac_98_7_catalog_metadata_matches_seed() -> None:
    # SIDELOAD_RECORD records only ids with a repository row: every id the scan can return
    # must be seeded (Session 42, MEU-98).
    from avkit_infra.database.engine import SEED_VARIANTS
    from avkit_infra.tts.voices import CATALOG_METADATA

    assert set(CATALOG_METADATA) == {variant[0] for variant in SEED_VARIANTS}
