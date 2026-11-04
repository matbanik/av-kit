"""Kokoro grapheme-to-phoneme routing (`G2P_ROUTE`) and phoneme chunking (`CHUNK_RULE`) (MEU-72).

`KokoroG2p` replaces kokoro's ``KPipeline`` front end, so the ONNX path runs without torch or
kokoro. English (lang codes a/b) goes to ``misaki.en.G2P``, with the eSpeak NG CLI as its
out-of-vocabulary fallback when it is installed. e/f/h/i/p go straight to the eSpeak NG CLI
(`EspeakCliAdapter`). ``misaki.espeak``, ``phonemizer`` and ``espeakng_loader`` are never
imported.

`split_phonemes` follows the cut order of kokoro 0.9.4 ``KPipeline``'s waterfall (Apache-2.0,
https://github.com/hexgrad/kokoro): sentence end, then clause mark, then space, then a hard cut
at the model's 510-symbol limit.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from avkit_core.domain.errors import ConflictError, ValidationError
from avkit_core.domain.tts import ESPEAK_LANG_CODES
from avkit_infra.tts.espeak import EspeakCliAdapter

__all__ = ["ENGLISH_LANG_CODES", "MAX_PHONEMES", "SPACY_MODEL", "KokoroG2p", "split_phonemes"]

ENGLISH_LANG_CODES = frozenset({"a", "b"})
# The spaCy pipeline `misaki.en.G2P(trf=False)` loads (misaki 0.9.4 `en.py:499`).
SPACY_MODEL = "en_core_web_sm"
# Kokoro's input limit: 510 phoneme symbols plus the two pad tokens (`MAX_ONNX_INPUT_IDS`).
MAX_PHONEMES = 510

SENTENCE_ENDS = ".!?"
CLAUSE_MARKS = ",;:—…"

MisakiFactory = Callable[..., Callable[[str], tuple[str | None, Any]]]


def _misaki_g2p_class() -> MisakiFactory:
    from misaki import en

    return en.G2P


class KokoroG2p:
    """`G2P_ROUTE`: text plus a Kokoro lang code to a phoneme string."""

    def __init__(
        self, espeak: EspeakCliAdapter, *, misaki_factory: MisakiFactory | None = None
    ) -> None:
        """Create the router.

        Args:
            espeak: The eSpeak NG CLI, for e/f/h/i/p and the English fallback.
            misaki_factory: Builds the English G2P (default: ``misaki.en.G2P``, imported on
                first use).
        """
        self._espeak = espeak
        self._misaki_factory = misaki_factory
        self._english: dict[bool, Callable[[str], tuple[str | None, Any]]] = {}

    def phonemize(self, text: str, lang_code: str) -> str:
        """Phonemize `text` for `lang_code`.

        Raises:
            ConflictError: English, and the spaCy model is not installed (`tts_spacy_model`).
            ValidationError: a lang code this runtime does not serve (j, z).
            TtsRuntimeError: the eSpeak NG subprocess failed.
        """
        if lang_code in ENGLISH_LANG_CODES:
            ps, _tokens = self._english_g2p(british=lang_code == "b")(text)
            return ps or ""
        if lang_code in ESPEAK_LANG_CODES:
            return self._espeak.phonemize(text, lang_code)
        raise ValidationError(f"no G2P serves lang_code {lang_code!r}")

    def _english_g2p(self, *, british: bool) -> Callable[[str], tuple[str | None, Any]]:
        cached = self._english.get(british)
        if cached is not None:
            return cached
        import spacy.util

        # misaki's `G2P.__init__` would otherwise run `spacy.cli.download`, a network install.
        if not spacy.util.is_package(SPACY_MODEL):
            raise ConflictError("tts asset missing: tts_spacy_model")
        factory = self._misaki_factory or _misaki_g2p_class()
        fallback = self._espeak.en_fallback(british) if self._espeak.status().available else None
        built = factory(trf=False, british=british, fallback=fallback, unk="")
        self._english[british] = built
        return built


def _cut_index(window: str) -> tuple[int, int]:
    """Where to end the chunk inside `window`, and where the rest starts."""
    for marks in (SENTENCE_ENDS, CLAUSE_MARKS):
        index = max(window.rfind(mark) for mark in marks)
        if index >= 0:
            return index + 1, index + 1
    space = window.rfind(" ")
    if space > 0:
        return space, space + 1
    return len(window), len(window)


def split_phonemes(ps: str, limit: int = MAX_PHONEMES) -> list[str]:
    """`CHUNK_RULE`: non-empty, stripped chunks of at most `limit` symbols, in order."""
    chunks: list[str] = []
    rest = ps.strip()
    while rest:
        if len(rest) <= limit:
            chunks.append(rest)
            break
        end, start = _cut_index(rest[:limit])
        chunk = rest[:end].strip()
        if chunk:
            chunks.append(chunk)
        rest = rest[start:].strip()
    return chunks
