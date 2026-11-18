"""Session 92 (mcp-audit-refresh) rerun of the Session 64 description eval (EVAL_RERUN, D-1158).

Reuses Session 64's prompts (eval-run.md), harness (eval-harness.ts), answer key, media and checker
(eval-check.py check_run) unchanged. Only the `real` surface is run, on the new avkit_capture
description, with three fresh roots beside Session 64's.

    prompts --describe <receipt>   build mar-eval-real-t1..t3-prompt.md from a describe receipt
    check                          run check_run on the three s92 roots and saved reports
    --session64                    reproduce Session 64's real result: t1 and t2 fail, t3 passes
    --selftest                     the prompt builder and the verdict logic on fixtures

Run with `uv run python` (eval-check.py imports PIL). Exit 0 when every check passes, 1 when one
fails, 2 on a usage or input error.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
S64 = REPO / "docs/execution/plans/2026-11-11-capture-export-copy"
EVAL_RUN = S64 / "eval-run.md"
EVAL_CHECK = S64 / "eval-check.py"
BASE = Path("C:/Temp/av-kit/s64/eval")
MEDIA = BASE / "media"
KEY = Path("C:/Temp/av-kit/s64/eval-key/answers.json")
TRANSCRIPT = MEDIA / "meeting-transcript.txt"
SCRATCH = Path("C:/Temp/av-kit/mcp-audit-refresh")
S64_REPORTS = Path("C:/Temp/av-kit")
CUT = "<!-- CUT: the real surface ends above this line -->"
TASKS = ("t1", "t2", "t3")
LEAD = "Call image to view a frame or sheet."
ZOOM = "To zoom, call sheet again with a narrower start and end"
# D-1186 (Session 92): the surface must carry the D-1134 A text as the server sends it.
EXPECTED = Path(__file__).resolve().parent / "capture-description.expected.txt"
# UTF-8 decoded through cp437: a lead byte E2, C2 or C3 (Γ, ┬, ├) then a continuation byte.
_CP437_CONT = bytes(range(0x80, 0xC0)).decode("cp437")
MOJIBAKE = re.compile("[Γ┬├][" + re.escape(_CP437_CONT) + "]")
# Session 64's real result (C:/Temp/av-kit/s64-E4-check.txt): t1 and t2 failed, t3 passed.
S64_REAL = {"t1": False, "t2": False, "t3": True}


def root_of(task: str) -> Path:
    return BASE / f"s92-real-{task}" / "root"


def prompt_path(task: str) -> Path:
    return SCRATCH / f"mar-eval-real-{task}-prompt.md"


def report_path(task: str) -> Path:
    return SCRATCH / f"mar-eval-real-{task}-report.txt"


def blocks(plan_text: str) -> tuple[str, dict[str, str]]:
    """The opening block and the three task blocks of eval-run.md §Prompts."""
    found = re.findall(r"```text\n(.*?)\n```", plan_text.replace("\r\n", "\n"), flags=re.S)
    if len(found) != 4:
        raise ValueError(f"expected 4 text blocks in eval-run.md, found {len(found)}")
    return found[0], dict(zip(TASKS, found[1:], strict=True))


def real_surface(describe: str, expected: str) -> str:
    """The text above the CUT line, with any rtk notice lines dropped; refuses a dirty receipt,
    one that was decoded through the console codepage (D-1186), and one whose surface does not
    hold the expected avkit_capture description verbatim."""
    if "\x1b" in describe:
        raise ValueError("the describe receipt holds an escape sequence")
    moj = MOJIBAKE.search(describe)
    if moj:
        raise ValueError(
            f"the describe receipt holds cp437 mojibake ({moj.group(0)!r}); capture raw bytes"
        )
    lines = [ln for ln in describe.replace("\r\n", "\n").split("\n") if not ln.startswith("[rtk]")]
    if "\r" in "\n".join(lines):
        raise ValueError("the describe receipt holds a bare CR")
    if lines.count(CUT) != 1:
        raise ValueError("the CUT line is not unique in the describe receipt")
    surface = "\n".join(lines[: lines.index(CUT)]).strip("\n")
    if "- avkit_capture." in surface:
        raise ValueError("the real surface holds action notes; the receipt is not split at CUT")
    if LEAD not in surface or ZOOM not in surface:
        raise ValueError("the real surface lacks the new avkit_capture lead facts (old build?)")
    if not expected or expected not in surface:
        raise ValueError("the real surface does not hold capture-description.expected.txt verbatim")
    return surface


def build(plan_text: str, describe: str, transcript: str, expected: str) -> dict[str, str]:
    """Each task's prompt body, with the placeholders filled as Session 64 filled them."""
    opening, task = blocks(plan_text)
    surface = real_surface(describe, expected)
    out: dict[str, str] = {}
    for t in TASKS:
        body = opening + "\n\n" + task[t]
        body = body.replace("{{DESCRIBE}}", surface).replace("{{ROOT}}", root_of(t).as_posix())
        body = body.replace("{{MEDIA}}", MEDIA.as_posix()).replace("{{TRANSCRIPT}}", transcript)
        if "{{" in body or "eval-key" in body:
            raise ValueError(f"real-{t}: a placeholder or the key name is left")
        out[t] = body
    return out


def load_checker():
    spec = importlib.util.spec_from_file_location("s64_eval_check", EVAL_CHECK)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {EVAL_CHECK}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verdicts(check_run, roots: dict[str, Path], reports: dict[str, Path], key: dict) -> dict:
    """{task: (passed, lines)} from check_run on each root and its saved report."""
    out = {}
    for t in TASKS:
        rp = reports[t]
        report = rp.read_text(encoding="utf-8") if rp.is_file() else None
        lines = check_run(t, roots[t], report, key, MEDIA)
        out[t] = (all(ok for ok, _ in lines), lines)
    return out


def show(prefix: str, results: dict) -> None:
    for t, (passed, lines) in results.items():
        for ok, line in lines:
            print(f"{'PASS' if ok else 'FAIL'} {prefix}-{t}: {line}")
        print(f"run {prefix}-{t}: {'pass' if passed else 'fail'}")


def cmd_prompts(describe_path: Path) -> int:
    raw = describe_path.read_bytes()
    describe = (
        raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8")
    )
    for t in TASKS:
        if not root_of(t).is_dir():
            print(f"FAIL {root_of(t).as_posix()} is missing; seed it with eval-harness.ts first")
            return 2
    if not (root_of("t3") / "seed" / "source-id.txt").is_file():
        print("FAIL the t3 root was not seeded with dashboard-4k.png")
        return 2
    transcript = TRANSCRIPT.read_text(encoding="utf-8").strip("\n")
    expected = EXPECTED.read_bytes().decode("utf-8")
    bodies = build(EVAL_RUN.read_text(encoding="utf-8"), describe, transcript, expected)
    for t, body in bodies.items():
        prompt_path(t).write_bytes((body + "\n").encode("utf-8"))
        print(f"real-{t}: {len(body)} chars -> {prompt_path(t).name}")
    return 0


def cmd_check() -> int:
    checker = load_checker()
    key = json.loads(KEY.read_text(encoding="utf-8"))
    roots = {t: root_of(t) for t in TASKS}
    reports = {t: report_path(t) for t in TASKS}
    results = verdicts(checker.check_run, roots, reports, key)
    show("s92-real", results)
    ok = all(passed for passed, _ in results.values())
    print("eval-rerun check: ok" if ok else "eval-rerun check: failed")
    return 0 if ok else 1


def cmd_session64() -> int:
    checker = load_checker()
    key = json.loads(KEY.read_text(encoding="utf-8"))
    roots = {t: BASE / f"real-{t}" / "root" for t in TASKS}
    reports = {t: S64_REPORTS / f"s64-eval-real-{t}-report.txt" for t in TASKS}
    results = verdicts(checker.check_run, roots, reports, key)
    show("s64-real", results)
    got = {t: passed for t, (passed, _) in results.items()}
    ok = got == S64_REAL
    print(f"session 64 real result reproduced: {ok} (got {got}, want {S64_REAL})")
    return 0 if ok else 1


def selftest() -> int:
    failures = 0

    def expect(label: str, cond: bool) -> None:
        nonlocal failures
        failures += 0 if cond else 1
        print(f"{'PASS' if cond else 'FAIL'} selftest {label}")

    plan = "\n".join(
        [
            "x",
            "```text",
            "Open {{DESCRIBE}} at {{ROOT}}",
            "```",
            *[f"```text\nTask {t} {{{{MEDIA}}}} {{{{TRANSCRIPT}}}}\n```" for t in TASKS],
        ]
    )
    exp = f"{LEAD} {ZOOM}; x.\nWorkflow: capture → get (0–1)."
    head = f"## Server instructions\n\n## avkit_capture description\n\n{exp}"
    good = f"[rtk] notice\n{head}\n\n{CUT}\n\n- avkit_capture.export: notes"
    bodies = build(plan, good, "T", exp)
    expect("three prompts built", sorted(bodies) == list(TASKS))
    expect(
        "the surface stops above CUT",
        all("- avkit_capture.export" not in b for b in bodies.values()),
    )
    expect("the rtk line is dropped", all("[rtk]" not in b for b in bodies.values()))
    expect("each prompt names its s92 root", all(root_of(t).as_posix() in bodies[t] for t in TASKS))
    for label, describe in [
        ("an old surface without the lead is refused", good.replace(LEAD, "Old.")),
        ("a receipt without CUT is refused", good.replace(CUT, "")),
        ("a receipt with two CUT lines is refused", good + "\n" + CUT),
        ("an escape sequence is refused", "\x1b[0m" + good),
        (
            "a cp437-decoded arrow is refused (D-1186)",
            good.encode("utf-8").decode("cp437").replace("[rtk] notice\n", ""),
        ),
        ("a cp437-decoded dash alone is refused (D-1186)", good.replace("–", "ΓÇô")),
        ("a cp437-decoded arrow alone is refused (D-1186)", good.replace("→", "ΓåÆ")),
        ("a surface without the expected text verbatim is refused", good.replace("; x.", "; y.")),
    ]:
        try:
            build(plan, describe, "T", exp)
            expect(label, False)
        except ValueError:
            expect(label, True)
    try:
        build(plan, good, "T", "")
        expect("an empty expected text is refused", False)
    except ValueError:
        expect("an empty expected text is refused", True)
    try:
        build(plan.replace("```text\nTask t3", "```txt\nTask t3"), good, "T", exp)
        expect("a missing task block is refused", False)
    except ValueError:
        expect("a missing task block is refused", True)

    def fake(passing: set[str]):
        return lambda task, root, report, key, media: [(task in passing, f"{task} line")]

    nowhere = {t: Path("C:/Temp/av-kit/mcp-audit-refresh/selftest-none") for t in TASKS}
    all_pass = verdicts(fake(set(TASKS)), nowhere, nowhere, {})
    expect("all runs pass -> verdict pass", all(p for p, _ in all_pass.values()))
    one_fail = verdicts(fake({"t1", "t3"}), nowhere, nowhere, {})
    expect("one run fails -> verdict fail", not all(p for p, _ in one_fail.values()))
    s64_like = verdicts(fake({"t3"}), nowhere, nowhere, {})
    expect(
        "the Session 64 shape matches S64_REAL",
        {t: p for t, (p, _) in s64_like.items()} == S64_REAL,
    )
    print("eval-rerun selftest: ok" if failures == 0 else f"eval-rerun selftest: {failures} failed")
    return 0 if failures == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", nargs="?", choices=["prompts", "check"])
    parser.add_argument("--describe", type=Path)
    parser.add_argument("--session64", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            return selftest()
        if args.session64:
            return cmd_session64()
        if args.command == "prompts" and args.describe is not None:
            return cmd_prompts(args.describe)
        if args.command == "check":
            return cmd_check()
    except (OSError, ValueError, ImportError) as exc:
        print(f"FAIL {type(exc).__name__}: {exc}")
        return 2
    parser.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
