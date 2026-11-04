---
date: "2026-09-29"
project: "2026-09-28-p11-capture-settings"
meu: "MEU-57"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md"
build_plan_section: "bp11 Capture page layout"
agent: "Claude Code (claude-opus-5-5)"
reviewer: "Fable 5.1 subagent (pending, H1-7)"
predecessor: "2026-09-28-p11-transcript-tts-MEU-56-handoff.md"
---

# Handoff: 2026-09-28-p11-capture-settings-MEU-57-handoff

> **Status**: `complete` · **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-57 — `gui-capture-layout`. The Capture page is now capped at `--layout-page-max-width` and arranged as:

- **Header row:** Capture region (primary md), which carries a `<kbd>` key cap only for a registered hotkey (CP2). It is followed by a muted "n shots · inbox {path}" line and a closed-by-default `Disclosure` (`capture-settings-toggle`). The disclosure holds the Inbox `PathRow`, the hotkey recorder, and "Save settings" (primary sm, existing dirty class).
- **Banner:** a warn line with a `Hotkey` `StatusChip` (CP3). It is always mounted with reserved height.
- **Filmstrip:** a 200 px column with 46 px rows. Each row has a 56×36 thumbnail, the `FILMSTRIP_LABEL_RULE` name, a time line, an sr-only full name, `aria-current` and a dirty dot (CP4).
- **Viewport toolbar:** an sm tool segment disabled without a shot (CP5); Undo/Redo; view variants; a labelled Color group; a labelled Stroke field. A right-hand action group owned by the page sits at the end of the second chrome row. The action group holds "Save overlay •", which is mounted only when dirty (CP1), plus Open file, Open folder and Delete.
- **Confirm strip:** one inline `capture-confirm-strip` above the surface replaces the portal. Its Cancel button gets focus when it opens, and `CONFIRM_EXCLUSIVITY` applies.
- **Status line:** `capture-status` stays the error channel under the surface. A separate `capture-shot-info` shows `name · W×H` (CP6).
- **Empty state:** `capture-empty` sits inside the viewport.

**Build Plan Section**: [Phase 11 Capture page layout](../../../docs/build-plan/11-page-layout.md#capture-page-layout) (CP1–CP6; §05 CP 1–24); [Session 26 plan](../../../docs/execution/plans/2026-09-28-p11-capture-settings/implementation-plan.md).

**Predecessor**: [Session 25 MEU-56 handoff](2026-09-28-p11-transcript-tts-MEU-56-handoff.md).

**Boundary inventory**: the IPC set is unchanged (`getHotkeyStatus` is still called once per hotkey value; its `registered` field is now read), as are `showDirectoryDialog`, `captureRegion`, `openPath` and `showItemInFolder`. HTTP calls are unchanged: `PUT /settings/capture` only through the explicit "Save settings", `POST …/annotate` only through Save overlay (with the `canSave` gate unchanged), and `DELETE` only after confirmation. The annotation reducer and the palette `capture:save` seam are unchanged. No API change: `git status -- packages/` is empty.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|---|---|---|---|---|---|
| AC-57.1 | integration | Capped page; header with Capture region then the closed Settings disclosure. Its panel holds the PathRow inbox/Browse, the hotkey recorder, and "Save settings" (sm, dirty class). The toggle issues no request; editing issues no PUT until Save, then exactly one. | Spec §Capture; CP3; OQ-3 | behavior `capture-page.behavior.test.ts:957`; Electron `capture-inbox.test.ts:675` | ✅ |
| AC-57.2 | integration | `capture-hotkey-keycap` renders inside `capture-region` only when `registered`. The accessible name still starts with "Capture region". There is one `getHotkeyStatus` call. | Spec CP2 | behavior `:989`, `:1002`; Electron `:675` (key cap consistent with live registration) | ✅ |
| AC-57.3 | integration | The banner is a warn line with a `Hotkey` chip and the byte-identical template when in use. It is always mounted with `min-h-4` and has no chip or text when free. | Spec §05 CP 11; R2-3 | behavior `:1002`, `:1014` | ✅ |
| AC-57.4 | integration | 200 px aside; `aria-label="Captures"`; native-button rows with `aria-current`, `FILMSTRIP_LABEL_RULE` name and time, the full name in `alt` and an sr-only span, and `data-dirty` on the dirty selected shot. There is no listbox role (APG). | Spec CP4; R2-4 | unit `capture-filmstrip-label.test.ts:12–32`; behavior `:1023`; Electron `:707` | ✅ |
| AC-57.5 | integration | The toolbar keeps `shrink-0`/`flex-nowrap`, has an sm tool segment disabled with a `title` hint when there is no shot, labelled Color/Stroke, and per-shot actions inside `capture-chrome` with their existing enablement. | Spec CP5; OQ-2; §05 CP 17–20; UX2 | behavior `:1044`, `:1064`, `:342` (AC-39.28 under TM-10), `:939` chrome classes; Electron `:727`; W9-5 | ✅ |
| AC-57.6 | integration | `capture-save` is mounted iff `CAPTURE_OVERLAY_DIRTY`, with `disabled = !canSave`. The label is "Save overlay •". One click sends one POST. The palette seam is unchanged. | Spec CP1 | behavior `:1078`, `:1095`, AC-60.10 `:668`/`:690` (palette refusal); Electron `:742` | ✅ |
| AC-57.7 | integration | An inline strip above the surface replaces the portal. Messages and IDs are unchanged, and the Delete confirm is labelled "Delete capture". Focus moves to Cancel, Cancel sends zero DELETE, and the filmstrip and Delete are disabled while the strip is open. | Spec §05 CP 23–24; APG alert dialog | behavior `:1107`, `:1123`; Electron `:742` (renderer fetch ledger) | ✅ |
| AC-57.8 | integration | `capture-status` sits under the surface, keeps `h-5` and its existing content rule. `capture-shot-info` is separate and never carries the error. | Spec CP6 | behavior `:1141`; Electron `:742` | ✅ |
| AC-57.9 | integration | `capture-empty`, with the same text, replaces the surface inside the viewport when there are no shots. It is absent when shots exist. | Spec §05 CP 13, CP 21 | behavior `:1154`, `:1165`; Electron `:727`; W9-3 | ✅ |
| AC-57.10 | integration | Real-Electron wave covering: header, key cap, disclosure and Save; filmstrip geometry and labels; the no-shot state; the Save-overlay mount rule; the confirm strips; shot info vs. status. Existing W9 / AC-59.12 / AC-60.12 cases stay green under TM-2/3/4/7. | E2; `create-plan.md` §4A | `capture-inbox.test.ts:675,707,727,742` + W9-1..W9-7, AC-59.12, AC-60.12 | ✅ |


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
| AC-58 (MEU-58) | Session 26 sibling MEU | See the sibling handoff for its own AC table | — |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

`validate-task.sh red57` produced `PASS RED vitest: 46 failing assertions cover ['AC-57']` and `PASS AC-57 E2E RED: 4 failing AC-57 specs`. The Vitest run is `s26-57-red-vitest.json`; the Electron run is `s26-57-red-e2e.json`, from a fresh build.

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|---|---|---|---|
| `capture-filmstrip-label.test.ts` (new module) | file-level `Cannot find module '…/capture-filmstrip-label'` (accepted only via `--new-file`) | 5 passed | `capture-filmstrip-label.test.ts:12–32` |
| AC-57.1 | `expected 'flex flex-col gap-4 p-4' to contain 'max-w-[var(--layout-page-max-width)]'` | pass | `capture-page.behavior.test.ts:957` |
| AC-57.2 | `Unable to find an element by: [data-testid="capture-hotkey-keycap"]` | pass | `:989` |
| AC-57.2/57.3 | `expected undefined to be 'Hotkey'` | pass | `:1002` |
| AC-57.4, 57.5, 57.6 ×2, 57.7 ×2, 57.8, 57.9 | `expected null to be 'true'` (the `CAPTURE_READY_SIGNAL` wait) / `expected false to be true` | pass | `:1023–1165` |
| AC-57.10 Electron ×4 | `stats.unexpected = 4`, each an `expect(` failure | pass | `capture-inbox.test.ts:675–742` |

`:1014` (a free hotkey keeps an empty, mounted banner) passed in Red by design: it pins today's `min-h-4` behavior, which R2-3 requires the recomposition to keep.

**Test migrations** (each is human-approved in [human-gate-decision.md](../../../docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md); census dispositions are in `walkthrough.md`):

- **TM-1** `layout-primitives.test.ts:218–230`: Capture moves to positive adoption (Disclosure, StatusChip, PathRow). Settings stays restricted until MEU-58.
- **TM-2** W9-3 `:217–218` and W9-5 `:322–323`: `capture-save` count 0. W9-3's force-click on Save was removed.
- **TM-3** W9-3: the four tools are `toBeDisabled` with no shot, replacing the no-force clicks.
- **TM-4** W9-3: a toggle click was added before the disclosure controls (setup only). `capture-picker.test.ts` needed nothing: its `toHaveValue` does not require visibility.
- **TM-5** `openSelectedSurface` (`:271`): waits on `data-overlay-ready="true"` with Save absent.
- **TM-6** `:466`, `:678`, `:697`: Save is absent on clean shots.
- **TM-7** `capture-inbox.test.ts:414`, `:459`, `:522`: `CAPTURE_READY_SIGNAL` plus Save count 0.
- **TM-8** `:441–447`.
- **TM-9** `:662–664`.
- **TM-10** `:349`: tool size `h-7`.
- **TM-11** AC-59.7 `:394–397`: draw one mark before injecting the seam selection.
- **TM-12** was **not applied**. AC-39.28 passed unchanged, because the page auto-selects the newest shot.

The conditional unit TM-4 toggle click was not needed either: `:320–327` and `:785` passed with the collapsed panel.

**Setup-only fixture change:** `catalogItems` in the behavior mock (`:149`, `:176`, `:233`) lets a test serve zero shots. No assertion changed.

### Commands Executed

| Command | Exit Code | Key Output |
|---|---|---|
| `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh red57` | 0 | `PASS RED vitest: 46 failing assertions cover ['AC-57']`; `PASS AC-57 E2E RED: 4 failing AC-57 specs` |
| `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh green57` | 0 | `PASS s26-57-green: 164 passed, env-bound tolerated: ['MEU-51 … AC-51.6']` |
| `bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate57` | 0 | typecheck, lint, vitest 164 passed, build; `PASS s26-57-e2e: 13 passed`; the 4 capture-picker specs are env-bound (the Windows stub `.exe` is absent) |
| `grep -nE 'TODO\|FIXME\|NotImplementedError\|transition-all\|bg-\[#' <4 capture sources>` | 1 | no hits (clean) |

```json
{"schema_version":"evidence.v1","check_id":"s26-57-red","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh red57","cwd":"/home/user/av-kit","scope":"MEU-57 unit (capture-page.behavior, capture-filmstrip-label) and Electron capture-inbox -g AC-57","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 1f9b035 + MEU-57 tests only (no production edit)","output":"PASS RED vitest: 46 failing assertions cover ['AC-57'] | PASS AC-57 E2E RED: 4 failing AC-57 specs","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s26-57-gate","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate57","cwd":"/home/user/av-kit","scope":"ui typecheck, ui lint, MEU-57 + REG57 Vitest, ui build, Electron capture-inbox + capture-picker","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 1f9b035 + MEU-57 working tree","output":"PASS s26-57-typecheck | PASS s26-57-lint | PASS s26-57-vitest: 164 passed, env-bound tolerated: AC-51.6 | PASS s26-57-build | PASS s26-57-e2e: 13 passed, env-bound tolerated: 4 capture-picker stub specs","fresh":true}
```

The authoritative fresh full gate is `WINDOWS_GATE` (H1-6). The container pre-gate evidence is recorded at H1-2.

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0 warnings (--max-warnings 0)
vitest (targeted MEU-57 + REG57): 164 passed; env-bound tolerated: AC-51.6 (CRLF-hash proof)
electron (capture-inbox + capture-picker): 13 passed; env-bound tolerated: 4 capture-picker (stub absent)
anti-placeholder / style audit: 0 matches
```

---

## Changed Files

| File | Action | Lines | Summary |
|---|---|---|---|
| `ui/src/renderer/src/features/capture/capture-filmstrip-label.ts` | new | 1–33 | `FILMSTRIP_LABEL_RULE` pure helper |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modified | 1–110 | Row anatomy, `aria-current`, `data-dirty`, `locked`, sr-only full name, 416 px scroll cap |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modified | props, toolbar, body | `hasSelection`/`overlayReady`/`actions`/`confirmStrip`/`emptyState`/`statusLine` slots; sm tool segment group; labelled Color group and Stroke field |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | imports, state, render | Header, key cap, Disclosure + PathRow, chip banner, inline confirm strip with focus, action slot, status/shot-info, empty slot; `createPortal` removed |
| `ui/tests/unit/capture-filmstrip-label.test.ts` | new | 1–38 | AC-57.4 unit |
| `ui/tests/unit/capture-page.behavior.test.ts` | modified | 149–233, 262–276, 349, 394–397, 441–447, 466, 662–698, 950–1170 | AC-57 behavior; TM-5/6/8/9/10/11; `catalogItems` seam |
| `ui/tests/unit/layout-primitives.test.ts` | modified | 218–230 | TM-1 (Capture half) |
| `ui/tests/e2e/capture-inbox.test.ts` | modified | 202–330, 410–530, 650–790 | TM-2/3/4/7; AC-57.10 wave; renderer fetch ledger |
| `ui/tests/e2e/test-ids.ts` | modified | tail | MEU-57 `NEW_TESTIDS` after the MEU-56 block |

```diff
-      {items.length === 0 ? (
-        <p data-testid="capture-empty" className="min-h-4">{EMPTY_STATE}</p>
-      ) : null}
+        <CaptureViewport
+          empty={items.length === 0}
+          hasSelection={selectedId !== null}
+          overlayReady={overlayReady && imageEpoch > 0}
+          actions={shotActions}
+          confirmStrip={confirmStrip}
+          emptyState={<p data-testid="capture-empty" …>{EMPTY_STATE}</p>}
```

```diff
-        <Button data-testid="capture-save" variant="primary" size="md" disabled={!canSave} …>Save</Button>
+      {dirty ? (
+        <Button data-testid="capture-save" variant="primary" size="sm" disabled={!canSave} …>Save overlay •</Button>
+      ) : null}
```

```diff
-  const confirmPortal = confirm !== null ? createPortal(<div style={{ position: 'fixed', … }}>…, document.body) : null
+  const confirmStrip = confirm !== null ? (<div data-testid="capture-confirm-strip" role="group" aria-labelledby="capture-confirm-message" …>…</div>) : null
```

---

## Codex Validation Report

_Left blank for reviewer agent._

---

## Corrections Applied (2026-09-29, pre-review)

A real-Electron screenshot check after the first gate found layout defects that the tests did not assert:

| # | Finding | Fix Applied | Verification |
|---|---|---|---|
| 1 | The per-shot actions sat at the end of the crowded first chrome row, off-screen behind a horizontal scroll, and the page gained a horizontal scrollbar because the viewport lacked `min-w-0`. | Actions moved to the right end of the second chrome row (`capture-chrome-marks`, still inside `capture-chrome`); viewport gets `min-w-0`. | Screenshot shows Open file / Open folder / Delete visible and no page-level scrollbar. `gate57` re-run: typecheck, lint, `vitest: 165 passed` (AC-51.6 env-bound; +1 from the new AC-58.5 PathRow case in the shared suite), build, `e2e: 13 passed` (4 picker specs env-bound). |
| 2 | The disclosure's Inbox label sat a full 168 px column away from its field. | The Capture `PathRow` gets a compact label column (`sm:grid-cols-[3.25rem_minmax(0,1fr)]!`). | Screenshot. |

```json
{"schema_version":"evidence.v1","check_id":"s26-57-gate-r2","command":"bash docs/execution/plans/2026-09-28-p11-capture-settings/validate-task.sh gate57","cwd":"/home/user/av-kit","scope":"ui typecheck, ui lint, MEU-57 + REG57 Vitest, ui build, Electron capture-inbox + capture-picker","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working tree committed as 4154da3","output":"PASS s26-57-typecheck | PASS s26-57-lint | PASS s26-57-vitest: 165 passed, env-bound tolerated: AC-51.6 | PASS s26-57-build | PASS s26-57-e2e: 13 passed, env-bound tolerated: 4 capture-picker stub specs","fresh":true}
```

---

## Deferred Items

None. `WINDOWS_GATE` (H1-6) runs the capture-picker specs on the Windows host, which has the stub `.exe`.

---

## Decision Log

```yaml
decision_log:
  - id: D-4
    stage: execution
    question: "Approve the two census-found test migrations TM-11 and TM-12?"
    resolution: human
    class: product-preference
    chosen: "Approve TM-11 + TM-12"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md — census follow-up TM-11/TM-12"]
    research: { engine: none, sources: [] }
    reasoning: "CP1 and CP5 made two pre-existing capture assertions unreachable; setup-only migrations keep every assertion, while editing the assertions would have weakened MEU-39/59 contracts."
  - id: D-5
    stage: execution
    question: "Fix the pre-existing pyright error at captures.py:78 inside this session?"
    resolution: human
    class: two-way
    chosen: "Fix it here (A8)"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-28-p11-capture-settings/human-gate-decision.md — A8 pyright follow-up"]
    research: { engine: none, sources: [] }
    reasoning: "The phase gate runs py-types with zero tolerance; a typing-only model_validate construction keeps the payload and OpenAPI identical, whereas deferring would leave the Phase 11 exit gate permanently red."
  - id: D-15
    stage: execution
    question: "Keep Save overlay, Open and Delete inside the viewport editor key scope after the confirm-strip fix?"
    resolution: autonomous
    class: two-way
    chosen: "Keep them in scope; exclude only the confirm strip"
    source_tag: Local Canon
    precedents: [".agent/context/handoffs/2026-09-28-p11-capture-settings-implementation-critical-review.md — Round 1 observation 5"]
    research: { engine: none, sources: [] }
    reasoning: "The pre-existing toolbar buttons already share that scope and the mockup places the actions in the viewport chrome; only the strip is modal-like under AC-57.7. Round 2 judged this acceptable."
```

---

## History

| Event | Date | Agent | Detail |
|---|---|---|---|
| Created | 2026-09-29 | Claude Code | Red → Green → targeted gate passed in the container |
