"""rc.3 F5: a generated file is named from its first three words and the voice.

Mat, 2026-11-09: "first 3 words from the Text with dash followed by voice"; ruling
"Lowercase slug (Recommended)".
"""

from __future__ import annotations

import uuid
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


# --- MEU-150 guards on the shipped names (AC-150.4 to AC-150.7) -------------------------
# These pin rc.3 F5 as shipped (`NAME_SAFE_GUARD`, `NAME_COLLISION_GUARD`, `LEGACY_OUTPUT_KEPT`):
# they pass when written, and one that fails is a product finding (S7), not a Red.

#: The characters Windows reserves in a file name (Microsoft Learn, "Naming files, paths, and
#: namespaces"): < > : " / \ | ? *, written as escapes so no test text depends on quoting.
RESERVED_CHARS = "".join(map(chr, (0x3C, 0x3E, 0x3A, 0x22, 0x2F, 0x5C, 0x7C, 0x3F, 0x2A)))
BACKSLASH = chr(0x5C)
SUPERSCRIPT_ONE = chr(0xB9)
CONTROLS = "".join(map(chr, (0x00, 0x07, 0x09, 0x0A, 0x0D, 0x1B, 0x1F, 0x7F)))
#: The reserved device names, with the superscript digits Windows also treats as digits.
DEVICE_NAMES = frozenset(
    {"con", "prn", "aux", "nul"}
    | {
        f"{port}{digit}"
        for port in ("com", "lpt")
        for digit in [*"0123456789", chr(0xB9), chr(0xB2), chr(0xB3)]
    }
)

UNSAFE_TEXTS = [
    pytest.param(f"a{RESERVED_CHARS}b c{RESERVED_CHARS} d", id="reserved-characters"),
    pytest.param(f"say{CONTROLS}this now please", id="control-characters"),
    pytest.param(f"..{BACKSLASH}..{BACKSLASH}x", id="dot-dot-backslash-x"),
    pytest.param(f"..{BACKSLASH}..{BACKSLASH}escape", id="dot-dot-backslash-escape"),
    pytest.param("../../escape", id="dot-dot-slash-escape"),
    pytest.param("CON", id="con"),
    pytest.param("nul.txt", id="nul-dot-txt"),
    pytest.param(f"COM{SUPERSCRIPT_ONE} LPT1", id="com-superscript-lpt1"),
    pytest.param("trailing dots...", id="trailing-dots"),
    pytest.param("trailing spaces   ", id="trailing-spaces"),
    pytest.param("end. . .", id="dot-space-tail"),
]


def _is_safe_stem(stem: str) -> list[str]:
    """Every way `stem` breaks `NAME_SAFE_GUARD`; empty when it is safe."""
    faults = [f"reserved {char!r}" for char in RESERVED_CHARS if char in stem]
    faults += [f"control {char!r}" for char in stem if ord(char) < 0x20 or ord(char) == 0x7F]
    if "." in stem:
        faults.append("a dot")
    if " " in stem:
        faults.append("a space")
    if stem.endswith((".", " ")):
        faults.append("a trailing dot or space")
    for part in {stem.casefold(), stem.split(".")[0].casefold()}:
        if part in DEVICE_NAMES:
            faults.append(f"device name {part!r}")
    return faults


@pytest.mark.parametrize("text", UNSAFE_TEXTS)
def test_ac_150_4_unsafe_text_gives_a_safe_name(tmp_path: Path, text: str) -> None:
    from avkit_core.domain.tts import output_stem

    stem = output_stem(text, "am_eric")
    assert _is_safe_stem(stem) == []
    assert stem.endswith("-am_eric")
    _require()
    stack = _Stack(tmp_path)
    written = _done(stack, text)
    assert written.parent == stack.root
    assert written.name == f"{stem}.mp3"
    assert sorted(path.name for path in stack.root.iterdir()) == [f"{stem}.mp3"]


def test_ac_150_5_text_with_no_word_gives_speech(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    assert _done(stack, RESERVED_CHARS) == stack.root / "speech-am_eric.mp3"


@pytest.mark.parametrize("suffix", [".mp3", ".wav"])
def test_ac_150_6_a_users_file_is_never_overwritten(tmp_path: Path, suffix: str) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.root.mkdir(parents=True)
    mine = stack.root / f"hello-world-again-am_eric{suffix}"
    mine.write_bytes(b"the user's own file")
    assert sorted(path.name for path in stack.root.iterdir()) == [mine.name]
    written = _done(stack, "Hello world again")
    assert written == stack.root / "hello-world-again-am_eric-2.mp3"
    assert mine.read_bytes() == b"the user's own file"
    assert sorted(path.name for path in stack.root.iterdir()) == sorted([mine.name, written.name])


def test_ac_150_7_legacy_output_and_job_id_are_kept(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.root.mkdir(parents=True)
    legacy = stack.root / f"{uuid.uuid4()}.mp3"
    legacy.write_bytes(b"a pre-rc.3 output")
    job = stack.generate(text="Hello there.")
    assert stack.service.wait_idle(WAIT) is True
    done = stack.service.get_status(job.id)
    assert done.status is TTSStatus.Done
    assert uuid.UUID(job.id).version == 4
    assert str(uuid.UUID(job.id)) == job.id
    assert done.output_path == stack.root / "hello-there-am_eric.mp3"
    assert done.output_path.name != f"{job.id}.mp3"
    assert legacy.read_bytes() == b"a pre-rc.3 output"
    assert sorted(path.name for path in stack.root.iterdir()) == sorted(
        [legacy.name, "hello-there-am_eric.mp3"]
    )
