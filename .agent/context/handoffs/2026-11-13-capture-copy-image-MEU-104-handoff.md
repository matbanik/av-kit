---
date: "2026-11-13"
project: "capture-copy-image"
meu: "MEU-104"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-13-capture-copy-image/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-13-capture-redact-MEU-103-handoff.md"
---

# Handoff: 2026-11-13-capture-copy-image-MEU-104-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-104 `capture-copy-image-actions`, P2. This is the second of the five capture annotation editor sessions, Sessions 68 to 72 (grouping D-674).

- **The render route.** `POST /api/v1/captures/{id}/render` takes the annotate body and returns the shot baked with those marks as `image/png`, without writing a file, sidecar or row (RENDER_ROUTE, D-689, D-695). It sits right after annotate.
  - `ImageAnnotatePort.render` (RENDER_PORT) and the adapter's `render`, which shares `_bake_canvas` with `bake` (RENDER_BAKE). It always returns PNG and maps an unreadable original to `InboxPathError("the image could not be opened")`, which names no path.
  - `CaptureService.render_marks` holds `CAPTURE_FILE_LOCK`, raises `NotFoundError` for an unknown shot or a missing original, and clamps each mark as annotate does (RENDER_SERVICE).
  - The MCP server gains no action: `render` is REST-only (D-691).
- **Copy image.** A `Copy image` button (`capture-copy-image`, Copy icon, ghost, shortcut `Ctrl+C`) sits after Save annotations and before Flatten into image (COPY_BUTTON, D-690, D-696). It and canvas Ctrl+C or Cmd+C (COPY_KEY, D-692) post the current marks, saved or not, to render through `postAuthorizedBlob` and `renderClipboardPng` (RENDER_CLIENT), and write the PNG with `writeClipboardImage`. A text field and a non-empty selection keep native copy.
- **The filmstrip copy** fetches the annotated variant for a shot with a non-empty `annotated_path`, else the original (FILMSTRIP_AS_SHOWN, D-677 A).
- **The shot actions** are renamed `Save annotations`, `Flatten into image…` and `Restore backup…`, with their titles, statuses, confirm text and Settings labels (ACTION_LABELS, D-694). A dirty Flatten is enabled when the marks can be saved, and its confirm accepts with `Save and flatten`, which saves before it flattens (SAVE_AND_FLATTEN, D-693).
- **The help body** names Copy image, Ctrl+C, the text-field rule and the three new names, and fixes the missing space in "marks.Right-click" (COPY_HELP).

The OpenAPI snapshot gains the render path and its `image/png` response (H1-4). The MCP audit baseline does not change.

**Build Plan Section**: bp09, `docs/build-plan/09-screenshot-capture.md` §Copy image and the shot action names, with `11-page-layout.md` and `gui-actions-index.md`.

**Predecessor**: [MEU-103 handoff](2026-11-13-capture-redact-MEU-103-handoff.md), Session 68. The grouping is `.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md` (row 45). Its decisions D-158, D-159, D-160, D-674, D-675, D-677 and D-678 carry.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-13. Codex approved the plan at round 1 (`.agent/context/handoffs/2026-11-13-capture-copy-image-plan-critical-review.md`). At the gate Mat set the execution budget and said to execute ("50M, execute"), D-698. During execution Mat ruled twice, each through a Decision Brief: AC-104.7 control characters ("Parity (Recommended)", D-699) and AC-104.8's committed-snapshot adjacency ("Live + index (Recommended)", D-700).

**Receipts.** A receipt named by its file name alone (`s69-*.txt`) is in the session's receipts folder (`RECEIPTS_DIR`). A name starting `s69/` is in that folder's session subfolder. Full paths appear only in the evidence records' `command` fields.

### Where values go, as built (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The render body's marks.**
  - The editor's `annotationsRef.current` goes through `parseAnnotateBody({annotations})` in `renderClipboardPng` (`capture-clipboard.ts:90`); a list the schema refuses throws `COPY_IMAGE_MARKS_ERROR` (`:10`) with no request.
  - `postAuthorizedBlob` (`capture-image.ts:20`) posts it as JSON with the same base and token seam as `fetchAuthorizedBlob` (`:8`), both through `backendBaseAndToken` (`:1`).
  - The route `render_capture` (`routes/captures.py:462`, between `annotate_capture` at `:446` and `flatten_capture` at `:473`) parses it as `AnnotateIn` and maps it with `_annotations_from_in` (`:158`), the same models as annotate, so the same bodies give 422 (AC-104.7, D-699).
  - `render_marks` (`services/capture.py:1493`) clamps each mark with `_clamp_annotation` and calls the adapter's `render` (`adapter.py:546`), which runs `_bake_canvas` (`:560`), the body `bake` (`:526`) now shares.
  - No response, log or Console line echoes a mark value. A refusal's body is the error envelope with no value in it (AC-104.7 asserts that).
- **The rendered bytes.** `_encode_view(canvas.convert("RGB"), ".png")` writes them in memory. The route returns them as `Response(media_type="image/png")`; the client takes the blob, `toClipboardPng` checks the PNG signature, and `writeClipboardImage` receives them. Nothing writes them to disk or logs them.
- **The filmstrip variant.** `onCopyImage` (`CapturePage.tsx:1848`) passes `'annotated'` only when `annotated_path` is a non-empty string; `loadClipboardPng(id, variant = 'original')` (`capture-clipboard.ts:81`) adds `?variant=` to the image GET.
- **An unreadable original.** `render` catches `(UnidentifiedImageError, OSError)` around the open and raises `InboxPathError("the image could not be opened")`, which `errors.py` maps to 422 with no path.
- **The copy trigger.** `copyEnabled` (`CapturePage.tsx:481`) is `selected !== null && overlayReady && textDraft === null`. The button (`:2128`) and the Ctrl+C branch of `handleEditorKey` (`:1647`, the call at `:1692`) both run `copyCurrentImage` (`:1817`). The key branch also needs `confirm === null`, `historyOwnsFocus()`, a target that is not editable and `selectionCollapsed()` (`:207`).

AC-104.10 traces one unsaved mark through the Python half with recording wrappers, and AC-104.11 through the renderer half from the keydown to the recording `writeClipboardImage` fake (Session 55 RULE-3).

### Row 1's caller grep (S55 RULE-1, S59 RULE-1, S62 RULE-4, S63 RULE-1, S66 RULE-1)

Before its edits, row 1 swept `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` at `b3f3933` (`s69/sweep-r1.txt`, `s69/sweep-r1b.txt`) and appended the hits to `s69-anchors.txt` (244 lines). It has one section for each of these:
- the bake path callers: `services/capture.py` annotate, crop, flatten, revert and export, `adapter.py`'s `apply_region_pass` and `tools/capture_bake_fixture.py`;
- `loadClipboardPng` and `fetchAuthorizedBlob`;
- the literals `Save overlay`, `Apply to image`, `Revert image`, `Save the overlay first` and `Save or discard overlay marks first`;
- the `ACTION_BUTTONS` pins, the route counts and ROUTE_INDEX, the annotate path pins, the `bake` and `loadClipboardPng` signature pins, and `flattenStatus`.

Row 0's part of the same file holds each target's SHA-256 and line endings.

- **Every pin the plan's §Pins that move table names moved as the table says**, in row 2: ROUTE_INDEX and the four route counts (78 to 79), `ROUTE_COUNT_AFTER`, `REST_ONLY`, the action-row, flatten, page, page-behaviour and help-content pins, and the capture-inbox lines.
- **Hits missing from the table.** Each moved in row 2 with the literals it carries (§Departures 1). Line numbers are the current ones:
  - `capture-flatten.test.ts:91`, the `REVERT_DIRTY_TITLE` literal;
  - `capture-page.behavior.test.ts:4003` and `capture-inbox.test.ts:1555`, the convert status `Applied to a new PNG copy: …`;
  - `capture-inbox.test.ts:1707`, the AC-81.9 overflow list `ACTION_IDS`, which gains `capture-copy-image` after `capture-save` (`:1710`);
  - `capture-page.test.ts:104`, `WAVE9_EXTRA_TESTIDS`, which gains `capture-copy-image` so the mount check at `:475` covers it; the source pin on the Save button's `shortcut=` (`:633`) still holds.
- **Hits that do not move.** `tests/e2e/test_api_captures.py:63` (CAPTURE_ROUTES checks presence only), `test_domain_capture.py:324-325` (the `probe` and `bake` signatures), `mcp-server/tests/fixtures.ts:87` (the audit route list; no MCP action), `ui/tests/unit/tooltip.test.tsx` (sample strings) and the comments the absence grep excludes.
- **The byte-hash guard.** Row 1 appended the MEU-104 block after the file's last line (`test-ids.ts:512-514`): `CAPTURE_COPY_IMAGE`. AC-51.6 and AC-81.13 read `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` (`capture-action-row.test.ts:756`). Row 1's own run passed 13 tests (`s69-types-action-row.txt`).

### Row 2's Red tests (S50 RULE-2, S61 RULE-3, S66 RULE-2)

Row 2 wrote three new files, all LF:

- `tests/unit/test_capture_render.py` (355 lines) covers AC-104.1 to .5 and .10.
- `tests/e2e/test_api_capture_render.py` (145 lines) covers AC-104.6 to .8.
- `ui/tests/unit/capture-copy-image.behavior.test.ts` (833 lines) covers AC-104.1 (TypeScript), .11 to .20 and .23.

It added tests to existing files, each keeping its endings:
- AC-104.9 to `mcp-server/tests/capture.test.ts:1647` (CRLF), with `"render"` appended to `REST_ONLY`;
- AC-104.22 to `ui/tests/e2e/capture-inbox.test.ts:3221` (LF).

It also moved the pins the plan's table names and the ones in §Departures 1 to 3. `id-length.py` found all 22 new pytest ids within red-check's header width (`s69-r2-id-length.txt`).

### Row 3's Green changes (S55 RULE-1)

Row 3 made counted byte replacements, keeping CRLF:

- **Port.** `ImageAnnotatePort.render` after `bake` (`ports/capture.py:32`).
- **Adapter.** `bake`'s body after the open moved into `_bake_canvas`; `render` opens, maps the error, bakes and encodes PNG.
- **Service.** `render_marks`.
- **API.** `render_capture`, and the regenerated `openapi.committed.json` (one added path, H1-4).
- **UI.**
  - `backendBaseAndToken` and `postAuthorizedBlob` (`capture-image.ts`); `renderClipboardPng` and the `variant` parameter (`capture-clipboard.ts`);
  - the Copy image entry and the new names in `ACTION_BUTTONS` (`capture-toolbar.ts:75-79`);
  - `APPLY_TITLES.dirty`, `REVERT_DIRTY_TITLE`, `applyState`'s `currentCount` and `canSave`, `flattenConfirmText`'s `unsaved` and the `flattenStatus` texts (`capture-flatten.ts`);
  - `selectionCollapsed`, `copyEnabled`, the COPY_KEY branch, `copyCurrentImage`, `onCopyImage`'s variant, the Save and flatten accept and the Copy image button (`CapturePage.tsx`);
  - the help body (`capture-help-content.ts`) and the two Settings labels (`SettingsPage.tsx:1056`, `:1086`).

**First runs.** Row 3's first pytest run (`s69/row3-py-try1.txt`) gave `5 failed, 123 passed`: AC-104.7's four 422 cases and AC-104.8. The 422 cases failed on row 2's test data: its expected envelope lacked `"details": None`, which every sibling 422 test carries (§Departures 4). AC-104.8 failed because the committed snapshot's paths are sorted, so render can't sit after annotate there; that went to Mat as a Decision Brief, and D-700 changed AC-104.8 (§Departures 5). The UI run then failed AC-104.16's kept-comment check on a wrong path in the test (§Departures 6). After those test fixes the targeted rerun passed (`s69/row3-py-try2.txt`: `8 passed in 2.40s`), and row 3's command exited 0 (`s69/row3-run.txt`).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-104.1 | type | The exact signatures: `ImageAnnotatePort.render(self, original_path, annotations)`, the adapter's `render` and `_bake_canvas(self, canvas, annotations)`, `CaptureService.render_marks(self, shot_id, annotations)`, `postAuthorizedBlob(path, body)`, `renderClipboardPng(id, annotations)` and `loadClipboardPng(id, variant = 'original')`. Row 1 added the names, so it passed where row 2 wrote it | Local Canon: D-689 | `tests/unit/test_capture_render.py:116`; `ui/tests/unit/capture-copy-image.behavior.test.ts:348` | ✅ |
| AC-104.2 | behaviour | RENDER_BAKE: over no marks and over a region mark plus a drawn mark, on a PNG RGBA, a JPEG and a WebP original, `render`'s bytes equal the PNG `bake` writes for the same marks; a WebP `annotated_format` still gives PNG bytes | Spec: 09 Copy image row | `test_capture_render.py:139`, `:159` | ✅ |
| AC-104.3 | behaviour | `render` writes nothing (the folder's listing and mtimes are unchanged), and an unreadable original raises `InboxPathError` whose message names no path | Spec: 09 Copy image row; Session 50 RULE-1 | `test_capture_render.py:181`, `:199` | ✅ |
| AC-104.4 | behaviour | RENDER_SERVICE: `render_marks` clamps a mark past the edge as annotate does, writes no file, sidecar or row, and raises `NotFoundError` for an unknown shot and a missing original | Local Canon: D-695 | `test_capture_render.py:222`, `:253` | ✅ |
| AC-104.5 | behaviour | `render_marks` holds `CAPTURE_FILE_LOCK` while it calls the adapter (a recording adapter reads the lock's state) | Local Canon: D-695 | `test_capture_render.py:273` | ✅ |
| AC-104.6 | behaviour | RENDER_ROUTE: POST render gives 200 `image/png` whose bytes equal the annotated file annotate writes for the same body in PNG format; the shot row, sidecar and folder are unchanged after it | Spec: 09 Copy image row | `tests/e2e/test_api_capture_render.py:68` | ✅ |
| AC-104.7 | behaviour | render gives the same status as annotate for each case, one parametrize id each: a lone surrogate, empty text, an extra field and a bad type give 422 from both; control characters give 200 from both with render's bytes equal to annotate's PNG; an unknown shot gives 404; no body echoes the refused value | Session 53 RULE-1; Session 50 RULE-1; Human-approved: D-699 | `test_api_capture_render.py:93` | ✅ |
| AC-104.8 | behaviour | The live OpenAPI schema lists render right after annotate; the committed snapshot carries it with `image/png` and an entry equal to the live one (its keys are sorted); ROUTE_INDEX lists it right after annotate, and the route count is 79 | Spec: 09 Copy image row; Human-approved: D-700 | `test_api_capture_render.py:125`; `tests/e2e/test_api_openapi.py:57-58` | ✅ |
| AC-104.9 | guard | MCP `REST_ONLY` names `render`, and `avkit_capture` has no render action. It passed where row 2 wrote it | Local Canon: D-691 | `mcp-server/tests/capture.test.ts:1647` | ✅ |
| AC-104.10 | behaviour | One unsaved mark traced from the API body through `_annotations_from_in`, `render_marks`, `_clamp_annotation` and `_bake_canvas` (recording wrappers, each recording it once) to the response's pixels | Session 55 RULE-3 | `test_capture_render.py:289` | ✅ |
| AC-104.11 | behaviour | One unsaved mark traced from a Ctrl+C keydown on the canvas through `handleEditorKey`, the recorded POST to render and `toClipboardPng`, to the recording `writeClipboardImage` fake, called once with exactly the bytes the fake server returned | Session 55 RULE-3; Spec: 09 Copy image row | `capture-copy-image.behavior.test.ts:365` | ✅ |
| AC-104.12 | behaviour | COPY_KEY: each guard row (text field, selection, repeat, Shift, Alt, confirm open, no shot, overlay not ready, crop, text draft) makes no POST and no `preventDefault`; Ctrl+C and Cmd+C on the canvas each make one | Spec: 09 Copy image row; D-678 | `capture-copy-image.behavior.test.ts:387`, `:403`, `:512` | ✅ |
| AC-104.13 | behaviour | COPY_BUTTON: Copy image sits between Save annotations and Flatten into image when dirty and before Flatten when not; its tooltip reads `Copy image (Ctrl+C)`; it is disabled with no shot, before the overlay loads and with a text draft open; a click posts the current marks | Local Canon: D-696 | `capture-copy-image.behavior.test.ts:539`, `:571` | ✅ |
| AC-104.14 | behaviour | A copy error (render refused, `writeClipboardImage` missing, the fake throwing, `COPY_IMAGE_MARKS_ERROR`) shows `copyErrorMessage`'s text, names no path and writes nothing | Local Canon: MEU-88 copy errors | `capture-copy-image.behavior.test.ts:596`, `:617`, `:628` | ✅ |
| AC-104.15 | behaviour | FILMSTRIP_AS_SHOWN: the filmstrip copy fetches `variant=annotated` for a non-empty `annotated_path` and `variant=original` for `null` and `''` | Spec: 09 Filmstrip row; D-677 A | `capture-copy-image.behavior.test.ts:636` | ✅ |
| AC-104.16 | behaviour | ACTION_LABELS: the aria-labels and confirm accepts read the new names; no `Save overlay`, `Apply to image` or `Revert image` outside comment lines in `ui/src`; the four kept comments keep them | Spec: 09 Labels row | `capture-copy-image.behavior.test.ts:660`, `:678` | ✅ |
| AC-104.17 | behaviour | SAVE_AND_FLATTEN: `applyState` gives each row of its rule (clean with and without saved marks; dirty with no current marks, with `canSave` false, with an unflattenable type, and enabled) | Local Canon: D-693 | `capture-copy-image.behavior.test.ts:719` | ✅ |
| AC-104.18 | behaviour | Accepting a dirty flatten (`Save and flatten`) posts annotate before flatten; a save that returns `false` or throws posts no flatten and shows the error | Spec: 09 Labels row; D-693 | `capture-copy-image.behavior.test.ts:746`, `:765` | ✅ |
| AC-104.19 | behaviour | The status lines, the confirm text (clean and dirty), APPLY_TITLES.dirty and REVERT_DIRTY_TITLE read the D-694 literals | Local Canon: D-694 | `capture-copy-image.behavior.test.ts:783` | ✅ |
| AC-104.20 | behaviour | COPY_HELP: the help body names Copy image and Ctrl+C with the current marks and the text-field rule, the three new action names, and no `marks.Right-click` | Local Canon: D-694 | `capture-copy-image.behavior.test.ts:813` | ✅ |
| AC-104.21 | check | Spec D3: 09's mock, route row, `:610`, `:664`, `:672`, `:704`, `:799` and the Delivered note; 11-page-layout `:41` and `:93`; the gui-index rows with the `capture:copy_image` IPC cell unchanged. Each file keeps CRLF | Local Canon: D3 | row 5's check (`s69-r5-spec.txt`) | ✅ |
| AC-104.22 | behaviour | Electron: the action row shows `Save annotations` when dirty, `Copy image` and `Flatten into image…`; a dirty flatten confirm accepts with `Save and flatten`. No step writes the system clipboard | Spec: 09 Labels and Copy image rows | `ui/tests/e2e/capture-inbox.test.ts:3221`; gate `ui-electron` | ✅ |
| AC-104.23 | guard | `RESERVED_CHORDS` holds Ctrl+C, and the command registry has no copy entry. It passed at Red and after | Local Canon: D-678 | `capture-copy-image.behavior.test.ts:825` | ✅ |
| AC-16 (cross-ref) | regression | AC-16.6's path census and ROUTE_INDEX rows read 79 routes with render right after annotate (row 2 moved them; they failed at Red) | plan §Pins that move | `tests/e2e/test_api_openapi.py`; gate `py-tests` | ✅ |
| AC-42 (cross-ref) | regression | AC-42.9's `ROUTE_COUNT_AFTER` reads 79 | plan §Pins that move | `tests/e2e/test_api_downloads.py`; gate `py-tests` | ✅ |
| AC-134 (cross-ref) | regression | AC-134.17's committed-OpenAPI frames check reads the regenerated snapshot (it failed at Red on the count) | plan §Pins that move | `test_api_openapi.py`; gate `py-tests` | ✅ |
| AC-135 (cross-ref) | regression | AC-135.20's sheet check reads the regenerated snapshot | plan §Pins that move | `test_api_openapi.py`; gate `py-tests` | ✅ |
| AC-136 (cross-ref) | regression | AC-136.16's export check reads the regenerated snapshot | plan §Pins that move | `test_api_openapi.py`; gate `py-tests` | ✅ |
| AC-57 (cross-ref) | regression | AC-57.6 and AC-57.10 read the aria-label `Save annotations`; the mount rule is unchanged | plan §Pins that move | `ui/tests/unit/capture-page.behavior.test.ts`, `capture-inbox.test.ts`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-67 (cross-ref) | regression | MEU-67's flatten and revert keep their rules except the dirty case, which follows SAVE_AND_FLATTEN; AC-67.20 to AC-67.25 and AC-67.33 read the D-694 titles, statuses and confirm text (§Departures 2 and 3) | plan §Pins that move | `capture-flatten.test.ts`, `capture-page.behavior.test.ts`, `capture-page.test.ts`, `capture-help-content.test.ts`, `capture-inbox.test.ts`; gate `ui-tests`, `ui-electron` | ✅ |
| AC-81 (cross-ref) | regression | AC-81.1 and AC-81.2 read the 9 action ids with `capture-copy-image` after `capture-save` and the dirty case under SAVE_AND_FLATTEN; AC-81.9's overflow list gains it (§Departures 1) | plan §Pins that move | `ui/tests/unit/capture-action-row.test.ts`, `capture-inbox.test.ts`; gate `action-row`, `ui-tests`, `ui-electron` | ✅ |
| AC-88 (cross-ref) | regression | MEU-88's filmstrip copy keeps its PNG check and errors; AC-88.5 fetches the original of a shot with no annotated file, now with `?variant=original` | plan §Pins that move; D-677 A | `ui/tests/unit/capture-filmstrip-actions.behavior.test.ts:394`, `capture-clipboard.test.ts`; gate `ui-tests` | ✅ |
| AC-89 (cross-ref) | regression | AC-89.8 reads the flatten help sentence with the new names | §Departures 3 | `capture-help-content.test.ts`; gate `ui-tests` | ✅ |
| AC-51.6 (cross-ref) | regression | The test-ids prefix hash is unchanged: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454` | plan §Files Modified (byte-hash guard) | `capture-action-row.test.ts:756`; gate `action-row` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-104.2 to AC-104.8, AC-104.10 (pytest) | Row 2: `21 failed, 1 passed in 11.04s`, exit 1 (`s69-py-red.txt`). Decisive lines: `assert b'' == b'\x89PNG\r\n\x1a\n'` ×8 (row 1's stub `render`); `assert 404 == 422` ×4 and `assert 404 == 200` ×3 (no route); `AssertionError: assert '/api/v1/captures/{id}/render' in [...]` (AC-104.8) | Row 3: `304 passed in 28.14s` (`s69-py-green.txt`); gate `py-tests` | `test_capture_render.py:139-289`, `test_api_capture_render.py:68-125` |
| AC-104.11 to AC-104.20 (Vitest) | Row 2: `17 failed \| 2 passed (19)` in `capture-copy-image.behavior.test.ts`, exit 1 (`s69-ui-red.txt`). Decisive lines: `Ctrl+C on the canvas is taken: expected false to be true`; `Copy image is mounted with no shot: expected null not to be null`; `Flatten is enabled while dirty: expected true to be false` ×2; `expected 'Save the overlay first' to be 'Save annotations first'`; `expected 'Apply to image' to be 'Flatten into image…'`; `promise resolved "Uint8Array[]" instead of rejecting`; `thumb 0: expected [ Array(1) ] to deeply equal [ Array(1) ]` | Row 3: `Tests 241 passed (241)` over 7 files (`s69-ui-green.txt`); gate `ui-tests` | `capture-copy-image.behavior.test.ts:365-813` |
| AC-104.22 (Electron) | Row 2: `1 failed`, exit 1 (`s69-e2e-red.txt`): `expect(locator).toBeVisible() failed … element(s) not found` | Row 3: `47 passed (1.1m)` (`s69-e2e-green.txt`); gate `ui-electron` | `capture-inbox.test.ts:3221` |
| The moved pins (§Pins that move) | Row 2: pytest `6 failed, 100 passed in 14.64s` (AC-16.6 ×2, AC-134.17, AC-135.20, AC-136.16, AC-42.9) and Vitest `17 failed \| 186 passed (203)` in 5 files (`s69-pins-red.txt`) | Row 3's runs and gate `py-tests`, `ui-tests` | §Pins that move |
| AC-104.1, AC-104.9, AC-104.23 | Row 1 met AC-104.1; AC-104.9 and AC-104.23 are guards. Row 2's guard runs: pytest `1 passed, 13 deselected` (`s69-r2-guard.txt`), MCP `1 passed \| 56 skipped (57)` (`s69-r2-guard-mcp.txt`), Vitest `1 passed \| 18 skipped (19)` each (`s69-r2-guard-ui.txt`, `s69-r2-guard-ui23.txt`) | Row 3 (`s69-mcp-green.txt`: `Tests 57 passed (57)`) and the gate | `test_capture_render.py:116`, `capture.test.ts:1647`, `capture-copy-image.behavior.test.ts:348`, `:825` |
| AC-104.21 | Row 5's check exits 1 before row 5 (plan §Verification Plan) | Row 5: all eight keys `True` (`s69-r5-spec.txt`) | row 5 |

- **red-check.** Row 2's check (`s69-red-check.txt`) reads `red-check: 3 receipt(s), 19 required test(s), 0 problem(s)`. Every failing block failed by assertion alone.
- **The passes in the Red runs** are AC-104.1 in pytest, and AC-104.1 and AC-104.23 in Vitest.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-copy-image/baseline.ps1 *> C:/Temp/av-kit/s69-baseline.txt (task.md row 0's Validation cell; base runs in C:/Temp/av-kit/s69-base-py.txt, s69-base-ui.txt, s69-base-mcp.txt, s69-base-e2e.txt, s69-base-ui-build.txt, s69-base-mcp-build.txt and s69-base-ruff.txt; the Electron rerun in C:/Temp/av-kit/s69-base-e2e-rerun.txt)", "scope": "Row 0: the D-698 words, the queue, the absent names and new files, the shapes (S7), baseline.sha, baseline-dirty.txt, the anchors and line endings, the lock syncs, the FFmpeg pair, the base runs, and the red-check, identity and id-length selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b3f3933 before any row", "output": "budget and execute words found, each USER_EXPLICIT 2026-11-13 '50M, execute'; queue: {'MEU-81': 'approved', 'MEU-99': 'approved', 'MEU-103': 'approved', 'MEU-104': 'pending'}; b3f3933 is an ancestor of HEAD: True; absent names and labels: lines [] in each of the 15 files; shapes wrong (S7): []; missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; ffmpeg version n8.1.3-27-g8dca1586f4-20261031; base pytest 2435 passed, 37 warnings in 165.99s; base UI Test Files 122 passed (122), Tests 1303 passed (1303); base MCP Test Files 36 passed (36), Tests 526 passed (526); base Electron 1 failed, 45 passed (1.1m), exit 1 (AC-81.11 F2 held by another process, §Departures 8; the rerun gave the same); base ruff All checks passed!; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; identity selftest exit 0; id-length selftest: 4 case(s), 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-1-types", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s69/row1.ps1 (task.md row 1's Validation cell: pytest test_domain.py, test_domain_capture.py and row 1's guards *> C:/Temp/av-kit/s69-types-py.txt; export_openapi.py --check *> C:/Temp/av-kit/s69-types-openapi.txt; pyright *> C:/Temp/av-kit/s69-types-pyright.txt; ruff *> C:/Temp/av-kit/s69-types-ruff.txt; npm --prefix ui run typecheck *> C:/Temp/av-kit/s69-types-ui.txt; capture-action-row.test.ts *> C:/Temp/av-kit/s69-types-action-row.txt; sweep C:/Temp/av-kit/s69/sweep-r1.txt, s69/sweep-r1b.txt, appended to C:/Temp/av-kit/s69-anchors.txt)", "scope": "Row 1: ImageAnnotatePort.render (RENDER_PORT); the adapter's _bake_canvas extracted from bake with bake's bytes unchanged, and a render stub returning empty bytes; a render_marks stub returning empty bytes; postAuthorizedBlob (returns null), renderClipboardPng (returns an empty Uint8Array) and COPY_IMAGE_MARKS_ERROR; loadClipboardPng's variant parameter, ignored by the stub; the MEU-104 test-id block; no route; and the caller sweep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b3f3933 plus rows 0 to 1", "output": "176 passed in 29.53s; export_openapi --check exit 0; pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; ui typecheck exit 0; capture-action-row Tests 13 passed (13); anchors 244 lines"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-2-red", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s69/row2.ps1 > C:/Temp/av-kit/s69/row2-run.txt 2>&1 (task.md row 2's Validation cell: pytest tests/unit/test_capture_render.py tests/e2e/test_api_capture_render.py *> C:/Temp/av-kit/s69-py-red.txt; Vitest capture-copy-image.behavior.test.ts *> C:/Temp/av-kit/s69-ui-red.txt; playwright capture-inbox.test.ts -g AC-104.22 *> C:/Temp/av-kit/s69-e2e-red.txt; the moved pins *> C:/Temp/av-kit/s69-pins-red.txt; red-check.py with the 19 --require ids *> C:/Temp/av-kit/s69-red-check.txt; the guards *> C:/Temp/av-kit/s69-r2-guard.txt, s69-r2-guard-mcp.txt, s69-r2-guard-ui.txt, s69-r2-guard-ui23.txt; id-length.py *> C:/Temp/av-kit/s69-r2-id-length.txt)", "scope": "MEU-104 Red: AC-104.2 to .8 and .10 in pytest, AC-104.11 to .20 in Vitest and AC-104.22 in Electron against the row 1 code; the moved pins; the AC-104.1, .9 and .23 guards", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD b3f3933 plus rows 0 to 2", "output": "pytest 21 failed, 1 passed in 11.04s (child exit 1): assert b'' == b'\\x89PNG\\r\\n\\x1a\\n' x8; assert 404 == 422 x4; assert 404 == 200 x3; the render path not in the live path list. Vitest 17 failed | 2 passed (19) (child exit 1): Ctrl+C on the canvas is taken: expected false to be true; Copy image is mounted with no shot: expected null not to be null; expected 'Save the overlay first' to be 'Save annotations first'; expected 'Apply to image' to be 'Flatten into image\u2026'. Electron 1 failed (child exit 1): expect(locator).toBeVisible() failed. Pins: pytest 6 failed, 100 passed in 14.64s; MCP 57 passed; Vitest 17 failed | 186 passed (203) in 5 files. red-check: 3 receipt(s), 19 required test(s), 0 problem(s). Guards: 1 passed, 13 deselected; MCP 1 passed | 56 skipped (57); Vitest 1 passed | 18 skipped (19) twice. id-length: 22 test(s), 0 too long"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-3-green", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s69/row3.ps1 > C:/Temp/av-kit/s69/row3-run.txt 2>&1 (task.md row 3's Validation cell: pytest *> C:/Temp/av-kit/s69-py-green.txt, Vitest *> C:/Temp/av-kit/s69-ui-green.txt, MCP *> C:/Temp/av-kit/s69-mcp-green.txt, Electron *> C:/Temp/av-kit/s69-e2e-green.txt, pyright *> C:/Temp/av-kit/s69-r3-pyright.txt, ruff *> C:/Temp/av-kit/s69-r3-ruff.txt, export_openapi.py --check *> C:/Temp/av-kit/s69-r3-openapi.txt, the UI and MCP typechecks, ui lint and ui build *> C:/Temp/av-kit/s69-r3-ui-types.txt, s69-r3-mcp-types.txt, s69-r3-ui-lint.txt, s69-r3-ui-build.txt; the first targeted pytest runs in C:/Temp/av-kit/s69/row3-py-try1.txt and s69/row3-py-try2.txt)", "scope": "MEU-104 Green: RENDER_PORT, RENDER_BAKE, RENDER_SERVICE, RENDER_ROUTE, RENDER_CLIENT, COPY_BUTTON, COPY_KEY, FILMSTRIP_AS_SHOWN, ACTION_LABELS, SAVE_AND_FLATTEN and COPY_HELP, the regenerated snapshot, and the plan's guards", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD b3f3933 plus rows 0 to 3", "output": "try 1: 5 failed, 123 passed (AC-104.7 422 cases on the test's VALIDATION constant, AC-104.8 on the sorted snapshot; §Departures 4 and 5); try 2: 8 passed in 2.40s; pytest 304 passed in 28.14s; Vitest Tests 241 passed (241) in 7 files; MCP Tests 57 passed (57); Electron 47 passed (1.1m); pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; export_openapi --check exit 0; typecheck, lint and build exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-5-spec", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s69/row5.ps1 > C:/Temp/av-kit/s69/row5-run.txt 2>&1 (task.md row 5's Validation cell: row 5's checks over 09, 11-page-layout and gui-actions-index.md *> C:/Temp/av-kit/s69-r5-spec.txt)", "scope": "Row 5 (D3, AC-104.21): 09's mock, route row, label lines and Delivered (Session 69) note; 11-page-layout's action row; the gui-index Copy image and shot rows with the capture:copy_image IPC cell unchanged; CRLF kept. Row 4 has no work in this plan", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b3f3933 plus rows 0 to 5", "output": "{'crlf_only': True, 'delivered_note': True, 'render_route': True, 'labels_09': True, 'layout': True, 'copy_image_cell': True, 'copy_shot_row': True, 'index_labels': True}"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-6-status", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s69/row6.ps1 > C:/Temp/av-kit/s69/row6-run.txt 2>&1 (task.md row 6's Validation cell: meu_status.py render --check *> C:/Temp/av-kit/s69-r6-render.txt and the status read *> C:/Temp/av-kit/s69-r6-status.txt; pre-status copies in C:/Temp/av-kit/s69/pre-status/)", "scope": "Row 6: MEU-104 ready_for_review with its execution_plan, the registry and BUILD_PLAN renders, and grouping row 45 executed, noting Session 69", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD b3f3933 plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content; MEU-104: ready_for_review row 45: ['| 45 | `capture-copy-image` | MEU-104 | P2 | executed (Session 69) | `docs/execution/plans/2026-11-13-capture-copy-image/` |']"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-13-capture-copy-image/session-gate.ps1 *> C:/Temp/av-kit/s69-gate-h1.txt (task.md row H1-2's Validation cell; step receipts C:/Temp/av-kit/s69-D6-*.txt; outer receipt C:/Temp/av-kit/s69/h12-run.txt)", "scope": "The plan's full gate: identity before; static py-types, py-lint, ui-types, ui-lint, task-contract, scope-paths, red-check-selftest and id-length; fresh full py-tests, openapi, action-row (the AC-51.6 byte-hash guard), ui-tests, ui-build, mcp-types, mcp-build, mcp-tests, state-render and issues-render; runtime ui-electron; identity after. mcp-audit and build-record skipped by the plan", "phase": "full", "fresh": true, "snapshot": false, "exit_code": 0, "result": "pass", "tested_state": "b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25", "output": "baseline failures excused: [] for py, ui, mcp and e2e; py-types 0 errors, 0 warnings, 0 informations; py-lint All checks passed!; task-contract OK: 23 row(s), 21 fully checked, 2 exempt (view_file): H1-5, H2-1; scope-paths changed paths: 42 outside scope: [] head moved (S3): False, baseline-dirty paths changed since row 0 (S3): []; red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong; id-length: 22 test(s), 0 too long; py-tests 2459 passed, 37 warnings in 163.11s; openapi exit 0; action-row Tests 13 passed (13); ui-tests Test Files 123 passed (123), Tests 1322 passed (1322); ui-build built in 3.67s; mcp-types and mcp-build exit 0; mcp-tests Test Files 36 passed (36), Tests 527 passed (527); state-render Drift check passed - SSOT loaded (142 MEUs, 12 phases); issues-render OK: known-issues.md is up-to-date; ui-electron 47 passed (1.2m); tested_state before = after; session-gate: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s69-h1-3-h1-4", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s69/rowH1-3.ps1 > C:/Temp/av-kit/s69/h13-run.txt 2>&1 (meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; meu_status.py get MEU-104 *> C:/Temp/av-kit/s69-h13-status.txt; check *> C:/Temp/av-kit/s69-h13-check.txt); pwsh -NoProfile -File C:/Temp/av-kit/s69/rowH1-4.ps1 > C:/Temp/av-kit/s69/h14-run.txt 2>&1 (export_openapi.py --check *> C:/Temp/av-kit/openapi-check.txt; git diff against baseline.sha *> C:/Temp/av-kit/openapi-delta.txt; check *> C:/Temp/av-kit/openapi-delta-check.txt)", "scope": "H1-3 the MEU status read after the gate; H1-4 the OpenAPI snapshot check and its delta: exactly one added path, the render route", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25", "output": "MEU-104 ready_for_review: True; added lines: 51 route lines: ['+    \"/api/v1/captures/{id}/render\": {']"}
```

### Quality Gate Results

The H1-2 gate's last line is `session-gate: all steps exit 0` (`s69-gate-h1.txt:120`). It passed on its first run, and its baseline excuse lists are all empty.

- **Static.** pyright 0 errors, 0 warnings, 0 informations; ruff passed; UI typecheck and lint (`--max-warnings 0`) exit 0. The checks of the plan's own tooling also passed:
  - the task contract (23 rows, 21 fully checked, H1-5 and H2-1 exempt);
  - scope-paths (42 changed paths, none outside scope, head not moved, no baseline-dirty path changed since row 0);
  - the red-check selftest (49 fixtures, 0 wrong);
  - id-length (22 ids, 0 too long).
- **Suites, against the Session 68 baseline.**
  - pytest 2459 passed (2435 + 24: the 22 new tests, plus the render row in two cases driven by ROUTE_INDEX, the parametrize at `test_api_openapi.py:127` and AC-16.9's extra-field oracle over POST routes, `test_api_bodies.py:9`);
  - Vitest 1322 passed in 123 files (1303 + 19 in the new file);
  - MCP 527 passed (526 + AC-104.9);
  - Electron 47 passed (46 + AC-104.22; the base run's F2 failure did not recur, §Departures 8).
  - Every moved pin passes in its own file.
- **Build.** UI build ok (3.67s); MCP typecheck and build exit 0; the OpenAPI check exit 0; the state and known-issues renders match.
- **The byte-hash guard.** `action-row` passed 13 tests: AC-51.6 and AC-81.13 still read `6E569F82…870FF454`.
- **After the gate.** H1-3 (`s69-h13-check.txt`: `MEU-104 ready_for_review: True`; `drift-check.txt`) and H1-4 (`openapi-delta-check.txt`: `added lines: 51 route lines: ['+    "/api/v1/captures/{id}/render": {']`) both exit 0. `current-focus.md` and this handoff are outside `tested_state`.
- **Skipped by the plan.** `mcp-audit` (live network and YouTube, which the brief forbids; render is REST-only, so the audit baseline does not change) and `build-record` (no release and no package build).
- **Identity.** `tested_state` before and after: `b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25`. The FFprobe, Deno pin, `uv.lock` and UI lock hashes are the same before and after.
- **Warnings.** pytest reports 37 warnings, the same count as the baseline run (`s69-base-py.txt`); one is Pillow's `getdata` deprecation in `test_capture_export_adapter.py:558`. No test fails on a warning.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/ports/capture.py` | modified | `ImageAnnotatePort.render` (RENDER_PORT) |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `_bake_canvas`, shared by `bake`, and `render` (RENDER_BAKE) |
| `packages/core/src/avkit_core/services/capture.py` | modified | `render_marks` (RENDER_SERVICE) |
| `packages/api/src/avkit_api/routes/captures.py`, `openapi.committed.json` | modified | `render_capture` after annotate; the regenerated snapshot (RENDER_ROUTE) |
| `ui/src/renderer/src/features/capture/capture-image.ts`, `capture-clipboard.ts` | modified | `backendBaseAndToken`, `postAuthorizedBlob`, `renderClipboardPng` and the `variant` parameter (RENDER_CLIENT, FILMSTRIP_AS_SHOWN) |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts`, `CapturePage.tsx`, `capture-flatten.ts`, `capture-help-content.ts`, `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | COPY_BUTTON, COPY_KEY, FILMSTRIP_AS_SHOWN, ACTION_LABELS, SAVE_AND_FLATTEN and COPY_HELP |
| `ui/tests/e2e/test-ids.ts` | modified | The MEU-104 block appended (row 1) |
| `tests/unit/test_capture_render.py`, `tests/e2e/test_api_capture_render.py`, `ui/tests/unit/capture-copy-image.behavior.test.ts` | new | The MEU-104 tests. LF, 355, 145 and 833 lines |
| `tests/e2e/test_api_openapi.py`, `tests/e2e/test_api_downloads.py`, `mcp-server/tests/capture.test.ts`, `ui/tests/unit/capture-action-row.test.ts`, `capture-flatten.test.ts`, `capture-help-content.test.ts`, `capture-page.behavior.test.ts`, `capture-page.test.ts`, `ui/tests/e2e/capture-inbox.test.ts` | modified | The moved pins, AC-104.9 and AC-104.22 |
| `docs/build-plan/09-screenshot-capture.md`, `11-page-layout.md`, `gui-actions-index.md` | modified | Row 5's spec text (D3) |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-104's fields and row, and grouping row 45 (row 6) |
| `.agent/context/current-focus.md` | modified | Session 69's paragraph (H1-3) |

`git diff --stat b3f3933`, leaving out `docs/execution/` and the handoffs: `29 files changed, 458 insertions(+), 115 deletions(-)`, plus the three new test files.

Line endings were measured with Python bytes before each edit and kept:

- **CRLF.** Every source file above, `openapi.committed.json`, `test-ids.ts`, `mcp-server/tests/capture.test.ts`, the Python and Vitest test files that existed, 09, 11-page-layout, the gui index and the grouping file.
- **LF.** `ui/tests/e2e/capture-inbox.test.ts`, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md`.
- **New files** are LF.

```diff
 # adapter.py, render (abridged)
+    def render(self, original_path: Path, annotations: Sequence[Annotation]) -> bytes:
+        try:
+            with Image.open(original_path) as opened:
+                canvas = opened.convert("RGBA")
+        except (UnidentifiedImageError, OSError) as exc:
+            # No path in the message: it reaches the renderer's status line.
+            raise InboxPathError("the image could not be opened") from exc
+        canvas = self._bake_canvas(canvas, annotations)
+        return _encode_view(canvas.convert("RGB"), ".png")
 # services/capture.py, render_marks (abridged)
+        with CAPTURE_FILE_LOCK, self._uow_factory() as uow:
+            shot = uow.capture_shots.get(shot_id)
+            ...
+            clamped = [self._clamp_annotation(item, shot.width, shot.height) for item in annotations]
+            return self._annotate.render(shot.original_path, clamped)
 # capture-toolbar.ts
-  'capture-save': { icon: Save, name: 'Save overlay' },
-  'capture-apply-image': { icon: Stamp, name: 'Apply to image' },
-  'capture-revert-image': { icon: ArchiveRestore, name: 'Revert image' },
+  'capture-save': { icon: Save, name: 'Save annotations' },
+  'capture-copy-image': { icon: Copy, name: 'Copy image' },
+  'capture-apply-image': { icon: Stamp, name: 'Flatten into image…' },
+  'capture-revert-image': { icon: ArchiveRestore, name: 'Restore backup…' },
```

The excerpt is abridged. The sources are `adapter.py:546-558`, `services/capture.py:1493` and `capture-toolbar.ts:75-79`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-13-capture-copy-image-implementation-critical-review.md`, on the ledger loop `s69-execution-2026-11-13-capture-copy-image` (budget 50,000,000 tokens, cap 6 rounds, D-698). The table is filled in as the rounds return.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 (intent achieved: yes; 9,785,727 of 50,000,000 tokens) | `b3f393310d7a04fcdcde5092c1a5f238774493d8+2664bab4de4ff0835a23fdb79e129c0aabc4a191d3a8509bba717ae78a3afa25` |

### Verdict

approved in round 1 of 6 with no findings. The report was validated under `C:/Temp/av-kit` and copied byte for byte (sha256 `516360075ba7699b54368d9583694f6ab791bbf8e6d03ebe5a11b852609254a3`); H1-7a wrote `C:/Temp/av-kit/review-state.json` and H1-7b reported `OK: approved at round 1 of 6, 0 open blocking findings` (`C:/Temp/av-kit/exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `ruff check tools/` fails on 10 errors in `tools/issue_triage*` and `tools/meu_status*` that were there before this session | observation | None | Session 68 DEP-1; this plan lints only the files it edits |
| Commit and push | out-of-scope | — | Only on Mat's words, after Codex approves (H2) |

### Departures and their basis

1. **Pins missing from the plan's table (row 1 found, row 2 moved).** Row 1's sweep found `capture-flatten.test.ts:91` (`REVERT_DIRTY_TITLE`), `capture-page.behavior.test.ts:4003` and `capture-inbox.test.ts:1555` (the convert status, now `Flattened into a new PNG copy: photo-converted.png.`), `capture-inbox.test.ts:1707` (`ACTION_IDS`, which gains `capture-copy-image` after `capture-save`, so AC-81.9's overflow check covers the new button) and `capture-page.test.ts:104` (`WAVE9_EXTRA_TESTIDS`). Line numbers are the current ones. Each moved in row 2 with the D-694 text.
2. **The dirty flatten in the MEU-67 tests (row 2).** SAVE_AND_FLATTEN (D-693) enables Flatten while dirty when the marks can be saved, so tests that used an edit to get a disabled Apply moved:
   - the unit tests TA-14 and TA-15 (`capture-page.behavior.test.ts`) now expect Apply enabled while dirty and read `Flatten into image…` on hover, clean and dirty;
   - in Electron, TA-22 (`capture-inbox.test.ts:1474`) expects `toBeEnabled()` after the edit, and TA-23 and TA-24 get a disabled Apply through a new helper, `removeOnlyMark` (`:1464`), which deletes the only saved mark (a dirty overlay with no current marks, `Flatten into image… — Save marks first`).
   - TA-22's title still says "off after an edit"; the title was left as it was so the test keeps its name in the run history.
3. **Literals the plan left to execution (row 2, row 3).**
   - The dirty confirm text: `flattenConfirmText` with `unsaved` leads `Save the current marks, then bake them into`, and the clean text keeps `Bake the saved marks into` (`capture-flatten.ts:94`). D-693 says only that it names the current marks and says they are saved first.
   - `FLATTEN_HELP_SENTENCE` (`capture-help-content.test.ts`), which AC-67.25 and AC-89.8 read, now carries the three new names in the old sentence's shape.
   - A Save and flatten whose save returns `false` or is refused because `canSave` is false throws `Error(APPLY_TITLES.dirty)`, so the status line shows `Save annotations first`.
4. **AC-104.7's expected envelope (row 3).** Row 2's `VALIDATION` constant (`test_api_capture_render.py`) lacked `"details": None`, which the error envelope carries and every sibling 422 test expects. Row 3 added it. No assertion and no source changed.
5. **AC-104.8 (row 3, D-700).** `tools/export_openapi.py` writes the snapshot with `sort_keys=True`, so the committed paths are alphabetical and render cannot sit right after annotate there. Mat ruled "Live + index (Recommended)" (D-700): the test keeps the live adjacency, ROUTE_INDEX's adjacency and the count of 79, and checks that the committed snapshot carries render with an entry equal to the live one. The plan's AC row, its vocabulary line and task.md H1-7 were updated to D-700.
6. **AC-104.16's kept-comment path (row 3).** The test named `features/capture/settings-schemas.ts`; the file is `features/settings/settings-schemas.ts`. Row 3 fixed the path.
7. **A parametrize id (row 2).** AC-104.4's clamp case is `AC-104.4-clamp`, shorter than the draft's `AC-104.4-clamp-no-write`, to keep red-check's header within 71 characters (Session 67).
8. **The base Electron run (row 0).** `s69-base-e2e.txt` and its rerun gave `45 passed`, `1 failed`: AC-81.11 `Error: F2 held by another process`. Another program held the F2 hotkey; it was closed before row 3, whose Electron run passed 47 (`s69-e2e-green.txt`).

Departures 2, 4, 5 and 6 changed test files after row 2 (S2). Only 5 changes an AC's text, and it went to Mat as a Decision Brief (S12). The two execution-stage decisions, D-699 and D-700, are in the plan's YAML.

---

## Decision Log

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-13 | claude-code-local (Claude Opus 5.5) | The AC table, where values go, row 1's sweep, the Red and Green receipts, the H1-2 gate and the evidence records (H1-6) |
| Execution review | 2026-11-13 | codex-independent-reviewer | Round 1 approved, 0 findings, 9,785,727 tokens; H1-7a and H1-7b passed |
