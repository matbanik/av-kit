---
date: "2026-11-08"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-07-convert-extract-index/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s54-execution-2026-11-07-convert-extract-index"
round: 1
---

# Critical Review: 2026-11-07-convert-extract-index

> **Review Mode:** execution · **Verdict:** approved · **Intent achieved:** yes

## Scope

Independent Codex review of Claude Code's MEU-123 work, working tree against HEAD `39ac742`. Reviewed the correlated plan, task, MEU-123 handoff, product/test/CI changes, saved receipts, and the D-379/D-380 filing and placement hunks. Session 53's unrelated edits and H2 closeout are excluded as instructed. No repository file was edited; probes, databases, generated media, outputs and this report are under `C:/Temp/av-kit`. No network request, product test runner, application launch or session gate was run by this reviewer.

**Intent anchor:** Session 54 gives `stream_index` one meaning, the Nth audio stream in ffprobe order, which is the N that FFmpeg's `-map a:N` selects. The service then picks an Extract's extension from that audio stream, plans All audio streams as positions 0 to k-1, and creates no job that asks for a track the file doesn't have. An Extract job saves no encoder. Proof is a real `.mp4` with one audio track and with two, through the real FFmpeg adapter.

## Findings

No findings. No Critical or High defect, material false-pass, or unfulfilled in-scope acceptance criterion was demonstrated.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|

## Review Questions

### Q1 — Done and the complete extraction path

**Accepted.** `adapter.py:445-485` returns video 0, AAC audio 1 and AC-3 audio 2 for the generated two-track MP4. `conversion.py:93-102` selects audio in index order; `:345-349` plans positions 0 and 1; `:402-409` selects AAC → `.m4a` and AC-3 → `.ac3`; `:279-335` creates and reserves the jobs; `:572-578` forwards those positions to `ExtractOptions`; `adapter.py:630-635` copies exactly `a:0` or `a:1` without video/subtitles. First mode gives position 0 and `_a.m4a`; All gives `_a0.m4a` and `_a1.ac3`, including the first track exactly once. Independent real-service/SQLite/FFmpeg probes verified both modes on one- and two-track files, terminal Done states, null encoders and output stream contents.

`PASS_THROUGH` holds: API schema `schemas/conversions.py:52`, request mapping `routes/conversions.py:145`, response `:81`, MCP `convert.ts:76`, GUI body `convert-body.ts:118` and queue metadata `convert-controls.ts:209` carry the number unchanged. ConvertPage passes the stored position and encoder at `:544-552`; a null encoder is omitted at `convert-controls.ts:229-234`. Current labels/help and the changed 08 contract describe audio selection consistently. The residual's historical diagnosis at `08-video-conversion.md:597` is explicitly preserved history, followed by the Delivered note. **Not accepted:** none.

### Q2 — AUDIO_POSITION, AUDIO_PLAN and EXTRACT_EXT

**Accepted.** The real probe produces validated `StreamInfo` entries whose indices are FFmpeg's global stream order. Filtering and sorting them gives the audio-only order that `a:N` counts. `None` is returned only for absent probe information or `streams=None`; an empty known list stays empty. An independent synthetic probe also verified gapped, out-of-order global indices and the distinction between absent and empty lists.

One-plan All mode retains `_a`; multiple plans use `_a0`, `_a1`, etc. Output reservation/collision logic at `conversion.py:364-388` remains applicable. The independent real-stack probe verified duplicate multi-plan inputs produce separate `_1` suffixes and that existing outputs become Skipped with `skip_existing=True`. The fallback to `audio_codec` applies only at unknown position 0; unknown position 1 and a known empty list give `.mka`. This matches the real adapter's first-audio fallback and the existing fake's `streams=None`. **Not accepted:** none.

### Q3 — MISSING_TRACK and retry

**Accepted.** `conversion.py:105-112,282-297,326` produces the two specified messages and Failed status at add. Failed rows retain an output reservation and are returned as normal created items; the API's `:149-157` serializes their status/error, so the existing GUI/MCP readers can display them. `_next_pending` at `:466-473` excludes them, preventing extraction on initial processing.

Independent real-stack probes verified both no-audio modes create no output and call no extraction, and a batch selecting position 1 from a one-track and a two-track file keeps the first Failed while extracting the second as AC-3. `reset_failed` delegates to `ConversionJob.reset_failed` (`domain/conversion.py:328-337`), clears the error/progress and requeues without reprobe. The probe confirmed retry calls FFmpeg and fails with `ffmpeg exited 4294967274`, as explicitly accepted at plan `:104`. This does not migrate or repair the stored plan. **Not accepted:** none.

### Q4 — EXTRACT_NO_ENCODER and LEGACY_JOBS

**Accepted.** `conversion.py:507-516` bypasses both GPU detection and encoder resolution only for Extract, saves None and leaves the cached `_gpu` alone. Compress/Cut still resolve as before; later jobs can populate an empty cache normally. The real-stack probe recorded zero GPU calls across extraction cases. AC-123.6 covers NVIDIA and unavailable software encoders, AC-123.7 proves a retried stored position 1 stays 1 while clearing its old label, and AC-123.8 preserves both Compress encoder choices.

The Compress guard at `:535-536` is sound: the preceding non-Extract branch returns a validated string from `_resolve_encoder` or raises, so normal Compress execution cannot reach it with None. An independent AST scan found **zero asserts** in `packages/core/src`. Saved run 1 genuinely failed AC-4.12 and marked later stages not_run; run 2 and the rerun targeted receipts pass after the guard fix. Existing Done labels and old stored positions remain under the accepted LEGACY_JOBS limit. Cut's label remains filed under D-373. **Not accepted:** none.

### Q5 — Tests, Red and CI_DESELECT

The saved child Red exit is **1**: **16 failed, 4 passed, 24 deselected**. Independently loading the receipt reader and taking the 16 required names from task.md confirmed every required block failed by assertion alone. The actual diagnostics match the current expected filenames, positions, errors and encoders; no collection/import failure substitutes for Red. The four passing cases are AC-123.8's two encoder guards, fixture guard .9 and Console guard .13.

| AC / cases | Grade | Assessment |
|---|---|---|
| AC-123.1 | Strong | Exact AAC name, position and dispatched options. |
| AC-123.2 | Strong | Exact ordered positions/names and both dispatched positions. |
| AC-123.3 | Strong | Exact one-track All name and position. |
| AC-123.4, three cases | Strong | Exact add-time failures, persisted Failed status and zero encoding. |
| AC-123.5 | Strong | Explicit unknown-stream fixture and exact 0/1 extension/status contrast. |
| AC-123.6, both cases | Strong | Done/null label/no GPU call and success without software encoders. |
| AC-123.7 | Strong | Seeded old position/encoder, actual retry, dispatched options and cleared label. |
| AC-123.8, both cases | Strong | Saved encoder, Done state and encode option agree. |
| AC-123.9 | Strong | Real binary resolution and exact video-first fixture stream lists. An audio-first fixture cannot satisfy it. |
| AC-123.10, both files | Strong | Real persisted lifecycle, exact name/position, null encoder and output AAC-only stream. |
| AC-123.11, both files | Strong | Both real tracks, ordered positions, correct containers/codecs and Done/null states. |
| AC-123.12, both modes | Strong | Real no-audio file; subclass counts calls to the dispatched extract_stream, with no output or processing. |
| AC-123.13 | Strong | Actual stdout/stderr/ring/file marker predicates plus engine.created/convert.finished positive controls. |

`CountingAdapter` increments before calling the real superclass (`test_extract_real_ffmpeg.py:73-75`), so .12 measures the intended dispatch rather than a fake encode proxy. `ci-collect.py:26-59` reads the python job's actual Tests argv, removes exactly the new deselect for its control, and collects offline. Its two receipts show **1199 / 0 module tests** versus **1207 / 8 module tests**; `.github/workflows/ci.yml:65` targets only this module. This is the accepted fetched-binary CI limit, not a skip hiding local failures.

The existing service-test prefix and API/MCP/UI guard files are unchanged against HEAD. AC-30.1, .11-.13, AC-112.1-.4, API AC-31.21 and AC-45.17 are covered by the matching saved passing suites. `ui/tests/e2e/test-ids.ts` is unchanged for AC-51.6/AC-81.13. No in-scope material behavior that false-passes these checks was demonstrated. **Not accepted:** none.

### Q6 — NO_RAW_CONSOLE

**Accepted.** The delta adds no log call. The missing-track errors and Compress guard contain no path, filename or codec. `convert.extract` supplies an integer. The raw argv attached to finished/cancelled events is removed by `HealthService._process` before rendering (`health.py:207-235`); FFmpeg stdout is discarded, stderr is consumed for progress, and encode failure text contains only the exit number (`adapter.py:282-286,369-374`). Probe-failure error storage is pre-existing and is not a new logging path.

AC-123.13 searches the unique fixture-folder marker and multiple representations of pytest's base path across all four surfaces. The independent probe reproduced successful extraction and missing-track retry with no marker/base leakage, verified engine.created/convert.finished were captured, then injected a marker event and detected it in stdout, ring and console.log. Thus the surface predicates are live. No additional raw-value leak from this delta was demonstrated. The production pre-HealthService startup line remains the already accepted D-377/D-379 issue. **Not accepted:** none.

### Q7 — Evidence, freshness and delivered claims

**Accepted.** Recomputed state:

`39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae`

This exactly matches the handoff and both gate identities. `ELECTRON_RUN_AS_NODE` was unset. To avoid reading the forbidden settings file while reproducing the host's exclusion, this reviewer supplied a temporary `core.excludesFile` containing only `.claude/settings.local.json`; `safe.directory=P:/av-kit` was also supplied process-locally. The first uv invocation hit the sandbox's inaccessible home cache; successful probes used a temporary UV_CACHE_DIR, offline mode and `--no-sync` with the existing environment. No dependency or repository configuration changed.

Read and compared the handoff's eight evidence.v1 records to their baseline/Red/Green/CI/register/full/render/OpenAPI receipts. Gate run 2 records all steps exit 0: **1338 Python, 1174 UI, 470 MCP, 8 standalone real-FFmpeg and 23 Electron tests passed**; those suites were not rerun by this reviewer. The evidence reader accepts the current state and refuses a deliberately wrong state. Run 1's failure, fail-fast record and row 2's two passing runs are consistent with the disclosed correction. The identity-selftest folder fix and ci-collect's python-job selection are sound; current Red assertions agree with the saved diagnostics.

Independent parsing of `s54/register-before-resolve.yaml` against the current register found exactly **10 differences**, all under status, verification or resolution_path of the two resolved issues, matching `s54-resolve.txt:6-16`. Current register SHA-256 matches the recorded after hash. The 08 spec edits and Delivered citations at `:176-177,468,476,607-612` accurately describe the source; status/render changes say ready_for_review rather than independent approval. **Not accepted:** none.

### Q8 — Plan-time filings and Session 55 discovery

**Accepted.** Reviewed the six-path diff against `39ac742`, including the plan-time changes captured by baseline-dirty.txt. `CONVERT-CUT-ENCODER-LABEL` is **open/P4** at `known-issues.yaml:4309`; `CONSOLE-STARTUP-DB-PATH` is **open/P3** at `:4366`, and both appear in the generated Markdown. Cut's historical service cite is pinned to HEAD and matches the unchanged adapter's copy/libx265 behavior (`adapter.py:590-604`). The startup description matches `engine.py:85`, wiring's engine-before-HealthService order (`wiring.py:135,205`) and the host-forwarding path.

The startup issue is discoverable as a MEU-124 / Session 55 rider in the grouping (`:27,51,200`), the MEU note (`meu-status.yaml:3263`), and 06's residual (`06-gui.md:1586,1595`). Its required Red explicitly builds services under a marker folder and rejects stdout containing that marker, which catches the current unsanitized path. D-380 places Cut last in current-focus's debt queue (`:62`) and names it in the grouping (`:61`). Session 55's planner has the issue, code references, intended behavior and regression trigger. **Not accepted:** none.

## Checklist Results

| Check | Result | Observation | Exit | Evidence |
|---|---|---|---|---|
| IR-1, IR-2, IR-4: runtime, collaborators, generalization | pass | Independent real-adapter probe and source trace | 0 | Both extraction modes, actual SQLite persistence/output probes, mixed batch, retries and collision/skip paths pass. |
| IR-3, IR-6: error mapping and boundaries | pass | Manual review by codex-independent-reviewer of unchanged API/MCP/UI schemas and error/status propagation | null | Failed-at-add remains a created queue row; strict schemas and nonnegative wire positions retained. |
| IR-5, AV-1 to AV-5: test rigor and bypass checks | pass | Receipt parser, source/test diff, AST scan and independent probes | 0 | 16 assertion-only Red failures; no test masking, no core asserts, no material false-pass demonstrated. |
| IR-7: AC coverage and accepted deferrals | pass | Manual plan/handoff/source/register comparison by codex-independent-reviewer | null | All 13 ACs accounted for; D-373/D-377 limits and their scheduled/debt placements match Mat's rulings. H2 remains after review. |
| DR: claims, citations and evidence freshness | pass | Independent identity and evidence/register audit | 0 | Exact state match; wrong-state control refused; 10 permitted register-field changes; matching saved gate totals. |

### Commands and durable reviewer evidence

All Python probes used `PYTHONDONTWRITEBYTECODE=1`, offline uv, a temporary UV_CACHE_DIR and `python -B`. Media/DB probes used TMP/TEMP `C:/Temp/av-kit/s54/review-tmp`. Shell streams were redirected to completed receipts and their exits preserved. The temporary helpers remain available beside this report for audit.

```json
{"schema_version":"evidence.v1","check_id":"s54-review-real","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s54_review_probe.py","cwd":"P:/av-kit","scope":"independent local real FFmpeg/SQLite extraction, missing tracks, retry, batch, names, Console and core-assert scan","phase":"targeted","exit_code":0,"result":"pass","tested_state":"39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae","output":"one/two-track First: a:0 AAC .m4a Done/null; two-track All: a:0 .m4a AAC and a:1 .ac3 AC-3 Done/null; no-audio First/All Failed without extraction/output; retry fails ffmpeg exited 4294967274; mixed batch Failed/Done; collision suffixes and skip_existing pass; GPU calls 0; no marker/base in stdout/stderr/ring/file; injected marker detected; core asserts 0"}
```

```json
{"schema_version":"evidence.v1","check_id":"s54-review-state","command":"rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-07-convert-extract-index/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 input identity with ELECTRON_RUN_AS_NODE unset and process-local git exclusions/safe.directory described in Q7","phase":"static","exit_code":0,"result":"pass","tested_state":"39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae","output":"39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae"}
```

```json
{"schema_version":"evidence.v1","check_id":"s54-review-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s54_review_audit.py","cwd":"P:/av-kit","scope":"independent register differences, unchanged contract/guard files and saved receipt comparison","phase":"static","exit_code":0,"result":"pass","tested_state":"39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae","output":"REGISTER independent parsed differences 10, only the two issues' resolution_path/status/verification fields; after SHA matches; both plan-time issues open at P4/P3; pass-through/guard/test-id files unchanged; existing service tests unchanged prefix; saved full counts 1338/1174/470/8/23; audit: PASS"}
```

```json
{"schema_version":"evidence.v1","check_id":"s54-review-checks","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/s54_review_checks.py","cwd":"P:/av-kit","scope":"saved Red parser, current-state evidence acceptance/refusal control and adversarial audio-helper inputs","phase":"targeted","exit_code":0,"result":"pass","tested_state":"39ac742d123aa12bcad849f60008818ede359a61+f67b517a559fc07414ffec531ac782498aec7e81a91130308978619ed40a22ae","output":"16 required failures assertion-only, child exit 1; current full-evidence state accepted and deliberately wrong state refused; gapped/out-of-order indices sorted; None/empty distinguished; fallback restricted to position 0; checks: PASS"}
```

## Verdict

**approved** — intent achieved. No corrections required for this review round. Approval covers MEU-123 and the requested filing/placement work; the coordinator still owns ledger collection and the authorized H2 closeout. Existing-job nonmigration, retry behavior, Cut's label and the filed startup line remain the accepted limits, not new findings.

Report validation: `validate_closeout_artifacts.py --review-state-only` accepted execution/round 1/approved with zero open findings. The verdict JSON passed `review-verdict.schema.v2.json`; goal-anchor and home-path redaction checks passed. Completion-preflight rechecked the canonical task: remaining review collection/H2 rows belong to the coordinator and are not claimed complete here.

🕐 Completed: 2026-11-08 00:32 (EST)
