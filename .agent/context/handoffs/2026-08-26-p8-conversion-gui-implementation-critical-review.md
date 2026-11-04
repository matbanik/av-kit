---
date: 2026-08-26
review_mode: implementation
target_plan: docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
template_version: 2.1
requested_verbosity: standard
---

# Critical Review: p8-conversion-gui — Round 1

> **Review Mode**: `implementation`
> **Verdict**: `changes_required`

## Intent Anchor

This execution was supposed to deliver MEU-33: a lazy, shell-reachable Convert page with a Downloader-shaped queue, safe multi-file staging, working converter settings, AppShell-owned palette delivery, and Wave 8 Electron proof, while preserving the Session 15 scope lock. Most structural and navigation contracts are present, but the delivered GUI does not fully achieve that intent because two user-visible settings/input behaviors violate the approved contract and the integration tests do not expose one of them.

## Scope

**Target plan**: `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md`

**Correlated task and named sets**: `docs/execution/plans/2026-08-26-p8-conversion-gui/task.md`; `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json`

**Seed and complete handoff set**: `.agent/context/handoffs/2026-08-26-p8-conversion-gui-MEU-33-handoff.md`. The plan and task identify Session 15 as MEU-33 only, so this one handoff is the complete project handoff set.

**Implementation reviewed**: the named converter page/support files, router/NavRail/AppShell/registry/HelpCard, Settings converter card/schema/hook, form guard, main/preload IPC, the four named test files, Phase 8/GUI specifications, and current SSOT state.

**Scope locks honored**: no Session 8c/MEU-27 work was started or required; Downloader-to-Convert remains a valid named deferral; no new MEU IDs were introduced; no edits to `packages/api/` or `mcp-server/` are required by the findings below. `P:/av-kit` is not a Git repository, so current file state, generated schema checks, fixed-count tests, and receipts were used instead of `git diff`.

## Findings

| Finding | Severity |
|---------|----------|
| **F1 — High confidence — `converter.default_preset` is saved but ignored by the Convert page (AC-33.4 / Settings namespace contract).** The specification defines `default_preset` for the Compress chips (`docs/build-plan/08-video-conversion.md:484`), and `useConverterSettings` correctly loads it (`ui/src/renderer/src/features/converter/useConverterSettings.ts:24-45`). However, `ConvertPage` always initializes the selected preset and its Advanced values from the hard-coded `PRESET_DEFAULT` (`ui/src/renderer/src/features/converter/ConvertPage.tsx:103-109`), never references `converter.form.default_preset`, and always sends that local preset in the create body (`ui/src/renderer/src/features/converter/ConvertPage.tsx:202-218`). Reproduction: save `default_preset=archival`, leave/reopen Convert, browse a file, and Add; the page still selects/posts `balanced`. The Settings control is therefore functionally inert for its documented consumer. **Recommendation/status:** initialize or synchronize the pristine preset and its catalog-derived Advanced values from the loaded converter form without overwriting later user selection; add a runtime test whose GET returns `archival` and whose captured POST proves `preset: "archival"`. Status: open. | High |
| **F2 — High confidence — Browse excludes the required audio inputs (AC-33.7 / Spec 124-132).** The specification requires the multi-file dialog to use video/audio filters (`docs/build-plan/08-video-conversion.md:129`). Production defines only a `Video` filter with six video extensions and passes it to `showFilesDialog` (`ui/src/renderer/src/features/converter/ConvertPage.tsx:56`, `ui/src/renderer/src/features/converter/ConvertPage.tsx:449-459`). A user cannot browse to supported audio-only inputs through the required Browse path; the Electron E2E stub ignores the supplied filters, so W8-4 cannot detect the defect. **Recommendation/status:** add the supported audio extensions/filter to the renderer dialog request and assert the exact filters at the IPC boundary; keep `show-file-dialog` unchanged. Status: open. | High |
| **F3 — High confidence — Advanced is not Compress-only as locked (AC-33.5).** Both the specification and approved implementation lock say Advanced is Compress-only (`docs/build-plan/08-video-conversion.md:148`; `docs/execution/plans/2026-08-26-p8-conversion-gui/implementation-plan.md:110`). The `convert-advanced` button is rendered unconditionally (`ui/src/renderer/src/features/converter/ConvertPage.tsx:505-514`); on Cut or Extract it opens a mostly empty card containing only GPU Refresh (`ui/src/renderer/src/features/converter/ConvertPage.tsx:515-574`). **Recommendation/status:** render the disclosure/card only for Compress and add a task-switch visibility assertion. Status: open. | Medium |
| **F4 — High confidence — IR-7/C3: integration AC-33.16 and AC-33.17 are certified by source inspection without runtime persistence assertions.** The handoff marks both integration ACs complete using only `convert-page.test.ts` (`.agent/context/handoffs/2026-08-26-p8-conversion-gui-MEU-33-handoff.md:50-51`). Those tests read source text and schema shape (`ui/tests/unit/convert-page.test.ts:467-513`); W8-3 clicks/fills the Settings controls and Save but never asserts dirty state, zero PUT before Save, PUT count/body on Save, or persisted reload state (`ui/tests/e2e/convert-queue.test.ts:308-322`). This gap concretely allowed F1 to pass 190 Vitest tests and 10 Electron tests. **Recommendation/status:** add RTL or Electron assertions for the dirty label/class, no request before Save, exactly one strict four-key PUT after Save, and reloaded values; cite those runtime tests for AC-33.16/.17 in the corrected handoff. Status: open. | Medium |

## Test Rigor Audit (IR-5)

| Test file | Rating | Evidence |
|-----------|--------|----------|
| `ui/tests/unit/convert-page.test.ts` | 🔴 Weak for integration ACs; 🟢 strong for pure helpers | Time parsing, create-body, polling, control-state, reorder, and label helpers have specific value/negative assertions. Many integration-titled tests use `readFileSync`/regex only; AC-33.16/.17 have no mounted component or fetch assertions and false-pass F1. |
| `ui/tests/e2e/convert-queue.test.ts` | 🟡 Adequate overall | W8-1/2/4/5/6 exercise real Electron navigation, zero-POST negatives, queue mutation, confirms, state, and off-route focus. W8-3 performs all census-required interactions but usually asserts only presence/clickability, not resulting values or requests. |
| `ui/tests/e2e/launch.test.ts` | 🟢 Strong | Real Electron assertions cover the Wave 0 rail, Downloader home, hash history, and a navigation transition. |
| `ui/tests/unit/e2e-wiring.test.ts` | 🟡 Adequate | It accurately checks file/test-id registration, but it is intentionally a wiring census rather than behavior proof. |

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | pass | Intact `C:/Temp/av-kit/e2e-wave8.txt` records a compiled Electron launch with 10 Playwright passes; independent build reproduced the lazy Convert chunk. |
| IR-2 Stub behavioral compliance | pass | The Wave 8 seam maintains collection state for Add/list/delete and returns `{ items, processor }`; the Browse E2E stub returns the named path. F2 is a filter-contract gap outside what the stub observes. |
| IR-3 Error mapping completeness | n/a | MEU-33 adds no REST route or server error mapping; OpenAPI remains in sync. |
| IR-4 Fix generalization | n/a | This is execution-review Round 1, not a corrections recheck. |
| IR-5 Test rigor | fail | F4 and the test-file grades above. |
| IR-6 Boundary validation coverage | partial | Create discriminated union, settings body, and IPC payloads are strict; empty create and extra fields are rejected. Reorder is behaviorally guarded as a nonempty full permutation, although the planned client Zod reorder schema is not present. |
| IR-7 Deferral and AC integrity | fail | All 24 plan AC IDs appear in the handoff and MEU-27/Downloader handoff deferrals are valid. Lifecycle evidence fails C3 for AC-33.16/.17 (F4). |

### Adversarial Verification

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | pass | Independent Red oracle: `PASS: RED_ORACLE ui MEU-33 AC-33 count=24`; JSON has 25 failures because the same Red run also failed the action audit. |
| AV-2 No bypass hacks | pass | No forced early-return/monkeypatch assertion bypass was found in the named tests. |
| AV-3 Changed paths asserted | partial | Helper and core E2E paths have explicit outcomes, but Settings persistence paths are merely clicked/source-grepped (F4). |
| AV-4 No skip/only masking | pass | Independent G36 scan found no `skip`, `todo`, or `only` markers. |
| AV-5 No unresolved placeholders | pass | Independent converter/main scan found no `TODO`, `FIXME`, or `NotImplementedError`. |
| AV-6 Source-backed criteria | pass | The 24 ACs use Spec, Local Canon, Research-backed, or approved carry-forward rules; no invented MEU or unsupported deferral was found. |

### Adversarial Contract Surfaces

| Surface | Result | Evidence |
|---------|--------|----------|
| Lazy Convert route and chunk | pass | `router.tsx:46-51` uses `lazyRouteComponent`, keeps Downloader static, and retains `ModuleSkeleton`; build emitted `ConvertPage-BDVf0rJH.js`. |
| Rail / Ctrl+4 / RULE-3 | pass | NavRail Convert is fourth with `Film`; rail and Ctrl+4 navigate only; W8-2 clicks the rail and proves two independent zero-POST counters. |
| Staging IPC/drop | partial | New multi-file channel, unchanged single-file channel, preload `webUtils`, no drop auto-POST, and empty Add negative pass. Browse filter contract fails (F2). |
| Create body / Cut / Extract | pass | Strict discriminated union, nonempty paths, preset wires, optional overrides, time-to-ms, invalid range rejection, and `first`/`all` were reproduced by unit assertions. |
| List / poll / statuses / reorder | pass | Envelope, query key, 1000/5000 intervals, no job `Paused`, full permutation, and nonempty PUT guard are present. |
| Enabled states / GPU chip | pass | Processor/FFmpeg gates, GPU mount/refresh paths, and all required chip labels are present; chip is not a select. |
| G23 converter persistence | partial | Save-only wiring, dirty class/label, strict four-key body, and no converter debounce are present; default preset consumption fails (F1) and lifecycle proof is weak (F4). |
| Palette G11 | pass | Registry dispatches events only; AppShell owns listeners; two-rAF off-route delivery and empty-staging focus are runtime-tested. |
| G20 confirms | pass | Both portal confirms and both cancels are clicked by W8-4; no `window.confirm`. |
| HelpCard G26 | pass | `converter` union, disclosure ARIA, collapse key, route, and required topics are present. |
| Wave 8 totality | pass | Independent census passes; 7 visual-only IDs and all other interaction bindings reconcile; cumulative count is 35. |
| G30-G36 / fixed REST-MCP state | pass | No skips/placeholders/raw-hex button classes found; Add/Remove variants comply; OpenAPI check passes; route-index suite 63 passed with 61 routes and MCP action-index suite 61 passed with 59 actions. |
| SSOT / Session lock | pass | MEU-33 is `ready_for_review` and bound without trailing slash; Phase 8 has the three required slash-terminated plans; the unique hub Next string is exact; MEU-27 remains untouched. |

## Commands Executed

All command streams were isolated under `C:/Temp/av-kit/p8-cg-exec-r1-*`; exit status was captured before receipt reads.

| Command | Result |
|---------|--------|
| `cd ui; npx tsc --noEmit` | exit 0 |
| `cd ui; npx vitest run --allowOnly=false` | exit 0; 30 files, 190 tests passed |
| `cd ui; npx eslint src/ tests/ --max-warnings 0` | exit 0 |
| `cd ui; npm run build` | exit 0; `ConvertPage-BDVf0rJH.js` emitted |
| `assert-red-oracle.ps1 -Kind ui -Meu 33` | exit 0; 24 distinct AC-33 Red titles |
| `assert-e2e-control-census.ps1` | exit 0; PASS |
| Existing `e2e-wave8.txt` inspection | intact; 10 Playwright tests passed in real Electron; no second launch required |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | exit 0 |
| `uv run pytest tests/e2e/test_api_openapi.py -q` | exit 0; 63 passed; route count assertion remains 61 |
| `cd mcp-server; npx vitest run tests/action-index.test.ts --allowOnly=false` | exit 0; 61 passed; action count assertion remains 59 |
| `assert-handoff-acs.ps1` | exit 0; all plan AC IDs present in handoff |
| Independent G36 and anti-placeholder scans | PASS |
| SSOT/current-state assertion | PASS; exact MEU binding, three Phase 8 plan entries, and unique hub Next |
| `git status --short` | exit 128; workspace is not a Git repository, as anticipated by the review brief |

## Follow-up Actions

1. Correct F1 and add the described non-balanced runtime scenario.
2. Correct F2 within renderer/IPC tests only; do not change the existing single-file dialog contract.
3. Correct F3 and add a Cut/Extract negative visibility assertion.
4. Replace the AC-33.16/.17 source-only proof with runtime persistence assertions, then update the MEU-33 handoff evidence and run `/execution-critical-review` Round 2.

No follow-up requires starting MEU-27, adding Downloader-to-Convert, inventing an MEU, or editing `packages/api/` or `mcp-server/`.

## Open Questions / Assumptions

None. The findings follow the approved plan/spec contract and do not re-litigate named deferrals.

## Residual Risk

The quality gates and existing Electron receipt establish broad regression safety, but they cannot compensate for the two concrete user-visible contract failures or the Settings lifecycle false-pass. The unchanged REST/MCP assertion counts prove current census state, not historical non-edit provenance, because the workspace has no Git metadata.

## Verdict

`changes_required` — F1 and F2 are evidence-backed High behavioral/contract failures. F3 and F4 are Medium and would not block on their own. Product code and tests were not modified by this review.

---

## Recheck (2026-08-26) — Round 2

**Workflow**: `/execution-critical-review` Round 2 recheck  
**Agent**: `gpt-5.6-sol`  
**Scope**: Session 15 / MEU-33 only

### Intent Anchor

This recheck verifies that the MEU-33 Convert GUI now honors saved converter defaults, accepts the specified video and audio Browse inputs, keeps Advanced Compress-only, and proves G23 persistence at runtime without regressing the already-passing lazy-route, navigation, portal, census, or fixed REST/MCP contracts.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|--------------|----------------|
| F1 — saved `default_preset` ignored | open | ✅ Fixed — ready-gated pristine hydration is present and the archival POST scenario passes |
| F2 — Browse omitted audio filters | open | ✅ Fixed — the exact Video and Audio sets reach `showFilesDialog` |
| F3 — Advanced rendered outside Compress | open | ✅ Fixed — Cut removes `convert-advanced`; the card is Compress-gated |
| F4 — AC-33.16/.17 lacked runtime persistence proof | open | ✅ Fixed — RTL and Electron evidence prove zero PUT while dirty and one PUT on Save |

### Confirmed Fixes

- **F1 fixed.** `ConvertPage` waits for `converter.ready`, hydrates `converter.form.default_preset` plus catalog-derived Advanced values while `presetTouched` is false, and preserves later user selection (`ui/src/renderer/src/features/converter/ConvertPage.tsx:150`, `ui/src/renderer/src/features/converter/ConvertPage.tsx:214`; readiness owner at `ui/src/renderer/src/features/converter/useConverterSettings.ts:85`). Runtime AC-33.4 selects the archival chip through its `bg-accent` class and captures `preset: 'archival'` in the Add POST (`ui/tests/unit/convert-page.behavior.test.ts:199`, `ui/tests/unit/convert-page.behavior.test.ts:216`). Status: **fixed**.
- **F2 fixed.** `CONVERT_DIALOG_FILTERS` contains Video and Audio groups with the specified extensions (`ui/src/renderer/src/features/converter/convert-filters.ts:1`, `ui/src/renderer/src/features/converter/convert-filters.ts:14`), and Browse maps that array into `showFilesDialog` (`ui/src/renderer/src/features/converter/ConvertPage.tsx:475`). Runtime AC-33.7 captures and compares the IPC-boundary array (`ui/tests/unit/convert-page.behavior.test.ts:235`). Status: **fixed**.
- **F3 fixed.** The disclosure and card are both gated by `kind === 'compress'`, and leaving Compress closes the card (`ui/src/renderer/src/features/converter/ConvertPage.tsx:144`, `ui/src/renderer/src/features/converter/ConvertPage.tsx:529`, `ui/src/renderer/src/features/converter/ConvertPage.tsx:541`). Runtime AC-33.5 proves `convert-advanced` is absent on Cut (`ui/tests/unit/convert-page.behavior.test.ts:220`). W8-3 still opens Advanced while on Compress. Status: **fixed**.
- **F4 fixed.** Runtime AC-33.16 proves zero converter PUTs before Save, the dirty class/label, exactly one PUT, and an exact four-key body; AC-33.17 proves the page Save path (`ui/tests/unit/convert-page.behavior.test.ts:250`, `ui/tests/unit/convert-page.behavior.test.ts:288`). W8-3 independently records `__e2eConverterPuts` from 0 to 1 after `convert-settings-save` and asserts `btn-save-dirty` (`ui/tests/e2e/convert-queue.test.ts:349`). Status: **fixed**.

### Findings

| Finding | Severity |
|---------|----------|
| None. No open High/Critical behavioral, contract, persistence, or false-claim finding survived verification. | — |

### Test Rigor Audit (IR-5)

| Test file | Rating | Evidence |
|-----------|--------|----------|
| `ui/tests/unit/convert-page.test.ts` | 🟡 Adequate | Retains 24 distinct AC-33 titles and specific helper/source-contract assertions; runtime-sensitive corrections are now covered by the companion behavior and Electron suites. |
| `ui/tests/unit/convert-page.behavior.test.ts` | 🟢 Strong | Mounts the real components and asserts archival POST content, exact Browse filters, negative visibility, dirty state, zero pre-Save PUTs, one post-Save PUT, and body content. |
| `ui/tests/e2e/convert-queue.test.ts` | 🟢 Strong | Real Electron receipt covers W8-1–W8-6; W8-3 now asserts the converter PUT lifecycle and dirty styling, while W8-2/W8-6 retain zero-POST negatives. |
| `ui/tests/e2e/launch.test.ts` | 🟢 Strong | Real Electron assertions retain the Wave 0 rail/home/hash/navigation contract. |
| `ui/tests/unit/e2e-wiring.test.ts` | 🟡 Adequate | Appropriate wiring census; behavioral responsibility remains in Playwright. |

### Checklist Results

#### Implementation Review (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | pass | Intact `C:/Temp/av-kit/e2e-wave8.txt` records 10 real-Electron passes in 1.2m; current corrected RTL suite passed 5/5. |
| IR-2 Stub behavioral compliance | pass | Electron seam tracks converter settings and PUT count; Browse/Add/list/delete behaviors remain stateful. |
| IR-3 Error mapping completeness | n/a | MEU-33 adds no REST route or server error mapping. |
| IR-4 Fix generalization | pass | F1–F4 are fixed at production and runtime-test layers; lazy route, RULE-3, G20, G23, census, and REST/MCP surfaces were rechecked. |
| IR-5 Test rigor | pass | No 🔴 test file remains in the corrected scope; runtime-sensitive ACs are no longer source-grep-only. |
| IR-6 Boundary validation coverage | partial | Corrected Browse and converter settings boundaries are exact/strict and runtime-tested; Round 1's non-blocking reorder-schema observation is unchanged and no concrete false-pass was demonstrated. |
| IR-7 Deferral and AC integrity | pass | All 24 AC IDs remain; AC-33.16/.17 now have runtime evidence. MEU-27 stays pending and Downloader→Convert remains the explicit Spec 08 deferral with no invented MEU. |

#### Adversarial Verification

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | pass | `PASS: RED_ORACLE ui MEU-33 AC-33 count=24`; current suite is Green. |
| AV-2 No bypass hacks | pass | Corrected tests exercise mounted components and captured calls; no forced early-return or assertion bypass was found. |
| AV-3 Changed paths asserted | pass | Hydration, filter delivery, visibility, dirty state, PUT count, and request bodies have explicit assertions. |
| AV-4 No skip/only masking | pass | Full Vitest ran with `--allowOnly=false`; AC-33.23/G36 remained Green. |
| AV-5 No unresolved placeholders | pass | Full UI gate and AC-33.23 remained Green; no new placeholder evidence surfaced. |
| AV-6 Source-backed criteria | pass | Corrections map directly to AC-33.4/.5/.7/.16/.17 and the cited Convert/GUI specifications. |

### Regression Spot-Checks

| Surface | Result | Evidence |
|---------|--------|----------|
| Lazy route | pass | `router.tsx:50` still uses `lazyRouteComponent`; no static `ConvertPage` import. |
| RULE-3 zero POST | pass | Intact Electron W8-2/W8-6 receipt; registry `convert:*` actions dispatch events only (`commandRegistry.ts:266-316`). |
| G20 portals | pass | `ConvertPage.tsx:327` uses `createPortal`; no converter `window.confirm`. |
| Wave 8 census | pass | Independent `PASS: E2E_CONTROL_CENSUS`; `06-gui.md:1138` remains cumulative 35. |
| G23 no converter debounce | pass | Settings `schedulePut` calls cover existing namespaces only; converter uses explicit Save. |
| REST/MCP scope lock | pass | OpenAPI check passed; `ROUTE_INDEX` assertion remains 61 (`tests/e2e/test_api_openapi.py:101`); `ACTION_INDEX` assertion remains 59 (`mcp-server/tests/action-index.test.ts:38`). |

### Commands Executed

All new command streams are isolated under `C:/Temp/av-kit/p8-cg-exec-r2-*`; exit status was captured before receipt reads.

| Command | Result |
|---------|--------|
| `npx vitest run tests/unit/convert-page.behavior.test.ts --allowOnly=false` | exit 0; 1 file, 5 tests passed |
| `npx tsc --noEmit` | exit 0 |
| `npx vitest run --allowOnly=false` | exit 0; 31 files, 195 tests passed |
| `npx eslint src/ tests/ --max-warnings 0` | exit 0 |
| `npm run build` | exit 0; lazy `ConvertPage-CouN-w59.js` emitted |
| `assert-red-oracle.ps1 -Kind ui -Meu 33 -Receipt ...txt -JsonReceipt ...json` | exit 0; 24 distinct AC-33 titles |
| `assert-e2e-control-census.ps1` | exit 0; PASS |
| Existing `C:/Temp/av-kit/e2e-wave8.txt` inspection | intact; 10 Playwright tests passed in 1.2m, including corrected W8-3 |
| `uv run python tools/export_openapi.py --check openapi.committed.json` | exit 0 |
| `uv run pytest tests/e2e/test_api_openapi.py -q` | exit 0; 63 passed; route assertion 61 |
| `npx vitest run tests/action-index.test.ts --allowOnly=false` | exit 0; 61 passed; action assertion 59 |

### Summary

All Round 1 findings are fixed and no blocking regression was found. The suites still emit non-blocking React `act(...)` warning noise, and the API test emits one dependency deprecation warning; both are test-output hygiene notes only and do not change the contract verdict.

### Follow-up Actions

No execution correction is required. The owning orchestrator may continue the existing H2 closeout rows for Session 15; this review does not authorize or start Session 8c / MEU-27.

### Residual Risk

This recheck trusted the intact post-correction 10-pass Electron receipt instead of launching Electron a second time, as allowed by the review brief. Independent current-state coverage came from the five correction RTL tests, the full 195-test UI suite, build/type/lint, and a fresh Wave 8 census.

### Verdict

`approved` — F1–F4 are fixed with current file-line and runtime evidence, no High/Critical finding remains, and the named scope locks are preserved. Product code, tests, plans, MEU handoffs, REST, and MCP were not modified by this review.
