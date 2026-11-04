---
project: "2026-09-26-p11-queue-pages"
date: "2026-09-26"
source: "docs/build-plan/11-page-layout.md"
meus: ["MEU-52", "MEU-53", "MEU-54"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 11 Queue Pages

> **Project:** `2026-09-26-p11-queue-pages`  
> **Build plan:** `docs/build-plan/11-page-layout.md` — Queue header row, Downloader page layout, Convert page layout  
> **Status:** `draft`; independent plan review required before execution

## Goal

Deliver Session 24 exactly as grouped: MEU-52 mounts one page-agnostic queue header on **both** Downloader and Convert; MEU-53 composes Downloader's add panel; MEU-54 composes Convert's add panel and queue metadata. Preserve `COMPOSITION_LOCK` (same IPC, API payloads, mutations, enablement, save behavior, and existing test-ID strings), the approved MEU-49 reorder/scroll geometry, and the Session 23 caller-owned primitive ID contract. This session does not exit Phase 11.

The worktree already contains substantial unrelated changes, including the uncommitted Session 23 canon and UI. Treat the live files as the baseline; do not reset, clean, or claim ownership of those changes. Predecessor MEU-50/51 are approved in `.agent/context/meu-status.yaml` and their rolling implementation review; the Session 23 handoffs and reflection record 579 Vitest and 85 real Electron tests after correction. Fresh execution receipts are still required.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "Rechecked for execution in C:/Temp/av-kit/s24-exec-prereq-static.txt: both graph files remain absent. This UI implementation uses TSX source, canonical specs, grep output, and exact receipts, which are Headroom bypass classes; no eligible compression payload or approved active disposition applies."
  human_message_reference: null
```

Re-evaluate this inventory before execution. This Codex API driver has no primary-driver row in `.agent/docs/harness-profiles.md`; the conservative `plan_to_exec_gate: human` applies. The Cursor-only `reviewer-auto` override in `.agent/context/harness.local.md` does not transfer to a different driver. No authorized in-harness fresh worker is resolved, so implementation rows use `shared` or `compact_continue`; an independent CLI review is still mandatory.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-52 | `.agent/context/handoffs/2026-09-26-p11-queue-pages-MEU-52-handoff.md` |
| MEU-53 | `.agent/context/handoffs/2026-09-26-p11-queue-pages-MEU-53-handoff.md` |
| MEU-54 | `.agent/context/handoffs/2026-09-26-p11-queue-pages-MEU-54-handoff.md` |
| Project review | `.agent/context/handoffs/2026-09-26-p11-queue-pages-implementation-critical-review.md` (rolling file) |

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Read canon and page contracts; freeze FIC and existing-ID inventory | — | `shared` | This plan and `task.md` |
| WP-2 | MEU-52: both page queue headers, Red → Green → gate → handoff | WP-1 | `compact_continue` | MEU-52 handoff and receipts; re-read `task.md` and handoff before WP-3 |
| WP-3 | MEU-53: Downloader add panel, Red → Green → gate → handoff | WP-2 | `compact_continue` | MEU-53 handoff and receipts; re-read `task.md` and handoff before WP-4 |
| WP-4 | MEU-54: Convert add panel, Red → Green → gate → handoff | WP-3 | `compact_continue` | MEU-54 handoff and receipts; re-read `task.md` and handoff before closeout |
| WP-5 | H1 final state, independent execution review, H2 reflection/metrics | WP-4 | `shared` | Rolling review, reflection, metrics, final receipts |

The current driver performs the coder/tester/orchestrator roles inline. It dispatches independent review; it never authors an `approved` verdict. `compact_continue` means save the named handoff and reread the live task before continuing; use native compaction only if this driver exposes it. No builder model or worker delegation is assumed.

## User Review Required

No new product decision is open. `DL1`–`DL4` and `CV1`–`CV7` are locked in the Phase 11 decision register. The plan-review loop must still examine the missing GUI reference documents described below. Following independent `approved`, the standalone `/create-plan` run ends at the resolved human plan-to-execution gate and waits for a direct user message to execute.

## Proposed Changes

### Authority and single-statement contracts

| Name | Single authority and use |
|---|---|
| `COMPOSITION_LOCK`, `PRESERVED_TESTIDS`, `QUEUE_SCROLL_CONTAINER_RULE` | `docs/build-plan/11-page-layout.md` §§Scope, Test-ID migration, Queue scroll container rule. Do not restate competing versions in code or tests. |
| `HEADER_SLOTS` | One `QueueHeaderRow` composes the existing `QueueSelectionHeader`, nonzero `StatusChip` children from each page's existing `JOB_STATUSES`/`queueSummary`, the live `processorLabel`, and the four-control `QueueToolbar`. It receives caller-owned IDs, counts, state, and callbacks; it owns no queue fetch/mutation. |
| `DL_STATUS_SET`, `CV_STATUS_SET` | `JOB_STATUSES` in `download-controls.ts` (eight) and `convert-controls.ts` (six), respectively. The visible chips filter count `> 0`; the existing full count model remains available in the read-only More summary. |
| `GUI_RULES` | `.agent/docs/emerging-standards.md` G30–G37, E2, UX1/UX2; actual `Button.tsx`, `SelectInput.tsx`, Session 23 primitives, and mockups §04–§05. |
| `POST_REVIEW_STATE` | After independent implementation `approved`, the orchestrator updates MEU-52/53/54 to `approved` with this plan binding through `meu_status.py`, renders/checks generated views, marks grouping Session 24 `approved` with the real folder, sets the hand-maintained hub Next to MEU-55, and updates current focus to Session 25. The final gate checks these exact postconditions. |

Each control AC below names a production entrypoint, the observable to assert, and a concrete negative oracle. Test titles include their AC IDs. **All** behavior-suite and Electron assertions for the active MEU are written before its production edit; run the named Vitest and fresh-build Electron targets to an assertion-failure Red receipt. A launch/build/collection failure is not Red. Tests cannot be weakened to obtain Green. Rendered interaction checks use `userEvent`; Electron E2E uses the existing renderer API seams, plus DOM geometry at the default window size. Existing E2E cases remain active.

### MEU-52 — `gui-queue-header-row`

#### Boundary Inventory

| Boundary | Schema owner | Field constraints / extra-field policy | Invalid-input response / parity |
|---|---|---|---|
| Existing queue actions on both pages | Existing `controlEnabled`, `QueueToolbar`, `useQueueBulk`, `download-commands.ts`, `convert-commands.ts`; API request models inherit `ApiModel(extra="forbid")` | `QueueHeaderRow` receives finite statuses, counts, processor state, and callbacks; it adds no REST/MCP/file/config write input. Existing action payloads and availability are unchanged. | Existing API rejects malformed request bodies with 422; no new create/update path. Test that disabled/absent actions issue zero requests. |

#### Feature Intent Contract — acceptance criteria

| AC | Type | Description and production → observable chain | Source | Negative test |
|---|---|---|---|---|
| AC-52.1 | integration | `DownloaderPage` and `ConvertPage` each mount the **same** `QueueHeaderRow` component in their queue region. Page query state → existing summary/selection/toolbar props → rendered header. Existing `queue-summary`, `convert-queue-summary`, `queue-select-all`, `processor-indicator`, `convert-processor`, and toolbar IDs stay on their respective live nodes. | Spec §Queue header row; DL3; mockups §05 | A page retaining the old separate footer/header, a duplicated ID on one page, or a caller ID on a wrapper instead of its interactive node fails. |
| AC-52.2 | integration | Each page's existing `queueSummary` → `DL_STATUS_SET`/`CV_STATUS_SET` → nonzero `StatusChip`s. `queue-summary`/`convert-queue-summary` remain on the chip group; read-only More exposes all status counts, including zeros, without changing query data. | Spec DL2; §Queue header row | A zero-count visible chip, a missing full-count entry, wrong status order, or a More action issuing a request fails. |
| AC-52.3 | integration | Existing processor envelope → `processorLabel` → live text chip in the header for Processing/Paused; Idle has no live chip. Existing IDs remain queryable as specified by §05, with readable text independent of color. | Spec §Queue header row; Phase 10 status tokens | A fabricated Idle live state, stale label after state change, or color-only status fails. |
| AC-52.4 | integration | Existing `QueueSelectionHeader` and `QueueToolbar` handlers remain wired through `QueueHeaderRow`: selecting all changes the same selection model; Start/Pause/Resume/Clear finished/overflow act through the same commands and confirmation. Observable: selection state, enabled/disabled controls, exact request ledger. | Spec `COMPOSITION_LOCK`; `10-queue-card-ui.md` §§Toolbar reduction, bulk | An unavailable action sending a request, Clear all bypassing confirmation, or a fifth toolbar control fails. |
| AC-52.5 | integration | Both page roots and queue regions retain `QUEUE_SCROLL_CONTAINER_RULE`; bulk bar/toast sit between header and list, and the existing per-page wrapper owns list scrolling. Observable: DOM ancestry, measured queue height, keyboard reorder and focus in real Electron. | Spec §Queue scroll container rule; MEU-49 AC-49.27/scroll E2E | Putting overflow on `QueueList`, allowing the region below `20rem`, or breaking ArrowDown reorder fails. |
| AC-52.6 | integration | A written, wired Electron wave exercises both product-page headers: visible controls/chips, zero-count filtering/More, processor transition, selection and toolbar action, responsive row wrapping, and preserved ID locators. | `create-plan.md` §4A; E2; grouping Session 24 | Missing page mount, inert control, or a passing unit-only substitute fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Header composition and simultaneous two-page mount | Spec | `11-page-layout.md` §Queue header row and DL3; grouping Session 24. |
| Status visibility/full count | Spec | DL2 and existing `queueSummary`/`JOB_STATUSES` give exact source of values. |
| Toolbar/selection request semantics | Local Canon | Existing `QueueToolbar`, `QueueSelectionHeader`, page command wiring and Phase 10 action contract. No handler rewrite. |
| Scroll/keyboard reorder | Spec | `QUEUE_SCROLL_CONTAINER_RULE` plus active AC-49 E2E cases. |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/queue/QueueHeaderRow.tsx` | new | Presentational `HEADER_SLOTS`, caller IDs and callbacks, read-only full-count More. |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | Mount shared header; preserve queue logic/scroll hierarchy. |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | Mount same header; preserve queue logic/scroll hierarchy. |
| `ui/tests/unit/queue-header-row.test.tsx` | new | Controlled/header state and exact caller-node assertions. |
| `ui/tests/unit/downloader-page.behavior.test.ts`, `ui/tests/unit/convert-page.behavior.test.ts` | modify | Both page mounts, action/request/scroll ancestry assertions. |
| `ui/tests/e2e/download-queue.test.ts`, `ui/tests/e2e/convert-queue.test.ts` | modify | Real Electron page header and retained keyboard-scroll oracles. |
| `ui/tests/e2e/test-ids.ts` | modify only if needed | Add new More ID; preserve every existing string. |

### MEU-53 — `gui-downloader-layout`

#### Boundary Inventory

| Boundary | Schema owner | Field constraints / extra-field policy | Invalid-input response / parity |
|---|---|---|---|
| URL/quality/audio Add form | `postDownloadCreate` in `download-commands.ts`, `DownloadCreateIn` in `schemas/downloads.py` via `ApiModel(extra="forbid")` | Existing URL, quality and audio enum/value validation; form submit and Add button share one command. | Blank/invalid URL produces no ghost row; API invalid body → 422. No new create/update route. |
| Cookie radios/browser/profile/file/test | `cookieSettingsPutBody` and `cookieTestBody` in `cookie-bar.ts`; existing Settings request model/API cookie test schema inherits `ApiModel(extra="forbid")` | Native `none`/`browser`/`file` modes, existing browser list and path semantics; current PUT/test payload keys only. | Invalid mode combinations fail at existing builder/API; malformed API body → 422. Moving fields cannot create a second write path. |
| SABR Check/Force/Clear | Existing `sabr-panel.ts` and `download-commands.ts` commands | No added user field or request body; existing busy/enablement behavior. | Busy action cannot duplicate a request; existing API mapping retained. |

#### Feature Intent Contract — acceptance criteria

| AC | Type | Description and production → observable chain | Source | Negative test |
|---|---|---|---|---|
| AC-53.1 | integration | `DownloaderPage` composes a capped, left-aligned Zone 1 with URL/Add on one row, natural-width Quality/Audio options, one status line and existing Help/error regions. Form submit Enter and Add click → `postDownloadCreate` → one POST/queue update; current IDs remain on controls. | Spec §Downloader page layout; mockup §04–§05 | Enter causing two POSTs, blank Add causing a ghost row, or an ID moved off its input/button fails. |
| AC-53.2 | integration | Caller-controlled `Disclosure` groups cookie controls and the three SABR actions. Initial open is derived once from configured non-none cookie mode or active SABR; subsequent toggle is local presentation state. Observable: `add-advanced-toggle` button ARIA, panel visibility/focus, persisted cookie action ledger. | Spec DL1; Session 23 `Disclosure` contract | A settings refresh overriding a user's toggle, hidden focusable controls, or toggle causing a PUT fails. |
| AC-53.3 | integration | Three cookie modes use `SegmentedControl` native radios with the existing `cookie-mode-*` IDs on each radio. Browser/profile/file/Browse/test controls preserve their current conditional visibility and exact request payloads. | Spec §Downloader page layout; `COMPOSITION_LOCK`; Session 23 caller-ID correction | A click on a styled label that leaves the radio/request unchanged, an unrelated extra PUT field, or a lost radio ID fails. |
| AC-53.4 | integration | Active SABR → warning `StatusChip` beside Quality and status in Advanced; inactive SABR is hidden. `sabr-check-btn`, `sabr-force-btn`, `sabr-clear-btn` remain live inside Advanced and call the existing commands once. | Spec DL4; mockup §05 | Inactive warning, duplicate SABR request, or a moved button with no callback fails. |
| AC-53.5 | integration | The new controls pane retains `QUEUE_SCROLL_CONTAINER_RULE` and MEU-52 header/list/bulk behavior. Real Electron checks at the default window size preserve visible queue controls and AC-49 keyboard reorder; new/moved interactive elements get presence, interaction, and visual-state assertions. | Spec §Queue scroll container rule; E2; Session 23 next-session RULE-1 | Queue under the minimum height, a stale page locator, or broken reorder fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Add panel zones, cap, status line and ID migration | Spec | `11-page-layout.md` §Downloader and DL §05; shared `--layout-page-max-width`. |
| Advanced initial vs later state | Spec | DL1 explicitly separates initial derivation from local toggling. |
| Cookie/SABR payload and enabling | Local Canon | `cookie-bar.ts`, `download-commands.ts`, Phase 6 GUI actions; composition lock preserves behavior. |
| GUI variants and feedback | Local Canon | `Button.tsx`, primitives, G30–G35/E2 and mockup §04; keep current request success/error feedback. |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | Zone 1 panel, controlled disclosure, segment/chip, unchanged commands and IDs. |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modify | Red-first Add, cookie, SABR, disclosure and scroll behavior. |
| `ui/tests/e2e/download-queue.test.ts` | modify | Real Electron form/disclosure/segment/SABR/geometry assertions. |
| `ui/tests/e2e/test-ids.ts` | modify | Register `add-advanced-toggle` without changing prior strings. |
| `ui/src/renderer/src/styles.css` | modify only if needed | Shared token classes, no duplicate cap/raw color/geometry animation. |

### MEU-54 — `gui-convert-layout`

#### Boundary Inventory

| Boundary | Schema owner | Field constraints / extra-field policy | Invalid-input response / parity |
|---|---|---|---|
| Dropped/Browsed file paths, task/preset/cut/extract/override options and Add | `createConversionBody` in `convert-body.ts`, `postConversionCreate` in `convert-commands.ts`, `ConversionCompressIn`/`ConversionCutIn`/`ConversionExtractIn` via `ApiModel(extra="forbid")` | Existing discriminated task kinds, preset IDs, time/scale/quality ranges and path list; staged-chip × removes one local pre-Add occurrence only. | Builder rejects invalid/empty staging before POST; API malformed/missing/out-of-range/extra fields → 422. No update variant is introduced. |
| Output folder and Skip existing Save | Existing `useConverterSettings` form/save and `SettingsPutIn` via `ApiModel(extra="forbid")` | Existing path/boolean fields and explicit Save; dirty state drives variant. | No PUT while merely editing or removing staged chips; invalid settings body → 422; Settings-page explicit Save remains unchanged. |
| GPU Refresh | Existing Convert GPU query/refresh command | No new user payload; one visible command. | A second hidden instance or duplicate request fails. |

#### Feature Intent Contract — acceptance criteria

| AC | Type | Description and production → observable chain | Source | Negative test |
|---|---|---|---|---|
| AC-54.1 | integration | `ConvertPage` composes capped, left-aligned Zone 1: native-radio task segment plus exact `gpuChipLabel` and one always-visible Refresh; drop strip with Browse and Add on one row; staged chips; one task-options row; Advanced override disclosure; output footer. Existing §05 IDs remain on live controls. | Spec §Convert page layout; CV5/CV6; mockup §04–§05 | A hidden duplicate Refresh, changed GPU label, wrong task radio value, or ID on a noninteractive wrapper fails. |
| AC-54.2 | integration | Drop/Browse → local `staging` → one chip per path. Chip × removes exactly one selected staged occurrence, updates the Add count, and sends **zero** network/IPC deletion requests. Remaining paths still pass to `createConversionBody` on Add. | Spec CV1/CV2; `COMPOSITION_LOCK` | Removing one chip clears all duplicates, deletes an already queued job, or posts before Add fails. |
| AC-54.3 | integration | Add label includes nonzero staged count, stays the same `convert-add` button and uses the existing `addFromForm`/`postConversionCreate` command. Empty/invalid staging retains current no-POST focus/error behavior; valid Add preserves the exact payload and queue update. | Spec CV2; `08-video-conversion.md` GUI contract | Count-only label with a dead button, a changed request body, or empty staging POST fails. |
| AC-54.4 | integration | Task, preset, cut mode and extract scope choices retain their wire values and enablement while using native-radio `SegmentedControl`; `convert-advanced` remains the live controlled disclosure for Compress overrides. All caller IDs land on exact radios/inputs and existing error feedback remains. | Spec §Convert; `COMPOSITION_LOCK`; G30–G35; Session 23 RULE-1 | Choice changing only visual style, hidden focusable override, or stale payload after task switch fails. |
| AC-54.5 | integration | Existing `useConverterSettings` form → Output folder/Skip existing footer → explicit `converter.save()`. `convert-page-save` is ghost/sm when clean, primary/sm with existing dirty-dot label when dirty; edits alone issue no PUT. | Spec CV3/CV4; Phase 8 settings contract | Autosave on edit, Save losing dirty status before response, or Settings-page save mutation changing fails. |
| AC-54.6 | integration | Existing conversion queue data → card metadata line contains only carried `kind`, preset/range/scope and encoder fields; absent optional preset/encoder falls back to task kind. MEU-52 header, full count model, bulk actions, and `QUEUE_SCROLL_CONTAINER_RULE` remain intact. | Spec CV7; §Convert page layout; Phase 10 card slot contract | Undefined metadata text, invented API field, broken keyboard reorder, or changed toolbar action fails. |
| AC-54.7 | integration | A written, wired real Electron wave covers task radio/Refresh, drop/Browse and per-chip removal with request ledger, Add count/payload, Advanced choices, output Save state, card metadata, and queue scroll/reorder at the default window size. | E2; grouping Session 24 | Dead moved control, unit-only proof, or a passing test with conditional early return fails. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Add panel order, geometry and ID migration | Spec | `11-page-layout.md` §Convert and CV §05; mockup §04. |
| Staged removal/count and Save model | Spec | CV1–CV4 settle the former §06 forks; no backend deletion or autosave. |
| GPU chip, Refresh and card metadata | Spec | CV5–CV7 and existing `gpuChipLabel`/queue fields. |
| Option values, validation, request payloads | Local Canon | `convert-body.ts`, `convert-controls.ts`, `useConverterSettings.ts`, Phase 8 and API schemas. |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | Zone 1 composition, local staged removal, segment/disclosure/footer, carried card metadata. |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | Red-first UI/API ledger, option, save and metadata assertions. |
| `ui/tests/e2e/convert-queue.test.ts` | modify | Real Electron moved-control, staging, Save, card and scroll assertions. |
| `ui/tests/e2e/test-ids.ts` | modify only if needed | Add distinct staged-remove ID; retain all prior values. |
| `ui/src/renderer/src/styles.css` | modify only if needed | Existing token-based layout styling. |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Transcript channel layout/header | deferred | MEU-55 | Grouping Session 25 and `11-page-layout.md` §Transcript assign its own QueueCard/action migration. |
| TTS layout and shared ProgressBar transfer | deferred | MEU-56 | Grouping Session 25 and canon §TTS/Supersession assign closed MEU-48's TTS AC there. |
| Capture and Settings page composition | deferred | MEU-57, MEU-58 | Grouping Session 26 and canon §§Capture/Settings; this session changes only two queue pages. |
| Phase 11 phase gate | deferred | MEU-58 | Grouping Session 26 is the phase exit; Session 24 runs targeted and full UI regression, not a premature phase-exit claim. |
| New backend endpoint, queue mutation, or persisted staged-chip removal | out-of-scope | — | `11-page-layout.md` `COMPOSITION_LOCK` and CV1; Session 24 is UI composition. |
| Commit, push, merge, release, deploy | out-of-scope | — | `AGENTS.md` §Human Approval Gate; none is authorized by `/create-plan`. |

## BUILD_PLAN.md Audit

`docs/BUILD_PLAN.md` already links Phase 11 and the grouping, but its hand-maintained Next text still says MEU-52. During H1, after the three MEUs move to `ready_for_review`, update that line and the grouping to describe Session 24 review and MEU-55 as the next pending dependent work. Do not hand-edit generated tracker spans. **After** H1-6 independent implementation approval, task H2-2 produces and verifies `POST_REVIEW_STATE`: status updates to `approved`, render/check, grouping approval, final hub Next, and current focus. The final completion gate asserts that state; H1-3 cannot claim post-review status.

## Verification Plan

All commands use `rtk proxy`, redirect every stream under `C:/Temp/av-kit/`, capture `$LASTEXITCODE` before receipt reads, and exit with that code. Execute only **after plan approval and the human execution message**. The old `tools/validate_codebase.py` described in the quality-gate skill is absent; use these registered runnable UI commands.

| Check | Exact command | Required evidence |
|---|---|---|
| Targeted MEU-52 | `rtk proxy npm --prefix ui run test -- tests/unit/queue-header-row.test.tsx tests/unit/downloader-page.behavior.test.ts tests/unit/convert-page.behavior.test.ts *> C:/Temp/av-kit/p11q-meu52-unit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-meu52-unit.txt -Tail 35; exit $code` | All AC-52 assertions Green and prior behavior cases Green. |
| Targeted MEU-53 | `rtk proxy npm --prefix ui run test -- tests/unit/downloader-page.behavior.test.ts *> C:/Temp/av-kit/p11q-meu53-unit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-meu53-unit.txt -Tail 35; exit $code` | All AC-53 assertions Green. |
| Targeted MEU-54 | `rtk proxy npm --prefix ui run test -- tests/unit/convert-page.behavior.test.ts *> C:/Temp/av-kit/p11q-meu54-unit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-meu54-unit.txt -Tail 35; exit $code` | All AC-54 assertions Green. |
| Red Electron MEU-52 | `rtk proxy pwsh -NoProfile -Command { rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/p11q-52-red-build.txt; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR=$null; $p='C:/Temp/av-kit/p11q-52-e2e-red.json'; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/download-queue.test.ts tests/e2e/convert-queue.test.ts -g AC-52 --reporter=json --outputFile=$p *> C:/Temp/av-kit/p11q-52-e2e-red.txt; $rc=$LASTEXITCODE; if($rc -eq 0 -or -not(Test-Path $p)){throw 'missing AC-52 E2E Red'}; $j=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($p)); $body=Get-Content $p -Raw; if($j.stats.unexpected -lt 1 -or $body -notmatch 'AC-52' -or (-not ($body -match 'AssertionError' -or $body -match 'expect\('))){throw 'AC-52 E2E assertion Red absent'}; 'PASS AC-52 E2E RED' } *> C:/Temp/av-kit/p11q-52-e2e-red-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-52-e2e-red-check.txt -Tail 25; exit $code` | Fresh build succeeded; at least one collected AC-52 page assertion failed. |
| Red Electron MEU-53 | `rtk proxy pwsh -NoProfile -Command { rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/p11q-53-red-build.txt; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR=$null; $p='C:/Temp/av-kit/p11q-53-e2e-red.json'; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/download-queue.test.ts -g AC-53 --reporter=json --outputFile=$p *> C:/Temp/av-kit/p11q-53-e2e-red.txt; $rc=$LASTEXITCODE; if($rc -eq 0 -or -not(Test-Path $p)){throw 'missing AC-53 E2E Red'}; $j=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($p)); $body=Get-Content $p -Raw; if($j.stats.unexpected -lt 1 -or $body -notmatch 'AC-53' -or (-not ($body -match 'AssertionError' -or $body -match 'expect\('))){throw 'AC-53 E2E assertion Red absent'}; 'PASS AC-53 E2E RED' } *> C:/Temp/av-kit/p11q-53-e2e-red-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-53-e2e-red-check.txt -Tail 25; exit $code` | Fresh build succeeded; at least one collected AC-53 page assertion failed. |
| Red Electron MEU-54 | `rtk proxy pwsh -NoProfile -Command { rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/p11q-54-red-build.txt; if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}; $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR=$null; $p='C:/Temp/av-kit/p11q-54-e2e-red.json'; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/convert-queue.test.ts -g AC-54 --reporter=json --outputFile=$p *> C:/Temp/av-kit/p11q-54-e2e-red.txt; $rc=$LASTEXITCODE; if($rc -eq 0 -or -not(Test-Path $p)){throw 'missing AC-54 E2E Red'}; $j=ConvertFrom-Json -InputObject ([IO.File]::ReadAllText($p)); $body=Get-Content $p -Raw; if($j.stats.unexpected -lt 1 -or $body -notmatch 'AC-54' -or (-not ($body -match 'AssertionError' -or $body -match 'expect\('))){throw 'AC-54 E2E assertion Red absent'}; 'PASS AC-54 E2E RED' } *> C:/Temp/av-kit/p11q-54-e2e-red-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-54-e2e-red-check.txt -Tail 25; exit $code` | Fresh build succeeded; at least one collected AC-54 page assertion failed. |
| Typecheck | `rtk proxy npm --prefix ui run typecheck *> C:/Temp/av-kit/p11q-typecheck.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-typecheck.txt -Tail 30; exit $code` | Exit 0, no errors. |
| Lint | `rtk proxy npm --prefix ui run lint *> C:/Temp/av-kit/p11q-lint.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-lint.txt -Tail 30; exit $code` | Exit 0, no warnings. |
| Full UI unit | `rtk proxy npm --prefix ui run test *> C:/Temp/av-kit/p11q-vitest.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-vitest.txt -Tail 35; exit $code` | Exit 0, exact count recorded. |
| Ordinary build | `rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/p11q-build.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-build.txt -Tail 35; exit $code` | Fresh `ui/out` for E2E. |
| Both page Electron wave | `rtk proxy pwsh -NoProfile -Command { $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR=$null; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/download-queue.test.ts tests/e2e/convert-queue.test.ts *> C:/Temp/av-kit/p11q-page-e2e-inner.txt; exit $LASTEXITCODE } *> C:/Temp/av-kit/p11q-page-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-page-e2e-inner.txt -Tail 40; exit $code` | Actual Electron page tests, both new and existing. |
| Full Electron regression | `rtk proxy pwsh -NoProfile -Command { $env:ELECTRON_RUN_AS_NODE=$null; $env:AVKIT_E2E_OUT_DIR=$null; rtk proxy npm --prefix ui run test:e2e *> C:/Temp/av-kit/p11q-full-e2e-inner.txt; exit $LASTEXITCODE } *> C:/Temp/av-kit/p11q-full-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-full-e2e-inner.txt -Tail 40; exit $code` | All existing waves; external launch failure only may be `[B]` with exact receipt and linked CI follow-up. |
| Contract/anti-placeholder audit | `rtk proxy pwsh -NoProfile -Command { rtk proxy rg -n -e 'TODO' -e 'FIXME' -e 'NotImplementedError' -e 'transition-all' -e 'bg-\[#' ui/src/renderer/src/components/queue/QueueHeaderRow.tsx ui/src/renderer/src/features/downloader/DownloaderPage.tsx ui/src/renderer/src/features/converter/ConvertPage.tsx *> C:/Temp/av-kit/p11q-source-audit.txt; $rc=$LASTEXITCODE; if($rc -eq 0){Get-Content C:/Temp/av-kit/p11q-source-audit.txt; exit 1}; if($rc -gt 1){Get-Content C:/Temp/av-kit/p11q-source-audit.txt; exit $rc}; 'PASS zero audit hits' } *> C:/Temp/av-kit/p11q-source-audit-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/p11q-source-audit-check.txt; exit $code` | `rg` code 1 means clean zero hits; matches and IO errors fail. Both unfiltered and classified receipts survive. |

No `packages/api/` modification is planned. H1 records an exact scoped diff; if an API file changes, stop and re-plan the boundary, then run the two-step OpenAPI `--check`/regenerate protocol rather than silently skipping it.

## GUI Element Compliance Check

`create-plan.md` §4A applies. The named `docs/gui-element-reference.md`, three GUI element indexes, and `.agent/docs/gui-standards-enforcement.md` do not exist in this checkout (`C:/Temp/av-kit/s24-gui-guides.txt`, `s24-gui-paths.txt`); therefore their checklist and Target Spec columns cannot be claimed as checked. The actual available controls are `Button.tsx` (five variants, three sizes), `SelectInput.tsx`, `Disclosure`, `SegmentedControl` native radios, `StatusChip`, `FormRow`, `PathRow`, `styles.css`, the two mockups §04–§05, and G30–G37/E2. Map Add to primary/md, Refresh/SABR/Browse to existing secondary or ghost/sm, clean Save to ghost/sm and dirty Save to primary/sm, Advanced to Disclosure's ghost Button, choices to native radios, and status to readable chips. Keep existing request/status feedback. Every moved or new interactive control has a written, wired Electron assertion in AC-52.6, AC-53.5, or AC-54.7. The reviewer must assess this live-source substitution and the missing-reference risk; no nonexistent checklist is represented as passed.

## Stop Conditions

Do not enter execution before independent plan approval **and** a direct human execution message for this driver. In execution, stop/re-plan if MEU-50/51 cease to be approved, the required behavior needs a new API/persisted mutation, any §05 ID/action cannot be preserved, the GUI gap exposes a material unresolved product choice, Red is not demonstrated, or a P1 check fails. A reviewer `changes_required` verdict means correct and re-dispatch inside the allowed review loop; the third unapproved plan round is a hard stop. No commit/push/merge/release/deploy without direct human approval.

## Open Questions

None remain for product behavior: Phase 11's DL/CV decision register resolved them. The absent GUI guide/index/checklist files are an evidence gap, not permission to invent variants or skip E2E. If independent review finds a material choice not settled by the live canon/components, research the specific fork and route a genuine human decision through the review loop.

## Research References

- `docs/build-plan/11-page-layout.md` §§Scope, Decision register, Queue scroll container rule, Queue header row, Downloader, Convert, Test-ID migration.
- `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md` §§Sessions, Session 24.
- `docs/build-plan/06-gui.md`, `08-video-conversion.md`, `10-queue-card-ui.md` for inherited behavior; two 2026-09-03 Downloader/Convert mockups §§04–06 for composition.
- `docs/execution/reflections/2026-09-26-p11-layout-canon-reflection.md` §Next Session Design Rules; MEU-50/51 approved handoffs and rolling review.

## Execution amendments — 2026-09-26

- **Human-approved:** after the seven obsolete source-shape assertions were explained individually, Mat replied “ok go ahead.” Update AC-47.5a's direct selection mount, AC-33.3's literal task radios, AC-33.5's 400-character Advanced proximity, both old summary wrappers, AC-46.5's direct toolbar import, and AC-51.7's pre-adoption page restriction. Preserve behavior expectations and verify the new shared component wiring; retain the primitive restriction for the four pages awaiting adoption.
- **Local Canon:** the newly adopted D6 task linter rejects inline PowerShell scriptblocks in task-table commands. `validate-task.ps1` contains the eight original procedures, and `task.md` invokes them with `-File`. Criteria and dependency ordering are unchanged. The linter passes all 19 rows.
- **Local Canon:** current reviewer routing requires actual author-vendor diversity. The OpenAI author cannot use the configured OpenAI reviewer; resolve eligibility before provider invocation and use PROFILE B4's Mat fallback if refusal remains. H2 remains ordered after a target-bound independent approval.
