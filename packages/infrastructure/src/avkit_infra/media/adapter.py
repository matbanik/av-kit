"""MediaPort adapter: FFmpeg convert/probe/encode via subprocess."""

from __future__ import annotations

import json
import queue
import re
import shutil
import subprocess
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import structlog

from avkit_core.domain.conversion import (
    CutOptions,
    ExtractOptions,
    FFmpegBinaries,
    GPUCapabilities,
    StreamInfo,
    VideoEncodeOptions,
)
from avkit_core.domain.enums import AudioEncodeMode, CutCopyMode
from avkit_core.domain.errors import (
    FFmpegEncodeError,
    FFmpegNotFoundError,
    FilesystemError,
    MediaProbeError,
    ValidationError,
)
from avkit_core.domain.progress import ConvertOptions, MediaInfo, ProgressSnapshot

log = structlog.get_logger(module="media")
convert_log = structlog.get_logger(module="convert")

GPU_PROBE_SIZE = "256x256"
GPU_PROBE_ENCODERS = ("hevc_nvenc", "hevc_amf", "hevc_qsv")
FRAME_RE = re.compile(r"frame=\s*(\d+)")
TIME_RE = re.compile(r"time=\s*(\d+):(\d+):(\d+(?:\.\d+)?)")
SPEED_RE = re.compile(r"speed=\s*([0-9.]+)x")
ENCODER_FLAG_RE = re.compile(r"^[VASD.]{6,}$")
AUDIO_BITRATE_K = {
    AudioEncodeMode.Aac96: 96,
    AudioEncodeMode.Aac128: 128,
    AudioEncodeMode.Aac192: 192,
}


def even_scale_filter(height: int) -> str:
    """Return an even-height scale filter (`scale=-2:H`)."""
    if not isinstance(height, int) or isinstance(height, bool) or height < 1:
        raise ValidationError("scale height must be a positive int")
    even = height if height % 2 == 0 else height + 1
    return f"scale=-2:{even}"


def _ms_to_seconds(ms: int) -> str:
    text = f"{ms / 1000:.3f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _ensure_output_parent(output_path: Path) -> None:
    # FFmpeg reports a missing folder only as an exit code; a failed mkdir names the path.
    output_path.parent.mkdir(parents=True, exist_ok=True)


def _parse_rate(raw: object) -> float | None:
    if not isinstance(raw, str) or raw in {"", "0/0", "N/A"}:
        return None
    try:
        if "/" in raw:
            numerator, denominator = raw.split("/", 1)
            denom = float(denominator)
            if denom == 0:
                return None
            return float(numerator) / denom
        return float(raw)
    except ValueError:
        return None


def _optional_int(raw: object) -> int | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int):
        return raw
    if isinstance(raw, float):
        try:
            return int(raw)
        except (OverflowError, ValueError):
            return None
    if isinstance(raw, str):
        try:
            return int(raw)
        except ValueError:
            return None
    return None


def _optional_float(raw: object) -> float | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return None
    if isinstance(raw, int | float):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw)
        except ValueError:
            return None
    return None


def _language(stream: dict[str, object]) -> str | None:
    tags = stream.get("tags")
    if not isinstance(tags, dict):
        return None
    lang = tags.get("language")
    return str(lang) if lang else None


def _snapshot_from_line(
    line: str, duration_seconds: float | None = None
) -> ProgressSnapshot | None:
    frame_match = FRAME_RE.search(line)
    time_match = TIME_RE.search(line)
    speed_match = SPEED_RE.search(line)
    if frame_match is None and time_match is None and speed_match is None:
        return None
    frame = int(frame_match.group(1)) if frame_match is not None else 0
    current = None
    if time_match is not None:
        hours = float(time_match.group(1))
        minutes = float(time_match.group(2))
        seconds = float(time_match.group(3))
        current = hours * 3600 + minutes * 60 + seconds
    speed = float(speed_match.group(1)) if speed_match is not None else None
    fraction = 0.0
    if duration_seconds is not None and duration_seconds > 0 and current is not None:
        fraction = min(1.0, max(0.0, current / duration_seconds))
    eta_seconds = None
    if (
        duration_seconds is not None
        and duration_seconds > 0
        and current is not None
        and speed is not None
        and speed > 0
    ):
        remaining = max(0.0, duration_seconds - current)
        eta_seconds = int(round(remaining / speed))
    return ProgressSnapshot(
        fraction=fraction,
        units_done=frame,
        units_total=None,
        unit_label="frames",
        rate=speed,
        eta_seconds=eta_seconds,
        error=None,
    )


def _encoder_names(stdout: str) -> set[str]:
    names: set[str] = set()
    for line in stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        flags = parts[0]
        if ENCODER_FLAG_RE.match(flags) is None:
            continue
        name = parts[1]
        if re.fullmatch(r"[A-Za-z0-9_]+", name) is None:
            continue
        names.add(name)
    return names


def _audio_args(mode: AudioEncodeMode) -> list[str]:
    if mode is AudioEncodeMode.Copy:
        return ["-c:a", "copy"]
    bitrate = AUDIO_BITRATE_K[mode]
    return ["-c:a", "aac", "-b:a", f"{bitrate}k"]


def _video_args(options: VideoEncodeOptions) -> list[str]:
    args: list[str] = ["-c:v", options.codec]
    pix_fmt = "p010" if options.bit_depth is not None and options.bit_depth >= 10 else "nv12"
    args.extend(["-pix_fmt", pix_fmt])
    if "nvenc" in options.codec or "amf" in options.codec or "qsv" in options.codec:
        args.extend(["-preset", options.nvenc_preset, "-cq", str(options.cq)])
    else:
        args.extend(["-crf", str(options.cq)])
    return args


class FFmpegAdapter:
    """Subprocess FFmpeg adapter. Binary paths are constructor-injected.

    The configured path is either fixed (`configured_path`) or read on every resolution
    (`configured_source`, the live setting). Nothing is cached between calls.
    """

    def __init__(
        self,
        *,
        configured_path: Path | None = None,
        configured_source: Callable[[], Path | None] | None = None,
        bundle_path: Path | None = None,
    ) -> None:
        if configured_path is not None and configured_source is not None:
            raise ValueError("pass configured_path or configured_source, not both")
        self._configured_path = configured_path
        self._configured_source = configured_source
        self._bundle_path = bundle_path

    def _configured(self) -> Path | None:
        if self._configured_source is not None:
            return self._configured_source()
        return self._configured_path

    def _resolve_ffmpeg(self) -> Path | None:
        """RESOLVER_ORDER, per call: the configured file, the bundled file, then PATH."""
        configured = self._configured()
        if configured is not None and configured.is_file():
            return configured
        if self._bundle_path is not None and self._bundle_path.is_file():
            return self._bundle_path
        found = shutil.which("ffmpeg")
        return Path(found) if found else None

    def _resolve_ffprobe(self, ffmpeg: Path) -> Path | None:
        """FFPROBE_RULE: the sibling of the resolved ffmpeg, else PATH."""
        sibling = self._ffprobe_path(ffmpeg)
        if sibling.is_file():
            return sibling
        found = shutil.which("ffprobe")
        return Path(found) if found else None

    def ffmpeg_binaries(self) -> FFmpegBinaries | None:
        ffmpeg = self._resolve_ffmpeg()
        if ffmpeg is None:
            return None
        return FFmpegBinaries(ffmpeg=ffmpeg, ffprobe=self._resolve_ffprobe(ffmpeg))

    def _require_ffmpeg(self) -> Path:
        resolved = self._resolve_ffmpeg()
        if resolved is None:
            raise FFmpegNotFoundError("ffmpeg binary was not found") from FileNotFoundError(
                "ffmpeg binary was not found"
            )
        return resolved

    def _ffprobe_path(self, ffmpeg: Path) -> Path:
        name = "ffprobe.exe" if ffmpeg.suffix.lower() == ".exe" else "ffprobe"
        return ffmpeg.with_name(name)

    def _run(self, command: list[str]) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise FFmpegNotFoundError("ffmpeg binary was not found") from exc

    def _run_with_progress(
        self,
        command: list[str],
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
        duration_seconds: float | None = None,
    ) -> None:
        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except FileNotFoundError as exc:
            raise FFmpegNotFoundError("ffmpeg binary was not found") from exc
        stderr = proc.stderr
        stdin = proc.stdin
        lines: queue.Queue[str | None] = queue.Queue()

        def _reader() -> None:
            try:
                if stderr is None:
                    return
                while True:
                    line = stderr.readline()
                    if line == "":
                        break
                    lines.put(line)
            except OSError:
                convert_log.warning("convert.stderr_read_failed")
            finally:
                lines.put(None)

        reader = threading.Thread(target=_reader, daemon=True)
        reader.start()
        cancelled = False
        try:
            while True:
                if should_stop():
                    cancelled = True
                    if stdin is not None:
                        try:
                            stdin.write("q")
                            stdin.flush()
                        except OSError:
                            convert_log.warning("convert.stdin_write_failed")
                    proc.terminate()
                    if stderr is not None:
                        closer = getattr(stderr, "close", None)
                        if callable(closer):
                            try:
                                closer()
                            except OSError:
                                convert_log.warning("convert.stderr_close_failed")
                    try:
                        proc.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=4)
                    break
                try:
                    line = lines.get(timeout=0.05)
                except queue.Empty:
                    if proc.poll() is not None:
                        while True:
                            try:
                                leftover = lines.get_nowait()
                            except queue.Empty:
                                break
                            if leftover is None:
                                break
                            snapshot = _snapshot_from_line(leftover, duration_seconds)
                            if snapshot is not None:
                                on_progress(snapshot)
                        break
                    continue
                if line is None:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.05)
                    continue
                snapshot = _snapshot_from_line(line, duration_seconds)
                if snapshot is not None:
                    on_progress(snapshot)
        finally:
            if stdin is not None:
                closer = getattr(stdin, "close", None)
                if callable(closer):
                    try:
                        closer()
                    except OSError:
                        convert_log.warning("convert.stdin_close_failed")
            reader.join(timeout=1)
        if cancelled:
            convert_log.info("convert.cancelled", argv=command[1:4])
            return
        if proc.returncode not in (0, None):
            raise FFmpegEncodeError(f"ffmpeg exited {proc.returncode}")
        convert_log.info("convert.finished", argv=command[1:4])

    def is_available(self) -> bool:
        return self._resolve_ffmpeg() is not None

    def ffmpeg_version(self) -> str | None:
        ffmpeg = self._resolve_ffmpeg()
        if ffmpeg is None:
            return None
        result = self._run([str(ffmpeg), "-version"])
        if result.returncode != 0 or not result.stdout:
            return None
        return result.stdout.splitlines()[0]

    def convert(self, input_path: Path, output_path: Path, options: ConvertOptions) -> None:
        ffmpeg = self._require_ffmpeg()
        command = [str(ffmpeg), "-y", "-i", str(input_path), "-c:a", options.codec]
        if options.bitrate_kbps is not None:
            command.extend(["-b:a", f"{options.bitrate_kbps}k"])
        if options.sample_rate is not None:
            command.extend(["-ar", str(options.sample_rate)])
        if options.channels is not None:
            command.extend(["-ac", str(options.channels)])
        command.append(str(output_path))
        result = self._run(command)
        if result.returncode != 0:
            raise FilesystemError(result.stderr or "ffmpeg convert failed")
        log.info("media.convert", input=str(input_path), output=str(output_path))

    def probe(self, file_path: Path) -> MediaInfo:
        ffmpeg = self._require_ffmpeg()
        ffprobe = self._resolve_ffprobe(ffmpeg)
        if ffprobe is None:
            raise FFmpegNotFoundError("ffprobe binary was not found") from FileNotFoundError(
                "ffprobe binary was not found"
            )
        command = [
            str(ffprobe),
            "-print_format",
            "json",
            "-of",
            "json",
            "-show_format",
            "-show_streams",
            str(file_path),
        ]
        result = self._run(command)
        if result.returncode != 0:
            raise MediaProbeError(result.stderr or "ffprobe failed")
        try:
            payload = json.loads(result.stdout or "{}")
        except json.JSONDecodeError as exc:
            raise MediaProbeError("ffprobe returned invalid JSON") from exc
        fmt = payload.get("format") if isinstance(payload, dict) else None
        if not isinstance(fmt, dict):
            fmt = {}
        streams_raw = payload.get("streams") if isinstance(payload, dict) else None
        if not isinstance(streams_raw, list):
            streams_raw = []
        duration = _optional_float(fmt.get("duration"))
        container = fmt.get("format_name")
        video_codec = None
        audio_codec = None
        sample_rate = None
        channels = None
        width = None
        height = None
        fps = None
        bit_depth = None
        field_order = None
        parsed_streams: list[object] = []
        for stream in streams_raw:
            if not isinstance(stream, dict):
                continue
            kind = stream.get("codec_type")
            codec_name = stream.get("codec_name")
            parsed_streams.append(
                StreamInfo(
                    index=int(stream.get("index") or 0),
                    codec_type=str(kind or "unknown"),
                    codec_name=str(codec_name or "unknown"),
                    language=_language(stream),
                    channels=_optional_int(stream.get("channels")),
                    sample_rate=_optional_int(stream.get("sample_rate")),
                )
            )
            if kind == "video" and video_codec is None:
                video_codec = str(codec_name) if codec_name else None
                width = _optional_int(stream.get("width"))
                height = _optional_int(stream.get("height"))
                fps = _parse_rate(stream.get("r_frame_rate") or stream.get("avg_frame_rate"))
                bit_depth = _optional_int(stream.get("bits_per_raw_sample"))
                field_raw = stream.get("field_order")
                field_order = str(field_raw) if field_raw else None
            if kind == "audio" and audio_codec is None:
                audio_codec = str(codec_name) if codec_name else None
                sample_rate = _optional_int(stream.get("sample_rate"))
                channels = _optional_int(stream.get("channels"))
        container_text = str(container) if container else None
        return MediaInfo(
            duration=duration,
            container=container_text,
            video_codec=video_codec,
            audio_codec=audio_codec,
            sample_rate=sample_rate,
            channels=channels,
            width=width,
            height=height,
            fps=fps,
            bit_depth=bit_depth,
            field_order=field_order,
            streams=parsed_streams,
        )

    def detect_gpu(self) -> GPUCapabilities:
        ffmpeg = self._require_ffmpeg()
        convert_log.info("convert.detect_gpu")
        encoder_result = self._run([str(ffmpeg), "-hide_banner", "-encoders"])
        names = _encoder_names(encoder_result.stdout or "")
        hw_result = self._run([str(ffmpeg), "-hide_banner", "-hwaccels"])
        vulkan = "vulkan" in (hw_result.stdout or "").lower()
        nvidia = False
        amd = False
        intel = False
        for encoder in GPU_PROBE_ENCODERS:
            if encoder not in names:
                continue
            probe = [
                str(ffmpeg),
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                f"color=black:s={GPU_PROBE_SIZE}:d=1",
                "-frames:v",
                "1",
                "-c:v",
                encoder,
                "-f",
                "null",
                "-",
            ]
            result = self._run(probe)
            ok = result.returncode == 0
            if encoder == "hevc_nvenc":
                nvidia = ok
            elif encoder == "hevc_amf":
                amd = ok
            elif encoder == "hevc_qsv":
                intel = ok
        software_h265 = "libx265" in names
        software_h264 = "libx264" in names
        if nvidia:
            recommended = "hevc_nvenc"
        elif amd:
            recommended = "hevc_amf"
        elif intel:
            recommended = "hevc_qsv"
        elif software_h265:
            recommended = "libx265"
        else:
            recommended = "libx264"
        caps = GPUCapabilities(
            nvidia_nvenc=nvidia,
            amd_amf=amd,
            intel_qsv=intel,
            vulkan=vulkan,
            software_h265=software_h265,
            software_h264=software_h264,
            recommended_encoder=recommended,
            checked_at=datetime.now(UTC),
        )
        return caps

    def encode(
        self,
        input_path: Path,
        output_path: Path,
        options: VideoEncodeOptions,
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
    ) -> None:
        ffmpeg = self._require_ffmpeg()
        _ensure_output_parent(output_path)
        command = [str(ffmpeg), "-y"]
        if options.hwaccel:
            command.extend(["-hwaccel", options.hwaccel])
        command.extend(["-i", str(input_path)])
        if options.scale_height is not None:
            command.extend(["-vf", even_scale_filter(options.scale_height)])
        command.extend(_video_args(options))
        command.extend(_audio_args(options.audio_mode))
        command.append(str(output_path))
        convert_log.info("convert.encode", codec=options.codec)
        self._run_with_progress(
            command,
            on_progress,
            should_stop,
            duration_seconds=options.duration_seconds,
        )

    def cut(
        self,
        input_path: Path,
        output_path: Path,
        options: CutOptions,
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
    ) -> None:
        ffmpeg = self._require_ffmpeg()
        _ensure_output_parent(output_path)
        start = _ms_to_seconds(options.in_ms)
        duration = _ms_to_seconds(options.out_ms - options.in_ms)
        command = [str(ffmpeg), "-y", "-ss", start, "-i", str(input_path), "-t", duration]
        if options.copy_mode is CutCopyMode.FastCopy:
            command.extend(["-c", "copy"])
        else:
            command.extend(
                [
                    "-c:v",
                    "libx265",
                    "-crf",
                    "25",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                ]
            )
        command.append(str(output_path))
        convert_log.info("convert.cut", copy_mode=options.copy_mode.name)
        duration_seconds = (options.out_ms - options.in_ms) / 1000.0
        self._run_with_progress(
            command,
            on_progress,
            should_stop,
            duration_seconds=duration_seconds,
        )

    def extract_stream(
        self,
        input_path: Path,
        output_path: Path,
        options: ExtractOptions,
        on_progress: Callable[[ProgressSnapshot], None],
        should_stop: Callable[[], bool],
    ) -> None:
        ffmpeg = self._require_ffmpeg()
        _ensure_output_parent(output_path)
        command = [
            str(ffmpeg),
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-sn",
            "-c:a",
            "copy",
            "-map",
            f"a:{options.stream_index}",
            str(output_path),
        ]
        convert_log.info("convert.extract", stream_index=options.stream_index)
        self._run_with_progress(command, on_progress, should_stop)
