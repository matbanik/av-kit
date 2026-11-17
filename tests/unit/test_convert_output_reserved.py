"""MEU-152 amendment A1 (Session 81, D-1060): a new Convert job never gets a name still in use.

QUEUE_OUTPUT_RESERVED: a stored Pending, Processing, Failed or Cancelled job holds its output
name against a later Add, and a row with a probe error never takes the skip alias (D-1061,
D-1062, D-1064). QUEUE_ADD_SERIAL: two Adds at once never read the same queue (D-1061).
ACTIVE_WRITER_RESERVED: a removed or cleared job's name stays held until its media call exits
(D-1065). Product imports stay inside the tests so collection cannot ERROR.
"""

from __future__ import annotations

import threading
import time
from dataclasses import replace
from pathlib import Path

import pytest
from tests.unit.test_conversion_service import (
    RecordingMedia,
    _process,
    _stack,
    _write_clip,
)


def _cut() -> object:
    from avkit_core.domain.enums import ConversionKind, CutCopyMode
    from avkit_core.services.conversion import ConversionAddSpec

    return ConversionAddSpec(
        kind=ConversionKind.Cut, in_ms=500, out_ms=1500, copy_mode=CutCopyMode.FastCopy
    )


def _compress() -> object:
    from avkit_core.domain.enums import ConversionKind
    from avkit_core.services.conversion import ConversionAddSpec

    return ConversionAddSpec(kind=ConversionKind.Compress)


def _add(service: object, clip: Path, spec: object) -> object:
    jobs = service.add_to_queue([clip], spec)  # type: ignore[attr-defined]
    assert len(jobs) == 1
    return jobs[0]


def _set_status(uow: object, job: object, status: object) -> None:
    stored = uow.conversion_jobs.get(job.id)  # type: ignore[attr-defined]
    uow.conversion_jobs.save(replace(stored, status=status))  # type: ignore[attr-defined]
    uow.commit()  # type: ignore[attr-defined]


def _join(service: object) -> bool:
    thread = service._thread  # type: ignore[attr-defined]
    if thread is not None:
        thread.join(timeout=10)
        return not thread.is_alive()
    return True


def _sqlite_service(tmp_path: Path, skip: bool) -> object:
    from avkit_core.services.conversion import ConversionService
    from avkit_core.services.settings import SettingsService
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    engine = create_sqlite_engine(tmp_path / "avkit.db")
    init_schema(engine)
    session_factory = create_session_factory(engine)

    def factory() -> SqlAlchemyUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

    settings = SettingsService(factory)
    settings.set("converter", "output_dir", str(tmp_path))
    settings.set("converter", "skip_existing", skip)
    return ConversionService(factory, media=RecordingMedia(), settings=settings)


class BarrierMedia(RecordingMedia):
    """Both Adds meet in ``probe``, after each has read the queue (AC-152.16)."""

    def __init__(self) -> None:
        super().__init__()
        self.barrier = threading.Barrier(2, timeout=2)

    def probe(self, file_path: Path):  # type: ignore[no-untyped-def]
        try:
            self.barrier.wait()
        except threading.BrokenBarrierError:
            pass
        return super().probe(file_path)


class GateMedia(RecordingMedia):
    """A media call that writes bytes naming its call and waits on ``gate`` or ``should_stop``.

    With ``partial`` it writes a partial file before the wait, as FFmpeg creates its output
    early (AC-152.18); without it the file appears only after the wait (AC-152.19, AC-152.20).
    """

    def __init__(self, *, partial: bool = False) -> None:
        super().__init__()
        self.gate = threading.Event()
        self.partial = partial
        self.calls = 0

    def encode(
        self,
        input_path: Path,
        output_path: Path,
        options: object,
        on_progress: object,
        should_stop: object,
    ) -> None:
        self.calls += 1
        tag = f"call {self.calls}".encode()
        if self.partial:
            output_path.write_bytes(b"partial " + tag)
        self.started.set()
        deadline = time.monotonic() + 10
        while not self.gate.is_set() and time.monotonic() < deadline:
            if should_stop():  # type: ignore[operator]
                return
            time.sleep(0.01)
        output_path.write_bytes(tag)


@pytest.mark.parametrize(
    ("ac_id", "skip"),
    [("AC-152.13", False), ("AC-152.13", True)],
    ids=["AC-152.13-skip-off", "AC-152.13-skip-on"],
)
@pytest.mark.unit
def test_ac_152_13_separate_adds_get_distinct_names(ac_id: str, skip: bool, tmp_path: Path) -> None:
    assert ac_id == "AC-152.13"
    from avkit_core.domain.enums import ConversionStatus

    service, _uow, _media, settings = _stack(tmp_path)
    settings.set("converter", "skip_existing", skip)
    clip = _write_clip(tmp_path)
    cuts = [_add(service, clip, _cut()) for _ in range(3)]
    compresses = [_add(service, clip, _compress()) for _ in range(2)]
    assert [job.output_path.name for job in cuts] == [  # type: ignore[attr-defined]
        "clip_cut.mp4",
        "clip_cut_1.mp4",
        "clip_cut_2.mp4",
    ]
    assert [job.output_path.name for job in compresses] == [  # type: ignore[attr-defined]
        "clip_compress.mp4",
        "clip_compress_1.mp4",
    ]
    assert {job.status for job in cuts + compresses} == {  # type: ignore[attr-defined]
        ConversionStatus.Pending
    }


@pytest.mark.parametrize(
    ("ac_id", "skip"),
    [("AC-152.13", False), ("AC-152.13", True)],
    ids=["AC-152.13-sqlite-skip-off", "AC-152.13-sqlite-skip-on"],
)
@pytest.mark.unit
def test_ac_152_13_separate_adds_distinct_on_sqlite(ac_id: str, skip: bool, tmp_path: Path) -> None:
    assert ac_id == "AC-152.13"
    from avkit_core.domain.enums import ConversionStatus

    service = _sqlite_service(tmp_path, skip)
    clip = _write_clip(tmp_path)
    for _ in range(3):
        _add(service, clip, _cut())
    stored = service.get_queue()  # type: ignore[attr-defined]
    assert [job.output_path.name for job in stored] == [
        "clip_cut.mp4",
        "clip_cut_1.mp4",
        "clip_cut_2.mp4",
    ]
    assert {job.status for job in stored} == {ConversionStatus.Pending}


@pytest.mark.parametrize(
    ("ac_id", "status_name"),
    [("AC-152.14", "Processing"), ("AC-152.14", "Failed"), ("AC-152.14", "Cancelled")],
    ids=["AC-152.14-processing", "AC-152.14-failed", "AC-152.14-cancelled"],
)
@pytest.mark.unit
def test_ac_152_14_unfinished_job_holds_its_name(
    ac_id: str, status_name: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-152.14"
    from avkit_core.domain.enums import ConversionStatus

    service, uow, _media, _settings = _stack(tmp_path)
    clip = _write_clip(tmp_path)
    first = _add(service, clip, _cut())
    _set_status(uow, first, ConversionStatus[status_name])
    assert not first.output_path.exists()  # type: ignore[attr-defined]
    later = _add(service, clip, _cut())
    assert later.output_path.name == "clip_cut_1.mp4"  # type: ignore[attr-defined]


@pytest.mark.parametrize("ac_id", ["AC-152.14"], ids=["AC-152.14-reset-failed"])
@pytest.mark.unit
def test_ac_152_14_reset_failed_keeps_distinct_paths(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.14"
    from avkit_core.domain.enums import ConversionStatus

    service, uow, _media, _settings = _stack(tmp_path)
    clip = _write_clip(tmp_path)
    first = _add(service, clip, _cut())
    _set_status(uow, first, ConversionStatus.Failed)
    later = _add(service, clip, _cut())
    reset = service.reset_failed(first.id)  # type: ignore[attr-defined]
    assert reset.status is ConversionStatus.Pending
    assert reset.output_path == first.output_path  # type: ignore[attr-defined]
    assert later.output_path != reset.output_path  # type: ignore[attr-defined]
    assert later.output_path.name == "clip_cut_1.mp4"  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("ac_id", "case"),
    [
        ("AC-152.15", "remove"),
        ("AC-152.15", "clear"),
        ("AC-152.15", "done-file-deleted"),
        ("AC-152.15", "done-file-skip-on"),
        ("AC-152.15", "done-file-skip-off"),
    ],
    ids=[
        "AC-152.15-remove",
        "AC-152.15-clear",
        "AC-152.15-done-file-deleted",
        "AC-152.15-done-file-skip-on",
        "AC-152.15-done-file-skip-off",
    ],
)
@pytest.mark.unit
def test_ac_152_15_released_names_guard(ac_id: str, case: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.15"
    from avkit_core.domain.enums import ConversionStatus

    service, uow, _media, settings = _stack(tmp_path)
    clip = _write_clip(tmp_path)
    first = _add(service, clip, _cut())
    out = first.output_path  # type: ignore[attr-defined]
    if case == "remove":
        service.remove(first.id)  # type: ignore[attr-defined]
    elif case == "clear":
        service.clear_queue()  # type: ignore[attr-defined]
    else:
        _set_status(uow, first, ConversionStatus.Done)
        out.write_bytes(b"done")
        if case == "done-file-deleted":
            out.unlink()
        settings.set("converter", "skip_existing", case == "done-file-skip-on")
    later = _add(service, clip, _cut())
    expected = {
        "remove": ("clip_cut.mp4", ConversionStatus.Pending),
        "clear": ("clip_cut.mp4", ConversionStatus.Pending),
        "done-file-deleted": ("clip_cut.mp4", ConversionStatus.Pending),
        "done-file-skip-on": ("clip_cut.mp4", ConversionStatus.Skipped),
        "done-file-skip-off": ("clip_cut_1.mp4", ConversionStatus.Pending),
    }[case]
    assert (later.output_path.name, later.status) == expected  # type: ignore[attr-defined]


@pytest.mark.parametrize("ac_id", ["AC-152.16"], ids=["AC-152.16-two-threads"])
@pytest.mark.unit
def test_ac_152_16_simultaneous_adds_get_distinct_names(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.16"
    service, _uow, _media, _settings = _stack(tmp_path, BarrierMedia())
    clip = _write_clip(tmp_path)
    results: list[object] = []
    errors: list[BaseException] = []

    def run() -> None:
        try:
            results.extend(service.add_to_queue([clip], _cut()))
        except BaseException as exc:  # recorded, then asserted below
            errors.append(exc)

    threads = [threading.Thread(target=run, daemon=True) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)
    assert [thread.is_alive() for thread in threads] == [False, False]
    assert errors == []
    assert len(results) == 2
    assert sorted(job.output_path.name for job in results) == [  # type: ignore[attr-defined]
        "clip_cut.mp4",
        "clip_cut_1.mp4",
    ]


@pytest.mark.parametrize("ac_id", ["AC-152.18"], ids=["AC-152.18-probe-fail-beside-running"])
@pytest.mark.unit
def test_ac_152_18_failed_add_beside_running_job(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.18"
    from avkit_core.domain.enums import ConversionStatus

    media = GateMedia(partial=True)
    service, _uow, _media, settings = _stack(tmp_path, media)
    settings.set("converter", "skip_existing", True)
    clip = _write_clip(tmp_path)
    first = _add(service, clip, _cut())
    service.start_processing()  # type: ignore[attr-defined]
    try:
        assert media.started.wait(timeout=5)
        assert first.output_path.read_bytes() == b"partial call 1"  # type: ignore[attr-defined]
        media.fail_probe = clip
        failed = _add(service, clip, _cut())
        media.fail_probe = None
        assert failed.status is ConversionStatus.Failed  # type: ignore[attr-defined]
        assert failed.error_message  # type: ignore[attr-defined]
        assert failed.output_path.name == "clip_cut_1.mp4"  # type: ignore[attr-defined]
    finally:
        media.gate.set()
        stopped = _join(service)
    assert stopped
    assert service.get_job(first.id).status is ConversionStatus.Done  # type: ignore[attr-defined]
    retried = service.reset_failed(failed.id)  # type: ignore[attr-defined]
    assert retried.output_path == failed.output_path  # type: ignore[attr-defined]
    _process(service)
    assert service.get_job(failed.id).status is ConversionStatus.Done  # type: ignore[attr-defined]
    assert first.output_path.read_bytes() == b"call 1"  # type: ignore[attr-defined]
    assert failed.output_path.read_bytes() == b"call 2"  # type: ignore[attr-defined]


@pytest.mark.parametrize("ac_id", ["AC-152.18"], ids=["AC-152.18-probe-fail-beside-done-file"])
@pytest.mark.unit
def test_ac_152_18_failed_add_beside_done_file(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.18"
    from avkit_core.domain.enums import ConversionStatus

    service, uow, media, settings = _stack(tmp_path)
    settings.set("converter", "skip_existing", True)
    clip = _write_clip(tmp_path)
    first = _add(service, clip, _cut())
    _set_status(uow, first, ConversionStatus.Done)
    first.output_path.write_bytes(b"done")  # type: ignore[attr-defined]
    media.fail_probe = clip
    failed = _add(service, clip, _cut())
    assert failed.status is ConversionStatus.Failed  # type: ignore[attr-defined]
    assert failed.error_message  # type: ignore[attr-defined]
    assert failed.output_path.name == "clip_cut_1.mp4"  # type: ignore[attr-defined]
    assert not failed.output_path.exists()  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("ac_id", "how"),
    [("AC-152.19", "remove"), ("AC-152.19", "clear")],
    ids=["AC-152.19-remove", "AC-152.19-clear"],
)
@pytest.mark.unit
def test_ac_152_19_removed_running_job_keeps_its_name(ac_id: str, how: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.19"
    from avkit_core.domain.enums import ConversionStatus

    media = GateMedia()
    service, _uow, _media, _settings = _stack(tmp_path, media)
    clip = _write_clip(tmp_path)
    first = _add(service, clip, _cut())
    service.start_processing()  # type: ignore[attr-defined]
    try:
        assert media.started.wait(timeout=5)
        assert not first.output_path.exists()  # type: ignore[attr-defined]
        if how == "remove":
            service.remove(first.id)  # type: ignore[attr-defined]
        else:
            service.clear_queue()  # type: ignore[attr-defined]
        later = _add(service, clip, _cut())
        assert later.output_path.name == "clip_cut_1.mp4"  # type: ignore[attr-defined]
    finally:
        media.gate.set()
        stopped = _join(service)
    assert stopped
    assert media.calls == 2
    assert service.get_job(later.id).status is ConversionStatus.Done  # type: ignore[attr-defined]
    assert first.output_path.read_bytes() == b"call 1"  # type: ignore[attr-defined]
    assert later.output_path.read_bytes() == b"call 2"  # type: ignore[attr-defined]


@pytest.mark.parametrize("ac_id", ["AC-152.20"], ids=["AC-152.20-release-on-exit"])
@pytest.mark.unit
def test_ac_152_20_running_name_freed_when_call_exits(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-152.20"
    from avkit_core.domain.enums import ConversionStatus

    media = GateMedia()
    service, _uow, _media, _settings = _stack(tmp_path, media)
    clip = _write_clip(tmp_path)
    other = _write_clip(tmp_path, "other.mp4")
    first = _add(service, clip, _cut())
    service.start_processing()  # type: ignore[attr-defined]
    try:
        assert media.started.wait(timeout=5)
        waiting = _add(service, other, _cut())
        service.remove(waiting.id)  # type: ignore[attr-defined]
        again = _add(service, other, _cut())
        assert again.output_path == waiting.output_path  # type: ignore[attr-defined]
        service.remove(first.id)  # type: ignore[attr-defined]
        service.cancel_processing()  # type: ignore[attr-defined]
        stopped = _join(service)
    finally:
        media.gate.set()
        _join(service)
    assert stopped
    assert not first.output_path.exists()  # type: ignore[attr-defined]
    fresh = _add(service, clip, _cut())
    assert fresh.output_path == first.output_path  # type: ignore[attr-defined]
    assert fresh.status is ConversionStatus.Pending  # type: ignore[attr-defined]
