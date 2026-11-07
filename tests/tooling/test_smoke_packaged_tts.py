"""The packaged smoke counts a WAV's frames only when its payload holds them.

Session 52 AC-121.8; execution review round 1 finding F2 (D-343).
"""

from __future__ import annotations

import struct
import sys
import wave
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import smoke_packaged_tts as smoke  # noqa: E402

RATE = 24_000
DECLARED = 100


class _DoneBackend:
    """Answers the generate call with a finished job whose output is `path`."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def ok(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        assert (method, path) == ("POST", "/tts/generate"), (method, path)
        return {"id": "job-1", "status": "Done", "output_path": str(self.path)}


def _header(frames: int) -> bytes:
    """A 16-bit mono PCM WAV header that declares `frames` frames."""
    data_bytes = frames * 2
    return (
        b"RIFF"
        + struct.pack("<I", 36 + data_bytes)
        + b"WAVEfmt "
        + struct.pack("<IHHIIHH", 16, 1, 1, RATE, RATE * 2, 2, 16)
        + b"data"
        + struct.pack("<I", data_bytes)
    )


def _generate(tmp_path: Path, wav: Path) -> dict[str, Any]:
    backend = cast(smoke.Backend, _DoneBackend(wav))
    return smoke._generate(backend, tmp_path, load=False)


def test_ac_121_8_header_only_wav_counts_no_samples(tmp_path: Path) -> None:
    wav = tmp_path / "header-only.wav"
    wav.write_bytes(_header(DECLARED))
    outcome = _generate(tmp_path, wav)
    assert (outcome["wav_samples"], outcome.get("wav_declared")) == (0, DECLARED)


def test_ac_121_8_truncated_wav_counts_no_samples(tmp_path: Path) -> None:
    wav = tmp_path / "truncated.wav"
    wav.write_bytes(_header(DECLARED) + b"\x00\x00" * (DECLARED // 2))
    outcome = _generate(tmp_path, wav)
    assert (outcome["wav_samples"], outcome.get("wav_declared")) == (0, DECLARED)


def test_ac_121_8_complete_wav_counts_its_frames(tmp_path: Path) -> None:
    wav = tmp_path / "complete.wav"
    with wave.open(str(wav), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(b"\x00\x00" * DECLARED)
    outcome = _generate(tmp_path, wav)
    got = (outcome["status"], outcome["wav_samples"], outcome["inside_out_dir"])
    assert got == ("Done", DECLARED, True)
