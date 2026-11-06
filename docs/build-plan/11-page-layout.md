# Phase 11 — Page layout canon

> Source: the six `docs/proposals/2026-09-03-*-page-layout-mockup.html` proposals, especially §04–§06; `docs/BUILD_PLAN.md` Phase 11 lock; approved MEU-49 queue geometry. MEU-50 authors this canon. MEU-51 provides the shared presentational primitives. MEU-52–58 compose product pages.

## Scope and non-goals

**COMPOSITION_LOCK:** Phase 11 preserves the same IPC, same API payloads, same persisted mutations, same enablement and save behavior, and every existing test ID. A control may move, gain a visual wrapper, or change presentation while retaining its operation. No new API endpoint, persisted mutation, or enablement rule is introduced by Session 23. Later page MEUs must reconcile each §05 keep/move/change entry before replacing a page. The Convert staged-file × in CV1 edits only local pre-Add staging; it does not delete a queued job.

The phase composes six pages: Downloader, Convert, Transcript, TTS, Capture, and Settings. Capture is a layout page, not a queue-card consumer. Session 23 does not mount any new primitive in a product page. A test-only Electron renderer entry exercises the five real MEU-51 primitives and is excluded from the product build; first product-page E2E assertions remain with their owning MEUs.

## Decision register

This is the single Phase 11 `DECISION_SET` of 37 §06 choices: DL1–DL4, CV1–CV7, TR1–TR6, TT1–TT7, CP1–CP6, ST1–ST7. Each source names the mockup's §06; §04 supplies sizing and §05 supplies the affected ID inventory. `COMPOSITION_LOCK` resolves proposals that otherwise change a mutation or enablement rule. The owner implements the locked presentation, without reopening the decision by inference.

| ID | Locked choice | Basis | Owner MEU | Test-ID effect |
|---|---|---|---|---|
| DL1 | Advanced initially opens when cookie mode is not none or SABR is active; later toggles are local presentation state. | `docs/proposals/2026-09-03-downloader-page-layout-mockup.html` §06; §05 | MEU-53 | Keep cookie and SABR IDs; add `add-advanced-toggle`. |
| DL2 | Header chips show nonzero statuses; retain all eight counts in the existing summary model and a read-only More summary. | `docs/proposals/2026-09-03-downloader-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-52 | Keep `queue-summary` on the chip group and existing status data. |
| DL3 | One page-agnostic queue header component mounts on both Downloader and Convert in the same MEU. | `docs/proposals/2026-09-03-downloader-page-layout-mockup.html` §06; grouping MEU-52 | MEU-52 | Keep both pages' toolbar, summary, and selection IDs. |
| DL4 | Active SABR appears as a warning chip beside Quality and remains visible in Advanced; inactive SABR stays hidden. | `docs/proposals/2026-09-03-downloader-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-53 | Move `sabr-status`; retain Check/Force/Clear IDs. |
| CV1 | Staged files are removable chips; × removes one path from local pre-Add staging and issues no API request. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Keep dropzone/Browse/Add IDs; new local chip removal ID may be added. |
| CV2 | Add includes the staged count when nonzero and retains the same Add command. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Keep `convert-add`; label changes only. |
| CV3 | Convert keeps its editable Output folder and explicit Save; Settings keeps its own explicit Save. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Move `convert-output-dir` and `convert-page-save`; keep action. |
| CV4 | Save is ghost while clean and primary when dirty, retaining the existing dirty-dot semantics. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Keep `convert-page-save`; appearance follows current dirty state. |
| CV5 | Retain exact `gpuChipLabel` strings and change only the chip container style. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Keep `convert-gpu-chip` and text assertions. |
| CV6 | Show one Refresh GPU control beside the chip at all times; remove the hidden duplicate only while the same command remains reachable. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Keep one `convert-gpu-refresh` ID. |
| CV7 | Card line two uses only metadata already on each queue item; when preset or encoder is absent, show task kind alone. | `docs/proposals/2026-09-03-convert-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-54 | Keep queue row IDs; no new API field. |
| TR1 | Use three toolbar actions: Start, Pause/Resume, Stop; no new Clear finished mutation and no empty fourth overflow. | `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-55 | Move `start-btn`, `pause-btn`/`resume-btn`, `stop-btn`; no fabricated fourth action. |
| TR2 | One Pause/Resume node swaps its label and the two existing IDs with processor state. | `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-55 | Preserve `pause-btn` and `resume-btn` as state-dependent IDs. |
| TR3 | Opening a card menu selects that card in the existing single-select model. | `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-55 | Keep `channel-card` selection semantics. |
| TR4 | Links and menu items appear only for actions currently available in that status; retain existing routes and IPC. | `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-55 | Move existing action IDs to menu items; new link IDs are separate. |
| TR5 | Processing line three shows last title, status and the last item's message; a Failed or Paused card with an `error_message`, or a Done card with one (a skipped video), shows it in a `job-message` line in place of the output root; other cards show output root, with raw/compiled paths available through the retained output-tree affordance and accessible text. | `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-55 | Keep `last-title` and `output-tree` with status-specific content. |
| TR6 | Transcript remains single-select; introduce no checkbox or bulk action in MEU-55. | `docs/proposals/2026-09-03-transcript-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-55 | Keep `channel-card` and current single-select action IDs. |
| TT1 | Keep native format select in the new row, with the `format-select` ID and existing values. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; COMPOSITION_LOCK; G30 | MEU-56 | Keep `format-select` and selectOptions behavior. |
| TT2 | Humanize cleanup labels while preserving exact cleanup values sent to the API. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-56 | Keep `cleanup-pipeline` and its field IDs/values. |
| TT3 | Shorten the visible loaded-model chip and retain full variant/device/bytes in accessible details inside Manage. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-56 | Keep `loaded-model`; move detail without dropping it. |
| TT4 | Render Open file and Open folder only when output exists, retaining both existing action IDs when rendered. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-56 | Keep `open-output-btn` and `open-output-folder-btn` when actionable. |
| TT5 | Keep muted “No output yet” in the idle run-bar slot, so no-output state remains explicit. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-56 | Keep `last-output`/idle-copy meaning. |
| TT6 | Add no voice preview control because there is no preview endpoint in the current contract. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-56 | Existing voice IDs remain; no dead preview ID. |
| TT7 | Place the run bar statically below the two columns, not sticky to the viewport. | `docs/proposals/2026-09-03-tts-page-layout-mockup.html` §06; §04 | MEU-56 | Move output/progress/action IDs into the static bar. |
| CP1 | Mount Save overlay only when dirty, retaining `capture-save` whenever actionable. | `docs/proposals/2026-09-03-capture-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-57 | Keep `capture-save` on the dirty overlay action. |
| CP2 | Put the hotkey key cap inside the Capture button only when a hotkey is registered. | `docs/proposals/2026-09-03-capture-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-57 | Keep `capture-region`; no fake unregistered key cap. |
| CP3 | Keep both Capture-page Settings disclosure controls and Settings-page controls with their existing save targets. | `docs/proposals/2026-09-03-capture-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-57 | Keep path/hotkey/Save IDs; add disclosure toggle ID. |
| CP4 | Strip the date from visible filmstrip name and show time below; retain full original name accessibly. | `docs/proposals/2026-09-03-capture-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-57 | Keep `capture-filmstrip-item` and accessible full name. |
| CP5 | Keep annotation tools visible but disabled when no shot is selected, matching existing enablement. | `docs/proposals/2026-09-03-capture-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-57 | Keep all `capture-tool-*` IDs and disabled semantics. |
| CP6 | Reserve `capture-status` for its current error/status channel; optional shot information is separate display text. | `docs/proposals/2026-09-03-capture-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-57 | Keep `capture-status`; never mask errors with shot info. |
| ST1 | Style existing native cookie radios as a segment, preserving radio semantics and IDs. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK; G30 | MEU-58 | Keep `settings-leaf-cookie_mode-*` IDs on radios. |
| ST2 | Label autosave, explicit-save, and immediate-apply sections without unifying their mutations. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-58 | Keep each save button and leaf ID. |
| ST3 | Track rail active section with IntersectionObserver; support click/keyboard navigation and a no-observer fallback. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-58 | Add rail IDs; retain section IDs. |
| ST4 | Source each number hint from existing GUI/settings validation; invent no unit or range. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-58 | Keep numeric leaf IDs, min/max/step. |
| ST5 | Write checkbox explanations only where a source-backed sentence exists; otherwise retain the HelpCard link. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-58 | Keep checkbox and HelpCard IDs. |
| ST6 | Keep Audio format enabled when Audio only is off, preserving the existing enablement rule. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-58 | Keep `settings-leaf-audio_format` enabled. |
| ST7 | Derive readiness count and rail warning from existing readiness state; show no fabricated count before it loads. | `docs/proposals/2026-09-03-settings-page-layout-mockup.html` §06; COMPOSITION_LOCK | MEU-58 | Keep readiness links/status IDs. |

## Queue scroll container rule

`QUEUE_SCROLL_CONTAINER_RULE` is a Phase 10 input, not a new Phase 11 layout option. The page root keeps `h-full min-h-0`. The queue region keeps `flex-1 min-h-[20rem]`. Put `overflow-auto` on the page wrapper around `QueueList`, never on the shared list or its file-drop containing block. The controls above the queue form one `min-h-0 overflow-auto` pane and yield the height deficit; a `shrink-0` summary and toolbar remain visible above the scroller. Both queue pages keep this entire chain when their Zone 1 controls are recomposed.

Sources: `docs/proposals/2026-09-03-downloader-page-layout-mockup.html §04`, `docs/proposals/2026-09-03-convert-page-layout-mockup.html §04`, and `docs/execution/reflections/2026-09-03-p10-queue-card-dnd-reflection.md` §Next Day Outline. The approved MEU-49 keyboard reorder geometry is a behavioral dependency.

## Shared layout primitives

The common vocabulary is a left-aligned **zone** within the column cap, a label/control **form grid**, a controlled **disclosure**, a native-radio **segment**, readable status **chip**, and a **save-model caption** that names the existing persistence mode. `--layout-page-max-width: 72rem` (1152 px) is declared once in `ui/src/renderer/src/styles.css` and used by Downloader, Convert, Transcript, TTS, and Capture. Settings uses its own 960 px cap from its mockup §04. No duplicate light-theme geometry value is added.

MEU-51 builds `Disclosure`, `SegmentedControl`, `StatusChip`, `FormRow`, and `PathRow` as controlled presentational components. Pages supply values, IDs, validation, browse callbacks, and persistence. The components add no API or IPC call. Use existing G32 colors, G33 motion tokens, and G34 button sizes. A test-only Electron harness mounts the real primitives for Session 23 E2E behavior; product pages first mount them in MEU-52–58.

## Queue header row

MEU-52 builds one queue header row for Downloader and Convert in the same change. It combines select-all, nonzero status chips, processor state, and the existing four-control `QueueToolbar`, while preserving each page's existing IDs and full count model. Bulk bar and toast remain outside the list scroller. Transcript may reuse the header anatomy in MEU-55, but TR1 permits only its three existing actions and no new queue mutation. The `QUEUE_SCROLL_CONTAINER_RULE` applies to both queue pages.

## Downloader page layout

MEU-53 composes Zone 1 from the URL/Add row, natural-width options, and Advanced disclosure. Cookie mode stays three native radios. SABR Check/Force/Clear move into Advanced, while active SABR status appears beside Quality. Advanced opens initially for a configured cookie mode or active SABR; toggling afterward is local presentation state. Add still submits on Enter. MEU-52 already owns the queue header below. The `QUEUE_SCROLL_CONTAINER_RULE` and every §05 keep/move/change item remain binding.

## Convert page layout

MEU-54 composes task, encoder, staged-file drop strip, Add, task options, Advanced, and output footer. Staged-chip removal is local pre-Add state only. The Add label may include a nonzero staged count but invokes the existing command. Output folder remains editable on this page with explicit Save; GPU chip text remains exact; one Refresh GPU command stays reachable. Queue card metadata uses only already-carried fields. MEU-52 supplies the queue header and `QUEUE_SCROLL_CONTAINER_RULE` remains intact.

## Transcript page layout

MEU-55 composes channel Add, QueueCard-shaped channel rows, and a three-action header toolbar. The existing single-select model remains. Card menus select their card and expose only currently available actions. Pause/Resume is one node whose ID follows state; no Clear finished mutation is added. The last-title/output-tree content follows TR5. MEU-55 also inherits the MEU-48 `ChannelCard` convergence AC in Supersession.

## TTS page layout

MEU-56 composes text and voice columns with Cleanup and Manage-model disclosures and a static run bar below. Format stays a native select. Cleanup labels may be humanized while their API values stay fixed. A compact loaded-model chip keeps full details accessible in Manage. Idle output remains explicit, and Open file/folder render only when output exists. MEU-56 inherits the MEU-48 shared ProgressBar AC.

## Capture page layout

MEU-57 composes a Capture header, Settings disclosure, filmstrip, viewport toolbar, draw surface, and inline confirm strips. It retains current IPC, annotation reducer, confirmation behavior, and duplicated page/Settings controls. Save overlay appears only when dirty; other annotation tools stay visible but disabled without a shot. `capture-status` remains the error/status channel, and shot information is separate. Capture is not a QueueCard page.

Since MEU-65 the header disclosure is titled **Options** (a secondary button with an icon and a chevron), and the viewport toolbar is icon buttons with a contextual options row; see [09 §Viewport toolbar icons and Options](09-screenshot-capture.md#viewport-toolbar-icons-and-options).

Since MEU-67 the per-shot actions also include **Apply to image** and, once a backup exists, **Revert**, behind the same inline confirm strip; see [09 §Flatten with backup](09-screenshot-capture.md#flatten-with-backup).

Since MEU-81 the per-shot and per-mark actions are icon buttons with MEU-80 hints, Delete sits red at the far right after a separator, and the hotkey status shows inline in the header instead of a reserved band; see [09 §Capture action row](09-screenshot-capture.md#capture-action-row).

## Settings page layout

MEU-58 composes a 960 px content column with a responsive section rail and 168 px form grid. Sections label their existing autosave, explicit-save, or immediate-apply model; no mutation is unified. Path rows pair the existing inputs/Browse callbacks. Native cookie radios get segment styling. Number hints use existing field validation, checkbox explanations require a source, and Audio format keeps existing enablement. The readiness count/rail warning use real loaded readiness state. The MEU-61 `start-at-sign-in-panel` and child IDs remain present when this page is recomposed.

## Residuals registered 2026-09-30

Three residual MEUs from the 2026-09-30 GUI walkthrough. They recompose within the MEU-50 canon (`COMPOSITION_LOCK`, column cap, primitives) and record every test id as keep / move / change in their plans.

<a id="tts-model-manager-residual"></a>

### TTS model manager (residual)

> **MEU-63.** Known issues `TTS-MODEL-MANAGE-AFFORDANCE`, `TTS-GENERATE-FAILED-SILENT` (GUI half). The Voice panel hides model management behind a bare "Manage" disclosure with four rows × Get + Load whose enabled and disabled states look alike; a `Failed` job shows no reason because `job.error_message` is never rendered.

| Rule | Contract | Source |
|------|----------|--------|
| Picker | A `SelectInput` lists the variants with a state suffix (not downloaded / downloaded / loaded); Device stays beside it | Human-approved 2026-09-30 ("selection of a model after which Get Load or Unload button will appear"); Local Canon G30 |
| One action | One primary button whose label and action follow the selected variant's state — **Get** when not downloaded, **Load** when downloaded and not loaded, **Unload** when it is the loaded variant — driven by the existing `getEnabled` / `loadEnabled` predicates | Research-backed (model-manager state machines); Local Canon `tts-controls.ts` |
| Readiness | MEU-62's `tts_onnx_vocab` / `tts_spacy_model` rows show beside the picker with their Get action | Local Canon [03 §TTS runtime assets](03-service-layer.md#tts-runtime-assets-residual) |
| Failure surface | `resolveRunBarSlot` treats a `Failed` job with `error_message` as the `error` slot and renders the message; regression test for Failed-with-error_message | Local Canon G25; TT5 |
| Test IDs | `model-manage-toggle`, `model-row`, `model-get-btn`, `model-load-btn`, `unload-btn`, `device-select`, `loaded-model`, `error-banner` recorded keep / move / change in the plan (registry names, D-15); the one action button's `data-testid` follows its action | Spec §Test-ID migration; plan D-15 |

Migration record: [Session 27 plan §MEU-63 Test-ID migration](../execution/plans/2026-09-30-tts-repair/implementation-plan.md#meu-63--gui-tts-model-manager). `model-manager` is the "Model details" panel (execution D-19).

<a id="tts-text-panel-residual"></a>

### TTS text panel (residual)

> **MEU-64.** Known issues `TTS-CLEANUP-APPLY-MISSING`, `TTS-CLEANUP-PREVIEW-REDUNDANT`, `TTS-LANGUAGE-VOICE-PICKER-SPACE`.

| Rule | Contract | Source |
|------|----------|--------|
| Apply cleanup | An **Apply cleanup** button beside Preview sets the text to `cleaned_text` from `POST /tts/prepare`, marks `input_text` touched and persists through the existing debounced leaf; the preview clears | Human-approved 2026-09-30 ("Apply Cleanup is missing so text in the main area gets replaced") |
| Preview | `preview-raw` is removed; `preview-cleaned` renders only after Preview runs and collapses otherwise | Human-approved 2026-09-30 ("do not need to see also on the bottom two text areas") |
| Voice picker | The full-width language select and the 236 px listbox are replaced by a searchable combobox that filters by voice id / name / language, shows the selection as a chip, and groups options by language inside the popup; `role="listbox"` / `option` semantics and the keyboard handler are kept inside the popup. Unavailable voices (missing eSpeak NG, or ja/zh) stay listed as `aria-disabled` options with their reason (`voice-unavailable-reason`), cannot be selected, and an unavailable current selection shows its reason on the chip (MEU-74) | Research-backed (Visa DS multiselect, searchable dropdown patterns); Human-approved delegation ("Web search what would be more compact") |
| Space | Speed and Format are visible without scrolling at the default window size | Spec |
| Test IDs | `preview-cleanup-btn`, `preview-cleaned`, `voice-card`, `voice-grid`, `language-select` recorded keep / move / change; `preview-raw` removed with its assertions amended under the plan's TEST_AMENDMENTS census | Spec §Test-ID migration |

Migration record: [Session 27 plan §MEU-64 Test-ID migration](../execution/plans/2026-09-30-tts-repair/implementation-plan.md#meu-64--gui-tts-text-panel). New ids: `apply-cleanup-btn`, `voice-combobox`, `voice-selected-chip`.

<a id="settings-section-emphasis-residual"></a>

### Settings section emphasis (residual)

> **MEU-70.** Known issue `SETTINGS-ACTIVE-SECTION-HIGHLIGHT`. MEU-58 shipped the rail half (`SettingsRail.tsx` IntersectionObserver + `aria-current`, ST3); the section the rail marks current has no emphasis of its own.

| Rule | Contract | Source |
|------|----------|--------|
| Verify first | The plan's first row confirms on the target that the rail highlight follows scroll on the current build; if it does not, that defect is fixed under ST3 before anything new | Local Canon ST3; [cloud-local-collaboration.md §7](../../.agent/docs/cloud-local-collaboration.md) |
| Emphasis | The current section card receives `data-current="true"` and a subtle surface-raised background / left border from G32 tokens, driven by the same observer state the rail uses; no layout shift, no motion beyond G33 tokens | Human-approved 2026-09-30 ("background on the right panel"); Local Canon G32/G33 |
| Trailing sections | A measured bottom spacer lets every section scroll up to the rail's top band, and the rail re-checks its current entry on scroll (never during a click lock), so each section becomes current in order on any window height. A smooth reveal's fallback jump fires only when its scroller emitted no scroll event | Human-approved 2026-10-10 (bottom spacer); Session 31 plan D-9, D-17, D-22 |
| Emphasis classes | One helper gives every section frame, Startup included, the same padding and 2 px left border; the current frame adds `bg-bg-elevated/40` and `border-accent`. No negative vertical margin, so adjacent frames stay more than the 16 px scroll margin apart | Session 31 plan D-14, D-20 |
| Test IDs | All `SETTINGS_SECTION_SET` section ids (eleven; `startup` only when supported) and rail ids keep | Spec §Test-ID migration; Session 31 plan D-18 |

## Residuals registered 2026-10-09

One residual MEU from the 2026-10-09 local check. It recomposes the TTS Voice panel within the MEU-50 canon and the MEU-63/64 residuals above; no test id is added, removed or renamed.

<a id="tts-voice-panel-alignment-residual"></a>

### TTS voice panel alignment (residual)

> **MEU-79.** Known issue `TTS-MODEL-ROW-LAYOUT`. The Model and Device selects render at different heights, so their labels sit at different baselines; at the default window the Load button wraps onto its own line; Format is taller with a different fill, and the Speed presets sit in a separately sized group.

| Rule | Contract | Source |
|------|----------|--------|
| Model row | `model-row` is a three-column grid (`minmax(0,1fr) 7rem auto`, `items-end`): Model takes the free width, Device is 7rem, and the one model action button (`size="md"`) never wraps | Triage D-68 (USER_EXPLICIT 2026-10-09); plan `VOICE_GRID` |
| Shared height | Model, Device, the model action button, the voice combobox, Format, the speed slider and the Speed preset group share one control height (`h-9`, the Button `md` height); `SegmentedControl` gains `size="md"` for this, and its default `sm` markup is unchanged | Triage D-68; plan `SEGMENT_SIZE`, `VOICE_GRID` |
| Speed and Format | The Speed label uses the `SelectInput` label style, the slider fills its row beside the presets, and Format moves to its own row at Device's width (7rem); Speed and Format stay visible without scrolling at the default window (AC-64.6) | Triage D-68; plan `VOICE_GRID` (D-14) |
| Device list | `device-select` lists only the devices the selected variant reports in the catalog `devices` field ([03 §TTS device resolution](03-service-layer.md#tts-device-resolution-residual)); a stored device the row cannot use is shown and sent as `auto` and is not rewritten | 03 §TTS device resolution (Device list); plan `DEVICE_SELECT_VALUE` (D-13) |
| Geometry | At the default window (1280×800) the Model-row controls have equal height and bottom and their labels equal tops; the Voice controls have the Model select's height; Format has Device's width; neither row overflows, and the slider is at least 96 px wide | Plan `VOICE_GEOMETRY` (D-16) |
| Test IDs | All keep; none added. `model-row`, `model-select`, `device-select`, the `MODEL_ACTION_TEST_IDS` button, `voice-combobox`, `format-select` and `speed-slider` are unchanged | Spec §Test-ID migration |

Migration record: [Session 35 plan](../execution/plans/2026-10-16-tts-voice-panel/implementation-plan.md) (`VOICE_GRID`, `VOICE_GEOMETRY`, `DEVICE_SELECT_VALUE`).

## Supersession

| Earlier source | Carry-forward owner | Binding rule |
|---|---|---|
| `docs/build-plan/06-gui.md` page layouts | MEU-52–58 | Phase 11 supersedes presentation geometry, while Phase 6 action/IPC/save behavior remains binding. |
| `docs/build-plan/08-video-conversion.md` Convert GUI | MEU-54 | Convert presentation follows this canon; existing conversion payloads and mutations remain binding. |
| `docs/build-plan/09-screenshot-capture.md` Capture GUI | MEU-57 | Capture presentation follows this canon; picker/annotation/IPC behavior remains binding. |
| `docs/build-plan/10-queue-card-ui.md` queue convergence | MEU-52/55/56 | QueueCard/QueueList/ProgressBar and MEU-49 scroll behavior remain binding. |
| Closed MEU-48 transcript AC | MEU-55 | `ChannelCard` renders through shared `QueueCard` primitives and has no `width: %` inline motion. |
| Closed MEU-48 TTS AC | MEU-56 | TTS uses shared `ProgressBar`, not a local duplicate. |

## Test-ID migration

`PRESERVED_TESTIDS` means every currently registered ID in `ui/tests/e2e/test-ids.ts` retains its exact string value. The rows below transcribe each mockup §05 inventory entry and its keep/move/change classification into the owning page MEU. A `change` row changes presentation or conditional mount as specified by its decision, never silently removes the action. New IDs for toggles/links are additional and may not duplicate an inherited ID. MEU-52 owns the shared queue header rows on both pages; each page MEU owns its own add-panel/card rows.

| Page | §05 row | Existing ID / element | Migration | Owner MEU |
|---|---:|---|---|---|
<!-- BEGIN MOCKUP INVENTORY -->
| DL | 1 | HelpCard “How it works” | keep | MEU-53 |
| DL | 2 | sabr-status | change | MEU-53 |
| DL | 3 | sabr-check-btn / sabr-force-btn / sabr-clear-btn | move | MEU-53 |
| DL | 4 | url-input | keep | MEU-53 |
| DL | 5 | add-btn | keep | MEU-53 |
| DL | 6 | quality-select | keep | MEU-53 |
| DL | 7 | audio-only | keep | MEU-53 |
| DL | 8 | audio-format | keep | MEU-53 |
| DL | 9 | cookie-mode-none\|browser\|file | move | MEU-53 |
| DL | 10 | cookie-browser, cookie-profile | move | MEU-53 |
| DL | 11 | cookie-file + Browse | move | MEU-53 |
| DL | 12 | cookie-test-btn | move | MEU-53 |
| DL | 13 | add-status | keep | MEU-53 |
| DL | 14 | error-banner | keep | MEU-53 |
| DL | 15 | download-queue-region | keep | MEU-52 |
| DL | 16 | QueueSelectionHeader (select-all, count) | keep | MEU-52 |
| DL | 17 | queue-toolbar (Start · Pause/Resume · Clear finished · More) | keep | MEU-52 |
| DL | 18 | queue-summary (8 counts) | change | MEU-52 |
| DL | 19 | processor-indicator | change | MEU-52 |
| DL | 20 | BulkActionBar, BulkResultToast | keep | MEU-52 |
| DL | 21 | QueueList, queue-empty-invite-action | keep | MEU-52 |
| DL | 22 | ConfirmModal | keep | MEU-53 |
| DL | 23 | new Advanced toggle | change | MEU-53 |
| CV | 1 | convert-page | change | MEU-54 |
| CV | 2 | HelpCard (converter) | keep | MEU-54 |
| CV | 3 | convert-task-compress / -cut / -extract | change | MEU-54 |
| CV | 4 | convert-gpu-chip | change | MEU-54 |
| CV | 5 | convert-gpu-refresh | move | MEU-54 |
| CV | 6 | convert-dropzone | change | MEU-54 |
| CV | 7 | convert-browse | change | MEU-54 |
| CV | 8 | Staged file list <ul> | change | MEU-54 |
| CV | 9 | convert-add | move | MEU-54 |
| CV | 10 | convert-preset-archival … -mobile | change | MEU-54 |
| CV | 11 | convert-advanced | move | MEU-54 |
| CV | 12 | Advanced: CQ, Scale, Audio, Encoder override | change | MEU-54 |
| CV | 13 | convert-cut-in / convert-cut-out | change | MEU-54 |
| CV | 14 | convert-copy radios (Fast / Accurate) | change | MEU-54 |
| CV | 15 | convert-extract-first / convert-extract-all | change | MEU-54 |
| CV | 16 | convert-output-dir | move | MEU-54 |
| CV | 17 | convert-skip-existing | move | MEU-54 |
| CV | 18 | convert-page-save | change | MEU-54 |
| CV | 19 | error-banner | move | MEU-54 |
| CV | 20 | convert-queue-region | change | MEU-52 |
| CV | 21 | QueueSelectionHeader (“Select all conversions”) | change | MEU-52 |
| CV | 22 | BulkActionBar | keep | MEU-52 |
| CV | 23 | BulkResultToast | keep | MEU-52 |
| CV | 24 | convert-queue / convert-queue-row | change | MEU-52 |
| CV | 25 | convert-queue-summary | move | MEU-52 |
| CV | 26 | convert-processor | move | MEU-52 |
| CV | 27 | queue-toolbar (Start · Pause/Resume · Clear finished · ⋯) | move | MEU-52 |
| CV | 28 | Queue overflow menu (Clear all) | keep | MEU-52 |
| CV | 29 | ConfirmModal (remove / clear / bulk) | keep | MEU-52 |
| TR | 1 | transcript-page | change | MEU-55 |
| TR | 2 | HelpCard (transcript) | keep | MEU-55 |
| TR | 3 | channel-input | change | MEU-55 |
| TR | 4 | channel-url-hint | move | MEU-55 |
| TR | 5 | add-btn | move | MEU-55 |
| TR | 6 | error-banner | move | MEU-55 |
| TR | 7 | channel-card | change | MEU-55 |
| TR | 8 | channel-progress | change | MEU-55 |
| TR | 9 | rate-display / eta-display | move | MEU-55 |
| TR | 10 | last-title | move | MEU-55 |
| TR | 11 | output-tree | change | MEU-55 |
| TR | 12 | processor-indicator | move | MEU-55 |
| TR | 13 | start-btn | move | MEU-55 |
| TR | 14 | pause-btn / resume-btn | change | MEU-55 |
| TR | 15 | stop-btn | move | MEU-55 |
| TR | 16 | Toolbar overflow ⋯ | change | MEU-55 |
| TR | 17 | up-btn / down-btn | move | MEU-55 |
| TR | 18 | compile-btn | move | MEU-55 |
| TR | 19 | view-compiled-btn / open-zip-btn / open-folder-btn | move | MEU-55 |
| TR | 20 | requeue-btn / retry-btn | move | MEU-55 |
| TR | 21 | remove-btn | move | MEU-55 |
| TR | 22 | remove-confirm-btn / remove-confirm-cancel | keep | MEU-55 |
| TT | 1 | tts-page | change | MEU-56 |
| TT | 2 | HelpCard (tts) | keep | MEU-56 |
| TT | 3 | error-banner | move | MEU-56 |
| TT | 4 | text-input | change | MEU-56 |
| TT | 5 | load-file-btn / paste-btn | move | MEU-56 |
| TT | 6 | word-count / sentence-count / duration-estimate | move | MEU-56 |
| TT | 7 | cleanup-pipeline (fieldset) | change | MEU-56 |
| TT | 8 | Cleanup disclosure toggle | change | MEU-56 |
| TT | 9 | preview-raw / preview-cleaned | move | MEU-56 |
| TT | 10 | preview-cleanup-btn | move | MEU-56 |
| TT | 11 | model-manager (section) | move | MEU-56 |
| TT | 12 | loaded-model | change | MEU-56 |
| TT | 13 | device-select | change | MEU-56 |
| TT | 14 | unload-btn | change | MEU-56 |
| TT | 15 | model-row / model-get-btn / model-load-btn / download-progress | change | MEU-56 |
| TT | 16 | language-select | change | MEU-56 |
| TT | 17 | voice-grid | change | MEU-56 |
| TT | 18 | voice-card | change | MEU-56 |
| TT | 19 | speed-slider | change | MEU-56 |
| TT | 20 | Speed presets 0.8 / 1.0 / 1.1 | change | MEU-56 |
| TT | 21 | format-select | change | MEU-56 |
| TT | 22 | output-path | move | MEU-56 |
| TT | 23 | browse-output-btn | move | MEU-56 |
| TT | 24 | generate-btn / cancel-btn | move | MEU-56 |
| TT | 25 | Status pill | keep | MEU-56 |
| TT | 26 | segment-progress | change | MEU-56 |
| TT | 27 | last-output | change | MEU-56 |
| TT | 28 | open-output-btn / open-output-folder-btn | change | MEU-56 |
| CP | 1 | capture-page | keep | MEU-57 |
| CP | 2 | HelpCard (capture) | keep | MEU-57 |
| CP | 3 | capture-region | change | MEU-57 |
| CP | 4 | capture-save | change | MEU-57 |
| CP | 5 | capture-delete | move | MEU-57 |
| CP | 6 | capture-open-file / capture-open-folder | move | MEU-57 |
| CP | 7 | capture-inbox-path / capture-inbox-browse | move | MEU-57 |
| CP | 8 | capture-hotkey / capture-hotkey-change | move | MEU-57 |
| CP | 9 | capture-page-save | change | MEU-57 |
| CP | 10 | Settings disclosure toggle | change | MEU-57 |
| CP | 11 | capture-hotkey-banner | change | MEU-57 |
| CP | 12 | capture-status | change | MEU-57 |
| CP | 13 | capture-empty | move | MEU-57 |
| CP | 14 | capture-filmstrip | change | MEU-57 |
| CP | 15 | capture-filmstrip-item | change | MEU-57 |
| CP | 16 | capture-viewport | keep | MEU-57 |
| CP | 17 | capture-tool-arrow / -box / -highlight / -text | change | MEU-57 |
| CP | 18 | capture-undo / capture-redo | keep | MEU-57 |
| CP | 19 | capture-color | change | MEU-57 |
| CP | 20 | capture-stroke | change | MEU-57 |
| CP | 21 | “Select a shot from the filmstrip.” | keep | MEU-57 |
| CP | 22 | capture-draw-surface / capture-viewport-image / capture-annotation / capture-text-draft | keep | MEU-57 |
| CP | 23 | capture-dirty-confirm / capture-dirty-confirm-cancel | change | MEU-57 |
| CP | 24 | capture-delete-confirm / capture-delete-confirm-cancel | change | MEU-57 |
| ST | 1 | settings-page | change | MEU-58 |
| ST | 2 | h1 “Settings”, HelpCard (settings), error p | keep | MEU-58 |
| ST | 3 | Section rail | change | MEU-58 |
| ST | 4 | download-settings … mcp-access-card (9 section ids) | change | MEU-58 |
| ST | 5 | Section save-mode caption | change | MEU-58 |
| ST | 6 | settings-leaf-path + browse-download-path-btn | change | MEU-58 |
| ST | 7 | settings-leaf-quality | change | MEU-58 |
| ST | 8 | settings-leaf-audio_only + settings-leaf-audio_format | change | MEU-58 |
| ST | 9 | settings-leaf-ffmpeg_path + browse-ffmpeg-btn | change | MEU-58 |
| ST | 10 | settings-leaf-cookie_mode + -none / -browser / -file | change | MEU-58 |
| ST | 11 | settings-leaf-cookie_browser / settings-leaf-cookie_browser_profile | change | MEU-58 |
| ST | 12 | settings-leaf-cookie_file_path + browse-cookie-file-btn | change | MEU-58 |
| ST | 13 | settings-leaf-archive_tracking / settings-leaf-yt_dlp_debug | change | MEU-58 |
| ST | 14 | apply-defaults-btn | change | MEU-58 |
| ST | 15 | settings-leaf-output_dir + browse-transcript-dir-btn | change | MEU-58 |
| ST | 16 | Transcript numbers (8): requests_per_hour, delay_between_requests, max_retries, retry_delay, batch_size, pause_between_batches, playlist_end, max_words_per_document | change | MEU-58 |
| ST | 17 | settings-leaf-models_directory + browse-models-dir-btn, settings-leaf-output_path + browse-tts-output-btn | change | MEU-58 |
| ST | 18 | settings-leaf-voice / settings-leaf-output_format / settings-leaf-device | change | MEU-58 |
| ST | 19 | settings-leaf-speed | change | MEU-58 |
| ST | 20 | settings-leaf-chunk_max_chars | change | MEU-58 |
| ST | 21 | settings-leaf-converter-output_dir + browse-convert-path-btn | change | MEU-58 |
| ST | 22 | settings-leaf-default_preset / settings-leaf-gpu_preference | change | MEU-58 |
| ST | 23 | settings-leaf-skip_existing | change | MEU-58 |
| ST | 24 | convert-settings-save / capture-settings-save | change | MEU-58 |
| ST | 25 | settings-leaf-capture-inbox_dir + browse-capture-path-btn | change | MEU-58 |
| ST | 26 | settings-leaf-hotkey | change | MEU-58 |
| ST | 27 | settings-leaf-copy_to_clipboard / settings-leaf-close_to_tray | change | MEU-58 |
| ST | 28 | settings-leaf-log_level | change | MEU-58 |
| ST | 29 | settings-leaf-log_to_file + settings-log-file-path + settings-copy-log-path | change | MEU-58 |
| ST | 30 | settings-leaf-console_visible | change | MEU-58 |
| ST | 31 | theme-dark-btn / theme-light-btn | change | MEU-58 |
| ST | 32 | start-at-sign-in-panel / start-at-sign-in-checkbox / start-minimized-checkbox | keep | MEU-58 |
| ST | 33 | Dependencies rows + check-deps-btn | change | MEU-58 |
| ST | 34 | readiness-descriptor-link / readiness-port-link / readiness-models-link / readiness-ffmpeg-link | change | MEU-58 |
| ST | 35 | mcp-token-present / copy-mcp-btn / pin-mcp-btn | change | MEU-58 |
<!-- END MOCKUP INVENTORY -->

## Verification

MEU-50 tests require exactly 37 unique decision rows with mockup §06 basis, owner, and test-ID effect; every §05 row must map; the Phase 11 hub link must resolve; and `COMPOSITION_LOCK`, the scroll rule, closed MEU-48 transfers, and column cap must remain explicit. MEU-51 tests assert controlled interaction and no product-page imports. The test-only Electron wave proves the real primitives are reachable and excludes its entry from the ordinary build/package. Product-page E2E waves belong to MEU-52–58. Tests, typecheck, lint, build, and independent execution review are recorded in the Session 23 task/handoffs.
