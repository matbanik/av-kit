"""Session 92 checks on the authoritative audit's outputs (AUDIT_RUN, BASELINE_RECORD).

    summary  --summary <mcp-audit-summary.json> --pending <key>... --head <sha>
        Row 6 (no update) and row 8 (update): exit 0, mode authoritative, cleanup ok with no
        residuals, discovery pass with no findings, removed or ghost key, every step a pass,
        the NEW deltas exactly the pending keys, every other delta UNCHANGED, commit == HEAD.
    baseline --old <row-0 copy> --new <baseline-snapshot.json> --pending <key>... --head <sha>
        Row 8: compared by tool.action key, the new baseline adds exactly the pending keys, all
        status pass with no issue field, keeps every old entry unchanged, removes none, has
        findings [], keeps schema and mode, records HEAD and a new recorded_at.
    --selftest
        Both checks on fixtures.

Exit 0 when every check passes, 1 when one fails, 2 on a usage or input error.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path


def key(entry: dict) -> str:
    return f"{entry.get('tool')}.{entry.get('action')}"


def summary_problems(s: dict, pending: list[str], head: str) -> list[str]:
    p: list[str] = []
    if s.get("schema") != "mcp-audit-summary.v1":
        p.append(f"schema is {s.get('schema')!r}")
    if s.get("exit_code") != 0:
        p.append(f"exit_code is {s.get('exit_code')!r}, not 0")
    if s.get("mode") != "authoritative":
        p.append(f"mode is {s.get('mode')!r}, not authoritative")
    if s.get("commit") != head:
        p.append(f"commit {s.get('commit')!r} is not HEAD {head}")
    cleanup = s.get("cleanup") or {}
    if cleanup.get("ok") is not True or cleanup.get("residuals"):
        p.append(
            f"cleanup not clean: ok={cleanup.get('ok')!r} residuals={cleanup.get('residuals')!r}"
        )
    disc = s.get("discovery") or {}
    if disc.get("status") != "pass":
        p.append(f"discovery status is {disc.get('status')!r}")
    for field in ("findings", "removed", "ghost"):
        if disc.get(field):
            p.append(f"discovery {field}: {disc.get(field)!r}")
    failed = [st.get("id") for st in s.get("steps") or [] if st.get("verdict") != "pass"]
    if failed:
        p.append(f"steps not pass: {failed}")
    if not s.get("steps"):
        p.append("no steps recorded")
    deltas = s.get("deltas") or []
    new = sorted(d["key"] for d in deltas if d.get("delta") == "NEW")
    if new != sorted(pending):
        p.append(f"NEW deltas {new} are not the pending keys {sorted(pending)}")
    other = [
        f"{d.get('key')}={d.get('delta')}"
        for d in deltas
        if d.get("delta") not in ("NEW", "UNCHANGED")
    ]
    if other:
        p.append(f"deltas other than NEW or UNCHANGED: {other}")
    return p


def baseline_problems(old: dict, new: dict, pending: list[str], head: str) -> list[str]:
    p: list[str] = []
    for field in ("schema", "mode"):
        if new.get(field) != old.get(field):
            p.append(f"{field} changed: {old.get(field)!r} -> {new.get(field)!r}")
    if new.get("mode") != "authoritative":
        p.append(f"mode is {new.get('mode')!r}")
    if new.get("recorded_commit") != head:
        p.append(f"recorded_commit {new.get('recorded_commit')!r} is not HEAD {head}")
    if new.get("recorded_at") == old.get("recorded_at"):
        p.append("recorded_at is unchanged")
    if new.get("findings") != []:
        p.append(f"findings is {new.get('findings')!r}, not []")
    old_by = {key(e): e for e in old.get("entries") or []}
    new_by = {key(e): e for e in new.get("entries") or []}
    if len(new_by) != len(new.get("entries") or []):
        p.append("the new baseline repeats a key")
    added = sorted(set(new_by) - set(old_by))
    removed = sorted(set(old_by) - set(new_by))
    if added != sorted(pending):
        p.append(f"added keys {added} are not the pending keys {sorted(pending)}")
    if removed:
        p.append(f"removed keys: {removed}")
    changed = sorted(k for k in set(old_by) & set(new_by) if old_by[k] != new_by[k])
    if changed:
        p.append(f"changed entries: {changed}")
    for k in added:
        if new_by[k] != {
            "tool": new_by[k].get("tool"),
            "action": new_by[k].get("action"),
            "status": "pass",
        }:
            p.append(f"{k} is not a plain pass entry: {new_by[k]!r}")
    return p


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def report(problems: list[str], label: str) -> int:
    for line in problems:
        print(f"FAIL {line}")
    print(
        f"baseline-diff {label}: ok"
        if not problems
        else f"baseline-diff {label}: {len(problems)} problem(s)"
    )
    return 0 if not problems else 1


def selftest() -> int:
    head = "a" * 40
    pending = ["avkit_capture.crop", "avkit_convert.probe"]
    summary = {
        "schema": "mcp-audit-summary.v1",
        "exit_code": 0,
        "mode": "authoritative",
        "commit": head,
        "cleanup": {"ok": True, "residuals": [], "backend_exited": True, "root_removed": True},
        "discovery": {"status": "pass", "findings": [], "new": pending, "removed": [], "ghost": []},
        "steps": [{"id": "s1", "verdict": "pass"}],
        "deltas": [
            {"key": "avkit_health.check", "delta": "UNCHANGED"},
            {"key": "avkit_capture.crop", "delta": "NEW"},
            {"key": "avkit_convert.probe", "delta": "NEW"},
        ],
    }
    old = {
        "schema": "mcp-audit-baseline.v1",
        "recorded_commit": "b" * 40,
        "mode": "authoritative",
        "recorded_at": "2026-10-16T00:00:00Z",
        "entries": [{"tool": "avkit_health", "action": "check", "status": "pass"}],
        "findings": [],
    }
    new = copy.deepcopy(old)
    new.update(recorded_commit=head, recorded_at="2026-11-18T00:00:00Z")
    new["entries"] += [
        {"tool": "avkit_capture", "action": "crop", "status": "pass"},
        {"tool": "avkit_convert", "action": "probe", "status": "pass"},
    ]

    def s_with(**kw) -> dict:
        x = copy.deepcopy(summary)
        for k, v in kw.items():
            x[k] = v
        return x

    def b_with(fn) -> dict:
        x = copy.deepcopy(new)
        fn(x)
        return x

    cases = [
        ("summary positive control", summary_problems(summary, pending, head), 0),
        ("summary exit 1", summary_problems(s_with(exit_code=1), pending, head), 1),
        ("summary container mode", summary_problems(s_with(mode="container"), pending, head), 1),
        ("summary stale commit", summary_problems(s_with(commit="c" * 40), pending, head), 1),
        (
            "summary residual",
            summary_problems(s_with(cleanup={"ok": True, "residuals": ["pid 1"]}), pending, head),
            1,
        ),
        (
            "summary a failing step",
            summary_problems(s_with(steps=[{"id": "s1", "verdict": "fail"}]), pending, head),
            1,
        ),
        (
            "summary a regression",
            summary_problems(
                s_with(
                    deltas=[
                        *summary["deltas"][1:],
                        {"key": "avkit_health.check", "delta": "REGRESSION"},
                    ]
                ),
                pending,
                head,
            ),
            1,
        ),
        ("summary an extra NEW", summary_problems(summary, pending[:1], head), 1),
        ("baseline positive control", baseline_problems(old, new, pending, head), 0),
        (
            "baseline one pending missing",
            baseline_problems(old, new, [*pending, "avkit_capture.sheet"], head),
            1,
        ),
        (
            "baseline an old entry changed",
            baseline_problems(
                old, b_with(lambda x: x["entries"][0].update(status="fail")), pending, head
            ),
            1,
        ),
        (
            "baseline an old entry removed",
            baseline_problems(old, b_with(lambda x: x["entries"].pop(0)), pending, head),
            1,
        ),
        (
            "baseline a finding",
            baseline_problems(
                old, b_with(lambda x: x.update(findings=[{"code": "x"}])), pending, head
            ),
            1,
        ),
        (
            "baseline an added entry with an issue",
            baseline_problems(
                old, b_with(lambda x: x["entries"][-1].update(issue="X")), pending, head
            ),
            1,
        ),
        (
            "baseline stale recorded_at",
            baseline_problems(
                old, b_with(lambda x: x.update(recorded_at=old["recorded_at"])), pending, head
            ),
            1,
        ),
        ("baseline stale commit", baseline_problems(old, new, pending, "c" * 40), 1),
    ]
    failed = 0
    for label, problems, want in cases:
        ok = len(problems) == want
        failed += 0 if ok else 1
        print(
            f"{'PASS' if ok else 'FAIL'} selftest {label}: {len(problems)} problem(s), want {want}"
        )
    print(
        "baseline-diff selftest: ok" if failed == 0 else f"baseline-diff selftest: {failed} failed"
    )
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", nargs="?", choices=["summary", "baseline"])
    parser.add_argument("--summary")
    parser.add_argument("--old")
    parser.add_argument("--new")
    parser.add_argument("--pending", nargs="+", default=[])
    parser.add_argument("--head")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if args.command == "summary" and args.summary and args.head and args.pending:
            return report(summary_problems(load(args.summary), args.pending, args.head), "summary")
        if args.command == "baseline" and args.old and args.new and args.head and args.pending:
            return report(
                baseline_problems(load(args.old), load(args.new), args.pending, args.head),
                "baseline",
            )
    except (OSError, ValueError, KeyError) as exc:
        print(f"FAIL {type(exc).__name__}: {exc}")
        return 2
    parser.print_usage()
    return 2


if __name__ == "__main__":
    sys.exit(main())
