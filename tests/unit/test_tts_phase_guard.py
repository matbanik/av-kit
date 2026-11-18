"""MEU-144 ONNX FP16 phase guard: the splice and `guarded_model` (Session 74, AC-144.1 to 144.8).

`GUARD_IN_MEMORY`, `GUARD_GATE`, `GUARD_REFUSE`, `GUARD_APPLIED` and `NO_FILE_WRITE` (plan
§Single-statement contracts). Every test runs on the synthetic model in
`tests/tts_onnx_synthetic.py`; none reads a real model file. Each test asserts that
`avkit_infra.tts.phase_guard` exists before it imports anything from it, so at Red each one
fails by assertion, not by a missing module.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from structlog.testing import capture_logs
from tests import tts_onnx_synthetic as synthetic

MODULE = "avkit_infra.tts.phase_guard"
FP16_ID = "kokoro-onnx-fp16"
INT8_ID = "kokoro-onnx-int8"
DIV = synthetic.G + "Div"


def _require_module() -> None:
    assert importlib.util.find_spec(MODULE) is not None, f"{MODULE} does not exist yet"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _guard_events(logs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry for entry in logs if entry["event"] == "tts.phase_guard"]


def _run(model: bytes, a: float, b: float) -> np.ndarray:
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.log_severity_level = 3
    session = ort.InferenceSession(model, options, providers=["CPUExecutionProvider"])
    feed = {"a": np.array([a], np.float16), "b": np.array([b], np.float16)}
    return session.run(["y"], feed)[0]


# --- AC-144.1 the splice on the synthetic model ---------------------------------------------


@pytest.mark.unit
def test_ac_144_1_splice_gives_the_planned_bytes_and_keeps_its_input() -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import splice

    src = synthetic.build()
    out = splice(src)
    assert (len(out), _sha(out)) == (synthetic.GUARDED_BYTES, synthetic.GUARDED_SHA256)
    assert splice(src) == out
    assert _sha(src) == synthetic.SOURCE_SHA256


# --- AC-144.2 ORT on the source and the guarded graph ---------------------------------------


@pytest.mark.unit
def test_ac_144_2_guard_turns_nan_phase_into_positive_zero_and_keeps_finite_bits() -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import splice

    src = synthetic.build()
    guarded = splice(src)
    nan = _run(src, 0.0, 0.0)
    zero = _run(guarded, 0.0, 0.0)
    assert np.isnan(nan).all()
    assert zero.dtype == np.float16
    assert (zero == 0).all() and not np.signbit(zero).any()
    finite_src = _run(src, 1.0, 2.0)
    finite_guarded = _run(guarded, 1.0, 2.0)
    assert finite_guarded.dtype == np.float16
    assert finite_src.tobytes() == finite_guarded.tobytes()
    assert finite_guarded.tolist() == [0.463623046875]


# --- AC-144.3 every refusal, with its exact text --------------------------------------------


REFUSALS = [
    ("already-guarded", None, "already guarded"),
    ("two-divs", {"div_names": [DIV, DIV]}, f"expected one {DIV}, found 2"),
    ("no-div", {"div_names": []}, f"expected one {DIV}, found 0"),
    ("not-div", {"div_op": "Mul"}, "Div is not one Div with one output"),
    ("quotient-output", {"quotient_output": True}, "quotient is a graph output"),
    ("no-atan", {"atan": False}, "quotient must feed exactly one Atan"),
    ("no-initializer", {"initializer": False}, "no initializer"),
    ("two-graphs", {"graphs": 2}, "expected one graph, found 2"),
    ("no-graph", {"graphs": 0}, "expected one graph, found 0"),
]


@pytest.mark.unit
@pytest.mark.parametrize(("case", "kwargs", "text"), REFUSALS, ids=[r[0] for r in REFUSALS])
def test_ac_144_3_splice_refuses_each_unknown_shape_with_its_text(
    case: str, kwargs: dict[str, Any] | None, text: str
) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import SpliceError, splice

    model = splice(synthetic.build()) if kwargs is None else synthetic.build(**kwargs)
    with pytest.raises(SpliceError) as caught:
        splice(model)
    assert str(caught.value) == text, case


WIRE_REFUSALS = [
    ("truncated-message", None, "field runs past its message"),
    ("truncated-varint", b"\x80", "truncated varint"),
    ("long-varint", b"\xff" * 11, "varint too long"),
    ("wire-type-3", b"\x0b", "unsupported wire type 3"),
]


@pytest.mark.unit
@pytest.mark.parametrize(("case", "raw", "text"), WIRE_REFUSALS, ids=[r[0] for r in WIRE_REFUSALS])
def test_ac_144_3_splice_refuses_broken_wire_bytes_with_its_text(
    case: str, raw: bytes | None, text: str
) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import SpliceError, splice

    model = synthetic.build()[:-1] if raw is None else raw
    with pytest.raises(SpliceError) as caught:
        splice(model)
    assert str(caught.value) == text, case


@pytest.mark.unit
def test_ac_144_3_splice_refuses_a_name_that_is_not_utf8() -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import SpliceError, splice

    with pytest.raises(SpliceError) as caught:
        splice(synthetic.build(name_bytes=b"\xff"))
    assert isinstance(caught.value.__cause__, UnicodeDecodeError)


# --- AC-144.4 and AC-144.5 GUARD_GATE and GUARD_PASS_THROUGH --------------------------------


@pytest.mark.unit
def test_ac_144_4_gate_returns_the_path_without_reading_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_module()
    from avkit_infra.tts import phase_guard

    monkeypatch.setattr(phase_guard, "KOKORO_FP16", synthetic.spec())

    def no_read(self: Path) -> bytes:
        raise AssertionError(f"read_bytes called on {self.name}")

    longer = tmp_path / "model_fp16.onnx"
    longer.write_bytes(synthetic.build() + b"\x00")
    missing = tmp_path / "missing.onnx"
    monkeypatch.setattr(Path, "read_bytes", no_read)
    with capture_logs() as logs:
        results = [
            phase_guard.guarded_model(missing, INT8_ID),
            phase_guard.guarded_model(missing, FP16_ID),
            phase_guard.guarded_model(longer, FP16_ID),
        ]
    assert results == [str(missing), str(missing), str(longer)]
    assert logs == []


@pytest.mark.unit
def test_ac_144_5_a_file_with_an_unknown_hash_loads_as_shipped(tmp_path: Path) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import guarded_model

    other = tmp_path / "model_fp16.onnx"
    other.write_bytes(b"\x00" * synthetic.SOURCE_BYTES)
    with capture_logs() as logs:
        result = guarded_model(other, FP16_ID, synthetic.spec())
    assert result == str(other)
    assert logs == []


# --- AC-144.6 GUARD_REFUSE -------------------------------------------------------------------


@pytest.mark.unit
def test_ac_144_6_a_refused_splice_or_a_wrong_result_hash_loads_as_shipped(
    tmp_path: Path,
) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import GuardSpec, guarded_model, splice

    guarded = splice(synthetic.build())
    spliced = tmp_path / "spliced_fp16.onnx"
    spliced.write_bytes(guarded)
    source = tmp_path / "model_fp16.onnx"
    source.write_bytes(synthetic.build())
    refuse = GuardSpec(_sha(guarded), len(guarded), synthetic.GUARDED_SHA256)
    wrong = GuardSpec(synthetic.SOURCE_SHA256, synthetic.SOURCE_BYTES, "0" * 64)
    with capture_logs() as logs:
        first = guarded_model(spliced, FP16_ID, refuse)
    with capture_logs() as logs_hash:
        second = guarded_model(source, FP16_ID, wrong)
    assert (first, second) == (str(spliced), str(source))
    assert logs == [
        {
            "event": "tts.phase_guard",
            "log_level": "warning",
            "module": "tts",
            "variant_id": FP16_ID,
            "outcome": "refused",
            "reason": "SpliceError",
        }
    ]
    assert _guard_events(logs_hash) == [
        {
            "event": "tts.phase_guard",
            "log_level": "warning",
            "module": "tts",
            "variant_id": FP16_ID,
            "outcome": "refused",
            "reason": "result_hash",
        }
    ]
    for entry in logs + logs_hash:
        for value in entry.values():
            text = str(value)
            assert str(tmp_path) not in text
            assert "model_fp16" not in text and "spliced_fp16" not in text


# --- AC-144.7 GUARD_APPLIED ------------------------------------------------------------------


@pytest.mark.unit
def test_ac_144_7_a_known_file_gives_the_guarded_bytes_and_one_info_event(
    tmp_path: Path,
) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import guarded_model, splice

    source = tmp_path / "model_fp16.onnx"
    source.write_bytes(synthetic.build())
    with capture_logs() as logs:
        result = guarded_model(source, FP16_ID, synthetic.spec())
    assert isinstance(result, bytes)
    assert result == splice(synthetic.build())
    assert len(logs) == 1
    assert set(logs[0]) == {"event", "log_level", "module", "variant_id", "outcome"}
    assert logs[0] == {
        "event": "tts.phase_guard",
        "log_level": "info",
        "module": "tts",
        "variant_id": FP16_ID,
        "outcome": "applied",
    }


# --- AC-144.8 NO_FILE_WRITE ------------------------------------------------------------------


@pytest.mark.unit
def test_ac_144_8_the_guard_never_writes_to_the_models_folder(tmp_path: Path) -> None:
    _require_module()
    from avkit_infra.tts.phase_guard import GuardSpec, guarded_model, splice

    guarded = splice(synthetic.build())
    files = {
        "model_fp16.onnx": synthetic.build(),
        "spliced_fp16.onnx": guarded,
        "other_fp16.onnx": b"\x01" * synthetic.SOURCE_BYTES,
    }
    for name, data in files.items():
        (tmp_path / name).write_bytes(data)
    before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.iterdir()}
    refuse = GuardSpec(_sha(guarded), len(guarded), synthetic.GUARDED_SHA256)
    applied = guarded_model(tmp_path / "model_fp16.onnx", FP16_ID, synthetic.spec())
    refused = guarded_model(tmp_path / "spliced_fp16.onnx", FP16_ID, refuse)
    passed = guarded_model(tmp_path / "other_fp16.onnx", FP16_ID, synthetic.spec())
    assert isinstance(applied, bytes)
    assert refused == str(tmp_path / "spliced_fp16.onnx")
    assert passed == str(tmp_path / "other_fp16.onnx")
    after = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.iterdir()}
    assert sorted(after) == sorted(files)
    assert after == before
