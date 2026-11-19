"""Capture the eval harness `describe` output as raw bytes (Session 95, D-1201 A).

Step 3 of eval-run.md used to capture `describe` through a shell redirect, and PowerShell decoded
the server's UTF-8 through the console code page on the way to the file (the issue named in
eval-run.md's dated note). This script runs the harness in a subprocess with its
stdout piped, so no shell sits between the server and the receipt, and writes the bytes as they
came.

    eval-describe.py capture ROOT OUT   run eval-harness.ts describe over ROOT; write stdout to OUT
    eval-describe.py check FILE         apply the capture's refusals to a saved receipt

The mojibake pattern and the CUT line are Session 92's (docs/execution/plans/
2026-11-17-mcp-audit-refresh/eval-rerun.py, D-1186), read from the loaded module at each call;
this file holds no second pattern. When that module cannot load, every command exits 2 and runs
nothing.

Run with `uv run python`. Output is ASCII. Exit 0 when the bytes pass, 1 on a refusal (`refused:`
and each reason: empty, bom, not-utf8, cr, mojibake, cut, harness-exit, timeout), 2 on a usage or
input error, an existing output file, or a guard that did not load. `capture` never overwrites a
file: it exits 2 when OUT, OUT.stderr.txt or OUT.refused exists, and creates each file it writes
with exclusive create; a write or close that fails removes the file it created and exits 2. A
refused capture writes no OUT and keeps the bytes as OUT.refused.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
MCP_DIR = REPO / "mcp-server"
# Relative to MCP_DIR, as step 3 ran it.
HARNESS = "../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts"
DIST = MCP_DIR / "dist/index.js"
TSX = MCP_DIR / "node_modules/tsx/dist/cli.mjs"
BASE = "C:/Temp/av-kit/s64/eval/"
DESCRIBE_TIMEOUT_S = 300
DRAIN_TIMEOUT_S = 30
GUARD_PATH = REPO / "docs/execution/plans/2026-11-17-mcp-audit-refresh/eval-rerun.py"
GUARD_ERRORS = (ImportError, OSError, SyntaxError)
USAGE = "usage: eval-describe.py capture ROOT OUT | eval-describe.py check FILE"
BOMS = (b"\xef\xbb\xbf", b"\xff\xfe", b"\xfe\xff")


class UsageError(Exception):
    """A bad argument or a missing prerequisite: exit 2."""


def load_guard(path: Path = GUARD_PATH):
    """Session 92's eval-rerun.py as a module; no .pyc is written into its folder."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("s92_eval_rerun", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {Path(path).as_posix()}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    missing = [n for n in ("MOJIBAKE", "CUT") if not hasattr(module, n)]
    if missing:
        raise ImportError(f"{Path(path).as_posix()} lacks {missing}")
    return module


try:
    GUARD = load_guard()
    GUARD_ERROR = ""
except GUARD_ERRORS as exc:
    GUARD = None
    GUARD_ERROR = f"{GUARD_PATH.as_posix()}: {type(exc).__name__}: {exc}"


def asc(text: str) -> str:
    """Text made ASCII for printing (non-ASCII characters as escapes)."""
    return text.encode("ascii", "backslashreplace").decode("ascii")


def refusals(data: bytes) -> list[tuple[str, str]]:
    """The reasons a raw describe capture is refused, in order; empty when it passes."""
    if not data:
        return [("empty", "no bytes")]
    found: list[tuple[str, str]] = []
    bom = next((b for b in BOMS if data.startswith(b)), None)
    if bom is not None:
        found.append(("bom", f"starts with {bom.hex(' ').upper()}"))
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        found.append(("not-utf8", f"invalid UTF-8 at byte offset {exc.start}"))
        return found
    crs = data.count(b"\r")
    if crs:
        found.append(("cr", f"{crs} CR byte(s)"))
    matches = list(GUARD.MOJIBAKE.finditer(text))
    if matches:
        first = matches[0]
        found.append(
            (
                "mojibake",
                f"{len(matches)} match(es), the first at character offset {first.start()}: "
                f"{ascii(first.group(0))}",
            )
        )
    cuts = text.replace("\r\n", "\n").split("\n").count(GUARD.CUT)
    if cuts != 1:
        found.append(("cut", f"{cuts} CUT line(s), expected exactly 1"))
    return found


def report(reasons: list[tuple[str, str]]) -> None:
    print("refused:")
    for name, detail in reasons:
        print(f"  {name}: {asc(detail)}")


def command(root: str) -> tuple[list[str], Path]:
    """The harness command and its working folder (the test seam)."""
    node = shutil.which("node")
    if node is None:
        raise UsageError("node is not on PATH")
    if not TSX.is_file():
        raise UsageError(f"the tsx CLI is missing: {TSX.as_posix()} (npm install in mcp-server)")
    if not DIST.is_file():
        raise UsageError(f"{DIST.as_posix()} is missing: build first (eval-run.md step 2)")
    if not (MCP_DIR / HARNESS).is_file():
        raise UsageError(f"the harness is missing: {(MCP_DIR / HARNESS).resolve().as_posix()}")
    return [node, str(TSX), HARNESS, root, "describe"], MCP_DIR


def stop(proc: subprocess.Popen) -> None:
    """Stop the recorded child (and its tree on Windows) by its pid only."""
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, check=False
        )
    else:
        proc.kill()


def write_new(path: Path, data: bytes) -> None:
    """Create PATH with exclusive create and write DATA; on any error remove only that file."""
    fh = open(path, "xb")
    try:
        with fh:
            fh.write(data)
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def capture(root: str, out_arg: str) -> int:
    root_posix = root.replace("\\", "/")
    if not (root_posix.lower().startswith(BASE.lower()) and len(root_posix) > len(BASE)):
        raise UsageError(f"ROOT must be a folder under {BASE}: {root_posix}")
    out = Path(out_arg)
    err_path = out.with_name(out.name + ".stderr.txt")
    refused_path = out.with_name(out.name + ".refused")
    held = [p for p in (out, err_path, refused_path) if p.exists()]
    if held:
        print(f"error: will not overwrite {asc(held[0].as_posix())}")
        return 2
    argv, cwd = command(root)
    env = {k: v for k, v in os.environ.items() if k.upper() != "ELECTRON_RUN_AS_NODE"}
    reasons: list[tuple[str, str]] = []
    pipe = subprocess.PIPE
    proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=pipe, stderr=pipe)
    try:
        stdout, stderr = proc.communicate(timeout=DESCRIBE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        stop(proc)
        try:
            stdout, stderr = proc.communicate(timeout=DRAIN_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = b"", b""
        detail = f"no exit within {DESCRIBE_TIMEOUT_S} s; pid {proc.pid} stopped"
        reasons.append(("timeout", detail))
    write_new(err_path, stderr or b"")
    stdout = stdout or b""
    code = proc.wait()
    if code != 0:
        reasons.append(("harness-exit", f"the harness exited {code}"))
    reasons.extend(refusals(stdout))
    if reasons:
        write_new(refused_path, stdout)
        report(reasons)
        print(f"kept: {asc(refused_path.as_posix())} ({len(stdout)} bytes); no OUT written")
        return 1
    write_new(out, stdout)
    print(f"captured: {len(stdout)} bytes sha256 {hashlib.sha256(stdout).hexdigest()}")
    print(f"stderr: {asc(err_path.as_posix())}")
    return 0


def check(file_arg: str) -> int:
    path = Path(file_arg)
    if not path.is_file():
        raise UsageError(f"no such file: {path.as_posix()}")
    data = path.read_bytes()
    reasons = refusals(data)
    if reasons:
        report(reasons)
        return 1
    print(f"ok: {len(data)} bytes sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else list(argv)
    if GUARD is None:
        print(f"error: guard not loaded: {ascii(GUARD_ERROR or GUARD_PATH.as_posix())}")
        return 2
    try:
        if len(args) == 3 and args[0] == "capture":
            return capture(args[1], args[2])
        if len(args) == 2 and args[0] == "check":
            return check(args[1])
        raise UsageError(USAGE)
    except UsageError as exc:
        print(f"usage error: {asc(str(exc))}")
        return 2
    except (OSError, ValueError) as exc:
        print(f"error: {type(exc).__name__}: {asc(str(exc))}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
