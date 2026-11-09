"""Phase 1 domain foundation tests — single registered gate file."""

from __future__ import annotations

import ast
import importlib
import inspect
import math
from dataclasses import fields
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CORE_SRC = REPO_ROOT / "packages" / "core" / "src"
AVKIT_CORE = CORE_SRC / "avkit_core"
DOMAIN_DIR = AVKIT_CORE / "domain"
PORTS_DIR = AVKIT_CORE / "ports"

INFRA_NAMES = frozenset(
    {
        "sqlalchemy",
        "yt_dlp",
        "fastapi",
        "youtube_transcript_api",
        "huggingface_hub",
        "soundfile",
        "PIL",
        "mss",
    }
)

LAYOUT_RELATIVE_PATHS = (
    "avkit_core/__init__.py",
    "avkit_core/domain/__init__.py",
    "avkit_core/domain/download.py",
    "avkit_core/domain/transcript.py",
    "avkit_core/domain/tts.py",
    "avkit_core/domain/settings.py",
    "avkit_core/domain/progress.py",
    "avkit_core/domain/queue.py",
    "avkit_core/domain/enums.py",
    "avkit_core/domain/errors.py",
    "avkit_core/domain/capture.py",
    "avkit_core/ports/capture.py",
    "avkit_core/ports/__init__.py",
    "avkit_core/ports/youtube.py",
    "avkit_core/ports/transcript.py",
    "avkit_core/ports/tts.py",
    "avkit_core/ports/media.py",
    "avkit_core/ports/filesystem.py",
    "avkit_core/ports/models.py",
    "avkit_core/ports/storage.py",
)

DEV_GROUP_PACKAGES = ("pytest", "pyright", "ruff", "pyyaml", "jsonschema")


def _read_toml(path: Path) -> dict[str, object]:
    import tomllib

    with path.open("rb") as handle:
        return tomllib.load(handle)


def _normalize_requires_python(value: str) -> str:
    return value.replace(" ", "")


def _dependency_name(spec: str) -> str:
    token = spec.strip()
    for separator in ("[", " ", "<", ">", "=", "!"):
        index = token.find(separator)
        if index != -1:
            token = token[:index]
    return token.lower()


def _imported_module_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


@pytest.mark.unit
def test_ac_1_1_root_uv_workspace() -> None:
    root_pyproject = REPO_ROOT / "pyproject.toml"
    assert root_pyproject.is_file(), "root pyproject.toml must exist"
    data = _read_toml(root_pyproject)
    project = data.get("project")
    assert isinstance(project, dict)
    requires_python = project.get("requires-python")
    assert isinstance(requires_python, str)
    assert _normalize_requires_python(requires_python) == ">=3.11"

    uv_table = data.get("tool")
    assert isinstance(uv_table, dict)
    uv = uv_table.get("uv")
    assert isinstance(uv, dict)
    workspace = uv.get("workspace")
    assert isinstance(workspace, dict)
    members = workspace.get("members")
    assert members == ["packages/core", "packages/infrastructure", "packages/api"]

    dependency_groups = data.get("dependency-groups")
    assert isinstance(dependency_groups, dict)
    dev = dependency_groups.get("dev")
    assert isinstance(dev, list)
    declared = {_dependency_name(str(item)) for item in dev}
    missing = [name for name in DEV_GROUP_PACKAGES if name not in declared]
    assert missing == [], f"dev group missing {missing}"


@pytest.mark.unit
def test_ac_1_2_package_layout_and_no_application() -> None:
    missing = [rel for rel in LAYOUT_RELATIVE_PATHS if not (CORE_SRC / rel).is_file()]
    assert missing == [], f"missing layout modules: {missing}"
    application = REPO_ROOT / "packages" / "application"
    assert not application.exists(), "packages/application must not exist"


@pytest.mark.unit
def test_ac_1_3_importable_core_has_zero_infra_imports() -> None:
    import avkit_core

    assert avkit_core is not None
    hits: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        imported = _imported_module_names(path)
        forbidden = sorted(imported & INFRA_NAMES)
        if forbidden:
            hits.append(f"{path.relative_to(REPO_ROOT)}:{forbidden}")
    assert hits == [], f"infrastructure imports in core: {hits}"


@pytest.mark.unit
def test_ac_1_4_domain_tests_are_unit_marked() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    assert "@pytest.mark.unit" in source
    assert (REPO_ROOT / "tests" / "unit" / "test_domain.py").is_file()


@pytest.mark.unit
def test_ac_1_5_numpy_is_a_core_dependency() -> None:
    core_pyproject = REPO_ROOT / "packages" / "core" / "pyproject.toml"
    assert core_pyproject.is_file()
    data = _read_toml(core_pyproject)
    project = data.get("project")
    assert isinstance(project, dict)
    dependencies = project.get("dependencies")
    assert isinstance(dependencies, list)
    declared = {_dependency_name(str(item)) for item in dependencies}
    assert "numpy" in declared
    import numpy as np

    assert np.__version__


@pytest.mark.unit
def test_ac_1_6_registered_gate_tools_are_declared() -> None:
    """AC-1.6 receipts are run by the MEU gate; this asserts the toolchain is declared."""
    root_pyproject = REPO_ROOT / "pyproject.toml"
    data = _read_toml(root_pyproject)
    dependency_groups = data.get("dependency-groups")
    assert isinstance(dependency_groups, dict)
    dev = dependency_groups.get("dev")
    assert isinstance(dev, list)
    declared = {_dependency_name(str(item)) for item in dev}
    for tool in ("pytest", "pyright", "ruff"):
        assert tool in declared


DOMAIN_ERROR_TYPE_NAMES = (
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "AgeRestrictedError",
    "DownloadCancelledError",
    "SABRDetectedError",
    "CookieTestError",
    "TranscriptsDisabledError",
    "NoTranscriptFoundError",
    "TranscriptRetryableError",
    "FFmpegNotFoundError",
    "FFmpegEncodeError",
    "MediaProbeError",
    "InvalidTimeRangeError",
    "GpuUnavailableError",
    "ModelDownloadError",
    "ModelLoadError",
    "FilesystemError",
    "SpacyModelNotFoundError",
    "CaptureNotSupportedError",
    "CaptureFailedError",
    "InboxPathError",
    "AnnotationValidationError",
    "CaptureRequestConflictError",
    "CaptureFlattenConflictError",  # TA-7 (Session 30, MEU-67)
    "ExtractError",  # TA-1 (Session 33, MEU-76)
)


@pytest.mark.unit
def test_ac_4_10_domain_error_types_are_distinct() -> None:
    from avkit_core.domain import errors as errors_mod

    assert not hasattr(errors_mod, "SabrDetectedError")
    table = errors_mod.DOMAIN_ERROR_TYPES
    names = [cls.__name__ for cls in table]
    assert names == list(DOMAIN_ERROR_TYPE_NAMES)
    assert len(table) == len(set(table))
    for cls in table:
        err = cls("domain failure")
        assert isinstance(err, Exception)
        assert type(err) is cls


@pytest.mark.unit
def test_ac_4_11_cookie_access_error_is_alias() -> None:
    from avkit_core.domain.errors import CookieAccessError, CookieTestError

    assert CookieAccessError is CookieTestError
    assert CookieAccessError.__name__ == "CookieTestError"
    source = (DOMAIN_DIR / "errors.py").read_text(encoding="utf-8")
    assert "class CookieAccessError" not in source


@pytest.mark.unit
def test_ac_4_12_validation_error_is_domain_constructor_error() -> None:
    from avkit_core.domain.errors import ValidationError

    err = ValidationError("invalid input")
    assert type(err) is ValidationError
    assert not isinstance(err, AssertionError)
    hits: list[str] = []
    for path in CORE_SRC.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                hits.append(f"{path.relative_to(REPO_ROOT)}:{node.lineno}")
    assert hits == [], f"assert remains in core source: {hits}"


ENUM_MEMBERS: dict[str, tuple[str, ...]] = {
    "DownloadStatus": (
        "Pending",
        "Downloading",
        "Done",
        "Failed",
        "Skipped",
        "QualityBlocked",
        "AgeRestricted",
        "Cancelled",
    ),
    "TranscriptStatus": ("Pending", "Processing", "Done", "Failed", "Paused", "Cancelled"),
    "TranscriptItemStatus": ("Pending", "Done", "Skipped", "Failed"),
    "TTSStatus": ("Pending", "Generating", "Done", "Failed", "Cancelled"),
    "TTSSourceKind": ("Inline", "File"),
    "QueueProcessorState": ("Idle", "Processing", "Paused"),
    "MediaFormat": ("MP4", "WEBM", "MP3", "M4A", "WAV", "OPUS"),
    "QualityPreset": (
        "Best",
        "P2160",
        "P1440",
        "P1080",
        "P720",
        "P480",
        "P360",
        "P240",
        "P144",
        "Lowest",
    ),
    "AudioFormat": (
        "Default",
        "Best",
        "Lowest",
        "LowWebm",
        "MediumWebm",
        "StandardWebm",
        "StandardM4a",
        "StandardMp3",
        "HighM4a",
    ),
    "DeviceType": ("Auto", "CUDA", "MPS", "CPU"),
    "ModelFormat": ("PyTorch", "ONNX"),
    "ModelPrecision": ("FP32", "FP16", "INT8"),
    "SABRMode": ("Inactive", "Active", "Checking"),
    "SABRSource": ("Detected", "Forced"),
    "SettingValueType": ("String", "Number", "Boolean", "Json"),
    "CaptureSource": (
        "Hotkey",
        "Gui",
        "McpFullscreen",
        "McpRegion",
        "McpInteractive",
        "Scan",
        "Import",
    ),
    "CaptureRequestStatus": ("Pending", "Completed", "Cancelled", "Expired"),
    # TA-6 (Session 39, D-24): + Pixelate, Eraser.
    "AnnotationType": ("Arrow", "Rect", "Highlight", "Text", "Pixelate", "Eraser"),
}

SPEC_PROGRESS_SNAPSHOT_FIELDS = (
    "fraction",
    "units_done",
    "units_total",
    "unit_label",
    "rate",
    "eta_seconds",
    "error",
)
SPEC_ERROR_INFO_FIELDS = ("message", "code")
SPEC_SABR_STATUS_FIELDS = ("mode", "source", "checked_at")
SPEC_QUEUE_RUNTIME_FIELDS = ("queue_name", "state", "current_job_id")
SPEC_MODEL_STATUS_FIELDS = ("variant_id", "name", "device", "memory_bytes", "is_loaded")
# TA-9 (Session 27, MEU-62): + `asset`, the in-flight TTS runtime asset (AC-62.6/62.8).
SPEC_MODEL_DOWNLOAD_RUNTIME_FIELDS = ("variant_id", "asset", "state", "fraction", "error_message")
SPEC_VOICE_CONFIG_FIELDS = ("voice_id", "lang_code", "language", "gender", "style_description")


def _field_names(cls: type[object]) -> tuple[str, ...]:
    return tuple(item.name for item in fields(cls))


@pytest.mark.unit
def test_ac_2_1_strenum_members_and_values() -> None:
    from avkit_core.domain import enums as enums_mod

    for name, expected in ENUM_MEMBERS.items():
        enum_cls = getattr(enums_mod, name)
        values = tuple(member.value for member in enum_cls)
        names = tuple(member.name for member in enum_cls)
        assert names == expected
        assert values == expected
        for member in enum_cls:
            assert member.value == member.name


@pytest.mark.unit
def test_ac_2_2_download_status_has_no_paused() -> None:
    from avkit_core.domain.enums import DownloadStatus

    assert "Paused" not in DownloadStatus
    with pytest.raises(ValueError):
        DownloadStatus("Paused")


@pytest.mark.unit
def test_ac_2_3_no_operation_symbol() -> None:
    import avkit_core
    from avkit_core.domain import enums as enums_mod

    assert not hasattr(avkit_core, "Operation")
    assert not hasattr(enums_mod, "Operation")
    with pytest.raises(ImportError):
        importlib.import_module("avkit_core.domain.operation")


@pytest.mark.unit
def test_ac_2_4_progress_snapshot_fields_and_ranges() -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.progress import (
        FRACTION_MAX,
        FRACTION_MIN,
        PROGRESS_SNAPSHOT_FIELDS,
        UNIT_LABELS,
        ProgressSnapshot,
    )

    assert PROGRESS_SNAPSHOT_FIELDS == SPEC_PROGRESS_SNAPSHOT_FIELDS
    assert _field_names(ProgressSnapshot) == PROGRESS_SNAPSHOT_FIELDS
    snapshot = ProgressSnapshot(
        fraction=0.25,
        units_done=1,
        units_total=4,
        unit_label="bytes",
        rate=1.5,
        eta_seconds=10,
        error=None,
    )
    assert snapshot.fraction == 0.25
    assert UNIT_LABELS == frozenset({"bytes", "videos", "segments", "frames"})
    assert FRACTION_MIN == 0.0
    assert FRACTION_MAX == 1.0
    with pytest.raises(ValidationError):
        ProgressSnapshot(
            fraction=1.1,
            units_done=1,
            units_total=4,
            unit_label="bytes",
            rate=1.5,
            eta_seconds=10,
            error=None,
        )
    with pytest.raises(ValidationError):
        ProgressSnapshot(
            fraction=0.25,
            units_done=1,
            units_total=4,
            unit_label="percent",
            rate=1.5,
            eta_seconds=10,
            error=None,
        )
    with pytest.raises(ValidationError):
        ProgressSnapshot(
            fraction=0.25,
            units_done=1,
            units_total=-1,
            unit_label="bytes",
            rate=1.5,
            eta_seconds=10,
            error=None,
        )
    with pytest.raises(TypeError):
        ProgressSnapshot(
            fraction=0.25,
            units_done=1,
            units_total=4,
            unit_label="bytes",
            rate=1.5,
            eta_seconds=10,
            error=None,
            extra_field=True,
        )


@pytest.mark.unit
def test_ac_2_5_error_info_fields() -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.progress import ERROR_INFO_FIELDS, ErrorInfo

    assert ERROR_INFO_FIELDS == SPEC_ERROR_INFO_FIELDS
    assert _field_names(ErrorInfo) == ERROR_INFO_FIELDS
    info = ErrorInfo(message="failed", code="E1")
    assert info.code == "E1"
    with pytest.raises(ValidationError):
        ErrorInfo(message="", code=None)
    with pytest.raises(TypeError):
        ErrorInfo(message="failed")


@pytest.mark.unit
def test_ac_2_6_sabr_status_fields() -> None:
    from avkit_core.domain.download import SABR_STATUS_FIELDS, SABRStatus
    from avkit_core.domain.enums import SABRMode, SABRSource
    from avkit_core.domain.errors import ValidationError

    assert SABR_STATUS_FIELDS == SPEC_SABR_STATUS_FIELDS
    assert _field_names(SABRStatus) == SABR_STATUS_FIELDS
    checked = datetime(2026, 8, 19, tzinfo=UTC)
    status = SABRStatus(mode=SABRMode.Active, source=SABRSource.Detected, checked_at=checked)
    assert status.checked_at == checked
    with pytest.raises(ValidationError):
        SABRStatus(mode=SABRMode.Active, source=None, checked_at=checked)
    with pytest.raises(TypeError):
        SABRStatus(mode=SABRMode.Inactive, source=None)


@pytest.mark.unit
def test_ac_2_7_queue_runtime_fields() -> None:
    from avkit_core.domain.enums import QueueProcessorState
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.queue import QUEUE_NAMES, QUEUE_RUNTIME_FIELDS, QueueRuntime

    assert QUEUE_RUNTIME_FIELDS == SPEC_QUEUE_RUNTIME_FIELDS
    assert _field_names(QueueRuntime) == QUEUE_RUNTIME_FIELDS
    assert QUEUE_NAMES == frozenset({"downloads", "transcripts", "conversions"})
    runtime = QueueRuntime(
        queue_name="downloads",
        state=QueueProcessorState.Idle,
        current_job_id=None,
    )
    assert runtime.current_job_id is None
    with pytest.raises(ValidationError):
        QueueRuntime(queue_name="tts", state=QueueProcessorState.Idle, current_job_id=None)
    with pytest.raises(TypeError):
        QueueRuntime(queue_name="downloads", state=QueueProcessorState.Idle)


@pytest.mark.unit
def test_ac_2_8_model_status_fields() -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.tts import MODEL_STATUS_FIELDS, ModelStatus

    assert MODEL_STATUS_FIELDS == SPEC_MODEL_STATUS_FIELDS
    assert _field_names(ModelStatus) == MODEL_STATUS_FIELDS
    status = ModelStatus(
        variant_id="onnx-fp32",
        name="ONNX FP32",
        device="cpu",
        memory_bytes=0,
        is_loaded=False,
    )
    assert status.is_loaded is False
    with pytest.raises(ValidationError):
        ModelStatus(
            variant_id=None,
            name="ONNX FP32",
            device="cpu",
            memory_bytes=-1,
            is_loaded=False,
        )
    with pytest.raises(TypeError):
        ModelStatus(variant_id=None, name="ONNX FP32", device="cpu", memory_bytes=0)


@pytest.mark.unit
def test_ac_2_9_model_download_runtime_and_no_fetch_job() -> None:
    from avkit_core.domain import tts as tts_mod
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.tts import (
        MODEL_DOWNLOAD_RUNTIME_FIELDS,
        MODEL_DOWNLOAD_STATES,
        ModelDownloadRuntime,
    )

    assert MODEL_DOWNLOAD_RUNTIME_FIELDS == SPEC_MODEL_DOWNLOAD_RUNTIME_FIELDS
    assert _field_names(ModelDownloadRuntime) == MODEL_DOWNLOAD_RUNTIME_FIELDS
    assert MODEL_DOWNLOAD_STATES == frozenset({"Idle", "Downloading", "Failed"})
    runtime = ModelDownloadRuntime(
        variant_id=None,
        asset=None,
        state="Idle",
        fraction=0.0,
        error_message=None,
    )
    assert runtime.variant_id is None
    with pytest.raises(ValidationError):
        ModelDownloadRuntime(
            variant_id=None,
            asset=None,
            state="Queued",
            fraction=0.0,
            error_message=None,
        )
    with pytest.raises(TypeError):
        ModelDownloadRuntime(state="Idle", fraction=0.0, error_message=None)
    assert not hasattr(tts_mod, "ModelFetchJob")


@pytest.mark.unit
def test_ac_2_10_voice_config_prefix_rule() -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.tts import VOICE_CONFIG_FIELDS, VoiceConfig

    assert VOICE_CONFIG_FIELDS == SPEC_VOICE_CONFIG_FIELDS
    assert _field_names(VoiceConfig) == VOICE_CONFIG_FIELDS
    voice = VoiceConfig(
        voice_id="af_bella",
        lang_code="a",
        language="en-us",
        gender="female",
        style_description="American",
    )
    assert voice.lang_code == "a"
    with pytest.raises(ValidationError):
        VoiceConfig(
            voice_id="af_bella",
            lang_code="j",
            language="en-us",
            gender="female",
            style_description="American",
        )
    with pytest.raises(TypeError):
        VoiceConfig(
            voice_id="af_bella",
            lang_code="a",
            language="en-us",
            gender="female",
            style_description="American",
            extra="nope",
        )


@pytest.mark.unit
def test_ac_2_11_enum_closed_set_exhaustiveness() -> None:
    from avkit_core.domain import enums as enums_mod

    for name, expected in ENUM_MEMBERS.items():
        enum_cls = getattr(enums_mod, name)
        assert {member.value for member in enum_cls} == set(expected)
        with pytest.raises(ValueError):
            enum_cls("not-a-member")


@pytest.mark.unit
def test_ac_2_12_vo_field_inventory() -> None:
    from avkit_core.domain.download import SABRStatus
    from avkit_core.domain.progress import ErrorInfo, ProgressSnapshot
    from avkit_core.domain.queue import QueueRuntime
    from avkit_core.domain.tts import ModelDownloadRuntime, ModelStatus, VoiceConfig

    inventory = {
        ProgressSnapshot: SPEC_PROGRESS_SNAPSHOT_FIELDS,
        ErrorInfo: SPEC_ERROR_INFO_FIELDS,
        SABRStatus: SPEC_SABR_STATUS_FIELDS,
        QueueRuntime: SPEC_QUEUE_RUNTIME_FIELDS,
        ModelStatus: SPEC_MODEL_STATUS_FIELDS,
        ModelDownloadRuntime: SPEC_MODEL_DOWNLOAD_RUNTIME_FIELDS,
        VoiceConfig: SPEC_VOICE_CONFIG_FIELDS,
    }
    for cls, expected in inventory.items():
        assert _field_names(cls) == expected
    with pytest.raises(TypeError):
        ProgressSnapshot(
            fraction=0.0,
            units_done=0,
            units_total=None,
            unit_label="bytes",
            rate=None,
            eta_seconds=None,
        )


SPEC_DOWNLOAD_JOB_FIELDS = (
    "id",
    "url",
    "video_id",
    "title",
    "quality",
    "audio_only",
    "audio_format",
    "status",
    "progress",
    "speed_bps",
    "eta_seconds",
    "file_size",
    "file_path",
    "error_message",
    "queue_position",
    "created_at",
    "updated_at",
    "received_height",
)
SPEC_ARCHIVE_FIELDS = ("extractor", "video_id", "title", "recorded_at")
SPEC_TRANSCRIPT_JOB_FIELDS = (
    "id",
    "channel_url",
    "channel_name",
    "status",
    "output_dir",
    "video_count",
    "word_count",
    "zip_path",
    "queue_position",
    "error_message",
    "created_at",
    "updated_at",
)
SPEC_TRANSCRIPT_ITEM_FIELDS = (
    "id",
    "job_id",
    "video_id",
    "title",
    "language",
    "word_count",
    "path",
    "status",
    "error_message",
    "retry_count",
    "processed_at",
)
SPEC_TTS_JOB_FIELDS = (
    "id",
    "source_kind",
    "source_path",
    "text_hash",
    "text_preview",
    "voice",
    "speed",
    "format",
    "status",
    "output_path",
    "segments_total",
    "segments_done",
    "error_message",
    "created_at",
    "updated_at",
)
SPEC_MODEL_VARIANT_FIELDS = (
    "id",
    "name",
    "format",
    "precision",
    "size_bytes",
    "path",
    "is_downloaded",
)
SPEC_SETTING_FIELDS = ("namespace", "key", "value", "value_type", "updated_at")


def _now() -> datetime:
    return datetime(2026, 8, 19, 12, 0, tzinfo=UTC)


def _download_job(**overrides: object) -> object:
    from avkit_core.domain.download import DownloadJob
    from avkit_core.domain.enums import AudioFormat, DownloadStatus, QualityPreset

    payload: dict[str, object] = {
        "id": str(uuid4()),
        "url": "https://youtu.be/dQw4w9wgGc",
        "video_id": "dQw4w9wgGc",
        "title": "Example",
        "quality": QualityPreset.P1080,
        "audio_only": False,
        "audio_format": AudioFormat.Default,
        "status": DownloadStatus.Pending,
        "progress": 0.0,
        "speed_bps": None,
        "eta_seconds": None,
        "file_size": None,
        "file_path": None,
        "error_message": None,
        "queue_position": 0,
        "created_at": _now(),
        "updated_at": _now(),
    }
    payload.update(overrides)
    return DownloadJob(**payload)


@pytest.mark.unit
def test_ac_3_1_download_job_persistable_fields() -> None:
    from avkit_core.domain.download import DownloadJob
    from avkit_core.domain.errors import ValidationError

    job = _download_job()
    assert _field_names(DownloadJob) == SPEC_DOWNLOAD_JOB_FIELDS
    assert "parent_id" not in _field_names(DownloadJob)
    with pytest.raises(TypeError):
        _download_job(parent_id="nope")
    with pytest.raises(ValidationError):
        _download_job(id="not-a-uuid")
    with pytest.raises(ValidationError):
        _download_job(title="")
    assert job.status.value == "Pending"


@pytest.mark.unit
def test_ac_3_2_download_job_status_cannot_be_paused() -> None:
    from avkit_core.domain.errors import ValidationError

    with pytest.raises(ValidationError):
        _download_job(status="Paused")


@pytest.mark.unit
def test_ac_3_3_download_transitions() -> None:
    from avkit_core.domain.enums import DownloadStatus
    from avkit_core.domain.errors import ConflictError

    pending = _download_job(status=DownloadStatus.Pending)
    downloading = pending.transition(DownloadStatus.Downloading)
    assert downloading.status is DownloadStatus.Downloading
    done = downloading.transition(DownloadStatus.Done)
    assert done.status is DownloadStatus.Done
    with pytest.raises(ConflictError):
        done.transition(DownloadStatus.Failed)


@pytest.mark.unit
def test_ac_10_13_pending_quality_blocked_and_skipped_edges() -> None:
    from avkit_core.domain.enums import DownloadStatus
    from avkit_core.domain.errors import ConflictError

    pending = _download_job(status=DownloadStatus.Pending)
    assert pending.transition(DownloadStatus.QualityBlocked).status is DownloadStatus.QualityBlocked
    assert pending.transition(DownloadStatus.Skipped).status is DownloadStatus.Skipped
    done = pending.transition(DownloadStatus.Downloading).transition(DownloadStatus.Done)
    with pytest.raises(ConflictError):
        done.transition(DownloadStatus.QualityBlocked)


@pytest.mark.unit
def test_ac_11_parent_and_item_transition_graphs() -> None:
    from avkit_core.domain.enums import TranscriptItemStatus, TranscriptStatus
    from avkit_core.domain.errors import ConflictError
    from avkit_core.domain.transcript import TranscriptItem, TranscriptJob

    job = TranscriptJob(
        id=str(uuid4()),
        channel_url="https://youtube.com/@example",
        channel_name="Example",
        status=TranscriptStatus.Pending,
        output_dir=Path("channels/example"),
        video_count=1,
        word_count=0,
        zip_path=None,
        queue_position=0,
        error_message=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    processing = job.transition(TranscriptStatus.Processing)
    assert processing.transition(TranscriptStatus.Pending).status is TranscriptStatus.Pending
    assert processing.transition(TranscriptStatus.Paused).status is TranscriptStatus.Paused
    with pytest.raises(ConflictError):
        job.transition(TranscriptStatus.Done)
    item = TranscriptItem(
        id=str(uuid4()),
        job_id=job.id,
        video_id="vid001",
        title="Item",
        language="en",
        word_count=0,
        path=None,
        status=TranscriptItemStatus.Pending,
        error_message=None,
        retry_count=0,
        processed_at=None,
    )
    failed = item.transition(TranscriptItemStatus.Failed)
    assert failed.transition(TranscriptItemStatus.Pending).status is TranscriptItemStatus.Pending
    with pytest.raises(ConflictError):
        item.transition(TranscriptItemStatus.Pending)


@pytest.mark.unit
def test_ac_12_tts_transition_graph() -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
    from avkit_core.domain.errors import ConflictError
    from avkit_core.domain.tts import TTSJob

    job = TTSJob(
        id=str(uuid4()),
        source_kind=TTSSourceKind.Inline,
        source_path=None,
        text_hash="abc123",
        text_preview="hello",
        voice="am_eric",
        speed=1.0,
        format=MediaFormat.MP3,
        status=TTSStatus.Pending,
        output_path=None,
        segments_total=0,
        segments_done=0,
        error_message=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    generating = job.transition(TTSStatus.Generating)
    assert generating.transition(TTSStatus.Cancelled).status is TTSStatus.Cancelled
    with pytest.raises(ConflictError):
        job.transition(TTSStatus.Done)


@pytest.mark.unit
def test_ac_3_4_reset_failed_clears_error_and_progress() -> None:
    from avkit_core.domain.enums import DownloadStatus
    from avkit_core.domain.errors import ConflictError

    failed = _download_job(
        status=DownloadStatus.Failed,
        error_message="boom",
        progress=0.4,
    )
    reset = failed.reset_failed()
    assert reset.status is DownloadStatus.Pending
    assert reset.error_message is None
    assert reset.progress == 0.0
    with pytest.raises(ConflictError):
        _download_job(status=DownloadStatus.Done).reset_failed()


@pytest.mark.unit
def test_ac_3_5_download_archive_entry_keys() -> None:
    from avkit_core.domain.download import DownloadArchiveEntry
    from avkit_core.domain.errors import ValidationError

    entry = DownloadArchiveEntry(
        extractor="youtube",
        video_id="abc123",
        title="Example",
        recorded_at=_now(),
    )
    assert _field_names(DownloadArchiveEntry) == SPEC_ARCHIVE_FIELDS
    assert entry.extractor == "youtube"
    with pytest.raises(ValidationError):
        DownloadArchiveEntry(extractor="youtube", video_id="", title=None, recorded_at=_now())


@pytest.mark.unit
def test_ac_3_6_transcript_job_has_no_dropped_fields() -> None:
    from avkit_core.domain.enums import TranscriptStatus
    from avkit_core.domain.transcript import TranscriptJob

    job = TranscriptJob(
        id=str(uuid4()),
        channel_url="https://youtube.com/@example",
        channel_name="Example",
        status=TranscriptStatus.Pending,
        output_dir=Path("out"),
        video_count=0,
        word_count=0,
        zip_path=None,
        queue_position=0,
        error_message=None,
        created_at=_now(),
        updated_at=_now(),
    )
    names = _field_names(TranscriptJob)
    assert names == SPEC_TRANSCRIPT_JOB_FIELDS
    assert "video_ids" not in names
    assert "processed_ids" not in names
    assert "progress" not in names
    assert job.video_count == 0


@pytest.mark.unit
def test_ac_3_7_transcript_job_may_be_paused() -> None:
    from avkit_core.domain.enums import TranscriptStatus
    from avkit_core.domain.transcript import TranscriptJob

    job = TranscriptJob(
        id=str(uuid4()),
        channel_url="https://youtube.com/@example",
        channel_name="Example",
        status=TranscriptStatus.Paused,
        output_dir=Path("out"),
        video_count=1,
        word_count=0,
        zip_path=None,
        queue_position=0,
        error_message=None,
        created_at=_now(),
        updated_at=_now(),
    )
    assert job.status is TranscriptStatus.Paused


@pytest.mark.unit
def test_ac_3_8_transcript_item_done_requires_path() -> None:
    from avkit_core.domain.enums import TranscriptItemStatus
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.transcript import TranscriptItem

    item = TranscriptItem(
        id=str(uuid4()),
        job_id=str(uuid4()),
        video_id="abc123",
        title="Example",
        language="en",
        word_count=0,
        path=None,
        status=TranscriptItemStatus.Pending,
        error_message=None,
        retry_count=0,
        processed_at=None,
    )
    assert _field_names(TranscriptItem) == SPEC_TRANSCRIPT_ITEM_FIELDS
    assert item.path is None
    with pytest.raises(ValidationError):
        TranscriptItem(
            id=str(uuid4()),
            job_id=str(uuid4()),
            video_id="abc123",
            title="Example",
            language="en",
            word_count=0,
            path=None,
            status=TranscriptItemStatus.Done,
            error_message=None,
            retry_count=0,
            processed_at=_now(),
        )


@pytest.mark.unit
def test_ac_3_9_tts_job_invariants() -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.tts import TTSJob

    job = TTSJob(
        id=str(uuid4()),
        source_kind=TTSSourceKind.Inline,
        source_path=None,
        text_hash="abc",
        text_preview="hello",
        voice="af_bella",
        speed=1.0,
        format=MediaFormat.MP3,
        status=TTSStatus.Pending,
        output_path=None,
        segments_total=1,
        segments_done=0,
        error_message=None,
        created_at=_now(),
        updated_at=_now(),
    )
    assert _field_names(TTSJob) == SPEC_TTS_JOB_FIELDS
    assert "text" not in _field_names(TTSJob)
    assert job.speed == 1.0
    with pytest.raises(ValidationError):
        TTSJob(
            id=str(uuid4()),
            source_kind=TTSSourceKind.Inline,
            source_path=None,
            text_hash="abc",
            text_preview="hello",
            voice="af_bella",
            speed=2.1,
            format=MediaFormat.MP3,
            status=TTSStatus.Pending,
            output_path=None,
            segments_total=1,
            segments_done=0,
            error_message=None,
            created_at=_now(),
            updated_at=_now(),
        )
    with pytest.raises(ValidationError):
        TTSJob(
            id=str(uuid4()),
            source_kind=TTSSourceKind.File,
            source_path=None,
            text_hash="abc",
            text_preview="hello",
            voice="af_bella",
            speed=1.0,
            format=MediaFormat.MP3,
            status=TTSStatus.Pending,
            output_path=None,
            segments_total=1,
            segments_done=0,
            error_message=None,
            created_at=_now(),
            updated_at=_now(),
        )
    with pytest.raises(ValidationError):
        TTSJob(
            id=str(uuid4()),
            source_kind=TTSSourceKind.Inline,
            source_path=None,
            text_hash="abc",
            text_preview="x" * 201,
            voice="af_bella",
            speed=1.0,
            format=MediaFormat.MP3,
            status=TTSStatus.Pending,
            output_path=None,
            segments_total=1,
            segments_done=0,
            error_message=None,
            created_at=_now(),
            updated_at=_now(),
        )


@pytest.mark.unit
def test_ac_3_10_model_variant_has_no_runtime_columns() -> None:
    from avkit_core.domain.enums import ModelFormat, ModelPrecision
    from avkit_core.domain.tts import ModelVariant

    variant = ModelVariant(
        id="kokoro-onnx-fp32",
        name="ONNX FP32",
        format=ModelFormat.ONNX,
        precision=ModelPrecision.FP32,
        size_bytes=1,
        path=None,
        is_downloaded=False,
    )
    names = _field_names(ModelVariant)
    assert names == SPEC_MODEL_VARIANT_FIELDS
    assert "is_loaded" not in names
    assert "device" not in names
    assert variant.is_downloaded is False


@pytest.mark.unit
def test_ac_3_11_setting_namespace_and_leaf_key() -> None:
    from avkit_core.domain.enums import SettingValueType
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.settings import SETTING_NAMESPACES, Setting

    setting = Setting(
        namespace="downloader",
        key="quality",
        value="P1080",
        value_type=SettingValueType.String,
        updated_at=_now(),
    )
    assert _field_names(Setting) == SPEC_SETTING_FIELDS
    assert SETTING_NAMESPACES == frozenset(
        {"downloader", "transcript", "tts", "app", "ui", "converter", "capture"}
    )
    assert setting.namespace in SETTING_NAMESPACES
    with pytest.raises(ValidationError):
        Setting(
            namespace="downloader",
            key="downloader.quality",
            value="P1080",
            value_type=SettingValueType.String,
            updated_at=_now(),
        )


@pytest.mark.unit
def test_ac_3_12_forbidden_persistable_types_absent() -> None:
    import avkit_core.domain as domain_pkg
    import avkit_core.domain.download as download_mod
    import avkit_core.domain.queue as queue_mod
    import avkit_core.domain.tts as tts_mod

    forbidden = (
        "SABRState",
        "ModelFetchJob",
        "ConversionJob",
        "SourceLocator",
        "JobArtifact",
    )
    modules = (domain_pkg, download_mod, queue_mod, tts_mod)
    for name in forbidden:
        for module in modules:
            assert not hasattr(module, name)
    assert queue_mod.QueueRuntime.__module__.endswith("queue")


SPEC_CONVERT_OPTIONS_FIELDS = ("codec", "bitrate_kbps", "sample_rate", "channels")
SPEC_MEDIA_INFO_FIELDS = (
    "duration",
    "container",
    "video_codec",
    "audio_codec",
    "sample_rate",
    "channels",
    "width",
    "height",
    "fps",
    "bit_depth",
    "field_order",
    "streams",
)
YOUTUBE_PORT_METHODS = (
    "extract_info",
    "extract_video_ids",
    "download",
    "get_formats",
    "check_sabr_status",
    "test_cookies",
    "ytdlp_version",
)
TRANSCRIPT_PORT_METHODS = ("get_transcript",)
TTS_PORT_METHODS = (
    "load_model",
    "unload_model",
    "generate",
    "list_voices",
    "get_model_status",
    "available_devices",  # TA-3 (Session 35, MEU-75)
    "runtime_present",  # TA-3 (Session 51, MEU-117)
)
MEDIA_PORT_METHODS = (
    "is_available",
    "ffmpeg_version",
    "ffmpeg_binaries",  # TA-3 (Session 33, MEU-78)
    "convert",
    "probe",
    "detect_gpu",
    "encode",
    "cut",
    "extract_stream",
)
FILESYSTEM_PORT_METHODS = (
    "write_text_atomic",
    "write_progress_export",
    "ensure_channel_dirs",
    "write_audio_wav",
    "read_text",
)
MODEL_CATALOG_PORT_METHODS = ("download", "sideload")
UOW_ATTRIBUTES = (
    "downloads",
    "archive",
    "transcripts",
    "tts_jobs",
    "settings",
    "models",
    "conversion_jobs",
    "commit",
    "rollback",
    "__enter__",
    "__exit__",
)


def _protocol_methods(cls: type[object]) -> tuple[str, ...]:
    return tuple(
        name
        for name, value in cls.__dict__.items()
        if callable(value) and not name.startswith("_")
    )


@pytest.mark.unit
def test_ac_4_1_video_playlist_format_dtos() -> None:
    from avkit_core.domain.download import FormatInfo, PlaylistInfo, VideoInfo

    fmt = FormatInfo(
        format_id="22",
        ext="mp4",
        height=720,
        abr=128.0,
        vcodec="avc1",
        acodec="mp4a",
    )
    info = VideoInfo(video_id="abc123", title="Example", duration=12.5, formats=[fmt])
    playlist = PlaylistInfo(playlist_id="PL1", title="List", video_ids=["abc123"])
    assert info.formats[0].format_id == "22"
    assert playlist.video_ids == ["abc123"]
    with pytest.raises(TypeError):
        VideoInfo(video_id="abc123", title="Example", duration=None)


@pytest.mark.unit
def test_ac_4_2_download_options_have_no_cookie_bytes() -> None:
    from avkit_core.domain.download import DownloadOptions
    from avkit_core.domain.enums import AudioFormat, QualityPreset

    options = DownloadOptions(
        quality=QualityPreset.P1080,
        audio_only=False,
        audio_format=AudioFormat.Default,
        output_dir=Path("out"),
        mode="browser",
        browser="chrome",
        profile=None,
        cookie_file=None,
    )
    assert "cookies" not in _field_names(DownloadOptions)
    assert options.cookie_file is None


@pytest.mark.unit
def test_ac_4_3_download_result_requires_sabr_detected() -> None:
    from avkit_core.domain.download import DownloadResult

    result = DownloadResult(
        file_path=Path("video.mp4"),
        file_size=10,
        video_id="abc123",
        title="Example",
        sabr_detected=False,
    )
    assert result.sabr_detected is False
    with pytest.raises(TypeError):
        DownloadResult(
            file_path=Path("video.mp4"),
            file_size=10,
            video_id="abc123",
            title="Example",
        )


@pytest.mark.unit
def test_ac_4_4_cookie_test_result_shape() -> None:
    from avkit_core.domain.download import CookieTestResult

    result = CookieTestResult(ok=True, error_message=None)
    assert _field_names(CookieTestResult) == ("ok", "error_message")
    assert result.ok is True
    assert "cookies" not in _field_names(CookieTestResult)


@pytest.mark.unit
def test_ac_4_5_transcript_result_is_port_return_only() -> None:
    from avkit_core.domain.transcript import ChannelInfo, TranscriptItem, TranscriptResult

    info = ChannelInfo(
        channel_id="UC1", name="Example", url="https://youtube.com/@e", video_count=3
    )
    result = TranscriptResult(video_id="abc123", title="Example", text="hello", language="en")
    assert info.video_count == 3
    assert result.text == "hello"
    assert "text" not in _field_names(TranscriptItem)


@pytest.mark.unit
def test_ac_4_6_convert_options_and_media_info_fields() -> None:
    from avkit_core.domain.progress import (
        CONVERT_OPTIONS_FIELDS,
        MEDIA_INFO_FIELDS,
        ConvertOptions,
        MediaInfo,
    )

    assert CONVERT_OPTIONS_FIELDS == SPEC_CONVERT_OPTIONS_FIELDS
    assert MEDIA_INFO_FIELDS == SPEC_MEDIA_INFO_FIELDS
    assert _field_names(ConvertOptions) == CONVERT_OPTIONS_FIELDS
    assert _field_names(MediaInfo) == MEDIA_INFO_FIELDS
    assert "codec" not in _field_names(MediaInfo)
    ConvertOptions(codec="mp3", bitrate_kbps=80, sample_rate=44100, channels=1)
    MediaInfo(
        duration=1.0,
        container="mp3",
        video_codec=None,
        audio_codec="mp3",
        sample_rate=44100,
        channels=1,
    )
    with pytest.raises(TypeError):
        ConvertOptions(codec="mp3", bitrate_kbps=80, sample_rate=44100)
    with pytest.raises(TypeError):
        MediaInfo(
            duration=1.0,
            container="mp3",
            video_codec=None,
            audio_codec="mp3",
            sample_rate=44100,
            channels=1,
            codec="legacy",
        )


@pytest.mark.unit
def test_ac_4_7_port_method_sets_and_signatures() -> None:
    from avkit_core.ports.filesystem import FilesystemPort
    from avkit_core.ports.media import MediaPort
    from avkit_core.ports.models import ModelCatalogPort
    from avkit_core.ports.transcript import TranscriptPort
    from avkit_core.ports.tts import TTSPort
    from avkit_core.ports.youtube import YouTubePort

    assert _protocol_methods(YouTubePort) == YOUTUBE_PORT_METHODS
    assert _protocol_methods(TranscriptPort) == TRANSCRIPT_PORT_METHODS
    assert _protocol_methods(TTSPort) == TTS_PORT_METHODS
    assert _protocol_methods(MediaPort) == MEDIA_PORT_METHODS
    assert _protocol_methods(FilesystemPort) == FILESYSTEM_PORT_METHODS
    assert _protocol_methods(ModelCatalogPort) == MODEL_CATALOG_PORT_METHODS
    generate = inspect.signature(TTSPort.generate)
    assert generate.return_annotation != inspect.Signature.empty
    catalog_progress = inspect.signature(ModelCatalogPort.download).parameters["on_progress"]
    assert catalog_progress.annotation is not inspect.Parameter.empty
    youtube_extract = inspect.signature(YouTubePort.extract_info)
    assert list(youtube_extract.parameters) == ["self", "url", "flat"]
    assert youtube_extract.parameters["flat"].default is False
    assert youtube_extract.parameters["url"].annotation in {"str", str}
    assert "VideoInfo" in str(youtube_extract.return_annotation)
    assert "PlaylistInfo" in str(youtube_extract.return_annotation)
    tts_generate = inspect.signature(TTSPort.generate)
    assert list(tts_generate.parameters) == ["self", "text", "voice", "speed", "on_progress"]
    assert "ndarray" in str(tts_generate.return_annotation)
    fs_read = inspect.signature(FilesystemPort.read_text)
    assert list(fs_read.parameters) == ["self", "path", "max_bytes"]
    assert fs_read.parameters["max_bytes"].kind is inspect.Parameter.KEYWORD_ONLY
    catalog = inspect.signature(ModelCatalogPort.download)
    assert list(catalog.parameters) == ["self", "variant", "dest_dir", "on_progress"]
    assert str(catalog.parameters["on_progress"].annotation) in {
        "Callable[[float], None]",
        "collections.abc.Callable[[float], None]",
    }


@pytest.mark.unit
def test_ac_4_8_read_text_max_bytes_is_keyword_only() -> None:
    from avkit_core.ports.filesystem import FilesystemPort

    params = inspect.signature(FilesystemPort.read_text).parameters
    assert params["max_bytes"].kind is inspect.Parameter.KEYWORD_ONLY
    assert "read_bytes" not in FilesystemPort.__dict__


@pytest.mark.unit
def test_ac_4_9_unit_of_work_attributes() -> None:
    from avkit_core.ports.storage import (
        ArchiveRepository,
        DownloadRepository,
        ModelRepository,
        SettingsRepository,
        TranscriptRepository,
        TTSJobRepository,
        UnitOfWork,
    )

    names = set(UnitOfWork.__annotations__) | {
        name
        for name in UnitOfWork.__dict__
        if not name.startswith("_") or name in {"__enter__", "__exit__"}
    }
    for attr in UOW_ATTRIBUTES:
        assert attr in names
    assert "items" not in UnitOfWork.__annotations__
    assert "items" not in UnitOfWork.__dict__
    assert _protocol_methods(DownloadRepository) == (
        "add",
        "get",
        "list_ordered",
        "save",
        "reorder",
        "delete",
        "delete_all",
        "reset_failed",
    )
    assert _protocol_methods(ArchiveRepository) == ("get", "add", "list")
    assert _protocol_methods(TranscriptRepository) == (
        "add_job",
        "get_job",
        "list_jobs_ordered",
        "save_job",
        "reorder_jobs",
        "delete_job",
        "replace_items",
        "list_items",
        "save_item",
        "count_items",
        "count_items_with_status",
    )
    # TA-5 (Session 33, MEU-77)
    assert _protocol_methods(TTSJobRepository) == (
        "add",
        "get",
        "save",
        "delete",
        "list_by_status",
    )
    assert _protocol_methods(SettingsRepository) == (
        "get",
        "set",
        "get_namespace",
        "set_namespace",
    )
    assert _protocol_methods(ModelRepository) == ("list_catalog", "get", "mark_downloaded")
    archive_get = inspect.signature(ArchiveRepository.get)
    assert list(archive_get.parameters) == ["self", "extractor", "video_id"]
    model_mark = inspect.signature(ModelRepository.mark_downloaded)
    assert list(model_mark.parameters) == ["self", "variant_id", "path"]


@pytest.mark.unit
def test_review_f1_nan_and_infinity_are_rejected() -> None:
    from avkit_core.domain.enums import MediaFormat, TTSSourceKind, TTSStatus
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.progress import ProgressSnapshot
    from avkit_core.domain.tts import ModelDownloadRuntime, TTSJob

    with pytest.raises(ValidationError):
        ProgressSnapshot(
            fraction=math.nan,
            units_done=0,
            units_total=None,
            unit_label="bytes",
            rate=None,
            eta_seconds=None,
            error=None,
        )
    with pytest.raises(ValidationError):
        _download_job(progress=math.nan)
    with pytest.raises(ValidationError):
        ModelDownloadRuntime(
            variant_id=None,
            asset=None,
            state="Idle",
            fraction=math.inf,
            error_message=None,
        )
    with pytest.raises(ValidationError):
        TTSJob(
            id=str(uuid4()),
            source_kind=TTSSourceKind.Inline,
            source_path=None,
            text_hash="abc",
            text_preview="hello",
            voice="af_bella",
            speed=math.nan,
            format=MediaFormat.MP3,
            status=TTSStatus.Pending,
            output_path=None,
            segments_total=1,
            segments_done=0,
            error_message=None,
            created_at=_now(),
            updated_at=_now(),
        )


@pytest.mark.unit
def test_review_f2_unhashable_closed_set_values_raise_validation_error() -> None:
    from avkit_core.domain.enums import QueueProcessorState, SettingValueType
    from avkit_core.domain.errors import ValidationError
    from avkit_core.domain.queue import QueueRuntime
    from avkit_core.domain.settings import Setting
    from avkit_core.domain.tts import ModelDownloadRuntime

    with pytest.raises(ValidationError):
        QueueRuntime(queue_name=[], state=QueueProcessorState.Idle, current_job_id=None)
    with pytest.raises(ValidationError):
        Setting(
            namespace=[],
            key="quality",
            value="P1080",
            value_type=SettingValueType.String,
            updated_at=_now(),
        )
    with pytest.raises(ValidationError):
        ModelDownloadRuntime(
            variant_id=None, asset=None, state=[], fraction=0.0, error_message=None
        )


# --- MEU-42 re-queue widening (AC-42.1, AC-42.2, AC-42.4, AC-42.5) -------------
# The two partitions are spelled here as names so the test is an independent
# statement of the contract rather than a re-import of the code under test.
REQUEUEABLE_DOWNLOAD_NAMES = ("Failed", "Cancelled", "QualityBlocked", "AgeRestricted")
NON_REQUEUEABLE_DOWNLOAD_NAMES = ("Pending", "Downloading", "Done", "Skipped")
REQUEUEABLE_CONVERSION_NAMES = ("Failed", "Cancelled")
NON_REQUEUEABLE_CONVERSION_NAMES = ("Pending", "Processing", "Done", "Skipped")
DOWNLOAD_SERVICE_PATH = REPO_ROOT / "packages/core/src/avkit_core/services/download.py"
DOWNLOAD_ROUTES_PATH = REPO_ROOT / "packages/api/src/avkit_api/routes/downloads.py"


@pytest.mark.unit
def test_ac_42_1_requeueable_status_sets_are_single_statement() -> None:
    from avkit_core.domain.conversion import REQUEUEABLE_CONVERSION_STATUSES
    from avkit_core.domain.download import REQUEUEABLE_DOWNLOAD_STATUSES
    from avkit_core.domain.enums import ConversionStatus, DownloadStatus

    assert isinstance(REQUEUEABLE_DOWNLOAD_STATUSES, frozenset)
    assert isinstance(REQUEUEABLE_CONVERSION_STATUSES, frozenset)
    downloads = {DownloadStatus[name] for name in REQUEUEABLE_DOWNLOAD_NAMES}
    conversions = {ConversionStatus[name] for name in REQUEUEABLE_CONVERSION_NAMES}
    assert REQUEUEABLE_DOWNLOAD_STATUSES == downloads
    assert REQUEUEABLE_CONVERSION_STATUSES == conversions

    # Exhaustiveness: a status added to either enum without being classified fails here.
    other_downloads = {DownloadStatus[name] for name in NON_REQUEUEABLE_DOWNLOAD_NAMES}
    assert downloads | other_downloads == set(DownloadStatus)
    assert downloads & other_downloads == set()
    other_conversions = {ConversionStatus[name] for name in NON_REQUEUEABLE_CONVERSION_NAMES}
    assert conversions | other_conversions == set(ConversionStatus)
    assert conversions & other_conversions == set()

    # Single statement: each guard names the constant, and no other layer redefines it.
    from avkit_core.domain.conversion import ConversionJob
    from avkit_core.domain.download import DownloadJob

    assert "REQUEUEABLE_DOWNLOAD_STATUSES" in inspect.getsource(DownloadJob.reset_failed)
    assert "REQUEUEABLE_CONVERSION_STATUSES" in inspect.getsource(ConversionJob.reset_failed)
    for path in (DOWNLOAD_SERVICE_PATH, DOWNLOAD_ROUTES_PATH):
        assert "REQUEUEABLE_DOWNLOAD_STATUSES = " not in path.read_text(encoding="utf-8")


@pytest.mark.unit
def test_ac_42_2_download_transitions_gain_requeue_edges() -> None:
    from avkit_core.domain.download import DOWNLOAD_TRANSITIONS
    from avkit_core.domain.enums import DownloadStatus

    for name in REQUEUEABLE_DOWNLOAD_NAMES:
        allowed = DOWNLOAD_TRANSITIONS[DownloadStatus[name]]
        assert DownloadStatus.Pending in allowed
    for name in NON_REQUEUEABLE_DOWNLOAD_NAMES:
        allowed = DOWNLOAD_TRANSITIONS.get(DownloadStatus[name], frozenset())
        assert DownloadStatus.Pending not in allowed


@pytest.mark.unit
def test_ac_42_4_download_reset_failed_accepts_requeueable_set() -> None:
    from avkit_core.domain.enums import DownloadStatus

    for name in REQUEUEABLE_DOWNLOAD_NAMES:
        job = _download_job(status=DownloadStatus[name], error_message="boom", progress=0.4)
        reset = job.reset_failed()
        assert reset.status is DownloadStatus.Pending
        assert reset.error_message is None
        assert reset.progress == 0.0


@pytest.mark.unit
def test_ac_42_5_download_reset_failed_refuses_non_requeueable() -> None:
    from avkit_core.domain.download import REQUEUEABLE_DOWNLOAD_STATUSES
    from avkit_core.domain.enums import DownloadStatus
    from avkit_core.domain.errors import ConflictError

    for name in NON_REQUEUEABLE_DOWNLOAD_NAMES:
        with pytest.raises(ConflictError) as caught:
            _download_job(status=DownloadStatus[name]).reset_failed()
        message = str(caught.value)
        for member in REQUEUEABLE_DOWNLOAD_STATUSES:
            assert member.value in message


@pytest.mark.unit
def test_ac_115_1_failure_messages_skip_causes_and_safe_reason() -> None:
    transcript = importlib.import_module("avkit_core.domain.transcript")
    for name in (
        "TranscriptFailureCause",
        "TranscriptSkip",
        "failure_message",
        "safe_reason",
        "REASON_LIMIT",
    ):
        assert hasattr(transcript, name), f"avkit_core.domain.transcript has no {name}"
    from dataclasses import FrozenInstanceError
    from enum import StrEnum

    from avkit_core.domain.errors import ValidationError

    cause = transcript.TranscriptFailureCause
    message = transcript.failure_message
    assert issubclass(cause, StrEnum)
    assert [member.value for member in cause] == ["blocked", "no_captions", "unavailable", "other"]
    assert message(cause.blocked) == (
        "YouTube is blocking caption requests from this network. "
        "Try again later or from another network, then Resume."
    )
    assert message(cause.no_captions) == "No captions for this video."
    assert message(cause.unavailable) == "This video is unavailable."
    assert message(cause.other, "the video is age-restricted") == (
        "Couldn't get captions: the video is age-restricted."
    )
    assert message(cause.other) == "Couldn't get captions."
    assert message(cause.other, None) == "Couldn't get captions."
    for allowed in (cause.no_captions, cause.unavailable):
        skip = transcript.TranscriptSkip(allowed)
        assert skip.cause is allowed
        assert skip == transcript.TranscriptSkip(allowed)
        with pytest.raises(FrozenInstanceError):
            skip.cause = cause.other  # type: ignore[misc]
    for refused in (cause.blocked, cause.other):
        with pytest.raises(ValidationError):
            transcript.TranscriptSkip(refused)
    safe = transcript.safe_reason
    assert transcript.REASON_LIMIT == 200
    assert safe("first line\nsecond line") == "first line"
    linked = "see https://example.invalid/a?token=SYNTHETIC_API_MARKER and http://x.invalid"
    assert safe(linked) == "see [link] and [link]"
    assert safe("x" * 500) == "x" * 200
    # The URL is replaced before the cut, so a cut never leaves part of a URL.
    assert safe("y" * 190 + " https://example.invalid/" + "z" * 50) == "y" * 190 + " [link]"


@pytest.mark.unit
def test_ac_117_1_model_availability_and_reasons() -> None:
    domain_tts = importlib.import_module("avkit_core.domain.tts")
    for name in ("ModelAvailability", "model_availability", "MODEL_REASONS"):
        assert hasattr(domain_tts, name), f"avkit_core.domain.tts has no {name}"
    from dataclasses import FrozenInstanceError

    from avkit_core.domain.enums import ModelFormat
    from avkit_core.domain.errors import ValidationError

    reasons = domain_tts.MODEL_REASONS
    assert set(reasons) == set(ModelFormat)
    assert reasons[ModelFormat.PyTorch] == (
        "This build can't run PyTorch models. Choose an ONNX model."
    )
    assert reasons[ModelFormat.ONNX] == "This build can't run ONNX models. Reinstall av-kit."
    availability = domain_tts.ModelAvailability
    refused = domain_tts.model_availability(ModelFormat.PyTorch, False)
    assert (refused.available, refused.reason) == (False, reasons[ModelFormat.PyTorch])
    for fmt in ModelFormat:
        present = domain_tts.model_availability(fmt, True)
        assert (present.available, present.reason) == (True, None), fmt
        assert domain_tts.model_availability(fmt, False) == availability(False, reasons[fmt])
    with pytest.raises(FrozenInstanceError):
        refused.available = True
    for available, reason in ((True, "x"), (False, None), (False, "")):
        with pytest.raises(ValidationError):
            availability(available, reason)


@pytest.mark.unit
def test_ac_124_1_received_height_defaults_to_none_and_is_checked() -> None:
    from avkit_core.domain.download import DownloadResult
    from avkit_core.domain.errors import ValidationError

    def _result(**overrides: object) -> object:
        payload: dict[str, object] = {
            "file_path": Path("video.mp4"),
            "file_size": 10,
            "video_id": "abc123",
            "title": "Example",
            "sabr_detected": False,
            **overrides,
        }
        return DownloadResult(**payload)  # type: ignore[arg-type]

    assert _download_job().received_height is None
    assert _download_job(received_height=360).received_height == 360
    assert _result().height is None
    assert _result(height=360).height == 360
    for bad in (-1, True):
        with pytest.raises(ValidationError):
            _download_job(received_height=bad)
        with pytest.raises(ValidationError):
            _result(height=bad)
