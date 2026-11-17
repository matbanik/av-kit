"""Tally a ready-gap-probe JSONL receipt (Session 82, MEU-153 measurement rows).

usage: gap-tally.py <file.jsonl> --runs N [--all-ok] [--label TEXT]
       gap-tally.py --selftest

Prints one line `gap-tally <label> {...}` with the run count, the first-request outcomes, the
refused count and the slowest and fastest accept-after-READY times. Exit 1 when the receipt is
missing, the record count is not N, a record carries `error`, or (with --all-ok) any first
request is not `http 200`. Without --all-ok a refused first request is a measurement, not a
failure. Reads only the receipt; writes nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def tally(records: list[dict[str, Any]]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    for record in records:
        key = "error" if "error" in record else str(record.get("first"))
        outcomes[key] = outcomes.get(key, 0) + 1
    accepts = [
        r["accept_after_ready_ms"]
        for r in records
        if isinstance(r.get("accept_after_ready_ms"), int)
    ]
    return {
        "runs": len(records),
        "outcomes": outcomes,
        "refused": sum(1 for r in records if "ECONNREFUSED" in str(r.get("first", ""))),
        "errors": sum(1 for r in records if "error" in r),
        "accept_after_ready_ms": {"min": min(accepts), "max": max(accepts)} if accepts else None,
    }


def verdict(records: list[dict[str, Any]], runs: int, all_ok: bool) -> list[str]:
    problems: list[str] = []
    if len(records) != runs:
        problems.append(f"expected {runs} records, found {len(records)}")
    if any("error" in r for r in records):
        problems.append("a record carries error")
    if all_ok and any(r.get("first") != "http 200" for r in records):
        problems.append("a first request was not http 200")
    return problems


def read(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def selftest() -> int:
    ok = {"first": "http 200", "accept_after_ready_ms": 3}
    refused = {"first": "ECONNREFUSED", "accept_after_ready_ms": 20}
    cases = [
        (verdict([ok, ok], 2, True), []),
        (verdict([ok, refused], 2, False), []),
        (verdict([ok, refused], 2, True), ["a first request was not http 200"]),
        (verdict([ok], 2, False), ["expected 2 records, found 1"]),
        (verdict([ok, {"error": "no READY in 60 s"}], 2, False), ["a record carries error"]),
    ]
    bad = [i for i, (got, want) in enumerate(cases) if got != want]
    counts = tally([ok, refused])
    if counts["refused"] != 1 or counts["accept_after_ready_ms"] != {"min": 3, "max": 20}:
        bad.append(len(cases))
    print("gap-tally selftest:", "ok" if not bad else f"failed cases {bad}")
    return 1 if bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", nargs="?", type=Path)
    parser.add_argument("--runs", type=int)
    parser.add_argument("--all-ok", action="store_true")
    parser.add_argument("--label", default="")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.receipt is None or args.runs is None:
        parser.error("receipt and --runs are required")
    if not args.receipt.is_file():
        print(f"gap-tally {args.label} missing receipt {args.receipt}")
        return 1
    records = read(args.receipt)
    problems = verdict(records, args.runs, args.all_ok)
    print(f"gap-tally {args.label} " + json.dumps({**tally(records), "problems": problems}))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
