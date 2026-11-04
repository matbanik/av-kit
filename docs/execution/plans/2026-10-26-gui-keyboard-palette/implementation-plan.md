---
project: "2026-10-26-gui-keyboard-palette"
date: "2026-10-26"
source: "docs/build-plan/06-gui.md#shortcut-binding-residual"
meus: ["MEU-95", "MEU-96", "MEU-97"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: GUI keyboard shortcuts and a context-aware command palette (Session 41)

> **Project:** `2026-10-26-gui-keyboard-palette`
> **Build plan:**
> - `docs/build-plan/06-gui.md` §Shortcut binding (residual) (`:1446-1455`, MEU-95)
> - `docs/build-plan/06-gui.md` §Command palette curation (residual) (`:1459-1470`, MEU-96)
> - `docs/build-plan/06-gui.md` §Common shortcuts (residual) (`:1474-1484`, MEU-97)
> - `docs/build-plan/06-gui.md` §Command palette and action registry (`:307-317`) and `docs/build-plan/gui-actions-index.md` are Local Canon; row 1 amends both (D-144)
>
> **Grouping:** `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md`, Session 41 (`:88-99`), MEU table `:18-20`, rider `:28`, decisions D-94, D-95 (`:160-161`), D-99 (`:165`) and D-103 (`:169`).
> **Known issues:** `GUI-SHORTCUTS-ADVERTISED-UNBOUND` (`known-issues.yaml:2868`, triage D-78), `GUI-COMMAND-PALETTE-CURATION` (`:2939`, triage D-79, D-87, D-88), `GUI-KEYBOARD-SHORTCUTS-COMMON` (`:3036`, triage D-89), rider `GUI-AUDIT-CLIPBOARD-RESOLVER` (`:2613`, grouping D-99).
> **Status:** `draft`. Under `plan_to_exec_gate: human`. Mat's message of 2026-10-26 ("upon reviewer approval start executing it") is the execution message: execution starts when the Codex plan review returns `approved`, with no further pause (D-132).
>
> Line anchors are from `main` `bb481ec` (Session 40 at `b6b288e`, the Session 42 plan at `e7f7970` and `bb481ec`). The tree was clean when this plan was written.

## Goal

The registry and the nav rail advertise Ctrl+1..5, Ctrl+, and Ctrl+B, but `AppShell.tsx:49-91` binds only Ctrl+K, Ctrl+4 and Ctrl+5. The palette lists all 40 commands on every page in every state (`CommandPalette.tsx:43` memoises `listCommands()` once). It has no Appearance command. Its Clear runs `DELETE /downloads` with no confirm (`download-commands.ts:178`, `:232`). Its labels use internal words ("Check SABR", "Focus download URL"), and its TTS Generate posts a hard-coded `af_heart` voice when the page button is missing (`tts-commands.ts:287`). Only navigation has chords, and only Ctrl+K shows a hint.

1. **MEU-95 — `gui-shortcut-binding`.**
   - Chords have one canonical form (`CHORD_FORMAT`).
   - One map is built from the registry's `shortcut` fields and refuses duplicates and reserved chords (`SHORTCUT_MAP`, `RESERVED_CHORDS`).
   - One handler dispatches from any focus, with guards for modals and IME (`SHORTCUT_HANDLER`).
   - `AppShell` binds no chord of its own except Ctrl+K (`SHELL_WIRING`).
   - The rail shows each chord (`NAV_HINTS`).
2. **MEU-96 — `gui-command-palette-curation`.**
   - Registry entries say where and when they can run (`AVAILABILITY`), and pages publish their control state (`COMMAND_STATE`, `PAGE_STATE`).
   - The palette lists from that (`PALETTE_LIST`) and recomputes on a route or state change.
   - Two Appearance commands use the Settings theme path (`APPEARANCE`).
   - Palette Clear and Cancel open the page's `ConfirmModal` (`CONFIRM_ROUTE`).
   - Labels change to user words, and TTS never posts a hard-coded voice (`LABELS`).
   - Check dependencies works from any page (`CHECK_DEPS_ROUTE`).
   - The index and 06 are amended to this model (`INDEX_AMEND`).
   - The rider adds the clipboard resolver and two Settings index rows (`CLIPBOARD_RIDER`).
3. **MEU-97 — `gui-common-shortcuts`.**
   - The core chord set is added (`CHORD_TABLE`), including a page primary action (`PAGE_PRIMARY`).
   - Page chords are inert on other pages.
   - Every bound control shows its chord and carries `aria-keyshortcuts` (`HINTS`).
   - The palette's own Enter acts only when unmodified, so Ctrl+Enter with the palette open runs the page action and nothing else (`PALETTE_ENTER`).
   - Ctrl+S and palette Save press the page's Save button, so the shot ends clean as after a click (`CAPTURE_SAVE_ROUTE`).

Order (grouping `:96`): MEU-95 → MEU-96 → MEU-97, with the rider beside MEU-96 (the same audit and index edit). They run in one tree because all three edit `commandRegistry.ts`, `AppShell.tsx` and `gui-actions-index.md`. Row 0 records the baseline in `baseline.sha`; treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-10-26); no headroom MCP or binary. Scope is the renderer registry and shell (registry/commandRegistry.ts, components/layout AppShell.tsx, NavRail.tsx, Header.tsx, CommandPalette.tsx), the feature *-commands.ts modules and the pages that publish state, read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. A reviewer `approved` does not start execution by itself. Here the user's explicit message already asks for execution on approval (D-132), so row 0 records it as the execution message.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`, including the MCP ids `mcp-types`, `mcp-tests` and `mcp-build`) plus targeted file lists.
- **Working directory:** `P:/av-kit` on `main` (D-133; AGENTS.md "No branches or worktrees"). The Session 42 plan (`2026-10-26-tts-sideload-load`) also executes on `main`, and it shares the hub files (`meu-status.yaml`, `known-issues.yaml`, the grouping, `BUILD_PLAN.md`, `metrics.md`, `current-focus.md`). This session runs alone: row 0 and the gate stop (S8) if `HEAD` moves or another session's paths appear in the tree. Row 0 still runs `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci`.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, Mat is the fallback (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-95` | `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-MEU-95-handoff.md` |
| `MEU-96` (with the rider) | `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-MEU-96-handoff.md` |
| `MEU-97` | `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-MEU-97-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1) (rows 8 and H1-2)
- [identity.py](identity.py) (input identity, H1-6b)
- [red-check.py](red-check.py) (Red proof, rows 2, 4 and 6)

Rolling reviews:

- `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census, the canon updates (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha`; 06 and index edits |
| WP-1 | MEU-95 TDD: `CHORD_FORMAT`, `SHORTCUT_MAP`, `SHORTCUT_HANDLER`, `SHELL_WIRING`, `NAV_HINTS` (rows 2–3) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-95; `row3-ui-src.json` |
| WP-2 | MEU-96 + rider TDD: `AVAILABILITY` … `CLIPBOARD_RIDER` (rows 4–5) | WP-1 | `shared` | tests + source; `walkthrough.md` §MEU-96; `row5-ui-src.json` |
| WP-3 | MEU-97 TDD: `CHORD_TABLE`, `PAGE_PRIMARY`, `HINTS` (rows 6–7) | WP-2 | `compact_continue` | tests + source; `walkthrough.md` §MEU-97; compact, then re-read `task.md` and the walkthrough |
| WP-4 | Session gate and hub reconciliation (rows 8–9) | WP-3 | `shared` | gate receipts in `walkthrough.md` §Gate; `meu-status.yaml`, rendered `BUILD_PLAN.md` |
| WP-5 | H1 closeout, execution review, H2 | WP-4 | `compact_continue` | three handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for Mat. They are not a pause point.
>
> 1. **Chords fire from any focus, text fields included (`SHORTCUT_HANDLER`, D-134).** 06 "Text fields" asks for this. No registry chord is a field's own editing key, and plain Enter is never bound (`RESERVED_CHORDS`). While any modal other than the palette is open, no chord runs. With the palette open, a chord runs its command and closes the palette.
> 2. **The palette is context-aware (`PALETTE_LIST`, D-137).**
>    - Global commands are always listed: navigation, the rail, console, help, Appearance and Check dependencies (D-87 names Settings among the global commands).
>    - Each page's *entry* commands (Add, Browse files, Capture region, Open folder, Check YouTube quality limit) are listed only on that page, first. D-87 rejects a palette that "still shows other pages' commands" (`known-issues.yaml:3018`).
>    - *Stateful* commands (Start, Pause, Resume, Cancel, Clear, Stop, Preview, Generate, Save) are listed only on their own page, and only when that page's own control for them is enabled. If the page has published no state, they are hidden.
>    - Pause and Resume stay two entries, and the palette lists at most one of them (D-139).
> 3. **Palette Clear and Cancel always confirm (`CONFIRM_ROUTE`, D-140).**
>    - Downloader and Convert Clear open the page's existing clear-all `ConfirmModal`.
>    - Cancel opens a new "cancel" confirm with its own copy, whose cancel button reads **Keep running**.
>    - No API call is made before Confirm.
>    - The queue cards' own Cancel button stays unconfirmed (Out of Scope).
> 4. **Appearance commands and chords (`APPEARANCE`, D-141).** **Appearance: Dark** (Ctrl+Shift+D) and **Appearance: Light** (Ctrl+Shift+L) write `ui.theme` through the same function the Settings buttons use. The theme applies at once, and a failure is logged to the console panel.
> 5. **New chords (`CHORD_TABLE`, D-146).**
>    - Page chords: Ctrl+L focuses the URL field (Downloader, Transcript), Ctrl+O opens Browse files (Convert) and Ctrl+S saves the capture (Capture).
>    - Global chords: Ctrl+Enter runs the page's primary action, Ctrl+J toggles the console and F1 toggles help.
>    - The Electron default menu's own chords (Ctrl+R reload, Ctrl+Shift+I DevTools, zoom, Ctrl+W, Ctrl+M and the edit keys) stay as they are (D-136).
> 6. **`TEST_AMENDMENTS` TA-1 to TA-6.** TA-1, TA-2, TA-5 and TA-6 rewrite the four retained Electron scenarios (W1-6, W2-6, W8-6, W9-6) that select another page's entry command from off-page: each now proves the command is absent off-page, navigates by a global nav command, and selects it on its page (D-137). TA-1 and TA-2 also carry the renamed labels. TA-3 and TA-4 change tests that pin AppShell's hard-coded Ctrl+4/Ctrl+5. They are listed in advance. Any other contradiction the census finds stops execution (S2).
> 7. **Decision ids.** Session 40 used D-120 for Mat's gate ruling (its walkthrough and `metrics.md`), and the Session 42 plan on `main` reuses D-120 to D-131 for its own decisions. Both are committed. This plan starts at D-132 and changes neither file.
> 8. **Optional visual check.** At the commit gate, Mat may try the chords and the palette in the dev app. This is non-blocking; the Electron tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values. All renderer paths are under `ui/src/renderer/src/`.

| Name | Definition | Source |
|---|---|---|
| `PREREQS` | Before any edit: the cwd is `P:/av-kit` on `main` and `git status --porcelain` lists nothing outside this plan folder; no `graphify-out*/`; in `meu-status.yaml`, MEU-19, MEU-23, MEU-69, MEU-93 and MEU-94 are `approved` and MEU-95, MEU-96 and MEU-97 are `pending`; `AppShell.tsx` contains `event.key === '4'` and `event.key === '5'`, `CommandPalette.tsx` contains `useMemo(() => listCommands(), [])`, and `download-commands.ts` `deliverPaletteClear` calls `clearDownloads` (the code this plan changes). | grouping `:88-99`; `meu-status.yaml:2485`, `:2510`, `:2536` |
| `SHELL_PAGE` | `registry/shortcuts.ts` exports `type ShellPage = '/' \| '/transcript' \| '/tts' \| '/convert' \| '/capture' \| '/settings'` and `currentShellPage(): ShellPage \| null`, which reads `window.location.hash`, drops the leading `#` and any `?…`, maps `''` to `'/'`, and returns `null` for any other path. | `lib/shell-nav.ts` (`navigateShell` sets the hash); router `createHashHistory` |
| `CHORD_FORMAT` | `registry/shortcuts.ts` exports three pure functions. **`normalizeChord(text): string \| null`** splits on `+` (a trailing `+` key is the key `Plus`). Modifiers are matched case-insensitively, and `Meta`, `Cmd` and `Control` count as `Ctrl`. The result is `Ctrl+`, `Shift+`, `Alt+` in that order, then the key: one letter uppercased, a digit, `,`, `=`, `-`, `Plus`, `Enter`, `Escape`, `F1`–`F12`. Anything else, a key-less chord or a repeated modifier gives `null`. **`chordFromEvent(event): string \| null`** builds the same form from `ctrlKey \|\| metaKey`, `shiftKey`, `altKey` and `event.key` (`+` → `Plus`). It returns `null` when `event.key` is a bare modifier. **`ariaKeyshortcuts(chord)`** returns the WAI-ARIA form: `Ctrl` → `Control`, `Plus` → `+`, joined by `+` (`Ctrl+Shift+D` → `Control+Shift+D`). | 06 §Shortcut binding "Registry-driven"; WAI-ARIA 1.2 `aria-keyshortcuts` (R-b) |
| `RESERVED_CHORDS` | An exported `ReadonlySet<string>` of normalized chords no registry entry may take. **Electron default menu** (Windows `role` accelerators, R-a): `Ctrl+Z`, `Ctrl+Y`, `Ctrl+Shift+Z`, `Ctrl+X`, `Ctrl+C`, `Ctrl+V`, `Ctrl+A`, `Ctrl+R`, `Ctrl+Shift+R`, `Ctrl+Shift+I`, `Ctrl+0`, `Ctrl+=`, `Ctrl+Plus`, `Ctrl+Shift+Plus`, `Ctrl+-`, `F11`, `Ctrl+M`, `Ctrl+W`. **Capture:** `F2` (the `globalShortcut` hotkey) and its zoom keys, which the set above already holds. **Shell:** `Ctrl+K` (the palette opener, not a registry chord). **Fields:** `Enter`. | 06 "Text fields", "No collisions"; triage D-89; R-a; D-136 |
| `AVAILABILITY` | `CommandRegistryEntry` gains three optional fields: `page?: ShellPage` (the page that owns the command), `stateful?: true` (it can run only when its page says so) and `palette?: false` (never listed). `category` gains `'appearance'`. **Entry commands** have `page` and no `stateful`: `download:add`, `download:sabr_check`, `transcript:add`, `convert:add`, `convert:browse` (new), `capture:region`, `capture:open_folder`. **Stateful commands** have `page` and `stateful: true`: `download:start/pause/resume/cancel/clear`, `transcript:start/pause/resume/stop`, `convert:start/pause/resume/cancel/clear`, `tts:prepare`, `tts:generate`, `capture:save`. Every other entry is global (no `page`), `settings:check_deps` included. | 06 §Command palette curation "Context-aware" (triage D-87); D-137 |
| `SHORTCUT_MAP` | `buildShortcutMap(commands): ReadonlyMap<string, CommandRegistryEntry>` keys each entry that has a `shortcut` as `${normalizeChord(shortcut)}@${page ?? '*'}`. It throws an `Error` whose message names both ids and the chord, for: a chord that normalizes to `null`; a chord in `RESERVED_CHORDS`; two entries with the same key; and a chord used both globally (`@*`) and on any page. The same chord on two different pages is allowed (Ctrl+L). | 06 "Registry-driven", "Tests" ("no two entries share a chord"); D-133 |
| `SHORTCUT_HANDLER` | `createShortcutHandler({ commands, getPage, getState, isPaletteOpen, closePalette }): (event: KeyboardEvent) => boolean` builds the map once. Per event it returns `false` without acting when: `event.repeat` or `event.isComposing`; the chord is `null`; any element matching `[aria-modal="true"]` other than `[data-testid="command-palette"]` is in the document (`MODAL_GUARD`); no entry matches. It looks up `chord@<getPage()>` first, then `chord@*`. A `stateful` match runs only when `getState(page)[id] === true`; otherwise it returns `false`. On a match it calls `event.preventDefault()`, then `closePalette()` if `isPaletteOpen()`, then `entry.action()`, and returns `true`. It ignores the focused element, so Ctrl and F-key chords fire from text fields. | 06 "Registry-driven", "Text fields"; D-134 |
| `SHELL_WIRING` | `AppShell` builds the handler with `listCommands()`, `currentShellPage`, `getCommandState` and its palette state, and calls it from its existing `window` `keydown` listener (`AppShell.tsx:205`; one listener, never on `document`). The listener keeps, in order: Ctrl/Meta+K opens the palette; Escape closes an open palette; `if (handler(event)) return`; Escape closes the console. The `event.key === '4'` and `'5'` branches (`:78-86`) are removed. `handleGlobalShortcut` (`:25`) keeps its Ctrl+K contract (AC-19.17). | 06 "Registry-driven" ("AppShell binds no chord outside the registry"); D-135 |
| `NAV_HINTS` | Every `NavRail` item renders `title={`${label} (${shortcut})`}` in both rail states (the collapse item uses its `aria-label`) and `aria-keyshortcuts={ariaKeyshortcuts(shortcut)}`. Each `SHELL_NAV` item's `shortcut` equals the registry entry with the same `id`. | 06 §Common shortcuts "Hints"; D-147 |
| `COMMAND_STATE` | `registry/command-state.ts` holds one in-memory record per `ShellPage`, of type `Partial<Record<string, boolean>>`. It exports `publishCommandState(page, state)` (replaces the record and notifies only on a change in value), `clearCommandState(page)`, `getCommandState(page)` (the stable record, or a frozen empty one), `subscribeCommandState(listener): () => void`, `usePublishCommandState(page, state)` (publishes in an effect when the values change and clears on unmount) and `useCommandState(page)` (`useSyncExternalStore`). | 06 "Context-aware" ("the list recomputes when … state changes"); D-138 |
| `PAGE_STATE` | Each page publishes the enabled state of the page control that performs each stateful command, using the same expression that control uses. **Downloader** (`DownloaderPage.tsx:807-811`): `download:start` = `canStart`; `download:pause` = `!paused && controlEnabled('pause', ctx) && !busy`; `download:resume` = `paused && controlEnabled('resume', ctx) && !busy`; `download:cancel` = `controlEnabled('cancel', ctx) && !busy`; `download:clear` = `canClearAll`. **Convert** (`ConvertPage.tsx:827-830`): the same five for `convert:*`, with `convert-controls`. **Transcript** (`TranscriptPage.tsx:509-512`): `transcript:start/pause/resume/stop` = `canStart`, `canPause`, `canResume`, `canStop`. **TTS**: `tts:prepare` = `!(busy \|\| text.trim().length < 1)` (the `preview-cleanup-btn` expression, `TTSPage.tsx:382`); `tts:generate` = `generateEnabled({ isLoaded, text, status }) && !busy` (`:666`). **Capture**: `capture:save` = `dirty && canSave` (the `capture-save` mount and `disabled`, `CapturePage.tsx:1353-1359`). | D-138 |
| `PALETTE_LIST` | `registry/shortcuts.ts` exports pure `paletteCommands(commands, page: ShellPage \| null, state): CommandRegistryEntry[]`. It drops `palette: false` entries; drops every entry whose `page` is set and differs from `page` (entry and stateful alike, so with `page === null` only global entries remain); and drops `stateful` entries unless `state[entry.id] === true`. If both `<feature>:pause` and `<feature>:resume` survive, it drops the resume entry. It orders entries whose `page === page` first, then the rest, each part in registry order. `CommandPalette` lists `paletteCommands(listCommands(), page, useCommandState(page))`, with `page` re-read on `hashchange`, and runs Fuse over that list. Groups appear in the order their category first appears in the list, and `CATEGORY_ORDER` is removed. `CATEGORY_LABELS` gains `appearance: 'Appearance'`. `listPaletteIds()` and `listCommands()` keep their meaning: every registry entry. | 06 "Context-aware"; D-137, D-139 |
| `APPEARANCE` | `features/settings/useSettingsPage.ts` exports `putSettingsNamespace(queryClient, namespace, patch): Promise<void>`, extracted from `flushPut` (`:68-88`) with the same five steps: parse, `PUT`, `applyDocumentTheme` when the patch has `theme`, invalidate the namespace, and invalidate dependencies after an `ffmpeg_path` change. `flushPut` calls it. A new `registry/appearance.ts` exports `setAppearance(theme: UiTheme): void`, which calls `putSettingsNamespace(queryClient, 'ui', { theme })` and catches any error into `logRenderer('ERROR', 'Appearance: <message>')`. The registry gains `appearance:dark` ("Appearance: Dark", `Ctrl+Shift+D`) and `appearance:light` ("Appearance: Light", `Ctrl+Shift+L`), category `'appearance'`, keywords `['theme', 'appearance', 'dark' \| 'light']`, each calling `setAppearance`. `commandRegistry.ts` never contains the text `apiFetch` (AC-20.13, AC-21.13, AC-22.19, AC-33.13). | 06 "Appearance" (triage D-88); D-141 |
| `CONFIRM_ROUTE` | `download-commands.ts` exports `DOWNLOAD_CONFIRM_EVENT = 'av-kit:download:confirm'`, and `convert-commands.ts` exports `CONVERT_CONFIRM_EVENT = 'av-kit:convert:confirm'`. Both are separate exports, so the pinned `DOWNLOAD_EVENTS`/`CONVERT_EVENTS` keys (AC-46.1a, AC-45.4a) are unchanged. `deliverPaletteClear` and `deliverPaletteCancel` in both modules keep their names and run `navigateAndDeliver(() => window.dispatchEvent(new CustomEvent(<CONFIRM_EVENT>, { detail: { kind: 'clear' \| 'cancel' } })))`, with no API call. Each page listens and calls `setConfirm({ kind })`. `DownloadConfirm` and `ConvertConfirm` gain `{ kind: 'cancel' }`. Its `confirmCopy` is `{ title: 'Cancel active downloads?' \| 'Cancel active conversions?', description: 'Work in progress stops. Files already on disk stay there.', confirmLabel: 'Cancel downloads' \| 'Cancel conversions' }`, and the page's `ConfirmModal` gets `cancelLabel="Keep running"` for that kind only. Confirm runs the page's existing `cancelDownload`/`cancelConversions` (or its clear-all path for `clear`) through `run`. | 06 "Destructive" (triage D-79); D-140 |
| `LABELS` | Registry labels: `download:sabr_check` "Check YouTube quality limit" (keywords gain `sabr`); `tts:prepare` "Preview cleaned text"; `download:add` "Enter download URL"; `transcript:add` "Enter transcript channel URL"; `nav:collapse` "Toggle sidebar". The other labels are unchanged. `tts-commands.ts`: `deliverPalettePrepare` and `deliverPaletteGenerate` click `preview-cleanup-btn` and `generate-btn` only when the element is an enabled `HTMLButtonElement`, and otherwise do nothing. The `postGenerate` fallback with `voice: 'af_heart'` and the direct `postPrepare` call are removed. | 06 "Labels" (triage D-87); D-142 |
| `CHECK_DEPS_ROUTE` | `settings:check_deps` stays global (no `page`). Its action navigates to `/settings` when the current page is not Settings, then dispatches `SETTINGS_EVENTS.checkDeps` after two `requestAnimationFrame`s (the `navigateAndDeliver` pattern). `SettingsPage`'s listener (`:388`) is unchanged. | D-143 |
| `CONVERT_BROWSE` | `convert-commands.ts` exports `CONVERT_BROWSE_EVENT = 'av-kit:convert:browse'` and `deliverPaletteBrowse()` (`navigateAndDeliver` to the page's `browseForFiles`, `ConvertPage.tsx:452`, through a page listener). The registry gains `convert:browse` ("Browse files", `page: '/convert'`) in its own `CONVERT_PALETTE_IDS` (`commandRegistry.ts:42`). The feature module's pinned `CONVERT_PALETTE_IDS` is unchanged. | 06 §Common shortcuts "Core set"; D-146 |
| `INDEX_AMEND` | **06** (row 1): the §Command palette "Wiring" row (`:313`) reads "Ctrl+K / header field; every registry chord is bound from the registry (§Shortcut binding)"; the "Type" row (`:314`) adds `appearance` to the category union and names `page`, `stateful` and `palette`; the "Inventory" row (`:315`) reads "Palette-eligible actions are `Palette = yes` rows; the palette lists them by the context-aware model (§Command palette curation)". **`gui-actions-index.md`** (row 1 legend, row 5 rows): the legend line "**Palette-eligible** ≠ **all actions**…" (`:5`) gains "Eligible rows are listed per page and state (06 §Command palette curation)". New rows: `appearance:dark` and `appearance:light` (Palette `yes`, `PUT /settings/{namespace}`), after `settings:check_deps` (`:99`); `page:primary` (Trigger `Ctrl+Enter`, Palette `no`), after `help:toggle` (`:118`). The `convert:browse` row (`:64`) becomes Palette `yes`. Row 7 adds the chords to the Trigger cells (`HINTS`). **Audit:** every registry entry without `palette: false` has exactly one index row with Palette `yes`, and every Palette `yes` row is a registry id (AC-23.18). | 06 "Index" (spec amendment under triage D-87); D-144 |
| `CLIPBOARD_RIDER` | `gui-actions-audit.test.ts` `resolveIpcChannel` (`:66-79`) gains `if (cell.includes('writeClipboardText')) return 'write-clipboard-text'`, placed after the `getMcpSetupPrompt` case. `gui-actions-index.md` gains, after `settings:start_minimized` (`:109`), `settings:copy_espeak_link` (Copy link, `tts-espeak-copy-link-btn`) and `settings:copy_log_path` (Copy path, `settings-copy-log-path`), both `IPC writeClipboardText`, Palette `no`. `SETTINGS_HELP_TESTIDS` (`:29-47`) maps both test ids to the rows. `ui/tests/e2e/test-ids.ts` gains, after the MEU-93 block, `// MEU-96 Palette curation (additive IDs).` and `export const SETTINGS_COPY_LOG_PATH = 'settings-copy-log-path'`. | known issue `GUI-AUDIT-CLIPBOARD-RESOLVER`; grouping D-99; D-145 |
| `CHORD_TABLE` | Registry chords after MEU-97 (all through `SHORTCUT_MAP`). Navigation, already present: `nav:downloader` Ctrl+1, `nav:transcript` Ctrl+2, `nav:tts` Ctrl+3, `nav:convert` Ctrl+4, `nav:capture` Ctrl+5, `nav:settings` `Ctrl+,`, `nav:collapse` Ctrl+B. Added by MEU-96: `appearance:dark` Ctrl+Shift+D, `appearance:light` Ctrl+Shift+L. Added by MEU-97: `download:add` Ctrl+L (page `/`); `transcript:add` Ctrl+L (page `/transcript`); `convert:browse` Ctrl+O (page `/convert`); `capture:save` Ctrl+S (page `/capture`, stateful); `page:primary` Ctrl+Enter (global); `console:toggle` Ctrl+J; `help:toggle` F1. | 06 §Common shortcuts "Core set" (triage D-89); D-146 |
| `PAGE_PRIMARY` | `registry/shortcuts.ts` exports `PAGE_PRIMARY_CONTROL: Record<ShellPage, string \| null>`: `'/'` `add-btn`, `'/transcript'` `add-btn`, `'/tts'` `generate-btn`, `'/convert'` `convert-add`, `'/capture'` `capture-region`, `'/settings'` `null`. The registry entry `page:primary` ("Run page action", global, `palette: false`, `Ctrl+Enter`) clicks `document.querySelector('[data-testid="<id>"]')` for the current page only when it is an enabled `HTMLButtonElement`; otherwise it does nothing. | 06 "Core set" ("Ctrl+Enter page primary action"); D-146 |
| `HINTS` | `registry/shortcuts.ts` exports `BOUND_CONTROLS: ReadonlyArray<{ testid: string; commandId: string }>`, which lists every rendered control that a chord performs: the seven nav items; `header-console-btn` (`console:toggle`); the `help-card` toggle (`help:toggle`); `url-input` (`download:add`); `channel-input` (`transcript:add`); `add-btn`, `generate-btn`, `convert-add` and `capture-region` (`page:primary`); `convert-browse` (`convert:browse`); `capture-save` (`capture:save`); `theme-dark-btn` and `theme-light-btn` (`appearance:*`). Each control carries `aria-keyshortcuts={ariaKeyshortcuts(chord)}` and shows the chord in its hint. A `Tooltip`-wrapped control (`ToolbarIconButton`) gets a new optional `shortcut` prop, giving the label `${name} (${chord})` (no `title`). Any other control gets `title={`${name} (${chord})`}`, where `name` is its visible text or `aria-label`. The palette button `header-palette-btn` is not in `BOUND_CONTROLS`: Ctrl+K is shell-owned and has no registry entry (`RESERVED_CHORDS`), and the button keeps its existing hint (`Header.tsx:73`). | 06 "Hints" (triage D-89; WAI-ARIA R-b); D-147 |
| `PALETTE_ENTER` | `CommandPalette`'s `Enter` case (`CommandPalette.tsx:134`) runs the highlighted command only when `ctrlKey`, `metaKey`, `altKey` and `shiftKey` are all false. A modified Enter returns at once, without `preventDefault` or `stopPropagation`, so it reaches the `window` listener, where Ctrl+Enter runs `page:primary` and closes the palette (`SHORTCUT_HANDLER`). Plain Enter, Escape and the arrow keys are unchanged. | 06 "Core set" (Ctrl+Enter); D-151 |
| `CAPTURE_SAVE_ROUTE` | `CAPTURE_COMMANDS.save` (`capture-commands.ts:172`) keeps its `navigateAndDeliver` wrapper and clicks `[data-testid="capture-save"]` when it is an enabled `HTMLButtonElement`; otherwise it does nothing. It no longer calls `saveAnnotations` itself, so Ctrl+S, the palette and the button all run `saveOverlay` (`CapturePage.tsx:1328`), which marks the shot saved after a successful POST. `saveAnnotations` and its `setCaptureSaveAllowed` gate are unchanged, so the AC-60.10 refusals still hold. | 06 "Core set" (Ctrl+S saves as the button does); D-152 |
| `TEST_AMENDMENTS` | TA-1, TA-2, TA-5 and TA-6 rewrite the four retained scenarios that select another page's entry command from off-page, which `PALETTE_LIST` forbids (D-137). Each keeps its W-id and its final focus or zero-POST assertions, and takes one shape: (a) off-page, the palette filled with the entry's id has no button with the entry's label (`toHaveCount(0)`); (b) the palette's global nav entry is activated (`page.getByRole('dialog').getByRole('button', { name: '<page label>', exact: true })`, the `command-palette-nav.spec.ts:45` form) and the hash is the owning page's; (c) the palette is reopened, filled with the id, and the entry is activated on its page. **TA-1** `ui/tests/e2e/download-queue.test.ts:590-599` (W1-6): (a) on Transcript, `download:add` lists no "Enter download URL"; (b) "Downloader" gives `#/`; (c) "Enter download URL" (was `'Focus download URL'`) is activated and `url-input` is focused. **TA-2** `ui/tests/e2e/transcript-queue.test.ts:482-491` (W2-6): (a) on Downloader, `transcript:add` lists no "Enter transcript channel URL"; (b) "Transcript" gives `#/transcript`; (c) the fill text `'Focus transcript channel URL'` becomes `'transcript:add'`, "Enter transcript channel URL" is activated and `channel-input` is focused. **TA-5** `ui/tests/e2e/convert-queue.test.ts:740-754` (W8-6): (a) on Downloader, `convert:add` lists no "Add conversion files"; (b) "Convert" gives `#/convert`; (c) "Add conversion files" is activated, `convert-dropzone` is focused, and `__e2eConversionPosts` and `seam.posts.count()` stay 0. **TA-6** `ui/tests/e2e/capture-inbox.test.ts:351-367` (W9-6): (a) on Downloader, `capture:region` lists no "Capture region"; (b) "Capture" gives `#/capture` and `capture-page` is visible; (c) "Capture region" is activated, `capture-page` stays visible and `capturePostCount` stays 0 across the whole test. In TA-1 and TA-2 the title's "off-route" becomes "on its page"; the other titles are unchanged. **TA-3** `ui/tests/unit/capture-page.test.ts:178-179` (AC-39.2): the two AppShell clauses `toMatch(/Ctrl\+5\|event\.key === '5'/)` and `toMatch(/navigateShell\(['"]\/capture['"]\)/)` become `expect(shell).toMatch(/createShortcutHandler/)` and `expect(readRequired(registryPath)).toMatch(/navigateShell\(['"]\/capture['"]\)/)`. The test's `const registry` is declared at `:183`, after these lines, so the amendment reads the file inline rather than referencing it early (TS2448); `:180` (`not.toMatch(/Ctrl\+5[\s\S]{0,200}capture:region/)`) stays on AppShell. **TA-4** `ui/tests/unit/convert-page.test.ts:182-183` (AC-33.2): the same change for `Ctrl+4` and `/convert`, also reading `registryPath` inline (its `const registry` is at `:187`); `:184` stays. TA-3 and TA-4 change only the lines they name; TA-1, TA-2, TA-5 and TA-6 change only their own scenario's body and title. | Local Canon |
| `CENSUS_PATTERNS` | Row 1 greps `ui/tests`, `tests` and `mcp-server/tests` for: `Collapse rail`, `Check SABR`, `Preview TTS cleanup`, `Focus download URL`, `Focus transcript channel URL`, `Toggle console`, `Toggle help`, `Generate TTS`, `af_heart`, `postGenerate`, `postPrepare`, `listCommands`, `listPaletteIds`, `getCommand`, `CATEGORY_ORDER`, `CATEGORY_LABELS`, `handleGlobalShortcut`, `event.key === '4'`, `event.key === '5'`, `Ctrl+4`, `Ctrl+5`, `Ctrl+B`, `keydown`, `aria-keyshortcuts`, `title=`, `deliverPaletteClear`, `deliverPaletteCancel`, `clearDownloads`, `cancelDownload`, `confirmCopy`, `confirm-modal`, `CommandRegistryEntry`, `category:`, `convert:browse`, `SETTINGS_HELP_TESTIDS`, `resolveIpcChannel`, `writeClipboardText`, `flushPut`, `ToolbarIconButton`, `check_deps`, `command-palette-input` and `COMMAND_PALETTE_INPUT` (every scenario that drives the palette, so each off-page selection is found). Each hit gets a disposition: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. | Local Canon (Session 35/40 census) |
| `PRODUCT_SCOPE` | The files this plan may change are exactly the Files Modified rows below plus the hub and state files; `session-gate.ps1` `scope-paths` holds the same allow-list. | grouping `:90-94` |

### MEU-95 — `gui-shortcut-binding`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `CommandRegistryEntry.shortcut` | `CHORD_FORMAT` | normalizes to non-`null`; not in `RESERVED_CHORDS`; unique per `SHORTCUT_MAP` key | `buildShortcutMap` throws on any violation |
| Renderer `window` `keydown` | `SHORTCUT_HANDLER` | `repeat`, `isComposing` and modifier-only keys ignored | unmatched chords are not prevented |
| REST, OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-95.1 | unit | `CHORD_FORMAT` (`shortcuts.test.ts`, `import * as sc` from `registry/shortcuts`; `typeof` first). `normalizeChord`: `'ctrl+b'` → `'Ctrl+B'`, `'Meta+1'` → `'Ctrl+1'`, `'Shift+Ctrl+d'` → `'Ctrl+Shift+D'`, `'Ctrl++'` → `'Ctrl+Plus'`, `'Ctrl+,'` → `'Ctrl+,'`, `'f1'` → `'F1'`; `''`, `'Ctrl+'`, `'Ctrl+Ctrl+A'` and `'Hyper+A'` → `null`. `chordFromEvent` for `KeyboardEvent('keydown', { key: 'l', ctrlKey: true })` → `'Ctrl+L'`, for `{ key: 'Control', ctrlKey: true }` → `null`, for `{ key: 'F1' }` → `'F1'`. `ariaKeyshortcuts('Ctrl+Shift+D')` → `'Control+Shift+D'`. | 06 "Registry-driven"; `CHORD_FORMAT` | `'Ctrl+Ctrl+A'` is `null`, not `'Ctrl+A'` |
| AC-95.2 | unit | `SHORTCUT_MAP`: `buildShortcutMap` throws (message contains the chord) for each fixture: two global entries on `Ctrl+B`; a global and a page entry on `Ctrl+L`; an entry on `Ctrl+C` (reserved); an entry on `Ctrl+` (invalid). Two entries on `Ctrl+L` for pages `/` and `/transcript` build. `buildShortcutMap(listCommands())` does not throw, and its size equals the number of registry entries with a `shortcut`. Every member of `RESERVED_CHORDS` is a fixed point of `normalizeChord`. | 06 "Tests" (no two entries share a chord); `RESERVED_CHORDS` | The baseline has no map, so a duplicate chord in the registry is never caught |
| AC-95.3 | unit | Dispatch: for every registry entry with a `shortcut`, a copy of `listCommands()` with that entry's `action` replaced by a spy, passed to `createShortcutHandler` (`getPage` → the entry's `page` or `'/'`, `getState` → every id `true`), receives a synthetic `keydown` for the chord. The handler returns `true`, calls `preventDefault`, and the spy is called once while no other entry's action runs. An unbound chord (`Ctrl+Q`) returns `false` and is not prevented. | 06 "Tests" ("every registry entry with a `shortcut` dispatches its action") | `Ctrl+Q` is not prevented |
| AC-95.4 | unit | Guards: `repeat: true` and `isComposing: true` return `false`. With a `<div aria-modal="true">` in the document, `Ctrl+2` returns `false`. With `<div aria-modal="true" data-testid="command-palette">` and `isPaletteOpen` → `true`, `Ctrl+2` runs the action and calls `closePalette` once before it. A `stateful` page entry whose state is not `true` returns `false`. | `SHORTCUT_HANDLER` | Without the modal, the same `Ctrl+2` runs |
| AC-95.5 | unit | Text fields: with focus in an `<input>` and in a `<textarea>`, `Ctrl+2` runs `nav:transcript` and is prevented; `Ctrl+A` and plain `Enter` in the same input return `false` and are not prevented. No `SHORTCUT_MAP` key starts with `Enter@` or a field editing chord (`Ctrl+A/C/V/X/Z`). | 06 "Text fields" | `Ctrl+A` in an input keeps its default |
| AC-95.6 | unit | `SHELL_WIRING` (`app-shell-wiring.test.ts` harness, `AppShell` rendered with the existing `window.api` stub): `Ctrl+1`, `Ctrl+2`, `Ctrl+3`, `Ctrl+4`, `Ctrl+5` and `Ctrl+,` set `window.location.hash` to `#/`, `#/transcript`, `#/tts`, `#/convert`, `#/capture` and `#/settings`; `Ctrl+B` toggles the rail (`nav-collapse` `aria-label` flips between "Collapse sidebar" and "Expand sidebar"); `Ctrl+K` still opens `command-palette`. Source: `AppShell.tsx` contains `createShortcutHandler` and neither `event.key === '4'` nor `event.key === '5'`; `addEventListener('keydown'` appears once and only on `window`. TA-3 and TA-4 apply. | 06 "Advertised set", "Registry-driven" | The baseline AppShell leaves `Ctrl+1` unhandled (the hash is unchanged) |
| AC-95.7 | unit | `NAV_HINTS` (`shortcuts.test.ts`, `NavRail` rendered expanded and collapsed): for each `SHELL_NAV` item, `getCommand(id)?.shortcut` equals `item.shortcut`; its button has `aria-keyshortcuts` equal to `ariaKeyshortcuts(item.shortcut)` and a `title` that contains `item.shortcut`, in both states. | 06 "Hints"; known issue (rail labels) | The baseline rail has no `title` when expanded |
| AC-95.8 | integration | Electron (`keyboard-shortcuts.test.ts`, new): from Downloader, `Ctrl+2`, `Ctrl+3`, `Ctrl+4`, `Ctrl+5`, `Ctrl+,` and `Ctrl+1` reach `#/transcript`, `#/tts`, `#/convert`, `#/capture`, `#/settings` and `#/`, and each page's root test id is visible; `Ctrl+B` adds `nav-rail--collapsed` to the rail and a second `Ctrl+B` removes it; with focus in `url-input`, `Ctrl+3` reaches `#/tts`. | 06 "Tests" ("Electron: each nav chord reaches its route") | Red on the baseline renderer: `Ctrl+2` leaves the hash at `#/` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Keydown map from the registry | Spec | 06 "Registry-driven" (`SHORTCUT_MAP`, `SHELL_WIRING`) |
| Chord text format | Local Canon / Research-backed | Registry strings already use `Ctrl+X`; `aria-keyshortcuts` needs `Control` (R-b; `CHORD_FORMAT`) |
| Chords the app must not take | Research-backed | Electron default menu roles (R-a); 06 "Text fields", "No collisions" (`RESERVED_CHORDS`, D-136) |
| A chord while a confirm dialog is open | Local Canon | The `ConfirmModal` (`aria-modal`, `ConfirmModal.tsx:127`) is the user's current decision; chords are suspended (`MODAL_GUARD`, D-134) |
| A chord while the palette is open | Local Canon | The palette is the shell's own overlay; the chord runs and closes it (D-134) |
| Hints on the rail | Spec | 06 "Hints" (`NAV_HINTS`) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/registry/shortcuts.ts` | new | `SHELL_PAGE`, `CHORD_FORMAT`, `RESERVED_CHORDS`, `SHORTCUT_MAP`, `SHORTCUT_HANDLER` (MEU-96 adds `PALETTE_LIST`; MEU-97 adds `PAGE_PRIMARY_CONTROL`, `BOUND_CONTROLS`) |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `CommandRegistryEntry` fields (`AVAILABILITY`, used from MEU-96 on) |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `SHELL_WIRING` |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modify | `NAV_HINTS` |
| `ui/tests/unit/shortcuts.test.ts` | new | AC-95.1–95.5, AC-95.7 |
| `ui/tests/unit/app-shell-wiring.test.ts` | modify | AC-95.6 |
| `ui/tests/unit/capture-page.test.ts` | modify | TA-3 |
| `ui/tests/unit/convert-page.test.ts` | modify | TA-4 |
| `ui/tests/e2e/keyboard-shortcuts.test.ts` | new | AC-95.8 |

### MEU-96 — `gui-command-palette-curation` (with the rider)

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `COMMAND_STATE` records | `registry/command-state.ts` | keys are registry ids; values boolean; one record per `ShellPage` | unknown keys are ignored by `paletteCommands` |
| `av-kit:download:confirm`, `av-kit:convert:confirm` | `CONFIRM_ROUTE` | `detail.kind` is `'clear'` or `'cancel'` | any other `kind` is ignored |
| `av-kit:convert:browse` | `CONVERT_BROWSE` | no detail | n/a |
| REST `PUT /settings/ui` (Appearance) | existing `ui` namespace (unchanged) | `{ theme: 'dark' \| 'light' }` through `parseSettingsPut` | unchanged |
| REST `DELETE /downloads`, `POST /downloads/cancel`, conversion equivalents | unchanged | called only after Confirm | unchanged |
| OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-96.1 | unit | `PALETTE_LIST` pure (`palette-curation.test.tsx`, fixtures): a `palette: false` entry is never listed; a stateful `/convert` entry is listed only for `page === '/convert'` with its state `true`; with both `x:pause` and `x:resume` `true`, only `x:pause` is listed; entries of the current page come first and keep registry order; an entry command owned by `/convert` is listed for `page === '/convert'` and absent for `'/'`; with `page === null`, only global commands are listed. | 06 "Context-aware"; D-137, D-139 | A stateful entry with state `false` on its own page is absent |
| AC-96.2 | unit | Per-page contents with the real registry and an empty state: for each `ShellPage`, the list contains every global id (`nav:*`, `console:toggle`, `help:toggle`, `appearance:dark`, `appearance:light`, `settings:check_deps`), begins with that page's own entry commands, contains no stateful id, and contains no command owned by another page (on `/settings`: no `download:add`, `convert:browse` or `capture:region`). With `/` and `{ 'download:start': true, 'download:clear': true }`, it adds exactly those two. `page:primary` is never listed. | 06 "Tests" (palette contents per page and per state) | The baseline palette lists `download:clear` and `download:add` on `/settings` |
| AC-96.3 | unit | `COMMAND_STATE`: publish, get, subscribe and clear behave as defined. A publish with unchanged values does not notify. A component using `usePublishCommandState('/tts', …)` clears `/tts` on unmount. `getCommandState` returns the same object between calls without a publish. | `COMMAND_STATE` | A second identical publish fires no listener |
| AC-96.4 | unit | Recompute: `CommandPalette` rendered open on `#/`: the first group is Download. After `navigateShell('/convert')` the first group is Convert, with no remount. After `publishCommandState('/convert', { 'convert:start': true })`, the `Start conversions` option appears while the palette stays open. `CATEGORY_LABELS.appearance` is `'Appearance'`. | 06 "Context-aware" ("recomputes") | The baseline list never changes while open |
| AC-96.5 | unit | `PAGE_STATE`, in each page's behaviour harness (`downloader-page.behavior.test.ts`, `tts-page.behavior.test.ts`, `convert-page.behavior.test.ts`): Downloader with the processor `Processing` and an active item publishes `download:pause` `true` and `download:resume` `false`; with `Paused`, the reverse; with an empty queue, `download:start`, `download:cancel` and `download:clear` are `false`. TTS with empty text publishes `tts:prepare` `false`, and after typing `hello` publishes `true`. Convert with an empty queue publishes `convert:clear` `false`. | `PAGE_STATE`; D-139 | — |
| AC-96.6 | unit | `APPEARANCE`: `putSettingsNamespace(qc, 'ui', { theme: 'light' })` sends one `PUT` to `SETTINGS_NAMESPACE_PATHS.ui` with body `{ theme: 'light' }`, removes the root `dark` class and invalidates `['settings', 'ui']`. Running `getCommand('appearance:dark')!.action()` with `putSettingsNamespace` mocked calls it once with `'ui'` and `{ theme: 'dark' }`. A rejected put logs one `ERROR` line through `logRenderer` and throws nothing. `commandRegistry.ts` does not match `/apiFetch/`. Both entries have `category: 'appearance'` and the chords in `CHORD_TABLE`. | 06 "Appearance" (triage D-88); 06 "Tests" ("Appearance commands set the theme") | A rejected put rejects nothing to the caller and changes no theme class |
| AC-96.7 | unit | `CONFIRM_ROUTE`. Commands (`palette-curation.test.tsx`): with `fetch` spied, `DOWNLOAD_COMMANDS.clear()` and `.cancel()` and `CONVERT_COMMANDS.clear()` and `.cancel()` dispatch their confirm event with the right `kind` after two animation frames and make no `fetch` call. Downloader page (`downloader-page.behavior.test.ts`): the `{ kind: 'clear' }` event shows `confirm-modal` with confirm text "Clear all"; `confirm-modal-cancel` closes it with no `DELETE /downloads`; a second event plus `confirm-modal-confirm` sends one. The `{ kind: 'cancel' }` event shows "Cancel downloads" and a cancel button "Keep running"; Confirm sends one `POST /downloads/cancel`. Convert (`convert-page.behavior.test.ts`): the same for `cancel`. AC-46.1a and AC-45.4a stay green. | 06 "Destructive" (triage D-79) | The baseline `clear()` sends `DELETE /downloads` with no modal |
| AC-96.8 | unit | `LABELS`: the five renamed labels are exact; `download:sabr_check` keywords contain `sabr`. `tts-commands.ts` does not contain `af_heart`, `postGenerate(` or `postPrepare(` inside `deliverPalette*`. On a document with no `generate-btn`, `TTS_COMMANDS.generate()` makes no `fetch` call; with a disabled `preview-cleanup-btn`, `TTS_COMMANDS.prepare()` does not click it; with an enabled one, it clicks it once. | 06 "Labels" (triage D-87) | The baseline `generate()` posts `voice: 'af_heart'` |
| AC-96.9 | unit | `CHECK_DEPS_ROUTE`: on `#/`, `getCommand('settings:check_deps')!.action()` sets `#/settings`, and `SETTINGS_EVENTS.checkDeps` fires once after two animation frames, not before. On `#/settings` it fires without a hash change. | D-143 | The baseline action dispatches with no listener mounted off-route |
| AC-96.10 | unit | `INDEX_AMEND` (`gui-actions-audit.test.ts`, MEU-96 describe): 06 `:313-315` contain the amended text; the index legend contains "Eligible rows are listed per page and state"; `appearance:dark`, `appearance:light` and `page:primary` rows exist once, in place; `convert:browse` is Palette `yes`. Bidirectional: the set of registry ids without `palette: false` equals the set of Palette `yes` ids. AC-23.18–AC-23.20 stay green. | 06 "Index" | Removing the `appearance:light` row fails the set equality |
| AC-96.11 | unit | `CLIPBOARD_RIDER`: `resolveIpcChannel('IPC writeClipboardText')` is `'write-clipboard-text'`; both new rows exist after `settings:start_minimized`; AC-23.20 resolves both to a channel in `RENDERER_TO_MAIN_CHANNELS` that the preload invokes; both test ids are in `test-ids.ts` and in Settings source; `SETTINGS_HELP_TESTIDS` maps them. | known issue `GUI-AUDIT-CLIPBOARD-RESOLVER` | The baseline resolver returns no channel for the cell |
| AC-96.12 | integration | Electron, palette Clear (`download-queue.test.ts`, `installSeam(page, { items: seededQueue() })`): open the palette, type "Clear", activate "Clear download queue": `confirm-modal` is visible with confirm text "Clear all"; `confirm-modal-cancel` closes it, the queue still has its rows, and `seam.callsTo('/downloads', 'DELETE')` is empty. Again with `confirm-modal-confirm`: one `DELETE`. | 06 "Tests" ("palette Clear opens the confirm and Cancel keeps the queue") | Red on the baseline renderer: no `confirm-modal` appears |
| AC-96.13 | integration | Electron, Appearance (`settings.test.ts`, the settings seam answering `{ theme: 'dark' }`): `Ctrl+Shift+L` removes `dark` from `html`, and the seam records one `PUT …/settings/ui` with `theme: 'light'`. Then the palette's "Appearance: Dark" sets `dark` with one `PUT` with `theme: 'dark'`. | 06 "Appearance"; triage D-88 | Red on the baseline renderer: `html` keeps `dark` after `Ctrl+Shift+L` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which commands are listed where | Human-approved | Triage D-87 (06 "Context-aware"); page-owned commands only on their page (`AVAILABILITY`, D-137) |
| "Commands that cannot run now hidden" | Human-approved / Local Canon | A command runs now iff its page control is enabled (`PAGE_STATE`, D-138) |
| Pause/Resume as one state-aware entry | Human-approved | Triage D-87; two ids, at most one listed (D-139) |
| Appearance path | Human-approved | Triage D-88: the Settings path (`APPEARANCE`, D-141) |
| Destructive confirm | Spec | Triage D-79 (`CONFIRM_ROUTE`, D-140) |
| Label words | Spec | Triage D-87 examples (`LABELS`, D-142) |
| Index model | Spec amendment | 06 "Index" (`INDEX_AMEND`, D-144) |
| Rider | Local Canon | Grouping D-99 (`CLIPBOARD_RIDER`, D-145) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/registry/shortcuts.ts` | modify | `PALETTE_LIST` |
| `ui/src/renderer/src/registry/command-state.ts` | new | `COMMAND_STATE` |
| `ui/src/renderer/src/registry/appearance.ts` | new | `setAppearance` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `AVAILABILITY` fields on entries; `appearance:*`, `convert:browse`; `LABELS`; `CHECK_DEPS_ROUTE` |
| `ui/src/renderer/src/components/CommandPalette.tsx` | modify | `PALETTE_LIST` wiring; `CATEGORY_LABELS.appearance`; `CATEGORY_ORDER` removed |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `convert:browse` listener |
| `ui/src/renderer/src/features/settings/useSettingsPage.ts` | modify | `putSettingsNamespace` extracted from `flushPut` |
| `ui/src/renderer/src/features/downloader/download-commands.ts` | modify | `DOWNLOAD_CONFIRM_EVENT`; palette clear and cancel request the confirm |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | confirm listener and `'cancel'` kind; `PAGE_STATE` publish |
| `ui/src/renderer/src/features/converter/convert-commands.ts` | modify | `CONVERT_CONFIRM_EVENT`, `CONVERT_BROWSE_EVENT`, `deliverPaletteBrowse` |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | confirm and browse listeners; `'cancel'` kind; `PAGE_STATE` publish |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify | `PAGE_STATE` publish |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | `PAGE_STATE` publish |
| `ui/src/renderer/src/features/tts/tts-commands.ts` | modify | `LABELS` (click-only palette delivery) |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `PAGE_STATE` publish |
| `ui/tests/unit/palette-curation.test.tsx` | new | AC-96.1–96.4, AC-96.6, the command part of AC-96.7, AC-96.8, AC-96.9 |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modify | AC-96.5, AC-96.7 (Downloader) |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | AC-96.5, AC-96.7 (Convert) |
| `ui/tests/unit/tts-page.behavior.test.ts` | modify | AC-96.5 (TTS) |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify | AC-96.10, AC-96.11 (`CLIPBOARD_RIDER`) |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-96 block |
| `ui/tests/e2e/download-queue.test.ts` | modify | AC-96.12; TA-1 |
| `ui/tests/e2e/transcript-queue.test.ts` | modify | TA-2 |
| `ui/tests/e2e/convert-queue.test.ts` | modify | TA-5 (W8-6) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | TA-6 (W9-6) |
| `ui/tests/e2e/settings.test.ts` | modify | AC-96.13 |
| `docs/build-plan/gui-actions-index.md` | modify | `INDEX_AMEND` rows; `CLIPBOARD_RIDER` rows |

### MEU-97 — `gui-common-shortcuts`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| New registry chords | `CHORD_TABLE` | pass `SHORTCUT_MAP` | n/a |
| `aria-keyshortcuts`, `title`, tooltip label on bound controls | `HINTS` | `aria-keyshortcuts` is `ariaKeyshortcuts(chord)` | n/a |
| `ToolbarIconButton` props | `HINTS` | `shortcut?: string`, optional and additive | without it the markup is unchanged |
| REST, OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-97.1 | unit | `CHORD_TABLE` (`shortcuts.test.ts`): for each row, `getCommand(id)?.shortcut` normalizes to the chord and `page` is as listed. `buildShortcutMap(listCommands())` builds. No key uses `F2`, `Ctrl+=`, `Ctrl+-`, `Ctrl+0` or `Ctrl+Plus`. | 06 "Core set", "No collisions" | `Ctrl+=` on any entry makes the build throw |
| AC-97.2 | unit | `PAGE_PRIMARY`: for each `ShellPage` with a control, a document with an enabled button of that test id is clicked once by `page:primary`; a disabled one is not; on `/settings` nothing is clicked. `page:primary` has `palette: false`. | 06 "Core set" (Ctrl+Enter) | A disabled `add-btn` gets no click |
| AC-97.3 | unit | Page scope: the handler with the real registry: `Ctrl+L` on `/convert`, `Ctrl+O` on `/`, and `Ctrl+S` on `/tts` return `false` and are not prevented. `Ctrl+S` on `/capture` with `capture:save` state `false` returns `false`; with `true` it runs `capture:save`. | 06 "Page scope" | — |
| AC-97.4 | unit | `HINTS`, where each control is rendered: `common-shortcuts.test.tsx` renders `Header`, `HelpCard` and `ToolbarIconButton`; the page controls are checked in `downloader-page.behavior.test.ts`, `transcript-page.behavior.test.ts`, `tts-page.behavior.test.ts`, `convert-page.behavior.test.ts` and `settings-page.test.ts`; `capture-region` and the `capture-save` `shortcut` prop are checked as source text in `capture-page.test.ts` (that file's existing style). Every `BOUND_CONTROLS` control has `aria-keyshortcuts` equal to `ariaKeyshortcuts(getCommand(commandId)!.shortcut!)` and a hint (`title`, or the `Tooltip` label) that contains the chord. `ToolbarIconButton` without `shortcut` renders no `aria-keyshortcuts`. | 06 "Hints" | The baseline `header-console-btn` has no `aria-keyshortcuts` |
| AC-97.5 | unit | Index triggers (`gui-actions-audit.test.ts`): each `CHORD_TABLE` id's index row has the chord in its Trigger cell. | 06 "Index"; `INDEX_AMEND` | The baseline `console:toggle` Trigger lacks `Ctrl+J` |
| AC-97.6 | integration | Electron (`keyboard-shortcuts.test.ts`): on Downloader, `Ctrl+L` focuses `url-input`; on Transcript, `channel-input`; on TTS, `Ctrl+L` leaves focus on `body` and the hash at `#/tts`. `Ctrl+J` shows the console panel, and a second press hides it. On Settings, `F1` flips the `help-card` toggle's `aria-expanded`. | 06 "Tests" ("each chord runs its action on its page and does nothing on another") | Red on the baseline renderer: `Ctrl+L` leaves focus on `body` |
| AC-97.7 | integration | Electron, Convert (`convert-queue.test.ts`, the existing seam): on Convert, `Ctrl+O` then `convert-add` gives one `convert-queue-row` (the E2E `showFilesDialog` stub). On Downloader, `Ctrl+O` leaves the hash at `#/`. | 06 "Core set" | Red on the baseline renderer: no row appears |
| AC-97.8 | integration | Electron, Capture (`capture-inbox.test.ts`, the AC-59.12 seam): after drawing one arrow, `Ctrl+S` posts one annotation set with the arrow, as a `capture-save` click does; afterwards `capture-save` is gone (the shot is clean) and a second `Ctrl+S` posts nothing. On a clean shot, `Ctrl+S` posts nothing. | 06 "Core set" | Red on the baseline renderer: nothing is posted |
| AC-97.9 | integration | Electron, Downloader (`download-queue.test.ts`): with `url-input` filled with a valid URL, `Ctrl+Enter` sends the same `POST /downloads` that `add-btn` sends; with `url-input` empty (`add-btn` disabled), `Ctrl+Enter` sends none. With a valid URL filled and the palette open after typing `console` (so `Toggle console` is highlighted), `Ctrl+Enter` sends exactly one `POST /downloads`, leaves the console panel hidden and closes the palette. | 06 "Core set" | Red on the baseline renderer: no `POST /downloads` |
| AC-97.10 | unit | `PALETTE_ENTER` (`common-shortcuts.test.tsx`): `CommandPalette` rendered open with a spied highlighted command. `Ctrl+Enter` on the palette input does not run it, and the event reaches a `window` listener with `defaultPrevented` false; plain `Enter` runs it once. | 06 "Core set" | Red on the row 5 tree: Ctrl+Enter runs the highlighted command |
| AC-97.11 | unit | `CAPTURE_SAVE_ROUTE` (`capture-page.behavior.test.ts`, the AC-60.10 harness): after one committed mark, `CAPTURE_COMMANDS.save()` posts once, then `capture-save` is unmounted, `getCommandState('/capture')['capture:save']` is not `true`, and a second `CAPTURE_COMMANDS.save()` posts nothing. The AC-60.10 tests stay green. | 06 "Core set" | Red on the row 5 tree: `capture-save` stays mounted after the post |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The core chord set | Human-approved | Triage D-89 (`CHORD_TABLE`, D-146) |
| "Page primary action" per page | Local Canon | Each page's primary-variant button (`PAGE_PRIMARY`, D-146) |
| Collisions | Human-approved / Research-backed | Triage D-89; Electron default menu roles (R-a; `RESERVED_CHORDS`) |
| Hint form | Spec / Research-backed | 06 "Hints"; WAI-ARIA `aria-keyshortcuts` (R-b; `HINTS`, D-147) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/registry/shortcuts.ts` | modify | `PAGE_PRIMARY_CONTROL`, `BOUND_CONTROLS` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `CHORD_TABLE` chords; `page:primary` |
| `ui/src/renderer/src/components/layout/Header.tsx` | modify | console button hint |
| `ui/src/renderer/src/components/help/HelpCard.tsx` | modify | toggle hint |
| `ui/src/renderer/src/features/capture/ToolbarIconButton.tsx` | modify | `shortcut` prop |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `capture-save` and `capture-region` hints |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `CAPTURE_CHORD_BUBBLE` (walkthrough EC-3) |
| `ui/src/renderer/src/features/capture/capture-commands.ts` | modify | `CAPTURE_SAVE_ROUTE` |
| `ui/src/renderer/src/components/CommandPalette.tsx` | modify | `PALETTE_ENTER` |
| `ui/src/renderer/src/features/downloader/DownloaderPage.tsx` | modify | `url-input`, `add-btn` hints |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify | `channel-input`, `add-btn` hints |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | `generate-btn` hint |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | `convert-browse`, `convert-add` hints |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | theme button hints |
| `ui/tests/unit/shortcuts.test.ts` | modify | AC-97.1–97.3 |
| `ui/tests/unit/common-shortcuts.test.tsx` | new | AC-97.4 (shell components), AC-97.10 |
| `ui/tests/unit/fixtures/chord-table.ts` | new | `CHORD_TABLE` rows shared by AC-97.1 and AC-97.5 (walkthrough EC-5) |
| `ui/tests/unit/helpers/bound-hint.ts` | new | `chordOf`, `expectBoundHint` for every AC-97.4 test (walkthrough EC-5) |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | AC-97.11 |
| `ui/tests/unit/downloader-page.behavior.test.ts` | modify | AC-97.4 (`url-input`, `add-btn`) |
| `ui/tests/unit/transcript-page.behavior.test.ts` | modify | AC-97.4 (`channel-input`, `add-btn`) |
| `ui/tests/unit/tts-page.behavior.test.ts` | modify | AC-97.4 (`generate-btn`) |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | AC-97.4 (`convert-browse`, `convert-add`) |
| `ui/tests/unit/settings-page.test.ts` | modify | AC-97.4 (theme buttons) |
| `ui/tests/unit/capture-page.test.ts` | modify | AC-97.4 (`capture-region`, `capture-save`, source text) |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify | AC-97.5 |
| `ui/tests/e2e/keyboard-shortcuts.test.ts` | modify | AC-97.6 |
| `ui/tests/e2e/convert-queue.test.ts` | modify | AC-97.7 |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-97.8 |
| `ui/tests/e2e/download-queue.test.ts` | modify | AC-97.9 |
| `docs/build-plan/gui-actions-index.md` | modify | Trigger cells name the chords |

If a page needs a file not listed here (for example a toolbar component that renders a listed test id), that is a scope change: record it as an Execution Correction Note and update the `scope-paths` allow-list in the same row (S5 otherwise).

### Hub and state files (rows 1, 9, H1-3, H2)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/06-gui.md` | modify (row 1, row 9) | `INDEX_AMEND` text at `:313-315` (row 1). Before each residual section's anchor in row 9: a `> **Delivered (Session 41).**` note per MEU naming this plan |
| `.agent/context/meu-status.yaml` | modify (row 9, H2-2) | MEU-95/96/97 `execution_plan` and `ready_for_review` (row 9, before the H1-2 gate binds this file); `approved` after review (H2-2, which re-runs `layout-canon` and `queue-canon`) |
| `docs/BUILD_PLAN.md` | generated | AUTOGEN regions written only by `meu_status.py render` |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 41 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | the four issues → `resolved` with the handoff links, after H1-7b approval (H2) |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` (H2-2); never hand-edited |
| `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md` | modify (H2-2) | Session 41 row `approved` with this plan folder |
| `docs/execution/metrics.md` | modify | the Session 41 row (H2-3) |

No `build-priority-matrix.md` edit: the rows for MEU-95 to MEU-97 already exist and the matrix has no status column.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| A confirm on each queue card's own Cancel and on Transcript Stop | out-of-scope | — | 06 "Destructive" names palette Clear and Cancel; the card buttons act on what the user just pointed at |
| A user-remappable keymap or a shortcuts help sheet | out-of-scope | — | Not in triage D-89 |
| Changing the Electron application menu | out-of-scope | — | `RESERVED_CHORDS` leaves the default menu as it is (D-136) |
| Capture's `globalShortcut` F2 and its zoom keys | out-of-scope | — | 06 "Registry-driven": they stay where they are, as collision constraints |
| Any REST, OpenAPI, IPC or MCP change | out-of-scope | — | Appearance uses the existing `PUT /settings/ui`; the rider adds index rows for an existing channel |

## BUILD_PLAN.md Audit

This project edits the D3 hub only through `meu_status.py` in row 9 (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s41-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s41-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-9[567]" -e "gui-keyboard-palette" -e "Delivered \(Session 41\)" docs/BUILD_PLAN.md docs/build-plan/06-gui.md .agent/context/meu-status.yaml *> C:/Temp/av-kit/s41-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s41-hub-rg.txt; exit $code
```

Row 9's deliverable is that the `rg` receipt shows the three 06 Delivered notes, MEU-95/96/97 with `execution_plan` set to this plan, and the rendered `BUILD_PLAN.md` lines; and that `render --check` exits 0.

## Verification Plan

All commands run from `P:/av-kit` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s41-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`.
- `PREREQS` (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-26-gui-keyboard-palette/baseline.sha`.
- The baseline receipts: `py-tests`, `ui-tests`, `mcp-tests`, `ui-build`, then `ui-electron` over `download-queue.test.ts`, `transcript-queue.test.ts`, `convert-queue.test.ts`, `capture-inbox.test.ts`, `settings.test.ts` and `command-palette-nav.spec.ts`. The baseline failed sets are recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression; a test passing at baseline that fails later is one. The Python baseline keeps the Session 40 rule for the environmental packaging tests (AC-24.10, AC-25.10, AC-25.7).

### 2. Red (rows 2, 4 and 6)

Each MEU's new and amended tests are written first. They must fail by assertion, or because a declared-new name does not exist yet (`red-check.py` `DECLARED_NEW`: `buildShortcutMap`, `createShortcutHandler`, `normalizeChord`, `chordFromEvent`, `ariaKeyshortcuts`, `paletteCommands`, `RESERVED_CHORDS`, `PAGE_PRIMARY_CONTROL`, `command-state`, `publishCommandState`, `usePublishCommandState`, `putSettingsNamespace`, `setAppearance`, and the new modules `shortcuts`, `command-state` and `appearance`).

- **Vitest imports are namespace imports** (`import * as sc from '../../src/renderer/src/registry/shortcuts'`). Each test first asserts `expect(typeof sc.buildShortcutMap).toBe('function')` (or the name's expected type), so a missing export fails as an assertion in that test instead of a `TypeError: … is not a function`, which `red-check.py` refuses. A module that does not exist yet (`registry/shortcuts.ts`, `registry/command-state.ts`, `registry/appearance.ts`) is loaded with a dynamic `import()` inside the test, after an `existsSync` assertion on its path, so a missing file fails one assertion instead of the whole file.
- **Electron tests assert `toBeVisible()` before acting on any new element**, and use `expect.poll` or `toHaveURL` for every chord effect, so a missing behaviour fails by `expect` instead of a `locator.click: Timeout`, which is refused. The checker refuses only `Test timeout of Nms exceeded`, `TimeoutError` and `locator|page|frame|elementHandle.<action>: Timeout`, plus `ECONNREFUSED` and `EADDRINUSE`.
- **No pytest Red:** this plan changes no Python.
- **Row 2 (MEU-95):** Vitest `-t "AC-95"` over `shortcuts.test.ts` and `app-shell-wiring.test.ts`, with TA-3 and TA-4 applied, then the UI build and Electron `--grep "AC-95"` over `keyboard-shortcuts.test.ts`, **on the baseline renderer**: the command refuses any `ui/src` change. AC-95.6, AC-95.7 and AC-95.8 must fail by `expect` (`--require`).
- **Row 4 (MEU-96):** Vitest `-t "AC-96"` over `palette-curation.test.tsx`, `gui-actions-audit.test.ts`, `downloader-page.behavior.test.ts`, `convert-page.behavior.test.ts` and `tts-page.behavior.test.ts`, then the build and Electron `--grep "AC-96"` over `download-queue.test.ts` and `settings.test.ts`, **on the row 3 tree**. Row 3's command ends by writing `row3-ui-src.json` (a SHA-256 per file under `ui/src`); row 4 recomputes it and refuses any `ui/src` file that was added, removed or changed since. AC-96.2, AC-96.7, AC-96.8, AC-96.12 and AC-96.13 must fail by `expect` (`--require`).
- **Row 6 (MEU-97):** Vitest `-t "AC-97"` over `shortcuts.test.ts`, `common-shortcuts.test.tsx`, `gui-actions-audit.test.ts`, the four page behaviour files, `settings-page.test.ts`, `capture-page.test.ts` and `capture-page.behavior.test.ts`, then the build and Electron `--grep "AC-97"` over `keyboard-shortcuts.test.ts`, `convert-queue.test.ts`, `capture-inbox.test.ts` and `download-queue.test.ts`, **on the row 5 tree** (`row5-ui-src.json`). AC-97.4, AC-97.6, AC-97.7, AC-97.8, AC-97.9, AC-97.10 and AC-97.11 must fail by `expect` (`--require`).

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit and exactly one failing-run summary (Vitest or Playwright);
- no hard setup failure anywhere in the receipt: an Electron launch failure, a test or action timeout, a refused connection or busy port, or Vitest unhandled errors;
- **every failure block is attributed:** the receipt is split into one block per failed test (Vitest `FAIL` headers, Playwright `N) title` headers), and the number of blocks equals the summary's failed count, so a failure that is not shown cannot hide. Every block carries at least one diagnostic, and **every** diagnostic in it is an assertion (`AssertionError`, `Error: expect(`) or a load/import error whose missing *subject* is exactly a declared-new name (or ends in one after a `.` or `/`). A `TypeError: … is not a function` is never attributed, even for a declared name. One unrelated diagnostic refuses the block, even beside a valid assertion;
- **`--require TITLE`**: each named test has its own failure block whose diagnostics are all assertions. A required test that passed, or failed only by a declared-new name, is refused. The title match is exact up to a non-digit (`AC-95.1` does not match `AC-95.10`).

Source-context and test-title lines never count. `red-check.py --selftest` runs 36 receipt fixtures, including the negative `vitest-not-a-function-is-unattributed` (R-2).

### 3. Targeted Green (rows 3, 5 and 7)

Each Green row runs its MEU's Vitest files plus the existing suites that pin the files it touches, then the build and the Electron specs whole. The task rows hold the exact commands.

- **Row 3:** `shortcuts.test.ts`, `app-shell-wiring.test.ts`, `capture-page.test.ts`, `convert-page.test.ts`, `command-palette.test.ts`, `shell-home.test.ts`, `header-toggles.test.ts`, `chrome-zorivest.test.ts`, `help-card.test.ts`; Electron `keyboard-shortcuts.test.ts`, `command-palette-nav.spec.ts`, `capture-inbox.test.ts`, `convert-queue.test.ts`.
- **Row 5:** `palette-curation.test.tsx`, `gui-actions-audit.test.ts`, `command-palette.test.ts`, `download-commands.test.ts`, `convert-commands.test.ts`, `downloader-page.test.ts`, `downloader-page.behavior.test.ts`, `convert-page.test.ts`, `convert-page.behavior.test.ts`, `transcript-page.test.ts`, `tts-page.test.ts`, `tts-page.behavior.test.ts`, `capture-page.test.ts`, `settings-emphasis.test.tsx`, `settings-page.test.ts`, `theme-selects.test.tsx`, `chrome-zorivest.test.ts`, `help-card.test.ts`; Electron `download-queue.test.ts`, `transcript-queue.test.ts`, `convert-queue.test.ts`, `capture-inbox.test.ts`, `settings.test.ts`, `tts-generate.test.ts`, `command-palette-nav.spec.ts` (TA-1, TA-2, TA-5 and TA-6 pass here, on the curated palette).
- **Row 7:** `shortcuts.test.ts`, `common-shortcuts.test.tsx`, `gui-actions-audit.test.ts`, `capture-toolbar.test.ts`, `tooltip.test.tsx`, `header-toggles.test.ts`, `help-card.test.ts`, `capture-page.test.ts`, `downloader-page.behavior.test.ts`, `transcript-page.behavior.test.ts`, `convert-page.behavior.test.ts`, `tts-page.behavior.test.ts`, `settings-page.test.ts`, `capture-page.behavior.test.ts` (AC-97.11 and AC-60.10), `command-palette.test.ts` (`PALETTE_ENTER`); Electron `keyboard-shortcuts.test.ts`, `convert-queue.test.ts`, `capture-inbox.test.ts`, `download-queue.test.ts`.

### 4. Session gate (rows 8, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `P:/av-kit`. It writes one receipt per step (`C:/Temp/av-kit/s41-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`. The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, then `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:** `py-tests` (whole suite, with the baseline rule for the environmental packaging tests: a packaging test is excused only if it appears as `FAILED <id>` in the row 0 receipt `s41-base-py.txt`, and a missing receipt excuses nothing; the gate prints the excused ids), `ui-tests` (no excused id), `mcp-build`, `mcp-tests` (the build first, because the tests load `mcp-server/dist`), `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite, because `AppShell`, the registry and the palette are on every page), then `e2e-repeat`: `test:e2e -- tests/e2e/keyboard-shortcuts.test.ts tests/e2e/download-queue.test.ts tests/e2e/convert-queue.test.ts tests/e2e/capture-inbox.test.ts tests/e2e/settings.test.ts --grep "AC-95|AC-96|AC-97" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm`, then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-gui-keyboard-palette/session-gate.ps1`, with the receipt pattern (task row 8).

The D6 `mcp-audit` runtime check is not a gate step: this plan changes no MCP action, schema or API; `mcp-build` and `mcp-tests` show the server still builds and passes.

### 5. `SCOPE_CHECK` (row 8)

- **`scope-paths`:** every path in `git diff --no-renames --name-only -z <baseline>` plus `git ls-files --others --exclude-standard -z` is a Files Modified row (product, test, hub and state files) or one of this project's artifacts (this plan folder, the handoffs, the reflection). With `--no-renames`, a rename shows its source deletion as well as its destination, so a move out of a disallowed path is caught. `-z` keeps paths with spaces or non-ASCII names whole (R-4). The allow-list in the script is the union of the Files Modified tables; changing either means changing both. The step also fails when `git rev-parse HEAD` differs from `baseline.sha` (S8).

### 6. OpenAPI drift (G8)

No `packages/api/` file changes. `openapi.committed.json` is not regenerated, and the `openapi` D6 check (`--check`) must pass in the gate. H1-4 proves the committed file is unchanged since `baseline.sha`: added, removed and changed schemas are all empty (any change is S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths:

- `validate_closeout_artifacts.py` per handoff, run twice: with `--handoff` + `--plan`, then with `--ac-coverage-only`;
- `durable_evidence.py --require-full`;
- the review-state parsers;
- the reflection validator, with `--decision-source` for the plan, the three handoffs, the 2026-10-17 grouping and `.agent/context/known-issues.yaml`, and `--decision-issue` for each of the four issue ids;
- `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent (recorded `gui-refs-not-shipped`). No element is added; the changed ones:

| Element | Kind | Change | Standard | E2E |
|---|---|---|---|---|
| `NavRail` items | nav button (changed) | `title` with the chord in both states; `aria-keyshortcuts` | 06 "Hints"; WAI-ARIA | AC-95.8 |
| `command-palette` list | dialog list (changed) | context-aware list; Appearance group | 06 §Command palette curation | AC-96.12, AC-96.13 |
| Downloader / Convert `confirm-modal` | modal (changed) | new `'cancel'` kind, cancel label "Keep running" | G20 (shared `ConfirmModal`) | AC-96.12 (clear); AC-96.7 (cancel, unit) |
| `header-console-btn`, `help-card` toggle | button (changed) | `title`, `aria-keyshortcuts` | 06 "Hints" | AC-97.6 |
| `url-input`, `channel-input` | input (changed) | `title`, `aria-keyshortcuts` | 06 "Hints" | AC-97.6 |
| `add-btn`, `generate-btn`, `convert-add`, `capture-region`, `convert-browse` | button (changed) | `title`, `aria-keyshortcuts` | 06 "Hints" | AC-97.7, AC-97.9 |
| `capture-save` | toolbar icon button (changed) | `ToolbarIconButton shortcut` → tooltip label and `aria-keyshortcuts` | 06 "Hints"; Tooltip (no `title`) | AC-97.8 |
| `theme-dark-btn`, `theme-light-btn` | button (changed) | `title`, `aria-keyshortcuts` | 06 "Hints" | AC-96.13 |

G36 (no silent test guards): the chord and palette tests assert; they never `skip`. G37: behaviour tests use `userEvent` (`userEvent.keyboard('{Control>}2{/Control}')`). G33–G35 surfaces are unchanged.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, a cwd other than `P:/av-kit`, a branch other than `main`, a dirty tree outside this plan folder, or a `PREREQS` status or symbol not as stated | Stop. Ask Mat, or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2), or the row 4/6 tree check refuses the tree | Fix the test setup only (or revert the early product edit), then re-prove Red. |
| S4 | A chord in `CHORD_TABLE` never reaches the renderer in Electron (the default menu or Chromium takes it first), or `MODAL_GUARD` cannot see the palette/confirm distinction | Stop for a Decision Brief with the measurement. Option B for a swallowed chord is another chord from triage D-89's spirit; the chord set is Mat's (D-89), so no silent swap. |
| S5 | `SCOPE_CHECK` finds a path outside `PRODUCT_SCOPE`, or `openapi.committed.json` changes | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake in `--repeat-each` | Fix the test's waiting, never add retries; if the product is racy, stop with a brief. |
| S7 | Review cap (plan 3, execution 6) or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |
| S8 | `HEAD` moves off `baseline.sha`, or a path another session owns (for example the Session 42 plan's Python files) appears in the tree during execution | Stop and ask Mat. Never commit, stash or revert another session's work. |

## Decision Log

Research engine for this plan: `native` (Claude Code reading of the renderer source and the Electron and WAI-ARIA documentation, 2026-10-26). Grouping §8 D-94, D-95, D-99 and D-103 carry forward unchanged into the reflection (stage `grouping`). "Triage D-78, D-79, D-87, D-88, D-89" are the 2026-10-17 triage decisions in `known-issues.yaml` that the spec and the known issues cite; D-87 to D-89 are Mat's. This plan's ids start at D-132 (User Review Required item 7).

```yaml
decision_log:
  - id: D-132
    stage: planning
    question: "When does execution start?"
    resolution: human
    class: two-way
    chosen: "On the Codex plan review's approved verdict, with no further pause; Mat's 2026-10-26 message is the execution message"
    source_tag: Human-approved
    precedents: ["plan_to_exec_gate: human (harness.local.md §Claude Code)", "USER_EXPLICIT 2026-10-26 'appon reviewer approval start executing it'"]
    research: { engine: none, sources: [] }
    reasoning: "The gate needs the user's explicit message, and Mat gave it in advance, tied to the reviewer's approval. A changes_required verdict still loops; only approved starts row 0. A second chat confirmation would add a pause Mat asked to skip."
  - id: D-133
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "P:/av-kit on main; alone, with S8 guarding HEAD and foreign paths"
    source_tag: Local Canon
    precedents: ["AGENTS.md 'No branches or worktrees' (bb481ec)", "the Session 42 plan also runs on main and shares the hub files"]
    research: { engine: none, sources: [] }
    reasoning: "AGENTS.md forbids branches and worktrees. Two sessions in one tree would mix the scope check and the identity hash, so this session stops if HEAD moves or another session's paths appear, instead of guessing which edits are whose. The open worktree P:/av-kit-wt/pill-palette-darker predates the rule and is not touched."
  - id: D-134
    stage: planning
    question: "How does one handler dispatch chords safely from any focus?"
    resolution: autonomous
    class: two-way
    chosen: "SHORTCUT_HANDLER: ignore repeat and IME composition; skip while a non-palette aria-modal is open; with the palette open, run and close it; prevent default only on a match"
    source_tag: Local Canon
    precedents: ["06 'Text fields' (Ctrl chords fire from any focus)", "AppShell.tsx:68 Ctrl+K already fires from any focus", "ConfirmModal sets aria-modal (ConfirmModal.tsx:127)"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/isComposing"] }
    reasoning: "A held key repeats keydown, so a navigation chord would fire many times. An IME composition uses the same keys for text. A confirm dialog is a pending decision, and a chord that navigates away would hide it without an answer, so chords wait. The palette is different: the user opened it to run a command, and a chord is a faster way to do that. Preventing only matched chords keeps every other key's default."
  - id: D-135
    stage: planning
    question: "What stays in AppShell's keydown listener?"
    resolution: autonomous
    class: two-way
    chosen: "Ctrl+K, palette Escape and console Escape stay; every other chord goes through the handler; Ctrl+4/5 branches removed"
    source_tag: Spec
    precedents: ["06 'Registry-driven' (Ctrl+K stays the palette opener; AppShell binds no chord outside the registry)", "download-queue e2e watchKeydownListeners counts document keydown listeners"]
    research: { engine: none, sources: [] }
    reasoning: "Escape is not a chord the registry owns: it closes whichever shell overlay is open. Keeping one window listener avoids a second listener that the existing listener-count test would see and keeps the order of Escape handling. Two hard-coded nav branches would duplicate the registry, which 06 forbids."
  - id: D-136
    stage: planning
    question: "Which chords must no registry entry take?"
    resolution: autonomous
    class: two-way
    chosen: "RESERVED_CHORDS: the Electron default menu's Windows accelerators, Capture's F2 and zoom keys, Ctrl+K and plain Enter"
    source_tag: Research-backed
    precedents: ["ui/src/main has no Menu.setApplicationMenu call, so Electron installs its default menu", "06 'No collisions' (Ctrl+=/-/0, F2)", "06 'Text fields' (Ctrl+A/C/V/X/Z, plain Enter)"]
    research: { engine: native, sources: ["https://www.electronjs.org/docs/latest/api/menu#default-menu", "https://www.electronjs.org/docs/latest/api/menu-item#roles"] }
    reasoning: "The default menu's accelerators run in the main process before the renderer sees the key, so a registry chord on them would be dead or would reload the app. Reserving them in the map makes a future collision a build-time error instead of a silent failure. Removing the default menu was rejected: it would drop DevTools, zoom and the edit roles, which is not this MEU's call."
  - id: D-137
    stage: planning
    question: "How does the palette decide which commands are listed?"
    resolution: autonomous
    class: two-way
    chosen: "AVAILABILITY + PALETTE_LIST: global commands (navigation, rail, console, help, Appearance, Check dependencies) always; a page's entry and stateful commands only on that page, listed first; stateful commands only when the page's control is enabled; fail closed with no published state"
    source_tag: Human-approved
    precedents: ["triage D-87 (Mat 2026-10-17): global always, current page first, cannot-run hidden, recompute on page or state", "listPaletteIds feeds AC-19.17 and the AC-23.18 audit"]
    research: { engine: none, sources: [] }
    reasoning: "D-87 lists the global commands (Settings among them) and rejects a palette that still shows other pages' commands, so page-owned commands are listed only on their page; plan review round 1 (F2) corrected an earlier draft that listed entry commands everywhere. Round 2 (F6) found four retained Electron scenarios (W1-6, W2-6, W8-6, W9-6) that select an entry command from another page; they are rewritten to prove the command absent off-page and select it on its page (TA-1, TA-2, TA-5, TA-6), not exempted. Stateful commands act on a page's live queue, and only the mounted page knows whether its control is enabled, so the page must say so. Hiding them when no state is published keeps the palette from offering an action that cannot run. listPaletteIds stays 'all entries' so the existing audits keep their meaning."
  - id: D-138
    stage: planning
    question: "How does the palette learn a page's control state?"
    resolution: autonomous
    class: two-way
    chosen: "COMMAND_STATE: a small external store per page; pages publish the same expressions their controls use (PAGE_STATE)"
    source_tag: Local Canon
    precedents: ["useDocumentTheme uses useSyncExternalStore (Session 40)", "the page toolbars compute canStart/canPauseResume/canClearAll from controlEnabled"]
    research: { engine: native, sources: ["https://react.dev/reference/react/useSyncExternalStore"] }
    reasoning: "Re-deriving queue state in the palette would duplicate each page's control rules and drift. Publishing the toolbar's own booleans makes the palette agree with the buttons by construction. A React context was rejected because pages render as AppShell children and the palette is a sibling; a store needs no provider and matches the theme hook."
  - id: D-139
    stage: planning
    question: "Pause and Resume: one entry or two?"
    resolution: autonomous
    class: two-way
    chosen: "Two registry entries; the palette lists at most one"
    source_tag: Human-approved
    precedents: ["triage D-87 'Pause/Resume one state-aware entry'", "AC-46.1a and AC-45.4a pin the pause and resume command names and events"]
    research: { engine: none, sources: [] }
    reasoning: "The user sees one entry, as D-87 asks. Merging the ids would break the pinned COMMANDS and EVENTS maps and the index rows for no visible gain."
  - id: D-140
    stage: planning
    question: "How do palette Clear and Cancel reach the page's confirm?"
    resolution: autonomous
    class: two-way
    chosen: "CONFIRM_ROUTE: navigate, then a confirm-request event the page answers with its own ConfirmModal; a new 'cancel' kind; no API call before Confirm"
    source_tag: Spec
    precedents: ["triage D-79 (Clear and Cancel open the same ConfirmModal the toolbar uses)", "DownloaderPage DownloadConfirm and confirmCopy (:131-165)", "AC-46.1a pins DOWNLOAD_EVENTS keys"]
    research: { engine: none, sources: [] }
    reasoning: "The page owns the modal and its copy, so the palette asks the page instead of drawing its own. A separate event keeps the pinned event maps unchanged. The toolbar has no Cancel confirm to reuse, so a cancel kind is added beside clear, with a cancel label that cannot be read as 'cancel the downloads'."
  - id: D-141
    stage: planning
    question: "Which path do the Appearance commands use?"
    resolution: human
    class: two-way
    chosen: "APPEARANCE: putSettingsNamespace extracted from flushPut; registry/appearance.ts calls it; the registry never imports apiFetch"
    source_tag: Human-approved
    precedents: ["triage D-88 (Mat 2026-10-17): same path as the Settings buttons", "AC-20.13/AC-21.13/AC-22.19/AC-33.13 forbid apiFetch in the registry source"]
    research: { engine: none, sources: [] }
    reasoning: "Extracting the existing put keeps one code path for parse, PUT, apply and invalidate, so the Settings page and the palette cannot drift. A small module between the registry and the settings hook keeps the registry free of network code, as four existing tests require."
  - id: D-142
    stage: planning
    question: "Which labels change, and what does palette Generate do without the page?"
    resolution: autonomous
    class: two-way
    chosen: "LABELS: five renames; palette Prepare and Generate only click the page's enabled button"
    source_tag: Spec
    precedents: ["triage D-87 examples ('Check SABR', 'Preview TTS cleanup', 'Focus download URL')", "06 'Labels' (Generate never posts a hard-coded voice)", "tts-commands.ts:287 af_heart fallback"]
    research: { engine: none, sources: [] }
    reasoning: "The page button carries the user's chosen voice, format and steps, so clicking it is the only way to generate what the user set up. With no enabled button there is nothing valid to post, and the command is hidden anyway by PAGE_STATE. 'Toggle sidebar' reads as a toggle, as 06 asks, and matches the rail's own Collapse/Expand sidebar labels."
  - id: D-143
    stage: planning
    question: "How does Check dependencies run from another page?"
    resolution: autonomous
    class: two-way
    chosen: "CHECK_DEPS_ROUTE: navigate to Settings, then dispatch after two animation frames"
    source_tag: Local Canon
    precedents: ["only SettingsPage listens for SETTINGS_EVENTS.checkDeps (:388)", "navigateAndDeliver double rAF (download-commands.ts:69-76)"]
    research: { engine: none, sources: [] }
    reasoning: "Today the event fires with no listener when Settings is not mounted, so the command silently does nothing off-route. The existing double-rAF pattern lets the page mount first."
  - id: D-144
    stage: planning
    question: "How are 06 and the actions index amended to the context-aware model?"
    resolution: autonomous
    class: two-way
    chosen: "INDEX_AMEND: 06 :313-315 and the index legend reworded; Appearance and page:primary rows; convert:browse becomes palette yes; the audit compares the eligible registry set with the Palette yes set"
    source_tag: Local Canon
    precedents: ["06 'Index' (amend the Palette column and the :315 rule; AC-23.20 stays bidirectional)", "AC-23.18 (every Palette yes id is registered)"]
    research: { engine: none, sources: [] }
    reasoning: "The Palette column keeps meaning 'eligible', and the curation rules decide when an eligible row is shown, so no row's column flips except the new Browse command. A set equality makes the audit bidirectional for the registry as well, so a new command cannot skip its index row."
  - id: D-145
    stage: planning
    question: "How does the clipboard rider land?"
    resolution: autonomous
    class: two-way
    chosen: "CLIPBOARD_RIDER: one resolver case, two Settings rows after settings:start_minimized, two audit test ids, one test-ids entry"
    source_tag: Local Canon
    precedents: ["known issue GUI-AUDIT-CLIPBOARD-RESOLVER", "console:copy already uses 'IPC writeClipboardText' but is not scanned", "preload.ts:55 writeClipboardText → write-clipboard-text"]
    research: { engine: none, sources: [] }
    reasoning: "The two Settings copy buttons exist (SettingsPage :149, :1054) with no index row, because the audit could not resolve the cell. The resolver case makes the existing AC-23.20 loop check them like every other IPC row."
  - id: D-146
    stage: planning
    question: "Which chords, and what is the page primary action?"
    resolution: human
    class: two-way
    chosen: "CHORD_TABLE and PAGE_PRIMARY: Mat's D-89 set; Ctrl+Enter clicks each page's primary button when enabled and is inert on Settings; Ctrl+O uses a new convert:browse command"
    source_tag: Human-approved
    precedents: ["triage D-89 (Mat 2026-10-17) core set", "DownloaderPage add-btn :546, TranscriptPage add-btn :462, TTSPage generate-btn :663, ConvertPage convert-add :593, CapturePage capture-region :1433"]
    research: { engine: none, sources: [] }
    reasoning: "The chords are Mat's. The primary action is the page's primary-variant button, so Ctrl+Enter does exactly what a click does, with the same enabled check. Settings saves per section, so it has no single primary action. Browse files needed a command so its chord goes through the registry like every other."
  - id: D-147
    stage: planning
    question: "How is a chord shown on its control?"
    resolution: autonomous
    class: two-way
    chosen: "HINTS: aria-keyshortcuts plus the chord in the title, or in the Tooltip label for ToolbarIconButton; BOUND_CONTROLS lists them"
    source_tag: Research-backed
    precedents: ["06 'Hints'", "header-palette-btn already has aria-keyshortcuts 'Control+K'", "ToolbarIconButton renders a Tooltip and no title"]
    research: { engine: native, sources: ["https://www.w3.org/TR/wai-aria-1.2/#aria-keyshortcuts"] }
    reasoning: "aria-keyshortcuts tells assistive technology the chord, and the title or tooltip shows it to a mouse user. A title on a Tooltip-wrapped button would show two hints, so that component gets a prop instead. One list of bound controls lets one test check them all."
  - id: D-148
    stage: planning
    question: "Where do the Electron tests go?"
    resolution: autonomous
    class: two-way
    chosen: "A new keyboard-shortcuts.test.ts for shell chords; page chords and palette flows in the spec that owns the page's seam"
    source_tag: Local Canon
    precedents: ["each page seam lives in its spec (download-queue, convert-queue, capture-inbox, settings)", "Session 40 D-115"]
    research: { engine: none, sources: [] }
    reasoning: "Shell chords need no seam, so a small new spec keeps them together. Page chords need the page's seam, and copying seams into a new spec would duplicate them."
  - id: D-149
    stage: planning
    question: "How do the Red tests fail cleanly when the new modules do not exist yet?"
    resolution: autonomous
    class: two-way
    chosen: "Namespace or dynamic imports with a typeof or existsSync assertion first; toBeVisible and expect.poll for every Electron effect"
    source_tag: Local Canon
    precedents: ["Session 40 D-113", "red-check.py fixture vitest-not-a-function-is-unattributed"]
    research: { engine: none, sources: [] }
    reasoning: "A static import of a missing module fails the whole file at load and hides every other test, so new modules are loaded after an existence assertion. A missing export becomes an attributed assertion through typeof. A chord that does nothing must fail by expect, not by a click timeout, which the checker refuses."
  - id: D-150
    stage: planning
    question: "Does the grouping's split candidate (MEU-97 as Session 41b) apply?"
    resolution: autonomous
    class: two-way
    chosen: "No split; row 6 (MEU-97 Red) starts after a compact (compact_continue)"
    source_tag: Local Canon
    precedents: ["grouping :99 split flag 'if the MEU-96 handoff passes ~50% context, run MEU-97 as 41b'", "Session 40 used compact_continue between MEUs"]
    research: { engine: none, sources: [] }
    reasoning: "The flag guards context size, and compact_continue resets context at the same point a split would, with the work and receipts on disk. A split would add a second plan, a second review and a second gate for the same tree. Mat can still ask for a split."
  - id: D-151
    stage: planning
    question: "What does Ctrl+Enter do while the palette is open?"
    resolution: autonomous
    class: two-way
    chosen: "PALETTE_ENTER: the palette acts only on unmodified Enter; Ctrl+Enter falls through to the window listener and runs page:primary once"
    source_tag: Local Canon
    precedents: ["CommandPalette.tsx:134 treats every Enter as selection and does not stop propagation", "plan review round 1 F3"]
    research: { engine: none, sources: [] }
    reasoning: "React's handler runs before the window listener, so without the modifier check one Ctrl+Enter would run the highlighted command and the page action. Routing every modified Enter to the registry keeps one chord, one action."
  - id: D-152
    stage: planning
    question: "How do Ctrl+S and palette Save reconcile the capture state the way the button does?"
    resolution: autonomous
    class: two-way
    chosen: "CAPTURE_SAVE_ROUTE: CAPTURE_COMMANDS.save clicks the enabled capture-save button, so saveOverlay runs"
    source_tag: Local Canon
    precedents: ["LABELS: TTS palette commands click their enabled page buttons", "PAGE_PRIMARY clicks the enabled primary button", "plan review round 1 F4"]
    research: { engine: none, sources: [] }
    reasoning: "saveOverlay is the only path that updates saved and baked state after a POST; calling saveAnnotations directly left the shot dirty and Save eligible. Clicking the page control reuses that path and inherits its disabled rule, the same pattern the plan uses for TTS and the page primary action."
```

## Research References

- Electron default application menu and menu-item roles (the Windows accelerators the default menu installs): https://www.electronjs.org/docs/latest/api/menu#default-menu, https://www.electronjs.org/docs/latest/api/menu-item#roles (R-a)
- WAI-ARIA 1.2 `aria-keyshortcuts` (value syntax: modifier names `Control`, `Shift`, `Alt`, `Meta`, joined by `+`): https://www.w3.org/TR/wai-aria-1.2/#aria-keyshortcuts (R-b)
- MDN `KeyboardEvent.isComposing` and `repeat`: https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/isComposing
- React `useSyncExternalStore`: https://react.dev/reference/react/useSyncExternalStore

The plan relies on three facts. The default menu's accelerators are handled in the main process, so the renderer never sees those chords. `aria-keyshortcuts` names `Control`, not `Ctrl`. A component that reads through `useSyncExternalStore` re-renders when the snapshot changes.

## Planning receipts

- **R-1 (2026-10-26).** `identity.py --selftest` (`C:/Temp/av-kit/s41-plan-R-identity.txt`): exit 0, `identity selftest: 0 failure(s)`.
- **R-2 (2026-10-26).** `red-check.py --selftest`, 36 fixtures (`C:/Temp/av-kit/s41-plan-R-redcheck.txt`): `36 fixture(s) (11 positive, 25 negative), 0 wrong`.
- **R-3 (2026-10-26).** `session-gate.ps1` parse (`C:/Temp/av-kit/s41-plan-R-gate-parse.txt`): `parse errors: 0`. The gate itself was not run during planning, because it needs the execution baseline.
- **R-4 (2026-10-26).** The `scope-paths` probe in a scratch repository, using the gate's own Python (`C:/Temp/av-kit/s41-plan-R-scope-probe.txt`): exit 0, 5 of 5 cases pass (clean tree; an uncommitted rename out of a disallowed path; a new allowed untracked file; an untracked disallowed path with a space and a non-ASCII name; a committed HEAD move, S8).
- **R-5 (2026-10-26).** `lint_task_contract.py` over `task.md` with `RECEIPTS_DIR=C:/Temp/av-kit` (`C:/Temp/av-kit/s41-plan-R-task-lint.txt`): exit 0, 26 rows, 24 fully checked, 2 `view_file` rows exempt (H1-5, H2-1).
- **R-a / R-b (2026-10-26, native).**
  - **R-a:** the Electron menu references above, together with `rg -n "setApplicationMenu" ui/src/main` (no hit), so the default menu is installed.
  - **R-b:** the WAI-ARIA `aria-keyshortcuts` definition, together with `Header.tsx:73` (`aria-keyshortcuts="Control+K"`), the one existing use.

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last input edit, from `P:/av-kit`, `pwsh`. Row 8 runs it after the product edits. Row 9 then changes bound inputs (`meu-status.yaml`, the rendered `BUILD_PLAN.md`, the 06 Delivered notes), so H1-2's run is the fresh full record the handoffs carry. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's check (User Review Required item 8).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state`, which is HEAD plus one SHA-256. The hash covers:
  - **The work tree:** the tracked diff and the untracked (not ignored) files of the whole work tree. It excludes only this session's own closeout outputs, which no suite or gate step reads: this plan folder's `*.md`, this session's handoffs and reflection, `docs/execution/metrics.md`, `.agent/context/current-focus.md` and `known-issues.yaml`/`.md`.
    - So the lockfiles, `openapi.committed.json`, the configs and this plan's scripts are bound.
    - So are the documents the suites read: `docs/build-plan/` (`gui-actions-audit`, `capture-page`, `convert-page`, `queue-canon`, `layout-canon`), `docs/BUILD_PLAN.md`, `meu-status.yaml` and the grouping files (`layout-canon`, `queue-canon`), and `meu-registry.md` (`state-render`).
    - Row 9 therefore runs before H1-2. The post-approval status write in H2-2 re-runs `layout-canon` and `queue-canon`.
  - **The runtime identity, observed live:**
    - the Python running it and the SHA-256 of its installed distribution set;
    - `node --version`;
    - the installed `electron` and `@playwright/test` versions;
    - the `segoeui.ttf` hash;
    - `ELECTRON_RUN_AS_NODE`.

  `--state-only` computes the same value. The gate records the state before and after it runs (§4), and each handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoffs.

## Execution Correction Notes

These are recorded during execution so that no plan-level contract changes silently. The execution review sees each item.

| Item | Change | Evidence |
|---|---|---|
| EC-1 (row 0) | Row 0's S1 tree check also admits `.agent/context/handoffs/2026-10-26-gui-keyboard-palette-*`, the prefix `session-gate.ps1` already allows (`:78`). | The first row 0 run stopped at S1 on this plan's own untracked review file `2026-10-26-gui-keyboard-palette-plan-critical-review.md`. Mat ruled, verbatim: `Treat it as ours, continue (Recommended)` (`walkthrough.md` §Execution Correction Notes). |
| EC-2 (row 0) | `session-gate.ps1` `$expectedBaselinePyFailed` gains the four `tests/tooling/test_framework_adoption.py` baseline ids, the two census ids in the gate's `^FAILED (\S+)` captured form. Each is excused only if `s41-base-py.txt` shows it `FAILED`. | Each fails on HEAD `bb481ec` with `REFUSE: rule map identity mismatch: AGENTS.md` after that commit's `AGENTS.md` edit, outside `PRODUCT_SCOPE`; a test failing at baseline is never a regression (§Verification Plan). `walkthrough.md` §Baseline. |
