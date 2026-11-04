"""Official Kokoro-82M voice catalog (HF VOICES.md document order)."""

from __future__ import annotations

from pathlib import Path

from avkit_core.domain.enums import ModelFormat, ModelPrecision
from avkit_core.domain.errors import ValidationError
from avkit_core.domain.tts import VoiceConfig

KOKORO_VOICE_IDS: tuple[str, ...] = (
    "af_heart",
    "af_alloy",
    "af_aoede",
    "af_bella",
    "af_jessica",
    "af_kore",
    "af_nicole",
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    "am_adam",
    "am_echo",
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa",
    "bf_alice",
    "bf_emma",
    "bf_isabella",
    "bf_lily",
    "bm_daniel",
    "bm_fable",
    "bm_george",
    "bm_lewis",
    "jf_alpha",
    "jf_gongitsune",
    "jf_nezumi",
    "jf_tebukuro",
    "jm_kumo",
    "zf_xiaobei",
    "zf_xiaoni",
    "zf_xiaoxiao",
    "zf_xiaoyi",
    "zm_yunjian",
    "zm_yunxi",
    "zm_yunxia",
    "zm_yunyang",
    "ef_dora",
    "em_alex",
    "em_santa",
    "ff_siwis",
    "hf_alpha",
    "hf_beta",
    "hm_omega",
    "hm_psi",
    "if_sara",
    "im_nicola",
    "pf_dora",
    "pm_alex",
    "pm_santa",
)

LANG_BY_PREFIX: dict[str, str] = {
    "a": "American English",
    "b": "British English",
    "e": "Spanish",
    "f": "French",
    "h": "Hindi",
    "i": "Italian",
    "j": "Japanese",
    "p": "Brazilian Portuguese",
    "z": "Mandarin Chinese",
}

VOICE_COUNT = 54

# ONNX_REPO pinned at ONNX_REVISION; the weights and voice packs land in ONNX_LOCAL_DIR.
ONNX_REPO = "onnx-community/Kokoro-82M-v1.0-ONNX"
ONNX_REVISION = "1939ad2a8e416c0acfeecc08a694d14ef25f2231"
ONNX_LOCAL_DIR = "kokoro-v1.0-onnx"

# VOICE_PACK: raw little-endian float32, one 256-wide style row per token count.
PACK_ROWS = 510
STYLE_DIM = 256
VOICE_PACK_BYTES = PACK_ROWS * STYLE_DIM * 4

HF_FILE_MAP: dict[str, tuple[str, str]] = {
    "kokoro-pt-fp32": ("hexgrad/Kokoro-82M", "kokoro-v1_0.pth"),
    "kokoro-onnx-fp32": (ONNX_REPO, "onnx/model.onnx"),
    "kokoro-onnx-fp16": (ONNX_REPO, "onnx/model_fp16.onnx"),
    "kokoro-onnx-int8": (ONNX_REPO, "onnx/model_quantized.onnx"),
}

CATALOG_METADATA: dict[str, dict[str, object]] = {
    "kokoro-pt-fp32": {
        "name": "PyTorch FP32",
        "format": ModelFormat.PyTorch,
        "precision": ModelPrecision.FP32,
        "catalog_size_bytes": 326 * 1024 * 1024,
    },
    "kokoro-onnx-fp32": {
        "name": "ONNX FP32",
        "format": ModelFormat.ONNX,
        "precision": ModelPrecision.FP32,
        "catalog_size_bytes": 326 * 1024 * 1024,
    },
    "kokoro-onnx-fp16": {
        "name": "ONNX FP16",
        "format": ModelFormat.ONNX,
        "precision": ModelPrecision.FP16,
        "catalog_size_bytes": 163 * 1024 * 1024,
    },
    "kokoro-onnx-int8": {
        "name": "ONNX INT8",
        "format": ModelFormat.ONNX,
        "precision": ModelPrecision.INT8,
        "catalog_size_bytes": 87 * 1024 * 1024,
    },
}

SIDELOAD_SUFFIXES = (".pth", ".onnx")


def is_onnx_variant(variant_id: str) -> bool:
    meta = CATALOG_METADATA.get(variant_id)
    return meta is not None and meta["format"] is ModelFormat.ONNX


def variant_local_path(variant_id: str, models_dir: Path) -> Path:
    """Where a download of `variant_id` lands: ONNX under `ONNX_LOCAL_DIR`, else the root.

    Raises:
        ValidationError: `variant_id` is not in `HF_FILE_MAP`.
    """
    mapping = HF_FILE_MAP.get(variant_id)
    if mapping is None:
        raise ValidationError(f"unknown catalog variant: {variant_id}")
    filename = mapping[1]
    if is_onnx_variant(variant_id):
        return models_dir / ONNX_LOCAL_DIR / filename
    return models_dir / filename


def voice_pack_path(models_dir: Path, voice_id: str) -> Path:
    """`VOICE_PACK` for `voice_id` under `models_dir`."""
    return models_dir / ONNX_LOCAL_DIR / "voices" / f"{voice_id}.bin"


def voice_pack_ready(models_dir: Path, voice_id: str) -> bool:
    path = voice_pack_path(models_dir, voice_id)
    return path.is_file() and path.stat().st_size == VOICE_PACK_BYTES


def sideload_variant_id(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix not in SIDELOAD_SUFFIXES:
        return None
    name = path.name.lower()
    if suffix == ".pth":
        return "kokoro-pt-fp32"
    if "fp16" in name:
        return "kokoro-onnx-fp16"
    if "quantized" in name or "int8" in name:
        return "kokoro-onnx-int8"
    if name == "model.onnx" or "fp32" in name:
        return "kokoro-onnx-fp32"
    return None


def voice_config_for(voice_id: str) -> VoiceConfig:
    language = LANG_BY_PREFIX.get(voice_id[0])
    if language is None:
        raise ValidationError(f"unknown voice language prefix: {voice_id}")
    gender = "Female" if len(voice_id) > 1 and voice_id[1] == "f" else "Male"
    style = voice_id.split("_", 1)[1] if "_" in voice_id else voice_id
    return VoiceConfig(
        voice_id=voice_id,
        lang_code=voice_id[0],
        language=language,
        gender=gender,
        style_description=style,
    )


def list_voice_configs() -> list[VoiceConfig]:
    return [voice_config_for(voice_id) for voice_id in KOKORO_VOICE_IDS]
