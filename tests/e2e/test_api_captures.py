"""MEU-37 capture REST contract (AC-37.1–AC-37.19)."""

from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from avkit_api.errors import DOMAIN_HTTP_MAP
from avkit_api.main import create_app
from avkit_api.schemas.settings import SettingsPutIn
from avkit_api.wiring import AppServices, build_services
from avkit_core.domain.capture import BBox, CaptureRequest, CaptureShot
from avkit_core.domain.enums import CaptureRequestStatus, CaptureSource
from avkit_core.domain.errors import (
    AnnotationValidationError,
    CaptureFailedError,
    CaptureNotSupportedError,
    CaptureRequestConflictError,
    InboxPathError,
    NotFoundError,
    ValidationError,
)
from avkit_core.domain.settings import SETTING_NAMESPACES
from avkit_core.ports.storage import CaptureRequestRepository
from avkit_core.services.capture import CaptureService

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/captures"
SHOT_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
REQ_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
NOW = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
ORIGINAL = Path("C:/tmp/inbox/shot.png")
IMAGE_MAX_BYTES = 15_728_640
CAPTURE_MIN_EDGE_PX = 8
# TA-4 (Session 30, MEU-67): + flatten_backup, backup_dir, annotated_format.
CAPTURE_KEYS = (
    "inbox_dir",
    "hotkey",
    "copy_to_clipboard",
    "close_to_tray",
    "flatten_backup",
    "backup_dir",
    "annotated_format",
)
CAPTURE_DEFAULTS = {
    "inbox_dir": "~/Pictures/av-kit",
    "hotkey": "F2",
    "copy_to_clipboard": False,
    "close_to_tray": True,
    "flatten_backup": True,  # TA-4 (Session 30, MEU-67)
    "backup_dir": "",
    "annotated_format": "png",
}
CAPTURE_ROUTES = (
    ("GET", "/api/v1/captures"),
    ("POST", "/api/v1/captures"),
    ("GET", "/api/v1/captures/requests"),
    ("POST", "/api/v1/captures/requests"),
    ("POST", "/api/v1/captures/requests/{id}/complete"),
    ("POST", "/api/v1/captures/requests/{id}/cancel"),
    ("GET", "/api/v1/captures/{id}"),
    ("GET", "/api/v1/captures/{id}/image"),
    ("POST", "/api/v1/captures/{id}/annotate"),
    ("DELETE", "/api/v1/captures/{id}"),
)
SHOT_OUT_FIELDS = (
    "id",
    "original_path",
    "annotated_path",
    "sidecar_path",
    "display_name",
    "width",
    "height",
    "file_size",
    "source",
    "created_at",
    "updated_at",
)
SHOT_DETAIL_OUT_FIELDS = SHOT_OUT_FIELDS + (
    "annotations",
    "backup_path",
)  # TA-8 (Session 30, MEU-67)
REQUEST_OUT_FIELDS = ("id", "status", "shot_id", "created_at", "expires_at")
SOURCE_OUT = (
    "Hotkey",
    "Gui",
    "McpFullscreen",
    "McpRegion",
    "McpInteractive",
    "Scan",
    "Import",
    "Crop",
    "Video",
)
STATUS_OUT = ("Pending", "Completed", "Cancelled", "Expired")
APPSERVICES_SITES = (
    "packages/api/src/avkit_api/wiring.py",
    "tools/export_openapi.py",
    "tests/e2e/api_fakes.py",
    "tests/e2e/test_api_downloads.py",
    "tests/e2e/test_api_health_settings.py",
    "tests/e2e/test_api_auth.py",
    "tests/e2e/test_api_conversions.py",
)
FORBIDDEN_RESPONSE_KEYS = ("media_bytes", "audio_bytes", "cookie_bytes", "image_bytes")
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"ok"


class _Lifecycle:
    def recover_stale_processing(self) -> None:
        return None

    def stop_processing(self) -> None:
        return None

    def unload(self) -> None:
        return None

    def cancel_processing(self) -> None:
        return None

    def liveness(self) -> SimpleNamespace:
        return SimpleNamespace(ok=True)

    def dependencies(self) -> SimpleNamespace:
        return SimpleNamespace(ffmpeg_version="6.0", ytdlp_version="2024.12")


class FakeSettings(_Lifecycle):
    def __init__(self) -> None:
        self.data = {"capture": dict(CAPTURE_DEFAULTS)}

    def get_namespace(self, namespace: str) -> dict[str, object]:
        if namespace not in SETTING_NAMESPACES:
            raise NotFoundError(f"unknown settings namespace {namespace}")
        return dict(self.data.get(namespace, {}))

    def set_namespace(self, namespace: str, mapping: dict[str, object]) -> None:
        if namespace not in SETTING_NAMESPACES:
            raise NotFoundError(f"unknown settings namespace {namespace}")
        known = set(self.data.get(namespace, {}))
        extra = set(mapping) - known
        if extra:
            raise ValidationError("unknown settings key")
        self.data.setdefault(namespace, {}).update(mapping)


class FakeHealth(_Lifecycle):
    def __init__(self) -> None:
        self.events = [
            SimpleNamespace(
                seq=1,
                message="capture-ok",
                module="capture",
                timestamp=NOW,
                level="INFO",
            )
        ]

    def console_snapshot(self, after_seq: object = 0) -> list[SimpleNamespace]:
        if isinstance(after_seq, bool) or not isinstance(after_seq, int) or after_seq < 0:
            raise ValidationError("after_seq must be an int >= 0")
        return [event for event in self.events if event.seq > after_seq]

    def record_startup_metric(self, name: str, value: object) -> None:
        del name, value


class FakeDownload(_Lifecycle):
    def __init__(self) -> None:
        self.cancel_calls = 0

    def cancel_processing(self) -> None:
        self.cancel_calls += 1


class FakeConversion(_Lifecycle):
    def __init__(self) -> None:
        self.cancel_calls = 0

    def cancel_processing(self) -> None:
        self.cancel_calls += 1


def _shot(
    *,
    shot_id: str = SHOT_ID,
    source: CaptureSource = CaptureSource.Hotkey,
    original: Path = ORIGINAL,
    annotated: Path | None = None,
) -> CaptureShot:
    return CaptureShot(
        id=shot_id,
        original_path=original,
        annotated_path=annotated,
        sidecar_path=None,
        display_name=original.name,
        width=32,
        height=32,
        file_size=12,
        source=source,
        created_at=NOW,
        updated_at=NOW,
    )


def _request(
    *,
    request_id: str = REQ_ID,
    status: CaptureRequestStatus = CaptureRequestStatus.Pending,
    shot_id: str | None = None,
    expires_at: datetime | None = None,
) -> CaptureRequest:
    return CaptureRequest(
        id=request_id,
        status=status,
        shot_id=shot_id,
        created_at=NOW,
        expires_at=expires_at if expires_at is not None else NOW + timedelta(seconds=120),
    )


class FakeCapture(_Lifecycle):
    def __init__(self) -> None:
        self.shots: list[CaptureShot] = [_shot()]
        self.requests: list[CaptureRequest] = []
        self.list_shots_calls = 0
        self.fullscreen_calls = 0
        self.region_bboxes: list[BBox] = []
        self.register_calls: list[tuple[Path, CaptureSource]] = []
        self.shot_inserts = 0
        self.expire_calls = 0
        self.remove_calls: list[str] = []
        self.image_bytes = PNG_BYTES
        self.grab_error: Exception | None = None
        self.cancel_calls = 0

    def cancel_processing(self) -> None:
        self.cancel_calls += 1

    def list_shots(self) -> list[CaptureShot]:
        self.list_shots_calls += 1
        self.expire_stale_requests()
        return list(self.shots)

    def get_shot(self, shot_id: str) -> CaptureShot:
        for shot in self.shots:
            if shot.id == shot_id:
                return shot
        raise NotFoundError(f"capture shot {shot_id} not found")

    def register_shot(self, path: Path, source: CaptureSource) -> CaptureShot:
        self.register_calls.append((path, source))
        self.shot_inserts += 1
        shot = _shot(source=source)
        self.shots.append(shot)
        return shot

    def capture_fullscreen(self) -> CaptureShot:
        self.fullscreen_calls += 1
        if self.grab_error is not None:
            raise self.grab_error
        return self.register_shot(ORIGINAL, CaptureSource.McpFullscreen)

    def capture_region(self, bbox: BBox) -> CaptureShot:
        self.region_bboxes.append(bbox)
        if self.grab_error is not None:
            raise self.grab_error
        return self.register_shot(ORIGINAL, CaptureSource.McpRegion)

    def request_interactive(self) -> CaptureRequest:
        self.expire_stale_requests()
        if any(item.status is CaptureRequestStatus.Pending for item in self.requests):
            raise CaptureRequestConflictError("a pending capture request already exists")
        request = _request()
        self.requests.append(request)
        return request

    def complete_request(self, request_id: str, path: Path) -> CaptureRequest:
        del path
        found = next((item for item in self.requests if item.id == request_id), None)
        if found is None:
            raise NotFoundError(f"capture request {request_id} not found")
        self.shot_inserts += 1
        shot = _shot(source=CaptureSource.McpInteractive)
        self.shots.append(shot)
        updated = _request(
            request_id=request_id,
            status=CaptureRequestStatus.Completed,
            shot_id=shot.id,
        )
        self.requests = [updated if item.id == request_id else item for item in self.requests]
        return updated

    def cancel_request(self, request_id: str) -> CaptureRequest:
        found = next((item for item in self.requests if item.id == request_id), None)
        if found is None:
            raise NotFoundError(f"capture request {request_id} not found")
        updated = _request(request_id=request_id, status=CaptureRequestStatus.Cancelled)
        self.requests = [updated if item.id == request_id else item for item in self.requests]
        return updated

    def expire_stale_requests(self) -> None:
        self.expire_calls += 1
        now = NOW
        updated: list[CaptureRequest] = []
        for item in self.requests:
            if item.status is CaptureRequestStatus.Pending and item.expires_at <= now:
                updated.append(
                    _request(
                        request_id=item.id,
                        status=CaptureRequestStatus.Expired,
                        expires_at=item.expires_at,
                    )
                )
            else:
                updated.append(item)
        self.requests = updated

    def list_requests(self, status: CaptureRequestStatus | None = None) -> list[CaptureRequest]:
        self.expire_stale_requests()
        rows = list(self.requests)
        if status is not None:
            rows = [item for item in rows if item.status is status]
        return rows

    def annotate_and_save(self, shot_id: str, annotations: list[object]) -> CaptureShot:
        shot = self.get_shot(shot_id)
        for item in annotations:
            color = getattr(item, "color", None)
            if color == "not-a-color":
                raise AnnotationValidationError("unknown color")
        return shot

    def load_shot_annotations(self, shot_id: str) -> list[object]:
        self.get_shot(shot_id)
        return []

    def latest_backup(self, shot_id: str) -> Path | None:
        # FIXTURE_REPAIRS (g) (Session 30): the detail route asks for the newest backup.
        self.get_shot(shot_id)
        return None

    def read_image(self, shot_id: str, variant: str) -> bytes:
        self.get_shot(shot_id)
        if variant == "annotated":
            shot = self.get_shot(shot_id)
            if shot.annotated_path is None:
                raise NotFoundError("annotated image not found")
        return self.image_bytes

    def remove(self, shot_id: str) -> None:
        self.get_shot(shot_id)
        self.remove_calls.append(shot_id)
        self.shots = [item for item in self.shots if item.id != shot_id]


def _services(
    capture: FakeCapture,
    *,
    settings: FakeSettings | None = None,
    health: FakeHealth | None = None,
    download: FakeDownload | None = None,
    conversion: FakeConversion | None = None,
) -> AppServices:
    life = _Lifecycle()
    kwargs: dict[str, Any] = {
        "download": download or FakeDownload(),
        "transcript": life,
        "tts": life,
        "models": life,
        "settings": settings or FakeSettings(),
        "health": health or FakeHealth(),
        "conversion": conversion or FakeConversion(),
    }
    params = inspect.signature(AppServices).parameters
    if "capture" in params:
        kwargs["capture"] = capture
    return AppServices(**kwargs)


def _client(
    capture: FakeCapture | None = None,
    **kwargs: Any,
) -> tuple[TestClient, FakeCapture]:
    fake = capture or FakeCapture()
    app = create_app(tokens=TOKENS, services=_services(fake, **kwargs), engine_dispose=None)
    return TestClient(app), fake


def _ac(n: int):
    label = f"AC-37.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


def _ac59(n: int):
    label = f"AC-59.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@_ac(1)
def test_ac_37_1_list_catalog(ac_id: str) -> None:
    assert ac_id == "AC-37.1"
    client, fake = _client()
    response = client.get(PREFIX, headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "processor" not in body
    assert fake.list_shots_calls == 1
    unauth = client.get(PREFIX)
    assert unauth.status_code == 401


@_ac(2)
def test_ac_37_2_register(ac_id: str) -> None:
    assert ac_id == "AC-37.2"
    client, fake = _client()
    response = client.post(
        PREFIX,
        headers=AUTH,
        json={"mode": "register", "path": str(ORIGINAL), "source": "hotkey"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "item" in body
    assert "items" not in body
    assert fake.register_calls[0][1] is CaptureSource.Hotkey
    extra = client.post(
        PREFIX,
        headers=AUTH,
        json={"mode": "register", "path": str(ORIGINAL), "source": "hotkey", "nope": 1},
    )
    assert extra.status_code == 422


@_ac(3)
def test_ac_37_3_fullscreen_and_grab_errors(ac_id: str) -> None:
    assert ac_id == "AC-37.3"
    client, fake = _client()
    response = client.post(PREFIX, headers=AUTH, json={"mode": "fullscreen"})
    assert response.status_code == 201
    assert fake.fullscreen_calls == 1
    failed = FakeCapture()
    failed.grab_error = CaptureFailedError("black frame")
    fail_client, _ = _client(failed)
    black = fail_client.post(PREFIX, headers=AUTH, json={"mode": "fullscreen"})
    assert black.status_code == 503
    assert DOMAIN_HTTP_MAP[CaptureFailedError] == 503
    unsupported = FakeCapture()
    unsupported.grab_error = CaptureNotSupportedError("no display")
    skip_client, _ = _client(unsupported)
    missing = skip_client.post(PREFIX, headers=AUTH, json={"mode": "fullscreen"})
    assert missing.status_code == 503
    assert DOMAIN_HTTP_MAP[CaptureNotSupportedError] == 503


@_ac(4)
def test_ac_37_4_region(ac_id: str) -> None:
    assert ac_id == "AC-37.4"
    client, fake = _client()
    response = client.post(
        PREFIX,
        headers=AUTH,
        json={"mode": "region", "x": 0, "y": 0, "width": 32, "height": 32},
    )
    assert response.status_code == 201
    assert fake.region_bboxes == [BBox(x=0, y=0, width=32, height=32)]
    tiny = client.post(
        PREFIX,
        headers=AUTH,
        json={"mode": "region", "x": 0, "y": 0, "width": 7, "height": 32},
    )
    assert tiny.status_code == 422
    assert CAPTURE_MIN_EDGE_PX == 8


@_ac(5)
def test_ac_37_5_list_requests(ac_id: str) -> None:
    assert ac_id == "AC-37.5"
    fake = FakeCapture()
    fake.requests = [
        _request(expires_at=NOW - timedelta(seconds=1)),
        _request(request_id="cccccccc-cccc-4ccc-8ccc-cccccccccccc"),
    ]
    client, bound = _client(fake)
    response = client.get(f"{PREFIX}/requests", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "processor" not in body
    assert bound.expire_calls >= 1
    statuses = {item["status"] for item in body["items"]}
    assert statuses <= set(STATUS_OUT)
    pending = client.get(f"{PREFIX}/requests", headers=AUTH, params={"status": "pending"})
    assert pending.status_code == 200
    for item in pending.json()["items"]:
        assert item["status"] == "Pending"
    unknown = client.get(f"{PREFIX}/requests", headers=AUTH, params={"status": "nope"})
    assert unknown.status_code == 422


@_ac(6)
def test_ac_37_6_interactive_create(ac_id: str) -> None:
    assert ac_id == "AC-37.6"
    client, _fake = _client()
    first = client.post(f"{PREFIX}/requests", headers=AUTH, json={})
    assert first.status_code == 201
    extra = client.post(f"{PREFIX}/requests", headers=AUTH, json={"nope": True})
    assert extra.status_code == 422
    second = client.post(f"{PREFIX}/requests", headers=AUTH, json={})
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "CaptureRequestConflictError"


@_ac(7)
def test_ac_37_7_complete_one_uow(ac_id: str) -> None:
    assert ac_id == "AC-37.7"
    fake = FakeCapture()
    fake.requests = [_request()]
    client, bound = _client(fake)
    ok = client.post(
        f"{PREFIX}/requests/{REQ_ID}/complete",
        headers=AUTH,
        json={"path": str(ORIGINAL)},
    )
    assert ok.status_code == 200
    assert ok.json()["status"] == "Completed"
    assert ok.json()["shot_id"] is not None
    extra = client.post(
        f"{PREFIX}/requests/{REQ_ID}/complete",
        headers=AUTH,
        json={"path": str(ORIGINAL), "nope": 1},
    )
    assert extra.status_code == 422
    unknown = FakeCapture()
    unknown.shot_inserts = 0
    unknown_client, unknown_fake = _client(unknown)
    missing = unknown_client.post(
        f"{PREFIX}/requests/{SHOT_ID}/complete",
        headers=AUTH,
        json={"path": str(ORIGINAL)},
    )
    assert missing.status_code == 404
    assert unknown_fake.shot_inserts == 0


@_ac(8)
def test_ac_37_8_cancel(ac_id: str) -> None:
    assert ac_id == "AC-37.8"
    fake = FakeCapture()
    fake.requests = [_request()]
    client, _bound = _client(fake)
    ok = client.post(f"{PREFIX}/requests/{REQ_ID}/cancel", headers=AUTH, json={})
    assert ok.status_code == 200
    assert ok.json()["status"] == "Cancelled"
    extra = client.post(
        f"{PREFIX}/requests/{REQ_ID}/cancel",
        headers=AUTH,
        json={"nope": 1},
    )
    assert extra.status_code == 422


@_ac(9)
def test_ac_37_9_get_metadata(ac_id: str) -> None:
    assert ac_id == "AC-37.9"
    client, _fake = _client()
    response = client.get(f"{PREFIX}/{SHOT_ID}", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == SHOT_ID
    assert isinstance(body["original_path"], str)
    assert b"\x89PNG" not in response.content
    missing = client.get(f"{PREFIX}/{REQ_ID}", headers=AUTH)
    assert missing.status_code == 404


@_ac(10)
def test_ac_37_10_image(ac_id: str) -> None:
    assert ac_id == "AC-37.10"
    client, fake = _client()
    response = client.get(f"{PREFIX}/{SHOT_ID}/image", headers=AUTH, params={"variant": "original"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/png")
    assert response.content == PNG_BYTES
    defaulted = client.get(f"{PREFIX}/{SHOT_ID}/image", headers=AUTH)
    assert defaulted.status_code == 200
    unauth = client.get(f"{PREFIX}/{SHOT_ID}/image")
    assert unauth.status_code == 401
    missing = client.get(
        f"{PREFIX}/{SHOT_ID}/image",
        headers=AUTH,
        params={"variant": "annotated"},
    )
    assert missing.status_code == 404
    fake.image_bytes = b"x" * (IMAGE_MAX_BYTES + 1)
    oversize = client.get(f"{PREFIX}/{SHOT_ID}/image", headers=AUTH)
    assert oversize.status_code == 413
    jpeg = FakeCapture()
    jpeg.shots = [
        _shot(
            original=Path("C:/tmp/inbox/photo.jpg"),
            annotated=Path("C:/tmp/inbox/photo.annotated.png"),
        )
    ]
    jpeg.image_bytes = PNG_BYTES
    jpeg_client, _jpeg_fake = _client(jpeg)
    annotated = jpeg_client.get(
        f"{PREFIX}/{SHOT_ID}/image",
        headers=AUTH,
        params={"variant": "annotated"},
    )
    assert annotated.status_code == 200
    assert annotated.headers["content-type"].startswith("image/png")
    assert annotated.content.startswith(b"\x89PNG")
    jpeg_original = jpeg_client.get(
        f"{PREFIX}/{SHOT_ID}/image",
        headers=AUTH,
        params={"variant": "original"},
    )
    assert jpeg_original.status_code == 200
    assert jpeg_original.headers["content-type"].startswith("image/jpeg")
    webp = FakeCapture()
    webp.shots = [
        _shot(
            original=Path("C:/tmp/inbox/photo.webp"),
            annotated=Path("C:/tmp/inbox/photo.annotated.png"),
        )
    ]
    webp.image_bytes = PNG_BYTES
    webp_client, _webp_fake = _client(webp)
    webp_annotated = webp_client.get(
        f"{PREFIX}/{SHOT_ID}/image",
        headers=AUTH,
        params={"variant": "annotated"},
    )
    assert webp_annotated.status_code == 200
    assert webp_annotated.headers["content-type"].startswith("image/png")
    webp_original = webp_client.get(
        f"{PREFIX}/{SHOT_ID}/image",
        headers=AUTH,
        params={"variant": "original"},
    )
    assert webp_original.status_code == 200
    assert webp_original.headers["content-type"].startswith("image/webp")


@_ac(11)
def test_ac_37_11_annotate(ac_id: str) -> None:
    assert ac_id == "AC-37.11"
    client, _fake = _client()
    ok = client.post(
        f"{PREFIX}/{SHOT_ID}/annotate",
        headers=AUTH,
        json={
            "annotations": [
                {
                    "type": "arrow",
                    "from": [1, 1],
                    "to": [8, 8],
                    "color": "red",
                    "stroke_width": 2,
                }
            ]
        },
    )
    assert ok.status_code == 200
    empty = client.post(
        f"{PREFIX}/{SHOT_ID}/annotate",
        headers=AUTH,
        json={"annotations": []},
    )
    assert empty.status_code == 200
    extra = client.post(
        f"{PREFIX}/{SHOT_ID}/annotate",
        headers=AUTH,
        json={"annotations": [], "nope": 1},
    )
    assert extra.status_code == 422
    color = client.post(
        f"{PREFIX}/{SHOT_ID}/annotate",
        headers=AUTH,
        json={
            "annotations": [
                {
                    "type": "rect",
                    "x": 0,
                    "y": 0,
                    "width": 8,
                    "height": 8,
                    "color": "not-a-color",
                    "stroke_width": 1,
                }
            ]
        },
    )
    assert color.status_code == 422


@_ac59(11)
def test_ac_59_11_api_rejects_circle_and_marker(ac_id: str) -> None:
    assert ac_id == "AC-59.11"
    client, _fake = _client()
    for forbidden in ("circle", "marker"):
        response = client.post(
            f"{PREFIX}/{SHOT_ID}/annotate",
            headers=AUTH,
            json={"annotations": [{"type": forbidden, "x": 1, "y": 1, "r": 4}]},
        )
        assert response.status_code == 422


@_ac(12)
def test_ac_37_12_delete(ac_id: str) -> None:
    assert ac_id == "AC-37.12"
    client, fake = _client()
    response = client.delete(f"{PREFIX}/{SHOT_ID}", headers=AUTH)
    assert response.status_code == 204
    assert fake.remove_calls == [SHOT_ID]
    missing = client.delete(f"{PREFIX}/{REQ_ID}", headers=AUTH)
    assert missing.status_code == 404


@_ac(13)
def test_ac_37_13_settings_capture(ac_id: str) -> None:
    assert ac_id == "AC-37.13"
    settings = FakeSettings()
    client, _fake = _client(settings=settings)
    got = client.get("/api/v1/settings/capture", headers=AUTH)
    assert got.status_code == 200
    assert set(got.json()) == set(CAPTURE_KEYS)
    put = client.put(
        "/api/v1/settings/capture",
        headers=AUTH,
        json={"inbox_dir": "C:/tmp/inbox", "hotkey": "F3"},
    )
    assert put.status_code == 200
    assert "inbox_dir" in SettingsPutIn.model_fields
    extra = client.put(
        "/api/v1/settings/capture",
        headers=AUTH,
        json={"not_a_leaf": True},
    )
    assert extra.status_code == 422
    missing = client.get("/api/v1/settings/nope", headers=AUTH)
    assert missing.status_code == 404


@_ac(14)
def test_ac_37_14_openapi_and_console(ac_id: str) -> None:
    assert ac_id == "AC-37.14"
    client, _fake = _client()
    schema = client.app.openapi()
    paths = schema["paths"]
    for method, path in CAPTURE_ROUTES:
        assert path in paths
        assert method.lower() in paths[path]
    src = Path("packages/api/src/avkit_api/routes/captures.py").read_text(encoding="utf-8")
    requests_pos = src.find('"/requests"')
    id_pos = src.find("/{id}")
    assert requests_pos != -1
    assert id_pos != -1
    assert requests_pos < id_pos
    unauth = client.get(PREFIX)
    assert unauth.status_code == 401
    console = client.get("/api/v1/health/console", headers=AUTH)
    assert console.status_code == 200
    modules = {item["module"] for item in console.json()["items"]}
    assert "capture" in modules


@_ac(15)
def test_ac_37_15_wiring_lifespan_http_map(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-37.15"
    assert DOMAIN_HTTP_MAP[InboxPathError] == 422
    assert DOMAIN_HTTP_MAP[AnnotationValidationError] == 422
    assert DOMAIN_HTTP_MAP[CaptureFailedError] == 503
    assert DOMAIN_HTTP_MAP[CaptureNotSupportedError] == 503
    assert "capture" in inspect.signature(AppServices).parameters
    from avkit_api.wiring import build_services

    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        assert getattr(services, "capture", None) is not None
        app = create_app(
            tokens=frozenset({"g29-token"}),
            services=services,
            engine_dispose=dispose,
        )
        with TestClient(app) as client:
            listed = client.get(PREFIX, headers={"Authorization": "Bearer g29-token"})
        assert listed.status_code == 200
    finally:
        dispose()
    download = FakeDownload()
    conversion = FakeConversion()
    capture = FakeCapture()
    bundled = _services(capture, download=download, conversion=conversion)
    app = create_app(tokens=TOKENS, services=bundled, engine_dispose=None)
    with TestClient(app) as client:
        client.get("/api/v1/health", headers=AUTH)
    assert download.cancel_calls == 1
    assert conversion.cancel_calls == 1
    assert capture.cancel_calls == 0
    for site in APPSERVICES_SITES:
        text = Path(site).read_text(encoding="utf-8")
        assert "capture=" in text or "capture:" in text


@_ac(16)
def test_ac_37_16_discriminated_union(ac_id: str) -> None:
    assert ac_id == "AC-37.16"
    client, _fake = _client()
    missing_path = client.post(PREFIX, headers=AUTH, json={"mode": "register", "source": "gui"})
    assert missing_path.status_code == 422
    fullscreen_extra = client.post(
        PREFIX,
        headers=AUTH,
        json={"mode": "fullscreen", "x": 1},
    )
    assert fullscreen_extra.status_code == 422
    region_missing = client.post(
        PREFIX,
        headers=AUTH,
        json={"mode": "region", "x": 0, "y": 0, "width": 32},
    )
    assert region_missing.status_code == 422


@_ac(17)
def test_ac_37_17_out_wires(ac_id: str) -> None:
    assert ac_id == "AC-37.17"
    client, _fake = _client()
    response = client.get(f"{PREFIX}/{SHOT_ID}", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert tuple(body) == SHOT_DETAIL_OUT_FIELDS
    assert body["source"] in SOURCE_OUT
    assert body["source"] != "hotkey"
    for key in FORBIDDEN_RESPONSE_KEYS:
        assert key not in body
    fake = FakeCapture()
    fake.requests = [_request()]
    req_client, _bound = _client(fake)
    listed = req_client.get(f"{PREFIX}/requests", headers=AUTH)
    assert listed.status_code == 200
    item = listed.json()["items"][0]
    assert tuple(item) == REQUEST_OUT_FIELDS
    assert item["status"] in STATUS_OUT


@_ac(18)
def test_ac_37_18_list_requests_port(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-37.18"
    assert hasattr(CaptureRequestRepository, "list")
    assert hasattr(CaptureService, "list_requests")
    from avkit_infra.database.engine import create_session_factory, create_sqlite_engine
    from avkit_infra.database.repositories import SqlAlchemyCaptureRequestRepository
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    assert hasattr(SqlAlchemyCaptureRequestRepository, "list")
    from tests.unit.test_conversion_service import FakeCaptureRequestRepo as ConvertFake
    from tests.unit.test_services import FakeCaptureRequestRepo as CoreFake

    assert hasattr(CoreFake, "list")
    assert hasattr(ConvertFake, "list")
    adapter_src = Path("tests/unit/test_capture_adapter.py").read_text(encoding="utf-8")
    assert '"list"' in adapter_src or "'list'" in adapter_src
    db_path = tmp_path / "avkit.db"
    services, dispose = build_services(app_data=tmp_path, database_path=db_path)
    try:
        factory = create_session_factory(create_sqlite_engine(db_path))
        now = datetime.now(UTC)
        stale_id = str(uuid4())
        cancelled_id = str(uuid4())
        stale = CaptureRequest(
            id=stale_id,
            status=CaptureRequestStatus.Pending,
            shot_id=None,
            created_at=now - timedelta(minutes=10),
            expires_at=now - timedelta(seconds=30),
        )
        cancelled = CaptureRequest(
            id=cancelled_id,
            status=CaptureRequestStatus.Cancelled,
            shot_id=None,
            created_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(seconds=120),
        )
        with SqlAlchemyUnitOfWork(factory) as uow:
            uow.capture_requests.add(stale)
            uow.capture_requests.add(cancelled)
        with SqlAlchemyUnitOfWork(factory) as uow:
            listed = uow.capture_requests.list()
        assert [item.id for item in listed] == [cancelled_id, stale_id]
        assert listed[1].status is CaptureRequestStatus.Pending
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            response = client.get(f"{PREFIX}/requests", headers=AUTH)
        assert response.status_code == 200
        body = response.json()
        assert "processor" not in body
        ids = [item["id"] for item in body["items"]]
        assert ids == [cancelled_id, stale_id]
        statuses = {item["id"]: item["status"] for item in body["items"]}
        assert statuses[stale_id] == "Expired"
        assert statuses[cancelled_id] == "Cancelled"
        live = services.capture.list_requests()
        assert [item.id for item in live] == [cancelled_id, stale_id]
        assert live[1].status is CaptureRequestStatus.Expired
    finally:
        dispose()


@_ac(19)
def test_ac_37_19_path_id_str(ac_id: str) -> None:
    assert ac_id == "AC-37.19"
    client, _fake = _client()
    malformed = "not-a-uuid"
    for method, path in (
        ("GET", f"{PREFIX}/{malformed}"),
        ("DELETE", f"{PREFIX}/{malformed}"),
        ("GET", f"{PREFIX}/{malformed}/image"),
        ("POST", f"{PREFIX}/{malformed}/annotate"),
        ("POST", f"{PREFIX}/requests/{malformed}/complete"),
        ("POST", f"{PREFIX}/requests/{malformed}/cancel"),
    ):
        kwargs: dict[str, Any] = {"headers": AUTH}
        if method == "POST" and path.endswith("/complete"):
            kwargs["json"] = {"path": str(ORIGINAL)}
        elif method == "POST" and path.endswith("/annotate"):
            kwargs["json"] = {"annotations": []}
        elif method == "POST":
            kwargs["json"] = {}
        response = client.request(method, path, **kwargs)
        assert response.status_code == 404, path
        assert response.status_code != 422
        assert response.status_code != 500
        assert response.json()["error"]["code"] == "NotFoundError"


@_ac59(8)
def test_ac_59_8_detail_get_includes_annotations(ac_id: str) -> None:
    assert ac_id == "AC-59.8"
    client, _fake = _client()
    listed = client.get(PREFIX, headers=AUTH)
    assert listed.status_code == 200
    assert "annotations" not in listed.json()["items"][0]
    detail = client.get(f"{PREFIX}/{SHOT_ID}", headers=AUTH)
    assert detail.status_code == 200
    body = detail.json()
    assert "annotations" in body
    assert body["annotations"] == []


@_ac59(10)
def test_ac_59_10_named_colors_reject_chartreuse(ac_id: str) -> None:
    assert ac_id == "AC-59.10"
    from pydantic import ValidationError

    from avkit_api.schemas.captures import ArrowAnnotationIn

    with pytest.raises(ValidationError):
        ArrowAnnotationIn.model_validate(
            {
                "type": "arrow",
                "from": [0, 0],
                "to": [8, 8],
                "color": "chartreuse",
                "stroke_width": 2,
            }
        )


@_ac59(15)
def test_ac_59_15_openapi_detail_annotations_not_list(ac_id: str) -> None:
    assert ac_id == "AC-59.15"
    client, _fake = _client()
    schema = client.app.openapi()
    components = schema["components"]["schemas"]
    get_id = schema["paths"]["/api/v1/captures/{id}"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    list_get = schema["paths"]["/api/v1/captures"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    detail_name = str(get_id.get("$ref", "")).rsplit("/", 1)[-1]
    list_name = str(list_get.get("$ref", "")).rsplit("/", 1)[-1]
    detail_props = components[detail_name]["properties"]
    list_props = components[list_name]["properties"]
    list_item_ref = list_props["items"]["items"]["$ref"].rsplit("/", 1)[-1]
    assert "annotations" in detail_props
    assert "annotations" not in components[list_item_ref]["properties"]


def _ac84(n: int):
    label = f"AC-84.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@_ac84(2)
def test_ac_84_2_list_reconciles_a_deleted_annotated_copy(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-84.2"
    from PIL import Image

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    Image.new("RGB", (32, 32), (255, 255, 255)).save(inbox / "shot.png")
    rect = {"type": "rect", "x": 2, "y": 2, "width": 8, "height": 8}
    rect |= {"color": "red", "stroke_width": 2}
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            settings = "/api/v1/settings/capture"
            put = client.put(settings, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            shot_id = client.get(PREFIX, headers=AUTH).json()["items"][0]["id"]
            annotated = client.post(
                f"{PREFIX}/{shot_id}/annotate", headers=AUTH, json={"annotations": [rect]}
            )
            assert annotated.status_code == 200
            image = f"{PREFIX}/{shot_id}/image"
            before = client.get(PREFIX, headers=AUTH).json()["items"][0]
            assert before["annotated_path"] is not None
            assert before["sidecar_path"] is not None
            shown = client.get(image, headers=AUTH, params={"variant": "annotated"})
            assert shown.status_code == 200
            Path(before["annotated_path"]).unlink()
            after = client.get(PREFIX, headers=AUTH).json()["items"][0]
            assert after["id"] == shot_id
            assert after["annotated_path"] is None
            assert after["sidecar_path"] == before["sidecar_path"]
            detail = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
            assert detail.status_code == 200
            assert [mark["type"] for mark in detail.json()["annotations"]] == ["rect"]
            gone = client.get(image, headers=AUTH, params={"variant": "annotated"})
            assert gone.status_code == 404
    finally:
        dispose()


def _ac90(n: int):
    label = f"AC-90.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@_ac90(3)
def test_ac_90_3_annotate_pixelate_round_trip_and_bounds(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-90.3"
    import json

    from PIL import Image

    from avkit_api.schemas.captures import PixelateAnnotationIn

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    Image.new("RGB", (64, 48), (255, 255, 255)).save(inbox / "shot.png")
    sized = {"type": "pixelate", "x": 2, "y": 3, "width": 20, "height": 10, "block_size": 7}
    unsized = {"type": "pixelate", "x": 30, "y": 4, "width": 12, "height": 9}
    echoed = [sized, {**unsized, "block_size": 10}]
    refused_bodies = (
        {**sized, "block_size": 1},
        {**sized, "block_size": 101},
        {**sized, "color": "red"},
        {key: value for key, value in sized.items() if key != "width"},
    )
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            settings = "/api/v1/settings/capture"
            put = client.put(settings, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            shot_id = client.get(PREFIX, headers=AUTH).json()["items"][0]["id"]
            annotate = f"{PREFIX}/{shot_id}/annotate"
            saved = client.post(annotate, headers=AUTH, json={"annotations": [sized, unsized]})
            assert saved.status_code == 200, saved.text
            detail = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
            assert detail.status_code == 200, detail.text
            assert detail.json()["annotations"] == echoed
            sidecar = Path(saved.json()["sidecar_path"])
            assert json.loads(sidecar.read_text(encoding="utf-8"))["annotations"] == echoed
            for body in refused_bodies:
                refused = client.post(annotate, headers=AUTH, json={"annotations": [body]})
                assert refused.status_code == 422, body
            again = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
            assert again.json()["annotations"] == echoed
            live = client.app.openapi()["components"]["schemas"]
    finally:
        dispose()
    block = live["PixelateAnnotationIn"]["properties"]["block_size"]
    assert (block["minimum"], block["maximum"], block["default"]) == (2, 100, 10)
    assert live["PixelateAnnotationIn"]["additionalProperties"] is False
    mapping = live["AnnotateIn"]["properties"]["annotations"]["items"]["discriminator"]["mapping"]
    assert mapping["pixelate"] == "#/components/schemas/PixelateAnnotationIn"
    committed_path = Path(__file__).resolve().parents[2] / "openapi.committed.json"
    committed = json.loads(committed_path.read_text(encoding="utf-8"))["components"]["schemas"]
    assert committed["PixelateAnnotationIn"] == live["PixelateAnnotationIn"]
    assert PixelateAnnotationIn.model_fields["block_size"].default == 10


def _ac91(n: int):
    label = f"AC-91.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@_ac91(3)
def test_ac_91_3_annotate_eraser_round_trip_and_refusals(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-91.3"
    import json

    from PIL import Image

    from avkit_api.schemas.captures import EraserAnnotationIn

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    Image.new("RGB", (64, 48), (255, 255, 255)).save(inbox / "shot.png")
    eraser = {"type": "eraser", "x": 2, "y": 3, "width": 20, "height": 10}
    refused_bodies = (
        {**eraser, "color": "red"},
        {**eraser, "block_size": 10},
        {key: value for key, value in eraser.items() if key != "x"},
    )
    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        app = create_app(tokens=TOKENS, services=services, engine_dispose=dispose)
        with TestClient(app) as client:
            settings = "/api/v1/settings/capture"
            put = client.put(settings, headers=AUTH, json={"inbox_dir": str(inbox)})
            assert put.status_code == 200
            shot_id = client.get(PREFIX, headers=AUTH).json()["items"][0]["id"]
            annotate = f"{PREFIX}/{shot_id}/annotate"
            saved = client.post(annotate, headers=AUTH, json={"annotations": [eraser]})
            assert saved.status_code == 200, saved.text
            detail = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
            assert detail.status_code == 200, detail.text
            assert detail.json()["annotations"] == [eraser]
            sidecar = Path(saved.json()["sidecar_path"])
            assert json.loads(sidecar.read_text(encoding="utf-8"))["annotations"] == [eraser]
            for body in refused_bodies:
                refused = client.post(annotate, headers=AUTH, json={"annotations": [body]})
                assert refused.status_code == 422, body
            again = client.get(f"{PREFIX}/{shot_id}", headers=AUTH)
            assert again.json()["annotations"] == [eraser]
            live = client.app.openapi()["components"]["schemas"]
    finally:
        dispose()
    schema = live["EraserAnnotationIn"]
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == {"type", "x", "y", "width", "height"}
    mapping = live["AnnotateIn"]["properties"]["annotations"]["items"]["discriminator"]["mapping"]
    assert mapping["eraser"] == "#/components/schemas/EraserAnnotationIn"
    committed_path = Path(__file__).resolve().parents[2] / "openapi.committed.json"
    committed = json.loads(committed_path.read_text(encoding="utf-8"))["components"]["schemas"]
    assert committed["EraserAnnotationIn"] == live["EraserAnnotationIn"]
    assert set(EraserAnnotationIn.model_fields) == {"type", "x", "y", "width", "height"}
