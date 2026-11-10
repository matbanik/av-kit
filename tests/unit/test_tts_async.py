"""MEU-77 asynchronous TTS generation (AC-77.1-77.7, 77.9, 77.11).

Contracts (Session 33 plan): ASYNC_GENERATE, WORKER_RULE, CANCEL_RULE, PARTIAL_CLEANUP,
SHUTDOWN_STOP and PROGRESS_LAZY. Every wait is bounded (BOUNDED_WAIT, at most 5 s) and its
result is asserted. New symbols are asserted present before use (PRESENCE_GUARD), so a missing
symbol fails as an assertion.
"""

from __future__ import annotations

import inspect
import threading
import time
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Self

import numpy as np
import pytest
from fastapi.testclient import TestClient
from structlog.testing import capture_logs
from tests.integration.test_tts_models import FakeKModel, FakeSession, _patch_engines, _variant
from tests.tts_asset_fakes import FakeAssets
from tests.tts_g2p_fakes import set_phonemes, write_voice_pack

from avkit_core.domain.enums import (
    DeviceType,
    MediaFormat,
    ModelFormat,
    ModelPrecision,
    TTSSourceKind,
    TTSStatus,
)
from avkit_core.domain.errors import ConflictError, ValidationError
from avkit_core.domain.tts import (
    AssetState,
    ModelStatus,
    ModelVariant,
    TtsAsset,
    TTSJob,
    VoiceConfig,
)
from avkit_core.services.prepare import TextPreparationService
from avkit_core.services.tts import TTSService

WAIT = 5.0
VARIANT = "kokoro-pt-fp32"
VOICE = "am_eric"
TOKENS = frozenset({"s33-token"})


def _require() -> None:
    assert "spawn" in inspect.signature(TTSService).parameters, "TTSService(spawn=...) is missing"
    for name in ("wait_idle", "stop_processing", "recover_stale_processing"):
        assert hasattr(TTSService, name), f"TTSService.{name} is missing"


def _sync(worker: Callable[[], None]) -> None:
    worker()


def _thread(target: Callable[[], None]) -> threading.Thread:
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    return thread


# --- fakes ------------------------------------------------------------------------------


class _Repo:
    """`TTSJobRepository` fake. `hold_done` blocks the terminal `Done` save (AC-77.5 barrier)."""

    def __init__(self) -> None:
        self.rows: dict[str, TTSJob] = {}
        self.hold_done = False
        self.done_entered = threading.Event()
        self.done_release = threading.Event()
        self.done_released: list[bool] = []

    def add(self, job: TTSJob) -> None:
        self.rows[job.id] = job

    def get(self, job_id: str) -> TTSJob | None:
        return self.rows.get(job_id)

    def save(self, job: TTSJob) -> None:
        if self.hold_done and job.status is TTSStatus.Done:
            self.done_entered.set()
            self.done_released.append(self.done_release.wait(WAIT))
        self.rows[job.id] = job

    def delete(self, job_id: str) -> None:
        self.rows.pop(job_id, None)

    def list_by_status(self, status: TTSStatus) -> list[TTSJob]:
        return [job for job in self.rows.values() if job.status is status]


class _Models:
    def get(self, variant_id: str) -> ModelVariant | None:
        if variant_id != VARIANT:
            return None
        return ModelVariant(
            id=VARIANT,
            name="Kokoro PT",
            format=ModelFormat.PyTorch,
            precision=ModelPrecision.FP32,
            size_bytes=1,
            path=None,
            is_downloaded=True,
        )


class _UnitOfWork:
    def __init__(self, repo: _Repo) -> None:
        self.tts_jobs = repo
        self.models = _Models()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        return None

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None


class _Factory:
    """Unit-of-work factory; with `events`, appends `uow` on every open (AC-77.9 (g))."""

    def __init__(self, uow: _UnitOfWork, events: list[str] | None, lock: threading.Lock) -> None:
        self.uow = uow
        self.events = events
        self.lock = lock

    def __call__(self) -> _UnitOfWork:
        if self.events is not None:
            with self.lock:
                self.events.append("uow")
        return self.uow


class _Settings:
    def __init__(self, tmp_path: Path) -> None:
        self.values = {
            ("tts", "output_path"): str(tmp_path / "out"),
            ("tts", "models_directory"): str(tmp_path / "models"),
        }

    def get(self, namespace: str, key: str) -> object:
        return self.values[(namespace, key)]


class _Port:
    """`TTSPort` fake: one `on_progress` per segment, with optional blocks and a raise."""

    def __init__(self, segments: int) -> None:
        self.voice = VoiceConfig(
            voice_id=VOICE,
            lang_code="a",
            language="en",
            gender="m",
            style_description="narration",
        )
        self.loaded = True
        self.segments = segments
        self.hold = False
        self.entered = threading.Event()
        self.release = threading.Event()
        self.pause_after: int | None = None
        self.paused = threading.Event()
        self.resume = threading.Event()
        self.error: BaseException | None = None
        self.run: list[int] = []
        self.generate_calls = 0
        self.status_calls = 0
        self.voices_gate: threading.Event | None = None
        self.voices_entered = threading.Event()
        self.waits: list[bool] = []

    def get_model_status(self) -> ModelStatus:
        self.status_calls += 1
        return ModelStatus(
            variant_id=VARIANT if self.loaded else None,
            name="Kokoro",
            device="cpu",
            memory_bytes=1,
            is_loaded=self.loaded,
        )

    def list_voices(self) -> list[VoiceConfig]:
        if self.voices_gate is not None:
            self.voices_entered.set()
            self.waits.append(self.voices_gate.wait(WAIT))
        return [self.voice]

    def generate(
        self, text: str, voice: VoiceConfig, speed: float, on_progress: Callable[[float], None]
    ) -> np.ndarray:
        del text, voice, speed
        self.generate_calls += 1
        self.entered.set()
        if self.hold:
            self.waits.append(self.release.wait(WAIT))
        if self.error is not None:
            raise self.error
        for index in range(1, self.segments + 1):
            on_progress((index - 1) / self.segments)
            self.run.append(index)
            if self.pause_after == index:
                self.paused.set()
                self.waits.append(self.resume.wait(WAIT))
        on_progress(1.0)
        return np.zeros(8, dtype=np.float32)


class _Filesystem:
    def __init__(self) -> None:
        self.after_wav: Callable[[Path], None] | None = None
        self.writes = 0

    def write_audio_wav(self, path: Path, samples: object, sample_rate: int) -> None:
        del samples, sample_rate
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"RIFF")
        self.writes += 1
        if self.after_wav is not None:
            self.after_wav(path)


class _Media:
    def __init__(self) -> None:
        self.after_convert: Callable[[Path], None] | None = None
        self.error: BaseException | None = None
        self.converts = 0

    def convert(self, input_path: Path, output_path: Path, options: object) -> None:
        del input_path, options
        self.converts += 1
        output_path.write_bytes(b"ID3")
        if self.error is not None:
            raise self.error
        if self.after_convert is not None:
            self.after_convert(output_path)


class _Prepare(TextPreparationService):
    def __init__(self) -> None:
        super().__init__()
        self.calls = 0

    def prepare(
        self, text: str, enabled_steps: list[str], chunk_max_chars: int | None = None
    ) -> str:
        del enabled_steps, chunk_max_chars
        self.calls += 1
        return text


class _Stack:
    def __init__(
        self,
        tmp_path: Path,
        *,
        spawn: Callable[[Callable[[], None]], None] | None = None,
        events: list[str] | None = None,
        segments: int = 2,
    ) -> None:
        self.root = tmp_path / "out"
        self.events_lock = threading.Lock()
        self.repo = _Repo()
        self.factory = _Factory(_UnitOfWork(self.repo), events, self.events_lock)
        self.port = _Port(segments)
        self.filesystem = _Filesystem()
        self.media = _Media()
        self.prepare = _Prepare()
        self.assets = FakeAssets()
        self.settings = _Settings(tmp_path)
        extra: dict[str, Any] = {} if spawn is None else {"spawn": spawn}
        self.service = TTSService(
            self.factory,
            tts=self.port,
            filesystem=self.filesystem,
            media=self.media,
            settings=self.settings,
            prepare=self.prepare,
            assets=self.assets,
            **extra,
        )

    def generate(
        self, text: str = "Hello there.", fmt: MediaFormat = MediaFormat.MP3, speed: float = 1.0
    ) -> TTSJob:
        return self.service.generate(text, VOICE, speed, fmt, [], TTSSourceKind.Inline, None)

    def generating_id(self) -> str:
        """The running job's id; a file's name no longer carries it (rc.3 F5)."""
        (running,) = self.repo.list_by_status(TTSStatus.Generating)
        return running.id

    def files(self, job_id: str) -> list[str]:
        # Every file in the output folder: the name comes from the text (rc.3 F5), and a
        # cleanup check must see any file left behind, whatever its name.
        del job_id
        if not self.root.is_dir():
            return []
        return sorted(path.name for path in self.root.iterdir() if path.is_file())

    def status(self, job_id: str) -> TTSStatus:
        return self.service.get_status(job_id).status


# --- AC-77.1 ASYNC_GENERATE -------------------------------------------------------------


def test_ac_77_1_generate_returns_generating_then_done(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.port.hold = True
    started = time.monotonic()
    job = stack.generate()
    assert time.monotonic() - started < 1.0
    assert job.status is TTSStatus.Generating
    assert stack.port.entered.wait(WAIT)
    assert stack.status(job.id) is TTSStatus.Generating
    stack.port.release.set()
    assert stack.service.wait_idle(WAIT) is True
    done = stack.service.get_status(job.id)
    assert done.status is TTSStatus.Done
    assert done.output_path == stack.root / "hello-there-am_eric.mp3"
    assert done.output_path.is_file()


def test_ac_77_1_not_done_while_port_blocks_neg(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.port.hold = True
    job = stack.generate()
    assert stack.port.entered.wait(WAIT)
    current = stack.service.get_status(job.id)
    assert current.status is not TTSStatus.Done
    assert current.output_path is None
    stack.port.release.set()
    assert stack.service.wait_idle(WAIT) is True


# --- AC-77.2 one at a time --------------------------------------------------------------


def test_ac_77_2_second_generate_conflicts_while_first_runs(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.port.hold = True
    first = stack.generate()
    assert stack.port.entered.wait(WAIT)
    with pytest.raises(ConflictError, match="already in progress"):
        stack.generate()
    assert list(stack.repo.rows) == [first.id]
    stack.port.release.set()
    assert stack.service.wait_idle(WAIT) is True


def test_ac_77_2_generate_after_first_finishes_neg(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)
    first = stack.generate()
    second = stack.generate()
    assert stack.status(first.id) is TTSStatus.Done
    assert stack.status(second.id) is TTSStatus.Done


# --- AC-77.3 synchronous checks ---------------------------------------------------------


@pytest.mark.parametrize("case", ["empty_text", "bad_speed", "no_model", "missing_asset"])
def test_ac_77_3_checks_raise_before_row_and_spawn(tmp_path: Path, case: str) -> None:
    _require()
    spawned: list[int] = []
    stack = _Stack(tmp_path, spawn=lambda worker: spawned.append(1))
    text, speed = "Hello there.", 1.0
    expected: type[Exception] = ValidationError
    if case == "empty_text":
        text = ""
    elif case == "bad_speed":
        speed = 9.0
    elif case == "no_model":
        stack.port.loaded = False
        expected = ConflictError
    else:
        stack.assets.states[TtsAsset.SPACY_MODEL] = AssetState.MISSING
        expected = ConflictError
    with pytest.raises(expected):
        stack.generate(text=text, speed=speed)
    assert stack.repo.rows == {}
    assert spawned == []


def test_ac_77_3_valid_request_spawns_once_neg(tmp_path: Path) -> None:
    _require()
    spawned: list[int] = []

    def spy(worker: Callable[[], None]) -> None:
        spawned.append(1)
        worker()

    stack = _Stack(tmp_path, spawn=spy)
    job = stack.generate()
    assert spawned == [1]
    assert stack.status(job.id) is TTSStatus.Done


# --- AC-77.4 cancel mid-synthesis -------------------------------------------------------


def test_ac_77_4_cancel_between_segments_stops_and_cleans(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, segments=3)
    stack.port.pause_after = 1
    job = stack.generate()
    assert stack.port.paused.wait(WAIT)
    assert stack.service.cancel(job.id) is None
    stack.port.resume.set()
    assert stack.service.wait_idle(WAIT) is True
    assert stack.port.run == [1]
    assert stack.status(job.id) is TTSStatus.Cancelled
    assert stack.files(job.id) == []


def test_ac_77_4_cancel_unknown_or_done_changes_nothing_neg(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)
    done = stack.generate()
    before = dict(stack.repo.rows)
    assert stack.service.cancel("no-such-job") is None
    assert stack.service.cancel(done.id) is None
    assert stack.repo.rows == before
    following = stack.generate()
    assert stack.status(following.id) is TTSStatus.Done


# --- AC-77.5 cancel after synthesis, and the terminal-write race -----------------------


@pytest.mark.parametrize("hook", ["wav", "mp3"])
def test_ac_77_5_cancel_from_write_hooks_leaves_no_files(tmp_path: Path, hook: str) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)

    def cancel_from(path: Path) -> None:
        del path
        stack.service.cancel(stack.generating_id())

    if hook == "wav":
        stack.filesystem.after_wav = cancel_from
    else:
        stack.media.after_convert = cancel_from
    job = stack.generate()
    assert stack.status(job.id) is TTSStatus.Cancelled
    assert stack.files(job.id) == []


@pytest.mark.parametrize("outcome", [TTSStatus.Cancelled, TTSStatus.Failed])
@pytest.mark.parametrize("hook", ["wav", "mp3"])
def test_ac_77_5_cleanup_uses_job_paths_after_output_path_changed(
    tmp_path: Path, hook: str, outcome: TTSStatus
) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)
    moved = tmp_path / "moved"

    def change_then_end(path: Path) -> None:
        stack.settings.values[("tts", "output_path")] = str(moved)
        del path
        if outcome is TTSStatus.Cancelled:
            stack.service.cancel(stack.generating_id())
        else:
            raise RuntimeError("encoder died")

    if hook == "wav":
        stack.filesystem.after_wav = change_then_end
    else:
        stack.media.after_convert = change_then_end
    job = stack.generate()
    assert stack.status(job.id) is outcome
    assert stack.files(job.id) == []
    assert not moved.exists()

def test_ac_77_5_cancel_waits_for_terminal_write_barrier(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.repo.hold_done = True
    stack.port.hold = True
    job = stack.generate()
    stack.port.release.set()
    assert stack.repo.done_entered.wait(WAIT)
    helper = _thread(lambda: stack.service.cancel(job.id))
    helper.join(0.2)
    assert helper.is_alive()
    stack.repo.done_release.set()
    helper.join(WAIT)
    assert not helper.is_alive()
    assert stack.service.wait_idle(WAIT) is True
    assert stack.repo.done_released == [True]
    done = stack.service.get_status(job.id)
    assert done.status is TTSStatus.Done
    assert "hello-there-am_eric.mp3" in stack.files(job.id)
    stack.repo.hold_done = False
    following = stack.generate()
    assert stack.service.wait_idle(WAIT) is True
    assert stack.status(following.id) is TTSStatus.Done


def test_ac_77_5_uncancelled_job_keeps_mp3_neg(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)
    job = stack.generate()
    assert stack.status(job.id) is TTSStatus.Done
    # rc.3 F7: the WAV an MP3 is encoded from is removed once the MP3 is written.
    assert stack.files(job.id) == ["hello-there-am_eric.mp3"]


# --- AC-77.6 WORKER_RULE ----------------------------------------------------------------


def test_ac_77_6_port_error_fails_job_on_worker_thread(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _require()
    hook_calls: list[object] = []
    monkeypatch.setattr(threading, "excepthook", hook_calls.append)
    stack = _Stack(tmp_path)
    stack.port.error = RuntimeError("engine died")
    with capture_logs() as logs:
        job = stack.generate()
        assert stack.service.wait_idle(WAIT) is True
    failed = stack.service.get_status(job.id)
    assert failed.status is TTSStatus.Failed
    assert failed.error_message == "RuntimeError: engine died"
    events = [entry for entry in logs if entry["event"] == "tts.generate_failed"]
    assert len(events) == 1
    assert events[0]["job_id"] == job.id
    assert events[0]["exc_info"] is True
    assert stack.files(job.id) == []
    assert stack.service._current_id is None
    assert hook_calls == []


def test_ac_77_6_convert_error_removes_partial_files(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.media.error = RuntimeError("encoder died")
    job = stack.generate()
    assert stack.service.wait_idle(WAIT) is True
    failed = stack.service.get_status(job.id)
    assert failed.status is TTSStatus.Failed
    assert failed.error_message == "RuntimeError: encoder died"
    assert stack.files(job.id) == []


def test_ac_77_6_validation_error_ends_failed_without_raise_neg(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)
    stack.port.error = ValidationError("progress fraction must be between 0.0 and 1.0")
    job = stack.generate()
    failed = stack.service.get_status(job.id)
    assert failed.status is TTSStatus.Failed
    assert failed.error_message == "progress fraction must be between 0.0 and 1.0"


# --- AC-77.7 spawn failure --------------------------------------------------------------


def test_ac_77_7_spawn_error_fails_row_and_reraises(tmp_path: Path) -> None:
    _require()

    def broken(worker: Callable[[], None]) -> None:
        raise RuntimeError("no threads")

    stack = _Stack(tmp_path, spawn=broken)
    with pytest.raises(RuntimeError, match="no threads"):
        stack.generate()
    rows = list(stack.repo.rows.values())
    assert len(rows) == 1
    assert rows[0].status is TTSStatus.Failed
    assert rows[0].error_message == "RuntimeError: no threads"
    assert stack.service._current_id is None


def test_ac_77_7_next_generate_after_spawn_error_neg(tmp_path: Path) -> None:
    _require()
    attempts: list[int] = []

    def flaky(worker: Callable[[], None]) -> None:
        attempts.append(1)
        if len(attempts) == 1:
            raise RuntimeError("no threads")
        worker()

    stack = _Stack(tmp_path, spawn=flaky)
    with pytest.raises(RuntimeError):
        stack.generate()
    job = stack.generate()
    assert stack.status(job.id) is TTSStatus.Done


# --- AC-77.9 SHUTDOWN_STOP --------------------------------------------------------------


def test_ac_77_9_a_stop_cancels_running_job_and_returns_true(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, segments=3)
    stack.port.pause_after = 1
    job = stack.generate()
    assert stack.port.paused.wait(WAIT)
    results: list[bool] = []
    stopper = _thread(lambda: results.append(stack.service.stop_processing(WAIT)))
    stopper.join(0.2)
    assert stopper.is_alive()
    stack.port.resume.set()
    stopper.join(WAIT)
    assert not stopper.is_alive()
    assert results == [True]
    assert stack.status(job.id) is TTSStatus.Cancelled
    assert stack.port.run == [1]


def test_ac_77_9_b_stop_timeout_returns_false_and_logs(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.port.hold = True
    job = stack.generate()
    assert stack.port.entered.wait(WAIT)
    with capture_logs() as logs:
        stopped = stack.service.stop_processing(timeout=0.2)
    assert stopped is False
    events = [entry for entry in logs if entry["event"] == "tts.stop_timeout"]
    assert len(events) == 1
    assert events[0]["job_id"] == job.id
    assert events[0]["timeout"] == 0.2
    stack.port.release.set()
    assert stack.service.wait_idle(WAIT) is True
    assert stack.status(job.id) is TTSStatus.Cancelled


class _LifespanSpy:
    def __init__(self, name: str, order: list[str], idle: bool = True) -> None:
        self.name = name
        self.order = order
        self.idle = idle

    def recover_stale_processing(self) -> None:
        self.order.append(f"{self.name}.recover")

    def cancel_processing(self) -> None:
        self.order.append(f"{self.name}.cancel")

    def stop_processing(self, timeout: float = 10.0) -> bool:
        del timeout
        self.order.append(f"{self.name}.stop")
        return self.idle

    def unload(self) -> None:
        self.order.append(f"{self.name}.unload")


@pytest.mark.parametrize("idle", [True, False])
def test_ac_77_9_c_lifespan_unloads_only_when_tts_idle(idle: bool) -> None:
    _require()
    from avkit_api.main import create_app
    from avkit_api.wiring import AppServices

    order: list[str] = []
    services = AppServices(
        download=_LifespanSpy("download", order),
        transcript=_LifespanSpy("transcript", order),
        tts=_LifespanSpy("tts", order, idle),
        models=_LifespanSpy("models", order),
        settings=SimpleNamespace(),
        health=SimpleNamespace(),
        conversion=_LifespanSpy("conversion", order),
        capture=SimpleNamespace(),
    )
    app = create_app(
        tokens=TOKENS, services=services, engine_dispose=lambda: order.append("dispose")
    )
    with capture_logs() as logs:
        with TestClient(app):
            assert order == ["transcript.recover", "tts.recover"]
    assert "transcript.stop" in order
    tail = order[order.index("transcript.stop") :]
    busy = [entry for entry in logs if entry["event"] == "api.shutdown_tts_busy"]
    if idle:
        assert tail == ["transcript.stop", "tts.stop", "models.unload", "dispose"]
        assert busy == []
    else:
        assert tail == ["transcript.stop", "tts.stop"]
        assert len(busy) == 1


def test_ac_77_9_d_generate_after_stop_conflicts(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    assert stack.service.stop_processing(timeout=0.2) is True
    with pytest.raises(ConflictError, match="stopping"):
        stack.generate()
    assert stack.repo.rows == {}


def test_ac_77_9_e_reservation_before_spawn_keeps_stop_busy(tmp_path: Path) -> None:
    _require()
    deferred: list[Callable[[], None]] = []
    stack = _Stack(tmp_path, spawn=deferred.append)
    job = stack.generate()
    assert job.status is TTSStatus.Generating
    assert len(deferred) == 1
    assert stack.service.stop_processing(timeout=0.2) is False
    assert stack.status(job.id) is TTSStatus.Generating
    worker = _thread(deferred[0])
    worker.join(WAIT)
    assert not worker.is_alive()
    assert stack.status(job.id) is TTSStatus.Cancelled
    assert stack.prepare.calls == 0
    assert stack.port.generate_calls == 0
    assert stack.service.stop_processing(timeout=0.2) is True


def test_ac_77_9_f_spawn_failure_while_stopping(tmp_path: Path) -> None:
    _require()
    entered = threading.Event()
    gate = threading.Event()

    def blocking_then_raise(worker: Callable[[], None]) -> None:
        entered.set()
        gate.wait(WAIT)
        raise RuntimeError("spawn died")

    stack = _Stack(tmp_path, spawn=blocking_then_raise)
    errors: list[BaseException] = []

    def run_generate() -> None:
        try:
            stack.generate()
        except RuntimeError as exc:
            errors.append(exc)

    caller = _thread(run_generate)
    assert entered.wait(WAIT)
    results: list[bool] = []
    stopper = _thread(lambda: results.append(stack.service.stop_processing(timeout=WAIT)))
    stopper.join(0.2)
    assert stopper.is_alive()
    gate.set()
    caller.join(WAIT)
    stopper.join(WAIT)
    assert not caller.is_alive()
    assert not stopper.is_alive()
    assert len(errors) == 1
    assert results == [True]
    rows = list(stack.repo.rows.values())
    assert len(rows) == 1
    assert rows[0].status is TTSStatus.Cancelled
    assert stack.service._current_id is None


def test_ac_77_9_g_stop_drains_caller_after_worker(tmp_path: Path) -> None:
    _require()
    events: list[str] = []
    finished = threading.Event()
    gate = threading.Event()

    def run_then_block(worker: Callable[[], None]) -> None:
        worker()
        finished.set()
        gate.wait(WAIT)

    stack = _Stack(tmp_path, spawn=run_then_block, events=events)
    returned: list[TTSJob] = []
    caller = _thread(lambda: returned.append(stack.generate()))
    assert finished.wait(WAIT)
    assert stack.service._current_id is None
    results: list[bool] = []

    def stop() -> None:
        results.append(stack.service.stop_processing(timeout=WAIT))
        with stack.events_lock:
            events.append("stopped")

    stopper = _thread(stop)
    stopper.join(0.2)
    assert stopper.is_alive()
    gate.set()
    caller.join(WAIT)
    stopper.join(WAIT)
    assert not caller.is_alive()
    assert not stopper.is_alive()
    assert len(returned) == 1
    assert returned[0].status is TTSStatus.Done
    assert results == [True]
    last_uow = max(index for index, name in enumerate(events) if name == "uow")
    assert last_uow < events.index("stopped")


def test_ac_77_9_h_stop_drains_caller_before_admission(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path)
    stack.port.voices_gate = threading.Event()
    errors: list[BaseException] = []

    def run_generate() -> None:
        try:
            stack.generate()
        except ConflictError as exc:
            errors.append(exc)

    caller = _thread(run_generate)
    assert stack.port.voices_entered.wait(WAIT)
    results: list[bool] = []
    stopper = _thread(lambda: results.append(stack.service.stop_processing(timeout=WAIT)))
    stopper.join(0.2)
    assert stopper.is_alive()
    stack.port.voices_gate.set()
    caller.join(WAIT)
    stopper.join(WAIT)
    assert not caller.is_alive()
    assert not stopper.is_alive()
    assert len(errors) == 1
    assert stack.repo.rows == {}
    assert results == [True]
    calls_before = stack.port.status_calls
    with pytest.raises(ConflictError):
        stack.generate()
    assert stack.port.status_calls == calls_before


def test_ac_77_9_stop_with_nothing_running_neg(tmp_path: Path) -> None:
    _require()
    stack = _Stack(tmp_path, spawn=_sync)
    stack.generate()
    before = dict(stack.repo.rows)
    started = time.monotonic()
    assert stack.service.stop_processing() is True
    assert time.monotonic() - started < 1.0
    assert stack.repo.rows == before


# --- AC-77.11 PROGRESS_LAZY -------------------------------------------------------------
# Merge note (Session 32 + 33 landing): Session 32 retired KPipeline for av-kit's own G2P and
# `split_phonemes` chunking, so these tests drive that chunk loop. The contract is unchanged:
# a cancel raised from `on_progress` stops before the next chunk is synthesized, progress is
# reported once per chunk, and only the last report is 1.0.


class _Stop(Exception):
    pass


def _heart() -> VoiceConfig:
    return VoiceConfig(
        voice_id="af_heart",
        lang_code="a",
        language="American English",
        gender="Female",
        style_description="heart",
    )


def _chunked_phonemes(chunks: int) -> str:
    """`chunks` sentences of 300 phonemes: each exceeds half of MAX_PHONEMES, so one per chunk."""
    from avkit_infra.tts.g2p import split_phonemes

    phonemes = " ".join("a" * 300 + "." for _ in range(chunks))
    assert len(split_phonemes(phonemes)) == chunks
    return phonemes


def _loaded_adapter(tmp_path: Path, variant_id: str) -> Any:
    import json

    from avkit_infra.tts.adapter import KokoroAdapter

    vocab = tmp_path / "config.json"
    vocab.write_text(json.dumps({"vocab": {"a": 7, "b": 8}}), encoding="utf-8")
    write_voice_pack(tmp_path, "af_heart")
    weights = tmp_path / ("pt.pth" if variant_id == VARIANT else "model.onnx")
    weights.write_bytes(b"w")
    adapter = KokoroAdapter(vocab_path=lambda: vocab)
    adapter.load_model(_variant(variant_id, weights), DeviceType.CPU)
    return adapter


def _raise_on_progress(fraction: float) -> None:
    raise _Stop(fraction)


def test_ac_77_11_pytorch_branch_stops_after_one_chunk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_engines(monkeypatch)
    set_phonemes(_chunked_phonemes(3))
    adapter = _loaded_adapter(tmp_path, VARIANT)
    with pytest.raises(_Stop):
        adapter.generate("text", _heart(), 1.0, _raise_on_progress)
    assert len(FakeKModel.forward_calls) == 1


@pytest.mark.parametrize(
    ("chunks", "expected"),
    [
        (2, [0.5, 1.0]),
        (4, [0.25, 0.5, 0.75, 1.0]),
    ],
)
def test_ac_77_11_pytorch_progress_is_per_chunk_and_ends_at_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    chunks: int,
    expected: list[float],
) -> None:
    _patch_engines(monkeypatch)
    set_phonemes(_chunked_phonemes(chunks))
    adapter = _loaded_adapter(tmp_path, VARIANT)
    values: list[float] = []
    adapter.generate("text", _heart(), 1.0, values.append)
    assert values == pytest.approx(expected)
    assert all(value < 1.0 for value in values[:-1])
    assert values[-1] == 1.0
    assert len(FakeKModel.forward_calls) == chunks


def test_ac_77_11_onnx_branch_synthesizes_one_chunk_neg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_engines(monkeypatch)
    set_phonemes(_chunked_phonemes(3))
    adapter = _loaded_adapter(tmp_path, "kokoro-onnx-int8")
    original = adapter._onnx_chunk
    synthesized: list[int] = []

    def spy(*args: Any, **kwargs: Any) -> Any:
        synthesized.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(adapter, "_onnx_chunk", spy)
    with pytest.raises(_Stop):
        adapter.generate("text", _heart(), 1.0, _raise_on_progress)
    assert synthesized == [1]
    assert len(FakeSession.runs) == 1
