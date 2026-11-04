---
project: "2026-08-20-p6-gui-zorivest-chrome"
date: "2026-08-20"
source: "docs/build-plan/06-gui.md"
meus: ["MEU-26"]
status: "draft"
template_version: "2.0"
---

# Implementation Plan: Phase 6 GUI Zorivest Chrome

> **Project**: `2026-08-20-p6-gui-zorivest-chrome`
> **Build Plan Section(s)**: [06-gui.md](../../../build-plan/06-gui.md) §Main Window Layout + §Console Panel + §Settings Page (chrome only)
> **Status**: `draft`
> **Grouping**: insert Session **8b** after Session 8 (`p6-gui-downloader`). Do not start MEU-21–25.

---

## Goal

Copy Zorivest desktop chrome into av-kit: Dracula token set (minus trading P&L), left-rail organization (primary routes top; Settings + Collapse pinned bottom), header breadcrumb with a **Console** button immediately left of **Settings: Ctrl+K**, and a right-side console drawer that opens like Zorivest `TradeDetailPanel` (40% / expand-to-full / close). Amend `06-gui.md` so the written spec matches this Human-approved placement. Do not implement Transcript/TTS pages, Settings leaf writes, or FastAPI/MCP changes.

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
| MEU-26 | `.agent/context/handoffs/2026-08-20-p6-gui-zorivest-chrome-MEU-26-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-20-p6-gui-zorivest-chrome-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB`. Expected count is named set `HANDOFF_COUNT`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-26a | Register `MEU-26` in YAML/matrix/grouping (`MEU26_ROW`). Do not start MEU-21–25. | — | `shared` | `.agent/context/meu-status.yaml` |
| WP-26b | Red: AC-26.1–26.18 UI tests **before** chrome production (`RED_TEST_TITLE` + `RED_AC_IDS` + `RED_JSON`). Include `SUPERSEDED_19` replacements. Receipt must pass `RED_ORACLE_CHECK` (kind `ui`) — 18 distinct failed JSON tests. | WP-26a | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-26-ui.txt`; `RED_JSON` |
| WP-26c | Green: tokens, Button, Header, NavRail, Console drawer, Settings chrome, G11 owner, persist/poll. Do not neutralize tests. Do not edit FastAPI/MCP. | WP-26b | `compact_continue` | `PAGE_FILES`; compact then re-read `task.md` |
| WP-26d | Wave-console E2E **written and wired** (`E2E_CASES` + `E2E_PER_CONTROL` + `E2E_CASE_ORACLES` + `E2E_CONTROL_CENSUS`). Run or `[B]` `E2E_SANDBOX`. | WP-26c | `compact_continue` | `ui/tests/e2e/console-chrome.test.ts`; `C:/Temp/av-kit/e2e-chrome.txt` |
| WP-26e | Amend `06-gui.md` ASCII 248–253, section 308–327 (heading/prose/height persist), tokens/rail, and `gui-actions-index.md` console rows including `console:collapse` semantic (no `Dock toggle`). Prove `SPEC_AMEND_MARKERS`. | WP-26d | `shared` | `docs/build-plan/06-gui.md`; `docs/build-plan/gui-actions-index.md` |
| WP-26f | `MEU_SCOPED_GATE` after `HANDOFF_SOURCE_READ`, then canonical handoff | WP-26e | `compact_continue` | `.agent/context/handoffs/2026-08-20-p6-gui-zorivest-chrome-MEU-26-handoff.md` |
| WP-26g | Hub + SSOT: bind MEU-26; keep prior plan slashes; `HUB_NEXT_AFTER` stays transcript. Grouping Session 8b → complete is **H2 after exec `approved`**. | WP-26f | `shared` | `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms; do not invent a third behavior):

1. **Harness gate:** `create-plan.md` §5c Cursor-default `plan_to_exec_gate=human` vs `.agent/context/harness.local.md` `reviewer-auto`. **Override wins.** After Codex `approved`, auto-continue to execution.
2. **Session pathway:** `current-focus.md` says next is `/create-plan p6-gui-transcript` and “Do not start MEU-21–25.” This project is **not** MEU-21–25. It is a Human-approved chrome insert (`USER_EXPLICIT` 2026-08-20). `HUB_NEXT_AFTER` remains `/create-plan p6-gui-transcript`.
3. **Console placement:** Spec 06-gui 248–253 / 308–327 is a **bottom dock** with `ui.panel.console.height`. Human asked for a right drawer like Zorivest Trade. **Lock `CONSOLE_SIDE_SHEET`.** Amend those spec lines in WP-26e. This is contract supersession, not G36 neutralization (`SUPERSEDED_19` + wave5 always-visible E2E).
4. **Tokens:** Spec 222 (`#1a1b26`) and 271 (purple `#bd93f9` accent bar) vs live Zorivest `globals.css` (`--color-bg: #282a36`, `--color-accent: #8be9fd`). Human: copy Zorivest CSS look. **Lock `TOKEN_SET`.** Trading `--color-pnl-*` stay out of scope.
5. **Width animation:** Zorivest `.nav-rail` animates `width`/`min-width` (150ms). G33 forbids geometry transitions. **Lock `RAIL_SNAP`:** copy 200/56 end-states; no width/min-width/height transition.
6. **Default visibility:** Spec `app.console_visible` default `true` (startup). Trade drawer is closed until click. Human: “open … like Trade opens when it is clicked.” **Lock `CONSOLE_DEFAULT_CLOSED`.** `app.console_visible` startup toggle remains MEU-23.
7. **4A indexes:** `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `.agent/docs/gui-standards-enforcement.md` remain **absent** (same as MEU-20). The §4A table below is the mapping. Apply G30–G35 + `gui-actions-index.md`.
8. **MEU ID:** Grouping said “Do not invent MEU IDs” for Sessions 9–12 (MEU-21–25). C2 forbids unowned product work. **Lock `MEU26_ROW`.** Do not reopen approved MEU-19.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `MEU26_ROW` | YAML MEU: `id: MEU-26`, `slug: gui-chrome-zorivest`, `phase: '6'`, `band: P2`, `matrix_item: '6.2a'`, `depends_on: [MEU-19, MEU-20]`, `build_ref.path: build-plan/06-gui.md`, `build_ref.anchor: main-window-layout`, status `pending` until H1-3 | C2; this plan |
| `TOKEN_SET` | Copy Zorivest `ui/src/renderer/src/globals.css` `@theme` + `:root:not(.dark)` + motion/easing + reduced-motion + `.nav-rail` / `.header-breadcrumb` / `.outline-btn` rules. **Omit** `--color-pnl-*`, `--color-status-filled/canceled/rejected`, trading-only files. Keep `--color-bg: #282a36`, `--color-accent: #8be9fd`, `--color-bg-subtle`, `--color-accent-ring`, `--duration-fast`, `--ease-out`, `--radius-control` | Human-approved; Local Canon `p:\zorivest\ui\src\renderer\src\globals.css` 3–96, 257–266, 479–530 |
| `LUCIDE_PIN` | `lucide-react: ^0.400.0` (zorivest `ui/package.json`) | Local Canon zorivest |
| `RAIL_EXPANDED_PX` | `200` | Zorivest `.nav-rail` |
| `RAIL_COLLAPSED_PX` | `56` | Zorivest `.nav-rail--collapsed` |
| `RAIL_SNAP` | rail width jumps between `RAIL_EXPANDED_PX` and `RAIL_COLLAPSED_PX`; CSS must not `transition` `width`, `min-width`, `height`, `top`, `left`, `margin`, or `box-shadow` | G33 |
| `SHELL_PRIMARY_NAV` | `{nav:downloader → `/` Ctrl+1, nav:transcript → `/transcript` Ctrl+2, nav:tts → `/tts` Ctrl+3}` rendered in a top `flex-1` group | Spec 263–265; zorivest `mainNavItems` |
| `SHELL_PINNED_NAV` | Settings (`nav:settings`, `/settings`, `Ctrl+,`) in `mt-auto` group; Collapse (`nav-collapse` / `nav-collapse-toggle`) below `border-t` | Spec 266–267; zorivest NavRail 104–131 |
| `HEADER_CLUSTER` | DOM order in header right cluster: `header-console-btn` then `header-palette-btn`. Palette visible text is `Settings: Ctrl+K` (not nav:settings) | Human-approved; zorivest `Header.tsx` 65–74 |
| `OPEN_PALETTE_EVENT` | `av-kit:open-palette` (existing) | MEU-19 |
| `TOGGLE_CONSOLE_EVENT` | `av-kit:toggle-console` | G11 |
| `CONSOLE_SIDE_SHEET` | standard (non-modal) right supporting pane; no scrim; no focus trap; `role="complementary"` `aria-label="Console"`; unmounted when closed | Human-approved; MD3 side sheets; WAI-ARIA complementary |
| `CONSOLE_DRAWER_GEOM` | closed: not mounted. Open: `w-[40%] min-w-[320px] max-w-[500px]`. Expanded: `w-full` and main content `hidden` | zorivest `TradesLayout.tsx` 450, 615 |
| `CONSOLE_DEFAULT_CLOSED` | first paint: panel absent. Persist last `ui.panel.console.visible` / `ui.panel.console.expanded` | Human-approved |
| `PERSIST_UI_KEYS` | `['ui.rail.collapsed', 'ui.panel.console.visible', 'ui.panel.console.expanded']` — **not** `ui.panel.console.height` | this plan lock 3/6 |
| `CONSOLE_POLL_OPEN_MS` | `500` | Spec 332 |
| `CONSOLE_POLL_CLOSED_MS` | `5000` | Spec 332 |
| `CONSOLE_LEVELS` | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` — exhaustive compile-time union | Spec 316 |
| `CONSOLE_CONTROLS` | `{console-panel, console-filter, console-search, console-clear, console-copy, console-collapse, console-expand, console-close, console-ytdlp-toggle, console-log-to-file}` | Spec 1104 + this plan |
| `CONSOLE_PALETTE_ID` | `console:toggle` — palette **yes**; action dispatches `TOGGLE_CONSOLE_EVENT` only (no fetch) | G11; `gui-actions-index.md` |
| `PALETTE_CONSOLE` | `AppShell` always-mounted listener is the production owner of `TOGGLE_CONSOLE_EVENT`. Header button, palette `CONSOLE_PALETTE_ID`, and Escape (when open) dispatch/handle the same event. Negative: listener only inside `ConsolePanel` ⇒ header click while closed is a no-op | G11 origin |
| `SETTINGS_CHROME_SECTIONS` | card roots: `settings-page`, `download-settings`, `transcript-settings`, `tts-settings`, `console-settings`, `appearance-settings`, `dependencies-section`. Headings only. **Zero** `PUT` / Browse / theme toggle / copy MCP | Spec 1103; MEU-23 owns leaves |
| `PAGE_FILES` | `styles.css`, `Button.tsx`, `SelectInput.tsx`, `AppShell.tsx`, `NavRail.tsx`, `Header.tsx`, `ConsolePanel.tsx`, `usePersistedState.ts`, `useBackendLogs.ts`, `commandRegistry.ts`, `router.tsx`, `features/settings/SettingsChrome.tsx` | this plan |
| `SUPERSEDED_19` | `persist-ui.test.ts` AC-19.18 height key; `app-shell-wiring.test.ts` always-visible `console-copy` + button text `Search`; `console-panel.test.ts` wave5 “panel is visible” on launch | this plan lock 3 |
| `E2E_WAVE` | `ui/tests/e2e/console-chrome.test.ts` (`E2E_CASES`, 6 tests) + `CONSOLE_CONTROLS` + header/rail/settings ids in `test-ids.ts` | E2; Spec 1104 |
| `E2E_CASES` | `C1-1` closed launch: same-expression `console-panel` `.toHaveCount(0)`; `C1-2` open → filter/search/clear/ytdlp visible; `C1-3` expand → `w-full` then restore `CONSOLE_DRAWER_GEOM`; `C1-4` close via X + collapse + Esc + header toggle, each path ending with a distinct `console-panel` `.toHaveCount(0)` (count ≥ 4); `C1-5` copy click + log-to-file click + `clipboard` and `settings/app` and `log_to_file`; `C1-6` `nav-collapse` click + `nav-rail--collapsed` + `SETTINGS_CHROME_SECTIONS` | E2 |
| `E2E_LOCATOR_FORM` | locators are literal `getByTestId('<kebab-id>')` (single quotes). Comments and `test-ids.ts` literals do not satisfy `E2E_CONTROL_CENSUS` | E2 |
| `E2E_PER_CONTROL` | allowed method chained on the same locator: `expect(page.getByTestId('id')).toBeVisible()` or `page.getByTestId('id').click()`. Closed-panel oracle is same-expression `console-panel` `.toHaveCount(0)` (Owner: `Get-BoundMatchCount` / `Test-HasBound`; C1-4 also `Assert-C14EachPathEndsAbsent`). A nearby method on an unrelated receiver is a fail. | E2 |
| `E2E_CASE_ORACLES` | Executable strings `assert-e2e-control-census.ps1` requires inside each titled case (comment-stripped): C1-1 same-expression `console-panel` `.toHaveCount(0)` (unrelated `toHaveCount(0)` does not count); C1-3 `w-full` and `min-w-[320px]`; C1-4 four close actions + ≥ 4 `Get-BoundMatchCount` + `Assert-C14EachPathEndsAbsent`; C1-5 `.click(` on copy and log-to-file plus `clipboard` and `settings/app` and `log_to_file`; C1-6 `nav-collapse` `.click(` plus `nav-rail--collapsed` | E2; r2 F1 |
| `SSOT_RENDER` | `rtk proxy uv run python tools/meu_status.py render` (no `--check`). Must run after the last pre-review YAML mutation and before `render --check`. `update` only `save()`s YAML; `--check` never regenerates Markdown | r1 F1; `meu_status.py` 129–156 |
| `SPEC_AMEND_MARKERS` | `06-gui.md` must contain `CONSOLE PANEL (right side sheet`, `Console Panel (Right Side Sheet)`, `dark background (`#282a36`)`, `accent bar (cyan `#8be9fd``, and `ui.panel.console.visible`; must not contain `CONSOLE PANEL (collapsible, bottom dock)`, `Console Panel (Bottom Dock)`, `docked to the bottom`, `ui.panel.console.height`, `dark background (`#1a1b26`)`, or `purple `#bd93f9`` (active-rail phrase; the status-legend `Purple (`#bd93f9`)` row is unrelated). `gui-actions-index.md` must contain `console:toggle`, `console:expand`, `console:close`, `console:collapse`, and `Side-sheet collapse`; must not contain `Dock toggle`. Row 5 owns ASCII 248–253 plus section 308–327 plus the collapse-row semantic. | r2 F2 |
| `E2E_CONTROL_CENSUS` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/assert-e2e-control-census.ps1` — executable owner of `E2E_CASE_ORACLES` + `E2E_PER_CONTROL` | E2; §4A.3 |
| `RED_AC_IDS` | `AC-26.1` … `AC-26.18` (18). Owner: `assert-red-oracle.ps1` ui kind + `RED_JSON` | FIC |
| `RED_TEST_TITLE` | every AC-26.N test is a **distinct** Vitest case whose `fullName`/`title` contains exactly one `AC-26.N` | FIC |
| `RED_JSON` | `C:/Temp/av-kit/fail-to-pass-meu-26-ui.json` from Vitest 3 `--reporter=json --outputFile` | Vitest 3 |
| `RED_ORACLE` | UI FAIL_TO_PASS text has allow-marker and no deny-marker **and** `RED_JSON` maps 18 distinct failed `assertionResults` 1:1 onto `RED_AC_IDS` (multi-id titles rejected) | r1 F2 carry-forward |
| `RED_ORACLE_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/assert-red-oracle.ps1 -Kind ui -Receipt <text> -JsonReceipt RED_JSON` | PR-9 |
| `BUILDER_PIN` | `—` while `fresh_worker: none` | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping |
| `GROUPING_DONE_MARK` | Progress-table row `\| 8b \| \`p6-gui-zorivest-chrome\` \| ✅ complete \|`; Sessions 9–12 stay `⬜ pending` | H2 only |
| `HANDOFF_COUNT` | `1` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-20-p6-gui-zorivest-chrome-MEU-26-handoff.md` | this plan |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/` | phase `"6"` |
| `PRIOR_PLAN_SLASH` | `docs/execution/plans/2026-08-20-p6-gui-downloader/` | must remain on phase `"6"` |
| `HUB_NEXT_AFTER` | `/create-plan p6-gui-transcript` | grouping Session 9 |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` | p6 pattern |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-20-p6-gui-zorivest-chrome-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — first YAML frontmatter only; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-26.txt` written **once** before the MEU-26 handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-20-p6-gui-zorivest-chrome/assert-handoff-markers.ps1` | PR-9 |
| `VITEST_ALLOW_ONLY` | every `npx vitest run` passes `--allowOnly=false` | G36 |
| `UI_ESLINT` | `npx eslint src/ tests/ --max-warnings 0` | G36 |
| `MEU26_TOUCHED` | `PAGE_FILES` + `ui/package.json` + unit tests for chrome + `SUPERSEDED_19` + `ui/tests/e2e/console-chrome.test.ts` + `console-panel.test.ts` + `test-ids.ts` | this plan |
| `MEU_SCOPED_GATE` | `ui`: `npx tsc --noEmit` + `npx vitest run --allowOnly=false` + `UI_ESLINT` + `npm run build`; + `SCAN_PLACEHOLDER` + `SCAN_G36` + `HANDOFF_MARKER_CHECK` + AC-26.* | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` is **not** modified → `--check` still run as no-drift proof. `-o` forbidden unless FAIL | G8 |
| `REGRESSION_TESTS` | p6-gui-downloader H1-2 Python set (do not drop) | p6 carry-forward |
| `SCAN_G36_ARGS` | skip/only/todo markers under `ui/tests/unit` + `ui/tests/e2e` | G36 |
| `SCAN_PLACEHOLDER_ARGS` | `TODO`, `FIXME`, `NotImplementedError` under `ui/src` | anti-placeholder |
| `E2E_SANDBOX` | un-run E2E in agent sandbox → `[B]` + CI follow-up. Tests stay written and wired | known-issue policy |
| `REFLECTION_TEMPLATE` | `docs/execution/reflections/TEMPLATE.md` | closeout |
| `REFLECTION_SCHEMA` | `.agent/schemas/reflection.v1.yaml` | closeout |
| `REFLECTION_PEER_RULE` | newest `docs/execution/reflections/*-reflection.md` excluding `TEMPLATE.md` | AGENTS |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `LOG_TO_FILE_PUT` | existing `PUT /settings/app` body `{ log_to_file: boolean }` only; API `extra=forbid`; 422 on extras | MEU-15 / MEU-19 |

---

## Proposed Changes

### MEU-26 — `gui-chrome-zorivest`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-Input Error | Create/Update Parity | Source |
|---------|-------------|-------------------|--------------------|---------------------|----------------------|--------|
| Header / rail / drawer clicks | none (local UI) | boolean open/expanded | n/a | n/a | n/a | this plan |
| Console search / `CONSOLE_LEVELS` filter | local React state | `CONSOLE_LEVELS` union; search string | ignore unknown level by failing closed to `DEBUG` | n/a (no network) | n/a | Spec 316 |
| `ui.panel.console.visible` / `.expanded` / `ui.rail.collapsed` | `usePersistedState` + `PERSIST_UI_KEYS` | JSON boolean | reject unknown persist keys (only listed keys write) | fallback to `CONSOLE_DEFAULT_CLOSED` / rail expanded | persist is the write | this plan |
| `PUT /settings/app` `log_to_file` | existing API `SettingsPutIn` | boolean | `extra="forbid"` | 422 | same PUT | MEU-15; `LOG_TO_FILE_PUT` |
| Settings chrome cards | none this MEU | headings only | no body | no writes | n/a | `SETTINGS_CHROME_SECTIONS` |

No new REST or MCP write surface. No Zod/Pydantic owner is created for chrome geometry.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-26.1 | unit | `styles.css` contains `TOKEN_SET` keys (`--color-bg`, `--color-accent`, `--color-bg-subtle`, `--color-accent-ring`, `--duration-fast`, `--ease-out`, `--radius-control`) and does **not** define `--color-pnl-` | Human-approved; Local Canon zorivest `globals.css` | file still has `#1a1b26` as `--color-bg` or `--color-pnl-positive` |
| AC-26.2 | unit | `Button` supports `icon`, uses `rounded-[var(--radius-control)]`, `duration-[var(--duration-fast)]`, `focus-visible:shadow-[0_0_0_3px_var(--color-accent-ring)]`; variants stay `primary\|secondary\|outline\|ghost\|destructive` | Local Canon zorivest `Button.tsx`; G34 | ad-hoc `className="bg-accent text-fg px-2"` still used as the shell button primitive |
| AC-26.3 | integration | `NavRail` renders `SHELL_PRIMARY_NAV` then `SHELL_PINNED_NAV`; collapsed width `RAIL_COLLAPSED_PX`; expanded `RAIL_EXPANDED_PX`; CSS satisfies `RAIL_SNAP` | Spec 259–273; zorivest NavRail | Settings sits in the top list (not `mt-auto`) or CSS transitions `width` |
| AC-26.4 | integration | Header left is breadcrumb `av-kit` › current page; right palette control visible text includes `Settings:` and `Ctrl+K` (`header-palette-btn`) | Human-approved; zorivest `Header.tsx` | header still shows a `Search` label with no breadcrumb |
| AC-26.5 | integration | `header-console-btn` is the immediate previous element sibling of `header-palette-btn` | Human-approved | Console button is to the right of Ctrl+K or not in the header |
| AC-26.6 | integration | On first paint with empty persist, `console-panel` is not in the document. After toggle, panel mounts with `CONSOLE_DRAWER_GEOM` open classes | Human-approved; `CONSOLE_DEFAULT_CLOSED` | panel is in the DOM on launch (old bottom dock) |
| AC-26.7 | integration | `console-expand` toggles expanded: main `hidden` + panel `w-full`; second click restores `CONSOLE_DRAWER_GEOM` | zorivest Trade expand | expand only changes a label and leaves 40% width |
| AC-26.8 | integration | Open panel closes via `console-close`, `console-collapse`, header Console click, and `Escape` | Human-approved; MD3 close icon | only an in-panel “Collapse” hides lines but leaves the dock mounted |
| AC-26.9 | integration | `PALETTE_CONSOLE`: `AppShell` is the only production listener for `TOGGLE_CONSOLE_EVENT`; palette lists `CONSOLE_PALETTE_ID` | G11 | listener lives only in `ConsolePanel` (unmounted when closed) so header/palette no-op |
| AC-26.10 | integration | When open, `CONSOLE_CONTROLS` except expand/close already listed exist; `console-filter` is `SelectInput` / `getG30Styles()` theme-aware | Spec 314–323; G30 | raw `<select>` without G30 inline styles |
| AC-26.11 | unit | `useBackendLogs(open)` uses `CONSOLE_POLL_OPEN_MS` when `open===true` and `CONSOLE_POLL_CLOSED_MS` when `open===false` (fake timers) | Spec 332 | interval stays `500` while closed |
| AC-26.12 | unit | `PERSIST_UI_KEYS` equals the named set; `DEFAULT_CONSOLE_HEIGHT` removed; persist round-trip visible/expanded/rail | this plan lock 3 | `ui.panel.console.height` still listed (AC-19.18) |
| AC-26.13 | integration | `/settings` renders `SettingsChrome` with `SETTINGS_CHROME_SECTIONS`; no `fetch`/`apiFetch` from that module | Spec 899–955 chrome; MEU-23 leaves | Settings route still `LazyPlaceholder` “Connecting to backend…” |
| AC-26.14 | unit | `PAGE_FILES` `className` strings contain no raw `#` hex (G32). G30 inline styles only inside `getG30Styles()` | G32 | `className="bg-[#282a36]"` |
| AC-26.15 | unit | Open `console-panel` has `role="complementary"` and must not have `role="dialog"` | Research-backed MD3 standard side sheet; WAI-ARIA complementary | `role="dialog"` (implies modal pattern) |
| AC-26.16 | integration | Rail items and expand/collapse use `lucide-react` icons (`LUCIDE_PIN` in `ui/package.json`) | Local Canon zorivest NavRail | collapsed rail still uses first-letter text only with no icons |
| AC-26.17 | integration | `listPaletteIds()` contains `CONSOLE_PALETTE_ID`; `handleGlobalShortcut('Ctrl+K')` still returns `OPEN_PALETTE_EVENT` | Spec 283–292; G11 | palette omits console; Ctrl+K bound to console |
| AC-26.18 | integration | After open, Copy writes clipboard and Log-to-file issues `LOG_TO_FILE_PUT` (SUPERSEDE `app-shell-wiring` always-mounted copy) | MEU-19 carry-forward | copy/log-to-file only work if panel was mounted at boot |

#### Control binding (PR-8)

| AC | Observable | Traceable call chain | Negative oracle |
|----|------------|----------------------|-----------------|
| AC-26.9 | `console-panel` mount/unmount; `window` listener count for `TOGGLE_CONSOLE_EVENT` | `header-console-btn`/`getCommand('console:toggle').action` → `window.dispatchEvent(TOGGLE_CONSOLE_EVENT)` → `AppShell` `useEffect` listener → `setConsoleOpen` → conditional `<ConsolePanel>` | If the only `addEventListener(TOGGLE_CONSOLE_EVENT)` is inside `ConsolePanel`, dispatch while closed appends **zero** panels (queryByTestId null) |
| AC-26.11 | `setInterval` delay captured via fake timers / injected scheduler | `AppShell` passes `consoleOpen` into `useBackendLogs(open)` → `setInterval(..., open ? CONSOLE_POLL_OPEN_MS : CONSOLE_POLL_CLOSED_MS)` → `GET /health/console?after_seq=` | Closed + interval `500` ⇒ fail (same cadence as open) |
| AC-26.12 | `PERSIST_UI_KEYS` array + `localStorage` JSON | `usePersistedState('ui.panel.console.visible')` → `writePersisted` → `setItem` (single statement; no read-then-write transaction) | `PERSIST_UI_KEYS` still includes `ui.panel.console.height` |
| AC-26.15 | `console-panel.getAttribute('role')` | `ConsolePanel` root `<section role="complementary">` rendered from `AppShell` | `role="dialog"` |
| AC-26.6 | `document.querySelector('[data-testid=console-panel]')` | persist read → `AppShell` `consoleOpen` → mount | panel present on first paint with empty storage |
| `LOG_TO_FILE_PUT` | fetch URL + JSON body | checkbox → `putLogToFile` → `apiFetch('/settings/app', { PUT, { log_to_file } })` | extra field in body accepted (API extra=forbid is the server oracle; UI sends only that key) |

`CONSOLE_LEVELS` is a closed set owned by this plan: adding a level without updating the union must fail typecheck. Unrecognized persisted filter string fails closed to `DEBUG`.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Right-side console vs bottom dock | Human-approved | User 2026-08-20 + screenshot; amend Spec 248–253, 308–327 |
| Drawer geometry 40%/320–500/full | Local Canon | zorivest `TradesLayout.tsx` 450, 615 |
| Standard side sheet (not modal) | Research-backed | [MD3 side sheets](https://m3.material.io/components/side-sheets); [MD3 supporting pane](https://m3.material.io/foundations/layout/canonical-examples/supporting-pane) |
| `role="complementary"` | Research-backed | WAI-ARIA complementary for supporting panes; avoid APG modal dialog ([MDN dialog](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/dialog_role)) |
| Tokens / accent cyan | Human-approved | overrides Spec 222, 271 |
| Rail Settings + Collapse pin | Spec + Local Canon | Spec 266–268; zorivest NavRail 104–131 |
| No width animation | Local Canon | G33 |
| Default closed | Human-approved | overrides `app.console_visible` default until MEU-23 |
| Settings leaf fields | Spec | deferred MEU-23; chrome cards only |
| Console transport / redact / seq | Spec | unchanged MEU-19 |
| Header Console left of Ctrl+K | Human-approved | user 2026-08-20 |
| G11 console toggle | Local Canon | G11 |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/src/renderer/src/styles.css` | modify | `TOKEN_SET` + rail/header/outline CSS |
| `ui/src/renderer/src/components/ui/Button.tsx` | modify | zorivest Button mechanics |
| `ui/src/renderer/src/components/ui/SelectInput.tsx` | new | G30 `getG30Styles` + SelectInput |
| `ui/src/renderer/src/components/layout/Header.tsx` | new | breadcrumb + `HEADER_CLUSTER` |
| `ui/src/renderer/src/components/layout/NavRail.tsx` | modify | `SHELL_PRIMARY_NAV` + `SHELL_PINNED_NAV` + lucide |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modify | Header, drawer slot, `PALETTE_CONSOLE` |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modify | `CONSOLE_SIDE_SHEET` chrome |
| `ui/src/renderer/src/hooks/usePersistedState.ts` | modify | `PERSIST_UI_KEYS` |
| `ui/src/renderer/src/hooks/useBackendLogs.ts` | modify | poll cadence from `open` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modify | `CONSOLE_PALETTE_ID` |
| `ui/src/renderer/src/features/settings/SettingsChrome.tsx` | new | `SETTINGS_CHROME_SECTIONS` |
| `ui/src/renderer/src/router.tsx` | modify | settings → `SettingsChrome` |
| `ui/package.json` | modify | `LUCIDE_PIN` |
| `ui/tests/unit/*` chrome + `SUPERSEDED_19` | modify/new | AC-26.* |
| `ui/tests/e2e/test-ids.ts` | modify | header/expand/close/settings cards |
| `ui/tests/e2e/console-chrome.test.ts` | new | `E2E_CASES` |
| `ui/tests/e2e/console-panel.test.ts` | modify | SUPERSEDE always-visible |
| `docs/build-plan/06-gui.md` | modify | console/token/rail ASCII |
| `docs/build-plan/gui-actions-index.md` | modify | `console:toggle` / expand / close |
| `docs/build-plan/build-priority-matrix.md` | modify | row `6.2a` MEU-26 |
| `.agent/context/meu-status.yaml` | modify | `MEU26_ROW`; P2 range MEU-14–26 |
| `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | modify | Session 8b row |

---

## create-plan §4A — GUI Element Compliance

Indexes absent. Mapping below is the Target Spec substitute.

| Element | testid | Variant / size / states | Feedback | E2E case |
|---------|--------|-------------------------|----------|----------|
| Console open | `header-console-btn` | `Button` ghost / sm / default+hover+focus | T1 | C1-1, C1-2 |
| Palette trigger | `header-palette-btn` | `Button` ghost / sm | T1 | C1-1 |
| Expand | `console-expand` | `Button` ghost / sm / `aria-expanded` | T1 | C1-3 |
| Close X | `console-close` | `Button` outline / sm / `icon` | T1 | C1-4 |
| Collapse (close) | `console-collapse` | `Button` ghost / sm | T1 | C1-4 |
| Clear | `console-clear` | `Button` outline / sm | T1 | C1-2 |
| Copy | `console-copy` | `Button` primary / sm | T1 | C1-5 |
| Level filter | `console-filter` | `SelectInput` + G30 | T0 | C1-2 |
| Search | `console-search` | text input, token classes | T0 | C1-2 |
| yt-dlp toggle | `console-ytdlp-toggle` | checkbox | T1 | C1-2 |
| Log to file | `console-log-to-file` | checkbox | T2 (`LOG_TO_FILE_PUT`) | C1-5 |
| Rail collapse | `nav-collapse` | `Button` ghost / sm / `aria-expanded` | T1 | C1-6 |
| Rail Settings | `nav-settings` | ghost link / sm / `aria-current` | T1 | C1-6 |
| Settings cards | `SETTINGS_CHROME_SECTIONS` | output cards (non-interactive headings) | T0 | C1-6 |
| Console panel | `console-panel` | complementary output | T1 | C1-2–C1-5 |

G31: all buttons use `bg-accent` via `Button` variants — no per-page accent forks.  
G33: `RAIL_SNAP`; drawer class swap without width transition.  
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
| Settings leaf PUT/Browse/theme/copy MCP/HelpCards/full action audit | deferred | MEU-23 | Spec 897–1009; matrix 6.5; grouping Session 11 |
| `app.console_visible` startup toggle | deferred | MEU-23 | Spec 952, 1008 |
| Downloader page restyle beyond inherited tokens | out-of-scope | — | MEU-20 approved; 06-gui Downloader section 352+ is not this project |
| Trading `--color-pnl-*` tokens | out-of-scope | — | zorivest trading domain; av-kit `AGENTS.md` §Project Context is YouTube media, not trading |
| StatusFooter / P&L widget / Import dialog | out-of-scope | — | zorivest-only; omitted from 06-gui av-kit shell ASCII 225–256 |
| FastAPI / MCP / OpenAPI regen | out-of-scope | — | no `packages/api/` or `mcp-server/` edits; G8 `--check` only |
| SSE console transport | out-of-scope | — | Spec 329–337 locked no-SSE; grouping named deferral |
| Copying zorivest width transitions | out-of-scope | — | G33 |
| MEU-21–25 implementation | out-of-scope | — | `current-focus.md`; grouping Sessions 9–12 |

---

## BUILD_PLAN.md Audit

This project **does** update the hub: register MEU-26, add Session 8b plan slash on phase 6, keep `HUB_NEXT_AFTER` = `/create-plan p6-gui-transcript`. Do not hand-edit AUTOGEN tables — `meu_status.py render`.

```powershell
rtk proxy pwsh -NoProfile -Command { $matches=@(Select-String -Path docs/BUILD_PLAN.md -Pattern 'p6-gui-zorivest-chrome'); [pscustomobject]@{matches=$matches.Count; lines=@($matches.LineNumber)} | ConvertTo-Json -Depth 3 } *> C:/Temp/av-kit/build-plan-audit.json; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/build-plan-audit.json; exit $code
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
| Console placement | Bottom dock | Spec 06-gui 308–327 | Matches current MEU-19 | Contradicts USER_EXPLICIT | ❌ |
| | Right standard side sheet | [MD3 side sheets](https://m3.material.io/components/side-sheets); zorivest Trade | Matches user + supporting-pane pattern | Requires spec amend | ✅ |
| MEU identity | Reopen MEU-19 | grouping “don’t invent IDs” | No new row | Pollutes approved MEU | ❌ |
| | `meus: []` | create-plan non-product shape | Avoids YAML | Product GUI with FIC | ❌ |
| | Register MEU-26 | C2; this plan | Owned product work | Extra SSOT row | ✅ |
| Default open | `app.console_visible=true` | Spec 1008 | Spec-faithful | Covers 40% of Downloader | ❌ |
| | Closed until click | zorivest Trade; user | Matches requested mechanic | Startup toggle waits for MEU-23 | ✅ |

---

## Research References

- [MD3 Side sheets](https://m3.material.io/components/side-sheets)
- [MD3 Supporting pane](https://m3.material.io/foundations/layout/canonical-examples/supporting-pane)
- [NN/g Bottom sheets](https://www.nngroup.com/articles/bottom-sheet/) (bottom sheet is the rejected mobile/transient pattern)
- [MDN ARIA dialog](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Reference/Roles/dialog_role)
- Zorivest: `AppShell.tsx`, `Header.tsx`, `NavRail.tsx`, `TradeDetailPanel.tsx` 297–337, `TradesLayout.tsx` 448–627, `globals.css`, `Button.tsx`
- av-kit: `06-gui.md` 220–337, 897–955, 1098–1106; MEU-19/20 handoffs
