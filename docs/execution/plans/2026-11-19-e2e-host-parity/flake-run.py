"""Session 97 flake run, copied from Session 91's (2026-11-17-e2e-pointer-flakes/flake-run.py;
D-1145, D-1146) with its receipt folder at C:/Temp/av-kit/e2e-host-parity/flake: the watched
Electron specs and the full suite on a busy host, with counts and a classification of every
failure in a receipt. The gate runs `--mode full --runs 1 --no-burn --label gate`.

    uv run --no-sync python <plan>/flake-run.py --selftest
    uv run --no-sync python <plan>/flake-run.py --kill-check --children 2 --churn
    uv run --no-sync python <plan>/flake-run.py --list-check --label base-list
    uv run --no-sync python <plan>/flake-run.py --mode watched --repeat 10 --runs 1 --churn \
        --label repro
    uv run --no-sync python <plan>/flake-run.py --mode full --runs 5 --label accept \
        --split-hang <scratch>/epf-hang-signatures.json
    uv run --no-sync python <plan>/flake-run.py --mode full --runs 1 --no-burn --label gate

Adapted from Session 90's load-run.py (2026-11-17-test-run-reliability): the busy children, the
interpreter ownership rule, the load arithmetic and the stop are the same code.

1. Host-load wait: five samples two seconds apart; while the mean is above --pre-load (50 %),
   wait 30 s and sample again, for up to 10 minutes. A load still above --pre-load when the
   10 minutes end is a setup failure, exit 2 (S8): the run never starts on a host that other
   work already holds.
2. Start --children busy children (default os.cpu_count() * 3 // 4: 18 of 24 logical CPUs, a
   load of about 75 % with headroom over the 60 % signal), each printing its own
   interpreter id before it spins; a handle is opened to each and kept only when the process is
   the launcher or the launcher's child created no earlier than it (a reused id is refused and
   left alone, exit 2). Then wait on the signal: sample every 2 s until the load reaches
   --threshold (60 %), for up to 60 s. Not reached: exit 2.
   The busy children alone give about 75 %, so the 60 % floor proves only that the children
   ran; it says nothing about the kind of load that makes Electron hang.
   --churn (row 3, D-1146) adds one more child that starts short processes in a loop, `node -e
   0` and `pwsh -NoProfile -Command exit`, one after the other, with their output discarded:
   the bursts of process starts the hang hypothesis names. node and pwsh are found on PATH by
   this script (missing: exit 2). The churn child prints its interpreter id first and is held
   by the same ownership rule; it is stopped with the busy children. The stop prints whether it
   was still alive; a churn child that died during the runs fails the run, exit 2. A start
   still in flight at the stop ends on its own; nothing is stopped by name.
   --no-burn (the session gate's plain Electron run) starts no child, skips the load signal
   and drops the median-load condition from the verdict; everything else is the same.
   --churn with --no-burn is refused.
3. Run Playwright --runs times through node and ui/node_modules/@playwright/test/cli.js (no
   npm shim, so the -g alternation never meets a shell), with --retries=0, the list reporter,
   ELECTRON_RUN_AS_NODE removed and RECEIPTS_DIR set.
   Each invocation takes a new id <inv> (time, pid, six random hex digits) and prints
   `invocation: <inv>`. Run i writes <out>/epf-<label>-<i>-<inv>.txt and its own diag folder
   <out>/epf-<label>-<i>-diag-<inv>, with AVKIT_E2E_DIAG_DIR set to that folder and
   AVKIT_E2E_RUN_ID to <inv>-<i>; it prints `run <i> files: receipt R diag D run_id ID` first.
   Both are created fresh: a folder or receipt already there is refused before Playwright
   starts (setup failure, exit 2), so nothing is appended across invocations. A solo rerun
   (point 4) gets its own receipt, folder and run id the same way.
   --mode watched: the three spec files and -g built from WATCHED, --repeat-each --repeat.
   --mode full: every *.test.ts and *.spec.ts under ui/tests/e2e except EXCLUDED (the two
   clipboard specs this session never runs), one separator-anchored file filter each.
   A sampler thread records the load every 3 s; another records host process starts
   (`tasklist /fo csv /nh` every 5 s) into <out>/epf-<label>-procs-<inv>.txt, created fresh.
   A run that passes --run-timeout ends with code 124; its process tree is stopped from the
   recorded node pid (taskkill /PID <pid> /T /F) while Popen still holds that pid.
4. Every failure block in the receipt is classified:
   watched   its title holds a WATCHED fragment;
   hang      its text holds "Test timeout of" (a hang in any spec: the launch/teardown shape);
   covered   watched or hang (the three issues this session closes);
   rejection its text holds "unhandled rejection:" (S10).
   A failure that is not covered and holds no rejection is rerun alone once (file:line, under
   the same load; Session 90 RULE-3). It counts as recorded when the rerun passes and fails the
   run when it fails. A covered failure is never rerun.
   The run's own diag folder adds, per failing test: the last phase of each launch (a stall
   names it) with its time, the repeat and the test state that phase line recorded
   (test_status and test_errors, from test.info() when the line was written); the final
   launch; the DIAG_EVENTS counts from each launch's main-process log (a bare
   main-<launch>.jsonl only: cursor, window, display, focus and visibility events); and the
   host processes started between that test's first launch and its last phase. A phase line
   counts for the test only when its run_id is this run's and its file (bare name), line and
   title name the failing test (the title equal to the header's, or its last ` › ` part).
   The summary also counts foreign lines (any line in the folder with another run_id or
   none), unreadable lines (not JSON) and malformed lines of the test (launch, repeat or t
   not a number, or an unknown phase).
   --split-hang FILE (D-1150, M-11; row 7 writes FILE): a JSON list of the hang signatures this
   session registered. Each entry is one of
     {"cause": "split", "file": F, "title": T, "phase": P, "issue": ID}     P in SPLIT_PHASES
     {"cause": "product-race", "file": F, "line": N, "phase": Q, "issue": ID, "meu": "MEU-n"}
   with no other key (F a bare spec file name, T the failure's title exactly as the list
   reporter prints it, Q any PHASE_LINES phase). A file that is not such a list is a setup
   failure, exit 2, before the host-load wait; so is --split-hang with --repeat other than 1
   (the failure header names no repeat). Only a hang ("Test timeout of") is ever excused; an
   assertion failure never is. The evidence is the failing test's own final launch in this
   run of this invocation, and nothing else excuses: the summary must show no foreign,
   unreadable or malformed line, exactly one repeat, a final launch (the latest last line; a
   tie leaves none), and every other launch of the test ended at exit. The final launch's last
   phase line must have been written while the test still stood clean: test_status "passed"
   and test_errors 0. Playwright sets the status to "timedOut" and records the error the moment
   the test timeout fires, while the body still runs, so a close begun after a body hang reads
   "timedOut" at close-start and excuses nothing. A missing or mistyped field excuses nothing.
     split: a hang that is not watched, in exactly file F and title T, whose final launch's last
       phase is P (launch-start: stopped inside the launch; close-start: the body ended
       clean and the close hung). launch-end is never split: an installMainDiag evaluate that
       hangs stops there. Another test, in the same file or another, is never excused by it.
     product-race: a hang (watched or not) at exactly file F line N, whose final launch's last
       phase is Q. It names a race in the product that this session registered (issue plus
       MEU), so the test fixes are not held behind it.
   Known limit: an assertion thrown inside a try reaches Playwright only after its finally
   ends, so a finally close that hangs after it still reads "passed". The file, line and title
   identity, the run id and the watched rule bound that case to the one registered test in
   this run.
   An excused hang is printed as `excused: ...`, listed again at the end, counted in the
   verdict, never rerun, and does not fail the verdict. Every other hang is still covered.
5. In a `finally`: stop the busy children exactly as load-run.py does and print the three
   counts; either "left" count above 0 fails the run.

--list-check runs `--list` for both modes (no Electron starts): no EXCLUDED file is listed,
each WATCHED fragment names exactly one test in the full list, the watched list holds
len(WATCHED) tests, and it prints the full total for --expect-total.

Pass (exit 0): no rejection line, no covered failure, every uncovered failure passed its solo
rerun, every run's count matched (--expect-total, or len(WATCHED) x --repeat), no run timed out,
and the median load during the runs is at least --threshold. Exit 1 otherwise; exit 2 when setup
failed. The output never names a path under the home folder.

--selftest checks the load arithmetic, the host-load ceiling, the verdict, the ownership rule,
the count regex on lines numbered below 10, the file filters (the clipboard specs excluded,
settings.test.ts not matching capture-settings-draft), the watched pattern (one match each; the
:1481 AC-67.20 title is not matched), the failure parse and its classification, the diag
summary with its timing, test state and visibility counts, the split rule (launch-start split,
launch-end not, close-start split only while the test stood clean, a missing state never, a
watched hang never, another file or another test in the same file never), the product-race
signature (watched allowed, exact file and line, never after a body timeout), the evidence
binding (two invocations of one label get two fresh folders and receipts and an earlier
invocation's clean close never excuses a current timedOut close; an existing folder or receipt
is refused; a foreign or missing run id, another file, line or title, a second repeat, an
unfinished earlier launch, a tie, a malformed or unreadable line and a main_log path all
excuse nothing; --split-hang with --repeat 2 is refused), the signature file check and the
churn script, on synthetic input in a fresh folder it removes. It starts no process.
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import io
import json
import os
import re
import secrets
import shutil
import statistics
import subprocess
import sys
import threading
import time
from ctypes import wintypes
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path("P:/av-kit")
UI = REPO / "ui"
E2E = UI / "tests/e2e"
CLI = UI / "node_modules/@playwright/test/cli.js"
EXCLUDED = ("capture-filmstrip-actions.test.ts", "capture-import.test.ts")
WATCHED = (
    ("download-queue.test.ts", "AC-49.25 dragging a row onto the third row"),
    ("download-queue.test.ts", "AC-49.26 the drag announces"),
    ("download-queue.test.ts", "AC-49.28 a row drag never"),
    ("convert-queue.test.ts", "AC-49.29 dragging a conversion onto the third row"),
    ("capture-inbox.test.ts", "AC-66.14 an arrow drawn at 100%"),
    ("capture-inbox.test.ts", "AC-67.20 A-6 a disabled Apply"),
    ("capture-inbox.test.ts", "AC-80.10: a real hover"),
    ("capture-inbox.test.ts", "AC-81.11: HOTKEY_IN_USE_FIXTURE"),
    ("capture-inbox.test.ts", "AC-81.14: at 100% after a pan"),
    ("capture-inbox.test.ts", "AC-87.6 the tool lock is on at load"),
    ("capture-inbox.test.ts", "AC-143.29 Electron: Lock on at load"),
)
DIAG_ENV = "AVKIT_E2E_DIAG_DIR"
RUN_ENV = "AVKIT_E2E_RUN_ID"
MAIN_LOG = re.compile(r"main-[0-9]+\.jsonl")
SEP = "\u203a"
OK_LINE = re.compile(r"^ +ok +[0-9]+ ", re.M)
FAIL_HEADER = re.compile(r"^\s{1,4}(\d+)\) (\S+?):(\d+):\d+ " + SEP + r" (.*?)\s*$")
SUMMARY = re.compile(r"^ +(\d+) (failed|flaky|passed|skipped|did not run|interrupted)\b")
LIST_LINE = re.compile(r"^ +(\S+?):(\d+):\d+ " + SEP + r" (.*?)\s*$", re.M)
LIST_TOTAL = re.compile(r"^Total: (\d+) tests? in (\d+) files?", re.M)
PHASES = (
    "launch-start",
    "launch-end",
    "evaluate-end",
    "evaluate-error",
    "close-start",
    "close-end",
    "exit",
)
SPLIT_PHASES = ("launch-start", "close-start")
DIAG_EVENTS = (
    "cursor-inside",
    "resize",
    "move",
    "display",
    "blur",
    "visibility",
    "hide",
    "minimize",
    "restore",
)
ISSUE_ID = re.compile(r"[A-Z0-9]+(-[A-Z0-9]+)+")
MEU_ID = re.compile(r"MEU-[0-9]+")
SPIN = "import os\nprint(os.getpid(), flush=True)\nwhile True:\n    pass\n"
CHURN = (
    "import os, subprocess, sys\n"
    "print(os.getpid(), flush=True)\n"
    "starts = [[sys.argv[1], '-e', '0'], [sys.argv[2], '-NoProfile', '-Command', 'exit']]\n"
    "while True:\n"
    "    for argv in starts:\n"
    "        subprocess.run(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
)
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


# ---------------------------------------------------------------- load and busy children
# (load-run.py, Session 90, unchanged in substance)


def process_identity(handle: int) -> tuple[int, int, int] | None:
    """(id, parent id, creation time) of the process behind HANDLE, read through that handle."""
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
    """True when IDENTITY (read through the handle opened for PID) is the launcher or its child."""
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
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, child.pid)
    if not handle:
        return None
    try:
        identity = process_identity(handle)
    finally:
        kernel32.CloseHandle(handle)
    return identity[2] if identity else None


def system_times() -> tuple[int, int, int]:
    idle, kernel, user = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
    if not kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user)):
        raise OSError("GetSystemTimes failed")

    def value(ft: wintypes.FILETIME) -> int:
        return (ft.dwHighDateTime << 32) | ft.dwLowDateTime

    return value(idle), value(kernel), value(user)


def load_between(before: tuple[int, int, int], after: tuple[int, int, int]) -> float:
    idle = after[0] - before[0]
    total = (after[1] - before[1]) + (after[2] - before[2])
    if total <= 0:
        return 0.0
    return round(100.0 * (total - idle) / total, 1)


def sample(seconds: float) -> float:
    before = system_times()
    time.sleep(seconds)
    return load_between(before, system_times())


def host_load_wait(limit: float, read=sample, pause=time.sleep, budget: float = 600.0) -> float:
    """The host load once it is at or below LIMIT, or the last reading when BUDGET s ran out."""
    samples = [read(2.0) for _ in range(5)]
    load = round(statistics.fmean(samples), 1)
    print(f"host-load samples: {samples} mean={load}")
    deadline = time.monotonic() + budget
    while load > limit and time.monotonic() < deadline:
        print(f"host-load {load} % is above {limit} %; waiting 30 s")
        pause(28)
        load = read(2.0)
    print(f"host-load: {load} %")
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


def parse_pid(line: bytes) -> int | None:
    text = line.decode("ascii", "replace").strip()
    return int(text) if text.isdigit() and int(text) > 0 else None


def read_pid(child: subprocess.Popen[bytes], timeout: float) -> int | None:
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
        self.churn_pid: int | None = None
        self.churn_alive: bool | None = None

    def _spawn(self, argv: list[str]) -> int | None:
        """Start ARGV, read the interpreter id it prints, and hold it under the ownership rule."""
        child = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.children.append(child)
        pid = read_pid(child, 30.0)
        if pid is None:
            print("SETUP FAIL: a busy child printed no interpreter id in 30 s")
            return None
        handle = kernel32.OpenProcess(
            SYNCHRONIZE | PROCESS_TERMINATE | PROCESS_QUERY_LIMITED_INFORMATION, False, pid
        )
        if not handle:
            print("SETUP FAIL: no handle to a busy interpreter")
            return None
        identity = process_identity(handle)
        if not owned_interpreter(pid, child.pid, launcher_created(child), identity):
            kernel32.CloseHandle(handle)
            print("SETUP FAIL: the printed id isn't this launcher's interpreter; left alone")
            return None
        self.handles[pid] = handle
        return pid

    def start(self, count: int) -> bool:
        for _ in range(count):
            if self._spawn([sys.executable, "-c", SPIN]) is None:
                return False
        same = sum(1 for c in self.children if c.pid in self.handles)
        print(
            f"busy children started: {len(self.children)}; interpreters: {len(self.handles)}"
            f" ({same} the launcher itself)"
        )
        return True

    def start_churn(self) -> bool:
        tools = [shutil.which("node"), shutil.which("pwsh")]
        if not all(tools):
            print("SETUP FAIL: --churn needs node and pwsh on PATH")
            return False
        self.churn_pid = self._spawn([sys.executable, "-c", CHURN, *tools])
        if self.churn_pid is None:
            return False
        print("churn child: started (node and pwsh starts)")
        return True

    def stop(self) -> int:
        if self.churn_pid is not None and self.churn_pid in self.handles:
            handle = self.handles[self.churn_pid]
            self.churn_alive = kernel32.WaitForSingleObject(handle, 0) != WAIT_OBJECT_0
            print(f"churn child alive at the stop: {'yes' if self.churn_alive else 'no'}")
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


# ---------------------------------------------------------------- Playwright selection


def js_escape(text: str) -> str:
    """TEXT as a literal inside a JavaScript RegExp (Playwright forceRegExp, flags gi)."""
    return re.sub(r"([.*+?^${}()|\[\]\\/])", r"\\\1", text)


def spec_files(names: list[str] | None = None) -> list[str]:
    found = names if names is not None else [p.name for p in E2E.iterdir() if p.is_file()]
    return sorted(
        n for n in found if (n.endswith(".test.ts") or n.endswith(".spec.ts")) and n not in EXCLUDED
    )


def file_filter(name: str) -> str:
    return "/tests/e2e/" + js_escape(name) + "$"


def watched_files() -> list[str]:
    return sorted({f for f, _ in WATCHED})


def watched_grep() -> str:
    return "(" + "|".join(js_escape(fragment) for _, fragment in WATCHED) + ")"


def playwright_args(mode: str, repeat: int, extra: list[str] | None = None) -> list[str]:
    if mode == "watched":
        filters = [file_filter(n) for n in watched_files()]
        grep = ["-g", watched_grep()]
    elif mode == "full":
        filters = [file_filter(n) for n in spec_files()]
        grep = []
    else:
        raise ValueError(mode)
    return [
        "test",
        *filters,
        *grep,
        f"--repeat-each={repeat}",
        "--retries=0",
        "--reporter=list",
        *(extra or []),
    ]


def child_env(diag: Path | None, run_id: str = "") -> dict[str, str]:
    env = dict(os.environ)
    env.pop("ELECTRON_RUN_AS_NODE", None)
    env.pop("PLAYWRIGHT_JSON_OUTPUT_NAME", None)
    env.setdefault("RECEIPTS_DIR", "C:/Temp/av-kit")
    env.pop(RUN_ENV, None)
    if diag is not None:
        env[DIAG_ENV] = str(diag)
        if run_id:
            env[RUN_ENV] = run_id
    else:
        env.pop(DIAG_ENV, None)
    return env


def new_invocation() -> str:
    """An id no earlier invocation used: the time, this process id and six random hex digits."""
    return f"{time.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}-{secrets.token_hex(3)}"


def run_files(out: Path, tag: str, inv: str) -> tuple[Path, Path]:
    """One run's receipt and diag folder, both named for this invocation."""
    return out / f"epf-{tag}-{inv}.txt", out / f"epf-{tag}-diag-{inv}"


def claim(diag: Path, receipt: Path) -> io.BufferedWriter:
    """Create the run's diag folder and receipt fresh; either one already there is refused."""
    diag.mkdir(parents=True, exist_ok=False)
    return receipt.open("xb")


# ---------------------------------------------------------------- receipt parsing


@dataclass
class Failure:
    file: str
    line: int
    title: str
    text: str
    watched: bool = False
    hang: bool = False
    rejection: bool = False
    rerun: str = ""
    excused: str = ""

    @property
    def covered(self) -> bool:
        return (self.watched or self.hang) and not self.excused


@dataclass
class RunResult:
    label: str
    code: int
    passed: int
    failures: list[Failure] = field(default_factory=list)
    rejection_lines: int = 0
    expected: int = 0

    def count_ok(self) -> bool:
        return self.expected == 0 or self.passed + len(self.failures) == self.expected


def is_watched(title: str) -> bool:
    return any(fragment in title for _, fragment in WATCHED)


def parse_failures(text: str) -> list[Failure]:
    """Every numbered failure block of a list-reporter receipt, classified."""
    lines = text.splitlines()
    blocks: list[tuple[re.Match[str], list[str]]] = []
    for line in lines:
        header = FAIL_HEADER.match(line)
        if header:
            blocks.append((header, []))
        elif blocks:
            if SUMMARY.match(line):
                break
            blocks[-1][1].append(line)
    failures = []
    for header, body in blocks:
        joined = "\n".join(body)
        name = header.group(2).replace("\\", "/").rsplit("/", 1)[-1]
        title = header.group(4)
        failures.append(
            Failure(
                file=name,
                line=int(header.group(3)),
                title=title,
                text=joined,
                watched=is_watched(title),
                hang="Test timeout of" in joined,
                rejection="unhandled rejection:" in joined,
            )
        )
    return failures


def parse_run(label: str, code: int, text: str, expected: int) -> RunResult:
    return RunResult(
        label=label,
        code=code,
        passed=len(OK_LINE.findall(text)),
        failures=parse_failures(text),
        rejection_lines=sum(1 for ln in text.splitlines() if "unhandled rejection:" in ln),
        expected=expected,
    )


def verdict(results: list[RunResult], samples: list[float], threshold: float) -> tuple[int, str]:
    if not results:
        return 1, "no run completed"
    if not samples:
        return 1, "no load sample was taken during the runs"
    median = statistics.median(samples)
    problems: list[str] = []
    for r in results:
        if r.rejection_lines:
            problems.append(f"{r.label}: {r.rejection_lines} rejection line(s) (S10)")
        if r.code == 124:
            problems.append(f"{r.label}: timed out")
        covered = [f for f in r.failures if f.covered]
        if covered:
            problems.append(
                f"{r.label}: {len(covered)} covered failure(s): "
                + "; ".join(f"{f.file}:{f.line}" for f in covered)
            )
        solo_failed = [
            f for f in r.failures if not f.covered and not f.excused and f.rerun != "passed"
        ]
        if solo_failed:
            problems.append(
                f"{r.label}: uncovered failure(s) not cleared by a solo rerun (S5): "
                + "; ".join(f"{f.file}:{f.line} rerun={f.rerun or 'none'}" for f in solo_failed)
            )
        if not r.count_ok():
            problems.append(
                f"{r.label}: {r.passed} passed + {len(r.failures)} failed != {r.expected}"
            )
        if r.code not in (0, 124) and not r.failures:
            problems.append(f"{r.label}: exit {r.code} with no parsed failure")
    if median < threshold:
        problems.append(f"median load {median} is below {threshold}")
    if problems:
        return 1, f"median load {median}; " + " | ".join(problems)
    recorded = sum(1 for r in results for f in r.failures if not f.excused)
    excused = sum(1 for r in results for f in r.failures if f.excused)
    return 0, (
        f"{len(results)} of {len(results)} runs clean at median load {median}"
        f" (threshold {threshold}); uncovered failures cleared by a solo rerun: {recorded};"
        f" hangs excused by a registered signature: {excused}"
    )


# ---------------------------------------------------------------- diag folder


def read_lines(path: Path) -> tuple[list[dict], int]:
    """The JSON object lines of a file, and how many of its lines are not one."""
    if not path.exists():
        return [], 0
    rows, unreadable = [], 0
    for line in path.read_bytes().decode("utf-8", "replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            unreadable += 1
            continue
        if isinstance(row, dict):
            rows.append(row)
        else:
            unreadable += 1
    return rows, unreadable


def read_jsonl(path: Path) -> list[dict]:
    return read_lines(path)[0]


def is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def same_test(p: dict, f: Failure) -> bool:
    """The phase line names the failing test: its spec file, its line and its title."""
    title = p.get("title")
    return (
        isinstance(title, str)
        and bool(title)
        and (f.title == title or f.title.endswith(f" {SEP} {title}"))
        and p.get("file") == f.file
        and is_int(p.get("line"))
        and p.get("line") == f.line
    )


def well_formed(p: dict) -> bool:
    t = p.get("t")
    return (
        isinstance(t, (int, float))
        and not isinstance(t, bool)
        and is_int(p.get("launch"))
        and is_int(p.get("repeat"))
        and p.get("phase") in PHASES
    )


def clean_launch(summary: dict, n: object) -> bool:
    """The launch's last phase line was written while the test stood passed with no error."""
    timing = summary.get("timing", {}).get(n, {})
    errors = timing.get("test_errors")
    return timing.get("test_status") == "passed" and is_int(errors) and errors == 0


def check_signatures(raw: object) -> list[dict]:
    """The --split-hang entries, or ValueError naming the first bad one."""
    if not isinstance(raw, list):
        raise ValueError("the signature file is not a JSON list")
    keys = {
        "split": {"cause", "file", "title", "phase", "issue"},
        "product-race": {"cause", "file", "line", "phase", "issue", "meu"},
    }
    for i, e in enumerate(raw):
        if not isinstance(e, dict) or e.get("cause") not in keys or set(e) != keys[e["cause"]]:
            raise ValueError(f"entry {i}: not a split or product-race entry with exactly its keys")
        if not isinstance(e["issue"], str) or not ISSUE_ID.fullmatch(e["issue"]):
            raise ValueError(f"entry {i}: issue is not a register id")
        name = e["file"]
        if (
            not isinstance(name, str)
            or "/" in name
            or "\\" in name
            or not (name.endswith(".test.ts") or name.endswith(".spec.ts"))
        ):
            raise ValueError(f"entry {i}: file is not a spec file name")
        if e["cause"] == "split":
            if e["phase"] not in SPLIT_PHASES:
                raise ValueError(f"entry {i}: a split phase is one of {SPLIT_PHASES}")
            if not isinstance(e["title"], str) or not e["title"].strip():
                raise ValueError(f"entry {i}: title is not a test title")
        if e["cause"] == "product-race":
            if e["phase"] not in PHASES:
                raise ValueError(f"entry {i}: phase is not a PHASE_LINES phase")
            if not isinstance(e["meu"], str) or not MEU_ID.fullmatch(e["meu"]):
                raise ValueError(f"entry {i}: meu is not an MEU id")
            if not isinstance(e["line"], int) or isinstance(e["line"], bool) or e["line"] < 1:
                raise ValueError(f"entry {i}: line is not a positive integer")
    return raw


def load_signatures(path: Path | None) -> list[dict]:
    if path is None:
        return []
    try:
        raw = json.loads(path.read_bytes().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"the signature file does not read as JSON: {type(exc).__name__}") from exc
    return check_signatures(raw)


def excuse(f: Failure, summary: dict, signatures: list[dict]) -> str:
    """The registered signature that excuses this hang, as a line; empty when none does.

    The only evidence is the failing test's own final launch in this run of this invocation
    (diag_summary binds it); anything else in the folder, or any doubt about which launch or
    repeat failed, excuses nothing.
    """
    if not f.hang or not signatures:
        return ""
    if any(summary.get(key) != 0 for key in ("foreign", "unreadable", "malformed")):
        return ""
    if len(summary.get("repeats", [])) != 1:
        return ""
    last = summary.get("last_phase", {})
    n = summary.get("final")
    if n is None or n not in last or not clean_launch(summary, n):
        return ""
    if any(phase != "exit" for m, phase in last.items() if m != n):
        return ""
    phase = last[n]
    for e in signatures:
        if e["file"] != f.file or e["phase"] != phase:
            continue
        if e["cause"] == "product-race" and e["line"] == f.line:
            return f"product-race {e['issue']} {e['meu']} {f.file}:{f.line} {phase}"
        if (
            e["cause"] == "split"
            and phase in SPLIT_PHASES
            and not f.watched
            and e["title"] == f.title
        ):
            return f"split {e['issue']} {f.file}:{f.line} {phase}"
    return ""


def diag_summary(diag: Path, f: Failure, run_id: str, procs: list[tuple[float, str, int]]) -> dict:
    """What this run's diag folder says about the launches of one failing test.

    A phase line counts only when it carries this run's id and names this test (file, line and
    title). Every line with another run id, or none, is counted as foreign; a line that is not
    JSON as unreadable; a line of this test without an integer launch and repeat, a numeric t and
    a known phase as malformed. The final launch is the one whose last line is the latest; a tie
    leaves none.
    """
    rows, unreadable = read_lines(diag / "phases.jsonl")
    foreign = sum(1 for p in rows if not run_id or p.get("run_id") != run_id)
    mine = [p for p in rows if run_id and p.get("run_id") == run_id and same_test(p, f)]
    good = [p for p in mine if well_formed(p)]
    launches: dict[int, list[dict]] = {}
    for p in good:
        launches.setdefault(p["launch"], []).append(p)
    out: dict = {
        "run_id": run_id,
        "lines": len(mine),
        "foreign": foreign,
        "unreadable": unreadable,
        "malformed": len(mine) - len(good),
        "repeats": sorted({p["repeat"] for p in good}),
        "launches": len(launches),
        "final": None,
        "last_phase": {},
        "timing": {},
        "events": {},
        "host_starts": [],
    }
    for n, group in sorted(launches.items()):
        out["last_phase"][n] = group[-1]["phase"]
        timing = {"repeat": group[0]["repeat"], "last_t": float(group[-1]["t"])}
        for key in ("test_status", "test_errors"):
            if key in group[-1]:
                timing[key] = group[-1][key]
        out["timing"][n] = timing
        log = group[0].get("main_log")
        ok_log = isinstance(log, str) and MAIN_LOG.fullmatch(log) and log == f"main-{n}.jsonl"
        events = read_jsonl(diag / log) if ok_log else []
        for kind in DIAG_EVENTS:
            hits = sum(1 for e in events if e.get("event") == kind)
            if hits:
                out["events"][kind] = out["events"].get(kind, 0) + hits
    ends = sorted(((t["last_t"], n) for n, t in out["timing"].items()), reverse=True)
    if ends and (len(ends) == 1 or ends[0][0] > ends[1][0]):
        out["final"] = ends[0][1]
    if good:
        start = min(float(p["t"]) for p in good) / 1000.0
        end = max(float(p["t"]) for p in good) / 1000.0 + 60.0
        out["host_starts"] = [f"{name}:{pid}" for t, name, pid in procs if start <= t <= end]
    return out


class ProcWatch(threading.Thread):
    """Host process starts, from tasklist every 5 s (names and ids only)."""

    def __init__(self, receipt: Path) -> None:
        super().__init__(daemon=True)
        self.receipt = receipt
        self.done = threading.Event()
        self.starts: list[tuple[float, str, int]] = []

    @staticmethod
    def snapshot() -> dict[int, str]:
        raw = subprocess.run(
            ["tasklist", "/fo", "csv", "/nh"], capture_output=True, check=False
        ).stdout.decode("mbcs", "replace")
        rows = {}
        for row in csv.reader(io.StringIO(raw)):
            if len(row) >= 2 and row[1].isdigit():
                rows[int(row[1])] = row[0]
        return rows

    def run(self) -> None:
        seen = self.snapshot()
        with self.receipt.open("x", encoding="utf-8") as out:
            while not self.done.wait(5.0):
                now = self.snapshot()
                stamp = time.time()
                for pid, name in now.items():
                    if seen.get(pid) != name:
                        self.starts.append((stamp, name, pid))
                        out.write(f"{time.strftime('%H:%M:%S')} start {name} {pid}\n")
                out.flush()
                seen = now


# ---------------------------------------------------------------- running


def node() -> str:
    found = shutil.which("node")
    if not found:
        raise OSError("node not on PATH")
    return found


def run_playwright(
    args: list[str], receipt: Path, diag: Path | None, timeout: float, run_id: str = ""
) -> int:
    # A run with a diag folder claims the folder and its receipt fresh (FileExistsError, an
    # OSError, is a setup failure before anything starts); --list-check writes neither.
    with claim(diag, receipt) if diag is not None else receipt.open("wb") as handle:
        child = subprocess.Popen(
            [node(), str(CLI), *args],
            cwd=UI,
            env=child_env(diag, run_id),
            stdout=handle,
            stderr=subprocess.STDOUT,
        )
        try:
            return child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            # Popen still holds the recorded pid, so the tree below it is this run's own.
            subprocess.run(
                ["taskkill", "/PID", str(child.pid), "/T", "/F"], capture_output=True, check=False
            )
            child.wait(timeout=60)
            return 124


def solo_rerun(f: Failure, out: Path, tag: str, inv: str, timeout: float) -> str:
    rerun = f"{tag}-rerun-{f.file.split('.')[0]}-{f.line}"
    receipt, diag = run_files(out, rerun, inv)
    args = [
        "test",
        file_filter(f.file)[:-1] + f":{f.line}",
        "--repeat-each=1",
        "--retries=0",
        "--reporter=list",
    ]
    print(f"  rerun files: receipt {receipt.name} diag {diag.name} run_id {inv}-{rerun}")
    code = run_playwright(args, receipt, diag, timeout, f"{inv}-{rerun}")
    text = receipt.read_bytes().decode("utf-8", "replace")
    if "unhandled rejection:" in text:
        return "rejection"
    ok = code == 0 and len(OK_LINE.findall(text)) == 1
    print(f"  solo rerun {f.file}:{f.line}: exit {code} -> {receipt.name}")
    return "passed" if ok else "failed"


def kill_check(args: argparse.Namespace) -> int:
    busy = Busy()
    started = False
    try:
        started = busy.start(args.children or 2) and (not args.churn or busy.start_churn())
        if started:
            time.sleep(2)
    finally:
        left = busy.stop()
    if not started:
        return 2
    if args.churn and not busy.churn_alive:
        print("FAIL: the churn child was not alive at the stop")
        return 1
    print("PASS: no busy process left" if left == 0 else f"FAIL: {left} busy process(es) left")
    return 1 if left else 0


def list_check(args: argparse.Namespace) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    texts = {}
    for mode in ("full", "watched"):
        receipt = args.out / f"epf-{args.label}-{mode}.txt"
        code = run_playwright(playwright_args(mode, 1, ["--list"]), receipt, None, args.run_timeout)
        texts[mode] = receipt.read_bytes().decode("utf-8", "replace")
        print(f"--list {mode}: exit {code} -> {receipt.name}")
        if code != 0:
            return 1
    full = LIST_LINE.findall(texts["full"])
    watched = LIST_LINE.findall(texts["watched"])
    names = {p.replace("\\", "/").rsplit("/", 1)[-1] for p, _, _ in full}
    bad = sorted(names & set(EXCLUDED))
    counts = {frag: sum(1 for _, _, t in full if frag in t) for _, frag in WATCHED}
    total = LIST_TOTAL.search(texts["full"])
    print(f"full list: {len(full)} tests in {len(names)} files; total line: {total and total[0]}")
    print(f"excluded files listed: {bad}")
    print(
        f"watched fragments with a count other than 1: {[f for f, c in counts.items() if c != 1]}"
    )
    print(f"watched list: {len(watched)} tests (want {len(WATCHED)})")
    ok = not bad and all(c == 1 for c in counts.values()) and len(watched) == len(WATCHED)
    print(f"expect-total {len(full)}" if ok else "FAIL: the selection is not what the plan pins")
    return 0 if ok else 1


def run(args: argparse.Namespace) -> int:
    args.out.mkdir(parents=True, exist_ok=True)
    try:
        signatures = load_signatures(args.split_hang)
    except ValueError as exc:
        print(f"SETUP FAIL: --split-hang: {exc}")
        return 2
    print(f"hang signatures: {len(signatures)}")
    for e in signatures:
        print(f"  signature: {json.dumps(e, sort_keys=True)}")
    # Every file this invocation writes carries its id and is created fresh, so no run reads a
    # line an earlier invocation left (plan review round 2, F3).
    inv = new_invocation()
    print(f"invocation: {inv}")
    if host_load_wait(args.pre_load) > args.pre_load:
        print(f"SETUP FAIL: host load stayed above {args.pre_load} % after the 10-minute wait (S8)")
        return 2
    cpus = args.children or max(1, (os.cpu_count() or 2) * 3 // 4)
    expected = args.expect_total if args.mode == "full" else len(WATCHED) * args.repeat
    busy = Busy()
    sampler = Sampler(3.0)
    procs = ProcWatch(args.out / f"epf-{args.label}-procs-{inv}.txt")
    results: list[RunResult] = []
    excused: list[str] = []
    left = 0
    try:
        if not args.no_burn and not busy.start(cpus):
            return 2
        if args.churn and not busy.start_churn():
            return 2
        deadline = time.monotonic() + 60
        load = sample(2.0)
        while not args.no_burn and load < args.threshold and time.monotonic() < deadline:
            load = sample(2.0)
        print(f"load before the runs: {load} % with {0 if args.no_burn else cpus} busy children")
        if not args.no_burn and load < args.threshold:
            print(f"SETUP FAIL: load {load} % never reached {args.threshold} % in 60 s")
            return 2
        sampler.start()
        procs.start()
        for i in range(1, args.runs + 1):
            tag = f"{args.label}-{i}"
            run_id = f"{inv}-{i}"
            receipt, diag = run_files(args.out, tag, inv)
            print(f"run {i} files: receipt {receipt.name} diag {diag.name} run_id {run_id}")
            started = time.monotonic()
            code = run_playwright(
                playwright_args(args.mode, args.repeat), receipt, diag, args.run_timeout, run_id
            )
            text = receipt.read_bytes().decode("utf-8", "replace")
            result = parse_run(tag, code, text, expected)
            took = round(time.monotonic() - started)
            print(
                f"run {i}: exit {code} in {took} s; ok lines {result.passed}; failures "
                f"{len(result.failures)}; rejection lines {result.rejection_lines}"
                f" -> {receipt.name}"
            )
            for f in result.failures:
                summary = diag_summary(diag, f, run_id, procs.starts)
                f.excused = excuse(f, summary, signatures)
                kind = "covered" if f.covered else ("excused" if f.excused else "uncovered")
                flags = [n for n in ("watched", "hang", "rejection") if getattr(f, n)]
                print(f"  {kind} {f.file}:{f.line} {flags} :: {f.title}")
                print(f"    diag: {json.dumps(summary)}")
                if f.excused:
                    excused.append(f"{tag} {f.excused}")
                    print(f"    excused: {f.excused} (D-1150, M-11)")
                if (
                    not f.covered
                    and not f.excused
                    and not f.rejection
                    and result.rejection_lines == 0
                ):
                    f.rerun = solo_rerun(f, args.out, tag, inv, args.run_timeout)
            results.append(result)
            if code == 124 or result.rejection_lines:
                break
    except OSError as exc:
        print(f"SETUP FAIL: {type(exc).__name__}: {exc}")
        return 2
    finally:
        sampler.done.set()
        procs.done.set()
        for thread in (sampler, procs):
            if thread.is_alive():
                thread.join(timeout=15)
        left = busy.stop()
    if left:
        print(f"FAIL: {left} busy process(es) left")
        return 1
    if args.churn and not busy.churn_alive:
        print("SETUP FAIL: the churn child died during the runs; the load was not held")
        return 2
    print(f"excused hangs: {len(excused)}")
    for line in excused:
        print(f"  excused: {line}")
    samples = sampler.samples
    if samples:
        print(
            f"load during the runs: n={len(samples)} min={min(samples)} "
            f"median={statistics.median(samples)} max={max(samples)}"
        )
    print(f"host process starts during the runs: {len(procs.starts)}")
    code, reason = verdict(results, samples, 0.0 if args.no_burn else args.threshold)
    print(("PASS: " if code == 0 else "FAIL: ") + reason)
    return code


# ---------------------------------------------------------------- selftest

SYNTHETIC = "\n".join(
    [
        "Running 14 tests using 1 worker",
        "",
        f"  ok   1 tests\\e2e\\launch.test.ts:8:1 {SEP} AC-1 launches (515ms)",
        f"  ok   9 tests\\e2e\\capture-inbox.test.ts:1481:1 {SEP} AC-67.20 AC-67.21 AC-67.22"
        " Apply: enabled (1.1s)",
        f"  ok  10 tests\\e2e\\capture-inbox.test.ts:1159:1 {SEP} AC-66.14 an arrow drawn at 100%"
        " stores (2.5s)",
        f"  x   35 tests\\e2e\\capture-inbox.test.ts:1601:1 {SEP} AC-67.20 A-6 a disabled Apply"
        " shows its reason (5.8s)",
        f"  x  104 tests\\e2e\\settings.test.ts:400:1 {SEP} AC-9.1 saves (2.0s)",
        f"  x  120 tests\\e2e\\transcript-queue.test.ts:295:1 {SEP} W2-5 E2E_ACTUATE (1.0m)",
        "",
        f"  1) tests\\e2e\\capture-inbox.test.ts:1601:1 {SEP} AC-67.20 A-6 a disabled Apply shows"
        " its reason ",
        "",
        "    Error: expect(locator).toBeVisible() failed",
        f"  2) tests\\e2e\\settings.test.ts:400:1 {SEP} AC-9.1 saves ",
        "    Error: expect(received).toBe(expected)",
        f"  3) tests\\e2e\\transcript-queue.test.ts:295:1 {SEP} W2-5 E2E_ACTUATE ",
        "    Test timeout of 60000ms exceeded.",
        "  3 failed",
        f"    tests\\e2e\\capture-inbox.test.ts:1601:1 {SEP} AC-67.20 A-6 a disabled Apply ",
        "  3 passed (7.1m)",
        "",
    ]
)

TITLES = {
    "AC-49.25": "AC-49.25 dragging a row onto the third row lands the exact order, and it survives"
    " a reload",
    "AC-49.26": "AC-49.26 the drag announces position-based progress naming the dragged title",
    "AC-49.28": "AC-49.28 a row drag never puts the list into its file-drop state",
    "AC-49.29": "AC-49.29 dragging a conversion onto the third row lands the exact order",
    "AC-66.14": "AC-66.14 an arrow drawn at 100% stores the zoomed image pixels; a Fit arrow keeps"
    " the fit mapping",
    "AC-67.20": "AC-67.20 A-6 a disabled Apply shows its reason where the pointer lands [TA-23]",
    "AC-80.10": "AC-80.10: a real hover shows the enabled Arrow hint and the disabled Undo hint"
    " inside the window; focus and Escape",
    "AC-81.11": "AC-81.11: HOTKEY_IN_USE_FIXTURE: the banner sits inside the header and nothing"
    " below it moves",
    "AC-81.14": "AC-81.14: at 100% after a pan the arrow handles track the arrow, a grab moves the"
    " head, and Tab then arrow keys nudge it",
    "AC-87.6": "AC-87.6 the tool lock is on at load; two real Box drags keep Box with the second"
    " box selected",
    "AC-143.29": "AC-143.29 Electron: Lock on at load, R arms Box, an Alt drag then V arms Select,"
    " a Lock click sends one PUT",
}
NOT_WATCHED = (
    "AC-67.20 AC-67.21 AC-67.22 Apply: enabled with saved marks, off after an edit; Cancel sends"
    " nothing; Confirm bakes once and refetches [TA-22]",
    "AC-67.35 A-10 hovering the disabled Apply shows a visible reason label inside the window"
    " [TA-24]",
    "AC-66.15 a shot change resets to Fit; Space+drag pans at 100% and creates no annotation",
)


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    check("all busy reads 100", load_between((0, 0, 0), (0, 500, 500)) == 100.0)
    check("a quarter idle reads 75", load_between((10, 10, 10), (260, 510, 510)) == 75.0)
    check("no elapsed time reads 0", load_between((5, 5, 5), (5, 5, 5)) == 0.0)
    check("an id line parses", parse_pid(b"66964\r\n") == 66964)
    check("a traceback line is no id", parse_pid(b"Traceback (most recent call last):\n") is None)
    check("the spinner prints its id first", SPIN.index("getpid") < SPIN.index("while True"))
    check("the churn child prints its id first", CHURN.index("getpid") < CHURN.index("while True"))
    check(
        "the churn child starts node -e 0 and pwsh exit",
        "'-e', '0'" in CHURN and "'-Command', 'exit'" in CHURN and "DEVNULL" in CHURN,
    )
    compile(CHURN, "<churn>", "exec")
    still = host_load_wait(50.0, read=lambda s: 90.0, pause=lambda s: None, budget=0.0)
    check("a host load still above --pre-load after the wait is returned (exit 2)", still > 50.0)
    readings = iter([90.0] * 5 + [40.0])
    eased = host_load_wait(50.0, read=lambda s: next(readings), pause=lambda s: None, budget=60.0)
    check("a host load that drops under --pre-load lets the run start", eased <= 50.0)
    launcher, born = 500, 1_000
    check(
        "the launcher's child is owned", owned_interpreter(501, launcher, born, (501, 500, 1_010))
    )
    check("a reused id is refused", not owned_interpreter(501, launcher, born, (501, 999, 5_000)))
    check(
        "an older stale-parent id is refused",
        not owned_interpreter(501, launcher, born, (501, 500, 900)),
    )

    # Session 89 RULE-1: the count regex on lines numbered below 10 and above.
    check("ok regex counts single-digit and two-digit lines", len(OK_LINE.findall(SYNTHETIC)) == 3)
    check("ok regex skips failed lines", not OK_LINE.match("  x   35 tests\\e2e\\a.test.ts:1:1"))

    names = [
        "capture-filmstrip-actions.test.ts",
        "capture-import.test.ts",
        "capture-inbox.test.ts",
        "capture-settings-draft.test.ts",
        "settings.test.ts",
        "command-palette-nav.spec.ts",
        "electron-app.ts",
        "main-error-watch.cjs",
    ]
    picked = spec_files(names)
    check("the clipboard specs are excluded", not set(EXCLUDED) & set(picked))
    check("helpers are not specs", "electron-app.ts" not in picked and len(picked) == 4)
    path = "P:/av-kit/ui/tests/e2e/capture-settings-draft.test.ts"
    check(
        "settings.test.ts does not match capture-settings-draft",
        re.search(file_filter("settings.test.ts"), path, re.I) is None,
    )
    check(
        "a filter matches its own file",
        re.search(file_filter("settings.test.ts"), "P:/av-kit/ui/tests/e2e/settings.test.ts", re.I)
        is not None,
    )
    convert = "P:/av-kit/ui/tests/e2e/convert-queue-labels.test.ts"
    check(
        "convert-queue.test.ts does not match convert-queue-labels",
        re.search(file_filter("convert-queue.test.ts"), convert, re.I) is None,
    )
    grep = re.compile(watched_grep(), re.I)
    check("the pattern has one fragment per watched title", len(WATCHED) == len(TITLES) == 11)
    check("every watched title matches", all(grep.search(t) for t in TITLES.values()))
    check(
        "each watched title matches exactly one fragment",
        all(sum(1 for _, f in WATCHED if f in t) == 1 for t in TITLES.values()),
    )
    check("no unwatched neighbour matches", not any(grep.search(t) for t in NOT_WATCHED))
    check("the three spec files are the watched files", len(watched_files()) == 3)
    args = playwright_args("watched", 10)
    check(
        "watched args repeat ten times with no retry",
        "--repeat-each=10" in args and "--retries=0" in args,
    )
    check("no shell metacharacter escapes", js_escape("a.b(c)") == "a\\.b\\(c\\)")
    env = child_env(Path("C:/Temp/av-kit/x"))
    check("ELECTRON_RUN_AS_NODE is cleared", "ELECTRON_RUN_AS_NODE" not in env)
    check("the diag folder is set", env.get(DIAG_ENV) == str(Path("C:/Temp/av-kit/x")))
    check("no run id is set without one", RUN_ENV not in env)
    check(
        "the run id is set beside its diag folder, and never without one",
        child_env(Path("C:/Temp/av-kit/x"), "inv-1").get(RUN_ENV) == "inv-1"
        and RUN_ENV not in child_env(None, "inv-1"),
    )
    a1, a2 = new_invocation(), new_invocation()
    check("two invocations get two ids", a1 != a2)
    out_dir = Path("C:/Temp/av-kit/e2e-host-parity/flake")
    check(
        "a run's receipt and diag folder carry the invocation id",
        run_files(out_dir, "accept-1", a1)
        == (out_dir / f"epf-accept-1-{a1}.txt", out_dir / f"epf-accept-1-diag-{a1}")
        and run_files(out_dir, "accept-1", a1) != run_files(out_dir, "accept-1", a2),
    )
    flags = argparse.Namespace(
        label="accept", churn=False, no_burn=False, split_hang=None, repeat=1
    )
    check("plain arguments pass", arg_problem(flags) == "")
    check(
        "--split-hang with --repeat 2 is refused, with --repeat 1 it runs",
        "--repeat 1"
        in arg_problem(argparse.Namespace(**{**vars(flags), "split_hang": Path("s"), "repeat": 2}))
        and arg_problem(argparse.Namespace(**{**vars(flags), "split_hang": Path("s")})) == "",
    )

    got = parse_failures(SYNTHETIC)
    check("three failure blocks parse", len(got) == 3)
    if len(got) == 3:
        a, b, c = got
        check("the A-6 failure is watched and covered", a.watched and a.covered and not a.hang)
        check("an uncovered failure is neither", not b.watched and not b.hang and not b.covered)
        check("a test timeout is a covered hang", c.hang and c.covered and not c.watched)
        check("file and line parse", a.file == "capture-inbox.test.ts" and a.line == 1601)
        check("the summary list is not a block", "  3 passed" not in c.text)
    r = parse_run("t-1", 1, SYNTHETIC, 6)
    check("count guard: 3 passed + 3 failed == 6", r.count_ok())
    for f in r.failures:
        if not f.covered:
            f.rerun = "passed"
    code, reason = verdict([r], [70.0, 65.0], 60)
    check("covered failures fail the verdict", code == 1 and "covered failure" in reason)
    clean = parse_run("t-2", 0, "  ok   1 a\n  ok   2 b\n  2 passed\n", 2)
    check("a clean run at load passes", verdict([clean], [61.0, 62.0], 60)[0] == 0)
    check("a low median fails", verdict([clean], [40.0, 50.0], 60)[0] == 1)
    check("a no-burn run (threshold 0) passes at a low load", verdict([clean], [5.0], 0.0)[0] == 0)
    check("no samples fails", verdict([clean], [], 60)[0] == 1)
    short = parse_run("t-3", 0, "  ok   1 a\n  1 passed\n", 2)
    check("a missing test fails the count", verdict([short], [70.0], 60)[0] == 1)
    rejected = parse_run("t-4", 0, "  ok   1 a\nunhandled rejection: boom\n", 1)
    check("a rejection line is S10", "S10" in verdict([rejected], [70.0], 60)[1])
    solo = RunResult("t-5", 1, 1, [Failure("settings.test.ts", 400, "AC-9.1", "", rerun="passed")])
    solo.expected = 2
    check("an uncovered failure cleared by its rerun passes", verdict([solo], [70.0], 60)[0] == 0)
    solo.failures[0].rerun = "failed"
    check("an uncovered failure whose rerun fails is S5", "S5" in verdict([solo], [70.0], 60)[1])
    crashed = parse_run("t-6", 1, "Error: global setup refused a stale out/\n", 0)
    check("a nonzero exit with no failure fails", verdict([crashed], [70.0], 60)[0] == 1)
    timed = RunResult("t-7", 124, 0)
    check("a timeout fails", verdict([timed], [70.0], 60)[0] == 1)

    root = Path("C:/Temp/av-kit/e2e-host-parity/flake/flake-run-selftest")
    root.mkdir(parents=True, exist_ok=True)
    scratch = root / new_invocation()
    scratch.mkdir()
    inv = "20261118T120000-1-abcdef"
    run = f"{inv}-1"
    hang = Failure("capture-inbox.test.ts", 1960, "AC-1 not watched", "", hang=True)
    cases = iter(range(1, 1000))

    def row(t: int, phase: str, launch: int, status: object = "passed", errors: object = 0, **kw):
        out = {
            "t": t,
            "phase": phase,
            "title": hang.title,
            "file": hang.file,
            "line": hang.line,
            "repeat": 0,
            "run_id": run,
            "launch": launch,
            "main_log": f"main-{launch}.jsonl",
            "test_status": status,
            "test_errors": errors,
        }
        out.update(kw)
        return {k: v for k, v in out.items() if v is not None}

    def write(folder: Path, rows: list[dict], tail: str = "") -> Path:
        folder.mkdir(parents=True, exist_ok=True)
        text = "".join(json.dumps(p) + "\n" for p in rows) + tail
        (folder / "phases.jsonl").write_bytes(text.encode("utf-8"))
        return folder

    def summ(rows: list[dict], f: Failure = hang, run_id: str = run, tail: str = "") -> dict:
        return diag_summary(write(scratch / f"case-{next(cases)}", rows, tail), f, run_id, [])

    split_sig = [
        {
            "cause": "split",
            "file": "capture-inbox.test.ts",
            "title": "AC-1 not watched",
            "phase": "close-start",
            "issue": "E2E-ELECTRON-CLOSE-HANG",
        }
    ]
    start_sig = [dict(split_sig[0], phase="launch-start")]
    race_sig = [
        {
            "cause": "product-race",
            "file": "capture-inbox.test.ts",
            "line": 1948,
            "phase": "evaluate-end",
            "issue": "CAPTURE-HOTKEY-RACE",
            "meu": "MEU-160",
        }
    ]
    clean_close = [
        row(1_000_000, "launch-start", 1001),
        row(1_001_000, "launch-end", 1001),
        row(1_002_000, "close-start", 1001),
    ]

    base = write(
        scratch / "base",
        clean_close + [row(1_003_000, "launch-start", 1002, title="AC-1 other", line=1970)],
    )
    (base / "main-1001.jsonl").write_bytes(
        b'{"event":"cursor-inside"}\n{"event":"resize"}\n{"event":"resize"}\n{"event":"show"}\n'
        b'{"event":"visibility","state":"hidden"}\n{"event":"minimize"}\n'
    )
    summary = diag_summary(base, hang, run, [(1_001.5, "node.exe", 42), (2_000.0, "late.exe", 43)])
    check("one launch belongs to the failing test", summary["launches"] == 1)
    check("a stall names its last phase", summary["last_phase"].get(1001) == "close-start")
    check("the one launch is the final launch", summary["final"] == 1001)
    check(
        "another test's line in the same run is neither counted nor foreign",
        summary["lines"] == 3 and summary["foreign"] == 0,
    )
    check(
        "cursor, resize, visibility and minimize events are counted",
        summary["events"] == {"cursor-inside": 1, "resize": 2, "visibility": 1, "minimize": 1},
    )
    check("host starts inside the window are named", summary["host_starts"] == ["node.exe:42"])
    check(
        "the timing holds the last phase time and the test state of the last phase line",
        summary["timing"].get(1001)
        == {"repeat": 0, "last_t": 1_002_000.0, "test_status": "passed", "test_errors": 0},
    )
    check(
        "a hang stopped inside the close is excused by a split entry",
        bool(excuse(hang, summary, split_sig)),
    )
    check("a hang with no signature is not excused", not excuse(hang, summary, []))
    check("a split entry of another phase does not excuse", not excuse(hang, summary, start_sig))

    def stalled(phase: str, status: object = "passed", errors: object = 0) -> dict:
        return {
            "foreign": 0,
            "unreadable": 0,
            "malformed": 0,
            "repeats": [0],
            "final": 1,
            "last_phase": {1: phase},
            "timing": {
                1: {"repeat": 0, "last_t": 1_002_000, "test_status": status, "test_errors": errors}
            },
        }

    check(
        "a close-start after the test timed out is not excused",
        not excuse(hang, stalled("close-start", "timedOut", 1), split_sig),
    )
    check(
        "a close-start after a recorded error is not excused",
        not excuse(hang, stalled("close-start", "passed", 1), split_sig),
    )
    no_state = stalled("close-start")
    no_state["timing"] = {1: {"repeat": 0, "last_t": 1}}
    check("a close-start with no test state is not excused", not excuse(hang, no_state, split_sig))
    check(
        "a test_errors that is not an integer is not clean",
        not excuse(hang, stalled("close-start", "passed", False), split_sig)
        and not excuse(hang, stalled("close-start", "passed", "0"), split_sig),
    )
    check(
        "a clean launch-start stall is split",
        bool(excuse(hang, stalled("launch-start"), start_sig)),
    )
    check(
        "a launch-start stall after the test timed out is not split",
        not excuse(hang, stalled("launch-start", "timedOut", 1), start_sig),
    )
    check(
        "a launch-end or exit stall is never split, even by a forged entry",
        not excuse(hang, stalled("launch-end"), [dict(split_sig[0], phase="launch-end")])
        and not excuse(hang, stalled("exit"), [dict(split_sig[0], phase="exit")]),
    )
    check(
        "a split entry does not excuse the same title in another file",
        not excuse(
            Failure("settings.test.ts", 1960, hang.title, "", hang=True), summary, split_sig
        ),
    )
    check(
        "a split entry does not excuse another test in the same file",
        not excuse(
            Failure("capture-inbox.test.ts", 1970, "AC-2 another test", "", hang=True),
            stalled("close-start"),
            split_sig,
        ),
    )
    check(
        "a split entry matches the title exactly, not as a part",
        not excuse(
            Failure("capture-inbox.test.ts", 1960, "AC-1 not watched again", "", hang=True),
            stalled("close-start"),
            split_sig,
        ),
    )
    late = summ(
        [
            row(1_005_000, "launch-start", 7),
            row(1_006_000, "launch-end", 7),
            row(1_007_000, "evaluate-end", 7),
            row(1_060_000, "close-start", 7, "timedOut", 1),
        ]
    )
    check(
        "setup before the launch, a body timeout, then a finally close 55 s after the launch:"
        " not excused by a split",
        late["last_phase"] == {7: "close-start"} and not excuse(hang, late, split_sig),
    )
    watched_hang = Failure(
        "capture-inbox.test.ts", 1948, TITLES["AC-81.11"], "", watched=True, hang=True
    )
    check(
        "a watched hang is never split", not excuse(watched_hang, stalled("close-start"), split_sig)
    )
    body = stalled("evaluate-end")
    check(
        "a product-race signature excuses a watched hang at its file and line",
        excuse(watched_hang, body, race_sig).startswith("product-race CAPTURE-HOTKEY-RACE MEU-160"),
    )
    check(
        "a product-race signature at another line does not excuse",
        not excuse(Failure("capture-inbox.test.ts", 1949, "x", "", hang=True), body, race_sig),
    )
    check(
        "a product-race signature of another phase does not excuse",
        not excuse(watched_hang, stalled("close-start"), race_sig),
    )
    close_race = [dict(race_sig[0], phase="close-start")]
    check(
        "a product-race close-start signature excuses a clean close that hung",
        bool(excuse(watched_hang, stalled("close-start"), close_race)),
    )
    check(
        "a product-race close-start signature does not excuse a later body hang in that test",
        not excuse(watched_hang, stalled("close-start", "timedOut", 1), close_race),
    )
    race_no_state = stalled("evaluate-end")
    race_no_state["timing"] = {1: {"repeat": 0, "last_t": 1}}
    check(
        "a product-race signature does not excuse a launch with no test state",
        not excuse(watched_hang, race_no_state, race_sig),
    )
    check(
        "a product-race signature does not excuse its line in another file",
        not excuse(
            Failure("convert-queue.test.ts", 1948, TITLES["AC-81.11"], "", hang=True),
            body,
            race_sig,
        ),
    )
    asserted = Failure("capture-inbox.test.ts", 1948, TITLES["AC-81.11"], "", watched=True)
    check("an assertion failure is never excused", not excuse(asserted, body, race_sig))

    # Plan review round 2, F3: the evidence is this invocation's, this run's, this test's own
    # final launch, and nothing else.
    inv_a, inv_b = new_invocation(), new_invocation()
    receipt_a, diag_a = run_files(scratch, "accept-1", inv_a)
    receipt_b, diag_b = run_files(scratch, "accept-1", inv_b)
    with claim(diag_a, receipt_a):
        pass
    write(diag_a, [dict(p, run_id=f"{inv_a}-1") for p in clean_close])
    with claim(diag_b, receipt_b):
        pass
    current = [
        row(2_000_000, "launch-start", 2001, run_id=f"{inv_b}-1"),
        row(2_001_000, "launch-end", 2001, run_id=f"{inv_b}-1"),
        row(2_002_000, "evaluate-end", 2001, run_id=f"{inv_b}-1"),
        row(2_060_000, "close-start", 2001, "timedOut", 1, run_id=f"{inv_b}-1"),
    ]
    write(diag_b, current)
    second = diag_summary(diag_b, hang, f"{inv_b}-1", [])
    check(
        "two invocations of one label write two folders and two receipts",
        diag_a != diag_b and receipt_a != receipt_b and diag_a.is_dir() and diag_b.is_dir(),
    )
    check(
        "two invocations: an earlier invocation's registered clean close does not excuse the"
        " current timedOut finally close",
        second["lines"] == 4
        and second["last_phase"] == {2001: "close-start"}
        and not excuse(hang, second, split_sig)
        and not excuse(hang, second, [dict(race_sig[0], line=hang.line, phase="close-start")]),
    )
    for name, (folder, receipt) in {
        "an existing diag folder": (diag_a, scratch / f"epf-new-{inv_b}.txt"),
        "an existing receipt": (scratch / f"epf-new-diag-{inv_b}", receipt_a),
    }.items():
        try:
            with claim(folder, receipt):
                pass
            refused = False
        except FileExistsError:
            refused = True
        check(f"a run refuses {name} before it starts", refused)
    appended = summ(
        [dict(p, run_id=f"{inv_a}-1") for p in clean_close] + current, run_id=f"{inv_b}-1"
    )
    check(
        "the review's case, both invocations appended to one phases.jsonl: not excused",
        appended["foreign"] == 3 and not excuse(hang, appended, split_sig),
    )
    stale_last = summ(
        current + [dict(p, run_id=f"{inv_a}-1", t=3_000_000) for p in clean_close[-1:]],
        run_id=f"{inv_b}-1",
    )
    check(
        "a foreign clean close written after the current launch does not excuse it",
        stale_last["foreign"] == 1 and not excuse(hang, stale_last, split_sig),
    )
    guest = summ(clean_close + [row(1_003_000, "launch-start", 1002, run_id="other-run")])
    check(
        "a phase line with a foreign run id anywhere in the folder blocks every excuse",
        guest["foreign"] == 1 and guest["final"] == 1001 and not excuse(hang, guest, split_sig),
    )
    bare = summ([dict(p, run_id=None) for p in clean_close])
    check(
        "phase lines with no run id are foreign and excuse nothing",
        bare["foreign"] == 3 and bare["lines"] == 0 and not excuse(hang, bare, split_sig),
    )
    blank = summ(clean_close, run_id="")
    check(
        "a run with no run id reads no line as its own",
        blank["lines"] == 0 and blank["foreign"] == 3,
    )
    other_line = summ([dict(p, line=1961) for p in clean_close])
    check(
        "the same title at another line is another test",
        other_line["lines"] == 0 and not excuse(hang, other_line, split_sig),
    )
    other_file = summ([dict(p, file="settings.test.ts") for p in clean_close])
    check(
        "the same title and line in another file is another test",
        other_file["lines"] == 0 and not excuse(hang, other_file, split_sig),
    )
    part = summ([dict(p, title="AC-1") for p in clean_close])
    check(
        "a phase-line title that is only part of the failure title is another test",
        part["lines"] == 0 and not excuse(hang, part, split_sig),
    )
    nested = Failure("capture-inbox.test.ts", 1960, f"inbox {SEP} AC-1 not watched", "", hang=True)
    in_describe = summ(clean_close, f=nested)
    check(
        "a describe prefix in the failure header still names the test",
        in_describe["lines"] == 3
        and bool(excuse(nested, in_describe, [dict(split_sig[0], title=nested.title)])),
    )
    repeats = summ(
        [
            row(1_000_000, "launch-start", 1001),
            row(1_030_000, "close-start", 1001, "timedOut", 1),
            row(1_031_000, "exit", 1001, "timedOut", 1),
            row(1_040_000, "launch-start", 1002, repeat=1),
            row(1_041_000, "launch-end", 1002, repeat=1),
            row(1_042_000, "close-start", 1002, repeat=1),
        ]
    )
    check(
        "two repeats in one run excuse nothing: repeat 0's body timeout cannot rest on repeat"
        " 1's clean close (the header names no repeat)",
        repeats["repeats"] == [0, 1] and not excuse(hang, repeats, split_sig),
    )
    unfinished = summ(
        [
            row(1_000_000, "launch-start", 1001),
            row(1_001_000, "close-start", 1001),
            row(1_040_000, "launch-start", 1002),
            row(1_042_000, "close-start", 1002),
        ]
    )
    check(
        "an earlier launch of the test that never reached exit blocks the excuse",
        unfinished["final"] == 1002 and not excuse(hang, unfinished, split_sig),
    )
    finished = summ(
        [
            row(1_000_000, "launch-start", 1001),
            row(1_001_000, "close-start", 1001),
            row(1_001_500, "exit", 1001),
            row(1_040_000, "launch-start", 1002),
            row(1_042_000, "close-start", 1002),
        ]
    )
    check(
        "an earlier launch that reached exit leaves the final launch to decide",
        finished["final"] == 1002 and bool(excuse(hang, finished, split_sig)),
    )
    earlier = summ(
        [
            row(1_000_000, "launch-start", 1001),
            row(1_002_000, "close-start", 1001),
            row(1_040_000, "launch-start", 1002),
            row(1_041_000, "launch-end", 1002),
            row(1_050_000, "evaluate-end", 1002, "timedOut", 1),
        ]
    )
    check(
        "an earlier launch's clean close-start does not excuse a final launch that timed out",
        earlier["final"] == 1002 and not excuse(hang, earlier, split_sig),
    )
    tie = summ(
        [
            row(1_000_000, "launch-start", 1001),
            row(1_002_000, "close-start", 1001),
            row(1_000_500, "launch-start", 1002),
            row(1_002_000, "close-start", 1002),
        ]
    )
    check(
        "two launches that end on the same ms leave no final launch",
        tie["final"] is None and not excuse(hang, tie, split_sig),
    )
    odd = summ(clean_close[:2] + [dict(clean_close[2], launch="1001")])
    check(
        "a line of the test with a text launch is malformed and excuses nothing",
        odd["malformed"] == 1 and not excuse(hang, odd, split_sig),
    )
    torn = summ(clean_close, tail='{"t": 1003000, "phase": "clo\n')
    check(
        "a line that is not JSON excuses nothing",
        torn["unreadable"] == 1 and not excuse(hang, torn, split_sig),
    )
    away = write(
        scratch / f"case-{next(cases)}",
        [dict(p, main_log="../base/main-1001.jsonl") for p in clean_close],
    )
    check(
        "a main_log that is not a bare main-<launch>.jsonl is not read",
        diag_summary(away, hang, run, [])["events"] == {},
    )
    check(
        "a missing diag folder reads empty and excuses nothing",
        diag_summary(scratch / "none", hang, run, [])["launches"] == 0
        and not excuse(hang, diag_summary(scratch / "none", hang, run, []), split_sig),
    )

    check(
        "the signature entries check",
        check_signatures(split_sig + race_sig) == split_sig + race_sig,
    )
    bad_entries = {
        "a list": {"cause": "split"},
        "a launch-end split": [dict(split_sig[0], phase="launch-end")],
        "an extra key": [dict(split_sig[0], line=3)],
        "a split with no file": [{k: v for k, v in split_sig[0].items() if k != "file"}],
        "a split with no title": [{k: v for k, v in split_sig[0].items() if k != "title"}],
        "a split with an empty title": [dict(split_sig[0], title=" ")],
        "a path for a split file": [dict(split_sig[0], file="tests/e2e/capture-inbox.test.ts")],
        "a product race with no MEU": [{k: v for k, v in race_sig[0].items() if k != "meu"}],
        "a path for a file": [dict(race_sig[0], file="ui/tests/e2e/capture-inbox.test.ts")],
        "a text line": [dict(race_sig[0], line="1948")],
        "a lower-case issue": [dict(race_sig[0], issue="hang")],
    }
    for name, raw in bad_entries.items():
        try:
            check_signatures(raw)
            refused = False
        except ValueError:
            refused = True
        check(f"the signature check refuses {name}", refused)
    (scratch / "sig-bad.json").write_bytes(b"[{]")
    try:
        load_signatures(scratch / "sig-bad.json")
        refused = False
    except ValueError:
        refused = True
    check("a signature file that is not JSON is refused", refused)
    check("no --split-hang reads no signature", load_signatures(None) == [])
    hang.excused = excuse(hang, summary, split_sig)
    split_run = RunResult("t-8", 1, 1, [hang], expected=2)
    code, reason = verdict([split_run], [70.0], 60)
    check(
        "an excused hang is counted, not a failure",
        code == 0 and "excused by a registered signature: 1" in reason,
    )
    check("an excused hang is not covered", not hang.covered)
    unexcused = RunResult("t-9", 1, 1, [Failure("a.test.ts", 9, "AC-1", "", hang=True)], expected=2)
    check("a hang with no signature fails the verdict", verdict([unexcused], [70.0], 60)[0] == 1)
    # This call's own folder only: the selftest leaves nothing for a later one to read.
    shutil.rmtree(scratch)
    print(f"flake-run selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def arg_problem(args: argparse.Namespace) -> str:
    """Why these arguments are refused (argparse exits 2), or empty."""
    if not re.fullmatch(r"[a-z0-9-]+", args.label):
        return "--label takes lower-case letters, digits and hyphens"
    if args.churn and args.no_burn:
        return "--churn runs only with the busy children; drop --no-burn"
    if args.split_hang is not None and args.repeat != 1:
        # The failure header names no repeat, so a hang in one repeat could rest on another's.
        return "--split-hang runs only with --repeat 1"
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--kill-check", action="store_true")
    parser.add_argument("--list-check", action="store_true")
    parser.add_argument("--mode", choices=("watched", "full"), default="watched")
    parser.add_argument("--label", default="run")
    parser.add_argument("--out", type=Path, default=Path("C:/Temp/av-kit/e2e-host-parity/flake"))
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--expect-total", type=int, default=0)
    parser.add_argument("--threshold", type=float, default=60.0)
    parser.add_argument("--pre-load", type=float, default=50.0)
    parser.add_argument(
        "--children", type=int, default=0, help="busy children; 0 means os.cpu_count() * 3 // 4"
    )
    parser.add_argument("--run-timeout", type=float, default=3600.0)
    parser.add_argument("--no-burn", action="store_true", help="no busy child, no load condition")
    parser.add_argument(
        "--split-hang", type=Path, default=None, help="D-1150 hang signature file: see 4. above"
    )
    parser.add_argument("--churn", action="store_true", help="D-1146 process-start child: see 2.")
    args = parser.parse_args()
    problem = arg_problem(args)
    if problem:
        parser.error(problem)
    if args.selftest:
        return selftest()
    if args.kill_check:
        return kill_check(args)
    if args.list_check:
        return list_check(args)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
