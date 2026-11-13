"""Session 68 ASSERT_NEVER_PROBE (AC-103.7; implementation-plan.md §Verification Plan).

The crop row of 09 §Redact mark says ``clip_mark``'s ``assert_never`` fails the type check until
the redact case exists. This proves it on a copy, never on the repository file:

1. copy ``packages/core/src/avkit_core/domain/capture.py`` to ``C:/Temp/av-kit/s68/never-probe/``;
2. run pyright from the repository root on the unchanged copy, which must report ``0 errors``;
3. remove the one ``case RedactAnnotation():`` line and the more-indented body lines under it;
4. run pyright on that copy, which must exit 1 with exactly one error, at the ``assert_never``
   call, naming ``"RedactAnnotation"`` and ``"Never"``. The line is printed as pyright wrote it
   (Session 64 RULE-2).

Before Green there is no redact case to remove, so the probe stops with ``no redact case`` and
exits 1. ``--selftest`` runs the same steps on toy modules in the scratch folder: one with the
case (pass), one without it (refused) and one whose fallback is not ``assert_never`` (refused).
The last line is ``assert-never-probe: pass`` or ``assert-never-probe: fail``.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

SOURCE = pathlib.Path("packages/core/src/avkit_core/domain/capture.py")
SCRATCH = pathlib.Path("C:/Temp/av-kit/s68/never-probe")
CASE = re.compile(r"^(\s+)case RedactAnnotation\(\):\s*$")
ERROR = re.compile(r" - error: ")


def pyright(path: pathlib.Path) -> tuple[int, list[str], str]:
    run = subprocess.run(
        ["uv", "run", "--no-sync", "pyright", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    lines = run.stdout.splitlines()
    summary = next((ln for ln in reversed(lines) if re.search(r"\d+ errors?, \d+ warnings?", ln)), "")
    return run.returncode, [ln for ln in lines if ERROR.search(ln)], summary


def remove_case(text: str) -> str | None:
    lines = text.splitlines(keepends=True)
    hits = [n for n, ln in enumerate(lines) if CASE.match(ln.rstrip("\r\n"))]
    if len(hits) != 1:
        return None
    start = hits[0]
    indent = len(CASE.match(lines[start].rstrip("\r\n")).group(1))  # type: ignore[union-attr]
    end = start + 1
    while end < len(lines):
        body = lines[end].rstrip("\r\n")
        if body.strip() and len(body) - len(body.lstrip()) <= indent:
            break
        end += 1
    return "".join(lines[:start] + lines[end:])


def probe(source: pathlib.Path, folder: pathlib.Path) -> bool:
    folder.mkdir(parents=True, exist_ok=True)
    whole = folder / f"{source.stem}_whole.py"
    shutil.copyfile(source, whole)
    code, errors, summary = pyright(whole)
    print(f"unchanged copy {whole}: exit={code} {summary!r}")
    if code != 0 or errors:
        for e in errors:
            print("  ", e)
        print("the unchanged copy does not type-check, so the probe proves nothing")
        return False
    cut = remove_case(source.read_text(encoding="utf-8"))
    if cut is None:
        print("no redact case: exactly one `case RedactAnnotation():` line is needed")
        return False
    mutated = folder / f"{source.stem}_no_redact_case.py"
    mutated.write_bytes(cut.encode("utf-8"))
    code, errors, summary = pyright(mutated)
    print(f"mutated copy {mutated}: exit={code} {summary!r}")
    for e in errors:
        print("pyright:", e.strip())
    named = [e for e in errors if '"RedactAnnotation"' in e and '"Never"' in e and "assert_never" in e]
    ok = code == 1 and len(errors) == 1 and len(named) == 1
    print(f"one error naming RedactAnnotation and Never at assert_never: {ok}")
    return ok


TOY_HEAD = (
    "from dataclasses import dataclass\n"
    "from typing import assert_never\n\n\n"
    "@dataclass(frozen=True)\nclass A:\n    x: int\n\n\n"
    "@dataclass(frozen=True)\nclass RedactAnnotation:\n    x: int\n\n\n"
    "Mark = A | RedactAnnotation\n\n\n"
    "def f(mark: Mark) -> int:\n    match mark:\n        case A():\n            return 1\n"
)
TOYS = (
    ("with_case", TOY_HEAD + "        case RedactAnnotation():\n            return 2\n        case _:\n            assert_never(mark)\n", True),
    ("without_case", TOY_HEAD + "        case _:\n            return 0\n", False),
    ("no_assert_never", TOY_HEAD + "        case RedactAnnotation():\n            return 2\n        case _:\n            return 0\n", False),
)


def selftest() -> int:
    wrong = []
    folder = SCRATCH / "selftest"
    for name, text, want in TOYS:
        toy = folder / f"toy_{name}.py"
        toy.parent.mkdir(parents=True, exist_ok=True)
        toy.write_bytes(text.encode("utf-8"))
        got = probe(toy, folder / name)
        print(f"selftest {name}: {'pass' if got else 'refused'} (expected {'pass' if want else 'refused'})")
        if got != want:
            wrong.append(name)
    print(f"assert-never-probe selftest: {len(TOYS)} toy(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print("usage: assert-never-probe.py [--selftest]  (run from the repository root)")
        return 2
    ok = probe(SOURCE, SCRATCH)
    print(f"assert-never-probe: {'pass' if ok else 'fail'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
