---
date: "2026-09-02"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-09-02-p10-queue-card-migration/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 3
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
dispatch_id: "plan-review-p10-queue-card-migration"
---

# Critical Review: p10-queue-card-migration

> **Review Mode**: `plan`
> **Verdict**: `changes_required`

## Intent Anchor

Executing this plan is supposed to replace both legacy queue tables and 13-button toolbars with the shared card surface while preserving every existing queue capability, then add the Phase 10 selection and bulk contract. As written, it would render the new surface, but several source contracts are wrong or untestable and at least two MEU boundaries can ship visible dead controls.

## Scope

Reviewed directly because this directory is not a git work tree:

- `implementation-plan.md`, `task.md`, and `named-sets.json`
- `docs/build-plan/10-queue-card-ui.md`, the MEU registry/matrix, predecessor reflection, and relevant local canon
- Both current table/page/control implementations, shared queue components, E2E suites/test-id registry, REST schemas/routes, persistence/service behavior, and UI package manifests

No product code, tests, plan files, or existing handoffs were modified. No test/build suite was run; this was a static plan review.

## Findings

| # | Severity | Finding | Primary locations | Status |
|---|---|---|---|---|
| 1 | High | Clear finished targets the wrong rows and omits normative failure detail. | `named-sets.json:36-39,159-168`; `implementation-plan.md:264-270`; `10-queue-card-ui.md:60,64-74` | open |
| 2 | High | The planned selection/bulk UI contradicts the spec and lacks a viable Shift-click wiring path. | `named-sets.json:19-28,107-110,174-176`; `implementation-plan.md:264-273`; `10-queue-card-ui.md:216-228` | open |
| 3 | High | Both reorder boundary inventories specify a request body the real API rejects. | `implementation-plan.md:128-137,195-202,264-271`; `downloads.py:79-82`; `conversions.py:61-64` | open |
| 4 | High | The mount/E2E controls can pass a page with missing or dead capabilities. | `named-sets.json:56-77,113-116`; `implementation-plan.md:148-158,211-220`; `task.md:32,42` | open |
| 5 | High | MEU-45 and MEU-46 expose Clear finished before any row implements it. | `task.md:34-46,49-51`; `implementation-plan.md:143-158,208-220,264-274` | open |
| 6 | High | The plan repeatedly invokes a closeout validator that does not exist and is not scheduled. | `task.md:40,47,53,61-69,83-86`; `tools/validate_closeout_artifacts.py` (absent) | open |
| 7 | High | `META_SEGMENTS_CONTRACT` drops speed/ETA values retained and displayed after completion. | `named-sets.json:129-140`; `ConvertQueueTable.tsx:76-82`; `conversion.py:477,490-504`; `conversions.py:82-85` | open |
| 8 | High | Removing `@tanstack/react-table` ignores the lockfile, so the dependency-removal gate can false-pass. | `implementation-plan.md:232-243`; `task.md:45`; `ui/package.json:23-27`; `ui/package-lock.json:7-14` | open |
| 9 | Medium | The two command modules are existing production owners, not new files, and their current exports/consumers are absent from the preservation contract. | `implementation-plan.md:146,181,208,236`; `task.md:35,43`; `convert-commands.ts:26-42,195-237,285-293`; `download-commands.ts:14-32,139-182,246-257` | open |
| 10 | Medium | The converter Retry contract incorrectly adopts downloader-only statuses. | `named-sets.json:31-34`; `implementation-plan.md:147,152,208-210`; `10-queue-card-ui.md:278-285` | open |
| 11 | Low | The meta separator has two live definitions despite the single-statement rule. | `named-sets.json:129-131`; `implementation-plan.md:143` | open |

No Critical findings were identified.

### Finding 1 — Clear finished violates the seven-clause source contract

**Failure scenario:** a queue contains `Done`, `Failed`, `Cancelled`, and `Skipped` rows. Clicking Clear finished snapshots `TERMINAL_STATUSES`, so the plan deletes all four records; the spec permits only the `Done` id set. If one deletion returns `404`, the planned `N removed, M failed` toast also omits the required reason for that failure. `CLEAR_FINISHED_SEMANTICS` compresses seven clauses into six but loses “every snapshotted id exactly once” and “reason per failure,” while AC-47.7 nevertheless claims all seven are covered.

**Required correction:** make the snapshot Done-only, require exactly one attempt per snapshotted id, retain failed-or-skipped counts and per-id reasons, and put those observables in AC-47.2/.3/.7 tests, including a `404` and a row that becomes Done after the click.

### Finding 2 — Selection and bulk behavior is a different product contract

**Failure scenario:** one of three visible rows is selected. The spec requires a header `SelectionCheckbox` showing indeterminate state and count, plus a sticky bar above the list with Retry, Move to top, Move to bottom, Remove, and Clear selection. The plan instead pins the bar to the viewport bottom and supplies Move up/down plus an extra bar-level Select all. It schedules no header checkbox. Further, the current `SelectionCheckbox.onChange` supplies only `(checked)` and `QueueCard.onSelectChange` only `(id, checked)` (`SelectionCheckbox.tsx:11-23,63-78`; `QueueCard.tsx:86-100,282-289`), while the MEU-47 file inventory modifies neither component. Shift-click modifiers therefore have no production path into `useQueueSelection`. AC-47.3 is also tagged `unit` even though “result feeds a toast” is page/component wiring.

**Required correction:** reconcile the human lock with the current spec (`sticky above the list`, not viewport-bottom), use the specified top/bottom action set, add the header tri-state/count contract, name the component callback changes that carry modifier state, and classify/test toast wiring as integration behavior.

### Finding 3 — Reorder uses the wrong wire shape and underspecifies sequential bulk ordering

**Failure scenario:** a card invokes `reorderConversion(id, 'up')` according to the Boundary Inventory and sends `{id,direction}`. Both REST schemas accept `{job_ids: [...]}` and both services require a complete permutation, so the request returns `422` rather than moving the row. For a multi-row bulk move, merely fanning out calls without a specified sequential, updated permutation can also submit stale arrays and produce the wrong final order.

The existing `buildReorderBody` functions already construct the real payload (`convert-controls.ts:108-128`; `download-controls.ts:95-115`), and the routes consume it (`routes/conversions.py:232-239`; `routes/downloads.py:210-217`).

**Required correction:** describe the real `{job_ids}` boundary, preserve/reuse the builders, and define a sequential bulk reorder algorithm whose next permutation is based on the preceding successful state. Add request-body and final-order assertions.

### Finding 4 — Mount completeness and the E2E rewrite can both false-pass

**Failure scenario:** Downloader implements every new home and its E2E file merely asserts each locator is visible; Convert omits Move to top or renders Retry with a no-op handler. Clause 4 still passes because it searches globally for downloader-style retired ids (`up-btn`, not `convert-up`), global new-home presence, and one assertion anywhere. Neither a click nor its request/result is required. The 59-test floor counts test cases, not assertions, so W1-3 can also lose its cookie/SABR assertions while remaining one passing test.

The gate also proves only `QueueList` is mounted. `QueueList` renders an empty `<div>` when `items=[]` (`QueueList.tsx:77-104`), and the plan never schedules `EmptyDropZone` or the compact non-empty drop strip required by `10-queue-card-ui.md:260-274`; “everything is mounted” can therefore pass while that foundation component remains unused.

**Required correction:** use a per-page old-id/action matrix (including `convert-*` ids), require E2E interaction plus endpoint/payload/result assertions for every moved capability, preserve a baseline assertion/capability census for unaffected W1/W8 assertions, and add explicit empty/non-empty drop-target mounting checks. Task rows 2 and 12 must author Red coverage for the integration ACs, not only unit ACs and locator rewrites.

### Finding 5 — The MEU order creates a dead toolbar control

**Failure scenario:** after the MEU-45 gate, Convert must render exactly `TOOLBAR_CONTROLS`, including Clear finished, but `runBulk` and Clear-finished wiring are not implemented until task rows 19-21 in MEU-47. MEU-46 repeats the same condition for Downloader. Both intermediate handoffs can therefore pass with a visible Clear finished button that does nothing.

**Required correction:** land the shared Clear-finished executor before the first toolbar is mounted and wire it page-by-page in MEU-45/46, or change the project sequencing/gates so no MEU boundary declares a toolbar complete while one of its four controls is dead.

### Finding 6 — The closeout validator is absent with no scheduled producer or fallback

**Failure scenario:** task row 10 reaches its handoff check and runs `python tools/validate_closeout_artifacts.py ...`; Python exits with file-not-found. The same absent executable gates the MEU-46/47 handoffs, AC coverage, execution-review state, reflection, and final closeout. Unlike the expressly handled `tools/run-meu-gate.ps1` absence, the task notes define no fallback and no row creates this tool, so execution cannot advance past the first handoff validation.

**Required correction:** either point every row at a real repository validator with equivalent flags, schedule this script as an explicit prerequisite deliverable, or provide exact existing fallback checks for every invocation surface.

### Finding 7 — The meta migration loses completed-job information

**Failure scenario:** a conversion completes after reporting `speed_bps=1.5` and `eta_seconds=8`. The service deliberately retains those values, the API serializes them, and the old table renders them on the Done row. `CONVERT_META_SEGMENTS` and `DOWNLOAD_META_SEGMENTS` restrict speed/ETA to in-flight rows, so the new card hides persisted values after completion. Download completion similarly preserves its last non-null speed (`services/download.py:134-143,559-568`).

**Required correction:** preserve every non-null legacy column value regardless of status unless the source contract explicitly says the backend clears it; add Done-row tests with non-null speed/ETA. The optional page-composed `metaSegments` mechanism itself is sound.

### Finding 8 — Dependency removal omits `ui/package-lock.json`

**Failure scenario:** implementation deletes the dependency from `ui/package.json`, both imports, and both tables, satisfying AC-46.5 and mount clause 3, while the root package-lock entry and resolved packages remain. A clean install can retain the supposedly removed package or reject manifest/lock drift, despite all planned scans passing.

**Required correction:** add `ui/package-lock.json` to the MEU-46 modified-file inventory/deliverable, remove both root and resolved entries through the package manager, and make clause 3 scan both manifests.

### Finding 9 — Existing command owners are treated as new disposable files

**Failure scenario:** an implementer follows “New `convert-commands.ts`” literally and replaces it with the four queue mutations. `AppShell.tsx` then loses `CONVERT_COMMANDS`/`DOWNLOAD_COMMANDS` palette dispatches and existing add/start/pause/resume/cancel/clear/SABR behavior. Both files already exist and are imported by production code and tests.

**Required correction:** change both actions to **modify/extend**, inventory the existing public exports/consumers, and require regression assertions that the command-palette surface survives while the new per-id operations share the same owner.

### Finding 10 — Converter Retry is widened past its enum contract

**Failure scenario:** a conversion item carrying an unexpected `QualityBlocked` status reaches the stringly typed list boundary. AC-45.5 requires `controlEnabled('reset')` to return true because it uses the download-wide `REQUEUEABLE_UI_STATUSES`, so the card offers Retry even though the conversion route permits only `Failed` and `Cancelled` and returns `409`. The Phase 10 spec explicitly gives distinct exhaustive sets.

**Required correction:** define separate download and conversion requeueable UI sets; AC-45.5/primary-action wiring must use `{Failed, Cancelled}`, while AC-46.2 uses the four download statuses.

### Finding 11 — Meta separator ambiguity

**Failure scenario:** implementation follows the named contract and renders `size - quality`, while AC-45.1 expects `size · quality`; either the Red test or the implementation is wrong despite following a live plan statement.

**Required correction:** choose one separator in `META_SEGMENTS_CONTRACT` and make AC-45.1 reference the NAME without restating it.

## Judgment Calls and Scope Results

- **DEC-2 toolbar count:** sound. The 13 originals are Start, Pause, Resume, Cancel, Up, Down, Top, Bottom, Reset, Remove, Clear all, Open file, and Open folder. Start remains; Pause/Resume become one toggle; Clear all moves to overflow; all other capabilities have an abstract named home. Findings 2-5 concern whether those homes are the correct ones and are actually wired, not the count.
- **In-flight defect corrections:** `controlEnabled('reset')`, `DEAD_REGION_RULE`, and removal of the table-only `STATUS_COLORS` maps all belong in MEU-45/46. They are not scope creep; Finding 9 narrows the converter status set correctly.
- **C2 deferrals:** Transcript `ChannelCard`/G33 and TTS to MEU-48, and drag reorder to MEU-49, are legitimate scheduled deferrals (`meu-registry.md:131-135`; matrix `10.5-10.9`). The untouched Transcript violation is pre-existing and MEU-48 depends on MEU-47, so this project does not worsen it.
- **C2 non-goals:** detail panel, bulk endpoint, density toggle, and backend/API additions have source-backed bases. The CI-promotion row cites current absence/design history rather than a build-plan line, ADR, or Human-approved exclusion; that basis should be tightened, but it does not conceal required migration work and is not a blocking finding.

## Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass with sequencing defect | Artifacts agree on MEU-45→46→47; Finding 5 shows that shared order is not usable. |
| PR-2 Not-started confirmation | pass with inventory drift | Toolbar/bulk/gate files are absent and tables remain; command modules pre-exist (Finding 8). |
| PR-3 Task contract completeness | pass | Actionable rows carry owner, deliverable, validation, dependency, context strategy, and status. |
| PR-4 Validation realism | fail | Findings 4-6 and 8 demonstrate concrete dead-control, missing-executable, and false-pass paths. |
| PR-5 Source-backed planning | fail | Findings 1, 2, 3, 6, and 9 contradict the cited source/current contracts. |
| PR-6 Handoff/corrections readiness | pass | Three MEU handoffs and rolling review paths are explicit; this is Round 1. |
| PR-7 Scope discipline | pass with note | MEU-48/49 deferrals are scheduled and substantive non-goals are supported; CI-gate promotion basis should cite an allowed C2 authority. |
| PR-8 Control reachability/totality | fail | Shift-click has no modifier path; Clear finished is dead at two boundaries; global presence checks do not prove handlers. |
| PR-9 Single-statement discipline | fail | Finding 11 is a direct duplicate-contract conflict; Findings 1/2/10 also attach incorrect values to source-named sets. |

## Commands Executed

All shell reads/searches were prefixed with RTK, redirected to `C:/Temp/av-kit/`, and consumed only after exit capture. Key receipts include:

- `p10-named-sets.txt`, `p10-plan-*.txt`, `p10-task-*.txt`, `p10-spec-*.txt`
- `p10-convert-table.txt`, `p10-download-table.txt`, `p10-queue-card-*.txt`, `p10-queue-list-selection.txt`
- `p10-controls-census.txt`, `p10-e2e-case-lines.txt`, `p10-*-e2e-*.txt`
- `p10-reorder-schemas.txt`, `p10-endpoint-census.txt`, `p10-progress-persistence.txt`
- `p10-existing-command-modules.txt`, `p10-command-module-consumers.txt`, `p10-package-files.txt`
- `p10-unstarted-state.txt`, `p10-referenced-artifacts.txt`, `p10-review-target-preedit.txt`

## Follow-up Actions

Route one correction pass through `/plan-corrections`, addressing Findings 1-11 and producing the Round 2 correction census/disposition evidence. The correction should first reconcile the Phase 10 named contracts, then realign ACs/task ordering and finally strengthen the page-specific behavioral gates.

## Residual Risk

After these corrections, implementation risk remains concentrated in multi-row reorder ordering and Electron E2E request/result assertions. Those are manageable if the revised Red phase captures actual payloads, final queue order, partial-failure reasons, and per-page control behavior.

## Verdict

`changes_required` — the toolbar-count decision and scheduled deferrals are sound, but the plan currently deletes the wrong rows under Clear finished, specifies the wrong bulk/reorder behavior, can pass missing or unwired capabilities, exposes a dead toolbar control at two MEU boundaries, depends on a missing validator, and drops persisted table data.

---

## Round 2 — Corrections Re-Review

### Intent Anchor

Executing this plan should migrate both queue pages to the shared card surface without losing any current table or toolbar capability, then add the complete §10.5–10.7 toolbar, selection, bulk, and empty-state behavior. The Round 1 corrections repair most of that contract, but the final mount gate can still accept dead bulk controls, and the newly generalized empty-state contract has no supported downloader Browse/drop action.

### Round 1 Finding Disposition

| Finding | Disposition | Round 2 evidence |
|---|---|---|
| F1 | **closed** | `CLEAR_FINISHED_SNAPSHOT_STATUSES` is `Done` only; `CLEAR_FINISHED_SEMANTICS` now contains all seven normative clauses, including exactly-once attempts and per-failure reasons. AC-45.18 and AC-47.7 bind the executor and the 404/mid-run negatives. |
| F2 | **closed** | The bar actions, header tri-state checkbox, and sticky-above-list placement now match the spec. Modifier propagation is structurally complete: `SelectionCheckbox` forwards `{ shiftKey }` to `QueueCard`; `QueueListProps` inherits `QueueCardProps` and spreads the callback to every card; row 21 wires the selection model into both pages. |
| F3 | **closed** | Both boundaries now use the existing complete-permutation `{ job_ids }` contract and exported `buildReorderBody`; `BULK_REORDER_ALGORITHM` correctly folds from the last accepted order and covers a failed middle step. |
| F4 | **still open** | The new per-page map fixes the downloader/converter id mix-up, but multi-home entries plus MEU-47-only controls leave a concrete dead-control false-pass; see the remaining F4 finding below. |
| F5 | **closed** | Row 3a implements Clear finished before row 4/row 6 mounts the converter toolbar; downloader mounting follows the same executor; row 20 implements bulk executors before row 21 mounts the bulk bar. No planned control precedes its handler. |
| F6 | **closed** | No row invokes `validate_closeout_artifacts.py`. The three plan-local checks are created and negatively self-tested in row 9a before row 10 first uses one; later rows use those scripts or the existing `tools/check_exec_review.py`. |
| F7 | **closed** | Both meta contracts retain non-null speed/ETA regardless of status, with `Done` regressions in AC-45.17, AC-46.3, and AC-46.9. |
| F8 | **closed** | AC-46.5 and row 15 use `npm --prefix ui uninstall @tanstack/react-table` and scan both package manifests. |
| F9 | **closed** | Both command modules are modify-in-place owners. The preserved-export inventories reproduce the current `export` declarations and name their live source/test consumers. |
| F10 | **closed** | Download and conversion Retry sets are separate and exhaustive over their actual enums; `Skipped` is excluded from both. |
| F11 | **closed** | `META_SEPARATOR` has one canonical definition and all composition requirements reference it by name. |

### Remaining / New Findings

| # | Severity | Confidence | Wrong delivered behavior | Evidence | Required correction |
|---|---|---|---|---|---|
| F4 | **High** | High | **A newly added bulk control can render and do nothing while the final mount-completeness gate passes.** Several retired controls map to two homes, for example `top-btn -> kebab move-top + bulk-move-top` and `reset-btn -> card Retry + bulk-retry`. MEU-45/46 run the gate before the bulk bar exists, so those homes must be treated as alternatives at those boundaries. If the same interpretation survives the final gate, a working kebab Move to top or card Retry satisfies clause 4 while `bulk-move-top` or `bulk-retry` is dead. Clause 5 proves only test-id registration, and AC-47.10 exercises bulk Remove and Clear finished only; it never clicks bulk Retry, bulk Move top, bulk Move bottom, or Clear selection and asserts an outcome. The assertion census cannot prove a capability that never had a required assertion. | `named-sets.json:74-76,89-91,144-162,168,405-406`; `implementation-plan.md:166,168,239,290-297,353`; `task.md:39,52-54` | Split the capability matrix into phase-aware, per-home obligations. The MEU-45/46 scopes may require the card/kebab home, but final `-Scope all` must require **every** MEU-47 control independently. Extend page E2E coverage to click bulk Retry, Move top, Move bottom, Clear selection, and the selection-header/keyboard entry paths and assert request bodies or DOM results. Add a self-test where one home works and its sibling home is dead. |
| F12 | **High** | High | **The new empty-state correction requires a file Drop/Browse surface on the downloader but defines no supported action for it.** `EMPTY_STATE_CONTRACT` and mount clause 7 require `queue-empty-dropzone` on each migrated page and call Browse an equal path. The existing `EmptyDropZone` requires an `onBrowse` callback, while the downloader creation boundary accepts a `url` and has no media-file picker/intake path. Backend/API changes are explicitly out of scope. A no-op callback therefore satisfies the current presence-only clause 7; passing a local path to `POST /downloads` invents unsupported behavior; focusing the URL field makes the file-drop/Browse copy false. | `named-sets.json:168,400-402`; `implementation-plan.md:172,201,368,429-430`; `task.md:35,39,47`; `ui/src/renderer/src/components/queue/EmptyDropZone.tsx:153,190,210-211`; `ui/src/renderer/src/features/downloader/download-commands.ts:36,43-54,124-133`; `10-queue-card-ui.md:262-274` | Resolve the page-specific intake contract before implementation. Either give Downloader a source-backed URL-specific empty invitation and exclude file Drop/Browse there, or explicitly widen scope/boundaries if local-file intake is genuinely intended. For each page, name the production handler and add an E2E interaction plus observable outcome; clause 7 must reject a present-but-no-op Browse control. |

No Critical findings were identified.

### Cross-Artifact Audit

- No duplicate top-level key was found in `named-sets.json`.
- No acceptance criterion or task row references a missing named contract.
- The task dependency walk is coherent after F5: `3a -> 4 -> 5 -> 6`, `13 -> 14`, and `20 -> 21` put handlers before mounts.
- Strict single-statement cleanup is not yet perfect: explanatory text repeats the values `Done only` and `{Failed, Cancelled}` outside `named-sets.json`. Those copies agree with the canonical sets and have no current wrong-outcome scenario, so they are recorded as a non-blocking correction note under the owner's substance rule rather than an additional finding. Remove the literal glosses during the correction pass.
- The plan remains unstarted: the new toolbar/bulk/lib/gate files and all three MEU handoffs are absent.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | The three artifacts describe the same MEU-45 -> MEU-46 -> MEU-47 order and the F5 dependency chain is now usable. |
| PR-2 Not-started confirmation | pass | All implementation rows are unchecked and all planned new production/gate/handoff artifacts tested absent. |
| PR-3 Task contract completeness | pass | Actionable rows retain owner, deliverable, validation, dependency, strategy, durable output, model, and status. |
| PR-4 Validation realism | **fail** | F4 and F12 demonstrate present-but-dead controls that the stated gates can accept. |
| PR-5 Source-backed planning | **fail** | F12 has no source-backed downloader intake behavior capable of satisfying the new generic empty-state contract. |
| PR-6 Handoff/corrections readiness | pass for substance review | Rolling targets and correction path are explicit; the owner's instruction excludes process-paperwork findings from this round. |
| PR-7 Scope discipline | pass | MEU-48/49 deferrals remain scheduled and the substantive non-goals remain supported. |
| PR-8 Control reachability/totality | **fail** | F4 leaves several final bulk controls without independent production-outcome oracles; F12 has no downloader Browse producer. |
| PR-9 Single-statement discipline | pass with correction note | No conflicting duplicate or dangling name exists; consistent literal glosses should be removed as noted above. |

### Commands Executed

Static reads and exact-evidence sweeps only; no pytest, Vitest, build, Playwright, generator, or product validation suite was run. All process output was redirected under `C:/Temp/av-kit/` with exit capture. Key Round 2 receipts:

- `round2-named-sets.txt`, `round2-plan-*`, `round2-task-again.txt`, `round2-spec-*.txt`
- `round2-queue-list.txt`, `round2-queue-card.txt`, `round2-selection-checkbox.txt`, `round2-empty-drop-zone.txt`
- `round2-convert-exports.txt`, `round2-download-exports.txt`, `round2-command-consumers.txt`, `round2-status-enum-values.txt`
- `round2-name-reference-census.json`, `round2-duplicate-top-keys.json`, `round2-artifact-census.txt`, `round2-unstarted-check.json`
- `round2-f4-refs.txt`, `round2-f12-refs.txt`, `round2-task-deps.txt`, `round2-preedit-guard.json`

### Follow-up Actions

1. Close F4 by making every final bulk/header/keyboard control an independent page-E2E interaction/outcome obligation, while keeping MEU-45/46 gates phase-aware.
2. Close F12 by resolving Downloader's empty-state intake to a supported, source-backed behavior and testing the real Browse/drop outcome rather than presence.
3. Remove the consistent literal set glosses noted by the single-statement audit; do not create a new named-set copy.

### Residual Risk

After those corrections, implementation risk remains concentrated in Electron request interception for multi-row reorder/partial failures and in page-specific empty-state intake. The corrected clear-finished semantics, command-module preservation, status sets, metadata retention, lockfile removal, and executor ordering are otherwise ready for implementation.

### Verdict

`changes_required` — ten Round 1 findings are closed, but F4 remains open because the final gate can accept dead MEU-47 controls, and new F12 leaves the downloader's required file Drop/Browse surface without a supported production action.

---

## Round 3 — Final Corrections Re-Review

### Intent Anchor

Executing this plan should migrate both queue pages to the shared card surface without losing any current table or toolbar capability, then deliver the complete Phase 10 toolbar, selection, bulk, and page-appropriate empty-state behavior. The Round 3 corrections make the remaining control obligations independently testable at the correct MEU boundaries and route each empty-state action to a production intake that exists.

### Open Finding Disposition

| Finding | Disposition | Round 3 evidence |
|---|---|---|
| F4 | **closed** | `RETIRED_TOOLBAR_CONTROLS` now models every home separately; `MOUNT_GATE_PHASE_SCOPES` makes `convert` and `downloader` enforce only their shipped homes while reporting MEU-47 homes as pending, and makes `all` enforce every home with an empty pending list. AC-45.13 includes the sibling-home negative, while AC-47.10/47.10a and task rows 19/21 require interaction plus outcome assertions for every bulk action, all header states, and keyboard selection on both pages (`named-sets.json:65,580,775-783`; `implementation-plan.md:167,300-302`; `task.md:39,52,54-55`). |
| F12 | **closed** | `EMPTY_STATE_CONTRACT` is page-specific. Converter Browse/drop reuses `showFilesDialog(CONVERT_DIALOG_FILTERS)` and `staging`; Downloader renders a URL invitation whose action focuses `url-input`, then the E2E types a URL and proves the normal `POST /downloads` body. Clause 7 rejects the wrong page surface and present-but-no-outcome actions (`named-sets.json:575-583`; `implementation-plan.md:173-174,244`; `task.md:35,47`). |

### New Findings

None. No Critical, High, Medium, or Low findings were identified.

### Cross-Artifact Audit

- `named-sets.json` parses with 86 root keys, 86 unique keys, and no duplicates.
- No acceptance criterion or task row references a missing named contract. The added `MOUNT_GATE_PHASE_SCOPES` and `BULK_CONTROL_E2E_OBLIGATION` references resolve consistently across the plan and task.
- MEU sequencing remains satisfiable: `-Scope convert` gates MEU-45, `-Scope downloader` gates MEU-46, and only row 22 / AC-47.11 uses `-Scope all` after the full MEU-47 Red and wiring rows.
- The downloader invitation has a real current producer chain: `url-input` -> `addFromForm()` -> `POST /downloads`; its existing Browse control is cookie-file-specific and is not repurposed. The converter retains its current picker -> `staging` chain.
- The Round 2 literal glosses are absent from `implementation-plan.md` and `task.md`; no replacement named-set copy was introduced.
- The plan remains unstarted: all 40 actionable task rows are unchecked, and the planned toolbar, bulk, selection, gate, and MEU handoff artifacts remain absent.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | The corrected ACs and task rows agree on the MEU-45 -> MEU-46 -> MEU-47 sequence and page-specific responsibilities. |
| PR-2 Not-started confirmation | pass | All actionable rows are unchecked; planned implementation and MEU handoff outputs are absent. |
| PR-3 Task contract completeness | pass | Actionable rows retain owner, deliverable, exact validation, dependency, strategy, durable output, model, and status. |
| PR-4 Validation realism | pass | Per-home phase scopes, sibling-home self-test, full bulk/header/keyboard E2E obligations, and page-specific empty-state outcomes prevent the two demonstrated false-pass paths. |
| PR-5 Source-backed planning | pass | F4 is bound to the existing toolbar capabilities and E2 rule; F12 follows the existing page intakes and the spec's no-new-REST constraint. |
| PR-6 Handoff/corrections readiness | pass for substance review | The rolling targets and correction path remain explicit; no process-paperwork issue was used as a blocker. |
| PR-7 Scope discipline | pass | The new downloader local-file exclusion is backed by the Phase 10 no-new-REST boundary and current URL-only intake. |
| PR-8 Control reachability/totality | pass | Every corrected control has a named production entry, interaction, observable outcome, and adversarial negative. |
| PR-9 Single-statement discipline | pass | 86 unique root names; no conflicting gloss or dangling contract remains. |

### Commands Executed

Static reads and exact-evidence sweeps only; no implementation test/build suite was run because the project remains unstarted. All process output was redirected under `C:/Temp/av-kit/` with exit capture. Key Round 3 receipts include:

- `round3-name-reference-audit.txt`, `round3-ac-reference-audit.txt`, `round3-gloss-audit.txt`
- `round3-unstarted-state.json`, `round3-task-status-audit.txt`, `round3-referenced-artifacts.json`
- `round3-downloader-intake.txt`, `round3-converter-intake.txt`, `round3-emptydrop-props.txt`, `round3-spec-empty.txt`
- `round3-f4-set-totality.txt`, `round3-scope-census.txt`, `round3-primary-line-refs.txt`, `round3-preedit-guard.json`

### Residual Risk

Implementation still has normal execution risk in the new PowerShell gate and Electron request interception, but the plan now requires negative self-tests and end-to-end outcome assertions at the relevant boundaries. No unresolved plan-level blocker remains.

### Verdict

`approved` — F4 and F12 are closed, the corrections introduced no new blocking or non-blocking findings, and executing the plan as written should preserve the existing queue capabilities while delivering §10.5–10.7.
