"""MEU-104 contract tests: POST /captures/{id}/render (RENDER_ROUTE, Session 69 plan).

Real `CaptureService`, real Pillow `CaptureAdapter` and real SQLite behind the real FastAPI app,
built by the MEU-67 stack. Render first, annotate second, so annotate's writes never feed render.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.e2e.test_api_capture_flatten import (
    AUTH,
    MARKS,
    PREFIX,
    _register,
    _row,
    _snapshot,
    _stack,
)

RENDER_PATH = "/api/v1/captures/{id}/render"
ANNOTATE_PATH = "/api/v1/captures/{id}/annotate"
VALIDATION = {
    "error": {"code": "validation_error", "message": "Request validation failed", "details": None}
}
JSON_HEADERS = {**AUTH, "Content-Type": "application/json"}


def _ac(label: str, case: str | None = None):
    ident = label if case is None else f"{label}-{case}"
    return pytest.mark.parametrize("ac_id", [label], ids=[ident])


def _text_body(text: str) -> bytes:
    mark = {"type": "text", "x": 2, "y": 2, "text": text, "color": "#ff0000", "font_size": 12}
    return json.dumps({"annotations": [mark]}).encode()


def _rect(**extra: object) -> dict[str, object]:
    return {
        "type": "rect",
        "x": 2,
        "y": 2,
        "width": 4,
        "height": 4,
        "color": "red",
        "stroke_width": 2,
        **extra,
    }


CASES: dict[str, tuple[bytes, int]] = {
    "lone-surrogate": (
        b'{"annotations":[{"type":"text","x":2,"y":2,"text":"\\ud800","color":"#ff0000","font_size":12}]}',
        422,
    ),
    "empty-text": (_text_body(""), 422),
    "extra-field": (json.dumps({"annotations": [_rect(zzz=1)]}).encode(), 422),
    "bad-type": (json.dumps({"annotations": [_rect(x="a")]}).encode(), 422),
    "control-chars": (_text_body("a\x01\x1b[31m"), 200),
    "unknown-shot": (json.dumps({"annotations": [_rect()]}).encode(), 404),
}


@_ac("AC-104.6")
def test_ac_104_6_render_matches_annotated_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.6"
    s = _stack(tmp_path)
    shot_id = _register(s, "shot.png")
    files_before = _snapshot(s.root)
    row_before = _row(s, shot_id)

    resp = s.client.post(f"{PREFIX}/{shot_id}/render", headers=AUTH, json={"annotations": MARKS})

    assert resp.status_code == 200, resp.text[:200]
    assert resp.headers["content-type"] == "image/png"
    assert _snapshot(s.root) == files_before
    assert _row(s, shot_id) == row_before
    assert row_before["sidecar_path"] is None

    saved = s.client.post(f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": MARKS})
    assert saved.status_code == 200, saved.text
    annotated = Path(str(_row(s, shot_id)["annotated_path"]))
    assert annotated.suffix == ".png"
    assert resp.content == annotated.read_bytes()


@pytest.mark.parametrize(
    "ac_id,case", [("AC-104.7", name) for name in CASES], ids=[f"AC-104.7-{name}" for name in CASES]
)
def test_ac_104_7_render_matches_annotate(ac_id: str, case: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.7"
    body, status = CASES[case]
    s = _stack(tmp_path)
    shot_id = "0" * 32 if case == "unknown-shot" else _register(s, "shot.png")

    render = s.client.post(f"{PREFIX}/{shot_id}/render", headers=JSON_HEADERS, content=body)
    annotate = s.client.post(f"{PREFIX}/{shot_id}/annotate", headers=JSON_HEADERS, content=body)

    assert render.status_code == status, render.text[:200]
    assert annotate.status_code == status, annotate.text[:200]
    if status == 422:
        assert render.json() == VALIDATION
        assert annotate.json() == VALIDATION
        for refused in ("ud800", "zzz", '"a"'):
            assert refused not in render.text
    elif status == 404:
        assert render.json().get("error", {}).get("code") == "NotFoundError"
        assert render.json() == annotate.json()
    else:
        assert render.headers["content-type"] == "image/png"
        annotated = Path(str(_row(s, shot_id)["annotated_path"]))
        assert render.content == annotated.read_bytes()
        assert "\x1b" not in render.headers.get("content-type", "")


def _assert_after_annotate(paths: list[str]) -> None:
    assert RENDER_PATH in paths
    assert paths.index(RENDER_PATH) == paths.index(ANNOTATE_PATH) + 1


@_ac("AC-104.8")
def test_ac_104_8_openapi_render_after_annotate(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-104.8"
    from tests.e2e.test_api_openapi import ROUTE_INDEX

    committed = json.loads(
        (Path(__file__).parents[2] / "openapi.committed.json").read_text(encoding="utf-8")
    )
    # D-700: the snapshot's keys are sorted, so adjacency is pinned on the live schema below.
    assert RENDER_PATH in committed["paths"]
    op = committed["paths"][RENDER_PATH]["post"]
    assert "image/png" in op["responses"]["200"]["content"]

    s = _stack(tmp_path)
    live = s.client.app.openapi()  # type: ignore[attr-defined]
    _assert_after_annotate(list(live["paths"]))
    assert live["paths"][RENDER_PATH] == committed["paths"][RENDER_PATH]

    index = list(ROUTE_INDEX)
    assert ("POST", RENDER_PATH) in index
    assert index.index(("POST", RENDER_PATH)) == index.index(("POST", ANNOTATE_PATH)) + 1
    assert len(index) == 79
