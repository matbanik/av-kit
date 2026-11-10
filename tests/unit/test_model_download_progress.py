"""rc.3 F4: a model download reports its bytes, not 0 until the whole file is on disk.

The fake `hf_hub_download` drives whatever `tqdm_class` it is given through huggingface_hub's
own progress code, on the HTTP path and on the Xet path, so the test breaks if the library
stops accepting the class the adapter hands it.
"""

from __future__ import annotations

import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from huggingface_hub.utils._xet_progress_reporting import XetDownloadProgressReporter
from huggingface_hub.utils.tqdm import _get_progress_bar_context

from avkit_core.domain.tts import ModelVariant
from avkit_infra.model_manager.catalog import CATALOG_METADATA
from avkit_infra.model_manager.manager import ModelCatalogAdapter

VARIANT_ID = "kokoro-pt-fp32"
TOTAL = 400


def _variant() -> ModelVariant:
    meta = CATALOG_METADATA[VARIANT_ID]
    return ModelVariant(
        id=VARIANT_ID,
        name=str(meta["name"]),
        format=meta["format"],  # type: ignore[arg-type]
        precision=meta["precision"],  # type: ignore[arg-type]
        size_bytes=int(meta["catalog_size_bytes"]),  # type: ignore[call-overload]
        path=None,
        is_downloaded=False,
    )


def _http_path(tqdm_class: Any) -> None:
    with _get_progress_bar_context(
        desc="kokoro-v1_0.pth",
        log_level=logging.INFO,
        total=TOTAL,
        initial=0,
        name="huggingface_hub.http_get",
        tqdm_class=tqdm_class,
    ) as bar:
        for _ in range(4):
            bar.update(TOTAL // 4)


def _xet_path(tqdm_class: Any) -> None:
    reporter = XetDownloadProgressReporter(
        reconstruction_desc="kokoro-v1_0.pth: reconstructing file",
        total=TOTAL,
        log_level=logging.INFO,
        name="huggingface_hub.xet_get",
        tqdm_class=tqdm_class,
    )
    for done in (100, 200, 300, 400):
        reporter.update_progress(
            SimpleNamespace(
                total_bytes=TOTAL,
                total_bytes_completed=done,
                total_bytes_completion_rate=None,
                total_transfer_bytes_completed=done // 2,
                total_transfer_bytes_completion_rate=None,
            )
        )
    reporter.close()


@pytest.mark.parametrize("path", [_http_path, _xet_path], ids=["http", "xet"])
def test_download_reports_byte_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, path: Any
) -> None:
    def fake_download(**kwargs: Any) -> str:
        path(kwargs.get("tqdm_class"))
        dest = Path(kwargs["local_dir"]) / kwargs["filename"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(b"model")
        return str(dest)

    monkeypatch.setattr("avkit_infra.model_manager.manager.hf_hub_download", fake_download)
    seen: list[float] = []
    ModelCatalogAdapter().download(_variant(), tmp_path, seen.append)
    assert [0.25, 0.5, 0.75] == [value for value in seen if 0.0 < value < 1.0]
    assert seen == sorted(seen)
    assert seen[0] == 0.0
    assert seen[-1] == 1.0
