---
project: "2026-11-14-capture-shapes-steps"
date: "2026-11-14"
source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md#session-48--capture-shapes-steps-meu-106-meu-107--p3"
grouping_source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md"
meus: ["MEU-106", "MEU-107"]
status: "draft"
template_version: "2.3"
---

# Implementation Plan: Capture line, ellipse and step marks (Session 72)

> **Project:** `2026-11-14-capture-shapes-steps`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Line and ellipse (`:988-999`, anchor `line-and-ellipse`) and §Step mark (`:1001-1010`, anchor `step-mark`). The MEU table rows are `:1303` (MEU-106) and `:1304` (MEU-107), and the build priority matrix rows are 9.32 and 9.33.
>
> **Source request.** On 2026-10-29 Mat accepted the capture annotation editor synthesis ("all recommendations are accepted", grouping D-158). D-674 renumbered the grouping's sessions into 68 to 72, and this is its last: grouping §3 Session 48 (`:91`) and §6 row 48 (`:127`). D-675 set the crop rule of each new mark, and on 2026-11-12 Mat chose the ellipse's (D-676, USER_EXPLICIT 2026-11-12 "both recommendations accpeted").
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 2 (`.agent/context/handoffs/2026-11-14-capture-shapes-steps-plan-critical-review.md`). At the plan gate Mat accepted every recommendation (D-779 P2 in both, D-780 one session, D-781 the Head and Shape controls plus a Step button with no letter, and the gate flags D-768, D-775 and D-777 as planned) and said to execute (USER_EXPLICIT 2026-11-14 'all recommendations accepted, execute'), with the repository's round cap of 6 and no token budget (D-782). The review loops have no token budget (`.agent/review-limits.json` `token_budgets: "off"`). Their round caps are the repository's: plan 3, execution 6.

## Goal

**Goal anchor:** Session 72 adds the last three marks of the capture annotation synthesis.
- A **Line** is an arrow with no head, and an arrow can have a head at both ends (C-13).
- An **Ellipse** is a box with an elliptical shape, resized by the same handles (A-14).
- A **Step** is a numbered badge for how-to screenshots. Each click places the next number (C-8).
- **Ctrl+D** duplicates the selected mark, offset and clamped, and selects the copy (B-7).

Five things are missing today (`5db3623`):

1. **No head choice.** `ArrowAnnotation` (`packages/core/src/avkit_core/domain/capture.py:284-455`) has `from_xy`, `to_xy`, `color` and `stroke_width` only. The bake always draws one head at `to` (`adapter.py:825`, `arrowhead_vertices` `:103`, `arrow_shaft_end` `:124`), and so does the preview (`CaptureViewport.tsx:220`).
2. **No ellipse.** `RectAnnotation` has no shape, `_apply_rect` (`adapter.py:868`) draws an unaliased rectangle, and the preview draws a `<rect>`.
3. **No step mark.** No `StepAnnotation`, no `step` wire type, no `step` tool and no `step_color` or `step_size` leaf exist (a plan-time grep at `5db3623` finds none).
4. **No duplicate.** No `Ctrl+D` exists in `ui/src` (a plan-time grep), and `RESERVED_CHORDS` (`registry/shortcuts.ts:141-163`) doesn't hold it.
5. **The API rebuilds each mark by hand.** `_annotations_from_in` (`packages/api/src/avkit_api/routes/captures.py:158-229`) builds each domain mark from its `*In` model field by field. A field it doesn't pass is dropped, and a type it doesn't match falls out of the loop silently. A `head` or `shape` sent over HTTP would be lost there.

Today's behaviour was read at `5db3623` (Session 69 RULE-1). The arrow and rect bakes were probed before parity was claimed (`C:/Temp/av-kit/s72-probe-pillow.txt`). The step badge's centring was probed over the AC case set (`C:/Temp/av-kit/s72-probe-step-centre.txt`, `C:/Temp/av-kit/s72-probe-step-centre-acset.txt`). The pins are listed in §Pins that move.

The session ends when:
- every rule row of 09 §Line and ellipse and §Step mark holds, each with a behaviour test;
- the session gate's last line is `session-gate: all steps exit 0`;
- MEU-106 and MEU-107 are `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-14). No payload is oversized: the domain, the wire codec, the clamp, the crop, the adapter, the API schemas and routes, the MCP toolsets, the UI schemas, the hit test, the toolbar, the registry, the viewport and the page were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, the Claude Code block of `.agent/context/harness.local.md`). Execution waits for Mat's explicit words at the plan gate (D-782). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s72-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s72\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. GUI references are not shipped (`gui-refs-not-shipped`).
- **Decisions:** every decision for Mat goes to Mat through the Human Decision Protocol (AGENTS.md §Communication Policy), with a recommendation first and a do-nothing option. No decision goes to a subagent in this session.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s72-plan-canonical-2026-11-14-capture-shapes-steps` and `s72-execution-2026-11-14-capture-shapes-steps`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps are the repository's: plan 3, execution 6. Token budgets are `off` (`.agent/review-limits.json`), so the loops stop on rounds only. Mat is not asked for a budget. The coordinator reports the token estimate and each round's spend.
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, so the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit` and then copied byte for byte to its canonical path. The `--review-state-only` receipt is then rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-767 to D-782, AC-106.1 to AC-106.34, AC-107.1 to AC-107.30, and the mechanism ids in §Single-statement contracts.
  - They forbid opening:
    - `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json` and any `.env`;
    - `.claude/settings.local.json`;
    - anything under `.agent/fleet/hub`;
    - `docs/proposals/2026-11-10-download-logic-divergence-report.md`.
  - They write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header. It also carries the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3). It asks for bare words in its Recheck cells, such as `fixed` and `open` (Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - the live MCP audit or `--update-baseline`;
  - `npm run dist`;
  - an `approved` verdict written by the implementer;
  - reading any user data: the capture inbox, its sidecars, the app database or Mat's settings file (Session 70 RULE-2). Every test works from fixtures and fakes.
- **No network, no clipboard:**
  - no test or row reaches YouTube or the network;
  - no test or row writes the system clipboard (Session 57 RULE-4);
  - nothing touches the installed avkit MCP servers, and no `mcp__avkit__*` tool is called;
  - no other program is stopped. If ShareX holds a key a row needs, the row stops and asks Mat (S13);
  - `ui/tests/e2e/capture-filmstrip-actions.test.ts` and `ui/tests/e2e/capture-import.test.ts` are never run in this session (Session 72 prompt). The session gate's Runtime step runs `capture-inbox.test.ts` alone.

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-106 | `.agent/context/handoffs/2026-11-14-capture-shapes-steps-MEU-106-handoff.md` | first |
| MEU-107 | `.agent/context/handoffs/2026-11-14-capture-shapes-steps-MEU-107-handoff.md` | second |

Rolling reviews:
- `.agent/context/handoffs/2026-11-14-capture-shapes-steps-plan-critical-review.md`
- `.agent/context/handoffs/2026-11-14-capture-shapes-steps-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | Type-only names: the `head` and `shape` fields with no checks, `StepAnnotation` outside the union, `AnnotationType.Step`, the stub helpers, the TS names, `LetterTool`, `CAPTURE_EDIT_IDS`, the new test ids | shared |
| WP-3 | 2 | Data: the two step settings leaves, the API mark schemas, the regenerated OpenAPI snapshot, the MCP and UI mark schemas, the two geometry fixture keys, and the key-set pins they move | shared |
| WP-4 | 3, 4 | Red, then Green (the behaviour and the help text) | shared |
| WP-5 | 5 | The actions index and 09's Delivered notes | shared |
| WP-6 | H1, H2 | Gate, handoffs, review, reflection, records, next prompt | compact_continue |

## User Review Required

**Carried rulings:**
- **D-158** (USER_EXPLICIT 2026-10-29 "all recommendations are accepted", grouping §8 `:142`) accepts the synthesis that 09 §Line and ellipse and §Step mark encode: A-14, B-7, C-8 and C-13.
- **D-159** (autonomous, Local Canon, `:143`) made one MEU per slice. **D-160** (autonomous, Local Canon, `:144`) is carried. The plan-time decision probe returns D-158 to D-160 from the grouping and D-767 to D-778 from this plan (`C:/Temp/av-kit/s72-plan-decision-probe.txt`).
- **D-674** (autonomous, grouping §9.8 `:201`) numbered this session 72.
- **D-675** (autonomous, `:202`) set the crop rules: `head` rides `_clip_arrow`, and the step takes MARK_CLIP_TEXT's anchor rule. `assert_never` fails the type check until the step's case exists.
- **D-676** (human, USER_EXPLICIT 2026-11-12 "both recommendations accpeted", `:203`) set MARK_CLIP_ELLIPSE: kept when its box lies inside the closed crop `[0,width]x[0,height]`, otherwise dropped, never clipped.
- **D-678** (autonomous, `:205`) keeps Ctrl+C on the page key handler. Ctrl+D follows a different route here (DUPLICATE), because 09's Duplicate row names the registry first.

**MEU-105 and MEU-143 contracts this plan keeps:**
- STYLE_STORE: the step tool's colour and size are saved as two new capture leaves through the same queue and filter (STEP_STYLE).
- STYLE_DISPLAY and STYLE_DRAW: a Line takes the arrow tool's style, an Ellipse the box tool's, and a Step its own.
- STYLE_TARGET: Duplicate selects the copy, so a style change then restyles the copy.
- LOCK_SELECTS and ARMED_EDIT: a placed step stays selected under Lock, and an armed press on its badge moves it.
- MODIFIERS: a Line takes the arrow's Shift snap and an Ellipse takes the box's rules (Shift draws a circle, Alt from the centre). No new numbers.
- FIELD_GUARD: it covers plain letters only, and Ctrl+D is a Ctrl chord. What Ctrl+D does from a field is stated in DUPLICATE.
- LETTERS: the eight letters don't change. The Step tool gets no letter (D-776).

**The toolbar route (D-776, asked at the gate as D-781).** 09 says a Line is an arrow with `head: "none"` and an Ellipse is a rect with `shape: "ellipse"`. It doesn't say how a user picks them. This plan adds the fewest controls:
- an **Arrow head** segmented control (End, None, Both) in the options row while Arrow is armed or an arrow is selected;
- a **Box shape** segmented control (Rectangle, Ellipse) while Box is armed or a box is selected;
- one **Step** tool button after Text, with no letter.

The pick is page state and not saved, as D-680 keeps the Redact mode. With a mark selected, a pick changes that mark as one undo step, as the Redact mode does. Recommendation: this route. The other options are separate Line and Ellipse tool buttons, or do nothing (no Step tool button, which leaves the step mark reachable only over MCP and the API, and records the gap).

**The split (D-780, asked at the gate).** The grouping's §3 says "yes, candidate; MEU-107 can run as 48b". Recommendation: one session, because both MEUs touch the same layers and the same records, and Session 68's single-MEU plan cost about as much as this one's estimate. The do-nothing option is the same, one session.

**Band mismatch (D-779, asked at the gate).** The grouping's §3 heading (`:91`) and tracker row 48 (`:127`) say P3. `.agent/context/meu-status.yaml` gives MEU-106 (`:2771`) and MEU-107 (`:2797`) `band: P2`. Mat ruled "P2 in both" at the gate (D-779), so row 6 changes the grouping's §3 heading and row 48 to P2, and `meu-status.yaml` keeps P2. The gate asked:
- recommendation: "P2 in both", as D-756 chose for MEU-143, because `meu-status.yaml` drives the queue and the build plan;
- do-nothing option: "leave both as they are".

**OpenAPI and MCP change (D-767, D-769, D-772, D-775).**
- `ArrowAnnotationIn` gains `head`, `RectAnnotationIn` gains `shape`, and `StepAnnotationIn` joins the `AnnotationIn` union. `SettingsPutIn` gains `step_color` and `step_size`. The committed OpenAPI snapshot is regenerated, never edited by hand.
- The strict MCP `avkit_capture` mark schemas gain `head`, `shape` and `stepAnn`. The `avkit_settings` set schema and `SETTINGS_SCHEMA` gain the two step leaves.
- The MCP audit baseline is keyed by tool, action and status, and no action is added, so it doesn't change.
- `step_size` is an integer leaf. `_reject_cookie_shaped` (`services/settings.py:141`) walks string leaves only, so it doesn't see an integer. The known big-integer issue applies to it as to every StrictInt leaf: a 401- to 4300-digit integer gets a 422, and 4301 digits or more get a 400 from the JSON parser's digit limit (`C:/Temp/av-kit/s72-probe-bigint.txt`; MEU-105 handoff `:377`). AC-107.15 pins both, and this plan doesn't change the limit.

**Rulings at plan time.** None. Four questions went to Mat at the gate through the HDP: the band (D-779), the split (D-780), the toolbar route (D-781) and his words to execute (D-782). He accepted every recommendation (USER_EXPLICIT 2026-11-14 'all recommendations accepted, execute').

**Gate flags.** At the gate Mat also sees these, each with a recommendation and its do-nothing option:
- D-768 DEFAULT_OMIT: `head` and `shape` are left out of the wire, the sidecar and the API response at their defaults, so today's sidecars and today's bytes don't change.
- D-775 STEP_STYLE: the step's colour and size are two new saved leaves, `step_color` (`#E0AF68`) and `step_size` (32).
- D-777 DUPLICATE: a duplicated step takes the next free number, not the same number; a mark at an edge copies only as far as the image allows, and no step copies once a step 999 exists.

An AC or contract change during execution goes to Mat as a Decision Brief (S12). Its do-nothing option is "record it as a departure and keep the approved text".

**Plan review.** Loop `s72-plan-canonical-2026-11-14-capture-shapes-steps`, `.agent/context/handoffs/2026-11-14-capture-shapes-steps-plan-critical-review.md`. Round 1 (Codex, 12,772,041 tokens): `changes_required`, with F1 (High: DUPLICATE clamped only a box's origin, so a copy could pass the image edge), F2 (High: Ctrl+D could append a step 1000, which every input boundary refuses), F3 (Medium: ELLIPSE_HIT's normalized radius was not the distance to the outline) and F4 (Medium: the arrow hit kept the end-head triangle whatever `head` was). All four are fixed above: DUPLICATE's per-axis room rule and the per-family Ctrl+D matrix with AC-106.24; the 999 stop in DUPLICATE, STEP_PLACE and AC-107.21; ELLIPSE_HIT's polyline distance with AC-106.13's probed cases; and the new HEAD_HIT with AC-106.10 as a Red behaviour test. Round 2 (Codex, 4,383,049 tokens): `approved`, 0 findings, F1 to F4 fixed. Its clerical note is applied in `task.md`: row 1's `_clip_step` stub returns `(None, "dropped")` and row 2's `clip_mark` call passes the five coordinates. Its R3 note stands as written: only the large-ellipse corner of AC-106.13 fails against today's box outline; the other cases are preservation variants, and FAIL_TO_PASS lists only the ids that actually failed. No AC was added or removed (34 and 30).

**Network.** Recommendation: none, because nothing here fetches. The do-nothing option is the same, so there is no brief.

**Token estimate (report only; budgets are off).** Calibrated against:
- Session 68 `capture-redact` (one new mark type through every layer): plan rounds of 8.85M and 4.32M, execution 13.2M;
- Session 71b `capture-tool-flow` (registry and page work): plan rounds of 10.18M and 7.64M (17.81M), execution 12.91M.

This session is two MEUs: one new mark type through every layer, as Session 68 was, plus two new mark fields and a registry chord. The estimates:
- plan review: about 10M for round 1 and about 8M for each recheck, so about 18M to 26M for the loop;
- execution review: about 14M for round 1 and about 7M for a recheck, so about 21M.

**Word meanings.**
- A *line* is an arrow mark with `head: "none"`. A *both arrow* has `head: "both"`.
- An *ellipse* is a rect mark with `shape: "ellipse"`, inscribed in its box.
- A *step* is a `step` mark: a filled disc of diameter `size` centred on `(x, y)`, holding `number`.
- *The pick* is the page's current Arrow head or Box shape choice, used for the next mark drawn.
- *A field* is what MEU-143's FIELD_GUARD names (`isEditableTarget` or a `<select>`).
- *The closed crop* is `[0,width]x[0,height]` in the crop's own pixels (D-676).

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `HEAD_FIELD` | `ArrowAnnotation` gains `head: ArrowHead = "end"` as its last field, with `ArrowHead = Literal["end", "none", "both"]` exported from `domain/capture.py`. `__post_init__` refuses any other value, including `""`, `"\x07"`, `"\ud800"`, `"End"`, `1` and `None`, with `AnnotationValidationError("arrow head must be end, none or both")`, which names the field and not the value (D-767) | `domain/capture.py` |
| `SHAPE_FIELD` | `RectAnnotation` gains `shape: BoxShape = "rect"` as its last field, with `BoxShape = Literal["rect", "ellipse"]`. `__post_init__` refuses any other value with `AnnotationValidationError("box shape must be rect or ellipse")`. Highlight, Redact, Pixelate and Eraser get no shape (D-769) | `domain/capture.py` |
| `DEFAULT_OMIT` | `_annotation_from_wire` reads `head` and `shape` when present and refuses a value outside the Literal. A missing key gives the default. `_annotation_to_wire` writes `head` only when it isn't `"end"` and `shape` only when it isn't `"rect"`. So an old sidecar decodes to the same mark and encodes to the same bytes. The API's output models carry `Field(exclude_if=…)` for the same two defaults (pydantic 2.14.1, probe `C:/Temp/av-kit/s72-probe-exclude-if.txt`). `createDrawnMark` adds `head` or `shape` only when the pick isn't the default. The explicit default is accepted on every input path (D-768) | `services/capture.py`, `schemas/captures.py`, `CapturePage.tsx` |
| `HEAD_BAKE` | A new adapter helper `arrow_shaft_span(from_xy, to_xy, stroke, head) -> tuple[Point, Point] \| None` gives the shaft's ends: for `"none"`, `(from_xy, to_xy)`; for `"end"`, `(from_xy, arrow_shaft_end(…))`, today's value; for `"both"`, both ends pulled back by the head's length, or `None` when the arrow is shorter than two heads. `_apply_arrow` draws the shaft over that span and a head at `to` for `"end"` and `"both"`, plus a head at `from` for `"both"` from `arrowhead_vertices(to_xy, from_xy, stroke)`. The tile mask and SUPERSAMPLE don't change, so an `"end"` arrow bakes to today's bytes (D-767) | `adapter.py` |
| `HEAD_PREVIEW` | `capture-arrow-head.ts` gains `arrowShaftSpan(from, to, stroke, head)`, the TS mirror of `arrow_shaft_span`. `AnnotationMark` draws an arrow's `<line>` over that span and one `<polygon>` per head, and its `<g>` carries `data-head` with the head value (D-767) | `capture-arrow-head.ts`, `CaptureViewport.tsx` |
| `HEAD_HIT` | `hitArrowBody` keeps the shaft test over the whole `from` to `to` segment and tests one head triangle per drawn head: none for `"none"`; `arrowheadVertices(from, to, stroke)` for `"end"`, as today; and that plus `arrowheadVertices(to, from, stroke)` for `"both"`. The endpoint handles and the body handle don't change (D-767) | `capture-hit-test.ts` |
| `ELLIPSE_BAKE` | `_apply_rect` draws `draw.ellipse` over the same box and width for `shape: "ellipse"`, unaliased as today's rectangle is (D-769) | `adapter.py` |
| `ELLIPSE_PREVIEW` | `AnnotationMark` draws an ellipse as `<ellipse data-annotation-type="rect" data-shape="ellipse">` with `cx`, `cy`, `rx` and `ry` from the box and the stroke inset that the `<rect>` uses (D-769) | `CaptureViewport.tsx` |
| `ELLIPSE_HIT` | `hitBody` for an ellipse hits when the press lies within `max(HIT_RADIUS_CSS, HIT_PADDING_CSS)` CSS pixels of the drawn outline. The distance is measured in CSS pixels against the outline sampled as a closed polyline: the centre `(cx, cy)` and half-axes `a` and `b` come from the box in CSS pixels (the box today's outline test uses), the points are `(cx + a cos t, cy + b sin t)` at `t = 2πk / N` with `N = max(64, ceil(π * max(a, b)))`, so no chord is longer than about 2 CSS px, and the distance is the least `distToSegment` over the chords. A normalized radius is not used: it scales the error by the short half-axis, so on a long, thin ellipse a press 50 px beyond a tip would hit. When `min(a, b) < 1` it falls back to the box's outline hit. The resize handles are the box's, because `isBoxMark` already covers `rect`, and the resize keeps `shape` (D-769) | `capture-hit-test.ts` |
| `ELLIPSE_CLIP` | `clip_mark`'s `RectAnnotation` case calls `_clip_ellipse` when `shape == "ellipse"`. It keeps the mark, moved into the crop's pixels, when `0 <= x0`, `0 <= y0`, `x0 + width <= crop width` and `y0 + height <= crop height`, and drops it otherwise. It never clips. `_clip_rect` stays for `shape: "rect"` (D-676 A, D-770) | `domain/capture.py` |
| `HEAD_CLIP` | `_clip_arrow` is unchanged: its `replace` carries `head`. A clipped `"end"` or `"both"` arrow keeps its head at the crop edge, as D-487 does for `"end"` today (D-675) | `domain/capture.py` (unchanged path; stated and tested) |
| `SHAPE_OPTIONS` | A new `capture-shapes.ts` exports `ARROW_HEADS` (`end`, `none`, `both`), `BOX_SHAPES` (`rect`, `ellipse`) and `shapeOption(tool: CaptureTool, selected: Annotation \| null): 'head' \| 'shape' \| null`. It returns `'head'` for the arrow tool with nothing selected or for a selected arrow, `'shape'` for the box tool or a selected `rect`, and `null` otherwise. The options row shows a `SegmentedControl` `capture-arrow-head` (End, None, Both) or `capture-box-shape` (Rectangle, Ellipse) after the stroke control. With nothing selected the control shows the pick. With a mark selected it shows the mark's value, and a pick changes the mark as one undo step and sends no PUT. The pick is page state, starts at the default on mount, and is not saved (D-771) | `capture-shapes.ts` (new), `capture-toolbar.ts`, `CapturePage.tsx`, `CaptureViewport.tsx` |
| `STEP_TYPE` | `domain/capture.py` gains `AnnotationType.Step = "step"` and `StepAnnotation(x: int, y: int, number: int, color: str, size: int)`, frozen like the others. `__post_init__` refuses a non-`int` or `bool` `x`, `y`, `number` or `size`; `x` or `y` below 0; `number` outside 1 to 999; `size` outside 12 to 200; and a `color` that `validate_color` refuses. Each message names the field and not the value. `StepAnnotation` joins the `Annotation` union, and `clip_mark` gets its case (D-772) | `domain/capture.py` |
| `STEP_WIRE` | `_annotation_from_wire` reads a `step` with exactly the keys `type`, `x`, `y`, `number`, `color` and `size`. A missing key is refused, and any other key is refused with `AnnotationValidationError("unexpected step field(s)")`, as redact does. `_annotation_to_wire` writes those keys in that order (D-772) | `services/capture.py` |
| `STEP_CLAMP` | `_clamp_annotation` clamps a step's `x` and `y` as it clamps a text mark's, with `replace` (D-772) | `services/capture.py` |
| `STEP_CLIP` | `_clip_step` applies MARK_CLIP_TEXT's anchor rule: kept, moved into the crop's pixels, when `(x, y)` lies in `[0,width)x[0,height)`, otherwise dropped. `assert_never` in `clip_mark` makes the type check fail until this case exists (D-675) | `domain/capture.py` |
| `STEP_BAKE` | The adapter gains `step_badge_layout(x, y, number, size) -> StepLayout` and `step_text_color(color) -> str`, plus `_apply_step`. The layout is: radius `size / 2`; font px `(size + 1) // 2` for one or two digits and `(size * 4 + 5) // 10` for three; the baseline `y + (font_px * 355 + 500) // 1000`; Pillow anchor `"ms"` at `x`. The disc is filled in `color` through the BAKE_AA tile mask at SUPERSAMPLE 4. The number is drawn with `_load_font(font_px)` in `step_text_color(color)`: `"#000000"` when the colour's WCAG relative luminance is above 0.179, else `"#FFFFFF"` (D-773) | `adapter.py` |
| `STEP_CENTRE` | The badge's ink box centre lies within `max(2, size / 40)` px of `x` across and `max(1, size / 40)` px of `y` down, and the ink lies inside the disc. This is measured in the bake for sizes 12, 32, 64 and 200 and numbers 1, 12 and 999 (AC-107.10; probe `C:/Temp/av-kit/s72-probe-step-centre-acset.txt`: worst 3.5 px across and 0.5 px down). The preview draws the same layout (the same disc, anchor `x`, baseline and font px; AC-107.11 and .12) with `text-anchor="middle"`. jsdom can't measure the preview's ink, so the one measured preview check is in Electron: the badge text's `getBBox()` centre lies within `max(2, size / 40)` px of its circle's `cx` across (AC-107.24). Down, the preview rests on the shared baseline alone (D-773) | `adapter.py`, `CaptureViewport.tsx` |
| `STEP_PREVIEW` | A new `capture-step.ts` exports `stepBadgeLayout` and `stepTextColor`, the TS mirrors, and `nextStepNumber(marks: readonly Annotation[]): number`. `AnnotationMark` draws `<g data-annotation-type="step">` with a `<circle>` and a `<text text-anchor="middle">` at the layout's baseline, in the text mark's font family (D-773) | `capture-step.ts` (new), `CaptureViewport.tsx` |
| `STEP_API` | `StepAnnotationIn` (`type: Literal["step"]`, `x` and `y` `StrictInt` `ge=0`, `number` `StrictInt` `ge=1, le=999`, `color` `StrictStr` with the colour pattern, `size` `StrictInt` `ge=12, le=200`, no defaults, `extra="forbid"`) joins `AnnotationIn`. `_annotations_from_in` passes `head` and `shape` and gets a `StepAnnotationIn` branch. Its loop ends with `assert_never(item)`, so pyright refuses a missing type (D-772) | `schemas/captures.py`, `routes/captures.py` |
| `STEP_MCP` | `mcp-server/src/toolsets/capture.ts` gains a strict `stepAnn` in the mark union, and `arrowAnn` and `rectAnn` gain `head: z.enum([...]).optional()` and `shape: z.enum([...]).optional()` (D-772) | `capture.ts` (MCP) |
| `STEP_ZOD` | `capture-annotate.ts` gains the same three: `head` and `shape` optional enums and a strict `step` schema with the domain's ranges (D-772) | `capture-annotate.ts` |
| `STEP_TOOL` | `CaptureTool` gains `'step'`. `TOOL_BUTTON_IDS` gains `step: 'capture-tool-step'` after `text`. The toolbar's Annotation tool group shows a Step button after Text, with the `ListOrdered` icon, the name `Step`, the hint `Step: Places the next number` and no letter. `TOOL_LETTERS` becomes `Readonly<Record<LetterTool, string>>` with `LetterTool = Exclude<CaptureTool, 'step'>`, and its eight entries don't change (D-776) | `CaptureViewport.tsx`, `capture-toolbar.ts` |
| `STEP_PLACE` | `createDrawnMark` returns `null` for `'step'`. A pointer-down with Step armed, after ARMED_EDIT and the text branch, places one step at the press point rounded and clamped to the image, numbered `nextStepNumber(list)` (one more than the largest step number, or 1). It goes through `applyHistory` as one undo step and the lock-aware selection (LOCK_SELECTS or one-shot). A drag places nothing more. When `nextStepNumber(list)` would be 1000 (a step 999 exists), the tool places nothing, adds no undo step, and the status reads `Step numbers stop at 999` (D-774) | `CapturePage.tsx`, `capture-step.ts` |
| `STEP_STYLE` | `SETTINGS_KEY_TABLE` gains `("capture", "step_color"): SettingSpec("string", "#E0AF68", pattern=COLOR_HEX)` and `("capture", "step_size"): SettingSpec("number", 32, min_number=12, max_number=200, integer=True)` after `tool_lock`. `SettingsPutIn` gains `step_color: str \| None` and `step_size: StrictInt \| None`. `SETTINGS_SCHEMA` and the MCP set schema gain both. `captureStylePutSchema` gains `step_color` (`COLOR_HEX`) and `step_size` (`z.number().int().min(12).max(200)`). `StyleTool` gains `'step'`, `ToolStyle` gains `stepSize`, `TOOL_STYLE_DEFAULTS.step` is `{ color: '#E0AF68', stepSize: 32 }`, `TOOL_STYLE_LEAVES.step` is `{ color: 'step_color', stepSize: 'step_size' }`, `NUMBER_RANGE.stepSize` is `[12, 200]`, and `styleToolFor` and `styleToolOfMark` return `'step'`. The options row shows the colour and a `capture-step-size` scrub field (label `Size`, aria `Step size`), which joins `COLOR_FOCUS_IDS`. `strokeApplies` returns `false` for step. `OptionGroup` gains `'size'`, and `optionGroups` gains one rule right after the text rule: `tool === 'step' \|\| selected?.type === 'step'` gives `['color', 'size']`. The earlier rules still win (crop, the redaction marks, Redact with nothing selected, the eraser, Select with nothing selected, then text) (D-775) | `services/settings.py`, `schemas/settings.py`, `openapi.committed.json`, `settings.ts` (MCP), `settings-schemas.ts`, `capture-tool-style.ts`, `capture-toolbar.ts`, `CapturePage.tsx` |
| `STEP_HIT` | `hitBody` hits a step when the press is within `size / 2` image px of `(x, y)` plus `HIT_PADDING_CSS` CSS px. `bodyHandleImagePoint` and `translateBody` move `(x, y)`, clamped. A step has no resize handle (D-774) | `capture-hit-test.ts` |
| `MARK_LABELS` | `markLabel` names a line `Line n`, an ellipse `Ellipse n` and a step `Step N`, where `n` counts marks of that kind and `N` is the step's number (D-778) | `capture-hit-test.ts` |
| `DUPLICATE` | `commandRegistry.ts` gains `CAPTURE_EDIT_IDS = ['capture:duplicate'] as const`, joined into the `CommandRegistryEntry.id` union, and one entry after `capture:tool_crop`: label `Duplicate mark`, `shortcut: 'Ctrl+D'`, `category: 'capture'`, `page: '/capture'`, `stateful: true`, `palette: false`. Its action dispatches `CAPTURE_EVENTS.duplicate` (`av-kit:capture:duplicate`), which the page listens for. The page publishes its state as a shot open, the crop closed, no text draft, no confirm and a mark selected. Ctrl+D stays out of `RESERVED_CHORDS`. The page listener does nothing when `historyOwnsFocus()` is false (a field or a modal has focus) or a gesture is live. Otherwise it appends `duplicateMark(mark, FIELD_STEP_SHIFT, W, H)` as one undo step and selects the copy, and sends no PUT. `duplicateMark` moves the copy by `d = max(0, min(shift, room))` on each axis, where `room` is how far the mark's far extent can move and stay on the image: for an arrow, its larger endpoint coordinate against `W - 1` (`H - 1` down); for a text or step mark, its anchor against `W - 1`; for a rect of either shape, `x + width` against `W - 1`, because its outline covers the closed box as `_clip_rect` reads it; for highlight, redact, pixelate and eraser, `x + width` against `W`, their half-open cover (D-486). It never moves a copy left or up and never resizes it, so a mark with no room on an axis copies in place on that axis, and a mark filling the image copies in place. It doesn't call `translateBody`, whose box case clamps only the origin, and `translateBody` doesn't change. A duplicated step takes `nextStepNumber(list)`. When that would be 1000, Ctrl+D appends nothing, adds no undo step, keeps the list and the selection, and the status reads `Step numbers stop at 999`, as STEP_PLACE's stop does. A non-step mark still copies beside a step 999. From a field Ctrl+D's default is still prevented, because the chord's state is true, and nothing is copied (D-777) | `commandRegistry.ts`, `capture-commands.ts`, `capture-shapes.ts`, `CapturePage.tsx` |
| `SHAPES_HELP` | The Annotation tools help body (`capture-help-content.ts:27`):<br>• starts `Seven annotation tools: Arrow, Box, Highlight, Text and Step draw on the selected shot;` in place of `Six annotation tools: Arrow, Box, Highlight and Text draw on the selected shot;`;<br>• after the Redact mode sentence, adds `The Head control turns an arrow into a line or gives it a head at both ends, and the Shape control turns a box into an ellipse; with a mark selected, either one changes that mark. Step places the next number at each click.`;<br>• after the nudge sentence, adds `Ctrl+D duplicates the selected mark 10 px down and right and selects the copy.`;<br>• in the resize sentence, `box, highlight, redact, pixelate or eraser` becomes `box, ellipse, highlight, redact, pixelate or eraser`;<br>• after the Shift and Alt sentence, adds `Shift and Alt work the same on an ellipse, and Shift snaps a line to 45 degrees.`<br>The MEU-143 sentences don't change. No section is added | `capture-help-content.ts` |
| `SHAPES_ACTIONS_INDEX` | In `gui-actions-index.md`: `capture:tool_step` (`Step tool`, local canvas) follows `capture:tool_eraser`; `capture:arrow_head` (`Arrow head: End, None or Both`) and `capture:box_shape` (`Box shape: Rectangle or Ellipse`) follow `capture:style_tool`; `capture:duplicate` (`Duplicate mark (Ctrl+D)`) follows `capture:redo`. `capture:style_tool`'s Trigger cell names the step's colour and size, and its route names `step_color` and `step_size` | `gui-actions-index.md` |
| `SHAPES_SPEC` | 09 gains `> **Delivered (Session 72).**` notes after the MEU-106 note (`:992`) and the MEU-107 note (`:1005`). Each names the mechanism ids, its AC range and the plan folder. The rule rows don't change | `09-screenshot-capture.md` |

### Pins that move

The plan-time reads cover:
- the settings key-set pins;
- the toolbar and registry order pins;
- the tool-letter pins;
- the help sentences;
- the chord table;
- the domain enum pins;
- the wire and clamp kind pins;
- every test that lists the capture tools or mark types in full.

Row 1 moves the enum pins and the tool-list pins, row 2 the key-set pins and the mark-type maps, and row 3 (Red) the rest, so Green changes no test file (S2). The tool-list pins move at row 1 because row 1 renders the Step button (§Verification Plan 2): `TOOL_BUTTON_IDS`' values must be `TOOLBAR_BUTTONS` keys, AC-80.8 renders every `TOOLBAR_BUTTONS` entry, and `npm run typecheck` covers `ui/tests/`, so a test whose literal is typed by `CaptureTool`, `StyleTool` or `ToolStyle` fails the type check at row 1 unless it moves there:

| Pin | File and line | Ending | Change |
|---|---|---|---|
| The `AnnotationType` members | `tests/unit/test_domain.py:316-317`, `tests/unit/test_domain_capture.py:32-41` | as each file | gain `Step = "step"` (row 1) |
| The wire's type guard | `tests/unit/test_domain_capture.py:129` | as the file | names `step` among the known types (row 1) |
| AC-130.6's sample of every mark | `tests/unit/test_domain_capture.py:864-876` | as the file | gains one step mark (row 2, once the wire reads it) |
| The clamp kinds | `tests/unit/test_capture_service.py:1208`, `:1247` | CRLF | gain `step` (row 2) |
| AC-36.12 (the capture key set) | `tests/unit/test_capture_service.py:20-40`, `:422` and on | CRLF | `CAPTURE_KEYS` and `CAPTURE_DEFAULTS` gain `step_color` (`#E0AF68`) and `step_size` (32) after `tool_lock` (row 2) |
| AC-105.2 (the style rows follow `annotated_format`) | `tests/unit/test_capture_style_settings.py:51-52` | LF | the nine leaves stay contiguous, and the keys after them become `["tool_lock", "step_color", "step_size"]` (row 2) |
| AC-143.2 (`tool_lock` follows `pixelate_block_size`) | `tests/unit/test_capture_tool_lock.py:62` | LF | the keys after `pixelate_block_size` become `["tool_lock", "step_color", "step_size"]`. `:52` holds, because `tool_lock` still follows `pixelate_block_size` in `SettingsPutIn` (row 2) |
| AC-38.6 (the MCP capture keys) | `mcp-server/tests/capture.test.ts:45-63`, `:194-206`, `:219`, `:229`, `:1723` | CRLF | the same leaves and defaults. AC-105.5's `CAPTURE_KEYS.slice(7, 16)` holds (row 2) |
| `TOOL_LETTERS`' key type | `ui/tests/unit/capture-tool-lock.test.ts:84` | LF | `Readonly<Record<CaptureTool, string>>` becomes `Readonly<Record<LetterTool, string>>`. `:85-86` (8 keys, 8 ids) and `:139-144` hold (row 1, the type check) |
| The toolbar tool order (AC-103.14) | `ui/tests/unit/capture-redact.behavior.test.ts:245`, `:252`, `:255`, `:265` | LF | `keys.slice(4, 7)` becomes `keys.slice(5, 8)`, equal to `['capture-tool-step', REDACT_ID, 'capture-tool-eraser']` (the `TOOLBAR_BUTTONS` entry for Step goes after Text), `Object.keys(ids)` gains `step` after `text`, the rendered `order.slice(at - 1, at + 2)` becomes `['capture-tool-step', REDACT_ID, 'capture-tool-eraser']`, and the title's `8 tools` becomes `9 tools` (row 1) |
| The toolbar tool list (AC-65.1, AC-87.1 negative) | `ui/tests/unit/capture-toolbar.test.ts:25`, `:175-186` | CRLF | `TOOLS` gains `step` after `text`; AC-87.1 negative's sorted list gains `step` and its title's `eight tools` becomes `nine tools` (row 1). The `expectedGroups` model needs no step rule at row 1: row 1's `strokeApplies('step')` is `false`, so both the model and `optionGroups` give `['color']` |
| OPTIONS_BY_TOOL's step rule (AC-65.1's table) | `ui/tests/unit/capture-toolbar.test.ts:28-40`, `:43-71` | CRLF | `MARKS` gains a step mark and `expectedGroups` gains, after its `text` line, `if (!text && (tool === 'step' \|\| selected?.type === 'step')) return ['color', 'size']` (row 3). AC-65.1's table test is then Red by assertion until row 4 |
| The no-shot and hint tables (AC-80.8) | `ui/tests/unit/icon-hints.test.ts:48-60`, `:74-85` | CRLF | `NO_SHOT_IDS` gains `capture-tool-step` and `HINT_OVERRIDE` gains `'capture-tool-step': 'Step: Places the next number'`. `TOOL_LETTER` doesn't change (row 1) |
| The style tool tables (AC-105.1, AC-105.7) | `ui/tests/unit/capture-tool-style.test.ts:19`, `:20`, `:23-29`, `:31-37`, `:72-90`, `:92-98`, `:136-138` | LF | `STYLE_TOOLS` and `TOOLS` gain `step`; `DEFAULTS.step` is `{ color: '#E0AF68', stepSize: 32 }`; `LEAVES.step` is `{ color: 'step_color', stepSize: 'step_size' }`; `FULL` gains `step_color: '#6789AB'` and `step_size: 48`, and `FULL_STYLES.step` is `{ color: '#6789AB', stepSize: 48 }`; `fields` gains `stepSize: 32` and its key list `stepSize` (row 1). `FOR_TOOL`'s fallthrough gives step `null` at row 1, which row 1's `styleToolFor` stub returns |
| The mark-type maps (AC-105.6) | `ui/tests/unit/capture-tool-style.test.ts:52-60`, `:62-70` | LF | `MARKS` and `OF_MARK` (`Record<Annotation['type'], …>`) gain `step` once row 2 joins the step schema to `annotateInSchema`, with `OF_MARK.step` `null`, which row 2's `styleToolOfMark` stub returns (row 2) |
| STYLE_MODEL's step rows (AC-105.6) | `ui/tests/unit/capture-tool-style.test.ts:45-50`, `:62-70` | LF | `FOR_TOOL` maps `step` to `'step'` and `OF_MARK.step` becomes `'step'` (row 3). AC-105.6 is then Red by assertion until row 4 |
| The resize help sentence | `ui/tests/unit/capture-help-content.test.ts:13` | CRLF | `RESIZE_HELP_SENTENCE` names `box, ellipse, highlight, redact, pixelate or eraser` (row 3) |
| The chord table | `ui/tests/unit/fixtures/chord-table.ts` | as the file | gains `['capture:duplicate', 'Ctrl+D', '/capture']` after `capture:save` (row 3). AC-97.1 (`shortcuts.test.ts:312`) is then Red until row 4, and AC-97.5 (`gui-actions-audit.test.ts:485`) until row 5 |
| The registry tool slice | `ui/tests/unit/capture-tool-lock.test.ts:157-161` | LF | holds: `capture:duplicate` goes after `capture:tool_crop`, outside `ids.slice(folder + 1, folder + 9)` |
| The geometry fixture | `ui/tests/e2e/fixtures/capture-geometry.json` | CRLF | gains the keys `arrow_both` and `steps` (row 2), computed by a scratch script under `C:/Temp/av-kit/s72/` from STEP_BAKE's and HEAD_BAKE's formulas. Its readers, `tests/unit/test_capture_adapter.py:35` and `ui/tests/unit/capture-arrow-head.test.ts:19`, read the old keys only, so they hold |

These were read and hold:
- HELP_EDIT_SENTENCE (`capture-help-content.test.ts:7-8`) and the LOCK_HELP sentences: SHAPES_HELP adds sentences after them and changes none;
- no test pins `Six annotation tools`;
- AC-105.5's `CAPTURE_KEYS.slice(7, 16)` (`capture.test.ts`);
- the resize regex `capture-redact.behavior.test.ts:519`;
- `TOOL_LETTERS`' eight letters and the registry's eight letter entries (`capture-tool-lock.test.ts:139-144`, `:157-161`);
- AC-19.17 and AC-23.18, which use `arrayContaining` and `toContain`; the Duplicate entry is `palette: false`;
- AC-97.4 (`common-shortcuts.test.tsx:49`): `capture:duplicate` has no bound control, so `BOUND_CONTROLS` doesn't change;
- AC-131.21's crop wait list (`capture-crop-tool.behavior.test.ts:876-885`) reads every `TOOL_BUTTON_IDS` value and expects it disabled with the crop's reason; the Step button takes `reason={cropReason ?? …}` as every tool button does, so it holds at row 1;
- AC-80.8's title says `14 Capture toolbar buttons`; `TOOLBAR_BUTTONS` already held 16 entries at `5db3623`, and the count is not asserted, so the title stays;
- AC-90.9's and AC-91.8's loops over `TOOLS` (`capture-toolbar.test.ts:201`, `:220`): a selected pixelate or eraser wins over every tool, Step included, so they hold;
- AC-81.1 (`capture-action-row.test.ts:365-379`): `ACTION_BUTTONS` stays disjoint from `TOOLBAR_BUTTONS`.

Before writing, row 1 sweeps `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` again (Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1, Session 66 RULE-1, Session 68 RULE-2, Session 71b RULE-4). It looks for:
- every caller of `ArrowAnnotation(`, `RectAnnotation(`, `_annotation_from_wire`, `_annotation_to_wire`, `_clamp_annotation`, `clip_mark`, `_annotations_from_in`, `createDrawnMark`, `hitBody`, `translateBody`, `markLabel`, `styleToolFor`, `styleToolOfMark`, `TOOL_BUTTON_IDS` and `TOOL_LETTERS`;
- every test that lists the capture tools, the mark types or the capture keys in full, including labels built from a table;
- the literal text this plan rewrites: `Six annotation tools`, `box, highlight, redact, pixelate or eraser`;
- every fake that answers `/settings/capture` and asserts its full key set.

It records the hits with each file's ending in `s72-anchors.txt`, and runs each caller's tests at its row (Session 55 RULE-1). A pin found then and missing here goes into the handoff as a departure.

**Enum-keyed maps (Session 68 RULE-1).** Each map keyed by an extended type gets its entry in row 1, so a missing one fails the type check there:
- `TOOL_BUTTON_IDS: Record<CaptureTool, …>` gains `step`;
- `TOOL_LETTERS` narrows to `LetterTool`;
- `TOOL_STYLE_DEFAULTS` and `TOOL_STYLE_LEAVES` (`Record<StyleTool, …>`) gain `step`;
- `styleToolFor`, `styleToolOfMark` and `strokeApplies`' `unreachable` switches gain `case 'step'`;
- Python's `clip_mark` match gains `case StepAnnotation():`, which `assert-never-probe.py` proves pyright needs.

**Order pins (Sessions 59 and 63).** These orders are pinned:
- the Annotation tool group: Select, Arrow, Box, Highlight, Text, Step, Redact, Smart eraser, then Lock, Crop, History (AC-107.13);
- the registry: the eight letter entries after `capture:open_folder`, then `capture:duplicate` (AC-106.22);
- the options row: colour, then stroke or size, then the Head or Shape control (AC-106.18);
- the settings keys: the nine style leaves, `tool_lock`, `step_color`, `step_size` (AC-107.15).

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| `head` | the Head control, an agent's `avkit_capture annotate`, the API | the UI schema, the MCP schema, `ArrowAnnotationIn`, `_annotations_from_in`, `_annotation_from_wire`, `ArrowAnnotation`, the sidecar, `_clip_arrow`, `_apply_arrow`, the preview | refused outside the Literal at every boundary; omitted at its default (DEFAULT_OMIT); no message names the value |
| `shape` | the Shape control, the agent, the API | the same, with `RectAnnotation`, `_clip_ellipse` or `_clip_rect`, `_apply_rect` | the same |
| A step mark | the Step tool, Duplicate, the agent, the API | the same chain, `StepAnnotation`, `_clamp_annotation`, `_clip_step`, `_apply_step`, the preview, `markLabel` | strict at every boundary: integer fields refuse `bool`, floats and strings, and the colour refuses an empty, control-character and lone-surrogate value |
| `step_color`, `step_size` | the options row (through STYLE_STORE), the agent's `avkit_settings` set, the Settings API | `SettingsPutIn`, `SettingsService._encode`, the app database, `_decode`, `fetchCaptureSettings`, `readToolStyles`, the page | refused at the API (pattern, StrictInt, range) and the service; a bad stored value reads back as the default in `readToolStyles` (AC-107.17) |
| The pick | the Head and Shape controls | `createDrawnMark` | page state; never saved |

Three traces cover the functions between the user's input and the port, using recording fakes (Session 55 RULE-3):
- AC-106.29 traces one MCP `annotate` with a `head: "none"` arrow and a `shape: "ellipse"` rect. It goes through the MCP schema, the API body, `_annotations_from_in` (a recording wrapper), `annotate_and_save`, the sidecar and the bake, and ends at the sidecar's JSON and a sampled baked pixel.
- AC-107.20 traces one MCP step the same way, ending at the sidecar's step keys and the badge's sampled centre pixel.
- AC-107.16 traces one step colour commit from the hex field through `saveCaptureToolStyle` and `captureStylePutSchema` to the recorded PUT body `{ "step_color": "#123456" }`.

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/09-screenshot-capture.md` | SHAPES_SPEC |
| `docs/build-plan/gui-actions-index.md` | SHAPES_ACTIONS_INDEX |

### MEU-106 `capture-line-ellipse-shapes`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `POST /captures/{id}/annotate` (and every route that takes `AnnotationIn`) | `head`, `shape` | `ArrowAnnotationIn` and `RectAnnotationIn` give 422 for any value outside the Literal, `null` included, and the body names no value |
| MCP `avkit_capture` | `head`, `shape` | the strict schema refuses any other value or type |
| The sidecar read-back | `head`, `shape` as stored | `_annotation_from_wire` refuses a value outside the Literal with `AnnotationValidationError`, which names the field |
| UI zod | `head`, `shape` | `annotateInSchema` refuses any other value |
| Keyboard (Ctrl+D) and GUI | a chord, a press | not a trust boundary; the server refuses what the client lets through |

**Input matrix (Session 64 RULE-1).** First, each head against the crop:

| head | Crop inside the arrow's span | Straddling (one end outside) | Wholly outside |
|---|---|---|---|
| `end` | kept, both ends moved (AC-106.16) | clipped at the edge, head kept at the edge (AC-106.16) | dropped (AC-106.16) |
| `none` | kept, `head` kept (AC-106.16) | clipped, `head` kept (AC-106.16) | dropped (AC-106.16) |
| `both` | kept (AC-106.16) | clipped, `head` kept, a head at the edge (AC-106.16) | dropped (AC-106.16) |

Then the ellipse against the closed crop (D-676 A), on a crop 40×30:

| Case | Box in the crop's pixels | Result |
|---|---|---|
| Inside | (5, 5, 20, 10) | kept, moved (AC-106.15) |
| Touching the far edges | (20, 20, 20, 10), so `x0 + w == 40` and `y0 + h == 30` | kept (AC-106.15) |
| Straddling | (30, 5, 20, 10) | dropped, never clipped (AC-106.15) |
| Outside | (50, 50, 5, 5) | dropped (AC-106.15) |
| One past | (21, 20, 20, 10), so `x0 + w == 41` | dropped (AC-106.15) |

Then each modifier against Line and Ellipse:

| Modifier | Line (draw) | Line (endpoint drag) | Ellipse (draw) | Ellipse (corner resize) | Ellipse (edge resize) |
|---|---|---|---|---|---|
| Shift | snaps to 45° (AC-106.21) | snaps about the fixed end (AC-106.21) | a circle (AC-106.21) | keeps the ratio (AC-106.21) | ignored (AC-106.21) |
| Alt | ignored (AC-106.21) | ignored | from the centre (AC-106.21) | ignored | ignored |
| Shift+Alt | snaps | snaps | a circle from the centre (AC-106.21) | keeps the ratio | ignored |

Then Ctrl+D against a mark at each image edge, on a 100×80 shot, by DUPLICATE's room rule:

| Mark | Before | Copy | Case |
|---|---|---|---|
| rect | (10, 10, 20, 20) | (20, 20, 20, 20) | away from the edges (AC-106.23) |
| rect | (0, 0, 20, 20) | (10, 10, 20, 20) | at the left and top edges (AC-106.24) |
| rect | (85, 20, 10, 10) | (89, 30, 10, 10) | 4 px of room across (AC-106.24) |
| rect | (89, 20, 10, 10) | (89, 30, 10, 10) | at the right edge; never (99, 30, 10, 10) (AC-106.24) |
| rect | (20, 69, 10, 10) | (30, 69, 10, 10) | at the bottom edge (AC-106.24) |
| rect | (0, 0, 99, 79) | (0, 0, 99, 79) | filling; never (10, 10, 99, 79) (AC-106.24) |
| ellipse | the rect rows (85, 20, 10, 10), (89, 20, 10, 10), (20, 69, 10, 10) and (0, 0, 99, 79) with `shape: "ellipse"` | the rect rows' copies, `shape` kept | the same edges (AC-106.24) |
| highlight, redact, pixelate and eraser | (90, 20, 10, 10) | (90, 30, 10, 10) | at the right edge, `x + width == W` (AC-106.24) |
| the same four | (20, 70, 10, 10) | (30, 70, 10, 10) | at the bottom edge (AC-106.24) |
| the same four | (0, 0, 100, 80) | (0, 0, 100, 80) | filling (AC-106.24) |
| arrow | (80, 10) to (95, 20) | (84, 20) to (99, 30) | 4 px of room across (AC-106.24) |
| text | anchor (99, 40) | anchor (99, 50) | at the right edge (AC-106.24) |
| step | (50, 79), the only step, number 1 | (60, 79), number 2 | at the bottom edge (AC-106.24) |

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-106.1 | type | The exact signatures (Session 66 RULE-1):<br>• Python: `ArrowHead = Literal["end", "none", "both"]`, `BoxShape = Literal["rect", "ellipse"]`, `ArrowAnnotation.head: ArrowHead = "end"` (last field), `RectAnnotation.shape: BoxShape = "rect"` (last field), `_clip_ellipse(mark: RectAnnotation, left: int, top: int, width: int, height: int) -> tuple[RectAnnotation \| None, MarkCarry]` (the five-coordinate convention of `clip_mark`'s helpers), `arrow_shaft_span(from_xy, to_xy, stroke: int, head: ArrowHead) -> tuple[tuple[float, float], tuple[float, float]] \| None`;<br>• TS: `ArrowHead`, `BoxShape`, `ARROW_HEADS`, `BOX_SHAPES`, `shapeOption(tool: CaptureTool, selected: Annotation \| null): 'head' \| 'shape' \| null`, `duplicateMark(mark: Annotation, shift: number, imageW: number, imageH: number): Annotation`, `arrowShaftSpan(…)`, `CAPTURE_EDIT_IDS`, `CAPTURE_EVENTS.duplicate === 'av-kit:capture:duplicate'`, `LetterTool` | Local Canon: D-767, D-769, D-771, D-777 | passes where it is written (row 2; row 1 adds the names) |
| AC-106.2 | behaviour | HEAD_FIELD: `ArrowAnnotation` defaults `head` to `"end"` and accepts `"none"` and `"both"`. It refuses `""`, `"\x07"`, `"\ud800"`, `"End"`, `1` and `None`, one parametrize id each, with `AnnotationValidationError` whose message holds `head` and not the value (Session 53 RULE-1) | Spec: 09 Line row | the lone-surrogate case raises |
| AC-106.3 | behaviour | SHAPE_FIELD: the same for `RectAnnotation.shape`, with `"rect"` the default and `"ellipse"` accepted. `HighlightAnnotation(…, shape="ellipse")` is a `TypeError` | Spec: 09 Ellipse row | `"Ellipse"` raises |
| AC-106.4 | behaviour | DEFAULT_OMIT on the wire:<br>• `_annotation_to_wire` of a default arrow and a default rect holds no `head` and no `shape` key;<br>• a `"none"` arrow and an `"ellipse"` rect hold them;<br>• `_annotation_from_wire` reads a missing key as the default, reads the explicit default, and refuses `"x"`, `""` and `null`;<br>• a sidecar fixture written at `5db3623` (one arrow, one rect) decodes and re-encodes to the same bytes | Local Canon: D-768 | the explicit-default read |
| AC-106.5 | behaviour | The API and OpenAPI:<br>• `POST /captures/{id}/annotate` with a `"none"` arrow and an `"ellipse"` rect gives 200, and the next GET returns both values;<br>• a default arrow's response holds no `head` key and a default rect's no `shape` key;<br>• `"x"`, `""`, `null` and `1` give 422 for each field, and no body echoes the value;<br>• the OpenAPI document equals the regenerated committed snapshot, and against the base snapshot the only changes are `ArrowAnnotationIn.head`, `RectAnnotationIn.shape`, `StepAnnotationIn`, its member and discriminator mapping in each union that lists the marks, and `SettingsPutIn.step_color` and `.step_size` | Local Canon: D-767, D-768, D-769 | the dropped-field case: without the `_annotations_from_in` change the GET returns `"end"`. Row 2 writes the 422 and OpenAPI blocks, which pass there; row 3 writes the round-trip block, which is Red until row 4's wire and bake |
| AC-106.6 | behaviour | MCP: the annotate schema accepts an arrow with `head: "both"` and a rect with `shape: "ellipse"`, and refuses `head: "End"`, `head: null`, `shape: "circle"` and `shape: 1`. A mark without either is accepted | Local Canon: D-767, D-769 | `"End"` refused |
| AC-106.7 | behaviour | UI zod: `annotateInSchema` accepts the same values and refuses the same, plus `head: "\uD800"` | Local Canon: D-767, D-769 | the lone surrogate |
| AC-106.8 | behaviour | HEAD_BAKE on a 120×60 white image, stroke 3, from (10, 30) to (110, 30):<br>• `"end"` bakes to the same bytes as the base adapter (a SHA-256 taken at row 0);<br>• `"none"` has ink at (108, 30) and no head ink outside the stroke band;<br>• `"both"` has head ink at both ends, and its head vertices equal the fixture's `arrow_both` within 1e-9;<br>• a `"both"` arrow shorter than two heads draws two heads and no shaft | Spec: 09 Line row | the `"end"` hash |
| AC-106.9 | behaviour | HEAD_PREVIEW: `arrowShaftSpan` equals the fixture's `arrow_both` shaft and the `arrows` shaft ends within 1e-9. The viewport renders `data-head` with the mark's value, 0, 1 or 2 `<polygon>` elements for `"none"`, `"end"` and `"both"`, and a `<line>` over the span | Spec: 09 Line row | `"none"` has no polygon |
| AC-106.10 | behaviour | HEAD_HIT through `hitTestMarks` at 1:1 on a (100, 100) to (300, 100) arrow, stroke 20, whose heads reach 90 px back from each tip (probe `C:/Temp/av-kit/s72-plan-r2-geometry-probe.txt`), one id per head:<br>• `"end"`: (240, 125), inside the end head and 25 px off the shaft, hits; (160, 125), where a start head would be, misses;<br>• `"none"`: (240, 125) misses, and (297, 100), on the shaft's last 5 px, hits;<br>• `"both"`: (160, 125) and (240, 125) hit;<br>• for each head, (200, 125), 25 px off the shaft between the heads, misses;<br>• with the mark selected, presses on `from` and `to` give its two endpoint handles, for each head | Spec: 09 Line row; Local Canon: D-767 | `"none"` misses at (240, 125) |
| AC-106.11 | behaviour | ELLIPSE_BAKE: an `"ellipse"` rect (10, 10, 60, 40), stroke 3, on white: the corner pixel (11, 11) stays white, the top centre (40, 11) is ink, and the baked image equals Pillow's `draw.ellipse` over the same box and width | Spec: 09 Ellipse row | the corner stays white |
| AC-106.12 | behaviour | ELLIPSE_PREVIEW: an `"ellipse"` mark renders one `<ellipse data-shape="ellipse">` with the `cx`, `cy`, `rx` and `ry` the box gives, and no `<rect>`. A `"rect"` mark renders today's `<rect>` and no `data-shape` | Spec: 09 Ellipse row | no `<rect>` |
| AC-106.13 | behaviour | ELLIPSE_HIT through `hitTestMarks`, one id per case, presses in CSS px with the image at `ox = oy = 0` (distances from probe `C:/Temp/av-kit/s72-plan-r2-geometry-probe.txt`):<br>• a (10, 10, 200, 120) ellipse at 1:1: the outline at (110, 10) hits; the box corner (11, 11), 29.8 px from the outline, misses; the centre (110, 70) misses;<br>• a wide (10, 10, 200, 20) ellipse at 1:1: (215, 20), 5 px past the right tip, hits; (222, 20), 12 px past, and (260, 20), 50 px past, miss;<br>• a tall (10, 10, 20, 200) ellipse at 1:1: (20, 215) hits; (20, 222) and (20, 260) miss;<br>• the (10, 10, 60, 40) ellipse at scale 2: (80, 20), on the outline, hits; (80, 32), 12 CSS px inside, misses;<br>• the (10, 10, 200, 120) ellipse at scale 0.5: (55, 13), 8 CSS px inside, hits; (55, 17), 12 CSS px inside, misses;<br>• a 1×1 ellipse is hit as its box | Spec: 09 Ellipse row (MEU-100 handles) | (260, 20) misses |
| AC-106.14 | guard | The ellipse's handles: a selected ellipse shows the box's eight handles. A corner drag resizes it, and the result keeps `shape: "ellipse"`. A body drag moves it as one undo step | Spec: 09 Ellipse row | `shape` kept after resize |
| AC-106.15 | behaviour | ELLIPSE_CLIP, one parametrize id per row of the ellipse matrix: inside and touching are kept and moved; straddling, outside and one past are dropped. A rect with the same straddling box is clipped as today (`_clip_rect`) | Spec: 09 Crop row; Human-approved: D-676 | the straddling ellipse is dropped, not clipped |
| AC-106.16 | guard | HEAD_CLIP, one parametrize id per cell of the head matrix (9 ids): the kept and clipped arrows keep their `head`, a clipped arrow's moved end lies on the crop edge, and the outside cases drop | Spec: 09 Crop row; Local Canon: D-675 | `"both"` keeps its head |
| AC-106.17 | behaviour | Crop end to end: `POST /captures/{id}/crop` on a shot whose sidecar holds a `"none"` arrow, a straddling `"both"` arrow, an inside ellipse and a straddling ellipse gives a sidecar with the line, the clipped `"both"` arrow and the inside ellipse, and not the straddling ellipse | Spec: 09 Crop row | the straddling ellipse is absent |
| AC-106.18 | behaviour | SHAPE_OPTIONS display:<br>• with Arrow armed and nothing selected, `capture-arrow-head` shows End pressed after the stroke control;<br>• with Box armed, `capture-box-shape` shows Rectangle pressed;<br>• with Highlight, Text, Redact, Eraser, Step or Select armed and nothing selected, neither control exists;<br>• with a `"both"` arrow selected (Select armed) the Head control shows Both, and with an ellipse selected the Shape control shows Ellipse | Local Canon: D-771 | Highlight shows neither |
| AC-106.19 | behaviour | Draw with a pick: with Arrow armed, a None pick and a drag give a mark `{ type: 'arrow', …, head: 'none' }`; with Box armed, an Ellipse pick and a drag give `shape: 'ellipse'`. The save POST carries both. With the default picks, the drawn marks hold no `head` and no `shape` key. A remount starts at End and Rectangle | Spec: 09 Line and Ellipse rows; Local Canon: D-768, D-771 | the default draw has no `head` key |
| AC-106.20 | behaviour | A pick with a mark selected: with an arrow selected, Both changes its `head` as one undo step, Undo restores `"end"`, and no `PUT /settings/capture` is sent. With a rect selected, Ellipse changes its `shape` the same way. Under Lock, after a box draw, Ellipse changes the just-drawn box | Local Canon: D-771; MEU-105 STYLE_TARGET | no PUT |
| AC-106.21 | behaviour | Modifiers, one parametrize id per cell of the modifier matrix that names an AC: a Shift Line drag from (10, 10) to (50, 22) ends at (52, 10) and keeps `head: "none"`; a Shift Ellipse drag from (10, 10) to (50, 30) draws a 40×40 ellipse; an Alt Ellipse drag from (30, 30) to (40, 35) draws (20, 25, 20, 10); Shift+Alt draws (20, 20, 20, 20); a Shift corner resize keeps 2:1; an edge resize ignores Shift; Alt on a Line does nothing. The helpers are MEU-143's, unchanged | Spec: 09 Line and Ellipse rows (the MEU-143 modifiers apply) | Alt on a Line |
| AC-106.22 | behaviour | DUPLICATE's entry:<br>• the registry holds `capture:duplicate` right after `capture:tool_crop`, with `shortcut: 'Ctrl+D'`, `page: '/capture'`, `stateful: true`, `palette: false` and the label `Duplicate mark`;<br>• `RESERVED_CHORDS` doesn't hold `Ctrl+D`, and `buildShortcutMap(listCommands())` doesn't throw;<br>• the chord table row passes AC-97.1;<br>• `paletteCommands(…, '/capture', all true)` doesn't list it | Spec: 09 Duplicate row (a page-scoped registry entry) | not in the palette |
| AC-106.23 | behaviour | DUPLICATE per mark type, one parametrize id each for arrow, line, rect, ellipse, highlight, text, redact, pixelate, eraser and step: with the mark selected and the surface focused, Ctrl+D appends a copy 10 px down and right with every other field equal, selects the copy, is `defaultPrevented`, and is one undo step. Undo removes the copy and selects nothing. No `PUT /settings/capture` is sent | Spec: 09 Duplicate row | Undo removes only the copy |
| AC-106.24 | behaviour | DUPLICATE at the edges, one parametrize id per row of the Ctrl+D matrix after the first (the ellipse row gives four ids, and each filled-box row one per type): Ctrl+D on the selected mark appends exactly the matrix's copy, with every other field equal, so no copy's far extent leaves the image and no copy moves left, up or changes size | Spec: 09 Duplicate row (clamped) | (89, 20, 10, 10) copies to (89, 30, 10, 10), not (99, 30, 10, 10) |
| AC-106.25 | behaviour | DUPLICATE guards:<br>• with nothing selected, Ctrl+D copies nothing and is not `defaultPrevented`;<br>• with the crop open, a text draft open, or an `aria-modal` element focused, it copies nothing;<br>• from the hex field with a mark selected, it is `defaultPrevented` and copies nothing (FIELD_GUARD's statement for Ctrl+D);<br>• during a live drag, it copies nothing;<br>• with no shot, nothing | Spec: 09 Duplicate row; Session 72 prompt (FIELD_GUARD) | the hex-field case copies nothing |
| AC-106.26 | behaviour | MARK_LABELS: after an arrow, a line, a box and an ellipse are drawn, the mark labels read `Arrow 1`, `Line 1`, `Box 1` and `Ellipse 1` | Local Canon: D-778 | `Line 1`, not `Arrow 2` |
| AC-106.27 | behaviour | SHAPES_HELP: the Annotation tools body holds each new sentence exactly, starts `Seven annotation tools`, holds the moved resize sentence, and still holds every MEU-143 sentence; `Six annotation tools` is absent | Spec: 09 Line, Ellipse, Duplicate and Step rows | `Six annotation tools` is absent |
| AC-106.28 | behaviour | Electron, on a seam with `tool_lock: false`:<br>• A arms Arrow; a None pick and a drag draw a line;<br>• R arms Box; an Ellipse pick and a drag draw an ellipse;<br>• with the ellipse selected, Ctrl+D adds a second ellipse and selects it;<br>• Save POSTs three marks, the line with `head: "none"` and both ellipses with `shape: "ellipse"`.<br>Every locator is checked with `toBeVisible()` before it is clicked | Spec: 09 Line, Ellipse and Duplicate rows | the POST body |
| AC-106.29 | behaviour | Trace (Session 55 RULE-3): one MCP annotate traced through the MCP schema, the API body, `_annotations_from_in` (a recording wrapper), the domain marks, the sidecar JSON (`head: "none"`, `shape: "ellipse"`) and the bake, where a pixel at the line's far end is ink and the ellipse's box corner is not | Session 55 RULE-3 | the wrapper saw `head: "none"` |
| AC-106.30 | guard | Unchanged behaviour: MEU-100's handles, MEU-105's style tests, MEU-143's tool-flow tests, every `"end"` arrow bake and every `"rect"` bake byte for byte, Ctrl+C (D-678), and `_clip_rect` for `shape: "rect"` | Local Canon: D-675, D-678 | — |
| AC-106.31 | guard | No pick, `head` or `shape` value reaches the capture settings: after a None pick, an Ellipse pick and a draw, the recorded PUTs are empty | Local Canon: D-771 | — |
| AC-106.32 | check | SHAPES_ACTIONS_INDEX: `capture:tool_step` follows `capture:tool_eraser`; `capture:arrow_head` and `capture:box_shape` follow `capture:style_tool`; `capture:duplicate` follows `capture:redo` and its Trigger names `Ctrl+D`; `gui-actions-audit.test.ts` passes | Local Canon: GUI actions index | row 5's check exits 1 before row 5 |
| AC-106.33 | check | SHAPES_SPEC for MEU-106: 09's Delivered (Session 72) note follows `:992`, names AC-106.1 to AC-106.34 and the plan folder, and 09 keeps CRLF | Local Canon: 09 Delivered notes | row 5's check exits 1 before row 5 |
| AC-106.34 | guard | `assert_never` in `_annotations_from_in`: `assert-never-probe.py` runs pyright on a scratch copy of `routes/captures.py` with the `StepAnnotationIn` branch removed, and pyright reports an error at the `assert_never` line | Local Canon: D-772; D-675 | the probe's copy fails pyright |

**Guards.** These pass after rows 1, 2 and 4:
- Python: `tests/unit/test_domain.py`, `tests/unit/test_domain_capture.py`, `tests/unit/test_capture_service.py`, `tests/unit/test_capture_adapter.py`, `tests/unit/test_capture_style_settings.py`, `tests/unit/test_capture_tool_lock.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_flatten.py`, `tests/e2e/test_api_capture_style.py`, `tests/e2e/test_api_capture_tool_lock.py`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_js_runtime.py` and `tests/e2e/test_api_openapi.py`.
- MCP: `mcp-server/tests/capture.test.ts`, `settings-runtime.test.ts`, `tools-parity.test.ts`, `action-index.test.ts` and the `tests/audit/` suite.
- UI: `capture-toolbar.test.ts`, `capture-page.behavior.test.ts`, `capture-action-row.test.ts`, `capture-help-content.test.ts`, `capture-redact.behavior.test.ts`, `capture-crop-tool.behavior.test.ts`, `capture-text-lines.behavior.test.ts`, `capture-style-flow.behavior.test.ts`, `capture-tool-style.test.ts`, `capture-tool-lock.test.ts`, `capture-tool-flow.behavior.test.ts`, `capture-arrow-head.test.ts`, `capture-hit-test.test.ts`, `capture-page.test.ts`, `common-shortcuts.test.tsx`, `command-palette.test.ts`, `shortcuts.test.ts`, `icon-hints.test.ts` and `gui-actions-audit.test.ts`.

**Spec sufficiency.** Every MEU-106 rule has an AC:

| Rule | ACs |
|---|---|
| Line: `head` with the default `"end"`, a Line is `"none"` | AC-106.2, .4 to .10, .19, .26, .28, .29 |
| Ellipse: `shape` with the default `"rect"`, the MEU-100 handles | AC-106.3 to .7, .11 to .14, .19, .26, .28, .29 |
| Duplicate: Ctrl+D, offset, clamped, selects the copy, a page-scoped entry | AC-106.22 to .25, .28 |
| Crop: `head` rides `_clip_arrow`, tested per value | AC-106.16, .17 |
| Crop: MARK_CLIP_ELLIPSE (D-676 A) | AC-106.15, .17 |
| The MEU-143 modifiers apply | AC-106.21 |
| Docs | AC-106.27, .32, .33 |

### MEU-107 `capture-step-mark`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `POST /captures/{id}/annotate` | a `step` mark | `StepAnnotationIn` gives 422 for a missing field, an extra field, a `bool`, float or string integer, an out-of-range value and a bad colour; the body names no value |
| API `PUT /settings/capture` | `step_color`, `step_size` | the pattern and StrictInt give 422; the service's range check gives 422; a 401- to 4300-digit integer gives 422 and 4301 digits or more give 400 (the parser's limit) |
| MCP `avkit_capture`, `avkit_settings` | the same | the strict schemas refuse what they don't list |
| The sidecar read-back | a stored step | `_annotation_from_wire` refuses a missing or extra key and every value `StepAnnotation` refuses |
| Settings read-back | the stored leaves | `_decode` and `readToolStyles` read a bad value as the default (AC-107.17) |
| GUI | a press | not a trust boundary |

**Input matrix (Session 64 RULE-1).** The step's fields against each boundary:

| Value | Domain | Wire | API | MCP | UI zod |
|---|---|---|---|---|---|
| `x = -1` | refused (AC-107.2) | refused (AC-107.3) | 422 (AC-107.6) | refused (AC-107.7) | refused (AC-107.8) |
| `x = true` | refused | refused | 422 | refused | refused |
| `x = 1.5` | refused | refused | 422 | refused | refused |
| `number = 0`, `1000` | refused | refused | 422 | refused | refused |
| `size = 11`, `201` | refused | refused | 422 | refused | refused |
| `color = ""`, `"\x07"`, `"\ud800"` | refused | refused | 422 | refused | refused |
| an extra key `"label"` | — | `unexpected step field(s)` | 422 | refused | refused |

And the step against the crop, on a crop 40×30: `(0, 0)` kept; `(39, 29)` kept; `(40, 5)` dropped; `(5, 30)` dropped; `(-1, 5)` before the move dropped (AC-107.5).

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-107.1 | type | The exact signatures (Session 66 RULE-1):<br>• Python: `AnnotationType.Step = "step"`; `StepAnnotation(x: int, y: int, number: int, color: str, size: int)`, frozen; `StepAnnotationIn`; `step_badge_layout(x: int, y: int, number: int, size: int) -> StepLayout` with `StepLayout(radius: float, font_px: int, baseline: int)`; `step_text_color(color: str) -> str`; `_clip_step(mark: StepAnnotation, left: int, top: int, width: int, height: int) -> tuple[StepAnnotation \| None, MarkCarry]`;<br>• TS: `CaptureTool` holds `'step'`; `StyleTool` holds `'step'`; `ToolStyle.stepSize?: number`; `stepBadgeLayout(x: number, y: number, n: number, size: number): { radius: number; fontPx: number; baseline: number }`; `stepTextColor(color: string): '#000000' \| '#FFFFFF'`; `nextStepNumber(marks: readonly Annotation[]): number`; the zod `step` schema; the MCP `stepAnn` | Local Canon: D-772, D-773, D-775 | passes where it is written (row 2; row 1 adds the names) |
| AC-107.2 | behaviour | STEP_TYPE: a valid step builds. Each refused value in the matrix's Domain column raises `AnnotationValidationError` whose message names the field and not the value, one parametrize id each (Session 53 RULE-1) | Spec: 09 Mark row | `x = true` raises |
| AC-107.3 | behaviour | STEP_WIRE: a step round-trips through `_annotation_to_wire` and `_annotation_from_wire` with exactly the keys `type, x, y, number, color, size` in that order. A missing `size` and the extra `label` are refused, the latter with `unexpected step field(s)` | Spec: 09 Mark row (through every layer) | the extra key |
| AC-107.4 | behaviour | STEP_CLAMP: `_clamp_annotation` of a step at (500, -3) on a 100×80 image gives the clamp a text mark at the same point gets, and keeps `number`, `color` and `size` | Spec: 09 Mark row | `number` kept |
| AC-107.5 | behaviour | STEP_CLIP, one parametrize id per crop case in the matrix: kept steps move into the crop's pixels; dropped ones are gone. `assert-never-probe.py` runs pyright on a scratch copy of `domain/capture.py` without `case StepAnnotation():` and pyright reports the `assert_never` line | Spec: 09 Crop row; Local Canon: D-675 | `(40, 5)` is dropped |
| AC-107.6 | behaviour | STEP_API: an annotate POST with a step gives 200, and the next GET returns it with the same keys. Each refused value in the API column gives 422, and no body echoes it. `_annotations_from_in` builds a `StepAnnotation` (a recording wrapper sees it) | Spec: 09 Mark row | the GET returns the step |
| AC-107.7 | behaviour | STEP_MCP: the annotate schema accepts a step and refuses each value in the MCP column | Spec: 09 Mark row | the extra key |
| AC-107.8 | behaviour | STEP_ZOD: `annotateInSchema` accepts a step and refuses each value in the UI column | Spec: 09 Mark row | `x = 1.5` |
| AC-107.9 | behaviour | STEP_BAKE's contrast: `step_text_color` gives `#000000` for `#E0AF68`, `#FFFFFF` (white), `#FFFF00`, `#00FF00` and `#FF0000` (luminance 0.2126, above 0.179), and `#FFFFFF` for `#000000`, `#1A1B26` and `#0000FF` (0.0722). A baked step's disc pixel at `(x, y - radius + 2)` has the mark's colour, and the number's ink has the text colour | Local Canon: D-773 | `#FF0000` gets black, not white |
| AC-107.10 | behaviour | STEP_CENTRE in the bake, one parametrize id per size and number pair (12 ids): the ink box centre is within the tolerance, and the ink lies inside the disc | Spec: 09 Mark row (centred in the bake); Local Canon: D-773 | size 200, number 1 |
| AC-107.11 | behaviour | STEP_PREVIEW: a step renders one `<g data-annotation-type="step">` with a `<circle>` at `(x, y)` of radius `size / 2` in the mark's colour, and a `<text text-anchor="middle">` at `x` and the layout's baseline, holding the number in `stepTextColor`'s colour. The preview's layout equals `step_badge_layout` for the 12 pairs (AC-107.12) | Spec: 09 Mark row (centred in the preview) | the text's `x` equals the mark's `x` |
| AC-107.12 | behaviour | Parity: the fixture's `steps` key, written by the scratch script from `step_badge_layout`, equals `stepBadgeLayout` for the 12 pairs exactly, and equals the adapter's values when read by `test_capture_step.py` | Spec: 09 Mark row (the preview and the bake alike) | one pair's baseline |
| AC-107.13 | behaviour | STEP_TOOL: the Annotation tool group's order is Select, Arrow, Box, Highlight, Text, Step, Redact, Smart eraser, then Lock, Crop, History. The Step button carries the `ListOrdered` icon, the hint `Step: Places the next number`, and no `aria-keyshortcuts`. `TOOL_BUTTON_IDS.step` is `capture-tool-step`. With no shot it is disabled with the reason. No letter arms it | Local Canon: D-776 | no `aria-keyshortcuts` |
| AC-107.14 | behaviour | STEP_PLACE:<br>• with Step armed, a press at (20.4, 30.6) places step 1 at (20, 31), and a second press places step 2;<br>• with steps 1, 2 and 3, deleting 2 and pressing places 4;<br>• a press and drag places one step at the press point;<br>• each place is one undo step;<br>• under Lock the tool stays and the new step is selected; one-shot returns to Select with it selected;<br>• with a step numbered 999 present, a press places nothing and the status reads `Step numbers stop at 999` | Spec: 09 Mark row; Local Canon: D-774 | the 999 case |
| AC-107.15 | behaviour | STEP_STYLE at the service and the API:<br>• `SETTINGS_KEY_TABLE` holds `step_color` and `step_size` after `tool_lock` with the defaults `#E0AF68` and 32, and a fresh store reads them as a `str` and an `int`;<br>• `PUT /settings/capture` with `{ "step_color": "#123456", "step_size": 48 }` gives 200;<br>• `"123456"`, `""`, `"\u0007"`, `"\ud800"`, `11`, `201`, `48.0`, `true` and `"48"` give 422, and no body echoes the value;<br>• a 401-digit `step_size` gives 422 and a 4301-digit one gives 400 (the known parser limit, D-775) | Spec: 09 Mark row; Local Canon: D-775 | `48.0` gives 422 |
| AC-107.16 | behaviour | STEP_STYLE in the UI:<br>• with Step armed, the options row shows `capture-color` with the saved `step_color` and `capture-step-size` with the saved `step_size`, and no stroke control;<br>• a hex commit sends one PUT whose body is exactly `{ "step_color": "#123456" }` (the trace), and the next step has that colour;<br>• a scrub sends `{ "step_size": … }`;<br>• **held GET:** with the page's GET held, a size commit shows the new size at once, and when the GET answers the old size the field keeps the new one;<br>• **failed GET:** with the GET failing (500) and nothing committed, the field shows 32; after a commit whose PUT succeeds, a failing refetch still shows the committed size;<br>• with a step selected, a colour commit restyles it as one undo step and sends no PUT | Session 71 RULE-1; Local Canon: D-775; MEU-105 STYLE_STORE, STYLE_TARGET | the held GET |
| AC-107.17 | behaviour | `readToolStyles` on bad stored leaves: `step_size` of `11`, `201`, `48.5`, `"48"` and `true`, and `step_color` of `""`, `"\u0007"`, `"\uD800"` and `"red"`, each read as the default, one id each | Session 53 RULE-1 | the lone surrogate reads the default |
| AC-107.18 | behaviour | STEP_HIT: a press inside the badge selects the step; a press 2 px outside its radius plus the padding doesn't. Under Lock with Step armed, a drag on the just-placed badge moves it as one undo step and places nothing (ARMED_EDIT). Arrow keys nudge a selected step. A selected step shows no resize handle | Spec: 09 Mark row; MEU-143 ARMED_EDIT, LOCK_SELECTS | the drag places nothing |
| AC-107.19 | behaviour | MARK_LABELS: steps numbered 1 and 4 are labelled `Step 1` and `Step 4` | Local Canon: D-778 | `Step 4`, not `Step 2` |
| AC-107.20 | behaviour | Trace (Session 55 RULE-3): one MCP annotate with a step traced through the MCP schema, the API body, `_annotations_from_in` (a recording wrapper), `StepAnnotation`, `_annotation_to_wire` (the sidecar's step keys) and the bake, where the pixel at the badge's top inner edge has the mark's colour | Session 55 RULE-3 | the wrapper saw one `StepAnnotation` |
| AC-107.21 | behaviour | DUPLICATE on a step:<br>• with steps 1 and 2 and step 1 at (20, 20) selected, Ctrl+D adds step 3 at (30, 30) with the same colour and size and selects it; Undo removes step 3 and selects nothing, and the next Step press places 3;<br>• with steps 999 and 5 and step 5 selected, Ctrl+D is `defaultPrevented`, appends nothing, leaves Undo as it was, keeps step 5 selected and the list unchanged, and the status reads `Step numbers stop at 999`;<br>• the same with step 999 itself selected;<br>• with step 999 and a rect, and the rect selected, Ctrl+D copies the rect as usual | Local Canon: D-777, D-774 | no step 1000 is appended |
| AC-107.22 | behaviour | Crop end to end: `POST /captures/{id}/crop` on a shot whose sidecar holds an inside step and an outside step gives a sidecar with the inside step moved into the crop's pixels and the outside step gone | Spec: 09 Crop row | the outside step is gone |
| AC-107.23 | behaviour | The export paths bake steps: the annotated export, the flatten and the copy-image bake each draw a step's disc, through the same adapter call (one test per path, on fakes) | Spec: 09 Mark row (the bake) | the flatten draws the disc |
| AC-107.24 | behaviour | Electron, on a seam with `tool_lock: true`: the Step button arms Step; two presses place steps 1 and 2; the second stays selected; the first badge's `<text>` `getBBox()` centre lies within `max(2, size / 40)` px of its `<circle>`'s `cx` across (STEP_CENTRE's preview check); Save POSTs both with their numbers. Every locator is checked with `toBeVisible()` before it is clicked | Spec: 09 Mark row | the POST body |
| AC-107.25 | behaviour | SHAPES_HELP's step sentence: the body holds `Step places the next number at each click.` | Spec: 09 Mark row | — |
| AC-107.26 | behaviour | STEP_STYLE at MCP: `SETTINGS_SCHEMA.namespaces.capture` lists `step_color` and `step_size` with their defaults after `tool_lock`. The set schema accepts `{ namespace: "capture", step_size: 48 }` and refuses `step_size: 48.5` and `"48"` | Local Canon: D-775 | `48.5` refused |
| AC-107.27 | guard | The Settings card: after a step style PUT, the Capture card's unsaved edit stays, and its Save sends a body with exactly today's seven keys | Session 55 RULE-1 (the settings store's callers) | no step leaf in the body |
| AC-107.28 | guard | Unchanged behaviour: every other mark's wire, clamp, clip and bake; the eight letters; the text tool's draft; MEU-105's style tests and MEU-143's tool-flow tests | Local Canon: D-675 | — |
| AC-107.29 | guard | No step style value enters the mark list beyond the step's own `color` and `size`: after a step colour commit with nothing selected, the save POST's marks hold exactly their earlier keys | Spec: 09 Tool style row (never mark JSON) | — |
| AC-107.30 | check | SHAPES_SPEC for MEU-107: 09's Delivered (Session 72) note follows `:1005`, names AC-107.1 to AC-107.30 and the plan folder, and 09 keeps CRLF | Local Canon: 09 Delivered notes | row 5's check exits 1 before row 5 |

**Guards.** MEU-106's guard list, plus `tests/unit/test_capture_step.py` and `tests/e2e/test_api_capture_step.py` after row 2.

**Spec sufficiency.** Every MEU-107 rule has an AC:

| Rule | ACs |
|---|---|
| Mark: `step {x, y, number, color, size}` through every layer | AC-107.1 to .8, .20, .23, .24 |
| Mark: centred in the preview and the bake alike | AC-107.9 to .12, .24 |
| Crop: MARK_CLIP_TEXT's anchor rule; `assert_never` | AC-107.5, .22 |
| The tool, the place and the selection | AC-107.13, .14, .18, .19, .21 |
| The step style (STYLE_STORE) | AC-107.15 to .17, .26, .27 |
| Docs | AC-107.25, .30 |

### Files Modified

The endings come from the plan-time Python byte count (`C:/Temp/av-kit/s72/endings.py`). Row 0 records them again, with SHA-256, in `s72-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/domain/capture.py` (`HEAD_FIELD`, `SHAPE_FIELD`, `STEP_TYPE`, `ELLIPSE_CLIP`, `STEP_CLIP`) | as measured at row 0 | 1, 4 |
| `packages/core/src/avkit_core/domain/enums.py` (`AnnotationType.Step`) | as measured | 1 |
| `packages/core/src/avkit_core/services/capture.py` (`DEFAULT_OMIT`, `STEP_WIRE`, `STEP_CLAMP`) | as measured | 1, 2, 4 |
| `packages/core/src/avkit_core/services/settings.py` (`STEP_STYLE`) | CRLF | 2 |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` (`HEAD_BAKE`, `ELLIPSE_BAKE`, `STEP_BAKE`) | as measured | 1, 4 |
| `packages/api/src/avkit_api/schemas/captures.py` (`STEP_API`, `DEFAULT_OMIT`) | as measured | 2 |
| `packages/api/src/avkit_api/routes/captures.py` (`STEP_API`'s `_annotations_from_in`) | as measured | 2 |
| `packages/api/src/avkit_api/schemas/settings.py` (`STEP_STYLE`) | CRLF | 2 |
| `openapi.committed.json` (regenerated) | as the generator writes (CRLF today) | 2 |
| `mcp-server/src/toolsets/capture.ts` (`STEP_MCP`) | as measured | 2 |
| `mcp-server/src/toolsets/settings.ts` (`STEP_STYLE`) | CRLF | 2 |
| `ui/src/renderer/src/features/capture/capture-annotate.ts` (`STEP_ZOD`) | as measured | 1, 2 |
| `ui/src/renderer/src/features/capture/capture-shapes.ts` (new; `SHAPE_OPTIONS`, `DUPLICATE`'s `duplicateMark`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-step.ts` (new; `STEP_PREVIEW`, `nextStepNumber`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-arrow-head.ts` (`arrowShaftSpan`) | as measured | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-hit-test.ts` (`HEAD_HIT`, `ELLIPSE_HIT`, `STEP_HIT`, `MARK_LABELS`) | as measured | 4 |
| `ui/src/renderer/src/features/capture/capture-transform.ts` (the resize keeps `shape`, if row 4 finds it rebuilds the mark) | as measured | 4 |
| `ui/src/renderer/src/features/capture/capture-tool-style.ts` (`STEP_STYLE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-toolbar.ts` (`STEP_TOOL`, `LetterTool`, the `step` option group, `strokeApplies`) | CRLF | 1, 4 |
| `ui/src/renderer/src/features/capture/capture-commands.ts` (`CAPTURE_EVENTS.duplicate`) | as measured | 1 |
| `ui/src/renderer/src/features/settings/settings-schemas.ts` (`captureStylePutSchema`) | CRLF | 2 |
| `ui/src/renderer/src/registry/commandRegistry.ts` (`DUPLICATE`) | LF | 1, 4 |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` (`CaptureTool`, `HEAD_PREVIEW`, `ELLIPSE_PREVIEW`, `STEP_PREVIEW`, the options row) | CRLF | 1, 4 |
| `ui/src/renderer/src/features/capture/CapturePage.tsx` (`DEFAULT_OMIT`, `SHAPE_OPTIONS`, `STEP_PLACE`, `DUPLICATE`, the published state) | CRLF | 4 |
| `ui/src/renderer/src/features/capture/capture-help-content.ts` (`SHAPES_HELP`) | CRLF | 4 |
| `ui/tests/e2e/test-ids.ts` (the new ids after the MEU-105 block) | as measured | 1 |
| `ui/tests/e2e/fixtures/capture-geometry.json` (`arrow_both`, `steps`) | CRLF | 2 |
| the enum pins (`tests/unit/test_domain.py`, `tests/unit/test_domain_capture.py`) | as each file | 1, 2 |
| `tests/unit/test_capture_service.py`, `mcp-server/tests/capture.test.ts` (moved pins; AC-106.6, AC-107.7 and AC-107.26 appended to the MCP file) | CRLF | 2 |
| `tests/unit/test_capture_style_settings.py`, `tests/unit/test_capture_tool_lock.py` (moved order pins) | LF | 2 |
| `tests/unit/test_capture_shapes.py` (new; AC-106.1 Python, .2 to .4, .8, .11, .15, .16, .34's probe call, AC-106.30's Python half) and `tests/unit/test_capture_step.py` (new; AC-107.1 Python, .2 to .5, .9, .10, .12's Python half, .15's service half, .23, AC-107.28's Python half) | LF | 2, 3 |
| `tests/e2e/test_api_capture_shapes.py` (new; AC-106.5, .17, .29) and `tests/e2e/test_api_capture_step.py` (new; AC-107.6, .15's API half, .20, .22) | LF | 2, 3 |
| `ui/tests/unit/capture-shapes.test.ts` (new; AC-106.1 TS, .7, AC-107.1 TS, .8 and .17 at row 2; AC-106.9, .10, .13, .22, .26, AC-107.11's layout half, .12 and .19 at row 3) | LF | 2, 3 |
| `ui/tests/unit/capture-shapes.behavior.test.ts` (new; AC-106.12, .14, .18 to .21, .23 to .25, .31, AC-107.11, .13, .14, .16, .18, .21, .27, .29) | LF | 3 |
| the moved pins in §Pins that move, at the row each names | as each file | 1, 2, 3 |
| `ui/tests/unit/capture-toolbar.test.ts` (`TOOLS`, AC-87.1 negative at row 1; `MARKS` and the `expectedGroups` step rule at row 3) | CRLF | 1, 3 |
| `ui/tests/unit/capture-tool-style.test.ts` (the style tables at row 1, the mark-type maps at row 2, STYLE_MODEL's step rows at row 3) | LF | 1, 2, 3 |
| `ui/tests/unit/icon-hints.test.ts` (`NO_SHOT_IDS`, `HINT_OVERRIDE`) | CRLF | 1 |
| `ui/tests/unit/capture-redact.behavior.test.ts` (AC-103.14's order pins) | LF | 1 |
| `ui/tests/e2e/capture-inbox.test.ts` (AC-106.28 and AC-107.24 appended) | LF | 3 |
| `ui/tests/unit/capture-tool-lock.test.ts` (`:84`'s key type at row 1; a reused harness helper if row 3 imports or extends it) | LF | 1, 3 |
| `ui/tests/unit/capture-tool-flow.behavior.test.ts`, `ui/tests/unit/capture-style-flow.behavior.test.ts` (reused harness helpers, if row 3 imports or extends them; Session 71b RULE-3) | LF | 3 |
| `docs/execution/plans/2026-11-13-capture-redact/assert-never-probe.py` is read, and this folder's copy is written | LF | plan |
| `docs/build-plan/gui-actions-index.md` (`SHAPES_ACTIONS_INDEX`) | CRLF | 5 |
| `docs/build-plan/09-screenshot-capture.md` (`SHAPES_SPEC`) | CRLF | 5 |

Before it writes, each row measures the file's endings with Python bytes and then writes in that ending. A scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3). Every doc write ends with a check for lone CR and for a line ending that differs from the file's own (Session 70 RULE-5). The session gate's scope-paths step allows exactly this table's paths, this folder and the project files below, so a helper module a row reuses has to be listed here first (Session 71b RULE-3).

**Byte-hash guard (Session 50).** AC-51.6 and AC-81.13 hash `ui/tests/e2e/test-ids.ts` up to `// MEU-51 primitive harness IDs.`. The new ids go after the MEU-105 block, below that boundary: `CAPTURE_TOOL_STEP`, `CAPTURE_STEP_SIZE`, `CAPTURE_STEP_SIZE_SCRUB`, `CAPTURE_ARROW_HEAD` with `_END`, `_NONE` and `_BOTH`, and `CAPTURE_BOX_SHAPE` with `_RECT` and `_ELLIPSE`. Row 1 hashes the prefix before and after its write and records both in `s72-anchors.txt`; they must be equal. The session gate runs `ui/tests/unit/capture-action-row.test.ts` on its own, and the handoff names the hash it reads.

### Project files

These project files are written:
- `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF) and `docs/BUILD_PLAN.md` (LF), through `meu_status.py`: `ready_for_review` at row 6 and `approved` at H2-2;
- the grouping file (CRLF): row 48 (`:127`) becomes `executed (Session 72)` with this plan folder, and the band follows D-779;
- the two handoffs, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- `C:/Temp/av-kit/session-73-prompt.md`, written after the next-work probe at H2;
- this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| The B-7 context menu (Duplicate from a right-click) | 09's Duplicate row names Ctrl+D only; the Session 72 prompt rules it out |
| A tool letter for Step, Line or Ellipse | 09's Letters row names eight tools; D-776 |
| Separate Line and Ellipse tool buttons | D-776 (asked at the gate as D-781) |
| Saving the Head or Shape pick | D-771: page state, as D-680 keeps the Redact mode |
| Renumbering steps after a delete | 09's Mark row doesn't name it; STEP_PLACE takes one more than the largest |
| Clipping an ellipse at the crop edge | D-676 A |
| An ellipse for Highlight, Redact, Pixelate or Eraser | 09's Ellipse row names `rect` only |
| Changing the JSON parser's digit limit for integer leaves | the known big-integer issue; pinned, not fixed (AC-107.15) |
| MEU-127 | not this session's |
| Members-only URLs or ids, `npm run dist`, the live MCP audit | Session 72 prompt |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after H2-2. MEU-106 (`meu-status.yaml:2771`) and MEU-107 (`:2797`) are `pending`, with MEU-100, MEU-105 and MEU-143 `approved` (`C:/Temp/av-kit/s72-prereq-status.txt`). H2 sets both to `approved` through `meu_status.py` after Codex approves.

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the execute words with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** Checks:
   - MEU-100, MEU-105 and MEU-143 are `approved`;
   - MEU-106 and MEU-107 are `pending`;
   - `5db3623` is an ancestor of `HEAD`.
3. **Shapes (S7, Session 61 RULE-3).** Checks by name the shapes this plan relies on:
   - `ArrowAnnotation`, `RectAnnotation`, `TextAnnotation`, `clip_mark`, `_clip_arrow`, `_clip_rect`, `_clip_text` and `assert_never` in `domain/capture.py`;
   - `_annotation_from_wire`, `_annotation_to_wire`, `_clamp_annotation` and `unexpected redact field(s)` in `services/capture.py`;
   - `arrowhead_vertices`, `arrow_shaft_end`, `_load_font`, `_apply_arrow`, `_apply_rect` and `SUPERSAMPLE` in `adapter.py`;
   - `ArrowAnnotationIn`, `RectAnnotationIn`, `RedactAnnotationIn` and `AnnotationIn` in `schemas/captures.py`, and `_annotations_from_in` in `routes/captures.py`;
   - the `tool_lock` row and `SettingsPutIn.tool_lock`;
   - `arrowAnn`, `rectAnn` and `redactAnn` in the MCP capture toolset, and `tool_lock` in its settings toolset;
   - `annotateInSchema`, `captureStylePutSchema`, `TOOL_STYLE_LEAVES`, `NUMBER_RANGE`, `styleToolFor`, `styleToolOfMark`, `TOOL_BUTTON_IDS`, `TOOL_LETTERS`, `strokeApplies`, `optionGroups`, `hitBody`, `translateBody`, `markLabel`, `isBoxMark`, `createDrawnMark`, `historyOwnsFocus`, `CAPTURE_EVENTS`, `CAPTURE_TOOL_IDS`, `capture:tool_crop` and `RESERVED_CHORDS`;
   - the `Six annotation tools` sentence and the resize sentence;
   - `capture:tool_eraser`, `capture:style_tool` and `capture:redo` in the actions index;
   - the test-ids hash boundary and the MEU-105 block;
   - 09's two anchors and its two MEU notes.

   It then checks that none of the following appears in the target files, and that the six new test files and two new modules don't exist:
   - the names `StepAnnotation`, `AnnotationType.Step`, `StepAnnotationIn`, `stepAnn`, `step_badge_layout`, `step_text_color`, `arrow_shaft_span`, `arrowShaftSpan`, `_clip_ellipse`, `_clip_step`, `shapeOption`, `duplicateMark`, `nextStepNumber`, `LetterTool`, `CAPTURE_EDIT_IDS`, `step_color`, `step_size`, `capture:duplicate`, `capture:tool_step`, `capture-tool-step` and `Ctrl+D`;
   - the texts `Seven annotation tools`, `Step numbers stop at 999`, `AC-106.` and `AC-107.`.
4. **Records.** Creates `C:\Temp\av-kit\s72\tmp`, and records:
   - `baseline.sha`;
   - `baseline-dirty.txt`, with each dirty path's porcelain line and SHA-256;
   - `s72-anchors.txt`, with every target's endings and SHA-256;
   - the SHA-256 of the base adapter's `"end"` arrow and `"rect"` bakes on AC-106.8's and AC-106.11's inputs.

   It hashes `docs/proposals/2026-11-10-download-logic-divergence-report.md` and never opens it.
5. **Installs.** Installs from the lock with `uv sync --frozen --offline --all-packages` and proves that both `node_modules` trees match their locks (S4).
6. **FFmpeg pair.** Checks the pinned FFmpeg pair, as the identity script binds it.
7. **Base runs.** Captures these, recorded and not fatal:
   - the base Python, UI and MCP suites;
   - the UI build;
   - the capture Electron spec `capture-inbox.test.ts`;
   - `ruff check packages/ tests/`.
8. **Selftests.** Runs the `red-check.py`, `identity.py`, `id-length.py`, `assert-never-probe.py` and `openapi-delta.py` selftests, each on its own fixtures (Session 56 RULE-4).

### 2. Type-only first, then data, then Red, then Green

**Row 1 (Session 53 RULE-2)** adds the names with no behaviour:
- `head` and `shape` on the domain classes with their defaults and no check;
- `AnnotationType.Step`, with the enum pins moved;
- `StepAnnotation` outside the `Annotation` union, with no check, and `_annotation_to_wire`'s step branch (Session 68's staging);
- `_clip_ellipse` delegating to `_clip_rect`, and `_clip_step` returning `(None, "dropped")`, neither called yet;
- `arrow_shaft_span` returning today's `(from, arrow_shaft_end)`, `step_badge_layout` and `step_text_color` returning fixed values, and `_apply_step` a no-op;
- `capture-shapes.ts` and `capture-step.ts` with stubs: `shapeOption` returns `null`, `duplicateMark` returns the mark, `nextStepNumber` returns 1, `stepBadgeLayout` returns zeros, `stepTextColor` returns `#FFFFFF`;
- `arrowShaftSpan` returning today's span;
- `CaptureTool`'s `'step'` with `TOOL_BUTTON_IDS.step`, the `TOOLBAR_BUTTONS['capture-tool-step']` entry after Text (`ListOrdered`, `Step`, the hint `Places the next number`), `LetterTool` and the narrowed `TOOL_LETTERS`, `OptionGroup`'s `'size'` (no rule returns it yet), `StyleTool`'s `'step'` with its defaults and leaves, `ToolStyle.stepSize` and `NUMBER_RANGE.stepSize`, and the switch cases returning `null` or `false` (`strokeApplies`, `styleToolFor`, `createDrawnMark`);
- the Step button in the Annotation tool group after Text, built as the Text button is (`reason={cropReason ?? (hasSelection ? undefined : NO_SHOT_HINT)}`, `onClick={() => onTool('step')}`) with no `shortcut`;
- the tool-list and style-table pins of §Pins that move marked row 1;
- `CAPTURE_EDIT_IDS` and `CAPTURE_EVENTS.duplicate`, with no registry entry;
- the new test ids.

The Step button renders from row 1, because the type checker and three existing tests require it once `TOOL_BUTTON_IDS` has `step`:
- `TOOL_BUTTON_IDS`' values are typed `keyof typeof TOOLBAR_BUTTONS`, so `step` needs its `TOOLBAR_BUTTONS` entry;
- AC-80.8 (`icon-hints.test.ts:338`) renders the page and expects every `TOOLBAR_BUTTONS` entry wrapped and hinted;
- AC-131.21 (`capture-crop-tool.behavior.test.ts:876`) expects every `TOOL_BUTTON_IDS` value present and disabled during the crop;
- AC-103.14 reads the rendered tool order.

Armed at row 1, Step places nothing: `createDrawnMark` returns `null` for it and STEP_PLACE is row 4's, and its options row shows only the colour, which `optionGroups`' fallthrough gives while `strokeApplies('step')` is `false`. Row 1 runs `npm --prefix ui run typecheck`, `npm --prefix ui run lint` and the UI files whose pins move at row 1 (`capture-tool-lock.test.ts`, `capture-redact.behavior.test.ts`, `capture-toolbar.test.ts`, `icon-hints.test.ts`, `capture-tool-style.test.ts`) with `capture-crop-tool.behavior.test.ts`, and each passes.

**Row 2 (data)** writes:
- STEP_STYLE's two settings rows, the API leaves, the MCP leaves and `captureStylePutSchema`'s leaves;
- the API mark schemas (`head`, `shape`, `StepAnnotationIn`) and `_annotations_from_in`'s pass-through and step branch with `assert_never`;
- the regenerated OpenAPI snapshot;
- the MCP mark schemas and the UI zod schemas;
- the wire's step decode, `StepAnnotation` in the union, and the clamp's step branch;
- `clip_mark`'s `case StepAnnotation(): return _clip_step(mark, left, top, width, height)`, which the type checker requires once `StepAnnotation` joins the union; `_clip_step` is still row 1's stub returning `(None, "dropped")`;
- `Field(exclude_if=…)` on the API's `head` and `shape` (DEFAULT_OMIT; the responses reuse the `*In` models);
- the UI's zod step schema joined to the `annotateInSchema` union (row 1 exports it outside the union), the optional `head` and `shape`, and stub cases returning `null` or `false` wherever the type checker then requires a step case;
- the geometry fixture's `arrow_both` and `steps` keys;
- the mark-type maps in `capture-tool-style.test.ts` (`MARKS`, `OF_MARK`), which the type check requires once `Annotation` has `step`, with `styleToolOfMark`'s step case returning `null`.

These are the data the Red tests read, so every key and schema a Red test names exists before row 3 (Session 69 RULE-4). The moved key-set pins (AC-36.12, AC-38.6, AC-105.2, AC-143.2), AC-130.6's sample and the clamp kinds move with the data. Row 2 is not a Green row, so S2 doesn't apply to it. `ruff check` runs on the new pytest files (Session 68 RULE-4).

The tests row 2 writes pass there, because row 2 writes what they check:
- pytest: AC-106.1 (Python), AC-106.5's 422 and OpenAPI blocks, AC-106.34 (the route's `assert_never` and the step branch are row 2's); AC-107.1 (Python), .3, .4 (the clamp's step branch is row 2's), .6 and .15;
- Vitest and the MCP suite: AC-106.1 (TS), .6, .7; AC-107.1 (TS), .7, .8, .17 (row 1 adds the step leaves, their defaults and the `NUMBER_RANGE` row that `readToolStyles` reads) and .26.

**Row 3 (Red)** edits the moved pins and the chord table, and requires only new-behaviour tests (Session 66 RULE-2):
- pytest: AC-106.2, .3, .4, .5's round-trip block, .8, .11, .15, .17, .29; AC-107.2, .5, .9, .10, .12's Python half, .20, .22, .23. For example, AC-106.15's straddling case fails at Red because `_clip_ellipse` delegates to `_clip_rect`, and AC-107.10 fails because `_apply_step` draws nothing.
- Vitest (UI): AC-106.9, .10, .12, .13, .18 to .27; AC-107.11, .12, .14, .16, .18, .19, .21, .25. Four moved pins are Red by assertion too: the chord-table row makes AC-97.1 Red until row 4 and AC-97.5 until row 5; the step rule in `expectedGroups` makes AC-65.1's table test (`optionGroups implements OPTIONS_BY_TOOL…`) Red until row 4; and STYLE_MODEL's step rows make AC-105.6 (`styleToolFor and styleToolOfMark give the STYLE_MODEL table…`) Red until row 4.
- Playwright: AC-106.28 and AC-107.24.

These are not in the Red list:
- Row 2's tests, listed above.
- AC-106.14, AC-106.16, AC-106.30, AC-106.31, AC-107.27, AC-107.28 and AC-107.29 are guards. Row 3 writes them and they pass throughout: `_clip_arrow`'s `replace` already carries `head` once row 2's data has the field (HEAD_CLIP doesn't change), the box's eight handles already serve a rect, and the Settings card's body is already today's seven keys. A guard that fails at row 3 is a finding about the base, not a Red test, and stops the row (S5).
- AC-106.32, AC-106.33 and AC-107.30 are row 5's checks.
- AC-107.13 passes when row 3 writes it, because row 1 renders the Step button (above). Row 3 runs it on its own and requires `Tests\s+[1-9][0-9]* passed`, as for a guard. Its receipt is `s72-ui-107-13.txt`.
- The guards run on their own at row 3, each with its own receipt: AC-106.16 and the pytest halves of AC-106.30 and AC-107.28, each with its own `-k` (`s72-r3-guard-py-<id>.txt`), and AC-106.14, .31, AC-107.27 and .29 with `-t` (`s72-r3-guard-<id>.txt`). Each must show a passed count of at least 1 and exit 0.

**Red-check (Session 50).** A Red row passes only when `red-check.py` reads each receipt and names each failing required test as an assertion failure. A required test that fails on a missing name is refused (the `vitest-required-ac-106-18-stub-name` fixture). Every Red test:
- asserts that a name exists before it patches or calls it (Session 52 RULE-4);
- catches an exception and asserts its type (Session 62 RULE-3);
- asserts length or membership before indexing (Session 62 RULE-3);
- finds a mark by its content, never by DOM index (Session 70 RULE-1);
- states every press on the image in image pixels, inside the image after VIEW_MAP's rounding (Session 68 RULE-3);
- reads its set-up against the page's automatic state: the newest shot is selected at mount, Undo clears the selection, and the lock comes from the GET (Session 71b RULE-2);
- in Electron, asserts `await expect(locator).toBeVisible()` before it clicks.

`id-length.py` checks every new pytest id against red-check's header width of 71 characters (Session 67 RULE-4).

**Rows 4 and 5 (Green)** change no test file. Row 4 writes the behaviour and SHAPES_HELP. Row 5 writes SHAPES_ACTIONS_INDEX and SHAPES_SPEC.

**Where the tests go.**
- `tests/unit/test_capture_shapes.py` (rows 2 and 3): AC-106.1 (Python), .2 to .4, .8, .11, .15, .16, .34's probe call, and the Python half of the guard AC-106.30 (row 3: the `"end"` arrow and `"rect"` bakes equal row 0's `s72-base-bakes.txt` hashes, written as literals with the same inputs, and `_clip_rect` keeps its result for `shape: "rect"`). The rest of AC-106.30 is the guard suites passing.
- `tests/unit/test_capture_step.py` (rows 2 and 3): AC-107.1 (Python), .2 to .5, .9, .10, .12's Python half, .15's service half, .23, and the Python half of the guard AC-107.28 (row 3: one mark of every other type keeps its wire keys, clamp and clip result once a step sits beside it in the list). The rest of AC-107.28 is the guard suites passing.
- `tests/e2e/test_api_capture_shapes.py` (rows 2 and 3): AC-106.5, .17 and .29.
- `tests/e2e/test_api_capture_step.py` (rows 2 and 3): AC-107.6, .15's API half, .20 and .22.
- `mcp-server/tests/capture.test.ts`, appended (row 2): AC-106.6, AC-107.7 and AC-107.26.
- `ui/tests/unit/capture-shapes.test.ts` (rows 2 and 3): the pure halves listed in §Files Modified.
- `ui/tests/unit/capture-shapes.behavior.test.ts` (row 3): the page halves. It runs on MEU-143's flow harness pattern (`capture-tool-flow.behavior.test.ts`), with a recording fake server for the GET, the PUT and the save POST, and with the registry handler mounted through `createShortcutHandler` with the real `listCommands()`, so Ctrl+D travels the real path. The page listener for `CAPTURE_EVENTS.duplicate` is the real one.
- `capture-help-content.test.ts` (row 3): AC-106.27 and AC-107.25 beside the moved resize pin.
- `ui/tests/e2e/capture-inbox.test.ts`, appended (row 3): AC-106.28 and AC-107.24.

### Plan-local scripts

The folder's `baseline.ps1`, `red-check.py`, `identity.py`, `id-length.py` and `session-gate.ps1` are adapted from Session 71b's, and `assert-never-probe.py` from Session 68's, with the `s72` names and this plan's paths. `openapi-delta.py` is new.

| Script | What it does | Plan-time result |
|---|---|---|
| `id-length.py` | checks pytest id widths | selftest (`C:/Temp/av-kit/s72-plan-idlen-selftest.txt`) |
| `red-check.py` | reads the Red receipts | selftest (`C:/Temp/av-kit/s72-plan-rc-selftest.txt`), including:<br>• the AC-106.1 and AC-107.1 boundaries against the Red ACs;<br>• the stub-name refusal, under which a declared new name that isn't a function is refused too;<br>• the Electron launch-failure refusal |
| `identity.py` | binds the tested state | selftest (`C:/Temp/av-kit/s72-plan-identity-selftest.txt`) |
| `assert-never-probe.py` | copies `domain/capture.py` and `routes/captures.py` to `C:/Temp/av-kit/s72/never-probe`, removes the step case from each, runs pyright on each copy, and passes only when pyright fails each at its `assert_never` line; its last line is `assert-never-probe: pass` | selftest (`C:/Temp/av-kit/s72-plan-never-selftest.txt`): at `5db3623` there is no step case, so it checks its own removal logic on the redact case |
| `openapi-delta.py` | AC-106.5's OpenAPI block: walks `git show 5db3623:openapi.committed.json` against the working snapshot. It requires the added properties (`ArrowAnnotationIn.head`, `RectAnnotationIn.shape`, `SettingsPutIn.step_color`, `SettingsPutIn.step_size`) and the new `StepAnnotationIn` schema, removes them, the `StepAnnotationIn` members of each `oneOf` and the `step` key of both discriminator mappings, and then requires the rest to equal the base. A pydantic split into `-Input` and `-Output` names fails it, and is a departure (S7). Its last line is `openapi-delta: pass` | selftest (`C:/Temp/av-kit/s72-plan-openapi-delta-selftest.txt`): the base against itself plus the expected additions passes; an extra property, a missing addition, a renamed schema and a changed `required` list are each refused |
| `baseline.ps1` | row 0 | parses. Its rulings, queue, shapes and anchors blocks ran alone (`C:/Temp/av-kit/s72-plan-shapes-dryrun.txt`) |
| `session-gate.ps1` | H1-2 | parses; it runs nothing at plan time |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s72-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright; `ruff check packages/ tests/`; UI typecheck and lint; the MCP typecheck; `lint_task_contract.py`; the scope-paths check (S3; the MCP audit baseline is refused); the `red-check.py` selftest; `id-length.py` on the four new pytest files; `assert-never-probe.py`; `openapi-delta.py` |
| Byte-hash guard | `npm --prefix ui run test -- tests/unit/capture-action-row.test.ts`, on its own |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s72\tmp`; only the Python ids that the base receipt shows failing are excused); `export_openapi.py --check` (equal to the snapshot row 2 regenerated); the whole UI suite and build; the MCP build and suite; `meu_status.py render --check`; `issue_triage.py render --check` |
| Runtime | the capture Electron spec `ui/tests/e2e/capture-inbox.test.ts` alone (AC-106.28, AC-107.24) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | `mcp-audit` (network and the installed servers); `build-record` (no release and no package build); `capture-filmstrip-actions.test.ts` and `capture-import.test.ts` (the Session 72 prompt forbids running them) |

The handoffs copy this session's counts from the receipts (Session 63 RULE-2). Row 0 runs the base counts again, and the handoffs copy them from the receipt.

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop. A moved pin goes into the handoff as a departure, and to Mat if it changes an AC (S12) |
| S3 | `HEAD` moves; or a path outside this plan and `baseline-dirty.txt` changes; or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat. Never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network, writes the system clipboard, or reads any user data (the capture inbox, its sidecars, the app database or Mat's settings file) | stop |
| S6 | A raw value (a refused setting or mark field, a user's path) reaches a log, stdout, a response body, the status line or the Console | fix it in the row or ask (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the execute words | stop at row 0 |
| S10 | Codex is unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file is dirty from another session | copy it to `C:/Temp/av-kit/s72/pre-status/`, byte-edit only this session's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to Mat as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs, such as a port, a file lock or a key like ShareX's F2, or Ctrl+D is taken by another program in Electron | stop and ask Mat. Never stop another program (Session 57 RULE-4) |
| S14 | `buildShortcutMap` refuses `Ctrl+D` as a page-scoped entry, or Electron's menu takes Ctrl+D before the page | stop and send Mat a Decision Brief: 09's fallback, Ctrl+D reserved and handled by the page key handler as Ctrl+C is (D-678). The do-nothing option is the fallback |
| S15 | AC-100.11 or AC-67.20 fails in a run | record both attempts in the handoff and tell Mat |
| S16 | STEP_CENTRE's tolerance fails at row 4 for a case of the bake (AC-107.10) or the Electron box check (AC-107.24) | stop and send Mat a Decision Brief with the measured offsets. The do-nothing option is "record it as a departure and keep the approved tolerance" |

## Decision Log

> [!WARNING]
> D-767 to D-778 are autonomous, and each lists its alternatives in `reasoning`. D-779 to D-782 record Mat's gate rulings of 2026-11-14. D-767 to D-799 were free at plan time (`C:/Temp/av-kit/s72-did-probe.txt`).
>
> Carried, and not relisted in the block:
> - D-158: human, `USER_EXPLICIT 2026-10-29 "all recommendations are accepted"`, grouping §8 `:142`;
> - D-159: autonomous, Local Canon, `:143`;
> - D-160: autonomous, Local Canon, `:144` (the plan-time probe returns it);
> - D-674 and D-675: autonomous, stage `grouping`, §9.8 `:201`, `:202`;
> - D-676: human, `USER_EXPLICIT 2026-11-12 "both recommendations accpeted"`, §9.8 `:203`;
> - D-678: autonomous, stage `grouping`, §9.8 `:205`.
>
> The reflection carries these and every id the decision probe returns (Session 54 RULE-5). The probe reads only the grouping's §8, so D-674, D-675, D-676 and D-678 are carried by hand.

```yaml
decision_log:
  - id: D-767
    stage: planning
    question: "How does an arrow carry its head choice, and how is a head at both ends drawn?"
    resolution: autonomous
    class: two-way
    chosen: "ArrowAnnotation.head: Literal['end','none','both'] = 'end' as the last field, refused outside the Literal at every boundary; the shaft span comes from one helper, arrow_shaft_span, mirrored in TS, and the start head is arrowhead_vertices with the ends swapped"
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:996 - arrow.head?: end|none|both, default end; a Line is an arrow with head none (C-13)"
      - "packages/infrastructure/src/avkit_infra/capture/adapter.py:103-124 - arrowhead_vertices and arrow_shaft_end"
      - "ui/tests/e2e/fixtures/capture-geometry.json - the shared arrow geometry the preview and the bake both read"
    research:
      engine: none
      sources: []
    reasoning: "09 names the field and its values. A separate line mark type lost: 09 rules a Line is an arrow, and a new type would need its own clip, wire, API and MCP schema. Two booleans (start_head, end_head) lost: 09 names one enum. Computing the both-ends shaft separately in the preview and the bake lost: the shared fixture is how the two stay equal. Two-way."
    human_message_reference: null
  - id: D-768
    stage: planning
    question: "Are head and shape written when they hold their defaults?"
    resolution: autonomous
    class: two-way
    chosen: "No: the wire, the sidecar, the API response (exclude_if) and createDrawnMark leave them out at end and rect; every input path accepts the explicit default"
    source_tag: Local Canon
    precedents:
      - "packages/core/src/avkit_core/services/capture.py:440-515 - _annotation_to_wire leaves text bg_color out when it is None"
      - "C:/Temp/av-kit/s72-probe-exclude-if.txt - pydantic 2.14.1 Field(exclude_if) drops the field at its default"
    research:
      engine: none
      sources: []
    reasoning: "Leaving the defaults out keeps every existing sidecar, response and test fixture byte for byte, so no reader of today's marks changes. Always writing them lost: every existing sidecar would change on its next save, and every test that compares a mark's keys would move. Two-way."
    human_message_reference: null
  - id: D-769
    stage: planning
    question: "How does a rect carry its shape, and which marks get it?"
    resolution: autonomous
    class: two-way
    chosen: "RectAnnotation.shape: Literal['rect','ellipse'] = 'rect' as the last field; only rect; the ellipse bakes with draw.ellipse, previews as an SVG ellipse element, hits on its outline, and keeps the box's handles"
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:997 - rect.shape?: rect|ellipse, default rect, with the MEU-100 handles (A-14)"
      - "ui/src/renderer/src/features/capture/capture-transform.ts:24 - isBoxMark covers rect, so the handles come for free"
    research:
      engine: none
      sources: []
    reasoning: "09 names the field on rect only. Giving Highlight or Redact a shape lost: 09 doesn't name them, and an elliptical redaction would change what is hidden. A box hit for the ellipse lost: a press at the box corner would select a mark that isn't drawn there. Two-way."
    human_message_reference: null
  - id: D-770
    stage: planning
    question: "How is MARK_CLIP_ELLIPSE implemented?"
    resolution: autonomous
    class: two-way
    chosen: "A _clip_ellipse case: kept and moved when the box lies inside the closed crop [0,width]x[0,height], dropped otherwise, never clipped; _clip_rect stays for shape rect"
    source_tag: Human-approved
    precedents:
      - "grouping §9.8 :203 - D-676 A, USER_EXPLICIT 2026-11-12 'both recommendations accpeted'"
      - "docs/build-plan/09-screenshot-capture.md:999 - inheriting _clip_rect was rejected"
    research:
      engine: none
      sources: []
    reasoning: "Mat chose the rule; this entry only places it. Inheriting _clip_rect was rejected by D-676. A half-open test lost: D-676 says closed, so an ellipse touching the far edge is kept. Two-way."
    human_message_reference: null
  - id: D-771
    stage: planning
    question: "How does a user pick a head or a shape?"
    resolution: autonomous
    class: two-way
    chosen: "A Head segmented control (End, None, Both) for the arrow tool or a selected arrow, and a Shape control (Rectangle, Ellipse) for the box tool or a selected rect, in the options row; the pick is page state and not saved; with a mark selected, a pick changes it as one undo step"
    source_tag: Local Canon
    precedents:
      - "Session 68 D-680 - the Redact mode is a segmented control, page state, and a pick with a redaction selected swaps it"
      - "Session 71 D-719 STYLE_TARGET - a control changes the selected mark, or the tool when nothing is selected"
    research:
      engine: none
      sources: []
    reasoning: "The Redact mode is the shipped pattern for one tool with two kinds, so the Head and Shape controls follow it. Saving the pick lost: D-680 kept the mode unsaved, and a saved None would surprise a user who expects an arrow. A shape picker on every box tool lost: 09 names rect only. Two-way."
    human_message_reference: null
  - id: D-772
    stage: planning
    question: "What is the step mark's shape at each layer?"
    resolution: autonomous
    class: two-way
    chosen: "StepAnnotation{x, y, number, color, size} with x and y int >= 0, number 1..999, size 12..200, strict at every layer; the wire refuses an extra key as redact does; the clamp follows text; the API's _annotations_from_in gains its branch and ends with assert_never"
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1009 - step {x, y, number, color, size} through every layer (C-8)"
      - "Session 68 (capture-redact) - one new mark type staged as a type-only stub, then the union, then behaviour"
      - "packages/api/src/avkit_api/routes/captures.py:158-229 - the API rebuilds each mark by hand"
    research:
      engine: none
      sources: []
    reasoning: "09 names the fields. The ranges keep a badge readable (12) and inside a screenshot's scale (200), and three digits fit the badge (999). Floats lost: every other mark's coordinates are ints. Defaults for colour and size at the API lost: the redact precedent makes every field required there, and the UI fills them from the step style. Without assert_never the API would drop an unknown type silently, as it would today. Two-way."
    human_message_reference: null
  - id: D-773
    stage: planning
    question: "How is the badge drawn so that the preview and the bake centre the number alike?"
    resolution: autonomous
    class: two-way
    chosen: "One layout formula in both: radius size/2, font px (size+1)//2 for one or two digits and (size*4+5)//10 for three, baseline y + (font_px*355+500)//1000, anchor ms; the text colour by WCAG luminance at 0.179; tolerance max(2, size/40) across and max(1, size/40) down"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s72-probe-step-centre.txt and s72-probe-step-centre-acset.txt - worst 4.0 px across at size 200 over a wide set, 3.5 px over the AC set"
      - "ui/tests/e2e/fixtures/capture-geometry.json segoe_ascent - the text mark's shared font metric"
    research:
      engine: none
      sources: []
    reasoning: "The 0.355 factor is Segoe UI's half cap height, so the digits' middle sits on y. Measuring the ink at run time lost: the preview can't measure Pillow's ink, and the two would disagree. A fixed text colour lost: white on the default amber fails contrast. Two-way."
    human_message_reference: null
  - id: D-774
    stage: planning
    question: "How is a step placed and numbered, and how is it hit?"
    resolution: autonomous
    class: two-way
    chosen: "A press with Step armed places one step at the rounded, clamped point, numbered one more than the largest step number (or 1), as one undo step with the lock-aware selection; nothing once a step 999 exists; the hit is the badge's disc plus the padding; no resize handle"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:1009 - a numbered step mark"
      - "MEU-143 LOCK_SELECTS and ARMED_EDIT - a placed mark stays selected under Lock, and a press on it moves it"
    research:
      engine: none
      sources: []
    reasoning: "Max plus one never repeats a number after a delete. Counting the steps lost: a delete would repeat a number. Renumbering after a delete lost: 09 doesn't name it, and it would change marks the user didn't touch. A drag to size the badge lost: the size is the tool's style. Two-way."
    human_message_reference: null
  - id: D-775
    stage: planning
    question: "Where does the step tool keep its style?"
    resolution: autonomous
    class: two-way
    chosen: "Two new capture leaves, step_color (#E0AF68) and step_size (32, 12..200, integer), after tool_lock, through the service, the API (StrictInt), OpenAPI, MCP and STYLE_STORE's queue; the known big-integer parser limit is pinned, not changed"
    source_tag: Local Canon
    precedents:
      - "Session 71 D-714 to D-717 - each style tool's style is a capture leaf through every layer"
      - "Session 72 prompt - a step style saved per tool as new capture leaves"
      - "C:/Temp/av-kit/s72-probe-bigint.txt - 401 digits give 422, 4301 digits give 400"
    research:
      engine: none
      sources: []
    reasoning: "The step tool keeps its style as the other style tools do. Reusing the text tool's colour lost: a step is a different tool and STYLE_DISPLAY shows each tool's own. Placing the leaves among the nine style leaves lost: it would move AC-105.2's and AC-143.2's order pins more and reorder the stored keys. Flagged at the gate. Two-way."
    human_message_reference: null
  - id: D-776
    stage: planning
    question: "Which toolbar controls do the three new marks get?"
    resolution: autonomous
    class: two-way
    chosen: "The Head and Shape controls (D-771) plus one Step tool button after Text, with no letter; TOOL_LETTERS narrows to LetterTool so it stays eight letters"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md Letters row - eight letters"
      - "Session 72 prompt - the fewest new controls and no new letter"
    research:
      engine: none
      sources: []
    reasoning: "Line and Ellipse are kinds of the Arrow and Box tools, so they need no button. Step is a new mark, so it needs a way in. Separate Line and Ellipse buttons lost: three more buttons for two kinds the controls already give. A Step letter lost: 09's Letters row names eight. Asked at the gate (D-781). Two-way."
    human_message_reference: null
  - id: D-777
    stage: planning
    question: "How does Ctrl+D reach the page, and what does it copy?"
    resolution: autonomous
    class: two-way
    chosen: "A page-scoped, stateful registry entry capture:duplicate (Ctrl+D) that dispatches CAPTURE_EVENTS.duplicate; the page copies the selected mark up to 10 px down and right, by as much as keeps its whole extent on the image (never left, up or resized), as one undo step, selects the copy, and gives a duplicated step the next free number, copying no step once a step 999 exists; nothing from a field or a modal"
    source_tag: Spec
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:998 - a page-scoped registry entry, or reserved and page-handled if the registry refuses a Ctrl chord (B-7)"
      - "ui/src/renderer/src/registry/commandRegistry.ts:446 - capture:save is a page-scoped Ctrl chord"
      - "ui/src/renderer/src/features/capture/CaptureCropBar.tsx - FIELD_STEP_SHIFT 10"
    research:
      engine: none
      sources: []
    reasoning: "09 names the registry first, and capture:save shows the registry takes page-scoped Ctrl chords, so the fallback isn't needed (S14 covers it if a run proves otherwise). Copying a step with the same number lost: two badges with one number would mislead a how-to. Copying at the same point lost: 09 says with an offset. Flagged at the gate. Two-way."
    human_message_reference: null
  - id: D-778
    stage: planning
    question: "What are the new marks' labels?"
    resolution: autonomous
    class: two-way
    chosen: "Line n, Ellipse n, and Step N with the step's own number"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/capture-hit-test.ts:314 - markLabel names each kind and counts it"
    research:
      engine: none
      sources: []
    reasoning: "A user sees a line and an ellipse as their own kinds, so the labels name them. Arrow n for a line lost: it names a head that isn't drawn. Step n by count lost: the badge shows its number, so the label should match it. Two-way."
    human_message_reference: null
  - id: D-779
    stage: planning
    question: "Which band do MEU-106, MEU-107 and the grouping row 48 take?"
    resolution: human
    class: two-way
    chosen: "P2 in both: the grouping's §3 heading and tracker row 48 change to P2 at row 6; meu-status.yaml keeps P2"
    recommendation: "P2 in both: meu-status.yaml drives the queue and the build plan, so the grouping row follows it"
    source_tag: Human-approved
    precedents:
      - "Session 71b D-756 - P2 in both for MEU-143 and row 47b"
      - ".agent/context/meu-status.yaml:2771 and :2797 - band P2"
    research:
      engine: none
      sources: []
    reasoning: "Mat accepted every recommendation through the HDP at the plan gate. The do-nothing option, leaving both as they are, and P3 in both were not chosen. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'all recommendations accepted, execute'"
  - id: D-780
    stage: planning
    question: "Do MEU-106 and MEU-107 run in one session, or does MEU-107 split off as 48b?"
    resolution: human
    class: two-way
    chosen: "One session"
    recommendation: "One session: both MEUs touch the same layers and records, and the plan review approved them together"
    source_tag: Human-approved
    precedents:
      - "grouping §3 - 'yes, candidate; MEU-107 can run as 48b'"
      - "Session 68 - a single-MEU plan at about this plan's cost"
    research:
      engine: none
      sources: []
    reasoning: "Mat accepted every recommendation through the HDP at the plan gate. The split was not chosen; the do-nothing option is the same as the recommendation. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'all recommendations accepted, execute'"
  - id: D-781
    stage: planning
    question: "How does a user pick Line, Ellipse and Step in the toolbar?"
    resolution: human
    class: two-way
    chosen: "D-776 as planned: the Arrow head control (End, None, Both), the Box shape control (Rectangle, Ellipse) and one Step tool button after Text with no letter"
    recommendation: "The fewest new controls and no letter (D-776)"
    source_tag: Human-approved
    precedents:
      - "Session 68 D-680 - the Redact mode is a segmented control in the options row"
      - "docs/build-plan/09-screenshot-capture.md Letters row - eight letters"
    research:
      engine: none
      sources: []
    reasoning: "Mat accepted every recommendation through the HDP at the plan gate. Separate Line, Ellipse and Step buttons, and the do-nothing option (no Step button, the gap recorded), were not chosen. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'all recommendations accepted, execute'"
  - id: D-782
    stage: planning
    question: "Does execution start?"
    resolution: human
    class: two-way
    chosen: "Execute now, with the repository's round cap of 6 and no token budget; the gate flags D-768, D-775 and D-777 stand as planned"
    recommendation: "Execute now, with the repository's round cap of 6 and no token budget"
    source_tag: Human-approved
    precedents:
      - "GUARDRAILS.md SIGN 3 - direct human execution authorization satisfies the plan-to-execution gate"
      - ".agent/review-limits.json - token_budgets off, execution rounds 6"
    research:
      engine: none
      sources: []
    reasoning: "Mat said to execute at the plan gate after the round 2 approval, having seen the gate flags D-768, D-775 and D-777 and the execution estimate of about 21M. The do-nothing option, holding, was not chosen. Two-way."
    human_message_reference: "USER_EXPLICIT 2026-11-14 'all recommendations accepted, execute'"
  - id: D-783
    stage: execution
    question: "How do the AC-106.29 and AC-107.20 traces run from the MCP schema to the bake?"
    resolution: autonomous
    class: two-way
    chosen: "Each trace is two tests that share one literal body: the Python half posts it through the API, a recording _annotations_from_in, the sidecar and the bake; the MCP half parses it through captureSchema and handleTool and pins the POST body"
    source_tag: Local Canon
    precedents:
      - "Session 55 RULE-3 - trace from MCP to the sidecar and the bake"
      - "implementation-plan.md AC-106.29 and AC-107.20 - one trace per MEU"
    research:
      engine: none
      sources: []
    reasoning: "One process cannot run the MCP tool and the FastAPI app with the bake. The shared literal joins the halves, so every layer is still crossed. Keeping it as one test lost: no harness holds both runtimes. No AC text changed. Two-way."
    human_message_reference: null
  - id: D-784
    stage: execution
    question: "How does a chip label count Line, Ellipse and Step marks?"
    resolution: autonomous
    class: two-way
    chosen: "markLabel gains an optional third argument, the mark list, for the per-kind count; a step's label is its own number; two-argument callers are unchanged"
    source_tag: Spec
    precedents:
      - "implementation-plan.md MARK_LABELS - Line 1, Ellipse 1 and Step N"
      - "S55 RULE-1 - every caller of an extended name runs its tests"
    research:
      engine: none
      sources: []
    reasoning: "markLabel(mark, index) cannot count marks of one kind. An optional argument keeps every existing caller. Keeping the signature lost: MARK_LABELS could not hold. Two-way."
    human_message_reference: null
  - id: D-785
    stage: execution
    question: "What about AC-99.6's adjacency pin that SHAPES_HELP's Ctrl+D sentence breaks?"
    resolution: autonomous
    class: two-way
    chosen: "AC-99.6's help test (capture-help-content.test.ts) now pins HELP_EDIT_SENTENCE, DUPLICATE_HELP_SENTENCE and HISTORY_HELP_SENTENCE in that order; logged as a plan gap, since the pins-that-move list did not name it"
    source_tag: Spec
    precedents:
      - "implementation-plan.md SHAPES_HELP - the Ctrl+D sentence follows the nudge sentence"
      - "Session 71b D-764 - a pin the plan did not list moves with the approved text"
    research:
      engine: none
      sources: []
    reasoning: "The approved SHAPES_HELP text puts the new sentence between the two AC-99.6 pinned as adjacent. Both stay present and in order. Keeping the pin lost: SHAPES_HELP could not hold. Reported to Mat. Two-way."
    human_message_reference: null
  - id: D-786
    stage: execution
    question: "Where do the rendered halves of AC-106.9 and AC-107.11 run?"
    resolution: autonomous
    class: two-way
    chosen: "capture-shapes.test.ts (node environment) holds the pure halves; capture-shapes.behavior.test.ts (jsdom) holds the rendered halves under the same AC ids"
    source_tag: Local Canon
    precedents:
      - "ui/vitest.config.ts - environment node; a behaviour file opts into jsdom with its first-line pragma"
    research:
      engine: none
      sources: []
    reasoning: "The node environment has no DOM, so the rendered viewport checks need the jsdom file. Same assertions, same ids. Two-way."
    human_message_reference: null
  - id: D-787
    stage: execution
    question: "Where does StepAnnotation sit in the Annotation union?"
    resolution: autonomous
    class: two-way
    chosen: "After TextAnnotation, so the union still ends with Pixelate, Eraser and Redact as AC-103.3 pins; no test changed"
    source_tag: Local Canon
    precedents:
      - "tests/unit/test_capture_redact.py:125 - AC-103.3 pins the union's last three members"
      - "implementation-plan.md STEP_TYPE - StepAnnotation joins the union, position not named"
    research:
      engine: none
      sources: []
    reasoning: "Appending it last failed AC-103.3 in row 4's first run. The other get_args readers test membership only. Row 1's sweep missed the tail pin. Two-way."
    human_message_reference: null
  - id: D-788
    stage: execution
    question: "What about AC-143.4's OpenAPI pin that row 2's planned additions break?"
    resolution: autonomous
    class: two-way
    chosen: "test_ac_143_4_openapi_adds_only_tool_lock compares MEU-143's baseline snapshot with the snapshot at this plan's baseline.sha (the commit that landed MEU-143), not the work tree; this session's additions are pinned by openapi-delta.py; the gate's allowed set gained the file before H1-2"
    source_tag: Local Canon
    precedents:
      - "Session 71b D-766 - a file the plan did not list joins the gate's allowed set"
      - "implementation-plan.md H1-4 - openapi-delta.py pins this session's additions"
    research:
      engine: none
      sources: []
    reasoning: "AC-143.4 asks that MEU-143 added only tool_lock; reading the work tree made it fail on this session's planned additions. Reading the commit that landed MEU-143 keeps its meaning. Neither the pins-that-move list nor the gate named the file. Reported to Mat. Two-way."
    human_message_reference: null
```

## Research References

- No web research: every rule comes from 09, the grouping's §8 and §9.8, the code at `5db3623` and the plan-time probes.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s72-head.txt` | `HEAD` `5db3623`, a clean tree |
| `C:/Temp/av-kit/s72-meu-next.txt` | the queue: MEU-127, MEU-106, MEU-107 |
| `C:/Temp/av-kit/s72-prereq-status.txt` | MEU-100, MEU-105 and MEU-143 `approved`; MEU-106 and MEU-107 `pending`, P2 |
| `C:/Temp/av-kit/s72-did-probe.txt` | D-767 to D-799 are free |
| `C:/Temp/av-kit/s72-ac-probe.txt` | AC-106 and AC-107 appear nowhere |
| `C:/Temp/av-kit/s72-probe-pillow.txt` | today's arrow and rect bakes, probed before parity was claimed (Session 69 RULE-1) |
| `C:/Temp/av-kit/s72-probe-step-centre.txt`, `C:/Temp/av-kit/s72-probe-step-centre-acset.txt` | the badge's centring, over a wide set and over the AC set |
| `C:/Temp/av-kit/s72-probe-exclude-if.txt`, `C:/Temp/av-kit/s72-probe-detail-defaults.txt` | pydantic's `exclude_if` drops a default; today's detail output keeps `bg_color: None` |
| `C:/Temp/av-kit/s72-probe-bigint.txt` | the StrictInt big-integer limits |
| `C:/Temp/av-kit/s72-plan-shapes-dryrun.txt` | `baseline.ps1`'s rulings, queue, shapes and anchors blocks, run alone at `5db3623` |
| `C:/Temp/av-kit/s72-plan-rc-selftest.txt`, `C:/Temp/av-kit/s72-plan-identity-selftest.txt`, `C:/Temp/av-kit/s72-plan-idlen-selftest.txt`, `C:/Temp/av-kit/s72-plan-never-selftest.txt`, `C:/Temp/av-kit/s72-plan-openapi-delta-selftest.txt` | the five selftests |
| `C:/Temp/av-kit/s72-plan-decision-probe.txt` | the decision probe: the grouping alone; the plan with the grouping; the plan alone, which is refused (HDP-18); every source unchanged |
| `C:/Temp/av-kit/s72-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit` |

No suite or build ran at plan time.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/`, `npm --prefix ui run typecheck`, `ui-lint`, the MCP typecheck, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest, `id-length.py`, `assert-never-probe.py` and `openapi-delta.py`.
- **Targeted:** each row's own files and each extended name's callers' tests. `red-check.py` reads the Red receipts.
- **Fresh full:** the session gate runs the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds and the capture Electron spec.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
