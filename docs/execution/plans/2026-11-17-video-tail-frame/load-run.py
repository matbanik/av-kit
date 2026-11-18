"""Session 93 load run (AC-160.6, AC-160.9; D-1168, D-1169): the real-ffmpeg module, traced, on a
busy host.

    uv run --no-sync python <plan>/load-run.py --mode base --runs 1
    uv run --no-sync python <plan>/load-run.py --mode green --runs 5

Session 90's `2026-11-17-test-run-reliability/load-run.py` is imported by path and used
unchanged: its host-load wait (Session 81 RULE-2), its busy children (one per CPU, each
interpreter held and stopped by its own handle, never by name), its load sampler and its
verdict. This file adds only what differs:

- FILES is `tests/integration/test_video_real_ffmpeg.py`;
- each run loads the plan's `grab_trace` plugin (`-p grab_trace`, with this folder on
  PYTHONPATH) and writes its trace to `<out>/vtf-trace-<mode>-<i>.log`, removed first, so a
  run's trace holds that run only;
- receipts are `<out>/vtf-load-run-<mode>-<i>.txt`;
- `--mode base` is the row 2 receipt: the module may fail at base, so the exit is 0 whenever
  the load held and no busy process was left, and trace-check.py reads the failures;
  `--mode green` is Session 90's verdict: every run passed and the median load during the runs
  is at least --threshold (85 %).

Exit 2 is a setup failure (the load never reached the threshold in 60 s, or a busy child did
not start); exit 1 is a failed verdict or a busy process left. --kill-check runs Session 90's
own kill check. --selftest checks FILES, the argv, the environment and the receipt names and
starts no process. The output names files by base name only, never a path under the home
folder.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path
from types import ModuleType

REPO = Path("P:/av-kit")
PLAN = Path(__file__).resolve().parent
PEER = REPO / "docs/execution/plans/2026-11-17-test-run-reliability/load-run.py"
FILES = ("tests/integration/test_video_real_ffmpeg.py",)
OUT = Path("C:/Temp/av-kit/video-tail-frame")
TRACE_ENV = "AVKIT_GRAB_TRACE_LOG"


def load_peer() -> ModuleType:
    spec = importlib.util.spec_from_file_location("trr_load_run", PEER)
    if spec is None or spec.loader is None:
        raise ImportError("Session 90 load-run.py is missing")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def receipt_name(mode: str, index: int) -> str:
    return f"vtf-load-run-{mode}-{index}.txt"


def trace_name(mode: str, index: int) -> str:
    return f"vtf-trace-{mode}-{index}.log"


def pytest_argv(python: str) -> list[str]:
    return [python, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider"] + [
        "-p",
        "grab_trace",
        *FILES,
    ]


def run_env(base: dict[str, str], trace: Path) -> dict[str, str]:
    env = dict(base)
    env.pop("ELECTRON_RUN_AS_NODE", None)
    env["PYTHONPATH"] = str(PLAN)
    env["PYTHONIOENCODING"] = "utf-8"
    env[TRACE_ENV] = str(trace)
    return env


def run(args: argparse.Namespace, peer: ModuleType) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    peer.host_load_wait()
    busy = peer.Busy()
    sampler = peer.Sampler(3.0)
    results: list[int] = []
    try:
        if not busy.start(args.children or (os.cpu_count() or 1)):
            return 2
        deadline = time.monotonic() + 60
        load = peer.sample(2.0)
        while load < args.threshold and time.monotonic() < deadline:
            load = peer.sample(2.0)
        print(f"load before the runs: {load} %")
        if load < args.threshold:
            print(f"SETUP FAIL: load {load} % never reached {args.threshold} % in 60 s")
            return 2
        sampler.start()
        for i in range(1, args.runs + 1):
            receipt = args.out / receipt_name(args.mode, i)
            trace = args.out / trace_name(args.mode, i)
            trace.unlink(missing_ok=True)
            started = time.monotonic()
            with receipt.open("wb") as handle:
                code = subprocess.run(
                    pytest_argv(sys.executable),
                    cwd=REPO,
                    env=run_env(dict(os.environ), trace),
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                    timeout=args.run_timeout,
                    check=False,
                ).returncode
            results.append(code)
            text = receipt.read_bytes().decode("utf-8", "replace")
            took = round(time.monotonic() - started)
            print(
                f"run {i}: exit {code} in {took} s :: {peer.last_line(text)}"
                f" -> {receipt.name}, {trace.name}"
            )
    except subprocess.TimeoutExpired:
        results.append(124)
        print(f"run {len(results)}: timed out after {args.run_timeout} s")
    except OSError as exc:
        print(f"SETUP FAIL: {type(exc).__name__}")
        return 2
    finally:
        sampler.done.set()
        if sampler.is_alive():
            sampler.join(timeout=10)
        left = busy.stop()
    if left:
        print(f"FAIL: {left} busy process(es) left")
        return 1
    samples = sampler.samples
    if samples:
        print(
            f"load during the runs: n={len(samples)} min={min(samples)} "
            f"median={statistics.median(samples)} max={max(samples)}"
        )
    if args.mode == "base":
        if not samples or statistics.median(samples) < args.threshold:
            print("FAIL: the base run's median load is below the threshold")
            return 1
        print(f"BASE: {len(results)} run(s), exit codes {results}; trace-check.py reads them")
        return 0
    code, reason = peer.verdict(results, samples, args.threshold)
    print(("PASS: " if code == 0 else "FAIL: ") + reason)
    return code


def selftest(peer: ModuleType) -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    check(
        "one file: the real-ffmpeg module",
        FILES == ("tests/integration/test_video_real_ffmpeg.py",),
    )
    argv = pytest_argv("py")
    check("the plugin is loaded by name", argv[argv.index("grab_trace") - 1] == "-p")
    check(
        "no cache provider, quiet, short tracebacks",
        argv[3:7] == ["-q", "--tb=short", "-p", "no:cacheprovider"],
    )
    check("the module is the last argument", argv[-1] == FILES[0])
    trace = OUT / trace_name("green", 2)
    env = run_env({"ELECTRON_RUN_AS_NODE": "1", "PATH": "x"}, trace)
    check("the plan folder is on PYTHONPATH", env["PYTHONPATH"] == str(PLAN))
    check("the trace file is set", env[TRACE_ENV].endswith("vtf-trace-green-2.log"))
    check("ELECTRON_RUN_AS_NODE is cleared", "ELECTRON_RUN_AS_NODE" not in env)
    check("PATH is kept", env["PATH"] == "x")
    check("receipt names", receipt_name("base", 1) == "vtf-load-run-base-1.txt")
    check("the plugin file sits beside this one", (PLAN / "grab_trace.py").is_file())
    check("Session 90's load-run.py is the peer", PEER.is_file())
    for name in ("host_load_wait", "Busy", "Sampler", "sample", "verdict", "last_line"):
        check(f"the peer has {name}", hasattr(peer, name))
    check("the peer verdict passes five clean runs", peer.verdict([0] * 5, [90.0], 85)[0] == 0)
    check("the peer verdict fails a failed run", peer.verdict([0, 1, 0, 0, 0], [90.0], 85)[0] == 1)
    print(f"load-run selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--kill-check", action="store_true")
    parser.add_argument("--mode", choices=("base", "green"), default="green")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=85.0)
    parser.add_argument("--children", type=int, default=0, help="0 means os.cpu_count()")
    parser.add_argument("--run-timeout", type=float, default=1800.0)
    args = parser.parse_args()
    peer = load_peer()
    if args.selftest:
        return selftest(peer)
    if args.kill_check:
        return peer.kill_check(args)
    return run(args, peer)


if __name__ == "__main__":
    sys.exit(main())
