---
project: "2026-11-13-capture-text-multiline"
date: "2026-11-13"
source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md#session-46--capture-text-multiline-meu-102--p3"
grouping_source: ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md"
meus: ["MEU-102"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: Capture multi-line text (Session 70)

> **Project:** `2026-11-13-capture-text-multiline`
> **Build plan:** `docs/build-plan/09-screenshot-capture.md` §Multi-line text (`:912-922`, anchor `multi-line-text`, MEU-102), with the build priority matrix row 9.28 (`docs/build-plan/build-priority-matrix.md:126`).
>
> **Source request.** On 2026-10-29 Mat accepted the capture annotation editor synthesis ("all recommendations are accepted", grouping D-158). The grouping's §3 lists this as Session 46 (`:83-85`) and its §6 tracker as row 46 (`:124`); §9.1 runs it as Session 70 (D-674).
> **Status:** `draft`. `plan_to_exec_gate: human`. The plan review approved at round 1 (`.agent/context/handoffs/2026-11-13-capture-text-multiline-plan-critical-review.md`). At the plan gate Mat set the execution review budget to 30M (USER_EXPLICIT 2026-11-13 '30M (Recommended)') and said to execute (USER_EXPLICIT 2026-11-13 'Execute now (Recommended)'), with the default execution cap of 6 rounds (D-712).

## Goal

**Goal anchor:** Session 70 lets a text mark hold more than one line. In the editor's text field, Enter commits and Shift+Enter adds a line, Enter belongs to the IME while it composes, and the field shows a hint. A stored `\n` starts a new line with a pitch derived from `font_size`, with no new field. `\r\n` and `\r` are stored as `\n`. The preview draws each line where the bake draws it, and bake fixtures prove that they agree. Nothing wraps.

Five things are missing today (`4e35af9`):

1. **The preview and the bake disagree on `\n` (G-3).** The bake already draws `"Hi\nHi"` on two lines: Pillow 13's multi-line path splits on `\n` with a pitch of `getbbox("A")` bottom plus 4, which equals the Segoe ascent plus 4 at every size from 1 to 500 (`C:/Temp/av-kit/s70-g3-pitch.txt`, `C:/Temp/av-kit/s70-g3-pillow.txt`). The SVG preview draws one `<text>` with `{ann.text}` (`CaptureViewport.tsx:323-330`), and Chromium collapses the newline, so `"Hi\nHi"` shows as one line (`C:/Temp/av-kit/s70-g3-svg.txt`, Electron 42.11.18).
2. **The preview's plate is one line.** `textBackgroundBox` (`capture-text-metrics.ts:40-63`) measures the whole text as one run of glyphs, so the plate, the hit test (`capture-hit-test.ts:126`, `:138`) and the text scale (`capture-transform.ts:125`, `:141`) miss every line after the first (`C:/Temp/av-kit/s70-g3-plate-ts.txt`).
3. **CR is a glyph.** The domain and the API accept `\r` (`domain/capture.py:359`, `schemas/captures.py:120`), and the bake draws it: `"Hi\r\nHi"` at size 16 gives the plate `(10, 26, 27, 60)` against `(10, 26, 25, 60)` for `"Hi\nHi"`, and a lone `\r` stays on one line (`C:/Temp/av-kit/s70-g3-pillow.txt`).
4. **The field is one line.** The text draft is an `<input>` (`CaptureViewport.tsx:1521-1547`), which can't hold a newline: Enter commits, and re-editing a mark whose text holds `\n` shows the lines run together (an `<input>` strips LF from its value).
5. **No hint.** Nothing tells the user which key commits.

The session ends when:
- every 09 §Multi-line text rule holds, each with a behaviour test;
- the session gate's last line is `session-gate: all steps exit 0`;
- MEU-102 is `approved` after Codex approves.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit (2026-11-13). No payload is oversized: the domain, schema, adapter, fixture tool, metrics, viewport, page and MCP capture files were read by section."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`plan_to_exec_gate: human`, `.agent/context/harness.local.md` Claude Code block). Execution waits for Mat's explicit words at the plan gate (§Status, D-712). Validation goes through `rtk proxy`:
  - receipts go under `C:/Temp/av-kit` with the `s70-*` names;
  - `RECEIPTS_DIR=C:/Temp/av-kit` and `PYTHONIOENCODING=utf-8`;
  - `TMP` and `TEMP` point at `C:\Temp\av-kit\s70\tmp` for the Python suite;
  - `ELECTRON_RUN_AS_NODE` is cleared before every UI and Electron run, and the scripts clear it as well.
- **Working directory:** `P:/av-kit` on `main`. No branches or worktrees. `.agent/fleet/hub` and every other worktree are left alone.
- **Cloud-local contract:** `.agent/docs/cloud-local-collaboration.md` doesn't apply, because the driver OS is the target OS. GUI references are not shipped (`gui-refs-not-shipped`).
- **Decisions:** every decision for Mat goes to Mat through the Human Decision Protocol (AGENTS.md §Communication Policy), with a recommendation first and a do-nothing option. No decision goes to a subagent in this session.
- **Reviewer:** Codex through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`.
  - Ledger loops: `s70-plan-canonical-2026-11-13-capture-text-multiline` and `s70-execution-2026-11-13-capture-text-multiline`.
  - Claude wrote the plan, so the reviewer is a different vendor.
  - Round caps: the ledger defaults, plan 3 and execution 6.
  - Token budgets: the plan loop opens above the 10.5M default, at the budget Mat sets before its first dispatch (§Token estimate). The execution loop opens at the budget Mat sets at the gate (`begin --token-budget`, D-712).
  - If Codex is unavailable or the ledger refuses a round, the fallback is Mat.
  - Each round is metered, and the coordinator tells Mat before each dispatch.
  - Each rolling report is validated under `C:/Temp/av-kit`, then copied byte for byte to its canonical path, and the `--review-state-only` receipt is rebuilt there.
- **Reviewer prompts:**
  - They name the ledger vocabulary up front: D-701 to D-712, AC-102.1 to AC-102.24, and the mechanism ids in §Single-statement contracts.
  - They forbid opening `P:/av-kit/.mcp.json`, any `mcp-token.txt`, `~/.claude.json`, any `.env`, `.claude/settings.local.json`, anything under `.agent/fleet/hub` and `docs/proposals/2026-11-10-download-logic-divergence-report.md`, and they write `<HOME>` for the home folder.
  - When a prompt asks for `tested_state`, it names `~/.config/git/ignore` and the path that file hides, `.claude/settings.local.json` (Session 51 RULE-4).
  - `## Findings` holds only the Findings table (Session 65 RULE-3).
  - Every prompt carries the literal `### New Findings` header and the Prior Pass Summary table, with the columns Finding, Prior Status and Recheck Result (Session 66 RULE-4).
  - A recheck names each prior finding by the review's own id (Session 53 RULE-3) and asks for bare words in its Recheck cells (`fixed`, `open`; Session 52 RULE-1, Session 57 RULE-5).
- **Never in these rows without Mat's words:**
  - a commit, a push, a tag, a release or an upload;
  - the live MCP audit or `--update-baseline`;
  - `npm run dist`;
  - an `approved` verdict authored by the implementer;
  - reading a user's capture inbox or the app database (B-4).
- **No network, no clipboard:**
  - no test or row reaches YouTube or the network;
  - no test or row writes the system clipboard (Session 57 RULE-4);
  - nothing touches the installed avkit MCP servers (no `mcp__avkit__*` tool is called);
  - no other program is stopped. If ShareX holds a key a row needs, the row stops and asks Mat (S13).

## Handoff Set

| MEU | Handoff | Chain |
|---|---|---|
| MEU-102 | `.agent/context/handoffs/2026-11-13-capture-text-multiline-MEU-102-handoff.md` | only |

Rolling reviews: `.agent/context/handoffs/2026-11-13-capture-text-multiline-plan-critical-review.md` and `.agent/context/handoffs/2026-11-13-capture-text-multiline-implementation-critical-review.md`.

## Work Packages and Context Lifecycle

| WP | Rows | Content | Context |
|---|---|---|---|
| WP-1 | 0 | Baseline: rulings, queue, shapes, dirty paths, anchors, base suites, selftests | shared |
| WP-2 | 1 | Type-only names: `normalize_text_newlines`, `TEXT_LINE_GAP`, `TEXT_LINE_GAP_PX`, `segoeLinePitchPx`, `textLines`, `CAPTURE_TEXT_DRAFT_HINT` | shared |
| WP-3 | 2 | The multi-line bake fixture and the geometry data | shared |
| WP-4 | 3, 4 | Red, then Green | shared |
| WP-5 | 5 | The 09 Delivered note | shared |
| WP-6 | 6 | Status and grouping | shared |
| WP-7 | H1, H2 | Gate, handoff, review, reflection, next prompt | compact_continue |

## User Review Required

**Carried rulings:**
- D-158 (USER_EXPLICIT 2026-10-29 "all recommendations are accepted", grouping §8 `:141`) accepts the synthesis that 09 §Multi-line text encodes (A-7, C-3 and §7's data-model rule).
- D-159 (autonomous, Local Canon, `:142`) splits slice 3 into MEU-101 (3a) and MEU-102 (3b), and holds 3b behind G-3. D-160 (autonomous, Local Canon, `:143`) is carried, because the decision probe returns it.
- D-674 and D-675 (autonomous, grouping §9.8) set the session number and the crop rule. MARK_CLIP_TEXT (`domain/capture.py:521-528`) keeps a text mark whose anchor is inside the crop and moves it by the crop's origin; this plan doesn't change it (AC-102.23).
- D-676 to D-678 bind other sessions, not this one.

**Band mismatch.** The grouping's §3 heading (`:83`) and tracker row 46 (`:124`) say P3; `.agent/context/meu-status.yaml:2674` says `band: P2`. This plan changes neither. Row 6 writes only the tracker's status column, and the handoff names the mismatch.

**G-3 settled at plan time.** The 09 Model row asks for a layout version only if stored marks need one. The plan-time probes found:
- the bake's line pitch is a pure function of `font_size` (ascent plus 4), so no field is needed (`C:/Temp/av-kit/s70-g3-pitch.txt`);
- the stored marks hold no newline: 29 shot rows, 5 sidecars and 11 text marks, with 0 LF, 0 CR and 0 other control characters (`C:/Temp/av-kit/s70-b4-scan.txt`).

So no stored mark changes its bake, and there is no layout version and no Decision Brief (D-702).

**Plan-time departure (B-4).** The stored-marks scan (`C:/Temp/av-kit/s70/b4_stored_marks_scan.py`) opened Mat's capture inbox sidecars and the app database read-only before Mat was told, which the Session 70 prompt forbids ("it reads no user's capture inbox without telling me first"). It printed counts only: no path, file name or mark text. It wrote nothing. The coordinator disclosed it in the session's interim message. The handoff and the reflection record it, and no execution row reads the inbox or the database.

**Rulings at plan time.** None. The plan gate asks Mat one question through the HDP (D-712): the execution review budget, with the Session 60 RULE-5 figure of 30M as the recommendation and the ledger default as the do-nothing option, and his words to execute.

**Gate flags.** At the gate Mat also sees, each with a recommendation and its do-nothing option:
- D-703: `\r\n` and `\r` are stored as `\n` at the domain and the API, so a CR never reaches a sidecar again;
- D-705: the text field becomes a `<textarea>` with the same test id;
- D-707: a one-line mark keeps today's single `<text>` child, so only a mark that holds `\n` renders differently;
- the band mismatch above;
- the B-4 departure above.

An AC or contract change during execution goes to Mat as a Decision Brief (S12). Its do-nothing option is "record it as a departure and keep the approved text".

**Plan review.** Round 1 approved with 0 findings (loop `s70-plan-canonical-2026-11-13-capture-text-multiline`, 8,576,994 tokens of 18,000,000; `.agent/context/handoffs/2026-11-13-capture-text-multiline-plan-critical-review.md`). Its three non-blocking notes are applied above: TEXT_PLATE_LINES and AC-102.10 state the union of unrounded extents, rounded and clamped once, and AC-102.10's negative case gives the real trailing-`\n` growth (Q4); TEXT_PARITY_E2E's argument carries the mark with the pair (Q7); S6 names a user's path, not a generated fixture path (Q11). No AC was added, removed or renumbered.

**Network.** Recommendation: none, because nothing here fetches. The do-nothing option is the same. There is no brief.

**Token estimate.** Calibrated against:
- Session 67: plan 10,193,204 over 2 rounds, execution 13,248,892 over 2 rounds;
- Session 68: plan 13,173,719 over 2 rounds, execution 13,213,554 in 1 round.

This session is one MEU across the domain, schema, adapter, fixture tool, metrics, viewport and MCP description, with a new Electron parity test:
- plan review: about 12M for round 1 and about 6M for one recheck, so the plan loop asks Mat for about 18M (the 10.5M default would stop before a recheck);
- execution review: about 12M for round 1, so the Session 60 RULE-5 figure is 30M (12M × 2 plus a recheck at about 6M).

**Word meanings.**
- A *line* is one item of `text.split("\n")`. An empty line has no glyphs. A trailing `\n` adds an empty last line.
- The *pitch* is the distance between two lines' tops: the Segoe ascent at the mark's size plus `TEXT_LINE_GAP` (4 px).
- *Line i's top* is `y + i × pitch`, counting from 0.
- The *plate* is the box drawn behind the text when `bg_color` is set, and the box the hit test and the scale handles use.
- *The draft* is the editor's text field (`data-testid="capture-text-draft"`), open while a text mark is typed or re-edited.
- *Exact cases* are the inputs where the preview's plate equals Pillow's to the pixel (D-709).

## Proposed Changes

### Single-statement contracts

Each mechanism id below is one statement. A row cites the id; a test names the AC.

| Id | Statement | File |
|---|---|---|
| `TEXT_NEWLINES` | `normalize_text_newlines(text: str) -> str` returns `text.replace("\r\n", "\n").replace("\r", "\n")`. `TextAnnotation.__post_init__` (`domain/capture.py:356`) applies it first when `text` is a `str`, through `object.__setattr__`, and then runs today's check, so the 1 to `TEXT_MAX_CHARS` rule counts the stored text. A non-`str` text is refused as today. LF and every other control character pass as today (D-703, D-704). `_clip_text`'s `replace` runs `__post_init__` again, which changes nothing, because the function is idempotent. | `domain/capture.py` |
| `TEXT_API_NEWLINES` | `TextAnnotationIn` (`schemas/captures.py:114`) gains `@field_validator("text", mode="before")`, which returns `normalize_text_newlines(value)` for a `str` and the value unchanged otherwise. So `max_length` counts the stored text, a non-`str` is still refused with today's 422, and the OpenAPI document is unchanged (`C:/Temp/av-kit/s70-api-validator-probe.txt`; D-703). | `schemas/captures.py` |
| `TEXT_LINE_GAP` | The adapter gains `TEXT_LINE_GAP = 4` and passes `spacing=TEXT_LINE_GAP` to `draw.textbbox` in `text_plate_box` (`adapter.py:149`) and to `draw.text` in `_apply_text` (`:885-891`). 4 is Pillow's default, so the baked bytes don't change. | `adapter.py` |
| `TEXT_LINE_PITCH` | `capture-text-metrics.ts` gains `TEXT_LINE_GAP_PX = 4`, `segoeLinePitchPx(fontSize: number): number`, which returns `segoeAscentPx(fontSize) + TEXT_LINE_GAP_PX`, and `textLines(text: string): string[]`, which returns `text.split('\n')`. | `capture-text-metrics.ts` |
| `TEXT_PLATE_LINES` | `textBackgroundBox` keeps today's body for a text with no `\n`. For a text with `\n`, it takes, for each line i with top `y_i = y + i × segoeLinePitchPx(font_size)`, the unrounded glyph extents that today's loop computes for that line at `(x, y_i)` when the line is not empty, or the point `(x, y_i)` when it is empty, unions those extents, and then rounds the union and applies today's at-least-1 width and height once. It doesn't union today's returned (rounded and clamped) one-line boxes: for two spaces, `\n`, two spaces, that would end 1 px below Pillow at sizes 8 and 16 (plan review round 1, Q4). The hit test and `scaleTextMark` call it, so they get the same plate. | `capture-text-metrics.ts` |
| `TEXT_GEOMETRY` | `capture-geometry.json` gains `segoe_line_pitch`, with the same 17 sizes as `segoe_ascent` and Pillow's pitch at each, and `text_plates`, a list of `{x, y, text, font_size, box}` holding only exact cases, each box equal to Pillow's `text_plate_box` (D-709). Its existing keys don't change. | `capture-geometry.json` |
| `TEXT_SVG_LINES` | A text mark whose text holds `\n` renders one `<tspan>` per line inside its `<text>`, each with `x={ann.x}` and `y={svgTextBaselineY(ann) + i × segoeLinePitchPx(ann.font_size)}`. An empty line renders an empty `<tspan>`. A text with no `\n` keeps today's single text child (D-707). At `y = 20`, size 16, the baselines are 38, 60 and 82. | `CaptureViewport.tsx` |
| `TEXT_DRAFT_KEYS` | The draft becomes a `<textarea>` with the same `data-testid`, `className` plus `resize-none`, `rows={Math.max(1, textLines(value).length)}`, `wrap="off"`, `spellCheck={false}` and `aria-describedby="capture-text-draft-hint"`. Its `onKeyDown` returns when `event.nativeEvent.isComposing` is set, as today. Enter without Shift calls `preventDefault` and commits. Shift+Enter is left to the browser, which inserts `\n`. Escape cancels as today (D-705). The page stores the draft's value as typed, so a commit keeps every `\n`; a draft of only whitespace and newlines commits nothing, as `draftCommits`'s `trim` already decides (D-708). | `CaptureViewport.tsx` |
| `TEXT_DRAFT_HINT` | While the draft is open, a sibling element with `id` and `data-testid` `capture-text-draft-hint`, `pointer-events: none` and the draft's position reads exactly `Enter to finish, Shift+Enter for a new line, Esc to cancel`. `test-ids.ts` appends `// MEU-102 Capture multi-line text (additive IDs).` and `CAPTURE_TEXT_DRAFT_HINT = 'capture-text-draft-hint'` after the MEU-104 block (D-706). | `CaptureViewport.tsx`, `test-ids.ts` |
| `TEXT_MCP_DOC` | The annotate description (`mcp-server/src/toolsets/capture.ts:101`) appends, after `${ANNOTATE_EXAMPLE}`, the sentence `A text mark's text may hold \n to start a new line; \r\n and \r are stored as \n, and lines never wrap.`, where each `\n` and `\r` is the two characters backslash and letter. No action, schema or audit baseline changes (D-711). | `mcp-server/src/toolsets/capture.ts` |
| `TEXT_FIXTURE_MULTILINE` | `tools/capture_bake_fixture.py` gains `MULTILINE_ORIGINAL_NAME = "capture-fidelity-multiline-original.png"`, `MULTILINE_ANNOTATED_NAME = "capture-fidelity-multiline-annotated.png"`, `MULTILINE_ORIGINAL_SIZE = (240, 160)`, `MULTILINE_FIXTURE_MARK = TextAnnotation(x=20, y=16, text="Hi\n\nHi\n", color="#000000", font_size=32, bg_color="#FFD400")`, `write_multiline_fixture(out_dir: Path) -> tuple[Path, Path]` (`write_original`, then the real `bake`) and a `--multiline` flag that writes only that pair. The default and `--region` runs are unchanged (D-710). | `tools/capture_bake_fixture.py`, the two PNGs |
| `TEXT_PARITY_E2E` | `installFidelitySeam` (`capture-inbox.test.ts:2112`) takes a fixture argument holding the original, the annotated file and the mark the detail responses serve (today `FIDELITY_MARK`, `:2107`, `:2117`, `:2144`, `:2152`), defaulting to today's pair and mark, and `fidelityBoxes` also returns `inkRows`, the runs of rows that hold ink. AC-82.6 calls it with the default. AC-102.19 calls it with the multi-line pair. | `capture-inbox.test.ts` |

MARK_CLIP_TEXT (`domain/capture.py:524`) doesn't change.

### Pins that move

None. The plan-time sweep (`C:/Temp/av-kit/s70/pin-sweep.txt`) read every caller and pin of `text_plate_box`, `_apply_text`, `textBackgroundBox`, `segoeAscentPx`, `svgTextBaselineY`, `TextAnnotation(`, `TextAnnotationIn`, the draft's tag, the geometry keys, the fixture names and the annotate description:
- `capture-page.behavior.test.ts:359`, `:431`, `:641`, `:3127` and `:3172-3209` cast the draft `as HTMLInputElement`. A cast is type-only; `.value`, `user.clear` and `user.type` work on a `<textarea>`, and `{Enter}` still commits through TEXT_DRAFT_KEYS, so these stay.
- No test reads the draft's `tagName`, `type` or `size`.
- `capture-text-metrics.test.ts:27` takes its sizes from `segoe_ascent`, which doesn't change.
- `test_capture_adapter.py:618` (`text_plate_box(10, 20, "Hi", 16)`) and `:612` (`_apply_text`'s source) hold: a one-line text and `spacing=` leave the result as it is. Row 1 runs the file to prove it.
- AC-59.16 (`mcp-server/tests/capture.test.ts:370`) checks that the annotate description holds the two examples and neither `circle` nor `marker`; the new sentence holds neither word.
- `isEditableTarget` (`capture-import.ts:137`) already treats a `<textarea>` as editable, so paste and canvas Ctrl+C keep leaving the draft alone.

Before writing, row 1 sweeps `packages/`, `tests/`, `tools/`, `ui/` and `mcp-server/` again for these names and records the hits in `s70-anchors.txt` (Session 55 RULE-1, Session 59 RULE-1, Session 62 RULE-4, Session 63 RULE-1, Session 66 RULE-1). A pin found then and missing here goes into the handoff as a departure.

### Where values go (Session 50 RULE-1, Session 53 RULE-1, Session 61 RULE-1)

| Value | Writers | Readers | Rule |
|---|---|---|---|
| A text mark's `text` | the draft's `onChange` (`onTextDraftChange`), the API body, the MCP annotate call, a sidecar load | `TextAnnotationIn`, `_annotations_from_in`, `TextAnnotation`, the sidecar, `_apply_text`, `textBackgroundBox`, the SVG | CR is folded to LF at `TextAnnotationIn` and at `TextAnnotation`, so the sidecar, the bake and the preview see LF only; the length rule counts the folded text; no log, response body or Console line echoes the text (S6) |
| The line pitch | `segoeAscentPx` plus `TEXT_LINE_GAP_PX` in the UI; Pillow's `getbbox("A")` bottom plus `TEXT_LINE_GAP` in the bake | `TEXT_PLATE_LINES`, `TEXT_SVG_LINES` | `segoe_line_pitch` in `capture-geometry.json` pins both to the same numbers (AC-102.7, AC-102.9) |

These functions sit between the user's keys and the stored mark, and AC-102.16 traces one two-line mark through them with recording fakes (Session 55 RULE-3): the draft's `onKeyDown` (Shift+Enter, then Enter), `onTextDraftChange`, `onTextCommit`, `annotationsRef.current`, `parseAnnotateBody` and the recorded save POST body. AC-102.17 traces the Python half: the API body with `\r\n`, `TextAnnotationIn`, `_annotations_from_in`, `TextAnnotation`, the sidecar's stored text and the baked pixels.

### Spec text (D3)

| File | Change |
|---|---|
| `docs/build-plan/09-screenshot-capture.md` | A `> **Delivered (Session 70).**` note goes after the §Multi-line text rule table (`:922`). It names the mechanism ids, AC-102.1 to AC-102.24, G-3's answer (the bake already split on `\n`; the preview now matches; no layout version, because no stored mark held a newline) and the plan folder. The rule rows don't change. |

The help body doesn't change: the hint shows while the field is open (D-706).

### MEU-102 `capture-text-multiline`

**Boundary inventory.**

| Boundary | Input | Refusal |
|---|---|---|
| API `POST /captures/{id}/annotate` (and render, crop and export, which share `AnnotateIn` or the domain) | `TextAnnotationIn.text` | `\r\n` and `\r` are folded to `\n` before the length check; an empty or over-long text after folding, a non-`str` text and a lone surrogate give today's 422; no response body echoes the text |
| MCP `avkit_capture` annotate | the same body | unchanged; the description states the newline rule |
| Domain `TextAnnotation` | any caller, including a sidecar load | the same folding and length rule; `AnnotationValidationError` as today |
| GUI | the draft | not a trust boundary; the server refuses what `parseAnnotateBody` let through |

The OpenAPI snapshot doesn't change (`C:/Temp/av-kit/s70-api-validator-probe.txt`). The MCP audit baseline is keyed by tool, action and status, and MCP gains no action, so the gate's scope check refuses the file.

**Input matrix (Session 64 RULE-1).** These cases come from the plan-time probes at `4e35af9` (`C:/Temp/av-kit/s70-matrix.txt` and `C:/Temp/av-kit/s70/matrix/`): the texts `Hi`, `Hi\nHi`, `Hi\n\nHi`, `Hi\n`, `\nHi`, `\n`, `Hello\nW\ngy`, `Hi\n\nHello\n`, `i\nWWWW` and two lines of two spaces, at sizes 1, 8, 12, 16, 20, 24, 32, 38, 48, 64, 72, 96 and 128, at `(10, 20)`.

| Text | Stored | Bake | Preview plate |
|---|---|---|---|
| no `\n`, no `\r` | as typed | unchanged | unchanged |
| `\n` anywhere | as typed | one line per item of `split("\n")`, top `y + i × pitch` | the union of the lines' unrounded glyph extents, with an empty line as the point `(x, y_i)`, rounded and clamped once (TEXT_PLATE_LINES); it differs from Pillow's by no more than the one-line box does at that size |
| `\r\n` or a lone `\r` | folded to `\n` | as the folded text, byte for byte | as the folded text |
| only whitespace and `\n` in the draft | nothing (the draft commits nothing) | — | — |
| 500 `\n`-separated characters after folding, sent as `\r\n` | accepted | — | — |

The exact cases (each edge equal to Pillow's) are, at `(10, 20)`:

| Text | Size | Box |
|---|---|---|
| `Hi` | 8, 16 | `[10, 23, 18, 29]`, `[10, 26, 25, 38]` |
| `Hi\nHi` | 8, 16 | `[10, 23, 18, 42]`, `[10, 26, 25, 60]` |
| `Hi\n\nHi` | 8, 16 | `[10, 23, 18, 55]`, `[10, 26, 25, 82]` |
| `Hi\n` | 8, 16, 24 | `[10, 23, 18, 33]`, `[10, 26, 25, 42]`, `[10, 29, 33, 50]` |
| `\nHi` | 8, 16 | `[10, 20, 18, 42]`, `[10, 20, 25, 60]` |
| `Hello\nW\ngy` | 16 | `[10, 26, 46, 86]` |
| `Hi\n\nHello\n` | 16 | `[10, 26, 46, 86]` |
| `i\nWWWW` | 16 | `[10, 26, 70, 60]` |
| two spaces, `\n`, two spaces | 8, 16 | `[10, 29, 14, 42]`, `[10, 38, 18, 60]` |

The multi-line fixture (`Hi\n\nHi\n`, size 32, at `(20, 16)` on 240×160) bakes the plate `(20, 28, 51, 133)` and the ink row runs `(28, 50)` and `(106, 128)` (`C:/Temp/av-kit/s70-fixture-probe.txt`). At size 32 the preview's plate for that text differs from Pillow's by at most 1 px (`blank@32` in `C:/Temp/av-kit/s70-matrix.txt`), which is AC-82.6's tolerance.

| AC | Type | Description | Source | Negative test |
|---|---|---|---|---|
| AC-102.1 | type | The exact signatures: `normalize_text_newlines(text: str) -> str`, the adapter's `TEXT_LINE_GAP == 4`, `write_multiline_fixture(out_dir: Path) -> tuple[Path, Path]`, `TEXT_LINE_GAP_PX === 4`, `segoeLinePitchPx(fontSize: number): number`, `textLines(text: string): string[]` and `CAPTURE_TEXT_DRAFT_HINT === 'capture-text-draft-hint'` (Session 66 RULE-1) | Local Canon: D-701 | passes where row 3 writes it (rows 1 and 2 add the names) |
| AC-102.2 | behaviour | TEXT_NEWLINES: a `TextAnnotation` built with `Hi\r\nHi`, `Hi\rHi` and `Hi\r\n\r\nHi` stores `Hi\nHi`, `Hi\nHi` and `Hi\n\nHi`, one parametrize id per case | Spec: 09 Model row; Local Canon: D-703 | the lone-CR case |
| AC-102.3 | guard | LF, a tab and other control characters are stored as given (D-704); a non-`str` text and empty text raise `AnnotationValidationError` | Local Canon: D-704 | the non-`str` case |
| AC-102.4 | behaviour | The length rule counts the folded text: 250 `a\r\n` pairs (750 characters sent, 500 stored) are accepted by the domain and by `TextAnnotationIn`; 251 pairs are refused by both | Local Canon: D-703 | the 251 case |
| AC-102.5 | behaviour | TEXT_API_NEWLINES: `POST /captures/{id}/annotate` with `Hi\r\nHi` gives 200, and the sidecar's stored text is `Hi\nHi`; a non-`str` text gives 422 with no echo of the value; the OpenAPI document equals the committed one | Spec: 09 Model row; Local Canon: D-703 | the non-`str` case |
| AC-102.6 | behaviour | A bake of `Hi\r\nHi` and of `Hi\rHi` gives bytes equal to the bake of `Hi\nHi`, at sizes 16 and 32, with and without `bg_color` | Spec: 09 Parity row; Local Canon: D-703 | the lone-CR case |
| AC-102.7 | guard | TEXT_GEOMETRY: each `segoe_line_pitch` entry equals Pillow's `getbbox("A")` bottom plus `TEXT_LINE_GAP` for the loaded font at that size, and each `text_plates` box equals `text_plate_box` for its case | Spec: 09 Parity row; Local Canon: D-709 | — |
| AC-102.8 | guard | TEXT_FIXTURE_MULTILINE: `write_multiline_fixture` writes a 240×160 white original and its real bake, and the bake's bytes equal the committed `capture-fidelity-multiline-annotated.png`; `--multiline` writes only that pair; the default and `--region` runs write today's files | Local Canon: D-710 | the default run writes no multi-line file |
| AC-102.9 | behaviour | TEXT_LINE_PITCH: `segoeLinePitchPx(size)` equals `segoe_line_pitch[size]` for every size in the file, and `textLines` splits `Hi\n\nHi\n` into `['Hi', '', 'Hi', '']` | Spec: 09 Model row (line spacing derives from `font_size`) | — |
| AC-102.10 | behaviour | TEXT_PLATE_LINES: `textBackgroundBox` equals each `text_plates` box; for each multi-line text in the input matrix at sizes 8, 16, 32 and 64, it equals the union of its lines' unrounded glyph extents at `y + i × pitch`, with an empty line as the point, rounded and clamped once; a text with no `\n` gives today's box | Spec: 09 Parity row | the trailing-`\n` case moves the bottom from the last glyph line to the empty line's top: `Hi` ends at 38 and `Hi\n` at 42, at size 16 |
| AC-102.11 | behaviour | TEXT_SVG_LINES: a rendered mark `Hi\n\nHi` at `(10, 20)`, size 16, has one `<text>` with three `<tspan>` children whose `x` is 10 and whose `y` is 38, 60 and 82; a mark `Hi` has no `<tspan>` and its text child is `Hi` | Spec: 09 Parity row; Local Canon: D-707 | the one-line case |
| AC-102.12 | behaviour | TEXT_DRAFT_KEYS: typing `Hi`, Shift+Enter, `Hi`, then Enter in a new draft commits one mark whose text is `Hi\nHi` | Spec: 09 Keys row | Enter alone after `Hi` commits `Hi` |
| AC-102.13 | behaviour | The draft is a `<textarea>` with `wrap="off"` and `rows` equal to its line count, at least 1 | Spec: 09 Keys row, Parity row (no wrap, C-3) | `rows` is 1 for an empty draft |
| AC-102.14 | guard | Enter during IME composition (`isComposing`) neither commits nor closes the draft; Escape closes it with no mark | Spec: 09 Keys row | the composing case |
| AC-102.15 | behaviour | TEXT_DRAFT_HINT: while the draft is open, `capture-text-draft-hint` reads exactly `Enter to finish, Shift+Enter for a new line, Esc to cancel` and the draft's `aria-describedby` names it; with no draft it is absent | Spec: 09 Keys row; Local Canon: D-706 | the no-draft case |
| AC-102.16 | behaviour | One two-line mark traced from the draft's keydowns through `onTextDraftChange`, `onTextCommit` and `annotationsRef.current` to the recorded save POST body, whose text is `Hi\nHi` | Session 55 RULE-3; Spec: 09 Keys row | the body holds the mark exactly once |
| AC-102.17 | behaviour | One mark traced from an annotate body holding `Hi\r\nHi` through `TextAnnotationIn`, `_annotations_from_in`, `TextAnnotation` (a recording wrapper) to the sidecar's text `Hi\nHi` and the annotated PNG, which equals the bake of `Hi\nHi` | Session 55 RULE-3; Spec: 09 Model row | the wrapper records the mark exactly once |
| AC-102.18 | behaviour | Re-editing a saved mark `Hi\nHi` (Select-mode double-click, MEU-101) opens the draft with the value `Hi\nHi` | Spec: 09 Keys row; MEU-101 TEXT_REEDIT | — |
| AC-102.19 | behaviour | Electron: with the multi-line fixture pair, the Original view's plate and ink box agree with the Annotated view's within 1 px at 100%, the image is 240×160, and each view has exactly 2 ink row runs whose ends agree within 1 px | Spec: 09 Parity row | a one-line preview gives 1 run |
| AC-102.20 | guard | AC-82.6 passes unchanged through the parameterised seam | Local Canon: MEU-82 TEXT_PIXEL_ORACLE | — |
| AC-102.21 | behaviour | TEXT_MCP_DOC: the annotate description holds the D-711 sentence, with backslash-n as two characters; it holds neither `circle` nor `marker`; the tool's actions are unchanged | Local Canon: D-711 | — |
| AC-102.22 | check | Spec D3: 09's Delivered (Session 70) note after the §Multi-line text table, naming AC-102.24 and the plan folder; 09 keeps CRLF endings | Local Canon: D3 | row 5's check exits 1 before row 5 |
| AC-102.23 | guard | MARK_CLIP_TEXT: a crop keeps a multi-line text mark whose anchor is inside and moves it by the crop's origin, with its text unchanged; a mark whose anchor is outside is dropped | Local Canon: D-675 | the outside case |
| AC-102.24 | behaviour | A Select-mode click on the second line of `Hi\nHi` (inside the second line's box, outside the first's) selects the mark | Spec: 09 Parity row (the plate is the multi-line plate) | a click below the last line selects nothing |

**Guards.** These pass after rows 1, 2 and 4:
- Python: `tests/unit/test_domain_capture.py`, `tests/unit/test_capture_adapter.py`, `tests/unit/test_capture_service.py`, `tests/unit/test_capture_render.py`, `tests/unit/test_capture_bake_fixture.py`, `tests/e2e/test_api_captures.py`, `tests/e2e/test_api_capture_crop.py`, `tests/e2e/test_api_capture_render.py` and `tests/e2e/test_api_openapi.py`;
- MCP: `mcp-server/tests/capture.test.ts`;
- UI: `capture-text-metrics.test.ts`, `capture-hit-test.test.ts`, `capture-transform.test.ts`, `capture-page.behavior.test.ts`, `capture-action-row.test.ts` and `capture-copy-image.behavior.test.ts`.

**Spec sufficiency.** Every 09 §Multi-line text rule has an AC:

| Rule | ACs |
|---|---|
| Keys | AC-102.12 to .16, .18 |
| Model | AC-102.1 to .6, .9, .17, .21, .23 |
| Parity | AC-102.7, .8, .10, .11, .19, .20, .24 |

### Files Modified

The endings come from the plan-time sweep (`C:/Temp/av-kit/s70/pin-sweep.txt`); row 0 records them again, with SHA-256, in `s70-anchors.txt`.

| File | Endings | Rows |
|---|---|---|
| `packages/core/src/avkit_core/domain/capture.py` (`TEXT_NEWLINES`) | CRLF | 1, 4 |
| `packages/api/src/avkit_api/schemas/captures.py` (`TEXT_API_NEWLINES`) | CRLF | 4 |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` (`TEXT_LINE_GAP`) | CRLF | 1 |
| `tools/capture_bake_fixture.py` (`TEXT_FIXTURE_MULTILINE`) | CRLF | 2 |
| `ui/tests/e2e/fixtures/capture-fidelity-multiline-original.png`, `capture-fidelity-multiline-annotated.png` (new) | binary | 2 |
| `ui/tests/e2e/fixtures/capture-geometry.json` (`TEXT_GEOMETRY`) | CRLF | 2 |
| `ui/src/renderer/src/features/capture/capture-text-metrics.ts` (`TEXT_LINE_PITCH`, `TEXT_PLATE_LINES`) | CRLF | 1, 4 |
| `ui/src/renderer/src/features/capture/CaptureViewport.tsx` (`TEXT_SVG_LINES`, `TEXT_DRAFT_KEYS`, `TEXT_DRAFT_HINT`) | CRLF | 4 |
| `ui/tests/e2e/test-ids.ts` (the MEU-102 block, after the MEU-104 block at `:513-514`) | CRLF | 1 |
| `mcp-server/src/toolsets/capture.ts` (`TEXT_MCP_DOC`) | CRLF | 4 |
| `mcp-server/tests/capture.test.ts` (AC-102.21 appended) | CRLF | 3 |
| `tests/unit/test_capture_bake_fixture.py` (AC-102.8 appended) | CRLF | 2 |
| `ui/tests/e2e/capture-inbox.test.ts` (`TEXT_PARITY_E2E`, AC-102.19, AC-102.20) | LF | 3 |
| `tests/unit/test_capture_text_lines.py`, `tests/e2e/test_api_capture_text_lines.py`, `ui/tests/unit/capture-text-lines.behavior.test.ts` (new) | LF | 3 |
| `docs/build-plan/09-screenshot-capture.md` | CRLF | 5 |

Before it writes, each row measures the file's endings with Python bytes, and then writes in that ending. A scratch script that edits a tracked file fails on mixed endings (Session 63 RULE-3). `CapturePage.tsx` is not written: it already stores the draft as typed.

**Byte-hash guard (Session 50).** AC-51.6 and AC-81.13 hash `ui/tests/e2e/test-ids.ts` up to `// MEU-51 primitive harness IDs.` (`:292`). Row 1 appends the MEU-102 block after the MEU-104 block (`:513-514`), after the hashed prefix, so the expected hash stays unchanged. Row 1 runs `ui/tests/unit/capture-action-row.test.ts` as its own check and names the hash it reads in the handoff.

### Project files

These project files are written:
- `.agent/context/meu-status.yaml` (LF), `.agent/context/meu-registry.md` (LF) and `docs/BUILD_PLAN.md` (LF);
- the grouping file (CRLF; tracker row 46 at `:124`);
- the handoff, the two rolling reviews and the reflection;
- `docs/execution/metrics.md` (CRLF) and `.agent/context/current-focus.md` (CRLF);
- this folder's plan, task and scripts.

## Out of Scope

| Item | Basis |
|---|---|
| Automatic wrap or a wrap width | 09 Parity row; C-3 (Later) |
| A layout version or any new text field | D-702; the B-4 scan found no stored newline |
| Refusing control characters other than CR | D-704 |
| Changing the help body | D-706 |
| Text alignment (centre, right) | not in 09 §Multi-line text |
| Changing MARK_CLIP_TEXT | D-675; AC-102.23 guards it |
| An MCP schema or action change | D-711 |
| The band mismatch between the grouping (P3) and `meu-status.yaml` (P2) | Session 70 prompt: named, not changed |
| Members-only URLs or ids, `npm run dist`, the live MCP audit | Session 70 prompt |

## BUILD_PLAN.md Audit

`uv run python tools/meu_status.py render --check` passes at baseline and after rows 6 and H2-2. MEU-102 is `pending`, with its dependency MEU-101 `approved` (`.agent/context/meu-status.yaml:2670`).

## Verification Plan

### 1. Baseline (row 0)

`baseline.ps1`:
1. **Rulings (S9).** Checks that this plan's single `> **Status:**` line carries the budget and execute words, each with a `USER_EXPLICIT` quote, and stops if not.
2. **Queue (S8).** Checks that MEU-82, MEU-101 and MEU-104 are `approved`, that MEU-102 is `pending`, and that `4e35af9` is an ancestor of `HEAD`.
3. **Shapes (S7, Session 61 RULE-3).** Checks by name the 27 shapes this plan relies on:
   - `TEXT_MAX_CHARS`, `TextAnnotation`, its text check, `_clip_text` and MARK_CLIP_TEXT;
   - `TextAnnotationIn` and its `text` field;
   - `text_plate_box`, its `textbbox`, `_apply_text` and its `anchor="la"`;
   - `write_fixture` and the `--region` flag;
   - `segoeAscentPx`, `svgTextBaselineY` and `textBackgroundBox`;
   - the draft's test id, the text baseline and the text child in `CaptureViewport.tsx`;
   - the geometry file's `segoe_ascent` and `arrows` keys;
   - the test-ids hash boundary and the MEU-104 block;
   - the annotate description;
   - `installFidelitySeam` and the AC-82.6 test;
   - 09's anchor.

   It then checks that none of `normalize_text_newlines`, `TEXT_LINE_GAP`, `segoeLinePitchPx`, `textLines`, `write_multiline_fixture`, `MULTILINE_`, `--multiline`, `capture-text-draft-hint`, `CAPTURE_TEXT_DRAFT_HINT`, `segoe_line_pitch`, `text_plates`, `Shift+Enter`, `tspan`, `capture-fidelity-multiline` and `AC-102` appears in the 12 target files, and that the five new files don't exist.
4. **Records.** Creates `C:\Temp\av-kit\s70\tmp`. Records `baseline.sha`, `baseline-dirty.txt` (each dirty path's porcelain line and SHA-256) and `s70-anchors.txt` (every target's endings and SHA-256). It hashes `docs/proposals/2026-11-10-download-logic-divergence-report.md` and never opens it.
5. **Installs.** Installs from the lock with `uv sync --frozen --offline --all-packages` and proves that both `node_modules` trees match their locks (S4).
6. **FFmpeg pair.** Checks the pinned FFmpeg pair, as the identity script binds it.
7. **Base runs.** Captures the base Python, UI and MCP suites, the UI build, the capture Electron spec and `ruff check packages/ tests/`. These are recorded and are not fatal.
8. **Selftests.** Runs the `red-check.py`, `identity.py` and `id-length.py` selftests, each on its own fixtures (Session 56 RULE-4).

At `4e35af9` the shapes and queue blocks ran alone with exit 0 (`C:/Temp/av-kit/s70-plan-shapes-dryrun.txt`).

### 2. Type-only first, then data, then Red, then Green

**Row 1 (Session 53 RULE-2)** adds the names with no behaviour:
- `normalize_text_newlines`, a stub that returns its input, not yet called;
- the adapter's `TEXT_LINE_GAP = 4`, passed as `spacing=` (bytes unchanged; this is the only row 1 change that runs, and `test_capture_adapter.py` proves it);
- `TEXT_LINE_GAP_PX`, `segoeLinePitchPx` (a stub that returns 0) and `textLines` (a stub that returns `[text]`);
- `CAPTURE_TEXT_DRAFT_HINT` in `test-ids.ts`.

**Row 2 (data)** writes TEXT_FIXTURE_MULTILINE and runs `uv run python tools/capture_bake_fixture.py --multiline --out ui/tests/e2e/fixtures` to write the pair; it writes TEXT_GEOMETRY's two keys, each value read from Pillow through the adapter; it appends AC-102.8 to `tests/unit/test_capture_bake_fixture.py`, which passes there. So every path a Red test names exists before row 3 (Session 69 RULE-4), and the Red tests fail by assertion, not on a missing file or key.

**Row 3 (Red)** requires only new-behaviour tests (Session 66 RULE-2):
- pytest: AC-102.2, .4, .5, .6 and .17;
- Vitest (UI): AC-102.9 to .13, .15, .16, .18 and .24;
- Vitest (MCP): AC-102.21;
- Playwright: AC-102.19.

These are not in the Red list:
- AC-102.1 tests what rows 1 and 2 add, so it must pass where it is written.
- AC-102.3, .7, .8, .14, .20 and .23 are guards that pass throughout.
- AC-102.22 is row 5's check.

**Red-check (Session 50).** A Red row passes only when `red-check.py` reads each receipt and names each failing required test as an assertion failure. A required test that fails on a missing name is refused (the `pytest-required-ac-102-2-stub-name` fixture). Every Red test:
- asserts that a name exists before it patches or calls it (Session 52 RULE-4);
- catches a domain exception and asserts its type (Session 62 RULE-3);
- asserts length or membership before indexing (Session 62 RULE-3);
- in Electron, asserts `await expect(locator).toBeVisible()` before it clicks.

`id-length.py` checks every new pytest id against red-check's header width of 71 characters (Session 67 RULE-4). Row 3 runs `ruff check` on the two new pytest files (Session 68 RULE-4).

**Rows 4 and 5 (Green)** change no test file.

### Plan-local scripts

The folder's `baseline.ps1`, `red-check.py`, `identity.py`, `id-length.py` and `session-gate.ps1` are adapted from Session 69's, with the `s70` names and this plan's paths.

| Script | What it does | Plan-time result |
|---|---|---|
| `id-length.py` | checks pytest id widths | selftest: 4 cases, 0 wrong (`C:/Temp/av-kit/s70-plan-idlen-selftest.txt`) |
| `red-check.py` | reads the Red receipts | selftest: 49 fixtures (15 positive, 34 negative), 0 wrong (`C:/Temp/av-kit/s70-plan-rc-selftest.txt`); this includes the AC-102.1 boundary against AC-102.10 to AC-102.19 and the stub-name refusal |
| `identity.py` | binds the tested state | selftest: 0 failures (`C:/Temp/av-kit/s70-plan-identity-selftest.txt`) |

### Session gate (H1-2)

`session-gate.ps1` runs each step with its own receipt (`s70-D6-<id>.txt`) and exit code:

| Step | Command |
|---|---|
| Identity before | `identity.py` |
| Static | pyright, `ruff check packages/ tests/ tools/capture_bake_fixture.py`, UI typecheck and lint, `lint_task_contract.py`, the scope-paths check (S3; the MCP audit baseline is refused), the `red-check.py` selftest, `id-length.py` on the two new pytest files |
| Byte-hash guard | `npm --prefix ui run test -- tests/unit/capture-action-row.test.ts` on its own |
| Fresh full | the whole Python suite (TMP and TEMP at `C:\Temp\av-kit\s70\tmp`; only the Python ids that the base receipt shows failing are excused), `export_openapi.py --check` (unchanged), the whole UI suite and build, the MCP typecheck, build and suite, `meu_status.py render --check`, `issue_triage.py render --check` |
| Runtime | the capture Electron spec `ui/tests/e2e/capture-inbox.test.ts` (AC-102.19, AC-102.20) |
| Identity after | `identity.py`, which must equal the before value |
| Skipped with reason | `mcp-audit` (network and the installed servers), `build-record` (no release and no package build) |

The handoff copies this session's counts from the receipts (Session 63 RULE-2).

## Stop Conditions

| Id | Condition | Action |
|---|---|---|
| S1 | A required Red test passes before its Green | fix the test; never weaken the Green |
| S2 | A Green row needs a test file change | stop; a moved pin goes into the handoff as a departure, and to Mat if it changes an AC (S12) |
| S3 | `HEAD` moves, or a path outside this plan and `baseline-dirty.txt` changes, or a `baseline-dirty.txt` path this plan doesn't write changes its SHA-256 | stop and ask Mat; never commit, stash or revert another session's work |
| S4 | `uv sync --frozen --offline` or a `node_modules` check fails at baseline | stop and ask Mat |
| S5 | A test or row reaches YouTube or the network, writes the system clipboard, or reads a user's capture inbox or the app database | stop |
| S6 | A raw value (a user's capture path, a mark's text) reaches a log, stdout, a response body or the Console. The paths of generated fixture files, which `tools/capture_bake_fixture.py` (`:331-333`) and the adapter (`adapter.py:769`) already print, are synthetic and not in scope (plan review round 1, Q11) | fix it in the row or ask (Session 50 RULE-1) |
| S7 | A shape this plan relies on is missing, or a new name exists at baseline | stop and re-plan |
| S8 | The queue isn't as row 0 expects | stop and ask Mat |
| S9 | The Status line lacks the budget or execute words | stop at row 0 |
| S10 | Codex is unavailable or the ledger refuses a round | Mat reviews |
| S11 | A status file is dirty from another session | copy it to `C:/Temp/av-kit/s70/pre-status/`, byte-edit only this session's fields, and prove them with `render --check` and a diff (Session 61 RULE-5) |
| S12 | A contract or AC in this plan needs to change | record a departure before the gate. One that changes an AC goes to Mat as a Decision Brief whose do-nothing option is "record it as a departure and keep the approved text" (Session 59 RULE-3) |
| S13 | A program other than this session's holds a resource that a row needs (a port, a file lock, a key such as ShareX's F2) | stop and ask Mat; never stop another program (Session 57 RULE-4) |

## Decision Log

> [!WARNING]
> D-701 to D-711 are autonomous, and each lists its alternatives in `reasoning`. D-712 records Mat's ruling at the plan gate, and is filled in when he rules. D-701 to D-716 were free at plan time (`C:/Temp/av-kit/s70/id-probe.txt`).
>
> Carried, and not relisted in the block:
> - D-158: human, `USER_EXPLICIT 2026-10-29 "all recommendations are accepted"`, grouping §8 `:141`;
> - D-159: autonomous, Local Canon, `:142`;
> - D-160: autonomous, Local Canon, `:143`;
> - D-674 and D-675: autonomous, stage `grouping`, §9.8.
>
> The reflection carries these and every id the decision probe returns (Session 54 RULE-5). The probe reads only the grouping's §8, so D-674 and D-675 (§9.8) are carried by hand.

```yaml
decision_log:
  - id: D-701
    stage: planning
    question: "What does a newline in a text mark mean?"
    resolution: autonomous
    class: two-way
    chosen: "A line is one item of text split on LF; line i's top is y plus i times the pitch, the pitch is the Segoe ascent at the mark's size plus 4 px, an empty line has no glyphs and a trailing LF adds an empty last line; both the bake and the preview follow this"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s70-g3-pitch.txt - Pillow's pitch is getbbox A bottom plus 4, equal to the Segoe ascent plus 4 at sizes 1 to 500"
      - "C:/Temp/av-kit/s70-g3-pillow.txt - the bake already splits on LF"
      - "docs/build-plan/09-screenshot-capture.md:920 - line spacing derives from font_size"
    research:
      engine: none
      sources: []
    reasoning: "The bake already draws lines this way, and every saved annotated file was baked by it, so defining the meaning as the bake's keeps every file as it is and moves only the preview. A pitch of 1.2 times the size lost: it changes the bake and would need a layout version. Dropping the trailing empty line lost: Pillow keeps it, so the plates would disagree. Two-way."
    human_message_reference: null
  - id: D-702
    stage: planning
    question: "Do stored marks need a layout version (G-3)?"
    resolution: autonomous
    class: two-way
    chosen: "No; no field is added, because the pitch derives from font_size and no stored text mark holds a newline"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s70-b4-scan.txt - 29 shot rows, 5 sidecars, 11 text marks, 0 LF, 0 CR"
      - "docs/build-plan/09-screenshot-capture.md:920 - no new field unless G-3 shows stored marks need one"
    research:
      engine: none
      sources: []
    reasoning: "A version only matters when an old mark would bake differently, and none would: the bake is unchanged and no stored mark holds a newline. Adding a version anyway lost: a field the rule says not to add. The scan read the inbox before Mat was told, which the plan records as a departure. Two-way."
    human_message_reference: null
  - id: D-703
    stage: planning
    question: "What happens to CR in a text mark?"
    resolution: autonomous
    class: two-way
    chosen: "CRLF and a lone CR are stored as LF, at the domain's TextAnnotation and at the API's TextAnnotationIn before the length check"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s70-g3-pillow.txt - the bake draws CR as a glyph and keeps a lone CR on one line"
      - "C:/Temp/av-kit/s70-api-validator-probe.txt - a before validator leaves the OpenAPI schema equal"
    research:
      engine: none
      sources: []
    reasoning: "A Windows client or a pasted text sends CRLF, and the user means a new line. Folding at both layers means a sidecar never holds CR and the length rule counts what is stored. Refusing CR lost: it breaks a client that sends CRLF for a new line. Leaving it as a glyph, the do-nothing option, lost: the preview and the bake would disagree on a stray glyph. Two-way."
    human_message_reference: null
  - id: D-704
    stage: planning
    question: "Do other control characters change?"
    resolution: autonomous
    class: two-way
    chosen: "No; a tab and the other control characters pass as today, and only CR is folded"
    source_tag: Local Canon
    precedents:
      - "Session 69 D-699 - annotate accepts control characters, and render keeps parity with it"
      - "C:/Temp/av-kit/s70-b4-scan.txt - no stored mark holds one"
    research:
      engine: none
      sources: []
    reasoning: "09 asks for newline semantics only. Refusing control characters lost: it changes accepted input that 09 doesn't mention and that D-699 kept. Two-way."
    human_message_reference: null
  - id: D-705
    stage: planning
    question: "How does the field take Shift+Enter?"
    resolution: autonomous
    class: two-way
    chosen: "A textarea with the same test id, wrap off and rows equal to the line count; Enter without Shift commits, Shift+Enter is left to the browser, composition and Escape stay as today"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:1521-1547 - the input and its onKeyDown"
      - "ui/src/renderer/src/features/capture/capture-import.ts:137 - isEditableTarget already covers a textarea"
    research:
      engine: none
      sources: []
    reasoning: "Only a textarea holds a newline in its value; an input strips it. A contenteditable lost: it needs its own text model and paste cleaning. Keeping the test id keeps every existing pin. Two-way."
    human_message_reference: null
  - id: D-706
    stage: planning
    question: "Where does the hint show?"
    resolution: autonomous
    class: two-way
    chosen: "A sibling of the field, shown only while it is open, reading Enter to finish, Shift+Enter for a new line, Esc to cancel, and named by the field's aria-describedby; the help body doesn't change"
    source_tag: Local Canon
    precedents:
      - "docs/build-plan/09-screenshot-capture.md:919 - the field shows the hint while editing"
    research:
      engine: none
      sources: []
    reasoning: "The rule asks for the hint while editing, so it lives with the field. A placeholder lost: it disappears as soon as the user types. A help body sentence alone lost: the user doesn't see it while typing. Two-way."
    human_message_reference: null
  - id: D-707
    stage: planning
    question: "How does the preview draw lines?"
    resolution: autonomous
    class: two-way
    chosen: "One tspan per line with an absolute x and y, only when the text holds LF; a one-line mark keeps its single text child"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s70-g3-svg.txt - Chromium collapses LF in a text element"
      - "ui/src/renderer/src/features/capture/CaptureViewport.tsx:323 - y is svgTextBaselineY"
    research:
      engine: none
      sources: []
    reasoning: "Absolute y per line puts each baseline on the bake's pitch with no font-dependent dy. Always using tspans lost: it changes every one-line mark's DOM, which the AC-82.6 oracle and many tests read. white-space pre lost: the browser's line height is not the bake's pitch. Two-way."
    human_message_reference: null
  - id: D-708
    stage: planning
    question: "What does a commit store?"
    resolution: autonomous
    class: two-way
    chosen: "The draft's value as typed, with every LF, leading and trailing; a draft of only whitespace and LF commits nothing, as draftCommits's trim decides today"
    source_tag: Local Canon
    precedents:
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:267-277 - draftCommits"
      - "ui/src/renderer/src/features/capture/CapturePage.tsx:2461-2480 - onTextCommit stores textDraft.value"
    research:
      engine: none
      sources: []
    reasoning: "The page already stores the value as typed, so the bake and the preview see what the user typed. Trimming trailing LF lost: a user who adds an empty line to grow the plate would lose it. Two-way."
    human_message_reference: null
  - id: D-709
    stage: planning
    question: "Which plate cases does the geometry file pin?"
    resolution: autonomous
    class: two-way
    chosen: "segoe_line_pitch for the 17 sizes of segoe_ascent, and text_plates holding only the cases whose preview plate equals Pillow's to the pixel; the others are pinned by the union rule"
    source_tag: Local Canon
    precedents:
      - "C:/Temp/av-kit/s70-matrix.txt - multi-line drift never exceeds the one-line drift at the same size"
      - "ui/tests/e2e/fixtures/capture-geometry.json - hand-kept, read by five tests"
    research:
      engine: none
      sources: []
    reasoning: "The one-line plate already drifts by up to 5 px at size 128, and multi-line adds no drift of its own. Pinning drifted cases lost: it would pin today's drift as the contract. Two-way."
    human_message_reference: null
  - id: D-710
    stage: planning
    question: "How is the multi-line bake fixture made?"
    resolution: autonomous
    class: two-way
    chosen: "A --multiline flag and write_multiline_fixture in tools/capture_bake_fixture.py, run in row 2 before the Red tests, writing a 240x160 pair with Hi, an empty line, Hi and a trailing LF at size 32 on a yellow plate"
    source_tag: Local Canon
    precedents:
      - "tools/capture_bake_fixture.py:57 - write_fixture, and :328 the --region flag"
      - "C:/Temp/av-kit/s70-fixture-probe.txt - the plate and the two ink runs"
      - "Session 69 RULE-4 - every path a test names exists at Red"
    research:
      engine: none
      sources: []
    reasoning: "The same tool and the real bake make the pair, so it can't drift from the adapter. An empty and a trailing line test both cases in one image, and size 32 is AC-82.6's size with drift of 1 px. Changing the existing pair lost: it moves AC-82.6. Two-way."
    human_message_reference: null
  - id: D-711
    stage: planning
    question: "Does MCP change?"
    resolution: autonomous
    class: two-way
    chosen: "Only the annotate description gains one sentence on the newline rule; no action, schema or audit baseline changes"
    source_tag: Local Canon
    precedents:
      - "mcp-server/src/toolsets/capture.ts:101 - the annotate description"
      - "mcp-server/tests/capture.test.ts:370 - AC-59.16 pins the examples and bans two words"
    research:
      engine: none
      sources: []
    reasoning: "An agent is the main sender of a raw newline, so the description says what it does. A schema change lost: the body already takes any string. Two-way."
    human_message_reference: null
  - id: D-712
    stage: planning
    question: "What is the execution review budget, and does execution start?"
    resolution: human
    class: two-way
    chosen: "Execution review budget 30M with the default cap of 6 rounds; execute now that the plan review has approved"
    recommendation: "An execution review budget of 30M (the round 1 estimate of 12M twice plus a 6M recheck, Session 60 RULE-5) with the default cap of 6"
    source_tag: Human-approved
    precedents:
      - "Session 70 prompt - at the plan gate, ask for the execution budget"
      - "GUARDRAILS.md SIGN 3 - direct human execution authorization satisfies the plan-to-execution gate"
    research:
      engine: none
      sources: []
    reasoning: "Mat gave the budget and the execution words at the plan gate after the round 1 approval, through the HDP. The ledger still stops the loop at 6 rounds and before a round that would overrun 30M. The do-nothing options, the ledger default budget and not executing, were not chosen. The gate question misstated the execution default as 10.5M (the plan-mode figure); review_ledger.py:102 sets it to 21M. Mat chose 30M, not the default, so the misstatement did not decide the ruling; it is disclosed to him."
    human_message_reference: "USER_EXPLICIT 2026-11-13 '30M (Recommended)'; USER_EXPLICIT 2026-11-13 'Execute now (Recommended)'"
```

## Research References

- No web research: every rule comes from 09, the grouping's §8 and §9, the code at `4e35af9` and the plan-time probes.

## Planning receipts

| Receipt | What it holds |
|---|---|
| `C:/Temp/av-kit/s70/id-probe.txt` | D-701 to D-716 and the AC-102 family were free |
| `C:/Temp/av-kit/s70/pin-sweep.txt` | the callers and pins of every name this plan touches, with each file's endings |
| `C:/Temp/av-kit/s70-g3-pillow.txt`, `C:/Temp/av-kit/s70-g3-pitch.txt` | what the domain, the API and the bake do today with LF and CR; Pillow's pitch at sizes 1 to 500 |
| `C:/Temp/av-kit/s70-g3-svg.txt` | the SVG preview collapses LF in Electron 42.11.18 |
| `C:/Temp/av-kit/s70-g3-plate-ts.txt`, `C:/Temp/av-kit/s70-matrix.txt` | today's one-line preview plate; the TEXT_PLATE_LINES prototype against Pillow over the input matrix |
| `C:/Temp/av-kit/s70-fixture-probe.txt` | the multi-line fixture's plate and ink runs |
| `C:/Temp/av-kit/s70-api-validator-probe.txt` | a before validator folds CR, leaves the schema equal and still refuses a non-`str` |
| `C:/Temp/av-kit/s70-b4-scan.txt` | the stored-marks scan, counts only (the B-4 departure) |
| `C:/Temp/av-kit/s70-plan-shapes-dryrun.txt` | `baseline.ps1`'s shapes and queue blocks run alone at `4e35af9` (exit 0) |
| `C:/Temp/av-kit/s70-plan-rc-selftest.txt`, `C:/Temp/av-kit/s70-plan-identity-selftest.txt`, `C:/Temp/av-kit/s70-plan-idlen-selftest.txt` | the red-check selftest (49 fixtures, 0 wrong), the identity selftest (0 failures), the id-length selftest (4 cases, 0 wrong) |
| `C:/Temp/av-kit/s70-plan-decision-probe.txt` | the decision probe with this plan and the grouping as sources |
| `C:/Temp/av-kit/s70-plan-task-lint.txt` | `lint_task_contract.py` on `task.md`, with `RECEIPTS_DIR=C:/Temp/av-kit` |

No suite or build ran at plan time.

## Validation stage contract

- **Static:** `pyright`, `ruff check packages/ tests/ tools/capture_bake_fixture.py`, `npm --prefix ui run typecheck`, `ui-lint`, `lint_task_contract.py`, the scope-paths check, the `red-check.py` selftest and `id-length.py`.
- **Targeted:** each row's own files. `red-check.py` reads the Red receipts, and `capture-action-row.test.ts` runs on its own in the row that touches `test-ids.ts`.
- **Fresh full:** the session gate runs the whole Python, UI and MCP suites, the OpenAPI check, the UI and MCP builds and the capture Electron spec.
- **Identity:** `identity.py` binds `HEAD`, the work tree minus `PROJECT_ARTIFACTS`, the pinned FFmpeg pair and the runtime. The gate records it before and after, and H1-6b checks the handoff's evidence against it.

Every stage is blocking. The native shell is PowerShell, the output is `evidence.v1`, and intermediate reuse stays off.
