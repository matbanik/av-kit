"""Session 76 dispatch-suite check (rows 0, 5 and 6, the gate's dispatch-tests and dispatch-source
steps; AC-10). A copy of Session 82's (2026-11-14-review-limits-no-token-budget) with
DEFAULT_BASE at this plan's row-0 receipt, plus the ``--expect-clean`` and ``--source`` modes.

Usage::

    python dispatch-check.py [--exact-baseline | --expect-clean] --exit-file RECEIPT.exit RECEIPT
    python dispatch-check.py --source [--file PS1] [--base-source PS1]
    python dispatch-check.py --selftest [--base RECEIPT] [--base-source PS1]

``RECEIPT`` is a ``Test-CliDispatch.ps1`` receipt; ``RECEIPT.exit`` holds the suite's exit,
saved straight after the run. ANSI colour codes are stripped first. The check accepts only when
all of these hold:

* the receipt has exactly one ``Total: N | PASS: p FAIL: f SKIP: s`` line;
* the bracketed records agree with those counts: ``[PASS] name (Ns) - msg`` and
  ``[FAIL] name (Ns) - msg``, and ``[SKIP] name - reason`` (``Write-TestSkip`` prints no
  duration, D-741). The summary table's unbracketed rows are not records;
* N is at least ``MIN_TOTAL``, the plan-time total;
* every FAIL name is one of ``BASELINE_FAILS``; with ``--exact-baseline`` the FAIL set must be
  that pair exactly (row 5's Red);
* with ``--expect-clean`` there is no FAIL record at all, and both ``BASELINE_FAILS`` names
  appear as ``[PASS]`` records (row 6's Green);
* the exit is 0 when f is 0 and 1 when f is above 0, which is how the suite ends. Any other
  exit, such as a startup failure, is refused.

``--source`` checks ``DISPATCH_TEST`` (default ``.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1``)
against ``BASE`` (default ``C:/Temp/av-kit/tth/base/Test-CliDispatch.ps1``), per AC-10:

* the UTF-8 BOM is kept and every line ends in CRLF (no bare LF or CR);
* every line before arm 2's comment, and every line from ``$r2 = Get-OutputDir`` on, is
  byte-equal to ``BASE``; so both ``Write-TestResult`` lines are, which is also checked by name;
* arm 2 (its comment to the ``refusal created no placeholder dir`` line) holds no ``{{``, and
  holds the ``$phToken`` assignment;
* no changed line matches ``VERIFIER``'s three census patterns, copied verbatim from
  ``docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py``.

``--selftest`` builds its receipt fixtures from row 0's receipt (``--base``) and its source
fixtures from ``BASE`` with the planned edit applied in memory: it must accept the baseline
receipt (exit 1) and a clean copy (exit 0, ``--expect-clean``), and refuse an added ``[FAIL]``,
an empty receipt with exit 64, a ``Total:`` line that disagrees with its records, the baseline
under ``--expect-clean``, a clean copy missing one pair name, and source copies with the literal
token, an LF line, a changed assertion line, and a comment naming a model family and a digit.
"""

from __future__ import annotations

import pathlib
import re
import sys

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
RUN = re.compile(r"^\s*\[(PASS|FAIL)\] (.+?) \([0-9.]+s\) - ")
SKIP = re.compile(r"^\s*\[SKIP\] (.+?) - ")
TOTAL = re.compile(r"^\s*Total: (\d+) \| PASS: (\d+) FAIL: (\d+) SKIP: (\d+)\s*$")
MIN_TOTAL = 31
BASELINE_FAILS = frozenset({"placeholder receipts dir refused", "refusal created no placeholder dir"})
DEFAULT_BASE = "C:/Temp/av-kit/tth/tth-base-dispatch.txt"
DISPATCH_TEST = ".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1"
BASE_SOURCE = "C:/Temp/av-kit/tth/base/Test-CliDispatch.ps1"

#: VERIFIER's census patterns (verify_adoption.py governance_inventory), copied verbatim.
CENSUS = (
    ("routing class", re.compile(
        r"(?i)(?:--?(?:model)?class[ =]+|resolve\s+)[`'\"]?"
        r"(?:builder|coordinator|verifier)\b|"
        r"class pins[^\{]*\{[^}]*\b(?:builder|coordinator|verifier)\b"
    )),
    ("unconfigured routing", re.compile(
        r"(?i)(?:default (?:reviewer|model)|fallback)\s*:\s*"
        r"(?:GPT|Gemini|Claude|Opus|Sonnet|Grok)"
    )),
    ("numeric model pin", re.compile(
        r"gpt[- ]?\d|opus[- ]?\d|sonnet[- ]?\d|haiku[- ]?\d|grok[- ]?\d|"
        r"composer[- ]?\d|gemini[- ]?\d",
        re.I,
    )),
)
ARM2_START = b"            # 2. An uninstantiated placeholder."
ARM2_SUFFIX = b"            $r2 = Get-OutputDir\r\n"
ARM2_END = b'Write-TestResult "refusal created no placeholder dir"'
ASSERT_LINES = (b'Write-TestResult "placeholder receipts dir refused"', ARM2_END)
BOM = b"\xef\xbb\xbf"


def check(text: str, exit_text: str, exact: bool, clean: bool = False) -> list[str]:
    text = ANSI.sub("", text).replace("\r\n", "\n").replace("\r", "\n")
    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    fails: list[str] = []
    passes: list[str] = []
    totals: list[tuple[int, int, int, int]] = []
    for line in text.split("\n"):
        run = RUN.match(line)
        if run:
            counts[run.group(1)] += 1
            (fails if run.group(1) == "FAIL" else passes).append(run.group(2))
            continue
        skip = SKIP.match(line)
        if skip:
            counts["SKIP"] += 1
            continue
        total = TOTAL.match(line)
        if total:
            totals.append(tuple(int(g) for g in total.groups()))  # type: ignore[arg-type]
    problems: list[str] = []
    try:
        code = int(exit_text.strip().lstrip("\ufeff"))
    except ValueError:
        problems.append(f"the exit file holds {exit_text.strip()!r}, not an integer")
        code = None
    if len(totals) != 1:
        problems.append(f"expected one 'Total: N | PASS: p FAIL: f SKIP: s' line, found {len(totals)}")
        return problems
    n, p, f, s = totals[0]
    if (p, f, s) != (counts["PASS"], counts["FAIL"], counts["SKIP"]) or n != p + f + s:
        problems.append(
            f"Total line says {n} = PASS {p} + FAIL {f} + SKIP {s}, records say "
            f"PASS {counts['PASS']} FAIL {counts['FAIL']} SKIP {counts['SKIP']}"
        )
    if n < MIN_TOTAL:
        problems.append(f"Total {n} is below the plan-time {MIN_TOTAL}")
    unknown = [name for name in fails if name not in BASELINE_FAILS]
    if unknown:
        problems.append(f"FAIL record(s) outside the baseline pair: {unknown}")
    if exact and set(fails) != BASELINE_FAILS:
        problems.append(f"--exact-baseline: FAIL set {sorted(set(fails))} is not {sorted(BASELINE_FAILS)}")
    if clean:
        if fails:
            problems.append(f"--expect-clean: FAIL record(s) present: {fails}")
        missing = sorted(BASELINE_FAILS - set(passes))
        if missing:
            problems.append(f"--expect-clean: no [PASS] record for {missing}")
    if code is not None:
        expected = 1 if f else 0
        if code != expected:
            problems.append(f"exit {code}, but a suite with {f} FAIL(s) ends with exit {expected}")
    print(f"dispatch receipt: Total {n} PASS {p} FAIL {f} SKIP {s}; exit {code}; FAIL names {fails}")
    return problems


def _lines(data: bytes) -> list[bytes]:
    return data.splitlines(keepends=True)


def _index(lines: list[bytes], prefix: bytes) -> int | None:
    found = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    return found[0] if len(found) == 1 else None


def check_source(new: bytes, base: bytes) -> list[str]:
    problems: list[str] = []
    if not new.startswith(BOM):
        problems.append("the UTF-8 BOM is missing")
    bare_lf = new.count(b"\n") - new.count(b"\r\n")
    bare_cr = new.count(b"\r") - new.count(b"\r\n")
    last_crlf = new.endswith(b"\r\n")
    if bare_lf or bare_cr or not last_crlf:
        problems.append(f"line endings: {bare_lf} bare LF, {bare_cr} bare CR, last line CRLF={last_crlf}")
    nl, bl = _lines(new), _lines(base)
    ni, bi = _index(nl, ARM2_START), _index(bl, ARM2_START)
    nj, bj = _index(nl, ARM2_SUFFIX), _index(bl, ARM2_SUFFIX)
    if None in (ni, bi, nj, bj):
        problems.append(f"arm 2 anchors not found exactly once (comment new={ni} base={bi}; $r2 new={nj} base={bj})")
        return problems
    assert ni is not None and bi is not None and nj is not None and bj is not None
    if nl[:ni] != bl[:bi]:
        problems.append("a line before arm 2's comment differs from BASE")
    if nl[nj:] != bl[bj:]:
        problems.append("a line from '$r2 = Get-OutputDir' on differs from BASE")
    for marker in ASSERT_LINES:
        a = [ln for ln in nl if marker in ln]
        b = [ln for ln in bl if marker in ln]
        if len(a) != 1 or a != b:
            problems.append(f"the Write-TestResult line {marker.decode()!r} is not byte-equal to BASE")
    end = _index(nl, b"            " + ARM2_END)
    arm2 = b"".join(nl[ni : (end + 1) if end is not None else nj])
    if b"{{" in arm2:
        problems.append("arm 2 holds the literal '{{'")
    if b"            $phToken = " not in arm2:
        problems.append("arm 2 holds no $phToken assignment")
    base_region = set(bl[bi:bj])
    changed = [ln for ln in nl[ni:nj] if ln not in base_region]
    for ln in changed:
        text = ln.decode("utf-8", errors="replace").rstrip("\r\n")
        for name, pattern in CENSUS:
            if pattern.search(text):
                problems.append(f"changed line matches the {name} census pattern: {text.strip()!r}")
    print(f"dispatch source: {len(nl)} lines (BASE {len(bl)}); arm 2 at {ni + 1}-{nj}; {len(changed)} changed line(s)")
    for ln in changed:
        print("   +", ln.decode("utf-8", errors="replace").rstrip("\r\n"))
    return problems


#: The planned arm-2 edit (implementation-plan.md §The dispatch arm), applied to BASE in --selftest.
PLANNED_COMMENT = (
    b"            # 2. An uninstantiated placeholder. The token is assembled at run time from\r\n"
    b"            #    braces and its name, because instantiation rewrites any literal token in\r\n"
    b"            #    this file. The path sits in a fresh folder under the real temp folder, so\r\n"
    b"            #    creating it would genuinely SUCCEED: a pass proves the guard fired.\r\n"
)
PLANNED_ASSIGN = (
    b"            $phToken = ('{' * 2) + 'PROJECT_NAME' + ('}' * 2)\r\n"
    b"            $phBase = Join-Path ([System.IO.Path]::GetTempPath()) ('cli-dispatch-ph-' + [guid]::NewGuid().ToString('N'))\r\n"
    b"            $env:RECEIPTS_DIR = Join-Path (Join-Path $phBase $phToken) 'receipts'\r\n"
)
OLD_ASSIGN_PREFIXES = (b"            $phBase = ", b"            $env:RECEIPTS_DIR = Join-Path $phBase ")


def planned_edit(base: bytes) -> bytes:
    lines = _lines(base)
    i, j = _index(lines, ARM2_START), _index(lines, ARM2_SUFFIX)
    assert i is not None and j is not None, "arm 2 anchors not found in BASE"
    k = i
    while lines[k].lstrip().startswith(b"#"):
        k += 1
    body = [ln for ln in lines[k:j] if not ln.startswith(OLD_ASSIGN_PREFIXES)]
    assert len(body) == len(lines[k:j]) - 2, "BASE's two assignment lines not found"
    return b"".join(lines[:i]) + PLANNED_COMMENT + b"".join(body) + PLANNED_ASSIGN + b"".join(lines[j:])


def selftest(base_path: str, base_source: str) -> int:
    base = pathlib.Path(base_path).read_text(encoding="utf-8", errors="replace")
    failures: list[str] = []
    lines = base.replace("\r\n", "\n").split("\n")
    last_fail = max(n for n, ln in enumerate(lines) if RUN.match(ANSI.sub("", ln)) and "[FAIL]" in ln)
    added = lines[: last_fail + 1] + ["  [FAIL] an added failure (0s) - injected"] + lines[last_fail + 1 :]
    mismatched = [TOTAL.sub("  Total: 31 | PASS: 30 FAIL: 1 SKIP: 0", ANSI.sub("", ln)) for ln in lines]
    clean_lines = []
    for ln in lines:
        plain = ANSI.sub("", ln)
        if RUN.match(plain) and "[FAIL]" in plain:
            ln = plain.replace("[FAIL]", "[PASS]", 1)
        m = TOTAL.match(ANSI.sub("", ln))
        if m:
            n, p, f, s = (int(g) for g in m.groups())
            ln = f"  Total: {n} | PASS: {p + f} FAIL: 0 SKIP: {s}"
        clean_lines.append(ln)
    drop = [ln for ln in clean_lines if "[PASS] refusal created no placeholder dir" not in ln]
    drop = [TOTAL.sub(lambda m: f"  Total: {int(m.group(1)) - 1} | PASS: {int(m.group(2)) - 1} FAIL: 0 SKIP: {m.group(4)}", ln) for ln in drop]
    cases = (
        ("control: the baseline receipt with exit 1 (--exact-baseline)", base, "1", True, False, True),
        ("control: the baseline receipt with exit 1", base, "1", False, False, True),
        ("control: a clean copy with exit 0 (--expect-clean)", "\n".join(clean_lines), "0", False, True, True),
        ("the baseline receipt with exit 0", base, "0", False, False, False),
        ("an added [FAIL] record", "\n".join(added), "1", False, False, False),
        ("an empty receipt with exit 64", "", "64", False, False, False),
        ("a Total line that disagrees with the records", "\n".join(mismatched), "1", False, False, False),
        ("the baseline receipt under --expect-clean", base, "1", False, True, False),
        ("a clean copy missing one pair name (--expect-clean)", "\n".join(drop), "0", False, True, False),
    )
    for name, text, code, exact, clean, accept in cases:
        problems = check(text, code, exact, clean)
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} {name}: {'accepted' if ok else problems}")
        if ok != accept:
            failures.append(name)
    src = pathlib.Path(base_source).read_bytes()
    good = planned_edit(src)
    token = good.replace(b"$phToken = ('{' * 2) + 'PROJECT_NAME' + ('}' * 2)", b"$phToken = '{{PROJECT_NAME}}'", 1)
    lf = good.replace(b"'PROJECT_NAME' + ('}' * 2)\r\n", b"'PROJECT_NAME' + ('}' * 2)\n", 1)
    assertion = good.replace(b"(-not (Test-Path -LiteralPath $phBase))", b"($true)", 1)
    model = good.replace(b"a pass proves the guard fired.", b"a pass proves the guard fired, as on opus 5.", 1)
    no_bom = good[len(BOM):]
    source_cases = (
        ("control: BASE with the planned edit", good, True),
        ("the literal token", token, False),
        ("an LF line", lf, False),
        ("a changed assertion line", assertion, False),
        ("a comment naming a model family and a digit", model, False),
        ("no BOM", no_bom, False),
        ("BASE itself (arm 2 unedited, no $phToken)", src, False),
    )
    for name, data, accept in source_cases:
        if data == good and name != source_cases[0][0]:
            print("BAD ", name, ": the mutation did not apply")
            failures.append(name)
            continue
        problems = check_source(data, src)
        ok = not problems
        print(f"{'ok  ' if ok == accept else 'BAD '} source {name}: {'accepted' if ok else problems}")
        if ok != accept:
            failures.append(name)
    for failure in failures:
        print("SELFTEST FAIL:", failure)
    print(f"dispatch-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def _opt(argv: list[str], name: str, default: str) -> str:
    return argv[argv.index(name) + 1] if name in argv else default


def main(argv: list[str]) -> int:
    base_source = _opt(argv, "--base-source", BASE_SOURCE)
    if "--selftest" in argv:
        return selftest(_opt(argv, "--base", DEFAULT_BASE), base_source)
    if "--source" in argv:
        target = pathlib.Path(_opt(argv, "--file", DISPATCH_TEST))
        problems = check_source(target.read_bytes(), pathlib.Path(base_source).read_bytes())
    else:
        exact = "--exact-baseline" in argv
        clean = "--expect-clean" in argv
        args = [a for a in argv if a not in ("--exact-baseline", "--expect-clean")]
        if len(args) != 3 or args[0] != "--exit-file" or (exact and clean):
            print(__doc__)
            return 2
        exit_file, receipt = pathlib.Path(args[1]), pathlib.Path(args[2])
        problems = check(
            receipt.read_text(encoding="utf-8", errors="replace"),
            exit_file.read_text(encoding="utf-8", errors="replace"),
            exact,
            clean,
        )
    for problem in problems:
        print("FAIL", problem)
    print(f"dispatch-check: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
