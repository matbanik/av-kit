---
project: "2026-10-01-mcp-live-audit"
source: "docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md"
meus: ["MEU-68"]
status: "approved"
template_version: "2.2"
---

# Task — MCP live audit (Session 28)

> **Project:** `2026-10-01-mcp-live-audit`
> **Type:** MCP + tooling + workflow docs
> **Estimate:** about 24 new files (11 runner modules, 2 schemas, 10 test files, workflow and skill), plus 6 modified docs/config files and 2 Part B evidence artifacts. The exact count follows the final diff.
> **Execution gate:** not authorized. It waits for independent plan approval **and** a direct user message ([human-gate-decision.md](human-gate-decision.md) H-4). Part B (rows 9–12) also waits for `SEQUENCING_GATE` (MEU-62 approved, H-3).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ absent; no headroom install (2026-10-01). TypeScript runner + docs scope uses direct file/search. Re-run in row 1 before execution."
  human_message_reference: null
```

## Task Table

- **Where commands run:** from the repo root, with `RECEIPTS_DIR` exported (container: an absolute scratchpad `receipts/` path; Windows: `C:/Temp/av-kit`).
- **`validate-task.sh`:** means `docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh`. Each check holds the exact procedure and writes raw receipts under `$RECEIPTS_DIR`.
- **Container rows:** these invoke tools raw, the unfiltered equivalent of `rtk proxy` (plan D-11). The Windows row (11) runs through `rtk proxy` inside `validate-task.ps1`.
- **Names:** `PART_A_PATHS`, `GATED_PATHS`, `SEQUENCING_GATE`, `AUTHORITATIVE_ACCEPTANCE`, `BASELINE_ANNOTATION_RULE`, `ENV_BOUND_AUDIT`, `MEU62_PENDING_TOLERANCE`, `TEST_SETS`/`VITEST_ACS`, `SSOT_MERGE_RULE`, `STALE_SPEC_PATTERNS` and `ISOLATION_KEYS` are defined once in `implementation-plan.md` §Single-statement contracts.

| # | Task | Owner | Deliverable | Validation | Depends on | Context strategy | Durable outputs | builder_model | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Prerequisites:<br>• Record the H-4 execution message in `human-gate-decision.md` and re-run the context-tool check.<br>• Run `npm --prefix mcp-server ci`, `uv sync --frozen`, `npm --prefix mcp-server run build`.<br>• Record `MCP_TEST_FLOOR` (pre-edit `mcp-tests` count) and the input identity in `walkthrough.md`.<br>• Set MEU-68 `in_progress` with `--plan`.<br>• File `MCP-PACKAGED-ENTRY-UNREACHABLE` through `issue_triage.py add`, root cause prefixed "hypothesis:" (plan D-6). | orchestrator | `walkthrough.md` §Prerequisites; SSOT rows | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh prereq > "${RECEIPTS_DIR}/s28-prereq.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s28-prereq.txt"; exit $code` | — | shared | `walkthrough.md`; `mcp-test-floor.json`; `s28-prereq.txt` | `avkit_coordinator` | `[x]` |
| 2 | Tests first:<br>• Write every `VITEST_ACS` test under `mcp-server/tests/audit/`, across all three `TEST_SETS` (unit, `run-cli` + `fake-backend.ts` + `runner-fake-backend`, `docs`).<br>• Create interface stubs in `scripts/audit/` that return neutral values, so the tests fail on assertions, not imports.<br>• Prove the Red. | coder | Test files; stubs; Red receipt | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh red > "${RECEIPTS_DIR}/s28-red.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s28-red.txt"; exit $code` | 1 | shared | `tests/audit/*.test.ts`; `s28-red.json` | `avkit_coordinator` | `[x]` |
| 3 | Implement the pure modules (`classify`, `ledger`, `report`, `redact`, `fixtures`, `plan`, both schemas) until `UNIT_TESTS` pass. Pin the row-3 behaviors (plan §`AUDIT_PLAN`: apply_defaults, capture.remove file state, the queue-level cancels, the transcript legal-state sequence) and `ISOLATION_KEYS`, with file:line, in `walkthrough.md`. Run `green` after each edit. | coder | Pure runner modules | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh green > "${RECEIPTS_DIR}/s28-green.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s28-green.txt"; exit $code` | 2 | shared | Source files; `s28-green.json` | `avkit_builder` | `[x]` |
| 4 | Implement `backend`, `client`, `observer`, `discovery`, `run` until `UNIT_TESTS` + `RUNNER_TESTS` pass, including the AC-68.1/4/6/7/8/12 negative oracles. | coder | Runner orchestration | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh fake > "${RECEIPTS_DIR}/s28-fake.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s28-fake.txt"; exit $code` | 3 | compact_continue | Source files; `s28-fake.json`; re-read `task.md` + `walkthrough.md` after compaction | `avkit_coordinator` | `[x]` |
| 5 | AC-68.17:<br>• Prove Red: a deliberate type error in `scripts/audit/classify.ts` passes the current `typecheck`.<br>• Add `tsconfig.scripts.json` and the `audit`/`typecheck` scripts; prove the same error now fails.<br>• Revert the error and prove typecheck passes.<br>• Register the D6 `mcp-audit` row in `.agent/docs/commands.md`. | coder | Config + D6 row; three receipts | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh typecheck-red-green > "${RECEIPTS_DIR}/s28-typecheck.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s28-typecheck.txt"; exit $code` | 4 | shared | `package.json`; `tsconfig.scripts.json`; `commands.md`; `s28-tc-*.txt` | `avkit_builder` | `[x]` |
| 6 | Container subset run against a real spawned backend (`--mode container --no-baseline`). Prove each `ENV_BOUND_AUDIT` member with its signature and environment proof, and record each `MEU62_PENDING_TOLERANCE` match, in `walkthrough.md` §Container run. Anything unproven is a real failure: fix the runner, or stop if it is a product defect. | tester | Container summary + report; census proofs | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh audit-container > "${RECEIPTS_DIR}/s28-audit-container.txt" 2>&1; code=$?; tail -n 40 "${RECEIPTS_DIR}/s28-audit-container.txt"; exit $code` | 5 | shared | `s28-audit-container/` (summary, `actions.jsonl`, report); walkthrough census table | `avkit_coordinator` | `[x]` |
| 7 | Docs:<br>• `.agent/workflows/mcp-audit.md` and `.agent/skills/mcp-tool-audit/SKILL.md`, with both README index rows.<br>• `05-mcp-server.md` §MCP live audit reconciled (AC-68.18).<br>• `docs.test.ts` green. | orchestrator → coder | Workflow, skill, indexes, spec section | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh docs > "${RECEIPTS_DIR}/s28-docs.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s28-docs.txt"; exit $code` | 6 | shared | Docs; `s28-docs.txt` | `avkit_builder` | `[x]` |
| 8 | Part A gate: `mcp-types`, `mcp-build`, `mcp-tests` (total > `MCP_TEST_FLOOR`, 0 failed), `scope a`, `task-contract`. Pre-handoff self-review notes in `walkthrough.md` §Part A checkpoint. Commit and push the Part A tree; record the SHA. | coder → tester → orchestrator | Part A checkpoint; pushed SHA | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh gate-a > "${RECEIPTS_DIR}/s28-gate-a.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s28-gate-a.txt"; exit $code` | 7 | compact_continue | Walkthrough checkpoint; `s28-gate-a-*.txt`; re-read `task.md` + walkthrough before row 9 | `avkit_coordinator` | `[x]` |
| 9 | `SEQUENCING_GATE`: merge `origin/main` into the session branch (merge commit, no rebase) per `SSOT_MERGE_RULE`. Prove MEU-62 is `approved` by JSON parse, prove `origin/main` is an ancestor, run both render checks, and re-run `scope b`. Planned `[B]` (dependency) until MEU-62 is approved. | orchestrator | Merge commit; gate receipt | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh seqgate > "${RECEIPTS_DIR}/s28-seqgate.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-seqgate.txt"; exit $code` | 8 | compact_continue | `s28-seqgate.txt`; walkthrough §Part B start | `avkit_coordinator` | `[x]` |
| 10 | Container pregate on the merged tree: the `WINDOWS_GATE` stages that can run here (`mcp-npm-ci`, `uv-sync`, `mcp-types`, `mcp-build`, `mcp-tests`, `audit-container`). Non-authoritative. Commit and push; record the SHA for the request. | tester | Pregate receipts; request SHA | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh pregate > "${RECEIPTS_DIR}/s28-pregate.txt" 2>&1; code=$?; tail -n 40 "${RECEIPTS_DIR}/s28-pregate.txt"; exit $code` | 9 | shared | `s28-pregate-*.txt` | `avkit_coordinator` | `[x]` |
| 11 | `WINDOWS_GATE` (authoritative). End the turn with the cloud-local §5.1 request block. Mat runs `validate-task.ps1 -Check windows-gate` (optionally `-PackagedServer <installed resources/mcp-server/index.js>`) and pushes `windows-gate-result.json`, `windows-gate-baseline.json`, `mcp-audit-summary.json`, the baseline and the report. Accept only when `windows-gate-check` passes. Planned turn boundary: `[B]` (human-decision) until the result lands. B-11; follow-up [WINDOWS_GATE request](walkthrough.md#windows_gate-row-11). | orchestrator → human (Mat) → tester | Result files; check receipt | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh windows-gate-check > "${RECEIPTS_DIR}/s28-windows-gate-check.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-windows-gate-check.txt"; exit $code` | 10 | shared | `windows-gate-result.json`; walkthrough §WINDOWS_GATE attempts | `avkit_coordinator` | `[x]` |
| 12 | Findings:<br>• File one known issue per non-`pass` authoritative result through `issue_triage.py add`, and render.<br>• Annotate baseline `issue` fields per `BASELINE_ANNOTATION_RULE`.<br>• Record the packaged-probe result, if run, as `MCP-PACKAGED-ENTRY-UNREACHABLE` `verification`.<br>• A MEU-62-surface failure stops for a Decision Brief (plan §Stop Conditions). | orchestrator | Known issues; annotated baseline | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh findings-check > "${RECEIPTS_DIR}/s28-findings.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-findings.txt"; exit $code` | 11 | shared | `known-issues.yaml`/`.md`; baseline; `s28-findings.txt` | `avkit_coordinator` | `[x]` |
| | **📋 Phase H1 — Pre-Review Closeout.** Continue directly; this divider is ordering, not a stop. | | | | | | | | |
| H1-1 | Prove rows 1–12 are `[x]` or evidence-backed `[B]`. | orchestrator | Row-state receipt | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh task-state > "${RECEIPTS_DIR}/s28-h1-rows.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-h1-rows.txt"; exit $code` | 12 | shared | Exact receipt | `avkit_coordinator` | `[x]` |
| H1-2 | Registered verification on the final tree: `windows-gate-check`, `findings-check`, `scope b`, `mcp-types`. | tester | Passing verification receipts | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh h1-verify > "${RECEIPTS_DIR}/s28-h1-verify.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s28-h1-verify.txt"; exit $code` | H1-1 | shared | Durable observations in the handoff | `avkit_coordinator` | `[x]` |
| H1-3 | Set MEU-68 to `ready_for_review`, then render and check. Mark grouping Session 28 as in review and update current focus. | orchestrator | SSOT, grouping, focus | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh ssot-review > "${RECEIPTS_DIR}/s28-h1-ssot.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s28-h1-ssot.txt"; exit $code` | H1-2 | shared | SSOT/render receipts | `avkit_coordinator` | `[x]` |
| H1-4 | OpenAPI skip-with-basis: prove this branch changed nothing under `packages/` relative to `origin/main` (G8 not triggered). | tester | Scoped receipt | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh api-scope > "${RECEIPTS_DIR}/s28-api-scope.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-api-scope.txt"; exit $code` | H1-3 | shared | API scope receipt | `avkit_coordinator` | `[x]` |
| H1-5 | Read `.agent/context/handoffs/TEMPLATE.md` and the latest peer handoff. Write `.agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md` with the evidence.v1 records, the Decision Log (H-1..H-4, D-1..D-11, plus any execution decisions) and full AC coverage. | orchestrator → tester | MEU-68 handoff | `bash -c 'uv run python tools/validate_closeout_artifacts.py --handoff .agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md --plan docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md && uv run python tools/validate_closeout_artifacts.py --plan docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md --handoff .agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md --ac-coverage-only' > "${RECEIPTS_DIR}/s28-handoff.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-handoff.txt"; exit $code` | H1-4 | compact_continue | Handoff; AC receipt; compact_continue fallback | `avkit_coordinator` | `[x]` |
| | **🔎 Execution Critical Review.** Blocking independent review; the implementer never writes the verdict. | | | | | | | | |
| H1-6 | Dispatch `/execution-critical-review` to the user-directed Fable 5.1 subagent ([human-review-decision.md](human-review-decision.md)). Correct and re-dispatch within 6 rounds. Any correction under `GATED_PATHS` reopens `WINDOWS_GATE` (row 11, next attempt). | reviewer dispatch / coder corrections | `.agent/context/handoffs/2026-10-01-mcp-live-audit-implementation-critical-review.md` | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh review-check .agent/context/handoffs/2026-10-01-mcp-live-audit-implementation-critical-review.md execution 6 > "${RECEIPTS_DIR}/s28-exec-review.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-exec-review.txt"; exit $code` | H1-5 | isolated | Rolling review; compact_continue fallback | `avkit_coordinator` | `[x]` |
| | **📋 Phase H2 — Post-Review Closeout.** Continue immediately after approval; re-read `task.md` first. | | | | | | | | |
| H2-1 | Write the reflection: review churn, the same-vendor route, the H-3 parallel-session outcome, grouping D-2/D-4/D-5 carried forward as G-D-2/G-D-4/G-D-5 (A14), and the Instruction Coverage YAML. | orchestrator | `docs/execution/reflections/2026-10-01-mcp-live-audit-reflection.md` | `uv run python tools/validate_closeout_artifacts.py --reflection docs/execution/reflections/2026-10-01-mcp-live-audit-reflection.md --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml --decision-source docs/execution/plans/2026-10-01-mcp-live-audit/implementation-plan.md --decision-source .agent/context/handoffs/2026-10-01-mcp-live-audit-MEU-68-handoff.md --decision-source .agent/context/known-issues.yaml --decision-issue MCP-LIVE-AUDIT-WORKFLOW > "${RECEIPTS_DIR}/s28-reflection.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-reflection.txt"; exit $code` | H1-6 | compact_continue | Reflection; compact_continue fallback | `avkit_coordinator` | `[x]` |
| H2-2 | Post-review state:<br>• MEU-68 `approved`.<br>• `MCP-LIVE-AUDIT-WORKFLOW` resolved through `issue_triage.py`.<br>• `BUILD_PLAN.md` Phase 5 row, grouping §6 Session 28, focus and the metrics row.<br>• `render --check`. | orchestrator | SSOT, hub, grouping, focus, metrics | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh post-review-state > "${RECEIPTS_DIR}/s28-post-review.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s28-post-review.txt"; exit $code` | H2-1 | shared | Post-review receipts | `avkit_coordinator` | `[x]` |
| H2-3 | Completion-preflight structural checks; prove every row is done; prepare the commit-message draft. Do not commit it without direction. | tester → orchestrator | Closeout receipt; draft | `bash docs/execution/plans/2026-10-01-mcp-live-audit/validate-task.sh closeout > "${RECEIPTS_DIR}/s28-closeout.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s28-closeout.txt"; exit $code` | H2-2 | shared | Closeout receipt | `avkit_coordinator` | `[x]` |

### Status Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[/]` | In progress |
| `[x]` | Complete |
| `[B]` | Blocked — evidence-gated (closed reason list + pasted error; must link follow-up) |

### Evidence-First & Sequencing Rules

- Tests first: all ACs → assertion Red → Green → targeted gate. Red assertions are never edited in Green.
- `[x]` needs the deliverable plus durable evidence in `walkthrough.md` or the handoff. `[B]` needs a `### B-<row-id>` block and a linked follow-up.
- Rows 9 and 11 are **planned** `[B]` boundaries:
  - Row 9 is a dependency (`SEQUENCING_GATE`); follow-up: Session 27.
  - Row 11 is a human-decision gate (Mat runs `WINDOWS_GATE`).
  - Neither is a failure, and neither licenses stopping elsewhere.
- H2 artifacts are created only after review approval. The author never writes a verdict.
- Git: commit and push only to `claude/sweet-goodall-mu69td` and only under the H-4 authorization. No PR, no merge to `main`, no release.

### B-11

Reason: human-decision

Decision: [human-gate-decision.md — H-4 split: Mat runs `WINDOWS_GATE`](human-gate-decision.md#h-4--execution-authorization-and-gate-location)

`WINDOWS_GATE` (the authoritative MCP live audit) runs only on Mat's Windows host (real Kokoro, ffmpeg, `mss` screen capture, residential network). The container pregate passed on `9b38503` (walkthrough §Container pregate). This row turns `[x]` when `validate-task.sh windows-gate-check` passes on the pushed `windows-gate-result.json`; row 12 then files the findings.

**Resolved:** attempt 1 passed on `8345599` (result commit `39de635`); `windows-gate-check` PASS (walkthrough §WINDOWS_GATE).

**Reopened (attempt 2):** the execution-review round 1 corrections (plan amendment A11) changed `GATED_PATHS` (`mcp-server/scripts/audit`, `validate-task.ps1`). Per row H1-6 the authoritative run repeats on the corrected commit. Rows 12 and H1-1 to H1-5 re-run after it (walkthrough §WINDOWS_GATE attempt 2).

**Resolved (attempt 2):** passed on `a044446` (result commit `0434895`); `windows-gate-check` PASS.

**Reopened (attempt 3):** the review round-2 fix R2-1 (A12; Mat chose "Fix now + attempt 3") changed `mcp-server/tests/audit/coverage.test.ts` under `GATED_PATHS`. Rows 12 and H1-1 to H1-6 re-run after it.

**Resolved (attempt 3):** passed on `65bfa42` (result commit `d9e2497`); `windows-gate-check` PASS.

