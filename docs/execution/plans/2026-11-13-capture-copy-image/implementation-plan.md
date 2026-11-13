---
project: "2026-11-13-capture-copy-image"
date: "2026-11-13"
source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md#session-45--capture-copy-image-meu-104--p2"
grouping_source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md"
meus: ["MEU-104"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture copy image (Session 69)

> **Project:** `2026-11-13-capture-copy-image`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Copy image and action names (`:945-955`, anchor `copy-image-and-action-names`, MEU-104), with the build priority matrix row 9.30 (`docs/build-plan/build-priority-matrix.md:128`).
>
> **Source request.** On 2026-10-29 Mat accepted the capture annotation editor synthesis ("all recommendations are accepted", grouping D-158). The grouping's §3 lists this as Session 45; its §9.1 runs it as Session 69 (D-674), and §9.4 settles the filmstrip rule (D-677 A, USER_EXPLICIT 2026-11-12 "both recommendations accpeted") and the Ctrl+C route (D-678).
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 1 (`.agent/context/handoffs/2026-11-13-capture-copy-image-plan-critical-review.md`). At the plan gate Mat set the execution review budget to 50M (USER_EXPLICIT 2026-11-13 '50M, execute') and said to execute (USER_EXPLICIT 2026-11-13 '50M, execute'), with the default execution cap of 6 rounds (D-698).

## Goal

**Goal anchor:** Session 69 lets a user copy the image as they see it, with the current marks, saved or not, through a Copy image button and canvas Ctrl+C. Both go through a new `POST /captures/{id}/render` that bakes the posted marks exactly as Save would and writes no file. The filmstrip's Copy image follows the as-shown rule, and the per-shot actions take the names "Save annotations", "Flatten into image…" and "Restore backup…", with "Save and flatten" in the dirty-flatten confirm.

Five things are missing today (`b3f3933`):

1. **No render route.** The only way to bake marks is `POST /captures/{id}/annotate` (`routes/captures.py:445-452`), which writes the annotated file and the sidecar. Nothing returns baked bytes without writing.
2. **No editor copy.** The editor has no Copy image button, and Ctrl+C on the canvas does nothing. The only copy is the filmstrip menu's (MEU-88), which calls `loadClipboardPng(id)` (`capture-clipboard.ts:76`).
3. **The filmstrip copies the original.** `loadClipboardPng` always fetches `variant=original` (`capture-clipboard.ts:76`, called at `CapturePage.tsx:1800`), so saved marks are left out.
4. **Old names.** The action row reads "Save overlay", "Apply to image" and "Revert image" (`capture-toolbar.ts:74-76`), and the confirm strip's accept buttons match (`CapturePage.tsx:1942`, `:1949`).
5. **A dirty shot can't be flattened.** `applyState` disables Flatten while the overlay is dirty (`capture-flatten.ts`, `APPLY_TITLES.dirty`), so there is no "Save and flatten".

The session ends when:
- every 09 §Copy image and action names rule holds, each with a behaviour test;
- the session gate's last line is `session-gate: all steps exit 0`;
- MEU-104 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-13). No payload is oversized: the port, adapter, service, route, clipboard, flatten, toolbar and page capture files were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, `.agent/context/harness.local.md` Claude Code block). Execution waits for Mat's explicit words at the plan gate (§Status, D-698). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s69-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s69\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. GUI references are not shipped (`gui-refs-not-shipped`).
- **Decisions:** every decision for Mat goes to Mat through the Human Decision Protocol (AGENTS.md §Communication Policy), with a recommendation first and a do-nothing option. No decision goes to a subagent in this session.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s69-plan-canonical-2026-11-13-capture-copy-image` and `s69-execution-2026-11-13-capture-copy-image`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps: the ledger defaults, plan 3 and execution 6.
  - Token budgets: the plan loop keeps the 10.5M default. The execution loop opens at the budget Mat sets at the gate (`begin --token-budget`, D-698).
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit`, then copied byte for byte to its canonical path, and the `--review-state-only` receipt is rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-689 to D-700, AC-104.1 to AC-104.23, and the mechanism ids in §Single-statement contracts.
  - They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and they write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header and the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3) and asks for bare words in its Recheck cells (`fixed`, `open`; Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - the live MCP audit or `--update-baseline`;
  - `npm run dist`;
  - an `approved` verdict authored by the implementer.
- **No network, no clipboard:**
  - no test or row reaches YouTube or the network;
  - no test or row writes the system clipboard (Session 57 RULE-4): every copy test uses a recording fake for `window.api.writeClipboardImage`;
  - nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called);
  - no other program is stopped.

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-104 | `.agent/context/handoffs/2026-11-13-capture-copy-image-MEU-104-handoff.md` | only |

Rolling reviews: `.agent/context/handoffs/2026-11-13-capture-copy-image-plan-critical-review.md` and `.agent/context/handoffs/2026-11-13-capture-copy-image-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | Type-only names: the port and adapter `render`, `render_marks`, `_bake_canvas`, `postAuthorizedBlob`, `renderClipboardPng`, `COPY_IMAGE_MARKS_ERROR`, `loadClipboardPng`'s `variant`, `CAPTURE_COPY_IMAGE` | shared |
| WP-3 | 2, 3 | Red, then Green | shared |
| WP-4 | 5 | The 09, 11-page-layout and gui-index spec text | shared |
| WP-5 | 6 | Status and grouping | shared |
| WP-6 | H1, H2 | Gate, handoff, review, reflection, next prompt | compact_continue |

There is no row 4: this MEU has no fixture to regenerate.

## User Review Required

**Carried rulings:**
- D-158 (USER_EXPLICIT 2026-10-29 "all recommendations are accepted", grouping §8 `:141`) accepts the synthesis that 09 §Copy image and action names encodes.
- D-159 and D-160 (autonomous, Local Canon, `:142-143`) are carried, because the decision probe returns them.
- D-674 and D-675 (autonomous, grouping §9.8) set the session number and the crop rule.
- D-677 (human, A, USER_EXPLICIT 2026-11-12 "both recommendations accpeted", grouping `:203`): the filmstrip fetches `annotated` when saved marks exist, else `original`.
- D-678 (autonomous, Local Canon, grouping `:204`): Ctrl+C follows Session 61's PASTE_KEY pattern with no registry entry.

**Rulings at plan time.** None. The plan gate asks Mat one question through the HDP (D-698): the execution review budget, with the Session 60 RULE-5 figure of 32.5M as the recommendation and the ledger default as the do-nothing option, and his words to execute.

**Gate flags.** At the gate Mat also sees, each with a recommendation and its do-nothing option:
- D-689: the shared `_bake_canvas` and an in-memory encode, not a temp file;
- D-691: no MCP render action;
- D-693: "Save and flatten" saves and then flattens in one accept, which moves the MEU-67 and MEU-81 pins that hold Flatten disabled while dirty (§Pins that move);
- the AC-88.12 Electron test (`ui/tests/e2e/capture-filmstrip-actions.test.ts:246`) already writes the real clipboard. This session's gate doesn't run it, and this plan doesn't change it.

An AC or contract change during execution goes to Mat as a Decision Brief (S12). Its do-nothing option is "record it as a departure and keep the approved text".

**Network.** Recommendation: none, because nothing here fetches. The do-nothing option is the same. There is no brief.

**Token estimate.** Calibrated against:
- Session 61 `capture-paste` (PASTE_KEY, the model for COPY_KEY);
- Session 67: plan 10,193,204 over 2 rounds, execution 13,248,892 over 2 rounds;
- Session 68: plan 13,173,719 over 2 rounds, execution 13,213,554 in 1 round.

This session is one MEU across the port, adapter, service, route, client and page, plus a label sweep:
- plan review: about 11M for round 1 and about 5.5M for one recheck;
- execution review: about 13M for round 1, so the Session 60 RULE-5 figure is 32.5M (13M × 2 plus a recheck at about 6.5M).

**Word meanings.**
- *Render* is `POST /captures/{id}/render`: the posted marks baked over the original, returned as PNG bytes, with nothing written.
- *Current marks* are the editor's `annotationsRef.current`, saved or not. *Saved marks* are the sidecar's.
- *Dirty* is `CapturePage`'s `dirty` (`:459`): the current marks differ from the saved ones, or a text draft would commit.
- *As shown* is the MEU-136 rule: `annotated` when the shot has saved marks (`annotated_path` set), else `original`.
- *The editor copy* is the Copy image button and canvas Ctrl+C. *The filmstrip copy* is the thumbnail menu's Copy image (MEU-88).

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `RENDER_PORT` | `ImageAnnotatePort` gains `render(self, original_path: Path, annotations: Sequence[Annotation]) -> bytes`, after `bake` (D-689). | `ports/capture.py` |
| `RENDER_BAKE` | The adapter's `bake` body after the open moves into `_bake_canvas(self, canvas, annotations)`: `apply_region_pass`, then `self._apply` per mark, returning the canvas. `bake` keeps its signature and output bytes. `render` opens the file with `Image.open(...).convert("RGBA")`, maps `(UnidentifiedImageError, OSError)` to `InboxPathError("the image could not be opened")`, which names no path, runs `_bake_canvas`, and returns `_encode_view(canvas.convert("RGB"), ".png")`. It always returns PNG, whatever `annotated_format` says, and writes nothing (D-689). | `avkit_infra/capture/adapter.py` |
| `RENDER_SERVICE` | `CaptureService.render_marks(self, shot_id: str, annotations: Sequence[Annotation]) -> bytes` runs under `with CAPTURE_FILE_LOCK, self._uow_factory() as uow`. An unknown shot raises `NotFoundError(f"capture shot {shot_id} not found")`, and a missing original raises `NotFoundError("original image is missing")`. It clamps each mark with `self._clamp_annotation(item, shot.width, shot.height)`, calls `self._annotate.render(shot.original_path, clamped)` and returns its bytes. It writes no file, sidecar or row (D-695). | `services/capture.py` |
| `RENDER_ROUTE` | `@router.post("/{id}/render")` sits right after annotate (`routes/captures.py:445-452`) and before flatten (`:455`). It takes `AnnotateIn`, maps it with `_annotations_from_in(body.annotations)`, and returns `Response(content=..., media_type="image/png")` with status 200. It has no `IMAGE_MAX_BYTES` cap (D-695). `InboxPathError` gives 422 (`errors.py:33`) and `NotFoundError` 404. `openapi.committed.json` is regenerated. | `routes/captures.py`, `openapi.committed.json` |
| `RENDER_CLIENT` | `postAuthorizedBlob(path: string, body: unknown): Promise<Blob \| null>` mirrors `fetchAuthorizedBlob`: the same base and token seam, method POST, `Content-Type: application/json`, and `null` when `!res.ok`. `renderClipboardPng(id: string, annotations: readonly Annotation[]): Promise<Uint8Array>` checks the list with `parseAnnotateBody({annotations})` (null throws `COPY_IMAGE_MARKS_ERROR`), posts it to `` `/captures/${encodeURIComponent(id)}/render` `` and returns `toClipboardPng(blob, encodePng)`. | `capture-image.ts`, `capture-clipboard.ts` |
| `COPY_BUTTON` | `ACTION_BUTTONS['capture-copy-image'] = { icon: Copy, name: 'Copy image' }` sits after `capture-save` and before `capture-apply-image`. The page mounts it on every selected shot, with variant `ghost` and shortcut `Ctrl+C`, disabled unless `selected !== null && overlayReady && textDraft === null`. Its click runs `reportCopy(target, …)`: a missing `window.api.writeClipboardImage` throws `COPY_IMAGE_UNAVAILABLE`; otherwise it awaits `writeImage(await renderClipboardPng(target.id, annotationsRef.current))` and reports `Copied {display_name} as an image.` (D-690, D-696). | `capture-toolbar.ts`, `CapturePage.tsx` |
| `COPY_KEY` | `handleEditorKey` (`CapturePage.tsx:1637`) gains a Ctrl+C branch after the history block. It fires when `ctrlKey` or `metaKey` is set, `key.toLowerCase() === 'c'`, shift and alt are off, the event is not a repeat, `confirm === null`, `historyOwnsFocus()` holds, `isEditableTarget(event.target)` (`capture-import.ts:132`) is false, the window selection is collapsed, and the COPY_BUTTON enable rule holds. It then calls `preventDefault` and runs the button's copy. Recording, a text draft and crop return earlier. A text field keeps native copy, and no `copy` listener is added (D-692, D-678). | `CapturePage.tsx` |
| `FILMSTRIP_AS_SHOWN` | `loadClipboardPng(id: string, variant: 'original' \| 'annotated' = 'original')` fetches that variant. `onCopyImage` (`CapturePage.tsx:1794-1803`) passes `'annotated'` when `typeof target.annotated_path === 'string' && target.annotated_path.length > 0`, else `'original'` (D-677 A). | `capture-clipboard.ts`, `CapturePage.tsx` |
| `ACTION_LABELS` | The action names become `Save annotations`, `Flatten into image…` and `Restore backup…` (`capture-toolbar.ts:74-76`). The confirm strip's accept reads `Flatten into image`, or `Save and flatten` when dirty (`:1942`), and `Restore backup` (`:1949`). The Settings labels read `Back up the original before Flatten into image` (`SettingsPage.tsx:1056`) and `Save annotations format` (`:1086`). APPLY_TITLES.dirty reads `Save annotations first`, REVERT_DIRTY_TITLE reads `Save or discard unsaved marks first`, and `flattenStatus` reads `Flattened into image. Backup: X`, `Flattened into image (no backup).`, `Flattened into a new PNG copy: X.` and `Restored from X.` (D-694). | `capture-toolbar.ts`, `CapturePage.tsx`, `SettingsPage.tsx`, `capture-flatten.ts` |
| `SAVE_AND_FLATTEN` | `applyState` gains `currentCount` and `canSave`. Not dirty, it is unchanged (no saved marks gives `noMarks`, then the file type). Dirty, the first match wins: `currentCount < 1` gives `noMarks`; `!canSave` gives `APPLY_TITLES.dirty`; a file type that can't be flattened gives `fileType`; otherwise it is enabled. `flattenConfirmText` gains `unsaved: boolean`, which names the current marks and says they are saved first. Accepting a dirty flatten checks `canSaveRef.current`, then awaits `saveAnnotations()`. A `false` or a throw stops with the error shown and no flatten. On success it sets `saved` and `baked` as Save does, then calls `flattenCapture`. `revertState` stays disabled while dirty (D-693). | `capture-flatten.ts`, `CapturePage.tsx` |
| `COPY_HELP` | The help body (`capture-help-content.ts:22`) names Flatten into image, Restore backup and Save annotations. `:27` gains, before "Right-click a thumbnail", "Copy image, or Ctrl+C while the image has focus, copies the shot with its current marks, saved or not; a text field keeps its own copy." This also fixes the missing space in "marks.Right-click". | `capture-help-content.ts` |

### Pins that move

| Row | Test | Today | After |
|---|---|---|---|
| 2 | `tests/e2e/test_api_openapi.py` `ROUTE_INDEX` (annotate at `:57`) and its counts at `:122`, `:208`, `:253`, `:311` | 78 routes; annotate then flatten | render sits right after annotate; 79 routes (AC-104.8) |
| 2 | `tests/e2e/test_api_downloads.py:372` | `ROUTE_COUNT_AFTER = 78` | 79 |
| 2 | `mcp-server/tests/capture.test.ts:44` | `REST_ONLY = ["complete", "cancel", "register"] as const;` | `"render"` appended (AC-104.9, D-691) |
| 2 | `ui/tests/unit/capture-action-row.test.ts:43-51` (ACTIONS), `:45-47` (names), `:362` (AC-81.1 key order), `:406` (AC-81.2 dirty Apply disabled) | 'Save overlay', 'Apply to image', 'Revert image'; no copy; dirty Apply disabled | the new names; `capture-copy-image` after `capture-save`; the key order includes it; the dirty case follows SAVE_AND_FLATTEN |
| 2 | `ui/tests/unit/capture-flatten.test.ts:57`, `:60`, `:121-135` (the MEU-67 tests AC-67.20, AC-67.22, AC-67.23 and AC-67.33) | the `dirty` title, `REVERT_DIRTY_TITLE`, `flattenStatus` text | D-694 text; the dirty `applyState` rows follow SAVE_AND_FLATTEN |
| 2 | `ui/tests/unit/capture-page.behavior.test.ts:1325` | aria 'Save overlay' | 'Save annotations' |
| 2 | `ui/tests/unit/capture-page.behavior.test.ts:3846`, `:4044`, `:4078` | 'Apply to image — Save the overlay first' | the dirty case is enabled, or titled `Save annotations first` while `canSave` is false (SAVE_AND_FLATTEN) |
| 2 | `ui/tests/unit/capture-page.behavior.test.ts:3855`, `:3864`, `:3919`, `:3967`, `:4065` | the old accept, status and confirm text | D-694 text |
| 2 | `ui/tests/unit/capture-page.behavior.test.ts:3990`, `:4046`, `:4087` | the revert title `Save or discard overlay marks first` | `Save or discard unsaved marks first` |
| 2 | `ui/tests/unit/capture-page.test.ts:613-614` (settings labels), `:62-103` (WAVE9 lists), `:290`, `:313`, `:626-631` (source pins) | the old labels | the new labels; `capture-copy-image` in the list it belongs to |
| 2 | `ui/tests/unit/capture-help-content.test.ts:46` | the old action names | the new names |
| 2 | `ui/tests/e2e/capture-inbox.test.ts:754` | aria 'Save overlay' | 'Save annotations' |
| 2 | `ui/tests/e2e/capture-inbox.test.ts:1478`, `:1602`, `:1629` | the dirty Apply hint | SAVE_AND_FLATTEN |
| 2 | `ui/tests/e2e/capture-inbox.test.ts:1492`, `:1513`, `:1525`, `:1619` | the old status and accept text | D-694 text |

These don't move:
- `ui/tests/unit/tooltip.test.tsx` uses sample strings, so the absence grep excludes it;
- `ui/tests/unit/icon-hints.test.ts` pins none of these names;
- `ui/tests/unit/capture-crop-tool.behavior.test.ts:908` only checks that the two button maps are disjoint, which `capture-copy-image` keeps;
- the fake adapters at `tests/unit/test_capture_service.py:87` and `tests/unit/test_capture_export_service.py:111` are never called through `render`, so they need no method.

These keep the old words, and the absence grep excludes them:
- the command palette's `Save annotated capture` (`commandRegistry.ts:426`), which D-694 leaves alone;
- the known-issues and triage text;
- the docstrings and comments naming Save overlay (`domain/capture.py:45`, `services/capture.py:318`, `settings.ts:11`, `settings-schemas.ts:76`, `CaptureViewport.tsx:115`, `capture-commands.ts:137`).

Before writing, row 1 sweeps `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` for these names and records the hits in `s69-anchors.txt`:
- every caller of the bake path: `services/capture.py:1471` (annotate), `:1688` (crop), `:1861`, `:1907` (flatten and revert), `:1976` (export), `adapter.py:542` (`apply_region_pass`) and `tools/capture_bake_fixture.py:53`;
- every caller of `loadClipboardPng` (`CapturePage.tsx:48`, `:1800`) and of `fetchAuthorizedBlob` (`CaptureFilmstrip.tsx`, `capture-clipboard.ts`, `capture-image.ts`);
- every literal `Save overlay`, `Apply to image`, `Revert image`, `Save the overlay first` and `Save or discard overlay marks first`;
- every pin by name, order, adjacency or exact signature on the router, ROUTE_INDEX, the OpenAPI paths, `ACTION_BUTTONS`, `bake`, `render` and `loadClipboardPng`.

This follows Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1 and Session 66 RULE-1. A pin found there and missing from this table goes into the handoff as a departure. The plan-time sweep found the rows above.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| The render body's marks | the editor's `annotationsRef.current` through `parseAnnotateBody` | `AnnotateIn`, `_annotations_from_in`, the domain dataclasses, the clamp, `_bake_canvas` | the same models as annotate, so a lone surrogate, empty text, an extra field and a bad type give the same 422 as annotate, control characters pass both routes as annotate accepts them (D-699), and no response, log or Console line echoes the value (AC-104.7) |
| The rendered bytes | `_encode_view` | the route's `Response`, `postAuthorizedBlob`, `toClipboardPng`, `writeClipboardImage` | PNG only; held in memory; never written to disk or logged |
| The filmstrip variant | `annotated_path` on the shot row | `loadClipboardPng` | `annotated` only when the path is a non-empty string |
| An unreadable original | the file on disk | `render` | `InboxPathError("the image could not be opened")`, which names no path |

These functions sit between Ctrl+C and the clipboard, and AC-104.11 traces one unsaved mark through all of them with recording fakes (Session 55 RULE-3): the window keydown listener, `handleEditorKey`, `renderClipboardPng`, `postAuthorizedBlob` (the recorded POST body), `toClipboardPng` and `window.api.writeClipboardImage` (the recorded bytes). AC-104.10 traces the Python half: `AnnotateIn`, `_annotations_from_in`, `render_marks`, `_clamp_annotation`, the adapter's `render` and `_bake_canvas`.

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/09-screenshot-capture.md` | `:103` the mock reads `[Save annotations]`. A route row `POST /captures/{id}/render` goes after `:528` (annotate): 200 `image/png`, body `{ "annotations": [ ... ] }`, writes nothing. `:610` reads "Back up the original before Flatten into image". `:664` and `:704` use the new names. `:672` reads "Save annotations format" and "when Save annotations runs". `:799` names the as-shown rule (D-677 A). A `> **Delivered (Session 69).**` note goes after the rule table (`:955`), naming the mechanism ids, AC-104.1 to AC-104.23 and the plan folder. |
| `docs/build-plan/11-page-layout.md` | `:93` names Flatten into image and Restore backup. `:41` CP1 reads "Save annotations". |
| `docs/build-plan/gui-actions-index.md` | `:74` `capture:save` reads "Save annotations / Ctrl+S". `:79` `capture:copy_image` changes only its description column; its IPC cell stays exactly `` IPC `writeClipboardImage` ``, which AC-88.11 parses with `` ^IPC `([A-Za-z]+)`$ ``. A new row `capture:copy_shot` "Copy image button / Ctrl+C (editor, current marks)" goes after it, with backend `` `POST /captures/{id}/render` then IPC `writeClipboardImage` ``. `:82` and `:83` read "Flatten into image…" and "Restore backup…". |

The MCP action table at 09 `:583` doesn't change (D-691).

### MEU-104 `capture-copy-image-actions`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `POST /captures/{id}/render` | `AnnotateIn` | the annotate models: an unknown field, a bad type or a refused value gives 422 in the error envelope; an unknown shot or a missing original gives 404; an unreadable original gives 422 with no path |
| MCP | none | `avkit_capture` gains no render action (D-691); `REST_ONLY` names it |
| Electron IPC `writeClipboardImage` | PNG bytes from the renderer | unchanged (MEU-88): main decodes the PNG with `nativeImage` |
| GUI | the editor's current marks | not a trust boundary; the server refuses what `parseAnnotateBody` let through |

The OpenAPI snapshot gains the render path. The MCP audit baseline is keyed by tool, action and status, and MCP gains no action, so the baseline doesn't change and the gate's scope check refuses the file.

**Input matrix (Session 64 RULE-1).** These cases come from reading the files named in each row at `b3f3933`:

| Marks | Original | Focus | Expected |
|---|---|---|---|
| none | PNG RGBA, JPEG, WebP | canvas | render posts `[]`; the clipboard gets the original as an RGB PNG, equal to `adapter.bake([])`'s PNG |
| saved only | PNG RGBA, JPEG, WebP | canvas | render posts the saved list; the bytes equal the PNG that Save wrote for the same marks |
| unsaved | PNG RGBA, JPEG, WebP | canvas | render posts the current list; the bytes equal annotate's PNG for that list, and the shot, sidecar and files stay unchanged |
| any | any | a text field (input, textarea, contenteditable) | no render; no `preventDefault`; native copy |
| any | any | canvas with a non-collapsed selection, a repeat, Shift or Alt held, the confirm strip open | no render |
| any | any | the Copy image button | as the canvas row for that marks state |
| any | a missing or unreadable file | canvas or button | 404 or 422; `copyErrorMessage` names no path; no clipboard write |

The `annotated_format` setting (PNG, JPEG or WebP) never changes render's output, which is always PNG.

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-104.1 | type | The exact signatures: `ImageAnnotatePort.render(self, original_path, annotations)`, the adapter's `render` and `_bake_canvas(self, canvas, annotations)`, `CaptureService.render_marks(self, shot_id, annotations)`, `postAuthorizedBlob(path, body)`, `renderClipboardPng(id, annotations)` and `loadClipboardPng(id, variant = 'original')` (Session 66 RULE-1) | Local Canon: D-689 | passes where row 2 writes it (row 1 adds the names) |
| AC-104.2 | behaviour | RENDER_BAKE: over no marks and over a region mark plus a drawn mark, on a PNG RGBA, a JPEG and a WebP original, `render`'s bytes equal the PNG that `bake` writes for the same marks; the no-marks case compares with `bake([])` | Spec: 09 Copy image row (bakes exactly as Save would) | a WebP `annotated_format` still gives PNG bytes |
| AC-104.3 | behaviour | `render` writes nothing (the folder's listing and mtimes are unchanged), and an unreadable original raises `InboxPathError` whose message names no path | Spec: 09 Copy image row (without writing a file); Session 50 RULE-1 | — |
| AC-104.4 | behaviour | RENDER_SERVICE: `render_marks` clamps a mark past the edge as annotate does, writes no file, sidecar or row, and raises `NotFoundError` for an unknown shot and for a missing original | Local Canon: D-695 | — |
| AC-104.5 | behaviour | `render_marks` holds `CAPTURE_FILE_LOCK` while it calls the adapter (a recording adapter reads the lock's state) | Local Canon: D-695 | — |
| AC-104.6 | behaviour | RENDER_ROUTE: POST render gives 200 `image/png` whose bytes equal the annotated file that annotate writes for the same body in PNG format; after the render the shot row, sidecar and folder are unchanged | Spec: 09 Copy image row | — |
| AC-104.7 | behaviour | render gives the same status as annotate for each case, with one parametrize id per case: a lone surrogate and empty text in a text mark, an extra field and a bad type each give 422 from both; control characters in a text mark give 200 from both, and render's bytes equal annotate's PNG (D-699); an unknown shot gives 404; no response body echoes the refused value | Session 53 RULE-1; Session 50 RULE-1; Human-approved: D-699 | each case is its own id |
| AC-104.8 | behaviour | The live OpenAPI schema lists `POST /captures/{id}/render` right after annotate in its paths, and the committed snapshot carries it with `image/png` and an entry equal to the live one (the snapshot's keys are sorted, D-700); ROUTE_INDEX lists it right after annotate, and the route count is 79 (Session 63 RULE-1) | Spec: 09 Copy image row; Human-approved: D-700 | an adjacency pin |
| AC-104.9 | guard | MCP `REST_ONLY` names `render`, and `avkit_capture` has no render action | Local Canon: D-691 | passes at baseline once row 2 edits the list |
| AC-104.10 | behaviour | One unsaved mark traced from the API body through `_annotations_from_in`, `render_marks`, `_clamp_annotation` and the adapter's `_bake_canvas` (recording wrappers) to the response's pixels | Session 55 RULE-3 | the wrapper records the mark exactly once |
| AC-104.11 | behaviour | One unsaved mark traced from a Ctrl+C keydown on the canvas through `handleEditorKey`, the recorded POST to `/captures/{id}/render` (its body holds that mark) and `toClipboardPng`, to the recording fake `writeClipboardImage`, which receives exactly the bytes the fake server returned | Session 55 RULE-3; Spec: 09 Copy image row | the fake is called once |
| AC-104.12 | behaviour | COPY_KEY: each guard row of the input matrix (text field, selection, repeat, Shift, Alt, confirm open, no shot, overlay not ready, crop, text draft) makes no POST and no `preventDefault`; Ctrl+C and Cmd+C on the canvas each make one | Spec: 09 Copy image row (text fields keep native copy); D-678 | the text-field case leaves `defaultPrevented` false |
| AC-104.13 | behaviour | COPY_BUTTON: the Copy image button sits between Save annotations and Flatten into image when dirty, and before Flatten when not; its tooltip reads `Copy image (Ctrl+C)`; it is disabled with no shot, before the overlay loads and with a text draft open; a click posts the current marks, saved or not | Local Canon: D-696 | an adjacency pin on the action row |
| AC-104.14 | behaviour | A copy error (render refused, `writeClipboardImage` missing, the fake throwing, `COPY_IMAGE_MARKS_ERROR`) shows `copyErrorMessage`'s text, names no path, and writes nothing | Local Canon: MEU-88 copy errors | — |
| AC-104.15 | behaviour | FILMSTRIP_AS_SHOWN: the filmstrip copy fetches `variant=annotated` for a shot with a non-empty `annotated_path` and `variant=original` for `null` and `''` | Spec: 09 Filmstrip row; D-677 A | the `''` case fetches original |
| AC-104.16 | behaviour | ACTION_LABELS: the action row's aria-labels and the confirm accepts read the new names, and a grep of `ui/src` outside comment lines (`//`, `/**`, ` *`) finds no `Save overlay`, `Apply to image` or `Revert image` (Session 61 RULE-3); the comments at `CaptureViewport.tsx:115`, `capture-commands.ts:137`, `capture-flatten.ts:2` and `settings-schemas.ts:76` keep them | Spec: 09 Labels row | the absence grep |
| AC-104.17 | behaviour | SAVE_AND_FLATTEN: `applyState` gives each row of its rule (not dirty with and without saved marks; dirty with no current marks, with `canSave` false, with an unflattenable file type, and enabled) | Local Canon: D-693 | the dirty and `canSave` false row is disabled |
| AC-104.18 | behaviour | Accepting a dirty flatten (`Save and flatten`) posts annotate before flatten, in that order; a save that returns `false` or throws posts no flatten and shows the error | Spec: 09 Labels row (Save and flatten); D-693 | the failed save makes no flatten call |
| AC-104.19 | behaviour | The status lines, the confirm text (clean and dirty), APPLY_TITLES.dirty and REVERT_DIRTY_TITLE read the D-694 literals (Session 68 RULE-2) | Local Canon: D-694 | — |
| AC-104.20 | behaviour | COPY_HELP: the help body names Copy image and Ctrl+C with the current marks and the text-field rule, the three new action names, and no `marks.Right-click` | Local Canon: D-694 | — |
| AC-104.21 | check | Spec D3: 09's mock, route row, `:610`, `:664`, `:672`, `:704`, `:799` and the Delivered note; 11-page-layout `:41` and `:93`; the gui-index rows, with the `capture:copy_image` IPC cell unchanged. Each file keeps CRLF endings | Local Canon: D3 | row 5's check exits 1 before row 5 |
| AC-104.22 | behaviour | Electron: on the capture page the action row shows `Save annotations` when dirty, `Copy image`, and `Flatten into image…`; the flatten confirm accepts with `Save and flatten` when dirty. No step writes the system clipboard | Spec: 09 Labels and Copy image rows | — |
| AC-104.23 | guard | `RESERVED_CHORDS` (`shortcuts.ts:137`) holds Ctrl+C, and the command registry has no copy entry | Local Canon: D-678 | passes at baseline and after |

**Guards.** These pass after rows 1 and 3:
- Python: `tests/unit/test_capture_adapter.py`, `tests/unit/test_capture_service.py`, `tests/unit/test_capture_export_service.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_flatten.py` and `tests/e2e/test_api_capture_export.py`;
- MCP: `mcp-server/tests/capture.test.ts`;
- UI: every capture Vitest file named in §Pins that move, and `ui/tests/unit/capture-crop-tool.behavior.test.ts`.

**Spec sufficiency.** Every 09 §Copy image and action names rule has an AC:

| Rule | ACs |
|---|---|
| Copy image | AC-104.2 to .14, .22 |
| Labels | AC-104.16 to .20, .22 |
| Filmstrip | AC-104.15, .23 |

### Files Modified

The endings come from `C:/Temp/av-kit/s69/endings-plan.txt`; row 0 records them again, with SHA-256, in `s69-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/ports/capture.py` (`RENDER_PORT`) | CRLF | 1 |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` (`RENDER_BAKE`) | CRLF | 1, 3 |
| `packages/core/src/avkit_core/services/capture.py` (`RENDER_SERVICE`) | CRLF | 1, 3 |
| `packages/api/src/avkit_api/routes/captures.py` (`RENDER_ROUTE`) | CRLF | 3 |
| `openapi.committed.json` | CRLF | 3 |
| `ui/src/renderer/src/features/capture/capture-image.ts`, `capture-clipboard.ts` (`RENDER_CLIENT`, `FILMSTRIP_AS_SHOWN`) | CRLF | 1, 3 |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` (`COPY_BUTTON`, `ACTION_LABELS`) | CRLF | 3 |
| `ui/src/renderer/src/features/capture/capture-flatten.ts` (`SAVE_AND_FLATTEN`, `ACTION_LABELS`) | CRLF | 3 |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` (`COPY_BUTTON`, `COPY_KEY`, `FILMSTRIP_AS_SHOWN`, `ACTION_LABELS`, `SAVE_AND_FLATTEN`) | CRLF | 3 |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` (`COPY_HELP`) | CRLF | 3 |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` (`ACTION_LABELS`) | CRLF | 3 |
| `ui/tests/e2e/test-ids.ts` (the MEU-104 block, after the MEU-103 block at `:507`) | CRLF | 1 |
| `tests/e2e/test_api_openapi.py`, `tests/e2e/test_api_downloads.py`, `mcp-server/tests/capture.test.ts` | CRLF | 2 |
| `ui/tests/unit/capture-flatten.test.ts`, `capture-action-row.test.ts`, `capture-page.behavior.test.ts`, `capture-page.test.ts`, `capture-help-content.test.ts` | CRLF | 2 |
| `ui/tests/e2e/capture-inbox.test.ts` | LF | 2 |
| `tests/unit/test_capture_render.py`, `tests/e2e/test_api_capture_render.py`, `ui/tests/unit/capture-copy-image.behavior.test.ts` (new) | LF | 2 |
| `docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/11-page-layout.md`, `docs/build-plan/gui-actions-index.md` | CRLF | 5 |

Before it writes, each row measures the file's endings with Python bytes, and then writes in that ending. A scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3).

**Byte-hash guard (Session 50).** AC-51.6 and AC-81.13 hash `ui/tests/e2e/test-ids.ts` up to `// MEU-51 primitive harness IDs.` (`:292`). Row 1 appends `// MEU-104 Capture copy image (additive IDs).` and `CAPTURE_COPY_IMAGE = 'capture-copy-image'` after the MEU-103 block (`:507`), which sits after the hashed prefix, so the expected hash `6E569F82…FF454` stays unchanged. Row 1 runs `ui/tests/unit/capture-action-row.test.ts` as its own check and names the hash it reads in the handoff.

### Project files

These project files are written:
- `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF) and `docs/BUILD_PLAN.md` (LF);
- the grouping file (CRLF; tracker row 45 at `:123`);
- the handoff, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| An MCP render action | D-691: an MCP client has no clipboard, and annotate already returns the baked file |
| A `copy` event listener or a registry entry for Ctrl+C | D-678, D-692 |
| Copying the Annotated view's file in the editor | D-690: the editor copy always renders the current marks |
| The command palette's `Save annotated capture` label | D-694 |
| Renaming the API, MCP action names or settings keys (`annotate`, `flatten`, `revert`, `capture.flatten_backup`, `capture.annotated_format`) | 09 Labels row names GUI text only |
| A render size cap | D-695 |
| Changing the AC-88.12 Electron test, which writes the real clipboard | Session 69 prompt; flagged to Mat at the gate |
| Multiline text (MEU-102) | Session 70 |
| Members-only URLs or ids, `npm run dist`, the live MCP audit | Session 69 prompt |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after rows 6 and H2-2. MEU-104 is `pending`, with its dependencies MEU-81 and MEU-99 `approved` (`.agent/context/meu-status.yaml:2719`).

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the budget and execute words, each with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** Checks that MEU-81, MEU-99 and MEU-103 are `approved`, that MEU-104 is `pending`, and that `b3f3933` is an ancestor of `HEAD`.
3. **Shapes (S7, Session 61 RULE-3).** Checks by name the 41 shapes this plan relies on:
   - `ImageAnnotatePort.bake`, the adapter's `bake`, `_encode_view`, `_write_png` and `apply_region_pass`;
   - `CaptureService.annotate`, `_clamp_annotation` and `CAPTURE_FILE_LOCK`;
   - the annotate and flatten routes, `AnnotateIn` and `_annotations_from_in`;
   - `fetchAuthorizedBlob`, `toClipboardPng`, `encodePng`, `loadClipboardPng` and the copy error constants;
   - `applyState`, `revertState`, `flattenConfirmText`, `flattenStatus`, `APPLY_TITLES` and `REVERT_DIRTY_TITLE`;
   - `ACTION_BUTTONS` with the three old names, `handleEditorKey`, `historyOwnsFocus`, `isEditableTarget`, `reportCopy`, `onCopyImage`, `canSave` and the confirm accepts;
   - the two Settings labels, the help sentences, `RESERVED_CHORDS`'s Ctrl+C, the test-ids hash boundary and the MEU-103 block;
   - 09's anchor and the gui-index `capture:copy_image` row.

   It then checks that none of `/render`, `render_marks`, `def render(`, `def _bake_canvas`, `renderClipboardPng`, `postAuthorizedBlob`, `capture-copy-image`, `CAPTURE_COPY_IMAGE`, `Save annotations`, `Flatten into image`, `Restore backup` and `Save and flatten` appears in the 15 target files, and that the three new files don't exist.
4. **Records.** Creates `C:\Temp\av-kit\s69\tmp`. Records `baseline.sha`, `baseline-dirty.txt` (each dirty path's porcelain line and SHA-256) and `s69-anchors.txt` (every target's endings and SHA-256). It hashes `docs/proposals/2026-11-10-download-logic-divergence-report.md` and never opens it.
5. **Installs.** Installs from the lock with `uv sync --frozen --offline --all-packages` and proves that both `node_modules` trees match their locks (S4).
6. **FFmpeg pair.** Checks the pinned FFmpeg pair, as the identity script binds it.
7. **Base runs.** Captures the base Python, UI and MCP suites, the UI build, the capture Electron spec and `ruff check packages/ tests/`. These are recorded and are not fatal.
8. **Selftests.** Runs the `red-check.py`, `identity.py` and `id-length.py` selftests, each on its own fixtures (Session 56 RULE-4).

At `b3f3933` the shapes and queue blocks ran alone with exit 0 (`C:/Temp/av-kit/s69/shapes-dry.txt`).

### 2. Type-only first, then Red, then Green

**Row 1 (Session 53 RULE-2)** adds the names with no behaviour:
- `ImageAnnotatePort.render`;
- the adapter's `_bake_canvas`, extracted from `bake` with `bake`'s bytes unchanged, and a `render` stub that returns `b""`;
- `CaptureService.render_marks`, a stub that returns `b""`;
- `postAuthorizedBlob`, a stub that returns `null`; `renderClipboardPng`, a stub that returns an empty `Uint8Array`; `COPY_IMAGE_MARKS_ERROR`;
- `loadClipboardPng`'s `variant` parameter, which the stub ignores (it still fetches `original`);
- `CAPTURE_COPY_IMAGE` in `test-ids.ts`.

Each stub is wrong, so the Red tests fail by assertion, not by a missing name. Row 1 runs `test_capture_adapter.py` (the extraction) and `capture-action-row.test.ts` (the hash) on their own.

**Row 2 (Red)** requires only new-behaviour tests (Session 66 RULE-2):
- pytest: AC-104.2 to .8 and .10;
- Vitest: AC-104.11 to .20;
- Playwright: AC-104.22.

These are not in the Red list:
- AC-104.1 tests what row 1 adds, so it must pass where it is written.
- AC-104.9 and AC-104.23 are guards that pass throughout.
- AC-104.21 is row 5's check.

**Red-check (Session 50).** A Red row passes only when `red-check.py` reads each receipt and names each failing required test as an assertion failure. A required test that fails on a missing name is refused (the `pytest-required-ac-104-4-stub-name` fixture). Every Red test:
- asserts that a name exists before it patches or calls it (Session 52 RULE-4);
- catches a domain exception and asserts its type (Session 62 RULE-3);
- asserts length or membership before indexing (Session 62 RULE-3);
- in Electron, asserts `await expect(locator).toBeVisible()` before it clicks.

`id-length.py` checks every new pytest id against red-check's header width of 71 characters (Session 67 RULE-4). Row 2 runs `ruff check` on the two new pytest files (Session 68 RULE-4).

**Rows 3 and 5 (Green)** change no test file.

### Plan-local scripts

The folder's `baseline.ps1`, `red-check.py`, `identity.py`, `id-length.py` and `session-gate.ps1` are adapted from Session 68's, with the `s69` names and this plan's paths. Session 68's `assert-never-probe.py` is not carried: no union grows.

| Script | What it does | Plan-time result |
|---|---|---|
| `id-length.py` | checks pytest id widths | selftest: 4 cases, 0 wrong (`C:/Temp/av-kit/s69-plan-idlen-selftest.txt`) |
| `red-check.py` | reads the Red receipts | selftest: 49 fixtures, 0 wrong (`C:/Temp/av-kit/s69-plan-rc-selftest.txt`); this includes the AC-104.1 boundary against AC-104.10 to AC-104.19 and the stub-name refusal |
| `identity.py` | binds the tested state | selftest: 0 failures (`C:/Temp/av-kit/s69-plan-identity-selftest.txt`) |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s69-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright, `ruff check packages/ tests/`, UI typecheck and lint, `lint_task_contract.py`, the scope-paths check (S3; the MCP audit baseline is refused), the `red-check.py` selftest, `id-length.py` on the two new pytest files |
| Byte-hash guard | `npm --prefix ui run test -- tests/unit/capture-action-row.test.ts` on its own |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s69\tmp`; only the Python ids that the base receipt shows failing are excused), `export_openapi.py --check` (AC-104.8), the whole UI suite and build, the MCP typecheck, build and suite, `meu_status.py render --check`, `issue_triage.py render --check` |
| Runtime | the capture Electron spec `ui/tests/e2e/capture-inbox.test.ts` (AC-104.22) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | `mcp-audit` (network and the installed servers), `build-record` (no release and no package build) |

The counts at the Session 68 gate were Python 2435, UI 1303, MCP 526 and Electron 46. The handoff copies this session's counts from the receipts (Session 63 RULE-2).

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop; a moved pin goes into the handoff as a departure, and to Mat if it changes an AC (S12) |
| S3 | `HEAD` moves, or a path outside this plan and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network, or writes the system clipboard | stop |
| S6 | A raw value (a path, a refused mark's text) reaches a log, stdout, a response body or the Console | fix it in the row or ask (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the budget or execute words | stop at row 0 |
| S10 | Codex is unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file is dirty from another session | copy it to `C:/Temp/av-kit/s69/pre-status/`, byte-edit only this session's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to Mat as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs (a port, a file lock) | stop and ask Mat; never stop another program (Session 57 RULE-4) |

## Decision Log

> [!WARNING]
> D-689 to D-697 are autonomous, and each lists its alternatives in `reasoning`. D-698 records Mat's ruling at the plan gate, D-699 his execution ruling on AC-104.7 (row 2), and D-700 his execution ruling on AC-104.8 (row 3; no D-70x id existed in the repo when it was taken). D-689 to D-698 were free at plan time (`C:/Temp/av-kit/s69/id-probe.txt`).
>
> Carried, and not relisted in the block:
> - D-158: human, `USER_EXPLICIT 2026-10-29 "all recommendations are accepted"`, grouping §8 `:141`;
> - D-159: autonomous, Local Canon, `:142`;
> - D-160: autonomous, Local Canon, `:143`;
> - D-674 and D-675: autonomous, stage `grouping`, §9.8;
> - D-677: human, A, `USER_EXPLICIT 2026-11-12 "both recommendations accpeted"`, `:203`;
> - D-678: autonomous, Local Canon, `:204`.
>
> The reflection carries these and every id the decision probe returns (Session 54 RULE-5). At plan time the probe (`C:/Temp/av-kit/s69-plan-decision-probe.txt`), with this plan and the grouping as sources, returned 12 decisions: D-689 to D-697 `planning` and D-158 to D-160 `grouping`. Without the grouping it refuses (HDP-18). It reads only the grouping's §8, so D-674, D-675, D-677 and D-678 (§9.8) are carried by hand. Each source's SHA-256 was unchanged by the run.

```yaml
decision_log:
  - id: D-689
    stage: planning
    question: "What does 'bakes through MEU-136's path' mean for render?"
    resolution: autonomous
    class: two-way
    chosen: "The adapter's bake body after the open becomes _bake_canvas (region pass, then the drawn marks), shared by bake and render; render encodes the canvas in memory with _encode_view as PNG, the encoder MEU-128's view uses, and returns the bytes"
    source_tag: Local Canon
    precedents:
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:526-547 - bake opens, runs apply_region_pass and _apply, then writes"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:291-305 - _encode_view encodes in memory (MEU-128)"
      - "C:/Temp/av-kit/s69/pngeq/out.txt - _encode_view's PNG bytes equal _write_png's for the same canvas"
    research:
      engine: none
      sources: []
    reasoning: "One function for the marks means render can't drift from Save. Baking to a temp file and reading it back lost: it writes a file, which the Copy image row forbids, and adds a cleanup path. Copying the bake loop into render lost: two copies of the order rule. Two-way."
    human_message_reference: null
  - id: D-690
    stage: planning
    question: "Does the editor copy ever skip render?"
    resolution: autonomous
    class: two-way
    chosen: "The Copy image button and canvas Ctrl+C always post the current marks to render, including an empty list and a list equal to the saved one"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:951 - the current, possibly unsaved, marks, rendered by POST render"
    research:
      engine: none
      sources: []
    reasoning: "One path is one set of tests. Fetching the annotated file when not dirty lost: a JPEG or WebP annotated_format would copy lossy bytes that differ from what render gives, and the editor would have two sources. Two-way."
    human_message_reference: null
  - id: D-691
    stage: planning
    question: "Does MCP get a render action?"
    resolution: autonomous
    class: two-way
    chosen: "No; REST_ONLY names render, and the MCP audit baseline is unchanged"
    source_tag: Local Canon
    precedents:
      - "mcp-server/tests/capture.test.ts:44 - REST_ONLY lists routes MCP doesn't expose"
      - "docs/build-plan/09-screenshot-capture.md:951 - the rule is a GUI copy"
    research:
      engine: none
      sources: []
    reasoning: "An MCP client has no clipboard, and annotate already returns the baked file's path. A render action lost: it returns image bytes over a text protocol and grows the audit baseline for no user. Two-way."
    human_message_reference: null
  - id: D-692
    stage: planning
    question: "Where does canvas Ctrl+C live?"
    resolution: autonomous
    class: two-way
    chosen: "A branch in handleEditorKey after the history block, guarded by historyOwnsFocus, isEditableTarget, a collapsed selection and the button's enable rule; no copy event listener"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:529-561 - PASTE_KEY"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1637 - handleEditorKey, reached once per key"
      - "grouping :204 - D-678, Ctrl+C follows PASTE_KEY with no registry entry"
    research:
      engine: none
      sources: []
    reasoning: "handleEditorKey already owns the canvas chords and their early returns for crop, recording and text drafts. A window copy listener lost: it fires for every copy in the app and needs its own focus rules. A registry entry lost: D-678. Two-way."
    human_message_reference: null
  - id: D-693
    stage: planning
    question: "What does 'the dirty-flatten confirm offers Save and flatten' do?"
    resolution: autonomous
    class: two-way
    chosen: "Flatten is enabled while dirty when the current marks are savable; its confirm names the current marks and accepts with Save and flatten, which saves, then flattens; a failed save flattens nothing; Restore backup stays disabled while dirty"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:952 - the Labels row"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:2022 - saveOverlay's save and state updates"
    research:
      engine: none
      sources: []
    reasoning: "The row asks for a dirty-flatten confirm, which can only open if Flatten is enabled while dirty. Keeping Flatten disabled while dirty lost: the confirm could never offer Save and flatten. Flattening the saved marks and dropping the unsaved ones lost: it loses work silently. This moves the MEU-67 and MEU-81 dirty-disabled pins, which the gate flags to Mat. Two-way."
    human_message_reference: null
  - id: D-694
    stage: planning
    question: "Which text follows the new names?"
    resolution: autonomous
    class: two-way
    chosen: "The action names, confirm accepts, Settings labels, APPLY_TITLES.dirty, REVERT_DIRTY_TITLE, flattenStatus, the help body and the spec docs; not the command palette's Save annotated capture, the API or MCP names, the settings keys or code comments"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:952 - the action row's names"
      - "ui/src/renderer/src/registry/commandRegistry.ts:426 - the palette label"
    research:
      engine: none
      sources: []
    reasoning: "Every place a user reads the action's name says the same words. Renaming the palette entry lost: the row names the action row, and the palette is a separate surface with its own pins. Renaming API or setting keys lost: it breaks clients for a label change. Two-way."
    human_message_reference: null
  - id: D-695
    stage: planning
    question: "Does render cap its size, and does it lock?"
    resolution: autonomous
    class: two-way
    chosen: "No IMAGE_MAX_BYTES cap; render_marks holds CAPTURE_FILE_LOCK while it reads the original and bakes"
    source_tag: Local Canon
    precedents:
      - "packages/api/src/avkit_api/routes/captures.py - the image route caps a file it streams at 15 MiB"
      - "packages/core/src/avkit_core/services/capture.py:1471 - annotate bakes under the lock"
    research:
      engine: none
      sources: []
    reasoning: "The cap guards streaming an arbitrary file; render's bytes are a re-encode of a shot annotate can already bake, and a cap would make Copy fail on a large shot that Save handles. The lock keeps a flatten or revert from swapping the original mid-read. Reading without the lock lost: a torn read under a concurrent flatten. Two-way."
    human_message_reference: null
  - id: D-696
    stage: planning
    question: "Where does the Copy image button sit and when is it enabled?"
    resolution: autonomous
    class: two-way
    chosen: "ACTION_BUTTONS capture-copy-image (Copy, Copy image) after capture-save and before capture-apply-image; variant ghost; shortcut Ctrl+C; mounted for every selected shot; enabled when a shot is selected, its overlay has loaded and no text draft is open"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-toolbar.ts:72-80 - ACTION_BUTTONS in ACTION_ORDER"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:681 - overlayReady is set once the marks load"
    research:
      engine: none
      sources: []
    reasoning: "Next to Save, the button reads as acting on the same marks. Before the overlay loads the current marks are an empty list, which would copy the bare image; an open text draft isn't a mark yet. Placing it in the filmstrip menu only lost: the row asks for a button in the editor. Two-way."
    human_message_reference: null
  - id: D-697
    stage: planning
    question: "How is the copy tested without the system clipboard?"
    resolution: autonomous
    class: two-way
    chosen: "Vitest uses a recording fake for window.api.writeClipboardImage and a fake server for render; pytest compares render's bytes with bake's; the Electron spec checks labels, mounting and the confirm accept only, and never clicks Copy image"
    source_tag: Local Canon
    precedents:
      - "Session 57 RULE-4 - no test touches the system clipboard"
      - "Session 55 RULE-3 - trace with a recording fake"
    research:
      engine: none
      sources: []
    reasoning: "The bytes are proved equal to Save's in Python and carried unchanged to the fake in Vitest, which covers the whole path except main's nativeImage decode that MEU-88 already tests. A live Electron copy lost: it writes Mat's clipboard. Two-way."
    human_message_reference: null
  - id: D-698
    stage: planning
    question: "What is the execution review budget, and does execution start?"
    resolution: human
    class: two-way
    chosen: "Execution review budget 50M with the default cap of 6 rounds; execute now that the plan review has approved"
    recommendation: "An execution review budget of 32.5M (the round 1 estimate of 13M twice plus a 6.5M recheck, Session 60 RULE-5) with the default cap of 6"
    source_tag: Human-approved
    precedents:
      - "Session 69 prompt - at the plan gate, ask for the execution budget"
      - "GUARDRAILS.md SIGN 3 - direct human execution authorization satisfies the plan-to-execution gate"
    research:
      engine: none
      sources: []
    reasoning: "Mat gave the budget and the execution words at the plan gate after the round 1 approval. The ledger still stops the loop at 6 rounds and before a round that would overrun 50M. The do-nothing option, the ledger default of 21M, was not chosen."
    human_message_reference: "USER_EXPLICIT 2026-11-13 '50M, execute'"
  - id: D-699
    stage: execution
    question: "AC-104.7 lists control characters in a text mark as a 422, but annotate accepts them with 200 at b3f3933. How should AC-104.7 read (row 2)?"
    resolution: human
    class: two-way
    chosen: "Parity with annotate: a lone surrogate, empty text, an extra field and a bad type give 422 from both routes; control characters give 200 from both, and render's bytes equal annotate's PNG; no product change"
    recommendation: "Parity with annotate, with the control-character case asserting 200 from both routes and no echo"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s69/probe-text.txt - annotate at b3f3933: lone-surrogate 422, control-chars 200, nul 200, empty 422, extra-field 422, bad-type 422"
      - "packages/api/src/avkit_api/schemas/captures.py:112 - TextAnnotationIn checks only the text's min and max length"
      - "Session 59 RULE-3 - an AC change goes to Mat as a Decision Brief"
    research:
      engine: none
      sources: []
    reasoning: "AC-104.7's rule is the same status as annotate, and its list wrongly put control characters among the 422 cases. Refusing control characters in both routes lost: it changes annotate's accepted input, which 09 does not ask for, and saved sidecars may hold such text. Leaving the AC as written, the do-nothing option, lost: the test could not pass without breaking parity. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-13 'Parity (Recommended)'"
  - id: D-700
    stage: execution
    question: "AC-104.8 puts render right after annotate in the committed OpenAPI snapshot, but tools/export_openapi.py writes it with sort_keys, so crop, export, flatten and image sit between them. How should AC-104.8 read (row 3)?"
    resolution: human
    class: two-way
    chosen: "The adjacency pin checks the live schema and ROUTE_INDEX; the committed snapshot carries render with image/png and its entry equals the live one; the route count stays 79"
    recommendation: "Adjacency on the live schema and ROUTE_INDEX, with the committed entry equal to the live one"
    source_tag: Human-approved
    precedents:
      - "tools/export_openapi.py:58 - render_openapi dumps with sort_keys=True"
      - "Session 59 RULE-3 - an AC change goes to Mat as a Decision Brief"
    research:
      engine: none
      sources: []
    reasoning: "The live schema keeps route order, so the pin still proves render sits after annotate in the router. Dropping sort_keys from the exporter lost: it reorders the whole committed file and changes a tool outside MEU-104. Leaving the AC as written, the do-nothing option, lost: its test cannot pass. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-13 'Live + index (Recommended)'"
```

## Research References

- No web research: every rule comes from 09, the grouping's §8 and §9, and the code at `b3f3933`.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s69/id-probe.txt` | D-689 to D-698 and the AC-104 family were free |
| `C:/Temp/av-kit/s69/endings-plan.txt` | the targets' line endings |
| `C:/Temp/av-kit/s69/pngeq/out.txt` | `_encode_view`'s PNG bytes equal `_write_png`'s for the same canvas |
| `C:/Temp/av-kit/s69/shapes-dry.txt` | `baseline.ps1`'s shapes and queue blocks run alone at `b3f3933` (exit 0) |
| `C:/Temp/av-kit/s69-plan-rc-selftest.txt`, `C:/Temp/av-kit/s69-plan-identity-selftest.txt`, `C:/Temp/av-kit/s69-plan-idlen-selftest.txt` | the red-check selftest (49 fixtures, 0 wrong), the identity selftest (0 failures), the id-length selftest (4 cases, 0 wrong) |
| `C:/Temp/av-kit/s69-plan-decision-probe.txt` | the decision probe: 12 decisions with this plan and the grouping as sources (D-689 to D-697, D-158 to D-160); a refusal without the grouping (HDP-18) |
| `C:/Temp/av-kit/s69-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit` |

No suite or build ran at plan time.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest and `id-length.py`.
- **Targeted:** each row's own files. `red-check.py` reads the Red receipts, and `capture-action-row.test.ts` runs on its own in each row that touches `test-ids.ts`.
- **Fresh full:** the session gate runs the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds and the capture Electron spec.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
