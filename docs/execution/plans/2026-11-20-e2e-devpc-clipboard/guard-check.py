"""Session 100 gated-file guard check (task row 2 and the gate's ``guard-list`` step;
implementation-plan.md §The moves and §Test pins; AC-2; D-1305), from Session 98's (D-1282).

Both gated files, ``ui/tests/e2e/capture-system-clipboard.test.ts`` (Session 98) and
``ui/tests/e2e/copy-system-clipboard.test.ts`` (this session), open with a file-level
``test.skip(process.env.AVKIT_E2E_CLIPBOARD_GATED !== '1', GUARD_REASON)``. Only the gated
stage of ``tools/e2e_host/run-e2e.ps1`` sets that variable, so any other run of the suite, the
dev PC's ``npm run test:e2e`` included, lists their five tests as skipped and never launches
them. This script proves that from Playwright's own list, without running a test::

    python guard-check.py --list OUT.json   # npm run test:e2e -- --list, then --judge OUT
    python guard-check.py --judge OUT.json  # read a list report already written
    python guard-check.py --selftest        # the judge on fixtures

``--list`` runs ``npm --prefix ui run test:e2e -- --list --reporter=json --outputFile=OUT``
(the package script, ``ui/scripts/playwright-with-outputfile.mjs``, turns ``--outputFile`` into
the config's JSON reporter) with ``ELECTRON_RUN_AS_NODE`` and ``AVKIT_E2E_CLIPBOARD_GATED``
removed from the child's environment. ``--list`` loads the spec files and runs no test and no
global setup; the argv is asserted to hold it before anything starts. OUT must not exist.

``--judge`` passes (exit 0) only when the report has no error, ``EXPECT_FILES`` spec files and
``EXPECT_TESTS`` tests; the tests of each ``GATED`` file are exactly its titles, each listed
``skipped`` with a ``skip`` annotation whose description is ``GUARD_REASON`` and no result; and
every other test is listed ``passed`` with no result. Exit 1 names each difference; exit 2 is a
setup failure (npm missing, OUT present, the list command failing, unreadable JSON).
"""

from __future__ import annotations

import copy
import json
import os
import pathlib
import shutil
import subprocess
import sys

#: Gated file -> title prefixes of its tests.
GATED = {
    "capture-system-clipboard.test.ts": ("AC-88.12 (a)(b)(f)", "AC-132.23"),
    "copy-system-clipboard.test.ts": ("C1-5 console copy", "AC-71.15 (b)", "AC-71.15 (d)"),
}
GATE_ENV = "AVKIT_E2E_CLIPBOARD_GATED"
GUARD_REASON = "system clipboard spec: runs only in the gated stage on the second Windows host"
#: After rows 1 and 2: f1ba411's 30 spec files (239 tests) plus copy-system-clipboard (3 moved
#: tests) and clipboard-guard (1 guard test); no kept test added or removed.
EXPECT_FILES = 32
EXPECT_TESTS = 243
#: D-1342 (coordinator ruling): Session 99's new E2E file. Its tests are counted by file name
#: only and kept out of the counts and the judgement above.
PEER_FILES = ("help-quick-start.test.ts",)


def list_tests(report: dict) -> list[dict]:
    """Every test entry as {file, title, expected, annotations, results}."""
    found: list[dict] = []

    def walk(suite: dict, file: str) -> None:
        for spec in suite.get("specs", []):
            for t in spec.get("tests", []):
                found.append(
                    {
                        "file": pathlib.PurePath(spec.get("file") or file).name,
                        "title": spec.get("title", ""),
                        "expected": t.get("expectedStatus"),
                        "annotations": t.get("annotations", []),
                        "results": t.get("results", []),
                    }
                )
        for child in suite.get("suites", []):
            walk(child, file)

    for top in report.get("suites", []):
        walk(top, top.get("file", ""))
    return found


def judge(report: object) -> list[str]:
    if not isinstance(report, dict):
        return ["the report is not a JSON object"]
    bad: list[str] = []
    errors = report.get("errors", [])
    if errors:
        bad.append(f"the list holds {len(errors)} error(s)")
    tests = [t for t in list_tests(report) if t["file"] not in PEER_FILES]
    files = {t["file"] for t in tests}
    if len(files) != EXPECT_FILES:
        bad.append(f"{len(files)} spec files listed, {EXPECT_FILES} expected")
    if len(tests) != EXPECT_TESTS:
        bad.append(f"{len(tests)} tests listed, {EXPECT_TESTS} expected")
    for name, prefixes in GATED.items():
        gated = [t for t in tests if t["file"] == name]
        titles = sorted(t["title"] for t in gated)
        if len(gated) != len(prefixes) or not all(
            sum(1 for t in titles if t.startswith(p)) == 1 for p in prefixes
        ):
            bad.append(f"{name} lists {titles}, not its {len(prefixes)} moved tests")
        for t in gated:
            skips = [a for a in t["annotations"] if isinstance(a, dict) and a.get("type") == "skip"]
            if t["expected"] != "skipped":
                bad.append(f"{t['title']}: listed {t['expected']}, not skipped")
            if [a.get("description") for a in skips] != [GUARD_REASON]:
                bad.append(f"{t['title']}: its skip annotation is not the guard's one reason")
            if t["results"]:
                bad.append(f"{t['title']}: has a result, so it ran")
    for t in tests:
        if t["file"] in GATED:
            continue
        if t["expected"] != "passed":
            bad.append(f"{t['file']} {t['title']}: listed {t['expected']}, not passed")
        if t["results"]:
            bad.append(f"{t['file']} {t['title']}: has a result, so it ran")
    return bad


def run_list(out: pathlib.Path) -> int:
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if npm is None:
        print("guard-check: npm not found")
        return 2
    if out.exists():
        print(f"guard-check: {out} exists; a list report is written fresh")
        return 2
    argv = [npm, "--prefix", "ui", "run", "test:e2e", "--", "--list", "--reporter=json"]
    argv.append(f"--outputFile={out}")
    assert "--list" in argv, "the guard check only ever lists"
    env = dict(os.environ)
    env.pop("ELECTRON_RUN_AS_NODE", None)
    env.pop(GATE_ENV, None)
    env.pop("PLAYWRIGHT_JSON_OUTPUT_NAME", None)
    r = subprocess.run(argv, env=env, stdin=subprocess.DEVNULL, timeout=600)
    print(f"guard-check: list exit {r.returncode}")
    if r.returncode != 0 or not out.is_file():
        return 2
    return run_judge(out)


def run_judge(path: pathlib.Path) -> int:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"guard-check: cannot read {path}: {exc}")
        return 2
    bad = judge(report)
    tests = list_tests(report) if isinstance(report, dict) else []
    skipped = sum(1 for t in tests if t["expected"] == "skipped")
    peer = sum(1 for t in tests if t["file"] in PEER_FILES)
    print(f"guard-check: {len(tests)} tests listed, {skipped} skipped")
    print(f"guard-check: Session 99 file tests (D-1342, not judged): {peer}")
    for b in bad:
        print("guard-check:", b)
    print(f"guard-check: {'ok' if not bad else 'FAILED'} ({len(bad)} problem(s))")
    return 1 if bad else 0


def fixture() -> dict:
    def test(expected: str, skip: bool) -> dict:
        ann = [{"type": "skip", "description": GUARD_REASON}] if skip else []
        return {"expectedStatus": expected, "annotations": ann, "results": []}

    gated_tests = sum(len(p) for p in GATED.values())
    plain_files = EXPECT_FILES - len(GATED)
    plain_tests = EXPECT_TESTS - gated_tests
    suites = []
    for i in range(plain_files):
        n = plain_tests // plain_files + (1 if i < plain_tests % plain_files else 0)
        name = f"spec-{i}.test.ts"
        specs = [
            {"title": f"t{j}", "file": name, "tests": [test("passed", False)]} for j in range(n)
        ]
        suites.append({"title": name, "file": name, "specs": specs})
    for name, prefixes in GATED.items():
        specs = [
            {"title": p + " x", "file": name, "tests": [test("skipped", True)]} for p in prefixes
        ]
        suites.append({"title": name, "file": name, "specs": specs, "suites": []})
    return {"config": {}, "suites": suites, "errors": []}


def selftest() -> int:
    base = fixture()
    cases: list[tuple[str, dict, bool]] = [("the listed guard", base, True)]

    def variant(name: str, edit) -> None:
        r = copy.deepcopy(base)
        edit(r)
        cases.append((name, r, False))

    first, second = len(base["suites"]) - 2, len(base["suites"]) - 1
    for label, idx in (("first", first), ("second", second)):
        variant(f"the gate variable set ({label})", lambda r, i=idx: _set_new(r, i, "passed", []))
        variant(
            f"another reason ({label})",
            lambda r, i=idx: _set_new(r, i, "skipped", [{"type": "skip"}]),
        )
        variant(
            f"a clipboard test ran ({label})",
            lambda r, i=idx: r["suites"][i]["specs"][0]["tests"][0]["results"].append(
                {"status": "passed"}
            ),
        )
        variant(f"a moved test missing ({label})", lambda r, i=idx: r["suites"][i]["specs"].pop())
    variant(
        "a kept test skipped",
        lambda r: r["suites"][0]["specs"][0]["tests"].__setitem__(
            0, {"expectedStatus": "skipped", "annotations": [], "results": []}
        ),
    )
    variant("a list error", lambda r: r["errors"].append({"message": "x"}))
    variant("a file missing", lambda r: r["suites"].pop(0))
    variant("the second gated file missing", lambda r: r["suites"].pop())
    peer_test = {"expectedStatus": "passed", "annotations": [], "results": []}
    peer_spec = {"title": "h", "file": PEER_FILES[0], "tests": [peer_test]}
    with_peer = copy.deepcopy(base)
    with_peer["suites"].append(
        {"title": PEER_FILES[0], "file": PEER_FILES[0], "specs": [peer_spec]}
    )
    cases.append(("Session 99's file listed beside the guard (D-1342)", with_peer, True))
    wrong = []
    for name, report, want in cases:
        bad = judge(report)
        passed = not bad
        print(f"case {name}: {'pass' if passed else 'refused'} {bad[:1]}")
        if passed != want:
            wrong.append(name)
    print(f"guard-check selftest: {len(cases)} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def _set_new(report: dict, idx: int, expected: str, ann: list) -> None:
    for spec in report["suites"][idx]["specs"]:
        spec["tests"][0]["expectedStatus"] = expected
        spec["tests"][0]["annotations"] = ann


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) == 2 and argv[0] == "--list":
        return run_list(pathlib.Path(argv[1]))
    if len(argv) == 2 and argv[0] == "--judge":
        return run_judge(pathlib.Path(argv[1]))
    print("usage: guard-check.py --list OUT | --judge OUT | --selftest")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
