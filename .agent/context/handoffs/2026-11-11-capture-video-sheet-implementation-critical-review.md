---
date: "2026-11-11"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-11-capture-video-sheet/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s63-execution-2026-11-11-capture-video-sheet"
round: 1
---

# Critical Review: 2026-11-11-capture-video-sheet

> **Review Mode:** execution. **Verdict:** approved. **Intent achieved:** yes. No findings; no High or Critical defect found.

## Intent Anchor

Session 63 gives an agent one view of a span of a local video. `POST /captures/sheet` and `avkit_capture` `sheet` grab `grid × grid` cells at the midpoints of the span, each already scaled to the cell by FFmpeg, tile them left to right and top to bottom with Pillow, label each cell with its number and time, and write the grid as one new shot in the capture inbox. The response lists each cell's time, so the agent cites times from `cells`, never from the image, and zooms by calling again with a narrower span. The video is read in place and never changed, and nothing is uploaded.

## Scope

MEU-135's handoff, correlated implementation plan/task, actual tracked diff against `7403f1875078c81e590032f566fbeed76673e309`, three new Python test modules, plan-local scripts and the named execution receipts. The baseline plan/review artifacts were treated as context: their hashes remain unchanged except `task.md`, whose execution statuses changed. Applied IR-1–IR-7, DR claim/evidence checks and AV-1–AV-6. Claude Code/Anthropic authored the work; this reviewer is Codex and did not author it.

No repository file was edited. Reviewer scripts, generated clips/sheet, receipts and this report are under `C:/Temp/av-kit`. No suites, npm, servers, network requests, Git mutations, capture inbox or app-data operations ran. Secrets were not opened. The coordinator owns canonical report adoption, ledger recording and subsequent H2 work; this approval does not authorize a commit or push.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Review Questions

### Q1 — Goal and agent trace

Accepted. For a 7,200,000 ms 3840×2160 video, grid 5 uses 288×162 cells and a 1440×810 sheet. Its 25 midpoint times run from 144,000 to 7,056,000 ms. Narrowing around cell 11 (3,024,000 ms) recomputes the span without session state; an agent can pass its returned `timecode` (`00:50:24.000`) to `frames.at` (or convert `time_ms` to seconds). The service computes one `times` list, derives `SheetCell` and labels from it, and grabs in that order (`packages/core/src/avkit_core/services/capture.py:817`, `:822`, `:826`, `:921`). AC-135.9/.10 and the independent midpoint probe support this trace.

The PNG is registered through the existing write path with `CaptureSource.Video` (`services/capture.py:886`); ordinary image, crop and annotate operations use its shot id/path without excluding Video (`:1361`, `:1426`, `:1544`). AC-135.17 proves list/detail/image bytes and source preservation after a scan. FFmpeg has the video only as input and returns PNG through a pipe (`packages/infrastructure/src/avkit_infra/media/adapter.py:589`); real-adapter tests and the independent probe verify unchanged source hashes. No goal segment lacks implementation and behavioral evidence. No new network path exists.

### Q2 — Size, times, labels and names

Accepted. `SHEET_SIZE` uses integer half-up rounding, applies the standard/high budget at the specified 1568/1569 boundary, and decreases the long cell edge until the area fits (`packages/core/src/avkit_core/services/video_input.py:272`, `:277`). Its feasible area is monotonic, so the first fitting size is maximal under the accepted aspect construction. An independent enumeration using rational arithmetic agreed in 2,360 cases, including narrow strips, portrait shapes and all grids. AC-135.2 also pins exact expected cells and missing-size fallback.

`frame_times` caps each rounded midpoint at `end-1`, sorts and deduplicates (`:247`); 1,800 independent short-span cases agreed with exact rational midpoint calculations. D-598's fewer cells at/below the cell-count span is preserved, with remaining cells black. Labels use the same timecodes, the exact 9,999/10,000 ms boundary, half-up size/stroke rules and 8 px floor (`:303`); the adapter recomputes font and stroke after fitting. `sheet_name` floors seconds and uses `import_stem`, which replaces controls/surrogates, supplies an empty fallback and prefixes reserved stems (`:325`; `services/capture.py:229`). AC-135.3–.5 and probes assert these cases. No alternative sizing, rounding or naming rule was imposed.

### Q3 — Write, deadlines and frames regression

Accepted within D-599–D-601 A and the inherited commit-window semantics. Phase 1 reserves an exclusive `"xb"` temp; phase 2 releases the file lock for grabs/tiling; phase 3 reacquires it, rechecks a destination collision, moves, registers and commits (`services/capture.py:858`, `:1101`, `:1166`). Only owned temps are removed. Failures remove moved destinations before releasing the file lock, and the real SQLite unit of work rolls back. AC-135.11/.12 cover failed grabs, tiling/probe/replace/commit, preservation of existing data, barrier concurrency, file/row collisions and another writer's temp.

Both capture file-lock waits pass the remaining timeout (`:1049`). Probe and each grab receive time left; the adapter carries one deadline across its FFmpeg/packet-read/retry processes. Checks (a), (b), (b'), (c) and (d) prevent an expired/abandoned call starting a new commit. The return gate bounds filesystem, pool, tile and output-probe stalls (`:713`), answering at 105 s or by 111 s plus one 0.05 s join step during commit, within 120 s. A commit begun before the deadline can finish later; the accepted unknown outcome after the commit wait remains a masked 503. This is not a promise to interrupt a commit. AC-135.13 exercises all listed stages and both waits.

The diff preserves frames' worker, 100/105/6 limits, error texts, source and first/last failure times. `not_written` correctly selects the operation-specific masked message. Pre-probe `last_ms` and masking a missing FFmpeg during a grab follow the disclosed contract. Existing AC-134 guards remain, and their recorded full-gate run passed. The helper and parameter refactor introduces no identified frames regression.

### Q4 — Real FFmpeg and Pillow

Accepted. `box` inserts exactly the single `-vf scale=…:force_original_aspect_ratio=decrease:flags=lanczos` pair after `-frames:v 1`; END_GAP carries it and `None` leaves existing argv unchanged (`media/adapter.py:545`, `:571`, `:593`). AC-135.8 compares complete argv, including no-box calls. AC-135.14 compares real sheet cells' lower halves with scaled full-decode references and proves neighboring frames differ, avoiding a constant-frame false pass (`tests/integration/test_video_real_ffmpeg.py:447`). The independent probe additionally downscaled a generated 160×120 clip to 80×60: all four grabs equalled full-decode references pixel for pixel, and their tiled lower halves also matched.

`CaptureAdapter.sheet` centres cells, shrinks oversized inputs, leaves missing cells black, labels on each cell's own canvas and saves a fresh RGB canvas as metadata-free PNG (`packages/infrastructure/src/avkit_infra/capture/adapter.py:504`). AC-135.6 tests centring, no enlargement, shrinking, ordering, clipping and decode/length failures. Independent poisoned-metadata input lost its text/EXIF marker. AC-135.7's white/black contrast and no-label controls are meaningful; reviewer contrast probes also passed. Mat's D-602 A legibility judgment is accepted as given, without treating pixel contrast alone as readability proof.

### Q5 — MCP and moved pins

Accepted. Pydantic and strict Zod expose the approved fields/bounds/defaults, preserving the documented REST/MCP differences for null or negative times (`packages/api/src/avkit_api/schemas/captures.py:322`; `mcp-server/src/toolsets/capture.ts:310`). The route is declared before `/{id}`, produces the four-key 201 body, and MCP removes `action` before posting. `sheet` uses ADD_TIMEOUT_MS (`registry.ts:394`); AC-135.18 checks the actual AbortSignal timeout, request body, pre-fetch refusals, markers and zoom advice.

FRAMES_TEXT now reads probe → sheet → frames → image. Counts 73→74, 76→77 and capture 12→13, fixtures, CAPTURE_ACTIONS, ROUTE_INDEX, valid body and signature pins are additive changes, preserving previous comparisons. S9's order-pin repair composes with AC-135.19 to guard crop → frames → sheet → capture_interactive (`mcp-server/tests/audit/runner-fake-backend.test.ts:190`; `audit/coverage.test.ts:239`). It restores the intended adjacency chain without weakening the old relative order. BASELINE_PENDING and the offline audit step implement D-603; no authoritative baseline update is claimed. AC-8.12's MediaPort signature checks are unchanged.

### Q6 — Tests and Red/Green evidence

Accepted. Manually mapped every AC-135.1–.20 row to the current assertions. Independently reran red-check against both Red receipts with task.md's exact required prefixes: Python 17, MCP 2, zero problems; preserved Red exits are checked by that script. Its 43-fixture selftest also passed (13 positive, 30 negative). AC-135.1 and the disclosed passing Red cases remain guards, not claimed failing cases.

Receipt counts agree: Python Red 196 failed/290 passed, MCP Red 23 failed/137 passed; Green Python 859 and MCP 508 in 35 files. The fresh gate reports Python 1999, MCP 508 in 35 files and real FFmpeg 21, with no baseline failures excused. These are inspected recorded suite results, not reviewer suite reruns.

Grades apply to every new test function and every changed assertion in each group; no Weak test was found.

| Test files/group | IR-5 grade | Basis |
|---|---|---|
| `test_domain_capture.py` | Strong | Exact parameter order, keyword/default/annotation and port-adapter signature equality. |
| `test_video_input.py` | Strong | Exact fixed values plus exhaustive bounded/maximal size and short-span properties, boundaries and unsafe stems. |
| `test_capture_sheet_adapter.py` | Strong | Real pixels, black bars, clipping controls, malformed images, metadata and positive-controlled label contrast. |
| `test_media_adapter_frames.py` | Strong | Complete argv, END_GAP box preservation and unchanged no-box argv. |
| `test_capture_sheet_service.py` | Strong | Recording collaborators with real SQLite rollback, exact calls/values/errors, concurrency and bounded-wait/abandonment assertions. |
| `test_video_real_ffmpeg.py` | Strong | Real binaries, independent decode references, distinct-frame positive control, source hashes and raw-stream refusal. |
| `test_api_capture_sheet.py` | Strong | Real wiring/database/Pillow, exact response/envelope values, no-write refusals, log absence with positive control and rescan persistence. |
| `test_api_openapi.py`, changed `test_api_bodies.py`/`test_api_downloads.py` pins | Strong | Exact schema, route census/order, negative extra-body behavior and preserved route/action census. |
| MCP `capture.test.ts` and moved `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, fixture and runner pins | Strong | Full body/value parity, no-fetch refusals, actual timeout selection, schema discovery, description literals and composed order. |
| MCP new `audit/coverage.test.ts` cases | Adequate | Exact call/cleanup and missing-step negative control. The observer case checks its count/id/path-free text rather than separately pinning success classification; the product behavior has independent stronger coverage. |

### Q7 — Freshness, records and claim accuracy

Accepted. Independently recomputed the exact registered state:

`7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652`

ELECTRON_RUN_AS_NODE was unset. A process-only `core.excludesFile` with just `.claude/settings.local.json` restored the documented host ignore behavior before identity enumeration; that file was never opened or hashed. A process-only safe.directory setting enabled child Git access. UV initially could not open its default cache under `<HOME>`; moving UV_CACHE_DIR to reviewer scratch resolved that environmental failure. No sync or download ran.

The eight evidence.v1 records' decisive results match the named receipts, including the initially failed S9 pin and subsequent successful Green/gate. The D-504 receipts contain the stated 10.30 s and 8.78 s measurements. The 30 files in baseline line-ending anchors retain their original LF/CRLF class; all three new test modules are LF. Plan-local baseline script hashes remain unchanged; only task status/content evolved.

Pre-status copies of YAML, registry and BUILD_PLAN match HEAD; their delta is MEU-135's fields/row and the derived Total ready-for-review count. Grouping changes only row 63. Structural JSON comparison proves OpenAPI adds only the sheet route and four schemas, preserves every old path/schema and has 77 operations. 09's Delivered behavior matches the implementation. The `ready_for_review` and pending-review fields are correct at this gate.

Minor prose precision only: the dedicated 21-test real-FFmpeg receipt is `test_video_real_ffmpeg.py` alone, not the extract module too (handoff :221); the full Python gate reports 32 helper warnings, versus Green's 16 (handoff :235). The disclosed white/black look sheets are grid 3, only the portrait is grid 5. These do not misrepresent a missing behavior or failed test and are not findings.

## Checklist Results

Manual observations below were made by **codex-independent-reviewer**, with null command exit; command results carry their actual exit.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| IR-1 live runtime evidence | pass | Inspect real-adapter tests/receipts; run independent scratch FFmpeg/Pillow probe. | 0 for probe | Four downscaled grabs and tile pixels match full decode; source unchanged. |
| IR-2 collaborator behavior | pass | Inspect all new fake ports, real SQLite fixture and call/value assertions. | null | Fakes preserve values/order; persistence failures use actual rollback. |
| IR-3 error mappings | pass | Trace schema/service/global handlers and API refusal tests. | null | Fixed 422 and masked 503 bodies; no caller path/stderr in errors or logs, positive control present. |
| IR-4 prior execution findings | n/a | First execution-review round. | null | No prior execution finding. |
| IR-5 test rigor | pass | Inspect all new tests and changed assertions/pins against every AC. | null | Grades above; no Weak tests or assertion bypass found. |
| IR-6 boundary validation | pass | Inspect Pydantic/Zod, negative tests, and probe schemas. | 0 for probe | 13 independent schema refusals and defaults passed; magnitude cases in API tests. |
| IR-7 scope and AC integrity | pass | Compare all 20 plan ACs, handoff rows and tests with accepted grouping/decisions. | null | No dropped AC or disguised required deferral; Session 64 work stays there. |
| AV-1–AV-6 | pass | Read Red/Green and diff; rerun Red checkers/selftest; inspect source-backed criteria. | 0 for checkers | Every required Red family has assertion failures; no new skips, placeholders or mocked assertions. |
| DR claims, records and generated files | pass | Read-only Git diff and scratch audit script. | 0 | Status-only scope, line endings, baseline hashes and additive OpenAPI delta verified. |
| PR full evidence freshness | pass | Scratch identity wrapper with cleared Electron variable and documented ignore exclusion. | 0 | Exact tested_state reproduced; gate's before/after values agree. |
| H2 reflection/metrics/commit/prompt | n/a | User-defined post-review coordinator scope. | null | No execution-complete or commit/push authorization inferred. |

### Commands Executed and Decisive Evidence

Source observations used `rtk proxy git status/diff` and bounded numbered reads through `C:/Temp/av-kit/s63-read.py`. Completed output receipts are `s63-review-*.txt`; no live process output was filtered. The scratch PowerShell wrappers set PYTHONDONTWRITEBYTECODE=1, TMP/TEMP and UV_CACHE_DIR under `C:/Temp/av-kit/s63/exec-review-tmp`, clear ELECTRON_RUN_AS_NODE, run `uv run --no-sync python -B` and propagate the child exit. The records below embed results rather than relying only on receipt paths.

```json
{"schema_version":"evidence.v1","check_id":"s63-review-identity","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s63-review-identity.ps1","cwd":"P:/av-kit","scope":"Independent read-only execution review, MEU-135","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652","output":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652"}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-red-python","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s63-review-python.ps1 docs/execution/plans/2026-11-11-capture-video-sheet/red-check.py --require test_ac_135_2 --require test_ac_135_3 --require test_ac_135_4 --require test_ac_135_5 --require test_ac_135_6 --require test_ac_135_7 --require test_ac_135_8 --require test_ac_135_9 --require test_ac_135_10 --require test_ac_135_11 --require test_ac_135_12 --require test_ac_135_13 --require test_ac_135_14 --require test_ac_135_15 --require test_ac_135_16 --require test_ac_135_17 --require test_ac_135_20 C:/Temp/av-kit/s63-py-red-135.txt","cwd":"P:/av-kit","scope":"Independent read-only execution review, MEU-135","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652","output":"red-check: 1 receipt(s), 17 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-red-mcp","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s63-review-python.ps1 docs/execution/plans/2026-11-11-capture-video-sheet/red-check.py --require AC-135.18 --require AC-135.19 C:/Temp/av-kit/s63-mcp-red-135.txt","cwd":"P:/av-kit","scope":"Independent read-only execution review, MEU-135","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652","output":"red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-red-selftest","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s63-review-python.ps1 docs/execution/plans/2026-11-11-capture-video-sheet/red-check.py --selftest","cwd":"P:/av-kit","scope":"Independent read-only execution review, MEU-135","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652","output":"red-check selftest: 43 fixture(s) (13 positive, 30 negative), 0 wrong: []"}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-independent-probe","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s63-review-python.ps1 C:/Temp/av-kit/s63-review-probe.py","cwd":"P:/av-kit","scope":"Independent read-only execution review, MEU-135","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652","output":"size: 2360 bounded, maximal cases against enumerated Fraction oracle; times: 1800 short spans exact; Pydantic: 13 refusals and defaults pass; Pillow grid/missing cell/poisoned metadata/contrast pass; real FFmpeg/Pillow [250,750,1250,1750]: 4/4 80x60 scaled grabs equal full-decode references and tiled lower halves equal; source SHA256 unchanged; review-probe: all checks passed"}
```

```json
{"schema_version":"evidence.v1","check_id":"s63-review-evidence-audit","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s63-review-python.ps1 C:/Temp/av-kit/s63-review-audit.py","cwd":"P:/av-kit","scope":"Independent read-only execution review, MEU-135","phase":"targeted","exit_code":0,"result":"pass","tested_state":"7403f1875078c81e590032f566fbeed76673e309+a9e456a1764d8d17941964dda1f2c2590ddc0751914eaf50394e0e8d586c1652","output":"HEAD 7403f1875078c81e590032f566fbeed76673e309; baseline artifact changes: task.md only; 30 existing files retain baseline line-ending class; 3 new modules LF; pre-status copies equal HEAD and only MEU-135/derived Total changed; OpenAPI adds one path/four schemas, all existing unchanged, 77 operations; recorded full gate: Python 1999, MCP 508/35 files, real FFmpeg 21; audit: all assertions passed"}
```

## Verdict

`approved` — the work achieves the registered intent, and the inspected evidence is real and bound to the current worktree. No corrective execution round is required.

## Follow-up and Residual Risk

The coordinator may adopt this complete report and record the verdict, then continue the already-authorized H2 sequence. No commit or push is authorized here.

Accepted limits remain: duration required, duplicate millisecond cells collapse, END_GAP may show the last frame, events between cells can be missed, tiny labels may clip, stored aspect/rotation assumptions hold, an abandoned worker finishes its current wait before cleanup, and a commit beyond the final wait has an uncertain outcome. Export/eval remain Session 64 and the documented known issues/audit-baseline pending state remain unchanged. No new unresolved behavioral concern was identified.

