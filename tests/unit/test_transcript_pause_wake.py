"""MEU-155 (Session 88, D-1090 C): a Transcript pause or stop ends the service's own wait.

AC-155.16 to AC-155.18. The service is built like `_transcript_stack`
(`tests/unit/test_services.py`) from that module's fakes, but with no injected `sleep`, so the
service's own wait runs. The sync point wraps the instance attribute `_sleep` (it exists today,
`transcript.py:107`): the wrapper sets an event when it is called with the target duration and
then calls the original, so the worker is entering the target wait when the test pauses.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from pathlib import Path

import pytest
from tests.unit.test_services import (
    DownloadYouTube,
    FakeCaptions,
    FakeFilesystem,
    FakeUnitOfWork,
    SharedFakeFactory,
)

from avkit_core.domain.download import PlaylistInfo
from avkit_core.domain.enums import QueueProcessorState, TranscriptStatus
from avkit_core.services.extract import ExtractCoordinator
from avkit_core.services.settings import SettingsService
from avkit_core.services.transcript import TranscriptService

#: How long a pause or stop may take to land once the worker is in a wait.
LAND_WITHIN = 2.0


def _service(
    tmp_path: Path, settings_values: dict[str, int]
) -> tuple[TranscriptService, FakeUnitOfWork, FakeCaptions]:
    uow = FakeUnitOfWork()
    factory = SharedFakeFactory(uow)
    settings = SettingsService(factory)
    settings.set("transcript", "output_dir", str(tmp_path))
    for key, value in settings_values.items():
        settings.set("transcript", key, value)
    yt = DownloadYouTube()
    yt.ids = ["v1", "v2"]
    yt.playlist = PlaylistInfo(playlist_id="ch", title="My Channel", video_ids=list(yt.ids))
    captions = FakeCaptions()
    # No `sleep`: the service's own wait runs.
    service = TranscriptService(
        factory,
        coordinator=ExtractCoordinator(yt),
        captions=captions,
        filesystem=FakeFilesystem(),
        settings=settings,
    )
    return service, uow, captions


def _sync_on(service: TranscriptService, target: float) -> threading.Event:
    """Wrap the service's wait; the event is set when it is called with TARGET seconds."""
    reached = threading.Event()
    original: Callable[[float], None] = getattr(service, "_sleep")

    def wrapper(seconds: float) -> None:
        if seconds == target:
            reached.set()
        original(seconds)

    setattr(service, "_sleep", wrapper)
    return reached


def _within(seconds: float, check: Callable[[], bool]) -> bool:
    deadline = time.monotonic() + seconds
    while True:
        if check():
            return True
        if time.monotonic() >= deadline:
            return False
        time.sleep(0.02)


#: (case id, settings, the wait to pause in, retryable calls before a result)
WAIT_CASES = [
    ("delay", {"delay_between_requests": 30}, 30.0, 0),
    (
        "batch_pause",
        {"delay_between_requests": 0, "batch_size": 1, "pause_between_batches": 300},
        300.0,
        0,
    ),
    ("retry_delay", {"delay_between_requests": 0, "retry_delay": 30, "max_retries": 3}, 30.0, 1),
]


@pytest.mark.parametrize(
    ("settings_values", "target", "retryable"),
    [case[1:] for case in WAIT_CASES],
    ids=[case[0] for case in WAIT_CASES],
)
def test_ac_155_16_pause_during_each_wait_lands_within_two_seconds(
    tmp_path: Path, settings_values: dict[str, int], target: float, retryable: int
) -> None:
    service, uow, captions = _service(tmp_path, settings_values)
    captions.retryable_left = retryable
    job = service.add_channel("https://youtube.com/@example")
    reached = _sync_on(service, target)
    service.start_processing()
    assert reached.wait(10), f"the worker never entered the {target} s wait"
    service.pause_processing()

    def paused() -> bool:
        return (
            service.get_processor_state().state is QueueProcessorState.Paused
            and uow.transcripts.get_job(job.id).status is TranscriptStatus.Paused
        )

    landed = _within(LAND_WITHIN, paused)
    state = service.get_processor_state().state
    status = uow.transcripts.get_job(job.id).status
    assert landed, (
        f"{LAND_WITHIN} s after pause_processing() in the {target} s wait: processor {state}, "
        f"job {status}"
    )
    assert len(captions.fetch_calls) == 1


def test_ac_155_17_stop_during_delay_wait_lands_within_two_seconds(tmp_path: Path) -> None:
    service, uow, captions = _service(tmp_path, {"delay_between_requests": 30})
    job = service.add_channel("https://youtube.com/@example")
    reached = _sync_on(service, 30.0)
    service.start_processing()
    assert reached.wait(10), "the worker never entered the 30 s wait"
    service.stop_processing()

    def stopped() -> bool:
        return (
            service.get_processor_state().state is QueueProcessorState.Idle
            and uow.transcripts.get_job(job.id).status is TranscriptStatus.Cancelled
        )

    landed = _within(LAND_WITHIN, stopped)
    state = service.get_processor_state().state
    status = uow.transcripts.get_job(job.id).status
    assert landed, (
        f"{LAND_WITHIN} s after stop_processing() in the 30 s wait: processor {state}, job {status}"
    )
    assert len(captions.fetch_calls) == 1


def test_ac_155_18_wait_ends_early_after_pause(tmp_path: Path) -> None:
    service, _uow, _captions = _service(tmp_path, {})
    wait: Callable[[float], None] = getattr(service, "_sleep")

    started = time.monotonic()
    wait(0.3)
    assert time.monotonic() - started >= 0.29

    service.pause_processing()
    started = time.monotonic()
    wait(2)
    took = time.monotonic() - started
    assert took < 0.5, f"wait(2) after pause_processing() took {took:.2f} s"

    service.start_processing()
    started = time.monotonic()
    wait(0.3)
    assert time.monotonic() - started >= 0.29
