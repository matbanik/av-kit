---
date: "2026-11-11"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-11-capture-video-sheet/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s63-plan-canonical-2026-11-11-capture-video-sheet"
round: 1
---

# Critical Review: 2026-11-11-capture-video-sheet

> **Review Mode:** plan. **Verdict:** approved. **Intent achieved:** yes, as a plan for execution after the stated human gate.

## Intent Anchor

Session 63 gives an agent one view of a span of a local video. `POST /captures/sheet` and `avkit_capture` `sheet` grab `grid × grid` cells at the midpoints of the span, each already scaled to the cell by FFmpeg, tile them left to right and top to bottom with Pillow, label each cell with its number and time, and write the grid as one new shot in the capture inbox. The response lists each cell's time, so the agent cites times from `cells`, never from the image, and zooms by calling again with a narrower span. The video is read in place and never changed, and nothing is uploaded.

## Scope

Reviewed the working-tree implementation plan, task, all five plan-local scripts, cited core/infrastructure/API/MCP entrypoints and guards, 09's sheet and delivered frames contracts, design §6.4/§6.6/§11, grouping and MEU-135 by id. Observed `main`, HEAD `7403f1875078c81e590032f566fbeed76673e309`; all 23 task rows are unchecked and the isolated shape check confirms sheet production names are absent.

Claude Code/Anthropic wrote the plan. Codex is the independent reviewer and did not author it. Applied PR-1–PR-9 and the Materiality Gate. Accepted the supplied prior approvals, decisions and exclusions. D-601 and D-602 remain Mat's decisions; this review chooses neither.

No repository file was edited. Reviewer artifacts are under `C:/Temp/av-kit`. No product suite, baseline/session gate, look.py, backend, MCP server or network request was run. The large D-504 video was not read or regenerated. All new video inputs were generated from lavfi under `C:/Temp/av-kit/s63/review`. Secret/configuration exclusions and the parallel session's proposal were not opened.

## Findings

No High or Critical finding, missing required deliverable, impossible implementation sequence or demonstrated material false-pass was established.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

Two nonblocking wording notes are recorded under Q5 and Q9. Neither requires a new implementation mechanism or another review round.

## Q1 — Goal and one call

Accepted. `SHEET_MCP` → `ACTION_INDEX` → `SHEET_ROUTE` → `SHEET_CHECKS` → probe → `SHEET_TIMES`/`SHEET_SIZE` → reservation → boxed `CELL_GRAB`/`END_GAP` → `SHEET_TILE`/`SHEET_LABEL` → probe/publish/register → 201 is a complete production chain (plan:116–128; AC-135.1–.20). For a 1920×1080, exactly 7,200,000 ms video at grid 3, the cell is 482×271, sheet 1446×813, spacing 800,000 ms and requested times 400,000 through 6,800,000 ms in 800,000 ms steps. The shot can be listed, fetched and viewed through `image` (AC-135.17). A second call with narrower start/end uses those explicit response times and creates another uniquely named shot; it needs no saved session state.

Every substantive rule in 09:1162–1170 has a row and AC. “Read in place and never changed” has direct source-hash evidence planned in AC-135.14, as well as the input-only FFmpeg argv and exclusive new-output ownership. The strict local-path check refuses URLs. No upload mechanism is introduced.

## Q2 — SHEET_SIZE

Accepted. With validated positive grid/max_edge and fallback source dimensions, `long` starts at least 12; `short` is at least 1 and no greater than `long`. Both are monotone as `long` decreases. At `long=1`, area is at most 25 pixels, far below either budget, so the loop terminates inside both bounds. The next-long-edge check proves maximality for this rounded-aspect construction, not maximal area over arbitrary aspect-distorting rectangles. `half_up(n,d)=(2n+d)//(2d)` is correct for its nonnegative inputs.

Independently checked every edge 64–2576, grids 2–5 and 12 ordinary/extreme/fallback shapes: **120,624 cases passed**, including 1×N, N×1, square, None, zero and negative source dimensions. The supplied 480-case probe and AC-135.2 agree on exact common-aspect cells and the 1568/1569 tier boundary. This establishes the construction's bounds; it does not claim the unimplemented function has passed tests.

## Q3 — SHEET_TIMES

Accepted. The plan calls the existing `frame_times(start,end,grid²)` directly. The four spacing examples are correct: 14/4→4, 13/4→3, 2/4→1 and 1/4→0. Independent evaluation of the production function over all 480 specified small-span combinations confirmed the sorted/distinct/in-range and count predicates, including `grid²−1` cells when span equals cell count.

One ordered result-cell list drives both response cells and label arguments (AC-135.10). Numbering the distinct times consecutively and leaving unfilled canvas positions black is consistent with D-598 and `SHEET_TILE`; no invented duplicate labels or drawn positions are needed.

## Q4 — Labels and tiling

Accepted. The fitting loop decreases an integer font size to the fixed floor 8, recalculates padding while fitting and stroke at the final size, and draws onto a separate cell canvas. That clips ink to its cell even when the floor cannot fit the text. The 9,999/10,000 ms label boundary and rounding examples are correct. The adapter contract explicitly rejects unequal label/cell lengths and counts over `grid²`, shrinks oversized inputs, never enlarges, centres and emits a fresh metadata-free RGB PNG.

AC-135.6 asserts placement, black bars, shrinkage, unused cells and neighbour isolation. AC-135.7's positive pixel thresholds, empty-label negative control and recording text wrapper cannot pass for an omitted drawing operation. Normal production bytes have already been scaled by FFmpeg; the canvas budget is at most 3,588,000 pixels. Pillow's configured decompression limit remains enabled and was independently observed as 89,478,485. D-602 correctly distinguishes contrast from human readability and discloses the small-cell clipping limitation. Its A/B/C options remain a human choice.

## Q5 — CELL_GRAB

Accepted, with a wording qualification. The filter belongs between `-frames:v 1` and PNG output; the same box must be passed through the single END_GAP retry. `None` omits the filter and preserves the existing argv, protected by AC-134.9 and AC-135.8.

Generated six square-pixel/no-rotation clips and checked 24 boxed grabs with the pinned FFmpeg. A 1919×1079 source with a 289×162 box returned 288×162; centring handles this. For the extreme 4000×2 strip, a 313×1 box returned **313×2**; Pillow's specified thumbnail fallback produced 156×1 and fit safely. The transposed case behaved likewise. All 24 thumbnail results had positive dimensions inside their boxes.

**Nonblocking note:** plan:100 describes the filter as fitting inside the box; it should acknowledge FFmpeg's degenerate-dimension rounding rather than promise that every raw output edge is bounded by that box. The already-planned oversize branch at plan:120 handles it without overflow, extra writes or a broken final size budget. No delivery-level failure was established.

## Q6 — Checks and REST/MCP boundaries

Accepted. The service checks path, parsed times, strict integer bounds, probe/video/duration and span bounds before reserving or grabbing. Past-start, past-end and reversed/equal span messages use parsed milliseconds through TIMECODE; end equal to duration is accepted. Errors are raised after exception handling to avoid leaking the underlying context.

Pydantic StrictInt and Zod integer-number constraints reject booleans/fractions, null grid/max_edge, out-of-range values and extra keys as specified. REST's nullable optional start and service-level negative-time refusal differ from MCP's pre-fetch filters as disclosed; neither admits an unsafe grab or write. `/sheet` precedes `/{id}`. AC-135.9/.15/.16/.18/.20 cover these boundaries, and D-601 B explicitly substitutes the lower cap and its first-invalid value.

## Q7 — Write ownership and frames refactor

Accepted. Reservation uses `xb` under the shared file lock, and `_import_dest` counts other writers' temp names as taken (capture.py:1008–1030). Releasing the lock during grabs does not release that name reservation. Publication rechecks files/rows under the lock, moves only owned temps, registers one Video shot and rolls back/removes owned destinations on failure. Closing before replace preserves Windows semantics. The mask for tile/probe/replace/database errors and time-specific grab refusal are appropriate.

Moving the worker loop and parametrizing names/failure times/source preserves a clear route for frames' old behavior. Existing AC-134.6–.8 guards cover cleanup, collisions, remaining budgets and abandonment; argv/signature guards cover the boxed-grab extension. AC-135.12's barrier is reached after each call has reserved its own temp and released the file lock, so it can actually rendezvous both calls. No lock/barrier deadlock or overwrite path was established.

## Q8 — Deadlines and D-601

Accepted. The inventory covers the material blocking classes: filesystem work, connection checkout, ffprobe/FFmpeg, both file-lock waits, Pillow/write/probe and commit. Worker operations without individual cancellation are covered by the caller's return gate; they are not falsely described as individually interruptible. Checks (a), (b), (b'), (c), (d) prevent expired work from publishing/committing, while (e) bounds the caller. AC-135.13 includes tiling, both lock waits, replace-to-commit expiry and a genuinely blocked body; frames' unchanged return-gate guards remain required.

D-601 A gives 100/105/6 and at most 111 seconds plus a join step against 120 seconds. B/C give 20/23/6 and at most 29 seconds plus a join step against 30 seconds. Only A adds sheet to ADD_TIMEOUT_MS. The receipt really reports 10.23 s grabs + 0.063 s tile/save = 10.30 s, with the separate pre-keyframe-position run at 8.78 s. These are measurements on that fixture, not a worst-case performance guarantee. The brief preserves that distinction and offers coherent alternatives without this review choosing one.

## Q9 — MCP description and audit

Accepted. SHEET_TEXT supplies its own four M7 markers, covers response times/zoom/statelessness/missed events, and stays compatible with the marker readers. D-605 correctly moves only the frames workflow pin and retains crop→frames adjacency. D-603 adds sheet to BASELINE_PENDING and an offline shared-clip audit step; it never authorizes `--update-baseline` or a live audit. AC-135.18/.19 exercise the conditional timeout and action/response/audit wiring.

**Nonblocking note:** plan:126's “each is the first frame at or after its time” should carry frames' existing last-frame exception (`capture.ts:64`), because the deliberately reused END_GAP can return an earlier final video frame. Copying that existing exception makes the description precise; no change to END_GAP, cells or the goal is requested.

## Q10 — Pins

Accepted. Independent targeted sweeps of tests/, mcp-server/tests/ and ui/tests/ found the enumerated 76→77 route/operation counts, 73→74 action counts, 12→13 capture counts, route/body fixtures, frame signature pin and ordering constraints. No additional moving count or signature-equality pin was established. The fixed historical prefix arrays remain prefixes; their presence does not require appending sheet. Tests that enumerate current ACTION_INDEX rows receive the new fixture data.

The literal-word `sheet` sweep returned no matches (rg exit 1, not a tool failure), confirming the absence-pin claim. The built-server action-count test is named and row 2b builds first. CI already deselects the real-video module at ci.yml:66.

## Q11 — Values and console

Accepted. The explicit value flow permits video/shot paths only in successful response path fields and the owned shot record. Names pass through the existing import sanitizer; errors use fixed text or TIMECODE, and FFmpeg stderr is discarded/masked. The new `capture.sheet` event contains count and shot id only. Existing mapped 503 handling masks the body without logging the domain exception (api/errors.py:131–149).

AC-135.16 builds HealthService before testing the log ring and includes the positive marker control; it checks error bodies, logs, stdout and stderr. This is an asserted absence with a working detector, not an unobserved claim.

## Q12 — Red, identity, scope and safety

Accepted. Row 1 provides the symbols required by Python behavior Reds; route/schema additions intentionally wait for Green, and API Reds assert the response status before reading it. The instructions prohibit importing new MCP names before existence assertions. DECLARED_NEW also lists later API names, but required blocks cannot use missing-name failures to pass Red. Row 2a requires .2–.17 and .20; row 2b requires .18/.19; .1 is a passing characterization. The independent Red selftest passed all 43 fixtures, including its 30 negative cases.

The identity selftest passed. Inspection confirms the gate scripts, look.py, code/tests/config, register/render/grouping/spec inputs, runtime/font and ignored pinned FFmpeg pair are bound; post-gate closeout prose is excluded. Files Modified and project paths are covered by the scope set/prefixes. CRLF/LF preservation and LF new files are explicit, including the OpenAPI CRLF check.

Executed only extracted read-only baseline predicates: the actual pending decisions were refused; scratch A/B/C ruling fixtures were accepted; current queue and shape checks passed; Pillow/font check observed 13.0.0 and a loadable Segoe UI font. These format checks are not evidence of human authorization. look.py's fixed output tree is `C:/Temp/av-kit/s63/look`, it constructs no service/inbox, and all clips come from lavfi. Real tests extend the existing temp fixture and stay CI-deselected. No planned session-specific probe requires external video, a network request or a non-fixture inbox.

## Checklist Results

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| PR-1, PR-3, PR-4 | pass | Manual plan/task/script trace by codex-independent-reviewer | null | Coherent type-only → Red → Green → guards/full gate sequence; every delivery surface and check is scheduled. |
| PR-2 | pass | Manual task-state read plus isolated shape probe | null | 23 unchecked task rows; new sheet production names absent. |
| PR-5, PR-7, PR-9 | pass | Manual comparison with 09/design/grouping and named contracts | null | Source-backed rules; MEU-136 exists and is deferred; supplied exclusions honored; no materially ambiguous competing contract found. |
| PR-6 | pass | Manual correction/handoff-route inspection | null | Named rolling report and corrections route; round-2 census is not applicable in round 1. |
| PR-8 | pass | Manual entrypoint-to-observable and negative-oracle trace | null | Pixel controls, refusal grab/write counts, owned-file cleanup and deadline schedules have explicit producers/assertions. |
| DR claim/source integrity | pass | Manual current-source and receipt comparison | null | Plan is presented as unimplemented; probe results match their receipts, subject to the two nonblocking wording notes. |
| Runtime product verification | n/a | Not run in read-only plan review | null | No pytest/Vitest, session gate, baseline script, look script or server execution. |

```json
{"schema_version":"evidence.v1","check_id":"s63-review-size-and-ffmpeg","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s63/review/check_cells.py","cwd":"P:/av-kit","scope":"Plan arithmetic and generated scratch clips only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review working tree at 7403f1875078c81e590032f566fbeed76673e309; pinned FFmpeg; Pillow 13.0.0","output":"SHEET_SIZE exhaustive edges: 120624 passed. 24 generated-clip grabs checked. 1919x1079 box 289x162 returned 288x162. 4000x2 box 313x1 returned 313x2; planned thumbnail produced 156x1. All 24 thumbnail outputs were positive and inside their cell boxes.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-controls-and-times","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s63/review/check_plan_controls.py","cwd":"P:/av-kit","scope":"Extracted read-only baseline predicates, scratch ruling fixtures and production FRAME_TIMES function","phase":"targeted","exit_code":0,"result":"pass","tested_state":"unimplemented Session 63 plan; HEAD 7403f1875078c81e590032f566fbeed76673e309","output":"Actual D-601/D-602 pending entries refused (predicate exit 1); scratch A/B/C entries accepted. Queue: MEU-134 approved, MEU-135 pending; 7403f18 ancestor true. Shapes wrong: []. Pillow 13.0.0 MAX_IMAGE_PIXELS 89478485 segoeui.ttf loads True. FRAME_TIMES exhaustive small spans: 480 passed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-red-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-11-capture-video-sheet/red-check.py --selftest","cwd":"P:/av-kit","scope":"Scratch receipt fixtures only; PYTHONDONTWRITEBYTECODE=1 and TMP/TEMP under C:/Temp/av-kit/s63/review","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working-tree red-check.py","output":"red-check selftest: 43 fixture(s) (13 positive, 30 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-11-capture-video-sheet/identity.py --selftest","cwd":"P:/av-kit","scope":"Scratch git fixture only; PYTHONDONTWRITEBYTECODE=1 and TMP/TEMP under C:/Temp/av-kit/s63/review","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working-tree identity.py","output":"Bound mutations changed state and refused historical evidence, including look.py and runtime FFmpeg/ffprobe keys; excluded project-artifact edits retained state. identity selftest: 0 failure(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-sheet-absence","command":"rtk proxy rg -n '\\bsheet\\b' tests/ mcp-server/tests/ ui/tests/","cwd":"P:/av-kit","scope":"Existing tests only","phase":"targeted","exit_code":1,"result":"pass","tested_state":"working-tree test sources at review time","output":"No matches; rg exit 1 is the expected absence result. Targeted ACTION_INDEX/ROUTE_INDEX/CAPTURE_ACTIONS/count/signature sweep established no additional moving pin.","fresh":true}
```

The first exploratory clip generator used FFV1, which refused a one-pixel source before any grab; that receipt is not a successful probe. The final generator used PNG-in-NUT and completed all six source shapes. No failure was attributed to product code from the initial fixture error.

## Verdict

`approved` — executing the plan as specified would deliver the registered goal. No blocking finding was established. The two wording clarifications above can be carried forward without reopening accepted frames behavior or changing scope.

D-601 and D-602 remain pending for Mat at the stated gate; approval of this plan does not supply those rulings or execution authorization. Actual implementation tests, source hashes, rendered-label judgment under the chosen option and the fresh execution gate remain future evidence. This is approval of an unstarted plan, not certification that the product implementation has passed.

Report written to `C:/Temp/av-kit/s63-plan-review-round-1.md`; the coordinator owns canonical copying and ledger collection.
