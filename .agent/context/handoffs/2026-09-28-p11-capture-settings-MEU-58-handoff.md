---
date: "2026-09-29"
project: "2026-09-28-p11-capture-settings"
meu: "MEU-58"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
build_plan_section: "bp11 Settings page layout"
agent: "Claude Code (claude-opus-5-5)"
reviewer: "Fable 5.1 subagent (pending, H1-7)"
predecessor: "2026-09-28-p11-capture-settings-MEU-57-handoff.md"
---

# Handoff: 2026-09-28-p11-capture-settings-MEU-58-handoff

> **Status**: `complete` · **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-58 — `gui-settings-layout`. The Settings page is now a `max-w-[60rem]` grid with a `SettingsRail` beside the content column (`11rem | minmax(0,1fr)` at ≥ 1000 px; below that the rail becomes a horizontal row above the content).

- **Rail:** sticky, with Pages / App / Setup groups and `aria-current="location"`. An IntersectionObserver rooted at the AppShell `<main>` sets the current entry, with a no-observer fallback and a click lock. Attention dots mark Convert/Capture drafts and readiness < 4.
- **Sections:** all 11 `SETTINGS_SECTION_SET` sections keep their IDs and gain `data-settings-section` anchors. Each has a header rule and a `settings-mode-{key}` caption from `SAVE_MODE_CAPTIONS`.
- **Form grid:** 168 px label column. PathRows (read-only where they were read-only) sit on one line with Browse. Native G30 selects (160 px) go through `FormRow`, with one label each. Numbers are 84 px with sourced hints only. Cookie mode is a native-radio `SegmentedControl` with indented sub-fields. Checkbox explanations come only from `CHECKBOX_COPY_SOURCES`.
- **Footers:** the explicit-save footers keep their label/class and are dimmed when clean. Apply defaults is ghost sm. Log to file is one row with a fixed-path hint. The theme control is a two-button `aria-pressed` segment.
- **Diagnostics:** chip lists. Readiness has "n of 4 ready" only after both sources load, with "checking" before load. The MCP token chip keeps the yes/no text.

**Build Plan Section**: [Phase 11 Settings page layout](../../../docs/build-plan/11-page-layout.md#settings-page-layout) (ST1–ST7; §05 ST 1–35); [Session 26 plan](../../../docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md).

**Predecessor**: [MEU-57 handoff](2026-09-28-p11-capture-settings-MEU-57-handoff.md).

**Boundary inventory**: persistence is unchanged.
- **Autosave** still goes through `schedulePut` (300 ms debounce, strict schemas) for downloader, transcript, tts and app. Browse still uses `putNow`.
- **Convert/Capture** still use their explicit-save drafts.
- **Theme** still uses `putNow('ui')`.
- **Startup** still uses `loginItemGet`/`loginItemSet`. The rail learns availability through the new `onAvailabilityChange` prop, with no extra IPC call.
- **Diagnostics/MCP** actions are unchanged.

There is no API change, no new min/max/step, and no unified save model.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-58.1 | integration | A 960 px two-column grid: rail then content (h1, HelpCard, error, all sections). `max-w-3xl` is removed. A narrow window turns the rail into a row above the content. | Spec §Settings; mockup §04 | `settings-rail.test.tsx:191`; `settings-page.test.ts:487`; Electron `settings.test.ts:275` | ✅ |
| AC-58.2 | integration | `settings-rail` nav with three groups. `settings-rail-{key}` entries follow `SETTINGS_SECTION_SET` order. Activation (click or Enter) focuses and reveals the section with no write. The startup entry appears only when the panel is mounted. | Spec ST3; mockup §02/§04 | `settings-rail.test.tsx:140,205,218,230`; Electron `:221` | ✅ |
| AC-58.3 | integration | An IntersectionObserver (root = nearest scroller) sets exactly one current entry and disconnects on unmount. The jsdom fallback works without the API. | Spec ST3 | `settings-rail.test.tsx:230,257`; Electron `:221` (scrolling `<main>` to top moves current to Download) | ✅ |
| AC-58.4 | integration | `settings-mode-{key}` captions match `SAVE_MODE_CAPTIONS`; none for Dependencies/MCP. A Convert edit sends zero PUTs until Save, then one. Theme sends one immediate PUT. | Spec ST2 | `settings-rail.test.tsx:156,289`; Electron `:250` | ✅ |
| AC-58.5 | integration | One accessible label per leaf. Path field and Browse share a row. Read-only paths stay read-only through the additive `PathRow readOnly`. Numbers are 84 px with hints only from `NUMBER_HINT_SOURCES` and no new min/max. Speed keeps 0.5/2/0.1. | Spec ST4; MEU-51 PathRow | `settings-rail.test.tsx:165,315`; `layout-primitives.test.ts:171`; Electron `:250` (y-overlap) | ✅ |
| AC-58.6 | integration | Cookie mode is a native-radio `SegmentedControl` with the existing IDs. A label click sends exactly one PUT, `{cookie_mode}`. Sub-field visibility is unchanged. | Spec ST1; G30 | `settings-rail.test.tsx:351` | ✅ |
| AC-58.7 | integration | Explanations appear only for `CHECKBOX_COPY_SOURCES` (via `aria-describedby`). `audio_format` stays enabled with `audio_only` off. | Spec ST5, ST6 | `settings-rail.test.tsx:165,370` | ✅ |
| AC-58.8 | integration | The explicit-save footers (sm) keep "Save Changes •" / `btn-save-dirty` and are dimmed when clean. Rail dots follow each draft and clear after Save. | Spec ST2; mockup §04 | `settings-rail.test.tsx:384`; Electron `:250`; AC-33.16/AC-39.15 unchanged | ✅ |
| AC-58.9 | integration | Dependency, readiness and MCP chip lists. Before load: no count, no dot, "checking". After load: "n of 4 ready", a dot iff n < 4, and Fix only on failing rows. Versions and paths are shown. The token text stays yes/no and is never the token value. | Spec ST7 | `settings-rail.test.tsx:182,404,415,438`; Electron `:275`; AC-23.11/23.12 unchanged | ✅ |
| AC-58.10 | integration | The MEU-61 panel and child IDs, visibility and IPC are unchanged. All AC-61.* tests pass unedited. | Spec §Settings; grouping | `settings-page.test.ts` MEU-61 suite; Electron AC-61.17 | ✅ |
| AC-58.11 | unit | `SETTINGS_SOURCE_LOCATION`: no subfolder, and the Convert/Capture strings stay in `SettingsPage.tsx`. `NEW_TESTIDS` come after the MEU-57 block; the AC-51.6 prefix hash is unchanged. | Local Canon | `settings-page.test.ts:497`; AC-51.6 (CRLF proof) | ✅ |
| AC-58.12 | integration | Real-Electron wave covering: rail groups; click → in viewport with current entry; scroll-driven current; captions; Browse geometry; Convert dirty dot and Save; readiness count; narrow rail row. W4-1..W4-3 and AC-61.17 unchanged. | E2 | `settings.test.ts:221,250,275` + W4-1..W4-3, AC-61.17 | ✅ |
| AC-58.13 | integration | Apply defaults: ghost sm footer, one POST. Log to file on one row with path, Copy and the fixed-path hint. The theme segment uses `aria-pressed`. | Spec §05 ST 14, 29, 31 | `settings-rail.test.tsx:449`; AC-23.3/23.8/23.9 unchanged | ✅ |


### Referenced existing contracts (not owned by this MEU)

The plan cites these earlier contracts as regression boundaries. This MEU does not own them. Their status on the final container pre-gate (`p11cs-pregate-r4.txt`) is listed; `WINDOWS_GATE` is authoritative.

| Contract | Owner | How this session touches it | Status |
|---|---|---|---|
| AC-23.3, AC-23.8, AC-23.9, AC-23.11, AC-23.12, AC-23.19 | MEU-23 (Settings page) | Same IDs, actions and source strings after the MEU-58 recomposition | ✅ green, unedited |
| AC-32.8, AC-38.8 | MEU-32 / MEU-38 (MCP dist registration) | None; these failed only while MCP tests ran before the MCP build (amendment A9) | ✅ green (215/215 after build-first order) |
| AC-33.16, AC-39.15 | MEU-33 / MEU-39 (explicit-save source pins) | Literal leaf IDs kept in `SettingsPage.tsx` | ✅ green, unedited |
| AC-39.28 | MEU-39 | TM-10 (tool size `h-7`); TM-12 not needed | ✅ green |
| AC-41.3 | MEU-41 (queue canon) | None | ⚠️ env-bound in the container (`P:/zorivest` absent, `styles.css` unchanged since `f7d3134`); authoritative on Windows |
| AC-49.25, AC-49.26, AC-49.27, AC-49.28 | MEU-49 (queue drag and drop E2E) | Test-helper timing only under the human-approved A12, A13 and A16; no assertion, test name or product file changed | ✅ green on `WINDOWS_GATE` attempt 7 (`cb864f3`) |
| AC-50.4 | MEU-50 (canon inventory) | The canon "9 section ids" label is left verbatim | ✅ green |
| AC-51.6, AC-51.7 | MEU-51 (primitives) | New IDs after the MEU-56 block; TM-1 moves Capture and Settings to positive adoption | ✅ AC-51.7; ⚠️ AC-51.6 env-bound (CRLF-hash proof) |
| AC-59.7, AC-59.8, AC-59.12, AC-60.8, AC-60.10, AC-60.12 | MEU-59 / MEU-60 (annotation edit) | TM-5 to TM-9 and TM-11 (Save mounts only when dirty, CP1) | ✅ green |
| AC-61.12 to AC-61.21 (AC-61.*) | MEU-61 (Startup) | `onAvailabilityChange` prop and section header only | ✅ green, unedited |
| AC-57 (MEU-57) | Session 26 sibling MEU | See the sibling handoff for its own AC table | — |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

`validate-task.sh red58` produced `PASS RED vitest: 5 failing assertions cover ['AC-58']` and `PASS AC-58 E2E RED: 3 failing AC-58 specs` (fresh build).

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|---|---|---|---|
| `settings-rail.test.tsx` (new module) | file-level `Failed to resolve import "…/settings/settings-sections"` (accepted only via `--new-file`) | 18 passed | `settings-rail.test.tsx:140–449` |
| AC-58.1 | `expected 'flex flex-col gap-4 p-4 max-w-3xl' to contain 'max-w-[60rem]'` | pass | `settings-page.test.ts:487` |
| AC-58.11 | `expected false to be true` (`SettingsRail.tsx` absent) | pass | `settings-page.test.ts:497` |
| AC-58.5 PathRow | `expected false to be true` (`readOnly`) | pass | `layout-primitives.test.ts:171` |
| TM-1 (AC-51.7, Settings half) | `SettingsPage adopts SegmentedControl: expected … to contain 'components/ui/SegmentedControl'` | pass | `layout-primitives.test.ts:237–242` |
| AC-58.12 Electron ×3 | `stats.unexpected = 3`, each an `expect(` failure | pass | `settings.test.ts:221,250,275` |

**Setup-only repairs after Red** (no assertion changed):
- **`settings-rail.test.tsx:358–361` (AC-58.6):** waits (`vi.waitFor`) for the downloader query before reading `settings-leaf-cookie_browser`. The first Green run read it before the query resolved.
- **`settings.test.ts` seam:** adds converter and capture GET responses, so the explicit-save drafts are real in Electron. It is additive; the existing W4 flows are unaffected.

**Production fixes found in Green:**
- **Literal leaf IDs.** AC-33.16 and AC-39.15 pin the leaf ID strings in `SettingsPage.tsx`, so the checkbox and number row helpers now take literal `testId` props instead of building `settings-leaf-${leaf}`.
- **Scroll reliability**, found by a real-Electron screenshot check. A focus call after a smooth `scrollIntoView` cancelled the scroll, and headless or throttled Chromium can drop smooth scrolling (probe: smooth 0 px vs auto 1809 px). `revealSection` now focuses first, scrolls smoothly (instantly under reduced motion), and completes an unmoved scroller with an instant scroll after 450 ms. The readiness Fix links use the same helper. After the fix, the probe shows the "Console & logging" click scrolled `<main>` to 1809 px with the entry current.

### Commands Executed

| Command | Exit Code | Key Output |
|---|---|---|
| `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh red58` | 0 | `PASS RED vitest: 5 failing assertions cover ['AC-58']`; `PASS AC-58 E2E RED: 3 failing AC-58 specs` |
| `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh green58` | 0 | `PASS s26-58-green: 176 passed, env-bound tolerated: ['MEU-51 … AC-51.6']` |
| `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate58` (after the scroll/overflow fixes) | 0 | typecheck, lint, `vitest: 176 passed` (AC-51.6 env-bound), build, harness build, `PASS s26-58-e2e: 43 passed, env-bound tolerated: []` |

```json
{"schema_version":"evidence.v1","check_id":"s26-58-red","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh red58","cwd":"/home/user/av-kit","scope":"MEU-58 unit (settings-page, settings-rail, layout-primitives) and Electron settings -g AC-58","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 3b3de3e + MEU-58 tests only (no production edit)","output":"PASS RED vitest: 5 failing assertions cover ['AC-58'] | PASS AC-58 E2E RED: 3 failing AC-58 specs","fresh":true}
```

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0 warnings (--max-warnings 0)
vitest (targeted MEU-58 + REG58): 176 passed; env-bound tolerated: AC-51.6 (CRLF-hash proof)
electron (settings, convert-queue, capture-inbox, help-search): 43 passed; env-bound: none
anti-placeholder / style audit: run in the H1-2 pre-gate over AUDIT_SRC
```

```json
{"schema_version":"evidence.v1","check_id":"s26-58-gate","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate58","cwd":"/home/user/av-kit","scope":"ui typecheck, ui lint, MEU-58 + REG58 Vitest, ui build, harness build, Electron settings/convert-queue/capture-inbox/help-search","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 3b3de3e + MEU-58 working tree (committed as 4154da3)","output":"PASS s26-58-typecheck | PASS s26-58-lint | PASS s26-58-vitest: 176 passed, env-bound tolerated: AC-51.6 | PASS s26-58-build | PASS s26-58-harness-build | PASS s26-58-e2e: 43 passed, env-bound tolerated: []","fresh":true}
```

---

## Changed Files

| File | Action | Lines | Summary |
|---|---|---|---|
| `ui/src/renderer/src/features/settings/settings-sections.ts` | new | all | `SETTINGS_SECTION_SET`, `RAIL_GROUPS`, `SAVE_MODE_CAPTIONS`, `CHECKBOX_COPY_SOURCES`, `NUMBER_HINT_SOURCES`, `readinessCount` |
| `ui/src/renderer/src/features/settings/SettingsRail.tsx` | new | all | Rail, observer/fallback, click lock, bottom rule, `revealSection` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | imports, helpers, render | Grid, section frame, FormRow/PathRow/GridSelect rows, segment, footers, chip lists, dots; handlers unchanged |
| `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | modified | props, header | `onAvailabilityChange`, section anchor, caption |
| `ui/src/renderer/src/components/ui/PathRow.tsx` | modified | props, input | Additive `readOnly` |
| `ui/tests/unit/settings-rail.test.tsx` | new | all | AC-58.1–58.9, 58.13 |
| `ui/tests/unit/settings-page.test.ts` | modified | 487–513 | AC-58.1, AC-58.11 |
| `ui/tests/unit/layout-primitives.test.ts` | modified | 171–186, 237–242 | AC-58.5 PathRow; TM-1 (Settings half) |
| `ui/tests/e2e/settings.test.ts` | modified | 79–85, 216–293 | AC-58.12 wave; additive seam GETs |
| `ui/tests/e2e/test-ids.ts` | modified | tail | MEU-58 `NEW_TESTIDS` (+ `settings-log-row`) |

```diff
-    <div data-testid="settings-page" className="flex flex-col gap-4 p-4 max-w-3xl">
+    <div ref={pageRef} data-testid="settings-page"
+      className="grid w-full max-w-[60rem] items-start gap-5 p-4 min-[1000px]:grid-cols-[11rem_minmax(0,1fr)]">
+      <SettingsRail sections={sections} rootRef={pageRef} dots={dots} />
```

```diff
-        <fieldset data-testid="settings-leaf-cookie_mode" …>{radios}</fieldset>
+            <SegmentedControl name="cookie_mode" testId="settings-leaf-cookie_mode" value={cookieMode}
+              options={…testId: `settings-leaf-cookie_mode-${mode}`…} onValueChange={(mode) => schedulePut('downloader', { cookie_mode: mode })} />
```

---

## Codex Validation Report

_Left blank for reviewer agent._

---

## Deferred Items

None. Observation for triage, not a deferral: the pre-existing readiness Fix links keep their visibility rules as-is under ST7. The FFmpeg Fix link still renders before dependencies load (`!ffmpegAvailable`), while its chip correctly shows "checking". This is out of scope per the plan's Out of Scope table.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Created | 2026-09-29 | Claude Code | Red → Green → targeted gate in the container |
