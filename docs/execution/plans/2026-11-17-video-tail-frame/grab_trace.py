"""Session 93 pytest plugin and tracer: log every ffmpeg and ffprobe run the media adapter makes.

Loaded only by name, with this folder on PYTHONPATH:

    uv run --no-sync python -m pytest -p grab_trace tests/integration/test_video_real_ffmpeg.py

with PYTHONPATH=<plan folder> and AVKIT_GRAB_TRACE_LOG=<file> set. load-run.py sets both.

With AVKIT_GRAB_TRACE_LOG unset or empty the plugin does nothing, so a run without it is the
plain module. With it set, an autouse fixture, which runs before the test module's own
fixtures, uses monkeypatch to:

- replace the name `subprocess` inside `avkit_infra.media.adapter` with a proxy whose `run`
  calls the real `subprocess.run` unchanged and logs one `run` record; every other attribute
  (`TimeoutExpired`, `CompletedProcess`, `Popen`) is the real module's, and no other module's
  `subprocess` changes, so the test's own reference decodes are not traced;
- wrap `FFmpegAdapter.grab_frame` so each call logs one `call` record with the requested time,
  the seek, the box and the size of the bytes it returned, and so the `run` records made inside
  it carry that time (`t=`), per thread: the frames service grabs on its own thread.

Records are tab-separated `key=value` fields after a record type:

    armed   node=...
    run     node=... kind=packet|grab|probe|other clip=NAME t=MS arg=... rc=N count=N
            last=MS bytes=N duration=S secs=S stderr='...'
    call    node=... clip=NAME t=MS seek=input box=- bytes=N secs=S

`kind=packet` is the END_GAP read (`packet=pts_time` in the argv): `arg` is the
`-read_intervals` value, `count` the number of finite packet times on stdout and `last` the
adapter's own `_last_packet_ms` of it (`None` when there is none). `kind=grab` is a frame grab
(`image2pipe`): `arg` is the `-ss` value. `kind=probe` is `-show_format`: `duration` is the
container duration from its JSON, the clip duration the brief asks to log. `rc` is the exit
code, `timeout` or `missing`. `stderr` is the first 200 characters, as a Python repr. `clip` is
the file's base name only, so no record holds a folder path (the temp folders sit under the
home folder).

`python grab_trace.py --selftest` checks the record format, the parse back, the packet
reading and the proxy's delegation with a fake `run`; it starts no process.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterator
from decimal import Decimal, InvalidOperation
from pathlib import PurePath
from typing import Any

ENV_LOG = "AVKIT_GRAB_TRACE_LOG"
ADAPTER_MODULE = "avkit_infra.media.adapter"
STDERR_CHARS = 200
_WRITE_LOCK = threading.Lock()


def finite_times(stdout: str) -> list[Decimal]:
    """Every finite packet time on STDOUT, as the adapter's `_last_packet_ms` reads them."""
    out: list[Decimal] = []
    for line in stdout.splitlines():
        text = line.strip().rstrip(",")
        if not text:
            continue
        try:
            value = Decimal(text)
        except InvalidOperation:
            continue
        if value.is_finite():
            out.append(value)
    return out


def last_ms(stdout: str) -> int | None:
    times = finite_times(stdout)
    if not times:
        return None
    return int(max(times) * 1000)


def kind_of(argv: list[str]) -> str:
    if "packet=pts_time" in argv:
        return "packet"
    if "image2pipe" in argv:
        return "grab"
    if "-show_format" in argv:
        return "probe"
    return "other"


def value_after(argv: list[str], flag: str) -> str:
    if flag in argv and argv.index(flag) + 1 < len(argv):
        return argv[argv.index(flag) + 1]
    return "-"


def clip_of(argv: list[str], kind: str) -> str:
    if kind == "grab":
        path = value_after(argv, "-i")
    else:
        path = argv[-1] if argv else "-"
    return PurePath(path.replace("\\", "/")).name if path != "-" else "-"


def text_of(data: object) -> str:
    if isinstance(data, bytes):
        return data.decode("utf-8", "replace")
    return data if isinstance(data, str) else ""


def size_of(data: object) -> int:
    if isinstance(data, bytes):
        return len(data)
    return len(data.encode("utf-8")) if isinstance(data, str) else 0


def duration_of(stdout: str) -> str:
    try:
        value = json.loads(stdout).get("format", {}).get("duration")
    except (ValueError, AttributeError):
        return "-"
    return str(value) if value is not None else "-"


def record(kind: str, fields: dict[str, object]) -> str:
    parts = [kind]
    for key, value in fields.items():
        text = str(value).replace("\t", " ").replace("\r", " ").replace("\n", " ")
        parts.append(f"{key}={text}")
    return "\t".join(parts)


def parse(line: str) -> tuple[str, dict[str, str]]:
    """(record type, fields) from one record line."""
    head, *rest = line.rstrip("\n").split("\t")
    fields: dict[str, str] = {}
    for item in rest:
        key, _, value = item.partition("=")
        fields[key] = value
    return head, fields


def run_fields(
    node: str, t_ms: object, argv: list[str], result: object, rc: object, secs: float
) -> dict[str, object]:
    kind = kind_of(argv)
    stdout = text_of(getattr(result, "stdout", None))
    stderr = text_of(getattr(result, "stderr", None))
    fields: dict[str, object] = {
        "node": node,
        "kind": kind,
        "clip": clip_of(argv, kind),
        "t": t_ms,
        "arg": value_after(argv, "-read_intervals" if kind == "packet" else "-ss"),
        "rc": rc,
        "count": len(finite_times(stdout)) if kind == "packet" else "-",
        "last": last_ms(stdout) if kind == "packet" else "-",
        "bytes": size_of(getattr(result, "stdout", None)),
        "duration": duration_of(stdout) if kind == "probe" else "-",
        "secs": f"{secs:.3f}",
        "stderr": repr(stderr[:STDERR_CHARS]),
    }
    return fields


class Tracer:
    """One trace sink: the subprocess proxy and the grab_frame wrapper write into it."""

    def __init__(self, sink: Callable[[str], None], node: str = "-") -> None:
        self.sink = sink
        self.node = node
        self.local = threading.local()

    def emit(self, kind: str, fields: dict[str, object]) -> None:
        self.sink(record(kind, fields))

    def proxy(self, real: Any) -> Any:
        tracer = self

        class SubprocessProxy:
            def __getattr__(self, name: str) -> Any:
                return getattr(real, name)

            def run(self, *args: Any, **kwargs: Any) -> Any:
                argv = [str(a) for a in (args[0] if args else kwargs.get("args", []))]
                t_ms = getattr(tracer.local, "t_ms", "-")
                started = time.monotonic()
                try:
                    result = real.run(*args, **kwargs)
                except real.TimeoutExpired:
                    secs = time.monotonic() - started
                    tracer.emit("run", run_fields(tracer.node, t_ms, argv, None, "timeout", secs))
                    raise
                except FileNotFoundError:
                    secs = time.monotonic() - started
                    tracer.emit("run", run_fields(tracer.node, t_ms, argv, None, "missing", secs))
                    raise
                secs = time.monotonic() - started
                rc = getattr(result, "returncode", "-")
                tracer.emit("run", run_fields(tracer.node, t_ms, argv, result, rc, secs))
                return result

        return SubprocessProxy()

    def wrap_grab(self, original: Callable[..., bytes]) -> Callable[..., bytes]:
        tracer = self

        def grab_frame(adapter: Any, path: Any, time_ms: int, **kwargs: Any) -> bytes:
            tracer.local.t_ms = time_ms
            started = time.monotonic()
            data = b""
            try:
                data = original(adapter, path, time_ms, **kwargs)
                return data
            finally:
                tracer.local.t_ms = "-"
                box = kwargs.get("box")
                tracer.emit(
                    "call",
                    {
                        "node": tracer.node,
                        "clip": PurePath(str(path).replace("\\", "/")).name,
                        "t": time_ms,
                        "seek": kwargs.get("seek", "-"),
                        "box": "-" if box is None else f"{box[0]}x{box[1]}",
                        "bytes": len(data) if isinstance(data, bytes) else 0,
                        "secs": f"{time.monotonic() - started:.3f}",
                    },
                )

        return grab_frame


def file_sink(path: str) -> Callable[[str], None]:
    def sink(line: str) -> None:
        with _WRITE_LOCK, open(path, "a", encoding="utf-8", newline="\n") as handle:
            handle.write(line + "\n")

    return sink


try:
    import pytest
except ImportError:  # the selftest runs without pytest
    pytest = None  # type: ignore[assignment]

if pytest is not None:

    @pytest.fixture(autouse=True)
    def avkit_grab_trace(
        request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
    ) -> Iterator[None]:
        path = os.environ.get(ENV_LOG, "").strip()
        if not path:
            yield
            return
        import importlib

        adapter = importlib.import_module(ADAPTER_MODULE)
        tracer = Tracer(file_sink(path), request.node.nodeid)
        monkeypatch.setattr(adapter, "subprocess", tracer.proxy(subprocess))
        cls = adapter.FFmpegAdapter
        monkeypatch.setattr(cls, "grab_frame", tracer.wrap_grab(cls.grab_frame))
        tracer.emit("armed", {"node": request.node.nodeid})
        yield


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    packet = ["ffprobe.exe", "-v", "error", "-select_streams", "v:0", "-read_intervals"]
    packet += ["0.000%+62.999", "-show_entries", "packet=pts_time", "-of", "csv=p=0"]
    packet += ["C:/x/s62_video_marker0/counter.mp4"]
    grab = ["ffmpeg.exe", "-ss", "2.959", "-i", "C:\\x\\long_audio.mp4", "-frames:v", "1"]
    grab += ["-c:v", "png", "-f", "image2pipe", "pipe:1"]
    probe = ["ffprobe.exe", "-print_format", "json", "-show_format", "C:/x/counter.mp4"]
    check("packet kind", kind_of(packet) == "packet")
    check("grab kind", kind_of(grab) == "grab")
    check("probe kind", kind_of(probe) == "probe")
    check("packet arg is the interval", value_after(packet, "-read_intervals") == "0.000%+62.999")
    check("clip is the base name only", clip_of(packet, "packet") == "counter.mp4")
    check("a Windows grab path gives its base name", clip_of(grab, "grab") == "long_audio.mp4")
    check("B-frame order: the largest time wins", last_ms("1.000\n2.960\n2.920\n") == 2960)
    check("N/A and blanks skipped", len(finite_times("N/A\n\n0.040,\n")) == 1)
    check("no packet gives None", last_ms("") is None)
    check("duration from probe JSON", duration_of('{"format": {"duration": "3.000"}}') == "3.000")
    check("bad JSON gives -", duration_of("not json") == "-")
    line = record("run", {"node": "a::b[1]", "stderr": repr("x\ty\nz"), "last": None})
    head, fields = parse(line)
    check("a record parses back", head == "run" and fields["node"] == "a::b[1]")
    check("tabs and newlines never split a record", "\n" not in line and line.count("\t") == 3)
    check("None reads back as None", fields["last"] == "None")

    class Result:
        def __init__(self, stdout: object, rc: int) -> None:
            self.stdout, self.stderr, self.returncode = stdout, "", rc

    class FakeSubprocess:
        TimeoutExpired = subprocess.TimeoutExpired
        marker = "real"

        def __init__(self) -> None:
            self.calls = 0

        def run(self, argv: list[str], **kwargs: Any) -> Result:
            self.calls += 1
            if "boom" in argv:
                raise subprocess.TimeoutExpired(argv, 1)
            return Result("2.960\n" if kind_of(argv) == "packet" else b"\x89PNG", 0)

    lines: list[str] = []
    tracer = Tracer(lines.append, "n1")
    fake = FakeSubprocess()
    proxy = tracer.proxy(fake)
    check("other attributes are the real module's", proxy.marker == "real")
    check("TimeoutExpired is the real class", proxy.TimeoutExpired is subprocess.TimeoutExpired)

    def original(adapter: object, path: object, time_ms: int, **kwargs: Any) -> bytes:
        proxy.run(packet, capture_output=True)
        return proxy.run(grab, capture_output=True).stdout

    wrapped = tracer.wrap_grab(original)
    data = wrapped(object(), "C:/x/counter.mp4", 2999, seek="input", timeout_s=5.0)
    check("the wrapped grab returns the original's bytes", data == b"\x89PNG")
    check("the real run was called twice", fake.calls == 2)
    kinds = [parse(item) for item in lines]
    check("two run records then one call", [k for k, _ in kinds] == ["run", "run", "call"])
    check("run records carry the requested time", kinds[0][1]["t"] == "2999")
    check("packet count and last", kinds[0][1]["count"] == "1" and kinds[0][1]["last"] == "2960")
    check("call record bytes", kinds[2][1]["bytes"] == "4" and kinds[2][1]["seek"] == "input")
    try:
        proxy.run(["ffprobe", "boom"])
        check("a timeout is raised again", False)
    except subprocess.TimeoutExpired:
        check("a timeout is raised again", parse(lines[-1])[1]["rc"] == "timeout")
    check("outside a grab the time is -", parse(lines[-1])[1]["t"] == "-")
    print(f"grab_trace selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
