"""Session 86 hdp-expert-pass plan-local checks (implementation-plan.md §Verification Plan).

Usage (from the repository root, ``PYTHONIOENCODING=utf-8``):

  python ep-check.py anchors          Session 85's anchors exist; each planned edit is absent or already equal (S1).
  python ep-check.py baseline         Record baseline.sha, the dirty tree with sha256 per path, and byte copies
                                      of every modified file under C:/Temp/av-kit/s86/baseline-files/.
  python ep-check.py delta [--only P]*Each modified file equals apply(its baseline copy) byte for byte (AC-5, AC-10);
                                      the compiled JSON adds only the new class.
  python ep-check.py newfiles         The skill and the agent equal their planned bytes (AC-6, AC-11).
  python ep-check.py eol              Line endings: modified files keep their bare-LF count; new files and the
                                      compiled JSON hold no CR (AC-13).
  python ep-check.py govern           The three governance regexes on added lines and on the new files (AC-12).
  python ep-check.py scope            HEAD equals baseline.sha; every changed path is planned, or baseline-dirty
                                      with an unchanged sha256 (S4).
  python ep-check.py upstream --hdp F --skill F
                                      The constants equal upstream a73d6df with av-kit's substitutions reversed.
  python ep-check.py selftest         Positive and negative fixtures for every check above.

Every check prints one line per problem and exits 1 on any problem, 0 otherwise. Edits are
applied to lines with their own line ending kept, so a CRLF file stays CRLF and a file's odd
bare LF (model-delegation.md line 5) stays where it is.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

PLAN = "docs/execution/plans/2026-11-15-hdp-expert-pass"
BASE_DIR = Path("C:/Temp/av-kit/s86/baseline-files")

HDP = ".agent/docs/human-decision-protocol.md"
ROUTING = ".agent/docs/model-routing.md"
DELEGATION = ".agent/docs/model-delegation.md"
COMMANDS = ".agent/docs/commands.md"
SKILLS_README = ".agent/skills/README.md"
CLI_SKILL = ".agent/skills/cli-dispatch/SKILL.md"
CLI_WORKFLOW = ".agent/workflows/cli-dispatch.md"
OVERLAY = ".agent/model-registry.local.yaml"
COMPILED = ".agent/model-registry.local.json"
SKILL = ".agent/skills/expert-pass/SKILL.md"
AGENT = ".claude/agents/av-kit-peer-reviewer.md"
TEST = "tests/tooling/test_hdp_expert_pass.py"
# Added in execution (D-890): verify_adoption.py refuses a numeric model pin in the overlay or the
# compiled JSON unless the routing census records that exact line, so the two new binding lines
# are recorded there and the three compiled lines that moved down get their new line numbers.
CENSUS = "docs/execution/plans/2026-09-26-framework-update-adoption/routing-census.md"

FILES_MODIFIED = [HDP, ROUTING, DELEGATION, COMMANDS, SKILLS_README, CLI_SKILL, CLI_WORKFLOW, OVERLAY, COMPILED, CENSUS]
FILES_NEW = [SKILL, AGENT, TEST]
PROJECT = [
    f"{PLAN}/*",
    ".agent/context/handoffs/2026-11-15-hdp-expert-pass-*",
    "docs/execution/reflections/2026-11-15-hdp-expert-pass-reflection.md",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
    ".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md",
]

# ---------------------------------------------------------------- planned text (av-kit form)

EXPECTED_5A = """## 5a. Expert pass — one review of a set of briefs

Before the human sees a set of briefs at a planned stop, the author gets one expert pass on the
set, in a fresh context. A reference to this step says "HDP §5a".

1. Send the set to the advisory peer reviewer (`avkit_peer_reviewer`) in a fresh context. Give
   the domain, the stage in three lines and the paths of the briefs and of the files that they
   cite. The packet template is `.agent/skills/expert-pass/SKILL.md`.
2. For each recommendation the reviewer answers three questions. Does it add work that the
   present stage does not need? Can it be done as written, at the present size? Can it be undone?
3. The reviewer checks that each named thing exists, and names a cheaper option when the brief
   lists none.
4. The result for each brief is one of four: holds, cut down, changed or widened, each with its
   evidence. "Holds" is a valid result.
5. The author checks each finding against the files. Then the author adopts it, or does not
   adopt it and gives the evidence.
6. One line goes above the set: `Expert pass (fresh context): <n> briefs. Holds: <ids>.
   Changed: <ids>. Not adopted: <ids>.` A brief gets its own line only in two cases: `Expert
   pass: changed from <X>: <reason>.` when the pass changed it, and `Expert pass: <result>, not
   adopted: <reason>.` when the author did not adopt the finding.

The pass is advice. It makes no ruling, writes no verdict file and adds no tool, hook, schema or
record field. It runs once for each set, in one round. `Expert pass: inline.` is for one
question during other work. `Expert pass: inline, not independent.` is for a run that cannot
start a fresh context. `Expert pass: not run: the human said to skip it.` is the only skip. A
request for a human action (M-10) gets no pass. The step names a role, and no model or effort.
There is no floor and no skip rule by set size.""".split("\n")

M3_PREFIX = "- M-3 covers edits to this list and to this protocol"
M3_PLAIN = "- M-3 covers edits to this list and to this protocol: they are human-approved, never autonomous."
M3_CLAUSE = [
    "- M-3 covers edits to this list and to this protocol: they are human-approved, never",
    "  autonomous, except a ruling that the human hands to the agent under §6.",
]
OVERTURN_PREFIX = (
    "A decision resolved autonomously in planning and later overturned by the human is recorded, not deleted"
)
HANDOVER = [
    "A ruling that the human hands to the agent for one brief set is the agent's ruling. Record it",
    "with `resolution: autonomous` and the agent's own basis tag, never `Human-approved`, and keep the",
    "entry's `mandatory:` list. The reasoning starts with `Handed to the agent: USER_EXPLICIT <date>",
    "'<quote>'.`, and that quote meets the gate. An acceptance criterion that rests on the ruling",
    "carries the same tag. The hand-over covers one set only, and only an item with no M hit or with",
    "M-3, M-5, M-6 or M-8; every other item of §4a stays the human's. One line from the human",
    "overturns it.",
]

ROUTING_FIVE = "The local overlay adds five classes"
ROUTING_SIX = "The local overlay adds six classes"
ROUTING_STACK_ANCHOR = "| Independent reviewer | `avkit_independent_reviewer` |"
ROUTING_STACK_ROW = (
    "| Peer reviewer (advisory) | `avkit_peer_reviewer` | Fresh-context advisory read: the HDP §5a expert"
    " pass and second opinions, through the Claude Code agent `av-kit-peer-reviewer`; never a verdict"
    " or an approval |"
)
ROUTING_DISPATCH_ANCHOR = "| Classification | `avkit_router` if authorized |"
ROUTING_DISPATCH_ROW = (
    "| Expert pass on a set of briefs before the human sees them (HDP §5a) | `avkit_peer_reviewer` in a"
    " fresh context, advisory (Claude Code agent `av-kit-peer-reviewer`); a harness that cannot start it"
    " records `Expert pass: inline, not independent.` | class default |"
)
DELEGATION_ANCHOR = "- **Open decisions.**"
DELEGATION_PEER = [
    "- **Peer reviewer.** The HDP §5a expert pass and other second opinions go to the Claude Code",
    "  agent `av-kit-peer-reviewer` (class `avkit_peer_reviewer`) in a fresh context. Its answer is",
    "  advice: it never writes a verdict file, never approves, and never stands in for",
    "  `avkit_independent_reviewer`.",
]
COMMANDS_ANCHOR = "| CLI Dispatch | `.agent/skills/cli-dispatch/SKILL.md` |"
COMMANDS_ROW = (
    "| Expert Pass | `.agent/skills/expert-pass/SKILL.md` | The packet for one expert pass on a set of"
    " briefs (HDP §5a). The reviewer reads only, and asks the three questions. |"
)
README_ANCHOR = "| `cli-dispatch/SKILL.md` |"
README_ROW = (
    "| `expert-pass/SKILL.md` | a set of decision briefs, HDP §5a | The packet for one fresh-context"
    " expert pass; the reviewer reads only |"
)
CLI_OLD = (
    "Only avkit_coordinator, avkit_builder, avkit_verifier, avkit_router and avkit_independent_reviewer"
    " are adopted local classes."
)
CLI_NEW = (
    "Only avkit_coordinator, avkit_builder, avkit_verifier, avkit_router, avkit_independent_reviewer and"
    " avkit_peer_reviewer are adopted local classes; avkit_peer_reviewer is the in-harness Claude Code"
    " agent for the HDP §5a expert pass, not a CLI dispatch route."
)
OVERLAY_BLOCK = [
    "  avkit_peer_reviewer:",
    "    contract:",
    "      capabilities: [deep_reasoning, agentic_exec]",
    "      effort_default: high",
    "      not_a_reviewer: true",
    "      forbid: [claude-fable-5-2]",
    "    bindings:",
    "      claude-code-agents: {slug: claude-opus-5-5, effort: high}",
]
COMPILED_CLASS = {
    "bindings": {"claude-code-agents": {"effort": "high", "slug": "claude-opus-5-5"}},
    "contract": {
        "capabilities": ["deep_reasoning", "agentic_exec"],
        "effort_default": "high",
        "forbid": ["claude-fable-5-2"],
        "not_a_reviewer": True,
    },
}

# The routing census (D-890). Each census match is keyed by (path, sha256 of the whole line).
CENSUS_REASON = "Approved AVKIT_CLASS_MAP catalog binding or compiled mirror; sole model identity authority."
CENSUS_NEW_JSON = '          "slug": "claude-opus-5-5"'  # compiled JSON line 78
CENSUS_NEW_YAML = OVERLAY_BLOCK[-1]  # overlay line 60
# (path, line the census holds, line the new class moves it to)
CENSUS_RENUMBER = [(COMPILED, 98, 117), (COMPILED, 94, 113), (COMPILED, 78, 97)]
# (path, census line it goes after, its line, its text)
CENSUS_ADD = [(COMPILED, 58, 78, CENSUS_NEW_JSON), (OVERLAY, 52, 60, CENSUS_NEW_YAML)]

SKILL_TEXT = """---
name: expert-pass
description: The packet for one expert pass on a set of briefs before the human sees them (HDP §5a). The reviewer reads only and asks three questions.
---

# Expert Pass

Use this packet when HDP §5a applies: a set of Decision Briefs goes to the human at a planned
stop. Send it to the advisory peer reviewer (`avkit_peer_reviewer`) in a fresh context. The
routing row is in the CLI Dispatch Decision Table of `.agent/docs/model-routing.md`.

## Packet

Fill in the five parts and send them as the prompt.

1. **Domain.** The domain of the decisions, and the role: "You are a senior practitioner of
   <domain>."
2. **Stage.** Two or three lines: who does the work, the present size, and what does not exist
   yet. Mark each number "measured" or "assumed".
3. **Paths.** The paths of the briefs and of the files that the briefs cite, with line ranges.
4. **The three questions.** For each recommendation: Does it add work that the present stage
   does not need? Can it be done as written, at the present size? Can it be undone? Does each
   thing that the brief names exist? If the brief lists no cheaper option, what is one?
5. **Result form.** For each brief, return one result: holds, cut down, changed or widened.
   Give a reason of two or three sentences and the evidence (`file:line` or a URL). Mark a claim
   that has no evidence "inference". "Holds" is a valid result.

End the packet with this line: "Read only. Do not edit, write or create a file. Return the
result as text."

## After the pass

- Save the result to a receipt.
- Check each finding against the files, and check that each thing the reviewer names exists
  (HDP §5a step 5).
- Write the set line and the per-brief lines of HDP §5a step 6.
- The pass is advice. It makes no ruling and writes no verdict file.
"""

AGENT_TEXT = """---
name: av-kit-peer-reviewer
description: Advisory adversarial read of one av-kit diff or plan, for a second opinion on correctness-critical work before the independent review. Writes findings to a receipt. Advisory only — it is not the independent reviewer, never writes a verdict file, and never authors an approval.
model: opus
effort: high
tools: Read, Grep, Glob, Bash
---
<!-- AUTOGEN: model-registry REGISTRY_SHA -->
<!-- Local class: avkit_peer_reviewer; project: P:/av-kit; overlay_sha256: OVERLAY_SHA. Do not run global sync: its filename convention resolves global classes. Re-resolve this explicit local class before regenerating only model and provenance. -->
# av-kit-peer-reviewer

You are a peer-reviewer subagent for the av-kit project. You give an **advisory** adversarial
read of exactly one diff or plan per dispatch, before the work goes to independent review.
This agent never writes a verdict file and never authors `approved`. The independent reviewer
(`avkit_independent_reviewer` class, a different vendor) remains the only source of a review
verdict; your findings are input the coordinator weighs, not a gate.
Read-only is enforced by the `tools` allowlist above — it grants no `Write`/`Edit`.

## What you do

1. Read the diff or plan named in the dispatch prompt and the files it touches, in full.
2. Try to break it: wrong behaviour on edge cases, missed call sites, contract or boundary-input
   gaps, tests that cannot fail, claims the evidence does not support. Run read-only commands
   (tests, type checks, `rg`) when they settle a question.
3. Report each finding with `file:line`, the concrete failure scenario, and the evidence, ranked
   most severe first. Write the report to the receipt path the dispatch prompt names, through the
   redirect pattern. When the prompt names no receipt path (the HDP §5a packet in
   `.agent/skills/expert-pass/SKILL.md` asks for text), return the report as text. If no finding
   survives your own check, say so.

## What you do not do

- You never write or edit a `*-critical-review.md` file, never record a review round, and never
  state a verdict (`approved`, `changes_required`, or any equivalent) — that would be self-review
  by the authoring vendor.
- You do not fix what you find; the coordinator decides what changes.

## Guardrails (non-negotiable — inlined because rule inheritance is not guaranteed)

- **Redirect every command to the receipts folder** `C:/Temp/av-kit`: in PowerShell
  `<command> *> C:/Temp/av-kit/<name>.txt`; in the Bash tool `<command> > C:/Temp/av-kit/<name>.txt 2>&1`,
  never `*>` there. Never pipe a long-running process to a filter.
- **Never edit, create, or delete repository files** — read-only via the `tools` allowlist (no
  `Write`/`Edit`); the receipt is written only through the redirect.
- **Never commit or push**, and never perform any irreversible action.
- **Never modify a test's assertions**; report what the tests actually did.
- **Never satisfy a human-approval gate** — your output is agent-generated, never `USER_EXPLICIT`.
"""

# The three regexes of verify_adoption.py governance_inventory (2026-09-26 adoption checks).
GOVERN = [
    (
        "global routing class",
        re.compile(
            r"(?i)(?:--?(?:model)?class[ =]+|resolve\s+)[`'\"]?(?:builder|coordinator|verifier)\b"
            r"|class pins[^\{]*\{[^}]*\b(?:builder|coordinator|verifier)\b"
        ),
    ),
    (
        "unconfigured live routing",
        re.compile(r"(?i)(?:default (?:reviewer|model)|fallback)\s*:\s*(?:GPT|Gemini|Claude|Opus|Sonnet|Grok)"),
    ),
    (
        "numeric model pin",
        re.compile(r"(?i)gpt[- ]?\d|opus[- ]?\d|sonnet[- ]?\d|haiku[- ]?\d|grok[- ]?\d|composer[- ]?\d|gemini[- ]?\d"),
    ),
]
HISTORICAL = re.compile(r"Historical observation \(\d{4}-\d{2}-\d{2}\): .+ was measured\.$")


class Stop(Exception):
    """An S1 condition: an anchor is missing, or a planned edit is present in another form."""


# ---------------------------------------------------------------- byte-level line editing


def split(data: bytes) -> list[bytes]:
    return data.splitlines(keepends=True)


def body(line: bytes) -> str:
    return line.rstrip(b"\r\n").decode("utf-8")


def eol_of(line: bytes) -> bytes:
    if line.endswith(b"\r\n"):
        return b"\r\n"
    return b"\n" if line.endswith(b"\n") else b""


def enc(texts: list[str], eol: bytes) -> list[bytes]:
    return [t.encode("utf-8") + eol for t in texts]


def flat(texts) -> str:
    return " ".join(" ".join(texts).split())


def find_one(lines: list[bytes], pred, what: str) -> int:
    hits = [i for i, ln in enumerate(lines) if pred(body(ln))]
    if len(hits) != 1:
        raise Stop(f"{what}: {len(hits)} matching lines, expected 1")
    return hits[0]


def block_end(lines: list[bytes], start: int, continuation: str) -> int:
    """Index after the block that starts at ``start`` (a bullet and its indented lines)."""
    end = start + 1
    while continuation and end < len(lines) and body(lines[end]).startswith(continuation):
        end += 1
    return end


def insert_after(data: bytes, anchor: str, new: list[str], what: str, continuation: str = "") -> bytes:
    lines = split(data)
    i = find_one(lines, lambda t: t.startswith(anchor), f"{what} anchor {anchor!r}")
    end = block_end(lines, i, continuation)
    if [body(x) for x in lines[end : end + len(new)]] == new:
        return data
    if any(new[0] == body(x) for x in lines):
        raise Stop(f"{what}: the new line is present but not right after its anchor")
    eol = eol_of(lines[i]) or b"\n"
    return b"".join(lines[:end] + enc(new, eol) + lines[end:])


def replace_once(data: bytes, old: str, new: str, what: str) -> bytes:
    o, n = old.encode("utf-8"), new.encode("utf-8")
    if data.count(o) == 1 and data.count(n) == 0:
        return data.replace(o, n)
    if data.count(o) == 0 and data.count(n) == 1:
        return data
    raise Stop(f"{what}: old text {data.count(o)}x, new text {data.count(n)}x")


def section_bounds(lines: list[bytes], heading: str) -> tuple[int, int]:
    start = find_one(lines, lambda t: t.startswith(heading), f"heading {heading!r}")
    end = start + 1
    while end < len(lines) and not body(lines[end]).startswith("## "):
        end += 1
    return start, end


# ---------------------------------------------------------------- the HDP edits


def hdp_anchors(data: bytes) -> list[str]:
    """Session 85's structure that Session 86 relies on (S1 when absent)."""
    lines = split(data)
    heads = [body(x) for x in lines if body(x).startswith("## ")]
    problems = []
    order = []
    for h in ("## 4a.", "## 5.", "## 6."):
        hits = [i for i, t in enumerate(heads) if t.startswith(h)]
        if len(hits) != 1:
            problems.append(f"S1 heading {h!r} found {len(hits)} times")
        else:
            order.append(hits[0])
    if len(order) == 3 and order != sorted(order):
        problems.append("S1 headings 4a, 5 and 6 are out of order")
    if len(order) == 3 and order[2] == len(heads) - 1:
        problems.append("S1 no heading follows §6")
    for m in ("M-3", "M-5", "M-6", "M-8"):
        if not any(body(x).startswith(f"| {m} |") for x in lines):
            problems.append(f"S1 §4a table row {m} missing")
    return problems


def hdp_apply(data: bytes) -> bytes:
    """Baseline HDP -> planned HDP. Idempotent; raises Stop on any anchor problem."""
    problems = hdp_anchors(data)
    if problems:
        raise Stop("; ".join(problems))
    lines = split(data)
    # 1. The M-3 note gains the hand-over clause.
    i = find_one(lines, lambda t: t.startswith(M3_PREFIX), "M-3 note")
    end = block_end(lines, i, "  ")
    text = flat(body(x) for x in lines[i:end])
    if text == flat(M3_CLAUSE):
        pass
    elif text == M3_PLAIN:
        lines[i:end] = enc(M3_CLAUSE, eol_of(lines[i]) or b"\n")
    else:
        raise Stop(f"M-3 note is neither the plain nor the clause form: {text!r}")
    # 2. The hand-over paragraph right after the overturn paragraph in §6.
    s6, e6 = section_bounds(lines, "## 6.")
    starts = [k for k in range(s6, e6) if body(lines[k]).startswith(OVERTURN_PREFIX[:60])]
    if len(starts) != 1:
        raise Stop(f"overturn paragraph in §6: {len(starts)} starts, expected 1")
    k = starts[0]
    j = k
    while j < e6 and body(lines[j]).strip():
        j += 1
    if not flat(body(x) for x in lines[k:j]).startswith(OVERTURN_PREFIX):
        raise Stop("overturn paragraph text differs from its expected opening")
    after = [body(x) for x in lines[j + 1 : j + 1 + len(HANDOVER)]]
    eol = eol_of(lines[k]) or b"\n"
    if after == HANDOVER:
        pass
    elif any("Handed to the agent" in body(x) for x in lines):
        raise Stop("a hand-over text is present in another place or form")
    else:
        lines[j:j] = enc([""] + HANDOVER, eol)
    # 3. §5a before §6.
    heads = [n for n, x in enumerate(lines) if body(x).startswith("## 5a.")]
    if heads:
        if len(heads) != 1:
            raise Stop("§5a heading appears more than once")
        s5a, e5a = section_bounds(lines, "## 5a.")
        got = [body(x) for x in lines[s5a:e5a]]
        if got != EXPECTED_5A + [""] or not body(lines[e5a]).startswith("## 6."):
            raise Stop("§5a is present but differs from the planned text or is not right before §6")
    else:
        s6 = find_one(lines, lambda t: t.startswith("## 6."), "heading '## 6.'")
        lines[s6:s6] = enc(EXPECTED_5A + [""], eol_of(lines[s6]) or b"\n")
    return b"".join(lines)


# ---------------------------------------------------------------- every planned edit


def overlay_apply(data: bytes) -> bytes:
    lines = split(data)
    tail = [body(x) for x in lines[-len(OVERLAY_BLOCK) :]]
    if tail == OVERLAY_BLOCK:
        return data
    if b"avkit_peer_reviewer" in data:
        raise Stop("overlay holds avkit_peer_reviewer in another form")
    if not data.endswith(b"\n"):
        raise Stop("overlay does not end with a line ending")
    return data + b"".join(enc(OVERLAY_BLOCK, eol_of(lines[-1])))


def census_row(path: str, line: int, text: str) -> str:
    return f"| `{path}:{line}` | binding | {CENSUS_REASON} | {text} |"


def census_object(path: str, line: int, text: str) -> list[str]:
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return [
        "    {",
        f'      "path": "{path}",',
        f'      "line": {line},',
        f'      "text_sha256": "{sha}",',
        '      "classification": "binding",',
        f'      "reason": "{CENSUS_REASON}"',
        "    },",
    ]


def census_line_index(lines: list[bytes], path: str, line: int) -> int:
    """Index of the ``"line": N,`` field of the census match object for ``path`` line ``line``."""
    hits = [
        i
        for i in range(1, len(lines))
        if body(lines[i]) == f'      "line": {line},' and body(lines[i - 1]) == f'      "path": "{path}",'
    ]
    if len(hits) != 1:
        raise Stop(f"census match {path}:{line}: {len(hits)} objects, expected 1")
    return hits[0]


def census_apply(data: bytes) -> bytes:
    """Record the two new binding lines and renumber the three moved ones, table and JSON alike.
    The census is applied once: when its new overlay row is present the file is returned as is,
    and ``EP delta`` proves it equals the baseline plus these edits byte for byte."""
    if census_row(OVERLAY, 60, CENSUS_NEW_YAML).encode("utf-8") in data:
        return data
    for path, old, new in CENSUS_RENUMBER:
        data = replace_once(data, f"| `{path}:{old}` |", f"| `{path}:{new}` |", f"census row {path}:{old}")
        lines = split(data)
        i = census_line_index(lines, path, old)
        lines[i] = f'      "line": {new},'.encode("utf-8") + eol_of(lines[i])
        data = b"".join(lines)
    for path, after, line, text in CENSUS_ADD:
        data = insert_after(data, f"| `{path}:{after}` |", [census_row(path, line, text)], f"census row {path}:{line}")
        lines = split(data)
        i = census_line_index(lines, path, after)
        end = i + 4  # after the line field: text_sha256, classification, reason, the closing brace
        if body(lines[end]) != "    },":
            raise Stop(f"census match {path}:{after} does not close with '    }},'")
        data = b"".join(lines[: end + 1] + enc(census_object(path, line, text), eol_of(lines[end])) + lines[end + 1 :])
    return data


def apply_file(path: str, data: bytes) -> bytes:
    if path == CENSUS:
        return census_apply(data)
    if path == HDP:
        return hdp_apply(data)
    if path == ROUTING:
        data = replace_once(data, ROUTING_FIVE, ROUTING_SIX, "routing class count")
        data = insert_after(data, ROUTING_STACK_ANCHOR, [ROUTING_STACK_ROW], "routing stack row")
        return insert_after(data, ROUTING_DISPATCH_ANCHOR, [ROUTING_DISPATCH_ROW], "routing dispatch row")
    if path == DELEGATION:
        return insert_after(data, DELEGATION_ANCHOR, DELEGATION_PEER, "delegation bullet", continuation="  ")
    if path == COMMANDS:
        return insert_after(data, COMMANDS_ANCHOR, [COMMANDS_ROW], "commands skills row")
    if path == SKILLS_README:
        return insert_after(data, README_ANCHOR, [README_ROW], "skills README row")
    if path in (CLI_SKILL, CLI_WORKFLOW):
        return replace_once(data, CLI_OLD, CLI_NEW, f"{path} class list")
    if path == OVERLAY:
        return overlay_apply(data)
    raise KeyError(path)


EDITED = [p for p in FILES_MODIFIED if p != COMPILED]


def compiled_problems(base: bytes, now: bytes) -> list[str]:
    problems = []
    if b"\r" in now:
        problems.append(f"{COMPILED} holds CR")
    try:
        b, n = json.loads(base), json.loads(now)
    except ValueError as exc:
        return problems + [f"{COMPILED} is not JSON: {exc}"]
    new_class = n.get("classes", {}).pop("avkit_peer_reviewer", None)
    if new_class != COMPILED_CLASS:
        problems.append(f"{COMPILED} avkit_peer_reviewer is {new_class!r}")
    if n != b:
        problems.append(f"{COMPILED} differs from its baseline in more than the new class")
    return problems


def first_diff(a: bytes, b: bytes) -> str:
    la, lb = split(a), split(b)
    for n, (x, y) in enumerate(zip(la, lb), 1):
        if x != y:
            return f"line {n}: expected {x[:90]!r}, got {y[:90]!r}"
    return f"line count: expected {len(la)}, got {len(lb)}"


def delta_problems(path: str, base: bytes, now: bytes) -> list[str]:
    if path == COMPILED:
        return compiled_problems(base, now)
    try:
        want = apply_file(path, base)
    except Stop as exc:
        return [f"S1 {path}: {exc}"]
    if now == want:
        return []
    return [f"{path} is not its baseline plus the planned edits ({first_diff(want, now)})"]


def eol_counts(data: bytes) -> tuple[int, int]:
    crlf = data.count(b"\r\n")
    return crlf, data.count(b"\n") - crlf


def eol_problems(path: str, base: bytes | None, now: bytes) -> list[str]:
    if base is None or path == COMPILED:
        return [f"{path} holds CR"] if b"\r" in now else []
    (bc, bl), (nc, nl) = eol_counts(base), eol_counts(now)
    problems = []
    if nl != bl:
        problems.append(f"{path} bare LF count {bl} -> {nl}")
    if bc and not nc:
        problems.append(f"{path} lost its CRLF endings")
    if now.count(b"\r") != nc:
        problems.append(f"{path} holds a lone CR")
    return problems


def govern_lines(lines) -> list[str]:
    out = []
    for where, text in lines:
        for name, rx in GOVERN:
            if rx.search(text) and not (name == "numeric model pin" and HISTORICAL.search(text)):
                out.append(f"{name}: {where}: {text.strip()[:100]}")
    return out


def added_lines(base: bytes, now: bytes) -> list[str]:
    a = [body(x) for x in split(base)]
    b = [body(x) for x in split(now)]
    return [ln[1:] for ln in difflib.unified_diff(a, b, lineterm="", n=0) if ln.startswith("+") and not ln.startswith("+++")]


def agent_expected(registry_sha: str, overlay_sha: str) -> str:
    return AGENT_TEXT.replace("REGISTRY_SHA", registry_sha).replace("OVERLAY_SHA", overlay_sha)


def newfile_problems(skill: bytes | None, agent: bytes | None, registry_sha: str, overlay_sha: str) -> list[str]:
    problems = []
    if skill is None:
        problems.append(f"{SKILL} missing")
    elif skill != SKILL_TEXT.encode("utf-8"):
        problems.append(f"{SKILL} differs ({first_diff(SKILL_TEXT.encode('utf-8'), skill)})")
    want = agent_expected(registry_sha, overlay_sha).encode("utf-8")
    if agent is None:
        problems.append(f"{AGENT} missing")
    elif agent != want:
        problems.append(f"{AGENT} differs ({first_diff(want, agent)})")
    return problems


def scope_problems(head: str, base_head: str, status: dict[str, str], baseline: dict[str, str], sha) -> list[str]:
    """``status`` maps each changed path to its porcelain code; ``baseline`` maps the paths dirty
    at row 0 to their sha256 then; ``sha`` reads a path's sha256 now (``deleted`` if absent)."""
    problems = []
    if head != base_head:
        problems.append(f"S4 HEAD {head} differs from baseline.sha {base_head}")
    planned = set(FILES_MODIFIED) | set(FILES_NEW)
    for path in sorted(status):
        if path in planned or any(fnmatch(path, g) for g in PROJECT):
            continue
        if path in baseline and sha(path) == baseline[path]:
            continue
        why = "changed since the baseline" if path in baseline else "not in this plan and not dirty at baseline"
        problems.append(f"S4 outside scope: {path} ({why})")
    for path in sorted(set(baseline) - set(status)):
        if path not in planned and not any(fnmatch(path, g) for g in PROJECT):
            problems.append(f"S4 outside scope: {path} was dirty at baseline and is clean now")
    return problems


# ---------------------------------------------------------------- repository access


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def git_status() -> dict[str, str]:
    raw = git("status", "--porcelain=v1", "-z", "--untracked-files=all").split(b"\0")
    out, k = {}, 0
    while k < len(raw):
        rec = raw[k].decode("utf-8")
        k += 1
        if not rec:
            continue
        code, path = rec[:2], rec[3:]
        out[path] = code
        if code[0] in "RC":
            k += 1  # the rename source follows
    return out


def file_sha(path: str) -> str:
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "deleted"


def read(path: str) -> bytes | None:
    p = Path(path)
    return p.read_bytes() if p.is_file() else None


def base_copy(path: str) -> bytes:
    record = json.loads(Path(f"{PLAN}/baseline-files.json").read_text(encoding="utf-8"))
    data = (BASE_DIR / path).read_bytes()
    if hashlib.sha256(data).hexdigest() != record[path]:
        raise SystemExit(f"baseline copy of {path} no longer matches baseline-files.json")
    return data


def report(problems: list[str], ok: str) -> int:
    for p in problems:
        print(p)
    print(ok if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


# ---------------------------------------------------------------- subcommands


def cmd_anchors(_args) -> int:
    problems, notes = [], []
    for path in EDITED:
        data = read(path)
        if data is None:
            problems.append(f"S1 {path} missing")
            continue
        try:
            done = apply_file(path, data)
            notes.append(f"{path}: {'already applied' if done == data else 'edits absent, anchors found'}")
        except Stop as exc:
            problems.append(f"S1 {path}: {exc}")
    for path in FILES_NEW:
        if Path(path).exists():
            notes.append(f"{path}: exists")
    print("\n".join(notes))
    return report(problems, "anchors: ok")


def cmd_baseline(_args) -> int:
    for path in FILES_NEW:
        if Path(path).exists():
            return report([f"{path} exists before row 1"], "")
    if cmd_anchors(None):
        return 1
    head = git("rev-parse", "HEAD").decode().strip()
    Path(f"{PLAN}/baseline.sha").write_text(head, encoding="utf-8", newline="")
    status = git_status()
    dirty = {p: file_sha(p) for p in sorted(status)}
    Path(f"{PLAN}/baseline-dirty.json").write_text(json.dumps(dirty, indent=1) + "\n", encoding="utf-8", newline="\n")
    Path(f"{PLAN}/baseline-dirty.txt").write_text(
        "".join(f"{status[p]} {p}\n" for p in sorted(status)), encoding="utf-8", newline="\n"
    )
    record = {}
    for path in FILES_MODIFIED:
        data = Path(path).read_bytes()
        target = BASE_DIR / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        record[path] = hashlib.sha256(data).hexdigest()
        crlf, bare = eol_counts(data)
        print(f"baseline {path} bytes={len(data)} crlf={crlf} bare_lf={bare} sha256={record[path]}")
    Path(f"{PLAN}/baseline-files.json").write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"baseline.sha {head}; {len(dirty)} dirty path(s)")
    return 0


def cmd_delta(args) -> int:
    problems = []
    for path in FILES_MODIFIED:
        if args.only and path not in args.only:
            continue
        now = read(path)
        if now is None:
            problems.append(f"{path} missing")
            continue
        problems += delta_problems(path, base_copy(path), now)
    return report(problems, "delta: every modified file is its baseline plus the planned edits")


def cmd_newfiles(_args) -> int:
    compiled = json.loads(Path(COMPILED).read_text(encoding="utf-8"))
    problems = newfile_problems(read(SKILL), read(AGENT), compiled["validated_against"], file_sha(OVERLAY))
    return report(problems, "newfiles: the skill and the agent are the planned bytes")


def cmd_eol(_args) -> int:
    problems = []
    for path in FILES_MODIFIED:
        problems += eol_problems(path, base_copy(path), Path(path).read_bytes())
    for path in FILES_NEW:
        data = read(path)
        problems += [f"{path} missing"] if data is None else eol_problems(path, None, data)
    return report(problems, "eol: line endings kept")


def cmd_govern(_args) -> int:
    lines = []
    for path in EDITED:
        # The census is where each pin line is recorded, so its added lines hold the pins by design;
        # the census is not among the files that verify_adoption.py scans (D-890).
        if path.endswith(".md") and path != CENSUS:
            lines += [(f"{path} (added)", t) for t in added_lines(base_copy(path), Path(path).read_bytes())]
    for path in (SKILL, AGENT):
        data = read(path) or b""
        lines += [(f"{path}:{n}", body(x)) for n, x in enumerate(split(data), 1)]
    return report(govern_lines(lines), "govern: no governance pattern in added or new lines")


def cmd_scope(_args) -> int:
    base_head = Path(f"{PLAN}/baseline.sha").read_text(encoding="utf-8").strip()
    baseline = json.loads(Path(f"{PLAN}/baseline-dirty.json").read_text(encoding="utf-8"))
    head = git("rev-parse", "HEAD").decode().strip()
    return report(scope_problems(head, base_head, git_status(), baseline, file_sha), "scope: every changed path is in scope")


def unwrap_avkit(text: str) -> str:
    return text.replace("`avkit_peer_reviewer`", "`peer_reviewer`")


def upstream_problems(hdp: str, skill: str) -> list[str]:
    problems = []
    lines = hdp.split("\n")
    s = [i for i, t in enumerate(lines) if t.startswith("## 5a.")]
    e = [i for i, t in enumerate(lines) if t.startswith("## 6.")]
    if len(s) != 1 or len(e) != 1:
        return ["upstream HDP lacks one §5a or §6 heading"]
    if flat(lines[s[0] : e[0]]) != flat([unwrap_avkit(t) for t in EXPECTED_5A]):
        problems.append("EXPECTED_5A differs from upstream §5a (flattened, substitution reversed)")
    if "\n".join(M3_CLAUSE) not in hdp:
        problems.append("M3_CLAUSE is not upstream's text")
    if "\n".join(HANDOVER) not in hdp:
        problems.append("HANDOVER is not upstream's text")
    if OVERTURN_PREFIX not in flat(lines):
        problems.append("OVERTURN_PREFIX is not in upstream")
    mine = unwrap_avkit(SKILL_TEXT).replace(
        "the CLI Dispatch Decision Table of `.agent/docs/model-routing.md`",
        "the Quick decision guide of `.agent/docs/model-routing.md`",
    )
    if flat(mine.split("\n")) != flat(skill.split("\n")):
        problems.append("SKILL_TEXT differs from upstream's skill (flattened, substitutions reversed)")
    return problems


def cmd_upstream(args) -> int:
    hdp = Path(args.hdp).read_text(encoding="utf-8").replace("\r\n", "\n")
    skill = Path(args.skill).read_text(encoding="utf-8").replace("\r\n", "\n")
    return report(upstream_problems(hdp, skill), "upstream: the constants match a73d6df")


# ---------------------------------------------------------------- selftest


def _fixture_hdp(eol: bytes = b"\r\n", m3: str = "plain") -> bytes:
    m3_lines = (
        ["- M-3 covers edits to this list and to this protocol: they are human-approved, never", "  autonomous."]
        if m3 == "plain"
        else M3_CLAUSE
        if m3 == "clause"
        else ["- M-3 covers edits to this list and to this protocol: they are sometimes autonomous."]
    )
    text = [
        "# Protocol",
        "",
        "## 4. Synthesis",
        "",
        "## 4a. Mandatory-human criteria",
        "",
        "| M-3 | policy | x |",
        "| M-5 | a | x |",
        "| M-6 | b | x |",
        "| M-8 | c | x |",
        "",
        *m3_lines,
        "- An M hit names every matching item.",
        "",
        "## 5. Decision Brief",
        "",
        "Advisory, not authorizing.",
        "",
        "---",
        "",
        "## 6. Recording — every decision leaves a trail",
        "",
        "A decision resolved autonomously in planning and later overturned by the human is recorded, not",
        "deleted: append the ruling with `human_message_reference` and keep the original reasoning.",
        "",
        "---",
        "",
        "## 7. Basis",
        "",
    ]
    return b"".join(t.encode("utf-8") + eol for t in text)


def selftest() -> int:
    failures = []

    def expect(name: str, cond: bool) -> None:
        print(f"{'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            failures.append(name)

    def raises(fn) -> bool:
        try:
            fn()
        except Stop:
            return True
        return False

    base = _fixture_hdp()
    done = hdp_apply(base)
    expect("hdp apply inserts §5a, the clause and the hand-over", b"## 5a." in done and b"under \xc2\xa76." in done and b"Handed to the agent" in done)
    expect("hdp apply is idempotent", hdp_apply(done) == done)
    expect("hdp apply keeps CRLF only", eol_counts(done)[1] == 0 and eol_counts(done)[0] > eol_counts(base)[0])
    expect("hdp §5a sits right before §6", done.index(b"## 5a.") < done.index(b"## 6.") and done.index(b"## 5.") < done.index(b"## 5a."))
    expect("hdp hand-over follows the overturn paragraph", done.index(b"keep the original reasoning.") < done.index(b"A ruling that the human hands"))
    expect("hdp delta accepts the planned file", delta_problems(HDP, base, done) == [])
    expect("hdp delta refuses one stray byte", delta_problems(HDP, base, done.replace(b"Holds", b"Hold", 1)) != [])
    expect("hdp delta refuses a moved hand-over", delta_problems(HDP, base, done.replace(b"\r\n---\r\n\r\n## 7.", b"\r\n## 7.")) != [])
    expect("hdp clause form at baseline is accepted", hdp_apply(_fixture_hdp(m3="clause")) == done)
    expect("hdp unknown M-3 form is S1", raises(lambda: hdp_apply(_fixture_hdp(m3="other"))))
    expect("hdp without §4a is S1", raises(lambda: hdp_apply(base.replace(b"## 4a.", b"## 4b."))))
    expect("hdp without the M-8 row is S1", raises(lambda: hdp_apply(base.replace(b"| M-8 |", b"| M-9 |"))))
    expect("hdp without the overturn paragraph is S1", raises(lambda: hdp_apply(base.replace(b"later overturned", b"later reversed"))))
    expect("hdp with a different §5a is S1", raises(lambda: hdp_apply(done.replace(b"Holds", b"Hold", 1))))
    expect("hdp LF fixture stays LF", eol_counts(hdp_apply(_fixture_hdp(b"\n")))[0] == 0)

    routing = (
        "# Model & CLI Routing\r\n\r\nThe local overlay adds five classes and more.\r\n\r\n"
        "| Role | Class | Scope |\r\n|---|---|---|\r\n| Independent reviewer | `avkit_independent_reviewer` | x |\r\n\r\n"
        "| Task | Route | Effort |\r\n|---|---|---|\r\n| Classification | `avkit_router` if authorized | low |\r\n"
    ).encode()
    r2 = apply_file(ROUTING, routing)
    expect("routing gains the class count and both rows", b"six classes" in r2 and ROUTING_STACK_ROW.encode() in r2 and ROUTING_DISPATCH_ROW.encode() in r2)
    expect("routing apply is idempotent", apply_file(ROUTING, r2) == r2)
    expect("routing without its anchor is S1", raises(lambda: apply_file(ROUTING, routing.replace(b"| Classification |", b"| Classify |"))))
    deleg = (
        "# Delegation\r\nline5 lf\n- **Never delegate** x\r\n  y.\r\n- **Open decisions.** The coordinator owns each question.\r\n"
        "  A subagent returns it.\r\n\r\n## Why\r\n"
    ).encode()
    d2 = apply_file(DELEGATION, deleg)
    expect("delegation bullet lands after the Open decisions bullet", d2.index(b"A subagent returns it.") < d2.index(b"- **Peer reviewer.**") < d2.index(b"## Why"))
    expect("delegation keeps its one bare LF", eol_problems(DELEGATION, deleg, d2) == [])
    expect("delegation without Open decisions is S1 (Session 85 not landed)", raises(lambda: apply_file(DELEGATION, deleg.replace(b"Open decisions", b"Other"))))
    cli = ("x\r\n" + CLI_OLD + " More.\r\n").encode()
    expect("cli-dispatch line is replaced once", apply_file(CLI_SKILL, cli).count(CLI_NEW.encode()) == 1)
    expect("cli-dispatch with two old lines is S1", raises(lambda: apply_file(CLI_SKILL, cli + cli)))
    overlay = b"extends: global\r\nclasses:\r\n  avkit_router:\r\n    contract: {}\r\n"
    o2 = apply_file(OVERLAY, overlay)
    expect("overlay gains the block, CRLF", o2.startswith(overlay) and o2.endswith(b"effort: high}\r\n") and eol_counts(o2)[1] == 0)
    expect("overlay delta refuses an edit above the block", delta_problems(OVERLAY, overlay, o2.replace(b"avkit_router", b"avkit_routers")) != [])
    cb = json.dumps({"classes": {"avkit_router": {"x": 1}}, "extends": "global"}, indent=2).encode() + b"\n"
    cn = json.dumps({"classes": {"avkit_router": {"x": 1}, "avkit_peer_reviewer": COMPILED_CLASS}, "extends": "global"}, indent=2).encode() + b"\n"
    expect("compiled JSON adding only the class is accepted", compiled_problems(cb, cn) == [])
    expect("compiled JSON with a changed class is refused", compiled_problems(cb, cn.replace(b'"x": 1', b'"x": 2')) != [])
    expect("compiled JSON with CRLF is refused", compiled_problems(cb, cn.replace(b"\n", b"\r\n")) != [])

    def census_fixture(lines_json: list[int], lines_yaml: list[int]) -> bytes:
        rows = [census_row(COMPILED, n, f"json{n}") for n in lines_json]
        rows += [census_row(OVERLAY, n, f"yaml{n}") for n in lines_yaml]
        objs = [o for n in lines_json for o in census_object(COMPILED, n, f"json{n}")]
        objs += [o for n in lines_yaml for o in census_object(OVERLAY, n, f"yaml{n}")]
        objs += ["    {", '      "path": "z"', "    }"]
        text = ["# Census", "", "| Path:line | c | r | t |", "|---|---|---|---|", *rows, "", "```json", '{"matches": [', *objs, "]}", "```"]
        return b"".join(t.encode("utf-8") + b"\r\n" for t in text)

    cen = census_fixture([7, 58, 78, 94, 98], [52])
    c2 = apply_file(CENSUS, cen)
    cj = c2.decode("utf-8")
    new_shas = ("53b2ac7e120ec7c408f2d39da6f2fed179c03c5bae29b26b71eeb69ab76dc586", "6fef92aea84bd893bf4a8bb4665ae51aa4246fc573de306654ea7a1ab2921ea2")
    expect("census gains both rows and both objects", cj.count(CENSUS_NEW_JSON) == 1 and cj.count(CENSUS_NEW_YAML) == 1 and all(cj.count(h) == 1 for h in new_shas))
    expect("census renumbers the three moved rows and objects", all(f"{COMPILED}:{n}` |" in cj and f'"line": {n},' in cj for n in (97, 113, 117)) and f"{COMPILED}:94` |" not in cj and f"{COMPILED}:98` |" not in cj)
    expect("census rows stay in line order", cj.index(f"{COMPILED}:58`") < cj.index(census_row(COMPILED, 78, CENSUS_NEW_JSON)) < cj.index(f"{COMPILED}:97`") < cj.index(f"{COMPILED}:113`"))
    expect("census objects stay in line order", cj.index('"line": 58,') < cj.index(new_shas[0]) < cj.index('"line": 97,') < cj.index('"line": 113,'))
    expect("census apply is idempotent", apply_file(CENSUS, c2) == c2)
    expect("census keeps CRLF only", eol_counts(c2)[1] == 0 and eol_problems(CENSUS, cen, c2) == [])
    expect("census delta accepts the planned file", delta_problems(CENSUS, cen, c2) == [])
    expect("census delta refuses a stray byte", delta_problems(CENSUS, cen, c2.replace(b'"line": 113,', b'"line": 112,')) != [])
    expect("census without the line-98 match is S1", raises(lambda: apply_file(CENSUS, census_fixture([7, 58, 78, 94], [52]))))
    expect("census without the yaml line-52 match is S1", raises(lambda: apply_file(CENSUS, census_fixture([7, 58, 78, 94, 98], [43]))))

    expect("eol refuses a new bare LF", eol_problems(HDP, base, done.replace(b"\r\n## 6.", b"\n## 6.")) != [])
    expect("eol refuses CR in a new file", eol_problems(SKILL, None, b"a\r\nb\n") != [])
    expect("eol accepts the planned HDP", eol_problems(HDP, base, done) == [])

    bad = [("t", "Opus 5.5 reviews it"), ("t", "Resolve-AgentModel --class builder -Harness x"), ("t", "Fallback: Claude")]
    expect("govern refuses the three patterns", len(govern_lines(bad)) == 3)
    expect("govern accepts a historical observation", govern_lines([("t", "Historical observation (2026-11-15): Opus 5.5 was measured.")]) == [])
    good = [(f"agent:{n}", t) for n, t in enumerate(agent_expected("a" * 64, "b" * 64).split("\n"), 1)]
    good += [(f"skill:{n}", t) for n, t in enumerate(SKILL_TEXT.split("\n"), 1)]
    good += [("rows", t) for t in [ROUTING_STACK_ROW, ROUTING_DISPATCH_ROW, COMMANDS_ROW, README_ROW, CLI_NEW, *DELEGATION_PEER, *EXPECTED_5A, *HANDOVER]]
    expect("govern accepts every planned line", govern_lines(good) == [])

    reg, ovl = "a" * 64, "b" * 64
    agent = agent_expected(reg, ovl).encode()
    expect("newfiles accepts the planned bytes", newfile_problems(SKILL_TEXT.encode(), agent, reg, ovl) == [])
    expect("newfiles refuses a stale overlay sha", newfile_problems(SKILL_TEXT.encode(), agent, reg, "c" * 64) != [])
    expect("newfiles refuses Write in the tools", newfile_problems(SKILL_TEXT.encode(), agent.replace(b"Bash\n", b"Bash, Write\n"), reg, ovl) != [])
    expect("newfiles refuses a missing skill", newfile_problems(None, agent, reg, ovl) != [])

    shas = {"a.md": "1", "other.md": "2"}
    ok = scope_problems("h", "h", {HDP: " M", "a.md": " M", f"{PLAN}/task.md": "??"}, {"a.md": "1", HDP: "9"}, lambda p: shas.get(p, "x"))
    expect("scope accepts planned, project and unchanged baseline-dirty paths", ok == [])
    expect("scope refuses a moved HEAD", scope_problems("h2", "h", {}, {}, lambda p: "x") != [])
    expect("scope refuses a changed baseline-dirty path", scope_problems("h", "h", {"a.md": " M"}, {"a.md": "0"}, lambda p: shas[p]) != [])
    expect("scope refuses a new unplanned path", scope_problems("h", "h", {"other.md": " M"}, {}, lambda p: shas[p]) != [])
    expect("scope refuses a baseline-dirty path that is now clean", scope_problems("h", "h", {}, {"a.md": "1"}, lambda p: "x") != [])

    up = Path("C:/Temp/av-kit/s86/plan-time/upstream-hdp-a73d6df.md")
    upskill = Path("C:/Temp/av-kit/s86/plan-time/upstream-expert-pass-SKILL.md")
    if up.is_file() and upskill.is_file():
        uh = up.read_text(encoding="utf-8")
        us = upskill.read_text(encoding="utf-8")
        expect("upstream accepts the a73d6df text", upstream_problems(uh, us) == [])
        expect("upstream refuses an edited §5a", upstream_problems(uh.replace("is the only skip", "is a skip"), us) != [])
    else:
        print("skip upstream fixtures: plan-time copies absent")
    print(f"selftest: {len(failures)} failure(s)")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("anchors", "baseline", "newfiles", "eol", "govern", "scope", "selftest"):
        sub.add_parser(name)
    d = sub.add_parser("delta")
    d.add_argument("--only", action="append", help="limit to this path; repeatable")
    u = sub.add_parser("upstream")
    u.add_argument("--hdp", required=True)
    u.add_argument("--skill", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    return {
        "anchors": cmd_anchors,
        "baseline": cmd_baseline,
        "delta": cmd_delta,
        "newfiles": cmd_newfiles,
        "eol": cmd_eol,
        "govern": cmd_govern,
        "scope": cmd_scope,
        "upstream": cmd_upstream,
    }[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
