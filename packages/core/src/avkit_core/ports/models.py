"""Model catalog download/sideload port protocol."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Protocol

from avkit_core.domain.tts import ModelVariant


class ModelCatalogPort(Protocol):
    """Hugging Face / sideload catalog operations. Progress is memory-only."""

    def download(
        self,
        variant: ModelVariant,
        dest_dir: Path,
        on_progress: Callable[[float], None],
    ) -> Path: ...

    def sideload(self, models_dir: Path) -> list[ModelVariant]: ...
