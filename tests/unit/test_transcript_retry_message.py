"""rc.3 F6: a blocked video's retries show on the Processing card instead of a silent wait.

Mat's rc.3 retest: Transcript "seems stuck and not processing any transcripts" while YouTube
refused the network; ruling "Show retries on card (Recommended)".
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from tests.unit.test_services import _join, _set_ids, _transcript_stack

from avkit_core.domain.enums import TranscriptStatus

URL = "https://youtube.com/@blocked"


def test_retry_message_text() -> None:
    from avkit_core.domain.transcript import retry_message

    lead = "YouTube is blocking caption requests from this network. "
    assert retry_message(1, 3, 30.0) == lead + "Attempt 1 of 3 was refused; trying again in 30 s."
    assert retry_message(3, 3, 30.0) == lead + "Attempt 3 of 3 was refused; pausing in 30 s."
    assert retry_message(1, 1, 2.5) == lead + "Attempt 1 of 1 was refused; pausing in 2.5 s."


def _stack(tmp_path: Path, refusals: int):
    seen: list[str | None] = []
    holder: dict[str, str] = {}

    def sleep(seconds: float) -> None:
        if seconds == 30:
            seen.append(uow.transcripts.get_job(holder["id"]).error_message)

    service, settings, yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path, sleep=sleep)
    _set_ids(yt, ["first", "second"])
    settings.set("transcript", "max_retries", 3)
    settings.set("transcript", "retry_delay", 30)
    settings.set("transcript", "delay_between_requests", 0)
    captions.retryable_left = refusals
    job = service.add_channel(URL)
    holder["id"] = job.id
    return service, uow, job, seen


def test_each_retry_shows_on_the_job_then_clears(tmp_path: Path) -> None:
    from avkit_core.domain.transcript import retry_message

    service, uow, job, seen = _stack(tmp_path, refusals=2)
    service.start_processing()
    _join(service)
    assert seen == [retry_message(1, 3, 30.0), retry_message(2, 3, 30.0)]
    parent = uow.transcripts.get_job(job.id)
    assert (parent.status, parent.error_message) == (TranscriptStatus.Done, None)


def test_an_exhausted_block_ends_on_the_pause_message(tmp_path: Path) -> None:
    from avkit_core.domain.transcript import (
        TranscriptFailureCause,
        failure_message,
        retry_message,
    )

    service, uow, job, seen = _stack(tmp_path, refusals=10**6)
    service.start_processing()
    _join(service)
    assert seen == [retry_message(n, 3, 30.0) for n in (1, 2, 3)]
    parent = uow.transcripts.get_job(job.id)
    blocked = failure_message(TranscriptFailureCause.blocked)
    assert (parent.status, parent.error_message) == (TranscriptStatus.Paused, blocked)


def test_a_run_clears_an_old_job_message(tmp_path: Path) -> None:
    service, settings, _yt, uow, _fs, captions, _sleeps = _transcript_stack(tmp_path)
    settings.set("transcript", "delay_between_requests", 0)
    job = service.add_channel(URL)
    uow.transcripts.save_job(replace(job, error_message="Skipped 1 video earlier."))
    captions.hold = True
    service.start_processing()
    assert captions.entered.wait(timeout=2)
    running = uow.transcripts.get_job(job.id)
    assert (running.status, running.error_message) == (TranscriptStatus.Processing, None)
    captions.release.set()
    _join(service)
