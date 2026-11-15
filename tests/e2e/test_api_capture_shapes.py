"""MEU-106 capture line and ellipse shapes through the API (Session 72): AC-106.5, .17 and .29.

Row 2 holds AC-106.5's default-omission, 422 and OpenAPI blocks; row 3 adds its round-trip
block, the crop (AC-106.17) and the trace (AC-106.29).
Every image is generated under tmp_path; nothing reaches the network.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from tests.e2e.test_api_capture_crop import AUTH, PREFIX, WHITE, _inbox, _shot_id, _stack

pytestmark = pytest.mark.e2e

REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN = REPO_ROOT / "docs/execution/plans/2026-11-14-capture-shapes-steps"
ARROW = {"type": "arrow", "color": "red", "stroke_width": 3, "from": [4, 6], "to": [40, 30]}
RECT = {
    "type": "rect",
    "x": 4,
    "y": 6,
    "width": 20,
    "height": 10,
    "color": "red",
    "stroke_width": 2,
}
# The API's one 422 envelope: it names no field and echoes no value.
REFUSAL = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
BAD_VALUES: dict[str, object] = {"x": "x", "empty": "", "null": None, "int": 1}
BAD = [
    (f"{field}-{name}", {**base, field: value})
    for field, base in (("head", ARROW), ("shape", RECT))
    for name, value in BAD_VALUES.items()
]


def _ac(n: int):
    label = f"AC-106.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _post(client: Any, shot_id: str, marks: list[dict[str, Any]]) -> Any:
    # ASCII-escaped JSON text, as the redact tests send it.
    return client.post(
        f"{PREFIX}/{shot_id}/annotate",
        headers={**AUTH, "Content-Type": "application/json"},
        content=json.dumps({"annotations": marks}, ensure_ascii=True),
    )


def _plain_shot(tmp_path: Path) -> Path:
    from PIL import Image

    inbox = _inbox(tmp_path)
    Image.new("RGB", (64, 48), WHITE).save(inbox / "shot.png")
    return inbox


@_ac(5)
def test_ac_106_5_default_marks_omit_head_and_shape(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.5"
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        # The explicit default is accepted (D-768) and left out of the response,
        # as a missing key is.
        explicit = [ARROW, {**RECT, "shape": "rect"}, {**ARROW, "head": "end"}]
        response = _post(client, shot_id, explicit)
        assert response.status_code == 200, response.text
        marks = client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()["annotations"]
    assert marks == [ARROW, RECT, ARROW]
    assert all("head" not in mark and "shape" not in mark for mark in marks)


@pytest.mark.parametrize(("case", "body"), BAD, ids=[case for case, _ in BAD])
def test_ac_106_5_bad_head_or_shape_is_422(case: str, body: dict[str, Any], tmp_path: Path) -> None:
    inbox = _plain_shot(tmp_path)
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        good = _post(client, shot_id, [ARROW, RECT])
        assert good.status_code == 200, good.text
        refused = _post(client, shot_id, [body])
        after = client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()["annotations"]
    assert refused.status_code == 422, f"{case}: {refused.text}"
    assert refused.json() == REFUSAL, case
    assert after == [ARROW, RECT]


@_ac(5)
def test_ac_106_5_openapi_snapshot_and_delta(ac_id: str) -> None:
    assert ac_id == "AC-106.5"
    import subprocess
    import sys

    from tools.export_openapi import build_openapi, render_openapi

    committed = (REPO_ROOT / "openapi.committed.json").read_text(encoding="utf-8")
    assert render_openapi(build_openapi()) == committed
    run = subprocess.run(
        [sys.executable, str(PLAN / "openapi-delta.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    assert run.returncode == 0, run.stdout[-2000:] + run.stderr[-2000:]
    assert run.stdout.strip().splitlines()[-1] == "openapi-delta: pass"


@_ac(5)
def test_ac_106_5_none_arrow_and_ellipse_round_trip(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.5"
    inbox = _plain_shot(tmp_path)
    sent = [{**ARROW, "head": "none"}, {**RECT, "shape": "ellipse"}]
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        response = _post(client, shot_id, sent)
        assert response.status_code == 200, response.text
        marks = client.get(f"{PREFIX}/{shot_id}", headers=AUTH).json()["annotations"]
    assert marks == sent


# ------------------------------------------------------------ AC-106.17 crop end to end


@_ac(17)
def test_ac_106_17_crop_keeps_line_drops_straddling_ellipse(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-106.17"
    from PIL import Image
    from tests.e2e.test_api_capture_crop import _annotate, _crop

    inbox = _inbox(tmp_path)
    Image.new("RGB", (200, 100), WHITE).save(inbox / "shot.png")
    pen = {"color": "red", "stroke_width": 3}
    line = {"type": "arrow", "from": [60, 30], "to": [120, 60], **pen, "head": "none"}
    both = {"type": "arrow", "from": [70, 40], "to": [180, 40], **pen, "head": "both"}
    inside = {"type": "rect", "x": 60, "y": 30, "width": 40, "height": 20, **pen}
    inside["shape"] = "ellipse"
    straddling = {**inside, "x": 130, "y": 50}
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        _annotate(client, shot_id, [line, both, inside, straddling])
        response = _crop(client, shot_id, {"x": 50, "y": 20, "width": 100, "height": 60})
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["marks"] == {"kept": 2, "clipped": 1, "dropped": 1}
    sidecar = json.loads(Path(payload["item"]["sidecar_path"]).read_text(encoding="utf-8"))
    assert sidecar["annotations"] == [
        {"type": "arrow", "from": [10, 10], "to": [70, 40], **pen, "head": "none"},
        {"type": "arrow", "from": [20, 20], "to": [100, 20], **pen, "head": "both"},
        {"type": "rect", "x": 10, "y": 10, "width": 40, "height": 20, **pen, "shape": "ellipse"},
    ]


# ------------------------------------------------------------ AC-106.29 trace (S55 RULE-3)

# The body the MCP tool sends for this annotate: mcp-server/tests/capture.test.ts (AC-106.29's
# MCP half) parses the same marks through the MCP schema and records the POST body it sends.
MCP_BODY: dict[str, Any] = {
    "annotations": [
        {
            "type": "arrow",
            "from": [10, 30],
            "to": [110, 30],
            "color": "#FF0000",
            "stroke_width": 3,
            "head": "none",
        },
        {
            "type": "rect",
            "x": 10,
            "y": 10,
            "width": 60,
            "height": 40,
            "color": "#FF0000",
            "stroke_width": 3,
            "shape": "ellipse",
        },
    ]
}


@_ac(29)
def test_ac_106_29_mcp_annotate_traced_to_sidecar_and_bake(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-106.29"
    from PIL import Image

    from avkit_api.routes import captures as route
    from avkit_core.domain.capture import ArrowAnnotation, RectAnnotation

    seen: list[object] = []
    original = route._annotations_from_in

    def recording(items: list[Any]) -> list[Any]:
        parsed = original(items)
        seen.extend(parsed)
        return parsed

    monkeypatch.setattr(route, "_annotations_from_in", recording)
    inbox = _inbox(tmp_path)
    Image.new("RGB", (120, 60), WHITE).save(inbox / "shot.png")
    with _stack(tmp_path, inbox) as (client, _services):
        shot_id = _shot_id(client, "shot.png")
        response = client.post(
            f"{PREFIX}/{shot_id}/annotate",
            headers={**AUTH, "Content-Type": "application/json"},
            content=json.dumps(MCP_BODY),
        )
    assert response.status_code == 200, response.text
    assert len(seen) == 2
    arrow, box = seen
    assert isinstance(arrow, ArrowAnnotation) and arrow.head == "none"
    assert isinstance(box, RectAnnotation) and box.shape == "ellipse"
    item = response.json()
    sidecar = json.loads(Path(item["sidecar_path"]).read_text(encoding="utf-8"))
    assert sidecar["annotations"] == MCP_BODY["annotations"]
    with Image.open(item["annotated_path"]) as opened:
        baked = opened.convert("RGB")
    far = baked.getpixel((108, 30))
    assert far[0] > 200 and far[1] < 160 and far[2] < 160, far
    assert min(baked.getpixel((100, 26))) > 240, baked.getpixel((100, 26))  # no head
    assert min(baked.getpixel((11, 11))) > 240, baked.getpixel((11, 11))  # the box corner
