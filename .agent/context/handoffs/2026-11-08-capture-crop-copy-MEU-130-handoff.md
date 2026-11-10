---
date: "2026-11-09"
project: "capture-crop-copy"
meu: "MEU-130"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-11-08-capture-crop-copy/implementation-plan.md"
build_plan_section: "bp09"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "codex (H1-7 execution review)"
predecessor: "2026-11-08-capture-region-import-MEU-129-handoff.md"
---

# Handoff: 2026-11-08-capture-crop-copy-MEU-130-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-130 `capture-crop-copy`. `POST /captures/{id}/crop` and the MCP `avkit_capture` `crop` action cut a region of any capture into a new PNG shot with source `Crop`. The source's saved marks are carried over and clipped to the region, and the source is never changed.
**Build Plan Section**: [09 §Crop to a new shot](../../../docs/build-plan/09-screenshot-capture.md) (anchor `crop-to-new-shot`; the Source, Marks and Tests rows at `:1046`, `:1047` and `:1049`, and the Delivered note at `:1051`), 09 `:282` and the MCP table's `crop` row (`:586`), [00 §Enums](../../../docs/build-plan/00-overview.md) (`:68`), and [05 §avkit_capture](../../../docs/build-plan/05-mcp-server.md) (`:228`, `:234-238`, `:310`, and the Delivered note at `:348`).
**Predecessor**: [MEU-129 handoff](2026-11-08-capture-region-import-MEU-129-handoff.md). This session calls Session 58's `resolve_region`, `import_stem` limits and `CAPTURE_FILE_LOCK`.

- **Domain (rows 1 and 3; D-484 to D-488, D-495).** `CaptureSource.Crop` is the last member (`enums.py:221`, `CROP_SOURCE`), reported as `Crop` with no register wire value (D-484). `clip_mark` (`domain/capture.py:424`) has one `case` per `Annotation` member (`:412`) and `assert_never` after the last, and returns the mark moved by `(-x, -y)` with `"kept"`, `"clipped"` or `"dropped"` (`MARK_CARRY`). Highlight, pixelate and eraser marks are clipped half-open (`_clip_half_open`, `:455`); a rect is clipped on its inclusive outline (`_clip_rect`, `:474`, D-486), so its right and bottom clip to `width - 1` and `height - 1` (`MARK_CLIP_BOX`). An arrow is clipped with Liang–Barsky (`_clip_arrow`, `:503`) in exact fractions, its new ends rounded half up (`_round_half_up`, `:499`) and clamped, so an exact half rounds up from either direction (round 1 F2), and dropped when it rounds to zero length; it never reverses (`MARK_CLIP_ARROW`, D-487). A text mark is kept by its anchor (`_clip_text`, `:489`, `MARK_CLIP_TEXT`, D-488).
- **Adapter (row 5; D-481, D-482).** `CaptureAdapter.crop` (`adapter.py:395`, port `ports/capture.py:47`) opens and decodes the original under one `except Exception` that raises `InboxPathError("the image could not be opened")`, refuses a file whose size differs from the row with a path-free `ConflictError`, and writes the box with no resampling into a PNG (`CROP_PIXELS`). It keeps a mode PNG stores (`_CROP_KEPT_MODES`, `:73`) and the ICC profile, and drops EXIF, XMP and text (`:70-74`). A CMYK, YCbCr or LAB source (`_CROP_ICC_CONVERT_MODES`, `:74`) converts through its profile to sRGB in `_to_srgb` (`:256`) and carries the sRGB profile; with no profile, or one that builds no transform, it converts plainly to RGB and carries none (D-506, round 1 F1).
- **Service (row 5; D-476, D-481, D-483, D-489, D-490).** `CaptureService.crop_shot` (`services/capture.py:887`) reads the row and the source's sidecar through `_saved_marks` (`:990`) without changing either (`CROP_READ`), resolves the box through Session 58's `resolve_region` (`CROP_REQUEST`), and under one `CAPTURE_FILE_LOCK` hold (`:97`):
  - picks the name with `_crop_dest` (`:1002`): `crop_default_stem` (`:146`) or `crop_name_stem` (`:127`), unique against inbox files, temporary files and rows, case-folded (`CROP_NAME`);
  - creates `<name>.avkit-tmp` with `open("xb")`, has the adapter write into it, and `os.replace`s it into place;
  - clips each saved mark, writes the crop's sidecar and bake (`CROP_BAKE`), probes and inserts the row.

  Any failure after the refusals removes only what the call wrote (`_discard`, `:1028`) and raises `CaptureFailedError`, a 503 `internal_error` (`CROP_CLEANUP`). The refusals in `CROP_REFUSALS` (`:118`) pass unchanged.
- **Route (row 5).** `crop_capture` (`routes/captures.py:397`) takes `CaptureCropIn` (`schemas/captures.py:206`, `extra="forbid"`) and answers 201 `CaptureCropOut` with `item`, `source_id`, `requested`, `applied`, `clamped` and `marks` (`CROP_RESPONSE`).
- **MCP (row 5; D-492, D-494).** `avkit_capture` gains a `.strict()` `crop` member (`capture.ts:243`) and `CROP_TEXT` (`:51`, `:68`). `ACTION_INDEX` gains the `crop` row after `revert` (`registry.ts:133`), and the `ADD_TIMEOUT_MS` branch takes `crop` (`:390`) (`CROP_MCP`). The audit plan gains a `capture.crop` step after `capture.revert` (`plan.ts:1578`).
- **Baseline (row 4b and row 6; D-499 A).** `coverage.test.ts:18` holds `BASELINE_PENDING = ["avkit_capture.crop"]`, and AC-68.5's committed-baseline clause (`:92`) accepts exactly that missing key. Row 6 filed `MCP-AUDIT-BASELINE-PENDING-CROP` (open, P3).
- **Parity fixture (row 5; D-493).** `tools/capture_bake_fixture.py` gains `crop_cases()`, four cases built through the real `clip_mark`, and the region fixture was regenerated.
- **Spec text and records (row 6).** The D3 notes above. MEU-130 is `ready_for_review` with this plan, and grouping row 59 is `executed`.

**Execution authorization:** `USER_EXPLICIT`, 2026-11-09. The session prompt opens "Start Session 59: `capture-crop-copy`, MEU-130 `capture-crop-copy`, P2 band." (`C:/Temp/av-kit/session-59-prompt.md:1`), after the Codex plan review approved in round 3 ([plan-critical-review.md](2026-11-08-capture-crop-copy-plan-critical-review.md) `:396`) (`plan_to_exec_gate: human`). At row 0 Mat set the execution loop's budget at 60M tokens ("60M"). **D-499:** Mat ruled "D-499 A" ([human-gate-decision.md](../../../docs/execution/plans/2026-11-08-capture-crop-copy/human-gate-decision.md) `:7`).

### Where values go (D-496, `NO_RAW_CONSOLE`)

- **The box and the counts** are numbers. They go into the response and are never logged.
- **A `name`** becomes the crop's file name and `display_name` only through `crop_name_stem`, which keeps letters, digits, space, dot, underscore and hyphen. No refusal repeats it: each is a fixed message (`CROP_NAME_LENGTH`, `CROP_NAME_UNUSABLE`, `CROP_NAME_ANNOTATED`, `services/capture.py:105-109`).
- **The source's stem** is already an inbox file name; it is reused only as `{stem}-crop`, cut to 100 characters.
- **Saved marks** are copied from the source's sidecar into the crop's. A text mark's `text` goes only into the sidecar and bake.
- **`capture.registered`** logs `shot_id` and `source.name` (`services/capture.py:1288`; the plan cited `:894`). Neither is a path.
- **`capture.wrote`** (`adapter.py:550`, `:567`; the plan cited `:366`) logs `path`, which isn't in `CONSOLE_FIELDS` (`services/health.py:47-56`), so the processor drops it once a HealthService is built.
- **A 503** is answered as `internal_error` with a fixed detail and isn't logged. A 4xx carries only its fixed message. No log line was added.
- **AC-130.22** proves the list through `build_services` with HealthService built first and the D-391 reset, and with a marker in every folder name: no `capfd` stdout or stderr line, ring message, `console.log` line or error message holds the marker. The controls show each surface was read (receipt `s59-py-green-crop`, and the gate's `py-tests`).

### Documented limits

- **The bake differences (D-486).** The crop's bake is close to a pixel crop of the source's bake, not identical: a rect cut on any side gets a stroke along the crop edge; a pixelate cut on its left or top re-aligns its block grid, and one cut on its right or bottom averages its partial blocks over the pixels inside; an eraser cut by the crop samples its fill from the ring inside the crop; a clipped arrow draws its head at the crop edge; a text mark whose anchor is outside is dropped even when its glyphs reach inside. AC-130.18 asserts each.
- **The stored frame.** A crop reads the stored frame, as `image` and `annotate` do. A scanned JPEG with EXIF orientation 5 to 8 is cropped sideways (`CAPTURE-EXIF-SCANNED-ORIENTATION`, Session 58), and the crop, a PNG with no EXIF, is upright as stored.
- **Unsaved marks.** Only saved marks travel. Marks in an open editor that weren't saved aren't on disk.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-130.1 | unit | `MARK_CLIP_BOX` inside, over rect, highlight, pixelate and eraser: kept, moved by `(-100, -50)`, every other field equal | Local Canon: 09 `:1047`; D-486 | `tests/unit/test_domain_capture.py:727` | ✅ |
| AC-130.2 | unit | `MARK_CLIP_BOX` partial over the four kinds, four sides and a corner; the rect clips to `width - 1` and `height - 1`; wholly outside dropped; zero-width and zero-height cases | Local Canon: 09 `:1047`; D-486 | `tests/unit/test_domain_capture.py:741` | ✅ |
| AC-130.3 | unit | `MARK_CLIP_ARROW`, the eleven probe cases: kept, clipped to the Liang–Barsky ends rounded half up, or dropped; a clipped arrow never reverses, each end within 0.5; an exact half rounds up in both directions (round 1 F2) | Research-backed: design D-7; D-487 | `tests/unit/test_domain_capture.py:767`, `:803` | ✅ |
| AC-130.4 | unit | `MARK_CLIP_TEXT`: the anchor at each inner corner kept and moved; at `x = width` or `y = -1` dropped | Local Canon: 09 `:1047`; D-488 | `tests/unit/test_domain_capture.py:829` | ✅ |
| AC-130.5 | unit | `MARK_CARRY` over 500 seeded marks: counts sum to the input, each returned mark is a fixed point of `_clamp_annotation`, no input mutated | Local Canon: D-485 | `tests/unit/test_capture_service.py:1190` | ✅ |
| AC-130.6 | unit | Every member of `typing.get_args(Annotation)` has a case: kept and moved by `(-5, -5)` | Local Canon: grouping D-406; D-485 | `tests/unit/test_domain_capture.py:854` | ✅ |
| AC-130.7 | unit | `"Crop" in CaptureSource.__members__` and it is last, asserted before `.value == "Crop"` is read | Local Canon: 09 `:1046`; D-484 | `tests/unit/test_domain_capture.py:886` | ✅ |
| AC-130.8 | unit | `CROP_PIXELS`: the crop of a 64×48 PNG decodes exactly to `image.crop((10, 8, 30, 24))` | Local Canon: AC-40.26 | `tests/unit/test_capture_adapter.py:1493` | ✅ |
| AC-130.9 | unit | Modes `1`, `L`, `LA`, `P` with transparency, `RGB`, `RGBA`, `I;16` kept; a `.jpg` gives RGB; a `.webp` with alpha gives RGBA | Local Canon: D-482 | `tests/unit/test_capture_adapter.py:1521` | ✅ |
| AC-130.10 | unit | ICC kept; EXIF and the `Comment` text dropped. Amended by D-506: a profiled CMYK JPEG gives an RGB crop of the profile's conversion to sRGB, carrying sRGB's profile; with no profile, or junk bytes, the plain RGB conversion and no profile | Local Canon: D-482; Human-approved: D-506 | `tests/unit/test_capture_adapter.py:1549`, `:1657`, `:1691` | ✅ |
| AC-130.11 | unit | A size mismatch raises a path-free `ConflictError` and writes nothing; a text `.png` raises `the image could not be opened` | Local Canon: D-481 | `tests/unit/test_capture_adapter.py:1716` | ✅ |
| AC-130.12 | e2e | `CROP_RESPONSE`, `CROP_SOURCE`: 201 with `Crop`, `source_id`, `requested`, `applied`, `clamped` false, marks 0; the source's bytes, `st_mtime_ns`, sidecar and row unchanged; both shots listed once | Local Canon: 09 | `tests/e2e/test_api_capture_crop.py:198` | ✅ |
| AC-130.13 | e2e | D-401 parity over five boxes: `applied` equals `X-Capture-Region`; the pixels equal `GET image` at scale 1, or the source's pixels where the view scales | Local Canon: grouping D-401 | `tests/e2e/test_api_capture_crop.py:244` (5 cases) | ✅ |
| AC-130.14 | e2e | A box past the right, the bottom, a corner, and a fraction box: `clamped` true, `applied` inside, no black pixel | Local Canon: 09 | `tests/e2e/test_api_capture_crop.py:285` | ✅ |
| AC-130.15 | e2e | `CROP_NAME`: `-crop`, `_2`, `_3` past a sidecar and a temporary file, the sanitized `name`, `crop_CON`, the three 422s, the 240-character stem cut to 100 | Local Canon: D-483 | `tests/e2e/test_api_capture_crop.py:307` | ✅ |
| AC-130.16 | e2e | Errors through the envelope: 404, `validation_error`, Session 58's region messages, `sidecar is malformed`, a path-free 409 | Local Canon: D-481 | `tests/e2e/test_api_capture_crop.py:344` | ✅ |
| AC-130.17 | e2e | `CROP_BAKE`: marks `{kept: 1, clipped: 1, dropped: 1}`, the crop's sidecar holds `clip_mark`'s output, its bake exists and is served; no marks gives no sidecar or bake | Local Canon: D-489 | `tests/e2e/test_api_capture_crop.py:392` | ✅ |
| AC-130.18 | e2e | The known bake differences, each on a region of the crop's bake | Local Canon: design §6.5 as D-486 corrects it | `tests/e2e/test_api_capture_crop.py:448` | ✅ |
| AC-130.19 | e2e | Redaction survives a clipped pixelate and a clipped eraser on a checkerboard | Local Canon: 09 `:1049` | `tests/e2e/test_api_capture_crop.py:537` | ✅ |
| AC-130.20 | e2e | Scan race: 10 crops against a scanning thread; each row `Crop`, no `.avkit-tmp` row, each crop listed once | Local Canon: D-490 | `tests/e2e/test_api_capture_crop.py:569` | ✅ |
| AC-130.21 | e2e | `CROP_CLEANUP`: four faults give a path-free 503 and leave the inbox, rows and source as they were; another writer's temporary file is never written over or removed (4 cases); a damaged source is a 422 | Local Canon: D-476 | `tests/e2e/test_api_capture_crop.py:612` (4 cases), `:688` (4 cases), `:762` | ✅ |
| AC-130.22 | e2e | `NO_RAW_CONSOLE` under `build_services` with a marker in every folder name; controls `engine.created`, `capture.registered`, `Crop` | Local Canon: Session 50 RULE-1; Session 54 RULE-2; D-496 | `tests/e2e/test_api_capture_crop.py:789` | ✅ |
| AC-130.23 | unit (MCP) | `crop` sends the box, `unit` and `name` as the POST body with no query string and with `ADD_TIMEOUT_MS` | Local Canon: D-492 | `mcp-server/tests/capture.test.ts:785` | ✅ |
| AC-130.24 | unit (MCP) | zod accepts a fraction box with `name`; refuses `x: -1`, `width: 0`, `unit: "inch"`, `name: ""`, 81 characters, an extra key, each missing required field | Local Canon: Boundary Inventory | `mcp-server/tests/capture.test.ts:833` | ✅ |
| AC-130.25 | unit (MCP) | The description holds `NEW shot`, `never changed`, `applied`, `clipped`, `-crop WxH+X+Y +repage` and at least three M7 markers; six fields advertised; not destructive, no confirm | Research-backed: design §6.7; D-494 | `mcp-server/tests/capture.test.ts:867` | ✅ |
| AC-130.26 | unit (MCP) | `ACTION_INDEX` has 71 rows, `crop` after `revert`, `avkit_capture` 11 actions | Local Canon: D-492 | `mcp-server/tests/capture.test.ts:884` | ✅ |
| AC-130.27 | unit (MCP) | `AUDIT_PLAN`'s `capture.crop` follows `capture.revert`, depends on `capture.flatten`, sends the 8×8 box and registers the new id | Local Canon: D-492 | `mcp-server/tests/audit/coverage.test.ts:105` | ✅ |
| AC-130.28 | unit (MCP) | Under D-499 A: `baselineCoverage`'s `missing` equals `BASELINE_PENDING`, `extra` empty; each pending key served and not in the baseline; two negative controls | Human: D-499 | `mcp-server/tests/audit/coverage.test.ts:143` | ✅ |
| AC-130.29 | unit (UI) | The region fixture holds the four crop cases, and the region pass matches Pillow on each | Local Canon: D-493 | `ui/tests/unit/capture-region-pass.test.ts:150` | ✅ |
| AC-37 (cross-ref) | regression | The three `CaptureSource` tuples gain `Crop`: `CAPTURE_SOURCE_MEMBERS` (`tests/unit/test_domain_capture.py`), the `test_domain.py` entry, `SOURCE_OUT` (`tests/e2e/test_api_captures.py`); every other AC-37 test passes | plan §Test Plan | gate `py-tests` | ✅ |
| AC-38 (cross-ref) | regression | The `avkit_capture` action list and counts move from 10 to 11 and the registry from 70 to 71 (`capture.test.ts` `CAPTURE_ACTIONS`, `action-index.test.ts`, `convert.test.ts`, `m7-resource.test.ts`); the other members pass unchanged | plan §MEU-130 guards | gate `mcp-tests` | ✅ |
| AC-40 (cross-ref) | regression | AC-40.26's pixel-exact shape is the model for AC-130.8; the adapter's other tests pass | plan §Test Plan | gate `py-tests` | ✅ |
| AC-67 (cross-ref) | regression | AC-67.19's step-order pin now reads revert, crop, capture_interactive (`runner-fake-backend.test.ts:175`); the other AC-67 tests pass | D-492 | gate `mcp-tests` | ✅ |
| AC-68 (cross-ref) | regression | AC-68.5's committed-baseline clause, amended under D-499 A (`coverage.test.ts:92`), and its 71-row pin (`:32`) | Human: D-499 | gate `mcp-tests` | ✅ |
| AC-84 (cross-ref) | regression | The scan and register tests pass; the crop shares `CAPTURE_FILE_LOCK` with the scan (D-490) | plan §MEU-130 guards | gate `py-tests` | ✅ |
| AC-16 (cross-ref) | regression | AC-16.9's extra-field oracle covers the new route: `_valid_body` gives the crop path a valid box (`tests/e2e/test_api_bodies.py:46`), so the extra key is the request's only fault, and `test_ac_16_9_extra_field_is_422` (`:56`) answers 422 for it | plan §Test Plan (row 4a) | gate `py-tests` | ✅ |
| AC-90 (cross-ref) | regression | AC-90.8 regenerates the region fixture and compares it with the committed set (`tests/unit/test_capture_bake_fixture.py:87`, `:126`); it passes with the four crop cases, and the existing cases keep their bytes (D-493) | plan §MEU-130 guards | gate `py-tests` | ✅ |
| AC-128, AC-129 (cross-ref) | regression | Session 58's region view (`resolve_region`, AC-128) and import (AC-129) pass unchanged; AC-129.1's "last member" assert now reads "Import follows Scan", since `Crop` is last (row 2) | [MEU-129 handoff](2026-11-08-capture-region-import-MEU-129-handoff.md) | gate `py-tests` | ✅ |
| AC-51, AC-81 (cross-ref) | regression | `ui/tests/e2e/test-ids.ts` is unchanged (scope-paths refuses it), so AC-51.6 and AC-81.13 pass | plan §Files Modified | gate `scope-paths`, `ui-tests` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|---------------------------|--------------|-----------|
| AC-130.1 to AC-130.7 | `assert 'kept' == 'clipped'` (31), `assert 'kept' == 'dropped'` (21), the moved fields `x: 150 != 50`, the clamp's `PixelateAnnot… == PixelateAnnot…`, and `assert 'Crop' in mappingproxy(…)` | Row 3: pass | `test_domain_capture.py:727-886`; `test_capture_service.py:1190` |
| AC-130.8 to AC-130.11 | `assert False` where `False = is_file()` (the stub wrote nothing); `Failed: DID NOT RAISE ConflictError` | Row 5: pass | `test_capture_adapter.py:1493-1716` |
| AC-130.12 to AC-130.22 | `assert 404 == 201`, `assert 404 == 503`, `assert 404 == 422`, `AssertionError: {"detail":"Not Found"}` (the route was missing) | Row 5: pass | `test_api_capture_crop.py:198-789` |
| AC-130.23 to AC-130.26 | `expected false to be true` (zod refused `crop`); `expected 'undefined' to be 'string'`; `expected [ …(70) ] to have a length of 71 but got 70` | Row 5: pass | `capture.test.ts:785-884` |
| AC-130.27 | `expected undefined to be defined` (no `capture.crop` step) | Row 5: pass | `coverage.test.ts:105` |
| AC-130.28 | `expected { missing: [], extra: [] } to deeply equal { …(2) }` | Row 5: pass | `coverage.test.ts:143` |
| AC-130.29 | `expected [] to deeply equal [ 'crop-pixelate-sliver', …(3) ]` | Row 5: pass | `capture-region-pass.test.ts:150` |
| AC-130.3 (round 1 F2) | `from_xy: (8, 4) != (8, 5)` in `[fwd]`; `[rev]` passed as the control | Pass (`s59-py-green-f2.txt`) | `test_domain_capture.py:803` |
| AC-130.10 (round 1 F1, D-506) | `assert None == <sRGB profile bytes>`: the crop carried no profile; the `none` and `junk` fallback cases passed as the controls | Pass (`s59-py-green-f1.txt`) | `test_capture_adapter.py:1657`, `:1691` |

- **Row 2, Python Red (carry):** 72 failed and 2 passed, every failure by assertion. The 2 that pass are cases the stub already satisfies (an arrow wholly inside), which the plan allows. `red-check.py` required 7 tests and found 0 problems.
- **Row 3, Green (carry):** the named suites passed 221; pyright 0 errors and ruff clean.
- **Row 4a, Python Red (crop):** 35 failed, every one by assertion. `red-check.py` required 15 tests and found 0 problems.
- **Row 4b, MCP and UI Red:** MCP 6 failed and 38 skipped in 2 files; UI 1 failed and 5 skipped. `red-check.py` read both receipts, required 7 tests and found 0 problems.
- **Round 1 corrections, Red:** F2's test failed 1 and passed 1 (its reversed control); F1's tests failed 1 and passed 2 (the fallback controls), every failure by assertion. `red-check.py` required each failing test and found 0 problems (`s59-redcheck-f2.txt`, `s59-redcheck-f1.txt`).
- **Round 1 corrections, Green:** F2's selection passed 225 and F1's `-k ac_130` selection passed 15 under `-W error::DeprecationWarning`; `pyright packages/` 0 errors and the gate's ruff paths clean. The reviewer's own oracle and reproducers, rerun on the fix, gave 0 of 20000 arrow mismatches and a CMYK crop carrying sRGB's 588-byte profile (`s59-f2-oracle.txt`, `s59-f12-repros.txt`).
- **Row 5, Green (crop):** the named Python suites passed 497; the OpenAPI check exited 0 after regeneration; pyright 0 errors and ruff clean; the MCP suite passed 485 in 35 files and its typecheck was clean; the UI region-pass suite passed 6.

### Commands Executed

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-red-carry", "command": "$env:TMP='C:\\Temp\\av-kit\\s59\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_capture_service.py -k ac_130 --tb=short -q *> C:/Temp/av-kit/s59-py-red-carry.txt; then red-check.py with the 7 --require ids *> C:/Temp/av-kit/s59-py-red-carry-check.txt (task.md row 2's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-130 carry Red: AC-130.1 to AC-130.7 against the row 1 clip_mark stub", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to 2", "output": "72 failed, 2 passed, 67 deselected in 7.09s. Decisive: assert 'kept' == 'clipped' (31); assert 'kept' == 'dropped' (21); x: 150 != 50; PixelateAnnot...block_size=12) == PixelateAnnot...block_size=12). red-check: 1 receipt(s), 7 required test(s), 0 problem(s). The row exits 0 because red-check confirms decisive failures."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-green-carry", "command": "$env:TMP='C:\\Temp\\av-kit\\s59\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain.py tests/unit/test_domain_capture.py tests/unit/test_capture_service.py tests/e2e/test_api_captures.py --tb=short -q *> C:/Temp/av-kit/s59-py-green-carry.txt; then pyright packages/ *> C:/Temp/av-kit/s59-r3-pyright.txt and ruff check packages/ tests/ *> C:/Temp/av-kit/s59-r3-ruff.txt (task.md row 3's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-130 carry Green: MARK_CARRY, MARK_CLIP_BOX, MARK_CLIP_ARROW, MARK_CLIP_TEXT and CROP_SOURCE", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to 3", "output": "221 passed in 4.38s. pyright: 0 errors, 0 warnings, 0 informations. ruff: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-red-crop-py", "command": "$env:TMP='C:\\Temp\\av-kit\\s59\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_capture_adapter.py tests/e2e/test_api_capture_crop.py -k ac_130 --tb=short -q *> C:/Temp/av-kit/s59-py-red-crop.txt; then red-check.py with the 15 --require ids *> C:/Temp/av-kit/s59-py-red-crop-check.txt (task.md row 4a's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-130 crop Python Red: AC-130.8 to AC-130.22 against the adapter stub and the missing route, with Pillow images under tmp_path and no network", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to 4a", "output": "35 failed, 34 deselected in 4.85s. Decisive: assert 404 == 201 (13); assert 404 == 503 (7); assert 404 == 422 (2); AssertionError: {\"detail\":\"Not Found\"} (10); assert False where False = is_file() (10); Failed: DID NOT RAISE ConflictError. red-check: 1 receipt(s), 15 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-red-mcp-ui", "command": "rtk proxy npm --prefix mcp-server run test -- tests/capture.test.ts tests/audit/coverage.test.ts -t \"AC-130\" *> C:/Temp/av-kit/s59-mcp-red.txt; rtk proxy npm --prefix ui run test -- tests/unit/capture-region-pass.test.ts -t \"AC-130\" *> C:/Temp/av-kit/s59-ui-red.txt; then red-check.py with the 7 --require ids over both *> C:/Temp/av-kit/s59-mcp-red-check.txt (task.md row 4b's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-130 MCP and UI Red: AC-130.23 to AC-130.29 against the unchanged capture.ts, registry.ts, plan.ts and region fixture, with AC-68.5 amended under D-499 A", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to 4b", "output": "MCP: Test Files 2 failed (2); Tests 6 failed | 38 skipped (44). UI: Test Files 1 failed (1); Tests 1 failed | 5 skipped (6). Decisive: expected false to be true; expected 'undefined' to be 'string'; expected [ …(70) ] to have a length of 71 but got 70; expected undefined to be defined; expected { missing: [], extra: [] } to deeply equal { …(2) }; expected [] to deeply equal [ 'crop-pixelate-sliver', …(3) ]. red-check: 2 receipt(s), 7 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-green-crop", "command": "$env:TMP='C:\\Temp\\av-kit\\s59\\tmp'; $env:TEMP=$env:TMP; rtk proxy uv run pytest tests/unit/test_domain.py tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py tests/unit/test_capture_bake_fixture.py tests/e2e/test_api_captures.py tests/e2e/test_api_capture_flatten.py tests/e2e/test_api_capture_region_import.py tests/e2e/test_api_capture_crop.py tests/e2e/test_api_openapi.py tests/e2e/test_api_bodies.py tests/e2e/test_api_downloads.py --tb=short -q *> C:/Temp/av-kit/s59-py-green-crop.txt; then export_openapi.py --check *> C:/Temp/av-kit/s59-r5-openapi.txt, pyright *> C:/Temp/av-kit/s59-r5-pyright.txt, ruff *> C:/Temp/av-kit/s59-r5-ruff.txt, npm --prefix mcp-server run test *> C:/Temp/av-kit/s59-mcp-green.txt, typecheck *> C:/Temp/av-kit/s59-r5-mcp-types.txt and npm --prefix ui run test -- tests/unit/capture-region-pass.test.ts *> C:/Temp/av-kit/s59-ui-green.txt (task.md row 5's Validation cell, run from P:/av-kit through an extracted .ps1)", "scope": "MEU-130 crop Green: CROP_REQUEST, CROP_READ, CROP_PIXELS, CROP_NAME, CROP_BAKE, CROP_CLEANUP, CROP_RESPONSE, CROP_MCP, BASELINE_PENDING and NO_RAW_CONSOLE", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to 5", "output": "497 passed, 21 warnings in 91.19s. export_openapi --check: exit 0, no output. pyright: 0 errors, 0 warnings, 0 informations. ruff: All checks passed! MCP: Test Files 35 passed (35); Tests 485 passed (485). tsc clean. UI: Tests 6 passed (6)."}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-6-records", "command": "task.md row 6 (abridged), run from P:/av-kit: the 09, 00 and 05 notes; tools/meu_status.py update MEU-130 ready_for_review --plan and render; issue-file.py *> C:/Temp/av-kit/s59-issue-file.txt; issue_triage.py render and triage; grouping row 59; then its Validation cell through an extracted .ps1 into s59-r6-render.txt, s59-r6-issues.txt and s59-r6-status.txt", "scope": "Row 6: the D3 spec text, MEU-130 ready_for_review with this plan, MCP-AUDIT-BASELINE-PENDING-CROP filed (D-499 A), the renders, and grouping row 59 executed", "phase": "static", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to 6", "output": "issue-file: D-499 ruling found (\"D-499 A\"); added lines 45 removed lines 0; MCP-AUDIT-BASELINE-PENDING-CROP open P3; 125 issues. Validation: ready_for_review open ['| 59 | `capture-crop-copy` | MEU-130 | P2 | executed | `docs/execution/plans/2026-11-08-capture-crop-copy/` |']; exit 0"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-r1-red-f2", "command": "TMP='C:\\Temp\\av-kit\\s59\\tmp' TEMP=$TMP PYTHONIOENCODING=utf-8 rtk proxy uv run pytest tests/unit/test_domain_capture.py -k half_tie -p no:cacheprovider > C:/Temp/av-kit/s59-py-red-f2.txt 2>&1; then red-check.py --require test_ac_130_3_arrow_half_tie_rounds_up C:/Temp/av-kit/s59-py-red-f2.txt > C:/Temp/av-kit/s59-redcheck-f2.txt 2>&1 (Bash tool, from P:/av-kit)", "scope": "Execution review round 1 F2 Red: AC-130.3's exact-half arrow in both directions against the float clip", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to H1-6b and the F2 test", "output": "1 failed, 1 passed, 106 deselected in 0.10s. Decisive: test_ac_130_3_arrow_half_tie_rounds_up[fwd] from_xy: (8, 4) != (8, 5); [rev] passed. pytest exit 1 (s59-py-red-f2.txt.exit). red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-r1-green-f2", "command": "TMP='C:\\Temp\\av-kit\\s59\\tmp' TEMP=$TMP PYTHONIOENCODING=utf-8 rtk proxy uv run pytest tests/unit/test_domain_capture.py tests/unit/test_domain.py tests/unit/test_capture_service.py tests/e2e/test_api_capture_crop.py tests/unit/test_capture_bake_fixture.py -p no:cacheprovider -q > C:/Temp/av-kit/s59-py-green-f2.txt 2>&1 (Bash tool, from P:/av-kit)", "scope": "Execution review round 1 F2 Green: MARK_CLIP_ARROW in exact fractions", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to H1-6b and the F2 test and fix", "output": "225 passed in 7.76s"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-r1-red-f1", "command": "TMP='C:\\Temp\\av-kit\\s59\\tmp' TEMP=$TMP PYTHONIOENCODING=utf-8 rtk proxy uv run pytest tests/unit/test_capture_adapter.py -k cmyk -p no:cacheprovider -W error::DeprecationWarning > C:/Temp/av-kit/s59-py-red-f1.txt 2>&1; then red-check.py --require test_ac_130_10_cmyk_icc_to_srgb C:/Temp/av-kit/s59-py-red-f1.txt > C:/Temp/av-kit/s59-redcheck-f1.txt 2>&1 (Bash tool, from P:/av-kit)", "scope": "Execution review round 1 F1 Red under D-506: AC-130.10's profiled CMYK JPEG, with Pillow images under tmp_path and a profile built from bytes", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to H1-6b, the F2 fix and the F1 tests", "output": "1 failed, 2 passed, 46 deselected. Decisive: test_ac_130_10_cmyk_icc_to_srgb assert None == <sRGB profile bytes>; the none and junk fallback cases passed. pytest exit 1 (s59-py-red-f1.txt.exit). red-check: 1 receipt(s), 1 required test(s), 0 problem(s)"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-130-r1-green-f1", "command": "TMP='C:\\Temp\\av-kit\\s59\\tmp' TEMP=$TMP PYTHONIOENCODING=utf-8 rtk proxy uv run pytest tests/unit/test_capture_adapter.py -k ac_130 -p no:cacheprovider -q -W error::DeprecationWarning > C:/Temp/av-kit/s59-py-green-f1.txt 2>&1; rtk proxy uv run pyright packages/ > C:/Temp/av-kit/s59-f12-pyright.txt 2>&1; rtk proxy uv run ruff check packages/ tests/ tools/capture_bake_fixture.py --output-format concise > C:/Temp/av-kit/s59-f12-ruff.txt 2>&1 (Bash tool, from P:/av-kit)", "scope": "Execution review round 1 F1 Green under D-506: CROP_PIXELS converts CMYK, YCbCr and LAB through the profile to sRGB", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD f15626c plus rows 0 to H1-6b and both corrections", "output": "15 passed, 34 deselected in 1.25s. pyright: 0 errors, 0 warnings, 0 informations. ruff: All checks passed!"}
```

```json
{"schema_version": "evidence.v1", "cwd": "P:/av-kit", "check_id": "s59-gate-r2", "command": "pwsh -NoProfile -File C:/Temp/av-kit/s59/gate-r2.ps1 (H1-2's wrapper with the receipt renamed: $env:ELECTRON_RUN_AS_NODE=$null; rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-11-08-capture-crop-copy/session-gate.ps1 *> C:/Temp/av-kit/s59-gate-r2.txt; then the same Select-String and exit $code)", "scope": "H1-2 rerun after the execution review round 1 corrections (F1 under D-506, F2): the registered D6 gate on the whole tree", "phase": "full", "exit_code": 0, "result": "pass", "fresh": true, "snapshot": false, "tested_state": "f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90", "output": "identity-before exit=0; py-types exit=0 (0 errors); py-lint exit=0 (All checks passed!); ui-types exit=0; ui-lint exit=0 (eslint --max-warnings 0); task-contract exit=0 (25 rows, 23 fully checked, 2 view_file exempt: H1-5, H2-1); scope-paths exit=0 (changed paths: 48, outside scope: [], head moved (S3): False); red-check-selftest exit=0 (36 fixtures, 11 positive, 25 negative, 0 wrong); py-tests exit=0 (1564 passed, no warnings); ui-tests exit=0 (114 files, 1193 passed); ui-build exit=0; openapi exit=0; mcp-types exit=0; mcp-build exit=0; mcp-tests exit=0 (35 files, 485 passed); state-render exit=0 (136 MEUs, 12 phases, regions match); issues-render exit=0 (known-issues.md is up-to-date); crop exit=0 (23 passed); identity-after exit=0 (tested_state before = after); mcp-audit, build-record, package-build and ui-electron skipped; baseline failures excused: py [], ui [], mcp []; session-gate: all steps exit 0"}
```

### Quality Gate Results

`s59-gate-r2` (H1-2, rerun on the whole tree after the round 1 corrections) is the fresh full record, and its last line is:

> session-gate: all steps exit 0

- **Static:** pyright 0 errors; ruff check passed; the UI typecheck and ESLint (`--max-warnings 0`) passed; lint_task_contract passed on 25 rows (23 fully checked, 2 `view_file` exempt); scope-paths found 48 changed paths, none outside scope, `ui/tests/e2e/test-ids.ts` unchanged, and HEAD f15626c did not move (S3); the red-check selftest read 36 fixtures with 0 wrong.
- **Suites:** pytest 1564 passed with no warnings (the baseline's 1448 plus 116 cases for MEU-130, 5 of them from the round 1 corrections); Vitest 1193 passed in 114 files (the baseline's 1192 plus AC-130.29); MCP tests 485 passed in 35 files (the baseline's 479 plus AC-130.23 to .28). No baseline failure was excused.
- **Build and state:** the UI build, the OpenAPI check, the MCP typecheck and the MCP build exited 0; the state render (136 MEUs) and the issue render match the files on disk. H1-3's `render --check` and H1-4's `export_openapi.py --check` passed again after the gate.
- **Runtime:** the crop module (`tests/e2e/test_api_capture_crop.py`) passed 23 of 23 on its own. It builds every image with Pillow under `tmp_path`; no test reads or writes the network.
- **Skipped:** `mcp-audit` (live network, which the brief forbids; `BASELINE_PENDING` covers the missing `avkit_capture.crop` key), `build-record` (no installer build), `package-build` (no packaged surface changes; MEU-125 ran the package build and its smokes) and `ui-electron` (no renderer source file and no route the renderer calls changes).
- **Identity:** the tested_state was the same before and after the gate, and again when recomputed afterwards: `f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90`. Round 1 reviewed the earlier gate, `s59-gate-h1-2`, at `f15626c25af428e33c0274cb280eef6579455320+fd97e8484a122e30240b8aeb29933ec764ba893f4937436f2cfc2b59998c9587`; its receipts are kept in `C:/Temp/av-kit/s59/gate-r1/`. It is re-derived with `ELECTRON_RUN_AS_NODE` unset, as H1-6b's cell does. The handoffs, reviews and other closeout records are artifacts the identity leaves out, so writing them doesn't change it.
- **Rerun after a test fix.** The first gate passed at tested_state `f15626c25af428e33c0274cb280eef6579455320+37e97b54908ea64acde7e53d6dbd974b9f31152bacb3d0897a31188979ad54c0` (1559 Python tests, 21 warnings). All 21 were Pillow 13's `DeprecationWarning` for `Image.getdata()`, raised by six calls in `tests/e2e/test_api_capture_crop.py`. Those calls now use `get_flattened_data()`, which returns the same pixel tuples; the module passed 23 of 23 under `-W error::DeprecationWarning`, and ruff passed. The change touched only that test file, but it is a gated input, so H1-2 ran again on the whole tree, and that run (`s59-gate-h1-2`, at the round-1 state above) is the gate round 1 reviewed. The round 1 corrections changed gated inputs again, so `s59-gate-r2` above replaces it as the record. It passed on its first try.

### Row 5 diffs

**OpenAPI.** `openapi.committed.json` gains 241 lines and loses none: the path `/api/v1/captures/{id}/crop` and the schemas `CaptureCropIn`, `CaptureCropOut`, `CaptureCropRequestedOut`, `CaptureCropAppliedOut` and `CaptureCropMarksOut`. The H1-4 check proves it still matches the code.

**Parity fixture.** `ui/tests/e2e/fixtures/capture-region-pass.json` gains the four crop cases; the old last case differs only by its trailing comma. The region PNG pair is byte-identical to HEAD.

```diff
 {"name": "pixelate-then-eraser", "width": 32, "height": 24, "pixels": [10, 101, 200, …]}
-]
+,
+{"name": "crop-pixelate-sliver", "width": 6, "height": 8, …},
+{"name": "crop-pixelate-corner", "width": 10, "height": 8, …},
+{"name": "crop-eraser-edge", "width": 12, "height": 12, …},
+{"name": "crop-eraser-ring", "width": 12, "height": 12, …}
+]
```

The excerpt is abridged; the fixture holds one case per line.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `packages/core/src/avkit_core/domain/enums.py` | modified | `CaptureSource.Crop`, last |
| `packages/core/src/avkit_core/domain/capture.py` | modified | `MarkCarry` (row 1, D-495), `clip_mark` and its four helpers (row 3); the arrow clip in exact fractions (round 1 F2) |
| `packages/core/src/avkit_core/ports/capture.py` | modified | `crop` on the annotate port |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | modified | `crop`, its mode and ICC constants, and `_to_srgb` (round 1 F1, D-506) |
| `packages/core/src/avkit_core/services/capture.py` | modified | The `CROP_NAME` constants, `crop_name_stem`, `crop_default_stem`, `CROP_REFUSALS`, `crop_shot`, `_saved_marks`, `_crop_dest`, `_discard` |
| `packages/api/src/avkit_api/schemas/captures.py`, `routes/captures.py` | modified | `CaptureCropIn`, the four out schemas and the `crop_capture` route |
| `openapi.committed.json` | modified | Regenerated in row 5 |
| `mcp-server/src/toolsets/capture.ts`, `registry.ts` | modified | The `crop` member, `CROP_TEXT`, the `ACTION_INDEX` row and the timeout branch |
| `mcp-server/scripts/audit/plan.ts` | modified | The `capture.crop` step |
| `tools/capture_bake_fixture.py`, `ui/tests/e2e/fixtures/capture-region-pass.json` | modified | `crop_cases()` and the regenerated fixture |
| `tests/unit/test_domain_capture.py`, `test_domain.py`, `test_capture_service.py`, `test_capture_adapter.py` | modified | AC-130.1 to .11, the `CaptureSource` tuples, and the round 1 F1 and F2 tests |
| `tests/e2e/test_api_capture_crop.py` | new | AC-130.12 to .22. LF |
| `tests/e2e/test_api_captures.py`, `test_api_openapi.py`, `test_api_bodies.py`, `test_api_downloads.py` | modified | `SOURCE_OUT` and the route and schema pins that count the crop route |
| `mcp-server/tests/capture.test.ts`, `action-index.test.ts`, `convert.test.ts`, `m7-resource.test.ts`, `audit/coverage.test.ts`, `audit/runner-fake-backend.test.ts` | modified | AC-130.23 to .28, the 70 → 71 pins, AC-68.5 under D-499 A, the AC-67.19 order |
| `ui/tests/unit/capture-region-pass.test.ts` | modified | AC-130.29 |
| `docs/build-plan/09-screenshot-capture.md`, `00-overview.md`, `05-mcp-server.md` | modified | §Spec text (row 6); 09's §Crop note amended by D-506 |
| `.agent/context/known-issues.yaml`, `known-issues.md`, `triage-output.yaml` | modified | `MCP-AUDIT-BASELINE-PENDING-CROP` filed and the renders (row 6) |
| `docs/BUILD_PLAN.md`, `.agent/context/meu-status.yaml`, `meu-registry.md`, the grouping file | modified | MEU-130 `ready_for_review`; grouping row 59 `executed` (row 6) |

Line endings were measured before each edit and kept: CRLF files stayed CRLF, and LF files stayed LF.

```diff
 # domain/capture.py
+MarkCarry = Literal["kept", "clipped", "dropped"]
+
+def clip_mark(
+    mark: Annotation, left: int, top: int, width: int, height: int
+) -> tuple[Annotation | None, MarkCarry]:
+    match mark:
+        case ArrowAnnotation():
+            return _clip_arrow(mark, left, top, width, height)
+        case RectAnnotation():
+            return _clip_rect(mark, left, top, width, height)
+        case HighlightAnnotation():
+            return _clip_half_open(mark, left, top, width, height)
+        ...  # PixelateAnnotation and EraserAnnotation: _clip_half_open
+        case TextAnnotation():
+            return _clip_text(mark, left, top, width, height)
+        case _:
+            assert_never(mark)
 # routes/captures.py
+@router.post("/{id}/crop", status_code=201, response_model=CaptureCropOut)
+def crop_capture(
+    id: str,
+    body: CaptureCropIn,
+    capture: Any = Depends(get_capture_service),
+) -> CaptureCropOut:
+    result = capture.crop_shot(
+        id, x=body.x, y=body.y, width=body.width, height=body.height, unit=body.unit, name=body.name
+    )
```

The excerpt is abridged; `domain/capture.py:424-535`, `services/capture.py:887-1040` and `routes/captures.py:397-430` are the source.

---

## Codex Validation Report

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| F1 | High | Round 1: `CROP_PIXELS` dropped the ICC profile of a CMYK JPEG (557168 bytes before, 0 after), against D-482 and AC-130.10 | `adapter.py:409-410` (round 1) | Keep the contract for converted modes, or get it amended | fixed (round 2, under D-506) |
| F2 | Medium | Round 1: `MARK_CLIP_ARROW` rounded an exact half-pixel entry down in one direction of the same arrow (`(8,4)`, not `(8,5)`) | `domain/capture.py:517`, `:526-527` (round 1) | Use exact arithmetic at the tie; add the case and its reverse to AC-130.3 | fixed (round 2) |

### Verdict

`approved` in round 2 of loop `s59-execution-2026-11-08-capture-crop-copy` (Codex, 2026-11-09), with no open findings and intent achieved as D-506 amends it. Round 1 (8,336,600 tokens) returned `changes_required` with F1 (High, blocking) and F2 (Medium, not blocking). Mat ruled F1's contract question as D-506. The corrections added 5 Red-first cases. Round 2 (4,475,811 tokens) closed both as `fixed` with no new finding. The loop used 12,812,411 of its 60,000,000-token budget and 2 of 6 rounds. The reviewer recomputed the tested_state independently and got `f15626c25af428e33c0274cb280eef6579455320+431a6b2db44b53eb217c171bbdfbbc504431a9fe41dcd4cb79991ad72be8ab90`. Its exact-rational oracle found 0 mismatches in 20000 arrows. Report: [implementation-critical-review.md](2026-11-08-capture-crop-copy-implementation-critical-review.md). H1-7a: `OK: review_mode=execution; round 2 of 6; verdict=approved; open findings=0` (`C:/Temp/av-kit/review-state-check.txt`). H1-7b: `OK: approved at round 2 of 6, 0 open blocking findings` (`C:/Temp/av-kit/exec-review.txt`).

---

## Deferred Items

| Item | Kind | Deferred-to | Basis |
|------|------|-------------|-------|
| The committed live-audit baseline doesn't hold `avkit_capture.crop` | out-of-scope | `MCP-AUDIT-BASELINE-PENDING-CROP` (filed in row 6); the next authoritative audit run closes it and empties `BASELINE_PENDING` | D-499 A |
| The Capture page's crop tool | out-of-scope | MEU-131, Session 60 `gui-capture-crop-tool` | grouping row 60 |
| A live agent run of the `crop` description | out-of-scope | Session 60's prompt | D-494 |
| Commit and push | out-of-scope | — | Only on Mat's explicit words (H2-5) |

**Execution notes.**
- **Row 2.** `test_ac_129_1_capture_source_import` asserted that `Import` is the last member; `Crop` now is. The assert reads "Import follows Scan", and AC-130.7 pins `Crop` as last. AC-130.2's zero-size case ids use `w0` and `h0`, because red-check's header pattern needs three leading underscores.
- **Row 4a.** AC-130.15's `_3` case uses a second source, `pic.png`, with `pic-crop.ANN.JSON` and another writer's `pic-crop_2.PNG.AVKIT-TMP` written first, so both kinds of taken name show, case-folded. AC-130.14 covers the right edge, the bottom edge, the bottom-right corner and a fraction box, because `resolve_region` refuses a negative `x` or `y`. The damaged-source case splits the `IDAT` into a 4-byte `IDAT` and a `BAD!` chunk, keeping the file's size, to get Pillow's `SyntaxError`. AC-130.9 and .10 assert `out.is_file()` before opening the crop, so their Red is an assertion.
- **Row 4b.** The `ADD_TIMEOUT_MS` branch the plan cites at `registry.ts:335-340` is at `:387-392` (Session 58's lines sit above it). AC-130.24 also refuses each missing required field and accepts an 80-character name. AC-130.27 runs the step on a fake `StepContext`. AC-130.28's helper has two negative controls.
- **Row 5, `CROP_NAME`.** The Windows reserved-name check reads the part before the first dot, with trailing spaces stripped, because Windows reserves `CON.txt` as well as `CON`. A source stem that is empty after stripping ` ._-` gives the stem `crop`.
- **Row 5, `CROP_CLEANUP`.** `_discard` swallows an `OSError` from a removal, so a failed clean-up can't replace the fixed 503. After `os.replace`, the temporary name no longer belongs to the call and isn't removed.
- **Row 5, `CROP_READ`.** `_saved_marks` raises `sidecar is malformed` when reading or parsing the JSON fails; `annotations_from_sidecar`'s own messages pass unchanged.
- **Row 5, two test files changed.** AC-130.21's damaged-source case put the source's bytes back before its follow-up list, because the list scans the inbox and the scan's probe doesn't catch Pillow's `SyntaxError` (see the observation below). AC-67.19 (`runner-fake-backend.test.ts:185`) pinned `capture_interactive` directly after `revert`; D-492 puts `crop` between them, so the pin now reads revert, crop, capture_interactive.
- **Row 5, the audit step.** `capture.crop` is a `StepSpec` with its own `execute`, not a `simpleStep`, because it reads the source's SHA-256 over REST before the call. `httpBody` didn't need a change.
- **Row 5, the fixture.** The fixture JSON is CRLF in the working copy and LF in git (`i/lf w/crlf`), as before.
- **Row 6.** 05 has no `avkit_capture` count to move; 09 §MCP's table gained the row. 05's ImageMagick table took design §6.6's crop rows but not the deferred `-trim` row. `issue-file.py`'s `last_checked` is 2026-11-09, the day AC-68.5 and AC-130.28 ran. `meu_status.py update` re-wrapped four notes f15626c wrote by hand; only MEU-130's fields changed in content.
- **Moved cites (Session 51 RULE-3).** `capture.registered` is `services/capture.py:1288` (the plan cited `:894`); `capture.wrote` is `adapter.py:550` and `:567` (the plan cited `:366`).
- **Observation, not fixed (it predates this session).** Any inbox-root file the scan can't probe breaks `GET /captures`. A non-image gives a 422 whose message names its path (`InboxPathError(f"{path} is not an image")`), and a PNG Pillow rejects with `SyntaxError` gives a 500. The crop's own refusal of a damaged source is right (AC-130.21). Not fixed here; filed at closeout as `CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST` (P2) under Mat's D-507.
- **Execution review round 1.** F1 (High): row 5 dropped the profile of a CMYK, YCbCr or LAB source without recording the departure from D-482. It went to Mat, who ruled D-506 A ("A: convert via profile (Recommended)"); the plan's goal ICC clause, behaviour, `CROP_PIXELS` row and AC-130.10 and 09's §Crop note carry the amendment. F2 (Medium): an exact-half arrow end rounded down in one direction through float error; the clip now runs in exact fractions. Both went Red then Green, and H1-2 ran again on the whole tree (`s59-gate-r2.txt`); the round-1 gate's receipts are kept in `C:/Temp/av-kit/s59/gate-r1/`.
- **No network.** No row and no gate step made a network request. Every test image is built with Pillow under `tmp_path`.

---

## Decision Log

```yaml
decision_log:
  - id: D-506
    stage: execution
    question: "Execution review round 1 F1: a CMYK JPEG's crop loses its ICC profile, though D-482 keeps it. PNG can't hold CMYK or a CMYK profile. How does a crop treat a source in a mode PNG can't store?"
    resolution: human
    class: two-way
    chosen: "A, as recommended: a CMYK, YCbCr or LAB source with a profile that builds a transform converts through it to sRGB with ImageCms, and the crop carries the sRGB profile; with no profile, or one that builds no transform, it converts plainly to RGB and carries none. Amends D-482, CROP_PIXELS and AC-130.10. Mat's words (2026-11-09): 'A: convert via profile (Recommended)'"
    source_tag: Human-approved
    precedents:
      - "C:/Temp/av-kit/s59-exec-review-round-1.md — F1, U.S. Web Coated (SWOP) v2: 557168 ICC bytes before the crop and 0 after"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:65 (before the fix) — _CROP_ICC_DROP_MODES dropped the profile, a departure from D-482 that row 5 did not record"
      - "C:/Temp/av-kit/s59-f1-probe.txt — Pillow 13 with littlecms2: plain CMYK to RGB (148,114,80), through SWOP (157,122,93); junk bytes raise OSError, a profile for another colour space raises PyCMSError"
    research:
      engine: none
      sources: []
    reasoning: "D-482 keeps the profile because stripping it shifts colours. A CMYK profile can't sit on RGB pixels in a PNG, so the literal rule can't hold; converting through the profile is how a colour-managed viewer shows the source, and the sRGB profile then describes the crop's pixels. C, dropping it and amending the contract, keeps the colour shift. Doing nothing leaves F1 open and MEU-130 unapproved. Mat rules it because it amends an approved AC. Two-way: one adapter helper and three tests."
    human_message_reference: null
  - id: D-507
    stage: closeout
    question: "Session 59 found a pre-existing scan defect outside the crop: one inbox-root file the scan can't open breaks GET /captures, with a 422 naming its path or a 500. File it, or leave it as the handoff's observation?"
    resolution: human
    class: two-way
    chosen: "File it, as recommended: CAPTURE-SCAN-UNPROBEABLE-FILE-BREAKS-LIST, P2, open, linked to MEU-130, in Session 59's commit. Mat's words (2026-11-10): 'File it (Recommended)'"
    source_tag: Human-approved
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:411 — scan_inbox calls probe on each scan-extension file with no catch"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:316 — probe raises InboxPathError naming the path, mapped to 422"
      - ".agent/context/handoffs/2026-11-08-capture-crop-copy-MEU-130-handoff.md — row 5's observation, not fixed"
    research:
      engine: none
      sources: []
    reasoning: "Session 50's rule says a raw value that reaches an API message is fixed or raised, never left as a residual, and the defect predates this session and lies outside MEU-130's scope. Filing records the probe and its two failure shapes for a plan of its own. Leaving it as a handoff observation hides it from the register. Two-way."
    human_message_reference: "File it (Recommended)"
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Initial MEU-130 handoff after the H1-2 gate |
| Updated | 2026-11-09 | claude-code-local (Claude Opus 5.5) | Execution review round 1 corrections: F1 under D-506 and F2, their Red and Green, and the H1-2 gate rerun |
| Approved | 2026-11-09 | codex-independent-reviewer | Execution review round 2: `approved`, F1 and F2 `fixed`, no new finding |
