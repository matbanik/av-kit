"""Packaged TTS smoke for the frozen backend (MEU-72 `PACKAGE_SMOKE`).

`--phase online` is `ONLINE_PROVISION`. It builds the onedir with `tools/package_backend.py`
(never `--stub-ok`) and checks that `_internal` has no torch, kokoro, phonemizer or
espeakng_loader. It then starts the frozen backend and downloads the ONNX model, vocab, spaCy model
and voice packs into `--models-dir`. Network is allowed in this phase, and no generate runs.

`--phase offline` is `OFFLINE_SMOKE` plus `NEGATIVE_PROBE`. It starts the backend copy in
`--backend-dir` (the installer's own, copied outside the checkout by `validate-task.ps1`) in a fresh
process with every proxy pointed at a dead port. It loads `kokoro-onnx-int8` on CPU and generates
one English WAV from the cached models. A voice-pack download into an empty folder must then fail,
which proves that the dead proxies held.

`--phase capability` is `CAPABILITY_SMOKE` (MEU-117). It starts the backend copy in `--backend-dir`
behind the same dead proxies, with a 16-byte stub PyTorch weights file and a vocab in an empty
`--models-dir`. It checks, stopping at the first failure, that the PyTorch row is listed
unavailable with its reason (`listed_fields`), that its download answers 409 and writes nothing
(`download_refused`), that its load answers 422 (`load_refused`), and that the backend logs both
refusals (`logged`).

`--phase sentences` is MEU-121's sentence smoke (D-332). It starts the backend copy in
`--backend-dir` behind the same dead proxies, with `--models-dir` as the models folder. It registers
`--variant`, loads it on CPU once and runs the `--test-set` jobs one at a time: each sentence with
each of its voices, then the paragraphs and the passage. Each job sends no cleanup steps, so the
text reaches the model as written. It passes only when every job ends `Done` with a WAV of more
than 0 samples in the run folder, and it lists each failure's kind, index, voice and
`error_message`.

Each phase writes one JSON object to `--out`; `validate-task.ps1 -Check package-smoke` merges them.
Exit 0 means the phase passed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import wave
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "packaging" / "dist" / "avkit-backend"
EXE_NAME = "avkit-backend.exe"
MIN_EXE_BYTES = 1_000_000
FORBIDDEN_DIRS = ("torch", "kokoro", "phonemizer", "espeakng_loader")
READY_RE = re.compile(r"AVKIT_READY port=(\d+) instance=(\S+)")
VARIANT_ID = "kokoro-onnx-int8"
ASSETS = ("tts_onnx_vocab", "tts_spacy_model", "tts_voice_packs")
DEAD_PROXY = "http://127.0.0.1:9"
PROXY_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY")
SMOKE_TEXT = "Hello from av-kit."
SMOKE_VOICE = "af_heart"
MIN_WAV_SAMPLES = 8000
READY_TIMEOUT_S = 120.0
DOWNLOAD_TIMEOUT_S = 1800.0
GENERATE_TIMEOUT_S = 300.0
PROBE_TIMEOUT_S = 60.0
PYTORCH_VARIANT_ID = "kokoro-pt-fp32"
PYTORCH_STUB = "kokoro-v1_0.pth"
PYTORCH_STUB_BYTES = 16
REFUSAL_EVENTS = ("model.download_refused", "model.load_refused")
LOG_WAIT_S = 10.0


def _now() -> str:
    return datetime.now(UTC).isoformat()


class Backend:
    """One frozen backend process and a Bearer-authenticated JSON client for it."""

    def __init__(
        self, exe: Path, *, app_data: Path, cwd: Path, env: dict[str, str] | None = None
    ) -> None:
        self.token = secrets.token_hex(16)
        self.log: deque[str] = deque(maxlen=200)
        self._proc = subprocess.Popen(
            [
                str(exe),
                "--token",
                self.token,
                "--mcp-token",
                secrets.token_hex(16),
                "--port",
                "0",
                "--app-data",
                str(app_data),
            ],
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        self.port = self._wait_ready()
        threading.Thread(target=self._drain, daemon=True).start()
        # Localhost only, and never through a proxy (this process keeps its own environment).
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def _wait_ready(self) -> int:
        assert self._proc.stdout is not None
        deadline = time.monotonic() + READY_TIMEOUT_S
        while time.monotonic() < deadline:
            line = self._proc.stdout.readline()
            if not line:
                break
            self.log.append(line.rstrip())
            match = READY_RE.search(line)
            if match:
                return int(match.group(1))
        self.stop()
        raise RuntimeError(f"no AVKIT_READY line; output tail: {list(self.log)[-20:]}")

    def _drain(self) -> None:
        assert self._proc.stdout is not None
        for line in self._proc.stdout:
            self.log.append(line.rstrip())

    def request(self, method: str, path: str, body: Any = None) -> tuple[int, Any]:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/v1{path}",
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"},
        )
        try:
            with self._opener.open(req, timeout=60) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            try:
                return exc.code, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return exc.code, raw.decode("utf-8", "replace")

    def ok(self, method: str, path: str, body: Any = None) -> Any:
        status, payload = self.request(method, path, body)
        if status >= 400:
            raise RuntimeError(f"{method} {path} -> {status}: {payload}")
        return payload

    def put_tts_settings(self, **leaves: str) -> None:
        self.ok("PUT", "/settings/tts", leaves)

    def stop(self) -> None:
        if self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait(timeout=20)

    def tail(self, count: int = 40) -> list[str]:
        return list(self.log)[-count:]


def _wait_download(backend: Backend, timeout_s: float) -> dict[str, Any]:
    """Poll `download-runtime` until it leaves `Downloading`; return the last snapshot."""
    deadline = time.monotonic() + timeout_s
    runtime: dict[str, Any] = {}
    while time.monotonic() < deadline:
        runtime = backend.ok("GET", "/models/download-runtime")
        if runtime.get("state") != "Downloading":
            return runtime
        time.sleep(1.0)
    return {**runtime, "state": "Timeout"}


def _asset_states(backend: Backend) -> dict[str, str]:
    deps = backend.ok("GET", "/health/dependencies")
    return {asset: str(deps[asset]["state"]) for asset in ASSETS}


def _download_target(backend: Backend, body: dict[str, str]) -> dict[str, Any]:
    status, payload = backend.request("POST", "/models/download", body)
    if status == 409 and "already ready" in json.dumps(payload):
        return {"result": "already_ready"}
    if status != 202:
        return {"result": "rejected", "status": status, "detail": payload}
    runtime = _wait_download(backend, DOWNLOAD_TIMEOUT_S)
    state = runtime.get("state")
    return {
        "result": "downloaded" if state == "Idle" else "failed",
        "state": state,
        "error": runtime.get("error_message"),
    }


def _forbidden_dirs(internal: Path) -> list[str]:
    return [name for name in FORBIDDEN_DIRS if (internal / name).is_dir()]


def _fresh_home(env: dict[str, str], home: Path) -> str:
    """Point `~` at an empty folder, so the default `tts.models_directory` (`~/.avkit/models`)
    is empty. The backend activates that folder's spaCy install at startup, and a later
    settings change does not remove it from `sys.path`, so a real home would leak its assets in.
    """
    shutil.rmtree(home, ignore_errors=True)
    home.mkdir(parents=True)
    for name in ("HOME", "USERPROFILE"):
        env[name] = str(home)
    return str(home)


def phase_online(models_dir: Path) -> dict[str, Any]:
    result: dict[str, Any] = {"phase": "online", "passed": False, "started": _now(), "errors": []}
    errors: list[str] = result["errors"]
    built = time.monotonic()
    build = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "package_backend.py")],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    result["build"] = {
        "exit": build.returncode,
        "seconds": round(time.monotonic() - built, 1),
        "tail": (build.stdout + build.stderr).splitlines()[-15:],
    }
    exe = DIST_DIR / EXE_NAME
    result["exe_bytes"] = exe.stat().st_size if exe.is_file() else 0
    result["forbidden_dirs"] = _forbidden_dirs(DIST_DIR / "_internal")
    if build.returncode != 0:
        errors.append(f"package_backend.py exited {build.returncode}")
    if result["exe_bytes"] < MIN_EXE_BYTES:
        errors.append(f"{exe} is {result['exe_bytes']} bytes, a stub (< {MIN_EXE_BYTES})")
    if result["forbidden_dirs"]:
        errors.append(f"forbidden _internal dirs: {result['forbidden_dirs']}")
    if errors:
        result["finished"] = _now()
        return result

    models_dir.mkdir(parents=True, exist_ok=True)
    app_data = models_dir.parent / "s32-smoke-online-app-data"
    shutil.rmtree(app_data, ignore_errors=True)
    env = dict(os.environ)
    result["home"] = _fresh_home(env, models_dir.parent / "s32-smoke-online-home")
    backend = Backend(exe, app_data=app_data, cwd=DIST_DIR, env=env)
    try:
        backend.put_tts_settings(models_directory=str(models_dir))
        downloads: dict[str, Any] = {}
        downloaded = backend.ok("GET", "/models/downloaded")
        if any(item["id"] == VARIANT_ID for item in downloaded["items"]):
            downloads[VARIANT_ID] = {"result": "already_downloaded"}
        else:
            downloads[VARIANT_ID] = _download_target(backend, {"variant_id": VARIANT_ID})
        for asset in ASSETS:
            downloads[asset] = _download_target(backend, {"asset": asset})
        result["downloads"] = downloads
        result["asset_states"] = _asset_states(backend)
        downloaded = backend.ok("GET", "/models/downloaded")
        result["variant_downloaded"] = any(item["id"] == VARIANT_ID for item in downloaded["items"])
        for target, outcome in downloads.items():
            if outcome["result"] in ("failed", "rejected"):
                errors.append(f"{target}: {outcome}")
        if not result["variant_downloaded"]:
            errors.append(f"{VARIANT_ID} is not downloaded")
        for asset, state in result["asset_states"].items():
            if state != "ready":
                errors.append(f"{asset} is {state}, not ready")
    except Exception as exc:  # recorded in the result; the phase fails
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        backend.stop()
        result["backend_tail"] = backend.tail()
    result["passed"] = not errors
    result["finished"] = _now()
    return result


def _offline_env(run_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    env = dict(os.environ)
    # Not set on purpose: the dead proxies must be what stops traffic (D-88).
    for key in ("HF_HUB_OFFLINE", "TRANSFORMERS_OFFLINE"):
        env.pop(key, None)
    # The lower-case forms are set too, with the same values. Only the upper-case names are
    # recorded, because PowerShell's ConvertFrom-Json rejects keys that differ only in case.
    proxy: dict[str, str] = {}
    for key in PROXY_KEYS:
        env[key] = env[key.lower()] = proxy[key] = DEAD_PROXY
    env["NO_PROXY"] = env["no_proxy"] = proxy["NO_PROXY"] = "127.0.0.1,localhost"
    _fresh_home(env, run_dir / "home")
    for name, sub in (("HF_HOME", "hf-home"), ("XDG_CACHE_HOME", "xdg-cache")):
        path = run_dir / sub
        shutil.rmtree(path, ignore_errors=True)
        path.mkdir(parents=True)
        env[name] = str(path)
    return env, proxy


def _register_variant(backend: Backend, *, variant_id: str = VARIANT_ID) -> dict[str, Any]:
    """Record the cached weights in the fresh database through the download fast path.

    `/models/downloaded` finds the file on disk, but `/models/load` reads the database row,
    whose path is empty in a new app-data. The download returns at once for a file already at
    `variant_local_path`, with no network, which the dead proxies would otherwise expose.
    """
    return _download_target(backend, {"variant_id": variant_id})


def _generate(
    backend: Backend,
    out_dir: Path,
    *,
    variant_id: str = VARIANT_ID,
    text: str = SMOKE_TEXT,
    voice: str = SMOKE_VOICE,
    load: bool = True,
) -> dict[str, Any]:
    """Generate one WAV of `text` in `voice`, loading `variant_id` on CPU first when `load`."""
    if load:
        backend.ok("POST", "/models/load", {"variant_id": variant_id, "device": "cpu"})
    job = backend.ok(
        "POST",
        "/tts/generate",
        {
            "text": text,
            "voice": voice,
            "speed": 1.0,
            "format": "WAV",
            "enabled_steps": [],
        },
    )
    deadline = time.monotonic() + GENERATE_TIMEOUT_S
    while job["status"] in ("Pending", "Generating") and time.monotonic() < deadline:
        time.sleep(0.5)
        job = backend.ok("GET", f"/tts/{job['id']}")
    outcome: dict[str, Any] = {
        "status": job["status"],
        "error": job.get("error_message"),
        "output_path": job.get("output_path"),
        "wav_samples": 0,
    }
    path = Path(job["output_path"]) if job.get("output_path") else None
    if job["status"] == "Done" and path is not None and path.is_file():
        with wave.open(str(path), "rb") as wav:
            # The header's count alone passes a header-only file (review F2, D-343): count the
            # frames only when the payload holds every one of them.
            declared = wav.getnframes()
            payload = len(wav.readframes(declared))
            complete = payload == declared * wav.getsampwidth() * wav.getnchannels()
            outcome["wav_declared"] = declared
            outcome["wav_samples"] = declared if complete else 0
            outcome["sample_rate"] = wav.getframerate()
        outcome["inside_out_dir"] = path.resolve().is_relative_to(out_dir.resolve())
    return outcome


def _negative_probe(backend: Backend, run_dir: Path, models_dir: Path) -> dict[str, Any]:
    probe_dir = run_dir / "probe-models"
    shutil.rmtree(probe_dir, ignore_errors=True)
    probe_dir.mkdir(parents=True)
    backend.put_tts_settings(models_directory=str(probe_dir))
    try:
        status, payload = backend.request("POST", "/models/download", {"asset": "tts_voice_packs"})
        if status != 202:
            return {"state": "Rejected", "error": f"{status}: {payload}"}
        runtime = _wait_download(backend, PROBE_TIMEOUT_S)
        probe = {"state": runtime.get("state"), "error": runtime.get("error_message")}
        if probe["state"] == "Idle":
            probe["packs_ready_after"] = _asset_states(backend)["tts_voice_packs"]
        return probe
    finally:
        backend.put_tts_settings(models_directory=str(models_dir))


def phase_offline(backend_dir: Path, models_dir: Path) -> dict[str, Any]:
    run_dir = backend_dir.parent
    result: dict[str, Any] = {
        "phase": "offline",
        "passed": False,
        "started": _now(),
        "backend_dir": str(backend_dir.resolve()),
        "cwd": str(run_dir.resolve()),
        "wav_samples": 0,
        "negative_probe": {"state": None, "error": None},
        "errors": [],
    }
    errors: list[str] = result["errors"]
    if backend_dir.resolve().is_relative_to(REPO_ROOT):
        errors.append(f"backend_dir {backend_dir} is inside the checkout {REPO_ROOT}")
    exe = backend_dir / EXE_NAME
    if not exe.is_file():
        errors.append(f"missing {exe}")
    if errors:
        result["finished"] = _now()
        return result

    env, proxy = _offline_env(run_dir)
    result["proxy"] = proxy
    result["proxy_lower_case_set"] = all(env[key.lower()] == DEAD_PROXY for key in PROXY_KEYS)
    result["home"] = env["USERPROFILE"]
    result["hf_home"] = env["HF_HOME"]
    app_data = run_dir / "app-data"
    shutil.rmtree(app_data, ignore_errors=True)
    out_dir = run_dir / "out"
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    backend = Backend(exe, app_data=app_data, cwd=run_dir, env=env)
    try:
        backend.put_tts_settings(models_directory=str(models_dir), output_path=str(out_dir))
        result["register"] = _register_variant(backend)
        if result["register"]["result"] != "downloaded":
            raise RuntimeError(f"registering {VARIANT_ID} failed: {result['register']}")
        result["asset_states"] = _asset_states(backend)
        started = time.monotonic()
        generated = _generate(backend, out_dir)
        generated["seconds"] = round(time.monotonic() - started, 1)
        result["generate"] = generated
        result["wav_samples"] = generated["wav_samples"]
        if generated["status"] != "Done":
            errors.append(f"generate ended {generated['status']}: {generated['error']}")
        elif generated["wav_samples"] <= MIN_WAV_SAMPLES:
            errors.append(f"WAV has {generated['wav_samples']} samples (<= {MIN_WAV_SAMPLES})")
        probe = _negative_probe(backend, run_dir, models_dir)
        result["negative_probe"] = probe
        if probe["state"] != "Failed" or not probe.get("error"):
            errors.append(f"NEGATIVE_PROBE did not fail closed: {probe}")
    except Exception as exc:  # recorded in the result; the phase fails
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        backend.stop()
        result["backend_tail"] = backend.tail()
    result["passed"] = not errors
    result["finished"] = _now()
    return result


def _tree(root: Path) -> list[list[Any]]:
    """Each path under `root` with its size and mtime (directories have neither)."""
    rows: list[list[Any]] = []
    for path in sorted(root.rglob("*")):
        stat = path.stat()
        if path.is_dir():
            rows.append([path.relative_to(root).as_posix() + "/", None, None])
        else:
            rows.append([path.relative_to(root).as_posix(), stat.st_size, stat.st_mtime_ns])
    return rows


def _error_fields(payload: Any) -> tuple[Any, Any]:
    error = payload.get("error") if isinstance(payload, dict) else None
    if not isinstance(error, dict):
        return None, None
    return error.get("code"), error.get("message")


def _check_listed(
    backend: Backend, reason: str, seed_ids: list[str]
) -> tuple[dict[str, Any], list[str]]:
    items = backend.ok("GET", "/models/available")["items"]
    seen = {
        item["id"]: {
            key: item.get(key, "<absent>") for key in ("available", "reason", "is_downloaded")
        }
        for item in items
    }
    problems: list[str] = []
    if sorted(seen) != sorted(seed_ids):
        problems.append(f"listed {sorted(seen)}, not the seeded {sorted(seed_ids)}")
    pytorch = seen.get(PYTORCH_VARIANT_ID)
    if pytorch != {"available": False, "reason": reason, "is_downloaded": True}:
        problems.append(f"{PYTORCH_VARIANT_ID} reads {pytorch}")
    for variant_id, row in seen.items():
        if variant_id != PYTORCH_VARIANT_ID and (row["available"], row["reason"]) != (True, None):
            problems.append(f"{variant_id} reads {row}")
    return seen, problems


def _check_download_refused(
    backend: Backend, reason: str, models_dir: Path
) -> tuple[dict[str, Any], list[str]]:
    before = _tree(models_dir)
    status, payload = backend.request(
        "POST", "/models/download", {"variant_id": PYTORCH_VARIANT_ID}
    )
    code, message = _error_fields(payload)
    runtime = backend.ok("GET", "/models/download-runtime")
    after = _tree(models_dir)
    seen = {
        "status": status,
        "code": code,
        "message": message,
        "runtime_state": runtime.get("state"),
        "files_unchanged": after == before,
    }
    problems: list[str] = []
    if (status, code, message) != (409, "ConflictError", reason):
        problems.append(f"download answered {status} {code}: {message}")
    if seen["runtime_state"] != "Idle":
        problems.append(f"download runtime reads {seen['runtime_state']}, not Idle")
    if not seen["files_unchanged"]:
        problems.append(f"models_dir changed: {before} -> {after}")
    return seen, problems


def _check_load_refused(
    backend: Backend, reason: str, stub: Path
) -> tuple[dict[str, Any], list[str]]:
    status, payload = backend.request(
        "POST", "/models/load", {"variant_id": PYTORCH_VARIANT_ID, "device": "cpu"}
    )
    code, message = _error_fields(payload)
    rows = {item["id"]: item for item in backend.ok("GET", "/models/available")["items"]}
    seen = {
        "status": status,
        "code": code,
        "message": message,
        "stub_bytes": stub.stat().st_size if stub.is_file() else None,
        "is_downloaded": rows.get(PYTORCH_VARIANT_ID, {}).get("is_downloaded"),
    }
    problems: list[str] = []
    if (status, code, message) != (422, "ModelLoadError", reason):
        problems.append(f"load answered {status} {code}: {message}")
    if seen["stub_bytes"] != PYTORCH_STUB_BYTES:
        problems.append(f"the stub reads {seen['stub_bytes']} bytes, not {PYTORCH_STUB_BYTES}")
    if seen["is_downloaded"] is not True:
        problems.append(f"{PYTORCH_VARIANT_ID} is_downloaded reads {seen['is_downloaded']}")
    return seen, problems


def _check_logged(backend: Backend) -> tuple[dict[str, bool], list[str]]:
    # The drain thread reads the backend's output, so a line can land just after the response.
    deadline = time.monotonic() + LOG_WAIT_S
    while True:
        lines = list(backend.log)
        seen = {event: any(event in line for line in lines) for event in REFUSAL_EVENTS}
        if all(seen.values()) or time.monotonic() >= deadline:
            break
        time.sleep(0.25)
    return seen, [
        f"no {event} line in the backend output" for event, found in seen.items() if not found
    ]


def phase_capability(backend_dir: Path, models_dir: Path) -> dict[str, Any]:
    """`CAPABILITY_SMOKE`: the frozen backend lists and refuses a variant it can't run."""
    from avkit_core.domain.enums import ModelFormat
    from avkit_core.domain.tts import MODEL_REASONS
    from avkit_infra.database.engine import SEED_VARIANTS

    reason = MODEL_REASONS[ModelFormat.PyTorch]
    seed_ids = [row[0] for row in SEED_VARIANTS]
    run_dir = backend_dir.parent
    result: dict[str, Any] = {
        "phase": "capability",
        "passed": False,
        "started": _now(),
        "backend_dir": str(backend_dir.resolve()),
        "models_dir": str(models_dir.resolve()),
        "checks": {},
        "failed_check": None,
        "errors": [],
    }
    errors: list[str] = result["errors"]
    real_models = (Path.home() / ".avkit" / "models").resolve()
    if backend_dir.resolve().is_relative_to(REPO_ROOT):
        errors.append(f"backend_dir {backend_dir} is inside the checkout {REPO_ROOT}")
    for root, label in ((REPO_ROOT, "the checkout"), (real_models, "the real models folder")):
        if models_dir.resolve().is_relative_to(root):
            errors.append(f"models_dir {models_dir} is inside {label} {root}")
    if models_dir.exists() and (not models_dir.is_dir() or any(models_dir.iterdir())):
        errors.append(f"models_dir {models_dir} exists and is not an empty folder")
    exe = backend_dir / EXE_NAME
    if not exe.is_file():
        errors.append(f"missing {exe}")
    if not errors:
        result["forbidden_dirs"] = _forbidden_dirs(backend_dir / "_internal")
        if result["forbidden_dirs"]:
            errors.append(f"forbidden _internal dirs: {result['forbidden_dirs']}")
    if errors:
        result["finished"] = _now()
        return result

    models_dir.mkdir(parents=True, exist_ok=True)
    stub = models_dir / PYTORCH_STUB
    stub.write_bytes(bytes(PYTORCH_STUB_BYTES))
    # A vocab, so the PyTorch row reads downloaded (a variant needs a valid vocab to).
    (models_dir / "config.json").write_text(json.dumps({"vocab": {"a": 1}}), encoding="utf-8")
    env, proxy = _offline_env(run_dir)
    result["proxy"] = proxy
    app_data = run_dir / "app-data"
    shutil.rmtree(app_data, ignore_errors=True)
    backend = Backend(exe, app_data=app_data, cwd=run_dir, env=env)
    checks: list[tuple[str, Callable[[], tuple[Any, list[str]]]]] = [
        ("listed_fields", lambda: _check_listed(backend, reason, seed_ids)),
        ("download_refused", lambda: _check_download_refused(backend, reason, models_dir)),
        ("load_refused", lambda: _check_load_refused(backend, reason, stub)),
        ("logged", lambda: _check_logged(backend)),
    ]
    try:
        backend.put_tts_settings(models_directory=str(models_dir))
        for name, check in checks:
            try:
                seen, problems = check()
            except Exception as exc:  # recorded as this check's failure
                seen, problems = None, [f"{type(exc).__name__}: {exc}"]
            result["checks"][name] = seen
            if problems:
                result["failed_check"] = name
                errors.extend(f"{name}: {problem}" for problem in problems)
                break
    except Exception as exc:  # recorded in the result; the phase fails
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        backend.stop()
        result["backend_tail"] = backend.tail()
    result["passed"] = not errors
    result["finished"] = _now()
    return result


def _sentence_jobs(test_set: dict[str, Any]) -> list[tuple[str, int, str, str]]:
    """The test set's jobs as (kind, index, voice, text), in the order they run."""
    sentences = list(test_set["sentences"])
    voices = test_set["voices"]
    groups = (
        ("sentence", sentences, voices["sentences"]),
        ("sentence", sentences[:20], voices["sentences_first_20"]),
        ("paragraph", list(test_set["paragraphs"]), voices["paragraphs"]),
        ("passage", [test_set["passage"]], voices["passage"]),
    )
    return [
        (kind, index, voice, text)
        for kind, texts, group_voices in groups
        for voice in group_voices
        for index, text in enumerate(texts)
    ]


def phase_sentences(
    backend_dir: Path, models_dir: Path, test_set: Path, variant_id: str
) -> dict[str, Any]:
    """MEU-121's sentence smoke: each test-set job on `variant_id` ends `Done` with audio."""
    run_dir = backend_dir.parent
    result: dict[str, Any] = {
        "phase": "sentences",
        "passed": False,
        "started": _now(),
        "backend_dir": str(backend_dir.resolve()),
        "models_dir": str(models_dir.resolve()),
        "test_set": str(test_set.resolve()),
        "variant_id": variant_id,
        "jobs": 0,
        "failures": [],
        "errors": [],
    }
    errors: list[str] = result["errors"]
    failures: list[dict[str, Any]] = result["failures"]
    real_models = (Path.home() / ".avkit" / "models").resolve()
    if backend_dir.resolve().is_relative_to(REPO_ROOT):
        errors.append(f"backend_dir {backend_dir} is inside the checkout {REPO_ROOT}")
    for root, label in ((REPO_ROOT, "the checkout"), (real_models, "the real models folder")):
        if models_dir.resolve().is_relative_to(root):
            errors.append(f"models_dir {models_dir} is inside {label} {root}")
    exe = backend_dir / EXE_NAME
    if not exe.is_file():
        errors.append(f"missing {exe}")
    if not errors:
        result["forbidden_dirs"] = _forbidden_dirs(backend_dir / "_internal")
        if result["forbidden_dirs"]:
            errors.append(f"forbidden _internal dirs: {result['forbidden_dirs']}")
    if errors:
        result["finished"] = _now()
        return result

    jobs = _sentence_jobs(json.loads(test_set.read_text(encoding="utf-8")))
    env, proxy = _offline_env(run_dir)
    result["proxy"] = proxy
    app_data = run_dir / "app-data"
    shutil.rmtree(app_data, ignore_errors=True)
    out_dir = run_dir / "out"
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    # One row per job run: kind, index, voice, status, WAV samples and seconds.
    rows: list[list[Any]] = []
    backend = Backend(exe, app_data=app_data, cwd=run_dir, env=env)
    try:
        backend.put_tts_settings(models_directory=str(models_dir), output_path=str(out_dir))
        result["register"] = _register_variant(backend, variant_id=variant_id)
        if result["register"]["result"] != "downloaded":
            raise RuntimeError(f"registering {variant_id} failed: {result['register']}")
        result["asset_states"] = _asset_states(backend)
        backend.ok("POST", "/models/load", {"variant_id": variant_id, "device": "cpu"})
        for kind, index, voice, text in jobs:
            started = time.monotonic()
            outcome: dict[str, Any]
            try:
                outcome = _generate(backend, out_dir, text=text, voice=voice, load=False)
            except Exception as exc:  # recorded as this job's failure
                outcome = {"status": "Error", "error": f"{type(exc).__name__}: {exc}"}
            seconds = round(time.monotonic() - started, 1)
            samples = int(outcome.get("wav_samples", 0))
            rows.append([kind, index, voice, outcome["status"], samples, seconds])
            if outcome["status"] != "Done" or samples <= 0 or not outcome.get("inside_out_dir"):
                failures.append(
                    {
                        "kind": kind,
                        "index": index,
                        "voice": voice,
                        "status": outcome["status"],
                        "error_message": outcome.get("error"),
                        "wav_samples": samples,
                    }
                )
    except Exception as exc:  # recorded in the result; the phase fails
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        backend.stop()
        result["jobs"] = len(rows)
        result["results"] = rows
        result["backend_tail"] = backend.tail()
    result["passed"] = not errors and not failures and len(rows) == len(jobs)
    result["finished"] = _now()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--phase", choices=("online", "offline", "capability", "sentences"), required=True
    )
    parser.add_argument("--models-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--backend-dir", type=Path, help="offline, capability and sentences: the copied onedir"
    )
    parser.add_argument("--test-set", type=Path, help="sentences: the test-set JSON")
    parser.add_argument("--variant", help="sentences: the variant id to load")
    args = parser.parse_args(argv)
    if args.phase == "online":
        result = phase_online(args.models_dir)
    else:
        if args.backend_dir is None:
            parser.error(f"--phase {args.phase} requires --backend-dir")
        if args.phase == "offline":
            result = phase_offline(args.backend_dir, args.models_dir)
        elif args.phase == "sentences":
            if args.test_set is None or args.variant is None:
                parser.error("--phase sentences requires --test-set and --variant")
            result = phase_sentences(args.backend_dir, args.models_dir, args.test_set, args.variant)
        else:
            result = phase_capability(args.backend_dir, args.models_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "backend_tail"}, indent=2))
    print(("PASS" if result["passed"] else "FAIL") + f": smoke_packaged_tts {args.phase}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
