---
project: "2026-11-26-capture-key-inbox-scrollbars"
date: "2026-11-26"
source: "Mat's three Capture findings of 2026-11-26, registered at triage as CAPTURE-HOTKEY-TEXT-HARDCODED (D-1400, MEU-165), CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS (D-1401, MEU-166) and CAPTURE-ZOOM-NO-SCROLLBARS (D-1402, MEU-167); homes in docs/build-plan/09-screenshot-capture.md §Capture key in texts, §Catalog follows the inbox folder and §Viewport scroll bars; Session 103 of .agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md (D-1410, D-1411)"
meus: ["MEU-165", "MEU-166", "MEU-167"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: the Capture page names the saved key, lists the current inbox folder, and shows scroll bars on a zoomed image

> **Project**: `2026-11-26-capture-key-inbox-scrollbars`
> **Build Plan Section(s)**: 09 §Capture key in texts (anchor `capture-key-in-texts`, matrix 9.48), 09 §Catalog follows the inbox folder (anchor `catalog-follows-the-inbox-folder`, matrix 9.49) and 09 §Viewport scroll bars (anchor `viewport-scroll-bars`, matrix 9.50), all in `docs/build-plan/09-screenshot-capture.md`, registered at triage on 2026-11-26. Parent canon: 09 §Viewport zoom (the Pan gestures row), 09 §Catalog (`scan_inbox`, `list_shots`, `get_shot`).
> **Status**: `draft`. `plan_to_exec_gate: human`. Mat ruled the grouping's D-1413 on 2026-11-26: 'drafts stand'. In the same message he gave the word to execute after Session 104, once this plan's review approves it: 'go for 104 after the reviews finish and then execute rest as you see fit'. Round 1 of the plan review asked for changes (F1 to F4); this draft carries the corrections. Nothing commits or pushes without Mat's words.

---

## Goal

**Goal anchor:** after this session the Capture page does three things it does not do today.

1. **It names the key the user saved.** Every in-app text that names the capture key (the Capture empty state, five lines of the Capture help, the Settings startup help and step 1 of the Capture quick start) shows the saved `capture.hotkey`, with no restart. `F2` stays the default, and with the default key every text reads as it does today.
2. **It lists the folder the user chose.** `scan_inbox` and `list_shots` return only the shots whose original file is directly inside the current inbox folder. Rows of other folders are kept with their links and come back when the user switches back. The list refreshes when the inbox folder is saved, and a selected shot that left the list is cleared.
3. **It shows where a zoomed view is.** On each axis where the zoomed image is larger than the frame, a scroll bar at the bottom or the right shows the position of the view, and a drag of its thumb moves the view inside the pan limits. Wheel zoom, Space+drag and middle-button drag are unchanged.

No IPC channel, preload surface or MCP tool changes. `GET /captures` keeps its reply shape. Vitest and pytest on the dev PC and four Electron tests on the mini-air host prove it, with no manual check.

**Why.**

- **Mat's three findings, 2026-11-26**, as the register holds them: the page tells the user to press a key that no longer captures (D-1400); shots from a folder the user left stay in the list, mixed with the new folder's shots (D-1401); and "Should the zoomed Capture image have scroll bars?" was answered by Mat: "Yes. On each axis where the zoomed image is larger than the frame, a scroll bar at the bottom or the right shows where the view is and moves it. Space+drag, middle-drag and wheel zoom keep working." (D-1402).
- **Mat, 2026-11-26 (D-1411):** "use fleet member mini air for E2E testing during execution".
- **Mat, 2026-11-16:** "This should be done with framework and scripts!" So the proof is tests in the gate.

**What the code shows (plan-time reads at `HEAD` `c0acc89`, one worktree):**

- **The key literals.** The renderer holds `F2` as user text in six files: `CapturePage.tsx:107` (`EMPTY_STATE = 'Press F2 or Capture region'`), `capture-help-content.ts:7`, `:11`, `:12`, `:36`, `:37`, `settings-help-content.ts:27` and `quick-start.json:154`. `useCaptureSettings.ts:28` (the default) and `registry/shortcuts.ts:136`, `:160` (the reserved chord) also hold it and stay.
- **What reads the real key today.** The key cap (`CapturePage.tsx:855-860`) reads main's `getHotkeyStatus()`, but its effect depends on the draft key (`settings.form.hotkey`), and main applies a saved key on a 1 s poll, so after Save the cap keeps the old key until the page is mounted again. The in-use banner (`:2222`) names the draft key, so it changes while the user types.
- **The settings hook.** `useCaptureSettings` (`useCaptureSettings.ts`, CRLF, 153 lines) returns `form` (saved values with the draft over them) and no saved-only value. `save` sends only the changed leaves and invalidates the capture settings query, nothing else. `SettingsPage.tsx:356` already calls the hook.
- **The help card.** `HelpCard.tsx:114` reads `QUICK_START[feature]` itself, and `help-quick-start.test.tsx` renders it with no query client, so the card cannot call a query hook; it takes the key as a prop.
- **Raw readers of the quick start.** `ui/tests/e2e/help-quick-start.test.ts:135` compares the rendered steps with the raw JSON texts, and `ui/tests/help-shots/help-shots.shots.ts:62-65` hashes the raw JSON steps into the shots manifest.
- **The catalog.** `CaptureService.scan_inbox` (`capture.py:651-746`) adds rows for the files of the current inbox, deletes a row only when its file is gone (`:706-709`) and returns every row (`:746`). `list_shots` (`:862-871`) returns every row. The by-id lookups (`:877`, `:1685`, `:1729`, `:1795`, `:1892`, `:2003`) have no inbox check; only the path-based entries (`:897`, `:1621`) call `_require_inbox_file`. The service already uses the predicate `shot.original_path.parent == inbox` for name collisions (`:1578`, `:2080`).
- **The page and the catalog.** A capture settings save does not invalidate the `['captures']` query (`useCaptureCatalog.ts`, `QUERY_KEY`); the list catches up on its 5 s poll. A selection whose shot left the catalog is not cleared (`CapturePage.tsx:663-682` selects the newest shot only when nothing is selected).
- **The viewport.** The frame is `relative overflow-hidden`; the image box is placed by `viewTransform` (`capture-fit-map.ts:98`), and pan is a clamped offset. Nothing shows the position of the view. No test asserts that scroll bars are absent.
- **Existing pins that change by name (D-1422).** `capture-page.test.ts` AC-39.13 scans the page source for `Press F2 or Capture region` (`:328`) and the help source for the topic titles `When F2 is in use` and `Close to tray keeps F2` (`:112`, `:117`, read at `:333`). `settings-page.test.ts` AC-61.16 scans `settings-help-content.ts` for `F2` (`:771`). The One source row forbids the literal in those sources, so these four expectations change to the token form. Every rendered-text pin keeps passing unchanged, because the default key gives today's text.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and ui/graphify-out/ are absent (2026-11-26). The change is nine renderer files, one service module, new test files and docs, all read at plan time; a bypass class."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. See `.agent/docs/harness-profiles.md` and the Claude Code block of `.agent/context/harness.local.md`.
  - Validation goes through `rtk proxy` with the receipt pattern. Task-cell commands run in pwsh.
  - Receipts go to `C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/`. Execution receipts start `cki-`. Planning receipts are in `C:/Temp/av-kit/2026-11-26-plans/s103/`.
  - Every row sets `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`, and clears `ELECTRON_RUN_AS_NODE`.
  - Vitest runs from pwsh after `Set-Location 'P:\av-kit\ui'`, never from the Bash tool, and returns to `P:\av-kit`.
  - `TMP` and `TEMP` are set to the undated `C:/Temp/av-kit/s103-tmp` for every pytest step.
- **Electron E2E runs on mini-air (D-1411), never on the dev PC.** Each E2E row runs `uv run python tools/e2e_remote.py run <commit>` per the run book `.agent/docs/e2e-remote-host.md`.
  - Work that is not committed goes as a snapshot commit that moves no ref, made by this plan's copy of `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/snapshot-commit.py`.
  - The evidence of a run is the tool's last stdout line, `e2e-remote: <reason> exit=<n> run=<run-id> receipts=<folder>`, plus that receipt folder.
  - Exit 22 (`host-busy`) and 23 (`host-locked`) mean wait and rerun. They are never a pass.
  - A run takes about 40 minutes. It runs in the background and is waited on with Monitor; nobody polls the host by hand.
- **Working directory:** `P:/av-kit` on `main`. Use no branch and no worktree. Leave `.agent/fleet/hub` alone.
- **Cloud-local contract:** local build and unit tests; E2E on mini-air.
- **Reviewer:** Codex runs through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `cki-plan-2026-11-26-capture-key-inbox-scrollbars` and `cki-execution-2026-11-26-capture-key-inbox-scrollbars`.
  - Caps come from `.agent/review-limits.json`: 3 plan rounds and 6 execution rounds. This plan carries no `review_limits` block.
  - Claude wrote the plan, so the reviewer is from a different vendor. The fallback is Mat.
  - The dispatch console goes to its own console file, never into the run log.
- **Never in these rows without Mat's words:** commit, push, or writing an `approved` verdict. Mat pushes himself.
- **Never read:** user data (the models folder, the app database, the settings file, the real `~/Pictures/av-kit`), `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json`. Every Electron launch uses a scratch `AVKIT_APP_DATA`. No row stops a process by image name.

## Lane Ownership

The grouping's `## Session Ownership` gives this session tier 1 and these paths. D-1429 lists the paths outside it that the homes' rows force.

```yaml
capture-key-inbox-scrollbars:
  tier: 1
  owns:
    - ui/src/renderer/src/features/capture/
    - ui/src/renderer/src/features/settings/settings-help-content.ts
    - ui/src/renderer/src/components/help/quick-start.json
    - packages/core/src/avkit_core/services/capture.py
    - packages/api/src/avkit_api/routes/captures.py
    - ui/tests/e2e/capture-inbox.test.ts
    - docs/build-plan/09-screenshot-capture.md
    - docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/
```

**Sibling overlap (execution order 104, 103, 106, 105):**

| File | Other session | What this session does to it |
|---|---|---|
| `ui/src/renderer/src/components/help/HelpCard.tsx` | 105 owns it | Adds one optional prop and one line that picks the page |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | 106 owns `features/settings/` | One import and one argument of the help card |
| `ui/src/renderer/src/features/settings/settings-help-content.ts` | 106 shares it | The startup body takes the token; the file gains `settingsHelpSections(key)`; `SETTINGS_HELP_SECTIONS` becomes the default reading |
| `ui/src/renderer/src/components/help/quick-start.json`, `quick-start.ts`, `ui/tests/help-shots/help-shots.shots.ts` | 105 shares the quick start and retakes help images by script | Step 1 of the Capture page holds the token; `QUICK_START` becomes the default reading; the shots script hashes the default reading |

Sessions 105 and 106 run after this one, so they read these files as this session leaves them: a help text that names the capture key holds `{captureKey}`, and the exported constants are the default readings.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-165 Capture key in texts | `.agent/context/handoffs/2026-11-26-capture-key-inbox-scrollbars-MEU-165-handoff.md` |
| MEU-166 Catalog follows the inbox folder | `.agent/context/handoffs/2026-11-26-capture-key-inbox-scrollbars-MEU-166-handoff.md` |
| MEU-167 Viewport scroll bars | `.agent/context/handoffs/2026-11-26-capture-key-inbox-scrollbars-MEU-167-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-11-26-capture-key-inbox-scrollbars-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-26-capture-key-inbox-scrollbars-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline and plan-local scripts (row 0) | — | shared | `baseline.sha`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, the plan-local scripts |
| WP-2 | Electron Red on mini-air (row 1) | WP-1 | shared | The four E2E tests, the Red snapshot, the run receipts, `cki-e2e-base.json` |
| WP-3 | MEU-166 service (rows 2 and 3) | WP-1 | shared | The two pytest files; `capture.py` per `INBOX_SCOPE` |
| WP-4 | MEU-166 renderer (rows 4 and 5) | WP-3 | shared | The Vitest file; the hook and the page per `INBOX_SAVE_REFRESH` and `INBOX_SELECTION_LEFT` |
| WP-5 | MEU-165 (rows 6 and 7) | WP-4 | `compact_continue` | The two Vitest files and the four named expectation changes; the key leaf, the texts and the pages |
| WP-6 | MEU-167 (rows 8 and 9) | WP-5 | `compact_continue` | The two Vitest files; the geometry module and the bars |
| WP-7 | Electron proof on mini-air (row 10) | WP-2, WP-6 | shared | The proof snapshot and the run receipts |
| WP-8 | Canon, register and status (row 11) | WP-7 | shared | The 09 rows and Delivered notes, the three issues resolved, the three MEUs `ready_for_review` |
| WP-9 | Closeout (H1, H2) | WP-8 | `compact_continue` | The handoffs, the review, the reflection, the commit draft |

**Size (D-1431).** The grouping calibrates against `2026-11-17-ui-small-fixes` plus about half as much again for the service change. MEU-167 is one pure module of about 80 lines, about 70 lines in `CaptureViewport.tsx` and about 350 lines of tests. That is well under half a context, so MEU-167 stays in this session. The Electron cost is two full-suite runs on mini-air of about 40 minutes each, both in the background.

## User Review Required

> [!IMPORTANT]
> **No question is open for Mat in this plan.** D-1420 to D-1432 are reversible agent choices made under Mat's 2026-11-18 hand-over, each with its do-nothing option in §Decision Log. The grouping's D-1413 (do the four drafts stand as inputs) is ruled: Mat, 2026-11-26, 'drafts stand'.
>
> **What changes for you:**
>
> - **The key.** After you change the capture key and click Save, the empty state, the Capture help, the Settings startup help and step 1 of the Capture quick start name the new key at once. The key cap beside Capture region shows a key only when that key is registered; for up to five seconds after a save it is hidden while the main process applies the key. The in-use banner names the saved key, not the key you are typing. If main does not confirm the saved key by the end of that wait, or the app cannot read main's key status, the banner place says that the key is saved but not confirmed, and asks you to restart av-kit if the key does nothing (`CAPTURE_KEY_UNCONFIRMED`).
> - **The inbox.** After you save a new inbox folder, the list shows only that folder's shots, at once. If the shot you had open is not in the new folder, the page opens the newest shot of the new folder or shows the empty state. **Marks you had drawn but not saved on that shot are dropped** (D-1425). Nothing is deleted on disk, and the old folder's shots and saved marks come back when you switch back. A crop or a PNG copy that finishes after you saved another folder is not opened and shows no notice; its new file is in the old folder and shows when you switch back (`INBOX_RESULT_BOUND`).
> - **By id.** A shot outside the current inbox answers "not found" to the app, the API and the MCP tools, exactly like an unknown id (D-1424). While you are on another folder, the app does not read, change or clean up anything in the folder you left.
> - **Scroll bars.** A zoomed image that is larger than the frame gets a thin bar at the bottom, the right, or both. Drag the thumb to move the view. The bars are drawn over the frame, so a thumb covers a 10-pixel strip of the image at the edge (D-1426). A click on the empty part of a bar does nothing, and the bars are not keyboard controls (D-1427).
>
> **Disclosed for your go-ahead:**
>
> - **Four existing test expectations change by name (D-1422).** They are source-text scans that require the literal `F2` in a source file, which the One source row forbids: three in `capture-page.test.ts` AC-39.13 and one in `settings-page.test.ts` AC-61.16. Rows 6 and 7 of `task.md` name each test and its new expectation. One E2E comparison (`help-quick-start.test.ts:135`) and the shots script's hash input change their source of the expected text from the raw JSON to the default reading; the expected text itself is the same.
> - **Ten files are outside the grouping's `owns` list (D-1429).** The homes' rows force each one. `HelpCard.tsx` is Session 105's file and `SettingsPage.tsx` is in Session 106's folder; both edits are a few lines and those sessions run later.
> - **No help image is retaken (D-1421).** The quick-start steps hash is computed on the default reading, so it does not change.

## Proposed Changes

### Single-statement contracts

| Mechanism id | Contract |
|---|---|
| `CAPTURE_KEY_TOKEN` | A text that names the capture key holds the token `{captureKey}`, and one formatter, `captureKeyText(template, key)` in `capture-key.ts`, replaces it; a blank key gives the default `F2`. |
| `CAPTURE_KEY_SAVED` | The key the texts, the key cap and the banner show is the saved `capture.hotkey`, exposed as `saved.hotkey` by `useCaptureSettings`; a draft changes none of them. |
| `CAPTURE_KEY_FOLLOW` | The page reads main's hotkey status on mount and when the saved key changes; while the status names another key than the saved one it reads again every 500 ms, at most 10 times, and stops on a match or on unmount. |
| `CAPTURE_KEY_UNCONFIRMED` | When the follow ends with no read that confirms the saved key (`registered`, with `accelerator` equal to it) and the last status is not in use, or a status read is refused, the banner place shows `HOTKEY_UNCONFIRMED_TEMPLATE` with the saved key: `{accelerator} is saved, but av-kit cannot confirm it works. Restart av-kit if {accelerator} does nothing.` It uses the in-use banner's test id and chip; the key cap stays hidden; the notice stays until a status read confirms the saved key or reports it in use. It claims no registration. |
| `CAPTURE_KEY_DEFAULT_READING` | `CAPTURE_HELP_SECTIONS`, `SETTINGS_HELP_SECTIONS` and `QUICK_START` are the texts resolved with `F2`, equal to today's; the per-key forms are `captureHelpSections(key)`, `settingsHelpSections(key)` and `quickStartPage(feature, key)`. |
| `INBOX_SCOPE` | A shot is in scope when `shot.original_path.parent` equals the current resolved inbox folder; the test makes no filesystem call. |
| `INBOX_SCOPE_SCAN` | `scan_inbox` and `list_shots` return only shots in scope, and neither scan loop touches a row out of scope: the first loop checks that a resolved file's parent equals the inbox before it probes or saves that file, and the second loop skips every row out of scope. No probe, no prune, no recovery, no write. |
| `INBOX_SCOPE_BY_ID` | Every public `CaptureService` method that takes a shot id answers a shot out of scope with the same `NotFoundError` as an unknown id, through one private lookup, and writes nothing. |
| `INBOX_SAVE_REFRESH` | A capture settings save that changed `inbox_dir` also invalidates the `['captures']` query; a save that did not change it does not. |
| `INBOX_SELECTION_LEFT` | A selection is bound to the saved `inbox_dir` under which it was made. A selected shot that a catalog answer held and a later answer lacks is cleared with the delete path's resets. A selection that no answer has held yet (a crop or copy result) is kept only while the saved `inbox_dir` is still the one it was made under. A selection made under an earlier saved `inbox_dir` is cleared by the first catalog answer that lacks it, held or not, and a not-found answer to its detail clears it with no error event and no notice. |
| `INBOX_RESULT_BOUND` | A crop, or a flatten that makes a PNG copy, selects its result, anchors the range on it and shows its notice only when the saved `inbox_dir` at its end equals the one at its start. Otherwise it selects nothing, moves no anchor and shows no notice; the crop tool still closes as today, and the new file stays where the service wrote it. |
| `SCROLL_BAR_GEOMETRY` | Pure functions in `capture-scroll-bars.ts` give, per axis, whether the bar shows, the track length, the thumb length and offset, the value 0 to 100, and the pan change for a thumb drag. |
| `SCROLL_BAR_OVERLAY` | The bars are absolutely positioned children of the viewport surface, drawn from the view transform; the frame stays `overflow-hidden` and `capture-fit-map.ts` does not change. |
| `SCROLL_BAR_DRAG` | Only a thumb takes pointer input; its drag pans through the existing clamped pan and never reaches the draw surface, so it makes no mark, history entry or colour sample. |
| `SCROLL_BAR_LOOK` | The bars use theme tokens only (thumb `--color-fg-muted` with a 1 px `--color-bg` edge, transparent track), have no geometry transition, and carry the `scrollbar` role with its values. |

### MEU-165: Capture key in texts

1. **The leaf.** New `ui/src/renderer/src/features/capture/capture-key.ts` (LF, no import): `CAPTURE_KEY_DEFAULT = 'F2'`, the token, and `captureKeyText(template, key)`, which replaces every `{captureKey}` and uses the default for a blank key.
2. **The saved key.** `useCaptureSettings` returns `saved` (its `baseline`). `CapturePage` reads `saved.hotkey` for the texts, the key cap and the banner.
3. **The key cap and the banner.** The cap shows the saved key only when the status says `registered` and its `accelerator` equals the saved key. The banner shows when the status says `inUse`, and names the saved key. The status follow is `CAPTURE_KEY_FOLLOW`; when it ends unconfirmed, or a status read is refused, the banner place shows the notice of `CAPTURE_KEY_UNCONFIRMED` (`HOTKEY_UNCONFIRMED_TEMPLATE` beside `HOTKEY_IN_USE_TEMPLATE`, with the same test id and chip, so `test-ids.ts` does not change).
4. **The texts.** `EMPTY_STATE`, the five lines of `capture-help-content.ts`, the startup body of `settings-help-content.ts` and step 1 of the Capture page in `quick-start.json` hold the token in place of `F2`. Topic ids stay.
5. **The readings.** Per `CAPTURE_KEY_DEFAULT_READING`. `quickStartPage` returns the same object as `QUICK_START[feature]` for a page with no token.
6. **The help card.** `HelpCard` takes an optional `captureKey` prop; with it the card shows `quickStartPage(feature, captureKey)`, without it `QUICK_START[feature]`. `CapturePage` passes `captureHelpSections(saved.hotkey)` and `captureKey`. `SettingsPage` passes `settingsHelpSections(capture.saved.hotkey)`.
7. **The raw readers.** `help-quick-start.test.ts:135` and the `stepsHash` of `help-shots.shots.ts` resolve the token with the default key through `captureKeyText`, so the E2E comparison and the manifest hash keep today's values.
8. **Not picked up:** a key changed outside the page (the MCP settings tool, the Settings page leaf) shows after the next settings read of the page; see §Out of Scope.

### MEU-166: Catalog follows the inbox folder

1. **Scope.** One private predicate per `INBOX_SCOPE`, the form the service already uses at `capture.py:1578` and `:2080`.
2. **Scan and list.** Per `INBOX_SCOPE_SCAN`. The first loop's check sits after `child.resolve()` and before the probe, so a file link in the inbox that resolves into another folder is neither probed nor saved. Rows of other folders keep every field and link. After a change back, the scan treats them as before, including the prune of a row whose file is gone.
3. **By id.** Per `INBOX_SCOPE_BY_ID` (D-1424): one private lookup replaces the six direct `uow.capture_shots.get(shot_id)` calls of the public entry points. The internal re-reads (`:1850`, `:2131`) stay. No route, schema or OpenAPI text changes; `routes/captures.py` is expected to stay as it is. The 404 answer already exists at run time: `errors.py:37` maps `NotFoundError` to 404 with the not-found body. The OpenAPI document lists no 404 for these routes (it lists 200 or 204, and 422) and stays byte-identical; documenting a 404 is out of scope.
4. **Refresh.** Per `INBOX_SAVE_REFRESH`, in `useCaptureSettings.save`.
5. **Selection.** Per `INBOX_SELECTION_LEFT` and `INBOX_RESULT_BOUND` (D-1425), in `CapturePage`. The page keeps the saved `inbox_dir` beside the selection, read from `useCaptureSettings`' `saved`; the crop commit and the flatten convert compare it at their start and their end. After the clear, the existing effect selects the newest shot, or the empty state shows. A by-id "not found" during the switch leaves no error line, whichever answer comes first.

### MEU-167: Viewport scroll bars

1. **Geometry.** New `ui/src/renderer/src/features/capture/capture-scroll-bars.ts` (LF, pure). With frame length `C`, content length `K` (image length times scale), and `SCROLL_BAR_THICKNESS = 10`, `SCROLL_THUMB_MIN = 24`:
   - an axis shows its bar when the view state is `scale` and `K > C`;
   - the track length `T` is `C`, less the thickness when both bars show;
   - the thumb length is `max(SCROLL_THUMB_MIN, T * C / K)`, at most `T`;
   - the thumb offset is `(T - thumb) * (-o) / (K - C)` for a pan offset `o`;
   - a thumb drag of `d` px changes the pan offset by `-d * (K - C) / (T - thumb)`, and by 0 when `T` equals the thumb.
2. **Bars.** Per `SCROLL_BAR_OVERLAY`, in `CaptureViewport.tsx`, with the test ids `capture-scrollbar-x`, `capture-scrollbar-y`, `capture-scrollbar-x-thumb` and `capture-scrollbar-y-thumb`, added to `ui/tests/e2e/test-ids.ts` in a new `// MEU-167 viewport scroll bar IDs.` block at the end.
3. **Drag.** Per `SCROLL_BAR_DRAG`: the thumb captures the pointer and calls the existing `panBy`, so the clamp is the pan's own.
4. **Look and names.** Per `SCROLL_BAR_LOOK`: `role="scrollbar"`, `aria-orientation`, `aria-valuemin` 0, `aria-valuemax` 100, `aria-valuenow`, `aria-controls` naming the image surface, the names "Horizontal scroll" and "Vertical scroll", and no tab stop.

### GUI compliance (create-plan Step 4A)

`gui-refs-not-shipped`: the five reference files that Step 4A names (`docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md`, `.agent/docs/gui-standards-enforcement.md`) are absent, so the step is skipped as the workflow says. The standards of `.agent/docs/emerging-standards.md` still bind:

| Standard | How this plan meets it |
|---|---|
| G26 contextual help | The Capture and Settings help topics keep their ids and count; only the key name in the text follows the setting (AC-165.4, AC-165.5, AC-165.8) |
| G32 tokens only | The bars use `--color-fg-muted` and `--color-bg`; no hex or `rgb(` literal (AC-167.6), seen in both themes (AC-167.8) |
| G33 motion tokens | The bars have no transition on position or size, so no motion token applies (AC-167.6) |
| G36 no silent test guards | No new test skips or returns early; the E2E checks require `skipped=0` (AC-165.10, AC-166.7, AC-167.7, AC-167.8) |
| G37 userEvent | The rendered Vitest tests drive the page with `userEvent`, the thumb drag included (AC-165.6, AC-167.5) |

### Test pins

| Pin | What it checks | After this change |
|---|---|---|
| `ui/tests/unit/capture-page.behavior.test.ts` AC-57.2 (`:1265-1277`), AC-57.2 AC-57.3 banner (`:1279`), AC-57.9 (`:1460`) | Key cap `F2` with one status read; banner `F2 is in use — quit ShareX or pick another key`; rendered empty state | Unchanged and passing: default key, and no follow read when the status matches |
| `ui/tests/unit/capture-action-row.test.ts` (`:685-703`) | The banner text and the status read | Unchanged and passing |
| `ui/tests/unit/help-quick-start.test.tsx` AC-162.6, AC-162.7, AC-162.9 and its `FACTS` map | Help texts, the steps hash against the manifest, STE facts that name `F2` | Unchanged and passing: the exports are the default readings |
| `ui/tests/unit/capture-help-content.test.ts`, `capture-tool-style.test.ts`, `capture-copy-image.behavior.test.ts`, `capture-redact.behavior.test.ts`, `failure-reason-copy.test.ts`, `help-card.test.ts` | Imports of the help constants; `HelpCard` rendered with three props | Unchanged and passing |
| `ui/tests/unit/capture-zoom.test.ts`, `capture-fit-map.test.ts` | Wheel zoom, pan clamp, the view transform | Byte-identical and passing |
| `ui/tests/unit/e2e-pointer.test.ts` AC-7 | The pointer helpers `capture-inbox.test.ts` must use | Unchanged and passing; the new tests use `settledZoom`, `settledBox` and `pointerOn` |
| `ui/tests/unit/gui-actions-audit.test.ts` AC-93.6, AC-96.11; `capture-page.test.ts:476` | The block order of `test-ids.ts` | Unchanged and passing; the new block is added at the end |
| `ui/tests/e2e/capture-inbox.test.ts` (every existing test), `ui/tests/e2e/capture-settings-draft.test.ts` AC-151.14 | Wheel zoom, Space+drag, middle-button drag, the settings draft | Existing lines kept: `row-check.py guards` allows added lines and a re-added `import` line only |
| `tests/unit/test_capture_service.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_crop.py`, `tests/tooling/test_help_guide_ste.py` | The catalog, the routes, the STE gate | Byte-identical and passing |
| `openapi.committed.json` | The API document | Byte-identical; `tools/export_openapi.py --check` passes |
| **Changed by name (D-1422):** `capture-page.test.ts` AC-39.13 (`:112`, `:117`, `:328`); `settings-page.test.ts` AC-61.16 (`:771`) | Source scans for the literal `F2` | The four expectations take the token form; from row 6 on, `row-check.py guards` allows those four lines and no other |

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `GET /captures` reply | `packages/api/src/avkit_api/routes/captures.py` models | No field added, removed or renamed; only which shots are listed changes | Unchanged |
| By-id capture routes (path `id`) | The same routes; `CaptureService` | An id out of scope answers 404 with the existing not-found body, through the existing `NotFoundError` mapping (`errors.py:37`; row 0 checks it). The OpenAPI document lists no 404 for these routes and stays byte-identical | Unchanged |
| `PUT /settings/capture` (`hotkey`, `inbox_dir`) | `SettingsService` validation | Unchanged; the page sends only changed leaves, as today | Unchanged |
| `window.api.getHotkeyStatus()` | `ui/src/main/ipc.ts:160` | Read only: `accelerator`, `registered`, `inUse`; no channel or preload change | Unchanged |
| `HelpCard` props | `HelpCard.tsx` `HelpCardProps` | `captureKey?: string`; rendered as React text, never as HTML | TypeScript refuses unknown props |
| `quick-start.json` | `validateQuickStart` in `quick-start.ts` | A step text may hold `{captureKey}`; every other rule is unchanged | Unknown fields refused as today |
| Key text | `captureKeyText` | Any string from the saved setting; blank gives `F2`; no markup is interpreted | Not applicable |
| Thumb pointer input | `CaptureViewport.tsx` | Drag distance in px; the result is clamped by the existing pan | Not applicable |

### Acceptance Criteria

**Families.** AC-165.x belongs to MEU-165, AC-166.x to MEU-166 and AC-167.x to MEU-167. Test titles start with the id and a space. The pytest names start `test_ac_166_<n>_`. A guard's Vitest title starts `guard AC-<id> `, so it never matches a required id.

**Red notes.** Every required id fails by assertion at Red, as `red-check.py` demands. A Vitest test loads a new module through `import.meta.glob` and asserts that the loader exists first; it reads a new export through a namespace import and asserts its `typeof` first. So a missing module or name is an assertion line, never a load error. `DECLARED_NEW` excuses only a block that no row requires; a pytest Red never fails on a missing name. AC-165.3 and the guards named below pass at Red and are recorded as guards, never as FAIL_TO_PASS.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-165.1 | unit | `capture-key.test.ts`: `captureKeyText('Press {captureKey} or Capture region', 'F9')` gives `Press F9 or Capture region`; every occurrence is replaced; a text with no token comes back unchanged; `CAPTURE_KEY_DEFAULT` is `F2`; a chord such as `Ctrl+Shift+S` is shown as given. | Spec (09 §Capture key in texts, One source); `CAPTURE_KEY_TOKEN` | A blank or all-space key gives the default, never `Press  or` |
| AC-165.2 | unit | A scan of every `.ts`, `.tsx` and `.json` file under `ui/src/renderer/src`: the files that hold the word `F2` are exactly `features/capture/capture-key.ts`, `features/capture/useCaptureSettings.ts` and `registry/shortcuts.ts`; the eight texts of step 4 hold `{captureKey}`. | Spec (One source: "no text restates the literal") | At Red six more files hold the literal |
| AC-165.3 | unit (guard) | `CAPTURE_HELP_SECTIONS`, `SETTINGS_HELP_SECTIONS` and `QUICK_START.capture` hold no `{captureKey}`, and the eight texts equal today's strings, pinned in the test from `HEAD`; topic ids, order and count are unchanged. | Spec (Default: "With the default key every text reads as it does today."); `CAPTURE_KEY_DEFAULT_READING` | An export that holds the token fails |
| AC-165.4 | unit | `captureHelpSections('F9')` gives the five lines with `F9`; `settingsHelpSections('F9')` ends its startup body `so F9 still works.`; `quickStartPage('capture', 'F9')` gives step 1 `Push F9 or click Capture region. Then drag a box on the screen.` with the shots unchanged; for a feature with no token `quickStartPage` returns the same object as `QUICK_START[feature]`. | Spec (Set key); `CAPTURE_KEY_DEFAULT_READING` | No result holds `F2` or `{captureKey}` |
| AC-165.5 | unit | `capture-key.behavior.test.ts` renders `CapturePage` with the saved key `F9` and a status of `F9`, registered: the empty state reads `Press F9 or Capture region`; the key cap reads `F9`; the open help card shows step 1 with `F9` and the topics `When F9 is in use` and `Close to tray keeps F9`. | Spec (Set key) | No rendered text on the page holds `F2` |
| AC-165.6 | unit | The same page starts on `F2`. A draft of `F9` changes no text and not the key cap. After Save the texts read `F9` with no remount. While the status still names `F2` the key cap is hidden and the page reads the status every 500 ms; on the first read that names `F9` the cap shows `F9` and the reads stop. With a status that never matches, the page makes exactly 10 follow reads and then shows the unconfirmed notice `F9 is saved, but av-kit cannot confirm it works. Restart av-kit if F9 does nothing.` with no key cap. A refused status read after the save shows the same notice at once. | Spec (Change: "with no restart"); `CAPTURE_KEY_SAVED`; `CAPTURE_KEY_FOLLOW` (D-1420); `CAPTURE_KEY_UNCONFIRMED` (round-1 review F3) | A draft alone changes nothing; an unmount stops the reads; no notice shows while the follow still runs |
| AC-165.7 | unit | With the saved key `F9` and a status of `F9`, in use: the banner reads `F9 is in use — quit ShareX or pick another key` and no key cap shows. A draft of `F10` leaves the banner on `F9`. | Local Canon (the banner template, `CapturePage.tsx:106`); D-1420 | At Red the banner follows the draft |
| AC-165.8 | unit | `SettingsPage` rendered with the saved capture key `F9`: the startup topic of its help card ends `so F9 still works.` | Spec (Set key: the Settings startup help) | With the default key the same topic ends `so F2 still works.` |
| AC-165.9 | tooling | `uv run python tools/help_guide_ste.py` ends `help-guide-ste: 0 problems` with exit 0 on the token texts; `validateQuickStart` returns no problem for `quickStartPage('capture', key)` with `F9` and with `Ctrl+Shift+F12`; `tests/tooling/test_help_guide_ste.py` passes unchanged. | Spec (Help rules: the STE gate) | A step text that breaks an STE rule still fails the linter (its own selftest) |
| AC-165.10 | integration | Electron on mini-air, real backend, in `capture-settings-draft.test.ts`, title `AC-165.10 a saved capture key shows in the Capture texts with no restart`. The inbox is set by the API to an empty temp folder before Capture opens, so the catalog never lists or stores a file of the real Pictures folder. Main's start-up watcher may list the default folder's file names until its first settings read; the test reads nothing from it. The empty state reads `Press F2 or Capture region`; the key is changed to `F9` in the page and saved; the empty state reads `Press F9 or Capture region`, and the open help card shows `F9` in step 1 and in the topic `When F9 is in use`; the key cap reads `F9` if main reports the key registered, else the banner names `F9`, and the test logs which. No reload and no relaunch. | Spec (Tests row; Change); grouping acceptance direction | Before Save the texts still read `F2` |
| AC-166.1 | unit | `tests/unit/test_capture_inbox_scope.py`: folders A (two PNG files) and B (one). With inbox A, `scan_inbox()` and `list_shots()` return exactly A's two shots; with inbox B, exactly B's one; back on A, A's two with the same ids and the saved mark of one of them still linked. A file in `A/sub` is never listed. | Spec (09 §Catalog follows the inbox folder: Scope, Rows kept); `INBOX_SCOPE`, `INBOX_SCOPE_SCAN` | At Red, B's list holds A's shots |
| AC-166.2 | unit | With inbox B, an original file of A is deleted on disk and the scan runs: A's row still exists with every field equal, and no file in A is created or changed. Back on A, the scan prunes that row as before. With inbox A holding a file link to a cataloged B image (or, where the host refuses to make a link, a fake resolver that maps an A child to B's file), the scan neither probes nor saves B's row in either loop: the probe is never called with B's path and every field of B's row is unchanged. | Spec (Rows kept); D-1423; round-1 review F4 | At Red the scan prunes A's row while the inbox is B, and the first loop probes the linked B file |
| AC-166.3 | unit | With inbox B, every public `CaptureService` method that takes a shot id raises the same `NotFoundError` for an A shot as for an unknown id, and writes nothing. The test's method list must equal the set found by inspection of the class. Guard: on inbox A the same calls on the same shot still work (`get_shot` checked). | Spec (By id: chosen at plan time); D-1424; `INBOX_SCOPE_BY_ID` | A new id-taking method with no test row fails the census |
| AC-166.4 | integration | `tests/e2e/test_api_capture_inbox_scope.py`, real stack: after `PUT` inbox A then B, `GET /captures` lists only B's shot, and the key set of the reply and of each item equals the set before the change; `GET /captures/{A id}` and one write route answer 404 with the body shape of an unknown id; A's file is still on disk; after `PUT` back to A the same id answers 200. | Spec (Scope; Tests); the grouping gate ("`GET /captures` keeps its reply shape") | The write route changes no file of A |
| AC-166.5 | unit | `capture-inbox-scope.behavior.test.ts`: a save that changes `inbox_dir` is followed at once by one more `GET /captures`, not at the 5 s poll. | Spec (Refresh); `INBOX_SAVE_REFRESH` | A save that changes only the key makes no extra `GET /captures` |
| AC-166.6 | unit | `CapturePage` with shots a1 and a2 and a2 open: after the list answers with b1 only, b1 is the current filmstrip item and the viewport shows it; with an empty answer the empty state shows; no detail request for a2 goes out after that answer and no `av-kit:capture:error` event fires. | Spec (Refresh); D-1425; `INBOX_SELECTION_LEFT` | Within one saved inbox, a selection that no list answer has held yet (a crop result) is kept |
| AC-166.7 | integration | Electron on mini-air, real backend, in `capture-settings-draft.test.ts`, title `AC-166.7 a saved inbox change lists only the new folder`. Temp folders A (two copies of the fixture PNG) and B (one). Inbox A is set by the API before Capture opens: the filmstrip has two items with A's names. The inbox is changed to B in the page and saved: the filmstrip has one item with B's name, that item is current, and no error line shows. After a change back to A the filmstrip has two items. | Spec (Tests row); grouping acceptance direction ("change the inbox and see the old shots leave") | A's two files are still on disk after the change |
| AC-166.8 | unit | `capture-inbox-scope.behavior.test.ts`, with held responses. (a) With a1 open in inbox A, a crop starts and its response is held; inbox B is saved and the list answers b1; then the crop response is released. b1 stays selected, no detail request for the crop's id goes out, no `av-kit:capture:error` event fires and no crop notice shows. (b) With a1 open, inbox B is saved and the `GET /captures` answer is held; the detail read of a1 answers 404 first; then the list answers b1. No `av-kit:capture:error` event fires, no error line shows, and b1 becomes current. | Round-1 review F2; D-1425; `INBOX_SELECTION_LEFT`; `INBOX_RESULT_BOUND` | With no inbox change, a released crop response selects its result and shows its notice, as today (a guard) |
| AC-167.1 | unit | `capture-scroll-bars.test.ts`: for `C` 400, `K` 1600, `T` 400 the thumb is 100 long; at pan offset 0 it sits at 0, at `C - K` at `T - thumb`, at half-way in the middle; the value runs 0 to 100. For `K` 40000 the thumb is `SCROLL_THUMB_MIN`. The thumb is never longer than the track. | Spec (09 §Viewport scroll bars: Bars); `SCROLL_BAR_GEOMETRY`; Research-backed (thumb length as the visible share of the content) | A thumb shorter than the minimum is refused by the minimum |
| AC-167.2 | unit | In the `fit` state neither bar shows. In `scale` with `K` at most `C` on both axes neither shows. With one axis larger only that bar shows, on the full frame length. With both larger both show and each track is shorter by `SCROLL_BAR_THICKNESS`. | Spec (Bars: "on each axis where the image is larger than the frame") | Equal lengths (`K` equal to `C`) show no bar |
| AC-167.3 | unit | A thumb drag of `d` px gives a pan change of `-d * (K - C) / (T - thumb)`; a drag of the whole free track from the start reaches the end exactly; after the pan clamp the offset is always within `C - K` to 0, over a table of cases. | Spec (Move); `SCROLL_BAR_GEOMETRY` | With the thumb as long as the track the change is 0, not a division by zero |
| AC-167.4 | unit | `capture-scroll-bars.behavior.test.ts` renders the viewport zoomed past the frame: both bars and thumbs exist under their test ids, each with `role="scrollbar"`, its `aria-orientation`, `aria-valuemin` 0, `aria-valuemax` 100, an integer `aria-valuenow` equal to the geometry, `aria-controls` naming the image surface, and its name; neither is a tab stop. | Research-backed (WAI-ARIA `scrollbar` role: `aria-valuenow` and `aria-controls`); `SCROLL_BAR_LOOK` | At Fit no bar is in the document |
| AC-167.5 | unit | A `userEvent` drag of the vertical thumb by 30 px moves the view by the geometry's amount on that axis and leaves the other axis as it was. | Spec (Move); `SCROLL_BAR_DRAG` | The drag adds no mark, no history entry and no colour sample, and the draw surface gets no pointer event |
| AC-167.6 | unit | A source scan: the bars' markup and `capture-scroll-bars.ts` hold no hex or `rgb(` colour and no transition class; the track is `pointer-events-none` and the thumb takes pointer events; the frame keeps `overflow-hidden`; `capture-fit-map.ts` is byte-identical to the baseline. | Local Canon (G32, G33); Spec (Look; Replaces) | A raw colour or a transition on a bar fails |
| AC-167.7 | integration | Electron on mini-air, in `capture-inbox.test.ts`, title `AC-167.7 scroll bars show the view and a thumb drag moves it`. On a zoomed shot both bars show; each thumb's length is the frame's share of the image, within 1 px; a drag of the vertical thumb by 40 px moves the image by the geometry's amount within 1 px and leaves the horizontal offset as it was; a drag far past the end stops at the limit with `aria-valuenow` 100. | Spec (Tests row); grouping acceptance direction ("zoom and drag a thumb") | After Fit both bars are gone |
| AC-167.8 | integration | Electron on mini-air, in `capture-inbox.test.ts`, title `AC-167.8 the scroll bar thumb is seen in both themes`. In the dark and in the light theme the thumb is visible, and the contrast of its fill against its edge colour, both read as sRGB bytes through a 1 by 1 canvas, is at least 3. | Local Canon (G32); Research-backed (WCAG 2.1 SC 1.4.11, 3:1 for a control's visible parts) | A fill equal to its edge gives contrast 1 and fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which texts follow the key | Spec | 09 §Capture key in texts, Set key row, and D-1400: the empty state, the Capture help, the Settings startup help, the Capture quick start |
| What "the value the key cap shows" means | Local Canon | The cap shows main's registered key, which lags a save and is absent when the key is in use. The plan reads the row as one shared value, the saved `capture.hotkey` (D-1420) |
| How the texts take the key | Local Canon | A token and one formatter; default-reading exports (D-1421) |
| Help images | Spec | Help rules row: retaken only if a step's text or target changes. The default text and the targets do not change, so no retake (D-1421) |
| Existing source scans for `F2` | Spec | The One source row forbids the literal, so four scans take the token form, named in rows 6 and 7 (D-1422) |
| Which shots the catalog lists | Spec | Scope row: `original_path` directly inside the current resolved `capture.inbox_dir`, non-recursive |
| What happens to rows of other folders | Spec | Rows kept row; the scan leaves them alone while they are out of scope (D-1423) |
| A shot outside the inbox, asked for by id | Human-approved to choose at plan time | By id row: "chosen at plan time". D-1424: not found |
| The selected shot after it leaves the list | Local Canon | The Refresh row gives the refresh; the clear follows the delete path's resets (D-1425) |
| How the bars are built | Human-approved to choose at plan time | Build row: "chosen at plan time". D-1426: drawn over the frame |
| What a bar does | Spec and Research-backed | Bars and Move rows; thumb drag only, with the `scrollbar` role (D-1427) |
| Where the Electron proof runs | Human-approved | D-1411: mini-air, through `tools/e2e_remote.py` |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-key.ts` | new, LF | The default, the token, `captureKeyText` |
| `ui/src/renderer/src/features/capture/useCaptureSettings.ts` | edit, CRLF | Returns `saved`; `save` invalidates the catalog when `inbox_dir` changed |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | edit, CRLF | The token in `EMPTY_STATE`; saved key for texts, cap and banner; the status follow; help card props; the selection clear |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | edit, CRLF | Five lines take the token; `captureHelpSections(key)`; the constant is the default reading |
| `ui/src/renderer/src/features/settings/settings-help-content.ts` | edit, CRLF | The startup body takes the token; `settingsHelpSections(key)`; the constant is the default reading |
| `ui/src/renderer/src/components/help/quick-start.json` | edit, LF | Step 1 of the Capture page takes the token |
| `ui/src/renderer/src/components/help/quick-start.ts` | edit, LF | `QUICK_START` is the default reading; `quickStartPage(feature, key)` |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | edit, LF | The optional `captureKey` prop |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | edit, CRLF | Passes `settingsHelpSections(capture.saved.hotkey)` |
| `packages/core/src/avkit_core/services/capture.py` | edit, CRLF | `INBOX_SCOPE`, `INBOX_SCOPE_SCAN`, `INBOX_SCOPE_BY_ID` |
| `ui/src/renderer/src/features/capture/capture-scroll-bars.ts` | new, LF | The geometry |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | edit, CRLF | The bars and the thumb drag |
| `ui/tests/e2e/test-ids.ts` | edit, CRLF | The four ids in a new MEU-167 block at the end |
| `ui/tests/unit/capture-key.test.ts`, `capture-key.behavior.test.ts` | new, LF | AC-165.1 to AC-165.9 (Vitest part) |
| `ui/tests/unit/capture-inbox-scope.behavior.test.ts` | new, LF | AC-166.5, AC-166.6, AC-166.8 |
| `ui/tests/unit/capture-scroll-bars.test.ts`, `capture-scroll-bars.behavior.test.ts` | new, LF | AC-167.1 to AC-167.6 |
| `ui/tests/unit/capture-page.test.ts` | edit, CRLF | AC-39.13: three expectations take the token form (D-1422) |
| `ui/tests/unit/settings-page.test.ts` | edit, CRLF | AC-61.16: one expectation takes the token form (D-1422) |
| `tests/unit/test_capture_inbox_scope.py` | new, LF | AC-166.1 to AC-166.3 |
| `tests/e2e/test_api_capture_inbox_scope.py` | new, LF | AC-166.4 |
| `ui/tests/e2e/capture-settings-draft.test.ts` | edit, LF | AC-165.10 and AC-166.7, added; one local helper for a request with a body |
| `ui/tests/e2e/capture-inbox.test.ts` | edit, LF | AC-167.7 and AC-167.8, added |
| `ui/tests/e2e/help-quick-start.test.ts` | edit, LF | The expected step texts are the default reading (`:135`) |
| `ui/tests/help-shots/help-shots.shots.ts` | edit, LF | `stepsHash` hashes the default reading |
| `docs/build-plan/09-screenshot-capture.md` | edit, CRLF | Row 11: the Pan gestures row, the empty-state line, the catalog scope notes, three Delivered notes (D-1432) |
| `.agent/context/known-issues.yaml`, `known-issues.md` | edit, CRLF | Row 11: three issues resolved, through `issue-resolve.py` and the render |
| `.agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md` | edit, LF | Row 11: the §6 row of Session 103 is set to `executed (Session 103)` |
| `.agent/context/meu-status.yaml`, `meu-registry.md`, `docs/BUILD_PLAN.md` | edit, LF | Rows 11 and H2-2, through `tools/meu_status.py` only |

`packages/api/src/avkit_api/routes/captures.py` is in the `owns` list and is expected to stay unchanged.

### Project files

- **Plan-local scripts (row 0), copied from `docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/` with this plan's `PLAN`, receipts folder, artifacts and `DECLARED_NEW`:** `baseline.ps1`, `red-check.py`, `identity.py`, `eol-check.py`, `row-check.py`, `session-gate.ps1`, `canon-edit.py`, `crlf.py`, `issue-resolve.py`. `snapshot-commit.py` is copied from `docs/execution/plans/2026-11-20-e2e-devpc-clipboard/` unchanged except its plan constants.
- **Row 0 data:** `baseline.sha`, `baseline-dirty.txt`, `baseline-dirty-hashes.json`, `baseline-scope.json`, `baseline-eol.json`, `baseline-pins.json`, `baseline-citations.txt`, `baseline-copies/`, `cki-by-id-methods.txt`, `cki-base-ui.txt`, `cki-base-py.txt`, `cki-check-0.json`.
- **Read, never changed:** `capture-fit-map.ts`, `capture-zoom.ts`, `useCaptureCatalog.ts`, `routes/captures.py`, `openapi.committed.json`, `ui/src/main/` (all of it), `mcp-server/` (all of it), `tools/e2e_remote.py`, `tools/e2e_host/`, `tools/help_guide_ste.py`, every §Test pins file not named as changed, the fixture `ui/tests/e2e/fixtures/capture-region-original.png`.
- **State:** `cki-red-hashes.json` (the test files of each Red row), `cki-e2e-base.json` (the base test count and the Red run id), `cki-snapshot-1.json`, `cki-snapshot-10.json`, `cki-run-10-dir.txt`.
- **`DECLARED_NEW`:** `capture-key`, `captureKeyText`, `CAPTURE_KEY_DEFAULT`, `HOTKEY_UNCONFIRMED_TEMPLATE`, `captureHelpSections`, `settingsHelpSections`, `quickStartPage`, `saved`, `capture-scroll-bars`, `scrollBars`, `thumbDragToPan`, `SCROLL_BAR_THICKNESS`, `SCROLL_THUMB_MIN`, `capture-scrollbar-x`, `capture-scrollbar-y`, `capture-scrollbar-x-thumb`, `capture-scrollbar-y-thumb`, and the new test files `capture-key.test`, `capture-key.behavior.test`, `capture-inbox-scope.behavior.test`, `capture-scroll-bars.test`, `capture-scroll-bars.behavior.test`, `test_capture_inbox_scope`, `test_api_capture_inbox_scope`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Picking up a key changed outside the Capture page (the MCP settings tool, another window) before the page reads its settings again | Behaviour | None; register an issue if Mat reports it | The Change row covers "After the key is changed and saved"; the page's own save is the path the row names |
| A prompt to save unsaved marks before the inbox change clears the selection | Behaviour | None | D-1425; the delete path has no such prompt either |
| Deleting or moving the rows or files of a folder the user left | Data | None | Rows kept row; D-1401 |
| A by-id answer other than "not found" for a shot outside the inbox | API | None | D-1424 |
| Keyboard control of the bars, a click on the track to page, and wheel scrolling | Behaviour | None | D-1427; the Bars and Move rows ask for position and a thumb drag, and every wheel event zooms (the grouping gate keeps the wheel tests unchanged) |
| A native scroll container | Build | None | D-1426 |
| README text and the default key | Docs | None | D-1400: "README text and code defaults keep `F2`"; the Default row |
| Retaking help images | Assets | Session 105 retakes by script for its own change | Help rules row; D-1421 |
| IPC, preload and MCP tool changes; the `GET /captures` reply shape | Surface | None | The grouping gate |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | Watch item | None | D-1197: a hang reopens it as TECH-DEBT P3; this session fixes nothing there (S7) |

## BUILD_PLAN.md Audit

MEU-165 (`gui-capture-key-text`, matrix 9.48), MEU-166 (`svc-capture-inbox-scope`, 9.49) and MEU-167 (`gui-capture-zoom-scrollbars`, 9.50) were registered as `pending` at triage. Row 11 sets each to `ready_for_review` with this plan's `execution_plan`, and H2-2 sets each to `approved`, both through `tools/meu_status.py update`. `meu-registry.md` and `docs/BUILD_PLAN.md` are regenerated by `tools/meu_status.py render`, never by hand:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars/cki-render-check.txt; exit $code
```

No other line of `docs/BUILD_PLAN.md` needs a hand edit. The three homes in 09 get their Delivered notes in row 11.

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. Use `rtk proxy` for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` has the shape of `2026-11-22-tray-show-and-baseline-fixes/baseline.ps1`:

1. **Tree.** It prints `HEAD`, `git status --porcelain --untracked-files=all` and `git worktree list`, and records `baseline.sha`, `baseline-dirty.txt` and `baseline-dirty-hashes.json`. It creates `C:/Temp/av-kit/s103-tmp`.
2. **Scope binding.** It records `baseline-scope.json`: the SHA-256 of each §Files Modified path and each "Read, never changed" path, or `absent`. Every new path must be `absent`. `current-focus.md`, `metrics.md`, `known-issues.yaml` and `.md`, `meu-status.yaml` and its two rendered files are recorded as `shared` with their hash, because Session 104 and the other sessions write them; the row that writes one re-reads it just before the edit. It also records `baseline-eol.json` and byte copies of the scope files under `baseline-copies/`.
3. **Pins.** `baseline-pins.json` holds the SHA-256 of each §Test pins file.
4. **Citations.** It finds by text, once each, and records the current line of: `const EMPTY_STATE = 'Press F2 or Capture region'`, `const HOTKEY_IN_USE_TEMPLATE =` and `void window.api.getHotkeyStatus().then((status) => {` (`CapturePage.tsx`); `title: 'When F2 is in use',` and `title: 'Close to tray keeps F2',` (`capture-help-content.ts`); `so F2 still works.` (`settings-help-content.ts`); `"text": "Push F2 or click Capture region. Then drag a box on the screen.",` (`quick-start.json`); `const page = QUICK_START[feature]` (`HelpCard.tsx`); `export const QUERY_KEY = ['captures'] as const` (`useCaptureCatalog.ts`); `def scan_inbox`, `def list_shots`, `def get_shot` and `def _require_inbox_file` (`capture.py`); `expect(page).toMatch(/Press F2 or Capture region/)`, `'When F2 is in use',` and `'Close to tray keeps F2',` (`capture-page.test.ts`); `expect(help).toContain('F2')` (`settings-page.test.ts`); the 09 Pan gestures row and the three home headings. A missing or doubled anchor is S2; a moved line is recorded.
5. **Free ids.** Every `DECLARED_NEW` name and `AC-165.`, `AC-166.`, `AC-167.` occur nowhere in the tree outside this plan folder. D-1420 to D-1459 occur only in this plan folder and the grouping file; a match that only ends another file's stated range is printed as a range end.
6. **By-id census and the 404 fact.** `cki-by-id-methods.txt` lists, by inspection, every public `CaptureService` method with a `shot_id` parameter. The row also checks the run-time 404: `packages/api/src/avkit_api/errors.py` maps `NotFoundError` to 404 with the not-found body (found by text, its line recorded); a mapping that is missing or differs is S8. The OpenAPI document is not checked for a 404: it lists none for these routes and stays byte-identical (the gate's `openapi` step).
7. **Base receipts.** The full Vitest suite (`cki-base-ui.txt`, pwsh in `ui/`) and the full pytest suite (`cki-base-py.txt`, undated TEMP). Their failures are recorded, not fatal.
8. **The host.** `tools/e2e_remote.py check --out cki-check-0.json`: a wait-band exit is recorded and is not a stop here; a tool stop is S11.
9. **Plan-local scripts.** It copies the scripts of §Project files. `red-check.py`'s fixtures use this plan's families (it must refuse `AC-165.1` matching `AC-165.10`). `row-check.py` has these subcommands:
   - `red-record --row N FILE…` records the hashes of a Red row's test files.
   - `guards --row N` checks the tree as it must be after row N: the Red files recorded so far are unchanged; the §Test pins files are unchanged; `capture-page.test.ts` and `settings-page.test.ts` equal the baseline before row 6 and differ from it in exactly the four named lines from row 6 on; `help-quick-start.test.ts` and `help-shots.shots.ts` equal the baseline before row 7 and differ only in the named statement from row 7 on; `capture-inbox.test.ts`, `capture-settings-draft.test.ts` and `test-ids.ts` differ from the baseline by added lines only (a re-added `import` line with more names is allowed); and `eol-check.py` passes.
   - `e2e-titles LIST` checks that a Playwright `--list` receipt holds the four new titles once each.
   - `snapshot-paths --out FILE` writes the §Files Modified paths under `ui/` and `packages/` that differ from `HEAD`.
   - `remote-red`, `remote-ok` and `remote-fresh` check a mini-air run as §3 and §Session gate say.
   - `canon` checks row 11's 09 and grouping edits; `decision-sources` probes the H2-2 decision sources; `--selftest` runs the fixtures of each check.
10. **Secrets and the fleet hub.** The scope walk drops `.mcp.json`, `mcp-token.txt`, `.claude.json`, `.env`, `.claude/settings.local.json` and `.agent/fleet/hub` before any stat or read.

If any step except the base receipts and the host check fails, the row fails and nothing else runs.

### 2. Red, then Green

- **Every Red comes before its change.** Rows 1, 2, 4, 6 and 8 change no product file. Row 6 also writes the three AC-39.13 expectations and the AC-61.16 expectation in their new form, so they fail at Red and pass at Green.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py --require` names the failing ids of each row, and each must fail by assertion (§Acceptance Criteria, Red notes). The pytest guards are named with `--allow-pass`.
- **Expectations stay the same in Green** (S3). Each Red row records the hashes of the test files it writes, and each Green row runs `row-check.py guards --row N`.
- **Two more test files change in row 7**, and only as §Files Modified says: `help-quick-start.test.ts` and `help-shots.shots.ts` take the default reading. `capture-inbox.test.ts` and `capture-settings-draft.test.ts` do not change after row 1.
- **Line endings** are checked by `eol-check.py` after each Green.

### 3. Electron on mini-air (rows 1 and 10)

- **Row 1, Red.** The snapshot holds `HEAD` plus the two E2E files only. `row-check.py remote-red` passes when the tool's last line says `new-failures exit=40`; `summary.json` has `new` equal to exactly AC-165.10, AC-166.7, AC-167.7 and AC-167.8, an empty `overlap`, `skipped` 0, `flaky` 0 and the snapshot's commit; and each of the four fails in `host/report.json` on an `expect` with no `Test timeout` and no launch error. It writes the base count, `tests` less 4, to `cki-e2e-base.json`. The count is taken from this run, not pinned.
- **Row 10, proof.** The snapshot holds `HEAD` plus every changed path under `ui/` and `packages/`. `row-check.py remote-ok` passes when the last line says `ok exit=0`; `summary.json` has `result` `ok`, `unexpected` 0, `flaky` 0, `skipped` 0, `new` empty, `overlap` empty, `tests` equal to the base count plus 4, and the snapshot's commit; the four titles are `expected` in `host/report.json`; and `host/run.log` and `host/run.err` hold no `unhandled rejection:` line.
- **What the snapshot does not hold.** Another session's work that is not committed is not in the snapshot, so the mini-air build is `HEAD` plus this session's paths. Sessions 103 and 104 share no product file. A scope path that carries another hand's change is S4.
- **Rows 2 to 9 may run while row 1's run is in the background.** The snapshot is fixed when it is made. Row 10 waits for row 1.

### Session gate (H1-2)

`session-gate.ps1` has the shape of `2026-11-22-tray-show-and-baseline-fixes/session-gate.ps1`: one receipt per step, `cki-D6-<step>`, fail-fast, later steps printed `not_run`, last line `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint` (pwsh in `ui/`); `py-types` (`uv run pyright packages/`); `py-lint` (`uv run ruff check packages/ tests/`); `py-format` (`ruff format --check` on the two new pytest files and this plan folder's Python); `task-contract`; `scope-paths`; `line-endings`; `home-path` (`tools/check_home_path.py`); `guards --row 11`; `canon`; `ste-lint` (`tools/help_guide_ste.py`); `openapi` (`tools/export_openapi.py --check openapi.committed.json`); the selftests |
| Targeted | `py-inbox` (the two new pytest files, `tests/unit/test_capture_service.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_crop.py`, `tests/tooling/test_help_guide_ste.py`); `ui-capture` (the five new Vitest files and the §Test pins unit files) |
| Fresh full | `ui-tests` (full Vitest); `py-tests` (`uv run pytest tests/ -x --tb=short -q`, undated TEMP, no `--deselect`); `ui-build`; `e2e-remote` (see below); `state-render` (`meu_status.py render --check`); `issues-render` (`issue_triage.py render --check`) |
| Skipped, with reason | Electron on the dev PC (D-1411: E2E runs on mini-air). `mcp-server` tests: no MCP file changed |

**The `e2e-remote` step (D-1430).** `row-check.py remote-fresh` compares the working tree under `ui/` and `packages/` with row 10's snapshot commit, untracked files included. If they are equal, the step reuses row 10's run and prints its last line and folder. If they differ, the step makes a fresh snapshot and runs again, with the same check as row 10. The stops are the same as row 10's.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | A `graphify-out` graph appears | Re-decide the context tool |
| S2 | Row 0 finds a citation anchor missing or doubled, or a free id taken | Stop and bring the receipt to Mat. A moved line is corrected, not a stop |
| S3 | A Red receipt fails `red-check.py` or `remote-red`, or a Green row needs a changed expectation | Fix the test setup; never edit an expectation in Green |
| S4 | A path outside this plan's scope and `baseline-dirty.txt` changes, or a scope path changes by another hand | Stop and re-baseline with Mat. Never commit, stash or revert another session's work |
| S5 | An existing test other than the four named in D-1422 fails after a Green | Rerun it alone once. If it fails again, stop: an M-7 question, not a fix |
| S6 | Codex is unavailable or the ledger refuses | Mat |
| S7 | In row 10 or the gate: an Electron test fails, a receipt holds `unhandled rejection:`, or a launch or close hangs | Stop and bring the receipts to Mat. Never raise a timeout or add a retry (D-1126). A hang reopens `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` as TECH-DEBT P3, classified by the last phase in that run's `phases.jsonl` (D-1197) |
| S8 | A contract cannot be met as written: the API does not map `NotFoundError` to 404, `validateQuickStart` refuses a key chord, lint refuses the leaf's import path, or a rendered pin needs the draft key | Stop and route back to the plan |
| S10 | `e2e_remote.py` exits 20 to 24, or `overlap` is not empty | Wait and rerun the same command; never a pass. After three waits of the same kind, tell Mat |
| S11 | `e2e_remote.py` exits 10, 11, 25 to 31, 33 or 34 | A tool stop: `release` once with this session's own run id if a lock is kept, then stop and bring the receipt folder to Mat |

## Decision Log

> [!NOTE]
> D-1420 to D-1432 are autonomous, made under Mat's hand-over (USER_EXPLICIT 2026-11-18: 'make the decisions always the recommenations'). Each passed the §4a list and the §4 test. D-1400 to D-1402 (triage) and D-1410 to D-1413 (grouping) are read from `known-issues.yaml` and the grouping file. The M items:
>
> - **M-4 clear.** No route, request body, reply body, OpenAPI document, IPC channel, preload surface or MCP tool changes. D-1424 changes which ids a by-id route treats as unknown. The 404 answer already exists at run time through the `NotFoundError` mapping (`errors.py:37`), which row 0 checks; the OpenAPI document lists no 404 for these routes, before and after, and stays byte-identical.
> - **M-2 clear.** No user data is read, deleted or moved. Rows of other folders are kept. Every Electron launch uses scratch app data and temp inbox folders, and the catalog never stores a file of the real Pictures folder. Main's start-up watcher may list the default folder's file names until its first settings read; the tests read nothing from it.
> - **M-5.** D-1424, D-1425 and D-1426 choose user-visible behaviour that the homes leave to the plan; each has a Decision Brief below.
> - **M-7 read as clear, and disclosed.** D-1422 changes four existing expectations. M-7 covers a change "that no approved plan row specifically calls for"; rows 6 and 7 of `task.md` name each test and its new expectation, so the change waits for the plan's approval and Mat's go-ahead. It is listed in §User Review Required.
> - **M-8.** D-1429 names files outside the grouping's `owns` list; D-1432 words the 09 updates.
>
> Execution decisions take D-1433 to D-1459. Expert pass: inline, not independent.

```yaml
decision_log:
  - id: D-1420
    stage: planning
    question: "Which value is the capture key that the texts, the key cap and the banner show?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the saved capture.hotkey (CAPTURE_KEY_SAVED). The key cap shows it only when main reports it registered; the banner names it when main reports it in use; the page follows main's status for at most 10 reads of 500 ms after a save (CAPTURE_KEY_FOLLOW); a follow that ends unconfirmed, or a refused status read, shows a saved-but-not-confirmed notice in the banner place (CAPTURE_KEY_UNCONFIRMED)."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Capture key in texts — One source and Change rows (D-1400)"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:855-860 — the key cap reads main's status in an effect that depends on the draft key"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:2222 — the banner names the draft key"
      - "ui/src/main/ipc.ts:160 — getHotkeyStatus gives accelerator, registered and inUse"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the saved setting for everything, with a bounded follow of main's status for the key cap; (B) main's registered key for everything, as the One source row's words say; (C) do nothing beyond replacing the literals with the draft key the page already holds. B fails the Change row: main applies a saved key on a 1 s poll and reports no usable key when the key is in use, so the texts would lag a save or fall back to F2. C makes every text change while the user types a key that is not saved. A gives one value that is right the moment the save returns. Weakness of A: for up to 5 s after a save the key cap is hidden while main applies the key. A key that main never confirms gets the unconfirmed notice, not silence (round-1 review F3). Two-way: one hook field and one effect."
  - id: D-1421
    stage: planning
    question: "How do the texts take the key, and do the help images need a retake?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the texts hold the token captureKey in braces and one formatter replaces it (CAPTURE_KEY_TOKEN); the exported constants are the readings with F2 and per-key accessors give the rest (CAPTURE_KEY_DEFAULT_READING); the E2E comparison and the shots hash use the default reading, so no image is retaken."
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Capture key in texts — One source, Default and Help rules rows"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:106 — the banner already uses a token, accelerator in braces"
      - "ui/tests/help-shots/help-shots.shots.ts:62-65 — the manifest hash is over the steps and the shots"
      - "C:/Temp/av-kit/2026-11-26-plans/s103/ste-probe.txt — the STE linter finds no problem in the token texts"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) token in the source, default-reading exports; (B) keep F2 in the sources and replace it when the text is drawn; (C) hash the raw token text and retake the Capture help images; (D) do nothing. B keeps the literal in six files, which the One source row forbids, and would also rewrite an F2 that is not the key. C spends a retake on images whose text at the default key and whose targets do not change, against the Help rules row. D leaves the issue open. With A about twenty test files that import the constants keep passing unchanged. Weakness of A: a reader of the raw JSON must resolve the token; two such readers exist and both are changed here. Two-way."
  - id: D-1422
    stage: planning
    question: "Which existing test expectations change, and how?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: four source-scan expectations take the token form, named in task rows 6 and 7: capture-page.test.ts AC-39.13 (the empty-state regex and the two topic titles) and settings-page.test.ts AC-61.16 (the F2 scan becomes a scan for the captureKey token). help-quick-start.test.ts:135 and the stepsHash of help-shots.shots.ts keep their expected values and take them from the default reading. No other expectation changes."
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Capture key in texts — One source: 'no text restates the literal'"
      - "ui/tests/unit/capture-page.test.ts:112, :117, :328 and ui/tests/unit/settings-page.test.ts:771 — the four scans"
      - "D-1367 (Session 102) — one named assertion change, disclosed in User Review Required"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) change the four scans by name; (B) keep the scans passing by leaving the literal in a comment in each source file; (C) do nothing, which leaves the One source row unmet. B games the scans and breaks AC-165.2. The four scans check that a source file holds a literal the home now forbids, so they cannot pass unchanged. M-7 is read as clear because the task rows name each test and its new expectation and the plan waits for approval; this is disclosed to Mat. Weakness of A: the scans now prove the token, not the rendered key; AC-165.3 to AC-165.5 prove the rendered texts. Two-way."
  - id: D-1423
    stage: planning
    question: "How is 'in the current inbox' tested, and what does the scan do with rows of other folders?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a row is in scope when original_path.parent equals the current resolved inbox, with no filesystem call (INBOX_SCOPE); the scan and the list return only rows in scope, and neither scan loop probes, prunes or saves a row out of scope: the first loop checks a resolved file's parent before its probe, and the second skips such rows (INBOX_SCOPE_SCAN)."
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Catalog follows the inbox folder — Scope and Rows kept rows (D-1401)"
      - "packages/core/src/avkit_core/services/capture.py:1578 and :2080 — the service already tests shot.original_path.parent == inbox"
      - "packages/core/src/avkit_core/services/capture.py:706-709 — the prune of a row whose file is gone"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) skip rows out of scope in the scan; (B) filter only the returned list and keep the prune and the recovery for every row; (C) do nothing. B deletes the row of an old-folder shot whose file is missing, for example on an unplugged drive, which breaks the Rows kept row, and it makes the app read and repair a folder the user left. C leaves the issue open. Weakness of A: a row whose file was deleted in a folder the user never returns to stays in the database; it is small and comes back into the prune when the folder is chosen again. Two-way."
  - id: D-1424
    stage: planning
    question: "What does a by-id request answer for a shot outside the current inbox?"
    resolution: autonomous
    class: two-way
    mandatory: [M-5]
    chosen: "A: not found, exactly as an unknown id, on every public CaptureService method that takes a shot id (INBOX_SCOPE_BY_ID). No route, schema or OpenAPI change."
    source_tag: Human-approved
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Catalog follows the inbox folder — By id row: chosen at plan time (D-1401)"
      - "packages/core/src/avkit_core/services/capture.py:2283 — _require_inbox_file already refuses a path outside the inbox"
      - "packages/api/src/avkit_api/errors.py:37 — NotFoundError already answers 404 at run time; the OpenAPI document lists no 404 for the by-id routes and stays as it is"
      - ".agent/context/known-issues.yaml CAPTURE-INBOX-CHANGE-KEEPS-OLD-SHOTS — 'stay selectable and editable, mixed with the new folder's shots'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) not found for every by-id call; (B) reads allowed, writes refused; (C) do nothing: every by-id call still works. See the Decision Brief. A gives one rule for the app, the API and the MCP tools: the catalog is the current inbox. B needs a new refusal that no route documents, and C lets a stale id annotate, flatten or remove a file in a folder the user left. Weakness of A: an MCP client that kept an id across an inbox change gets 'not found' until the folder is chosen again. Two-way: one private lookup."
  - id: D-1425
    stage: planning
    question: "What does the page do with the open shot when the inbox change removes it from the list?"
    resolution: autonomous
    class: two-way
    mandatory: [M-5]
    chosen: "A: the save refreshes the list at once (INBOX_SAVE_REFRESH), and a selection that a list answer held and a later answer lacks is cleared with the delete path's resets (INBOX_SELECTION_LEFT); the page then opens the newest shot or shows the empty state. A selection is bound to the saved inbox it was made under, and a crop or PNG copy that ends under another saved inbox selects nothing (INBOX_RESULT_BOUND). Marks not saved on that shot are dropped."
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Catalog follows the inbox folder — Refresh row"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:663-682 — the newest shot is selected only when nothing is selected"
      - "ui/src/renderer/src/features/capture/useCaptureCatalog.ts — QUERY_KEY ['captures'] and the 5 s poll"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) refresh and clear; (B) hold the inbox save until the open shot's marks are saved or discarded, with a prompt; (C) do nothing: the list catches up on its 5 s poll and the open shot stays on screen. See the Decision Brief. With D-1424, C leaves a shot on screen whose every action answers 'not found'. B adds a dialog and a new blocked state to the settings save for a rare case. Weakness of A: unsaved marks on the open shot are dropped without a prompt; this is disclosed, and saved marks are kept. The clear also applies when a file is deleted outside the app, which is the same case. A crop or copy still running when the inbox is saved would otherwise select a result that the new list never holds, so its result is bound to the inbox it started in (round-1 review F2). Two-way."
  - id: D-1426
    stage: planning
    question: "Are the scroll bars drawn over the frame, or is the frame turned into a native scroll container?"
    resolution: autonomous
    class: two-way
    mandatory: [M-5]
    chosen: "A: drawn bars, absolutely positioned over the frame and computed from the view transform (SCROLL_BAR_OVERLAY); the frame stays overflow-hidden and capture-fit-map.ts does not change."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Viewport scroll bars — Build row: chosen at plan time (D-1402)"
      - "docs/build-plan/09-screenshot-capture.md:646 — the Pan gestures row: a clamped offset inside a fixed frame"
      - "ui/src/renderer/src/features/capture/capture-fit-map.ts:98 — viewTransform places the image box"
    research:
      engine: tavily
      sources:
        - "https://blog.master.dev/custom-scrollbar-component-in-2026"
        - "https://developer.chrome.com/docs/css-ui/custom-scrollbar"
        - "https://medium.com/@Fjonan/performant-drag-and-zoom-using-fabric-js-3f320492f24b"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) drawn bars over the transform; (B) a native overflow container with the pan kept in scrollLeft and scrollTop; (C) do nothing, which Mat's answer in D-1402 rules out and is listed for the record. See the Decision Brief. B moves the pan state into the browser's scroll position, so the pointer mapping, the zoom anchor, the pan clamp and every pan and zoom test would change, and the grouping gate keeps those tests unchanged. A adds a read-only view of the state the page already has. Weakness of A: a thumb covers a 10 px strip of the image at the edge, and the bars are the app's own, not the system's. Two-way: one module and one block of markup."
  - id: D-1427
    stage: planning
    question: "What can the user do with a bar, and how is it named for assistive technology?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a thumb drag only, through the existing clamped pan (SCROLL_BAR_DRAG); thickness 10 px and a shortest thumb of 24 px; role scrollbar with aria-orientation, aria-valuemin 0, aria-valuemax 100, aria-valuenow and aria-controls, and no tab stop (SCROLL_BAR_LOOK). No track click, no keyboard control, no wheel scrolling."
    source_tag: Research-backed
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Viewport scroll bars — Bars, Move and Look rows"
      - "the grouping gate — wheel zoom, Space+drag and middle-button drag keep their tests unchanged"
    research:
      engine: tavily
      sources:
        - "https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/scrollbar_role"
        - "https://w3c.github.io/aria"
        - "https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html"
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) thumb drag with the scrollbar role; (B) add a click on the track that pages the view and arrow keys on a focused bar; (C) show position only, with no drag, which does not meet the Move row. B adds two more inputs to a surface where a click already draws a mark and every key is a tool shortcut; each would need its own rules and tests, and Mat asked for a bar that shows where the view is and moves it. Weakness of A: the bars are not keyboard controls; Space+drag is unchanged and no keyboard pan exists today either. Two-way."
  - id: D-1428
    stage: planning
    question: "Where do the Electron proofs go, and what do they use?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: the key proof (AC-165.10) and the inbox proof (AC-166.7) run on the real backend and go into ui/tests/e2e/capture-settings-draft.test.ts, which already holds the real-backend launch and the bounded close; the two scroll bar proofs (AC-167.7, AC-167.8) go into ui/tests/e2e/capture-inbox.test.ts with its seam and pointer helpers. Shots are copies of the fixture capture-region-original.png in temp folders; the new key is F9; the inbox is set by the API before Capture opens."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/capture-settings-draft.test.ts AC-151.14 — a real-backend launch that saves a capture setting and closes within a bound"
      - "ui/tests/e2e/capture-inbox.test.ts — installSeam pins the settings and the catalog, so it cannot prove the service's scope"
      - "ui/tests/unit/e2e-pointer.test.ts AC-7 — the pointer helpers capture-inbox.test.ts must use"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) real-backend proofs beside AC-151.14; (B) all four in capture-inbox.test.ts, with the real-backend helpers copied into it; (C) all four in capture-inbox.test.ts on the seam; (D) a shared helper module for the real-backend launch. C would prove the inbox change against a fake catalog that the test itself writes, so it would not show the old shots leaving. B copies about 120 lines of process handling into a 3700-line file. D changes AC-151.14's file structure for no gain here. Weakness of A: one more E2E file outside the grouping's owns list (D-1429), and the grouping's words 'the same E2E file' hold for the scroll bars only. Two-way."
  - id: D-1429
    stage: planning
    question: "Which files outside the grouping's owns list does this session change?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: ten paths that the homes' rows force. Product: components/help/HelpCard.tsx, components/help/quick-start.ts, features/settings/SettingsPage.tsx. Tests: the Vitest files under ui/tests/unit (five new; capture-page.test.ts and settings-page.test.ts by name), tests/unit/test_capture_inbox_scope.py, tests/e2e/test_api_capture_inbox_scope.py, ui/tests/e2e/capture-settings-draft.test.ts, ui/tests/e2e/help-quick-start.test.ts, ui/tests/e2e/test-ids.ts and ui/tests/help-shots/help-shots.shots.ts. The existing Python test files the grouping names stay byte-identical."
    source_tag: Local Canon
    precedents:
      - "the grouping's Session Ownership block and its Session 103 Layer / files list"
      - "ui/src/renderer/src/components/help/HelpCard.tsx:114 — the card reads the quick start itself"
      - "grouping §2 — Session 105 shares the quick start and help files with 103; Session 106 shares settings-help-content.ts"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) change the ten paths and record them; (B) stay inside the owns list, which cannot meet the Set key row for the quick start or the Settings help, and cannot add a test id; (C) ask for the grouping to be changed first. The owns list is tier 1 and the two files other sessions own (HelpCard.tsx, SettingsPage.tsx) belong to tiers that run later, so no two sessions write one file at the same time. New pytest files are used so that the two existing files the grouping names keep their bytes. This is reported to the orchestrator, who owns the grouping. Two-way."
  - id: D-1430
    stage: planning
    question: "How many mini-air runs does the session make, and when is a run reused?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: two full-suite runs. Row 1 runs a snapshot of HEAD plus the two E2E files and must end new-failures with exactly the four new tests failing on an expectation; the base test count is taken from that run. Row 10 runs a snapshot of every changed path under ui/ and packages/ and must end ok with the base count plus 4. The gate reuses row 10's run when the tree under ui/ and packages/ equals that snapshot, and runs again when it does not."
    source_tag: Human-approved
    precedents:
      - "grouping D-1411 — Mat: 'use fleet member mini air for E2E testing during execution'"
      - ".agent/docs/e2e-remote-host.md — the run book, the exit bands and the last stdout line"
      - "docs/execution/plans/2026-11-20-e2e-clipboard-specs/task.md row 8 — the snapshot, check, run and summary check"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) one Red run and one proof run; (B) a Red run per MEU and a proof run per MEU, six runs of about 40 minutes on a host shared with another runner; (C) no Red run on mini-air, which leaves the four E2E tests without a recorded failure before the change. The tool runs the whole suite each time, so one Red run records all four failures. Weakness of A: a wrong E2E test found in row 10 costs one more run. Two-way."
  - id: D-1431
    stage: planning
    question: "Does MEU-167 stay in this session?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: yes. MEU-167 is one pure module, about 70 lines in CaptureViewport.tsx and about 350 lines of tests, well under half a context."
    source_tag: Local Canon
    precedents:
      - "the grouping's Session 103 Split flag — 'no. If the plan sizes MEU-167 over half a context, it moves to its own session'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) keep it; (B) move it to its own session; (C) do nothing differs from A in nothing. The drawn-bar build (D-1426) reads state the viewport already has and changes no pan or zoom code. Its two E2E tests share the two mini-air runs with the other MEUs; a session of its own would pay two more runs. Two-way."
  - id: D-1432
    stage: planning
    question: "Which 09 lines change on delivery?"
    resolution: autonomous
    class: two-way
    mandatory: [M-8]
    chosen: "A: in row 11, through canon-edit.py with CRLF kept: the Pan gestures row of §Viewport zoom is rewritten to name the bars (the Replaces row asks for it); the empty-state line (:115) names the configured key with F2 as the default; the scan and catalog lines (:308, :480 to :482) say that the prune, the list and the by-id lookups cover the current inbox only; and each of the three homes gets a 'Delivered (Session 103)' note."
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md §Viewport scroll bars — Replaces row"
      - "docs/build-plan/09-screenshot-capture.md:115, :308, :480, :481, :482, :646"
      - "docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes — row 7: the 09 row and the Delivered note"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the six line groups; (B) only the Pan gestures row, which the home names; (C) do nothing. B leaves 09 saying 'Press F2' as spec text and saying that the scan prunes every row, both contradicted by the delivered code. The file is dirty from other sessions today, so row 11 re-reads it and edits by anchor. Two-way."
  - id: D-1433
    stage: execution
    question: "Which grouping cell does row 11's canon edit accept before it writes 'executed (Session 103)'?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: canon-edit.py accepts '| planning |', '| planned |' or '| plan approved (round 2) |' in Session 103's status cell and writes '| executed (Session 103) |'; any other cell stops the edit."
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-26-ui-findings-and-auto-update-session-grouping.md:281 — Session 103's status cell reads 'plan approved (round 2)' at HEAD e5028a3"
      - "docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test/canon-edit.py — Session 104's script, copied here, which accepts only planning or planned"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) accept the cell the grouping now holds as well as the two earlier forms; (B) keep only planning or planned, so row 11 stops on a cell that the orchestrator wrote at plan approval; (C) do nothing and edit the cell by hand, outside the before-copy and the anchor check. A keeps the anchor check and the before-copy and matches the file as it is. Weakness of A: a cell written by hand to the round-2 form also passes; the edit still writes only Session 103's row. Two-way."
  - id: D-1434
    stage: execution
    question: "How does row 0 test that a declared new name is free, for names that are also ordinary words?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: a name is a hit only as a whole token, with a hyphen counted as part of the token; 'saved' is tested as a key that useCaptureSettings.ts returns (a line matching ^\\s*saved\\s*[,:}]); 'capture-key' is tested as a module path (a file named capture-key.ts or capture-key.tsx, or a line that names /capture-key, 'capture-key' or capture-key.ts). Hits in this session's own files do not count."
    source_tag: Local Canon
    precedents:
      - "implementation-plan.md §Session gate row 0 — the free-id check of each declared new name"
      - ".agent/context/handoffs/2026-11-14-capture-tool-flow-plan-critical-review.md:33 and :182, docs/execution/metrics.md:81, docs/execution/reflections/2026-11-14-capture-tool-flow-reflection.md:30 — 'capture-key' as prose for the capture settings keys ('the capture-key suffix', 'the capture-key order pin')"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) test each name in the form the plan adds it; (B) a plain substring test, which fails on 'saved' in hundreds of lines and on four lines of 2026-11-14 prose about settings keys, none of which is the new hook key or the new TS module; (C) drop the free-id check. A still stops row 0 when the hook already returns 'saved' or a module named capture-key exists. Weakness of A: a prose use of 'capture-key' in a later document reads as a settings phrase, not as the module. Two-way: a check in baseline.ps1 only."
  - id: D-1435
    stage: execution
    question: "Row 1 says 'no raised timeout'; may the two real-backend tests (AC-165.10, AC-166.7) set the test budget that AC-151.14 sets?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: AC-165.10 and AC-166.7 call test.setTimeout(240_000) as their first statement, as AC-151.14 does; every expect keeps its own bounded timeout (15 s at most after launch), and the seam tests AC-167.7 and AC-167.8 keep the config's 60 s."
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/capture-settings-draft.test.ts:152 — AC-151.14 sets test.setTimeout(240_000) for the same launch, whose backend poll alone allows 120 s"
      - "ui/playwright.config.ts:16 — the config's test timeout is 60 s"
      - "implementation-plan.md §Verification row 1 — each Red fails on an expect with no 'Test timeout'"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) the AC-151.14 budget for the launch; (B) keep 60 s and shorten the launch polls, which on mini-air can end in a Test timeout during backend start, the one Red that remote-red refuses; (C) do nothing and read the row's words as forbidding the budget, which gives the same risk as B. The row's rule is aimed at a Red that times out instead of failing an expect; A keeps every assertion bounded and fails first on the 15 s expect. Weakness of A: a hung step after launch has 240 s, not 60 s, before the test stops. Two-way: two lines in a test file."
  - id: D-1436
    stage: execution
    question: "Row 5's first Green run failed AC-166.5 and AC-166.6 on two defects of the row 4 test, not of the product code; may the test be amended and row 4's Red run again before row 5?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: amend ui/tests/unit/capture-inbox-scope.behavior.test.ts in its harness only: AC-166.5 counts list requests from the index of the inbox PUT, not from after the wait for it; releaseList ends the hold before it answers, so the refetch that replaces a cancelled held request also answers; AC-166.6 sets the hold again before its second save. Then rerun row 4's whole cell (Red by assertion, a new red-record hash), then row 5. red-record refuses a second hash for a row, so the first record is kept as cki-red-hashes.row4-r1.json (copies in cki-red-copies-row4-r1) and row 4 is dropped from cki-red-hashes.json before the rerun."
    source_tag: Local Canon
    precedents:
      - "cki-row5-green.txt — AC-166.5 'expected [] to have a length of 1' while the recorded calls show GET /captures right after the PUT and the settings GET; AC-166.6 still shows A's two shots"
      - "task.md row 5 — 'Change no test'; row 4 records the hash that red-unchanged checks"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) fix the two harness defects and redo row 4, so the record stays a true Red of the fixed file; (B) bend the product code to the defects, for example a delayed refresh, which would break INBOX_SAVE_REFRESH's 'at once'; (C) do nothing and stop at row 5, which leaves MEU-166 unfinished. A changes no assertion and no AC; every required test still fails by assertion at Red. Weakness of A: row 4 runs twice, and the review sees an amended Red file. Two-way: a test-file edit."
  - id: D-1437
    stage: execution
    question: "Row 7's first Green run failed two tests that do not test the product: AC-165.1 ran a stale vitest transform of capture-key.test.ts (its import.meta.glob still empty from the Red run), and guard AC-165.8 found the Settings help card already open from the test before it; may the stale cache entries be removed and the row 6 test amended and its Red run again before row 7?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: remove the vitest file-cache entries (ui/node_modules/.vitest-cache) that hold a transform of either new test, before and after each phase change; amend ui/tests/unit/capture-key.behavior.test.ts in its harness only (afterEach clears localStorage, where a help card keeps its open state); rerun row 6's whole cell with the product files at their row 6 state (byte-exact HEAD content for the files row 7 first touches, CapturePage.tsx with row 7's edits reversed, no capture-key.ts), which records the new hash; then row 7. red-record refuses a second hash for a row, so the first record is kept as cki-red-hashes.row6-r1.json (copies in cki-red-copies-row6-r1) and row 6 is dropped from cki-red-hashes.json before the rerun."
    source_tag: Local Canon
    precedents:
      - "D-1436 — the same redo for row 4's harness"
      - "cki-row7-green.txt — AC-165.1 'capture-key.ts exists: expected undefined'; a copy of the same file passes; the cached transform of 11:41 holds Object.assign({}) for the glob"
      - "cki-row7-green.txt — guard AC-165.8 'expected '' to match /so F2 still works/' after AC-165.8 opened the card"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) clear the stale transforms, fix the harness and redo row 6, so the record stays a true Red of the fixed file; (B) change the product so the card forgets its open state, which breaks the card's saved state; (C) do nothing and stop at row 7, which leaves MEU-165 unfinished. A changes no assertion and no AC; every required test still fails by assertion at Red (row6-console-r2.txt). The cache is a build cache outside the repository. Weakness of A: row 6 runs twice, and the review sees an amended Red file. Two-way: a test-file edit and a cache removal."
  - id: D-1438
    stage: execution
    question: "The first H1-2 gate run stopped at ui-tests: 9 tests in six main-process files that this session does not change timed out at Vitest's 5 s limit while another repository's gate ran about 50 pytest workers on the same PC; may the whole gate run again, and on what condition?"
    resolution: autonomous
    class: two-way
    mandatory: none
    chosen: "A: keep the first run's receipts as cki-gate-h1-r1.txt and cki-D6-*-r1.txt; wait until the other repository's gate processes have ended; then run the whole gate again, unchanged, once. No test is excused, deselected or given a longer timeout. If the second run fails in any step, stop and report it."
    source_tag: Local Canon
    precedents:
      - "cki-D6-ui-tests-r1.txt — 'Tests  9 failed | 1707 passed (1716)', each failure 'Error: Test timed out in 5000ms.', in capture-lifecycle, capture-paste-main, capture-picker, e2e-harness, rejection-watch and setup-readiness"
      - "cki-h12-diag-6files.txt — the same six files alone: 'Tests  99 passed (99)', 'Duration  551ms'"
      - "Session 104's gate ran three times; each run after the first followed a recorded cause"
    research: { engine: none, sources: [] }
    reasoning: "Handed to the agent: USER_EXPLICIT 2026-11-18 'make the decisions always the recommenations'. Options: (A) rerun the whole gate once after the other load ends, with the first receipts kept; (B) raise the Vitest timeout of the six files, which changes tests outside this plan's files (M-7) and hides a real slow-down; (C) stop and report with no rerun, which leaves H1-2 unproven for a cause outside the session. The six files import nothing this session changes (ui/src/main/ is read-only here) and pass alone in under a second, so the timeouts measure the PC's load, not the product. Weakness of A: one more full run; a second failure is not excused, it stops the session. Two-way: a rerun changes no file."
open_decisions: []
```

### Decision Briefs

**D-1424: a shot outside the current inbox, asked for by id.**

- **Recommended, and taken: it is not found.** The app, the API and the MCP tools treat the shot exactly like an id that does not exist. You get one rule: the catalog is the folder you chose. The shot and its marks are untouched and come back when you choose the old folder again.
- **Alternative: it can be read but not changed.** An old id still shows its image, but annotate, crop, flatten, revert and remove are refused. This needs a new kind of refusal in the API, and a client must learn two rules.
- **Keep things as they are:** every old id keeps working. A client that kept an id could then change or delete a file in a folder you left, while the list no longer shows it.

**D-1425: the open shot when you save another inbox folder.**

- **Recommended, and taken: the list refreshes at once and the page moves on.** It opens the newest shot of the new folder, or shows the empty state. A crop or copy that finishes after the change is not opened; its file stays in the old folder. Marks you drew on the old shot and did not save are dropped; saved marks are kept on disk.
- **Alternative: the save waits.** If the open shot has unsaved marks, a prompt asks you to save or discard them before the inbox changes. It protects those marks, at the cost of a new dialog in the settings save.
- **Keep things as they are:** the list catches up within five seconds and the old shot stays on screen. With D-1424 that shot could then no longer be saved or changed.

**D-1426: how the scroll bars are built.**

- **Recommended, and taken: bars drawn over the frame.** They read the zoom and pan the page already has. Zoom, Space+drag and middle-button drag work exactly as today. A thumb covers a thin strip of the image at the edge.
- **Alternative: the system's own scroll bars.** The frame becomes a scrolling box. The bars look like every other Windows scroll bar, but the pan and zoom code and all their tests must be rebuilt on the browser's scroll position.
- **Keep things as they are:** no scroll bars. Mat's answer in D-1402 rules this out; it is listed for the record.

## Research References

- WAI-ARIA `scrollbar` role, its required `aria-valuenow` and `aria-controls`, and its default vertical orientation: <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/scrollbar_role>, <https://w3c.github.io/aria>.
- Custom scroll bars and their thumb geometry: <https://blog.master.dev/custom-scrollbar-component-in-2026>, <https://developer.chrome.com/docs/css-ui/custom-scrollbar>.
- Pan and zoom kept as a transform, not as a scroll position: <https://medium.com/@Fjonan/performant-drag-and-zoom-using-fabric-js-3f320492f24b>.
- WCAG 2.1 SC 1.4.11 Non-text Contrast, 3:1: <https://www.w3.org/WAI/WCAG21/Understanding/non-text-contrast.html> (from knowledge; not in a receipt).

## Planning receipts

All under `C:/Temp/av-kit/2026-11-26-plans/s103/`, read-only against the repository:

| Receipt | What it shows |
|---|---|
| `f2-src.txt`, `f2-tests.txt`, `f2-text-pins.txt` | Every `F2` in the renderer sources and in the tests, and the pins on the key texts |
| `ste-probe.py`, `ste-probe.txt` | The STE linter's rules run on the token texts: no finding |
| `meu-stats.txt` | 174 MEUs, 10 pending |
| `precedent-issues.txt` | The register entries of the three issues and the watch item |
| `research-aria-scrollbar.txt`, `research-zoom-scrollbars.txt` | The research answers for D-1426 and D-1427 (engine `tavily`) |
| `cki99-task-lint.txt` | `tools/lint_task_contract.py` on `task.md` |

## Validation stage contract

| Stage | Checks | Where |
|---|---|---|
| Plan review | This plan and `task.md`, against the three 09 homes, the three issues, the grouping's Session 103 block and the code reads above | `cki-plan-2026-11-26-capture-key-inbox-scrollbars` (dispatched by the orchestrator) |
| Row checks | Each row's validation command | `task.md` |
| Session gate | §Session gate | H1-2 |
| Execution review | The delta from `baseline.sha` in the §Files Modified paths, against AC-165.1 to AC-165.10, AC-166.1 to AC-166.8 and AC-167.1 to AC-167.8 | `cki-execution-2026-11-26-capture-key-inbox-scrollbars` |
