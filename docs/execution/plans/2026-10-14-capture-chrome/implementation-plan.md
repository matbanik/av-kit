---
project: "2026-10-14-capture-chrome"
date: "2026-10-14"
source: "docs/build-plan/09-screenshot-capture.md#icon-button-hints"
meus: ["MEU-80", "MEU-81"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture chrome — icon hints and the action row (Session 34)

> **Project:** `2026-10-14-capture-chrome`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md`:
> - §Icon-button hints (`:678-689`, MEU-80, matrix 9.13)
> - §Capture action row (`:691-702`, MEU-81, matrix 9.14)
> - §Capture page controls (`:119-123`), §Annotation edit until Save (`:386-397`) and §Viewport toolbar icons and Options (`:612-643`) as Local Canon that MEU-81 amends
> - `docs/build-plan/11-page-layout.md` §Capture page layout (`:87-91`), with the CP rows (`:267-290`) as locked canon
>
> **Grouping:** `.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, Session 34 (`:112-117`), decisions D-1 to D-7 (`:211-221`).
> **Known issues:** `CAPTURE-TOOLTIPS-NOT-SHOWN` (MEU-80); `CAPTURE-ACTION-ROW-ICONS`, `CAPTURE-MARKS-ROW-SQUEEZED`, `CAPTURE-SAMPLE-ORIGINAL-UNLABELED`, `CAPTURE-HOTKEY-BANNER-GAP` (MEU-81). Their triage decisions D-48, D-49, D-50, D-51, D-64 and D-69 do not collide with this plan's D-8 to D-24; the reflection carries them with stage `triage`, and H2-1 reconciles each issue's `enrichment.decision_log` with `--decision-issue`.
> **Status:** `draft`, Round 1. Execution waits for the user's direct message (`plan_to_exec_gate: human`).

## Goal

Mat's Session 29/30 looks found two problems in the Capture chrome:

- **No hints.** No native `title` tooltip appears anywhere in the dev app (local check 2026-10-09). Icon-only buttons, which have no words, give no clue what they do. Mat: "i don't care about tool tips on navigation only on function buttons that have images and no words" (triage D-69).
- **A crowded action row.** The second chrome row (`CaptureViewport.tsx:886-987`) overflows at 1280×800 once Apply to image and Revert join it, and it can shrink to 28 px. Body/Tail/Head and the four nudge buttons fill it. The Sample original eyedropper is unexplained. The always-mounted hotkey banner leaves an empty band under the header.

This session ships two MEUs, in order (grouping `:65`, MEU-81 depends on MEU-80):

1. **MEU-80 `gui-icon-button-hints`:**
   - Row 2 first reproduces the missing native tooltips on this machine and records the cause, or a one-line environment fix if one is found (`ROOT_CAUSE_PROBE`).
   - Then one shared renderer `Tooltip` primitive (portaled, fixed, `role="tooltip"`, `aria-describedby`) gives every icon-only function button a hint on hover and on keyboard focus, including while disabled.
   - It generalises Session 30's A-10 reason label.
2. **MEU-81 `gui-capture-action-row`:**
   - Remove mark, Save overlay, Apply to image, Revert, Open file, Open folder and Delete shot become icon buttons with MEU-80 hints. Delete is red, at the far right, after a separator.
   - Body/Tail/Head, the four nudge buttons and Sample original are removed. Arrow keys nudge the selected mark, or the arrow end that was grabbed or focused.
   - The marks row keeps its height and never scrolls sideways.
   - The hotkey status moves inline into the header row, so no band is reserved and nothing shifts.

The product change is renderer-only (`PRODUCT_SCOPE`). The worktree is `P:/av-kit-wt/s34-capture-chrome`, on branch `claude/s34-capture-chrome`, created from `main` at `7861020` (Session 30 closeout). Row 0 records the execution baseline in `baseline.sha`.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent in the worktree and no headroom is on PATH (2026-10-14). Scope is renderer internals (Capture page, viewport, five icon-button sites) read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Row 0 re-runs this gate before execution. The `prereq` check refuses if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code (VS Code extension) on Mat's Windows 11 host.
  - `native_shell: pwsh`, `rtk` on PATH, receipts in `C:/Temp/av-kit/`.
  - `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; `.agent/docs/harness-profiles.md`).
  - `fresh_worker` is the Agent tool with `.claude/agents/`. Every non-shared row keeps `compact_continue` as the fallback.
- **Gate location:** local. There is no container/Windows split for this session: one script, `validate-task.ps1`, holds every check, and the agent runs the authoritative gate itself (`GATE`). The only human step is the `CHROME_LOOK` checklist (H1-6).
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1`, resolved with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`:
  - class `avkit_independent_reviewer`, slug `gpt-6.1-sol`, effort high, vendor openai (vendor-distinct from the anthropic author);
  - registry 2026-10-07 `a7c95972…`, overlay `.agent/model-registry.local.json` `34e7dcbb…` (validated 2026-10-14);
  - caps: plan 3 rounds, execution 6;
  - ledger loops `s34-plan-2026-10-14-capture-chrome` and `s34-execution-2026-10-14-capture-chrome`.
- **Electron:** every launch unsets `ELECTRON_RUN_AS_NODE` (the scripts clear it in-process). Manual dev-app runs start detached with `Start-Process`.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-80` | `.agent/context/handoffs/2026-10-14-capture-chrome-MEU-80-handoff.md` |
| `MEU-81` | `.agent/context/handoffs/2026-10-14-capture-chrome-MEU-81-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-10-14-capture-chrome-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-14-capture-chrome-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census, `ROOT_CAUSE_PROBE` (task rows 0–2) | — | `shared` | `walkthrough.md` §Baseline, §Census, §Root cause; `baseline.sha` |
| WP-1 | MEU-80 TDD: Tooltip primitive and `ICON_ONLY_INVENTORY` adoption (rows 3–5) | WP-0 | `compact_continue` | MEU-80 handoff; compact, then re-read `task.md` and the handoff |
| WP-2 | MEU-81 TDD: action icons, retirements, nudge, marks row, header status (rows 6–8) | WP-1 | `compact_continue` | MEU-81 handoff; compact, then re-read |
| WP-3 | Registry and fixture proof, hub reconciliation (rows 9–10) | WP-2 | `shared` | `s34-registry.txt`; `docs/build-plan/09…`, `11…`, `build-priority-matrix.md` |
| WP-4 | H1 closeout, `GATE`, `CHROME_LOOK`, execution review, H2 | WP-3 | `compact_continue` | handoffs, `gate-result.json`, walkthrough, rolling review, reflection |

---

## User Review Required

> [!IMPORTANT]
> These items are review-loop content, not a pause point. The plan goes to the Codex plan review first. Execution then waits for the user's direct message.
>
> 1. **Human-approved inputs carried as written:**
>    - D-69: scope is icon-only function buttons; the nav rail is out.
>    - D-49: the icon set; Delete red at the far right; Body/Tail/Head and the nudge pad removed (amends MEU-60 ACs).
>    - D-51: Sample original removed (amends the AC-60 sampling ACs).
>    - D-64: hotkey status inline in the header (amends AC-57.3).
>    - These amend earlier ACs, so `TEST_AMENDMENTS` rewrites those tests. Each TA row cites its triage decision.
> 2. **Autonomous calls the reviewer should challenge:**
>    - Disabled-button hints use a focusable wrapper span (D-8), which adds DOM around every inventory control: QueueCard snapshot repair (a) and TA-25.
>    - Wrapped controls drop their `title` (D-12).
>    - The hint reads `Name — reason` when disabled (D-9).
>    - The endpoint-nudge model: grab or focus a handle (D-17).
>    - The in-use hotkey fixture holds F2 through the Win32 `RegisterHotKey` API (D-20).
> 3. **Root-cause fix:** if `ROOT_CAUSE_PROBE` finds a one-line environment fix that would make native tooltips work, this plan records it and does not apply it, because `ui/src/main/` is outside `PRODUCT_SCOPE` (D-14). The final report brings it to Mat as a Decision Brief.
> 4. **Human step:** the `CHROME_LOOK` checklist (L1–L8) before the execution review; one line per item from Mat.
> 5. **`BASELINE_RED` (D-30):** main `7861020` has one failing Vitest case, `queue-canon.test.ts` AC-41.3. It reads `P:/zorivest`'s live CSS, and Session 31's unmerged `da1d111` fixes it. This plan tolerates exactly that case and message, and stops (S9) on anything else.
> 6. **Round 1 corrections (D-25 to D-29):** `DESCRIBEDBY_COMPOSE` (F1); `HANDLE_LAYER` and `Element` focus ownership, with AC-81.14 and AC-81.15 (F2); the `CASE_EVIDENCE` model with `AC_CASES`, `ASSERTION_FAILURE`, `SETUP_SENTINEL`, `TA_TAGS` and `selftest`, which redesigns the `task-row-completion-predicate` mechanism (F3); `PROBE_RUN` (F4); `IDENTITY_SCOPE`, `ADMIN_PATHS`, `native/` frozen, and SSOT updates before `GATE` (F5); `HINT_TITLE_RULE` proved in the DOM, including spread titles (F6).
> 7. **Round 2 corrections (D-31, D-32):** the `PROBE_RUN` producer binding and full PNG decode, with round 2's metadata-free record as a selftest negative, and the same producer binding for `gate-result.json` and its raw reports (F4, the `task-row-completion-predicate` mechanism); `HANDLE_LAYER` inside `capture-zoom-content`, with AC-81.14 measuring rendered handle geometry and a real grab at 100% after a pan (F7).

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `PRODUCT_SCOPE` | The product files this plan may change are exactly the Files Modified rows below. `ui/src/main/`, `ui/src/preload/`, `packages/`, `mcp-server/`, `tools/` (except `tools/validate_closeout_artifacts.py`, D-39) and `native/` stay byte-identical to `baseline.sha`. `validate-task.ps1 -Check scope` (via `plan_checks.py scope`) proves the frozen paths and classifies **every** changed path in the repository (committed since `baseline.sha`, staged, unstaged or untracked and not ignored): each must be a Files Modified row, a file in this plan folder, or one of `ADMIN_PATHS`. Anything else fails, whatever its directory. | D-14; grouping `:114`; D-29 (R1 F5); D-39 |
| `ADMIN_PATHS` | The administrative files this plan's rows may change, and nothing else outside Files Modified and the plan folder:<br>`docs/build-plan/09-screenshot-capture.md`, `docs/build-plan/11-page-layout.md`, `docs/build-plan/build-priority-matrix.md` (row 10, `HUB_EDITS`);<br>`docs/BUILD_PLAN.md`, `.agent/context/meu-registry.md`, `.agent/context/meu-status.yaml` (`meu_status.py update` and `render`, H1-2 and H2-2);<br>`.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md`, `.agent/context/current-focus.md` (H1-2, H2-2);<br>`.agent/context/known-issues.yaml`, `.agent/context/known-issues.md` (H2-2), `docs/execution/metrics.md` (H2-2);<br>the prefixes `.agent/context/handoffs/2026-10-14-capture-chrome-` and `docs/execution/reflections/2026-10-14-capture-chrome-`. | D-29 |
| `ICON_ONLY_INVENTORY` | The controls that render an image or glyph and no visible words, and so get the hint:<br>(1) the 12 `TOOLBAR_BUTTONS` (`capture-toolbar.ts:30-43`);<br>(2) the 7 `ACTION_BUTTONS` (MEU-81);<br>(3) `console-close` (`ConsolePanel.tsx:130-140`), `bulk-toast-dismiss` (`BulkResultToast.tsx:49-57`), `queue-card-drag-handle` (`QueueCard.tsx:507-520`), `queue-card-kebab` (`QueueCardMenu.tsx:425-441`), `up-btn` and `down-btn` (`TranscriptPage.tsx:392-419`) and `convert-staged-remove` (`ConvertPage.tsx:607-615`).<br>Nav-rail items (`nav-*`) and every control with visible words are excluded. | D-69 (Human-approved); D-13 |
| `TOOLTIP` | The component `ui/src/renderer/src/components/ui/Tooltip.tsx`: `<Tooltip id label reason? disabled? suppressed?>{child}</Tooltip>`. The child must be a single element.<br>**Wrapper.** It always renders `<span data-testid="{id}-tip" className="inline-flex">` around the child.<br>**Disabled child.** When `disabled`, the span gets `tabIndex={0}` and is the focus target.<br>**Enabled child.** The child is the focus target and the span has no `tabindex`.<br>**Title.** The child's `title` prop is removed (`HINT_TITLE_RULE`).<br>**Showing.** Shown and hidden by `HINT_TIMING`. While shown, it portals (`createPortal`, `document.body`) one `<div role="tooltip" id={useId()} data-testid="{id}-hint">` placed by `TOOLTIP_PLACEMENT`.<br>**Description relation (`DESCRIBEDBY_COMPOSE`).** The focus target's `aria-describedby` is composed, never replaced: while shown it is the target's own tokens (the child's `aria-describedby` prop, for example dnd-kit's `DndDescribedBy-0` on the drag handle, or the wrapper's none) followed by the hint id; while hidden it is exactly the target's own value, or absent if it had none. Only the hint id is ever added or removed.<br>**Child preservation.** The child is rendered through `cloneElement`, which keeps its `ref` (for example dnd-kit's `setActivatorNodeRef`), its props and its handlers (`{...listeners}`, `{...attributes}`); Tooltip adds its pointer and focus listeners to the wrapper only and never overrides a child handler.<br>**Styling.** Token classes only (`bg-bg-elevated text-fg border border-border rounded-[var(--radius-control)] shadow-[var(--shadow-elevated)] px-2 py-0.5 text-xs`). No motion.<br>**Suppression.** `suppressed` hides the hint and blocks showing (an open menu). | D-8, D-10, D-11; triage D-48; Session 30 A-10; Research-backed (WAI-ARIA APG tooltip; MUI disabled elements) |
| `HINT_TEXT(label, reason)` | `label` when the control is enabled or `reason` is empty; otherwise `` `${label} — ${reason}` `` (an em dash with a space on each side). `label` is the control's accessible name (its `aria-label`). | D-9 |
| `HINT_TIMING` | **Show:** `pointerenter` on the wrapper shows after `HINT_DELAY_MS` = 400; `focus` (focusin from the wrapper or the child) shows at once.<br>**Hide:** `blur`/focusout hides; `pointerdown` anywhere in the wrapper hides and cancels a pending show; `Escape` keydown on `document` hides, without `preventDefault` or `stopPropagation`.<br>**Hoverable:** `pointerleave` hides after `HINT_GRACE_MS` = 120, unless the pointer enters the hint first; leaving the hint hides after the same grace.<br>**Focus wins:** a hint shown by focus stays until blur or Escape, whatever the pointer does. | D-10, D-11; Research-backed (WCAG 2.2 SC 1.4.13; APG) |
| `TOOLTIP_PLACEMENT` | `position: fixed`, z-50, `max-width: min(32rem, calc(100vw - 16px))`, text wraps.<br>**Vertical.** `top` = trigger `bottom + 6`. If that would put the hint's bottom past `innerHeight - 8`, it flips: `top` = trigger `top - 6 - hintHeight`.<br>**Horizontal.** `left` = trigger centre − hintWidth/2, clamped to `[8, innerWidth - 8 - hintWidth]`.<br>**Measuring.** Done in `useLayoutEffect` after mount, and again on `resize` and on `scroll` (capture phase) while shown. | D-10; Local Canon A-10 (`CapturePage.tsx:1136-1160`) |
| `HINT_SINGLETON` | At most one hint is visible app-wide. Showing one hides any other (a module-level store in `Tooltip.tsx`). | D-10 |
| `HINT_TITLE_RULE` | No `ICON_ONLY_INVENTORY` control, and no Tooltip wrapper, has a `title` attribute, whether the `title` was written in JSX or passed through a spread; Tooltip strips it from the cloned child and never renders one on the wrapper. It is proved in the rendered DOM (AC-80.4, AC-80.8, AC-80.9, AC-81.2: control and `{id}-tip`, enabled and disabled), not by a source grep. Labelled controls keep their titles (for example the queue-card primary action, AC-44.7). | D-12; R1 F6 |
| `ROOT_CAUSE_PROBE` | Row 2, a bounded on-target probe (at most 3 hypotheses, one row). A plan-local `tooltip-probe.mjs` launches the built app under Playwright `_electron`, reads the window's content area as a physical screen rect through `app.evaluate` (`screen.dipToScreenRect` of the content bounds), then for each hypothesis moves the real OS cursor (pwsh `user32!SetCursorPos`) over the centre of `nav-capture` (which has a native `title`) and of a Capture toolbar button that still has its `title` at baseline. After 1500 ms it captures exactly that content rect from the screen (`Graphics.CopyFromScreen`, saved as an 8-bit RGB/RGBA PNG) to `C:/Temp/av-kit/s34-probe-h{n}-{target}.png`, where `{target}` is `nav-capture` or `capture-tool-arrow`. All probe coordinates (cursor, target rect, window) are physical screen pixels. As its last output line the probe prints `PROBE-DONE <the 6 PNG sha256, comma-joined, in H1–H3 × (nav-capture, capture-tool-arrow) order>`, which lands in its receipt `C:/Temp/av-kit/s34-probe-run.txt`.<br>**Hypotheses:**<br>H1 — the window is not foreground (`win.show(); win.focus(); win.moveTop()` first);<br>H2 — the cursor must physically move: a second `SetCursorPos` 3 px away, then wait;<br>H3 — a Chromium switch or `BrowserWindow` option in `ui/src/main/index.ts` suppresses native tooltips (`rg -n "appendSwitch\|disable-features\|tooltip" ui/src/main`).<br>**Run record (`PROBE_RUN`).** `validate-task.ps1 -Check probe` runs `tooltip-probe.mjs --out C:/Temp/av-kit --run C:/Temp/av-kit/s34-probe-run.json`, which writes the observations, then adds the binding fields (D-31), so the record holds: `check: probe` (the producer); `head` (must equal `baseline.sha`); `gated_clean` (no product change against `baseline.sha` at probe time); `build_sha256` (of `ui/out/main/index.js`), `probe_sha256` (of `tooltip-probe.mjs`) and `receipt_sha256` (of `s34-probe-run.txt`); the probe exit code; zoned ISO `started` and `finished` times; and 6 `observations` (H1–H3 × the 2 targets), each with the cursor position, the captured `window` rect, the target's screen rect, the time `at` which it was taken, the target's non-empty `title` attribute read in the page, and the PNG path and sha256.<br>**Output.** The agent views each PNG and records in `walkthrough.md` §Root cause one line per observation (`H{n} {target}: tooltip-visible yes\|no — s34-probe-h{n}-{target}.png`) and a `finding:` line, which is either a cause plus a one-line fix, or `not found`.<br>**Check.** `plan_checks.py root-cause` refuses unless: HEAD is still `baseline.sha` and the tree is clean (row 2 closes on the probed tree); the run record exists with `check: probe`, exit 0, `head` = `baseline.sha` and `gated_clean`; `build_sha256`, `probe_sha256` and `receipt_sha256` are sha256 values equal to the current `ui/out/main/index.js`, `tooltip-probe.mjs` and `s34-probe-run.txt` (a rebuild, a probe edit or a hand-written receipt after the run refuses); `started` precedes `finished` by at most 15 minutes; all 6 observations exist, each taken inside the run, with the cursor inside its target rect and the target rect inside the captured window, and a non-empty title; every PNG decodes (every chunk CRC, IHDR first, IDAT present, IEND last, 8-bit RGB/RGBA non-interlaced, and inflated image data of exactly the size IHDR declares), is exactly the captured window's size and at least 320×200, matches its recorded sha256, and was written during the run (mtime ±2 s); the receipt has exactly one `PROBE-DONE` line naming those 6 hashes in order; and the walkthrough has exactly the 6 observation lines naming those files plus exactly one `finding:` line whose text is `not found` or longer than 10 characters. The binding proves the record came from `-Check probe` on this build; it is not tamper-proof against an agent that rewrites the run, the receipt and the PNGs together, which `GUARDRAILS` already forbids. | Spec 09:684 ("Root cause first"); triage D-48; D-14; R1 F4; D-31 (R2 F4) |
| `ACTION_BUTTONS` | A new export in `capture-toolbar.ts`, keyed by test id, `{icon, name}`:<br>`capture-remove-mark` → `Delete`, "Remove mark";<br>`capture-save` → `Save`, "Save overlay";<br>`capture-apply-image` → `Stamp`, "Apply to image";<br>`capture-revert-image` → `ArchiveRestore`, "Revert image";<br>`capture-open-file` → `ExternalLink`, "Open file";<br>`capture-open-folder` → `FolderOpen`, "Open folder";<br>`capture-delete` → `Trash2`, "Delete shot".<br>All seven icons exist in the locked `lucide-react` 0.400.0. `ActionButtonId` is its key union. `TOOLBAR_BUTTONS` is unchanged. | Human-approved D-49 icon proposal; D-15 |
| `ICON_BUTTON` | `ToolbarIconButton` moves to `ui/src/renderer/src/features/capture/ToolbarIconButton.tsx`. It takes `spec: ToolbarButtonSpec`, `id`, `variant: 'primary' \| 'secondary' \| 'outline' \| 'ghost' \| 'destructive'`, `pressed?`, `disabled?`, `reason?` and `onClick`. It renders `TOOLTIP` around `<Button size="sm" aria-label={name}>` with the 16 px icon as its only child (`aria-hidden`). There is no `title`. `CaptureViewport.tsx` and `CapturePage.tsx` both import it. | Local Canon ICON_BUTTON_RULE (`CaptureViewport.tsx:305`); D-15 |
| `ACTION_ORDER` | Left to right, in the marks row's action slot:<br>Remove mark (`ghost`, mounted when a mark is selected), Save overlay (`primary`, mounted iff dirty), Apply to image (`secondary`), Revert image (`secondary`, mounted iff a backup exists), `{reasonLabel}` retired, Open file (`ghost`), Open folder (`ghost`), the separator `<span role="separator" aria-orientation="vertical" data-testid="capture-actions-separator" className="mx-1 h-5 w-px shrink-0 bg-border">`, then Delete shot (`destructive`) last.<br>Each action's enabled and mounted rules (`canSave`, `APPLY_ENABLED`, `REVERT_VISIBLE`, the Open and Delete guards) are unchanged. Disabled reasons pass through `reason` (`apply.title`, `revert.title`). | Human-approved D-49; Session 30 `APPLY_ENABLED`/`REVERT_VISIBLE`; AC-39.28 (Delete stays destructive) |
| `RETIRED_CONTROLS` | Removed from the product:<br>`capture-nudge-body`, `-tail`, `-head`, `-left`, `-right`, `-up`, `-down` and `capture-color-sample`;<br>the `CaptureViewport` props `nudgeTarget`, `sampling`, `sampleReady`, `onColorSample`, `onNudgeTarget`, `onNudgeStep` and the `NudgeTarget` export;<br>`CapturePage` sampling state, the sample effect and handlers, and the Esc "cancel sampling" branch;<br>the module `features/capture/capture-sample.ts`;<br>the A-10 `reasonTip` state, `showReason`, `hideReason`, `reasonLabel` and the `capture-apply-image-reason`/`capture-revert-image-reason` ids. The A-10 items go in MEU-80, where `TOOLTIP` replaces the reason label on Apply to image and Revert image (D-8). Everything else goes in MEU-81. | Human-approved D-49, D-51; D-8 |
| `NUDGE_TARGET` | Internal `CapturePage` state `'body' \| 'from' \| 'to'`.<br>**Grab.** A Select-mode pointerdown whose `hitTestMarks` result is a handle (`hit.kind === 'handle'`) sets it to `hit.end`.<br>**Focus.** Focusing `capture-handle-from` or `capture-handle-to` selects nothing new and sets it to that end.<br>**Handle layer (`HANDLE_LAYER`).** The two arrow handle circles move out of the `aria-hidden` marks `<svg>` (`CaptureViewport.tsx:1147-1180`) into a second `<svg data-testid="capture-handle-layer">` with the same `viewBox`, `preserveAspectRatio` and `absolute inset-0 w-full h-full pointer-events-none` classes, rendered inside `capture-zoom-content` (`CaptureViewport.tsx:1134`) as the next sibling after the marks `<svg>`, and with no `aria-hidden` (D-32). Sharing the marks `<svg>`'s parent means the layer gets the same zoom box (`contentStyle`, `:632-635`: `left: view.ox`, `top: view.oy`, `width: imageWidth × view.s`, `height: imageHeight × view.s`), so a handle drawn at image `(cx, cy)` with `r={handleRadius}` (`:404`, `HANDLE_RADIUS_CSS / view.s`) lands on the arrow's end at every zoom and pan, at a constant `2 × HANDLE_RADIUS_CSS` CSS px across. `capture-zoom-content` is `pointer-events-none` and not `aria-hidden`, which keeps the layer focusable by keyboard and out of pointer hit-testing. Each circle gets `tabIndex={0}`, `role="button"`, `aria-label` "Arrow tail" / "Arrow head", `pointer-events: none` (a grab still goes through the surface's `hitTestMarks`, unchanged) and a focus ring (token stroke on `:focus-visible`). The body handle stays in the marks `<svg>`. Because the circles are descendants of `capture-draw-surface`, their keydown bubbles to the surface's single existing `onKeyDown` (`:1005-1010`); no second key owner is added.<br>**Focus ownership.** `annotationOwnsFocus()` (`CapturePage.tsx:102-118`) accepts any `Element` (`instanceof Element`, not `HTMLElement`), so a focused SVG circle owns annotation keys; the confirm-strip and `COLOR_FOCUS_IDS` exclusions are unchanged. `spaceArmable` (`CaptureViewport.tsx:531-537`) treats `[role="button"]` as a control, so Space on a focused handle does not arm pan.<br>**Reset.** Any selection change, tool change, shot change or mark removal resets it to `body`, and so does focus landing on `capture-draw-surface` itself (`event.target === event.currentTarget` in a `focus` handler).<br>**Arrow keys.** They move `translateBody` when it is `body` or the mark is not an arrow, and otherwise `moveEndpoint(mark, NUDGE_TARGET, …)`, by `KEYBOARD_NUDGE_PX`. They are handled only while `annotationOwnsFocus()` and no pointer gesture is live (`pressed`, `moving`, `endpointDragging`). Burst history (`finishNudge`) and Esc rollback are unchanged. | Human-approved D-49 ("Arrow keys should then nudge the whole selected mark, or the endpoint being dragged or focused"); D-17; D-26 (R1 F2) |
| `HELP_EDIT_TEXT` | The `capture-help-content.ts` four-tools sentence that replaces "Select a mark … Sample original image fills the color code; Apply commits color.":<br>"Select a mark to move it or drag an arrow end until Save. Arrow keys nudge the selected mark, or the arrow end you grabbed or tabbed to; Apply commits color." | D-49, D-51 |
| `MARKS_ROW_LAYOUT` | `capture-chrome-marks` gets `flex flex-nowrap items-center gap-1 shrink-0 min-h-9` and no `overflow-x-auto`. `capture-mark-list` gets `flex min-w-0 flex-1 items-center gap-1 overflow-x-auto` (only the chips scroll). The action slot is `ml-auto flex shrink-0 items-center gap-1 pl-2`. | Triage D-50; D-18 |
| `NO_OVERFLOW_FIXTURE` | Electron, 1280×800 default window, one PNG shot seeded with 12 saved marks (3 per type), a dirty overlay (Save mounted), a backup (Revert mounted), an arrow selected (Remove mark mounted).<br>**Settling.** Before measuring: `await document.fonts.ready`, then `twoFrames`.<br>**Assertions.** `capture-chrome-marks` `scrollWidth ≤ clientWidth`; its `offsetHeight` equals its `scrollHeight` and is at least 36 px; every action's trigger wrapper (`{id}-tip`, the "tip box"; not the `{id}-hint` popup) lies inside the row box (±0.5 px); Delete's tip is the rightmost.<br>**Variants.** Repeated with the Text tool selected and the Options disclosure open. | Triage D-50 (NO_OVERFLOW as AC-65.4); D-18 |
| `HEADER_STATUS` | The Capture header row gets `data-testid="capture-header"` and the classes `flex flex-nowrap items-center gap-3`. The count paragraph gets `min-w-0 truncate`.<br>`capture-hotkey-banner` (the id is kept; AC-39.5 pins it in source) becomes `<p role="status" className="flex shrink-0 items-center gap-2 text-sm">`, a child of `capture-header` placed after the count paragraph. It is mounted **only** when `hotkeyInUse`, holding `<StatusChip label="Hotkey" tone="warning"/>` and the `HOTKEY_IN_USE_TEMPLATE` text.<br>The reserved band (`min-h-4`, always mounted, `CapturePage.tsx:1390-1397`) is removed. | Human-approved D-64; D-19 |
| `HOTKEY_IN_USE_FIXTURE` | **Hold.** Before launching the app, the Electron test spawns `pwsh -NoProfile -Command` running a P/Invoke `user32!RegisterHotKey(IntPtr.Zero, 0x5334, 0, 0x71)` (F2, no modifiers). It prints `HELD` and sleeps; the test waits for `HELD`.<br>**In-use run.** The app's own `globalShortcut.register('F2')` then fails, so `window.api.getHotkeyStatus().inUse` is true.<br>**Free run.** A second launch with no helper.<br>**Helper lifecycle.** The helper prints `HELD` only after `RegisterHotKey` returns true, and otherwise prints `FAILED <GetLastError>` and exits 1. It then blocks on `GetMessage` in the same thread that registered (a hotkey belongs to its registering thread). The test spawns it before any app launch, and the whole in-use run (spawn, wait for `HELD`, launch, measure, app close) sits in one `try`; its `finally` closes the in-use app, kills the helper and awaits its `exit` event (5 s cap), on every path including spawn failure, `FAILED`, the 5 s `HELD` timeout and a launch failure.<br>**Order.** The free run starts only after that `finally` completes, so the in-use app is closed and the helper has exited before the second launch.<br>**Precondition.** If `getHotkeyStatus()` reports `inUse` in the free run, or the helper prints `FAILED` or no `HELD` within 5 s, the test fails with "F2 held by another process" (Stop condition S4). | D-20; Research-backed (Win32 RegisterHotKey; Electron globalShortcut); R1 Q4 |
| `HEADER_GEOMETRY` | Measured in both runs at 1280×800 with Options closed, after `twoFrames`: `capture-header` `getBoundingClientRect().height` and `capture-viewport` `top`. In-use minus free is within ±0.5 px for both. In the in-use run, `capture-hotkey-banner`'s box lies inside `capture-header`'s box, and its `scrollWidth ≤ clientWidth` (no truncation). | Human-approved D-64 ("nothing shifts"); D-19 |
| `RETIRED_TESTIDS` | The 8 `test-ids.ts` constants removed from the AC-51.6-hashed prefix: `CAPTURE_COLOR_SAMPLE` (`:230`), `CAPTURE_NUDGE_BODY`, `_TAIL`, `_HEAD`, `_LEFT`, `_RIGHT`, `_UP`, `_DOWN` (`:234-240`). The new prefix equals the baseline prefix minus exactly these 8 lines (`plan_checks.py registry`). | D-21 |
| `NEW_TESTIDS` | Appended after the MEU-67 block (`test-ids.ts:417`) under `// MEU-80/81 icon hints and the Capture action row (additive IDs).`:<br>`CAPTURE_HEADER = 'capture-header'`, `CAPTURE_ACTIONS_SEPARATOR = 'capture-actions-separator'`, `CAPTURE_REMOVE_MARK_TIP = 'capture-remove-mark-tip'`, `CAPTURE_TOOL_ARROW_HINT = 'capture-tool-arrow-hint'`, `CAPTURE_UNDO_TIP = 'capture-undo-tip'`, `CAPTURE_UNDO_HINT = 'capture-undo-hint'`, `CAPTURE_APPLY_IMAGE_TIP = 'capture-apply-image-tip'`, `CAPTURE_APPLY_IMAGE_HINT = 'capture-apply-image-hint'`, `CAPTURE_DELETE_TIP = 'capture-delete-tip'`, `CONSOLE_CLOSE_HINT = 'console-close-hint'`. | E2 (every E2E-used id registered); AC-65.7/66.17/67.26 block order |
| `HUB_EDITS` | The exact build-plan edits of task row 10 (§BUILD_PLAN.md Audit items 1–4). | D-22, D-23 |
| `GATE` | `validate-task.ps1 -Check gate` runs the fresh full D6 stage list, in this order: `ui-ci`, `mcp-ci`, `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `py-tests`, `ui-tests`, `ui-build`, `ui-harness-build`, `mcp-build`, `mcp-tests`, `openapi`, `state-render`, `ui-electron`, `source-audit`.<br>It writes `gate-result.json` (schema `s34-gate.v2`) with `identity_before` (`plan_checks.py identity`), each stage's argv/exit/receipt (for `ui-tests`, `exit` is the verdict of `plan_checks.py vitest-ok --meu 81` on that stage's raw reports and `raw_exit` is Vitest's own exit, because `BASELINE_RED` makes Vitest exit 1), the paths of the raw Vitest and Playwright JSON reports and the Vitest text receipt with the sha256 of each (`vitest_json_sha256`, `vitest_txt_sha256`, `e2e_json_sha256`), `check: gate` (the producer), the pytest summary, and `identity_after` (D-31).<br>`validate-task.ps1 -Check gate-check` refuses unless: the result has `check: gate` and each named raw report exists with the recorded sha256 (a report replaced or hand-written after the gate refuses); every stage's `exit` is 0, in this order; the raw reports pass `CASE_EVIDENCE` (every `AC_CASES` unit and integration case and every `TA_TAGS` tag collected and passed, no skips among them, no Vitest failure but `BASELINE_RED`, Electron `unexpected` = `flaky` = `skipped` = 0, no unhandled errors in the text receipt); `COUNT_FLOORS` hold as a supplementary check; `identity_before` = `identity_after` = a fresh `plan_checks.py identity`. | D-24; PROFILE D6; D-27; D-31 |
| `IDENTITY_SCOPE` | The gate identity is a SHA-256 over the sorted (path, file sha256) pairs of **every** git-visible file (`git ls-files -co --exclude-standard`), except `IDENTITY_EXCLUDE`: this plan folder's `walkthrough.md`, `gate-result.json` and `task.md`, and the prefixes `.agent/context/handoffs/` and `docs/execution/reflections/`. That covers the product, `native/`, the plan-local checkers, and every doc a test reads (for example `layout-canon` reads the build plan, the grouping file and `meu-status.yaml`; `gui-actions-audit` reads `gui-actions-index.md`). So every row that changes a hashed file (row 10, and the H1-2 SSOT updates) runs before `GATE`; only the excluded files may change after it. The H2 rows run after approval and change only `ADMIN_PATHS` and excluded files; the identity binds the reviewed tree, not the post-approval state. | D-24; D-29 (R1 F5) |
| `COUNT_FLOORS` | Vitest total ≥ 773 and Electron expected ≥ 133; pytest failed 0 and passed ≥ 655. These are the Session 30 gate-of-record counts (`2026-10-02-capture-flatten-backup/windows-gate-result.json`, Electron skipped 0). New tests outnumber the removed ones (`TEST_AMENDMENTS` deletes 1 Vitest file and 2 cases). The floors are supplementary: `CASE_EVIDENCE` is the decisive check. | Local Canon S30 gate |
| `BASELINE_RED` | Exactly one existing test may fail in any Vitest run of this plan: `queue-canon.test.ts` AC-41.3, and only with the message `--color-accent-cyan light diverges from PILL_TOKEN_SOURCE`. It reads the live `P:/zorivest/ui/src/renderer/src/globals.css`, whose light accent-cyan is now `#0e7490`, while main's `styles.css:89` still has `#0891b2`. Session 31 commit `da1d111` (unmerged branch `claude/vigilant-volta-f04tvs`) ports the fix. This plan does not touch `styles.css`. The test may fail but never must; any other failure is real. `plan_checks.py` (`is_baseline_red`) enforces this in `baseline`, every Red, Green and gate evaluation. If Session 31 merges first, this branch rebases on main before row 0 and the tolerance goes unused. | plan-time check 2026-10-14; Session 38 plan `BASELINE_RED` (same failure); D-30 |
| `AC_CASES` | The case manifest in `plan_checks.py`: for every unit and integration AC, its runner (`vitest` or `e2e`), its test file and its Red class:<br>`red-import` — the file cannot load at Red because the module it tests does not exist yet (only `tooltip.test.tsx`, on `components/ui/Tooltip`); each case's title must still appear in the file source;<br>`red` — collected, not skipped, and failed by an assertion (`ASSERTION_FAILURE`);<br>`guard` — a regression guard of behaviour that already exists (for example arrow keys already nudge the body): collected and not skipped; it may pass or fail by assertion at Red. The `guard` cases are AC-81.3, AC-81.5, AC-81.7 and AC-81.15; every other case of a loading file is `red`.<br>Each case is one test whose title contains its AC id (`AC-81.6:` matches `AC-81.6` and never `AC-81.60`). `plan_checks.py static` asserts the manifest's AC set equals this plan's unit and integration AC rows, and each file equals the file named in §NEW files, and the `red-import` and `guard` sets equal the ones named here. | D-27 (R1 F3) |
| `ASSERTION_FAILURE` | A failed case counts as Red only when its first failure message starts with `AssertionError`, `Error: expect(` or `TestingLibraryElementError` (Vitest), or carries `expect(` and no `TypeError`/`ReferenceError`/`SyntaxError` (Playwright). A Red test asserts that a thing exists before it uses it, so a missing export or element fails as an assertion. | D-27 |
| `SETUP_SENTINEL` | Each new Vitest file that loads at Red (`icon-hints.test.ts`, `capture-action-row.test.ts`) has a first case titled `setup sentinel` that runs the file's shared render harness and asserts the page mounted. At Red it must pass, which proves the AC failures are not setup failures. | D-27 (R1 F3) |
| `TA_TAGS` | Every existing test whose body a `TEST_AMENDMENTS` row changes gains the title suffix ` [TA-n]` (one per row, several if several rows change it), applied in the same edit. TA-4 and TA-17 delete their tests and carry no tag. A Red failure outside the run's AC tag is tolerated only when its title carries a `TA-n` tag of a row the same task row applies, in the file that TA row names, or when it is `FIXTURE_RED` at row 3; any other failure is Stop condition S2. At Green and in `GATE`, every tag of the non-deleting rows is collected and passed. | D-27 (R1 F3) |
| `AUDIT_SRC` | The `source-audit` stage scans: `ui/src/renderer/src/components/ui/Tooltip.tsx`, `ui/src/renderer/src/features/capture/ToolbarIconButton.tsx`, `ui/src/renderer/src/features/capture/CaptureViewport.tsx`, `ui/src/renderer/src/features/capture/CapturePage.tsx`, `ui/src/renderer/src/features/capture/capture-toolbar.ts`, `ui/src/renderer/src/components/layout/ConsolePanel.tsx`, `ui/src/renderer/src/components/queue/BulkResultToast.tsx`, `ui/src/renderer/src/components/queue/QueueCard.tsx`, `ui/src/renderer/src/components/queue/QueueCardMenu.tsx`, `ui/src/renderer/src/features/transcript/TranscriptPage.tsx`, `ui/src/renderer/src/features/converter/ConvertPage.tsx`. Pattern: `TODO\|FIXME\|transition-all\|bg-\[#\|console\.log\(\|@ts-ignore\|@ts-expect-error\|: any\b`.<br>` title=` is not in the pattern: these files keep legitimate titles on labelled controls (for example ConvertPage "Advanced", QueueCard's primary action, AC-44.7). `HINT_TITLE_RULE` is enforced by AC-80.4 (the wrapped child's `title` is not rendered), AC-80.7 (no `title=` in `Tooltip.tsx`) and AC-80.8/80.9 (no inventory control has a `title`). | G32, G33 |
| `CHROME_LOOK` | L1–L8 in §Look checklist: Mat's one-line `pass`/`fail` per item, recorded in `walkthrough.md` §CHROME_LOOK with the tested commit. | Local Canon S29/S30 looks |

### TEST_AMENDMENTS

Only these rows change existing expectations, and only as written. File paths are relative to `ui/tests/`. Any other existing test that fails against this design is Stop condition S2.

| TA | File:line | Current expectation | Amended expectation | Basis |
|---|---|---|---|---|
| TA-1 | `unit/capture-page.behavior.test.ts:695-746` (AC-60.10) | A nudge burst is opened by clicking `capture-nudge-body` (`:715`) | The burst is opened by an `ArrowRight` keydown on the focused surface, with no keyup | D-49 |
| TA-2 | `unit/capture-page.behavior.test.ts:748-785` (AC-60.13) | Sample is visible (`:755`) | That line is removed; the rest is unchanged | D-51 |
| TA-3 | `unit/capture-page.behavior.test.ts:786-828` (AC-60.19) | Body/Tail/Head inspector buttons exist and choose the target (`:789-794`, `:811`, `:822`) | Focusing `capture-handle-from`/`-to` chooses the target (`NUDGE_TARGET`); the Delete-focus and Esc-without-history parts are unchanged | D-49 |
| TA-4 | `unit/capture-page.behavior.test.ts:829-877` (AC-60.9 sampler decode miss) | Sampling state and decode failure | Test deleted | D-51 |
| TA-5 | `unit/capture-page.behavior.test.ts:878-888` (AC-60.19 labels) | The inspector and pad buttons are labelled | The handles carry `aria-label` "Arrow tail"/"Arrow head" and `tabIndex` 0 | D-49 |
| TA-6 | `unit/capture-page.behavior.test.ts:889-915` | Tail/head are hidden for non-arrow marks; the pad moves the object | For a box, arrow keys move the body; no handle renders for non-arrow marks | D-49 |
| TA-7 | `unit/capture-page.behavior.test.ts:1007-1031` (AC-57.2, AC-57.3) | In use: banner with chip. Free: banner mounted with `min-h-4`, empty | In use: the banner is inside `capture-header` with chip and text. Free: `queryByTestId('capture-hotkey-banner')` is null | D-64 (amends AC-57.3) |
| TA-8 | `unit/capture-page.behavior.test.ts:1075` (AC-57.5) | Disabled Box tool `title` matches /shot/ | Focusing `capture-tool-box-tip` shows `capture-tool-box-hint` matching /shot/; `title` is null | D-12 |
| TA-9 | `unit/capture-page.behavior.test.ts:1083-1095` (AC-57.6) | Save text matches /Save overlay/ (`:1088`) | Save's accessible name is "Save overlay" and its text is empty | D-49 |
| TA-10 | `unit/capture-page.behavior.test.ts:1221-1232` (`MEU65_OPTION_IDS`) | The color options include `capture-color-sample` | Entry removed (affects `:1306`, `:1323` unchanged otherwise) | D-51 |
| TA-11 | `unit/capture-page.behavior.test.ts:1263`, `:1297`, `:1518` | Toolbar `title` equals the name, or 'Select a shot first' | `title` is null on the button and on `${id}-tip`. Disabled: focusing `${id}-tip` (the wrapper is the tab stop) shows `${id}-hint` with `HINT_TEXT(name, 'Select a shot first')`. Enabled: focusing the **button** `${id}` (the wrapper has no `tabindex`) shows `${id}-hint` with `name` | D-9, D-12; R1 Q6 |
| TA-12 | `unit/capture-page.behavior.test.ts:2244-2272`, `:2384-2396` (AC-67.20, AC-67.23) | Apply/Revert `title` holds the reason, or null | `title` is null; the focused tip shows `HINT_TEXT('Apply to image' \| 'Revert image', reason)` | D-9, D-12 |
| TA-13 | `unit/capture-page.behavior.test.ts:2250` | `delete.parentElement` is the Apply tip's parent | `capture-delete-tip.parentElement` is the Apply tip's parent | D-8 |
| TA-14 | `unit/capture-page.behavior.test.ts:2426-2450` (A-6) | The wrapper `title` holds the reason | The wrapper has no `title`; focusing it shows the reason through the hint | D-8, D-12 |
| TA-15 | `unit/capture-page.behavior.test.ts:2452-2475` (AC-67.35) | `capture-apply-image-reason`, `capture-revert-image-reason` on disabled hover; and no reason label on enabled hover (`:2458-2460`) | Disabled: `capture-apply-image-hint`, `capture-revert-image-hint`, text `HINT_TEXT(name, reason)`. Enabled: the old "no reason label" check becomes: after hover plus `HINT_DELAY_MS`, the hint shows the plain name (`HINT_TEXT(name, '')`), and after leaving plus `HINT_GRACE_MS` it is gone | D-8, D-9; R1 Q6 |
| TA-16 | `unit/capture-help-content.test.ts:8-9` | `HELP_EDIT_SENTENCE` = the Sample sentence | `HELP_EDIT_SENTENCE` = `HELP_EDIT_TEXT` | D-51 |
| TA-17 | `unit/capture-sample.test.ts` | The module loads | File deleted with the module | D-51 |
| TA-18 | `e2e/capture-inbox.test.ts:236` (W9-3) | The banner is visible | The banner is visible iff `window.api.getHotkeyStatus()` reports `inUse` | D-64 |
| TA-19 | `e2e/capture-inbox.test.ts:477-630` (AC-60.12) | Color comes from Sample (`:609-613`) | Color comes from typing the same hex in `capture-color` (the hex input) and Apply; the later assertions are unchanged | D-51 |
| TA-20 | `e2e/capture-inbox.test.ts:766` (AC-57.10) | Save contains the text "Save overlay" | Save has `aria-label` "Save overlay" | D-49 |
| TA-21 | `e2e/capture-inbox.test.ts:845-868` (AC-65.4 helpers) | `chromeRows` reads tools and options | It also reads `capture-chrome-marks`; `expectNoOverflow` asserts all three | D-50 |
| TA-22 | `e2e/capture-inbox.test.ts:1446` | Apply `title` = 'Save the overlay first' | The Apply hint shows `HINT_TEXT('Apply to image', 'Save the overlay first')` on hover | D-12 |
| TA-23 | `e2e/capture-inbox.test.ts:1552-1578` (A-6) | Walks up from the pointer to a `title` | The hint `capture-apply-image-hint` is visible after hovering where the pointer lands | D-8 |
| TA-24 | `e2e/capture-inbox.test.ts:1580-1607` (AC-67.35) | `capture-apply-image-reason` on disabled hover; no reason label on enabled hover (`:1588-1590`) | Disabled: `capture-apply-image-hint` with `HINT_TEXT`. Enabled: after real hover and `HINT_DELAY_MS`, the hint shows the plain name; after moving away and `HINT_GRACE_MS`, its count is 0 | D-8; R1 Q6 |
| TA-25 | `unit/queue-card.test.ts:1245`, `:1296` | The drag handle leads the row and hangs off the card | `queue-card-drag-handle-tip` leads the row and hangs off the card, and contains the handle as its only child. `:1261`'s `aria-describedby` = `DndDescribedBy-0` assertion is unchanged (`DESCRIBEDBY_COMPOSE` keeps it while the hint is hidden) | D-8; D-25 |
| TA-26 | `unit/layout-primitives.test.ts:200-214` (AC-51.6) | Prefix hash `819760B9…8A73` | The re-pinned hash of the new prefix (`RETIRED_TESTIDS`) | D-21 |
| TA-27 | `e2e/download-queue.test.ts:1339` (AC-49.27) | After focusing the handle: Space, then a wait for any `document` keydown listener (`keydownListenerCount > 0`) before ArrowDown | After focusing the handle the test waits for `queue-card-drag-handle-hint` and zeroes the count, then presses Space and keeps the `> 0` wait. Position 2 of 4, the PUT body and the focus return are unchanged. Added at H1-3 (`walkthrough.md` A-9) | D-37 |
| TA-28 | `e2e/convert-queue.test.ts:1243`, `:1284` (AC-52) | The same wait as TA-27, in both converter keyboard-drag tests | The same change as TA-27 in both tests; the moved-row and rejected-reorder expectations are unchanged. Added at H1-3 (`walkthrough.md` A-9) | D-37 |

### FIXTURE_REPAIRS

| Id | Fixture | Exact change | Check |
|---|---|---|---|
| (a) | `ui/tests/unit/fixtures/queue-slot-baseline.json` key `doneWithMenu` | The kebab `<button …data-testid="queue-card-kebab"…>` loses ` title="Actions for Done job"`, and is wrapped in `<span data-testid="queue-card-kebab-tip" class="inline-flex">…</span>`. The other three keys are byte-identical. | `plan_checks.py fixture --baseline <sha>` reproduces the transformation from the baseline string and compares |

**`FIXTURE_RED`.** (a) lands at row 3, before `QueueCard.tsx` changes at row 4, so its one consumer case, `queue-card-slots.test.tsx` `AC-55.1 a card with no slot renders the exact pre-change markup` (it compares `container.innerHTML` with the fixture), fails at row 3's Red by assertion. `vitest-red --meu 80` tolerates exactly that file and title, by assertion, at MEU-80's Red only; MEU-81's Red, every Green, the targeted gates and `GATE` require it to pass.

### NEW Vitest and Electron files

- `ui/tests/unit/tooltip.test.tsx` (AC-80.1–80.7, AC-80.13)
- `ui/tests/unit/icon-hints.test.ts` (AC-80.8, AC-80.9)
- `ui/tests/unit/capture-action-row.test.ts` (AC-81.1–81.8, AC-81.10, AC-81.12, AC-81.13, AC-81.15)
- Appended Electron tests in `ui/tests/e2e/capture-inbox.test.ts` (AC-80.10, AC-81.9, AC-81.11, AC-81.14) and `ui/tests/e2e/console-chrome.test.ts` (AC-80.11)

### MEU-80 — `gui-icon-button-hints`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Tooltip props (renderer component) | TypeScript props type in `Tooltip.tsx` | `id` non-empty, `label` non-empty, `reason` optional string, child a single element | Excess props are compile errors (`tsc --noEmit`) |

There is no REST, MCP, IPC or file boundary.

#### Acceptance Criteria

Unit tests render with Testing Library in jsdom, with fake timers for `HINT_TIMING`. Electron tests use real pointer input (Playwright `hover`, which sends real Chromium mouse events) on the built app.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-80.1 | unit | Hover: `pointerenter` on `{id}-tip` shows, after `HINT_DELAY_MS`, one `role="tooltip"` `{id}-hint` that is a child of `document.body` (portaled, not inside the wrapper), with text `HINT_TEXT`. While shown, the focus target's `aria-describedby` token list contains the hint id (`DESCRIBEDBY_COMPOSE`). | Spec 09:682-683; `TOOLTIP`, `HINT_TIMING` | At `HINT_DELAY_MS − 1` there is no hint; the wrapper contains no `role="tooltip"` |
| AC-80.2 | unit | Focus: focusing the button shows the hint at once; blur hides it; while hidden, the focus target's `aria-describedby` does not contain the hint id (absent when the child had none). | Spec 09:682 ("keyboard focus"); APG | Focusing an unrelated button never shows this hint |
| AC-80.3 | unit | Dismissal (WCAG 1.4.13): `Escape` hides the hint, and a later `document` keydown listener still receives the event with `defaultPrevented` false. `pointerdown` hides and cancels a pending show. `pointerleave` hides after `HINT_GRACE_MS`, unless the pointer enters the hint within the grace. Leaving the hint hides it. | `HINT_TIMING`; D-11 | A hint entered from the trigger stays at `HINT_GRACE_MS + 50` |
| AC-80.4 | unit | Disabled child: the wrapper has `tabIndex` 0 and receives the hint id in `aria-describedby`, and focusing the wrapper shows the hint. Enabled child: the wrapper has no `tabindex` attribute and the child's `aria-describedby` receives the hint id. In both cases neither the child nor the wrapper renders a `title`, including when the child's `title` arrives through a spread (`{...{ title: 'x' }}`). | Spec 09:683 ("disabled buttons get a focusable wrapper"); triage D-48; D-8, D-12; R1 F6 | An enabled wrapper is not a tab stop (`getAttribute('tabindex')` null); a spread `title` is not rendered |
| AC-80.5 | unit | `HINT_TEXT` and `HINT_SINGLETON`: enabled → label; disabled with a reason → `label — reason`; disabled without one → label. Showing hint B hides hint A. `suppressed` hides a shown hint and blocks show on hover and focus. | D-9, D-10 | With `suppressed`, hover past `HINT_DELAY_MS` shows nothing |
| AC-80.6 | unit | `TOOLTIP_PLACEMENT` with stubbed `getBoundingClientRect` and `innerWidth`/`innerHeight`: centred below; clamped at 8 px on the left and right edges; flipped above near the bottom edge. | D-10 | A trigger at x = 2 never yields a negative `left` |
| AC-80.7 | unit | Source guard for `Tooltip.tsx`: it imports nothing from `features/`; it has no hex colour, `transition-all` or `title=`; it calls `createPortal(` with `document.body`; it uses `bg-bg-elevated`, `text-fg` and `border-border`. | G32, G33, AC-51.5 rules; D-12 | A hex colour, a `features/` import or `transition-all` fails the guard (checked by mutating a copy of the source in the test) |
| AC-80.8 | unit | Capture inventory: with a shot open, each of the 12 `TOOLBAR_BUTTONS` sits in `{id}-tip`, neither the button nor `{id}-tip` has a `title`, and focusing the button shows `{id}-hint` with its name. With no shot, neither node has a `title` and focusing a disabled tool's tip shows `HINT_TEXT(name, NO_SHOT_HINT)`. | Spec 09:682; D-13; R1 F6 | The `nav-capture` rail item is not wrapped (no `nav-capture-tip`) |
| AC-80.9 | unit | Non-Capture inventory: `console-close`, `bulk-toast-dismiss`, `queue-card-drag-handle`, `queue-card-kebab`, `up-btn`, `down-btn` and `convert-staged-remove` each sit in `{id}-tip`, have a non-empty `aria-label`, have no `title` on the control or on `{id}-tip` (enabled, and disabled where the control can be disabled), and on focus show `{id}-hint` equal to the `aria-label`. `queue-card-kebab` hides its hint while its menu is open (`suppressed`). `queue-card-drag-handle` keeps `DndDescribedBy-0` in `aria-describedby` while its hint is hidden and while it is shown, and the `listeners` passed to it (`onKeyDown`, `onPointerDown`, as `queue-card.test.ts:1212` mocks them) still fire on the handle. The real keyboard drag stays proved by the existing Electron AC-49.27 (`download-queue.test.ts:1339`), which `GATE` runs. | Spec 09:682 ("every icon-only function button"); D-13; D-25 (R1 F1); R1 F6 | The labelled queue-card primary action keeps its `title` (AC-44.7) and has no tip; the drag handle never loses `DndDescribedBy-0` |
| AC-80.10 | integration | Electron, Capture, real hover at 1280×800: `capture-tool-arrow` (enabled, shot open) shows `capture-tool-arrow-hint` "Arrow", inside the window. `capture-undo` (disabled, no history) shows `capture-undo-hint` with `HINT_TEXT`. `capture-undo-tip.focus()` shows it, and `Escape` hides it. | Spec 09:685 (Electron real hover, enabled and disabled) | Before hover, `capture-tool-arrow-hint` has count 0; after moving the mouse to the page corner it returns to 0 |
| AC-80.11 | integration | Electron, outside Capture: hovering `console-close` shows `console-close-hint` "Close console" inside the window; moving away hides it. | D-13 (shared primitive, one non-Capture surface) | Hovering `nav-capture` shows no `role="tooltip"` |
| AC-80.12 | integration | `ROOT_CAUSE_PROBE` ran on the target: the `PROBE_RUN` record was produced by `-Check probe` and binds the run to `baseline.sha`, the current build, probe script and receipt, with 6 observations taken during the run; the 6 PNGs decode as window-sized captures written during the run and matching their recorded hashes and the receipt's `PROBE-DONE` line, and `walkthrough.md` §Root cause has the 6 observation lines and a `finding:` line. A found fix is recorded and not applied (`PRODUCT_SCOPE`). | Spec 09:684; triage D-48; D-14; D-28 (R1 F4); D-31 (R2 F4) | `-Check root-cause` refuses a missing run record, a record without producer evidence (round 2's metadata-free record with header-only PNGs), a build, probe script or receipt that differs from the recorded hash, a missing or reordered `PROBE-DONE` line, an observation or PNG outside the run, a header-only, bad-CRC, truncated, wrong-size, one-byte or wrong-hash PNG, a missing observation or a placeholder line (`plan_checks.py selftest` proves each refusal, and each negative must refuse for its named reason) |
| AC-80.13 | unit | `DESCRIBEDBY_COMPOSE` and child preservation: an enabled child rendered with `aria-describedby="pre-1"`, a callback ref and an `onKeyDown` handler has `aria-describedby` exactly `pre-1` while hidden and `pre-1 <hintId>` while shown, and `pre-1` again after hide; its ref receives the button element; its `onKeyDown` still fires. The same for a disabled child, whose wrapper carries only the hint id. | D-25 (R1 F1); APG | The child's own `pre-1` token is never removed, and the hint id is never left behind after hide |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Which buttons get a hint | Human-approved | D-69; `ICON_ONLY_INVENTORY` (D-13) |
| Primitive shape (portal, fixed, role, describedby) | Spec | 09:683 |
| Disabled buttons | Spec + Research-backed | 09:683 focusable wrapper; MUI disabled-elements pattern (D-8) |
| Show delay, grace, Escape | Research-backed | APG tooltip; WCAG 1.4.13 (D-10, D-11) |
| Hint wording when disabled | Local Canon | A-10 showed the reason; the name is added now that the buttons have no words (D-9) |
| `title` on wrapped controls | Local Canon | Avoids two hints if native tooltips ever appear (D-12) |
| Root-cause procedure | Spec | 09:684, bounded by D-14 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/components/ui/Tooltip.tsx` | new | `TOOLTIP`, `HINT_TEXT`, `HINT_TIMING`, `TOOLTIP_PLACEMENT`, `HINT_SINGLETON` |
| `ui/src/renderer/src/features/capture/ToolbarIconButton.tsx` | new | `ICON_BUTTON` (moved from `CaptureViewport.tsx:295-322`, wraps `TOOLTIP`) |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | Imports `ICON_BUTTON`; the 12 toolbar buttons pass `reason` instead of `disabledHint` |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | The A-10 reason label on Apply to image and Revert image is replaced by `TOOLTIP` (`reason` = `apply.title`/`revert.title`); both buttons lose `title` (`RETIRED_CONTROLS`, A-10 part) |
| `ui/src/renderer/src/components/layout/ConsolePanel.tsx` | modify | `console-close` in `TOOLTIP` |
| `ui/src/renderer/src/components/queue/BulkResultToast.tsx` | modify | `bulk-toast-dismiss` in `TOOLTIP` |
| `ui/src/renderer/src/components/queue/QueueCard.tsx` | modify | `queue-card-drag-handle` in `TOOLTIP` (disabled-aware) |
| `ui/src/renderer/src/components/queue/QueueCardMenu.tsx` | modify | Kebab in `TOOLTIP` with `suppressed={open}`; `title` removed |
| `ui/src/renderer/src/features/transcript/TranscriptPage.tsx` | modify | `up-btn`, `down-btn` in `TOOLTIP` (disabled-aware); `title` removed |
| `ui/src/renderer/src/features/converter/ConvertPage.tsx` | modify | `convert-staged-remove` in `TOOLTIP` |
| `ui/tests/unit/tooltip.test.tsx` | new | AC-80.1–80.7, AC-80.13 |
| `ui/tests/unit/icon-hints.test.ts` | new | AC-80.8, AC-80.9 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | TA-8, TA-11, TA-12, TA-14, TA-15 |
| `ui/tests/unit/queue-card.test.ts` | modify | TA-25 |
| `ui/tests/unit/fixtures/queue-slot-baseline.json` | modify | `FIXTURE_REPAIRS` (a) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-80.10; TA-22–TA-24 |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-80's `NEW_TESTIDS`: `CAPTURE_TOOL_ARROW_HINT`, `CAPTURE_UNDO_TIP`, `CAPTURE_UNDO_HINT`, `CONSOLE_CLOSE_HINT` |
| `ui/tests/e2e/console-chrome.test.ts` | modify | AC-80.11 |
| `ui/tests/e2e/download-queue.test.ts` | modify | TA-27 (added at H1-3, `walkthrough.md` A-9; D-37) |
| `ui/tests/e2e/convert-queue.test.ts` | modify | TA-28 (added at H1-3, `walkthrough.md` A-9; D-37) |
| `docs/execution/plans/2026-10-14-capture-chrome/tooltip-probe.mjs` | new | `ROOT_CAUSE_PROBE` (plan-local, not product) |

### MEU-81 — `gui-capture-action-row`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| Keyboard nudge (renderer) | `CapturePage` `handleEditorKey` | Arrow keys only, 1 image px, clamped by the existing `clampImagePoint` | Other keys fall through unchanged |

The saved annotation DTO, REST, MCP and IPC are unchanged.

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-81.1 | unit | `ACTION_BUTTONS` has exactly the 7 ids, icons and names of the contract; its ids are unique and disjoint from `TOOLBAR_BUTTONS`; every icon is a lucide component. | Spec 09:695; D-49; D-15 | A duplicate id or an id shared with `TOOLBAR_BUTTONS` fails |
| AC-81.2 | unit | Rendering per `ACTION_ORDER`: every mounted action is icon-only (trimmed text '', `aria-label` = its `ACTION_BUTTONS` name, one `aria-hidden` svg), sits in `{id}-tip`, has its variant class, and has no `title` on the button or on `{id}-tip`, both enabled and disabled (Apply with an unsaved overlay; Revert with no backup is unmounted). `capture-delete-tip` is the last element of the action slot, and `capture-actions-separator` (`role="separator"`, `aria-orientation="vertical"`) immediately precedes it. | Spec 09:695; D-49; AC-39.28; R1 F6 | No action button has a text node; Delete is never before the separator; no action node has a `title` |
| AC-81.3 | unit | Behaviour per icon:<br>Remove mark removes only the selected mark (the DTO loses one entry, no `DELETE /captures`);<br>Save posts `annotate` once;<br>Apply opens `capture-flatten-confirm`;<br>Revert opens `capture-revert-confirm`;<br>Open file calls `openPath` and Open folder calls `showItemInFolder` once each;<br>Delete opens `capture-delete-confirm`. | Spec 09:701 (behaviour tests for each icon action) | Remove mark with no selection is not mounted; Delete opens no request before confirm |
| AC-81.4 | unit | `RETIRED_CONTROLS` are absent for each mark type selected (arrow, box, highlight, text) and for every tool, including Color options open. Importing `features/capture/capture-sample` fails (the module is gone). The Color options row renders exactly well, hex, Apply, Cancel, Named. | Spec 09:696-697; D-49, D-51 | `queryByTestId` for each of the 8 retired ids is null in every state |
| AC-81.5 | unit | Body nudge: with a box selected and the surface focused, each arrow key moves it by `KEYBOARD_NUDGE_PX` in its direction. With an arrow selected and the surface focused, both ends move. One burst adds one history entry on keyup; Esc during a burst restores the start geometry with no history. | Spec 09:696; D-49; `NUDGE_TARGET` | A key with no selection changes nothing and adds no history |
| AC-81.6 | unit | Endpoint nudge (`NUDGE_TARGET`, `HANDLE_LAYER`): the two handles are in `capture-handle-layer`, whose parent is `capture-zoom-content` (the marks `<svg>`'s parent) and whose `viewBox` equals the marks `<svg>`'s; it is inside `capture-draw-surface` and has no `aria-hidden` ancestor; each has `tabIndex` 0, `role="button"` and its aria-label. Focusing `capture-handle-to` then `ArrowUp` (keydown dispatched on the handle, bubbling) moves only `to`; focusing `capture-handle-from` moves only `from`. A pointerdown/up on a handle with no move, then `ArrowLeft`, moves only that end. Space on a focused handle does not arm pan (`data-zoom-kind` and the cursor are unchanged). Selecting another mark, changing tool, or focus landing on the surface itself resets to body. | Spec 09:696 ("the focused endpoint"); D-49 quote; D-17; D-26 (R1 F2); D-32 (R2 F7) | After focusing the `to` handle and then the surface, `ArrowUp` moves both ends; a handle layer that is a direct child of `capture-draw-surface` fails the parent check |
| AC-81.7 | unit | During a live pointer gesture (`pressed`, `moving`, `endpointDragging`), arrow keys change no geometry and add no history. | D-17 | — (the AC is itself the negative) |
| AC-81.8 | unit | `MARKS_ROW_LAYOUT` classes: the row has `shrink-0` and not `overflow-x-auto`; `capture-mark-list` has `min-w-0`, `flex-1`, `overflow-x-auto`; the action slot has `shrink-0`. | Spec 09:698; triage D-50; D-18 | The row class list never contains `overflow-x-auto` |
| AC-81.9 | integration | Electron `NO_OVERFLOW_FIXTURE` at 1280×800: all of its assertions hold in each variant. | Spec 09:698, 09:701; triage D-50 (as AC-65.4) | The marks row never reports `scrollWidth > clientWidth`; no action tip box extends past the row's right edge |
| AC-81.10 | unit | `HEADER_STATUS` DOM: in use, `capture-hotkey-banner` is a child of `capture-header` with the Hotkey warning chip and the template text; free, it is absent. `capture-header` has `flex-nowrap`. | Spec 09:699; D-64 | Free: `queryByTestId('capture-hotkey-banner')` is null (no reserved band) |
| AC-81.11 | integration | Electron `HOTKEY_IN_USE_FIXTURE` and `HEADER_GEOMETRY`: in the in-use run, `getHotkeyStatus().inUse` is true and the banner is visible inside the header; header height and viewport top equal the free run's within ±0.5 px. | Spec 09:699, 09:701; D-64 | Free run: banner count 0 |
| AC-81.12 | unit | Help content: the four-tools body contains `HELP_EDIT_TEXT`; no Capture help body contains "Sample". | D-51; D-49 | "Sample original" is absent from every Capture help section |
| AC-81.13 | unit | Registry: the `RETIRED_TESTIDS` constants are absent from `test-ids.ts`; every `NEW_TESTIDS` constant is present in the new block after the MEU-67 block; the AC-51.6 hash equals the re-pinned value (TA-26). | E2; D-21 | A retired constant that comes back changes the hash and fails |
| AC-81.14 | integration | Electron, real input, away from Fit (D-32): on `ZOOM_SHOT` (`openZoomShot`), click `capture-zoom-in` until `capture-zoom-level` reads `100%`, then pan with a real middle-button drag of (−40, −30) px (the AC-66.14 pattern), and read the view (`readZoom`). Draw an arrow with the Arrow tool between two client points inside the surface; it stays selected. **Geometry:** for each of `capture-handle-from` and `capture-handle-to`, the centre of its `boundingBox()` equals `toClient(cx, cy)` = (`left + ox + cx × s`, `top + oy + cy × s`) within 1 px, and its width is `2 × HANDLE_RADIUS_CSS` within 1 px. **Grab:** `mouse.down` at the `to` handle's box centre, move +20 px in x, `mouse.up`: the arrow's `x2` grows by `20 / s` within 1 image px and `x1`/`y1` are unchanged. **Keys:** `keyboard.press('Tab')` repeatedly from `capture-draw-surface` until `document.activeElement` is `capture-handle-to` (at most 4 presses), then `ArrowUp` ×3: the `to` circle's `cy` decreases by 3 image px, the `from` circle's `cx`/`cy` are unchanged, the `to` handle's box centre still equals `toClient(cx, cy)` within 1 px, and `capture-draw-surface`'s `scrollLeft`/`scrollTop` stay 0 (focus did not scroll the surface). Then focus `capture-color` (Options open) and press `ArrowUp`: no circle moves and the input's value is unchanged. | D-49 quote; D-17; D-26 (R1 F2); D-32 (R2 F7) | Arrow keys in `capture-color` move no mark; a handle layer outside `capture-zoom-content` draws the `to` handle at the Fit mapping, off its arrow end by more than 1 px, and fails the geometry check |
| AC-81.15 | unit | Key ownership negatives with an arrow selected: `ArrowUp` while focus is in `capture-text-draft` (Text tool), `capture-color` (Options open), a `capture-filmstrip-item` button, or a `capture-confirm-strip` button (Delete confirm open) changes no geometry and adds no history; with focus in `capture-color`, the input's value is unchanged. | D-17; D-26 (R1 F2) | — (the AC is itself the negative) |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Icon per action | Human-approved | D-49 icon proposal (`ACTION_BUTTONS`) |
| Delete placement | Human-approved | D-49: red, far right, after a separator |
| How a keyboard user picks an endpoint | Human-approved + Local Canon | D-49 quote ("dragged or focused"); handles made focusable (D-17) |
| Keys during a pointer gesture | Local Canon | Ignored (D-17), the same as the existing Save-during-gesture refusal (AC-60.10) |
| Which part of the row scrolls | Research-backed + Local Canon | Only the chip list (D-18); NO_OVERFLOW as AC-65.4 |
| Header status placement and in-use reproduction | Human-approved + Local Canon | D-64; `HOTKEY_IN_USE_FIXTURE` (D-20) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` | modify | `ACTION_BUTTONS`, `ActionButtonId` |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` | modify | `RETIRED_CONTROLS` props and markup; `MARKS_ROW_LAYOUT`; Remove mark as an icon; `HANDLE_LAYER` (the arrow handles focusable, `onHandleFocus`, rendered inside `capture-zoom-content`); `spaceArmable` treats `[role="button"]` as a control; surface-focus reset |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` | modify | `ACTION_ORDER`; `NUDGE_TARGET` (`annotationOwnsFocus` accepts `Element`); `HEADER_STATUS`; the sampling and A-10 reason code removed |
| `ui/src/renderer/src/features/capture/capture-sample.ts` | delete | D-51 |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` | modify | `HELP_EDIT_TEXT` |
| `ui/tests/unit/capture-action-row.test.ts` | new | AC-81.1–81.8, AC-81.10, AC-81.12, AC-81.13, AC-81.15 |
| `ui/tests/unit/capture-page.behavior.test.ts` | modify | TA-1–TA-7, TA-9, TA-10, TA-13 |
| `ui/tests/unit/capture-help-content.test.ts` | modify | TA-16 |
| `ui/tests/unit/capture-sample.test.ts` | delete | TA-17 |
| `ui/tests/unit/layout-primitives.test.ts` | modify | TA-26 |
| `ui/tests/e2e/test-ids.ts` | modify | `RETIRED_TESTIDS` removed; `NEW_TESTIDS` appended (MEU-80's four hint ids are added in row 3) |
| `ui/tests/e2e/capture-inbox.test.ts` | modify | AC-81.9, AC-81.11, AC-81.14; TA-18–TA-21 |
| `tools/validate_closeout_artifacts.py` | modify | D-39, session tooling outside both MEUs' product: `parse_review` judges a rolling review by its latest round; `TABLE_ROW` no longer drops a data row whose first cell is blank; nineteen rolling-review selftest scenarios |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Hints on nav-rail items and other labelled controls | out-of-scope | — | Human-approved triage D-69; 09:682 "labelled controls such as nav-rail items are out of scope" |
| Applying a native-tooltip fix in `ui/src/main/` | out-of-scope | — | 09:684 asks to record a one-line fix and ship the primitive anyway; `PRODUCT_SCOPE` (D-14). Brought to Mat as a Decision Brief if found |
| Resize handles for box/highlight | out-of-scope | — | 09:388 "No resize handles in this MEU" (Human-approved 2026-09-20) |
| A desktop eyedropper replacement | out-of-scope | — | 09:697 "hex and Named cover colour choice" (D-51) |
| Command-palette entries or `gui-actions-index.md` rows for the icon actions | out-of-scope | — | The actions keep their existing ids and rows (`gui-actions-index.md:69-75`); 09:695 changes their look, not the action set |
| Editing the CP rows in `11-page-layout.md` (`:267-290`) | out-of-scope | — | AC-50.1/50.4 lock; a prose sentence is added instead, as Session 30 did |
| Filmstrip actions and tool lock | deferred | MEU-88, MEU-89 | Session 38 (grouping `:88-155`) |
| Text baseline and arrow geometry | deferred | MEU-82, MEU-83 | Session 36 |
| Matrix rows other than 9.13 and 9.14 | deferred | MEU-82 | The grouping follow-up writes 9.15–9.24 with their sessions (grouping D-1; `current-focus.md` Next steps 2) |

## BUILD_PLAN.md Audit

The D3 hub is `docs/BUILD_PLAN.md` + `docs/build-plan/`. Task row 10 makes these edits (`HUB_EDITS`) and validates them exactly (`validate-task.ps1 -Check hub`). Session 30 is approved, so grouping D-1's condition for gated build-plan edits is met.

1. `09-screenshot-capture.md`:
   - The Hotkey row (`:122`): the failure message shows "inline in the Capture header row (MEU-81, Human-approved triage D-64)" instead of "banner".
   - §Annotation edit until Save:
     - History (`:390`): drop "and sampling".
     - Pointer (`:391`): drop the `sampling` state.
     - Sampler (`:394`): becomes "Removed by MEU-81 (Human-approved 2026-10-03, triage D-51)".
     - Keyboard (`:395`): becomes the `NUDGE_TARGET` rule and drops "cancel sampling"; its source adds "Human-approved 2026-10-03, triage D-49; Session 34 plan D-17".
   - The historical "Sample" mentions in §Viewport toolbar icons and Options (`:617`, `:622`, `:640`) gain "(Sample removed by MEU-81)".
   - §Icon-button hints gains two rows: "Hint text and timing" (`HINT_TEXT`, `HINT_TIMING`; "Session 34 plan D-9, D-10") and "Root-cause finding" (the one-line `finding:` from §Root cause; "Session 34 plan D-14").
   - §Capture action row gains two rows: "Endpoint nudge" ("Session 34 plan D-17") and "Marks row layout" ("Session 34 plan D-18").
2. `11-page-layout.md` §Capture page layout: one prose sentence after the MEU-67 sentence (`:91`): "Since MEU-81 the per-shot and per-mark actions are icon buttons with MEU-80 hints, Delete sits red at the far right after a separator, and the hotkey status shows inline in the header instead of a reserved band; see [09 §Capture action row](09-screenshot-capture.md#capture-action-row)." The CP rows are **not** edited.
3. `build-priority-matrix.md`: after 9.12 (`:69`), append only if absent:
   - `| 9.13 | MEU-80 | \`gui-icon-button-hints\` | [09 §Icon-button hints](09-screenshot-capture.md#icon-button-hints) | MEU-65, MEU-67 |`
   - `| 9.14 | MEU-81 | \`gui-capture-action-row\` | [09 §Capture action row](09-screenshot-capture.md#capture-action-row) | MEU-80, MEU-67 |`
4. `docs/BUILD_PLAN.md`: the AUTOGEN status regions are re-rendered by `tools/meu_status.py render` (H1-2, H2-2) and checked with `render --check`.

Row 10 re-runs the doc-reading Vitest (`layout-canon`, `gui-actions-audit`, `capture-page`).

## Verification Plan

Every command is a `validate-task.ps1 -Check <name>` case, run from the worktree root through `rtk proxy`, with receipts in `C:/Temp/av-kit/`.

### 0. Plan-local verifier (planning time; re-run at the start of `GATE`)

`uv run python docs/execution/plans/2026-10-14-capture-chrome/plan_checks.py static` is stdlib-only and read-only and runs no product code (GUARDRAILS SIGN 1 carve-out). It checks:

- the task table's structure, its dependency graph, its strategies and its builder classes;
- that every `validate-task.ps1 -Check <name>` that `task.md` or this plan names is a case in the script, and every `PlanCheck` the script calls is a subcommand;
- that `GATE`'s stage order in the plan equals the `.ps1` `$stages` ids;
- that `COUNT_FLOORS`, `AUDIT_SRC`, the frozen paths, `ADMIN_PATHS`, `IDENTITY_EXCLUDE`, `BASELINE_RED`, `FIXTURE_RED`, `SETUP_SENTINEL`, `RETIRED_TESTIDS` and `NEW_TESTIDS` equal their executable copies;
- that `AC_CASES` covers exactly this plan's unit and integration ACs, with the runner each AC type implies, the files §NEW files names, and the `red-import` and `guard` sets the `AC_CASES` row names;
- that `TA_FILE` in `plan_checks.py` equals the TEST_AMENDMENTS file column and the deleting rows are exactly TA-4 and TA-17;
- that every TA row other than TA-4 and TA-17 is applied by exactly one of rows 3 and 6 (`TA_TAGS` scoping);
- that every `D-n`, `TA-n` and `AC-8x.n` named in `task.md` has a definition site, and every AC falls inside a range or is named in a task row;
- that the TEST_AMENDMENTS table is contiguous (TA-1…TA-28) and every TA is cited by a task row (TA-27 and TA-28 by H1-3, `TA_LATE`, after `walkthrough.md` A-9).

`plan_checks.py selftest` (stdlib-only, in memory) feeds synthetic inputs to the pure evaluators and must see each one refuse: a missing AC case, a skipped case, a `TypeError` Red, a failed `SETUP_SENTINEL`, a failure outside the tag with no `TA_TAGS` tag or with another row's tag, a `BASELINE_RED` look-alike with a different message, an unlisted `native/` or `docs/` change, a one-byte or wrong-hash PNG, a probe run on another head, a placeholder observation line, a handoff that names only `AC-80` instead of each `AC-80.n`, a census wildcard, and a gate whose raw report lacks an `AC_CASES` case or whose identity changed. It also proves that a well-formed input passes each evaluator.

### 1. Prerequisites and baseline (row 0)

`-Check install` (`uv sync`, `npm --prefix ui ci`, the Electron binary, `npm --prefix mcp-server ci`, `build:picker-stub` built in this worktree), then `-Check prereq`, then `-Check baseline`. `baseline` refuses a dirty tree (`plan_checks.py clean`: any git-visible change outside this plan folder and the `.agent/context/handoffs/2026-10-14-capture-chrome-` files, which hold the plan review), then writes `baseline.sha`, the full Vitest JSON and text receipt (`plan_checks.py vitest-ok`: no failure but `BASELINE_RED`, no unhandled errors), and the Electron baseline for `capture-inbox`, `console-chrome`, `convert-queue`, `download-queue` and `transcript-queue` (unexpected = flaky = skipped = 0).

### 2. Census (row 1) and root cause (row 2)

`-Check census` runs `rg` over `ui/tests` for the retired tokens and test ids, the inventory ids, `title` assertions and the accessibility relations a wrapper can disturb (`aria-describedby`, `setActivatorNodeRef`, `listeners.`), into `s34-census.txt`. `plan_checks.py census-check` then requires that every hit is covered in `walkthrough.md` §Census by a `path:line` or `path:a-b` entry (no wildcards) whose disposition is `TA-n`, `fixture (a)`, `unaffected` (with the reason) or `new-contradiction`; any `new-contradiction` refuses (S2).<br>`-Check probe` refuses unless HEAD equals `baseline.sha` and the tree is clean, builds the app, runs `tooltip-probe.mjs` and writes the `PROBE_RUN` record. The agent views the 6 PNGs and writes §Root cause. `-Check root-cause` (`plan_checks.py root-cause`) then applies the `ROOT_CAUSE_PROBE` check (AC-80.12).

### 3. Red (rows 3 and 6)

`-Check red-80` and `-Check red-81` run the targeted Vitest with the JSON reporter **and** the default reporter (text receipt), then `plan_checks.py vitest-red --meu 80|81`, which applies `CASE_EVIDENCE` in Red mode:

- every `AC_CASES` Vitest case of the MEU is collected and not skipped (or, for `red-import`, its file fails to load only on the missing `Tooltip` module and its title is in the file source);
- every `red` case fails by `ASSERTION_FAILURE`; `guard` cases pass or fail by assertion;
- each new loading file's `SETUP_SENTINEL` passes;
- every other failure carries a `TA_TAGS` tag of a TA row this task row applies, in that row's file, and fails by assertion, or is `BASELINE_RED`, or (at MEU-80's Red only) is `FIXTURE_RED` failing by assertion;
- no unhandled errors in the text receipt, no pending or todo tests.

Then, after `npm --prefix ui run build`, the Electron Red runs `-g "AC-80"` / `-g "AC-81"`, and `plan_checks.py e2e-red --meu` requires every `AC_CASES` Electron case of the MEU to be collected, not skipped, and failed by `ASSERTION_FAILURE`.

### 4. Targeted Green (after each production edit)

`-Check green-80` and `-Check green-81` run the targeted Vitest files plus the regression neighbours (`capture-page.behavior`, `capture-toolbar`, `capture-page`, `layout-primitives`, `queue-card`, `queue-card-slots`, `queue-dnd`, `transcript-page.behavior`, `convert-page.behavior`, `console-polish`, `capture-help-content`), then build and run the Electron specs with `-g "AC-80"` (green-80) or `-g "AC-8[01]"` (green-81, so MEU-80's cases re-run). `plan_checks.py vitest-ok --meu` and `e2e-ok --meu` require every `AC_CASES` case of the MEU (and of MEU-80 during MEU-81) and every applied Vitest `TA_TAGS` tag to be collected and passed (the Electron `TA_TAGS` specs are outside the `-g` filter and are checked by the targeted gates), with no skips, no failure but `BASELINE_RED`, and no unhandled errors.

### 5. Targeted gates (rows 5 and 8)

`-Check gate80` and `-Check gate81` run:

- UI typecheck, lint and full Vitest (`vitest-ok --meu`);
- the UI build;
- the whole `capture-inbox.test.ts` and `console-chrome.test.ts` under Electron (`e2e-ok --meu --tags`: the MEU's Electron `AC_CASES` and `TA_TAGS` specs all expected);
- `--repeat-each=10` on the hover, geometry and keyboard specs, one `-g` run per AC so no `|` passes through npm and cmd: `gate80` repeats AC-80.10 and AC-80.11, and `gate81` repeats those plus AC-81.9, AC-81.11 and AC-81.14, into `s34-repeat-*`; `e2e-ok --ac` requires the repeated case in each report.

### 6. Administrative state, then `GATE` (H1-2, H1-3)

H1-2 (`-Check ssot-review`) moves MEU-80/81 to `ready_for_review`, renders, and updates the grouping and `current-focus.md` **before** the gate, because those files are inside `IDENTITY_SCOPE` and tests read some of them.<br>H1-3 (`-Check gate`) runs the fresh full D6 stages listed in `GATE`; then `-Check gate-check` applies `CASE_EVIDENCE` in gate mode to the raw reports and checks the order, the exits, the supplementary `COUNT_FLOORS` and the identity. Any later change to an `IDENTITY_SCOPE` file invalidates the gate, so `GATE` is re-run after every correction that touches one.

### 7. Product-scope proof (H1-4)

`-Check scope`: `plan_checks.py scope --baseline (Get-Content baseline.sha)` proves the frozen paths (including `native/`) unchanged in commits and the working tree, and classifies every changed git-visible path against Files Modified, the plan folder and `ADMIN_PATHS` (`PRODUCT_SCOPE`). `packages/api` is untouched, so the OpenAPI step is a recorded skip: `export_openapi.py --check` still runs inside `GATE`.

### 8. Closeout (H1-5…H1-7, H2)

- `plan_checks.py handoff-cases`: each handoff names every dotted AC id of its MEU (`AC-80.1`…`AC-80.13`, `AC-81.1`…`AC-81.15`) and quotes `gate-result.json`'s `identity_after`, and refuses a `gate-result.json` that fails the D-31 binding (`check: gate` and the raw report hashes);
- `validate_closeout_artifacts.py --ac-coverage-only` for each handoff;
- `durable_evidence.py --require-full --expected-state` with the fresh `plan_checks.py identity` (A-10, D-38): each handoff's `phase: full` record has that identity as its `tested_state`;
- `-Check look-check`;
- the review state and approval checks;
- the reflection validator with `--decision-source` for the plan, both handoffs, the grouping and `known-issues.yaml`, plus `--decision-issue` for each of the five issues;
- `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped (`docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent: `gui-refs-not-shipped`). The applicable canon:

| Element | Variant / size | States | Standard | E2E |
|---|---|---|---|---|
| Tooltip hint | token surface, `text-xs`, portaled | hidden / shown (hover, focus) / flipped | UX2, G20, G32, G33 (no motion) | AC-80.10, AC-80.11 |
| Disabled-control tip wrapper | `inline-flex` span, `tabIndex` 0 | focus / hover | UX2 (disable with a hint, don't hide) | AC-80.10 |
| 12 toolbar icon buttons | existing (`primary`/`outline`/`ghost`), `sm` | enabled / disabled / pressed | G34 | AC-80.10, AC-65.4 |
| Remove mark | `ghost`, `sm`, icon | mounted with a selection | G34 | AC-81.9 |
| Save overlay | `primary`, `sm`, icon | mounted iff dirty / disabled | G34, G35 | AC-81.9 |
| Apply to image | `secondary`, `sm`, icon | enabled / disabled + hint | G34, UX2 | AC-81.9; AC-67.35 (TA-24) |
| Revert image | `secondary`, `sm`, icon | absent / enabled / disabled + hint | G34, UX2 | AC-81.9 |
| Open file, Open folder | `ghost`, `sm`, icon | enabled / disabled + hint | G34 | AC-81.9 |
| Delete shot | `destructive`, `sm`, icon, last | enabled / disabled | G34; AC-39.28 | AC-81.9 |
| Action separator | 1 px `bg-border` rule | — | G32 | AC-81.9 |
| Arrow handles | SVG circles in `capture-handle-layer` (not `aria-hidden`, inside `capture-zoom-content` so they track zoom and pan), `role="button"`, focusable, token focus ring | idle / focused / grabbed | UX2; E2 | AC-81.14 (geometry and grab at 100% after a pan; real Tab and arrow keys); AC-81.6, AC-81.15 (unit) |
| Hotkey status | `StatusChip` warning + text, inline | absent / shown | G35 | AC-81.11 |
| Non-Capture inventory (7) | existing variants | enabled / disabled + hint | UX2 | AC-80.11 (console-close); unit AC-80.9 |

G32/G33 are enforced by `source-audit` over `AUDIT_SRC`; `HINT_TITLE_RULE` by the rendered-DOM checks of AC-80.4, AC-80.8, AC-80.9 and AC-81.2, and by AC-80.7 for `Tooltip.tsx` itself. E2 is met: every new interactive state has a registered test id and an Electron assertion (the handles through AC-81.14), or a unit assertion where the state is not geometric.

## Look checklist (`CHROME_LOOK`)

Mat runs the built app (`npm --prefix ui run dev`, launched detached) at the default window and replies one line per item: `L{n}: pass` or `L{n}: fail — note`.

| Id | Check |
|---|---|
| L1 | Hover any Capture toolbar icon: a hint matching the theme appears under it in about half a second; it never covers the button. |
| L2 | With no shot, hover a disabled tool: the hint reads "Arrow — Select a shot first" (name, then reason). |
| L3 | Tab to a disabled icon: the hint appears at once; Esc hides it; the page does nothing else. |
| L4 | Open a shot with many marks: the actions are icons, Delete is red at the far right after a thin separator, and nothing scrolls sideways at the default window. |
| L5 | Select an arrow; Tab to its head handle (a visible focus ring); arrow keys move only the head. Click the surface: arrow keys move the whole arrow. |
| L6 | No Sample original anywhere; hex and Named still set the colour. |
| L7 | With ShareX (or any app) holding F2, the warning sits in the header row and nothing below moves; with F2 free, there is no empty band. |
| L8 | Console close, the queue card grip and ⋮ menu, transcript ↑/↓ and the Convert staged × each show a hint. |

`validate-task.ps1 -Check look-check` refuses unless `walkthrough.md` §CHROME_LOOK records L1–L8 `pass`, with Mat as the source and the tested commit, and `gate-result.json` passes the D-31 binding and its `identity_after` equals a fresh identity. Any `fail` is a Decision Brief before the review.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, MEU-65 or MEU-67 is not `approved`, or MEU-80/81 is not `pending` | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS`/`FIXTURE_REPAIRS` | Stop with a Decision Brief naming the test and the minimal amendment. No test edit. |
| S3 | A Red is not an assertion failure (collection or import error outside the declared `red-import` file, a failed `SETUP_SENTINEL`, or a missing or skipped `AC_CASES` case) | Fix the test setup only, then re-prove Red. |
| S4 | `HOTKEY_IN_USE_FIXTURE` cannot hold F2 (the helper prints `FAILED` or no `HELD`), or F2 is already held in the free run | Stop AC-81.11. Decision Brief (for example, Mat closes the holder, or a seam). AC-81.10 still proves the DOM rule. |
| S5 | `NO_OVERFLOW_FIXTURE` cannot pass at 1280×800 with `ACTION_ORDER` | Stop. Decision Brief (for example, a narrower filmstrip or an overflow menu). An action is never hidden silently. |
| S6 | A fix needs a change outside `PRODUCT_SCOPE` (`ui/src/main/`, `ui/src/preload/`, `packages/`, `mcp-server/`, `tools/` except `tools/validate_closeout_artifacts.py` (D-39), `native/`, or any path not in Files Modified, the plan folder or `ADMIN_PATHS`) | Stop. Decision Brief; `ROOT_CAUSE_PROBE` findings are recorded only (D-14). |
| S7 | A gate failure that is not a product defect (environment, flake) | Decision Brief, and an A-n row in `walkthrough.md` §Amendments. |
| S9 | `baseline` sees a Vitest failure other than `BASELINE_RED`, or `BASELINE_RED` fails with a different message | Stop. Decision Brief; the tolerance is never widened. |
| S8 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |

## Decision Log

Research engine for this plan: `native` (Claude Code WebSearch, 2026-10-14). Grouping §8 rows D-1 to D-7 are carried forward unchanged; this plan's ids start at D-8. The triage decisions D-48, D-49, D-50, D-51, D-64 and D-69 live in `known-issues.yaml` (each issue's `enrichment.decision_log`). They are cited by id here and are not restated in this log; the reflection carries them with stage `triage`.

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "How does a disabled icon button show its hint, given Button's disabled:pointer-events-none and that disabled buttons take no focus?"
    resolution: autonomous
    class: two-way
    chosen: "Tooltip always wraps the child in an inline-flex span (\x7Bid\x7D-tip) that owns the pointer handlers; the span is a tab stop (tabIndex 0) and the aria-describedby owner only while the child is disabled"
    source_tag: Research-backed
    precedents: ["ui/src/renderer/src/features/capture/CapturePage.tsx:1196-1218 — Session 30 A-6/A-10 already wraps Apply in capture-apply-image-tip for the same reason", "ui/src/renderer/src/components/ui/Button.tsx:34 — disabled:pointer-events-none"]
    research: { engine: native, sources: ["https://mui.com/material-ui/react-tooltip/#disabled-elements — wrap a disabled element in a span so it can receive events", "https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/ — role tooltip, aria-describedby, shown on hover or focus"] }
    reasoning: "A constant wrapper keeps the React tree stable when a control toggles disabled (no remount, no lost focus) and gives one test-id scheme. Switching to aria-disabled would break every existing toBeDisabled assertion. A wrapper only while disabled remounts the child on toggle. The cost is DOM churn around 19+ controls: FIXTURE_REPAIRS (a) and TA-13, TA-25."
  - id: D-9
    stage: planning
    question: "What does the hint say when the control is disabled?"
    resolution: autonomous
    class: two-way
    chosen: "HINT_TEXT: the name; 'name — reason' when disabled with a reason"
    source_tag: Local Canon
    precedents: ["CaptureViewport.tsx:316 — title={disabledHint ?? name} showed only the reason", "CapturePage.tsx:1146-1160 — A-10 label showed only the reason"]
    research: { engine: none, sources: [] }
    reasoning: "With text labels gone (D-49), a reason alone ('Select a shot first') no longer says what the button is. Prefixing the name keeps both. Two-way: a wording change."
  - id: D-10
    stage: planning
    question: "Hover delay, hide grace, placement and how many hints may show"
    resolution: autonomous
    class: two-way
    chosen: "HINT_DELAY_MS 400, focus immediate, HINT_GRACE_MS 120, below and centred with an 8 px viewport clamp and flip, at most one hint, no animation"
    source_tag: Research-backed
    precedents: ["CapturePage.tsx:1146-1160 — A-10 fixed, centred label with token classes", "ui/src/renderer/src/components/ui/ConfirmModal.tsx — createPortal to document.body, z-50 (G20)"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html — dismissible, hoverable, persistent", "https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/ — show on focus; Escape dismisses"] }
    reasoning: "A short hover delay avoids flicker when sweeping across a toolbar, while focus shows at once for keyboard users. The grace makes the hint hoverable (1.4.13). One hint at a time avoids stacks. G33 is met trivially by having no motion."
  - id: D-11
    stage: planning
    question: "Does Escape on a shown hint stop the page's own Escape handling?"
    resolution: autonomous
    class: two-way
    chosen: "No: Escape hides the hint and is not consumed"
    source_tag: Local Canon
    precedents: ["CapturePage.tsx:896-944 — Escape cancels draft, colour candidate and geometry; tests pin that"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/ — Escape dismisses the tooltip"] }
    reasoning: "Consuming Escape would change the Capture editor's Escape contract whenever a hint happens to be shown (for example on a focused Undo). Hiding without consuming satisfies 1.4.13 'dismissible' and keeps every existing Escape test valid."
  - id: D-12
    stage: planning
    question: "Keep the title attribute on controls that now have the rendered hint?"
    resolution: autonomous
    class: two-way
    chosen: "Remove it from every ICON_ONLY_INVENTORY control and wrapper (HINT_TITLE_RULE); labelled controls keep theirs"
    source_tag: Local Canon
    precedents: ["Session 30 A-10 — native titles do not show in this app", "ui/tests/unit/queue-card.test.ts:449 — labelled primary action keeps title (AC-44.7)"]
    research: { engine: none, sources: [] }
    reasoning: "If ROOT_CAUSE_PROBE's fix is ever applied, keeping titles would show two hints per icon. The accessible name stays on aria-label, so nothing is lost. The cost is TA-8, TA-11, TA-12, TA-14 and TA-22."
  - id: D-13
    stage: planning
    question: "Which controls are 'icon-only function buttons'?"
    resolution: autonomous
    class: two-way
    chosen: "ICON_ONLY_INVENTORY: 12 toolbar + 7 action + 7 non-Capture controls; nav rail excluded"
    source_tag: Human-approved
    precedents: ["known-issues.yaml CAPTURE-TOOLTIPS-NOT-SHOWN triage D-69 — 'only on function buttons that have images and no words'", "planning census 2026-10-14 — rg over ui/src for icon-only Buttons and raw buttons without text"]
    research: { engine: none, sources: [] }
    reasoning: "The census found seven non-Capture controls with only an icon or glyph. Mat's rule names the class, not the page, so all are in. The nav rail has words (labels) and is excluded by name."
  - id: D-14
    stage: planning
    question: "If the root-cause probe finds a one-line fix for native tooltips, is it applied in this plan?"
    resolution: autonomous
    class: two-way
    chosen: "Record it (walkthrough §Root cause, 09 row, known-issues note) and bring it to Mat as a Decision Brief; do not apply it"
    source_tag: Local Canon
    precedents: ["docs/build-plan/09-screenshot-capture.md:684 — 'a one-line environment fix is recorded if found, and the primitive still ships'"]
    research: { engine: native, sources: ["no published Electron issue matched 'title tooltip not shown' for this setup (planning search, 2026-10-14)"] }
    reasoning: "A fix would most likely live in ui/src/main (a BrowserWindow option or a Chromium switch), which PRODUCT_SCOPE freezes. Applying it would also bring back native titles on the nav rail, which D-69 left alone. Recording satisfies the spec. Mat decides separately."
  - id: D-15
    stage: planning
    question: "Where do the action icons live: in TOOLBAR_BUTTONS or a separate map?"
    resolution: autonomous
    class: two-way
    chosen: "A separate ACTION_BUTTONS map, plus ToolbarIconButton moved to its own module used by both components"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/capture-page.behavior.test.ts:1255-1265 — iterates every toolbar entry expecting it in capture-chrome-tools", "capture-toolbar.ts:30-45 — TOOLBAR_BUTTONS keyed by test id"]
    research: { engine: none, sources: [] }
    reasoning: "Adding actions to TOOLBAR_BUTTONS would break the AC-65 loop, which expects every entry in the tools row, and Save is not always mounted. A sibling map keeps AC-65 intact. CapturePage needs the button too, so it cannot stay private to CaptureViewport."
  - id: D-16
    stage: planning
    question: "Save overlay's dirty bullet and emphasis as an icon"
    resolution: autonomous
    class: two-way
    chosen: "Keep variant primary; drop the bullet (Save is mounted only while dirty, so its presence is the signal)"
    source_tag: Local Canon
    precedents: ["CapturePage.tsx:1165-1194 — mounted iff dirty, primary", "docs/build-plan/11-page-layout.md:89 — 'Save overlay appears only when dirty'"]
    research: { engine: none, sources: [] }
    reasoning: "The bullet duplicated the mount rule. Primary keeps Save the one emphasised action."
  - id: D-17
    stage: planning
    question: "How does a keyboard user choose which arrow end the arrow keys move, once Body/Tail/Head are gone?"
    resolution: autonomous
    class: two-way
    chosen: "NUDGE_TARGET: grabbing a handle or focusing it (handles become tab stops with aria-labels) targets that end; any selection or tool change resets to the body; keys are ignored during a live pointer gesture"
    source_tag: Human-approved
    precedents: ["known-issues.yaml CAPTURE-ACTION-ROW-ICONS triage D-49 — 'Arrow keys should then nudge the whole selected mark, or the endpoint being dragged or focused'", "CapturePage.tsx:852-879 — nudgeSelected already routes by target", "CapturePage.tsx:620-660 — hitTestMarks returns hit.end for handles"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/ — every interactive element is reachable by Tab"] }
    reasoning: "Mat's rule names 'dragged or focused'; the handles are the only things that can be focused per end. Ignoring keys mid-gesture avoids two writers on one geometry, the same way Save already refuses mid-gesture (AC-60.10)."
  - id: D-18
    stage: planning
    question: "What scrolls when many marks are present?"
    resolution: autonomous
    class: two-way
    chosen: "MARKS_ROW_LAYOUT: only the chip list scrolls; the row and the action slot never do"
    source_tag: Local Canon
    precedents: ["known-issues.yaml CAPTURE-MARKS-ROW-SQUEEZED triage D-50 — shrink-0 and NO_OVERFLOW as AC-65.4", "CaptureViewport.tsx:886 — the whole row is overflow-x-auto today"]
    research: { engine: none, sources: [] }
    reasoning: "The actions must stay reachable. The chip list is the only unbounded content, so it takes the scroll. AC-81.9 proves the row itself never scrolls."
  - id: D-19
    stage: planning
    question: "How does the in-use hotkey status sit in the header without shifting the layout?"
    resolution: autonomous
    class: two-way
    chosen: "HEADER_STATUS: keep the capture-hotkey-banner id as an inline child of a nowrap header row, mounted only when in use; HEADER_GEOMETRY proves no shift"
    source_tag: Human-approved
    precedents: ["known-issues.yaml CAPTURE-HOTKEY-BANNER-GAP triage D-64 (USER_EXPLICIT 2026-10-09 'All recommendations accpeted as proposed')", "ui/tests/unit/capture-page.test.ts:215-225 — AC-39.5 pins the id and sentence in source"]
    research: { engine: none, sources: [] }
    reasoning: "Keeping the id preserves AC-39.5. The header row already holds the 36 px Capture button, so a 20 px chip-and-text line fits inside its height without changing it."
  - id: D-20
    stage: planning
    question: "How does the Electron test make the hotkey 'in use' for real?"
    resolution: autonomous
    class: two-way
    chosen: "HOTKEY_IN_USE_FIXTURE: a helper process holds F2 through user32 RegisterHotKey before the app launches"
    source_tag: Research-backed
    precedents: ["ui/src/main/capture-hotkey.ts:26-39 — inUse = !globalShortcut.register(...)", "ui/tests/e2e/capture-inbox.test.ts:681 — AC-57.10 reads window.api.getHotkeyStatus()"]
    research: { engine: native, sources: ["https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey — fails when another thread holds the hotkey", "https://www.electronjs.org/docs/latest/api/global-shortcut — register returns false when the accelerator is taken by another application"] }
    reasoning: "It reproduces Mat's real case (ShareX holds F2) without touching ui/src/main. An in-app double registration would need main-process hooks outside PRODUCT_SCOPE. S4 covers a machine where F2 is already held."
  - id: D-21
    stage: planning
    question: "Retire the 8 test-id constants (which changes the AC-51.6 hash) or keep them as dead entries?"
    resolution: autonomous
    class: two-way
    chosen: "Delete them and re-pin the hash (TA-26), with plan_checks.py registry proving the prefix lost exactly those 8 lines"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/layout-primitives.test.ts:200-214 — AC-51.6 pins the pre-MEU-51 prefix", "Session 29/30 — additive ids appended after the MEU-51 marker"]
    research: { engine: none, sources: [] }
    reasoning: "Dead registry entries would claim test ids that no longer exist, which E2's registry is meant to prevent. The mechanical prefix check keeps the re-pin honest: nothing else in the prefix can move."
  - id: D-22
    stage: planning
    question: "How are the Human-approved amendments recorded in the build plan?"
    resolution: autonomous
    class: two-way
    chosen: "HUB_EDITS item 1: amend the 09 rows in place with their triage and plan sources; annotate the historical Sample mentions rather than delete them"
    source_tag: Local Canon
    precedents: ["Session 30 HUB edits — rows added with 'Session 30 plan D-n' sources"]
    research: { engine: none, sources: [] }
    reasoning: "The 09 rows are the contract later sessions read. Annotating (not deleting) the MEU-65 history keeps those rows true for their time."
  - id: D-23
    stage: planning
    question: "Write matrix rows 9.13 and 9.14 in this plan?"
    resolution: autonomous
    class: two-way
    chosen: "Yes, only these two and only if absent"
    source_tag: Local Canon
    precedents: [".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md:215 — D-1 gates matrix rows on Session 30 approval, now met", ".agent/context/meu-status.yaml:2118, :2143 — matrix_item 9.13, 9.14"]
    research: { engine: none, sources: [] }
    reasoning: "The SSOT already names 9.13/9.14; the matrix is missing them. The other residual rows stay with the grouping follow-up, so this session does not write rows for MEUs it does not ship."
  - id: D-24
    stage: planning
    question: "Gate location and identity for a local-only session"
    resolution: autonomous
    class: two-way
    chosen: "One validate-task.ps1; GATE is authoritative locally; identity is a content hash over IDENTITY_SCOPE taken before and after the gate and recomputed by gate-check (amended by D-29)"
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-09-26-p11-queue-pages/validate-task.ps1 — local single-script precedent", "docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.ps1:105-122 — D6 stage list"]
    research: { engine: none, sources: [] }
    reasoning: "No container exists for this session, so the cloud-local split adds nothing. A content hash catches uncommitted edits, which a commit SHA alone would miss."
  - id: D-25
    stage: planning
    question: "How does Tooltip set aria-describedby on a child that already has one (dnd-kit's DndDescribedBy-0 on the drag handle)?"
    resolution: autonomous
    class: one-way
    chosen: "DESCRIBEDBY_COMPOSE: the target's own tokens, then the hint id while shown; exactly the target's own value while hidden. cloneElement keeps the child's ref, props and handlers; Tooltip's listeners go on the wrapper only."
    source_tag: Research-backed
    precedents: ["ui/src/renderer/src/components/queue/QueueCard.tsx:507-520 — the handle spreads \x7B...attributes\x7D \x7B...listeners\x7D and setActivatorNodeRef", "ui/tests/unit/queue-card.test.ts:1261 — aria-describedby = DndDescribedBy-0", "ui/tests/e2e/download-queue.test.ts:1339 — AC-49.27 keyboard drag"]
    research: { engine: none, sources: ["https://www.w3.org/TR/wai-aria-1.2/#aria-describedby — an ID reference list", "https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/"] }
    reasoning: "R1 F1: replacing the attribute would drop dnd-kit's drag instructions and break TA-25's unchanged :1261 assertion. aria-describedby is a list, so appending is the conformant composition. AC-80.13 proves it in isolation and AC-80.9 on the real handle."
  - id: D-26
    stage: planning
    question: "How do the arrow handles become keyboard-reachable when they sit in an aria-hidden svg and annotationOwnsFocus only accepts HTMLElement?"
    resolution: autonomous
    class: two-way
    chosen: "HANDLE_LAYER: a second, non-aria-hidden svg inside capture-draw-surface (placed inside capture-zoom-content by D-32) holds the two focusable role=button circles; keydown bubbles to the surface's one existing handler; annotationOwnsFocus accepts Element; spaceArmable treats [role=button] as a control; focus on the surface resets NUDGE_TARGET."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CaptureViewport.tsx:1147-1180 — the aria-hidden marks svg", "ui/src/renderer/src/features/capture/CapturePage.tsx:102-118 — annotationOwnsFocus", "ui/src/renderer/src/features/capture/CaptureViewport.tsx:531-537 — spaceArmable", "ui/src/renderer/src/features/capture/CapturePage.tsx:929-936 — arrow keys already nudge the body"]
    research: { engine: none, sources: [] }
    reasoning: "R1 F2: focusable content inside aria-hidden is announced as nothing, and an SVGElement is not an HTMLElement, so the keys would have been dropped. One key owner avoids a second arrow-key path. AC-81.14 proves real Tab and arrow input in Electron; AC-81.15 proves the key-ownership negatives."
  - id: D-27
    stage: planning
    question: "What proves Red, Green and the gate case by case, now that three findings showed row-completion predicates could pass vacuously (V30 mechanism task-row-completion-predicate)?"
    resolution: autonomous
    class: one-way
    chosen: "One evidence model, CASE_EVIDENCE, applied by pure evaluators in plan_checks.py to the raw reports: the AC_CASES manifest (runner, file, class red-import / red / guard), ASSERTION_FAILURE for Red, a SETUP_SENTINEL per new loading file, TA_TAGS for amended tests, BASELINE_RED as the only tolerated failure (and FIXTURE_RED, the one consumer of FIXTURE_REPAIRS (a), at row 3's Red only), the gate's ui-tests exit taken from the vitest-ok verdict with raw_exit kept, the text receipt for unhandled errors, gate-check over the raw reports, and handoff-cases over every dotted AC id. selftest proves each evaluator refuses its negative inputs."
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-02-capture-flatten-backup/plan_checks.py — Red by test name", "Session 38 plan BASELINE_RED and the UNHANDLED pattern"]
    research: { engine: none, sources: [] }
    reasoning: "R1 F3 and the ledger's mechanism stop: counting failures or matching a tag cannot tell a missing test, a skipped test or a TypeError from a real Red. The mechanism is redesigned, not patched: every completion predicate now reads named cases, and selftest makes each refusal executable rather than asserted."
  - id: D-28
    stage: planning
    question: "What makes the root-cause probe non-vacuous?"
    resolution: autonomous
    class: two-way
    chosen: "PROBE_RUN: a run record bound to baseline.sha on a clean product tree, 6 observations (H1-H3 x 2 targets) with the cursor inside the target rect and a non-empty title, PNGs validated by signature, IHDR size and sha256, and exact walkthrough lines naming those files. Superseded in part by D-31 (producer binding and full PNG decode)."
    source_tag: Local Canon
    precedents: ["docs/build-plan/09-screenshot-capture.md:684 — root cause first"]
    research: { engine: none, sources: [] }
    reasoning: "R1 F4: three PNG paths and free-text lines could be satisfied by any file. Binding the run to the head, the target geometry and the image hashes makes a skipped or off-target probe fail."
  - id: D-29
    stage: planning
    question: "Which paths do the scope proof and the gate identity cover?"
    resolution: autonomous
    class: one-way
    chosen: "Scope classifies every changed git-visible path against Files Modified, the plan folder and ADMIN_PATHS, with native/ frozen too; the identity hashes every git-visible file except IDENTITY_EXCLUDE. H1-2 (SSOT updates) now runs before H1-3 (GATE)."
    source_tag: Local Canon
    precedents: ["ui/tests/unit/layout-canon.test.ts — reads the build plan, the grouping file and meu-status.yaml", "native/ — 18 tracked files"]
    research: { engine: none, sources: [] }
    reasoning: "R1 F5: GATED_PATHS missed native/ and every doc a test reads, so a post-gate SSOT edit could change test inputs without invalidating the gate, and an unlisted docs/ change passed scope. An allow-list over the complete surface closes both."
  - id: D-30
    stage: planning
    question: "How does this plan handle queue-canon AC-41.3, which fails on main 7861020 for a reason outside this session?"
    resolution: autonomous
    class: two-way
    chosen: "BASELINE_RED: that one case, with that one message, may fail and never must; every other failure is real. Stop condition S9 if anything else fails at baseline."
    source_tag: Local Canon
    precedents: ["Session 38 plan BASELINE_RED (the same failure)", "Session 31 commit da1d111 — the styles.css port, unmerged"]
    research: { engine: none, sources: [] }
    reasoning: "The test reads a sibling repository's live CSS, which changed. Fixing styles.css belongs to Session 31; a named single-case tolerance keeps every other check strict."
  - id: D-31
    stage: planning
    question: "How does root-cause know the PROBE_RUN record and its PNGs came from the -Check probe run (R2 F4)?"
    resolution: autonomous
    class: two-way
    chosen: "PROBE_RUN producer binding: the ps1 writes check, build_sha256, probe_sha256 and receipt_sha256, and root-cause re-hashes the build, the probe script and the receipt on disk; the probe prints a PROBE-DONE line with the 6 PNG hashes into that receipt; every observation and PNG mtime lies inside a bounded run; every PNG fully decodes at the captured window's size; row 2 closes at baseline.sha on a clean tree. The selftest positive is a complete record, and round 2's metadata-free record with header-only PNGs is a negative. The other checkers that read a record written by a separate producer are the three readers of gate-result.json (gate-check, look-check, handoff-cases); all three apply one binding, eval_gate_binding: check: gate and the sha256 of each raw report it names, re-hashed on disk."
    source_tag: Local Canon
    precedents: ["R2 F4 — eval_probe accepted evidence without the producer's build/run binding", "D-28"]
    research: { engine: none, sources: [] }
    reasoning: "R2 F4 (mechanism task-row-completion-predicate): a hand-written record with header-only PNGs passed root-cause. Binding the record to the files the producer used, its receipt and its time window means a record that -Check probe did not write refuses, and a real decode means a PNG must hold an image. A determined forger who rewrites every artefact together is out of scope; GUARDRAILS forbids it and the reviewer reads the PNGs."
  - id: D-32
    stage: planning
    question: "Where does the HANDLE_LAYER svg sit so the handles stay on the arrow at every zoom and pan (R2 F7)?"
    resolution: autonomous
    class: two-way
    chosen: "Inside capture-zoom-content, as the next sibling after the aria-hidden marks svg, with the same viewBox and preserveAspectRatio; still a descendant of capture-draw-surface, so keydown bubbles to the one handler. AC-81.6 checks the parent; AC-81.14 checks each handle's rendered centre and size and a real grab at 100% after a middle-drag pan."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/capture/CaptureViewport.tsx:632-635 — contentStyle, the zoom box", "ui/src/renderer/src/features/capture/CaptureViewport.tsx:1134 — capture-zoom-content wraps the image and the marks svg", "ui/tests/unit/capture-page.behavior.test.ts:1721-1748 — AC-66.11 ZOOM_EXAMPLE", "ui/tests/e2e/capture-inbox.test.ts AC-66.14 — zoom to 100%, middle-drag pan, toClient"]
    research: { engine: none, sources: [] }
    reasoning: "R2 F7: a later child of capture-draw-surface fills the surface, not the zoom box, so away from Fit its viewBox maps image (700,375) to surface (350,262.5) instead of (400,300), and the radius is a quarter of the intended size. Sharing the marks svg's parent gives the layer the same transform; a cy-only keyboard check could not see the misplacement, so AC-81.14 now measures rendered geometry and a real grab."
  - id: D-37
    stage: execution
    question: "GATE run 3 failed AC-49.27 and AC-52 because their keyboard-drag wait counts every document keydown listener and MEU-80's focused grip hint adds one. How is it fixed (walkthrough.md A-9, an S6 stop)?"
    resolution: human
    class: two-way
    chosen: "Option 1: TEST_AMENDMENTS TA-27 (download-queue.test.ts) and TA-28 (convert-queue.test.ts) wait for the grip hint and zero the count before Space; both files join MEU-80's Files Modified; H1-3 applies them (TA_LATE) and gate-check requires their tags"
    source_tag: Human-approved
    precedents: ["walkthrough.md A-9 — USER_EXPLICIT Mat 2026-10-15 'Option 1.'", "ui/tests/e2e/download-queue.test.ts:1260 — watchKeydownListeners counts every document keydown listener"]
    research: { engine: none, sources: [] }
    reasoning: "The wait stood for 'the keyboard sensor is listening'. A visible hint's Escape listener made it pass early, so ArrowDown raced the sensor (3 of 6 failed alone). Zeroing the count once the hint is up restores what it measures (30 of 30), and no expected value changes. Option 2, bending Tooltip.tsx around the test instrument, was not chosen."
  - id: D-38
    stage: execution
    question: "H1-5's handoff-ac called durable_evidence.py --require-full without --expected-state, which the tool refuses (exit 2). What state binds the handoffs' final full record (walkthrough.md A-10)?"
    resolution: autonomous
    class: two-way
    chosen: "Pass --expected-state from Get-Identity (plan_checks.py identity, computed fresh in the same check), and record that identity as the tested_state of each handoff's s34-gate record. GATE and gate-check rerun because validate-task.ps1 and this plan are in IDENTITY_SCOPE."
    source_tag: Local Canon
    precedents: [".agent/docs/output-evidence-policy.md:25 — final evidence adds --require-full --expected-state ACTUAL_STATE; obtain state independently", "walkthrough.md A-1 — a plan-local checker defect fixed as an S7 amendment"]
    research: { engine: none, sources: [] }
    reasoning: "The identity already binds gate-result.json, look-check and handoff-cases, so it is the project's state for this plan. Reading it fresh in handoff-ac means a handoff can only pass while the tree is the one GATE tested. No product file or expected value changes."
  - id: D-39
    stage: execution
    question: "H1-7's review-check refuses the approved round 2: tools/validate_closeout_artifacts.py parse_review reads round 1's Findings table of the rolling review, where F1 is still open and blocking, although the round 2 recheck closes it (walkthrough.md A-13). tools/ is frozen by PRODUCT_SCOPE (S6)."
    resolution: human
    class: two-way
    chosen: "Option 3: fix parse_review so a rolling review is judged by its latest round: each round runs to the next `## Recheck` heading; round 1's open blocking findings are carried through every recheck until one closes them by whole id in a Recheck result cell that is only a closure status (closed, fixed, resolved, verified, accepted, accepted_risk, withdrawn, optionally joined by / or ,), and each round's own Findings tables (level 2 to 6) add their open blocking rows. A round without its own Findings table counts as one more open blocking finding. TABLE_ROW reads a row with a blank first cell as data, not as the separator, so a finding without an id counts and can never be closed. Execution review round 3 attempt 1 (refused by the ledger) found three false approvals in the first design (F3-F5) and the author a fourth (blank id); all four were fixed test-first. PRODUCT_SCOPE excepts tools/validate_closeout_artifacts.py only; it joins MEU-81's Files Modified. validate-task.ps1:432 gains --max-review-rounds 6. GATE reruns (run 10) and execution review round 3 sees the change."
    source_tag: Human-approved
    precedents: ["walkthrough.md A-13 — USER_EXPLICIT Mat 2026-10-15 'Fix the validator'", "tools/validate_closeout_artifacts.py parse_review — open/blocking row rules reused unchanged for every round"]
    research: { engine: none, sources: [] }
    reasoning: "The canonical review keeps every round verbatim, so round 1's table never changes and a recheck's closure is invisible to a first-table reader; every rolling review would refuse. Reading the latest round, and requiring a closure status by whole id for each carried blocking finding, keeps the gate fail-closed: silence, prose, a prefix id, a new blocking row, an unreadable round or a blank id all refuse. Options 1 and 2 would have reshaped or edited the reviewer's file instead."
```

## Research References

- WAI-ARIA APG Tooltip pattern — https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/
- WCAG 2.2 Understanding SC 1.4.13 Content on Hover or Focus — https://www.w3.org/WAI/WCAG22/Understanding/content-on-hover-or-focus.html
- MUI Tooltip, disabled elements — https://mui.com/material-ui/react-tooltip/#disabled-elements
- Win32 `RegisterHotKey` — https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-registerhotkey
- Electron `globalShortcut` — https://www.electronjs.org/docs/latest/api/global-shortcut
- Session 30 plan A-6/A-10 (`2026-10-02-capture-flatten-backup/implementation-plan.md` §Amendments) — the rendered reason label this primitive generalises

## Planning receipts

Filled in at planning time (receipts in `C:/Temp/av-kit/`):

- `s34-plan-static.txt`, `s34-plan-static-r2.txt` — `plan_checks.py static` (round 1, after the R1 corrections)
- `s34-plan-selftest-r2.txt` — `plan_checks.py selftest`
- `s34-plan-lint.txt`, `s34-plan-lint-r2.txt` — `lint_task_contract.py`
- `s34-census-r1.txt` — the blast-radius census of the R1 corrections
- §4A check — the table above (`gui-refs-not-shipped`)

## Validation stage contract

Bound to PROFILE D6:

- **Static:** `plan_checks.py static`, `ui-types`, `ui-lint` and `source-audit`.
- **Targeted:** `green-80`/`green-81` and `gate80`/`gate81`.
- **Fresh full:** `GATE`, the D6 stage list in `GATE` order, recorded in `gate-result.json`.
- **Runtime:** `CHROME_LOOK` (manual, Mat).

Each stage records argv, cwd (the worktree root), exit, receipt path and counts. Input identity is `plan_checks.py identity` over `IDENTITY_SCOPE`. It is computed before and after `GATE` and again by `gate-check`. Reuse of earlier receipts is disabled: `GATE` deletes `s34-gate-*` before it runs. The final implementation review follows one fresh full `GATE` whose identity matches the reviewed tree.
