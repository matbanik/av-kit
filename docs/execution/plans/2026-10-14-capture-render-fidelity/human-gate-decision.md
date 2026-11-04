# Human gate decisions: execution (Session 36)

This file records the human decisions taken during execution. Execution itself was authorized by the user's "proceed" after the Codex round 3 plan approval. Neither entry below authorizes commit, push, merge or release.

## A-1: `TEST_AMENDMENTS` TA-7 (found by the row-1 census, D-20)

Source: `USER_EXPLICIT`, trusted user chat channel (Claude Code, VS Code extension), 2026-10-16 (AskUserQuestion), during row 1. The census found AC-65.3 (`ui/tests/unit/capture-page.behavior.test.ts:1331`) outside TA-1..TA-6. Its 7-image-px arrow at stroke 7 is shorter than the shaft back (30.52), so `SHAFT_END` renders no `<line>` and the test's `line` read throws. That is Stop condition S2, so the executor asked:

> D-20 (S2 at row 1): AC-65.3 reads stroke-width from the arrow <line>. With SHAFT_END, its 7-px arrow at stroke 7 renders a head only, so there is no <line> and the test throws. No drag on the 8×8 fixture can fix this. Approve TA-7: replace lines 1331–1332 so the test asserts the rendered head polygon's length is 35 (factor 5 × stroke 7; 15 if the stroke edit never reaches the render)?

The user chose:

> Approve TA-7 (Recommended)

The option text: "Test-only amendment, the same kind as TA-5/TA-6 (move a <line> read to an element that keeps the value). I add TA-7 to §TEST_AMENDMENTS, log it as A-1 in human-gate-decision.md, and the Codex execution reviewer checks it. Then row 1 → [x] and execution continues."

TA-7 is defined in `implementation-plan.md` §`TEST_AMENDMENTS`. The brief, precedents and research are in `walkthrough.md` §Decision — S2 (row 1).

## A-2: head outline added to MEU-83 as AC-83.9 (D-21)

Source: `USER_EXPLICIT`, same channel and question batch, 2026-10-16. The executor asked:

> D-21: the head <polygon> inherits the <g>'s stroke at the SVG default 1 px, so the preview head has an outline the bake doesn't draw (about 0.5 px larger per side). No AC covers it. Add the fix to MEU-83?

The user chose:

> Add to MEU-83 (Recommended)

The option text: "Plan amendment: set stroke="none" on the head polygon and add one Red-first AC. The <g> stroke stays because the colour tests read it. I log it as A-2, and the execution reviewer covers it."

AC-83.9 is defined in `implementation-plan.md` §MEU-83 Acceptance Criteria. `CaptureViewport.tsx` and `capture-page.behavior.test.ts` were already on MEU-83's Files Modified list; their rows now name D-21 and AC-83.9.
