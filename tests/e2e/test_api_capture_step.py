"""MEU-107 capture step mark through the API (Session 72): AC-107.6, .15's API half, .20, .22.

`build_services` builds the real app over a temporary SQLite file; every image is generated
under tmp_path. Nothing reaches the network or reads user data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from tests.e2e.test_api_capture_crop import AUTH, PREFIX, WHITE, _inbox, _shot_id, _stack

pytestmark = pytest.mark.e2e

SETTINGS = "/api/v1/settings/capture"
JSON = {**AUTH, "Content-Type": "application/json"}
STEP = {"type": "step", "x": 12, "y": 9, "number": 3, "color": "#E0AF68", "size": 24}
REFUSAL = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
# The input matrix (implementation-plan.md MEU-107), API column: each of these is 422.
BAD_STEPS: dict[str, dict[str, Any]] = {
    "x-negative": {**STEP, "x": -1},
    "x-bool": {**STEP, "x": True},
    "x-float": {**STEP, "x": 1.5},
    "x-text": {**STEP, "x": "1"},
    "number-0": {**STEP, "number": 0},
    "number-1000": {**STEP, "number": 1000},
    "size-11": {**STEP, "size": 11},
    "size-201": {**STEP, "size": 201},
    "color-empty": {**STEP, "color": ""},
    "color-bell": {**STEP, "color": "\x07"},
    "color-surrogate": {**STEP, "color": "\ud800"},
    "extra-label": {**STEP, "label": "one"},
    "missing-size": {key: value for key, value in STEP.items() if key != "size"},
}
# AC-107.15: the raw JSON of each refused settings value.
BAD_LEAVES: dict[str, tuple[str, str]] = {
    "color-no-hash": ("step_color", '"123456"'),
    "color-empty": ("step_color", '""'),
    "color-bell": ("step_color", '"\\u0007"'),
    "color-surrogate": ("step_color", '"\\ud800"'),
    "size-11": ("step_size", "11"),
    "size-201": ("step_size", "201"),
    "size-float": ("step_size", "48.0"),
    "size-bool": ("step_size", "true"),
    "size-text": ("step_size", '"48"'),
    "size-401-digits": ("step_size", "1" + "0" * 400),
}


def _ac(n: int):
    label = f"AC-107.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _post(client: TestClient, shot_id: str, marks: list[dict[str, Any]]) -> Any:
    # ASCII-escaped JSON text: a lone surrogate reaches the server as `\ud800`.
    return client.post(
        f"{PREFIX}/{shot_id}/annotate",
        headers=JSON,
        content=json.dumps({"annotations": marks}, ensure_ascii=True),
    )


def _plain_shot(tmp_path: Path) -> Path:
    from PIL import Image

    inbox = _inbox(tmp_path)
    Image.new("RGB", (64, 48), WHITE).save(inbox / "shot.png")
    return inbox


# ------------------------------------------------------------ AC-107.6 STEP_API


@_ac(6)
def test_ac_107_6_step_round_trips_through_annotate(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-107.6"
    from avkit_api.routes import captures as route
    from avkit_core.domain.capture import StepAnnotation

    seen: list[object] = []
    original = route._annotations_from_in

    def recording(items: list[Any]) -> list[Any]:
        parsed = original(items)
        seen.extend(parsed)
        return parsed

    monkeypatch.setattr(route, "_annotations_from_in", recording)
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        response = _post(client, shot_id, [STEP])
        assert response.status_code == 200, response.text
        marks = client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()["annotations"]
    assert marks == [STEP]
    assert list(marks[0]) == list(STEP)
    assert seen == [StepAnnotation(x=12, y=9, number=3, color="#E0AF68", size=24)]


@pytest.mark.parametrize("case", list(BAD_STEPS), ids=list(BAD_STEPS))
def test_ac_107_6_bad_step_is_422(case: str, tmp_path: Path) -> None:
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        good = _post(client, shot_id, [STEP])
        assert good.status_code == 200, good.text
        refused = _post(client, shot_id, [BAD_STEPS[case]])
        after = client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()["annotations"]
    assert refused.status_code == 422, f"{case}: {refused.text}"
    assert refused.json() == REFUSAL, case
    assert after == [STEP]


# ------------------------------------------------------------ AC-107.15 STEP_STYLE (API)


@_ac(15)
def test_ac_107_15_put_step_leaves_round_trips(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.15"
    inbox = _inbox(tmp_path)
    body = {"step_color": "#123456", "step_size": 48}
    with _stack(tmp_path, inbox) as (client, _services):
        fresh = client.get(SETTINGS, headers=AUTH).json()
        put = client.put(SETTINGS, headers=JSON, content=json.dumps(body))
        got = client.get(SETTINGS, headers=AUTH).json()
    assert (fresh["step_color"], fresh["step_size"]) == ("#E0AF68", 32)
    assert put.status_code == 200, put.text
    assert {key: got[key] for key in body} == body
    assert type(got["step_size"]) is int


@pytest.mark.parametrize("case", list(BAD_LEAVES), ids=list(BAD_LEAVES))
def test_ac_107_15_bad_step_leaf_is_422(case: str, tmp_path: Path) -> None:
    key, raw = BAD_LEAVES[case]
    inbox = _inbox(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        before = client.get(SETTINGS, headers=AUTH).json()
        response = client.put(SETTINGS, headers=JSON, content=f'{{"{key}": {raw}}}')
        after = client.get(SETTINGS, headers=AUTH).json()
    assert response.status_code == 422, f"{case}: {response.text[:200]}"
    # As AC-105.4: the body echoes no value (an empty string is looked for as its JSON `""`).
    assert (raw.strip('"') or '""') not in response.text, case
    assert after == before


@_ac(15)
def test_ac_107_15_4301_digit_size_is_400(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.15"
    # The known parser limit (D-775): 4301 digits fail JSON parsing before validation.
    inbox = _inbox(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        response = client.put(SETTINGS, headers=JSON, content='{"step_size": 1' + "0" * 4300 + "}")
    assert response.status_code == 400, response.text[:200]
    assert "0" * 50 not in response.text


# ------------------------------------------------------------ AC-107.20 trace (S55 RULE-3)

# The body the MCP tool sends for this annotate: mcp-server/tests/capture.test.ts (AC-107.20's
# MCP half) parses the same mark through the MCP schema and records the POST body it sends.
MCP_STEP = {"type": "step", "x": 32, "y": 24, "number": 1, "color": "#E0AF68", "size": 32}


@_ac(20)
def test_ac_107_20_mcp_step_traced_to_sidecar_and_bake(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-107.20"
    from PIL import Image

    from avkit_api.routes import captures as route
    from avkit_core.domain.capture import StepAnnotation

    seen: list[object] = []
    original = route._annotations_from_in

    def recording(items: list[Any]) -> list[Any]:
        parsed = original(items)
        seen.extend(parsed)
        return parsed

    monkeypatch.setattr(route, "_annotations_from_in", recording)
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        response = _post(client, shot_id, [MCP_STEP])
    assert response.status_code == 200, response.text
    assert seen == [StepAnnotation(x=32, y=24, number=1, color="#E0AF68", size=32)]
    item = response.json()
    sidecar = json.loads(Path(item["sidecar_path"]).read_text(encoding="utf-8"))
    assert sidecar["annotations"] == [MCP_STEP]
    assert list(sidecar["annotations"][0]) == list(MCP_STEP)
    with Image.open(item["annotated_path"]) as opened:
        # The badge's top inner edge: (x, y - radius + 2) with radius 16.
        edge = opened.convert("RGB").getpixel((32, 10))
    assert all(abs(got - want) <= 3 for got, want in zip(edge, (224, 175, 104), strict=True)), edge


# ------------------------------------------------------------ AC-107.22 crop end to end


@_ac(22)
def test_ac_107_22_crop_moves_inside_step_drops_outside(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-107.22"
    from PIL import Image
    from tests.e2e.test_api_capture_crop import _annotate, _crop

    inbox = _inbox(tmp_path)
    Image.new("RGB", (200, 100), WHITE).save(inbox / "shot.png")
    inside = {**STEP, "x": 60, "y": 40, "number": 1}
    outside = {**STEP, "x": 10, "y": 10, "number": 2}
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        _annotate(client, shot_id, [inside, outside])
        response = _crop(client, shot_id, {"x": 50, "y": 20, "width": 100, "height": 60})
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["marks"] == {"kept": 1, "clipped": 0, "dropped": 1}
    sidecar = json.loads(Path(payload["item"]["sidecar_path"]).read_text(encoding="utf-8"))
    assert sidecar["annotations"] == [{**inside, "x": 10, "y": 20}]
