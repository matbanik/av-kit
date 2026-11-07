"""Model catalog request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from avkit_api.schemas.common import ApiModel

# Wire values of `avkit_core.domain.tts.TtsAsset` (TTS_ASSETS).
TtsAssetWire = Literal["tts_onnx_vocab", "tts_spacy_model", "tts_voice_packs"]
# Wire values of `avkit_core.domain.enums.DeviceType` (`DEVICE_WIRE_MAP`).
DeviceWire = Literal["auto", "cuda", "cpu", "mps"]


class ModelDownloadIn(ApiModel):
    """POST /models/download body: exactly one of `variant_id` or `asset`."""

    variant_id: str | None = Field(default=None, min_length=1)
    asset: TtsAssetWire | None = None

    @model_validator(mode="after")
    def _exactly_one_target(self) -> ModelDownloadIn:
        if (self.variant_id is None) == (self.asset is None):
            raise ValueError("exactly one of variant_id or asset is required")
        return self


class ModelLoadIn(ApiModel):
    """POST /models/load body."""

    variant_id: str = Field(min_length=1)
    device: Literal["auto", "cuda", "cpu", "mps"] = "auto"


class ModelVariantOut(ApiModel):
    """Catalog or downloaded variant."""

    id: str
    name: str
    format: str
    precision: str
    size_bytes: int
    path: str | None
    is_downloaded: bool
    # The devices this variant's format can load on here (`DEVICE_FIELD`).
    devices: list[DeviceWire]
    # Whether this build can run the variant (`MODEL_FIELDS`); `reason` is set exactly when
    # `available` is false, and says why and what to do instead.
    available: bool
    reason: str | None


class ModelListOut(ApiModel):
    """Available or downloaded list."""

    items: list[ModelVariantOut]


class ModelStatusOut(ApiModel):
    """Loaded model snapshot."""

    variant_id: str | None
    name: str
    device: str
    memory_bytes: int
    is_loaded: bool


class ModelDownloadRuntimeOut(ApiModel):
    """In-flight model or TTS-asset download snapshot."""

    variant_id: str | None
    asset: TtsAssetWire | None
    state: str
    fraction: float
    error_message: str | None


class ModelDownloadAcceptedOut(ApiModel):
    """202 immediate download acceptance: the variant, or the TTS asset, being fetched."""

    variant: ModelVariantOut | None
    asset: TtsAssetWire | None = None
