"""Model catalog and download-runtime routes. No `{id}` paths."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Body, Depends, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_model_service
from avkit_api.schemas.common import EmptyIn
from avkit_api.schemas.models import (
    DeviceWire,
    ModelDownloadAcceptedOut,
    ModelDownloadIn,
    ModelDownloadRuntimeOut,
    ModelListOut,
    ModelLoadIn,
    ModelStatusOut,
    ModelVariantOut,
)
from avkit_core.domain.enums import DeviceType
from avkit_core.domain.tts import TtsAsset
from avkit_core.domain.wire import DEVICE_WIRE_MAP

CONFLICT_409: dict[int | str, dict[str, Any]] = {
    409: {
        "description": (
            "Conflict: a download is in flight, a TTS asset is missing or already ready, "
            "or the variant can't run in this build"
        ),
    },
}

# Inverse of `DEVICE_WIRE_MAP`, typed for `ModelVariantOut.devices` (`DEVICE_FIELD`).
_DEVICE_TO_WIRE: dict[DeviceType, DeviceWire] = {
    device: cast(DeviceWire, wire) for wire, device in DEVICE_WIRE_MAP.items()
}

router = APIRouter(prefix="/models", dependencies=[Depends(require_bearer)])


def _variant_out(variant: Any, models: Any) -> ModelVariantOut:
    path = None if variant.path is None else str(variant.path)
    devices: tuple[DeviceType, ...] = models.available_devices(variant.format)
    availability = models.availability(variant.format)
    return ModelVariantOut(
        id=variant.id,
        name=variant.name,
        format=variant.format.value,
        precision=variant.precision.value,
        size_bytes=variant.size_bytes,
        path=path,
        is_downloaded=variant.is_downloaded,
        devices=[_DEVICE_TO_WIRE[device] for device in devices],
        available=availability.available,
        reason=availability.reason,
    )


@router.get("/available", response_model=ModelListOut)
def list_available(models: Any = Depends(get_model_service)) -> ModelListOut:
    """Return the catalog union sideload."""
    return ModelListOut(items=[_variant_out(item, models) for item in models.list_available()])


@router.get("/downloaded", response_model=ModelListOut)
def list_downloaded(models: Any = Depends(get_model_service)) -> ModelListOut:
    """Return downloaded variants."""
    return ModelListOut(items=[_variant_out(item, models) for item in models.list_downloaded()])


@router.post(
    "/download",
    status_code=202,
    response_model=ModelDownloadAcceptedOut,
    responses=CONFLICT_409,
)
def download_model(
    body: ModelDownloadIn,
    models: Any = Depends(get_model_service),
) -> ModelDownloadAcceptedOut:
    """Accept a variant or TTS-asset download immediately.

    409 if one is in flight, or the variant can't run in this build.
    """
    if body.asset is not None:
        models.download_asset(TtsAsset(body.asset))
        return ModelDownloadAcceptedOut(variant=None, asset=body.asset)
    if body.variant_id is None:  # unreachable: ModelDownloadIn requires exactly one target
        raise ValueError("download body has neither variant_id nor asset")
    variant = models.download(body.variant_id)
    return ModelDownloadAcceptedOut(variant=_variant_out(variant, models))


@router.post("/load", response_model=ModelStatusOut, responses=CONFLICT_409)
def load_model(body: ModelLoadIn, models: Any = Depends(get_model_service)) -> ModelStatusOut:
    """Load a variant onto a device."""
    models.load(body.variant_id, DEVICE_WIRE_MAP[body.device])
    status = models.get_status()
    return ModelStatusOut(
        variant_id=status.variant_id,
        name=status.name,
        device=status.device,
        memory_bytes=status.memory_bytes,
        is_loaded=status.is_loaded,
    )


@router.post("/unload", status_code=204)
def unload_model(
    body: EmptyIn | None = Body(default=None),
    models: Any = Depends(get_model_service),
) -> Response:
    """Unload the current model."""
    del body
    models.unload()
    return Response(status_code=204)


@router.get("/status", response_model=ModelStatusOut)
def model_status(models: Any = Depends(get_model_service)) -> ModelStatusOut:
    """Return the loaded-model snapshot."""
    status = models.get_status()
    return ModelStatusOut(
        variant_id=status.variant_id,
        name=status.name,
        device=status.device,
        memory_bytes=status.memory_bytes,
        is_loaded=status.is_loaded,
    )


@router.get("/download-runtime", response_model=ModelDownloadRuntimeOut)
def download_runtime(models: Any = Depends(get_model_service)) -> ModelDownloadRuntimeOut:
    """Poll in-flight model download state."""
    runtime = models.get_download_runtime()
    return ModelDownloadRuntimeOut(
        variant_id=runtime.variant_id,
        asset=None if runtime.asset is None else runtime.asset.value,
        state=runtime.state,
        fraction=runtime.fraction,
        error_message=runtime.error_message,
    )
