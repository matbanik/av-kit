"""MEU-105 STYLE_API through the real stack (AC-105.4, AC-105.22).

`build_services` builds the real app over a temporary SQLite file; no network, no user data.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services

pytestmark = pytest.mark.e2e

REPO_ROOT = Path(__file__).resolve().parents[2]
TOKEN = "s71-e2e-token"
AUTH = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SETTINGS = "/api/v1/settings/capture"
STYLE = {
    "arrow_color": "#12ABCD",
    "arrow_stroke": 5,
    "box_color": "#00FF00",
    "box_stroke": 9,
    "highlight_color": "#ffee00",
    "text_color": "#FFFFFF",
    "text_font_size": 24,
    "text_bg_color": "#000000",
    "pixelate_block_size": 12,
}
REFUSED: dict[str, tuple[str, str]] = {
    "stroke_float": ("arrow_stroke", "3.0"),
    "stroke_bool": ("arrow_stroke", "true"),
    "stroke_text": ("arrow_stroke", '"3"'),
    "block_float": ("pixelate_block_size", "10.0"),
    "colour_number": ("arrow_color", "5"),
    "colour_bad_hex": ("arrow_color", '"#GGGGGG"'),
    "bg_bad_hex": ("text_bg_color", '"#GGG"'),
    "stroke_range": ("arrow_stroke", "101"),
    "font_range": ("text_font_size", "0"),
    "stroke_huge": ("arrow_stroke", "1" + "0" * 400),
    "unknown_key": ("arrow_colour", '"#12ABCD"'),
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


def test_ac_105_4_put_nine_leaves_round_trips(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        put = client.put(SETTINGS, headers=AUTH, content=json.dumps(STYLE))
        got = client.get(SETTINGS, headers=AUTH).json()
    assert put.status_code == 200
    assert {key: got[key] for key in STYLE} == STYLE
    assert got["inbox_dir"] == "~/Pictures/av-kit"


@pytest.mark.parametrize("case", list(REFUSED), ids=list(REFUSED))
def test_ac_105_4_refused_with_422(tmp_path: Path, case: str) -> None:
    key, raw = REFUSED[case]
    with _client(tmp_path) as client:
        before = client.get(SETTINGS, headers=AUTH).json()
        response = client.put(SETTINGS, headers=AUTH, content=f'{{"{key}": {raw}}}')
        after = client.get(SETTINGS, headers=AUTH).json()
    assert response.status_code == 422, response.text[:200]
    assert raw.strip('"') not in response.text
    assert after == before


def test_ac_105_4_openapi_equals_committed() -> None:
    from tools.export_openapi import build_openapi, render_openapi

    committed = (REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8")
    assert render_openapi(build_openapi()) == committed
    put = json.loads(committed)["components"]["schemas"]["SettingsPutIn"]["properties"]
    for key in STYLE:
        assert key in put, key


def test_ac_105_22_one_body_traced_to_next_get(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.services.settings import SettingsService

    calls: list[tuple[str, dict[str, object]]] = []
    original = SettingsService.set_namespace

    def recording(self: SettingsService, namespace: str, mapping: dict[str, object]) -> None:
        calls.append((namespace, dict(mapping)))
        original(self, namespace, mapping)

    monkeypatch.setattr(SettingsService, "set_namespace", recording)
    body = {"arrow_color": "#12ABCD", "arrow_stroke": 5}
    with _client(tmp_path) as client:
        put = client.put(SETTINGS, headers=AUTH, content=json.dumps(body))
        got = client.get(SETTINGS, headers=AUTH).json()
    assert put.status_code == 200
    assert calls == [("capture", body)]
    assert type(calls[0][1]["arrow_stroke"]) is int
    assert got["arrow_color"] == "#12ABCD"
    assert got["arrow_stroke"] == 5 and type(got["arrow_stroke"]) is int
    assert put.json()["arrow_stroke"] == 5
    assert got["box_color"] == "#E0AF68"
