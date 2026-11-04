"""MEU-72 AC-72.2 `G2P_ROUTE` and AC-72.3 `CHUNK_RULE`.

The new `avkit_infra.tts.g2p` symbols are imported inside each test, so before Green every
test fails on the missing module rather than at collection.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from tests.tts_g2p_fakes import (
    G2pSeam,
    tts_g2p_seam,  # noqa: F401 — the G2P_SEAM fixture
    write_voice_pack,
)

from avkit_core.domain.errors import ConflictError, ValidationError
from avkit_infra.tts.espeak import ESPEAK_VOICE, EspeakCliAdapter

MISAKI_STUB_PS = "mɪsˈɑki"


class FakeEspeakRun:
    """The `run` seam of `EspeakCliAdapter`: `--version` succeeds, every G2P run prints `r`."""

    def __init__(self) -> None:
        self.argvs: list[list[str]] = []

    def __call__(self, argv: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        self.argvs.append(list(argv))
        stdout = "eSpeak NG text-to-speech: 1.52.0\n" if "--version" in argv else "r\n"
        return subprocess.CompletedProcess(argv, 0, stdout=stdout, stderr="")

    def g2p_argvs(self) -> list[list[str]]:
        return [argv for argv in self.argvs if "--version" not in argv]


class MisakiFactory:
    """Stands in for `misaki.en.G2P`: records each construction's kwargs."""

    def __init__(self) -> None:
        self.constructions: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> Callable[[str], tuple[str, list[object]]]:
        self.constructions.append(kwargs)
        return lambda text: (MISAKI_STUB_PS, [])


class _Token:
    def __init__(self, text: str) -> None:
        self.text = text


def _espeak(tmp_path: Path, run: FakeEspeakRun, *, available: bool = True) -> EspeakCliAdapter:
    exe = tmp_path / "espeak-ng.exe"
    exe.write_bytes(b"exe")
    found = str(exe) if available else None
    return EspeakCliAdapter(which=lambda _name: found, environ={}, run=run)


@pytest.fixture
def spacy_model(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Fake `spacy.util.is_package` and record any `spacy.cli.download` call."""
    import spacy.cli
    import spacy.util

    state: dict[str, Any] = {"installed": True, "downloads": []}
    monkeypatch.setattr(spacy.util, "is_package", lambda _name: bool(state["installed"]))
    monkeypatch.setattr(
        spacy.cli, "download", lambda *args, **kwargs: state["downloads"].append(args)
    )
    return state


# --- AC-72.2 G2P_ROUTE ----------------------------------------------------------------------


@pytest.mark.unit
def test_ac_72_2_english_gets_espeak_fallback_only_when_available(
    tmp_path: Path, spacy_model: dict[str, Any]
) -> None:
    from avkit_infra.tts.g2p import KokoroG2p

    run = FakeEspeakRun()
    factory = MisakiFactory()
    g2p = KokoroG2p(_espeak(tmp_path, run), misaki_factory=factory)
    assert g2p.phonemize("Hello.", "a") == MISAKI_STUB_PS
    assert g2p.phonemize("Hello.", "b") == MISAKI_STUB_PS
    assert [kwargs["british"] for kwargs in factory.constructions] == [False, True]
    for kwargs in factory.constructions:
        assert kwargs["trf"] is False
        assert kwargs["unk"] == ""
        assert callable(kwargs["fallback"])
    # ESPEAK_EN_FALLBACK maps through EN_E2M (`r` -> `ɹ`), with rating 2.
    assert factory.constructions[0]["fallback"](_Token("x")) == ("ɹ", 2)
    assert ["-v", ESPEAK_VOICE["a"]] in [argv[4:6] for argv in run.g2p_argvs()]

    absent = MisakiFactory()
    g2p = KokoroG2p(_espeak(tmp_path, FakeEspeakRun(), available=False), misaki_factory=absent)
    assert g2p.phonemize("Hello.", "a") == MISAKI_STUB_PS
    assert len(absent.constructions) == 1
    assert absent.constructions[0]["fallback"] is None


@pytest.mark.unit
def test_ac_72_2_espeak_languages_use_multi_map_not_misaki(
    tmp_path: Path, spacy_model: dict[str, Any]
) -> None:
    from avkit_infra.tts.g2p import KokoroG2p

    factory = MisakiFactory()
    for code in ("e", "f", "h", "i", "p"):
        run = FakeEspeakRun()
        g2p = KokoroG2p(_espeak(tmp_path, run), misaki_factory=factory)
        # MULTI_E2M leaves `r` alone; EN_E2M would have produced `ɹ`.
        assert g2p.phonemize("hola", code) == "r", code
        argvs = run.g2p_argvs()
        assert argvs, code
        for argv in argvs:
            index = argv.index("-v")
            assert argv[index + 1] == ESPEAK_VOICE[code], code
    assert factory.constructions == []


@pytest.mark.unit
def test_ac_72_2_unserved_lang_codes_raise_validation_error(
    tmp_path: Path, spacy_model: dict[str, Any]
) -> None:
    from avkit_infra.tts.g2p import KokoroG2p

    factory = MisakiFactory()
    g2p = KokoroG2p(_espeak(tmp_path, FakeEspeakRun()), misaki_factory=factory)
    for code in ("j", "z"):
        with pytest.raises(ValidationError):
            g2p.phonemize("text", code)
    assert factory.constructions == []


@pytest.mark.unit
def test_ac_72_2_missing_spacy_model_is_409_before_misaki(
    tmp_path: Path, spacy_model: dict[str, Any]
) -> None:
    from avkit_infra.tts.g2p import KokoroG2p

    spacy_model["installed"] = False
    factory = MisakiFactory()
    g2p = KokoroG2p(_espeak(tmp_path, FakeEspeakRun()), misaki_factory=factory)
    with pytest.raises(ConflictError) as err:
        g2p.phonemize("Hello.", "a")
    assert str(err.value) == "tts asset missing: tts_spacy_model"
    assert factory.constructions == []
    assert spacy_model["downloads"] == []

    spacy_model["installed"] = True
    assert g2p.phonemize("Hello.", "a") == MISAKI_STUB_PS
    assert len(factory.constructions) == 1


@pytest.mark.unit
def test_ac_72_2_misaki_built_once_per_british_flag(
    tmp_path: Path, spacy_model: dict[str, Any]
) -> None:
    from avkit_infra.tts.g2p import KokoroG2p

    factory = MisakiFactory()
    g2p = KokoroG2p(_espeak(tmp_path, FakeEspeakRun()), misaki_factory=factory)
    for code in ("a", "a", "b", "b", "a"):
        assert g2p.phonemize("Hello.", code) == MISAKI_STUB_PS
    assert [kwargs["british"] for kwargs in factory.constructions] == [False, True]


# --- AC-72.3 CHUNK_RULE ---------------------------------------------------------------------


def _check_properties(ps: str, chunks: list[str]) -> None:
    assert all(chunks), chunks
    assert all(len(chunk) <= 510 for chunk in chunks)
    assert all(chunk == chunk.strip() for chunk in chunks)
    assert "".join(chunks).replace(" ", "") == ps.replace(" ", "")


@pytest.mark.unit
def test_ac_72_3_short_and_empty_input() -> None:
    from avkit_infra.tts.g2p import split_phonemes

    assert split_phonemes("") == []
    assert split_phonemes("ab. cd") == ["ab. cd"]


@pytest.mark.unit
def test_ac_72_3_cut_prefers_sentence_then_clause_then_space() -> None:
    from avkit_infra.tts.g2p import split_phonemes

    a, b, c = "a" * 100, "b" * 100, "c" * 400
    long_a, long_b = "a" * 300, "b" * 300
    cases = [
        # A sentence end beats a later clause mark.
        (f"{a}. {b * 2}, {c[:300]}", [f"{a}.", f"{b * 2}, {c[:300]}"]),
        # The last sentence end before the limit wins.
        (f"{a}. {b}! {c}", [f"{a}. {b}!", c]),
        (f"{a}. {b}? {c}", [f"{a}. {b}?", c]),
        # Without a sentence end, a clause mark beats a later space.
        (f"{a * 2}, {a} {long_b}", [f"{a * 2},", f"{a} {long_b}"]),
        (f"{long_a};{long_b}", [f"{long_a};", long_b]),
        (f"{long_a}:{long_b}", [f"{long_a}:", long_b]),
        (f"{long_a}—{long_b}", [f"{long_a}—", long_b]),
        (f"{long_a}…{long_b}", [f"{long_a}…", long_b]),
        # Without either, the last space.
        (f"{long_a} {long_b}", [long_a, long_b]),
    ]
    for ps, expected in cases:
        chunks = split_phonemes(ps)
        assert chunks == expected, ps
        _check_properties(ps, chunks)


@pytest.mark.unit
def test_ac_72_3_unbroken_run_splits_hard_at_510() -> None:
    from avkit_infra.tts.g2p import split_phonemes

    ps = "a" * 2000
    chunks = split_phonemes(ps)
    assert [len(chunk) for chunk in chunks] == [510, 510, 510, 470]
    _check_properties(ps, chunks)

    mixed = ("ab cd, ef. " * 120).strip()
    _check_properties(mixed, split_phonemes(mixed))


@pytest.mark.unit
def test_ac_72_3_empty_phonemes_generate_empty_audio(
    tmp_path: Path,
    tts_g2p_seam: G2pSeam,  # noqa: F811
) -> None:
    import numpy as np
    from tests.integration.test_tts_models import _variant, _voice

    from avkit_core.domain.enums import DeviceType

    vocab_path = tmp_path / "config.json"
    vocab_path.write_text(json.dumps({"vocab": {"a": 1}}), encoding="utf-8")
    write_voice_pack(tmp_path, "af_heart")
    onnx = tmp_path / "model.onnx"
    onnx.write_bytes(b"weights")
    adapter = tts_g2p_seam.adapter(onnx_vocab_path=vocab_path)
    adapter.load_model(_variant("kokoro-onnx-fp32", onnx), DeviceType.CPU)
    tts_g2p_seam.set_phonemes("")
    session = tts_g2p_seam.session
    for text in ("", "Hello."):
        session.runs = []
        progress: list[float] = []
        pcm = adapter.generate(text, _voice(), 1.0, progress.append)
        assert pcm.dtype == np.float32, text
        assert pcm.size == 0, text
        assert progress == [1.0], text
        assert session.runs == [], text
