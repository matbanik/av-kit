"""rc.3 F7: an MP3 job leaves only the MP3; the WAV it was encoded from is removed.

Mat, 2026-11-09: "wav and mp3 are being created even though only mp3 is selected".
`_inspiration/_tts_pseudo_logic.md:181`: "Delete temp WAV after conversion".
"""

from __future__ import annotations

from pathlib import Path

import pytest
from structlog.testing import capture_logs
from tests.unit.test_tts_async import _require, _Stack

from avkit_core.domain.enums import MediaFormat, TTSStatus

WAIT = 5.0


def _run(stack: _Stack, fmt: MediaFormat) -> str:
    job = stack.generate(text="Hello there friend", fmt=fmt)
    assert stack.service.wait_idle(WAIT) is True
    assert stack.status(job.id) is TTSStatus.Done
    return job.id


def test_mp3_job_leaves_only_the_mp3(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    job_id = _run(stack, MediaFormat.MP3)
    assert stack.files(job_id) == ["hello-there-friend-am_eric.mp3"]
    assert stack.service.get_status(job_id).output_path == (
        stack.root / "hello-there-friend-am_eric.mp3"
    )


def test_wav_job_keeps_its_wav(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    job_id = _run(stack, MediaFormat.WAV)
    assert stack.files(job_id) == ["hello-there-friend-am_eric.wav"]


def test_a_wav_that_cannot_be_removed_still_ends_done_and_is_logged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require()
    stack = _Stack(tmp_path)
    real_unlink = Path.unlink

    def locked(self: Path, missing_ok: bool = False) -> None:
        if self.suffix == ".wav":
            raise PermissionError("in use")
        real_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(Path, "unlink", locked)
    with capture_logs() as logs:
        job_id = _run(stack, MediaFormat.MP3)
    assert "hello-there-friend-am_eric.mp3" in stack.files(job_id)
    assert any(entry["event"] == "tts.cleanup_failed" for entry in logs)
