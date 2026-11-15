"""Session 85 hdp-v2-protocol oracle (implementation-plan.md §Verification Plan). Read-only.

Checks the protocol rewrite and every file that cites the protocol, against the base commit:

* C1  every protocol section citation in the live tree resolves to §1-§7 or §4a;
* C2  the stale phrases are gone from the live tree (two only from the protocol);
* C3  the protocol's structure: headings, §4 word-equal to the base, §4a (each M row's own
      criterion and source, M_ROWS), Brief v2, §6, §7, the av-kit sweep table, rg receipts and
      research ladder kept;
* C4  the required new text in AGENTS, model-delegation, create-plan, session-grouping and
      the four templates;
* C5  the template twins are byte-identical;
* C6  each edited file keeps its working-tree line endings against the row-0 --eol-snapshot
      (bare-LF count unchanged; model-delegation's LF-only line stays LF);
* C7  AGENTS.md size and line count, and the rule-preservation postimage digest;
* C8  no uncensused numeric model name in an edited file (verify_adoption's census rule);
* C9  the handoff template's Decision Log is one comment plus one yaml block;
* C10 the issue-lifecycle-guide boxes keep their line lengths;
* C11 (with --binding) each §6 validator clause fixed in TOPICS is stated and proved by its
      fixed Session 84 selftest arms or tests, or dropped with all its evidence absent.

``--selftest`` builds a synthetic all-green tree from the same required texts, proves it
passes, then plants one fault per rule and requires the named check to refuse it.
Run from anywhere; the repository root is four levels up. Exit 0 = pass, 1 = fail.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE_DEFAULT = "6813232d8769be71eb6e72505b6f39c58c11bddd"

PROTOCOL = ".agent/docs/human-decision-protocol.md"
AGENTS = "AGENTS.md"
DELEGATION = ".agent/docs/model-delegation.md"
CREATE_PLAN = ".agent/workflows/create-plan.md"
GROUPING_WF = ".agent/workflows/session-grouping.md"
LIFECYCLE_GUIDE = ".agent/docs/issue-lifecycle-guide.md"
ADOPTION = "docs/execution/plans/2026-09-26-framework-update-adoption"
RULE_MAP = f"{ADOPTION}/rule-preservation.md"
CENSUS = f"{ADOPTION}/routing-census.md"

PLAN_TPL = ".agent/templates/PLAN-TEMPLATE.md"
TASK_TPL = ".agent/templates/TASK-TEMPLATE.md"
HANDOFF_TPL = ".agent/templates/HANDOFF-TEMPLATE.md"
REFLECTION_TPL = ".agent/templates/REFLECTION-TEMPLATE.md"
TWINS = [
    (PLAN_TPL, "docs/execution/plans/PLAN-TEMPLATE.md"),
    (TASK_TPL, "docs/execution/plans/TASK-TEMPLATE.md"),
    (HANDOFF_TPL, ".agent/context/handoffs/TEMPLATE.md"),
    (REFLECTION_TPL, "docs/execution/reflections/TEMPLATE.md"),
]

EDITED = [
    AGENTS,
    PROTOCOL,
    DELEGATION,
    *[p for pair in TWINS for p in pair],
    CREATE_PLAN,
    ".agent/workflows/execution-session.md",
    ".agent/workflows/issue-triage.md",
    ".agent/workflows/next-project.md",
    ".agent/workflows/meu-handoff.md",
    ".agent/workflows/delegated-plan-creation.md",
    GROUPING_WF,
    ".agent/workflows/inspiration-research.md",
    ".agent/workflows/tdd-implementation.md",
    LIFECYCLE_GUIDE,
    ".agent/docs/commands.md",
    ".agent/docs/development-lifecycle.md",
    ".agent/docs/emerging-standards.md",
    ".agent/docs/cloud-local-collaboration.md",
    ".agent/skills/completion-preflight/SKILL.md",
    ".agent/skills/cli-dispatch/SKILL.md",
    RULE_MAP,
]

# The live tree. .agent/context (sessions, grouping, known issues, other handoffs) and
# .agent/fleet are history or other people's work, and are never walked.
LIVE_ROOTS = [
    "AGENTS.md",
    "GUARDRAILS.md",
    "PROJECT-PROFILE.md",
    "CLAUDE.md",
    ".agent/docs",
    ".agent/workflows",
    ".agent/skills",
    ".agent/templates",
    ".agent/roles",
    ".claude/agents",
    ".cursor/agents",
    ".agent/context/handoffs/TEMPLATE.md",
    ".agent/context/handoffs/REVIEW-TEMPLATE.md",
    "docs/execution/plans/PLAN-TEMPLATE.md",
    "docs/execution/plans/TASK-TEMPLATE.md",
    "docs/execution/reflections/TEMPLATE.md",
]
CITATION_EXTRA_ROOTS = ["tools"]  # C1 also reads tools' messages and comments.
DOC_SUFFIXES = {".md"}
CITATION_SUFFIXES = {".md", ".py", ".ps1"}
SKIP_DIRS = {"__pycache__", "fleet", "node_modules"}

VALID_SECTIONS = {"1", "2", "3", "4", "4a", "5", "6", "7"}

STALE_EVERYWHERE = [
    "default if unanswered",
    "if you do not answer",
    "and what happens without an answer",
    "every autonomous decision",
    "→ web research",
    "precedent sweep, web research",
    "web research via the harness",
    "**Web search** each surviving question",
    "prior decisions), web research",
    "reconciles it with the reflection",
    "reconciles every entry with the reflection",
    "row without Stage",
    "must appear in the consuming session's reflection",
    "carried into the closeout reflection",
    "becomes a row of the closeout reflection",
    "log the decision in the reflection's Decisions Log",
    "surface in the reflection's `### Decisions Log`",
    "and the reflection's Decisions Log",
    "and in the session reflection's",
    "and in the reflection's `### Decisions Log`",
    "The human reads it afterwards in the session",
]
STALE_PROTOCOL_ONLY = ["Anti-patterns", "Research basis"]

EXPECTED_H2 = [
    "## 1. Trigger",
    "## 2. Precedent sweep (codebase first)",
    "## 3. Research",
    "## 4. Synthesis and the obviousness test",
    "## 4a. Mandatory-human criteria",
    "## 5. Decision Brief — how a human-gated decision is presented",
    "## 6. Recording — every decision leaves a trail",
    "## 7. Basis",
]

FORBIDDEN_PROTOCOL = [
    "human-all",
    "run_parameters",
    "claude-credits",
    "gate-wait-then-exit",
    "SIGN 3 (a)",
    "§5a",
    "Handed to the agent",
    "lane branch",
    "{{PROJECT",
    "(§5f)",
    "TL;DR (§5e)",
]

PROTOCOL_HEAD_MARKERS = [
    "AskUserQuestion",
    "a subagent return that carries an open decision",
    "the round-cap TL;DR (§5d)",
    "(§5e)",
    "**Rule in one line:** decide before you ask.",
    "**It never loosens a hard gate.**",
]
S2_MARKERS = [
    "If a prior ruling settles the decision, apply it and cite it. "
    "Then no research is necessary.",
]
CURRENT_FOCUS_ROW = (
    "| `.agent/context/current-focus.md` | The current priority and the recent rulings "
    "of the user |"
)
S3_MARKERS = [
    "Research each open fact that can change the recommendation, before you decide or ask.",
    "A local measurement counts as research",
    "pomera_web_search",
    "`WebSearch`",
    "Codex `--search`",
    "research: unavailable",
    # plan review R1 Q1: the angles table applies to web research, not to every decision
    "When web research is needed, run 2–3 queries per decision, one per angle:",
    "| Angle | Query shape | Why |",
]
S4_OLD = "write the Decision Log entry (§6)"
S4_NEW = "record the decision as §6 tells you"
S4A_MARKERS = [
    "`hdp` is av-kit's only mode",
    "#authority-and-approval",
    "§Commits",
    "EGRESS_PRECEDENCE",
    "av-kit has no `stop_gate.py` or `commit_gate.py`",
    "`.agent/model-registry.local.yaml`",
    "§Testing & TDD Protocol",
    "§Planning Contract",
    "§Execution Contract",
    "`.agent/review-limits.json`",
    "§Validation Pipeline",
    "§Dual-Agent Workflow",
    "`harness-profiles.md`",
    "av-kit runs no headless sessions",
    "`GUARDRAILS.md` SIGN 3",
    "Five notes:",
    "*new decisions*",
    "M-3 covers edits to this list and to this protocol: they are human-approved, "
    "never autonomous.",
    "Nothing is exempt",
    "An M hit names every matching item",
    "do not ask the human to confirm a choice the obviousness test already settled",
]
# Each M row: (phrases its criterion cell must hold, phrases its own Source cell must hold).
# The phrases are upstream a73d6df's criterion wording kept by D-845, plus the av-kit
# adaptations named in implementation-plan.md §The §4a adaptation.
M_ROWS = {
    1: (["Push to any remote; a merge; tag; release; deploy."],
        ["#authority-and-approval", "§Commits"]),
    2: (["Destructive data operations",
         "deletion of backups; secret or credential rotation; a change to who may read a secret."],
        ["#authority-and-approval"]),
    3: (["**New policy**: a new or changed threshold, cap, budget, round cap or retention window",
         "`.agent/review-limits.json`", "`.agent/model-registry.local.yaml`",
         "av-kit has no `stop_gate.py` or `commit_gate.py`.",
         "A mechanical repair under existing policy"],
        ["§4 test 4"]),
    4: (["One-way doors not already in the approved plan",
         "**any** external spend that the approved plan did not declare"],
        ["`one-way-door`"]),
    5: (["A user-visible product fork with no local canon **and** materially different "
         "plausible behaviours"],
        ["`product-preference`"]),
    6: (["A source conflict that the Planning Contract order",
         "any conflict with a prior `USER_EXPLICIT` ruling"],
        ["`source-conflict`"]),
    7: (["A change to an existing test's assertion that no approved plan row specifically "
         "calls for", "The setup-and-fixture repair carve-out stays the agent's."],
        ["§Testing & TDD Protocol"]),
    8: (["A change to an approved plan's *acceptance or scope*",
         "Bookkeeping rows (a receipt, a status flip, an evidence row)"],
        ["§Planning Contract"]),
    9: (["Review-loop exits that are already sanctioned stops: every round cap, the stagnation "
         "rule, every reviewer rung unavailable."],
        ["§Execution Contract"]),
    10: (["A required **human action**",
          "A transient failure the plan authorizes the agent to retry"],
         ["`externally-blocked`"]),
    11: (["Waiving a **blocking** quality gate, test or review step",
          "Advisory floors (coverage, the security scans) stay advisory"],
         ["§Validation Pipeline", "§Dual-Agent Workflow"]),
    12: (["A new external disclosure: a push to a public repository"],
         ["#authority-and-approval"]),
    13: (["Widening the agent's own permissions: a settings allow rule"],
         ["`harness-profiles.md`"]),
    14: (["Headless start, resume or fork authority",
          "av-kit runs no headless sessions; starting one is this item."],
         ["`GUARDRAILS.md` SIGN 3"]),
}
# Upstream anchors that av-kit does not have (no such heading, no SIGN 3 (b)).
S4A_FORBIDDEN = ["§Authority and Approval", "§Independent Review", "SIGN 3 (b)"]
S5_ORDERED = [
    "**Two outcomes.**",
    "### D-n: <the question in plain words>",
    "**I recommend A: <what happens, in plain words>.**",
    "- B: <what happens, and what it costs compared with A.>",
    "- C: keep things as they are: <what that costs>.",
    "Refs: <precedent paths>, <sources>, <M-n>.",
    "**Plain words.**",
    "**Recommendation first.**",
    "unless the human ruled it out in words you can quote",
    "**The reader decides from the brief alone.**",
    "**Ask at plan time**",
    "**Without an answer**",
    "anthropics/claude-code#73125",
    "**Batch at the existing stop.**",
    "the §5d TL;DR",
    "**Advisory, not authorizing.**",
]
S6_MARKERS = [
    "Record each human ruling, and each consequential new choice or departure from "
    "precedent, once, in the log of the stage that made it.",
    "A decision that applies an existing ruling gets no new record.",
    "mandatory: [M-n, …] | none",
    "uses `stage: planning` and lists its unruled items under `open_decisions:`",
    "There is no other stage value and no class alias.",
    "The closeout reads each row with stage `grouping`.",
    "is a short list",
    "`None.` is valid",
    "A human ruling, a grouping row or an applied ruling does not go on the list.",
    "is recorded, not deleted",
]
S6_FORBIDDEN = ["**every** autonomous decision", "reconciles"]
S7_MARKERS = [
    "G24",
    "https://adr.github.io/madr/",
    "https://fs.blog/reversible-irreversible-decisions/",
    "2603.26233",
    "2610.24411",
]

AGENTS_OLD = (
    "Every question for the human, at any stage, is reached and presented per "
    "[.agent/docs/human-decision-protocol.md](.agent/docs/human-decision-protocol.md): precedent "
    "sweep → web research → obviousness test → Decision Brief with the recommendation first and a "
    "do-nothing option. Decisions the test settles are logged (plan/handoff Decision Log, "
    "reflection Decisions Log), not asked; the protocol never loosens a hard gate."
)
AGENTS_NEW = (
    "**Decide before you ask.** Before you put a question, a choice or a decision to the human, "
    "run [.agent/docs/human-decision-protocol.md](.agent/docs/human-decision-protocol.md). If it "
    "settles the decision, state your decision in one line and continue. If not, ask once, early, "
    "with your recommendation first and a do-nothing option, in plain words about outcomes, and "
    "name the precedent and the sources that you used. The protocol never loosens a hard gate."
)
DELEGATION_NEW = (
    "- **Open decisions.** The coordinator owns each question to the human. A subagent that finds "
    "an open decision returns it with its facts and a recommendation, and does not ask the human."
)
GROUPING_HEADER = (
    "| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the "
    "alternatives lost) | Human ref |"
)
CP_TEST_SEARCH = (
    "Search the tests for each string, number and field that the plan changes, and put the "
    "test changes into one question before the work starts."
)
REQUIRED_TEXT = {
    CREATE_PLAN: [
        "Also read `.agent/context/current-focus.md`. If a prior ruling settles the question, "
        "apply it and cite it.",
        "**Research** each open fact that can change the recommendation (protocol §3).",
        "A local measurement (git history, a test run, a simulation) counts as research",
        "pomera_web_search",
        "The Refs line cites the sources (precedent `path:line`, URL, doc path, or standard ID).",
        CP_TEST_SEARCH,
        "Record each autonomous resolution once, in the plan's `## Decision Log`.",
        "the closeout reads each declared D-row with stage `grouping`",
        "The human decides. The recommendation never self-executes.",
    ],
    GROUPING_WF: [GROUPING_HEADER, "reads each D-row with stage `grouping`"],
    PLAN_TPL: [
        "Record them per `.agent/docs/human-decision-protocol.md` §6.",
        "A decision that applies an existing ruling gets no new entry.",
        "**Decision Brief** in the protocol §5 form",
        "### D-n: <the question in plain words>",
        "**I recommend A: <what happens, in plain words>.**",
        "- C: keep things as they are: <what that costs>.",
        "Refs: <precedent paths>, <sources>, <M-n>.",
    ],
    REFLECTION_TPL: [
        "- _{the choice in plain words}_ — [D-1](_{path to the stage log}_)",
        "A human ruling, a grouping row or an applied ruling does not go on the list.",
    ],
    HANDOFF_TPL: [
        "Each human ruling and each consequential new choice of this MEU "
        "(.agent/docs/human-decision-protocol.md §6)",
        "The closeout validator checks each entry and refuses an example left unfilled.",
    ],
    TASK_TPL: [
        "Its Decisions Log lists only the reversible choices that the agent made without "
        "asking (protocol §6).",
    ],
}
FORBIDDEN_TEXT = {
    REFLECTION_TPL: ["| ID | Stage | Question |"],
    PLAN_TPL: ["**Recommendation:** {Option A}"],
    CREATE_PLAN: ["**Recommendation:** {Option A}"],
}

# §6 validator paragraph (D-850, amended after plan review R1). Row 1 writes this text into §6;
# implementation-plan.md §The §6 validator paragraph quotes it word for word (selftest-checked).
S6_VALIDATOR = (
    "`tools/validate_closeout_artifacts.py --reflection … --decision-source {plan} "
    "--decision-source {handoff} [--decision-source {grouping-file}] [--decision-source "
    "known-issues.yaml --decision-issue ID]` (task row H2-2) reads these records, and its "
    "messages cite this section. Each plan, handoff and issue entry must state the question, "
    "the choice and the reasoning as text, and a `chosen` that still starts with `pending` is "
    "refused. A quoted value is read without its trailing `# comment`, and a `#` inside the "
    "quotes is text. A double-quoted value is read after its escapes are decoded, so `\"\\n\"` "
    "is blank. Each grouping row must fill its Question and Reasoning cells, and a row "
    "ruled `autonomous` or `human` must give a Chosen that is filled and does not start with "
    "`pending`; an `open` row's Chosen is not read. Two logs must give one decision the same "
    "stage. The reflection's `### Decisions Log` is not compared with them: the check refuses "
    "only the template's example line left in place, and `None.` is valid. A `decision_log:` "
    "is read only from a fenced ```yaml or `~~~yaml` block, indented or not (a handoff's "
    "section is exactly `None.` or one such block, with the template's instruction comment and "
    "closing rule allowed around it); the key in prose or in any other fence except a "
    "```diff/```patch excerpt is refused rather than skipped. A source is a grouping by its "
    "`## 8. Open Decisions` heading (a heading inside a fence or an HTML comment is an "
    "example), or by being the file the plan's frontmatter declares as `grouping_source`, and "
    "a plan that declares one is refused unless that file is among the sources. A relative "
    "declaration resolves from the plan's project root: the nearest ancestor that holds "
    "`.agent/`, and never past the repository root (the first ancestor with `.git`). A handoff "
    "is known by its `plan_source` frontmatter or `handoff` filename, and `plan_source: null` "
    "or `~` is no value; a plan is anything else. A block outside the reader's bounded YAML "
    "grammar, a `decision_log:` nested under another key or inside a flow collection, a key "
    "written twice in one mapping, and a grouping table in an ad-hoc shape are refused rather "
    "than read as empty. `--decision-issue` is repeated once per issue; a named issue the file "
    "does not hold is refused, and naming one twice is a usage error. A decision that was made "
    "and written nowhere cannot be caught by a validator, so record it at the moment of "
    "deciding, not at closeout."
)

# C11 (D-850, D-855; fixed here after plan review R1, never supplied by the binding): each
# topic is (the §6 clause it states, the Session 84 evidence that proves it). `arm:<label>` is
# a passing line `  ok   <label> want=` of the closeout selftest receipt; every label is in the
# post-port arm set that Session 84's selftest-arms-check.py fixes (kept, flipped or added,
# never removed). `test:<file>::<prefix>` is a `<file>::<prefix>… PASSED` line of the
# `pytest -v` receipt; Session 84 names its tests `test_ac_<n>_…` after its own ACs.
RECORD_ONCE = "tests/tooling/test_closeout_record_once.py"
TOPICS: dict[str, tuple[str, list[str]]] = {
    "question-choice-reasoning": (
        "Each plan, handoff and issue entry must state the question, the choice and the "
        "reasoning as text",
        ["arm:decision-blank-reasoning-in-log-refused", "arm:decision-non-text-chosen-refused"]),
    "pending-refused": (
        "a `chosen` that still starts with `pending` is refused",
        ["arm:decision-pending-chosen-refused"]),
    "quoted-comment": (
        "A quoted value is read without its trailing `# comment`, and a `#` inside the quotes "
        "is text",
        ["arm:decision-commented-pending-chosen-refused",
         "arm:decision-commented-empty-chosen-refused", "arm:decision-quoted-hash-text-ok"]),
    # D-856 (execution, plan review R2 Q3 note): Session 84 decodes double-quoted escapes.
    "dq-escapes": (
        "A double-quoted value is read after its escapes are decoded, so `\"\\n\"` is blank",
        ["arm:decision-escaped-newline-reasoning-refused",
         "arm:decision-escaped-pending-chosen-refused",
         "arm:decision-escaped-blank-question-refused",
         "arm:decision-escaped-blank-chosen-refused", "arm:decision-escaped-text-ok"]),
    "grouping-row-fields": (
        "Each grouping row must fill its Question and Reasoning cells",
        [f"test:{RECORD_ONCE}::test_ac_3_", f"test:{RECORD_ONCE}::test_ac_4_"]),
    "grouping-ruled-chosen": (
        "a row ruled `autonomous` or `human` must give a Chosen that is filled and does not "
        "start with `pending`; an `open` row's Chosen is not read",
        ["arm:grouping-blank-chosen-refused", "arm:grouping-pending-chosen-refused",
         "arm:grouping-open-row-read"]),
    "same-stage": (
        "Two logs must give one decision the same stage",
        [f"test:{RECORD_ONCE}::test_ac_8_"]),
    "reflection-not-compared": (
        "The reflection's `### Decisions Log` is not compared with them",
        ["arm:reflection-decisions-log-link-list-ok", f"test:{RECORD_ONCE}::test_ac_7_"]),
    "template-example-refused": (
        "the check refuses only the template's example line left in place",
        ["arm:reflection-decisions-log-example-refused"]),
    "none-valid": (
        "left in place, and `None.` is valid",
        [f"test:{RECORD_ONCE}::test_ac_6_"]),
    "fenced-yaml-only": (
        "A `decision_log:` is read only from a fenced ```yaml or `~~~yaml` block, indented or not",
        ["arm:decision-tilde-yaml-fence-read", "arm:decision-indented-fence-read"]),
    "handoff-section-shape": (
        "a handoff's section is exactly `None.` or one such block",
        ["arm:handoff-separator-then-prose-refused", "arm:handoff-template-separator-none-ok"]),
    "prose-key-refused": (
        "the key in prose or in any other fence",
        ["arm:decision-bare-key-outside-fence-refused", "arm:handoff-decision-log-prose-refused",
         "arm:decision-text-fence-refused"]),
    "diff-patch-exemption": (
        "except a ```diff/```patch excerpt is refused rather than skipped",
        ["arm:decision-diff-excerpt-ignored-ok"]),
    "grouping-by-heading-or-declaration": (
        "A source is a grouping by its `## 8. Open Decisions` heading (a heading inside a fence "
        "or an HTML comment is an example), or by being the file the plan's frontmatter "
        "declares as `grouping_source`",
        ["arm:grouping-any-filename-read", "arm:grouping-declared-supplied-ok",
         "arm:grouping-fenced-example-before-real-section-read",
         "arm:plan-commented-heading-read-as-plan"]),
    "grouping-source-required": (
        "a plan that declares one is refused unless that file is among the sources",
        ["arm:grouping-declared-not-supplied-refused"]),
    "repo-boundary-root": (
        "A relative declaration resolves from the plan's project root: the nearest ancestor "
        "that holds `.agent/`, and never past the repository root (the first ancestor with "
        "`.git`)",
        ["arm:grouping-declared-root-resolved-read", "arm:grouping-declared-repo-boundary-read",
         "arm:grouping-declared-repo-boundary-outer-decoy-refused"]),
    "handoff-by-plan-source": (
        "A handoff is known by its `plan_source` frontmatter or `handoff` filename",
        ["arm:grouping-named-handoff-read-as-handoff"]),
    "null-plan-source": (
        "`plan_source: null` or `~` is no value; a plan is anything else",
        ["arm:grouping-plan-source-null-read-as-grouping", "arm:grouping-named-plan-read-as-plan"]),
    "bounded-grammar": (
        "A block outside the reader's bounded YAML grammar",
        ["arm:decision-unclosed-quote-refused"]),
    "nested-key-refused": (
        "a `decision_log:` nested under another key",
        ["arm:decision-nested-key-refused", "arm:decision-root-plus-nested-refused"]),
    "flow-collection-key": (
        "or inside a flow collection",
        ["arm:decision-flow-only-nested-refused", "arm:decision-root-plus-flow-nested-refused"]),
    "duplicate-key-refused": (
        "a key written twice in one mapping",
        ["arm:decision-duplicate-root-key-refused"]),
    "adhoc-grouping-refused": (
        "a grouping table in an ad-hoc shape are refused rather than read as empty",
        ["arm:grouping-table-wrong-shape-refused"]),
    "decision-issue-rules": (
        "`--decision-issue` is repeated once per issue; a named issue the file does not hold is "
        "refused, and naming one twice is a usage error",
        ["arm:decision-issue-same-id-twice-is-usage", "arm:decision-issue-absent-refused",
         "arm:decision-issue-repeated-reconciled-ok"]),
}

MODEL_NUMERIC = re.compile(
    r"gpt[- ]?\d|opus[- ]?\d|sonnet[- ]?\d|haiku[- ]?\d|grok[- ]?\d|composer[- ]?\d|gemini[- ]?\d",
    re.I,
)
HISTORICAL = re.compile(r"Historical observation \(\d{4}-\d{2}-\d{2}\): .+ was measured\.$")
JSON_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.S)


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\r", "")).strip()


class Tree:
    """New and base file contents, from the repository or from a synthetic dict."""

    def __init__(self, new: dict[str, bytes] | None = None,
                 base: dict[str, bytes] | None = None, base_sha: str = BASE_DEFAULT,
                 eol_baseline: dict[str, dict] | None = None) -> None:
        self.synthetic = new is not None
        self._new = new or {}
        self._base = base or {}
        self.base_sha = base_sha
        self._cache: dict[str, bytes | None] = {}
        if self.synthetic and eol_baseline is None:
            eol_baseline = {p: eol_profile(d) for p, d in self._base.items()}
        self.eol_baseline = eol_baseline

    def new(self, path: str) -> bytes | None:
        if self.synthetic:
            return self._new.get(path)
        p = ROOT / path
        return p.read_bytes() if p.is_file() else None

    def base(self, path: str) -> bytes | None:
        if self.synthetic:
            return self._base.get(path)
        if path not in self._cache:
            run = subprocess.run(["git", "show", f"{self.base_sha}:{path}"], cwd=ROOT,
                                 capture_output=True)
            self._cache[path] = run.stdout if run.returncode == 0 else None
        return self._cache[path]

    def text(self, path: str) -> str:
        data = self.new(path)
        if data is None:
            raise FileNotFoundError(path)
        return data.decode("utf-8").replace("\r\n", "\n")

    def base_text(self, path: str) -> str:
        data = self.base(path)
        if data is None:
            raise FileNotFoundError(f"{self.base_sha}:{path}")
        return data.decode("utf-8").replace("\r\n", "\n")

    def live(self, roots: list[str], suffixes: set[str]) -> list[str]:
        if self.synthetic:
            return sorted(
                p for p in self._new
                if Path(p).suffix in suffixes
                and any(p == r or p.startswith(r.rstrip("/") + "/") for r in roots)
            )
        out = []
        for root in roots:
            p = ROOT / root
            if p.is_file():
                out.append(root)
                continue
            if not p.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(p):
                dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
                for name in filenames:
                    if Path(name).suffix in suffixes:
                        out.append(Path(dirpath, name).relative_to(ROOT).as_posix())
        return sorted(set(out))


def sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """(head before the first H2, [(H2 line, body)]); headings inside fences are ignored."""
    head: list[str] = []
    out: list[tuple[str, list[str]]] = []
    fence = None
    for line in text.split("\n"):
        marker = line.lstrip()[:3]
        if marker in ("```", "~~~"):
            if fence is None:
                fence = marker
            elif fence == marker:
                fence = None
        if fence is None and line.startswith("## "):
            out.append((line.rstrip(), []))
            continue
        (out[-1][1] if out else head).append(line)
    return "\n".join(head), [(h, "\n".join(b)) for h, b in out]


def section(text: str, prefix: str) -> str:
    for heading, body in sections(text)[1]:
        if heading.startswith(prefix):
            return body
    return ""


# -- checks: each returns a list of failure messages ---------------------------------------

CITE_FILE = re.compile(r"human-decision-protocol(?:\.md)?`?\)?[\s>]*(§)")
CITE_WORD = re.compile(r"\b(?:protocol|HDP)\s+(§)")
CITE_TAIL = re.compile(r"§\s*[\w-]+(?:\s*[–-]\s*§\s*[\w-]+)?")
SECTION_TOKEN = re.compile(r"§\s*(\d+[A-Za-z]?|[A-Za-z][\w-]*)")


def c1(tree: Tree) -> list[str]:
    bad = []
    for path in tree.live(LIVE_ROOTS + CITATION_EXTRA_ROOTS, CITATION_SUFFIXES):
        text = tree.text(path)
        for rx in (CITE_FILE, CITE_WORD):
            for m in rx.finditer(text):
                start = m.start(1)
                tail = CITE_TAIL.match(text, start)
                line = text.count("\n", 0, start) + 1
                for tok in SECTION_TOKEN.findall(tail.group(0) if tail else "§?"):
                    if tok not in VALID_SECTIONS:
                        bad.append(f"C1 {path}:{line} cites protocol §{tok}, not one of "
                                   f"{sorted(VALID_SECTIONS)}")
    return bad


def c2(tree: Tree) -> list[str]:
    bad = []
    for path in tree.live(LIVE_ROOTS, DOC_SUFFIXES):
        flat = norm(tree.text(path)).lower()
        phrases = STALE_EVERYWHERE + (STALE_PROTOCOL_ONLY if path == PROTOCOL else [])
        for phrase in phrases:
            if norm(phrase).lower() in flat:
                bad.append(f"C2 {path} still says {phrase!r}")
    return bad


def _ordered(body: str, markers: list[str], label: str) -> list[str]:
    flat, pos, bad = norm(body), 0, []
    for marker in markers:
        found = flat.find(norm(marker), pos)
        if found < 0:
            where = "missing" if norm(marker) not in flat else "out of order"
            bad.append(f"C3 {label}: {marker!r} {where}")
        else:
            pos = found + len(norm(marker))
    return bad


def _contains(body: str, markers: list[str], label: str, check: str = "C3") -> list[str]:
    flat = norm(body)
    return [f"{check} {label}: missing {m!r}" for m in markers if norm(m) not in flat]


def _table_rows(body: str) -> list[str]:
    rows = [ln.strip() for ln in body.split("\n") if ln.strip().startswith("|")]
    return [r for r in rows if not re.fullmatch(r"\|[\s:|-]+\|", r)]


def _m_rows(s4a: str) -> list[str]:
    """Each M row is `| M-n | criterion | source |`; its criterion cell holds M_ROWS[n]'s
    criterion phrases and its own Source cell holds M_ROWS[n]'s source phrases."""
    bad = []
    for line in s4a.split("\n"):
        m = re.match(r"\| M-(\d+) \|", line.strip())
        if not m or int(m.group(1)) not in M_ROWS:
            continue
        n = int(m.group(1))
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            bad.append(f"C3 §4a M-{n}: {len(cells)} cells, not Id | Always human | Source")
            continue
        crit, src = norm(cells[1]), norm(cells[2])
        want_crit, want_src = M_ROWS[n]
        bad += [f"C3 §4a M-{n} criterion lacks {p!r}" for p in want_crit if norm(p) not in crit]
        bad += [f"C3 §4a M-{n} Source lacks {p!r}" for p in want_src if norm(p) not in src]
    return bad


def c3(tree: Tree) -> list[str]:
    text, base = tree.text(PROTOCOL), tree.base_text(PROTOCOL)
    head, secs = sections(text)
    bad = []
    headings = [h for h, _ in secs]
    if headings != EXPECTED_H2:
        bad.append(f"C3 H2 headings {headings} != {EXPECTED_H2}")
    bad += [f"C3 protocol holds forbidden {w!r}" for w in FORBIDDEN_PROTOCOL if w in text]
    bad += _contains(head, PROTOCOL_HEAD_MARKERS, "scope")
    s2, b2 = section(text, "## 2."), section(base, "## 2.")
    bad += _contains(s2, S2_MARKERS, "§2")
    rows = _table_rows(s2)
    if len(rows) < 2 or rows[1] != CURRENT_FOCUS_ROW:
        bad.append("C3 §2: the current-focus row is not the first sweep row")
    bad += [f"C3 §2: base sweep row dropped: {r[:60]!r}" for r in _table_rows(b2)
            if r not in rows]
    new_lines = [ln.strip() for ln in s2.split("\n")]
    for cmd in [ln.strip() for ln in b2.split("\n") if ln.strip().startswith("rtk proxy rg")]:
        if cmd not in new_lines:
            bad.append(f"C3 §2: base rg receipt command dropped: {cmd[:50]!r}")
    bad += _contains(section(text, "## 3."), S3_MARKERS, "§3")
    s4, b4 = norm(section(text, "## 4.")), norm(section(base, "## 4."))
    if S4_OLD not in b4:
        bad.append("C3 §4: the base no longer holds the recording sentence")
    elif s4 != b4.replace(S4_OLD, S4_NEW):
        bad.append("C3 §4: the body differs from the base beyond the recording sentence")
    s4a = section(text, "## 4a.")
    ids = [int(n) for n in re.findall(r"^\| M-(\d+) \|", s4a, re.M)]
    if ids != list(range(1, 15)):
        bad.append(f"C3 §4a: M rows {ids} are not M-1..M-14 once each in order")
    bad += _m_rows(s4a)
    bad += _contains(s4a, S4A_MARKERS, "§4a")
    bad += [f"C3 §4a holds upstream's anchor {w!r}" for w in S4A_FORBIDDEN if w in s4a]
    # The notes are the bullet block after the last "Five notes:" (bullets may wrap).
    at = s4a.rfind("Five notes:")
    block = s4a[at + len("Five notes:"):].lstrip("\n").split("\n\n", 1)[0] if at >= 0 else ""
    bullets = [ln for ln in block.split("\n") if ln.startswith("- ")]
    if len(bullets) != 5:
        bad.append(f"C3 §4a: {len(bullets)} notes after 'Five notes:', not 5")
    bad += _ordered(section(text, "## 5."), S5_ORDERED, "§5")
    s6 = section(text, "## 6.")
    bad += _contains(s6, S6_MARKERS, "§6")
    bad += [f"C3 §6 holds {w!r}" for w in S6_FORBIDDEN if w in s6]
    bad += _contains(section(text, "## 7."), S7_MARKERS, "§7")
    return bad


def c4(tree: Tree) -> list[str]:
    bad = []
    agents = tree.text(AGENTS)
    if AGENTS_NEW not in agents:
        bad.append("C4 AGENTS.md lacks the decide-before-you-ask text")
    if AGENTS_OLD in agents:
        bad.append("C4 AGENTS.md still holds the old protocol sentence")
    if norm(DELEGATION_NEW) not in norm(tree.text(DELEGATION)):
        bad.append(f"C4 {DELEGATION} lacks the Open decisions bullet")
    for path, markers in REQUIRED_TEXT.items():
        bad += _contains(tree.text(path), markers, path, "C4")
    for path, words in FORBIDDEN_TEXT.items():
        bad += [f"C4 {path} still holds {w!r}" for w in words if w in tree.text(path)]
    return bad


def c5(tree: Tree) -> list[str]:
    return [f"C5 twins differ: {a} {b}" for a, b in TWINS if tree.new(a) != tree.new(b)]


def eol_profile(data: bytes) -> dict:
    """Working-tree line endings. Git stores these files LF (`* text=auto`), so the base is a
    snapshot of the checkout taken before the edits (--eol-snapshot), never a git blob."""
    lines = data.split(b"\n")[:-1]
    bare = [ln.decode("utf-8", "replace") for ln in lines if not ln.endswith(b"\r")]
    return {"crlf": len(lines) - len(bare), "bare_lf": len(bare),
            "bare_lf_lines": bare if len(bare) <= 20 else None}


def c6(tree: Tree) -> list[str]:
    if tree.eol_baseline is None:
        return ["C6 not run: pass --eol-baseline (the row-0 snapshot)"]
    bad = []
    for path in EDITED:
        data, base = tree.new(path), tree.eol_baseline.get(path)
        if data is None or base is None:
            bad.append(f"C6 {path} missing (file={data is not None}, baseline={base is not None})")
            continue
        new = eol_profile(data)
        if base["crlf"] == 0:
            if new["crlf"]:
                bad.append(f"C6 {path} was LF and now has {new['crlf']} CRLF endings")
        elif new["bare_lf"] != base["bare_lf"]:
            bad.append(f"C6 {path} bare-LF endings {base['bare_lf']} -> {new['bare_lf']}")
        elif base["crlf"] and base["bare_lf_lines"]:
            lost = [ln for ln in base["bare_lf_lines"] if ln not in (new["bare_lf_lines"] or [])]
            bad += [f"C6 {path} LF-only line now CRLF: {ln[:50]!r}" for ln in lost]
    return bad


def c7(tree: Tree) -> list[str]:
    bad = []
    data = tree.new(AGENTS) or b""
    lines = len(data.decode("utf-8").splitlines())
    base_lines = len((tree.base(AGENTS) or b"").decode("utf-8").splitlines())
    if lines > 170 or len(data) >= 20000:
        bad.append(f"C7 AGENTS.md {lines} lines / {len(data)} bytes exceeds 170 / 20000")
    if lines != base_lines:
        bad.append(f"C7 AGENTS.md line count {base_lines} -> {lines}")
    try:
        rule_map = json.loads(JSON_BLOCK.findall(tree.text(RULE_MAP))[0])
        pinned = rule_map["counts"]["AGENTS.md"]["postimage_sha256"]
    except (IndexError, KeyError, ValueError) as exc:
        return bad + [f"C7 {RULE_MAP} unreadable: {exc}"]
    if pinned != hashlib.sha256(data).hexdigest():
        bad.append(f"C7 {RULE_MAP} postimage_sha256 does not match AGENTS.md")
    return bad


def c8(tree: Tree) -> list[str]:
    census = json.loads(JSON_BLOCK.findall(tree.text(CENSUS))[0])
    known = {(m["path"], m["text_sha256"]) for m in census["matches"] if m.get("reason")}
    bad = []
    for path in EDITED:
        if path.startswith(ADOPTION):
            continue
        for line in (tree.new(path) or b"").decode("utf-8-sig").splitlines():
            if MODEL_NUMERIC.search(line) and not HISTORICAL.search(line):
                if (path, hashlib.sha256(line.encode()).hexdigest()) not in known:
                    bad.append(f"C8 {path} uncensused model pin: {line.strip()[:70]!r}")
    return bad


def c9(tree: Tree) -> list[str]:
    body = section(tree.text(HANDOFF_TPL), "## Decision Log")
    body = re.sub(r"\n-{3,}\s*$", "", body.strip()).strip()
    if not re.fullmatch(r"<!--.*?-->\s*```yaml\n.*?\n```", body, re.S):
        return [f"C9 {HANDOFF_TPL} Decision Log is not one comment plus one yaml block"]
    return []


def _boxes(text: str) -> list[list[int]]:
    boxes, cur = [], []
    for line in text.split("\n"):
        if line.lstrip()[:1] in ("┌", "│", "└", "├"):
            cur.append(len(line.rstrip()))
        elif cur:
            boxes.append(sorted(set(cur)))
            cur = []
    if cur:
        boxes.append(sorted(set(cur)))
    return boxes


def c10(tree: Tree) -> list[str]:
    if _boxes(tree.text(LIFECYCLE_GUIDE)) != _boxes(tree.base_text(LIFECYCLE_GUIDE)):
        return [f"C10 {LIFECYCLE_GUIDE} box line lengths changed"]
    return []


def selector_found(selector: str, evidence: str) -> bool:
    """`arm:<label>` needs a passing selftest arm line; `test:<file>::<prefix>` a PASSED
    pytest -v line. A FAIL or FAILED line, or the bare name anywhere else, does not count."""
    kind, _, name = selector.partition(":")
    if kind == "arm":
        rx = rf"^\s*ok\s+{re.escape(name)}\s+want="
    elif kind == "test":
        rx = rf"^{re.escape(name)}\S* PASSED\b"
    else:
        raise ValueError(f"unknown selector kind {selector!r}")
    return re.search(rx, evidence, re.M) is not None


def c11(tree: Tree, binding: Path, receipts: list[Path]) -> list[str]:
    """The clauses and evidence are TOPICS', fixed in this oracle. The binding only says, per
    topic, `{"topic"}` (bound) or `{"topic", "dropped_by_s84": true, "reason"}`."""
    entries = json.loads(binding.read_text(encoding="utf-8"))
    s6 = norm(section(tree.text(PROTOCOL), "## 6."))
    evidence = "\n".join(p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
                         for p in receipts)
    bad, seen = [], set()
    for e in entries:
        topic = e.get("topic")
        if topic not in TOPICS:
            bad.append(f"C11 unknown topic {topic!r}")
            continue
        if topic in seen:
            bad.append(f"C11 topic {topic} has two binding entries")
        seen.add(topic)
        clause, selectors = TOPICS[topic]
        stated = norm(clause) in s6
        found = [s for s in selectors if selector_found(s, evidence)]
        missing = [s for s in selectors if s not in found]
        if e.get("dropped_by_s84"):
            if stated:
                bad.append(f"C11 {topic}: §6 still states a check S84 dropped: {clause[:50]!r}")
            if found:
                bad.append(f"C11 {topic}: dropped, but S84's evidence is in the receipts: {found}")
            if not str(e.get("reason", "")).strip():
                bad.append(f"C11 {topic}: a drop needs a reason")
            continue
        if not stated:
            bad.append(f"C11 {topic}: §6 lacks the clause {clause[:60]!r}")
        if missing:
            bad.append(f"C11 {topic}: evidence not in the receipts (S2: S84 landed otherwise): "
                       f"{missing}")
    bad += [f"C11 topic {t} has no binding entry" for t in TOPICS if t not in seen]
    return bad


CHECKS = {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5, "C6": c6, "C7": c7, "C8": c8,
          "C9": c9, "C10": c10}


def run(tree: Tree, only: list[str] | None = None, binding: Path | None = None,
        receipts: list[Path] | None = None) -> dict[str, list[str]]:
    results = {}
    for cid, fn in CHECKS.items():
        if only and cid not in only:
            continue
        try:
            results[cid] = fn(tree)
        except (FileNotFoundError, UnicodeDecodeError, ValueError, IndexError) as exc:
            results[cid] = [f"{cid} could not run: {exc!r}"]
    if binding is not None and (not only or "C11" in only):
        results["C11"] = c11(tree, binding, receipts or [])
    elif not only or "C11" in only:
        results["C11"] = ["C11 not run: pass --binding validator-binding.json"]
    return results


def only_paths(results: dict[str, list[str]], paths: list[str]) -> tuple[dict, int]:
    """Keep the failures that name one of ``paths`` (a row checks only its own files; the
    rest are deferred to the row that edits them). C1/C2 name a path; C4/C6 name the file."""
    kept, deferred = {}, 0
    for cid, msgs in results.items():
        kept[cid] = [m for m in msgs if any(p in m for p in paths)]
        deferred += len(msgs) - len(kept[cid])
    return kept, deferred


# -- selftest -------------------------------------------------------------------------------

def _crlf(text: str) -> bytes:
    return text.replace("\n", "\r\n").encode("utf-8")


def _m_row(n: int) -> str:
    """A substantive M row: its criterion and source phrases in their own cells."""
    crit, src = M_ROWS[n]
    return f"| M-{n} | {' '.join(crit)} | `AGENTS.md` {'; '.join(src)} |\n"


def _protocol_pair() -> tuple[str, str]:
    s4_base = (
        "\nWeigh the precedents. **The decision is the agent's to make** when **all** hold:\n\n"
        "1. **Convergence:** a precedent decided it.\n2. **Two-way door:** reversible.\n"
        "3. **No product fork:** none.\n4. **Not a governance number:** no new cap.\n\n"
        f"When all four hold: decide, tag the criterion, {S4_OLD}, and continue.\n\n"
        "| Class | Failing test | Typical example |\n|---|---|---|\n"
        "| `one-way-door` | 2 | Schema migration |\n\n---\n"
    )
    sweep = ("| Where prior decisions live | What to look for |\n|---|---|\n"
             "| `.agent/context/grouping/*.md` §8 | D tables |\n"
             "| `docs/execution/reflections/*.md` | Autonomous decisions |\n")
    rg = ("```bash\nrtk proxy rg -n -i \"Human-approved\" .agent > C:/Temp/s.txt 2>&1\n```\n\n"
          "```powershell\nrtk proxy rg -n -i \"Human-approved\" .agent *> C:/Temp/s.txt\n```\n")
    base = ("# Human Decision Protocol\n\n> **Scope:** old.\n\n## 1. Trigger\n\nRun it.\n\n"
            f"## 2. Precedent sweep (codebase first)\n\n{sweep}\n{rg}\n"
            "## 3. Web research (any search beats none)\n\nold\n\n"
            f"## 4. Synthesis and the obviousness test\n{s4_base}\n"
            "## 5. Decision Brief — how a human-gated decision is presented\n\nold\n\n"
            "## 6. Recording — every decision leaves a trail\n\nold\n\n"
            "## 7. Anti-patterns\n\nold\n\n## 8. Research basis\n\nold\n")
    m_rows = "".join(_m_row(n) for n in range(1, 15))
    notes = "".join(f"- note {n}.\n" for n in range(1, 6))
    s4a = (f"\n{' '.join(S4A_MARKERS[:15])}\n\n| Id | Always human | Source |\n"
           f"| :- | :- | :- |\n{m_rows}\nFive notes:\n\n{notes}\n"
           f"{' '.join(S4A_MARKERS[16:])}\n\n---\n")
    s5 = ("\n**Two outcomes.** Decide or ask.\n\n```markdown\n" + "\n".join(S5_ORDERED[1:6])
          + "\n```\n\nRules:\n\n" + "\n".join(f"- {m}" for m in S5_ORDERED[6:]) + "\n\n---\n")
    s6 = "\n" + "\n".join(S6_MARKERS) + "\n\n" + S6_VALIDATOR + "\n\n---\n"
    focus_sweep = sweep.replace("|---|---|\n", "|---|---|\n" + CURRENT_FOCUS_ROW + "\n")
    new = ("# Human Decision Protocol\n\n> " + " ".join(PROTOCOL_HEAD_MARKERS[:4]) + "\n> "
           + PROTOCOL_HEAD_MARKERS[5] + "\n\n" + PROTOCOL_HEAD_MARKERS[4] + "\n\n"
           "## 1. Trigger\n\nRun it.\n\n## 2. Precedent sweep (codebase first)\n\n"
           + S2_MARKERS[0] + "\n\n" + focus_sweep + "\n" + rg
           + "\n## 3. Research\n\n" + "\n".join(S3_MARKERS) + "\n\n"
           "## 4. Synthesis and the obviousness test\n" + s4_base.replace(S4_OLD, S4_NEW)
           + "\n## 4a. Mandatory-human criteria\n" + s4a
           + "\n## 5. Decision Brief — how a human-gated decision is presented\n" + s5
           + "\n## 6. Recording — every decision leaves a trail\n" + s6
           + "\n## 7. Basis\n\n" + " ".join(S7_MARKERS) + "\n")
    return new, base


def _synthetic() -> tuple[dict[str, bytes], dict[str, bytes]]:
    new_protocol, base_protocol = _protocol_pair()
    agents_base = "\n".join(["# AGENTS"] + [f"rule {i}" for i in range(2, 27)] + [AGENTS_OLD]
                            + [f"rule {i}" for i in range(28, 127)]) + "\n"
    agents_new = agents_base.replace(AGENTS_OLD, AGENTS_NEW)
    deleg_base = (b"# Delegation\r\n\r\nline3\r\nline4\r\nline5 lf\nline6\r\n"
                  b"- **Never delegate** x.\r\n")
    deleg_new = deleg_base + DELEGATION_NEW.encode() + b"\r\n"

    def rule_map(digest: str) -> bytes:
        body = json.dumps({"counts": {"AGENTS.md": {"postimage_sha256": digest}}})
        return _crlf(f"# Rule map\n\n```json\n{body}\n```\n")

    census = "# Census\n\n```json\n" + json.dumps({"matches": [], "files": []}) + "\n```\n"
    box = "Box:\n\n┌──────┐\n│ old. │\n└──────┘\n"
    handoff = ("# Handoff\n\n## Decision Log\n\n<!-- " + " ".join(REQUIRED_TEXT[HANDOFF_TPL])
               + " -->\n\n```yaml\ndecision_log:\n  - id: D-{n}\n```\n\n---\n\n## Next\n")
    templates_new = {
        PLAN_TPL: "# Plan\n\n" + "\n".join(REQUIRED_TEXT[PLAN_TPL]) + "\n",
        TASK_TPL: "# Task\n\n" + REQUIRED_TEXT[TASK_TPL][0] + "\n",
        HANDOFF_TPL: handoff,
        REFLECTION_TPL: "# Reflection\n\n### Decisions Log\n\n"
        + "\n".join(REQUIRED_TEXT[REFLECTION_TPL][::-1]) + "\n",
    }
    templates_base = {
        PLAN_TPL: "# Plan\n\n**Recommendation:** {Option A}\n",
        TASK_TPL: "# Task\n\nH2-2 row.\n",
        HANDOFF_TPL: handoff.replace("checks each entry", "compares each"),
        REFLECTION_TPL: "# Reflection\n\n| ID | Stage | Question |\n",
    }
    new: dict[str, bytes] = {}
    base: dict[str, bytes] = {}
    for path in EDITED:
        new[path] = base[path] = _crlf(f"# {path}\n\nUnrelated text.\n")
    for a, b in TWINS:
        new[a] = new[b] = _crlf(templates_new[a])
        base[a] = base[b] = _crlf(templates_base[a])
    new[PROTOCOL], base[PROTOCOL] = _crlf(new_protocol), _crlf(base_protocol)
    new[AGENTS], base[AGENTS] = _crlf(agents_new), _crlf(agents_base)
    new[DELEGATION], base[DELEGATION] = deleg_new, deleg_base
    new[CREATE_PLAN] = _crlf("# create-plan\n\n" + "\n".join(REQUIRED_TEXT[CREATE_PLAN])
                             + "\n\nCite `human-decision-protocol.md` §2–§4 and (protocol §5).\n")
    new[GROUPING_WF] = _crlf("# grouping\n\n" + "\n".join(REQUIRED_TEXT[GROUPING_WF]) + "\n")
    new[LIFECYCLE_GUIDE] = _crlf(box.replace("old.", "new."))
    base[LIFECYCLE_GUIDE] = _crlf(box)
    new[RULE_MAP] = rule_map(hashlib.sha256(new[AGENTS]).hexdigest())
    base[RULE_MAP] = rule_map(hashlib.sha256(base[AGENTS]).hexdigest())
    new[CENSUS] = base[CENSUS] = census.encode()
    return new, base


def _plant(new: dict[str, bytes], path: str, old: str, repl: str) -> dict[str, bytes]:
    """Replace the first `old` in one synthetic CRLF file (both sides given with \\n)."""
    text = new[path].decode("utf-8")
    old_crlf = old.replace("\n", "\r\n")
    if old_crlf not in text:
        raise AssertionError(f"selftest fixture lacks {old!r} in {path}")
    return {**new, path: text.replace(old_crlf, repl.replace("\n", "\r\n"), 1).encode()}


def _swap(new: dict[str, bytes], path: str, a: str, b: str) -> dict[str, bytes]:
    """Exchange two marker texts in one synthetic file (an order fault)."""
    text = new[path].decode("utf-8")
    if a not in text or b not in text:
        raise AssertionError(f"selftest fixture lacks {a!r} or {b!r} in {path}")
    text = text.replace(a, "\0").replace(b, a).replace("\0", b)
    return {**new, path: text.encode("utf-8")}


def _faults(new: dict[str, bytes], base: dict[str, bytes]) -> list[tuple[str, str, dict]]:
    wf = ".agent/workflows/execution-session.md"
    rg_pwsh = "rtk proxy rg -n -i \"Human-approved\" .agent *> C:/Temp/s.txt\n"
    handoff_prose = {p: _plant(new, p, "-->\n", "-->\n\nExtra prose.\n")[p] for p in TWINS[2]}
    old_table = _crlf("| ID | Stage | Question |\n")
    return [
        ("F01 an '## 8.' heading", "C3",
         _plant(new, PROTOCOL, "## 7. Basis", "## 7. Basis\n\n## 8. Old basis\n")),
        ("F02 §4 criterion 4 deleted", "C3",
         _plant(new, PROTOCOL, "4. **Not a governance number:** no new cap.\n", "")),
        ("F03 §4 class table row edited", "C3",
         _plant(new, PROTOCOL, "| 2 | Schema migration |", "| 2 | Anything |")),
        ("F04 human-all mode in §4a", "C3",
         _plant(new, PROTOCOL, "Five notes:", "A `human-all` mode.\n\nFive notes:")),
        ("F05 M-9 row missing", "C3", _plant(new, PROTOCOL, _m_row(9), "")),
        ("F06 Refs before the recommendation", "C3",
         _swap(new, PROTOCOL, S5_ORDERED[2], S5_ORDERED[5])),
        ("F07 SIGN 3 (a)", "C3",
         _plant(new, PROTOCOL, "## 7. Basis", "`GUARDRAILS.md` SIGN 3 (a)\n\n## 7. Basis")),
        ("F08 current-focus row missing", "C3",
         _plant(new, PROTOCOL, CURRENT_FOCUS_ROW + "\n", "")),
        ("F09 pwsh rg command dropped", "C3", _plant(new, PROTOCOL, rg_pwsh, "")),
        ("F10 §6 hand-over paragraph", "C3",
         _plant(new, PROTOCOL, S6_MARKERS[-1], S6_MARKERS[-1] + "\nHanded to the agent: x.")),
        ("F11 upstream §5f numbering", "C3", _plant(new, PROTOCOL, "(§5e)", "(§5f)")),
        ("F12 five notes become four", "C3", _plant(new, PROTOCOL, "- note 5.\n", "")),
        ("F13 citation of protocol §8", "C1",
         _plant(new, CREATE_PLAN, "(protocol §5)", "(protocol §8)")),
        ("F14 citation of §Where it lives", "C1",
         _plant(new, CREATE_PLAN, "`human-decision-protocol.md` §2–§4",
                "`human-decision-protocol.md` §Where it lives")),
        ("F15 citation range ends at §9", "C1", _plant(new, CREATE_PLAN, "§2–§4", "§2–§9")),
        ("F16 citation of §2B", "C1", _plant(new, CREATE_PLAN, "§2–§4", "§2B")),
        ("F17 stale phrase in a template", "C2",
         _plant(new, PLAN_TPL, "# Plan\n", "# Plan\n\nDefault if unanswered: A.\n")),
        ("F18 'Research basis' kept in the protocol", "C2",
         _plant(new, PROTOCOL, "## 7. Basis\n", "## 7. Basis\n\nResearch basis.\n")),
        ("F19 old AGENTS sentence kept", "C4", _plant(new, AGENTS, AGENTS_NEW, AGENTS_OLD)),
        ("F20 delegation bullet missing", "C4", _plant(new, DELEGATION, DELEGATION_NEW, "")),
        ("F21 create-plan test-search sentence missing", "C4",
         _plant(new, CREATE_PLAN, CP_TEST_SEARCH, "")),
        ("F22 reflection template keeps the table", "C4",
         {**new, REFLECTION_TPL: old_table, TWINS[3][1]: old_table}),
        ("F23 twin differs", "C5", {**new, TWINS[1][1]: new[TWINS[1][1]] + b"x"}),
        ("F24 CRLF file converted to LF", "C6", {**new, wf: new[wf].replace(b"\r\n", b"\n")}),
        ("F25 delegation line 5 made CRLF", "C6",
         {**new, DELEGATION: new[DELEGATION].replace(b"line5 lf\n", b"line5 lf\r\n")}),
        ("F25b LF-only ending moved to another line", "C6",
         {**new, DELEGATION: new[DELEGATION].replace(b"line5 lf\nline6\r\n",
                                                     b"line5 lf\r\nline6\n")}),
        ("F26 AGENTS gains a line", "C7", _plant(new, AGENTS, "rule 28\n", "rule 28\nrule 28b\n")),
        ("F27 stale rule-map digest", "C7", {**new, RULE_MAP: base[RULE_MAP]}),
        ("F28 uncensused model pin", "C8", _plant(new, wf, "Unrelated text.", "Use opus-5 here.")),
        ("F29 prose in the handoff Decision Log", "C9", {**new, **handoff_prose}),
        ("F30 box width changed", "C10", _plant(new, LIFECYCLE_GUIDE, "│ new. │", "│ new.  │")),
        ("F35 M-7 criterion removed, its id kept", "C3",
         _plant(new, PROTOCOL, _m_row(7), "| M-7 |  | `AGENTS.md` §Testing & TDD Protocol |\n")),
        ("F36 M-7 and M-11 sources swapped", "C3",
         _swap(new, PROTOCOL, "§Testing & TDD Protocol |",
               "§Validation Pipeline; §Dual-Agent Workflow |")),
        ("F37 M-14 cites upstream's SIGN 3 (b)", "C3",
         _plant(new, PROTOCOL, "`GUARDRAILS.md` SIGN 3 |", "`GUARDRAILS.md` SIGN 3 (b) |")),
    ]


def _evidence_receipts(tmp: str) -> tuple[Path, Path]:
    """A closeout selftest receipt and a pytest -v receipt holding every TOPICS selector."""
    arms, tests = [], []
    for _, selectors in TOPICS.values():
        for sel in selectors:
            kind, _, name = sel.partition(":")
            if kind == "arm":
                arms.append(f"  ok   {name} want=1/REFUSE got=1/REFUSE")
            else:
                tests.append(f"{name}case PASSED                    [ 50%]")
    closeout = Path(tmp, "closeout-selftest.txt")
    closeout.write_text("\n".join(arms + ["RESULT: 226 arm(s), 0 failure(s)"]) + "\n",
                        encoding="utf-8")
    pytest = Path(tmp, "s84-tests.txt")
    pytest.write_text("\n".join(tests + ["==== 40 passed in 3.1s ===="]) + "\n", encoding="utf-8")
    return closeout, pytest


def _binding_cases(new: dict[str, bytes], base: dict[str, bytes]) -> bool:
    ok = True
    stage_clause = TOPICS["same-stage"][0] + ". "
    stage_test = TOPICS["same-stage"][1][0].partition(":")[2]
    pending_arm = TOPICS["pending-refused"][1][0].partition(":")[2]
    no_stage = _plant(new, PROTOCOL, stage_clause, "")
    no_paragraph = _plant(new, PROTOCOL, S6_VALIDATOR, "")
    with tempfile.TemporaryDirectory() as tmp:
        closeout, pytest = _evidence_receipts(tmp)
        full = closeout.read_text(encoding="utf-8")
        tests = pytest.read_text(encoding="utf-8")
        fail_arm = Path(tmp, "fail-arm.txt")
        fail_arm.write_text(full.replace(f"  ok   {pending_arm} ", f"  FAIL {pending_arm} "),
                            encoding="utf-8")
        failed_test = Path(tmp, "failed-test.txt")
        failed_test.write_text(
            tests.replace(f"{stage_test}case PASSED", f"{stage_test}case FAILED"), encoding="utf-8")
        no_stage_test = Path(tmp, "no-stage-test.txt")
        no_stage_test.write_text("\n".join(ln for ln in tests.split("\n")
                                           if stage_test not in ln), encoding="utf-8")
        good = [{"topic": t} for t in TOPICS]
        drop = [{"topic": "same-stage", "dropped_by_s84": True, "reason": "D-8xx"}] + [
            e for e in good if e["topic"] != "same-stage"]
        cases = [
            ("C11 all-green binding", new, good, [closeout, pytest], False),
            ("C11 a real drop (clause and evidence both absent)", no_stage, drop,
             [closeout, no_stage_test], False),
            ("F31 a fixed clause missing from §6", no_stage, good, [closeout, pytest], True),
            ("F32 an arm that FAILs in the receipt", new, good, [fail_arm, pytest], True),
            ("F33 binding topic missing", new, good[1:], [closeout, pytest], True),
            ("F34 dropped check still stated", new, drop, [closeout, no_stage_test], True),
            ("F38 dropped while S84's evidence is in the receipts", no_stage, drop,
             [closeout, pytest], True),
            ("F39 §6 holds only the record-once opening (every topic on one sentence)",
             no_paragraph, good, [closeout, pytest], True),
            ("F40 a test that FAILED in the pytest receipt", new, good, [closeout, failed_test],
             True),
            ("F41 an unknown topic", new, good + [{"topic": "made-up"}], [closeout, pytest], True),
        ]
        for name, tree_new, entries, receipts, should_fail in cases:
            path = Path(tmp, "binding.json")
            path.write_text(json.dumps(entries), encoding="utf-8")
            msgs = c11(Tree(tree_new, base), path, receipts)
            right = bool(msgs) == should_fail
            print(f"{'ok  ' if right else 'MISS'} {name}: {'refused' if msgs else 'accepted'}")
            if not right:
                for m in msgs:
                    print("    ", m)
            ok &= right
    clauses = [c for c, _ in TOPICS.values()]
    plan = Path(__file__).with_name("implementation-plan.md")
    right = (all(norm(c) in norm(S6_VALIDATOR) for c in clauses)
             and len(set(clauses)) == len(clauses)
             and plan.is_file() and norm(S6_VALIDATOR) in norm(plan.read_text(encoding="utf-8")))
    print(f"{'ok  ' if right else 'MISS'} every C11 clause is in S6_VALIDATOR, once, and the plan "
          "quotes S6_VALIDATOR word for word")
    return ok and right


def selftest() -> int:
    new, base = _synthetic()
    green = run(Tree(new, base), only=list(CHECKS))
    failures = [m for msgs in green.values() for m in msgs]
    print(f"all-green tree: {len(failures)} failure(s)")
    for m in failures:
        print("  ", m)
    ok = not failures
    for name, want, tree_new in _faults(new, base):
        got = run(Tree(tree_new, base), only=list(CHECKS))
        hit = bool(got.get(want))
        print(f"{'ok  ' if hit else 'MISS'} {name}: {want} {'refused' if hit else 'accepted it'}")
        ok &= hit
    ok &= _binding_cases(new, base)
    sample = {"C4": [f"C4 {AGENTS} lacks x", f"C4 {DELEGATION} lacks y"], "C6": []}
    kept, deferred = only_paths(sample, [DELEGATION])
    right = kept == {"C4": [f"C4 {DELEGATION} lacks y"], "C6": []} and deferred == 1
    print(f"{'ok  ' if right else 'MISS'} --paths keeps the named file and defers the rest")
    ok &= right
    print("hdp-check selftest:", "0 failures" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n", 1)[0])
    parser.add_argument("--base", default=BASE_DEFAULT, help="base commit for §4 and endings")
    parser.add_argument("--checks", help="comma list, e.g. C3,C4 (default: all)")
    parser.add_argument("--binding", type=Path, help="validator-binding.json for C11")
    parser.add_argument("--evidence-receipt", type=Path, action="append", default=[])
    parser.add_argument("--eol-snapshot", type=Path,
                        help="write the edited files' working-tree line endings and exit")
    parser.add_argument("--eol-baseline", type=Path, help="the --eol-snapshot file, for C6")
    parser.add_argument("--paths", help="comma list: count only failures naming these files")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.eol_snapshot:
        snap = {p: eol_profile((ROOT / p).read_bytes()) for p in EDITED}
        args.eol_snapshot.write_text(json.dumps(snap, indent=1), encoding="utf-8")
        mixed = [p for p, v in snap.items() if v["crlf"] and v["bare_lf"]]
        print(f"eol snapshot: {len(snap)} files, "
              f"{sum(1 for v in snap.values() if v['crlf'])} CRLF, mixed {mixed}")
        return 0
    only = [c.strip() for c in args.checks.split(",")] if args.checks else None
    eol = (json.loads(args.eol_baseline.read_text(encoding="utf-8"))
           if args.eol_baseline else None)
    results = run(Tree(base_sha=args.base, eol_baseline=eol), only, args.binding,
                  args.evidence_receipt)
    if args.paths:
        results, deferred = only_paths(results, [p.strip() for p in args.paths.split(",")])
        print(f"--paths: {deferred} failure(s) in other files deferred to their rows")
    total = 0
    for cid, msgs in results.items():
        print(f"{cid} {'ok' if not msgs else f'FAIL ({len(msgs)})'}")
        for m in msgs:
            print("  ", m)
        total += len(msgs)
    print("hdp-check: all checks pass" if not total else f"hdp-check: {total} failure(s)")
    return 0 if not total else 1


if __name__ == "__main__":
    sys.exit(main())
