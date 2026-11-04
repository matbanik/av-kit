---
agent: gpt-5.6-sol
review_mode: implementation
review_target: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
target_plan: docs/execution/plans/2026-09-03-p10-queue-card-dnd/implementation-plan.md
round: 1
verdict: approved
findings_count: 0
dispatch_id: exec-review-p10-queue-card-dnd-r1
date: "2026-09-16"
---

# Implementation Critical Review — Round 1

MEU-49 exists to add pointer and keyboard reordering to the Downloader and Convert queue-card lists without weakening file-drop isolation, the kebab/Alt+Arrow alternatives, accessibility feedback, or queue-wide mutation serialization. The implementation achieves that intent: the final-index permutation is correct, the module-level gates cover every production reorder path and release after reconciliation, the alternative controls remain honest while held, and X4 preserves a usable keyboard geometry.

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|

No substantive High, Medium, or Low findings.

## Verification

- `npm --prefix ui run typecheck`, `npm --prefix ui run lint`, and `npm --prefix ui run build` exited 0.
- `npm --prefix ui run test` reproduced **492 passed in 57 files**. `uv run pytest -q` reproduced **509 passed** after redirecting uv and pytest temporary storage to the reviewer sandbox's writable `C:/Temp/av-kit/` root.
- The exact Electron command enumerates the expected **81 tests in 12 files**, but this reviewer host cannot execute them: an isolated Electron launch dies before the first window because its GPU subprocess repeatedly exits with Windows status `-1073741515`, followed by `GPU process isn't usable. Goodbye.` The resulting suite shape is 1 non-Electron pass and 80 `firstWindow` failures, so it is an environment non-result rather than evidence against an MEU behavior.
- As an independent runtime check against the built renderer, headless Edge drove the real dnd-kit pointer and keyboard sensors. Moving `dl-1` over `dl-3` kept the file-drop container at `data-drag-state="idle"`, rendered no file overlay, and emitted the exact final-index body `{ "job_ids": ["dl-2", "dl-3", "dl-1", "dl-4"] }`. A native file `dragenter` then changed the same container to `direct-hover` and rendered `queue-drop-overlay` without initiating a row drag.
- The keyboard probe emitted `{ "job_ids": ["dl-2", "dl-1", "dl-3", "dl-4"] }` and the position-2 announcement at viewport heights from 800px through 300px. Below 450px the outer `<main>` becomes scrollable, but the queue region remains 320px and its inner scroller remains 280px, so the ArrowDown move still commits rather than being swallowed by dnd-kit's clamp. The `min-h-[20rem]` floor, shrinkable controls pane, and `shrink-0` footer therefore behave coherently beyond the default window in the challenged direction.
- AC-49.27's three waits are observation-based synchronization: document keydown-listener registration, the ArrowDown position announcement, and restored handle focus. None is a fixed-duration sleep, and none weakens the asserted reorder outcome.

verdict: approved
