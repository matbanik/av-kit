"""Session 90 dev-launch proof (AC-15, AC-16, D-1118, D-1120): does `npm run dev` open a window?

    uv run --no-sync python <plan>/dev-proof.py
        --run-as-node set --expect window --expect-notice yes

Starts `npm --prefix ui run dev` from P:/av-kit (through `cmd.exe /d /c`) with
ELECTRON_RUN_AS_NODE set to "1" (`--run-as-node set`) or removed (`unset`), AVKIT_E2E removed,
and AVKIT_APP_DATA pointed at a scratch folder under C:/Temp/av-kit/test-run-reliability.
The launch runs with CREATE_NO_WINDOW, so its console never shows. Every second the script
takes one process snapshot (`snapshot()` of Session 81's dev-app-procs.py, loaded in place
from DEV_APP_PROCS after its SHA-256 prefix is checked), adds the launch's running tree to
the record, and looks for a visible, titled top-level window of class Chrome_WidgetWin_1
(an Electron BrowserWindow) owned by an Electron process of that tree (EnumWindows and
GetClassNameW; a console window belongs to conhost and a native error dialog has class
#32770, so neither counts). It stops at the first of: a window, the launch's root exiting,
an Electron process it saw earlier exiting, or --timeout seconds.

First of all it runs load-run.py's host-load wait (Session 81 RULE-2, imported in place from
this folder), so a first-run Vite compile isn't timed on a busy host.

Then it writes the record, runs `dev-app-procs.py check --record R --stop` as a child (a
child, so the checker's own exclusions skip this script but not the launch it started), and
re-runs `check --record R` every 2 s for up to 30 s until it exits 0. It removes the scratch
app data with shutil.rmtree and never opens a file in it (the app writes an mcp-token.txt
there). The dev output goes to <out>/dev-proof-<mode>.log; only the notice line is searched.

Preflight: an av-kit dev app that isn't this launch's would hold the "av-kit-ui"
single-instance lock (`ui/src/main/index.ts:99`, taken before userData moves to
AVKIT_APP_DATA), so this launch would quit without a window. Such an app is an
`electron.exe` main process (no `--type=`) whose executable is under an av-kit
`ui/node_modules/electron/dist/` (the main tree P:/av-kit or a worktree P:/av-kit-wt/<name>),
that is not an avkit MCP server and not an E2E launch (which loads main-error-watch.cjs and
skips the lock). Electron apps of other projects (a zorivest lane app, say) use another
lock and are counted as "other" and ignored. The script re-checks every 15 s for up to
--foreign-wait seconds, then exits 2. It never stops a process it didn't start.

Prints: the mode, the host load, `foreign av-kit dev apps: N; other Electron main processes
(ignored): M`, `window: yes|no` with why the wait ended, `notice:
yes|no`, the number of processes recorded, the checker's lines (an id, a parent id and a
role each) and the number left. Never a command line, an argument or a path.

Exit 0: the window and the notice are as expected and nothing of the launch is left.
Exit 1: a mismatch, or a process of the launch is left. Exit 2: setup failed (a foreign
app stayed, the launch didn't start, or its root wasn't seen).

Identities: the record holds each process as (id, creation time) from the first snapshot it
was seen in, and that entry never changes. The launch's root must be this script's child,
started after the launch began. A live process that holds a recorded id with another creation
time is a later holder: it isn't added, its window doesn't count, it passes no ownership on,
and it never reaches the record, so the checker's --stop can't pick it. A window passes only
when its owner still has its recorded identity in a snapshot taken after the windows were
listed.

--selftest checks the environment, the foreign classification, the window class rule, the
notice search, the exit matrix, that no synthetic argument or path reaches the output, and
(through the real run() on synthetic snapshots) that a reused id is never adopted: a recorded
child whose id an unrelated Electron takes, an id reused while the windows were listed, and a
launch id held by another process. It starts no process.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = Path("P:/av-kit")
SCRATCH = Path("C:/Temp/av-kit/test-run-reliability")
NOTICE = "electron-vite-dev: cleared ELECTRON_RUN_AS_NODE"
E2E_WATCH = "main-error-watch.cjs"
LEFT_RE = re.compile(r"dev-app-procs: (\d+) of this launch's left")
LAUNCH = ["cmd.exe", "/d", "/c", "npm", "--prefix", "ui", "run", "dev"]
DEV_APP_PROCS = REPO / "docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py"
DEV_APP_PROCS_SHA = "03053bc97a32"
LOAD_RUN = HERE / "load-run.py"
APP_WINDOW_CLASS = "Chrome_WidgetWin_1"
FILETIME_EPOCH_S = 11_644_473_600
ROOT_SLACK = 10_000_000
AVKIT_ELECTRON = re.compile(
    r'^"?p:/av-kit(?:-wt/[^/"]+)?/ui/node_modules/electron/dist/electron\.exe(?:"|\s|$)'
)

Proc = dict[str, Any]


def load_procs() -> ModuleType:
    """Session 81's checker, in place; exit 2 when its bytes aren't the ones this plan read."""
    digest = hashlib.sha256(DEV_APP_PROCS.read_bytes()).hexdigest()
    if not digest.startswith(DEV_APP_PROCS_SHA):
        print(f"SETUP FAIL: dev-app-procs.py sha256 {digest[:12]}, expected {DEV_APP_PROCS_SHA}")
        raise SystemExit(2)
    spec = importlib.util.spec_from_file_location("dev_app_procs", DEV_APP_PROCS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


procs_mod = load_procs()


def load_run_module() -> ModuleType:
    """This folder's load-run.py, for its host-load wait."""
    spec = importlib.util.spec_from_file_location("load_run", LOAD_RUN)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def proof_env(base: dict[str, str], mode: str, app_data: Path) -> dict[str, str]:
    """A copy of BASE for the launch; BASE itself is not changed."""
    env = {k: v for k, v in base.items() if k.upper() not in ("ELECTRON_RUN_AS_NODE", "AVKIT_E2E")}
    if mode == "set":
        env["ELECTRON_RUN_AS_NODE"] = "1"
    env["AVKIT_APP_DATA"] = str(app_data)
    return env


def classify(p: Proc, own: set[int]) -> str | None:
    """The class of an Electron main process that isn't this launch's, or None.

    foreign: an av-kit dev app, which would hold the lock. other: another project's Electron
    main process, which uses its own lock and is ignored.
    """
    if p["pid"] in own or (p.get("name") or "").lower() != "electron.exe":
        return None
    argv = (p.get("argv") or "").replace("\\", "/")
    if "--type=" in argv or procs_mod.MCP_SERVER in argv or E2E_WATCH in argv:
        return None
    exe = (p.get("exe") or argv).replace("\\", "/").lower()
    return "foreign" if AVKIT_ELECTRON.match(exe) else "other"


def is_foreign(p: Proc, own: set[int]) -> bool:
    return classify(p, own) == "foreign"


def counts_as_app_window(visible: bool, title_len: int, cls: str) -> bool:
    """A visible, titled Electron BrowserWindow; a native dialog (#32770) never counts."""
    return bool(visible) and title_len > 0 and cls == APP_WINDOW_CLASS


def notice_seen(text: str) -> bool:
    return NOTICE in text


def outcome(window: bool, notice: bool, expect_notice: bool, left: int) -> tuple[int, str]:
    """(exit code, reason) for an expected window."""
    problems = []
    if not window:
        problems.append("no window opened")
    if notice != expect_notice:
        seen = "printed" if notice else "missing"
        problems.append(f"notice {seen}, expected {'yes' if expect_notice else 'no'}")
    if left:
        problems.append(f"{left} process(es) of the launch left")
    if problems:
        return 1, "; ".join(problems)
    return 0, "window opened, notice as expected, nothing left"


def window_pids() -> set[int]:
    """Ids of the processes that own a visible, titled Electron top-level window."""
    user32 = ctypes.windll.user32
    found: set[int] = set()
    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

    def visit(hwnd: int, _lparam: int) -> bool:
        buf = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(hwnd, buf, 64)
        visible = bool(user32.IsWindowVisible(hwnd))
        if counts_as_app_window(visible, user32.GetWindowTextLengthW(hwnd), buf.value):
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            found.add(int(pid.value))
        return True

    user32.EnumWindows(proto(visit), 0)
    return found


def electron_mains(own: set[int]) -> tuple[int, int]:
    """(foreign av-kit dev apps, other Electron main processes) in one snapshot."""
    classes = [classify(p, own) for p in procs_mod.snapshot()]
    return classes.count("foreign"), classes.count("other")


def filetime_now() -> int:
    """Now, in the snapshot's creation-time unit (100 ns since 1601, UTC)."""
    return int((time.time() + FILETIME_EPOCH_S) * 10_000_000)


def root_is_launch(p: Proc | None, parent_pid: int, floor: int) -> bool:
    """The first snapshot's row for the launch's id is this script's child, started after FLOOR.

    Popen holds the root's handle, so its id can't be reused during the proof; this check
    still refuses a row held by any other process (a different parent or an older start).
    """
    return p is not None and p["ppid"] == parent_pid and p["created"] >= floor


def collect(snap: list[Proc], seen: dict[int, Proc]) -> set[int]:
    """Add the launch's new processes to SEEN; return the ids running as recorded.

    A recorded (id, creation time) never changes. A live process that holds a recorded id
    with another creation time is a later holder: it isn't written into SEEN, isn't counted as
    running (so its window can't pass), and can't pass ownership to processes it started. A
    new process of the launch that gets a recorded id is left out too; that errs toward a
    failed proof, never toward adopting a stranger, and the checker still finds it under its
    recorded parent.
    """
    alive = {p["pid"]: p for p in snap}
    roots = {
        pid: p["created"]
        for pid, p in seen.items()
        if pid not in alive or alive[pid]["created"] == p["created"]
    }
    running: set[int] = set()
    for pid, created in procs_mod.descendants(snap, roots).items():
        p = alive.get(pid)
        if p is None or p["created"] != created:
            continue
        if pid in seen and seen[pid]["created"] != created:
            continue
        seen.setdefault(pid, p)
        running.add(pid)
    return running


def still_same(pids: set[int], seen: dict[int, Proc], snap: list[Proc]) -> bool:
    """True when one of PIDS runs under its recorded identity in SNAP, taken after the windows
    were listed; a window whose owner's id was reused in between doesn't count."""
    alive = {p["pid"]: p for p in snap}
    return any(pid in alive and alive[pid]["created"] == seen[pid]["created"] for pid in pids)


def record_of(root_pid: int, seen: dict[int, Proc]) -> dict[str, Any]:
    return {
        "root_pid": root_pid,
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "processes": [
            {"pid": p["pid"], "ppid": p["ppid"], "created": p["created"], "role": procs_mod.role(p)}
            for p in sorted(seen.values(), key=lambda q: q["pid"])
        ],
    }


def left_count(text: str) -> int:
    """This launch's processes left, from the checker's last summary line; 1 when there is none."""
    found = LEFT_RE.findall(text)
    return int(found[-1]) if found else 1


def checker(record_path: Path, stop: bool) -> tuple[int, str]:
    argv = [sys.executable, str(DEV_APP_PROCS), "check", "--record", str(record_path)]
    if stop:
        argv.append("--stop")
    run = subprocess.run(argv, capture_output=True, text=True, check=False)
    return run.returncode, run.stdout


def run(args: argparse.Namespace) -> int:
    print(f"dev-proof: run-as-node {args.run_as_node}, expect {args.expect}", end="")
    print(f", expect notice {args.expect_notice}")
    args.out.mkdir(parents=True, exist_ok=True)
    load_run_module().host_load_wait()
    deadline = time.monotonic() + args.foreign_wait
    while True:
        foreign, other = electron_mains({os.getpid()})
        print(f"foreign av-kit dev apps: {foreign};", end="")
        print(f" other Electron main processes (ignored): {other}")
        if not foreign:
            break
        if time.monotonic() >= deadline:
            print("SETUP FAIL: a dev app that isn't this launch's is still running", end="")
            print(f" after {args.foreign_wait} s; left alone")
            return 2
        time.sleep(15)
    app_data = SCRATCH / f"dev-proof-{args.run_as_node}-appdata"
    shutil.rmtree(app_data, ignore_errors=True)
    log_path = args.out / f"dev-proof-{args.run_as_node}.log"
    record_path = args.out / f"dev-proof-{args.run_as_node}-record.json"
    env = proof_env(dict(os.environ), args.run_as_node, app_data)
    floor = filetime_now() - ROOT_SLACK
    try:
        log = log_path.open("wb")
        launch = subprocess.Popen(
            LAUNCH,
            cwd=REPO,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    except OSError as exc:
        if "log" in locals():
            log.close()
        print(f"SETUP FAIL: the launch didn't start ({type(exc).__name__})")
        return 2
    print(f"launch: root pid {launch.pid}")
    seen: dict[int, Proc] = {}
    window = False
    why = "timeout"
    started = time.monotonic()
    electrons: set[int] = set()
    try:
        while time.monotonic() - started < args.timeout:
            snap = procs_mod.snapshot()
            alive = {p["pid"]: p for p in snap}
            if not seen:
                root = alive.get(launch.pid)
                if root is None or not root_is_launch(root, os.getpid(), floor):
                    why = "root not seen"
                    break
                seen[root["pid"]] = root
            running = collect(snap, seen)
            now_electrons = {pid for pid in running if procs_mod.role(alive[pid]) == "electron"}
            hits = window_pids() & now_electrons
            if hits and still_same(hits, seen, procs_mod.snapshot()):
                window, why = True, "window"
                break
            if electrons - now_electrons:
                why = "electron exited"
                break
            electrons |= now_electrons
            if launch.poll() is not None:
                why = "root exited"
                break
            time.sleep(1)
    finally:
        record_path.write_text(
            json.dumps(record_of(launch.pid, seen), indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        code, text = checker(record_path, stop=True)
        print(text.rstrip())
        left_code, left_text = code, text
        settle = time.monotonic() + 30
        while left_code != 0 and time.monotonic() < settle:
            time.sleep(2)
            left_code, left_text = checker(record_path, stop=False)
        print("final check:")
        print(left_text.rstrip())
        try:
            launch.wait(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        log.close()
        shutil.rmtree(app_data, ignore_errors=True)
    elapsed = round(time.monotonic() - started)
    notice = notice_seen(log_path.read_bytes().decode("utf-8", "replace"))
    left = left_count(left_text) if left_code != 0 else 0
    print(f"window: {'yes' if window else 'no'} (after {elapsed} s; {why})")
    print(f"notice: {'yes' if notice else 'no'}")
    print(f"processes recorded: {len(seen)}")
    print(f"left: {left}")
    if why == "root not seen":
        print("SETUP FAIL: the launch's root wasn't in the first snapshot as this script's child")
        return 2
    code, reason = outcome(window, notice, args.expect_notice == "yes", left)
    print(("PASS: " if code == 0 else "FAIL: ") + reason)
    return code


def simulate(
    snaps: list[list[Proc]], windows: set[int], polls: list[int | None]
) -> tuple[int, str, dict[str, Any], list[tuple[int, int, int]]]:
    """The real run() on synthetic snapshots, with the launch, the windows, the checker, the
    host-load wait and the scratch removal replaced; starts and stops no process.

    Returns (exit code, output, the cleanup record, the identities the inherited checker's
    classify() would stop for that record against the last snapshot).
    """
    import contextlib
    import io
    from unittest import mock

    queue = list(snaps)
    taken: list[list[Proc]] = []

    def next_snapshot() -> list[Proc]:
        snap = queue.pop(0) if len(queue) > 1 else queue[0]
        taken.append(snap)
        return snap

    poll_queue = list(polls)

    class Launch:
        pid = 100

        def poll(self) -> int | None:
            return poll_queue.pop(0) if len(poll_queue) > 1 else poll_queue[0]

        def wait(self, timeout: float) -> int:
            return 0

    records: list[dict[str, Any]] = []
    candidates: list[tuple[int, int, int]] = []

    def fake_checker(record_path: Path, stop: bool) -> tuple[int, str]:
        record = json.loads(record_path.read_text(encoding="utf-8"))
        records.append(record)
        mine = procs_mod.classify(taken[-1], record, 800)["mine"]
        candidates[:] = [(p["pid"], p["created"], p["ppid"]) for p in mine]
        return 0, "dev-app-procs: 0 of this launch's left, 0 not this launch's\n"

    args = argparse.Namespace(
        out=SCRATCH / "dev-proof-selftest",
        run_as_node="unset",
        expect="window",
        expect_notice="no",
        timeout=60.0,
        foreign_wait=0.0,
    )
    out = io.StringIO()
    replaced = {
        "load_run_module": mock.MagicMock(),
        "electron_mains": mock.MagicMock(return_value=(0, 0)),
        "window_pids": mock.MagicMock(return_value=set(windows)),
        "checker": mock.MagicMock(side_effect=fake_checker),
    }
    with (
        mock.patch.dict(globals(), replaced),
        mock.patch.object(procs_mod, "snapshot", side_effect=next_snapshot),
        mock.patch.object(subprocess, "Popen", return_value=Launch()),
        mock.patch.object(shutil, "rmtree"),
        mock.patch.object(time, "sleep"),
        contextlib.redirect_stdout(out),
    ):
        code = run(args)
    return code, out.getvalue(), records[-1] if records else {}, candidates


def reuse_cases(check: Any) -> None:
    """R1-F1: a recorded id reused by an unrelated process is never adopted."""
    t = filetime_now() + 100_000_000
    me = os.getpid()
    electron = "P:/av-kit/ui/node_modules/electron/dist/electron.exe"

    def row(pid: int, ppid: int, created: int, name: str, exe: str = "") -> Proc:
        return {"pid": pid, "ppid": ppid, "created": created, "name": name, "exe": exe, "argv": ""}

    root = row(100, me, t, "cmd.exe")

    def entry(record: dict[str, Any], pid: int) -> tuple[int, int, int] | None:
        for p in record.get("processes", []):
            if p["pid"] == pid:
                return p["pid"], p["created"], p["ppid"]
        return None

    child = row(101, 100, t + 10, "node.exe")
    stranger = row(101, 999, t + 4_000, "electron.exe", electron)
    code, text, record, stop = simulate([[root, child], [root, stranger]], {101}, [None, 0])
    check(
        f"a recorded child's id reused by an unrelated Electron: no window pass (exit {code})",
        code == 1 and "window: no" in text,
    )
    check(
        "the reused id keeps its recorded identity in the cleanup record",
        entry(record, 101) == (101, t + 10, 100),
    )
    check(
        f"the unrelated identity is never a stop candidate: {len(stop)} candidate(s)",
        (101, t + 4_000, 999) not in stop and all(c[1] != t + 4_000 for c in stop),
    )

    app = row(102, 100, t + 20, "electron.exe", electron)
    code, text, record, stop = simulate([[root, app]], {102}, [None])
    check(f"the launch's own Electron window passes (exit {code})", code == 0)

    swapped = row(102, 999, t + 5_000, "electron.exe", electron)
    code, text, record, stop = simulate([[root, app], [root, swapped]], {102}, [None])
    check(
        f"an id reused while the windows were listed doesn't pass (exit {code})",
        code == 1 and "window: no" in text and entry(record, 102) == (102, t + 20, 100),
    )
    check("nor is its new holder a stop candidate", (102, t + 5_000, 999) not in stop)

    reused_root = row(100, 999, t, "cmd.exe")
    code, text, record, stop = simulate([[reused_root]], {100}, [None])
    check(
        f"a launch id held by another process is a setup failure (exit {code})",
        code == 2 and not record.get("processes") and not stop,
    )
    old_root = row(100, me, t - 900_000_000, "cmd.exe")
    code, text, record, stop = simulate([[old_root]], set(), [None])
    check(f"a launch id held by an older process is a setup failure (exit {code})", code == 2)


def selftest() -> int:
    failures: list[str] = []

    def check(name: str, ok: bool) -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}")
        if not ok:
            failures.append(name)

    home = "C:\\Users\\synthetic"
    base = {"PATH": "x", "ELECTRON_RUN_AS_NODE": "1", "AVKIT_E2E": "1", "KEEP": "k"}
    frozen = dict(base)
    scratch = Path("C:/Temp/av-kit/test-run-reliability/dev-proof-set-appdata")
    env_set = proof_env(base, "set", scratch)
    env_unset = proof_env(base, "unset", scratch)
    check("set mode sets the variable to 1", env_set.get("ELECTRON_RUN_AS_NODE") == "1")
    check("unset mode removes the variable", "ELECTRON_RUN_AS_NODE" not in env_unset)
    check(
        "AVKIT_E2E is removed in both", "AVKIT_E2E" not in env_set and "AVKIT_E2E" not in env_unset
    )
    check(
        "scratch app data is set and other keys kept",
        env_set["AVKIT_APP_DATA"] == str(scratch) and env_set["KEEP"] == "k",
    )
    check("the base environment is unchanged", base == frozen)

    electron = "P:\\av-kit-wt\\x\\ui\\node_modules\\electron\\dist\\electron.exe"

    def proc(pid: int, name: str, argv: str) -> Proc:
        return {"pid": pid, "ppid": 1, "name": name, "exe": electron, "argv": argv, "created": pid}

    other_app = proc(10, "electron.exe", f"{electron} . --token SYNTH-TOKEN-7f3a")
    renderer = proc(11, "electron.exe", f"{electron} --type=renderer {home}\\x")
    mcp = proc(12, "electron.exe", f"{electron} P:\\av-kit\\mcp-server\\dist\\index.js")
    e2e = proc(
        13,
        "electron.exe",
        f"{electron} -r P:\\av-kit\\ui\\tests\\e2e\\main-error-watch.cjs out\\main\\index.js",
    )
    own = proc(14, "electron.exe", f"{electron} .")
    backend = proc(15, "python.exe", f"{home}\\python.exe -m avkit_api --token SYNTH-TOKEN-7f3a")
    main_tree = {
        **proc(16, "electron.exe", "x ."),
        "exe": "P:\\av-kit\\ui\\node_modules\\electron\\dist\\electron.exe",
    }
    zorivest = {
        **proc(17, "electron.exe", "x ."),
        "exe": "P:\\zorivest-wt\\x\\ui\\node_modules\\electron\\dist\\electron.exe",
    }
    no_exe = {
        **proc(18, "electron.exe", f'"{electron}" .'),
        "exe": "",
    }
    lookalike = {
        **proc(19, "electron.exe", "x ."),
        "exe": "P:\\av-kit-backup\\ui\\node_modules\\electron\\dist\\electron.exe",
    }
    table = [other_app, renderer, mcp, e2e, own, backend, main_tree, zorivest, no_exe, lookalike]
    got = sorted(p["pid"] for p in table if is_foreign(p, {14}))
    check(f"only other av-kit dev apps are foreign: {got}", got == [10, 16, 18])
    others = sorted(p["pid"] for p in table if classify(p, {14}) == "other")
    check(f"another project's Electron is other, not foreign: {others}", others == [17, 19])

    check("a titled Electron window counts", counts_as_app_window(True, 6, APP_WINDOW_CLASS))
    check("a native dialog doesn't count", not counts_as_app_window(True, 5, "#32770"))
    check("an untitled window doesn't count", not counts_as_app_window(True, 0, APP_WINDOW_CLASS))
    check("a hidden window doesn't count", not counts_as_app_window(False, 6, APP_WINDOW_CLASS))
    check("the host-load wait is importable", callable(load_run_module().host_load_wait))

    check("the notice is found", notice_seen(f"x\n{NOTICE} for this dev launch\ny"))
    check(
        "no notice without the line",
        not notice_seen("vite dev server running\nstart electron app...\n"),
    )

    check("window, notice expected and seen, nothing left: 0", outcome(True, True, True, 0)[0] == 0)
    check("window, no notice expected and none seen: 0", outcome(True, False, False, 0)[0] == 0)
    check("no window: 1", outcome(False, True, True, 0)[0] == 1)
    check("notice missing: 1", outcome(True, False, True, 0)[0] == 1)
    check("notice unexpected: 1", outcome(True, True, False, 0)[0] == 1)
    check("a process left: 1", outcome(True, True, True, 1)[0] == 1)

    import contextlib
    import io

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        print(json.dumps(record_of(14, {p["pid"]: p for p in table})))
        print(outcome(False, True, True, 2)[1])
    printed = out.getvalue()
    leaked = [
        s
        for s in (
            "SYNTH-TOKEN",
            "--token",
            "avkit_api",
            "synthetic",
            "Users",
            "node_modules",
            "--type=",
        )
        if s in printed
    ]
    check(f"no argument, token or path reaches the output: leaked {leaked}", not leaked)
    summary = (
        "dev-app-procs: 2 of this launch's left, 0 not this launch's\n"
        "after --stop:\n"
        "dev-app-procs: 0 of this launch's left, 1 not this launch's\n"
    )
    check("the left count reads the last summary", left_count(summary) == 0)
    check("the left count without a summary is 1", left_count("") == 1)
    check("the window enumeration runs", isinstance(window_pids(), set))
    reuse_cases(check)
    print(f"dev-proof selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--run-as-node", choices=("set", "unset"))
    parser.add_argument("--expect", choices=("window",), default="window")
    parser.add_argument("--expect-notice", choices=("yes", "no"))
    parser.add_argument("--out", type=Path, default=SCRATCH)
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--foreign-wait", type=float, default=600.0)
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.run_as_node is None or args.expect_notice is None:
        parser.error("give --run-as-node and --expect-notice, or --selftest")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
