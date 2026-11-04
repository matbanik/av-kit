"""MEU-78 FFmpeg resolver: RESOLVER_ORDER, LIVE_SOURCE, FFPROBE_RULE (AC-78.1-78.4).

Real temp files stand in for the binaries; `shutil.which` and `subprocess.run` are patched
on the adapter module, so no real ffmpeg runs. New symbols are asserted present before use.
"""

from __future__ import annotations

import inspect
import subprocess
from pathlib import Path
from typing import Any

import pytest

from avkit_core.domain.errors import FFmpegNotFoundError
from avkit_core.domain.progress import ConvertOptions
from avkit_infra.media.adapter import FFmpegAdapter


def _require_resolver() -> None:
    import avkit_core.domain.conversion as conversion

    assert hasattr(conversion, "FFmpegBinaries"), (
        "avkit_core.domain.conversion.FFmpegBinaries is missing"
    )
    assert hasattr(FFmpegAdapter, "ffmpeg_binaries"), "FFmpegAdapter.ffmpeg_binaries is missing"
    assert "configured_source" in inspect.signature(FFmpegAdapter).parameters, (
        "FFmpegAdapter(configured_source=...) is missing"
    )


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"")
    return path


def _which(monkeypatch: pytest.MonkeyPatch, table: dict[str, Path]) -> None:
    def fake_which(name: str) -> str | None:
        found = table.get(name)
        return str(found) if found is not None else None

    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", fake_which)


def _runner(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    calls: list[list[str]] = []

    def fake_run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        del kwargs
        calls.append(list(command))
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", fake_run)
    return calls


def test_ac_78_1_configured_beats_bundle_then_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_resolver()
    configured = _touch(tmp_path / "cfg" / "ffmpeg.exe")
    bundle = _touch(tmp_path / "bundle" / "ffmpeg.exe")
    on_path = _touch(tmp_path / "path" / "ffmpeg.exe")
    missing = tmp_path / "missing" / "ffmpeg.exe"
    _which(monkeypatch, {"ffmpeg": on_path})

    chosen = FFmpegAdapter(configured_path=configured, bundle_path=bundle).ffmpeg_binaries()
    assert chosen is not None
    assert chosen.ffmpeg == configured

    bundled = FFmpegAdapter(configured_path=missing, bundle_path=bundle).ffmpeg_binaries()
    assert bundled is not None
    assert bundled.ffmpeg == bundle

    path_only = FFmpegAdapter(
        configured_path=missing, bundle_path=tmp_path / "no-bundle" / "ffmpeg.exe"
    ).ffmpeg_binaries()
    assert path_only is not None
    assert path_only.ffmpeg == on_path


def test_ac_78_1_nothing_found_neg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _require_resolver()
    _which(monkeypatch, {})
    calls = _runner(monkeypatch)
    adapter = FFmpegAdapter(
        configured_path=tmp_path / "a" / "ffmpeg.exe", bundle_path=tmp_path / "b" / "ffmpeg.exe"
    )
    assert adapter.ffmpeg_binaries() is None
    with pytest.raises(FFmpegNotFoundError):
        adapter.convert(
            tmp_path / "in.wav",
            tmp_path / "out.mp3",
            ConvertOptions(codec="libmp3lame", bitrate_kbps=None, sample_rate=None, channels=None),
        )
    assert calls == []


def test_ac_78_2_configured_source_has_no_latch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_resolver()
    target = tmp_path / "live" / "ffmpeg.exe"
    on_path = _touch(tmp_path / "path" / "ffmpeg.exe")
    _which(monkeypatch, {"ffmpeg": on_path})
    reads: list[Path] = []

    def source() -> Path:
        reads.append(target)
        return target

    adapter = FFmpegAdapter(configured_source=source)  # type: ignore[call-arg]
    before = adapter.ffmpeg_binaries()
    assert before is not None
    assert before.ffmpeg == on_path

    _touch(target)
    created = adapter.ffmpeg_binaries()
    assert created is not None
    assert created.ffmpeg == target

    target.unlink()
    removed = adapter.ffmpeg_binaries()
    assert removed is not None
    assert removed.ffmpeg == on_path
    assert len(reads) == 3


def test_ac_78_2_fixed_path_and_both_arguments_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_resolver()
    fixed = _touch(tmp_path / "fixed" / "ffmpeg.exe")
    _which(monkeypatch, {})
    found = FFmpegAdapter(configured_path=fixed).ffmpeg_binaries()
    assert found is not None
    assert found.ffmpeg == fixed

    consulted: list[int] = []

    def source() -> Path | None:
        consulted.append(1)
        return None

    with pytest.raises(ValueError):
        FFmpegAdapter(configured_path=fixed, configured_source=source)  # type: ignore[call-arg]
    assert consulted == []


def test_ac_78_3_ffprobe_sibling_then_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _require_resolver()
    ffmpeg = _touch(tmp_path / "bin" / "ffmpeg.exe")
    sibling = _touch(tmp_path / "bin" / "ffprobe.exe")
    path_probe = _touch(tmp_path / "path" / "ffprobe.exe")
    _which(monkeypatch, {"ffprobe": path_probe})
    adapter = FFmpegAdapter(configured_path=ffmpeg)

    beside = adapter.ffmpeg_binaries()
    assert beside is not None
    assert beside.ffprobe == sibling

    sibling.unlink()
    from_path = adapter.ffmpeg_binaries()
    assert from_path is not None
    assert from_path.ffmpeg == ffmpeg
    assert from_path.ffprobe == path_probe

    plain = _touch(tmp_path / "posix" / "ffmpeg")
    plain_probe = _touch(tmp_path / "posix" / "ffprobe")
    posix = FFmpegAdapter(configured_path=plain).ffmpeg_binaries()
    assert posix is not None
    assert posix.ffprobe == plain_probe


def test_ac_78_3_no_ffprobe_anywhere_neg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _require_resolver()
    ffmpeg = _touch(tmp_path / "bin" / "ffmpeg.exe")
    _which(monkeypatch, {})
    calls = _runner(monkeypatch)
    adapter = FFmpegAdapter(configured_path=ffmpeg)
    found = adapter.ffmpeg_binaries()
    assert found is not None
    assert found.ffmpeg == ffmpeg
    assert found.ffprobe is None
    with pytest.raises(FFmpegNotFoundError, match="ffprobe"):
        adapter.probe(tmp_path / "clip.mp4")
    assert calls == []


def test_ac_78_4_detect_gpu_runs_the_binary_resolved_at_each_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_resolver()
    first = _touch(tmp_path / "one" / "ffmpeg.exe")
    second = _touch(tmp_path / "two" / "ffmpeg.exe")
    _which(monkeypatch, {})
    calls = _runner(monkeypatch)
    current = {"path": first}
    adapter = FFmpegAdapter(configured_source=lambda: current["path"])  # type: ignore[call-arg]

    adapter.detect_gpu()
    assert calls
    assert {command[0] for command in calls} == {str(first)}

    calls.clear()
    current["path"] = second
    adapter.detect_gpu()
    assert calls
    assert {command[0] for command in calls} == {str(second)}


def test_ac_78_4_unchanged_path_probes_every_call_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_resolver()
    ffmpeg = _touch(tmp_path / "one" / "ffmpeg.exe")
    _which(monkeypatch, {})
    calls = _runner(monkeypatch)
    adapter = FFmpegAdapter(configured_source=lambda: ffmpeg)  # type: ignore[call-arg]
    adapter.detect_gpu()
    adapter.detect_gpu()
    encoder_lists = [command for command in calls if "-encoders" in command]
    assert len(encoder_lists) == 2
