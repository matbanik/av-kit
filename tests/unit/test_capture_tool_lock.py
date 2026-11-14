"""MEU-143 LOCK_LEAF and LOCK_DECODE on the service (AC-143.1 Python half, AC-143.2, AC-143.3)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

pytestmark = pytest.mark.unit

# LOCK_DECODE: a stored boolean reads True only when it is exactly "true".
STORED_FALSE: dict[str, str] = {
    "empty": "",
    "control": "\x07",
    "lone_surrogate": "\ud800",
    "upper_true": "TRUE",
    "one": "1",
}
REFUSED: tuple[object, ...] = ("false", 0, 1, None)


def _service():
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.settings import SettingsService

    uow = FakeUnitOfWork()
    return SettingsService(SharedFakeFactory(uow)), uow


def _store_raw(uow, value: str) -> None:
    from avkit_core.domain.settings import Setting
    from avkit_core.services.settings import _kind_to_enum

    uow.settings.set(
        Setting(
            namespace="capture",
            key="tool_lock",
            value=value,
            value_type=_kind_to_enum("boolean"),
            updated_at=datetime.now(UTC),
        )
    )


def test_ac_143_1_settings_put_field_is_strict_bool() -> None:
    from pydantic import StrictBool

    from avkit_api.schemas.settings import SettingsPutIn

    fields = list(SettingsPutIn.model_fields)
    assert fields[fields.index("pixelate_block_size") + 1] == "tool_lock"
    field = SettingsPutIn.model_fields["tool_lock"]
    assert field.annotation == StrictBool | None
    assert field.default is None


def test_ac_143_2_tool_lock_row_follows_pixelate() -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, SettingSpec

    keys = [key for ns, key in SETTINGS_KEY_TABLE if ns == "capture"]
    assert keys[keys.index("pixelate_block_size") + 1 :] == ["tool_lock"]
    assert SETTINGS_KEY_TABLE[("capture", "tool_lock")] == SettingSpec("boolean", True)


def test_ac_143_2_fresh_store_reads_bool_true() -> None:
    service, _uow = _service()
    got = service.get_namespace("capture")["tool_lock"]
    assert got is True


def test_ac_143_3_false_stores_text_false_and_reads_false() -> None:
    service, uow = _service()
    service.set_namespace("capture", {"tool_lock": False})
    stored = uow.settings.get("capture", "tool_lock")
    assert stored is not None and stored.value == "false"
    assert service.get_namespace("capture")["tool_lock"] is False


@pytest.mark.parametrize("raw", list(STORED_FALSE.values()), ids=list(STORED_FALSE))
def test_ac_143_3_stored_text_reads_false(raw: str) -> None:
    service, uow = _service()
    _store_raw(uow, raw)
    assert service.get("capture", "tool_lock") is False
    assert service.get_namespace("capture")["tool_lock"] is False


def test_ac_143_3_stored_true_reads_true() -> None:
    service, uow = _service()
    _store_raw(uow, "true")
    assert service.get("capture", "tool_lock") is True


@pytest.mark.parametrize("value", REFUSED, ids=[repr(v) for v in REFUSED])
def test_ac_143_3_encode_refuses_non_bool(value: object) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_core.services.settings import SETTINGS_KEY_TABLE, _encode

    with pytest.raises(ValidationError) as caught:
        _encode(SETTINGS_KEY_TABLE[("capture", "tool_lock")], "tool_lock", value)
    message = str(caught.value)
    assert "tool_lock" in message
    assert repr(value) not in message
    if isinstance(value, str):
        assert value not in message
