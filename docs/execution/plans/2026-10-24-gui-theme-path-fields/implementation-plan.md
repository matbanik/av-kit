---
project: "2026-10-24-gui-theme-path-fields"
date: "2026-10-24"
source: "docs/build-plan/06-gui.md#theme-reactive-selects-residual"
meus: ["MEU-94", "MEU-93"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: GUI theme-reactive selects and one path-field primitive (Session 40)

> **Project:** `2026-10-24-gui-theme-path-fields`
> **Build plan:**
> - `docs/build-plan/06-gui.md` §Theme-reactive selects (residual) (`:1416-1428`, MEU-94; matrix row 6.9)
> - `docs/build-plan/06-gui.md` §Path fields (residual) (`:1402-1414`, MEU-93; matrix row 6.8). Its neighbours §DirectoryPicker and §Settings Key Convention are Local Canon
> - `.agent/docs/emerging-standards.md` G30 (`:1041-1077`) and G32 (`:1102`) are Local Canon; row 1 updates them to the new hook (D-109)
>
> **Grouping:** `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md`, Session 40 (`:76-86`), decisions D-94, D-95 (`:160-161`) and D-103 (`:169`); scoping review approved in round 2 (§9, ledger loop `s40-42-grouping-scoping-2026-10-24`).
> **Known issues:** `GUI-LIGHT-THEME-SELECT-STALE-DARK` (`known-issues.yaml:2797`, triage D-77), `GUI-CONVERT-OUTPUT-NO-BROWSE` (`:2740`, triage D-76).
> **Status:** `draft`. Under `plan_to_exec_gate: human`, execution starts only on the user's explicit chat message after plan-review approval.
>
> Line anchors are from `main` `7b29fcd` (the 2026-10-24 squashed root commit) plus the uncommitted grouping, status and `06-gui.md` edits that the scoping review approved. Those edits are in the working tree and inside this plan's scope allow-list.

## Goal

In Light, the selects on Settings, TTS and Convert keep their dark colours. `getG30Styles()` (`SelectInput.tsx:19-23`) reads `html.dark` once at render. `THEME_CHANGED_EVENT` re-renders only `AppShell`, and route pages arrive as `children`, so they never re-read it. `index.html` boots with `class="dark"`, and `useSyncDocumentTheme` (`lib/theme.ts:52-80`) applies the persisted `ui.theme` only after a single `GET /settings/ui` that is never retried. So a cold boot in Light paints dark selects, and they stay dark. The native option menus always use the light pair (`NATIVE_OPTION_MENU_STYLE`, `:17`). Measured 2026-10-17: all 8 Settings selects stay `rgb(26, 26, 46)` after switching to Light (triage D-77). Separately, the Convert **Output folder** is a bare `<input>` with no folder picker (`ConvertPage.tsx:751-758`). Settings edits the same leaf through `PathRow`, and TTS hand-rolls a third variant (`TTSPage.tsx:641-665`; triage D-76).

1. **MEU-94 — `gui-theme-reactive-selects`.**
   - One subscription to the document theme (`THEME_HOOK`) backs every G30 consumer: a pure style pair plus a hook (`G30_STYLES`).
   - The select and its options use the same pair, so the option menu follows the theme.
   - `ConsolePanel`'s copy is removed.
   - The last GUI-applied theme is applied before the first render (`BOOT_THEME`), so the shell paints in it.
   - The route area waits for the stored theme before it renders (`THEME_GATE`), so no route select paints in a missing or stale mirror's theme.
   - The boot `GET /settings/ui` retries while the backend is starting (`BOOT_RETRY`).
2. **MEU-93 — `gui-path-fields`.**
   - Convert's Output folder, the TTS output path and the Settings capture-backup folder all render `PathRow` (`PATH_ROWS`).
   - `PathRow` gains two additive props (`PATH_ROW_PROPS`).
   - The new Browse gets its actions-index row and audit (`CONVERT_BROWSE_INDEX`).

Order (grouping `:83`, D-95): MEU-94 first, because it is visible on every page and MEU-96 later builds on its theme path; then MEU-93. Both MEUs touch `SettingsPage.tsx` and `TTSPage.tsx`, so they run in this order in one tree. Row 0 records the baseline in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-10-24); no headroom MCP or binary. Scope is the renderer theme path (lib/theme.ts, main.tsx, components/ui SelectInput.tsx and PathRow.tsx, layout/ConsolePanel.tsx) and its consumers (features settings, tts, converter, capture), read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. A reviewer `approved` does not start execution; the user's explicit chat message does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target, so the gates are authoritative where they run. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 argv (`.agent/docs/commands.md:190-210`, including the MCP ids `mcp-types`, `mcp-tests` and `mcp-build`) plus targeted file lists.
- **Working directory:** `P:/av-kit` on `main` (D-104). This is D6's default cwd. No other session branch is open: Session 31b merged and the history was squashed on 2026-10-24. Row 0 still runs `uv sync --frozen --all-packages`, `npm --prefix ui ci` and `npm --prefix mcp-server ci`.
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`). Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, Mat is the fallback (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-94` | `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-94-handoff.md` |
| `MEU-93` | `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-MEU-93-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1) (rows 6 and H1-2)
- [identity.py](identity.py) (input identity, H1-6b)
- [red-check.py](red-check.py) (Red proof, rows 2 and 4)

Rolling reviews:

- `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-24-gui-theme-path-fields-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census, the canon updates (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha`; 06/G30/G32 edits |
| WP-1 | MEU-94 TDD: `THEME_HOOK`, `G30_STYLES`, `BOOT_THEME`, `BOOT_RETRY`, `THEME_PROBE` (rows 2–3) | WP-0 | `shared` | tests + source; Red/Green receipts; `walkthrough.md` §MEU-94 |
| WP-2 | MEU-93 TDD: `PATH_ROW_PROPS`, `PATH_ROWS`, `CONVERT_BROWSE_INDEX` (rows 4–5) | WP-1 | `compact_continue` | tests + source; `walkthrough.md` §MEU-93; compact, then re-read `task.md` and the walkthrough |
| WP-3 | Session gate and hub reconciliation (rows 6–7) | WP-2 | `shared` | gate receipts in `walkthrough.md` §Gate; `meu-status.yaml`, rendered `BUILD_PLAN.md` |
| WP-4 | H1 closeout, execution review, H2 | WP-3 | `compact_continue` | two handoffs, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for the user's execution message. They are not a pause point.
>
> 1. **Route content waits for the stored theme (`THEME_GATE`, D-117); the shell paints from a local mirror (`BOOT_THEME`, D-107).**
>    - `applyDocumentTheme` mirrors each theme it applies into renderer `localStorage`, and the boot module applies that mirror before the first render. So the header, nav rail and console paint in the last GUI theme.
>    - The route area (`AppShell`'s `<main>`) shows a `route-theme-pending` placeholder until the boot `GET /settings/ui` settles. It reads "Connecting...", then "Still loading…" after 3 s, as 06 §Progressive Loading Strategy specifies per panel.
>    - So a profile with Light stored and no mirror never paints a route select dark. That is every existing install on its first launch after this change. The same holds for a stale mirror, for example `ui.theme` changed through MCP `avkit_settings` while the app was closed.
>    - The wait lasts while the backend is not yet published (`BACKEND_NOT_READY`). The pages cannot load data during that time anyway.
>    - The route renders at once, with the mirror or dark, in three cases: the backend is published but unreachable (`FETCH_FAILED`), it answers any other error, or the retry window ends. A later successful retry still corrects the theme live.
>    - A first launch with no stored theme boots dark, as today.
> 2. **The boot theme request retries while the backend starts (`BOOT_RETRY`, D-108).** Only an `ApiError` with status 503 is retried: `BACKEND_NOT_READY` (`lib/api.ts:25-58`) and `FETCH_FAILED` (`:75`). Retries stop once the next attempt would start 60 s or more after the first. Any other error is logged once, as today. A backend that never comes up gives one log line when the window ends, not one per attempt. If the backend is never published, each attempt waits up to `BACKEND_READY_TIMEOUT_MS` (10 s) inside `apiFetch`, so the route placeholder can show for about 70 s before the route renders dark.
> 3. **`getG30Styles` and `NATIVE_OPTION_MENU_STYLE` are removed (`G30_STYLES`, D-106).** G30 and G32 in `emerging-standards.md` change to name `useG30Styles()` (row 1, D-109). The option menu follows the theme: Light gives the light pair and Dark the dark pair. Before, it always used the light pair. This is triage D-77 ("Option menu").
> 4. **The TTS output path gains a visible "Output path" label, and its Browse becomes the `PathRow` secondary button (`PATH_ROWS`, D-111).** The ids `output-path` and `browse-output-btn` and the busy-disabled Browse are kept. The run bar keeps the field, so AC-56.4's run-bar containment and AC-64.6 still apply. If either breaks, that is S4.
> 5. **`TEST_AMENDMENTS` TA-1 to TA-2.** Each changes an existing test that pins the removed `getG30Styles` name. They are listed in advance. Any other contradiction the census finds stops execution (S2).
> 6. **Optional visual check.** At the commit gate, Mat may open Settings, TTS and Convert in the dev app in Light and Dark, and restart once in Light. This is non-blocking; the Electron colour tests are the gate.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `PREREQS` | Before any edit: no `graphify-out*/`; in `meu-status.yaml`, MEU-19, MEU-22, MEU-23, MEU-33, MEU-58 and MEU-92 are `approved`, and MEU-93 and MEU-94 are `pending`; `lib/theme.ts` defines `useSyncDocumentTheme` and `SelectInput.tsx` defines `getG30Styles` (the functions this plan replaces). | grouping `:76-86`, D-95; `meu-status.yaml:2434`, `:2459` |
| `G30_PAIRS` | The two style pairs stay the existing `G30_DARK` / `G30_LIGHT` constants (`SelectInput.tsx:14-15`). Their computed oracles in Chromium: Dark `backgroundColor rgb(26, 26, 46)`, `color rgb(224, 224, 224)`; Light `rgb(255, 255, 255)`, `rgb(30, 41, 59)`. | G30 (`emerging-standards.md:1041-1077`) |
| `THEME_HOOK` | `useDocumentTheme(): UiTheme` in `lib/theme.ts`, built on React `useSyncExternalStore`. `subscribe` adds and removes a `THEME_CHANGED_EVENT` listener on `window`. `getSnapshot` returns `'dark'` iff `document.documentElement.classList.contains('dark')`, else `'light'`. `getServerSnapshot` returns `'dark'`. `lib/theme.ts` is the only renderer file that reads the root `dark` class. | 06 §Theme-reactive selects "Reactive styles"; R-a; D-105 |
| `G30_STYLES` | `SelectInput.tsx` exports `g30StylesFor(theme: UiTheme)`, which returns the `G30_PAIRS` member for that theme, and `useG30Styles()`, which is `g30StylesFor(useDocumentTheme())`. `getG30Styles` and `NATIVE_OPTION_MENU_STYLE` are removed. **Consumers:** `SelectInput` styles the select and every `<option>` with `useG30Styles()`, keeping the merge `{...callerStyle, ...g30}` (`:42-43`) so a caller cannot override the pair. The Settings `GridSelect` select and its options (`SettingsPage.tsx:228-239`), the Settings `audio_format` select and its options (`:612-623`), the CaptureViewport named-menu select and its "Named" option (`CaptureViewport.tsx:519`, `:964`) and `ConsolePanel`'s `console-search` input (`ConsolePanel.tsx:176`) all use `useG30Styles()`. `ConsolePanel.tsx` loses its own `G30_DARK`/`G30_LIGHT`/`getG30Styles` (`:9-15`). The redundant `style={getG30Styles()}` props on TTS `model-select`, `device-select` and `format-select` (`TTSPage.tsx:466`, `:476`, `:625`) and on the VoiceCombobox language `SelectInput` (`VoiceCombobox.tsx:252`) are deleted. `SelectInput` already applies the pair. | 06 "Reactive styles", "One copy", "Option menu"; triage D-77; D-106 |
| `BOOT_THEME` | `lib/theme.ts` exports `THEME_STORAGE_KEY = 'av-kit.ui.theme'` and `readBootTheme(): UiTheme \| null`. `readBootTheme` returns `'light'` or `'dark'` when `localStorage.getItem(THEME_STORAGE_KEY)` holds exactly that value, and `null` for anything else or when the read throws. `applyDocumentTheme(theme)` also calls `localStorage.setItem(THEME_STORAGE_KEY, theme)` inside `try`/`catch`; a throwing storage never stops the class toggle or the event. A new module, `src/renderer/src/boot-theme.ts`, runs `const t = readBootTheme(); if (t !== null) applyDocumentTheme(t)` at module evaluation. It is the **first** import of `main.tsx` (`import './boot-theme'`), so it runs before the router, the query client and `createRoot`. `index.html` is unchanged: the production CSP (`RENDERER_CSP`, `ui/src/main/index.ts:66-67`, set through `onHeadersReceived` at `:494-496`) is `script-src 'self'`, which forbids an inline script (R-b). The mirror sets the shell's first paint, and the theme used when `THEME_GATE` opens without an answer. It never decides the route's first paint when the backend answers. | 06 "First paint"; 06 §Progressive Loading Strategy (`06-gui.md:140-146`); R-b; D-107 |
| `BOOT_RETRY` | `useSyncDocumentTheme(): boolean` keeps its single-subscriber role (`AppShell`) and returns `settled` for `THEME_GATE`. **Retry:** on an `ApiError` with `status === 503` it retries `GET /settings/ui` after `BOOT_RETRY_DELAYS_MS = [250, 500, 1000]`, then every 2000 ms. It retries only while the next attempt would start less than `BOOT_RETRY_WINDOW_MS = 60_000` after the first attempt started; with attempts that reject at once, that is 33 attempts. The first success applies `resolveUiTheme(data.theme)` (as today). Unmounting cancels the pending timer and ignores a late answer. Any other error, or a 503 after which no attempt fits the window, calls `logRenderer('ERROR', 'Failed to load ui.theme: <message>')` exactly once and stops. **`settled`** starts `false`. It becomes `true`, and stays `true`, at the first of: a success (`applyDocumentTheme` runs before `settled` is set, so no render sees `settled` without the theme); an error whose `code` is not `'BACKEND_NOT_READY'`, `FETCH_FAILED` included (retries go on in the background); or the final failure. | `lib/api.ts` (503 `BACKEND_NOT_READY` / `FETCH_FAILED`); `ipc.ts:322-323` (`get-backend-url` waits for the published backend); triage D-77; D-108 |
| `THEME_GATE` | `AppShell` renders `{settled ? children : <RouteThemePending />}` inside its `<main>` (`AppShell.tsx:273-277`), with `settled` from `useSyncDocumentTheme()`. The header, nav rail, console and palette are never gated. `AppShell.tsx` exports `RouteThemePending`: `<div data-testid="route-theme-pending" role="status" className="p-4 text-sm text-fg-muted">`. Its text is `Connecting...` and becomes `Still loading…` 3000 ms after mount; unmounting clears the timer. It uses token classes only. **E2E effect:** `ui/src/main/index.ts:460-464` publishes an unreachable E2E backend (port 9) at once, so a load without a seam gets `FETCH_FAILED` and opens the gate on its first attempt. A spec seam opens it with its own answer: Settings `{theme: 'dark'}` (`settings.test.ts:82-83`), TTS 599 (`tts-generate.test.ts:243`), Convert the unreachable fall-through (`convert-queue.test.ts:461`). With `AVKIT_E2E_BACKEND_DELAY_MS` (`startup-reveal.test.ts`, 600 ms; `capture-inbox.test.ts` W9-7, 800 ms), the gate waits that long; both specs wait only for `app-shell`. | 06 "First paint"; 06 §Progressive Loading Strategy (`06-gui.md:140-146`: shell first, per-panel "Still loading…", never full-screen); review round 1 F1; D-117 |
| `THEME_PROBE` | A test helper, `ui/tests/e2e/theme-probe.ts` (not a test file). **Registration, no navigation:** `addThemeProbe(page, mode)` only adds an init script; it never reloads. The three seam installers (`installSettingsSeam`, `installTtsSeam`, Convert `installSeam`) gain an optional `themeProbe?: ThemeProbeMode`. They call `addThemeProbe` before their own `addInitScript`, then do their one existing `page.reload()`. With `theme.hold` they then wait for `app-shell` (Convert waits for `downloader-page` today, `convert-queue.test.ts:466`, which the gate holds back). So between registration and the probed load, a launch makes theme requests only on its first, un-seamed load. Those get `FETCH_FAILED` and write nothing, because `BOOT_RETRY` applies only a success. **Order-independent:** the probe defines `window.__avkitThemeProbe`. Each seam's `window.fetch` looks it up at request time, before its own routing: `const probed = window.__avkitThemeProbe?.handle(url, method, init); if (probed) return probed`. So the order in which Playwright runs the two init scripts, which is unspecified, does not matter. **Mode** `{ mirror?: UiTheme \| null, theme: { hold: true } \| { answer: UiTheme } }`. At document start the probe writes `mirror` to `localStorage[THEME_STORAGE_KEY]`; `null` removes the key and an absent `mirror` leaves it alone. `hold` keeps every `GET …/settings/ui` pending in a list. `releaseTheme(page, theme)` answers all held requests `200 {theme}` and every later one at once. `answer` answers at once. A `PUT …/settings/ui` whose body carries `theme` updates the answer and still passes to the seam. Every other request passes to the seam unchanged. `themeProbeCounts(page)` returns `{ held, released }`. **Observation:** a `MutationObserver` installed at document start records, for each `select` added to the DOM, its `data-testid` (or index), `whileHeld` (a held request was unanswered at insertion) and its computed `backgroundColor`/`color`. `visibleSelectColors(page)` returns the computed pair for every visible `select` and for its selected `option`. `launchWithAppData(dir)` launches Electron with a caller-owned `AVKIT_APP_DATA`, so two launches share `localStorage` (`ui/src/main/index.ts:220-222` sets `userData` from it). | Local Canon (spec seams, `settings.test.ts:11-20`, `:82`, `:110-112`); Playwright `addInitScript` (order unspecified); review round 1 F2; D-114 |
| `THEME_COLOURS` | For a page and a theme: every visible `select` and its selected `option` compute that theme's `G30_PAIRS` oracle, and at least the page floor of selects is visible: Settings 8 (the 2026-10-17 measurement; the source has 11 select sites), TTS 3 (`model-select`, `device-select`, `format-select`), Convert 3 (the three `SelectInput`s, `ConvertPage.tsx:660-675`, after opening `convert-advanced`). Checked with `expect.poll` (default timeout), never a fixed sleep. | 06 §Theme-reactive selects "Tests"; G30 checklist item 6 |
| `PATH_ROW_PROPS` | `PathRow` gains two optional, additive props: `placeholder?: string`, passed to the input, and `browseDisabled?: boolean`, passed to the Browse `Button` as `disabled`. Without them the rendered markup is unchanged: no `placeholder` attribute and no `disabled` attribute. The component stays token-only (AC-51.5). | 06 §Path fields "One primitive"; D-111, D-112 |
| `PATH_ROWS` | **Convert:** the Output folder `<label>` (`ConvertPage.tsx:751-758`) becomes `<PathRow id="convert-output-dir" label="Output folder" inputTestId="convert-output-dir" browseTestId="convert-output-dir-browse" value={converter.form.output_dir} onChange={(v) => converter.patchForm({ output_dir: v })} onBrowse={…} className="min-w-[24rem] flex-1" />`. `onBrowse` awaits `window.api.showDirectoryDialog()`, does nothing on `undefined`, and otherwise calls `converter.patchForm({ output_dir: chosen })`. Saving stays on `convert-page-save` (AC-33.17). **TTS:** the run-bar `output-path` input and `browse-output-btn` (`TTSPage.tsx:641-665`) become `<PathRow id="tts-output-path" label="Output path" inputTestId="output-path" browseTestId="browse-output-btn" value={outputPath} onChange={() => {}} readOnly browseDisabled={busy} onBrowse={…} className="min-w-[20rem] flex-1" />`. `onBrowse` keeps today's body: `run(async () => { chosen = await browseOutputDir(); undefined → return; touched; setOutputPath; putSettings({ output_path }) })`. The field stays inside `[data-run-bar]`. **Settings:** the capture-backup `FormRow` (`SettingsPage.tsx:995-1025`) becomes `<PathRow id="settings-capture-backup" label="Backup folder" inputTestId="settings-leaf-capture-backup_dir" browseTestId="settings-capture-backup-browse" placeholder={`${capture.form.inbox_dir}/${BACKUP_DIR_DEFAULT_NAME}`} …/>` with the same Browse body. Every id stays a string literal in the page source (AC-67.24, AC-67.26). | 06 §Path fields "Convert output", "TTS output"; triage D-76; D-110–D-112 |
| `CONVERT_BROWSE_INDEX` | `docs/build-plan/gui-actions-index.md` gains, directly after the `convert:gpu_refresh` row (`:68`), exactly `` | `convert:browse_output_dir` | Output folder Browse | no | IPC `showDirectoryDialog` + `converter.output_dir` | specified | 08 / 06 | ``. `ui/tests/e2e/test-ids.ts` gains, after the MEU-71 block, `// MEU-93 Path fields (additive IDs).` and `export const CONVERT_OUTPUT_DIR_BROWSE = 'convert-output-dir-browse'`. `CONVERT_AUDIT_TESTIDS` (`gui-actions-audit.test.ts:49-58`) gains `{ testid: 'convert-output-dir-browse', indexId: 'convert:browse_output_dir' }`. | 06 §Path fields "Tests"; AC-71.14 pattern (`gui-actions-audit.test.ts:303-345`); D-110 |
| `TEST_AMENDMENTS` | **TA-1** `ui/tests/unit/chrome-zorivest.test.ts:304`: `toContain('getG30Styles')` becomes `toContain('useG30Styles')`, and the same test adds `not.toMatch(/G30_DARK\s*=/)` on the ConsolePanel source. **TA-2** `ui/tests/unit/tts-page.test.ts:271`: `toMatch(/getG30Styles/)` becomes `not.toMatch(/getG30Styles/)`; the `/SelectInput/` assertion stays. An amendment changes only those lines; every other line in those tests stays. | Local Canon |
| `CENSUS_PATTERNS` | Row 1 greps `ui/tests`, `tests` and `mcp-server/tests` for `getG30Styles`, `NATIVE_OPTION_MENU_STYLE`, `G30_DARK`, `G30_LIGHT`, `useSyncDocumentTheme`, `applyDocumentTheme`, `THEME_CHANGED_EVENT`, `settings/ui`, `localStorage`, `classList.contains('dark')`, `rgb(26, 26, 46)`, `#1a1a2e`, `convert-output-dir`, `output-path`, `browse-output-btn`, `settings-capture-backup`, `PathRow`, `FormRow`, `convert:gpu_refresh`, `CONVERT_AUDIT_TESTIDS`, `MCP_ADVANCED_SUMMARY`, `boot-theme`, `AppShell`, `route-theme-pending`, `RouteThemePending`, `__avkitThemeProbe` and `AVKIT_E2E_BACKEND_DELAY_MS`. A unit test that renders `AppShell` with route content is `unaffected` only when its `fetch` stub answers `/settings/ui` (so the gate opens) and it reads the content asynchronously; otherwise it is a `new-contradiction`. Each hit gets a disposition: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. | Local Canon (Session 35/36 census) |
| `PRODUCT_SCOPE` | The files this plan may change are exactly the Files Modified rows below; `session-gate.ps1` `scope-paths` holds the same allow-list. | grouping `:78-81` |

### MEU-94 — `gui-theme-reactive-selects`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| REST `GET /settings/ui` (read by the boot hook) | existing `ui` namespace (unchanged) | `theme` resolved by `resolveUiTheme` (`'light'` → light, anything else → dark) | extra fields ignored (existing) |
| REST `PUT /settings/ui` (theme buttons, `useSettingsPage.ts:75-78`) | unchanged | unchanged | unchanged |
| Renderer `localStorage[THEME_STORAGE_KEY]` | `BOOT_THEME` | exactly `'light'` or `'dark'`; any other value reads as `null` | not applicable |
| `THEME_CHANGED_EVENT` `CustomEvent` | `lib/theme.ts` (unchanged) | `detail.theme` in `UI_THEMES` | n/a |
| OpenAPI, IPC, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-94.1 | unit | `THEME_HOOK` (`theme-selects.test.tsx`, jsdom, `renderHook`): with `html.dark` set, `useDocumentTheme()` is `'dark'`; `act(() => applyDocumentTheme('light'))` makes the same mounted hook `'light'` without a remount, and `'dark'` again after `applyDocumentTheme('dark')`. Unmounting removes its `THEME_CHANGED_EVENT` listener (`removeEventListener` spy). | 06 "Reactive styles"; `THEME_HOOK` | A component that only uses the hook re-renders on the event (render count rises by one per switch) |
| AC-94.2 | unit | `G30_STYLES`: `g30StylesFor('dark')` and `g30StylesFor('light')` equal the two `G30_PAIRS` constants. A mounted `SelectInput` with three options and a caller `style={{ backgroundColor: 'red', width: 50 }}`: after each `applyDocumentTheme` switch, without a remount, the select and **every** option carry the current theme's pair, and the select keeps `width: 50px`. Inline colours are compared through jsdom's `CSSStyleDeclaration` (a probe element given the hex reads back the same normalised string). | 06 "Reactive styles", "Option menu" | In Dark, no option carries the light pair (the baseline `NATIVE_OPTION_MENU_STYLE` did) |
| AC-94.3 | unit | One copy, no DOM read (source): no file under `ui/src/renderer/src` contains `getG30Styles` or `NATIVE_OPTION_MENU_STYLE`; `classList.contains('dark')` appears only in `lib/theme.ts`; `ConsolePanel.tsx` and `CaptureViewport.tsx` contain `useG30Styles`; `SettingsPage.tsx` contains `useG30Styles` and its two raw `<select>` sites style their options with it; `TTSPage.tsx` and `VoiceCombobox.tsx` pass no `style=` prop to `SelectInput`. TA-1 and TA-2 apply. | 06 "One copy"; `G30_STYLES` | The baseline tree fails on the `ConsolePanel` copy and on the fixed option pair |
| AC-94.4 | unit | Settings rendered (jsdom, the `settings-emphasis.test.tsx` harness): after `applyDocumentTheme('light')`, every `select` on the page and each of its options carry the light pair, without a remount; after `'dark'`, the dark pair. The page renders at least 8 selects. | 06 "Tests"; known issue (8 Settings selects) | The baseline page keeps the dark pair after the switch |
| AC-94.5 | unit | `BOOT_THEME`: `applyDocumentTheme('light')` stores `'light'` under `THEME_STORAGE_KEY`; `readBootTheme()` returns `'light'`, `'dark'`, and `null` for an unset key and for `'blue'`. With `Storage.prototype.getItem` and `setItem` stubbed to throw, `readBootTheme()` is `null` and `applyDocumentTheme('light')` still removes `dark` and dispatches the event. Source text, never imported: `src/renderer/src/boot-theme.ts` exists and contains `readBootTheme()` and `applyDocumentTheme(`; the first `import` statement of `main.tsx` is `import './boot-theme'`. | 06 "First paint"; `BOOT_THEME` | `index.html` gains no inline `<script>` (CSP `script-src 'self'`) |
| AC-94.6 | unit | `BOOT_RETRY` (fake timers, `renderHook(useSyncDocumentTheme)`, `vi.mock` of `lib/api` keeping the real `ApiError` through `importOriginal`, and of `lib/renderer-log`): (a) two `ApiError(503, 'BACKEND_NOT_READY')` and then `{theme: 'light'}`: `result.current` stays `false` until the third call answers; light is applied after 250 + 500 ms with 3 calls and no log; when `result.current` first reads `true`, the root has no `dark` class. (b) `ApiError(500, …)`: 1 call, 1 log, `true` at once, and no call after 70 s. (c) `ApiError(503, 'FETCH_FAILED')` on every call: `true` after the first call, exactly 33 calls and 1 log. (d) `ApiError(503, 'BACKEND_NOT_READY')` on every call: `false` until the 33rd call fails, then `true` and 1 log. (e) Unmounting during a backoff means no further call. | `BOOT_RETRY`; `lib/api.ts` | The baseline single-shot hook never applies light in (a) and returns no `settled` value |
| AC-94.7 | integration | Electron, Settings live toggle (`settings.test.ts`, `installSettingsSeam(page, …, { themeProbe: { theme: { answer: 'dark' } } })`): `THEME_COLOURS` Dark; click `theme-light-btn` → `THEME_COLOURS` Light without navigation; click `theme-dark-btn` → Dark. | 06 "Tests" (live toggle); known issue | Red on the baseline renderer: in Dark the options carry the fixed light pair ("Option menu"), and in Light the Settings selects stay `rgb(26, 26, 46)` |
| AC-94.8 | integration | Electron cold boot, Settings (`settings.test.ts`, `installSettingsSeam(page, …, { themeProbe })`, fresh app data unless stated; four tests titled `AC-94.8 (a)` to `(d)`). **(a) Stored Light, no mirror** (an existing profile): `{ mirror: null, theme: { hold: true } }`. While held: `themeProbeCounts` shows `held ≥ 1`, `app-shell` and `route-theme-pending` are visible, and no select has been inserted. After `releaseTheme(page, 'light')`: `released ≥ 1`; `html` has no `dark` class; at least 8 selects have been inserted, each recorded with the Light oracle and none `whileHeld`; and `THEME_COLOURS` Light. **(b) Stale mirror:** `{ mirror: 'dark', theme: { hold: true } }`, released `'light'`: the same assertions as (a). **(c) Mirror agrees:** `{ mirror: 'light', theme: { hold: true } }`. While held, `html` has no `dark` class (the shell's first paint) and no select has been inserted; after release `'light'`, `THEME_COLOURS` Light. **(d) The mirror persists across launches:** launch 1 with `launchWithAppData(dir)` and `{ theme: { answer: 'light' } }` (no `mirror`) polls until `localStorage[THEME_STORAGE_KEY]` is `'light'`, then closes. Launch 2 on the same `dir` with `{ theme: { hold: true } }` (no `mirror`): while held, `held ≥ 1` and `html` has no `dark` class; after release `'dark'`, `html` has `dark` and `THEME_COLOURS` Dark. | 06 "First paint", "Tests" (cold boot); review round 1 F1, F2 | Red on the baseline renderer: no `route-theme-pending` appears and selects are inserted dark while held ((a), (b)); `html` keeps `dark` while held ((c), (d)) |
| AC-94.9 | integration | Electron, TTS cold boot with no mirror (`tts-generate.test.ts`, fresh app data, `installTtsSeam(page, { themeProbe: { mirror: null, theme: { hold: true } } })`, the TTS route opened while held). While held: `held ≥ 1`, `route-theme-pending` is visible and no select has been inserted. After `releaseTheme(page, 'light')`: the TTS selects are inserted, each recorded with the Light oracle and none `whileHeld`, and `THEME_COLOURS` Light on TTS. | 06 "Tests"; known issue (TTS dark on a light cold boot) | Red on the baseline renderer: no placeholder, and the TTS selects are inserted dark while held |
| AC-94.10 | integration | Electron, Convert cold boot with a stale mirror (`convert-queue.test.ts`, fresh app data, `installSeam(page, …, { themeProbe: { mirror: 'dark', theme: { hold: true } } })`, the Convert route opened while held). While held: `held ≥ 1`, `route-theme-pending` is visible and no select has been inserted. After `releaseTheme(page, 'light')`, open `convert-advanced`: every select is recorded with the Light oracle, none `whileHeld`, and `THEME_COLOURS` Light on Convert. | 06 "Tests" | Red on the baseline renderer: no `route-theme-pending` while held |
| AC-94.11 | unit | `THEME_GATE` (`theme-selects.test.tsx`, jsdom, the `app-shell-wiring.test.ts` `window.api` stub, `import * as shell` of `AppShell`). `typeof shell.RouteThemePending` is `'function'`. Rendered alone with fake timers, it has `role="status"` and the text `Connecting...`, then `Still loading…` after 3000 ms. `AppShell` is rendered from `html.dark` with a child that records `document.documentElement.classList.contains('dark')` at its first render, and a `fetch` whose `/settings/ui` answer is a deferred promise. Before the answer: `route-theme-pending`, `nav-settings` and `header-console-btn` are present and the child is absent. After answering `200 {theme: 'light'}`: the child is present, the placeholder is gone, and the child recorded `false`. With `/settings/ui` answering 599, the child renders after that one answer. | 06 "First paint"; §Progressive Loading Strategy; `THEME_GATE` | The baseline shell renders the child before the answer, and the child records `dark` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Re-render on a theme change | Spec / Research-backed | 06 "Reactive styles": one hook on `THEME_CHANGED_EVENT`. `useSyncExternalStore` is React's API for an external store read during render (R-a; D-105) |
| Option menu pair | Spec | 06 "Option menu" (`G30_STYLES`) |
| One copy | Spec | 06 "One copy" (ConsolePanel) |
| Persisted theme before the first route renders | Spec / Research-backed | 06 "First paint": the route waits for the stored theme (`THEME_GATE`, D-117); a synchronous `localStorage` mirror read before `createRoot` sets the shell's first paint (R-c; D-107). The 06 row's citation is corrected to §Progressive Loading Strategy in row 1 (D-109) |
| Route area while it waits | Spec | 06 §Progressive Loading Strategy: per-panel "Connecting..." and "Still loading…" after 3 s, never a full-screen block (`THEME_GATE`) |
| Boot request while the backend starts | Local Canon | `lib/api.ts` maps a not-ready backend and a failed fetch to 503 (D-108) |
| Proof in both themes and after a cold boot | Spec / Local Canon | 06 "Tests"; G30 checklist item 6; the spec seams (`THEME_PROBE`, D-114) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/lib/theme.ts` | modify | `useDocumentTheme`; `THEME_STORAGE_KEY`, `readBootTheme`, mirror in `applyDocumentTheme`; `BOOT_RETRY` in `useSyncDocumentTheme` |
| `ui/src/renderer/src/boot-theme.ts` | new | applies `readBootTheme()` at module evaluation |
| `ui/src/renderer/src/main.tsx` | modify | first import `./boot-theme` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `THEME_GATE`: route children wait for `settled`; exports `RouteThemePending` |
| `ui/src/renderer/src/components/ui/SelectInput.tsx` | modify | `g30StylesFor`, `useG30Styles`; select and options use the hook; `getG30Styles`, `NATIVE_OPTION_MENU_STYLE` removed |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modify | copy removed; `console-search` uses `useG30Styles()` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | named-menu select and option use `useG30Styles()` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | `GridSelect` and `audio_format` select and options use `useG30Styles()` |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | redundant `style` props removed (three selects) |
| `ui/src/renderer/src/features/tts/VoiceCombobox.tsx` | modify | redundant `style` prop removed |
| `ui/tests/unit/theme-selects.test.tsx` | new | AC-94.1–94.6, AC-94.11 |
| `ui/tests/unit/chrome-zorivest.test.ts` | modify | TA-1 |
| `ui/tests/unit/tts-page.test.ts` | modify | TA-2 |
| `ui/tests/unit/console-polish.test.ts` | modify | TA-3 (EC-3, D-118) |
| `ui/tests/e2e/theme-probe.ts` | new | `THEME_PROBE` helper |
| `ui/tests/e2e/settings.test.ts` | modify | AC-94.7, AC-94.8; the seam's `themeProbe` option and request-time probe lookup |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-94.9; the same seam change |
| `ui/tests/e2e/convert-queue.test.ts` | modify | AC-94.10; the same seam change, and the `app-shell` wait under `hold` |

### MEU-93 — `gui-path-fields`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| IPC `showDirectoryDialog` (`preload.ts`, channel `show-directory-dialog`) | existing (unchanged) | returns a path string or `undefined` (cancel) | n/a |
| Settings leaf `converter.output_dir` | existing (unchanged) | string; saved by `convert-page-save` | unchanged |
| Settings leaf `tts.output_path` | existing (unchanged) | string; `PUT` after Browse (as today) | unchanged |
| Settings leaf `capture.backup_dir` | existing (unchanged) | string; empty → the placeholder default | unchanged |
| `PathRow` props | `PATH_ROW_PROPS` | `placeholder?: string`, `browseDisabled?: boolean`, both optional | n/a |
| REST, OpenAPI, MCP | unchanged | no change | no change |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-93.1 | unit | `PATH_ROW_PROPS` (`layout-primitives.test.ts`, `loadComponent('PathRow')`): `placeholder="D:/x"` reaches the input; `browseDisabled` disables the Browse button and a click does not call `onBrowse`; without either prop the input has no `placeholder` attribute and the button no `disabled` attribute. AC-51.4, AC-51.5, AC-51.6 and AC-58.5 stay green. | 06 §Path fields "One primitive" | `browseDisabled={false}` leaves Browse enabled |
| AC-93.2 | integration | Convert (`convert-page.behavior.test.ts`): `convert-output-dir` is labelled "Output folder" (`getByLabelText`) and is a `PathRow` (its `FormRow` grid wrapper holds the input and `convert-output-dir-browse`). Clicking Browse with the mock dialog answering `'C:/e2e/outdir'` sets the field to it, and `convert-page-save` then sends `output_dir: 'C:/e2e/outdir'`. With the dialog answering `undefined`, the value is unchanged and the save stays clean (no `btn-save-dirty`). AC-33.17 (typed edit, save only on `convert-page-save`) stays green. | 06 "Convert output"; triage D-76 | No `PUT /settings/converter` is sent by Browse alone |
| AC-93.3 | integration | TTS (`tts-page.behavior.test.ts`): `output-path` is labelled "Output path" (`getByLabelText`), is `readOnly`, and sits in a `PathRow` inside `[data-run-bar]`. Browse with `'D:/audio'` sets the field and sends one `PUT /settings` with `output_path: 'D:/audio'`. Cancel (`undefined`) sends no `PUT` and keeps the value. While a job is running, `browse-output-btn` is disabled. AC-56.4's run-bar containment stays green. | 06 "TTS output"; triage D-76 | Typing in `output-path` does not change it |
| AC-93.4 | integration | Settings (`settings-path-fields.test.tsx`, jsdom, the `settings-emphasis.test.tsx` harness with a capture fixture `inbox_dir: 'C:/inbox'`, `backup_dir: ''`): `settings-leaf-capture-backup_dir` has placeholder `C:/inbox/.avkit-backup` and sits in a `PathRow` with `settings-capture-backup-browse`. Browse answering `'C:/e2e/outdir'` sets the field to it; cancel keeps it empty. Source: `SettingsPage.tsx` contains no `showDirectoryDialog` call outside a `PathRow` `onBrowse` (every `showDirectoryDialog(` sits inside an `onBrowse=` handler). | 06 "One primitive" | The baseline hand-built `FormRow` fails the source check |
| AC-93.5 | unit | `CONVERT_BROWSE_INDEX` audit (`gui-actions-audit.test.ts`, AC-71.14 pattern): the `convert:browse_output_dir` row appears once, equals the contract line, and directly follows `convert:gpu_refresh`; its IPC cell resolves to `show-directory-dialog`, which `RENDERER_TO_MAIN_CHANNELS` and `listRegisteredChannels()` contain and the preload invokes; `convert-output-dir-browse` is in `test-ids.ts` and, as a literal, in production source; `CONVERT_AUDIT_TESTIDS` maps it to the row. | 06 "Tests"; AC-23.20 | A second copy of the row, or one placed elsewhere, fails |
| AC-93.6 | unit | `test-ids.ts` (asserted in `gui-actions-audit.test.ts`, which reads it): the MEU-93 block follows the MEU-71 block, `convert-output-dir-browse` is registered once, and AC-51.6 (prefix hash) and AC-81.13 stay green. | Local Canon (AC-51.6) | The id is not in the MEU-51 prefix |
| AC-93.7 | integration | Electron, Convert (`convert-queue.test.ts`): `convert-output-dir-browse` is visible beside `convert-output-dir`; a click fills the field with the E2E dialog answer `C:/e2e/outdir` (`ui/src/main/index.ts:343-347`). | 06 "Tests" (Electron Convert Browse) | Red on the baseline renderer: `toBeVisible` fails (no Browse) |
| AC-93.8 | integration | Electron, TTS regression: the existing Browse flow (`tts-generate.test.ts:371-396`) and AC-64.6 pass on the `PathRow` run bar in the same run. | 06 "TTS output"; AC-64.6 | A run-bar overflow, or AC-64.6 failing, is S4 and never a relaxed bound |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Convert Output folder | Spec | 06 "Convert output" (`PATH_ROWS`) |
| TTS output path | Spec | 06 "TTS output": `PathRow readOnly`; the busy-disabled Browse is kept through `browseDisabled` (D-111) |
| Settings capture-backup folder | Spec / Local Canon | 06 "One primitive" ("every page field that edits a folder path"); the placeholder default is Session 67's (`BACKUP_DIR_DEFAULT_NAME`) (D-112) |
| Cancel | Spec | 06 "One primitive": a cancelled dialog leaves the value unchanged |
| No API change | Local Canon | 06 "No API change" |
| Index row and audit | Local Canon | 06 "Tests"; AC-23.20 / AC-71.14 precedent (`CONVERT_BROWSE_INDEX`) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/ui/PathRow.tsx` | modify | `PATH_ROW_PROPS` |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | Output folder `PathRow` |
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | run-bar output `PathRow readOnly` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | capture-backup `PathRow` |
| `ui/tests/unit/layout-primitives.test.ts` | modify | AC-93.1 |
| `ui/tests/unit/convert-page.behavior.test.ts` | modify | AC-93.2 |
| `ui/tests/unit/tts-page.behavior.test.ts` | modify | AC-93.3 |
| `ui/tests/unit/settings-path-fields.test.tsx` | new | AC-93.4 |
| `ui/tests/unit/gui-actions-audit.test.ts` | modify | AC-93.5 |
| `ui/tests/e2e/test-ids.ts` | modify | AC-93.6 (MEU-93 block) |
| `ui/tests/e2e/convert-queue.test.ts` | modify | AC-93.7 |
| `ui/tests/e2e/tts-generate.test.ts` | modify | AC-93.8 (no new test; regression run) |
| `docs/build-plan/gui-actions-index.md` | modify | `CONVERT_BROWSE_INDEX` row |

### Hub and state files (rows 1, 7, H1-3, H2)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/06-gui.md` | modify (row 1) | §Theme-reactive selects: the "Reactive styles" row names `useDocumentTheme`/`useG30Styles` instead of "backs `getG30Styles`"; the "First paint" Source cell becomes "Triage D-77; Spec §Progressive Loading Strategy (`06-gui.md:140-146`, themed `backgroundColor`, no white flash)" (D-109). After the section tables in row 7: a `> **Delivered (Session 40).**` note per MEU naming this plan |
| `.agent/docs/emerging-standards.md` | modify (row 1) | G30 (`:1041-1077`): the rule and the good example use `useG30Styles()` for the select and its options; checklist item 2 names the hook. G32 (`:1102`): `getG30Styles()` → `useG30Styles()` (D-109) |
| `.agent/context/meu-status.yaml` | modify (row 7, H2-2) | MEU-93/94 `execution_plan` and `ready_for_review` (row 7, before the H1-2 gate binds this file); `approved` after review (H2-2, which re-runs `layout-canon` and `queue-canon`) |
| `docs/BUILD_PLAN.md` | generated | AUTOGEN regions written only by `meu_status.py render` |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 40 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | both issues → `resolved` with the handoff links, after H1-7b approval (H2) |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` (H2-2); never hand-edited |
| `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md` | modify (H2-2) | Session 40 marked delivered |
| `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md` | none planned | in the allow-list only because its uncommitted 2026-10-24 status edit is part of the working tree at baseline |
| `docs/execution/metrics.md` | modify | the Session 40 row (H2-3) |

No `build-priority-matrix.md` edit: rows 6.8 and 6.9 already exist and the matrix has no status column.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| `BrowserWindow` `backgroundColor` per theme | out-of-scope | — | §Progressive Loading Strategy owns the window colour; the issue is the select styles, and `THEME_GATE` with the renderer mirror fixes their first paint |
| Downloader selects (`SELECT_THEME_STYLE` CSS variables, `quality-options.ts:40`) | out-of-scope | — | They already follow the theme through CSS variables; not in the measured issue nor the 06 "Tests" pages |
| Any REST, OpenAPI, IPC or MCP change | out-of-scope | — | 06 §Path fields "No API change"; MEU-94 reads the existing `ui` namespace |
| Keyboard shortcuts, palette curation, Appearance commands | deferred | MEU-95, MEU-96, MEU-97 | grouping Session 41 (D-94) |
| A server-pushed theme change while the app is open (MCP edits `ui.theme`) | out-of-scope | — | Not in triage D-77; the next boot reads it through `BOOT_RETRY` |

## BUILD_PLAN.md Audit

This project edits the D3 hub only through `meu_status.py` in row 7 (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s40-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s40-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-9[34]" -e "gui-theme-path-fields" -e "Delivered \(Session 40\)" docs/BUILD_PLAN.md docs/build-plan/06-gui.md .agent/context/meu-status.yaml *> C:/Temp/av-kit/s40-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s40-hub-rg.txt; exit $code
```

Row 7's deliverable is that the `rg` receipt shows the two 06 Delivered notes, MEU-93/94 with `execution_plan` set to this plan, and the rendered `BUILD_PLAN.md` lines; and that `render --check` exits 0.

## Verification Plan

All commands run from `P:/av-kit` in `pwsh`, after `$env:ELECTRON_RUN_AS_NODE=$null` for any Electron step. Receipts go to `C:/Temp/av-kit/s40-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list.

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages`, `npm --prefix ui ci`, `npm --prefix mcp-server ci`.
- `PREREQS` (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-24-gui-theme-path-fields/baseline.sha`.
- The baseline receipts: `py-tests`, `ui-tests`, `mcp-tests`, `ui-build`, then `ui-electron` over `settings.test.ts`, `tts-generate.test.ts` and `convert-queue.test.ts`. The baseline failed sets are recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression; a test passing at baseline that fails later is one. The UI baseline is expected clean: `QUEUE-PILL-TOKEN-DRIFT` was resolved by the 31b merge (grouping D-96), so the gate's `ui-tests` excuses no id. The Python baseline keeps the Session 36/39 rule for the two environmental packaging tests (AC-24.10, AC-25.10).

### 2. Red (rows 2 and 4)

Each MEU's new and amended tests are written first. They must fail by assertion, or because a declared-new name does not exist yet (`red-check.py` `DECLARED_NEW`: `useDocumentTheme`, `useG30Styles`, `g30StylesFor`, `readBootTheme`, `THEME_STORAGE_KEY`, `boot-theme`).

- **Vitest imports are namespace imports** (`import * as theme from '../../src/renderer/src/lib/theme'`). Each test first asserts `expect(typeof theme.useDocumentTheme).toBe('function')` (or the name's expected type), so a missing export fails as an assertion in that test instead of a `TypeError: … is not a function`, which `red-check.py` refuses.
- **`boot-theme.ts` is checked as source text** (`existsSync`, then the first `import` of `main.tsx`), never imported. A missing module therefore fails one assertion instead of breaking the whole test file at load.
- **Electron tests assert `toBeVisible()` before acting on any new element** (for example `convert-output-dir-browse`), so a missing element fails by `expect` instead of a `locator.click: Timeout`, which is refused. Colour checks use `expect.poll`; a poll that times out is an `expect` failure, which the checker accepts. It refuses only `Test timeout of Nms exceeded`, `TimeoutError` and `locator|page|frame|elementHandle.<action>: Timeout`, plus `ECONNREFUSED` and `EADDRINUSE`.
- **No pytest Red:** this plan changes no Python.
- **Row 2 (MEU-94):** Vitest `-t "AC-94"` over `theme-selects.test.tsx` with TA-1 and TA-2 applied, then the UI build and Electron `--grep "AC-94"` over the three specs, **on the baseline renderer**: the command refuses any `ui/src` change. AC-94.7, AC-94.8 (each of its four tests), AC-94.9, AC-94.10 and AC-94.11 must fail by `expect` (`--require`).
- **Row 4 (MEU-93):** Vitest `-t "AC-93"` over the four MEU-93 unit files, then the build and Electron `--grep "AC-93.7"` over `convert-queue.test.ts`, **on the row 3 tree**. Row 3's command ends by writing `row3-ui-src.json` (a SHA-256 per file under `ui/src`); row 4 recomputes it and refuses any `ui/src` file that was added, removed or changed since. AC-93.6 may pass at Red if the id block is written first; AC-93.7 must fail by `expect` (`--require AC-93.7`). AC-93.8 is a regression run and is not part of Red.

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit and exactly one failing-run summary (Vitest or Playwright);
- no hard setup failure anywhere in the receipt: an Electron launch failure, a test or action timeout, a refused connection or busy port, or Vitest unhandled errors;
- **every failure block is attributed:** the receipt is split into one block per failed test (Vitest `FAIL` headers, Playwright `N) title` headers), and the number of blocks equals the summary's failed count, so a failure that is not shown cannot hide. Every block carries at least one diagnostic, and **every** diagnostic in it is an assertion (`AssertionError`, `Error: expect(`) or a load/import error whose missing *subject* is exactly a declared-new name (or ends in one after a `.` or `/`). A `TypeError: … is not a function` is never attributed, even for a declared name: the namespace-import strategy makes the assertion fail first. One unrelated diagnostic refuses the block, even beside a valid assertion;
- **`--require TITLE`** (row 2: AC-94.7, AC-94.8, AC-94.9, AC-94.10, AC-94.11; row 4: AC-93.7): each named test has its own failure block whose diagnostics are all assertions. A required test that passed, or failed only by a declared-new name, is refused. The title match is exact up to a non-digit (`AC-94.1` does not match `AC-94.10`, and `AC-94.8` matches each of `AC-94.8 (a)` to `(d)`, every one of which must fail by assertion).

Source-context and test-title lines never count. `red-check.py --selftest` runs 36 receipt fixtures, including the negative `vitest-not-a-function-is-unattributed` (R-2).

### 3. Targeted Green (rows 3 and 5)

Row 3 runs the MEU-94 Vitest files, then the build and the three Electron specs. Row 5 runs the MEU-93 Vitest files, then the build and the same three specs.

```powershell
rtk proxy npm --prefix ui run test -- tests/unit/theme-selects.test.tsx tests/unit/chrome-zorivest.test.ts tests/unit/tts-page.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/capture-page.test.ts tests/unit/capture-flatten.test.ts tests/unit/app-shell-wiring.test.ts tests/unit/console-polish.test.ts tests/unit/header-toggles.test.ts tests/unit/downloader-page.behavior.test.ts *> C:/Temp/av-kit/s40-94-green-ui.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s40-94-green-ui.txt -Tail 25; exit $code
```

```powershell
rtk proxy npm --prefix ui run test -- tests/unit/layout-primitives.test.ts tests/unit/convert-page.behavior.test.ts tests/unit/convert-page.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/tts-page.test.ts tests/unit/settings-path-fields.test.tsx tests/unit/gui-actions-audit.test.ts tests/unit/capture-page.test.ts tests/unit/capture-flatten.test.ts tests/unit/capture-action-row.test.ts *> C:/Temp/av-kit/s40-93-green-ui.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s40-93-green-ui.txt -Tail 25; exit $code
```

```powershell
$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/s40-<meu>-green-build.txt; if ($LASTEXITCODE -ne 0) { Get-Content C:/Temp/av-kit/s40-<meu>-green-build.txt -Tail 25; exit $LASTEXITCODE }; rtk proxy npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts tests/e2e/tts-generate.test.ts tests/e2e/convert-queue.test.ts *> C:/Temp/av-kit/s40-<meu>-green-e2e.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s40-<meu>-green-e2e.txt -Tail 30; exit $code
```

`<meu>` is `94` in row 3 and `93` in row 5. The task rows hold the exact commands.

### 4. Session gate (rows 6, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from `P:/av-kit`. It writes one receipt per step (`C:/Temp/av-kit/s40-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`. The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, then `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:** `py-tests` (whole suite, with the baseline rule for the two environmental packaging tests: a packaging test is excused only if it appears as `FAILED <id>` in the row 0 receipt `s40-base-py.txt`, and a missing receipt excuses nothing; the gate prints the excused ids), `ui-tests` (no excused id), `mcp-build`, `mcp-tests` (the build first, because the tests load `mcp-server/dist`), `ui-build`, `ui-harness-build`, `ui-picker-stub`, `openapi`, `state-render`.
4. **Runtime:** `ui-electron` (the full Electron suite, because `SelectInput`, `PathRow` and `lib/theme.ts` are shared by every page), then `e2e-repeat`: `test:e2e -- tests/e2e/settings.test.ts tests/e2e/tts-generate.test.ts tests/e2e/convert-queue.test.ts --grep "AC-94|AC-93|AC-64.6" --repeat-each=10`. Any flake is a defect (S6).
5. `identity-npm`, then `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-24-gui-theme-path-fields/session-gate.ps1`, with the receipt pattern (task row 6).

The D6 `mcp-audit` runtime check is not a gate step: this plan changes no MCP action, schema or API; `mcp-build` and `mcp-tests` show the server still builds and passes.

### 5. `SCOPE_CHECK` (row 6)

- **`scope-paths`:** every path in `git diff --no-renames --name-only -z <baseline>` plus `git ls-files --others --exclude-standard -z` is a Files Modified row (product, test, hub and state files) or one of this project's artifacts (this plan folder, the handoffs, the reflection). With `--no-renames`, a rename shows its source deletion as well as its destination, so a move out of a disallowed path is caught. `-z` keeps paths with spaces or non-ASCII names whole (R-4). The allow-list in the script is the union of the Files Modified tables; changing either means changing both.

### 6. OpenAPI drift (G8)

No `packages/api/` file changes. `openapi.committed.json` is not regenerated, and the `openapi` D6 check (`--check`) must pass in the gate. H1-4 proves the committed file is unchanged since `baseline.sha`: added, removed and changed schemas are all empty (any change is S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths:

- `validate_closeout_artifacts.py` per handoff, run twice: with `--handoff` + `--plan`, then with `--ac-coverage-only`;
- `durable_evidence.py --require-full`;
- the review-state parsers;
- the reflection validator, with `--decision-source` for the plan, the two handoffs, the 2026-10-17 grouping and `.agent/context/known-issues.yaml`, and `--decision-issue` for each of the two issue ids;
- `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent (recorded `gui-refs-not-shipped`). Two elements are added (`convert-output-dir-browse` and the `route-theme-pending` placeholder); the changed and new ones:

| Element | Kind | Change | Standard | E2E |
|---|---|---|---|---|
| Every `SelectInput` select and option (TTS, Convert, VoiceCombobox, MCP and other Settings `GridSelect`s) | select (changed) | `useG30Styles()` for the select and its options | G30 (`emerging-standards.md:1041`) | AC-94.7–94.10 |
| Settings `GridSelect` / `audio_format` raw selects | select (changed) | same | G30 | AC-94.7, AC-94.8 |
| CaptureViewport named-menu select | select (changed) | same | G30 | — (AC-94.3 source check; the capture Electron wave runs in the gate) |
| `console-search` | input (changed) | `useG30Styles()` | G30, G32 (`:1102`) | — (full Electron suite in the gate) |
| `route-theme-pending` | status placeholder (new) | `RouteThemePending` in `AppShell`'s `<main>` while the boot theme is unknown | 06 §Progressive Loading Strategy (per panel, never full-screen) | AC-94.8–94.11 |
| `convert-output-dir` + `convert-output-dir-browse` | path field (changed / new button) | `PathRow` | G31 (Browse: secondary `sm`, the `PathRow` default), E2 (`:1167`) | AC-93.7 |
| `output-path` + `browse-output-btn` | path field (changed) | `PathRow readOnly`, `browseDisabled={busy}` | E2 | AC-93.8, AC-64.6 |
| `settings-leaf-capture-backup_dir` + `settings-capture-backup-browse` | path field (changed) | `PathRow` with `placeholder` | E2 | the capture-inbox Electron test (`:1548-1558`) in the gate |

G36 (no silent test guards): the colour and Browse tests assert; they never `skip`. G37: behaviour tests use `userEvent`. G33–G35 surfaces are unchanged.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, or a `PREREQS` status or symbol is not as stated | Stop. Ask Mat, or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS`, including a unit or Electron test that reads route content inside `AppShell` before the boot theme settles | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2) | Fix the test setup only, then re-prove Red. |
| S4 | AC-56.4's run bar or AC-64.6 breaks with the TTS `PathRow`; or the probe never holds a theme request (`held` stays 0, so AC-94.8 cannot observe a first paint); or `localStorage` does not persist across two launches that share `AVKIT_APP_DATA` (AC-94.8 (d)) | Stop for a Decision Brief with the measurement. For a run-bar break, option B is the field on its own row above the run bar. The bounds are contracts, not tuning knobs. |
| S5 | `SCOPE_CHECK` finds a path outside `PRODUCT_SCOPE`, or `openapi.committed.json` changes | Revert that change or stop with a Decision Brief. |
| S6 | An Electron flake in `--repeat-each` | Fix the test's waiting, never add retries; if the product is racy, stop with a brief. |
| S7 | Review cap (plan 3, execution 6) or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |

## Decision Log

Research engine for this plan: `native` (Claude Code reading of the renderer source and the React, Electron and MDN documentation, 2026-10-24). Grouping §8 D-94, D-95 and D-103 carry forward unchanged into the reflection (stage `grouping`). "Triage D-76/D-77" are the 2026-10-17 triage decisions in `known-issues.yaml` (`:2767`, `:2828`) that the spec and the known issues cite. This plan's ids start at D-104.

```yaml
decision_log:
  - id: D-104
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "P:/av-kit on main, no worktree"
    source_tag: Local Canon
    precedents: ["D6 default cwd is P:/av-kit (.agent/docs/commands.md:190-210)", "Session 31b merged and history squashed 2026-10-24; no other session branch is open"]
    research: { engine: none, sources: [] }
    reasoning: "Earlier sessions used a worktree to isolate themselves from other open session branches. None is open now, and the approved grouping and status edits this plan builds on are uncommitted on main, so a worktree would have to copy them. The scope allow-list covers those files. Two-way: a worktree can still be cut before execution if another session opens."
  - id: D-105
    stage: planning
    question: "How do already-mounted selects learn the theme changed?"
    resolution: autonomous
    class: two-way
    chosen: "THEME_HOOK: useDocumentTheme on useSyncExternalStore, subscribed to THEME_CHANGED_EVENT, snapshot from html.dark"
    source_tag: Research-backed
    precedents: ["06 §Theme-reactive selects 'One hook (subscribing to THEME_CHANGED_EVENT)'", "lib/theme.ts:43-45 already dispatches the event on every apply"]
    research: { engine: native, sources: ["https://react.dev/reference/react/useSyncExternalStore"] }
    reasoning: "useSyncExternalStore is React's documented way to read an external mutable source during render without tearing; every consumer re-renders when the snapshot changes. A React context provider at AppShell was rejected because route pages are children created above it, and a provider adds a second source of truth beside the DOM class. Reading the class in the snapshot keeps applyDocumentTheme the only writer."
  - id: D-106
    stage: planning
    question: "What replaces getG30Styles, and what does the option menu use?"
    resolution: autonomous
    class: two-way
    chosen: "G30_STYLES: pure g30StylesFor(theme) plus useG30Styles(); the select and its options use the same pair; getG30Styles, NATIVE_OPTION_MENU_STYLE and the ConsolePanel copy are removed"
    source_tag: Spec
    precedents: ["06 'Option menu' (the pair follows the theme)", "06 'One copy' (ConsolePanel duplicate removed)", "G30 good example uses one pair for select and options (emerging-standards.md:1041-1077)"]
    research: { engine: native, sources: ["https://textslashplain.com/2021/10/17/spooky-enhancing-dark-mode-in-chromium"] }
    reasoning: "A function that reads the DOM at render cannot re-render its caller, so the name must become a hook. Keeping a getG30Styles alias would leave a non-reactive path that the next consumer could pick up. Chromium paints the native option popup from the option's own inline colours (triage D-77 source), so one pair for both keeps the menu readable in each theme. CSS variables were rejected because G30 requires inline hex values for the options."
  - id: D-107
    stage: planning
    question: "How is the persisted theme applied before the first render?"
    resolution: autonomous
    class: two-way
    chosen: "BOOT_THEME: applyDocumentTheme mirrors the theme to localStorage; boot-theme.ts, the first import of main.tsx, applies it before createRoot"
    source_tag: Research-backed
    precedents: ["06 'First paint'", "06 §Progressive Loading Strategy (06-gui.md:140-146) 'no white flash'", "ui/src/main/index.ts:220-222 userData from AVKIT_APP_DATA (localStorage persists per profile)"]
    research: { engine: native, sources: ["https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage", "https://www.electronjs.org/docs/latest/api/native-theme"] }
    reasoning: "localStorage is synchronous and persists in the renderer profile, so the boot module can apply the last theme before any route renders. An inline script in index.html was rejected because the CSP is script-src 'self'. A main-process read (IPC or argv) was rejected because main does not own ui.theme and would need the backend before the window exists. nativeTheme follows the OS, not the user's setting. The mirror alone does not decide the route's first paint: a profile with Light stored and no mirror, or a stale mirror, would still paint dark (review round 1 F1). THEME_GATE (D-117) decides it; the mirror keeps the always-visible shell in the last theme while the route waits. User Review Required item 1 states the behaviour."
  - id: D-108
    stage: planning
    question: "What happens when the boot theme request fails because the backend is still starting?"
    resolution: autonomous
    class: two-way
    chosen: "BOOT_RETRY: retry only ApiError 503 with backoff 250/500/1000 ms then 2000 ms inside a 60 s window, one log on final failure; the hook returns settled for THEME_GATE"
    source_tag: Local Canon
    precedents: ["lib/api.ts maps a not-ready backend to ApiError(503, BACKEND_NOT_READY) after its 10 s wait, and a failed fetch to ApiError(503, FETCH_FAILED)", "known issue: 'the boot fetch is single-shot with no retry'"]
    research: { engine: none, sources: [] }
    reasoning: "503 is the client's own signal for 'backend not reachable yet'; anything else is a real answer and retrying it would only repeat the error. The schedule covers a slow first start (model warm-up) without polling forever. A window replaced an attempt count because a BACKEND_NOT_READY attempt itself waits up to 10 s inside apiFetch, so a count would not bound the time. In E2E, a load without a seam gets FETCH_FAILED and retries in the background; THEME_GATE does not wait for it, and the single log line moves from the first failure to the end of the window."
  - id: D-109
    stage: planning
    question: "Which canon text changes with the new hook?"
    resolution: autonomous
    class: two-way
    chosen: "Row 1 updates G30 and G32 to useG30Styles(), the 06 'Reactive styles' row to name the hook, and the 06 'First paint' citation to §Progressive Loading Strategy"
    source_tag: Local Canon
    precedents: ["G30 preferred getG30Styles() (emerging-standards.md:1041-1077)", "G32 mentions getG30Styles() (:1102)", "06 First paint cited 'Spec §Loading (no theme flash)', a section that does not exist under that name"]
    research: { engine: none, sources: [] }
    reasoning: "Canon that names a removed function would steer the next consumer back to it. The 06 citation pointed at a heading that does not exist; §Progressive Loading Strategy is the section that requires a themed first paint. The edits change names and a citation, not a rule, so they stay inside triage D-77."
  - id: D-110
    stage: planning
    question: "How is the new Convert Browse registered and audited?"
    resolution: autonomous
    class: two-way
    chosen: "CONVERT_BROWSE_INDEX: an index row after convert:gpu_refresh, a MEU-93 test-ids block, a CONVERT_AUDIT_TESTIDS entry and an AC-71.14-style audit"
    source_tag: Local Canon
    precedents: ["06 §Path fields 'Tests' (gui-actions-index gains the convert-output-dir-browse row)", "AC-71.14 audit (gui-actions-audit.test.ts:303-345)", "tts:browse_output and settings:browse_convert_dir rows use 'IPC showDirectoryDialog + the settings leaf'"]
    research: { engine: none, sources: [] }
    reasoning: "The audit already proves that every index row resolves to a registered IPC channel and that every audited test id exists in source; adding the row the same way keeps the index complete. The row sits beside the other convert rows."
  - id: D-111
    stage: planning
    question: "How does the TTS run-bar output path become PathRow without losing its busy-disabled Browse?"
    resolution: autonomous
    class: two-way
    chosen: "PathRow readOnly with an additive browseDisabled prop; ids kept; the field stays in the run bar with a visible label"
    source_tag: Spec
    precedents: ["06 'TTS output' (PathRow readOnly; output-path and browse-output-btn kept)", "TTSPage.tsx:650 Browse disabled while busy", "AC-56.4 run-bar containment (tts-page.behavior.test.ts:385-404)"]
    research: { engine: none, sources: [] }
    reasoning: "Dropping the busy guard would let a second dialog open during a job. An additive optional prop leaves every existing PathRow unchanged. The visible label is what PathRow renders (FormRow), and it replaces the aria-label. If the run bar overflows or AC-64.6 breaks, S4 offers moving the field above the run bar."
  - id: D-112
    stage: planning
    question: "Does the Settings capture-backup folder also become PathRow?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, with an additive placeholder prop; ids and the default-folder placeholder kept"
    source_tag: Spec
    precedents: ["06 'One primitive' (every page field that edits a folder path renders PathRow)", "SettingsPage.tsx:995 comment 'PathRow markup … with the default folder as a placeholder'"]
    research: { engine: none, sources: [] }
    reasoning: "It is the last hand-built copy of PathRow on Settings, built that way only because PathRow had no placeholder. One optional prop removes the copy. AC-67.24 and AC-67.26 keep pinning its ids."
  - id: D-113
    stage: planning
    question: "How do the Red tests fail cleanly when the new names do not exist yet?"
    resolution: autonomous
    class: two-way
    chosen: "Namespace imports with a typeof assertion first; boot-theme.ts checked as source text; toBeVisible before any action on a new element"
    source_tag: Local Canon
    precedents: ["Session 35 RED_PROOF (red-check.py refuses setup failures)", "red-check.py fixture vitest-not-a-function-is-unattributed"]
    research: { engine: none, sources: [] }
    reasoning: "A named import of a missing export is undefined, and calling it throws a TypeError that says nothing about the contract; a typeof assertion turns it into an attributed failure. Importing a missing module fails the whole file at load, hiding every other test, so the boot module is checked as text. A click on a missing element waits for a timeout, which the checker refuses, so visibility is asserted first."
  - id: D-114
    stage: planning
    question: "How do the Electron tests observe first paint and a held boot request?"
    resolution: autonomous
    class: two-way
    chosen: "THEME_PROBE: an init-script-only helper that the seam installers register before their single reload; each seam's fetch consults window.__avkitThemeProbe at request time; the probe seeds the mirror, holds or answers GET /settings/ui, counts held and released requests, and records each select's colours at insertion"
    source_tag: Local Canon
    precedents: ["spec seams install an init script then reload once (settings.test.ts:110-112, tts-generate.test.ts:246-247, convert-queue.test.ts:465-466)", "Playwright: the evaluation order of several init scripts is not defined (page.addInitScript)", "plan-critical-review round 1 F2"]
    research: { engine: native, sources: ["https://playwright.dev/docs/api/class-page#page-add-init-script"] }
    reasoning: "Holding the theme request is the only way to see what the page paints before the GET answers, and a MutationObserver installed at document start sees each select as React inserts it. A second reload after the seam's would let the seam's own dark answer reach the app first (review F2), so the probe never navigates. Looking the probe up at request time removes any dependence on init-script order. Seeding the mirror from the init script gives the no-mirror and stale-mirror cases in one launch. Two launches on one AVKIT_APP_DATA are kept only to prove the mirror persists; launch 2's un-seamed first load gets FETCH_FAILED, which writes nothing, so it cannot overwrite the mirror. Counting held and released requests proves the hold happened. A shared helper module (not a test file) avoids one spec importing another."
  - id: D-115
    stage: planning
    question: "Do the Electron tests go in a new spec or the existing page specs?"
    resolution: autonomous
    class: two-way
    chosen: "The existing settings, tts-generate and convert-queue specs, which already own each page's seam"
    source_tag: Local Canon
    precedents: ["each page seam lives in its spec (settings.test.ts:11-20, tts-generate.test.ts:13, convert-queue.test.ts:143)"]
    research: { engine: none, sources: [] }
    reasoning: "A new spec would have to copy three seams. The probe is shared, and the seams stay where they are."
  - id: D-116
    stage: planning
    question: "Are the Downloader selects in scope?"
    resolution: autonomous
    class: two-way
    chosen: "No"
    source_tag: Local Canon
    precedents: ["quality-options.ts:40 SELECT_THEME_STYLE uses CSS variables, which follow the class change", "06 'Tests' names Settings, TTS and Convert"]
    research: { engine: none, sources: [] }
    reasoning: "Their colours come from CSS variables, which change with the html class and need no re-render. They are not in the measured issue. The full Electron suite in the gate still runs the Downloader page."
  - id: D-117
    stage: planning
    question: "How does a cold boot apply the stored theme before the first route renders when the mirror is missing or stale?"
    resolution: autonomous
    class: two-way
    chosen: "THEME_GATE: AppShell renders the route children only after the boot GET settles, with a per-panel RouteThemePending placeholder until then; the shell is never gated"
    source_tag: Spec
    precedents: ["06 'First paint' (the persisted theme is applied before the first route renders)", "06 §Progressive Loading Strategy (06-gui.md:140-146: shell first, per-panel 'Still loading…', never full-screen)", "ipc.ts:322-323 get-backend-url waits for the published backend", "plan-critical-review round 1 F1"]
    research: { engine: none, sources: [] }
    reasoning: "The stored ui.theme lives in the backend, so only its answer makes the first route paint right for a profile with no mirror or a stale one. The wait is tied to the backend being unpublished (BACKEND_NOT_READY), when route pages cannot load data anyway. The placeholder sits in the route panel, so the shell, console and palette stay usable, as §Progressive Loading Strategy requires. Opening on FETCH_FAILED and on other errors keeps a broken backend from hiding the route. It also leaves every Electron spec without a theme seam unchanged, because the E2E backend is published, unreachable, at once. A fixed time cap was rejected: it would let a slow backend's first route paint dark again. Gating the whole window or the shell was rejected as a full-screen block."
```

## Research References

- React `useSyncExternalStore` (subscribe and snapshot; re-render on change): https://react.dev/reference/react/useSyncExternalStore (R-a)
- Chromium paints the native option popup from the option's own colours; dark mode needs both pairs: https://textslashplain.com/2021/10/17/spooky-enhancing-dark-mode-in-chromium (triage D-77 source)
- MDN `Window.localStorage` (synchronous, persists per origin and profile; `setItem` can throw): https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage (R-c)
- Electron `nativeTheme` (follows the OS setting; rejected for a user setting): https://www.electronjs.org/docs/latest/api/native-theme
- Playwright `page.addInitScript` (the evaluation order of several init scripts is not defined): https://playwright.dev/docs/api/class-page#page-add-init-script (D-114)

The plan relies on three facts. A component that reads through `useSyncExternalStore` re-renders when the snapshot changes. `localStorage` reads are synchronous and survive a restart within one `userData` profile. Chromium styles the open option list from each option's inline colours. R-b checks the CSP that rules out an inline script.

## Planning receipts

- **R-1 (2026-10-24).** `identity.py --selftest`, exit 0, 0 failures (`C:/Temp/av-kit/s40-plan-R-identity.txt`). Each bound path, an untracked test file and the runtime keys change `tested_state` and make `durable_evidence.evidence_problems` refuse the earlier full record. Edits to the closeout artifacts leave it unchanged. `NAMED_DISTRIBUTIONS` is empty: this plan changes no Python.
- **R-2 (2026-10-24).** `red-check.py --selftest`, exit 0, 36 fixtures, 0 wrong (`C:/Temp/av-kit/s40-plan-R-redcheck.txt`). It includes the negative `vitest-not-a-function-is-unattributed`, an `expect.poll` timeout accepted as an assertion, and a `locator.click: Timeout` refused.
- **R-3 (2026-10-24).** `session-gate.ps1` parses with 0 PowerShell parse errors (`C:/Temp/av-kit/s40-plan-R-gate-parse.txt`). It was not run during planning, because it needs the execution baseline.
- **R-4 (2026-10-24).** The `scope-paths` probe in a scratch repository, using the gate's own Python (`C:/Temp/av-kit/s40-plan-R-scope-probe.txt`). It covers four cases: a clean tree; a committed rename from a disallowed path into an allowed one, which must name the source; a new allowed file; and an untracked disallowed path containing a space and a non-ASCII character. Exit 0, 4 of 4 cases pass; the rename case lists only the source deletion.
- **R-5 (2026-10-24).** `lint_task_contract.py` over `task.md` with `RECEIPTS_DIR=C:/Temp/av-kit` (`C:/Temp/av-kit/s40-plan-R-task-lint.txt`): exit 0, 24 rows, 22 fully checked, 2 `view_file` rows exempt (H1-5, H2-1).
- **R-a / R-b / R-c (2026-10-24, native).**
  - **R-a:** the React reference for `useSyncExternalStore`.
  - **R-b:** the renderer CSP. `ui/src/renderer/index.html` declares no CSP. The production policy is `RENDERER_CSP` (`ui/src/main/index.ts:66-67`), installed on every response through `onHeadersReceived` (`:494-496`, `activeRendererCsp()`), and its `script-src 'self'` blocks an inline boot script. The development policy differs, so a dev-only pass would prove nothing; the boot module is a bundled file either way.
  - **R-d:** the E2E backend. `ui/src/main/index.ts:460-464` and `:614-620` publish `http://127.0.0.1:9/api/v1` (unreachable) at once, or after `AVKIT_E2E_BACKEND_DELAY_MS`. `ipc.ts:322-323` makes `get-backend-url` wait for that publication. So an un-seamed load gets `FETCH_FAILED` and `THEME_GATE` opens on the first attempt.
  - **R-c:** the MDN `localStorage` reference, together with `ui/src/main/index.ts:220-222` (`app.setPath('userData', AVKIT_APP_DATA)`).

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`, `scope-paths` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last input edit, from `P:/av-kit`, `pwsh`. Row 6 runs it after the product edits. Row 7 then changes bound inputs (`meu-status.yaml`, the rendered `BUILD_PLAN.md`, the 06 Delivered notes), so H1-2's run is the fresh full record the handoffs carry. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (optional, non-blocking):** Mat's visual check (User Review Required item 6).
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state`, which is HEAD plus one SHA-256. The hash covers:
  - **The work tree:** the tracked diff and the untracked (not ignored) files of the whole work tree. It excludes only this session's own closeout outputs, which no suite or gate step reads: this plan folder's `*.md`, this session's handoffs and reflection, `docs/execution/metrics.md`, `.agent/context/current-focus.md` and `known-issues.yaml`/`.md`.
    - So the lockfiles, `openapi.committed.json`, the configs and this plan's scripts are bound.
    - So are the documents the suites read: `docs/build-plan/` (`gui-actions-audit`, `capture-page`, `convert-page`, `queue-canon`, `layout-canon`), `docs/BUILD_PLAN.md`, `meu-status.yaml` and the grouping files (`layout-canon`, `queue-canon`), and `meu-registry.md` (`state-render`).
    - Row 7 therefore runs before H1-2. The post-approval status write in H2-2 re-runs `layout-canon` and `queue-canon`.
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
| EC-1 (row 0) | `session-gate.ps1` `$expectedBaselinePyFailed` gains `tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]`, excused like the other two only if `s40-base-py.txt` shows it `FAILED`. The two expected environmental tests (AC-24.10, AC-25.10) passed at baseline and so are not excused. | `walkthrough.md` §Baseline: AC-25.7 fails on HEAD `7b29fcd` against the committed `docs/distribution/mcp.json.example` (no `AVKIT_API_TOKEN`), outside `PRODUCT_SCOPE`; §1 says a test failing at baseline is never a regression. |
| EC-2 (row 4, D-119) | AC-93.4's source clause reads "every `showDirectoryDialog(` sits inside an `onBrowse=` handler" as: the call sits inside an `onBrowse=` handler, or inside a helper function whose every reference sits inside an `onBrowse=` handler. Plan review F4 (Low) carried this to row 4. | `SettingsPage.tsx:407`, `:437`, `:447`, `:457` call it from `browseDownloadPath`, `browseTranscriptDir`, `browseModelsDir` and `browseTtsOutputPath`, each referenced once from a `PathRow` `onBrowse` (`:589`, `:731`, `:770`, `:822`). Mat accepted D-119 A on 2026-10-25 (`walkthrough.md` §MEU-94 Green: S2 stop). |
| EC-3 (row 3, D-118) | `TEST_AMENDMENTS` gains **TA-3** `ui/tests/unit/console-polish.test.ts:234` (AC-27.10): `not.toContain('SelectInput')` becomes `not.toMatch(/<SelectInput\b/)` plus `not.toMatch(/import\s*\{[^}]*\bSelectInput\b[^}]*\}/)`; lines 235–237 stay. The file joins Files Modified and the `session-gate.ps1` `scope-paths` allow-list. | S2 at row 3: ConsolePanel's `useG30Styles` import path `'../ui/SelectInput'` (AC-94.3, TA-1) tripped the substring check; `SelectInput` is not in `CENSUS_PATTERNS`. Mat accepted D-118 A on 2026-10-25 (`walkthrough.md` §MEU-94 Green: S2 stop). |
| EC-4 (row 5) | The row 4 AC-93.3 test asserted the read-only `output-path` stays `''` after typing and after a cancelled Browse. It now asserts that the field keeps the value it had before typing (`initial`), which is the AC text ("Cancel ... keeps the value"; "Typing in `output-path` does not change it"). No assertion was removed, and the PUT checks are unchanged. | Row 5's first run (`s40-run-row5.txt`) failed only there: `expected '~/Documents' to be ''`. `TTSPage.tsx:64` `OUTPUT_DEFAULT` is shown while `settings.output_path` is empty. The Red run had stopped at the earlier `label[for="tts-output-path"]` assertion, so it never reached the line. This is a test-fixture fact, not a product change. Flagged for the reviewer. |
| EC-5 (rows 6–H2, D-120) | The plan closes out under Mat's ruling D-120 (2026-10-26, option 2, which revised that day's option 1). Gate runs 1–4 stand as the row 6 gate, with no re-run. H1-2 and H1-6b are waived, not run, and their task rows are `[B]` (human-decision). The H1-7 Codex execution review runs, and H2 sets MEU-93/94 to `approved` only on its approved verdict. | `walkthrough.md` §Gate ruling (D-120); `task.md` §Blocked Rows |
| EC-6 (H1-7 round 1, F1) | `useSyncDocumentTheme` bounds the whole boot load by `BOOT_RETRY_WINDOW_MS`: on expiry with an attempt pending it logs once, settles on the current document theme and ignores a late answer; unmount clears the deadline. Tests AC-94.6 (f), (g) and an AC-94.11 never-answering case are added. | `walkthrough.md` §Execution review; review round 1 F1 |
