"""Session 102 debt edits (task rows 1 and 2; implementation-plan.md §Single-statement contracts).

``--stage red`` (row 1) applies ``ICC_HEADER_MASK``'s Red half to
``tests/unit/test_capture_adapter.py``:
the helper's Red form just before AC-130.10's first decorator line, so both decorators stay on
AC-130.10; the two ``test_ac_164_8_`` tests right after AC-130.10's last line; and AC-130.10's one
comparison line. ``--stage green`` (row 2) replaces the helper's Red form with its Green form, and
replaces ``plan_slug`` in ``tools/validate_closeout_artifacts.py`` with ``PLAN_SLUG_PARENT_ONLY``.

Every edit is by bytes on a CRLF file, and every old text must occur exactly once, or nothing is
written. ``row-check.py`` imports these forms (``named-edits``, ``slug-edit``), so the edit and the
check read the same text. The forms are written with LF here and with CRLF in the files.
"""

from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ADAPTER = "tests/unit/test_capture_adapter.py"
VALIDATOR = "tools/validate_closeout_artifacts.py"

HELPER = "_same_icc_ignoring_creation"
AC_130_10 = "test_ac_130_10_cmyk_icc_to_srgb"
AC_164_8 = (
    "test_ac_164_8_icc_compare_ignores_creation_time",
    "test_ac_164_8_icc_compare_sees_other_bytes",
)
PLAN_SLUG_FN = "plan_slug"

#: AC-130.10's first decorator, its second and its def line: the first line alone occurs 3 times.
AC_130_10_HEAD = (
    '@pytest.mark.parametrize("ac_id", ["AC-130.10"], ids=["AC-130.10"])\n'
    "@pytest.mark.unit\n"
    "def test_ac_130_10_cmyk_icc_to_srgb("
)
#: AC-130.10's last line, after which the two AC-164.8 tests go.
AC_130_10_LAST = "        assert cropped.tobytes() == managed.tobytes()\n"
AC_130_10_LINE_OLD = '        assert cropped.info.get("icc_profile") == srgb.tobytes()\n'
AC_130_10_LINE_NEW = (
    '        assert _same_icc_ignoring_creation(cropped.info.get("icc_profile"), srgb.tobytes())\n'
)

_HELPER_HEAD = '''def _same_icc_ignoring_creation(a: bytes | None, b: bytes | None) -> bool:
    """Compare two ICC profiles byte for byte.

    The ICC header's creation date and time, bytes 24 to 35 (ICC.1 §7.2.1), are ignored.
    """
    if a is None or b is None or len(a) != len(b) or len(a) < 128:
        return False
'''
HELPER_RED = _HELPER_HEAD + "    return a == b"
HELPER_GREEN = _HELPER_HEAD + "    return a[:24] + a[36:] == b[:24] + b[36:]"

TEST_IGNORES = '''@pytest.mark.unit
def test_ac_164_8_icc_compare_ignores_creation_time() -> None:
    """D-1367: two profiles that differ only in the creation date and time are the same."""
    from PIL import ImageCms

    base = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    assert _same_icc_ignoring_creation(base, base)
    for index in range(24, 36):
        changed = bytearray(base)
        changed[index] ^= 0xFF
        assert _same_icc_ignoring_creation(base, bytes(changed)), index
    every = bytearray(base)
    for index in range(24, 36):
        every[index] ^= 0xFF
    assert _same_icc_ignoring_creation(base, bytes(every))'''
TEST_SEES = '''@pytest.mark.unit
def test_ac_164_8_icc_compare_sees_other_bytes() -> None:
    """D-1367: any other byte, a length or a missing or short profile still tells them apart."""
    from PIL import ImageCms

    base = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    for index in (23, 36, 100):
        changed = bytearray(base)
        changed[index] ^= 0xFF
        assert not _same_icc_ignoring_creation(base, bytes(changed)), index
    assert not _same_icc_ignoring_creation(base, base[:-1])
    assert not _same_icc_ignoring_creation(None, base)
    assert not _same_icc_ignoring_creation(base, None)
    short = bytes(100)
    assert not _same_icc_ignoring_creation(short, short)'''
TESTS = {AC_164_8[0]: TEST_IGNORES, AC_164_8[1]: TEST_SEES}

PLAN_SLUG_OLD = '''def plan_slug(plan_path: str) -> str:
    """The ``{date}-{project-slug}`` directory that identifies one plan.

    The slug, not the filename. Every plan is called ``implementation-plan.md``, so
    a handoff that merely mentions that filename is bound to no particular plan --
    which is the defect this whole check exists for.
    """
    parts = Path(plan_path).as_posix().split("/")
    for part in reversed(parts[:-1] if parts[-1].endswith(".md") else parts):
        match = PLAN_SLUG.fullmatch(part)
        if match:
            return match.group(1)
    raise Usage(
        f"cannot derive a plan slug from {plan_path!r}. Expected a path under "
        f"docs/execution/plans/{{YYYY-MM-DD}}-{{project-slug}}/."
    )'''
PLAN_SLUG_NEW = '''def plan_slug(plan_path: str) -> str:
    """The ``{date}-{project-slug}`` directory that identifies one plan.

    The slug, not the filename. Every plan is called ``implementation-plan.md``, so
    a handoff that merely mentions that filename is bound to no particular plan --
    which is the defect this whole check exists for.
    Only the plan's own folder counts, so a dated ancestor (a dated TEMP, say) names no plan.
    """
    parts = Path(plan_path).as_posix().split("/")
    folder = parts[-2] if parts[-1].endswith(".md") and len(parts) > 1 else parts[-1]
    match = PLAN_SLUG.fullmatch(folder)
    if match:
        return match.group(1)
    raise Usage(
        f"cannot derive a plan slug from {plan_path!r}. Expected a path under "
        f"docs/execution/plans/{{YYYY-MM-DD}}-{{project-slug}}/."
    )'''


def crlf(text: str) -> bytes:
    return text.replace("\n", "\r\n").encode("utf-8")


def red_edits() -> list[tuple[bytes, bytes]]:
    """(old, new) byte pairs for ``test_capture_adapter.py`` at Red."""
    tests = "\n\n\n".join(TESTS.values())
    return [
        (crlf(AC_130_10_HEAD), crlf(HELPER_RED + "\n\n\n" + AC_130_10_HEAD)),
        (crlf(AC_130_10_LINE_OLD), crlf(AC_130_10_LINE_NEW)),
        (crlf(AC_130_10_LAST), crlf(AC_130_10_LAST + "\n\n" + tests + "\n")),
    ]


def green_edits() -> dict[str, list[tuple[bytes, bytes]]]:
    return {
        ADAPTER: [(crlf(HELPER_RED + "\n"), crlf(HELPER_GREEN + "\n"))],
        VALIDATOR: [(crlf(PLAN_SLUG_OLD + "\n"), crlf(PLAN_SLUG_NEW + "\n"))],
    }


def apply(raw: bytes, edits: list[tuple[bytes, bytes]], label: str) -> tuple[bytes, list[str]]:
    """Every old text is found exactly once in ``raw`` before any is replaced."""
    problems: list[str] = []
    bare = raw.count(b"\n") - raw.count(b"\r\n")
    if bare:
        problems.append(f"{label}: {bare} bare LF; the file must be CRLF")
    for old, _ in edits:
        n = raw.count(old)
        if n != 1:
            problems.append(f"{label}: old text found {n} time(s): {old[:70]!r}")
    if problems:
        return raw, problems
    for old, new in edits:
        raw = raw.replace(old, new)
    return raw, []


def run(stage: str, root: pathlib.Path) -> list[str]:
    plan = {ADAPTER: red_edits()} if stage == "red" else green_edits()
    out: dict[str, bytes] = {}
    problems: list[str] = []
    for name, edits in plan.items():
        new, found = apply((root / name).read_bytes(), edits, name)
        problems += found
        out[name] = new
    if problems:
        return problems
    for name, data in out.items():
        (root / name).write_bytes(data)
        bare = data.count(b"\n") - data.count(b"\r\n")
        print(f"debt-edit {stage}: {name}: {len(plan[name])} edit(s); bare LF {bare}")
    return []


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] != "--stage" or argv[1] not in ("red", "green"):
        print("usage: debt-edit.py --stage red|green")
        return 2
    problems = run(argv[1], ROOT)
    for p in problems:
        print("PROBLEM:", p)
    print(
        f"debt-edit {argv[1]}: {len(problems)} problem(s); nothing written"
        if problems
        else f"debt-edit {argv[1]}: written"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
