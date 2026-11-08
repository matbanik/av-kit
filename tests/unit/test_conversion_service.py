"""MEU-30 ConversionService tests. Imports stay inside tests so collection cannot ERROR."""

from __future__ import annotations

import inspect
import threading
import time
from dataclasses import replace
from pathlib import Path
from typing import Self

import pytest

from avkit_core.domain.progress import MediaInfo, ProgressSnapshot


def _snapshot(frame: int = 3) -> ProgressSnapshot:
    return ProgressSnapshot(
        fraction=0.2,
        units_done=frame,
        units_total=10,
        unit_label="frames",
        rate=1.5,
        eta_seconds=8,
        error=None,
    )


class FakeConversionRepo:
    def __init__(self) -> None:
        self.rows: dict[str, object] = {}

    def add(self, job: object) -> None:
        self.rows[getattr(job, "id")] = job

    def get(self, job_id: str) -> object | None:
        return self.rows.get(job_id)

    def list_ordered(self) -> list[object]:
        return sorted(self.rows.values(), key=lambda item: getattr(item, "queue_position"))

    def save(self, job: object) -> None:
        self.rows[getattr(job, "id")] = job

    def reorder(self, job_ids: list[str]) -> None:
        for position, job_id in enumerate(job_ids):
            job = self.rows[job_id]
            self.rows[job_id] = replace(job, queue_position=position)

    def delete(self, job_id: str) -> None:
        self.rows.pop(job_id, None)

    def delete_all(self) -> None:
        self.rows.clear()


class FakeSettingsRepo:
    def __init__(self) -> None:
        self._rows: dict[tuple[str, str], object] = {}

    def get(self, namespace: str, key: str) -> object | None:
        return self._rows.get((namespace, key))

    def set(self, setting: object) -> None:
        self._rows[(getattr(setting, "namespace"), getattr(setting, "key"))] = setting

    def get_namespace(self, namespace: str) -> list[object]:
        return [row for (ns, _key), row in self._rows.items() if ns == namespace]

    def set_namespace(self, namespace: str, settings: list[object]) -> None:
        for key in [key for ns, key in list(self._rows) if ns == namespace]:
            self._rows.pop((namespace, key), None)
        for setting in settings:
            self.set(setting)


class FakeCaptureShotRepo:
    def __init__(self) -> None:
        self.rows: dict[str, object] = {}

    def add(self, shot: object) -> None:
        self.rows[getattr(shot, "id")] = shot

    def get(self, shot_id: str) -> object | None:
        return self.rows.get(shot_id)

    def list(self) -> list[object]:
        return list(self.rows.values())

    def save(self, shot: object) -> None:
        self.rows[getattr(shot, "id")] = shot

    def delete(self, shot_id: str) -> None:
        self.rows.pop(shot_id, None)

    def get_by_path(self, original_path: Path) -> object | None:
        for shot in self.rows.values():
            if getattr(shot, "original_path") == original_path:
                return shot
        return None


class FakeCaptureRequestRepo:
    def __init__(self) -> None:
        self.rows: dict[str, object] = {}

    def add(self, request: object) -> None:
        self.rows[getattr(request, "id")] = request

    def get(self, request_id: str) -> object | None:
        return self.rows.get(request_id)

    def save(self, request: object) -> None:
        self.rows[getattr(request, "id")] = request

    def list(self) -> list[object]:
        return list(self.rows.values())

    def get_pending_request(self) -> object | None:
        for request in self.rows.values():
            status = getattr(request, "status")
            name = getattr(status, "name", status)
            if name == "Pending":
                return request
        return None


class FakeUnitOfWork:
    def __init__(self) -> None:
        self.settings = FakeSettingsRepo()
        self.conversion_jobs = FakeConversionRepo()
        self.capture_shots = FakeCaptureShotRepo()
        self.capture_requests = FakeCaptureRequestRepo()
        self.commits = 0
        self.enters = 0
        self.file_deletes = 0

    def __enter__(self) -> Self:
        self.enters += 1
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        return None


class SharedFakeFactory:
    def __init__(self, uow: FakeUnitOfWork) -> None:
        self.uow = uow

    def __call__(self) -> FakeUnitOfWork:
        return self.uow


class RecordingMedia:
    def __init__(
        self,
        *,
        probe: MediaInfo | None = None,
        fail_probe: Path | None = None,
        fail_probe_exc: Exception | None = None,
        gpu: object | None = None,
    ) -> None:
        self.probe_payload = probe
        self.fail_probe = fail_probe
        self.fail_probe_exc = fail_probe_exc
        self.gpu = gpu
        self.inflight = 0
        self.max_inflight = 0
        self.encode_calls = 0
        self.encode_options: list[object] = []
        self.q_writes: list[str] = []
        self.convert_calls: list[object] = []
        self.started = threading.Event()
        self.hold = False

    def is_available(self) -> bool:
        return True

    def ffmpeg_version(self) -> str | None:
        return "7.0"

    def convert(self, input_path: Path, output_path: Path, options: object) -> None:
        self.convert_calls.append((input_path, output_path, options))

    def probe(self, file_path: Path) -> MediaInfo:
        from avkit_core.domain.errors import MediaProbeError

        if self.fail_probe is not None and file_path == self.fail_probe:
            if self.fail_probe_exc is not None:
                raise self.fail_probe_exc
            raise MediaProbeError("not media")
        if self.probe_payload is not None:
            return self.probe_payload
        return MediaInfo(
            duration=2.0,
            container="mp4",
            video_codec="hevc",
            audio_codec="aac",
            sample_rate=48000,
            channels=2,
            width=1920,
            height=1080,
            fps=30.0,
            bit_depth=8,
            field_order="progressive",
            streams=None,
        )

    def detect_gpu(self):  # type: ignore[no-untyped-def]
        from avkit_core.domain.conversion import GPUCapabilities

        if self.gpu is not None:
            return self.gpu
        return GPUCapabilities(
            nvidia_nvenc=False,
            amd_amf=False,
            intel_qsv=False,
            vulkan=False,
            software_h265=True,
            software_h264=True,
            recommended_encoder="libx265",
            checked_at=None,
        )

    def encode(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        self.encode_calls += 1
        self.encode_options.append(options)
        self.inflight += 1
        self.max_inflight = max(self.max_inflight, self.inflight)
        self.started.set()
        try:
            on_progress(_snapshot(1))
            if self.hold:
                while not should_stop():  # type: ignore[operator]
                    time.sleep(0.01)
                self.q_writes.append("q")
                return
            time.sleep(0.05)
            on_progress(_snapshot(5))
        finally:
            self.inflight -= 1

    def cut(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        self.encode(input_path, output_path, options, on_progress, should_stop)

    def extract_stream(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        self.encode(input_path, output_path, options, on_progress, should_stop)


def _stack(tmp_path: Path, media: RecordingMedia | None = None):
    from avkit_core.services.conversion import ConversionService
    from avkit_core.services.settings import SettingsService

    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("converter", "output_dir", str(tmp_path))
    settings.set("converter", "skip_existing", False)
    settings.set("converter", "default_preset", "balanced")
    settings.set("converter", "gpu_preference", "auto")
    media_port = media or RecordingMedia()
    service = ConversionService(factory, media=media_port, settings=settings)
    return service, uow, media_port, settings


def _write_clip(tmp_path: Path, name: str = "clip.mp4") -> Path:
    path = tmp_path / name
    path.write_bytes(b"media")
    return path


@pytest.mark.parametrize("ac_id", ["AC-30.1"], ids=["AC-30.1"])
@pytest.mark.unit
def test_ac_30_1_add_to_queue_probe_failure_continues(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.1"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    good = _write_clip(tmp_path, "good.mp4")
    bad = _write_clip(tmp_path, "bad.mp4")
    media = RecordingMedia(fail_probe=bad)
    service, uow, _media, _settings = _stack(tmp_path, media)
    jobs = service.add_to_queue(
        [good, bad],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    assert len(jobs) == 2
    statuses = {job.input_path.name: job.status for job in jobs}
    assert statuses["good.mp4"] is ConversionStatus.Pending
    assert statuses["bad.mp4"] is ConversionStatus.Failed
    assert len(uow.conversion_jobs.list_ordered()) == 2


@pytest.mark.parametrize("ac_id", ["AC-30.2"], ids=["AC-30.2"])
@pytest.mark.unit
def test_ac_30_2_output_name_suffix_and_skip_existing(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.2"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    clip = _write_clip(tmp_path)
    service, _uow, _media, settings = _stack(tmp_path)
    first = service.add_to_queue([clip], ConversionAddSpec(kind=ConversionKind.Compress))[0]
    assert first.output_path.name == "clip_compress.mp4"
    first.output_path.write_bytes(b"existing")
    second = service.add_to_queue([clip], ConversionAddSpec(kind=ConversionKind.Compress))[0]
    assert second.output_path.name == "clip_compress_1.mp4"
    settings.set("converter", "skip_existing", True)
    third = service.add_to_queue([clip], ConversionAddSpec(kind=ConversionKind.Compress))[0]
    assert third.status is ConversionStatus.Skipped
    assert third.output_path == first.output_path
    assert first.output_path.read_bytes() == b"existing"


@pytest.mark.parametrize("ac_id", ["AC-30.3"], ids=["AC-30.3"])
@pytest.mark.unit
def test_ac_30_3_one_ffmpeg_at_a_time(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.3"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    a = _write_clip(tmp_path, "a.mp4")
    b = _write_clip(tmp_path, "b.mp4")
    media = RecordingMedia()
    service, _uow, media, _settings = _stack(tmp_path, media)
    service.add_to_queue([a, b], ConversionAddSpec(kind=ConversionKind.Compress))
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert media.max_inflight <= 1
    assert media.encode_calls == 2


@pytest.mark.parametrize("ac_id", ["AC-30.4"], ids=["AC-30.4"])
@pytest.mark.unit
def test_ac_30_4_start_while_processing_conflict(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.4"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.domain.errors import ConflictError
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia()
    media.hold = True
    service, _uow, media, _settings = _stack(tmp_path, media)
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    service.start_processing()
    assert media.started.wait(timeout=1)
    with pytest.raises(ConflictError):
        service.start_processing()
    service.cancel_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)


@pytest.mark.parametrize("ac_id", ["AC-30.5"], ids=["AC-30.5"])
@pytest.mark.unit
def test_ac_30_5_pause_after_current_file_never_job_paused(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-30.5"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus, QueueProcessorState
    from avkit_core.services.conversion import ConversionAddSpec

    a = _write_clip(tmp_path, "a.mp4")
    b = _write_clip(tmp_path, "b.mp4")
    service, uow, media, _settings = _stack(tmp_path)
    service.add_to_queue([a, b], ConversionAddSpec(kind=ConversionKind.Compress))
    service.start_processing()
    assert media.started.wait(timeout=1)
    service.pause_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert service.get_processor_state().state is QueueProcessorState.Paused
    for job in uow.conversion_jobs.list_ordered():
        assert job.status is not getattr(ConversionStatus, "Paused", None)
        assert job.status.name != "Paused"


@pytest.mark.parametrize("ac_id", ["AC-30.6"], ids=["AC-30.6"])
@pytest.mark.unit
def test_ac_30_6_cancel_writes_q_inflight_cancelled_rest_pending(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-30.6"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus, QueueProcessorState
    from avkit_core.services.conversion import ConversionAddSpec

    a = _write_clip(tmp_path, "a.mp4")
    b = _write_clip(tmp_path, "b.mp4")
    media = RecordingMedia()
    media.hold = True
    service, uow, media, _settings = _stack(tmp_path, media)
    service.add_to_queue([a, b], ConversionAddSpec(kind=ConversionKind.Compress))
    service.start_processing()
    assert media.started.wait(timeout=1)
    service.cancel_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert media.q_writes == ["q"]
    jobs = {job.input_path.name: job.status for job in uow.conversion_jobs.list_ordered()}
    assert jobs["a.mp4"] is ConversionStatus.Cancelled
    assert jobs["b.mp4"] is ConversionStatus.Pending
    assert service.get_processor_state().state is QueueProcessorState.Idle


@pytest.mark.parametrize("ac_id", ["AC-30.7"], ids=["AC-30.7"])
@pytest.mark.unit
def test_ac_30_7_converter_settings_key_table(ac_id: str) -> None:
    assert ac_id == "AC-30.7"
    from avkit_core.services.settings import SETTINGS_KEY_TABLE

    keys = {key for ns, key in SETTINGS_KEY_TABLE if ns == "converter"}
    assert keys == {"output_dir", "default_preset", "skip_existing", "gpu_preference"}
    assert SETTINGS_KEY_TABLE[("converter", "skip_existing")].default is True
    assert SETTINGS_KEY_TABLE[("converter", "default_preset")].default == "balanced"
    assert SETTINGS_KEY_TABLE[("converter", "gpu_preference")].default == "auto"
    assert SETTINGS_KEY_TABLE[("converter", "output_dir")].default == "~/Videos/av-kit"


@pytest.mark.parametrize("ac_id", ["AC-30.8"], ids=["AC-30.8"])
@pytest.mark.unit
def test_ac_30_8_tts_download_do_not_use_conversion_service(ac_id: str) -> None:
    assert ac_id == "AC-30.8"
    from avkit_core.services import conversion as conversion_mod
    from avkit_core.services import download as download_mod
    from avkit_core.services import tts as tts_mod

    assert hasattr(conversion_mod, "ConversionService")
    assert "ConversionService" not in inspect.getsource(download_mod)
    assert "ConversionService" not in inspect.getsource(tts_mod)
    assert "conversion_jobs" not in inspect.getsource(download_mod)
    assert "conversion_jobs" not in inspect.getsource(tts_mod)


@pytest.mark.parametrize("ac_id", ["AC-30.9"], ids=["AC-30.9"])
@pytest.mark.unit
def test_ac_30_9_progress_uses_short_uow(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.9"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    service, uow, media, _settings = _stack(tmp_path)
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    before_enters = uow.enters
    before_commits = uow.commits
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert uow.enters > before_enters + 1
    assert uow.commits > before_commits
    assert media.encode_calls == 1
    done = service.get_queue()[0]
    assert done.speed_bps == 1.5
    assert done.eta_seconds == 8


@pytest.mark.parametrize("ac_id", ["AC-30.10"], ids=["AC-30.10"])
@pytest.mark.unit
def test_ac_30_10_reorder_clear_remove_keep_files(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.10"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    a = _write_clip(tmp_path, "a.mp4")
    b = _write_clip(tmp_path, "b.mp4")
    service, uow, _media, _settings = _stack(tmp_path)
    jobs = service.add_to_queue([a, b], ConversionAddSpec(kind=ConversionKind.Compress))
    out_a = jobs[0].output_path
    out_a.write_bytes(b"keep")
    ids = [jobs[1].id, jobs[0].id]
    service.reorder_queue(ids)
    ordered = [item.id for item in service.get_queue()]
    assert ordered == ids
    service.remove(jobs[1].id)
    assert service.get_job(jobs[0].id).id == jobs[0].id
    service.clear_queue()
    assert service.get_queue() == []
    assert out_a.exists()
    assert uow.file_deletes == 0


@pytest.mark.parametrize("ac_id", ["AC-30.11"], ids=["AC-30.11"])
@pytest.mark.unit
def test_ac_30_11_auto_gpu_never_fails_page(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.11"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    service, _uow, media, settings = _stack(tmp_path)
    settings.set("converter", "gpu_preference", "auto")
    caps = service.detect_gpu()
    assert caps.nvidia_nvenc is False
    assert caps.recommended_encoder == "libx265"
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert media.encode_calls == 1


@pytest.mark.parametrize("ac_id", ["AC-30.12"], ids=["AC-30.12"])
@pytest.mark.unit
def test_ac_30_12_g29_tmp_sqlite_add_list(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.12"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec, ConversionService
    from avkit_core.services.settings import SettingsService
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    settings.set("converter", "output_dir", str(tmp_path))
    settings.set("converter", "skip_existing", False)
    media = RecordingMedia()
    service = ConversionService(factory, media=media, settings=settings)
    clip = _write_clip(tmp_path)
    added = service.add_to_queue([clip], ConversionAddSpec(kind=ConversionKind.Compress))
    listed = service.get_queue()
    assert len(listed) == 1
    assert listed[0].id == added[0].id


@pytest.mark.parametrize("ac_id", ["AC-30.13"], ids=["AC-30.13"])
@pytest.mark.unit
def test_ac_30_13_extract_all_explodes_audio_streams(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-30.13"
    from avkit_core.domain.conversion import StreamInfo
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    streams = [
        StreamInfo(0, "audio", "aac", "eng", 2, 48000),
        StreamInfo(1, "audio", "ac3", "deu", 6, 48000),
        StreamInfo(2, "video", "hevc", None, None, None),
    ]
    info = MediaInfo(
        duration=1.0,
        container="mkv",
        video_codec="hevc",
        audio_codec="aac",
        sample_rate=48000,
        channels=2,
        width=1280,
        height=720,
        fps=24.0,
        bit_depth=8,
        field_order=None,
        streams=list(streams),
    )
    media = RecordingMedia(probe=info)
    service, uow, _media, _settings = _stack(tmp_path, media)
    clip = _write_clip(tmp_path, "movie.mkv")
    jobs = service.add_to_queue(
        [clip],
        ConversionAddSpec(kind=ConversionKind.Extract, stream_mode="all"),
    )
    assert len(jobs) == 2
    assert {job.stream_index for job in jobs} == {0, 1}
    paths = {job.output_path.name for job in jobs}
    assert len(paths) == 2
    assert len(uow.conversion_jobs.list_ordered()) == 2


@pytest.mark.parametrize("ac_id", ["AC-30.13"], ids=["AC-30.13-same-codec"])
@pytest.mark.unit
def test_ac_30_13_extract_all_same_codec_distinct_paths(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-30.13"
    from avkit_core.domain.conversion import StreamInfo
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    streams = [
        StreamInfo(0, "audio", "aac", "eng", 2, 48000),
        StreamInfo(1, "audio", "aac", "deu", 2, 48000),
    ]
    info = MediaInfo(
        duration=1.0,
        container="mkv",
        video_codec="hevc",
        audio_codec="aac",
        sample_rate=48000,
        channels=2,
        width=1280,
        height=720,
        fps=24.0,
        bit_depth=8,
        field_order=None,
        streams=list(streams),
    )
    media = RecordingMedia(probe=info)
    service, _uow, _media, _settings = _stack(tmp_path, media)
    clip = _write_clip(tmp_path, "movie.mkv")
    jobs = service.add_to_queue(
        [clip],
        ConversionAddSpec(kind=ConversionKind.Extract, stream_mode="all"),
    )
    assert len(jobs) == 2
    assert {job.stream_index for job in jobs} == {0, 1}
    paths = {job.output_path for job in jobs}
    assert len(paths) == 2
    names = {path.name for path in paths}
    assert len(names) == 2


@pytest.mark.parametrize("ac_id", ["AC-30.1"], ids=["AC-30.1-filesystem"])
@pytest.mark.unit
def test_ac_30_1_adapter_filesystem_probe_error_continues(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-30.1"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.domain.errors import FilesystemError
    from avkit_core.services.conversion import ConversionAddSpec

    good = _write_clip(tmp_path, "good.mp4")
    bad = _write_clip(tmp_path, "bad.mp4")
    media = RecordingMedia(fail_probe=bad, fail_probe_exc=FilesystemError("ffprobe failed"))
    service, uow, _media, _settings = _stack(tmp_path, media)
    jobs = service.add_to_queue(
        [good, bad],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    assert len(jobs) == 2
    statuses = {job.input_path.name: job.status for job in jobs}
    assert statuses["good.mp4"] is ConversionStatus.Pending
    assert statuses["bad.mp4"] is ConversionStatus.Failed
    assert len(uow.conversion_jobs.list_ordered()) == 2


@pytest.mark.parametrize("ac_id", ["AC-30.11"], ids=["AC-30.11-software-miss"])
@pytest.mark.unit
def test_ac_30_11_software_preference_raises_when_no_libx(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-30.11"
    from avkit_core.domain.conversion import GPUCapabilities
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.domain.errors import GpuUnavailableError
    from avkit_core.services.conversion import ConversionAddSpec

    caps = GPUCapabilities(
        nvidia_nvenc=False,
        amd_amf=False,
        intel_qsv=False,
        vulkan=False,
        software_h265=False,
        software_h264=False,
        recommended_encoder="libx264",
        checked_at=None,
    )
    media = RecordingMedia(gpu=caps)
    service, uow, _media, settings = _stack(tmp_path, media)
    settings.set("converter", "gpu_preference", "software")
    with pytest.raises(GpuUnavailableError):
        service._resolve_encoder(caps)
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    job = uow.conversion_jobs.list_ordered()[0]
    assert job.status is ConversionStatus.Failed
    assert job.error_message is not None
    assert "software" in job.error_message.lower() or "encoder" in job.error_message.lower()


@pytest.mark.parametrize("ac_id", ["AC-30.9"], ids=["AC-30.9-bit-depth"])
@pytest.mark.unit
def test_ac_30_9_encode_options_carry_probed_bit_depth(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-30.9"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    info = MediaInfo(
        duration=10.0,
        container="mp4",
        video_codec="hevc",
        audio_codec="aac",
        sample_rate=48000,
        channels=2,
        width=1920,
        height=1080,
        fps=30.0,
        bit_depth=10,
        field_order="progressive",
        streams=None,
    )
    media = RecordingMedia(probe=info)
    service, _uow, media, _settings = _stack(tmp_path, media)
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    assert media.encode_options
    options = media.encode_options[0]
    assert getattr(options, "bit_depth") == 10
    assert getattr(options, "duration_seconds") == 10.0


@pytest.mark.parametrize("ac_id", ["AC-109.5"], ids=["AC-109.5"])
@pytest.mark.unit
def test_ac_109_5_blocked_output_folder_fails_job_naming_path(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-109.5"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = tmp_path / "ffmpeg.exe"
    binary.write_text("fake", encoding="utf-8")
    blocker = tmp_path / "blocker-file"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    spawned: list[list[str]] = []

    def _popen(cmd: list[str], **_kwargs: object) -> object:
        spawned.append(list(cmd))
        raise RuntimeError("ffmpeg must not start")

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)

    class _RealEncode(RecordingMedia):
        def encode(
            self,
            input_path: Path,
            output_path: Path,
            options: object,
            on_progress: object,
            should_stop: object,
        ) -> None:
            FFmpegAdapter(configured_path=binary).encode(
                input_path,
                output_path,
                options,  # type: ignore[arg-type]
                on_progress,  # type: ignore[arg-type]
                should_stop,  # type: ignore[arg-type]
            )

    service, uow, _media, settings = _stack(tmp_path, _RealEncode())
    settings.set("converter", "output_dir", str(blocker / "sub"))
    clip = _write_clip(tmp_path)
    service.add_to_queue([clip], ConversionAddSpec(kind=ConversionKind.Compress))
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=5)
    job = uow.conversion_jobs.list_ordered()[0]
    assert spawned == []
    assert job.status is ConversionStatus.Failed
    assert "blocker-file" in (job.error_message or "")


def _nvidia_caps() -> object:
    from avkit_core.domain.conversion import GPUCapabilities

    return GPUCapabilities(
        nvidia_nvenc=True,
        amd_amf=False,
        intel_qsv=False,
        vulkan=False,
        software_h265=True,
        software_h264=True,
        recommended_encoder="hevc_nvenc",
        checked_at=None,
    )


def _run_compress(tmp_path: Path, *, setting: str, choice: object | None) -> tuple[object, object]:
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(gpu=_nvidia_caps())
    service, uow, _media, settings = _stack(tmp_path, media)
    settings.set("converter", "gpu_preference", setting)
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress, gpu_preference=choice),
    )
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    return uow.conversion_jobs.list_ordered()[0], media


@pytest.mark.parametrize("ac_id", ["AC-112.1"], ids=["AC-112.1"])
@pytest.mark.unit
def test_ac_112_1_job_software_runs_software_on_nvidia(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-112.1"
    from avkit_core.domain.enums import GpuPreference

    job, media = _run_compress(tmp_path, setting="auto", choice=GpuPreference.Software)
    assert job.gpu_encoder == "libx265"
    assert media.encode_options[0].codec == "libx265"


@pytest.mark.parametrize("ac_id", ["AC-112.2"], ids=["AC-112.2"])
@pytest.mark.unit
def test_ac_112_2_no_choice_reads_setting_when_job_runs(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-112.2"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(gpu=_nvidia_caps())
    service, uow, _media, settings = _stack(tmp_path, media)
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress),
    )
    settings.set("converter", "gpu_preference", "software")
    service.start_processing()
    if service._thread is not None:
        service._thread.join(timeout=2)
    job = uow.conversion_jobs.list_ordered()[0]
    assert job.gpu_encoder == "libx265"
    assert media.encode_options[0].codec == "libx265"


@pytest.mark.parametrize("ac_id", ["AC-112.3"], ids=["AC-112.3"])
@pytest.mark.unit
def test_ac_112_3_job_auto_beats_a_non_auto_setting(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-112.3"
    from avkit_core.domain.enums import GpuPreference

    job, media = _run_compress(tmp_path, setting="software", choice=GpuPreference.Auto)
    assert job.gpu_encoder == "hevc_nvenc"
    assert media.encode_options[0].codec == "hevc_nvenc"


@pytest.mark.parametrize("ac_id", ["AC-112.4"], ids=["AC-112.4-requeue"])
@pytest.mark.unit
def test_ac_112_4_choice_survives_a_requeue(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-112.4"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus, GpuPreference
    from avkit_core.services.conversion import ConversionAddSpec

    service, uow, _media, _settings = _stack(tmp_path, RecordingMedia(gpu=_nvidia_caps()))
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Compress, gpu_preference=GpuPreference.Software),
    )
    job = uow.conversion_jobs.list_ordered()[0]
    assert job.gpu_preference is GpuPreference.Software
    uow.conversion_jobs.save(replace(job, status=ConversionStatus.Failed, error_message="boom"))
    uow.commit()
    requeued = service.reset_failed(job.id)
    assert requeued.status is ConversionStatus.Pending
    assert requeued.gpu_preference is GpuPreference.Software


@pytest.mark.parametrize(
    ("ac_id", "kind_name", "extra"),
    [
        ("AC-112.4", "Cut", {"in_ms": 0, "out_ms": 1000}),
        ("AC-112.4", "Extract", {}),
    ],
    ids=["AC-112.4-cut", "AC-112.4-extract"],
)
@pytest.mark.unit
def test_ac_112_4_only_compress_stores_the_choice(
    ac_id: str, kind_name: str, extra: dict[str, int], tmp_path: Path
) -> None:
    assert ac_id == "AC-112.4"
    from avkit_core.domain.enums import ConversionKind, GpuPreference
    from avkit_core.services.conversion import ConversionAddSpec

    service, uow, _media, _settings = _stack(tmp_path, RecordingMedia(gpu=_nvidia_caps()))
    service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(
            kind=ConversionKind[kind_name], gpu_preference=GpuPreference.Software, **extra
        ),
    )
    job = uow.conversion_jobs.list_ordered()[0]
    assert job.gpu_preference is None


def _picture_first(*audio_codecs: str) -> MediaInfo:
    """A probe that lists the picture at stream 0 and one audio stream per codec after it."""
    from avkit_core.domain.conversion import StreamInfo

    streams: list[object] = [StreamInfo(0, "video", "h264", None, None, None)]
    streams += [
        StreamInfo(number + 1, "audio", codec, None, 2, 48000)
        for number, codec in enumerate(audio_codecs)
    ]
    return MediaInfo(
        duration=1.0,
        container="mov,mp4,m4a,3gp,3g2,mj2",
        video_codec="h264",
        audio_codec=audio_codecs[0] if audio_codecs else None,
        sample_rate=48000 if audio_codecs else None,
        channels=2 if audio_codecs else None,
        width=1280,
        height=720,
        fps=24.0,
        bit_depth=8,
        field_order=None,
        streams=streams,
    )


def _process(service: object) -> None:
    service.start_processing()  # type: ignore[attr-defined]
    thread = service._thread  # type: ignore[attr-defined]
    if thread is not None:
        thread.join(timeout=2)
        assert not thread.is_alive()


class GpuCountingMedia(RecordingMedia):
    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self.detect_gpu_calls = 0

    def detect_gpu(self):  # type: ignore[no-untyped-def]
        self.detect_gpu_calls += 1
        return super().detect_gpu()


@pytest.mark.parametrize("ac_id", ["AC-123.1"], ids=["AC-123.1"])
@pytest.mark.unit
def test_ac_123_1_first_mode_takes_audio_position_0(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.1"
    from avkit_core.domain.conversion import ExtractOptions
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(probe=_picture_first("aac"))
    service, _uow, _media, _settings = _stack(tmp_path, media)
    jobs = service.add_to_queue(
        [_write_clip(tmp_path)], ConversionAddSpec(kind=ConversionKind.Extract)
    )
    assert [(job.stream_index, job.output_path.name) for job in jobs] == [(0, "clip_a.m4a")]
    _process(service)
    assert media.encode_options == [ExtractOptions(stream_index=0, output_container="m4a")]


@pytest.mark.parametrize("ac_id", ["AC-123.2"], ids=["AC-123.2"])
@pytest.mark.unit
def test_ac_123_2_all_mode_plans_audio_positions(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.2"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(probe=_picture_first("aac", "ac3"))
    service, _uow, _media, _settings = _stack(tmp_path, media)
    jobs = service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Extract, stream_mode="all"),
    )
    assert [(job.stream_index, job.output_path.name) for job in jobs] == [
        (0, "clip_a0.m4a"),
        (1, "clip_a1.ac3"),
    ]
    _process(service)
    assert [getattr(options, "stream_index") for options in media.encode_options] == [0, 1]


@pytest.mark.parametrize("ac_id", ["AC-123.3"], ids=["AC-123.3"])
@pytest.mark.unit
def test_ac_123_3_all_mode_single_track_is_unnumbered(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.3"
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    service, _uow, _media, _settings = _stack(
        tmp_path, RecordingMedia(probe=_picture_first("aac"))
    )
    jobs = service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Extract, stream_mode="all"),
    )
    assert [(job.stream_index, job.output_path.name) for job in jobs] == [(0, "clip_a.m4a")]


@pytest.mark.parametrize(
    ("ac_id", "audio", "mode", "index", "message"),
    [
        ("AC-123.4", (), "first", None, "the file has no audio track"),
        ("AC-123.4", (), "all", None, "the file has no audio track"),
        ("AC-123.4", ("aac",), "first", 2, "no audio track a:2; the file has 1 audio track(s)"),
    ],
    ids=["AC-123.4-first-no-audio", "AC-123.4-all-no-audio", "AC-123.4-index-past-end"],
)
@pytest.mark.unit
def test_ac_123_4_missing_track_fails_at_add(
    ac_id: str,
    audio: tuple[str, ...],
    mode: str,
    index: int | None,
    message: str,
    tmp_path: Path,
) -> None:
    assert ac_id == "AC-123.4"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(probe=_picture_first(*audio))
    service, uow, _media, _settings = _stack(tmp_path, media)
    jobs = service.add_to_queue(
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Extract, stream_mode=mode, stream_index=index),
    )
    assert [(job.status, job.error_message) for job in jobs] == [
        (ConversionStatus.Failed, message)
    ]
    _process(service)
    assert [job.status for job in uow.conversion_jobs.list_ordered()] == [
        ConversionStatus.Failed
    ]
    assert media.encode_calls == 0


@pytest.mark.parametrize("ac_id", ["AC-123.5"], ids=["AC-123.5"])
@pytest.mark.unit
def test_ac_123_5_unknown_positions_fall_back_at_0_only(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.5"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia()
    assert media.probe(tmp_path / "any.mp4").streams is None
    service, _uow, _media, _settings = _stack(tmp_path, media)
    clip = _write_clip(tmp_path)
    found = [
        service.add_to_queue(
            [clip], ConversionAddSpec(kind=ConversionKind.Extract, stream_index=position)
        )
        for position in (0, 1)
    ]
    assert [[(job.output_path.suffix, job.status) for job in jobs] for jobs in found] == [
        [(".m4a", ConversionStatus.Pending)],
        [(".mka", ConversionStatus.Pending)],
    ]


@pytest.mark.parametrize("ac_id", ["AC-123.6"], ids=["AC-123.6-nvidia"])
@pytest.mark.unit
def test_ac_123_6_extract_saves_no_encoder(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.6"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    media = GpuCountingMedia(gpu=_nvidia_caps())
    service, uow, _media, _settings = _stack(tmp_path, media)
    service.add_to_queue([_write_clip(tmp_path)], ConversionAddSpec(kind=ConversionKind.Extract))
    _process(service)
    job = uow.conversion_jobs.list_ordered()[0]
    assert (job.status, job.gpu_encoder, media.detect_gpu_calls) == (
        ConversionStatus.Done,
        None,
        0,
    )


@pytest.mark.parametrize("ac_id", ["AC-123.6"], ids=["AC-123.6-software"])
@pytest.mark.unit
def test_ac_123_6_extract_needs_no_software_encoder(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.6"
    from avkit_core.domain.conversion import GPUCapabilities
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    caps = GPUCapabilities(
        nvidia_nvenc=False,
        amd_amf=False,
        intel_qsv=False,
        vulkan=False,
        software_h265=False,
        software_h264=False,
        recommended_encoder="libx264",
        checked_at=None,
    )
    service, uow, _media, settings = _stack(tmp_path, RecordingMedia(gpu=caps))
    settings.set("converter", "gpu_preference", "software")
    service.add_to_queue([_write_clip(tmp_path)], ConversionAddSpec(kind=ConversionKind.Extract))
    _process(service)
    job = uow.conversion_jobs.list_ordered()[0]
    assert (job.status, job.error_message, job.gpu_encoder) == (ConversionStatus.Done, None, None)


@pytest.mark.parametrize("ac_id", ["AC-123.7"], ids=["AC-123.7"])
@pytest.mark.unit
def test_ac_123_7_legacy_extract_row_runs_unchanged(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-123.7"
    from avkit_core.domain.conversion import ExtractOptions
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(gpu=_nvidia_caps())
    service, uow, _media, _settings = _stack(tmp_path, media)
    service.add_to_queue([_write_clip(tmp_path)], ConversionAddSpec(kind=ConversionKind.Extract))
    job = uow.conversion_jobs.list_ordered()[0]
    uow.conversion_jobs.save(
        replace(
            job,
            status=ConversionStatus.Failed,
            error_message="boom",
            stream_index=1,
            gpu_encoder="hevc_nvenc",
        )
    )
    uow.commit()
    service.reset_failed(job.id)
    _process(service)
    done = uow.conversion_jobs.list_ordered()[0]
    assert media.encode_options == [ExtractOptions(stream_index=1, output_container="m4a")]
    assert (done.status, done.gpu_encoder) == (ConversionStatus.Done, None)


@pytest.mark.parametrize(
    ("ac_id", "nvidia", "encoder"),
    [("AC-123.8", False, "libx265"), ("AC-123.8", True, "hevc_nvenc")],
    ids=["AC-123.8-default", "AC-123.8-nvidia-auto"],
)
@pytest.mark.unit
def test_ac_123_8_compress_still_saves_encoder(
    ac_id: str, nvidia: bool, encoder: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-123.8"
    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_core.services.conversion import ConversionAddSpec

    media = RecordingMedia(gpu=_nvidia_caps() if nvidia else None)
    service, uow, _media, _settings = _stack(tmp_path, media)
    service.add_to_queue([_write_clip(tmp_path)], ConversionAddSpec(kind=ConversionKind.Compress))
    _process(service)
    job = uow.conversion_jobs.list_ordered()[0]
    assert (job.status, job.gpu_encoder) == (ConversionStatus.Done, encoder)
    assert getattr(media.encode_options[0], "codec") == encoder
