---
project: "2026-11-08-light-accent-contrast"
date: "2026-11-08"
source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md#session-56--light-accent-contrast-meu-126--p2-band-issue-p4"
grouping_source: ".agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md"
meus: ["MEU-126"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Light accent labels read at 4.5:1 (Session 56)

> **Project:** `2026-11-08-light-accent-contrast`
> **Build plan:** `docs/build-plan/06-gui.md` §Light accent contrast (residual) (`:1608-1619`, anchor `light-accent-contrast-residual`, MEU-126).
>
> **Source request,** Mat's Session 56 brief, 2026-11-08. One MEU closes `LIGHT-ACCENT-BELOW-AA-CONTRAST` (P4, TECH-DEBT, Mat's triage ruling D-235) and carries grouping D-249. It has no riders. Done means "in the light theme, white labels on the accent and accent labels on their tint read at 4.5:1 or more, by a test that reads the shipped token values; the dark theme is unchanged; I have looked at the light theme and said yes, quoted in the handoff."
> **Known issue:** `LIGHT-ACCENT-BELOW-AA-CONTRAST` (D-235).
> **Status:** `draft`. `plan_to_exec_gate: human`, so nothing runs until Mat says so after the plan review.
>
> Line anchors are from `main` `f69ee08`, read 2026-11-08. `P:/av-kit` is the only worktree (`git worktree list`, one line). The tree holds another session's uncommitted capture-crop planning (Sessions 58 to 61, MEU-128 to MEU-132): `.agent/context/meu-registry.md`, `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `docs/build-plan/09-screenshot-capture.md` and `docs/build-plan/build-priority-matrix.md` are modified, and `.agent/context/grouping/2026-11-08-capture-crop-session-grouping.md`, `.agent/context/handoffs/2026-11-08-capture-region-import-plan-critical-review.md`, `_inspiration/capture-crop/` and `docs/execution/plans/2026-11-08-capture-region-import/` are untracked. This session leaves them alone, records each with its SHA-256 at row 0, and names them to Mat before any commit. That session's ids reach D-426 and MEU-132, so this plan's decisions start at D-450. During the second plan review, that session committed the five modified files, the grouping and `_inspiration/capture-crop/` as `7561737`. Their bytes are the ones these anchors were read from, so no cite moved. Row 0 baselines on that HEAD, and its plan folder and review handoff are still untracked.

## Goal

**Goal anchor:** Session 56 sets the light theme's `--color-accent` to `#155e75` and `--color-accent-hover` to `#164e63`, the values Mat ruled in D-235. With them, white labels on the accent and accent labels on their 12%, 15% and 20% tints read at 4.5:1 or more. A unit test reads the shipped tokens from `styles.css` and computes each ratio, and an E2E proves the built app paints the ruled colours. The dark theme doesn't change. Mat looks at the light theme and says yes before the execution review.

Three things are wrong today:

1. **White button labels on the light accent read 3.68:1.** The primary button is `bg-accent text-accent-fg hover:bg-accent-hover` (`ui/src/renderer/src/components/ui/Button.tsx:15`). The light theme sets `--color-accent: #0891b2` (`ui/src/renderer/src/styles.css:97`) and `--color-accent-fg: #ffffff` (`:98`). Button labels are `text-sm` (sizes `sm` and `md`), so the 4.5:1 floor applies. The hover fill `#0e7490` (`:99`) reads 5.36:1 and already passes.
2. **Accent labels on their tint read 2.72:1 to 3.20:1.** The secondary button is `bg-accent/12 text-accent hover:bg-accent/20` (`Button.tsx:16`), and a selected segmented-control option is `bg-accent/15 text-accent` (`ui/src/renderer/src/components/ui/SegmentedControl.tsx:44`), whose group is `bg-surface-0` (`:22`). Today the secondary label reads 2.98:1 over the page's `#f5f6fa` and 3.20:1 over a white card, 2.72:1 and 2.90:1 on hover, and the selected option reads 3.09:1 (`C:/Temp/av-kit/s56/contrast-probe.txt`).
3. **No test measures these pairs.** The triage worked the figures out from the token values. `ui/tests/unit/chrome-zorivest.test.ts:21` pins only the dark accent, `queue-primitives.test.ts:583` pins the `var()` reference, and nothing checks what the running app paints in the light theme.

The session ends when the contract's tests and Done's three lines hold, the session gate passes, Mat has said yes to the light theme, and the issue is resolved in the register.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (ls: No such file or directory, 2026-11-08). No payload is oversized: the change is two lines of styles.css, one new unit test, one E2E test and 40 values in one JSON file, all read directly."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host. Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit`, named `s56-*`;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `ELECTRON_RUN_AS_NODE` is cleared;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s56\tmp` for the Python suite, because `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` is still open.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and any other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s56-plan-2026-11-08-light-accent-contrast` and `s56-execution-2026-11-08-light-accent-contrast`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Caps: plan 3 rounds, execution 6.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path, and the review-state receipt is rebuilt there (Session 49b D-290).
  - Reviewer prompts name the ledger vocabulary up front: D-450 to D-459, AC-126.1 to AC-126.10, AC-43.3 and the mechanism ids in §Single-statement contracts. They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json` or anything under `.agent/fleet/hub`, and they write `<HOME>` for the home folder. When they ask for `tested_state`, they name `~/.config/git/ignore` and the path it hides, `.claude/settings.local.json` (Session 51 RULE-4).
- **Never in these rows without Mat's words:** commit, push, a network request of any kind, a model, runtime, FFmpeg or Python package download, or an `approved` verdict authored by the implementer. This session makes no YouTube request, and nothing uploads, publishes or writes to YouTube.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-126 `gui-light-accent-contrast` | `.agent/context/handoffs/2026-11-08-light-accent-contrast-MEU-126-handoff.md` |

Rolling reviews: `.agent/context/handoffs/2026-11-08-light-accent-contrast-plan-critical-review.md` and `.agent/context/handoffs/2026-11-08-light-accent-contrast-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-1 | Baseline (row 0) | — | shared | `baseline.sha`, `baseline-dirty.txt`, base suite receipts, the matrix control |
| WP-2 | Red (rows 1, 2) | WP-1 | shared | The failing contrast test and E2E |
| WP-3 | Green (row 3) | WP-2 | shared | `LIGHT_ACCENT_TOKENS`, `MATRIX_REBASELINE` |
| WP-4 | Mat's look (row 4) | WP-3 | shared | `human-check.md` with Mat's words (D-458) |
| WP-5 | Records (row 5) | WP-4 | shared | Spec note, MEU status, register, renders, grouping tracker |
| WP-6 | Closeout (H1, H2) | WP-5 | `compact_continue` | Handoff, review, reflection, Session 57's prompt |

## User Review Required

> [!IMPORTANT]
> **Four things at this gate.** D-450 to D-454, D-456 and D-457 are autonomous and two-way, with their alternatives in §Decision Log. The gate asks Mat to accept the plan or override one of them, and also the four items below. On 2026-11-08, before the second plan review, Mat answered: "all recommendations accpeted, proceed". That chooses B for D-455, accepts D-459's routing, the D-456 amendment and the 15M execution budget. On this harness (`plan_to_exec_gate: human`), the reviewer's approval still goes to Mat, and execution starts on Mat's next message (`create-plan.md` §5c).
>
> **1. D-455: the TTS status pill. Mat chose B.** The ruled accent makes one more label worse, and it isn't one the brief names. The TTS page draws a job's status as `text-xs text-fg` on a solid fill (`ui/src/renderer/src/features/tts/TTSPage.tsx:721`, fills from `STATUS_COLORS`, `ui/src/renderer/src/features/tts/tts-controls.ts:14-21`). The Generating fill is `bg-accent`, so in the light theme its `#1e293b` label falls from 3.97:1 to 2.01:1. The pill already fails 4.5:1 for most statuses in both themes, the default dark one included (`C:/Temp/av-kit/s56-plan-tts-pill-dark.txt`, `C:/Temp/av-kit/s56/tts-pill-probe.txt`):
>
> | Status | Dark (`#f8f8f2` label) | Light (`#1e293b` label) |
> |---|---|---|
> | Idle, Cancelled | 4.41 | 5.71 |
> | Pending | 1.60 | 2.00 |
> | Generating | 1.30 | 3.97 today, 2.01 after this session |
> | Done | 1.29 | 4.44 |
> | Failed | 2.95 | 3.03 |
>
> No register issue covers the pill. The transcript feature's `STATUS_COLORS` (`transcript-controls.ts:41`) is exported but not rendered.
> - **B, keep the scope and file the pill (Recommended).** MEU-126 changes only the two ruled tokens. Row 5 files `TTS-STATUS-PILL-BELOW-AA-CONTRAST` (P3, severity low, component ui, TECH-DEBT, related to this issue and `QUEUE-PILL-TOKEN-DRIFT`) for the whole pill in both themes, with Mat's words as D-455's reference (`issue-file.py`, dry-run receipt `C:/Temp/av-kit/s56-plan-issue-file-dry.txt`). Fixing Generating alone leaves the pill failing in the default theme, and a whole-pill fix changes the TTS page in both themes, which D-235 didn't rule on.
> - **A, Generating's label uses `text-accent-fg`.** White on `#155e75` reads 7.27:1 in light and `#282a36` on `#8be9fd` reads well in dark. It fixes Generating only, and the class string already holds `text-fg`, so the two utilities compete by CSS order and `TTSPage.tsx:721` must be restructured. The plan gains a row, a test and a review round.
> - **A', Generating's fill becomes a 10% wash** (`bg-accent/10`, as the queue pills' detail backdrop). It fixes Generating in both themes and changes how the pill looks. Same cost as A.
> - **C, do nothing.** Ship the tokens and record nothing. Light Generating reads 2.01:1, and no issue says so.
>
> If Mat picks A or A', the plan is revised and goes back to the plan review before execution.
>
> **2. Test amendment, `MATRIX_REBASELINE` (D-456).** AC-43.3 (`ui/tests/unit/queue-primitives.test.ts:419-454`) recomputes the queue pills' contrast matrix from `styles.css` and requires it to equal `docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json`. Two of its backdrops are the accent over the page (`checkbox-selected` at 5%, `detail-open` at 10%), so the ruled accent moves exactly 40 light values: the label and icon ratios of all 10 statuses on those two backdrops. Every one falls slightly: labels from 11.46 to 11.24 at most and 10.19 to 9.91 at least, and the lowest icon, Cancelled on `detail-open`, from 3.94 to 3.8. `_meta` doesn't change: 80 pairings, 80 labels pass, the worst label is 6.61, 4 icons are below the advisory and the worst icon is 1.94. No assertion or test code changes. AGENTS.md (`:57`) asks for a source-backed amendment and explicit human authorization or independent review before a pinned expectation changes, so "proceed" at this gate is that authorization, and the execution review re-checks the values. Precedent: A-6, 16 values re-baselined the same way (`docs/execution/plans/2026-10-10-gui-polish-residuals/human-gate-decision.md:95-99`). Without it, AC-43.3 fails and the tokens can't ship.
>
> **3. Mat's look at the light theme, after the Green (row 4, D-458).** This is the brief's own Decision Brief, asked at row 4, not here:
> - **Recommendation:** Mat opens the dev app, launched detached, in the light theme and looks at the Downloader, Convert and Settings pages: a primary button, a secondary button and a segmented control. If Mat approves, the session goes on to the review.
> - **Do nothing:** keep `#0891b2`. The issue stays open at P4, and rc.2 doesn't wait for it (D-249).
> - **Mat's "no":** the hexes go back to Mat as a new decision, and nothing ships. Rows 1 to 3 stay as they are in the work tree (§3), and the session stops before records.
>
> **4. Budget.** Calibrated against Session 41 `gui-keyboard-palette` (plan 32.5M over 3 rounds, execution 6.1M in 1 round; this session matches its renderer part), Session 55 (plan 9.1M then 5.9M, execution 11.6M in 1 round with real-stack probes) and Session 54 (plan 8.5M in 1 round, execution 7.9M in 1 round). This session is smaller than any of them: expect 1 to 2 plan rounds (about 5M to 10M) and 1 to 2 execution rounds (about 6M to 12M; Session 55 RULE-4 puts a round with real-stack probes at about 12M). The plan loop opens with the default 10.5M. If round 1 costs more than 5.25M, the gate asks Mat for the execution loop's budget (Session 52 RULE-3); the recommendation is then 15M, one probing round and a recheck.
>
> The first plan dispatch, `s56-plan-r1`, cost about 6.14M (input 6,113,223, 5,924,224 of it cached; output 27,735; `C:/Temp/av-kit/dispatch/s56-plan-run-r1.txt`). The ledger refused to record it, because its F3 cites `PR-8`, which isn't in this loop's registered set, so the ledger shows 0 rounds and 0 tokens. Its three findings are fixed in this revision, under AC-126.9 and AC-126.10 (D-459). The real plan spend is that 6.14M plus every recorded round, and it passes 5.25M, so the gate asks for the execution budget: the recommendation is 15M, and Mat accepted it on 2026-11-08. The execution loop opens with `--token-budget 15000000`.
>
> **For H2-5, not this gate: the commit.** `meu-status.yaml`, `BUILD_PLAN.md` and `meu-registry.md` already hold the capture-crop session's uncommitted MEU-128 to MEU-132 lines, and row 5 writes MEU-126 into the same three files. Row 5 and H2-2 write them only through `status-write.py`, which holds all three from its first read to its last write, so a capture-crop write lands either before it, and is kept, or fails in that session (`GUARDED_STATUS_WRITE`, D-454). The commit tool stages whole files, so a commit made first would carry that session's lines too. H2-5 recommends that the capture-crop planning commit lands first and asks Mat before committing (D-454).
>
> **What the words in Done mean here, and the limits they leave.**
> - **"Their tint" is each tint the code draws:** 12% (secondary button), 20% (its hover) and 15% (selected segmented option). Each is checked over the page background `#f5f6fa` and over the white card or group surface (`TINT_MODEL`, D-451). A secondary button also sits on a selected queue card, whose 5% accent wash lies over the page (`CARD_STATE_CLASSES['checkbox-selected']`, `ui/src/renderer/src/components/queue/QueueCard.tsx:66`; the Retry button `:356`, drawn at `:604-606`; the Downloader passes the selection at `ui/src/renderer/src/features/downloader/DownloaderPage.tsx:887`), so the 12% and 20% tints are also checked over that wash. The one `bg-bg-subtle` fill is a 20% wash behind a rail label (`ui/src/renderer/src/features/settings/SettingsRail.tsx:253`), and no button sits on it.
> - **"Reads at 4.5:1" is the WCAG 2.2 ratio** of the label colour over the composited fill, unrounded (`CONTRAST_FLOOR`). The worst pair after the change is the secondary hover on a selected queue card, 4.62:1 (5.24:1 at rest); over the page alone it is 4.96:1. Rounding a composite channel by one step either way can't push any pair under 4.5 (`C:/Temp/av-kit/s56-plan-rounding-margin.txt`: worst 4.91 over plain surfaces; `C:/Temp/av-kit/s56-plan-selected-card.txt`: worst 4.54 on the selected card, moving the card's channels and the fill's).
> - **A detail-open queue card isn't reachable today.** Its 10% wash would put the secondary hover at 4.36:1, but no caller passes `detailOpenId` to `QueueList` (`ui/src/renderer/src/components/queue/QueueList.tsx:81`, `:217`), so no card is drawn in that state (§Out of Scope).
> - **"The dark theme is unchanged"** means the dark block's accent, accent-fg and hover keep `#8be9fd`, `#282a36` and `#a6f0ff`, and the light `--color-accent-fg` stays `#ffffff` (`DARK_UNCHANGED`). Only `styles.css:97` and `:99` change.
> - **Other uses of the light accent change colour too,** because they read the same token: focus rings (`--color-accent-ring` mixes `var(--color-accent)` at 35%, `:100`), borders, the 5% and 10% washes of the queue cards and the filmstrip, and checkbox fills. None of them carries a text label on the accent except the TTS pill (item 1). `--color-accent-cyan` is already `#155e75` (`:89`).
> - **`ui/tests/unit/fixtures/queue-slot-baseline.json` needs no re-baseline.** It names the token as `var(--color-accent)` 13 times and holds no hex (`C:/Temp/av-kit/s56/plan-callers.txt`). The 06 contract's "may need a re-baseline" (`:1618`) is answered no.
> - **Light is not the default theme** (`packages/core/src/avkit_core/services/settings.py:80`), so the change shows only to a user who picks it.

## Proposed Changes

### Single-statement contracts

| Term | Meaning |
|---|---|
| `LIGHT_ACCENT_TOKENS` | In `ui/src/renderer/src/styles.css`'s `:root:not(.dark)` block (`:82`), `--color-accent` is `#155e75` (`:97`) and `--color-accent-hover` is `#164e63` (`:99`). No other line of the file changes. |
| `CONTRAST_FLOOR` | Each label pair in the light theme reads at 4.5:1 or more by the WCAG 2.2 ratio, `(L1 + 0.05) / (L2 + 0.05)`, with relative luminance from sRGB channels linearised at the 0.04045 threshold and the ratio unrounded. |
| `TINT_MODEL` | `bg-accent/N` paints the accent at alpha N/100 over the opaque surface behind it, composited per channel in sRGB and rounded to 8 bits, half up. The tint's backdrop is the page `--color-bg`, the card and group surfaces `--color-bg-elevated` and `--color-surface-0`, or a selected queue card: its `checkbox-selected` wash, composited the same way over `--color-bg` first. |
| `DARK_UNCHANGED` | The dark block keeps `--color-accent: #8be9fd`, `--color-accent-fg: #282a36` and `--color-accent-hover: #a6f0ff`, and the light block keeps `--color-accent-fg: #ffffff`. |
| `RUNTIME_COLOURS` | In the built app the light theme paints the primary theme button at `rgb(21, 94, 117)` with an `rgb(255, 255, 255)` label, `rgb(22, 78, 99)` on hover, and the secondary button's and the selected segmented option's labels at `rgb(21, 94, 117)`. The dark theme paints them as before. |
| `MATRIX_REBASELINE` | `contrast-matrix.json` changes in exactly the 40 light values the ruled accent moves (label and icon, `checkbox-selected` and `detail-open`, all 10 statuses), written by `matrix-rebaseline.py` from AC-43.3's own algorithm. Every other byte, its CRLF endings and `_meta` stay as they are. |
| `NO_RAW_CONSOLE` | No log line is added or changed, and no plan-local script prints or writes a process's command line, arguments or executable path. |
| `LAUNCH_OWNERSHIP` | Row 4 counts a process as left over only when it belongs to the launch it recorded: the root pwsh, or a process whose parent belongs to the launch and that started no earlier than that parent, each matched by its id and creation time. The checker, the processes it runs under and the ones it starts, the avkit MCP servers and another worktree's app or backend never count, and only the launch's own processes are stopped. |
| `GUARDED_STATUS_WRITE` | Row 5 and H2-2 write `meu-status.yaml`, `BUILD_PLAN.md` and `meu-registry.md` only through `status-write.py`. It holds all three files from its first read to its last write, so another process's write in that interval fails in that process. It runs the status tool's own update and render on staged copies and refuses, writing nothing, any change outside MEU-126's entry and the two generated regions. Its `--verify` checks afterwards that MEU-126 still holds its status and that the renders match. |

### Tokens: `LIGHT_ACCENT_TOKENS` (D-235)

`ui/src/renderer/src/styles.css` (CRLF, 211 lines), in the light block:

```css
  --color-accent: #155e75;
  --color-accent-fg: #ffffff;
  --color-accent-hover: #164e63;
```

`:97` and `:99` change; `:98` and the ring at `:100` stay. The row replaces the two lines' bytes in place and checks the file is still 211 CRLF lines with no bare LF. The ruled values are `_inspiration/zorivest/globals.css:144,146`.

### The contrast unit test: `CONTRAST_FLOOR`, `TINT_MODEL`, `DARK_UNCHANGED` (D-450, D-451)

A new `ui/tests/unit/light-accent-contrast.test.ts` (LF), with `/** @vitest-environment jsdom */` as `queue-primitives.test.ts` and `queue-card.test.ts` have. It reads `styles.css` with `readFileSync` from the path `queue-primitives.test.ts` uses (`TOKEN_FILE`, `:55`), takes the `:root:not(.dark)` block and the dark block, and reads each token by name. It holds no copy of either ruled light value: every ratio comes from the file. For the selected queue card it imports `CARD_STATE_CLASSES` from `ui/src/renderer/src/components/queue/QueueCard.tsx` and reads the wash's alpha from the `bg-accent/N` class in `checkbox-selected`, throwing when there is none, so the test follows the class the card ships.

Its helpers are its own, after `queue-primitives.test.ts:203-251` (block parse, hex to RGB, `over`, luminance and ratio), with two differences. The luminance threshold is WCAG 2.2's 0.04045, which gives the same result as AC-43.3's 0.03928 for every 8-bit channel, and the ratio isn't rounded, so a pair at 4.496 fails. `over(top, alpha, backdrop)` rounds each channel half up, as `Math.round` does. Each helper throws when a token is missing or isn't a 6-digit hex, so a renamed token fails the test instead of passing it vacuously.

Why the tints are composites: the built CSS draws `.bg-accent\/12` as `color-mix(in oklab, var(--color-accent) 12%, transparent)`, with `/15` and `/20` the same (`ui/out/renderer/assets/index-BJyOr5xS.css`, `C:/Temp/av-kit/s56-plan-tint-css.txt`). Mixing a colour with `transparent` keeps its hue at that alpha, and the compositor blends it over the backdrop in sRGB. The hex fallback before each `color-mix` holds the dark accent and applies only where `color-mix` isn't supported, which isn't the case in Electron's Chromium.

### The E2E: `RUNTIME_COLOURS` (D-452)

`ui/tests/e2e/settings.test.ts` (CRLF) gains AC-126.8 after AC-94.7 (`:687-699`), with the same seam: `installSettingsSeam(page, {}, { themeProbe: { theme: { answer: 'dark' } } })`, then `openSettings(page)`. It reads three elements that already have test ids:

- `theme-dark-btn` and `theme-light-btn` (`ui/src/renderer/src/features/settings/SettingsPage.tsx:1098-1118`). The active theme's button is `primary` and the other `secondary`.
- The cookie-mode `file` option's label: `page.getByTestId('settings-leaf-cookie_mode-file').locator('xpath=..')`. The test id is on the radio input inside the label (`SegmentedControl.tsx:38-60`), and the seam's cookie mode is `file`, so that option is selected (`SettingsPage.tsx:653-667`).

Steps, each a `toHaveCSS` that polls past the 120 ms colour transition (`--duration-fast`, `styles.css:62`; `Button.tsx:31-32`):

1. **Dark, the positive control.** `theme-dark-btn` background `rgb(139, 233, 253)` and colour `rgb(40, 42, 54)`; `theme-light-btn` colour `rgb(139, 233, 253)`; the `file` label colour `rgb(139, 233, 253)`.
2. Click `theme-light-btn`, then `expectThemeColours(page, 'light', THEME_FLOORS.settings)`, then `page.mouse.move(0, 0)` so the pointer no longer rests on the button.
3. **Light.** `theme-light-btn` background `rgb(21, 94, 117)` and colour `rgb(255, 255, 255)`; `theme-dark-btn` colour `rgb(21, 94, 117)`; the `file` label colour `rgb(21, 94, 117)`.
4. **Hover.** `theme-light-btn.hover()`, then its background `rgb(22, 78, 99)`.
5. Click `theme-dark-btn`, move the pointer away, and repeat step 1.

It asserts no tint's computed value: Chromium serialises a `color-mix` result in its own colour space, not as the `rgb()` a test can compare. The tints' contrast is the unit test's. No test id is added (S9).

### The matrix: `MATRIX_REBASELINE` (D-456)

`docs/execution/plans/2026-11-08-light-accent-contrast/matrix-rebaseline.py` re-baselines `docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` (CRLF, 27,141 B, SHA-256 `e4e8ab278f0265f91756f7673467b5f289c8bac8347777db025f3974dd0f7d6b`). It replicates AC-43.3's algorithm: the WCAG 2.0 threshold 0.03928, and composites and ratios rounded half up as `Math.round`. It refuses unless:

- the values that move are exactly its 40 `EXPECTED_MOVES`;
- every label is at 4.5 or more;
- `_meta` still describes the matrix;
- AC-43.3's three negative controls still move it;
- the tokens in `styles.css` are the ruled ones;
- the file's SHA-256 equals `--expect-sha256`.

It then replaces only those 40 numbers in place. Its dry run on a copy wrote the 40 values with 0 problems (27,142 B, 1,138 CRLF, SHA-256 `9a66afa961852da71d02e8ae5468d87ef2ab86e07c382aedd682fd5a40b01b50`, `C:/Temp/av-kit/s56-plan-matrix-dry-run.txt`). Row 0's control (`--check-shipped`) proves the replica equals the pinned matrix from the shipped tokens before row 3 uses it (S8).

### Where values go (Session 50 RULE-1; D-450)

The change is two colour values in a stylesheet, one test file, one E2E test and 40 numbers in a test fixture. No log line, stdout line or Console field is added or changed, and no value from outside the app is read. Row 4's dev-app log goes to a receipt under `C:/Temp/av-kit`, not to a test or a record. Row 4's process check reads command lines only to tell an Electron process, the backend and an MCP server apart. It prints and records each process as its id, its parent's id, a fixed role and whether it is this launch's, because the backend's arguments carry `--token` and `--mcp-token` (`ui/src/main/python-manager.ts:23-30`) and an executable path can hold the home folder (`NO_RAW_CONSOLE`, AC-126.9; plan review round 1, F2). Session 53 RULE-1, Session 54 RULE-1 and RULE-2's HealthService order, and Session 55 RULE-3 have no target: no field carries outside text, no `packages/core/src` file changes, no real stack is built outside `wiring.py`, and nothing fans out.

### Spec text (D3)

| File | Lines | Change |
|---|---|---|
| `docs/build-plan/06-gui.md` | after `:1619`, before `## Validation Commands` (`:1621`) | A `> **Delivered (Session 56).**` note in Session 55's form (`:1597-1606`): the mechanism ids with the lines they hold, the answer to the Baseline row (`queue-slot-baseline.json` needed none; AC-43.3's matrix moved 40 values), Mat's words from row 4, AC-126.1 to AC-126.8 and this plan folder |

Row 5 re-reads the anchor before it writes (Session 51 RULE-3) and cites the lines as they read after row 3. `06-gui.md` is CRLF.

### MEU-126 `gui-light-accent-contrast`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Light theme tokens | `styles.css` `:root:not(.dark)` (`:82-110`) | 6-digit hex; `--color-accent` and `--color-accent-hover` are D-235's | The block's other tokens unchanged |
| Dark theme tokens | `styles.css` dark block (`:44-46`) | Unchanged (`DARK_UNCHANGED`) | — |
| `bg-accent/N` tints | Tailwind's compiled CSS | `color-mix(in oklab, var(--color-accent) N%, transparent)` | — |
| Primary and secondary button | `Button.tsx:15-16` (unchanged) | `text-sm` labels at sizes `sm` and `md` | — |
| Selected segmented option | `SegmentedControl.tsx:44` (unchanged) | `text-sm` label on `bg-accent/15` over `bg-surface-0` | — |
| AC-43.3 matrix | `contrast-matrix.json` | Ratios to 2 dp; `_meta` unchanged | Only the 40 `EXPECTED_MOVES` change |

#### Acceptance Criteria

Vitest titles start `AC-126.<n>`. AC-126.1 to AC-126.7 go in the new `ui/tests/unit/light-accent-contrast.test.ts`, and AC-126.8 in `ui/tests/e2e/settings.test.ts`. AC-126.9 and AC-126.10 are the contracts of row 4's and rows 5 and H2-2's plan-local scripts, added after plan review round 1's F1 to F3 (D-459). Each script's selftest and real-stack control prove them, at plan time and again in row 0, and each row's own validation runs them on the real files. "Over X" names the opaque backdrop the tint is composited on.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-126.1 | unit (UI) | `--color-accent-fg` on `--color-accent`, both read from the light block, is at 4.5:1 or more | Human-approved: D-235; Local Canon: 06 `:1619` | Yes: Red, 3.68 |
| AC-126.2 | unit (UI) | `--color-accent-fg` on `--color-accent-hover` is at 4.5:1 or more | Human-approved: D-235 | Guard: passes in Red (5.36) |
| AC-126.3 | unit (UI) | `--color-accent` on the accent at 12% over `--color-bg`, over `--color-bg-elevated`, and over a selected queue card (the `checkbox-selected` wash read from `CARD_STATE_CLASSES`, over `--color-bg`) is at 4.5:1 or more | Local Canon: 06 `:1619` ("over the page background"); `Button.tsx:16`; `QueueCard.tsx:66`, `:356` | Yes: Red, 2.98, 3.20 and 2.82 |
| AC-126.4 | unit (UI) | The same at 20% (the secondary hover) over each backdrop | Local Canon: `Button.tsx:16`; `QueueCard.tsx:66` | Yes: Red, 2.72, 2.90 and 2.59 |
| AC-126.5 | unit (UI) | `--color-accent` on the accent at 15% over `--color-surface-0`, and over `--color-bg`, is at 4.5:1 or more | Local Canon: `SegmentedControl.tsx:22`, `:44` | Yes: Red, 3.09 and 2.87 |
| AC-126.6 | unit (UI) | `--color-accent` as plain text on `--color-bg` and on `--color-bg-elevated` is at 4.5:1 or more | Local Canon: `text-accent` (`ui/src/renderer/src/components/queue/BulkActionBar.tsx:65`) | Yes: Red, 3.41 and 3.68 |
| AC-126.7 | unit (UI) | `DARK_UNCHANGED`: the dark block's `--color-accent`, `--color-accent-fg` and `--color-accent-hover` are `#8be9fd`, `#282a36` and `#a6f0ff`, and the light `--color-accent-fg` is `#ffffff`. The ratio helper gives 21 for `#000000` on `#ffffff`, and between 4.54 and 4.55 for `#767676` on `#ffffff`, the positive control | Human-approved: D-235 ("the dark values don't change") | Guard: passes in Red and Green |
| AC-126.8 | e2e | `RUNTIME_COLOURS`: in the built app, the steps in §The E2E. Dark first as the positive control, then light, the hover, and dark again | Local Canon: the issue's "not measured in the running app"; AC-94.7 (`settings.test.ts:687-699`) | Yes: Red, `rgb(8, 145, 178)` |
| AC-126.9 | plan-local script | `LAUNCH_OWNERSHIP` and `NO_RAW_CONSOLE` for row 4: `dev-app-procs.py check` exits 0 once the recorded launch has quit and 1 while any of its processes, an orphan included, is still running. It never counts the checker or its hosts, whatever their arguments hold, an MCP server, a reused process id or another worktree's app or backend, and its output and record hold no argument, token or path | Human-approved: Mat's brief ("stop only its own processes, filtered by path, never by name"); Local Canon: `PROJECT-PROFILE.md:78` (E5); plan review round 1, F1 and F2 | Yes: the selftest's leftover, orphan and leak cases, and the real-stack control's leftover run, which exits 1 |
| AC-126.10 | plan-local script | `GUARDED_STATUS_WRITE` for rows 5 and H2-2: a capture-crop write that lands before `status-write.py` holds the files is kept, one made while it holds them fails in the writer, a change outside MEU-126's entry and the generated regions is refused with nothing written, and `--verify` exits 1 when a later stale save drops MEU-126's status | Human-approved: Mat's brief (record each capture-crop path and leave it alone); Local Canon: Session 55 RULE-2; D-454; plan review round 1, F3 | Yes: the selftest's positive control, in which the unguarded tool loses an interleaved write, and its refused-change and stale-save cases |
| AC-43.3 | unit (UI), amended data | The queue pill matrix, recomputed from `styles.css`, equals `contrast-matrix.json` after `MATRIX_REBASELINE` | Local Canon: MEU-43; D-456 (TEST_AMENDMENTS) | Unchanged test; its data changes in row 3 |

Guards that run unchanged in row 3, each a test that reads `styles.css` or names an accent token (Session 55 RULE-1; `C:/Temp/av-kit/s56/plan-callers.txt`): `app-icon`, `chrome-zorivest` (`:21` pins the dark accent), `console-polish`, `convert-page`, `downloader-page`, `layout-canon`, `queue-canon`, `queue-primitives` (AC-43.3, and `:583`'s `var()` pin), `transcript-page`, `tts-page` and `queue-card-slots` with its `queue-slot-baseline.json` fixture. The whole UI suite and the settings E2E run in the session gate.

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The two light token values | Human-approved | D-235; 06 `:1616` |
| The 4.5:1 floor for `text-sm` labels | Local Canon | 06 `:1612`; WCAG 2.2 SC 1.4.3 |
| Which tints are checked, and over which backdrops | Inferred, flagged | D-451: every tint the code draws behind a label, over the darkest and the lightest surface it sits on |
| How a tint is composited | Inferred, flagged | D-451: from the compiled CSS |
| The dark theme is unchanged | Human-approved | D-235 |
| The running app paints the ruled colours | Inferred, flagged | D-452: the issue's measured-in-the-app gap |
| The AC-43.3 re-baseline | Human-approved at this gate | D-456; AGENTS.md `:57` |
| Mat's look before it ships | Human-approved | D-235; 06 `:1617`; D-458 at row 4 |
| The TTS status pill | Human decision at this gate | D-455 |
| Row 4 counts and stops only this launch's processes and prints no argument | Human-approved | Mat's brief; AC-126.9; D-458 |
| A capture-crop write to the three status files is kept or fails loudly, never lost | Human-approved | Mat's brief ("leave it alone"); AC-126.10; D-454 |

### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/styles.css` | Modify | `LIGHT_ACCENT_TOKENS`: `:97` and `:99` |
| `ui/tests/unit/light-accent-contrast.test.ts` | New | AC-126.1 to AC-126.7 |
| `ui/tests/e2e/settings.test.ts` | Modify | AC-126.8 |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/contrast-matrix.json` | Modify | `MATRIX_REBASELINE`: 40 values |
| `docs/build-plan/06-gui.md` | Modify | §Spec text |

No test id is added, so `ui/tests/e2e/test-ids.ts` and its byte-hash tests aren't touched (S9). Line endings (`C:/Temp/av-kit/s56-plan-line-endings.txt`): CRLF are `styles.css` (211), `settings.test.ts` (889), `contrast-matrix.json` (1,138), `06-gui.md`, the grouping file, `current-focus.md` and `metrics.md`. LF are the register, its renders, `triage-output.yaml` and `meu-status.yaml`. Each row measures with Python bytes before it writes and writes by byte replacement or with `newline=""`, then checks the counts. New files are LF.

### Project files

- `docs/execution/plans/2026-11-08-light-accent-contrast/`: `implementation-plan.md`, `task.md`, `baseline.ps1`, `baseline.sha`, `baseline-dirty.txt`, `red-check.py`, `identity.py`, `matrix-rebaseline.py`, `dev-app-procs.py`, `status-write.py`, `issue-file.py`, `issue-resolve.py`, `session-gate.ps1` and row 4's `human-check.md`.
- `.agent/context/meu-status.yaml`, `docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/known-issues.yaml` and its render `known-issues.md`, `.agent/context/triage-output.yaml`, and the grouping tracker row 56 (`:259`).
- `.agent/context/handoffs/2026-11-08-light-accent-contrast-*.md`, `docs/execution/reflections/2026-11-08-light-accent-contrast-reflection.md`, `docs/execution/metrics.md`, `.agent/context/current-focus.md`.

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| The TTS status pill's contrast in either theme | Neighbouring defect | None; D-455 files it if Mat picks B | Not in D-235's ruling |
| `QUEUE-PILL-TOKEN-DRIFT` | Neighbouring issue | Its own placement | The brief: related, not in scope |
| A 12% tint over `bg-bg-subtle` (4.21:1 after the change) | Pair no control draws | None | No button or segmented control sits on an opaque `bg-bg-subtle` fill (§User Review Required) |
| Any dark token | Theme | None | D-235; `DARK_UNCHANGED` |
| Making light the default theme | Product | None | `settings.py:80`; not asked |
| Re-baselining `queue-slot-baseline.json` | Fixture | None | It holds no hex |
| A secondary button on a detail-open queue card (4.92:1 at rest, 4.36:1 on hover after the change) | Pair no caller draws | None | No caller passes `detailOpenId` (`QueueList.tsx:81`, `:217`); `C:/Temp/av-kit/s56-plan-selected-card.txt`. The handoff names it, so a later caller is measured first |

## BUILD_PLAN.md Audit

MEU-126 is at `.agent/context/meu-status.yaml:3298`, phase 6, band P2, matrix item 6.17, anchor `light-accent-contrast-residual`, status `pending`. Plan time: 132 MEUs, 118 completed (117 approved, 1 closed), 14 pending (`C:/Temp/av-kit/s56/meu-stats.txt`), the capture-crop session's five uncommitted MEUs included. Row 5 sets `ready_for_review` and H2-2 sets `approved`, each with `status-write.py` (`GUARDED_STATUS_WRITE`, D-454). Both write files the capture-crop session has changed. `tools/meu_status.py update` loads `meu-status.yaml` and saves the whole file, and `render` rewrites both renders whole, each without a lock (`tools/meu_status.py:131-145`, `tools/meu_status/model.py:204-225`, `tools/meu_status/render.py:296-310`). A capture-crop save between that load and that save would be lost, and a copy saved beforehand and diffed afterwards wouldn't show it (plan review round 1, F3).

`status-write.py` opens the three files through Windows handles that let other processes read them but not write, replace or delete them, and holds them from its first read to its last write. A capture-crop write that lands before the hold is in the bytes it reads, so it is kept; one tried during the hold fails loudly in that session's tool. The script keeps the bytes it read under `--keep`, runs the status tool's own `update_meu_status`, `save`, `render_all` and `check_drift` on staged copies, and refuses, writing nothing, if any line outside MEU-126's YAML entry and the two AUTOGEN regions changes or a file's line endings change. Only then does it replace the three files through the held handles and read each back. It writes the unified diff to `--diff-out` and lists each changed render line that doesn't name MEU-126, for the handoff (Session 55 RULE-2). `--verify MEU-126=STATUS` writes nothing: it checks that MEU-126 still holds the status and that the renders match the YAML, which catches the other direction, a capture-crop save from a load taken before this write. It runs at H1-3 and before H2-5.

Plan-time evidence: the selftest's 9 cases (`C:/Temp/av-kit/s56-plan-status-write-selftest.txt`), including the positive control in which the unguarded tool loses an interleaved write, and a dry run on copies of today's three files (`C:/Temp/av-kit/s56-plan-status-write-dry.txt`). The dry run changed only MEU-126's entry in the YAML, and its one disclosed render line is the BUILD_PLAN total, `117 + 1🚫` to `117 + 1🟡 + 1🚫`. The render check also runs at rows 5 and H1-3:

```powershell
rtk proxy uv run python tools/meu_status.py render --check > C:/Temp/av-kit/s56-render-check.txt 2>&1; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s56-render-check.txt; exit $code
```

## Verification Plan

> [!IMPORTANT]
> Classify every command through `.agent/docs/output-evidence-policy.md`. `rtk proxy` is used for exact evidence.

### 1. Baseline (row 0)

`baseline.ps1` is Session 55's without the yt-dlp and DDL steps:

1. Creates `C:\Temp\av-kit\s56\tmp`. Records `HEAD` in `baseline.sha`, and `git status --porcelain --untracked-files=all` in `baseline-dirty.txt` with each dirty path's SHA-256, the capture-crop session's paths among them.
2. Runs `uv sync --frozen --offline --all-packages`, so this step can't fetch a package (plan-time dry run: `s56-uv-offline-dry-run.txt`), and proves `ui/` and `mcp-server/node_modules` match their locks. `npm ci` isn't run, for Session 50's reason. It asserts the pinned FFmpeg pair under `packaging/ffmpeg-win64/` exists and is over 1024 B, because the full Python suite runs Session 54's real-FFmpeg module; a missing pair is S4, not a fetch.
3. Runs `matrix-rebaseline.py --check-shipped`: from the shipped tokens, the replica must equal the pinned matrix (S8).
4. Captures the base Python suite to `s56-base-py.txt`, the base UI suite to `s56-base-ui.txt` and the base MCP suite to `s56-base-mcp.txt`, with `TMP` and `TEMP` at `C:\Temp\av-kit\s56\tmp`.
5. Runs the `red-check.py`, `identity.py`, `matrix-rebaseline.py`, `dev-app-procs.py` and `status-write.py` selftests.

The plan-local copies:

- **`red-check.py`** is Session 55's. `DECLARED_NEW` holds no name of this session's, because the Reds read existing files and elements, and keeps the selftest fixtures' names. It gains one fixture shape, a Playwright `toHaveCSS` failure (`Expected: "rgb(21, 94, 117)"`, `Received: "rgb(8, 145, 178)"`), which it accepts as an assertion failure, while a `locator.evaluate: Timeout` stays a setup failure (`C:/Temp/av-kit/s56-plan-red-check-selftest.txt`: 38 fixtures, 0 wrong).
- **`identity.py`** is Session 55's with `PLAN` set to this folder and `NAMED_DISTRIBUTIONS` empty. It still binds the pinned FFmpeg pair. Its selftest binds `styles.css`, `matrix-rebaseline.py` and the gate scripts (`C:/Temp/av-kit/s56-plan-identity-selftest.txt`, 0 failures). `PROJECT_ARTIFACTS` are this plan's `*.md`, the handoff, review and reflection files, `docs/execution/metrics.md` and `.agent/context/current-focus.md`, which are written after the gate. The registers and renders stay bound, because row 5 writes them before H1-2.
- **`matrix-rebaseline.py`** is new (§The matrix). Its selftest covers each refusal and a CRLF round trip on matrices built in memory (`C:/Temp/av-kit/s56-plan-matrix-selftest.txt`, 0 failures), and its control reports 0 of 160 rows different (`s56-plan-matrix-control.txt`).

### 2. Red, then Green (rows 1 to 3)

- **No type-only row (D-457).** No row adds a name: the Reds read `styles.css` and elements that exist, so Session 53 RULE-2 and Session 52 RULE-4 have no target.
- **Each Red receipt holds an assertion failure, never a setup failure.** `red-check.py` reads row 1's Vitest receipt and row 2's Playwright receipt, and refuses a collection error, a launch failure or a timeout. A Vitest test is required by its title's `AC-126.<n>` prefix, matched up to a non-digit boundary.
- **Row 2 builds first.** `launchApp()` starts `out/main/index.js` (`settings.test.ts:24`), so the row runs `npm --prefix ui run build` before the E2E, and the Red fails on the shipped `rgb(8, 145, 178)` after the dark steps pass.
- **Guards pass in Red by design.** AC-126.2 and AC-126.7 are in row 1's selection, and no Red row requires them.
- **Expectations stay immutable in Green.** No test file changes in row 3. `contrast-matrix.json` is AC-43.3's pinned data, and its 40 values change only through `MATRIX_REBASELINE` under the authorization in §User Review Required.
- **Row 3's Green runs every caller** (Session 55 RULE-1): the new test, the eleven unit files named under §Acceptance Criteria (`queue-card-slots` with its fixture among them), the UI typecheck and lint, a fresh build, and the settings E2E.

### 3. Mat's look (row 4, D-458)

After row 3, the coordinator launches the dev app detached, so it outlives this harness:

```powershell
$p = Start-Process pwsh -ArgumentList '-NoProfile','-Command',"Set-Location P:/av-kit/ui; `$env:ELECTRON_RUN_AS_NODE=`$null; npm run dev *> C:/Temp/av-kit/s56-dev-app.txt" -PassThru
rtk proxy uv run python docs/execution/plans/2026-11-08-light-accent-contrast/dev-app-procs.py record --root-pid $p.Id --out C:/Temp/av-kit/s56/dev-app-launch.json *> C:/Temp/av-kit/s56-dev-app-record.txt
```

`record` waits up to 120 s until the tree under the launched pwsh holds an Electron process under `P:\av-kit\ui\node_modules\electron\dist\` and the backend (`-m avkit_api`), then writes each process in the tree as its id, its parent's id, its creation time and a role. It exits 1 if the root has gone or a role never appears. The coordinator then asks Mat through the Human Decision Protocol with §User Review Required item 3's brief. Mat switches to Light in Settings, looks at the Downloader, Convert and Settings pages, and quits the app from the tray. The row writes `human-check.md` with Mat's answer and words, verbatim, as `USER_EXPLICIT 2026-11-DD 'words'`.

Then `dev-app-procs.py check --record C:/Temp/av-kit/s56/dev-app-launch.json` lists what is left (`LAUNCH_OWNERSHIP`). A process is this launch's when the record holds its id with the same creation time, or when its parent is this launch's and it started no earlier than that parent. A recorded process that has exited still counts as the parent of an orphan it left, unless its id now belongs to a different process. This launch's processes still running are listed and fail the check, and `check --stop` ends each by its id after checking its creation time again, then checks once more. Any other Electron process under that folder, and any backend wherever its executable is (a uv environment's `python.exe` starts the base interpreter as its child, `ui/src/main/python-manager.ts:23-26`), is listed as not this launch's, named to Mat and left alone. The checker, the processes it runs under and the ones it starts never count, whatever their arguments hold, and the avkit MCP servers (`electron.exe mcp-server/dist/index.js`) never count and are never touched. Each process shows as its id, its parent's id, a role and an owner: no command line, argument or path (`NO_RAW_CONSOLE`). Plan-time evidence: the selftest's 11 cases on synthetic process tables (`C:/Temp/av-kit/s56-plan-dev-app-procs-selftest.txt`) and a real-stack control on a stand-in pwsh tree (`C:/Temp/av-kit/s56-plan-dev-app-procs-live.txt`): 3 recorded, 3 left while it ran (exit 1), 2 orphans left after its root alone was stopped (exit 1), 0 after `--stop` (exit 0).

- **Approve:** the session goes on to row 5.
- **No:** rows 1 to 3 stay as they are in the work tree, no record is written, and the session stops with a brief for Mat: the hexes go back to Mat as a new decision, and nothing ships.
- **Do nothing:** the same stop, with `#0891b2` kept by reverting row 3's two lines and the 40 values. The issue stays open at P4.

### Plan-local scripts

- `baseline.ps1`, `red-check.py`, `identity.py`, `matrix-rebaseline.py`: §1.
- `issue-file.py` (row 5, only if Mat picks B at this gate): files `TTS-STATUS-PILL-BELOW-AA-CONTRAST` through `tools/issue_triage/model.py`. It refuses an empty `--quote`, a register whose SHA-256 isn't `--expect-sha256`, and a duplicate, and fails on any removed line, on the validator's bounded grammar and unless `issue_decision_log` reads D-455 at stage `planning`. Dry run on a copy: 42 lines added, 0 removed, 123 issues (`C:/Temp/av-kit/s56-plan-issue-file-dry.txt`).
- `dev-app-procs.py` (row 4, AC-126.9): §3.
- `status-write.py` (rows 5 and H2-2, AC-126.10): §BUILD_PLAN.md Audit. Its exclusive handle is `issue-resolve.py`'s.
- `issue-resolve.py` (row 5): Session 55's copy with `SCRATCH` at `C:/Temp/av-kit/s56`. `RESOLVE_KEYS` stay `status`, `verification` and `resolution_path`, and the issue holds all three (Session 51 RULE-2; `C:/Temp/av-kit/s56-plan-register-keys.txt`). Its `resolution_path` holds D-235's ruling today, so row 5 writes the ruling and the fix into it.
- `session-gate.ps1` (H1-2): below.

### Session gate (H1-2)

`session-gate.ps1` is Session 55's shape. It writes one receipt per step in `C:/Temp/av-kit`, named `s56-D6-<step>`. It is fail-fast, and it prints later steps as `not_run`. It sets `TMP` and `TEMP` as in §1 and clears `ELECTRON_RUN_AS_NODE`. Its last line is `session-gate: all steps exit 0`.

| Stage | Steps |
|---|---|
| Identity | `identity.py` before and after the run; the two must match |
| Static | `py-types`, `py-lint`, `ui-types`, `ui-lint`, `task-contract`, `scope-paths` (this plan's Files Modified and project files, plus `baseline-dirty.txt`; `ui/tests/e2e/test-ids.ts` refused), `red-check-selftest` |
| Fresh full | `py-tests`, `ui-tests`, `ui-build`, `openapi`, `mcp-types`, `mcp-tests`, `mcp-build`, `state-render`, `issues-render` |
| Runtime | `light-accent` (the new test on its own, so its receipt stands alone), then `ui-electron`, targeted to `ui/tests/e2e/settings.test.ts` |
| Skipped with reason | `mcp-audit` (live network), `build-record` (no installer build), the package build and its smokes (no packaged surface changes; MEU-125 runs them) |

`py-tests`, `ui-tests` and `mcp-tests` excuse only ids that row 0's receipts show failing. A step that fails in a file this session didn't touch is rerun once unchanged, and both attempts' receipts are kept (Session 53 RULE-4). `tested_state` binds the whole work tree, the capture-crop session's files included, so if that session writes during the gate, `identity-after` fails and the gate is rerun once that write has settled, with both receipts kept.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `graphify-out/` or `graphify-out-research/` appears | Re-decide the context tool |
| S2 | A Red receipt fails `red-check.py` | Fix the test setup; don't move to Green |
| S3 | `HEAD` moves from `baseline.sha`, or a path outside `baseline-dirty.txt` and this plan appears | Stop and tell Mat; never commit, stash or revert another session's work. A `baseline-dirty.txt` path whose SHA-256 changes is the other session at work: it is recorded in the handoff and named at H2-5, and this session never writes it except through `status-write.py` at rows 5 and H2-2 (D-454) |
| S4 | The pinned FFmpeg pair is missing or under 1024 B | Stop: a fetch is a download and needs Mat's words |
| S5 | Any network request, download or upload, or any write to YouTube | Stop and tell Mat |
| S6 | Row 3's `styles.css` diff holds more than lines `:97` and `:99`, or the dark block changes | Stop and find out why |
| S7 | Codex is unavailable or the ledger refuses a round | Mat is the fallback |
| S8 | `matrix-rebaseline.py --check-shipped` finds the replica differs from the pinned matrix, or the re-baseline moves any value outside its 40 | Stop before Green; the re-baseline would prove nothing |
| S9 | A row finds it must edit `ui/tests/e2e/test-ids.ts` | Stop, add ids in an additive block at the end, and run AC-51.6 and AC-81.13 in that row's own check |
| S10 | Mat answers "no" or "do nothing" at row 4 | Stop before records, as §3 says |
| S11 | `status-write.py` refuses: a file is already held, or a line outside MEU-126's entry and the generated regions would change | Nothing was written. Wait for the capture-crop session's write to settle and rerun once, keeping both receipts (Session 53 RULE-4); a second refusal stops and tells Mat. A `--verify` failure stops and tells Mat, because a later save dropped MEU-126's status |
| S12 | `dev-app-procs.py record` exits 1, or `check --stop` still lists a process of this launch | Stop and tell Mat, naming the process ids; never stop a process that isn't this launch's |

## Decision Log

> [!WARNING]
> Mat's brief and triage D-235 settle the scope and the values, and grouping D-249 gives MEU-126 its own session. D-450 to D-454, D-456 and D-457 didn't need Mat: each is autonomous with its alternatives in `reasoning`. Mat answered D-455 (B) and D-459, how round 1's findings are routed now that the ledger refused that round, on 2026-11-08: "all recommendations accpeted, proceed". Both are in the block with those words: D-455 at stage `planning`, carried with the same stage and text into the new issue's `decision_log` by `issue-file.py`, and D-459 at stage `plan-review`. D-458 is open at row 4 and is added with Mat's words in `human-check.md`, the handoff and the reflection, with stage `execution`.
>
> Carried and not relisted in the block: every grouping §8 row, D-240 to D-250, D-267, D-277 and D-280, with stage `grouping`; D-249 is among them. The register holds D-235 (stage `triage`, under `LIGHT-ACCENT-BELOW-AA-CONTRAST`). This plan cites it in prose only, so no id carries a second stage. The probe (`C:/Temp/av-kit/s56-decision-issue-probe.txt`), run with this plan as a source (Session 54 RULE-5), shows what `--decision-issue LIGHT-ACCENT-BELOW-AA-CONTRAST` pulls in. H2-2 passes it.

```yaml
decision_log:
  - id: D-450
    stage: planning
    question: "How does the contrast test read the tokens and compute each ratio?"
    resolution: autonomous
    class: two-way
    chosen: "A new ui/tests/unit/light-accent-contrast.test.ts reads both theme blocks of styles.css, holds its own helpers after queue-primitives.test.ts:203-251 with the 0.04045 threshold and unrounded ratios, throws on a missing token, and copies neither ruled light value"
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1619: a contrast test of the two light token values", "ui/tests/unit/queue-primitives.test.ts:55, :203-251: TOKEN_FILE and the matrix helpers", "WCAG 2.2 SC 1.4.3"]
    research: { engine: none, sources: [] }
    reasoning: "The contract asks for values read from the file, so the test computes from styles.css and a later token change is measured, not trusted. AC-43.3's helpers round each ratio to 2 dp, which would pass 4.496 as 4.50; the new test keeps them unrounded. Extending queue-primitives.test.ts would mix this contract into the queue matrix's file. A Playwright-only measurement can't compare a color-mix result."
  - id: D-451
    stage: planning
    question: "Which tints does the test check, over which backdrops, and how is a tint composited?"
    resolution: autonomous
    class: two-way
    chosen: "TINT_MODEL: the 12%, 20% and 15% tints, each over the page bg and the white card or group surface, and the 12% and 20% tints also over a selected queue card's wash; the accent at alpha N composited per channel in sRGB over the opaque backdrop and rounded half up"
    source_tag: Local Canon
    precedents: ["ui/out/renderer/assets/index-BJyOr5xS.css: .bg-accent\\/12 is color-mix(in oklab, var(--color-accent) 12%, transparent) (C:/Temp/av-kit/s56-plan-tint-css.txt)", "ui/src/renderer/src/components/ui/Button.tsx:16 and SegmentedControl.tsx:22, :44", "C:/Temp/av-kit/s56-plan-rounding-margin.txt: one rounding step either way leaves every pair at 4.91 or more"]
    research: { engine: none, sources: [] }
    reasoning: "The brief asks whether both tints are checked; the code draws three behind labels, so all three are. The page bg and white bound every opaque surface a button sits on, but a selected queue card lays a 5% accent wash over the page under its secondary button, which gives the lowest live pair, 4.62 on hover (plan review round 1, Q2), so the test checks that stack too and reads the wash from the card's own class. The compiled CSS shows each tint is the accent mixed with transparent, which keeps its hue at that alpha. Checking one tint only would leave the hover and the segmented option unmeasured."
  - id: D-452
    stage: planning
    question: "How does the plan prove the running app paints the ruled colours?"
    resolution: autonomous
    class: two-way
    chosen: "RUNTIME_COLOURS: AC-126.8 in settings.test.ts after AC-94.7, on existing test ids, asserts the solid accent, hover and label colours in dark, then light, then dark, with dark first as the positive control; it pins the ruled colours as rgb literals and asserts no tint"
    source_tag: Local Canon
    precedents: ["known issue LIGHT-ACCENT-BELOW-AA-CONTRAST: the figures are worked out from the token values, not measured in the running app", "ui/tests/e2e/settings.test.ts:687-699: AC-94.7", "ui/src/renderer/src/features/settings/SettingsPage.tsx:1098-1118, :653-667"]
    research: { engine: none, sources: [] }
    reasoning: "The unit test reads the tokens, so a build that dropped or overrode them would still pass it. The E2E closes that gap on the built app. It pins rgb literals because its contract is what the app paints, while the ratio test keeps reading the file. Chromium serialises a color-mix result outside sRGB, so tints stay the unit test's. Alternatives: a jsdom test, which computes no cascade, or a screenshot diff, which needs a baseline and breaks on any layout change."
  - id: D-453
    stage: planning
    question: "Which checks does the session gate run?"
    resolution: autonomous
    class: two-way
    chosen: "Session 55's shape: identity, static, the full Python, UI and MCP suites, the UI and MCP builds, the OpenAPI and render checks, then the new test alone and the settings E2E; no package build or smokes; mcp-audit and build-record skipped with reasons"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-11-08-download-received-quality/implementation-plan.md:390-402: Session 55's session gate"]
    research: { engine: none, sources: [] }
    reasoning: "No Python changes, but row 5 writes the registers and renders that Python tests read, and the gate is the fresh-full proof of the tree it binds. The settings E2E runs AC-126.8 and AC-94.7 on the built app. No packaged surface changes, and MEU-125 builds the installer."
  - id: D-454
    stage: planning
    question: "How do this session's record writes share files with the capture-crop session's uncommitted edits?"
    resolution: autonomous
    class: governance-value
    chosen: "GUARDED_STATUS_WRITE: row 5 and H2-2 write meu-status.yaml, BUILD_PLAN.md and meu-registry.md only through status-write.py, which holds all three from its first read to its last write, runs the status tool's own update and render on staged copies, refuses any change outside MEU-126's entry and the generated regions, keeps the bytes it read, writes the diff and discloses each render line that doesn't name MEU-126; status-write.py --verify runs at H1-3 and before H2-5; H2-5 recommends the capture-crop planning commit lands first and asks Mat before committing"
    source_tag: Local Canon
    precedents: ["Session 55 RULE-2: save, diff and disclose before a tool rewrites another session's file", "Mat's Session 56 brief: record each path with its SHA-256, leave it alone, name it before any commit", "plan review round 1, F3: a save and diff can't see a write lost between the tool's load and its save", "docs/execution/plans/2026-11-08-light-accent-contrast/issue-resolve.py: the exclusive handle"]
    research: { engine: none, sources: [] }
    reasoning: "The status tool loads and saves whole files without a lock, so a capture-crop save between its load and its save would be lost, and a copy diffed afterwards wouldn't show it. Holding all three files from the first read to the last write makes that write fail loudly in the other session instead. Running the tool's own functions on staged copies keeps the renders in step, and the preservation check refuses before anything is written. --verify catches a later stale save, which no hold here can prevent. Writing the MEU by hand would skip the tool that keeps the renders in step; asking the capture-crop session to pause would depend on its coordinator answering. The commit tool stages whole files, so naming the order at H2-5 lets Mat choose."
  - id: D-456
    stage: planning
    question: "AC-43.3 pins a contrast matrix that the ruled accent moves. How is it re-baselined?"
    resolution: autonomous
    class: governance-value
    chosen: "MATRIX_REBASELINE: matrix-rebaseline.py recomputes AC-43.3's matrix with its own algorithm and replaces exactly the 40 light values that move, every label still at 4.5 or more and _meta unchanged; authorized as TEST_AMENDMENTS by Mat's proceed at the plan gate and re-checked by the execution review"
    source_tag: Local Canon
    precedents: ["AGENTS.md:57: a proven wrong expectation needs a source-backed amendment and explicit human authorization or independent review", "docs/execution/plans/2026-10-10-gui-polish-residuals/human-gate-decision.md:95-99: A-6 re-baselined 16 values the same way", "C:/Temp/av-kit/s56-plan-matrix-dry-run.txt"]
    research: { engine: none, sources: [] }
    reasoning: "The matrix is data computed from the tokens, and the change follows from Mat's ruled values. A script that refuses any other move, checks the floors and keeps every other byte makes the amendment exact. Editing the 40 numbers by hand risks a typo AC-43.3 would then pin. Changing AC-43.3 to skip the accent backdrops would weaken a passing test."
  - id: D-457
    stage: planning
    question: "In what order do the rows run?"
    resolution: autonomous
    class: two-way
    chosen: "Row 0 baseline; row 1 the unit Red; row 2 the build and the E2E Red; row 3 the two tokens, the matrix and every caller's tests; row 4 Mat's look; row 5 records. No type-only row"
    source_tag: Local Canon
    precedents: ["Session 53 RULE-2: a type-only row exists for a shared missing name", "Mat's Session 56 brief: the human check after the Green and before the execution review"]
    research: { engine: none, sources: [] }
    reasoning: "No row adds a name, so a type-only row would hold nothing. Mat's look follows the Green so Mat sees the shipped tokens, and the records follow Mat's yes so a no leaves nothing to undo in the registers."
  - id: D-455
    stage: planning
    question: "Session 56's ruled light accent moves the TTS Generating pill's label from 3.97:1 to 2.01:1, and the pill already fails 4.5:1 for most statuses in both themes. Widen the session or keep its scope?"
    resolution: human
    class: product-preference
    chosen: "B: keep MEU-126 to the two ruled light tokens and file the whole TTS status pill as an open TECH-DEBT issue"
    source_tag: Human-approved
    precedents: ["ui/src/renderer/src/features/tts/TTSPage.tsx:721 — text-xs text-fg on the STATUS_COLORS fill", "C:/Temp/av-kit/s56-plan-tts-pill-dark.txt — both themes' ratios", "docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md — the D-455 brief and its options"]
    research: { engine: none, sources: [] }
    reasoning: "The pill fails in the default dark theme for five of six statuses before this session, so fixing Generating alone leaves the pill failing, and fixing it whole changes the TTS page in both themes, outside D-235's two tokens. Filing keeps the ruled scope and records the probe. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'all recommendations accpeted, proceed'"
  - id: D-459
    stage: plan-review
    question: "The ledger refused plan review round 1 because F3 cited PR-8, which isn't a registered family, and the reviewer found no AC that stated F2's or F3's property. How are the findings routed?"
    resolution: human
    class: governance-value
    chosen: "Accept the routing: F1 under AC-126 as the reviewer mapped it, F2 under the new AC-126.9 (LAUNCH_OWNERSHIP and NO_RAW_CONSOLE) and F3 under the new AC-126.10 (GUARDED_STATUS_WRITE), and re-dispatch the revised plan as s56-plan-r1b, which the ledger records as round 1; round 1's cost of about 6.14M stays disclosed outside the ledger"
    source_tag: Human-approved
    precedents: ["C:/Temp/av-kit/s56-plan-review-round-1.md:39 — the reviewer kept NO_RAW_CONSOLE and PR-8 and asked Mat to rule on the routing", "C:/Temp/av-kit/dispatch/s56-plan-r1/ledger-record.txt — the refusal", "tools/review_ledger.py:2493-2497 — a blocking finding may cite only the plan's AC ids"]
    research: { engine: none, sources: [] }
    reasoning: "The ledger registers only the plan's AC ids and the closed mechanism catalogue, so PR-8 can't be recorded, and neither the verdict nor the catalogue may be edited to get it through. The two new ACs state the properties the reviewer said no AC stated, so the findings cite what they really are. Accepting the fixes without a second review would leave the two new scripts, which handle tokens and another session's writes, unreviewed until after rows 4 and 5 have used them. Doing nothing leaves the issue open at P4. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-08 'all recommendations accpeted, proceed'"
```

## Research References

- `docs/build-plan/06-gui.md:1608-1619` (the residual contract) and `:1597-1606` (Session 55's Delivered note, the form row 5 follows).
- `.agent/context/known-issues.yaml:3891` (`LIGHT-ACCENT-BELOW-AA-CONTRAST`), the grouping file §1 `:29`, §2 `:134`, §3 `:205-207`, §4 `:240`, §6 `:259`, §8 `:288` (D-249) and `:304`.
- `_inspiration/zorivest/globals.css:144,146` (the ruled values).
- WCAG 2.2 SC 1.4.3 and its relative luminance definition (the 0.04045 threshold).
- Session 55's plan, task and scripts (`docs/execution/plans/2026-11-08-download-received-quality/`), A-6 (`docs/execution/plans/2026-10-10-gui-polish-residuals/human-gate-decision.md:95-99`), and the AC-43.3 matrix's plan (`docs/execution/plans/2026-08-28-p10-queue-card-foundations/`).

## Planning receipts

- `C:/Temp/av-kit/s56/baseline-dirty.txt`: the tree at plan time, the capture-crop session's paths with their SHA-256.
- `C:/Temp/av-kit/s56/accent-census.txt`: every accent utility and `var()` in the renderer, by file and line.
- `C:/Temp/av-kit/s56/plan-callers.txt`: the tests that read `styles.css` or name an accent token, and the fixture's 0 hex values.
- `C:/Temp/av-kit/s56/contrast-probe.txt`: every pair before and after, from the tokens in `styles.css`.
- `C:/Temp/av-kit/s56-plan-tint-css.txt`: the compiled CSS for `bg-accent/12`, `/15` and `/20`.
- `C:/Temp/av-kit/s56-plan-rounding-margin.txt`: each composite channel moved by one step either way; worst 4.91.
- `C:/Temp/av-kit/s56/matrix-probe.txt`, `s56/meta-probe.txt`, `C:/Temp/av-kit/s56-plan-matrix-selftest.txt`, `s56-plan-matrix-control.txt` and `s56-plan-matrix-dry-run.txt`: the 40 moves, `_meta` unchanged, the selftest, the control and the dry run.
- `C:/Temp/av-kit/s56-plan-tts-pill-dark.txt` and `s56/tts-pill-probe.txt`: the TTS pill in both themes (D-455).
- `C:/Temp/av-kit/s56-plan-issue-file-dry.txt`: `issue-file.py` on a copy of the register; the real register untouched.
- `C:/Temp/av-kit/s56-plan-register-keys.txt`: the register's SHA-256 (`1b1331db…`, 388,872 B, 122 issues) and the issue's keys (Session 51 RULE-2). Row 5 reads the SHA-256 again for `--expect-sha256`.
- `C:/Temp/av-kit/s56-plan-line-endings.txt`: every target file's endings.
- `C:/Temp/av-kit/s56-plan-red-check-selftest.txt` and `s56-plan-identity-selftest.txt`.
- `C:/Temp/av-kit/s56/meu-stats.txt`.
- `C:/Temp/av-kit/s56-uv-offline-dry-run.txt` (Session 52 RULE-2): `uv sync --frozen --offline --all-packages --dry-run`. This plan relies on no cached wheel, model or file except the pinned FFmpeg pair, already on disk.
- `C:/Temp/av-kit/s56-decision-issue-probe.txt`: the closeout flag, with this plan as a source, pulls in D-235 (triage), the grouping rows D-240 to D-250, D-267, D-277 and D-280, and the plan's D-450 to D-454, D-456 and D-457. Without the flag, the register source is refused.
- `C:/Temp/av-kit/s56-plan-task-lint.txt`: `lint_task_contract.py` on `task.md`.
- `C:/Temp/av-kit/s56-plan-selected-card.txt`: the secondary button's tints on a selected and a detail-open queue card, before and after, with one rounding step either way (D-451).
- `C:/Temp/av-kit/s56-plan-dev-app-procs-selftest.txt` and `s56-plan-dev-app-procs-live.txt`: `dev-app-procs.py`'s 11 selftest cases and its real-stack control (AC-126.9).
- `C:/Temp/av-kit/s56-plan-status-write-selftest.txt` and `s56-plan-status-write-dry.txt`: `status-write.py`'s 9 selftest cases and its dry run on copies of today's files (AC-126.10).
- `C:/Temp/av-kit/s56-plan-review-round-1.md`, `C:/Temp/av-kit/dispatch/s56-plan-r1/final.json` and `ledger-record.txt`: plan review round 1, `changes_required` with F1 to F3, which the ledger refused to record (D-459).
- Step 4A GUI check (`gui-refs-not-shipped`, items 3 and 5): the visible change is the light accent's colour wherever it is drawn. No control, layout, icon or text changes, and the dark theme doesn't change.
- Not run at plan time: any suite, build, E2E or the dev app. Row 0 runs the suites.

## Validation stage contract

- **Static:** `pyright packages/`, `ruff`, the UI typecheck and lint, `lint_task_contract.py`, the scope-paths check and the `red-check.py` selftest.
- **Targeted:** each row's own files, with `red-check.py` reading every Red receipt, and every caller's tests in row 3.
- **Fresh full:** the whole Python, UI and MCP suites, the UI and MCP builds, the OpenAPI guard and the two render checks, in the session gate.
- **Runtime:** the new contrast test on its own, and the settings E2E spec on the built app.
- **Human:** Mat's look at the light theme in the dev app (row 4), with `dev-app-procs.py check` after Mat quits it.
- **Plan-local scripts:** the `dev-app-procs.py` and `status-write.py` selftests in row 0, and `status-write.py --verify` at H1-3 and before H2-5.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
