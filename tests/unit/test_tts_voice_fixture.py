"""VOICE_CATALOG_FIXTURE parity (Session 27, MEU-64 AC-64.6).

The Electron AC-64.6 spec serves `ui/tests/e2e/fixtures/tts-voices.json` so its layout
measurement sees the production voice catalog. This test fails if the fixture drifts
from `avkit_infra.tts.voices.list_voice_configs()` (the `GET /tts/voices` source).
"""

from __future__ import annotations

import json
from pathlib import Path

from avkit_infra.tts.voices import VOICE_COUNT, list_voice_configs

FIXTURE = (
    Path(__file__).resolve().parents[2] / "ui" / "tests" / "e2e" / "fixtures" / "tts-voices.json"
)


def test_ac_64_6_voice_fixture_matches_production_catalog() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    expected = [
        {
            "voice_id": voice.voice_id,
            "language": voice.language,
            "gender": voice.gender,
            "style_description": voice.style_description,
            "available": True,
            "reason": None,
        }
        for voice in list_voice_configs()
    ]
    assert payload == {"items": expected}
    assert len(payload["items"]) == VOICE_COUNT
