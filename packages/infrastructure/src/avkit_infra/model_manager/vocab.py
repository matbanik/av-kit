"""Kokoro vocab/config fetch from Hugging Face (MEU-62 `VOCAB_LOCATION`).

Kept under `model_manager`, the only infra package allowed to import `huggingface_hub`
(AC-9.12). `TtsAssetAdapter` receives `fetch_vocab` by injection from the composition root.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import structlog
from huggingface_hub import hf_hub_download

from avkit_core.domain.errors import ModelDownloadError
from avkit_infra.tts.assets import ONNX_VOCAB_FILE, ONNX_VOCAB_REPO, vocab_path

log = structlog.get_logger(module="model_manager")


def fetch_vocab(models_dir: Path, on_progress: Callable[[float], None]) -> Path:
    """Download `config.json` from `ONNX_VOCAB_REPO` into `models_dir`; return its path.

    Raises:
        ModelDownloadError: the Hugging Face download failed (cause chained).
    """
    on_progress(0.0)
    try:
        downloaded = hf_hub_download(
            repo_id=ONNX_VOCAB_REPO,
            filename=ONNX_VOCAB_FILE,
            local_dir=str(models_dir),
        )
    except Exception as exc:
        raise ModelDownloadError(f"vocab download failed: {exc}") from exc
    on_progress(1.0)
    path = Path(downloaded)
    if path != vocab_path(models_dir) and path.is_file():
        vocab_path(models_dir).write_bytes(path.read_bytes())
        path = vocab_path(models_dir)
    log.info("model.vocab_download", path=str(path))
    return path
