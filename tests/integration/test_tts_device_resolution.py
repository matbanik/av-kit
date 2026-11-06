"""MEU-75 TTS device probe, resolution, load fallback and status contract (Session 35).

`DEVICE_PROBE`, `DEVICE_RESOLVE` and `LOAD_FALLBACK` (plan §Single-statement contracts). Engines
are fakes that record every call; the probe is injected, so no test depends on the host GPU
except AC-75.10, which reads the live runtimes.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest
from structlog.testing import capture_logs

from avkit_core.domain.enums import DeviceType, ModelFormat, ModelPrecision
from avkit_core.domain.errors import ModelLoadError
from avkit_core.domain.tts import ModelStatus, ModelVariant, VoiceConfig

ADAPTER = "avkit_infra.tts.adapter"
AUTO, CUDA, CPU, MPS = DeviceType.Auto, DeviceType.CUDA, DeviceType.CPU, DeviceType.MPS
CUDA_PROVIDERS = ("CUDAExecutionProvider", "CPUExecutionProvider")
CPU_PROVIDERS = ("CPUExecutionProvider",)
VOICE = VoiceConfig("af_heart", "a", "American English", "Female", "heart")


def cpu_only(fmt: ModelFormat) -> tuple[DeviceType, ...]:
    del fmt
    return (AUTO, CPU)


def with_cuda(fmt: ModelFormat) -> tuple[DeviceType, ...]:
    del fmt
    return (AUTO, CUDA, CPU)


def _fake_torch(*, cuda: bool, mps: bool | None, backends: bool = True) -> SimpleNamespace:
    """A torch stand-in: `mps=None` gives a `backends` without `mps`; `backends=False` none."""
    fake = SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: cuda))
    if backends:
        fake.backends = (
            SimpleNamespace()
            if mps is None
            else SimpleNamespace(mps=SimpleNamespace(is_available=lambda: mps))
        )
    return fake


class Engines:
    """Configurable `KModel` and `InferenceSession` fakes sharing one call log."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, ...]] = []
        self.kmodel_init_error: BaseException | None = None
        self.to_errors: dict[str, BaseException] = {}
        self.eval_error: BaseException | None = None
        self.session_errors: dict[tuple[str, ...], BaseException] = {}
        #: What `get_providers()` reports; `None` echoes the providers the session was built with.
        self.session_providers: list[str] | None = None
        self.get_providers_error: BaseException | None = None

    def kmodel_class(self) -> type:
        engines = self

        class KModel:
            def __init__(self, *args: object, **kwargs: object) -> None:
                engines.calls.append(("KModel",))
                if engines.kmodel_init_error is not None:
                    raise engines.kmodel_init_error

            def to(self, device: object) -> KModel:
                engines.calls.append(("to", str(device)))
                error = engines.to_errors.get(str(device))
                if error is not None:
                    raise error
                return self

            def eval(self) -> KModel:
                engines.calls.append(("eval",))
                if engines.eval_error is not None:
                    raise engines.eval_error
                return self

        return KModel

    def session_class(self) -> type:
        engines = self

        class Session:
            def __init__(self, path: object, providers: object = None, **kwargs: object) -> None:
                key = tuple(providers or ())  # type: ignore[arg-type]
                engines.calls.append(("session", key))
                error = engines.session_errors.get(key)
                if error is not None:
                    raise error
                self._providers = list(key)

            def get_providers(self) -> list[str]:
                engines.calls.append(("get_providers",))
                if engines.get_providers_error is not None:
                    raise engines.get_providers_error
                if engines.session_providers is not None:
                    return list(engines.session_providers)
                return list(self._providers)

            def run(self, _outputs: object, feed: dict[str, Any]) -> list[np.ndarray]:
                return [np.zeros((1, 2), dtype=np.float32)]

        return Session


@pytest.fixture
def engines(monkeypatch: pytest.MonkeyPatch) -> Engines:
    fakes = Engines()
    kokoro_stub = types.ModuleType("kokoro")
    kokoro_stub.KModel = fakes.kmodel_class()  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "kokoro", kokoro_stub)
    monkeypatch.setattr(f"{ADAPTER}.InferenceSession", fakes.session_class())
    # The probe is injected; torch only has to be present for the PyTorch path.
    monkeypatch.setattr(f"{ADAPTER}.torch", _fake_torch(cuda=False, mps=False))
    return fakes


def _adapter(tmp_path: Path, probe: Any) -> Any:
    from avkit_infra.tts.adapter import KokoroAdapter

    return KokoroAdapter(onnx_vocab_path=tmp_path / "config.json", device_probe=probe)


def _variant(tmp_path: Path, fmt: ModelFormat) -> ModelVariant:
    weights = tmp_path / "private-weights-dir"
    weights.mkdir(exist_ok=True)
    if fmt is ModelFormat.PyTorch:
        variant_id, name, path = "kokoro-pt-fp32", "PyTorch FP32", weights / "kokoro-v1_0.pth"
    else:
        variant_id, name, path = "kokoro-onnx-fp32", "ONNX FP32", weights / "model.onnx"
    path.write_bytes(b"weights")
    return ModelVariant(
        id=variant_id,
        name=name,
        format=fmt,
        precision=ModelPrecision.FP32,
        size_bytes=7,
        path=path,
        is_downloaded=True,
    )


def _events(logs: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    return [entry for entry in logs if entry["event"] == name]


def _load_cuda_first(adapter: Any, variant: ModelVariant, engines: Engines) -> None:
    """Every failure case starts from a successful CUDA load (round 1 Q2)."""
    adapter.load_model(variant, CUDA)
    status = adapter.get_model_status()
    assert (status.is_loaded, status.device) == (True, "cuda")
    engines.calls.clear()


def _assert_unloaded(adapter: Any) -> None:
    status: ModelStatus = adapter.get_model_status()
    assert (status.is_loaded, status.variant_id, status.device) == (False, None, "cpu")
    assert adapter._variant is None
    assert adapter._kmodel is None
    assert adapter._session is None
    assert adapter._device_name == "cpu"
    with pytest.raises(ModelLoadError):
        adapter.generate("Hello.", VOICE, 1.0, lambda _fraction: None)


def _assert_no_path(error: ModelLoadError, variant: ModelVariant) -> None:
    assert variant.path is not None
    message = str(error)
    for part in (str(variant.path), variant.path.name, variant.path.parent.name):
        assert part not in message, message


# --- AC-75.1 / AC-75.2 DEVICE_PROBE ---------------------------------------------------------


@pytest.mark.integration
def test_ac_75_1_pytorch_probe_matrix(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.tts.adapter import runtime_devices

    matrix = (
        (_fake_torch(cuda=False, mps=None), (AUTO, CPU)),
        (_fake_torch(cuda=False, mps=False), (AUTO, CPU)),
        (_fake_torch(cuda=True, mps=False), (AUTO, CUDA, CPU)),
        (_fake_torch(cuda=False, mps=True), (AUTO, CPU, MPS)),
        (_fake_torch(cuda=True, mps=True), (AUTO, CUDA, CPU, MPS)),
        (_fake_torch(cuda=True, mps=None), (AUTO, CUDA, CPU)),
        (_fake_torch(cuda=False, mps=None, backends=False), (AUTO, CPU)),
    )
    for fake, expected in matrix:
        monkeypatch.setattr(f"{ADAPTER}.torch", fake)
        devices = runtime_devices(ModelFormat.PyTorch)
        assert devices == expected, fake
        if not fake.cuda.is_available():
            assert CUDA not in devices, fake
    monkeypatch.setattr(f"{ADAPTER}.torch", None)
    assert runtime_devices(ModelFormat.PyTorch) == (AUTO, CPU)


@pytest.mark.integration
def test_ac_75_2_onnx_probe_reads_available_providers(monkeypatch: pytest.MonkeyPatch) -> None:
    from avkit_infra.tts.adapter import runtime_devices

    # MPS is never an ONNX device, even when torch says MPS is there.
    monkeypatch.setattr(f"{ADAPTER}.torch", _fake_torch(cuda=True, mps=True))
    cases = (
        (["CPUExecutionProvider"], (AUTO, CPU)),
        (["CUDAExecutionProvider", "CPUExecutionProvider"], (AUTO, CUDA, CPU)),
        (["TensorrtExecutionProvider", "CPUExecutionProvider"], (AUTO, CPU)),
    )
    for providers, expected in cases:
        monkeypatch.setattr(f"{ADAPTER}.get_available_providers", lambda p=providers: list(p))
        devices = runtime_devices(ModelFormat.ONNX)
        assert devices == expected, providers
        assert MPS not in devices, providers


# --- AC-75.3 / AC-75.6 DEVICE_RESOLVE -------------------------------------------------------


@pytest.mark.integration
def test_ac_75_3_unavailable_device_loads_on_cpu_with_one_warning(
    tmp_path: Path, engines: Engines
) -> None:
    adapter = _adapter(tmp_path, cpu_only)
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    for requested, wire in ((CUDA, "cuda"), (MPS, "mps")):
        engines.calls.clear()
        with capture_logs() as logs:
            adapter.load_model(variant, requested)
        status = adapter.get_model_status()
        assert (status.is_loaded, status.device) == (True, "cpu"), wire
        assert engines.calls == [("KModel",), ("to", "cpu"), ("eval",)], wire
        fallback = _events(logs, "tts.device_fallback")
        assert len(fallback) == 1, logs
        assert fallback[0]["log_level"] == "warning"
        assert fallback[0]["variant_id"] == variant.id
        assert (fallback[0]["requested"], fallback[0]["actual"], fallback[0]["reason"]) == (
            wire,
            "cpu",
            "unavailable",
        )


@pytest.mark.integration
def test_ac_75_3_available_or_cpu_request_logs_no_fallback_neg(
    tmp_path: Path, engines: Engines
) -> None:
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    cpu_adapter = _adapter(tmp_path, cpu_only)
    with capture_logs() as logs:
        cpu_adapter.load_model(variant, CPU)
    assert cpu_adapter.get_model_status().device == "cpu"
    assert _events(logs, "tts.device_fallback") == []

    cuda_adapter = _adapter(tmp_path, with_cuda)
    engines.calls.clear()
    with capture_logs() as logs:
        cuda_adapter.load_model(variant, CUDA)
    assert cuda_adapter.get_model_status().device == "cuda"
    assert engines.calls == [("KModel",), ("to", "cuda"), ("eval",)]
    assert _events(logs, "tts.device_fallback") == []


@pytest.mark.integration
def test_ac_75_6_auto_prefers_cuda_then_mps_then_cpu(tmp_path: Path, engines: Engines) -> None:
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    cases = (
        ((AUTO, CUDA, CPU, MPS), "cuda"),
        ((AUTO, CPU, MPS), "mps"),
        ((AUTO, CPU), "cpu"),
    )
    for probe, expected in cases:
        adapter = _adapter(tmp_path, lambda fmt, p=probe: p)
        engines.calls.clear()
        with capture_logs() as logs:
            adapter.load_model(variant, AUTO)
        assert adapter.get_model_status().device == expected, probe
        # Auto on a CPU-only probe never tries the GPU.
        assert [call for call in engines.calls if call[0] == "to"] == [("to", expected)], probe
        assert _events(logs, "tts.device_fallback") == [], probe


@pytest.mark.integration
def test_ac_75_6_onnx_auto_on_cpu_probe_builds_one_cpu_session(
    tmp_path: Path, engines: Engines
) -> None:
    adapter = _adapter(tmp_path, cpu_only)
    with capture_logs() as logs:
        adapter.load_model(_variant(tmp_path, ModelFormat.ONNX), AUTO)
    assert adapter.get_model_status().device == "cpu"
    assert engines.calls == [("session", CPU_PROVIDERS)]
    assert _events(logs, "tts.device_fallback") == []


# --- AC-75.4 PyTorch LOAD_FALLBACK ----------------------------------------------------------


@pytest.mark.integration
def test_ac_75_4_pytorch_to_failure_retries_once_on_cpu(tmp_path: Path, engines: Engines) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    _load_cuda_first(adapter, variant, engines)
    engines.to_errors["cuda"] = AssertionError("Torch not compiled with CUDA enabled")
    with capture_logs() as logs:
        adapter.load_model(variant, CUDA)
    status = adapter.get_model_status()
    assert (status.is_loaded, status.device) == (True, "cpu")
    assert engines.calls == [("KModel",), ("to", "cuda"), ("to", "cpu"), ("eval",)]
    fallback = _events(logs, "tts.device_fallback")
    assert len(fallback) == 1, logs
    assert (fallback[0]["requested"], fallback[0]["actual"], fallback[0]["reason"]) == (
        "cuda",
        "cpu",
        "load_failed",
    )
    assert _events(logs, "tts.load_failed") == []


@pytest.mark.integration
def test_ac_75_4_pytorch_cpu_retry_failure_raises_model_load_error(
    tmp_path: Path, engines: Engines
) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    _load_cuda_first(adapter, variant, engines)
    cpu_error = RuntimeError("cpu move failed")
    engines.to_errors.update(
        cuda=AssertionError("Torch not compiled with CUDA enabled"), cpu=cpu_error
    )
    with capture_logs() as logs, pytest.raises(ModelLoadError) as err:
        adapter.load_model(variant, CUDA)
    assert err.value.__cause__ is cpu_error
    assert str(err.value) == "PyTorch model failed to load"
    _assert_no_path(err.value, variant)
    failed = _events(logs, "tts.load_failed")
    assert len(failed) == 1, logs
    assert failed[0]["log_level"] == "error"
    assert (failed[0]["variant_id"], failed[0]["device"], failed[0]["error"]) == (
        variant.id,
        "cpu",
        "RuntimeError",
    )
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_75_4_pytorch_constructor_failure_is_wrapped_and_not_retried(
    tmp_path: Path, engines: Engines
) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    _load_cuda_first(adapter, variant, engines)
    init_error = ValueError("bad weights")
    engines.kmodel_init_error = init_error
    with capture_logs() as logs, pytest.raises(ModelLoadError) as err:
        adapter.load_model(variant, CUDA)
    assert err.value.__cause__ is init_error
    assert engines.calls == [("KModel",)]
    _assert_no_path(err.value, variant)
    failed = _events(logs, "tts.load_failed")
    assert len(failed) == 1, logs
    assert failed[0]["error"] == "ValueError"
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_75_4_pytorch_eval_failure_is_final(tmp_path: Path, engines: Engines) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    _load_cuda_first(adapter, variant, engines)
    eval_error = RuntimeError("eval failed")
    engines.eval_error = eval_error
    with capture_logs() as logs, pytest.raises(ModelLoadError) as err:
        adapter.load_model(variant, CUDA)
    assert err.value.__cause__ is eval_error
    assert engines.calls == [("KModel",), ("to", "cuda"), ("eval",)]
    _assert_no_path(err.value, variant)
    failed = _events(logs, "tts.load_failed")
    assert len(failed) == 1, logs
    assert (failed[0]["device"], failed[0]["error"]) == ("cuda", "RuntimeError")
    _assert_unloaded(adapter)


# --- AC-75.5 ONNX LOAD_FALLBACK -------------------------------------------------------------


@pytest.mark.integration
def test_ac_75_5_onnx_cuda_session_without_cuda_provider_reports_cpu(
    tmp_path: Path, engines: Engines
) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.ONNX)
    _load_cuda_first(adapter, variant, engines)
    engines.session_providers = ["CPUExecutionProvider"]
    with capture_logs() as logs:
        adapter.load_model(variant, CUDA)
    status = adapter.get_model_status()
    assert (status.is_loaded, status.device) == (True, "cpu")
    assert engines.calls == [("session", CUDA_PROVIDERS), ("get_providers",)]
    fallback = _events(logs, "tts.device_fallback")
    assert len(fallback) == 1, logs
    assert (fallback[0]["requested"], fallback[0]["actual"], fallback[0]["reason"]) == (
        "cuda",
        "cpu",
        "provider_fallback",
    )


@pytest.mark.integration
def test_ac_75_5_onnx_cuda_constructor_failure_retries_on_cpu(
    tmp_path: Path, engines: Engines
) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.ONNX)
    _load_cuda_first(adapter, variant, engines)
    engines.session_errors[CUDA_PROVIDERS] = RuntimeError("CUDA session failed")
    with capture_logs() as logs:
        adapter.load_model(variant, CUDA)
    status = adapter.get_model_status()
    assert (status.is_loaded, status.device) == (True, "cpu")
    # The CPU session is trusted as built: get_providers is never called on it.
    assert engines.calls == [("session", CUDA_PROVIDERS), ("session", CPU_PROVIDERS)]
    fallback = _events(logs, "tts.device_fallback")
    assert len(fallback) == 1, logs
    assert (fallback[0]["requested"], fallback[0]["actual"], fallback[0]["reason"]) == (
        "cuda",
        "cpu",
        "load_failed",
    )


@pytest.mark.integration
def test_ac_75_5_onnx_unreadable_providers_retries_on_cpu(tmp_path: Path, engines: Engines) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.ONNX)
    _load_cuda_first(adapter, variant, engines)
    engines.get_providers_error = RuntimeError("providers unreadable")
    with capture_logs() as logs:
        adapter.load_model(variant, CUDA)
    status = adapter.get_model_status()
    assert (status.is_loaded, status.device) == (True, "cpu")
    assert engines.calls == [
        ("session", CUDA_PROVIDERS),
        ("get_providers",),
        ("session", CPU_PROVIDERS),
    ]
    fallback = _events(logs, "tts.device_fallback")
    assert len(fallback) == 1, logs
    assert fallback[0]["reason"] == "load_failed"


@pytest.mark.integration
def test_ac_75_5_onnx_cpu_failure_raises_model_load_error(tmp_path: Path, engines: Engines) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.ONNX)
    for requested in (CPU, CUDA):
        _load_cuda_first(adapter, variant, engines)
        cpu_error = RuntimeError("CPU session failed")
        engines.session_errors = {
            CUDA_PROVIDERS: RuntimeError("CUDA session failed"),
            CPU_PROVIDERS: cpu_error,
        }
        with capture_logs() as logs, pytest.raises(ModelLoadError) as err:
            adapter.load_model(variant, requested)
        assert err.value.__cause__ is cpu_error, requested
        assert str(err.value) == "ONNX session failed"
        _assert_no_path(err.value, variant)
        failed = _events(logs, "tts.load_failed")
        assert len(failed) == 1, logs
        assert (failed[0]["device"], failed[0]["error"]) == ("cpu", "RuntimeError")
        _assert_unloaded(adapter)
        engines.session_errors = {}


@pytest.mark.integration
def test_ac_75_5_cpu_only_loads_never_read_providers(tmp_path: Path, engines: Engines) -> None:
    variant = _variant(tmp_path, ModelFormat.ONNX)
    for probe, requested in ((cpu_only, CUDA), (cpu_only, AUTO), (with_cuda, CPU)):
        adapter = _adapter(tmp_path, probe)
        engines.calls.clear()
        adapter.load_model(variant, requested)
        assert adapter.get_model_status().device == "cpu", requested
        assert engines.calls == [("session", CPU_PROVIDERS)], requested


# --- AC-75.7 port (adapter half; the service half is in tests/unit/test_services.py) --------


@pytest.mark.integration
def test_ac_75_7_adapter_available_devices_returns_the_probe(tmp_path: Path) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter, runtime_devices

    seen: list[ModelFormat] = []

    def probe(fmt: ModelFormat) -> tuple[DeviceType, ...]:
        seen.append(fmt)
        return (AUTO, CUDA, CPU)

    adapter = _adapter(tmp_path, probe)
    assert adapter.available_devices(ModelFormat.ONNX) == (AUTO, CUDA, CPU)
    assert seen == [ModelFormat.ONNX]
    default = KokoroAdapter(onnx_vocab_path=tmp_path / "config.json")
    assert default.available_devices(ModelFormat.PyTorch) == runtime_devices(ModelFormat.PyTorch)


# --- AC-75.9 status contract (the map and envelope are in tests/e2e/test_api_error_surface.py)


@pytest.mark.integration
def test_ac_75_9_load_route_reports_the_actual_device(tmp_path: Path, engines: Engines) -> None:
    from tests.e2e.api_fakes import AUTH, FakeModels, make_client

    adapter = _adapter(tmp_path, cpu_only)
    variant = _variant(tmp_path, ModelFormat.ONNX)

    class AdapterModels(FakeModels):
        def load(self, variant_id: str, device: object) -> None:
            assert variant_id == variant.id
            adapter.load_model(variant, device)

        def get_status(self) -> ModelStatus:
            return adapter.get_model_status()

    client, _trx, _tts, _models = make_client(models=AdapterModels())
    loaded = client.post(
        "/api/v1/models/load", headers=AUTH, json={"variant_id": variant.id, "device": "cuda"}
    )
    assert loaded.status_code == 200, loaded.text
    assert (loaded.json()["is_loaded"], loaded.json()["device"]) == (True, "cpu")
    status = client.get("/api/v1/models/status", headers=AUTH)
    assert status.status_code == 200, status.text
    assert (status.json()["is_loaded"], status.json()["device"]) == (True, "cpu")


# --- AC-75.9 a failing runtime query (execution review R1 F1) -------------------------------


def _raise_runtime(*_args: object) -> Any:
    raise RuntimeError("provider enumeration failed")


def _torch_raising(*, cuda: bool, mps: bool) -> SimpleNamespace:
    """A torch stand-in whose CUDA (`cuda=True`) and/or MPS (`mps=True`) query raises."""
    return SimpleNamespace(
        cuda=SimpleNamespace(is_available=_raise_runtime if cuda else lambda: True),
        backends=SimpleNamespace(
            mps=SimpleNamespace(is_available=_raise_runtime if mps else lambda: True)
        ),
    )


@pytest.mark.integration
def test_ac_75_9_failing_runtime_query_lists_no_such_device_neg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from avkit_infra.tts.adapter import runtime_devices

    monkeypatch.setattr(f"{ADAPTER}.get_available_providers", _raise_runtime)
    cases = (
        (ModelFormat.ONNX, None, (AUTO, CPU), ["cuda"]),
        (ModelFormat.PyTorch, _torch_raising(cuda=True, mps=False), (AUTO, CPU, MPS), ["cuda"]),
        (ModelFormat.PyTorch, _torch_raising(cuda=False, mps=True), (AUTO, CUDA, CPU), ["mps"]),
        (ModelFormat.PyTorch, _torch_raising(cuda=True, mps=True), (AUTO, CPU), ["cuda", "mps"]),
    )
    for fmt, fake, expected, failed in cases:
        if fake is not None:
            monkeypatch.setattr(f"{ADAPTER}.torch", fake)
        with capture_logs() as logs:
            assert runtime_devices(fmt) == expected, (fmt, failed)
        probe_failed = _events(logs, "tts.device_probe_failed")
        assert [entry["device"] for entry in probe_failed] == failed, logs
        for entry in probe_failed:
            assert entry["log_level"] == "warning"
            assert (entry["format"], entry["error"]) == (fmt.value, "RuntimeError")


@pytest.mark.integration
def test_ac_75_9_failing_runtime_query_still_loads_on_cpu(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path, None)  # the default probe, `runtime_devices`
    onnx = _variant(tmp_path, ModelFormat.ONNX)
    monkeypatch.setattr(f"{ADAPTER}.get_available_providers", lambda: list(CUDA_PROVIDERS))
    _load_cuda_first(adapter, onnx, engines)
    monkeypatch.setattr(f"{ADAPTER}.get_available_providers", _raise_runtime)
    for requested, reasons in ((CPU, []), (CUDA, ["unavailable"]), (AUTO, [])):
        engines.calls.clear()
        with capture_logs() as logs:
            adapter.load_model(onnx, requested)
        status = adapter.get_model_status()
        assert (status.is_loaded, status.device) == (True, "cpu"), requested
        assert engines.calls == [("session", CPU_PROVIDERS)], requested
        fallback = _events(logs, "tts.device_fallback")
        assert [entry["reason"] for entry in fallback] == reasons, logs
        assert _events(logs, "tts.load_failed") == []
    monkeypatch.setattr(f"{ADAPTER}.torch", _torch_raising(cuda=True, mps=True))
    engines.calls.clear()
    with capture_logs() as logs:
        adapter.load_model(_variant(tmp_path, ModelFormat.PyTorch), CUDA)
    assert adapter.get_model_status().device == "cpu"
    assert engines.calls == [("KModel",), ("to", "cpu"), ("eval",)]
    assert [entry["reason"] for entry in _events(logs, "tts.device_fallback")] == ["unavailable"]


@pytest.mark.integration
def test_ac_75_9_raising_probe_or_vocab_is_model_load_error_neg(
    tmp_path: Path, engines: Engines
) -> None:
    from avkit_infra.tts.adapter import KokoroAdapter

    failing_probe = RuntimeError("probe failed")

    def probe(fmt: ModelFormat) -> tuple[DeviceType, ...]:
        if probe.fail:  # type: ignore[attr-defined]
            raise failing_probe
        return (AUTO, CUDA, CPU)

    probe.fail = False  # type: ignore[attr-defined]
    adapter = _adapter(tmp_path, probe)
    onnx = _variant(tmp_path, ModelFormat.ONNX)
    _load_cuda_first(adapter, onnx, engines)
    probe.fail = True  # type: ignore[attr-defined]
    with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
        adapter.load_model(onnx, CPU)
    assert raised.value.__cause__ is failing_probe
    assert len(_events(logs, "tts.load_failed")) == 1, logs
    assert engines.calls == []
    _assert_no_path(raised.value, onnx)
    _assert_unloaded(adapter)

    failing_vocab = OSError("settings unreadable")

    def vocab() -> Path:
        raise failing_vocab

    torch_adapter = KokoroAdapter(vocab_path=vocab, device_probe=cpu_only)
    pytorch = _variant(tmp_path, ModelFormat.PyTorch)
    with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
        torch_adapter.load_model(pytorch, CPU)
    assert raised.value.__cause__ is failing_vocab
    assert len(_events(logs, "tts.load_failed")) == 1, logs
    _assert_no_path(raised.value, pytorch)
    _assert_unloaded(torch_adapter)


@pytest.mark.integration
def test_ac_75_9_unreadable_weight_file_is_model_load_error_neg(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path, cpu_only)
    variant = _variant(tmp_path, ModelFormat.ONNX)
    denied = PermissionError("access denied")
    real_is_file = Path.is_file

    def is_file(self: Path) -> bool:
        if self == variant.path:
            raise denied
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", is_file)
    with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
        adapter.load_model(variant, CPU)
    assert raised.value.__cause__ is denied
    # TA-1 (Session 42, MEU-98): the unreadable file logs one `tts.load_failed`.
    failed = _events(logs, "tts.load_failed")
    assert [(e["variant_id"], e["device"], e["error"]) for e in failed] == [
        (variant.id, "cpu", "PermissionError")
    ], logs
    assert engines.calls == []
    _assert_no_path(raised.value, variant)
    monkeypatch.setattr(Path, "is_file", real_is_file)
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_75_9_failing_runtime_query_http_catalog_and_load(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.e2e.api_fakes import AUTH, FakeModels, make_client

    adapter = _adapter(tmp_path, None)
    variant = _variant(tmp_path, ModelFormat.ONNX)
    monkeypatch.setattr(f"{ADAPTER}.get_available_providers", _raise_runtime)

    class AdapterModels(FakeModels):
        def available_devices(self, fmt: ModelFormat) -> tuple[DeviceType, ...]:
            return adapter.available_devices(fmt)

        def load(self, variant_id: str, device: object) -> None:
            assert variant_id == variant.id
            adapter.load_model(variant, device)

        def get_status(self) -> ModelStatus:
            return adapter.get_model_status()

    models = AdapterModels()
    models.variant = variant
    client, _trx, _tts, _models = make_client(models=models)
    available = client.get("/api/v1/models/available", headers=AUTH)
    assert available.status_code == 200, available.text
    assert [item["devices"] for item in available.json()["items"]] == [["auto", "cpu"]]
    for wire in ("cpu", "cuda"):
        loaded = client.post(
            "/api/v1/models/load", headers=AUTH, json={"variant_id": variant.id, "device": wire}
        )
        assert loaded.status_code == 200, loaded.text
        assert (loaded.json()["is_loaded"], loaded.json()["device"]) == (True, "cpu"), wire
    status = client.get("/api/v1/models/status", headers=AUTH)
    assert status.status_code == 200, status.text
    assert (status.json()["is_loaded"], status.json()["device"]) == (True, "cpu")


def _kokoro_failing_import(error: BaseException) -> types.ModuleType:
    """A `kokoro` whose `KModel` import raises `error`, as a dependency that fails to initialize."""
    module = types.ModuleType("kokoro")

    def __getattr__(name: str) -> Any:
        raise error

    module.__getattr__ = __getattr__  # type: ignore[attr-defined]
    return module


@pytest.mark.integration
def test_ac_75_9_engine_import_failure_is_model_load_error_neg(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    from tests.e2e.api_fakes import AUTH, FakeModels, make_client

    adapter = _adapter(tmp_path, with_cuda)
    _load_cuda_first(adapter, _variant(tmp_path, ModelFormat.ONNX), engines)
    pytorch = _variant(tmp_path, ModelFormat.PyTorch)
    for error in (OSError("engine dependency DLL initialization failed"), RuntimeError("init")):
        monkeypatch.setitem(sys.modules, "kokoro", _kokoro_failing_import(error))
        with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
            adapter.load_model(pytorch, CPU)
        assert raised.value.__cause__ is error
        assert str(raised.value) == "PyTorch model failed to load"
        assert len(_events(logs, "tts.load_failed")) == 1, logs
        assert engines.calls == []
        _assert_no_path(raised.value, pytorch)
        _assert_unloaded(adapter)

    class AdapterModels(FakeModels):
        def load(self, variant_id: str, device: object) -> None:
            assert variant_id == pytorch.id
            adapter.load_model(pytorch, device)

        def get_status(self) -> ModelStatus:
            return adapter.get_model_status()

    models = AdapterModels()
    models.variant = pytorch
    client, _trx, _tts, _models = make_client(models=models)
    loaded = client.post(
        "/api/v1/models/load", headers=AUTH, json={"variant_id": pytorch.id, "device": "cpu"}
    )
    assert loaded.status_code == 422, loaded.text
    assert loaded.json()["error"]["code"] == "ModelLoadError"
    assert loaded.json()["error"]["message"] == "PyTorch model failed to load"


# --- AC-75.10 the real probe ----------------------------------------------------------------


@pytest.mark.integration
def test_ac_75_10_real_probe_agrees_with_installed_runtimes() -> None:
    import onnxruntime

    from avkit_infra.tts import adapter as adapter_mod
    from avkit_infra.tts.adapter import runtime_devices

    torch = adapter_mod.torch
    pytorch = runtime_devices(ModelFormat.PyTorch)
    torch_cuda = torch is not None and bool(torch.cuda.is_available())
    mps = getattr(getattr(torch, "backends", None), "mps", None)
    torch_mps = mps is not None and bool(mps.is_available())
    assert pytorch[0] is AUTO and CPU in pytorch
    assert (CUDA in pytorch) is torch_cuda
    assert (MPS in pytorch) is torch_mps
    onnx = runtime_devices(ModelFormat.ONNX)
    assert onnx[0] is AUTO and CPU in onnx
    assert (CUDA in onnx) is ("CUDAExecutionProvider" in onnxruntime.get_available_providers())
    assert MPS not in onnx


# --- AC-98.4 / 98.5 LOAD_FAILURE_PATHS, LOG_CAUSE (Session 42, MEU-98) ------------------------


def _load_failed(logs: list[dict[str, Any]]) -> list[tuple[str, str, str]]:
    return [
        (entry["variant_id"], entry["device"], entry["error"])
        for entry in _events(logs, "tts.load_failed")
    ]


@pytest.mark.integration
@pytest.mark.parametrize("missing", ["path_none", "no_file"])
def test_ac_98_4_missing_weight_logs_load_failed(
    tmp_path: Path, engines: Engines, missing: str
) -> None:
    import dataclasses

    adapter = _adapter(tmp_path, with_cuda)
    onnx = _variant(tmp_path, ModelFormat.ONNX)
    path = None if missing == "path_none" else tmp_path / "gone" / "model.onnx"
    variant = dataclasses.replace(onnx, path=path)
    with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
        adapter.load_model(variant, CUDA)
    assert str(raised.value) == "model weight file is missing"
    assert isinstance(raised.value.__cause__, FileNotFoundError)
    assert _load_failed(logs) == [(variant.id, "cpu", "FileNotFoundError")], logs
    assert engines.calls == []
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_98_5_torch_absent_logs(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    pytorch = _variant(tmp_path, ModelFormat.PyTorch)
    monkeypatch.setattr(f"{ADAPTER}.torch", None)
    with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
        adapter.load_model(pytorch, CUDA)
    assert str(raised.value) == "PyTorch runtime is not bundled"
    # The resolved target device, as the other `_load_pytorch` failures log it.
    assert _load_failed(logs) == [(pytorch.id, "cuda", "ModelLoadError")], logs
    assert engines.calls == []
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_98_5_kokoro_import_logs(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter = _adapter(tmp_path, with_cuda)
    pytorch = _variant(tmp_path, ModelFormat.PyTorch)
    missing = ImportError("No module named 'kokoro'")
    monkeypatch.setitem(sys.modules, "kokoro", _kokoro_failing_import(missing))
    with capture_logs() as logs, pytest.raises(ModelLoadError) as raised:
        adapter.load_model(pytorch, CUDA)
    assert str(raised.value) == "PyTorch runtime is not bundled"
    assert raised.value.__cause__ is missing
    assert _load_failed(logs) == [(pytorch.id, "cuda", "ImportError")], logs
    assert engines.calls == []
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_98_5_unsupported_format_logs(tmp_path: Path, engines: Engines) -> None:
    from avkit_core.domain.errors import ValidationError

    adapter = _adapter(tmp_path, lambda fmt: frozenset())
    variant = _variant(tmp_path, ModelFormat.ONNX)
    # No constructible variant reaches this defensive branch (`__post_init__` validates
    # `format`), so the field is forced on this one frozen instance.
    object.__setattr__(variant, "format", "TFLite")
    with capture_logs() as logs, pytest.raises(ValidationError, match="unsupported model format"):
        adapter.load_model(variant, CPU)
    assert _load_failed(logs) == [(variant.id, "cpu", "ValidationError")], logs
    assert engines.calls == []
    _assert_unloaded(adapter)


@pytest.mark.integration
def test_ac_98_5_success_logs_none(tmp_path: Path, engines: Engines) -> None:
    adapter = _adapter(tmp_path, cpu_only)
    for fmt in (ModelFormat.ONNX, ModelFormat.PyTorch):
        with capture_logs() as logs:
            adapter.load_model(_variant(tmp_path, fmt), CPU)
        assert adapter.get_model_status().is_loaded, fmt
        assert _events(logs, "tts.load_failed") == [], logs


# --- AC-115.9 the load failure's detail ------------------------------------------------------


@pytest.mark.integration
def test_ac_115_9_load_failed_carries_detail(
    tmp_path: Path, engines: Engines, monkeypatch: pytest.MonkeyPatch
) -> None:
    def details(logs: list[dict[str, Any]]) -> list[tuple[str, str, str, str | None]]:
        return [
            (entry["variant_id"], entry["device"], entry["error"], entry.get("detail"))
            for entry in _events(logs, "tts.load_failed")
        ]

    adapter = _adapter(tmp_path, with_cuda)
    variant = _variant(tmp_path, ModelFormat.PyTorch)
    _load_cuda_first(adapter, variant, engines)
    engines.to_errors.update(
        cuda=AssertionError("Torch not compiled with CUDA enabled"),
        cpu=RuntimeError("cpu move failed\nsecond line"),
    )
    with capture_logs() as logs, pytest.raises(ModelLoadError):
        adapter.load_model(variant, CUDA)
    assert details(logs) == [(variant.id, "cpu", "RuntimeError", "cpu move failed")], logs

    engines.to_errors.clear()
    empty = _adapter(tmp_path, with_cuda)
    _load_cuda_first(empty, variant, engines)
    engines.eval_error = RuntimeError("")
    with capture_logs() as logs, pytest.raises(ModelLoadError):
        empty.load_model(variant, CUDA)
    flags = [("detail" in entry, entry["error"]) for entry in _events(logs, "tts.load_failed")]
    assert flags == [(False, "RuntimeError")], logs

    absent = _adapter(tmp_path, with_cuda)
    monkeypatch.setattr(f"{ADAPTER}.torch", None)
    with capture_logs() as logs, pytest.raises(ModelLoadError):
        absent.load_model(variant, CUDA)
    assert details(logs) == [
        (variant.id, "cuda", "ModelLoadError", "PyTorch runtime is not bundled")
    ], logs
