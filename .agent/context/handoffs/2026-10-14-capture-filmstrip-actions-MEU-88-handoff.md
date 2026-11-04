---
date: "2026-10-16"
project: "capture-filmstrip-actions"
meu: "MEU-88"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-capture-filmstrip-actions/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-vscode (Claude Opus 5.5)"
reviewer: "Codex via local dispatch (human-review-decision.md)"
predecessor: "none"
---

# Handoff: 2026-10-14-capture-filmstrip-actions-MEU-88-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-88 — `gui-capture-filmstrip-menu`.
- A right-click, the ContextMenu key or Shift+F10 on a filmstrip thumb opens a "Shot actions" menu (`MENU_PATTERN`, WAI-ARIA APG menu) rendered fixed in a portal. It holds **Copy full path**, **Copy image** and **Delete**. The menu targets the thumb it was opened on and never changes the editor's selection (`MENU_TARGET`). It does not open while a confirm strip is open, and a confirm that opens closes it (`MENU_LOCK`).
- Copy full path writes the target's `original_path` through the existing `writeClipboardText`.
- Copy image fetches the target's `variant=original` image. PNG bytes pass through and any other format is re-encoded to PNG in the renderer (`RENDERER_PNG`). The bytes go to a new IPC channel `write-clipboard-image` (`IMAGE_CHANNEL`), whose main handler decodes them with `nativeImage.createFromBuffer` and calls `clipboard.writeImage` (`MAIN_IMAGE_WRITE`).
- Delete reuses the existing confirm strip. For a non-selected target, the strip names the shot and the editor keeps its shot, marks and dirty state (`DELETE_TARGETS`, `DELETE_CONFIRM_TEXT`, `SINGLE_DELETE`).
- `TEST_AMENDMENTS` TA-1 (`ipc-strict-census`), TA-2 (`login-item-ipc`) and TA-3 (`ipc-channels`) are applied as planned.

**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Filmstrip context menu (09:777-785)
**Predecessor**: none (first MEU of Session 38). MEU-89 (rows 6–8) builds on this MEU's menu and `DELETE_TARGETS`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-88.1 | integration | Right-click on a non-selected thumb opens the menu with the three items in order, the first focused, at the pointer; `aria-current` stays put. No menu while a confirm is open; opening a confirm closes the menu | Spec 09:781; D-8, D-12 | `ui/tests/unit/capture-filmstrip-actions.behavior.test.ts:278`, `:300` | ✅ |
| AC-88.2 | integration | ContextMenu and Shift+F10 open the menu at the thumb's rect; arrows wrap, Home/End jump, Escape returns focus, Tab and an outside pointer-down close. F10 alone and a letter open nothing; a second open signal leaves one menu | Spec 09:785; APG Menu; D-9 | `capture-filmstrip-actions.behavior.test.ts:313`, `:356` | ✅ |
| AC-88.3 | integration | Copy full path writes that shot's `original_path` once and shows `Copied the path of {name}.`; a rejection shows `Could not copy {name}: {message}` | Spec 09:781-782 | `capture-filmstrip-actions.behavior.test.ts:368`, `:381` | ✅ |
| AC-88.4 | unit | `toClipboardPng` passes PNG through without `encode`, sends other blobs to `encode`; null throws the fetch error, a non-PNG `encode` result throws the encode error | D-11 | `ui/tests/unit/capture-clipboard.test.ts:15`, `:22`, `:32`, `:39` | ✅ |
| AC-88.5 | integration | Copy image fetches the percent-encoded `variant=original` URL and sends a PNG-signed `Uint8Array` once; a 404 reports the load failure; no `writeClipboardImage` reports unavailability and fetches nothing for the target | Spec 09:781-782; D-10; RULE-2 | `capture-filmstrip-actions.behavior.test.ts:394`, `:412`, `:423` (oracle corrected, D-20) | ✅ |
| AC-88.6 | unit | `handleIpc('write-clipboard-image')` calls the dependency once, counts one clipboard effect, returns ok; malformed, oversized, unsigned and extra-key payloads are refused without a call | Spec 09:782; G27 | `ui/tests/unit/clipboard-image-main.test.ts:23`, `:53` | ✅ |
| AC-88.7 | unit | `writePngToClipboard` decodes exactly the given bytes and writes once; an empty decode returns false with no write | Spec 09:782, :785 | `clipboard-image-main.test.ts:66`, `:87` | ✅ |
| AC-88.8 | unit | Channel registered (20-entry census), `writeClipboardImage` in `API_KEYS`, preload invokes `'write-clipboard-image', { png }` | `PRELOAD_KEY`; G27 | `clipboard-image-main.test.ts:99`; TA-1/TA-2/TA-3 suites | ✅ |
| AC-88.9 | integration | Menu Delete on the selected shot reuses the confirm and its text; accept sends one DELETE and the selection falls to the newest; Cancel sends none and the toolbar Delete still targets the selected shot | Spec 09:781, :151-153 | `capture-filmstrip-actions.behavior.test.ts:434`, `:451` | ✅ |
| AC-88.10 | integration | Menu Delete on a non-selected shot names it; accept deletes only it; the editor keeps its shot, marks and dirty state with no discard confirm | D-12, D-14 | `capture-filmstrip-actions.behavior.test.ts:466` | ✅ |
| AC-88.11 | unit | `ACTION_ROWS` resolve: IPC cells to registered channels the preload names, REST cells to the OpenAPI capture path, new test ids to `test-ids.ts` and production source | 09:783; AC-23.20 | `ui/tests/unit/gui-actions-audit.test.ts:268`, `:294` | ✅ |
| AC-88.12 | integration (Electron) | Built app: (a) path reaches `clipboard.readText()`; (b) PNG and WebP shots reach `clipboard.readImage()` with the shot's size and `SHOT_PIXELS`; (c) Shift+F10 and ContextMenu via `locator.press`; (d) non-selected Delete removes only that id; (e) no menu during a confirm; (f) a transparent primer is rejected first | Spec 09:781-785; E2; S3 | `ui/tests/e2e/capture-filmstrip-actions.test.ts:246`, `:273`, `:290` | ✅ |

### Other plan AC references (not owned by MEU-88)

| AC | Owner | Status in MEU-88 |
|----|-------|------------------|
| AC-89.x | [MEU-89 handoff](2026-10-14-capture-filmstrip-actions-MEU-89-handoff.md) | delivered in rows 6–8 and the D-25 rework; pass in the gate of record (`walkthrough.md` §Gate re-run after F1, Vitest 857/857) |
| AC-41.3 (`queue-canon`, `BASELINE_RED`) | existing suite | the tolerance went unused: passes in the gate of record (`walkthrough.md` §Gate re-run after F1, Vitest 857/857) |
| AC-59.20, AC-60.15, AC-66.16, AC-67.25 (help) | existing suite; `HELP_SENTENCE` is MEU-89's (AC-89.8) | pass unchanged |
| AC-61.19 (login-item IPC census) | existing suite | TA-2 applied; passes |
| Capture regression set (`capture-page.behavior`, `capture-page`, `capture-inbox` E2E) | existing suites | pass unchanged in `gate88` |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| Vitest AC-88.1–88.3, 88.5, 88.9–88.11 | 13 assertion failures (no menu, no `writeClipboardImage` in preload, no named confirm text) | pass | `capture-filmstrip-actions.behavior.test.ts`, `gui-actions-audit.test.ts:268` |
| Vitest AC-88.4, 88.6–88.8 | load-tolerated (module absent at Red: `capture-clipboard.ts`, `clipboard-image.ts`) | pass | `capture-clipboard.test.ts`, `clipboard-image-main.test.ts` |
| TA-2 AC-61.19 | `listRegisteredChannels length` 19 ≠ 20 | pass | `login-item-ipc.test.ts:50-51` |
| Electron AC-88.12 (×3) | failing (`PASS MEU-88 E2E RED: ['AC-88.12']`) | pass, and 30/30 at `--repeat-each=10` | `capture-filmstrip-actions.test.ts:246,273,290` |

TA-1 was already green at Red (its unregistered-channel payloads return `ok:false` either way); see [walkthrough.md](../../../docs/execution/plans/2026-10-14-capture-filmstrip-actions/walkthrough.md) §MEU-88 Red.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s38-88-red","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check red88 *> C:/Temp/av-kit/s38-run-red88.txt","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"MEU-88 Vitest and Electron -g AC-88 before any product edit","phase":"targeted","exit_code":0,"result":"pass","tested_state":"baseline 90f041e + row 2 tests and TA-1/TA-2/TA-3; no product source changed","output":"PASS MEU-88 Vitest RED: 13 assertion failures, 0 missing-symbol | PASS ui-build | PASS MEU-88 E2E RED: ['AC-88.12'] | PASS red88","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s38-88-green-main","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check green88-main *> C:/Temp/av-kit/s38-run-green88-main.txt","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"clipboard-image-main, ipc-strict-census, login-item-ipc","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main half: ipc.ts, clipboard-image.ts, index.ts, preload.ts, env.d.ts","output":"PASS green88-main-vitest: 19 passed of 19 | PASS green88-main","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s38-88-green","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check green88 *> C:/Temp/av-kit/s38-run-green88.txt","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"MEU-88 Vitest, ui build, Electron -g AC-88","phase":"targeted","exit_code":0,"result":"pass","tested_state":"renderer half added: capture-clipboard.ts, CaptureFilmstripMenu.tsx, CaptureFilmstrip.tsx, CapturePage.tsx; AC-88.5 oracle corrected (D-20)","output":"PASS green88-vitest: 41 passed of 41 | PASS ui-build | PASS green88-e2e: expected 3 skipped 0 | PASS green88","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s38-88-gate","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check gate88 *> C:/Temp/av-kit/s38-run-gate88.txt","cwd":"P:/av-kit-wt/s38-capture-filmstrip-actions","scope":"ui typecheck, lint, MEU-88 unit set plus capture/IPC regression set, ui build, Electron capture-filmstrip-actions + capture-inbox, --repeat-each=10 on AC-88","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-88 final working tree (baseline 90f041e + MEU-88 diff, unused SHOT_C fixture removed, E2E clipboard read settled per D-21)","output":"PASS ui-types | PASS ui-lint | PASS gate88-vitest: 257 passed of 257 | PASS ui-build | PASS gate88-e2e: expected 31 skipped 0 | PASS gate88-repeat: expected 30 skipped 0 | PASS gate88","fresh":true}
```

Two earlier `gate88` runs failed and were fixed before the gate of record:
1. `ui-lint` exit 1: `capture-filmstrip-actions.behavior.test.ts:67 'SHOT_C' is assigned a value but never used`. The fixture had no reader in any MEU-88 test, so it was removed (no assertion touched).
2. `gate88-repeat`: one flaky repeat (8 of 10) of AC-88.12 (a)(b)(f) — `b.webp: expect(probe.empty).toBe(false)` received `true` right after the status read "Copied b.webp as an image." On this host Windows clipboard history is on (`HKCU\Software\Microsoft\Clipboard EnableClipboardHistory = 1`) and ShareX is running; both open the clipboard after every write, and a `readImage()` that loses that race comes back empty. A failed product write would have left the non-empty transparent primer, so the empty read was the probe, not the product. The probe now polls until the read is non-empty and then makes the same assertions (D-21). A 30× stress run of that test passed 30/30 before the gate re-run.

### Quality Gate Results

```
ui typecheck: 0 errors
ui lint: 0
Vitest MEU-88 unit set + capture/IPC regression set: 257/257
ui build: pass
Electron capture-filmstrip-actions + capture-inbox: 31 passed
repeat-each=10 (-g AC-88): 30 expected, 0 unexpected, 0 flaky
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/main/ipc.ts` | modified | +27 | `IMAGE_CHANNEL` in `RENDERER_TO_MAIN_CHANNELS`; `IMAGE_PAYLOAD` schema (Uint8Array, 1 B–64 MiB, PNG signature, strict); `IMAGE_HANDLER` |
| `ui/src/main/clipboard-image.ts` | new | 1–17 | `writePngToClipboard` (`MAIN_IMAGE_WRITE`) |
| `ui/src/main/index.ts` | modified | +3/−1 | `nativeImage` import; `writeClipboardImage` dependency |
| `ui/src/main/preload.ts` | modified | +2 | `writeClipboardImage` key and invoke |
| `ui/src/renderer/src/env.d.ts` | modified | +1 | optional `writeClipboardImage` |
| `ui/src/renderer/src/features/capture/capture-clipboard.ts` | new | 1–85 | `toClipboardPng`, `encodePng`, `loadClipboardPng`, `copyErrorMessage` |
| `ui/src/renderer/src/features/capture/CaptureFilmstripMenu.tsx` | new | 1–149 | `MENU_PATTERN` portal menu |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modified | +127/−2 | `FilmstripShotActions`; `MENU_OPEN`, `MENU_ANCHOR`, `MENU_TARGET`, `MENU_LOCK` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modified | +71/−2 | `deleteTargets`; `reportCopy`; `filmstripActions`; `deleteConfirmText`; targeted `acceptConfirm` delete |
| `ui/tests/unit/capture-filmstrip-actions.behavior.test.ts` | new | — | AC-88.1–88.3, 88.5, 88.9, 88.10 |
| `ui/tests/unit/capture-clipboard.test.ts` | new | — | AC-88.4 |
| `ui/tests/unit/clipboard-image-main.test.ts` | new | — | AC-88.6–88.8 |
| `ui/tests/unit/gui-actions-audit.test.ts` | modified | +62 | AC-88.11 |
| `ui/tests/e2e/capture-filmstrip-actions.test.ts` | new | — | AC-88.12 |
| `ui/tests/e2e/test-ids.ts` | modified | +6 | MEU-88 `NEW_TESTIDS` |
| `ui/tests/unit/ipc-strict-census.test.ts`, `login-item-ipc.test.ts`, `ipc-channels.ts` | modified | TA-1/TA-2/TA-3 only | channel count 19 → 20 and the new channel's census rows |

```diff
   'login-item-set',
+  'write-clipboard-image',
 ] as const
...
+    case 'write-clipboard-image': {
+      const png = (parsed.data as { png: Uint8Array }).png
+      effects.clipboard += 1
+      const written = (await deps.writeClipboardImage?.(png)) ?? false
+      if (!written) {
+        return { ok: false, error: IMAGE_DECODE_ERROR }
+      }
+      return { ok: true, value: undefined }
+    }
```

```diff
-    if (kind === 'delete' && selectedId !== null) {
-      const id = selectedId
+    if (kind === 'delete' && targets.length === 1) {
+      // SINGLE_DELETE: only deleting the editor's own shot clears the selection.
+      const id = targets[0] as string
+      const wasSelected = id === selectedId
       void run(async () => {
         await deleteCapture(id)
-        setSelectedId(null)
+        if (wasSelected) {
+          setSelectedId(null)
+        }
       })
     }
```

Not in the plan but recorded here: `copyErrorMessage` (`capture-clipboard.ts:82`) strips Electron's `Error invoking remote method '<channel>': Error: ` prefix, so a main-side decode failure reads `Could not copy b.png: image could not be decoded` (D-22). `blobBytes` (`capture-clipboard.ts:15`) reads bytes via `Blob.arrayBuffer()` with a `FileReader` fallback, because jsdom's `Blob` has no `arrayBuffer`; Chromium takes the first branch.

### Residual risk

- `clipboard.writeImage` returns nothing, so a main-process write that loses the same OS clipboard race described above would fail silently while the status says "Copied". Electron offers no signal to check; the risk is bounded to a retry by the user.

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Deferred Items

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-20
    stage: execution
    question: "The Red oracle for 'AC-88.5 without writeClipboardImage … fetches nothing' rejects any variant=original request, but the viewport already fetches the selected shot's original. Narrow it?"
    resolution: human
    class: two-way
    chosen: "Assert no request for the menu target's original (/captures/shot-b/image?variant=original); the rest of the test is unchanged"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-10-14-capture-filmstrip-actions/walkthrough.md §MEU-88 Green, renderer half — the test correction"]
    research: { engine: none, sources: [] }
    reasoning: "The original oracle conflicted with existing viewport behavior and could never pass; the AC's intent is that Copy image does not fetch its target when it cannot copy. Approved under Mat's standing session auto-approval (USER_EXPLICIT 2026-10-16)."
  - id: D-21
    stage: execution
    question: "AC-88.12 (a)(b)(f) flaked once in 10 repeats because a clipboard image read lost the race with OS clipboard listeners. Settle the probe or change product code?"
    resolution: human
    class: two-way
    chosen: "Poll the main-process readImage() until it is non-empty, then make the unchanged size and SHOT_PIXELS assertions on that probe (primer and copy reads)"
    source_tag: Human-approved
    precedents: ["ui/tests/e2e/capture-filmstrip-actions.test.ts — the Copy full path check already uses expect.poll on clipboard.readText()"]
    research: { engine: none, sources: [] }
    reasoning: "The failed read was empty, while a failed product write would have left the non-empty primer, so the flake is in the probe. Clipboard history and ShareX are active on this host. Approved under the standing session auto-approval (USER_EXPLICIT 2026-10-16)."
  - id: D-22
    stage: execution
    question: "A rejected writeClipboardImage invoke carries Electron's 'Error invoking remote method …: Error:' prefix. Show it verbatim?"
    resolution: autonomous
    class: two-way
    chosen: "copyErrorMessage strips the prefix so capture-status shows only the main-process message"
    source_tag: Local Canon
    precedents: ["ui/src/main/index.ts:440 — ipcMain.handle throws Error(result.error) on ok:false"]
    research: { engine: none, sources: [] }
    reasoning: "The status line is user-facing; the channel name is noise. Copy-path failures pass through the same helper, so both copy errors read the same way."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-16 | claude-code-vscode | Initial handoff after gate88 |
