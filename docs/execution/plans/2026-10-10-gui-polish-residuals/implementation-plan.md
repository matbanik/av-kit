---
project: "2026-10-10-gui-polish-residuals"
date: "2026-10-10"
source: "docs/build-plan/06-gui.md#header-toggles-residual; docs/build-plan/11-page-layout.md#settings-section-emphasis-residual"
meus: ["MEU-69", "MEU-70"]
status: "approved"
template_version: "2.2"
---

# Implementation Plan: GUI polish residuals (Session 31)

> **Project:** `2026-10-10-gui-polish-residuals`
> **Build plan:**
> - `docs/build-plan/06-gui.md` §Header toggles (residual) (`:1381-1393`, matrix 6.7)
> - `docs/build-plan/11-page-layout.md` §Settings section emphasis (residual) (`:133-143`, matrix 11.12)
> - `docs/build-plan/11-page-layout.md` §Settings page layout (`:95`, MEU-58 / ST3) as locked canon
>
> **Grouping:** `.agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md`, Session 31 (`:110-115`), decisions D-1 to D-7 (`:164-176`).
> **Status:** `approved` by the independent plan review in round 2 (Codex `gpt-6.1-sol`, effort `high`, dispatched locally; verdict `approved`, 0 blocking, `intent_achieved: yes`; `.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md`, commit `31a7058`). Round 1 was `changes_required` (F1–F4, all closed in round 2). Loop `s31-plan-2026-10-10-gui-polish-residuals`: 2 of 3 rounds used; tokens 18,210,635 of 19,500,000 after a +9,000,000 `continue` authorized by Mat (recorded `--by Mat` at 2026-10-10T21:21:08-04:00). The one Low non-blocking round 2 finding, F5, is resolved in §Round 2 Correction Notes. Execution was authorized by Mat on 2026-10-11 ([human-gate-decision.md](human-gate-decision.md) §Execution authorization).

## Goal

Mat's 2026-09-30 walkthrough found two problems in the app chrome:

- **Header.** `Console` and `Settings: Ctrl+K` read as plain text. `Console` shows no pressed state while its panel is open. The palette control is labelled Settings, but it opens the command palette.
- **Settings page.** The section the rail marks as current has no emphasis of its own on the right. Session 27's local repro R4 then showed the rail itself stops following scroll at Convert on a large screen: Capture through MCP access never become current while you scroll (`2026-09-30-tts-repair/walkthrough.md:29`).

This session fixes both.

- **MEU-69 `gui-header-toggle-state`** (UI only):
  - `header-console-btn` becomes an `aria-pressed` toggle with a terminal icon. Its label stays constant, and a tinted background shows the pressed state.
  - `header-palette-btn` reads **Commands**, with a command icon and the `Ctrl+K` hint.
  - Both render as outlined buttons, so they read as buttons.
- **MEU-70 `gui-settings-section-emphasis`** (UI only):
  - **The rail fix comes first (spec "Verify first" row, ST3).** A bottom spacer lets every section scroll up into the rail's top band, and the rail re-checks its current entry on scroll (D-9, user-chosen). Each section then becomes current in order while you scroll, on any window height.
  - **Then the emphasis.** The current section card gets `data-current="true"`, a subtle raised background and an accent left border. The state comes from the rail's own active entry, so the two never disagree, and nothing moves when the emphasis changes.

Order: MEU-69 first, then MEU-70 (matrix 6.7 → 11.12; grouping `:111`). The two MEUs share no file. Both touch the global chrome and the Settings page that the same Electron waves cover.

Neither MEU touches Python, REST, MCP, settings persistence or OpenAPI (`PRODUCT_SCOPE`). Planning started from `477579d` (the Session 29 closeout, on `claude/vigilant-volta-f04tvs`). Row 0 records the branch HEAD at execution start in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent (ls: No such file or directory, 2026-10-10); no headroom on PATH (`which headroom` empty). Scope is four TSX renderer files plus tests, where .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). The `prereq` check refuses if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the claude.ai/code container:
  - `native_shell: bash`; no `rtk`, no `pwsh`, no Codex CLI;
  - `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; `.agent/docs/harness-profiles.md`);
  - `fresh_worker` is the Agent tool with `.claude/agents/`, and rows keep `compact_continue` as the fallback.
- **Reviewer:** Codex CLI (`avkit_independent_reviewer`, vendor OpenAI), model `gpt-6.1-sol`, effort `high`. A local agent on Mat's machine dispatches it through `tools/Invoke-CodexDispatch.ps1`, with the prompt this plan ships ([human-review-decision.md](human-review-decision.md)). It is vendor-distinct from the author (Anthropic). Caps: plan 3 rounds, execution 6 (PROFILE B5).
- **Gate location:** the Sessions 25–29 split ([human-gate-decision.md](human-gate-decision.md) A-1).
  - The container pre-gate is non-authoritative.
  - `WINDOWS_GATE` and the `CHROME_LOOK` checklist run on Mat's machine and are authoritative.
  - Container commands call tools raw, which is the unfiltered equivalent of `rtk proxy`. `validate-task.ps1` runs every stage through `rtk proxy`.
- **Receipts:** `$RECEIPTS_DIR` in the container (default `/tmp/av-kit`), `C:/Temp/av-kit/` on Windows.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-69` | `.agent/context/handoffs/2026-10-10-gui-polish-residuals-MEU-69-handoff.md` |
| `MEU-70` | `.agent/context/handoffs/2026-10-10-gui-polish-residuals-MEU-70-handoff.md` |

Rolling reviews:
- plan: `.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md`
- execution: `.agent/context/handoffs/2026-10-10-gui-polish-residuals-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census (task rows 0–1) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha` |
| WP-1 | MEU-69 TDD and handoff (rows 2–4) | WP-0 | `compact_continue` | MEU-69 handoff; compact, then re-read `task.md` and the handoff |
| WP-2 | MEU-70 TDD and handoff (rows 5–8) | WP-1 | `compact_continue` | MEU-70 handoff; compact, then re-read |
| WP-3 | Hub reconciliation (row 9) | WP-2 | `shared` | `docs/build-plan/06-gui.md`, `11-page-layout.md` |
| WP-4 | H1 closeout, `WINDOWS_GATE` + `CHROME_LOOK`, execution review, H2 | WP-3 | `compact_continue` | handoffs, gate result JSON, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> These items are for the plan-review loop and for the user's execution message. They are not a pause point before review.
>
> 1. **Execution authorization** (`plan_to_exec_gate: human`). After the reviewer approves, execution starts only on a direct user message. It is recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization.
> 2. **Two test amendments, TA-1 and TA-2.** Two existing assertions pin the old label: `chrome-zorivest.test.ts:180` and `app-shell-wiring.test.ts:84` both expect `/Settings:/` in the palette button. The Spec rule (06:1390, Human-approved 2026-09-30; grouping D-7) changes that label to **Commands**, so those expectations are now wrong. AGENTS §Testing & TDD allows such a correction only with a source-backed amendment plus independent review or explicit human authorization. Both amendments are therefore listed in `TEST_AMENDMENTS` for the plan reviewer to judge. They apply only if the review approves them and the execution message does not veto them (Stop condition S8). Nothing else changes in those tests.
> 3. **Decisions D-10 to D-21** (§Decision Log) are resolved autonomously and logged. The user may veto any of them in the execution message. The ones most likely to matter to you:
>    - D-11: Console pressed = `secondary` (tinted) variant, unpressed = `outline`. A transparent 1 px border keeps the width identical.
>    - D-12: the palette button's accessible name is "Commands", with `aria-keyshortcuts="Control+K"`.
>    - D-14: the section emphasis is a raised `bg-bg-elevated/40` background plus a 2 px accent left border. Every section carries the same padding and border all the time, so the emphasis never moves content.
> 4. **Section frames grow by 16 px each.** `SECTION_EMPHASIS` gives every frame 8 px of padding top and bottom, always, so that the emphasis has room without moving anything when it changes. The page is therefore a little longer than today (`BOX_SEPARATION` explains why the padding cannot be cancelled vertically).
> 5. **D-9 (user-chosen 2026-10-10): the bottom spacer.** The empty space it adds sits below MCP access, and only at the end of the page. On your large screen the page then scrolls further than today, by up to one screen minus the last section's height. That is how every section can reach the top.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the "Files Modified" rows below, all under `ui/`. `packages/`, `mcp-server/`, `openapi.committed.json`, `tools/` and `ui/src/main/` stay byte-identical to `baseline.sha`. `validate-task.sh api-scope` proves this. | Spec 06:1381-1393, 11:133-143 (GUI-only rules); grouping `:111` |
| `CONSOLE_TOGGLE` | `header-console-btn` is `<Button size="sm">` with `aria-pressed={consoleOpen ? 'true' : 'false'}`. Its children are a lucide `SquareTerminal` icon (`size={14}`, `aria-hidden="true"`) and the constant text `Console`, so its accessible name is always exactly "Console". **Unpressed:** `variant="outline"`. **Pressed:** `variant="secondary"` plus `className="border border-transparent"`, so the box keeps the outline variant's 1 px border width (D-11). `consoleOpen` is the `AppShell` state `usePersistedState('ui.panel.console.visible')` (`AppShell.tsx:43`), passed to `Header` as a new required prop `consoleOpen: boolean`. The click handler is unchanged (it dispatches `TOGGLE_CONSOLE_EVENT`). | Spec 06:1389; D-11, D-13 |
| `PALETTE_BUTTON` | `header-palette-btn` is `<Button variant="outline" size="sm">` with `aria-label="Commands"`, `aria-keyshortcuts="Control+K"` and `title="Open the command palette (Ctrl+K)"`. Its children are a lucide `Command` icon (`size={14}`, `aria-hidden="true"`), the text `Commands`, and `<kbd className="text-xs text-fg-muted">Ctrl+K</kbd>`. The click handler is unchanged (it dispatches `OPEN_PALETTE_EVENT`). It stays the next sibling of `header-console-btn` (AC-26.5). | Spec 06:1390; D-12, D-13 |
| `HEADER_ICONS` | `SquareTerminal`, `Command`. Both exist in the locked `lucide-react@0.400.0` (`ui/package-lock.json:7440-7442`). Checked against that tarball's `dist/lucide-react.d.ts` at plan time (2026-10-10); `validate-task.sh prereq` re-checks the installed package. | D-13 |
| `CONSOLE_PRESSED_INVARIANT` | At every observable moment, `header-console-btn`'s `aria-pressed` is `"true"` exactly when `console-panel` is mounted. Every path that opens or closes the panel keeps it: the header button, `console-close`, Escape (`AppShell.tsx:70`), the palette's toggle command (`TOGGLE_CONSOLE_EVENT`) and a persisted-open launch. | Spec 06:1389, 06:1392 |
| `TAIL_SPACER` | One `div data-testid="settings-tail-spacer" aria-hidden="true"`, rendered as the last child of the Settings content column, after the last section. Its inline `height` is `tailSpacerHeight(...)` px. It is measured by `useTailSpacer(pageRef, lastKey)` in `features/settings/settings-tail-spacer.ts` (new). The hook measures on mount, whenever a `ResizeObserver` reports a change in the scroller (`main`) or in any section frame, and on `window` `resize`. It never observes the spacer or the column that contains it, and it applies each new height inside one `requestAnimationFrame`, so a height change cannot re-trigger its own observer in the same frame (no ResizeObserver loop error). It unsubscribes and cancels a pending frame on unmount. With no `ResizeObserver` (jsdom), the height stays `0`. | Human-approved D-9; Local Canon ST3 |
| `TAIL_SPACER_HEIGHT` | Pure `tailSpacerHeight({ clientHeight, belowLastTop, margin }): number` in `settings-tail-spacer.ts` returns `Math.max(0, Math.ceil(clientHeight - margin - belowLastTop))`. `clientHeight` is the scroller's `clientHeight`. `belowLastTop` is the content height from the last section's top to the end of the scroll content, **excluding** the spacer's current height: `scroller.scrollHeight - spacerHeight - (last.getBoundingClientRect().top - scroller.getBoundingClientRect().top + scroller.scrollTop)`. `margin` is `SECTION_SCROLL_MARGIN`. Any non-finite or negative input returns `0` (fail closed: no spacer, today's layout). Subtracting the current spacer height makes the measurement a fixpoint, so re-measuring after the spacer has grown gives the same value. | D-16 |
| `SECTION_SCROLL_MARGIN` | `16` px: the `scroll-mt-4` on every section frame (`SettingsPage.tsx:106`), which `revealSection` honours via `scrollIntoView({block: 'start'})`. Exported from `settings-tail-spacer.ts`. AC-70.4 asserts that every rendered section frame (`[data-settings-section]`, whichever component produces it) carries `scroll-mt-4`, so the two cannot drift apart (Review R2 F5). | Local Canon `SettingsPage.tsx:106`, `StartAtSignInControl.tsx:83`, `SettingsRail.tsx:43-64` |
| `TRAIL_REACH` | At `DEFAULT_WINDOW` and at `TALL_WINDOW`, after `WINDOW_SETTLED` and readiness load, for each visible section in DOM order: `scrollIntoView({block: 'start', behavior: 'instant'})` on that section, then wait (Playwright auto-retry, ≤ 5 s) until its `settings-rail-<key>` entry has `aria-current="location"` and exactly one `[aria-current="location"]` exists. Then, with `main` scrolled to its maximum: the last visible section's rail entry is current, and that section's top is within `[0, SECTION_SCROLL_MARGIN + 1]` px of `main`'s top. | Spec 11:141 ("follows scroll"); D-9 |
| `TALL_WINDOW` | `BrowserWindow.setSize(1280, 1000)`, the tallest size inside the container's xvfb screen (1280×1024). The setSize pattern is `settings.test.ts:292-294`. It stands in for Mat's large screen. `CHROME_LOOK` K4 re-checks on the real one. | Local Canon `settings.test.ts:292`; R4 |
| `DEFAULT_WINDOW` | 1280 × 800 (`ui/src/main/index.ts:138`), with a fresh `AVKIT_APP_DATA`. Electron settles to about 1280 × 773 (`download-queue.test.ts:1109-1116`). | Local Canon |
| `WINDOW_SETTLED` | Before any geometry read, wait for two `requestAnimationFrame`s and then for `window.innerWidth`/`innerHeight` to be unchanged for 500 ms. This is the `windowSettled` helper pattern (`download-queue.test.ts:1117`), copied into `settings.test.ts` and `console-chrome.test.ts`. | Local Canon |
| `SCROLL_RECHECK` | `SettingsRail`'s observer effect also adds a passive `scroll` listener on the observer's scroller (`window` when the scroller is `null`). It is coalesced to one `requestAnimationFrame` per frame and runs the existing `current()` choice. While the click lock holds (`Date.now() < clickLockUntil.current`) it changes nothing, the same rule the observer callback follows (`SettingsRail.tsx:133-135`). It is removed in the effect's cleanup together with `observer.disconnect()`. The `current()` function itself is unchanged. | D-17; Local Canon ST3, Session 27 A-6 |
| `REVEAL_FALLBACK` | Added in execution (D-22). `revealSection` (`SettingsRail.tsx`) completes a smooth reveal with an instant `scrollIntoView` **only if its scroller emitted no `scroll` event** within `SMOOTH_SCROLL_FALLBACK_MS` (450 ms). Any scroll event means the smooth scroll started or the user took over, so the fallback stays out of the way even when the scroller is back at its start position. The scroll listener is removed when the timer fires and on cancel. The A-3 case (a dropped smooth scroll in a hidden or throttled window: no scroll event at all) still jumps. | Local Canon Session 27 A-3 / A-6; D-22 |
| `ACTIVE_SOURCE` | `SettingsRail` gains an optional prop `onActiveChange?: (key: SettingsSectionKey \| null) => void`. A `useEffect` keyed on `active` calls it after every change, including the initial value. `SettingsPage` keeps `const [currentSection, setCurrentSection] = useState<SettingsSectionKey \| null>(null)` and passes `setCurrentSection`. It hands `current={currentSection === key}` to **every** section producer: each `SettingsSectionFrame`, and `StartAtSignInControl` for `startup`, which renders its own `<section>` (`StartAtSignInControl.tsx:79-83`, mounted at `SettingsPage.tsx:934`). The rail's `active` is the **only** source of "current". `SettingsPage` runs no observer, no scroll listener and no second computation of its own. | Spec 11:142 ("driven by the same observer state the rail uses"); D-15 |
| `SECTION_EMPHASIS` | Defined once, in `features/settings/settings-section-frame.ts` (new), as `sectionFrameProps(current: boolean): { className: string; 'data-current'?: 'true' }`. Both section producers spread it on their `<section>`: `SettingsSectionFrame` (`SettingsPage.tsx:101-107`) and `StartAtSignInControl` (`:79-83`, new optional prop `current?: boolean`, default `false`). Neither restates a class. **Every** frame always carries `SECTION_FRAME_BASE`: today's `flex scroll-mt-4 flex-col gap-3 outline-none` (identical in both producers today) plus `-mx-3 pl-2.5 pr-3 py-2 rounded-[var(--radius-control)] border-l-2` and `transition-[background-color,border-color] duration-[var(--duration-fast)] ease-[var(--ease-out)]`. Horizontally, `-mx-3` (12 px) is cancelled exactly by the 2 px border plus `pl-2.5` (10 px) on the left and by `pr-3` (12 px) on the right, so content keeps today's x positions. Vertically there is **no** negative margin, so `BOX_SEPARATION` holds; each frame is 16 px taller than today, the same in every state. When `current`, the frame also carries `data-current="true"`, `bg-bg-elevated/40` and `border-accent`. Otherwise it has no `data-current` attribute and carries `border-transparent`. A section never carries `aria-current`, because AC-58.12 counts exactly one `[aria-current="location"]` on the page. | Spec 11:142; Human-approved 2026-09-30 ("background on the right panel"); Local Canon G32/G33; D-14, D-20 |
| `BOX_SEPARATION` | The vertical distance between adjacent section frames' border boxes is the column's `gap-6` (24 px), which must stay **greater than** `SECTION_SCROLL_MARGIN` (16 px). When a section is scrolled to its scroll margin, the previous frame's bottom is then 8 px above `main`'s top, outside the rail's top band, so `current()` picks the scrolled section. A negative vertical margin on the frames would shrink this distance to 8 px and leave the previous section current. | Local Canon `SettingsRail.tsx:141,152`, `SettingsPage.tsx:106,427` |
| `NO_SHIFT` | In Electron at `DEFAULT_WINDOW`, measured in **document coordinates** so that two different scroll positions are comparable: for each visible section `h2`, `docX = box.x - main.left` and `docY = box.y - main.top + main.scrollTop`, with `main`'s `getBoundingClientRect()` read in the same `evaluate`. Sample A: `main` at the top, `download-settings` is the `data-current` section. Sample B: Capture scrolled to the top and **still current** when sampled (`capture-settings` has `data-current="true"`). The spec first asserts that the two samples' current keys differ (`download` vs `capture`); if they are equal the spec fails, so it can never compare a state with itself. Then every `docX`, `docY`, `width` and `height` in B matches A within 0.5 px. Separately, the `header-console-btn` `boundingBox()` matches within 0.5 px with the console closed and open. | Spec 11:142 ("no layout shift"); D-11; Review R1 F3 |
| `EMPHASIS_TESTS` | Every test that needs `ACTIVE_SOURCE` or `SECTION_EMPHASIS`: the jsdom suite `ui/tests/unit/settings-emphasis.test.tsx` (new; AC-70.5, AC-70.9) and the Electron spec titled `AC-70.6`. They are written with the other MEU-70 tests in row 5 and must be Red there, but they are first **required green** at row 7, after the emphasis exists. The executable copy is `UNIT70E` in `validate-task.sh`. | Review R1 F1 |
| `RAIL_STAGE_TESTS` | What row 6 (`green70-rail`, the rail fix alone) must turn green: `ui/tests/unit/settings-tail-spacer.test.ts` (AC-70.1, AC-70.8), the existing `REGSET` suites including `settings-rail.test.tsx` (which then holds only AC-70.3, AC-70.4 and AC-70.10 of the new ACs) and the Electron specs `AC-70.2`, `AC-58.12` and `A-6`. It contains no member of `EMPHASIS_TESTS`. `plan_checks.py static` item 9 asserts that `settings-emphasis.test.tsx` appears in `red70`, `green70` and `gate70`, and in neither `REGSET`, `UNIT70` nor `green70-rail`. | Review R1 F1 |
| `TEST_AMENDMENTS` | **TA-1** `ui/tests/unit/chrome-zorivest.test.ts`: the AC-26.4 title becomes `'AC-26.4 header breadcrumb and Commands Ctrl+K palette trigger'`, and `:180` `expect(palette?.textContent).toMatch(/Settings:/)` becomes `expect(palette?.textContent).toMatch(/Commands/)`. **TA-2** `ui/tests/unit/app-shell-wiring.test.ts:84`: `expect(palette.textContent).toMatch(/Settings:/)` becomes `expect(palette.textContent).toMatch(/Commands/)`. Nothing else in either file changes; the `/Ctrl\+K/` assertion (`chrome-zorivest.test.ts:181`) stays. These two edits are authorized only by an independent plan approval plus an execution message that does not veto them (S8). | Spec 06:1390; grouping D-7; AGENTS §Testing & TDD |
| `NEW_TESTIDS` | Appended at the **end** of `ui/tests/e2e/test-ids.ts`, after the MEU-66 block, in one new block `// MEU-70 Settings section emphasis (additive IDs).`: `SETTINGS_TAIL_SPACER = 'settings-tail-spacer'`. The AC-51.6 prefix hash covers only the text before `// MEU-51 primitive harness IDs.` (`test-ids.ts:300`), so it stays valid. MEU-69 adds no test id. | Local Canon AC-51.6 |
| `GATED_PATHS` | The executable copy is the `gated` list in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/build-plan/06-gui.md docs/build-plan/10-queue-card-ui.md docs/build-plan/11-page-layout.md docs/build-plan/build-priority-matrix.md docs/build-plan/gui-actions-index.md docs/proposals docs/execution/plans/2026-08-28-p10-queue-card-foundations docs/execution/plans/2026-09-02-p10-queue-card-migration docs/execution/plans/2026-09-03-p10-queue-card-dnd docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md .agent/model-registry.local.json .agent/model-registry.local.yaml docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.ps1`. That is the code, plus the non-code files the gate stages read. A plan-time sweep (2026-10-10) of the repo-relative paths that `ui/tests/unit` reads found the same set as Session 29 (`2026-10-01-capture-viewport-chrome/implementation-plan.md` §`GATED_PATHS`). **Excluded, as a rule:** `.agent/context/meu-status.yaml` and `docs/BUILD_PLAN.md` are SSOT. They change only at H1-3 (before the gate) and H2-2 (after approval). cloud-local §3.4 treats those doc-only closeout edits as not reopening the gate, and H2-2 re-runs the doc-reading suites after them. | cloud-local §3.3 item 2, §3.4 |
| `COUNT_FLOORS` | Vitest total ≥ 748 and Electron expected ≥ 127, taken from the last authoritative gate: Session 29 attempt 4 (`2026-10-01-capture-viewport-chrome/windows-gate-result.json`, gate of record), Vitest 748/748, Playwright 127/0/0. In the runner's own vocabulary (reflection 2026-09-30 RULE-3): Vitest `numTotalTests` ≥ 748 with `numFailedTests` 0, and Playwright `stats.expected` ≥ 127 with `unexpected` 0 and `flaky` 0. pytest reports failed == 0, and every later attempt's passed count must be ≥ the first attempt's (`pytest_floor`, carried by the `.ps1`). The executable copies are the literals in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts they equal 748 / 127. | cloud-local §3.3 |

**Environment-bound census** (cloud-local §4). The container pre-gate tolerates only these failures. `WINDOWS_GATE` tolerates none. This is the same set as Sessions 27 and 29 (`2026-10-01-capture-viewport-chrome/implementation-plan.md:155-163`):

| Tier | Member | Signature / handling |
|---|---|---|
| Vitest | AC-51.6 `ui/tests/unit/layout-primitives.test.ts` | The CRLF prefix hash recomputes to `819760B9…` and new ids are unique (`vitest_env_ok` `crlf_proof`). `NEW_TESTIDS` lands after the marker, so the proof still holds. |
| Vitest | AC-41.3 `ui/tests/unit/queue-canon.test.ts` | `P:/zorivest` is absent and `styles.css` is unchanged since `f7d3134`. This plan does not edit `styles.css`. |
| Electron | capture-picker specs in `ui/tests/e2e/capture-picker.test.ts` | Not on Windows, the stub `.exe` is absent, and the failure is exactly the stub-missing error (`electron_env_ok`). |
| pytest | the Windows-bound tooling tests (`tests/tooling/*`) | `pytest_env_ok`: the container's failed set must be a subset of the failed set at `baseline.sha`. This session changes no Python, so any new failure is real. |
| External inputs | `P:/agentic-framework` HEAD; `P:/.agent/model-registry.json` hash | `validate-task.ps1` records both before stage 1. On attempt ≥ 2 a mismatch with the previous attempt stops before stage 1 (cloud-local §3.2). |

### MEU-69 — `gui-header-toggle-state`

#### Boundary Inventory

No new external input surface. Both controls are buttons with no user text. They keep their existing handlers (`TOGGLE_CONSOLE_EVENT`, `OPEN_PALETTE_EVENT`). The only new value is the `consoleOpen` boolean, read from existing persisted state, whose loader is unchanged (`usePersistedState`).

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| `Header` props | `HeaderProps` (TypeScript, `Header.tsx:21`) | `consoleOpen: boolean` (required), two callbacks unchanged | not applicable (an in-process prop, not external input; `tsc` rejects a missing or extra prop) |
| `ui.panel.console.visible` | unchanged: `usePersistedState` | boolean; unchanged | unchanged |

#### Acceptance Criteria

Call chain for every integration AC: `AppShell` (`consoleOpen` state, `AppShell.tsx:43`) → `Header` (`consoleOpen` prop) → `header-console-btn` `aria-pressed` and variant. The palette button → `OPEN_PALETTE_EVENT` → `CommandPalette` (`AppShell.tsx:188`). The Electron cases run against the built app (`out/main/index.js`).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-69.1 | unit | jsdom, `Header` rendered alone (`header-toggles.test.ts`, new): with `consoleOpen={false}`, `header-console-btn` has `aria-pressed="false"` and class `btn-outline`. With `consoleOpen={true}`, it has `aria-pressed="true"`, classes `btn-secondary` and `border-transparent`. In both, the accessible name is exactly "Console" (`getByRole('button', {name: 'Console', exact: true})` resolves this element), there is one `svg` with `aria-hidden="true"`, and the class has `h-7` (`CONSOLE_TOGGLE`). | Spec 06:1389; D-11, D-13 | A rerender with `consoleOpen={true}` whose name is not "Console" (for example "Close console") fails. A button with no `aria-pressed` attribute in either state fails. `btn-ghost` in either state fails. |
| AC-69.2 | integration | jsdom, `AppShell` rendered with the `chrome-zorivest.test.ts` setup (copied into `header-toggles.test.ts`): `CONSOLE_PRESSED_INVARIANT` holds after each step of this sequence. Launch closed → header click (open) → `console-close` → header click → Escape → `window.dispatchEvent(new CustomEvent(TOGGLE_CONSOLE_EVENT))` (the palette command's path) → the same event again. Separately, a launch with `ui.panel.console.visible` persisted `true` starts with the panel mounted and `aria-pressed="true"`. | Spec 06:1389, 06:1392 | After each step, a state where `console-panel` is mounted and `aria-pressed` is `"false"`, or the reverse, fails. That check runs after every step, not only at the end. |
| AC-69.3 | integration | jsdom, keyboard and mouse twins (RULE-1, reflection 2026-10-01). Focus `header-console-btn`, then `{Enter}`: the panel opens and `document.activeElement` is still the button. Then `{ }` (Space): the panel closes and focus stays on the button. Mouse twin: `user.click` the button: the panel opens, `document.activeElement` is the button, and Escape then closes the panel with `aria-pressed="false"`. | Spec 06:1389 ("Enter/Space toggle; focus stays on the button"); RULE-1 | Focus that moves into `console-panel` (or to `body`) after either activation fails. A Space that scrolls the page instead of toggling fails. |
| AC-69.4 | integration | jsdom: `PALETTE_BUTTON`. `getByRole('button', {name: 'Commands', exact: true})` resolves `header-palette-btn`. Its `textContent` contains "Commands" and "Ctrl+K". It has `aria-keyshortcuts="Control+K"`, one `aria-hidden` svg, class `btn-outline` and `h-7`. Clicking it opens the command palette (the palette's `Settings` command is then reachable, as `app-shell-wiring.test.ts:85-88` does). Ctrl+K still opens the palette. | Spec 06:1390; D-12 | `textContent` matching `/Settings/` fails. `getByRole('button', {name: 'Open command palette'})` resolving anything fails. `header-palette-btn` stops being the next sibling of `header-console-btn` (AC-26.5) → fail. |
| AC-69.5 | integration | Electron (`console-chrome.test.ts`, append only; title contains `AC-69.5`), built app at `DEFAULT_WINDOW`. At launch `header-console-btn` has `aria-pressed="false"`. Click: `console-panel` is visible and `aria-pressed="true"`. Escape: `console-panel` count is 0 and `aria-pressed="false"`. The `NO_SHIFT` header check holds. The palette button's visible text contains "Commands" and clicking it opens the palette. The spec's **first** assertion is the `aria-pressed="false"` check, so on the pre-change header it fails on that assertion and not on a missing element. | Spec 06:1392 ("Playwright asserts `aria-pressed` flips with the panel") | **Red on the pre-change header:** `red69` runs `require_failed_title AC-69.5 toHaveAttribute`. A width difference > 0.5 px between closed and open fails. The existing C1-1 to C1-5 specs pass unchanged. |
| AC-69.6 | unit | `TEST_AMENDMENTS` TA-1 and TA-2 are applied exactly as defined, and nothing else in `chrome-zorivest.test.ts` or `app-shell-wiring.test.ts` changes. `validate-task.sh ta-check` diffs both files against `baseline.sha` and allows only the three lines TA-1/TA-2 name. | AGENTS §Testing & TDD | Any other changed line in those two files fails `ta-check`. An amendment applied before the plan approval and execution message are recorded fails `prereq` (it checks the tree at row 0). |

**Test-ID migration (MEU-69).**

| Existing ID | Migration | Detail |
|---|---|---|
| `header-console-btn` | change | `CONSOLE_TOGGLE` (icon, `aria-pressed`, outline/secondary); id, handler and position unchanged |
| `header-palette-btn` | change | `PALETTE_BUTTON` (Commands, icon, kbd hint, accessible name); id, handler and position unchanged |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Console as a toggle with `aria-pressed` and a constant label | Research-backed | 06:1389 ([WAI-ARIA APG button](https://www.w3.org/WAI/ARIA/apg/patterns/button/): a toggle button keeps its label and changes `aria-pressed`) |
| Pressed visual and button affordance | Local Canon | 06:1391 (shared `Button`, G32/G34, no new component); D-11 (`toolVariant` precedent) |
| Icons | Local Canon | lucide-react, as the nav rail and Capture toolbar use (`NavRail.tsx:1`, 09:619); D-13 |
| Palette label and accessible name | Spec + Research-backed | 06:1390; D-12 (WCAG 2.5.3 Label in Name; WAI-ARIA `aria-keyshortcuts`) |
| Focus after activation | Spec | 06:1389 ("focus stays on the button"); RULE-1 twin |
| Feedback tier (G35) | Local Canon | Console toggle and palette open: T0 (immediate visual state change: `aria-pressed` + panel / palette mount) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/layout/Header.tsx` | modify | `CONSOLE_TOGGLE`, `PALETTE_BUTTON`; new `consoleOpen` prop |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | passes `consoleOpen` to `Header` (`:256`) |
| `ui/tests/unit/header-toggles.test.ts` | new | AC-69.1 – AC-69.4 |
| `ui/tests/unit/chrome-zorivest.test.ts` | modify (TA-1 only) | AC-26.4 title and `:180` |
| `ui/tests/unit/app-shell-wiring.test.ts` | modify (TA-2 only) | `:84` |
| `ui/tests/e2e/console-chrome.test.ts` | modify (append only + `windowSettled`) | AC-69.5 |

### MEU-70 — `gui-settings-section-emphasis`

#### Boundary Inventory

No new external input surface. The spacer and the emphasis read only DOM geometry and the rail's own state. No setting, payload or IPC changes, and no settings value is read or written by the new code.

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| DOM geometry read by `useTailSpacer` | `tailSpacerHeight` (`TAIL_SPACER_HEIGHT`) | finite, ≥ 0; anything else → `0` (fail closed) | not applicable (no external payload) |
| `SettingsRail` props | TypeScript props (`SettingsRail.tsx:5-12`) | `onActiveChange` optional; existing props unchanged | not applicable |
| `StartAtSignInControl` props | TypeScript props (`StartAtSignInControl.tsx:28-31`) | `current?: boolean` (default `false`); `onAvailabilityChange` unchanged | not applicable |

#### Acceptance Criteria

Call chain for every integration AC: route `#/settings` → `SettingsPage` (`pageRef`) → `SettingsRail` (IntersectionObserver + `SCROLL_RECHECK` → `active` → `onActiveChange`) → `SettingsPage` `currentSection` → `SettingsSectionFrame current` or, for `startup`, `StartAtSignInControl current` → `sectionFrameProps` (`SECTION_EMPHASIS`). The spacer runs `SettingsPage` → `useTailSpacer` → `settings-tail-spacer` height. The Electron cases run against the built app with the `settings.test.ts` seam (`installSettingsSeam`).

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-70.1 | unit | `settings-tail-spacer.test.ts` (new): `tailSpacerHeight` per `TAIL_SPACER_HEIGHT`. `{clientHeight: 700, belowLastTop: 300, margin: 16}` → `384`. `{700, 900, 16}` → `0`. `{700, 683.5, 16}` → `1` (`Math.ceil`). It is idempotent in the sense the contract states: the same measurement with the spacer included and then subtracted gives the same height. `SECTION_SCROLL_MARGIN === 16`. | D-16 | `NaN`, `Infinity`, `-1` in any field → `0`. A result that is negative or non-integer fails. |
| AC-70.2 | integration | Electron (`settings.test.ts`, append only): `TRAIL_REACH` as **two independent specs**, `AC-70.2 DEFAULT_WINDOW` and `AC-70.2 TALL_WINDOW`, so a failure at the first size never hides the second (Review R1 Q2). Each attaches a diagnostics record (`test.info().attach`): `window.innerWidth/innerHeight`, `main.clientHeight/scrollHeight/scrollTop`, and per section its top after its own scroll and the rail's current key. Before the spacer and `SCROLL_RECHECK` exist, the trailing sections fail this spec on their `aria-current` assertion (R4). | Spec 11:141; Human-approved D-9; RULE-2 (surface size against the container) | **Red on the pre-change page:** `red70` runs `require_failed_title AC-70.2 toHaveAttribute`. If it does not go Red at either window size, Stop condition S4 applies. Any section whose entry does not become current after its own scroll fails, and so do two current entries. A last section whose top cannot reach `SECTION_SCROLL_MARGIN + 1` px of `main`'s top fails. |
| AC-70.3 | integration | jsdom (`settings-rail.test.tsx`, append only): `SCROLL_RECHECK`. A fake `IntersectionObserver` never calls back. The test stubs `main`'s `scrollHeight`/`clientHeight`/`scrollTop` at the bottom and the sections' `getBoundingClientRect` so that only the last section's top is on screen. Dispatching `scroll` on `main` (then one animation frame) makes `settings-rail-mcp` current. During a click lock on `settings-rail-tts`, the same scroll leaves `tts` current until the lock is released. After unmount, a `scroll` event changes nothing and throws nothing (the listener is removed). | D-17; Local Canon ST3, A-6 | A bottom scroll that leaves an earlier entry current fails. A scroll during the lock that changes the clicked entry fails. A listener still attached after unmount (counted with a spy on `addEventListener`/`removeEventListener`) fails. |
| AC-70.4 | integration | jsdom (`settings-rail.test.tsx`, append only): `TAIL_SPACER`. `settings-tail-spacer` is the last child of the content column, after `mcp-access-card`, with `aria-hidden="true"`. With no `ResizeObserver` its height is `0px`. With a stubbed `ResizeObserver` and stubbed metrics, its height equals `tailSpacerHeight(...)` of those metrics, and it is re-measured when the stub fires. Every rendered `[data-settings-section]` frame's class list contains `scroll-mt-4` (`SECTION_SCROLL_MARGIN`'s producer; Review R2 F5). | D-9, D-16 | A spacer with a non-zero height when `belowLastTop ≥ clientHeight - margin` fails. A spacer placed before the last section fails. A rendered section frame without `scroll-mt-4` fails. |
| AC-70.5 | integration | jsdom (`settings-emphasis.test.tsx`, new; a member of `EMPHASIS_TESTS`): `ACTIVE_SOURCE` and `SECTION_EMPHASIS`. Exactly one section has `data-current="true"`, and its `data-settings-section` key equals the key of the rail entry with `aria-current="location"`. That holds after the initial render, after a rail click (`settings-rail-capture`), after keyboard activation (Enter on `settings-rail-transcript`) and after a fake observer callback marking `mcp` visible. The current section has `bg-bg-elevated/40` and `border-accent`. Every other section has `border-transparent` and no `bg-bg-elevated/40`. All sections carry every `SECTION_FRAME_BASE` token, none has a negative vertical margin class (`-my-*`, `-mt-*`, `-mb-*`), and none has `aria-current`. | Spec 11:142; D-14, D-15 | Zero or two `data-current` sections fail. A `data-current` section that differs from the rail's current entry fails. `[aria-current="location"]` count ≠ 1 fails. A section class containing `transition-all` or a raw hex fails. |
| AC-70.6 | integration | Electron (`settings.test.ts`, append only; title contains `AC-70.6`; a member of `EMPHASIS_TESTS`), at `DEFAULT_WINDOW`: `NO_SHIFT` for the section `h2` boxes. In sample B (Capture scrolled to the top), `capture-settings` has `data-current="true"` and is the only section with it. Its computed `background-color` differs from `download-settings`'s, and its computed `border-left-color` differs from `transparent`. | Spec 11:142; D-14; Review R1 F3 | Samples A and B with the same current key fail (no self-comparison). An `h2` whose document-relative box moved by > 0.5 px on any axis between A and B fails. A `data-current` section that does not match the rail's current entry fails. `BOX_SEPARATION`: any two adjacent visible frames whose border boxes are ≤ 16 px apart fail. |
| AC-70.7 | integration | Regression: the existing MEU-58 / A-6 / MEU-61 / MEU-62 Settings specs pass **unchanged** (`TEST_AMENDMENTS` has no MEU-70 entry). That covers `settings-rail.test.tsx`, `settings-page.test.ts`, `settings.test.ts` W4-1 to W4-3, both AC-58.12 specs, AC-61.17, AC-62.15 and the A-6 slow-scroll spec. The spacer also leaves a rail click on MCP landing MCP at the top. | Local Canon ST3, A-6 | Any of those specs failing fails the MEU gate. Changing one of them is Stop condition S5. |
| AC-70.8 | unit | `settings-tail-spacer.test.ts`: `NEW_TESTIDS` (MEU-70 block) is registered at the end of `test-ids.ts`, and the source uses the id literally. | Local Canon AC-51.6 | The AC-51.6 prefix-hash test stays green in `vitest_env_ok`. A duplicate of a prior value fails it. |
| AC-70.9 | integration | jsdom (`settings-emphasis.test.tsx`; a member of `EMPHASIS_TESTS`), with the supported login-item fixture (`loginItemGet` → `{supported: true, …}`, as `settings-rail.test.tsx:218-227` does): activating `settings-rail-startup` makes `start-at-sign-in-panel` the only section with `data-current="true"`, equal to the rail's `aria-current` key. Its class token set equals the class token set of another current frame (activate `settings-rail-appearance` and compare), and with Appearance current, Startup's tokens equal every other non-current frame's. Activating another entry clears Startup's `data-current`. `StartAtSignInControl` still renders no panel when unsupported (AC-61.x unchanged). | Spec 11:142; D-20; Review R1 F2 | With Startup the rail's current key, zero `data-current` sections fails. A Startup token set that differs from the page frames' in the same state (any missing `SECTION_FRAME_BASE` token, or a state token on the wrong side) fails. `data-current` on Startup while another key is current fails. |
| AC-70.10 | integration | Added in execution (D-22). jsdom (`settings-rail.test.tsx`, append only + `revealSection` import): `REVEAL_FALLBACK`. A smooth reveal whose scroller emits a `scroll` event and is then back at its start is not completed by the fallback (one `scrollIntoView` call); a smooth reveal with no scroll event is still completed as a jump (`smooth`, then `auto`). The existing Electron AC-58.12 spec (click MCP, then scroll to the top: Download current) is the end-to-end regression and passes **unchanged**. | Local Canon A-3; D-22; AC-58.12 | A fallback jump after a scroll event fails. Losing the A-3 jump when no scroll event arrives fails. |

**Test-ID migration (MEU-70).** Spec 11:143 says "All nine section ids and rail ids keep". The live set is `SETTINGS_SECTION_SET`: eleven keys, with `startup` mounted only when the login item is supported (`settings-sections.ts:33-46`). D-18 applies the keep rule to all eleven, and row 9 corrects the count in the canon.

| Existing ID | Migration | Detail |
|---|---|---|
| every `SETTINGS_SECTION_SET` `testId` (11) | keep | the frame gains `SECTION_EMPHASIS` classes and `data-current` (Startup's through `StartAtSignInControl`); id, `data-settings-section`, `tabIndex` and `scroll-mt-4` unchanged |
| every `settings-rail-<key>` and `settings-rail-dot-<key>` | keep | unchanged markup; `aria-current` logic unchanged apart from `SCROLL_RECHECK` |
| new: `settings-tail-spacer` | add | MEU-70 block |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Rail follows scroll for trailing sections | Spec + Human-approved | 11:141 ("verify first … fixed under ST3"); R4 shows it does not; D-9 (bottom spacer + re-check on scroll, user-chosen 2026-10-10) |
| Spacer size | Research-backed + Local Canon | D-16; `SECTION_SCROLL_MARGIN` = `scroll-mt-4` |
| Re-check on scroll | Research-backed | D-17 (bottom-of-page fallback, as docs TOCs do) |
| Emphasis look | Human-approved + Local Canon | 11:142; G32 tokens (`bg-bg-elevated`, `border-accent`), G33 motion tokens; D-14 |
| Emphasis state source | Spec | 11:142 ("same observer state the rail uses"); D-15 |
| Emphasis for the separately rendered Startup section | Spec + Local Canon | 11:142 ("the current section card"; every section); `StartAtSignInControl.tsx:79-83`; D-20 |
| No layout shift | Spec | 11:142; `NO_SHIFT` |
| Which ids keep | Spec + Local Canon | 11:143, `SETTINGS_SECTION_SET`; D-18 |
| Feedback tier (G35) | Local Canon | rail click / scroll → emphasis: T0 (immediate visual state) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/settings/settings-tail-spacer.ts` | new | `tailSpacerHeight`, `SECTION_SCROLL_MARGIN`, `useTailSpacer` |
| `ui/src/renderer/src/features/settings/SettingsRail.tsx` | modify | `SCROLL_RECHECK`; `onActiveChange` (`ACTIVE_SOURCE`); `REVEAL_FALLBACK` (D-22); group heading band (A-3) |
| `ui/src/renderer/src/features/settings/settings-section-frame.ts` | new | `sectionFrameProps`, `SECTION_FRAME_BASE` (`SECTION_EMPHASIS`, defined once) |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | `currentSection` state; `SettingsSectionFrame` and `StartAtSignInControl` get `current`; `TAIL_SPACER` |
| `ui/src/renderer/src/features/settings/StartAtSignInControl.tsx` | modify | optional `current` prop; its `<section>` spreads `sectionFrameProps(current)` |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-70 block (`NEW_TESTIDS`) |
| `ui/tests/unit/settings-tail-spacer.test.ts` | new | AC-70.1, AC-70.8 |
| `ui/tests/unit/settings-rail.test.tsx` | modify (append only + `revealSection` import) | AC-70.3, AC-70.4, AC-70.10; A-3 heading case |
| `ui/tests/unit/settings-emphasis.test.tsx` | new | AC-70.5, AC-70.9 (`EMPHASIS_TESTS`) |
| `ui/tests/e2e/settings.test.ts` | modify (append only + `windowSettled`) | AC-70.2, AC-70.6 |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Restyling other header elements (breadcrumb, brand mark) or the nav rail | out-of-scope | — | 06:1387-1392 scope the rules to `header-console-btn` and `header-palette-btn` |
| A global keyboard shortcut to toggle the console | out-of-scope | — | 06:1389 lists Enter/Space on the button only; the palette command already toggles it (`gui-actions-index.md:102`) |
| Renaming or regrouping Settings sections, or a different rail layout | out-of-scope | — | 11:143 ("All … section ids and rail ids keep"); 11:95 (MEU-58 composition) |
| Proportional "progress mapping" of trailing sections, or a bottom-only fallback without the spacer | out-of-scope | — | Human-approved D-9 (the user chose the bottom spacer over both, 2026-10-10) |
| Capture flatten-with-backup and its Settings field | deferred | MEU-67 | Session 30 (grouping `:103-108`). Any Settings field it adds lands inside an existing section frame and inherits `SECTION_EMPHASIS` |
| Editing the locked Phase 11 ST rows or the Settings mockup in `docs/proposals/` | out-of-scope | — | `layout-canon.test.ts` AC-50.1/50.4 lock them to MEU-5x owners and the mockup text. Row 9 edits only the residual section (`11:133-143`) |
| The open TECH-DEBT rows `E2E-ELECTRON-LAUNCH-FLAG` and `TOOLING-SHARED-REGISTRY-COUPLING` | out-of-scope | — | grouping D-5 (`:172`): not MEUs in this batch |

## BUILD_PLAN.md Audit

The D3 hub is `docs/BUILD_PLAN.md` + `docs/build-plan/`. Task row 9 makes these edits, with exact validation (`validate-task.sh hub`):

1. `06-gui.md`:
   - §ConsolePanel (`:334`): "Header **Console** (left of **Settings: Ctrl+K**)" becomes "Header **Console** (left of **Commands Ctrl+K**)". This is hub drift the project creates.
   - §Header toggles (residual): one row each for the pressed variant rule (tagged "Session 31 plan D-11") and the accessible name (tagged "Session 31 plan D-12"). Plan D-ids collide across plans, so the canon always names the plan (Session 29 Review R1 F5g).
2. `11-page-layout.md` §Settings section emphasis (residual) (`:133-143`):
   - The "Test IDs" row's "All nine section ids" becomes "All `SETTINGS_SECTION_SET` section ids (eleven; `startup` only when supported)" (D-18).
   - One row for the trailing-section rail fix: the bottom spacer plus the re-check on scroll, tagged "Human-approved 2026-10-10; Session 31 plan D-9, D-17".
   - One row for the emphasis classes, tagged "Session 31 plan D-14".
   - The ST decision rows (`:47-51`, ST1–ST5) and the mockup inventory are **not** edited (AC-50.1/50.4 lock). Row 9 re-runs `layout-canon.test.ts`.
3. `gui-actions-index.md`: no change. `palette:open` (`:16`) and `console:toggle` (`:102`) already describe the actions, and neither label changes. Row 9 re-runs `gui-actions-audit.test.ts` to prove it.
4. `docs/BUILD_PLAN.md`: the AUTOGEN status regions are re-rendered by `tools/meu_status.py render` (H1-3 / H2-2) and checked with `render --check`.

## Verification Plan

Every command is registered in `validate-task.sh` (container) and `validate-task.ps1` (Windows), from one stage list. The stage ids match exactly (`windows-gate-check` asserts the order).

### 0. Plan-local static verifier (planning time; re-run in `pregate`)

`python3 docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static` is stdlib-only and read-only, and runs no product code (GUARDRAILS SIGN 1 carve-out). It checks:

- the task table's structure and its dependency graph;
- that every `validate-task.sh` check invoked from `task.md` exists;
- that the `.sh` `windows-gate-check` order equals the `.ps1` stage ids;
- that `AUDIT_SRC` and the audit pattern are identical in both scripts;
- that `GATED_PATHS` and `COUNT_FLOORS` equal their executable copies;
- that every `D-n` and `AC-69.n`/`AC-70.n` named in `task.md` has a definition site (an AC table row, a `decision_log` id, a `### D-n` heading, or a grouping §8 row), not merely a prose mention;
- that every file named in a Files Modified table is either present at plan time (`modify`) or absent (`new`);
- that the review prompt quotes the ledger goal anchor;
- that `EMPHASIS_TESTS` stays out of the rail stage (`RAIL_STAGE_TESTS`) and inside `red70`, `green70` and `gate70`.

Its negative case: `plan_checks.py selftest` corrupts an in-memory copy (a duplicate row id, an unknown `validate-task.sh` check, a swapped stage, an undefined `AC-70.99`, a changed floor, a missing goal anchor, a missing `modify` target, the emphasis suite added to the rail stage) and requires every one to be reported. Planning receipts are recorded in §Planning receipts below.

### 1. Prerequisites and baseline (row 0)

`validate-task.sh prereq`, then `electron-setup` and `baseline`. `baseline` writes `baseline.sha` (HEAD before any product edit) and collects the baseline pytest failed set and the Vitest and Electron receipts.

### 2. Red (per MEU)

- `red69`:
  - Vitest assertion Red (`AC-69`; the new `header-toggles.test.ts` fails on assertions, because `Header.tsx` exists and only its output changes);
  - then the Electron Red after a fresh build;
  - then `require_failed_title … AC-69.5 toHaveAttribute`.
- `red70`:
  - Vitest assertion Red (`AC-70`, including `EMPHASIS_TESTS`; the new `settings-tail-spacer.test.ts` may fail only with a missing-module message, while `settings-emphasis.test.tsx` imports only existing modules and fails on assertions);
  - then the Electron Red after a fresh build;
  - then `require_failed_title … AC-70.2 toHaveAttribute`.

### 3. Targeted Green (after each production edit)

`green69`, `green70-rail` (`RAIL_STAGE_TESTS`, row 6) and `green70` (adds `EMPHASIS_TESTS`, row 7) run the targeted suites plus the regression neighbours named in `validate-task.sh` (`REGHDR`: `chrome-zorivest`, `app-shell-wiring`, `console-polish`, `capture-page`, `convert-page`, `persist-ui`; `REGSET`: `settings-page`, `settings-rail`, `help-card`, `layout-primitives`, `layout-canon`, `gui-actions-audit`, `e2e-wiring`).

### 4. Targeted MEU gates (rows 4 and 8)

`gate69` / `gate70`:

- UI typecheck, lint, Vitest (`REGHDR` + `REGSET` + targeted) and build;
- under Electron: `console-chrome.test.ts` and `command-palette-nav.spec.ts` (MEU-69), `settings.test.ts` (MEU-70);
- `--repeat-each=20` over the specs named by `REPEAT_GREP` (defined once in `validate-task.sh`) into `$RECEIPTS_DIR/s31-repeat-*`. These are the touched and scroll-driven specs (cloud-local §3.1 item 2).

### 5. Product-scope proof (H1-4)

`validate-task.sh api-scope` proves `PRODUCT_SCOPE`:

- `git diff --name-only $(cat baseline.sha) -- packages mcp-server openapi.committed.json tools ui/src/main` is empty, and so is the matching `git status --porcelain`;
- `export_openapi.py --check` passes;
- every changed `ui/` file is in a Files Modified table;
- `ta-check` passes (AC-69.6).

There is no OpenAPI regeneration (G8 does not apply, since `packages/api/` is unchanged).

### 6. Container pre-gate (H1-2, non-authoritative)

`validate-task.sh pregate` runs every D6 stage that can run here:

- input identity;
- `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan-static`, `task-contract`;
- `pytest_env_ok`, `vitest_env_ok`;
- `ui-build`, `ui-harness-build`, `mcp-build`, `mcp-tests`, `openapi`, `state-render`;
- `electron_env_ok`;
- `source-audit` over `AUDIT_SRC`.

### 7. `WINDOWS_GATE` + `CHROME_LOOK` (H1-6, authoritative, local)

`validate-task.ps1 -Check windows-gate` runs the D6 stages. The canonical order is the `order` list in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts that the `.ps1` `$stages` ids equal it. The script records the preflight fields and the `ui-electron` duration (schema `s31-windows-gate.v1`; RULE-3).

`CHROME_LOOK` is the human visual checklist K1–K5 in [local-requests.md](local-requests.md) §GATE. Mat runs it on the same commit after the gate, on his large screen, and returns one line per item. `validate-task.sh look-check` refuses unless all five are recorded with a result and provenance in `walkthrough.md` §CHROME_LOOK. Any `fail` is a Decision Brief (cloud-local §3.5), never a silent fix.

`validate-task.sh windows-gate-check` validates the JSON:

- schema, clean tree, stage order and exits, `COUNT_FLOORS`, flaky;
- code identity over `GATED_PATHS`.

### 8. Closeout (H1-5, H1-7, H2)

- `validate_closeout_artifacts.py --ac-coverage-only` per handoff;
- `review-check`;
- the reflection validator with `--decision-source` for the plan, handoffs and grouping;
- `lint_task_contract.py`.

### Planning receipts

Run at plan time (container, 2026-10-10, before each dispatch; system `python3 -I`, no `uv sync`, no product code). Round 2 receipts:

```text
$ python3 -I docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py static        # exit 0
PASS static: 20 task rows; scripts, plan cross-references and file targets agree
$ python3 -I docs/execution/plans/2026-10-10-gui-polish-residuals/plan_checks.py selftest      # exit 0
PASS selftest duplicate row id / unknown check / swapped stage / undefined AC / changed floor / missing goal anchor / emphasis suite in rail stage / emphasis suite in REGSET / missing modify target
PASS selftest: every injected defect was reported
$ python3 tools/lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier \
    --task docs/execution/plans/2026-10-10-gui-polish-residuals/task.md                         # exit 0
OK: 20 row(s); 10-column table (with builder_model); 20 row(s) fully checked: backticked, exit-code re-raised, receipt under RECEIPTS_DIR; dependencies resolve and are acyclic
$ bash -n docs/execution/plans/2026-10-10-gui-polish-residuals/validate-task.sh                 # exit 0
```

`validate-task.ps1` was not parsed here (no `pwsh` in the container). Its stage list is checked against the `.sh` copy by `plan_checks.py static` item 3, and the reviewer may run `pwsh -NoProfile -Command "[ScriptBlock]::Create((Get-Content -Raw <path>)) | Out-Null"` as a static parse.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent (`gui-refs-not-shipped`, create-plan §4A note). The applicable canon is used instead:

| Element | Variant / size | States | Standard | E2E |
|---|---|---|---|---|
| Console toggle | `outline` / `secondary` (pressed), `sm` | `aria-pressed` false/true; hover; focus ring | G34, G32, UX1-style toggle (APG button) | AC-69.5; C1-1 to C1-5 (existing) |
| Commands button | `outline`, `sm` | enabled; hover; focus ring | G34, G32 | AC-69.5; `command-palette-nav.spec.ts` (existing) |
| Section card emphasis | not a control (a `section` frame) | current / not current | G32 (tokens), G33 (motion tokens; only `background-color`, `border-color` transition) | AC-70.6. Startup: jsdom AC-70.9 only, because the unpackaged Electron app never mounts the panel (AC-61.17); `CHROME_LOOK` K5 covers it when Mat runs a packaged build |
| Rail entries | unchanged | `aria-current` | unchanged (MEU-58) | AC-70.2; AC-58.12, A-6 (existing) |

G32/G33 (tokens; no `transition-all`; no raw hex) are enforced by `source-audit`. E2 is met: the one new element (`settings-tail-spacer`) has a registered test id and an Electron assertion (AC-70.2 measures what it is for). The spacer is `aria-hidden` and not interactive.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, a dependency MEU (19, 26, 58) is not `approved`, MEU-69/70 is not `pending`, the plan review is not `approved`, or the execution message is not recorded | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | The census finds an existing expectation this design contradicts, other than TA-1 and TA-2 | Stop for the human with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | A Red is not an assertion failure (collection or import error outside the declared new test file) | Fix the test setup only, then re-prove Red. |
| S4 | `AC-70.2` does not go Red on the pre-change page at `DEFAULT_WINDOW` or `TALL_WINDOW` in the container | Stop MEU-70 Red. Record which sections passed and their tops, then present a Decision Brief (for example: a `LOCAL_REPRO` of the Red spec on Mat's screen). Never weaken the assertion. |
| S5 | The spacer or `SCROLL_RECHECK` can pass only by changing an existing MEU-58 / A-6 / MEU-61 / MEU-62 Settings spec | Stop. That reopens MEU-58's rail contract; present a Decision Brief. |
| S6 | A gate failure that is not a product defect | Handle per cloud-local §3.5: a Decision Brief and an A-n row in `human-gate-decision.md`. No self-authorized test change. |
| S7 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |
| S8 | TA-1 or TA-2 is not authorized (the plan review rejects it, or the execution message vetoes it) | Do not edit either test. Stop MEU-69 before Green and present a Decision Brief (keep "Settings:" in the label vs. amend). |

## Decision Log

Carried from the grouping (stage `grouping`, reflection carry-forward). Session 31's own row is **D-7** (rename the palette control to "Commands Ctrl+K", with a command icon). **D-2** and **D-5** apply to every session. The H2-1 reflection still carries **every** grouping §8 row, D-1 to D-7, with stage `grouping`, because `validate_closeout_artifacts.py` requires the whole §8 table when the grouping is a decision source (Session 27 Review R2-1). The triage decisions in `known-issues.yaml` are cited in prose only, because their ids collide with grouping and plan ids (Session 27 Review R1 F5).

Planning decisions:

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Plan Session 31 before Session 30 (capture-flatten-backup)?"
    resolution: human
    class: two-way
    chosen: "Yes — plan Session 31 now"
    source_tag: Human-approved
    precedents: [".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md:72 — sessions are sequenced by session, not by dependency", ".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md:112 — Session 31 has no dependency on the sessions above", "docs/execution/plans/2026-10-01-capture-viewport-chrome/implementation-plan.md D-8 — Session 29 was planned out of order on the user's request"]
    research: { engine: none, sources: [] }
    reasoning: "The user asked for Session 31 by name. MEU-69 and MEU-70 depend only on approved MEUs (19, 26, 58). Session 30's MEU-67 may add a field to the Capture section of SettingsPage.tsx; that is a merge-order risk only, because the field sits inside an existing section frame and inherits SECTION_EMPHASIS."
    human_message_reference: "USER_EXPLICIT 2026-10-10 '/create-plan for Session 31 as per session grouping'"
  - id: D-9
    stage: planning
    question: "How do trailing Settings sections become current while scrolling (R4: the rail stops at Convert on a large screen)?"
    resolution: human
    class: product-preference
    chosen: "Bottom spacer so every section can reach the rail's top band, plus a re-check on scroll"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-09-30-tts-repair/walkthrough.md:29 — R4: rail follows Download..Convert only; the trailing sections cannot cross the observer threshold", "docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-6 — the click lock was fixed; the observer and current() were explicitly left to MEU-70", "ui/src/renderer/src/features/settings/SettingsRail.tsx:141 — rootMargin '0px 0px -60% 0px': a section is current only once it reaches the top 40 % band"]
    research: { engine: native, sources: ["https://github.com/twbs/bootstrap/issues/36431 — scrollspy: a short final section never reaches the top, so its link never activates", "https://forum.freecodecamp.org/t/portfolio-project-help-with-bootstrap-4-scrollspy/189351 — fix by giving the last section enough height/padding", "https://www.mintlify.com/fuma-nama/fumadocs/features/table-of-contents — Fumadocs selects the last item when scrolled to the bottom"] }
    reasoning: "Recommended and chosen. The spacer makes every section reachable by scroll, so the highlight walks through all of them in order and a click lands the section at the top. Its cost is empty space below the last section, at the end of the page only. A bottom-only fallback leaves Capture..Readiness unreachable by scroll on a large screen. Proportional progress mapping highlights a section that is not at the top of the view."
    human_message_reference: "USER_EXPLICIT 2026-10-10 AskUserQuestion 'Bottom spacer (Recommended)'"
  - id: D-10
    stage: planning
    question: "Does MEU-70's 'verify first' row need a new LOCAL_REPRO before execution?"
    resolution: autonomous
    class: two-way
    chosen: "No. R4 (2026-09-30) is the target check; the container Red (AC-70.2) reproduces the mechanism, and CHROME_LOOK K4 re-checks the fix on the target"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml SETTINGS-ACTIVE-SECTION-HIGHLIGHT verification — LOCAL_REPRO R4 result 'different'", "git log 407db19 — A-6 changed only the click lock; the scroll path is as R4 saw it", "docs/execution/plans/2026-10-01-capture-viewport-chrome/human-gate-decision.md A-1 — Session 29 used R3 instead of a new LOCAL_REPRO"]
    research: { engine: none, sources: [] }
    reasoning: "The scroll path (observer + current()) is byte-identical to the build R4 ran on, so a second repro would observe the same thing. If the container cannot reproduce it, Stop condition S4 sends the Red spec to the target instead."
  - id: D-11
    stage: planning
    question: "How does the Console toggle show its pressed state within the shared Button?"
    resolution: autonomous
    class: two-way
    chosen: "Unpressed variant outline; pressed variant secondary plus 'border border-transparent' so the box width is identical"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CaptureViewport.tsx:114 — toolVariant switches variant for aria-pressed toggles", "ui/src/renderer/src/components/ui/Button.tsx:14-20 — secondary is the tinted accent fill; outline-btn carries a 1 px border (styles.css:142-146)", "docs/build-plan/06-gui.md:1391 — shared Button, G32 colours, no new component"]
    research: { engine: none, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/button/ — toggle button: constant label, aria-pressed carries the state"] }
    reasoning: "A variant switch is the repo's existing toggle idiom and needs no ad-hoc colour (G34). Outline makes the idle control read as a button, which was the complaint. Without the transparent border the pressed box would be 2 px narrower and shift the header; NO_SHIFT asserts it does not. Alternatives: ghost→secondary keeps the 'reads as text' defect; outline plus a custom pressed background is ad-hoc styling under G34."
  - id: D-12
    stage: planning
    question: "What is the palette button's accessible name?"
    resolution: autonomous
    class: two-way
    chosen: "aria-label 'Commands', aria-keyshortcuts 'Control+K', title 'Open the command palette (Ctrl+K)'"
    source_tag: Research-backed
    precedents: ["docs/build-plan/06-gui.md:1390 — reads Commands, aria-label updated", "ui/src/renderer/src/components/layout/Header.tsx:64 — today's aria-label 'Open command palette'"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html — the accessible name must contain the visible label text", "https://www.w3.org/TR/wai-aria-1.2/#aria-keyshortcuts — aria-keyshortcuts exposes the shortcut to assistive tech"] }
    reasoning: "Keeping 'Open command palette' would fail WCAG 2.5.3, because the visible label 'Commands' would not be in the name, so voice users saying 'click Commands' would miss it. The shortcut goes in aria-keyshortcuts rather than the name. The title keeps the longer description as a tooltip."
  - id: D-13
    stage: planning
    question: "Which icons?"
    resolution: autonomous
    class: two-way
    chosen: "lucide SquareTerminal (Console) and Command (Commands), size 14, aria-hidden"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/components/layout/NavRail.tsx:1 — the app's icon set is lucide-react", "docs/build-plan/06-gui.md:1389-1390 — 'a terminal icon'; 'a command/search icon'", "ui/package-lock.json:7440-7442 — lucide-react 0.400.0 locked; both names exist in its dist/lucide-react.d.ts (checked 2026-10-10)"]
    research: { engine: none, sources: [] }
    reasoning: "SquareTerminal reads as a terminal panel at 14 px inside a 28 px button; Command is the ⌘ glyph palettes conventionally use, and Search would suggest a search box. Size 14 fits h-7 with the label."
  - id: D-14
    stage: planning
    question: "What does the current-section emphasis look like, and how is layout shift avoided?"
    resolution: autonomous
    class: two-way
    chosen: "Every frame always has SECTION_FRAME_BASE (-mx-3 pl-2.5 pr-3 py-2, rounded, border-l-2); current adds bg-bg-elevated/40 and border-accent; others border-transparent; no negative vertical margin (BOX_SEPARATION)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/11-page-layout.md:140 — subtle surface-raised background / left border from G32 tokens; no layout shift; no motion beyond G33", ".agent/docs/emerging-standards.md G33 — never animate box-shadow geometry; use the duration/ease tokens", "ui/src/renderer/src/features/settings/SettingsRail.tsx:229 — the rail's own current entry uses a tinted background"]
    research: { engine: none, sources: [] }
    reasoning: "Padding and border present on every frame means only colours change when the current section moves, so nothing shifts. The horizontal negative margin keeps today's x positions. A vertical negative margin was rejected: it would bring adjacent frames to 8 px apart, less than the 16 px scroll margin, so the previous section would stay inside the rail's top band (BOX_SEPARATION). A box-shadow bar was rejected because G33 lists box-shadow; padding only on the current frame would shift content."
  - id: D-15
    stage: planning
    question: "Where does the emphasis get its current section?"
    resolution: autonomous
    class: two-way
    chosen: "SettingsRail reports its active entry through onActiveChange; SettingsPage stores it and passes current to each frame"
    source_tag: Local Canon
    precedents: ["docs/build-plan/11-page-layout.md:140 — 'driven by the same observer state the rail uses'", "docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-6 — the click lock that owns the active entry lives in SettingsRail"]
    research: { engine: none, sources: [] }
    reasoning: "One source means the emphasis and the rail can never disagree, including during the A-6 click lock. A second observer in the page could disagree mid-scroll. Lifting all rail state into the page would rewrite the A-6 code for no behaviour change."
  - id: D-16
    stage: planning
    question: "How is the spacer sized?"
    resolution: autonomous
    class: two-way
    chosen: "Measured: clientHeight − SECTION_SCROLL_MARGIN − (content below the last section's top, excluding the spacer), ≥ 0, re-measured by ResizeObserver"
    source_tag: Research-backed
    precedents: ["ui/src/renderer/src/features/settings/SettingsRail.tsx:43-64 — revealSection scrolls block 'start', honouring scroll-mt-4"]
    research: { engine: native, sources: ["https://forum.freecodecamp.org/t/portfolio-project-help-with-bootstrap-4-scrollspy/189351 — padding after the last section lets it reach the top"] }
    reasoning: "This is the smallest spacer that lets the last section reach the same position a rail click scrolls it to, on any window height, and it shrinks to 0 when content is already long enough. A fixed padding (say 60vh) over-pads small windows and under-pads very tall ones; CSS alone cannot know the last section's height."
  - id: D-17
    stage: planning
    question: "Should the rail also re-check its current entry on scroll?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: a passive, frame-coalesced scroll listener runs the existing current(), respecting the click lock"
    source_tag: Research-backed
    precedents: ["ui/src/renderer/src/features/settings/SettingsRail.tsx:143-154 — current() already has an at-bottom rule, but it runs only inside the observer callback, which no crossing triggers at the bottom"]
    research: { engine: native, sources: ["https://www.mintlify.com/fuma-nama/fumadocs/features/table-of-contents — bottom-of-page selects the last item"] }
    reasoning: "The existing at-bottom rule is dead code at the bottom of the page, because nothing calls it there. The listener makes it live, and covers the case where the spacer measures 0 (no ResizeObserver). The user's chosen option text named this re-check."
  - id: D-18
    stage: planning
    question: "Spec 11:143 says 'all nine section ids'; the live set has eleven. Which governs?"
    resolution: autonomous
    class: two-way
    chosen: "SETTINGS_SECTION_SET (eleven, startup conditional); row 9 corrects the canon text"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/settings/settings-sections.ts:33-46 — eleven keys", "docs/build-plan/11-page-layout.md:95 — MEU-58 composes the sections from this set"]
    research: { engine: none, sources: [] }
    reasoning: "The rule's intent is 'keep every id'; the count is a stale number. Keeping all eleven is a superset of keeping nine, so no behaviour narrows."
  - id: D-19
    stage: planning
    question: "Apply TA-1 / TA-2, or keep 'Settings:' in the label so no test changes?"
    resolution: autonomous
    class: two-way
    chosen: "Apply TA-1 and TA-2 (subject to independent review and the execution message, S8)"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1390 — 'reads Commands' (Human-approved 2026-09-30)", ".agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md:175 — D-7 rename"]
    research: { engine: none, sources: [] }
    reasoning: "The Spec rule makes the old expectation wrong; keeping 'Settings:' to spare two assertions would ship the defect the MEU exists to fix. The amendment is the minimal one: the label regex, and the title that names it."
  - id: D-20
    stage: planning
    question: "How does the separately rendered Startup section get the emphasis (Review R1 F2)?"
    resolution: autonomous
    class: two-way
    chosen: "One helper, sectionFrameProps(current), in a new settings-section-frame.ts; SettingsSectionFrame and StartAtSignInControl both spread it; StartAtSignInControl gains an optional current prop"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/settings/StartAtSignInControl.tsx:79-83 — Startup renders its own section with the same base classes as SettingsSectionFrame (SettingsPage.tsx:106)", "ui/tests/unit/settings-page.test.ts:500-505 (AC-58.11) — settings sources stay top-level files in features/settings", "AGENTS §Planning Contract single-statement rule (create-plan Step 4)"]
    research: { engine: none, sources: [] }
    reasoning: "The rail lists Startup whenever the login item is supported (SettingsPage.tsx:362), so the emphasis must reach it or the right panel shows nothing for a current entry. A shared helper states the frame classes once, so the two producers cannot drift. Rendering Startup through SettingsSectionFrame would move that frame out of SettingsPage.tsx and rewrite a MEU-61 component for no behaviour gain; copying the classes into StartAtSignInControl would restate SECTION_EMPHASIS at two sites. Both files are under ui/, so the goal's 'UI only, no change outside ui/' boundary holds."
  - id: D-21
    stage: planning
    question: "How does the rail-only stage (row 6) avoid running emphasis assertions before row 7 implements them (Review R1 F1)?"
    resolution: autonomous
    class: two-way
    chosen: "Put every emphasis assertion in EMPHASIS_TESTS (a new settings-emphasis.test.tsx plus the AC-70.6 Electron spec); row 6 runs RAIL_STAGE_TESTS only; row 7 adds EMPHASIS_TESTS"
    source_tag: Local Canon
    precedents: [".agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md F1 — green70-rail ran AC-70.5 through REGSET", "docs/execution/plans/2026-10-01-capture-viewport-chrome/task.md rows 6-7 — the peer split pure geometry and viewport Green the same way"]
    research: { engine: none, sources: [] }
    reasoning: "A file boundary keeps every assertion intact and needs no test-name filter, which a later rename could silently bypass. The rail-before-emphasis order stays: row 6 still turns the rail green first, and plan_checks.py item 9 makes the split a checked control rather than a convention. A Vitest -t exclusion was rejected for that rename fragility; moving AC-70.5 to row 7's Red would break the tests-first rule for the MEU."
  - id: D-22
    stage: execution
    question: "The spacer made the existing AC-58.12 Electron spec fail deterministically (5/5): after a click on MCP access and a scroll back to the top, the page jumped back to MCP. How is it fixed?"
    resolution: autonomous
    class: two-way
    chosen: "Fix the latent race in revealSection's A-3 fallback: complete a smooth reveal only if the scroller emitted no scroll event (REVEAL_FALLBACK); add AC-70.10; AC-58.12 unchanged"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-3 — the fallback exists for a smooth scroll a hidden/throttled window drops entirely", "docs/execution/plans/2026-09-30-tts-repair/human-gate-decision.md A-6 — the rail's click-path timing was fixed in product code, with AC-58.12 unchanged", "AGENTS §Testing & TDD — never weaken an existing assertion to get Green"]
    research: { engine: none, sources: [] }
    reasoning: "Diagnosis (a throwaway replay spec, deleted): with the spacer, MCP enters the viewport earlier in its smooth scroll, so AC-58.12 scrolls back to scrollTop 0 before the 450 ms fallback fires; the fallback's test 'scrollTop equals its start' then mistakes 'moved and came back' for 'never moved' and jumps to MCP (log: scrollTop 0, then 2429 within 250 ms). That is a real user-visible race, not a test artefact. The alternatives were not legitimate: changing AC-58.12 would weaken an existing assertion, and dropping the spacer would reverse the user's D-9. Detecting 'never started' by the absence of any scroll event is the intent A-3 stated, keeps the A-3 jump, and touches only revealSection in a file already in PRODUCT_SCOPE. It passes the obviousness test, so it is decided and logged here, not asked; the execution review sees it."
```

## Round 1 Review Corrections

Plan review round 1 (Codex `gpt-6.1-sol`, `high`; `.agent/context/handoffs/2026-10-10-gui-polish-residuals-plan-critical-review.md`) returned `changes_required` with four findings. The review file is the reviewer's record and is not edited here (plan-critical-review §Write Scope). Each correction, with its blast-radius census (plan-corrections Step 5c), is in [review-r1-census.md](review-r1-census.md).

| Finding | Resolution |
|---|---|
| F1 High (blocking): `green70-rail` ran AC-70.5 through `REGSET` before row 7 implements the emphasis | Fixed at the root: the emphasis assertions live in `EMPHASIS_TESTS` (a new `settings-emphasis.test.tsx` plus the AC-70.6 spec); row 6 runs `RAIL_STAGE_TESTS` only; rows 5 (Red) and 7 (Green) and `gate70` include `EMPHASIS_TESTS`. No assertion changes and the rail still goes first (D-21). `plan_checks.py static` item 9 checks the split, and its selftest proves the check fires. |
| F2 High (blocking): the supported Startup section has no emphasis producer | `SECTION_EMPHASIS` is now one helper, `sectionFrameProps`, in a new `settings-section-frame.ts`; `SettingsSectionFrame` and `StartAtSignInControl` both use it, and `SettingsPage` passes `current` to both (D-20). New AC-70.9 covers the supported login-item state in jsdom. Both new and changed files are under `ui/`, so the goal holds; they are in Files Modified (`PRODUCT_SCOPE`) and `AUDIT_SRC`. |
| F3 Medium: `NO_SHIFT` compared a scroll round trip that ends in the same current section | `NO_SHIFT` now compares document-relative `h2` geometry between two samples whose current keys are asserted to differ (Download vs Capture, sampled while Capture is still current). |
| F4 Low: the GATE request restated `COUNT_FLOORS` and `DEFAULT_WINDOW` literals | `local-requests.md` §GATE now names both contracts; the numbers are copied in only when a request is sent. |

Two non-finding notes from the review are also applied: AC-70.2 is two independent specs with diagnostics (Q2), and the left padding is `pl-2.5` so the 2 px border no longer moves content 2 px right (Q3).

## Round 2 Correction Notes (post-approval, non-blocking)

Round 2 approved the plan with one Low, non-blocking finding. The reviewer asked for no further round for it ("No additional review round is requested for this clerical note"), and Mat's execution message (2026-10-11) asked for it to be resolved at row 5, before the new test is written, via this recorded route rather than a silent edit.

| Finding | Resolution |
|---|---|
| F5 Low: the planned scroll-margin source oracle named `SettingsPage.tsx`, but `SECTION_FRAME_BASE` moves `scroll-mt-4` into `settings-section-frame.ts` | Took the reviewer's second option: assert `scroll-mt-4` on the **rendered** section frames. The first option (a source check on `settings-section-frame.ts`) would put a check on a row 7 file inside AC-70.1, which runs in the row 6 rail stage (`RAIL_STAGE_TESTS`) before that file exists, and would reopen F1. The rendered check lives in AC-70.4 (`settings-rail.test.tsx`, a rail-stage suite that already renders the page). It holds before row 7 (`SettingsSectionFrame` and `StartAtSignInControl` both carry `scroll-mt-4` today) and after it (via `SECTION_FRAME_BASE`), and it covers both producers. `SECTION_SCROLL_MARGIN === 16` stays in AC-70.1. `SECTION_SCROLL_MARGIN`, AC-70.1 and AC-70.4 are updated; no existing test changes. Census: [review-r2-census.md](review-r2-census.md). |

## Execution Correction Notes

Recorded during execution so that no plan-level contract changes silently (Mat's execution message, 2026-10-11). Each item is visible to the execution review.

| Item | Change | Evidence |
|---|---|---|
| D-22 / AC-70.10 / `REVEAL_FALLBACK` | Row 6 exposed a latent race in `revealSection`'s A-3 fallback: the existing AC-58.12 Electron spec failed 5/5 after the spacer landed. The fallback now completes a smooth reveal only if its scroller emitted no scroll event. New AC-70.10 (jsdom) proves both sides; AC-58.12 passes unchanged. | `walkthrough.md` §MEU-70 rail fix (row 6); census [review-exec-census.md](review-exec-census.md) |
| A-3 rail group headings | After `CHROME_LOOK` attempt 1 the user asked for the PAGES / APP / SETUP headings to read as non-clickable. The heading `<p>` gets `cursor-default select-none`, a token tint `bg-bg-subtle/20`, padding and `tracking-wider`; no role, focus or entry change. One appended `settings-rail.test.tsx` case (Red first). The user approved it in the app. | `human-gate-decision.md` §A-3; commit `3dc8fd2` |
| A-4 framework drift | `WINDOWS_GATE` attempt 2 stopped at the preflight: `P:/agentic-framework` moved `80461f6` → `e387dec`; the registry hash is unchanged. The user accepted it. | `human-gate-decision.md` §A-4 |
| A-5 `PILL_TOKEN_SOURCE` drift | `WINDOWS_GATE` attempt 2 failed only AC-41.3 (MEU-41 canon): Zorivest `7b73b5b7` (MEU-661, 2026-10-14) changed light `--color-accent-cyan` `#0891b2` → `#0e7490`. The user chose to port that one token into `styles.css`'s light block; light `--color-accent` (also `#0891b2`) is deliberately left as is. Outside the MEU-69/70 surface, inside `ui/`. | `human-gate-decision.md` §A-5; receipts `C:/Temp/av-kit/keep/f9303a1-attempt2/` |
| A-6 contrast baseline | `WINDOWS_GATE` attempt 3 failed only AC-43.3: A-5's darker cyan moves 16 light rows of the MEU-43 measured matrix (`docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json`, a `GATED_PATHS` member). The user approved re-baselining exactly those 16 values (data only; labels 10.65–12.74, all above `CONTRAST_MIN`). | `human-gate-decision.md` §A-6; receipts `C:/Temp/av-kit/keep/da1d111-attempt3/` |
| Execution review R1 F1 (`TAIL_SPACER`) | The independent execution review (round 1, High) found that `useTailSpacer` reset its spacer bookkeeping to `0` on every effect restart while the rendered spacer kept its height. A section-list change (supported Startup loading after the first nonzero spacer) then made the next measurement subtract nothing, so a later resize undersized the spacer and MCP could not reach the top band (AC-70.2 / AC-70.4). The applied height now lives in a `useRef` that outlives effect restarts; the `TAIL_SPACER` and `TAIL_SPACER_HEIGHT` contracts are unchanged. One appended `settings-rail.test.tsx` case (Red first: `expected 100 to be 484`, the reviewer's own trace). | `.agent/context/handoffs/2026-10-10-gui-polish-residuals-implementation-critical-review.md` F1; `walkthrough.md` §Execution review corrections |

Files added to the Files Modified set during execution:

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/styles.css` | modify | light `--color-accent-cyan` `#0e7490` (A-5) |

## Research References

- WAI-ARIA APG, Button pattern (toggle buttons): https://www.w3.org/WAI/ARIA/apg/patterns/button/
- WCAG 2.2 Understanding SC 2.5.3 Label in Name: https://www.w3.org/WAI/WCAG22/Understanding/label-in-name.html
- WAI-ARIA 1.2 `aria-keyshortcuts`: https://www.w3.org/TR/wai-aria-1.2/#aria-keyshortcuts
- Bootstrap scrollspy issue 36431 (short final sections never activate): https://github.com/twbs/bootstrap/issues/36431
- freeCodeCamp forum, scrollspy and section size: https://forum.freecodecamp.org/t/portfolio-project-help-with-bootstrap-4-scrollspy/189351
- Fumadocs table of contents (last item at the bottom): https://www.mintlify.com/fuma-nama/fumadocs/features/table-of-contents
- Session 27 R4 and A-6: `docs/execution/plans/2026-09-30-tts-repair/walkthrough.md:29`, `human-gate-decision.md` §A-6

## Validation stage contract

The stages bind to PROFILE D6 (`.agent/docs/commands.md` §D6): static (`py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan-static`, `task-contract`), targeted (`red*`, `green*`, `gate*` above), and one fresh full gate (`WINDOWS_GATE`, authoritative; `pregate`, its non-authoritative container rehearsal). Each `validate-task.sh` check records its argv in its receipt, runs from the repo root under bash, is blocking, and writes `$RECEIPTS_DIR/s31-*`. Each `validate-task.ps1` stage records argv, exit and receipt in `windows-gate-result.json`.

Input identity is obtained independently of the run: `git rev-parse HEAD`, the `git status --porcelain` digest, the three lockfile hashes, the Node and Electron versions, plus the two external inputs in the preflight. `windows-gate-check` binds the result to the reviewed code over `GATED_PATHS`. Any change to those paths after the tested commit invalidates the gate, and a new attempt is required (cloud-local §3.4). Intermediate evidence is never reused for the final review. The handoffs carry `evidence.v1` records from the fresh gate.
