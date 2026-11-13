"""Session 69 pytest id-length check (task row 2; Session 59 RULE-2, Session 67 RULE-4).

red-check.py splits a pytest receipt on ``PYTEST_HEADER = ^_{3,} (.+?) _{3,}\\s*$``. pytest pads
a failure header to the terminal width, so a long title leaves fewer than three underscores a
side and its block is never found. Measured on this host through ``rtk proxy`` on 2026-11-13
(Session 68's measurement, ``C:/Temp/av-kit/s68/idw/out.txt``): a 71-character title keeps ``___``, a 72-character one
gets ``__``. So every title must be at most ``LIMIT`` = 71 characters.

The title is the node id after the module's ``::``, with any further ``::`` written as ``.``
(``TestX.test_y[case]``), which is what pytest prints in the header.

Usage: ``python id-length.py MODULE [MODULE ...]`` collects each module with
``pytest --collect-only -q`` and exits 1 when a title is too long, when a module collects no
test, or when collection fails. ``python id-length.py --selftest`` checks the title rule on
fixed ids. The last line is ``id-length: N test(s), M too long``.
"""

from __future__ import annotations

import subprocess
import sys

LIMIT = 71


def title(nodeid: str) -> str:
    _, _, rest = nodeid.partition("::")
    return rest.replace("::", ".")


def too_long(nodeids: list[str]) -> list[str]:
    return [t for t in (title(n) for n in nodeids) if len(t) > LIMIT]


def collect(module: str) -> tuple[int, list[str]]:
    run = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", module],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    ids = [line.strip() for line in run.stdout.splitlines() if "::" in line and not line.startswith(" ")]
    return run.returncode, ids


def selftest() -> int:
    cases = (
        ("tests/unit/test_x.py::test_" + "a" * 66, False),  # 71 characters: fits
        ("tests/unit/test_x.py::test_" + "a" * 67, True),  # 72 characters: too long
        ("tests/unit/test_x.py::TestX::test_y[" + "b" * 57 + "]", False),  # 71 with the class
        ("tests/unit/test_x.py::TestX::test_y[" + "b" * 58 + "]", True),  # 72 with the class
    )
    wrong = [nodeid for nodeid, want in cases if bool(too_long([nodeid])) != want]
    for nodeid, want in cases:
        print(f"selftest {len(title(nodeid))} chars: too_long={bool(too_long([nodeid]))} (expected {want})")
    print(f"id-length selftest: {len(cases)} case(s), {len(wrong)} wrong")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if not argv:
        print("usage: id-length.py MODULE [MODULE ...] | --selftest")
        return 2
    total, bad, broken = 0, [], []
    for module in argv:
        code, ids = collect(module)
        if code != 0 or not ids:
            broken.append(f"{module} (collect exit={code}, {len(ids)} test(s))")
            continue
        total += len(ids)
        for t in too_long(ids):
            bad.append(t)
            print(f"too long ({len(t)} > {LIMIT}): {t}")
    for b in broken:
        print("not collected:", b)
    print(f"id-length: {total} test(s), {len(bad)} too long")
    return 1 if bad or broken else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
