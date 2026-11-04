"""Session 44 live MCP audit rule (implementation-plan.md §Verification Plan 5, D-186).

``audit-rule.py SUMMARY --head SHA`` decides whether an authoritative audit that exited 1 may
let the gate continue. It may only when the one thing wrong is ``YOUTUBE-CAPTIONS-IP-BLOCK``:
``transcript.compile`` found no fetched transcript but wrote a non-empty output file,
everything else matches the baseline, and a direct caption fetch through the product's adapter
really is blocked. That last check is the audit's own census proof (``run.ts``
``captionFetchBlocked``), which it runs only in container mode. Without it, a fetch bug would show
the same observation and pass.

The fetch proves a block exists. It doesn't prove the fetch path works or that compile handles
real transcripts, because neither ran. So a tolerated run is incomplete verification, not a clean
audit: the audit's own verdict and report stay non-pass, and the gate's last line says so. An
audit that exits 0 never reaches this rule.
Exit 0 = tolerated, 1 = refused, 2 = unreadable summary.

``--selftest`` proves the rule on built summaries. Run it from any directory.
"""

from __future__ import annotations

import argparse
import copy
import json
import pathlib
import re
import sys
from collections.abc import Callable

SCHEMA = "mcp-audit-summary.v1"
BLOCKED_STEP = "transcript.compile"
BLOCKED_DELTA = ("avkit_transcript.compile", "REGRESSION")
# The observer's blocked form (plan.ts:1176) with fileReport's one good form (plan.ts:133). Its other
# forms (missing, empty, outside the isolated root, no path) mean compile itself is wrong.
_VOLUME = r"[^;\\/:]+_vol\d+\.md [1-9]\d* B"
OBSERVATION = re.compile(
    rf"no transcript fetched \(transcripts_done 0, last_item_status (?:Pending|Failed)\); {_VOLUME}(?:; {_VOLUME})*"
)
FIXTURES = pathlib.Path(__file__).resolve().parents[4] / "mcp-server/scripts/audit/fixtures.ts"


def problems(summary: dict, head: str) -> list[str]:
    out: list[str] = []
    for key, expected in (("schema", SCHEMA), ("mode", "authoritative"), ("commit", head), ("exit_code", 1)):
        if summary.get(key) != expected:
            out.append(f"{key} is {summary.get(key)!r}, expected {expected!r}")
    if summary.get("isolation", {}).get("ok") is not True:
        out.append("isolation is not ok")
    if summary.get("cleanup", {}).get("ok") is not True:
        out.append("cleanup is not ok")

    discovery = summary.get("discovery", {})
    if discovery.get("status") != "pass":
        out.append(f"discovery status is {discovery.get('status')!r}")
    for key in ("findings", "new", "removed", "ghost"):
        if discovery.get(key, ["missing"]):
            out.append(f"discovery {key}: {discovery.get(key, 'missing')}")

    steps = summary.get("steps", [])
    non_pass = [step for step in steps if step.get("verdict") != "pass"]
    if [step.get("id") for step in non_pass] != [BLOCKED_STEP]:
        out.append(f"non-pass steps: {[(s.get('id'), s.get('verdict')) for s in non_pass]}")
    else:
        step = non_pass[0]
        if step.get("verdict") != "fail":
            out.append(f"{BLOCKED_STEP} verdict is {step.get('verdict')!r}")
        if step.get("reason") != "hollow":
            out.append(f"{BLOCKED_STEP} reason is {step.get('reason')!r}")
        if not OBSERVATION.fullmatch(str(step.get("error") or "")):
            out.append(f"{BLOCKED_STEP} isn't the blocked form with a real output file: {step.get('error')!r}")

    counts = summary.get("counts", {})
    if counts.get("total") != len(steps) or counts.get("pass") != len(steps) - 1:
        out.append(f"counts {counts} don't match {len(steps)} steps")

    changed = [(d.get("key"), d.get("delta")) for d in summary.get("deltas", []) if d.get("delta") != "UNCHANGED"]
    if changed != [BLOCKED_DELTA]:
        out.append(f"changed deltas: {changed}")
    return out


def caption_fetch_blocked() -> bool:
    """True only when the product's TranscriptAdapter is blocked for the fixture's first video."""
    import yt_dlp

    from avkit_core.domain.errors import TranscriptRetryableError
    from avkit_infra.transcript.adapter import TranscriptAdapter

    url = re.search(r'transcript_source_url:\s*"([^"]+)"', FIXTURES.read_text(encoding="utf-8")).group(1)
    with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True, "extract_flat": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    entries = info.get("entries") or [info]
    try:
        TranscriptAdapter().get_transcript(entries[0]["id"], ["en"])
    except TranscriptRetryableError:
        return True
    return False


def proof_problems(fetch_blocked: Callable[[], bool]) -> list[str]:
    try:
        if fetch_blocked():
            return []
        return ["a direct caption fetch isn't blocked, so this failure is a real regression"]
    except Exception as exc:
        return [f"a direct caption fetch failed another way: {exc!r}"]


def _observed(detail: str, done: int = 0, status: str = "Pending") -> str:
    return f"no transcript fetched (transcripts_done {done}, last_item_status {status}); {detail}"


def _sample() -> dict:
    return {
        "schema": SCHEMA,
        "mode": "authoritative",
        "commit": "abc",
        "exit_code": 1,
        "isolation": {"ok": True},
        "cleanup": {"ok": True},
        "discovery": {"status": "pass", "findings": [], "new": [], "removed": [], "ghost": []},
        "counts": {"pass": 1, "fail": 1, "skip_env": 0, "blocked": 0, "total": 2},
        "steps": [
            {"id": "capture.image", "verdict": "pass", "error": None},
            {"id": BLOCKED_STEP, "verdict": "fail", "reason": "hollow", "error": _observed("channel_vol1.md 37 B")},
        ],
        "deltas": [
            {"key": "avkit_capture.image", "delta": "UNCHANGED"},
            {"key": BLOCKED_DELTA[0], "delta": BLOCKED_DELTA[1]},
        ],
    }


def _extra_regression(s: dict) -> None:
    s["steps"][0].update(verdict="fail", error="MCP error -32000: Connection closed")
    s["deltas"][0]["delta"] = "REGRESSION"


def _set(path: tuple[str | int, ...], value: object):
    def mutate(s: dict) -> None:
        target = s
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return mutate


def _add_delta(delta: str):
    def mutate(s: dict) -> None:
        s["deltas"].append({"key": "avkit_x.y", "delta": delta})

    return mutate


def _error(*args, **kwargs):
    return _set(("steps", 1, "error"), _observed(*args, **kwargs))


TOLERATED = {
    "the item failed": _error("channel_vol1.md 37 B", status="Failed"),
    "two real volumes": _error("channel_vol1.md 37 B; channel_vol2.md 40 B"),
}

REFUSED = {
    "another step also failed": _extra_regression,
    "the same step failed differently": _set(("steps", 1, "error"), "MCP error -32000: Connection closed"),
    "the step failed as an MCP error": _set(("steps", 1, "reason"), "observable_failed"),
    "only the signature, with no observation": _set(("steps", 1, "error"), "no transcript fetched"),
    "the compile output is missing": _error("C:/Temp/root/compiled/channel_vol1.md missing", status="Failed"),
    "the compile output is empty": _error("C:/Temp/root/compiled/channel_vol1.md empty"),
    "the compile output is outside the root": _error("C:/Users/x/channel_vol1.md outside isolated root"),
    "compile returned an empty path": _error("no path"),
    "a zero-byte size": _error("channel_vol1.md 0 B"),
    "a second volume is missing": _error("channel_vol1.md 37 B; C:/Temp/root/channel_vol2.md missing"),
    "text follows the output": _error("channel_vol1.md 37 B; extra"),
    "transcripts were fetched": _error("channel_vol1.md 37 B", done=1),
    "an unexpected item status": _error("channel_vol1.md 37 B", status="Completed"),
    "a step is blocked": _set(("steps", 0, "verdict"), "blocked"),
    "the blocked step was blocked, not failed": _set(("steps", 1, "verdict"), "blocked"),
    "cleanup left something": _set(("cleanup", "ok"), False),
    "isolation failed": _set(("isolation", "ok"), False),
    "discovery failed": _set(("discovery", "status"), "fail"),
    "discovery found a ghost": _set(("discovery", "ghost"), ["avkit_x"]),
    "an action was removed": _add_delta("REMOVED"),
    "an action is new": _add_delta("NEW"),
    "summary from another commit": _set(("commit",), "def"),
    "not authoritative": _set(("mode",), "container"),
    "steps are missing": _set(("steps",), []),
    "the caption delta is absent": _set(("deltas", 1, "delta"), "UNCHANGED"),
}


def _raises() -> bool:
    raise RuntimeError("yt-dlp changed")


PROOF_REFUSED = {
    "the direct fetch isn't blocked": lambda: False,
    "the direct fetch failed another way": _raises,
}


def selftest() -> int:
    failures = 0
    base = problems(_sample(), "abc")
    print(f"PASS case 'only the caption block' -> {base or 'tolerated'}" if not base else f"FAIL base case: {base}")
    failures += bool(base)
    for name, mutate in TOLERATED.items():
        summary = copy.deepcopy(_sample())
        mutate(summary)
        found = problems(summary, "abc")
        print(f"{'FAIL' if found else 'PASS'} case '{name}' -> {found or 'tolerated'}")
        failures += bool(found)
    for name, mutate in REFUSED.items():
        summary = copy.deepcopy(_sample())
        mutate(summary)
        found = problems(summary, "abc")
        print(f"{'PASS' if found else 'FAIL'} refused '{name}' -> {found}")
        failures += not found
    blocked = proof_problems(lambda: True)
    print(f"{'FAIL' if blocked else 'PASS'} case 'the direct fetch is blocked' -> {blocked or 'tolerated'}")
    failures += bool(blocked)
    for name, fetch in PROOF_REFUSED.items():
        found = proof_problems(fetch)
        print(f"{'PASS' if found else 'FAIL'} refused '{name}' -> {found}")
        failures += not found
    total = 2 + len(TOLERATED) + len(REFUSED) + len(PROOF_REFUSED)
    print(f"audit-rule selftest: {total - failures} of {total} passed")
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", nargs="?", type=pathlib.Path)
    parser.add_argument("--head")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.summary is None or not args.head:
        parser.error("give a summary path and --head, or --selftest")
    try:
        summary = json.loads(args.summary.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"audit rule: can't read {args.summary}: {exc}")
        return 2
    # The summary comes first: the direct fetch is real YouTube traffic.
    found = problems(summary, args.head) or proof_problems(caption_fetch_blocked)
    for problem in found:
        print(f"audit rule refuses: {problem}")
    if found:
        return 1
    print(
        f"audit rule: only {BLOCKED_STEP} failed, with a real output file, and a direct caption fetch is blocked; "
        "tolerated as incomplete verification. Transcript is not verified end to end."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
