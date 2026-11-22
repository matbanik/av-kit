# ruff: noqa: E501 -- one-shot edit script; its long lines are byte-exact edit literals.
"""Plan review round 1 corrections (F1 decorator boundary, F2 Red helper validation, F3 Playwright message).

Edits implementation-plan.md and task.md by bytes; refuses unless each old text occurs exactly once; keeps LF.
"""

import sys
from pathlib import Path

CR, LF, CRLF = b"\r", b"\n", b"\r\n"

HERE = Path(__file__).resolve().parent
PLAN = HERE / "implementation-plan.md"
TASK = HERE / "task.md"

PLAN_EDITS = [
    (
        "gains, just before `test_ac_130_10_cmyk_icc_to_srgb`, the module helper",
        "gains, just before AC-130.10's first decorator (the line "
        '`@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])`, so both of AC-130.10\'s '
        "decorators stay on it), the module helper",
    ),
    (
        "Its Green body returns False when either is None, when the lengths differ or when either is shorter than "
        "the 128-byte header, and otherwise returns `a[:24] + a[36:] == b[:24] + b[36:]`. Its Red body (row 1) is "
        "`return a is not None and a == b`, which is today's comparison.",
        "Both forms first return False when either is None, when the lengths differ or when either is shorter than "
        "the 128-byte header. Then the Green form returns `a[:24] + a[36:] == b[:24] + b[36:]`, and the Red form "
        "(row 1) returns `a == b`, which is today's comparison. So the guard passes at Red and at Green.",
    ),
    (
        "with the message `tray hook`, so a missing hook is an assertion",
        "with the message `expect(tray hook)` (Playwright prints it as `Error: expect(tray hook)`, which "
        "`red-check.py` reads as an assertion line), so a missing hook is an assertion",
    ),
    (
        "until the hook exists, asserted with the message `tray hook`;",
        "until the hook exists, asserted with the message `expect(tray hook)`;",
    ),
    (
        "- **`ICC_HEADER_MASK`.**",
        "- **`ICC_HEADER_MASK`.**",
    ),
]

TASK_EDITS = [
    (
        "`red` inserts the helper's Red form just before `def test_ac_130_10_cmyk_icc_to_srgb`, the two tests right "
        "after that test,",
        "`red` inserts the helper's Red form just before AC-130.10's first decorator line "
        '(`@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])`), so both decorators stay on '
        "AC-130.10, the two tests right after AC-130.10's last line,",
    ),
    (
        "AC-130.10 differs in its one line only;",
        "AC-130.10's source from its first decorator to its last line differs in its one line only, so its "
        "decorators are kept;",
    ),
    (
        "{ message: 'tray hook', timeout: 10_000 }",
        "{ message: 'expect(tray hook)', timeout: 10_000 }",
    ),
]


def apply(path: Path, edits: list[tuple[str, str]]) -> None:
    raw = path.read_bytes()
    if b"\r" in raw:
        sys.exit(f"{path.name}: not LF")
    text = raw.decode("utf-8")
    for old, new in edits:
        if old == new:
            continue
        n = text.count(old)
        if n != 1:
            sys.exit(f"{path.name}: anchor found {n} times: {old[:60]!r}")
        text = text.replace(old, new)
    path.write_bytes(text.encode("utf-8"))
    print(
        f"{path.name}: {len([e for e in edits if e[0] != e[1]])} edits; LF only: {CR not in text.encode()}"
    )


apply(PLAN, PLAN_EDITS)
apply(TASK, TASK_EDITS)
