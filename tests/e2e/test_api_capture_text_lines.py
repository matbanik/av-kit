"""MEU-102 multi-line text marks through the API on the real stack (Session 70).

Every image is built with Pillow in the test's own tmp inbox; nothing reaches the network or a
user's capture inbox.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import build_services

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/captures"
SETTINGS = "/api/v1/settings/capture"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _ac102(n: int, suffix: str = ""):
    label = f"AC-102.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label + suffix])


@contextmanager
def _stack(app_data: Path, inbox: Path) -> Iterator[TestClient]:
    services, dispose = build_services(app_data=app_data, database_path=app_data / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            put = client.put(SETTINGS, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            yield client
    finally:
        dispose()


def _white_shot(tmp_path: Path) -> Path:
    from PIL import Image

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    Image.new("RGB", (160, 120), (255, 255, 255)).save(inbox / "shot.png", format="PNG")
    return inbox


def _shot_id(client: TestClient) -> str:
    items = client.get(PREFIX, headers=AUTH).json()["items"]
    ids = [item["id"] for item in items if Path(item["original_path"]).name == "shot.png"]
    assert len(ids) == 1, items
    return ids[0]


def _mark(text: object) -> dict[str, Any]:
    return {
        "type": "text",
        "x": 10,
        "y": 20,
        "text": text,
        "color": "#000000",
        "font_size": 16,
        "bg_color": "#FFD400",
    }


def _annotate(client: TestClient, shot_id: str, text: object) -> Any:
    body = {"annotations": [_mark(text)]}
    return client.post(f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json=body)


def _sidecar_texts(inbox: Path) -> list[str]:
    payload = json.loads((inbox / "shot.ann.json").read_text(encoding="utf-8"))
    return [item["text"] for item in payload["annotations"] if item["type"] == "text"]


def _pixels(path: Path) -> tuple[str, tuple[int, int], bytes]:
    from PIL import Image

    with Image.open(path) as image:
        return image.mode, image.size, image.tobytes()


def _openapi_drift() -> str | None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "export_openapi", REPO_ROOT / "tools" / "export_openapi.py"
    )
    assert spec is not None and spec.loader is not None
    export = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export)
    try:
        export.check_openapi(REPO_ROOT / "openapi.committed.json")
    except SystemExit as exc:
        return str(exc)
    return None


@_ac102(5)
@pytest.mark.e2e
def test_ac_102_5_annotate_stores_lf_and_refuses_non_str(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-102.5"
    inbox = _white_shot(tmp_path)
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client)
        refused = _annotate(client, shot_id, 918273645)
        assert refused.status_code == 422, refused.text
        assert refused.json()["error"]["code"] == "validation_error"
        assert "918273645" not in refused.text
        response = _annotate(client, shot_id, "Hi\r\nHi")
        assert response.status_code == 200, response.text
        assert "Hi\r\nHi" not in response.text
        assert _sidecar_texts(inbox) == ["Hi\nHi"]
    assert _openapi_drift() is None


@_ac102(17)
@pytest.mark.e2e
def test_ac_102_17_one_mark_traced_from_body_to_sidecar_and_png(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-102.17"
    from avkit_api.routes import captures as route
    from avkit_core.domain.capture import TextAnnotation
    from avkit_infra.capture.adapter import CaptureAdapter

    received: list[object] = []

    def recording(**fields: Any) -> TextAnnotation:
        received.append(fields["text"])
        return TextAnnotation(**fields)

    monkeypatch.setattr(route, "TextAnnotation", recording)
    inbox = _white_shot(tmp_path)
    with _stack(tmp_path, inbox) as client:
        shot_id = _shot_id(client)
        response = _annotate(client, shot_id, "Hi\r\nHi")
        assert response.status_code == 200, response.text
        annotated = Path(response.json()["annotated_path"])
    assert received == ["Hi\nHi"]
    assert _sidecar_texts(inbox) == ["Hi\nHi"]
    lf = TextAnnotation(
        x=10, y=20, text="Hi\nHi", color="#000000", font_size=16, bg_color="#FFD400"
    )
    expected = tmp_path / "expected.png"
    CaptureAdapter().bake(inbox / "shot.png", [lf], expected)
    assert _pixels(annotated) == _pixels(expected)
