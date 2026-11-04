# Walkthrough — Capture new marks (Session 39)

Execution record for [implementation-plan.md](implementation-plan.md) and [task.md](task.md). Worktree `P:/av-kit-wt/s39-capture-new-marks`, branch `claude/s39-capture-new-marks`. Receipts are under `C:/Temp/av-kit/s39-*.txt`; decisive lines are pasted here.

## Execution message

- **Execution gate (`plan_to_exec_gate: human`).** Plan review loop `s39-plan-2026-10-16-capture-new-marks` closed `approved` in round 2 (2/3). Mat's explicit execution message, 2026-10-16, verbatim: `@.agent/workflows/execution-session.md  Session 39 as per session grouping`.
- **D-16 confirmation.** Mat's message of 2026-10-16, answering User Review Required item 2 (separate Block size field), verbatim: `2. confirmed`.
- **Base.** Sessions 34 and 36 landed on `main` as `90bb409` (Mat: `3. merge as you see fit`); the worktree was fast-forwarded to it before execution.
- **Latest reflection rules applied** (`2026-10-14-capture-render-fidelity-reflection.md` §Next Session Design Rules): RULE-1 (the gate runs every build stage and applies the baseline rule itself; already in `session-gate.ps1`), RULE-2 (`red-check.py` strips ANSI and carries the coloured fixture), RULE-3 (dispatch commands set `RECEIPTS_DIR` and `AGENT_MODEL_REGISTRY_HOME`).

## Baseline (row 0)

- **Environment fix before the row command.** The first run exited 2 at `uv sync --frozen --all-packages`: the worktree's gitignored `.venv` had been created on CPython 3.14 (`version_info = 3.14`), and `spacy==3.8.15` has no `cp314` wheel. `P:/av-kit/.venv` and the s34 worktree use 3.12.12, so the worktree venv was recreated with `uv venv --clear --python 3.12.12 .venv` (receipt `C:/Temp/av-kit/s39-venv.txt`: `Using CPython 3.12.12`), and the row command was re-run unchanged.
- **Row command** (task row 0, verbatim, from the worktree in `pwsh`): exit 0.
- **Prerequisites (S1)**, `C:/Temp/av-kit/s39-prereq.txt`: `ancestors (record only): {'89c2937': True, 'bb0ef7e': True}`, `prereq problems: []`. No `graphify-out*` directory exists.
- **`baseline.sha`**: `90bb40977e487f4893a1c586c2c20b8f78ef105f`.

```yaml
evidence.v1:
  - command: "rtk proxy uv run pytest tests/ -q --tb=no"
    exit: "not captured (the row command records the summary only)"
    receipt: C:/Temp/av-kit/s39-base-py.txt
    decisive: "2 failed, 674 passed, 1 warning in 83.84s"
    failed:
      - "tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]"
      - "tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]"
  - command: "rtk proxy npm --prefix ui run test"
    receipt: C:/Temp/av-kit/s39-base-ui.txt
    decisive: "Test Files 87 passed (87); Tests 839 passed (839)"
  - command: "rtk proxy npm --prefix mcp-server run test"
    receipt: C:/Temp/av-kit/s39-base-mcp.txt
    decisive: "Test Files 3 failed | 20 passed (23); Tests 10 failed | 401 passed (411)"
    failed: "8 in tests/audit/runner-fake-backend.test.ts (AC-67.19, AC-68.1 x2, AC-68.6, AC-68.7 x2, AC-68.8 x2), tests/capture.test.ts AC-38.8, tests/convert.test.ts AC-32.8; every one needs the built server mcp-server/dist, which is gitignored and absent from a fresh worktree"
  - command: "rtk proxy npm --prefix mcp-server run build; rtk proxy npm --prefix mcp-server run test"
    exit: 0
    receipt: C:/Temp/av-kit/s39-base-mcp-build.txt, C:/Temp/av-kit/s39-base-mcp2.txt
    decisive: "Test Files 23 passed (23); Tests 411 passed (411)"
  - command: "rtk proxy npm --prefix ui run build"
    exit: 0
    receipt: C:/Temp/av-kit/s39-base-build.txt
    decisive: "built in 3.90s"
  - command: "rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts"
    receipt: C:/Temp/av-kit/s39-base-e2e.txt
    decisive: "Running 34 tests using 1 worker; 34 passed (1.1m)"
  - command: "baseline summary check (row 0)"
    exit: 0
    receipt: C:/Temp/av-kit/s39-base-check.txt
    decisive: "baseline receipts without a result summary: []"
```

**Baseline failed sets.** Python: the two environmental packaging tests above, the same two the gate's `$baselinePyFailed` lists (`session-gate.ps1:83-86`). UI unit: none. MCP: none once `mcp-server/dist` is built; the 10 failures without it are a missing build output, not a product baseline. Electron `capture-inbox.test.ts`: none.

**Gate-order finding (RULE-1).** `session-gate.ps1:106-107` runs `mcp-tests` before `mcp-build`. In a fresh worktree that is the failure seen above; with a `dist` left over from earlier, `mcp-tests` runs against a stale build of `mcp-server/src`, which rows 3a and 5a change. This is raised in the S2 Decision Brief below, not edited.

## Census (row 1)

Command: task row 1 `rg` over `CENSUS_PATTERNS` in `ui/tests tests mcp-server/tests`, receipt `C:/Temp/av-kit/s39-census.txt`, exit 0, `census hits: 289` (one line is the `rtk` banner). Hits per file: `capture-page.behavior.test.ts` 138, `capture-inbox.test.ts` 56, `capture-toolbar.test.ts` 31, `capture-action-row.test.ts` 18, `capture-page.test.ts` 11, `icon-hints.test.ts` 9, `test-ids.ts` 7, `capture-help-content.test.ts` 6, `test_domain_capture.py` 6, `capture-hit-test.test.ts` 2, `convert-page.test.ts` 1, `layout-primitives.test.ts` (e2e) 1, `test_domain.py` 1, `test_api_capture_flatten.py` 1.

| Hit (file:line) | What it pins | Disposition |
|---|---|---|
| `tests/unit/test_domain_capture.py:27-33, 111-120` | `ANNOTATION_TYPE_MEMBERS` / `ANNOTATION_WIRE` exact members | TA-1 |
| **`tests/unit/test_domain.py:306`** (`ENUM_MEMBERS["AnnotationType"]`, read by `test_ac_2_1_strenum_members_and_values` `names == expected` and `test_ac_2_11_enum_closed_set_exhaustiveness` `== set(expected)`) | the exact `AnnotationType` member tuple `("Arrow", "Rect", "Highlight", "Text")` | **new-contradiction (S2)**: adding `Pixelate`/`Eraser` fails both tests; not in `TEST_AMENDMENTS` |
| `ui/tests/unit/capture-toolbar.test.ts:10-13, 31-38, 42-49, 65-69, 77-97` | `TOOLS`, `TOOL_BUTTON_IDS`, `TOOLBAR_BUTTONS` names, `expectedGroups`, `:83` colour always present | TA-2 |
| `ui/tests/unit/capture-toolbar.test.ts:109, 114` | options row ids exist in the chrome | unaffected: ids unchanged |
| `ui/tests/unit/capture-page.test.ts:69-76, 259-271` | AC-39.8 tool id list in the viewport, kept off the picker | TA-3 (id list) |
| `ui/tests/unit/capture-page.test.ts:111` | `HELP_TOPICS` `'four tools'` | TA-3 (`'annotation tools'`) |
| `ui/tests/unit/capture-page.behavior.test.ts:1395-1541` | `MEU65_TOOLBAR`, `MEU65_TOGGLES`, `MEU65_OPTION_IDS`, `expectOptionGroups` type unions, AC-65.3 cases | TA-4 |
| `ui/tests/unit/capture-page.behavior.test.ts:1244, 1489` | loops over a literal five-id subset (h-7, disabled hint) | unaffected: subset loops, the new ids are not required by them |
| `ui/tests/unit/capture-page.behavior.test.ts` remaining 120-odd hits | clicks on existing tools and counts of existing `data-annotation-type` marks | unaffected: existing tools and marks behave as before |
| `ui/tests/e2e/test-ids.ts:186-224, 389, 412` | existing constants, all in the AC-51.6 hashed prefix or earlier blocks | TA-5: the four new constants go in a new block appended at the end, so the AC-51.6/AC-81.13 prefix hash (`6E569F82…F454`) is unchanged |
| `ui/tests/e2e/capture-inbox.test.ts:896-898` | AC-65.4 NO_OVERFLOW tool loop | TA-5 |
| `ui/tests/e2e/capture-inbox.test.ts:222-225, 250, 746` | literal subsets of tool ids visible/disabled | unaffected: subsets |
| `ui/tests/e2e/capture-inbox.test.ts` remaining hits | clicks on existing tools and existing mark counts; `expectNoOverflow` definition | unaffected |
| **`ui/tests/unit/icon-hints.test.ts:48-57`** (`NO_SHOT_IDS`, read by AC-80.8 at `:309-325`) | AC-80.8 loops over every `TOOLBAR_BUTTONS` entry with no shot and expects the hint `spec.name` unless the id is in the literal `NO_SHOT_IDS`; a disabled new tool shows `Pixelate — Select a shot first`, so the expectation `Pixelate` fails | **new-contradiction (S2)**: not in `TEST_AMENDMENTS` |
| `ui/tests/unit/icon-hints.test.ts:21, 305, 311-318` | `TOOLBAR_BUTTONS` loop (shot open) | covered by the S2 row above; with a shot open the new buttons pass (name hint) |
| `ui/tests/unit/capture-action-row.test.ts:294-306, 359, 392-394, 499, 550, 614-615, 754, 766` | existing marks and tools | unaffected |
| `ui/tests/unit/capture-action-row.test.ts:362-376` | AC-81.1 `ACTION_BUTTONS` disjoint from `TOOLBAR_BUTTONS` | unaffected: the new ids are tools, not actions |
| `ui/tests/unit/capture-action-row.test.ts:466-474` | literal subset loops over tools/marks | unaffected |
| `ui/tests/unit/capture-action-row.test.ts:702-705` | AC-81.12 `four-tools` body contains `HELP_EDIT_TEXT`, no `Sample` | unaffected: `HELP_TOOLS` keeps the id and `HELP_EDIT_TEXT` (constraint on row 5b) |
| `ui/tests/unit/capture-action-row.test.ts:710-748` | AC-81.13 registry prefix hash | unaffected (see `test-ids.ts` row) |
| `ui/tests/unit/capture-help-content.test.ts:12-30` | AC-59.20, AC-60.15, AC-66.16 sentences in the `four-tools` body | unaffected: `HELP_TOOLS` keeps every existing sentence (constraint on row 5b) |
| `ui/tests/unit/capture-hit-test.test.ts:128, 135` | `translateBody` on arrow and box | unaffected |
| `ui/tests/unit/convert-page.test.ts:375`, `ui/tests/e2e/layout-primitives.test.ts:64`, `tests/e2e/test_api_capture_flatten.py:513` | Convert sources, a CSS `color`, `convert_on_apply` (pattern-only matches) | unaffected: unrelated to capture marks |

**Required confirmations.**

- **AC-59.16 (`mcp-server/tests/capture.test.ts:355`) is `unaffected`.** It asserts that the annotate description contains the arrow and text example and no `circle`/`marker`, that no `suggest` action exists, and that the arrow+text example parses. D-21 keeps the description and `ANNOTATE_EXAMPLE` unchanged, no action is added, and the example's members stay in the union.
- **The AC-67 flatten byte oracle (`tests/e2e/test_api_capture_flatten.py`, `_sha256` at `:174`) is `unaffected`.** Its bodies carry only arrow, rect, highlight and text marks. `REGION_PASS` with no region marks is a no-op, and `_apply` for the existing types is unchanged (`PRODUCT_SCOPE`), so the baked bytes are identical. AC-67.15 (`:496`) checks route refs and `CaptureShotDetailOut`/`SettingsPutIn` properties, not the annotation union.

### S2 stop: two new contradictions (row 1 → `[B]` (c), human decision)

Plan §Stop Conditions S2: "The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS`: Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit." No test has been edited.

| # | Test | Why the approved design breaks it | Smallest amendment (proposed) |
|---|---|---|---|
| TA-6 (proposed) | `tests/unit/test_domain.py:306` `ENUM_MEMBERS["AnnotationType"]`, used by `test_ac_2_1_strenum_members_and_values` and `test_ac_2_11_enum_closed_set_exhaustiveness` | `REGION_MARKS` adds `AnnotationType.Pixelate` (MEU-90) and `AnnotationType.Eraser` (MEU-91); the test compares the exact ordered tuple | Append `"Pixelate"` in row 2 and `"Eraser"` in row 4: `("Arrow", "Rect", "Highlight", "Text", "Pixelate", "Eraser")`, the same order as TA-1 |
| TA-7 (proposed) | `ui/tests/unit/icon-hints.test.ts:48-57` `NO_SHOT_IDS`, used by AC-80.8 | `TOOLS_ADDED` adds two tool buttons to `TOOLBAR_BUTTONS`; with no shot they are disabled like every tool and carry `NO_SHOT_HINT`, but the test expects the bare name for any id not in its literal set | Add `'capture-tool-pixelate'` (row 2) and `'capture-tool-eraser'` (row 4) after `'capture-tool-text'` |
| G-1 (proposed) | `session-gate.ps1:106-107` (plan tooling, not a test) | `mcp-tests` runs before `mcp-build`, so it fails in a fresh worktree or tests a stale `dist` (§Baseline) | Swap the two entries so `mcp-build` runs first (RULE-1); plan §Verification §4 step 3 lists `mcp-build` before `mcp-tests` to match |

Bookkeeping that follows from TA-6 and TA-7: both files join the plan's Files Modified tables (MEU-90 and MEU-91 rows) and the `scope-paths` allow-list in `session-gate.ps1` (`allowed`, line 25), which the plan says must change together; `TEST_AMENDMENTS` gains TA-6 and TA-7.

**Decision (2026-10-16).** Mat, verbatim: `yes, all three`. Applied as plan D-24: TA-6 and TA-7 are added to `TEST_AMENDMENTS`; both test files are added to the MEU-90 and MEU-91 Files Modified tables and to the `scope-paths` allow-list in `session-gate.ps1`; G-1 moves `mcp-build` before `mcp-tests` in `session-gate.ps1` and in plan Verification §4. Row 1 is `[x]`; the `B-1` block is removed from `task.md` because the block is resolved.

## MEU-90 Red (row 2)

Command: task row 2 (pytest `-k "ac_90"` over the six Python files, MCP and UI Vitest `-t "AC-90"`, then `red-check.py` on the three receipts). Wrapper exit 0 (red-check's exit); child exits in `C:/Temp/av-kit/s39-90-red-{py,mcp,ui}.txt.exit` are `1`, `1`, `1`.

`C:/Temp/av-kit/s39-90-red-check.txt`: `red-check: 3 receipt(s), 0 problem(s)`.

**Python** (`s39-90-red-py.txt`): `8 failed, 109 deselected`. Every failure is an `E   ImportError` for a declared-new name:

```
FAILED tests/unit/test_domain_capture.py::test_ac_90_1_pixelate_annotation_and_block_bounds[AC-90.1]
FAILED tests/unit/test_capture_service.py::test_ac_90_2_pixelate_sidecar_round_trip_and_clamp[AC-90.2]
FAILED tests/unit/test_capture_adapter.py::test_ac_90_5_pixelate_bake_equals_pixelate_quant[AC-90.5]
FAILED tests/unit/test_capture_adapter.py::test_ac_90_6_region_pass_runs_before_drawn_marks[AC-90.6]
FAILED tests/unit/test_capture_bake_fixture.py::test_ac_90_8_region_fixture_reproduces_the_committed_set[AC-90.8]
FAILED tests/unit/test_capture_bake_fixture.py::test_ac_90_8_main_region_writes_only_the_region_set[AC-90.8-main]
FAILED tests/e2e/test_api_captures.py::test_ac_90_3_annotate_pixelate_round_trip_and_bounds[AC-90.3]
FAILED tests/e2e/test_api_capture_flatten.py::test_ac_90_13_flatten_bakes_the_mosaic[AC-90.13]
E   ImportError: cannot import name 'PixelateAnnotation' from 'avkit_core.domain.capture'   (AC-90.1, .2, .5, .8, .8-main, .13)
E   ImportError: cannot import name 'PIXELATE_BLOCK_DEFAULT' from 'avkit_core.domain.capture'
E   ImportError: cannot import name 'apply_region_pass' from 'avkit_infra.capture.adapter'   (AC-90.6)
E   ImportError: cannot import name 'PixelateAnnotationIn' from 'avkit_api.schemas.captures' (AC-90.3)
```

**MCP** (`s39-90-red-mcp.txt`): `Tests 1 failed | 20 skipped (21)`. AC-90.4: `AssertionError: expected false to be true` at `captureSchema.safeParse(body).success` (the Zod union refuses the pixelate).

**UI** (`s39-90-red-ui.txt`): `Test Files 5 failed (5)`, `Tests 5 failed | 101 skipped (106)`.

```
capture-region-pass.test.ts  Error: Cannot find module '../../src/renderer/src/features/capture/capture-region-pass' (declared-new; AC-90.7 x3)
capture-annotate.test.ts     AC-90.4  AssertionError: expected null not to be null   (parseAnnotateBody refuses the pixelate)
capture-toolbar.test.ts      AC-90.9  AssertionError: expected undefined to be 'capture-tool-pixelate'
capture-hit-test.test.ts     AC-90.10 AssertionError: expected 'Text 1' to be 'Pixelate 1'
capture-page.behavior.test.ts AC-90.10 AssertionError: expected null not to be null (no capture-tool-pixelate)
capture-page.behavior.test.ts AC-90.11 AssertionError: expected 'false' to be 'true' (the detail's pixelate is refused, overlay never ready)
```

**AC-90.12** is written in `ui/tests/e2e/capture-inbox.test.ts` (`installRegionSeam`, `openRegionShot`, oracle (a)/(b)/(c)); it first runs in row 3a, after the fixtures exist (`REGION_E2E_RED`).

**Amendments applied (pixelate parts only).** TA-1 and TA-6 (`Pixelate`); TA-2 (`TOOLS`, `MARKS`, the leading `expectedGroups` rule, the `regionCase` colour line, the `Pixelate` name); TA-3 (the AC-39.8 id list gains `capture-tool-pixelate`; the `HELP_TOPICS` part is MEU-91); TA-4 (`MEU65_OPTION_IDS.block`, the four type unions, `MEU65_TOOLBAR`, `MEU65_TOGGLES`, the AC-65.3 pixelate case before Text); TA-5 (`CAPTURE_TOOL_PIXELATE`, `CAPTURE_BLOCK_SIZE`, `CAPTURE_REGION_LAYER` appended at the end of `test-ids.ts`, so the MEU-51 prefix is unchanged; `CAPTURE_TOOL_ERASER` lands with the eraser in row 4; the AC-65.4 NO_OVERFLOW loop gains `'pixelate'`); TA-7 (`NO_SHOT_IDS` gains `capture-tool-pixelate`). The amended Session 34 tests (AC-65.1, AC-65.3, AC-80.8, AC-39.8) are expected Red until row 3b.

Lint: `ruff check --fix` sorted the `tools` import in the AC-90.5/AC-90.8 tests (I001). `ruff format --check` reports drift in `test_capture_adapter.py` and `test_capture_service.py` that predates this row; it is left alone.

## MEU-90 Green, backend (row 3a)

Command: task row 3a. Wrapper exit 0 (red-check's exit).

- **Domain** (`domain/capture.py`, `enums.py`): `PIXELATE_BLOCK_MIN/MAX/DEFAULT` (2, 100, 10); frozen `PixelateAnnotation(x, y, width, height, block_size)` in the `Annotation` union (ints like `rect`, size not negative, `block_size` an int in range, else `AnnotationValidationError`); `AnnotationType.Pixelate` → `"pixelate"`.
- **Sidecar** (`services/capture.py`): `_annotation_from_wire` reads a pixelate (`block_size` required, so a missing one is the existing "missing annotation field" error; extra keys ignored); `_annotation_to_wire` always writes `block_size`; `_clamp_annotation` clamps `x`/`y` as for `rect`/`highlight`. `SIDECAR_VERSION` unchanged.
- **API** (`schemas/captures.py`, `routes/captures.py`): `PixelateAnnotationIn` (`extra="forbid"` via `ApiModel`; `block_size` `Field(default=10, ge=2, le=100)`) joins `AnnotationIn`; `_annotations_from_in` builds the domain mark. `openapi.committed.json` regenerated: `+51` lines, additions only (`PixelateAnnotationIn`, its entry in both `anyOf` unions, and the two `pixelate` discriminator mappings, in `AnnotateIn` and `CaptureShotDetailOut`).
- **MCP** (`toolsets/capture.ts`): `pixelateAnn` (`.strict()`, `block_size` `.int().min(2).max(100).optional()`) joins the `discriminatedUnion`.
- **Adapter** (`capture/adapter.py`): module functions `region_clip` (`REGION_RECT`), `_apply_pixelate` (`PIXELATE_BAKE`: per-band `reduce`, `NEAREST` ×block, crop, paste at the clipped top-left) and `apply_region_pass` (region marks in list order; drawn marks skipped). `bake` runs `apply_region_pass` and then `_apply` over the list; `_apply` returns the canvas unchanged for a pixelate.
- **Fixtures:** `capture_bake_fixture.main` gains `--region` (writes only the region set). `uv run python tools/capture_bake_fixture.py --region --out ui/tests/e2e/fixtures` wrote `capture-region-pass.json` (47,392 B), `capture-region-original.png` (725 B) and `capture-region-annotated.png` (924 B).

Receipts:

```
s39-90-green-py.txt       117 passed, 1 warning in 20.61s   (the six Python files, full)
s39-90-green-openapi.txt  export_openapi --check: exit 0
s39-90-green-mcp.txt      Test Files 1 passed (1), Tests 21 passed (21)
ui/src guard              no renderer file changed
s39-90-red-build.txt      built in 4.32s
```

TA-6 (`tests/unit/test_domain.py`, not in the row command): `51 passed`.

Lint: `ruff check packages tools tests` passes after a one-line docstring shortening in `write_region_original` (E501, row 2 code; the fixture bytes do not depend on it). `ruff format --check` drift in `domain/capture.py`, `services/capture.py` and `capture/adapter.py` is present on `main` as well and is left alone.

## MEU-90 Electron Red (row 3a)

`s39-90-red-e2e.txt` (exit file `1`): `1 failed`. The seam loaded (both `REGION_IMAGE_FIXTURE` PNGs read, detail served), and the test fails at its first assertion, as `REGION_E2E_RED` predicts: the baseline renderer's annotate schema refuses the pixelate.

```
x  1 tests\e2e\capture-inbox.test.ts:2479:1 › AC-90.12 REGION_PIXEL_ORACLE: ... (2.4s)
Error: expect(received).toEqual(expected) // deep equality
- Array []
+ Array [
+   "Invalid overlay marks",
+ ]
> 2393 |   expect(errors).toEqual([])
    at openRegionShot (ui/tests/e2e/capture-inbox.test.ts:2393:18)
```

`s39-90-red-e2e-check.txt`: `red-check: 1 receipt(s), 0 problem(s)`.

## MEU-90 Green, renderer (row 3b)

Command: task row 3b. Wrapper exit 0.

- **Schema** (`capture-annotate.ts`): `pixelateSchema` (`.strict()`, integer geometry, `block_size` `.int().min(2).max(100)` and required) joins the `discriminatedUnion`.
- **Region pass** (`capture-region-pass.ts`, new): `PIXELATE_BLOCK_MIN/MAX/DEFAULT`; `isRegionMark`; `regionClip(mark, w, h)` (`REGION_RECT`; null for a drawn mark or an empty clip); `applyRegionPass(rgba, w, h, marks)`, in place, region marks in list order, `PIXELATE_QUANT` on R, G, B and A, blocks anchored at the clipped top-left with partial edge blocks.
- **Toolbar** (`capture-toolbar.ts`): `capture-tool-pixelate` (lucide `Grid3x3`, "Pixelate") after Text; `TOOL_BUTTON_IDS.pixelate`; `OptionGroup` gains `'block'`; `strokeApplies` has an explicit `pixelate` → `false`; `optionGroups` puts the `OPTIONS_BY_TOOL_V2` pixelate rule first.
- **Hit test** (`capture-hit-test.ts`): a pixelate is a filled body like a highlight (`hitBody`); `markLabel` gives `Pixelate n`; `translateBody` uses the existing origin clamp, unchanged.
- **Viewport** (`CaptureViewport.tsx`): `CaptureTool` gains `'pixelate'`; the Pixelate tool button; the `capture-block-size` number field (label, `aria-label` and `title` "Block size") when `optionGroups` includes `'block'`; `REGION_MARK_SVG` (an explicit `pixelate` branch, a `<rect>` with `fill="none"` and `stroke="none"`); `REGION_SOURCE` (the Original `<img>`'s `onLoad` reads its pixels once through an offscreen canvas, keyed by URL and size; a tainted canvas gives no source rather than a throw); `REGION_PREVIEW` (the `capture-region-layer` canvas at natural size between the `<img>` and the SVG, Original view only, repainted from the region marks of `[...annotations, preview]`: clear, copy the source inside the union box grown by 1 px, `applyRegionPass`, `putImageData` on each clipped rectangle only).
- **Page** (`CapturePage.tsx`): `blockSize` state (initial `'10'`); `changeBlockSize` mirrors `changeStroke` (an in-range int applied to a selected pixelate with a different block is one `applyHistory` step; other text is held); `createDrawnMark` has an explicit `pixelate` case (Box's zero-size rule; block from the field or the default); `inspectMark` sets the field from a selected pixelate and keeps the color candidate at the tool color; `colorBaseline` and `applyColor` skip marks without a color; `capture-block-size` joins `COLOR_FOCUS_IDS`.

Red-test correction (`ui/tests/unit/capture-hit-test.test.ts`, AC-90.10, written in row 2): the last assertion expected `translateBody(pix, 80, 0, 100, 100)` to give `x: 40`, which assumes the whole rectangle stays inside the image. `REGION_EDIT` says "existing clamp", and the existing clamp (`clampImagePoint` on the origin, as for `rect` and `highlight`) gives `x: 90`. The expectation was changed to `x: 90`; the rest of the line (size and `block_size` kept) is unchanged. This was a test-authoring error, not a contract change.

Receipts:

```
s39-90-green-ui.txt     Test Files 7 passed (7), Tests 147 passed (147)
s39-90-green-build.txt  built in 10.48s
s39-90-green-e2e.txt    35 passed (1.5m)   (full capture-inbox.test.ts)
s39-ui-src-3b.txt       git diff HEAD -- ui/src (5 files) + 1 untracked (capture-region-pass.ts)
```

AC-90.12 measured values (tolerances: (a) 1, (b) 2):

```
AC-90.12 (a) {"worst":0,"opaqueInside":true,"leaks":0}
AC-90.12 (b) {"viewWorst":0}
AC-90.12 (c) {"liveRgba":[91,105,151,255],"sourceRgb":[100,110,160]}
```

The Session 34 amended tests that were Red after row 2 (AC-65.1, AC-65.3, AC-80.8 with TA-7, AC-39.8) pass in this run, and so does the e2e AC-65.4 tool loop with `pixelate` (no tools-row overflow at the default window). Also run outside the row command: `tests/unit/icon-hints.test.ts` (in the 150-test pre-run with the row's 7 files), `tsc --noEmit` clean, and `eslint` clean on the changed renderer files.

## MEU-91 Red (row 4)

Command: task row 4. Wrapper exit 0; `red-check: 3 receipt(s), 0 problem(s)`.

```
s39-91-red-py.txt   5 failed, 97 deselected   ImportError: EraserAnnotation (AC-91.1, .2, .6), eraser_fill (AC-91.5), EraserAnnotationIn (AC-91.3)
s39-91-red-mcp.txt  1 failed | 21 skipped     AC-91.4: captureSchema refuses the eraser body (expected false to be true)
s39-91-red-ui.txt   6 failed | 106 skipped    AC-91.4 schema (null), AC-91.7 x2 (typeof eraserFill 'undefined'), AC-91.8 (TOOL_BUTTON_IDS.eraser undefined),
                                              AC-91.9 page (eraser tool null), AC-91.11 (title 'four tools')
s39-91-red-hit.txt  1 failed | 7 skipped      AC-91.9 hit test (markLabel), run outside the row command
```

Tests added:

- **Fixture** (`tools/capture_bake_fixture.py`): `REGION_IMAGE_MARKS` gains the eraser `(140, 40, 40, 30)`. `region_cases()` gains five `ERASER_SAMPLE` cases with the helpers `_eraser`, `_stems_pattern` and `_checker`:
  - `eraser-stems`: two ink stems give 4 ink pixels in a 24-pixel ring, so the mode is `REGION_BG` and the mean is not.
  - `eraser-tie`: a 6/6 tie between (9, 9, 9) and (0, 0, 0); (0, 0, 0) wins on the smaller packed value.
  - `eraser-clipped`: the rectangle hangs off the left edge.
  - `eraser-cover`: the rectangle covers the image, so the inner ring gives (1, 2, 3).
  - `pixelate-then-eraser`: a pixelate with block 3 over the boundary pattern, then the eraser `(10, 7, 6, 5)`. The pixelated ring's mode, (73, 150, 48), is not in the original palette, so the fill shows the eraser sampled the canvas after the pixelate. The first design (block 2, eraser at x 9) failed this test: the raw and mosaic ring modes were both (1, 254, 8), so it could not tell the order apart, and it was changed before writing.
  The committed `--region` fixtures are regenerated in row 5a, as in the plan.
- **Python:**
  - AC-91.1 in `test_domain_capture.py`: the enum, the union member, the fields, and the refusals for a negative size, a bool and a float.
  - AC-91.2 in `test_capture_service.py`: wire round-trip; extra keys ignored; a missing field refused; the clamp matches a rect's; the sidecar.
  - AC-91.3 in `tests/e2e/test_api_captures.py`: API round-trip; refusals for color, block_size and a missing x; the `EraserAnnotationIn` schema and discriminator; committed equals live.
  - AC-91.5 and AC-91.6 in `test_capture_adapter.py`. The independent `_ring`/`_ring_mode`/`_ref_eraser` oracle, the stems mean negative, JPEG/WebP decoded-ring parity, the pixelate-then-eraser order and its reversal, and a text mark that stays crisp in either list position.
- **MCP:** AC-91.4 in `capture.test.ts` (accepts the eraser and forwards it unchanged; refuses color and block_size).
- **Renderer:**
  - AC-91.4 in `capture-annotate.test.ts`.
  - AC-91.7 x2 in `capture-region-pass.test.ts`: parity for every eraser case against `expected` plus a comparator self-check; `eraserFill` gives stems, tie and cover.
  - AC-91.8 in `capture-toolbar.test.ts`: the id, icon and name, and `optionGroups` with the `OPTIONS_BY_TOOL_V2` rule order (pixelate tool x selected eraser stays `['block']`).
  - AC-91.9 in `capture-hit-test.test.ts` and `capture-page.behavior.test.ts`.
  - AC-91.11 in `capture-help-content.test.ts`.
- **Electron:** AC-91.10 in `capture-inbox.test.ts`, which mirrors AC-90.12 (a) with tolerance 0 and (b) with the ≤ 2 view check. It is Red only after row 5a has rebuilt the API and fixtures, so row 5a runs `--grep "AC-91.10"` first (plan line 354).

Test amendments (only the named lines; Mat approved TA-6 and TA-7 in D-24):

- TA-1: `ANNOTATION_TYPE_MEMBERS` and `ANNOTATION_WIRE` gain `Eraser`.
- TA-2: in `capture-toolbar.test.ts`, `TOOLS`, `MARKS` and the key type gain the eraser; `expectedGroups` gains the eraser rule after the pixelate rule; `regionCase` includes the eraser; the accessible name gains `'capture-tool-eraser': 'Eraser'`.
- TA-3: `HELP_TOPICS` `'four tools'` becomes `'annotation tools'`, and the AC-39.8 id list gains `capture-tool-eraser`. Casing note for row 5b: `HELP_TOPICS` is a case-sensitive `toContain` on the help source, and AC-91.11 needs the title `Annotation tools`. So the section body must also contain the lowercase phrase "annotation tools", for example "Six annotation tools: …".
- TA-4: `MEU65_TOOLBAR`, `MEU65_TOGGLES` and the AC-65.3 `cases` gain the eraser (`[]`) before Text.
- TA-5: `CAPTURE_TOOL_ERASER`; the AC-65.4 tool loop gains `'eraser'`.
- TA-6: `ENUM_MEMBERS["AnnotationType"]` gains `"Eraser"`.
- TA-7: `NO_SHOT_IDS` gains `'capture-tool-eraser'`. The AC-80.8 title still says "the 12 Capture toolbar buttons". Pixelate made 12 into 13 and the eraser makes 14. TA-7 allows only the `NO_SHOT_IDS` lines, so the title is left as it is and recorded here as a follow-up.

AC-90.12 (a) leak scope: the `REGION_IMAGE_MARKS` fixture now holds the eraser too. AC-90.12 (a) used to count every non-transparent pixel outside the pixelate as a leak, and the eraser's opaque layer pixels would count. Its leak test is now "alpha 0 outside every region mark", the same rule AC-91.10 (a) uses. The comment says so, and the pixelate comparison inside its rectangle is unchanged.

These amended tests were Red in a separate run (outside the row command; receipts `s39-91-red-amended-ui.txt`, `s39-91-red-amended-py.txt`). They stay Red until 5a or 5b:

- `capture-page.behavior.test.ts`: AC-65.2, AC-65.3.
- `capture-page.test.ts`: AC-39.8, AC-39.13.
- `capture-toolbar.test.ts`: AC-65.1 x2.
- `icon-hints.test.ts`: AC-80.8, which fails on the missing `capture-tool-eraser` element, not on a count.
- `test_domain_capture.py`: AC-34.1.
- `test_domain.py`: AC-2.1, AC-2.11.

Checks: `ruff check` is clean on the six changed Python files. `ruff format --check` passes on the three files that were clean at HEAD. The other three (`test_capture_adapter.py`, `test_capture_service.py`, `test_domain.py`) already failed `ruff format --check` at HEAD, and only the pre-existing hunks are reported, so they are left as they are. `tsc --noEmit`: every error is about the missing `eraser` type or `eraserFill`, which is Red as expected.

## MEU-91 Green, backend (row 5a)

Command: task row 5a. Wrapper exit 0.

- **Domain** (`domain/capture.py`, `domain/enums.py`): `EraserAnnotation(x, y, width, height)` checks the four values as ints with no negative size, exactly as `RectAnnotation` and `PixelateAnnotation` do. It joins the `Annotation` union and `__all__`. `AnnotationType.Eraser` has the wire value `"eraser"`.
- **Sidecar** (`services/capture.py`): `_annotation_from_wire` and `_annotation_to_wire` gain the `eraser` case, written as the four ints. Extra keys are ignored on read, and a missing field is the existing "missing annotation field" error. `_clamp_annotation` clamps an eraser exactly like a rect. `SIDECAR_VERSION` is unchanged.
- **API** (`schemas/captures.py`, `routes/captures.py`): `EraserAnnotationIn` (`extra="forbid"` through `ApiModel`; the rect schema's int geometry) joins `AnnotationIn`, and `_annotations_from_in` builds the domain mark. `openapi.committed.json` was regenerated with `export_openapi.py -o`: +95 lines, additions only. They are `EraserAnnotationIn`, its entry in both `anyOf` unions, and the two `eraser` discriminator mappings.
- **MCP** (`toolsets/capture.ts`): a `.strict()` `eraserAnn` with int geometry joins the discriminated union. The description and `ANNOTATE_EXAMPLE` are unchanged (D-21).
- **Adapter** (`adapter.py`, only the names `PRODUCT_SCOPE` allows):
  - `eraser_fill(canvas, box)` is `ERASER_SAMPLE`: the outer ring, else the inner ring; the most frequent RGB; a tie goes to the smallest packed value. It reads one crop of the ring's bounding box converted to RGB.
  - `_apply_eraser` pastes that colour at alpha 255 over the clipped rectangle.
  - `apply_region_pass` dispatches both region types in list order, so an eraser after a pixelate samples the mosaic.
  - `_apply` skips both region types.
  - `region_clip` takes either region type.
- **Fixtures:** `uv run python tools/capture_bake_fixture.py --region --out ui/tests/e2e/fixtures` rewrote all three files:
  - `capture-region-pass.json`: 82,320 B, 11 cases (the 6 pixelate cases plus the 5 row 4 eraser cases).
  - `capture-region-original.png`: 725 B, unchanged.
  - `capture-region-annotated.png`: 931 B; the bake now carries the eraser at (140, 40, 40, 30).

Receipts:

```
s39-91-green-py.txt      122 passed (6 files, incl. AC-90.8 fixture reproduction and the flatten API)
s39-91-green-openapi.txt export_openapi --check: exit 0
s39-91-green-mcp.txt     Test Files 1 passed (1), Tests 22 passed (22)
s39-ui-src-5a.txt        byte-identical to s39-ui-src-3b.txt (no ui/src change in this row)
s39-91-red-build.txt     built in 5.01s
```

Also run outside the row command: `tests/unit/test_domain.py` passes 51 (TA-6 is green), and `npm --prefix mcp-server run build` (`tsc`) is clean. `ruff check` is clean on the six changed Python sources. `ruff format --check` reports only hunks that were already at HEAD in `domain/capture.py`, `services/capture.py` and `adapter.py`, none in the new lines. `mcp-server` has no ESLint config.

## MEU-91 Electron Red (row 5a)

```
s39-91-red-e2e.txt        1 failed: AC-91.10 at openRegionShot, expect(errors).toEqual([]), received ["Invalid overlay marks"]
s39-91-red-e2e-check.txt  red-check: 1 receipt(s), 0 problem(s)
```

This is `REGION_E2E_RED` as planned. The MEU-90 renderer's annotate schema does not know `eraser`, so it refuses the detail, and the first assertion (no capture error) fails before any pixel is read. AC-90.12 is not run here: its seam now serves the eraser too, so it stays Red until row 5b.

## MEU-91 Green, renderer (row 5b)

Command: task row 5b, run from the worktree. Wrapper exit 0.

- **Region pass** (`capture-region-pass.ts`): `RegionMark` and `isRegionMark` include the eraser. `eraserFill(rgba, width, height, box)` is `ERASER_SAMPLE`, matching the adapter: the outer ring with a bounds check, else the inner ring; the most frequent RGB; a tie goes to the smaller packed value. `applyRegionPass` dispatches pixelate or erase in list order, so an eraser samples the buffer as the earlier region marks left it. The erase fill sets alpha 255. `paintRegionLayer` needed no change: its work box is already the union of region boxes grown by 1 px and clipped to the image, which covers the eraser's outer ring.
- **Schema** (`capture-annotate.ts`): a `.strict()` `eraserSchema` with int geometry joins the discriminated union.
- **Toolbar** (`capture-toolbar.ts`, `CaptureViewport.tsx`): `capture-tool-eraser` uses the lucide `Eraser` icon and the name "Eraser". It sits after Pixelate, and with no shot it is disabled with `NO_SHOT_HINT`. `TOOL_BUTTON_IDS.eraser` is added. `strokeApplies` is false for the eraser. In `optionGroups`, rule 2 (`OPTIONS_BY_TOOL_V2`: eraser tool or selected eraser gives `[]`) follows the pixelate rule.
- **Marks** (`CaptureViewport.tsx`, `capture-hit-test.ts`, `CapturePage.tsx`): an eraser renders as the same transparent `REGION_MARK_SVG` rect as a pixelate, with `data-annotation-type="eraser"`. It hit-tests as a filled body, and its label is `Eraser n`. `createDrawnMark` returns the four-int `REGION_DTO`. `inspectMark` resets the colour candidate only.
- **Help** (`capture-help-content.ts`): the section id is still `four-tools`. The title is now "Annotation tools", and the body opens with "Six annotation tools: …". The body names Pixelate and Eraser as region marks that drawn marks stay on top of, and says the eraser takes the most common colour along its border. It does not contain "Sample" (AC-81.12).

Receipts:

```
s39-91-green-ui.txt     Test Files 8 passed (8), Tests 158 passed (158)
s39-91-green-build.txt  built in 7.45s
s39-91-green-e2e.txt    36 passed (1.2m)
  AC-90.12 (a) {"worst":0,"opaqueInside":true,"leaks":0}   (b) {"viewWorst":0}
  AC-91.10 (a) {"worst":0,"opaqueInside":true,"leaks":0}   (b) {"viewWorst":0}
s39-91-green-extra-ui.txt  icon-hints, capture-action-row, layout-primitives: 3 files, 28 passed
```

`tsc --noEmit -p ui/tsconfig.json` and `eslint` on the capture feature and the changed tests are clean.

The first full run of the command failed one test, AC-91.9 (see the correction below). A rerun was then launched from the main checkout by mistake. `npm --prefix ui` resolved to `P:/av-kit/ui`, so it tested, built and ran E2E on `main` (7 files, 143 tests, 34 E2E, no AC-91.10). Those receipts were discarded and overwritten by the worktree run above. `git status` on main was clean afterwards; the build output there is gitignored.

Red-test correction (AC-91.9, a test-authoring error, not a contract change): the deselect step clicked at (190, 190). On the 8 x 8 test image at 25 css px per pixel, `mapPointerWithView` rounds 190 / 25 = 7.6 to 8, which is off the image. So `event.image` is null and the page ignores the pointerdown before the Select branch runs, and the chip stayed pressed. The click is now at (175, 175), which maps to pixel 7: on the image, off the mark (25..150 x 25..125 css). The test passes, and the deselect really happens. A probe run before the fix showed the chip still pressed after the 190 click with the Select tool active.

Follow-up, not changed (outside this row): AC-90.10 uses the same (190, 190) click, but it clicks Undo just before, and Undo clears the selection (`CapturePage.tsx` `onUndo`). So its "a click on empty image deselects" check passes without the click doing anything. For a real check, the mark has to be selected before the click, and the click has to be on the image, for example at (175, 175).

## Session gate (row 6)

Command: task row 6 (`session-gate.ps1`, fail-fast), run from the worktree with `ELECTRON_RUN_AS_NODE` unset and `RECEIPTS_DIR=C:/Temp/av-kit`. It took five runs. Run 5 passed, wrapper exit 0.

Run 5 (receipts copied to `C:/Temp/av-kit/s39-gate-run5/`):

| Step | Stage | Exit | Decisive line |
|------|-------|------|---------------|
| identity-before | identity | 0 | `tested_state 90bb40977e487f4893a1c586c2c20b8f78ef105f+6ff3a8477070c9f7edc18f339b35c07c3ae1c8786ccfa03723d3a008d6f7b986` |
| py-types | static | 0 | pyright 0 errors |
| py-lint, py-lint-tools | static | 0 | ruff check clean |
| ui-types, ui-lint, mcp-types | static | 0 | tsc and eslint clean |
| task-contract | static | 0 | task table valid |
| scope-ast | static | 0 | `scope-ast: adapter outside PRODUCT_SCOPE: 0 problem(s) (base 90bb409…)` |
| scope-paths | static | 0 | `changed paths: 47 outside scope: []` |
| py-tests | full | 1, accepted | `2 failed, 687 passed`; `py-tests baseline rule: failed=2 outside_baseline=[] errors=0` (AC-24.10, AC-25.10 packaging, the §Baseline set) |
| ui-tests | full | 0 | `Test Files 88 passed (88)`, `Tests 854 passed (854)` |
| mcp-build, mcp-tests | full | 0 | `Test Files 23 passed (23)`, `Tests 413 passed (413)` |
| ui-build, ui-harness-build, ui-picker-stub | full | 0 | built |
| openapi | full | 0 | `export_openapi --check` exit 0 |
| state-render | full | 0 | `Drift check passed — SSOT loaded (91 MEUs, 12 phases)` |
| ui-electron | runtime | 0 | `146 passed (2.9m)` |
| e2e-repeat | runtime | 0 | `20 passed (1.1m)`: AC-90.12 and AC-91.10 10× each; every run `{"worst":0,"opaqueInside":true,"leaks":0}` and `{"viewWorst":0}` |
| identity-npm | identity | 0 | `@playwright/test@1.62.1`, `electron@42.9.3` |
| identity-after | identity | 0 | `before` equals `after`, the `tested_state` above |

Compared with the §Baseline counts: py-tests 674 → 687 passed with the same two failures; ui-tests 839 → 854; mcp-tests 411 → 413; capture-inbox 34 → 36.

The earlier runs:

1. **Run 1, py-types failed.** pyright refused `eraser_fill`'s `Image.load()` pixel access (an Optional `PixelAccess`, and a pixel type of `float | tuple`). Fix (D-29, a product change after row 5a, inside `PRODUCT_SCOPE`): `eraser_fill` now reads the RGB crop's bytes with `area.tobytes()` and indexes `((y - top) * area.width + (x - left)) * 3`. Afterwards pyright reports 0 errors, `test_capture_adapter.py` passes 27, and a fresh `--region` run into a temporary folder is byte-identical to the three committed fixtures, so the fill values did not change.
2. **Run 2, task-contract exit 3.** `RECEIPTS_DIR` was not set in the shell that launched the gate. Every later run exports `RECEIPTS_DIR=C:/Temp/av-kit`. No file changed.
3. **Run 3, ui-electron: 2 failed, 144 passed.** `download-queue.test.ts` AC-49.25 and `transcript-queue.test.ts` W2-5. An isolated run of those two files then failed AC-49.26, with the A-4 diagnostics `"DL-1" was moved to position 4 of 4.` (the target was position 3), `focused: true` and `visibility: visible`. Repeated alone, both passed: AC-49.25/26 8/8 (`s39-gate-flake-drag.txt`), W2-5 4/4 (`s39-gate-flake-w25.txt`).
4. **Run 4, ui-electron: 1 failed, 145 passed.** `convert-queue.test.ts` AC-49.29: the PUT body was `[job-2, job-3, job-4, job-1]` where `[job-2, job-3, job-1, job-4]` was expected. Repeated alone it passed 20/20 (`s39-gate-flake-4929.txt`).

Runs 3 and 4 failed on drag-reorder tests outside Capture. No change in this session reaches the queue pages: outside the capture feature it only adds enum members, OpenAPI schemas and capture test ids. Both misses drop the row exactly one place too far while the window has focus, and they show up only in the full 146-test run. This matches the open known issue `DOWNLOAD-QUEUE-DRAG-OVER-MISS`. I put the evidence to Mat, who chose "Re-run, hands off" (D-30). The known issue is reopened with these misses (it now also covers convert-queue and transcript-queue). The plan's S6 rule applies to the Capture `e2e-repeat` step, which never failed.

`tested_state` was rechecked with `identity.py --state-only` after the known-issue edit, which sits in an excluded path, and it is unchanged. The recheck must also run with `ELECTRON_RUN_AS_NODE` unset, because `runtime_identity` binds that variable.

## Hub reconciliation (row 7)

Command: task row 7, run from the worktree. Wrapper exit 0.

Edits (hub files only; `INPUT_IDENTITY` excludes all of them):

- `docs/build-plan/09-screenshot-capture.md`:
  - "Four tools only" becomes "Six tools only", and "hide the four tools" becomes "hide the six tools".
  - The help topics line (`:157`) and the Phase 9 exit line say "six tools".
  - The `AnnotationType` row gains `Pixelate` and `Eraser`.
  - The DTO table gains the `pixelate` and `eraser` rows (`REGION_DTO`).
  - The mark list says "all mark types".
  - A Plan row after the §Pixelate mark Tests row records `REGION_PASS` and `PIXELATE_BLOCK` (D-10, D-11, D-12). A Plan row after the §Eraser mark Tests row records `ERASER_SAMPLE` (D-10, D-13).
- `docs/build-plan/06-gui.md`: the help row says "annotation tools", and the Capture row says "arrow/box/highlight/text/pixelate/eraser".
- `docs/build-plan/gui-actions-index.md`: `capture:tool_pixelate` and `capture:tool_eraser` after `capture:tool_text`.
- `docs/build-plan/build-priority-matrix.md`: rows 9.23 (MEU-90) and 9.24 (MEU-91) after 9.17.
- `docs/BUILD_PLAN.md` Phase 9 line: "MEU-90–91 bound to capture-new-marks." That line sits inside the `meu-status:phase-tracker` AUTOGEN region. My first attempt edited it by hand, and `render --check` failed with `Drift check failed — regions out of sync: phase-tracker (BUILD_PLAN.md)`. Following the plan's "AUTOGEN regions only through `meu_status.py render`", I reverted that edit. The sentence now goes on phase 9's `note` in `.agent/context/meu-status.yaml`, where Session 36 put its own binding, and `meu_status.py render` wrote the line. The rendered `BUILD_PLAN.md` diff is that one line, and `meu-registry.md` is byte-identical.

Receipts:

```
s39-hub-rg.txt       every edit present: 09 :46, :157, :391, :889 and the MEU-90/91 rows; gui-actions-index :80, :81;
                     matrix :75, :76; BUILD_PLAN.md :53 "MEU-90–91 bound to capture-new-marks."
s39-hub-four.txt     one line: 09 :373 ("Box / highlight ... four tools"), the historical HEAD :371 shifted by the two DTO rows
s39-state-render.txt Drift check passed — SSOT loaded (91 MEUs, 12 phases), rendered regions match on-disk content
s39-hub-audit.txt    gui-actions-audit: Test Files 1 passed (1), Tests 4 passed (4)
```

The plan expected the historical lines `:358` and `:371` to remain. At HEAD, `:358` no longer contains "four tools", so only `:371` is left, which still meets the condition. The capitalised "Four tools only" in the not-built row at `:840` does not match the case-sensitive `rg`. It already says that Pixelate and Eraser are added by MEU-90/91, so it is left as it is.

## Closeout H1 (rows H1-1 to H1-6b)

The H1 receipts are snapshotted in `C:/Temp/av-kit/s39-closeout/`, because other sessions write the same receipt names in `C:/Temp/av-kit`. The H1-2 gate receipts are in `C:/Temp/av-kit/s39-gate-h1/`.

- **H1-1**: `unchecked implementation rows: []`.
- **H1-2**: the session gate re-ran after the row 7 hub edits. Every step exits 0, with the same counts as run 5 (py-tests 2 failed / 687 passed under the baseline rule; ui-tests 854; mcp-tests 413; Electron `146 passed (2.9m)`; e2e-repeat `20 passed (1.2m)`, every run `{"worst":0,"opaqueInside":true,"leaks":0}` and `{"viewWorst":0}`). scope-paths reports `changed paths: 54 outside scope: []`; the extra 7 paths are the row 7 hub files and the SSOT. `identity-before` and `identity-after` print the same `tested_state` as row 6, `90bb409…+6ff3a847…b986`, because every file touched since row 6 is a project artifact that `INPUT_IDENTITY` excludes.
- **H1-3**: `meu_status.py update` set MEU-90 and MEU-91 to `ready_for_review` with `execution_plan` set to this plan. The BUILD_PLAN total reads `74 + 2🟡 + 1🚫`. `current-focus.md` now opens with Session 39's state. `render --check`: `Drift check passed — SSOT loaded (91 MEUs, 12 phases)`.
- **H1-4**: `added: ['EraserAnnotationIn', 'PixelateAnnotationIn'] removed: [] changed without a new-schema reference: []`, exit 0.
- **H1-5**: read `.agent/context/handoffs/TEMPLATE.md` and the MEU-67 exemplar. The handoffs follow the Session 36 layout (evidence.v1 JSON records, a Decision Log `decision_log` fence).
- **H1-6**: the two handoffs are written. The validator reports 19 AC rows and 4 decisions for MEU-90 (D-25, D-26, D-27, D-30), and 17 AC rows and 2 decisions for MEU-91 (D-28, D-29). For both: `all 7 plan AC(s) present`, no `[B]` rows.
- **H1-6a**: `OK: all 7 plan AC(s) present in the handoff`, for both.
- **H1-6b**: with `ELECTRON_RUN_AS_NODE` unset, `identity.py --state-only` re-derives the H1-2 `tested_state`, and `durable_evidence.py --require-full` passes against it for both handoffs (`OK: durable evidence records`).

## Execution review and closeout H2 (rows H1-7 to H2-3)

**H1-7, the execution review.** Codex CLI `gpt-6.1-sol` (high, ReviewReadOnly), loop `s39-execution-2026-10-16-capture-new-marks`. Mat was told that Codex is metered.

- **Attempt 1:** returned `approved` with one Low finding, but checklist IR-5 was marked `partial`. The dispatcher refused it before the ledger recorded anything: `checklist_results/5/result: 'partial' is not one of ['pass', 'n/a']`. Copies are preserved as `C:/Temp/av-kit/dispatch/s39-exec-review-report-r1-refused.md` and `s39-exec-r1-refused-final.json`. The verdict was not edited.
- **Attempt 2 (`dispatch-20261016192157-3185`):** the same round, resubmitted with the refusal and the schema rule quoted and no verdict preference. Result: `OK: recorded round 1 verdict=approved agent='gpt-6.1-sol' blocking=0 intent_achieved=yes`; receipt `recorded=True`. F1 (Low, non-blocking) says the AC-90.10 deselect sub-check is vacuous. It is deferred, not corrected.
- **Report:** copied to `.agent/context/handoffs/2026-10-16-capture-new-marks-implementation-critical-review.md`, verbatim except for an appended Orchestrator Note. The note corrects one line ("The user authorized evidence reuse"): the reuse permission was in the author's resubmission notice, not from Mat. Both handoffs' Corrections Applied now say "none needed". The reviewer section was left for `/validation-review`, as in Session 36.

**H1-7a:** `OK: review_mode=execution; round 1 of 6; verdict=approved; open findings=0`.

**H1-7b:** `OK: approved at round 1 of 6, 0 open blocking findings`. Both receipts are copied to `C:/Temp/av-kit/s39-closeout/`.

**H2-2, the reflection and SSOT.**
- `CAPTURE-PIXELATE-TOOL` and `CAPTURE-ERASER-TOOL` are set to `resolved`, with verification pointing at the MEU-90 and MEU-91 handoffs. MEU-90 and MEU-91 are set to `approved` through `meu_status.py update`. `known-issues.md` and the registry were rendered.
- The reflection check refused twice before passing. Neither fix changed meaning:
  1. Plan D-15's `chosen` text contained the literal `<img>`, which matches the placeholder pattern `<[a-z-]+>`. It now reads "img element", in the plan and the reflection. Plan `*.md` files are `PROJECT_ARTIFACTS`, so `tested_state` is unaffected.
  2. The D-62 enrichment entry used indentless sequences and a wrapped single-quoted `reasoning`, which are outside the validator's YAML subset. The sequences were re-indented and the scalar joined onto one line, as Session 36 did in `bb0ef7e`. `yaml.safe_load` of the whole file is identical before and after.
- Result: `OK: all 15 template section(s) present; all 7 required schema field(s) emitted; 3 design rule(s), all sourced; 31 recorded decision(s) reconciled against 32 Decisions Log row(s)`, `known-issues.md is up-to-date`, `Drift check passed`.

**H2-3:** the metrics row was appended, and the check exited 0.
