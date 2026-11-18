"""Session 91 assertion and wait check (D-1151 ASSERTIONS_KEPT, D-1145 no retries, no raised
timeouts).

    uv run --no-sync python <plan>/assert-check.py --snapshot     (row 0: copy the baselines)
    uv run --no-sync python <plan>/assert-check.py                (rows 4 to 8, the gate)
    uv run --no-sync python <plan>/assert-check.py --selftest

--snapshot copies SPECS, HARNESS files that exist and CONFIG into --baseline (default
C:/Temp/av-kit/e2e-pointer-flakes/baseline-copies/assert) and refuses to overwrite a copy.

The check compares the working tree with those copies:
1. ASSERTIONS_KEPT: in each of SPECS, the multiset of stripped lines that hold `expect(` or
   `expect.` equals the copy's. An added, removed or edited assertion line is named with its
   file and the line text, and fails the check (an assertion change is M-7; S7 undoes it).
2. TESTS_KEPT: in each of SPECS, the list of `test(` title lines equals the copy's, in order.
3. NO_NEW_WAIT_KNOBS: across SPECS + HARNESS + NEW, the count of each BANNED token is no higher
   than across the copies (a helper moved into a shared file keeps or lowers the count; a new
   retry, timeout option, fixed sleep or slow mark raises it). One named exception: ALLOWED_TIMEOUT,
   the text `timeout: AC9_SPAWN_TIMEOUT_MS` in ui/tests/e2e/e2e-diag.test.ts, the bound on AC-9's
   one spawnSync (D-1149). It is allowed once, in that file only, and taken off the `timeout:`
   count; a second copy, or the text in any other file, fails.
4. CONFIG_KEPT: ui/playwright.config.ts is byte-identical to its copy.
5. LF_ONLY: every file of SPECS + HARNESS + NEW that exists holds no CR byte.
6. EXIT_WAIT_KEPT: electron-app.ts still holds `const EXIT_WAIT_MS = 5_000`.

Exit 0 when all six hold, 1 otherwise, 2 when a baseline copy is missing.
--selftest runs the six checks on synthetic trees under the scratch folder.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from collections import Counter
from pathlib import Path

REPO = Path("P:/av-kit")
SCRATCH = Path("C:/Temp/av-kit/e2e-pointer-flakes")
SPECS = (
    "ui/tests/e2e/download-queue.test.ts",
    "ui/tests/e2e/convert-queue.test.ts",
    "ui/tests/e2e/capture-inbox.test.ts",
)
HARNESS = (
    "ui/tests/e2e/electron-app.ts",
    "ui/tests/e2e/electron-env.ts",
    "ui/tests/e2e/main-error-watch.cjs",
)
NEW = (
    "ui/tests/e2e/pointer-settle.ts",
    "ui/tests/e2e/e2e-diag.ts",
    "ui/tests/e2e/e2e-diag.test.ts",
    "ui/tests/unit/e2e-pointer.test.ts",
)
CONFIG = "ui/playwright.config.ts"
BANNED = (
    "retries",
    "waitForTimeout(",
    "setTimeout(",
    "test.slow",
    "repeatEach",
    "timeout:",
    "Timeout =",
    "sleep(",
)
EXIT_WAIT = "const EXIT_WAIT_MS = 5_000"
ALLOWED_TIMEOUT = ("ui/tests/e2e/e2e-diag.test.ts", "timeout: AC9_SPAWN_TIMEOUT_MS")


def text_of(path: Path) -> str:
    return path.read_bytes().decode("utf-8") if path.exists() else ""


def assertion_lines(text: str) -> Counter[str]:
    return Counter(
        line.strip() for line in text.split("\n") if "expect(" in line or "expect." in line
    )


def test_titles(text: str) -> list[str]:
    return [line.strip() for line in text.split("\n") if line.startswith("test(")]


def token_counts(texts: list[str]) -> Counter[str]:
    joined = "\n".join(texts)
    return Counter({token: joined.count(token) for token in BANNED})


def check(repo: Path, baseline: Path) -> tuple[int, list[str]]:
    out: list[str] = []
    bad = 0
    for rel in (*SPECS, *HARNESS, CONFIG):
        if (repo / rel).exists() and not (baseline / rel).exists():
            out.append(f"SETUP: no baseline copy of {rel}")
            return 2, out
    for rel in SPECS:
        now, then = text_of(repo / rel), text_of(baseline / rel)
        added = assertion_lines(now) - assertion_lines(then)
        removed = assertion_lines(then) - assertion_lines(now)
        for line, n in sorted(added.items()):
            out.append(f"ASSERTIONS_KEPT FAIL {rel}: added x{n}: {line}")
        for line, n in sorted(removed.items()):
            out.append(f"ASSERTIONS_KEPT FAIL {rel}: removed x{n}: {line}")
        bad += 1 if added or removed else 0
        kept = sum(assertion_lines(then).values())
        out.append(
            f"ASSERTIONS_KEPT {rel}: {kept} baseline assertion lines;"
            f" changed {len(added) + len(removed)}"
        )
        if test_titles(now) != test_titles(then):
            out.append(f"TESTS_KEPT FAIL {rel}: the test( title lines differ")
            bad += 1
        else:
            out.append(f"TESTS_KEPT {rel}: {len(test_titles(now))} tests")
    before = token_counts([text_of(baseline / rel) for rel in (*SPECS, *HARNESS)])
    after = token_counts([text_of(repo / rel) for rel in (*SPECS, *HARNESS, *NEW)])
    owner, named = ALLOWED_TIMEOUT
    for rel in (*SPECS, *HARNESS, *NEW):
        n = text_of(repo / rel).count(named)
        if n and (rel != owner or n > 1):
            out.append(f"NO_NEW_WAIT_KNOBS FAIL {rel}: {named!r} x{n} (allowed once, in {owner})")
            bad += 1
    allowed = min(text_of(repo / owner).count(named), 1)
    after["timeout:"] -= allowed
    out.append(f"NO_NEW_WAIT_KNOBS allowed {named!r} in {owner}: {allowed}")
    for token in BANNED:
        grew = after[token] > before[token]
        out.append(
            f"NO_NEW_WAIT_KNOBS {'FAIL ' if grew else ''}{token!r}:"
            f" {before[token]} -> {after[token]}"
        )
        bad += 1 if grew else 0
    same = (repo / CONFIG).read_bytes() == (baseline / CONFIG).read_bytes()
    out.append(f"CONFIG_KEPT {'' if same else 'FAIL '}{CONFIG}")
    bad += 0 if same else 1
    for rel in (*SPECS, *HARNESS, *NEW):
        path = repo / rel
        if path.exists():
            crs = path.read_bytes().count(b"\r")
            if crs:
                out.append(f"LF_ONLY FAIL {rel}: {crs} CR byte(s)")
                bad += 1
    out.append("LF_ONLY checked")
    exit_wait = EXIT_WAIT in text_of(repo / "ui/tests/e2e/electron-app.ts")
    out.append(f"EXIT_WAIT_KEPT {'' if exit_wait else 'FAIL '}{EXIT_WAIT}")
    bad += 0 if exit_wait else 1
    return (1 if bad else 0), out


def snapshot(repo: Path, baseline: Path) -> int:
    for rel in (*SPECS, *HARNESS, CONFIG):
        src, dst = repo / rel, baseline / rel
        if not src.exists():
            continue
        if dst.exists():
            print(f"REFUSED: {dst.relative_to(baseline)} already has a baseline copy")
            return 1
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        print(f"copied {rel} ({len(src.read_bytes())} B)")
    return 0


def selftest() -> int:
    failures: list[str] = []

    def expect_code(name: str, got: int, want: int) -> None:
        ok = got == want
        print(f"{'ok  ' if ok else 'FAIL'} {name} (exit {got}, want {want})")
        if not ok:
            failures.append(name)

    root = SCRATCH / "assert-check-selftest"
    if root.exists():
        shutil.rmtree(root)
    base, tree = root / "base", root / "tree"
    spec = (
        "import { expect, test } from '@playwright/test'\n"
        "async function aim() {\n  await page.mouse.move(1, 2)\n}\n"
        "test('AC-1 a', async () => {\n  expect(a).toBe(1)\n  await expect(b).toHaveCount(2)\n})\n"
    )
    app = "const EXIT_WAIT_MS = 5_000\nsetTimeout(done, EXIT_WAIT_MS)\n"
    config = "export default { timeout: 60_000 }\n"

    def build(where: Path, spec_text: str, app_text: str = app, extra: dict | None = None) -> None:
        for rel in SPECS:
            (where / rel).parent.mkdir(parents=True, exist_ok=True)
            (where / rel).write_bytes(spec_text.encode("utf-8"))
        for rel in HARNESS:
            (where / rel).write_bytes((app_text if rel.endswith("app.ts") else "x\n").encode())
        (where / CONFIG).write_bytes(config.encode())
        for rel, body in (extra or {}).items():
            (where / rel).parent.mkdir(parents=True, exist_ok=True)
            (where / rel).write_bytes(body.encode("utf-8"))

    def fresh(spec_text: str, app_text: str = app, extra: dict | None = None) -> int:
        if tree.exists():
            shutil.rmtree(tree)
        build(tree, spec_text, app_text, extra)
        return check(tree, base)[0]

    build(base, spec)
    expect_code("an unchanged tree passes", fresh(spec), 0)
    moved = spec.replace("  await page.mouse.move(1, 2)\n", "  await settle(page)\n")
    expect_code("a non-assertion edit passes", fresh(moved), 0)
    expect_code(
        "an assertion edit fails",
        fresh(spec.replace("expect(a).toBe(1)", "expect(a).toBe(2)")),
        1,
    )
    expect_code(
        "an added assertion fails",
        fresh(spec.replace("  expect(a).toBe(1)\n", "  expect(a).toBe(1)\n  expect.poll(c)\n")),
        1,
    )
    expect_code(
        "a moved assertion line (same text) passes",
        fresh(
            spec.replace("  expect(a).toBe(1)\n  await expect(b)", "  await expect(b)").replace(
                "toHaveCount(2)\n", "toHaveCount(2)\n  expect(a).toBe(1)\n"
            )
        ),
        0,
    )
    expect_code(
        "a removed test fails", fresh(spec.replace("test('AC-1 a'", "test.skip('AC-1 a'")), 1
    )
    expect_code(
        "a waitForTimeout in a new helper fails",
        fresh(spec, extra={NEW[0]: "await page.waitForTimeout(400)\n"}),
        1,
    )
    expect_code(
        "a timeout option in a spec fails",
        fresh(spec.replace("await page.mouse.move(1, 2)", "await x.waitFor({ timeout: 9 })")),
        1,
    )
    expect_code(
        "a setTimeout moved from a harness file into a helper passes",
        fresh(spec, app_text=EXIT_WAIT + "\n", extra={NEW[0]: "setTimeout(done, EXIT_WAIT_MS)\n"}),
        0,
    )
    expect_code(
        "a retries knob fails",
        fresh(spec, extra={NEW[1]: "test.describe.configure({ retries: 2 })\n"}),
        1,
    )
    named = "  spawnSync(cmd, args, { timeout: AC9_SPAWN_TIMEOUT_MS })\n"
    expect_code("the one named AC-9 spawn timeout passes", fresh(spec, extra={NEW[2]: named}), 0)
    expect_code(
        "a second named AC-9 spawn timeout fails", fresh(spec, extra={NEW[2]: named * 2}), 1
    )
    expect_code(
        "the named AC-9 spawn timeout in another file fails", fresh(spec, extra={NEW[0]: named}), 1
    )
    expect_code("a raised exit wait fails", fresh(spec, app_text=app.replace("5_000", "9_000")), 1)
    expect_code("a CR byte fails", fresh(spec.replace("\n", "\r\n", 1)), 1)
    if tree.exists():
        shutil.rmtree(tree)
    build(tree, spec)
    (tree / CONFIG).write_bytes(b"export default { timeout: 90_000 }\n")
    expect_code("a changed config fails", check(tree, base)[0], 1)
    shutil.rmtree(base / "ui/tests/e2e")
    expect_code("a missing baseline copy is a setup failure", check(tree, base)[0], 2)
    print(f"assert-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--snapshot", action="store_true")
    parser.add_argument("--baseline", type=Path, default=SCRATCH / "baseline-copies/assert")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.snapshot:
        return snapshot(REPO, args.baseline)
    code, lines = check(REPO, args.baseline)
    print("\n".join(lines))
    print("PASS" if code == 0 else ("SETUP FAIL" if code == 2 else "FAIL"))
    return code


if __name__ == "__main__":
    sys.exit(main())
