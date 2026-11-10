---
date: "2026-11-10"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s60-plan-canonical-2026-11-10-gui-capture-crop-tool"
round: 3
---

# Critical Review: 2026-11-10-gui-capture-crop-tool

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial.

## Intent Anchor

Session 60 adds a Crop tool to the Capture page. A Crop button opens a box over the whole image with 8 handles. The user drags a handle to resize, drags inside to move or drags outside to draw a new box; Shift keeps the ratio. Six aspect presets and a swap set the ratio, and X, Y, W and H fields set the box in original px. The outside is dimmed, a thirds grid shows while dragging, and the size reads out in original px. Enter, a double-click inside the box or Save as copy sends the box to Session 59's `POST /captures/{id}/crop`. The new shot is selected and named on the status line, and the source stays. Esc or Cancel leaves; Reset returns to the whole image. While the crop is open, other tools and keys do nothing, and Crop is disabled while marks are unsaved.

## Scope

Reviewed the working-tree implementation plan, task, d494-run.md, all named plan-local script surfaces, cited spec/design/grouping, MEU-131 by id, current renderer entrypoints and existing test guards, and Session 59's route/schema/service resolver and MCP advertisement. Claude Code/Anthropic authored the plan; this is independent Codex review. Plan-relative references below resolve under `docs/execution/plans/2026-11-10-gui-capture-crop-tool/`.

Accepted the supplied rulings, Session 59's approval, the grouping and split, open D-521/D-522, F2's environmental conflict and the token estimate. No option was selected for Mat. No product suite, baseline/gate, app, seed, harness or network was run. No prohibited secret file was opened. Reviewer writes are confined to `C:/Temp/av-kit`; Python bytecode was disabled. External research and the client-specific advertisement observation were assessed from local code and the supplied receipts.

## Findings

All three findings have High confidence. F1 is the approval blocker. F2 and F3 are non-blocking verification corrections; none concerns review paperwork.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `CROP_MIN` permits boxes the committed endpoint rejects, and its combination with `CROP_RATIO`/`CROP_PRESETS` can be impossible. On a 5×300 shot, the whole-image box is valid under AC-131.2 but `resolve_region(5,300,0,0,5,300,'px')` raises `ValidationError`: each edge must be at least 8 px. Save therefore yields 422, contrary to D-511 and `CROP_COMMIT`. Separately, on an 8×8 shot, the only minimum-valid size is 8×8; it fails `fitsRatio` for 16:9, 4:3 and 3:2. A preset must violate the minimum, its selected ratio or image bounds. Current AC-131.6–.8 omit that case. Violates family AC-131, specifically the combined guarantees in AC-131.2, .6–.8 and .17. | `implementation-plan.md:120`; `implementation-plan.md:124`; `implementation-plan.md:125`; `implementation-plan.md:202`; `packages/core/src/avkit_core/domain/capture.py:190` | Define GUI eligibility for images with an axis below 8 and a feasible policy for unavailable ratios/swaps, preserving Session 59's endpoint. Add small/odd/portrait cases and assert that every committable box satisfies the actual resolver and every enabled ratio operation has a feasible result. | fixed |
| F2 | Medium | no | behavior | Row 1's four pin changes leave contradictory Green expectations. Adding `crop` to `TOOLS` makes AC-65.1's `expectedGroups('crop',null)` expect `['color']`; its separate color invariant also requires color. With a selected text it expects `['color','text']`, and the pixelate loop expects `['block']`. `CROP_ENTRY` and AC-131.22 require `[]` for crop with any selection. Thus the specified row-1 check fails before geometry Red, and later unchanged guard runs remain incompatible. | `task.md:57`; `implementation-plan.md:159`; `implementation-plan.md:226`; `ui/tests/unit/capture-toolbar.test.ts:37`; `ui/tests/unit/capture-toolbar.test.ts:100`; `ui/tests/unit/capture-toolbar.test.ts:160` | Explicitly adapt the existing option-group oracle, color invariant and selected-pixelate loop in row 1 for crop precedence, retaining all existing annotation-tool expectations. Include these semantic amendments alongside the four pins before expectations become immutable. | fixed |
| F3 | Medium | no | control-defeat | `D494_RUN` can report a successful panel crop in the wrong coordinate frame; mechanism: `task-row-completion-predicate`. A fixture first crops chart-source at `(0,100,1200,700)`, then crops that intermediate shot at `(640,120,520,320)` into chart.png. The checker accepts every criterion, although the final region is `(640,220,520,320)` in chart-source, IoU 0.524 with the requested panel. It never binds the last crop's source id to chart-source. This affects D-521 A/B's supporting run, not the GUI's AC-131 acceptance or Session 59's approved implementation; no AC-family violation is asserted. | `d494-check.py:106`; `d494-check.py:116`; `d494-check.py:123`; `implementation-plan.md:139` | Bind the evaluated crop to the seeded source id, or resolve a verified provenance chain into the original frame before measuring IoU. Add this two-crop negative fixture before relying on an A/B result. Keep D-521 C's explicit not-run result. | fixed |

## Q1 — Goal and the 3840×2160 path

The normal path is coherent: clean saved marks permit entry; Original shows the saved rect beneath the overlay; `SurfacePointer` supplies the live scale and image mapping; the crop branch takes the gesture before mark editing. At fit scale 0.25, an SE drag of −160/−90 CSS px corresponds to −640/−360 image px, producing 3200×1800 under 16:9. W=1920 gives 1920×1080. Enter **in that field** applies the value and sends no request; Enter after focus leaves it commits. That distinction follows the explicit field contract.

`cropCapture` sends four integers to the encoded id, refreshes the catalog, and the page selects/names `item.id`. Session 59 creates its own PNG, sidecar and bake without changing/removing the source. The AC set covers each ordinary goal sentence, including all three commit entries. Passing the current cases would still miss F1's invalid GUI eligibility and impossible presets. The accepted 60b split must complete its assigned controls before claiming the entire anchor.

## Q2 — Geometry and endpoint compatibility

Accepted half-up integer rounding, fixed opposite edges in free resize, no flipping, move clamping, normalized outside drawing and recomputing each move from the down state. Ratio resize is the stated exception that adjusts the perpendicular sides about the centre. These are implementable without reusing mark `resizeBox`, which flips. F1 disproves the assertion that the per-axis `min(8,image side)` rule always supplies a committable box. The actual endpoint minimum is unconditionally eight after clamping.

## Q3 — Ratios, presets and swap

The tolerance is appropriate when one integer side determines the other rounded side: rounding H contributes at most r/2 to width error; rounding W contributes at most 1/2. Original uses `imageW/imageH`, so 600×1000 has ratio 0.6 and its swap 5/3. Swapping Square is inert; free swap's clamping is explicitly allowed. F1 identifies the missing feasibility policy on small images and extreme Original swaps. A rounding tolerance cannot make those feasible.

## Q4 — Fields and nudges

Accepted trim/finite-number validation, null/revert for empty, abc, NaN and 1e999, half-up decimals and negative-to-zero before size/origin bounds. W/H retain origin and fit the dependent side; X/Y retain size. Enter, Escape and arrow stepping stay in fields, with surface arrows moving the box separately. AC-131.16 and .24 explicitly distinguish a field Enter from commit. F1's feasibility policy must also govern ratio-constrained field application.

## Q5 — Page state and modality

`dirty` compares current/saved marks and draft commits; Save updates the saved baseline and Undo can return exactly to it. It is the right unsaved-mark gate. Accepted a crop-first editor branch, pointer routing before marks, cancel on shot/view/removal changes, and disabling annotation/history/lock/Annotated controls. The implementation must preserve the stated modal contract across the viewport's own view-key entrypoint (`CaptureViewport.tsx:697`, called before the editor at `:1169`), with zoom's permitted availability as described in D-518. AC-131.11's sibling/group assertions preserve AC-87.2's lock placement (`capture-page.behavior.test.ts:3280`); placing Crop after the lock is sound.

## Q6 — Commit, refresh and errors

Accepted the explicit one-request-in-flight rule, encoded id, pending busy/disabled feedback, retained box on 409/422 and fixed endpoint messages through `run`. `flattenCapture` already demonstrates awaiting the shared catalog invalidation before returning; following that pattern gives the new id a catalog item before page selection. AC-131.17/.23 assert the observable selected thumb and retained source. The notice must be keyed to the returned item's id as the existing convert path is. No new Console logging is planned. F1 is a deterministic 422 for a box the plan currently calls valid.

## Q7 — Electron seam and Red

Accepted the new seam contract: return 201 with `item`, add it to the GET list and support its image/detail requests; assert selected `aria-current`, status name and source retention. The named flatten precedent actually uses `page.addInitScript` to replace `window.fetch`, not solely `page.route`; row 4 already requires rereading that implementation. Use its shared mutable catalog pattern so refresh sees the new item. A ±1 original-pixel comparison is sound when the chosen mouse coordinates/fixture scale support that precision; derive expectations from the actual surface transform rather than assuming one CSS pixel equals one image pixel.

Both Electron Reds assert the absent bar with `expect(...).toBeVisible()` before acting on it. That is an assertion failure, distinct from an action/test timeout, and the Red parser's locator-detail handling supports it. No Electron run was performed in this review.

## Q8 — Names, pins and guards

Row 1 covers the new production imports listed in `DECLARED_NEW`; its retained fixture-only names already exist or are confined to selftests. Geometry and page Reds can fail by assertion after those stubs. The four named inventory/hint pin movements and additive test-id block are appropriate. F2 identifies semantic expectations beyond those four pins that become live when `TOOLS` gains crop. The AC-80.8 inventory remains compatible with keeping conditional swap in the separate `CROP_BUTTONS` record. No additional out-of-scope exhaustive caller was identified in the targeted reads/sweeps.

## Q9 — D-494 agent run

The supplied describe receipt matches the current server: top-level description plus flattened action/field schema precede the separate `_meta.action_descriptions.crop` section. CROP_TEXT is absent from the model-visible part. Cutting at that heading gives a useful test of the locally observed client surface and arithmetic, rather than a test of CROP_TEXT or vision. One Haiku pass is evidence for that run, not a guarantee that every stronger model succeeds.

The harness refuses remove/flatten/revert/image before making a server call. `spawnBackend` binds 127.0.0.1 and `buildLaunch` supplies isolated app data/token without an inherited API-base override. D-521 A/B have an operational path; C is a deliberate not-run and leaves D-494 carried. F3 qualifies what an A/B checker pass currently proves. Existing negative selftests correctly reject absent/failed crop, wrong applied box, changed source, missing chart/report and forbidden actions; the new wrong-source fixture passes them all.

## Q10 — Human look and process ownership

Accepted the default look root, fresh-root refusal, real-stack seeded settings/marks and AVKIT_APP_DATA propagation. Main startup redirects Electron userData as well as backend storage (`ui/src/main/index.ts:219`), so this is not merely a backend-only isolation claim. Process records bind descendants by pid and creation time; stop rechecks that identity and excludes MCP servers/foreign processes. D-522 A requires Mat's words and no owned process left; B requires not-run and no launch record. The A/no result passing `look-check` is intentional: row 6 separately requires correction rows. No launch or real process enumeration/termination was run here.

## Q11 — Endings, scope, identity and safety

Existing CRLF/LF files and new LF modules/tests are stated explicitly; rows require byte-preserving edits. `scope-paths` includes the product paths, registers and plan prefix, covering row3-ui-src.json, human-check.md and all d494/look files. Identity binds source/tests/config, the scripts and row3 snapshot, registers, grouping and runtime inputs; post-gate prose exclusions are explicit. The supplied identity selftest ends with zero failures; it was read, not rerun against the real tree.

S14 uses the same ruling grammar as look/d494 and fails for the current unruled decisions. S8 looks up `id: MEU-130` and checks approved plus dirty Session 59 paths. S11 checks the actual route/export lines and absence of the new tool. Supplied probes show ruled exit 1, queue/shapes/anchors exit 0. No demonstrated material false pass was found in these three checks. Unit/Electron work uses mocks/seams; optional images stay under seeded temporary roots. D-521's authorized model text is the only proposed external egress; image is refused. The review itself made no network request and ran no repository-writing validation.

## Checklist Results

### Plan Review (PR-1 to PR-9)

| Check | Result | Observation |
|---|---|---|
| PR-1 Plan/task alignment | pass | Same MEU, geometry-before-page sequence, 24 ACs, optional outside checks and H1/H2 order. |
| PR-2 Unstarted | pass | Task rows are unstarted; new production/test paths are absent in supplied anchors and current reads. MEU-131 is pending. |
| PR-3 Task contracts | pass | Rows declare owner, deliverable, exact validation, dependency and status. |
| PR-4 Validation realism | partial | Red parser and staged commands are concrete; F2 leaves contradictory existing expectations. |
| PR-5 Source-backed planning | partial | Ordinary behavior traces to 09/design/grouping. F1 contradicts the committed resolver used to justify D-511. |
| PR-6 Corrections readiness | pass | Target-bound rolling review and correction path; this is round 1, so no recheck census is due. |
| PR-7 Scope discipline | pass | Renderer-only session, named MEU-105/132 deferrals and accepted grouping split; Session 59 is preserved. |
| PR-8 Reachability and negative oracles | partial | Main GUI entrypoints and Red oracles are reachable. F3 demonstrates an optional row-7 predicate false pass. |
| PR-9 Single-statement contracts | pass | Named geometry/page/run contracts provide the operative definitions. No materially ambiguous repeated literal was found. |

### Evidence

The probe command exits zero because it confirms its expected counterexamples; that exit is not a product pass.

```json
{"schema_version":"evidence.v1","check_id":"s60-independent-plan-probes","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-review-probes.py (PYTHONDONTWRITEBYTECODE=1, PYTHONIOENCODING=utf-8)","cwd":"P:/av-kit","scope":"resolver, mathematical feasibility, existing toolbar oracle, synthetic d494 checker ledger","phase":"targeted","exit_code":0,"result":"fail","tested_state":"working-tree plan and referenced code at supplied HEAD 8f29046; read-only review, not full-gate identity","output":"5x300 whole box: ValidationError each edge must be at least 8 px. No feasible CROP_MIN/fitsRatio sizes on 8x8 for 16:9, 4:3, 3:2. Existing crop option expectations include color/text/block while contract requires []. D494 wrong-source fixture accepted=True; actual original-frame IoU=0.5238095238095238."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-plan-script-selftests","procedure":"With PYTHONDONTWRITEBYTECODE=1 and TMP/TEMP=C:/Temp/av-kit, independently ran red-check.py, look-check.py, d494-check.py, dev-app-procs.py and hotkey-free.py --selftest through the repository .venv interpreter; inspected each completed receipt and exit.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"plan-local synthetic selftests only","phase":"targeted","exit_code":null,"result":"pass","tested_state":"current five plan-local scripts; no product tests or live processes","output":"All five child exits 0. red-check: 40 fixtures, 12 positive, 28 negative, 0 wrong. look-check and d494-check: 0 wrong. dev-app-procs: 0 failures. hotkey-free: 0 wrong. These existing fixtures do not include F3's wrong-source case."}
```

### Design/implementation review applicability

Contract and local-code traceability were manually assessed by codex-independent-reviewer as recorded in Q1–Q11 (null exit). Runtime/full-gate implementation checks are n/a for this unstarted, read-only plan review. Formatting/template-order observations are excluded under Mat's scope direction.

## Verdict

`changes_required` — F1 prevents the planned GUI from keeping its geometry and endpoint guarantees on supported small images. Define feasible eligibility/ratio behavior and test it before implementation. Also correct F2's incompatible guard expectations and F3's optional-run source binding. D-521 and D-522 remain Mat's decisions. No repository file was edited; the coordinator may copy this report to the canonical path.


## Recheck (Round 2)

**Date:** 2026-11-10. **Reviewer:** codex-independent-reviewer (Codex/OpenAI); author and corrector: Claude Code/Anthropic. **Verdict:** `changes_required`. **Intent achieved:** partial. One blocking finding remains, F1; F2 and F3 are fixed. The preceding round 1 account is historical and retained, apart from the permitted status-cell updates.

### Recheck Result

| Finding | Recheck Result | Evidence |
|---|---|---|
| F1 | fixed | The fixed minimum and `cropEligible` solve the endpoint-size failure (`implementation-plan.md:120`, `:130`, `:204`, `:214`). The new ratio definitions still disagree after rounding (`:124-125`, `:209`): on 400×10, swapped 4:3 has `ratioMinBox={8,11}` and is infeasible, while its largest rounded box `{8,10}` has both sides ≥8, passes `fitsRatio` and is accepted unclamped by the real resolver. The asserted exact feasibility equivalence cannot pass. On 380×608, swapped Original is feasible, but its largest rounded box 380×238 fails the literal `fitsRatio`: error `0.8000000000000114` exceeds `0.8`. |
| F2 | fixed | `CROP_ENTRY` now takes crop before the region rules (`implementation-plan.md:129`); the two new pin rows explicitly change the independent oracle/color invariant and the selected-pixelate loop (`:163-167`), with crop assertions retained. `task.md:57` includes them. AC-131.22 covers every selected mark kind (`implementation-plan.md:224`). The existing eraser loop already accepts crop's empty groups. |
| F3 | fixed | The checker compares the last successful crop's response `source_id` to `seed/source-id.txt` (`d494-check.py:117-122`); the harness requires exactly one source basename and writes its id synchronously after registration (`d494-harness.ts:103-109`). Coordinator step 3 seeds before agent dispatch (`d494-run.md:12-14`). Independently rerun selftest: 19 cases, 0 wrong, including wrong-frame and missing-id rejection and correct-run acceptance. |

### Remaining Finding

**F1 — High; blocking; behavior; High confidence; violates AC-131 (specifically AC-131.6–.8 and the combined `CROP_RATIO`/`CROP_PRESETS` guarantees).** The original eight-pixel endpoint failure is fixed, but the replacement ratio contract is not jointly satisfiable as written. This is the existing minimum/ratio finding, not a new finding on a nearby surface.

The 400×10 case is already in AC-131.2's required sweep. For swapped 4:3, `r=0.75`, the defined minimum is `(8, roundHalfUp(8/0.75)) = (8,11)`, so `ratioFeasible` and `presetFeasible` are false. Fitting the ratio to that image gives `(7.5,10)`, rounded by `CROP_ROUND` to `(8,10)`; `abs(8-10*0.75)=0.5` meets the stated tolerance, and `resolve_region(400,10,0,0,8,10,'px')` returns `(0,0,8,10,False)`. Thus a valid rounded preset is disabled while AC-131.7 requires it to be feasible exactly when that largest box has both sides at least eight. Implementing the formula and implementing that oracle yield different UI behavior and cannot both go Green.

There is also an enabled-preset counterexample: on a 380×608 portrait shot, swapped Original has `r=608/380=1.6` and minimum 13×8. The largest fit is 380×237.5, which `CROP_ROUND` makes 380×238. IEEE-754 evaluation of the specified `fitsRatio` yields `abs(380-238*1.6)=0.8000000000000114`, greater than its `0.8` tolerance. Returning the specified largest rounded box violates the promised ratio predicate; shrinking or changing rounding abandons another stated contract. The real resolver accepts this box unclamped, so this is a ratio-contract failure, not a claim that Session 59 rejects it.

**References:** `implementation-plan.md:119`, `:124-127`, `:204`, `:208-210`. **Recommendation:** use one consistent definition of rounded feasibility and the minimum for presets, swaps, subsequent drags and fields; make the ratio predicate numerically stable at half-pixel boundaries. Add the 400×10/swapped-4:3 and 380×608/swapped-Original cases before Green. Preserve the fixed endpoint minimum and the ineligible-shot gate. This blocks because the operative behavior and mandatory oracle disagree, not because of wording or formatting.

### New Findings

| ID | Finding | Status |
|---|---|---|
| None | None. F1 carries the remaining ratio/minimum incompatibility; no F4 is introduced. | n/a |

### R1 — Geometry, rounding and endpoint compatibility

**Partially fixed.** On an eligible integer-sized image, the six bounds in `CROP_MIN` imply exactly that `resolve_region` accepts the box without clamping. The planned `endpointAccepts` restatement is adequate for this property: an independent comparison against the real resolver found zero mismatches over 32,768 boundary cases. Reference arithmetic across 3,254 small/named images and 29,286 ratio cases also supplied 253,435 accepted integer boxes with no endpoint mismatch. These are independent mathematical/source probes, not executions of future crop functions and not proof that the unimplemented functions satisfy the contract.

The ratio equivalence is false after rounding, as F1 shows (153 disagreements in the reference sweep). Minima and largest boxes are endpoint-safe, and an eligible Shift start ratio has a feasible minimum. Nonetheless a blanket claim that all presets, swaps, drags and fields agree with `fitsRatio` is premature while F1 remains. `endpointAccepts` checks bounds/minimum, not ratio truth, and therefore cannot catch that defect on its own. AC-131.12 asserts the undersized-shot reason and no-entry behavior; AC-131.15 asserts unavailable preset options, disabled swap reason and X doing nothing (`implementation-plan.md:214`, `:217`). These are meaningful disabled-state tests; their future runtime execution is not claimed here.

### R2 — Existing toolbar guards

**Fixed at plan level.** Read all of `capture-toolbar.test.ts`, the production option rules, the nearby icon pins, and a targeted `CaptureTool`/`TOOLS` census in TypeScript tests. Applying the stated amendments leaves the seven existing tools' 49 tool/selection combinations unchanged and gives crop empty groups for all seven selection states. Removing crop's leading rule is detected for six selection states, including selected pixelate; the selected-eraser case already returns empty. AC-90.9 now retains its old assertions for every annotation tool and separately asserts crop precedence. AC-91.8's existing loop remains correct. Inventory and no-shot pins are covered; the literal annotation-tool loop at `capture-inbox.test.ts:876` does not consume `TOOLS` or assert exhaustive tool inventory. No additional contradictory caller was found in the targeted census. No Vitest or Electron test was run.

### R3 — D-494 source frame and seed reliability

**Fixed.** Under A/B, an actual last crop with another response `source_id` fails independently of IoU; missing seed identity fails too. The approved Session 59 service supplies the actual source shot id (`packages/core/src/avkit_core/services/capture.py:980`, route forwarding at `packages/api/src/avkit_api/routes/captures.py:417`). The id is selected from the seeded capture list by exact basename with a uniqueness check and written synchronously before seed resolves; the agent runs later. Correct original-source and near-box fixtures pass; last-wrong-crop, crop-of-a-crop and missing identity fixtures fail. Under C, explicit not-run remains intentional. This is code tracing and synthetic evidence, not a live harness claim.

### R4 — Corrections, Red, scope, endings and intent

**No new independent finding.** Plan/task declarations and the four added `DECLARED_NEW` names agree; the true/8×8 stubs permit assertion Reds. Required Red blocks still reject missing-export diagnostics: four new-name assertion fixtures were accepted and four required missing-export fixtures refused. The complete Red selftest returned 40 fixtures, 0 wrong. The S11 source includes the new endpoint constant check (`baseline.ps1:129`), consistent with the supplied isolated-shapes receipt; baseline itself was not executed.

The only remaining substantive correction problem is F1's arithmetic. No tracked diff was present (`git diff --name-only HEAD`, exit 0; only the known sandbox ignore-file warning), so no tracked CRLF file was changed. `git status --short` showed only the supplied plan/review paths and the disclosed sandbox-only ignored-file artifact; that file was not opened. No scope/identity gap or other goal-anchor break was demonstrated in the corrected surfaces. D-521 and D-522 stay open for Mat. The goal anchor is retained verbatim above. No repository file was edited, and no network, product suite, baseline, gate, app, seed or harness was run.

The independent byte-level check also confirms all nine named CRLF targets retain pure CRLF: each has zero bare LF and zero bare CR (`rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-r2-endings.py`, exit 0). This checks actual working-tree bytes rather than inferring endings from Git normalization.

### Round 2 Checklist Results

| Check | Result | Observation |
|---|---|---|
| R1 endpoint/minimum fix | pass | Real resolver agrees with `endpointAccepts` in 32,768 boundary cases; reference valid boxes accepted unclamped. |
| R1 ratio/minimum consistency | fail | F1's 400×10 swapped-4:3 equivalence and 380×608 swapped-Original tolerance counterexamples. |
| R2 toolbar fix | pass | Explicit oracle, invariant and pixelate-loop changes; old annotation expectations preserved. |
| R3 source-frame fix | pass | Synchronous unique-source seed write; response source-id comparison; 19 selftest cases, 0 wrong. |
| R4 Red declarations and negative oracle | pass | 40 Red fixtures, 0 wrong; eight added-name diagnostic probes behave as required. |
| Repository and network scope | pass | Read-only source inspection; all reviewer writes confined to scratch; no network request. |
| Product/runtime validation | n/a | Unstarted plan; prohibited suites and live programs not run. |

### Commands and Durable Evidence

All Python commands below used `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`; temporary fixture roots used `TMP`/`TEMP=C:/Temp/av-kit`. Receipts preserve each child's exit. The failing arithmetic probe intentionally asserts the plan's incompatible guarantees; its exit 1 is the decisive negative case, not setup failure. The broader probe's exit 0 means its observations completed, not that the plan passed.

```json
{"schema_version":"evidence.v1","check_id":"s60-r2-ratio-contract","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-r2-ratio-counterexample.py","cwd":"P:/av-kit","scope":"literal CROP_ROUND/CROP_RATIO/CROP_PRESETS arithmetic and committed resolve_region","phase":"targeted","exit_code":1,"result":"fail","tested_state":"round-2 working-tree plan at supplied HEAD 8f29046; source/formula probe, not product implementation","output":"400x10, swapped 4:3: ratioMinBox=(8,11), ratioFeasible=False; largest rounded=(8,10), fitsRatio=True, resolver=(0,0,8,10,False); exact equivalence=False. 380x608, swapped Original: largest rounded=(380,238); error=0.8000000000000114, tolerance=0.8, fitsRatio=False; resolver=(0,0,380,238,False). AssertionError: remaining F1: ratio contracts are not jointly satisfiable as written."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r2-reference-probes","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-r2-probe.py","cwd":"P:/av-kit","scope":"endpoint predicate comparison, reference ratio arithmetic, planned toolbar semantic tables, new Red-name diagnostics","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current source and stated round-2 plan formulas; reference arithmetic only","output":"3254 images; 29286 ratio cases; 253435 reference boxes accepted by resolve_region; 32768 endpointAccepts boundary comparisons, 0 mismatches; 153 feasibility/rounded-largest disagreements observed; Shift start-ratio feasibility 0 mismatches; 49 old toolbar cases unchanged, 7 crop cases empty, omitted crop rule caught for 6 selections; 4 required assertion diagnostics accepted and 4 required missing-export diagnostics rejected. This probe completes successfully while exposing F1."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r2-d494-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-check.py --selftest","cwd":"P:/av-kit","scope":"synthetic D494_RUN checker fixtures only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current round-2 d494-check.py","output":"19 cases; d494-check selftest: 0 wrong. A good run and B near box pass; crop of a crop, wrong frame and no source-id.txt both pass=False want=False."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r2-red-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-crop-tool/red-check.py --selftest","cwd":"P:/av-kit","scope":"synthetic Red parser fixtures only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current round-2 red-check.py","output":"red-check selftest: 40 fixture(s) (12 positive, 28 negative), 0 wrong: []"}
```

Manual source observations in R1–R4 were made by `codex-independent-reviewer`, with null exit codes; file:line references identify the inspected paths. Shell receipts also include targeted reads/searches of the plan/task, `capture-toolbar.test.ts`, `capture-toolbar.ts`, relevant capture source and the d494/baseline scripts. No baseline or full-gate result is inferred from those reads.

### Round 2 Verdict and Follow-up

`changes_required` — retain F1 as partially corrected and reconcile rounded feasibility/minimum and numerical ratio tolerance before implementation. F2 and F3 are fixed. No new findings. This review does not select D-521 or D-522. The complete rolling report is `C:/Temp/av-kit/s60-plan-review-round-2.md`; the coordinator owns canonical copying and ledger recording. Product implementation remains unstarted; this is a plan verdict only.


## Recheck (Round 3)

**Date:** 2026-11-10. **Reviewer:** codex-independent-reviewer (Codex/OpenAI, class `avkit_independent_reviewer`); author and corrector: Claude Code/Anthropic. **Verdict:** `approved`. **Intent achieved:** yes, at plan level. F1, F2 and F3 are fixed; no new findings. The round 1 and round 2 accounts above remain historical, unchanged except their finding status cells. This section is the current assessment.

### Recheck Result

| Finding | Recheck Result | Evidence |
|---|---|---|
| F1 | fixed | `CROP_RATIO` now constructs and checks the same integer-driving-side box and defines all three feasibility predicates from one monotone range (`implementation-plan.md:124-127`). Swapped 4:3 on 400×10 has minimum 8×11, largest 7×9 and is infeasible; swapped Original on 380×608 has largest 379×237 and fits. AC-131.2/.6/.7/.8 require endpoint safety, exact ratio membership, feasibility agreement and swap refusal (`:204`, `:208-210`). Independent reference operations satisfy bounds, minimum and the real resolver; no remaining contract counterexample was found. |
| F2 | fixed | The leading crop option rule and the explicit independent oracle, color-invariant and pixelate-loop amendments remain (`implementation-plan.md:129`, `:163-167`; `task.md:57`). The ratio correction does not change these rules or their old annotation-tool expectations. |
| F3 | fixed | The last crop still must identify the seeded original source (`implementation-plan.md:139`; `d494-check.py:117-122`). The independently rerun 19-case checker selftest passes, including rejection of a crop of a crop in the wrong frame and missing source identity. Mechanism: `task-row-completion-predicate`. |

### New Findings

| ID | Finding | Status |
|---|---|---|
| None | None. | n/a |

### T1 — Joint satisfiability and operation boundaries

**Yes.** For a fixed positive ratio, `ratioBox(s, r)` is monotone in its whole driving side. Thus every allowable driving side lies in the same interval ending at `sMax`: the minimum fits exactly when `sMax ≥ 8`, exactly when the largest box has both sides at least eight. Construction and `fitsRatio` use the identical rounded expression. The prior tolerance and independently rounded continuous-largest rectangle have been removed (`implementation-plan.md:124`). Infeasible presets and swaps return `null` without changing the active ratio (`:125-126`); enabled presets return `ratioLargestBox` and reposition it without changing its size.

Corner resize retains the opposite corner. Its available rectangle already contains the starting ratio box, so its upper driving limit is at least that box's driving side and cannot fall below eight. An edge fixes its opposite edge and can centre/shift across the whole perpendicular image axis; that space also admits the start. Fields retain an origin already admitting the active box. Drawing has no such starting-box guarantee, but `CROP_DRAW` explicitly shifts inside when the local minimum will not fit; global feasibility supplies that minimum (`:123-127`). This fallback prevents an empty local interval from becoming an enabled impossible operation. Moving and X/Y edits leave the ratio size unchanged; Reset/Free deliberately leave ratio mode.

The non-driving inverse mapping is sound: rounding the dependent side adds at most half a pixel, and converting it back contributes at most `0.5/r` to the driving side for `r ≥ 1`, or `0.5*r` for `r < 1`; at `r = 1` the mapping is exact. In particular, an unchanged starting ratio box maps back to its own driving side. Rebuilding after clamping always uses `ratioBox`; it does not reuse the requested dependent side as an independently rounded dimension. Under Free/Shift the start ratio is the start width divided by height, so the start box supplies a feasible driving side. Independent probes included 43,025 rounded-side inverse cases and 10,000 additional Free/Shift starts, with no disagreement.

The independently written constructive probe checked 16,900 feasibility cases over small, odd, long and portrait images; its reference operations covered 53,760 handle cases, 10,752 draws, 7,840 fields, 1,680 moves/origin edits and 560 starting/preset boxes. Every one of those 74,592 reference boxes fit the exact ratio, had integer coordinates, stayed inside the image, met the eight-pixel minimum and passed the actual `resolve_region` unchanged. The supplied reference probe was also inspected and independently rerun: 16 named cases and 10,980 preset cases over 1,098 shots, zero problems. These are formula/construction checks, not tests of future TypeScript functions.

### T2 — Acceptance oracles and intended Red

**Yes, at plan level.** AC-131.2 requires endpoint acceptance and no clamping across all named box producers, all handles and feasible preset orientations, including 380×608. AC-131.6 adds the exact positive/negative ratio pair (16×9 accepted, 17×9 rejected), `ratioBox(9, 16/9)`, the portrait regression and ratio membership for the resize/draw/field sweep. AC-131.7 asserts the three-way equivalence, largest-box membership/bounds and the 400×10 swapped-4:3 regression. AC-131.8 covers successful portrait swap and unchanged Square as well as refusal of infeasible swaps (`implementation-plan.md:204`, `:208-210`). Together these distinguish the old wrong formulas from the corrected contract; endpoint acceptance alone would not do so.

Each required AC has a concrete assertion Red against row 1, without missing imports: `.2` expects `cropEligible(5,300)` false while the stub returns true; `.6` expects `ratioBox(9,16/9)` 16×9 while the stub returns 8×8; `.7` expects the six ids while `ASPECT_PRESETS` is empty; `.8` requires a successful 16:9-to-9:16 swap, which neither an unchanged landscape input nor `null` satisfies. A null result is asserted before accessing its fields. The declarations in `implementation-plan.md:145`, `:319`, `:325` and `task.md:57` agree with the added exports in `red-check.py:79-82`; row 2 requires AC-131.1 through .10 by assertion (`task.md:59`; `red-check.py:295-314`). Five synthetic stub witnesses fail their intended value assertions, four required assertion blocks are accepted, and four required missing-export cases are rejected. The parser's full selftest remains 40 fixtures, zero wrong. These checks establish runnable Red design; no actual Vitest Red is claimed before implementation.

### T3 — Consistency and prior fixes

**No new contradiction found.** `CROP_DRAW`, `CROP_PRESETS`, `CROP_SWAP` and `CROP_FIELDS` all build or retain the canonical `ratioBox`, and their feasibility/space rules refer back to `CROP_RATIO` (`implementation-plan.md:123-127`). D-512's chosen text and reasoning describe the same construction and exact predicate (`:454`, `:462`). D-513 still describes the largest feasible box, reciprocal ratio, centring and unavailable-ratio policy (`:469`, `:476`). Their meaning agrees with the changed ACs, export list and row 1 stubs in both plan and task. The old toolbar amendments and the D-494 source-frame check remain intact. No F4 is warranted. D-521 and D-522 remain Mat's open decisions; approval does not select either option.

### Round 3 Checklist Results

| Check | Result | Observation |
|---|---|---|
| T1 ratio/feasibility/operation contract | pass | Monotone shared construction; named counterexamples resolved; independent reference operations and real endpoint agree. |
| T2 ACs and assertion Red design | pass | Exact positive/negative oracles, operation sweep and three-way equivalence; synthetic stub witnesses and required-name rejection probes pass. |
| T3 plan/task/decisions and prior fixes | pass | Corrected surfaces agree; F2 amendments retained; all 19 D-494 checker fixtures pass. |
| Review boundaries | pass | Confirmed `main`, HEAD `8f290462cdbb733172a1ec3b1e95673ed0081301`. All reviewer writes under `C:/Temp/av-kit`; no secret file opened and no network request. |
| Product/runtime verification | n/a | Unstarted plan. No pytest, Vitest, Playwright, baseline, session gate, dev app, seed or live harness run. |

### Commands and Durable Evidence

Python commands used `PYTHONDONTWRITEBYTECODE=1`, `PYTHONIOENCODING=utf-8`, `RECEIPTS_DIR=C:/Temp/av-kit`; selftests also used `TMP`/`TEMP=C:/Temp/av-kit`. Each process was run through `rtk proxy` with all streams redirected and the child exit captured immediately. The following outputs are observations of this recheck, not product/full-gate evidence.

```json
{"schema_version":"evidence.v1","check_id":"s60-r3-independent-ratio-operations","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-r3-independent-probe.py","cwd":"P:/av-kit","scope":"constructive reference ratio arithmetic, inverse mappings, local operation spaces and actual resolve_region","phase":"targeted","exit_code":0,"result":"pass","tested_state":"round-3 working-tree plan and committed resolver at HEAD 8f290462cdbb733172a1ec3b1e95673ed0081301; not future TypeScript","output":"PASS: named counterexamples, exact fitting range, inverse rounding, all eight handles, field origins, draw fallback, Free/Shift. Counts: draw 10752, feasibility 16900, field 7840, free-shift 10000, inverse 43025, move-or-xy 1680, preset-or-shift-start 560, resize 53760. Every constructed reference box passed the real resolver unclamped."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r3-supplied-reference-rerun","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-r2-ratio-probe.py","cwd":"P:/av-kit","scope":"inspected supplied reference implementation of the round-3 ratio contract","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current plan formulas and committed resolve_region; reference only","output":"16 named cases correct. 400x10 swapped 4:3 minimum=(8,11), largest=(7,9), feasible=False. 380x608 swapped Original largest=(379,237). sweep: 1098 shots, 10980 preset cases; problems: 0."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r3-red-oracles","command":"rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s60-r3-red-oracles.py","cwd":"P:/av-kit","scope":"row-1 stub assertion witnesses and synthetic required-Red parser fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current plan/task stubs and current red-check.py; no product runner","output":"PASS: 5 stub assertion witnesses, 4 required assertion blocks accepted, 4 required missing-export cases rejected."}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r3-red-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-crop-tool/red-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local synthetic Red-parser selftest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current round-3 red-check.py","output":"red-check selftest: 40 fixture(s) (12 positive, 28 negative), 0 wrong: []"}
```

```json
{"schema_version":"evidence.v1","check_id":"s60-r3-d494-selftest","command":"rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-10-gui-capture-crop-tool/d494-check.py --selftest","cwd":"P:/av-kit","scope":"plan-local synthetic D494_RUN checker selftest","phase":"targeted","exit_code":0,"result":"pass","tested_state":"current d494-check.py; no live agent or seed","output":"19 cases; d494-check selftest: 0 wrong. crop of a crop, wrong frame: pass=False want=False; no source-id.txt: pass=False want=False; A good run and B near box pass."}
```

Manual cross-file observations for T1 to T3 were made by `codex-independent-reviewer`, with null exit codes, at the file:line locations above. Required product implementation and runtime assertions remain future execution work, not completed tasks. No implementation completion is claimed.

### Round 3 Verdict

`approved` — F1 is fixed and F2/F3 remain fixed. No open High/Critical finding or other new finding remains. Executing this plan now has a coherent geometry/ratio contract and substantive acceptance oracles for the registered Crop-tool intent. The coordinator owns canonical copying and ledger recording; this reviewer wrote no repository file.
