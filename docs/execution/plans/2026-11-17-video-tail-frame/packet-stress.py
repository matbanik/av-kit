"""Session 93 packet stress (AC-160.4, AC-160.5; D-1168, D-1169): the adapter's own END_GAP path,
many times, on a busy host.

    uv run --no-sync python <plan>/packet-stress.py --expect bad   --sequences 400
    uv run --no-sync python <plan>/packet-stress.py --expect clean --sequences 1000
    uv run --no-sync python <plan>/packet-stress.py --selftest

Each sequence is one real `FFmpegAdapter(configured_path=FFMPEG).grab_frame(clip, T,
seek="input", timeout_s=100)` call: the first grab past the last frame, the END_GAP packet read
and the retry grab, through the product code unchanged. The sequences alternate between the
module's two tail cases: `counter.mp4` at T = 2999 ms and `long_audio.mp4` at T = 3200 ms,
built from the integration module's own `CLIPS` arguments under
`C:/Temp/av-kit/video-tail-frame/stress-clips`. The name `subprocess` inside the adapter module
is replaced by grab_trace's proxy, so every process the adapter starts is logged to
`<out>/vtf-stress-<expect>.log` (removed first) and read back here.

Before the load starts: the reference is frame 74 of each clip by the module's own full decode
(`_reference`, `_pixels`), and the reference last packet time by a full ffprobe packet read with
no `-read_intervals` (2960 ms on both clips). Then one busy child per CPU (Session 90's Busy,
each stopped by its own handle) must bring the load to --threshold (85 %) within 60 s.

A sequence is `correct` when its PNG's pixels equal the reference, `empty` when it returned no
bytes, `wrong` otherwise. It carries the signal when its packet read exited non-zero or timed
out, read no packet time, or read a last time below the reference. Its interval must be the
form for the mode: `--expect bad` the open form `S%`, today's adapter; `--expect clean` the
bounded form `S%+D`, S = max(0, T - 60 s) and D = T + 60 s (D-1166).

Exit codes:

- 2: setup or premise: the load never reached the threshold, the median load during the
  sequences is below it, a reference could not be made, or a sequence made no packet read (the
  first grab gave a frame, so END_GAP was not exercised).
- 1: an interval not in the mode's form; or `--expect clean` and a bad sequence with the signal
  (the fix did not hold).
- 3: a bad sequence without the signal (Session 90 RULE-3): its records are printed.
- 4: `--expect bad` and no bad sequence: the base did not reproduce at this count.
- 0: `--expect bad`: at least one bad sequence and every one carries the signal.
  `--expect clean`: every sequence correct, every packet read good and bounded.

The output names clips by base name only, never a folder path.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType
from typing import Any

REPO = Path("P:/av-kit")
PLAN = Path(__file__).resolve().parent
OUT = Path("C:/Temp/av-kit/video-tail-frame")
LOOKBACK_MS = 60_000
CASES = (("counter.mp4", 2999), ("long_audio.mp4", 3200))
LAST_FRAME = 74


def seek_text(ms: int) -> str:
    return f"{ms // 1000}.{ms % 1000:03d}"


def expected_arg(expect: str, t_ms: int) -> str:
    start = seek_text(max(0, t_ms - LOOKBACK_MS))
    if expect == "bad":
        return f"{start}%"
    return f"{start}%+{seek_text(t_ms + LOOKBACK_MS)}"


def load_file(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"{path.name} is missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signal_of(packet: dict[str, str] | None, reference_last: int) -> str | None:
    """Why this packet read is bad, or None when it is good."""
    if packet is None:
        return "no packet read"
    if packet.get("rc") != "0":
        return f"packet read rc {packet.get('rc')}"
    if packet.get("count") == "0" or packet.get("last") in ("None", "-", None):
        return "empty packet read"
    if int(packet["last"]) < reference_last:
        return f"partial packet read: last {packet['last']} below {reference_last}"
    return None


def classify(data: bytes, reference: Any, pixels: Any) -> str:
    if not data:
        return "empty"
    try:
        return "correct" if pixels(data) == reference else "wrong"
    except Exception:  # noqa: BLE001 - an undecodable PNG is a wrong result, recorded as such
        return "wrong"


def decide(expect: str, sequences: list[dict[str, Any]]) -> tuple[int, str]:
    """(exit code, reason) from the classified sequences."""
    no_packet = [s for s in sequences if s["packets"] != 1]
    if no_packet:
        return 2, f"{len(no_packet)} sequence(s) without exactly one packet read: END_GAP premise"
    wrong_form = [s for s in sequences if not s["arg_ok"]]
    if wrong_form:
        return 1, f"{len(wrong_form)} interval(s) not in the {expect} form"
    bad = [s for s in sequences if s["outcome"] != "correct"]
    without = [s for s in bad if s["signal"] is None]
    signalled_good = [s for s in sequences if s["outcome"] == "correct" and s["signal"]]
    if without:
        return 3, f"{len(without)} bad sequence(s) without the signal (RULE-3)"
    if expect == "bad":
        if not bad:
            return 4, f"0 bad in {len(sequences)}: the base did not reproduce at this count"
        return 0, f"{len(bad)} bad in {len(sequences)}, every one with the signal"
    if bad or signalled_good:
        return 1, f"{len(bad)} bad and {len(signalled_good)} bad read(s) with a correct frame"
    return 0, f"{len(sequences)} of {len(sequences)} correct, every packet read good and bounded"


def make_clips(module: ModuleType, folder: Path) -> dict[str, Path]:
    folder.mkdir(parents=True, exist_ok=True)
    made: dict[str, Path] = {}
    for name, _ in CASES:
        made[name] = folder / name
        command = [str(module.FFMPEG), "-hide_banner", "-nostdin", "-y", *module.CLIPS[name]]
        subprocess.run([*command, str(made[name])], check=True, capture_output=True, timeout=120)
    return made


def full_last(ffprobe: Path, clip: Path, last_ms: Any) -> int | None:
    command = [str(ffprobe), "-v", "error", "-select_streams", "v:0"]
    command += ["-show_entries", "packet=pts_time", "-of", "csv=p=0", str(clip)]
    out = subprocess.run(command, capture_output=True, check=True, timeout=120, text=True).stdout
    return last_ms(out)


def run(args: argparse.Namespace) -> int:
    sys.path[:0] = [str(PLAN), str(REPO)]
    import grab_trace

    from avkit_infra.media import adapter as adapter_module

    module = load_file("vtf_real_ffmpeg", REPO / "tests/integration/test_video_real_ffmpeg.py")
    peer = load_file("vtf_load_run", PLAN / "load-run.py").load_peer()
    module._assert_pinned()
    args.out.mkdir(parents=True, exist_ok=True)
    clips = make_clips(module, args.out / "stress-clips")
    references = {n: module._pixels(module._reference(p, LAST_FRAME)) for n, p in clips.items()}
    lasts = {n: full_last(module.FFPROBE, p, grab_trace.last_ms) for n, p in clips.items()}
    print(f"reference last packet ms: {lasts}; reference frame {LAST_FRAME} sizes:")
    print("  " + ", ".join(f"{n} {ref[0]}" for n, ref in references.items()))
    if any(lasts[name] is None or lasts[name] >= t_ms for name, t_ms in CASES):
        print("SETUP FAIL: a reference last packet is missing or not before T")
        return 2
    log = args.out / f"vtf-stress-{args.expect}.log"
    log.unlink(missing_ok=True)
    lines: list[str] = []
    file_sink = grab_trace.file_sink(str(log))

    def sink(line: str) -> None:
        lines.append(line)
        file_sink(line)

    tracer = grab_trace.Tracer(sink, "packet-stress")
    adapter_module.subprocess = tracer.proxy(subprocess)
    grab = tracer.wrap_grab(adapter_module.FFmpegAdapter.grab_frame)
    media = adapter_module.FFmpegAdapter(configured_path=module.FFMPEG)

    peer.host_load_wait()
    busy = peer.Busy()
    sampler = peer.Sampler(3.0)
    sequences: list[dict[str, Any]] = []
    try:
        if not busy.start(args.children or (os.cpu_count() or 1)):
            return 2
        deadline = time.monotonic() + 60
        load = peer.sample(2.0)
        while load < args.threshold and time.monotonic() < deadline:
            load = peer.sample(2.0)
        print(f"load before the sequences: {load} %")
        if load < args.threshold:
            print(f"SETUP FAIL: load {load} % never reached {args.threshold} % in 60 s")
            return 2
        sampler.start()
        for index in range(args.sequences):
            name, t_ms = CASES[index % len(CASES)]
            tracer.node = f"seq-{index + 1}"
            first = len(lines)
            data = grab(media, clips[name], t_ms, seek="input", timeout_s=100.0)
            records = [grab_trace.parse(line) for line in lines[first:]]
            packets = [f for head, f in records if head == "run" and f.get("kind") == "packet"]
            packet = packets[0] if packets else None
            sequences.append(
                {
                    "index": index + 1,
                    "clip": name,
                    "t": t_ms,
                    "outcome": classify(data, references[name], module._pixels),
                    "signal": signal_of(packet, lasts[name]),
                    "packets": len(packets),
                    "arg_ok": packet is not None
                    and packet.get("arg") == expected_arg(args.expect, t_ms),
                    "records": records,
                }
            )
    finally:
        sampler.done.set()
        if sampler.is_alive():
            sampler.join(timeout=10)
        left = busy.stop()
    if left:
        print(f"FAIL: {left} busy process(es) left")
        return 1
    samples = sampler.samples
    median = statistics.median(samples) if samples else 0.0
    if samples:
        print(
            f"load during: n={len(samples)} min={min(samples)} median={median} max={max(samples)}"
        )
    tally = collections.Counter(
        (s["clip"], s["outcome"], s["signal"] or "good read") for s in sequences
    )
    for (clip, outcome, signal), count in sorted(tally.items()):
        print(f"  {count:5d}  {clip} {outcome}; {signal}")
    shown = 0
    for s in sequences:
        if (s["outcome"] != "correct" or s["signal"]) and shown < 20:
            shown += 1
            print(f"  seq {s['index']} {s['clip']} t={s['t']}: {s['outcome']}; {s['signal']}")
            for head, fields in s["records"]:
                print(
                    f"    {head} {fields.get('kind', 'call')} arg={fields.get('arg', '-')}"
                    f" rc={fields.get('rc', '-')} count={fields.get('count', '-')}"
                    f" last={fields.get('last', '-')} bytes={fields.get('bytes')}"
                    f" secs={fields.get('secs')} stderr={fields.get('stderr', '-')}"
                )
    if not samples or median < args.threshold:
        print(f"SETUP FAIL: median load {median} is below {args.threshold} (exit 2)")
        return 2
    code, reason = decide(args.expect, sequences)
    print(f"RESULT: {reason} (exit {code}); trace {log.name}")
    return code


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    check("bad form at 2999", expected_arg("bad", 2999) == "0.000%")
    check("clean form at 2999", expected_arg("clean", 2999) == "0.000%+62.999")
    check("clean form at 3200", expected_arg("clean", 3200) == "0.000%+63.200")
    check("clean form at 89999", expected_arg("clean", 89_999) == "29.999%+149.999")
    good = {"rc": "0", "count": "75", "last": "2960"}
    check("a full read is good", signal_of(good, 2960) is None)
    check("an empty read is the signal", signal_of({**good, "count": "0", "last": "None"}, 2960))
    check(
        "a partial read is the signal",
        "partial" in (signal_of({**good, "last": "1560"}, 2960) or ""),
    )
    check(
        "a timeout is the signal", "timeout" in (signal_of({**good, "rc": "timeout"}, 2960) or "")
    )
    check("no packet read is the signal", signal_of(None, 2960) == "no packet read")
    ref = ((320, 240), b"x")
    check("empty bytes", classify(b"", ref, lambda d: ref) == "empty")
    check("same pixels", classify(b"png", ref, lambda d: ref) == "correct")
    check("other pixels", classify(b"png", ref, lambda d: ((320, 240), b"y")) == "wrong")

    def boom(data: bytes) -> Any:
        raise OSError("not a PNG")

    check("an undecodable PNG is wrong", classify(b"junk", ref, boom) == "wrong")

    def seq(outcome: str, signal: str | None, packets: int = 1, arg_ok: bool = True) -> dict:
        return {"outcome": outcome, "signal": signal, "packets": packets, "arg_ok": arg_ok}

    ok_run = [seq("correct", None)] * 4
    check("bad: none bad is 4", decide("bad", ok_run)[0] == 4)
    check("bad: a signalled empty is 0", decide("bad", [*ok_run, seq("empty", "empty")])[0] == 0)
    check(
        "bad: a bad without the signal is 3", decide("bad", [*ok_run, seq("wrong", None)])[0] == 3
    )
    check("bad: a wrong form is 1", decide("bad", [seq("correct", None, arg_ok=False)])[0] == 1)
    check("clean: all correct is 0", decide("clean", ok_run)[0] == 0)
    check("clean: a signalled bad is 1", decide("clean", [*ok_run, seq("empty", "empty")])[0] == 1)
    check(
        "clean: a bad read with a good frame is 1",
        decide("clean", [seq("correct", "partial")])[0] == 1,
    )
    check("clean: a bad without the signal is 3", decide("clean", [seq("wrong", None)])[0] == 3)
    check("no packet read is 2", decide("clean", [seq("correct", None, packets=0)])[0] == 2)
    check("two packet reads is 2", decide("clean", [seq("correct", None, packets=2)])[0] == 2)
    check(
        "the integration module exists",
        (REPO / "tests/integration/test_video_real_ffmpeg.py").is_file(),
    )
    check("grab_trace sits beside this file", (PLAN / "grab_trace.py").is_file())
    check("load-run.py sits beside this file", (PLAN / "load-run.py").is_file())
    source = (REPO / "tests/integration/test_video_real_ffmpeg.py").read_text(encoding="utf-8")
    for name, _ in CASES:
        check(f"CLIPS has {name}", f'"{name}": [' in source)
    for helper in ("def _reference(", "def _pixels(", "def _assert_pinned("):
        check(f"the module has {helper[4:-1]}", helper in source)
    print(f"packet-stress selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--expect", choices=("bad", "clean"))
    parser.add_argument("--sequences", type=int, default=0, help="0: 400 for bad, 1000 for clean")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--threshold", type=float, default=85.0)
    parser.add_argument("--children", type=int, default=0, help="0 means os.cpu_count()")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.expect is None:
        parser.print_help()
        return 2
    args.sequences = args.sequences or (400 if args.expect == "bad" else 1000)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
