"""Session 61 Electron precheck (task rows 0, 3, 4 and 5, and the gate's hotkey-free step; plan §1 item 6, S6).

The E2E suite registers F2 as the global capture hotkey (`ui/tests/e2e/capture-inbox.test.ts:84`).
Another program holding F2 makes that test fail on setup, not on its assertion. This check
registers F2 itself through `user32.RegisterHotKey` with no window, releases it at once, and
names Windows' error when the key is taken (1409, ERROR_HOTKEY_ALREADY_REGISTERED). Holding the
key for a moment can't disturb a holder: a registration that fails changes nothing, and one
that succeeds is released before the next line runs.

It also lists any Electron process whose executable is under ELECTRON_DIR, as its id and its
parent's id only (Session 57 RULE-4): a dev app or an E2E run of this work tree still up. The
avkit MCP servers (`electron.exe mcp-server/dist/index.js`) run the same binary and never
count. Command lines are read only to tell them apart and are never printed.

New in Session 61: the paste proof (AC-132.23) reads and writes the system clipboard, which
only one program can hold open at a time. This check opens the clipboard with
`OpenClipboard(NULL)` and closes it on the next line, reading no data and emptying nothing, so
the clipboard's contents and owner are unchanged. A copy elsewhere holds it open for a few
milliseconds, so it tries CLIPBOARD_TRIES times CLIPBOARD_GAP_S apart; only when every try
fails does it name the holder: `GetOpenClipboardWindow`'s window class and process id, never a
path or a title.

The backend binds port 0 (`ui/src/main/python-manager.ts:31-32`), so no port is checked.

Exit 0 when F2 is free, no such process runs and the clipboard opens; 1 otherwise, naming which
(S6: stop and tell Mat; free it only by a recorded process id, never by name, and never stop
another program).

`--selftest` runs the error reading, the process filter and the clipboard reading on fixtures.
It registers no key, reads no process and never opens the clipboard.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import subprocess
import sys
import time
from typing import Any

VK_F2 = 0x71
HOTKEY_ID = 0x6161
ERROR_HOTKEY_ALREADY_REGISTERED = 1409
ELECTRON_DIR = "p:/av-kit/ui/node_modules/electron/dist/"
MCP_SERVER = "mcp-server/dist/index.js"
CLIPBOARD_TRIES = 5
CLIPBOARD_GAP_S = 0.1
QUERY = (
    "Get-CimInstance Win32_Process -Filter \"Name='electron.exe'\" | "
    "Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
)

Proc = dict[str, Any]


def read_hotkey(registered: bool, error: int) -> tuple[bool, str]:
    """Whether F2 is free, and the line that says so, from one RegisterHotKey result."""
    if registered:
        return True, "F2 free: RegisterHotKey succeeded and was released"
    if error == ERROR_HOTKEY_ALREADY_REGISTERED:
        return False, "F2 taken: error 1409 (ERROR_HOTKEY_ALREADY_REGISTERED); another program holds the global hotkey (S6)"
    return False, f"F2 not registrable: error {error}; the E2E hotkey test can't register it either (S6)"


def probe_hotkey() -> tuple[bool, int]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.RegisterHotKey.argtypes = (ctypes.c_void_p, ctypes.c_int, ctypes.c_uint, ctypes.c_uint)
    user32.UnregisterHotKey.argtypes = (ctypes.c_void_p, ctypes.c_int)
    ok = bool(user32.RegisterHotKey(None, HOTKEY_ID, 0, VK_F2))
    error = 0 if ok else ctypes.get_last_error()
    if ok and not user32.UnregisterHotKey(None, HOTKEY_ID):
        print(f"UnregisterHotKey failed: error {ctypes.get_last_error()}")
    return ok, error


def read_clipboard(opened: bool, tries: int, error: int, holder_class: str | None, holder_pid: int | None) -> tuple[bool, str]:
    """Whether the clipboard is free, and the line that says so, from the last OpenClipboard try."""
    if opened:
        return True, f"clipboard free: OpenClipboard succeeded on try {tries} and was closed at once; no data read"
    if holder_class is None:
        holder = "no window holds it open (GetOpenClipboardWindow returned NULL)"
    else:
        # A window class is a registered name, never a path; keep it short and printable.
        safe = "".join(ch for ch in holder_class if ch.isprintable())[:64]
        holder = f"window class {safe!r}, process {holder_pid}"
    return False, f"clipboard held: OpenClipboard failed {tries} times, last error {error}; {holder} (S6)"


def probe_clipboard() -> tuple[bool, int, int, str | None, int | None]:
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.OpenClipboard.argtypes = (ctypes.c_void_p,)
    user32.OpenClipboard.restype = ctypes.c_int
    user32.CloseClipboard.restype = ctypes.c_int
    user32.GetOpenClipboardWindow.restype = ctypes.c_void_p
    user32.GetClassNameW.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int)
    user32.GetWindowThreadProcessId.argtypes = (ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong))
    error = 0
    for attempt in range(1, CLIPBOARD_TRIES + 1):
        if user32.OpenClipboard(None):
            if not user32.CloseClipboard():
                print(f"CloseClipboard failed: error {ctypes.get_last_error()}")
            return True, attempt, 0, None, None
        error = ctypes.get_last_error()
        if attempt < CLIPBOARD_TRIES:
            time.sleep(CLIPBOARD_GAP_S)
    hwnd = user32.GetOpenClipboardWindow()
    if not hwnd:
        return False, CLIPBOARD_TRIES, error, None, None
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    pid = ctypes.c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return False, CLIPBOARD_TRIES, error, buf.value, int(pid.value)


def worktree_electron(procs: list[Proc]) -> list[Proc]:
    """The Electron processes under ELECTRON_DIR that aren't an avkit MCP server."""
    found = []
    for p in procs:
        if (p.get("name") or "").lower() != "electron.exe":
            continue
        exe = (p.get("exe") or "").replace("\\", "/").lower()
        argv = (p.get("argv") or "").replace("\\", "/").lower()
        if exe.startswith(ELECTRON_DIR) and MCP_SERVER not in argv:
            found.append(p)
    return found


def snapshot() -> list[Proc]:
    run = subprocess.run(["pwsh", "-NoProfile", "-Command", QUERY], capture_output=True, text=True, check=True)
    if not run.stdout.strip():
        return []
    rows = json.loads(run.stdout)
    return [
        {
            "pid": int(r["ProcessId"]),
            "ppid": int(r["ParentProcessId"] or 0),
            "name": r.get("Name") or "",
            "exe": r.get("ExecutablePath") or "",
            "argv": r.get("CommandLine") or "",
        }
        for r in (rows if isinstance(rows, list) else [rows])
    ]


def report(free: bool, line: str, electron: list[Proc], clip_free: bool = True, clip_line: str = "") -> int:
    print(line)
    for p in electron:
        print(f"electron process from this work tree: pid {p['pid']} parent {p['ppid']} (S6)")
    print(f"electron processes from this work tree: {len(electron)}")
    if clip_line:
        print(clip_line)
    ok = free and not electron and clip_free
    print("hotkey-free: ok" if ok else "hotkey-free: blocked (S6)")
    return 0 if ok else 1


def selftest() -> int:
    wrong = 0

    def expect(label: str, got: object, want: object) -> None:
        nonlocal wrong
        status = "ok" if got == want else "WRONG"
        if got != want:
            wrong += 1
        print(f"{status} {label}: got {got!r} want {want!r}")

    expect("registered", read_hotkey(True, 0)[0], True)
    free, line = read_hotkey(False, 1409)
    expect("1409 taken", free, False)
    expect("1409 named", "1409" in line and "ALREADY_REGISTERED" in line, True)
    free, line = read_hotkey(False, 5)
    expect("other error", free, False)
    expect("other error named", "error 5" in line, True)

    secret = "C:/Users/someone/AppData tok_SELFTEST_SECRET"
    table = [
        {"pid": 10, "ppid": 1, "name": "electron.exe", "exe": "P:\\av-kit\\ui\\node_modules\\electron\\dist\\electron.exe", "argv": f". {secret}"},
        {"pid": 11, "ppid": 1, "name": "electron.exe", "exe": "P:/av-kit/ui/node_modules/electron/dist/electron.exe", "argv": f"P:\\av-kit\\mcp-server\\dist\\index.js {secret}"},
        {"pid": 12, "ppid": 1, "name": "electron.exe", "exe": "P:/av-kit-wt/other/ui/node_modules/electron/dist/electron.exe", "argv": secret},
        {"pid": 13, "ppid": 1, "name": "Code.exe", "exe": "P:/av-kit/ui/node_modules/electron/dist/Code.exe", "argv": secret},
        {"pid": 14, "ppid": 10, "name": "ELECTRON.EXE", "exe": "p:/av-kit/ui/node_modules/electron/dist/electron.exe", "argv": "--type=renderer"},
    ]
    expect("filter", [p["pid"] for p in worktree_electron(table)], [10, 14])
    expect("empty table", worktree_electron([]), [])

    # The clipboard reading (Session 61).
    clip_free, clip_line = read_clipboard(True, 2, 0, None, None)
    expect("clipboard opened", clip_free, True)
    expect("clipboard opened names the try", "try 2" in clip_line and "no data read" in clip_line, True)
    held, held_line = read_clipboard(False, CLIPBOARD_TRIES, 5, "Chrome_WidgetWin_1", 4242)
    expect("clipboard held", held, False)
    expect("clipboard holder named", "Chrome_WidgetWin_1" in held_line and "4242" in held_line and "error 5" in held_line, True)
    nobody, nobody_line = read_clipboard(False, CLIPBOARD_TRIES, 5, None, None)
    expect("clipboard held by no window", nobody, False)
    expect("clipboard no window named", "NULL" in nobody_line, True)
    _, odd_line = read_clipboard(False, CLIPBOARD_TRIES, 5, "A\x07B\nC" + "x" * 100, 1)
    expect("clipboard class is printable and short", "\x07" not in odd_line and "\n" not in odd_line and "x" * 70 not in odd_line, True)

    import contextlib
    import io

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = report(True, read_hotkey(True, 0)[1], worktree_electron(table), clip_free, clip_line)
    text = buf.getvalue()
    expect("process blocks", code, 1)
    expect("no secret, path or argument printed", any(s in text for s in ("SELFTEST_SECRET", "Users", "av-kit", ".exe")), False)
    with contextlib.redirect_stdout(io.StringIO()):
        clean = report(True, "free", [], True, clip_line)
        taken = report(False, "taken", [], True, clip_line)
        clip_blocks = report(True, "free", [], False, held_line)
    expect("clean passes", clean, 0)
    expect("taken blocks", taken, 1)
    expect("held clipboard blocks", clip_blocks, 1)

    print(f"hotkey-free selftest: {wrong} wrong")
    return 1 if wrong else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if sys.platform != "win32":
        print("hotkey-free: Windows only")
        return 2
    ok, error = probe_hotkey()
    free, line = read_hotkey(ok, error)
    opened, tries, clip_error, holder_class, holder_pid = probe_clipboard()
    clip_free, clip_line = read_clipboard(opened, tries, clip_error, holder_class, holder_pid)
    return report(free, line, worktree_electron(snapshot()), clip_free, clip_line)


if __name__ == "__main__":
    sys.exit(main())
