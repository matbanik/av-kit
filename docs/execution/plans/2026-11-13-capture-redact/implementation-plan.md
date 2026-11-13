---
project: "2026-11-13-capture-redact"
date: "2026-11-13"
source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md#session-44--capture-redact-meu-103--p2"
grouping_source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md"
meus: ["MEU-103"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture redact (Session 68)

> **Project:** `2026-11-13-capture-redact`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Redact mark (`:922-934`, anchor `redact-mark`, MEU-103), with the build priority matrix row 9.29 (`docs/build-plan/build-priority-matrix.md:127`).
>
> **Source request.** On 2026-10-29 Mat accepted the capture annotation editor synthesis ("all recommendations are accepted", grouping D-158). This is the grouping's first session after the 2026-11-12 planning notes (grouping §9), which run the five capture sessions as Sessions 68 to 72 (D-674) and give `redact` the half-open crop rule (D-675). The 09 Crop row (`:934`) is uncommitted at plan time and in `baseline-dirty.txt`.
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 2 (`.agent/context/handoffs/2026-11-13-capture-redact-plan-critical-review.md`). Before the review Mat set the execution review budget to 50M (USER_EXPLICIT 2026-11-13 'set token buget for 50M and add 2 more round just so we do no run into limits') and said to execute (USER_EXPLICIT 2026-11-13 'upon plan approval auto proceed with execution'), so execution starts when the plan review approves.

## Goal

**Goal anchor:** Session 68 adds a solid `redact` mark across every layer: the Annotation union and sidecar, the region-pass bake and its TS preview, the crop, the API, OpenAPI and MCP schemas, and a GUI Redact tool. The tool is Solid by default and has a Pixelate toggle. The session also renames Eraser to "Smart eraser" in the GUI, keeping the JSON type `eraser`.

Four things are missing today (`3c5676f`):

1. **No solid mark.** The Annotation union (`packages/core/src/avkit_core/domain/capture.py:412-419`) has six members. The only way to hide pixels is Pixelate, which can leave a short secret readable at small block sizes, and a user can't see that happen.
2. **No layer knows `redact`.** These all reject it today:
   - the sidecar reader `_annotation_from_wire` (`services/capture.py:350`);
   - the region pass (`avkit_infra/capture/adapter.py:269`);
   - the API's `AnnotationIn` (`schemas/captures.py:149`);
   - the MCP zod union (`mcp-server/src/toolsets/capture.ts:182`);
   - the UI's `Annotation` union (`capture-annotate.ts:84`).
3. **One tool per mark.** The toolbar has separate Pixelate and Eraser buttons (`capture-toolbar.ts:48-49`), and Eraser's name doesn't say that it fills with the surrounding colour.
4. **No editor outline.** A region mark draws no outline of its own in the editor, so a redaction is hard to find on a dark image.

The session ends when:
- every 09 §Redact mark rule holds, each with a behaviour test (the Crop row included);
- the session gate's last line is `session-gate: all steps exit 0`;
- MEU-103 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-13). No payload is oversized: the domain, service, adapter, schema, route, MCP and UI capture files were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, `.agent/context/harness.local.md` Claude Code block). Mat's 2026-11-13 messages authorize execution once the plan review approves (§Status). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s68-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s68\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. GUI references are not shipped (`gui-refs-not-shipped`).
- **Decisions:** by Mat's direction (USER_EXPLICIT 2026-11-13 'if decisions are needed send them to Fable subagent and accept answers as human ruling'):
  - a decision for Mat goes to a Fable subagent as a Decision Brief that includes its do-nothing option;
  - the subagent's answer is recorded as a human ruling by delegation, quoting that message and naming the subagent as the source.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s68-plan-canonical-2026-11-13-capture-redact` and `s68-execution-2026-11-13-capture-redact`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps: plan 5 and execution 8. Mat added two rounds to the ledger defaults of 3 and 6 (D-688), so each loop is lifted with `review_ledger.py continue --rounds 2`, quoting his words.
  - Token budgets: the execution loop opens at 50,000,000 (`begin --token-budget`). The plan loop keeps the 10.5M default; if its token stop fires, it is lifted with `continue --tokens`, quoting the same words.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit`, then copied byte for byte to its canonical path, and the `--review-state-only` receipt is rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-679 to D-688, AC-103.1 to AC-103.25, and the mechanism ids in §Single-statement contracts.
  - They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and they write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header and the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3) and asks for bare words in its Recheck cells (`fixed`, `open`; Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - the live MCP audit or `--update-baseline`;
  - `npm run dist`;
  - an `approved` verdict authored by the implementer.
- **No network:**
  - no test or row reaches YouTube or the network;
  - nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called);
  - no other program is stopped.

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-103 | `.agent/context/handoffs/2026-11-13-capture-redact-MEU-103-handoff.md` | only |

Rolling reviews: `.agent/context/handoffs/2026-11-13-capture-redact-plan-critical-review.md` and `.agent/context/handoffs/2026-11-13-capture-redact-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | Type-only names: `RedactAnnotation` outside the union, `AnnotationType.Redact`, the TS `RedactAnnotation` and `RedactMode` types, the MEU-103 test ids | shared |
| WP-3 | 2, 3 | Red, then Green | shared |
| WP-4 | 4, 5 | The region fixture's redact cases, and the 09, 06 and gui-index spec text | shared |
| WP-5 | 6 | Status and grouping | shared |
| WP-6 | H1, H2 | Gate, handoff, review, reflection, next prompt | compact_continue |

## User Review Required

**Carried rulings:**
- D-158 (USER_EXPLICIT 2026-10-29 "all recommendations are accepted", grouping §8 `:141`) accepts the synthesis that 09 §Redact mark encodes.
- D-159 and D-160 (autonomous, Local Canon, `:142-143`) are carried, because the decision probe returns them.
- D-674 and D-675 (autonomous, grouping §9.8) set the session number and the crop rule.
- D-676 to D-678 belong to later sessions.

**Rulings at plan time (D-688).** On 2026-11-13 Mat:
- set the execution review budget to 50M;
- added two rounds to each review loop;
- said to execute once the plan review approves;
- sent every further decision to a Fable subagent, whose answer is accepted as his ruling.

No open decision remains for the plan gate. An AC or contract change during execution goes as a Decision Brief to the Fable subagent (S12). Its do-nothing option is "record it as a departure and keep the approved text".

**Network.** Recommendation: none, because nothing here fetches. The do-nothing option is the same. There is no brief.

**Token estimate.** Calibrated against:
- Session 38 `capture-new-marks`, a two-mark slice across the same layers: plan approved at r2, execution at r1;
- Session 43: plan 14.9M over 3 rounds, execution 21.0M;
- Session 67: plan 10,193,204 over 2 rounds, execution 13,248,892 over 2 rounds.

This session is one MEU across seven layers plus a GUI rename:
- plan review: about 11M for round 1 and about 5.5M for one recheck;
- execution review: about 13M for round 1, so the Session 60 RULE-5 figure would be 32.5M (13M × 2 plus a recheck at about 6.5M). Mat set 50M.

**Word meanings.**
- *A redact* is an `Annotation` of type `redact`.
- *Solid* and *Pixelate* are the two values of the Redact tool's mode (`RedactMode`).
- *A redaction mark* is a `redact` or a `pixelate` mark.
- *The region pass* is REGION_PASS step 1 (`apply_region_pass` in Pillow, `applyRegionPass` in TS): every region mark in list order, before the drawn marks.

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `REDACT_TYPE` | `RedactAnnotation` is a frozen dataclass `{x: int, y: int, width: int, height: int, color: str = "#000000"}` whose `__post_init__` applies `_require_int` to the four numbers, refuses a negative width or height with `redact size must not be negative`, and normalises `color` through `_require_color`, re-raising its `ValidationError` for a non-str or empty colour as `AnnotationValidationError` (AC-103.2). `AnnotationType.Redact = "Redact"` is appended after `Eraser`, and `AnnotationType.to_wire`'s explicit mapping gains `AnnotationType.Redact: "redact"`. `RedactAnnotation` is appended last in the `Annotation` union (D-679). | `domain/capture.py`, `domain/enums.py` |
| `REDACT_WIRE` | `_annotation_from_wire` reads a `redact` entry with exactly `x`, `y`, `width`, `height` and `color` (`color` is required in the sidecar, D-682). `_annotation_to_wire` writes those five keys. A sidecar with no redact entry reads and writes the same bytes as at baseline. | `services/capture.py` |
| `REDACT_CLAMP` | `_clamp_annotation` clamps a redact's box into the image as it does a pixelate's and an eraser's, and the result is a fixed point of the clamp (D-485). | `services/capture.py` |
| `REDACT_CLIP` | `clip_mark` gains `case RedactAnnotation(): return _clip_half_open(...)` before the `assert_never` arm, and the `_HalfOpenMark` TypeVar gains `RedactAnnotation` (MARK_CLIP_BOX, D-486, D-675). | `domain/capture.py` |
| `REDACT_BAKE` | `apply_region_pass` pastes `(*_color_rgb(color), 255)` over `region_clip(mark)` for each redact, in list order with the other region marks. `region_clip` accepts a redact, and `_apply` returns the canvas unchanged for a redact, as for the other region marks. | `avkit_infra/capture/adapter.py` |
| `REDACT_FIXTURE` | `region_cases()` appends `redact-` cases after `*crop_cases(),`, and earlier cases keep their names, order and bytes (D-685). | `tools/capture_bake_fixture.py`, `ui/tests/e2e/fixtures/capture-region-pass.json` |
| `REDACT_PREVIEW` | `applyRegionPass` fills a redact's `regionClip` box with `displayHex(color)`'s RGB at alpha 255, in list order. `RegionMark` gains the redact type. | `capture-region-pass.ts` |
| `REDACT_API` | `RedactAnnotationIn` has `extra="forbid"`, `type: Literal["redact"]`, `StrictInt` `x` and `y`, and `width` and `height` `StrictInt` with `ge=0`, so `"1"` and `1.5` give 422 as the input matrix says (`ApiModel` forbids extras but is not strict). Its `color` matches `COLOR_PATTERN` and defaults to `"#000000"` (D-682). It is a member of the `AnnotationIn` discriminated union, after the eraser. `_annotations_from_in` maps it to `RedactAnnotation`, and `openapi.committed.json` is regenerated. | `schemas/captures.py`, `routes/captures.py`, `openapi.committed.json` |
| `REDACT_MCP` | `redactAnn` is a `.strict()` zod object `{type: literal "redact", x, y: int, width, height: non-negative int, color?: string}` placed after `eraserAnn` in the annotate union. The tool forwards it unchanged, and the server's 422 decides the colour (D-682). | `mcp-server/src/toolsets/capture.ts` |
| `REDACT_TOOL` | `CaptureTool`'s `'pixelate'` becomes `'redact'`, so the union keeps 8 members (D-679). TOOLBAR_BUTTONS replaces `capture-tool-pixelate` with `capture-tool-redact` `{icon: EyeOff, name: 'Redact'}` in the same slot, and `TOOL_BUTTON_IDS.redact` is that id. A drawn box under Solid gives `{type: 'redact', …, color: '#000000'}`; under Pixelate it gives the pixelate mark with the current block size. The tool has no letter (§9.3). | `CaptureViewport.tsx`, `capture-toolbar.ts`, `CapturePage.tsx` |
| `REDACT_MODE` | The page holds `redactMode: RedactMode` (`'solid' \| 'pixelate'`), which is `'solid'` on mount and is not persisted. The options row shows a `SegmentedControl` (size `sm`, label `Redact mode`, test ids `capture-redact-mode`, `capture-redact-solid` and `capture-redact-pixelate`) whenever `optionGroups` includes the new `OptionGroup` `'mode'` (D-680). | `CapturePage.tsx`, `CaptureViewport.tsx`, `capture-toolbar.ts` |
| `MODE_GROUPS` | `optionGroups(tool, selected, mode = 'solid')`, first matching rule: crop gives `[]`; a selected redact gives `['mode']`; a selected pixelate gives `['mode', 'block']`; the redact tool with nothing selected gives `['mode']` under Solid and `['mode', 'block']` under Pixelate; eraser (tool or selected) gives `[]`; otherwise today's color, text and stroke rules apply. `strokeApplies` swaps `'pixelate'` for `'redact'` (D-680). | `capture-toolbar.ts` |
| `MODE_SWAP` | When a redaction mark is selected and the user picks the other mode, the mark is replaced in place by `applyHistory(replaceAt)` as one undo step. The new mark keeps the box. Solid gives the color `#000000`; Pixelate gives the page's current block size. With nothing selected, the pick only sets `redactMode`. Picking the mode already checked is a no-op (D-680). | `CapturePage.tsx` |
| `SMART_ERASER` | `ToolbarButtonSpec` gains an optional `hint`. The eraser button is `{icon: Eraser, name: 'Smart eraser', hint: 'Covers an area with the surrounding colour'}`. `ToolbarIconButton`'s tooltip reads the name, then ` (shortcut)` when there is one, then `: hint` when there is one. The aria-label stays the name. Mark chips read `Smart eraser N`, and the JSON type stays `eraser` (D-683). | `capture-toolbar.ts`, `ToolbarIconButton.tsx`, `capture-hit-test.ts` |
| `REDACT_OUTLINE` | A redaction mark's SVG element (REGION_MARK_SVG) draws a 1 px dashed outline (`stroke-dasharray`) in the editor's Original view only. The Annotated view and every bake draw none (D-684). | `CaptureViewport.tsx` |
| `REDACT_HIT` | `BoxMark` and `isBoxMark` (`capture-transform.ts:14`, `:24`) gain `redact`, and `hitBody` (`capture-hit-test.ts:156`) treats a redact's body as a box like the other region marks. The MEU-100 handles move and resize it as a box, and `markLabel` gives `Redact N` (D-683). | `capture-hit-test.ts`, `capture-transform.ts` |
| `REDACT_HELP` | The help body names Redact (Solid by default, Pixelate as its other mode) and Smart eraser, and its resize sentence includes redact (D-686). | `capture-help-content.ts` |

### Pins that move

| Row | Test | Today | After |
|---|---|---|---|
| 1 | `tests/unit/test_domain.py:316-317` | `AnnotationType` members end at `"Eraser"` | the members end `"Eraser", "Redact"`, and the comment names Session 68, D-679 |
| 1 | `tests/unit/test_domain_capture.py:32-41` (`ANNOTATION_TYPE_MEMBERS`, `ANNOTATION_WIRE`) | six members | `Redact` / `"redact"` appended |
| 2 | `tests/unit/test_domain_capture.py:864-876` (AC-130.6) | `samples` has six classes and must equal `get_args(Annotation)` | a `capture.RedactAnnotation(x=15, y=25, width=40, height=30)` sample is added; the set equality and the per-kind `kept` and shift assertions stay. It fails in the pins receipt until row 3 puts `RedactAnnotation` in the union |
| 2 | `tests/unit/test_capture_service.py:1208`, `:1247` | the clamp's `kinds` tuple has six kinds | `"redact"` appended (AC-103.5) |
| 2 | `ui/tests/unit/capture-toolbar.test.ts:87-88`, `:170-172`, `:174-201`, `:190-192` | `capture-tool-pixelate` 'Pixelate'; `capture-tool-eraser` 'Eraser'; `optionGroups('pixelate', …)` | `capture-tool-redact` 'Redact'; 'Smart eraser' with its hint; `optionGroups('redact', …, mode)` per MODE_GROUPS; the file's `TOOLS` list, `expectedGroups` helper, eight-tool key list and icon expectation follow D-679 and MODE_GROUPS |
| 2 | `ui/tests/unit/capture-page.behavior.test.ts:1445-1446`, `:1460-1461`, `:1563-1564`, `:1628-1640`, `:1711-1721`, `:2971-2972` | Pixelate and Eraser button ids, names, groups and chips; the pixelate drawing test clicks `capture-tool-pixelate` | the Redact id and name; `Smart eraser` and `Smart eraser 1`; the pixelate drawing test clicks `capture-tool-redact`, then `capture-redact-pixelate`; the tool map gets `['capture-tool-redact', 'redact']`; `HINT_OVERRIDE` (`:1453`, read at `:1509`) gains `'capture-tool-eraser': 'Smart eraser: Covers an area with the surrounding colour'` |
| 2 | `ui/tests/unit/capture-page.test.ts:274-275` | the viewport source contains `capture-tool-pixelate` | it contains `capture-tool-redact` and not `capture-tool-pixelate` |
| 2 | `ui/tests/unit/icon-hints.test.ts:54-55` (`NO_SHOT_IDS`), `:61` (`HINT_OVERRIDE`) | `capture-tool-pixelate`; no eraser override | `capture-tool-redact`; `HINT_OVERRIDE['capture-tool-eraser'] = 'Smart eraser: Covers an area with the surrounding colour'` |
| 2 | `ui/tests/unit/capture-hit-test.test.ts:245` | `markLabel(eraser, 0)` is `'Eraser 1'` | `'Smart eraser 1'` |
| 2 | `ui/tests/unit/capture-help-content.test.ts:103` | tool names `'Pixelate', 'Eraser'` | `'Redact', 'Pixelate', 'Smart eraser'` |
| 2 | `ui/tests/e2e/capture-inbox.test.ts:876` | the tool loop names `'pixelate'` | it names `'redact'` |
| 2 | `ui/tests/e2e/capture-inbox.test.ts:2687` (AC-90.12 (c)) | clicks `capture-tool-pixelate` | clicks `capture-tool-redact`, then `capture-redact-pixelate` |

Before writing, row 1 sweeps `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` for these names and records the hits in `s68-anchors.txt`:
- every caller and test of `clip_mark`, `_clamp_annotation`, `apply_region_pass`, `region_clip`, `_annotation_from_wire` and `_annotation_to_wire`;
- every caller and test of `optionGroups`, `TOOL_BUTTON_IDS`, `TOOLBAR_BUTTONS`, `markLabel` and `applyRegionPass`;
- every literal `capture-tool-pixelate`, `capture-tool-eraser`, `'Eraser'` and `'Pixelate'`;
- every pin by name, order, adjacency or exact signature on the Annotation union, the enum, the zod union, the toolbar list and the help list.

This follows Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1 and Session 66 RULE-1. A pin found there and missing from this table goes into the handoff as a departure. The plan-time sweep found the rows above (`C:/Temp/av-kit/s68/pin-sweep.txt`).

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| A redact's `color` | the API body (`COLOR_PATTERN`, default `#000000`), the MCP body (passed through), the GUI (`#000000`), the sidecar on disk | `_require_color`, the sidecar, `_color_rgb` (Pillow), `displayHex` (TS) | `RedactAnnotation` refuses an invalid colour, so the sidecar holds only a named colour or `#RRGGBB`. AC-103.2 drives a lone surrogate, control characters, `""`, `#000` and a trailing space through the dataclass, the API (422) and a sidecar read from disk (refused). |
| A redact's box | the API body, the MCP body, the GUI drag and handles, the crop | the clamp, `clip_mark`, `region_clip` (Pillow and TS) | REGION_RECT is half-open. A negative size is refused, and the clamp and the clip keep it a fixed point. |
| `redactMode` | the SegmentedControl | `createDrawnMark`, `optionGroups`, MODE_SWAP | page state only, not persisted, and Solid on mount |

These functions sit between an API body and a baked pixel, and AC-103.10 traces all of them with a recording wrapper (Session 55 RULE-3):
- `RedactAnnotationIn` and `_annotations_from_in`;
- the annotate service and `_clamp_annotation`;
- `_annotation_to_wire`, the sidecar file and `_annotation_from_wire`;
- the bake's `apply_region_pass` and `_color_rgb`.

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/09-screenshot-capture.md` | `:284` AnnotationType row: `Redact` appended. A `RedactAnnotation` DTO row goes after the eraser row (`:348`). `:826` REGION_PASS reads "region marks (pixelate, eraser, redact)". A `> **Delivered (Session 68).**` note goes after the Crop row (`:934`), before `:936`, naming the mechanism ids, AC-103.1 to AC-103.25 and the plan folder. |
| `docs/build-plan/06-gui.md` | `:943` the viewport tool list reads `…/text/redact/smart eraser` |
| `docs/build-plan/gui-actions-index.md` | `:88` `capture:tool_pixelate` becomes `capture:tool_redact` "Redact tool (Solid / Pixelate)"; `:89` `capture:tool_eraser` reads "Smart eraser tool" |

### MEU-103 `capture-redact-mark`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `POST /captures/{id}/annotations` | `RedactAnnotationIn` | Pydantic `extra="forbid"`: an unknown field, a bad type, a negative size or a colour outside `COLOR_PATTERN` gives 422 in the error envelope |
| API, unknown `type` | a discriminator not in `AnnotationIn` | 422 (the "older server" half of the Mark row: a server without `redact` refuses it the same way) |
| MCP `avkit_capture annotate` | `redactAnn` `.strict()` | a zod error before any HTTP call |
| Sidecar on disk | a `redact` entry | `_annotation_from_wire` refuses a missing or extra key, or a bad value, as it does for every type |
| GUI | the drawn box, the mode control | not a trust boundary; the GUI writes through the API |

The OpenAPI snapshot changes by the `RedactAnnotationIn` schema and its place in the union. The MCP audit baseline (`.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json`) is keyed by tool, action and status. `annotate` stays one action, so the baseline doesn't change, and the gate's scope check refuses the file.

**Input matrix (Session 64 RULE-1).** These cases come from reading the files named in each row at `3c5676f` (`C:/Temp/av-kit/s68/pin-sweep.txt`):

| Input | Domain | API | MCP | Sidecar from disk | Expected |
|---|---|---|---|---|---|
| `{x, y, width, height}` | `#000000` default | 201/200, stored `#000000` | forwarded with no colour | — (required) | black box |
| `color: "#FF0000"`, `"#ff0000"`, `"red"` | kept | accepted | forwarded | read | that colour |
| `color: ""`, `"#000"`, `"#000000 "`, `"\x00"`, `"\ud800"` | `AnnotationValidationError` | 422 | forwarded; the server answers 422 | refused | — |
| `width: -1` | refused | 422 | zod error | refused | — |
| `width: 0` | kept | accepted | accepted | read | nothing baked; the crop keeps it while its origin is inside |
| `x: 1.5`, `"1"` | refused | 422 | zod error | refused | — |
| extra field `block_size` | — | 422 | zod error | refused | — |
| `type: "blur"` | — | 422 | zod error | refused | — |
| box straddling, outside or inside the crop | `clip_mark` clipped, dropped or kept | — | — | — | MARK_CLIP_BOX |

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-103.1 | type | `RedactAnnotation` has the fields `x`, `y`, `width`, `height` and `color`, in that order, with `color` defaulting to `#000000`; `AnnotationType.Redact.value == "Redact"` and `AnnotationType.Redact.to_wire() == "redact"` | Spec: 09 Mark row (`:930`) | passes where row 2 writes it (row 1 adds the names) |
| AC-103.2 | behaviour | `RedactAnnotation` refuses a negative size, a non-int number and every bad colour in the input matrix (lone surrogate, control characters, `""`, `#000`, trailing space), each caught and asserted as `AnnotationValidationError` | Spec: 09 Mark row; Session 53 RULE-1 | the good colours are kept |
| AC-103.3 | behaviour | The `Annotation` union's members end `PixelateAnnotation, EraserAnnotation, RedactAnnotation`, in that order (an adjacency pin, Session 63 RULE-1) | Local Canon: D-679 | fails while `RedactAnnotation` is outside the union |
| AC-103.4 | behaviour | REDACT_WIRE: a redact writes the five keys and reads back equal. A missing `color`, an extra key or a bad value in a sidecar on disk is refused. A sidecar with no redact keeps its bytes through a read and a write | Spec: 09 Mark row (sidecar); D-682 | each refusal is its own parametrize id |
| AC-103.5 | behaviour | REDACT_CLAMP: the clamp's fixed-point test covers `"redact"`, and a redact past each edge clamps like a pixelate | Local Canon: D-485 | — |
| AC-103.6 | behaviour | REDACT_CLIP: `clip_mark` on a redact gives `clipped` when it straddles, `dropped` when outside, `kept` when inside, and a zero-size mark is kept while its origin is inside and dropped otherwise. Each result equals an independent oracle (the half-open box intersection written in the test) and is a fixed point of `_clamp_annotation` | Local Canon: 09 Crop row (`:934`), D-675 | the oracle disagrees with a closed-box clip on the edge cases |
| AC-103.7 | check | `assert-never-probe.py` passes: pyright reports 0 errors on `domain/capture.py`, and exactly one `assert_never` error naming `RedactAnnotation` when the `case RedactAnnotation():` arm is removed from a copy | Local Canon: 09 Crop row (`assert_never` fails the type check) | the probe's selftest; before row 3 it prints `no redact case` and exits 1 |
| AC-103.8 | behaviour | REDACT_BAKE: on a generated gradient image, each pixel inside `region_clip` of a redact equals the colour at alpha 255, and each pixel outside equals the source. Two overlapping region marks apply in list order (redact over pixelate, then pixelate over redact). A redact under an arrow is drawn before the arrow | Spec: 09 Mark row (region pass, full opacity) | a semi-transparent source pixel under the redact becomes alpha 255 |
| AC-103.9 | behaviour | REDACT_FIXTURE and REDACT_PREVIEW: `applyRegionPass` equals the committed Pillow bake byte for byte on every `redact-` case, and the earlier case names keep their order | Local Canon: 09 MEU-102 Parity row; grouping §9.5 | the redact case list is not empty |
| AC-103.10 | behaviour | One redact traced from the API body through the annotate service, the clamp, the sidecar file on disk, the sidecar read and the bake's `apply_region_pass` (a recording wrapper) to the annotated image's pixels | Local Canon: Session 55 RULE-3 | the wrapper's recorded marks include the redact exactly once |
| AC-103.11 | behaviour | REDACT_API: annotate accepts a redact with and without `color`, storing `#000000` when it is absent. Each bad row of the input matrix gives 422 in the error envelope, with one parametrize id per case | Spec: 09 Mark row; prompt (unknown field 422) | the extra-field case |
| AC-103.12 | guard | An unknown annotation `type` gives 422 through the API and is refused from a sidecar | Spec: 09 Mark row (an older server rejects the unknown type) | passes at baseline and after |
| AC-103.13 | behaviour | REDACT_MCP: annotate forwards a redact with and without `color` unchanged. An extra field, a negative size or a non-int gives a zod error with no backend call | Spec: 09 Mark row (MCP schema); grouping §9.5 | — |
| AC-103.14 | behaviour | REDACT_TOOL: the tool row holds `capture-tool-redact` (`Redact`) in Pixelate's slot, between Text and Smart eraser, and no `capture-tool-pixelate`; `TOOL_BUTTON_IDS.redact` is that id; `CaptureTool` has 8 members | Spec: 09 Tool row | an adjacency pin on the row order |
| AC-103.15 | behaviour | SMART_ERASER: the eraser button's aria-label is `Smart eraser`, and its tooltip reads `Smart eraser: Covers an area with the surrounding colour`. Its chip reads `Smart eraser 1`. A drawn eraser's JSON type is `eraser` | Spec: 09 Rename row | `Eraser` alone appears nowhere in the row |
| AC-103.16 | behaviour | Drawing with Redact under Solid (the mount default) gives one `redact` with `#000000`; under Pixelate it gives one `pixelate` with the current block size | Spec: 09 Tool row (Solid by default) | the Solid radio is checked on mount |
| AC-103.17 | behaviour | MODE_GROUPS: `optionGroups` gives each row of its rule for the redact tool under both modes, a selected redact, a selected pixelate, the eraser and the crop | Local Canon: D-680 | a selected redact shows no `color` group |
| AC-103.18 | behaviour | MODE_SWAP: with a redact selected, picking Pixelate replaces it with a pixelate on the same box, and one Undo restores the redact; the reverse gives `#000000`. With nothing selected, a pick changes no mark. Picking the checked mode is a no-op that leaves the undo stack unchanged | Spec: 09 Tool row (one undo step) | the undo stack grows by exactly one per swap |
| AC-103.19 | behaviour | REDACT_HIT: a click inside a redact selects it, the MEU-100 handles resize it as a box, and its chip reads `Redact 1` | Spec: 09 Tool row (MEU-100 handles) | a click outside its box does not select it |
| AC-103.20 | behaviour | REDACT_OUTLINE: a redact's and a pixelate's SVG element has a `stroke-dasharray` in the Original view and none in the Annotated view; the Pillow bake of a redact has no outline pixel (the ring just outside the box equals the source) | Spec: 09 Outlines row | an eraser's element has no dashed outline |
| AC-103.21 | behaviour | REDACT_PREVIEW in the editor: the region layer shows the redact's colour inside its box during and after a drag | Spec: 09 Mark row | — |
| AC-103.22 | behaviour | REDACT_HELP: the help body names Redact, its Solid default and its Pixelate mode, and Smart eraser; the resize sentence includes redact | Local Canon: D-686 | the old `Pixelate and Eraser change the pixels under them` sentence is gone |
| AC-103.23 | check | Spec D3: 09's `:284`, the DTO row, `:826` and the Delivered note; 06 `:943`; the gui-index rows. Each file keeps CRLF endings | Local Canon: D3 | row 5's check exits 1 before row 5 |
| AC-103.24 | behaviour | Electron: on the capture page the Redact button is visible with Solid checked, and the Smart eraser button's tooltip shows the hint text. The AC-90.12 live Pixelate drag runs through the Redact tool's Pixelate mode | Spec: 09 Tool and Rename rows; grouping §9.6 | — |
| AC-103.25 | behaviour | Crop and export end to end: a shot with a redact straddling the crop crops into a shot whose sidecar holds the clipped redact and whose annotated image is the colour in the clipped box. The MEU-136 export of that shot bakes it the same way | Local Canon: 09 Crop row; grouping §9.5 (MEU-130 crop, MEU-136 export) | the dropped case leaves no redact in the crop's sidecar |

**Guards.** These pass after rows 1 and 3:
- Python: `tests/unit/test_capture_adapter.py`, `tests/unit/test_capture_service.py`, `tests/unit/test_domain.py`, `tests/unit/test_domain_capture.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_crop.py`, `tests/e2e/test_api_capture_flatten.py` and `tests/e2e/test_api_capture_export.py`;
- MCP: `mcp-server/tests/capture.test.ts`;
- UI: every capture Vitest file named in §Pins that move.

`tests/unit/test_capture_bake_fixture.py` and `ui/tests/unit/capture-region-pass.test.ts` pass after row 4.

**Spec sufficiency.** Every 09 §Redact mark rule has an AC:

| Rule | ACs |
|---|---|
| Mark | AC-103.1 to .4, .8 to .13, .21 |
| Tool | AC-103.14, .16 to .19 |
| Rename | AC-103.15, .24 |
| Outlines | AC-103.20 |
| Crop | AC-103.6, .7, .25 |

### Files Modified

The endings come from `C:/Temp/av-kit/s68/endings-plan.txt`; row 0 records them again, with SHA-256, in `s68-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/domain/enums.py` (`REDACT_TYPE`) | CRLF | 1 |
| `packages/core/src/avkit_core/domain/capture.py` (`REDACT_TYPE`, `REDACT_CLIP`) | CRLF | 1, 3 |
| `packages/core/src/avkit_core/services/capture.py` (`REDACT_WIRE`, `REDACT_CLAMP`) | CRLF | 3 |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` (`REDACT_BAKE`) | CRLF | 3 |
| `packages/api/src/avkit_api/schemas/captures.py`, `packages/api/src/avkit_api/routes/captures.py` (`REDACT_API`) | CRLF | 3 |
| `openapi.committed.json` | CRLF | 3 |
| `mcp-server/src/toolsets/capture.ts` (`REDACT_MCP`) | CRLF | 3 |
| `ui/src/renderer/src/features/capture/capture-annotate.ts` (the TS type) | CRLF | 1, 3 |
| `ui/src/renderer/src/features/capture/capture-region-pass.ts` (`REDACT_PREVIEW`) | CRLF | 3 |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx`, `CapturePage.tsx`, `capture-toolbar.ts`, `ToolbarIconButton.tsx`, `capture-hit-test.ts`, `capture-transform.ts`, `capture-help-content.ts` | CRLF | 1, 3 |
| `ui/tests/e2e/test-ids.ts` (the MEU-103 block, after the MEU-141 block) | CRLF | 1 |
| `tools/capture_bake_fixture.py` (`REDACT_FIXTURE`) | CRLF | 3 |
| `ui/tests/e2e/fixtures/capture-region-pass.json` | CRLF | 4 |
| `tests/unit/test_domain.py`, `tests/unit/test_domain_capture.py` | CRLF | 1 |
| `tests/unit/test_capture_service.py`, `mcp-server/tests/capture.test.ts` | CRLF | 2 |
| `ui/tests/unit/capture-toolbar.test.ts`, `capture-page.behavior.test.ts`, `capture-page.test.ts`, `icon-hints.test.ts`, `capture-hit-test.test.ts`, `capture-help-content.test.ts`, `capture-region-pass.test.ts` | CRLF | 2 |
| `ui/tests/e2e/capture-inbox.test.ts` | LF | 2 |
| `tests/unit/test_capture_redact.py`, `tests/e2e/test_api_capture_redact.py`, `ui/tests/unit/capture-redact.behavior.test.ts` (new) | LF | 2 |
| `docs/build-plan/09-screenshot-capture.md` (dirty at baseline), `docs/build-plan/06-gui.md`, `docs/build-plan/gui-actions-index.md` | CRLF | 5 |

Before it writes, each row measures the file's endings with Python bytes, and then writes in that ending. A scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3).

**Byte-hash guard (Session 50).** AC-51.6 and AC-81.13 hash `ui/tests/e2e/test-ids.ts` up to `// MEU-51 primitive harness IDs.` (`:292`). Row 1 appends the MEU-103 block after the file's last line and removes `CAPTURE_TOOL_PIXELATE` (`:449`). Both edits sit after the hashed prefix, so the expected hash `6E569F82…FF454` stays unchanged. Row 1 runs `ui/tests/unit/capture-action-row.test.ts` as its own check and names the hash it reads in the handoff. No source or test reads `CAPTURE_TOOL_PIXELATE`, as the plan-time grep of `ui/` shows.

### Project files

These project files are written:
- `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF) and `docs/BUILD_PLAN.md` (LF);
- the grouping file (CRLF, dirty at baseline; tracker row 44 at `:122`);
- the handoff, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| A tool letter for Redact (X) | grouping §9.3: X is Redact's letter in MEU-105 |
| The Pixelate block-size scrub | grouping §9.3: MEU-105 |
| The ellipse crop, `head`, `step` and Duplicate | MEU-106 and MEU-107 (D-675, D-676) |
| A colour picker for a GUI redact | D-681: the GUI draws `#000000`; the API and MCP take any valid colour |
| Persisting the Redact mode across launches | D-680: Solid on mount is the safe default the Tool row names |
| A second `CaptureTool` for Pixelate | D-679: the toggle is a tool control, and the union keeps one button per tool |
| Copy image and the action renames | MEU-104 (Session 69) |
| Members-only URLs or ids, `npm run dist`, the live MCP audit | Session 68 prompt |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after rows 6 and H2-2. MEU-103 is `pending`, with its dependencies MEU-91 and MEU-100 `approved` (`.agent/context/meu-status.yaml:2694-2707`).

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the budget and execute words, each with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** Checks that MEU-91, MEU-100 and MEU-142 are `approved`, that MEU-103 is `pending`, and that `3c5676f` is an ancestor of `HEAD`.
3. **Shapes (S7, Session 61 RULE-3).** Checks by name the shapes this plan relies on:
   - `EraserAnnotation`, the union, `clip_mark` with its eraser arm and `assert_never`, `_HalfOpenMark`, `_clip_half_open`, `_require_color` and `AnnotationType.Eraser`;
   - `_annotation_from_wire` and `_to_wire`, `_clamp_annotation`, `region_clip`, `apply_region_pass`, `_apply` and `_color_rgb`;
   - `EraserAnnotationIn`, `AnnotationIn` and `_annotations_from_in`;
   - the MCP `eraserAnn` and union, and the UI annotate union;
   - `RegionMark`, `applyRegionPass`, `BoxMark`, `CaptureTool`, the Pixelate and Eraser buttons, `OptionGroup` and the icon button's label;
   - the help sentence, the fixture's `*crop_cases(),`, the test-ids hash boundary and `CAPTURE_TOOL_PIXELATE`;
   - 09's `### Redact mark` and the gui-index pixelate row.

   It then checks that `redact` and `Smart eraser` appear in none of the 21 capture files, and that the three new files don't exist.
4. **Records.** Creates `C:\Temp\av-kit\s68\tmp`. Records `baseline.sha`, `baseline-dirty.txt` (each dirty path's porcelain line and SHA-256) and `s68-anchors.txt` (every target's endings and SHA-256). It hashes `docs/proposals/2026-11-10-download-logic-divergence-report.md` and never opens it.
5. **Installs.** Installs from the lock with `uv sync --frozen --offline --all-packages` and proves that both `node_modules` trees match their locks (S4).
6. **FFmpeg pair.** Checks the pinned FFmpeg pair, as the identity script binds it.
7. **Base runs.** Captures the base Python, UI and MCP suites, the UI build, the capture Electron spec and `ruff check packages/ tests/ tools/capture_bake_fixture.py`. These are recorded and are not fatal.
8. **Selftests.** Runs the `red-check.py`, `identity.py`, `id-length.py` and `assert-never-probe.py` selftests, each on its own fixtures (Session 56 RULE-4).

At `3c5676f` the shapes and queue blocks ran alone with exit 0 (`C:/Temp/av-kit/s68/shapes-dry.txt`).

### 2. Type-only first, then Red, then Green

**Row 1 (Session 53 RULE-2)** adds the names with no behaviour:
- `RedactAnnotation` with its fields and the `#000000` default but no `__post_init__`, outside the union. It is a wrong stub that accepts every bad value, so AC-103.2 fails at Red by `DID NOT RAISE`; row 3 adds the validation;
- `AnnotationType.Redact` with its `to_wire` entry, because the all-member wire guard (`test_domain_capture.py:129`) raises `KeyError` without it;
- the TS `RedactAnnotation` and `RedactMode` types, which are exported and appear in no union;
- the four MEU-103 test ids.

Row 1 moves the two enum pins, so `test_domain.py` and `test_domain_capture.py` run there (Session 54 RULE-1).

**Row 2 (Red)** requires only new-behaviour tests (Session 66 RULE-2):
- pytest: AC-103.2 to .6, .8, .10, .11 and .25;
- Vitest: AC-103.13 to .22;
- Playwright: AC-103.24.

These are not in the Red list:
- AC-103.1 tests what row 1 adds, so it must pass where it is written.
- AC-103.12 is a guard that passes throughout.
- AC-103.9 passes after row 4's fixture regeneration.
- AC-103.7 is `assert-never-probe.py`.
- AC-103.23 is row 5's check.

**Red-check (Session 50).** A Red row passes only when `red-check.py` reads each receipt and names each failing required test as an assertion failure. A required test that fails on a missing name is refused (the `pytest-required-ac-103-5-stub-name` fixture). Every Red test:
- asserts that a name exists before it patches or calls it (Session 52 RULE-4);
- catches a domain exception and asserts its type (Session 62 RULE-3);
- asserts length or membership before indexing (Session 62 RULE-3);
- in Electron, asserts `await expect(locator).toBeVisible()` before it clicks.

`id-length.py` checks every new pytest id against red-check's header width of 71 characters (Session 67 RULE-4).

**Rows 3 and 4 (Green)** change no test file. Row 4 regenerates the fixture JSON, which is test data that the writer produces.

### Plan-local scripts

The folder's `baseline.ps1`, `red-check.py`, `identity.py` and `session-gate.ps1` are adapted from Session 67's, with the `s68` names and this plan's paths.

| Script | What it does | Plan-time result |
|---|---|---|
| `id-length.py` | checks pytest id widths | selftest: 4 cases |
| `assert-never-probe.py` | proves AC-103.7 on a copy of `domain/capture.py` under `C:/Temp/av-kit/s68/never-probe/` | selftest on three toy modules: `C:/Temp/av-kit/s68-plan-never-selftest.txt`; on the real file before row 3 it prints `no redact case` and exits 1, AC-103.7's negative (`C:/Temp/av-kit/s68-plan-never-pre.txt`) |
| `red-check.py` | reads the Red receipts | selftest: 49 fixtures (15 positive, 34 negative), 0 wrong (`C:/Temp/av-kit/s68/rc-selftest.txt`); this includes the AC-103.1 boundary against AC-103.10 to AC-103.19 and the stub-name refusal |
| `identity.py` | binds the tested state | selftest: 0 failures (`C:/Temp/av-kit/s68/id-selftest.txt`) |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s68-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright, `ruff check packages/ tests/ tools/capture_bake_fixture.py`, UI typecheck and lint, `lint_task_contract.py`, the scope-paths check (S3; the MCP audit baseline is refused), the `red-check.py` selftest, `id-length.py`, `assert-never-probe.py` (AC-103.7; its last line must be `assert-never-probe: pass`) |
| Byte-hash guard | `npm --prefix ui run test -- tests/unit/capture-action-row.test.ts` on its own |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s68\tmp`; only the Python ids that the base receipt shows failing are excused), `export_openapi.py --check`, the whole UI suite and build, the MCP typecheck, build and suite, `meu_status.py render --check`, `issue_triage.py render --check` |
| Runtime | the capture Electron spec `ui/tests/e2e/capture-inbox.test.ts` (AC-103.24) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | `mcp-audit` (network and the installed servers), `build-record` (no release and no package build) |

The baseline counts at the Session 67 gate were Python 2369, UI 1293, MCP 525, Electron 26 and real FFmpeg 1. The handoff copies this session's counts from the receipts (Session 63 RULE-2).

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop; a moved pin goes into the handoff as a departure, and to the Fable subagent if it changes an AC (S12) |
| S3 | `HEAD` moves, or a path outside this plan and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network | stop |
| S6 | A raw value (a path, a colour string the domain refused) reaches a log, stdout or the Console | fix it in the row or ask (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the budget or execute words | stop at row 0 |
| S10 | Codex is unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file is dirty from another session (the grouping file is dirty at baseline) | copy it to `C:/Temp/av-kit/s68/pre-status/`, byte-edit only this session's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to the Fable subagent as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs (a port, a file lock) | stop and ask Mat; never stop another program (Session 57 RULE-4) |

## Decision Log

> [!WARNING]
> D-679 to D-687 are autonomous, and each lists its alternatives in `reasoning`. D-688 records Mat's 2026-11-13 rulings. D-679 to D-692 were free at plan time (`C:/Temp/av-kit/s68/id-probe.txt`).
>
> Carried, and not relisted in the block:
> - D-158: human, `USER_EXPLICIT 2026-10-29 "all recommendations are accepted"`, grouping §8 `:141`;
> - D-159: autonomous, Local Canon, `:142`;
> - D-160: autonomous, Local Canon, `:143` (Session 43's slicing; the probe returns it, so the reflection carries it);
> - D-674 and D-675: autonomous, stage `grouping`, §9.8.
>
> The reflection carries these five and every id the decision probe returns (Session 54 RULE-5). At plan time the probe (`C:/Temp/av-kit/s68-plan-decision-probe.txt`), with this plan and the grouping as sources, returned 13 decisions: D-679 to D-688 `planning` and D-158 to D-160 `grouping`. Without the grouping it refuses (HDP-18). It reads only the grouping's §8, so D-674 and D-675 (§9.8) are carried by hand. Each source's SHA-256 was unchanged by the run.

```yaml
decision_log:
  - id: D-679
    stage: planning
    question: "Is the Pixelate toggle a second CaptureTool or a control of one Redact tool?"
    resolution: autonomous
    class: two-way
    chosen: "One tool: CaptureTool pixelate becomes redact, so the union keeps 8 members; the capture-tool-redact button (EyeOff, Redact) takes the Pixelate slot and capture-tool-pixelate is retired; the mode lives in page state; RedactAnnotation is appended last in the Annotation union and AnnotationType.Redact after Eraser"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:931 - One Redact tool with a Solid / Pixelate toggle"
      - "ui/src/renderer/src/features/capture/capture-toolbar.ts:87-96 - TOOL_BUTTON_IDS maps every CaptureTool to exactly one button"
      - "grouping §9.3 - the toggle is a tool control unless the plan shows the union needs it"
    research:
      engine: none
      sources: []
    reasoning: "TOOL_BUTTON_IDS is a Record over CaptureTool, so a pixelate tool with no button of its own would fail the type check; keeping the union at 8 with redact in pixelate's place gives one button and one tool. A ninth tool for pixelate lost: it needs a button the Tool row says not to show. Keeping the tool named pixelate lost: the button, chips and tests would name the old tool. Appending the domain type last keeps every existing wire and enum position. Two-way."
    human_message_reference: null
  - id: D-680
    stage: planning
    question: "How does the Solid / Pixelate toggle look and behave?"
    resolution: autonomous
    class: two-way
    chosen: "A SegmentedControl (size sm, label Redact mode) in the options row under a new mode option group, Solid on mount and not persisted; optionGroups takes the mode; picking the other mode with a redaction mark selected replaces it through applyHistory as one undo step, keeping the box; picking the checked mode is a no-op"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/components/ui/SegmentedControl.tsx - native radios, so the checked one fires no change"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:1351 - the block-size change on a selected pixelate already edits through history"
      - "docs/build-plan/09-screenshot-capture.md:931 - switching a selected mark replaces it as one undo step"
    research:
      engine: none
      sources: []
    reasoning: "The SegmentedControl already ships in four pages and gives keyboard and screen-reader behaviour for free. Solid on mount is the safe default the header names. Persisting the mode lost: a user who last chose Pixelate would get a silent failure on the next secret. Two icon buttons lost: they would need their own pressed-state logic and test ids that duplicate the radio group. Two-way."
    human_message_reference: null
  - id: D-681
    stage: planning
    question: "Which colours can a redact have?"
    resolution: autonomous
    class: two-way
    chosen: "The GUI draws #000000 and shows no colour picker for a redact; the API and MCP accept any valid colour (a named colour or #RRGGBB), which the bake and preview honour"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:930 - color=#000000 is a field with a default"
      - "packages/core/src/avkit_core/domain/capture.py:72 - _require_color"
    research:
      engine: none
      sources: []
    reasoning: "The Mark row makes colour a field, so the API must carry it; the Tool row asks for nothing beyond Solid and Pixelate in the GUI. A GUI picker lost: it adds a control the spec doesn't ask for. Refusing non-black colours lost: it contradicts the field. Two-way."
    human_message_reference: null
  - id: D-682
    stage: planning
    question: "Where does the #000000 default apply?"
    resolution: autonomous
    class: two-way
    chosen: "The domain dataclass and the API default to #000000; the sidecar requires color; MCP leaves color optional and forwards the body unchanged; the UI type requires color"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:350 - every sidecar field is read explicitly"
      - "mcp-server/src/toolsets/capture.ts:161 - pixelateAnn leaves block_size optional and forwards it"
    research:
      engine: none
      sources: []
    reasoning: "A default in one place, the API, means every writer stores an explicit colour, so a later default change can't recolour saved marks. MCP follows MEU-90's block_size precedent. Defaulting in the sidecar reader lost: a damaged sidecar would read as black silently. Two-way."
    human_message_reference: null
  - id: D-683
    stage: planning
    question: "How is Eraser renamed and its tooltip shown?"
    resolution: autonomous
    class: two-way
    chosen: "ToolbarButtonSpec gains an optional hint; the eraser's name is Smart eraser and its hint is Covers an area with the surrounding colour; the tooltip reads name, shortcut, then a colon and the hint; the aria-label stays the name; chips read Smart eraser N and Redact N; the gui index gains capture:tool_redact, drops capture:tool_pixelate and renames the eraser row"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:932 - the Rename row"
      - "ui/src/renderer/src/features/capture/ToolbarIconButton.tsx:34 - the tooltip label is built from the name and shortcut"
    research:
      engine: none
      sources: []
    reasoning: "A hint field keeps the accessible name short and puts the explanation where the spec says, the tooltip. Folding the hint into the name lost: screen readers would read a sentence on every focus. Changing the JSON type lost: the Rename row forbids it. Two-way."
    human_message_reference: null
  - id: D-684
    stage: planning
    question: "Which marks get the dashed outline, and where is it drawn?"
    resolution: autonomous
    class: two-way
    chosen: "Redact and pixelate SVG elements draw a 1 px dashed outline in the Original view only; the Annotated view and the bakes draw none; the eraser draws none"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:933 - redaction marks show a dashed editor-only outline, never baked"
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:1149-1166 - REGION_MARK_SVG"
    research:
      engine: none
      sources: []
    reasoning: "Both modes of the Redact tool make redaction marks, so both are outlined; the Smart eraser is meant to look like nothing was there. An outline on the eraser lost: it would show where content was removed. Drawing it on the region layer canvas lost: that canvas is what the preview parity compares. Two-way."
    human_message_reference: null
  - id: D-685
    stage: planning
    question: "How do the parity fixtures grow?"
    resolution: autonomous
    class: two-way
    chosen: "Cases named redact- are appended after the crop cases in region_cases(); earlier cases keep their names, order and bytes; the committed JSON is regenerated by the writer in row 4"
    source_tag: Local Canon
    precedents:
      - "tools/capture_bake_fixture.py:221 - the crop cases were appended the same way (D-493)"
      - "ui/tests/unit/capture-region-pass.test.ts:33 - each AC filters its own case names"
    research:
      engine: none
      sources: []
    reasoning: "Appending keeps every older AC's filter and expected bytes unchanged. A separate fixture file lost: a third writer path for one mark. Two-way."
    human_message_reference: null
  - id: D-686
    stage: planning
    question: "What does the help body say?"
    resolution: autonomous
    class: two-way
    chosen: "The help names Redact with Solid as its default and Pixelate as its other mode, and Smart eraser; the resize sentence includes redact; the AC-91.11 tool list moves to Redact, Pixelate and Smart eraser"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-help-content.ts:27 - the region sentence"
      - "grouping §9.5 - the help body is one of the layers a new mark touches"
    research:
      engine: none
      sources: []
    reasoning: "The help must match the toolbar or it teaches a button that no longer exists. Keeping Pixelate as a separate help entry lost: there is no Pixelate button. Two-way."
    human_message_reference: null
  - id: D-687
    stage: planning
    question: "How is the crop rule tested?"
    resolution: autonomous
    class: two-way
    chosen: "A parametrized unit test over straddling, outside, inside and zero-size cases against an oracle written in the test, each result a fixed point of the clamp; an API end-to-end test that crops and exports a shot with a redact; assert-never-probe.py proves the type check"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:934 - the Crop row's four cases and the assert_never rule"
      - "tests/e2e/test_api_capture_crop.py:538 - AC-130.19 redaction survives the crop, for pixelate"
    research:
      engine: none
      sources: []
    reasoning: "An oracle in the test catches a closed-box clip that reusing _clip_half_open would hide. The probe proves the Crop row's type-check clause on the real file, which a unit test can't. Testing only through the API lost: it hides which layer fails. Two-way."
    human_message_reference: null
  - id: D-688
    stage: planning
    question: "What are the execution review budget, the review round caps, the execution gate and the route for later decisions?"
    resolution: human
    class: two-way
    chosen: "Execution review budget 50M; each review loop gets two rounds over the ledger default (plan 5, execution 8), lifted with review_ledger.py continue; execution starts when the plan review approves; later decisions go to a Fable subagent whose answer is recorded as a ruling by delegation"
    recommendation: "An execution review budget of 32.5M (the round 1 estimate of 13M twice plus a 6.5M recheck, Session 60 RULE-5) with the default caps, and execution after Mat's word at the plan gate"
    source_tag: Human-approved
    precedents:
      - "Session 68 prompt - at the plan gate, ask for the execution budget"
      - "GUARDRAILS.md SIGN 3 - direct human execution authorization satisfies the plan-to-execution gate"
    research:
      engine: none
      sources: []
    reasoning: "Mat gave the budget, the caps and the execution words in the user channel before the review, so the gate needs no second question; the ledger still stops each loop at its raised cap and budget. The do-nothing option, asking again at the gate, would repeat a question Mat has answered."
    human_message_reference: "USER_EXPLICIT 2026-11-13 'set token buget for 50M and add 2 more round just so we do no run into limits'; USER_EXPLICIT 2026-11-13 'upon plan approval auto proceed with execution'; USER_EXPLICIT 2026-11-13 'if decisions are needed send them to Fable subagent and accept answers as human ruling'"
```

## Research References

- No web research: every rule comes from 09, the grouping's §8 and §9, and the code at `3c5676f`.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s68/id-probe.txt` | D-679 to D-692 and the AC-103 family were free |
| `C:/Temp/av-kit/s68/idw/out.txt` | red-check's pytest header width, 71 characters |
| `C:/Temp/av-kit/s68/endings-plan.txt` | the targets' line endings |
| `C:/Temp/av-kit/s68/pin-sweep.txt` | the pins that move, over `tests/`, `ui/tests/` and `mcp-server/tests/` |
| `C:/Temp/av-kit/s68/shapes-dry.txt` | `baseline.ps1`'s shapes and queue blocks run alone at `3c5676f` (exit 0) |
| `C:/Temp/av-kit/s68-plan-rc-selftest.txt`, `C:/Temp/av-kit/s68-plan-id-selftest.txt` | the red-check selftest (49 fixtures, 0 wrong) and the identity selftest (0 failures) |
| `C:/Temp/av-kit/s68-plan-id-length-selftest.txt`, `C:/Temp/av-kit/s68-plan-never-selftest.txt` | the two new scripts' selftests: 4 cases, 0 wrong; 3 toys, 0 wrong |
| `C:/Temp/av-kit/s68-plan-never-pre.txt` | `assert-never-probe.py` on the real file before row 3 (exit 1, `no redact case`), AC-103.7's negative |
| `C:/Temp/av-kit/s68-plan-decision-probe.txt` | the decision probe: 13 decisions with this plan and the grouping as sources (D-679 to D-688, D-158 to D-160); a refusal without the grouping (HDP-18) |
| `C:/Temp/av-kit/s68-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit`: OK, 24 rows, 22 fully checked, 2 `view_file` rows exempt |

No suite or build ran at plan time.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/ tools/capture_bake_fixture.py`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest, `id-length.py` and `assert-never-probe.py`.
- **Targeted:** each row's own files. `red-check.py` reads the Red receipts, and `capture-action-row.test.ts` runs on its own in each row that touches `test-ids.ts`.
- **Fresh full:** the session gate runs the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds, the two render checks and the capture Electron spec.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
