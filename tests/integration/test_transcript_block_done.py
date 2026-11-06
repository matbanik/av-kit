"""MEU-116 done test (AC-116.7): a block pauses the job, and its reason reaches every surface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from tests.integration.test_transcript_failure_delivery import _console_text, _run
from tests.unit.test_services import FakeCaptions


@pytest.mark.integration
def test_ac_116_7_blocked_job_reads_paused_with_its_reason_everywhere(tmp_path: Path) -> None:
    from avkit_api.routes.transcripts import _job_out
    from avkit_core.domain.transcript import TranscriptFailureCause, failure_message

    blocked = failure_message(TranscriptFailureCause.blocked)
    captions = FakeCaptions()
    captions.retryable_left = 10**6
    service, health, job = _run(tmp_path, ["first", "second"], captions)
    out = _job_out(service, service.get_job(job.id)).model_dump()
    assert (out["status"], out["error_message"]) == ("Paused", blocked)
    lines = [
        event
        for event in health.console_snapshot(0)
        if event.message.startswith("transcript.blocked")
    ]
    assert [(event.level, blocked in event.message) for event in lines] == [("ERROR", True)]
    filed = [json.loads(line)["message"] for line in _console_text(tmp_path / "app").splitlines()]
    assert lines[0].message in filed
