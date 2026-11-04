"""MEU-29 conversion infrastructure tests. Imports stay inside tests so collection cannot ERROR."""

from __future__ import annotations

import inspect
import json
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

PLAN_SETS = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "execution"
    / "plans"
    / "2026-08-24-p8-conversion-engine"
    / "named-sets.json"
)
CONVERSION_JOB_COLUMNS = (
    "id",
    "kind",
    "input_path",
    "output_path",
    "display_name",
    "preset_id",
    "cq",
    "scale_height",
    "audio_mode",
    "gpu_encoder",
    "in_ms",
    "out_ms",
    "copy_mode",
    "stream_index",
    "status",
    "progress",
    "speed_bps",
    "eta_seconds",
    "file_size",
    "duration_seconds",
    "width",
    "height",
    "error_message",
    "queue_position",
    "created_at",
    "updated_at",
    "gpu_preference",
)
REPO_METHODS = (
    "add",
    "get",
    "list_ordered",
    "save",
    "reorder",
    "delete",
    "delete_all",
)


def _now() -> datetime:
    return datetime.now(UTC)


def _sets() -> dict[str, object]:
    return json.loads(PLAN_SETS.read_text(encoding="utf-8"))


def _protocol_methods(cls: type[object]) -> tuple[str, ...]:
    return tuple(
        name
        for name, value in cls.__dict__.items()
        if callable(value) and not name.startswith("_")
    )


def _make_uow_factory(tmp_path: Path):
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

    return factory, engine


def _cut_job(**overrides: object):
    from avkit_core.domain.conversion import ConversionJob
    from avkit_core.domain.enums import (
        AudioEncodeMode,
        ConversionKind,
        ConversionPresetId,
        ConversionStatus,
        CutCopyMode,
    )

    payload: dict[str, object] = {
        "id": str(uuid4()),
        "kind": ConversionKind.Cut,
        "input_path": Path("C:/in/clip.mp4"),
        "output_path": Path("C:/out/clip_cut.mp4"),
        "display_name": "clip.mp4",
        "preset_id": ConversionPresetId.Balanced,
        "cq": 25,
        "scale_height": 720,
        "audio_mode": AudioEncodeMode.Aac128,
        "gpu_encoder": "libx265",
        "in_ms": 100,
        "out_ms": 2500,
        "copy_mode": CutCopyMode.FastCopy,
        "stream_index": 0,
        "status": ConversionStatus.Pending,
        "progress": 0.0,
        "speed_bps": 1.5,
        "eta_seconds": 12,
        "file_size": 4096,
        "duration_seconds": 2.4,
        "width": 1920,
        "height": 1080,
        "error_message": "none",
        "queue_position": 3,
        "created_at": _now(),
        "updated_at": _now(),
    }
    payload.update(overrides)
    return ConversionJob(**payload)


def _encode_options():
    from avkit_core.domain.conversion import VideoEncodeOptions
    from avkit_core.domain.enums import AudioEncodeMode

    return VideoEncodeOptions(
        codec="libx265",
        cq=25,
        nvenc_preset="p4",
        scale_height=720,
        audio_mode=AudioEncodeMode.Aac128,
        hwaccel=None,
    )


def _fake_ffmpeg(tmp_path: Path) -> Path:
    binary = tmp_path / "ffmpeg.exe"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.write_text("fake", encoding="utf-8")
    return binary


class _Result:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class _Stdin:
    def __init__(self) -> None:
        self.writes: list[str] = []

    def write(self, data: str) -> int:
        self.writes.append(data)
        return len(data)

    def flush(self) -> None:
        return None

    def close(self) -> None:
        return None


class _FakePopen:
    def __init__(
        self,
        argv: list[str],
        *,
        returncode: int = 0,
        lines: list[str] | None = None,
        hang: bool = False,
    ) -> None:
        self.args = list(argv)
        self.stdin = _Stdin()
        self._lines = list(
            lines
            if lines is not None
            else ["frame=  12 fps=30 time=00:00:00.40 bitrate=N/A speed=1.00x\n"]
        )
        self.returncode: int | None = None
        self._final = returncode
        self._hang = hang
        self.stderr = self
        self.terminated = False

    def readline(self) -> str:
        if self._lines:
            return self._lines.pop(0)
        if not self._hang:
            self.returncode = self._final
        return ""

    def poll(self) -> int | None:
        if self.returncode is not None:
            return self.returncode
        if not self._lines and not self._hang:
            self.returncode = self._final
            return self._final
        return None

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = 255

    def wait(self, timeout: float | None = None) -> int:
        if self.returncode is None:
            self.returncode = self._final
        return self.returncode

    def close(self) -> None:
        self._hang = False
        if self.returncode is None:
            self.returncode = self._final

    def __iter__(self) -> object:
        return self

    def __next__(self) -> str:
        line = self.readline()
        if line == "" and self.poll() is not None:
            raise StopIteration
        if line == "":
            raise StopIteration
        return line


@pytest.mark.parametrize("ac_id", ["AC-29.1"], ids=["AC-29.1"])
@pytest.mark.unit
def test_ac_29_1_conversion_jobs_table_not_sti(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-29.1"
    from sqlalchemy import inspect as sa_inspect

    _factory, engine = _make_uow_factory(tmp_path)
    inspector = sa_inspect(engine)
    tables = set(inspector.get_table_names())
    assert "conversion_jobs" in tables
    assert "jobs" not in tables
    indexes = {item["name"] for item in inspector.get_indexes("conversion_jobs")}
    assert any("queue_position" in name for name in indexes)
    assert any("status" in name for name in indexes)


@pytest.mark.parametrize("ac_id", ["AC-29.2"], ids=["AC-29.2"])
@pytest.mark.unit
def test_ac_29_2_greenfield_and_if_not_exists_migration(
    ac_id: str, tmp_path: Path
) -> None:
    assert ac_id == "AC-29.2"
    from avkit_infra.database import models as models_mod
    from avkit_infra.database.migrations import MIGRATIONS, apply_migrations

    assert hasattr(models_mod, "ConversionJobRow")
    assert models_mod.ConversionJobRow.__tablename__ == "conversion_jobs"
    assert any(
        "CREATE TABLE IF NOT EXISTS conversion_jobs" in statement for statement in MIGRATIONS
    )
    _factory, engine = _make_uow_factory(tmp_path)
    apply_migrations(engine)
    apply_migrations(engine)


@pytest.mark.parametrize("ac_id", ["AC-29.3"], ids=["AC-29.3"])
@pytest.mark.unit
def test_ac_29_3_uow_conversion_jobs_download_shape(ac_id: str) -> None:
    assert ac_id == "AC-29.3"
    from avkit_core.ports.storage import ConversionJobRepository, UnitOfWork

    assert "conversion_jobs" in UnitOfWork.__annotations__
    assert _protocol_methods(ConversionJobRepository) == REPO_METHODS


@pytest.mark.parametrize("ac_id", ["AC-29.4"], ids=["AC-29.4"])
@pytest.mark.unit
def test_ac_29_4_probe_fills_additive_media_info(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.4"
    from avkit_core.domain.conversion import StreamInfo
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    # FIXTURE_REPAIRS (g) (Session 33, MEU-78): FFPROBE_RULE reads the sibling ffprobe.
    (tmp_path / "ffprobe.exe").write_text("fake", encoding="utf-8")
    payload = {
        "format": {"duration": "2.5", "format_name": "mov,mp4,m4a,3gp,3g2,mj2"},
        "streams": [
            {
                "index": 0,
                "codec_type": "video",
                "codec_name": "hevc",
                "width": 1920,
                "height": 1080,
                "r_frame_rate": "30/1",
                "bits_per_raw_sample": "10",
                "field_order": "progressive",
                "tags": {"language": "und"},
            },
            {
                "index": 1,
                "codec_type": "audio",
                "codec_name": "aac",
                "sample_rate": "48000",
                "channels": 2,
                "tags": {"language": "eng"},
            },
        ],
    }
    seen: list[list[str]] = []

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        seen.append(list(cmd))
        return _Result(stdout=json.dumps(payload))

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    info = FFmpegAdapter(configured_path=binary).probe(tmp_path / "clip.mp4")
    probe_cmd = seen[0]
    assert "-show_streams" in probe_cmd
    assert "-show_format" in probe_cmd
    assert "-of" in probe_cmd or "-print_format" in probe_cmd
    assert "json" in probe_cmd
    assert info.width == 1920
    assert info.height == 1080
    assert info.fps == 30.0
    assert info.bit_depth == 10
    assert info.field_order == "progressive"
    assert info.streams is not None
    assert len(info.streams) == 2
    first = info.streams[0]
    assert isinstance(first, StreamInfo)
    assert first.index == 0
    assert first.codec_type == "video"


@pytest.mark.parametrize("ac_id", ["AC-29.5"], ids=["AC-29.5"])
@pytest.mark.unit
def test_ac_29_5_detect_gpu_parses_encoders_never_wmic(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.5"
    from avkit_infra.media.adapter import FFmpegAdapter

    sets = _sets()
    ban = str(sets["WMIC_BAN"])
    binary = _fake_ffmpeg(tmp_path)
    source = Path(inspect.getfile(FFmpegAdapter)).read_text(encoding="utf-8")
    assert hasattr(FFmpegAdapter, "detect_gpu")
    assert ban not in source.lower()
    captured: list[list[str]] = []

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        captured.append(list(cmd))
        joined = " ".join(cmd)
        assert ban not in joined.lower()
        if "-encoders" in cmd:
            return _Result(
                stdout=(
                    "Encoders:\n"
                    " V..... = Video\n"
                    " V..... libx264              libx264 H.264 / AVC"
                    " / MPEG-4 part 10 (codec h264)\n"
                    " V..... libx265              libx265 H.265 / HEVC (codec hevc)\n"
                    " V....D hevc_nvenc           NVIDIA NVENC hevc encoder (codec hevc)\n"
                )
            )
        return _Result(returncode=1, stderr="encoder not available")

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    caps = FFmpegAdapter(configured_path=binary).detect_gpu()
    assert any("-encoders" in cmd for cmd in captured)
    assert caps.software_h265 is True
    assert caps.software_h264 is True
    assert any(
        "-c:v" in cmd and cmd[cmd.index("-c:v") + 1] == "hevc_nvenc" for cmd in captured
    )
    assert all(ban not in " ".join(cmd).lower() for cmd in captured)


@pytest.mark.parametrize("ac_id", ["AC-29.6"], ids=["AC-29.6"])
@pytest.mark.unit
def test_ac_29_6_gpu_probe_lavfi_size_and_missing_encoder(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.6"
    from avkit_infra.media.adapter import FFmpegAdapter

    sets = _sets()
    size = str(sets["GPU_PROBE_SIZE"])
    encoders = [str(item) for item in sets["GPU_PROBE_ENCODERS"]]
    assert encoders == ["hevc_nvenc", "hevc_amf", "hevc_qsv"]
    binary = _fake_ffmpeg(tmp_path)
    captured: list[list[str]] = []

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        captured.append(list(cmd))
        if "-encoders" in cmd:
            return _Result(
                stdout=(
                    " V..... libx265              libx265 H.265 / HEVC (codec hevc)\n"
                    " V..... hevc_amf             AMD AMF HEVC encoder (codec hevc)\n"
                )
            )
        return _Result(returncode=1)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    adapter = FFmpegAdapter(configured_path=binary)
    caps = adapter.detect_gpu()
    probe_cmds = [cmd for cmd in captured if any("color=black:s=" in part for part in cmd)]
    assert probe_cmds
    joined = " ".join(probe_cmds[0])
    assert f"color=black:s={size}" in joined
    assert caps.nvidia_nvenc is False
    assert caps.amd_amf is False
    nvenc_probe = [cmd for cmd in probe_cmds if "hevc_nvenc" in cmd]
    assert nvenc_probe == []
    amf_probe = [cmd for cmd in probe_cmds if "hevc_amf" in cmd]
    assert amf_probe


@pytest.mark.parametrize("ac_id", ["AC-29.7"], ids=["AC-29.7"])
@pytest.mark.unit
def test_ac_29_7_encode_progress_frames_and_nonzero_error(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.7"
    from avkit_core.domain.errors import FFmpegEncodeError
    from avkit_core.domain.progress import ProgressSnapshot
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    pops: list[_FakePopen] = []

    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        proc = _FakePopen(
            cmd,
            returncode=0,
            lines=[
                "frame=  120 fps=30 time=00:00:04.00 bitrate=1747.6kbits/s speed=1.25x\n"
            ],
        )
        pops.append(proc)
        return proc

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    adapter = FFmpegAdapter(configured_path=binary)
    snapshots: list[ProgressSnapshot] = []
    from avkit_core.domain.conversion import VideoEncodeOptions
    from avkit_core.domain.enums import AudioEncodeMode

    options = VideoEncodeOptions(
        codec="libx265",
        cq=25,
        nvenc_preset="p4",
        scale_height=720,
        audio_mode=AudioEncodeMode.Aac128,
        hwaccel=None,
        duration_seconds=10.0,
    )
    adapter.encode(
        tmp_path / "in.mp4",
        tmp_path / "out.mp4",
        options,
        on_progress=snapshots.append,
        should_stop=lambda: False,
    )
    assert snapshots
    assert snapshots[0].unit_label == "frames"
    assert snapshots[0].units_done == 120
    assert snapshots[0].fraction == 0.4
    assert snapshots[0].rate == 1.25
    assert snapshots[0].eta_seconds == 5
    assert isinstance(snapshots[0], ProgressSnapshot)

    def _failing(cmd: list[str], **_kwargs: object) -> _FakePopen:
        return _FakePopen(cmd, returncode=1)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _failing)
    with pytest.raises(FFmpegEncodeError):
        adapter.encode(
            tmp_path / "in.mp4",
            tmp_path / "out.mp4",
            _encode_options(),
            on_progress=lambda _snap: None,
            should_stop=lambda: False,
        )


@pytest.mark.parametrize("ac_id", ["AC-29.8"], ids=["AC-29.8"])
@pytest.mark.unit
def test_ac_29_8_cut_fastcopy_preseek_and_reencode(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.8"
    from avkit_core.domain.conversion import CutOptions
    from avkit_core.domain.enums import CutCopyMode
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    captured: list[list[str]] = []

    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        captured.append(list(cmd))
        return _FakePopen(cmd)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    adapter = FFmpegAdapter(configured_path=binary)
    adapter.cut(
        tmp_path / "in.mp4",
        tmp_path / "out.mp4",
        CutOptions(in_ms=1000, out_ms=4000, copy_mode=CutCopyMode.FastCopy),
        on_progress=lambda _snap: None,
        should_stop=lambda: False,
    )
    argv = captured[0]
    ss_at = argv.index("-ss")
    i_at = argv.index("-i")
    assert ss_at < i_at
    assert "-t" in argv
    assert argv[argv.index("-c") + 1] == "copy" or "-c:v" not in argv
    assert "copy" in argv
    captured.clear()
    adapter.cut(
        tmp_path / "in.mp4",
        tmp_path / "out.mp4",
        CutOptions(in_ms=0, out_ms=1000, copy_mode=CutCopyMode.Reencode),
        on_progress=lambda _snap: None,
        should_stop=lambda: False,
    )
    reencode = captured[0]
    assert "copy" not in reencode
    assert "-ss" in reencode
    assert "-t" in reencode


@pytest.mark.parametrize("ac_id", ["AC-29.9"], ids=["AC-29.9"])
@pytest.mark.unit
def test_ac_29_9_extract_stream_copy_map_and_container(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.9"
    from avkit_core.domain.conversion import ExtractOptions
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    captured: list[list[str]] = []

    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        captured.append(list(cmd))
        return _FakePopen(cmd)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    adapter = FFmpegAdapter(configured_path=binary)
    dest = tmp_path / "out.m4a"
    adapter.extract_stream(
        tmp_path / "in.mp4",
        dest,
        ExtractOptions(stream_index=2, output_container="m4a"),
        on_progress=lambda _snap: None,
        should_stop=lambda: False,
    )
    argv = captured[0]
    assert "-vn" in argv
    assert "-sn" in argv
    assert "-c:a" in argv
    assert argv[argv.index("-c:a") + 1] == "copy"
    assert "-map" in argv
    assert argv[argv.index("-map") + 1] == "a:2"
    assert str(dest) in argv


@pytest.mark.parametrize("ac_id", ["AC-29.10"], ids=["AC-29.10"])
@pytest.mark.unit
def test_ac_29_10_convert_remains_audio_only(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.10"
    from avkit_core.domain.progress import ConvertOptions
    from avkit_infra.media.adapter import FFmpegAdapter

    assert hasattr(FFmpegAdapter, "encode")
    binary = _fake_ffmpeg(tmp_path)
    seen: list[list[str]] = []

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        seen.append(list(cmd))
        return _Result()

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    adapter = FFmpegAdapter(configured_path=binary)
    src = tmp_path / "in.wav"
    dest = tmp_path / "out.mp3"
    src.write_bytes(b"x")
    adapter.convert(
        src,
        dest,
        ConvertOptions(codec="libmp3lame", bitrate_kbps=80, sample_rate=44100, channels=1),
    )
    argv = seen[0]
    assert "-c:a" in argv
    assert "-c:v" not in argv
    assert "libmp3lame" in argv
    assert "-b:a" in argv


@pytest.mark.parametrize("ac_id", ["AC-29.11"], ids=["AC-29.11"])
@pytest.mark.unit
def test_ac_29_11_scale_filter_even_height(ac_id: str) -> None:
    assert ac_id == "AC-29.11"
    from avkit_infra.media.adapter import even_scale_filter

    expr = even_scale_filter(721)
    assert "721" not in expr
    assert "-2" in expr
    assert even_scale_filter(720) == "scale=-2:720"
    assert "scale=1280:721" != expr


@pytest.mark.parametrize("ac_id", ["AC-29.12"], ids=["AC-29.12"])
@pytest.mark.unit
def test_ac_29_12_cancel_hook_writes_q_then_terminate(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.12"
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    holder: dict[str, _FakePopen] = {}

    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        proc = _FakePopen(cmd, hang=True, lines=["frame=   1 fps=1 time=00:00:00.01 speed=1.00x\n"])
        holder["proc"] = proc
        return proc

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    adapter = FFmpegAdapter(configured_path=binary)
    adapter.encode(
        tmp_path / "in.mp4",
        tmp_path / "out.mp4",
        _encode_options(),
        on_progress=lambda _snap: None,
        should_stop=lambda: True,
    )
    proc = holder["proc"]
    assert proc.stdin.writes
    assert proc.stdin.writes[0].strip() == "q"
    assert proc.terminated is True


@pytest.mark.parametrize("ac_id", ["AC-29.13"], ids=["AC-29.13"])
@pytest.mark.unit
def test_ac_29_13_convert_module_logger_split(ac_id: str) -> None:
    assert ac_id == "AC-29.13"
    from avkit_infra.media import adapter as media_mod

    source = Path(media_mod.__file__).read_text(encoding="utf-8")
    assert 'module="convert"' in source
    assert 'module="media"' in source
    convert_idx = source.index("def convert")
    probe_idx = source.index("def probe")
    encode_idx = source.index("def encode")
    media_logger = 'get_logger(module="media")'
    convert_logger = 'get_logger(module="convert")'
    assert media_logger in source
    assert convert_logger in source
    assert encode_idx > 0
    assert convert_idx > 0
    assert probe_idx > 0


@pytest.mark.parametrize("ac_id", ["AC-29.14"], ids=["AC-29.14"])
@pytest.mark.unit
def test_ac_29_14_conversion_job_columns_round_trip(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-29.14"
    from sqlalchemy import inspect as sa_inspect

    factory, engine = _make_uow_factory(tmp_path)
    inspector = sa_inspect(engine)
    names = [col["name"] for col in inspector.get_columns("conversion_jobs")]
    assert names == list(CONVERSION_JOB_COLUMNS)
    original = _cut_job()
    with factory() as uow:
        uow.conversion_jobs.add(original)
        uow.commit()
    with factory() as uow:
        loaded = uow.conversion_jobs.get(original.id)
    assert loaded is not None
    assert loaded.in_ms == original.in_ms
    assert loaded.out_ms == original.out_ms
    assert loaded.copy_mode is original.copy_mode
    assert loaded.preset_id is original.preset_id
    assert loaded.gpu_encoder == original.gpu_encoder
    assert loaded.input_path == original.input_path
    assert loaded.stream_index == original.stream_index
    assert loaded.width == original.width
    assert loaded.created_at == original.created_at


class _BlockingPopen:
    def __init__(self, argv: list[str]) -> None:
        self.args = list(argv)
        self.stdin = _Stdin()
        self.stderr = self
        self.returncode: int | None = None
        self.terminated = False
        self.blocked = threading.Event()
        self._closed = threading.Event()

    def readline(self) -> str:
        self.blocked.set()
        self._closed.wait(timeout=30)
        return ""

    def poll(self) -> int | None:
        return self.returncode

    def terminate(self) -> None:
        self.terminated = True
        self.returncode = 255
        self._closed.set()

    def wait(self, timeout: float | None = None) -> int:
        return self.returncode if self.returncode is not None else 0

    def close(self) -> None:
        self._closed.set()


@pytest.mark.parametrize("ac_id", ["AC-29.12"], ids=["AC-29.12-quiet"])
@pytest.mark.unit
def test_ac_29_12_cancel_polls_while_stderr_is_quiet(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.12"
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    holder: dict[str, _BlockingPopen] = {}
    stop = {"value": False}

    def _popen(cmd: list[str], **_kwargs: object) -> _BlockingPopen:
        proc = _BlockingPopen(cmd)
        holder["proc"] = proc
        return proc

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    adapter = FFmpegAdapter(configured_path=binary)
    done = threading.Event()
    error: list[BaseException] = []

    def _run() -> None:
        try:
            adapter.encode(
                tmp_path / "in.mp4",
                tmp_path / "out.mp4",
                _encode_options(),
                on_progress=lambda _snap: None,
                should_stop=lambda: stop["value"],
            )
        except Exception as exc:
            error.append(exc)
        finally:
            done.set()

    worker = threading.Thread(target=_run, daemon=True)
    worker.start()
    deadline = time.monotonic() + 2
    while "proc" not in holder and time.monotonic() < deadline:
        time.sleep(0.01)
    assert "proc" in holder
    assert holder["proc"].blocked.wait(timeout=2)
    stop["value"] = True
    assert done.wait(timeout=2)
    worker.join(timeout=1)
    assert error == []
    proc = holder["proc"]
    assert proc.stdin.writes
    assert proc.stdin.writes[0].strip() == "q"
    assert proc.terminated is True


@pytest.mark.parametrize("ac_id", ["AC-29.5"], ids=["AC-29.5-column"])
@pytest.mark.unit
def test_ac_29_5_encoder_names_use_name_column_not_description(
    ac_id: str,
) -> None:
    assert ac_id == "AC-29.5"
    from avkit_infra.media.adapter import _encoder_names

    stdout = (
        " V..... libx264              libx264 H.264 / AVC"
        " / MPEG-4 part 10 (codec h264)\n"
        " V..... libx265              libx265 H.265 / HEVC (codec hevc)\n"
        " V....D hevc_nvenc           NVIDIA NVENC hevc encoder (codec hevc)\n"
    )
    names = _encoder_names(stdout)
    assert "libx264" in names
    assert "libx265" in names
    assert "hevc_nvenc" in names
    assert "h264" not in names
    assert "hevc)" not in names
    assert "10" not in names


@pytest.mark.parametrize("ac_id", ["AC-29.7"], ids=["AC-29.7-pixfmt"])
@pytest.mark.unit
def test_ac_29_7_ten_bit_uses_p010_not_nv12(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-29.7"
    from avkit_core.domain.conversion import VideoEncodeOptions
    from avkit_core.domain.enums import AudioEncodeMode
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = _fake_ffmpeg(tmp_path)
    captured: list[list[str]] = []

    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        captured.append(list(cmd))
        return _FakePopen(cmd)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    adapter = FFmpegAdapter(configured_path=binary)
    ten = VideoEncodeOptions(
        codec="hevc_nvenc",
        cq=25,
        nvenc_preset="p4",
        scale_height=None,
        audio_mode=AudioEncodeMode.Aac128,
        hwaccel="cuda",
        bit_depth=10,
    )
    adapter.encode(
        tmp_path / "in.mp4",
        tmp_path / "out.mp4",
        ten,
        on_progress=lambda _snap: None,
        should_stop=lambda: False,
    )
    argv = captured[0]
    assert "p010" in argv
    assert "nv12" not in argv
    eight = VideoEncodeOptions(
        codec="hevc_nvenc",
        cq=25,
        nvenc_preset="p4",
        scale_height=None,
        audio_mode=AudioEncodeMode.Aac128,
        hwaccel="cuda",
        bit_depth=8,
    )
    adapter.encode(
        tmp_path / "in.mp4",
        tmp_path / "out.mp4",
        eight,
        on_progress=lambda _snap: None,
        should_stop=lambda: False,
    )
    argv8 = captured[1]
    assert "nv12" in argv8
    assert "p010" not in argv8


def _record_parent_at_spawn(seen: list[bool], output: Path):
    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        seen.append(output.parent.is_dir())
        return _FakePopen(cmd)

    return _popen


def _no_progress(_snap: object) -> None:
    return None


def _never_stop() -> bool:
    return False


@pytest.mark.parametrize("ac_id", ["AC-109.1"], ids=["AC-109.1"])
@pytest.mark.unit
def test_ac_109_1_encode_creates_missing_parents_before_ffmpeg(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-109.1"
    from avkit_infra.media.adapter import FFmpegAdapter

    output = tmp_path / "Converted" / "nested" / "out.mp4"
    seen: list[bool] = []
    monkeypatch.setattr(
        "avkit_infra.media.adapter.subprocess.Popen", _record_parent_at_spawn(seen, output)
    )
    FFmpegAdapter(configured_path=_fake_ffmpeg(tmp_path)).encode(
        tmp_path / "in.mp4", output, _encode_options(), _no_progress, _never_stop
    )
    assert seen == [True]


@pytest.mark.parametrize("ac_id", ["AC-109.2"], ids=["AC-109.2"])
@pytest.mark.unit
def test_ac_109_2_cut_creates_missing_parents_before_ffmpeg(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-109.2"
    from avkit_core.domain.conversion import CutOptions
    from avkit_core.domain.enums import CutCopyMode
    from avkit_infra.media.adapter import FFmpegAdapter

    output = tmp_path / "Converted" / "nested" / "out.mp4"
    seen: list[bool] = []
    monkeypatch.setattr(
        "avkit_infra.media.adapter.subprocess.Popen", _record_parent_at_spawn(seen, output)
    )
    FFmpegAdapter(configured_path=_fake_ffmpeg(tmp_path)).cut(
        tmp_path / "in.mp4",
        output,
        CutOptions(in_ms=0, out_ms=1000, copy_mode=CutCopyMode.FastCopy),
        _no_progress,
        _never_stop,
    )
    assert seen == [True]


@pytest.mark.parametrize("ac_id", ["AC-109.3"], ids=["AC-109.3"])
@pytest.mark.unit
def test_ac_109_3_extract_creates_missing_parents_before_ffmpeg(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-109.3"
    from avkit_core.domain.conversion import ExtractOptions
    from avkit_infra.media.adapter import FFmpegAdapter

    output = tmp_path / "Converted" / "nested" / "out.m4a"
    seen: list[bool] = []
    monkeypatch.setattr(
        "avkit_infra.media.adapter.subprocess.Popen", _record_parent_at_spawn(seen, output)
    )
    FFmpegAdapter(configured_path=_fake_ffmpeg(tmp_path)).extract_stream(
        tmp_path / "in.mp4",
        output,
        ExtractOptions(stream_index=0, output_container="m4a"),
        _no_progress,
        _never_stop,
    )
    assert seen == [True]


@pytest.mark.parametrize("ac_id", ["AC-109.4"], ids=["AC-109.4"])
@pytest.mark.unit
def test_ac_109_4_existing_folder_and_contents_survive(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-109.4"
    from avkit_infra.media.adapter import FFmpegAdapter

    folder = tmp_path / "Converted"
    folder.mkdir()
    keeper = folder / "keeper.txt"
    keeper.write_text("keep me", encoding="utf-8")
    seen: list[bool] = []
    output = folder / "out.mp4"
    monkeypatch.setattr(
        "avkit_infra.media.adapter.subprocess.Popen", _record_parent_at_spawn(seen, output)
    )
    FFmpegAdapter(configured_path=_fake_ffmpeg(tmp_path)).encode(
        tmp_path / "in.mp4", output, _encode_options(), _no_progress, _never_stop
    )
    assert seen == [True]
    assert keeper.read_text(encoding="utf-8") == "keep me"


@pytest.mark.parametrize("ac_id", ["AC-109.5"], ids=["AC-109.5"])
@pytest.mark.unit
def test_ac_109_5_blocked_folder_raises_and_never_spawns(
    ac_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert ac_id == "AC-109.5"
    from avkit_infra.media.adapter import FFmpegAdapter

    blocker = tmp_path / "blocker-file"
    blocker.write_text("a file, not a folder", encoding="utf-8")
    output = blocker / "sub" / "out.mp4"
    spawned: list[list[str]] = []

    def _popen(cmd: list[str], **_kwargs: object) -> _FakePopen:
        spawned.append(list(cmd))
        return _FakePopen(cmd)

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.Popen", _popen)
    with pytest.raises(OSError) as caught:
        FFmpegAdapter(configured_path=_fake_ffmpeg(tmp_path)).encode(
            tmp_path / "in.mp4", output, _encode_options(), _no_progress, _never_stop
        )
    assert "blocker-file" in str(caught.value)
    assert spawned == []


@pytest.mark.parametrize("ac_id", ["AC-112.4"], ids=["AC-112.4-sqlite"])
@pytest.mark.unit
def test_ac_112_4_choice_survives_sqlite_round_trip(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-112.4"
    from avkit_core.domain.enums import GpuPreference
    from avkit_core.domain.errors import ValidationError

    factory, _engine = _make_uow_factory(tmp_path)
    chosen = _cut_job(gpu_preference=GpuPreference.Software)
    unset = _cut_job(gpu_preference=None, queue_position=1)
    with factory() as uow:
        uow.conversion_jobs.add(chosen)
        uow.conversion_jobs.add(unset)
        uow.commit()
    with factory() as uow:
        loaded_chosen = uow.conversion_jobs.get(chosen.id)
        loaded_unset = uow.conversion_jobs.get(unset.id)
    assert loaded_chosen is not None
    assert loaded_chosen.gpu_preference is GpuPreference.Software
    assert loaded_unset is not None
    assert loaded_unset.gpu_preference is None
    with pytest.raises(ValidationError):
        _cut_job(gpu_preference="Software")


#: conversion_jobs as every database before MEU-112 has it.
_PRE_MEU_112_CONVERSION_JOBS = """
CREATE TABLE conversion_jobs (
    id VARCHAR(36) NOT NULL PRIMARY KEY,
    kind TEXT NOT NULL,
    input_path TEXT NOT NULL,
    output_path TEXT NOT NULL,
    display_name TEXT NOT NULL,
    preset_id TEXT,
    cq INTEGER,
    scale_height INTEGER,
    audio_mode TEXT,
    gpu_encoder TEXT,
    in_ms INTEGER,
    out_ms INTEGER,
    copy_mode TEXT,
    stream_index INTEGER,
    status TEXT NOT NULL,
    progress FLOAT NOT NULL,
    speed_bps FLOAT,
    eta_seconds INTEGER,
    file_size INTEGER,
    duration_seconds FLOAT,
    width INTEGER,
    height INTEGER,
    error_message TEXT,
    queue_position INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
)
"""


@pytest.mark.parametrize("ac_id", ["AC-112.5"], ids=["AC-112.5"])
@pytest.mark.unit
def test_ac_112_5_old_database_upgrades_in_place(ac_id: str, tmp_path: Path) -> None:
    assert ac_id == "AC-112.5"
    import sqlite3

    from sqlalchemy import inspect as sa_inspect

    from avkit_core.domain.enums import ConversionKind, ConversionStatus
    from avkit_infra.database.engine import (
        create_session_factory,
        create_sqlite_engine,
        init_schema,
    )
    from avkit_infra.database.migrations import apply_migrations
    from avkit_infra.database.unit_of_work import SqlAlchemyUnitOfWork

    def _columns(engine: object) -> list[str]:
        return [col["name"] for col in sa_inspect(engine).get_columns("conversion_jobs")]

    old_path = tmp_path / "old.db"
    job_id = str(uuid4())
    connection = sqlite3.connect(old_path)
    connection.execute(_PRE_MEU_112_CONVERSION_JOBS)
    connection.execute(
        "INSERT INTO conversion_jobs (id, kind, input_path, output_path, display_name, preset_id,"
        " cq, gpu_encoder, status, progress, queue_position, created_at, updated_at)"
        " VALUES (?, 'Compress', 'C:/in/old.mp4', 'C:/out/old_compress.mp4', 'old.mp4',"
        " 'Balanced', 25, 'hevc_nvenc', 'Done', 1.0, 0,"
        " '2026-10-01 10:00:00.000000', '2026-10-01 10:05:00.000000')",
        (job_id,),
    )
    connection.commit()
    connection.close()

    engine = create_sqlite_engine(old_path)
    init_schema(engine)
    assert _columns(engine) == list(CONVERSION_JOB_COLUMNS)
    session_factory = create_session_factory(engine)
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        loaded = uow.conversion_jobs.get(job_id)
    assert loaded is not None
    assert loaded.gpu_preference is None
    assert loaded.kind is ConversionKind.Compress
    assert loaded.status is ConversionStatus.Done
    assert loaded.input_path == Path("C:/in/old.mp4")
    assert loaded.gpu_encoder == "hevc_nvenc"
    assert loaded.cq == 25

    apply_migrations(engine)
    assert _columns(engine) == list(CONVERSION_JOB_COLUMNS)
    with SqlAlchemyUnitOfWork(session_factory) as uow:
        assert [job.id for job in uow.conversion_jobs.list_ordered()] == [job_id]

    fresh_dir = tmp_path / "fresh"
    fresh_dir.mkdir()
    _factory, fresh = _make_uow_factory(fresh_dir)
    assert _columns(fresh) == _columns(engine)

    migrated_path = tmp_path / "migrations-only.db"
    migrated = create_sqlite_engine(migrated_path)
    apply_migrations(migrated)
    assert _columns(migrated) == _columns(engine)
