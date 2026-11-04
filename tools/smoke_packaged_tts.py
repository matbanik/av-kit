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


def _register_variant(backend: Backend) -> dict[str, Any]:
    """Record the cached weights in the fresh database through the download fast path.

    `/models/downloaded` finds the file on disk, but `/models/load` reads the database row,
    whose path is empty in a new app-data. The download returns at once for a file already at
    `variant_local_path`, with no network, which the dead proxies would otherwise expose.
    """
    return _download_target(backend, {"variant_id": VARIANT_ID})


def _generate(backend: Backend, out_dir: Path) -> dict[str, Any]:
    backend.ok("POST", "/models/load", {"variant_id": VARIANT_ID, "device": "cpu"})
    job = backend.ok(
        "POST",
        "/tts/generate",
        {
            "text": SMOKE_TEXT,
            "voice": SMOKE_VOICE,
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
            outcome["wav_samples"] = wav.getnframes()
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--phase", choices=("online", "offline"), required=True)
    parser.add_argument("--models-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--backend-dir", type=Path, help="offline: the copied onedir to run")
    args = parser.parse_args(argv)
    if args.phase == "online":
        result = phase_online(args.models_dir)
    else:
        if args.backend_dir is None:
            parser.error("--phase offline requires --backend-dir")
        result = phase_offline(args.backend_dir, args.models_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "backend_tail"}, indent=2))
    print(("PASS" if result["passed"] else "FAIL") + f": smoke_packaged_tts {args.phase}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
