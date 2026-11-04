---
project: "2026-10-01-capture-viewport-chrome"
source: "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md"
meus: ["MEU-65", "MEU-66"]
status: "complete"
template_version: "2.2"
---

# Task — Capture viewport chrome (Session 29)

> **Project:** `2026-10-01-capture-viewport-chrome`
> **Type:** GUI
> **Estimate:** about 16 changed files (2 new source files, 2 new test files); the exact count follows the final diff.
> **Execution gate:** the plan was approved by the Fable 5.1 plan review in Round 2 ([human-review-decision.md](human-review-decision.md)). Execution needs a direct user message (`plan_to_exec_gate: human`; [human-gate-decision.md](human-gate-decision.md) §Execution authorization).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ absent; no headroom on PATH (2026-10-01). Row 0 re-checks before execution (validate-task.sh prereq refuses if a graph appears)."
  human_message_reference: null
```

## Task Table

- **Where commands run:** from the repo root, with `RECEIPTS_DIR` exported (default `/tmp/av-kit`).
- **`validate-task.sh`:** means `docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh`. Each check holds the exact procedure and writes its raw receipts under `$RECEIPTS_DIR`.
- **Container runs:** these invoke tools raw, which is the unfiltered equivalent of `rtk proxy`.
- **`WINDOWS_GATE`:** runs through `rtk proxy` on Mat's host (`validate-task.ps1`).
- **Named sets:** `TEST_AMENDMENTS`, `ENV_BOUND_*`, `GATED_PATHS`, `COUNT_FLOORS`, `PRODUCT_SCOPE` and `NEW_TESTIDS` are defined once, in `implementation-plan.md` §Single-statement contracts.

| # | Task | Owner | Deliverable | Validation | Depends on | Context strategy | Durable outputs | builder_model | Status |
|---|---|---|---|---|---|---|---|---|---|
| 0 | Record the execution message in `human-gate-decision.md`.<br>Install dependencies (`uv sync`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`) and run `validate-task.sh electron-setup` by hand first; `prereq` refuses without the Electron binary.<br>Prove prerequisites: the context-tool gate re-check, MEU-57/59/60 `approved` and MEU-65/66 `pending`.<br>Run `baseline`, which writes `baseline.sha` and the baseline receipts.<br>Write `walkthrough.md` §Baseline. | orchestrator | `walkthrough.md` §Baseline; `baseline.sha` | `bash -c 'bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh prereq && bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh baseline' > "${RECEIPTS_DIR}/s29-prereq.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s29-prereq.txt"; exit $code` | — | shared | `walkthrough.md`; `baseline.sha`; `s29-prereq.txt` | `avkit_coordinator` | `[x]` |
| 1 | Run the `TEST_AMENDMENTS` census. Give every hit a disposition in `walkthrough.md` §Census: `unaffected` with the reason (for example "id kept", "h-7 kept by D-9", "label text kept in the options row"), or `new-contradiction`. `TEST_AMENDMENTS` is empty, so any `new-contradiction` triggers Stop condition S2. | orchestrator → tester | census receipt; disposition table | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh census > "${RECEIPTS_DIR}/s29-census-run.txt" 2>&1; code=$?; tail -n 5 "${RECEIPTS_DIR}/s29-census-run.txt"; exit $code` | 0 | shared | `s29-census.txt`; `walkthrough.md` §Census | `avkit_coordinator` | `[x]` |
| 2 | MEU-65 tests first:<br>• Write every AC-65.1–65.7 assertion: `capture-toolbar.test.ts` (new), `capture-page.behavior.test.ts` and `layout-primitives.test.ts` (append only), and `capture-inbox.test.ts` (append only, plus the `sampleShot` optional override and `windowSettled`).<br>• Register the MEU-65 block of `NEW_TESTIDS`.<br>• Prove Vitest and Electron assertion Red before any production edit. `AC-65.4` must fail on its own `toBeLessThanOrEqual` (Stop condition S4 otherwise). | coder | MEU-65 tests; Red receipts | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh red65 > "${RECEIPTS_DIR}/s29-65-red.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s29-65-red.txt"; exit $code` | 1 | shared | test files; `s29-65-red-*` | `avkit_coordinator` | `[x]` |
| 3 | Implement MEU-65:<br>• `capture-toolbar.ts`: `TOOLBAR_BUTTONS` and `optionGroups`.<br>• `CaptureViewport.tsx`: the icon tools row and the `OPTIONS_ROW`.<br>• `Disclosure.tsx`: `DISCLOSURE_PROPS`.<br>• `CapturePage.tsx`: `OPTIONS_TOGGLE`.<br>Run the targeted Vitest after each edit. | coder | capture toolbar source; `Disclosure.tsx` | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh green65 > "${RECEIPTS_DIR}/s29-65-green.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s29-65-green.txt"; exit $code` | 2 | shared | source files; Green receipts | `avkit_builder` | `[x]` |
| 4 | Run the MEU-65 targeted gate, including `--repeat-each=20` on the touched Electron specs. Then the pre-handoff self-review, then the MEU-65 handoff. | coder → tester → orchestrator | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-65-handoff.md` | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh gate65 > "${RECEIPTS_DIR}/s29-65-gate.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s29-65-gate.txt"; exit $code` | 3 | compact_continue | MEU-65 handoff; gate receipts; re-read `task.md` and the handoff before row 5 | `avkit_coordinator` | `[x]` |
| 5 | MEU-66 tests first:<br>• Write every AC-66.1–66.17 assertion: `capture-zoom.test.ts` (new), and append-only additions to `capture-fit-map.test.ts`, `capture-hit-test.test.ts`, `capture-page.behavior.test.ts`, `capture-help-content.test.ts` and `capture-inbox.test.ts` (`ZOOM_SHOT`).<br>• Every test of a new export starts with an `expect(typeof …).toBe('function')`, so the Red is an assertion.<br>• Register the MEU-66 block of `NEW_TESTIDS`.<br>• Prove Vitest and Electron assertion Red. | coder | MEU-66 tests; Red receipts | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh red66 > "${RECEIPTS_DIR}/s29-66-red.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s29-66-red.txt"; exit $code` | 4 | shared | test files; `s29-66-red-*` | `avkit_coordinator` | `[x]` |
| 6 | Implement the pure MEU-66 geometry: `capture-zoom.ts` (`ZOOM_LADDER`, `zoomStep`, `zoomAbout`, `wheelSteps`, `zoomKeyAction`) and the `capture-fit-map.ts` additions (`viewTransform`, `VIEW_MAP`). Existing exports stay unchanged (Stop condition S6). | coder | `capture-zoom.ts`; `capture-fit-map.ts` | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh green66-unit > "${RECEIPTS_DIR}/s29-66-green-unit.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s29-66-green-unit.txt"; exit $code` | 5 | shared | source files; Green receipts | `avkit_coordinator` | `[x]` |
| 7 | Implement the MEU-66 viewport:<br>• `ZOOM_STATE`, `CONTENT_BOX`, `SURFACE_POINTER`;<br>• `ZOOM_INPUTS`, `PAN_GESTURES`, `ZOOM_READOUT`, `ZOOM_OBSERVABLES`, `ZOOM_RESET` (the `shotId` prop);<br>• the zoom rows of `TOOLBAR_BUTTONS`;<br>• `ZOOM_HELP_SENTENCE`.<br>Run the targeted Vitest after each edit, then the Electron `AC-66` specs. If the page-zoom oracle fails after the renderer prevents the event, apply Stop condition S5. | coder | `CaptureViewport.tsx`; `CapturePage.tsx`; help content | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh green66 > "${RECEIPTS_DIR}/s29-66-green.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s29-66-green.txt"; exit $code` | 6 | shared | source files; Green receipts | `avkit_coordinator` | `[x]` |
| 8 | Run the MEU-66 targeted gate, including the repeat checks. Then the pre-handoff self-review, then the MEU-66 handoff. | coder → tester → orchestrator | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-66-handoff.md` | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh gate66 > "${RECEIPTS_DIR}/s29-66-gate.txt" 2>&1; code=$?; tail -n 30 "${RECEIPTS_DIR}/s29-66-gate.txt"; exit $code` | 7 | compact_continue | MEU-66 handoff; gate receipts; re-read `task.md` before row 9 | `avkit_coordinator` | `[x]` |
| 9 | Hub reconciliation (plan §BUILD_PLAN.md Audit items 1–3):<br>• 09: the Viewport tools zoom pointer, the `ZOOM_LADDER` Levels row, the rows tagged "Session 29 plan D-12/D-15/D-17/D-18", and the MEU-65/66/67 rows in §MEUs.<br>• 11: one Options prose sentence. The CP rows are **not** edited (the AC-50.1/50.4 lock).<br>• `gui-actions-index.md`: three zoom rows.<br>• Re-run the doc-reading Vitest (`layout-canon`, `queue-canon`, `gui-actions-audit`). | orchestrator | hub edits | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh hub > "${RECEIPTS_DIR}/s29-hub.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s29-hub.txt"; exit $code` | 8 | shared | `docs/build-plan/09…`, `11…`, `gui-actions-index.md` | `avkit_coordinator` | `[x]` |
| | **📋 Phase H1 — Pre-Review Closeout.** Continue directly; this divider is ordering, not a stop. | | | | | | | | |
| H1-1 | Prove rows 0–9 are `[x]` or an evidence-backed `[B]`. | orchestrator | row-state receipt | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh task-state > "${RECEIPTS_DIR}/s29-h1-rows.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-h1-rows.txt"; exit $code` | 9 | shared | exact receipt | `avkit_coordinator` | `[x]` |
| H1-2 | Run the container pre-gate (non-authoritative): the full D6 stage set with input identity, `ENV_BOUND_*` tolerance and the source audit. | tester | pre-gate receipts; identity in `walkthrough.md` | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh pregate > "${RECEIPTS_DIR}/s29-pregate.txt" 2>&1; code=$?; tail -n 40 "${RECEIPTS_DIR}/s29-pregate.txt"; exit $code` | H1-1 | shared | `s29-gate-*` receipts | `avkit_coordinator` | `[x]` |
| H1-3 | Set MEU-65/66 to `ready_for_review`, then render and check. Mark grouping Session 29 as in review, and update `current-focus.md`. | orchestrator | SSOT, grouping, focus | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh ssot-review > "${RECEIPTS_DIR}/s29-h1-ssot.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s29-h1-ssot.txt"; exit $code` | H1-2 | shared | SSOT/render receipts | `avkit_coordinator` | `[x]` |
| H1-4 | Prove `PRODUCT_SCOPE`: no change under `packages/`, `mcp-server/`, `tools/`, `ui/src/main/` or `openapi.committed.json`; the OpenAPI check is clean; every changed `ui/` file is in a Files Modified table. | tester | scope receipt | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh api-scope > "${RECEIPTS_DIR}/s29-api-scope.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-api-scope.txt"; exit $code` | H1-3 | shared | scope receipt | `avkit_coordinator` | `[x]` |
| H1-5 | Reconcile the two handoffs against the final ACs and evidence, and prove AC coverage. | orchestrator → tester | two final handoffs | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh handoff-ac > "${RECEIPTS_DIR}/s29-handoff-ac.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-handoff-ac.txt"; exit $code` | H1-4 | shared | handoffs; AC receipt | `avkit_coordinator` | `[x]` |
| H1-6 | Push the branch and send the `WINDOWS_GATE` + `CAPTURE_LOOK` request ([local-requests.md](local-requests.md) §GATE, cloud-local §5.1).<br>Mat runs `validate-task.ps1 -Check windows-gate`, pushes the result JSON, then runs the L1–L6 look checklist on the same commit and replies one line per item.<br>Record the look results in `walkthrough.md` §CAPTURE_LOOK. Accept them only when the gate binds to the reviewed code and L1–L6 all pass.<br>This is a planned turn boundary: `[B]` human-decision until the results land. B-H1-6; follow-up [GATE request](local-requests.md). | human (Mat) → tester | `windows-gate-result.json`; `walkthrough.md` §CAPTURE_LOOK; check receipt | `bash -c 'bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh windows-gate-check && bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh look-check' > "${RECEIPTS_DIR}/s29-windows-gate-check.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-windows-gate-check.txt"; exit $code` | H1-5 | shared | result JSON; check receipt; `walkthrough.md` §Windows gate, §CAPTURE_LOOK | `avkit_coordinator` | `[x]` |
| | **🔎 Execution Critical Review.** Blocking independent review; the implementer never writes the verdict. | | | | | | | | |
| H1-7 | Dispatch `/execution-critical-review` to the user-directed Fable 5.1 subagent ([human-review-decision.md](human-review-decision.md)). Correct and re-dispatch within 6 rounds. Re-run `WINDOWS_GATE` after any correction that touches `GATED_PATHS` (cloud-local §3.4). | reviewer dispatch / coder corrections | `.agent/context/handoffs/2026-10-01-capture-viewport-chrome-implementation-critical-review.md` | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh review-check .agent/context/handoffs/2026-10-01-capture-viewport-chrome-implementation-critical-review.md execution 6 > "${RECEIPTS_DIR}/s29-exec-review.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-exec-review.txt"; exit $code` | H1-6 | isolated | rolling review; compact_continue fallback | `avkit_coordinator` | `[x]` |
| | **📋 Phase H2 — Post-Review Closeout.** Continue immediately after approval; re-read `task.md` first. | | | | | | | | |
| H2-1 | Write the reflection. It covers review churn, the same-vendor route and the Instruction Coverage YAML. Its Decisions Log includes **every** grouping §8 row, D-1 to D-7 (stage `grouping`; the validator requires the whole table), plan D-8 to D-21, and D-22 if S5 fired. The triage decisions in `known-issues.yaml` are cited in prose only. | orchestrator | `docs/execution/reflections/2026-10-01-capture-viewport-chrome-reflection.md` | `uv run python tools/validate_closeout_artifacts.py --reflection docs/execution/reflections/2026-10-01-capture-viewport-chrome-reflection.md --reflection-template docs/execution/reflections/TEMPLATE.md --reflection-schema .agent/schemas/reflection.v1.yaml --decision-source docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md --decision-source .agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-65-handoff.md --decision-source .agent/context/handoffs/2026-10-01-capture-viewport-chrome-MEU-66-handoff.md --decision-source .agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md > "${RECEIPTS_DIR}/s29-reflection.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-reflection.txt"; exit $code` | H1-7 | compact_continue | reflection; compact_continue fallback | `avkit_coordinator` | `[x]` |
| H2-2 | Produce `POST_REVIEW_STATE`:<br>• MEU-65/66 `approved`, rendered and checked.<br>• Grouping Session 29 approved.<br>• Focus updated.<br>• Metrics row.<br>• CAPTURE-TOOLBAR-ICONS, CAPTURE-SETTINGS-BUTTON-LABEL and CAPTURE-VIEWPORT-ZOOM resolved, with their verification pointing at this plan's committed gate and look evidence. | orchestrator | SSOT, grouping, focus, metrics, issues | `bash docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.sh post-review-state > "${RECEIPTS_DIR}/s29-post-review.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s29-post-review.txt"; exit $code` | H2-1 | shared | post-review receipts | `avkit_coordinator` | `[x]` |
| H2-3 | Run the completion-preflight structural checks and prove every row is done. Prepare the commit-message draft (no AI attribution trailers). | tester → orchestrator | closeout receipt; commit draft | `uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-01-capture-viewport-chrome/task.md > "${RECEIPTS_DIR}/s29-closeout.txt" 2>&1; code=$?; cat "${RECEIPTS_DIR}/s29-closeout.txt"; exit $code` | H2-2 | shared | closeout receipt | `avkit_coordinator` | `[x]` |

### Row Evidence

| Row | Evidence |
|---|---|
| Row 0 | `walkthrough.md` §Execution authorization and prerequisites, §Baseline (`baseline.sha` `c169453`; `s29-prereq.txt`); A-2 (`electron-setup` via `install.js`) |
| Row 1 | `walkthrough.md` §Census (333 hits, all `unaffected`; AC-39.8 literal-id design constraint) |
| Row 2 | `walkthrough.md` §MEU-65 Red; AC-65.4 Red on geometry (1300 > 836) |
| Rows 3–4 | MEU-65 handoff §Evidence (`green65`, `gate65`: repeat-each=20 160/160) |
| Row 5 | `walkthrough.md` §MEU-66 Red |
| Rows 6–8 | `walkthrough.md` §MEU-66 Green and gate; MEU-66 handoff §Evidence (`gate66`: repeat-each=20 240/240); A-3 (TA-1, TA-2) |
| Row 9 | `walkthrough.md` §Hub reconciliation (row 9) |
| H1-1 | `PASS implementation rows 0-9` (`s29-h1-rows.txt`) |
| H1-2 | `walkthrough.md` §Container pre-gate (H1-2) |
| H1-3 | `PASS SSOT review state` (`s29-h1-ssot.txt`): MEU-65/66 `ready_for_review`, grouping Session 29 in review, focus updated |
| H1-4 | `PASS product scope` (`s29-api-scope.txt`): frozen paths unchanged, every `ui/` change listed |
| H1-5 | `PASS s29-handoff-ac-65`, `PASS s29-handoff-ac-66` (`s29-handoff-ac.txt`) |
| H1-6 | `walkthrough.md` §WINDOWS_GATE attempts 3 and 4, §CAPTURE_LOOK; `windows-gate-check` + `look-check` PASS on `bde58a4` |
| H1-7 | `PASS execution review approved round 1 by claude-fable-5-1-subagent` (`s29-exec-review.txt`); `walkthrough.md` §Execution review |
| H2-1 | Reflection validator OK: 15 template sections, 7 schema fields, 3 sourced rules, 28 decisions reconciled against 34 rows |
| H2-2 | `PASS POST_REVIEW_STATE` (`s29-post-review.txt`): MEU-65/66 approved, grouping approved, focus, metrics, three issues resolved |
| H2-3 | `lint_task_contract.py` OK (`s29-closeout.txt`); `commit-message.txt` |

### B-H1-6
Reason: human-decision
Decision: [WINDOWS_GATE + CAPTURE_LOOK request, attempt 1](local-requests.md)

This is a planned turn boundary for the split gate (A-1). Mat runs `validate-task.ps1 -Check windows-gate` on Windows, pushes `windows-gate-result.json`, then runs the `CAPTURE_LOOK` checklist L1–L6 on the same commit and replies one line per item. The request was sent 2026-10-02. The tested code is `05b5b86`; later commits touch only `.agent` state, `docs/BUILD_PLAN.md` (SSOT render) and this plan folder's notes, outside `GATED_PATHS`. After the results land, the row's check runs (`windows-gate-check` and `look-check`), then H1-7.

**Attempt 1:** `WINDOWS_GATE` PASS on `f69a9d0` (result `a12ecea`; `windows-gate-check` PASS). The machine was not fully quiet (two zorivest agent sessions were busy), and this is recorded. `CAPTURE_LOOK`: L1–L4 and L6 pass, **L5 fail** (Space+drag right after a tool click drew a mark). Decision A-4 (focus hand-off, AC-66.18) and A-5 (two layout fixes, AC-65.8 and AC-66.19; two items filed) are in human-gate-decision.md. The fix commit is `c2452aa`. Then WINDOWS_GATE attempt 2 + CAPTURE_LOOK on the new commit ([request](local-requests.md)).

**Attempt 2:** FAIL at `ui-electron` on `c13a005` (result `2c2b34b`). W1-8 (Downloader) timed out under host load (a 48-worker zorivest pytest run, Electron stage 13.2 min against 2.8). `CAPTURE_LOOK` 2: L1–L6 and the frame height all pass. Decision A-6: harden W1-8 (TA-3, `66c7bfd`); the look is reused (D-29). Then WINDOWS_GATE attempt 3 ([request](local-requests.md)).

**Attempts 3 and 4:** both PASS. **Attempt 4**, quiet (`f7a3c44`, tested `bde58a4`, code `66c7bfd`), is the gate of record: 17/17 stages; pytest 629/0, Vitest 748/748, Playwright 127/0/0. `windows-gate-check` and `look-check` PASS. The look of record is CAPTURE_LOOK 2, all pass (D-29). The row is done.

### Status Legend

| Symbol | Meaning |
|--------|---------|
| `[ ]` | Not started |
| `[/]` | In progress |
| `[x]` | Complete |
| `[B]` | Blocked — evidence-gated (closed reason list + pasted error; must link follow-up) |

### Evidence-First & Sequencing Rules

- Each MEU goes FIC → all tests → assertion Red → Green → targeted gate → handoff. Red assertions are never edited in Green. `TEST_AMENDMENTS` is empty, so no existing expectation changes in this plan.
- `[x]` needs the deliverable plus durable evidence (the handoff or `walkthrough.md` carries `evidence.v1`). `[B]` needs a `### B-<row-id>` block and a linked follow-up.
- After every renderer edit that an Electron AC covers, run `npm --prefix ui run build` and then the named Electron `-g` spec (reflection 2026-09-20 KEEP).
- H2 artifacts are created only after review approval. The author never writes a verdict. Commit and push go to the designated branch only, and only on the user's direction; there is no merge, release or deploy.
