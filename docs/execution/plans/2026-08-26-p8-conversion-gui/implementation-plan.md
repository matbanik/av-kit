---
project: "2026-08-26-p8-conversion-gui"
date: "2026-08-26"
source: "docs/build-plan/08-video-conversion.md"
meus: ["MEU-33"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 8 Conversion GUI

> **Project**: `2026-08-26-p8-conversion-gui`
> **Build Plan Section(s)**: [08-video-conversion.md](../../../build-plan/08-video-conversion.md) §Convert Page + §GUI implementation notes; [06-gui.md](../../../build-plan/06-gui.md) Wave 8; [gui-actions-index.md](../../../build-plan/gui-actions-index.md) `convert:*`
> **Status**: `draft`
> **Grouping**: [2026-08-24-p8-video-conversion-session-grouping.md](../../../../.agent/context/grouping/2026-08-24-p8-video-conversion-session-grouping.md) Session 15 — MEU-33 only

---

## Goal

Ship the **Convert page** (`CONVERT_HOME`) as a Downloader-shaped queue: rail item under TTS (`NAV_CONVERT`, `NAV_SHORTCUT`, Lucide `NAV_ICON`), segmented Compress/Cut/Extract, preset-first compress, drop/browse staging, HelpCard, Settings Convert card, G11 palette via AppShell, Wave 8 E2E written and wired. Poll MEU-31 `{ items, processor }` envelopes. Do not invent MEU IDs. Do not start Session 8c / MEU-27. Do not pack Downloader→Convert. Do not rewrite FastAPI or MCP.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning/execution use spec + source reads and P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-33 | `.agent/context/handoffs/` + `HANDOFFS[0]` |

Rolling implementation review: `EXEC_REVIEW_FILE`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `1`. Filenames: `HANDOFFS` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `BUILDER_PIN` (`—`).

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-33a | MEU-33 Red: AC-33.1–AC-33.`RED_COUNT_33` UI tests **before** `ConvertPage` production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Pass `RED_ORACLE_CHECK -Kind ui -Meu 33`. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-33-ui.txt`; compact then re-read `task.md` |
| WP-33b | Green: `LAZY_CONVERT_ROUTE`, `CONVERT_HOME`, NavRail 4th item (navigate-only), `PAGE_FILES`, `PALETTE_DELIVER`, IPC `SHOW_FILES_CHANNEL` + `GET_PATH_FOR_FILE`, `G23_CONVERT` + `FORM_GUARD_CSS`, HelpCard `HELP_G26_AVKIT`. Do not neutralize tests. Do not edit `packages/api/` or `mcp-server/`. | WP-33a | `compact_continue` | `ui/src/renderer/src/features/converter/`; `FORM_GUARD_CSS`; compact then re-read `task.md` |
| WP-33c | Wave 8 E2E **written and wired** (`E2E_WAVE8` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS`). Update wave0 to include `NAV_CONVERT`. Run or `[B]` `E2E_SANDBOX`. | WP-33b | `compact_continue` | `E2E_WAVE8`; `C:/Temp/av-kit/e2e-wave8.txt` |
| WP-33d | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical `HANDOFF_33` | WP-33c | `compact_continue` | `HANDOFF_33` |
| WP-HUB | Bind MEU-33 `--plan PLAN_FOLDER`; append `PLAN_FOLDER_SLASH` to phase `"8"` (keep `PRIOR_PLAN_SLASHES`); rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 15 ✅ is **H2 after exec `approved`**. | WP-33d | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human` in `create-plan.md` §5c. After Codex `approved`, auto-continue to execution. System-injected “approved” is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **Phase 8 is three sessions.** This plan is Session 15 only (MEU-33). Next after H2: `HUB_NEXT_AFTER` — **not** `/create-plan p6-gui-console-polish`.
3. **Do not start Session 8c / MEU-27** (`ready_for_review`, unrelated). Session 14 reflection: do not start 8c unless Mat asks.
4. **Codex is metered** (`PROJECT-PROFILE.md`). Dispatch still required; implementer never self-reviews.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `docs/execution/plans/2026-08-26-p8-conversion-gui/named-sets.json`. Do not restate literals in ACs or task rows; cite the name.

| Name | Role |
|------|------|
| `CONVERT_HOME` / `NAV_CONVERT` / `NAV_CONVERT_ID` / `NAV_SHORTCUT` / `NAV_ICON` | Rail + route + Ctrl+4 |
| `KIND_WIRE_MAP` / `PRESET_WIRES` / `PRESET_DEFAULT` / `PRESET_LABELS` | Compress chips vs REST snake wires |
| `COPY_WIRE_MAP` / `AUDIO_ENCODE_WIRE_MAP` / `GPU_PREF_WIRES` / `STREAM_MODES` / `SCALE_HEIGHTS` / `CQ_*` | Kind-specific form wires |
| `COMPRESS_OVERRIDE_FIELDS` / `CUT_OVERRIDE_FIELDS` / `EXTRACT_OVERRIDE_FIELDS` | Optional create fields |
| `LIST_ENVELOPE` / `QUERY_KEY` / `POLL_*` / `PROCESSOR_STATES` / `JOB_STATUSES` | Queue poll (no SABR statuses) |
| `CONVERT_PALETTE_IDS` / `CONVERT_LOCAL_IDS` / `CONVERT_EVENTS` / `NAVIGATE_AND_DELIVER` | G11 + Session 14 RULE-3 |
| `SHOW_FILES_CHANNEL` / `SHOW_FILES_PROPERTIES` / `GET_PATH_FOR_FILE` / `E2E_FILES_STUB` | Multi-file browse + drop paths |
| `SETTING_NS` / `CONVERTER_KEYS` / `CONVERTER_DEFAULTS` | Settings card + page output/skip |
| `WAVE8_*` / `E2E_CASES` / `WAVE8_VISUAL_ONLY` / `WAVE8_INTERACT_BIND` / `WAVE8_W8_3_*` / `WAVE8_W8_4_CONFIRM` / `WAVE8_W8_5_ENABLED` / `WAVE8_POST_ZERO_ORACLE` | Wave 8 census: visual-only IDs may use visibility; every other ID needs `WAVE8_INTERACT_BIND` |
| `REORDER_BODY` | Full permutation; never `[]` (Session 14 RULE-1) |
| `LAZY_CONVERT_ROUTE` / `FORM_GUARD_CSS` / `G23_CONVERT` / `G23_SAVE_CLASS` / `G23_SAVE_LABEL_DIRTY` | Lazy `/convert` + Settings-only G23 L1+L2 |
| `HELP_FEATURE` / `HELP_CONTENT_FILE` / `HELP_G26_AVKIT` / `HELP_COLLAPSE_KEY` / `HELP_ROUTES_AFTER` | HelpCard + AppShell help:toggle |
| `HANDOFF_*` / `RED_*` / `HUB_NEXT_AFTER` / `PRIOR_PLAN_SLASHES` | Closeout + hub |
| `ROUTE_COUNT_AFTER` / `ACTION_INDEX_AFTER` | Keep Session 14 REST/MCP census (no API/MCP edits) |

---

## Implementation locks (research + local canon)

| Lock | Value | Source |
|------|-------|--------|
| Scope | MEU-33 only. No MEU-27. No Downloader→Convert. No REST/MCP edits. | grouping Session 15; Spec 535–541; Session 14 reflection |
| Route | `LAZY_CONVERT_ROUTE`: TanStack `lazyRouteComponent` for `/convert`. `router.tsx` must **not** statically import `ConvertPage`. Downloader `/` stays eager. `pendingComponent` remains `ModuleSkeleton`. | Spec 521; 06-gui.md 912; [lazyRouteComponent](https://tanstack.com/router/latest/docs/framework/react/api/router/lazyRouteComponentFunction) |
| Rail | Insert Convert **after TTS**, before Settings pin. `testid` `NAV_CONVERT`. Lucide `Film`. | Spec 53–57 |
| `NAV_SHORTCUT` | AppShell `keydown` Ctrl+4 → `navigateShell(CONVERT_HOME)` only (no convert POST). Ctrl+1–3 stay palette labels (unchanged). | Spec 37, 57; Local Canon AppShell only captures Ctrl+K today |
| Task control | Three radios `convert-task-*`. Changing task changes the options card only; **does not** clear the queue or staging paths. | Spec 120–122 |
| Presets | Five chips; default `PRESET_DEFAULT`. Display `PRESET_LABELS`; POST `PRESET_WIRES`. Changing preset **resets** Advanced to that preset’s CQ/scale/audio. | Spec 134–157 |
| Advanced | Compress-only, collapsed. CQ `CQ_MIN`–`CQ_MAX` step `CQ_STEP`; scale `SCALE_HEIGHTS` (`0` = source); audio + GPU override. `convert-gpu-refresh` lives here (chip is not a dropdown). | Spec 148–156; index `convert:gpu_refresh` |
| Cut | In/Out parsed by `parseConvertTime` (`HH:MM:SS.mmm` **or** seconds → ms). Invalid / `out_ms <= in_ms` → inline error, POST count 0. Fast default `fast_copy`. | Spec 159–166 |
| Extract | `first` / `all`. Container chosen by API. No re-encode UI. | Spec 170–179 |
| Staging | Drop + Browse fill a path list. Add POSTs that list. Empty Add → no POST. | Spec 124–132 |
| Drop paths | Preload `GET_PATH_FOR_FILE` via `webUtils.getPathForFile`. Renderer never `readFile` / never `File.path` (removed Electron 32). Empty string paths dropped. | Spec 128; [Electron webUtils](https://www.electronjs.org/docs/latest/api/web-utils); [breaking-changes File.path](https://github.com/electron/electron/blob/main/docs/breaking-changes.md) |
| Browse | **New** IPC `SHOW_FILES_CHANNEL` (`SHOW_FILES_PROPERTIES`, return `string[]`, `[]` if canceled). Do **not** change `show-file-dialog` single-string (Settings/TTS/cookies). E2E: `E2E_FILES_STUB`. | Spec 129; [dialog.showOpenDialog multiSelections](https://www.electronjs.org/docs/latest/api/dialog); Local Canon `show-file-dialog` |
| Create body | Client Zod discriminated union on `CREATE_DISCRIMINATOR`, `.strict()`, `paths.min(1)`, kind-specific fields. Extra key → no fetch. | MEU-31 `ConversionCreateIn`; Session 14 RULE-2 |
| Lists | `LIST_ENVELOPE`; `QUERY_KEY`; `POLL_ACTIVE_MS` / `POLL_IDLE_MS`; `RENDER_ALL_ITEMS`; no invented page API. | Spec 206; Local Canon MEU-20; G5 |
| Statuses | `JOB_STATUSES` only. `Paused` is processor-only. | Spec 196–200 |
| Reorder | Full permutation `REORDER_BODY`. Never PUT `{ job_ids: [] }`. | Session 14 RULE-1; `ConversionReorderIn` min_length 1 |
| Palette | `CONVERT_PALETTE_IDS` in registry dispatch `CONVERT_EVENTS`. `AppShell` always-mounted listener calls `CONVERT_COMMANDS`. `convert:add`: if staging empty → focus `convert-dropzone` (no POST); if nonempty → POST after `NAVIGATE_AND_DELIVER`. | G11; Spec 526; Session 14 RULE-3 |
| Destructive | G20 themed `createPortal` for remove **and** clear (Transcript pattern). No `window.confirm`. | G20; Local Canon `TranscriptPage.tsx` confirm portal; MCP `DESTRUCTIVE_CONVERT` |
| GPU chip | GET `/conversions/gpu` (lazy server-side). Labels: `GPU_CHIP_CHECKING` until first 200; NVENC/AMF/QSV from booleans; else `GPU_CHIP_SOFTWARE`. `ffmpeg.available === false` → `GPU_CHIP_MISSING` and Add/Start disabled. | Spec 181–190; MEU-31 `GPU_LAZY_GET` |
| Settings | New Convert card `convert-settings`. Zod `.strict()` `CONVERTER_KEYS`. **`G23_CONVERT` L1+L2** (`FORM_GUARD_CSS`, `G23_SAVE_CLASS`, `G23_SAVE_LABEL_DIRTY`). PUT only on Save — **not** `schedulePut` debounce. L3 N/A. Other settings namespaces stay MEU-23 debounce (out of this MEU). | Spec 531; G23 Settings-only mode |
| Page output/skip | Output folder + skip-existing edit the **same** converter form (`isDirty`). Persist only via Save (`convert-page-save` / `convert-settings-save`). | Spec 102; G23 L1 |
| Help | `HELP_CONTENT_FILE` + HelpCard `HELP_FEATURE`. `HELP_G26_AVKIT` (MEU-23 HelpCard ARIA + `HELP_COLLAPSE_KEY` + Spec 208–210 topics). Not TaxHelpCard learnMore/dismiss. AppShell `HELP_ROUTES_AFTER`. | Spec 208–210, 524; G26; Local Canon AC-23.15 |
| 4A indexes | `docs/gui-element-reference.md`, button/input/output indexes, `gui-standards-enforcement.md` remain **absent**. Apply `06-gui.md` + G30–G35 + `gui-actions-index.md`. | Local Canon MEU-20 §4A |
| E2E | `E2E_WAVE8` six cases; `E2E_SEAM` Playwright `page.route` on `/conversions`, `/conversions/gpu`, `/settings/converter`, `/health/dependencies`. Happy path = Browse stub → Add → row (not live FFmpeg). | Spec 529; 06-gui 1138; Playwright network mocking |
| Wave0 | Add `NAV_CONVERT` visibility. Contract supersession, not G36 neutralization. | 06-gui Wave 0 nav census |
| Closeout | Named receipts + `assert-handoff-markers.ps1` + `CHECK_EXEC_REVIEW` (`validate_closeout_artifacts.py` is not in this tree). | Local Canon p8-conversion-api-mcp |
| Keep REST/MCP | `ROUTE_COUNT_AFTER` / `ACTION_INDEX_AFTER` unchanged. | Session 14 |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| Domain / ConversionService / REST `/conversions*` | YES | MEU-28–31 `approved` |
| MCP `avkit_convert` | YES | MEU-32 `approved`. Do not rewrite. |
| `apiFetch` + AppShell + IPC allowlist | YES | MEU-19 `approved` |
| Convert page + rail + Wave 8 | NO → **this MEU** | grouping Session 15 |
| Session 8c console polish | NO — do not start | MEU-27 `ready_for_review` |

---

## create-plan §4A — GUI Element Compliance

**Triggered:** Convert page + Settings Convert card create buttons, radios, inputs, selects, badges in `ui/src/renderer/`.

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens |
| Button/input/output indexes | **Absent** — map via table below |
| E2E written+wired | `E2E_WAVE8` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS` |
| G30–G35 / E2 | G30 on Advanced/Settings `<SelectInput>`. G31 `bg-accent` only. G32 no raw hex in `className`. G33 duration tokens. G34 variants below. G35 T0–T2 (Save is T2). E2 = `E2E_WAVE8` + named Wave 8 groups. |
| G20 | portal confirm for remove/clear; no `window.confirm` |
| G11 | `PALETTE_DELIVER` in AppShell; registry does not `apiFetch` |
| G16 | existing CSP — do not regress |
| G5 | `POLL_ACTIVE_MS` / `POLL_IDLE_MS` |
| G3 | `RENDER_ALL_ITEMS` (no list search API) |
| G23 | Queue Add is create-not-persist (L1–L3 N/A). Converter **settings** (card + page output/skip) = `G23_CONVERT` L1+L2. Create `FORM_GUARD_CSS`. L3 / `UnsavedChangesModal` N/A. |
| G26 | `HELP_G26_AVKIT` (MEU-23 HelpCard ARIA + collapse persist + Spec 208–210). Not TaxHelpCard. |
| G27 | new `SHOW_FILES_CHANNEL` added to allowlist + census; `GET_PATH_FOR_FILE` is preload-only |
| 10-item enforcement doc | **Absent** — this table is the mapping |

Indexes remain absent. **Local fallback:** G34 5 variants × 3 sizes. Toolbar `md`; row actions `sm`.

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Task Compress/Cut/Extract | radio / segment | md | default/focus | `convert-task-*` | T0 layout |
| Dropzone | region | — | default/focus | `convert-dropzone` | T0 staging |
| Browse | secondary | md | default/hover/focus | `convert-browse` | T1 IPC multi paths |
| Preset chips | outline (active = primary) | md | default/hover/focus | `convert-preset-*` | T0; resets Advanced |
| Add | primary | md | default/hover/focus/disabled/loading | `convert-add` | T1 POST create |
| Advanced disclosure | ghost | sm | default | `convert-advanced` | T0 |
| GPU chip | status | — | checking / vendor / software / missing | `convert-gpu-chip` | T1 GET gpu |
| GPU refresh | secondary | sm | default/hover/disabled | `convert-gpu-refresh` | T1 POST refresh |
| Cut in/out | text | md | default/focus/invalid | `convert-cut-in`, `convert-cut-out` | T0 parse |
| Extract first/all | radio | md | default/focus | `convert-extract-*` | T0 |
| Output folder | text + browse | md | default/focus | `convert-output-dir` | T0 until Save |
| Skip existing | checkbox | md | default/focus | `convert-skip-existing` | T0 until Save |
| Convert Save | primary | md | default/dirty (`G23_SAVE_CLASS`) / pending | `convert-page-save`, `convert-settings-save` | T2 G23 L2 PUT |
| Start | primary | md | default/hover/focus/disabled | `convert-start` | T1 202/409 |
| Pause / Resume / Cancel | secondary | md | default/hover/focus/disabled | `convert-pause` etc. | T1 202 |
| Up/Down/Top/Bottom | secondary | sm | default/hover/focus/disabled | `convert-up` etc. | T1 PUT reorder |
| Reset | secondary | sm | default/hover/focus/disabled | `convert-reset` | T1 POST reset |
| Remove / Clear All | destructive | sm/md | default/hover/focus/disabled | `convert-remove`, `convert-clear-all` | T1 204 after G20 |
| Confirm / cancel | destructive / outline | sm | default | `convert-*-confirm*` | T1 |
| Open file / folder | ghost | sm | default/hover/focus/disabled | `convert-open-*` | T1 existing IPC |
| Queue table / row / summary | output | — | default | `convert-queue*` | T1 poll |
| Settings Convert card | section | — | default/dirty | `convert-settings` | T2 Save PUT |

---

## Proposed Changes

### MEU-33 — `gui-convert`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Add form → REST | client Zod `.strict()` discriminated union then `ConversionCreateIn` | `paths` min 1 absolute; `kind` ∈ `KIND_WIRE_MAP` keys; compress `preset` ∈ `PRESET_WIRES`; cut `in_ms`/`out_ms`; extract `stream_mode` ∈ `STREAM_MODES` | extra forbid (client + server) | empty staging / invalid time / extra key → POST count 0; API 422 `ERROR_SURFACE` | create only | Spec 124–132; MEU-31 schemas |
| Reorder | Zod `.strict()` `REORDER_BODY` | permutation of current ids; array `.min(1)` | extra forbid | `[]` or extra key → PUT count 0 | n/a | Session 14 RULE-1/2 |
| Start/pause/resume/cancel | empty body | no extra keys | extra forbid | 422 | n/a | MEU-31 EmptyIn |
| Settings converter PUT (page + card) | Zod `.strict()` `CONVERTER_KEYS` then `SettingsPutIn` | preset ∈ `PRESET_WIRES`; gpu ∈ `GPU_PREF_WIRES`; bool skip; string dir | extra forbid | 422 unknown key | same leaves on create and change | Spec 531; MEU-31 |
| Browse IPC | Zod `.strict()` filters optional | `SHOW_FILES_PROPERTIES` only | extra forbid | handler reject | n/a | G27 |
| Drop | preload `GET_PATH_FOR_FILE` | `File` objects only; empty path discarded | n/a | no POST on drop alone | n/a | Spec 128 |
| Queue poll | `ConversionListOut` | must have `items` + `processor` | ignore unknown out; never treat as array | `ERROR_SURFACE` | GET only | Spec 206 |
| GPU GET/POST | `GPUCapabilitiesOut` | 200 snapshot | n/a | `ERROR_SURFACE` | GET lazy; POST refresh | MEU-31 |
| Row open | existing IPC Zod | `target` min 1; exe deny remains | `.strict()` | handler reject | n/a | MEU-19 |

#### Acceptance Criteria

> Tag: `unit` or `integration`. Each control AC names observable + call chain + negative oracle.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-33.1 | integration | **Control `CONVERT_HOME` + `LAZY_CONVERT_ROUTE`.** Observable: hash `#/convert` + `convert-page`; `router.tsx` source has `lazyRouteComponent` and **no** static `import { ConvertPage }`. Chain: first navigation to `/convert` loads the Convert chunk; Downloader remains a static import. Negative: `router.tsx` still `import { ConvertPage } from './features/converter/ConvertPage'` → fail. | Spec 521; 06-gui.md 912; [lazyRouteComponent](https://tanstack.com/router/latest/docs/framework/react/api/router/lazyRouteComponentFunction) | eager static ConvertPage import |
| AC-33.2 | integration | **Control `NAV_CONVERT` + RULE-3 rail.** Observable: 4th primary after TTS; `testid` `NAV_CONVERT`; Lucide `NAV_ICON`; palette `NAV_CONVERT_ID` + `NAV_SHORTCUT`. Chain: `NavRail` click → `onNavigate(CONVERT_HOME)` → `navigateShell` **only** (zero `POST /conversions` on that tick). AppShell Ctrl+4 same: navigate, no `convert:add`. Negative: NavRail Convert click POSTs convert on the same tick → fail. | Spec 53–57; RULE-3 | three-rail Compress/Cut/Extract; sync POST on rail click |
| AC-33.3 | unit | **Control task segments.** Observable: `convert-task-compress\|cut\|extract` radios; options card swaps; queue length unchanged. Chain: page state `kind`. Negative: switching task DELETEs queue or POSTs → fail. | Spec 120–122 | cycle button / inner routes |
| AC-33.4 | unit | **Control presets.** Observable: five chips, default `PRESET_DEFAULT` selected, labels `PRESET_LABELS`, POST `preset` ∈ `PRESET_WIRES`. Changing chip resets Advanced CQ/scale/audio to catalog. Negative: POST `Balanced` / `HighQuality` / `hevc_nvenc` as preset → fail. | Spec 134–157 | domain enum on the wire |
| AC-33.5 | unit | **Control Advanced + GPU refresh.** Observable: collapsed by default; CQ `CQ_MIN`–`CQ_MAX`; scale `SCALE_HEIGHTS`; audio/gpu wires; `convert-gpu-refresh` POSTs `/conversions/gpu/refresh`. Chip is not a `<select>`. Negative: NVENC flags on the default surface → fail. | Spec 148–190 | encoder dropdown on default card |
| AC-33.6 | unit | **Control Cut/Extract fields.** Observable: cut fields visible iff Cut; extract iff Extract. `parseConvertTime` maps `HH:MM:SS.mmm` and seconds to ms; `out_ms <= in_ms` or unparsable → Add POST count 0. Extract `STREAM_MODES`. Negative: POST relative times as strings → fail. | Spec 159–179 | timeline player |
| AC-33.7 | integration | **Control staging drop/browse.** Observable: Browse invokes `SHOW_FILES_CHANNEL` (not `show-file-dialog`); drop maps files through `GET_PATH_FOR_FILE`; no `readFile` of video bytes. Empty Add: POST count 0. Chain: staging store → `CONVERT_COMMANDS.add`. Negative: `File.path` in renderer; drop auto-POSTs without Add → fail. | Spec 124–132; Electron webUtils | single-file dialog reuse |
| AC-33.8 | integration | **Control create body.** Observable: POST `/conversions` JSON keys exactly the discriminated member (no extra). Compress includes `paths`,`kind`,`preset` plus any `COMPRESS_OVERRIDE_FIELDS` actually set. Extract `all` may return N `items`. Chain: Add → Zod `.strict()` → `apiFetch`. Negative: extra `ffmpeg_args` / empty `paths: []` fetch → fail. | MEU-31; RULE-2 | untyped fetch |
| AC-33.9 | integration | **Control `LIST_ENVELOPE` + `QUERY_KEY` + poll.** Observable: hook `{ items, processor }`; `downloadPollInterval` twin: Processing → `POLL_ACTIVE_MS` else `POLL_IDLE_MS` including undefined data. Negative: `data.map` treating envelope as array → fail. | Spec 206; Query v5 `refetchInterval(query)` | v4 `(data, query)` |
| AC-33.10 | integration | **Control queue table.** Observable: columns # / Status / File / Kind / Mode / Size / Progress / Speed / ETA; rows = `items`; statuses ∈ `JOB_STATUSES`; summary counts; processor hidden when Idle. `Paused` not a row status. | Spec 192–204 | SABR columns; item status `Paused` |
| AC-33.11 | integration | **Control `ENABLED_WHEN` + processor verbs.** Observable: button `disabled` + fetch path. Start: pending ∧ Idle/Paused ∧ ffmpeg available; Pause: Processing; Resume: Paused; Cancel: Processing∨Paused; reorder bounds; Reset: selected Failed; Remove: selected; Clear: items>0. Start while Processing does not POST. | Spec 204; Local Canon MEU-20 `controlEnabled` | always-enabled Start |
| AC-33.12 | unit | **Control `REORDER_BODY`.** Observable: Up/Down/Top/Bottom send full id permutation `.min(1)`. Chain: selection → PUT `/conversions/reorder`. Negative: `{ job_ids: [] }` or selected-id-only → fail (RULE-1). | Session 14 RULE-1; Spec 204 | empty PUT |
| AC-33.13 | integration | **Control `CONVERT_PALETTE_IDS` + `PALETTE_DELIVER`.** Observable: registry ids + `CONVERT_EVENTS` + AppShell listener + same `CONVERT_COMMANDS` as page buttons. Off-route `convert:add` uses `NAVIGATE_AND_DELIVER` then focuses dropzone when staging empty (POST count 0). Negative: listener only inside `ConvertPage`; same-tick POST with navigate; palette `apiFetch` second path → fail. | G11; Spec 526; RULE-3 | page-only listener |
| AC-33.14 | integration | **Control G20 remove/clear.** Observable: destructive click opens portal (`convert-remove-confirm` / `convert-clear-confirm`); Confirm DELETEs; Cancel/backdrop/Escape does not DELETE. No `window.confirm`. | G20; Transcript portal | native confirm |
| AC-33.15 | integration | **Control GPU chip + FFmpeg gate.** Observable: GET `/conversions/gpu` on Convert mount; chip text ∈ checking / vendor / `GPU_CHIP_SOFTWARE` / `GPU_CHIP_MISSING`; Add/Start disabled when ffmpeg missing. Negative: GUI calls `wmic`; Barrier inside detect; chip is a dropdown → fail. | Spec 181–190; MEU-31 GPU GET | `wmic` |
| AC-33.16 | integration | **Control Settings Convert card + `G23_CONVERT`.** Observable: `convert-settings` + `CONVERTER_KEYS` leaves; `isDirty` vs last GET; Save (`convert-settings-save`) uses `G23_SAVE_CLASS` + `G23_SAVE_LABEL_DIRTY` when dirty; PUT `/settings/converter` Zod `.strict()` **only** on Save (fetch count 0 while dirty-unsent). Extra key rejected before fetch. Browse dir uses existing `show-directory-dialog`. Import `FORM_GUARD_CSS`. Negative: `schedulePut` debounce PUT on every keystroke; no dirty class when form ≠ GET → fail. | Spec 531; G23 L1+L2 | invent debounce-only Convert card |
| AC-33.17 | integration | **Control page output/skip as the same G23 form.** Observable: `convert-output-dir` / `convert-skip-existing` mutate converter form `isDirty`; persist only via `convert-page-save` (same PUT body as the card). Negative: checkbox PUT on change without Save → fail. | Spec 102; G23 L1 | local-only checkbox; debounce PUT |
| AC-33.18 | integration | **Control HelpCard `HELP_G26_AVKIT`.** Observable: HelpCard `HELP_FEATURE`; `aria-expanded` + `aria-controls`; `HELP_COLLAPSE_KEY`; reload restores collapse; `HELP_ROUTES_AFTER` includes `/convert`; `help:toggle` on Convert expands Convert help. Sections cover Spec 208–210 minimum topics. Negative: missing `aria-expanded`; bounce to Settings; omit topics → fail. Do **not** require TaxHelpCard `learnMoreUrl` / dismiss (MEU-23 HelpCard is the av-kit G26 surface). | Spec 524; G26; Local Canon AC-23.15 | omit HelpCard; Tax-only fields as a blocker |
| AC-33.19 | integration | **Control open file/folder.** Observable: existing IPC `open-path` / `show-item-in-folder` with row `output_path` (fallback input). Disabled when path null. Exe deny unchanged. | Spec 204; MEU-19 | bypass exe deny |
| AC-33.20 | integration | **Control `ERROR_SURFACE`.** Observable: in-page error on 422/409/`ApiError`. Negative: `.catch(() => undefined)` on Add/Start → fail. | G15 | swallow 422 |
| AC-33.21 | integration | Wave 8 E2E **written and wired** (`E2E_WAVE8`, `E2E_CASES`, `E2E_LOCATOR_FORM`, `E2E_PER_CONTROL`, `E2E_CONTROL_CENSUS`, `E2E_SEAM`). Keep visual groups. Interactive IDs are **not** satisfied by visibility alone: census requires `WAVE8_INTERACT_BIND` except `WAVE8_VISUAL_ONLY`. W8-3 also binds `WAVE8_W8_3_PRESET_CLICK`, `WAVE8_W8_3_FILL`, `WAVE8_W8_3_TOGGLE_CLICK`, `WAVE8_W8_3_ADVANCED_CLICK`, `WAVE8_W8_3_SETTINGS_INTERACT`. W8-2 `WAVE8_W8_2_CLICK` + `WAVE8_POST_ZERO_ORACLE`. W8-4 `WAVE8_W8_4_REMOVE_CLICK` + confirm **click**. W8-5 `WAVE8_W8_5_ENABLED`. Isolated `AVKIT_APP_DATA`. No live FFmpeg. Sandbox no-display → `[B]` `E2E_SANDBOX`; files still exist. Update `06-gui.md` Wave 8 count to `E2E_CUMULATIVE_AFTER`. | Spec 529; 06-gui 1138; E2 | visual-only oracles for presets/inputs/confirms/settings |
| AC-33.22 | integration | Wave0 + shell tests include `NAV_CONVERT`. `e2e-wiring.test.ts` lists it. Contract supersession of the three-item primary rail. | 06-gui Wave 0; lock Wave0 | keep three-item rail census |
| AC-33.23 | unit | G30–G35 + G36 / anti-placeholder on converter + Settings Convert + new IPC + `FORM_GUARD_CSS`. G33: no arbitrary `duration-200` / `transition-all` in converter `className` (canonical duration/easing tokens). G34: Convert buttons use `Button` `variant`/`size` from the §4A table (Add `primary` `md`; Remove `destructive`). G35: Save is T2; Add/Start T1; staging T0. No `test.skip` / `.only`. No raw hex in `className`. | G30–G35; G36 | skip a Red test; ad-hoc `bg-blue-600` button |
| AC-33.24 | integration | OpenAPI `--check` exit 0 (no `packages/api/` edits). MCP `ACTION_INDEX_AFTER` untouched. `ROUTE_COUNT_AFTER` unchanged. | G8; grouping | regen OpenAPI “just in case”; edit `convert.ts` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Rail under TTS, Ctrl+4, `/convert` | Spec | 08 53–57, 63 |
| Downloader-shaped layout / verbs | Spec + Local Canon | 08 25–37; MEU-20 page |
| Preset catalog + Advanced | Spec | 08 134–157 |
| Cut numeric / extract streams | Spec | 08 159–179; named deferral timeline |
| Drop/browse absolute paths | Spec + Research-backed | 08 124–132; Electron webUtils + dialog multiSelections |
| `{ items, processor }` poll | Spec + Local Canon | 08 206; MEU-20/31 |
| Palette G11 + RULE-3 | Local Canon | G11; Session 14 RULE-3; MEU-20 `navigateAndDeliver` |
| Empty reorder 422 | Local Canon | Session 14 RULE-1 |
| G20 portal | Local Canon | G20; Transcript confirm |
| Settings Convert card | Spec + Local Canon | 08 531; `G23_CONVERT` L1+L2 (explicit Save, not `schedulePut`) |
| Lazy `/convert` | Spec + Research-backed | 08 521; 06-gui.md 912; TanStack lazyRouteComponent |
| Wave 8 E2E | Spec | 08 529; 06-gui 1138 |
| 4A indexes absent | Local Canon | MEU-20 §4A |
| Query v5 interval | Research-backed | [useQuery refetchInterval](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) |
| Table selection | Research-backed | [TanStack Table row selection](https://tanstack.com/table/v8/docs/guide/row-selection) |
| No CUDA/wmic | Spec | 08 571–584 |
| Downloader→Convert | out-of-scope | 08 535–541 Deferred-to `—` |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `FORM_GUARD_CSS` | new | G23 L2 amber-pulse + `G23_SAVE_CLASS` |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modify | 4th primary `NAV_CONVERT` + `Film` |
| `ui/src/renderer/src/components/layout/Header.tsx` | modify | `PAGE_LABELS['/convert']` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | convert listeners + Ctrl+4 + `HELP_ROUTES_AFTER` |
| `ui/src/renderer/src/router.tsx` | modify | `LAZY_CONVERT_ROUTE` `/convert` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `NAV_CONVERT_ID` + `CONVERT_PALETTE_IDS` (events only) |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | modify | `HELP_FEATURE` in union |
| `ui/src/renderer/src/features/settings/settings-paths.ts` | modify | `converter` path |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` | modify | `converterPutSchema` `.strict()` |
| `ui/src/renderer/src/features/settings/useSettingsPage.ts` | modify | converter query + PUT |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | Convert card |
| `ui/src/main/ipc.ts` | modify | `SHOW_FILES_CHANNEL` schema + handler |
| `ui/src/main/preload.ts` | modify | `showFilesDialog` + `getPathForFile` |
| `ui/src/main/index.ts` | modify | multi `showOpenDialog`; E2E stub `E2E_FILES_STUB` |
| `ui/src/renderer/src/env.d.ts` | modify | new API types |
| `ui/tests/unit/ipc-channels.ts` | modify | census channel |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify | converter sources + convert testids |
| `ui/tests/unit/convert-*.test.ts` | new | AC-33.* |
| `ui/tests/unit/settings-page.test.ts` | modify | Convert card |
| `ui/tests/unit/app-shell-wiring.test.ts` | modify | nav-convert + convert events |
| `ui/tests/unit/command-palette.test.ts` | modify | convert palette ids |
| `ui/tests/unit/shell-home.test.ts` | modify | four primary nav items |
| `ui/tests/unit/e2e-wiring.test.ts` | modify | Wave 8 files + nav-convert |
| `ui/tests/e2e/test-ids.ts` | modify | `WAVE8_TESTIDS` + `WAVE8_EXTRA_TESTIDS` |
| `ui/tests/e2e/launch.test.ts` | modify | `NAV_CONVERT` visible |
| `E2E_WAVE8` | new | W8-1…W8-6 + `E2E_SEAM` |
| `docs/build-plan/06-gui.md` | modify | Wave 8 cumulative `E2E_CUMULATIVE_AFTER` |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-33; `HUB_NEXT_AFTER` |
| `GROUPING_FILE` | modify at H2 | `GROUPING_DONE_MARK` after exec `approved` only |
| `docs/execution/plans/2026-08-26-p8-conversion-gui/assert-*.ps1` | new | red oracle, handoff markers/ACs, E2E census |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Downloader Done → Add to Convert | out-of-scope | — | [08-video-conversion.md](../../../build-plan/08-video-conversion.md) 535–541 named deferral; Deferred-to is `—`, not MEU-33 |
| Extract audio → Transcript / TTS | out-of-scope | — | same table 535–541 |
| Timeline player / split-equal / 2-pass / size-target / deinterlace / custom GOP / subtitle extract / user-saved presets table | out-of-scope | — | same table 541 |
| Session 8c `gui-console-polish` | deferred | MEU-27 | grouping Session 8c; MEU-27 already `ready_for_review`; Session 14 reflection “do not start 8c unless asked” |
| Rewrite `/conversions` or OpenAPI routes | out-of-scope | — | MEU-31 approved; grouping Session 15 is GUI |
| Rewrite `avkit_convert` MCP | out-of-scope | — | MEU-32 approved |
| Invent new MEU IDs | out-of-scope | — | grouping §4; Session 14 Next Day Outline item 2 |
| Live FFmpeg encode in agent E2E | out-of-scope | — | Local Canon MEU-20 `E2E_SEAM`; substitute Browse stub + `E2E_HAPPY_PATH` |
| Change `show-file-dialog` return type | out-of-scope | — | Local Canon Settings/TTS/cookie single-string; Convert adds `SHOW_FILES_CHANNEL` instead |
| L3 `UnsavedChangesModal` on Convert queue | out-of-scope | — | G23 L3 is list-detail only (emerging-standards G23); Convert is not list-detail |
| TaxHelpCard `learnMoreUrl` / dismiss | out-of-scope | — | av-kit G26 surface is shared `HelpCard` (MEU-23 AC-23.15); Zorivest Tax fields are not in this tree |
| Debounced `schedulePut` on non-converter settings namespaces | out-of-scope | — | MEU-23 Local Canon; this MEU changes **converter** only to `G23_CONVERT` explicit Save |
| Three rail items for Compress/Cut/Extract | out-of-scope | — | Spec 39–47 rejected layouts |
| `wmic` GPU detect / CUDA wheel | out-of-scope | — | Spec 571–584 |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-33 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"8"` **without removing** `PRIOR_PLAN_SLASHES`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 13–14 links. Do not hand-edit AUTOGEN tables. Do **not** mark `GROUPING_FILE` complete until H2 after exec `approved`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import json, re, sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-26-p8-conversion-gui'; SLASH=PLAN+'/'; sets=json.loads(Path(PLAN+'/named-sets.json').read_text(encoding='utf-8')); NEXT=sets['HUB_NEXT_AFTER']; PRIORS=sets['PRIOR_PLAN_SLASHES']; MEUS=('MEU-33',); data=load(); p8=next(p for p in data['phases'] if str(p['id'])=='8'); eps=list(p8.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 8 missing PLAN_FOLDER_SLASH'); miss_prior=next((s for s in PRIORS if s not in eps), None); miss_prior is not None and sys.exit('phase 8 missing prior '+miss_prior); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

> Classify every command through `.agent/docs/output-evidence-policy.md`. Exact-evidence: `rtk proxy`. Capture `$LASTEXITCODE` immediately.

### 1. UI Red oracle (MEU-33)

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx vitest run --allowOnly=false --reporter=default --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-33-ui.json; exit $LASTEXITCODE } *> C:/Temp/av-kit/fail-to-pass-meu-33-ui.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'UI Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-33-ui.txt; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-26-p8-conversion-gui/assert-red-oracle.ps1 -Kind ui -Meu 33 -Receipt C:/Temp/av-kit/fail-to-pass-meu-33-ui.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-33-ui.json; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-33-ui.txt | Select-Object -Last 40; exit $LASTEXITCODE }; 'PASS: FAIL_TO_PASS red'; exit 0
```

### 2. UI Green / MEU gate

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/ui-green-meu-33.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-green-meu-33.txt | Select-Object -Last 40; exit $code
```

### 3. E2E census + Wave 8 (sandbox may `[B]`)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-26-p8-conversion-gui/assert-e2e-control-census.ps1 *> C:/Temp/av-kit/e2e-control-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/e2e-control-census.txt; exit $code }; rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts convert-queue.test.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave8.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave8.txt | Select-Object -Last 40; exit $code
```

### N. OpenAPI Drift Check (no `packages/api/` edits — `--check` still required)

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

`-o` is forbidden unless Step 1 reported `[FAIL]`.

---

## Open Questions

None remaining. Step 2B forks were resolved from Spec / Local Canon / research and promoted into locks:

| Question | Option | Source | Recommendation |
|----------|--------|--------|----------------|
| Multi-file Browse vs existing single-file IPC | Additive `SHOW_FILES_CHANNEL` | Electron dialog `multiSelections`; Local Canon `show-file-dialog` string return | ✅ additive channel |
| Drop path after Electron 32 | Preload `webUtils.getPathForFile` | [webUtils](https://www.electronjs.org/docs/latest/api/web-utils) | ✅ preload bridge |
| convert:add / NavRail off-route | Focus dropzone if staging empty; POST only if staging nonempty after `NAVIGATE_AND_DELIVER`; **NavRail / Ctrl+4 never POST** | G11; RULE-3; MEU-20 `download:add` | ✅ |
| Lazy `/convert` | `LAZY_CONVERT_ROUTE`; Downloader stays eager | Spec 521; 06-gui.md 912; TanStack lazyRouteComponent | ✅ |
| Confirm Clear All | G20 portal (Transcript), not Downloader skip-confirm | G20; MCP destructive set | ✅ portal |
| Hub Next after Phase 8 | Human-gated 8c text, not `/create-plan p6-gui-console-polish` | Session 14 reflection item 2 | ✅ `HUB_NEXT_AFTER` |
| G23 on converter settings | Settings-only L1+L2 (`G23_CONVERT`); L3 N/A; queue Add is not persist | G23; Spec 531 | ✅ |

---

## Research References

- Electron `webUtils.getPathForFile` — https://www.electronjs.org/docs/latest/api/web-utils
- Electron 32 removed `File.path` — https://github.com/electron/electron/blob/main/docs/breaking-changes.md
- Electron `dialog.showOpenDialog` `multiSelections` — https://www.electronjs.org/docs/latest/api/dialog
- TanStack Router `lazyRouteComponent` — https://tanstack.com/router/latest/docs/framework/react/api/router/lazyRouteComponentFunction
- TanStack Table v8 row selection — https://tanstack.com/table/v8/docs/guide/row-selection
- Playwright network mocking — https://playwright.dev/docs/network#network-mocking
- Steve Krug / Spec thesis — `docs/build-plan/08-video-conversion.md` 25–47
- Local Canon Downloader — `docs/execution/plans/2026-08-20-p6-gui-downloader/`
- Local Canon REST/MCP wires — `docs/execution/plans/2026-08-26-p8-conversion-api-mcp/named-sets.json`
