"""Session 61 dev-app process check (task row 6; plan LOOK_LAUNCH, D-561). A copy of Session 60's (D-458).

`record --root-pid N` runs while the dev app is up. N is the pwsh that row 6 started with
`Start-Process -PassThru`. It waits until the process tree under N holds every role in
`--roles` (an Electron process under ELECTRON_DIR and the backend, by default), then writes
each process in that tree to `--out` as its id, its parent's id, its creation time and a
role from ROLES.

`check --record PATH` runs after Mat quits the app. A process is this launch's when the
record holds its id with the same creation time, or when its parent is this launch's and it
started no earlier than that parent; a recorded process that has exited still counts as the
parent of an orphan it left. Each of this launch's processes still running is listed, and
the run exits 1. `--stop` ends each one by its id, after checking its creation time again,
and then checks once more.

Any other Electron process under ELECTRON_DIR, and any backend wherever its executable is,
is listed as not this launch's and doesn't count: another worktree's app or backend. The
avkit MCP servers (`electron.exe mcp-server/dist/index.js`) never count and are never
stopped. The checker itself, the processes it runs under and the ones it starts never
count, whatever their arguments hold.

Nothing here prints or writes a command line or an executable path. A process is shown as
its id, its parent's id and a role, because the backend's arguments carry the session's
tokens (`ui/src/main/python-manager.ts:17-35`) and an executable path can hold the home
folder (NO_RAW_CONSOLE). Command lines are read only to tell the roles apart.

`--selftest` runs the classifier on synthetic process tables: a clean quit passes, a
leftover and an orphan fail, and a reused id, the checker and its hosts, an MCP server and a
foreign backend don't count. It also proves that no synthetic token, argument or path
reaches the output or the record.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import signal
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ELECTRON_DIR = "p:/av-kit/ui/node_modules/electron/dist/"
BACKEND_MODULE = "-m avkit_api"
MCP_SERVER = "mcp-server/dist/index.js"
ROLES = ("electron", "backend", "mcp-server", "node", "python", "uv", "pwsh", "cmd", "conhost", "other")
QUERY = (
    "Get-CimInstance Win32_Process | Select-Object ProcessId,ParentProcessId,Name,ExecutablePath,"
    "CommandLine,@{n='Created';e={$_.CreationDate.ToFileTimeUtc()}} | ConvertTo-Json -Compress"
)

Proc = dict[str, Any]


def role(p: Proc) -> str:
    """The process's role, from its name, executable and arguments; neither is kept."""
    name = (p.get("name") or "").lower()
    argv = (p.get("argv") or "").replace("\\", "/").lower()
    exe = (p.get("exe") or "").replace("\\", "/").lower()
    if name == "electron.exe":
        if MCP_SERVER in argv:
            return "mcp-server"
        return "electron" if exe.startswith(ELECTRON_DIR) else "other"
    if name.startswith("python") and BACKEND_MODULE in argv:
        return "backend"
    stem = name.removesuffix(".exe")
    if stem in ("powershell", "pwsh"):
        return "pwsh"
    return stem if stem in ROLES else "other"


def snapshot() -> list[Proc]:
    """Every process on the host, from one Win32_Process query."""
    run = subprocess.run(["pwsh", "-NoProfile", "-Command", QUERY], capture_output=True, text=True, check=True)
    rows = json.loads(run.stdout)
    return [
        {
            "pid": int(r["ProcessId"]),
            "ppid": int(r["ParentProcessId"] or 0),
            "name": r.get("Name") or "",
            "exe": r.get("ExecutablePath") or "",
            "argv": r.get("CommandLine") or "",
            "created": int(r["Created"] or 0),
        }
        for r in (rows if isinstance(rows, list) else [rows])
    ]


def descendants(procs: list[Proc], roots: dict[int, int]) -> dict[int, int]:
    """ROOTS (id to creation time) and every running process descended from them.

    A child counts when its parent is in the set and it started no earlier than that parent.
    A root that has exited still parents its orphans, unless a running process with a
    different creation time now holds its id.
    """
    alive = {p["pid"]: p for p in procs}
    found = {pid: created for pid, created in roots.items()}
    changed = True
    while changed:
        changed = False
        for p in procs:
            if p["pid"] in found:
                continue
            parent = found.get(p["ppid"])
            if parent is None:
                continue
            holder = alive.get(p["ppid"])
            if holder is not None and holder["created"] != parent:
                continue
            if p["created"] >= parent:
                found[p["pid"]] = p["created"]
                changed = True
    return found


def checker_ids(procs: list[Proc], self_pid: int) -> set[int]:
    """The checker, the processes it runs under, and the ones it starts."""
    alive = {p["pid"]: p for p in procs}
    ids = {self_pid}
    pid = self_pid
    while pid in alive and alive[pid]["ppid"] not in ids and alive[pid]["ppid"] != 0:
        pid = alive[pid]["ppid"]
        ids.add(pid)
    me = alive.get(self_pid)
    if me is not None:
        ids |= set(descendants(procs, {self_pid: me["created"]}))
    return ids


def classify(procs: list[Proc], record: dict[str, Any], self_pid: int) -> dict[str, list[Proc]]:
    """This launch's processes still running, and the dev-app processes that aren't this launch's."""
    alive = {p["pid"]: p for p in procs}
    skip = checker_ids(procs, self_pid)
    roots = {r["pid"]: r["created"] for r in record["processes"]}
    # A recorded id now held by another process (a different creation time) isn't this launch's.
    roots = {pid: c for pid, c in roots.items() if pid not in alive or alive[pid]["created"] == c}
    owned = descendants(procs, roots)
    mine, foreign = [], []
    for p in procs:
        if p["pid"] in skip:
            continue
        r = role(p)
        if r == "mcp-server":
            continue
        if p["pid"] in owned:
            mine.append(p)
        elif r in ("electron", "backend"):
            foreign.append(p)
    return {"mine": mine, "foreign": foreign}


def line(p: Proc, owner: str) -> str:
    """One process as its id, its parent's id, its role and its owner; nothing from its arguments."""
    return f"  pid {p['pid']} parent {p['ppid']} role {role(p)} {owner}"


def report(result: dict[str, list[Proc]]) -> int:
    for p in result["mine"]:
        print(line(p, "this launch's"))
    for p in result["foreign"]:
        print(line(p, "not this launch's, left alone"))
    print(f"dev-app-procs: {len(result['mine'])} of this launch's left, {len(result['foreign'])} not this launch's")
    return 1 if result["mine"] else 0


def tree_record(procs: list[Proc], root_pid: int) -> dict[str, Any] | None:
    """The record of ROOT_PID's running tree, or None when ROOT_PID isn't running."""
    alive = {p["pid"]: p for p in procs}
    if root_pid not in alive:
        return None
    tree = descendants(procs, {root_pid: alive[root_pid]["created"]})
    rows = [alive[pid] for pid in sorted(tree) if pid in alive]
    return {
        "root_pid": root_pid,
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "processes": [{"pid": p["pid"], "ppid": p["ppid"], "created": p["created"], "role": role(p)} for p in rows],
    }


def cmd_record(args: argparse.Namespace) -> int:
    wanted = [r for r in args.roles.split(",") if r]
    deadline = time.monotonic() + args.wait
    while True:
        record = tree_record(snapshot(), args.root_pid)
        if record is None:
            print(f"FAIL: process {args.root_pid} isn't running; nothing recorded")
            return 1
        roles = {p["role"] for p in record["processes"]}
        missing = [r for r in wanted if r not in roles]
        if not missing or time.monotonic() >= deadline:
            break
        time.sleep(2)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    for p in record["processes"]:
        print(f"  pid {p['pid']} parent {p['ppid']} role {p['role']}")
    if missing:
        print(f"dev-app-procs: recorded {len(record['processes'])}, still missing roles {missing}")
        return 1
    print(f"dev-app-procs: recorded {len(record['processes'])} processes under {args.root_pid}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    record = json.loads(args.record.read_text(encoding="utf-8"))
    result = classify(snapshot(), record, os.getpid())
    code = report(result)
    if not (args.stop and result["mine"]):
        return code
    for p in result["mine"]:
        now = {q["pid"]: q for q in snapshot()}
        if p["pid"] in now and now[p["pid"]]["created"] == p["created"]:
            with contextlib.suppress(OSError):
                os.kill(p["pid"], signal.SIGTERM)
            print(f"  stopped pid {p['pid']}")
    time.sleep(2)
    print("after --stop:")
    return report(classify(snapshot(), record, os.getpid()))


def selftest() -> int:
    secret, mcp_secret, home = "SYNTH-TOKEN-7f3a", "SYNTH-MCP-91c2", "C:\\Users\\synthetic"
    backend_argv = f"{home}\\python.exe -m avkit_api --token {secret} --mcp-token {mcp_secret} --port 0"
    electron = "P:\\av-kit\\ui\\node_modules\\electron\\dist\\electron.exe"

    def proc(pid: int, ppid: int, name: str, created: int, exe: str = "", argv: str = "") -> Proc:
        return {"pid": pid, "ppid": ppid, "name": name, "exe": exe, "argv": argv, "created": created}

    launch = [
        proc(100, 90, "pwsh.exe", 1000, argv="pwsh -NoProfile -Command npm run dev"),
        proc(101, 100, "node.exe", 1010, argv="node electron-vite dev"),
        proc(102, 101, "electron.exe", 1020, electron, f"{electron} ."),
        proc(103, 102, "python.exe", 1030, f"{home}\\venv\\python.exe", backend_argv),
        proc(104, 103, "python.exe", 1031, f"{home}\\base\\python.exe", backend_argv),
    ]
    others = [
        proc(90, 4, "explorer.exe", 10),
        proc(200, 50, "electron.exe", 900, electron, f"{electron} P:\\av-kit\\mcp-server\\dist\\index.js"),
        proc(300, 299, "python.exe", 950, "Q:\\other\\python.exe", backend_argv),
        # The checker's hosts: 399's arguments hold the backend module, as round 1's inline check did.
        proc(399, 50, "python.exe", 1990, argv="python -c \"... '-m avkit_api' ...\""),
        proc(400, 399, "uv.exe", 2000),
        proc(401, 400, "python.exe", 2001, argv="python dev-app-procs.py check"),
        proc(402, 401, "pwsh.exe", 2002, argv="pwsh -NoProfile -Command Get-CimInstance"),
    ]
    record = tree_record(launch + others, 100)
    assert record is not None
    failures: list[str] = []

    def case(name: str, procs: list[Proc], mine: list[int], foreign: list[int], rec: dict[str, Any] = record) -> None:
        result = classify(procs, rec, 401)
        got = (sorted(p["pid"] for p in result["mine"]), sorted(p["pid"] for p in result["foreign"]))
        ok = got == (mine, foreign)
        print(f"{'ok  ' if ok else 'FAIL'} {name}: this launch's {got[0]}, not this launch's {got[1]}")
        if not ok:
            failures.append(name)

    recorded = sorted(p["pid"] for p in record["processes"])
    ok = recorded == [100, 101, 102, 103, 104]
    print(f"{'ok  ' if ok else 'FAIL'} the record holds the launch's tree: {recorded}")
    if not ok:
        failures.append("record")
    case("a clean quit passes", others, [], [300])
    case("a leftover backend fails", others + [launch[4]], [104], [300])
    orphan = proc(105, 103, "python.exe", 1040, argv=backend_argv)
    case("an orphan of an exited recorded process fails", others + [orphan], [105], [300])
    reused = proc(104, 77, "python.exe", 5000, argv=backend_argv)
    case("a reused id is not this launch's", others + [reused], [], [104, 300])
    child_of_reused = proc(106, 104, "node.exe", 5001)
    case("a child of a reused id is not this launch's", others + [reused, child_of_reused], [], [104, 300])
    mcp_under_launch = proc(201, 102, "electron.exe", 1050, electron, f"{electron} P:/av-kit/mcp-server/dist/index.js")
    case("an MCP server never counts", others + launch + [mcp_under_launch], [100, 101, 102, 103, 104], [300])
    case("the checker and its hosts never count", others, [], [300])
    case("a foreign backend and app are only listed", others + [proc(310, 309, "electron.exe", 960, electron)], [], [300, 310])

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        report(classify(others + launch, record, 401))
    printed = out.getvalue() + json.dumps(record)
    leaked = [s for s in (secret, mcp_secret, "--token", "--mcp-token", "avkit_api", "synthetic", "Users", "node_modules") if s in printed]
    ok = not leaked and "pid 104 parent 103 role backend this launch's" in printed
    print(f"{'ok  ' if ok else 'FAIL'} no argument, token or path reaches the output or the record: leaked {leaked}")
    if not ok:
        failures.append("leak")
    roles_missing = tree_record(launch[:3] + others, 100)
    ok = roles_missing is not None and "backend" not in {p["role"] for p in roles_missing["processes"]}
    print(f"{'ok  ' if ok else 'FAIL'} a tree without the backend lacks the role record waits for")
    if not ok:
        failures.append("roles")
    print(f"dev-app-procs selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--selftest", action="store_true")
    sub = parser.add_subparsers(dest="cmd")
    rec = sub.add_parser("record", help="record the launch's process tree")
    rec.add_argument("--root-pid", type=int, required=True)
    rec.add_argument("--out", type=Path, required=True)
    rec.add_argument("--roles", default="electron,backend", help="roles to wait for, comma-separated")
    rec.add_argument("--wait", type=float, default=120.0, help="seconds to wait for the roles")
    chk = sub.add_parser("check", help="list the launch's processes still running")
    chk.add_argument("--record", type=Path, required=True)
    chk.add_argument("--stop", action="store_true", help="end each of this launch's processes by its id")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.cmd == "record":
        return cmd_record(args)
    if args.cmd == "check":
        return cmd_check(args)
    parser.error("give --selftest, record or check")
    return 2


if __name__ == "__main__":
    sys.exit(main())
