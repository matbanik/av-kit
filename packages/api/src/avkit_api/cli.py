"""Runtime CLI: bind localhost, write the descriptor, print READY_LINE."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import uvicorn

from avkit_api.main import create_app
from avkit_api.wiring import build_services

BIND_HOST = "127.0.0.1"
DESCRIPTOR_FILENAME = "backend.json"
PORT_SIBLING_FILENAME = "backend-port.txt"
READY_PREFIX = "AVKIT_READY"
_LAUNCHER_NAMES = frozenset({"python.exe", "pythonw.exe", "uv.exe"})


def _process_image(pid: int) -> Path | None:
    """Return the on-disk image for `pid`, or None if the query fails."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        query = kernel32.OpenProcess
        query.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        query.restype = wintypes.HANDLE
        handle = query(0x1000, False, pid)
        if not handle:
            return None
        try:
            get_name = kernel32.QueryFullProcessImageNameW
            get_name.argtypes = [
                wintypes.HANDLE,
                wintypes.DWORD,
                wintypes.LPWSTR,
                ctypes.POINTER(wintypes.DWORD),
            ]
            get_name.restype = wintypes.BOOL
            size = wintypes.DWORD(32768)
            buf = ctypes.create_unicode_buffer(size.value)
            if not get_name(handle, 0, buf, ctypes.byref(size)):
                return None
            return Path(buf.value)
        finally:
            kernel32.CloseHandle(handle)
    try:
        return Path(os.readlink(f"/proc/{pid}/exe"))
    except OSError:
        return None


def _parent_pid(pid: int) -> int | None:
    """Return the parent pid of `pid` (Windows toolhelp / Linux proc)."""
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class _Entry(ctypes.Structure):
            _fields_ = [
                ("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", wintypes.WCHAR * 260),
            ]

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        snap = kernel32.CreateToolhelp32Snapshot(0x2, 0)
        if snap == -1:
            return None
        try:
            entry = _Entry()
            entry.dwSize = ctypes.sizeof(_Entry)
            ok = kernel32.Process32FirstW(snap, ctypes.byref(entry))
            while ok:
                if entry.th32ProcessID == pid:
                    return int(entry.th32ParentProcessID)
                ok = kernel32.Process32NextW(snap, ctypes.byref(entry))
            return None
        finally:
            kernel32.CloseHandle(snap)
    try:
        status = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
    except OSError:
        return None
    for line in status.splitlines():
        if line.startswith("PPid:"):
            return int(line.split()[1])
    return None


def _is_launcher(path: Path | None) -> bool:
    if path is None:
        return False
    return path.name.lower() in _LAUNCHER_NAMES


def owned_pid() -> int:
    """Pid the spawn parent observes.

    uv's Windows venv `python.exe` is a trampoline that stays as the parent of
    the real interpreter. Both images are named python.exe, so we detect a
    two-level Python launch (pytest → trampoline → CLI) and publish the
    trampoline pid. Electron spawns `PYTHON_IMAGE` directly (parent is not a
    Python launcher), so ChildProcess.pid matches `os.getpid()`.
    """
    current = os.getpid()
    parent = os.getppid()
    if not _is_launcher(_process_image(parent)):
        return current
    grandparent = _parent_pid(parent)
    if grandparent is None:
        return current
    if _is_launcher(_process_image(grandparent)):
        return parent
    return current


@dataclass(frozen=True)
class CliArgs:
    token: str
    mcp_token: str
    port: int
    app_data: Path


def parse_args(argv: list[str] | None = None) -> CliArgs:
    """Parse SPAWN_FLAGS. Unknown flags and blank tokens exit nonzero."""
    parser = argparse.ArgumentParser(prog="avkit_api")
    parser.add_argument("--token", required=True)
    parser.add_argument("--mcp-token", required=True)
    parser.add_argument("--port", required=True, type=int)
    parser.add_argument("--app-data", required=True)
    ns = parser.parse_args(argv)
    if ns.port < 0:
        parser.error("--port must be >= 0")
    token = str(ns.token)
    mcp_token = str(ns.mcp_token)
    if token.strip() == "":
        parser.error("--token must be non-blank")
    if mcp_token.strip() == "":
        parser.error("--mcp-token must be non-blank")
    return CliArgs(
        token=token,
        mcp_token=mcp_token,
        port=int(ns.port),
        app_data=Path(ns.app_data),
    )


def write_descriptor(
    *,
    app_data: Path,
    pid: int,
    instance_id: str,
    executable_path: str,
    host: str,
    port: int,
    token: str,
    mcp_token: str,
) -> dict[str, object]:
    """Atomically write backend.json without secrets. token/mcp_token are accepted and discarded."""
    del token, mcp_token
    root = Path(app_data)
    root.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {
        "schema_version": 1,
        "pid": pid,
        "instance_id": instance_id,
        "executable_path": executable_path,
        "host": host,
        "port": port,
        "bind": host,
        "api_base": f"http://{host}:{port}/api/v1",
        "app_data": str(root),
        "started_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    dest = root / DESCRIPTOR_FILENAME
    tmp = root / f".backend.json.{pid}.tmp"
    tmp.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, dest)
    (root / PORT_SIBLING_FILENAME).write_text(str(port), encoding="utf-8")
    return payload


def main(argv: list[str] | None = None) -> int:
    """Bind 127.0.0.1, write the descriptor, print READY_LINE, then serve."""
    args = parse_args(argv)
    args.app_data.mkdir(parents=True, exist_ok=True)
    services, dispose = build_services(app_data=args.app_data)
    app = create_app(
        tokens=frozenset({args.token, args.mcp_token}),
        services=services,
        engine_dispose=dispose,
    )
    instance_id = str(uuid4())
    config = uvicorn.Config(
        app,
        host=BIND_HOST,
        port=args.port,
        log_level="warning",
        access_log=False,
    )
    sock = config.bind_socket()
    bound_port = int(sock.getsockname()[1])
    write_descriptor(
        app_data=args.app_data,
        pid=owned_pid(),
        instance_id=instance_id,
        executable_path=str(Path(sys.executable).resolve()),
        host=BIND_HOST,
        port=bound_port,
        token=args.token,
        mcp_token=args.mcp_token,
    )
    print(f"{READY_PREFIX} port={bound_port} instance={instance_id}", flush=True)
    server = uvicorn.Server(config)
    server.run(sockets=[sock])
    return 0
