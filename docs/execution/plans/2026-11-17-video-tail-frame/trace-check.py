"""Session 93 trace check (AC-160.6, AC-160.9, AC-160.10; D-1169): read each load run's pytest
receipt against its grab_trace log.

    python trace-check.py --mode base  RECEIPT TRACE [RECEIPT TRACE ...]
    python trace-check.py --mode green RECEIPT TRACE [RECEIPT TRACE ...] [--min-packets 3]
    python trace-check.py --selftest

The watched signal is a bad END_GAP packet read: a `run kind=packet` record that exited
non-zero or timed out, or exited 0 with no packet time (`count=0`, the empty read), or with a
last packet time below the most common last time of the same clip and interval across every
trace given (the partial read). A failed test carries the signal when a record with its node
id has it.

Expected interval for a record with time T (`t=`): `--mode base` the open form
`S%` with S = max(0, T - 60 s), today's adapter line; `--mode green` the bounded form
`S%+D` with D = T + 60 s (D-1166). Both are written with the adapter's three-decimal seconds.

Exit codes, in this order of precedence:

- 2: an input problem: a missing file, a receipt with no pytest summary line, a FAILED count
  that does not match the summary, or a trace with no `armed` record.
- 1: `--mode green` and any bad packet read, any interval not in the bounded form, a run with
  fewer than --min-packets packet reads, or any failed test that carries the signal: the fix
  did not hold (Stop condition S7). `--mode base` and an interval not in the open form: the
  base is not the code the plan read (S2).
- 3: a failed test without the signal, in either mode (Session 90 RULE-3; Stop condition S8):
  it is listed with its trace records, so the row can rerun that test alone once under the
  same load and disclose both results. It is never counted as a pass.
- 0: `--mode base`: every failed test carries the signal (no failure at all is also 0; the
  counts are printed). `--mode green`: no failed test, no bad read, every interval bounded.

The output names tests and clip base names only, never a folder path.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

LOOKBACK_MS = 60_000
SUMMARY = re.compile(r"^=*\s*((?:\d+ [a-z]+(?:, )?)+) in [\d.]+s\b")
FAILED = re.compile(r"^(FAILED|ERROR) (\S+?)(?: - .*)?$")


def seek_text(ms: int) -> str:
    return f"{ms // 1000}.{ms % 1000:03d}"


def expected_arg(mode: str, t_ms: int) -> str:
    start = seek_text(max(0, t_ms - LOOKBACK_MS))
    if mode == "base":
        return f"{start}%"
    return f"{start}%+{seek_text(t_ms + LOOKBACK_MS)}"


def parse_record(line: str) -> tuple[str, dict[str, str]]:
    head, *rest = line.rstrip("\n").split("\t")
    fields: dict[str, str] = {}
    for item in rest:
        key, _, value = item.partition("=")
        fields[key] = value
    return head, fields


def read_trace(text: str) -> list[tuple[str, dict[str, str]]]:
    return [parse_record(line) for line in text.splitlines() if line.strip()]


def read_receipt(text: str) -> tuple[dict[str, int] | None, list[str]]:
    """(summary counts or None, failed node ids) from one pytest -q receipt."""
    counts: dict[str, int] | None = None
    failed: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        match = SUMMARY.match(stripped)
        if match:
            counts = {}
            for part in match.group(1).split(", "):
                number, word = part.split(" ", 1)
                counts[word.rstrip("s") if word != "passed" else word] = int(number)
        hit = FAILED.match(stripped)
        if hit:
            failed.append(hit.group(2))
    return counts, failed


def modal_last(records: list[tuple[str, dict[str, str]]]) -> dict[tuple[str, str], int]:
    seen: dict[tuple[str, str], collections.Counter[int]] = collections.defaultdict(
        collections.Counter
    )
    for head, fields in records:
        if head == "run" and fields.get("kind") == "packet" and fields.get("rc") == "0":
            last = fields.get("last", "None")
            if last not in ("None", "-"):
                seen[(fields.get("clip", "-"), fields.get("arg", "-"))][int(last)] += 1
    return {key: counter.most_common(1)[0][0] for key, counter in seen.items()}


def bad_reason(fields: dict[str, str], modal: dict[tuple[str, str], int]) -> str | None:
    if fields.get("rc") != "0":
        return f"packet read rc {fields.get('rc')}"
    if fields.get("count") == "0" or fields.get("last") in ("None", "-"):
        return "empty packet read"
    key = (fields.get("clip", "-"), fields.get("arg", "-"))
    if key in modal and int(fields["last"]) < modal[key]:
        return f"partial packet read: last {fields['last']} below {modal[key]}"
    return None


def check(mode: str, pairs: list[tuple[str, str]], min_packets: int) -> tuple[int, list[str]]:
    """(exit code, report lines) over (receipt text, trace text) pairs."""
    report: list[str] = []
    traces = [read_trace(trace) for _, trace in pairs]
    modal = modal_last([rec for trace in traces for rec in trace])
    input_problem = fix_failed = no_signal = False
    totals = collections.Counter()
    for index, ((receipt_text, _), records) in enumerate(zip(pairs, traces, strict=True), 1):
        counts, failed = read_receipt(receipt_text)
        if counts is None:
            report.append(f"run {index}: INPUT no pytest summary line")
            input_problem = True
            continue
        if len(failed) != counts.get("failed", 0) + counts.get("error", 0):
            report.append(f"run {index}: INPUT {len(failed)} FAILED/ERROR lines, summary {counts}")
            input_problem = True
        if not any(head == "armed" for head, _ in records):
            report.append(f"run {index}: INPUT the trace has no armed record")
            input_problem = True
        packets = [f for head, f in records if head == "run" and f.get("kind") == "packet"]
        bad_nodes: dict[str, list[str]] = collections.defaultdict(list)
        wrong_arg = 0
        for fields in packets:
            reason = bad_reason(fields, modal)
            if reason:
                bad_nodes[fields.get("node", "-")].append(
                    f"{reason} ({fields.get('clip')} t={fields.get('t')} arg={fields.get('arg')}"
                    f" stderr={fields.get('stderr')})"
                )
            t_ms = fields.get("t", "-")
            if not t_ms.isdigit() or fields.get("arg") != expected_arg(mode, int(t_ms)):
                wrong_arg += 1
        bad = sum(len(v) for v in bad_nodes.values())
        totals.update(packets=len(packets), bad=bad, failed=len(failed), wrong_arg=wrong_arg)
        report.append(
            f"run {index}: summary {counts}; packet reads {len(packets)}, bad {bad},"
            f" interval not in the {mode} form {wrong_arg}"
        )
        for node, reasons in sorted(bad_nodes.items()):
            for reason in reasons:
                report.append(f"  signal {node}: {reason}")
        for node in failed:
            if node in bad_nodes:
                report.append(f"  FAILED WITH SIGNAL {node}")
                if mode == "green":
                    fix_failed = True
            else:
                no_signal = True
                report.append(
                    f"  FAILED WITHOUT SIGNAL {node} (RULE-3: rerun alone once, disclose)"
                )
                for head, fields in records:
                    if fields.get("node") == node and head != "armed":
                        report.append(
                            f"    {head} {fields.get('kind', 'call')} {fields.get('clip')}"
                            f" t={fields.get('t')} arg={fields.get('arg', fields.get('seek'))}"
                            f" rc={fields.get('rc', '-')} bytes={fields.get('bytes')}"
                            f" last={fields.get('last', '-')}"
                            f" duration={fields.get('duration', '-')}"
                        )
        if wrong_arg:
            fix_failed = True
        if mode == "green" and (bad or len(packets) < min_packets):
            fix_failed = True
    report.append(f"totals: {dict(totals)}; modal last per clip and interval: {modal}")
    if input_problem:
        return 2, report + ["RESULT: input problem (exit 2)"]
    if fix_failed:
        return 1, report + [f"RESULT: {mode} expectation not met (exit 1)"]
    if no_signal:
        return 3, report + ["RESULT: a failure without the signal (exit 3, RULE-3)"]
    return 0, report + [f"RESULT: {mode} expectation met (exit 0)"]


def selftest() -> int:
    failures: list[str] = []

    def ok(name: str, cond: bool) -> None:
        print(f"{'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            failures.append(name)

    ok("base form at 2999", expected_arg("base", 2999) == "0.000%")
    ok("green form at 2999", expected_arg("green", 2999) == "0.000%+62.999")
    ok("green form at 3200", expected_arg("green", 3200) == "0.000%+63.200")
    ok("green form at 7200021", expected_arg("green", 7_200_021) == "7140.021%+7260.021")
    ok("base form at 7200021", expected_arg("base", 7_200_021) == "7140.021%")
    ok("green form at 60000", expected_arg("green", 60_000) == "0.000%+120.000")

    node_a = "tests/integration/test_video_real_ffmpeg.py::test_a"
    node_b = "tests/integration/test_video_real_ffmpeg.py::test_b[1.05]"

    def pk(node: str, arg: str, rc: str, count: str, last: str, t: str = "2999") -> str:
        return (
            f"run\tnode={node}\tkind=packet\tclip=counter.mp4\tt={t}\targ={arg}\trc={rc}"
            f"\tcount={count}\tlast={last}\tbytes=9\tduration=-\tsecs=0.1\tstderr=''"
        )

    def armed(node: str) -> str:
        return f"armed\tnode={node}"

    passed = "...\n2 passed in 3.10s\n"
    one_failed = f"F.\nFAILED {node_a} - AssertionError: x\n1 failed, 1 passed in 3.10s\n"
    full = pk(node_a, "0.000%", "0", "75", "2960")
    empty = pk(node_a, "0.000%", "0", "0", "None")
    partial = pk(node_a, "0.000%", "0", "40", "1560")
    good_b = pk(node_b, "0.000%", "0", "75", "2960")
    trace_full = "\n".join([armed(node_a), full, armed(node_b), good_b])
    trace_empty = "\n".join([armed(node_a), empty, armed(node_b), good_b])
    trace_partial = "\n".join([armed(node_a), partial, armed(node_b), good_b, full])

    ok(
        "base: a failure with an empty read passes",
        check("base", [(one_failed, trace_empty)], 1)[0] == 0,
    )
    ok(
        "base: a failure with a partial read passes",
        check("base", [(one_failed, trace_partial)], 1)[0] == 0,
    )
    ok("base: no failure passes", check("base", [(passed, trace_full)], 1)[0] == 0)
    ok(
        "base: a failure without the signal is exit 3",
        check("base", [(one_failed, trace_full)], 1)[0] == 3,
    )
    ok(
        "base: a bounded interval at base is exit 1",
        check("base", [(passed, trace_full.replace("0.000%", "0.000%+62.999"))], 1)[0] == 1,
    )

    g = lambda text: text.replace("arg=0.000%", "arg=0.000%+62.999")  # noqa: E731
    ok("green: clean passes", check("green", [(passed, g(trace_full))], 2)[0] == 0)
    ok("green: an open interval is exit 1", check("green", [(passed, trace_full)], 2)[0] == 1)
    ok(
        "green: a bad read with no failure is exit 1",
        check("green", [(passed, g(trace_empty))], 2)[0] == 1,
    )
    ok(
        "green: a failure with the signal is exit 1",
        check("green", [(one_failed, g(trace_empty))], 2)[0] == 1,
    )
    ok(
        "green: a failure without the signal is exit 3",
        check("green", [(one_failed, g(trace_full))], 2)[0] == 3,
    )
    ok(
        "green: too few packet reads is exit 1",
        check("green", [(passed, g(trace_full))], 3)[0] == 1,
    )
    rc_bad = g(trace_full.replace("rc=0\tcount=75", "rc=1\tcount=75", 1))
    ok("green: a non-zero packet read is bad", check("green", [(passed, rc_bad)], 2)[0] == 1)
    ok("no summary line is exit 2", check("base", [("F\n", trace_full)], 1)[0] == 2)
    ok(
        "a FAILED count mismatch is exit 2",
        check("base", [("1 failed in 1.0s\n", trace_full)], 1)[0] == 2,
    )
    ok("a trace with no armed record is exit 2", check("base", [(passed, full)], 1)[0] == 2)
    counts, failed = read_receipt(f"ERROR {node_b}\n1 error, 3 passed, 1 skipped in 2.00s\n")
    ok(
        "an error line counts",
        failed == [node_b] and counts == {"error": 1, "passed": 3, "skipped": 1},
    )
    two = [(passed, g(trace_full)), (passed, g(trace_full))]
    ok("two clean green runs pass", check("green", two, 2)[0] == 0)
    print(f"trace-check selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if argv == ["--selftest"]:
        return selftest()
    if len(argv) < 4 or argv[0] != "--mode" or argv[1] not in ("base", "green"):
        print(__doc__)
        return 2
    mode, rest = argv[1], argv[2:]
    min_packets = 3
    if "--min-packets" in rest:
        at = rest.index("--min-packets")
        min_packets = int(rest[at + 1])
        rest = rest[:at] + rest[at + 2 :]
    if len(rest) % 2:
        print("give RECEIPT TRACE pairs")
        return 2
    pairs: list[tuple[str, str]] = []
    for receipt, trace in zip(rest[0::2], rest[1::2], strict=True):
        paths = (Path(receipt), Path(trace))
        missing = [p.name for p in paths if not p.is_file()]
        if missing:
            print(f"INPUT missing: {missing}")
            return 2
        pairs.append(tuple(p.read_bytes().decode("utf-8", "replace") for p in paths))  # type: ignore[arg-type]
    code, report = check(mode, pairs, min_packets)
    print("\n".join(report))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
