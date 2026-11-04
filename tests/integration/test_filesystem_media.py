"""MEU-8 filesystem and media adapter integration tests."""

from __future__ import annotations

import inspect
import json
import math
import os
import wave
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FILESYSTEM_PORT_METHODS = (
    "write_text_atomic",
    "write_progress_export",
    "ensure_channel_dirs",
    "write_audio_wav",
    "read_text",
)
COMPILE_PARENT_NAMES = frozenset({"raw", "compiled"})
COMPILE_SUFFIX = ".md"
PROGRESS_EXPORT_FILENAME = "progress.json"
PROGRESS_EXPORT_KEY = "video_ids_done"


@pytest.mark.integration
def test_ac_8_1_write_text_atomic_uses_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.domain.errors import FilesystemError
    from avkit_infra.filesystem.writer import FilesystemAdapter

    adapter = FilesystemAdapter()
    target = tmp_path / "raw" / "video.md"
    target.parent.mkdir()
    seen: list[tuple[Path, Path]] = []
    real_replace = os.replace

    def _tracking_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        seen.append((Path(src), Path(dst)))
        real_replace(src, dst)

    monkeypatch.setattr("avkit_infra.filesystem.writer.os.replace", _tracking_replace)
    adapter.write_text_atomic(target, "hello")
    assert target.read_text(encoding="utf-8") == "hello"
    assert seen
    src, dst = seen[0]
    assert src.parent == target.parent
    assert dst == target

    def _failing_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("avkit_infra.filesystem.writer.os.replace", _failing_replace)
    with pytest.raises(FilesystemError):
        adapter.write_text_atomic(target, "nope")
    assert target.read_text(encoding="utf-8") == "hello"


@pytest.mark.integration
def test_ac_8_2_progress_export_has_no_reader(tmp_path: Path) -> None:
    from avkit_infra.filesystem.writer import FilesystemAdapter

    adapter = FilesystemAdapter()
    adapter.write_progress_export(tmp_path, ["aaa", "bbb"])
    payload = json.loads((tmp_path / PROGRESS_EXPORT_FILENAME).read_text(encoding="utf-8"))
    assert payload == {PROGRESS_EXPORT_KEY: ["aaa", "bbb"]}
    names = {name for name in dir(adapter) if not name.startswith("_")}
    forbidden = {
        name
        for name in names
        if "progress" in name.lower() and name != "write_progress_export"
    }
    assert forbidden == set()
    assert not hasattr(adapter, "read_progress")
    assert not hasattr(adapter, "load_progress")
    assert not hasattr(adapter, "resume")


@pytest.mark.integration
def test_ac_8_3_ensure_channel_dirs_creates_raw_and_compiled(tmp_path: Path) -> None:
    from avkit_infra.filesystem.writer import FilesystemAdapter

    output_dir = tmp_path / "channel"
    FilesystemAdapter().ensure_channel_dirs(output_dir)
    assert (output_dir / "raw").is_dir()
    assert (output_dir / "compiled").is_dir()


@pytest.mark.integration
def test_ac_8_4_write_audio_wav_stdlib_wave(tmp_path: Path) -> None:
    from avkit_core.domain.errors import ValidationError
    from avkit_infra.filesystem.writer import FilesystemAdapter

    adapter = FilesystemAdapter()
    int16_path = tmp_path / "int16.wav"
    samples_i16 = np.array([0, 16384, -16384], dtype=np.int16)
    adapter.write_audio_wav(int16_path, samples_i16, 24000)
    with wave.open(str(int16_path), "rb") as handle:
        frames = handle.readframes(handle.getnframes())
        assert handle.getframerate() == 24000
        assert handle.getnchannels() == 1
        assert handle.getsampwidth() == 2
    round_trip = np.frombuffer(frames, dtype="<i2")
    np.testing.assert_array_equal(round_trip, samples_i16)

    float_path = tmp_path / "float.wav"
    samples_f32 = np.array([0.0, 1.0, -1.0], dtype=np.float32)
    adapter.write_audio_wav(float_path, samples_f32, 24000)
    with wave.open(str(float_path), "rb") as handle:
        raw = handle.readframes(handle.getnframes())
    decoded = np.frombuffer(raw, dtype="<i2")
    assert decoded[0] == 0
    assert decoded[1] == 32767
    assert decoded[2] == -32768

    with pytest.raises(ValidationError):
        adapter.write_audio_wav(tmp_path / "bad.wav", np.zeros((2, 2), dtype=np.float32), 24000)

    nan_path = tmp_path / "nan.wav"
    with pytest.raises(ValidationError):
        adapter.write_audio_wav(
            nan_path, np.array([0.0, math.nan], dtype=np.float32), 24000
        )
    assert not nan_path.exists()
    inf_path = tmp_path / "inf.wav"
    with pytest.raises(ValidationError):
        adapter.write_audio_wav(
            inf_path, np.array([0.0, math.inf], dtype=np.float32), 24000
        )
    assert not inf_path.exists()
    source = (
        REPO_ROOT
        / "packages"
        / "infrastructure"
        / "src"
        / "avkit_infra"
        / "filesystem"
        / "writer.py"
    ).read_text(encoding="utf-8")
    assert "soundfile" not in source


@pytest.mark.integration
def test_ac_8_5_read_text_compile_only_and_bounded(tmp_path: Path) -> None:
    from avkit_core.domain.errors import FilesystemError
    from avkit_core.ports.filesystem import FilesystemPort
    from avkit_infra.filesystem.writer import FilesystemAdapter

    adapter = FilesystemAdapter()
    signature = inspect.signature(adapter.read_text)
    assert list(signature.parameters) == ["path", "max_bytes"]
    assert signature.parameters["max_bytes"].kind is inspect.Parameter.KEYWORD_ONLY
    proto = inspect.signature(FilesystemPort.read_text)
    assert proto.parameters["max_bytes"].kind is inspect.Parameter.KEYWORD_ONLY

    raw = tmp_path / "raw"
    compiled = tmp_path / "compiled"
    raw.mkdir()
    compiled.mkdir()
    allowed = raw / "video.md"
    allowed.write_text("ok", encoding="utf-8")
    assert adapter.read_text(allowed, max_bytes=16) == "ok"
    compiled_file = compiled / "video.md"
    compiled_file.write_text("compiled", encoding="utf-8")
    assert adapter.read_text(compiled_file, max_bytes=32) == "compiled"

    secrets = tmp_path / "secrets.txt"
    secrets.write_text("secret", encoding="utf-8")
    traversal = raw / ".." / "secrets.txt"
    with pytest.raises(FilesystemError):
        adapter.read_text(traversal, max_bytes=1024)

    txt = raw / "notes.txt"
    txt.write_text("nope", encoding="utf-8")
    with pytest.raises(FilesystemError):
        adapter.read_text(txt, max_bytes=1024)

    oversize = raw / "big.md"
    oversize.write_text("abcdef", encoding="utf-8")
    with pytest.raises(FilesystemError):
        adapter.read_text(oversize, max_bytes=3)

    tts_like = tmp_path / "input.txt"
    tts_like.write_text("tts source", encoding="utf-8")
    with pytest.raises(FilesystemError):
        adapter.read_text(tts_like, max_bytes=1024)

    with pytest.raises(TypeError):
        adapter.read_text(allowed, 16)


MEDIA_PORT_METHODS = (
    "is_available",
    "ffmpeg_version",
    "ffmpeg_binaries",  # TA-4 (Session 33, MEU-78)
    "convert",
    "probe",
    "detect_gpu",
    "encode",
    "cut",
    "extract_stream",
)
CONVERT_OPTIONS_FIELDS = ("codec", "bitrate_kbps", "sample_rate", "channels")
MEDIA_INFO_FIELDS = (
    "duration",
    "container",
    "video_codec",
    "audio_codec",
    "sample_rate",
    "channels",
)


def _mp3_options():
    from avkit_core.domain.progress import ConvertOptions

    return ConvertOptions(codec="libmp3lame", bitrate_kbps=80, sample_rate=44100, channels=1)


@pytest.mark.integration
def test_ac_8_6_is_available_probe_order_and_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.media.adapter import FFmpegAdapter

    configured = tmp_path / "configured" / "ffmpeg.exe"
    configured.parent.mkdir()
    configured.write_text("fake", encoding="utf-8")
    bundle = tmp_path / "bundle" / "ffmpeg.exe"
    which_calls: list[str] = []

    def _which(name: str) -> str | None:
        which_calls.append(name)
        raise AssertionError("PATH must not be used when configured file exists")

    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", _which)
    adapter = FFmpegAdapter(configured_path=configured, bundle_path=bundle)
    assert adapter.is_available() is True
    assert adapter.is_available() is True
    assert which_calls == []

    path_adapter = FFmpegAdapter()
    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", lambda name: None)
    assert path_adapter.is_available() is False
    count = {"n": 0}

    def _count_which(name: str) -> str | None:
        count["n"] += 1
        return None

    cached = FFmpegAdapter()
    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", _count_which)
    assert cached.is_available() is False
    assert cached.is_available() is False
    assert count["n"] == 2  # TA-2 (Session 33, MEU-78)

    bundle.parent.mkdir(parents=True, exist_ok=True)
    bundle.write_text("fake", encoding="utf-8")
    missing_configured = tmp_path / "missing-configured" / "ffmpeg.exe"
    path_hits: list[str] = []

    def _which_should_not_run(name: str) -> str | None:
        path_hits.append(name)
        return str(tmp_path / "path" / "ffmpeg")

    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", _which_should_not_run)
    bundle_adapter = FFmpegAdapter(
        configured_path=missing_configured, bundle_path=bundle
    )
    assert bundle_adapter.is_available() is True
    assert path_hits == []

    missing_bundle = tmp_path / "missing-bundle" / "ffmpeg.exe"
    path_ffmpeg = tmp_path / "from-path" / "ffmpeg"
    path_ffmpeg.parent.mkdir()
    path_ffmpeg.write_text("fake", encoding="utf-8")
    monkeypatch.setattr(
        "avkit_infra.media.adapter.shutil.which", lambda name: str(path_ffmpeg)
    )
    path_fallback = FFmpegAdapter(
        configured_path=missing_configured, bundle_path=missing_bundle
    )
    assert path_fallback.is_available() is True


@pytest.mark.integration
def test_ac_8_7_missing_binary_raises_ffmpeg_not_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.domain.errors import FFmpegNotFoundError
    from avkit_core.domain.progress import ConvertOptions
    from avkit_infra.media.adapter import FFmpegAdapter

    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", lambda name: None)
    adapter = FFmpegAdapter()
    assert adapter.is_available() is False
    options = ConvertOptions(codec="libmp3lame", bitrate_kbps=80, sample_rate=44100, channels=1)
    with pytest.raises(FFmpegNotFoundError) as convert_info:
        adapter.convert(tmp_path / "in.wav", tmp_path / "out.mp3", options)
    assert isinstance(convert_info.value.__cause__, FileNotFoundError)
    with pytest.raises(FFmpegNotFoundError) as probe_info:
        adapter.probe(tmp_path / "in.wav")
    assert isinstance(probe_info.value.__cause__, FileNotFoundError)
    with pytest.raises(FFmpegNotFoundError):
        raise FFmpegNotFoundError("missing")
    try:
        adapter.convert(tmp_path / "in.wav", tmp_path / "out.mp3", options)
    except Exception as exc:
        assert type(exc) is FFmpegNotFoundError
        assert type(exc) is not FileNotFoundError


@pytest.mark.integration
def test_ac_8_8_ffmpeg_version_parses_first_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = tmp_path / "ffmpeg.exe"
    binary.write_text("fake", encoding="utf-8")
    captured: list[list[str]] = []

    class _Result:
        def __init__(self, stdout: str) -> None:
            self.stdout = stdout
            self.returncode = 0

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        captured.append(list(cmd))
        return _Result("ffmpeg version 7.0.2 Copyright\nconfiguration: --enable-gpl\n")

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    adapter = FFmpegAdapter(configured_path=binary)
    assert adapter.ffmpeg_version() == "ffmpeg version 7.0.2 Copyright"
    assert captured[0][1] == "-version"
    assert not hasattr(adapter, "get_version")
    missing = FFmpegAdapter()
    monkeypatch.setattr("avkit_infra.media.adapter.shutil.which", lambda name: None)
    assert missing.ffmpeg_version() is None


@pytest.mark.integration
def test_ac_8_9_convert_argv_maps_convert_options(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = tmp_path / "ffmpeg.exe"
    binary.write_text("fake", encoding="utf-8")
    seen: list[list[str]] = []

    class _Result:
        returncode = 0
        stdout = ""
        stderr = ""

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        seen.append(list(cmd))
        return _Result()

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    adapter = FFmpegAdapter(configured_path=binary)
    src = tmp_path / "in.wav"
    dest = tmp_path / "out.mp3"
    src.write_bytes(b"x")
    adapter.convert(src, dest, _mp3_options())
    argv = seen[0]
    assert argv[0] == str(binary)
    assert "-y" in argv
    assert argv[argv.index("-c:a") + 1] == "libmp3lame"
    assert argv[argv.index("-b:a") + 1] == "80k"
    assert argv[argv.index("-ar") + 1] == "44100"
    assert argv[argv.index("-ac") + 1] == "1"
    assert str(src) in argv
    assert str(dest) in argv


@pytest.mark.integration
def test_ac_8_10_probe_maps_ffprobe_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from avkit_core.domain.progress import MEDIA_INFO_FIELDS, MediaInfo
    from avkit_infra.media.adapter import FFmpegAdapter

    binary = tmp_path / "ffmpeg.exe"
    binary.write_text("fake", encoding="utf-8")
    # FIXTURE_REPAIRS (g) (Session 33, MEU-78): FFPROBE_RULE reads the sibling ffprobe.
    (tmp_path / "ffprobe.exe").write_text("fake", encoding="utf-8")
    payload = {
        "format": {"duration": "1.5", "format_name": "mp3"},
        "streams": [
            {
                "codec_type": "audio",
                "codec_name": "mp3",
                "sample_rate": "44100",
                "channels": 1,
            }
        ],
    }

    class _Result:
        def __init__(self) -> None:
            self.returncode = 0
            self.stdout = json.dumps(payload)
            self.stderr = ""

    def _run(cmd: list[str], **_kwargs: object) -> _Result:
        assert "-print_format" in cmd
        assert "json" in cmd
        assert "-show_format" in cmd
        assert "-show_streams" in cmd
        assert cmd[0].endswith("ffprobe.exe") or cmd[0].endswith("ffprobe")
        return _Result()

    monkeypatch.setattr("avkit_infra.media.adapter.subprocess.run", _run)
    adapter = FFmpegAdapter(configured_path=binary)
    info = adapter.probe(tmp_path / "clip.mp3")
    assert isinstance(info, MediaInfo)
    assert info.duration == 1.5
    assert info.container == "mp3"
    assert info.video_codec is None
    assert info.audio_codec == "mp3"
    assert info.sample_rate == 44100
    assert info.channels == 1
    assert "codec" not in MEDIA_INFO_FIELDS
    assert not hasattr(info, "codec")


@pytest.mark.integration
def test_ac_8_11_no_conversion_job_and_mocked_subprocess() -> None:
    from avkit_infra.database import models as models_mod
    from avkit_infra.media import adapter as media_mod

    assert not hasattr(models_mod, "ConversionJob")
    assert not hasattr(media_mod, "ConversionJob")
    source = Path(media_mod.__file__).read_text(encoding="utf-8")
    assert "ConversionJob" not in source
    assert "subprocess" in source


@pytest.mark.integration
def test_ac_8_12_port_signatures_match_frozen_protocols() -> None:
    from avkit_core.ports.filesystem import FilesystemPort
    from avkit_core.ports.media import MediaPort
    from avkit_infra.filesystem.writer import FilesystemAdapter
    from avkit_infra.media.adapter import FFmpegAdapter

    for name in FILESYSTEM_PORT_METHODS:
        proto = inspect.signature(getattr(FilesystemPort, name))
        impl = inspect.signature(getattr(FilesystemAdapter, name))
        proto_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in proto.parameters.items()
        ]
        impl_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in impl.parameters.items()
        ]
        assert impl_params == proto_params, name
        assert impl.return_annotation == proto.return_annotation
    for name in MEDIA_PORT_METHODS:
        proto = inspect.signature(getattr(MediaPort, name))
        impl = inspect.signature(getattr(FFmpegAdapter, name))
        proto_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in proto.parameters.items()
        ]
        impl_params = [
            (key, param.kind, param.annotation, param.default)
            for key, param in impl.parameters.items()
        ]
        assert impl_params == proto_params, name
        assert impl.return_annotation == proto.return_annotation
    read = inspect.signature(FilesystemAdapter.read_text)
    assert read.parameters["max_bytes"].kind is inspect.Parameter.KEYWORD_ONLY
    assert CONVERT_OPTIONS_FIELDS
    assert not hasattr(FFmpegAdapter, "get_version")

