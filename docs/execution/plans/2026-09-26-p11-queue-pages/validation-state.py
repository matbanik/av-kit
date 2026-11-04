"""Capture the selected Session 24 UI gate inputs, independently of its receipts."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
SKIP = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "node_modules", "obj", "bin"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def observe(argv: list[str]) -> str:
    result = subprocess.run(["rtk", "proxy", *argv], cwd=ROOT, capture_output=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{argv}: exit {result.returncode}: {result.stderr.decode(errors='replace')}")
    return result.stdout.decode("utf-8", errors="strict").strip()


def main() -> None:
    output = Path(sys.argv[1])
    files: set[Path] = set()
    for relative in (
        "ui/src", "ui/tests", "ui/scripts", "ui/out", "ui/out-e2e",
        "native/region-picker-stub", "packages", "docs/build-plan",
    ):
        directory = ROOT / relative
        if not directory.is_dir():
            raise FileNotFoundError(directory)
        files.update(p for p in directory.rglob("*") if p.is_file() and not SKIP.intersection(p.relative_to(directory).parts))
    files.update(p for p in (ROOT / "ui").iterdir() if p.is_file() and p.suffix in {".json", ".ts", ".mjs", ".cjs", ".yaml", ".yml"})
    for relative in (
        ".agent/docs/commands.md", ".agent/model-registry.local.yaml",
        "openapi.committed.json", "mcp-server/package.json", "mcp-server/package-lock.json",
        "ui/node_modules/.package-lock.json", "ui/node_modules/electron/dist/electron.exe",
    ):
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        files.add(path)
    files.update(BASE / name for name in ("implementation-plan.md", "validate-task.ps1", "validation-state.py", "run-validation.ps1"))
    hashes = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in sorted(files)}
    versions = {"node": observe(["node", "--version"]), "npm": observe(["npm", "--version"]), "dotnet": observe(["dotnet", "--list-runtimes"])}
    installed = json.loads(observe(["npm", "--prefix", "ui", "ls", "--all", "--json"]))
    executable_hashes = {}
    for name in ("node", "rtk", "pwsh", "dotnet"):
        resolved = shutil.which(name)
        if not resolved:
            raise FileNotFoundError(name)
        executable_hashes[name] = {"path": resolved, "sha256": digest(Path(resolved).read_bytes())}
    env_names = {"PATH", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "CI", "FORCE_COLOR", "NO_COLOR", "RECEIPTS_DIR", "ELECTRON_RUN_AS_NODE", "AVKIT_E2E_OUT_DIR", "AVKIT_PRIMITIVE_HARNESS_BUILD", "AGENT_MODEL_REGISTRY", "AGENT_MODEL_REGISTRY_HOME"}
    env_names.update(name for name in os.environ if name.startswith(("AVKIT_", "NODE_", "ELECTRON_", "PLAYWRIGHT_", "npm_config_", "DOTNET_")))
    env = {name: None if name not in os.environ else digest(os.environ[name].encode()) for name in sorted(env_names)}
    state = {
        "schema": "p11q-ui-inputs.v1", "scope": "UI static/unit/build and all real Electron cases",
        "files": hashes, "runtime": versions, "executables": executable_hashes,
        "installed_dependencies_sha256": digest(json.dumps(installed, sort_keys=True).encode()),
        "process_environment_sha256_by_key": env, "os": platform.platform(),
        "external_inputs": "Electron tests create isolated app-data directories and local HTTP seams; capture uses the hashed region-picker-stub publish tree; primitive harness uses hashed out-e2e",
    }
    state_id = "sha256:" + digest(json.dumps(state, sort_keys=True, separators=(",", ":")).encode())
    output.write_text(json.dumps({"state_id": state_id, **state}, indent=2) + "\n", encoding="utf-8")
    print(f"{state_id}\n{len(hashes)} input files; live runtime, installed dependency versions and environment captured")


if __name__ == "__main__":
    main()
