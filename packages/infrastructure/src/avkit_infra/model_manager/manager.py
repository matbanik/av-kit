"""Hugging Face / sideload catalog adapter. Persistence is a later service MEU."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import structlog
from huggingface_hub import hf_hub_download

from avkit_core.domain.enums import ModelFormat, ModelPrecision
from avkit_core.domain.errors import ModelDownloadError, ValidationError
from avkit_core.domain.tts import ModelVariant, is_legacy_onnx_path
from avkit_infra.model_manager.catalog import CATALOG_METADATA, HF_FILE_MAP, sideload_variant_id
from avkit_infra.model_manager.progress import progress_bar_class
from avkit_infra.tts.voices import (
    ONNX_LOCAL_DIR,
    ONNX_REVISION,
    is_onnx_variant,
    variant_local_path,
)

log = structlog.get_logger(module="model_manager")


def _variant_from_meta(variant_id: str, path: Path) -> ModelVariant:
    meta = CATALOG_METADATA.get(variant_id)
    if meta is None:
        raise ModelDownloadError(f"unknown catalog variant: {variant_id}")
    catalog_size = meta["catalog_size_bytes"]
    if not isinstance(catalog_size, int) or isinstance(catalog_size, bool):
        raise ValidationError("catalog size is invalid")
    size = path.stat().st_size if path.is_file() else catalog_size
    fmt = meta["format"]
    precision = meta["precision"]
    if not isinstance(fmt, ModelFormat) or not isinstance(precision, ModelPrecision):
        raise ValidationError("catalog metadata types are invalid")
    name = meta["name"]
    if not isinstance(name, str):
        raise ValidationError("catalog metadata name is invalid")
    return ModelVariant(
        id=variant_id,
        name=name,
        format=fmt,
        precision=precision,
        size_bytes=size,
        path=path,
        is_downloaded=True,
    )


class ModelCatalogAdapter:
    """HF download and directory sideload. Persistence is a later service MEU."""

    def download(
        self,
        variant: ModelVariant,
        dest_dir: Path,
        on_progress: Callable[[float], None],
    ) -> Path:
        mapping = HF_FILE_MAP.get(variant.id)
        if mapping is None:
            raise ModelDownloadError(f"unknown variant id: {variant.id}")
        repo_id, filename = mapping
        dest_path = variant_local_path(variant.id, dest_dir)
        # A v0.19 file (LEGACY_ONNX_PATH) is never reused; the v1.0 weights are fetched.
        known = variant.path
        if known is not None and known.is_file() and not is_legacy_onnx_path(known, dest_dir):
            on_progress(1.0)
            return known
        if dest_path.is_file():
            on_progress(1.0)
            return dest_path
        try:
            on_progress(0.0)
            # The bytes as they arrive, not 0 until the whole file is on disk.
            bar = progress_bar_class(on_progress)
            if is_onnx_variant(variant.id):
                downloaded = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    revision=ONNX_REVISION,
                    local_dir=str(dest_dir / ONNX_LOCAL_DIR),
                    tqdm_class=bar,
                )
            else:
                downloaded = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    local_dir=str(dest_dir),
                    tqdm_class=bar,
                )
            on_progress(1.0)
        except (OSError, FileNotFoundError) as exc:
            raise ModelDownloadError("model download failed") from exc
        except Exception as exc:
            raise ModelDownloadError("model download failed") from OSError(str(exc))
        path = Path(downloaded)
        log.info("model.download", variant_id=variant.id, path=str(path))
        return path

    def sideload(self, models_dir: Path) -> list[ModelVariant]:
        found: dict[str, Path] = {}
        ignored: list[str] = []
        if models_dir.is_dir():
            for path in sorted(models_dir.rglob("*")):
                if not path.is_file():
                    continue
                if is_legacy_onnx_path(path, models_dir):
                    ignored.append(path.name)
                    continue
                variant_id = sideload_variant_id(path)
                if variant_id is None or variant_id in found:
                    continue
                found[variant_id] = path
        if ignored:
            log.info("model.legacy_onnx_ignored", directory=str(models_dir), files=ignored)
        return [_variant_from_meta(variant_id, path) for variant_id, path in found.items()]
