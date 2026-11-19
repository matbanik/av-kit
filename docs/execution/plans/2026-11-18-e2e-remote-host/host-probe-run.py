"""Run the read-only host probe (Session 96 plan, rows 0, 5 and 6).

Usage: ``host-probe-run.py CONFIG OUT``. It reads ``host``, ``root``, ``task``, ``ffmpeg_bin``
and ``busy_users`` from CONFIG (the untracked local config, or at plan time a scratch copy),
sends one first line that sets the probe's variables and then ``host-probe.ps1`` on stdin to
``ssh -o BatchMode=yes -o StrictHostKeyChecking=yes HOST powershell.exe -NoProfile
-NonInteractive -Command -``, and writes stdout and stderr to OUT (exclusive create) with the
exit code on the last line. It never retries and never bypasses the pinned host key.
Exit: ssh's own code; 2 on usage, a value the probe cannot quote, or an existing OUT.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBE = HERE / "host-probe.ps1"
SAFE = re.compile(r"^[A-Za-z0-9 _:,\\.\-]*$")
HOST = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.\-]*$")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: host-probe-run.py CONFIG OUT")
        return 2
    cfg = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    out = Path(argv[1])
    if out.exists():
        print("refused: exists", ascii(str(out)))
        return 2
    task = str(cfg["task"])
    task_path, _, task_name = task.rpartition("\\")
    values = {
        "root": cfg["root"],
        "busyUsers": ",".join(cfg["busy_users"]),
        "ffbin": cfg["ffmpeg_bin"],
        "taskPath": task_path + "\\",
        "taskName": task_name,
    }
    host = str(cfg["host"])
    if not HOST.match(host) or not all(SAFE.match(str(v)) for v in values.values()):
        print("refused: a config value holds a character the probe cannot quote")
        return 2
    first = "; ".join(f"${k} = '{v}'" for k, v in values.items())
    script = first + "\n" + PROBE.read_text(encoding="ascii")
    argv_ssh = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=yes",
        host,
        "powershell.exe",
        "-NoProfile",
        "-NonInteractive",
        "-Command",
        "-",
    ]
    proc = subprocess.run(argv_ssh, input=script.encode("ascii"), capture_output=True, timeout=180)
    text = proc.stdout.decode("utf-8", "replace")
    err = proc.stderr.decode("utf-8", "replace")
    with out.open("x", encoding="utf-8", newline="\n") as f:
        f.write(text.replace("\r\n", "\n"))
        f.write("--- stderr ---\n" + err.replace("\r\n", "\n"))
        f.write(f"exit={proc.returncode}\n")
    print(f"probe exit={proc.returncode} lines={len(text.splitlines())} out={ascii(str(out))}")
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
