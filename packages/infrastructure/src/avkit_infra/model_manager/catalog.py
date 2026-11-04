"""Catalog maps for the model manager. Literal seed ids live under tts/."""

from avkit_infra.tts.voices import (
    CATALOG_METADATA,
    HF_FILE_MAP,
    SIDELOAD_SUFFIXES,
    sideload_variant_id,
)

__all__ = ["CATALOG_METADATA", "HF_FILE_MAP", "SIDELOAD_SUFFIXES", "sideload_variant_id"]
