---
project: "2026-11-15-hdp-v2-protocol"
date: "2026-11-15"
source: "P:/agentic-framework commit a73d6df (the HD1 protocol part)"
grouping_source: ".agent/context/grouping/2026-11-15-hdp-framework-sync-session-grouping.md"
meus: []
status: "draft"
template_version: "2.3"
---

# Implementation Plan: Decide before you ask — the HDP v2 protocol

> **Project**: `2026-11-15-hdp-v2-protocol`
> **Build Plan Section(s)**: none (framework docs; no MEU, D-821)
> **Status**: `draft`
> **Session**: 85 of the HDP framework-sync grouping (Sessions 84 to 87, run in order on `main`)

---

## Goal

**Goal anchor:** av-kit's Human Decision Protocol, `AGENTS.md`, the four templates and every workflow, doc and skill that cites the protocol follow upstream HD1: the agent decides before it asks, a brief leads with a plain-words recommendation and keeps a do-nothing option, §4a names what is always the human's, and each decision is recorded once, in the log of the stage that made it.

One upstream commit in `P:/agentic-framework` is ported: **`a73d6df`** ("feat(hdp): port the decision protocol and the expert pass", 2026-11-14), the HD1 protocol part only. Session 84 (`closeout-record-once`) ported its closeout-validator part. Session 86 (`hdp-expert-pass`) owns §5a, the expert-pass skill and the §6 hand-over rule.

Today `.agent/docs/human-decision-protocol.md` (18,562 bytes, 287 lines, CRLF) has §3 "Web research", a brief with "**If you do not answer:**" and `SIGN 3 (a)`, no §4a list, a §6 that has the reflection restate **every** autonomous decision, and §7 Anti-patterns and §8 Research basis. `AGENTS.md:27` sends Codex to "precedent sweep → web research → … reflection Decisions Log". Once Session 84 lands, the validator no longer compares the reflection, so these lines describe a check that is gone.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-15). Every payload here is governance prose and an upstream diff that must be read verbatim, which is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`, with receipts under `C:/Temp/av-kit/hdp85/` named `hdp-*`, `RECEIPTS_DIR=C:/Temp/av-kit`, `PYTHONIOENCODING=utf-8` and `ELECTRON_RUN_AS_NODE` cleared. Python runs through `uv run`; Vitest is not used.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub`, `P:/agentic-framework`, `P:/zorivest` and `P:/.agent` are read only, and the hub is never opened.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `hdp-plan-2026-11-15-hdp-v2-protocol` and `hdp-execution-2026-11-15-hdp-v2-protocol`. Claude wrote the plan, so the reviewer is a different vendor. Caps come from `.agent/review-limits.json` (plan 3, execution 6, token budgets off) and are printed by `review_ledger.py state`. The orchestrator dispatches; if Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered, and the coordinator warns before dispatching.
- **Never in these rows without Mat's words:** commit, push, merge, release, a destructive data operation, external disclosure, credentials, or an `approved` verdict authored by the implementer.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| HDP v2 protocol (no MEU) | `.agent/context/handoffs/2026-11-15-hdp-v2-protocol-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-15-hdp-v2-protocol-plan-critical-review.md` and `.agent/context/handoffs/2026-11-15-hdp-v2-protocol-implementation-critical-review.md`. The single non-MEU handoff follows `2026-11-14-review-limits-no-token-budget` and Session 84.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and the oracle's Red run (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `baseline-content.txt`, `eol-baseline.json`, `hdp-base-*.txt`, `hdp-red.txt` |
| WP-2 | The protocol and the §6 binding (row 1) | WP-1 | shared | `.agent/docs/human-decision-protocol.md`, `validator-binding.json` |
| WP-3 | Templates and twins (row 2) | WP-2 | shared | the eight template files |
| WP-4 | `AGENTS.md`, the rule-map repin, `model-delegation.md` (rows 3, 4) | WP-2 | shared | `AGENTS.md`, `rule-preservation.md`, `model-delegation.md` |
| WP-5 | Workflows, docs and skills (rows 5, 6) | WP-2 | shared | the files in §Inventory I8 to I23 |
| WP-6 | The full oracle run (row 7) | WP-3, WP-4, WP-5 | shared | `hdp-green.txt` |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | Handoff, review, reflection, Session 86 prompt |

## User Review Required

> [!IMPORTANT]
> **What changes for every later session.** Before any question goes to Mat, the agent sweeps the precedent (now including `current-focus.md`) and researches the open facts. A local measurement counts as research. It decides whatever is still its to decide and says so in one line. What reaches Mat is a short brief: the question in plain words, "I recommend A", the other options, a do-nothing option, and one Refs line. A new §4a lists fourteen kinds of decision that are always Mat's, whatever the obviousness test says. Each decision is written once, in the stage that made it; the reflection keeps only a short link list of reversible choices.
>
> **Two decisions are Mat's, and both were ruled by his default acceptance** ("Run HDP on any decisions that come up and and I approving acceptance of the defaults.", 2026-11-15):
> 1. **D-843:** adopt the §4a list, adapted to av-kit (M-3: it changes what the protocol allows).
> 2. **D-844:** replace the `AGENTS.md:27` protocol sentence with the decide-before-you-ask rule (M-3: an `AGENTS.md` edit).
>
> That acceptance does not cover commit, push, merge, release, destructive data operations, external disclosure or credentials (S8).
>
> **Gate:** Session 84 must be closed first. Row 0 refuses to start until `s84-landed.py` finds Session 84's port in the validator, every Session 84 task row done, and its handoff and reflection written (S2).

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `PROTOCOL` | `.agent/docs/human-decision-protocol.md`. CRLF, 287 lines at base; it stays CRLF. |
| `UPSTREAM` | `git -C P:/agentic-framework show a73d6df:core/.agent/docs/human-decision-protocol.md` (read only). A copy is `C:/Temp/av-kit/s85-upstream-hdp.md`. The upstream template, `AGENTS.md`, `create-plan.md` and `model-delegation.md` hunks are `git -C P:/agentic-framework show a73d6df -- core/templates/ core/AGENTS.md core/.agent/workflows/create-plan.md core/.agent/docs/model-delegation.md`. |
| `BASE` | `6813232d8769be71eb6e72505b6f39c58c11bddd`, HEAD at plan time. Every EDITED file equals `BASE` at row 0 (S3). |
| `EDITED` | The 28 files in §Files Modified, listed as `EDITED` in `hdp-check.py`. |
| `ORACLE` | `docs/execution/plans/2026-11-15-hdp-v2-protocol/hdp-check.py`: read-only checks C1 to C11 and a planted-fault selftest (46 arms, 0 failures at plan time). Its constants are the required and forbidden texts this plan names, including `M_ROWS` (each M row's criterion and source), `S6_VALIDATOR` (the §6 paragraph) and `TOPICS` (each §6 clause and its proof). |
| `BINDING` | `validator-binding.json` in this plan folder, written in row 1. One entry per topic in `ORACLE.TOPICS` (25 topics; `dq-escapes` added in execution, D-856): `{"topic"}`, or `{"topic", "dropped_by_s84": true, "reason"}`. The clauses and the evidence are fixed in `ORACLE`; the binding only says which topics landed. |
| `S84_LANDED` | `docs/execution/plans/2026-11-15-hdp-v2-protocol/s84-landed.py`: row 0's gate (S2). It runs Session 84's read-only `docs/execution/plans/2026-11-15-closeout-record-once/port-check.py` on `VALIDATOR` (the port's identifiers `decision_field_text`, `_NON_TEXT_SCALAR`, `_quoted_scalar_text` and `grouping_row_problems`, `DECISIONS_LOG_HEADERS` and `reflection_decision_rows` gone, `check_decisions_log(sources, issues)` with no reflection, `grouping_decisions` judging rows with `grouping_row_problems(`, and its files' line endings), then needs every status cell of Session 84's `task.md` to be `[x]` and its handoff and reflection to exist. Any problem exits 12. `--selftest`: 12 arms. |
| `EVIDENCE` | Row 0's two receipts: `C:/Temp/av-kit/hdp85/hdp-base-closeout-selftest.txt` (the landed validator's selftest) and `C:/Temp/av-kit/hdp85/hdp-base-s84-tests.txt` (`pytest -v` of Session 84's two test files). |
| `VALIDATOR` | `tools/validate_closeout_artifacts.py`, as Session 84 left it. Read only here (AC-18). |
| `CRLF rule` | Every EDITED file is CRLF in the work tree (the blobs are LF; `.gitattributes` is `* text=auto`, `core.autocrlf=true`). `model-delegation.md` is mixed: 51 CRLF endings and one bare LF, on line 5, which stays bare LF. Edits read and write Python bytes with `newline=""`, or the Edit tool, which keeps endings. `C:/Temp/av-kit/hdp85/plan-eol.txt` |

### The protocol rewrite (row 1, AC-1 to AC-10)

`PROTOCOL` takes `UPSTREAM`'s structure and wording, minus §5a and the §6 hand-over paragraph (Session 86), with av-kit's local steps kept (D-842) and the adaptations of D-845. The H2 headings are exactly, in order:

`## 1. Trigger` · `## 2. Precedent sweep (codebase first)` · `## 3. Research` · `## 4. Synthesis and the obviousness test` · `## 4a. Mandatory-human criteria` · `## 5. Decision Brief — how a human-gated decision is presented` · `## 6. Recording — every decision leaves a trail` · `## 7. Basis`

No other H2. §7 Anti-patterns goes, as upstream dropped it, and §8 Research basis becomes §7 Basis (D-841).

| Part | Change | Required (`ORACLE` C3) | Forbidden |
|---|---|---|---|
| Head | av-kit's scope list stays, with "AskUserQuestion", "a subagent return that carries an open decision", "the round-cap TL;DR (§5d)" and reviewer questions "(§5e)" (av-kit's `create-plan.md` numbering). The rule line becomes upstream's. | `PROTOCOL_HEAD_MARKERS`: those four, `**Rule in one line:** decide before you ask.`, `**It never loosens a hard gate.**` | `(§5f)`, `TL;DR (§5e)` |
| §1 | Upstream's text | the H2 | — |
| §2 | The sweep table keeps every av-kit row and both `rtk proxy rg` receipt commands (bash and pwsh). A first row is added: `` \| `.agent/context/current-focus.md` \| The current priority and the recent rulings of the user \| ``. After the table: "If a prior ruling settles the decision, apply it and cite it. Then no research is necessary." | `CURRENT_FOCUS_ROW` first; `S2_MARKERS`; every base table row; both base rg commands | — |
| §3 | Renamed "Research". Upstream's opening ("Research each open fact that can change the recommendation, before you decide or ask." and "A local measurement counts as research"), then av-kit's ladder kept: Pomera `pomera_web_search`, `WebSearch`, Codex `--search`, `research: unavailable`, and the angles table. The table's lead-in "Run 2–3 queries per decision, one per angle:" becomes "When web research is needed, run 2–3 queries per decision, one per angle:" (plan review R1 Q1), so it does not contradict the local-measurement rule | `S3_MARKERS` | — |
| §4 | Word-equal to `BASE`'s §4 except one phrase: "write the Decision Log entry (§6)" becomes "record the decision as §6 tells you" | `S4_NEW`; everything else equal after whitespace folding | `S4_OLD` |
| §4a | New, "Mandatory-human criteria". `hdp` is av-kit's only mode (D-820): the M-list is checked before the §4 test, and a hit is human-gated and logged `mandatory: [M-n, …]`. M-1 to M-14 in one table (Id, Always human, Source), adapted per §The §4a adaptation below. Then "Five notes:" with five bullets. | `S4A_MARKERS`; M-1 to M-14 once each, in order; each M row exactly three cells, with its `M_ROWS` criterion phrases in the Always-human cell and its `M_ROWS` source phrases in the Source cell; exactly five bullets after "Five notes:" | `human-all`, `run_parameters`, `claude-credits`; `S4A_FORBIDDEN` (`§Authority and Approval`, `§Independent Review`, `SIGN 3 (b)`) |
| §5 | Brief v2. "**Two outcomes.**" paragraph; the brief block `### D-n: <the question in plain words>`, `**I recommend A: <what happens, in plain words>.**` + why/failure/undo, `- B: <what happens, and what it costs compared with A.>`, `- C: keep things as they are: <what that costs>.` (D-840), `Refs: <precedent paths>, <sources>, <M-n>.`; then the rules Plain words, Recommendation first (adds "unless the human ruled it out in words you can quote" to the status-quo sentence, D-840), The reader decides from the brief alone, Ask at plan time, Without an answer (`anthropics/claude-code#73125`, `GUARDRAILS.md` SIGN 3), Batch at the existing stop (plan `## Decision Log`, the §5d TL;DR, triage Step 8, grouping §8; ends the turn; no polling), Advisory, not authorizing | `S5_ORDERED`, in that order; "Refs" after the recommendation | `SIGN 3 (a)`, `gate-wait-then-exit`, `§5a` |
| §6 | Upstream's §6 minus the hand-over paragraph: record once; the entry yaml with `mandatory: [M-n, …] \| none   # §4a; optional` (D-851); the pre-plan sentence without "the Step 0 intake" (av-kit has none): "A brief written before any plan file exists uses `stage: planning` and lists its unruled items under `open_decisions:`. There is no other stage value and no class alias."; the "Where it lives" table with upstream's Grouping and Closeout rows; the validator paragraph of §The §6 validator paragraph; the overturned paragraph | `S6_MARKERS` | `**every** autonomous decision`, `reconciles`, `Handed to the agent` |
| §7 | "Basis": base §8's content, upstream's wording: G24, MADR, the fs.blog door test, arXiv 2603.26233 and 2610.24411 | `S7_MARKERS` | `Anti-patterns`, `Research basis` (C2) |

Anywhere in `PROTOCOL`: no `{{PROJECT`, `lane branch` or `Handed to the agent` (`FORBIDDEN_PROTOCOL`).

#### The §4a adaptation (D-845)

Each M row keeps upstream's criterion wording, with av-kit's own source anchor. `ORACLE` fixes both as `M_ROWS` (plan review R1, F2): C3 parses each `| M-n |` row into exactly three cells and needs the row's criterion phrases in the Always-human cell and its source phrases in the Source cell, so a row that keeps its id but loses its criterion, or takes another row's source, fails (selftest F35, F36). `§Authority and Approval`, `§Independent Review` and `SIGN 3 (b)` are upstream's anchors and are refused anywhere in §4a (F37). Each row carries every listed phrase; the rest of upstream's criterion text stays as upstream wrote it.

| M | Required criterion phrases (Always-human cell) | Required source phrases (Source cell) |
|---|---|---|
| M-1 | “Push to any remote; a merge; tag; release; deploy.” | “#authority-and-approval” · “§Commits” |
| M-2 | “Destructive data operations” · “deletion of backups; secret or credential rotation; a change to who may read a secret.” | “#authority-and-approval” |
| M-3 | “**New policy**: a new or changed threshold, cap, budget, round cap or retention window” · “`.agent/review-limits.json`” · “`.agent/model-registry.local.yaml`” · “av-kit has no `stop_gate.py` or `commit_gate.py`.” · “A mechanical repair under existing policy” | “§4 test 4” |
| M-4 | “One-way doors not already in the approved plan” · “**any** external spend that the approved plan did not declare” | “`one-way-door`” |
| M-5 | “A user-visible product fork with no local canon **and** materially different plausible behaviours” | “`product-preference`” |
| M-6 | “A source conflict that the Planning Contract order” · “any conflict with a prior `USER_EXPLICIT` ruling” | “`source-conflict`” |
| M-7 | “A change to an existing test's assertion that no approved plan row specifically calls for” · “The setup-and-fixture repair carve-out stays the agent's.” | “§Testing & TDD Protocol” |
| M-8 | “A change to an approved plan's *acceptance or scope*” · “Bookkeeping rows (a receipt, a status flip, an evidence row)” | “§Planning Contract” |
| M-9 | “Review-loop exits that are already sanctioned stops: every round cap, the stagnation rule, every reviewer rung unavailable.” | “§Execution Contract” |
| M-10 | “A required **human action**” · “A transient failure the plan authorizes the agent to retry” | “`externally-blocked`” |
| M-11 | “Waiving a **blocking** quality gate, test or review step” · “Advisory floors (coverage, the security scans) stay advisory” | “§Validation Pipeline” · “§Dual-Agent Workflow” |
| M-12 | “A new external disclosure: a push to a public repository” | “#authority-and-approval” |
| M-13 | “Widening the agent's own permissions: a settings allow rule” | “`harness-profiles.md`” |
| M-14 | “Headless start, resume or fork authority” · “av-kit runs no headless sessions; starting one is this item.” | “`GUARDRAILS.md` SIGN 3” |

Where the phrases come from:

- M-1, M-2, M-12: `AGENTS.md` `#authority-and-approval` (the anchor at `AGENTS.md:7`), and §Commits (`AGENTS.md:98`) for M-1. av-kit merges nothing (main only), so M-1 reads "Push to any remote; a merge; tag; release; deploy."
- M-3: §4 test 4. The criterion names "`AGENTS.md`, `GUARDRAILS.md`, a hook, `.agent/review-limits.json`, the model registry (`.agent/model-registry.local.yaml`) or this protocol", and adds "av-kit has no `stop_gate.py` or `commit_gate.py`."
- M-4 to M-6, M-10: the §4 class table, as upstream.
- M-7: `AGENTS.md` §Testing & TDD Protocol (`:54`). M-8: §Planning Contract (`:46`). M-9: §Execution Contract (`:60`). M-11: §Validation Pipeline (`:80`) and §Dual-Agent Workflow (`:73`).
- M-13: the harness permission model (`harness-profiles.md`).
- M-14: `GUARDRAILS.md` SIGN 3 (`:33`; av-kit's SIGN 3 has no (a) or (b)). The row adds "av-kit runs no headless sessions; starting one is this item."

The mode sentence names EGRESS_PRECEDENCE (`GUARDRAILS.md:9`) for a disclosure that the plan already declares. The five notes are upstream's six minus the `human-all` note:

1. The list gates *new decisions*, never the carrying-out of rows the human already approved.
2. The list is a floor on every existing human-only gate; gates it does not name stay in force.
3. "M-3 covers edits to this list and to this protocol: they are human-approved, never autonomous." No hand-over exception (Session 86 adds it).
4. "Nothing is exempt": `hdp` still escalates every question that fails the obviousness test, M hit or not.
5. "An M hit names every matching item" (`mandatory: [M-3, M-11]`), and the brief states each.

Then upstream's closing sentence, ending "do not ask the human to confirm a choice the obviousness test already settled".

#### The §6 validator paragraph (D-850, AC-9)

The paragraph describes what Session 84's landed `VALIDATOR` checks: no more and no less. Row 1 writes this text, `ORACLE.S6_VALIDATOR`, into §6 (upstream's paragraph plus the checks av-kit already had, amended after plan review R1 Q3 for Session 84's corrected grouping-row and quoted-scalar checks). A selftest arm fails unless this quote equals `S6_VALIDATOR` word for word:

> `tools/validate_closeout_artifacts.py --reflection … --decision-source {plan} --decision-source {handoff} [--decision-source {grouping-file}] [--decision-source known-issues.yaml --decision-issue ID]` (task row H2-2) reads these records, and its messages cite this section. Each plan, handoff and issue entry must state the question, the choice and the reasoning as text, and a `chosen` that still starts with `pending` is refused. A quoted value is read without its trailing `# comment`, and a `#` inside the quotes is text. A double-quoted value is read after its escapes are decoded, so `"\n"` is blank. Each grouping row must fill its Question and Reasoning cells, and a row ruled `autonomous` or `human` must give a Chosen that is filled and does not start with `pending`; an `open` row's Chosen is not read. Two logs must give one decision the same stage. The reflection's `### Decisions Log` is not compared with them: the check refuses only the template's example line left in place, and `None.` is valid. A `decision_log:` is read only from a fenced ```yaml or `~~~yaml` block, indented or not (a handoff's section is exactly `None.` or one such block, with the template's instruction comment and closing rule allowed around it); the key in prose or in any other fence except a ```diff/```patch excerpt is refused rather than skipped. A source is a grouping by its `## 8. Open Decisions` heading (a heading inside a fence or an HTML comment is an example), or by being the file the plan's frontmatter declares as `grouping_source`, and a plan that declares one is refused unless that file is among the sources. A relative declaration resolves from the plan's project root: the nearest ancestor that holds `.agent/`, and never past the repository root (the first ancestor with `.git`). A handoff is known by its `plan_source` frontmatter or `handoff` filename, and `plan_source: null` or `~` is no value; a plan is anything else. A block outside the reader's bounded YAML grammar, a `decision_log:` nested under another key or inside a flow collection, a key written twice in one mapping, and a grouping table in an ad-hoc shape are refused rather than read as empty. `--decision-issue` is repeated once per issue; a named issue the file does not hold is refused, and naming one twice is a usage error. A decision that was made and written nowhere cannot be caught by a validator, so record it at the moment of deciding, not at closeout.

`ORACLE.TOPICS` fixes each topic's clause and its proof; the implementer supplies neither (plan review R1, F2). A clause is a substring of `S6_VALIDATOR`, each used once. An arm selector is proved by a `  ok   <arm> want=` line of the closeout selftest receipt, so a failing arm does not count; every arm named here is in the post-port arm set that Session 84's `selftest-arms-check.py` fixes (kept, flipped or added, never removed; receipt `C:/Temp/av-kit/hdp85/plan-r1-selector-probe.txt`). A test selector is proved by a `<file>::<prefix>… PASSED` line of the `pytest -v` receipt; Session 84 names its tests `test_ac_<n>_…` after its own ACs.

| Topic | Clause (a substring of `S6_VALIDATOR`) | Evidence (every one must pass) |
|---|---|---|
| question-choice-reasoning | “Each plan, handoff and issue entry must state the question, the choice and the reasoning as text” | arm `decision-blank-reasoning-in-log-refused`; arm `decision-non-text-chosen-refused` |
| pending-refused | “a `chosen` that still starts with `pending` is refused” | arm `decision-pending-chosen-refused` |
| quoted-comment | “A quoted value is read without its trailing `# comment`, and a `#` inside the quotes is text” | arm `decision-commented-pending-chosen-refused`; arm `decision-commented-empty-chosen-refused`; arm `decision-quoted-hash-text-ok` |
| dq-escapes | “A double-quoted value is read after its escapes are decoded, so `"\n"` is blank” (added in execution, D-856) | arm `decision-escaped-newline-reasoning-refused`; arm `decision-escaped-pending-chosen-refused`; arm `decision-escaped-blank-question-refused`; arm `decision-escaped-blank-chosen-refused`; arm `decision-escaped-text-ok` |
| grouping-row-fields | “Each grouping row must fill its Question and Reasoning cells” | test `test_closeout_record_once.py::test_ac_3_…`; test `test_closeout_record_once.py::test_ac_4_…` |
| grouping-ruled-chosen | “a row ruled `autonomous` or `human` must give a Chosen that is filled and does not start with `pending`; an `open` row's Chosen is not read” | arm `grouping-blank-chosen-refused`; arm `grouping-pending-chosen-refused`; arm `grouping-open-row-read` |
| same-stage | “Two logs must give one decision the same stage” | test `test_closeout_record_once.py::test_ac_8_…` |
| reflection-not-compared | “The reflection's `### Decisions Log` is not compared with them” | arm `reflection-decisions-log-link-list-ok`; test `test_closeout_record_once.py::test_ac_7_…` |
| template-example-refused | “the check refuses only the template's example line left in place” | arm `reflection-decisions-log-example-refused` |
| none-valid | “left in place, and `None.` is valid” | test `test_closeout_record_once.py::test_ac_6_…` |
| fenced-yaml-only | “A `decision_log:` is read only from a fenced ```yaml or `~~~yaml` block, indented or not” | arm `decision-tilde-yaml-fence-read`; arm `decision-indented-fence-read` |
| handoff-section-shape | “a handoff's section is exactly `None.` or one such block” | arm `handoff-separator-then-prose-refused`; arm `handoff-template-separator-none-ok` |
| prose-key-refused | “the key in prose or in any other fence” | arm `decision-bare-key-outside-fence-refused`; arm `handoff-decision-log-prose-refused`; arm `decision-text-fence-refused` |
| diff-patch-exemption | “except a ```diff/```patch excerpt is refused rather than skipped” | arm `decision-diff-excerpt-ignored-ok` |
| grouping-by-heading-or-declaration | “A source is a grouping by its `## 8. Open Decisions` heading (a heading inside a fence or an HTML comment is an example), or by being the file the plan's frontmatter declares as `grouping_source`” | arm `grouping-any-filename-read`; arm `grouping-declared-supplied-ok`; arm `grouping-fenced-example-before-real-section-read`; arm `plan-commented-heading-read-as-plan` |
| grouping-source-required | “a plan that declares one is refused unless that file is among the sources” | arm `grouping-declared-not-supplied-refused` |
| repo-boundary-root | “A relative declaration resolves from the plan's project root: the nearest ancestor that holds `.agent/`, and never past the repository root (the first ancestor with `.git`)” | arm `grouping-declared-root-resolved-read`; arm `grouping-declared-repo-boundary-read`; arm `grouping-declared-repo-boundary-outer-decoy-refused` |
| handoff-by-plan-source | “A handoff is known by its `plan_source` frontmatter or `handoff` filename” | arm `grouping-named-handoff-read-as-handoff` |
| null-plan-source | “`plan_source: null` or `~` is no value; a plan is anything else” | arm `grouping-plan-source-null-read-as-grouping`; arm `grouping-named-plan-read-as-plan` |
| bounded-grammar | “A block outside the reader's bounded YAML grammar” | arm `decision-unclosed-quote-refused` |
| nested-key-refused | “a `decision_log:` nested under another key” | arm `decision-nested-key-refused`; arm `decision-root-plus-nested-refused` |
| flow-collection-key | “or inside a flow collection” | arm `decision-flow-only-nested-refused`; arm `decision-root-plus-flow-nested-refused` |
| duplicate-key-refused | “a key written twice in one mapping” | arm `decision-duplicate-root-key-refused` |
| adhoc-grouping-refused | “a grouping table in an ad-hoc shape are refused rather than read as empty” | arm `grouping-table-wrong-shape-refused` |
| decision-issue-rules | “`--decision-issue` is repeated once per issue; a named issue the file does not hold is refused, and naming one twice is a usage error” | arm `decision-issue-same-id-twice-is-usage`; arm `decision-issue-absent-refused`; arm `decision-issue-repeated-reconciled-ok` |

`BINDING` holds one entry per topic: `{"topic"}` when the topic landed, or `{"topic", "dropped_by_s84": true, "reason"}` when Session 84 did not land it. C11 refuses an unknown topic, a topic written twice and a missing topic. For a bound topic, its clause must be in the final §6 (after whitespace folding) and **every** one of its selectors must be proved by `EVIDENCE`. For a dropped topic, its clause must be absent from §6, **none** of its selectors may be proved, and the reason must be filled. A topic with only part of its evidence is neither: it means Session 84 landed otherwise than its plan said, so row 1 stops with S2 rather than rewrite the clause or the proof. `VALIDATOR` is never edited to fit the prose (AC-18).

### `AGENTS.md` and the repin (row 3, AC-11)

In `AGENTS.md:27`, the sentence beginning "Every question for the human, at any stage, …" (through "the protocol never loosens a hard gate.") is replaced, in place on the same line, by:

> **Decide before you ask.** Before you put a question, a choice or a decision to the human, run [.agent/docs/human-decision-protocol.md](.agent/docs/human-decision-protocol.md). If it settles the decision, state your decision in one line and continue. If not, ask once, early, with your recommendation first and a do-nothing option, in plain words about outcomes, and name the precedent and the sources that you used. The protocol never loosens a hard gate.

The rest of line 27 is unchanged. `AGENTS.md` stays 126 lines (S6) and goes from 17,861 to about 17,891 bytes, under `verify_adoption.py`'s 170-line and 20,000-byte caps. Upstream added a new bullet instead; av-kit replaces its own existing sentence, so the line count and the rule block count (`after_blocks: 50`) do not move (D-844).

`docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md:183` pins `postimage_sha256` = `11309a09…7ad`, today's `AGENTS.md` work-tree bytes. `verify_adoption.py:219` compares it with `digest(AGENTS.md)` (SHA-256 of the work-tree bytes). After the edit, row 3 sets it to the new digest and changes nothing else in that file (D-846; precedent D-743). `rule-preservation.md` is CRLF and stays CRLF.

### `model-delegation.md` (row 4, AC-12)

After line 48 (the end of the "**Never delegate**" bullet), one bullet is inserted, verbatim from upstream except av-kit's line wrap is not needed:

> `- **Open decisions.** The coordinator owns each question to the human. A subagent that finds an open decision returns it with its facts and a recommendation, and does not ask the human.`

It ends CRLF like its neighbours. Line 5 keeps its bare LF (C6 checks both the bare-LF count and which line holds it).

### Templates and twins (row 2, AC-13)

Each change is made in `.agent/templates/<NAME>` and copied byte for byte to its twin (C5). Upstream's hunks are the source.

| Template (twin) | Change | Required (`ORACLE` C4) | Forbidden |
|---|---|---|---|
| `PLAN-TEMPLATE.md` (`docs/execution/plans/`) `:188-232` | The `[!WARNING]` text takes upstream's "Each consequential design decision …" + "Record them per `.agent/docs/human-decision-protocol.md` §6." + "A decision that applies an existing ruling gets no new entry."; "Precedent sweep and web research first" becomes "Precedent sweep and research first"; the brief sentence becomes "**Decision Brief** in the protocol §5 form: …". The yaml gains `mandatory: [M-n, …] \| none` (D-851). The brief example becomes Brief v2 with the C line. | `REQUIRED_TEXT[PLAN_TPL]` | `**Recommendation:** {Option A}`; "default if unanswered" (C2) |
| `REFLECTION-TEMPLATE.md` (`docs/execution/reflections/TEMPLATE.md`) `:62-71` | The comment and table become upstream's comment and the link-list example line | `REQUIRED_TEXT[REFLECTION_TPL]` | `\| ID \| Stage \| Question \|` |
| `HANDOFF-TEMPLATE.md` (`.agent/context/handoffs/TEMPLATE.md`) `:153` | Upstream's new comment. The section stays one comment plus one yaml block (C9) | `REQUIRED_TEXT[HANDOFF_TPL]` | "reconciles every entry with the reflection" (C2) |
| `TASK-TEMPLATE.md` (`docs/execution/plans/`) H2-2 `:109` | Append upstream's sentence to the Task cell | `REQUIRED_TEXT[TASK_TPL]` | — |

The task template's header row, columns and commands do not change, so `tests/tooling/test_framework_adoption.py:903` and the template-mode lint keep passing.

### Inventory: every other file (rows 5 and 6)

`ORACLE` C2 enforces the stale phrases (`STALE_EVERYWHERE`, case-insensitive) across the live tree; C1 enforces every protocol `§` citation. The plan-time hits are in `C:/Temp/av-kit/hdp85/plan-stale-lines.txt` (30 hits in 22 files) and `plan-citations.txt`.

| # | File and lines | Change |
|---|---|---|
| I1 | `AGENTS.md:27` | §`AGENTS.md` above |
| I2 | `.agent/docs/model-delegation.md` after `:48` | §`model-delegation.md` above |
| I3 | `PROTOCOL` | §The protocol rewrite |
| I4–I7 | the four templates and twins | §Templates and twins |
| I8 | `.agent/workflows/create-plan.md` `:104-105`, `:120-162`, `:143`, `:463`, `:512`, `:585` | Port upstream's create-plan hunks: step 0 sweep sources plus "Also read `.agent/context/current-focus.md`. If a prior ruling settles the question, apply it and cite it."; step 1 "**Research** each open fact …" keeping av-kit's Pomera ladder; step 4's Brief v2 block (with the C line) and "The Refs line cites the sources …"; the new rule `CP_TEST_SEARCH`; "Record each autonomous resolution once, in the plan's `## Decision Log`. …"; §3's "the closeout reads each declared D-row with stage `grouping`"; `:512` "prior decisions), research"; the §5d TL;DR's "The human decides. The recommendation never self-executes."; Step 6 item 7 (`:585`) takes upstream's link-list wording |
| I9 | `.agent/workflows/session-grouping.md:90` | The §8 header becomes `GROUPING_HEADER` (no Stage column, already av-kit's table shape) and the carry rule "the closeout reads each D-row with stage `grouping`" replaces "row without Stage … must appear in the consuming session's reflection" |
| I10 | `.agent/workflows/execution-session.md:199`, `:284` | Drop "default if unanswered"; "and what happens without an answer" becomes "and the recommendation" |
| I11 | `.agent/workflows/issue-triage.md:161-163`, `:174`, `:297-301` | The brief sentence takes the §5 v2 wording; drop "Default if unanswered: the recommendation."; drop "and in the session reflection's `### Decisions Log`" |
| I12 | `.agent/workflows/next-project.md:219` | Drop "default if unanswered" |
| I13 | `.agent/workflows/meu-handoff.md:41` | "reconciles it with the reflection" becomes "checks each entry" |
| I14 | `.agent/workflows/delegated-plan-creation.md:347` | Drop "default if unanswered" |
| I15 | `.agent/workflows/inspiration-research.md:158` | Only the "Topic too broad" row: "log the decision in the reflection's Decisions Log" becomes "record the decision per the protocol §6". Session 87 binds to this file after this edit (D-887); nothing else in the file changes |
| I16 | `.agent/workflows/tdd-implementation.md:31` | "precedent sweep, web research" becomes "precedent sweep, research" |
| I17 | `.agent/docs/issue-lifecycle-guide.md:146-183` | `:148` "web research via the harness" becomes "research"; `:153` drop "The human reads it afterwards in the session reflection"; `:182-183` record-once wording. The box diagram line at `:165` keeps its width (C10) |
| I18 | `.agent/docs/commands.md:126` | "→ web research" becomes "→ research"; drop "and the reflection's Decisions Log". Session 86 edits `:108` of this file, not `:126` |
| I19 | `.agent/docs/development-lifecycle.md:257` | As I18 |
| I20 | `.agent/docs/emerging-standards.md:842` | "surface in the reflection's `### Decisions Log`" becomes "are recorded in the stage log (protocol §6)" |
| I21 | `.agent/docs/cloud-local-collaboration.md:319` | "§Where it lives" becomes "§6" (the only invalid citation, C1) |
| I22 | `.agent/skills/completion-preflight/SKILL.md:163` | "every autonomous decision" becomes the record-once wording |
| I23 | `.agent/skills/cli-dispatch/SKILL.md:406` | Drop "default if unanswered" |
| I24 | `rule-preservation.md:183` | The repin |

The exact wording of each replacement is the implementer's, under three rules: the C2 phrase is gone, the sentence says what §6 says, and nothing else on the line changes.

#### Citations

The protocol is cited §2 ×6, §3 ×3, §4 ×3, §5 ×17 and §6 ×9 across the live tree and `tools/`. No citation names §7 or §8, so the rename moves nothing (D-841). §3 keeps its number with a new title; `harness-profiles.md:66,159` cite §3 and stay valid (D-853). `VALIDATOR` cites §6 at `:1325, :1345, :1400, :1415, :1447, :1475, :1571, :1844`, all valid.

#### Files that need no edit (D-853)

The grouping named `plan-corrections.md`, `git-workflow` and `session-meta-review`. The plan-time sweep found no stale phrase and no invalid citation in them, nor in `context-tool-decision-gate` or `harness-profiles.md`. `.agent/skills/git-workflow/SKILL.md` is shared with Session 87, which binds to it unchanged.

#### Test search (create-plan rule, `CP_TEST_SEARCH`)

`rg` over `tests/` and `tools/` for every string this plan changes (`C:/Temp/av-kit/hdp85/plan-test-strings.txt`): no test pins the protocol's text, the template comments or `AGENTS.md:27`. Three tests touch the edited files' shape, and none changes:

- `test_framework_adoption.py` checks the rule-map pin (repinned, row 3) and the line and byte caps.
- `test_framework_adoption.py:903` reads the task template's header row (unchanged).
- `test_closeout_register_grammar.py:208` builds a reflection from `VALIDATOR._GOOD_REFLECTION` (Session 84's, not the template).

No test assertion changes, so M-7 is not hit.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| A stage-log `decision_log` entry | `PROTOCOL` §6; `VALIDATOR` `decision_entries` | Upstream's keys; `mandatory:` optional (`[M-n, …]` or `none`) | `VALIDATOR` reads other keys as today; `mandatory` is not checked (D-851) |
| The reflection's `### Decisions Log` | `REFLECTION-TEMPLATE.md`; `VALIDATOR` (selftest arm `reflection-decisions-log-example-refused`) | A link list or `None.`; the template example line is refused | No row-level check |
| A Decision Brief | `PROTOCOL` §5 | `### D-n:`, `**I recommend A: …**`, options, C line, `Refs:` | Optional table when options differ on more than one point |
| `BINDING` | this plan | `topic` in `ORACLE.TOPICS`, once each; `dropped_by_s84: true` + `reason` for a drop. Clauses and evidence are `ORACLE`'s, never the binding's | Unknown, repeated and missing topics refused (C11) |

### Acceptance Criteria

Each AC is proved by the named `ORACLE` check on the live tree (row 7, the gate) and by the named planted fault in `ORACLE --selftest` (its negative test).

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | static | `PROTOCOL`'s H2 headings are exactly the eight in §The protocol rewrite, in order | Spec (`UPSTREAM`); Local Canon (D-841) | F01: an `## 8.` heading is refused by C3 |
| AC-2 | static | The head keeps av-kit's scope and carries `PROTOCOL_HEAD_MARKERS`; §1 is present | Spec (`UPSTREAM`); Local Canon (D-845) | C3 refuses a missing marker; F11: upstream's `(§5f)` is refused |
| AC-3 | static | §2 has the `current-focus.md` row first, the apply-and-cite sentence, every base sweep row and both rg receipt commands | Spec (`UPSTREAM`); Local Canon (D-842) | F08: the row missing; F09: the pwsh rg command dropped |
| AC-4 | static | §3 is "Research", with the local-measurement sentence and av-kit's ladder and angles table | Spec (`UPSTREAM`); Local Canon (D-842) | C3 refuses a missing `S3_MARKERS` entry |
| AC-5 | static | §4 equals `BASE`'s §4 except `S4_OLD` → `S4_NEW` | Spec (`UPSTREAM`) | F02: criterion 4 deleted; F03: a class-table row edited |
| AC-6 | static | §4a: `hdp` only, M-1 to M-14 once each in order, each row carrying its own `M_ROWS` criterion phrases and its own av-kit source phrases; none of `S4A_FORBIDDEN`; "Five notes:" with five bullets, no `human-all` | Human-approved (D-843); Local Canon (D-820, D-845) | F04: `human-all`; F05: M-9 missing; F12: four notes; F35: M-7's criterion removed, its id kept; F36: M-7 and M-11 sources swapped; F37: M-14 cites upstream's `SIGN 3 (b)` |
| AC-7 | static | §5 has `S5_ORDERED` in order, with the C line; no `SIGN 3 (a)`, `gate-wait-then-exit` or `§5a` | Spec (`UPSTREAM`); Local Canon (D-840, D-845) | F06: Refs before the recommendation; F07: `SIGN 3 (a)` |
| AC-8 | static | §6 has `S6_MARKERS` and none of `S6_FORBIDDEN`; no hand-over paragraph | Spec (`UPSTREAM`); Local Canon (D-851) | F10: the hand-over paragraph |
| AC-9 | static | §6 states `S6_VALIDATOR`'s clauses: each `ORACLE.TOPICS` topic is bound, with its fixed clause in §6 and every one of its fixed selectors passing in `EVIDENCE`, or dropped, with its clause absent, none of its evidence present and a reason | Local Canon (D-850, D-855) | F31: a fixed clause missing from §6; F32: an arm that FAILs in the receipt; F33: a topic missing; F34: a dropped check still stated; F38: a drop while Session 84's evidence is present; F39: §6 holding only the record-once opening; F40: a test that FAILED; F41: an unknown topic; the plan-quote arm (this plan's §6 quote equals `S6_VALIDATOR`) |
| AC-10 | static | §7 "Basis" carries `S7_MARKERS`; "Anti-patterns" and "Research basis" are gone from `PROTOCOL` | Spec (`UPSTREAM`) | F18: "Research basis" kept (C2) |
| AC-11 | static | `AGENTS.md` holds `AGENTS_NEW` and not `AGENTS_OLD`; 126 lines; ≤ 20,000 bytes; the rule-map digest equals `AGENTS.md`'s; `test_framework_adoption.py` passes | Human-approved (D-844); Local Canon (D-846) | F19: old sentence kept; F26: a line added; F27: stale digest |
| AC-12 | static | `model-delegation.md` holds `DELEGATION_NEW`; line 5 stays bare LF; every other line stays CRLF | Spec (`UPSTREAM`); Local Canon (D-847) | F20: bullet missing; F25: line 5 made CRLF; F25b: the bare LF moved |
| AC-13 | static | The four templates hold `REQUIRED_TEXT` and none of `FORBIDDEN_TEXT`; each twin is byte-identical; the handoff Decision Log is one comment plus one yaml block; the template-mode task lint passes; `VALIDATOR --selftest` reports 0 failures | Spec (`UPSTREAM`); Local Canon (D-840, D-851) | F22: the reflection table kept; F23: a twin differs; F29: prose in the handoff Decision Log |
| AC-14 | static | `create-plan.md` and `session-grouping.md` hold their `REQUIRED_TEXT` (including `CP_TEST_SEARCH` and `GROUPING_HEADER`) and not `**Recommendation:** {Option A}` | Spec (`UPSTREAM`) | F21: the test-search sentence missing |
| AC-15 | static | Every protocol `§` citation in the live tree and `tools/` names §1 to §7 or §4a | Local Canon (D-841, D-852) | F13: §8; F14: §Where it lives; F15: a range ending at §9; F16: §2B |
| AC-16 | static | No `STALE_EVERYWHERE` phrase in the live tree; no `STALE_PROTOCOL_ONLY` phrase in `PROTOCOL` | Local Canon (D-852) | F17: a stale phrase in a template |
| AC-17 | static | Each EDITED file keeps its row-0 work-tree line endings (C6); no uncensused numeric model name in an EDITED file (C8); the `issue-lifecycle-guide.md` boxes keep their line lengths (C10) | Local Canon (D-854; the CRLF rule) | F24: CRLF → LF; F28: an uncensused model pin; F30: a box width changed |
| AC-18 | static | Scope: `scope-check.py --check` passes. Every changed path is in EDITED, this plan folder or the closeout artifacts, or dirty at row 0 with its row-0 hash; `VALIDATOR`'s hash equals row 0's; HEAD equals `baseline.sha` | Local Canon (D-850; S4) | `scope-check.py --selftest`: a dirty path changed, a new out-of-scope file, a validator change and a moved HEAD are each refused |
| AC-19 | static | `ORACLE --selftest`, `scope-check.py --selftest`, `identity.py --selftest` and `s84-landed.py --selftest` report 0 failures | Local Canon (D-848) | Each selftest's planted faults; a selftest that cannot refuse its faults fails itself |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| The protocol's structure and wording | Spec | `UPSTREAM` |
| Which local steps stay | Local Canon | D-842 |
| The §4a list and its av-kit sources | Human-approved | D-843; D-845 |
| The `AGENTS.md` rule | Human-approved | D-844 |
| The do-nothing option in Brief v2 | Local Canon | D-840 |
| What the §6 validator paragraph may say | Local Canon | D-850: Session 84's landed checks: `S6_VALIDATOR`, with each clause proved by its fixed `TOPICS` evidence (`BINDING` records only drops) |
| The template text | Spec | Upstream's template hunks |
| Citation and stale-phrase scope | Local Canon | D-852 |

#### Files Modified

All 28 are CRLF in the work tree and stay CRLF (`C:/Temp/av-kit/hdp85/plan-eol.txt`); `model-delegation.md` line 5 stays bare LF.

| File | Action | Row | Summary |
|------|--------|-----|---------|
| `.agent/docs/human-decision-protocol.md` | modify | 1 | §The protocol rewrite |
| `.agent/templates/PLAN-TEMPLATE.md`, `docs/execution/plans/PLAN-TEMPLATE.md` | modify | 2 | I4 |
| `.agent/templates/REFLECTION-TEMPLATE.md`, `docs/execution/reflections/TEMPLATE.md` | modify | 2 | I5 |
| `.agent/templates/HANDOFF-TEMPLATE.md`, `.agent/context/handoffs/TEMPLATE.md` | modify | 2 | I6 |
| `.agent/templates/TASK-TEMPLATE.md`, `docs/execution/plans/TASK-TEMPLATE.md` | modify | 2 | I7 |
| `AGENTS.md` | modify | 3 | I1 |
| `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md` | modify | 3 | I24, one digest |
| `.agent/docs/model-delegation.md` | modify | 4 | I2 |
| `.agent/workflows/create-plan.md`, `session-grouping.md`, `execution-session.md`, `issue-triage.md`, `next-project.md`, `meu-handoff.md`, `delegated-plan-creation.md`, `inspiration-research.md`, `tdd-implementation.md` | modify | 5 | I8 to I16 |
| `.agent/docs/issue-lifecycle-guide.md`, `commands.md`, `development-lifecycle.md`, `emerging-standards.md`, `cloud-local-collaboration.md` | modify | 6 | I17 to I21 |
| `.agent/skills/completion-preflight/SKILL.md`, `.agent/skills/cli-dispatch/SKILL.md` | modify | 6 | I22, I23 |

`current-focus.md` already carries the triage workstream's uncommitted hunks (`baseline-dirty.txt`); H1-3 changes only this session's lines.

### Project files

- **Plan-local scripts** (all in this plan folder):
  - `hdp-check.py` (`ORACLE`)
  - `scope-check.py` (S3, S4, AC-18)
  - `s84-landed.py` (S2; reuses Session 84's read-only `port-check.py`)
  - `identity.py` (a copy of Session 84's, with this plan's values)
  - `baseline.ps1`
  - `session-gate.ps1`, written at H1-2
- **Written by rows:** `baseline.sha`, `baseline-dirty.txt`, `baseline-content.txt`, `eol-baseline.json` (row 0); `validator-binding.json` (row 1).
- **State:**
  - `docs/execution/metrics.md`
  - `.agent/context/current-focus.md`
  - the handoff
  - the rolling reviews
  - the reflection
  - `C:/Temp/av-kit/session-86-prompt.md`, outside the repository

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| §5a expert pass, the expert-pass skill, the peer-reviewer agent and routing rows, the §6 hand-over rule and the M-3 hand-over exception | deferred | — | Session 86 (`hdp-expert-pass`, grouping D-821) |
| `tools/validate_closeout_artifacts.py` and its tests | out-of-scope | — | Session 84 landed them; this session only reads them (D-850, AC-18) |
| `human-all`, `run_parameters`, `create-plan.md` Step 0 intake | out-of-scope | — | D-820, D-733 |
| Upstream `AGENTS.md` Planning Contract rewording (`:46` upstream) | out-of-scope | — | av-kit's Planning Contract line does not name the protocol's steps; line 27 carries the rule (D-844) |
| The standing commit grant and the commit gate | out-of-scope | — | D-825 |
| Old plans, handoffs and reflections that use the old brief form | out-of-scope | — | History; the protocol governs new decisions |
| `.agent/workflows/inspiration-research.md` beyond `:158`; `.agent/skills/git-workflow/SKILL.md` | out-of-scope | — | Session 87 owns them (grouping §2) |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU, so `docs/BUILD_PLAN.md` and `meu-status.yaml` don't change. Both are dirty from the triage workstream and are only hashed (S4). H1-3 proves the hub is a no-op:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/hdp85/hdp-render-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/hdp85/hdp-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following, fail-fast except where noted:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. **S2:** `s84-landed.py` (`S84_LANDED`): Session 84's `port-check.py` finds its port shape in `VALIDATOR` and its files' endings (the identifiers Session 84 writes, not this plan's labels), every status cell of Session 84's `task.md` is `[x]`, and its handoff and reflection exist. A reflection alone is not proof (plan review R1 Q6). Otherwise exit 12. Step 5 then needs its fresh selftest and tests to pass.
3. **S3:** `scope-check.py --record`. Every EDITED file equals `BASE` once CRLF is read as LF, or exit 10. It writes `baseline-content.txt`: HEAD, `VALIDATOR`'s SHA-256, and the SHA-256 of every path that is dirty and outside this session's scope.
4. `hdp-check.py --eol-snapshot eol-baseline.json`: the EDITED files' work-tree endings (28 files, 28 CRLF, `model-delegation.md` mixed at plan time).
5. **`EVIDENCE`:** `VALIDATOR --selftest` under the user's own temp (`hdp-base-closeout-selftest.txt`), which must exit 0 and say ` 0 failure`; then `pytest -v` of `tests/tooling/test_closeout_record_once.py` and `tests/tooling/test_closeout_register_grammar.py` (`hdp-base-s84-tests.txt`), exit 0. A failure is S2.
6. `uv sync --frozen --all-packages`, then the base Python suite (`hdp-base-py.txt`, `TMP` at `C:/Temp/av-kit/hdp85/tmp`), recorded, not fatal.
7. `meu_status.py render --check`; the selftests of `identity.py`, `scope-check.py`, `s84-landed.py` and `hdp-check.py`.
8. **Red:** `hdp-check.py --eol-baseline eol-baseline.json` (`hdp-red.txt`) must exit 1. At plan time it fails C1 (1), C2 (38), C3 (63) and C4 (29), with C5 to C10 ok, and C11 refuses because no binding exists yet.

Its last line is `baseline: all steps as expected`.

### 2. Rows 1 to 7

Each row ends with the `ORACLE` checks it owns, run with `--checks`, plus C6 on every row (no row may change an ending). Rows 2 to 5 also pass `--paths` with the row's own files: `ORACLE` then counts only the failures that name those files and prints the rest as deferred. Every message of C1, C2 and C4 to C10 names its file. Rows 1 to 6 do not need the whole oracle green; row 7 does.

| Row | Checks |
|---|---|
| 1 | `--checks C3,C6,C11 --binding validator-binding.json --evidence-receipt <both EVIDENCE receipts>` |
| 2 | `--checks C4,C5,C6,C9 --paths <the eight template files>`; the template-mode task lint; `VALIDATOR --selftest` |
| 3 | `--checks C4,C6,C7 --paths AGENTS.md,<rule-preservation.md>`; `pytest tests/tooling/test_framework_adoption.py` |
| 4 | `--checks C4,C6 --paths .agent/docs/model-delegation.md` |
| 5 | `--checks C2,C4,C6 --paths <the nine workflow files>` |
| 6 | `--checks C1,C2,C6,C8,C10`, over the whole tree |
| 7 | All of C1 to C11 with the binding and evidence; the `ORACLE` selftest; `scope-check.py --check` |

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape (`2026-11-14-review-limits-no-token-budget/session-gate.ps1`):

- It writes one receipt per step in `C:/Temp/av-kit/hdp85/`, named `hdp-D6-<step>`.
- It is fail-fast, and prints later steps as `not_run`.
- Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `tools-lint` (`ruff check` on `hdp-check.py`, `scope-check.py` and `s84-landed.py`); `task-contract` (this `task.md`, and `--template-mode` on `.agent/templates/TASK-TEMPLATE.md`); `scope-paths` (`scope-check.py --check`); `hdp-check` (all checks with binding and evidence); `hdp-check-selftest`; `scope-check-selftest`; `s84-landed-selftest` |
| Targeted | `adoption` (`pytest tests/tooling/test_framework_adoption.py`); `closeout-selftest` (`VALIDATOR --selftest`, ` 0 failure`) |
| Fresh full | `py-tests` (the full suite, `TMP` at `C:/Temp/av-kit/hdp85/tmp` as in row 0); `state-render` |
| Skipped, with reason | `py-lint`, `py-types`: nothing under `packages/` or `tests/` changes. `ui-*`: nothing under `ui/` changes. `mcp-*`: no MCP change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build |

`py-tests` excuses only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Session 84 is not closed, or landed otherwise than its plan: `s84-landed.py` exits 12 (the port shape or endings `port-check.py` checks, an open Session 84 task row, or its handoff or reflection missing), its fresh selftest or tests fail, or a `TOPICS` topic has only part of its evidence (row 1) | Stop; don't start. Session 85 runs only after Session 84 |
| S3 | An EDITED file at row 0 differs from `BASE` (CRLF read as LF) | Stop; another session changed a file this plan edits. Re-plan the affected rows with Mat |
| S4 | Any of these happens:<br>• `HEAD` moves from `baseline.sha`<br>• a path outside this session's scope and `baseline-content.txt` changes<br>• a `baseline-content.txt` path changes content<br>• `VALIDATOR` changes | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | An edited line would hold a numeric model name the routing census does not list (C8) | Stop; reword without the pin |
| S6 | `AGENTS.md`'s line count would change | Stop; the edit must stay on line 27 (D-844) |
| S7 | Codex is unavailable or the ledger refuses | Mat |
| S8 | A step would commit, push, merge, release, run a destructive data operation, disclose anything externally or touch credentials | Stop and report; Mat's default acceptance doesn't cover it |

## Decision Log

> [!WARNING]
> **D-843 and D-844 are the two human-gated decisions**, below as Decision Briefs in the v2 form this plan adopts. Mat accepted the defaults in advance ("Run HDP on any decisions that come up and and I approving acceptance of the defaults.", 2026-11-15), so each is recorded with its recommendation as `chosen`. That acceptance does not cover commit, push, merge, release, destructive data operations, external disclosure or credentials (S8).
>
> **D-840 to D-842 and D-845 to D-855** passed the obviousness test as two-way choices. The grouping rows D-818, D-819, D-820, D-821 and D-824 bear on this session; under the new §6 the closeout reads them from the grouping file, so they are not restated.

### D-843: Should av-kit's protocol name the decisions that are always Mat's, whatever the obviousness test says?

**I recommend A: add upstream's list of fourteen always-human decisions (§4a), with each source pointing at av-kit's own rule.** Today the only guard is the §4 test, and an agent that misreads it can decide a policy change or a test-assertion change by itself. The list makes those a lookup, not a judgment. It adds nothing new to the rules: every item restates a gate av-kit already has (`AGENTS.md`, `GUARDRAILS.md`, the review limits). How A can fail: a source anchor goes stale when `AGENTS.md` is reorganised, and C1-style checks don't cover anchors. Undo is one section delete.

- B: change only §4's wording and add no list. Smaller diff, but the protocol keeps relying on the agent to spot a governance change, which is the gap Zorivest closed.
- C: keep things as they are: av-kit's protocol and upstream's drift further apart, and Session 86's hand-over rule, which names M-3, M-5, M-6 and M-8, has nothing to point to.

Refs: `UPSTREAM` §4a; `P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md` (AC-940.4); grouping D-820; M-3.

### D-844: Should `AGENTS.md` carry the decide-before-you-ask rule?

**I recommend A: replace the protocol sentence on `AGENTS.md:27` with the decide-before-you-ask rule, keeping the do-nothing option.** Codex reads only `AGENTS.md`, and today's sentence sends it to "web research" and to a reflection Decisions Log that Session 84 stopped checking. Mat's global instructions already hold this rule (Zorivest MEU-941), so this aligns Codex with Claude. The line stays line 27, so the line count and the rule-block count don't move; only the rule-map digest is repinned. How A can fail: a reader who relied on the step list in the old sentence must follow the link. Undo is one line.

- B: add a new bullet, as upstream did. It grows `AGENTS.md` by a line and a rule block, and leaves the stale sentence on line 27, so two rules would disagree.
- C: keep things as they are: Codex keeps reading "web research" and the reflection Decisions Log, which the protocol no longer uses.

Refs: `AGENTS.md:27`; upstream `core/AGENTS.md` (`a73d6df`); `P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md:293` (MEU-941); `rule-preservation.md:183`; M-3.

```yaml
decision_log:
  - id: D-840
    stage: planning
    question: "Does av-kit's Brief v2 keep a do-nothing option, which upstream's brief block lacks?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Yes. The brief block gains '- C: keep things as they are: <what that costs>.', and the Recommendation-first rule says the status quo stays unless the human ruled it out in words you can quote"
    source_tag: Local Canon
    precedents: ["AGENTS.md:27 — today's rule requires a do-nothing option", ".agent/docs/human-decision-protocol.md:132-170 — av-kit's current brief has one", "UPSTREAM §5 — 'Keep the status quo is an option when it is real'"]
    research: { engine: none, sources: [] }
    reasoning: "av-kit already requires the option, and Mat's briefs keep it unless he rules it out. Upstream's 'when it is real' left it to the writer, which is how it got dropped before. Two-way: the line can go later."
  - id: D-841
    stage: planning
    question: "How are the protocol's sections numbered after the rewrite?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "§1 to §7 plus §4a, as upstream: §7 Anti-patterns is removed and §8 Research basis becomes §7 Basis"
    source_tag: Local Canon
    precedents: ["UPSTREAM headings", "C:/Temp/av-kit/hdp85/plan-citations.txt — no citation names §7 or §8"]
    research: { engine: none, sources: [] }
    reasoning: "Matching upstream keeps future syncs a diff, and the citation sweep shows nothing cites §7 or §8, so no reference moves. Keeping §7 Anti-patterns lost: upstream folded those into §4 and §5."
  - id: D-842
    stage: planning
    question: "Which av-kit-only steps does the rewrite keep?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The §2 sweep table and both rtk proxy rg receipt commands, the §3 Pomera ladder and the angles table"
    source_tag: Local Canon
    precedents: [".agent/docs/human-decision-protocol.md:31-100 — the local sweep and ladder", "grouping Session 85 'av-kit's local sweep sources, rg receipt commands and Pomera research steps stay'"]
    research: { engine: none, sources: [] }
    reasoning: "Upstream dropped them as project-specific; for av-kit they are the project. The grouping already says they stay."
  - id: D-843
    stage: planning
    question: "Should av-kit's protocol name the decisions that are always Mat's, whatever the obviousness test says?"
    resolution: human
    class: governance-value
    mandatory: [M-3]
    chosen: "Option A: add upstream's §4a list of M-1 to M-14 with av-kit's own sources, hdp the only mode"
    source_tag: Human-approved
    precedents: ["UPSTREAM §4a", "P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md — AC-940.4", "grouping D-820 — hdp only"]
    research: { engine: none, sources: [] }
    reasoning: "The list turns governance changes into a lookup and restates only gates av-kit already has. B leaves the gap Zorivest closed; C drifts from upstream and leaves Session 86's hand-over rule nothing to name."
    human_message_reference: "USER_EXPLICIT 2026-11-15 \"Run HDP on any decisions that come up and and I approving acceptance of the defaults.\""
  - id: D-844
    stage: planning
    question: "Should AGENTS.md carry the decide-before-you-ask rule?"
    resolution: human
    class: governance-value
    mandatory: [M-3]
    chosen: "Option A: replace the protocol sentence on AGENTS.md:27 with the rule, keeping the do-nothing option, and repin the rule-map digest"
    source_tag: Human-approved
    precedents: ["AGENTS.md:27", "P:/agentic-framework a73d6df core/AGENTS.md", "P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md:293 — MEU-941", "docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md:183"]
    research: { engine: none, sources: [] }
    reasoning: "Codex reads only AGENTS.md, and today's sentence names steps the protocol drops. In place, the line and block counts hold. B leaves two disagreeing rules; C leaves Codex on the old process."
    human_message_reference: "USER_EXPLICIT 2026-11-15 \"Run HDP on any decisions that come up and and I approving acceptance of the defaults.\""
  - id: D-845
    stage: planning
    question: "How are upstream's Zorivest-specific parts adapted?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "§4a sources name av-kit's AGENTS and GUARDRAILS anchors, review-limits.json, the local registry overlay and harness-profiles.md; the pre-plan sentence drops 'Step 0 intake'; the TL;DR is §5d and reviewer questions §5e; no gate-wait-then-exit; SIGN 3 without (a); the M-3 note has no hand-over exception"
    source_tag: Local Canon
    precedents: ["AGENTS.md:7,46,54,60,73,80,98", "GUARDRAILS.md:9,33 — EGRESS_PRECEDENCE; SIGN 3 has no (a) or (b)", ".agent/workflows/create-plan.md:437,503 — §5d round cap, §5e edge cases", "grouping D-820"]
    research: { engine: none, sources: [] }
    reasoning: "Each upstream name either points at Zorivest machinery av-kit lacks or at a number that differs here. Copying them would make every citation false. The hand-over exception belongs to Session 86."
  - id: D-846
    stage: planning
    question: "How is the rule-preservation digest kept true after the AGENTS.md edit?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Repin rule-preservation.md:183 postimage_sha256 to verify_adoption's digest of the edited AGENTS.md; after_blocks stays 50"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-26-framework-update-adoption/checks/verify_adoption.py:46,219", "D-743 — the earlier repin"]
    research: { engine: none, sources: [] }
    reasoning: "The pin exists to catch an unreviewed AGENTS.md edit; this edit is reviewed, so the pin moves with it, as D-743 did."
  - id: D-847
    stage: planning
    question: "How is the open-decisions bullet added to model-delegation.md?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Verbatim from upstream, after the Never delegate bullet at :48, CRLF; line 5 stays bare LF"
    source_tag: Local Canon
    precedents: ["P:/agentic-framework a73d6df core/.agent/docs/model-delegation.md", ".agent/docs/model-delegation.md:46-48"]
    research: { engine: none, sources: [] }
    reasoning: "Session 86 binds to this bullet's content, so it must match upstream word for word."
  - id: D-848
    stage: planning
    question: "How is a prose-only port verified?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "One read-only plan-local oracle, hdp-check.py, with checks C1 to C11 and a planted-fault selftest; plus scope-check.py for S3, S4 and AC-18"
    source_tag: Local Canon
    precedents: ["P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md:474-530 — HD1-D3, one oracle with a planted-fault selftest", "docs/execution/plans/2026-11-14-review-limits-no-token-budget/prose-check.py"]
    research: { engine: none, sources: [] }
    reasoning: "Prose has no tests, so the required and forbidden texts become checks, and the selftest proves each check can fail. Repo tests lost: they would pin wording the protocol may change later."
  - id: D-849
    stage: planning
    question: "What does this session's own reflection list, and what does H2-2 pass?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The new link-list form with only this session's reversible choices; H2-2 passes the plan, the handoff and the declared grouping as --decision-source, and no issue"
    source_tag: Local Canon
    precedents: ["UPSTREAM §6 Closeout row", "docs/execution/plans/2026-11-15-closeout-record-once/task.md H2-2"]
    research: { engine: none, sources: [] }
    reasoning: "The session adopts the new rule, so its reflection follows it. The plan declares the grouping, so the validator needs that file among the sources."
  - id: D-850
    stage: planning
    question: "How does §6's validator paragraph stay true to the validator Session 84 lands?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Bind each clause to a landed selftest arm or test id through validator-binding.json (C11); drop a clause with no evidence; never edit the validator"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-closeout-record-once/implementation-plan.md — its arm list", "Session 84 Out of Scope — the protocol is Session 85's"]
    research: { engine: none, sources: [] }
    reasoning: "The paragraph describes code written in another session. Binding to that session's receipts keeps prose and code equal. Editing the validator here lost: it is Session 84's, and AC-18 holds it fixed. Amended after plan review R1 (F2, Q3): the paragraph is fixed as ORACLE.S6_VALIDATOR, with Session 84's corrected grouping-row and quoted-scalar checks; each clause and its proof are fixed in ORACLE.TOPICS, not chosen by the implementer; a bound topic needs every one of its selectors, a drop needs none, and partial evidence is S2."
  - id: D-851
    stage: planning
    question: "Is the new mandatory: field required in a decision_log entry?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Optional: written as [M-n, …] or none; the PLAN template yaml is otherwise unchanged; the validator does not check it"
    source_tag: Local Canon
    precedents: ["UPSTREAM §6 — 'omitted when the plan has no run_parameters block'", "grouping D-820 — no run_parameters in av-kit"]
    research: { engine: none, sources: [] }
    reasoning: "Requiring it would refuse every existing log; upstream already makes it optional for plans without run parameters, which is every av-kit plan."
  - id: D-852
    stage: planning
    question: "Which files do the citation and stale-phrase checks cover?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "The live tree (AGENTS, GUARDRAILS, PROJECT-PROFILE, CLAUDE, .agent docs, workflows, skills, templates, roles, agents and the template twins) plus tools/ for citations; not .agent/context history or .agent/fleet"
    source_tag: Local Canon
    precedents: ["grouping Session 85 Gate — 'covers every human-decision-protocol.md § citation in the tree'", "MEMORY — never open .agent/fleet/hub"]
    research: { engine: none, sources: [] }
    reasoning: "Live instructions must agree with the protocol; history records what was true then and is never rewritten."
  - id: D-853
    stage: planning
    question: "Do the grouping's other named files need edits?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "No: plan-corrections.md, git-workflow, session-meta-review, context-tool-decision-gate and harness-profiles.md hold no stale phrase and no invalid citation"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/hdp85/plan-stale-lines.txt", "C:/Temp/av-kit/hdp85/plan-citations.txt"]
    research: { engine: native, sources: ["local measurement — rg sweep of the live tree, 2026-11-15"] }
    reasoning: "The grouping named them by search before the stale list was fixed; the measured sweep finds nothing to change. Editing them anyway lost: it would add diff without effect, and git-workflow is Session 87's."
  - id: D-854
    stage: planning
    question: "What does the line-ending check compare against?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A work-tree snapshot taken at row 0 (--eol-snapshot), not the git blobs"
    source_tag: Local Canon
    precedents: [".gitattributes '* text=auto' with core.autocrlf=true — blobs LF, work tree CRLF", "C:/Temp/av-kit/hdp85/plan-eol.txt"]
    research: { engine: native, sources: ["local measurement — Python bytes of the 28 files, 2026-11-15"] }
    reasoning: "The blobs are LF, so comparing with them would flag every CRLF file. The snapshot also catches model-delegation's one bare LF moving."
  - id: D-855
    stage: planning
    question: "Where does the §6 binding's evidence come from?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "Row 0 runs the landed validator's selftest and pytest -v of Session 84's tests itself, and C11 reads those receipts"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-15-closeout-record-once/task.md row 6 — Session 84's own receipts, cro-*"]
    research: { engine: none, sources: [] }
    reasoning: "Fresh receipts prove what is on disk now; Session 84's receipts could predate a later correction. Reusing them lost for that reason. Amended after plan review R1 (F1, Q6): before the receipts, row 0 proves Session 84 landed with s84-landed.py, which reuses Session 84's read-only port-check.py (its own identifiers, not this plan's labels) and needs every Session 84 task row done and its handoff and reflection written; a reflection alone is not proof."
```

## Research References

- Upstream change: `P:/agentic-framework` commit `a73d6df`, `core/.agent/docs/human-decision-protocol.md`, `core/templates/`, `core/AGENTS.md`, `core/.agent/workflows/create-plan.md`, `core/.agent/docs/model-delegation.md`. Primary.
- Zorivest's port: `P:/zorivest/docs/execution/plans/2026-11-07-hd1-human-decision-protocol/implementation-plan.md` (HD1-D1 to HD1-D3 at `:474-530`; MEU-941 at `:293`; AC-940.4).
- The protocol's own basis, kept in §7: MADR (https://adr.github.io/madr/), the one-way and two-way door test (https://fs.blog/reversible-irreversible-decisions/), "Ask or Assume?" (arXiv 2603.26233), the earlier-answers check (arXiv 2610.24411).
- The popup-timeout issue cited in §5: `anthropics/claude-code#73125`.

## Planning receipts

All are under `C:/Temp/av-kit/hdp85/`. Each probe was read-only with respect to the repository.

- **`plan-selftest.txt`.** `hdp-check.py --selftest`: the all-green tree passes; F01 to F34, F25b and the C11 arms each refused; the `--paths` filter keeps the named file and defers the rest; 0 failures.
- **`plan-paths-probe.txt`.** `--checks C4,C6 --paths .agent/docs/model-delegation.md` on today's tree: 1 failure (the missing bullet), 28 deferred.
- **`plan-red.txt`.** The oracle on today's tree: exit 1, 131 failures (C1 1, C2 38, C3 62, C4 29, C11 not run); C5 to C10 ok.
- **`plan-eol.txt`, `plan-eol-snapshot.json`.** 28 files, 28 CRLF; `model-delegation.md` mixed (one bare LF, line 5).
- **`plan-stale-lines.txt`.** 30 stale-phrase hits in 22 files.
- **`plan-citations.txt`.** Every protocol `§` citation; one invalid (`cloud-local-collaboration.md:319`).
- **`plan-test-strings.txt`.** No test pins a string this plan changes.
- **`plan-template-lint.txt`.** The task template passes the template-mode lint today.
- **`plan-task-lint.txt`.** This `task.md` passes `lint_task_contract.py`: 25 rows, 23 fully checked, 2 `view_file` rows exempt.
- **`plan-scope-probe.txt`.** `scope-check.py`'s record logic, not written: 28 EDITED files, 0 differ from `BASE`; 29 dirty paths outside scope.
- **Selftests:** `plan-identity-selftest.txt`, `plan-scope-selftest.txt`, both 0 failures.
- **`plan-ruff.txt`.** `hdp-check.py` and `scope-check.py` are clean.
- **Not run at plan time:** row 0 (Session 84 has not landed), any edit, the binding.

### After plan review R1

Same folder; each probe read-only with respect to the repository.

- **`plan-r1-selftest.txt`.** `hdp-check.py --selftest`: 46 arms, 0 failures. New: F35 to F37 (C3, `M_ROWS` and `S4A_FORBIDDEN`), F38 to F41 and a real-drop arm (C11, fixed `TOPICS`), and the arm that this plan quotes `S6_VALIDATOR` word for word.
- **`plan-r1-selector-probe.txt`.** Every `TOPICS` arm selector is in Session 84's post-port arm set (kept, flipped or added; none removed or absent); exit 0.
- **`plan-r1-red.txt`.** The oracle on today's tree: exit 1, 132 failures (C1 1, C2 38, C3 63, C4 29, C11 not run); C5 to C10 ok. C3 gained one: today's §3 lacks the "When web research is needed" lead-in.
- **`plan-r1-paths-probe.txt`.** As before: 1 failure, 28 deferred.
- **`plan-r1-s84-landed-selftest.txt`.** `s84-landed.py --selftest`: 12 arms, 0 failures. The corrected port passes; the pre-port source and four half-ports (`_quoted_scalar_text` missing, `_unquote` still called, `DECISIONS_LOG_HEADERS` back, `grouping_decisions` not calling `grouping_row_problems`) are refused; an open, a `[B]` and an absent status row are refused; a missing reflection is refused.
- **`plan-r1-s84-landed-live.txt`.** `s84-landed.py` on today's tree: exit 12, 45 problems. Right: Session 84 has not landed.
- **Selftests:** `plan-r1-identity-selftest.txt`, `plan-r1-scope-selftest.txt`, both 0 failures; the scope selftest's commits now pass `-c commit.gpgsign=false` (R1 Q7).
- **`plan-r1-ruff.txt`.** `hdp-check.py`, `scope-check.py` and `s84-landed.py` are clean.
- **`plan-r1-task-lint.txt`.** This `task.md` passes `lint_task_contract.py`.
- **`plan-r1-eol.txt`.** Every file in this folder is LF, as before.

## Validation stage contract

- **Static:** `tools-lint`, `task-contract`, `scope-paths`, `hdp-check`, `hdp-check-selftest`, `scope-check-selftest`.
- **Targeted:** each row's `--checks` subset (§Verification Plan 2); `adoption`; `closeout-selftest`.
- **Fresh full:** `py-tests`, `state-render`.
- **Identity:** from `identity.py`, independent of the receipts.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
