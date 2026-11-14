---
date: "2026-11-13"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-13-capture-text-multiline/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s70-plan-canonical-2026-11-13-capture-text-multiline"
round: 1
---

# Critical Review: 2026-11-13-capture-text-multiline

> **Review Mode:** `plan`
> **Verdict:** `approved`

## Scope

Reviewed the working-tree implementation plan, task table and five plan-local scripts against the MEU-102 spec, grouping, registry, affected production code, existing tests and supplied receipts. HEAD is `4e35af91ac242514b8994c286a49b37a8f1cb2ce`, branch `main`; no tracked path is dirty. Applied PR-1 through PR-9, the Materiality Gate and Verdict Rule. Claude Code/Anthropic authored the plan; Codex is the independent reviewer.

**Intent anchor:** Session 70 lets a text mark hold more than one line. In the editor's text field, Enter commits and Shift+Enter adds a line, Enter belongs to the IME while it composes, and the field shows a hint. A stored `\n` starts a new line with a pitch derived from `font_size`, with no new field. `\r\n` and `\r` are stored as `\n`. The preview draws each line where the bake draws it, and bake fixtures prove that they agree. Nothing wraps.

**Intent assessment:** yes, as a plan. The proposed production changes and behavioral oracles cover the requested feature. No evidence-backed High or Critical defect was found. The small precision corrections below do not change the intended feature or exceed its inherited 1 px fixture tolerance.

Only read-only source inspection, scratch Python probes and the three expressly permitted selftests ran. Writes were confined to `C:/Temp/av-kit`. No product suite, build, baseline/session gate, package manager, backend, MCP server, network request or clipboard operation ran. No private settings, capture inbox, app database, forbidden report or stored-marks scan script was opened. The coordinator owns the canonical report copy and ledger recording. Approval does not authorize execution; D-712 remains Mat's gate.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and end-to-end trace

Accepted: draft keydown → `onTextDraftChange` → `onTextCommit` → `applyHistory`/`annotationsRef.current` → save body/`parseAnnotateBody` → `TextAnnotationIn` → `_annotations_from_in` → `TextAnnotation` → sidecar/bake. The renderer consumes the same text through `textBackgroundBox` and the proposed per-line SVG. AC-102.16 and .17 join the renderer and Python paths; .19 observes real preview/bake pixels (`implementation-plan.md:159-170,190-193,259-262`).

The Keys, Model and Parity rows at `09-screenshot-capture.md:920-922` map to explicit implementation rows and ACs (`implementation-plan.md:274-280`). IME, hint, re-edit, CR folding, length boundaries, blank/trailing lines, second-line hit testing and no wrap are represented. No missing goal sentence or required deliverable found.

## Q2 — TEXT_NEWLINES and TEXT_API_NEWLINES

Accepted folding CRLF first, then lone CR, before domain and API length validation. The scratch mirror accepted 250 three-character CRLF pairs as 500 stored characters and refused 251 pairs at both layers. It verified frozen-dataclass assignment, idempotence through `replace` and `_clip_text`, and non-string refusal. Adding the before validator leaves the model schema unchanged when the class's existing name and docstring are preserved.

Sidecar decoding constructs `TextAnnotation` (`services/capture.py:381-389`); annotate/render construct it through `_annotations_from_in` (`routes/captures.py:195-204,445-469`). Clamp/crop use `replace`, which revalidates. Export consumes the saved baked image. No ordinary constructor path bypasses the proposed fold. The existing request-error handler emits a fixed 422 envelope without refused input (`errors.py:121-128`); AC-102.5 covers that route and the unchanged OpenAPI snapshot. No substantive objection to D-703/D-704.

## Q3 — TEXT_LINE_GAP

Accepted explicit `spacing=4` at both draw calls. An AST-based scratch copy of those two functions produced identical pixels in **260 comparisons** over the input texts, 13 sizes, and backgrounds present/absent. No production file was changed. The probe also confirmed `getbbox("A")[3]` equals the UI ascent formula at **all sizes 1–500**. This is the installed Segoe/Pillow behavior the plan pins, rather than a new typography rule.

The existing one-line source/box assertions at `test_capture_adapter.py:612-618` remain compatible. The default/region fixture branches are retained, with their existing regeneration guards scheduled. No bake-byte regression mechanism was found from making Pillow's default explicit.

## Q4 — TEXT_LINE_PITCH, TEXT_PLATE_LINES and TEXT_GEOMETRY

Accepted the per-line pitch and union model, including empty lines as points. Hit testing and scale handles already call `textBackgroundBox` (`capture-hit-test.ts:126,138`; `capture-transform.ts:125,141-150`), so they inherit its multiline extent without another geometry implementation. The supplied matrix supports retaining the existing per-line approximation; it does not establish a universal 5 px bound for arbitrary text. For example, the mixed-word size-128 case has 7 px drift, which D-709's choice to preserve the existing one-line approximation accommodates.

**Nonblocking precision correction:** a literal union of today's *returned* one-line boxes does not make all 16 cases exact. The helper clamps each line's height to at least 1 (`capture-text-metrics.ts:60-61`). For two spaces, LF, two spaces, the literal union is `[10,29,14,43]` at size 8 and `[10,38,18,61]` at size 16; Pillow and the plan's exact table end at 42 and 60 respectively (`implementation-plan.md:163,238,253`). The scratch mirror matched the other **14/16** cases. Clarify union of glyph extents before minimum-size clamping, or classify those two entries as tolerance cases. This is a 1 px precision discrepancy within the retained oracle tolerance, not a materially missing feature.

Also correct AC-102.10's shorthand that a trailing LF grows the plate "by one pitch" (`implementation-plan.md:253`): its empty-line origin advances by one pitch, but `Hi` at size 16 extends the bottom from 38 to 42, **4 px**, not 22. The explicit boxes already show the intended result.

## Q5 — TEXT_SVG_LINES

Accepted absolute `<tspan>` positions: `svgTextBaselineY` adds the same ascent used by Pillow's `la` anchor, then each line adds the verified pitch. At size 16 and y=20 the proposed baselines 38/60/82 follow directly. An empty span requires no glyph to reserve spacing because later spans have absolute positions. SVG text does not introduce wrapping.

Keeping the single text child for a mark without LF preserves existing SVG pins and AC-82.6's input. AC-102.11 checks structure/positions and .19 checks rasterized parity. No new baseline or empty-slot defect found; actual Electron behavior remains execution evidence to collect.

## Q6 — TEXT_DRAFT_KEYS and TEXT_DRAFT_HINT

Accepted the textarea swap, native Shift+Enter insertion, Enter prevention/commit and existing composition guard. Existing draft casts are erased TypeScript assertions; the used `.value`, clear and typing operations support textarea. The page stores the value without trimming; `draftCommits` uses trim only to decide whether anything commits (`CapturePage.tsx:268-276,2458-2489`). Consequently whitespace-only drafts remain no-ops and LF changes affect dirty state correctly.

`wrap="off"`, line-count rows, `resize-none`, an editing-only hint and `aria-describedby` satisfy the requested behavior. Pointer-transparent hint content does not capture canvas events. Paste and copy recognize textarea (`capture-import.ts:132-138`); editor keys return while a draft exists (`CapturePage.tsx:1648-1652`), and zoom excludes textarea (`CaptureViewport.tsx:743-745`). No new canvas-copy, Delete or zoom-key interception found.

Appending after MEU-104 preserves the prefix hashed by AC-51.6/AC-81.13. Independently computed prefix SHA-256: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`.

## Q7 — TEXT_FIXTURE_MULTILINE and TEXT_PARITY_E2E

Accepted the separate flag/pair, exclusive with `--region`, before Red. The scratch draw confirmed a 240×160 fixture, plate `(20,28,51,133)` and exactly two ink runs `(28,50)` and `(106,128)`. A collapsed one-line preview cannot satisfy the two-run oracle. Default and region outputs retain separate unchanged branches and existing fixture checks.

The parameterized seam must serve the multiline mark together with its pair; today's helper passes `FIDELITY_MARK` into detail responses (`capture-inbox.test.ts:2107,2117,2144,2152`). Read the plan's fixture argument as carrying that matching mark, not merely swapping two filenames. This is an evident implementation detail checked by AC-102.19, not an unreachable producer. AC-82.6 retains its default input/assertions; AC-102.20 guards the parameterization. Row 2 creates every named fixture/key before row 3 (`task.md:86-87`).

## Q8 — Type-only names and Red rules

Accepted rows 1 → 2 → 3 → 4. New behavior imports have names before Red; constants and the fixture writer are supplied before their guards. The declaration list includes the names that matter for required tests; the adapter constant is also created in row 1. Assertions precede missing values, list indexing and UI interactions. Domain acceptance failures are caught then asserted. Guards and the spec check are correctly excluded from the required-failure set.

The independent inventory found exactly **16 required titles**: Python .2/.4/.5/.6/.17; UI .9/.10/.11/.12/.13/.15/.16/.18/.24; MCP .21; Playwright .19. The guard selectors distinguish .1/.14, .82.6 and .102.20 as intended for the prescribed title format. The Playwright .19 filter's unescaped dot is imprecise regex spelling but has no competing selected title in this file. No material selector error found.

Fresh selftests: red-check **49 fixtures, 0 wrong**; identity **0 failures**; id-length **4 cases, 0 wrong**. The actual proposed tests do not exist yet; these observations establish plan feasibility and checker behavior, not a completed Red/Green cycle.

## Q9 — TEXT_MCP_DOC

Accepted appending the sentence after `ANNOTATE_EXAMPLE` while retaining both examples. It contains neither banned word, leaves the action/schema definitions alone, and .21 explicitly checks a literal backslash followed by n (`implementation-plan.md:168,264`; `mcp-server/tests/capture.test.ts:370-381`). The TypeScript literal must escape its backslashes to yield those two runtime characters. No audit-baseline change is required or allowed by the session scope.

## Q10 — Endings, identity, scope and records

The scratch inventory checked **18 Files Modified paths**, all allowed by the gate, and **five scheduled absent files**. Existing stated endings match current bytes; new tests are LF and PNGs binary. The py-lint step explicitly includes the fixture tool. All six root Python tools referenced in task commands exist. No scope rejection of a planned product/test/spec file found.

Accepted identity's HEAD/diff/untracked/runtime/font/binary binding and explicit closeout-output exclusions; its selftest ran only in scratch storage. The live whole-tree identity was not run because it would encounter the sandbox-visible private settings file. Row 6 confines writes to MEU-102 and grouping row 46, preserves P2/P3, and requires pre-status copies, diffs and render checks (`task.md:79,91`).

Baseline rulings inspect the single Status line; queue checks named statuses and ancestor; shape checks count required anchors and refuse already-present new features. The supplied isolated queue/shapes receipt passes at this HEAD. The current missing execution ruling is expected. The session gate stops on blocking failures, records later stages not_run and compares input identities; no concrete materially missing deliverable that these controls would certify was demonstrated. No paperwork finding raised.

## Q11 — Safety

Accepted generated images/temporary app data, in-process API tests, recording UI fakes, no new clipboard operation, and the capture-only Electron selector. Vitest excludes E2E; the real-clipboard filmstrip test is outside the listed Playwright commands. The existing capture launcher sets `AVKIT_E2E` and isolated `AVKIT_APP_DATA` (`capture-inbox.test.ts:65-72`); TMP/TEMP are redirected by the session scripts. No planned private-inbox/database read, YouTube operation, live audit/server call or report-content read is needed. G-3's no-version conclusion follows from the supplied counts and unchanged existing LF bake semantics; the disclosed scan departure was not reopened.

**Nonblocking wording limitation:** S6's literal prohibition on *every* raw path in stdout is broader than this plan's existing fixture machinery: the fixture CLI prints generated paths (`tools/capture_bake_fixture.py:331-333`) and the adapter logs generated output paths (`adapter.py:769`). Row 2 calls that CLI. These are generated fixture paths, not disclosed private capture paths or mark text. Distinguish synthetic fixture diagnostics from private-data leakage, or suppress the new mode's diagnostics if the literal rule is intended. This does not establish a new security exposure and is not a reason to reopen prior sessions.

## Checklist Results

All manual checks below were observed by `codex-independent-reviewer`; their exit is null. A pass judges the unstarted plan's substantive readiness, with the nonblocking precision notes above. It does not claim product validation ran.

| Check | Result | Procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 | pass | Compare plan contracts/ACs with task rows 0–6 and H1/H2 | null | Matching scope and dependency order |
| PR-2 | pass | Inspect current production source, task state and inventory | null | No tracked dirty paths; five new product/test files absent; rows unchecked |
| PR-3 | pass | Read task contract columns and supplied lint receipt | null | 24 rows, dependencies acyclic, owners/deliverables/validation/status supplied |
| PR-4 | pass | Trace planned assertions to production observables; inspect scripts and run permitted probes | null | End-to-end traces, pixel oracle, 16 required Reds; minor extent notes in Q4 |
| PR-5 | pass | Reconcile D-701–D-711 with spec, grouping and measured behavior | null | Choices are sourced; D-712 remains reserved |
| PR-6 | pass | Inspect handoff/review destinations and correction routing | null | One MEU handoff; rolling reviews; coordinator owns canonical copy |
| PR-7 | pass | Compare Out of Scope with supplied scope and 09 rules | null | No required feature silently deferred |
| PR-8 | pass | Trace callers and inspect positive/negative oracles and gate flow | null | No demonstrated material false-pass; fixed 422 handler; actual pixel producer |
| PR-9 | pass | Compare named contracts with AC/task references | null | Canonical mechanisms referenced; Q4 precision shorthand is nonblocking |
| Completed implementation/real Electron parity | n/a | Not authorized for this read-only plan review | null | Product checks intentionally not run |

### Independently executed evidence

Commands used `.venv/Scripts/python.exe` directly, with `PYTHONDONTWRITEBYTECODE=1`; selftests also used TMP/TEMP under `C:/Temp/av-kit/s70/review`. Shell streams were redirected, child exits preserved immediately, and completed receipts read. The two scratch scripts contain only synthetic inputs and source/inventory reads.

```json
{"schema_version":"evidence.v1","check_id":"s70-plan-behavior-probes","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s70/review/probe.py","cwd":"P:/av-kit","scope":"read-only scratch mirrors of proposed normalization, explicit draw spacing and plate arithmetic","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main@4e35af91ac242514b8994c286a49b37a8f1cb2ce; current unstarted plan; scratch mirrors only","output":"250 CRLF pairs accepted as 500 stored chars; 251 refused at both layers. Frozen dataclass and replace pass; before-validator model schema unchanged. Ascent=A bbox bottom at sizes 1..500. 260 spacing comparisons pixel-identical. Literal returned-box union matches 14/16 exact cases: whitespace-only bottoms +1 px at sizes 8/16. Trailing-LF Hi@16 bottom extension 4 px versus 22 px pitch. Fixture plate (20,28,51,133), ink runs (28,50)/(106,128).","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-plan-inventory","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe C:/Temp/av-kit/s70/review/inventory.py","cwd":"P:/av-kit","scope":"HEAD, branch, public changed-path inventory, scope, endings, hash prefix and Red title list","phase":"targeted","exit_code":0,"result":"pass","tested_state":"main@4e35af91ac242514b8994c286a49b37a8f1cb2ce; current unstarted plan","output":"main; tracked dirty count 0; out-of-review paths []; 18 Files Modified paths all allowed; 5 scheduled absent files; stated endings mismatches []; 16 distinct required Red titles; 6 referenced root Python tools, none missing; prefix SHA256 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-plan-red-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-text-multiline/red-check.py --selftest","cwd":"P:/av-kit","scope":"synthetic runner-receipt fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current working-tree plan-local script at main@4e35af9","output":"red-check selftest: 49 fixture(s) (15 positive, 34 negative), 0 wrong: []","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-plan-identity-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-text-multiline/identity.py --selftest","cwd":"P:/av-kit","scope":"synthetic scratch git repository only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current working-tree plan-local script at main@4e35af9","output":"Bound mutations changed state and refused historical evidence; excluded artifacts kept state; identity selftest: 0 failure(s).","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-plan-idlen-selftest","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe docs/execution/plans/2026-11-13-capture-text-multiline/id-length.py --selftest","cwd":"P:/av-kit","scope":"four synthetic title lengths; no pytest collection","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current working-tree plan-local script at main@4e35af9","output":"71-character titles accepted; 72-character titles refused; id-length selftest: 4 case(s), 0 wrong.","fresh":true}
```

## Verdict

`approved` — the plan delivers the requested multiline feature and its independent parity oracle. No High/Critical finding warrants another bounded review round. Carry the Q4 extent/wording corrections and Q11 synthetic-diagnostic distinction as nonblocking notes; collect actual Red/Green and Electron evidence during execution. Mat's execution-budget and execute ruling remain pending.

## Follow-up Actions

- Coordinator validates and copies this report byte for byte to the canonical rolling plan-review path and records the matching round-1 verdict.
- Reconcile the small Q4 plate precision statements before encoding immutable test expectations; retain the existing single-line behavior and inherited tolerance.
- At the plan gate obtain D-712 from Mat. This review performs and authorizes no implementation or commit.
