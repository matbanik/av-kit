"""Session 100 D-1301 counting rule for a gated stage with two files (task rows 8 and 9 and the
gate's ``gated-count`` step; implementation-plan.md §The D-1301 count; AC-16; D-1314).

``E2E-CLIPBOARD-PRIMER-EMPTY`` closes after five gated runs "with outcome run and 2 of 2
expected" (D-1301), counted from ``r20261120T215925Z-9ac9adc``. From this session the gated stage
holds five tests in two files. The rule: a run counts toward D-1301 only when its gated outcome
is ``run`` and ``PRIMER_FILE``'s two tests are both in the gated report with status
``expected``; the other gated file's results never decide D-1301 (a failure there still fails
the gated stage, exit 40, and is a finding for the row, not a D-1301 count).

    python gated-count.py --run RUN_DIR [--prior N]   # RUN_DIR/summary.json, host/gated/report.json
    python gated-count.py --selftest

It prints one ``gated-count: outcome=... primer=<passed>/<listed> other=<passed>/<listed>``
line, then ``d1301: counts`` or ``d1301: does-not-count (<reason>)``, then
``d1301 tally: <prior + 1 or prior> of 5 -> close|open`` (``--prior`` defaults to 2, the runs
counted before this session), and ``gated-stage: pass|fail|not-run``. Exit 0 when the files read
cleanly, whatever the verdict. Exit 1 names a missing, empty or invalid summary, a summary with
no gated object, or a ``run`` outcome whose gated report is missing, empty, invalid or holds a
test of another file (Session 98 RULE-1: each such observation is a non-pass, never a count).
It reads only the run folder and writes nothing.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import tempfile

PRIMER_FILE = "capture-system-clipboard.test.ts"
OTHER_FILE = "copy-system-clipboard.test.ts"
PRIMER_TESTS = 2
OTHER_TESTS = 3
BAR = 5
START_RUN = "r20261120T215925Z-9ac9adc"
OUTCOMES = (
    "run",
    "skipped-connected",
    "skipped-undecided",
    "voided-connected-during",
    "voided-undecided-during",
)


class Unreadable(Exception):
    pass


def _json(path: pathlib.Path, label: str) -> object:
    if not path.is_file():
        raise Unreadable(f"{label} missing: {path.name}")
    raw = path.read_bytes()
    if not raw.strip():
        raise Unreadable(f"{label} empty: {path.name}")
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        raise Unreadable(f"{label} invalid: {path.name}: {exc}") from exc


def report_rows(report: object) -> list[tuple[str, str]]:
    """(file name, status) for every test in a Playwright JSON report."""
    if not isinstance(report, dict) or not isinstance(report.get("suites"), list):
        raise Unreadable("gated report invalid: no suites")
    rows: list[tuple[str, str]] = []

    def walk(suite: dict, file: str) -> None:
        here = suite.get("file") or file
        for spec in suite.get("specs", []):
            for t in spec.get("tests", []):
                name = pathlib.PurePath(str(spec.get("file") or here)).name
                rows.append((name, str(t.get("status"))))
        for child in suite.get("suites", []):
            walk(child, here)

    for top in report["suites"]:
        walk(top, top.get("file", ""))
    return rows


def count(run_dir: pathlib.Path, prior: int) -> tuple[int, list[str]]:
    lines: list[str] = []
    try:
        summary = _json(run_dir / "summary.json", "summary")
        gated = summary.get("gated") if isinstance(summary, dict) else None
        if not isinstance(gated, dict):
            raise Unreadable("summary has no gated object")
        outcome = gated.get("outcome")
        if outcome not in OUTCOMES:
            raise Unreadable(f"gated outcome {outcome!r} is not one of the five")
        primer = other = (0, 0)
        stage = "not-run"
        if outcome == "run":
            rows = report_rows(_json(run_dir / "host" / "gated" / "report.json", "gated report"))
            stray = sorted({f for f, _ in rows if f not in (PRIMER_FILE, OTHER_FILE)})
            if stray:
                raise Unreadable(f"gated report holds other files: {stray}")
            p = [s for f, s in rows if f == PRIMER_FILE]
            o = [s for f, s in rows if f == OTHER_FILE]
            primer = (sum(1 for s in p if s == "expected"), len(p))
            other = (sum(1 for s in o if s == "expected"), len(o))
            stage = "pass" if all(s == "expected" for _, s in rows) and rows else "fail"
    except Unreadable as exc:
        return 1, [f"gated-count: unreadable: {exc}"]
    lines.append(
        f"gated-count: outcome={outcome} primer={primer[0]}/{primer[1]} other={other[0]}/{other[1]}"
    )
    if outcome != "run":
        verdict = f"does-not-count (outcome {outcome})"
    elif primer != (PRIMER_TESTS, PRIMER_TESTS):
        verdict = f"does-not-count ({PRIMER_FILE} {primer[0]} of {primer[1]} expected)"
    else:
        verdict = "counts"
    tally = prior + (1 if verdict == "counts" else 0)
    lines.append(f"d1301: {verdict}")
    lines.append(
        f"d1301 tally: {tally} of {BAR} from {START_RUN} -> {'close' if tally >= BAR else 'open'}"
    )
    if outcome == "run" and other[1] != OTHER_TESTS:
        lines.append(f"gated-count: note: {OTHER_FILE} listed {other[1]}, {OTHER_TESTS} expected")
    lines.append(f"gated-stage: {stage}")
    return 0, lines


def _report(rows: list[tuple[str, str]]) -> dict:
    suites = []
    for name in sorted({f for f, _ in rows}):
        specs = [
            {"title": f"t{i}", "file": name, "tests": [{"status": s}]}
            for i, (f, s) in enumerate(rows)
            if f == name
        ]
        suites.append({"title": name, "file": name, "specs": specs, "suites": []})
    return {"suites": suites, "stats": {}, "errors": []}


def selftest() -> int:
    ok5 = [(PRIMER_FILE, "expected")] * 2 + [(OTHER_FILE, "expected")] * 3
    cases: list[tuple[str, object, object, int, str]] = [
        ("run 5 of 5", {"gated": {"outcome": "run"}}, _report(ok5), 0, "d1301: counts"),
        (
            "other file fails",
            {"gated": {"outcome": "run"}},
            _report(ok5[:2] + [(OTHER_FILE, "unexpected")] + ok5[3:]),
            0,
            "d1301: counts",
        ),
        (
            "primer fails",
            {"gated": {"outcome": "run"}},
            _report([(PRIMER_FILE, "unexpected")] + ok5[1:]),
            0,
            "d1301: does-not-count",
        ),
        (
            "primer test missing",
            {"gated": {"outcome": "run"}},
            _report(ok5[1:]),
            0,
            "d1301: does-not-count",
        ),
        ("skipped", {"gated": {"outcome": "skipped-connected"}}, None, 0, "d1301: does-not-count"),
        (
            "voided",
            {"gated": {"outcome": "voided-undecided-during"}},
            None,
            0,
            "d1301: does-not-count",
        ),
        ("summary missing", None, None, 1, "unreadable: summary missing"),
        ("summary empty", b"", None, 1, "unreadable: summary empty"),
        ("summary invalid", b"{not json", None, 1, "unreadable: summary invalid"),
        ("no gated object", {"tests": 1}, None, 1, "unreadable: summary has no gated object"),
        ("unknown outcome", {"gated": {"outcome": "ran"}}, None, 1, "unreadable: gated outcome"),
        ("run, report missing", {"gated": {"outcome": "run"}}, None, 1, "gated report missing"),
        ("run, report empty", {"gated": {"outcome": "run"}}, b"  ", 1, "gated report empty"),
        ("run, report invalid", {"gated": {"outcome": "run"}}, b"[1", 1, "gated report invalid"),
        (
            "run, stray file",
            {"gated": {"outcome": "run"}},
            _report(ok5 + [("x.test.ts", "expected")]),
            1,
            "other files",
        ),
    ]
    wrong: list[str] = []
    with tempfile.TemporaryDirectory(prefix="gated-count-") as tmp:
        for i, (name, summary, report, want_code, want_text) in enumerate(cases):
            d = pathlib.Path(tmp) / f"c{i}"
            (d / "host" / "gated").mkdir(parents=True)
            for obj, path in (
                (summary, d / "summary.json"),
                (report, d / "host/gated/report.json"),
            ):
                if obj is None:
                    continue
                path.write_bytes(obj if isinstance(obj, bytes) else json.dumps(obj).encode())
            code, lines = count(d, 2)
            text = "\n".join(lines)
            good = code == want_code and want_text in text
            print(
                f"case {name}: exit {code} {'ok' if good else 'WRONG'} | {lines[-1] if lines else ''}"  # noqa: E501
            )
            if not good:
                wrong.append(name)
        d = pathlib.Path(tmp) / "tally"
        (d / "host" / "gated").mkdir(parents=True)
        (d / "summary.json").write_text(json.dumps({"gated": {"outcome": "run"}}), encoding="utf-8")
        (d / "host/gated/report.json").write_text(json.dumps(_report(ok5)), encoding="utf-8")
        _, lines = count(d, 4)
        if "d1301 tally: 5 of 5" not in "\n".join(lines) or "-> close" not in "\n".join(lines):
            wrong.append("tally reaches the bar")
        _, lines = count(d, 2)
        if "-> open" not in "\n".join(lines):
            wrong.append("tally below the bar")
    print(f"gated-count selftest: {len(cases) + 2} case(s), {len(wrong)} wrong: {wrong}")
    return 1 if wrong else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run")
    ap.add_argument("--prior", type=int, default=2)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.run:
        print("usage: gated-count.py --run RUN_DIR [--prior N] | --selftest")
        return 2
    code, lines = count(pathlib.Path(a.run), a.prior)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
