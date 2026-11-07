"""TTS model load/generate port protocol."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

import numpy as np

from avkit_core.domain.enums import DeviceType, ModelFormat
from avkit_core.domain.tts import (
    AssetState,
    EspeakStatus,
    ModelStatus,
    ModelVariant,
    TtsAsset,
    VoiceConfig,
)


class TTSPort(Protocol):
    """Kokoro load/generate surface. Services write files via FilesystemPort."""

    def load_model(self, variant: ModelVariant, device: DeviceType) -> None: ...

    def unload_model(self) -> None: ...

    def generate(
        self,
        text: str,
        voice: VoiceConfig,
        speed: float,
        on_progress: Callable[[float], None],
    ) -> np.ndarray: ...

    def list_voices(self) -> list[VoiceConfig]: ...

    def get_model_status(self) -> ModelStatus: ...

    def available_devices(self, fmt: ModelFormat) -> tuple[DeviceType, ...]:
        """The devices `fmt` can load on in this process (`DEVICE_PROBE`)."""
        ...

    def runtime_present(self, fmt: ModelFormat) -> bool:
        """Whether this process can import the runtime that loads `fmt` (`RUNTIME_PRESENT`)."""
        ...


class TtsAssetPort(Protocol):
    """Kokoro runtime assets (vocab/config file, spaCy model) under the models directory.

    `state` reports only what is on disk (`ready` or `missing`); an in-flight download is
    the ModelService runtime's business.
    """

    def state(self, asset: TtsAsset, models_dir: Path) -> AssetState: ...

    def version(self, asset: TtsAsset, models_dir: Path) -> str | None: ...

    def download(
        self,
        asset: TtsAsset,
        models_dir: Path,
        on_progress: Callable[[float], None],
    ) -> Path: ...

    def activate(self, models_dir: Path) -> None: ...


class EspeakPort(Protocol):
    """The user-installed eSpeak NG CLI (MEU-74). av-kit never ships or installs it.

    `status` re-probes on every call (`ESPEAK_DETECT`), so an install made while the app
    runs is seen without a restart. `phonemize` is `ESPEAK_G2P` for lang codes e/f/h/i/p.
    """

    def status(self) -> EspeakStatus: ...

    def phonemize(self, text: str, lang_code: str) -> str: ...
