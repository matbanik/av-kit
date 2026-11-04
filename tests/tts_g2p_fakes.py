"""`G2P_SEAM` and voice-pack setup helpers for tests that drive `KokoroAdapter.generate`.

Session 32 plan (MEU-73): every Python test that reaches phonemes through the adapter goes
through the `tts_g2p_seam` fixture, so its body does not change when the engine underneath
switches. From MEU-72 the seam patches `avkit_infra.tts.adapter.KokoroG2p` with `FakeG2p`
and injects one through `KokoroAdapter(g2p=...)`. (Until MEU-72 it patched kokoro's
`KPipeline` with `FakeKPipeline`.)

Tests that build the adapter outside the fixture (the API stack, the AC-9.x cases) reach the
same fake through `set_phonemes` and `g2p_lang_codes`, which also follow the switch. They
read the fake that `_patch_engines` installed on `avkit_infra.tts.adapter`. Importing it is
not enough: pytest collects that file as `test_tts_models`, while
`from tests.integration.test_tts_models import ...` loads a second copy with its own fakes.

`write_voice_packs` seeds `VOICE_PACK` files (`{models_dir}/kokoro-v1.0-onnx/voices/<id>.bin`,
exactly 510*256*4 bytes) the way a finished `tts_voice_packs` download leaves them.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from avkit_infra.tts.voices import KOKORO_VOICE_IDS

PACK_ROWS = 510
STYLE_DIM = 256
PACK_BYTES = PACK_ROWS * STYLE_DIM * 4


def voice_pack_file(models_dir: Path, voice_id: str) -> Path:
    """The `VOICE_PACK` path for `voice_id` under `models_dir`."""
    return models_dir / "kokoro-v1.0-onnx" / "voices" / f"{voice_id}.bin"


def write_voice_pack(models_dir: Path, voice_id: str, pack: np.ndarray | None = None) -> Path:
    """Write one pack: `pack` (510x256 float32) or zeros."""
    path = voice_pack_file(models_dir, voice_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.zeros((PACK_ROWS, STYLE_DIM), dtype="<f4") if pack is None else pack
    array = np.ascontiguousarray(data, dtype="<f4")
    if array.shape != (PACK_ROWS, STYLE_DIM):
        raise ValueError(f"a voice pack is {PACK_ROWS}x{STYLE_DIM}, got {array.shape}")
    path.write_bytes(array.tobytes())
    return path


def write_voice_packs(models_dir: Path, voices: Iterable[str] | None = None) -> Path:
    """Write zero packs for `voices` (default: the whole catalog); return the voices dir."""
    for voice_id in KOKORO_VOICE_IDS if voices is None else voices:
        write_voice_pack(models_dir, voice_id)
    return models_dir / "kokoro-v1.0-onnx" / "voices"


def ramp_pack() -> np.ndarray:
    """A pack whose row `i` is filled with `i / 1000`, so a feed shows which row it used."""
    rows = np.arange(PACK_ROWS, dtype=np.float32)[:, None] / 1000.0
    return np.repeat(rows, STYLE_DIM, axis=1).astype("<f4")


class FakeG2p:
    """Stands in for `KokoroG2p`: records each phonemize request, returns `phonemes`."""

    calls: list[dict[str, str]] = []
    phonemes = "ab"

    def __init__(self, *args: object, **kwargs: object) -> None:
        pass

    def phonemize(self, text: str, lang_code: str) -> str:
        type(self).calls.append({"text": text, "lang_code": lang_code})
        return type(self).phonemes


def _active_g2p_fake() -> Any:
    """The G2P fake `_patch_engines` installed on the adapter module."""
    import avkit_infra.tts.adapter as adapter_mod

    return adapter_mod.KokoroG2p


def set_phonemes(phonemes: str) -> None:
    """Make the active G2P fake return `phonemes` for every request."""
    _active_g2p_fake().phonemes = phonemes


def g2p_lang_codes() -> list[str]:
    """The lang code of every phonemize request the active G2P fake has seen, oldest first."""
    return [str(call["lang_code"]) for call in _active_g2p_fake().calls]


class G2pSeam:
    """What a test needs from the phoneme source: an adapter factory and the phonemes."""

    def __init__(self, g2p: Any) -> None:
        self._g2p = g2p

    def adapter(self, **kwargs: Any) -> Any:
        from avkit_infra.tts.adapter import KokoroAdapter

        kwargs.setdefault("g2p", _active_g2p_fake()())
        return KokoroAdapter(**kwargs)

    def set_phonemes(self, phonemes: str) -> None:
        set_phonemes(phonemes)

    def lang_codes(self) -> list[str]:
        return g2p_lang_codes()

    @property
    def session(self) -> Any:
        """The recording `InferenceSession` fake the seam installed (its class-level `runs`)."""
        import avkit_infra.tts.adapter as adapter_mod

        return adapter_mod.InferenceSession


@pytest.fixture
def tts_g2p_seam(monkeypatch: pytest.MonkeyPatch) -> G2pSeam:
    """`G2P_SEAM`, `FakeG2p` phase: fake engines and a fixed phoneme string."""
    from tests.integration.test_tts_models import _patch_engines

    _patch_engines(monkeypatch)
    return G2pSeam(_active_g2p_fake())
