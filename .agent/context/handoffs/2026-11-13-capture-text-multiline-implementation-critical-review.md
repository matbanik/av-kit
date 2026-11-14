---
date: "2026-11-13"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-13-capture-text-multiline/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s70-execution-2026-11-13-capture-text-multiline"
round: 1
---

# Critical Review: 2026-11-13-capture-text-multiline

> **Review Mode:** `execution`
> **Verdict:** `approved`

## Scope

Reviewed Session 70 / MEU-102's uncommitted delta against `main` at `4e35af91ac242514b8994c286a49b37a8f1cb2ce`: production changes, new and modified tests, both multiline PNGs, geometry data, the plan/task/scripts, handoff, and this session's project-record edits. Claude Code / Anthropic authored the work; Codex did not implement it. Applied IR-1 through IR-7, AV-1 through AV-6, the Materiality Gate and Verdict Rule.

**Intent anchor:** Session 70 lets a text mark hold more than one line. In the editor's text field, Enter commits and Shift+Enter adds a line, Enter belongs to the IME while it composes, and the field shows a hint. A stored `\n` starts a new line with a pitch derived from `font_size`, with no new field. `\r\n` and `\r` are stored as `\n`. The preview draws each line where the bake draws it, and bake fixtures prove that they agree. Nothing wraps.

**Intent achieved:** yes. No evidence-backed High/Critical defect or other actionable finding was found.

This review used source/diff inspection, named receipt reads, permitted Python/Pillow probes, the required Red-receipt checker, identity recomputation, and read-only OpenAPI/registry checks. No test runner, build, baseline/session gate, app/backend, MCP server, network operation or clipboard operation ran during review. Writes were confined to `C:/Temp/av-kit`. No forbidden settings, user inbox, app database or forbidden report was opened. The coordinator owns the canonical report copy and ledger recording. H2, commit and push are outside this verdict.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Q1 — Goal and end-to-end trace

Accepted the complete trace: textarea keydown/change → page draft → commit/history/`annotationsRef.current` → parsed save POST → `TextAnnotationIn` → `_annotations_from_in` → `TextAnnotation` → sidecar/bake. AC-102.16 checks the real renderer's recorded POST, and AC-102.17 uses the real API/service/adapter stack with a recording constructor that delegates to the real domain object (`capture-text-lines.behavior.test.ts:405`; `test_api_capture_text_lines.py:128`). Preview tspans and plate consume the same LF text and pitch (`CaptureViewport.tsx:333`; `capture-text-metrics.ts:58`). AC-102.19 checks actual Electron pixels. Every sentence of the goal has implementation and behavioral evidence; no missing goal slice was found.

## Q2 — TEXT_NEWLINES and TEXT_API_NEWLINES

Accepted CRLF-first, then lone-CR folding before length validation at both boundaries (`domain/capture.py:345,364`; `schemas/captures.py:126`). Independent probes covered mixed CR/LF runs, preserved LF/tab/other controls, idempotence, 250 versus 251 CRLF pairs, invalid types and empty strings; the API also rejects a lone surrogate. Existing fixed 422 handling discards rejected input (`packages/api/src/avkit_api/errors.py:121`), and AC-102.5 checks the refusal envelope without echo.

Annotate/render share `_annotations_from_in` (`routes/captures.py:158,452,468`); sidecar loading constructs `TextAnnotation` (`services/capture.py:382`); crop's `replace` revalidates (`domain/capture.py:531`); saved export consumes the baked result. No constructor path bypass or meaning change beyond CR folding was found. The independent OpenAPI check exited 0, and the snapshot has no HEAD delta.

## Q3 — TEXT_LINE_GAP and bake compatibility

Accepted explicit `spacing=4` at both Pillow calls (`adapter.py:71,151,893`). Independent draws compared the old default against explicit spacing over 40 text/size combinations: identical pixels and boxes. Eight CRLF/lone-CR bakes at sizes 16/32, with/without a plate, equaled the corresponding LF PNG file bytes. The fresh full gate retains the existing one-line, fixture, AC-82/AC-90 and render guards. No changed old bake behavior was found. Pitch derives from size with the existing font/runtime inputs bound in the identity; no new persisted field or layout version was introduced.

## Q4 — TEXT_LINE_PITCH, TEXT_PLATE_LINES and TEXT_GEOMETRY

Accepted all 17 pitch entries and all 16 exact plate entries after independently recomputing them with Pillow. The implementation unions unrounded glyph extents, treats empty lines as points, then rounds/clamps once (`capture-text-metrics.ts:58`). This correctly handles the whitespace-only cases that a union of clamped line boxes would overgrow. Existing one-line values remain equivalent.

The independent matrix mirror covered 117 multiline text/size combinations and found no drift beyond the corresponding inherited one-line tolerance. This is not a universal 1 px plate guarantee: existing large-size approximation can reach 7 px in the supplied matrix. The actual size-32 Electron fixture meets its 1 px oracle. Hit testing, selection/scale handles and `scaleTextMark` all call the shared plate helper (`capture-hit-test.ts:126,138`; `capture-transform.ts:125,141`); AC-102.24 proves second-line selection. No added geometry defect was found.

## Q5 — TEXT_SVG_LINES

Accepted one absolute-positioned tspan per split item, including an empty tspan, only for LF-bearing text (`CaptureViewport.tsx:333`). At `(10,20)`, size 16, AC-102.11 asserts x=10 and baselines 38/60/82; the one-line case asserts zero tspans and the original text child. Shared plate geometry drives the selection outline and handles, and re-edit retains the whole string. Nothing introduces wrapping. No collapsed empty slot or changed one-line SVG was found.

## Q6 — TEXT_DRAFT_KEYS and TEXT_DRAFT_HINT

Accepted the handler and its behavioral tests: unshifted Enter prevents default and commits; Shift+Enter leaves insertion to the textarea; composing Enter returns before commit; Escape cancels (`CaptureViewport.tsx:1543,1562`; AC-102.12 through .16). Ctrl+Enter and Alt+Enter also commit when Shift is absent, consistent with the approved rule and previous Enter behavior; no separate modifier behavior was required. Key behavior was audited against the existing tests/receipts, not replayed through a prohibited runner during review.

Rows follow the split line count, at least one, with `wrap="off"`. The exact editing-only hint has `pointer-events-none` and is named by `aria-describedby`. Editable-target/zoom/editor guards already recognize textarea, preserving native paste/copy/undo and preventing canvas shortcuts from taking the draft. AC-102.18 checks saved multiline re-edit; unchanged `draftCommits` rejects whitespace-only drafts while storing a nonempty draft verbatim (`CapturePage.tsx:268,2463`). No new keyboard interception or line loss was found.

## Q7 — TEXT_FIXTURE_MULTILINE and TEXT_PARITY_E2E

Accepted the real-bake producer and exclusive flag (`tools/capture_bake_fixture.py:47,76,351`). Regeneration under the review temp directory produced the 240×160 white original and annotated image equal to both repository PNGs, including encoded bytes. Decoded-pixel comparison in Departure 3 still proves the visual contract; the independent byte comparison additionally passed. Existing default/region tests remain unchanged prefixes and passed in the matching gate.

The seam's default remains the original pair and mark; the multiline argument carries its pair and its mark together (`capture-inbox.test.ts:2130`). AC-102.19 requires two ink runs and compares every run endpoint, ink bounds and plate bounds within 1 px. A collapsed line fails its run count (as the Red receipt demonstrates); wrong second-line pitch fails the endpoint comparisons. Gate preview and bake runs both read 28–51 and 106–129, with plate edges differing by at most 1 px. AC-82.6 remains unchanged and AC-102.20 checks the default pair. Departure 5 hid nothing: both named tests actually ran in the broad filter, and .20 also ran alone.

## Q8 — TEXT_MCP_DOC

Accepted the appended sentence with literal backslash-letter sequences (`mcp-server/src/toolsets/capture.ts:101`). AC-102.21 checks the complete sentence/suffix, no real LF in its expected sentence, absence of `circle`/`marker`, the exact capture action list, and schema acceptance of multiline text (`mcp-server/tests/capture.test.ts:1658`). AC-59.16 is unchanged. The diff changes no MCP action, schema or audit baseline. No client-contract change beyond documented CR normalization was found.

## Q9 — Tests, pins and IR-5

Accepted all AC-102.1 through .24 mappings. The independent `red-check.py` run read all four receipts and reported **16 required tests, 0 problems**; the required blocks are assertion failures, not setup/import failures. The inspected tests discriminate normalization after length checking, wrong pitch, rounded/clamped per-line unions, Shift+Enter commit, IME commit, and tspans added to one-line marks.

Departure 1 is a disclosed Green-stage test edit, but its replacement assertion remains as strong as AC-102.12: the test first requires one two-line mark, then exactly two marks whose contents are exactly `Hi` and `Hi\nHi`, independent of painting order (`capture-text-lines.behavior.test.ts:351`). It does not excuse missing/extra marks. Departure 4 accurately distinguishes CRLF-without-plate cases already equal at Red from failing lone-CR/plate cases. No existing pin moved; the existing fixture and MCP tests are unchanged prefixes, and AC-82.6's assertions remain intact.

| Test file / reviewed delta | IR-5 rating | Basis |
|---|---|---|
| `tests/unit/test_capture_text_lines.py` | Strong | Exact stored values, accepted/refused length boundary, bake comparisons, independent Pillow fixture values, crop keep/drop |
| `tests/e2e/test_api_capture_text_lines.py` | Strong | Real isolated API stack, fixed refusal, sidecar contents, delegating constructor trace, actual baked output |
| `ui/tests/unit/capture-text-lines.behavior.test.ts` | Strong overall | Real page events/POSTs, exact SVG/key/hint/re-edit/selection expectations; union oracle is supported by independently generated Pillow anchors |
| `tests/unit/test_capture_bake_fixture.py` additions | Strong | White image, committed pixel equality, one-line negative control, exclusive output sets |
| `mcp-server/tests/capture.test.ts` addition | Strong | Exact documentation sentence and action list, schema parse |
| `ui/tests/e2e/capture-inbox.test.ts` changed seam/new tests | Strong | Real Electron screenshots, independent bake PNG, per-line count/endpoints and bounds; old oracle retained |

Small constant/signature guards are adequate for their type-only AC. No weak test was found that permits a demonstrated material product defect to pass.

## Q10 — Freshness, identity and records

Accepted the fresh full gate. Both gate identities and independent recomputations equal:

`4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95`

`ELECTRON_RUN_AS_NODE` was unset. To reproduce the documented user-ignore effect without opening the secret, the reviewer added a process-only `core.excludesFile` pointing to a temp file containing only `.claude/settings.local.json`, preserving the sandbox's two safe-directory settings. No repository/user Git configuration was changed.

All 21 executed gate steps record exit 0, their receipts exist, and the last line is exactly `session-gate: all steps exit 0`. The nine evidence.v1 records agree with the inspected decisive receipt outputs; 21 named row-level receipts also corroborate the disclosed first-run failures and final passes. No baseline failure exemption was used.

| Suite | Baseline | Final | Delta |
|---|---:|---:|---:|
| Python | 2459 | 2480 | 21 |
| UI | 1322 / 123 files | 1333 / 124 files | 11 / 1 file |
| MCP | 527 | 528 | 1 |
| Electron | 47 | 49 | 2 |

The independently hashed AC-51.6 prefix is unchanged: `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`. All 18 modified text files have the handoff's stated line-ending conventions. Earlier geometry JSON values are unchanged. Comparing the four pre-status copies proves only MEU-102's YAML block, its registry row, BUILD_PLAN's derived total and grouping row 46 changed; P2/P3 remain as instructed. The Delivered note matches delivered behavior. The B-4 disclosure accurately states the supplied plan-time departure; it was not re-investigated. Pending review/H2 state is intentional and is not missing execution behavior.

## Q11 — Safety

Accepted the new tests/probes' synthetic inputs and isolation. Python API tests use function-local temporary inbox/database paths; UI unit fetch/IPC collaborators are fakes; Electron uses temporary `AVKIT_APP_DATA`, E2E mode and fixture fetch seams. New parity tests never invoke clipboard IPC. No added path reads a user's inbox or sends a YouTube/network request. Error responses discard refused values; new production code logs no mark text. New Electron logs contain numerical boxes only. Existing adapter fixture-path logs refer to synthetic generated files, within the expressly accepted S6 distinction.

Review Python writes, images, cache and TMP/TEMP were under `C:/Temp/av-kit`; bytecode was disabled and uv was offline with `--no-sync`. Initial review-command environment/CLI failures were corrected (uv cache access, preserving sandbox Git settings, and supplying OpenAPI's required check path); the successful probe/check exits cited below are actual final runs. No product defect is inferred from those review setup errors. No safety finding was found within this delta.

## Checklist Results

Manual observations below were performed by `codex-independent-reviewer`; they do not claim new suite execution.

| Check | Result | Procedure / command | Exit | Evidence |
|---|---|---|---|---|
| IR-1 Live runtime evidence | pass | Inspect matching-state API integration tests and full-gate/Electron receipts | null | Real API stack; Electron .19/.20/AC-82.6 passed; identity independently matches |
| IR-2 Stub behavioral compliance | pass | Trace recorded UI save state and delegating API constructor | null | Saved marks feed GET detail; no domain/bake assertion mocked away |
| IR-3 Error mapping | pass | Inspect text schema, fixed error handler and AC-102.5 | null | No new route/error mapping; malformed text remains fixed-envelope 422 |
| IR-4 Generalization | pass | Trace annotate/render/sidecar/crop/export and shared geometry callers | null | Folding and multiline plate propagate through canonical shared functions |
| IR-5 Test rigor | pass | Audit every new/changed test against AC .1–.24 and required Red receipts | null | Ratings and mutation discrimination above; no demonstrated material false-pass |
| IR-6 Boundary validation | pass | Inspect Pydantic before-validator, domain checks, existing MCP schema, API negatives | null | Normalized length rule, invalid-type refusal, no new schema/action |
| IR-7 Coverage/deferrals | pass | Compare all 24 ACs, handoff evidence, supplied exclusions and task phase state | null | No required feature silently deferred; later H2 deliberately pending |
| AV-1 through AV-6 | pass | Inspect Red/Green, unchanged assertions/pins, implementations and sourced contracts | null | Required failing-then-passing evidence; no skipped masking, bypass or unfinished product stub |
| Independent behavior probes | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s70-review-probe.py` | 0 | Boundary folding, 17 pitches, 16 plates, eight bake variants, fixture bytes, 117 matrix cases, 40 spacing comparisons, EOL/hash/state |
| Independent receipt audit | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s70-review-audit.py` | 0 | Full-gate exits/counts, nine records, row outputs, unchanged pins, pre-status scope |
| Independent Red attribution | pass | `red-check.py` with the 16 task-row-3 `--require` ids and four named receipts | 0 | 4 receipts, 16 required tests, 0 problems |
| Independent identity | pass | `rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-13-capture-text-multiline/identity.py --state-only` | 0 | Exact gate-state equality with documented ignore reconciliation |
| OpenAPI | pass | `rtk proxy uv run --no-sync python -B tools/export_openapi.py --check openapi.committed.json` | 0 | Empty successful check output; snapshot absent from delta |
| Registry render | pass | `rtk proxy uv run --no-sync python -B tools/meu_status.py render --check` | 0 | 142 MEUs / 12 phases; rendered regions match |
| New full-suite/build execution during review | n/a | Prohibited by reviewer scope; matching fresh evidence reused | null | No runner/build/gate rerun |

### Durable reviewer evidence

The command environment set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`, `UV_OFFLINE=true`, `UV_CACHE_DIR=C:/Temp/av-kit/s70/exec-review-tmp/uv-cache`, TMP/TEMP to `C:/Temp/av-kit/s70/exec-review-tmp`, and `RECEIPTS_DIR=C:/Temp/av-kit`. Identity/probe commands unset `ELECTRON_RUN_AS_NODE` and appended the one-path exclude through process-only Git configuration. Shell streams were redirected, child exits saved immediately, and completed receipts read. The embedded output below carries the decisive evidence independently of scratch receipt retention.

```json
{"schema_version":"evidence.v1","check_id":"s70-exec-independent-probes","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s70-review-probe.py","cwd":"P:/av-kit","scope":"synthetic domain/API/Pillow probes, fixture regeneration, geometry matrix, EOL/hash and current identity","phase":"targeted","exit_code":0,"result":"pass","tested_state":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","output":"6 mixed/control cases domain+API; idempotence; pre-length fold 250/251; invalid types/empty and API surrogate refusal pass. 17 pitches and 16 exact plates match Pillow. 8 CRLF/CR bakes equal LF PNG bytes at 16/32, plain/plate. Both multiline fixtures match repository PNG bytes and pixels; original white RGB 240x160. 117 matrix comparisons add no drift over one-line tolerance (max 7px at large sizes). 40 old-default/new-explicit draws and boxes unchanged. Prefix hash 6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454. All 18 modified text EOL conventions match. Gate identity matches.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-exec-independent-receipt-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s70-review-audit.py","cwd":"P:/av-kit","scope":"named baseline/row/full-gate receipts, evidence records, prior pins and four pre-status copies","phase":"targeted","exit_code":0,"result":"pass","tested_state":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","output":"21 observed gate exits 0; receipts exist; exact success last line. Python 2459->2480; UI 1322->1333 (124 final files); MCP 527->528; Electron 47->49. Nine evidence records and 21 named row receipts agree on decisive outputs and disclosed failures. Existing fixture/MCP test and test-id prefixes unchanged. Earlier geometry values unchanged. Pre-status comparison: MEU-102 YAML only, registry row only, BUILD_PLAN total only, grouping row 46 only; P2/P3 preserved. Both AC-82.6 and AC-102.20 ran in the broad guard filter.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-exec-independent-red","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-13-capture-text-multiline/red-check.py --require test_ac_102_2 --require test_ac_102_4 --require test_ac_102_5 --require test_ac_102_6 --require test_ac_102_17 --require AC-102.9 --require AC-102.10 --require AC-102.11 --require AC-102.12 --require AC-102.13 --require AC-102.15 --require AC-102.16 --require AC-102.18 --require AC-102.24 --require AC-102.21 --require AC-102.19 C:/Temp/av-kit/s70-py-red.txt C:/Temp/av-kit/s70-ui-red.txt C:/Temp/av-kit/s70-mcp-red.txt C:/Temp/av-kit/s70-e2e-red.txt","cwd":"P:/av-kit","scope":"all task row 3 required Red ids and their recorded child exits","phase":"targeted","exit_code":0,"result":"pass","tested_state":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","output":"red-check: 4 receipt(s), 16 required test(s), 0 problem(s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-exec-independent-identity","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-13-capture-text-multiline/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 inputs with ELECTRON_RUN_AS_NODE unset and the documented one-path ignore restored in process only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","output":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-exec-independent-openapi","command":"rtk proxy uv run --no-sync python -B tools/export_openapi.py --check openapi.committed.json","cwd":"P:/av-kit","scope":"current schema matches unchanged committed OpenAPI document","phase":"targeted","exit_code":0,"result":"pass","tested_state":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","output":"Command completed with exit 0 and empty stdout/stderr.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s70-exec-independent-state-render","command":"rtk proxy uv run --no-sync python -B tools/meu_status.py render --check","cwd":"P:/av-kit","scope":"current registry and BUILD_PLAN rendered regions","phase":"targeted","exit_code":0,"result":"pass","tested_state":"4e35af91ac242514b8994c286a49b37a8f1cb2ce+c6cdff919178329bf884e4d2f56623aabe00cc09726a21834135b329f90d2b95","output":"Drift check passed — SSOT loaded (142 MEUs, 12 phases), rendered regions match on-disk content","fresh":true}
```

## Verdict

`approved` — intent achieved, with zero findings. Implementation, real behavioral oracles and independently matched fresh-gate evidence support the requested multiline slice. No High/Critical finding requires corrections.

Residual limits are the accepted existing one-line metric approximation and the disclosed unrelated AC-100.11 timing flake, which passed its three isolated reruns and both later full Electron runs. This review reuses the matching fresh full gate rather than claiming to have rerun it. No open product question remains for this loop.

## Follow-up Actions

- Coordinator validates and copies this report byte for byte to the canonical rolling implementation-review path and records this round-1 verdict in the existing loop.
- Coordinator continues the authorized H2 rows and preserves Mat's separate commit/push gate. This review performs neither those actions nor a correction phase.
