---
date: "2026-11-11"
project: "capture-export-copy"
meu: "MEU-136"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-11-capture-video-sheet-MEU-135-handoff.md"
---

# Handoff: 2026-11-11-capture-export-copy-MEU-136-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-136 `capture-export-copy`. A caller writes a resized or re-encoded PNG, JPEG or WebP copy of a shot into the capture inbox, as a new shot with source `Export`. The source is the shot as it is shown: its bake when it has saved marks, otherwise the original. The source's file, sidecar, bake and row are only read.
- **REST.** `POST /api/v1/captures/{id}/export` takes `{format, max_edge?, quality?}` and answers 201 with `{shot, source_id}`. `shot` holds `id`, `path`, `width`, `height` and `bytes`. No image bytes are returned.
- **MCP.** `avkit_capture` `export` sends the same body, minus `action` and `id`, on `ADD_TIMEOUT_MS` (120 s, D-616).
- **Rulings.**
  - D-608 A: the description eval ran as six Haiku runs, the three tasks on the real surface and on the real surface plus each action's `_meta` text.
  - D-621 A, in execution at row E-4: AC-136.19 cites the exit-1 eval receipt as it stands (§Evidence, The description eval).

**Build Plan Section**: [09 §Export copy](../../../docs/build-plan/09-screenshot-capture.md) (the Delivered note at `:1201`).
**Predecessor**: [MEU-135 handoff](2026-11-11-capture-video-sheet-MEU-135-handoff.md), Session 63. This is the last session of the grouping `.agent/context/grouping/2026-11-09-video-stills-session-grouping.md` (Sessions 62 to 64, D-500 to D-505). Grouping D-501 placed this MEU after the sheet, and D-505 asked for the eval here.

- **Core enum (row 1; D-618).** `CaptureSource.Export` (`packages/core/src/avkit_core/domain/enums.py:226`), after `Video`, with no register wire value (`EXPORT_SOURCE_MEMBER`).
- **Port (row 1; D-614).** `ImageAnnotatePort.export` (`packages/core/src/avkit_core/ports/capture.py:76`): positional `source`, `source_size` and `out`, keyword-only `fmt`, `size` and `quality`, returning an `ImageProbe`.
- **Service (rows 1 and 3; D-609 to D-612, D-615).** In `packages/core/src/avkit_core/services/capture.py`:
  - the constants `EXPORT_FORMATS` to `EXPORT_REFUSALS` (`:191-202`), with `EXPORT_REFUSALS` equal to `CROP_REFUSALS`;
  - `ExportResult` (`:206`);
  - `export_size` (`:239`), for `EXPORT_SIZE`, and `export_stem` (`:253`), for `EXPORT_NAME`;
  - `CaptureService.export_shot` (`:1691`), for `EXPORT_CHECKS`, `EXPORT_SOURCE` and `EXPORT_WRITE`, with the one `capture.export` log line (`:1769`);
  - `_crop_dest`'s keyword `ext` (`:1785`), defaulting to `FLATTEN_PNG_SUFFIX` (D-615).
- **Adapter (row 3; D-613, D-614, D-619).** In `packages/infrastructure/src/avkit_infra/capture/adapter.py`: `CaptureAdapter.export` (`:572`), `EXPORT_DEPTH_MODES` (`:84`), `_png_key` (`:311`) and `_depth_to_l` (`:329`), for `EXPORT_ENCODE`.
- **API (row 3).**
  - `CaptureExportIn` (`packages/api/src/avkit_api/schemas/captures.py:270`), `CaptureExportShotOut` (`:291`) and `CaptureExportOut` (`:301`).
  - The route is at `packages/api/src/avkit_api/routes/captures.py:500`, declared after `/{id}/crop` (`:468`) and before `DELETE /{id}` (`:523`).
  - `wiring.py` doesn't change: `CaptureService` already gets `annotate`.
  - `openapi.committed.json` is regenerated.
- **MCP (row 3; D-616, D-620).**
  - `mcp-server/src/toolsets/capture.ts`: `EXPORT_TEXT` (`:85`), the exported `EXPORT_UNKNOWN_KEY` (`:89`), the description map entry and the strict `export` member (`:334`), after `sheet`.
  - `mcp-server/src/toolsets/registry.ts`: the `ACTION_INDEX` row (`:137`) after `sheet`, and `export` in the `ADD_TIMEOUT_MS` selection (`:404`).
  - `mcp-server/scripts/audit/plan.ts`: the offline `capture.export` step after `capture.sheet` (`:1703`), and the `capture.crop` step now sets the state key `crop_id` (`:1622`), which the export step reads (Departure 2).
- **Tests.**
  - `tests/unit/test_domain_capture.py:985`: AC-136.1.
  - `tests/unit/test_capture_export_adapter.py` (new, LF): AC-136.4 to .7.
  - `tests/unit/test_capture_export_service.py` (new, LF): AC-136.2, .3 and .8 to .12.
  - `tests/e2e/test_api_capture_export.py` (new, LF): AC-136.13 to .15.
  - `tests/e2e/test_api_openapi.py:298`: AC-136.16.
  - `mcp-server/tests/capture.test.ts` and `audit/coverage.test.ts`: AC-136.17 and .18.
  - The pins in the plan's §Pins that move (rows 1, 2a and 2b), plus the four named below under §Evidence.
- **Spec text and records (row 6).** 09's Delivered note (`docs/build-plan/09-screenshot-capture.md:1201`), MEU-136 `ready_for_review` with this plan (`.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`), and grouping row 64 `executed`.
- **No UI (D-617).** An export is an ordinary shot on the Capture page, as a sheet is. D-617 corrects Session 63's D-593 reasoning, which said MEU-136 adds a UI action.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-11. The Codex plan review approved in round 4 of 5 ([plan-critical-review.md](2026-11-11-capture-export-copy-plan-critical-review.md)). Mat then said "accept the plan, D-608 A, execution budget 60M". That accepts the plan, rules D-608 A, and sets the execution loop's budget at 60M tokens over at most 6 rounds (`implementation-plan.md:112`; the decision log quotes it at `:394`). At row E-4 Mat ruled D-621 with "A" (`implementation-plan.md:611`), after asking for an independent Opus subagent's read at xhigh. A commit or a push waits on Mat's own words, and the review's approval is Codex's.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

- **The shot id** comes from the path. It reaches the database lookup, crop's existing `capture shot {id} not found` message, the 201 body's `source_id` and the `capture.export` log line. Its writers are the caller and the ids the service itself made.
- **The source's stem** goes through `export_stem` into the export's name, which reaches the inbox, the row, the 201 body's `shot.path` and the Capture page. `_IMPORT_STEM_DROP` turns a control character or a lone surrogate into `_`, and the stem always ends in `-export`, so it is never a Windows reserved name (AC-136.3).
- **`format`** comes from a closed set. It picks the encoder and the suffix, and no message echoes it.
- **`max_edge` and `quality`** reach `export_size` and the encoder. A refused value gets a fixed message that echoes nothing (AC-136.8, AC-136.14).
- **The inbox path** is read from settings at use (`self._inbox()`), and reaches `dest`, the row and the 201 body only.
- **Pillow's exception text**, which can hold a path, stays in `__cause__`. Error bodies, the log and the console carry only the fixed messages (AC-136.6, AC-136.15).
- **The exported pixels** come from the source's pixels only, with the ICC profile. No EXIF, XMP or text chunk reaches the file (AC-136.4).
- **An unknown MCP key** in an `export` call is refused with the fixed `EXPORT_UNKNOWN_KEY`, so a key holding a path never comes back (D-620, AC-136.17).
- **The marker checks.** AC-136.12 puts a marker in the source stem, and AC-136.15 puts one in the inbox path on the real stack with `HealthService` built first (Session 54 RULE-2). The marker is absent from every error body, the log ring, stdout and stderr, and a positive control finds it.
- **No network.** Every test image is made by Pillow in a temp folder. The eval's clips were made by the pinned FFmpeg under the eval root, outside the repository.

### Deadline inventory, as built (Session 62 RULE-1)

Export has no deadline, as crop has none. Every blocking call, with its bound:

| # | Blocking call | Where | Bound as built |
|---|---|---|---|
| 1 | `CAPTURE_FILE_LOCK` wait | `export_shot` | the holder's own. An export holds the lock through its own encode, so a second export can wait one export's encode. Not a numeric bound |
| 2 | Connection checkout and commit | `export_shot` | SQLite `busy_timeout` 5,000 ms, as crop |
| 3 | Open and decode the source | `CaptureAdapter.export` | Pillow's `DecompressionBombError` above 178,956,970 px, which is the fixed open refusal |
| 4 | Resize and encode | `CaptureAdapter.export` | none. The plan-time worst case is a full-size WebP at Pillow's pixel refusal edge, 82.53 s (`s64-plan-cap-probe.txt`) |
| 5 | `probe` of the output and `stat` | `export_shot` | one decode of the output |

So `export` joins `ADD_TIMEOUT_MS` (120 s), as crop, frames and sheet are (D-616). The 120 s is not a bound either. On a slower machine, or behind another export holding the lock, the client can give up first. The server still finishes the export whole or discards it whole (`EXPORT_WRITE`), so the agent's next `list` shows the new shot or nothing.

### Documented limits

- **JPEG has no alpha.** A transparent source's alpha, or its transparency key, is dropped before any resize, so its stored colour shows at every size.
- **A resized PNG or WebP** keeps each fully transparent pixel's alpha 0 but not its hidden colour, because Pillow resamples alpha premultiplied.
- **16-bit sources.** A 16-bit gray PNG is mapped to 8 bits by `v × 255 / 65535` rounded half up for JPEG and WebP, and kept at 16 bits for an unresized PNG (D-619). Pillow opens a 16-bit gray-and-alpha or 16-bit RGB PNG as 8-bit before export sees it. A 16-bit RGB key can't be matched after that, so export removes it and that colour exports opaque.
- **The stored frame is kept.** Export doesn't apply `exif_transpose`. A scanned JPEG or WebP tagged with orientation 5 to 8 exports sideways, with the tag dropped. AC-136.7 records this behaviour by test for `CAPTURE-EXIF-SCANNED-ORIENTATION`. The issue still applies and is not fixed here (D-613).
- **`CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST`** was not observed. Export never scans the inbox and writes only a file it has just encoded and probed.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-136.1 | unit | Type characterisation of row 1: `ImageAnnotatePort.export`'s parameters and kinds; `CaptureAdapter.export`'s signature equals the protocol's; `CaptureSource` ends `Crop`, `Video`, `Export`; `Export` has no register wire value. It passed from row 1 and ran as a guard in row 2a | 09 Source member | `tests/unit/test_domain_capture.py:985` | ✅ |
| AC-136.2 | unit | `EXPORT_SIZE`: the eight named cases; `None`, an equal edge and a larger edge unchanged; the exhaustive loop over widths and heights 1 to 200 and `max_edge` 64 to 220 against `Fraction` half-up rounding, never growing, both edges at least 1, a square kept square and no edge order flipped (Departure 1) | 09 Request | `tests/unit/test_capture_export_service.py:243`, `:280` | ✅ |
| AC-136.3 | unit | `EXPORT_NAME`: `shot-export`, `Łodz-export`, the surrogate, control-character, `..` and empty stems, the 100-character cut, `CON-export`; `_crop_dest` with `ext=".jpg"` against an empty inbox, an existing `.png`, an existing temp, and no `ext` still `.png` | 09 Name; D-612, D-615 | `test_capture_export_service.py:315`, `:340` | ✅ |
| AC-136.4 | unit | `EXPORT_ENCODE` with the real `CaptureAdapter`: metadata dropped and the ICC profile kept for each format; no resample at the source size; the modes; the depth map over all 65,536 values; the four-block `I;16` source, keyed and unkeyed; the stored colour under alpha 0; the keys Pillow misreads (1-px columns, 1-, 2- and 4-bit stripes, 16-bit RGB) | 09 Writes, Tests; D-614, D-619 | `tests/unit/test_capture_export_adapter.py:258`, `:294`, `:313`, `:329`, `:353`, `:379`, `:405`, `:452`, `:471`, `:493`, `:518`, `:548` | ✅ |
| AC-136.5 | unit | Quality: quality 20 gives strictly smaller bytes than 95 for JPEG and WebP; a recording `save` sees `quality=90` for `None`, 37 for 37, and no `quality` for PNG | 09 Request, Tests | `test_capture_export_adapter.py:568`, `:580` | ✅ |
| AC-136.6 | unit | Adapter failures: the fixed `the image could not be opened`, crop's `ConflictError`, and the fixed `the export could not be saved` without the marker | 09 Writes | `test_capture_export_adapter.py:621`, `:634`, `:646` | ✅ |
| AC-136.7 | unit | `CAPTURE-EXIF-SCANNED-ORIENTATION` characterisation: a 400×300 JPEG tagged 6 exports at 400×300 in its stored frame, with no orientation tag | Known issue; D-613 | `test_capture_export_adapter.py:672` | ✅ |
| AC-136.8 | unit | `EXPORT_CHECKS`: every refusal of the plan's list makes no `export` call, leaves the inbox as it was and adds no row; type and message checked first; the bounds 64, 16383, 1 and 100 accepted | 09 Request; D-609, D-610, D-611 | `test_capture_export_service.py:398`, `:453`, `:471` | ✅ |
| AC-136.9 | unit | `EXPORT_SOURCE` call trace: a marked shot passes the bake, the size, the temp, `fmt`, `export_size(…)` and `quality`; no sidecar and an empty sidecar pass the original | 09 Source | `test_capture_export_service.py:498`, `:525` | ✅ |
| AC-136.10 | unit | `EXPORT_WRITE` with the real adapter: the temp opened `"xb"`; another writer's temp left byte for byte; `-export` then `-export_2`; PNG then JPEG gives `x-export_2.jpg`; the source's file, sidecar, bake and row unchanged; the new row `Export`; `bytes` equals the file size; no temp left | 09 Writes, Name | `test_capture_export_service.py:567`, `:621`, `:635` | ✅ |
| AC-136.11 | unit | Failure cleanup: four injected failures, for PNG and for JPEG, give exactly `the export could not be written` and leave no file, temp or row; an adapter refusal passes with its own text | 09 Writes | `test_capture_export_service.py:706`, `:733` | ✅ |
| AC-136.12 | unit | `NO_RAW_OUTPUT` in the service: `capture.export` logs exactly `shot_id` and `source_id`; no record and no refusal holds the marker | NO_RAW_OUTPUT | `test_capture_export_service.py:755`, `:776` | ✅ |
| AC-136.13 | API | The real stack: the 201 body's exact keys; each format's file opens with its size and `bytes`; 64×43 and never grows; no EXIF; a shot annotated through the API exports its bake; the source unchanged; `-export` and `-export_2`; `source` `"Export"` kept after a scan | 09 Response, Tests | `tests/e2e/test_api_capture_export.py:135`, `:188` | ✅ |
| AC-136.14 | API | Route validation: each schema refusal is the fixed 422, `64.0` and `80.0` sent as raw JSON; `quality` with `png` gives its fixed 422; an unknown id 404; no file or row added | 09 Request | `test_api_capture_export.py:237` | ✅ |
| AC-136.15 | API | Path-free errors on the real stack: the missing bake 404, the undecodable source 422, the masked 503; the inbox marker absent everywhere, with a positive control | 09 Writes; S54 RULE-2 | `test_api_capture_export.py:282` | ✅ |
| AC-136.16 | API | OpenAPI: the export route with `CaptureExportIn` and `CaptureExportOut` in the committed snapshot; 78 operations; `--check` passes; `/{id}/export` after `/{id}/crop` and before `DELETE /{id}` | 09 Tests | `tests/e2e/test_api_openapi.py:298`; H1-4 | ✅ |
| AC-136.17 | MCP | `EXPORT_MCP`: keys accepted and refusals before fetch; the marker key gets exactly `EXPORT_UNKNOWN_KEY` and isn't echoed, and crop echoes it as the positive control (D-620); `64.0` and `80.0` reach REST as `64` and `80` (D-610); the body minus `action` and `id` on `ADD_TIMEOUT_MS` (D-616), as AC-135.18 checks for sheet; the description markers | 09 Request, Response | `mcp-server/tests/capture.test.ts:1360`, `:1376`, `:1414`, `:1440`, `:1463`, `:1498` | ✅ |
| AC-136.18 | MCP | `ACTION_INDEX` has 75 rows with `export` after `sheet`; REST body keys equal the zod keys minus `action` and `id`; the fake backend's 201 body reaches the tool result; `BASELINE_PENDING` ends with `avkit_capture.export`; `AUDIT_PLAN`'s step after `capture.sheet` depends on `capture.crop`; coverage fails without it | 09 Tests; D-616 | `capture.test.ts:1527`, `:1544`, `:1574`; `mcp-server/tests/audit/coverage.test.ts:309`, `:321`, `:328` | ✅ |
| AC-136.19 | eval | `EVAL_RUN` under D-608 A, amended by D-621: `s64-E4-check.txt` cited as it stands (exit 1); every t3 and meta line passes; every real run passes its allowlist, media and answer lines; the real-t1 `image` line and the real-t2 sheet-count line fail and are evidence for `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`; `s64-E4-amended.txt` checks those are the only FAIL lines | Grouping D-505; D-608; D-621 | E-4 receipts (§Evidence, The description eval) | ✅ |
| AC-134 (cross-ref) | regression | MEU-134's ACs are owned by the MEU-134 handoff. Moved pins: AC-134.1's last `CaptureSource` members now read `members[-2] == "Video"` and `members[-3] == "Crop"` (`test_domain_capture.py:914-915`); AC-134.16's 74 → 75; AC-134.17's operation count 77 → 78 (`test_api_openapi.py:208`) | plan §Pins that move | [MEU-134 handoff](2026-11-10-video-probe-frames-MEU-134-handoff.md); gate `py-tests`, `mcp-tests` | ✅ |
| AC-135 (cross-ref) | regression | MEU-135's ACs are owned by the MEU-135 handoff. Moved pins: AC-135.20's operation count 77 → 78 (`test_api_openapi.py:253`); AC-135.19's 74 → 75, and its last-key pin now reads `BASELINE_PENDING.slice(-2)` equal to `avkit_capture.sheet`, `avkit_capture.export` (`coverage.test.ts:301`) | plan §Pins that move | [MEU-135 handoff](2026-11-11-capture-video-sheet-MEU-135-handoff.md); gate `mcp-tests` | ✅ |
| AC-130 (cross-ref) | regression | AC-130.7 (`Crop` then `Video`, `test_domain_capture.py:894`) passes unchanged. AC-130.26 (the crop row after revert) and AC-130.28 (the baseline misses only the pending keys) failed in row 2b on the 75 count and the pending list, and pass after row 3 | plan §Pins that move; D-616 | `capture.test.ts`, `coverage.test.ts`; gate `py-tests`, `mcp-tests` | ✅ |
| AC-38, AC-32 (cross-ref) | regression | AC-38.1, AC-38.2, AC-38.5 and AC-32.1 read `ACTION_INDEX_AFTER`, `CAPTURE_ACTIONS` and the shared markers; they failed in row 2b on the moved counts and pass after row 3, `export` carrying the marker words from `EXPORT_TEXT` | plan §Pins that move | `capture.test.ts`, `convert.test.ts`; gate `mcp-tests` | ✅ |
| AC-68, AC-67 (cross-ref) | regression | AC-68.5's `AUDIT_ACTION_SET` and AC-68.1/AC-68.4's built-server discovery count 75 actions. AC-67.19's order pin (`runner-fake-backend.test.ts:193-197`) was an adjacency pin, `capture_interactive` directly after `sheet`; it moved in row 2b to sheet after frames, export after sheet, and `capture_interactive` after export | plan §Pins that move; S62 RULE-4 | `coverage.test.ts`, `runner-fake-backend.test.ts:65`, `:80`, `:193-197`; gate `mcp-tests` | ✅ |
| AC-16, AC-42 (cross-ref) | regression | AC-16.6 walks the 78 `ROUTE_INDEX` rows (the export row at `test_api_openapi.py:61`), AC-16.9 sends `_valid_body`'s export body with an extra key, and AC-42.9 counts 78 operations and 75 actions (`test_api_downloads.py:377`) | plan §Pins that move | `test_api_openapi.py`, `test_api_bodies.py`, `test_api_downloads.py`; gate `py-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-136.2 to AC-136.16 (Python) | Row 2a: 111 failed, 148 passed against row 1's stubs (`s64-py-red-136.txt`). `assert False` ×59; `AssertionError: export raised NotImplementedError: CaptureAdapter.export is not built yet` ×50; `At index N diff: <class 'NotImplementedError'> != <class '…ValidationError'>` ×21; `… != <class '…CaptureFailedError'>` ×8; `AssertionError: export raised NotImplementedError: CaptureService.export_shot is not built yet` ×8; `assert 404 == 201` ×2 | Row 3: 722 passed (`s64-py-green-136.txt`); gate `py-tests` 2108 passed | `test_capture_export_adapter.py:258-672`, `test_capture_export_service.py:243-776`, `test_api_capture_export.py:135-282`, `test_api_openapi.py:298` |
| AC-136.1 | A characterisation of row 1: row 2a's guard passed 1 (`s64-r2a-guard.txt`) | Gate `py-tests` | `test_domain_capture.py:985` |
| AC-136.17, AC-136.18 (MCP) | Row 2b: Test Files 6 failed (6); Tests 27 failed, 145 passed (172) (`s64-mcp-red-136.txt`). `expected [ …(N) ] to have a length of N but got N` ×8; `expected { missing: [ …(4) ], extra: [] } to deeply equal { missing: [ …(5) ], extra: [] }` ×2; `expected 'validation_error: Invalid input' to be 'validation_error: export accepts only…'`; `expected [ 'avkit_download.add', …(N) ] to include 'avkit_capture.export'`; `CaptureExportIn in openapi.committed.json: expected undefined to be defined` | Row 3: 35 files, 520 passed (`s64-mcp-green-136.txt`); gate `mcp-tests` 520 passed | `capture.test.ts:1360-1574`, `coverage.test.ts:309-328` |

- **red-check.** Row 2a's receipt: 1 receipt, 15 required tests, 0 problems. Row 2b's: 1 receipt, 2 required tests, 0 problems. Every failing block is an assertion.
- **The failures in the Red runs that aren't AC-136 tests.**
  - Row 2a's other 6 failures are the moved Python pins: the route census and the export route row (AC-16.6), AC-134.17, AC-135.20, AC-42.9 and the export extra-field body (AC-16.9).
  - In row 2b, the 12 AC-136.17 and AC-136.18 tests fail, and the other 15 are moved MCP pins: AC-38.1, .2, .5, AC-32.1, AC-130.26, .28, AC-134.16, AC-135.19, the `ACTION_INDEX` census, both `M7_PER_ACTION` counts, both AC-68.5 tests, AC-68.1/.4 and AC-67.19. Each has a cross-ref row.
- **The passes in the Red runs.** Row 2a's 148 passes are the crop, sheet and frames tests in the same files, the moved pins' neighbours, and the cases that row 1's stubs already met. Row 2b's 145 passes are the MCP tests that don't read `export` or the counts.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-0-baseline", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-capture-export-copy/baseline.ps1 *> C:/Temp/av-kit/s64-baseline.txt (task.md row 0's Validation cell, run from P:/av-kit; base suites in C:/Temp/av-kit/s64-base-py.txt, s64-base-mcp.txt, s64-base-ruff.txt and s64-base-mcp-build.txt)", "scope": "Row 0: D-608 ruled (S14), the queue (S8), the shapes and absent names (S11), baseline.sha and baseline-dirty.txt, the anchors and line endings, the lock sync, the pinned FFmpeg pair and Pillow (S4), base suites and the red-check, identity and eval-check selftests", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d before any row", "output": "missing targets: [] new files already present: []; ui lock sync: 651 locked packages, 0 differ, 0 missing; mcp-server lock sync: 133 locked packages, 0 differ, 0 missing; base pytest 1999 passed, 32 warnings in 146.69s; base MCP Test Files 35 passed (35), Tests 508 passed (508); ruff All checks passed!; identity selftest: 0 failure(s); eval-check selftest: 0 wrong; baseline: all steps exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-1-types", "command": "$env:TMP='C:\\Temp\\av-kit\\s64\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_domain.py tests/unit/test_capture_service.py tests/unit/test_capture_adapter.py tests/e2e/test_api_captures.py tests/e2e/test_api_capture_crop.py tests/integration/test_api_wiring.py --tb=short -q -rfE *> C:/Temp/av-kit/s64-types-py.txt; rtk proxy uv run pyright packages/ *> C:/Temp/av-kit/s64-types-pyright.txt; rtk proxy uv run ruff check packages/ tests/ *> C:/Temp/av-kit/s64-types-ruff.txt (task.md row 1's Validation cell); AC-136.1 alone *> C:/Temp/av-kit/s64-r1-ac1.txt; the sheet and frames guards *> C:/Temp/av-kit/s64-r1-guards.txt; the caller grep *> C:/Temp/av-kit/s64-r1-callers.txt", "scope": "Row 1: the shared names as wrong stubs (CaptureSource.Export, ImageAnnotatePort.export, CaptureAdapter.export, the EXPORT_* constants, ExportResult, export_size, export_stem, export_shot, _crop_dest's ext), the CaptureSource pins, AC-136.1, and the caller, implementer and pin grep", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to 1", "output": "301 passed in 9.49s; pyright 0 errors; ruff All checks passed!; AC-136.1 file run 4 passed, 107 deselected; sheet and frames guards 102 passed in 6.55s; callers: _crop_dest is called only by crop_shot, with no ext; ImageAnnotatePort is implemented by CaptureAdapter and duck-typed test fakes"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-2a-red-136-py", "command": "$env:TMP='C:\\Temp\\av-kit\\s64\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_capture_export_adapter.py tests/unit/test_capture_export_service.py tests/e2e/test_api_capture_export.py tests/e2e/test_api_openapi.py tests/e2e/test_api_downloads.py tests/e2e/test_api_bodies.py --tb=short -q *> C:/Temp/av-kit/s64-py-red-136.txt; red-check.py with the 15 --require ids *> C:/Temp/av-kit/s64-py-red-136-check.txt; pytest tests/unit/test_domain_capture.py -k test_ac_136_1_ *> C:/Temp/av-kit/s64-r2a-guard.txt (task.md row 2a's Validation cell)", "scope": "MEU-136 Python Red: AC-136.2 to AC-136.16 against row 1's stubs, plus AC-136.1 as a passing guard and the moved Python pins", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to 2a", "output": "111 failed, 148 passed in 20.21s. Decisive: assert False x59; AssertionError: export raised NotImplementedError: CaptureAdapter.export is not built yet x50; At index N diff: NotImplementedError != ValidationError x21; != CaptureFailedError x8; CaptureService.export_shot is not built yet x8; assert 404 == 201 x2. red-check: 1 receipt(s), 15 required test(s), 0 problem(s). AC-136.1 guard: 1 passed, 110 deselected"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-2b-red-136-mcp", "command": "rtk proxy npm --prefix mcp-server run build *> C:/Temp/av-kit/s64-r2b-mcp-build.txt; rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts tests/convert.test.ts tests/action-index.test.ts tests/m7-resource.test.ts tests/audit/coverage.test.ts tests/audit/runner-fake-backend.test.ts *> C:/Temp/av-kit/s64-mcp-red-136.txt; red-check.py --require AC-136.17 --require AC-136.18 *> C:/Temp/av-kit/s64-mcp-red-136-check.txt (task.md row 2b's Validation cell)", "scope": "MEU-136 MCP Red: AC-136.17, AC-136.18 and the moved MCP pins, on a fresh build", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to 2b", "output": "tsc exit 0. Test Files 6 failed (6); Tests 27 failed | 145 passed (172). Decisive: expected [ ...(N) ] to have a length of N but got N x8; expected { missing: [ ...(4) ], extra: [] } to deeply equal { missing: [ ...(5) ], extra: [] } x2; expected 'validation_error: Invalid input' to be 'validation_error: export accepts only...'; expected [...] to include 'avkit_capture.export'; CaptureExportIn in openapi.committed.json: expected undefined to be defined. red-check: 1 receipt(s), 2 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-3-green-136", "command": "$env:TMP='C:\\Temp\\av-kit\\s64\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest (row 3's files: the MEU-136 tests, every CaptureService caller and capture guard, test_domain, test_domain_capture and test_api_wiring) --tb=short -q -rfE *> C:/Temp/av-kit/s64-py-green-136.txt; export_openapi.py --check *> C:/Temp/av-kit/s64-r3-openapi.txt; git diff -- openapi.committed.json *> C:/Temp/av-kit/s64-r3-openapi-diff.txt; pyright, ruff, MCP build, MCP test and typecheck *> C:/Temp/av-kit/s64-r3-*.txt and s64-mcp-green-136.txt; the caller sweep *> C:/Temp/av-kit/s64-r3-callers.txt; tests/integration/test_video_real_ffmpeg.py *> C:/Temp/av-kit/s64-r3-callers-ffmpeg.txt (task.md row 3's Validation cell)", "scope": "MEU-136 Green: EXPORT_SIZE, EXPORT_NAME, EXPORT_CHECKS, EXPORT_SOURCE, EXPORT_ENCODE, EXPORT_WRITE, EXPORT_ROUTE, EXPORT_MCP, EXPORT_AUDIT, NO_RAW_OUTPUT", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to 3", "output": "722 passed, 5 warnings in 59.12s; openapi --check exit 0; the OpenAPI delta is 155 added lines and 0 removed (CaptureExportIn, CaptureExportOut, CaptureExportShotOut and POST /api/v1/captures/{id}/export), CRLF kept (7704 CRLF, 7704 LF); pyright 0 errors, 0 warnings, 0 informations; ruff All checks passed!; MCP build exit 0; MCP Test Files 35 passed (35), Tests 520 passed (520); typecheck exit 0; real-FFmpeg callers 21 passed, 16 warnings in 8.57s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-E1-E3-eval-runs", "command": "eval-run.md steps 1 to 3, from P:/av-kit: eval-seed.py *> C:/Temp/av-kit/s64-E1-seed.txt; MCP build *> C:/Temp/av-kit/s64-E1-mcp-build.txt; eval-harness.ts describe > C:/Temp/av-kit/s64-E1-describe-utf8.txt 2>&1; per run eval-harness.ts seed *> C:/Temp/av-kit/s64-E2-<run>-seed.txt and the prompts check *> C:/Temp/av-kit/s64-E2-prompts.txt; six general-purpose subagents with model haiku, each given only C:/Temp/av-kit/s64-eval-<run>-prompt.md, reports in C:/Temp/av-kit/s64-eval-<run>-report.txt, checked *> C:/Temp/av-kit/s64-E3-reports.txt (task.md rows E-1 to E-3)", "scope": "EVAL_RUN under D-608 A: the media, the key, the real and meta surfaces, six runs", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to 3", "output": "eval-seed: ok; describe 724 lines, the CUT at :690, the export description below it (meta surface); seeds not ready: [] source ids missing: [] prompts not ready: []; reports missing or empty: []; ledgers hold 3, 4, 3, 5, 6 and 2 lines (real-t1 to meta-t3)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-E4-eval-check", "command": "rtk proxy uv run python docs/execution/plans/2026-11-11-capture-export-copy/eval-check.py *> C:/Temp/av-kit/s64-E4-check.txt; then, under D-621 A, the amended check *> C:/Temp/av-kit/s64-E4-amended.txt (task.md row E-4)", "scope": "AC-136.19: the six runs scored against the key; D-621 A's amended reading", "phase": "runtime", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to E-4", "output": "s64-E4-check.txt: exit 1, 43 PASS and 2 FAIL lines, eval-check: failed; FAIL real-t1: successful image calls: 0; FAIL real-t2: successful sheet calls on driveway.mp4: 1 (needs 2). s64-E4-amended.txt: PASS lines: 43 FAIL lines: 2; unexpected FAIL lines: []; expected FAIL lines missing: []; required PASS lines absent: []; e4-amended: ok"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the S3 check, the pre-status copies, the 09 Delivered note, MEU-136's fields byte-edited in meu-status.yaml (S15), the render, grouping row 64; then its Validation cell into C:/Temp/av-kit/s64-r6-render.txt and its status check into C:/Temp/av-kit/s64-r6-status.txt; the docstring fix's tests into C:/Temp/av-kit/s64-r6-docfix.txt", "scope": "Row 6: the D3 spec text, MEU-136 ready_for_review with this plan, the render, and grouping row 64 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD 2832e3d plus rows 0 to 6", "output": "Drift check passed - SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content. ready_for_review; grouping row 64 executed; spec note: True. Docstring fix: 101 passed in 8.32s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s64-gate-h1-2", "command": "$env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-11-capture-export-copy/session-gate.ps1 *> C:/Temp/av-kit/s64-gate-h1.txt; then Select-String for ' exit=', 'not_run', 'skipped', 'tested_state', '_sha256 ', 'outside scope', 'mismatch', 'session-gate:' and exit $code (task.md row H1-2's Validation cell, run from P:/av-kit; per-step receipts C:/Temp/av-kit/s64-D6-*.txt; run 2, copied to C:/Temp/av-kit/s64-gate-h1-run2.txt)", "scope": "H1-2: the registered D6 gate on the whole tree", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "2832e3d3eb61960c9359a4aabab2c6bea3ad71b0+b6332ad6e1c5d8f16c179337ff2fd5d709c98d8b926a08283ba135e977312b5b", "output": "baseline failures excused: py [], mcp []; ui-types, ui-lint, ui-tests, ui-build, ui-electron, mcp-audit, build-record, package-build and real-ffmpeg skipped with reasons; identity-before exit=0; py-types exit=0 (0 errors, 0 warnings, 0 informations); py-lint exit=0 (All checks passed!); task-contract exit=0 (27 rows, 25 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 44, outside scope: [], head moved (S3): False, baseline-dirty paths changed since row 0: []); red-check-selftest exit=0 (44 fixtures, 13 positive, 31 negative, 0 wrong); py-tests exit=0 (2108 passed, 37 warnings in 184.70s); openapi exit=0; mcp-types exit=0; mcp-build exit=0; mcp-tests exit=0 (Test Files 35 passed (35), Tests 520 passed (520)); state-render exit=0 (142 MEUs, 12 phases); issues-render exit=0 (known-issues.md is up-to-date); status-canon exit=0 (Test Files 2 passed (2), Tests 14 passed (14)); identity-after exit=0 (tested_state before = after); session-gate: all steps exit 0"}
```

### Quality Gate Results

`s64-gate-h1-2` (H1-2) is the fresh full record. Its last line is:

> session-gate: all steps exit 0

- **Two runs.** Run 1 (`s64-gate-h1-run1.txt`) stopped at `task-contract`, exit 1 (`s64-D6-task-contract-run1.txt`). Its first refusal reads `task.md:56 row 0 has Status '[x]` `…`: each Status cell held the row's evidence note after `[x]`, and the lint takes only the bare status. The notes moved out of the cells into a row-notes file outside the repository, which this handoff's §Evidence and §Deferred Items carry. Run 2 (`s64-gate-h1.txt`, the same bytes as `s64-gate-h1-run2.txt`) passed every step. `task.md` is a project artifact, so the move doesn't change the tested_state. Both runs' receipts are kept.
- **Static checks.**
  - pyright: 0 errors, 0 warnings, 0 informations. ruff check: all checks passed.
  - lint_task_contract passed on 27 rows (25 fully checked; H1-5 and H2-1 are exempt as `view_file`).
  - scope-paths found 44 changed paths, none outside scope. HEAD `2832e3d` did not move, and no path in `baseline-dirty.txt` changed since row 0 (S3). Before the gate, the tree's changed paths were listed against the gate's scope paths (Session 60 RULE-4).
  - The red-check selftest read 44 fixtures (13 positive, 31 negative), with 0 wrong.
- **Suites.**
  - pytest: 2108 passed (the baseline's 1999 plus 109 new cases).
  - MCP: 520 passed in 35 files (the baseline's 508 plus 12).
  - status-canon: 14 passed.
- **Build and state.**
  - `export_openapi.py --check`, the MCP typecheck and the MCP build exited 0.
  - The state render and the issue render match the files on disk.
  - H1-3's `render --check` (`drift-check.txt`) and H1-4's `export_openapi.py --check` (`openapi-check.txt`) passed after the gate, both exit 0.
- **Skipped.** Each skip has a reason in the gate:
  - the UI steps: no `ui/` file changed (D-617), and status-canon runs the only UI tests that read a file this session writes;
  - `mcp-audit`: it needs the live network, which the brief forbids, and AC-136.18 covers `AUDIT_PLAN`'s new step offline;
  - `build-record`: no installer build;
  - `package-build`: no packaged surface change;
  - `real-ffmpeg`: export encodes with Pillow (D-614), and `py-tests` still runs `test_video_real_ffmpeg.py`.
- **Identity.**
  - The tested_state was the same before and after: `2832e3d3eb61960c9359a4aabab2c6bea3ad71b0+b6332ad6e1c5d8f16c179337ff2fd5d709c98d8b926a08283ba135e977312b5b`.
  - The closeout records, this plan's `*.md` and `task.md` are left out of the identity, so writing them doesn't change it.
- **Warnings.** The gate's `py-tests` has 37 warnings, and every one is Pillow's `getdata` deprecation from a test helper, none from product code:
  - 16 from `test_capture_sheet_adapter.py:89`;
  - 16 from `test_video_real_ffmpeg.py`, through that sheet helper;
  - 2 from `test_ac_136_4_depth_map_formula` (`test_capture_export_adapter.py:363`, `:373`);
  - 3 from `test_ac_136_4_sixteen_bit_rgb_key_is_dropped` (`:558`).

### The row 3 OpenAPI diff

`export_openapi.py` regenerated `openapi.committed.json`, and CRLF was kept (7704 CRLF line ends, no bare LF). Against `2832e3d`, the delta (`s64-r3-openapi-diff.txt`, 155 added lines and no removed line) adds:
- the path `/api/v1/captures/{id}/export`;
- the schemas `CaptureExportIn`, `CaptureExportOut` and `CaptureExportShotOut`.

It changes no path or schema, and it removes nothing. `CaptureSource.Export` doesn't reach the snapshot, because the shot's `source` field is a plain string (D-618).

### The description eval (D-608 A, D-621 A; AC-136.19)

Six fresh `general-purpose` subagents with `model: haiku` ran in parallel, each given only its prompt. The `real-*` runs saw the surface that Claude Code gives a model: the server instructions, each tool's description and its flattened input schema. The `meta-*` runs saw that surface plus each action's `_meta` text. The per-run lines of `s64-E4-check.txt`:

| Run | Answer | Process lines | t3 file |
|---|---|---|---|
| real-t1 | slide `Velvet Margins 38`, right | 2 frames or sheet calls on `meeting.mp4`; **FAIL** 0 image calls | — |
| real-t2 | arrival 3953 s against the key's 3954 s, within 5 s | **FAIL** 1 sheet call on `driveway.mp4` (needs 2) | — |
| real-t3 | new shot `bfe614ec-1727-4c26-8271-852aa3c4dd5b` | 2 export calls; the last is `jpeg`; `source_id` is the seeded shot's | `dashboard-4k-export_2.jpg`, 444076 bytes, decodes as JPEG at (1920, 1080) |
| meta-t1 | slide `Velvet Margins 38`, right | 2 frames or sheet calls; 1 image call | — |
| meta-t2 | arrival 3954 s, right | 3 sheet calls (needs 2) | — |
| meta-t3 | new shot `0978c1f1-3a9c-42c7-9b2c-460f6b6bd130` | 1 export call; `jpeg`; `source_id` is the seeded shot's | `dashboard-4k-export.jpg`, 288052 bytes, decodes as JPEG at (1280, 720) |

- Every run called nothing outside the allowlist and left every media file unchanged. Each t3 run left `dashboard-4k.png` byte for byte.
- **The two FAIL lines** are on the real surface only, and the same tasks pass on the meta surface. As D-608 A reads that outcome, they are evidence for `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`, not for a wrong text. real-t1 read the slide from the PNG that `frames` wrote, without the `image` call, and real-t2 found the arrival with one sheet and then frames. No description text and no line of `eval-check.py` changed (D-621).
- **Inbox PNGs read by path.** Four video runs (real-t1, real-t2, meta-t1 and meta-t2) opened the inbox PNGs that frames and sheet returned, by path, with their own file reader. The prompts allowed it, and the checker can't see it.
- **What the runs said was unclear.** These are raised, not fixed:
  - real-t1: how a video gets into the catalog, and that the `at` values are seconds.
  - real-t2: the time unit of `start`, `end` and `at`, and that `frames` returns paths the caller has to open.
  - real-t3: `export` is only an enum value on the real surface, with no text of its own.
  - meta-t1: `avkit_convert` probe refused `paths` and took `path`; the sheet's labels cover the slide titles, so a frames still was needed.
  - meta-t2: probe's field isn't named. It also says `"00:01:04.000"` was "silently read as 64 seconds". That note misreads: 1:04 is 64 s.
  - meta-t3: the flattened `max_edge` schema is an `anyOf` of 64 to 2576 and 64 to 16383, with no note on which range applies to which action.
  - real-t2, real-t3 and meta-t3 report the export or sheet as they worked. No run reported the `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` failure.

### Caller and pin grep (S55 RULE-1, S59 RULE-1, Session 61 RULE-3, Session 62 RULE-4, Session 63 RULE-1)

- **`_crop_dest`** is called only by `crop_shot` (`services/capture.py:1637`), which passes no `ext`, and by `export_shot` (`:1739`). AC-136.3 checks that crop still gets `.png`, and crop's tests pass in the gate.
- **Implementers.** `ImageAnnotatePort` is implemented by `CaptureAdapter` and used by `CaptureService` and duck-typed test fakes. The signature-equality tests are in `test_domain_capture.py` (AC-134.1, AC-135.1, AC-136.1).
- **`CaptureSource` walkers.** `test_domain.py`'s `ENUM_MEMBERS`, `test_api_captures.py`'s `SOURCE_OUT`, `test_domain_capture.py`'s AC-134.1 last-member pin, and `CAPTURE_SOURCE_MEMBERS` (`test_domain_capture.py:18`), which the plan didn't list (Departure 7).
- **Count, order and adjacency pins.** Every hit of the sweep in rows 2a and 2b is in §Pins that move or named here: `runner-fake-backend.test.ts:193` (an adjacency pin, AC-67.19) and AC-135.19's last-key pin (Departures 8 and 9). Row 3 hit no new pin.
- **Absence pins.** The plan-time grep for `export`, `Export`, `capture.export` and the new names in `tests/`, `mcp-server/tests/` and `ui/tests/` found no test asserting an export name is absent, and row 2a read it again.
- **The real-FFmpeg callers.** `tests/integration/test_video_real_ffmpeg.py` uses `CaptureService`'s frames and sheet. It isn't in row 3's file list, so it ran on its own: 21 passed (`s64-r3-callers-ffmpeg.txt`).

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modified | `CaptureSource.Export` |
| `packages/core/src/avkit_core/ports/capture.py` | modified | `ImageAnnotatePort.export` |
| `packages/core/src/avkit_core/services/capture.py` | modified | The `EXPORT_*` constants, `ExportResult`, `export_size`, `export_stem`, `export_shot`, `_crop_dest`'s `ext` |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `CaptureAdapter.export`, `EXPORT_DEPTH_MODES`, `_png_key`, `_depth_to_l` |
| `packages/api/src/avkit_api/routes/captures.py`, `schemas/captures.py` | modified | `EXPORT_ROUTE` |
| `openapi.committed.json` | regenerated | The export route and its three schemas |
| `mcp-server/src/toolsets/capture.ts`, `registry.ts` | modified | `EXPORT_MCP`, `EXPORT_TEXT`, `EXPORT_UNKNOWN_KEY`, the `ACTION_INDEX` row and `ADD_TIMEOUT_MS` |
| `mcp-server/scripts/audit/plan.ts` | modified | The offline `capture.export` step; `crop_id` set by the crop step |
| `tests/unit/test_capture_export_adapter.py`, `test_capture_export_service.py` | new | AC-136.2 to .12. LF |
| `tests/e2e/test_api_capture_export.py` | new | AC-136.13 to .15. LF |
| `tests/unit/test_domain_capture.py`, `test_domain.py`, `tests/e2e/test_api_captures.py` | modified | AC-136.1; the `CaptureSource` pins |
| `tests/e2e/test_api_openapi.py`, `test_api_downloads.py`, `test_api_bodies.py` | modified | AC-136.16; the counts 77 → 78 and 74 → 75; `ROUTE_INDEX`; the export valid body |
| `mcp-server/tests/capture.test.ts`, `convert.test.ts`, `action-index.test.ts`, `m7-resource.test.ts`, `fixtures.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | modified | AC-136.17, .18; the counts 74 → 75, capture 13 → 14; `CAPTURE_ACTIONS`; `BASELINE_PENDING`; the AC-67.19 adjacency pin; the AC-135.19 last-key pin |
| `docs/build-plan/09-screenshot-capture.md` | modified | The Delivered note (`:1201`) |
| `.agent/context/meu-status.yaml`, `.agent/context/meu-registry.md`, `docs/BUILD_PLAN.md`, the grouping file | modified | Only MEU-136's fields and rows, and grouping row 64 (row 6) |
| `.agent/context/current-focus.md` | modified | Session 64's priority line (a project artifact) |

`git diff --stat` on the tracked files: 29 files changed, 1073 insertions(+), 43 deletions(-). The three new test files hold 698, 793 and 339 lines.

Line endings were measured with Python bytes before each edit and kept:
- These files stayed CRLF: `enums.py`, `ports/capture.py`, `services/capture.py`, `capture/adapter.py`, `routes/captures.py`, `schemas/captures.py`, `openapi.committed.json`, `capture.ts`, `registry.ts`, `plan.ts`, the MCP test files, `test_domain_capture.py`, `test_domain.py`, `test_api_captures.py`, `test_api_openapi.py`, `test_api_downloads.py`, 09, the grouping and `current-focus.md`.
- `test_api_bodies.py`, `meu-status.yaml`, `meu-registry.md` and `BUILD_PLAN.md` stayed LF.
- New files are LF.

```diff
 # ports/capture.py
+    def export(
+        self,
+        source: Path,
+        source_size: tuple[int, int],
+        out: Path,
+        *,
+        fmt: str,
+        size: tuple[int, int],
+        quality: int | None,
+    ) -> ImageProbe:
 # services/capture.py
-    def _crop_dest(uow: UnitOfWork, inbox: Path, stem: str) -> Path:
+    def _crop_dest(
+        uow: UnitOfWork, inbox: Path, stem: str, *, ext: str = FLATTEN_PNG_SUFFIX
+    ) -> Path:
 # routes/captures.py
+@router.post("/{id}/export", status_code=201, response_model=CaptureExportOut)
 # registry.ts
+  { tool: "avkit_capture", action: "export", method: "POST", path: "/captures/{id}/export" },
 # runner-fake-backend.test.ts:193-197 (AC-67.19)
-    // MEU-135 (Session 63): capture.sheet sits between frames and capture_interactive.
-    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.sheet") + 1);
+    // MEU-135 (Session 63): capture.sheet sits right after frames.
+    expect(ids.indexOf("capture.sheet")).toBe(ids.indexOf("capture.frames") + 1);
+    // MEU-136 (Session 64): capture.export sits between sheet and capture_interactive.
+    expect(ids.indexOf("capture.export")).toBe(ids.indexOf("capture.sheet") + 1);
+    expect(ids.indexOf("capture.capture_interactive")).toBe(ids.indexOf("capture.export") + 1);
```

The excerpt is abridged. The source is `ports/capture.py:76`, `services/capture.py:1785`, `routes/captures.py:500`, `registry.ts:137` and `runner-fake-backend.test.ts:193-197`.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

Codex reviews the execution in one rolling report, `2026-11-11-capture-export-copy-implementation-critical-review.md`, on the ledger loop `s64-execution-2026-11-11-capture-export-copy`.

| Round | Verdict | Findings | Tested state |
|-------|---------|----------|--------------|
| 1 | approved | 0 findings; blocking 0; intent achieved yes; 9,796,997 tokens of 60,000,000 (`C:/Temp/av-kit/dispatch/s64-exec-run-r1.txt`) | `2832e3d3eb61960c9359a4aabab2c6bea3ad71b0+b6332ad6e1c5d8f16c179337ff2fd5d709c98d8b926a08283ba135e977312b5b` |

### Verdict

Approved by Codex in round 1 of 6 with 0 findings. H1-7a (`C:/Temp/av-kit/review-state-check.txt`) reads `verdict=approved; open findings=0`, and H1-7b (`C:/Temp/av-kit/exec-review.txt`) reads `OK: approved at round 1 of 6, 0 open blocking findings`. MEU-136 moves to `approved` in H2-2.

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| `avkit_capture.export` in `BASELINE_PENDING` | known issue | The next authoritative baseline update | D-616; `MCP-AUDIT-BASELINE-PENDING-CROP`; `--update-baseline` needs Mat's words |
| Per-action text hidden from models | known issue | `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL`'s own session | D-608 A measured it; D-621 records the two real-surface lines as its evidence |
| `CAPTURE-EXIF-SCANNED-ORIENTATION` | known issue | Its own session | D-613; AC-136.7 records export's behaviour; not fixed |
| `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` | known issue | Its own session | Not observed; export doesn't scan |
| 16-bit gray clipped by `_encode_view` (the `image` view) and `bake` | bug, raised for Mat | None | Plan §Out of Scope; both convert `I;16` straight to 8 bits; export maps the depth itself (D-619) |
| An unknown key named in the refusal of the other strict MCP actions | MCP, raised for Mat | None | Plan §Out of Scope; D-620 fixes export only; the others answer the calling client and log nothing. AC-136.17's positive control shows crop's echo |
| A PNG transparency key Pillow misreads (2- and 4-bit gray, 16-bit RGB) in crop and the resized `image` view | bug, raised for Mat | None | Plan §Out of Scope; crop writes the unscaled key into an 8-bit PNG and the view resizes with it. Export corrects it with `_png_key` (D-614) |
| The eval runs' unclear points | MCP text | None | §Evidence, The description eval; no text changes without Mat's words |
| Download reliability | feature | MEU-137 to MEU-142, Sessions 65 on | Their own grouping |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2) |

**Execution notes.**
- **One source for the bounds.** `schemas/captures.py` imports `EXPORT_MAX_EDGE_MAX` and `REGION_MAX_EDGE_MIN` for `CaptureExportIn`, so REST and the service share one cap.
- **`EXPORT_UNKNOWN_KEY` is exported** from `capture.ts` so AC-136.17 compares the refusal with the constant itself.
- **The describe receipt.** The PowerShell `*>` describe receipt began with an `[rtk]` banner and carried cp437 mojibake, so the eval surfaces come from the same describe run through the Bash `> f 2>&1` form that `eval-run.md` step 3 gives (`s64-E1-describe-utf8.txt`, 724 lines, CUT at `:690`). Its lines equal the first receipt's once the banner is dropped and the cp437 decoding undone (Departure 3).
- **The status write.** `meu_status.py update` re-wraps other MEUs' YAML, so its output was discarded, the pre-row copy restored, and only MEU-136's five fields byte-edited (S15, Session 61 RULE-5). `render --check` passes.

### Departures and their basis

1. **The size property test (row 3, a test file edit in Green).** `test_ac_136_2_export_size_properties` held a strict orientation clause that the approved half-up rule contradicts: 127×128 at 64 is 63.5, so 64×64, which the exhaustive `Fraction` check requires. Its clauses now read "a square stays square" and "no edge order flips". The AC text and `EXPORT_SIZE` are unchanged. Disclosed for review under Session 59 RULE-1.
2. **The crop audit step sets `crop_id` (`plan.ts:1622`).** The `capture.export` step needs the crop's new shot id, and the crop step held it only in the ledger. The step now also sets the state key, as other steps do. The plan's `EXPORT_AUDIT` says "the crop step's shot id" and names no mechanism.
3. **The describe receipt** (Execution notes above). The surfaces are unchanged; only the receipt form differs.
4. **The eval reports.** The harness's subagent transcript files were empty (0 lines), so each report is the subagent's final message, saved byte for byte from its completion notification, LF.
5. **The status YAML byte edit** (Execution notes above).
6. **The docstring ids.** `export_size`'s and `export_stem`'s docstrings cited D-612 and D-615 wrongly. They now cite `EXPORT_SIZE (MEU-136)` and `EXPORT_NAME (MEU-136, D-612)`. 101 tests passed after the fix (`s64-r6-docfix.txt`). The first row 6 script had a broken `TMP` line; it was rerun with the line fixed, and both runs exit 0.
7. **A fourth `CaptureSource` pin.** `CAPTURE_SOURCE_MEMBERS` (`test_domain_capture.py:18`) gained `"Export"` in row 1, with the three pins the plan listed.
8. **The fixtures' form.** `fixtures.ts` has no crop rows, so the export rows follow sheet's form, not the crop form the plan named.
9. **Two pins the plan didn't list, moved in row 2b.** The AC-67.19 adjacency pin (`runner-fake-backend.test.ts:193`) and AC-135.19's last-key pin (`coverage.test.ts:301`, now `slice(-2)`). Both are in §Evidence and the cross-ref rows. No execution decision was needed, because S9 names the action.
10. **Gate run 1** stopped on the notes in task.md's Status cells (§Quality Gate Results).

---

## Decision Log

```yaml
decision_log:
  - id: D-621
    stage: execution
    question: "Row E-4 eval-check exits 1 (S13): real-t1 makes no image call and real-t2 one sheet call where two are needed, while all six answers are right. What does AC-136.19 accept?"
    resolution: human
    class: two-way
    chosen: "A: amend AC-136.19 to cite the exit-1 receipt as it stands; every t3 and every meta line passes, every real run passes its allowlist, media and answer lines, and the two real-surface process lines are recorded as evidence for MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL; eval-check.py and the description text are unchanged"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s64-E4-check.txt — 43 PASS and 2 FAIL lines, eval-check: failed, exit 1"
      - "D-608 A in User Review Required — a task that fails on real and passes on meta is evidence for the open known issue, not for a wrong text"
      - "eval-check.py:387 — the checker prints eval-check: ok, so the former AC text eval-check: all runs PASS could not be met as written"
      - "an independent Opus subagent read at xhigh, consulted at Mat's request, recommended this option and the AC wording"
    research:
      engine: none
      sources: []
    reasoning: "B reruns only the two failures until they pass, one run per cell, and nothing that caused them changes. C changes description text and reaches into a known issue this plan leaves out of scope. D, the status quo, blocks MEU-136 on the frames and sheet surface of MEU-133 to MEU-135 although export (t3) passed every check on both surfaces. A keeps the failure on record where D-608 A said it belongs, and records that four video runs opened inbox PNGs by returned path, which the prompts allowed. Two-way: the eval rows can be re-run once the known issue is fixed."
    human_message_reference: "USER_EXPLICIT 2026-11-11 'A'"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-11 | claude-code-local (Claude Opus 5.5) | Initial MEU-136 handoff after the H1-2 gate |
| Reviewed | 2026-11-11 | codex-independent-reviewer | Execution review round 1 approved, 0 findings |
