"""Session 104 copy (of Session 102's) of Session 90's load run; only host-wait.py
loads it, for host_load_wait().

Session 90 load run (AC-5, D-1120): the three files that reach the waits pass three times on
a busy host.

    uv run --no-sync python <plan>/load-run.py --out C:/Temp/av-kit/test-run-reliability
    uv run --no-sync python <plan>/load-run.py --kill-check --children 2

1. Host-load wait (Session 81 RULE-2): five samples two seconds apart; while the mean is above
   50 %, wait 30 s and sample again, for up to 10 minutes. The wait never fails the run; it
   only keeps this run from stacking on another session's work. The load it ran at is printed.
   dev-proof.py imports host_load_wait() from this file and runs it before each dev proof.
2. Start os.cpu_count() busy children, then wait on the signal: sample the load every 2 s
   until it reaches --threshold (85 %), for up to 60 s. Not reached: exit 2.
   Each child runs SPIN, which prints its own os.getpid() and then spins. The venv python.exe
   is a launcher whose child is the real interpreter, so the printed id is the interpreter's,
   not the launcher's. The script opens a handle to each interpreter as soon as it reads the
   id; a child whose id isn't read within 30 s is a setup failure (exit 2). Through that
   handle it reads the process's id, parent id and creation time, and keeps the handle only
   when the process is the launcher itself or a child of the launcher created no earlier than
   it; an id reused by an unrelated process in between is refused and left alone (exit 2), so
   no handle to it is kept or terminated.
3. Run `python -m pytest -q --tb=short -p no:cacheprovider` on FILES --runs times (3),
   each into <out>/trr-load-run-<i>.txt, while a sampler thread records the load every ~3 s.
   A run that passes --run-timeout (1800 s) ends the runs with code 124.
4. In a `finally`: kill every launcher by its own handle and wait for each; then wait up to
   10 s on each interpreter's handle, and stop one that is still running through that same
   handle. It prints `busy children left: N` (launchers), `busy interpreters still running
   after the launcher kill: N`, and `busy interpreters left: N`. Either "left" count above 0
   fails the run.

--kill-check does steps 2 and 4 only (no threshold wait, no pytest run) with --children
children (default 2): it proves on this host that the stop leaves no interpreter running.
Exit 0 when both "left" counts are 0, else 1; 2 when a child would not start.

Load is the share of non-idle CPU time between two GetSystemTimes readings
(kernel time includes idle time). Python's psutil isn't installed here.

Pass (exit 0): every run passed and the median of the samples taken during the runs is at
least --threshold. Exit 1: a run failed, the median was below the threshold, or a busy process
was left. Exit 2: setup failed (the load never reached the threshold, or a child would not
start or print its id). The output names the files, the counts from each run's last line and
the load figures; never a path under the home folder.

--selftest checks the load arithmetic, the median, the verdict, the id parsing and the
interpreter ownership rule (a reused id refused) on synthetic input, reads its own identity
through a handle, and starts no process.
"""

from __future__ import annotations

import argparse
import ctypes
import os
import statistics
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

REPO = Path("P:/av-kit")
FILES = (
    "tests/integration/test_tts_assets.py",
    "tests/integration/test_youtube_adapter.py",
    "tests/integration/test_tts_voice_packs.py",
)
SPIN = "import os\nprint(os.getpid(), flush=True)\nwhile True:\n    pass\n"
SYNCHRONIZE = 0x00100000
PROCESS_TERMINATE = 0x0001
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
WAIT_OBJECT_0 = 0

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
kernel32.WaitForSingleObject.restype = wintypes.DWORD
kernel32.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
kernel32.TerminateProcess.restype = wintypes.BOOL
kernel32.TerminateProcess.argtypes = (wintypes.HANDLE, wintypes.UINT)
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
kernel32.GetProcessTimes.restype = wintypes.BOOL
kernel32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4


class ProcessBasicInformation(ctypes.Structure):
    _fields_ = [
        ("exit_status", ctypes.c_long),
        ("peb_base_address", ctypes.c_void_p),
        ("affinity_mask", ctypes.c_size_t),
        ("base_priority", ctypes.c_long),
        ("unique_process_id", ctypes.c_size_t),
        ("inherited_from_unique_process_id", ctypes.c_size_t),
    ]


ntdll = ctypes.WinDLL("ntdll")
ntdll.NtQueryInformationProcess.restype = ctypes.c_long
ntdll.NtQueryInformationProcess.argtypes = (
    wintypes.HANDLE,
    ctypes.c_ulong,
    ctypes.c_void_p,
    ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ulong),
)


def process_identity(handle: int) -> tuple[int, int, int] | None:
    """(id, parent id, creation time) of the process behind HANDLE, read through that handle.

    A handle stays bound to one process, so what it reads can't belong to a later holder of
    the id. None when either read fails.
    """
    info = ProcessBasicInformation()
    size = ctypes.c_ulong()
    status = ntdll.NtQueryInformationProcess(
        handle, 0, ctypes.byref(info), ctypes.sizeof(info), ctypes.byref(size)
    )
    times = [wintypes.FILETIME() for _ in range(4)]
    if status != 0 or not kernel32.GetProcessTimes(handle, *(ctypes.byref(t) for t in times)):
        return None
    created = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime
    return int(info.unique_process_id), int(info.inherited_from_unique_process_id), created


def owned_interpreter(
    pid: int,
    launcher_pid: int,
    launcher_created: int | None,
    identity: tuple[int, int, int] | None,
) -> bool:
    """True when IDENTITY (read through the handle opened for PID) is the launcher or its child.

    A printed id can be reused by an unrelated process before the handle opens. Such a process
    has another parent, or (a stale parent id equal to the launcher's) was created before the
    launcher; either way it is refused, so its handle is never kept or terminated.
    """
    if identity is None or identity[0] != pid:
        return False
    if pid == launcher_pid:
        return True
    return (
        launcher_created is not None
        and identity[1] == launcher_pid
        and identity[2] >= launcher_created
    )


def launcher_created(child: subprocess.Popen[bytes]) -> int | None:
    """The launcher's creation time; Popen holds its handle, so its id can't be reused."""
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, child.pid)
    if not handle:
        return None
    try:
        identity = process_identity(handle)
    finally:
        kernel32.CloseHandle(handle)
    return identity[2] if identity else None


def system_times() -> tuple[int, int, int]:
    """(idle, kernel, user) in 100 ns units; kernel includes idle."""
    idle, kernel, user = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
    if not kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        raise OSError("GetSystemTimes failed")

    def value(ft: wintypes.FILETIME) -> int:
        return (ft.dwHighDateTime << 32) | ft.dwLowDateTime

    return value(idle), value(kernel), value(user)


def load_between(before: tuple[int, int, int], after: tuple[int, int, int]) -> float:
    """Percent of CPU time that wasn't idle between two readings."""
    idle = after[0] - before[0]
    total = (after[1] - before[1]) + (after[2] - before[2])
    if total <= 0:
        return 0.0
    return round(100.0 * (total - idle) / total, 1)


def sample(seconds: float) -> float:
    before = system_times()
    time.sleep(seconds)
    return load_between(before, system_times())


def host_load_wait() -> float:
    samples = [sample(2.0) for _ in range(5)]
    load = round(statistics.fmean(samples), 1)
    print(f"host-load samples: {samples} mean={load}")
    deadline = time.monotonic() + 600
    while load > 50 and time.monotonic() < deadline:
        print(f"host-load {load} % is above 50 %; waiting 30 s")
        time.sleep(28)
        load = sample(2.0)
    print(f"host-load: ran at {load} %")
    return load


class Sampler(threading.Thread):
    def __init__(self, interval: float) -> None:
        super().__init__(daemon=True)
        self.interval = interval
        self.samples: list[float] = []
        self.done = threading.Event()

    def run(self) -> None:
        before = system_times()
        while not self.done.wait(self.interval):
            after = system_times()
            self.samples.append(load_between(before, after))
            before = after


def verdict(results: list[int], samples: list[float], threshold: float) -> tuple[int, str]:
    """(exit code, reason) from each run's exit code and the load samples taken during them."""
    if not samples:
        return 1, "no load sample was taken during the runs"
    median = statistics.median(samples)
    failed = [i for i, code in enumerate(results, 1) if code != 0]
    if failed:
        return 1, f"run(s) {failed} failed; median load {median}"
    if median < threshold:
        return 1, f"every run passed but the median load {median} is below {threshold}"
    return (
        0,
        f"{len(results)} of {len(results)} runs passed at median load {median}"
        f" (threshold {threshold})",
    )


def last_line(text: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[-1] if lines else "(no output)"


def parse_pid(line: bytes) -> int | None:
    """The interpreter id a spinner printed, or None when the line isn't a positive integer."""
    text = line.decode("ascii", "replace").strip()
    return int(text) if text.isdigit() and int(text) > 0 else None


def read_pid(child: subprocess.Popen[bytes], timeout: float) -> int | None:
    """The first line the child prints, parsed; None when nothing usable arrives in time."""
    got: list[bytes] = []

    def reader() -> None:
        assert child.stdout is not None
        got.append(child.stdout.readline())

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    thread.join(timeout)
    return parse_pid(got[0]) if got else None


class Busy:
    """The busy children: each launcher's Popen and a handle to each interpreter."""

    def __init__(self) -> None:
        self.children: list[subprocess.Popen[bytes]] = []
        self.handles: dict[int, int] = {}

    def start(self, count: int) -> bool:
        for _ in range(count):
            child = subprocess.Popen(
                [sys.executable, "-c", SPIN],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            self.children.append(child)
            pid = read_pid(child, 30.0)
            if pid is None:
                print("SETUP FAIL: a busy child printed no interpreter id in 30 s")
                return False
            handle = kernel32.OpenProcess(
                SYNCHRONIZE | PROCESS_TERMINATE | PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if not handle:
                print("SETUP FAIL: no handle to a busy interpreter")
                return False
            identity = process_identity(handle)
            if not owned_interpreter(pid, child.pid, launcher_created(child), identity):
                kernel32.CloseHandle(handle)
                print("SETUP FAIL: the printed id isn't this launcher's interpreter; left alone")
                return False
            self.handles[pid] = handle
        same = sum(1 for c in self.children if c.pid in self.handles)
        print(
            f"busy children started: {len(self.children)}; interpreters: {len(self.handles)}"
            f" ({same} the launcher itself)"
        )
        return True

    def stop(self) -> int:
        """Stop everything; print the counts; return the number left (launchers + interpreters)."""
        for child in self.children:
            if child.poll() is None:
                child.kill()
        for child in self.children:
            try:
                child.wait(timeout=30)
            except subprocess.TimeoutExpired:
                pass
            if child.stdout is not None:
                child.stdout.close()
        launchers_left = sum(1 for child in self.children if child.poll() is None)
        print(f"busy children left: {launchers_left}")
        deadline = time.monotonic() + 10
        survivors = []
        for pid, handle in self.handles.items():
            wait_ms = max(0, int((deadline - time.monotonic()) * 1000))
            if kernel32.WaitForSingleObject(handle, wait_ms) != WAIT_OBJECT_0:
                survivors.append(pid)
        print(f"busy interpreters still running after the launcher kill: {len(survivors)}")
        left = 0
        for pid in survivors:
            handle = self.handles[pid]
            kernel32.TerminateProcess(handle, 1)
            if kernel32.WaitForSingleObject(handle, 10000) != WAIT_OBJECT_0:
                left += 1
        for handle in self.handles.values():
            kernel32.CloseHandle(handle)
        self.handles.clear()
        print(f"busy interpreters left: {left}")
        return launchers_left + left


def kill_check(args: argparse.Namespace) -> int:
    busy = Busy()
    started = False
    try:
        started = busy.start(args.children or 2)
        if started:
            time.sleep(2)
    finally:
        left = busy.stop()
    if not started:
        return 2
    print("PASS: no busy process left" if left == 0 else f"FAIL: {left} busy process(es) left")
    return 1 if left else 0


def run(args: argparse.Namespace) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    host_load_wait()
    cpus = args.children or (os.cpu_count() or 1)
    busy = Busy()
    sampler = Sampler(3.0)
    results: list[int] = []
    left = 0
    try:
        if not busy.start(cpus):
            return 2
        deadline = time.monotonic() + 60
        load = sample(2.0)
        while load < args.threshold and time.monotonic() < deadline:
            load = sample(2.0)
        print(f"load before the runs: {load} %")
        if load < args.threshold:
            print(f"SETUP FAIL: load {load} % never reached {args.threshold} % in 60 s")
            return 2
        sampler.start()
        for i in range(1, args.runs + 1):
            receipt = args.out / f"trr-load-run-{i}.txt"
            started = time.monotonic()
            with receipt.open("wb") as handle:
                code = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "-q",
                        "--tb=short",
                        "-p",
                        "no:cacheprovider",
                        *FILES,
                    ],
                    cwd=REPO,
                    stdout=handle,
                    stderr=subprocess.STDOUT,
                    timeout=args.run_timeout,
                    check=False,
                ).returncode
            results.append(code)
            text = receipt.read_bytes().decode("utf-8", "replace")
            took = round(time.monotonic() - started)
            print(f"run {i}: exit {code} in {took} s :: {last_line(text)} -> {receipt.name}")
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
    code, reason = verdict(results, samples, args.threshold)
    print(("PASS: " if code == 0 else "FAIL: ") + reason)
    return code


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    check("all busy reads 100", load_between((0, 0, 0), (0, 500, 500)) == 100.0)
    check("all idle reads 0", load_between((0, 0, 0), (1000, 1000, 0)) == 0.0)
    check("a quarter idle reads 75", load_between((10, 10, 10), (260, 510, 510)) == 75.0)
    check("no elapsed time reads 0", load_between((5, 5, 5), (5, 5, 5)) == 0.0)
    check("three passes at 90 pass", verdict([0, 0, 0], [88.0, 90.0, 95.0], 85)[0] == 0)
    check("a failed run fails", verdict([0, 1, 0], [90.0, 90.0], 85)[0] == 1)
    check("a low median fails", verdict([0, 0, 0], [50.0, 84.0, 99.0], 85)[0] == 1)
    check("no samples fails", verdict([0, 0, 0], [], 85)[0] == 1)
    check("a timeout code fails", verdict([0, 124], [90.0], 85)[0] == 1)
    check("last line skips blanks", last_line("a\n12 passed in 3.0s\n\n") == "12 passed in 3.0s")
    check("an id line parses", parse_pid(b"66964\r\n") == 66964)
    check("an empty line is no id", parse_pid(b"") is None)
    check("a traceback line is no id", parse_pid(b"Traceback (most recent call last):\n") is None)
    check("zero is no id", parse_pid(b"0\n") is None)
    check("the spinner prints its id first", SPIN.index("getpid") < SPIN.index("while True"))
    check("the three files are run", len(FILES) == 3 and FILES[2].endswith("voice_packs.py"))

    launcher, born = 500, 1_000
    check("the launcher itself is owned", owned_interpreter(500, launcher, born, (500, 4, 900)))
    check(
        "the launcher's child is owned", owned_interpreter(501, launcher, born, (501, 500, 1_010))
    )
    check(
        "a reused id under another parent is refused",
        not owned_interpreter(501, launcher, born, (501, 999, 5_000)),
    )
    check(
        "an older process with a stale parent id is refused",
        not owned_interpreter(501, launcher, born, (501, 500, 900)),
    )
    check(
        "a handle to another id is refused",
        not owned_interpreter(501, launcher, born, (502, 500, 1_010)),
    )
    check("no identity is refused", not owned_interpreter(501, launcher, born, None))
    check(
        "an unknown launcher time refuses a child",
        not owned_interpreter(501, launcher, None, (501, 500, 1_010)),
    )
    me = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, os.getpid())
    try:
        mine = process_identity(me) if me else None
    finally:
        if me:
            kernel32.CloseHandle(me)
    check(
        "the identity read through a handle names this process and its parent",
        mine is not None and mine[0] == os.getpid() and mine[1] == os.getppid() and mine[2] > 0,
    )
    print(f"load-run selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--kill-check", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("C:/Temp/av-kit/test-run-reliability"))
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=85.0)
    parser.add_argument(
        "--children", type=int, default=0, help="busy children; 0 means os.cpu_count()"
    )
    parser.add_argument("--run-timeout", type=float, default=1800.0)
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.kill_check:
        return kill_check(args)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
