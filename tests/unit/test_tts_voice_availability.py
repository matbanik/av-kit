"""MEU-74 voice availability (AC-74.1): `VOICE_REASON` over every Kokoro lang code."""

from __future__ import annotations

import pytest

from avkit_core.domain.errors import ValidationError

# (lang_code, espeak_available) -> (available, reason). D-70: j/z are unsupported in both states.
VOICE_REASON_TABLE: list[tuple[str, bool, bool, str | None]] = [
    ("a", False, True, None),
    ("a", True, True, None),
    ("b", False, True, None),
    ("b", True, True, None),
    ("e", False, False, "espeak_missing"),
    ("e", True, True, None),
    ("f", False, False, "espeak_missing"),
    ("f", True, True, None),
    ("h", False, False, "espeak_missing"),
    ("h", True, True, None),
    ("i", False, False, "espeak_missing"),
    ("i", True, True, None),
    ("p", False, False, "espeak_missing"),
    ("p", True, True, None),
    ("j", False, False, "language_unsupported"),
    ("j", True, False, "language_unsupported"),
    ("z", False, False, "language_unsupported"),
    ("z", True, False, "language_unsupported"),
]


def test_ac_74_1_table_covers_every_lang_code_in_both_states() -> None:
    from avkit_core.domain.tts import KOKORO_LANG_CODES, voice_availability  # noqa: F401

    rows = {(code, espeak) for code, espeak, _available, _reason in VOICE_REASON_TABLE}
    assert rows == {(code, espeak) for code in KOKORO_LANG_CODES for espeak in (False, True)}


@pytest.mark.parametrize(("lang_code", "espeak", "available", "reason"), VOICE_REASON_TABLE)
def test_ac_74_1_voice_availability_follows_voice_reason(
    lang_code: str, espeak: bool, available: bool, reason: str | None
) -> None:
    from avkit_core.domain.tts import voice_availability

    result = voice_availability(lang_code, espeak)
    assert (result.available, result.reason) == (available, reason)


def test_ac_74_1_reason_is_a_closed_string_enum() -> None:
    from avkit_core.domain.tts import VoiceUnavailableReason

    assert [member.value for member in VoiceUnavailableReason] == [
        "espeak_missing",
        "language_unsupported",
    ]
    assert VoiceUnavailableReason("espeak_missing") == "espeak_missing"


def test_ac_74_1_availability_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    from avkit_core.domain.tts import voice_availability

    result = voice_availability("a", False)
    with pytest.raises(FrozenInstanceError):
        result.available = False  # type: ignore[misc]


@pytest.mark.parametrize("lang_code", ["x", "", "A", "en"])
def test_ac_74_1_unknown_lang_code_raises_validation_error(lang_code: str) -> None:
    from avkit_core.domain.tts import voice_availability

    with pytest.raises(ValidationError):
        voice_availability(lang_code, True)
