"""MEU-148 console home short form: the 8.3 form of the home folder becomes "~" too.

AC-148.1 to AC-148.9 (docs/execution/plans/2026-11-15-text-scrub-residuals, D-337, D-925 to
D-927). The home and its short form are synthetic; no test reads or writes the real home
folder. Each test asserts the new names exist before any patch (Session 52 RULE-4), so a
missing name fails as an assertion.
"""

from __future__ import annotations

import os
import sys
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from avkit_core.services import health
from avkit_core.services.download import scrub_line

#: The D-335 synthetic home (tests/unit/test_services.py) and a synthetic short form of it.
SYNTHETIC_HOME = "C:\\Users\\SYNTHETIC_HOME_USER"
SYNTHETIC_SHORT = "C:\\Users\\SYNTHE~1"
OTHER_HOME = "C:\\Users\\OTHER_SYNTHETIC_USER"


def _require_names(*extra: str) -> None:
    assert hasattr(health, "home_forms")
    assert hasattr(health, "short_path_name")
    for name in extra:
        assert hasattr(health, name)


class CountingLookup:
    """A stand-in for `short_path_name` that records each path it is asked about."""

    def __init__(self, answers: dict[str, str]) -> None:
        self.answers = answers
        self.calls: list[str] = []

    def __call__(self, path: str) -> str:
        self.calls.append(path)
        return self.answers.get(path, "")


def _short_ready(
    monkeypatch: pytest.MonkeyPatch,
    *,
    short: str = SYNTHETIC_SHORT,
    lookup: bool = True,
    ignore_case: bool = True,
) -> CountingLookup:
    """Asserts the names exist, then patches the home, both flags, the lookup and the cache."""
    _require_names()
    fake = CountingLookup({SYNTHETIC_HOME: short})
    monkeypatch.setattr(health, "home_folder", lambda: SYNTHETIC_HOME)
    monkeypatch.setattr(health, "HOME_IGNORES_CASE", ignore_case)
    monkeypatch.setattr(health, "SHORT_FORM_LOOKUP", lookup)
    monkeypatch.setattr(health, "short_path_name", fake)
    monkeypatch.setattr(health, "_SHORT_FORMS", {})
    return fake


Script = Callable[[str, Any, int], int]


class FakeNative:
    """A stand-in for the `GetShortPathNameW` callable; records `(path, buffer is None, size)`."""

    def __init__(self, script: Script) -> None:
        self.script = script
        self.calls: list[tuple[str, bool, int]] = []

    def __call__(self, path: str, buffer: Any, size: int) -> int:
        self.calls.append((path, buffer is None, size))
        return self.script(path, buffer, size)


def _fills_alias(_path: str, buffer: Any, size: int) -> int:
    if buffer is None:
        return len(SYNTHETIC_SHORT) + 1
    buffer.value = SYNTHETIC_SHORT
    return len(SYNTHETIC_SHORT)


def _native_ready(monkeypatch: pytest.MonkeyPatch, native: FakeNative | None) -> None:
    """Asserts the names exist, then makes `_short_path_api` return `native`."""
    _require_names("_short_path_api")
    monkeypatch.setattr(health, "_short_path_api", lambda: native)


def _scrub_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    """The home, both flags and a fresh cache, with the real `short_path_name` kept."""
    monkeypatch.setattr(health, "home_folder", lambda: SYNTHETIC_HOME)
    monkeypatch.setattr(health, "HOME_IGNORES_CASE", True)
    monkeypatch.setattr(health, "SHORT_FORM_LOOKUP", True)
    monkeypatch.setattr(health, "_SHORT_FORMS", {})


def test_ac_148_1_real_native_lookup_does_not_break(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require_names("_short_path_api")
    if sys.platform == "win32":
        assert callable(health._short_path_api())
        folder = tmp_path / "LongFolderNameForShortForm"
        folder.mkdir()
        got = health.short_path_name(str(folder))
        assert got == "" or os.path.samefile(got, folder)
        assert health.short_path_name(str(tmp_path / "MissingSyntheticFolder" / "f")) == ""
    linux = types.SimpleNamespace(platform="linux", stdout=sys.stdout, stderr=sys.stderr)
    monkeypatch.setattr(health, "sys", linux)
    assert health._short_path_api() is None
    assert health.short_path_name(str(tmp_path)) == ""


SHORT_TO_TILDE = (
    ("at C:\\Users\\SYNTHE~1\\.avkit\\m.onnx", "at ~\\.avkit\\m.onnx"),
    ("at C:/Users/SYNTHE~1/.avkit/m.onnx", "at ~/.avkit/m.onnx"),
    ("at 'C:\\\\Users\\\\SYNTHE~1\\\\m.onnx'", "at '~\\\\m.onnx'"),
    ("at c:\\users\\synthe~1\\f", "at ~\\f"),
    ("home is C:\\Users\\SYNTHE~1", "home is ~"),
    ('quoted "C:\\Users\\SYNTHE~1"', 'quoted "~"'),
)
SHORT_KEPT = (
    "at C:\\Users\\SYNTHE~10\\a",
    "at xC:\\Users\\SYNTHE~1\\a",
)


def test_ac_148_2_short_form_becomes_tilde(monkeypatch: pytest.MonkeyPatch) -> None:
    _short_ready(monkeypatch)
    want = [(text, tilde) for text, tilde in SHORT_TO_TILDE] + [(t, t) for t in SHORT_KEPT]
    inputs = [text for text, _tilde in want]
    assert [(text, health.console_field(text)) for text in inputs] == want
    assert [(text, health.scrub_home(text)) for text in inputs] == want


def test_ac_148_3_lookup_runs_once_per_home(monkeypatch: pytest.MonkeyPatch) -> None:
    line = "at C:\\Users\\SYNTHE~1\\a"
    fake = _short_ready(monkeypatch)
    for _ in range(3):
        health.console_field(line)
        health.scrub_home(line)
        scrub_line(line)
    assert fake.calls == [SYNTHETIC_HOME]

    empty = _short_ready(monkeypatch, short="")
    for _ in range(3):
        health.console_field(line)
        health.scrub_home(line)
        scrub_line(line)
    assert empty.calls == [SYNTHETIC_HOME]

    monkeypatch.setattr(health, "home_folder", lambda: OTHER_HOME)
    for _ in range(3):
        health.console_field(line)
        scrub_line(line)
    assert empty.calls == [SYNTHETIC_HOME, OTHER_HOME]


CORPUS = (
    "at C:\\Users\\SYNTHETIC_HOME_USER\\.avkit\\m.onnx",
    "at C:/Users/SYNTHETIC_HOME_USER/f",
    "at C:\\Users\\SYNTHE~1\\f",
    "home is C:\\Users\\SYNTHETIC_HOME_USER",
    "at C:\\Users\\Public\\f",
)
LONG_ONLY = (
    "at ~\\.avkit\\m.onnx",
    "at ~/f",
    "at C:\\Users\\SYNTHE~1\\f",
    "home is ~",
    "at C:\\Users\\Public\\f",
)


@pytest.mark.parametrize(
    "answer", ["", SYNTHETIC_HOME.lower()], ids=["failed-lookup", "long-form-other-case"]
)
def test_ac_148_4_no_short_form_matches_only_the_long_form(
    monkeypatch: pytest.MonkeyPatch, answer: str
) -> None:
    fake = _short_ready(monkeypatch, short=answer)
    assert tuple(health.scrub_home(line) for line in CORPUS) == LONG_ONLY
    assert health.home_forms() == (SYNTHETIC_HOME,)
    assert fake.calls == [SYNTHETIC_HOME]


def test_ac_148_5_no_lookup_when_the_flag_is_false(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _short_ready(monkeypatch, lookup=False)
    assert health.scrub_home("at C:\\Users\\SYNTHE~1\\f") == "at C:\\Users\\SYNTHE~1\\f"
    assert health.scrub_home("at C:\\Users\\SYNTHETIC_HOME_USER\\f") == "at ~\\f"
    assert health.home_forms() == (SYNTHETIC_HOME,)
    assert fake.calls == []


def test_ac_148_6_one_line_with_both_forms(monkeypatch: pytest.MonkeyPatch) -> None:
    _short_ready(monkeypatch)
    line = "copy C:\\Users\\SYNTHETIC_HOME_USER\\a to C:\\Users\\SYNTHE~1\\b"
    assert health.scrub_home(line) == "copy ~\\a to ~\\b"
    assert health.console_field(line) == "copy ~\\a to ~\\b"


SPLIT_SHORT = (
    ("plain", "at C:\\Users\\SYNTHE~1\\v.mp4", "at C:\\Users\\SYNTHE~1\\v.mp4"),
    ("tab", "at C:\\Users\\SYN\tTHE~1\\v.mp4", "at C:\\Users\\SYN THE~1\\v.mp4"),
    ("control", "at C:\\Users\\SYN\x01THE~1\\v.mp4", "at C:\\Users\\SYNTHE~1\\v.mp4"),
    ("ansi", "at C:\\Users\\SYN\x1b[0mTHE~1\\v.mp4", "at C:\\Users\\SYNTHE~1\\v.mp4"),
)


@pytest.mark.parametrize(
    ("text", "kept"),
    [case[1:] for case in SPLIT_SHORT],
    ids=[case[0] for case in SPLIT_SHORT],
)
def test_ac_148_7_scrub_line_matches_a_split_short_form(
    monkeypatch: pytest.MonkeyPatch, text: str, kept: str
) -> None:
    _short_ready(monkeypatch)
    assert scrub_line(text) == "at ~\\v.mp4"
    _short_ready(monkeypatch, short="")
    assert scrub_line(text) == kept


def test_ac_148_8_real_helper_returns_the_filled_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    native = FakeNative(_fills_alias)
    _native_ready(monkeypatch, native)
    assert health.short_path_name(SYNTHETIC_HOME) == SYNTHETIC_SHORT
    assert native.calls == [
        (SYNTHETIC_HOME, True, 0),
        (SYNTHETIC_HOME, False, len(SYNTHETIC_SHORT) + 1),
    ]


def test_ac_148_8_real_helper_feeds_the_scrub(monkeypatch: pytest.MonkeyPatch) -> None:
    native = FakeNative(_fills_alias)
    _native_ready(monkeypatch, native)
    _scrub_ready(monkeypatch)
    assert health.home_forms() == (SYNTHETIC_HOME, SYNTHETIC_SHORT)
    assert health.console_field("at C:\\Users\\SYNTHE~1\\a") == "at ~\\a"
    assert len(native.calls) == 2


def _size_zero(_path: str, _buffer: Any, _size: int) -> int:
    return 0


def _fill_zero(_path: str, buffer: Any, _size: int) -> int:
    return len(SYNTHETIC_SHORT) + 1 if buffer is None else 0


def _fill_too_big(_path: str, buffer: Any, size: int) -> int:
    if buffer is None:
        return len(SYNTHETIC_SHORT) + 1
    buffer.value = SYNTHETIC_SHORT
    return size


def _raises(_path: str, _buffer: Any, _size: int) -> int:
    raise OSError("synthetic native failure")


FAILING = (
    ("size-query-zero", _size_zero, 1),
    ("fill-zero", _fill_zero, 2),
    ("fill-does-not-fit", _fill_too_big, 2),
    ("os-error", _raises, 1),
    ("no-api", None, 0),
)


@pytest.mark.parametrize(
    ("script", "calls"),
    [case[1:] for case in FAILING],
    ids=[case[0] for case in FAILING],
)
def test_ac_148_9_failed_native_lookup_gives_nothing(
    monkeypatch: pytest.MonkeyPatch, script: Script | None, calls: int
) -> None:
    native = FakeNative(script) if script is not None else None
    _native_ready(monkeypatch, native)
    assert health.short_path_name(SYNTHETIC_HOME) == ""
    _scrub_ready(monkeypatch)
    assert health.console_field("at C:\\Users\\SYNTHE~1\\a") == "at C:\\Users\\SYNTHE~1\\a"
    assert health.home_forms() == (SYNTHETIC_HOME,)
    if native is not None:
        assert len(native.calls) == calls * 2
