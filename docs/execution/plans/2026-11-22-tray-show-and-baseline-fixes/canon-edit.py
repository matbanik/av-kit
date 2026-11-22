"""Session 102 canon edit (task row 7; MEU-164, AC-164.7).

It edits by bytes and refuses, writing nothing, unless each target text is found exactly once:

- 09 §Electron OS surface: the tray row becomes ``TRAY_ROW_NEW`` (CRLF kept).
- 09 §Tray double-click: a Delivered note follows the Menu row (CRLF kept).
- Grouping §6 row 102 goes from ``planned`` to ``executed (Session 102)`` (LF kept).

The texts come from ``row-check.py``, which ``row-check.py canon`` and ``register`` check.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CR, LF, CRLF = b"\r", b"\n", b"\r\n"


def _row_check():
    spec = importlib.util.spec_from_file_location("tsb_row_check", HERE / "row-check.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["tsb_row_check"] = module
    spec.loader.exec_module(module)
    return module


rc = _row_check()

DELIVERED_BULLETS = (
    "> - `TRAY_SHOW_SHARED`: `startCaptureTray` in `ui/src/main/capture-tray.ts` defines one "
    "`showWindow` function, which does a `restore` when the window is minimized and then shows "
    "and focuses it. The Show window item's `click` and the tray's `double-click` listener are "
    "that same function (D-1365).",
    "> - `TRAY_E2E_HOOK`: only a launch with `AVKIT_E2E=1` sets "
    "`globalThis.__AVKIT_E2E_TRAY__` to `{ tray, menu }`, so Playwright can emit the tray's "
    "`double-click` and call the Show window item (D-1366).",
    "> - Tests: `ui/tests/unit/capture-tray.test.ts` (AC-164.1 to AC-164.3) and the Electron "
    "test `ui/tests/e2e/tray-double-click.test.ts` (AC-164.4 hidden, AC-164.5 minimized).",
    "> - The same session fixed two test baselines: AC-130.10 compares ICC profiles without "
    "their creation time (D-1367), and the closeout validator names a plan by its own folder "
    "only (D-1368). D-1365 to D-1368 are in the plan "
    "`docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/`.",
)


def canon_edit(raw: bytes) -> tuple[bytes, list[str]]:
    problems: list[str] = []
    if raw.count(LF) != raw.count(CRLF):
        return raw, ["09 has a bare LF; expected CRLF only"]
    lines = raw.split(CRLF)
    tray = [i for i, line in enumerate(lines) if line == rc.TRAY_ROW_OLD.encode()]
    menu = [i for i, line in enumerate(lines) if line.startswith(rc.MENU_PREFIX.encode())]
    if len(tray) != 1:
        problems.append(f"09: the old tray row is found {len(tray)} time(s)")
    if len(menu) != 1:
        problems.append(f"09: the Menu row is found {len(menu)} time(s)")
    if raw.count(rc.DELIVERED_HEAD.encode()):
        problems.append("09: a Delivered (Session 102) note already exists")
    if problems:
        return raw, problems
    lines[tray[0]] = rc.TRAY_ROW_NEW.encode()
    note = [b"", rc.DELIVERED_HEAD.encode(), *(b.encode() for b in DELIVERED_BULLETS)]
    lines[menu[0] + 1 : menu[0] + 1] = note
    return CRLF.join(lines), []


def grouping_edit(raw: bytes) -> tuple[bytes, list[str]]:
    if CR in raw:
        return raw, ["grouping has a CR; expected LF"]
    lines = raw.split(LF)
    rows = [i for i, line in enumerate(lines) if line.startswith(b"| 102 |")]
    if len(rows) != 1:
        return raw, [f"grouping: row 102 is found {len(rows)} time(s)"]
    row = lines[rows[0]]
    old, new = rc.GROUPING_OLD.encode(), rc.GROUPING_NEW.encode()
    if row.count(old) != 1:
        return raw, [f"grouping: row 102 does not read planned once: {row[:90]!r}"]
    lines[rows[0]] = row.replace(old, new, 1)
    return LF.join(lines), []


def main() -> int:
    canon_path, grouping_path = ROOT / rc.CANON, ROOT / rc.GROUPING
    canon_new, p1 = canon_edit(canon_path.read_bytes())
    grouping_new, p2 = grouping_edit(grouping_path.read_bytes())
    problems = p1 + p2
    for problem in problems:
        print("PROBLEM:", problem)
    if problems:
        return 1
    canon_path.write_bytes(canon_new)
    grouping_path.write_bytes(grouping_new)
    print(f"{rc.CANON}: tray row set; Delivered note added ({len(DELIVERED_BULLETS)} bullets)")
    print(f"{rc.GROUPING}: row 102 is {rc.GROUPING_NEW}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
