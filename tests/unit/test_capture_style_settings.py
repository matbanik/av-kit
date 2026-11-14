"""MEU-105 STYLE_SETTINGS on the service (AC-105.1 Python half, AC-105.2, AC-105.3)."""

from __future__ import annotations

import dataclasses

import pytest

pytestmark = pytest.mark.unit

STYLE_DEFAULTS: dict[str, object] = {
    "arrow_color": "#E0AF68",
    "arrow_stroke": 3,
    "box_color": "#E0AF68",
    "box_stroke": 3,
    "highlight_color": "#E0AF68",
    "text_color": "#E0AF68",
    "text_font_size": 16,
    "text_bg_color": "",
    "pixelate_block_size": 10,
}
COLOR_LEAVES = ("arrow_color", "box_color", "highlight_color", "text_color")
BAD_COLORS = ("#12ABC", "12ABCD", "#12ABCDE", "red", "", "#12AB\uD800", "#12AB\u0007D", "#12ABCD\n")
BAD_STROKES: tuple[object, ...] = (3.5, 3.0, True, 0, 101, "3")
BAD_BLOCKS: tuple[object, ...] = (1, 101)


def _service():
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.settings import SettingsService

    return SettingsService(SharedFakeFactory(FakeUnitOfWork()))


def test_ac_105_1_setting_spec_fields() -> None:
    from avkit_core.services.settings import SettingSpec

    fields = {f.name: f for f in dataclasses.fields(SettingSpec)}
    assert fields["pattern"].type in ("str | None", str | None)
    assert fields["pattern"].default is None
    assert fields["integer"].type in ("bool", bool)
    assert fields["integer"].default is False


def test_ac_105_2_capture_rows_follow_annotated_format() -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE

    keys = [key for ns, key in SETTINGS_KEY_TABLE if ns == "capture"]
    after = keys[keys.index("annotated_format") + 1 :]
    assert after[: len(STYLE_DEFAULTS)] == list(STYLE_DEFAULTS)
    # LOCK_LEAF (Session 71b, MEU-143): tool_lock is the only key after the style leaves.
    assert after[len(STYLE_DEFAULTS) :] == ["tool_lock"]


@pytest.mark.parametrize("leaf", list(STYLE_DEFAULTS), ids=list(STYLE_DEFAULTS))
def test_ac_105_2_fresh_store_returns_default(leaf: str) -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE

    assert SETTINGS_KEY_TABLE[("capture", leaf)].default == STYLE_DEFAULTS[leaf]
    got = _service().get_namespace("capture")[leaf]
    assert got == STYLE_DEFAULTS[leaf]
    assert type(got) is type(STYLE_DEFAULTS[leaf])


def test_ac_105_2_stored_stroke_reads_back_as_int() -> None:
    service = _service()
    service.set_namespace("capture", {"arrow_stroke": 7, "text_bg_color": "#112233"})
    data = service.get_namespace("capture")
    assert data["arrow_stroke"] == 7 and type(data["arrow_stroke"]) is int
    assert data["text_bg_color"] == "#112233"


@pytest.mark.parametrize("leaf", COLOR_LEAVES, ids=list(COLOR_LEAVES))
@pytest.mark.parametrize("value", BAD_COLORS, ids=[f"bad{i}" for i in range(len(BAD_COLORS))])
def test_ac_105_3_colour_refused(leaf: str, value: str) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    with pytest.raises(ValidationError) as caught:
        _encode(SETTINGS_KEY_TABLE[("capture", leaf)], leaf, value)
    assert leaf in str(caught.value)
    if value:
        assert value not in str(caught.value)


@pytest.mark.parametrize("value", ["#12abcd", "#12ABCD"], ids=["lower", "upper"])
def test_ac_105_3_colour_accepted(value: str) -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    assert _encode(SETTINGS_KEY_TABLE[("capture", "arrow_color")], "arrow_color", value) == value


def test_ac_105_3_empty_text_bg_accepted() -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    spec = SETTINGS_KEY_TABLE[("capture", "text_bg_color")]
    assert _encode(spec, "text_bg_color", "") == ""
    assert _encode(spec, "text_bg_color", "#00ff00") == "#00ff00"
    with pytest.raises(ValidationError):
        _encode(spec, "text_bg_color", "#00ff0")


@pytest.mark.parametrize("value", BAD_STROKES, ids=[repr(v) for v in BAD_STROKES])
def test_ac_105_3_stroke_refused(value: object) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    with pytest.raises(ValidationError) as caught:
        _encode(SETTINGS_KEY_TABLE[("capture", "arrow_stroke")], "arrow_stroke", value)
    assert "arrow_stroke" in str(caught.value)
    assert repr(value) not in str(caught.value)


@pytest.mark.parametrize("value", BAD_BLOCKS, ids=[repr(v) for v in BAD_BLOCKS])
def test_ac_105_3_block_size_refused(value: int) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    with pytest.raises(ValidationError):
        spec = SETTINGS_KEY_TABLE[("capture", "pixelate_block_size")]
        _encode(spec, "pixelate_block_size", value)


def test_ac_105_3_range_edges_accepted() -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    table = SETTINGS_KEY_TABLE
    assert _encode(table[("capture", "arrow_stroke")], "arrow_stroke", 1) == "1"
    assert _encode(table[("capture", "arrow_stroke")], "arrow_stroke", 100) == "100"
    assert _encode(table[("capture", "text_font_size")], "text_font_size", 400) == "400"
    assert _encode(table[("capture", "pixelate_block_size")], "pixelate_block_size", 2) == "2"


@pytest.mark.parametrize("sign", [1, -1], ids=["pos", "neg"])
def test_ac_105_3_huge_int_is_validation_error(sign: int) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    with pytest.raises(ValidationError) as caught:
        _encode(SETTINGS_KEY_TABLE[("capture", "arrow_stroke")], "arrow_stroke", sign * 10**400)
    assert "out of range" in str(caught.value)


def test_ac_105_3_rows_without_integer_keep_floats() -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    assert _encode(SETTINGS_KEY_TABLE[("tts", "speed")], "speed", 1.5) == "1.5"
    assert _encode(SETTINGS_KEY_TABLE[("transcript", "max_retries")], "max_retries", 3.0) == "3"
