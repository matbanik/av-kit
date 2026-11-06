"""Session 50 real-log guard (implementation-plan.md Verification Plan §3; stop condition S4).

Usage:
  ``python real-log-check.py --record OUT.json``  writes the state of the real console.log.
  ``python real-log-check.py --compare BEFORE.json``  exits 1 if that state changed.
  ``python real-log-check.py --selftest``  proves both directions on a scratch file.

The real file is ``%LOCALAPPDATA%\\av-kit\\logs\\console.log``, the one the installed and dev
apps write when ``AVKIT_APP_DATA`` is unset (``avkit_infra/database/engine.py``). Its state is
its size, modification time (ns) and SHA-256, or ``absent``. No test or gate step may touch it:
every ``HealthService`` in the suite uses ``tmp_path``, and the E2E app gets its own app data.
The script only reads the file.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import sys
import tempfile


def real_log() -> pathlib.Path:
    local = os.environ.get("LOCALAPPDATA", "").strip()
    if not local:
        raise SystemExit("real-log-check: LOCALAPPDATA is not set")
    return pathlib.Path(local) / "av-kit" / "logs" / "console.log"


def state(path: pathlib.Path) -> dict[str, object]:
    if not path.exists():
        return {"path": str(path), "absent": True}
    stat = path.stat()
    return {
        "path": str(path),
        "absent": False,
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def compare(before: dict[str, object], now: dict[str, object]) -> list[str]:
    return [f"{key}: {before.get(key)!r} -> {now.get(key)!r}" for key in sorted(set(before) | set(now)) if before.get(key) != now.get(key)]


def selftest() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "console.log"
        absent = state(path)
        if compare(absent, state(path)):
            failures.append("absent file compared unequal to itself")
        path.write_bytes(b'{"seq": 1}\n')
        first = state(path)
        if not compare(absent, first):
            failures.append("a created file compared equal to absent")
        if compare(first, state(path)):
            failures.append("an unchanged file compared unequal")
        with path.open("ab") as handle:
            handle.write(b'{"seq": 2}\n')
        if not compare(first, state(path)):
            failures.append("an appended file compared equal")
    for failure in failures:
        print(f"FAIL {failure}")
    print(f"real-log-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) == 2 and argv[0] == "--record":
        now = state(real_log())
        pathlib.Path(argv[1]).write_text(json.dumps(now, indent=2) + "\n", encoding="utf-8")
        print(f"real-log-check: recorded {json.dumps(now)}")
        return 0
    if len(argv) == 2 and argv[0] == "--compare":
        before = json.loads(pathlib.Path(argv[1]).read_text(encoding="utf-8"))
        now = state(real_log())
        changes = compare(before, now)
        for change in changes:
            print(f"CHANGED {change}")
        print("real-log-check: real console.log " + ("CHANGED (S4)" if changes else "unchanged"))
        return 1 if changes else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
