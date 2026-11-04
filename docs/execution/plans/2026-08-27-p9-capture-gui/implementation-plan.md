---
project: "2026-08-27-p9-capture-gui"
date: "2026-08-27"
source: "docs/build-plan/09-screenshot-capture.md"
meus: ["MEU-39"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 9 Capture GUI

> **Project**: `2026-08-27-p9-capture-gui`
> **Build Plan Section(s)**: [09-screenshot-capture.md](../../../build-plan/09-screenshot-capture.md) §Capture Page + §Electron OS surface + §GUI implementation notes; [06-gui.md](../../../build-plan/06-gui.md) Wave 9; [gui-actions-index.md](../../../build-plan/gui-actions-index.md) `nav:capture` + `capture:*`
> **Status**: `draft`
> **Grouping**: [2026-08-26-p9-screenshot-capture-session-grouping.md](../../../../.agent/context/grouping/2026-08-26-p9-screenshot-capture-session-grouping.md) Session 18 — MEU-39 only

---

## Goal

Ship the **Capture page** (`CAPTURE_HOME`) plus the Electron OS surface that FastAPI cannot own: tray, `globalShortcut` (`capture.hotkey`), region overlay (`OVERLAY_WINDOW`), inbox watcher, and interactive-request poll. Rail item is 5th primary after Convert (`NAV_CAPTURE`, `NAV_SHORTCUT`, Lucide `NAV_ICON`). Filmstrip + four viewport tools + Save bake via existing REST. Wave 9 E2E written and wired. Do not invent MEU IDs. Do not start Session 8c / MEU-27. Do not pack Downloader/Convert→Capture. Do not rewrite FastAPI or MCP (`ROUTE_COUNT_AFTER` / `ACTION_INDEX_AFTER` stay).

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
| MEU-39 | `.agent/context/handoffs/` + `HANDOFFS[0]` |

Rolling implementation review: `EXEC_REVIEW_FILE`.
Rolling plan review: `PLAN_REVIEW_FILE`.

Product glob owner: `HANDOFF_FILTER`. Expected count: `HANDOFF_COUNT` = `1`. Filenames: `HANDOFFS` in `named-sets.json` (do not restate).

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`. `builder_model` is `BUILDER_PIN` (`—`).

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-39a | MEU-39 Red: AC-39.1–AC-39.`RED_COUNT_39` UI/main tests **before** `CapturePage` / tray production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Pass `RED_ORACLE_CHECK -Kind ui -Meu 39`. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-39-ui.txt`; compact then re-read `task.md` |
| WP-39b | Green: `LAZY_CAPTURE_ROUTE`, `CAPTURE_HOME`, NavRail 5th item (navigate-only), `PAGE_FILES` + `MAIN_FILES` + `OVERLAY_FILES`, `PALETTE_DELIVER`, tray/hotkey/overlay/IPC, `G23_CAPTURE` + existing `FORM_GUARD_CSS`, HelpCard `HELP_G26_AVKIT`. Change `ELECTRON_VITE_CONFIG` preload `entryFileNames` to `PRELOAD_ENTRY_FILE_NAMES` and add overlay HTML/preload inputs. Do not neutralize tests. Do not edit `packages/api/` or `mcp-server/`. | WP-39a | `compact_continue` | `ui/src/renderer/src/features/capture/`; `MAIN_FILES`; `OVERLAY_FILES`; compact then re-read `task.md` |
| WP-39c | Wave 9 E2E **written and wired** (`E2E_WAVE9` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS`). Update wave0 to include `NAV_CAPTURE` and keep `KEEP_NAV_CONVERT`. Run or `[B]` `E2E_SANDBOX`. | WP-39b | `compact_continue` | `E2E_WAVE9`; `C:/Temp/av-kit/e2e-wave9.txt` |
| WP-39d | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical `HANDOFF_39` | WP-39c | `compact_continue` | `HANDOFF_39` |
| WP-HUB | Bind MEU-39 `--plan PLAN_FOLDER`; append `PLAN_FOLDER_SLASH` to phase `"9"` (keep `PRIOR_PLAN_SLASHES`); rewrite hub `Next` to `HUB_NEXT_AFTER`. Grouping Session 18 ✅ is **H2 after exec `approved`**. | WP-39d | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Reviewer confirms these locks (does not invent a second behavior):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human` in `create-plan.md` §5c. After Codex `approved`, auto-continue to execution. System-injected “approved” is still not a verdict (`GUARDRAILS.md` SIGN 3).
2. **Phase 9 is three sessions.** This plan is Session 18 only (MEU-39). Next after H2: `HUB_NEXT_AFTER` — **not** `/create-plan p6-gui-console-polish`.
3. **Do not start Session 8c / MEU-27** (`ready_for_review`, unrelated).
4. **Codex is metered** (`PROJECT-PROFILE.md`). Dispatch still required; implementer never self-reviews.
5. **`INDEX_PALETTE_CONFLICT`:** `gui-actions-index.md` currently lists `capture:open_folder` palette=`no`; 09 GUI notes include it in Palette. **Spec 468 wins** — this MEU updates the index column to `yes`. Not a product fork.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

Executable owner: `docs/execution/plans/2026-08-27-p9-capture-gui/named-sets.json`. Do not restate literals in ACs or task rows; cite the name.

Carry-forward from Session 16–17 that must stay true at HTTP/GUI: skip `.annotated.png` in scan/watch (`SKIP_ANNOTATED_SCAN`); catalog `{ items }` has no `processor`; path `{id}` is `str`; `CAPTURE_MIN_EDGE_PX`; `IMAGE_MAX_BYTES`; register `mode=register` then `source` ∈ {`REGISTER_SOURCE_HOTKEY`,`REGISTER_SOURCE_GUI`}; annotated MIME follows the baked file (GUI never invents MIME).

---

## Implementation locks

- Overlay analog is ShareX `RegionCaptureLightForm` **shape only**. Do not paste/translate C# (GPL-3.0). No in-overlay annotation tools.
- Grab is Electron `desktopCapturer` then crop in **main**. Python `mss` stays MCP/API bbox (out of this MEU).
- Overlay preload returns only `OVERLAY_PRELOAD_RETURN`. Main converts if needed.
- `FREEZE_ORDER`: capture freeze **before** showing the overlay window so overlay chrome is not in the bitmap.
- `DISPLAY_UNDER_CURSOR`: do not stitch the virtual desktop.
- Relative inbox paths: do not PUT; API already 422.
- Filmstrip images: `IMAGE_BLOB`.
- Close-to-tray default true (`CAPTURE_DEFAULTS.close_to_tray`).
- Do not edit `packages/api/` or `mcp-server/`. OpenAPI `--check` only (no `-o` unless someone accidentally edits API — they must not).

Research URLs used to lock under-specified Electron behavior:

- [`globalShortcut.register` returns boolean](https://www.electronjs.org/docs/latest/api/global-shortcut)
- [`screen.getCursorScreenPoint` / `getDisplayNearestPoint`](https://www.electronjs.org/docs/latest/api/screen)
- [`desktopCapturer.getSources`](https://www.electronjs.org/docs/latest/api/desktop-capturer)
- [Transparent / frameless / skipTaskbar / alwaysOnTop window options](https://www.electronjs.org/docs/latest/api/browser-window)
- [TanStack `lazyRouteComponent`](https://tanstack.com/router/latest/docs/framework/react/api/router/lazyRouteComponentFunction)
- [TanStack Query v5 `refetchInterval(query)`](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery)

---

## §4A GUI Element Compliance

**Triggered:** Capture page + Settings Capture card + overlay (overlay is a separate BrowserWindow; census covers the **page** controls).

| Check | Result |
|-------|--------|
| `docs/gui-element-reference.md` | **Absent** — G31–G35 + Spec tokens |
| Button/input/output indexes | **Absent** except `gui-actions-index.md` — map via table below |
| E2E written+wired | `E2E_WAVE9` + `E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CONTROL_CENSUS` |
| G30–G35 / E2 | G30 on Capture settings `<SelectInput>` if any. G31 shared `bg-accent` only (cyan selected bar = existing accent token). G32 no raw hex in `className`. G33 duration tokens. G34 variants below. G35 T0–T2 (Save is T2). E2 = `E2E_WAVE9`. |
| G20 | portal confirm for Delete and dirty-thumb switch; no `window.confirm` |
| G11 | `PALETTE_DELIVER` in AppShell; registry does not `apiFetch` |
| G16 | existing CSP — do not regress; `img-src` already allows localhost for authenticated image GET |
| G5 | `POLL_PENDING_MS` / `POLL_IDLE_MS` (page); `POLL_REQUEST_MS` (main interactive) |
| G3 | filmstrip rows = `data.items` (no invented search API) |
| G23 | Capture **settings** (card + page inbox/hotkey) = `G23_CAPTURE` L1+L2. Reuse `FORM_GUARD_CSS`. L3 / `UnsavedChangesModal` N/A (not list-detail). |
| G26 | `HELP_G26_AVKIT` (MEU-23 HelpCard ARIA + collapse persist + `HELP_TOPICS`). Not TaxHelpCard. |
| G27 | reuse existing `SHOW_DIRECTORY_CHANNEL`; add `IPC_CAPTURE_REGION` / `IPC_HOTKEY_STATUS` / `IPC_INBOX_CHANGED` to allowlist + census |
| 10-item enforcement doc | **Absent** — this table is the mapping |

Indexes remain absent except actions. **Local fallback:** G34 5 variants × 3 sizes. Toolbar `md`; row actions `sm`.

| Element | Variant | Size | States | testid | Feedback |
|---------|---------|------|--------|--------|----------|
| Capture region | primary | md | default/hover/focus/disabled | `capture-region` | T1 IPC overlay |
| Inbox path | text | md | default/focus | `capture-inbox-path` | T0 until Save |
| Inbox Browse | secondary | md | default/hover/focus | `capture-inbox-browse` | T1 existing directory IPC |
| Hotkey display | output | — | registered / failed | `capture-hotkey` | T1 `IPC_HOTKEY_STATUS` |
| Hotkey Change | secondary | sm | default/hover/focus | `capture-hotkey-change` | T0 recorder then G23 dirty |
| Status | output | — | default | `capture-status` | T1 poll |
| Hotkey banner | status | — | hidden / visible | `capture-hotkey-banner` | T1 register false |
| Filmstrip | output | — | default/selected | `capture-filmstrip` | T1 catalog |
| Filmstrip item | output | — | default/selected | `capture-filmstrip-item` | T1 click selects |
| Viewport | canvas | — | default | `capture-viewport` | T0 overlay vectors |
| Tool Arrow/Box/Highlight/Text | outline (active = primary) | md | default/hover/focus | `capture-tool-*` | T0 local |
| Color / stroke | text | sm | default/focus | `capture-color`, `capture-stroke` | T0 local |
| Undo / Redo | ghost | sm | default/disabled | `capture-undo`, `capture-redo` | T0 session stack |
| Save annotated | primary | md | default/hover/focus/disabled | `capture-save` | T1 POST annotate |
| Open file / folder | ghost | sm | default/hover/focus/disabled | `capture-open-*` | T1 existing IPC |
| Delete | destructive | sm | default/hover/focus/disabled | `capture-delete` | T1 204 after G20 |
| Confirm / cancel | destructive / outline | sm | default | `capture-*-confirm*` | T1 |
| Empty state | output | — | default | `capture-empty` | T0 `EMPTY_STATE` |
| Capture Save (settings) | primary | md | default/dirty (`G23_SAVE_CLASS`) / pending | `capture-settings-save` | T2 G23 L2 PUT |
| Settings Capture card | section | — | default/dirty | `capture-settings` | T2 Save PUT |

---

## Proposed Changes

### MEU-39 — `gui-capture`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| Settings capture PUT (page + card) | Zod `.strict()` `CAPTURE_KEYS` then existing `SettingsPutIn` | `inbox_dir` absolute; `hotkey` Electron accelerator string; bools | extra forbid (client + server) | extra key → PUT count 0; relative path 422 `ERROR_SURFACE` | same leaves | Spec 09 inbox/hotkey; MEU-37 CAPTURE_KEYS |
| Annotate Save | client Zod `.strict()` matching `AnnotateIn` | annotation union; colors named/`#RRGGBB`; text 1–500 | extra forbid | extra key / unknown type → POST count 0; API 422 | create-only overlay | Spec viewport tools; MEU-37 |
| Overlay IPC rect | `OVERLAY_RECT_SCHEMA` (Zod `.strict()` in `OVERLAY_PRELOAD` then re-parse in main) | finite ints; width/height ≥ `CAPTURE_MIN_EDGE_PX`; then display-bound clamp | extra forbid | extra key / NaN / 7px → no crop, no PNG, no POST | n/a | Spec overlay min 8; Boundary Input Contract |
| Complete interactive | existing `CaptureCompleteIn` | `COMPLETE_BODY`; `{id}` is `str` | extra forbid | extra key 422; unknown id `PATH_ID_UNKNOWN_HTTP`; relative path 422 | n/a | MEU-37; Spec 171 |
| Cancel interactive | existing `EmptyIn` optional | `CANCEL_BODY` | extra forbid | extra key 422; unknown id `PATH_ID_UNKNOWN_HTTP` | n/a | MEU-37; Spec 171 |
| Register POST (main) | `CaptureRegisterIn` | `mode=REGISTER_MODE`; `source` ∈ {`REGISTER_SOURCE_HOTKEY`,`REGISTER_SOURCE_GUI`}; absolute `path` | extra forbid | extra key / relative path → no success | n/a | MEU-37 |
| Delete | confirm then `DELETE /captures/{id}` | path id `str` | n/a | 404 envelope `ERROR_SURFACE` | n/a | Spec destructive Delete |
| Browse IPC | existing directory Zod | `SHOW_DIRECTORY_CHANNEL` only | extra forbid | handler reject | n/a | G27; MEU-19 |
| Open file/folder | existing IPC Zod | `target` min 1; exe deny remains | `.strict()` | handler reject | n/a | MEU-19 |
| Catalog poll | `CaptureListOut` | must have `items`; must **not** have `FORBIDDEN_LIST_KEY` | ignore unknown out; never treat as array | `ERROR_SURFACE` | GET only | Spec filmstrip; Session 17 RULE-1 |

Python `assert` is not validation (N/A in renderer — Zod + REST).

#### Acceptance Criteria

> Tag: `unit` or `integration`. Each control AC names observable + call chain + negative oracle.

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-39.1 | integration | **Control `CAPTURE_HOME` + `LAZY_CAPTURE_ROUTE`.** Observable: hash `#/capture` + `capture-page`; `router.tsx` source has `lazyRouteComponent` and **no** static `import { CapturePage }`. Chain: first navigation to `/capture` loads the Capture chunk; Downloader remains a static import; Convert remains lazy. Negative: `router.tsx` still `import { CapturePage } from './features/capture/CapturePage'` → fail. | Spec 463; 06-gui.md Wave 9; [lazyRouteComponent](https://tanstack.com/router/latest/docs/framework/react/api/router/lazyRouteComponentFunction) | eager static CapturePage import |
| AC-39.2 | integration | **Control `NAV_CAPTURE` + RULE-3 rail.** Observable: 5th primary after Convert (`NAV_INDEX`); `testid` `NAV_CAPTURE`; Lucide `NAV_ICON`; palette `NAV_CAPTURE_ID` + `NAV_SHORTCUT`. `KEEP_NAV_CONVERT` stays 4th with `KEEP_NAV_CONVERT_SHORTCUT`. Settings stays pinned, not a 5th primary. Chain: `NavRail` click → `onNavigate(CAPTURE_HOME)` → `navigateShell` **only** (zero `POST /captures` on that tick). AppShell Ctrl+5 same: navigate, no `capture:region`. Negative: NavRail Capture click POSTs capture on the same tick; Convert becomes 5th → fail. | Spec 89, 464; RULE-3 | four-item primary rail; sync POST on rail click |
| AC-39.3 | integration | **Control `CATALOG_ENVELOPE` + `QUERY_KEY` + poll.** Observable: hook `{ items }` with **no** `FORBIDDEN_LIST_KEY`; Query v5 `refetchInterval(query)`: pending interactive request while page visible → `POLL_PENDING_MS` else `POLL_IDLE_MS` (including undefined data); IPC `IPC_INBOX_CHANGED` invalidates immediately. No SSE. Chain: `useCaptureCatalog` → `apiFetch GET /captures`. Negative: `data.map` treating envelope as array; poll uses convert `{ items, processor }` → fail. | Spec 125–131; Session 17 catalog; [useQuery refetchInterval](https://tanstack.com/query/v5/docs/framework/react/reference/useQuery) | processor key; v4 `(data, query)` |
| AC-39.4 | integration | **Control inbox header + Browse.** Observable: `capture-inbox-path` bound to `capture.inbox_dir`; Browse invokes existing `SHOW_DIRECTORY_CHANNEL` (not a new file dialog). Relative path does not PUT. Persist via `G23_CAPTURE` Save (same PUT as Settings card). Chain: Browse → form dirty → Save → Zod `.strict()` → `PUT /settings/capture`. Negative: relative path fetch; Browse PUT on pick without Save → fail. | Spec 115–123; G23 L1 | drop-zone as primary Add |
| AC-39.5 | integration | **Control hotkey display + recorder + banner.** Observable: `capture-hotkey` shows current accelerator; Change records a key → Electron accelerator string → form dirty → PUT `capture.hotkey`; `IPC_HOTKEY_STATUS` `{ registered, accelerator, error? }`; register false → `capture-hotkey-banner` text = `HOTKEY_IN_USE_BANNER` with that accelerator. Chain: page → PUT → main unregister old / `globalShortcut.register` (boolean). Negative: silent fail with no banner; Python `keyboard` hook → fail. | Spec 119–121; [globalShortcut.register](https://www.electronjs.org/docs/latest/api/global-shortcut) | ignore boolean false |
| AC-39.6 | integration | **Control Capture region IPC.** Observable: `capture-region` click invokes `IPC_CAPTURE_REGION` (same path as F2). Chain: button / `CAPTURE_COMMANDS.region` / tray menu → main overlay. Negative: renderer calls `mss`; button POSTs `mode=region` bbox to FastAPI → fail. | Spec 121, 176–177 | GUI bbox POST; renderer grab |
| AC-39.7 | integration | **Control filmstrip.** Observable: items newest first (`FILMSTRIP_SORT`); selected thumb uses shared accent token (cyan bar); click selects only (`NO_OS_VIEWER_ON_THUMB`); thumbs load via `IMAGE_BLOB` (revoke on unmount). Chain: GET list → GET image with Bearer → `URL.createObjectURL`. Negative: `<img src="file://">`; click `openPath` → fail. | Spec 125–129, 470 | file:// thumbs; OS viewer |
| AC-39.8 | unit | **Control viewport four tools + undo/redo.** Observable: Arrow/Box/Highlight/Text match Spec gestures; overlay is vector until Save; undo/redo session-local to the open image. Chain: page state stack. Negative: tools on the snip overlay window; undo persists across thumbs without confirm → fail. | Spec 133–146 | ShapeManager on overlay |
| AC-39.9 | integration | **Control Save annotate.** Observable: Save POSTs full `ANNOTATE_POST` list (empty array allowed). Extra key → POST count 0. Chain: `CAPTURE_COMMANDS.save` → Zod `.strict()` → `apiFetch`. Negative: extra `processor` / untyped fetch; Save writes PNG in renderer → fail. | Spec 142; MEU-37 AnnotateIn | bake in renderer |
| AC-39.10 | integration | **Control dirty-thumb G20.** Observable: switching thumbs while dirty opens `capture-dirty-confirm`; Confirm discards overlay and switches; Cancel/backdrop/Escape keeps selection and overlay. No `window.confirm`. | Spec 144; G20 | native confirm; silent discard |
| AC-39.11 | integration | **Control Delete G20 + files.** Observable: Delete opens `capture-delete-confirm`; Confirm `DELETE /captures/{id}` (`DELETE_FILES`); Cancel does not DELETE. Unlike Convert Clear, files go. Chain: portal → `apiFetch` DELETE. Negative: row-only delete; no confirm → fail. | Spec 148–150; G20 | Convert Clear semantics |
| AC-39.12 | integration | **Control open file/folder.** Observable: existing `IPC_OPEN_PATH` / `IPC_SHOW_ITEM` with selected original (fallback annotated). Disabled when no selection. Exe deny unchanged. | Spec GUI notes; MEU-19 | bypass exe deny |
| AC-39.13 | integration | **Control empty state + HelpCard `HELP_G26_AVKIT`.** Observable: empty viewport shows `EMPTY_STATE` (`NO_DROPZONE_PRIMARY`); HelpCard `HELP_FEATURE`; `aria-expanded` + `aria-controls`; `HELP_COLLAPSE_KEY`; reload restores collapse; `HELP_ROUTES_AFTER` includes `/capture`; `help:toggle` on Capture expands Capture help; sections cover `HELP_TOPICS`. Negative: drop-zone as primary; omit topics; bounce to Settings → fail. | Spec 111–113, 152–154, 466; G26 | TaxHelpCard fields as blocker |
| AC-39.14 | integration | **Control `CAPTURE_PALETTE_IDS` + `PALETTE_DELIVER`.** Observable: registry ids + `CAPTURE_EVENTS` + AppShell listener + same `CAPTURE_COMMANDS` as page buttons. Off-route `capture:region` uses `NAVIGATE_AND_DELIVER` then invokes IPC (not same-tick POST). Palette category `capture`. Negative: listener only inside `CapturePage`; same-tick POST with navigate; palette `apiFetch` second path → fail. | G11; Spec 467–468; RULE-3; `INDEX_PALETTE_CONFLICT` | page-only listener |
| AC-39.15 | integration | **Control Settings Capture card + `G23_CAPTURE`.** Observable: `capture-settings` + `CAPTURE_KEYS` leaves; `isDirty` vs last GET; Save uses `G23_SAVE_CLASS` + `G23_SAVE_LABEL_DIRTY` when dirty; PUT `/settings/capture` Zod `.strict()` **only** on Save (fetch count 0 while dirty-unsent). Extra key rejected before fetch. Browse dir uses existing `SHOW_DIRECTORY_CHANNEL`. Import `FORM_GUARD_CSS`. Page inbox/hotkey share this form. Negative: `schedulePut` debounce PUT on every keystroke; no dirty class when form ≠ GET → fail. | Spec 474; G23 L1+L2 | invent debounce-only Capture card |
| AC-39.16 | integration | **Control tray.** Observable: Tray created while app runs; menu labels = `TRAY_MENU`. Show window focuses main; Capture region = same overlay path as F2; Open inbox folder uses `showItemInFolder` on `inbox_dir`; Quit sets `QUIT_INTENT` then `app.quit`. Chain: `capture-tray.ts` from `boot()`. Negative: tray as a React route; Quit only `window.close()` without `QUIT_INTENT` → fail. | Spec 164–165 | React tray page |
| AC-39.17 | integration | **Control close-to-tray + `QUIT_INTENT`.** Observable: `close_to_tray` true → hide on close **only when** `QUIT_INTENT` is false (`CLOSE_TO_TRAY_TRUE`); false → `CLOSE_TO_TRAY_FALSE`. Explicit Quit/app-menu Quit sets `QUIT_INTENT` so the same close handler does **not** `preventDefault`. Chain: window `close` + tray Quit + `before-quit`. Negative: hide even when `QUIT_INTENT` is true (Quit never exits); hide even when setting false → fail. | Spec 165–166; `CAPTURE_DEFAULTS` | ignore setting; preventDefault on Quit |
| AC-39.18 | integration | **Control `globalShortcut` lifetime.** Observable: register `capture.hotkey` after settings load; unregister on change/quit; boolean false surfaces banner (AC-39.5). Chain: `capture-hotkey.ts`. Negative: leave old accelerator registered; Python hook → fail. | Spec 167; Electron globalShortcut | leak old hotkey |
| AC-39.19 | unit | **Control overlay window + display + freeze.** Observable: `OVERLAY_WINDOW` flags; bounds = `DISPLAY_UNDER_CURSOR`; `FREEZE_ORDER` uses `desktopCapturer.getSources` `thumbnailSize` = display.size × scaleFactor. Chain: overlay factory. Negative: virtual-desktop stitch; freeze after overlay shown (chrome in bitmap) → fail. | Spec 168, 185–186; Electron screen + desktopCapturer | primary-display-only grab when cursor is on another |
| AC-39.20 | unit | **Control overlay interaction + `OVERLAY_RECT_SCHEMA`.** Observable: drag rect; `OVERLAY_CONFIRM`; no annotation tools in overlay DOM (`OVERLAY_HTML` + `OVERLAY_SCRIPT`). Overlay preload is `OVERLAY_PRELOAD` and returns only `OVERLAY_PRELOAD_RETURN` after Zod `.strict()`. Edge &lt; `CAPTURE_MIN_EDGE_PX`, extra key, or non-finite coords → cancel, no write, no POST. Chain: overlay renderer → preload Zod → main re-parse → crop. Negative: Arrow/Box on overlay; 7px write success; extra `color` key accepted → fail. | Spec 168, 183; ShareX Light analog (shape) | in-overlay ShapeManager |
| AC-39.21 | integration | **Control write PNG + register.** Observable: `{inbox_dir}/{TIMESTAMP_FORMAT}.png` using `TIMESTAMP_CLOCK`; then `POST /captures` `mode=REGISTER_MODE` `source` = `REGISTER_SOURCE_HOTKEY` (F2) or `REGISTER_SOURCE_GUI` (button/tray). `COPY_TO_CLIPBOARD` after success when setting true. Chain: `capture-register.ts` with Bearer `guiNonce`. Negative: UTC filename when local clock differs; `source=scan` from overlay; skip POST → fail. | Spec 169; MEU-37 register | scan source from GUI |
| AC-39.22 | integration | **Control black-frame block.** Observable: empty/black bitmap → log `CONSOLE_MODULE_TAG` + surface `SCREEN_CAPTURE_BLOCKED`; `BLACK_FRAME_POLICY` (no PNG, no POST). Negative: save black PNG as success → fail. | Spec 187 | silent black success |
| AC-39.23 | integration | **Control inbox watcher.** Observable: `fs.watch` (or equivalent) on `inbox_dir` → IPC `IPC_INBOX_CHANGED`; `SKIP_ANNOTATED_SCAN`. Chain: main → renderer query invalidate. Negative: watch `.annotated.png` as a new original; SSE → fail. | Spec 170; Session 16 skip annotated | treat annotated as original |
| AC-39.24 | integration | **Control interactive poll + complete/cancel boundaries.** Observable: main `INTERACTIVE_POLL` at `POLL_REQUEST_MS` (always ≤ 1 s); show overlay; complete via `COMPLETE_PATH` with `COMPLETE_BODY`; Esc → `CANCEL_PATH` with `CANCEL_BODY`. Chain: GET pending → overlay → POST complete/cancel with Bearer. Negative: poll only from renderer; leave Pending on Esc; extra key on complete fetch; unknown `{id}` treated as 200 → fail. | Spec 171; MEU-37 | renderer-only poll |
| AC-39.25 | integration | **Control preload allowlist.** Observable: main preload adds invoke `IPC_CAPTURE_REGION`, invoke `IPC_HOTKEY_STATUS`, on `IPC_INBOX_CHANGED` only among new channels; `PRELOAD_LOCK` unchanged. Overlay dedicated preload cannot `require('fs')`. Census in `ipc-channels` / `gui-actions-audit`. Negative: `nodeIntegration: true`; expose `desktopCapturer` to renderer → fail. | Spec 173–181; G27 | Node in renderer |
| AC-39.26 | integration | Wave 9 E2E **written and wired** (`E2E_WAVE9`, `E2E_CASES`, `E2E_LOCATOR_FORM`, `E2E_PER_CONTROL`, `E2E_CONTROL_CENSUS`, `E2E_SEAM`). Keep visual groups. Interactive IDs are **not** satisfied by visibility alone: census requires `WAVE9_INTERACT_BIND` except `WAVE9_VISUAL_ONLY`. W9-2 `WAVE9_W9_2_CLICK` + `WAVE9_POST_ZERO_ORACLE` (`WAVE9_REGISTER_POST` assembled from `WAVE9_POST_COUNTER` + `WAVE9_POST_METHOD` + `WAVE9_CAPTURE_POST_PATH`). W9-3 settings interact. W9-4 region stub + delete confirm **click**. W9-5 `WAVE9_W9_5_ENABLED`. W9-6 palette `capture:region` + post-zero. Isolated `AVKIT_APP_DATA`. No live desktop grab (`E2E_HAPPY_PATH`). Sandbox no-display → `[B]` `E2E_SANDBOX`; files still exist. Update `06-gui.md` Wave 9 cumulative to `E2E_CUMULATIVE_AFTER`. | Spec 471, 516; 06-gui 1163; E2 | visual-only oracles for tools/save/delete/settings |
| AC-39.27 | integration | Wave0 + shell tests include `NAV_CAPTURE` **and** `KEEP_NAV_CONVERT`. `e2e-wiring.test.ts` lists both. Header `PAGE_LABELS['/capture']`. Console module tag `CONSOLE_MODULE_TAG`. | 06-gui Wave 0; lock Wave0 | drop Convert from wave0; Capture as pinned Settings |
| AC-39.28 | unit | G30–G35 + G36 / anti-placeholder on capture feature + Settings Capture + `MAIN_FILES` + `OVERLAY_FILES` + new IPC. G33: no arbitrary `duration-200` / `transition-all` in capture `className`. G34: buttons use `Button` `variant`/`size` from the §4A table (Capture region `primary` `md`; Delete `destructive`). G35: Settings Save is T2; Capture region/Save T1; tools T0. No `test.skip` / `.only`. No raw hex in `className`. OpenAPI `--check` exit 0 (no `packages/api/` edits). MCP `ACTION_INDEX_AFTER` untouched. `ROUTE_COUNT_AFTER` unchanged. `OVERLAY_BUILD_ORACLE` after `npm run build`. | G30–G35; G36; G8 | skip a Red test; edit `captures.py`; ad-hoc `bg-blue-600`; missing `OVERLAY_PRELOAD_OUT` |
| AC-39.29 | unit | **Control `OVERLAY_RECT_SCHEMA` fail-closed.** Observable: Zod `.strict()` rejects extra keys, non-finite numbers, and width/height &lt; `CAPTURE_MIN_EDGE_PX` **before** crop/write. Chain: preload parse → main re-parse (same schema). Negative: extra key still writes PNG; NaN coerced to 0 and saved → fail. | Boundary Input Contract; Spec min 8 | preload type-only without runtime parse |
| AC-39.30 | integration | **Control `COMPLETE_BODY` / `CANCEL_BODY`.** Observable: complete extra key → no successful complete (422); unknown `{id}` → `PATH_ID_UNKNOWN_HTTP`; cancel extra key → 422. Chain: main `capture-register.ts` / interactive poll uses the same REST schemas as MEU-37. Negative: untyped `fetch` JSON with extra `shot_id`; 200 on unknown id → fail. | MEU-37 CaptureCompleteIn / EmptyIn; Spec 171 | skip schema on complete |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Rail under Convert, Ctrl+5, `/capture` | Spec | 09 89, 464–465 |
| Not a Downloader queue | Spec | 09 81–83 |
| Inbox + hotkey header | Spec | 09 115–123 |
| Filmstrip `{ items }` poll + watcher | Spec + Local Canon | 09 125–131; Session 17 RULE-1 |
| Four tools + Save bake | Spec | 09 133–146 |
| Delete files + G20 | Spec + Local Canon | 09 148–150; G20 |
| HelpCard topics | Spec + Local Canon | 09 152–154; G26 MEU-23 |
| Lazy `/capture` | Spec + Research-backed | 09 463; TanStack lazyRouteComponent |
| Palette G11 + RULE-3 | Spec + Local Canon | 09 467–468; G11; Session 14 RULE-3 |
| Settings Capture card G23 | Spec + Local Canon | 09 474; G23 L1+L2 |
| Tray / close-to-tray | Spec | 09 164–166 |
| `globalShortcut` boolean + banner | Spec + Research-backed | 09 119, 167; Electron globalShortcut |
| Overlay Light analog, min 8, Esc | Spec + Human-approved ShareX map | 09 168, 540–584 (read, rewrite) |
| Overlay packaging | Research-backed + Local Canon | dedicated `OVERLAY_FILES`; electron-vite second preload+HTML; `PRELOAD_ENTRY_FILE_NAMES`; `OVERLAY_BUILD_ORACLE` |
| Display under cursor + freeze order | Spec + Research-backed | 09 185; Electron screen + desktopCapturer |
| Write PNG local timestamp + register | Spec + Local Canon | 09 169; MEU-37 register |
| Black frame blocked | Spec | 09 187 |
| Interactive poll 500 ms | Spec | 09 171 |
| Preload allowlist | Spec | 09 173–181 |
| Blob image not file:// | Spec | 09 470 |
| Wave 9 E2E | Spec | 09 471, 516; 06-gui 1163 |
| 4A indexes absent | Local Canon | MEU-20 / MEU-33 §4A |
| `INDEX_PALETTE_CONFLICT` | Spec wins | 09 468 over index line 72; update index |
| Query v5 interval | Research-backed | TanStack Query v5 refetchInterval |
| macOS/Linux overlay | out-of-scope | 09 478–492 named deferral |
| Session 8c | deferred | MEU-27 already scheduled pending |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `PAGE_FILES` | new | Capture page, filmstrip, viewport, commands, help, annotate Zod, catalog hook, settings hook |
| `MAIN_FILES` | new | overlay / hotkey / tray / inbox-watch / register |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modify | 5th primary `NAV_CAPTURE` + `Camera`; keep Convert 4th |
| `ui/src/renderer/src/components/layout/Header.tsx` | modify | `PAGE_LABELS['/capture']` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | capture listeners + Ctrl+5 + `HELP_ROUTES_AFTER` |
| `ui/src/renderer/src/router.tsx` | modify | `LAZY_CAPTURE_ROUTE` `/capture` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `NAV_CAPTURE_ID` + `CAPTURE_PALETTE_IDS` (events only) |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | modify | `HELP_FEATURE` in union |
| `ui/src/renderer/src/features/settings/settings-paths.ts` | modify | `capture` path |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` | modify | `capturePutSchema` `.strict()` |
| `ui/src/renderer/src/features/settings/useSettingsPage.ts` | modify | capture query + PUT |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | Capture card |
| `ui/src/main/ipc.ts` | modify | new capture IPC schemas + handlers |
| `ui/src/main/preload.ts` | modify | invoke/on allowlist |
| `ui/src/main/index.ts` | modify | tray, `QUIT_INTENT`, overlay boot, watcher, interactive poll |
| `OVERLAY_HTML` | new | Overlay page inside renderer root; no annotation tools |
| `OVERLAY_SCRIPT` | new | Overlay drag/Esc/Enter only |
| `OVERLAY_PRELOAD` | new | Zod `OVERLAY_RECT_SCHEMA`; `PRELOAD_LOCK` |
| `ELECTRON_VITE_CONFIG` | modify | preload inputs `index` + `overlay`; `entryFileNames` = `PRELOAD_ENTRY_FILE_NAMES` (must not stay `index.js`); renderer input `overlay` → `OVERLAY_HTML` |
| `ui/src/renderer/src/env.d.ts` | modify | new API types |
| `ui/tests/unit/ipc-channels.ts` | modify | census channels |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify | capture sources + testids; index palette yes for open_folder |
| `ui/tests/unit/capture-*.test.ts` | new | AC-39.* |
| `ui/tests/unit/settings-page.test.ts` | modify | Capture card |
| `ui/tests/unit/app-shell-wiring.test.ts` | modify | nav-capture + capture events |
| `ui/tests/unit/command-palette.test.ts` | modify | capture palette ids |
| `ui/tests/unit/shell-home.test.ts` | modify | five primary nav items |
| `ui/tests/unit/e2e-wiring.test.ts` | modify | Wave 9 files + nav-capture |
| `ui/tests/e2e/test-ids.ts` | modify | `WAVE9_TESTIDS` + `WAVE9_EXTRA_TESTIDS` |
| `ui/tests/e2e/launch.test.ts` | modify | `NAV_CAPTURE` visible; keep Convert |
| `E2E_WAVE9` | new | W9-1…W9-6 + `E2E_SEAM` |
| `docs/build-plan/06-gui.md` | modify | Wave 9 cumulative `E2E_CUMULATIVE_AFTER` |
| `docs/build-plan/gui-actions-index.md` | modify | `capture:open_folder` palette yes (`INDEX_PALETTE_CONFLICT`) |
| `docs/BUILD_PLAN.md` | modify via `meu_status.py` | bind MEU-39; `HUB_NEXT_AFTER` |
| `GROUPING_FILE` | modify at H2 | `GROUPING_DONE_MARK` after exec `approved` only |
| `docs/execution/plans/2026-08-27-p9-capture-gui/assert-*.ps1` | new | red oracle, handoff markers/ACs, E2E census, exec-review dispatch |

Do **not** modify `packages/api/`, `mcp-server/`, or `openapi.committed.json` except `--check`.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| macOS / Linux overlay + hotkey | out-of-scope | — | [09-screenshot-capture.md](../../../build-plan/09-screenshot-capture.md) 478–492 named deferral; Windows-first |
| Window / fullscreen GUI buttons | out-of-scope | — | same table; F2 region is the user loop |
| In-overlay arrows (ShareX ShapeManager) | out-of-scope | — | same table; annotation is Capture page / MCP |
| Extra tools (circle, freehand, blur, GIF, OCR, uploaders) | out-of-scope | — | same table 483–487 |
| Timer / clipboard-watch auto-capture | out-of-scope | — | same table 486 |
| Downloader / Convert → Capture handoff | out-of-scope | — | same table 488; grouping Session 18 |
| Recursive inbox scan / subfolders | out-of-scope | — | same table 489 |
| SSE | out-of-scope | — | same table 490; poll + `fs.watch` |
| MCP Guard | out-of-scope | — | same table 491; still deferred (06) |
| Session 8c `gui-console-polish` | deferred | MEU-27 | grouping Session 8c; MEU-27 already `ready_for_review` |
| Rewrite `/captures` or OpenAPI routes | out-of-scope | — | MEU-37 approved; grouping Session 18 is GUI |
| Rewrite `avkit_capture` MCP | out-of-scope | — | MEU-38 approved |
| Invent new MEU IDs | out-of-scope | — | grouping Session 18 is MEU-39 only |
| Live desktop grab in agent E2E | out-of-scope | — | Local Canon MEU-33 `E2E_SEAM`; substitute IPC stub + `E2E_HAPPY_PATH` |
| Paste/translate ShareX C# | out-of-scope | — | 09 536–537 Human-approved; Golden Rule 5 |
| L3 `UnsavedChangesModal` on Capture filmstrip | out-of-scope | — | G23 L3 is list-detail only; dirty-thumb uses G20 portal (AC-39.10) not L3 |
| TaxHelpCard `learnMoreUrl` / dismiss | out-of-scope | — | av-kit G26 surface is shared `HelpCard` (MEU-23 AC-23.15) |
| Python `keyboard` / second MCP transport in Electron | out-of-scope | — | 09 527–528 forbidden |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: bind MEU-39 `execution_plan` to `PLAN_FOLDER`; add `PLAN_FOLDER_SLASH` to phase `"9"` **without removing** `PRIOR_PLAN_SLASHES`; rewrite `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`; preserve Session 16–17 links. Do not hand-edit AUTOGEN tables. Do **not** mark `GROUPING_FILE` complete until H2 after exec `approved`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import json, re, sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-27-p9-capture-gui'; SLASH=PLAN+'/'; sets=json.loads(Path(PLAN+'/named-sets.json').read_text(encoding='utf-8')); NEXT=sets['HUB_NEXT_AFTER']; PRIORS=sets['PRIOR_PLAN_SLASHES']; MEUS=('MEU-39',); data=load(); p9=next(p for p in data['phases'] if str(p['id'])=='9'); eps=list(p9.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 9 missing PLAN_FOLDER_SLASH'); miss_prior=next((s for s in PRIORS if s not in eps), None); miss_prior is not None and sys.exit('phase 9 missing prior '+miss_prior); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

> Classify every command through `.agent/docs/output-evidence-policy.md`. Exact-evidence: `rtk proxy`. Capture `$LASTEXITCODE` immediately.

### 1. UI Red oracle (MEU-39)

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx vitest run --allowOnly=false --reporter=default --reporter=json --outputFile=C:/Temp/av-kit/fail-to-pass-meu-39-ui.json; exit $LASTEXITCODE } *> C:/Temp/av-kit/fail-to-pass-meu-39-ui.txt; $code=$LASTEXITCODE; if ($code -eq 0) { Write-Error 'UI Red unexpectedly green'; Get-Content C:/Temp/av-kit/fail-to-pass-meu-39-ui.txt; exit 1 }; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-gui/assert-red-oracle.ps1 -Kind ui -Meu 39 -Receipt C:/Temp/av-kit/fail-to-pass-meu-39-ui.txt -JsonReceipt C:/Temp/av-kit/fail-to-pass-meu-39-ui.json; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/fail-to-pass-meu-39-ui.txt | Select-Object -Last 40; exit $LASTEXITCODE }; 'PASS: FAIL_TO_PASS red'; exit 0
```

### 2. UI Green / MEU gate

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; if (-not (Test-Path 'out/preload/overlay.js')) { Write-Error 'missing OVERLAY_PRELOAD_OUT'; exit 1 }; if (-not (Test-Path 'out/renderer/overlay.html')) { Write-Error 'missing OVERLAY_HTML_OUT'; exit 1 }; exit 0 } *> C:/Temp/av-kit/ui-green-meu-39.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-green-meu-39.txt | Select-Object -Last 40; exit $code
```

### 3. E2E control census + Wave 9 (or `[B]` `E2E_SANDBOX`)

```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-gui/assert-e2e-control-census.ps1 *> C:/Temp/av-kit/e2e-control-census.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/e2e-control-census.txt; exit $code }; rtk proxy pwsh -NoProfile -Command { Push-Location ui; npm run build; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx playwright test launch.test.ts capture-inbox.test.ts; exit $LASTEXITCODE } *> C:/Temp/av-kit/e2e-wave9.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/e2e-wave9.txt | Select-Object -Last 40; exit $code
```

### 4. OpenAPI `--check` (no API edits)

```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

---

## Stop Conditions

1. **DONE** — every `task.md` row `[x]` or valid `[B]`; exec review `approved`; closeout artifacts pass markers.
2. Plan-review round cap **`PLAN_REVIEW_MAX_ROUND`** — HARD STOP, present remaining-risk buckets.
3. Exec-review round cap **`EXEC_REVIEW_MAX_ROUND`** — HARD STOP.
4. All CLI reviewer rungs rate-limited — HARD STOP; never self-review.
5. Human-decision gate (none identified in this plan).
6. `~50%` context checkpoint — finish current MEU handoff, compact, continue.

Do not stop after writing this plan. Auto-dispatch `/plan-critical-review`. Do not run project tests during plan review (SIGN 1).
