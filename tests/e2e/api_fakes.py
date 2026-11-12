"""Shared TestClient fakes for Phase 4 REST contract tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from avkit_api.main import create_app
from avkit_api.wiring import AppServices
from avkit_core.domain.enums import (
    DeviceType,
    MediaFormat,
    ModelFormat,
    ModelPrecision,
    QueueProcessorState,
    TranscriptItemStatus,
    TranscriptStatus,
    TTSSourceKind,
    TTSStatus,
)
from avkit_core.domain.errors import ConflictError, NotFoundError, ValidationError
from avkit_core.domain.queue import QueueRuntime
from avkit_core.domain.settings import SETTING_NAMESPACES
from avkit_core.domain.transcript import TranscriptItem, TranscriptJob
from avkit_core.domain.tts import (
    AssetState,
    ModelAvailability,
    ModelDownloadRuntime,
    ModelStatus,
    ModelVariant,
    TTSJob,
    VoiceConfig,
)
from avkit_core.services.prepare import PREPARE_STEP_IDS

GUI_TOKEN = "gui-nonce-token"
TOKENS = frozenset({GUI_TOKEN, "mcp-api-key"})
AUTH = {"Authorization": f"Bearer {GUI_TOKEN}"}
JOB_A = "11111111-1111-4111-8111-111111111111"
JOB_B = "22222222-2222-4222-8222-222222222222"
ITEM_A = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
ITEM_B = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
TTS_JOB = "33333333-3333-4333-8333-333333333333"
VARIANT_ID = "kokoro-onnx-fp32"


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
        return SimpleNamespace(
            ffmpeg_version="6.0",
            ytdlp_version="2024.12",
            tts_onnx_vocab=AssetState.READY,
            tts_spacy_model=AssetState.READY,
            tts_spacy_version="3.8.0",
            tts_voice_packs=AssetState.READY,
            tts_espeak=SimpleNamespace(available=False, version=None, path=None),
            ffmpeg_path=None,
            ffprobe_available=False,
            # FIXTURE_REPAIRS (Session 66, MEU-141): the RUNTIME_HEALTH field.
            js_runtime=SimpleNamespace(
                available=False, name=None, path=None, version=None, source=None, solver=False
            ),
        )


class FakeFilesystem:
    def __init__(self) -> None:
        self.read_text_calls = 0

    def read_text(self, path: Path, max_bytes: int | None = None) -> str:
        del path, max_bytes
        self.read_text_calls += 1
        return "disk-text"


class FakeTranscript(_Lifecycle):
    def __init__(self) -> None:
        now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        self.runtime = QueueRuntime("transcripts", QueueProcessorState.Idle, None)
        self.jobs: list[TranscriptJob] = [
            TranscriptJob(
                id=JOB_A,
                channel_url="https://www.youtube.com/@demo",
                channel_name="Demo",
                status=TranscriptStatus.Pending,
                output_dir=Path("C:/tmp/transcripts"),
                video_count=2,
                word_count=10,
                zip_path=None,
                queue_position=0,
                error_message=None,
                created_at=now,
                updated_at=now,
            )
        ]
        older = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
        newer = datetime(2026, 1, 3, 0, 0, 0, tzinfo=UTC)
        self.last_reorder: list[str] = []
        self.items: dict[str, list[TranscriptItem]] = {
            JOB_A: [
                TranscriptItem(
                    id=ITEM_A,
                    job_id=JOB_A,
                    video_id="vid-a",
                    title="First",
                    language="en",
                    word_count=4,
                    path=Path("C:/tmp/transcripts/raw/first.md"),
                    status=TranscriptItemStatus.Done,
                    error_message=None,
                    retry_count=0,
                    processed_at=older,
                ),
                TranscriptItem(
                    id=ITEM_B,
                    job_id=JOB_A,
                    video_id="vid-b",
                    title="Latest",
                    language="en",
                    word_count=6,
                    path=None,
                    status=TranscriptItemStatus.Pending,
                    error_message=None,
                    retry_count=0,
                    processed_at=newer,
                ),
            ]
        }

    def add_channel(self, channel_url: str) -> TranscriptJob:
        now = datetime.now(UTC)
        job = TranscriptJob(
            id=str(uuid4()),
            channel_url=channel_url,
            channel_name="New",
            status=TranscriptStatus.Pending,
            output_dir=Path("C:/tmp/transcripts"),
            video_count=0,
            word_count=0,
            zip_path=None,
            queue_position=len(self.jobs),
            error_message=None,
            created_at=now,
            updated_at=now,
        )
        self.jobs.append(job)
        self.items[job.id] = []
        return job

    def get_queue(self) -> list[TranscriptJob]:
        return list(self.jobs)

    def get_processor_state(self) -> QueueRuntime:
        return self.runtime

    def get_job(self, job_id: str) -> TranscriptJob:
        for job in self.jobs:
            if job.id == job_id:
                return job
        raise NotFoundError(f"transcript job {job_id} not found")

    def list_items(self, job_id: str) -> list[TranscriptItem]:
        self.get_job(job_id)
        return list(self.items.get(job_id, []))

    def start_processing(self) -> None:
        return None

    def pause_processing(self) -> None:
        return None

    def resume_processing(self) -> None:
        return None

    def stop_processing(self) -> None:
        return None

    def reorder_queue(self, job_ids: list[str]) -> None:
        by_id = {job.id: job for job in self.jobs}
        self.jobs = [by_id[job_id] for job_id in job_ids if job_id in by_id]
        self.last_reorder = list(job_ids)

    def requeue_channel(self, job_id: str) -> TranscriptJob:
        job = self.get_job(job_id)
        updated = job.transition(TranscriptStatus.Pending)
        self.jobs = [updated if item.id == job_id else item for item in self.jobs]
        return updated

    def retry_failed_channel(self, job_id: str) -> TranscriptJob:
        job = self.get_job(job_id)
        updated = job.transition(TranscriptStatus.Pending)
        self.jobs = [updated if item.id == job_id else item for item in self.jobs]
        return updated

    def remove_channel(self, job_id: str) -> None:
        self.get_job(job_id)
        self.jobs = [job for job in self.jobs if job.id != job_id]

    def compile_channel(self, job_id: str) -> list[Path]:
        self.get_job(job_id)
        return [Path("C:/tmp/compiled/vol-1.md")]

    def set_status(self, job_id: str, status: TranscriptStatus) -> None:
        job = self.get_job(job_id)
        self.jobs = [
            TranscriptJob(
                id=job.id,
                channel_url=job.channel_url,
                channel_name=job.channel_name,
                status=status,
                output_dir=job.output_dir,
                video_count=job.video_count,
                word_count=job.word_count,
                zip_path=job.zip_path,
                queue_position=job.queue_position,
                error_message=job.error_message,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            if item.id == job_id
            else item
            for item in self.jobs
        ]


class FakeTTS(_Lifecycle):
    def __init__(self) -> None:
        self.list_voices_calls = 0
        self.busy = False
        self.model_loaded = True
        self.filesystem = FakeFilesystem()
        self.jobs: dict[str, TTSJob] = {}
        now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
        self.jobs[TTS_JOB] = TTSJob(
            id=TTS_JOB,
            source_kind=TTSSourceKind.Inline,
            source_path=None,
            text_hash="abc",
            text_preview="hello",
            voice="am_eric",
            speed=1.0,
            format=MediaFormat.MP3,
            status=TTSStatus.Pending,
            output_path=None,
            segments_total=1000,
            segments_done=0,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    def __getattribute__(self, name: str) -> object:
        if name == "_tts":
            raise AssertionError("VOICES_FACADE forbids reading _tts")
        return object.__getattribute__(self, name)

    def list_voices(self) -> list[tuple[VoiceConfig, SimpleNamespace]]:
        # MEU-74 (D-89): `TTSService.list_voices` pairs each voice with its availability.
        self.list_voices_calls += 1
        return [
            (
                VoiceConfig(
                    voice_id="am_eric",
                    lang_code="a",
                    language="American English",
                    gender="male",
                    style_description="Eric",
                ),
                SimpleNamespace(available=True, reason=None),
            )
        ]

    def prepare(
        self,
        text: str,
        enabled_steps: list[str],
        chunk_max_chars: int | None = None,
    ) -> str:
        del chunk_max_chars
        unknown = [step for step in enabled_steps if step not in PREPARE_STEP_IDS]
        if unknown:
            raise ValidationError("unknown prepare step")
        return text

    def generate(
        self,
        text: str,
        voice: str,
        speed: float,
        format: MediaFormat,
        enabled_steps: list[str],
        source_kind: TTSSourceKind,
        source_path: Path | None,
    ) -> TTSJob:
        del enabled_steps
        if not self.model_loaded:
            raise ConflictError("a TTS model must be loaded")
        if self.busy:
            raise ConflictError("a TTS generation is already in progress")
        now = datetime.now(UTC)
        job = TTSJob(
            id=str(uuid4()),
            source_kind=source_kind,
            source_path=source_path,
            text_hash="hash",
            text_preview=text[:200],
            voice=voice,
            speed=speed,
            format=format,
            status=TTSStatus.Generating,
            output_path=None,
            segments_total=1000,
            segments_done=0,
            error_message=None,
            created_at=now,
            updated_at=now,
        )
        self.jobs[job.id] = job
        return job

    def get_status(self, job_id: str) -> TTSJob:
        job = self.jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"tts job {job_id} not found")
        return job

    def cancel(self, job_id: str) -> None:
        self.get_status(job_id)


class FakeModels(_Lifecycle):
    def __init__(self) -> None:
        self.downloading = False
        self.variant = ModelVariant(
            id=VARIANT_ID,
            name="ONNX FP32",
            format=ModelFormat.ONNX,
            precision=ModelPrecision.FP32,
            size_bytes=1,
            path=None,
            is_downloaded=False,
        )
        self.runtime = ModelDownloadRuntime(None, None, "Idle", 0.0, None)
        self.status = ModelStatus(None, "unloaded", "cpu", 0, False)

    def list_available(self) -> list[ModelVariant]:
        return [self.variant]

    def list_downloaded(self) -> list[ModelVariant]:
        return [self.variant] if self.variant.is_downloaded else []

    def available_devices(self, fmt: ModelFormat) -> tuple[DeviceType, ...]:
        # TA-2 (Session 35, MEU-75): every route that builds `ModelVariantOut` asks for this.
        del fmt
        return (DeviceType.Auto, DeviceType.CPU)

    def availability(self, fmt: ModelFormat) -> ModelAvailability:
        # TA-3 (Session 51, MEU-117): every route that builds `ModelVariantOut` asks for this.
        del fmt
        return ModelAvailability(True, None)

    def download(self, variant_id: str) -> ModelVariant:
        if self.downloading:
            raise ConflictError("a model download is already in progress")
        if variant_id != self.variant.id:
            raise NotFoundError(f"model variant {variant_id} not found")
        self.downloading = True
        self.runtime = ModelDownloadRuntime(variant_id, None, "Downloading", 0.0, None)
        return self.variant

    def load(self, variant_id: str, device: object) -> None:
        del device
        if variant_id != self.variant.id:
            raise NotFoundError(f"model variant {variant_id} not found")
        self.status = ModelStatus(variant_id, self.variant.name, "cpu", 0, True)

    def unload(self) -> None:
        self.status = ModelStatus(None, "unloaded", "cpu", 0, False)

    def get_status(self) -> ModelStatus:
        return self.status

    def get_download_runtime(self) -> ModelDownloadRuntime:
        return self.runtime


class FakeSettings(_Lifecycle):
    def get(self, namespace: str, key: str) -> object:
        del namespace, key
        return None

    def get_namespace(self, namespace: str) -> dict[str, object]:
        if namespace not in SETTING_NAMESPACES:
            raise ValidationError("unknown settings namespace")
        return {"theme": "dark"} if namespace == "ui" else {}

    def set_namespace(self, namespace: str, mapping: dict[str, object]) -> None:
        del mapping
        if namespace not in SETTING_NAMESPACES:
            raise ValidationError("unknown settings namespace")


class FakeDownload(_Lifecycle):
    def __init__(self) -> None:
        self.jobs: list[object] = []
        self.last_reorder: list[str] = []

    def get_queue(self) -> list[object]:
        return list(self.jobs)

    def get_processor_state(self) -> QueueRuntime:
        return QueueRuntime("downloads", QueueProcessorState.Idle, None)

    def add_to_queue(self, *args: object, **kwargs: object) -> list[object]:
        del args, kwargs
        return []

    def start_processing(self) -> None:
        return None

    def pause_processing(self) -> None:
        return None

    def resume_processing(self) -> None:
        return None

    def cancel_processing(self) -> None:
        return None

    def remove_from_queue(self, job_id: str) -> None:
        del job_id

    def clear_queue(self) -> None:
        return None

    def reorder_queue(self, job_ids: list[str]) -> None:
        by_id = {getattr(job, "id", None): job for job in self.jobs}
        self.jobs = [by_id[job_id] for job_id in job_ids if job_id in by_id]
        self.last_reorder = list(job_ids)

    def reset_failed(self, job_id: str) -> object:
        raise NotFoundError(f"download job {job_id} not found")

    def get_job(self, job_id: str) -> object:
        raise NotFoundError(f"download job {job_id} not found")

    def get_sabr_status(self) -> SimpleNamespace:
        return SimpleNamespace(mode=SimpleNamespace(value="Inactive"), source=None, checked_at=None)

    def check_sabr(self) -> SimpleNamespace:
        return self.get_sabr_status()

    def force_sabr(self) -> SimpleNamespace:
        return self.get_sabr_status()

    def clear_sabr(self) -> SimpleNamespace:
        return self.get_sabr_status()

    def apply_defaults_to_pending(self) -> int:
        return 0

    def test_cookies(self, *args: object, **kwargs: object) -> SimpleNamespace:
        del args, kwargs
        return SimpleNamespace(ok=True)


class FakeConversion(_Lifecycle):
    def get_queue(self) -> list[object]:
        return []

    def get_processor_state(self) -> QueueRuntime:
        return QueueRuntime("conversions", QueueProcessorState.Idle, None)

    def get_job(self, job_id: str) -> object:
        raise NotFoundError(f"conversion job {job_id} not found")

    def get_gpu(self) -> object | None:
        return None

    def detect_gpu(self) -> object:
        raise NotFoundError("gpu probe is not available on the shared fake")

    def add_to_queue(self, *args: object, **kwargs: object) -> list[object]:
        del args, kwargs
        return []

    def start_processing(self) -> None:
        return None

    def pause_processing(self) -> None:
        return None

    def resume_processing(self) -> None:
        return None

    def reorder_queue(self, job_ids: list[str]) -> None:
        del job_ids

    def remove(self, job_id: str) -> None:
        del job_id

    def clear_queue(self) -> None:
        return None

    def reset_failed(self, job_id: str) -> object:
        raise NotFoundError(f"conversion job {job_id} not found")


class FakeHealth(_Lifecycle):
    def console_snapshot(self, after_seq: object) -> list[object]:
        del after_seq
        return []

    def record_startup_metric(self, name: str, value: object) -> None:
        del name, value


def make_bundle(
    *,
    transcript: FakeTranscript | None = None,
    tts: FakeTTS | None = None,
    models: FakeModels | None = None,
) -> tuple[AppServices, FakeTranscript, FakeTTS, FakeModels]:
    trx = transcript or FakeTranscript()
    speech = tts or FakeTTS()
    catalog = models or FakeModels()
    services = AppServices(
        download=FakeDownload(),
        transcript=trx,
        tts=speech,
        models=catalog,
        settings=FakeSettings(),
        health=FakeHealth(),
        conversion=FakeConversion(),
        capture=_Lifecycle(),
    )
    return services, trx, speech, catalog


def make_client(
    *,
    transcript: FakeTranscript | None = None,
    tts: FakeTTS | None = None,
    models: FakeModels | None = None,
) -> tuple[TestClient, FakeTranscript, FakeTTS, FakeModels]:
    services, trx, speech, catalog = make_bundle(
        transcript=transcript,
        tts=tts,
        models=models,
    )
    app = create_app(tokens=TOKENS, services=services, engine_dispose=None)
    return TestClient(app), trx, speech, catalog
