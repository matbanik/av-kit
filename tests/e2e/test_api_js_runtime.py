"""MEU-141 on the API: the `deno_path` setting (AC-141.1) and `js_runtime` on Health (AC-141.8).

`build_services` builds the real stack. `shutil.which` and `subprocess.run` are patched on their
modules and `bundled_deno` on `avkit_api.wiring`, so nothing runs and no test sees this
machine's Deno. Every failure is an assertion.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services

pytestmark = pytest.mark.e2e

REPO_ROOT = Path(__file__).resolve().parents[2]
TOKEN = "s66-e2e-token"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
SETTINGS = "/api/v1/settings/downloader"
DEPENDENCIES = "/api/v1/health/dependencies"
RUNTIME_FIELDS = ["available", "name", "path", "version", "source", "solver"]
DENO_VERSION_TEXT = (
    "deno 2.9.8 (stable, release, x86_64-pc-windows-msvc)\nv8 14.3\ntypescript 5.9\n"
)


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"MZ")
    return path


def _tools(monkeypatch: pytest.MonkeyPatch) -> None:
    """No Deno on PATH; a Deno `--version` run answers 2.9.8; anything else fails."""

    def fake_which(name: str, *args: Any, **kwargs: Any) -> str | None:
        del name, args, kwargs
        return None

    def fake_run(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del args, kwargs
        if Path(str(cmd[0])).stem.lower() == "deno":
            return subprocess.CompletedProcess(cmd, 0, DENO_VERSION_TEXT, "")
        return subprocess.CompletedProcess(cmd, 1, "", "")

    monkeypatch.setattr("shutil.which", fake_which)
    monkeypatch.setattr("subprocess.run", fake_run)


@contextmanager
def _client(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bundled: Path | None
) -> Iterator[TestClient]:
    import avkit_api.wiring as wiring
    from avkit_core.services.health import HealthService

    assert hasattr(wiring, "bundled_deno")
    monkeypatch.setattr(HealthService, "_active", None)
    monkeypatch.setattr(wiring, "bundled_deno", lambda: bundled)
    _tools(monkeypatch)
    app_data = tmp_path / "app"
    app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=frozenset({TOKEN}), services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield client
    finally:
        dispose()


# --- AC-141.1: DENO_SETTING through the API -------------------------------------------------------


def test_ac_141_1_deno_path_is_the_last_downloader_key() -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE

    keys = [key for (namespace, key) in SETTINGS_KEY_TABLE if namespace == "downloader"]
    assert "deno_path" in keys
    assert keys[-1] == "deno_path"
    spec = SETTINGS_KEY_TABLE[("downloader", "deno_path")]
    assert (spec.kind, spec.default) == ("string", "")


def test_ac_141_1_settings_put_schema_takes_deno_path() -> None:
    from avkit_api.schemas.settings import SettingsPutIn

    assert "deno_path" in SettingsPutIn.model_fields


def test_ac_141_1_deno_path_round_trips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    chosen = str(tmp_path / "chosen" / "deno.exe")
    with _client(tmp_path, monkeypatch, None) as client:
        before = client.get(SETTINGS, headers=AUTH).json().get("deno_path", "absent")
        put = client.put(SETTINGS, headers=AUTH, json={"deno_path": chosen})
        after = client.get(SETTINGS, headers=AUTH).json().get("deno_path", "absent")
    assert before == ""
    assert put.status_code == 200
    assert after == chosen


def test_ac_141_1_unknown_leaf_refused_neg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with _client(tmp_path, monkeypatch, None) as client:
        response = client.put(SETTINGS, headers=AUTH, json={"deno_path_extra": "C:/x/deno.exe"})
    assert response.status_code == 422


# --- AC-141.8: RUNTIME_WIRE -----------------------------------------------------------------------


def test_ac_141_8_dependencies_serve_all_six_fields(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bundled = _touch(tmp_path / "resources" / "deno" / "deno.exe")
    with _client(tmp_path, monkeypatch, bundled) as client:
        response = client.get(DEPENDENCIES, headers=AUTH)
    assert response.status_code == 200
    runtime = response.json().get("js_runtime")
    assert isinstance(runtime, dict), runtime
    assert sorted(runtime) == sorted(RUNTIME_FIELDS)
    assert runtime == {
        "available": True,
        "name": "deno",
        "path": str(bundled),
        "version": "2.9.8",
        "source": "bundled",
        "solver": True,
    }


def test_ac_141_8_committed_snapshot_names_the_wire() -> None:
    committed = json.loads((REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8"))
    schemas = committed.get("components", {}).get("schemas", {})
    assert sorted(schemas.get("JsRuntimeOut", {}).get("properties", {})) == sorted(RUNTIME_FIELDS)
    assert "js_runtime" in schemas.get("DependenciesOut", {}).get("properties", {})
    assert "deno_path" in schemas.get("SettingsPutIn", {}).get("properties", {})


def test_ac_141_8_dependencies_need_the_bearer_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with _client(tmp_path, monkeypatch, None) as client:
        response = client.get(DEPENDENCIES)
    assert response.status_code == 401
