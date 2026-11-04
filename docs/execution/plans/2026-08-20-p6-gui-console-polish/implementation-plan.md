---
project: "2026-08-20-p6-gui-console-polish"
date: "2026-08-20"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-27"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI Console Polish

> **Project**: `2026-08-20-p6-gui-console-polish`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §Console Panel (Right Side Sheet)
> **Status**: `draft`
> **Grouping**: insert Session **8c** after Session 8b (`p6-gui-zorivest-chrome`). Do not start MEU-21–25.

---

## Goal

Fix the four Human-reported console defects after MEU-26: copy Zorivest Trade expand/collapse chrome (single header-left toggle with lucide icons; expand hides `main` so only the console fills the content row; collapse restores the 40% drawer and stays mounted), contain log scroll inside the pane, replace the Level dropdown with exclusive exact-level buttons, and paint the log viewport black-on-console-green. Amend `06-gui.md` + `gui-actions-index.md` so collapse, filter, and output color match this contract. Do not implement Transcript/TTS pages, Settings leaf writes, or FastAPI/MCP changes.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom is a bypass class for source/docs/exact-evidence and has no approved disposition. Planning and execution use file reads + P0 receipts."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-27 | `.agent/context/handoffs/2026-08-20-p6-gui-console-polish-MEU-27-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-20-p6-gui-console-polish-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` task row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-27a | Register `MEU27_ROW` in YAML/matrix/grouping. Do not start MEU-21–25. | — | `shared` | `.agent/context/meu-status.yaml` |
| WP-27b | Red: AC-27.1–27.10 UI tests **before** polish production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Include `SUPERSEDED_26` replacements. Receipt must pass `RED_ORACLE_CHECK` (kind `ui`) — 10 distinct failed JSON tests. | WP-27a | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-27-ui.txt`; `RED_JSON` |
| WP-27c | Green: `EXPAND_TOGGLE`, `COLLAPSE_SEMANTIC`, `SHELL_VIEWPORT`, `LEVEL_BUTTONS`, `CONSOLE_OUTPUT_THEME`. Do not neutralize tests. Do not edit FastAPI/MCP. | WP-27b | `compact_continue` | `PAGE_FILES`; compact then re-read `task.md` |
| WP-27d | Amend `E2E_WAVE` (`E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CASE_ORACLES` + `E2E_CONTROL_CENSUS`). Run or `[B]` `E2E_SANDBOX`. | WP-27c | `compact_continue` | `ui/tests/e2e/console-chrome.test.ts`; `C:/Temp/av-kit/e2e-console-polish.txt` |
| WP-27e | Amend `06-gui.md` console rows + `gui-actions-index.md` `console:collapse` persist key and `console:filter` exclusive-button label. Prove `SPEC_AMEND_MARKERS`. | WP-27d | `shared` | `docs/build-plan/06-gui.md`; `docs/build-plan/gui-actions-index.md` |
| WP-27f | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-27e | `compact_continue` | `.agent/context/handoffs/2026-08-20-p6-gui-console-polish-MEU-27-handoff.md` |
| WP-27g | Hub + SSOT: bind MEU-27; keep prior plan slashes; `HUB_NEXT_AFTER` stays transcript. Grouping Session 8c → complete is **H2 after exec `approved`**. | WP-27f | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution.
2. **Session pathway:** `current-focus.md` says next is `/create-plan p6-gui-transcript` and “Do not start MEU-21–25.” This project is **not** MEU-21–25. It is a Human-approved console-polish insert (`USER_EXPLICIT` 2026-08-20). `HUB_NEXT_AFTER` remains `/create-plan p6-gui-transcript`.
3. **Expand/collapse chrome:** Live MEU-26 shows both Expand and Collapse as text links in the toolbar, always. Zorivest `TradeDetailPanel.tsx` 303–324 is one ghost `sm` button in the **panel header left**, lucide `PanelLeftClose` / `PanelLeftOpen`, label swaps, `aria-expanded`. **Lock `EXPAND_TOGGLE`.**
4. **Collapse semantic:** MEU-26 AC-26.8 / C1-4 / spec 324 treat collapse as unmount. Zorivest collapse restores open `CONSOLE_DRAWER_GEOM` and keeps the pane mounted; Close is the X. Human: “look how it works in zorivest” + “expand so only console is visible.” **Lock `COLLAPSE_SEMANTIC`.** Amend spec + `gui-actions-index.md` persist key. This is contract supersession (`SUPERSEDED_26`), not G36 neutralization.
5. **Only console visible:** Zorivest `TradesLayout.tsx` 450 hides the table (`main`) and sets the pane `w-full`; rail + header stay. **Lock `EXPAND_SOLO`:** hide `main` only. Do not hide `NavRail` or `Header`.
6. **Document scroll:** AppShell today is `min-h-screen` with an unconstrained `<pre>`. Zorivest shell is `h-screen` + `main.overflow-auto`; Trade detail is `flex flex-col h-full` + `flex-1 overflow-auto` (298, 385). **Lock `SHELL_VIEWPORT`.**
7. **Level control:** Spec 316 dropdown + MEU-26 threshold filter vs Human “buttons … only the DEBUG events.” G21 requires exclusive direct selection. **Lock `LEVEL_BUTTONS` + `LEVEL_EXACT`.** Do not add an invented ALL button (dropdown had five values). Default stays `DEBUG` (current React state). Lines with no level token fail closed (hidden) when a level is selected.
8. **Output color:** Spec 317 color-by-level vs Human “background … black and text … console green.” **Lock `CONSOLE_OUTPUT_THEME`** on `console-output` only. Header/toolbar stay `TOKEN_SET`.
9. **4A indexes:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` remain **absent** (same as MEU-26). The §4A table below is the mapping.
10. **MEU ID:** C2 forbids unowned product work. **Lock `MEU27_ROW`.** Do not reopen approved MEU-26.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `MEU27_ROW` | YAML MEU: `id: MEU-27`, `slug: gui-console-polish`, `phase: '6'`, `band: P2`, `matrix_item: '6.2b'`, `depends_on: [MEU-26]`, `build_ref.path: build-plan/06-gui.md`, `build_ref.anchor: console-panel-right-side-sheet`, status `pending` until H1-3 | C2; this plan |
| `EXPAND_TOGGLE` | Exactly one expand/collapse control is mounted at a time, in `console-header` **left** (DOM: toggle then title `Console`, then `console-close` on the right). Collapsed: `data-testid="console-expand"`, lucide `PanelLeftClose` size 16, visible text `Expand`, `aria-expanded="false"`, `aria-label="Expand panel to full width"`. Expanded: `data-testid="console-collapse"`, lucide `PanelLeftOpen` size 16, visible text `Collapse`, `aria-expanded="true"`, `aria-label="Collapse panel"`. Variant `ghost` size `sm`. Not in the Search/Clear/Copy toolbar | Human-approved; Local Canon zorivest `TradeDetailPanel.tsx` 300–336 |
| `EXPAND_SOLO` | When `ui.panel.console.expanded===true` and the panel is open: `console-panel` has `w-full`; `main` has class `hidden`. Rail + Header remain visible | zorivest `TradesLayout.tsx` 450, 615; Human-approved |
| `COLLAPSE_SEMANTIC` | `console-collapse` click sets expanded false and **keeps** `console-panel` mounted at open `CONSOLE_DRAWER_GEOM`. It must not call `setConsoleOpen(false)` | zorivest `onToggleExpand`; Human-approved |
| `CONSOLE_DRAWER_GEOM` | closed: not mounted. Open: `w-[40%] min-w-[320px] max-w-[500px]`. Expanded: `w-full` + `EXPAND_SOLO` | MEU-26 named set; unchanged |
| `CLOSE_PATHS` | Unmount via `console-close`, `Escape`, and `header-console-btn` / `console:toggle` only. Not via `console-collapse` | this plan lock 4 |
| `SHELL_VIEWPORT` | AppShell root: `h-screen overflow-hidden flex flex-col` (must not use `min-h-screen`). Body row: `flex flex-1 min-h-0 overflow-hidden`. `console-panel`: `flex flex-col h-full min-h-0 overflow-hidden` plus `CONSOLE_DRAWER_GEOM`. `console-output`: `flex-1 min-h-0 overflow-auto` | zorivest `AppShell.tsx` 155–160 + Trade detail 298/385; Human-approved |
| `LEVEL_BUTTONS` | `console-filter` is `role="radiogroup"` `aria-label="Level"` containing one `Button` per `CONSOLE_LEVELS` value. Testids `console-level-DEBUG` … `console-level-CRITICAL`. Active: `aria-checked="true"` `role="radio"` variant `primary`. Inactive: `aria-checked="false"` variant `ghost`. Click sets that level directly (G21 — no cycling) | Human-approved; G21 |
| `CONSOLE_LEVELS` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` — exhaustive compile-time union | MEU-26 / Spec 316 |
| `LEVEL_DEFAULT` | `DEBUG` | current `ConsolePanel` state; Spec dropdown default |
| `LEVEL_EXACT` | `lineMatchesExactLevel(line, level)` is true iff the line contains a bracket token whose captured name equals `level` case-insensitively: regex `\[(DEBUG\|INFO\|WARNING\|ERROR\|CRITICAL)\s*\]`. No token ⇒ `false` (fail closed). Search + yt-dlp filters still apply after the level predicate | Human-approved |
| `CONSOLE_OUTPUT_THEME` | `styles.css` defines `--color-console-bg: #000000` and `--color-console-fg: #33ff00`. `console-output` uses `bg-[var(--color-console-bg)]` and `text-[var(--color-console-fg)]`. Header/toolbar do not | Human-approved; G32 |
| `CONSOLE_CONTROLS` | `{app-shell, console-panel, console-header, console-filter, console-level-DEBUG, console-level-INFO, console-level-WARNING, console-level-ERROR, console-level-CRITICAL, console-search, console-clear, console-copy, console-expand, console-collapse, console-close, console-ytdlp-toggle, console-log-to-file, console-output}` — expand and collapse are mutually exclusive in the DOM (`EXPAND_TOGGLE`) | this plan |
| `PAGE_FILES` | `styles.css`, `AppShell.tsx`, `ConsolePanel.tsx` | this plan |
| `SUPERSEDED_26` | `chrome-zorivest.test.ts` AC-26.8 collapse-unmounts; AC-26.10 requires `SelectInput` as the level control and both expand+collapse present; `console-actions.test.ts` / `e2e-wiring.test.ts` control lists if they require both toggle ids always; `console-chrome.test.ts` C1-3 second click on `console-expand`; C1-4 collapse as a close path; spec 316 “Dropdown”; spec 317 color-by-level; spec 324 “collapse unmounts”; `gui-actions-index.md` `console:collapse` persist `ui.panel.console.visible`; `gui-actions-index.md` `console:filter` label `Level dropdown` | this plan lock 4/7/8 |
| `E2E_WAVE` | `ui/tests/e2e/console-chrome.test.ts` (`E2E_CASES`) + `CONSOLE_CONTROLS` ids in `test-ids.ts` | E2 |
| `E2E_CASES` | `C1-1` closed launch: same-expression `console-panel` `.toHaveCount(0)`; `C1-2` open → filter/search/clear/ytdlp/`console-output` visible + `console-level-DEBUG` `.click(`; `C1-3` after `console-expand` `.click(` same-expression `console-panel` is bound to `w-full`; after `console-collapse` `.click(` same-expression `console-panel` is bound to `min-w-[320px]` and `.toHaveCount(1)`; `C1-4` close via X + Esc + header toggle only (count ≥ 3 `Get-BoundMatchCount` + `Assert-C14EachPathEndsAbsent`); `C1-5` copy + log-to-file + `clipboard` + `settings/app` + `log_to_file`; `C1-6` `nav-collapse` + `nav-rail--collapsed` + settings cards; `C1-7` `console-level-INFO` `.click(` then same-expression `console-output` asserts INFO present and DEBUG absent; `C1-8` same-expression `console-output` bound to `overflow-auto`, `--color-console-bg`, and `--color-console-fg`; same-expression `app-shell` bound to `h-screen` | E2 |
| `E2E_LOCATOR_FORM` | locators are literal `getByTestId('<kebab-id>')` (single quotes) | E2 |
| `E2E_PER_CONTROL` | allowed method chained on the same locator: `expect(page.getByTestId('id')).toBeVisible()` or `page.getByTestId('id').click()`. Closed-panel oracle is same-expression `console-panel` `.toHaveCount(0)`. Mounted-after-collapse oracle is same-expression `console-panel` `.toHaveCount(1)` | E2 |
| `E2E_CASE_ORACLES` | `E2E_CASES` — sole prose statement. `E2E_CONTROL_CENSUS` is the executable owner; do not restate case text here | E2; r1 F1 |
| `E2E_CONTROL_CENSUS` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-console-polish/assert-e2e-control-census.ps1` | E2; §4A.3 |
| `RED_AC_IDS` | `AC-27.1` … `AC-27.10` (10). Owner: `assert-red-oracle.ps1` ui kind + `RED_JSON` | FIC |
| `RED_TEST_TITLE` | every AC-27.N test is a **distinct** Vitest case whose `fullName`/`title` contains exactly one `AC-27.N` | FIC |
| `RED_JSON` | `C:/Temp/av-kit/fail-to-pass-meu-27-ui.json` from Vitest 3 `--reporter=json --outputFile` | Vitest 3 |
| `RED_ORACLE` | UI FAIL_TO_PASS text has allow-marker and no deny-marker **and** `RED_JSON` maps 10 distinct failed `assertionResults` 1:1 onto `RED_AC_IDS` | carry-forward |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-console-polish/assert-red-oracle.ps1 -Kind ui -Receipt <text> -JsonReceipt RED_JSON` | PR-9 |
| `BUILDER_PIN` | `—` while `fresh_worker: none` | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping |
| `GROUPING_DONE_MARK` | Progress-table row `\| 8c \| .+p6-gui-console-polish.+ \| ✅ complete \|`; Sessions 9–12 stay `✅ complete` (do not require `⬜ pending`) | H2 only; USER_EXPLICIT 2026-08-27 |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-20-p6-gui-console-polish-MEU-27-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-20-p6-gui-console-polish` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-console-polish/` | phase `"6"` |
| `PRIOR_PLAN_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/` | must remain on phase `"6"` |
| `HUB_NEXT_AFTER` | `All registered MEUs approved; no next /create-plan.` | USER_EXPLICIT 2026-08-27 closeout |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p6 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-20-p6-gui-console-polish-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-20-p6-gui-console-polish/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-27.txt` written **once** before the MEU-27 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-console-polish/assert-handoff-markers.ps1` | PR-9 |
| `VITEST_ALLOW_ONLY` | every `npx vitest run` passes `--allowOnly=false` | G36 |
| `UI_ESLINT` | `npx eslint src/ tests/ --max-warnings 0` | G36 |
| `MEU27_TOUCHED` | `PAGE_FILES` + unit tests for polish + `SUPERSEDED_26` + `ui/tests/e2e/console-chrome.test.ts` + `test-ids.ts` | this plan |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-27.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` is **not** modified → `--check` still run as no-drift proof. `-o` forbidden unless FAIL | G8 |
| `REGRESSION_TESTS` | p6-gui-zorivest-chrome H1-2 Python set (do not drop) | p6 carry-forward |
| `SCAN_G36_ARGS` | skip/only/todo markers under `ui/tests/unit` + `ui/tests/e2e` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `ui/src` | anti-placeholder |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up. Tests stay written and wired | known-issue policy |
| `REFLECTION_TEMPLATE` | `docs/execution/reflections/TEMPLATE.md` | closeout |
| `REFLECTION_SCHEMA` | `.agent/schemas/reflection.v1.yaml` | closeout |
| `REFLECTION_PEER_RULE` | newest `docs/execution/reflections/*-reflection.md` excluding `TEMPLATE.md` | AGENTS |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `SSOT_RENDER` | `rtk proxy uv run python tools/meu_status.py render` (no `--check`). Must run after the last pre-review YAML mutation and before `render --check` | MEU-26 carry-forward |
| `SPEC_AMEND_MARKERS` | `06-gui.md` must contain `Exclusive level buttons`, `panel header left`, `console-output`, `--color-console-bg`, and `restores the 40% drawer`; must not contain `Dropdown: DEBUG`, `Green = INFO, Yellow = WARNING`, or `Side-sheet collapse unmounts`. `gui-actions-index.md` `console:collapse` persist column is `ui.panel.console.expanded` (not `ui.panel.console.visible`). `gui-actions-index.md` `console:filter` row must contain `exclusive exact-level buttons` and must not contain `dropdown` | this plan lock 4/7/8; r1 F2 |
| `LOG_TO_FILE_PUT` | existing `PUT /settings/app` body `{ log_to_file: boolean }` only | MEU-15 / MEU-19 / MEU-26 |
| `TOKEN_SET` | MEU-26 Dracula tokens — unchanged except the two `CONSOLE_OUTPUT_THEME` variables added | MEU-26 |

---

## Proposed Changes

### MEU-27 — `gui-console-polish`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-Input Error | Create/Update Parity | Source |
|---------|-------------|-------------------|--------------------|---------------------|----------------------|--------|
| Level button clicks | local React state + `CONSOLE_LEVELS` union | closed set; unknown label ignored | n/a | fail closed — keep prior `LEVEL_DEFAULT` | n/a (no network) | Human-approved; G21 |
| Console search / yt-dlp checkbox | local React state | string; boolean | ignore | n/a | n/a | Spec 319–320 |
| `ui.panel.console.visible` / `.expanded` | `usePersistedState` | JSON boolean | reject non-boolean (MEU-26 typeof guard) | fallback closed / not-expanded | persist is the write | MEU-26 |
| `PUT /settings/app` `log_to_file` | existing API `SettingsPutIn` | boolean | `extra="forbid"` | 422 | same PUT | `LOG_TO_FILE_PUT` |

No new REST or MCP write surface. No Zod/Pydantic owner is created.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-27.1 | integration | Open panel header matches `EXPAND_TOGGLE`: one toggle in `console-header` left with lucide `PanelLeftClose` + text `Expand`; `console-collapse` is absent; Close is the right sibling | Human-approved; Local Canon zorivest `TradeDetailPanel.tsx` 300–336 | both Expand and Collapse text buttons exist in the toolbar at once, or icons are missing |
| AC-27.2 | integration | `console-expand` click applies `EXPAND_SOLO` (`w-full` + `main.hidden`); the same control re-renders as `console-collapse` with `PanelLeftOpen` + `Collapse` | Human-approved; zorivest expand | expand only changes a label and leaves 40% width, or hides `NavRail`/`Header` |
| AC-27.3 | integration | `console-collapse` applies `COLLAPSE_SEMANTIC`: panel stays mounted at open `CONSOLE_DRAWER_GEOM`; `main` is not `hidden` | Human-approved; zorivest collapse | collapse unmounts `console-panel` (AC-26.8) |
| AC-27.4 | integration | `CLOSE_PATHS` unmount the panel; after expand, a close path also clears expanded so `main` is not `hidden` | MEU-26 AC-26.8 minus collapse; exec r1 F1 | collapse is required to unmount, or close-while-expanded leaves `main.hidden` |
| AC-27.5 | unit | `SHELL_VIEWPORT` class tokens are present on AppShell root (`data-testid="app-shell"`), body row, `console-panel`, and `console-output`. AppShell root must not contain `min-h-screen` | Human-approved; zorivest AppShell 155–160 | root is `min-h-screen` or `console-output` has no `overflow-auto` |
| AC-27.6 | unit | `CONSOLE_OUTPUT_THEME` variables exist in `styles.css`; `console-output` className uses both `var(--color-console-*)` tokens and no raw `#` hex | Human-approved; G32 | output uses `text-fg` / `bg-bg` or `className` contains `#000` / `#33ff` |
| AC-27.7 | integration | `LEVEL_BUTTONS`: five radios; click `console-level-INFO` sets `aria-checked` on INFO only (G21 direct select) | Human-approved; G21 | `SelectInput` is still the level control, or click cycles to the next level |
| AC-27.8 | unit | `lineMatchesExactLevel` implements `LEVEL_EXACT`: `[debug ]` matches DEBUG only; `INFO` line is false for DEBUG; tokenless line is false | Human-approved | threshold semantics (`INFO` line visible when filter is DEBUG) still hold |
| AC-27.9 | integration | Open panel applies `LEVEL_EXACT` to rendered `console-output` text: with DEBUG selected, an INFO line is absent and a DEBUG line is present | Human-approved | dropdown `console-filter` `<select>` still drives a min-level filter |
| AC-27.10 | unit | `PAGE_FILES` `className` strings contain no raw `#` hex (G32). `SUPERSEDED_26` tests/spec no longer require collapse-unmount or Level `SelectInput` | G32; this plan lock 4/7 | `className="bg-[#000000]"` or AC-26.8 still asserts collapse unmounts |

#### Control binding (PR-8)

| AC | Observable | Traceable call chain | Negative oracle |
|----|------------|----------------------|-----------------|
| AC-27.3 | `document.querySelector('[data-testid=console-panel]')` after collapse click | `console-collapse` `onClick` → `AppShell` `setConsoleExpanded(false)` only → `ConsolePanel` remains in the tree with open `CONSOLE_DRAWER_GEOM` | If `onCollapse` still calls `setConsoleOpen(false)`, query is **null** after collapse |
| AC-27.5 | className strings on AppShell root / body row / `console-output` | `AppShell` root `className` + body `div` + `ConsolePanel` root + `console-output` | Root still `min-h-screen` **or** `console-output` lacks `overflow-auto` (document grows with `<pre>`) |
| AC-27.8 | boolean from `lineMatchesExactLevel` | `ConsolePanel` `useMemo` visible-lines filter → `lineMatchesExactLevel(line, filter)` (single statement; no read-then-write) | `lineMatchesExactLevel('[info] x', 'DEBUG')===true` (old threshold) |
| AC-27.4 | `console-panel` null after X / Esc / header; `main.className` not `hidden` | Close / Escape / `TOGGLE_CONSOLE_EVENT` → `setConsoleOpen(false)` **and** `setConsoleExpanded(false)` (MEU-26 r1 F1) | Close-while-expanded leaves `main.hidden` |
| AC-27.7 | `aria-checked` on the five radios | `console-level-*` `onClick` → `setFilter(level)` (direct map; not `next[current]`) | Click INFO results in WARNING (cycle map) |

`CONSOLE_LEVELS` is a closed set owned by this plan: adding a level without updating the union must fail typecheck. Unrecognized filter string fails closed to `LEVEL_DEFAULT`.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Single header-left expand/collapse with lucide icons | Human-approved + Local Canon | User 2026-08-20 + zorivest `TradeDetailPanel.tsx` 303–324 |
| Collapse restores drawer (does not unmount) | Human-approved + Local Canon | Overrides spec 324 / AC-26.8 |
| Expand hides `main` only | Local Canon | zorivest `TradesLayout.tsx` 450 |
| Viewport containment | Human-approved + Local Canon | zorivest `h-screen` + `flex-1 overflow-auto` |
| Exclusive exact-level buttons | Human-approved + Local Canon G21 | Overrides spec 316 dropdown + MEU-26 threshold |
| Black / `#33ff00` output | Human-approved | Overrides spec 317 color-by-level for the viewport |
| No ALL button | Human-approved (literal) | Dropdown had five values; do not invent a sixth |
| G32 tokens | Local Canon | G32 |
| Settings leaves / Transcript / TTS | Spec | deferred MEU-21–23 |
| Console transport / redact / seq | Spec | unchanged MEU-19/26 |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/styles.css` | modify | `CONSOLE_OUTPUT_THEME` variables |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | `SHELL_VIEWPORT`; `onCollapse` = un-expand only |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modify | `EXPAND_TOGGLE`, `LEVEL_BUTTONS`, `LEVEL_EXACT`, `console-output` |
| `ui/tests/unit/chrome-zorivest.test.ts` | modify | `SUPERSEDED_26` AC-26.8 / AC-26.10 |
| `ui/tests/unit/console-polish.test.ts` | new | AC-27.1–27.10 |
| `ui/tests/unit/console-actions.test.ts` | modify | `CONSOLE_CONTROLS` if listed |
| `ui/tests/unit/e2e-wiring.test.ts` | modify | level button ids |
| `ui/tests/e2e/test-ids.ts` | modify | header/output/level ids |
| `ui/tests/e2e/console-chrome.test.ts` | modify | `E2E_CASES` C1-3/C1-4/C1-7/C1-8 |
| `docs/build-plan/06-gui.md` | modify | filter / color / collapse rows |
| `docs/build-plan/gui-actions-index.md` | modify | `console:collapse` persist key |
| `docs/build-plan/build-priority-matrix.md` | modify | row `6.2b` MEU-27 |
| `.agent/context/meu-status.yaml` | modify | `MEU27_ROW`; P2 range MEU-14–27 |
| `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | modify | Session 8c row |

---

## create-plan §4A — GUI Element Compliance

Indexes absent. Mapping below is the Target Spec substitute.

| Element | testid | Variant / size / states | Feedback | E2E case |
|---------|--------|-------------------------|----------|----------|
| Expand | `console-expand` | `Button` ghost / sm / `aria-expanded=false` + lucide `PanelLeftClose` | T1 | C1-3 |
| Collapse | `console-collapse` | `Button` ghost / sm / `aria-expanded=true` + lucide `PanelLeftOpen` | T1 | C1-3 |
| Close X | `console-close` | `Button` outline / sm / `icon` | T1 | C1-4 |
| Level radios | `console-level-*` | `Button` primary (active) / ghost (inactive) / sm / `role=radio` | T1 | C1-2, C1-7 |
| Level group | `console-filter` | `radiogroup` | T0 | C1-2 |
| Search | `console-search` | text input + `getG30Styles()` | T0 | C1-2 |
| Clear | `console-clear` | `Button` outline / sm | T1 | C1-2 |
| Copy | `console-copy` | `Button` primary / sm | T1 | C1-5 |
| yt-dlp toggle | `console-ytdlp-toggle` | checkbox | T1 | C1-2 |
| Log to file | `console-log-to-file` | checkbox | T2 (`LOG_TO_FILE_PUT`) | C1-5 |
| Log viewport | `console-output` | output pane | T1 | C1-8 |
| App shell | `app-shell` | layout root `h-screen overflow-hidden` | T0 | C1-8 |
| Console panel | `console-panel` | complementary | T1 | C1-2–C1-5 |
| Panel header | `console-header` | chrome row | T0 | C1-3 |

G30: search input keeps `getG30Styles()`. Level is no longer a `<select>`.  
G31: level active uses `Button` `primary` (`bg-accent`) — no per-page accent fork.  
G33: class swap without width/height transition.  
G34: variants stay `primary|ghost|outline`.  
G35: no silent save except `LOG_TO_FILE_PUT` (T2, existing).  
E2: `E2E_CONTROL_CENSUS` must pass before Playwright.

### Plan-validation checklist (indexes absent; local substitute)

1. Every new/modified control is in the §4A table — pass by construction.  
2. Target Spec column substituted by Variant/size — pass.  
3. E2E written+wired with per-control census — required in task row 4.  
4–10. G30–G35 + E2 named above — required in ACs / census.

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| Transcript page | deferred | MEU-21 | grouping Session 9; matrix 6.3 |
| TTS + Model Manager page | deferred | MEU-22 | grouping Session 10; matrix 6.4 |
| Settings leaf PUT/Browse/theme/copy MCP/HelpCards | deferred | MEU-23 | Spec 897–1009; matrix 6.5 |
| `app.console_visible` startup toggle | deferred | MEU-23 | Spec 952, 1008 |
| Virtual scrolling 10k+ lines | deferred | MEU-23 | Spec 326; settings/console leaves |
| Color-coded-by-level log lines | out-of-scope | — | Human-approved 2026-08-20 supersedes Spec 317 for `console-output` |
| Invented ALL level button | out-of-scope | — | Human-approved literal: five dropdown values become five buttons |
| Hiding NavRail/Header on expand | out-of-scope | — | zorivest `TradesLayout.tsx` 450 hides the table only |
| Downloader page restyle | out-of-scope | — | MEU-20 approved; 06-gui Downloader section 352+ is not this project |
| FastAPI / MCP / OpenAPI regen | out-of-scope | — | no `packages/api/` or `mcp-server/` edits; G8 `--check` only |
| SSE console transport | out-of-scope | — | Spec 329–337 locked no-SSE |
| MEU-21–25 implementation | out-of-scope | — | `current-focus.md`; grouping Sessions 9–12 |
| Reopening MEU-26 as unapproved | out-of-scope | — | MEU-26 status `approved`; this plan owns `SUPERSEDED_26` replacements |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: register MEU-27, add Session 8c plan slash on phase 6, keep `HUB_NEXT_AFTER` = `/create-plan p6-gui-transcript`. Do not hand-edit AUTOGEN tables — `meu_status.py render`.

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern 'p6-gui-console-polish'); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
```

---

## Verification Plan

### 1. UI MEU-scoped gate
```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx tsc --noEmit; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx vitest run --allowOnly=false; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npx eslint src/ tests/ --max-warnings 0; if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }; npm run build; exit $LASTEXITCODE } *> C:/Temp/av-kit/ui-verify.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ui-verify.txt | Select-Object -Last 40; exit $code
```

### 2. Python regression (carry-forward)
```powershell
rtk proxy uv run pytest tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py tests/e2e tests/integration/test_api_wiring.py tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p6-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p6-regression.txt | Select-Object -Last 40; exit $code
```

### 3. OpenAPI no-drift
```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

---

## Open Questions

Resolved before review. No Human-decision-required item remains.

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| Collapse action | Unmount pane | MEU-26 AC-26.8; spec 324 | Matches current tests | Contradicts zorivest + user screenshot | ❌ |
| | Restore 40% drawer | zorivest `onToggleExpand`; Human 2026-08-20 | Matches requested mechanic | Requires `SUPERSEDED_26` | ✅ |
| Level widget | Keep dropdown + threshold | Spec 316 | Less churn | User asked for buttons + “only DEBUG” | ❌ |
| | Exclusive exact buttons, 5 values | G21; Human 2026-08-20 | Direct select; no invented ALL | Default DEBUG hides INFO until click | ✅ |
| | Exclusive + invented ALL | DevTools “All levels” | First paint shows everything | Sixth control not in the dropdown | ❌ |
| Output color | Color-by-level | Spec 317 | Spec-faithful | Contradicts “console green” | ❌ |
| | Black / `#33ff00` viewport | Human 2026-08-20; VGA green | Reads as a console | Supersedes per-level colors | ✅ |
| Expand chrome | Two always-visible text links in toolbar | MEU-26 live | Current code | User: wrong location, missing icons | ❌ |
| | Header-left single toggle + lucide | zorivest 303–324 | Matches Trade | Testid swaps with state | ✅ |

---

## Research References

- [MD3 Side sheets](https://m3.material.io/components/side-sheets) (standard supporting pane; expand fills the remaining row)
- [MDN ARIA radio group](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/radiogroup_role)
- [WAI-ARIA radio](https://www.w3.org/WAI/ARIA/apg/patterns/radio/)
- G21 exclusive segmented controls — `.agent/docs/emerging-standards.md`
- Zorivest: `TradeDetailPanel.tsx` 297–337, `TradesLayout.tsx` 448–627, `AppShell.tsx` 155–160
- av-kit: `06-gui.md` 308–327; MEU-26 plan + `ConsolePanel.tsx` / `AppShell.tsx`

---

## 2026-08-27 USER_EXPLICIT closeout addendum

Mat directed `proceed with 8c` after Sessions 9–18 independently approved MEU-21–39 under their own Codex-approved plans. This addendum does **not** reopen AC-27.1–27.10.

**F1 isolation is superseded.** Do not restore a MEU-27-only tree. Do not delete Transcript/TTS/Settings/Distribution/Convert/Capture. Prove AC-27 on the current AppShell (later GUI MEUs present). Exec r3 must not demand Hub Next `` `/create-plan p6-gui-transcript` `` or MEU-21 `pending`.

H2 grouping/hub use the named-set values above (`GROUPING_DONE_MARK`, `HUB_NEXT_AFTER`). Session 8c ✅ complete; Sessions 9–18 stay ✅ complete.
