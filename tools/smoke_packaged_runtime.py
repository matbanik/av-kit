"""RUNTIME_SMOKE (MEU-141): the packaged backend reports its bundled Deno and yt-dlp's solver.

Starts the onedir backend in `--backend-dir` through `Backend` from `smoke_packaged_tts`, with a
fresh app-data and home folder, dead proxies and a PATH from which every folder holding a
`deno.exe` is removed, then reads `/health/dependencies` once. Exit 0 only when `js_runtime`
is available, came from the bundle, has a parsed version and the solver imports; exit 1 names
the first missing field; exit 2 when the backend is missing or never gets ready. The backend
is ended through its recorded process (Session 56). Nothing reaches the network.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.smoke_packaged_tts import (  # noqa: E402 - the repo root must be importable first
    DEAD_PROXY,
    EXE_NAME,
    PROXY_KEYS,
    Backend,
    _fresh_home,
)

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def verdict(body: object) -> str | None:
    """The first field `RUNTIME_SMOKE` needs and the body lacks, or None when all hold."""
    runtime = body.get("js_runtime") if isinstance(body, dict) else None
    if not isinstance(runtime, dict):
        return "js_runtime"
    if runtime.get("available") is not True:
        return "js_runtime.available"
    if runtime.get("source") != "bundled":
        return "js_runtime.source"
    version = runtime.get("version")
    if not isinstance(version, str) or VERSION_RE.match(version) is None:
        return "js_runtime.version"
    if runtime.get("solver") is not True:
        return "js_runtime.solver"
    return None


def _path_without_deno(path_value: str) -> tuple[str, list[str]]:
    """PATH with every entry that holds a `deno.exe` removed, and the entries removed."""
    kept: list[str] = []
    removed: list[str] = []
    for entry in path_value.split(os.pathsep):
        if entry == "":
            continue
        try:
            holds = (Path(entry).expanduser() / "deno.exe").is_file()
        except (OSError, ValueError):
            holds = False
        (removed if holds else kept).append(entry)
    return os.pathsep.join(kept), removed


def _env(home: Path) -> tuple[dict[str, str], list[str]]:
    env = dict(os.environ)
    for key in PROXY_KEYS:
        env[key] = DEAD_PROXY
        env[key.lower()] = DEAD_PROXY
    env["NO_PROXY"] = "127.0.0.1,localhost"
    env["no_proxy"] = env["NO_PROXY"]
    _fresh_home(env, home)
    env["PATH"], removed = _path_without_deno(env.get("PATH", ""))
    return env, removed


def run(backend_dir: Path) -> tuple[int, dict[str, Any]]:
    result: dict[str, Any] = {"smoke": "runtime", "started": datetime.now(UTC).isoformat()}
    exe = backend_dir / EXE_NAME
    result["backend"] = str(exe)
    if not exe.is_file():
        result["error"] = f"missing {EXE_NAME}"
        return 2, result
    run_dir = Path(tempfile.mkdtemp(prefix="avkit-runtime-smoke-"))
    backend: Backend | None = None
    try:
        app_data = run_dir / "app-data"
        app_data.mkdir(parents=True)
        env, removed = _env(run_dir / "home")
        result["path_entries_removed"] = len(removed)
        try:
            backend = Backend(exe, app_data=app_data, cwd=run_dir, env=env)
        except (OSError, RuntimeError) as exc:
            result["error"] = f"backend did not start: {type(exc).__name__}"
            return 2, result
        status, body = backend.request("GET", "/health/dependencies")
        result["status"] = status
        result["js_runtime"] = body.get("js_runtime") if isinstance(body, dict) else None
        missing = verdict(body) if status == 200 else "js_runtime"
        result["missing"] = missing
        result["passed"] = missing is None
        return (0 if missing is None else 1), result
    finally:
        if backend is not None:
            backend.stop()
            result["backend_tail"] = backend.tail(20)
        shutil.rmtree(run_dir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--backend-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    code, result = run(args.backend_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if code == 0:
        runtime = result.get("js_runtime") or {}
        print(f"PASS: smoke-runtime source=bundled version={runtime.get('version')} solver=True")
    elif code == 1:
        print(f"smoke-runtime: missing {result.get('missing')}")
    else:
        print(f"smoke-runtime: {result.get('error')}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
