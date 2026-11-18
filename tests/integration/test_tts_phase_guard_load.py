"""MEU-144 the phase guard through `KokoroAdapter.load_model` (Session 74, AC-144.9, AC-144.11).

`BOTH_SESSIONS` (plan §Single-statement contracts): `_load_onnx` calls `guarded_model` once and
hands the same object to the CUDA and the CPU session. AC-144.9 replaces
`avkit_infra.tts.adapter.InferenceSession` with a recording fake, as
`test_tts_device_resolution.py` does; AC-144.11 runs the real ONNX Runtime on the synthetic
model (`tests/tts_onnx_synthetic.py`). Each test asserts that `avkit_infra.tts.phase_guard`
exists before it imports from it or patches it, so at Red each one fails by assertion.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from tests import tts_onnx_synthetic as synthetic

from avkit_core.domain.enums import DeviceType, ModelFormat, ModelPrecision
from avkit_core.domain.tts import ModelVariant

ADAPTER = "avkit_infra.tts.adapter"
MODULE = "avkit_infra.tts.phase_guard"
AUTO, CUDA, CPU = DeviceType.Auto, DeviceType.CUDA, DeviceType.CPU


def _require_module() -> None:
    assert importlib.util.find_spec(MODULE) is not None, f"{MODULE} does not exist yet"


def with_cuda(fmt: ModelFormat) -> tuple[DeviceType, ...]:
    del fmt
    return (AUTO, CUDA, CPU)


def cpu_only(fmt: ModelFormat) -> tuple[DeviceType, ...]:
    del fmt
    return (AUTO, CPU)


class Recorder:
    """A recording `InferenceSession` stand-in; CUDA providers raise unless `cuda_ok`."""

    def __init__(self, *, cuda_ok: bool) -> None:
        self.cuda_ok = cuda_ok
        self.models: list[object] = []
        self.providers: list[tuple[str, ...]] = []

    def session_class(self) -> type:
        recorder = self

        class Session:
            def __init__(self, model: object, providers: object = None, **kwargs: object) -> None:
                key = tuple(providers or ())  # type: ignore[arg-type]
                recorder.models.append(model)
                recorder.providers.append(key)
                if "CUDAExecutionProvider" in key and not recorder.cuda_ok:
                    raise RuntimeError("CUDA provider failed")
                self._providers = list(key)

            def get_providers(self) -> list[str]:
                return list(self._providers)

        return Session


def _adapter(tmp_path: Path, probe: Any) -> Any:
    from avkit_infra.tts.adapter import KokoroAdapter

    return KokoroAdapter(onnx_vocab_path=tmp_path / "config.json", device_probe=probe)


def _variant(tmp_path: Path, variant_id: str, precision: ModelPrecision) -> ModelVariant:
    weights = tmp_path / "private-weights-dir"
    weights.mkdir(exist_ok=True)
    path = weights / f"{variant_id}.onnx"
    path.write_bytes(synthetic.build())
    return ModelVariant(
        id=variant_id,
        name=variant_id,
        format=ModelFormat.ONNX,
        precision=precision,
        size_bytes=synthetic.SOURCE_BYTES,
        path=path,
        is_downloaded=True,
    )


def _wrap_guard(monkeypatch: pytest.MonkeyPatch) -> list[tuple[Path, str]]:
    """Patch the synthetic spec in and count `guarded_model` calls made by the adapter."""
    from avkit_infra.tts import adapter, phase_guard

    monkeypatch.setattr(phase_guard, "KOKORO_FP16", synthetic.spec())
    calls: list[tuple[Path, str]] = []
    real = adapter.guarded_model

    def counted(path: Path, variant_id: str) -> str | bytes:
        calls.append((path, variant_id))
        return real(path, variant_id)

    monkeypatch.setattr(f"{ADAPTER}.guarded_model", counted)
    return calls


# --- AC-144.9 BOTH_SESSIONS ------------------------------------------------------------------


@pytest.mark.integration
def test_ac_144_9_cuda_failure_falls_back_to_cpu_on_the_same_guarded_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import splice

    recorder = Recorder(cuda_ok=False)
    monkeypatch.setattr(f"{ADAPTER}.InferenceSession", recorder.session_class())
    calls = _wrap_guard(monkeypatch)
    adapter = _adapter(tmp_path, with_cuda)
    adapter.load_model(_variant(tmp_path, "kokoro-onnx-fp16", ModelPrecision.FP16), CUDA)
    assert len(recorder.models) == 2
    first, second = recorder.models
    assert isinstance(first, bytes)
    assert first is second
    assert first == splice(synthetic.build())
    assert [p[0] for p in recorder.providers] == ["CUDAExecutionProvider", "CPUExecutionProvider"]
    assert len(calls) == 1
    assert adapter.get_model_status().device == "cpu"


@pytest.mark.integration
def test_ac_144_9_an_accepted_cuda_session_gets_the_guarded_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import splice

    recorder = Recorder(cuda_ok=True)
    monkeypatch.setattr(f"{ADAPTER}.InferenceSession", recorder.session_class())
    calls = _wrap_guard(monkeypatch)
    adapter = _adapter(tmp_path, with_cuda)
    adapter.load_model(_variant(tmp_path, "kokoro-onnx-fp16", ModelPrecision.FP16), CUDA)
    assert len(recorder.models) == 1
    assert isinstance(recorder.models[0], bytes)
    assert recorder.models[0] == splice(synthetic.build())
    assert len(calls) == 1
    assert adapter.get_model_status().device == "cuda"


@pytest.mark.integration
def test_ac_144_9_an_int8_variant_gives_both_sessions_its_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_module()
    recorder = Recorder(cuda_ok=False)
    monkeypatch.setattr(f"{ADAPTER}.InferenceSession", recorder.session_class())
    calls = _wrap_guard(monkeypatch)
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, "kokoro-onnx-int8", ModelPrecision.INT8)
    adapter.load_model(variant, CUDA)
    assert recorder.models == [str(variant.path), str(variant.path)]
    assert len(calls) == 1
    assert adapter.get_model_status().device == "cpu"


# --- AC-144.11 real ONNX Runtime through the adapter -----------------------------------------


def _phase(adapter: Any) -> np.ndarray:
    feed = {"a": np.array([0.0], np.float16), "b": np.array([0.0], np.float16)}
    return adapter._session.run(["y"], feed)[0]


@pytest.mark.integration
def test_ac_144_11_real_ort_through_the_adapter_gives_zero_only_when_guarded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_module()
    from avkit_infra.tts import phase_guard

    shipped = phase_guard.KOKORO_FP16
    variant = _variant(tmp_path, "kokoro-onnx-fp16", ModelPrecision.FP16)

    monkeypatch.setattr(phase_guard, "KOKORO_FP16", synthetic.spec())
    guarded = _adapter(tmp_path, cpu_only)
    guarded.load_model(variant, CPU)
    zero = _phase(guarded)
    assert (zero == 0).all() and not np.signbit(zero).any()

    monkeypatch.setattr(phase_guard, "KOKORO_FP16", shipped)
    plain = _adapter(tmp_path, cpu_only)
    plain.load_model(variant, CPU)
    assert np.isnan(_phase(plain)).all()
