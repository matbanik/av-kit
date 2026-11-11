"""MEU-31 conversion REST contract (AC-31.1–AC-31.22)."""

from __future__ import annotations

import threading
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from avkit_api.errors import DOMAIN_HTTP_MAP
from avkit_api.formatters import format_speed
from avkit_api.main import create_app
from avkit_api.wiring import AppServices
from avkit_core.domain.conversion import ConversionJob, GPUCapabilities
from avkit_core.domain.enums import (
    AudioEncodeMode,
    ConversionKind,
    ConversionPresetId,
    ConversionStatus,
    CutCopyMode,
    GpuPreference,
    QueueProcessorState,
)
from avkit_core.domain.errors import ConflictError, InvalidTimeRangeError, NotFoundError
from avkit_core.domain.queue import QueueRuntime
from avkit_core.domain.settings import SETTING_NAMESPACES
from avkit_core.services.conversion import ConversionAddSpec

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
PREFIX = "/api/v1/conversions"
JOB_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
SAMPLE_ENCODER = "hevc_nvenc"
GPU_COLD_GET_N = 2
GPU_COLD_JOIN_TIMEOUT_S = 2
CONVERTER_KEYS = ("output_dir", "default_preset", "skip_existing", "gpu_preference")
CONVERT_ROUTES = (
    ("POST", "/api/v1/conversions"),
    ("GET", "/api/v1/conversions"),
    ("GET", "/api/v1/conversions/gpu"),
    ("POST", "/api/v1/conversions/gpu/refresh"),
    ("POST", "/api/v1/conversions/probe"),
    ("POST", "/api/v1/conversions/start"),
    ("POST", "/api/v1/conversions/pause"),
    ("POST", "/api/v1/conversions/resume"),
    ("POST", "/api/v1/conversions/cancel"),
    ("PUT", "/api/v1/conversions/reorder"),
    ("DELETE", "/api/v1/conversions"),
    ("GET", "/api/v1/conversions/{id}"),
    ("POST", "/api/v1/conversions/{id}/reset"),
    ("DELETE", "/api/v1/conversions/{id}"),
)
STATIC_BEFORE_ID = (
    "/gpu",
    "/gpu/refresh",
    "/probe",
    "/start",
    "/pause",
    "/resume",
    "/cancel",
    "/reorder",
)
FORBIDDEN_RESPONSE_KEYS = ("media_bytes", "audio_bytes", "cookie_bytes")
JOB_OUT_FIELDS = (
    "id",
    "kind",
    "input_path",
    "output_path",
    "display_name",
    "preset_id",
    "cq",
    "scale_height",
    "audio_mode",
    "gpu_encoder",
    "in_ms",
    "out_ms",
    "copy_mode",
    "stream_index",
    "status",
    "progress",
    "speed",
    "eta",
    "file_size",
    "duration_seconds",
    "width",
    "height",
    "error_message",
    "queue_position",
    "created_at",
)


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
        self.data = {
            "converter": {
                "output_dir": "~/Videos/av-kit",
                "default_preset": "balanced",
                "skip_existing": True,
                "gpu_preference": "auto",
            }
        }
        self.commit_count = 0

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
            from avkit_core.domain.errors import ValidationError

            raise ValidationError("unknown settings key")
        self.data.setdefault(namespace, {}).update(mapping)
        self.commit_count += 1


class FakeHealth(_Lifecycle):
    def __init__(self) -> None:
        now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        self.events = [
            SimpleNamespace(
                seq=1,
                message="convert-ok",
                module="convert",
                timestamp=now,
                level="INFO",
            )
        ]

    def console_snapshot(self, after_seq: object = 0) -> list[SimpleNamespace]:
        if isinstance(after_seq, bool) or not isinstance(after_seq, int) or after_seq < 0:
            from avkit_core.domain.errors import ValidationError

            raise ValidationError("after_seq must be an int >= 0")
        return [event for event in self.events if event.seq > after_seq]


class FakeConversion(_Lifecycle):
    def __init__(self) -> None:
        now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        self.runtime = QueueRuntime("conversions", QueueProcessorState.Idle, None)
        self.jobs: list[ConversionJob] = []
        self.last_spec: ConversionAddSpec | None = None
        self.last_paths: list[Path] = []
        self.add_calls = 0
        self.reorder_calls = 0
        self.clear_calls = 0
        self.remove_calls: list[str] = []
        self.detect_calls = 0
        self.cancel_calls = 0
        self._gpu: GPUCapabilities | None = None
        self.entered = threading.Event()
        self.release = threading.Event()
        self.release.set()
        self._hold_detect = False
        self.sample_gpu = GPUCapabilities(
            nvidia_nvenc=True,
            amd_amf=False,
            intel_qsv=False,
            vulkan=False,
            software_h265=True,
            software_h264=True,
            recommended_encoder=SAMPLE_ENCODER,
            checked_at=now,
        )
        self._seed = ConversionJob(
            id=JOB_ID,
            kind=ConversionKind.Compress,
            input_path=Path("C:/tmp/in.mp4"),
            output_path=Path("C:/tmp/out.mp4"),
            display_name="in.mp4",
            preset_id=ConversionPresetId.Balanced,
            cq=25,
            scale_height=None,
            audio_mode=AudioEncodeMode.Aac128,
            gpu_encoder=SAMPLE_ENCODER,
            in_ms=None,
            out_ms=None,
            copy_mode=None,
            stream_index=None,
            status=ConversionStatus.Pending,
            progress=0.0,
            speed_bps=1.25,
            eta_seconds=90,
            file_size=None,
            duration_seconds=10.0,
            width=1920,
            height=1080,
            error_message=None,
            queue_position=0,
            created_at=now,
            updated_at=now,
        )

    def cancel_processing(self) -> None:
        self.cancel_calls += 1

    def get_queue(self) -> list[ConversionJob]:
        return list(self.jobs)

    def get_job(self, job_id: str) -> ConversionJob:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise NotFoundError(f"conversion job {job_id} not found")

    def get_processor_state(self) -> QueueRuntime:
        return self.runtime

    def get_gpu(self) -> GPUCapabilities | None:
        return self._gpu

    def detect_gpu(self) -> GPUCapabilities:
        self.detect_calls += 1
        self.entered.set()
        if self._hold_detect and not self.release.wait(timeout=GPU_COLD_JOIN_TIMEOUT_S):
            raise TimeoutError("detect_gpu release timed out")
        self._gpu = self.sample_gpu
        return self._gpu

    def add_to_queue(self, paths: list[Path], spec: ConversionAddSpec) -> list[ConversionJob]:
        self.add_calls += 1
        self.last_paths = list(paths)
        self.last_spec = spec
        job = self._seed
        self.jobs.append(job)
        return [job]

    def start_processing(self) -> None:
        if self.runtime.state is QueueProcessorState.Processing:
            raise ConflictError("conversion already processing")
        self.runtime = QueueRuntime("conversions", QueueProcessorState.Processing, JOB_ID)

    def pause_processing(self) -> None:
        self.runtime = QueueRuntime("conversions", QueueProcessorState.Paused, JOB_ID)

    def resume_processing(self) -> None:
        self.start_processing()

    def reorder_queue(self, job_ids: list[str]) -> None:
        self.reorder_calls += 1
        del job_ids

    def remove(self, job_id: str) -> None:
        self.remove_calls.append(job_id)
        self.jobs = [job for job in self.jobs if job.id != job_id]

    def clear_queue(self) -> None:
        self.clear_calls += 1
        self.jobs = []

    def reset_failed(self, job_id: str) -> ConversionJob:
        job = self.get_job(job_id)
        if job.status is not ConversionStatus.Failed:
            raise ConflictError("reset_failed is only valid from Failed")
        updated = job.reset_failed()
        self.jobs = [updated if item.id == job_id else item for item in self.jobs]
        return updated


class FakeDownload(_Lifecycle):
    def __init__(self) -> None:
        self.cancel_calls = 0

    def cancel_processing(self) -> None:
        self.cancel_calls += 1


def _services(conversion: FakeConversion, settings: FakeSettings | None = None) -> AppServices:
    life = _Lifecycle()
    return AppServices(
        download=FakeDownload(),
        transcript=life,
        tts=life,
        models=life,
        settings=settings or FakeSettings(),
        health=FakeHealth(),
        conversion=conversion,
        capture=life,
    )


def _client(
    conversion: FakeConversion | None = None,
    settings: FakeSettings | None = None,
) -> tuple[TestClient, FakeConversion]:
    fake = conversion or FakeConversion()
    app = create_app(tokens=TOKENS, services=_services(fake, settings), engine_dispose=None)
    return TestClient(app), fake


def _ac(n: int):
    label = f"AC-31.{n}"
    return pytest.mark.parametrize("ac_id", [label], ids=[label])


@_ac(1)
def test_ac_31_1_post_compress(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.1"
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"x")
    client, fake = _client()
    extra = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [str(media.resolve())], "kind": "compress", "nope": True},
    )
    assert extra.status_code == 422
    response = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [str(media.resolve())], "kind": "compress", "preset": "balanced"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "items" in body
    assert fake.last_spec is not None
    assert fake.last_spec.kind is ConversionKind.Compress
    assert fake.last_spec.preset_id is ConversionPresetId.Balanced
    denied = client.post(
        PREFIX,
        json={"paths": [str(media.resolve())], "kind": "compress"},
    )
    assert denied.status_code == 401


@_ac(2)
def test_ac_31_2_list_envelope(ac_id: str) -> None:
    assert ac_id == "AC-31.2"
    client, fake = _client()
    fake.jobs = [fake._seed]
    response = client.get(PREFIX, headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, dict)
    assert "items" in body
    assert "processor" in body
    assert body["processor"]["state"] in {"Idle", "Processing", "Paused"}


@_ac(3)
def test_ac_31_3_gpu_lazy_get_sequential(ac_id: str) -> None:
    assert ac_id == "AC-31.3"
    client, fake = _client()
    first = client.get(f"{PREFIX}/gpu", headers=AUTH)
    assert first.status_code == 200
    payload = first.json()
    assert payload["recommended_encoder"] == SAMPLE_ENCODER
    assert "probed" not in payload
    assert fake.detect_calls == 1
    second = client.get(f"{PREFIX}/gpu", headers=AUTH)
    assert second.status_code == 200
    assert fake.detect_calls == 1


@_ac(4)
def test_ac_31_4_gpu_refresh_reprobes(ac_id: str) -> None:
    assert ac_id == "AC-31.4"
    client, fake = _client()
    client.get(f"{PREFIX}/gpu", headers=AUTH)
    assert fake.detect_calls == 1
    refresh = client.post(f"{PREFIX}/gpu/refresh", headers=AUTH)
    assert refresh.status_code == 200
    assert fake.detect_calls == 2
    assert refresh.json()["recommended_encoder"] == SAMPLE_ENCODER


@_ac(5)
def test_ac_31_5_start_conflict(ac_id: str) -> None:
    assert ac_id == "AC-31.5"
    client, fake = _client()
    ok = client.post(f"{PREFIX}/start", headers=AUTH)
    assert ok.status_code == 202
    fake.runtime = QueueRuntime("conversions", QueueProcessorState.Processing, JOB_ID)
    conflict = client.post(f"{PREFIX}/start", headers=AUTH)
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"]


@_ac(6)
def test_ac_31_6_pause_resume_cancel(ac_id: str) -> None:
    assert ac_id == "AC-31.6"
    client, _fake = _client()
    for action in ("pause", "resume", "cancel"):
        response = client.post(f"{PREFIX}/{action}", headers=AUTH)
        assert response.status_code == 202


@_ac(7)
def test_ac_31_7_reorder(ac_id: str) -> None:
    assert ac_id == "AC-31.7"
    client, fake = _client()
    fake.jobs = [fake._seed]
    empty = client.put(f"{PREFIX}/reorder", headers=AUTH, json={"job_ids": []})
    assert empty.status_code == 422
    assert fake.reorder_calls == 0
    extra = client.put(
        f"{PREFIX}/reorder",
        headers=AUTH,
        json={"job_ids": [JOB_ID], "nope": 1},
    )
    assert extra.status_code == 422
    assert fake.reorder_calls == 0
    ok = client.put(f"{PREFIX}/reorder", headers=AUTH, json={"job_ids": [JOB_ID]})
    assert ok.status_code == 200
    assert "items" in ok.json()
    assert fake.reorder_calls == 1


@_ac(8)
def test_ac_31_8_clear_keeps_files(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.8"
    output = tmp_path / "keep.mp4"
    output.write_bytes(b"keep")
    client, fake = _client()
    fake.jobs = [fake._seed]
    response = client.delete(PREFIX, headers=AUTH)
    assert response.status_code == 204
    assert fake.clear_calls == 1
    assert output.is_file()


@_ac(9)
def test_ac_31_9_get_by_id(ac_id: str) -> None:
    assert ac_id == "AC-31.9"
    client, fake = _client()
    fake.jobs = [fake._seed]
    ok = client.get(f"{PREFIX}/{JOB_ID}", headers=AUTH)
    assert ok.status_code == 200
    missing = client.get(f"{PREFIX}/{uuid4()}", headers=AUTH)
    assert missing.status_code == 404
    assert missing.json()["error"]["code"]


@_ac(10)
def test_ac_31_10_reset_failed_only(ac_id: str) -> None:
    assert ac_id == "AC-31.10"
    client, fake = _client()
    fake.jobs = [fake._seed]
    pending = client.post(f"{PREFIX}/{JOB_ID}/reset", headers=AUTH)
    assert pending.status_code == 409
    failed = ConversionJob(
        id=fake._seed.id,
        kind=fake._seed.kind,
        input_path=fake._seed.input_path,
        output_path=fake._seed.output_path,
        display_name=fake._seed.display_name,
        preset_id=fake._seed.preset_id,
        cq=fake._seed.cq,
        scale_height=fake._seed.scale_height,
        audio_mode=fake._seed.audio_mode,
        gpu_encoder=fake._seed.gpu_encoder,
        in_ms=fake._seed.in_ms,
        out_ms=fake._seed.out_ms,
        copy_mode=fake._seed.copy_mode,
        stream_index=fake._seed.stream_index,
        status=ConversionStatus.Failed,
        progress=fake._seed.progress,
        speed_bps=fake._seed.speed_bps,
        eta_seconds=fake._seed.eta_seconds,
        file_size=fake._seed.file_size,
        duration_seconds=fake._seed.duration_seconds,
        width=fake._seed.width,
        height=fake._seed.height,
        error_message="boom",
        queue_position=fake._seed.queue_position,
        created_at=fake._seed.created_at,
        updated_at=fake._seed.updated_at,
    )
    fake.jobs = [failed]
    ok = client.post(f"{PREFIX}/{JOB_ID}/reset", headers=AUTH)
    assert ok.status_code == 200


@_ac(11)
def test_ac_31_11_delete_id_keeps_files(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.11"
    output = tmp_path / "stay.mp4"
    output.write_bytes(b"stay")
    client, fake = _client()
    fake.jobs = [fake._seed]
    response = client.delete(f"{PREFIX}/{JOB_ID}", headers=AUTH)
    assert response.status_code == 204
    assert fake.remove_calls == [JOB_ID]
    assert output.is_file()


@_ac(12)
def test_ac_31_12_path_precheck(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.12"
    client, fake = _client()
    clip = tmp_path / "clip.mp4"
    clip.write_bytes(b"x")
    relative = client.post(PREFIX, headers=AUTH, json={"paths": ["rel.mp4"], "kind": "compress"})
    missing = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [str((tmp_path / "nope.mp4").resolve())], "kind": "compress"},
    )
    directory = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [str(tmp_path.resolve())], "kind": "compress"},
    )
    unknown_preset = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [str(clip.resolve())], "kind": "compress", "preset": "ultra"},
    )
    assert relative.status_code == 422
    assert missing.status_code == 422
    assert directory.status_code == 422
    assert unknown_preset.status_code == 422
    assert fake.add_calls == 0


@_ac(13)
def test_ac_31_13_discriminated_union(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.13"
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"x")
    path = str(media.resolve())
    client, _fake = _client()
    cut_missing = client.post(PREFIX, headers=AUTH, json={"paths": [path], "kind": "cut"})
    extract_missing = client.post(PREFIX, headers=AUTH, json={"paths": [path], "kind": "extract"})
    cut_preset = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [path], "kind": "cut", "in_ms": 0, "out_ms": 10, "preset": "balanced"},
    )
    inverted = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [path], "kind": "cut", "in_ms": 10, "out_ms": 10},
    )
    assert cut_missing.status_code == 422
    assert extract_missing.status_code == 422
    assert cut_preset.status_code == 422
    assert inverted.status_code == 422


@_ac(14)
def test_ac_31_14_format_encode_speed(ac_id: str) -> None:
    assert ac_id == "AC-31.14"
    from avkit_api.formatters import format_encode_speed

    assert format_encode_speed(1.25) == "1.25x"
    assert format_encode_speed(None) is None
    speed = format_speed(1.25)
    assert speed is not None
    assert "B" in speed
    assert speed != "1.25x"


@_ac(15)
def test_ac_31_15_job_out_wires(ac_id: str) -> None:
    assert ac_id == "AC-31.15"
    client, fake = _client()
    fake.jobs = [fake._seed]
    response = client.get(f"{PREFIX}/{JOB_ID}", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    for key in JOB_OUT_FIELDS:
        assert key in body
    for banned in FORBIDDEN_RESPONSE_KEYS:
        assert banned not in body
    assert body["kind"] == "compress"
    assert body["preset_id"] == "balanced"
    assert body["audio_mode"] == "aac_128"
    assert body["speed"] == "1.25x"
    assert body["eta"] == "1:30"
    assert "speed_bps" not in body


@_ac(16)
def test_ac_31_16_converter_settings(ac_id: str) -> None:
    assert ac_id == "AC-31.16"
    settings = FakeSettings()
    client, _fake = _client(settings=settings)
    got = client.get("/api/v1/settings/converter", headers=AUTH)
    assert got.status_code == 200
    for key in CONVERTER_KEYS:
        assert key in got.json()
    put = client.put(
        "/api/v1/settings/converter",
        headers=AUTH,
        json={"default_preset": "sharing", "skip_existing": False, "gpu_preference": "nvidia"},
    )
    assert put.status_code == 200
    unknown_leaf = client.put(
        "/api/v1/settings/converter",
        headers=AUTH,
        json={"nope": True},
    )
    assert unknown_leaf.status_code == 422
    missing_ns = client.get("/api/v1/settings/nope", headers=AUTH)
    assert missing_ns.status_code == 404


@_ac(17)
def test_ac_31_17_openapi_static_auth_console(ac_id: str) -> None:
    assert ac_id == "AC-31.17"
    client, _fake = _client()
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]
    for method, path in CONVERT_ROUTES:
        assert path in paths
        ops = paths[path]
        assert method.lower() in ops
    unauth = client.get(PREFIX)
    assert unauth.status_code == 401
    console = client.get("/api/v1/health/console", headers=AUTH)
    assert console.status_code == 200
    modules = {item["module"] for item in console.json()["items"]}
    assert "convert" in modules
    src = Path("packages/api/src/avkit_api/routes/conversions.py").read_text(encoding="utf-8")
    gpu_pos = src.find('"/gpu"')
    id_pos = src.find("/{id}")
    assert gpu_pos != -1
    assert id_pos != -1
    for fragment in STATIC_BEFORE_ID:
        assert src.find(f'"{fragment}"') < id_pos


@_ac(18)
def test_ac_31_18_wiring_lifespan_time_range(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.18"
    assert DOMAIN_HTTP_MAP[InvalidTimeRangeError] == 422
    from avkit_api.wiring import build_services

    services, dispose = build_services(app_data=tmp_path, database_path=tmp_path / "avkit.db")
    try:
        assert getattr(services, "conversion", None) is not None
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
    conversion = FakeConversion()
    download = FakeDownload()
    life = _Lifecycle()
    bundled = AppServices(
        download=download,
        transcript=life,
        tts=life,
        models=life,
        settings=FakeSettings(),
        health=FakeHealth(),
        conversion=conversion,
        capture=life,
    )
    app = create_app(tokens=TOKENS, services=bundled, engine_dispose=None)
    with TestClient(app) as client:
        client.get("/api/v1/health", headers=AUTH)
    assert download.cancel_calls == 1
    assert conversion.cancel_calls == 1


@_ac(19)
def test_ac_31_19_compress_overrides(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.19"
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"x")
    client, fake = _client()
    response = client.post(
        PREFIX,
        headers=AUTH,
        json={
            "paths": [str(media.resolve())],
            "kind": "compress",
            "preset": "balanced",
            "cq": 18,
            "scale_height": 720,
            "audio_mode": "aac_192",
            "gpu_preference": "nvidia",
        },
    )
    assert response.status_code == 201
    spec = fake.last_spec
    assert spec is not None
    assert spec.cq == 18
    assert spec.scale_height == 720
    assert spec.audio_mode is AudioEncodeMode.Aac192
    assert spec.gpu_preference is GpuPreference.Nvidia


@_ac(20)
def test_ac_31_20_cut_copy_mode(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.20"
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"x")
    path = str(media.resolve())
    client, fake = _client()
    reencode = client.post(
        PREFIX,
        headers=AUTH,
        json={
            "paths": [path],
            "kind": "cut",
            "in_ms": 0,
            "out_ms": 1000,
            "copy_mode": "reencode",
        },
    )
    assert reencode.status_code == 201
    assert fake.last_spec is not None
    assert fake.last_spec.copy_mode is CutCopyMode.Reencode
    defaulted = client.post(
        PREFIX,
        headers=AUTH,
        json={"paths": [path], "kind": "cut", "in_ms": 0, "out_ms": 1000},
    )
    assert defaulted.status_code == 201
    assert fake.last_spec is not None
    assert fake.last_spec.copy_mode is CutCopyMode.FastCopy


@_ac(21)
def test_ac_31_21_extract_stream_index(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-31.21"
    media = tmp_path / "clip.mp4"
    media.write_bytes(b"x")
    client, fake = _client()
    response = client.post(
        PREFIX,
        headers=AUTH,
        json={
            "paths": [str(media.resolve())],
            "kind": "extract",
            "stream_mode": "first",
            "stream_index": 2,
        },
    )
    assert response.status_code == 201
    assert fake.last_spec is not None
    assert fake.last_spec.stream_index == 2
    assert fake.last_spec.stream_mode == "first"


@_ac(22)
def test_ac_31_22_gpu_cold_oracle(ac_id: str) -> None:
    assert ac_id == "AC-31.22"
    from avkit_api.routes.conversions import ensure_conversion_gpu

    fake = FakeConversion()
    fake.release.clear()
    fake._hold_detect = True
    results: list[GPUCapabilities] = []
    starter = threading.Barrier(GPU_COLD_GET_N)

    def _run() -> None:
        starter.wait()
        results.append(ensure_conversion_gpu(fake))

    workers = [threading.Thread(target=_run) for _ in range(GPU_COLD_GET_N)]
    for worker in workers:
        worker.start()
    assert fake.entered.wait(timeout=GPU_COLD_JOIN_TIMEOUT_S)
    assert fake.detect_calls == 1
    fake.release.set()
    for worker in workers:
        worker.join(timeout=GPU_COLD_JOIN_TIMEOUT_S)
        assert not worker.is_alive()
    assert fake.detect_calls == 1
    assert results
    assert {item.recommended_encoder for item in results} == {SAMPLE_ENCODER}
    client, wired = _client()
    gpu = client.get(f"{PREFIX}/gpu", headers=AUTH)
    assert gpu.status_code == 200
    assert wired.detect_calls >= 1
    src = Path("packages/api/src/avkit_api/routes/conversions.py").read_text(encoding="utf-8")
    assert "ensure_conversion_gpu" in src


# --- MEU-42 re-queue widening (AC-42.8) ---------------------------------------
REQUEUE_ROUTE_DOCSTRING_42 = "Re-queue a job from a re-queueable state."


@pytest.mark.parametrize("ac_id", ["AC-42.8"], ids=["AC-42.8"])
def test_ac_42_8_both_reset_routes_honor_widened_contract(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-42.8"
    from tests.e2e.real_stack import real_stack

    from avkit_core.domain.enums import DownloadStatus

    with real_stack(tmp_path / "avkit.db") as stack:
        for status in (DownloadStatus.Failed, DownloadStatus.Cancelled):
            job = stack.seed_download(status, error_message="boom")
            response = stack.client.post(
                f"/api/v1/downloads/{job.id}/reset", headers=AUTH
            )
            assert response.status_code == 200
            assert response.json()["status"] == "Pending"
        for status in (
            DownloadStatus.Pending,
            DownloadStatus.Downloading,
            DownloadStatus.Done,
            DownloadStatus.Skipped,
        ):
            job = stack.seed_download(status)
            refused = stack.client.post(f"/api/v1/downloads/{job.id}/reset", headers=AUTH)
            assert refused.status_code == 409
        missing = stack.client.post(f"/api/v1/downloads/{uuid4()}/reset", headers=AUTH)
        assert missing.status_code == 404
        extra = stack.seed_download(DownloadStatus.Failed)
        rejected = stack.client.post(
            f"/api/v1/downloads/{extra.id}/reset", headers=AUTH, json={"status": "Pending"}
        )
        assert rejected.status_code == 422

        for status in (ConversionStatus.Failed, ConversionStatus.Cancelled):
            conv = stack.seed_conversion(status, error_message="boom")
            response = stack.client.post(f"{PREFIX}/{conv.id}/reset", headers=AUTH)
            assert response.status_code == 200
            assert response.json()["status"] == "Pending"
        for status in (
            ConversionStatus.Pending,
            ConversionStatus.Processing,
            ConversionStatus.Done,
            ConversionStatus.Skipped,
        ):
            conv = stack.seed_conversion(status)
            refused = stack.client.post(f"{PREFIX}/{conv.id}/reset", headers=AUTH)
            assert refused.status_code == 409
        assert stack.client.post(f"{PREFIX}/{uuid4()}/reset", headers=AUTH).status_code == 404
        extra_conv = stack.seed_conversion(ConversionStatus.Failed)
        rejected_conv = stack.client.post(
            f"{PREFIX}/{extra_conv.id}/reset", headers=AUTH, json={"status": "Pending"}
        )
        assert rejected_conv.status_code == 422

    for relative in (
        "packages/api/src/avkit_api/routes/downloads.py",
        "packages/api/src/avkit_api/routes/conversions.py",
    ):
        source = Path(relative).read_text(encoding="utf-8")
        assert REQUEUE_ROUTE_DOCSTRING_42 in source
        assert "Reset a Failed job." not in source
