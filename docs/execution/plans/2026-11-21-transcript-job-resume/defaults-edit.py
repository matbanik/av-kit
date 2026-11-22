"""Row 4a: TRANSCRIPT_DEFAULTS (Mat 2026-11-21, D-1355).

Replaces the one number on each of the six transcript lines of the core settings table and of
the MCP settings schema, by bytes. Both files are CRLF and stay CRLF. It refuses, and writes
nothing, when an old line is not found exactly once or a file holds a bare LF.
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
SETTINGS_PY = ROOT / "packages/core/src/avkit_core/services/settings.py"
SETTINGS_TS = ROOT / "mcp-server/src/toolsets/settings.ts"

#: (key, old, new)
DEFAULTS = (
    ("requests_per_hour", 300, 20),
    ("delay_between_requests", 6, 120),
    ("max_retries", 3, 1),
    ("retry_delay", 30, 7),
    ("batch_size", 50, 5),
    ("pause_between_batches", 300, 500),
)


def py_line(key: str, value: int) -> str:
    return f'    ("transcript", "{key}"): SettingSpec("number", {value}, min_number=0),'


def ts_line(key: str, value: int) -> str:
    return f'      {key}: {{ type: "number", default: {value} }},'


def edited(path: pathlib.Path, line_for) -> bytes:
    raw = path.read_bytes()
    if raw.count(b"\n") != raw.count(b"\r\n"):
        sys.exit(f"defaults-edit: {path.name} holds a bare LF")
    lines = raw.split(b"\r\n")
    for key, old, new in DEFAULTS:
        old_b = line_for(key, old).encode("utf-8")
        hits = [i for i, line in enumerate(lines) if line == old_b]
        if len(hits) != 1:
            sys.exit(f"defaults-edit: {path.name}: {key} old line found {len(hits)} time(s)")
        lines[hits[0]] = line_for(key, new).encode("utf-8")
    return b"\r\n".join(lines)


def main() -> None:
    out = {SETTINGS_PY: edited(SETTINGS_PY, py_line), SETTINGS_TS: edited(SETTINGS_TS, ts_line)}
    for path, data in out.items():
        path.write_bytes(data)
        print(f"defaults-edit: {path.relative_to(ROOT).as_posix()}: {len(DEFAULTS)} line(s)")


if __name__ == "__main__":
    main()
