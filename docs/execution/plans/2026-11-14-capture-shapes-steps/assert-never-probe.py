"""Session 72 ASSERT_NEVER_PROBE (AC-106.34, AC-107.5; implementation-plan.md §Verification Plan).

Adapted from Session 68's probe (``docs/execution/plans/2026-11-13-capture-redact/assert-never-probe.py``).

09 §Step mark's crop row says ``clip_mark``'s ``assert_never`` fails the type check until the
step case exists (D-675). STEP_API makes ``_annotations_from_in`` end with ``assert_never(item)``
so that a missing ``*In`` type fails the same way (D-772). This proves both on copies, never on
the repository files. For each target:

1. copy the file to ``C:/Temp/av-kit/s72/never-probe/<target>/``;
2. run pyright from the repository root on the unchanged copy, which must report ``0 errors``;
3. remove the one step branch line (``case StepAnnotation():`` in the domain,
   ``if isinstance(item, StepAnnotationIn):`` in the route) and the more-indented body under it;
4. run pyright on that copy, which must exit 1 with exactly one error, at the ``assert_never``
   call, naming the removed class in quotes and ``"Never"``. Each error line is printed as
   pyright wrote it (Session 64 RULE-2).

Before row 2 there is no step branch to remove, so the probe stops with ``no step branch`` and
exits 1. ``--selftest`` runs the same steps on toy modules in both styles (a ``match`` and an
``isinstance`` chain): with the branch (pass), without it (refused) and with a fallback that is
not ``assert_never`` (refused). It then runs the domain steps on the real
``domain/capture.py`` with today's ``case RedactAnnotation():``, which must pass, so the removal
logic is proved on the real file at plan time. The last line is ``assert-never-probe: pass`` or
``assert-never-probe: fail``.
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

SCRATCH = pathlib.Path("C:/Temp/av-kit/s72/never-probe")
ERROR = re.compile(r" - error: ")
DOMAIN = pathlib.Path("packages/core/src/avkit_core/domain/capture.py")
ROUTE = pathlib.Path("packages/api/src/avkit_api/routes/captures.py")


def case_line(name: str) -> re.Pattern[str]:
    return re.compile(r"^(\s+)case " + re.escape(name) + r"\(\):\s*$")


def isinstance_line(name: str) -> re.Pattern[str]:
    return re.compile(r"^(\s+)if isinstance\(item, " + re.escape(name) + r"\):\s*$")


TARGETS = (
    ("domain", DOMAIN, case_line("StepAnnotation"), "StepAnnotation"),
    ("route", ROUTE, isinstance_line("StepAnnotationIn"), "StepAnnotationIn"),
)


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


def remove_branch(text: str, line: re.Pattern[str]) -> str | None:
    lines = text.splitlines(keepends=True)
    hits = [n for n, ln in enumerate(lines) if line.match(ln.rstrip("\r\n"))]
    if len(hits) != 1:
        return None
    start = hits[0]
    indent = len(line.match(lines[start].rstrip("\r\n")).group(1))  # type: ignore[union-attr]
    end = start + 1
    while end < len(lines):
        body = lines[end].rstrip("\r\n")
        if body.strip() and len(body) - len(body.lstrip()) <= indent:
            break
        end += 1
    return "".join(lines[:start] + lines[end:])


def probe(source: pathlib.Path, folder: pathlib.Path, line: re.Pattern[str], name: str) -> bool:
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
    cut = remove_branch(source.read_text(encoding="utf-8"), line)
    if cut is None:
        print(f"no step branch: exactly one line matching {line.pattern!r} is needed")
        return False
    mutated = folder / f"{source.stem}_no_{name}.py"
    mutated.write_bytes(cut.encode("utf-8"))
    code, errors, summary = pyright(mutated)
    print(f"mutated copy {mutated}: exit={code} {summary!r}")
    for e in errors:
        print("pyright:", e.strip())
    named = [e for e in errors if f'"{name}"' in e and '"Never"' in e and "assert_never" in e]
    ok = code == 1 and len(errors) == 1 and len(named) == 1
    print(f"one error naming {name} and Never at assert_never: {ok}")
    return ok


MATCH_HEAD = (
    "from dataclasses import dataclass\n"
    "from typing import assert_never\n\n\n"
    "@dataclass(frozen=True)\nclass A:\n    x: int\n\n\n"
    "@dataclass(frozen=True)\nclass StepAnnotation:\n    x: int\n\n\n"
    "Mark = A | StepAnnotation\n\n\n"
    "def f(mark: Mark) -> int:\n    match mark:\n        case A():\n            return 1\n"
)
CHAIN_HEAD = (
    "from dataclasses import dataclass\n"
    "from typing import assert_never\n\n\n"
    "@dataclass(frozen=True)\nclass AIn:\n    x: int\n\n\n"
    "@dataclass(frozen=True)\nclass StepAnnotationIn:\n    x: int\n\n\n"
    "def f(items: list[AIn | StepAnnotationIn]) -> list[int]:\n    out: list[int] = []\n"
    "    for item in items:\n        if isinstance(item, AIn):\n            out.append(1)\n            continue\n"
)
TOYS = (
    ("match_with", MATCH_HEAD + "        case StepAnnotation():\n            return 2\n        case _:\n            assert_never(mark)\n", "domain", True),
    ("match_without", MATCH_HEAD + "        case _:\n            return 0\n", "domain", False),
    ("match_no_never", MATCH_HEAD + "        case StepAnnotation():\n            return 2\n        case _:\n            return 0\n", "domain", False),
    ("chain_with", CHAIN_HEAD + "        if isinstance(item, StepAnnotationIn):\n            out.append(2)\n            continue\n        assert_never(item)\n    return out\n", "route", True),
    ("chain_without", CHAIN_HEAD + "    return out\n", "route", False),
    ("chain_no_never", CHAIN_HEAD + "        if isinstance(item, StepAnnotationIn):\n            out.append(2)\n            continue\n    return out\n", "route", False),
)


def selftest() -> int:
    wrong = []
    folder = SCRATCH / "selftest"
    styles = {t[0]: (t[2], t[3]) for t in TARGETS}
    for toy_name, text, style, want in TOYS:
        toy = folder / f"toy_{toy_name}.py"
        toy.parent.mkdir(parents=True, exist_ok=True)
        toy.write_bytes(text.encode("utf-8"))
        line, name = styles[style]
        got = probe(toy, folder / toy_name, line, name)
        print(f"selftest {toy_name}: {'pass' if got else 'refused'} (expected {'pass' if want else 'refused'})")
        if got != want:
            wrong.append(toy_name)
    real = probe(DOMAIN, folder / "real_domain_redact", case_line("RedactAnnotation"), "RedactAnnotation")
    print(f"selftest real domain/capture.py without its redact case: {'pass' if real else 'refused'} (expected pass)")
    if not real:
        wrong.append("real_domain_redact")
    print(f"assert-never-probe selftest: {len(TOYS) + 1} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if argv:
        print("usage: assert-never-probe.py [--selftest]  (run from the repository root)")
        return 2
    results = []
    for label, source, line, name in TARGETS:
        print(f"== {label}: {source}")
        results.append(probe(source, SCRATCH / label, line, name))
    ok = all(results)
    print(f"assert-never-probe: {'pass' if ok else 'fail'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
