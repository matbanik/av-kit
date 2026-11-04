"""MEU-25 FFmpeg bundle wire — AC-25.4 and AC-25.5."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from avkit_infra.media.adapter import FFmpegAdapter, FFmpegNotFoundError


@pytest.mark.parametrize("ac_id", ["AC-25.4"], ids=["AC-25.4"])
def test_bundle_resolver_frozen_sibling(
    ac_id: str, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """AC-25.4 BUNDLE_RESOLVER + BUNDLE_WIRE from frozen sibling layout."""
    assert ac_id == "AC-25.4"
    from avkit_api import wiring

    assert hasattr(wiring, "bundled_ffmpeg")
    resources = tmp_path / "resources"
    backend = resources / "avkit-backend"
    ffmpeg_dir = resources / "ffmpeg"
    backend.mkdir(parents=True)
    ffmpeg_dir.mkdir(parents=True)
    exe = backend / "avkit-backend.exe"
    bundled = ffmpeg_dir / "ffmpeg.exe"
    exe.write_bytes(b"MZ")
    bundled.write_bytes(b"MZ")
    monkeypatch.setattr(wiring.sys, "frozen", True, raising=False)
    monkeypatch.setattr(wiring.sys, "executable", str(exe))
    resolved = wiring.bundled_ffmpeg()
    assert resolved == bundled
    src = inspect.getsource(wiring.build_services)
    assert "bundle_path" in src
    assert "bundled_ffmpeg" in src


@pytest.mark.parametrize("ac_id", ["AC-25.5"], ids=["AC-25.5"])
def test_probe_order_bundle_beats_path(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-25.5 PROBE_ORDER — bundled file wins over a PATH decoy."""
    assert ac_id == "AC-25.5"
    bundled = tmp_path / "ffmpeg.exe"
    bundled.write_text("bundled", encoding="utf-8")
    decoy_dir = tmp_path / "decoy"
    decoy_dir.mkdir()
    decoy = decoy_dir / "ffmpeg.exe"
    decoy.write_text("decoy", encoding="utf-8")
    monkeypatch.setenv("PATH", str(decoy_dir))
    adapter = FFmpegAdapter(configured_path=None, bundle_path=bundled)
    resolved = adapter._resolve_ffmpeg()
    assert resolved == bundled
    empty = FFmpegAdapter(configured_path=None, bundle_path=tmp_path / "missing.exe")
    monkeypatch.setenv("PATH", str(tmp_path / "empty-path"))
    with pytest.raises(FFmpegNotFoundError):
        empty._require_ffmpeg()
