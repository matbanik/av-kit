---
date: "2026-11-19"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-19-e2e-host-parity/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ehp-execution-2026-11-19-e2e-host-parity"
round: 1
tested_state: "2c41c70a50863f013988e2a153fdef9c1f19032e+bad49170b39ee7e725fd7637cf5bfb951c950c7038b9bd359ff8e49461bba881"
---

# Critical Review: 2026-11-19-e2e-host-parity

> **Review Mode:** execution
> **Verdict:** approved
> **Intent achieved:** yes. No findings.

## Scope

Independent Codex review of Anthropic-authored Session 97, MEU-161, execution round 1. Reviewed the delta from baseline `2c41c70a50863f013988e2a153fdef9c1f19032e` in the plan's Files Modified paths, the plan/task, implementation handoff, relevant bake/consumer code, plan-local scripts and baseline data, and the specifically cited diagnosis, Red/Green, gate and real-host receipts. Applied IR, DR and AV checks against AC-161.1–AC-161.15. Approved plan decisions D-1241–D-1255 and coordinator decisions D-1256–D-1259 are accepted as instructed; their implementation and assertion strength were checked.

**Intent anchor:** the full Electron E2E suite passes on the second Windows host (the mini-air) through `tools/e2e_remote.py run <commit>` at this session's final tree, with 232 tests, 232 expected, the two clipboard specs skipped by their tracked `skip` entries, and `tools/e2e_host/known-failures.json` holding no `known` entry; the four entries it holds now are shown passing in that run's `known_now_passing`. Two causes are fixed, each after a receipt names the side that moves with numbers from both hosts, and each with its own Red: 1. **The capture text plate.** The preview's text plate (`textBackgroundBox` in `ui/src/renderer/src/features/capture/capture-text-metrics.ts`) is 2 px narrower on the right than the plate the bake paints. The bake is the reference (D-1242): `adapter.text_plate_box` returns Pillow's inclusive `(l, t, r, b)` and `_apply_text` fills `draw.rectangle` over it, so the painted plate is `r - l + 1` wide; the preview drops that pixel and scales a 16 px glyph table linearly, where FreeType rounds each size's extents and advances itself. The preview now computes the box from a Segoe UI glyph and kerning table in font units with FreeType's 26.6 rounding and Pillow's basic-layout kerning (D-1243, `PLATE_UNITS`) and returns the painted rectangle (`PREVIEW_FOLLOWS_BAKE`). A Pillow fixture of 2,488 painted boxes pins it; the measured residual (1,702 of 2,448 breadth cases exact, 5 more than 1 px off on a side, worst 2) is pinned as a threshold and registered as a low issue (D-1244). The three fidelity specs run at a device scale of 1 on every host (`FIDELITY_FRAME`, D-1245), so the dev PC, at a scale of 2, measures what the mini-air measures. 2. **The hover colour.** The mini-air has no pointing device, so Chromium reports `hover: none`, and Tailwind v4 puts every `hover:` style inside `@media (hover: hover)`; `settings.test.ts` AC-126.8 hovers a button and waits for a colour that cannot apply there. The spec now launches with a Blink setting that states a mouse-capable device (`HOVER_CAPABLE`, D-1246), checks that the media query matches before it hovers, and no other spec changes.

**Tested state:** `2c41c70a50863f013988e2a153fdef9c1f19032e+bad49170b39ee7e725fd7637cf5bfb951c950c7038b9bd359ff8e49461bba881`. Independently obtained twice with the plan's `identity.py --state-only`, ELECTRON_RUN_AS_NODE unset. It exactly equals the final H1 gate's before/after value. There is no identity difference from the sandbox's unavailable global Git ignore: identity.py explicitly excludes `.claude/settings.local.json`; that file was never opened. The repository verdict schema forbids additional properties and has no top-level `tested_state`; the returned JSON records it in summary/checklist evidence, and this report records it in frontmatter.

All reviewer writes are under `C:/Temp/av-kit`. No repository file was edited; no real host transport, network request, model, avkit MCP server, backend, app, build or GUI test was started. Real-host behavior is judged from existing receipts and copied reports. This approves the H1 deliverable; H2 closeout and committing remain coordinator work.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted every goal clause against the delivered state and evidence below. Did not treat a wrapper exit, the superseded run alone, or tests passing without state binding as proof.

| Clauses / AC | Accepted evidence and observation |
|---|---|
| Diagnosis before tracked changes; AC-161.1–2 | `ehp-diagnosis-1.txt:3` and `:8` identify both earlier host reports; `:17`–`:34` compare native scale 2 and scale 1 on the dev PC. Width 30 gives right gap 2 at three origins; width 32 gives four zero gaps. Hover-none gives `rgb(21, 94, 117)`, capable gives `rgb(22, 78, 99)` (`:43`–`:47`). Equal font hashes at `:49`–`:50`; row-0 differing paths `[]` at `:52`; moving-side conclusion at `:53`. |
| Registration before product code; AC-161.13 | Row-2 registration/status receipts establish MEU-161 at 9.46, initially pending, before row-3 Red and row-7 product Green. Current SSOT is ready_for_review, depending on MEU-82 and MEU-102. |
| Separate Reds; AC-161.3/5/8/9 | Row 1 reproduces the real hover assertion with hover-none; row 3 has the two static assertion failures; row 5 has three pixel assertions receiving 2 against <=1; row 6 has the absent-export and plate assertions. Reviewer reran red-check on rows 3, 5 and 6: all required failures attributed, zero problems. |
| Plate, oracle and residual; AC-161.3–7 | Generated table/fixture checks match; independent pytest checks all 2,488 fixture boxes against the local bake; delivered breadth reproduces exactly 1,702 exact, 5 over 1 px, worst 2. Residual is registered as low. |
| Frame and hover; AC-161.8–9 | Only the three fidelity specs receive scale 1; only AC-126.8 receives hover-capable flags, with a hard media-query assertion before hovering. Existing fidelity/colour assertions remain. |
| Final mini-air run; AC-161.10–11 | Snapshot 484d4ab binds all 14 session files. Its own report has 232 expected passes across 27 files, one attempt per test, no clipboard specs, zero plate gaps and empty overlap. All four former known tests are explicitly passing; see Q5. |
| Known list and records; AC-161.11–14 | Known is empty; label and both skip entries equal row 0. Both original issues resolved through recorded tool runs; residual added. Only grouping row 97 changes. |
| Dev-PC full suite and gate; AC-161.15 | The matching-state final gate has 31 successful steps; full Electron result is 232 passes, no failures/rejections/solo retries. See Q6. |

## Q2 — The plate

Accepted PREVIEW_FOLLOWS_BAKE and PLATE_UNITS. `capture-text-metrics.ts:55` implements signed FT_MulFix, `:61` rounds 26.6 values, `:66` models Pillow basic-layout kerning, and `:78` unions rounded glyph extents at the ascent/line-pitch positions. Empty lines contribute their point; empty text follows the approved space convention. At `:115`, the rectangle includes both painted edges. The reference remains unchanged: `adapter.py:223` measures the Pillow box and `:1124` fills its inclusive rectangle.

The generated module contains 95 glyphs and 372 kerning pairs. Reviewer `segoe-units.py --check` reproduces 10,335 bytes, SHA-256 prefix `f93720ecdc6cb72d`; `plate-fixture.py --check` reproduces 39,108 bytes, 2,488 boxes, prefix `36b15443d46282a6`. The fixture generator calls `adapter.text_plate_box`, never the TypeScript model. The independent guard confirms zero mismatches, then detects exactly one changed box in a scratch mutant.

The fixed limits were already specified before implementation; current measurements equal those limits without amendment. The four matrix differences remain individually pinned. Reviewer mutation probes reject dropping the inclusive width (2 exact, 113 over 1 px) and dropping kerning (1,472 exact, 27 over, worst 5). Additional empty/multiline/unknown-character inputs at nine sizes from 1 to 500 return finite, positive boxes in 63 cases.

All five consumer calls remain unchanged: CaptureViewport.tsx:406, capture-transform.ts:125/:141, capture-hit-test.ts:161/:177. The new rectangle feeds rendering, selection, handles and hit testing consistently. The named drag/point pins preserve their original premises; `capture-geometry.json` and the bake retain baseline bytes. The affected behavior/transform tests pass. No new behavior outside the intended rectangle change was established.

Did not interpret the finite-box unknown-glyph probe as proof of exact Unicode/font-fallback parity. Non-ASCII tables and parity beyond the approved residual are explicitly excluded and tracked by D-1244.

## Q3 — Frame and hover

Accepted FIDELITY_FRAME and HOVER_CAPABLE. `electron-app.ts:43` exposes optional args and `:136` appends them; default callers keep their existing arguments. `capture-inbox.test.ts:2248` and `:2311` cover exactly the three fidelity tests. Their image-pixel scans, <=1 comparisons, multiline row comparisons and preview-versus-bake checks at `:2230`, `:2287`, `:2361` and `:2384` remain unchanged. Row-5 Red shows the frame exposes the original right gap of 2, so it does not conceal that mismatch.

`settings.test.ts:728` uses an unconditional `expect(...matchMedia('(hover: hover)').matches...).toBe(true)`, followed by hover and the original colour assertion. There is no return/skip/fixme in that span. The AC-161.9 filter at `e2e-harness.test.ts:192` still catches the same substrings as the old includes-based filter; an independent 192-case equivalence probe passes. Its regex change and message rewrite do not change a matcher or expected result. Only the named capture/settings E2E files and shared launcher change; no other spec launch or assertion changes.

Did not accept a capability-dependent early exit as success: the scratch early-return mutant is refused by diff-check, and the delivered precondition is hard.

## Q4 — Test pins and assertion strength

Accepted PINS_NAMED and the implementations of D-1255, D-1257 and D-1259. All existing-test deltas were inspected against the pin table/decisions. `diff-check.py --expect-changed` passes, its 34-case selftest passes, and the independent early-return insertion fails with `unnamed line 729: '  return'`. Eleven current hashes equal the row-3b/5/6 records. The row-3 hash change is limited to the disclosed D-1257 lines; the old record is retained.

For D-1259, `tests/tooling/test_e2e_remote.py:1565` now asserts an empty known list. The skip tuples, reasons and KNOWN_FILE assertion remain. Executing the delivered test function on scratch JSON accepts the current list and rejects a restored known entry, removal of a skip entry and a changed skip label. The 181-test remote-tool suite also passes with fake transport. AC-43.13 and AC-44.13 themselves are unchanged; their retained sweep receipt shows 47 passes and the matching full gate includes them.

| Test surface | IR-5 grade | Basis |
|---|---|---|
| New plate Vitest tests and Pillow guard | Strong | Independent bake fixture, all four edges, exact fidelity marks, explicit matrix residuals, mutation rejection. |
| Metrics, multiline, viewport/page and transform pin changes | Strong | Concrete painted dimensions, retained selection/re-edit/scale assertions and fixed opposite anchors. |
| Three fidelity E2Es and AC-126.8 | Strong | Pixel/line comparisons and exact CSS values; reproducing Reds plus final real-host passes. |
| Harness source-read tests | Adequate | Concrete call counts, placement and hard-precondition checks, supported by real E2E evidence and diff/hash controls. |
| D-1259 tracked-list test / surrounding remote-tool tests | Strong | Exact known/skip values and tool path; negative mutants and 181 passing fake-transport tests. |

No changed assertion was found to weaken an existing product contract. Did not change a test, loosen a threshold or treat static reads alone as runtime evidence.

## Q5 — Snapshot and mini-air run

Accepted SNAPSHOT_NO_REF and KNOWN_EMPTY. Independent audit checks each of snapshot 484d4ab's 14 recorded blobs against both the current file's filtered Git hash and the snapshot object; all agree. Raw file SHA-256 values are saved in `exec-review/snapshot-bindings.json`. Both stored guards agree, current HEAD is the baseline on main, and current refs/index hashes still equal the snapshot guards. No ref contains the snapshot. Its author/committer match the required noreply identity. Snapshot source uses a temporary index, commit-tree, and GIT_OPTIONAL_LOCKS=0.

The copied run-10b report independently yields 232 tests, all expected, 27 files and one passed attempt per test. None is a clipboard spec. AC-82.6, AC-102.19 and AC-102.20 each log plate gaps `[0,0,0,0]`; AC-126.8 passes. Run summary exit is 0 and overlap is empty. All ten recorded tool/host-file hashes still match. The two snapshot trees differ only in `ui/tests/unit/e2e-harness.test.ts`, which the host's Electron suite does not execute.

D-1258 is honestly supported. Run 10's old-list summary exits 0 with the four known_now_passing entries. Run 10b's corresponding receipt also names all four, then correctly exits 32 because the current register has resolved their issues. That exit was disclosed, not converted to a successful host run. Additionally, reviewer offline summarize of run 10b, with its copied `host/specs.txt`, the row-0 known list and row-0 issue register, exits 0 with `specs_checked=True` and all four known_now_passing entries. This is a historical-register reclassification of an existing report, not another real-host run.

The two retained real runs are both green. The second is the disclosed S13 repeat after the unit-file change; neither report retries a failed test. Both run receipts record release, and no S10/S11/S12 bypass is evidenced. Did not contact the mini-air or substitute a new host observation for its receipts.

## Q6 — Tests, gate and records

Accepted AC-161.12–15 and the final fresh gate. The reviewer receipt audit compares the gate's step sequence directly with session-gate.ps1's declared sequence: all 31 steps have nonempty receipts and recorded exit 0, in order, at stamp `20261119-100429`. Both identities match the reviewer's current state.

| Final gate evidence | Observed result |
|---|---|
| ehp-D6-ui-tests.txt:10 | 146 files, 1,639 tests pass. |
| ehp-D6-py-tests.txt (also ehp-gate-h1.txt:124) | 3,301 pass, 37 warnings. |
| ehp-D6-canon.txt | 14 pass. |
| ehp-D6-e2e-touched.txt | 78 pass. |
| ehp-D6-e2e-full.txt:8 | 232 ok, 0 failures, 0 rejection lines; zero solo retries/registered hang excuses. |
| ehp-D6-remote-evidence.txt | Ten current hashes match; snapshot commit and 232/232 counts agree. |

Both earlier gates are retained. The first stops at ui-tests with exit 1 and later stages not_run; the second restarts at identity-before, stops at py-tests with exit 1 and later stages not_run. The final gate restarts from identity-before and completes. The corrections are the recorded D-1257 and D-1259 changes, followed by the required rerun, not suppressed failures.

Registration/resolution receipts agree with the actual deltas: MEU-161 is ready_for_review at matrix 9.46; row-11 tool receipts resolve only the named issues and add the low residual. Independent parsed comparison finds exactly those three issue records changed. Only grouping line 134 (row 97) changes. `issue_triage.py render --check` passes independently; the retained MEU render check reports 161 MEUs and matching generated regions. D-1256's revised hub check reflects the generator's actual output. H2 status approval/reflection/metrics/prompt are subsequent work, as the task requires; their present absence is not a review finding.

## Q7 — Safety and evidence fidelity

Accepted LOCAL_HOST_DETAILS within the permitted review boundary. The final gate's host-details scan reports `files=44 grown_pairs=3 bad=0`; the post-handoff scan reports `files=45 grown_pairs=0 bad=0`. Home-path checks are clean. The complete product/test deltas and plan/handoff text inspected contain no new host IP/account/root/task details. Reviewer did not open the local config, host-value files, secret-named files, SSH folder or real app data, and therefore did not independently compare against secret host values.

Independent eol-check covers 28 paths with zero problems, preserving the declared LF/CRLF conventions. The gate scope check has outside-scope `[]`, read-only mismatches `[]` and foreign-class changes `[]`. All 191 package/MCP/native baseline hashes still match; the unchanged bake and geometry are included in the read-only comparison. Current HEAD/refs/index and the no-ref snapshot checks give no evidence of a commit, stash, revert or branch/ref change. Historical snapshot status guards match before/after; later record/closeout additions are the planned changes.

No changed product path introduces network/model/data access. The unit runs use scratch roots and the remote-tool tests use fake ssh/scp. The handoff's decisive counts, state, Reds and deviations agree with the receipts and delivered tree. Did not claim that a read-only review can reconstruct every past process action or remote-host fact independently.

## Checklist Results

Commands ran with PYTHONDONTWRITEBYTECODE=1, TMP/TEMP under `C:/Temp/av-kit/e2e-host-parity/exec-review/tmp`, ELECTRON_RUN_AS_NODE unset, offline uv and a scratch UV_CACHE_DIR. Each shell receipt captures all streams and preserves the child exit before reading it.

| Check | Result | Command or observed procedure | Exit | Evidence |
|---|---|---|---|---|
| IR-1/4/5, AV-1/3; affected Python | pass | `rtk proxy uv run --no-sync python -B -m pytest tests/unit/test_capture_text_plates.py tests/tooling/test_e2e_remote.py -p no:cacheprovider --basetemp C:/Temp/av-kit/e2e-host-parity/exec-review/tmp/pytest` | 0 | 182 passed in 35.66 s; no skips. |
| IR-4/5, AV-2/3/4; affected UI | pass | From ui through pwsh: `rtk proxy npx --no-install vitest run --no-cache tests/unit/capture-text-plates.test.ts tests/unit/capture-text-metrics.test.ts tests/unit/capture-page.behavior.test.ts tests/unit/capture-text-lines.behavior.test.ts tests/unit/capture-transform.test.ts tests/unit/e2e-harness.test.ts` | 0 | 6 files, 168 tests pass. |
| Oracle/pins/EOL/Red integrity | pass | `rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/e2e-host-parity/exec-review/checks.ps1` | 0 | Both generators match; diff-check passes, 34 negative/selftest cases pass; EOL 28 paths/0 problems; required Reds pass; issue render clean. |
| Snapshot/report/records and adversarial mutants | pass | `rtk proxy uv run --no-sync python -B C:/Temp/av-kit/e2e-host-parity/exec-review/audit.py` | 0 | 14 blobs, 10 tool hashes and 191 unchanged backend/MCP/native hashes bind; final report 232/232 without retries; D-1259 and fixture mutants refused. |
| PLATE_UNITS, PREVIEW_FOLLOWS_BAKE, HOVER_CAPABLE probes | pass | `rtk proxy node C:/Temp/av-kit/e2e-host-parity/exec-review/plate-probe.cjs` | 0 | Original thresholds reproduced; two metric mutants refused; 63 edge cases finite/positive; 192 filter-equivalence cases pass. |
| Gate and tool provenance | pass | `rtk proxy python -B C:/Temp/av-kit/e2e-host-parity/exec-review/receipt-audit.py` | 0 | Two failed gates retained/fail-fast; final 31-step sequence complete; registration, triage and post-handoff scan receipts match. |
| Final-run former-known classification | pass | `rtk proxy uv run --no-sync python -B tools/e2e_remote.py summarize C:/Temp/av-kit/e2e-remote/r20261119T143010Z-484d4ab/host/report.json --label mini-air --known C:/Temp/av-kit/e2e-host-parity/baseline-copies/tools/e2e_host/known-failures.json --register C:/Temp/av-kit/e2e-host-parity/baseline-copies/.agent/context/known-issues.yaml --specs C:/Temp/av-kit/e2e-remote/r20261119T143010Z-484d4ab/host/specs.txt --out C:/Temp/av-kit/e2e-host-parity/exec-review/summarize-final-row0-verified` | 0 | 232/232, specs_checked=True, four known_now_passing, result ok. |
| Fresh state | pass | `rtk proxy uv run --no-sync python -B docs/execution/plans/2026-11-19-e2e-host-parity/identity.py --state-only` | 0 | Exact matching state before and after review checks. |
| DR-1/3/4/5/6/7/8; AV-5/6 | pass | Inspect baseline-relative code/test/record deltas, complete new modules/tests, consumers, plan contracts and named receipts; observer codex-independent-reviewer | null | Delivered claims agree with observed behavior/evidence; no hidden required gap or weakened assertion established. |
| IR-2/3/6 external write schemas and HTTP mapping | n/a | No route, MCP shape, persisted-input schema or product Python change | null | Outside the changed surface. |

```json
{"schema_version":"evidence.v1","check_id":"ehp-independent-execution-audit","command":"rtk proxy uv run --no-sync python -B C:/Temp/av-kit/e2e-host-parity/exec-review/audit.py","cwd":"P:/av-kit","scope":"Session 97 snapshot, copied final report, record deltas and negative probes","phase":"targeted","exit_code":0,"result":"pass","tested_state":"2c41c70a50863f013988e2a153fdef9c1f19032e+bad49170b39ee7e725fd7637cf5bfb951c950c7038b9bd359ff8e49461bba881","output":"14 snapshot files bound; 10 remote tool hashes bound; own report 232 expected of 232, 27 spec files, zero retries; three plate gaps zero; 191 unchanged package/MCP/native hashes; known-list, skip, early-return and fixture mutants refused; AUDIT PASS","fresh":true}
```

Reviewer setup failures were not counted as deliverable failures: uv initially refused its default cache (exit 2), then passed with a scratch cache; an offline summarize initially pointed at root specs.txt (exit 31), then passed using the tool's actual host/specs.txt. A scratch audit's incorrect hardcoded step count was replaced with comparison to the declared step sequence; the final audit passes. No product file was changed to address any reviewer setup issue.

## Verdict

`approved` — the delivered H1 work achieves the registered goal within the approved residual and font boundary. No High/Critical defect, weakened product test or materially false completion claim was established. No correction is required by this review. The coordinator may save this report unchanged to the canonical review path, record the verdict and continue the planned H2 closeout. This review performs no commit or push.

Residual risk remains the already approved and tracked CAPTURE-TEXT-PLATE-METRICS-RESIDUAL, including non-ASCII fallback/font-version limitations. It is not a new finding.

🕐 Completed: 2026-11-19 10:36 (EST)
