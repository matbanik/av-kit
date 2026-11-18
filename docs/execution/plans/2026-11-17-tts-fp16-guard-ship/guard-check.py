"""Session 74 row 6 (AC-144.12): `guarded_model` on the real FP16 file in `models-copy`.

Puts `packages/infrastructure/src` on `sys.path`, imports `phase_guard`, records the FP16 file's
SHA-256, size and `st_mtime_ns`, starts `tracemalloc`, calls `guarded_model` under
`structlog.testing.capture_logs`, checks the result's length and SHA-256 against Session 73's
guarded file, builds an ORT CPU session from the bytes, calls `guarded_model` on the INT8 file,
re-reads the FP16 file's identity, and prints one JSON object with each check, the wall time and
the `tracemalloc` peak. Exit 0 only when every check holds, the peak at most 400,000,000 bytes
(`ONE_JOIN`). A pass-through or refusal on the real file, or a peak over the limit, is S10.

Usage:
  python guard-check.py --models DIR --out JSON
  python guard-check.py --selftest
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "packages" / "infrastructure" / "src"))
sys.path.insert(0, str(REPO))

FP16_REL = "kokoro-v1.0-onnx/onnx/model_fp16.onnx"
INT8_REL = "kokoro-v1.0-onnx/onnx/model_quantized.onnx"
GUARDED_BYTES = 163_235_204
PEAK_LIMIT = 400_000_000
MB = 1024 * 1024


def _identity(path: Path) -> dict[str, Any]:
    st = path.stat()
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": st.st_size,
        "mtime_ns": st.st_mtime_ns,
    }


def check(
    models: Path,
    *,
    guarded_bytes: int = GUARDED_BYTES,
    peak_limit: int = PEAK_LIMIT,
    build_session: bool = True,
) -> dict[str, Any]:
    import structlog.testing

    from avkit_infra.tts import phase_guard

    spec = phase_guard.KOKORO_FP16
    fp16 = models / FP16_REL
    int8 = models / INT8_REL
    before = _identity(fp16)
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()
    with structlog.testing.capture_logs() as logs:
        result = phase_guard.guarded_model(fp16, "kokoro-onnx-fp16")
    wall = time.perf_counter() - t0
    _cur, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    is_bytes = isinstance(result, bytes)
    got_sha = hashlib.sha256(result).hexdigest() if is_bytes else None
    checks: dict[str, Any] = {
        "source_sha256": before["sha256"] == spec.source_sha256,
        "source_bytes": before["bytes"] == spec.source_bytes,
        "result_is_bytes": is_bytes,
        "result_bytes": len(result) == guarded_bytes if is_bytes else False,
        "result_sha256": got_sha == spec.guarded_sha256,
        "one_applied_event": [(e.get("event"), e.get("outcome")) for e in logs]
        == [("tts.phase_guard", "applied")],
        "peak_within_limit": peak <= peak_limit,
    }
    if build_session and is_bytes:
        import onnxruntime as ort

        options = ort.SessionOptions()
        options.log_severity_level = 3
        try:
            ort.InferenceSession(result, options, providers=["CPUExecutionProvider"])
            checks["ort_cpu_session"] = True
        except Exception as exc:
            checks["ort_cpu_session"] = f"failed: {type(exc).__name__}"
    elif build_session:
        checks["ort_cpu_session"] = "no bytes"
    del result
    int8_result = phase_guard.guarded_model(int8, "kokoro-onnx-int8")
    checks["int8_returns_str"] = int8_result == str(int8)
    after = _identity(fp16)
    checks["fp16_file_unchanged"] = after == before
    return {
        "checks": checks,
        "pass": all(v is True for v in checks.values()),
        "source": before,
        "result_bytes": guarded_bytes if checks["result_bytes"] is True else None,
        "result_sha256": got_sha,
        "events": [{k: v for k, v in e.items()} for e in logs],
        "wall_seconds": round(wall, 3),
        "tracemalloc_peak_bytes": peak,
        "tracemalloc_peak_MB": round(peak / MB, 1),
        "peak_limit_bytes": peak_limit,
    }


def selftest() -> int:
    from tests import tts_onnx_synthetic as synthetic

    from avkit_infra.tts import phase_guard

    wrong = 0
    shipped = phase_guard.KOKORO_FP16
    try:
        phase_guard.KOKORO_FP16 = synthetic.spec()
        with tempfile.TemporaryDirectory(prefix="s74-guard-check-") as tmp:
            models = Path(tmp)
            (models / FP16_REL).parent.mkdir(parents=True)
            (models / FP16_REL).write_bytes(synthetic.build())
            (models / INT8_REL).write_bytes(b"\x02" * 64)
            cases = [
                ("synthetic-pass", {"guarded_bytes": synthetic.GUARDED_BYTES}, True),
                ("wrong-length", {"guarded_bytes": synthetic.GUARDED_BYTES + 1}, False),
                ("peak-over", {"guarded_bytes": synthetic.GUARDED_BYTES, "peak_limit": 1}, False),
            ]
            for name, kwargs, want in cases:
                got = check(models, **kwargs)["pass"]
                ok = got is want
                wrong += not ok
                print(f"{name}: {'ok' if ok else 'WRONG'}")
            (models / FP16_REL).write_bytes(b"\x00" * synthetic.SOURCE_BYTES)
            got = check(models, guarded_bytes=synthetic.GUARDED_BYTES)["pass"]
            ok = got is False
            wrong += not ok
            print(f"pass-through-refused: {'ok' if ok else 'WRONG'}")
    finally:
        phase_guard.KOKORO_FP16 = shipped
    print(f"guard-check selftest: 4 case(s), {wrong} wrong")
    return 1 if wrong else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.models is None or args.out is None:
        ap.error("--models and --out are required")
    payload = check(args.models)
    text = json.dumps(payload, indent=1) + "\n"
    args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    print(f"guard-check: {'pass' if payload['pass'] else 'FAIL'}")
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
