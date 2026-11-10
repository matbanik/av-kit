---
date: "2026-11-09"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s59-plan-canonical-2026-11-08-capture-crop-copy"
round: 3
---

# Critical Review: 2026-11-08-capture-crop-copy

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.

## Intent Anchor

Session 59 lets an agent cut a region of any capture into a new shot. `POST /captures/{id}/crop` and MCP `crop` take `x`, `y`, `width` and `height` in original pixels, or in fractions with `unit: "fraction"`, and an optional `name`. The box goes through Session 58's `resolve_region`, so a crop and a region view of the same box cut the same pixels (grouping D-401). The original's pixels are saved exactly, with no resampling, as a PNG in the inbox root with metadata stripped and the ICC profile kept. The new shot has source `Crop`. The source's saved marks are carried over, moved by the crop's origin and clipped to it, and the crop gets its own sidecar and bake. The response is 201 with the new shot, the source id, the requested and applied boxes, whether the box was clamped, and how many marks were kept, clipped and dropped. The source's file, sidecar, bake and row are never changed, so no `confirm` is asked.

## Scope

Reviewed the working-tree plan, task, D-499 brief, five plan-local scripts, cited design/grouping/spec, Session 58's approved plan, relevant production paths and test guards. HEAD reads `8bcb4a68e796f5b340b20eae41b7ad8c71e1fab9`. All 25 task rows remain unstarted. Claude/Anthropic authored the plan; this review is independent Codex review.

Accepted the user's givens, Session 58's decisions, queue order, GUI deferral and the open status of D-499. Session 57 was outside scope; only its cited `audit-rule.py` was read. No repository files, secrets, product suites, plan execution scripts, app or network were accessed for execution. Reviewer writes are confined to `C:/Temp/av-kit`; Python bytecode was disabled. External research quotations were not independently fetched in this offline review.

## Findings

All findings have High confidence. F1 is the sole approval blocker. No Critical finding. All are behavior findings about the deliverable; none is a control-defeat or review-scaffolding finding. Plan-relative references below resolve under `docs/execution/plans/2026-11-08-capture-crop-copy/`.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `MARK_CLIP_BOX` drops a visible, valid zero-width rect when its origin is outside the crop. A saved rect `(x=20,y=0,width=0,height=40,stroke_width=1)` on an 80×80 source crosses crop `(10,10,30,30)`. Pillow draws 30 red pixels in that crop, but the special zero-dimension rule sees translated origin `(10,-10)` and drops the mark. The new bake loses the line and reports it dropped despite a nonempty inclusive intersection. This violates the goal and saved-mark intersection contract (09:1030, family AC-130); AC-130.2 currently codifies the wrong exception, while AC-130.5 cannot detect a dropped mark. | `implementation-plan.md:122`; `implementation-plan.md:153`; `implementation-plan.md:164`; `packages/core/src/avkit_core/domain/capture.py:166`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:471` | Handle zero-width/height rects through their inclusive intersection rather than the empty-area origin shortcut. Amend D-486/AC-130.2 and add vertical/horizontal crossing-rect regressions, their counts and resulting bake. | fixed |
| F2 | Medium | no | behavior | AC-130.19 applies the pixelate no-unchanged-pixel oracle to the eraser on a black-and-white checkerboard. `eraser_fill` selects a ring colour, hence black or white; a 12×12 covered checkerboard retains 72 identical pixels. Correct erasing cannot satisfy this Green expectation. | `implementation-plan.md:295`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:191`; `packages/infrastructure/src/avkit_infra/capture/adapter.py:203` | Keep the checkerboard oracle for pixelate. For eraser, assert the expected uniform ring fill, or use a distinct-colour ring fixture if every covered pixel must change. Amend the expectation before Red. | fixed |
| F3 | Medium | no | behavior | AC-130.13's claimed unresampled view oracle is not general. An applied 8 px maximum edge requires forbidden `max_edge=8`; using 64 gives scale 4. A 3000 px edge requires forbidden 3000; using 2576 downsamples. Requested dimensions also differ from applied dimensions after clamping, and fractional request values are not pixel max_edge values. | `implementation-plan.md:100`; `implementation-plan.md:289`; `task.md:84`; `docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:121`; `docs/execution/plans/2026-11-08-capture-region-import/implementation-plan.md:196` | Assert identical applied rectangles for every supported input. Limit decoded PNG view equality to scale-1 cases using the applied pixel dimensions in 64–2576; use direct source-pixel comparisons for smaller/larger/clamped/fraction cases. Preserve Session 58's view contract. | fixed |
| F4 | Medium | no | behavior | `CROP_NAME` leaves the default source stem unbounded. A legal 240-character stem has a 244-character source name and a 249-character crop name, but the temporary and annotated names are 259 characters. On this Windows host the source was created successfully and the planned temporary PNG write raised `OSError` (errno 22). A valid shot therefore cannot be cropped without supplying a shorter name. | `implementation-plan.md:119`; `implementation-plan.md:126`; `implementation-plan.md:231` | Define a length-safe default stem with headroom for the longest derived suffix and collision counter; test a long scanned inbox filename. | fixed |
| F5 | Medium | no | behavior | AC-130.3's unchanged signs of both `dx` and `dy` contradict its required bottom-sliver case. Liang–Barsky gives `(0,49.846...)→(1.818...,50)`; half-up rounding gives `(0,50)→(2,50)`. The original positive `dy` becomes zero. The specified algorithm cannot pass that exact sign assertion. | `implementation-plan.md:123`; `implementation-plan.md:166`; `implementation-plan.md:279`; `C:/Temp/av-kit/s59-plan-probes.txt:71` | Test non-reversal and the stated endpoint rounding error, allowing a component to round to zero. Retain the reject-zero-length rule for clipped results. | fixed |
| F6 | Medium | no | behavior | AC-130.22 requires a `capture.registered` ring line with source `Crop`, but HealthService keeps only `CONSOLE_FIELDS`; `source` and `shot_id` are absent. The actual processor turns that event into exactly `capture.registered` and clears the original fields. Correct crop logging cannot satisfy this positive control. | `implementation-plan.md:298`; `task.md:84`; `packages/core/src/avkit_core/services/health.py:47`; `packages/core/src/avkit_core/services/health.py:207`; `packages/core/src/avkit_core/services/health.py:234` | Assert newly appended registration events in a bounded ring slice and independently assert the returned shot's `Crop` source. Keep the stdout engine control and marker checks; do not widen Console fields to satisfy the test. | fixed |

## Q1 — Goal and two calls

**MCP fraction crop:** on 3840×2160, `{action:"crop",id,x:0.25,y:0.25,width:0.5,height:0.5,unit:"fraction",name:"detail"}` passes the strict union. The new ACTION_INDEX row selects POST; `QUERY_GET_ONLY` suppresses query construction, `httpBody` drops action/id and retains all crop fields, and the crop timeout uses `ADD_TIMEOUT_MS`. The route calls `crop_shot`; the shared resolver yields `(960,540,1920,1080,false)`. Rect/arrow/text marks pass through `clip_mark`; the adapter cuts original pixels, then the service writes the new row, sidecar and configured bake and returns 201 with the requested/applied boxes and counts. This normal chain is sound; F1 identifies a saved-mark case it mishandles.

**REST clamped JPEG:** on a 200×100 stored JPEG, `{x:180,y:10,width:40,height:30}` resolves to `(180,10,20,30,true)`. The adapter verifies stored dimensions, decodes, crops without padding and writes a PNG. The independent JPEG probe retained the ICC bytes, dropped EXIF and preserved the decoded crop pixels. The plan writes only the new destinations and a new row; no source mutation was found in either normal chain or the specified rollback paths. Passing the current AC set would nevertheless miss F1's lost mark.

## Q2 — Resolution and D-401

Accepted direct reuse of `resolve_region`, including Session 58's integer-before-sum px handling, outward fraction rounding, nine-place guard, right/bottom clamp and post-clamp eight-pixel minimum. This gives the same applied rectangle as the region view. F3 qualifies the stronger claim about the view's returned pixels; changing the view's bounds or restricting crop to those bounds is unnecessary.

## Q3 — Pixels, modes and metadata

Accepted the mode rule against installed Pillow 13.0.0: `1`, `L`, `LA`, `P` plus transparency, `RGB`, `RGBA` and `I;16` round-trip; `I`, `F`, `CMYK` and `YCbCr` require conversion for this PNG writer. The fallback intentionally changes those unsupported modes' representation; it performs no geometric resampling. A normal JPEG decodes to RGB. The independent PNG and JPEG probes retained ICC and removed EXIF; the PNG probe also removed Comment and XMP text. This Pillow version's PNG writer only emits EXIF explicitly supplied in encoder arguments (`PngImagePlugin.py:1546`), so inherited `info['exif']` did not leak. Resolving against the row and checking actual file dimensions before cropping prevents padding.

## Q4 — Windows names and concurrency

Accepted sanitization/empty/length refusals, reserved-device prefixing (including a reserved basename before an extension), case-folded collisions, checking image/sidecar/bake/temp roles and stale rows, and allocating names within the shared lock. Two concurrent crops therefore cannot allocate the same name. F4 covers the unbounded default name. A small clerical inconsistency remains: the case-folded rule predicts `crop_con.png`, while AC-130.15 spells `crop_CON.png`; select the canonical spelling before Red.

## Q5 — Mark geometry and bake differences

No counterexample was found to AC-130.5's clamp fixed-point property: returned box/text origins lie inside the clamp bounds and arrow ends use its closed rectangle. That invariant does not detect F1 because the mark is dropped. Ordinary rects correctly use their inclusive right/bottom outline; zero-dimension rects still have visible geometry and need the separate correction.

Liang–Barsky preserves endpoint ordering before rounding, and rejecting coincident rounded endpoints prevents a zero-length result being called clipped. F5 corrects the stronger sign oracle. Exhaustive returning `match` cases followed by `assert_never(mark)` will expose a future union member to pyright.

D-486's rect-edge strokes, pixelate grid/partial-block changes, eraser sampling, new arrowhead and outside-anchor text differences follow the adapter. The list is not a universal pixel-equivalence theorem: thin rects with stroke wider than their box can paint beyond nominal bounds (the probe's width 1/stroke 5 rect spans x=17..24 for nominal x=20..21), and rounded/antialiased arrows can differ locally. F2 separately corrects the eraser redaction oracle.

## Q6 — Lock, rollback and scan

Accepted one lock hold, an inner UoW inside the cleanup try, and no call to locked `annotate_and_save`/scan. `probe`, `ensure_dir`, `bake`, `_upsert_shot` and the geometry/wire helpers do not acquire CAPTURE_FILE_LOCK. Closing the UoW after a failed commit rolls back its uncommitted session. The planned cleanup encloses replace, probe, sidecar, bake and commit; pre-write errors retain their fixed 4xx messages. No specified callee writes the source. The scanner uses the same lock and excludes `.avkit-tmp`.

This acceptance relies on the stated whole-operation lock contract including cleanup, and on preserving its ownership condition when coding. The real service does not exist yet; rollback and races were traced, not executed.

## Q7 — Crop source and its readers

Accepted `CaptureSource.Crop` after Import, with no wire-map entry or migration. The mapper writes `.name` and dynamically reconstructs CaptureSource; API source is a string; the renderer catalog's source is also a string with no source whitelist/label map in the capture feature; MCP forwards the output JSON. The three explicit member/source tuples are listed for update.

## Q8 — MCP, baseline and fixture

Accepted the strict member, POST row, generic body forwarding, timeout branch, non-destructive status, description and audit step/cleanup registration. D-499's local facts are accurate: the committed authoritative baseline has 70 pass entries and no crop; the update/annotation rules forbid the proposed shortcuts; the caption issue is open; Session 57's cited rule rejects NEW. A's exact missing set plus served/absent checks preserves extra-key, non-pass-issue and finding-issue checks and fails once crop is baselined. B/C/D are explicitly subject to re-planning; no option was selected here.

One clerical pin was missed: `mcp-server/tests/audit/runner-fake-backend.test.ts:76` expects 70 actions from the built server. Add its 71 update and path to scope. Build the MCP dist before testing its new action set; the current gate places `mcp-build` after `mcp-tests`. A fresh build will reveal that stale pin. This is not a newly invented product requirement or an approval blocker.

The separate RNG and appended cases preserve existing case values. AC-90.8 compares parsed JSON and PNG pixels, so the row's diff check still matters for byte identity. The fixture generator currently explicitly writes LF (`tools/capture_bake_fixture.py:217`) while the committed JSON is CRLF; row 5's required CRLF check needs an explicit writer adjustment in the already-scoped generator. The unchanged region PNG pair must remain byte-identical when that command also regenerates it.

## Q9 — Console and error paths

Accepted fixed crop refusals, generic unlogged 503, and interception of `probe`'s path-bearing exceptions after publication. HealthService removes the existing bake log's path before stdout/ring/file rendering. Successful API/MCP responses intentionally contain the crop's paths and sanitized display name; that is the response contract, not a Console emission. F6 corrects the impossible ring positive control; the marker/engine controls remain useful.

## Q10 — Red tests and guards

The row-1 stubs cover new domain/port/adapter names that Red tests need. Service/schema names need not be imported for HTTP Reds; the task keeps new imports inside tests and puts assertions before missing values. Enum membership, adapter output existence, HTTP statuses, absent audit step/description and action counts can all fail by assertion on today's code. The pytest and Vitest selectors match the declared names. `red-check.py` aggregates both row-4b receipts before checking all seven requirements, and refuses missing/assertion-free required blocks.

F2, F5 and F6 are Green-oracle defects rather than missing-name Red failures. No demonstrated gate that cannot fail on a materially missing deliverable was found; none is classified control-defeat. Product suites and parser selftests were not rerun here; the provided plan-time selftest receipts were read.

## Q11 — Endings, identity, scope, queue and safety

Independent byte reads confirm CRLF in the seven source files, OpenAPI and fixture JSON. The task requires preservation and checks regeneration; Q8 names the generator adjustment. The plan-local Python scripts parse. Named current executables exist; future Session 58 and new crop files are explicitly scheduled dependencies/deliverables.

The gate identity binds source/tests/config, fixture, scripts, registers/grouping and runtime inputs and excludes later project narratives. Its full worktree scan was not executed because this sandbox exposes the expressly forbidden local settings file. Scope covers the stated work apart from the clerical missing pin path above.

S8 reads actual `id:` entries and their following status; all three dependencies are pending now, so it refuses execution. S12 finds no ruling line now. S11 checks names only; exact signatures/messages/order/counts require the task's explicit re-read comparison before row 1. Neither the name check nor a file's ruling text independently proves human authorization. No new feature call requires external network/model work; generated images, fake fetches and the test app are local. The full existing suite's local subprocess/loopback harnesses are distinct from a live external audit. No forbidden runtime command was run during review.

## Checklist Results

Manual observations are by `codex-independent-reviewer`, exit code null. These are plan-review results, not product-suite passes.

| Check | Result | Procedure / evidence |
|---|---|---|
| PR-1 Plan/task alignment | pass | Compared contracts, AC locations, rows 0–6 and H1/H2: scope and dependency order agree. |
| PR-2 Not started | pass | 25 unchecked rows; production crop service and new e2e module are absent as expected. |
| PR-3 Task contracts | pass | Observed owner/deliverable/validation/status in each row. No paperwork finding raised. |
| PR-4 Validation realism | partial | Named executables exist; F2/F3/F5/F6 correct behavioral oracles. |
| PR-5 Source-backed planning | pass | Compared design/grouping/spec and decision log; kept D-499 open and Session 58 settled. |
| PR-6 Corrections readiness | pass | Explicit single-MEU handoff and rolling review paths; this is round 1. |
| PR-7 Scope discipline | pass | GUI/future marks map to the grouping; other omitted operations are outside this crop contract. |
| PR-8 Controls and observable behavior | fail | F1 loses a valid saved mark even though the declared origin-rule tests and fixed-point invariant can pass. No control-defeat finding asserted. |
| PR-9 Single-statement consistency | pass | Named contracts resolve repeated rules; case/count/generator notes above are clerical, not competing product contracts. |
| IR / source and executable checks | pass | Local design/spec sources and scheduled artifacts resolved; static probe parsed three scripts and found ten named executables. |
| DR / paperwork | n/a | Formatting/template ordering was excluded by the user's review scope. |
| AV / runtime implementation proof | n/a | Unstarted plan; no pytest, Vitest, Playwright, baseline or session gate executed. |

```json
{"schema_version":"evidence.v1","check_id":"s59-independent-image-and-collaborator-probes","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s59_review_probe.py","cwd":"P:/av-kit","scope":"Pillow 13 metadata/modes, existing adapter geometry and eraser, HealthService processor, Windows scratch filenames; no feature implementation executed","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review-8bcb4a68e796f5b340b20eae41b7ad8c71e1fab9-working-tree-read","fresh":true,"output":"PNG and JPEG crops: ICC_equal True, pixels_equal True, only icc_profile metadata. Zero-width rect crossing crop: 30 visible pixels, zero_rule_drops True. Eraser checkerboard: 72 unchanged of 144. Health ring: ['capture.registered'], source removed. Legal 244-character source created; planned 259-character temporary write: OSError errno 22. Bottom-sliver rounds to ((0,50),(2,50)), dy sign becomes 0. max_edge 8 and 3000 are outside 64..2576; substitutes scale to 4 and 0.8586667."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-independent-plan-static-observations","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s59_review_static.py","cwd":"P:/av-kit","scope":"Plan-local Python syntax, baseline snapshot, executable existence, selected file endings and unstarted state","phase":"static","exit_code":0,"result":"pass","tested_state":"plan-review-8bcb4a68e796f5b340b20eae41b7ad8c71e1fab9-working-tree-read","fresh":true,"output":"Three plan-local Python scripts parse. Baseline mcp-audit-baseline.v1: 70 entries, all pass, crop absent. Ten named executable paths exist. Seven source files, OpenAPI and fixture JSON have CRLF only. 25 task rows unstarted; crop_shot and new crop e2e file absent."}
```

## Verdict

`changes_required` — F1 is an evidence-backed High violation of saved-mark carry: the plan can pass its declared mark tests while dropping a visible crossing rect. The normal crop pipeline and source-preservation design are otherwise accepted. F2–F6 are non-blocking correctness/verification notes; they do not independently set the verdict. D-499 remains Mat's open decision. Report saved at `C:/Temp/av-kit/s59-plan-review-round-1.md`; the coordinator owns canonical adoption.

## Corrections Applied (2026-11-09)

Written by the plan's author acting as the corrections agent (`claude-opus-claude-code-coordinator`), not by a reviewer, for round 1 of loop `s59-plan-canonical-2026-11-08-capture-crop-copy`. The frontmatter verdict is now `corrections_applied`. Only the round-2 independent recheck can approve.

### Findings verified

6 confirmed, 0 refuted. Each finding was checked against the anchors it cites before the plan was changed.

| # | Evidence | Result |
|---|---|---|
| F1 | `domain/capture.py:166` allows a rect width or height of 0; `adapter.py:463-471` draws `[x, y, x+w, y+h]` with `width=max(1, stroke)` | Confirmed. A zero-width rect is a drawn line, so the origin shortcut dropped visible pixels |
| F2 | `adapter.py:191`, `:203` (`eraser_fill` takes a ring colour) | Confirmed. On a black-and-white checkerboard about half the covered pixels already have the fill colour |
| F3 | Session 58's plan `:121`, `:196` (`max_edge` 64 to 2576) | Confirmed. An 8 px or 3000 px applied edge can't be viewed at scale 1 |
| F4 | the review's probe; Session 58's `IMPORT_NAME` 100-character cap | Confirmed. `{stem}-crop.png.avkit-tmp` passes 255 characters for a 240-character stem |
| F5 | `C:/Temp/av-kit/s59-plan-probes.txt:71` | Confirmed. The bottom sliver rounds to `(0,50)` to `(2,50)`, so `dy` becomes 0 |
| F6 | `health.py:47-56`, `:207-234` | Confirmed. The ring keeps only `CONSOLE_FIELDS`, so no entry carries `source` |

### Changes made

- **F1**, `implementation-plan.md`:
  - `MARK_CLIP_BOX` limits the zero-size shortcut to highlight, pixelate and eraser.
  - The rect paragraph adds `x0 >= 0` and `y0 >= 0` to "inside", and gives the worked case: `(20, 0, 0, 40)` under a crop at `(10, 10)` sized 30×30 clips to `(10, 0, 0, 29)`.
  - AC-130.2 adds zero-width and zero-height rects crossing the crop (`"clipped"`) and wholly outside it (`"dropped"`).
  - D-486's `chosen` text matches.
- **F2**: AC-130.19 keeps the no-unchanged-pixel check for pixelate only. The eraser case puts a checkerboard inside a ring of one colour and asserts that the ring colour fills the whole clipped box. Row 4a's note matches.
- **F3**: "Same box, same pixels" and AC-130.13 run on a 3000×1500 PNG over five boxes: px, fraction, clamped at the right edge, 8×8 and 2800×1400.
  - `applied` equals `X-Capture-Region` in every case.
  - The view comparison at `max_edge` equal to applied's long edge applies only where that edge is 64 to 2576. Those are the first three boxes, each at most 1600, so the view stays under `IMAGE_MAX_BYTES`.
  - The other two boxes compare the crop with the source's own pixels.
  - Row 4a's note matches.
- **F4**: `CROP_NAME`'s default `{stem}` is the source stem cut to 100 characters (IMPORT_NAME's cap), with trailing ` ._-` stripped. AC-130.15 adds a 240-character stem. D-483's `chosen` text matches.
- **F5**: `MARK_CLIP_ARROW` and AC-130.3 now say a clipped arrow never reverses: no component of `to_xy - from_xy` changes sign, though rounding can make one zero. AC-130.3 also checks that each end is within 0.5 of its exact end. D-487's `chosen` text matches.
- **F6**: AC-130.22's positive controls are now:
  - the stdout `engine.created` line;
  - at least one new `capture.registered` entry in the ring slice taken across the crops;
  - `item.source` `"Crop"` in each response.

  `CONSOLE_FIELDS` is not widened. Row 4a's note matches.
- **Q4 clerical note**: a `name` keeps its case, so AC-130.15's `crop_CON.png` is the canonical spelling. A trailing `.png` is dropped in any case, and collisions still compare case-folded.
- **Q7 clerical note (the `runner-fake-backend.test.ts:76` pin)**:
  - The Pins table gains the pin (70 → 71, row 4b).
  - Files Modified, the row 4b text, the scope list in `session-gate.ps1` and the targets in `baseline.ps1` gain the file.
  - Row 5 and the gate's Fresh full stage build the MCP `dist` before `mcp-tests`.
- **Q8 clerical note (line endings)**: the generator is not changed.
  - `export_openapi.py:66` keeps `openapi.committed.json` CRLF.
  - `capture_bake_fixture.py:217` writes the fixture LF.
  - Git stores both as LF.
  - Row 5 now checks that `git ls-files --eol` reads `i/lf` for both, and that the region PNG pair is unchanged (`git diff --quiet`).
  - Its pwsh uses `Set-Content -Path ... -Value` and an array `-notmatch`, with no pipe characters. A pipe split the table cell; the task lint caught it before this section was written. `C:/Temp/av-kit/s59-eol-probe.txt` shows that the check passes on the real files and refuses a CRLF index line.
- **Q5 note, not changed**: thin rects with a wide stroke, and anti-aliased arrows, can differ locally. Round 1 accepted D-486's list as the known differences and asked for no change, so the list wasn't widened into a pixel-equivalence claim.
- `task.md`'s estimate line now says "six MCP test files".

### Mat's words after round 1

- "add 60M tokes and 2 more rounds": recorded with `review_ledger.py continue` (`C:/Temp/av-kit/s59-plan-ledger-continue.txt`). The loop now allows 5 rounds and 70,500,000 tokens.
- "D-499 A":
  - Recorded as `**Mat's ruling (2026-11-09):**` under D-499 in `human-gate-decision.md`.
  - The decision log's D-499 is now `Human-approved`, with option A chosen.
  - The plan's goal line, the gate summary and the Decision Log intro now say it is ruled.
  - `task.md`'s D-499 note says the rows are written for A.
  - `baseline.ps1`'s S12 check and `issue-file.py`'s ruling check both accept the recorded line (`C:/Temp/av-kit/s59-d499-parse.txt`).

Bytes after the corrections, all LF with 0 CRLF:
- `implementation-plan.md`: 85,635 B, `9faf53f3...`
- `task.md`: 45,243 B, `eb4adc6e...`
- `human-gate-decision.md`: 7,673 B, `b5a45a19...`
- `session-gate.ps1`: 11,231 B, `4dcd79db...`
- `baseline.ps1`: 14,237 B, `a26b8aec...`

`red-check.py`, `identity.py` and `issue-file.py` are unchanged.

### Blast-radius census

The receipts are `C:/Temp/av-kit/census-s59-<value>-<old|old2|new|variant|variant2>.txt` (42 sweeps over the plan folder, each `rg -F -n`, unfiltered). The index is `C:/Temp/av-kit/census-s59-summary.txt`, and the script is `C:/Temp/av-kit/s59-census.py`.

| Value | Sweeps | Result |
|---|---|---|
| same-box view | `max_edge = max(width, height)`; `long edge`; `max_edge` | Old 0. Plan `:100`, `:290` and `task.md:84` updated |
| AC-130.13 image | `2000×1500`; `3000×1500` | Old 0. `:290` updated |
| zero-size marks | `zero width or height is kept`; `zero-width box`; `zero-size shortcut`; `zero width or height`; `zero-width` | Old 0. `:122`, `:164`, `:279` and `:550` updated |
| arrow sign | `` sign of `dx` ``; `keeps its direction`; `never reverses`; `direction` | Old 0. `:123`, `:280` and D-487 updated. `:575` (Liang-Barsky keeps the direction, the per-point clamp doesn't) is consistent. `task.md:107` is unrelated |
| default stem | `{source.stem}`; `100 characters`; `source stem` | Old 0. `:119`, `:292` (AC-130.15) and `:506` updated |
| name case | `case-folded`; `case otherwise kept`; `casefold`; `case-fold` | `:119` updated. Consistent: `:119`'s collision rule, which case-folds; `:506`; `:515`. Unrelated: `:299` (the marker search) and `:510` (Session 58's `IMPORT_NAME` precedent) |
| eraser oracle | `a pixelate and an eraser each`; `ring colour`; `eraser` | Old 0. `:296` and `task.md:84` updated. The other 10 `eraser` sites name the kind and are consistent |
| Console controls | `` with source `Crop` in the ring ``; `ring line with source`; `CONSOLE_FIELDS`; `capture.registered` | Old 0. `:299` and `task.md:84` updated. `:130` and `:234` are consistent: the event logs `source`, and the Console drops it |
| served-action pin | `runner-fake-backend`; `70 → 71` | Plan Pins and Files Modified, `task.md:85`, row 5, `session-gate.ps1` and `baseline.ps1` updated (8 sites). The other `70 → 71` sites are consistent |
| MCP order | `` `mcp-tests`, `mcp-build` ``; `mcp-build` | Old 0. Plan Fresh full, `task.md` row 5 and `session-gate.ps1` updated |
| endings | `still CRLF`; `keep CRLF`; `i/lf`; `CRLF` | Old 0. Plan endings paragraph and row 5 updated. The other 16 `CRLF` sites state source-file endings and are consistent |
| MCP test count | `five MCP test files`; `six MCP test files` | Old 0. `task.md` estimate updated |
| D-499 ruling | `Pending Mat`; `Mat rules`; `ruled A`; `unruled` | Plan `:33`, `:89`, `:95`, `:465`, D-499 and `task.md:74` updated. Consistent: `issue-file.py:45` (the `--probe` dry run records a pending D-499 on a register copy); `:747` (why Mat rules it); S12 `:460` and `baseline.ps1:44`, `:55` (the stop when the ruling is missing) |

Blast-radius census: 13 values changed, 12 variants swept, 68 sites found, 30 updated, 38 confirmed consistent or unrelated.

Cross-doc sweep: 09 `:1017-1032` and design §6.3 and §6.5 (`:190`, `:215`, `:228-229`) were checked, and none was updated. They say a box mark is intersected and dropped only when empty, which the zero-size rect now meets. They say a Liang–Barsky arrow keeps its direction, which non-reversal states exactly. They name the default `{stem}-crop.png` without a length or case rule, so the 100-character cut and the kept case refine them without contradicting them. The cut is recorded in `CROP_NAME` and D-483, not in 09's Stage A text, whose SHA-256 the plan pins.

### Verification

- `lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier`: OK, 25 rows (`C:/Temp/av-kit/s59-plan-task-lint-d499.txt`).
- Decision probe: 26 decisions through D-499, no issues (`C:/Temp/av-kit/s59-decision-issue-probe-d499.txt`).
- `session-gate.ps1` and `baseline.ps1` parse with 0 errors.
- `red-check.py`, `identity.py` and `issue-file.py` are unchanged, so their round-0 selftests and dry run stand.
- No suite, build, app or network request was run.

## Recheck (2026-11-09)

**Workflow**: `/planning-corrections` recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | fixed |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | fixed |
| F5 | open | fixed |
| F6 | open | fixed |

### Confirmed Fixes

References to the plan, task and scripts below resolve under `docs/execution/plans/2026-11-08-capture-crop-copy/`. This recheck judges the corrected plan's ability to deliver the registered goal; it does not certify an implementation. Claude/Anthropic authored the plan and corrections; Codex is the independent reviewer. All writes were under `C:/Temp/av-kit`. No suite, application, baseline, issue-filing script, session gate or network request was run. Session 57's concurrent changes remain outside review.

- **R1 / F1 — fixed (`MARK_CLIP_BOX`, AC-130.2).** `implementation-plan.md:122`, `:164`, `:279` and D-486 at `:550` agree. Rects bypass the zero-size shortcut; the inside predicate includes both nonnegative-origin checks. Inclusive intersection keeps a crossing vertical or horizontal line, clips it to the closed pixel bounds and drops it only when that intersection is empty. The worked vertical case produces `(10, 0, 0, 29)` and the existing adapter paints all 30 pixels. The horizontal counterpart produces `(0, 10, 29, 0)`; wholly outside counterparts drop. Each of these four expected results differs from row 1's `(mark, "kept")` stub by assertion, and row 3's prescribed rule produces them (`task.md:81-82`). Zero-width highlight, pixelate and eraser retain the separate inside-origin rule. The probe checks the proposed rule against the existing adapter; it does not claim the future tests ran. The horizontal bake has two endpoint closure pixels beyond the original bake's pixel crop, consistent with Q5's already accepted limit on bake equivalence, not a recurrence of the lost line.
- **R2 / F2 — fixed (AC-130.19).** `implementation-plan.md:296` and `task.md:84` now distinguish the pixelate oracle from eraser ring fill. A constructible witness is a 20×20 black/white checkerboard at `(8,8)` in a 50×50 image otherwise coloured `(173,41,91)`, cropped at `(10,0)` to 30×40. Its clipped eraser box is `(0,8,18,20)`; the remaining top, bottom and right ring pixels have that colour. Existing `eraser_fill` and `apply_region_pass` fill every covered pixel with it; omitting the eraser fails the assertion (`packages/infrastructure/src/avkit_infra/capture/adapter.py:164-203`).
- **R2 / F3 — fixed (AC-130.13, D-401).** `implementation-plan.md:100`, `:290` and `task.md:84` agree: compare resolved boxes in all five cases, decoded view pixels only at scale 1, and original-source pixels for 8×8 and 2800×1400. Session 58's bounds are 64–2576 and its region scale is `min(max_edge / long_edge, 4)` (`../2026-11-08-capture-region-import/implementation-plan.md:121`, `:196`, `:220`). On a distinct-pixel 3000×1500 PNG, feasible px/fraction/clamped witnesses have applied sizes 1200×600, 1500×750 and 200×900; matching `max_edge` gives scale 1. The first three cases' stated maximum edge of 1600 keeps even uncompressed RGBA pixel data below the REST cap of 15,728,640 bytes. The 8×8 witness scales 4× at 64; 2800×1400 scales 0.92× at 2576. Both therefore use the correct direct source-pixel oracle. All five probe PNGs round-trip exactly.
- **R2 / F4 — fixed (`CROP_NAME`, AC-130.15).** `implementation-plan.md:119`, `:292`, `:506` consistently bound the default source stem to 100 characters and strip trailing ` ._-`. Including `_9999`, every listed image, sidecar, bake and temporary filename is at most 125 characters; even 100 supplementary Unicode characters occupy at most 225 UTF-16 units with the longest suffix. The cut itself can become empty or `CON`, but the mandatory `-crop` suffix makes the resulting crop stem nonempty and nonreserved (`-crop`, `CON-crop`). No fallback is needed to cure a device name produced by that cut. The long-name regression is constructible from a legal 240-character ASCII source stem.
- **R2 / F5 — fixed (`MARK_CLIP_ARROW`, AC-130.3).** `implementation-plan.md:123`, `:166`, `:280`, `:566` and `:575` agree on non-reversal and half-up rounding. Independently recomputing all eleven reference cases confirms the statuses, the diagonal `(7,0)→(93,50)`, both drops and the bottom sliver `(0,50)→(2,50)`. Every retained end is within 0.5 on each axis of its exact Liang–Barsky end; no retained component reverses sign. Allowing one component to become zero resolves the former impossible expectation.
- **R2 / F6 — fixed (`NO_RAW_CONSOLE`, AC-130.22).** `implementation-plan.md:299` and `task.md:84` now assert three separate observables. `HealthService._process` increments `seq` and appends each sanitized event (`packages/core/src/avkit_core/services/health.py:218-230`), so a before/after sequence slice excludes source registration before the crops and measures new registrations. The existing processor yields `capture.registered` without `source`, as required. A bounded probe observed two new registrations in `(2,4]`; removing the stdout engine event, the new ring registrations or a response's `item.source` independently falsifies its positive-control assertion. No widening of `CONSOLE_FIELDS` is required.

**R3 — accepted clerical corrections.** Case preservation and case-folded collision detection are distinct and now consistent: `name: "CON"` becomes `crop_CON.png` (`implementation-plan.md:119`, `:292`). The built-server pin is genuinely at `mcp-server/tests/audit/runner-fake-backend.test.ts:76`, using `dist/index.js` at `:12`; its update is in the plan inventory/pins, row 4b, baseline targets and gate scope (`implementation-plan.md:219`, `:352`; `task.md:85`; `baseline.ps1:191`; `session-gate.ps1:65`). Row 5 and the gate both build MCP before its tests (`task.md:86`; `session-gate.ps1:141-143`). The endings correction matches the actual writers and `.gitattributes`: OpenAPI's working copy is CRLF; the fixture writer emits LF; both index entries are `i/lf` (`implementation-plan.md:357`; `tools/export_openapi.py:66`; `tools/capture_bake_fixture.py:217`). Row 5's endings fragment contains no pipe character and preserves the region-PNG diff check. An independent pwsh probe accepted both real `i/lf` entries, rejected an `i/crlf` entry and observed `git diff --quiet` exit 0 for the region PNG pair. No regeneration was run.

**R4 — actual D-499 A accepted; parser limits stated explicitly.** The ruling at `human-gate-decision.md:7`, `Human-approved` decision at `implementation-plan.md:731-732` and `task.md:74` agree with Mat's supplied words. Extracting and executing only the pure parser fragments against in-memory brief variants gives:

| Brief variant | S12 parser exit | Issue ruling parser exit |
|---|---|---|
| Recorded A | 0 | 0 |
| Missing ruling | 1 | 2 |
| Option B | 0 | 2 |
| Option C | 0 | 2 |
| Option D | 0 | 2 |

Thus the answer to whether **both** refuse B/C/D is **no**: S12 checks ruling presence (`baseline.ps1:49-56`), whereas issue filing requires A and explicitly rejects the other options (`issue-file.py:52-61`). This matches S12's stated “unruled” stop condition (`implementation-plan.md:460`); it is not an option-A enforcement claim. Under the actual A ruling, both pass and the rows carry it out through `BASELINE_PENDING` and the filed follow-up (`task.md:85`, `:88`). A later B/C/D ruling would require revised rows before executing this A-specific plan; it would not be rejected by S12 alone. That hypothetical change is not a demonstrated delivery failure under the registered, settled A ruling and does not reopen D-499. The pending issue is correctly scheduled for row 6, not claimed to exist already; lookup by id found no current entry, and `YOUTUBE-CAPTIONS-IP-BLOCK` remains open.

**R5 — blast radius accepted.** Independently read all 42 raw census receipts and compared every full hit with current files: 100 literal hits, 68 unique `file:line` sites, no truncated or missing raw hits. The summary is an abbreviated index; the raw receipts carry the full lines. The correction log supplies updated/consistent dispositions by cluster. Re-read the actual changed contracts, ACs, decisions, task rows and script scope/order entries rather than treating the census as proof. The former generic rect shortcut, strict sign oracle, unconditional view-pixel comparison and unbounded default stem have no surviving competing rule. The remaining “Pending Mat” is confined to the documented `--probe` branch of the filing tool. Initial plan-cap prose still names three rounds; Mat's continuation receipt authoritatively raises this existing loop to five, with 70,500,000 tokens. That inherited initial value is not a new cap or a reason to reset the loop.

**R6 — earlier acceptances preserved.** The corrections change no resolver, source-preservation, pixel-mode/metadata, locking, cleanup or MCP forwarding contract. Session 58's not-yet-implemented shapes remain explicit prerequisites with S11 recheck before coding. All 25 task rows remain unchecked, MEU-130 is pending (`.agent/context/meu-status.yaml:3402-3422`), and no crop implementation is asserted. PR-1 through PR-9 pass for this recheck: task alignment, not-started state, row contracts, corrected test feasibility, source traceability, census/readiness, scope discipline, observable controls and contract consistency. Runtime implementation proof remains n/a. No new materially different failure was demonstrated.

```json
{"schema_version":"evidence.v1","check_id":"s59-round2-bounded-recheck","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s59_r2_probe.py","cwd":"P:/av-kit","scope":"Corrected mark rules, existing Pillow/adapter/HealthService collaborators, in-memory ruling parser variants and raw census completeness; no product-suite execution","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review-8bcb4a6-round2-working-tree-9faf53f3-eb4adc6e-b5a45a19","fresh":true,"output":"Four crossing/outside rect expectations differ from row-1 stub by assertion; vertical line rebuild matches all 30 pixels. Clipped eraser fills (173,41,91). Five distinct-pixel PNG cases round-trip exactly; first three scale 1, 8x8 scale 4, large scale 0.92. Derived names max 125 characters / 225 UTF-16 units. Eleven arrow cases satisfy non-reversal and rounding tolerance. Ring seq slice (2,4] contains two new capture.registered events; omission of each positive control fails. A parser exits 0/0; missing 1/2; B,C,D each 0/2 (S12 presence-only). All 42 raw receipts match 100 hits / 68 unique sites. PYTHONDONTWRITEBYTECODE=1."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-round2-endings","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/s59_r2_eol.ps1","cwd":"P:/av-kit","scope":"Two regenerated-file index endings and unchanged region PNG pair; no regeneration","phase":"static","exit_code":0,"result":"pass","tested_state":"plan-review-8bcb4a6-round2-working-tree-9faf53f3-eb4adc6e-b5a45a19","fresh":true,"output":"Both openapi.committed.json and capture-region-pass.json read i/lf w/crlf attr/text=auto; synthetic i/crlf entry refused. Region PNG pair git diff --quiet exit 0."}
```

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None.

### Remaining Findings

None.

### Verdict

`approved` — F1–F6 are fixed, including the sole High blocker. Executing the corrected plan after its dependency and human execution gates would deliver the registered crop-copy intent. No new High/Critical or other delivery finding remains. S12's presence-only parser is explicitly distinguished from issue filing's A-only parser above. This is plan approval, not execution authorization or implemented-behavior certification. Report written only to `C:/Temp/av-kit/s59-plan-review-round-2.md`; the coordinator owns canonical adoption.

## Corrections Applied (2026-11-09) -- Round 2 plan amendment, D-476

Written by the plan's author acting as the corrections agent (`claude-opus-claude-code-coordinator`), not by a reviewer, after round 2's approval. The frontmatter verdict is now `corrections_applied`. Only round 3's independent recheck can approve.

### Why the approved plan changed

- Row 0's S11 check found that a Session 58 shape this plan relies on, the `.avkit-tmp` pattern, differs from Session 58's plan. Session 58's execution review changed it: execution F1 (a failed import deleted another writer's `NAME.avkit-tmp`) and F2 (filesystem calls outside the mapped `try`, and Pillow's `SyntaxError` uncaught), recorded as its RULE-1 and RULE-2 (`docs/execution/reflections/2026-11-08-capture-region-import-reflection.md:41-43`).
- S11's response is "Stop; amend this plan through the plan review before row 1" (`implementation-plan.md:459`). Mat chose option A at the row-0 gate, in Mat's words: "A: plan round 3 (Recommended)". It is recorded as D-476 (`implementation-plan.md:749`).
- Session 58 has since landed in `8e79282`, so its code is now real: `_import_copy` (`packages/core/src/avkit_core/services/capture.py:512-546`), `_import_dest` (`:549-570`), `view`'s `except Exception` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:297-304`) and AC-129.9 (`tests/e2e/test_api_capture_region_import.py:627`).

### Changes made

- **`CROP_NAME`** (`implementation-plan.md:119`): every inbox-root entry ending in `.avkit-tmp` also takes its name without that suffix, as `_import_dest` does. The helper is `CaptureService._crop_dest(uow, inbox, stem)`, and its `iterdir` runs inside `CROP_CLEANUP`'s `try`.
- **`CROP_CLEANUP`** (`:126`): every filesystem call on the crop's paths runs inside one `try`. The temporary file is created with `open("xb")`, and `tmp` is set only after the create succeeds. `cut` is set when the adapter's `crop` returns, and `moved` is set by `os.replace`. The `except` removes `tmp` when set, and the crop, its sidecar and its bakes only when `moved` is true. A refusal raised while `cut` is false passes through unchanged after that cleanup; anything else is the 503. This replaces "re-raised before the first write", which no longer separates the cases once the temporary file exists before the adapter decodes the source.
- **Adapter `crop`** (`:174`, `:176`, `:179`): step 1 catches `Exception` on open and load, as `view` does. Step 3 no longer calls `load()` a second time outside that `try`. A failure of the save or of `probe(out)` is raised as `OSError("the crop could not be saved")`, so the only refusals `crop` raises are the two fixed, pathless ones.
- **Service step 3** (`:183`): it follows `_import_copy`, with the `tmp`, `cut` and `moved` flags, and cites `_unlink_if_file` at its current line, `:1145`.
- **AC-130.21** (`:298`): two tests are added. The first, "keeps a temporary file it did not write", runs `none`, `race` (`_crop_dest` patched), `replace` and `commit` against another writer's `shot-crop.png.avkit-tmp`, whose bytes must survive every case. The second registers a PNG, then damages its IDAT chunk in place, and expects a 422 `the image could not be opened` with no path.
- **D-476** is added to the decision log (`:749`), and the banner (`:465`) and the provenance row (`:323`) name it.
- **Budget** (`:108`): Mat set the execution loop at 60M tokens ("60M"), with the cap of 6 rounds.
- **`task.md`**: rows 4a (`:84`) and 5 (`:86`) carry the same notes. No validation command changed.

### What did not change

- `CROP_REQUEST`, `CROP_READ`, `CROP_PIXELS` apart from the adapter's error mapping, `CROP_SOURCE`, the mark mechanisms, `CROP_BAKE`, `CROP_RESPONSE`, `CROP_MCP`, `BASELINE_PENDING`, `NO_RAW_CONSOLE`, D-481 to D-499, and every other AC.
- No Session 58 shape other than the `.avkit-tmp` pattern differed. Row 0's baseline (`C:/Temp/av-kit/s59-baseline.txt`) ends `baseline: all steps exit 0`, at `HEAD` `f15626c`.

### Verification

- The decision log parses as YAML: 20 entries, unique ids, and D-476 and D-499 `human`.
- `lint_task_contract.py` on `task.md`: `OK: 25 row(s)` (`C:/Temp/av-kit/s59-amend-task-lint.txt`).
- Both plan files keep their LF endings. The whole edit, old and new text, is `C:/Temp/av-kit/s59-amend-diff.txt`.

## Recheck (2026-11-09) -- Round 3

**Workflow**: `/planning-corrections` recheck
**Agent**: codex-independent-reviewer

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | fixed | fixed |
| F4 | fixed | fixed |
| F5 | fixed | fixed |
| F6 | fixed | fixed |

### Confirmed Fixes

References abbreviated to `implementation-plan.md` and `task.md` resolve under `docs/execution/plans/2026-11-08-capture-crop-copy/`. This is the independent Codex recheck of Claude Code/Anthropic's D-476 amendment. The registered intent remains the complete Intent Anchor above. Mat's D-476 A ruling, D-499 A, the grouping, Session 58's settled decisions and round 2's acceptances were preserved. HEAD is `f15626c25af428e33c0274cb280eef6579455320`, branch `main`. The amendment changes only the two plan files; all five plan-local scripts match HEAD. All 25 task rows remain unchecked and the crop service/helper/e2e module are absent. Row 0's supplied receipt says `baseline step session58-shapes exit=0` and ends `baseline: all steps exit 0`; that receipt was read, not rerun.

- **A1 — accepted: ownership (`CROP_NAME`, `CROP_CLEANUP`).** `implementation-plan.md:119`, `:126`, `:183` and `:754` implement Session 58 RULE-1. With another writer's `shot-crop.png.avkit-tmp` present, the name is occupied and normal allocation chooses `shot-crop_2.png`. If the helper instead returns the occupied name, exclusive `open("xb")` fails before `tmp` is assigned; cleanup has no acquired temporary path and `moved` is false. The foreign bytes survive and the result is the fixed 503. After successful exclusive acquisition, a save failure removes only the acquired temporary file. A replace failure does the same with `cut` true and `moved` false. After successful replace, a probe, sidecar-write, bake-write or commit failure removes the published crop and its derived paths. A partial sidecar or bake is included. The temporary name is then absent, so its cleanup is harmless. Derived cleanup guarded by `moved` is sound: those writes occur only after replace, and `CROP_NAME` checked every image/sidecar/bake destination free while the same lock remains held through cleanup. This is the existing single-process `CAPTURE_FILE_LOCK` contract (`packages/core/src/avkit_core/services/capture.py:91`, `:346`), not a new cross-process filesystem guarantee. The real predecessor creates exclusively and assigns ownership afterward at `:531-532`; its occupied-name handling is at `:555-570`. No source file or source-derived path enters the crop's cleanup set. **Not accepted: none.**

- **A2 — accepted: mapping and decode coverage (`CROP_CLEANUP`, `CROP_PIXELS`).** The whole-UoW boundary at `implementation-plan.md:126` and `:183` explicitly includes `_crop_dest`'s `iterdir`, `ensure_dir`, the source-sidecar read, exclusive create, adapter crop, replace, both probes, row upsert, sidecar/bake writes and UoW exit/commit. Step 2's semicolon-separated order at `:182` describes work inside that boundary, not calls to perform before it. Inbox path resolution also belongs inside this boundary under the stated every-filesystem-call rule: `_inbox` calls `expanduser().resolve()` (`packages/core/src/avkit_core/services/capture.py:1011-1016`). No listed forward call remains prescribed outside it. Adapter open and load share `except Exception` (`implementation-plan.md:174`), matching actual `view` (`packages/infrastructure/src/avkit_infra/capture/adapter.py:297-304`), so both `SyntaxError` and `ValueError` are covered. Step 3 no longer repeats `load()` outside that handler (`implementation-plan.md:176`). Save and `probe(out)` failures become the pathless `OSError` at `:179`; other unexpected crop/conversion failures reach the service's broad 503 mapping. The real UoW commits in `__exit__` and always closes its session (`packages/infrastructure/src/avkit_infra/database/unit_of_work.py:54-65`), so placing that exit inside the try matters. **Not accepted: none.**

- **A3 — accepted: refusal versus 503 (`CROP_READ`, `CROP_CLEANUP`, `NO_RAW_CONSOLE`).** `cut` stays false until the adapter returns (`implementation-plan.md:126`). The pre-cut refusals are the fixed name checks (`:181`), missing-row/malformed-sidecar rules (`:117`), shared resolver messages (`:116`), and the adapter's fixed decode/changed-size refusals (`:174-175`). CROP_READ still requires malformed sidecars to become `AnnotationValidationError("sidecar is malformed")`; it does not authorize forwarding a raw parser diagnostic containing sidecar content. Before the adapter returns, its save or `probe(out)` can already have written bytes, but their exceptions are converted to `OSError`, which is outside the refusal set and becomes 503 even while `cut` is false (`:179`). The later service `probe(crop)` occurs after `cut` is true, so AC-130.21's injected path-bearing `InboxPathError` also becomes 503, never a path-bearing 422 (`:298`). The adapter's direct AC-130.11 still writes no output before rejecting invalid input; at service level the already-created owned temporary file is removed before the same 422/409 refusal is returned. AC-130.16's 404/422/409 cases remain consistent (`:288`, `:293`). The path-bearing real `probe` messages at `packages/infrastructure/src/avkit_infra/capture/adapter.py:281-289` are therefore contained at both crop call sites. **Not accepted: no refusal-path leak demonstrated under these contracts.**

- **A4 — accepted: constructible, discriminating tests (AC-130.21).** `implementation-plan.md:298` and `task.md:84` require the foreign-temporary cases `none`, `race`, `replace` and `commit`, including exact success name, failure status, unchanged inbox names/no new row on failure, and preserved foreign bytes in every case. With `shot.png` already registered, patch replace/probe/commit against the expected crop destination (`shot-crop_2.png` in ordinary allocation), as row 4a specifies. In particular, copying Session 58's broad `any .png exists` commit trigger literally would trip on the existing source; the crop-specific trigger reaches the intended commit. The race helper does not exist at row 4a: install that test patch with `raising=False` (the scratch witness used `patch.object(..., create=True)`) so the HTTP status assertion remains the Red failure. A direct default-raising patch copied verbatim from Session 58 would instead fail in setup and is not an acceptable realization of the plan's assertion-first rule (`task.md:34-36`, `:80`; `implementation-plan.md:414-419`). This is a constructible fixture choice, not missing product behavior or an impossible Red contract.

  The damaged-IDAT witness is also constructible. The probe first decoded a valid 64x48 PNG, then retained its IHDR, dimensions and total byte length while shortening IDAT and inserting an invalid chunk. `Image.open` still reported 64x48; `load()` raised `SyntaxError` under Pillow 13.0.0. Registering the valid source before this mutation avoids setup's decoder. To inspect no-new-row afterward, read the UoW directly or restore the exact original bytes before a scanning `GET /captures`; scanning the still-damaged source is outside this crop-refusal oracle (`packages/core/src/avkit_core/services/capture.py:343-356`). Against the missing crop route all five new cases reach an assertion: 404 differs from the respective expected 201, 503 or 422. They do not invoke row 1's adapter stub through an absent route. The existing direct adapter Reds still assert output existence or expected exceptions before reading missing output (`task.md:36`; `implementation-plan.md:288`, `:414-416`). The fixed ownership model distinguished the four expected outcomes and additional save/probe/sidecar/bake failures. **Not accepted: no impossible expectation or assertion-free required failure found; these are feasibility probes, not execution of the future tests.**

- **A5 — accepted: blast radius, with one clerical note.** Contracts at `implementation-plan.md:119`, `:126`, `:174-179`, `:183`, AC-130.21 at `:298`, provenance at `:323`, D-476 at `:749-765`, and row 4a/5 at `task.md:84`, `:86` agree. The scanner still uses the same lock and ignores `.avkit-tmp` by extension, preserving AC-130.20 (`implementation-plan.md:297`; `packages/core/src/avkit_core/services/capture.py:346-353`). CROP_READ's pathless 422/409 rule and step 2's order remain valid with the exclusive temporary file preceding decode. `_unlink_if_file` really is at `packages/core/src/avkit_core/services/capture.py:1145`; the new predecessor/view/test anchors also resolve to the cited behavior. Older moved anchors do not change the named operations, and `task.md:32` requires current-anchor reads and handoff corrections. The 60M execution budget is Mat's record at `implementation-plan.md:108`, not a finding.

  **Clerical note:** D-490's `chosen` text at `implementation-plan.md:608` still says any exception "after the first write" becomes 503. Read it through the explicit "D-476, refining D-490" at `:126` and D-476's later human-approved text at `:754`: the named contract's `cut` rule governs. Synchronizing that historical summary would remove the stale phrase, but there is no unresolved behavioral choice and no delivery blocker. No F7 is opened for it. F1-F6 remain fixed: the amendment does not change their corrected geometry, naming bound, pixel oracle, eraser oracle or Console controls (`implementation-plan.md:119`, `:122-123`, `:279-280`, `:290`, `:296`, `:299`). **Not accepted: no new material contradiction.**

PR-1 through PR-9 pass within this amendment's scope: the two plan files align; implementation remains unstarted; row contracts and validation commands are retained; the new negative cases are feasible; D-476 supplies the human/source basis; the amendment can be corrected and handed off; no scope item was cut; ownership and exception paths have observable negative oracles; and the governing named rule is unambiguous. Paperwork review and runtime implementation certification are n/a under the requested scope.

The following evidence is plan-local review evidence. It does not certify a production implementation or fresh product-suite run. Python used `PYTHONDONTWRITEBYTECODE=1` and `-B`. No pytest, Vitest, Playwright, baseline, issue-file, session gate, dev app, network request or repository write was run. Only scratch files under `C:/Temp/av-kit` were written.

```json
{"schema_version":"evidence.v1","check_id":"s59-round3-bounded-probes","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s59_r3_probe.py","cwd":"P:/av-kit","scope":"Pillow damaged-IDAT and Windows exclusive-create witnesses; finite-state model of amended ownership/refusal flags; missing-helper patch feasibility and missing-route assertion oracles","phase":"targeted","exit_code":0,"result":"pass","tested_state":"plan-review-f15626c-plan-8eb90f1f69e8be3c0d47215e356225c2747c9423898e1c3dc42fbe558a988f6c-task-b5d12a059ff8c2ab985f1d489099b9cbf46d3e7db1ffdf2040dfbe78d8373643","fresh":true,"output":"Pillow 13.0.0, bytecode disabled. Damaged IDAT: dimensions 64x48 and total byte length preserved, load raises SyntaxError. Flag model: none 201; race/save/replace/probe/sidecar/bake/commit 503; decode 422; size 409. Every modeled failure restores original names and preserves foreign bytes. Real open('xb') raises FileExistsError without ownership or byte changes. Missing helper can be patched with create=True; missing-route 404 differs by AssertionError from 201/503/422. No future crop service or HTTP stack was executed."}
```

```json
{"schema_version":"evidence.v1","check_id":"s59-round3-amendment-state","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s59_r3_static.py","cwd":"P:/av-kit","scope":"Exact two-file amendment, focused boundary census, unchanged scripts, unstarted state and supplied baseline receipt","phase":"static","exit_code":0,"result":"pass","tested_state":"plan-review-f15626c-plan-8eb90f1f69e8be3c0d47215e356225c2747c9423898e1c3dc42fbe558a988f6c-task-b5d12a059ff8c2ab985f1d489099b9cbf46d3e7db1ffdf2040dfbe78d8373643","fresh":true,"output":"HEAD f15626c25af428e33c0274cb280eef6579455320, main. Changed paths only implementation-plan.md and task.md. All five plan-local scripts equal HEAD. 25 unchecked rows; crop_shot, _crop_dest and crop e2e module absent. Focused census identifies D-490:608 as the stale summary; the named CROP_CLEANUP:126 and human D-476:754 resolve it. Supplied baseline reports session58-shapes exit=0 and baseline: all steps exit 0; it was not executed by this reviewer."}
```

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

None.

### Remaining Findings

None.

### Verdict

`approved` — F1-F6 remain fixed. The D-476 amendment correctly carries Session 58's ownership and file-error corrections into the crop plan, and its new negative cases are constructible and able to fail. Executing this amended plan would deliver the registered crop-copy intent. No evidence-backed High/Critical or other delivery finding remains. D-490's stale summary is a non-blocking clerical note, resolved in favor of the explicitly refined named contract. This approves the plan only; implementation and its runtime checks remain the coordinator's subsequent work. The complete rolling report is `C:/Temp/av-kit/s59-plan-review-round-3.md`; canonical adoption belongs to the coordinator.
