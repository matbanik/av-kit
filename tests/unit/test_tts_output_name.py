"""rc.3 F5: a generated file is named from its first three words and the voice.

Mat, 2026-11-09: "first 3 words from the Text with dash followed by voice"; ruling
"Lowercase slug (Recommended)".
"""

from __future__ import annotations

from pathlib import Path

import pytest
from tests.unit.test_tts_async import _require, _Stack

from avkit_core.domain.enums import MediaFormat, TTSStatus

WAIT = 5.0


@pytest.mark.parametrize(
    ("text", "voice", "stem"),
    [
        ("Hello world, this is a test.", "am_eric", "hello-world-this-am_eric"),
        ("  Hello   there.  ", "af_heart", "hello-there-af_heart"),
        ("— Wait... what?! Really now", "am_eric", "wait-what-really-am_eric"),
        ("Ça va? Très bien, merci", "ff_siwis", "ça-va-très-ff_siwis"),
        ("!!! ... ???", "am_eric", "speech-am_eric"),
        ("A" * 200, "am_eric", "a" * 60 + "-am_eric"),
    ],
)
def test_output_stem(text: str, voice: str, stem: str) -> None:
    from avkit_core.domain.tts import output_stem

    assert output_stem(text, voice) == stem


def _done(stack: _Stack, text: str, fmt: MediaFormat = MediaFormat.MP3) -> Path:
    job = stack.generate(text=text, fmt=fmt)
    assert stack.service.wait_idle(WAIT) is True
    done = stack.service.get_status(job.id)
    assert done.status is TTSStatus.Done
    assert done.output_path is not None
    return done.output_path


def test_generate_names_the_file_from_text_and_voice(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    assert _done(stack, "Hello world, this is a test.") == (
        stack.root / "hello-world-this-am_eric.mp3"
    )
    assert _done(stack, "Second take here", MediaFormat.WAV) == (
        stack.root / "second-take-here-am_eric.wav"
    )


def test_a_taken_name_gets_a_number(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    first = _done(stack, "Hello world again")
    first_bytes = first.read_bytes()
    second = _done(stack, "Hello world again")
    third = _done(stack, "Hello world again")
    assert first.name == "hello-world-again-am_eric.mp3"
    assert second.name == "hello-world-again-am_eric-2.mp3"
    assert third.name == "hello-world-again-am_eric-3.mp3"
    assert first.read_bytes() == first_bytes
