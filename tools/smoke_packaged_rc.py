"""Packaged release-candidate smoke for one install root (MEU-110).

`--install-root` is `ui/dist/win-unpacked` or a real NSIS install, so both get the same checks:

- Layout (AC-110.3, AC-110.11): the files the installer must carry, and no zip beside FFmpeg.
- Bans (AC-110.11): the packages left out of the build are absent from `_internal` and from the
  module archive inside the shipped exe. A folder test alone passed the 2026-08-24 build with
  phonemizer inside its exe, so `--negative-control` must report phonemizer on that exe.
- Picker (AC-110.11): run with no arguments it loads .NET and WinForms and refuses the command line.
- Backend (AC-110.12): the frozen backend starts on throwaway folders, reports the release version
  and the bundled FFmpeg, and completes a real first conversion into a folder that does not exist.
- Licence list (AC-110.17): the complete text of onnxruntime's and numpy's embedded notices.

Writes one JSON object to `--out`. Exit 0 means every check passed. Run it with `uv run`: the module
archive reader and the notices it compares against come from the project environment.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata as md
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.generate_third_party_licenses import _read_notice, read_exe_modules  # noqa: E402
from tools.smoke_packaged_tts import Backend  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
    "project"
]["version"]
FFMPEG_SOURCE_ZIP = REPO_ROOT / "packaging" / "ffmpeg-win64" / "ffmpeg-pin.zip"
REQUIRED_FILES = (
    "av-kit.exe",
    "LICENSE.electron.txt",
    "LICENSES.chromium.html",
    "resources/LICENSE",
    "resources/THIRD_PARTY_NOTICES.md",
    "resources/THIRD_PARTY_LICENSES.txt",
    "resources/ffmpeg/ffmpeg.exe",
    "resources/ffmpeg/ffprobe.exe",
    "resources/ffmpeg/LICENSE.txt",
    "resources/avkit-backend/avkit-backend.exe",
    "resources/region-picker/avkit-region-picker.exe",
    "resources/region-picker/avkit-region-picker.deps.json",
    "resources/region-picker/coreclr.dll",
    "resources/region-picker/System.Windows.Forms.dll",
    "resources/mcp-server/index.mjs",
    "resources/mcp-server/LICENSES.txt",
)
BANNED_PACKAGES = (
    "torch",
    "torchvision",
    "torchaudio",
    "kokoro",
    "phonemizer",
    "espeakng_loader",
)
BANNED_MODULES = (*BANNED_PACKAGES, "misaki.espeak")
PICKER_EXIT_ERROR = 1
PICKER_REFUSAL = "--out <path> is required"
EMBEDDED_NOTICES = {
    "onnxruntime": ("onnxruntime/ThirdPartyNotices.txt", "onnxruntime/LICENSE"),
    "numpy": (
        "numpy/ma/LICENSE",
        "numpy/random/LICENSE.md",
        "numpy/_core/include/numpy/random/LICENSE.txt",
    ),
}
CONVERT_TIMEOUT_S = 180.0
MIN_OUTPUT_SECONDS = 1.0
SOFTWARE_ENCODERS = ("libx265", "libx264")


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _layout(root: Path, errors: list[str]) -> dict[str, Any]:
    missing = [
        name
        for name in REQUIRED_FILES
        if not (root / name).is_file() or (root / name).stat().st_size == 0
    ]
    errors += [f"missing or empty: {name}" for name in missing]
    zips = sorted(path.name for path in (root / "resources" / "ffmpeg").glob("**/*.zip"))
    errors += [f"zip shipped beside FFmpeg: {name}" for name in zips]
    source_zip = FFMPEG_SOURCE_ZIP.is_file()
    if not source_zip:
        errors.append(f"{FFMPEG_SOURCE_ZIP} is absent, so the zip filter proved nothing")
    return {"missing": missing, "ffmpeg_zips": zips, "ffmpeg_source_zip_present": source_zip}


def _banned_in_archive(exe: Path) -> list[str]:
    modules = read_exe_modules(exe)
    return sorted(
        ban
        for ban in BANNED_MODULES
        if any(name == ban or name.startswith(f"{ban}.") for name in modules)
    )


def _bans(root: Path, negative_control: Path, errors: list[str]) -> dict[str, Any]:
    backend_dir = root / "resources" / "avkit-backend"
    internal = backend_dir / "_internal"
    folders = sorted(
        name
        for name in BANNED_PACKAGES
        if (internal / name).exists() or any(internal.glob(f"{name}-*.dist-info"))
    )
    archive = _banned_in_archive(backend_dir / "avkit-backend.exe")
    negative = _banned_in_archive(negative_control)
    errors += [f"banned package in _internal: {name}" for name in folders]
    errors += [f"banned module in the exe's archive: {name}" for name in archive]
    if "phonemizer" not in negative:
        errors.append(f"the check missed phonemizer on the negative control: {negative}")
    return {"internal": folders, "archive": archive, "negative_control": negative}


def _picker(root: Path, errors: list[str]) -> dict[str, Any]:
    picker = root / "resources" / "region-picker" / "avkit-region-picker.exe"
    run = subprocess.run(
        [str(picker)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    if run.returncode != PICKER_EXIT_ERROR or PICKER_REFUSAL not in run.stderr:
        errors.append(f"picker exited {run.returncode}: {run.stderr.strip()!r}")
    return {"exit": run.returncode, "stderr": run.stderr.strip()}


def _backend_env(run_dir: Path) -> dict[str, str]:
    """Empty home and app-data folders, so the real ones are neither read nor written."""
    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("AVKIT_") and key != "ELECTRON_RUN_AS_NODE"
    }
    folders = (
        ("HOME", "home"),
        ("USERPROFILE", "home"),
        ("APPDATA", "roaming"),
        ("LOCALAPPDATA", "local"),
    )
    for name, sub in folders:
        path = run_dir / sub
        path.mkdir(parents=True, exist_ok=True)
        env[name] = str(path)
    return env


def _reported_version(backend: Backend) -> str:
    request = urllib.request.Request(f"http://127.0.0.1:{backend.port}/openapi.json")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=60) as response:
        return str(json.loads(response.read())["info"]["version"])


def _make_source(ffmpeg: Path, source: Path) -> None:
    """Two seconds of video and audio, with encoders every FFmpeg build has."""
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "testsrc2=size=320x240:rate=15:duration=2",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:duration=2",
            "-c:v",
            "mpeg4",
            "-c:a",
            "aac",
            str(source),
        ],
        capture_output=True,
        timeout=60,
        check=True,
    )


def _output_seconds(ffprobe: Path, path: Path) -> float:
    run = subprocess.run(
        [
            str(ffprobe),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    return float(run.stdout.strip())


def _run_one_job(backend: Backend, body: dict[str, Any]) -> dict[str, Any]:
    job = backend.ok("POST", "/conversions", body)["items"][0]
    backend.ok("POST", "/conversions/start")
    deadline = time.monotonic() + CONVERT_TIMEOUT_S
    while job["status"] in ("Pending", "Processing") and time.monotonic() < deadline:
        time.sleep(0.5)
        job = backend.ok("GET", f"/conversions/{job['id']}")
    return job


def _first_conversion(backend: Backend, ffmpeg_dir: Path, run_dir: Path) -> dict[str, Any]:
    source = run_dir / "source.mp4"
    _make_source(ffmpeg_dir / "ffmpeg.exe", source)
    output_dir = run_dir / "not" / "yet" / "there"
    outcome: dict[str, Any] = {"output_dir": str(output_dir), "folder_existed": output_dir.exists()}
    backend.ok("PUT", "/settings/converter", {"output_dir": str(output_dir)})
    job = _run_one_job(backend, {"paths": [str(source)], "kind": "compress"})
    output = Path(job["output_path"])
    outcome |= {
        "status": job["status"],
        "error": job["error_message"],
        "encoder": job["gpu_encoder"],
        "output_path": str(output),
        "output_bytes": output.stat().st_size if output.is_file() else 0,
    }
    if output.is_file():
        outcome["output_seconds"] = _output_seconds(ffmpeg_dir / "ffprobe.exe", output)
    # AC-112.7: its own copy of the source, because skip_existing would skip the same output.
    software_source = run_dir / "source-software.mp4"
    shutil.copyfile(source, software_source)
    software = _run_one_job(
        backend,
        {"paths": [str(software_source)], "kind": "compress", "gpu_preference": "software"},
    )
    outcome["software_job"] = {
        "status": software["status"],
        "error": software["error_message"],
        "encoder": software["gpu_encoder"],
    }
    return outcome


def _check_conversion(outcome: dict[str, Any], errors: list[str]) -> None:
    if outcome["folder_existed"]:
        errors.append(f"{outcome['output_dir']} existed before the conversion")
    if outcome["status"] != "Done":
        errors.append(f"conversion ended {outcome['status']}: {outcome['error']}")
    if Path(outcome["output_path"]).parent != Path(outcome["output_dir"]):
        errors.append(f"output {outcome['output_path']} is outside {outcome['output_dir']}")
    if outcome.get("output_seconds", 0.0) < MIN_OUTPUT_SECONDS:
        errors.append(f"output is not a real {MIN_OUTPUT_SECONDS} s video: {outcome}")
    software = outcome["software_job"]
    if software["status"] != "Done" or software["encoder"] not in SOFTWARE_ENCODERS:
        errors.append(f"the job that asked for the software encoder did not run one: {software}")


def _backend(root: Path, errors: list[str]) -> dict[str, Any]:
    backend_dir = root / "resources" / "avkit-backend"
    ffmpeg_dir = root / "resources" / "ffmpeg"
    with tempfile.TemporaryDirectory(prefix="avkit-rc-smoke-", ignore_cleanup_errors=True) as temp:
        run_dir = Path(temp)
        backend = Backend(
            backend_dir / "avkit-backend.exe",
            app_data=run_dir / "app-data",
            cwd=run_dir,
            env=_backend_env(run_dir),
        )
        outcome: dict[str, Any] = {}
        try:
            outcome["version"] = _reported_version(backend)
            ffmpeg = backend.ok("GET", "/health/dependencies")["ffmpeg"]
            outcome["ffmpeg"] = ffmpeg
            outcome["conversion"] = _first_conversion(backend, ffmpeg_dir, run_dir)
        except Exception as exc:  # recorded beside the backend's own output; the smoke fails
            errors.append(f"backend: {type(exc).__name__}: {exc}")
            return outcome
        finally:
            backend.stop()
            outcome["backend_tail"] = backend.tail()
    if outcome["version"] != EXPECTED_VERSION:
        errors.append(f"backend reports {outcome['version']}, expected {EXPECTED_VERSION}")
    bundled = (ffmpeg_dir / "ffmpeg.exe").resolve()
    if not ffmpeg["available"] or not ffmpeg["ffprobe_available"]:
        errors.append(f"FFmpeg is not available: {ffmpeg}")
    if ffmpeg["path"] is None or Path(ffmpeg["path"]).resolve() != bundled:
        errors.append(f"backend uses {ffmpeg['path']}, not the bundled {bundled}")
    _check_conversion(outcome["conversion"], errors)
    return outcome


def _licence_list(root: Path, errors: list[str]) -> dict[str, Any]:
    path = root / "resources" / "THIRD_PARTY_LICENSES.txt"
    text = path.read_bytes().decode("utf-8")
    notices: dict[str, int] = {}
    for dist_name, names in EMBEDDED_NOTICES.items():
        dist = md.distribution(dist_name)
        for name in names:
            body = _read_notice(Path(str(dist.locate_file(name)))).rstrip()
            notices[name] = len(body)
            if not body or body not in text:
                errors.append(f"{name} is not complete in {path.name}")
    return {"bytes": path.stat().st_size, "sha256": _sha256(path), "notice_chars": notices}


def _run_check(
    result: dict[str, Any], name: str, check: Callable[..., dict[str, Any]], *args: Any
) -> None:
    errors: list[str] = result["errors"]
    try:
        result[name] = check(*args, errors)
    except Exception as exc:  # recorded in the result; the smoke fails
        errors.append(f"{name}: {type(exc).__name__}: {exc}")


def run_smoke(root: Path, negative_control: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "install_root": str(root),
        "expected_version": EXPECTED_VERSION,
        "passed": False,
        "started": _now(),
        "errors": [],
    }
    _run_check(result, "layout", _layout, root)
    _run_check(result, "bans", _bans, root, negative_control)
    _run_check(result, "picker", _picker, root)
    _run_check(result, "backend", _backend, root)
    _run_check(result, "licence_list", _licence_list, root)
    result["passed"] = not result["errors"]
    result["finished"] = _now()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--install-root", type=Path, required=True)
    parser.add_argument("--negative-control", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_smoke(args.install_root.resolve(), args.negative_control)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    shown = {
        key: value
        for key, value in result.items()
        if key != "backend" or not isinstance(value, dict)
    }
    print(json.dumps(shown, indent=2))
    if isinstance(result.get("backend"), dict):
        print(json.dumps({k: v for k, v in result["backend"].items() if k != "backend_tail"}))
    print(("PASS" if result["passed"] else "FAIL") + ": smoke_packaged_rc")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
