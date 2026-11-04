"""TTS_LIVE — real-network "audio actually comes out" check for 2026-09-30-tts-repair.

Runs the production service graph in-process (``avkit_api.wiring.build_services``) against a
throwaway app-data directory and a throwaway ``tts.models_directory``. It never touches
``~/.avkit``. It exercises the MEU-62 contract end to end with real Hugging Face and GitHub
downloads, then writes a ``s27-tts-live.v1`` JSON result that
``validate-task.sh tts-live-check`` validates.

It runs twice:

- non-authoritatively in the container, as ``validate-task.sh tts-live-pre`` inside ``pregate``;
- authoritatively on Windows, as ``validate-task.ps1 -Check tts-live``.

This script was written at plan time against the MEU-62 contract in ``implementation-plan.md``
(§Single-statement contracts, AC-62.2/62.6/62.7/62.8/62.10). Task row 5 keeps it in step with
the implemented API, and ``tts-live-pre`` proves it runs before any Windows request. It is in
``GATED_PATHS``.

Steps, in order (the ids are asserted by ``tts-live-check``):

1. ``fresh-rows`` — ``dependencies()`` reports both TTS asset rows as not ``ready`` on the
   empty models directory. If spaCy is already importable from the interpreter's own
   site-packages (checked before any service starts), the spaCy row is ``ready``; that is
   recorded as ``site_spacy`` and the step passes on the vocab row alone.

``~`` is redirected (``HOME`` and ``USERPROFILE``) to a throwaway directory under
``--app-data`` before the services start. The default ``tts.models_directory`` is
``~/.avkit/models``, and startup activates it before this script sets its own directory, so a
real user install there would otherwise leak onto ``sys.path`` (Session 27 WINDOWS_GATE
attempt 3).
2. ``variant-download`` — ``download("kokoro-onnx-int8")`` finishes and leaves a valid
   ``{models_dir}/config.json`` (the ``VOCAB_LOCATION``), and the variant lists as downloaded.
3. ``spacy-autoload`` — ``load`` starts the spaCy download (AC-62.7), and it reaches ``ready``
   within 300 s.
4. ``generate-wav`` — generating "Hello from av-kit." with voice ``am_eric`` to WAV, with the GUI
   default prepare steps (``PREPARE_DEFAULT_ON``, so ``chunk`` loads spaCy), ends ``Done`` with a
   WAV longer than 0.5 s whose RMS is above 0.
5. ``console-events`` — the console ring holds ``tts.generate`` and ``tts.generate_done``.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
import traceback
import wave
from array import array
from pathlib import Path
from typing import Any

# TTS_LIVE_STEPS: the single definition of the step ids and their order (validate-task.sh imports it).
STEP_IDS: tuple[str, ...] = ("fresh-rows", "variant-download", "spacy-autoload", "generate-wav", "console-events")
FRESH, VARIANT_DL, SPACY_AUTO, GENERATE, CONSOLE = STEP_IDS

VARIANT = "kokoro-onnx-int8"
VOICE = "am_eric"
TEXT = "Hello from av-kit."
DOWNLOAD_TIMEOUT_S = 900
SPACY_TIMEOUT_S = 300


def _wait_idle(models: Any, timeout_s: int) -> Any:
    """Poll the download runtime until it leaves ``Downloading``; raise on timeout."""
    deadline = time.monotonic() + timeout_s
    runtime = models.get_download_runtime()
    while runtime.state == "Downloading":
        if time.monotonic() > deadline:
            raise TimeoutError(f"download still running after {timeout_s}s: {runtime}")
        time.sleep(1.0)
        runtime = models.get_download_runtime()
    return runtime


def _row_state(deps: Any, name: str) -> str:
    """Read one TTS asset row's state from ``DependencyHealth`` (AC-62.8 field names).

    The domain row is the ``AssetState`` itself (only the wire ``TtsAssetOut`` wraps it with
    ``available`` / ``version``), so a ``.state`` attribute is read only when present.
    """
    row = getattr(deps, name)
    state = getattr(row, "state", row)
    return str(getattr(state, "value", state))


def _wav_observation(path: Path) -> dict[str, float]:
    """Return duration (s) and RMS of a 16-bit PCM WAV file."""
    with wave.open(str(path), "rb") as handle:
        frames = handle.readframes(handle.getnframes())
        rate = handle.getframerate()
        width = handle.getsampwidth()
        count = handle.getnframes()
    if width != 2:
        raise ValueError(f"expected 16-bit PCM, got sample width {width}")
    samples = array("h")
    samples.frombytes(frames)
    rms = math.sqrt(sum(s * s for s in samples) / len(samples)) if samples else 0.0
    return {"duration_s": round(count / rate, 3), "rms": round(rms, 2), "bytes": path.stat().st_size}


def main() -> int:
    """Run the five steps and write the result JSON; exit 1 on the first failed step."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--app-data", required=True, type=Path)
    parser.add_argument("--models-dir", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tested-commit", required=True)
    parser.add_argument("--clean-tree", required=True, choices=["true", "false"])
    args = parser.parse_args()

    result: dict[str, Any] = {
        "schema": "s27-tts-live.v1",
        "tested_commit": args.tested_commit,
        "clean_tree": args.clean_tree == "true",
        "models_directory": str(args.models_dir),
        "python": sys.version.split()[0],
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "steps": [],
    }

    def record(step_id: str, ok: bool, observed: object, error: str | None = None) -> None:
        result["steps"].append({"id": step_id, "ok": ok, "observed": observed, "error": error})
        print(f"{'PASS' if ok else 'FAIL'} {step_id}: {observed} {error or ''}", flush=True)

    code = 0
    home = args.app_data / "home"
    home.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(home)
    os.environ["USERPROFILE"] = str(home)
    site_spacy = importlib.util.find_spec("en_core_web_sm") is not None
    result["site_spacy"] = site_spacy
    try:
        from avkit_api.wiring import build_services
        from avkit_core.domain.enums import DeviceType, MediaFormat, TTSSourceKind
        from avkit_core.services.prepare import PREPARE_DEFAULT_ON, PREPARE_STEP_IDS

        services, dispose = build_services(app_data=args.app_data)
        try:
            settings = services.settings
            settings.set("tts", "models_directory", str(args.models_dir))  # type: ignore[attr-defined]
            settings.set("tts", "output_path", str(args.app_data / "tts-out"))  # type: ignore[attr-defined]
            health, models, tts = services.health, services.models, services.tts

            deps = health.dependencies()  # type: ignore[attr-defined]
            vocab0 = _row_state(deps, "tts_onnx_vocab")
            spacy0 = _row_state(deps, "tts_spacy_model")
            fresh = vocab0 == "missing" and (spacy0 == "missing" or site_spacy)
            record(FRESH, fresh, {"tts_onnx_vocab": vocab0, "tts_spacy_model": spacy0, "site_spacy": site_spacy})
            if not fresh:
                raise RuntimeError("stop after fresh-rows")

            models.download(VARIANT)
            runtime = _wait_idle(models, DOWNLOAD_TIMEOUT_S)
            vocab_path = args.models_dir / "config.json"
            vocab_ok = vocab_path.is_file() and isinstance(
                json.loads(vocab_path.read_text(encoding="utf-8")).get("vocab"), dict)
            listed = any(v.id == VARIANT and v.is_downloaded for v in models.list_available())
            ok = runtime.state == "Idle" and vocab_ok and listed
            record(VARIANT_DL, ok, {"runtime": runtime.state, "vocab_valid": vocab_ok, "listed": listed},
                   runtime.error_message)
            if not ok:
                raise RuntimeError("stop after variant-download")

            models.load(VARIANT, DeviceType.Auto)
            _wait_idle(models, SPACY_TIMEOUT_S)
            spacy1 = _row_state(health.dependencies(), "tts_spacy_model")  # type: ignore[attr-defined]
            autoload = spacy1 == "ready" and (spacy0 == "missing" or site_spacy)
            record(SPACY_AUTO, autoload, {"before": spacy0, "after": spacy1})
            if not autoload:
                raise RuntimeError("stop after spacy-autoload")

            steps = [s for s in PREPARE_STEP_IDS if s in PREPARE_DEFAULT_ON]  # GUI default order and set
            job = tts.generate(TEXT, VOICE, 1.0, MediaFormat.WAV, steps, TTSSourceKind.Inline, None)  # type: ignore[attr-defined]
            observed: dict[str, Any] = {"status": str(job.status), "error_message": job.error_message, "steps": steps}
            ok = str(job.status).endswith("Done") and job.output_path is not None
            if ok:
                observed.update(_wav_observation(Path(job.output_path)))
                ok = observed["duration_s"] > 0.5 and observed["rms"] > 0
            record(GENERATE, ok, observed, job.error_message)
            if not ok:
                raise RuntimeError("stop after generate-wav")

            messages = [e.message for e in health.console_snapshot(0)]  # type: ignore[attr-defined]
            seen = {name: any(m.split(" ", 1)[0] == name for m in messages)
                    for name in ("tts.generate", "tts.generate_done")}
            record(CONSOLE, all(seen.values()), seen)
            if not all(seen.values()):
                code = 1
        finally:
            dispose()
    except Exception as exc:  # noqa: BLE001 — the result JSON must record any failure verbatim
        if not result["steps"] or result["steps"][-1]["ok"]:
            record("exception", False, None, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        code = 1
    result["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {args.out}")
    return code


if __name__ == "__main__":
    sys.exit(main())
