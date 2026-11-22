"""MEU-163 TRANSCRIPT_DEFAULTS (AC-163.10, Python half): Mat's transcript values are the defaults.

Mat 2026-11-21 (D-1355): the defaults are the settings he runs with.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

MATS_VALUES: dict[str, int] = {
    "requests_per_hour": 20,
    "delay_between_requests": 120,
    "max_retries": 1,
    "retry_delay": 7,
    "batch_size": 5,
    "pause_between_batches": 500,
    "playlist_end": 0,
    "max_words_per_document": 490000,
}


def test_ac_163_10_transcript_defaults_are_mats_values() -> None:
    from avkit_core.services.settings import SETTINGS_KEY_TABLE

    found = {key: SETTINGS_KEY_TABLE[("transcript", key)].default for key in MATS_VALUES}
    assert found == MATS_VALUES


def test_ac_163_10_unsaved_key_reads_the_default() -> None:
    from tests.unit.test_services import FakeUnitOfWork, SharedFakeFactory

    from avkit_core.services.settings import SettingsService

    settings = SettingsService(SharedFakeFactory(FakeUnitOfWork()))
    assert settings.get("transcript", "requests_per_hour") == 20
    settings.set("transcript", "requests_per_hour", 42)
    assert settings.get("transcript", "requests_per_hour") == 42
