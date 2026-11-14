---
date: "2026-11-14"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-14-review-limits-no-token-budget/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "rl-plan-2026-11-14-review-limits-no-token-budget"
round: 2
---

# Critical Review: 2026-11-14-review-limits-no-token-budget

> **Review Mode:** `plan`
> **Current Verdict:** `approved`

## Scope

**Intent anchor:** Review loops in av-kit stop on their round caps and never on token spend, while every round's token usage is still recorded and shown.

**Intent assessment: yes, as a plan.** Executing the specified port would remove the token stop for newly opened default loops, preserve usage accounting and display, and retain round-cap enforcement. F1 is fixed in the plan; no new delivery-level finding remains.

Claude Code/Anthropic authored this draft. Codex (`codex-independent-reviewer`, class `avkit_independent_reviewer`) independently reviewed it. This round rechecked F1, Q4's prompt, Q5's exits and Q6's fixture correction against the working tree, original sources and UPSTREAM `6dd76b7`. Previously accepted surfaces were retained unless affected by those edits. HEAD is `1abf6698c2112e42deb8c298ec04c9f439cc63c3`, branch `main`; implementation rows remain unchecked.

The round-1 Findings table below is preserved verbatim as history. Its `open` status describes that pass; the Round 2 Prior Pass Summary explicitly closes F1. The latest verdict and findings_count describe this pass.

Only `C:/Temp/av-kit` was written. No repository file or live ledger was changed. No network, pytest, session gate, uv command, npm command or product suite ran. The coordinator owns copying this report to the canonical path and recording the verdict. Plan approval does not authorize execution; Mat's human plan gate remains.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | High | yes | control-defeat | **Row 8 can certify AC-13 when the dispatch suite never runs.** Confidence: High. `mechanism: task-row-completion-predicate`. After `Test-CliDispatch.ps1`, the command discards the child exit and decides success solely from `extra`. A PowerShell startup failure with no `FAIL` text therefore yields an empty set and exit 0. The independent negative probe used an absent scratch suite: PowerShell exited 64, no tests ran, and the exact prescribed predicate exited 0. A missing runner or early setup failure could consequently be reported as wrapper compatibility. Separately, `FAIL[: ]+(.+)` does not parse the actual `[FAIL] name (duration) - ...` records; on the supplied baseline it extracts three summary/table fragments and rejects the permitted pair. Violates **AC-13**. | `docs/execution/plans/2026-11-14-review-limits-no-token-budget/task.md:51`; `.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:75`; `:104` | Capture the suite exit immediately. Require evidence that the suite completed and emitted test results. Parse actual named result records; tolerate a nonzero test exit only for the explicitly permitted, observed baseline failures. Refuse startup/setup failures and unexpected failures. Prove the predicate on the real baseline, an added failing test and a suite that fails before any tests run; use that same policy in the session gate. | open |

## Recheck (Round 2)

**Date:** 2026-11-14. **Reviewer:** `codex-independent-reviewer`.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

No new delivery-level findings. The nonblocking parser-shape observation in Q4 does not require another review round.

### Confirmed Fixes

- **F1 / AC-13:** `implementation-plan.md:274-282` specifies a completed-suite summary, matching named result counts, minimum total, baseline-only FAIL ids and exit/count agreement. Row 0 requires the exact baseline pair; row 8 and the session gate use the same checker (`task.md:40,51`; plan `:309`). The prescribed selftest exercises startup failure and unexpected failures. A scratch reference implementation accepted the actual 31/29/2/0 receipt and rejected all three prescribed negative fixtures, a consistently recounted extra FAIL, wrong exits and a missing summary. This verifies the specification; the plan-local script is intentionally not written yet.
- **Q4:** Row 8 now passes `-PromptText` equal to its registered probe goal (`task.md:51`; plan `:299`). That reaches evaluate's INTENT_BINDING check correctly.
- **Q5:** The Boundary Inventory and AC-9 now distinguish malformed/contradicted-basis FailClosed exit 3 from sibling-block mismatch exit 1 (`implementation-plan.md:180,198`). D-733 stays exit 1. Scratch calls confirmed the corrected invalid-value/basis semantics.
- **Q6:** Both mocked loosening arms now use an existing inert RUN_PARAMETERS fixture, restoring it afterward; the new missing-tool arm has its own absent path (plan `:120`; task `:45`). Scratch calls reached both original expected refusals, and the absent-path case refused before either limits-check invocation or a ledger write.

### Q1 — Goal and end-to-end trace

**Accepted.** LEDGER's begin resolves LIMITS_FILE to OFF and the configured round cap. Its stored budget drives evaluate/record through stops; record still reads each usage receipt; state keeps per-round usage and the unbudgeted sum. The OFF reserve branch avoids numeric operations on the string, and AC-7 still asserts the cap boundary. AC-2/4/5/7/12 and rows 1–4 cover this path. Round 1's five-mode begin/evaluate/record/state probe with 10^12 tokens per round remains applicable; it was not rerun as implementation evidence. No goal sentence lacks a substantive planned producer/check.

### Q2 — Port and D-733

**Accepted, unchanged from round 1.** The function-by-function port includes LEDGER_KEYS/provenance, helper constants, removal of the `or` fallback, OFF reserve handling, conditional token stop, both readouts, begin resolution, continue refusal and parser flags. Evaluate's OK format remains compatible and record needs no accounting rewrite. UPSTREAM's ordinary path has no missing framework dependency. D-733 is inside the loosened branch before limits-check and save_ledger; the revised fixture probe confirms the missing-tool refusal with continue guidance and no write. The accepted exclusion of run parameters, credits and instantiate remains sound.

### Q3 — Existing loops

**Accepted, unchanged from round 1.** Validation adds no restriction to valid integer-budget ledgers, grants, mechanism reliefs or older optional fields. Missing limits_source remains legal. Round 1's copied-ledger survey passed all 93 then present ledgers without altering the live SHA map; the plan's 92 is its earlier observation, not a required fixed count. Row 8 surveys the execution-time set, copies every JSON, redirects RECEIPTS_DIR and runs state only on copies (`implementation-plan.md:298`; `task.md:51`). No live migration or rewrite is prescribed.

### Q4 — Wrapper and AC-13

**Accepted after correction.** The wrapper reads `mode=` from evaluate, whose line and exit mapping are unchanged; begin's added fields do not affect that parser. The corrected GateOnly prompt uses the registered goal and the command checks the intended kind/gate output without inference. The suite path and real `[FAIL] name (duration) - ...` parse are correct, and F1's unrun-suite false pass is closed across all three callers.

**Nonblocking parser-shape note:** `Write-TestSkip` emits `[SKIP] name - reason` without a duration (`.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1:115-117`), whereas the new common regex requires one (`implementation-plan.md:277`). A receipt containing an actual SKIP would be refused by count mismatch. The actual baseline has zero skips, and this fails closed, so it does not reopen F1 or prevent this plan from delivering. If skip tolerance is intended, recognize that duration-free shape while implementing the checker. No additional mutation round is requested.

### Q5 — Tests, Reds and sequencing

**Accepted.** Temp-root CLI copies and imports isolate REPO_ROOT/LIMITS_FILE; AC-1 intentionally reads the repo file. The peer copy pattern includes schema and vocabulary dependencies. The explicit assertion-only Red contract prevents import/setup errors being called a Red. AC-7 and AC-8's positive legacy case correctly already pass, and row 2's selected tests require begin/loading rather than OFF-aware rendering. Correcting AC-9 to upstream exits 3/1 removes the prior numerical mismatch without changing semantics. Rows 2–3 and their selected `-k` set remain coherent.

### Q6 — Selftest

**Accepted after correction.** The prior-name set comparison catches removed and renamed arms, while required limits-* names and zero failures cover the additions. Existing selftest was independently rerun this round: **105 arms, 0 failures, 53 must-OK**. The mocked-arm inert fixture now reaches the expected code; the separate absent path proves D-733's specific message before a write. Scope restoration preserves isolation and changes no prior expectation.

### Q7 — Prose and templates

**Accepted, unchanged from round 1.** Re-read all 22 INVENTORY locations and the four begin examples. The prior live-rule sweep remains applicable; no additional affected live cap/token-stop rule was identified. The rewrites name the file/block/state source, retain defaults and correctly keep continue as the way to add rounds. Commented template lines are invisible both to the flat frontmatter reader and PLAN_BLOCK's starting-key parser. Current AGENTS is **126 lines, 17,805 bytes, all CRLF**; replacing P20 fits its bounds. Historical records and unrelated context token budgets remain outside scope.

### Q8 — Safety and scope

**Accepted.** Planned edits remain in Files Modified, the plan folder, project artifacts, tmp_path or C:/Temp/av-kit. The survey reads live ledgers and invokes state only on copies; GateOnly uses a scratch loop. All three dispatch-check callers preserve the suite exit and apply one policy. CRLF preservation is explicit and LIMITS_FILE alone is deliberately new LF. Skipping package types, UI, MCP, OpenAPI and build is sound for these tooling/docs changes; affected tooling, wrapper and full Python checks remain planned. Repository status shows only the two plan files, the coordinator's round-1 report and the stated sandbox-only ignored-file artifact; that artifact was not opened.

## Checklist Results

Manual checks below were performed by `codex-independent-reviewer`; they assess the draft plan, not implementation completion.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Compare revised scope, row 0/8, AC-13 and session gate | null | One dispatch checker contract used throughout |
| PR-2 Not started | pass | Read task statuses and current git status | null | Implementation rows unchecked; no product changes |
| PR-3 Task contract | pass | `python -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-11-14-review-limits-no-token-budget/task.md` | 0 | 25 rows; dependencies acyclic; 23 executable rows checked |
| PR-4 Validation realism | pass | Run scratch reference predicate and corrected fixture probes | 0 | Real baseline accepted; unrun/unexpected/inconsistent results refused |
| PR-5 Source-backed planning | pass | Compare D-730–D-738 against source request, UPSTREAM and local canon | null | Accepted scope and policy choices retained |
| PR-6 Corrections readiness | pass | Recheck F1 and Q4–Q6 across all specified consumers and supplied census account | null | Corrections agree in plan/task; no procedural paperwork objection |
| PR-7 Scope discipline | pass | Reconcile exclusions with Mat's accepted recommendation | null | No required limits behavior omitted |
| PR-8 Control reachability | pass | Trace receipt/exit through all three checker callers and test negative cases | null | Failed startup cannot establish AC-13 |
| PR-9 Single-statement contracts | pass | Compare LEDGER/LIMITS_FILE/UPSTREAM/OFF/PLAN_BLOCK/INVENTORY consumers | null | No competing material behavior found |

### Durable evidence

```json
{"schema_version":"evidence.v1","check_id":"round2-corrections-design-probes","command":"rtk proxy python -B C:/Temp/av-kit/rl/review/r2-probe.py","cwd":"P:/av-kit","scope":"scratch-only reference of revised dispatch-check contract and review-only in-memory UPSTREAM splice plus D-733","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 1abf6698c2112e42deb8c298ec04c9f439cc63c3; revised working-tree plan/task; not a product implementation","output":"Real baseline accepted: Total=31 PASS=29 FAIL=2 SKIP=0; exact baseline ids. Added FAIL, empty exit-64 startup, inconsistent counts, wrong exits and absent summary refused. Both mocked loosening arms regained expected refusals with inert RUN_PARAMETERS. Absent path refused before check call/ledger write with continue guidance. Invalid values and contradicted basis exit 3; D-733 exits 1.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"round2-ledger-baseline","command":"rtk proxy python -B tools/review_ledger.py selftest","cwd":"P:/av-kit","scope":"existing ledger; PYTHONDONTWRITEBYTECODE=1; RECEIPTS_DIR/TMP/TEMP=C:/Temp/av-kit/rl/review","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 1abf6698c2112e42deb8c298ec04c9f439cc63c3; unchanged working-tree ledger","output":"RESULT: 105 arm(s), 0 failure(s) [53 must-OK arms, so the tool is not refusing everything]","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"round2-task-contract","command":"rtk proxy python -B tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-11-14-review-limits-no-token-budget/task.md","cwd":"P:/av-kit","scope":"revised task contract","phase":"static","exit_code":0,"result":"pass","tested_state":"revised working-tree task.md at review round 2","output":"OK: 25 row(s); 10-column table (with builder_model); 23 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic; 2 row(s) exempt (view_file): H1-5, H2-1","fresh":true}
```

Prior round-1 accepted evidence is attributed in Q1/Q3 and was not rerun or represented as fresh. Current source/probe receipts and reviewed-file SHA-256 identities are under `C:/Temp/av-kit/rl/review/r2-*`; decisive results are embedded above.

## Verdict

**approved** — F1 is fixed and all three prior correction notes are resolved. No evidence-backed High/Critical defect remains in the revised plan. The low-impact SKIP-format observation is recorded once in Q4. The next gate is Mat's explicit execution authorization to the coordinator.

Residual risk: the probes verify the specified design and unchanged baseline. The future script implementations, new tests, actual CRLF preservation and fresh execution gate remain to be verified during execution. No implementation approval is claimed.
