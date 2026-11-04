---
project: "2026-10-14-capture-filmstrip-actions"
date: "2026-10-14"
source: "docs/build-plan/09-screenshot-capture.md#filmstrip-context-menu"
meus: ["MEU-88", "MEU-89"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture filmstrip actions (Session 38)

> **Project:** `2026-10-14-capture-filmstrip-actions`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Filmstrip context menu (`:775-786`, MEU-88) and §Filmstrip multi-select (`:788-798`, MEU-89)
> - §Filmstrip (`:127-133`), §Destructive Delete (`:151-153`) and the image route row (`:601`) as Local Canon
> - `docs/build-plan/11-page-layout.md` CP4 (`:44`), CP 14/15 `capture-filmstrip` / `capture-filmstrip-item` (`:280-281`) and the CP 23/24 inline confirm strip as locked canon
> - `docs/build-plan/06-gui.md` preload listing (`:96`) and `docs/build-plan/gui-actions-index.md` Capture rows (`:69-86`)
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 38 (`:140-145`), decisions D-1 to D-7 (`:215-221`).
> **Known issues:** `CAPTURE-FILMSTRIP-CONTEXT-MENU` (triage decision D-58, autonomous) and `CAPTURE-FILMSTRIP-MULTISELECT` (triage decision D-59, autonomous). Their D-ids collide with this plan's, so they are cited in prose only.
> **User decisions (USER_EXPLICIT 2026-10-14):** "Registered scope (Recommended)": follow 09 exactly. MEU-88 is the menu with Copy full path, Copy image and Delete, where Delete reuses the existing confirm. MEU-89 is Shift-range multi-select; with more than one shot selected the menu shows only Delete, behind one batch confirm. Work happens in "New worktree off main (Recommended)": branch `claude/s38-capture-filmstrip-actions` at `P:/av-kit-wt/s38-capture-filmstrip-actions`, from main `7861020`.
> **Status:** `draft`, Round 1.

## Goal

Session 38 delivers MEU-88 (a thumbnail menu with Copy full path, Copy image and Delete) and MEU-89 (Shift-click range selection with one batch Delete), changing only `ui/` and three hub docs, with one new main-process IPC channel for the image clipboard.

Mat's Session 30 `FLATTEN_LOOK` (2026-10-03) asked for two things in the Capture filmstrip:

- **A right-click menu on each thumbnail** with Copy full path, Copy image and Delete (`CAPTURE-FILMSTRIP-CONTEXT-MENU`).
- **Shift-select across several shots.** With more than one shot selected, right-click shows only Delete, with one confirm for the whole batch (`CAPTURE-FILMSTRIP-MULTISELECT`).

Today `CaptureFilmstrip.tsx` (106 lines) renders one `<button data-testid="capture-filmstrip-item">` per shot with a plain `onClick → onSelect(id)`. It has no context menu, no keyboard menu and no notion of more than one selected shot. Delete exists only as the toolbar `capture-delete`, which always targets the editor's shot (`CapturePage.tsx:984-1003`). The clipboard bridge can write text (`write-clipboard-text`, `ui/src/main/ipc.ts:70`) but not images.

This session adds:

- **MEU-88 `gui-capture-filmstrip-menu`:**
  - An accessible thumbnail menu (`MENU_PATTERN`) that opens on right-click, the ContextMenu key or Shift+F10.
  - Its items: Copy full path (existing `writeClipboardText`), Copy image (new `write-clipboard-image` channel, written by `clipboard.writeImage` in main) and Delete (the existing inline confirm, aimed at the right-clicked shot).
- **MEU-89 `gui-capture-filmstrip-multiselect`:**
  - Shift-click range selection from an anchor, in filmstrip order. The editor shows the last-clicked shot.
  - With more than one shot in the range, the menu holds only "Delete {n} shots". One confirm names the count. Deletes run in filmstrip order, continue past failures, and report each failed shot in the status line.

Order (grouping `:143`): MEU-88 first, then MEU-89, which reuses the menu and the delete-target state. The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Planning started from `7861020` (the Session 30 closeout). Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent in the worktree (ls: No such file or directory, 2026-10-14); headroom is not on PATH. Scope is one renderer feature folder plus three main/preload files, read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). The `prereq` check refuses if a graph directory has appeared.

Execution re-check (task row 0, 2026-10-16). Headroom appeared on PATH after planning, so S1 fired and the gate was re-run:

```yaml
context_tool_decision:
  phase: execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "2026-10-16 row 0: graphify-out/ and graphify-out-research/ still absent. headroom is now on PATH (C:/Users/Mat/AppData/Roaming/Python/Python313/Scripts/headroom.exe) but has no approved Headroom disposition (the gate requires one; ten earlier plans record the same), and execution payloads are source code, grep output and exact test evidence (bypass classes). Not eligible."
  human_message_reference: "USER_EXPLICIT 2026-10-16: S1 Decision Brief answered 'all recommendations are auto-approved' for this session; recommendation was not_applicable plus the Invoke-Prereq amendment"
```

## Harness, driver and reviewer route

- **Driver:** Claude Code (VS Code extension) on Mat's Windows host:
  - `native_shell: powershell`, with `rtk` on PATH. Receipts go to `C:/Temp/av-kit/`.
  - `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; GUARDRAILS SIGN 1). The reviewer's `approved` does not start execution; Mat's chat "proceed" does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every row keeps `compact_continue` as the fallback.
- **Gate location:** local. The Windows host is the authoritative environment, so there is no container pre-gate and no `LOCAL_SEQUENCE` request. Real Electron runs in the driver's own shell, with `ELECTRON_RUN_AS_NODE` removed (`validate-task.ps1` does this before every stage).
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1`, using the `avkit_independent_reviewer` class (`.agent/skills/cli-dispatch/SKILL.md`). The author is Anthropic and the reviewer OpenAI, so vendors differ. Mat is the fallback if Codex is unauthenticated (`harness.local.md:53`). Caps: plan 3 rounds, execution 6. Each dispatch is metered and is announced before it runs.
- **Receipts:** `C:/Temp/av-kit/s38-*`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-88` | `.agent/context/handoffs/2026-10-14-capture-filmstrip-actions-MEU-88-handoff.md` |
| `MEU-89` | `.agent/context/handoffs/2026-10-14-capture-filmstrip-actions-MEU-89-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-10-14-capture-filmstrip-actions-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-14-capture-filmstrip-actions-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, dependency install, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-88 TDD: IPC + main + preload, renderer menu and copy/delete, Electron (rows 2–4) | WP-0 | `shared` | MEU-88 tests and source; Red/Green receipts |
| WP-2 | MEU-88 targeted gate and handoff (row 5) | WP-1 | `compact_continue` | MEU-88 handoff; compact, then re-read `task.md` and the handoff |
| WP-3 | MEU-89 TDD and handoff (rows 6–8) | WP-2 | `compact_continue` | MEU-89 handoff; compact, then re-read |
| WP-4 | Hub reconciliation (row 9) | WP-3 | `shared` | `docs/build-plan/06…`, `09…`, `gui-actions-index.md` |
| WP-5 | H1 closeout (full D6 gate, `FILMSTRIP_LOOK`), execution review, H2 | WP-4 | `compact_continue` | handoffs, gate receipts, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> These items record what the user's "proceed" will cover and what the next report must surface. They are not a pause point before review.
>
> 1. **Decided by the user (2026-10-14):** the registered 09 scope (above), the worktree, and Session number 38.
> 2. **`TEST_AMENDMENTS` TA-1 to TA-3** (contracts table). The new channel raises the two registered-channel count pins from 19 to 20, and the census gains the new channel's valid/invalid payloads. These are the same kind of count and list amendment as MEU-61 (Session 30 TA-6). Any other contradiction stops execution (Stop condition S2).
> 3. **`BASELINE_RED`** (contracts table): main fails one test, `queue-canon` AC-41.3, because Zorivest's light accent-cyan changed and only the unmerged Session 31 branch ports it. This plan tolerates exactly that failure. If Session 31 merges first, rebase this branch on main before row 0 and the tolerance goes unused.
> 4. **Autonomous decisions, logged for veto:**
>    - D-10: Copy image copies the **original** image, which is what the thumbnail shows. The annotated copy (when one exists) is not offered. Alternative: copy the annotated image when it exists.
>    - D-11: Copy image re-encodes non-PNG originals to PNG in the renderer before they reach main. A WebP original then copies correctly, because Electron's `nativeImage` decodes only PNG and JPEG.
>    - D-12: the menu acts on the right-clicked shot **without** changing the selection, as in Explorer and VS Code. Deleting a non-selected shot keeps the editor's shot and its unsaved marks.
>    - D-15: the Shift anchor stays fixed across repeated Shift-clicks (Explorer and APG listbox behaviour). With no plain click yet, the editor's current shot (including the auto-selected newest) is the anchor. A Shift-click that would leave unsaved marks first shows the existing discard confirm; Cancel applies nothing.
>    - D-17: Ctrl-toggle and keyboard multi-select stay out of scope (09 `:794` names Shift-click only; triage D-59 keeps Ctrl out by default). D-17 asks whether to register a follow-up for keyboard range selection.
>    - D-18: after a partial batch failure, the surviving shots stay in the filmstrip, the range clears, and the error line names every failed shot.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. `packages/`, `mcp-server/`, `tools/`, `native/` and `openapi.committed.json` stay byte-identical to `baseline.sha`. In `ui/src/main/`, only `ipc.ts`, `index.ts`, `preload.ts` and the new `clipboard-image.ts` change. Nothing else in the repository changes except this plan's closeout outputs (the plan directory, the session's handoffs and reflection, and the rendered `meu-registry.md` / `known-issues.md` / `known-issues-archive.md`). `validate-task.ps1 -Check scope` proves all of this against every path changed since `baseline.sha`. | Grouping `:142`; 09 `:775-798` |
| `IMAGE_CHANNEL` | The renderer-to-main channel `write-clipboard-image`, appended after `login-item-set` in `RENDERER_TO_MAIN_CHANNELS`, so the list has 20 entries. | 09 `:782` (main-process clipboard via preload IPC); D-11 |
| `PNG_SIGNATURE` | The 8 bytes `89 50 4E 47 0D 0A 1A 0A`. | PNG spec (W3C PNG §5.2) |
| `COPY_IMAGE_MAX_BYTES` | `64 * 1024 * 1024`. | D-11 |
| `IMAGE_PAYLOAD` | The strict zod schema for `IMAGE_CHANNEL`: `{ png: Uint8Array }`. `png` is non-empty, at most `COPY_IMAGE_MAX_BYTES`, and starts with `PNG_SIGNATURE`. Any extra key, a non-`Uint8Array` value (string, number array, `ArrayBuffer`) or a failed refinement returns `{ ok: false }` before any dependency is called and before `effects.clipboard` changes. | `ipc.ts:70` strict precedent; D-11 |
| `IMAGE_HANDLER` | The `handleIpc` case for `IMAGE_CHANNEL`: increment `effects.clipboard` by 1, then `await deps.writeClipboardImage(png)`. A `false` result, or a missing dependency, returns `{ ok: false, error: IMAGE_DECODE_ERROR }`. `true` returns `{ ok: true }`. | `ipc.ts:371-375` precedent |
| `IMAGE_DECODE_ERROR` | `image could not be decoded` | D-11 |
| `MAIN_IMAGE_WRITE` | `writePngToClipboard(png, electron)` in the new `ui/src/main/clipboard-image.ts`. It runs `nativeImage.createFromBuffer(Buffer.from(png.buffer, png.byteOffset, png.byteLength))`; if `isEmpty()` it returns `false` without calling `clipboard.writeImage`; otherwise it calls `clipboard.writeImage(image)` and returns `true`. `electron` is `{ nativeImage, clipboard }`, injected so a unit test can fake it. `index.ts` wires `writeClipboardImage: async (png) => writePngToClipboard(png, { nativeImage, clipboard })`. | `capture-picker.ts:466-483` (`nativeImage` + `clipboard.writeImage` precedent); Electron `nativeImage` docs |
| `PRELOAD_KEY` | `writeClipboardImage: (png: Uint8Array) => ipcRenderer.invoke('write-clipboard-image', { png })`, appended to `API_KEYS`. `env.d.ts` declares it **optional** (`writeClipboardImage?`), so the existing `window.api` mocks need no edit. | `env.d.ts` `loginItemGet?` precedent (MEU-61); 06 `:1125` |
| `RENDERER_PNG` | `toClipboardPng(blob, encode)` in the new `capture-clipboard.ts`. If `blob` is `null` it throws `Error(COPY_IMAGE_FETCH_ERROR)`. It reads the bytes; if they start with `PNG_SIGNATURE` it returns them unchanged. Otherwise it returns `encode(blob)`, whose result must also start with `PNG_SIGNATURE`, or it throws `Error(COPY_IMAGE_ENCODE_ERROR)`. The production `encode` is `createImageBitmap(blob)` → an `OffscreenCanvas` of the bitmap's size → `getContext('2d').drawImage(bitmap, 0, 0)` → `convertToBlob({ type: 'image/png' })`. Skipping the draw yields a transparent image of the right size, so only AC-88.12(b)'s pixel oracle, not the PNG signature or the size, proves this step. | D-11 |
| `SHOT_PIXELS` | The AC-88.12 pixel oracle. Both Copy image fixtures are 8×6: left half opaque `#ff0000`, right half opaque `#0000ff`. The spec builds them in the run, the PNG with `nativeImage.createFromBitmap(...).toPNG()` in main and the WebP with `OffscreenCanvas.convertToBlob({ type: 'image/webp', quality: 1 })` in the renderer, and its seam serves them by id. The oracle reads `clipboard.readImage().toBitmap()` (BGRA) in main and requires pixel (1,3) to be red and (6,3) blue, each channel within ±16, alpha 255. A transparent image of the same size fails it. | D-11; review F1 |
| `COPY_IMAGE_SOURCE` | `fetchAuthorizedBlob('/captures/' + encodeURIComponent(id) + '/image?variant=original')`. | D-10; `capture-image.ts:15-24`; Session 30 reflection RULE-2 (`:178`, path parameters are percent-encoded) |
| `COPY_IMAGE_FETCH_ERROR` / `COPY_IMAGE_ENCODE_ERROR` / `COPY_IMAGE_UNAVAILABLE` | `the image could not be loaded` / `the image could not be converted to PNG` / `copying images is not available in this window` (the last when `window.api.writeClipboardImage` is undefined). | D-11 |
| `MENU_PATTERN` | `CaptureFilmstripMenu`, a new component following the WAI-ARIA APG menu pattern and the `QueueCardMenu.tsx` precedent: `role="menu"`, `aria-label="Shot actions"`, `data-testid="capture-filmstrip-menu"`, items `role="menuitem"` with `tabIndex={-1}`. On open, the first item takes focus. ArrowDown/ArrowUp move with wrap-around; Home/End jump to the first/last item; Enter or Space activates. Escape closes and returns focus to the thumb that opened it. Tab, a pointer-down outside the menu, a scroll of the filmstrip and window blur close it without moving focus. It renders `position: fixed`, clamped inside the viewport, with the menu surface classes of `QueueCardMenu` (`rounded-[var(--radius-md)] border border-border bg-bg-elevated`); the Delete item uses `text-error`. | APG Menu pattern; `ui/src/renderer/src/components/queue/QueueCardMenu.tsx`; D-8 |
| `MENU_OPEN` | A thumb opens the menu on (a) its `contextmenu` event (`preventDefault`), (b) keydown `ContextMenu`, or (c) keydown `F10` with `shiftKey`. (b) and (c) call `preventDefault`. Opening for the shot whose menu is already open is a no-op, so Chromium's paired keydown/`contextmenu` dispatch never opens twice. | 09 `:785` (keyboard access via the context-menu key); D-9 |
| `MENU_ANCHOR` | A pointer-opened menu is placed at `clientX/clientY`. A keyboard-opened menu (b, c), or a `contextmenu` whose `clientX` and `clientY` are both 0, is placed at the thumb's `getBoundingClientRect()` bottom-left. | D-9 |
| `MENU_TARGET` | The menu acts on the shot it was opened on. Opening it never changes `selectedId`, the range, the editor's marks or the dirty state. | D-12 |
| `MENU_LOCK` | No menu opens while the filmstrip is `locked` (a confirm strip is open; `CONFIRM_EXCLUSIVITY`). A menu that is open when `locked` turns true closes. | `CapturePage.tsx:1076` CONFIRM_EXCLUSIVITY; D-13 |
| `MENU_ITEMS_SINGLE` | In order: `Copy full path` (`capture-filmstrip-menu-copy-path`), `Copy image` (`capture-filmstrip-menu-copy-image`), `Delete` (`capture-filmstrip-menu-delete`). Used when the target is not a member of a range larger than 1. | 09 `:781` |
| `MENU_ITEMS_BATCH` | Exactly one item, `Delete {n} shots` (`capture-filmstrip-menu-delete-batch`), where `n = RANGE.length`. Used when the target is a member of a `RANGE` larger than 1. | 09 `:795` |
| `COPY_PATH` | Copy full path calls `window.api.writeClipboardText(target.original_path)`, closes the menu, and then reports `COPY_STATUS`. | 09 `:781-782`; `writeClipboardText` exists (`preload.ts`) |
| `COPY_IMAGE` | Copy image closes the menu. If `window.api.writeClipboardImage` is undefined it fails with `COPY_IMAGE_UNAVAILABLE`. Otherwise it loads `COPY_IMAGE_SOURCE`, converts with `RENDERER_PNG`, calls `window.api.writeClipboardImage(png)`, and reports `COPY_STATUS`. | 09 `:781-782`; D-10; D-11 |
| `COPY_STATUS` | Success sets the shot notice `{ shotId: selectedId, text }`, with `text` = `Copied the path of {display_name}.` or `Copied {display_name} as an image.`. Failure sets `error` = `Could not copy {display_name}: {message}` and logs it through `logRenderer('ERROR', …)`. The notice is keyed to the **editor's** shot because the menu does not change the selection (`MENU_TARGET`). That is why it shows at once in `capture-status`. | `CapturePage.tsx:1111-1124` `editorStatus` precedence; G35 |
| `DELETE_TARGETS` | New `CapturePage` state, `string[]`, read by the `'delete'` confirm. Toolbar `capture-delete` sets `[selectedId]`, which is today's behaviour. Menu Delete sets `[target.id]`; menu "Delete {n} shots" sets `RANGE`. Cancel clears it. The `ConfirmKind` union is unchanged. | `CapturePage.tsx:190`, `:984-1003`; D-14 |
| `DELETE_CONFIRM_TEXT` | For targets `[selectedId]`: the existing `Delete this capture and its files from disk?`. For one target that is not the selected shot: `Delete "{display_name}" and its files from disk?`. For `n > 1` targets: `Delete {n} captures and their files from disk?`. The cancel and accept test ids (`capture-delete-confirm-cancel`, `capture-delete-confirm`) and the accept label `Delete capture` stay the same for one target; for `n > 1` the accept label is `Delete {n} captures`. | `CapturePage.tsx:1043-1049`; 09 `:795` ("one confirm naming the count"); D-14 |
| `SINGLE_DELETE` | Accepting a one-target delete calls the existing `deleteCapture(id)`. If the target is the editor's shot, `setSelectedId(null)` follows (today's path; the newest shot is then auto-selected). If not, `selectedId`, the marks, undo history and dirty state stay as they were. | `CapturePage.tsx:996-1002`; D-12 |
| `RANGE` | New `CapturePage` state: `anchorId: string \| null` and `rangeIds: string[]`, in `RANGE_ORDER`. A plain (non-Shift) choice sets `anchorId` to the chosen id and `rangeIds` to `[]`. Shift+click on shot X with `anchorId` set gives `rangeIds = rangeBetween(RANGE_ORDER, anchorId, X)`, and the editor moves to X through `chooseItem`. `anchorId` does not change. Shift+click with `anchorId` null takes the editor's current shot (`selectedId`, including the one `CapturePage` auto-selects at `:281-289` and the one chosen after the anchor's shot is removed) as the anchor, sets `anchorId` to it, and applies the range from it. Only when both are null does Shift+click behave as a plain click. Membership counts only when `rangeIds.length > 1`. When the catalog changes, ids that no longer exist are dropped from `rangeIds`, and `anchorId` becomes null if its shot is gone. **Amended (D-25):** `rangeIds` is the selection set. It is a contiguous slice after a Shift+click and any subset after `CHECK_TOGGLE`, and it is always held in `RANGE_ORDER`. A plain thumb click still clears it. | 09 `:794`; APG Listbox (Shift+click); D-15 |
| `RANGE_ORDER` | `sortFilmstrip(items)` order, which is what the filmstrip shows (`useCaptureCatalog.ts:50-58`). | 09 `:129` |
| `rangeBetween` | `rangeBetween(orderedIds, a, b)` returns the inclusive slice between the indices of `a` and `b`, in `orderedIds` order and in either direction. An unknown `b` gives `[]`; an unknown `a` gives `[b]`. | D-15 |
| `RANGE_DIRTY` | A Shift+click while the editor is dirty follows `chooseItem`'s existing discard confirm. Confirm applies the new `rangeIds` and selection. Cancel applies neither. The pending range is held next to `pendingSelect`. | `CapturePage.tsx:503-515`; D-15 |
| `RANGE_MARK` | Each thumb whose id is in a range larger than 1 gets `data-in-range="true"`, the class `ring-1 ring-accent/40` (the selected thumb keeps its existing classes), and an sr-only `, selected` suffix after the full name. The editor's thumb keeps `aria-current="true"`. | 11 CP4 accessible-name rule (`:44`); D-16 |
| `RANGE_STATUS` | With no higher-precedence status, `capture-status` shows `{n} shots selected` while `rangeIds.length > 1`. It sits below the shot notice in `editorStatus` precedence. | G35 (T0); D-16 |
| `CHECK` | (D-25) Each filmstrip row renders an `<input type="checkbox">` to the left of its thumb, as a sibling of the thumb button, because a button cannot contain a checkbox. It has `data-testid="capture-filmstrip-check"` and `aria-label="Select {full name}"`. It is `checked` when the shot's id is in `rangeIds`, whatever the length, and `disabled` while `locked`. The thumb button, its text and its attributes are unchanged. | Mat's request 2026-10-16 (`FILMSTRIP_LOOK` round 1); Windows Explorer item check boxes; zorivest `TradesTable.tsx:263-291` |
| `CHECK_TOGGLE` | (D-25) A plain click on a shot's checkbox sets `rangeIds = toggleSelection(RANGE_ORDER, rangeIds, id)` and `anchorId = id`. It does not move the editor's shot, and it shows no discard confirm because the editor is unchanged. A Shift+click on a checkbox, with an anchor (`anchorId ?? selectedId`), sets `rangeIds = rangeBetween(RANGE_ORDER, anchor, id)`, keeps the editor's shot, and sets `anchorId` to the anchor. `toggleSelection(orderedIds, selected, id)` lives in `capture-filmstrip-select.ts`. It adds an absent id or removes a present one and returns the ids in `orderedIds` order. An id not in `orderedIds` leaves the selection as it was. `RANGE_MARK`, `RANGE_STATUS`, `MENU_ITEMS_BATCH`, `BATCH_DELETE`, `BATCH_RESULT` and `NEXT_SELECTION` apply to this set unchanged. | D-25 |
| `BATCH_DELETE` | `deleteCaptures(ids, remove)` in `capture-commands.ts`. For each id in the given order it awaits `remove(id)`, which is one `DELETE /captures/{encodeURIComponent(id)}`. The next request starts only after the previous one settles. A rejection is recorded as `{ id, message }`, and the loop continues. Afterwards it invalidates `QUERY_KEY` once and returns `{ deleted: string[], failed: { id, message }[] }`. An empty `ids` sends no request and does not invalidate. The page passes `RANGE` order. | 09 `:795` ("removes run in order and report per-shot failures"); RULE-2; D-18 |
| `BATCH_RESULT` | After `BATCH_DELETE` the page clears `rangeIds` and `anchorId`. If the editor's shot was deleted, the selection moves to `NEXT_SELECTION`. With no failures it sets the notice `Deleted {n} shots.` keyed to the resulting selection. With failures it sets `error` = `Deleted {k} of {n} shots. Could not delete {name}: {message}` and joins further failures with `; {name}: {message}`, where `name` is the shot's `display_name`. | 09 `:795`; G35; D-18 |
| `NEXT_SELECTION` | The first id in `RANGE_ORDER` that was not deleted, or `null` when none is left (auto-select then has nothing to pick). | `CapturePage.tsx:281-289` (newest-first auto-select); D-18 |
| `HELP_SENTENCE` | `Right-click a thumbnail (or press Shift+F10) to copy its path or image, or delete it; Shift-click selects a range to delete together.` It is appended to the end of the `four-tools` section body in `CAPTURE_HELP_SECTIONS`. It is not added to `original-annotated`, whose body must keep ending with the flatten sentence (AC-67.25, `endsWith`). The existing `four-tools` assertions (AC-59.20, AC-60.15, AC-66.16) use `toContain`, so they still hold. | 09 `:155-157` HelpCard; `capture-help-content.test.ts:41-47`; D-19 |
| `NEW_TESTIDS` | MEU-88: `capture-filmstrip-menu`, `capture-filmstrip-menu-copy-path`, `capture-filmstrip-menu-copy-image`, `capture-filmstrip-menu-delete`. MEU-89: `capture-filmstrip-menu-delete-batch`, and (D-25) `capture-filmstrip-check`. They are appended to `ui/tests/e2e/test-ids.ts` as two additive blocks. `data-in-range` is an attribute on the existing `capture-filmstrip-item`, not a new id. | E2; `test-ids.ts` tail precedent |
| `ACTION_ROWS` | Four rows in `docs/build-plan/gui-actions-index.md`, after `capture:delete`. They are written at plan time (09 `:783`), each `specified` with owner `09`: `capture:copy_path` (Copy full path, thumbnail menu; IPC `writeClipboardText`), `capture:copy_image` (Copy image, thumbnail menu; IPC `writeClipboardImage`), `capture:menu_delete` (Delete from thumbnail menu; `DELETE /captures/{id}`), `capture:batch_delete` (Delete {n} shots; `DELETE /captures/{id}` per shot). All four have Palette `no`. | 09 `:783`; grouping D-1 (gated edits allowed once Session 30 approved, 2026-10-12) |
| `TEST_AMENDMENTS` | **TA-1:** `ui/tests/unit/ipc-strict-census.test.ts:52` `toHaveLength(19)` → `20`, plus `IMAGE_CHANNEL` entries in its valid-payload and type-failure tables. **TA-2:** `ui/tests/unit/login-item-ipc.test.ts:50-51`, both `toHaveLength(19)` → `20`. **TA-3:** `ui/tests/unit/ipc-channels.ts` gains `IMAGE_CHANNEL` (not in `IPC_NO_PAYLOAD`). No other existing expectation changes. | MEU-61 TA precedent; Stop condition S2 |
| `COUNT_FLOORS` | Computed by `plan_checks.py floors` against `baseline-counts.json` (row 0). Vitest: `numFailedTests` is 0, and `numPassedTests` ≥ baseline passed + the number of passing tests whose name carries an `AC-88.n`/`AC-89.n` id. Playwright: `unexpected` and `flaky` are 0, `skipped` ≤ baseline, and `expected` ≥ baseline expected + the passing specs whose title carries an AC id. Every non-Electron AC id (matched as `AC-88.n` not followed by a digit) appears in a passing Vitest test name, and AC-88.12 and AC-89.9 each appear in a passing Playwright spec title. | G36; Session 29/30 `COUNT_FLOORS` precedent |
| `BASELINE_RED` | Exactly one existing test may fail in any run of this plan: `queue-canon.test.ts` AC-41.3, and only with the message `--color-accent-cyan light diverges from PILL_TOKEN_SOURCE`. It reads the live `P:/zorivest/ui/src/renderer/src/globals.css`, whose light accent-cyan is now `#0e7490`, while main's `styles.css:89` still has `#0891b2`. Session 31 commit `da1d111` (unmerged branch `claude/vigilant-volta-f04tvs`) ports the fix. This plan does not touch `styles.css`. The test may fail but never must; any other failure is real. `plan_checks.py` (`is_baseline_red`) enforces this, and `COUNT_FLOORS` allows at most the baseline's count of it. The tolerance covers that assertion only: every Vitest run also uses the default reporter, and `vitest`, `vitest-red` and `floors` fail when its text receipt shows `Unhandled Errors`/`Unhandled Rejection` or an `Errors  N error` summary, which the JSON report omits. | plan-time run 2026-10-14 (`C:/Temp/av-kit/s38-plantime-docsuites.txt`); Session 31 A-5 |
| `FILMSTRIP_LOOK` | Mat's manual check on the dev app (launched detached with `Start-Process`, `ELECTRON_RUN_AS_NODE` removed). L1: right-click → menu at the pointer; Copy full path pastes into Notepad. L2: Copy image on a PNG and on a JPEG/WebP shot pastes into Paint at the right size. L3: Shift+F10 / Menu key opens the menu; arrows and Escape behave. L4: Delete from the menu on a non-selected shot keeps the editor's shot and marks. L5: Shift-click a range of 3, right-click → only "Delete 3 shots", one confirm, all gone. L6: the range is visible and readable in dark and light themes. **Round 2 (D-25):** L3 is re-checked with the steps spelled out: click or Tab to a thumb so that it has focus, then press Shift+F10. The Menu key is the ≣ key next to the right Ctrl, and many laptops lack it. L5 becomes: tick three shots' boxes, or Shift-click a range of 3; right-click a ticked shot → only "Delete 3 shots", one confirm, all gone. L7: ticking a box leaves the editor's shot and marks alone, and a plain thumb click clears the ticks. | Session 29/30 look precedent; memory "launch dev app detached" |

### MEU-88 — `gui-capture-filmstrip-menu`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| IPC `write-clipboard-image` (renderer → main) | zod in `ui/src/main/ipc.ts` `schemas` | `IMAGE_PAYLOAD` | `.strict()`: an extra key returns `{ ok: false }` before Electron is touched |
| IPC `write-clipboard-text` (existing, reused) | zod `ipc.ts:70` | `{ text: string }` | `.strict()` (unchanged) |
| REST `GET /captures/{id}/image?variant=original` (existing, reused) | `packages/api` route `:237` (unchanged) | `id` percent-encoded (`COPY_IMAGE_SOURCE`) | n/a (GET) |
| REST `DELETE /captures/{id}` (existing, reused) | `packages/api` (unchanged) | existing `deleteCapture` | n/a |
| UI menu (pointer + keyboard) | `CaptureFilmstripMenu` props | `MENU_OPEN`, `MENU_LOCK` | n/a |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-88.1 | integration | Right-click on a non-selected thumb opens `MENU_PATTERN` with `MENU_ITEMS_SINGLE` in order, the first item focused, at `MENU_ANCHOR`. `aria-current` stays on the previously selected thumb (`MENU_TARGET`). | Spec 09 `:781`; D-8, D-12 | A right-click while the confirm strip is open opens no menu (`MENU_LOCK`). Opening a confirm (toolbar Delete) while the menu is open closes it. |
| AC-88.2 | integration | Keyboard: with a thumb focused, the ContextMenu key and Shift+F10 each open the menu at the thumb's rect. ArrowDown/ArrowUp wrap; Home/End jump; Escape closes and focus returns to that thumb; Tab and an outside pointer-down close it. | Spec 09 `:785`; APG Menu; D-9 | F10 without Shift and a plain letter key open nothing. A second open signal for the same thumb leaves exactly one menu (`MENU_OPEN` idempotence). |
| AC-88.3 | integration | Copy full path on a non-selected shot calls `writeClipboardText` once with **that** shot's `original_path`, closes the menu, and shows `Copied the path of {display_name}.` in `capture-status` (`COPY_PATH`, `COPY_STATUS`). | Spec 09 `:781-782` | A rejecting `writeClipboardText` shows `Could not copy {display_name}: {message}` and no success notice. |
| AC-88.4 | unit | `toClipboardPng` (`RENDERER_PNG`) returns PNG bytes unchanged without calling `encode`, and passes a non-PNG blob to `encode`, returning its PNG result. | D-11 | A `null` blob throws `COPY_IMAGE_FETCH_ERROR`. An `encode` result without `PNG_SIGNATURE` throws `COPY_IMAGE_ENCODE_ERROR`. |
| AC-88.5 | integration | Copy image fetches `COPY_IMAGE_SOURCE` for the target id (percent-encoded, e.g. an id containing `/` reaches the request as `%2F`). It calls `writeClipboardImage` once with a `Uint8Array` that starts with `PNG_SIGNATURE`, and shows `Copied {display_name} as an image.` | Spec 09 `:781-782`; D-10; RULE-2 | The image GET returns 404 → `Could not copy …: the image could not be loaded`, and `writeClipboardImage` is not called. `window.api.writeClipboardImage` undefined → `COPY_IMAGE_UNAVAILABLE`, and no fetch. |
| AC-88.6 | unit | `handleIpc('write-clipboard-image', { png })` with valid PNG bytes calls `deps.writeClipboardImage` once with those bytes, increments `effects.clipboard` by 1, and returns `{ ok: true }` (`IMAGE_HANDLER`). | Spec 09 `:782`; G27 | Each of these returns `{ ok: false }`, with no dependency call and `effects.clipboard` unchanged: `{ png: 'x' }`, `{ png: [137, 80] }`, `{ png: new ArrayBuffer(8) }`, empty bytes, bytes over `COPY_IMAGE_MAX_BYTES`, bytes without `PNG_SIGNATURE`, and `{ png, path: 'C:/x' }`. A dependency returning `false` gives `{ ok: false, error: IMAGE_DECODE_ERROR }`. |
| AC-88.7 | unit | `writePngToClipboard` (`MAIN_IMAGE_WRITE`) decodes through `nativeImage.createFromBuffer` with exactly the given bytes, calls `clipboard.writeImage` once with the decoded image, and returns `true`. | Spec 09 `:782`, `:785` (main-process clipboard test) | An empty decoded image returns `false`, and `clipboard.writeImage` is never called. |
| AC-88.8 | unit | `IMAGE_CHANNEL` is registered: `listRegisteredChannels()` equals the test-side list, which has 20 entries (TA-1, TA-2, TA-3). `getPreloadApiKeys()` contains `writeClipboardImage`. The preload source maps it to `invoke('write-clipboard-image', { png })`. | `PRELOAD_KEY`; G27 | The census type-failure table rejects `IMAGE_CHANNEL` payloads of the wrong type (TA-1). |
| AC-88.9 | integration | Menu Delete on the **selected** shot opens the existing confirm strip with `Delete this capture and its files from disk?` and the existing ids. Accepting sends exactly one `DELETE /captures/{id}` for that id, and the selection then falls to the newest shot (`SINGLE_DELETE`). | Spec 09 `:781` ("reuses the existing confirm"), `:151-153` | Cancel sends no DELETE and leaves `DELETE_TARGETS` empty; a following toolbar Delete targets the selected shot. |
| AC-88.10 | integration | Menu Delete on a **non-selected** shot shows `Delete "{display_name}" and its files from disk?`. Accepting sends one DELETE for that id only. The editor keeps its shot, its marks and its dirty state, with no discard confirm (`SINGLE_DELETE`, `MENU_TARGET`). | D-12, D-14 | The selected shot's id is never sent a DELETE. After the DELETE settles and the catalog refetch resolves, the same thumb keeps `aria-current`, the unsaved SVG marks are still drawn and the dirty dot is still shown. |
| AC-88.11 | unit | `gui-actions-index.md` contains every `ACTION_ROWS` id. Each IPC cell resolves to a registered channel that the preload source names, and each REST cell names `/api/v1/captures/{id}` in `openapi.committed.json`. Every MEU-88 `NEW_TESTIDS` id is in `test-ids.ts` and in production source. | 09 `:783`; AC-23.20 precedent | A row whose IPC cell names an unregistered channel fails, which the census Red of the new assertion before `IMAGE_CHANNEL` exists shows. |
| AC-88.12 | integration (Electron) | In the built app with the e2e seam: (a) right-click a thumb → Copy full path → the main-process `clipboard.readText()` equals that shot's `original_path`; (b) Copy image on a PNG shot and on a WebP shot → `clipboard.readImage()` is not empty, its `getSize()` equals the shot's pixel size, and its pixels pass `SHOT_PIXELS`. (c) Shift+F10 and the ContextMenu key, each sent with Playwright's `locator.press` on a focused thumb (the Chromium input path, not `dispatchEvent`), open the menu with focus on the first item, and Escape returns focus to the thumb; (d) menu Delete on a non-selected shot removes that thumb only, and the DELETE ledger holds exactly that id. | Spec 09 `:781-785`; E2; Stop condition S3 | (e) right-click while the confirm strip is open shows no `capture-filmstrip-menu`. (f) Before each Copy image the spec writes a transparent 8×6 image to the clipboard in main and asserts `SHOT_PIXELS` rejects it, so the oracle discriminates and the copy must overwrite it. |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Menu items and Delete reusing the confirm | Spec | 09 `:781` |
| Clipboard work in main through preload IPC | Spec | 09 `:782`; `IMAGE_CHANNEL`, `MAIN_IMAGE_WRITE` |
| Keyboard access | Spec | 09 `:785`; `MENU_OPEN` adds Shift+F10, the Windows equivalent of the Menu key (D-9) |
| Menu widget semantics | Research-backed | APG Menu pattern + `QueueCardMenu` (D-8) |
| Which image Copy image copies | Local Canon | The original, matching the thumbnail and Copy full path (D-10; veto item) |
| Non-PNG originals | Research-backed | Electron `nativeImage` decodes PNG/JPEG only; re-encode in the renderer (D-11) |
| Whether the menu changes the selection | Research-backed | It does not (Explorer, VS Code; D-12) |
| Delete text for a non-selected shot | Local Canon | Name the shot (D-14) |
| Copy feedback | Local Canon | `capture-status` via the existing notice/error (G35 T1; `COPY_STATUS`) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/main/ipc.ts` | modify | `IMAGE_CHANNEL`, `IMAGE_PAYLOAD`, `IpcDeps.writeClipboardImage`, `IMAGE_HANDLER` |
| `ui/src/main/clipboard-image.ts` | new | `MAIN_IMAGE_WRITE` |
| `ui/src/main/index.ts` | modify | Wire `writeClipboardImage` (`MAIN_IMAGE_WRITE`) |
| `ui/src/main/preload.ts` | modify | `PRELOAD_KEY` |
| `ui/src/renderer/src/env.d.ts` | modify | Optional `writeClipboardImage?` |
| `ui/src/renderer/src/features/capture/capture-clipboard.ts` | new | `RENDERER_PNG`, `COPY_IMAGE_SOURCE`, copy error/status strings |
| `ui/src/renderer/src/features/capture/CaptureFilmstripMenu.tsx` | new | `MENU_PATTERN` |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modify | `MENU_OPEN`, `MENU_ANCHOR`, `MENU_LOCK`, menu callbacks |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `COPY_PATH`, `COPY_IMAGE`, `COPY_STATUS`, `DELETE_TARGETS`, `DELETE_CONFIRM_TEXT`, `SINGLE_DELETE` |
| `ui/tests/unit/clipboard-image-main.test.ts` | new | AC-88.6, AC-88.7 |
| `ui/tests/unit/capture-clipboard.test.ts` | new | AC-88.4 |
| `ui/tests/unit/capture-filmstrip-actions.behavior.test.ts` | new | AC-88.1–88.3, 88.5, 88.9, 88.10 (jsdom + RTL + `userEvent`). It imports only existing modules, so Red is by assertion: after each open gesture it queries the menu with `queryBy*` and asserts `expect(menu).not.toBeNull()` before using an item (a `getBy*`/`findBy*` miss is a query error, not an assertion), and it asserts range attributes explicitly. Collaborators are mocked; the menu and selection behaviour are not. |
| `ui/tests/unit/ipc-strict-census.test.ts` | modify | TA-1 |
| `ui/tests/unit/login-item-ipc.test.ts` | modify | TA-2 |
| `ui/tests/unit/ipc-channels.ts` | modify | TA-3 |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify (append only) | AC-88.11 |
| `ui/tests/e2e/capture-filmstrip-actions.test.ts` | new | AC-88.12 (Electron), with its own stateful fetch seam (per-id DELETE ledger, per-id image content type, the `SHOT_PIXELS` fixtures) |
| `ui/tests/e2e/test-ids.ts` | modify (append only) | MEU-88 `NEW_TESTIDS` block |
| `docs/build-plan/gui-actions-index.md` | modify (plan time) | `ACTION_ROWS` |

### MEU-89 — `gui-capture-filmstrip-multiselect`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| REST `DELETE /captures/{id}` (existing, called per shot) | `packages/api` (unchanged) | `id` percent-encoded (`BATCH_DELETE`) | n/a |
| UI pointer (Shift+click, right-click on a range member) | `CaptureFilmstrip` props | `RANGE`, `MENU_ITEMS_BATCH` | n/a |

No new IPC, REST or MCP surface.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-89.1 | unit | `rangeBetween` returns the inclusive slice in either direction, in the given order. | 09 `:794`; D-15 | An unknown target gives `[]`; an unknown anchor gives `[target]`. |
| AC-89.2 | integration | Click A, then Shift+click C (filmstrip order A, B, C): A, B and C carry `RANGE_MARK`, `aria-current` is on C, and `capture-status` shows `3 shots selected`. A further Shift+click on B gives the range A, B (the anchor stays A). A plain click clears every `data-in-range`. With no click at all (A auto-selected on load), Shift+click C gives A, B, C. After the anchor's shot is deleted, the next Shift+click anchors on the editor's current shot. | 09 `:794`; APG Listbox; D-15, D-16 | After a plain click no thumb has `data-in-range`, and `RANGE_STATUS` is absent. A Shift+click on the anchor itself gives a range of 1, so no range marks and no count. |
| AC-89.3 | integration | `RANGE_DIRTY`: with unsaved marks, a Shift+click shows the discard confirm. Confirm applies the range and moves the editor. | `CapturePage.tsx:503-515`; D-15 | Cancel leaves the editor's shot, the marks and the range unchanged. |
| AC-89.4 | integration | With a range of 3, right-clicking a member opens a menu with exactly `MENU_ITEMS_BATCH` (`Delete 3 shots`). Right-clicking a shot outside the range opens `MENU_ITEMS_SINGLE` and leaves the range as it was. | 09 `:795` | The batch menu contains no Copy item. |
| AC-89.5 | integration | Batch confirm: `Delete 3 captures and their files from disk?`, with accept label `Delete 3 captures` and the existing confirm test ids. Accepting sends one DELETE per shot in `RANGE_ORDER`. Each request starts after the previous one settles, ids are percent-encoded, and the catalog is invalidated once. Afterwards the range is cleared, the selection follows `NEXT_SELECTION`, and `capture-status` shows `Deleted 3 shots.` (`BATCH_DELETE`, `BATCH_RESULT`). | 09 `:795`; D-18 | Cancel sends no DELETE and keeps the range. |
| AC-89.6 | integration | Partial failure: the second of three DELETEs returns 500. The third is still sent. `capture-status` shows `Deleted 2 of 3 shots. Could not delete b.png: {message}`. The failed shot stays in the filmstrip, and the range is cleared. | 09 `:795` ("report per-shot failures"); D-18 | No failure is swallowed: with two failures, both names appear in the message. |
| AC-89.7 | unit | `deleteCaptures` (`BATCH_DELETE`) calls `remove` once per id in order. It does not start a call before the previous one settles, continues past a rejection, invalidates once, and returns `{ deleted, failed }`. | D-18 | An empty `ids` makes no call and no invalidation. |
| AC-89.8 | unit | The `four-tools` help body ends with `HELP_SENTENCE` and still contains the MEU-59/60/66 sentences. | 09 `:155-157`; D-19 | The `original-annotated` body still ends with the flatten sentence, so AC-67.25 is unchanged. |
| AC-89.9 | integration (Electron) | In the built app, with the newest shot auto-selected and no prior click, Shift+click the third. Three thumbs have `data-in-range`. Right-click a member → only `capture-filmstrip-menu-delete-batch` (`Delete 3 shots`). Accept with the seam failing the middle id → two thumbs are gone and the failed one remains. `capture-status` names the failed shot, and the seam's DELETE ledger order equals `RANGE_ORDER`. | 09 `:794-797`; E2 | Cancel on a second batch sends no DELETE (the ledger is unchanged). |
| AC-89.10 | unit | `toggleSelection` adds an absent id, removes a present one, and returns the result in `orderedIds` order whatever order the ids were ticked in. | D-25 | An id not in `orderedIds` returns the selection unchanged. |
| AC-89.11 | integration | `CHECK`: every row has one checkbox before its thumb in document order, labelled `Select {full name}`, unchecked on open, and outside the thumb button (the thumb's text has no `Select`). Ticking B and then D checks both, gives B and D `RANGE_MARK`, leaves `aria-current` on A, and shows `2 shots selected`. Ticking B again unticks it. A plain thumb click clears every tick. | Mat 2026-10-16; D-25 | A single tick shows the tick but no `RANGE_MARK` and no count (membership counts only above 1). |
| AC-89.12 | integration | With unsaved marks on the editor's shot, ticking boxes shows no discard confirm and keeps the shot, its marks and `data-dirty`. A Shift+click on D's box after ticking B ticks B, C and D, and the editor stays on A. | D-25 | — |
| AC-89.13 | integration | Non-contiguous batch: tick D, then B. Right-clicking B gives only `Delete 2 shots`. Accepting sends DELETE `shot-b` and then `shot-d` (`RANGE_ORDER`, not tick order), one at a time. The editor keeps A, and `capture-status` shows `Deleted 2 shots.`. | 09 `:795`; D-25 | Unticking the middle of a Shift-click range of 3 gives `Delete 2 shots`. |
| AC-89.14 | integration | `CHECK` follows `locked`: while the batch confirm strip is open every checkbox is disabled. After Cancel they are enabled and the ticks are unchanged. | `CONFIRM_EXCLUSIVITY`; D-25 | — |
| AC-89.15 | integration (Electron) | In the built app, every row's checkbox is visible and sits left of its thumb (bounding boxes). Tick the first and third shots, then right-click the third → only `Delete 2 shots`. Accept → both are gone, the second remains, and the seam's DELETE ledger is first then third. | Mat 2026-10-16; E2; D-25 | — |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Shift-click range; editor = last clicked | Spec | 09 `:794` |
| Anchor behaviour on repeated Shift-clicks | Research-backed | APG Listbox; Explorer (D-15) |
| Shift-click with unsaved marks | Local Canon | Reuse `chooseItem`'s discard confirm (D-15) |
| Batch menu content and one confirm | Spec | 09 `:795` |
| Order and failure reporting | Spec | 09 `:795`; `BATCH_DELETE`, `BATCH_RESULT` (D-18) |
| Range visuals and announcement | Local Canon | `RANGE_MARK`, `RANGE_STATUS` (D-16) |
| Ctrl toggle, keyboard range | Human-approved scope | Out of scope (D-17) |
| Toolbar Delete while a range is active | Local Canon | Targets the editor's shot only, as today (D-14) |
| Checkbox selection beside each thumb | Human request | Mat 2026-10-16 (`FILMSTRIP_LOOK` round 1); `CHECK`, `CHECK_TOGGLE` (D-25) |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/capture/capture-filmstrip-select.ts` | new | `rangeBetween`; `toggleSelection` (D-25) |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modify | `BATCH_DELETE` (`deleteCaptures`); `deleteCapture` unchanged |
| `ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx` | modify | Shift-click (`onSelect(id, { extend })`), `RANGE_MARK`, `MENU_ITEMS_BATCH` choice; `CHECK` (D-25) |
| `ui/src/renderer/src/features/capture/CaptureFilmstripMenu.tsx` | modify | Batch item |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `RANGE`, `RANGE_DIRTY`, `RANGE_STATUS`, batch `DELETE_CONFIRM_TEXT`, `BATCH_RESULT`, `NEXT_SELECTION`; `CHECK_TOGGLE` (D-25) |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | `HELP_SENTENCE` (end of `four-tools`) |
| `ui/tests/unit/capture-filmstrip-select.test.ts` | new | AC-89.1, AC-89.10 |
| `ui/tests/unit/capture-batch-delete.test.ts` | new | AC-89.7 (`deleteCaptures` with an injected `remove` and a mocked `queryClient`) |
| `ui/tests/unit/capture-filmstrip-actions.behavior.test.ts` | modify (append only) | AC-89.2–89.6, AC-89.11–89.14 |
| `ui/tests/unit/capture-help-content.test.ts` | modify (append only) | AC-89.8 |
| `ui/tests/e2e/capture-filmstrip-actions.test.ts` | modify (append only) | AC-89.9, AC-89.15 |
| `ui/tests/e2e/test-ids.ts` | modify (append only) | MEU-89 `NEW_TESTIDS` block |

### Shared (both MEUs)

| File | Action | Summary |
|------|--------|---------|
| `docs/build-plan/06-gui.md` | modify (row 9) | Preload listing (`:96` block) gains the `writeClipboardImage` line |
| `docs/build-plan/gui-actions-index.md` | modify (D-25) | The `capture:batch_delete` label also names ticked shots; the REST/IPC cell is unchanged |
| `docs/build-plan/09-screenshot-capture.md` | modify (row 9) | One "Session 38 plan" note line under each of the two sections, naming the resolved contracts (D-10, D-11, D-15, D-18); the rule rows are unchanged |
| `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md` (rendered) | modify | `execution_plan` (plan time), then status at H1/H2 |
| `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md` | modify (H1/H2) | Session 38 row status |
| `.agent/context/current-focus.md`, `.agent/context/known-issues.yaml`, `docs/execution/metrics.md` | modify (H1/H2) | Focus, issue resolution, metrics row |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Ctrl/Cmd-click toggle selection | out-of-scope | — | 09 `:794` names Shift-click only; triage D-59 ("A Ctrl toggle is a plan-time option, not in scope by default"); Human-approved registered scope (USER_EXPLICIT 2026-10-14). Non-contiguous selection now comes from `CHECK_TOGGLE` (D-25); Ctrl-click itself stays out |
| Keyboard range selection (Shift+Arrow) | out-of-scope | — | 09 `:794` (Shift-click); Human-approved registered scope. D-17 offers a follow-up issue |
| Open file / Show in folder menu items | out-of-scope | — | 09 `:781` lists exactly three items; the user replaced the earlier "per-thumb menu" idea with the registered scope (USER_EXPLICIT 2026-10-14) |
| Copy of the annotated image | out-of-scope | — | 09 `:781` "Copy image"; D-10 (the original), flagged for veto |
| Native (OS) context menu via `Menu.popup` | out-of-scope | — | D-8: G27 keeps renderer UI in the renderer; an in-DOM menu is testable under E2 |
| Batch Copy (paths/images of a range) | out-of-scope | — | 09 `:795` ("the context menu shows only Delete") |
| Server-side batch DELETE endpoint | out-of-scope | — | 09 `:795` ("removes run in order"); `PRODUCT_SCOPE` keeps `packages/` unchanged |
| Percent-encoding the existing `deleteCapture`/`flattenCapture`/`revertCapture` calls | out-of-scope | — | Session 30 reflection RULE-2 binds new code; changing existing calls is outside the 09 `:775-798` contract. New calls here encode |

---

## BUILD_PLAN.md Audit

This project changes these build-plan homes:

1. **Plan time:** `gui-actions-index.md` `ACTION_ROWS` (09 `:783` requires plan-time rows). `meu-status.yaml` `execution_plan` for MEU-88/89, then render.
2. **Row 9:** `06-gui.md` preload listing; one note line in each of the two 09 sections; nothing in 11 (CP rows are locked; no layout change).
3. **H1/H2:** MEU statuses through `meu_status.py`, never by hand in `BUILD_PLAN.md`.

`docs/build-plan/11-page-layout.md` stays unchanged, which `scope` proves.

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s38-build-plan-audit.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s38-build-plan-audit.txt; exit $code
```

---

## Verification Plan

> [!IMPORTANT]
> Every command runs through `rtk proxy` and writes to `C:/Temp/av-kit/`. `validate-task.ps1` holds the exact procedure for each check. Each check removes `ELECTRON_RUN_AS_NODE` first.

### 0. Task contract (planning time; re-run at H2)

```powershell
rtk proxy uv run python tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier --task docs/execution/plans/2026-10-14-capture-filmstrip-actions/task.md *> C:/Temp/av-kit/s38-task-lint.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s38-task-lint.txt; exit $code
```

### 1. Prerequisites and baseline (row 0)

`-Check prereq` covers: no graph directory and no `headroom` on PATH; MEU-57 `approved`; MEU-88 and MEU-89 `pending`; the Electron binary present (`ui/node_modules/electron/path.txt`). `-Check baseline` writes `baseline.sha` and records the baseline Vitest JSON and Playwright JSON for `COUNT_FLOORS`.

### 2. Red (rows 2, 6)

`-Check red88` / `-Check red89` run the named new and amended test files. They pass only when every failure is an assertion failure and every failing test id belongs to that MEU's ACs. A collection or import error outside the declared new modules fails the check (Stop condition S4). For the Electron Red, the check builds first and then runs the MEU's `-g` filter.

### 3. Green (rows 3–4, 7)

`-Check green88` / `-Check green89` run the same files and require zero failures. Electron specs run after `npm --prefix ui run build`.

### 4. Targeted gates (rows 5, 8)

`-Check gate88` / `-Check gate89`: `ui-types`, `ui-lint`, the MEU's unit files plus the doc-reading suites (`gui-actions-audit`, `layout-canon`, `queue-canon`), build, and the MEU's Electron spec with `--repeat-each=10`.

### 5. Full D6 gate (H1-2)

`-Check gate` runs PROFILE D6's UI stages fresh and in order: `npm --prefix ui ci` + Electron `install.js`, `ui-types`, `ui-lint`, `ui-build`, the primitive-harness build (`out-e2e`), `ui-tests` (JSON), `ui-electron` (JSON), `state-render`, `task-contract`, then the source audit over the changed renderer/main files (`TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b`). It checks `COUNT_FLOORS` and records `tested_commit`, the lockfile hash and the Electron/Node versions in the receipt. The `py-*`, `mcp-*` and `openapi` stages are skipped on the basis of `scope` (no file under `packages/`, `mcp-server/` or `openapi.committed.json` changed); the receipt records that skip.

### 6. Product scope (H1-4)

`-Check scope` takes every path changed since `baseline.sha` anywhere in the repository (committed diff plus uncommitted and untracked files). Each must be a backticked path in a Files Modified table or a closeout output: a file under the plan directory, a `2026-10-14-capture-filmstrip-actions-*` handoff or reflection, or the rendered `meu-registry.md`, `known-issues.md` or `known-issues-archive.md`. So root files such as `pyproject.toml` and `uv.lock`, and any unlisted source or test, fail it. It also refuses any change under `packages/`, `mcp-server/`, `tools/`, `native/`, `openapi.committed.json` or `docs/build-plan/11-page-layout.md`, and any `ui/src/main/` file outside the four named. `plan_checks.py selftest` holds negative cases for each.

### 7. Closeout (H1-5 to H2)

Through `tools/validate_closeout_artifacts.py` (`--handoff`, `--ac-coverage-only`, `--review-state-only`, `--approved-state-only`, `--reflection`) and `lint_task_contract.py`, with the exact commands in `task.md`.

### 8. OpenAPI drift (G8)

Not applicable: `packages/api/` is outside `PRODUCT_SCOPE`. `scope` proves it, `pyproject.toml` and `uv.lock` are unchanged, which is the recorded skip basis for the Python and MCP stages.

---

## GUI Element Compliance Check

The §4A reference files are not shipped (`docs/gui-element-reference.md` and its siblings are absent: `gui-refs-not-shipped`, as in Sessions 29/30). Feedback tiers follow the local usage in earlier plans: T0 means an immediate visual state change, and T1 means an inline status message.

| Element | Variant / size | States | Feedback tier (G35) | Standard | E2E |
|---|---|---|---|---|---|
| Thumbnail menu (`capture-filmstrip-menu`) | `QueueCardMenu` surface | closed / open (pointer or keyboard) | T0 | G27, APG Menu | AC-88.12 |
| Copy full path item | menuitem | — | T1 (`COPY_STATUS`) | G35 | AC-88.12 |
| Copy image item | menuitem | — | T1 (`COPY_STATUS`) | G35 | AC-88.12 |
| Delete item | menuitem, `text-error` | — | T1 confirm strip, then T0 removal | CP 23/24 | AC-88.12 |
| Delete {n} shots item | menuitem, `text-error` | — | T1 batch confirm, then T1 `BATCH_RESULT` | CP 23/24, G35 | AC-89.9 |
| Range marking on `capture-filmstrip-item` | ring + sr-only suffix | in range / not | T0 (+ `RANGE_STATUS` text) | 11 CP4 | AC-89.9 |
| Selection checkbox (`capture-filmstrip-check`) | native checkbox, left of each thumb | unticked / ticked / disabled while locked | T0 (+ `RANGE_STATUS` text) | 11 CP4, CP 23/24 | AC-89.15 |
| Confirm strip (existing) | existing buttons | single / named / batch text | T1 | CP 23/24 | AC-88.12, AC-89.9 |

The `source-audit` stage enforces G32/G33. E2 is met: every new interactive element has a registered test id and an Electron assertion.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, MEU-57 is not `approved`, or MEU-88/89 is not `pending` | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | In real Electron, the `png` field does not arrive in main as a `Uint8Array` (structured clone), so `IMAGE_PAYLOAD` rejects valid copies | Stop Green. Decision Brief: accept `ArrayBuffer` and wrap it in main, or send a base64 string. Never loosen the schema to `unknown`. |
| S4 | A Red is not an assertion failure (collection or import error outside the declared new modules) | Fix the test setup only, then re-prove Red. |
| S5 | Chromium in Electron does not deliver the ContextMenu key or Shift+F10 to the renderer as `keydown`, so AC-88.12(c) cannot pass | Stop. Decision Brief: open from the `contextmenu` event alone, with evidence of what Chromium dispatches. |
| S6 | A gate failure that is not a product defect (environment, flaky infrastructure) | Record the evidence and present a Decision Brief; never mark the row `[x]`. |
| S7 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |

## Decision Log

Research engine for this plan: `native` (Claude Code `WebSearch`, 2026-10-14). Grouping §8 rows D-1 to D-7 are carried forward unchanged and are listed in the reflection with stage `grouping`. D-1's condition ("after Session 30's execution review approves") is met: Session 30 was approved and closed on main at `7861020`. D-6's scoping review was not run for this batch; the plan review below covers MEU scope. This plan's ids start at D-8.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "In-DOM menu component or native Electron Menu.popup?"
    resolution: autonomous
    class: two-way
    chosen: "A new in-DOM CaptureFilmstripMenu following the APG menu pattern and the QueueCardMenu precedent (MENU_PATTERN); not a shared extraction"
    source_tag: Research-backed
    precedents: ["ui/src/renderer/src/components/queue/QueueCardMenu.tsx — role=menu, roving focus, Escape restores focus, outside pointer-down closes", "docs/build-plan/09-screenshot-capture.md:785 — tests require keyboard access"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/menubar/ — menu/menuitem roles, focus on open, arrow/Home/End, Escape returns focus", "https://www.electronjs.org/docs/latest/api/menu — Menu.popup is a main-process native menu (needs IPC per item, not visible to Playwright DOM queries)"] }
    reasoning: "The in-DOM menu is testable in jsdom and Playwright, needs no extra IPC, and matches the app's existing menu. A native popup would need a main-side menu plus a new channel per action and cannot be asserted through the DOM. Extracting a shared menu from QueueCardMenu would touch the queue pages outside this scope."
  - id: D-9
    stage: planning
    question: "Which keys open the menu, and where is a keyboard-opened menu placed?"
    resolution: autonomous
    class: two-way
    chosen: "contextmenu event, keydown ContextMenu, keydown Shift+F10, idempotent per thumb; keyboard opens anchor to the thumb rect (MENU_OPEN, MENU_ANCHOR)"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:785 — keyboard access (context-menu key)"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/API/Element/contextmenu_event — fired by right-click or the context-menu key; keyboard-fired events can carry zero coordinates", "https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-accelerators — Shift+F10 is the Windows equivalent of the Menu key"] }
    reasoning: "Handling the keys explicitly does not depend on how Chromium or Playwright's synthetic keys produce contextmenu, and idempotence absorbs the paired event. Stop condition S5 covers the case where Electron never delivers the keydown."
  - id: D-10
    stage: planning
    question: "Copy image: the original or the annotated image?"
    resolution: autonomous
    class: two-way
    chosen: "The original (variant=original), matching the thumbnail and Copy full path; flagged for veto"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx — the thumbnail shows /captures/:id/image (original)", "docs/build-plan/09-screenshot-capture.md:781 — 'Copy image' on the thumbnail"]
    research: { engine: none, sources: [] }
    reasoning: "The menu is on the thumbnail, and the thumbnail shows the original, so copying what the user sees is the least surprising choice. The annotated copy is one more menu item and a two-way change if Mat wants it."
  - id: D-11
    stage: planning
    question: "How do image bytes reach the clipboard, and how is a WebP or JPEG original handled?"
    resolution: autonomous
    class: two-way
    chosen: "The renderer fetches the original through the authorized image route, re-encodes non-PNG to PNG (OffscreenCanvas), and sends PNG bytes over a strict write-clipboard-image channel; main decodes with nativeImage.createFromBuffer and calls clipboard.writeImage (IMAGE_PAYLOAD, MAIN_IMAGE_WRITE, RENDERER_PNG)"
    source_tag: Research-backed
    precedents: ["ui/src/main/capture-picker.ts:466-483 — nativeImage + clipboard.writeImage in main", "ui/src/main/ipc.ts:70 — strict zod per channel", "docs/build-plan/09-screenshot-capture.md:601 — images are fetched through the authenticated route, never file://"]
    research: { engine: native, sources: ["https://www.electronjs.org/docs/latest/api/native-image — supported formats are PNG and JPEG", "https://www.electronjs.org/docs/latest/api/clipboard — clipboard.writeImage(image) in main", "https://www.electronjs.org/docs/latest/tutorial/ipc — invoke arguments use the structured clone algorithm (typed arrays survive)", "https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas/convertToBlob — PNG encode in the renderer"] }
    reasoning: "Sending a path for main to read would let the renderer choose a file for main to open, which is a wider trust surface than bytes checked by a strict schema, and it would still fail on WebP. The bytes route reuses the authorized fetch the thumbnail already uses. The 64 MiB cap bounds a hostile payload. Stop condition S3 covers a typed-array arrival failure."
  - id: D-12
    stage: planning
    question: "Does right-clicking a thumbnail select it?"
    resolution: autonomous
    class: two-way
    chosen: "No; the menu acts on the right-clicked shot and leaves selection, marks and dirty state alone (MENU_TARGET, SINGLE_DELETE)"
    source_tag: Research-backed
    precedents: ["ui/src/renderer/src/features/capture/CapturePage.tsx:503-515 — selecting a shot can raise the discard confirm, which a menu must not trigger"]
    research: { engine: native, sources: ["https://code.visualstudio.com/docs/getstarted/userinterface — Explorer context menu acts on the right-clicked item without opening it"] }
    reasoning: "Selecting on right-click would raise the discard confirm on every right-click with unsaved marks, and would lose the editor's place to copy a path. Acting on the target keeps the editor untouched."
  - id: D-13
    stage: planning
    question: "Can the menu open while a confirm strip is open?"
    resolution: autonomous
    class: two-way
    chosen: "No; MENU_LOCK, and opening a confirm closes an open menu"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CapturePage.tsx:1076 — CONFIRM_EXCLUSIVITY disables the filmstrip while a confirm is open"]
    research: { engine: none, sources: [] }
    reasoning: "This extends the existing exclusivity rule to the new surface; two pending destructive targets would make the confirm text ambiguous."
  - id: D-14
    stage: planning
    question: "How does Delete from the menu reuse the existing confirm, and what does it say for a non-selected shot or a batch?"
    resolution: autonomous
    class: two-way
    chosen: "Keep ConfirmKind 'delete' and its test ids; add DELETE_TARGETS; the text names the shot when it is not the selected one, and the count for a batch (DELETE_CONFIRM_TEXT); toolbar Delete still targets the editor's shot only"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CapturePage.tsx:1043-1049 — delete confirm spec", "docs/build-plan/09-screenshot-capture.md:781, :795 — reuse the existing confirm; one confirm naming the count"]
    research: { engine: none, sources: [] }
    reasoning: "Reusing the kind keeps every existing delete test and E2E id valid. 'Delete this capture' would be wrong for a shot other than the one in the editor, so the text names it."
  - id: D-15
    stage: planning
    question: "Range anchor semantics and Shift-click with unsaved marks"
    resolution: autonomous
    class: two-way
    chosen: "The anchor is the last plain-clicked shot, or the editor's current shot when there is none (the auto-selected newest shot on load, or the shot chosen after the anchor's shot is removed), and stays fixed across Shift-clicks; the range is the inclusive slice in filmstrip order; Shift-click goes through chooseItem's discard confirm, and Cancel applies nothing (RANGE, rangeBetween, RANGE_DIRTY)"
    source_tag: Research-backed
    precedents: ["docs/build-plan/09-screenshot-capture.md:794 — Shift-click from the current shot; editor shows the last-clicked shot"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/listbox/ — Shift+click selects contiguous items from the most recently selected item (anchor)", "https://learn.microsoft.com/en-us/windows/apps/design/controls/listview-and-gridview — Extended selection: Shift+click selects a contiguous range from the anchor"] }
    reasoning: "This matches what Windows users expect. Moving the editor means leaving the current shot, so the existing unsaved-marks protection must apply."
  - id: D-16
    stage: planning
    question: "How is the range shown and announced?"
    resolution: autonomous
    class: two-way
    chosen: "data-in-range plus an accent ring, an sr-only ', selected' suffix, and 'N shots selected' in capture-status at the lowest precedence (RANGE_MARK, RANGE_STATUS)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/11-page-layout.md:44 — CP4 keeps the accessible full name on capture-filmstrip-item", "ui/src/renderer/src/features/capture/CapturePage.tsx:1111-1124 — editorStatus precedence"]
    research: { engine: none, sources: [] }
    reasoning: "The thumbs stay buttons (CP 14/15 locked), so aria-selected (a listbox/grid attribute) does not apply. An sr-only suffix plus the status count gives the same information without changing roles."
  - id: D-17
    stage: planning
    question: "Ctrl toggle and keyboard range selection"
    resolution: autonomous
    class: two-way
    chosen: "Out of scope; offer Mat a follow-up issue for keyboard range selection in the next report"
    source_tag: Local Canon
    precedents: ["known-issues CAPTURE-FILMSTRIP-MULTISELECT triage D-59 — Ctrl toggle not in scope by default", "docs/build-plan/09-screenshot-capture.md:794 — Shift-click only"]
    research: { engine: none, sources: [] }
    reasoning: "The user chose the registered scope on 2026-10-14. Keyboard users can still delete one shot at a time through Shift+F10, so nothing becomes unreachable."
  - id: D-18
    stage: planning
    question: "Batch delete order, failure handling and resulting selection"
    resolution: autonomous
    class: two-way
    chosen: "Sequential DELETEs in filmstrip order with encoded ids, continue past failures, invalidate once; clear the range; move the selection to the newest survivor if the editor's shot went; report 'Deleted N shots.' or name every failure (BATCH_DELETE, BATCH_RESULT, NEXT_SELECTION)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/09-screenshot-capture.md:795 — removes run in order and report per-shot failures", "docs/execution/reflections/2026-10-02-capture-flatten-backup-reflection.md:178 — RULE-2 percent-encode path parameters"]
    research: { engine: none, sources: [] }
    reasoning: "Sequential requests give a deterministic order that a test can assert, and avoid racing the service's file lock. Continuing past a failure means one locked file does not block the rest. Keeping failures in the range was weighed and rejected: a stale range after the catalog refresh is harder to read than a clear message."
  - id: D-19
    stage: planning
    question: "Do the hidden gestures need help text?"
    resolution: autonomous
    class: two-way
    chosen: "One HELP_SENTENCE appended to the four-tools help body (not original-annotated, which AC-67.25 pins to end with the flatten sentence)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/09-screenshot-capture.md:155-157 — HelpCard topics", "Session 29 ZOOM_HELP_SENTENCE — new gestures get one help sentence"]
    research: { engine: none, sources: [] }
    reasoning: "Right-click, Shift+F10 and Shift-click are not visible affordances, and one sentence in the existing help is enough to make them discoverable."
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
  - id: D-23
    stage: execution
    question: "The plan has the page pass deleteCaptures a remove function. Where does the encoded per-shot DELETE live?"
    resolution: autonomous
    class: two-way
    chosen: "A removeCapture export in capture-commands.ts next to deleteCapture: one DELETE /captures/{encodeURIComponent(id)} with no catalog refresh, so deleteCaptures is the only place that invalidates"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/capture-commands.ts — every capture REST call lives here", "Session 30 reflection RULE-2 — path parameters are percent-encoded"]
    research: { engine: none, sources: [] }
    reasoning: "Keeps REST paths out of the page component and makes the invalidate-once rule hold by construction. deleteCapture stays unchanged, as the plan requires."
  - id: D-24
    stage: execution
    question: "The first full gate ran every test green (Vitest 848/848) and then failed gate-ui-tests with 'receipt C missing'. Fix the harness or the check?"
    resolution: autonomous
    class: two-way
    chosen: "Fix the PowerShell array in validate-task.ps1: $extra = @(if … { \"receipt path\" }); the vitest_ok check and its receipt scan are unchanged"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-capture-filmstrip-actions/walkthrough.md §Gate — D-24, reproduced in isolation"]
    research: { engine: none, sources: [] }
    reasoning: "$(if … { @(x) }) unrolls a one-element array to a string, and splatting a string passes one character per argument, so plan_checks.py read 'C' as the receipt path. The fix restores the intended argument; nothing about what the gate accepts changed."
  - id: D-25
    stage: execution
    question: "FILMSTRIP_LOOK round 1 (2026-10-16): Mat found Shift-click gave no visible result (L5) and asked for a check mark left of each image for multi-select, like zorivest. How does selection change?"
    resolution: human
    class: two-way
    chosen: "Add CHECK and CHECK_TOGGLE: a checkbox left of each thumb toggles that shot in the selection set without moving the editor; Shift-click on a thumb or a box still selects a range; a plain thumb click clears the ticks (Explorer item check boxes); the batch menu, confirm and delete apply to the set in filmstrip order. HELP_SENTENCE is unchanged (the box is a visible affordance). L3 is re-checked with explicit focus steps."
    source_tag: Human
    precedents: ["Mat, FILMSTRIP_LOOK answer 2026-10-16 - 'The multi image selection should enable check mark to the left of the images so they can be multi selected'", "P:/zorivest/ui/src/renderer/src/features/trades/TradesTable.tsx:263-291 - selection checkbox column prepended to each row", "Windows Explorer item check boxes - clicking an item selects only it, its box toggles it", "USER_EXPLICIT 2026-10-16 - all recommendations auto-approved for this session"]
    research: { engine: none, sources: [] }
    reasoning: "The Shift-click range works (AC-89.2-89.9 pass in jsdom and Electron) but its only marks are a faint ring and a status line, so Mat saw nothing. A visible box per row is the affordance Mat asked for and makes the selection state obvious. Keeping the set in filmstrip order leaves BATCH_DELETE's ordering contract intact, and keeping plain click as 'select one, clear ticks' leaves AC-89.2 unchanged. It partly supersedes the Ctrl-click out-of-scope row; that is a human scope change, recorded here."
```

---

## Research References

- WAI-ARIA APG Menu and Menubar pattern: https://www.w3.org/WAI/ARIA/apg/patterns/menubar/
- WAI-ARIA APG Listbox pattern (Shift+click range): https://www.w3.org/WAI/ARIA/apg/patterns/listbox/
- MDN `contextmenu` event: https://developer.mozilla.org/en-US/docs/Web/API/Element/contextmenu_event
- Electron `clipboard`: https://www.electronjs.org/docs/latest/api/clipboard
- Electron `nativeImage` (PNG and JPEG only): https://www.electronjs.org/docs/latest/api/native-image
- Electron IPC (structured clone): https://www.electronjs.org/docs/latest/tutorial/ipc
- Electron `Menu.popup`: https://www.electronjs.org/docs/latest/api/menu
- MDN `OffscreenCanvas.convertToBlob`: https://developer.mozilla.org/en-US/docs/Web/API/OffscreenCanvas/convertToBlob
- Windows list selection modes: https://learn.microsoft.com/en-us/windows/apps/design/controls/listview-and-gridview
- Windows keyboard accelerators (Shift+F10): https://learn.microsoft.com/en-us/windows/apps/design/input/keyboard-accelerators

## Validation stage contract

The checks bind to PROFILE D6 (`.agent/docs/commands.md:194-230`):

- **Static:** `ui-types`, `ui-lint` and the `source-audit`.
- **Targeted:** the Red/Green files and the per-MEU gates.
- **Fresh full:** `-Check gate` (H1-2). It runs all UI stages from `npm ci`, and covers `state-render` and `task-contract`. The `py`, `mcp` and `openapi` stages are skipped on the `scope` basis.
- **Runtime:** `FILMSTRIP_LOOK` (manual, Mat).

Every check runs in `pwsh` from the worktree root (`P:/av-kit-wt/s38-capture-filmstrip-actions`) and writes raw receipts under `C:/Temp/av-kit/s38-*`. The handoffs carry `evidence.v1` records.

Input identity is obtained independently by `-Check gate`. It records `git rev-parse HEAD`, the uncommitted product paths (`git status --porcelain --untracked-files=all -- ui docs/build-plan`) with a SHA-256 of each one's working-tree content, untracked files included, the `ui/package-lock.json` SHA-256, `node --version` and the installed Electron version, in `gate-result.json`. The execution review reads the gate receipt for the commit under review. Any code change after the gate re-runs `-Check gate` before the next review round. Intermediate reuse is disabled: partial runs never satisfy the full gate.
