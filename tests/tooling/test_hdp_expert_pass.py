"""HDP expert pass (HDP §5a), the hand-over ruling, the expert-pass skill and the advisory peer
reviewer class and agent (Session 86, docs/execution/plans/2026-11-15-hdp-expert-pass).

Each test has a check function that returns a list of problems. It asserts that its file exists,
that the real file gives no problems, and that a mutated copy gives at least one.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HDP = ROOT / ".agent/docs/human-decision-protocol.md"
SKILL = ROOT / ".agent/skills/expert-pass/SKILL.md"
COMMANDS = ROOT / ".agent/docs/commands.md"
SKILLS_README = ROOT / ".agent/skills/README.md"
ROUTING = ROOT / ".agent/docs/model-routing.md"
DELEGATION = ROOT / ".agent/docs/model-delegation.md"
CLI_SKILL = ROOT / ".agent/skills/cli-dispatch/SKILL.md"
CLI_WORKFLOW = ROOT / ".agent/workflows/cli-dispatch.md"
OVERLAY = ROOT / ".agent/model-registry.local.yaml"
COMPILED = ROOT / ".agent/model-registry.local.json"
AGENT = ROOT / ".claude/agents/av-kit-peer-reviewer.md"
RESOLVER = Path("P:/.agent/tools/resolve_model.py")

H5A = "## 5a. Expert pass — one review of a set of briefs"
OPENING_END = 'A reference to this step says "HDP §5a".'
QUESTIONS = (
    "Does it add work that the present stage does not need?",
    "Can it be done as written, at the present size?",
    "Can it be undone?",
)
CLOSING = (
    "`Expert pass: inline.`",
    "`Expert pass: inline, not independent.`",
    "`Expert pass: not run: the human said to skip it.`",
    "There is no floor and no skip rule by set size.",
)
MODEL_OR_EFFORT = re.compile(
    r"(?i)\b(opus|sonnet|haiku|fable|gpt|codex|gemini|grok|claude)\b|\b(xhigh|high|medium|low)\b"
)
OVERTURN = (
    "A decision resolved autonomously in planning and later overturned by the human"
    " is recorded, not deleted"
)
HANDOVER = (
    "A ruling that the human hands to the agent for one brief set is the agent's ruling."
    " Record it with `resolution: autonomous` and the agent's own basis tag,"
    " never `Human-approved`, and keep the entry's `mandatory:` list."
    " The reasoning starts with `Handed to the agent: USER_EXPLICIT <date> '<quote>'.`,"
    " and that quote meets the gate. An acceptance criterion that rests on the ruling"
    " carries the same tag. The hand-over covers one set only, and only an item with"
    " no M hit or with M-3, M-5, M-6 or M-8; every other item of §4a stays the human's."
    " One line from the human overturns it."
)
M3_CLAUSE = (
    "- M-3 covers edits to this list and to this protocol: they are human-approved, never"
    " autonomous, except a ruling that the human hands to the agent under §6."
)
M3_PLAIN = (
    "- M-3 covers edits to this list and to this protocol: they are human-approved,"
    " never autonomous."
)
READ_ONLY_LINE = '"Read only. Do not edit, write or create a file. Return the result as text."'
CLI_OLD = (
    "Only avkit_coordinator, avkit_builder, avkit_verifier, avkit_router"
    " and avkit_independent_reviewer are adopted local classes."
)
CLI_NEW = (
    "Only avkit_coordinator, avkit_builder, avkit_verifier, avkit_router,"
    " avkit_independent_reviewer and avkit_peer_reviewer are adopted local classes;"
    " avkit_peer_reviewer is the in-harness Claude Code agent for the HDP §5a expert pass,"
    " not a CLI dispatch route."
)
EXISTING_CLASSES = {
    "avkit_builder",
    "avkit_coordinator",
    "avkit_independent_reviewer",
    "avkit_router",
    "avkit_verifier",
}
INDEPENDENT_SHA = "1ed3856c5a069cedd24c1d63d06e33afaa7915d6bf0d021bcebdc20002a3f4bd"
FALLBACK_GEMINI = re.compile(r"(?im)^.*(?:default reviewer|fallback)\s*:\s*(?:GPT-|Gemini)")


# ------------------------------------------------ helpers


def flat(text: str) -> str:
    return " ".join(text.split())


def read(path: Path) -> str:
    assert path.is_file(), f"required file missing: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def section(lines: list[str], start: int) -> list[str]:
    """The section whose heading is ``lines[start]``, up to the next ``## `` heading."""
    end = start + 1
    while end < len(lines) and not lines[end].startswith("## "):
        end += 1
    return lines[start:end]


def paragraphs(lines: list[str]) -> list[str]:
    out, cur = [], []
    for line in lines:
        if line.strip():
            cur.append(line)
        elif cur:
            out.append(flat(" ".join(cur)))
            cur = []
    if cur:
        out.append(flat(" ".join(cur)))
    return out


def section_5a(text: str) -> list[str] | None:
    lines = text.split("\n")
    hits = [i for i, line in enumerate(lines) if line == H5A]
    return section(lines, hits[0]) if len(hits) == 1 else None


def steps(sec: list[str]) -> dict[int, str]:
    """Numbered steps of a section: number -> the flattened step with its indented lines."""
    out: dict[int, str] = {}
    cur = None
    for line in sec:
        m = re.match(r"^(\d)\. ", line)
        if m:
            cur = int(m.group(1))
            out[cur] = line
        elif cur is not None and line.startswith("   ") and line.strip():
            out[cur] += " " + line
        else:
            cur = None
    return {k: flat(v) for k, v in out.items()}


def resolve(class_name: str, harness: str) -> subprocess.CompletedProcess:
    assert RESOLVER.is_file(), f"required resolver missing: {RESOLVER}"
    return subprocess.run(
        [
            sys.executable,
            str(RESOLVER),
            "resolve",
            class_name,
            "--harness",
            harness,
            "--project",
            str(ROOT),
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        env=os.environ
        | {"RECEIPTS_DIR": "C:/Temp/av-kit", "AGENT_MODEL_REGISTRY_HOME": "P:/.agent"},
        check=False,
    )


# ------------------------------------------------ AC-1 to AC-4: the HDP


def check_5a_place(text: str) -> list[str]:
    lines = text.split("\n")
    problems = []
    heads = [i for i, line in enumerate(lines) if line == H5A]
    if len(heads) != 1:
        return [f"the §5a heading appears {len(heads)} times, expected 1"]
    i5a = heads[0]
    five = [i for i, line in enumerate(lines) if line.startswith("## 5.")]
    six = [i for i, line in enumerate(lines) if line.startswith("## 6.")]
    if len(five) != 1 or len(six) != 1:
        return [f"headings '## 5.' x{len(five)} and '## 6.' x{len(six)}, expected one each"]
    if not five[0] < i5a < six[0]:
        problems.append("§5a is not between '## 5.' and '## 6.'")
    if any(line.startswith("## ") for line in lines[i5a + 1 : six[0]] if six[0] > i5a):
        problems.append("another heading stands between §5a and '## 6.'")
    paras = paragraphs(section(lines, i5a)[1:])
    if not paras or not paras[0].endswith(OPENING_END):
        problems.append("§5a's opening paragraph does not end with the HDP §5a reference line")
    return problems


def check_5a_steps(text: str) -> list[str]:
    sec = section_5a(text)
    if sec is None:
        return ["§5a heading missing or repeated"]
    got = steps(sec)
    problems = []
    if sorted(got) != [1, 2, 3, 4, 5, 6]:
        problems.append(f"§5a steps are {sorted(got)}, expected 1 to 6")
    one = got.get(1, "")
    for needle in ("`avkit_peer_reviewer`", "`.agent/skills/expert-pass/SKILL.md`"):
        if needle not in one:
            problems.append(f"step 1 does not name {needle}")
    for q in QUESTIONS:
        if q not in got.get(2, ""):
            problems.append(f"step 2 lacks the question {q!r}")
    if "`Expert pass (fresh context):" not in got.get(6, ""):
        problems.append("step 6 lacks the set line 'Expert pass (fresh context):'")
    return problems


def check_5a_closing(text: str) -> list[str]:
    sec = section_5a(text)
    if sec is None:
        return ["§5a heading missing or repeated"]
    paras = paragraphs(sec[1:])
    problems = []
    closing = paras[-1] if paras else ""
    for needle in CLOSING:
        if needle not in closing:
            problems.append(f"§5a's closing paragraph lacks {needle!r}")
    for n, line in enumerate(sec):
        m = MODEL_OR_EFFORT.search(line)
        if m:
            problems.append(f"§5a line {n} names a model or effort: {m.group(0)!r}")
    return problems


def check_handover(text: str) -> list[str]:
    lines = text.split("\n")
    problems = []
    whole = flat(text)
    if whole.count(HANDOVER) != 1:
        problems.append(
            f"the hand-over paragraph appears {whole.count(HANDOVER)} times, expected 1"
        )
    six = [i for i, line in enumerate(lines) if line.startswith("## 6.")]
    if len(six) != 1:
        return problems + [f"'## 6.' heading appears {len(six)} times"]
    paras = paragraphs(section(lines, six[0])[1:])
    at = [k for k, p in enumerate(paras) if p.startswith(OVERTURN)]
    if len(at) != 1:
        problems.append(f"the overturn paragraph appears {len(at)} times in §6, expected 1")
    elif at[0] + 1 >= len(paras) or paras[at[0] + 1] != HANDOVER:
        problems.append(
            "the paragraph right after the overturn paragraph in §6 is not the hand-over"
        )
    if whole.count(M3_CLAUSE) != 1:
        problems.append(
            f"the M-3 note in its clause form appears {whole.count(M3_CLAUSE)} times, expected 1"
        )
    if M3_PLAIN in whole:
        problems.append("the M-3 note appears in its plain form")
    return problems


def test_ac_1_section_5a_heading_sits_right_before_section_6():
    text = read(HDP)
    assert check_5a_place(text) == []
    lines = text.split("\n")
    i5a = lines.index(H5A)
    sec = section(lines, i5a)
    rest = lines[:i5a] + lines[i5a + len(sec) :]
    six = next(i for i, line in enumerate(rest) if line.startswith("## 6."))
    moved = rest[: six + 1] + sec + rest[six + 1 :]
    assert check_5a_place("\n".join(moved))
    twice = lines[:i5a] + sec + lines[i5a:]
    assert check_5a_place("\n".join(twice))


def test_ac_2_section_5a_has_six_steps_naming_the_class_and_skill():
    text = read(HDP)
    assert check_5a_steps(text) == []
    assert SKILL.is_file(), "step 1 names .agent/skills/expert-pass/SKILL.md, which must exist"
    assert check_5a_steps(text.replace("(`avkit_peer_reviewer`)", "(`peer_reviewer`)"))
    assert check_5a_steps(text.replace(" Can it be undone?", ""))


def test_ac_3_section_5a_closing_names_no_model_and_no_floor():
    text = read(HDP)
    assert check_5a_closing(text) == []
    assert check_5a_closing(
        text.replace("advisory peer reviewer", "advisory peer reviewer on Opus", 1)
    )
    assert check_5a_closing(
        text.replace(
            "There is no floor and no skip rule by set size.",
            "A set of fewer than three briefs gets no pass.",
        )
    )


def test_ac_4_handover_paragraph_follows_the_overturn_paragraph():
    text = read(HDP)
    assert check_handover(text) == []
    lines = text.split("\n")
    first = next(
        i for i, line in enumerate(lines) if line.startswith("A ruling that the human hands")
    )
    block = lines[first - 1 : first + 7]
    rest = lines[: first - 1] + lines[first + 7 :]
    seven = next(i for i, line in enumerate(rest) if line.startswith("## 7."))
    moved = rest[: seven + 1] + block + rest[seven + 1 :]
    assert check_handover("\n".join(moved))
    plain = text.replace(
        "never\n  autonomous, except a ruling that the human hands to the agent under §6.",
        "never\n  autonomous.",
    )
    assert check_handover(plain)


# ------------------------------------------------ AC-6 and AC-7: the skill and the indexes


def check_skill(text: str) -> list[str]:
    lines = text.split("\n")
    problems = []
    if lines[0] != "---" or "---" not in lines[1:]:
        return ["the skill has no frontmatter"]
    close = lines.index("---", 1)
    front = lines[1:close]
    if (
        len(front) != 2
        or front[0] != "name: expert-pass"
        or not front[1].startswith("description: ")
    ):
        problems.append(
            f"the frontmatter is {front!r}, expected name: expert-pass and one description"
        )
    packet = [i for i, line in enumerate(lines) if line == "## Packet"]
    after = [i for i, line in enumerate(lines) if line == "## After the pass"]
    if len(packet) != 1 or len(after) != 1:
        return problems + ["the skill lacks one '## Packet' and one '## After the pass'"]
    psec = section(lines, packet[0])
    if sorted(steps(psec)) != [1, 2, 3, 4, 5]:
        problems.append(f"the packet parts are {sorted(steps(psec))}, expected 1 to 5")
    paras = paragraphs(psec[1:])
    if not paras or not paras[-1].endswith(READ_ONLY_LINE):
        problems.append("the packet does not end with the read-only line")
    bullets = [line for line in section(lines, after[0]) if line.startswith("- ")]
    if len(bullets) != 4:
        problems.append(f"'## After the pass' has {len(bullets)} bullets, expected 4")
    if "`avkit_peer_reviewer`" not in text:
        problems.append("the skill does not name avkit_peer_reviewer")
    if "CLI Dispatch Decision Table" not in text:
        problems.append("the skill does not name the CLI Dispatch Decision Table")
    if "Quick decision guide" in text:
        problems.append("the skill names the 'Quick decision guide'")
    for n, line in enumerate(lines, 1):
        m = MODEL_OR_EFFORT.search(line)
        if m:
            problems.append(f"skill line {n} names a model or effort: {m.group(0)!r}")
    return problems


def check_commands(text: str) -> list[str]:
    lines = text.split("\n")
    hits = [i for i, line in enumerate(lines) if ".agent/skills/expert-pass/SKILL.md" in line]
    if len(hits) != 1:
        return [f"commands.md names the skill on {len(hits)} lines, expected 1"]
    i = hits[0]
    problems = []
    if not lines[i].startswith("| Expert Pass | "):
        problems.append("the commands.md line is not the Expert Pass table row")
    if i == 0 or not lines[i - 1].startswith(
        "| CLI Dispatch | `.agent/skills/cli-dispatch/SKILL.md` |"
    ):
        problems.append("the Expert Pass row is not right after the CLI Dispatch row")
    return problems


def check_readme(text: str) -> list[str]:
    lines = text.split("\n")
    hits = [i for i, line in enumerate(lines) if line.startswith("| `expert-pass/SKILL.md` |")]
    if len(hits) != 1:
        return [f"the skills README has {len(hits)} expert-pass rows, expected 1"]
    i = hits[0]
    if i == 0 or not lines[i - 1].startswith("| `cli-dispatch/SKILL.md` |"):
        return ["the expert-pass row is not right after the cli-dispatch row"]
    return []


def test_ac_6_expert_pass_skill_has_the_packet_and_after_the_pass():
    text = read(SKILL)
    assert check_skill(text) == []
    assert check_skill(text.replace("CLI Dispatch Decision Table", "Quick decision guide"))
    wrapped = '"Read only. Do not edit, write or create a file. Return the\nresult as text."'
    assert wrapped in text
    assert check_skill(text.replace(wrapped, '"Return the result as text."'))


def test_ac_7_commands_and_skills_readme_index_the_skill_once():
    commands = read(COMMANDS)
    readme = read(SKILLS_README)
    assert check_commands(commands) == []
    assert check_readme(readme) == []
    row = next(
        line for line in commands.split("\n") if ".agent/skills/expert-pass/SKILL.md" in line
    )
    assert check_commands(commands.replace(row, row + "\n" + row))
    rrow = next(
        line for line in readme.split("\n") if line.startswith("| `expert-pass/SKILL.md` |")
    )
    assert check_readme(readme.replace(rrow, rrow + "\n" + rrow))


# ------------------------------------------------ AC-8: routing, delegation and cli-dispatch


def check_routing(text: str) -> list[str]:
    lines = text.split("\n")
    problems = []
    if "adds six classes" not in text:
        problems.append("model-routing.md does not say 'adds six classes'")
    for heading in ("## The routed stack", "## CLI Dispatch Decision Table"):
        at = [i for i, line in enumerate(lines) if line == heading]
        if len(at) != 1:
            problems.append(f"{heading!r} found {len(at)} times")
            continue
        rows = [
            line
            for line in section(lines, at[0])
            if line.startswith("|") and "`avkit_peer_reviewer`" in line
        ]
        if len(rows) != 1:
            problems.append(f"{heading!r} has {len(rows)} avkit_peer_reviewer rows, expected 1")
    for line in lines:
        if "avkit_peer_reviewer" in line and "Gemini" in line:
            problems.append("an avkit_peer_reviewer line names Gemini")
    if FALLBACK_GEMINI.search(text):
        problems.append("model-routing.md names a Gemini default reviewer or fallback")
    return problems


def check_delegation(text: str) -> list[str]:
    lines = text.split("\n")
    peer = [i for i, line in enumerate(lines) if line.startswith("- **Peer reviewer.**")]
    opened = [i for i, line in enumerate(lines) if line.startswith("- **Open decisions.**")]
    if len(peer) != 1 or len(opened) != 1:
        return [
            f"model-delegation.md has {len(peer)} Peer reviewer"
            f" and {len(opened)} Open decisions bullets"
        ]
    if peer[0] < opened[0]:
        return ["the Peer reviewer bullet comes before the Open decisions bullet"]
    return []


def check_cli(text: str) -> list[str]:
    problems = []
    if text.count(CLI_NEW) != 1:
        problems.append(f"the six-class sentence appears {text.count(CLI_NEW)} times, expected 1")
    if CLI_OLD in text:
        problems.append("the five-class sentence is still present")
    return problems


def test_ac_8_routing_delegation_and_cli_dispatch_name_the_peer_reviewer():
    routing = read(ROUTING)
    delegation = read(DELEGATION)
    assert check_routing(routing) == []
    assert check_delegation(delegation) == []
    for path in (CLI_SKILL, CLI_WORKFLOW):
        assert check_cli(read(path)) == [], path
    assert check_routing(routing.replace("adds six classes", "adds five classes"))
    lines = delegation.split("\n")
    peer = next(i for i, line in enumerate(lines) if line.startswith("- **Peer reviewer.**"))
    block = lines[peer : peer + 4]
    rest = lines[:peer] + lines[peer + 4 :]
    opened = next(i for i, line in enumerate(rest) if line.startswith("- **Open decisions.**"))
    assert check_delegation("\n".join(rest[:opened] + block + rest[opened:]))
    assert check_cli(read(CLI_SKILL).replace(CLI_NEW, CLI_OLD))


# ------------------------------------------------ AC-9 and AC-10: the registry class


def check_resolution(
    peer: dict, class_out: dict, refusals: dict[str, tuple[int, str]]
) -> list[str]:
    problems = []
    for key in ("catalog_id", "effort"):
        if class_out.get(key) != peer.get(key):
            problems.append(
                f"{key} {class_out.get(key)!r} differs from peer_reviewer's {peer.get(key)!r}"
            )
    if class_out.get("vendor") != "anthropic":
        problems.append(f"vendor is {class_out.get('vendor')!r}, expected anthropic")
    for harness, (code, output) in refusals.items():
        if code == 0 or "unresolvable_on_harness" not in output:
            problems.append(f"{harness} did not refuse with unresolvable_on_harness (exit {code})")
    return problems


def test_ac_9_peer_reviewer_class_resolves_only_on_claude_code_agents():
    peer = resolve("peer_reviewer", "claude-code-agents")
    assert peer.returncode == 0, peer.stdout + peer.stderr
    got = resolve("avkit_peer_reviewer", "claude-code-agents")
    assert got.returncode == 0, got.stdout + got.stderr
    refusals = {}
    for harness in ("cursor-task", "codex-cli", "claude-p"):
        r = resolve("avkit_peer_reviewer", harness)
        refusals[harness] = (r.returncode, r.stdout + r.stderr)
    peer_out, class_out = json.loads(peer.stdout), json.loads(got.stdout)
    assert check_resolution(peer_out, class_out, refusals) == []
    assert check_resolution(peer_out, class_out, {"cursor-task": (0, "{}")})


def check_compiled(compiled: dict) -> list[str]:
    problems = []
    classes = compiled.get("classes", {})
    if set(classes) != EXISTING_CLASSES | {"avkit_peer_reviewer"}:
        problems.append(f"compiled classes are {sorted(classes)}")
    independent = json.dumps(
        classes.get("avkit_independent_reviewer"), sort_keys=True, separators=(",", ":")
    )
    if hashlib.sha256(independent.encode("utf-8")).hexdigest() != INDEPENDENT_SHA:
        problems.append("avkit_independent_reviewer differs from its plan-time compiled form")
    return problems


def test_ac_10_compiled_registry_is_current_and_adds_only_the_peer_reviewer():
    assert OVERLAY.is_file() and COMPILED.is_file()
    result = subprocess.run(
        [
            sys.executable,
            str(RESOLVER),
            "validate",
            "--overlay",
            ".agent/model-registry.local.yaml",
            "--check-compiled",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        env=os.environ
        | {"RECEIPTS_DIR": "C:/Temp/av-kit", "AGENT_MODEL_REGISTRY_HOME": "P:/.agent"},
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    compiled = json.loads(COMPILED.read_text(encoding="utf-8"))
    assert check_compiled(compiled) == []
    mutated = json.loads(json.dumps(compiled))
    mutated["classes"]["avkit_independent_reviewer"]["contract"]["effort_default"] = "low"
    assert check_compiled(mutated)


# ------------------------------------------------ AC-11: the agent


def check_agent(data: bytes) -> list[str]:
    problems = []
    if b"\r" in data:
        problems.append("the agent file holds CR")
    lines = data.decode("utf-8").replace("\r", "").split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        return problems + ["the agent has no frontmatter"]
    close = lines.index("---", 1)
    front = dict(line.split(": ", 1) for line in lines[1:close] if ": " in line)
    if [line.split(":", 1)[0] for line in lines[1:close]] != [
        "name",
        "description",
        "model",
        "effort",
        "tools",
    ]:
        problems.append(
            f"frontmatter keys are {[line.split(':', 1)[0] for line in lines[1:close]]}"
        )
    want = {"name": "av-kit-peer-reviewer", "effort": "high", "tools": "Read, Grep, Glob, Bash"}
    for key, value in want.items():
        if front.get(key) != value:
            problems.append(f"frontmatter {key} is {front.get(key)!r}, expected {value!r}")
    head = lines[close + 1 : close + 4]
    if len(head) < 3 or not re.fullmatch(r"<!-- AUTOGEN: model-registry [0-9a-f]{64} -->", head[0]):
        problems.append("the line after the frontmatter is not the AUTOGEN line")
    else:
        local = head[1]
        if not (
            local.startswith("<!-- Local class: avkit_peer_reviewer;")
            and "P:/av-kit" in local
            and re.search(r"overlay_sha256: [0-9a-f]{64}\.", local)
            and "Do not run global sync" in local
        ):
            problems.append("the local-class comment is missing or incomplete")
        if head[2] != "# av-kit-peer-reviewer":
            problems.append("the title does not follow the local-class comment")
    text = "\n".join(lines)
    for needle in ("never writes a verdict file", "avkit_independent_reviewer"):
        if needle not in text:
            problems.append(f"the agent does not say {needle!r}")
    return problems


def test_ac_11_peer_reviewer_agent_has_the_registry_header():
    assert AGENT.is_file(), f"required file missing: {AGENT.relative_to(ROOT)}"
    data = AGENT.read_bytes()
    assert check_agent(data) == []
    assert check_agent(
        data.replace(b"tools: Read, Grep, Glob, Bash", b"tools: Read, Write, Grep, Glob, Bash")
    )
    assert check_agent(data.replace(b"---\n<!-- AUTOGEN", b"---\n\n<!-- AUTOGEN"))
