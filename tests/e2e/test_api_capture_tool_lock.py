"""MEU-143 LOCK_LEAF through the real stack (AC-143.4, AC-143.22 Python half).

`build_services` builds the real app over a temporary SQLite file; no network, no user data.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services

pytestmark = pytest.mark.e2e

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN = REPO_ROOT / "docs/execution/plans/2026-11-14-capture-tool-flow"
TOKEN = "s71b-e2e-token"
AUTH = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SETTINGS = "/api/v1/settings/capture"
REFUSED: dict[str, str] = {
    "text_false": '"false"',
    "zero": "0",
    "one": "1",
    "null": "null",
}


@contextmanager
def _client(tmp_path: Path) -> Iterator[TestClient]:
    app_data = tmp_path / "app"
    app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=frozenset({TOKEN}), services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            yield client
    finally:
        dispose()


def test_ac_143_4_put_false_round_trips(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        fresh = client.get(SETTINGS, headers=AUTH).json()
        put = client.put(SETTINGS, headers=AUTH, content=json.dumps({"tool_lock": False}))
        got = client.get(SETTINGS, headers=AUTH).json()
    assert fresh["tool_lock"] is True
    assert put.status_code == 200
    assert got["tool_lock"] is False


@pytest.mark.parametrize("case", list(REFUSED), ids=list(REFUSED))
def test_ac_143_4_refused_with_422(tmp_path: Path, case: str) -> None:
    raw = REFUSED[case]
    with _client(tmp_path) as client:
        before = client.get(SETTINGS, headers=AUTH).json()
        response = client.put(SETTINGS, headers=AUTH, content=f'{{"tool_lock": {raw}}}')
        after = client.get(SETTINGS, headers=AUTH).json()
    assert response.status_code == 422, response.text[:200]
    error = response.json()["error"]
    assert set(error) == {"code", "message", "details"}
    assert error["details"] is None
    assert raw.strip('"') not in error["code"] + error["message"]
    assert after == before


def test_ac_143_4_openapi_equals_committed() -> None:
    from tools.export_openapi import build_openapi, render_openapi

    committed = (REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8")
    assert render_openapi(build_openapi()) == committed


def test_ac_143_4_openapi_adds_only_tool_lock() -> None:
    base = (PLAN / "baseline.sha").read_text(encoding="utf-8").strip()
    shown = subprocess.run(
        ["git", "show", f"{base}:openapi.committed.json"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=True,
    )
    old = json.loads(shown.stdout)
    new = json.loads((REPO_ROOT / "openapi.committed.json").read_bytes())
    put_old = old["components"]["schemas"]["SettingsPutIn"]["properties"]
    put_new = new["components"]["schemas"]["SettingsPutIn"]["properties"]
    assert sorted(set(put_new) - set(put_old)) == ["tool_lock"]
    put_new.pop("tool_lock")
    assert new == old


def test_ac_143_22_one_body_traced_to_next_get(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.settings import SettingsService

    calls: list[tuple[str, dict[str, object]]] = []
    stored: list[str | None] = []
    original = SettingsService.set_namespace

    def recording(self: SettingsService, namespace: str, mapping: dict[str, object]) -> None:
        calls.append((namespace, dict(mapping)))
        original(self, namespace, mapping)
        with self._uow_factory() as uow:
            row = uow.settings.get(namespace, "tool_lock")
        stored.append(None if row is None else row.value)

    monkeypatch.setattr(SettingsService, "set_namespace", recording)
    body = {"tool_lock": False}
    with _client(tmp_path) as client:
        put = client.put(SETTINGS, headers=AUTH, content=json.dumps(body))
        got = client.get(SETTINGS, headers=AUTH).json()
    assert put.status_code == 200
    assert calls == [("capture", body)]
    assert calls[0][1]["tool_lock"] is False
    assert stored == ["false"]
    assert got["tool_lock"] is False
    assert put.json()["tool_lock"] is False
