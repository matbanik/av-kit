"""MEU-28 conversion domain tests. Imports stay inside tests so collection cannot ERROR."""

from __future__ import annotations

import inspect
from dataclasses import fields
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest


def _now() -> datetime:
    return datetime.now(UTC)


def _job_kwargs(**overrides: object) -> dict[str, object]:
    from avkit_core.domain.enums import ConversionKind, ConversionPresetId, ConversionStatus

    base: dict[str, object] = {
        "id": str(uuid4()),
        "kind": ConversionKind.Compress,
        "input_path": Path("C:/in/a.mp4"),
        "output_path": Path("C:/out/a_compress.mp4"),
        "display_name": "a.mp4",
        "preset_id": ConversionPresetId.Balanced,
        "cq": 25,
        "scale_height": None,
        "audio_mode": None,
        "gpu_encoder": None,
        "in_ms": None,
        "out_ms": None,
        "copy_mode": None,
        "stream_index": None,
        "status": ConversionStatus.Pending,
        "progress": 0.0,
        "speed_bps": None,
        "eta_seconds": None,
        "file_size": None,
        "duration_seconds": None,
        "width": None,
        "height": None,
        "error_message": None,
        "queue_position": 0,
        "created_at": _now(),
        "updated_at": _now(),
    }
    base.update(overrides)
    return base


def _job(**overrides: object):  # type: ignore[no-untyped-def]
    from avkit_core.domain.conversion import ConversionJob

    return ConversionJob(**_job_kwargs(**overrides))


@pytest.mark.parametrize("ac_id", ["AC-28.1"], ids=["AC-28.1"])
@pytest.mark.unit
def test_ac_28_1_conversion_enums_persist_name(ac_id: str) -> None:
    assert ac_id == "AC-28.1"
    from avkit_core.domain.enums import (
        AudioEncodeMode,
        ConversionKind,
        ConversionPresetId,
        ConversionStatus,
        CutCopyMode,
        GpuPreference,
    )

    assert ConversionKind.Compress.name == "Compress"
    assert ConversionKind.Cut.name == "Cut"
    assert ConversionKind.Extract.name == "Extract"
    assert {m.name for m in ConversionStatus} == {
        "Pending",
        "Processing",
        "Done",
        "Failed",
        "Cancelled",
        "Skipped",
    }
    assert ConversionPresetId.Balanced.name == "Balanced"
    assert CutCopyMode.FastCopy.name == "FastCopy"
    assert AudioEncodeMode.Aac128.name == "Aac128"
    assert GpuPreference.Auto.name == "Auto"
    with pytest.raises(ValueError):
        ConversionKind("Unknown")


@pytest.mark.parametrize("ac_id", ["AC-28.2"], ids=["AC-28.2"])
@pytest.mark.unit
def test_ac_28_2_paused_is_not_a_conversion_status(ac_id: str) -> None:
    assert ac_id == "AC-28.2"
    from avkit_core.domain.enums import ConversionStatus
    from avkit_core.domain.errors import ValidationError

    assert "Paused" not in ConversionStatus.__members__
    with pytest.raises((ValidationError, ValueError, TypeError)):
        _job(status="Paused")


@pytest.mark.parametrize("ac_id", ["AC-28.3"], ids=["AC-28.3"])
@pytest.mark.unit
def test_ac_28_3_compress_forbids_trim_fields(ac_id: str) -> None:
    assert ac_id == "AC-28.3"
    from avkit_core.domain.errors import ValidationError

    with pytest.raises(ValidationError):
        _job(in_ms=0)
    with pytest.raises(ValidationError):
        _job(out_ms=1000)


@pytest.mark.parametrize("ac_id", ["AC-28.4"], ids=["AC-28.4"])
@pytest.mark.unit
def test_ac_28_4_cut_rejects_invalid_time_range(ac_id: str) -> None:
    assert ac_id == "AC-28.4"
    from avkit_core.domain.conversion import CutOptions
    from avkit_core.domain.enums import ConversionKind, CutCopyMode
    from avkit_core.domain.errors import InvalidTimeRangeError

    with pytest.raises(InvalidTimeRangeError):
        CutOptions(in_ms=1000, out_ms=1000, copy_mode=CutCopyMode.FastCopy)
    with pytest.raises(InvalidTimeRangeError):
        _job(
            kind=ConversionKind.Cut,
            preset_id=None,
            cq=None,
            in_ms=500,
            out_ms=500,
            copy_mode=CutCopyMode.FastCopy,
        )
    with pytest.raises(InvalidTimeRangeError):
        CutOptions(in_ms=-1, out_ms=10, copy_mode=CutCopyMode.FastCopy)


@pytest.mark.parametrize("ac_id", ["AC-28.5"], ids=["AC-28.5"])
@pytest.mark.unit
def test_ac_28_5_reset_failed_only_from_failed(ac_id: str) -> None:
    assert ac_id == "AC-28.5"
    from avkit_core.domain.enums import ConversionStatus
    from avkit_core.domain.errors import ConflictError

    failed = _job(status=ConversionStatus.Failed, error_message="boom", progress=0.4)
    reset = failed.reset_failed()
    assert reset.status is ConversionStatus.Pending
    assert reset.error_message is None
    assert reset.progress == 0.0
    done = _job(status=ConversionStatus.Done)
    with pytest.raises(ConflictError):
        done.reset_failed()


@pytest.mark.parametrize("ac_id", ["AC-28.6"], ids=["AC-28.6"])
@pytest.mark.unit
def test_ac_28_6_conversion_transitions_exhaustive(ac_id: str) -> None:
    assert ac_id == "AC-28.6"
    from avkit_core.domain.conversion import CONVERSION_TRANSITIONS
    from avkit_core.domain.enums import ConversionStatus

    assert set(CONVERSION_TRANSITIONS.keys()) == set(ConversionStatus)
    assert ConversionStatus.Skipped in CONVERSION_TRANSITIONS


@pytest.mark.parametrize("ac_id", ["AC-28.7"], ids=["AC-28.7"])
@pytest.mark.unit
def test_ac_28_7_mediaport_additive_requires_cancel_hook(ac_id: str) -> None:
    assert ac_id == "AC-28.7"
    from avkit_core.ports.media import MediaPort

    methods = tuple(
        name
        for name, value in MediaPort.__dict__.items()
        if callable(value) and not name.startswith("_")
    )
    keep = (
        "is_available",
        "ffmpeg_version",
        "ffmpeg_binaries",  # TA-11 (Session 33, MEU-78)
        "convert",
        "probe",
    )
    additive = ("detect_gpu", "encode", "cut", "extract_stream")
    assert methods == keep + additive
    for name in ("encode", "cut", "extract_stream"):
        params = inspect.signature(getattr(MediaPort, name)).parameters
        assert "on_progress" in params
        assert "should_stop" in params


@pytest.mark.parametrize("ac_id", ["AC-28.8"], ids=["AC-28.8"])
@pytest.mark.unit
def test_ac_28_8_mediainfo_additive_optional_defaults(ac_id: str) -> None:
    assert ac_id == "AC-28.8"
    from avkit_core.domain.progress import MediaInfo

    info = MediaInfo(
        duration=1.0,
        container="mp4",
        video_codec="hevc",
        audio_codec="aac",
        sample_rate=48000,
        channels=2,
    )
    assert info.width is None
    assert info.height is None
    assert info.fps is None
    assert info.bit_depth is None
    assert info.field_order is None
    assert info.streams is None
    names = {item.name for item in fields(MediaInfo)}
    assert names >= {
        "width",
        "height",
        "fps",
        "bit_depth",
        "field_order",
        "streams",
    }
    with pytest.raises(TypeError):
        MediaInfo(
            duration=1.0,
            container="mp4",
            video_codec="hevc",
            audio_codec="aac",
            sample_rate=48000,
            channels=2,
            codec="legacy",
        )


@pytest.mark.parametrize("ac_id", ["AC-28.9"], ids=["AC-28.9"])
@pytest.mark.unit
def test_ac_28_9_queue_names_and_frame_unit_label(ac_id: str) -> None:
    assert ac_id == "AC-28.9"
    from avkit_core.domain.enums import QueueProcessorState
    from avkit_core.domain.progress import UNIT_LABELS, ProgressSnapshot
    from avkit_core.domain.queue import QUEUE_NAMES, QueueRuntime

    assert "conversions" in QUEUE_NAMES
    QueueRuntime(
        queue_name="conversions",
        state=QueueProcessorState.Idle,
        current_job_id=None,
    )
    assert "frames" in UNIT_LABELS
    snapshot = ProgressSnapshot(
        fraction=0.1,
        units_done=1,
        units_total=10,
        unit_label="frames",
        rate=None,
        eta_seconds=None,
        error=None,
    )
    assert snapshot.unit_label == "frames"


@pytest.mark.parametrize("ac_id", ["AC-28.10"], ids=["AC-28.10"])
@pytest.mark.unit
def test_ac_28_10_converter_setting_namespace(ac_id: str) -> None:
    assert ac_id == "AC-28.10"
    from avkit_core.domain.enums import SettingValueType
    from avkit_core.domain.settings import SETTING_NAMESPACES, Setting

    assert "converter" in SETTING_NAMESPACES
    setting = Setting(
        namespace="converter",
        key="skip_existing",
        value="true",
        value_type=SettingValueType.Boolean,
        updated_at=_now(),
    )
    assert setting.namespace == "converter"


@pytest.mark.parametrize("ac_id", ["AC-28.11"], ids=["AC-28.11"])
@pytest.mark.unit
def test_ac_28_11_builtin_presets_five_frozen_default_balanced(ac_id: str) -> None:
    assert ac_id == "AC-28.11"
    from avkit_core.domain.conversion import ConversionPreset, builtin_conversion_presets
    from avkit_core.domain.enums import ConversionPresetId

    presets = builtin_conversion_presets()
    assert len(presets) == 5
    assert all(isinstance(item, ConversionPreset) for item in presets)
    ids = [item.preset_id for item in presets]
    assert ids == [
        ConversionPresetId.Archival,
        ConversionPresetId.HighQuality,
        ConversionPresetId.Balanced,
        ConversionPresetId.Sharing,
        ConversionPresetId.Mobile,
    ]
    balanced = next(item for item in presets if item.preset_id is ConversionPresetId.Balanced)
    assert balanced.preset_id is ConversionPresetId.Balanced
    assert getattr(ConversionPreset, "__dataclass_params__").frozen is True


@pytest.mark.parametrize("ac_id", ["AC-28.12"], ids=["AC-28.12"])
@pytest.mark.unit
def test_ac_28_12_convert_options_fields_unchanged(ac_id: str) -> None:
    assert ac_id == "AC-28.12"
    from avkit_core.domain.conversion import CONVERT_OPTIONS_FIELDS as CONV_REEXPORT
    from avkit_core.domain.progress import CONVERT_OPTIONS_FIELDS, ConvertOptions

    assert CONV_REEXPORT == CONVERT_OPTIONS_FIELDS
    assert CONVERT_OPTIONS_FIELDS == ("codec", "bitrate_kbps", "sample_rate", "channels")
    assert tuple(item.name for item in fields(ConvertOptions)) == CONVERT_OPTIONS_FIELDS


@pytest.mark.parametrize("ac_id", ["AC-28.13"], ids=["AC-28.13"])
@pytest.mark.unit
def test_ac_28_13_new_conversion_errors_exist(ac_id: str) -> None:
    assert ac_id == "AC-28.13"
    from avkit_core.domain.errors import (
        FFmpegEncodeError,
        FFmpegNotFoundError,
        GpuUnavailableError,
        InvalidTimeRangeError,
        MediaProbeError,
        ValidationError,
    )

    assert issubclass(FFmpegEncodeError, Exception)
    assert issubclass(MediaProbeError, Exception)
    assert issubclass(InvalidTimeRangeError, Exception)
    assert issubclass(GpuUnavailableError, Exception)
    assert FFmpegNotFoundError is FFmpegNotFoundError
    with pytest.raises(ValidationError):
        raise ValidationError("boundary")


@pytest.mark.parametrize("ac_id", ["AC-28.14"], ids=["AC-28.14"])
@pytest.mark.unit
def test_ac_28_14_gpu_capabilities_session_vo_not_a_table(ac_id: str) -> None:
    assert ac_id == "AC-28.14"
    from avkit_core.domain.conversion import GPUCapabilities

    caps = GPUCapabilities(
        nvidia_nvenc=False,
        amd_amf=False,
        intel_qsv=False,
        vulkan=False,
        software_h265=True,
        software_h264=True,
        recommended_encoder="libx265",
        checked_at=None,
    )
    assert caps.recommended_encoder == "libx265"
    assert not hasattr(GPUCapabilities, "__tablename__")
    assert not hasattr(caps, "__tablename__")


# --- MEU-42 re-queue widening (AC-42.3, AC-42.6) ------------------------------
REQUEUEABLE_CONVERSION_NAMES = ("Failed", "Cancelled")
NON_REQUEUEABLE_CONVERSION_NAMES = ("Pending", "Processing", "Done", "Skipped")


@pytest.mark.parametrize("ac_id", ["AC-42.3"], ids=["AC-42.3"])
@pytest.mark.unit
def test_ac_42_3_conversion_transitions_gain_requeue_edge(ac_id: str) -> None:
    assert ac_id == "AC-42.3"
    from avkit_core.domain.conversion import CONVERSION_TRANSITIONS
    from avkit_core.domain.enums import ConversionStatus

    # The table stays exhaustive: every status keeps a key.
    assert set(CONVERSION_TRANSITIONS) == set(ConversionStatus)
    for name in REQUEUEABLE_CONVERSION_NAMES:
        assert ConversionStatus.Pending in CONVERSION_TRANSITIONS[ConversionStatus[name]]
    for name in NON_REQUEUEABLE_CONVERSION_NAMES:
        assert ConversionStatus.Pending not in CONVERSION_TRANSITIONS[ConversionStatus[name]]
    requeue = frozenset({ConversionStatus.Pending})
    assert CONVERSION_TRANSITIONS[ConversionStatus.Cancelled] == requeue
    assert CONVERSION_TRANSITIONS[ConversionStatus.Done] == frozenset()
    assert CONVERSION_TRANSITIONS[ConversionStatus.Skipped] == frozenset()


@pytest.mark.parametrize("ac_id", ["AC-42.6"], ids=["AC-42.6"])
@pytest.mark.unit
def test_ac_42_6_conversion_reset_failed_widens_to_cancelled(ac_id: str) -> None:
    assert ac_id == "AC-42.6"
    from avkit_core.domain.conversion import REQUEUEABLE_CONVERSION_STATUSES
    from avkit_core.domain.enums import ConversionStatus
    from avkit_core.domain.errors import ConflictError

    for name in REQUEUEABLE_CONVERSION_NAMES:
        job = _job(status=ConversionStatus[name], error_message="boom", progress=0.4)
        reset = job.reset_failed()
        assert reset.status is ConversionStatus.Pending
        assert reset.error_message is None
        assert reset.progress == 0.0

    for name in NON_REQUEUEABLE_CONVERSION_NAMES:
        with pytest.raises(ConflictError) as caught:
            _job(status=ConversionStatus[name]).reset_failed()
        message = str(caught.value)
        for member in REQUEUEABLE_CONVERSION_STATUSES:
            assert member.value in message
