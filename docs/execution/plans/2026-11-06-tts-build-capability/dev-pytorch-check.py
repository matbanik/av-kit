"""Session 51 `DEV_CHECK` (implementation-plan.md §Packaged and dev checks; AC-117.16).

Usage: ``python dev-pytorch-check.py [--baseline]``, run from the repository root.

It starts the dev backend the way ``npm run dev`` does (``buildDevSpawnArgv``,
``ui/src/main/python-manager.ts:17-36``: ``python -m avkit_api --token --mcp-token --port 0
--app-data``) through ``DevBackend``, a subclass of the packaged smoke's ``Backend`` that keeps
its ready wait, drain, client and stop. The process gets fresh app data under ``RUN_DIR``, dead
proxies, ``HF_HUB_OFFLINE=1`` and ``PYTHONDONTWRITEBYTECODE=1``. The real ``~/.avkit/models`` is
its ``tts.models_directory``, and its output folder is under ``RUN_DIR``.

Before any download or load, the vocab, spaCy and voice packs must read ``ready`` there, so
nothing starts a download (S5). Then ``kokoro-pt-fp32`` must read ``available: true`` with
``reason: null``; its download answers 202 through the manager's fast path
(``model_manager/manager.py:54-72``), which writes nothing; the download runtime returns to
``Idle``; the load on ``cpu`` answers 200; and a short generate makes a WAV of more than 8000
samples. ``--baseline`` (row 0, before any change) lets the two fields be absent; a present
field must still hold the strict value. Exit 0 means the check passed.
"""

from __future__ import annotations

import json
import os
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import wave
from collections import deque
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from smoke_packaged_tts import (  # noqa: E402  (tools/ is not a package)
    DEAD_PROXY,
    MIN_WAV_SAMPLES,
    PROXY_KEYS,
    SMOKE_TEXT,
    SMOKE_VOICE,
    Backend,
    _asset_states,
    _now,
    _wait_download,
)

VARIANT_ID = "kokoro-pt-fp32"
MODELS_DIR = Path.home() / ".avkit" / "models"
RUN_DIR = Path("C:/Temp/av-kit/s51/dev-check")
FAST_PATH_TIMEOUT_S = 60.0
GENERATE_TIMEOUT_S = 300.0


class DevBackend(Backend):
    """The dev backend (``python -m avkit_api``); everything after the spawn is ``Backend``'s."""

    def __init__(self, *, app_data: Path, cwd: Path, env: dict[str, str]) -> None:
        self.token = secrets.token_hex(16)
        self.log: deque[str] = deque(maxlen=200)
        self._proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "avkit_api",
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
        self._opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _dev_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in PROXY_KEYS:
        env[key] = env[key.lower()] = DEAD_PROXY
    env["NO_PROXY"] = env["no_proxy"] = "127.0.0.1,localhost"
    env["HF_HUB_OFFLINE"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("ELECTRON_RUN_AS_NODE", None)
    return env


def _row_problems(row: dict[str, Any], baseline: bool) -> list[str]:
    problems: list[str] = []
    if row.get("is_downloaded") is not True:
        problems.append(f"{VARIANT_ID} is not downloaded in {MODELS_DIR}")
    for key, want in (("available", True), ("reason", None)):
        if key not in row:
            if not baseline:
                problems.append(f"{VARIANT_ID} has no {key!r} field")
        elif row[key] != want:
            problems.append(f"{VARIANT_ID} {key} is {row[key]!r}, not {want!r}")
    return problems


def _generate(backend: Backend, out_dir: Path) -> dict[str, Any]:
    job = backend.ok(
        "POST",
        "/tts/generate",
        {"text": SMOKE_TEXT, "voice": SMOKE_VOICE, "speed": 1.0, "format": "WAV", "enabled_steps": []},
    )
    deadline = time.monotonic() + GENERATE_TIMEOUT_S
    while job["status"] in ("Pending", "Generating") and time.monotonic() < deadline:
        time.sleep(0.5)
        job = backend.ok("GET", f"/tts/{job['id']}")
    outcome: dict[str, Any] = {"status": job["status"], "error": job.get("error_message"), "wav_samples": 0}
    path = Path(job["output_path"]) if job.get("output_path") else None
    if job["status"] == "Done" and path is not None and path.is_file():
        with wave.open(str(path), "rb") as wav:
            outcome["wav_samples"] = wav.getnframes()
            outcome["sample_rate"] = wav.getframerate()
        outcome["inside_out_dir"] = path.resolve().is_relative_to(out_dir.resolve())
    return outcome


def run(baseline: bool) -> dict[str, Any]:
    result: dict[str, Any] = {
        "check": "dev-pytorch",
        "mode": "baseline" if baseline else "strict",
        "passed": False,
        "started": _now(),
        "python": sys.executable,
        "models_dir": str(MODELS_DIR),
        "errors": [],
    }
    errors: list[str] = result["errors"]
    shutil.rmtree(RUN_DIR, ignore_errors=True)
    app_data, out_dir = RUN_DIR / "app-data", RUN_DIR / "out"
    out_dir.mkdir(parents=True)
    backend = DevBackend(app_data=app_data, cwd=REPO_ROOT, env=_dev_env())
    try:
        backend.put_tts_settings(models_directory=str(MODELS_DIR), output_path=str(out_dir))
        result["asset_states"] = states = _asset_states(backend)
        not_ready = {asset: state for asset, state in states.items() if state != "ready"}
        if not_ready:
            # Stop before any download or load could fetch them (S5).
            raise RuntimeError(f"assets not ready in {MODELS_DIR}: {not_ready}")
        listed = backend.ok("GET", "/models/available")["items"]
        row = next((item for item in listed if item["id"] == VARIANT_ID), None)
        if row is None:
            raise RuntimeError(f"{VARIANT_ID} is not listed")
        result["row"] = {k: row.get(k, "<absent>") for k in ("is_downloaded", "devices", "available", "reason")}
        errors += _row_problems(row, baseline)
        if errors:
            raise RuntimeError("the listed row is wrong; no download or load is attempted")
        status, payload = backend.request("POST", "/models/download", {"variant_id": VARIANT_ID})
        result["download_status"] = status
        if status != 202:
            raise RuntimeError(f"download answered {status}: {payload}")
        runtime = _wait_download(backend, FAST_PATH_TIMEOUT_S)
        result["download_runtime"] = {"state": runtime.get("state"), "error": runtime.get("error_message")}
        if runtime.get("state") != "Idle":
            raise RuntimeError(f"the download runtime ended {runtime.get('state')}, not Idle")
        status, payload = backend.request("POST", "/models/load", {"variant_id": VARIANT_ID, "device": "cpu"})
        result["load_status"] = status
        if status != 200:
            raise RuntimeError(f"load answered {status}: {payload}")
        result["model_status"] = backend.ok("GET", "/models/status")
        result["generate"] = generated = _generate(backend, out_dir)
        if generated["status"] != "Done":
            errors.append(f"generate ended {generated['status']}: {generated['error']}")
        elif generated["wav_samples"] <= MIN_WAV_SAMPLES:
            errors.append(f"WAV has {generated['wav_samples']} samples (<= {MIN_WAV_SAMPLES})")
        elif not generated.get("inside_out_dir"):
            errors.append("the WAV is outside the run's output folder")
    except Exception as exc:  # recorded in the result; the check fails
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        backend.stop()
        result["backend_tail"] = backend.tail()
    result["passed"] = not errors
    result["finished"] = _now()
    return result


def main(argv: list[str]) -> int:
    if argv not in ([], ["--baseline"]):
        print("usage: dev-pytorch-check.py [--baseline]")
        return 2
    result = run(baseline=argv == ["--baseline"])
    out = RUN_DIR / "result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "backend_tail"}, indent=2))
    if not result["passed"]:
        print("backend tail:")
        for line in result["backend_tail"]:
            print("  ", line)
    print(("PASS" if result["passed"] else "FAIL") + f": dev-pytorch-check {result['mode']}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
