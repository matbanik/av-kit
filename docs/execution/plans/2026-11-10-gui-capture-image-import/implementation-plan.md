---
project: "2026-11-10-gui-capture-image-import"
date: "2026-11-10"
source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md#session-61--gui-capture-image-import-meu-132--p2"
grouping_source: ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md"
meus: ["MEU-132"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Image import on the Capture page (Session 61)

> **Project:** `2026-11-10-gui-capture-image-import`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §GUI image import (`:1091-1102`, anchor `gui-image-import`, MEU-132).
>
> **Source request.** Mat asked on 2026-11-08 for crop and import on the Capture page, agent use first (`_inspiration/capture-crop/design.md` §7.2, design D-12). Session 58 shipped the import endpoint (`POST /captures {"mode":"import","path":…}`, MEU-129). The grouping (D-400 to D-406) puts slice S5, the GUI entry points, here, as the grouping's last session. Done comes from 09's contract, not from Mat's words: drop, the **Import image…** button and Ctrl+V each hold with a behaviour test, and an Electron proof covers a real drop and a real paste.
> **Known issues:** none open for this MEU. `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` (P2) and `CAPTURE-EXIF-SCANNED-ORIENTATION` (P3) are out of scope: an observation of either is recorded in the handoff and raised, never fixed here. `MCP-AUDIT-BASELINE-PENDING-CROP` stays open and isn't touched. `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` is out of scope.
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review. Two questions are Mat's (§User Review Required): D-560, the system clipboard in the paste proof, and D-561, the human look.

## Goal

**Goal anchor:** Session 61 lets a person bring images into the Capture inbox three ways. Image files dropped on the Capture page are imported one by one through the import endpoint. An **Import image…** button with the lucide `ImagePlus` icon opens a file dialog in main, filtered to png, jpg, jpeg and webp, with multi-select, and imports each file the same way. Ctrl+V with an image on the clipboard has main write it to the inbox as `{yyyy-MM-dd_HH-mm-ss}.png` and register it as `gui` through the hotkey's publication path, while text fields keep their native paste. One toast reports each run, and a file that isn't an image is named in it with a fixed reason.

Four things are missing today:

1. **No drop on the Capture page.** `CapturePage.tsx`'s `<section data-testid="capture-page">` (`:1996`) has no drag or drop handler, though preload already exposes `getPathForFile` (`ui/src/main/preload.ts:45`).
2. **No import button or renderer call.** The header holds only Capture region (`CapturePage.tsx:2002-2022`), and `capture-commands.ts` has no call for `mode: "import"`.
3. **No paste.** Ctrl+V is reserved (`RESERVED_CHORDS`, `ui/src/renderer/src/registry/shortcuts.ts:132-138`, D-136), so no command can take it, and main has no IPC that writes a clipboard image to the inbox. The hotkey's publication path (`publishStagedCapture`, `ui/src/main/capture-picker.ts:456-529`) takes only a picker's staged file and always notifies with paths.
4. **No toast on the Capture page.** Its errors go to the status line (`run`, `CapturePage.tsx:1624`), which names one error, not a run over several files.

The session ends when 09's §GUI image import holds with a behaviour test per rule, the Electron proof passes, the session gate's last line is `session-gate: all steps exit 0`, D-560 and D-561 are ruled, and MEU-132 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-10). No payload is oversized: CapturePage.tsx (2305 lines) and capture-picker.ts were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s61-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s61\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s61-plan-canonical-2026-11-10-gui-capture-image-import` and `s61-execution-2026-11-10-gui-capture-image-import`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before dispatching.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path (Session 49b D-290), and the `--review-state-only` receipt is rebuilt there.
  - Reviewer prompts name the ledger vocabulary up front: D-550 to D-565, AC-132.1 to AC-132.23, and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4). Each recheck asks for a `### New Findings` table and bare words in its Recheck cells (`fixed`, `open`).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, the live MCP audit, `--update-baseline`, a tag, release or upload, or an `approved` verdict authored by the implementer. Capture stays local: no test or row uploads an image or reads one from the network. Unit tests build images in the renderer's test setup or as byte buffers; the Electron proof builds its PNGs in main with `nativeImage.createFromBitmap`; the look and the Python guard use Pillow images under `C:/Temp/av-kit/s61`. Nothing touches the installed avkit MCP servers, Mat's inbox or YouTube. The paste proof touches Mat's system clipboard only as D-560 rules.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-132 `gui-capture-image-import` | `.agent/context/handoffs/2026-11-10-gui-capture-image-import-MEU-132-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-10-gui-capture-image-import-plan-critical-review.md` and `.agent/context/handoffs/2026-11-10-gui-capture-image-import-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, `s61-anchors.txt` |
| WP-2 | Type-only names (row 1) | WP-1 | shared | `capture-import.ts` stubs, the `importCapture` stub, the `capture-paste-image` channel with a handler that answers `failed`, the preload key and its type, the `pasteClipboardImage` stub, an Import button that does nothing, the moved IPC pins |
| WP-3 | Module and main Red, then Green (rows 2, 3) | WP-2 | shared | `IMPORT_TYPES`, `IMPORT_NAME`, `IMPORT_RUN`, `IMPORT_CALL`, `PASTE_MAIN`, `PASTE_PUBLISH`, `PASTE_LOG`, `PASTE_IPC`; `row3-ui-src.json` |
| WP-4 | Page and Electron Red, then Green (rows 4, 5) | WP-3 | shared | `IMPORT_BUTTON`, `IMPORT_DROP`, `PASTE_KEY`, `PASTE_MESSAGES`, `IMPORT_TOAST`, `IMPORT_GATE`, `SELECTION_EFFECTS`, `ACTIONS_INDEX`, `IMPORT_ELECTRON`, the test-id block |
| WP-5 | Human look (row 6, under D-561) | WP-4 | shared | `LOOK_LAUNCH`, `human-check.md` |
| WP-6 | Records (row 7) | WP-5 | shared | The 09 note, MEU status, renders, grouping tracker |
| WP-7 | Closeout (H1, H2) | WP-6 | `compact_continue` | The handoff, review, reflection, Session 62's prompt |

The page Red and the Electron Red share row 4, as Session 60's did: an Electron Red written after the page Green would pass at once and prove nothing. Row 4 builds the row 3 renderer and refuses to run if any `ui/src` file differs from `row3-ui-src.json`, so both Reds run on the tree before the page wiring exists. The main-process paste is Green by then; the Electron paste Red still fails, because the row 1 page has no `paste` listener.

**Split flag (D-559): no 61b.** The grouping (`:80`) set no split for this session, and the work doesn't need one. The paste path is about 12 ACs of unit work around a function that reuses the hotkey's publication path; the page work is three small handlers, one toast and one gate over state that already exists. Session 60 was larger (24 ACs, a geometry module, two components, a live agent run) and finished in one session. If the session passes about half its context before row 4, the coordinator tells Mat; nothing moves without Mat's words, because a split here would separate the Electron drop from the Electron paste that 09's Tests row asks for together.

## User Review Required

> [!IMPORTANT]
> **Two questions are Mat's.** Every other choice is recorded as autonomous in §Decision Log (D-550 to D-559, D-562 to D-565), with its alternatives. The gate asks Mat to accept the plan, rule D-560 and D-561, set the execution budget, and override any autonomous choice. Only Mat's words start execution.
>
> **D-560: how does the Electron paste proof treat Mat's system clipboard?** (`governance-value`.) A real Ctrl+V in the real app reads the Windows clipboard, which is Mat's: whatever Mat copied last is on it while the proof runs.
> - **A (Recommended): save, restore and verify.** Before the proof writes its test PNG, `capture-import.test.ts` reads the clipboard in main through `app.evaluate`: `clipboard.availableFormats()`, the text, HTML, RTF and the image (as PNG bytes). It writes the test image, runs the paste steps, and in a `finally` block writes the saved formats back in one `clipboard.write` call, then reads them again and fails the test if any differs. `hotkey-free.py` first checks that no other program holds the clipboard open (`OpenClipboard` then `CloseClipboard`, error named, nothing stopped). **What A can't keep:** formats Electron can't read or write (a file list copied in Explorer, Office's private formats, custom formats) are lost, and Windows' clipboard history (Win+V) gets the test image and the restored entry. The test prints `availableFormats()` before and after so a loss is visible. Mat is asked not to copy anything during the gate's Electron step, which runs about two minutes.
> - **B: a seam.** With `AVKIT_E2E=1` and `AVKIT_E2E_PASTE_PNG` set, the paste dep reads that PNG file instead of the clipboard, as `readClipboard` already answers `'pasted'` under E2E (`ui/src/main/index.ts:395-399`). Mat's clipboard is never touched. The real `clipboard.readImage()` call then runs only in the look and in the unit tests' stub, so the Electron proof proves the keystroke, the IPC, the publication and the register, but not the read.
> - **C, do nothing:** the proof writes its image to the clipboard and leaves it there. Whatever Mat had copied is lost each time the gate runs.
>
> **D-561: does Mat look at the import before the execution review?** (`human-check`.) Row 6 runs after the Electron proof is Green and before H1-7.
> - **A (Recommended): Mat looks.** Row 6 builds a test inbox and app data under `C:/Temp/av-kit/s61/look` (one Pillow shot already in the inbox) and a drop folder `C:/Temp/av-kit/s61/look/drop` holding two Pillow PNGs, a JPEG and `notes.txt`. It launches the dev app detached on that app data (`Start-Process`, `AVKIT_APP_DATA` set, `ELECTRON_RUN_AS_NODE` cleared), records the process ids and later stops only those. Mat drops the two PNGs and `notes.txt` from Explorer, imports the JPEG through the button, and pastes a Win+Shift+S snip. Mat's words go in `human-check.md`. The tests check rules; only a person can judge whether the toast reads well, whether a drop feels accepted with no highlight, and what a real snip does.
> - **B, do nothing:** the review runs on the Electron proof alone, and Mat looks after the commit. Row 6 writes `human-check.md` with `decision: not-run` and Mat's ruling, and launches nothing.
> - **What Mat's "no" changes.** Each finding becomes a fix row before H1-7, with its own Red where it is a rule. A finding that changes 09's contract or an AC (for example a drop highlight, a timed toast, or paste into a text field importing too) goes to Mat as a brief under S59 RULE-3, with a do-nothing option, and doesn't change an AC without Mat's words.
>
> **What the words in the contract mean here, and the limits they leave.**
> - **"Imported one by one."** One `POST /captures {"mode":"import","path":…}` per importable file, in the order the drop or the dialog lists them, each awaited before the next, then one refetch (`IMPORT_RUN`, D-553).
> - **"A file that isn't an image shows an error toast."** The renderer decides "image" by the last extension, the same four the dialog filters to and the server's own suffix rule (`IMPORT_TYPES`, D-558). A non-image is never sent; the toast names it with the fixed reason `not an image av-kit can open (png, jpg, jpeg, webp)`. A file with an image extension that the server refuses (corrupt, too large, unreadable) is named with the server's message. The toast is the page's one `BulkResultToast` (D-554), which is dismissible and has no timer.
> - **"The hotkey's publication path."** The paste writes a staging file in the inbox, then runs the same steps the hotkey's picker result does: the blank and black pixel check, the exclusive claim of `{yyyy-MM-dd_HH-mm-ss}.png` (a taken name gets `_2`, `_3`… as the hotkey's does), the settle and the register as `gui` (`PASTE_PUBLISH`, D-556). It doesn't copy the image back to the clipboard and doesn't raise a system notification; the renderer's toast reports the outcome instead (`PASTE_MESSAGES`).
> - **"Text fields keep their native paste."** A paste whose target is a text input, a textarea or an editable element is left alone (`isEditableTarget`). Anywhere else on the Capture page, Ctrl+V asks main to paste. Ctrl+V stays in `RESERVED_CHORDS`, and no registry entry is added (D-550).
> - **The crop and unsaved marks.** While the crop is open (D-515), a confirm dialog is open, or an import is running, a drop, a paste and the button do nothing (the button is disabled with a reason). Unsaved marks don't block an import: the selection doesn't change, so the marks stay on the shot they belong to (`IMPORT_GATE`, D-555).
>
> **The token estimate,** calibrated against Session 41 `gui-keyboard-palette` (plan 32.5M over 3 rounds, execution 6.1M), Session 60 (plan 20.8M over 3 rounds; execution round 1 10,867,306 and round 2 4,244,246, 15.1M of a loop Mat raised to 30M) and Session 59 (execution round 1 8,336,600, round 2 4,475,811). This session has one MEU across the main process and the renderer, a new module, one IPC channel, a toast, 23 ACs, a Python guard and an Electron proof that touches the clipboard, plus a human look. Expect 1 to 3 plan rounds (about 10M to 24M) and 2 to 3 execution rounds. The plan loop opens with the default 10.5M. At the plan gate Mat sets the execution loop's budget; the opening ask is round 1 ×2 plus one recheck at about half of round 1 (Session 60 RULE-5, Session 58 RULE-4): about 10M ×2 + 5M = 25M, 3 rounds. The citable AC family is fixed when the plan loop opens: AC-132.
>
> **The gate.** Mat ruled on 2026-11-10 at the plan gate, after Codex approved the plan in round 3 (10,063,310 + 4,933,328 + 2,829,804 = 17,826,442 tokens of a loop Mat raised to 50M and 6 rounds). Execution: "Start execution (Recommended)". Execution review budget: "50M tokens, 6 rounds", so H1-7 opens `s61-execution-2026-11-10-gui-capture-image-import` with 50,000,000 tokens and 6 rounds. D-560: "A: save and restore (Recommended)". D-561: "A: I'll look (Recommended)". No autonomous choice was overridden.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `IMPORT_TYPES` | `IMPORT_EXTENSIONS = ['png', 'jpg', 'jpeg', 'webp']` in the new `features/capture/capture-import.ts`. `isImportableName(name)` takes the text after the last `.` of the basename, lowercased, and is true when it is one of the four. It is false for a name with no `.`, for `.png` (a dotfile has no suffix, as Python's `Path.suffix` reads it), for `a.` and for `a.png.txt`. |
| `IMPORT_NAME` | `importDisplayName(name)` is the basename after the last `/` or `\`, with each control character (U+0000 to U+001F, U+007F) and each lone surrogate replaced by U+FFFD; an empty result is `(unnamed file)`. It is the only form of a file's name the toast shows. A path never reaches the toast. |
| `IMPORT_RUN` | `importFiles(entries: {path, name}[], port: {importOne(path), refetch()})` walks the entries in order. An entry whose `path` is empty fails with `not a file on disk` and an entry that isn't `isImportableName` fails with `not an image av-kit can open (png, jpg, jpeg, webp)`, both with no call. Every other entry awaits `port.importOne(path)` before the next. Only MEU-129's own refusal shows its text: an `ApiError` with `status` 422 and `code` `InboxPathError` (the envelope `errors.py` builds from `str(exc)` for the service's fixed, path-free messages, D-416) fails the entry with that error's `message`. Every other error fails it with `the import could not be completed`: the `ApiError`s `apiFetch` builds from a thrown fetch (`FETCH_FAILED`, `ui/src/renderer/src/lib/api.ts:75`) or from backend resolution (`BACKEND_NOT_READY`, `:52`), whose messages carry the thrown text; an envelope-less `HTTP_ERROR` that carries the raw body; `validation_error`, `http_error` and any 5xx; and any non-`ApiError` throw. After the walk, `port.refetch()` runs once if any call was made. The result is a `BulkResult` keyed by display names: `message` is `Imported N of M.`, or `Imported N of M. K failed: {name} - {reason}; {name} - {reason}` when any failed. It never names a path. |
| `IMPORT_CALL` | `importCapture(path)` in `capture-commands.ts` is `POST /captures` with body exactly `{mode: 'import', path}`, returning `{item}`. The server's own rules apply unchanged (MEU-129). |
| `IMPORT_GATE` | `importBlocked` is true while the crop is open (`cropRef.current !== null`, `CapturePage.tsx:397`), while a confirm dialog is open (`confirm !== null`, `:349`) or while an import or paste is running. While it is true, a drop and a paste do nothing and the button is disabled: with the reason `Finish or cancel the crop first` for the crop, `aria-busy="true"` while running. `dirty` (`:412`) doesn't block. |
| `IMPORT_BUTTON` | `capture-import`: `Button` `secondary` `md` with the lucide `ImagePlus` icon (`aria-hidden`) and the label `Import image…`, straight after `capture-region` in `capture-header` (`CapturePage.tsx:2001`). Its title is `Import image files. You can also drop them here or paste with Ctrl+V.` A click calls `window.api.showFilesDialog([{ name: 'Images', extensions: IMPORT_EXTENSIONS }])` on the existing `show-files-dialog` channel (D-552), whose main side already allows multi-select (`SHOW_FILES_PROPERTIES`, `ui/src/main/ipc.ts:17`). An empty result does nothing; otherwise each path becomes `{path, name: path}` for `IMPORT_RUN`. |
| `IMPORT_DROP` | `dragover` and `drop` handlers on the `capture-page` section. Both call `preventDefault()` whenever `dataTransfer.types` includes `Files`, gated or not, so a dropped file never navigates the window. Under `IMPORT_GATE` the drop does nothing else. Otherwise each `dataTransfer.files` entry becomes `{path: window.api.getPathForFile(file), name: file.name}` for `IMPORT_RUN`, in list order (D-551). A drag with no `Files` type is left alone. |
| `PASTE_KEY` | A `useEffect` in `CapturePage` adds a `paste` listener on `window` and removes it on unmount. When the event's target is `isEditableTarget`, it returns and the native paste runs. Under `IMPORT_GATE` it returns. Otherwise it calls `preventDefault()`, then `window.api.pasteCaptureImage()`, shows `PASTE_MESSAGES`, and invalidates `['captures']` after a `saved` outcome. `isEditableTarget(target)` is true for a `TEXTAREA`, for an `INPUT` whose type is text, search, url, tel, email, password or number (or has none), and for any element with `isContentEditable`. No `commandRegistry` entry is added and `RESERVED_CHORDS` doesn't change (D-550). |
| `PASTE_IPC` | The channel `capture-paste-image` with `noPayloadSchema` (`ipc.ts:52`), appended last to `RENDERER_TO_MAIN_CHANNELS` (`ipc.ts:19`), to `ui/tests/unit/ipc-channels.ts` and to the strict census. `IpcDeps` gains `pasteCaptureImage?: () => Promise<PasteOutcome>`; a missing dep answers `{kind: 'failed'}`. Preload's `pasteCaptureImage` invokes it and is appended last to `API_KEYS` (`preload.ts:3`); `env.d.ts` gets its type. The `index.ts` dep sits beside `captureRegion` (`:418-428`): it reads `clipboard.readImage()`, passes `null` when `isEmpty()` and otherwise `toPNG()`, with `BrowserWindow.getAllWindows()[0]` and `resolveInboxDir: () => resolvePasteInbox(fetchCaptureRuntime)`. Main's cached `captureInboxDir` can be wrong for a paste in two ways: it is the default `~/Pictures/av-kit` (`index.ts:228`, `capture-runtime.ts:10`) until `refreshCaptureRuntime` (`:559`) first gets a settings answer, and after a Save in Settings it keeps the old folder until the next successful 1-second poll. So the paste never reads it. `resolvePasteInbox(readSettings)` in `capture-picker.ts` awaits `readSettings()` once on every call and answers that reply's `inbox_dir`, or `null` when the read answers `null` or rejects. `fetchCaptureRuntime` (`capture-runtime.ts:65`) already answers `null` when the backend isn't ready, on a non-ok status and on a thrown request. The resolver doesn't touch `captureRuntime`, `captureInboxDir`, the runtime hooks or the watcher, so it can't race the poll, apply a runtime twice or roll the cache back. The hotkey, picker and tray keep reading `captureInboxDir` as today. |
| `PASTE_MAIN` | `pasteClipboardImage({resolveInboxDir, window, readClipboardPng, nextStagingName?})` in `capture-picker.ts`. It has its own `pasteInFlight` flag: a second call while one runs answers `{kind: 'busy'}`. It first awaits `resolveInboxDir()`. A `null` answer, or a rejection, answers `{kind: 'not-ready'}` before the clipboard is read and before any filesystem call, so a paste can never create or write a folder that isn't the configured inbox. A `null` read answers `{kind: 'empty'}` with no file written. Otherwise it expands the resolved inbox and creates it, writes the bytes to `PICKER_STAGING_PREFIX + hex + '.tmp'` in the inbox with `openSync(…, 'wx')` (an existing name, another writer's included, is never opened, and a new name is drawn), then runs `PASTE_PUBLISH`. It answers `{kind: 'saved', name, registered}`, `{kind: 'blocked', reason: 'black' \| 'empty'}`, `{kind: 'not-ready'}` or `{kind: 'failed'}`. It never rejects: every filesystem call on the inbox, from the expand to the staging removal, sits inside the error mapping (S58 RULE-2), and a failure removes its own staging file. |
| `PASTE_PUBLISH` | The body of `publishStagedCapture` (`capture-picker.ts:456-529`) moves into an inner `publishStaged(stagingPath, opts)` that returns a `PublishOutcome` and takes `notify`, `logPaths` and `copyToClipboard`. `publishStagedCapture` calls it with `notify: true`, `logPaths: true` and its own clipboard setting, so the hotkey and the picker keep their current behaviour and messages byte for byte; their tests run unchanged as guards. The paste calls it with `notify: false`, `logPaths: false`, `copyToClipboard: false`, source `gui` and register on. The claim (`claimInboxName`, `:432`), the settle and `finalizeCapturedPng` (`capture-register.ts:174`) are the same calls. |
| `PASTE_LOG` | A paste's log lines carry a fixed code and at most the claimed basename: `paste not ready`, `paste empty`, `paste busy`, `paste blocked {kind}`, `paste saved {name}`, `paste register failed, kept {name}`, `paste failed {code}` where `{code}` is the Node error code or `unknown`. No paste line holds the inbox folder, a full path or the staging name. This holds through the helpers a paste calls, not only the lines in its own body: `claimInboxName` logs full paths today (`capture-picker.ts:446`, `:450`), `removeStaging` swallows its unlink failure (`:175`) and `finalizeCapturedPng` has its own log sink (`capture-register.ts:186`). So `publishStaged`'s `logPaths: false` reaches both helpers through a new trailing optional parameter with a default that keeps today's bytes. `claimInboxName(inbox, stagingPath, logPaths = true)` logs `could not claim a name ({code})` and `could not claim a name after {limit} tries` when false. `finalizeCapturedPng(…, onRegisterFailure?, logFailure = true)` skips its own `register failed: {message}` line when false, and the paste's `onRegisterFailure` logs `paste register failed, kept {name}` instead. Every existing caller passes neither, so its lines stay byte for byte. AC-132.10 and .11 run the real helpers with a recording log, not mocks of them. A thrown settings read keeps `fetchCaptureRuntime`'s existing `[Capture] settings poll failed: {message}` line (`capture-runtime.ts:80`), whose message comes from a request to the local API, not from a file. The hotkey's path-bearing lines are unchanged and pre-existing (D-557). |
| `PASTE_MESSAGES` | The toast after a paste is a one-item `BulkResult`: `saved` registered reads `Pasted as {name}.`; `saved` not registered reads `Pasted as {name}, but the library did not record it.`; `empty` reads `Nothing to paste: the clipboard holds no image.`; `blocked` black reads `The pasted image is entirely black, so nothing was saved.`; `blocked` empty reads `The pasted image has no pixels, so nothing was saved.`; `not-ready` reads `The inbox isn't ready yet, so nothing was saved. Try again in a moment.`; `failed`, and an IPC rejection, read `The pasted image could not be saved to the inbox.`; `busy` shows nothing. `{name}` goes through `IMPORT_NAME`. |
| `IMPORT_TOAST` | One `BulkResultToast` (`components/queue/BulkResultToast.tsx`) below `capture-header`, fed by all three entries. A new run replaces the note, Dismiss clears it, and it has no timer. It is separate from the status line, which keeps its own uses (D-516). |
| `SELECTION_EFFECTS` | An import changes the list only. The effects that read the list or the selection are: the auto-select effect (`CapturePage.tsx:461-469`), which selects `sortFilmstrip(items)[0]` only while `selectedId === null`, so an empty inbox selects its first import and nothing else changes the selection; the RANGE effect (`:472-476`), which keeps range ids that still exist; the status-line notice, which shows only while `notice.shotId === selectedId` (`:1878`); the crop's cancel on a shot change, which the gate makes unreachable; and the view and image fetch effect (`:490`), which reruns only on a selection change. None of the explicit `setSelectedId` calls (`:752`, `:945`, `:1702`, `:1729`, `:1743`, `:1758`) runs on an import. |
| `ACTIONS_INDEX` | `docs/build-plan/gui-actions-index.md` gains three capture rows straight after `capture:region` (`:70`), in this order: `` | `capture:import` | Import image… button | no | IPC `showFilesDialog` then `POST /captures` (mode import) per file | specified | 09 | ``, `` | `capture:drop` | Drop image files on the Capture page | no | preload `getPathForFile` then `POST /captures` (mode import) per file | specified | 09 | `` and `` | `capture:paste` | Ctrl+V with an image on the clipboard (Capture page, outside text fields) | no | IPC `pasteCaptureImage` | specified | 09 | ``. The paste row's cell is exactly `` IPC `pasteCaptureImage` `` so that AC-88.11's `preloadChannelFor` (`gui-actions-audit.test.ts:265-272`) resolves it, which needs preload's `pasteCaptureImage: () => ipcRenderer.invoke('capture-paste-image'),` on one line. `gui-actions-audit.test.ts` gains a `describe('MEU-132 gui-actions audit')` at its end; `CAPTURE_AUDIT_TESTIDS` (`:65-69`) and `resolveIpcChannel` (`:71`, which AC-23.20 applies to settings rows only) don't change, so AC-23.19 and AC-23.20 keep their own titles and inputs. |
| `IMPORT_ELECTRON` | The new `ui/tests/e2e/capture-import.test.ts` (LF) starts a stub backend copied from `capture-picker.test.ts`'s `startBackend` (`:49`) that answers `POST /captures` `mode: "import"` with 201 `{item}` and `mode: "register"` as that file does, recording every body. Its PNGs come from main (`nativeImage.createFromBitmap(…).toPNG()` through `app.evaluate`), written under the test's temp root; `notes.txt` is text. The drop test sets the three files on a hidden `<input type=file>` with `setInputFiles`, moves them into a `DataTransfer` and dispatches `dragover` and `drop` on `capture-page`. The paste test runs under D-560 and is set out in AC-132.23. Each test asserts the toast before it reads the recorded bodies. |
| `LOOK_LAUNCH` | Under D-561 A. `look-seed.py` builds `C:/Temp/av-kit/s61/look/app-data` through `build_services`, `create_app` and a `TestClient`: a `PUT /api/v1/settings/capture` with `inbox_dir` `C:/Temp/av-kit/s61/look/inbox`, one Pillow shot registered through `GET /captures`, and the drop folder. The app starts detached with `AVKIT_APP_DATA` pointing there, and `dev-app-procs.py` records and later stops only its own processes. Each paste reads the seeded inbox from the backend, and a failed read answers `not-ready` and writes nothing (`PASTE_IPC`, `PASTE_MAIN`), so the look's paste can't land in `<HOME>/Pictures/av-kit`. Main's existing read-only watcher on that default, until its first settings answer, is pre-existing and writes nothing. |
| `NO_RAW_CONSOLE` | The renderer adds no log line: an import failure's reason goes to the toast only, and the toast names no path. Main's new lines are `PASTE_LOG`'s. |

### The renderer (D-551 to D-555, D-558)

`capture-import.ts` is pure, with no React or DOM imports apart from the `EventTarget` type `isEditableTarget` reads. It exports `IMPORT_EXTENSIONS`, `isImportableName`, `importDisplayName`, `importFiles`, `ImportEntry`, `ImportPort`, `isEditableTarget`, `pasteToastResult` and the reason constants. `runBulk` (`lib/queue/run-bulk.ts`) isn't reused: its ids would be paths, its message format joins ids, and it runs requests in parallel where 09 says one by one (D-553).

`CapturePage` gains `importNote: BulkResult | null`, `importing: boolean` (held in state and in a ref so the listener reads the current value) and the three handlers. The paste listener reads `cropRef`, a `confirmRef` and the `importing` ref, so it is added once per mount and never sees a stale gate.

### The main process (D-556, D-557)

- **Callers of the publication path (S55 RULE-1).** `publishStagedCapture`'s one caller is `captureRegionFromGui` (`capture-picker.ts:575`), which `index.ts` calls three times: the `capture-region` IPC dep (`:423`), the F2 hotkey and tray (`fireRegion`, `:530`) and the agent's interactive request loop (`:602`). `finalizeCapturedPng`'s one caller is `publishStagedCapture` (`:505`). Their tests: `ui/tests/unit/capture-picker.test.ts`, `capture-main.behavior.test.ts`, `capture-lifecycle.test.ts` and `capture-interactive.test.ts` (both import `capture-register`), and the Electron `ui/tests/e2e/capture-picker.test.ts`. Row 1 greps every caller again and lists any other.
- **Callers of the preload API and IPC lists.** `API_KEYS` (`preload.ts:3`) and `RENDERER_TO_MAIN_CHANNELS` (`ipc.ts:19`) are pinned by count and order in `clipboard-image-main.test.ts:101`, `ipc-strict-census.test.ts:56`, `login-item-ipc.test.ts:50-51` and `mcp-prompt-ipc.test.ts:71`, and listed in `ui/tests/unit/ipc-channels.ts`. Row 1 greps every test that states either list's length or last entry (S59 RULE-1).
- **`RESERVED_CHORDS`.** Unchanged. Its tests (`shortcuts.test.ts` and the registry tests that assert a reserved chord throws) run in row 5 as guards.
- **The toolbar records.** No `TOOLBAR_BUTTONS`, `ACTION_BUTTONS` or `CROP_BUTTONS` entry is added: the button is a header `Button` like `capture-region`, so AC-80.8's set doesn't move.

### Pins that move

| Pin | Where | From → to | Row |
|---|---|---|---|
| Channel count | `ui/tests/unit/clipboard-image-main.test.ts:101` | 21 → 22, last `capture-paste-image` | 1 |
| Strict census | `ui/tests/unit/ipc-strict-census.test.ts:56`, with `VALID_PAYLOAD` `{}` and `TYPE_FAIL` `{extra: true}` for the new channel | 21 → 22 | 1 |
| Channel list | `ui/tests/unit/login-item-ipc.test.ts:50-51` | 21 → 22 | 1 |
| Channel list | `ui/tests/unit/mcp-prompt-ipc.test.ts:71` | 21 → 22 | 1 |
| Shared list | `ui/tests/unit/ipc-channels.ts` | gains `capture-paste-image` last | 1 |
| Audit | `ui/tests/unit/gui-actions-audit.test.ts`, at the end | a `MEU-132 gui-actions audit` describe (`ACTIONS_INDEX`); nothing above it changes | 4 |
| Test ids | `ui/tests/e2e/test-ids.ts`, at the end | a `// MEU-132 Capture image import (additive IDs).` block with `CAPTURE_IMPORT = 'capture-import'` | 4 |

The IPC pins move in row 1, because row 1 adds the channel, and the old pins would fail on that row's own check. Row 1 greps the neighbours of each pin again (S59 RULE-1): every literal channel count, every `API_KEYS` length or last-key assertion and every test that walks `RENDERER_TO_MAIN_CHANNELS`. The header pins AC-81.10 (`capture-action-row.test.ts:673`) and AC-81.11 (`capture-inbox.test.ts:1930`, "nothing below it moves") don't move: they run unchanged in rows 1 and 5 as guards on the header the new button joins. If either fails, S12 applies.

### Where values go (Session 50 RULE-1, Session 53 RULE-1)

- **A dropped or chosen path** goes into the POST body and nowhere else in the renderer. It is never logged or shown.
- **A file's name** goes to the toast through `IMPORT_NAME`.
- **The server's error message** goes to the toast. MEU-129's import messages are fixed texts that name no path (`name-probe.txt`: `no file at that path`, `path must be absolute`).
- **Any other error** becomes `the import could not be completed`, so a message that might carry a path never reaches the toast.
- **A pasted image** goes from the clipboard to a staging file in the inbox, then to `{ts}.png`. Its name goes to the toast and to the `paste saved` line; no other path is printed (`PASTE_LOG`).
- **Main's failures** in a paste are mapped to a code. A Node error's message, which carries the path, is never logged or returned.

### Spec text (D3)

| File | Lines at `55d1289` | Change |
|---|---|---|
| `docs/build-plan/09-screenshot-capture.md` | after `:1102` (the Tests row) | A Delivered note naming the mechanism ids, the ACs, the toast (D-554), the paste gate (D-550, D-555), the extension filter (D-558) and this plan folder, in the format of Session 60's note (`:1081-1088`) |
| `docs/build-plan/gui-actions-index.md` | after `capture:region` (`:70`) | The three `ACTIONS_INDEX` rows, written in row 5, because they are AC-132.20's Green |

Rows 5 and 7 re-read each anchor before they write (Session 51 RULE-3) and cite the lines as they read then. `09` and `gui-actions-index.md` are CRLF. The index's other readers, `capture-page.test.ts:342` (`capture:open_folder` is palette yes) and AC-71.14, AC-93.5 and AC-96.11's "directly after" checks, name rows this insert doesn't touch; they run in row 5.

### MEU-132 `gui-capture-image-import`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Drop and dialog entries → import body | `capture-import.ts` `importFiles`, `capture-commands.ts` `importCapture` | `IMPORT_TYPES`; an empty path isn't sent | The body is exactly `{mode, path}`; the server's `CaptureCreateIn` is `extra="forbid"` |
| `capture-paste-image` | `ipc.ts` `noPayloadSchema` | no payload | Any payload is refused (`ipc-strict-census`) |
| Paste outcome → renderer | `capture-picker.ts` `PasteOutcome` | six kinds (`saved`, `blocked`, `empty`, `busy`, `not-ready`, `failed`); `name` is a basename | Unread keys are ignored |
| 201 body → renderer | `capture-commands.ts` | MEU-129's `{item}`; the renderer reads nothing from it but the refetch | — |

#### Acceptance Criteria

Vitest titles start `AC-132.<n>`. AC-132.1 to .5 go in the new `ui/tests/unit/capture-import.test.ts` (LF). AC-132.6 to .12 go in the new `ui/tests/unit/capture-paste-main.test.ts` (LF), which uses `helpers/electron-stub.ts`'s `nativeImage` factory and a temp inbox. AC-132.13 to .20 go in the new `ui/tests/unit/capture-import.behavior.test.ts` (LF), whose harness is copied from `capture-crop-tool.behavior.test.ts:1-222` with fakes for `showFilesDialog`, `getPathForFile` and `pasteCaptureImage` and a stubbed `fetch` that records each request; no image leaves the test. AC-132.20's audit cases go in `gui-actions-audit.test.ts`. AC-132.21 is a Python test. AC-132.22 and .23 go in `ui/tests/e2e/capture-import.test.ts`.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-132.1 | unit | `IMPORT_TYPES`: `IMPORT_EXTENSIONS` is png, jpg, jpeg, webp in order; `isImportableName` is true for `a.png`, `A.PNG`, `b.Jpeg`, `c.webp`, `d.e.jpg` and false for `notes.txt`, `a.png.txt`, `.png`, `png`, `a.` and `a.gif` | Local Canon: 09 Button, Drop; D-558 | Yes: Red, the stub returns true |
| AC-132.2 | unit | `IMPORT_NAME`: `C:\x\y\shot.png` and `/x/shot.png` give `shot.png`; a name with U+0007 and one with a lone U+D800 each come back with U+FFFD in its place and no other change; an empty name and `C:\x\` give `(unnamed file)`; a name with no separator is unchanged (S53 RULE-1) | Inferred: S50 RULE-1, S53 RULE-1 | Yes: Red, the stub returns its input |
| AC-132.3 | unit | `IMPORT_RUN` fan-out with a fake port (S55 RULE-3): entries `a.png`, `notes.txt`, `b.jpg` make exactly two `importOne` calls, `a.png`'s path then `b.jpg`'s, the second only after the first resolves, then one `refetch`; the message is exactly `Imported 2 of 3. 1 failed: notes.txt - not an image av-kit can open (png, jpg, jpeg, webp)`; two images give `Imported 2 of 2.` | Local Canon: 09 Drop | Yes: Red, the stub makes no call |
| AC-132.4 | unit | `IMPORT_RUN` errors: an `ApiError(422, 'InboxPathError', 'no file at that path')` gives that reason; each of `ApiError(503, 'FETCH_FAILED', 'EACCES C:\secret\a.png')`, `ApiError(503, 'BACKEND_NOT_READY', 'Backend not ready — C:\secret\a.png')`, `ApiError(422, 'HTTP_ERROR', 'C:\secret\a.png')`, `ApiError(422, 'validation_error', 'Request validation failed')`, `ApiError(500, 'internal_error', 'Internal server error (request id r1)')` and `Error('EACCES C:\secret\a.png')` gives `the import could not be completed`, and no message holds `C:\`; an empty path fails `not a file on disk` with no call; all entries non-images make no call and no refetch; no message holds any entry's path | Inferred: S50 RULE-1 | Yes: Red, the stub |
| AC-132.5 | unit | `isEditableTarget`: true for a textarea, a text, search and number input, an input with no type and a contenteditable div; false for a button, a checkbox input, the body, `null` and `window` | Local Canon: 09 Paste | Yes: Red, the stub returns false |
| AC-132.6 | unit | `PASTE_MAIN` saved, through the real resolver: `resolveInboxDir` is `() => resolvePasteInbox(read)`, where the fake settings `read` answers `{inbox_dir: A}` and A is a temp inbox distinct from a second temp path standing in for the default. With a 4×3 non-black PNG read, the call answers `{kind: 'saved', name, registered: true}` with `name` matching `^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.png$`; A's file bytes equal the read bytes; one register body `{mode: 'register', source: 'gui', path}` names that file in A; the stand-in default path still doesn't exist; inbox-changed is sent; no staging file is left; `notifyUser` and `clipboard.writeImage` are not called. Then `read` switches to answer a second temp inbox B, as a Save in Settings does, with no other call between, and a second paste is saved in B, its register body names the B file, and A still holds exactly one PNG (plan review round 2, F2). `read` is called once per paste | Local Canon: 09 Paste; D-556 | Yes: Red, the stub answers `failed` |
| AC-132.7 | unit | `PASTE_MAIN` not-ready, empty and busy: a `resolveInboxDir` that answers `null`, and one that rejects, each give `{kind: 'not-ready'}`, never call `readClipboardPng` and create nothing (round-1 F2); through `resolvePasteInbox`, after a paste saved in A and `read` switched to B, a `read` that answers `null` and one that rejects each give `not-ready`, and nothing new appears in A or B (round-2 F2); a `null` read answers `empty` and writes nothing; a second call while the first awaits its register answers `busy` and writes nothing; after the first settles, a third call runs | Inferred: D-556 | Yes: Red, the stub |
| AC-132.8 | unit | `PASTE_MAIN` blocked: an all-black PNG answers `{kind: 'blocked', reason: 'black'}` and a zero-pixel image `{kind: 'blocked', reason: 'empty'}`; neither leaves a file in the inbox or calls `notifyUser` | Local Canon: §Result publication; D-556 | Yes: Red, the stub |
| AC-132.9 | unit | Exclusive staging (S58 RULE-1): with `nextStagingName` forced to a name whose temp another writer holds with bytes `OTHER`, the paste draws a new name and that file still holds `OTHER` afterwards; with the clock fixed (`vi.setSystemTime`) and `{ts}.png` already in the inbox, the paste saves `{ts}_2.png` and the first file is unchanged | Local Canon: S58 RULE-1; `claimInboxName` | Yes: Red, the stub |
| AC-132.10 | unit | Failure mapping (S58 RULE-2): the inbox path is a file; `openSync` throws `EACCES`; `writeSync` throws; the claim's `linkSync` throws `EACCES`; each answers `{kind: 'failed'}`, never rejects, and leaves no staging file it made; each case also asserts its injected call was reached, so a stub that answers `failed` early can't pass it | Local Canon: S58 RULE-2 | Yes: Red, the row 1 stub answers `failed` without reaching the injected call |
| AC-132.11 | unit | `PASTE_LOG`: across AC-132.6 to .10's cases the logged lines hold neither the inbox folder nor a full destination path nor a staging name; a register failure answers `registered: false` and logs `paste register failed, kept {name}` with the basename only and no `register failed:` line; AC-132.10's claim failure logs `could not claim a name (EACCES)` with no path; the log comes from the real `claimInboxName` and `finalizeCapturedPng`, not mocks of them; `publishStagedCapture`'s hotkey lines are unchanged (its existing tests and `capture-main.behavior.test.ts` pass as guards) | Inferred: S50 RULE-1; D-557 | Yes: Red, the stub logs the path |
| AC-132.12 | unit | `PASTE_IPC`: `capture-paste-image` is the last channel; `{}` passes, `{extra: true}` and a non-object are refused; the handler calls the dep once and returns its outcome; with no dep it answers `{kind: 'failed'}`; preload's `pasteCaptureImage` is the last `API_KEYS` entry and invokes that channel | Local Canon: IPC strict census | Yes: Red, the row 1 handler answers `failed` with a dep present |
| AC-132.13 | unit (page) | `IMPORT_BUTTON`: `capture-import` sits straight after `capture-region` in `capture-header`, reads `Import image…`, holds an `ImagePlus` svg and has the title above; a click calls `showFilesDialog` once with `[{name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'webp']}]`; a two-path result sends two `POST /api/v1/captures` with `{mode: 'import', path}` in order, then one list refetch; an empty result sends nothing and shows no toast | Local Canon: 09 Button; D-552 | Yes: Red, the stub button calls nothing |
| AC-132.14 | unit (page) | `IMPORT_DROP`: a `drop` with three files on `capture-page` sends two import POSTs, in order, with the paths `getPathForFile` gave; `dragover` and `drop` with `Files` are `defaultPrevented`, also while gated; a drag with only `text/plain` isn't; a file whose `getPathForFile` is empty is named `not a file on disk` and not sent | Local Canon: 09 Drop; D-551 | Yes: Red, nothing is sent |
| AC-132.15 | unit (page) | `IMPORT_TOAST`: the drop's toast reads `Imported 2 of 3. 1 failed: notes.txt - not an image av-kit can open (png, jpg, jpeg, webp)`; a 422 envelope `{error: {code: 'InboxPathError', message: 'no file at that path'}}` names the file with that text; through the real `importCapture` and `apiFetch`, a stubbed `fetch` that rejects with `TypeError('Failed to fetch C:\secret\red.png')` gives `the import could not be completed` and the toast holds no `C:\` (round-1 F1); a second run replaces the toast; Dismiss removes it; no toast text holds a path | Local Canon: 09 Drop; D-554 | Yes: Red, no toast |
| AC-132.16 | unit (page) | `PASTE_KEY`: a paste event on the body, on a button after a pointer click and on a button reached with Tab after Enter activated it (S60 RULE-1) each call `pasteCaptureImage` once and are `defaultPrevented`; a paste on `capture-inbox-path`, a textarea and a contenteditable calls nothing and isn't prevented; after unmount a paste calls nothing | Local Canon: 09 Paste; D-550 | Yes: Red, no call |
| AC-132.17 | unit (page) | `PASTE_MESSAGES`: each outcome kind shows its text exactly; `busy` shows no toast; a rejected IPC shows the `failed` text; `saved` refetches the list and the others don't | Inferred: D-556 | Yes: Red, no toast |
| AC-132.18 | unit (page) | `IMPORT_GATE`: with the crop open, the button is disabled with `Finish or cancel the crop first`, and a drop and a paste call nothing; with a delete confirm open, a drop and a paste call nothing; while an import runs, the button has `aria-busy="true"` and a second drop sends nothing; with unsaved marks, a drop imports and the marks are still there | Inferred: D-555 | Yes: Red, the gate lets the paste through |
| AC-132.19 | unit (page) | `SELECTION_EFFECTS`: on an empty inbox, a drop's first import becomes selected after the refetch; with a shot selected, unsaved marks, a range and a notice, an import leaves `selectedId`, the marks, the range and the notice as they were | Local Canon: `CapturePage.tsx:461-476`, `:1878` | Yes: Red, the stub drop sends nothing, so the empty inbox stays empty |
| AC-132.20 | unit | `ACTIONS_INDEX`: each of the three rows appears once, in order, straight after `capture:region`, with palette `no`; `capture:paste`'s cell resolves through `preloadChannelFor` to `capture-paste-image`, which `listRegisteredChannels()` holds; `capture:import`'s cell names `showFilesDialog` and `POST /captures`, and `RENDERER_TO_MAIN_CHANNELS` holds `show-files-dialog`; `capture:drop`'s names `getPathForFile`, which preload exposes; `openapi.committed.json` holds `"/api/v1/captures"`; `capture-import` is in `test-ids.ts` and in production source | Local Canon: gui-actions-index, AC-88.11's resolver; D-562 | Yes: Red, the rows are absent until row 5 |
| AC-132.21 | e2e (Python) | Real stack, `tests/e2e/test_api_capture_import_names.py`, building Pillow images under a temp root: an import of a file named with a lone surrogate answers 201 and stores `snip_x.png` (MEU-129's name rule); a path with U+0007 answers 422 `no file at that path`; an empty path answers 422 `path must be absolute`; neither 422 body nor the captured log holds the outside folder, and a positive control asserts the folder text is findable in a body built to hold it | Local Canon: MEU-129; S53 RULE-1 | Characterisation guard: passes on `55d1289` (`name-probe.txt`), not `--require`d |
| AC-132.22 | e2e (Electron) | `IMPORT_ELECTRON` drop: `red.png`, `notes.txt` and `green.png` dropped on `capture-page` give the toast `Imported 2 of 3. 1 failed: notes.txt - not an image av-kit can open (png, jpg, jpeg, webp)`, then exactly two recorded import bodies, `red.png`'s full path then `green.png`'s | Local Canon: 09 Tests | Yes: Red, no toast |
| AC-132.23 | e2e (Electron) | `IMPORT_ELECTRON` paste, under D-560: a click on `capture-import` (the E2E dialog answers `C:/e2e/sample.mp4`, `ui/src/main/index.ts:360`) shows the not-an-image toast; with a test PNG on the clipboard, Ctrl+V gives the toast `Pasted as …`, a new file in the stub's configured inbox (its `/settings/capture` `inbox_dir` under the test root, never the default) matching `^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}(_\d+)?\.png$` and one register body `{mode: 'register', source: 'gui', path}` naming it; focus reaches `capture-import` by Tab and Enter activates it (the E2E dialog answers at once, so the not-an-image toast shows again); the stub's `setInbox` then switches its `inbox_dir` to a second folder under the test root, and with no wait for main's poll Ctrl+V pastes a second file into that folder, its register body names it, the first folder still holds one PNG (round-2 F2), and its toast replaces the previous one; Ctrl+V in `capture-inbox-path` adds no file; under A the saved clipboard is restored and read back equal in `finally` | Local Canon: 09 Tests, Paste; S60 RULE-1 | Yes: Red, no toast after Ctrl+V |

Guards that run unchanged in rows 3 and 5: the whole of `capture-picker.test.ts` (unit and Electron), `capture-main.behavior.test.ts`, `capture-lifecycle.test.ts`, `capture-interactive.test.ts`, AC-81.10, AC-81.11, AC-80.x, AC-23.20, AC-131.x, AC-51.6, AC-81.13, the `RESERVED_CHORDS` tests and the rest of `capture-page.behavior.test.ts` and `capture-inbox.test.ts`.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Drop route to a path | Local Canon, probed | 09 Drop; D-551 (`paste-drop-probe.txt` P2) |
| One by one, error toast | Local Canon | 09 Drop; D-553, D-554 |
| What counts as an image | Inferred | D-558 |
| Button and dialog | Local Canon | 09 Button; D-552 |
| Paste capture with Ctrl+V reserved | Inferred, probed | D-550 (`paste-drop-probe.txt` P1) |
| Paste publication | Local Canon | 09 Paste, §Result publication; D-556 |
| Paste logs | Inferred | D-557 |
| Crop, confirm, unsaved marks | Inferred | D-555 |
| Actions index | Local Canon | D-562 |
| Help text | Inferred | D-563 |
| Electron proof by stub backend | Local Canon | D-564 |
| The clipboard in the proof | Human | D-560 |
| Human look | Human | D-561 |
| Shared status files | Inferred | D-565 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-import.ts` | New | `IMPORT_TYPES`, `IMPORT_NAME`, `IMPORT_RUN`, `isEditableTarget`, `pasteToastResult` |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | Modify | `importCapture` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | Modify | The button, drop, paste listener, gate and toast |
| `ui/src/renderer/src/env.d.ts` | Modify | `pasteCaptureImage` and `PasteOutcome` |
| `ui/src/main/capture-picker.ts` | Modify | `PASTE_PUBLISH`, `PASTE_MAIN`, `PASTE_LOG` |
| `ui/src/main/ipc.ts`, `ui/src/main/preload.ts`, `ui/src/main/index.ts` | Modify | `PASTE_IPC` |
| `ui/tests/unit/capture-import.test.ts` | New | AC-132.1 to .5 |
| `ui/tests/unit/capture-paste-main.test.ts` | New | AC-132.6 to .12 |
| `ui/tests/unit/capture-import.behavior.test.ts` | New | AC-132.13 to .19 |
| `ui/tests/unit/gui-actions-audit.test.ts` | Modify | AC-132.20 |
| `ui/tests/unit/clipboard-image-main.test.ts`, `ipc-strict-census.test.ts`, `login-item-ipc.test.ts`, `mcp-prompt-ipc.test.ts`, `ipc-channels.ts` | Modify | §Pins that move |
| `tests/e2e/test_api_capture_import_names.py` | New | AC-132.21 |
| `ui/tests/e2e/capture-import.test.ts` | New | AC-132.22, .23 |
| `ui/tests/e2e/test-ids.ts` | Modify | The additive block |
| `docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/gui-actions-index.md` | Modify | §Spec text |

Line endings at `55d1289` (`C:/Temp/av-kit/s61-plan-probes.txt`): CRLF are `CapturePage.tsx`, `capture-commands.ts`, `ipc.ts`, `preload.ts`, `index.ts`, `env.d.ts`, `test-ids.ts`, `ipc-channels.ts`, `clipboard-image-main.test.ts`, `ipc-strict-census.test.ts`, `login-item-ipc.test.ts`, `mcp-prompt-ipc.test.ts`, `gui-actions-audit.test.ts`, `gui-actions-index.md`, `09` and the grouping. LF are `capture-picker.ts`, `helpers/electron-stub.ts` (read only), the Electron `capture-picker.test.ts` and `capture-inbox.test.ts` (read only), `meu-status.yaml`, `docs/BUILD_PLAN.md` and `meu-registry.md`. Row 0 measures every file again with Python bytes, and every row writes with `newline=""` or by byte replacement. New files are LF.

### Project files

- `docs/execution/plans/2026-11-10-gui-capture-image-import/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `row3-ui-src.json`, `red-check.py`, `identity.py`, `session-gate.ps1`, `hotkey-free.py`, `dev-app-procs.py`, `look-seed.py`, `look-launch.ps1`, `look-check.py`, `human-check.md`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, and the grouping tracker row (`:111`), under D-565.
- `.agent/context/handoffs/2026-11-10-gui-capture-image-import-*.md`, `docs/execution/reflections/2026-11-10-gui-capture-image-import-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

Not this session's, and left out of its commit unless Mat says otherwise: `docs/proposals/2026-11-10-download-logic-divergence-report.md` (never opened), `.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md`, and the other session's edits in `known-issues.md`, `known-issues.yaml`, `triage-output.yaml` and build-plan `02`, `03`, `06-gui` and `build-priority-matrix.md`. They are named to Mat before any commit.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A palette command for import or paste | Shortcut | None | D-562 |
| A help-sheet sentence for import | Docs | MEU-105 (it rewrites the capture help) | D-563 |
| A drop highlight on the page | UI | None unless Mat rules it under D-561 | D-563 |
| A dropped folder, a URL or a browser image with no file | Feature | None | `getPathForFile` gives `""`; the toast says `not a file on disk` |
| Paste of a file list copied in Explorer | Feature | None | `clipboard.readImage()` is empty for it; the toast says `Nothing to paste` |
| Paste into a text field importing too | Behaviour | None | 09 Paste |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` | Bug | Its own session | D-507; recorded if seen, never fixed here |
| `CAPTURE-EXIF-SCANNED-ORIENTATION` | Bug | Its own session | Recorded if seen, never fixed here |
| `MCP-AUDIT-BASELINE-PENDING-CROP` | Audit | The next authoritative update | D-499 |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | MCP | Its own session | No MCP change here |
| The hotkey's own path-bearing log and notification lines | Logs | None | Pre-existing; D-557 |

## BUILD_PLAN.md Audit

MEU-132 is in `.agent/context/meu-status.yaml` (`:3453`, phase 9, band P2, matrix item 9.39, anchor `gui-image-import`, `pending`). Row 7 sets it `ready_for_review` with `tools/meu_status.py update` under D-565, and H2-2 sets `approved`. The render check runs at rows 7 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s61-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s61-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` does the following:

1. Checks that D-560 and D-561 carry Mat's ruling in §Decision Log (S14). **The ruling format:** once Mat rules, the entry's `chosen` starts with the option letter, as `"A: …"`, `"B: …"` or `"C: …"`, and its `human_message_reference` becomes `"USER_EXPLICIT <date> '<Mat's words>'"`. A `chosen` that starts `Pending Mat's ruling`, or a `null` reference, is unruled. `look-check.py` `ruling()` reads this, and `baseline.ps1` uses the same rule. Checks the queue: MEU-131 is `approved` in `meu-status.yaml`, and no path of Session 60's Files Modified is dirty.
2. Checks the shapes this plan relies on, by name: the import mode in `packages/api/src/avkit_api/routes/captures.py` and its schema, `getPathForFile` in `preload.ts`, `'show-files-dialog'` in `ipc.ts`, `publishStagedCapture`, `claimInboxName` and `PICKER_STAGING_PREFIX` in `capture-picker.ts`, `finalizeCapturedPng` in `capture-register.ts`, `'Ctrl+V'` in `RESERVED_CHORDS` and `BulkResultToast`; and that `capture-paste-image`, `pasteCaptureImage`, `pasteClipboardImage`, `importCapture`, `capture-import.ts` and `capture-import` (page, test ids) are absent. The anchors step also stops when a new file of §Files Modified already exists.
3. Creates `C:\Temp\av-kit\s61\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256; the other session's proposal is hashed by `Get-FileHash` and never opened.
4. Runs `uv sync --frozen --offline --all-packages`, and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair is over 1024 B and that Pillow is 13.0.0 (S4).
5. Records the line endings and SHA-256 of every file in §Files Modified to `s61-anchors.txt`, which row 1 reads before it writes.
6. Runs `hotkey-free.py`: F2 through `user32.RegisterHotKey`, released at once, the holder's error (1409) named when taken; any Electron process whose path is under `P:/av-kit/ui` (Session 57 RULE-4); and, new here, whether the clipboard can be opened (`OpenClipboard(NULL)`, then `CloseClipboard` at once, up to five tries 100 ms apart because any copy holds it for a moment), with the window class and process id of `GetOpenClipboardWindow` named when every try fails. `GetClipboardOwner` isn't used: it names whoever last put data on the clipboard, not who holds it open. It reads no clipboard data and empties nothing. The backend binds port 0, so no port is checked. It is fail-fast: any of the three is S6. At plan time all three were free (`C:/Temp/av-kit/s61/probe/hotkey-free.txt` for F2 and the process list; the clipboard check's selftest and live run are in `s61-plan-hotkey-*`).
7. Captures the base Python suite to `s61-base-py.txt`, the base UI suite to `s61-base-ui.txt`, the base MCP suite to `s61-base-mcp.txt`, and the base Electron runs of `capture-picker.test.ts` and `capture-inbox.test.ts` after a build to `s61-base-e2e.txt`. The suites' own failures are recorded, not fatal; a failing renderer build stops the row.
8. Runs the `red-check.py`, `identity.py`, `dev-app-procs.py`, `hotkey-free.py` and `look-check.py` selftests.

The scripts are copies of Session 60's, with this plan's values:

- **`red-check.py`.** `DECLARED_NEW` holds `IMPORT_EXTENSIONS`, `isImportableName`, `importDisplayName`, `importFiles`, `ImportEntry`, `ImportPort`, `isEditableTarget`, `pasteToastResult`, `importCapture`, `pasteCaptureImage`, `pasteClipboardImage`, `PasteOutcome` and `PublishOutcome`, and keeps the selftest fixtures' names. These excuse a non-required block only: no required Red reaches them by name. `LOCATOR_DETAIL` is read as the detail line of a `toBeVisible()` assertion just before it, never as a setup failure on its own.
- **`identity.py`.** `PLAN` is this folder. Its selftest binds `session-gate.ps1`, `dev-app-procs.py`, the look scripts, the new test modules, `test-ids.ts`, `09`, `gui-actions-index.md`, the register's renders and the grouping.
- **`PROJECT_ARTIFACTS`.** This plan's `*.md` (including `human-check.md`), the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`.

### 2. Type-only first, then Red, then Green (rows 1 to 5)

- **Row 1 adds the shared names with no behaviour (Session 53 RULE-2).** `capture-import.ts` with every export: `IMPORT_EXTENSIONS` empty, `isImportableName` true, `importDisplayName` returning its input, `importFiles` returning an empty result with no call, `isEditableTarget` false, `pasteToastResult` returning `null`; `importCapture` throwing `not implemented`; the `capture-paste-image` channel, schema, census entry and a handler that answers `{kind: 'failed'}` whether or not a dep is present; preload's `pasteCaptureImage` and its `env.d.ts` type; `PasteOutcome` and a `pasteClipboardImage` that answers `{kind: 'failed'}`; the `index.ts` dep wired to it; an Import button that does nothing; and the IPC pins in §Pins that move. `publishStagedCapture` isn't touched in row 1. Its check runs `npm --prefix ui run typecheck`, `lint`, the four IPC pin tests, `ipc-channels.ts`'s users, `capture-action-row.test.ts`, `capture-page.test.ts` and `capture-page.behavior.test.ts`.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` refuses a collection error, a launch failure, a test or action timeout, and a required test that fails on a missing name.
- **Why each Red fails by assertion.** The module Reds call the row 1 stubs, whose values are wrong. The main Reds call a `pasteClipboardImage` that answers `failed`, so each `kind` assertion fails on its value. The page Reds find a button, a section and a window with no handlers, so the calls, POSTs and toasts they wait for are absent. The Electron Reds drop or paste, then `await expect(toast).toBeVisible()` before reading anything else; Playwright reports that as `Error: expect(locator).toBeVisible() failed`, which `red-check.py` reads as an assertion. The paste Red runs D-560's save and restore around it, so a Red leaves Mat's clipboard as it was.
- **`--require` matches a test name up to a non-digit boundary.** Row 2: `AC-132.1` to `.12`. Row 4: `AC-132.13` to `.20`, `.22` and `.23`, across the Vitest and the Playwright receipts. AC-132.21 is a characterisation guard and must pass in row 4.
- **Expectations stay immutable in Green.** No test file changes in rows 3 and 5.
- **Electron.** Rows 4 and 5 build the renderer and run Playwright with `ELECTRON_RUN_AS_NODE` cleared, after `hotkey-free.py`. Row 4 runs only `capture-import.test.ts`; row 5 runs it with `capture-picker.test.ts` and `capture-inbox.test.ts`.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`: §1.
- `session-gate.ps1` (H1-2): below.
- `hotkey-free.py` (rows 0, 4, 5 and H1-2): §1 item 6. `--selftest` checks the error-code reading, the path filter and the clipboard result reading with fixtures, without registering a key or opening the clipboard.
- `dev-app-procs.py` (row 6): Session 60's, with its docstring line changed. `record --root-pid --out --roles electron,backend --wait 120`, `check --record [--stop]`, `--selftest`.
- `look-seed.py`, `look-launch.ps1`, `look-check.py` (row 6): `LOOK_LAUNCH`, under D-561 A. `look-launch.ps1` refuses to start when the seed's app data is missing, clears `ELECTRON_RUN_AS_NODE`, sets `AVKIT_APP_DATA`, starts `npm --prefix ui run dev` with `Start-Process` and no wait, and runs `dev-app-procs.py record`. `look-check.py` reads D-561's `chosen` from this plan and `human-check.md`: under A it requires a `decision:` of `approve`, `no` or `do-nothing` and a `human_message_reference: USER_EXPLICIT <date> '<words>'` line, and that `dev-app-procs.py check --record` lists none of this launch's processes; under B it requires `decision: not-run` with Mat's ruling quoted. It exits 0 only then.

### Session gate (H1-2)

`session-gate.ps1` is Session 60's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s61-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `ui-types`, `ui-lint`, `py-lint` (`ruff check packages/ tests/`, because AC-132.21 adds a Python test), `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `mcp-types`, `mcp-build`, `mcp-tests`, `state-render`, `issues-render` |
| Runtime | `hotkey-free` (`hotkey-free.py`, F2, the process list and the clipboard), then `ui-electron`: `npm --prefix ui run test:e2e -- tests/e2e/capture-import.test.ts tests/e2e/capture-picker.test.ts tests/e2e/capture-inbox.test.ts` after `ui-build` |
| Skipped with reason | `py-types` (no change under `packages/`, the only tree pyright checks), `openapi` (no route or schema changes; H1-4 still checks the OpenAPI snapshot is unchanged), `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes) |

`py-tests` stays, because AC-132.21 adds a Python test. It excuses only ids that row 0's receipt shows failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`; a path outside `baseline-dirty.txt` and this plan appears; or, before rows 7 and H1-2, a `baseline-dirty.txt` path differs from its recorded SHA-256 | Stop and tell Mat; never commit, stash or revert another session's work |
| S4 | The pinned FFmpeg pair is missing or under 1024 B, or Pillow isn't 13.0.0 | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, including the live audit | Stop and tell Mat |
| S6 | F2 is taken, an Electron process from this work tree is running, or another program holds the clipboard open, at row 0, 4, 5 or H1-2; or row 6's `record` exits 1 | Stop and name the holder to Mat; free it only by a recorded process id, never by name, and never stop another program |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | At row 0, MEU-131 isn't `approved` or a Session 60 path is dirty | Stop; Session 60 closes first |
| S9 | A row must edit `ui/tests/e2e/test-ids.ts` outside the additive block | Stop; ids go in the block at the end, and AC-51.6 and AC-81.13 run in that row's own check |
| S10 | A path, a staging name or an error body reaches a log line, a notification or the toast in a way it didn't before | Fix it in the row or raise it with Mat; never record it as a residual (Session 50 RULE-1) |
| S11 | A row 0 shape check fails: the import mode, `getPathForFile`, `show-files-dialog`, the publication path or `'Ctrl+V'` in `RESERVED_CHORDS` is missing, or a new name already exists | Stop; amend this plan through the plan review before row 1 |
| S12 | A row would change 09's rule text, an AC, the import endpoint or `RESERVED_CHORDS`; or AC-81.10 or AC-81.11 fails with the button in the header | Stop; brief Mat with a recommendation and a do-nothing option (S59 RULE-3) |
| S13 | Under D-560 A, the clipboard read back after the paste proof differs from what was saved, or `availableFormats()` lost a format | Stop the Electron runs, tell Mat what was lost, and don't rerun until Mat rules |
| S14 | At row 0, D-560 or D-561 has no ruling from Mat in §Decision Log | Stop; ask Mat through the Human Decision Protocol, and run the paste proof and row 6 only as ruled |
| S15 | At row 7, `meu-status.yaml`, `meu-registry.md` or `BUILD_PLAN.md` differs from its `baseline-dirty.txt` SHA-256, or the MEU-132 write changes any line outside MEU-132's entry and rows | Stop and tell Mat (D-565) |

## Decision Log

> [!WARNING]
> Mat's request and design D-12 settle the scope, and the grouping (D-400 to D-406) placed this MEU. D-550 to D-559 and D-562 to D-565 didn't need Mat: each is autonomous, with its alternatives in `reasoning`. D-560 and D-561 are Mat's. D-536 to D-543 are claimed on `main` and in the other session's work, and D-544 to D-549 stay as headroom (`C:/Temp/av-kit/s61-plan-dids.txt`), so this block starts at D-550.
>
> Carried and not relisted in the block: every grouping §8 row, D-400 to D-406, with stage `grouping`. Of those, D-400 bears on this session, and the reflection carries all seven, since this is the grouping's last session. Session 58's MEU-129 decisions are carried as it ruled them, as are Session 60's D-515 (the crop's modal state) and D-516 (the status line). The design's own D-1 to D-13 are a separate namespace, cited as "design D-n" in prose only. The probe (`C:/Temp/av-kit/s61-decision-issue-probe.txt`), run with this plan, the handoff and the grouping as sources (Session 54 RULE-5), shows what the closeout's decision flags pull in.

```yaml
decision_log:
  - id: D-550
    stage: planning
    question: "Ctrl+V is in RESERVED_CHORDS (D-136), so no command can take it. How does the Capture page catch a paste?"
    resolution: autonomous
    class: two-way
    chosen: "PASTE_KEY: a window paste listener added by CapturePage while it is mounted; it skips editable targets and the gate, prevents the default and asks main; no registry entry, RESERVED_CHORDS unchanged"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/registry/shortcuts.ts:132-138, :173 — Ctrl+V is reserved and registering it throws"
      - "C:/Temp/av-kit/s61/probe/paste-drop-probe.txt P1 — in the built app one Ctrl+V gives exactly one window paste event with focus on the body, on a button after a click, on a button after Tab and on an input, none prevented"
      - "ui/src/renderer/src/router.tsx:57 — the Capture page is a route, so the listener exists only while it is shown"
    research:
      engine: none
      sources: []
    reasoning: "The paste event is what Chromium fires for Ctrl+V and for the context menu's Paste, so listening for it keeps the reserved chord's meaning (paste) instead of overriding a key. A keydown handler for Ctrl+V would duplicate the reservation's purpose and miss a menu paste. A registry entry would break D-136's rule that reserved chords stay native. Skipping editable targets keeps 09's 'text fields keep their native paste'. Two-way."
    human_message_reference: null
  - id: D-551
    stage: planning
    question: "How does a dropped file reach the import endpoint as a path?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_DROP: window.api.getPathForFile(file) for each dataTransfer file, in list order; an empty path is named 'not a file on disk' and not sent"
    source_tag: Local Canon
    precedents:
      - "ui/src/main/preload.ts:45 — getPathForFile returns webUtils.getPathForFile(file)"
      - "C:/Temp/av-kit/s61/probe/paste-drop-probe.txt P2 — files moved from a real-path input into a DataTransfer keep their full Windows paths inside a drop handler; a synthetic File gives an empty string"
    research:
      engine: none
      sources: []
    reasoning: "Electron removed File.path, and webUtils.getPathForFile is its replacement, already exposed by preload. Reading the bytes in the renderer and posting them would need a new upload endpoint, against the import endpoint's path contract. An empty path (a browser image, a URL) can't be imported by path, so the toast says why instead of sending a body the server refuses. Two-way."
    human_message_reference: null
  - id: D-552
    stage: planning
    question: "Where does the Import image… dialog run?"
    resolution: autonomous
    class: two-way
    chosen: "The existing show-files-dialog channel with filters [{name: 'Images', extensions: png, jpg, jpeg, webp}]; its main side already allows multi-select; no new dialog IPC"
    source_tag: Local Canon
    precedents:
      - "ui/src/main/ipc.ts:17, :365 — SHOW_FILES_PROPERTIES includes multiSelections; the handler passes the renderer's filters"
      - "ui/src/main/preload.ts:43 — showFilesDialog(filters?)"
    research:
      engine: none
      sources: []
    reasoning: "The dialog already runs in main with multi-select and filters, as 09 asks, so a new channel would duplicate it and move four IPC pins for nothing. The filter is a convenience the user can switch to All files; IMPORT_TYPES still checks each chosen file. Two-way."
    human_message_reference: null
  - id: D-553
    stage: planning
    question: "How are several files imported?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_RUN: its own sequential runner in capture-import.ts, one awaited POST per importable file, one refetch, a BulkResult keyed by display names"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1097 — imported one by one"
      - "ui/src/renderer/src/lib/queue/run-bulk.ts:18-35 — BulkFailure.id and the message are built from ids"
    research:
      engine: none
      sources: []
    reasoning: "runBulk fans out in parallel and builds its message from ids, which here would be paths, so the toast would print them (S50 RULE-1). One by one keeps the inbox's naming order equal to the drop order and makes the server's per-file errors line up with names. A single batch request would need a new endpoint. Only a 422 InboxPathError shows its own text, because apiFetch also wraps a thrown fetch or a backend-resolution failure as an ApiError whose message is the thrown text, which can hold a path (plan review round 1, F1); every other error gets the fixed fallback. Two-way."
    human_message_reference: null
  - id: D-554
    stage: planning
    question: "What is the error toast?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_TOAST: the app's BulkResultToast, below capture-header, for all three entries; separate from the status line"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/components/queue/BulkResultToast.tsx — the app's toast: role status, polite, dismissible, no timer"
      - "ui/src/renderer/src/features/converter/ConvertPage.tsx:902 — used the same way on the Convert page"
      - "docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md D-516 — the crop used the status line for one named shot"
    research:
      engine: none
      sources: []
    reasoning: "A drop of several files has several outcomes, which the one-line status line can't hold, and 09 says toast. The bulk toast already carries a partial result and is the app's only toast, so reusing it keeps one look. A paste is a one-item result through the same toast, so the three entries report in one place. The status line keeps D-516's single-shot uses. A timed toast would vanish while the user reads a list of failures. Two-way."
    human_message_reference: null
  - id: D-555
    stage: planning
    question: "What do the crop's modal state, a confirm dialog and unsaved marks do to an import or paste?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_GATE: the crop, a confirm or a running import block all three entries, the button disabled with a reason; unsaved marks don't block, because the selection doesn't change"
    source_tag: Inferred
    precedents:
      - "docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md D-515, D-518 — while the crop is open, other actions do nothing and say why"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:461-469 — the auto-select effect runs only with no selection"
    research:
      engine: none
      sources: []
    reasoning: "The crop owns the page while open (D-515), so a paste landing then would act behind a modal. A confirm dialog is modal too. Blocking on unsaved marks would stop a user from pasting a reference image while annotating, and the import never touches the selected shot or its marks, so there is nothing to lose. A running import blocks a second one so two runs can't interleave their toasts. Two-way."
    human_message_reference: null
  - id: D-556
    stage: planning
    question: "How does main publish a pasted image through the hotkey's path?"
    resolution: autonomous
    class: two-way
    chosen: "PASTE_IPC, PASTE_MAIN and PASTE_PUBLISH: a capture-paste-image channel; main writes the clipboard PNG to an exclusive staging file in the inbox and runs publishStagedCapture's body, moved into an inner publish that returns an outcome, with notify, path logs and clipboard copy off"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1100 — main writes a PNG named by its yyyy-MM-dd_HH-mm-ss time and registers it as gui, the hotkey's publication path"
      - "ui/src/main/capture-picker.ts:432, :456-529 — claimInboxName and publishStagedCapture"
      - "docs/execution/plans/2026-11-08-capture-region-import/ — S58 RULE-1 and RULE-2, exclusive temps and the error mapping"
    research:
      engine: none
      sources: []
    reasoning: "Reusing the inner publish keeps one pixel check, one claim and one register for the hotkey and the paste, so they can't drift. Its system notifications would duplicate the renderer's toast, and copying the pasted image back to the clipboard is pointless, so the paste turns both off; the hotkey keeps them. Writing the bytes in the renderer would need a write IPC that takes an image. Calling the import endpoint on a temp file outside the inbox would register it as import, not gui, against 09. Main's cached inbox is the default until its first settings answer and stays on the old folder after a Save until the next successful poll, so each paste reads the current inbox from the backend through resolvePasteInbox and answers not-ready, writing nothing, when that read fails (plan review rounds 1 and 2, F2). A first-adoption flag would fix only start-up, and refreshing the shared cache from the paste would race the poll; a read of its own touches neither. The hotkey's own reading of the cached value is unchanged and out of scope. Two-way."
    human_message_reference: null
  - id: D-557
    stage: planning
    question: "What may a paste print?"
    resolution: autonomous
    class: two-way
    chosen: "PASTE_LOG: codes and the claimed basename only; the hotkey's existing path-bearing lines are pre-existing and unchanged"
    source_tag: Inferred
    precedents:
      - "docs/execution/plans/2026-11-08-capture-region-import/ — S50 RULE-1 and S58 RULE-2 carried in Session 61's prompt"
      - "ui/src/main/capture-picker.ts:456-529 — publishStagedCapture logs and notifies with full paths"
    research:
      engine: none
      sources: []
    reasoning: "A new path in a log is what S50 RULE-1 forbids for this session's surfaces. Changing the hotkey's lines would change behaviour Session 58 approved and its tests pin, outside this MEU. Recording them as pre-existing, not as a residual of this session, keeps the scope honest; the handoff names them. Two-way."
    human_message_reference: null
  - id: D-558
    stage: planning
    question: "How does the renderer decide that a file isn't an image?"
    resolution: autonomous
    class: two-way
    chosen: "IMPORT_TYPES: the last extension, case-insensitive, one of png, jpg, jpeg, webp, matching the dialog filter and the server's suffix rule; a non-image is never sent and gets the fixed reason"
    source_tag: Inferred
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1098 — the dialog filters to png, jpg, jpeg and webp"
      - "C:/Temp/av-kit/s61/probe/name-probe.txt — the server answers fixed messages"
    research:
      engine: none
      sources: []
    reasoning: "Sending a text file to the server would only bring back the server's refusal, after a request, and its text is about the file's content rather than what the user did. The client check uses the same four extensions as the dialog, so the button and drop agree. Sniffing bytes in the renderer would need file reads it doesn't have. A file with an image extension and bad content still goes to the server, whose message names the problem. Two-way."
    human_message_reference: null
  - id: D-559
    stage: planning
    question: "Is there a Session 61b?"
    resolution: autonomous
    class: two-way
    chosen: "No. The session runs whole; if it passes half its context before row 4, the coordinator tells Mat and nothing moves without Mat's words"
    source_tag: Local Canon
    precedents:
      - ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md:80 — no split flag for Session 61"
      - "docs/execution/plans/2026-11-10-gui-capture-crop-tool/ — 24 ACs, a geometry module and two components ran as one session"
    research:
      engine: none
      sources: []
    reasoning: "The paste path is about 12 ACs of unit work around a function that reuses an existing publication path, and the page work is three small handlers, a toast and a gate. The natural split (paste into 61b) would separate the drop and paste Electron proofs that 09's Tests row asks for together, and would move the IPC pins twice. Two-way."
    human_message_reference: null
  - id: D-560
    stage: planning
    question: "How does the Electron paste proof treat Mat's system clipboard?"
    resolution: human
    class: two-way
    chosen: "A: save text, HTML, RTF and image before, restore them in finally and verify, with the clipboard-free check first; other formats and the Win+V history entry are disclosed"
    source_tag: Human
    precedents:
      - "ui/src/main/index.ts:395-399 — readClipboard answers 'pasted' under AVKIT_E2E, the seam pattern of option B"
    research:
      engine: none
      sources: []
    reasoning: "The proof writes to a clipboard Mat uses, so what it may change is Mat's call. A proves the real read and keeps what Electron can carry. B never touches the clipboard but leaves clipboard.readImage unproven in the real app. C, doing nothing, loses whatever Mat had copied each run. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: save and restore (Recommended)'"
  - id: D-561
    stage: planning
    question: "Does Mat look at the import before the execution review?"
    resolution: human
    class: two-way
    chosen: "A: row 6 launches the dev app detached on a test inbox; Mat drops two PNGs and notes.txt, imports the JPEG through the button and pastes a Win+Shift+S snip"
    source_tag: Human
    precedents:
      - "docs/execution/plans/2026-11-10-gui-capture-crop-tool/human-check.md — Session 60's look"
    research:
      engine: none
      sources: []
    reasoning: "A real Explorer drop, a real snip and how the toast reads are judgements the tests can't make. B, doing nothing, reviews on the Electron proof alone and Mat looks after the commit. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-10 'A: I'll look (Recommended)'"
  - id: D-562
    stage: planning
    question: "How are the three entries recorded in the GUI actions index?"
    resolution: autonomous
    class: two-way
    chosen: "ACTIONS_INDEX: capture:import, capture:drop and capture:paste rows after capture:region, palette no; a MEU-132 audit describe checks them with AC-88.11's preloadChannelFor; CAPTURE_AUDIT_TESTIDS and resolveIpcChannel are unchanged"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/gui-actions-index.md:70-92 — the capture rows"
      - "ui/tests/unit/gui-actions-audit.test.ts:246-310 — MEU-88's ACTION_ROWS and preloadChannelFor, the pattern this follows"
      - "ui/tests/unit/gui-actions-audit.test.ts:65-69, :168-187 — CAPTURE_AUDIT_TESTIDS feeds AC-23.19, so adding to it would fail under AC-23.19's title"
    research:
      engine: none
      sources: []
    reasoning: "Every GUI action has an index row, and AC-23.20 audits them. A palette command for import would need a dialog opened from the palette, and paste is native Ctrl+V; neither adds anything the button and the key don't. Two-way."
    human_message_reference: null
  - id: D-563
    stage: planning
    question: "Does the capture help or the page gain text or a drop highlight?"
    resolution: autonomous
    class: two-way
    chosen: "No. The button's title names drop and Ctrl+V; the help sheet and the page's look are unchanged"
    source_tag: Inferred
    precedents:
      - "ui/tests/unit/capture-help-content.test.ts — the help bodies are pinned by several ACs"
    research:
      engine: none
      sources: []
    reasoning: "09 asks for neither. The help sheet is pinned by five ACs and MEU-105 rewrites it. A drop highlight is a look judgement; D-561's look is where Mat can ask for one, as a brief. Two-way."
    human_message_reference: null
  - id: D-564
    stage: planning
    question: "Which backend does the Electron proof talk to?"
    resolution: autonomous
    class: two-way
    chosen: "A stub HTTP backend copied from capture-picker.test.ts's startBackend, answering import with 201 and an item, and recording every body"
    source_tag: Local Canon
    precedents:
      - "ui/tests/e2e/capture-picker.test.ts:49 — startBackend records POST /captures bodies"
      - "tests/e2e/test_api_capture_region_import.py — MEU-129's import on the real stack"
    research:
      engine: none
      sources: []
    reasoning: "The stub lets the proof assert the exact bodies and their order, which is what 'one by one' means at the boundary. The real import rules are already proven by Session 58's suite and characterised again by AC-132.21. A real backend in Electron would need a seeded app data folder and test the server a second time. Two-way."
    human_message_reference: null
  - id: D-565
    stage: planning
    question: "Another session has uncommitted edits in meu-status.yaml, meu-registry.md and BUILD_PLAN.md. How does row 7 record MEU-132?"
    resolution: autonomous
    class: two-way
    chosen: "Row 7 copies each of the three files to C:/Temp/av-kit/s61/pre-status/ first (S55 RULE-2), checks each still hashes to its baseline-dirty.txt SHA-256, runs tools/meu_status.py update, and diffs against the copy to prove only MEU-132's entry and rows changed. At commit, the three files are named to Mat with both sessions' changes, and only Mat's words decide what is staged"
    source_tag: Inferred
    precedents:
      - "git status at 55d1289 — the three files dirty from the download-reliability session"
      - "Session 55 RULE-2 — save a copy before a tool rewrites a shared file"
    research:
      engine: none
      sources: []
    reasoning: "meu_status.py rewrites the whole file, so without a copy and a diff a row could silently fold the other session's edits into this record or lose them. Waiting for the other session to commit would block row 7 on work Claude can't see. Staging only this MEU's hunks is possible but is a commit choice, which is Mat's. Two-way."
    human_message_reference: null
```

## Research References

- `docs/build-plan/09-screenshot-capture.md:1091-1102` (the contract), §Image import (MEU-129) and §Result publication.
- `_inspiration/capture-crop/design.md`: §7.2 and design D-12.
- The grouping file: §3 (`:78-80`), §7 (`:115-122`), §8 (`:126-143`), the tracker (`:111`).
- Session 60's plan and scripts (`docs/execution/plans/2026-11-10-gui-capture-crop-tool/`), Session 58's plan (`2026-11-08-capture-region-import/`), Session 41 `gui-keyboard-palette` and MEU-39 `gui-capture`.

## Planning receipts

- `C:/Temp/av-kit/s61-plan-probes.txt`: line endings and SHA-256 of every target file at `55d1289`.
- `C:/Temp/av-kit/s61-plan-dids.txt`: the D-id and AC sweep; D-550 up and AC-132 are free.
- `C:/Temp/av-kit/s61/probe/paste-drop-probe.txt`: P1, the paste event per focus case; P2, real paths through a drop (D-550, D-551). It counted events and read no clipboard data.
- `C:/Temp/av-kit/s61/probe/name-probe.txt`: the lone surrogate, control character and empty path through the real import (AC-132.21).
- `C:/Temp/av-kit/s61/probe/hotkey-free.txt`: F2 free and no Electron process from this tree.
- `C:/Temp/av-kit/s61-plan-identity-selftest.txt`, `s61-plan-redcheck-selftest.txt`, `s61-plan-devprocs-selftest.txt`, `s61-plan-hotkey-selftest.txt`, `s61-plan-hotkey-live.txt`, `s61-plan-lookcheck-selftest.txt`: the scripts' selftests and the live hotkey and clipboard check.
- `C:/Temp/av-kit/s61-plan-baseline-probe.txt`: `baseline.ps1`'s ruled, queue, shapes and anchors checks run alone; ruled fails as it must before Mat rules.
- `C:/Temp/av-kit/s61-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s61-plan-decision-probe.txt`: the decision probe (`s61-decision-issue-probe.py`), with this plan and the grouping as sources: 23 decisions, D-400 to D-406 at stage `grouping` and D-550 to D-565 at `planning`. Its first run refused two `{…}` slots in D-556 and D-564 as template placeholders; both were reworded.
- `C:/Temp/av-kit/s61-plan-ruff.txt`: `ruff check packages/ tests/` passes at `55d1289`, so the gate's `py-lint` starts clean.
- Step 4A GUI check (`gui-refs-not-shipped`): E2 is AC-132.22 and .23, written and wired for the drop, the button and the paste; G34 is `Button` `secondary` `md` for Import beside the `primary` Capture region; G35 is the toast and the button's `aria-busy`.
- Not run at plan time: any suite, build or the look.

## Validation stage contract

- **Static:** the UI typecheck and lint, `ruff check packages/ tests/`, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds and the two render checks, in the session gate.
- **Runtime:** the Electron runs of `capture-import.test.ts`, `capture-picker.test.ts` and `capture-inbox.test.ts`; under D-561, the look.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
