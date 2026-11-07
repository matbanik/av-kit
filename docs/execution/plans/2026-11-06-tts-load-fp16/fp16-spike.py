"""Session 52 FP16 spike (MEU-121, AC-121.9, D-333; implementation-plan.md §FP16 spike).

Usage: ``python fp16-spike.py all [--e5]`` | ``phonemize`` | ``run --id ID --expect-ort VERSION``
| ``e5 --levels JSON --failing JSON``.

``all`` runs the whole spike behind dead proxies. It phonemizes the test set's 40 sentences
once (lang ``a``, and ``b`` for the first 20) into ``s52-spike-phonemes.json``, then runs E0 to
E4 on the FP16 copy in ``C:/Temp/av-kit/s52/smoke-models``: the rate probe's 140 (sentence,
voice) pairs, fed as the adapter feeds them. Each experiment writes ``s52-spike-<id>.json`` with
the onnxruntime version, the session options, each pair's non-finite sample count and its start
and end times. E2's versions each run in a ``uv run --offline --no-sync --with`` child, and a
child whose ``onnxruntime.__version__`` isn't the one asked for is recorded as not run.

A setting that makes all 140 pairs finite is run again straight after E0's control; when the
control still fails and the setting is still clean, it is a cause and the spike stops. The box is
2 hours from the phonemes JSON's start: each experiment checks it first, and once it has run out
every remaining experiment is ``boxed``. ``--e5`` adds E5 after E4: a hashed ``--no-deps``
install of ``onnx`` and ``ml-dtypes`` into ``C:/Temp/av-kit/s52/e5-site`` (the one fetch this
plan allows), then an offline child that adds every node's output to a copy of the model and
finds the first node in graph order whose output holds NaN or Inf. Its cache, venv and lock
checks are S5 when anything else changes.

The summary, ``s52-spike-summary.json``, holds each experiment's status (``run``, ``not_run``
with its error, or ``boxed``), the stop reason (``cause``, ``done``, ``box`` or ``control``), the
candidate setting and E5's S5 marks. The script exits 0 whichever way the spike stops, and 1
only on its own error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
VENV_PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
RECEIPTS = Path("C:/Temp/av-kit")
MODELS = RECEIPTS / "s52" / "smoke-models"
FP16 = MODELS / "kokoro-v1.0-onnx" / "onnx" / "model_fp16.onnx"
TEST_SET = HERE / "fp16-test-set" / "test-set.json"
PHONEMES = RECEIPTS / "s52-spike-phonemes.json"
SUMMARY = RECEIPTS / "s52-spike-summary.json"
E5_SITE = RECEIPTS / "s52" / "e5-site"
E5_REQUIREMENTS = RECEIPTS / "s52" / "e5-requirements.txt"
E5_MODEL = RECEIPTS / "s52" / "e5-model_fp16-node-outputs.onnx"
E5_RUN = RECEIPTS / "s52-spike-e5-run.json"
BOX_S = 7200
LOCKED_ORT = "1.31.1"
# 1.20.1 is cached only for cp311, so it isn't tried (plan §FP16 spike, E2).
E2_VERSIONS = ("1.24.4", "1.29.0")
E1_LEVELS = ("ORT_DISABLE_ALL", "ORT_ENABLE_BASIC", "ORT_ENABLE_EXTENDED")
E4_SETTINGS = {
    "e4-threads-1": {"intra_op_num_threads": 1},
    "e4-no-arena": {"enable_cpu_mem_arena": False},
}
# The rate probe's failing pairs (fp16-rate-probe.txt:29-34): the phoneme-string lengths for
# the American voices, and bf_emma's count, which it printed without lengths.
RATE_PROBE = {
    "af_heart": [53, 80, 93, 102],
    "am_michael": [53, 119],
    "af_bella": [53, 100],
    "bf_emma": 3,
}
AMERICAN = ("af_heart", "am_michael", "af_bella")
# Picked at plan time (C:/Temp/av-kit/s52-onnx-pin.txt, s52-ml-dtypes-pin.txt).
E5_PINS = (
    "onnx==1.23.2 --hash=sha256:9b382ba898a7c142a0801d03cf04ecabced96c1543c7b643a86f0928143802de",
    "ml-dtypes==0.6.0 --hash=sha256:"
    "2a3e9d53925597fbffafd2a37048dadeddd0bdaba58058f6ae0869ed709a184d",
)
E5_DISTS = {"onnx-1.23.2.dist-info", "ml_dtypes-0.6.0.dist-info"}
E5_CACHE_NAMES = {"onnx", "ml-dtypes"}
DEAD_PROXY = "http://127.0.0.1:9"
PROXY_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")
TRAILING_PUNCTUATION = set(".!?,;:…")
FLOAT_TYPES = {"tensor(float16)", "tensor(float)", "tensor(double)", "tensor(bfloat16)"}
E5_BATCH = 200


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _experiment_path(exp_id: str) -> Path:
    return RECEIPTS / f"s52-spike-{exp_id}.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phonemize() -> dict[str, Any]:
    """Phonemize the test set's sentences as the adapter does, into `PHONEMES`."""
    from avkit_infra.tts.adapter import _sentences
    from avkit_infra.tts.assets import activate_spacy_dir
    from avkit_infra.tts.espeak import EspeakCliAdapter
    from avkit_infra.tts.g2p import KokoroG2p

    started = _now()
    sentences = json.loads(TEST_SET.read_text(encoding="utf-8"))["sentences"]
    activate_spacy_dir(MODELS)
    g2p = KokoroG2p(EspeakCliAdapter())

    def joined(text: str, lang: str) -> str:
        parts = (g2p.phonemize(sentence, lang) for sentence in _sentences(text))
        return " ".join(ps for ps in parts if ps)

    payload = {
        "started": started,
        "models": str(MODELS),
        "a": [joined(text, "a") for text in sentences],
        "b": [joined(text, "b") for text in sentences[:20]],
    }
    spacy_model = sys.modules.get("en_core_web_sm")
    payload["en_core_web_sm"] = getattr(spacy_model, "__file__", None)
    payload["finished"] = _now()
    _write(PHONEMES, payload)
    return payload


def _pairs(phonemes: dict[str, Any]) -> list[tuple[str, int, str]]:
    """The rate probe's 140 (voice, index, phonemes) pairs, in its order."""
    pairs = [(voice, i, ps) for voice in AMERICAN for i, ps in enumerate(phonemes["a"])]
    return pairs + [("bf_emma", i, ps) for i, ps in enumerate(phonemes["b"])]


class Feeder:
    """`ONNX_FEEDS` for the FP16 copy: vocab ids, the voice pack row and speed."""

    def __init__(self) -> None:
        from avkit_infra.tts.adapter import _phoneme_symbols
        from avkit_infra.tts.g2p import split_phonemes
        from avkit_infra.tts.voices import PACK_ROWS, STYLE_DIM, voice_pack_path

        self._symbols = _phoneme_symbols
        self._split = split_phonemes
        self._rows = PACK_ROWS
        self._dim = STYLE_DIM
        payload = json.loads((MODELS / "config.json").read_text(encoding="utf-8"))
        self.vocab: dict[str, int] = payload["vocab"]
        self._packs = {
            voice: np.fromfile(voice_pack_path(MODELS, voice), dtype="<f4").reshape(
                PACK_ROWS, STYLE_DIM
            )
            for voice in (*AMERICAN, "bf_emma")
        }

    def chunks(self, phonemes: str) -> list[list[str]]:
        return [self._symbols(chunk) for chunk in self._split(phonemes)]

    def ids(self, symbols: list[str]) -> list[int]:
        return [self.vocab[s] for s in symbols if s in self.vocab]

    def style_row(self, ids: list[int]) -> int:
        return max(min(len(ids), self._rows) - 1, 0)

    def feeds(
        self, voice: str, ids: list[int], *, row: int | None = None, speed: float = 1.0
    ) -> dict[str, np.ndarray]:
        index = self.style_row(ids) if row is None else min(max(row, 0), self._rows - 1)
        return {
            "input_ids": np.array([[0, *ids, 0]], dtype=np.int64),
            "style": self._packs[voice][index].reshape(1, self._dim),
            "speed": np.array([speed], dtype=np.float32),
        }


def _session(model: Path, options: dict[str, Any]) -> Any:
    import onnxruntime as ort

    so = ort.SessionOptions()
    for key, value in options.items():
        if key == "graph_optimization_level":
            value = getattr(ort.GraphOptimizationLevel, value)
        setattr(so, key, value)
    return ort.InferenceSession(str(model), so, providers=["CPUExecutionProvider"])


def _nonfinite(array: np.ndarray) -> int:
    return int(np.count_nonzero(~np.isfinite(array)))


def _float_nonfinite(value: object) -> int:
    """Non-finite count of a float tensor; 0 for any other output."""
    if isinstance(value, np.ndarray) and value.dtype.kind == "f":
        return _nonfinite(value)
    return 0


def run_pairs(exp_id: str, options: dict[str, Any], expect_ort: str) -> dict[str, Any]:
    """Run the 140 pairs on one session and write `s52-spike-<exp_id>.json`."""
    import onnxruntime as ort

    result: dict[str, Any] = {
        "id": exp_id,
        "status": "run",
        "started": _now(),
        "onnxruntime": ort.__version__,
        "onnxruntime_file": ort.__file__,
        "expect_ort": expect_ort,
        "model": str(FP16),
        "session_options": options,
    }
    if ort.__version__ != expect_ort:
        result.update(
            status="not_run",
            error=f"onnxruntime {ort.__version__} loaded, expected {expect_ort}",
            finished=_now(),
        )
        _write(_experiment_path(exp_id), result)
        return result
    feeder = Feeder()
    session = _session(FP16, options)
    rows = []
    for voice, index, phonemes in _pairs(json.loads(PHONEMES.read_text(encoding="utf-8"))):
        tokens, styles, samples, bad = [], [], 0, 0
        for symbols in feeder.chunks(phonemes):
            ids = feeder.ids(symbols)
            audio = session.run(None, feeder.feeds(voice, ids))[0].reshape(-1)
            tokens.append(len(ids))
            styles.append(feeder.style_row(ids))
            samples += int(audio.size)
            bad += _nonfinite(audio)
        rows.append(
            {
                "key": f"{voice}#{index}",
                "voice": voice,
                "index": index,
                "phoneme_chars": len(phonemes),
                "tokens": tokens,
                "style_rows": styles,
                "samples": samples,
                "nonfinite": bad,
            }
        )
    failing = [row["key"] for row in rows if row["nonfinite"]]
    result.update(pairs=rows, failing=failing, failing_count=len(failing), finished=_now())
    _write(_experiment_path(exp_id), result)
    return result


def run_e3(failing: list[str]) -> dict[str, Any]:
    """E3, diagnostic only: vary the style row, the speed and the trailing punctuation."""
    import onnxruntime as ort

    result: dict[str, Any] = {
        "id": "e3",
        "status": "run",
        "started": _now(),
        "onnxruntime": ort.__version__,
        "model": str(FP16),
        "session_options": {},
        "note": "diagnostic only: run on E0's failing pairs, never a candidate",
    }
    feeder = Feeder()
    session = _session(FP16, {})
    by_key = {
        f"{v}#{i}": (v, ps) for v, i, ps in _pairs(json.loads(PHONEMES.read_text(encoding="utf-8")))
    }
    rows = []
    for key in failing:
        voice, phonemes = by_key[key]
        variants: dict[str, int | None] = {}
        for symbols in feeder.chunks(phonemes):
            ids = feeder.ids(symbols)
            base = feeder.style_row(ids)
            trials: dict[str, dict[str, Any]] = {"base": {}}
            for delta in (-2, -1, 1, 2):
                trials[f"style{delta:+d}"] = {"row": base + delta}
            for speed in (0.9, 1.1):
                trials[f"speed-{speed}"] = {"speed": speed}
            for name, kwargs in trials.items():
                audio = session.run(None, feeder.feeds(voice, ids, **kwargs))[0]
                variants[name] = (variants.get(name) or 0) + _nonfinite(audio)
            if symbols and symbols[-1] in TRAILING_PUNCTUATION:
                trimmed = feeder.ids(symbols[:-1])
                audio = session.run(None, feeder.feeds(voice, trimmed, row=base))[0]
                variants["no-trailing-punctuation"] = _nonfinite(audio)
            else:
                variants.setdefault("no-trailing-punctuation", None)
        rows.append({"key": key, "nonfinite": variants})
    result.update(pairs=rows, finished=_now())
    _write(_experiment_path("e3"), result)
    return result


def _dead_proxy_env(env: dict[str, str]) -> dict[str, str]:
    out = dict(env)
    for key in PROXY_KEYS:
        out[key] = out[key.lower()] = DEAD_PROXY
    out["NO_PROXY"] = out["no_proxy"] = "127.0.0.1,localhost"
    return out


def _tail(text: str, lines: int = 40) -> str:
    return "\n".join(text.splitlines()[-lines:])


def _child(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def run_e2(version: str, exp_id: str | None = None) -> dict[str, Any]:
    """One E2 version in its own `uv run --offline --no-sync --with` child."""
    exp_id = exp_id or f"e2-{version}"
    path = _experiment_path(exp_id)
    started = _now()
    done = _child(
        [
            "uv",
            "run",
            "--offline",
            "--no-sync",
            "--with",
            f"onnxruntime=={version}",
            "python",
            str(Path(__file__).resolve()),
            "run",
            "--id",
            exp_id,
            "--expect-ort",
            version,
        ],
        dict(os.environ),
    )
    if path.is_file():
        result = json.loads(path.read_text(encoding="utf-8"))
        result["child_exit"] = done.returncode
        if done.returncode:
            result.update(status="not_run", error=_tail(done.stderr))
        _write(path, result)
        return result
    result = {
        "id": exp_id,
        "status": "not_run",
        "started": started,
        "expect_ort": version,
        "child_exit": done.returncode,
        "error": _tail(done.stderr) or _tail(done.stdout),
        "finished": _now(),
    }
    _write(path, result)
    return result


def _cache_root(env: dict[str, str]) -> Path:
    done = _child(["uv", "cache", "dir", "--no-config"], env)
    if done.returncode:
        raise RuntimeError(f"uv cache dir failed: {done.stderr.strip()}")
    return Path(done.stdout.strip())


def _normal(name: str) -> str:
    for suffix in (".rkyv", ".lock", ".msgpack"):
        name = name.removesuffix(suffix)
    return re.sub(r"[-_.]+", "-", name.lower())


def cache_inventory(root: Path) -> list[str]:
    """The package names under each `wheels-v*/<source>/` and `simple-v*/<source>/` folder."""
    entries: set[str] = set()
    for bucket in sorted(root.glob("wheels-v*")) + sorted(root.glob("simple-v*")):
        for source in sorted(p for p in bucket.iterdir() if p.is_dir()):
            parents = [source]
            if source.name in ("index", "url"):
                parents = sorted(p for p in source.iterdir() if p.is_dir())
            for parent in parents:
                for item in parent.iterdir():
                    rel = parent.relative_to(root).as_posix()
                    entries.add(f"{rel}/{_normal(item.name)}")
    return sorted(entries)


def _venv_state(env: dict[str, str]) -> dict[str, Any]:
    done = _child(
        [
            "uv",
            "pip",
            "list",
            "--offline",
            "--python",
            str(VENV_PYTHON),
            "--format",
            "json",
        ],
        env,
    )
    return {
        "pip_list_exit": done.returncode,
        "pip_list": json.loads(done.stdout) if done.returncode == 0 else done.stderr.strip(),
        "pyproject.toml": _sha256(REPO_ROOT / "pyproject.toml"),
        "uv.lock": _sha256(REPO_ROOT / "uv.lock"),
    }


def _site_dists() -> list[str]:
    if not E5_SITE.is_dir():
        return []
    return sorted(p.name for p in E5_SITE.iterdir() if p.name.endswith(".dist-info"))


def run_e5_step(levels: list[str], failing: list[str], fetch_env: dict[str, str]) -> dict[str, Any]:
    """E5's install child, then its offline run child, with the plan's S5 checks."""
    path = _experiment_path("e5")
    offline_env = dict(os.environ)
    result: dict[str, Any] = {"id": "e5", "status": "run", "started": _now(), "s5": []}
    root = _cache_root(offline_env)
    result["cache_root"] = str(root)
    before = cache_inventory(root)
    result["venv_before"] = _venv_state(offline_env)
    requirements = "\n".join(E5_PINS) + "\n"
    E5_REQUIREMENTS.parent.mkdir(parents=True, exist_ok=True)
    E5_REQUIREMENTS.write_text(requirements, encoding="utf-8", newline="\n")
    result["requirements"] = requirements
    dists = _site_dists()
    if dists and set(dists) == E5_DISTS:
        result["install"] = {"skipped": "e5-site already holds exactly the two distributions"}
    elif dists:
        result.update(status="not_run", error=f"e5-site holds other distributions: {dists}")
    else:
        command = [
            "uv",
            "pip",
            "install",
            "--no-config",
            "--default-index",
            "https://pypi.org/simple",
            "--no-deps",
            "--require-hashes",
            "--only-binary",
            ":all:",
            "--python",
            str(VENV_PYTHON),
            "--target",
            str(E5_SITE),
            "-r",
            str(E5_REQUIREMENTS),
        ]
        done = _child(command, fetch_env)
        result["install"] = {
            "command": command,
            "exit": done.returncode,
            "stdout": done.stdout,
            "stderr": done.stderr,
        }
        if done.returncode:
            result.update(status="not_run", error=f"install exited {done.returncode}")
    result["site_dists"] = _site_dists()
    if result["status"] == "run":
        run_env = dict(offline_env, PYTHONPATH=str(E5_SITE))
        done = _child(
            [
                "uv",
                "run",
                "--offline",
                "--no-sync",
                "python",
                str(Path(__file__).resolve()),
                "e5",
                "--levels",
                json.dumps(levels),
                "--failing",
                json.dumps(failing),
            ],
            run_env,
        )
        result["run_child"] = {"exit": done.returncode, "stderr_tail": _tail(done.stderr)}
        if E5_RUN.is_file():
            result["run"] = json.loads(E5_RUN.read_text(encoding="utf-8"))
        if done.returncode or "run" not in result:
            result.update(status="not_run", error=f"e5 run child exited {done.returncode}")
    after = cache_inventory(root)
    result["venv_after"] = _venv_state(offline_env)
    new = sorted(set(after) - set(before))
    result["cache_new"] = new
    result["cache_removed"] = sorted(set(before) - set(after))
    s5 = result["s5"]
    stray = [entry for entry in new if entry.rsplit("/", 1)[1] not in E5_CACHE_NAMES]
    if stray:
        s5.append(f"new uv cache entries outside onnx and ml-dtypes: {stray}")
    if result["site_dists"] and set(result["site_dists"]) != E5_DISTS:
        s5.append(f"e5-site holds {result['site_dists']}, expected {sorted(E5_DISTS)}")
    for key in ("pip_list", "pyproject.toml", "uv.lock"):
        if result["venv_before"][key] != result["venv_after"][key]:
            s5.append(f"the project's {key} changed during E5")
    result["finished"] = _now()
    _write(path, result)
    return result


def e5_child(levels: list[str], failing: list[str]) -> dict[str, Any]:
    """Run in the e5-site child: find the first non-finite node output for each failing pair."""
    # onnx and ml_dtypes resolve only from e5-site, through the child's PYTHONPATH.
    import ml_dtypes  # pyright: ignore[reportMissingImports]
    import numpy
    import onnx  # pyright: ignore[reportMissingImports]
    import onnxruntime as ort
    from google import protobuf
    from onnx import numpy_helper  # pyright: ignore[reportMissingImports]

    result: dict[str, Any] = {"started": _now(), "modules": {}}
    site = E5_SITE.resolve()
    venv = (REPO_ROOT / ".venv").resolve()
    for module, home in (
        (onnx, site),
        (ml_dtypes, site),
        (numpy, venv),
        (protobuf, venv),
        (ort, venv),
    ):
        file = Path(str(module.__file__)).resolve()
        result["modules"][module.__name__] = {
            "version": getattr(module, "__version__", None),
            "file": str(file),
        }
        if not file.is_relative_to(home):
            raise RuntimeError(f"{module.__name__} loaded from {file}, expected under {home}")
    if ort.__version__ != LOCKED_ORT:
        raise RuntimeError(f"onnxruntime {ort.__version__} loaded, expected {LOCKED_ORT}")

    model = onnx.load(str(FP16))
    graph = model.graph
    final = graph.output[0].name
    declared = {out.name for out in graph.output}
    order: list[str] = []
    producer: dict[str, Any] = {}
    for node in graph.node:
        for out in node.output:
            if out and out not in producer:
                producer[out] = node
                order.append(out)
    graph.output.extend(onnx.ValueInfoProto(name=out) for out in order if out not in declared)
    onnx.save(model, str(E5_MODEL))
    initializers = {init.name: init for init in graph.initializer}
    feeds_by_name = {inp.name for inp in graph.input}
    result.update(model=str(E5_MODEL), nodes=len(graph.node), outputs=len(order), final=final)

    feeder = Feeder()
    by_key = {
        f"{v}#{i}": (v, ps) for v, i, ps in _pairs(json.loads(PHONEMES.read_text(encoding="utf-8")))
    }
    tried: list[dict[str, Any]] = []
    session = None
    reproduced = False
    types: dict[str, str | None] = {}
    for level in [*levels, "ORT_ENABLE_ALL"]:
        candidate = _session(E5_MODEL, {"graph_optimization_level": level})
        types = {o.name: o.type for o in candidate.get_outputs()}
        hits = []
        for key in failing:
            voice, phonemes = by_key[key]
            for symbols in feeder.chunks(phonemes):
                audio = candidate.run([final], feeder.feeds(voice, feeder.ids(symbols)))[0]
                if _nonfinite(audio):
                    hits.append(key)
                    break
        tried.append({"level": level, "reproduced": hits})
        if hits:
            session, reproduced = candidate, True
            result["level"] = level
            break
    result["levels_tried"] = tried
    result["reproduced"] = reproduced
    if session is None:
        result["finished"] = _now()
        return result

    # An output whose type ORT didn't infer is scanned too; `_float_nonfinite` reads its dtype.
    scan = [out for out in order if out in types and types[out] in (*FLOAT_TYPES, None, "")]
    result["scanned"] = len(scan)
    rows = []
    for key in failing:
        voice, phonemes = by_key[key]
        for chunk_index, symbols in enumerate(feeder.chunks(phonemes)):
            feeds = feeder.feeds(voice, feeder.ids(symbols))
            first = None
            for start in range(0, len(scan), E5_BATCH):
                names = scan[start : start + E5_BATCH]
                values = session.run(names, feeds)
                bad = [n for n, v in zip(names, values, strict=True) if _float_nonfinite(v)]
                if bad:
                    first = bad[0]
                    break
            row: dict[str, Any] = {"key": key, "chunk": chunk_index, "first": None}
            if first is not None:
                node = producer[first]
                inputs = []
                fetch = [name for name in node.input if name in producer]
                fetched = dict(zip(fetch, session.run(fetch, feeds), strict=True)) if fetch else {}
                for name in node.input:
                    if not name:
                        continue
                    if name in fetched:
                        value, origin = fetched[name], "node"
                    elif name in initializers:
                        value, origin = numpy_helper.to_array(initializers[name]), "initializer"
                    elif name in feeds_by_name:
                        value, origin = feeds[name], "input"
                    else:
                        inputs.append({"name": name, "origin": "unknown"})
                        continue
                    array = np.asarray(value)
                    floating = array.dtype.kind == "f"
                    finite = array[np.isfinite(array)] if floating else array
                    peak = float(np.max(np.abs(finite))) if finite.size else None
                    inputs.append(
                        {
                            "name": name,
                            "origin": origin,
                            "dtype": str(array.dtype),
                            "shape": list(array.shape),
                            "nonfinite": _nonfinite(array) if floating else 0,
                            "max_abs_finite": peak,
                        }
                    )
                row["first"] = {
                    "output": first,
                    "op_type": node.op_type,
                    "name": node.name,
                    "inputs": inputs,
                }
            rows.append(row)
    result["pairs"] = rows
    result["finished"] = _now()
    return result


class Spike:
    """`all`: the experiments in order, the box, the candidate check and the summary."""

    def __init__(self, e5: bool) -> None:
        self.e5 = e5
        self.summary: dict[str, Any] = {
            "started": _now(),
            "box_seconds": BOX_S,
            "experiments": {},
            "stop": None,
            "candidate": None,
            "s5": [],
        }
        self.box_started = 0.0

    def boxed(self) -> bool:
        return time.time() - self.box_started >= BOX_S

    def record(self, exp_id: str, result: dict[str, Any]) -> None:
        entry: dict[str, Any] = {"status": result["status"]}
        if result["status"] == "not_run":
            entry["error"] = result.get("error")
        if "failing_count" in result:
            entry["failing"] = result["failing_count"]
        self.summary["experiments"][exp_id] = entry

    def mark(self, exp_ids: list[str], status: str, error: str | None = None) -> None:
        for exp_id in exp_ids:
            entry: dict[str, Any] = {"status": status}
            if error:
                entry["error"] = error
            self.summary["experiments"][exp_id] = entry

    def check_candidate(self, exp_id: str, options: dict[str, Any], version: str) -> bool:
        """Re-run E0's control, then the clean setting: a cause when both hold again."""
        control = run_pairs(f"e0-control-for-{exp_id}", {}, LOCKED_ORT)
        self.record(f"e0-control-for-{exp_id}", control)
        if version == LOCKED_ORT:
            again = run_pairs(f"{exp_id}-again", options, LOCKED_ORT)
        else:
            again = run_e2(version, f"{exp_id}-again")
        self.record(f"{exp_id}-again", again)
        cause = bool(control.get("failing_count")) and again.get("failing_count") == 0
        self.summary["candidate"] = {
            "id": exp_id,
            "options": options,
            "onnxruntime": version,
            "control_failing": control.get("failing_count"),
            "again_failing": again.get("failing_count"),
            "cause": cause,
        }
        return cause

    def run(self) -> dict[str, Any]:
        fetch_env = dict(os.environ)
        os.environ.update(_dead_proxy_env(dict(os.environ)))
        for stale in RECEIPTS.glob("s52-spike-*.json"):
            stale.unlink()
        phonemes = phonemize()
        self.box_started = datetime.fromisoformat(phonemes["started"]).timestamp()
        self.summary["box_started"] = phonemes["started"]
        self.summary["en_core_web_sm"] = phonemes["en_core_web_sm"]

        plan: list[tuple[str, dict[str, Any], str]] = [
            *[
                (f"e1-{lvl.lower()}", {"graph_optimization_level": lvl}, LOCKED_ORT)
                for lvl in E1_LEVELS
            ],
            *[(f"e2-{v}", {}, v) for v in E2_VERSIONS],
            ("e3", {}, LOCKED_ORT),
            *[(exp_id, options, LOCKED_ORT) for exp_id, options in E4_SETTINGS.items()],
        ]
        if self.e5:
            plan.append(("e5", {}, LOCKED_ORT))
        remaining = ["e0", *[exp_id for exp_id, _, _ in plan]]

        if self.boxed():
            self.summary["stop"] = "box"
            self.mark(remaining, "boxed")
            return self.finish()
        e0 = run_pairs("e0", {}, LOCKED_ORT)
        self.record("e0", e0)
        remaining.remove("e0")
        reproduced = self.reproduces(e0)
        self.summary["e0_reproduces_rate_probe"] = reproduced
        if not reproduced:
            self.summary["stop"] = "control"
            self.mark(remaining, "not_run", "E0 did not reproduce the rate probe")
            return self.finish()
        failing = list(e0["failing"])
        levels_reproduced: list[str] = []

        for exp_id, options, version in plan:
            if self.boxed():
                self.summary["stop"] = "box"
                self.mark(remaining, "boxed")
                return self.finish()
            remaining.remove(exp_id)
            if exp_id == "e3":
                result = run_e3(failing)
            elif exp_id == "e5":
                result = run_e5_step(levels_reproduced, failing, fetch_env)
                self.summary["s5"] = result["s5"]
                e5_run = result.get("run", {})
                self.summary["e5"] = {
                    "level": e5_run.get("level"),
                    "reproduced": e5_run.get("reproduced"),
                    "first": [
                        {
                            "key": row["key"],
                            "op_type": (row["first"] or {}).get("op_type"),
                            "name": (row["first"] or {}).get("name"),
                        }
                        for row in e5_run.get("pairs", [])
                    ],
                }
            elif exp_id.startswith("e2-"):
                result = run_e2(version)
            else:
                result = run_pairs(exp_id, options, version)
            self.record(exp_id, result)
            if self.summary["s5"]:
                self.summary["stop"] = "done"
                self.mark(remaining, "not_run", "the spike stopped at an S5 mark")
                return self.finish()
            if exp_id.startswith("e1-") and result.get("failing_count"):
                levels_reproduced.append(options["graph_optimization_level"])
            clean = result["status"] == "run" and result.get("failing_count") == 0
            if (
                clean
                and exp_id not in ("e3", "e5")
                and self.check_candidate(exp_id, options, version)
            ):
                self.summary["stop"] = "cause"
                self.mark(remaining, "not_run", "the spike stopped at a cause")
                return self.finish()
        self.summary["stop"] = "done"
        return self.finish()

    @staticmethod
    def reproduces(e0: dict[str, Any]) -> bool:
        if e0["status"] != "run":
            return False
        rows = e0["pairs"]
        for voice in AMERICAN:
            got = sorted(r["phoneme_chars"] for r in rows if r["voice"] == voice and r["nonfinite"])
            if got != sorted(RATE_PROBE[voice]):  # type: ignore[arg-type]
                return False
        emma = sum(1 for r in rows if r["voice"] == "bf_emma" and r["nonfinite"])
        return emma == RATE_PROBE["bf_emma"]

    def finish(self) -> dict[str, Any]:
        self.summary["finished"] = _now()
        _write(SUMMARY, self.summary)
        print(json.dumps(self.summary, indent=2, ensure_ascii=False))
        return self.summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Session 52 FP16 spike (MEU-121).")
    sub = parser.add_subparsers(dest="command", required=True)
    every = sub.add_parser("all")
    every.add_argument("--e5", action="store_true")
    sub.add_parser("phonemize")
    one = sub.add_parser("run")
    one.add_argument("--id", required=True)
    one.add_argument("--expect-ort", required=True)
    e5 = sub.add_parser("e5")
    e5.add_argument("--levels", required=True)
    e5.add_argument("--failing", required=True)
    args = parser.parse_args(argv)
    if args.command == "all":
        Spike(args.e5).run()
    elif args.command == "phonemize":
        phonemize()
    elif args.command == "run":
        run_pairs(args.id, {}, args.expect_ort)
    else:
        result = e5_child(json.loads(args.levels), json.loads(args.failing))
        _write(E5_RUN, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
