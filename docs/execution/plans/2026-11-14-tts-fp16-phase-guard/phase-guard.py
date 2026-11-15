"""Session 73 FP16 phase guard spike (MEU-127, D-336; implementation-plan.md §Phase guard).

Usage: ``python phase-guard.py`` and one of ``selftest``, ``patch``, ``count``, ``compare`` or
``wavs`` (``--help`` on each lists its arguments).

PHASE_GUARD inserts two nodes between the exported atan2's ``Div``
(``/decoder/decoder/generator/Div``, ``Div(imag, real)``) and its one consumer, ``Atan``:
``IsNaN`` on the quotient, then ``Where(isnan, 0, quotient)``. A quotient of 0/0 becomes 0, and
every other quotient, an infinite one included, passes through bit for bit. ``patch`` writes the
guarded graph to a new file and never changes its source.

- ``selftest`` patches a fixture graph that it builds in its own folder (Session 56 RULE-4) and
  checks the values, the refusals, the source bytes and the determinism.
- ``count`` runs the test set's 149 jobs at graph level on a copy of a model with the phase
  tensors added as outputs, and counts the zero and near-zero denominators per chunk.
- ``compare`` runs the 149 jobs on the original and the guarded graph and compares each chunk's
  waveform bit for bit.
- ``wavs`` maps three packaged smoke runs' WAVs to their jobs through each run's own database
  copy, compares the control's passing WAVs with the guarded run's byte for byte, and writes the
  listening folder.

Each command writes one JSON receipt and exits 0 when its checks hold, 1 when one fails and 2 on
a usage or input error. Everything runs offline on copies under ``C:/Temp/av-kit``. ``onnx`` comes
from Session 52's hashed ``e5-site`` folder (D-333 E5); nothing is fetched.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sqlite3
import sys
import time
import wave
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
RECEIPTS = Path("C:/Temp/av-kit")
WORK = RECEIPTS / "s73"
S52_MODELS = RECEIPTS / "s52" / "smoke-models"
E5_SITE = RECEIPTS / "s52" / "e5-site"
S52_PLAN = REPO_ROOT / "docs" / "execution" / "plans" / "2026-11-06-tts-load-fp16"
SPIKE = S52_PLAN / "fp16-spike.py"
TEST_SET = S52_PLAN / "fp16-test-set" / "test-set.json"
S52_PHONEMES = RECEIPTS / "s52-spike-phonemes.json"
SMOKE = REPO_ROOT / "tools" / "smoke_packaged_tts.py"
PHONEMES = RECEIPTS / "s73-phonemes.json"
SELFTEST_DIR = WORK / "selftest"
TAPPED = WORK / "count-tapped-model_fp16.onnx"
REAL_MODELS = Path.home() / ".avkit"

G = "/decoder/decoder/generator/"
DIV = G + "Div"
GUARD_ISNAN = G + "PhaseGuard_IsNaN"
GUARD_WHERE = G + "PhaseGuard_Where"
GUARD_ZERO = G + "PhaseGuard_zero"
GUARD_MASK = G + "PhaseGuard_IsNaN_output_0"
GUARD_OUT = G + "PhaseGuard_Where_output_0"
TAPS = {
    "real": G + "Gather_4_output_0",
    "imag": G + "Gather_5_output_0",
    "div": G + "Div_output_0",
    "atan": G + "Atan_output_0",
    "phase": G + "Where_1_output_0",
}
FP16_MIN_NORMAL = 2.0**-14
FP16_MAX = 65504.0
COUNT_FIELDS = (
    "real_zero",
    "imag_zero",
    "both_zero",
    "real_subnormal",
    "ratio_overflow",
    "div_nan",
    "div_inf",
    "atan_nan",
    "phase_nan",
    "waveform_nonfinite",
)


class PatchError(Exception):
    """The graph is not the one PHASE_GUARD expects; nothing is written."""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def _onnx() -> Any:
    if str(E5_SITE) not in sys.path:
        sys.path.insert(0, str(E5_SITE))
    import onnx

    return onnx


def _module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inside(path: Path, root: Path) -> bool:
    return path.resolve().is_relative_to(root.resolve())


# --- PHASE_GUARD -------------------------------------------------------------------------------


def patch_model(model: Any) -> dict[str, Any]:
    """Insert PHASE_GUARD into `model` in place, or raise PatchError and leave it unchanged."""
    onnx = _onnx()
    nodes = model.graph.node
    names = [n.name for n in nodes]
    if GUARD_ISNAN in names or GUARD_WHERE in names:
        raise PatchError("already guarded")
    hits = [i for i, name in enumerate(names) if name == DIV]
    if len(hits) != 1:
        raise PatchError(f"expected one node named {DIV}, found {len(hits)}")
    index = hits[0]
    div = nodes[index]
    if div.op_type != "Div" or len(div.output) != 1:
        raise PatchError(f"{DIV} is {div.op_type} with {len(div.output)} outputs, not one Div")
    quotient = div.output[0]
    if any(o.name == quotient for o in model.graph.output):
        raise PatchError(f"{quotient} is a graph output")
    consumers = [n for n in nodes if quotient in n.input]
    if len(consumers) != 1 or consumers[0].op_type != "Atan":
        found = [(n.op_type, n.name) for n in consumers]
        raise PatchError(f"{quotient} must feed exactly one Atan, found {found}")
    atan = consumers[0]
    helper, tensor = onnx.helper, onnx.TensorProto
    zero = helper.make_tensor(GUARD_ZERO, tensor.FLOAT16, [], np.zeros((), np.float16).tobytes(),
                              raw=True)
    isnan = helper.make_node("IsNaN", [quotient], [GUARD_MASK], name=GUARD_ISNAN)
    where = helper.make_node("Where", [GUARD_MASK, GUARD_ZERO, quotient], [GUARD_OUT],
                             name=GUARD_WHERE)
    model.graph.initializer.append(zero)
    nodes.insert(index + 1, where)
    nodes.insert(index + 1, isnan)
    for slot, name in enumerate(atan.input):
        if name == quotient:
            atan.input[slot] = GUARD_OUT
    return {
        "div_index": index,
        "quotient": quotient,
        "consumer": atan.name,
        "inserted": [GUARD_ISNAN, GUARD_WHERE],
        "initializer": GUARD_ZERO,
        "nodes_before": len(names),
        "nodes_after": len(nodes),
    }


def _refuse_destination(src: Path, dst: Path) -> str | None:
    if dst.resolve() == src.resolve():
        return "the destination is the source"
    for root, label in (
        (S52_MODELS, "Session 52's cached models"),
        (REPO_ROOT, "the checkout"),
        (REAL_MODELS, "the real models folder"),
    ):
        if _inside(dst, root):
            return f"the destination is inside {label}"
    return None


def patch_file(src: Path, dst: Path) -> dict[str, Any]:
    """Write the guarded graph of `src` to `dst`, twice from fresh loads, and compare the bytes."""
    onnx = _onnx()
    refusal = _refuse_destination(src, dst)
    if refusal is not None:
        raise PatchError(refusal)
    src_before = _sha256(src)
    dst_before = _sha256(dst) if dst.is_file() else None
    builds = []
    info: dict[str, Any] = {}
    for _ in range(2):
        model = onnx.load(str(src))
        info = patch_model(model)
        builds.append(model.SerializeToString())
    if builds[0] != builds[1]:
        raise PatchError("two builds from the same source differ")
    onnx.checker.check_model(onnx.load_from_string(builds[0]))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(builds[0])
    src_after = _sha256(src)
    return {
        **info,
        "src": str(src),
        "src_sha256_before": src_before,
        "src_sha256_after": src_after,
        "src_unchanged": src_before == src_after,
        "dst": str(dst),
        "dst_sha256_before": dst_before,
        "dst_sha256": _sha256(dst),
        "dst_bytes": dst.stat().st_size,
        "deterministic": True,
        "checker": "onnx.checker.check_model passed",
    }


# --- selftest ----------------------------------------------------------------------------------


def _fixture(onnx: Any, *, tap: bool = False, second: str | None = None, op: str = "Div") -> Any:
    """A Div -> Atan -> Identity graph named like the generator's, with fp16 inputs."""
    helper, tensor = onnx.helper, onnx.TensorProto
    quotient = DIV + "_output_0"
    nodes = [
        helper.make_node(op, ["imag", "real"], [quotient], name=DIV),
        helper.make_node("Atan", [quotient], ["a"], name=G + "Atan"),
        helper.make_node("Identity", ["a"], ["phase"], name=G + "Identity"),
    ]
    outputs = [helper.make_tensor_value_info("phase", tensor.FLOAT16, [None])]
    if second is not None:
        nodes.append(helper.make_node(second, [quotient], ["b"], name=G + "Second"))
        outputs.append(helper.make_tensor_value_info("b", tensor.FLOAT16, [None]))
    if tap:
        outputs.append(helper.make_tensor_value_info(quotient, tensor.FLOAT16, [None]))
    graph = helper.make_graph(
        nodes,
        "phase-guard-fixture",
        [
            helper.make_tensor_value_info("imag", tensor.FLOAT16, [None]),
            helper.make_tensor_value_info("real", tensor.FLOAT16, [None]),
        ],
        outputs,
    )
    return helper.make_model(graph, opset_imports=[helper.make_opsetid("", 20)], ir_version=9)


def _bits(array: np.ndarray) -> np.ndarray:
    return np.ascontiguousarray(array).view(np.uint16)


def selftest() -> int:
    import onnxruntime as ort

    onnx = _onnx()
    shutil.rmtree(SELFTEST_DIR, ignore_errors=True)
    SELFTEST_DIR.mkdir(parents=True)
    checks: list[dict[str, Any]] = []

    def check(name: str, ok: bool, detail: object = None) -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    # imag / real: 0/0, -0/0, 0/-0, 1/0, -1/0, ordinary, subnormal pair, large finite, overflow,
    # zero numerator.
    imag = np.array([0, -0.0, 0, 1, -1, 0.5, 6e-8, 1e-3, 65504, 0], np.float16)
    real = np.array([0, 0, -0.0, 0, 0, 0.25, 6e-8, 6e-8, 6e-8, 2], np.float16)
    nan_at = [0, 1, 2]
    src = SELFTEST_DIR / "fixture.onnx"
    dst = SELFTEST_DIR / "fixture-guarded.onnx"
    onnx.save(_fixture(onnx), str(src))
    try:
        info = patch_file(src, dst)
        check("patch_file writes the guarded fixture", True, info["inserted"])
        check("source bytes unchanged", info["src_unchanged"])
        check("two builds identical", info["deterministic"])
        check("two nodes inserted", info["nodes_after"] == info["nodes_before"] + 2)
    except PatchError as exc:
        check("patch_file writes the guarded fixture", False, str(exc))
        info = {}
    if dst.is_file():
        guarded = onnx.load(str(dst))
        order = [n.name for n in guarded.graph.node]
        check("guard sits between Div and Atan",
              order[:4] == [DIV, GUARD_ISNAN, GUARD_WHERE, G + "Atan"], order)
        check("Atan reads the guard", list(guarded.graph.node[3].input) == [GUARD_OUT])
        check("opset and IR unchanged",
              (guarded.opset_import[0].version, guarded.ir_version) == (20, 9))
        for level in ("ORT_DISABLE_ALL", "ORT_ENABLE_ALL"):
            options = ort.SessionOptions()
            options.graph_optimization_level = getattr(ort.GraphOptimizationLevel, level)
            feeds = {"imag": imag, "real": real}
            before = ort.InferenceSession(str(src), options, providers=["CPUExecutionProvider"])
            after = ort.InferenceSession(str(dst), options, providers=["CPUExecutionProvider"])
            a0 = before.run(None, feeds)[0]
            a1 = after.run(None, feeds)[0]
            keep = [i for i in range(imag.size) if i not in nan_at]
            check(f"{level}: original is NaN exactly at the 0/0 slots",
                  np.flatnonzero(np.isnan(a0)).tolist() == nan_at, a0.tolist())
            check(f"{level}: guarded is +0 at the 0/0 slots",
                  _bits(a1[nan_at]).tolist() == [0, 0, 0], a1.tolist())
            check(f"{level}: every other slot is bit-identical",
                  _bits(a0[keep]).tolist() == _bits(a1[keep]).tolist())
            check(f"{level}: guarded output is finite", bool(np.isfinite(a1).all()))
    # Refusals: nothing is written, and the message names the reason.
    refusals = {
        "already guarded": onnx.load(str(dst)) if dst.is_file() else None,
        "graph output": _fixture(onnx, tap=True),
        "exactly one Atan": _fixture(onnx, second="Identity"),
        "not one Div": _fixture(onnx, op="Mul"),
    }
    no_div = _fixture(onnx)
    no_div.graph.node[0].name = G + "Div_renamed"
    refusals["expected one node named"] = no_div
    for reason, model in refusals.items():
        try:
            if model is None:
                raise PatchError("no guarded fixture to re-patch")
            patch_model(model)
            check(f"refuses: {reason}", False, "patched")
        except PatchError as exc:
            check(f"refuses: {reason}", reason in str(exc), str(exc))
    for label, target in (
        ("the destination is the source", src),
        ("Session 52's cached models", S52_MODELS / "phase-guard-selftest.onnx"),
        ("the checkout", HERE / "phase-guard-selftest.onnx"),
        ("the real models folder", REAL_MODELS / "models" / "phase-guard-selftest.onnx"),
    ):
        try:
            patch_file(src, target)
            check(f"refuses destination: {label}", False, "written")
        except PatchError as exc:
            untouched = target == src or not target.exists()
            check(f"refuses destination: {label}", label in str(exc) and untouched, str(exc))
    failed = [c for c in checks if not c["ok"]]
    _write(RECEIPTS / "s73-phase-guard-selftest.json",
           {"finished": _now(), "checks": checks, "failed": len(failed)})
    for c in checks:
        print(("ok   " if c["ok"] else "FAIL ") + c["check"])
    print(f"selftest: {len(checks)} checks, {len(failed)} failed")
    return 1 if failed else 0


# --- the 149 jobs at graph level ---------------------------------------------------------------


def _jobs() -> list[tuple[str, int, str, str]]:
    smoke = _module("smoke_packaged_tts", SMOKE)
    return smoke._sentence_jobs(json.loads(TEST_SET.read_text(encoding="utf-8")))


def phonemize() -> dict[str, Any]:
    """Each job's joined phonemes as the adapter builds them, into `PHONEMES`."""
    from avkit_infra.tts.adapter import _sentences
    from avkit_infra.tts.assets import activate_spacy_dir
    from avkit_infra.tts.espeak import EspeakCliAdapter
    from avkit_infra.tts.g2p import KokoroG2p

    started = _now()
    activate_spacy_dir(S52_MODELS)
    g2p = KokoroG2p(EspeakCliAdapter())
    cache: dict[tuple[str, str], str] = {}
    rows = []
    for kind, index, voice, text in _jobs():
        lang = voice[0]
        if (text, lang) not in cache:
            parts = (g2p.phonemize(sentence, lang) for sentence in _sentences(text))
            cache[(text, lang)] = " ".join(ps for ps in parts if ps)
        rows.append({"kind": kind, "index": index, "voice": voice, "lang": lang,
                     "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                     "phonemes": cache[(text, lang)]})
    s52 = json.loads(S52_PHONEMES.read_text(encoding="utf-8"))
    same = sum(1 for r in rows if r["kind"] == "sentence"
               and s52["b" if r["lang"] == "b" else "a"][r["index"]] == r["phonemes"])
    payload = {"started": started, "finished": _now(), "test_set_sha256": _sha256(TEST_SET),
               "en_core_web_sm": getattr(sys.modules.get("en_core_web_sm"), "__file__", None),
               "sentence_jobs_equal_to_s52": same, "jobs": rows}
    _write(PHONEMES, payload)
    return payload


def _counts(t: dict[str, np.ndarray]) -> dict[str, Any]:
    real = t["real"].astype(np.float32)
    imag = t["imag"].astype(np.float32)
    both = (real == 0) & (imag == 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.abs(imag) / np.abs(real)
    return {
        "frames": int(real.shape[-1]),
        "real_zero": int(np.count_nonzero(real == 0)),
        "imag_zero": int(np.count_nonzero(imag == 0)),
        "both_zero": int(np.count_nonzero(both)),
        "both_zero_bins": sorted(set(np.nonzero(both)[1].tolist())),
        "real_subnormal": int(np.count_nonzero((real != 0) & (np.abs(real) < FP16_MIN_NORMAL))),
        "ratio_overflow": int(np.count_nonzero((real != 0) & (ratio > FP16_MAX))),
        "div_nan": int(np.count_nonzero(np.isnan(t["div"]))),
        "div_inf": int(np.count_nonzero(np.isinf(t["div"]))),
        "atan_nan": int(np.count_nonzero(np.isnan(t["atan"]))),
        "phase_nan": int(np.count_nonzero(np.isnan(t["phase"]))),
    }


def _key(row: dict[str, Any]) -> str:
    return f"{row['kind']}#{row['index']}#{row['voice']}"


def _feed_jobs() -> tuple[Any, list[dict[str, Any]]]:
    spike = _module("fp16_spike", SPIKE)
    payload = phonemize()
    return spike.Feeder(), payload["jobs"]


def _session(model: Path) -> Any:
    import onnxruntime as ort

    return ort.InferenceSession(str(model), providers=["CPUExecutionProvider"])


def count(model: Path, out: Path) -> int:
    import onnxruntime as ort

    onnx = _onnx()
    started = _now()
    source_sha = _sha256(model)
    tapped = onnx.load(str(model))
    have = {o.name for o in tapped.graph.output}
    for name in TAPS.values():
        if name not in have:
            tapped.graph.output.append(
                onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT16, None))
    TAPPED.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(tapped, str(TAPPED))
    feeder, jobs = _feed_jobs()
    session = _session(TAPPED)
    names = ["waveform", *TAPS.values()]
    rows = []
    for job in jobs:
        chunks = []
        for symbols in feeder.chunks(job["phonemes"]):
            values = session.run(names, feeder.feeds(job["voice"], feeder.ids(symbols)))
            row = _counts(dict(zip(TAPS, values[1:], strict=True)))
            row["waveform_nonfinite"] = int(np.count_nonzero(~np.isfinite(values[0])))
            chunks.append(row)
        rows.append({"key": _key(job), "chunks": chunks})
    failing = [r["key"] for r in rows if any(c["waveform_nonfinite"] for c in r["chunks"])]
    with_nan = [r["key"] for r in rows if any(c["div_nan"] for c in r["chunks"])]
    with_both = [r["key"] for r in rows if any(c["both_zero"] for c in r["chunks"])]

    def total(keys: set[str], field: str) -> int:
        return sum(c[field] for r in rows if r["key"] in keys for c in r["chunks"])

    passing = {r["key"] for r in rows} - set(failing)
    summary = {
        "jobs": len(rows),
        "chunks": sum(len(r["chunks"]) for r in rows),
        "failing": failing,
        "failing_count": len(failing),
        "jobs_with_div_nan": with_nan,
        "jobs_with_both_zero": with_both,
        "div_nan_jobs_equal_failing_jobs": with_nan == failing,
        "both_zero_bins": sorted({b for r in rows for c in r["chunks"]
                                  for b in c["both_zero_bins"]}),
        "failing_totals": {f: total(set(failing), f) for f in COUNT_FIELDS},
        "passing_totals": {f: total(passing, f) for f in COUNT_FIELDS},
    }
    _write(out, {"command": "count", "started": started, "finished": _now(),
                 "onnxruntime": ort.__version__, "onnx": onnx.__version__,
                 "model": str(model), "model_sha256": source_sha,
                 "model_unchanged": _sha256(model) == source_sha, "tapped_copy": str(TAPPED),
                 "taps": TAPS, "summary": summary, "jobs": rows})
    print(json.dumps(summary, indent=1))
    ok = summary["jobs"] == 149 and summary["div_nan_jobs_equal_failing_jobs"]
    return 0 if ok and _sha256(model) == source_sha else 1


def compare(original: Path, patched: Path, out: Path) -> int:
    import onnxruntime as ort

    started = _now()
    shas = {"original": _sha256(original), "patched": _sha256(patched)}
    feeder, jobs = _feed_jobs()
    before, after = _session(original), _session(patched)
    rows = []
    for job in jobs:
        chunks = []
        for symbols in feeder.chunks(job["phonemes"]):
            feeds = feeder.feeds(job["voice"], feeder.ids(symbols))
            a0 = before.run(["waveform"], feeds)[0]
            a1 = after.run(["waveform"], feeds)[0]
            same = a0.shape == a1.shape and a0.tobytes() == a1.tobytes()
            chunks.append({
                "samples": int(a1.size),
                "original_nonfinite": int(np.count_nonzero(~np.isfinite(a0))),
                "guarded_nonfinite": int(np.count_nonzero(~np.isfinite(a1))),
                "identical": same,
                "differing_samples": 0 if same or a0.shape != a1.shape
                else int(np.count_nonzero(a0.view(np.uint32) != a1.view(np.uint32))),
                "guarded_peak": float(np.max(np.abs(a1))) if np.isfinite(a1).all() else None,
            })
        rows.append({"key": _key(job), "chunks": chunks})
    original_failing = [r["key"] for r in rows if any(c["original_nonfinite"] for c in r["chunks"])]
    guarded_failing = [r["key"] for r in rows if any(c["guarded_nonfinite"] for c in r["chunks"])]
    changed = [r["key"] for r in rows if not all(c["identical"] for c in r["chunks"])]
    summary = {
        "jobs": len(rows),
        "original_failing": original_failing,
        "original_failing_count": len(original_failing),
        "guarded_failing": guarded_failing,
        "changed": changed,
        "changed_equal_original_failing": changed == original_failing,
        "unchanged_jobs": len(rows) - len(changed),
    }
    _write(out, {"command": "compare", "started": started, "finished": _now(),
                 "onnxruntime": ort.__version__, "models": {"original": str(original),
                 "patched": str(patched)}, "sha256": shas,
                 "unchanged_after": _sha256(original) == shas["original"],
                 "summary": summary, "jobs": rows})
    print(json.dumps(summary, indent=1))
    ok = (summary["jobs"] == 149 and not guarded_failing
          and summary["changed_equal_original_failing"])
    return 0 if ok and _sha256(original) == shas["original"] else 1


# --- packaged WAVs -----------------------------------------------------------------------------


def _wav(path: Path) -> dict[str, Any]:
    with wave.open(str(path), "rb") as wav:
        declared = wav.getnframes()
        payload = len(wav.readframes(declared))
        complete = payload == declared * wav.getsampwidth() * wav.getnchannels()
        return {"frames": declared, "complete": complete, "rate": wav.getframerate(),
                "seconds": round(declared / wav.getframerate(), 2)}


def _run_rows(run_dir: Path, label: str) -> dict[tuple[str, str], list[tuple[str, str | None]]]:
    """(text sha256, voice) to (status, output_path) from a copy of the run's own database."""
    source = run_dir / "app-data"
    copy = WORK / "db-copies" / label
    shutil.rmtree(copy, ignore_errors=True)
    copy.mkdir(parents=True)
    for path in source.glob("avkit.db*"):
        shutil.copy2(path, copy / path.name)
    rows: dict[tuple[str, str], list[tuple[str, str | None]]] = {}
    with sqlite3.connect(copy / "avkit.db") as db:
        for text_hash, voice, status, output in db.execute(
            "SELECT text_hash, voice, status, output_path FROM tts_jobs"
        ):
            rows.setdefault((text_hash, voice), []).append((status, output))
    return rows


def wavs(control_run: Path, patched_run: Path, reference_run: Path, control_json: Path,
         dest: Path, out: Path) -> int:
    if not _inside(dest, WORK):
        print(f"the listening folder must be inside {WORK}")
        return 2
    control = json.loads(control_json.read_text(encoding="utf-8"))
    failed = {(f["kind"], f["index"], f["voice"]) for f in control["failures"]}
    runs = {label: _run_rows(path, label) for label, path in
            (("control", control_run), ("guarded", patched_run), ("reference", reference_run))}
    problems: list[str] = []

    def done_wav(label: str, key: tuple[str, str]) -> Path | None:
        hits = runs[label].get(key, [])
        if len(hits) != 1:
            problems.append(f"{label}: {len(hits)} rows for one job")
            return None
        status, output = hits[0]
        if status != "Done" or not output or not Path(output).is_file():
            return None
        return Path(output)

    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    identical, differing, listening = 0, [], []
    lines = []
    for kind, index, voice, text in _jobs():
        key = (hashlib.sha256(text.encode("utf-8")).hexdigest(), voice)
        name = f"{kind}#{index}#{voice}"
        guarded = done_wav("guarded", key)
        if guarded is None or not _wav(guarded)["complete"]:
            problems.append(f"guarded: {name} has no complete WAV")
            continue
        if (kind, index, voice) not in failed:
            original = done_wav("control", key)
            if original is None:
                problems.append(f"control: {name} passed in the receipt but has no WAV")
            elif original.read_bytes() == guarded.read_bytes():
                identical += 1
            else:
                differing.append(name)
            continue
        reference = done_wav("reference", key)
        if reference is None or not _wav(reference)["complete"]:
            problems.append(f"reference: {name} has no complete WAV")
            continue
        number = len(listening) + 1
        stem = f"{number:02d}-{kind}-{index:02d}-{voice}"
        files = {}
        for suffix, path in (("fp16-guarded", guarded), ("int8", reference)):
            target = dest / f"{stem}-{suffix}.wav"
            shutil.copy2(path, target)
            files[suffix] = {"file": target.name, **_wav(target)}
        listening.append({"job": name, **files})
        preview = " ".join(text.split())[:100]
        lines.append(f"{stem}  FP16 guarded {files['fp16-guarded']['seconds']} s, "
                     f"INT8 {files['int8']['seconds']} s  {preview}")
    (dest / "listen.txt").write_text(
        "Session 73 listening folder: each job the control run failed, guarded FP16 then INT8.\n"
        + "\n".join(lines) + "\n", encoding="utf-8")
    summary = {"control_failed": len(failed), "control_passed_identical": identical,
               "control_passed_differing": differing, "listening": listening,
               "listening_folder": str(dest), "problems": problems}
    _write(out, {"command": "wavs", "finished": _now(), "control": str(control_json),
                 "summary": summary})
    print(json.dumps({k: v for k, v in summary.items() if k != "listening"}, indent=1))
    ok = (not problems and not differing and len(listening) == len(failed)
          and identical + len(failed) == len(_jobs()))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("selftest")
    p = sub.add_parser("patch")
    p.add_argument("--src", type=Path, required=True)
    p.add_argument("--dst", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    c = sub.add_parser("count")
    c.add_argument("--model", type=Path, required=True)
    c.add_argument("--out", type=Path, required=True)
    m = sub.add_parser("compare")
    m.add_argument("--original", type=Path, required=True)
    m.add_argument("--patched", type=Path, required=True)
    m.add_argument("--out", type=Path, required=True)
    w = sub.add_parser("wavs")
    for name in ("--control-run", "--patched-run", "--reference-run", "--control", "--dest",
                 "--out"):
        w.add_argument(name, type=Path, required=True)
    args = parser.parse_args(argv)
    t0 = time.monotonic()
    try:
        if args.command == "selftest":
            code = selftest()
        elif args.command == "patch":
            try:
                info = patch_file(args.src, args.dst)
            except PatchError as exc:
                print(f"patch refused: {exc}")
                return 1
            _write(args.out, {"command": "patch", "finished": _now(), **info})
            print(json.dumps(info, indent=1))
            code = 0 if info["src_unchanged"] else 1
        elif args.command == "count":
            code = count(args.model, args.out)
        elif args.command == "compare":
            code = compare(args.original, args.patched, args.out)
        else:
            code = wavs(args.control_run, args.patched_run, args.reference_run, args.control,
                        args.dest, args.out)
    except (OSError, ValueError, KeyError) as exc:
        print(f"phase-guard: {type(exc).__name__}: {exc}")
        return 2
    print(f"phase-guard {args.command}: exit {code} in {time.monotonic() - t0:.0f} s")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
