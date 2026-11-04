# Local requests — 2026-10-01-capture-viewport-chrome

Requests from the cloud driver to Mat's Windows machine (`P:/av-kit`), in the shapes from `.agent/docs/cloud-local-collaboration.md` §5.1 and §7. Each request is sent as the last block of a cloud turn; this file keeps the durable copy.

No `LOCAL_REPRO` is needed before execution ([human-gate-decision.md](human-gate-decision.md) A-1).

## GATE — sent at task row H1-6 (filled in at that time)

The template is below. `<sha>`, the attempt number and the container counts are filled in when the request is sent. Counts use the runner's own vocabulary (reflection 2026-09-30 RULE-3): Playwright `expected` means passed.

```text
WINDOWS_GATE + CAPTURE_LOOK request — 2026-10-01-capture-viewport-chrome (Session 29), attempt <N>
branch:   claude/bold-edison-b91w56
commit:   <full sha>   (tree clean at exactly this sha; a leftover windows-gate-result.json is fine)
run:      pwsh -NoProfile -File docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.ps1 -Check windows-gate
from:     P:/av-kit, quiet machine (no other agent thread / Remote Control / Electron / Playwright — say so in the reply),
          ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared (the script clears them too); do not touch the
          Electron windows while ui-electron runs (S27 A-7)
preflight: script records P:/agentic-framework HEAD + P:/.agent registry hash; if either differs from
          attempt <N-1>, it stops before stage 1 — report it
expect:   every stage of validate-task.ps1 in order (canonical list: validate-task.sh windows-gate-check `order`), all exit 0;
          Vitest numTotalTests / Playwright stats.expected at or above COUNT_FLOORS (implementation-plan.md;
          copy the numbers in when sending), numFailedTests 0, unexpected 0, flaky 0 (container pre-gate saw <counts>)
return:   commit + push docs/execution/plans/2026-10-01-capture-viewport-chrome/windows-gate-result.json
          ("docs(execution): record Session 29 Windows gate (attempt N)")
on fail:  preserve ui/test-results + C:/Temp/av-kit/s29-* to C:/Temp/av-kit/keep/<sha>-attempt<N>/ FIRST;
          targeted --repeat-each into a separate dir; classify vs diff; report — do not fix without an A-decision

then CAPTURE_LOOK, on the same commit, app started as you normally run it for manual testing (say dev or packaged),
default window size (1280x800), no window zoom, one large capture in the inbox (any real screenshot ≥ 1920 px wide):
  L1 Capture page, shot selected, each tool in turn: the toolbar row and the options row show no horizontal
     scrollbar and nothing is clipped; hovering each icon shows its tooltip name.
  L2 The header control reads "Options", looks like a button (fill + icon + chevron), and opens/closes the
     inbox/hotkey panel.
  L3 One mouse-wheel notch over the image changes the zoom readout by exactly one step, and the pixel under
     the cursor stays under the cursor.
  L4 Ctrl+= / Ctrl+- / Ctrl+0 change the image zoom readout, and the rest of the window (nav rail, header text)
     does NOT grow or shrink.
  L5 At 200 %: Space+drag and middle-button drag move the image; neither creates a mark.
  L6 At 200 %: draw an arrow onto a small, recognisable detail, Save, switch to Annotated: the baked arrow
     sits on that detail.
return:   one line per item: L<n> pass|fail: <what you saw> (+ a screenshot for any fail)
```

## GATE — attempt 1, sent 2026-10-02 (row H1-6)

The tested code is `05b5b86`. The branch head named in the chat request is a descendant that changes only `.agent` state, `docs/BUILD_PLAN.md` (SSOT render) and this plan folder's notes, all outside `GATED_PATHS`, so `windows-gate-check` binds the result to the reviewed code.

```text
WINDOWS_GATE + CAPTURE_LOOK request — 2026-10-01-capture-viewport-chrome (Session 29), attempt 1
branch:   claude/hopeful-rubin-y3qkgn
commit:   <the branch head named in the chat request>   (tree clean at exactly this sha; tested code = 05b5b86 for GATED_PATHS)
run:      pwsh -NoProfile -File docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.ps1 -Check windows-gate
from:     P:/av-kit, quiet machine (no other agent thread / Remote Control / Electron / Playwright — say so in the reply),
          ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared (the script clears them too); do not touch the
          Electron windows while ui-electron runs (S27 A-7)
preflight: script records P:/agentic-framework HEAD + P:/.agent registry hash (attempt 1: recorded, nothing to compare)
expect:   every stage of validate-task.ps1 in order (canonical list: validate-task.sh windows-gate-check `order`), all exit 0;
          Vitest numTotalTests >= 702 with numFailedTests 0; Playwright stats.expected >= 118 with unexpected 0, flaky 0
          (container pre-gate saw Vitest 744 passed of 746 [AC-51.6, AC-41.3 env-bound]; Electron 120 expected +
          4 capture-picker stub specs env-bound, so 124 specs; on Windows all 124 should be expected)
return:   commit + push docs/execution/plans/2026-10-01-capture-viewport-chrome/windows-gate-result.json
          ("docs(execution): record Session 29 Windows gate (attempt 1)")
on fail:  preserve ui/test-results + C:/Temp/av-kit/s29-* to C:/Temp/av-kit/keep/<sha>-attempt1/ FIRST;
          targeted --repeat-each into a separate dir; classify vs diff; report — do not fix without an A-decision

then CAPTURE_LOOK, on the same commit, app started as you normally run it for manual testing (say dev or packaged),
default window size (1280x800), no window zoom, one large capture in the inbox (any real screenshot >= 1920 px wide):
  L1 Capture page, shot selected, each tool in turn: the toolbar row and the options row show no horizontal
     scrollbar and nothing is clipped; hovering each icon shows its tooltip name.
  L2 The header control reads "Options", looks like a button (fill + icon + chevron), and opens/closes the
     inbox/hotkey panel.
  L3 One mouse-wheel notch over the image changes the zoom readout by exactly one step, and the pixel under
     the cursor stays under the cursor (on an axis where the image is wider/taller than the frame; an axis
     that fits stays centred — A-3 TA-1).
  L4 Ctrl+= / Ctrl+- / Ctrl+0 change the image zoom readout, and the rest of the window (nav rail, header text)
     does NOT grow or shrink.
  L5 At 200 %: Space+drag and middle-button drag move the image; neither creates a mark.
  L6 At 200 %: draw an arrow onto a small, recognisable detail, Save, switch to Annotated: the baked arrow
     sits on that detail.
return:   one line per item: L<n> pass or fail: <what you saw> (+ a screenshot for any fail)
```

## GATE — attempt 2, sent 2026-10-02 (after A-4, A-5)

The tested code is `c2452aa`. The branch head named in the chat request is a docs-only descendant (this request, `task.md` and `walkthrough.md`), outside `GATED_PATHS`.

```text
WINDOWS_GATE + CAPTURE_LOOK request — 2026-10-01-capture-viewport-chrome (Session 29), attempt 2
branch:   claude/hopeful-rubin-y3qkgn
commit:   <the branch head named in the chat request>   (tree clean at exactly this sha; tested code = c2452aa for GATED_PATHS)
run:      pwsh -NoProfile -File docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.ps1 -Check windows-gate
from:     P:/av-kit, quiet machine if possible (attempt 1 ran beside two busy zorivest sessions — say what was running),
          ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared; do not touch the Electron windows while ui-electron runs
preflight: P:/agentic-framework HEAD + P:/.agent registry hash must equal attempt 1's; the script stops before stage 1 otherwise
expect:   all 17 stages exit 0; Vitest numTotalTests >= 702, numFailedTests 0; Playwright expected >= 118, unexpected 0, flaky 0
          (container: Vitest 746 of 748 [AC-51.6, AC-41.3 env-bound]; Electron 123 + 4 picker-stub specs = 127; expect 127 on Windows)
return:   commit + push windows-gate-result.json ("docs(execution): record Session 29 Windows gate (attempt 2)")
on fail:  preserve ui/test-results + C:/Temp/av-kit/s29-* to C:/Temp/av-kit/keep/<sha>-attempt2/ FIRST; report — no fix without an A-decision

then CAPTURE_LOOK L1–L6 again on the same commit (look-check binds every item to the gate's tested commit), same setup as
attempt 1. L1, L3, L4 and L6 are re-confirmations. Focus on:
  L2 Options reads as a button and opens/closes the panel, AND the Options button stays where it is when the panel opens (A-5).
  L5 At 200 %: click the Arrow tool with the mouse, then Space+drag: the image pans and no mark is created (A-4). Middle-drag pans too.
  also: at 1280x800 the image frame now fills the height below the toolbar (no large empty area) (A-5).
return:   one line per item: L<n> pass or fail: <what you saw>, plus one line on the frame height
```

## GATE — attempt 3, sent 2026-10-02 (after A-6)

The tested code is `66c7bfd`. Its only difference from `c2452aa` is TA-3 in `ui/tests/e2e/download-queue.test.ts`. The chat request names a docs-only descendant. No `CAPTURE_LOOK` this time: the attempt-2 look is reused, because `ui/src` is unchanged (D-29).

```text
WINDOWS_GATE request — 2026-10-01-capture-viewport-chrome (Session 29), attempt 3
branch:   claude/hopeful-rubin-y3qkgn
commit:   <the branch head named in the chat request>   (tree clean at exactly this sha; tested code = 66c7bfd for GATED_PATHS)
run:      pwsh -NoProfile -File docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.ps1 -Check windows-gate
from:     P:/av-kit, QUIET machine: stop zorivest-gt7's validate_codebase / pytest runs and any other busy agent session first
          (attempt 2 failed under ~96 % CPU); ELECTRON_RUN_AS_NODE and AVKIT_E2E_OUT_DIR cleared; hands off the Electron windows
preflight: agentic-framework HEAD + registry hash must equal attempts 1–2
expect:   all 17 stages exit 0 (including source-audit); Vitest total >= 702, 0 failed; Playwright expected >= 118, unexpected 0, flaky 0
          (container: Vitest 746/748 env-bound; Electron 123 + 4 picker-stub = 127, expect 127 on Windows); Electron stage near 3 min
return:   commit + push windows-gate-result.json ("docs(execution): record Session 29 Windows gate (attempt 3)"),
          plus one line: what else was running, and the ui-electron duration
on fail:  preserve ui/test-results + C:/Temp/av-kit/s29-* to C:/Temp/av-kit/keep/<sha>-attempt3/ FIRST, include the failing
          test's error-context.md step; report — no fix without an A-decision
```
