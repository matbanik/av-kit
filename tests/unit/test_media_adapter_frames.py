"""MEU-133 FFmpegAdapter._run decoding (Session 62): RUN_UTF8, under D-573 A.

A recording fake `subprocess.run` decodes its byte payload the way the real one does: with the
`encoding` and `errors` it was given, else with cp1252 and strict errors, the Windows locale
default that broke a probe whose path or tags hold a character outside cp1252 (D-573).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from avkit_infra.media.adapter import FFmpegAdapter

RUN_KEYS = ("encoding", "errors", "text", "capture_output")
WANTED = {"encoding": "utf-8", "errors": "replace", "text": True, "capture_output": True}
#: 0x81 is undefined in cp1252, and a lone continuation byte is not UTF-8.
BAD = b"\x81\xff"


class _Result:
    def __init__(self, stdout: str) -> None:
        self.returncode = 0
        self.stdout = stdout
        self.stderr = ""


class RecordingRun:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, command: list[str], **kwargs: object) -> _Result:
        self.calls.append((list(command), dict(kwargs)))
        encoding = kwargs.get("encoding") or "cp1252"
        errors = kwargs.get("errors") or "strict"
        return _Result(self.payload.decode(str(encoding), str(errors)))


def _adapter(tmp_path: Path) -> FFmpegAdapter:
    binary = tmp_path / "ffmpeg.exe"
    binary.write_text("fake", encoding="utf-8")
    (tmp_path / "ffprobe.exe").write_text("fake", encoding="utf-8")
    return FFmpegAdapter(configured_path=binary)


def _probe_payload(title: bytes) -> bytes:
    text = json.dumps(
        {
            "format": {
                "duration": "3.000000",
                "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
                "tags": {"title": "@"},
            },
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 320,
                    "height": 240,
                },
            ],
        }
    )
    return text.encode("ascii").replace(b"@", title)


def _outcome(call: object) -> tuple[str | None, object]:
    try:
        return None, call()  # type: ignore[operator]
    except Exception as exc:  # noqa: BLE001 - the test reads the failure's type name only
        return type(exc).__name__, None


def test_ac_133_6_probe_runs_with_utf8_and_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = RecordingRun(_probe_payload(b"plain"))
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    info = _adapter(tmp_path).probe(tmp_path / "clip.mp4")
    assert info.duration == 3.0
    assert len(run.calls) == 1
    command, kwargs = run.calls[0]
    assert Path(command[0]).name == "ffprobe.exe"
    assert {key: kwargs.get(key) for key in RUN_KEYS} == WANTED


def test_ac_133_6_version_runs_with_utf8_and_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = RecordingRun(b"ffmpeg version 7.1 Copyright\nbuilt with gcc\n")
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    line = _adapter(tmp_path).ffmpeg_version()
    assert line == "ffmpeg version 7.1 Copyright"
    assert len(run.calls) == 1
    command, kwargs = run.calls[0]
    assert command[1:] == ["-version"]
    assert {key: kwargs.get(key) for key in RUN_KEYS} == WANTED


def test_ac_133_6_invalid_bytes_in_a_probe_do_not_raise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = RecordingRun(_probe_payload(BAD))
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    adapter = _adapter(tmp_path)
    failure, info = _outcome(lambda: adapter.probe(tmp_path / "clip.mp4"))
    assert failure is None
    assert info is not None
    assert (info.duration, info.video_codec, info.width) == (3.0, "h264", 320)  # type: ignore[attr-defined]


def test_ac_133_6_invalid_bytes_in_the_version_do_not_raise(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = RecordingRun(b"ffmpeg version 7.1 " + BAD + b"\n")
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    adapter = _adapter(tmp_path)
    failure, line = _outcome(adapter.ffmpeg_version)
    assert failure is None
    assert line == "ffmpeg version 7.1 ��"


# ---------------------------------------------------------------- MEU-134 (Session 62)
# FRAME_GRAB, END_GAP and FRAME_PORT's probe timeout, with a scripted fake `subprocess.run`
# and a fake clock put in place of the adapter module's `time`.

import subprocess  # noqa: E402
import time as real_time  # noqa: E402
from collections.abc import Callable  # noqa: E402

from avkit_core.domain.errors import FFmpegNotFoundError, MediaProbeError  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"frame"
GRAB_TAIL = ["-frames:v", "1", "-c:v", "png", "-f", "image2pipe", "pipe:1"]


class _Bytes:
    def __init__(self, stdout: bytes | str, returncode: int = 0) -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = b"" if isinstance(stdout, bytes) else ""


class _Clock:
    def __init__(self, now: float = 100.0) -> None:
        self.now = now

    def monotonic(self) -> float:
        return self.now

    def __getattr__(self, name: str) -> object:
        return getattr(real_time, name)


Answer = object


class ScriptedRun:
    """Answers each call in turn: a result, an exception to raise, or a callable."""

    def __init__(self, clock: _Clock, answers: list[Answer], cost: float = 0.0) -> None:
        self.clock = clock
        self.answers = list(answers)
        self.cost = cost
        self.calls: list[tuple[list[str], dict[str, object]]] = []

    def __call__(self, command: list[str], **kwargs: object) -> object:
        self.calls.append((list(command), dict(kwargs)))
        self.clock.now += self.cost
        answer = self.answers.pop(0) if self.answers else _Bytes(b"", 1)
        if isinstance(answer, BaseException):
            raise answer
        if callable(answer):
            return answer()
        return answer

    def programs(self) -> list[str]:
        return [Path(command[0]).stem for command, _ in self.calls]


def _grab_setup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answers: list[Answer], cost: float = 0.0
) -> tuple[FFmpegAdapter, ScriptedRun, _Clock, Path]:
    clock = _Clock()
    run = ScriptedRun(clock, answers, cost)
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    monkeypatch.setattr("avkit_infra.media.adapter.time", clock)
    adapter = _adapter(tmp_path)
    video = tmp_path / "clip.mp4"
    video.write_bytes(b"video")
    return adapter, run, clock, video


def _ffmpeg(tmp_path: Path) -> str:
    return str(tmp_path / "ffmpeg.exe")


def test_ac_134_9_input_seek_argv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adapter, run, _clock, video = _grab_setup(tmp_path, monkeypatch, [_Bytes(PNG)])
    data = adapter.grab_frame(video, 725_500, seek="input", timeout_s=5.0)
    assert data == PNG
    command, kwargs = run.calls[0]
    assert command == [
        _ffmpeg(tmp_path),
        "-hide_banner",
        "-nostdin",
        "-v",
        "error",
        "-ss",
        "725.500",
        "-i",
        str(video),
        *GRAB_TAIL,
    ]
    assert kwargs.get("capture_output") is True
    assert kwargs.get("check") is False
    assert kwargs.get("timeout") == pytest.approx(5.0)
    assert not kwargs.get("text")
    assert len(run.calls) == 1


def test_ac_134_9_output_seek_argv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adapter, run, _clock, video = _grab_setup(tmp_path, monkeypatch, [_Bytes(PNG)])
    data = adapter.grab_frame(video, 1, seek="output", timeout_s=5.0)
    assert data == PNG
    command, kwargs = run.calls[0]
    assert command == [
        _ffmpeg(tmp_path),
        "-hide_banner",
        "-nostdin",
        "-v",
        "error",
        "-i",
        str(video),
        "-ss",
        "0.001",
        *GRAB_TAIL,
    ]
    assert kwargs.get("timeout") == pytest.approx(5.0)


@pytest.mark.parametrize(
    "answer",
    [_Bytes(b"", 1), _Bytes(PNG, 1), subprocess.TimeoutExpired(["ffmpeg"], 5.0)],
    ids=["exit-1-empty", "exit-1-bytes", "timeout"],
)
def test_ac_134_9_a_failed_output_grab_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: Answer
) -> None:
    adapter, run, _clock, video = _grab_setup(tmp_path, monkeypatch, [answer])
    data = adapter.grab_frame(video, 1000, seek="output", timeout_s=5.0)
    assert run.programs() == ["ffmpeg"]
    assert data == b""


def test_ac_134_9_a_missing_ffmpeg_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    adapter, _run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [FileNotFoundError("ffmpeg.exe")]
    )
    with pytest.raises(FFmpegNotFoundError):
        adapter.grab_frame(video, 1000, seek="input", timeout_s=5.0)


def _packet(stdout: str) -> Callable[[], _Bytes]:
    return lambda: _Bytes(stdout)


def test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [_Bytes(b""), _packet("2.960\n"), _Bytes(PNG)]
    )
    data = adapter.grab_frame(video, 2999, seek="input", timeout_s=5.0)
    assert data == PNG
    assert run.programs() == ["ffmpeg", "ffprobe", "ffmpeg"]
    packet, kwargs = run.calls[1]
    assert packet == [
        str(tmp_path / "ffprobe.exe"),
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-read_intervals",
        "0.000%",
        "-show_entries",
        "packet=pts_time",
        "-of",
        "csv=p=0",
        str(video),
    ]
    assert {key: kwargs.get(key) for key in RUN_KEYS} == WANTED
    assert kwargs.get("check") is False
    assert "timeout" in kwargs
    retry, _ = run.calls[2]
    assert retry[retry.index("-ss") + 1] == "2.959"
    assert retry.index("-ss") < retry.index("-i")


def test_ac_134_9_end_gap_reads_from_60_seconds_before(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [_Bytes(b""), _packet("7199.980\n"), _Bytes(PNG)]
    )
    data = adapter.grab_frame(video, 7_200_021, seek="input", timeout_s=5.0)
    assert data == PNG
    packet, _ = run.calls[1]
    assert packet[packet.index("-read_intervals") + 1] == "7140.021%"
    retry, _ = run.calls[2]
    assert retry[retry.index("-ss") + 1] == "7199.979"


def test_ac_134_9_the_largest_packet_time_wins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path,
        monkeypatch,
        [_Bytes(b""), _packet("1.000\nN/A\n\n2.960\n2.920\n"), _Bytes(PNG)],
    )
    data = adapter.grab_frame(video, 2999, seek="input", timeout_s=5.0)
    assert data == PNG
    retry, _ = run.calls[2]
    assert retry[retry.index("-ss") + 1] == "2.959"


@pytest.mark.parametrize(
    "stdout",
    ["N/A\n", "", "3.000\n", "3.500\n2.000\n", "nan\ninf\n"],
    ids=["na-only", "blank", "at-t", "after-t", "non-finite"],
)
def test_ac_134_9_no_usable_earlier_packet_means_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, stdout: str
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [_Bytes(b""), _packet(stdout), _Bytes(PNG)]
    )
    data = adapter.grab_frame(video, 3000, seek="input", timeout_s=5.0)
    assert run.programs() == ["ffmpeg", "ffprobe"]
    assert data == b""


@pytest.mark.parametrize(
    "answer",
    [subprocess.TimeoutExpired(["ffprobe"], 1.0), _Bytes("2.960\n", 1)],
    ids=["timeout", "exit-1"],
)
def test_ac_134_9_a_failed_packet_read_means_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: Answer
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [_Bytes(b""), answer, _Bytes(PNG)]
    )
    data = adapter.grab_frame(video, 2999, seek="input", timeout_s=5.0)
    assert run.programs() == ["ffmpeg", "ffprobe"]
    assert data == b""


def test_ac_134_9_an_empty_output_grab_runs_no_packet_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(tmp_path, monkeypatch, [_Bytes(b"")])
    data = adapter.grab_frame(video, 2999, seek="output", timeout_s=5.0)
    assert run.programs() == ["ffmpeg"]
    assert data == b""


def test_ac_134_9_every_process_gets_the_time_left(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [_Bytes(b""), _packet("2.960\n"), _Bytes(PNG)], cost=3.0
    )
    data = adapter.grab_frame(video, 2999, seek="input", timeout_s=10.0)
    assert data == PNG
    timeouts = [kwargs.get("timeout") for _, kwargs in run.calls]
    assert timeouts == [pytest.approx(10.0), pytest.approx(7.0), pytest.approx(4.0)]


def test_ac_134_9_no_time_left_after_the_packet_read_starts_no_retry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(
        tmp_path, monkeypatch, [_Bytes(b""), _packet("2.960\n"), _Bytes(PNG)], cost=5.0
    )
    data = adapter.grab_frame(video, 2999, seek="input", timeout_s=10.0)
    assert run.programs() == ["ffmpeg", "ffprobe"]
    assert data == b""


def test_ac_134_9_no_time_at_entry_starts_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    adapter, run, _clock, video = _grab_setup(tmp_path, monkeypatch, [_Bytes(PNG)])
    data = adapter.grab_frame(video, 1000, seek="input", timeout_s=0.0)
    assert data == b""
    assert run.calls == []


def test_ac_134_9_probe_passes_its_timeout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = RecordingRun(_probe_payload(b"plain"))
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    info = _adapter(tmp_path).probe(tmp_path / "clip.mp4", timeout_s=2.5)
    assert info.duration == 3.0
    _command, kwargs = run.calls[0]
    assert kwargs.get("timeout") == 2.5


def test_ac_134_9_a_probe_past_its_timeout_is_a_probe_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _late(command: list[str], **kwargs: object) -> object:
        raise subprocess.TimeoutExpired(command, 2.5)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _late)
    adapter = _adapter(tmp_path)
    failure: BaseException | None = None
    try:
        adapter.probe(tmp_path / "clip.mp4", timeout_s=2.5)
    except BaseException as exc:  # noqa: BLE001 - the test reads the failure's type and text
        failure = exc
    assert type(failure).__name__ == "MediaProbeError"
    assert isinstance(failure, MediaProbeError)
    assert str(failure) == "ffprobe timed out"


def test_ac_134_9_no_timeout_keyword_without_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = RecordingRun(_probe_payload(b"plain"))
    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", run)
    adapter = _adapter(tmp_path)
    adapter.probe(tmp_path / "clip.mp4")
    adapter.ffmpeg_version()
    assert len(run.calls) == 2
    assert ["timeout" in kwargs for _, kwargs in run.calls] == [False, False]
