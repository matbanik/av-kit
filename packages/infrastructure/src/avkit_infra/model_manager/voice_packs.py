"""Kokoro v1.0 voice-pack fetch from Hugging Face (MEU-73 `VOICE_PACK_DOWNLOAD`).

Kept under `model_manager`, the only infra package allowed to import `huggingface_hub`
(AC-9.12). `TtsAssetAdapter` receives `fetch_pack` by injection from the composition root
and does the size check itself.
"""

from __future__ import annotations

from pathlib import Path

from huggingface_hub import hf_hub_download

from avkit_core.domain.errors import ModelDownloadError
from avkit_infra.tts.voices import ONNX_LOCAL_DIR, ONNX_REPO, ONNX_REVISION, voice_pack_path


def fetch_voice_pack(voice_id: str, models_dir: Path) -> Path:
    """Download `voices/<voice_id>.bin` at `ONNX_REVISION` into `ONNX_LOCAL_DIR`.

    Raises:
        ModelDownloadError: the Hugging Face download failed; names the voice (cause chained).
    """
    try:
        hf_hub_download(
            repo_id=ONNX_REPO,
            filename=f"voices/{voice_id}.bin",
            revision=ONNX_REVISION,
            local_dir=str(models_dir / ONNX_LOCAL_DIR),
        )
    except Exception as exc:
        raise ModelDownloadError(f"voice pack {voice_id} download failed: {exc}") from exc
    return voice_pack_path(models_dir, voice_id)
