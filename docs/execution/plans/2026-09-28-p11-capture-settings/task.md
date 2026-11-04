---
project: "2026-09-28-p11-capture-settings"
source: "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
meus: ["MEU-57", "MEU-58"]
status: "in_progress"
template_version: "2.2"
---

# Task — Phase 11 Capture and Settings (Phase 11 exit)

> **Project:** `2026-09-28-p11-capture-settings`
> **Type:** GUI
> **Estimate:** 2 page recompositions, 1 additive primitive prop, 3 new source files, about 12 changed files; the exact count follows the final diff.
> **Execution gate:** the plan was approved in plan review Round 2. The user authorized execution on 2026-09-29 and chose the Session 25 split: container execution plus an authoritative `WINDOWS_GATE`. See [human-gate-decision.md](human-gate-decision.md) and plan §Execution amendments — 2026-09-29.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Execution recheck 2026-09-29: graphify-out/ and graphify-out-research/ absent (validate-task.sh prereq guard), no headroom install; TSX page composition uses direct file/search per the decision gate."
  human_message_reference: null
```

## Task Table

- **Where commands run:** from the repo root, with `RECEIPTS_DIR` exported.
- **`validate-task.sh`:** means `docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh`. Each check holds the exact procedure (helpers adapted from Session 25), and each writes its raw receipts under `$RECEIPTS_DIR`.
- **Container runs:** these invoke tools raw, which is the unfiltered equivalent of `rtk proxy` (plan amendment A2).
- **`WINDOWS_GATE`:** runs through `rtk proxy` on Mat's host.

| # | Task | Owner | Deliverable | Validation | Depends on | Context strategy | Durable outputs | builder_model | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Record the user's decisions and the execution amendments. Install UI and MCP dependencies. Run `electron-setup`. Prove prerequisites and `SEQUENCING_GATE`. Record the pre-edit baseline in `walkthrough.md`. | orchestrator | `walkthrough.md` prerequisites, decisions and baseline | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh prereq > "${RECEIPTS_DIR}/p11cs-prereq.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-prereq.txt"; exit $code` | — | shared | `walkthrough.md`; `p11cs-prereq.txt`; `p11cs-baseline.txt` | `avkit_coordinator` | `[x]` |
| 2 | Run `MIGRATION_CENSUS` and give every hit a disposition in `walkthrough.md`: unaffected, TM-n, or new-contradiction. A new-contradiction stops execution for the human. | orchestrator → tester | Census receipt; disposition table | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh census > "${RECEIPTS_DIR}/p11cs-census-run.txt" 2>&1; code=$?; tail -n 5 "${RECEIPTS_DIR}/p11cs-census-run.txt"; exit $code` | 1 | shared | `s26-census.txt`; `walkthrough.md` | `avkit_coordinator` | `[x]` |
| 3 | MEU-57 tests first:<br>• Write all AC-57.1–57.10 assertions.<br>• Register the MEU-57 `NEW_TESTIDS` after the MEU-56 block.<br>• Apply TM-1..TM-12 (Capture half).<br>• Prove Vitest and Electron assertion Red before any production edit. | coder | MEU-57 tests; Red receipts | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh red57 > "${RECEIPTS_DIR}/p11cs-57-red.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-57-red.txt"; exit $code` | 2 | shared | Test files; `s26-57-red-*.json` | `avkit_coordinator` | `[x]` |
| 4 | Implement MEU-57 per plan ACs and `CAPTURE_SOURCE_LOCATION`, running the targeted suite after each production edit. | coder | Capture page and helper | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh green57 > "${RECEIPTS_DIR}/p11cs-57-green.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-57-green.txt"; exit $code` | 3 | shared | Source files; Green receipts | `avkit_builder` | `[x]` |
| 5 | MEU-57 targeted gate: typecheck, lint, suites, build, and the Capture Electron specs. Then pre-handoff self-review and the MEU-57 handoff. | coder → tester → orchestrator | `.agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-57-handoff.md` | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate57 > "${RECEIPTS_DIR}/p11cs-57-gate.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/p11cs-57-gate.txt"; exit $code` | 4 | compact_continue | MEU-57 handoff; gate receipts; re-read `task.md` and the handoff before row 6 | `avkit_coordinator` | `[x]` |
| 6 | MEU-58 tests first:<br>• Write all AC-58.1–58.13 assertions, including the PathRow `readOnly` unit case.<br>• Register the MEU-58 `NEW_TESTIDS`.<br>• Apply the Settings half of TM-1.<br>• Prove Vitest and Electron assertion Red. | coder | MEU-58 tests; Red receipts | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh red58 > "${RECEIPTS_DIR}/p11cs-58-red.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-58-red.txt"; exit $code` | 5 | shared | Test files; `s26-58-red-*.json` | `avkit_coordinator` | `[x]` |
| 7 | Implement MEU-58 per plan ACs and `SETTINGS_SOURCE_LOCATION`, running the targeted suite after each edit. | coder | Settings page, rail, section table, primitive prop | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh green58 > "${RECEIPTS_DIR}/p11cs-58-green.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-58-green.txt"; exit $code` | 6 | shared | Source files; Green receipts | `avkit_builder` | `[x]` |
| 8 | MEU-58 targeted gate: typecheck, lint, suites, build, harness build, and the Settings/Convert/Capture/help Electron specs. Then pre-handoff self-review and the MEU-58 handoff. | coder → tester → orchestrator | `.agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-58-handoff.md` | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate58 > "${RECEIPTS_DIR}/p11cs-58-gate.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/p11cs-58-gate.txt"; exit $code` | 7 | compact_continue | MEU-58 handoff; gate receipts; re-read `task.md` and the handoff before H1 | `avkit_coordinator` | `[x]` |
| | **📋 Phase H1 — Pre-Review Closeout.** Continue directly; this divider is ordering, not a stop. | | | | | | | | |
| H1-1 | Prove rows 1–8 are `[x]` or evidence-backed `[B]`. | orchestrator | Row-state receipt | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh task-state > "${RECEIPTS_DIR}/p11cs-h1-rows.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-h1-rows.txt"; exit $code` | 8 | shared | Exact receipt | `avkit_coordinator` | `[x]` |
| H1-2 | Container pre-gate (non-authoritative): the full D6 stage set, with the input-identity manifest, `ENV_BOUND_TESTS` tolerance and the source audit. | tester | Pre-gate receipts; identity in `walkthrough.md` | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh pregate > "${RECEIPTS_DIR}/p11cs-pregate.txt" 2>&1; code=$?; tail -n 40 "${RECEIPTS_DIR}/p11cs-pregate.txt"; exit $code` | H1-1 | shared | `s26-gate-*` receipts | `avkit_coordinator` | `[x]` |
| H1-3 | Set MEU-57/58 to `ready_for_review`, then render and check. Mark grouping Session 26 as in review and update current focus. Re-run `DOC_READING_TESTS`. | orchestrator | SSOT, registry, grouping, focus | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh ssot-review > "${RECEIPTS_DIR}/p11cs-h1-ssot.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-h1-ssot.txt"; exit $code` | H1-2 | shared | SSOT/render receipts | `avkit_coordinator` | `[x]` |
| H1-4 | Prove the only change under `API_SCOPE_PATHS` is the human-approved typing fix (`packages/api/src/avkit_api/routes/captures.py`, amendment A8), and that OpenAPI has no drift. | tester | Scoped status receipt | `uv run python -c "import subprocess,sys; out=subprocess.run(['git','diff','--name-only','0f51036','HEAD','--','packages/','mcp-server/'],capture_output=True,text=True,check=True).stdout+subprocess.run(['git','status','--porcelain','--','packages/','mcp-server/'],capture_output=True,text=True,check=True).stdout; allowed=set(['packages/api/src/avkit_api/routes/captures.py']); changed=set([l.strip().split()[-1] for l in out.splitlines() if l.strip()]); print(sorted(changed)); sys.exit(0 if changed<=allowed else 1)" > "${RECEIPTS_DIR}/p11cs-api-scope.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-api-scope.txt"; exit $code` | H1-3 | shared | API scope receipt | `avkit_coordinator` | `[x]` |
| H1-5 | Reconcile both handoffs against the final ACs and evidence, and prove AC coverage. | orchestrator → tester | Two final handoffs | `bash -c 'uv run python tools/validate_closeout_artifacts.py --plan docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md --handoff .agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-57-handoff.md --ac-coverage-only && uv run python tools/validate_closeout_artifacts.py --plan docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md --handoff .agent/context/handoffs/2026-09-28-p11-capture-settings-MEU-58-handoff.md --ac-coverage-only' > "${RECEIPTS_DIR}/p11cs-handoff-ac.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-handoff-ac.txt"; exit $code` | H1-4 | shared | Handoffs; AC receipt | `avkit_coordinator` | `[x]` |
| H1-6 | Resolved after [B-H1-6](walkthrough.md#b-h1-6): `WINDOWS_GATE` attempt 7 passed at `cb864f3`, after the review corrections and A12–A17; attempts 1–6 are preserved in the walkthrough. Push the branch. Mat runs `WINDOWS_GATE` (`validate-task.ps1 -Check windows-gate`) on that commit and pushes `windows-gate-result.json`. Accept it only when it binds to the reviewed code. This is a planned turn boundary: `[B]` human-decision until the result lands. | human (Mat) → tester | `windows-gate-result.json`; check receipt | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh windows-gate-check > "${RECEIPTS_DIR}/p11cs-windows-gate-check.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-windows-gate-check.txt"; exit $code` | H1-5 | shared | Result JSON; check receipt | `avkit_coordinator` | `[x]` |
| | **🔎 Execution Critical Review.** Blocking independent review; the implementer never writes the verdict. | | | | | | | | |
| H1-7 | Dispatch `/execution-critical-review` to the user-directed Fable 5.1 subagent ([human-review-decision.md](human-review-decision.md)). Correct and re-dispatch within 6 rounds, re-running `WINDOWS_GATE` after any code correction. | reviewer dispatch / coder corrections | `.agent/context/handoffs/2026-09-28-p11-capture-settings-implementation-critical-review.md` | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh review-check .agent/context/handoffs/2026-09-28-p11-capture-settings-implementation-critical-review.md execution 6 > "${RECEIPTS_DIR}/p11cs-exec-review.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-exec-review.txt"; exit $code` | H1-6 | isolated | Rolling review; compact_continue fallback | `avkit_coordinator` | `[x]` |
| | **📋 Phase H2 — Post-Review Closeout.** Continue immediately after approval; re-read `task.md` first. | | | | | | | | |
| H2-1 | Write the reflection, with review churn, the same-vendor route, the readiness pre-load observation and the Instruction Coverage YAML. | orchestrator | `docs/execution/reflections/2026-09-28-p11-capture-settings-reflection.md` | `uv run python tools/validate_closeout_artifacts.py --reflection docs/execution/reflections/2026-09-28-p11-capture-settings-reflection.md --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml > "${RECEIPTS_DIR}/p11cs-reflection.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-reflection.txt"; exit $code` | H1-7 | compact_continue | Reflection; compact_continue fallback | `avkit_coordinator` | `[x]` |
| H2-2 | Produce `POST_REVIEW_STATE`: MEU-57/58 approved; grouping, hub Phase 11 ✅ and Next, focus, metrics. Assert `PHASE11_EXIT_PREDICATE`, including `DOC_READING_TESTS`. | orchestrator | SSOT, hub, grouping, focus, metrics | `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh post-review-state > "${RECEIPTS_DIR}/p11cs-post-review.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/p11cs-post-review.txt"; exit $code` | H2-1 | shared | Post-review receipts | `avkit_coordinator` | `[x]` |
| H2-3 | Run the completion-preflight structural checks and prove every row is done. Prepare the commit-message draft. | tester → orchestrator | Closeout receipt | `bash -c 'uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-09-28-p11-capture-settings/task.md && uv run python docs/execution/plans/2026-09-28-p11-capture-settings/plan_checks.py rows --task docs/execution/plans/2026-09-28-p11-capture-settings/task.md' > "${RECEIPTS_DIR}/p11cs-closeout.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/p11cs-closeout.txt"; exit $code` | H2-2 | shared | Closeout receipt | `avkit_coordinator` | `[x]` |

### Status Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[/]` | In progress |
| `[x]` | Complete |
| `[B]` | Blocked — evidence-gated (closed reason list + pasted error; must link follow-up) |

### Evidence-First & Sequencing Rules

- Each MEU goes FIC → all tests → assertion Red → Green → targeted gate → handoff. Red assertions are never edited in Green, and TM-1..TM-12 are the only approved expectation changes.
- `[x]` needs the deliverable plus durable evidence. `[B]` needs a `### B-<row-id>` block and a linked follow-up.
- H2 artifacts are created only after review approval. The author never writes a verdict. Commit and push go to the designated branch only; there is no merge, release or deploy.

### B-H1-6

Reason: human-decision

Decision: [human-gate-decision.md — WINDOWS_GATE is run by Mat](human-gate-decision.md)

`WINDOWS_GATE`, the authoritative Phase 11 exit gate, runs only on Mat's Windows host. That host has RTK, the region-picker stub `.exe` and the Windows-bound Python suite. This row turns `[x]` when `validate-task.sh windows-gate-check` passes on the pushed `windows-gate-result.json`. The run commands are in [walkthrough.md](walkthrough.md#b-h1-6).

Resolved 2026-09-29: attempt 1 (`47efbff`) failed py-tests on sibling-repo drift. After A11, attempt 2 (`e05d484`, tested `7613beb`) passed. The Round 1 corrections and A12–A17 then needed re-runs; attempts 3–6 failed and are preserved in the walkthrough. Attempt 7 (`f4c1a12`, tested `cb864f3`) passed all 17 stages, and `windows-gate-check` passes (receipt `p11cs-windows-gate-check.txt`).
