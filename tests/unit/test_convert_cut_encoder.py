"""MEU-152 (Session 81) CUT_NO_GPU_ENCODER: a Cut saves no GPU encoder and runs no GPU check.

A Fast Copy Cut copies its streams, so, like an Extract (EXTRACT_NO_ENCODER), it needs no
encoder: it saves ``None``, which also clears a label an older build stored on the row. A
Reencode Cut is always re-encoded in software, so it saves ``"libx265"`` without a GPU check
(D-968). Product imports stay inside the tests so collection cannot ERROR.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest
from tests.unit.test_conversion_service import (
    GpuCountingMedia,
    RecordingMedia,
    _nvidia_caps,
    _process,
    _stack,
    _write_clip,
)


def _add_cut(service: object, tmp_path: Path, copy_mode: object) -> None:
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    service.add_to_queue(  # type: ignore[attr-defined]
        [_write_clip(tmp_path)],
        ConversionAddSpec(kind=ConversionKind.Cut, in_ms=500, out_ms=1500, copy_mode=copy_mode),
    )


@pytest.mark.parametrize(
    ("ac_id", "stored_mode"),
    [("AC-152.10", "FastCopy"), ("AC-152.10", None)],
    ids=["AC-152.10-fast-copy", "AC-152.10-copy-mode-none"],
)
@pytest.mark.unit
def test_ac_152_10_fast_copy_cut_saves_no_encoder(
    ac_id: str, stored_mode: str | None, tmp_path: Path
) -> None:
    assert ac_id == "AC-152.10"
    from avkit_core.domain.conversion import CutOptions
    from avkit_core.domain.enums import ConversionStatus, CutCopyMode

    media = GpuCountingMedia(gpu=_nvidia_caps())
    service, uow, _media, _settings = _stack(tmp_path, media)
    _add_cut(service, tmp_path, CutCopyMode.FastCopy)
    if stored_mode is None:
        job = uow.conversion_jobs.list_ordered()[0]
        uow.conversion_jobs.save(replace(job, copy_mode=None))
        uow.commit()
    _process(service)
    job = uow.conversion_jobs.list_ordered()[0]
    assert (job.status, job.gpu_encoder, media.detect_gpu_calls) == (
        ConversionStatus.Done,
        None,
        0,
    )
    assert media.encode_options == [
        CutOptions(in_ms=500, out_ms=1500, copy_mode=CutCopyMode.FastCopy)
    ]


@pytest.mark.parametrize("ac_id", ["AC-152.11"], ids=["AC-152.11-reencode"])
@pytest.mark.unit
def test_ac_152_11_reencode_cut_saves_software_encoder(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.11"
    from avkit_core.domain.enums import ConversionStatus, CutCopyMode

    media = GpuCountingMedia(gpu=_nvidia_caps())
    service, uow, _media, _settings = _stack(tmp_path, media)
    _add_cut(service, tmp_path, CutCopyMode.Reencode)
    _process(service)
    job = uow.conversion_jobs.list_ordered()[0]
    assert (job.status, job.gpu_encoder, media.detect_gpu_calls) == (
        ConversionStatus.Done,
        "libx265",
        0,
    )


@pytest.mark.parametrize("ac_id", ["AC-152.11"], ids=["AC-152.11-no-software-encoder"])
@pytest.mark.unit
def test_ac_152_11_fast_copy_cut_needs_no_software_encoder(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.11"
    from avkit_core.domain.conversion import GPUCapabilities
    from avkit_core.domain.enums import ConversionStatus, CutCopyMode

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
    _add_cut(service, tmp_path, CutCopyMode.FastCopy)
    _process(service)
    job = uow.conversion_jobs.list_ordered()[0]
    assert (job.status, job.error_message, job.gpu_encoder) == (ConversionStatus.Done, None, None)


@pytest.mark.parametrize("ac_id", ["AC-152.11"], ids=["AC-152.11-legacy-row"])
@pytest.mark.unit
def test_ac_152_11_legacy_cut_row_clears_its_encoder(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.11"
    from avkit_core.domain.enums import ConversionStatus, CutCopyMode

    media = RecordingMedia(gpu=_nvidia_caps())
    service, uow, _media, _settings = _stack(tmp_path, media)
    _add_cut(service, tmp_path, CutCopyMode.FastCopy)
    job = uow.conversion_jobs.list_ordered()[0]
    uow.conversion_jobs.save(
        replace(job, status=ConversionStatus.Failed, error_message="boom", gpu_encoder="hevc_nvenc")
    )
    uow.commit()
    service.reset_failed(job.id)
    _process(service)
    done = uow.conversion_jobs.list_ordered()[0]
    assert (done.status, done.gpu_encoder) == (ConversionStatus.Done, None)
