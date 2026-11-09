"""Session 57 live MCP audit rule (implementation-plan.md §Verification Plan 5, D-186, D-464).

A copy of Session 44's rule, rewritten for the shape MEU-116 gives a caption block.
``audit-rule.py SUMMARY --head SHA`` decides whether an authoritative audit that exited 1 may
let the gate continue. It may only when the one thing wrong is ``YOUTUBE-CAPTIONS-IP-BLOCK``.
Since MEU-116 a block that outlasts its retries pauses the job with the block's message and
leaves the item Pending (services transcript ``_fetch_item``, ``_pause_parent``), so the audit
sees one root step fail and the transcript chain after it blocked:

* the root is ``transcript.resume`` (the usual case) or ``transcript.start`` (when the block
  paused the job before start's poll saw Processing). Its verdict is fail, reason hollow,
  is_error false, its error is exactly the block message and its observable is the Paused form;
* every step that depends on the root, and only those, is blocked by its own dependency
  (``CHAIN``, pinned from plan.ts and checked against it on every run);
* the changed deltas are exactly REGRESSION for the seven transcript actions in that chain;
* everything else matches the baseline, and a direct caption fetch through the product's
  adapter really is blocked. That last check is the audit's own census proof (``run.ts``
  ``captionFetchBlocked``), which it runs only in container mode. Without it, a fetch bug that
  raised the retryable error would show the same observation and pass.

Session 44's shape (only ``transcript.compile`` failed) can't occur with MEU-116 in the build, so
this rule refuses it. The fetch proves a block exists. It doesn't prove the fetch path works or
that compile handles real transcripts, because neither ran. So a tolerated run is incomplete
verification, not a clean audit: the audit's own verdict and report stay non-pass, and the
gate's last line says so. An audit that exits 0 never reaches this rule.
Exit 0 = tolerated, 1 = refused, 2 = unreadable summary.

``--selftest`` proves the rule on built summaries and checks ``CHAIN`` and ``BLOCK_MESSAGE``
against the source. Run it from any directory.
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
ROOT = pathlib.Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "mcp-server/scripts/audit/fixtures.ts"
PLAN_TS = ROOT / "mcp-server/scripts/audit/plan.ts"
# domain/transcript.py failure_message(TranscriptFailureCause.blocked); source_problems checks it.
BLOCK_MESSAGE = (
    "YouTube is blocking caption requests from this network. "
    "Try again later or from another network, then Resume."
)
# Each step's one dependency in plan.ts TRANSCRIPT_STEPS, from start to compile.
CHAIN = {
    "transcript.pause": "transcript.start",
    "transcript.resume": "transcript.pause",
    "transcript.pause.again": "transcript.resume",
    "transcript.stop": "transcript.pause.again",
    "transcript.requeue": "transcript.stop",
    "transcript.requeue.conflict": "transcript.requeue",
    "transcript.retry.conflict": "transcript.requeue",
    "transcript.start.again": "transcript.requeue",
    "transcript.pause.third": "transcript.start.again",
    "transcript.stop.again": "transcript.pause.third",
    "transcript.retry": "transcript.stop.again",
    "transcript.compile": "transcript.retry",
}
# transcriptControl's and transcriptResume's details (plan.ts) for a job the block paused.
ROOT_OBSERVABLE = {
    "transcript.start": "REST job Paused (want Processing)",
    "transcript.resume": "REST job Paused (want Processing), transcripts_done 0, last_item_status Pending",
}
CHANGED = sorted(
    (f"avkit_transcript.{action}", "REGRESSION")
    for action in ("start", "pause", "resume", "stop", "requeue", "retry", "compile")
)


def dependents(root: str, edges: dict[str, str]) -> set[str]:
    out: set[str] = set()
    grew = True
    while grew:
        grew = False
        for step, dep in edges.items():
            if (dep == root or dep in out) and step not in out:
                out.add(step)
                grew = True
    return out


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
    roots = [step for step in steps if step.get("verdict") not in ("pass", "blocked")]
    blocked = {step.get("id"): step for step in steps if step.get("verdict") == "blocked"}
    expected_blocked: set[str] = set()
    if [step.get("id") for step in roots] not in ([r] for r in ROOT_OBSERVABLE):
        out.append(f"failed steps: {[(s.get('id'), s.get('verdict')) for s in roots]}")
    else:
        step = roots[0]
        name = step["id"]
        expected_blocked = dependents(name, CHAIN)
        for key, expected in (("verdict", "fail"), ("reason", "hollow"), ("is_error", False)):
            if step.get(key) != expected:
                out.append(f"{name} {key} is {step.get(key)!r}, expected {expected!r}")
        if step.get("error") != BLOCK_MESSAGE:
            out.append(f"{name} error isn't the block message: {step.get('error')!r}")
        if step.get("observable") != ROOT_OBSERVABLE[name]:
            out.append(f"{name} isn't the blocked-pause form: {step.get('observable')!r}")
    if set(blocked) != expected_blocked:
        out.append(f"blocked steps {sorted(map(str, blocked))} aren't the chain {sorted(expected_blocked)}")
    for name in sorted(set(blocked) & expected_blocked):
        record, by = blocked[name], CHAIN[name]
        seen = (record.get("blocked_by"), record.get("observable"), record.get("reason"), record.get("error"))
        if seen != (by, f"{by} did not pass", None, None):
            out.append(f"{name} isn't blocked by {by}: {seen}")

    counts = summary.get("counts", {})
    want = {
        "total": len(steps),
        "fail": 1,
        "blocked": len(expected_blocked),
        "skip_env": 0,
        "pass": len(steps) - 1 - len(expected_blocked),
    }
    if any(counts.get(key) != value for key, value in want.items()):
        out.append(f"counts {counts} don't match {want}")

    changed = sorted((d.get("key"), d.get("delta")) for d in summary.get("deltas", []) if d.get("delta") != "UNCHANGED")
    if changed != CHANGED:
        out.append(f"changed deltas: {changed}")
    return out


def chain_problems(plan_text: str) -> list[str]:
    """CHAIN against plan.ts: each step's dependency, and no other step depending on the chain."""
    start = plan_text.find("const TRANSCRIPT_STEPS")
    end = plan_text.find("// ----", start)
    if start < 0 or end < 0:
        return ["plan.ts has no TRANSCRIPT_STEPS block"]
    block = plan_text[start:end]
    edges: dict[str, list[str]] = {}
    patterns = (
        r'transcript(?:Control|Resume|Transition)\(\s*"([^"]+)"(?:,\s*"[^"]+")?,\s*\[([^\]]*)\]',
        r'id:\s*"([^"]+)",(?:(?!\bid:)[\s\S])*?depends_on:\s*\[([^\]]*)\]',
    )
    for pattern in patterns:
        for match in re.finditer(pattern, block):
            edges[match.group(1)] = re.findall(r'"([^"]+)"', match.group(2))
    out = [
        f"plan.ts {name} depends on {edges.get(name)}, expected [{dep!r}]"
        for name, dep in CHAIN.items()
        if edges.get(name) != [dep]
    ]
    chain = set(CHAIN) | {"transcript.start"}
    extra = sorted(name for name, deps in edges.items() if name not in CHAIN and chain & set(deps))
    outside = plan_text[:start] + plan_text[end:]
    extra += sorted(set(re.findall(r'depends_on:\s*\[[^\]]*"(transcript\.[^"]+)"', outside)))
    if extra:
        out.append(f"plan.ts has other steps on the transcript chain: {extra}")
    return out


def source_problems() -> list[str]:
    from avkit_core.domain.transcript import TranscriptFailureCause, failure_message

    out = chain_problems(PLAN_TS.read_text(encoding="utf-8"))
    if failure_message(TranscriptFailureCause.blocked) != BLOCK_MESSAGE:
        out.append("BLOCK_MESSAGE isn't failure_message(TranscriptFailureCause.blocked)")
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


def _pass(step_id: str) -> dict:
    return {"id": step_id, "verdict": "pass", "reason": None, "is_error": False, "observable": "ok", "error": None}


def _sample(root: str = "transcript.resume") -> dict:
    ids = ["capture.image", "transcript.add", "transcript.reorder", "transcript.start", *CHAIN, "transcript.remove"]
    chain = dependents(root, CHAIN)
    steps = []
    for step_id in ids:
        if step_id == root:
            steps.append(
                {
                    "id": root,
                    "verdict": "fail",
                    "reason": "hollow",
                    "is_error": False,
                    "observable": ROOT_OBSERVABLE[root],
                    "error": BLOCK_MESSAGE,
                }
            )
        elif step_id in chain:
            by = CHAIN[step_id]
            steps.append(
                {
                    "id": step_id,
                    "verdict": "blocked",
                    "reason": None,
                    "is_error": None,
                    "observable": f"{by} did not pass",
                    "error": None,
                    "blocked_by": by,
                }
            )
        else:
            steps.append(_pass(step_id))
    deltas = [{"key": "avkit_capture.image", "delta": "UNCHANGED"}, {"key": "avkit_transcript.add", "delta": "UNCHANGED"}]
    deltas += [{"key": key, "delta": delta} for key, delta in CHANGED]
    return {
        "schema": SCHEMA,
        "mode": "authoritative",
        "commit": "abc",
        "exit_code": 1,
        "isolation": {"ok": True},
        "cleanup": {"ok": True},
        "discovery": {"status": "pass", "findings": [], "new": [], "removed": [], "ghost": []},
        "counts": {
            "pass": len(steps) - 1 - len(chain),
            "fail": 1,
            "skip_env": 0,
            "blocked": len(chain),
            "total": len(steps),
        },
        "steps": steps,
        "deltas": deltas,
    }


def _index(s: dict, step_id: str) -> int:
    return next(i for i, step in enumerate(s["steps"]) if step["id"] == step_id)


def _step(step_id: str, **fields: object):
    def mutate(s: dict) -> None:
        s["steps"][_index(s, step_id)].update(fields)

    return mutate


def _set(path: tuple[str | int, ...], value: object):
    def mutate(s: dict) -> None:
        target = s
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value

    return mutate


def _delta(key: str, delta: str):
    def mutate(s: dict) -> None:
        for entry in s["deltas"]:
            if entry["key"] == key:
                entry["delta"] = delta
                return
        s["deltas"].append({"key": key, "delta": delta})

    return mutate


def _both(*mutations):
    def mutate(s: dict) -> None:
        for m in mutations:
            m(s)

    return mutate


def _session44_shape(s: dict) -> None:
    """RC1's tolerated summary: the chain ran and only compile failed, hollow, with a real file."""
    for i, step in enumerate(s["steps"]):
        if step["id"].startswith("transcript."):
            s["steps"][i] = _pass(step["id"])
    s["steps"][_index(s, "transcript.compile")].update(
        verdict="fail",
        reason="hollow",
        error="no transcript fetched (transcripts_done 0, last_item_status Pending); channel_vol1.md 37 B",
    )
    s["counts"].update({"pass": len(s["steps"]) - 1, "blocked": 0})
    s["deltas"] = [d for d in s["deltas"] if d["delta"] == "UNCHANGED"] + [
        {"key": "avkit_transcript.compile", "delta": "REGRESSION"}
    ]


def _unblock(step_id: str):
    def mutate(s: dict) -> None:
        s["steps"][_index(s, step_id)] = _pass(step_id)
        s["counts"]["blocked"] -= 1
        s["counts"]["pass"] += 1

    return mutate


def _block_remove(s: dict) -> None:
    s["steps"][_index(s, "transcript.remove")].update(
        verdict="blocked", observable="transcript.add did not pass", blocked_by="transcript.add"
    )
    s["counts"]["blocked"] += 1
    s["counts"]["pass"] -= 1


def _pause_root(s: dict) -> None:
    """A start-root summary with start passing and pause failing on the block instead."""
    fresh = _sample("transcript.start")
    fresh["steps"][_index(fresh, "transcript.start")] = _pass("transcript.start")
    fresh["steps"][_index(fresh, "transcript.pause")].update(
        verdict="fail", reason="hollow", is_error=False, error=BLOCK_MESSAGE,
        observable="REST job Processing (want Paused)", blocked_by=None,
    )
    fresh["counts"].update({"blocked": 11, "pass": fresh["counts"]["total"] - 12})
    s.clear()
    s.update(fresh)


START = "transcript.start"
RESUME = "transcript.resume"
TOLERATED = {
    "the block paused the job before start saw Processing": lambda s: (s.clear(), s.update(_sample(START))),
}

REFUSED = {
    "Session 44's compile-only shape": _session44_shape,
    "another step also failed": _both(
        _step("capture.image", verdict="fail", reason="observable_failed", error="MCP error -32000: Connection closed"),
        _delta("avkit_capture.image", "REGRESSION"),
    ),
    "pause is the root": _pause_root,
    "the root failed with another message": _step(RESUME, error="No captions for this video."),
    "the root has no message": _step(RESUME, error=None),
    "the root failed as an MCP error": _step(RESUME, reason="observable_failed", is_error=True),
    "the root's is_error is missing": _step(RESUME, is_error=None),
    "the root was blocked, not failed": _step(RESUME, verdict="blocked"),
    "a transcript was fetched": _step(
        RESUME, observable="REST job Paused (want Processing), transcripts_done 1, last_item_status Done"
    ),
    "the item failed": _step(
        RESUME, observable="REST job Paused (want Processing), transcripts_done 0, last_item_status Failed"
    ),
    "the job is still Processing": _step(
        RESUME, observable="REST job Processing (want Processing), transcripts_done 0, last_item_status Pending"
    ),
    "the job never left Pending": _step(
        RESUME, observable="REST job Pending (want Processing), transcripts_done 0, last_item_status Pending"
    ),
    "the resume form on a start root": lambda s: (
        s.clear(),
        s.update(_sample(START)),
        _step(START, observable=ROOT_OBSERVABLE[RESUME])(s),
    ),
    "a chain step passed": _unblock("transcript.compile"),
    "a step off the chain is blocked": _block_remove,
    "a chain step is blocked by the wrong step": _step("transcript.retry.conflict", blocked_by="transcript.stop"),
    "a blocked step carries an error": _step("transcript.stop", error="boom"),
    "a blocked step's observable differs": _step("transcript.stop", observable="skipped"),
    "a step is skipped for the environment": _both(
        _step("capture.image", verdict="skip_env"), _set(("counts", "skip_env"), 1)
    ),
    "counts don't match": _set(("counts", "pass"), 1),
    "the compile delta is unchanged": _delta("avkit_transcript.compile", "UNCHANGED"),
    "another action regressed": _delta("avkit_capture.image", "REGRESSION"),
    "a delta is known, not a regression": _delta("avkit_transcript.stop", "KNOWN"),
    "a delta is listed twice": lambda s: s["deltas"].append({"key": "avkit_transcript.start", "delta": "REGRESSION"}),
    "an action was removed": _delta("avkit_x.y", "REMOVED"),
    "an action is new": _delta("avkit_x.y", "NEW"),
    "cleanup left something": _set(("cleanup", "ok"), False),
    "isolation failed": _set(("isolation", "ok"), False),
    "discovery failed": _set(("discovery", "status"), "fail"),
    "discovery found a ghost": _set(("discovery", "ghost"), ["avkit_x"]),
    "summary from another commit": _set(("commit",), "def"),
    "not authoritative": _set(("mode",), "container"),
    "the audit exited 0": _set(("exit_code",), 0),
    "another schema": _set(("schema",), "mcp-audit-summary.v2"),
    "steps are missing": _set(("steps",), []),
}


def _raises() -> bool:
    raise RuntimeError("yt-dlp changed")


PROOF_REFUSED = {
    "the direct fetch isn't blocked": lambda: False,
    "the direct fetch failed another way": _raises,
}


def _drifted(text: str) -> dict[str, str]:
    """plan.ts texts the chain check must refuse, each one edit from the real file."""
    return {
        "compile depends on another step": text.replace(
            'depends_on: ["transcript.retry"]', 'depends_on: ["transcript.stop.again"]', 1
        ),
        "a new step depends on the chain": text.replace(
            "const TRANSCRIPT_STEPS: StepSpec[] = [",
            'const TRANSCRIPT_STEPS: StepSpec[] = [\n  transcriptControl("transcript.x", "pause", ["transcript.stop"], "Paused", 1),',
            1,
        ),
        "a step outside the block depends on the chain": text.replace(
            "// ---------------------------------------------------------------- captures",
            '  { id: "capture.x", depends_on: ["transcript.compile"] },\n// ---------------------------------------------------------------- captures',
            1,
        ),
    }


def selftest() -> int:
    failures = 0
    total = 0

    def check(ok: bool, line: str) -> None:
        nonlocal failures, total
        total += 1
        failures += not ok
        print(f"{'PASS' if ok else 'FAIL'} {line}")

    found = source_problems()
    check(not found, f"CHAIN and BLOCK_MESSAGE match plan.ts and the domain -> {found or 'match'}")
    text = PLAN_TS.read_text(encoding="utf-8")
    for name, drifted in _drifted(text).items():
        found = chain_problems(drifted) if drifted != text else []
        check(bool(found), f"refused plan.ts drift '{name}' -> {found}")
    for root, size in ((RESUME, 10), (START, 12)):
        chain = dependents(root, CHAIN)
        check(len(chain) == size, f"root {root} blocks {size} steps -> {len(chain)}")

    base = problems(_sample(), "abc")
    check(not base, f"case 'the block paused the job on resume' -> {base or 'tolerated'}")
    for name, mutate in TOLERATED.items():
        summary = copy.deepcopy(_sample())
        mutate(summary)
        found = problems(summary, "abc")
        check(not found, f"case '{name}' -> {found or 'tolerated'}")
    for name, mutate in REFUSED.items():
        summary = copy.deepcopy(_sample())
        mutate(summary)
        found = problems(summary, "abc")
        check(bool(found), f"refused '{name}' -> {found}")
    blocked = proof_problems(lambda: True)
    check(not blocked, f"case 'the direct fetch is blocked' -> {blocked or 'tolerated'}")
    for name, fetch in PROOF_REFUSED.items():
        found = proof_problems(fetch)
        check(bool(found), f"refused '{name}' -> {found}")
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
    # The summary and the source come first: the direct fetch is real YouTube traffic.
    found = problems(summary, args.head) or source_problems() or proof_problems(caption_fetch_blocked)
    for problem in found:
        print(f"audit rule refuses: {problem}")
    if found:
        return 1
    root = next(step["id"] for step in summary["steps"] if step["verdict"] == "fail")
    print(
        f"audit rule: only {root} failed, paused on the caption block as MEU-116 requires, its chain is blocked, "
        "and a direct caption fetch is blocked; tolerated as incomplete verification. "
        "Transcript is not verified end to end."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
