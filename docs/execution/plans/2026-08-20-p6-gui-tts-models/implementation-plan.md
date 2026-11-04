---
project: "2026-08-20-p6-gui-tts-models"
date: "2026-08-20"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-22"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI TTS + Models

> **Project**: `2026-08-20-p6-gui-tts-models`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §TTS Page (`/tts`)
> **Status**: `draft`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 10 — MEU-22 only

---

## Goal

Replace the `/tts` `LazyPlaceholder` with the TTS page: text editor (Load File / Paste), 11-step prepare pipeline + preview, voice grid with language filter, speed/format/output-path controls, generate/cancel bar, and Model Manager (available rows + download-runtime + load/unload). Persist editor leaves via `PUT /settings/tts`. Do not rewrite FastAPI routers or MCP tools. Do not start MEU-23–25. Do not invent MEU IDs. Do not rewind MEU-26 chrome.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning and execution use file reads + P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-22 | `.agent/context/handoffs/2026-08-20-p6-gui-tts-models-MEU-22-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-20-p6-gui-tts-models-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-22a | MEU-22 Red: AC-22.1–22.24 UI tests **before** `TTSPage` production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Receipt must pass `RED_ORACLE_CHECK` (kind `ui`) — 24 distinct failed JSON tests, not a stuffed title. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-22-ui.txt`; `RED_JSON` |
| WP-22b | Green: `TTS_HOME` + Query hooks + prepare/generate + Model Manager + `CLIPBOARD_READ` + `FILE_LOAD_OUT` + `PALETTE_DELIVER` (`AppShell` + `TTS_COMMANDS`). Do not neutralize tests. Do not edit FastAPI/MCP. Do not import Settings page. | WP-22a | `compact_continue` | `ui/src/renderer/src/features/tts/`; `ui/src/main/ipc.ts`; `ui/src/main/preload.ts`; `ui/src/renderer/src/env.d.ts`; `AppShell.tsx`; compact then re-read `task.md` |
| WP-22c | Wave 2 E2E **written and wired** (`E2E_WAVE2` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_ACTUATE` + `E2E_ATTACHED_FIRST` + `E2E_CONTROL_CENSUS` + `E2E_SEAM_INSTALL` + `E2E_SEAM_GATE` + `E2E_SEAM_PROOF` + `E2E_SEAM_NEG`). Isolated `AVKIT_APP_DATA`. Honor `E2E_NO_LIVE_HF` via `E2E_SEAM_INSTALL` + `E2E_HAPPY_PATH`. Run or `[B]` `E2E_SANDBOX`. | WP-22b | `compact_continue` | `ui/tests/e2e/tts-generate.test.ts`; `C:/Temp/av-kit/e2e-wave2.txt` |
| WP-22d | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-22c | `compact_continue` | `.agent/context/handoffs/2026-08-20-p6-gui-tts-models-MEU-22-handoff.md` |
| WP-22e | Hub + SSOT: bind MEU-22; keep prior phase-6 slashes; `HUB_NEXT_AFTER`. Grouping Session 10 → complete is **H2 after exec `approved`**, not this row. | WP-22d | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution.
2. **Slug:** user typed `p6-gui-tts-model`. Grouping pathway #10 is `p6-gui-tts-models`. **Lock grouping slug.**
3. **No TTS queue:** there is no `GET /tts` list envelope. One active job is polled at `GET /tts/{id}` after `POST /tts/generate` returns 201. **Lock `JOB_POLL`.** Do not invent `{ items, processor }` for TTS.
4. **Cancel, not Stop:** index `tts:cancel` → `DELETE /tts/{id}`. **Lock `CANCEL_VERB`.** Do not ship `stop-btn` / `tts:stop` on this page.
5. **File-load dialog only:** `readTextFile` always opens a main-process dialog (`.txt`/`.md`, `maxBytes` ≤ 2 MiB). Renderer cannot pass a path. Success value is `FILE_LOAD_OUT` (`text` + `basename` only). `source_path` on generate is that basename. **Lock `FILE_LOAD`.**
6. **Paste IPC stub:** `read-clipboard-text` currently returns `''` (`ipc.ts` 289–290). `tts:paste` cannot work until the existing channel reads `clipboard.readText()`. **Lock `CLIPBOARD_READ`** — complete the registered channel; do not add a new IPC name; do not use `navigator.clipboard`.
7. **Catalog rows:** **Lock `CATALOG_ITEMS`:** render `GET /models/available` `items` as-is. Do not hardcode or filter rows. `SEED_VARIANTS` currently has four rows (including PyTorch FP32); fixtures may use those rows or arbitrary API rows.
8. **Language labels:** spec table says “English (US)”. `VoiceOut.language` is `American English` / `British English` / … (`voices.py` `LANG_BY_PREFIX`). **Lock `LANG_FILTER`** to `VoiceOut.language` from `GET /tts/voices`. Never expose `lang_code`.
9. **Settings writes on this page:** persist `input_text`, `voice`, `speed`, `output_format`, `output_path`, `device` via `PUT /settings/tts` (`SettingsPutIn` extra forbid). `chunk_max_chars` is **read** for prepare; the chunk editor and `models_directory` Browse stay MEU-23.
10. **4A indexes:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` remain **absent**. Apply `06-gui.md` + G30–G35 + `gui-actions-index.md`. Language / format / device use existing `SelectInput` (G30).
11. **Live HF/Kokoro in Wave 2:** generate and model download must not reach adapters. **Lock `E2E_SEAM`** (renderer `fetch` override + `E2E_SEAM_GATE` + fail-closed `E2E_SEAM_UNHANDLED`). `page.route` is not proof (downloader RULE-2).

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `TTS_HOME` | route `/tts` component is `TTSPage` (not `LazyPlaceholder` / `ModuleSkeleton`). `nav:tts` hashes to `/tts`. | Spec 194–197, 265, 741 |
| `PAGE_FILES` | `ui/src/renderer/src/features/tts/{TTSPage,useTtsPage,tts-controls,tts-commands,tts-stats,prepare-steps,voice-grid,model-manager}.tsx?ts` + `ui/src/renderer/src/router.tsx` + `ui/src/renderer/src/registry/commandRegistry.ts` + `ui/src/renderer/src/components/layout/AppShell.tsx` + `ui/src/main/ipc.ts` + `ui/src/main/index.ts` | this plan |
| `PREPARE_STEPS` | `punctuation`, `symbols`, `numbers`, `currency`, `all_caps`, `chapter_markers`, `urls_emails`, `page_numbers`, `whitespace`, `chunk`, `kokoro` | `PREPARE_STEP_IDS` |
| `PREPARE_DEFAULT_ON` | all `PREPARE_STEPS` except `chapter_markers` | `prepare.py` 24 |
| `PREPARE_BODY` | `{ text: string, enabled_steps: PREPARE_STEPS[], chunk_max_chars?: number }` — extra forbid | `TTSPrepareIn` |
| `PREPARE_OUT` | `{ cleaned_text: string }` — no job row | `TTSPrepareOut`; 04 243 |
| `GENERATE_BODY` | `{ text: string.min(1), voice: string, speed: number, format: 'MP3'\|'WAV', enabled_steps: string[], source_kind: 'inline'\|'file', source_path?: string\|null }` — extra forbid. `source_path` is basename metadata only. | `TTSGenerateIn`; Spec 894 |
| `JOB_OUT` | `TTSJobOut` fields; **never** full input text (`text_preview` / `text_hash` only) | `TTSJobOut`; 04 259–261 |
| `JOB_STATUSES` | `Pending`, `Generating`, `Done`, `Failed`, `Cancelled` | `TTSStatus` |
| `JOB_POLL` | after 201, poll `GET /tts/{id}`. No `GET /tts` list. No `{ items, processor }` for TTS. | `tts.py` 54–89; lock 3 |
| `QUERY_JOB` | `['tts', 'job', id]` | this plan |
| `QUERY_VOICES` | `['tts', 'voices']` | this plan |
| `QUERY_MODELS` | `['models', 'available']` | this plan |
| `QUERY_STATUS` | `['models', 'status']` | this plan |
| `QUERY_RUNTIME` | `['models', 'download-runtime']` | this plan |
| `QUERY_SETTINGS` | `['settings', 'tts']` | this plan |
| `POLL_ACTIVE_MS` | `1000` when job status is `Generating` **or** runtime `state === 'Downloading'` | Spec 846, 737 cadence |
| `POLL_IDLE_MS` | `5000` otherwise (including no job yet) | MEU-20/21 cadence |
| `SPEED_RANGE` | min `0.5`, max `2.0`, step `0.1` | `TTS_SPEED_MIN`/`MAX`; Spec 872 |
| `SPEED_PRESETS` | `0.8`, `1.0`, `1.1` | Spec 872 |
| `FORMAT_VALUES` | `MP3`, `WAV` | `TTSGenerateIn.format` |
| `DEVICE_VALUES` | `auto`, `cuda`, `cpu`, `mps` | `ModelLoadIn.device` |
| `DURATION_WPM` | `150` words/minute at speed `1.0`; minutes = `words / (150 * speed)`; hide when `words === 0` or speed non-finite | Spec 834 |
| `WORD_COUNT` | whitespace-split tokens on current editor text | Spec 833 |
| `SENTENCE_COUNT` | segments matching `[.!?]+` on current editor text | Spec 833 |
| `FILE_LOAD_OUT` | existing `read-text-file` success `value` is `{ text: string, basename: string }`. `basename` is `path.basename(chosen)` with no directory separators. Full selected path never appears in the IPC success payload or renderer types. | Spec 106–107, 894; F3 |
| `FILE_LOAD` | `window.api.readTextFile({ maxBytes: 2_097_152 })` — dialog in main; allowed `.txt`/`.md`; denied secret paths remain. On success: replace editor text with `FILE_LOAD_OUT.text`; set `source_kind='file'`; `source_path` = `FILE_LOAD_OUT.basename`. Cancel (`ok: false`) leaves text unchanged. Update `env.d.ts` + preload return type to `Promise<FILE_LOAD_OUT>`. | Spec 106–107, 830; `ipc.ts` 297–310 |
| `CLIPBOARD_READ` | `IpcDeps.readClipboard` → Electron `clipboard.readText()`; channel stays `read-clipboard-text`. Renderer calls `window.api.readClipboardText()` only. | Spec 831; Electron clipboard; lock 6 |
| `PASTE` | Insert clipboard text at the textarea caret (or append if no selection). Sets `source_kind='inline'` and clears `source_path`. Empty clipboard is a no-op (no settings PUT). | Spec 831; index 47 |
| `PREVIEW_SPLIT` | `preview-cleanup-btn` → `POST /tts/prepare` with `PREPARE_BODY` → show `preview-raw` (current text) and `preview-cleaned` (`cleaned_text`) side-by-side. Unknown step → 422 `ERROR_SURFACE`. Blank text → POST count 0. | Spec 823; 04 249–251 |
| `ENABLED_WHEN` | Generate: `status.is_loaded` ∧ `text.trim().length ≥ 1` ∧ job status ∉ {`Generating`,`Pending`}; Cancel: job status ∈ {`Pending`,`Generating`}; Preview: `text.trim().length ≥ 1`; Unload: `status.is_loaded`; Load: row `is_downloaded` ∧ not currently loaded; Get: `!is_downloaded` ∧ runtime `state !== 'Downloading'`; Open File: job `output_path` non-null; Open Folder: job `output_path` or settings `output_path` non-empty; Browse output: always | Spec 875; 04 257 |
| `CANCEL_VERB` | control id `cancel-btn` / action `tts:cancel` → `apiFetch<void>` `DELETE /tts/{id}` 204. Page has no `stop-btn`. | index 50; `tts.py` 92–96 |
| `CREATED_201` | `POST /tts/generate` → 201 `JOB_OUT`; 409 `ERROR_ENVELOPE` if no model loaded or another generate is in flight | `tts.py` 54–67, 127–155 |
| `VOID_204` | `DELETE /tts/{id}` and `POST /models/unload` → `apiFetch<void>` | Spec 132; models.py 74–82 |
| `VOICES_ENVELOPE` | `{ items: VoiceOut[] }` — unwrap `items`; fields `voice_id`, `language`, `gender`, `style_description` only | `VoiceListOut` |
| `LANG_FILTER` | `language-select` options = unique `VoiceOut.language` values from `VOICES_ENVELOPE`. Cards shown for the selected language. Choosing a voice does **not** send `lang_code`. No `lang_code` input exists in `PAGE_FILES`. | Spec 851–866; `VoiceOut` |
| `DEFAULT_VOICE` | `am_eric` until settings `voice` is a known `voice_id` | settings.py 67; Spec 857 |
| `CATALOG_ITEMS` | unwrap `GET /models/available` `{ items }`. `is_loaded` is **not** on the variant — only `GET /models/status`. Render every item as-is; never hardcode or filter catalog ids. | `ModelVariantOut`; `SEED_VARIANTS` engine.py 23–28; lock 7 |
| `RUNTIME_BIND` | bind percent only to the row whose `id === runtime.variant_id` while `state === 'Downloading'`. Other rows stay Get/Ready. | Spec 846 |
| `DOWNLOAD_BODY` | `{ variant_id: string.min(1) }` — extra forbid; 202 `{ variant }`; 409 if another download is in flight | `ModelDownloadIn`; 04 275 |
| `LOAD_BODY` | `{ variant_id: string.min(1), device: DEVICE_VALUES }` — extra forbid | `ModelLoadIn` |
| `SETTINGS_LEAVES` | writable this MEU: `input_text`, `voice`, `speed`, `output_format`, `output_path`, `device`. Zod `.strict()` subset of `SettingsPutIn`. | `SettingsPutIn`; lock 9 |
| `SETTINGS_READ_ONLY` | `chunk_max_chars` (passed through to prepare), `models_directory` (never written here) | lock 9; index 63 |
| `OUTPUT_DEFAULT` | settings `output_path` default `~/Documents` (R3-2). Browse = `showDirectoryDialog` then `PUT /settings/tts` `{ output_path }`. Generate does **not** send `output_path` (server reads the leaf). | Spec 874, 1003; grouping R3-2 |
| `RESUME_TEXT` | on mount, GET `/settings/tts` fills the textarea from `input_text`. Debounced PUT `{ input_text }` after edit / file-load / paste. Max `1_000_000`. | Spec 894, 1006; `TTS_INPUT_TEXT_MAX` |
| `ERROR_SURFACE` | 422/409/`ApiError` shown in-page (G15); never swallow | G15 |
| `TTS_PALETTE_IDS` | `{tts:prepare, tts:generate}` | index 48–49 |
| `TTS_LOCAL_IDS` | `{tts:load_file, tts:paste, tts:browse_output, tts:cancel, tts:open_output, tts:open_output_folder, models:download, models:load, models:unload}` | index 45–47, 50–55 |
| `TTS_EVENTS` | `av-kit:tts:{prepare,generate}` dispatched from palette and page buttons; **no** `apiFetch` in `commandRegistry` | G11 |
| `TTS_COMMANDS` | `ui/src/renderer/src/features/tts/tts-commands.ts` — the single handler set for `TTS_PALETTE_IDS` | G11 |
| `PALETTE_DELIVER` | `AppShell` always-mounted listener is the production owner. It calls `TTS_COMMANDS`. Off `/tts`: navigate `#/tts` then invoke the same handler. `tts:prepare` with blank text no-ops (POST count 0). Page buttons call the same exports. Negative: listener only inside `TTSPage` → off-route no-op. | G11; MEU-21 pattern |
| `WAVE2_TESTIDS` | `tts-page`, `text-input`, `model-manager`, `voice-grid`, `generate-btn`, `speed-slider`, `cleanup-pipeline`, `preview-cleanup-btn` | Spec 1104 |
| `WAVE2_EXTRA_TESTIDS` | `load-file-btn`, `paste-btn`, `word-count`, `sentence-count`, `duration-estimate`, `preview-raw`, `preview-cleaned`, `language-select`, `format-select`, `device-select`, `output-path`, `browse-output-btn`, `cancel-btn`, `segment-progress`, `last-output`, `open-output-btn`, `open-output-folder-btn`, `loaded-model`, `unload-btn`, `model-row`, `model-get-btn`, `model-load-btn`, `voice-card`, `download-progress` | E2; §4A |
| `E2E_WAVE2` | `ui/tests/e2e/tts-generate.test.ts` (`E2E_CASES`, 6 tests) + `WAVE2_TESTIDS` / `WAVE2_EXTRA_TESTIDS` in `test-ids.ts` | Spec 1104; E2 |
| `E2E_CASES` | `W2-1` `TTS_HOME`; `W2-2` nav from `#/` via `nav-tts`; `W2-3` page-chrome EXTRA presence (`toBeVisible` on editor/pipeline/manager/generate; `E2E_ATTACHED_FIRST` on Idle `segment-progress`); `W2-4` `E2E_HAPPY_PATH` via `E2E_SEAM_INSTALL` + `E2E_SEAM_PROOF` + `E2E_SEAM_NEG`; `W2-5` `E2E_ACTUATE` after `E2E_SEAM_INSTALL` + `__e2eSeamInstalled`; `W2-6` `PALETTE_DELIVER` off-route `tts:prepare` after `E2E_SEAM_INSTALL`. Every case calls `installTtsSeam(`. | Spec 1104; E2; G11 |
| `E2E_LOCATOR_FORM` | Wave 2 locators are literal `getByTestId('<kebab-id>')` (single quotes). Comments and `test-ids.ts` literals do not satisfy `E2E_CONTROL_CENSUS`. | E2 |
| `E2E_PER_CONTROL` | The allowed method must be chained on the same locator expression: `expect(page.getByTestId('id')).toBeVisible()` or `page.getByTestId('id').click()`. Owner: `Test-HasBound`. | E2; MEU-21 R4-1 |
| `E2E_ATTACHED_FIRST` | Before any intentional hidden-state assertion, require `toBeAttached` or `toHaveCount(1)`. Presence oracles are `toBeVisible` / `toBeAttached` / `toHaveCount(1)`, never `toBeHidden` alone. | E2; Playwright `toBeHidden` |
| `E2E_SEAM_GATE` | `window.__e2eSeamInstalled === true` set in the pre-app `addInitScript` **before** any TTS `apiFetch`. | Local Canon: `api.ts` 21–27; downloader RULE-2 |
| `E2E_SEAM_LEDGER` | `window.__e2eCalls` — `{ url, method, bodyKeys }` appended on every intercepted `fetch` | downloader RULE-2 |
| `E2E_IPC_LEDGER` | `window.__e2eIpc` — `{ channel, target? }` appended on `readTextFile` / `readClipboardText` / `showDirectoryDialog` / `openPath` / `showItemInFolder` stubs | MEU-19 IPC |
| `E2E_SEAM_UNHANDLED` | HTTP 599 JSON/text body `E2E_SEAM_UNHANDLED` for any `/tts*`, `/models*`, or `/settings/tts*` request the override does not explicitly fulfill. Must not call original `fetch` for those prefixes. | downloader RULE-2; lock 11 |
| `E2E_SEAM_INSTALL` | File-level `async function installTtsSeam(page)` in `tts-generate.test.ts` (downloader `installSeam` shape). This function is the **sole** owner of `page.addInitScript(`, `window.fetch =`, protected prefixes, `599`, `new Response`, and `E2E_SEAM_UNHANDLED`. Every `E2E_CASES` test calls `installTtsSeam(` **outside string literals** before page work. | E2; downloader `installSeam`; R3-F1 |
| `E2E_SEAM` | `E2E_SEAM_INSTALL` sets `E2E_SEAM_GATE` and installs a `window.fetch` override **before** app load, then `page.reload()`. Fulfills GET `/settings/tts` leaves; GET `/tts/voices` `{ items }`; GET `/models/available` `{ items }`; GET `/models/status`; GET `/models/download-runtime`; POST `/tts/prepare` `{ cleaned_text }`; POST `/tts/generate` 201 `JOB_OUT`; GET `/tts/{id}`; DELETE `/tts/{id}` 204; POST `/models/download` 202; POST `/models/load`; POST `/models/unload` 204; PUT `/settings/tts`. Records `E2E_SEAM_LEDGER`. Fail-closed via `E2E_SEAM_UNHANDLED`. Also stubs `CLIPBOARD_READ` / `FILE_LOAD` / directory dialog into `E2E_IPC_LEDGER`. `page.route` is optional and is **not** the proof. | Local Canon; downloader RULE-2; Playwright `addInitScript` |
| `E2E_SEAM_PROOF` | Helper extracts `installTtsSeam` and requires executable calls **outside string literals** (`addInitScript(`, `window.fetch =`, `new Response`, `reload(`) plus prefixes/`599`/`E2E_SEAM_UNHANDLED`. Each W2-1…W2-6 must call `installTtsSeam(` **outside strings** (`Get-CodeWithoutStrings`). W2-5 `__e2eSeamInstalled` gate is also outside strings. Token-only / quoted `installTtsSeam(` / `toContain` blobs do not satisfy. Helper self-probes: (a) W2-4 token string with no installer call fails; (b) W2-5 Generate/Get/Load clicks with no installer call fail; (c) installer body that only returns those tokens as a string fails; (d) W2-4/W2-5 fixtures with quoted `installTtsSeam(` and quoted `__e2eSeamInstalled` fail. `page.route` is non-probative. | E2; downloader RULE-2; R3-F1 |
| `E2E_SEAM_NEG` | W2-4 issues one unhandled protected URL containing `__e2e-unhandled` (under `/tts*`, `/models*`, or `/settings/tts*`) and asserts HTTP 599 plus body/ledger `E2E_SEAM_UNHANDLED`. The override must not call original `fetch` for those prefixes. Helper requires the `E2E_SEAM_NEG` token and `__e2e-unhandled`. | F1 |
| `E2E_ACTUATE` | W2-5 clicks each interactive control and asserts **that control's own** observable in the same case: `load-file-btn`→`__e2eIpc` channel `readTextFile`; `paste-btn`→`readClipboardText`; `open-output-btn`→`openPath`; `open-output-folder-btn`→`showItemInFolder`; `browse-output-btn`→`showDirectoryDialog` + `PUT /settings/tts`; `preview-cleanup-btn`→`POST /tts/prepare`; `generate-btn`→`POST /tts/generate`; `cancel-btn`→`DELETE /tts/`; `model-get-btn`→`POST /models/download`; `model-load-btn`→`POST /models/load`; `unload-btn`→`POST /models/unload`; `voice-card`→`PUT /settings/tts` with `voice`; `language-select` / `format-select` / `device-select` `toBeVisible` (G30). Generating fixture → `segment-progress` `toBeVisible`. A generic `__e2eIpc` token does not satisfy any IPC row. Do not click disabled controls (`TRANSCRIPT_RULES` RULE-1). | E2; create-plan §4A.3; F2 |
| `E2E_HAPPY_PATH` | with `E2E_SEAM` active: fill `text-input` → Preview click → `preview-cleaned` visible from seam `cleaned_text`; Generate click (after loaded-status fixture) → `last-output` / `segment-progress` traceable to seam `JOB_OUT`. | Spec 823, 894 |
| `E2E_NO_LIVE_HF` | Wave 2 must not let Generate/Get/Load reach Kokoro or Hugging Face. Enforced by `E2E_SEAM_INSTALL` in every case (including independently launched W2-5) + `E2E_SEAM_GATE` + `E2E_SEAM_PROOF` + `E2E_SEAM_NEG`, not by `page.route`. | Local Canon `tts.py` 189–200; `models.py` download; downloader RULE-2 |
| `E2E_CONTROL_CENSUS` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-e2e-control-census.ps1` — comment-stripped `E2E_LOCATOR_FORM` + `E2E_PER_CONTROL` + `E2E_SEAM_INSTALL` + `E2E_SEAM_PROOF` + `E2E_SEAM_NEG` + `E2E_SEAM_GATE` + `E2E_ACTUATE` + `E2E_ATTACHED_FIRST`. Empty/skip tests fail. Helper rejects the R4-1 unrelated-receiver snippet, the R2-F1 token-only / no-installer self-probes, and the R3-F1 quoted-`installTtsSeam(` / quoted-gate self-probes. `toBeHidden` is not a presence oracle. | E2; create-plan §4A.3 |
| `RED_AC_IDS` | `AC-22.1` … `AC-22.24` (24). Owner: `assert-red-oracle.ps1` ui kind + `RED_JSON`. | FIC |
| `RED_TEST_TITLE` | every AC-22.N unit/integration test is a **distinct** Vitest case whose `fullName`/`title` contains exactly one `AC-22.N`. | FIC tests-first |
| `RED_JSON` | `C:/Temp/av-kit/fail-to-pass-meu-22-ui.json` from Vitest 3 `--reporter=json --outputFile`. | Vitest 3 json reporter |
| `BUILDER_PIN` | `—` while `fresh_worker: none`. | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping authority |
| `GROUPING_DONE_MARK` | Progress-table row `\| 10 \| \`p6-gui-tts-models\` \| ✅ complete \|` and Session 10 heading `✅ complete`; Sessions 11–12 stay `⬜ pending`. Applied at H2 after exec `approved` only. | grouping Progress |
| `REFLECTION_TEMPLATE` | `docs/execution/reflections/TEMPLATE.md` | closeout |
| `REFLECTION_SCHEMA` | `.agent/schemas/reflection.v1.yaml` | closeout |
| `REFLECTION_PEER_RULE` | newest `docs/execution/reflections/*-reflection.md` excluding `TEMPLATE.md`, sorted by `LastWriteTime` descending | AGENTS closeout |
| `REFLECTION_SOURCE_READ` | `C:/Temp/av-kit/reflection-source-read-meu-22.txt` with `TEMPLATE=`, `SCHEMA=`, `PEER=`, `PASS: REFLECTION_SOURCE_READ` | H2-1 |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up. Tests stay written and wired. Isolated `AVKIT_APP_DATA` (chrome RULE-1). | known-issue policy; chrome RULE-1 |
| `STATUS_COLORS` | map `JOB_STATUSES` + runtime states to CSS `@theme` tokens (no raw hex in `className`) | G31–G32 |
| `SCAN_G36_ARGS` | skip/only/todo markers under `ui/tests/unit` + `ui/tests/e2e` + `tests/` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `ui/src` | anti-placeholder |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-20-p6-gui-tts-models-MEU-22-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-20-p6-gui-tts-models` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-tts-models/` | phase `"6"` |
| `PRIOR_PLAN_SLASHES` | `docs/execution/plans/2026-08-19-p6-gui-shell/`; `docs/execution/plans/2026-08-20-p6-gui-downloader/`; `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/`; `docs/execution/plans/2026-08-20-p6-gui-transcript/` | must remain on phase `"6"` |
| `HUB_NEXT_AFTER` | `/create-plan p6-gui-settings-help` | grouping pathway #11 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p6 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-20-p6-gui-tts-models-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-22.txt` written **once** before the MEU-22 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `VITEST_ALLOW_ONLY` | `ui/vitest.config.ts` has `test.allowOnly: false`. Every `npx vitest run` passes `--allowOnly=false`. | G36 |
| `UI_ESLINT` | `npx eslint src/ tests/ --max-warnings 0` | G36 |
| `RED_ORACLE` | UI FAIL_TO_PASS text has allow-marker and no deny-marker **and** `RED_JSON` maps 24 distinct failed `assertionResults` 1:1 onto `RED_AC_IDS`. | MEU-21 r1 |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-red-oracle.ps1 -Kind ui -Receipt <text> -JsonReceipt RED_JSON` | PR-9 |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-handoff-markers.ps1` | PR-9 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `MEU22_TOUCHED` | `PAGE_FILES` + `ui/tests/unit` tts + `ui/tests/e2e/tts-generate.test.ts` + `test-ids.ts` + `AppShell.tsx` + `commandRegistry.ts` + `router.tsx` | MEU-22 files |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-22.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` is **not** modified → `--check` still run as no-drift proof. `-o` forbidden unless FAIL. | G8 skip-with-proof |
| `CHROME_RULES` | RULE-1 `AVKIT_APP_DATA` userData isolation; RULE-2 closed console must not hide `main`; RULE-3 reactive breadcrumb. Consume; do not rewind chrome. | p6-gui-zorivest-chrome reflection |
| `TRANSCRIPT_RULES` | RULE-1 do not click disabled queue/generate controls; RULE-2 keep MEU sources in-tree; RULE-3 do not rewind chrome. | p6-gui-transcript reflection |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| Domain / TTSService / ModelService / FastAPI tts+models routes | YES | MEU-12 + MEU-16 `approved`. Do not rewrite. |
| Prepare / generate 201 / cancel 204 / voices / models catalog | YES | `tts.py`, `models.py` |
| `apiFetch` + IPC + AppShell + chrome | YES | MEU-19/20/21/26 `approved` |
| TTS page at `/tts` | NO → **this MEU** | grouping Session 10 |
| Settings leaf editor / HelpCards / action audit | NO — **later MEU** | grouping Session 11 |
| MCP tools | YES — do not rewrite | MEU-17/18 `approved` |

---

## create-plan §4A — GUI Element Compliance

**Triggered:** TTS page creates `<button>`, `<textarea>`, `<select>`, `<input type="range">`, status badges, and preview panels in `ui/src/renderer/`.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens |
| Button/input/output indexes | **Absent** — map via table below |
| E2E written+wired | `E2E_WAVE2` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_ACTUATE` + `E2E_ATTACHED_FIRST` + `E2E_SEAM_INSTALL` + `E2E_SEAM_GATE` + `E2E_SEAM_PROOF` + `E2E_SEAM_NEG` + `E2E_CONTROL_CENSUS` |
| G30–G35 / E2 | G30 **applies**: `language-select`, `format-select`, `device-select` use `SelectInput` / `getG30Styles()`. G31 `bg-accent` only. G32 no raw hex in `className` (G30 inline styles excepted). G33 duration tokens. G34 variants below. G35 tiers below. E2 = `E2E_WAVE2`. |
| G11 | `PALETTE_DELIVER`: `AppShell` owns reachability; `TTS_COMMANDS` is the one fetch path |
| G16 | existing `CSP_IMG` — do not regress |
| G5 | `POLL_ACTIVE_MS` / `POLL_IDLE_MS` |
| G3 | voice catalog is 54 rows — client filter by language is in-spec; no server search API exists |
| G20 | n/a — no destructive confirm on this page (Cancel/Unload have no Spec confirm) |
| G27 | not used; `openPath` / `showItemInFolder` already allowlisted (MEU-19) |

Indexes remain absent. **Local fallback basis:** G34 text in `emerging-standards.md` (5 variants × 3 sizes). Toolbar `md`; row actions `sm`. G35 tiers T0–T1.

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Text area | textarea | md | default/focus/disabled | `text-input` | T0 |
| Load File | secondary | md | default/hover/focus | `load-file-btn` | T1 IPC |
| Paste | secondary | md | default/hover/focus | `paste-btn` | T1 IPC |
| Word / sentence / duration | output | — | hidden when empty | `word-count`, `sentence-count`, `duration-estimate` | T0 |
| Cleanup toggles | checkbox | sm | default/disabled | `cleanup-pipeline` + `cleanup-{step}` | T0 |
| Preview cleaned | secondary | md | default/hover/focus/disabled | `preview-cleanup-btn` | T1 POST prepare |
| Preview panes | output | — | hidden until preview | `preview-raw`, `preview-cleaned` | T1 |
| Language | `SelectInput` | md | G30 | `language-select` | T0 |
| Voice card | secondary | sm | default/selected | `voice-card` | T1 PUT voice |
| Voice grid | output | — | default | `voice-grid` | T1 GET voices |
| Speed | range | md | 0.5–2.0 / 0.1 | `speed-slider` | T1 PUT speed |
| Format | `SelectInput` | md | G30 | `format-select` | T1 PUT format |
| Output path | output + browse | md | default | `output-path`, `browse-output-btn` | T1 dialog + PUT |
| Generate | primary | md | default/hover/focus/disabled/loading | `generate-btn` | T1 201/409 |
| Cancel | secondary | md | default/hover/focus/disabled | `cancel-btn` | T1 204 |
| Segment progress | output | — | hidden when idle | `segment-progress` | T1 poll |
| Last output | output | — | hidden until path | `last-output` | T1 |
| Open file / folder | ghost | sm | default/hover/focus/disabled | `open-output-btn`, `open-output-folder-btn` | T1 IPC |
| Model manager | output | — | default | `model-manager` | T1 |
| Loaded / unload | status + secondary | sm | default/disabled | `loaded-model`, `unload-btn` | T1 204 |
| Model row / Get / Load | output + secondary | sm | default/disabled | `model-row`, `model-get-btn`, `model-load-btn` | T1 202/200 |
| Download % | output | — | hidden unless bound row | `download-progress` | T1 runtime |
| Device | `SelectInput` | sm | G30; shown on load | `device-select` | T1 POST load |

---

## MEU-22 — `gui-tts-models`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Prepare form → REST | client Zod `.strict()` `PREPARE_BODY` then `TTSPrepareIn` | `enabled_steps` ⊆ `PREPARE_STEPS`; `chunk_max_chars` > 0 if sent | extra forbid | blank text: POST 0; unknown step 422 `ERROR_SURFACE` | n/a | 04 249–251 |
| Generate form → REST | client Zod `.strict()` `GENERATE_BODY` then `TTSGenerateIn` | text min 1; speed 0.5–2.0; format `FORMAT_VALUES`; `source_kind` `inline`\|`file` | extra forbid | no POST if `ENABLED_WHEN` false; 409 no model / in-flight | n/a | 04 253–257 |
| Job poll | `TTSJobOut` | no full text | ignore unknown out fields | 404/422 `ERROR_SURFACE` | GET only | 04 259–261 |
| Cancel | no body | 204 void | n/a | 404 `ERROR_SURFACE` | n/a | `tts.py` 92–96 |
| Voices | `VoiceListOut` | unwrap `items` | ignore unknown | `ERROR_SURFACE` | GET only | `VoiceListOut` |
| Model download | Zod `.strict()` `DOWNLOAD_BODY` | `variant_id` min 1 | extra forbid | 422; 409 in-flight | n/a | 04 275 |
| Model load | Zod `.strict()` `LOAD_BODY` | `DEVICE_VALUES` | extra forbid | 422 | n/a | `ModelLoadIn` |
| Model unload | `EmptyIn` / no body | 204 void | extra forbid if body sent | `ERROR_SURFACE` | n/a | models.py 74–82 |
| Settings TTS PUT | Zod `.strict()` `SETTINGS_LEAVES` then `SettingsPutIn` | speed range; format `FORMAT_VALUES`; device `DEVICE_VALUES`; `input_text` ≤ 1e6 | extra forbid | 422; never send `models_directory` | same leaves on resume + browse | lock 9 |
| Settings TTS GET | namespace dict | read `SETTINGS_LEAVES` + `SETTINGS_READ_ONLY` | ignore unknown leaves | missing `output_path` → show `OUTPUT_DEFAULT` literal | read + write this MEU | settings.py 67–75 |
| Load File | existing IPC Zod `maxBytes`; success `FILE_LOAD_OUT` | `.txt`/`.md`; 2 MiB; `basename` has no `/` or `\\` | `.strict()` | cancel / denied → no editor change; full path in success value → fail | n/a | `FILE_LOAD` |
| Paste | existing IPC `read-clipboard-text` | no payload | `.strict()` | empty string → no-op | n/a | `CLIPBOARD_READ` |
| Browse output | existing `show-directory-dialog` | no payload | `.strict()` | cancel → no PUT | n/a | index 46 |
| Open file/folder | existing IPC Zod | `target` min 1; exe/URL deny remains | `.strict()` | handler reject | n/a | MEU-19 `IPC_SCHEMAS` |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-22.1 | integration | **Control `TTS_HOME`.** Observable: hash `#/tts` + `tts-page` + `text-input`. Chain: `router.tsx` `/tts` → `TTSPage` → `AppShell` outlet. Negative: route still `LazyPlaceholder` / “Connecting…” with `text-input` count 0 → fail. | Spec 194–197, 741; grouping Session 10 | keep placeholder as the page |
| AC-22.2 | unit | **Control `WORD_COUNT` + `SENTENCE_COUNT` + `DURATION_WPM`.** Observable: helper return + `word-count` / `sentence-count` / `duration-estimate` text. Chain: textarea value → stats. Negative: treat duration as independent of speed; show duration when words=0 → fail. | Spec 832–834 | `words/150` ignoring speed |
| AC-22.3 | integration | **Control `FILE_LOAD` + `FILE_LOAD_OUT`.** Observable: IPC invoke `read-text-file` with `{ maxBytes: 2097152 }` only (no path key); success value `{ text, basename }`; editor text = `text`; next generate `source_kind='file'` and `source_path` equals `basename`. Chain: `load-file-btn` → `window.api.readTextFile` → main dialog → `FILE_LOAD_OUT`. Negative: renderer passes `{ path: 'C:\\…' }`; success value contains `\\` or `/`; `source_path` is a full path; handler still returns a bare string → fail. | Spec 106–107, 830, 894; F3 | `readTextFile({ path })`; string-only IPC value |
| AC-22.4 | integration | **Control `PASTE` + `CLIPBOARD_READ`.** Observable: main `read-clipboard-text` returns `deps.readClipboard()` (not `''`); renderer insert at caret; generate `source_kind='inline'`. Chain: `index.ts` `clipboard.readText` → `handleIpc` → `paste-btn`. Negative: handler still returns `''` while deps supply text; `navigator.clipboard` in `PAGE_FILES` → fail. | Spec 831; Electron clipboard; lock 6 | stub empty return; renderer clipboard API |
| AC-22.5 | unit | **Control `PREPARE_STEPS` + `PREPARE_DEFAULT_ON`.** Observable: 11 checkboxes; `chapter_markers` unchecked; others checked. Chain: defaults → `cleanup-pipeline`. Negative: omit `kokoro`; default chapter on → fail. | Spec 809–821; `prepare.py` 10–24 | 10 steps only |
| AC-22.6 | integration | **Control `PREPARE_BODY` + `PREVIEW_SPLIT`.** Observable: `POST /tts/prepare` JSON keys exactly `{ text, enabled_steps }` plus optional `chunk_max_chars` from settings; `preview-cleaned` shows `cleaned_text`; `preview-raw` shows pre-prepare text. Chain: Preview → client `.strict()` → `apiFetch`. Blank text: POST count 0. Extra field stripped/rejected before fetch. | Spec 823; 04 249–251 | POST `{ text, enabled_steps, lang_code }` |
| AC-22.7 | integration | **Control `GENERATE_BODY` + `CREATED_201` + `JOB_OUT`.** Observable: `POST /tts/generate` 201; body keys exactly `GENERATE_BODY`; response has `text_preview`/`text_hash` and no full text field. Chain: Generate → `TTS_COMMANDS` → `apiFetch`. Negative: send `output_path` or `lang_code`; persist full text on the job card → fail. | Spec 894; 04 253–261 | `{ …, output_path: 'C:\\' }` |
| AC-22.8 | unit | **Control `POLL_ACTIVE_MS` / `POLL_IDLE_MS` + `JOB_POLL` + `QUERY_JOB`.** Observable: `refetchInterval(query)` return. Chain: job `Generating` or runtime `Downloading` → 1000 else 5000 (including `data` undefined). No `GET /tts` list call. | Spec 846; [Query v5 refetchInterval](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery); lock 3 | v4 `(data, query)` signature; `GET /tts` |
| AC-22.9 | integration | **Control `ENABLED_WHEN` + `CANCEL_VERB` + `VOID_204`.** Observable: button `disabled` + fetch method/path. Chain: loaded+text → Generate 201; Generating → Cancel DELETE 204. Negative: Generate while unloaded still POSTs; page contains `stop-btn` / `tts:stop` → fail. | Spec 875; index 50; lock 4 | always-enabled Generate; Stop label |
| AC-22.10 | integration | **Control `SEGMENT` progress.** Observable: `segment-progress` text uses `segments_done`/`segments_total` from `JOB_OUT`. Chain: `GET /tts/{id}` → bar. Negative: invent a second progress store; treat `fraction` as a job field → fail. | Spec 882; `TTSJobOut` | bind `runtime.fraction` to generate bar |
| AC-22.11 | integration | **Control `VOICES_ENVELOPE` + `LANG_FILTER` + `DEFAULT_VOICE`.** Observable: `voice-grid` cards from `items`; `language-select` unique languages; selected voice PUT `{ voice }`. Chain: GET `/tts/voices` → filter → card click → settings. Negative: `lang_code` input or generate body key; hardcode spec “English (US)” instead of `VoiceOut.language` → fail. | Spec 851–866; lock 8 | user-set `lang_code` |
| AC-22.12 | unit | **Control `SPEED_RANGE` + `FORMAT_VALUES` + G30.** Observable: slider min/max/step; format `SelectInput` options MP3/WAV; PUT `{ speed }` / `{ output_format }`. Chain: slider/select → `SETTINGS_LEAVES`. Negative: speed 2.5 POSTs; raw `<select>` without `getG30Styles`/`SelectInput` → fail. | Spec 872–873; G30 | `speed: 3` |
| AC-22.13 | integration | **Control `OUTPUT_DEFAULT` + `tts:browse_output`.** Observable: `output-path` shows settings value defaulting to `~/Documents`; Browse → `showDirectoryDialog` → PUT `{ output_path }` only. Chain: `browse-output-btn` → IPC → `apiFetch` PUT. Negative: generate body includes `output_path`; Browse writes `models_directory` → fail. | Spec 874, 1003; R3-2; index 46 | Settings models-dir browse here |
| AC-22.14 | integration | **Control `RESUME_TEXT`.** Observable: GET `/settings/tts` hydrates `text-input`; edit → PUT `{ input_text }` only (plus other dirty `SETTINGS_LEAVES` if changed). Chain: mount → GET → debounce PUT. Negative: PUT includes `models_directory` or unknown key → fail. | Spec 894, 1006 | `{ input_text, models_directory }` |
| AC-22.15 | integration | **Control model status + `VOID_204` unload.** Observable: `loaded-model` from `GET /models/status` (`is_loaded`, device, memory); Unload → `POST /models/unload` 204. Chain: `QUERY_STATUS` → `unload-btn`. Negative: read `is_loaded` from `CATALOG_ITEMS` row → fail. | Spec 842–848; models.py 74–96 | `variant.is_loaded` |
| AC-22.16 | integration | **Control `CATALOG_ITEMS` + `DOWNLOAD_BODY` + `RUNTIME_BIND`.** Observable: one `model-row` per `items[]`; `model-get-btn` → POST `{ variant_id }`; `download-progress` only on matching `runtime.variant_id` while `Downloading`. Chain: available + runtime queries. Negative: hardcode/filter catalog ids; show percent on every row → fail. | Spec 845–846; lock 7 | hardcoded id list |
| AC-22.17 | integration | **Control `LOAD_BODY` + `DEVICE_VALUES`.** Observable: Load → POST `{ variant_id, device }`; `device-select` is `SelectInput` G30. Chain: row Load → `apiFetch`. Negative: omit `device`; send `gpu` → fail. | Spec 847–849; `ModelLoadIn` | `{ variant_id }` only |
| AC-22.18 | integration | **Control `ERROR_SURFACE`.** Observable: in-page error text. Chain: `apiFetch` throw `ApiError` 422/409 → G15 banner. Negative: `.catch(() => undefined)` on Generate/Get → fail. | G15; tts.py 128, 155 | swallow 409 |
| AC-22.19 | integration | **Control `TTS_PALETTE_IDS` + `PALETTE_DELIVER`.** Observable: registry ids + event name + `AppShell` listener + `TTS_COMMANDS` (same function as the page button). Off `/tts` (`#/`): `tts:prepare` navigates to `#/tts` then invokes prepare (blank → POST 0). Negative: listener only inside `TTSPage`; palette `apiFetch` second path → fail. | index 48–49; G11 | page-only listener |
| AC-22.20 | integration | **Control `TTS_LOCAL_IDS`.** Observable: testids + handler call. Load/Paste/Browse/Cancel/Open file/folder/Get/Load/Unload exist. `settings:browse_models_dir` **not** on this page. | index 45–55, 63 | Settings models Browse here |
| AC-22.21 | integration | **Control completed opens.** Observable: Open File IPC `open-path` with job `output_path`; Open Folder `show-item-in-folder` with that path (or settings `output_path` if job path null). Disabled when both empty. Negative: open URL or exe still denied (MEU-19). | index 51–52; MEU-19 F4 | bypass exe deny |
| AC-22.22 | integration | Wave 2 E2E **written and wired** (`E2E_WAVE2`, `E2E_CASES` W2-1…W2-6, `E2E_PER_CONTROL`, `E2E_ACTUATE`, `E2E_ATTACHED_FIRST`, `E2E_CONTROL_CENSUS`, `E2E_SEAM_INSTALL`, `E2E_SEAM`, `E2E_SEAM_GATE`, `E2E_SEAM_PROOF`, `E2E_SEAM_NEG`). Isolated `AVKIT_APP_DATA`. `E2E_NO_LIVE_HF` via `E2E_SEAM_INSTALL` + `E2E_HAPPY_PATH`. Sandbox no-display → `[B]` `E2E_SANDBOX`; files still exist. Spec 1104’s “6 tests” is the wave **minimum**; six cases are the E2 per-control bind. | Spec 1104, 1199; E2; downloader RULE-2; R3-F1 | unbound locator; `page.route`-only seam; token-only W2-4; quoted `installTtsSeam(`; quoted `__e2eSeamInstalled`; W2-5 without executable installer call; `toBeHidden` as presence |
| AC-22.23 | unit | G36 / anti-placeholder on `MEU22_TOUCHED` + `CHROME_RULES` / `TRANSCRIPT_RULES` not rewound. No `test.skip` / `.only`. OpenAPI `--check` exit 0 (no `packages/api/` edits). MCP tools untouched. | G36; G8; grouping | skip a Red test to go green; regenerate OpenAPI “just in case” |
| AC-22.24 | unit | `STATUS_COLORS` / G31–G32. No raw hex in `className`. New selects use `SelectInput`. `SPEED_PRESETS` buttons set slider to 0.8/1.0/1.1 without leaving `SPEED_RANGE`. | G30–G32; Spec 872 | `className="... #50fa7b"` |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Layout editor + pipeline + manager + generate bar | Spec | `06-gui.md` 741–894 |
| 11 prepare steps + defaults | Spec + Local Canon | 809–821; `PREPARE_STEP_IDS` |
| Preview `POST /tts/prepare` | Spec | 823; 04 243 |
| File-load dialog-only | Spec | 106–107, 830, 894 |
| Paste via IPC | Spec | 831 |
| Clipboard channel currently empty | Local Canon | `ipc.ts` 289–290 → `CLIPBOARD_READ` |
| Voices + hidden lang_code | Spec + Local Canon | 851–866; `VoiceOut` |
| Language label mismatch | Local Canon | `LANG_BY_PREFIX` vs spec table → `LANG_FILTER` |
| Speed / format / `~/Documents` | Spec | 872–874, 1003; R3-2 |
| Generate 201 + poll + cancel 204 | Spec + Local Canon | 881–894; `tts.py` |
| No full text on job | Spec + Local Canon | 894; `TTSJobOut` |
| Resume `input_text` | Spec | 894, 1006 |
| Model manager + runtime bind | Spec | 836–849 |
| Catalog rows as-is | Local Canon | `CATALOG_ITEMS` renders `GET /models/available` `items`; `SEED_VARIANTS` is four rows |
| Query v5 `refetchInterval(query)` | Research-backed | [useQuery](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) |
| Clipboard read API | Research-backed | [Electron `clipboard.readText`](https://www.electronjs.org/docs/latest/api/clipboard) |
| Wire / 422 / extra forbid | Local Canon | MEU-16 schemas |
| Palette tts ids | Spec | index 48–49 |
| E2E wave 3 | Spec + E2 | 1104; six cases |
| No live HF/Kokoro in Wave 2 | Local Canon + Research-backed | `tts.py` 189–200; downloader RULE-2; Playwright `addInitScript` |
| 4A indexes absent | Local Canon | G30–G35 |
| Chrome / transcript RULE-1/2/3 | Local Canon | prior reflections |
| Settings models Browse | Local Canon | index 63 → MEU-23 |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/features/tts/*` | new | page, hooks, stats, prepare, voices, models, `TTS_COMMANDS` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `PALETTE_DELIVER` listeners for `TTS_EVENTS` (keep download/transcript) |
| `ui/src/renderer/src/router.tsx` | modify | `/tts` → `TTSPage` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `TTS_PALETTE_IDS` + events (no `apiFetch`); category `tts` |
| `ui/src/main/ipc.ts` | modify | `CLIPBOARD_READ` via `IpcDeps.readClipboard`; `read-text-file` success `value` = `FILE_LOAD_OUT` |
| `ui/src/main/preload.ts` | modify | `readTextFile` type surface `Promise<FILE_LOAD_OUT>` (existing channel) |
| `ui/src/renderer/src/env.d.ts` | modify | `readTextFile` return type `Promise<FILE_LOAD_OUT>` |
| `ui/src/main/index.ts` | modify | wire `clipboard.readText` into deps |
| `ui/src/renderer/src/styles.css` | modify | `STATUS_COLORS` tokens for TTS badges if missing |
| `ui/tests/unit/tts-*.test.ts` | new | AC-22.* |
| `ui/tests/unit` ipc tests | modify | clipboard read no longer hard-empty |
| `ui/tests/e2e/test-ids.ts` | modify | WAVE2 + EXTRA |
| `ui/tests/e2e/tts-generate.test.ts` | new | `E2E_CASES` (6) + `E2E_SEAM` |
| `ui/tests/e2e/fixtures/` | modify | tts/models envelopes |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-22; `HUB_NEXT_AFTER` |
| `GROUPING_FILE` | modify at H2 | `GROUPING_DONE_MARK` after exec `approved` only |
| `docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-*.ps1` | new | `RED_ORACLE_CHECK`, `HANDOFF_MARKER_CHECK`, `E2E_CONTROL_CENSUS` |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Settings page cards / HelpCards / bidirectional action audit | deferred | MEU-23 | grouping Session 11; `gui-actions-index.md` 56–72 |
| `settings:browse_models_dir` / `chunk_max_chars` editor | deferred | MEU-23 | index 63; Spec 945 |
| PyInstaller / NSIS | deferred | MEU-24, MEU-25 | grouping Session 12 |
| Rewrite FastAPI routers / OpenAPI routes | out-of-scope | — | grouping Session 10; MEU-16 approved |
| Rewrite MCP tools | out-of-scope | — | MEU-17/18 approved |
| Rewind / restyle MEU-26 chrome | out-of-scope | — | chrome reflection Next Day Outline |
| SSE / OCR Part 1 / multi-file TTS / MCP Guard | out-of-scope | — | `06-gui.md` 1167–1169 |
| Invent new MEU IDs | out-of-scope | — | grouping §4 |
| Hardcode or filter catalog rows | out-of-scope | — | Local Canon `CATALOG_ITEMS` |
| Live Hugging Face / Kokoro in agent E2E | out-of-scope | — | Local Canon `tts.py` 189–200; `E2E_SEAM` |
| TTS job queue / `{ items, processor }` | out-of-scope | — | no `GET /tts` list in 04 243–247 |
| New IPC channel names | out-of-scope | — | MEU-19 already registered `read-clipboard-text` / `read-text-file` / `show-directory-dialog` |
| Session 8c console polish | out-of-scope | — | grouping Session 8c stays pending; Human-approved insert after MEU-26 |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-22 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"6"` **without removing** `PRIOR_PLAN_SLASHES`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 1–9 links. Do not hand-edit AUTOGEN tables.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-20-p6-gui-tts-models'; SLASH=PLAN+'/'; PRIORS=('docs/execution/plans/2026-08-19-p6-gui-shell/','docs/execution/plans/2026-08-20-p6-gui-downloader/','docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/','docs/execution/plans/2026-08-20-p6-gui-transcript/'); NEXT='/create-plan p6-gui-settings-help'; MEUS=('MEU-22',); data=load(); p6=next(p for p in data['phases'] if str(p['id'])=='6'); eps=list(p6.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 6 missing PLAN_FOLDER_SLASH'); miss_prior=next((p for p in PRIORS if p not in eps), None); miss_prior is not None and sys.exit('phase 6 missing '+miss_prior); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../../.agent/docs/output-evidence-policy.md).

### 1. UI type / unit / lint / build
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/ui-verify.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-verify.txt | Select-Object -Last 40; exit $code
```

### 2. Python regression (no API edits expected)
```powershell
rtk proxy uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py tests/e2e tests/integration/test_api_wiring.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p6-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p6-regression.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI no-drift
```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### 4. `HANDOFF_MARKER_CHECK`
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-handoff-markers.ps1 *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

### 5. E2E control census + prior waves + wave 2
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-tts-models/assert-e2e-control-census.ps1 *> C:/Temp/av-kit/e2e-control-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/e2e-control-census.txt; exit $code }; rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts download-queue.test.ts transcript-queue.test.ts tts-generate.test.ts console-panel.test.ts console-chrome.test.ts command-palette-nav.spec.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave2.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave2.txt | Select-Object -Last 40; exit $code
```

### Stop conditions

- Plan review cap 3 without `approved`
- Exec review cap 6 without `approved`
- All reviewer rungs rate-limited
- Human-decision gate
- Genuine `[B]` with receipt (E2E no-display is valid `[B]` only for the **run**)

---

## Open Questions

None that block. Locks 2–11 resolve the forks.

| Question | Option | Source | Pros | Cons | Rec |
|----------|--------|--------|------|------|-----|
| TTS list widget | `JOB_POLL` single job | 04 243–247 | matches API | cannot reuse transcript cards | ✅ |
| | Invent `{ items, processor }` | MEU-21 | shared hook | no list route | ❌ |
| Stop vs Cancel | `CANCEL_VERB` | index 50 | matches DELETE | name differs from transcript Stop | ✅ |
| | Reuse `stop-btn` | MEU-21 | shared testid | wrong action id | ❌ |
| Catalog rows | `CATALOG_ITEMS` | `SEED_VARIANTS` (four rows) | honest to API | mockup is one snapshot | ✅ |
| | Hardcode or filter ids | Spec 845 | matches one mockup | drifts from `GET /models/available` | ❌ |
| Language labels | `LANG_FILTER` from `VoiceOut.language` | `voices.py` 68–78 | matches GET | mockup says “English (US)” | ✅ |
| | Hardcode spec table | Spec 856–864 | prettier labels | drift from `VoiceOut` | ❌ |
| Clipboard | `CLIPBOARD_READ` on existing channel | Spec 831; [Electron clipboard](https://www.electronjs.org/docs/latest/api/clipboard) | Paste works | touches main | ✅ |
| | Leave stub `''` | `ipc.ts` 289–290 | thinner | `tts:paste` dead | ❌ |

---

## Research References

- [TanStack Query v5 `useQuery` / `refetchInterval`](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery)
- [TanStack Query v5 polling](https://tanstack.com/query/v5/docs/framework/react/guides/polling)
- [Playwright `page.addInitScript`](https://playwright.dev/docs/api/class-page#page-add-init-script)
- [Playwright `toBeHidden` (absent node passes)](https://playwright.dev/docs/api/class-locatorassertions#locator-assertions-to-be-hidden)
- [Electron `clipboard.readText`](https://www.electronjs.org/docs/latest/api/clipboard)
- [06-gui.md](../../../build-plan/06-gui.md) §TTS
- [04-rest-api.md](../../../build-plan/04-rest-api.md) TTS + models routes
- [gui-actions-index.md](../../../build-plan/gui-actions-index.md)
- `.agent/docs/emerging-standards.md` G5, G11, G15, G30–G36, E2
- p6-gui-transcript approved implementation + reflection RULE-1/2/3
- p6-gui-downloader reflection RULE-2 (renderer fetch seam)
- p6-gui-zorivest-chrome reflection RULE-1/2/3
