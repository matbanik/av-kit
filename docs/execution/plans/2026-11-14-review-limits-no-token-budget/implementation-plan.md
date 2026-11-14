---
project: "2026-11-14-review-limits-no-token-budget"
date: "2026-11-14"
source: "P:/agentic-framework commit 6dd76b7 (docs/execution/plans/2026-10-20-review-limits-parameters/)"
meus: []
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Review loops stop on rounds, not tokens

> **Project**: `2026-11-14-review-limits-no-token-budget`
> **Build Plan Section(s)**: none (tooling and governance prose; no MEU)
> **Status**: `draft`

---

## Goal

**Goal anchor:** Review loops in av-kit stop on their round caps and never on token spend, while every round's token usage is still recorded and shown.

Mat asked on 2026-11-14 to "integrate the run parameters that would allow us to not have budget and only keep round limits". The upstream framework added this as commit `6dd76b7` in `P:/agentic-framework` ("setup choices and plan parameters for review limits"). av-kit's ledger predates it:

- `tools/review_ledger.py:87` and `:100` hard-code `ROUND_BUDGETS` and `TOKEN_BUDGETS`.
- `begin` always writes an integer `token_budget` (`:743-747`).
- `tokens_spent` (`:448`) reads `ledger.get("token_budget") or TOKEN_BUDGETS[...]`, so even a zero or null budget falls back to the default. A token stop cannot be turned off.

Every recent session has had Mat set or raise an execution token budget by hand (D-698 "50M", D-712 30M, D-727 33M, D-729 53M). This plan ports the upstream ledger change and adds `.agent/review-limits.json` with `token_budgets: "off"`. The round caps stay plan 3 and execution 6. The governance prose that states the caps as fixed numbers is changed to name where the number comes from.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls, 2026-11-14). A headroom binary is on PATH, but every payload here is source code or exact prose that must be read verbatim (the ledger, the upstream diff, 22 inventory lines), which is a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`, with receipts under `C:/Temp/av-kit/rl/` named `rl-*`, `RECEIPTS_DIR=C:/Temp/av-kit`, `PYTHONIOENCODING=utf-8` and `ELECTRON_RUN_AS_NODE` cleared.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`, under ledger loops `rl-plan-2026-11-14-review-limits-no-token-budget` and `rl-execution-2026-11-14-review-limits-no-token-budget`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable or the ledger refuses a round, the fallback is Mat. Each round is metered, and the coordinator warns before dispatching.
- **Token budgets of this session's own loops (D-737).** The plan loop opens under today's ledger, so it opens with `--token-budget 45000000` (three rounds at the measured high of about 15M). The execution loop opens after row 4, under the new ledger and `.agent/review-limits.json`, so it has no token budget. That `begin` is the first real use of the change.
- **Never in these rows without Mat's words:** commit, push, or author an `approved` verdict.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| Review limits (no MEU) | `.agent/context/handoffs/2026-11-14-review-limits-no-token-budget-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-14-review-limits-no-token-budget-plan-critical-review.md` and `.agent/context/handoffs/2026-11-14-review-limits-no-token-budget-implementation-critical-review.md`. The single non-MEU handoff follows `2026-11-05-closeout-register-grammar`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, `rl-base-*.txt`, `selftest-arms-before.txt` |
| WP-2 | Tests Red, then the ledger port Green (rows 1 to 4) | WP-1 | shared | `tests/tooling/test_review_limits.py`, `tools/review_ledger.py`, `.agent/review-limits.json` |
| WP-3 | Prose, templates and AGENTS (rows 5 to 7) | WP-2 | shared | The 11 prose files, `prose-check.py` |
| WP-4 | Runtime checks (row 8) | WP-3 | shared | `rl-existing-ledgers.txt`, `rl-gate-only.txt` |
| WP-5 | Closeout (H1, H2) | WP-4 | `compact_continue` | Handoff, review, reflection |

## User Review Required

> [!IMPORTANT]
> **What changes for every later session.** With `.agent/review-limits.json` saying `"token_budgets": "off"`, a new review loop never stops on tokens. Each round's usage is still recorded from its receipt, and `state` prints `tokens: off (N spent, not budgeted)`. The round caps don't change: plan 3, execution 6, discovery 2, handoff 3, multi-handoff 3. A round past the cap still needs a named human's `review_ledger.py continue --rounds N`.
>
> **What you can still do.** A per-loop token budget is still possible: `begin --token-budget N` tightens "off" to N for that one loop. `continue --tokens N` is refused on a loop with no budget, because there is nothing to lift. Switching budgets back on for the whole repo is one value in `.agent/review-limits.json` (`"on"`). The `tokens` map stays in the file, so the old defaults come back without retyping them.
>
> **What this plan leaves out.** Upstream's `tools/run_parameters.py` (the typed-offer check behind a plan that loosens its caps), the credits USD caps and `scripts/instantiate.py` aren't ported (D-733). A plan block may only keep or tighten the repo's limits. A block marked `loosened` is refused with a message that names `continue` as the way to get more rounds.
>
> **Loops that are already open.** All 92 ledgers under `C:/Temp/av-kit/review-ledger` hold an integer `token_budget` (read-only survey, 2026-11-14). Each keeps its budget. Row 8 proves each one still loads.
>
> **Two lines in `AGENTS.md` and `PROJECT-PROFILE.md` change wording** (§Prose inventory rows P20 and P21). The rule stays the same; only the source of the number is named.
>
> **The token estimate.** The upstream ledger diff is 501 added lines, and the prose is 22 short edits. Recent sessions' review rounds cost 5M to 15M tokens each. Expect 1 or 2 plan rounds and 1 or 2 execution rounds, about 10M to 50M tokens in all.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `LEDGER` | `tools/review_ledger.py`. |
| `LIMITS_FILE` | `.agent/review-limits.json`. |
| `UPSTREAM` | `git -C P:/agentic-framework show 6dd76b7 -- core/tools/review_ledger.py`, the diff being ported. |
| `OFF` | The string `"off"` as a `token_budget` value: the loop has no token stop. |
| `PLAN_BLOCK` | The optional `review_limits` mapping in a plan's frontmatter, read from `begin --ac-file`. |
| `INVENTORY` | The 22 rows in §Prose inventory, each a file, a line and the phrase it holds today. |

### The limits file

`LIMITS_FILE` is new, LF, with these exact values:

```json
{
  "schema": "review-limits/1",
  "token_budgets": "off",
  "rounds": {"plan": 3, "execution": 6, "discovery": 2, "handoff": 3, "multi-handoff": 3},
  "tokens": {"plan": 10500000, "execution": 21000000, "discovery": 7000000, "handoff": 10500000, "multi-handoff": 10500000}
}
```

### The ledger port

`UPSTREAM` is ported function by function, not by `patch`. A plan-time dry run (`C:/Temp/av-kit/rl/patch-dry-run.txt`) applied 19 of 22 hunks with offsets, but hunks 19 to 21 landed 650 lines away with fuzz 2, so placement can't be trusted. Hunks 9 (`stops`), 10 (`stop_readout`) and 22 (the parser) failed. Each change goes into the function it belongs to:

- **Constants.** `REVIEW_LIMITS_SCHEMA`, `REVIEW_LIMITS_FILE`, `REVIEW_LIMITS_KEYS`, `TOKEN_SWITCH`, `REPO_ROOT`, `PLAN_LIMIT_MODES`, `PLAN_LIMIT_KEYS`, `PLAN_BASES`, the plan-block regexes, `RUN_PARAMETERS`. `LEDGER_KEYS` gains `limits_source`.
- **Reading the limits.** `read_repo_limits`, `load_repo_limits`, `_limit_text`, `_looser`, `_frontmatter`, `load_plan_limits`, `_repo_mode_limits`, `plan_basis`, `run_limits_check`, `verified_limits`, `resolve_limits`, as upstream.
- **One change from upstream (D-733).** `resolve_limits` checks `RUN_PARAMETERS.is_file()` before it runs `limits-check`. When it is absent, a `loosened` block is refused with `review_limits basis 'loosened' needs tools/run_parameters.py, which this repo does not have; a plan may only keep or tighten .agent/review-limits.json, and more rounds come from review_ledger.py continue`.
- **Loading a ledger.** `load_ledger` refuses a `token_budget` that is neither `"off"` nor an integer of at least 1, and a malformed `limits_source`. Both refusals are exit 3.
- **The token stop.** `tokens_spent` uses `ledger.get("token_budget", TOKEN_BUDGETS[mode])` and returns `"off"` as the budget when it is `OFF`. `stops` adds no `tokens` stop when the budget is `OFF`. `stop_readout` prints `tokens: off (N spent, not budgeted)`.
- **Commands.** `begin` takes its limits from `resolve_limits` and prints `tokens=` and `source=`, plus `plan=` and `flags=` when they apply. The `mode=` and `budget=` fields stay where they are. `continue --tokens` on an `OFF` loop is refused. `state` prints the token line and a `limits:` line, or `(pre-review-limits ledger)` for a ledger without `limits_source`. `evaluate`'s OK line doesn't change, so `Invoke-CodexDispatch.ps1:474` still reads `mode=`.
- **Flags.** `--round-budget` (a count of at least 1) and `--token-budget N|off` may only tighten what the file and the block say.
- **Selftest.** Upstream's `limits-*` arms come over, with the temp `REPO_ROOT` and `run_limits_check` swap they use. The D-733 check runs first, so the two upstream arms that mock `run_limits_check` (`limits-loosened-needs-limits-check` and `limits-loosened-other-block-refused`) also point `RUN_PARAMETERS` at an inert scratch file for their duration and restore it afterwards. Without that they would get the D-733 refusal instead of the message they test. This changes a fixture, not an expectation, and no prior arm is touched, so it is not S5. One new arm, `limits-loosened-without-run-parameters`, points `RUN_PARAMETERS` at a missing path and needs the message above. All 105 arms that exist today stay (AC-12).
- **The docstring and usage text** name `LIMITS_FILE` and `--token-budget N|off`.
- **Line endings.** `LEDGER` stays CRLF, written with `newline=""`.

### Templates (D-734)

`PLAN-TEMPLATE.md` and `TASK-TEMPLATE.md` go to `template_version: "2.3"` and gain the optional block as commented frontmatter lines:

```yaml
# review_limits:            # optional (v2.3): equal in plan and task; absent = .agent/review-limits.json
#   schema: review-limits/1
#   plan_rounds: 3          # integer >= 1, at most rounds.plan
#   execution_rounds: 6     # integer >= 1, at most rounds.execution
#   plan_tokens: off        # integer >= 1 or off; a number tightens off
#   execution_tokens: off
#   basis: tightened        # repo (every value equal) | tightened (none looser)
```

A literal copy of the template therefore carries no block. Neither the strict block parser nor the closeout validator's flat `frontmatter()` (`tools/validate_closeout_artifacts.py:156`, which skips `#` lines) reads it. The task template's `{configured-cap}` note in H1-7a and H1-7b says to copy the execution cap from `review_ledger.py state --loop-id <execution loop>` (base budget plus every `continue` grant). `create-plan.md` §4 gets the upstream "Review limits" paragraph, without the `run-parameters-offer/2` path. In its place it says that more rounds come from `continue`.

### Prose inventory

Each row's old phrase is replaced with a phrase that names the source of the cap and keeps its default: `review_limits` in the plan, else `rounds.<mode>` in `.agent/review-limits.json`, default N, printed by `review_ledger.py state`. The wording follows upstream's for the same line where upstream has one. `prose-check.py` holds this table as data.

| Row | File:line | Phrase today |
|---|---|---|
| P1 | `.agent/workflows/create-plan.md:430` | `Plan review round cap: 3 rounds.** If the review loop reaches 3 rounds` |
| P2 | `.agent/workflows/create-plan.md:437` | `Plan review reached 3 rounds without approval.` |
| P3 | `.agent/workflows/create-plan.md:518` | `Round cap reached (3 rounds)` |
| P4 | `.agent/workflows/create-plan.md:586` | `round cap (6)` |
| P5 | `.agent/workflows/create-plan.md:591` | `**Round cap: 6 rounds**` |
| P6 | `.agent/workflows/delegated-plan-creation.md:37` | `round cap (3)` |
| P7 | `.agent/workflows/delegated-plan-creation.md:250` | ``--review-mode plan` is what sets the cap of 3`` |
| P8 | `.agent/workflows/delegated-plan-creation.md:332` | ``--review-mode plan` is 3 rounds`` |
| P9 | `.agent/workflows/delegated-plan-creation.md:346` | `If 3 rounds without approval` |
| P10 | `.agent/workflows/execution-session.md:64` | `the 3-round cap` |
| P11 | `.agent/workflows/execution-session.md:191` | ``(`ROUND_BUDGETS`, execution = 6), token budget (`TOKEN_BUDGETS`)`` |
| P12 | `.agent/docs/development-lifecycle.md:55` | `(≤3 rounds)` |
| P13 | `.agent/docs/development-lifecycle.md:74` | `(≤6 rounds)` |
| P14 | `.agent/docs/development-lifecycle.md:278` | `(max 3 rounds before T2 escalation)` |
| P15 | `.agent/docs/development-lifecycle.md:287` | `3 non-approved rounds → T2 escalation` |
| P16 | `.agent/docs/development-lifecycle.md:372, 378, 380` | `(max 6 rounds before T2 escalation)`; `6 non-approved rounds → T2 escalation`; `7th autonomous round` |
| P17 | `.agent/docs/development-lifecycle.md:920, 922` | `→ ≤3 rounds, agent loops`; `→ ≤6 rounds, agent loops` |
| P18 | `.agent/docs/issue-lifecycle-guide.md:314` | `a 6-round cap` |
| P19 | `.agent/skills/cli-dispatch/SKILL.md:407` | `capped at 3 rounds` |
| P20 | `AGENTS.md:66` | `Initial ledger caps: plan 3, execution 6;` |
| P21 | `PROJECT-PROFILE.md:37` | `plan: 3 · execution: 6` |
| P22 | `.agent/docs/model-routing.md:23` | `(plan 3, execution 6)` |

Three `begin` examples also gain the limits sentence, and `--ac-file` where it is missing, so that a plan block is read at all: `delegated-plan-creation.md:244`, `validation-review.md:40-46` and `cli-dispatch/SKILL.md:283`. `execution-session.md:183` already passes `--ac-file` and gains the sentence only.

- **P20.** It becomes `Initial ledger caps come from .agent/review-limits.json (plan 3, execution 6; token budgets off);`. It is the same rule with its source named. `AGENTS.md` stays at 126 lines and under 20,000 bytes (17,805 today).
- **P21.** It becomes `plan: 3 · execution: 6 · token budgets: off (.agent/review-limits.json)`.
- **Unchanged.** The svg diagram and the historical plans, handoffs and reflections aren't touched. They record what was true when they were written.

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `LIMITS_FILE` | `read_repo_limits` in `LEDGER` | `schema` = `review-limits/1`; `token_budgets` in `on`/`off`; `rounds` and `tokens` each have exactly the five modes; each round an int ≥ 1 (bool refused); each token an int ≥ 1; no duplicate keys | Unknown key refused, exit 3 |
| `PLAN_BLOCK` | `load_plan_limits` | `schema`, `plan_rounds`, `execution_rounds` (int ≥ 1), `plan_tokens`, `execution_tokens` (int ≥ 1 or `off`), `basis` in `repo`/`tightened`/`loosened`; equal in `task.md` when that file holds one | Unknown key, bad value or a `basis` the values contradict refused, exit 3 (UPSTREAM `FailClosed`); a block that differs from `task.md` refused, exit 1 |
| `begin --round-budget`, `--token-budget` | `_count_arg`, `_budget_arg` | Count ≥ 1; budget int ≥ 1 or `off`; tighten only | argparse exit 2 |
| Ledger JSON | `load_ledger` | `token_budget` is `"off"` or an int ≥ 1; `limits_source` keys in `repo`/`plan`/`flags` | Unknown key refused, exit 3 |

### Acceptance Criteria

Tests are `tests/tooling/test_review_limits.py`, named `test_ac_<n>_…`. CLI tests copy `LEDGER` into a temp root, the same pattern as `tests/tooling/test_framework_adoption.py:506`, so `REPO_ROOT` is the temp root and the test writes its own `LIMITS_FILE`. Unit tests import that copy.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-1 | unit | `LIMITS_FILE` holds exactly the values in §The limits file, its `tokens` map equals `TOKEN_BUDGETS`, and `read_repo_limits(REPO_ROOT)` accepts it | Human-approved (D-730, D-731) | A copy with `token_budgets` `"on"`, or `rounds.plan` 4, fails the equality check |
| AC-2 | integration | With a `LIMITS_FILE` that says `off`, `begin` for each of the five modes writes `round_budget` = `rounds[mode]`, `token_budget` = `"off"` and `limits_source.repo`; its OK line holds `mode=<mode>`, `budget=<N> `, `tokens=off` and `source=` | Spec (UPSTREAM AC-5) | With no `LIMITS_FILE`, the same `begin` writes `TOKEN_BUDGETS[mode]` and prints `source=constants` |
| AC-3 | integration | A malformed `LIMITS_FILE` makes `begin` exit 3 and write no ledger | Spec (UPSTREAM AC-6) | Eight files: wrong `schema`; a missing mode; an extra key; round 0; round `true`; `token_budgets` `"maybe"`; token 0; a duplicate key |
| AC-4 | unit | For a ledger whose `token_budget` is `OFF`, `stops()` returns no `tokens` stop for any recorded usage (up to 10^12), and `stop_readout` holds `off (` and `not budgeted` | Spec (UPSTREAM AC-10) | The same ledger with `token_budget` 1 returns a `tokens` stop |
| AC-5 | integration | `state` on a loop just opened under an `off` file exits 0 and prints `off (0 spent, not budgeted)` and a `limits:` line naming the repo file | Spec (UPSTREAM AC-10) | A ledger with no `limits_source` prints `(pre-review-limits ledger)` |
| AC-6 | integration | `continue --tokens 1` on an `OFF` loop exits 1, names that there is no token budget to lift, and leaves the ledger bytes unchanged; `continue --rounds 1` on the same loop exits 0 and raises the cap by 1 | Spec (UPSTREAM AC-11) | The `--tokens` case is the negative |
| AC-7 | unit | An `OFF` loop still stops at its round cap: with `round_budget` rounds recorded, `stops()` returns a `budget` stop | Human-approved (D-730: "only keep round limits") | With one round fewer, no `budget` stop |
| AC-8 | integration | `state` exits 3 on a ledger whose `token_budget` is 0, null, -1, `true`, `"none"` or 1.5, or whose `limits_source` has an unknown key | Spec (UPSTREAM AC-12) | A ledger with an integer budget and no `limits_source` exits 0 |
| AC-9 | integration | A `PLAN_BLOCK` in the `--ac-file` frontmatter applies to plan and execution loops: `tightened` with `plan_rounds: 2` gives budget 2 and prints `plan=`; `repo` with equal values is accepted; a discovery loop ignores the block | Spec (UPSTREAM AC-7, AC-8) | Refused with no ledger written. Exit 3: a `basis` its values contradict; an unknown key; `plan_rounds: 0`; `plan_tokens: maybe`. Exit 1: a block that differs from the sibling `task.md` (`differs between`) |
| AC-10 | integration | A `loosened` block (`plan_rounds: 4` against 3) is refused with exit 1 and the D-733 message, and no ledger is written | Local Canon (D-733) | The message must name `continue`; a raw `can't open file` output fails the test |
| AC-11 | integration | Flags only tighten: `--round-budget 2` gives budget 2 and `flags=round_budget`; `--token-budget 5000000` under an `off` file gives 5,000,000 | Spec (UPSTREAM AC-9) | `--round-budget 4` is refused (`only tighten`); `--token-budget off` under an `on` file is refused; `--round-budget 0`, `--token-budget 0` and `--token-budget abc` exit 2 |
| AC-12 | unit | `LEDGER selftest` exits 0 with 0 failures. Every arm name in `selftest-arms-before.txt` (row 0) is still present, and the upstream `limits-*` arms and `limits-loosened-without-run-parameters` are there | Local Canon (V31: a selftest must not shrink) | A missing prior arm name fails `selftest-arms-check.py` |
| AC-13 | integration | `Invoke-CodexDispatch.ps1 -GateOnly` against a plan loop opened under the new ledger, with budgets `off`, exits 0 and prints `dispatch kind 'plan'` and `-GateOnly: gate result`. `Test-CliDispatch.ps1` completes, and `dispatch-check.py` accepts its receipt: every FAIL is one of the two baseline ids | Local Canon (`Invoke-CodexDispatch.ps1:474` reads `mode=`) | `dispatch-check.py --selftest` refuses three fixtures: the real baseline receipt plus one added `[FAIL]` record; an empty receipt with exit 64 (the suite never started); a receipt whose `Total:` line disagrees with its records |
| AC-14 | unit | `prose-check.py`: no `INVENTORY` phrase remains in its file, and each of those lines, plus the four `begin` examples, names `.agent/review-limits.json` or `review_limits`; `AGENTS.md` has at most 126 lines and fewer than 20,000 bytes | Local Canon (single-statement rule; AGENTS size limits) | `prose-check.py --selftest` feeds a line `capped at 3 rounds` and an `AGENTS.md` of 127 lines and must refuse both |
| AC-15 | unit | Both templates say `template_version: "2.3"`, hold the commented block, and none of its lines is live YAML; the task template's cap note names `review_ledger.py state`; `lint_task_contract.py` and `validate_closeout_artifacts.py --selftest` still pass | Local Canon (D-734) | A template with an uncommented `review_limits:` line fails the check |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Resolution order (file, then block, then flags) and tighten-only | Spec | `UPSTREAM` `resolve_limits` |
| `off` is looser than any number | Spec | `UPSTREAM` `_looser` |
| What av-kit does without `run_parameters.py` | Local Canon | D-733 |
| Whether the template block is live or commented | Local Canon | D-734 |
| av-kit's own values | Human-approved | D-730, D-731 |
| Existing open ledgers | Spec | `UPSTREAM` keeps a pre-change ledger loadable; row 8 proves it on all 92 |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `tools/review_ledger.py` | modify | The port (§The ledger port) |
| `.agent/review-limits.json` | new | `token_budgets: off`; rounds 3/6/2/3/3; the tokens map |
| `tests/tooling/test_review_limits.py` | new | AC-1 to AC-11 |
| `docs/execution/plans/PLAN-TEMPLATE.md`, `TASK-TEMPLATE.md` | modify | v2.3, the commented block, the cap note |
| `.agent/templates/PLAN-TEMPLATE.md`, `.agent/templates/TASK-TEMPLATE.md` | modify | Added at execution (D-742): byte copies of the two templates above, which `verify_adoption.py` requires to be identical (`test_framework_adoption.py`) |
| `docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md` | modify | Added at execution (D-743, Mat): `counts."AGENTS.md".postimage_sha256` set to the hash of `AGENTS.md` after P20, which `verify_adoption.py:213-221` checks |
| `.agent/workflows/create-plan.md` | modify | P1 to P5; the §4 Review limits paragraph |
| `.agent/workflows/delegated-plan-creation.md` | modify | P6 to P9; the `begin` example |
| `.agent/workflows/execution-session.md` | modify | P10, P11; the `begin` sentence |
| `.agent/workflows/validation-review.md` | modify | The `begin` example |
| `.agent/docs/development-lifecycle.md` | modify | P12 to P17 |
| `.agent/docs/issue-lifecycle-guide.md` | modify | P18 |
| `.agent/docs/model-routing.md` | modify | P22 |
| `.agent/skills/cli-dispatch/SKILL.md` | modify | P19; the `begin` example |
| `AGENTS.md`, `PROJECT-PROFILE.md` | modify | P20, P21 |

### Project files

Plan-local scripts, all in this plan folder: `baseline.ps1`, `red-check.py`, `identity.py`, `selftest-arms-check.py`, `prose-check.py`, `dispatch-check.py`, `ledger-survey.py`, `session-gate.ps1`. State: `docs/execution/metrics.md`, `.agent/context/current-focus.md`, the handoff, the rolling reviews and the reflection.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `tools/run_parameters.py` and the `run-parameters-offer/2` schema | out-of-scope | — | D-733: av-kit has no run-parameters tool; Mat's request is for no token budget, not for loosening caps |
| `claude-credits` USD caps and `credits_state.py` | out-of-scope | — | av-kit has no credits skill (`ls .agent/skills`, 2026-11-14); D-733 |
| `scripts/instantiate.py`, `ADOPTION-QUESTIONS.md`, `MANIFEST.md`, `refcheck.py` | out-of-scope | — | Framework-only setup files that av-kit does not carry; D-733 |
| The two baseline failures in `Test-CliDispatch.ps1` (`placeholder receipts dir refused`, `refusal created no placeholder dir`) | out-of-scope | — | They fail before this change (`C:/Temp/av-kit/rl/pester-plan-time.txt`) in the receipts-dir guard, which this plan doesn't touch; reported to Mat at closeout |
| The `development-lifecycle` svg diagram and historical plans, handoffs and reflections | out-of-scope | — | They record past state; P1 to P22 cover the live rules |
| `tools/check_exec_review.py --max-round` and `validate_closeout_artifacts.py --max-review-rounds` | out-of-scope | — | Both already take the cap as an argument (`grep`, 2026-11-14); the task template's cap note feeds them |

## BUILD_PLAN.md Audit

This project adds no build-plan section and changes no MEU (`meu_status.py stats`: 143 MEUs, 139 complete, `C:/Temp/av-kit/rl/meu-stats.txt`), so `docs/BUILD_PLAN.md` and `meu-status.yaml` don't change. H1-3 proves the hub is a no-op:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/rl/rl-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/rl/rl-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Records `HEAD` in `baseline.sha` and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt`.
2. Checks that `LEDGER`'s SHA-256 equals the plan-time value, which row 0 records from `git show HEAD:tools/review_ledger.py`. If the file differs from `HEAD`, S4 applies.
3. Runs `LEDGER selftest` (`rl-base-selftest.txt`, 105 arms at plan time), and writes the sorted arm names to `selftest-arms-before.txt`.
4. Runs `uv sync --frozen --all-packages` and the base Python suite (`rl-base-py.txt`), with `TMP` and `TEMP` at `C:\Temp\av-kit\rl\tmp`.
5. Runs `Test-CliDispatch.ps1` (`rl-base-dispatch.txt`, with its exit in `rl-base-dispatch.txt.exit`) and checks it with `dispatch-check.py --exact-baseline`, which requires exactly the two FAIL ids named in §Out of Scope.
6. Runs the `red-check.py`, `identity.py`, `prose-check.py` and `dispatch-check.py` selftests. The first two are copied from `2026-11-05-closeout-register-grammar` with this plan's `PLAN` and `PROJECT_ARTIFACTS`.

**`dispatch-check.py`** reads a `Test-CliDispatch.ps1` receipt and the suite's exit, which the caller saves to `<receipt>.exit` straight after the run. It accepts only when all of these hold:

- the receipt has the suite's `Total: N | PASS: p FAIL: f SKIP: s` line;
- the `[PASS]`, `[FAIL]` and `[SKIP]` records, parsed as `^\s*\[(PASS|FAIL|SKIP)\] (.+?) \([0-9.]+s\) - `, agree with those counts;
- N is at least 31, the plan-time total;
- every FAIL name is one of the two baseline ids (with `--exact-baseline`, the FAIL set must equal the pair);
- the exit is 0 when f is 0 and 1 when f is above 0, which is how the suite ends (`Test-CliDispatch.ps1:1133`). Any other exit, such as a startup failure, is refused.

Its `--selftest` builds its fixtures from row 0's `rl-base-dispatch.txt`, which step 5 has just checked. It must accept that receipt with exit 1, and refuse the three negative fixtures in AC-13. Row 8 and the session gate's `dispatch-tests` step use this check.

### 2. Red then Green (rows 1 to 4)

- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require test_ac_<n>` matches exactly.
- **AC-7 and AC-8's positive case pass in Red by design.** They guard what Green could break. Row 1 requires AC-1 to AC-6 and AC-9 to AC-11.
- **AC-1 fails in Red** because `LIMITS_FILE` doesn't exist. Row 3 writes it.
- **AC-12 has no Red.** It is the selftest plus `selftest-arms-check.py`, run in row 4.
- **Expectations stay immutable in Green.** `LEDGER` keeps its CRLF line endings: it is measured with Python bytes and written with `newline=""`.

### 3. Prose (rows 5 to 7)

`prose-check.py` holds `INVENTORY` and the four `begin` examples as data. It reads each file as bytes, refuses any file whose line endings changed from CRLF, and checks AC-14. With `--templates` it also checks AC-15's template conditions. Row 7 also runs `lint_task_contract.py` on this plan's `task.md` and the closeout validator's selftest, for AC-15.

### 4. Runtime (row 8)

- **`ledger-survey.py`** copies every `C:/Temp/av-kit/review-ledger/*.json` to `C:/Temp/av-kit/rl/survey/review-ledger/`, then runs `LEDGER state` on each copy with `RECEIPTS_DIR=C:/Temp/av-kit/rl/survey`. Every one must exit 0. The live ledgers are only read.
- **AC-13.** A loop opened under `RECEIPTS_DIR=C:/Temp/av-kit/rl/gate` is checked with `Invoke-CodexDispatch.ps1 -GateOnly`, with `-PromptText` set to the probe loop's goal anchor, because the wrapper needs a prompt before it reaches the gate. The dispatch test script then runs, and `dispatch-check.py` reads its receipt and its exit.

### Session gate (H1-2)

`session-gate.ps1` follows the peer's shape. It writes one receipt per step in `C:/Temp/av-kit/rl/`, named `rl-D6-<step>`. It is fail-fast, prints later steps as `not_run`, and its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `tools-lint` (`ruff check tools/review_ledger.py tests/tooling/`, clean at plan time: `rl/ruff-plan-time.txt`), `py-lint` (`ruff check packages/ tests/`), `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `prose-check`, `red-check-selftest` |
| Targeted | `ledger-selftest` and `selftest-arms-check.py`, `review-limits-tests` (`pytest tests/tooling/test_review_limits.py`), `dispatch-tests` (`Test-CliDispatch.ps1`, then `dispatch-check.py` on its receipt and exit) |
| Fresh full | `py-tests` (the full suite, which runs `LEDGER selftest` through `test_framework_adoption.py:265`), `state-render`, `closeout-selftest` |
| Skipped, with reason | `py-types`: `pyright packages/`, and nothing under `packages/` changes. `ui-*`: nothing under `ui/` changes. `mcp-*`: no MCP change. `openapi`: no `packages/api` change (H1-4). `build-record`: no build |

`py-tests` excuses only ids that row 0's receipt shows failing.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | An upstream hunk depends on code av-kit doesn't have, and porting it would change behavior outside the limits | Stop; bring the hunk and the options to Mat |
| S3 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S4 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan's files changes | Stop and re-baseline with Mat; never commit, stash or revert another session's work |
| S5 | A prior selftest arm would have to be removed or changed to pass | Stop; that is a behavior change outside the goal. Bring it to Mat |
| S6 | `ledger-survey.py` finds an existing ledger that no longer loads | Stop; open loops must keep working |
| S7 | Codex is unavailable or the ledger refuses | Mat |

## Decision Log

> [!WARNING]
> Every decision here is autonomous except D-730, D-737 and D-739, which rest on Mat's words of 2026-11-14. Mat's request rules out the do-nothing option.

```yaml
decision_log:
  - id: D-730
    stage: planning
    question: "Does av-kit keep token budgets on review loops?"
    resolution: human
    class: governance-value
    chosen: "No. .agent/review-limits.json sets token_budgets to off; usage is still recorded and printed, and a per-loop --token-budget N stays available"
    source_tag: Human-approved
    precedents: ["P:/agentic-framework commit 6dd76b7 — token_budgets on|off is a setup choice", "tools/review_ledger.py:448 — today a budget cannot be turned off"]
    research: { engine: none, sources: [] }
    reasoning: "Mat asked for exactly this. Keeping the per-loop flag costs nothing and leaves a way to cap one costly loop."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'I want to integrate the run parameters that would allow us to not have budget and only keep round limits.'"
  - id: D-731
    stage: planning
    question: "What are av-kit's round caps?"
    resolution: autonomous
    class: two-way
    chosen: "Unchanged: plan 3, execution 6, discovery 2, handoff 3, multi-handoff 3"
    source_tag: Local Canon
    precedents: ["PROJECT-PROFILE.md:37 — B5 plan 3, execution 6", "tools/review_ledger.py:87 — ROUND_BUDGETS"]
    research: { engine: none, sources: [] }
    reasoning: "Mat said to keep the round limits. The file writes today's constants down, so no loop's cap changes."
  - id: D-732
    stage: planning
    question: "Does the limits file keep a tokens map while budgets are off?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, equal to TOKEN_BUDGETS"
    source_tag: Local Canon
    precedents: ["P:/agentic-framework core/.agent/review-limits.json — the schema requires both maps"]
    research: { engine: none, sources: [] }
    reasoning: "The upstream schema refuses a file without it. Turning budgets back on is then a one-word change."
  - id: D-733
    stage: planning
    question: "Is run_parameters.py ported for plans that loosen a cap?"
    resolution: autonomous
    class: two-way
    chosen: "No. A loosened block is refused with a message naming continue; credits caps and instantiate.py stay out too"
    source_tag: Local Canon
    precedents: ["ls tools/ — av-kit has no run_parameters.py", "AGENTS.md:66 — rounds past a cap come from a named human's continuation"]
    research: { engine: none, sources: [] }
    reasoning: "The request is about removing the token stop. Upstream's run_parameters.py is about 7,000 lines, and the human-typed offer flow it guards isn't used in av-kit. A named human's continue already covers more rounds. The resolve_limits hook stays, so a later port only needs to add the tool."
  - id: D-734
    stage: planning
    question: "Is the template's review_limits block live YAML or commented?"
    resolution: autonomous
    class: two-way
    chosen: "Commented lines, so a literal copy of the template carries no block"
    source_tag: Local Canon
    precedents: ["P:/agentic-framework core/templates/PLAN-TEMPLATE.md — upstream writes it live with brace placeholders", "tools/validate_closeout_artifacts.py:156 — the flat frontmatter reader skips # lines"]
    research: { engine: none, sources: [] }
    reasoning: "A live block of placeholders would make begin refuse every plan that kept it unfilled, and av-kit plans are written from the template. Commented lines document the block with no effect until a planner uncomments them."
  - id: D-735
    stage: planning
    question: "Does av-kit rewrite the prose that states the caps as fixed numbers?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, the 22 INVENTORY rows and four begin examples, with upstream's wording where upstream has it"
    source_tag: Local Canon
    precedents: [".agent/workflows/delegated-plan-creation.md:250 — 'one place to change it and no prose copy to drift'", "P:/agentic-framework 6dd76b7 — the same lines rewritten upstream"]
    research: { engine: none, sources: [] }
    reasoning: "The numbers don't change, but a plan block can now tighten them, so a fixed number in prose becomes a second statement that can be wrong for a given loop."
  - id: D-736
    stage: planning
    question: "How is the ledger ported, and where are the tests?"
    resolution: autonomous
    class: two-way
    chosen: "Function by function from UPSTREAM, keeping all 105 arms and adding upstream's limits arms; CLI tests in tests/tooling/test_review_limits.py on a temp copy of the ledger"
    source_tag: Local Canon
    precedents: ["C:/Temp/av-kit/rl/patch-dry-run.txt — 3 hunks fail and 3 land 650 lines away", "tests/tooling/test_framework_adoption.py:506 — the temp-copy pattern", "pyproject.toml:28 — testpaths is tests"]
    research: { engine: none, sources: [] }
    reasoning: "patch would misplace three hunks. A temp copy gives each test its own REPO_ROOT and LIMITS_FILE without touching the repo's."
  - id: D-737
    stage: planning
    question: "What token budget do this session's own loops use?"
    resolution: human
    class: governance-value
    chosen: "The plan loop, under today's ledger, opens with --token-budget 45000000; the execution loop opens under the new ledger and has none"
    source_tag: Human-approved
    precedents: ["current-focus.md — D-727 33M and D-729 53M, Mat-set budgets for one session's loops"]
    research: { engine: native, sources: ["https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentcost07-bp01.md — cap both iterations and token spend; supports budgets in general, not this number"] }
    reasoning: "Today's default of 10.5M would have refused plan round 2 (7.2M spent plus a 7.2M reserve), and round 2 approved. 45M is three rounds at the measured high. The round cap of 3 still binds. As first written, this entry cited Mat's request 'not have budget and only keep round limits' as approval of 45M; that request names no number, so the coordinator set the number itself. Mat ratified it after the plan review (2026-11-14 Decision Brief, recommendation A): the plan loop spent 11,809,568 of 45,000,000 in two rounds."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'proceed as recommended'"
  - id: D-738
    stage: planning
    question: "What does the session gate cover?"
    resolution: autonomous
    class: two-way
    chosen: "Identity, lint over the ledger, tests and packages, the task contract, scope paths, the prose check, the ledger selftest with the arm check, the new tests, the dispatch tests, the full Python suite, the state render and the closeout validator's selftest; types, UI, MCP, OpenAPI and the build are skipped"
    source_tag: Local Canon
    precedents: [".agent/docs/commands.md:190-207 — the D6 stages", "docs/execution/plans/2026-11-05-closeout-register-grammar/implementation-plan.md — the same shape for a tooling session"]
    research: { engine: none, sources: [] }
    reasoning: "Only a Python tool, one JSON file, one test file and Markdown change. The dispatch wrapper reads the ledger's output, so its tests run."
  - id: D-739
    stage: plan-review
    question: "Does this plan fix the two Test-CliDispatch.ps1 tests that fail before the change?"
    resolution: human
    class: two-way
    chosen: "No. The plan stays as approved, with the baseline pair allowed by dispatch-check.py; closeout registers the defect as a known issue for its own session"
    source_tag: Human-approved
    precedents: ["P:/agentic-framework core/.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:619 — the fixture's path holds the literal PROJECT_NAME token in double curly braces", ".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:565 — instantiation replaced it with av-kit, so the guard (:162, matches two opening curly braces) sees a real path; the leftover %TEMP%/av-kit/receipts/dispatch-tests keeps the second arm failing"]
    research: { engine: native, sources: ["https://arxiv.org/pdf/2212.00908 — a test that always fails is fixed, not quarantined", "https://docs.trunk.io/flaky-tests/quarantining/index.md — known failures keep running outside the gate, with an expiry"] }
    reasoning: "The guard works; the fixture is wrong. Fixing it here would reopen an approved plan and spend the plan loop's last round. Registering it keeps it tracked; any new FAIL still fails dispatch-check."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'proceed as recommended'"
  - id: D-740
    stage: plan-review
    question: "Does the plan's count of 92 live ledgers need correcting after the reviewer counted 93?"
    resolution: autonomous
    class: two-way
    chosen: "No change. task.md row 8 surveys every ledger present when it runs; 92 is a dated planning observation"
    source_tag: Local Canon
    precedents: ["task.md row 8 — ledger-survey.py copies every C:/Temp/av-kit/review-ledger/*.json with no fixed count", ".agent/context/handoffs/2026-11-14-review-limits-no-token-budget-plan-critical-review.md Q3 — the reviewer calls 92 an earlier observation, not a required count"]
    research: { engine: none, sources: [] }
    reasoning: "Other sessions open loops all the time, so any fixed count goes stale; the check already reads the live set."
  - id: D-741
    stage: plan-review
    question: "Does dispatch-check.py accept a [SKIP] record without a duration?"
    resolution: autonomous
    class: two-way
    chosen: "Yes. [PASS] and [FAIL] records keep the duration form; [SKIP] records also match '^\\s*\\[SKIP\\] (.+?) - ', the shape Write-TestSkip prints"
    source_tag: Local Canon
    precedents: [".agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:115-117 — Write-TestSkip prints [SKIP] name - reason", ".agent/context/handoffs/2026-11-14-review-limits-no-token-budget-plan-critical-review.md Q4 — the reviewer's nonblocking parser-shape note"]
    research: { engine: none, sources: [] }
    reasoning: "Without it a real skip would fail the record-count agreement. The FAIL and exit rules are unchanged, so the check is no looser on failures."
```

## Research References

- Upstream change: `P:/agentic-framework` commit `6dd76b7`, plan `docs/execution/plans/2026-10-20-review-limits-parameters/`. Primary.
- No web research: the design questions are settled by upstream and local canon, so no outside source applies.

## Planning receipts

All under `C:/Temp/av-kit/rl/`. Each probe was read-only with respect to the repository.

- **`meu-stats.txt`.** 143 MEUs, 139 complete, 4 pending.
- **`selftest-plan-time.txt`.** `LEDGER selftest`: 105 arms, 0 failures, 53 must-OK.
- **`patch-dry-run.txt`.** `UPSTREAM` against a copy of `LEDGER`: hunks 9, 10 and 22 fail; 19 to 21 apply 650 lines off with fuzz 2.
- **`ruff-plan-time.txt`.** `LEDGER` and `tests/tooling/` are lint-clean.
- **`pester-plan-time.txt`.** `Test-CliDispatch.ps1`: 31 arms, 29 pass, and 2 fail in the receipts-dir guard.
- **Ledger survey (inline, 2026-11-14).** 92 ledgers under `C:/Temp/av-kit/review-ledger`, every `token_budget` an integer of at least 1.
- **Not run at plan time:** any change to `LEDGER`, the new tests, the prose edits.

## Validation stage contract

- **Static:** `tools-lint`, `py-lint`, `task-contract`, `scope-paths`, `prose-check`, `red-check-selftest`.
- **Targeted:** the new test file in rows 1 to 4, the ledger selftest and arm check in row 4, the dispatch tests in row 8.
- **Fresh full:** `py-tests`, `state-render`, `closeout-selftest`.
- **Runtime:** `ledger-survey.py` and `-GateOnly` in row 8.
- **Identity:** from `identity.py`, independent of the receipts.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
