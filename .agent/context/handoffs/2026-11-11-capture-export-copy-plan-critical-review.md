---
date: "2026-11-11"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s64-plan-canonical-2026-11-11-capture-export-copy"
round: 4
---

# Critical Review: 2026-11-11-capture-export-copy

> **Review Mode:** plan. **Verdict:** changes_required. **Intent achieved:** partial, judged as a plan.

## Intent Anchor

Session 64 lets an agent make a small deliverable from a shot. `POST /captures/{id}/export` and `avkit_capture` `export` take the shot as it is shown (the annotated bake when it has saved marks, otherwise the original), shrink it so its long edge is at most `max_edge` (never enlarging), encode it as PNG, JPEG or WebP at `quality`, and write it into the capture inbox as a new shot with source `Export`. The source's file, sidecar and bake are only read. The response gives the new shot's id, path, size and byte count, so an agent can see when an export came out larger than it wanted and export again with a smaller edge or quality. The session also runs the design's three-task description eval on the finished video stills surface.

## Scope

Reviewed the working-tree plan/task, all eight plan-local scripts/run instructions, cited export spec/design/grouping, MEU-136 by id, relevant existing capture/API/MCP code, count/order/signature guards, and supplied planning receipts. Observed HEAD `2832e3d`; implementation rows remain unstarted and MEU-136 is pending. Applied PR-1–PR-9, the Materiality Gate and Verdict Rule. Claude Code/Anthropic authored the plan; Codex did not.

Accepted the supplied prior approvals, design D-1–D-5, grouping decisions and exclusions. D-608 remains Mat's decision. No repository file was edited, no video was read, and no network request, product suite, baseline/session gate, backend, MCP server, npm, npx or tsx was run. New probes and small images were written only under `C:/Temp/av-kit/s64/review`; the report is in the assigned receipts directory. Forbidden files were not opened. Product behavior below is a review of proposed implementation, not a claim that unimplemented code passed.

## Findings

All findings have High confidence. F1 and F2 block; F3 and F4 do not independently require another round.

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | behavior | `EXPORT_ENCODE` clips 16-bit grayscale PNG values when converting directly to RGB for JPEG/WebP. A valid `I;16` PNG with samples 0, 32768, 65535 exports as 0, 255, 255, destroying midtones. AC-136.4 checks mode/encoding success without checking these pixel values; thus the planned tests can pass while the exported shot loses visible content. Violates AC-136, especially AC-136.4/.13 and the source-as-shown contract. | `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md:121`; `:205` | Define a depth-aware conversion preserving the 16-bit tonal range before JPEG/WebP encoding. Add grayscale-ramp/midtone pixel assertions with and without shrinking. Keep PNG's native-depth behavior. | open |
| F2 | High | yes | control-defeat | `EVAL_RUN` can mark t3 complete without the requested JPEG deliverable. The checker trusts requested format and response dimensions, then checks only file existence/length. A PNG, a 16×16 JPEG and even a 12-byte non-image each pass with response dimensions 1280×720, correct byte count/source id and an unchanged source. This demonstrably false-passes AC-136.19 under D-608 A/B. Subject: committable-tooling; mechanism: task-row-completion-predicate. Violates AC-136. | `docs/execution/plans/2026-11-11-capture-export-copy/eval-check.py:163`; `:169`; `:175` | Load/decode the actual output; require JPEG, verify actual dimensions against the response and the minimum edge, and include these three negative fixtures beside a real JPEG positive control. | open |
| F3 | Medium | no | behavior | `EXPORT_ROUTE` and `EXPORT_MCP` differ on integral JSON floats beyond the stated PNG-quality difference: REST `StrictInt` rejects `max_edge:64.0` and `quality:80.0`; JavaScript/Zod accepts them and serializes integer literals to REST. AC-136.18's key comparison cannot detect this. | `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md:123`; `:124`; `:219` | Explicitly document this representation difference, or accept bounded integer-valued JSON numbers consistently while continuing to reject booleans and fractional values; test the same JSON cases through both transports. | open |
| F4 | Medium | no | behavior | The proposed bare `.strict()` permits a path to appear in the new MCP action's validation error: an extra key `C:/private-marker/source.png` is reflected as `Unrecognized key: "C:/private-marker/source.png"`. The existing registry forwards issue messages and `toToolError` redacts token values only. This contradicts `NO_RAW_OUTPUT` for rejected input. Invalid enum *values* are masked by the existing union; this finding concerns extra-key names. | `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md:124`; `:127`; `mcp-server/src/toolsets/registry.ts:360`; `mcp-server/src/client.ts:70` | Give the export schema a fixed unknown-field error or sanitize its validation messages, and add an MCP marker-path negative test with a positive control. | open |

## Q1 — Goal and one call

The ordinary annotated 3840×2160 PNG trace is complete: `EXPORT_MCP` → registry POST → `EXPORT_ROUTE` → checks → saved-marks bake → 1920×1080 → quality-80 JPEG → owned temp/replace/register → 201 with actual bytes and `Export`. `get` reads the new row; exporting that id again at lower quality uses its original file and returns another shot. All seven spec rule rows have AC coverage. AC-136.10 explicitly hashes the source file, sidecar and bake and checks the source row; it does not merely assert immutability. F1 prevents general acceptance of “as shown”; F2 prevents trusting the eval completion result.

## Q2 — EXPORT_SIZE

Accepted. `(2*n+d)//(2*d)` implements nonnegative half-up rounding; orientation restoration and the floor of one preserve the dimensions' bounds. The supplied probe really compares against `Fraction`, covering 3,060,000 cases with zero mismatches and zero growth cases. It samples the edge in steps of seven, whereas AC-136.2 deliberately tests every edge in its smaller exhaustive span and adds the specified half/portrait/extreme cases. This is adequate mathematical coverage.

## Q3 — Checks and transport

Scalar format/type/range/PNG-quality checks precede locking and I/O. Source and target-format-limit checks occur under the lock but before output creation, as their inputs require the loaded shot. A 20000×10 WebP target and 70000×1 JPEG target with omitted max_edge reach the two limit refusals. Messages and order are sound at the service/API layers. The before-validator sees explicit null and leaves omitted defaults alone; the permitted probe confirmed that. Booleans, fractional numbers, huge magnitudes, invalid formats and unknown fields are refused. F3 records the additional integral-float transport difference. PNG-quality's downstream API refusal is harmless. The proposed route position is coherent with the current crop/delete declarations.

## Q4 — Source selection

Accepted. `_saved_marks` and `_variant_path` implement the stated source choice, including fixed missing-bake and malformed-sidecar refusals. Bake draws on the original-sized canvas without cropping/resampling, so its dimensions match the row. AC-136.9 proves arguments and AC-136.13 checks a marked pixel through the real API stack. No rebake or source write is introduced.

## Q5 — Encoding

The prescribed conversions save all twelve named modes in small independent Pillow probes. Palette/1-bit conversion before LANCZOS, no resize at unchanged dimensions, alpha handling, default/passed quality and explicit metadata clearing are sound. `_to_srgb` returns a replacement sRGB profile after a successful managed conversion; “keep ICC” must retain that returned profile rather than reattach the old CMYK/LAB profile. AC-136.4/.5/.6 cover metadata reads, quality forwarding and fixed save errors. Successful encoding alone does not preserve tones: F1 reproduces the valid 16-bit PNG failure. D-613's accepted orientation/metadata policy is not reopened.

## Q6 — Names and ownership

Accepted. Sanitizing the stem removes surrogates, controls and dots; the fallback is safe and reserved names acquire the suffix. `_crop_dest`'s extension default keeps crop's PNG names; its existing taken set covers cross-format originals, sidecars, bakes and temps. The plan preserves the crop pattern's important ownership detail: assign the owned temp only after `xb` succeeds, then relinquish its name after replace. Existing other-writer temps survive. Real-adapter hashes, failure cleanup and crop guards cover the reuse. Reading `_inbox()` at use is explicit. The planned refusal/mask boundary is appropriate.

## Q7 — Deadlines

The inventory names the main blocking classes, but its sub-10-second cap claim is not established by the receipt. The receipt measures one mixed-content 4K image, not a cap-sized encode or a worst case. Also, `Image.MAX_IMAGE_PIXELS` is a warning threshold: the permitted no-allocation Pillow probe accepted 100,000,000 pixels with `DecompressionBombWarning`; the exception threshold is twice MAX_IMAGE_PIXELS. The lock wait is not a numeric bound either. Treat the 30-second choice as an unproven performance assumption; a cap/contention measurement or an explicit enforced bound would support it. No actual timeout was reproduced, so this is not promoted to a High finding or a demand to redesign crop's accepted pipeline.

## Q8 — MCP and audit

Accepted apart from F3/F4. `desc()` preserves all four shared M7 markers; AC-38.5 and AC-67.17 remain compatible. `EXPORT_TEXT` explains bytes/retry, source selection and format-specific quality. Pending-baseline membership, action adjacency and an offline audit step without `--update-baseline` follow the current mechanism. AC-136.18 explicitly obtains REST property keys from committed OpenAPI. The pending status does not claim a live audit pass.

## Q9 — Pins

The independent grep and targeted reads found the material 77→78, 74→75, 13→14, enum-tail, fixture/body, last-pending-key, adjacency and signature pins accounted for by the listed files/rows. The original prefix and Crop→Video / frames→sheet guards can remain unchanged. No additional export-absence assertion was established; ordinary TypeScript `export` keywords and OpenAPI-export tests are not absence pins. Building before the built-server Red suite is necessary and is included.

## Q10 — Output values

Accepted for the service/API success and exception paths: id-only export logging, fixed domain refusals, owned destination only in the successful path response, and masked encode/replace/probe/database failures. The current mapped-503 API handler does not print exception causes. AC-136.15 builds HealthService and includes the requested positive-control marker check over bodies/ring/stdout/stderr. F4 identifies the uncovered MCP unknown-field path; the union masks an invalid format value in the independent probe.

## Q11 — Eval and D-608

The real/meta distinction is accurately supported by describe receipt lines 13–15 and 667–683. A/B/C and S13/S14 are coherent; C exits without consulting run/key files, while A/B require a ruling and all selected runs. The brief's ten-slide count is stale against the seed script's 24 slides; this does not alter the one-hour task or require a finding.

The checker binds source id/source hash, answers, successful call counts and refused actions, but F2 disproves the t3 deliverable oracle. t1/t2 require the specified answer and call counts; they do not independently prove that the agent opened a particular view or used a narrower second span. Fresh prompt-only agents are instructed not to read the key, sibling files or repository. This is instruction-based isolation: the harness checks action membership and the lexical root prefix, not `args.path` confinement or an OS sandbox. Do not describe it as enforced file-read isolation. Inspection found no external-network/upload call in the intended eval path; its transport is the intentional isolated loopback backend. No eval/model run was performed by this reviewer, and D-608 is not decided here.

## Q12 — Red, identity and safety

Accepted the row-1 stubs, assertion-first exception recording, Python/Vitest require sets, build-before-Red and immutable Green expectations. Schema names listed in DECLARED_NEW are not imported by the type-only row; route tests can fail on status assertions without importing absent schemas. Patches must assert new names first as specified. New tests are LF and edits preserve existing endings; the byte-hash-guarded UI file is outside scope. The gate's allowed paths cover the target sources/tests, scripts, grouping and project artifacts. Status writes are explicitly restricted to MEU-136 and followed by render/diff checks.

Identity binds code/tests/config/runtime, FFmpeg/font and the plan-local executable scripts; the selftest demonstrates stale-evidence rejection when bound files change. The before/after comparison and fail-fast gate are present. Baseline's unruled D-608 refusal and A/B/C fixtures read the plan decision block. All three permitted selftests passed independently. Production suites and execution gates remain not_run by instruction. Review probes used synthetic images/temp fixtures only; no repository cache was generated intentionally and no video was opened.

## Checklist Results

| Check | Result | Observation |
|---|---|---|
| PR-1–PR-3: alignment, unstarted state, task ownership | pass | Manual plan/task and MEU-by-id inspection; HEAD 2832e3d. |
| PR-4: behavioral validation realism | fail | F1's destructive conversion is not caught by mode assertions; F2 accepts absent JPEG behavior. |
| PR-5–PR-7: source basis, correction readiness, scope | pass | Named spec/design/grouping/decisions trace the export and eval; supplied exclusions respected. |
| PR-8: concrete control reachability/negative oracle | fail | F2's three negative output fixtures all pass the real checker. |
| PR-9: contract meaning | pass | Named contracts identify intended behavior; no materially ambiguous competing delivery rule established. |
| Red-check selftest | pass | 44 fixtures, 13 positive / 31 negative, 0 wrong; exit 0. |
| Identity selftest | pass | 0 failures; exit 0; scratch fixture only. |
| Eval-check selftest | pass | 0 wrong; exit 0. This does not invalidate F2's independent counterexamples. |
| Product tests / full gate / live eval | n/a | Prohibited for this read-only planning review. |

```json
{"schema_version":"evidence.v1","check_id":"review-high-depth","command":"rtk proxy python C:/Temp/av-kit/s64/review/high_depth_probe.py","cwd":"P:/av-kit","scope":"EXPORT_ENCODE on synthetic I;16 PNG","phase":"targeted","exit_code":0,"result":"fail","tested_state":"HEAD 2832e3d plus working-tree Session 64 plan, round 1; Pillow 13.0.0","output":"Source samples [0,32768,65535]; full-range 8-bit reference [0,128,255]; JPEG and WEBP decoded samples [(0,0,0),(255,255,255),(255,255,255)]. PNG retains [0,32768,65535].","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"review-eval-oracle","command":"rtk proxy python C:/Temp/av-kit/s64/review/eval_oracle_probe.py","cwd":"P:/av-kit","scope":"Actual eval-check.py check_run(t3) on isolated fixtures","phase":"targeted","exit_code":0,"result":"fail","tested_state":"HEAD 2832e3d plus working-tree Session 64 eval-check.py, round 1","output":"Positive JPEG 1280x720: PASS. PNG 1280x720: PASS. JPEG 16x16: PASS. 12-byte non-image: PASS. All retain source hash and exact reported byte count; response dimensions claim 1280x720.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"review-schema-and-modes","command":"rtk proxy python C:/Temp/av-kit/s64/review/review_probes.py","cwd":"P:/av-kit","scope":"Proposed Pydantic schema, Pillow mode conversions and warning threshold","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus working-tree Session 64 plan, round 1","output":"Omitted numeric defaults accepted; explicit null and bool refused; StrictInt refuses 64.0/80.0. All twelve modes save after the prescribed conversions. 100000000 pixels produce DecompressionBombWarning without an exception. LAB managed conversion returns an sRGB profile.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"review-mcp-schema","command":"rtk proxy python -c \"import subprocess; p=subprocess.run(['node','C:/Temp/av-kit/s64/review/zod_probe.cjs'],capture_output=True,text=True); print(p.stdout,end=''); print(p.stderr,end=''); raise SystemExit(p.returncode)\"","cwd":"P:/av-kit","scope":"Current capture union extended in memory with exact planned export Zod member; no server","phase":"targeted","exit_code":0,"result":"fail","tested_state":"HEAD 2832e3d, installed Zod/TypeScript, working-tree Session 64 EXPORT_MCP contract","output":"Integral 64.0/80.0 accepted. Invalid format path value gives Invalid input. Extra key C:/private-marker/source.png gives Unrecognized key containing the complete marker path.","fresh":true}
```

For the three selftests, actual commands were `rtk proxy python docs/execution/plans/2026-11-11-capture-export-copy/red-check.py --selftest`, the same with `identity.py`, and the same with `eval-check.py`. Each ran with `PYTHONDONTWRITEBYTECODE=1` and TMP/TEMP under `C:/Temp/av-kit/s64/review`, preserved exit 0 and produced the decisive results above. Read/sweep receipts are under `C:/Temp/av-kit/s64-review-*.txt`; durable decisive output is embedded here.

## Verdict

`changes_required` — correct F1's destructive depth conversion and F2's demonstrated missing-deliverable false-pass through `/plan-corrections`, then recheck. There is no Critical finding. D-608 remains open for Mat; this review neither selects an option nor authorizes execution. F3/F4 are non-blocking behavior observations. The ordinary export pipeline, source ownership, naming, size construction, wiring and pin inventory are otherwise coherent.

## Corrections Applied (2026-11-11)

Written by the coordinator (Claude Code), not the reviewer. Plan cites are to `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md` as it reads for the recheck, and task cites to `task.md` in the same folder. Only plan files and `eval-check.py` changed; no product code, test or status file did.

- **F1, fixed, pending verification.** `EXPORT_ENCODE` (plan :122) now maps 16-bit gray itself before any 8-bit encode (new D-619, plan :555-570).
  - The modes are `EXPORT_DEPTH_MODES = ("I;16", "I;16L", "I;16B", "I;16N", "I")`. `_depth_to_l` maps each value `v` to `(2 × v × 255 + 65535) // (2 × 65535)`, clamped to 0 to 255, so 0, 257, 32768 and 65535 become 0, 1, 128 and 255.
  - The map applies for JPEG and WebP, for mode `I`, and for a PNG resized with a transparency key. With a key, the alpha is exact: 0 where `v` equals the key. Otherwise PNG keeps `I;16`.
  - The behaviour is stated at plan :108, and Files Modified names the new functions (plan :249, task :61).
  - AC-136.4 (plan :206) now checks pixel values, not modes:
    - an exhaustive map test over 65,536 values with 0 mismatches;
    - the clamp of an `I` image holding -5 and 70000;
    - a four-block 256×64 `I;16` source exported at its own size and at `max_edge` 128, with JPEG and WebP block centres 0, 1, 128 and 255 within 2;
    - PNG unchanged (unresized exact, resized within 1);
    - a keyed PNG resize to `LA`;
    - "the 32768 block is never 255 in any output".
  - Receipt `C:/Temp/av-kit/s64-plan-depth-probe.txt`:
    - `direct RGB [(0, 0, 0), (255, 255, 255), (255, 255, 255), (255, 255, 255)]` reproduces the finding;
    - `to_l [0, 1, 128, 255] want [0, 1, 128, 255]`;
    - `exhaustive 0..65535 mismatches 0`;
    - `key 0 LA px [(0, 0), (1, 255), (128, 255), (255, 255)]`;
    - `JPEG mid 129`.
  - The two siblings that already clip `I;16`, `_encode_view` and `bake`, are raised, not fixed (Out of Scope, plan :281; H1-6, task :75). A marked 16-bit shot therefore exports its clipped bake, as plan :108 says.
- **F2, fixed, pending verification.** `eval-check.py`'s t3 check now decodes the exported file with Pillow. The run passes only when:
  - the file sits directly in `ROOT/inbox`;
  - Pillow decodes it as `JPEG`;
  - the decoded size equals the reported width and height.

  The response alone no longer vouches for the file. The checker's docstring and plan :93 and :129 say so.
  - The selftest now writes real image fixtures. The good JPEG passes.
  - Each of these is refused, each by its own rule, with the `refused by:` line printed:
    - a PNG claiming JPEG;
    - a 16×16 JPEG;
    - a 12-byte non-image;
    - a JPEG outside the inbox;
    - a size mismatch;
    - a missing file.
  - Receipt `C:/Temp/av-kit/s64-plan-eval-check-selftest-r1d.txt` ends `eval-check selftest: 0 wrong`, `exit=0`.
  - The first run after the change, `…-r1c.txt`, was 3 wrong with exit 1. That was the selftest's own byte-count placeholder sitting inside an escaped JSON string; it was fixed before r1d (plan :93).
- **F3, fixed, pending verification.** The second transport difference is documented in `EXPORT_MCP` (plan :125) and in D-610 (plan :407).
  - REST's `StrictInt` refuses JSON `64.0` and `80.0`. MCP receives them as the JavaScript numbers 64 and 80 and sends `64` and `80`.
  - D-610 records why REST keeps `StrictInt`: lax int would also take the string `"64"`.
  - Both transports are tested:
    - AC-136.14 (plan :216) adds `max_edge` `64.0` and `quality` `80.0`, sent as raw JSON text, to the REST refusals;
    - AC-136.17 (plan :219) parses `{"action":"export","id":"cap-1","format":"jpeg","max_edge":64.0,"quality":80.0}` with `JSON.parse`, and checks that the fetch body text holds `"max_edge":64` and `"quality":80`.
  - Receipt `C:/Temp/av-kit/s64-plan-strict-probe.txt`: `fixed max_edge 64.0: (accepted)` and `JSON.parse('64.0') -> 64 true`.
- **F4, fixed for export, pending verification; other actions raised.** `EXPORT_MCP` (plan :125, boundary row :192) is now
  `z.strictObject({...}, {error: (issue) => (issue.code === "unrecognized_keys" ? EXPORT_UNKNOWN_KEY : undefined)})`,
  with `EXPORT_UNKNOWN_KEY = "export accepts only action, id, format, max_edge and quality"` (new D-620, plan :571-586). `NO_RAW_OUTPUT` (plan :128) says so.
  - AC-136.17 checks:
    - the marker key gives exactly that text, absent from the tool result and from stderr;
    - a positive control sends the same key to `crop` and finds the marker echoed.
  - Receipt `C:/Temp/av-kit/s64-plan-strict-probe.txt`:
    - `real crop extra key: Unrecognized key: "C:/private-marker/source.png" | marker=true`;
    - `fixed extra key: export accepts only action, id, format, max_edge and quality | marker=false`;
    - the missing-format, `max_edge` 63, fraction, enum and null refusals keep zod's own text.
  - The other strict actions still name an unknown key, to the calling client only and never in a log. That is raised, not fixed (Out of Scope, plan :282; H1-6, task :75).
- **Q5 note, fixed.** When `_to_srgb` converts a CMYK, YCbCr or LAB source, the profile kept is the sRGB one it returns, never the source's (plan :105, :122; D-614, plan :473).
- **Q7 note, fixed.** The deadline inventory is corrected and export takes the longer MCP timeout (D-616, plan :505).
  - Row 1 (plan :137) says an export holds the lock through its own encode.
  - Row 3 (plan :139) says `MAX_IMAGE_PIXELS` 89,478,485 is a warning and the refusal is above 178,956,970.
  - Row 4 (plan :140) adds the cap-edge timings.
  - From `C:/Temp/av-kit/s64-plan-cap-probe.txt`:
    - `open+load: 0.36 s`;
    - `full-size WEBP: 82.53 s`;
    - `full-size JPEG: 0.38 s`;
    - `full-size PNG: 2.00 s`;
    - `LANCZOS to 1920: 0.78 s`;
    - `1920 WEBP q90: 0.32 s`;
    - `178962432 refused: DecompressionBombError`;
    - `178935126 opened (warning only)`.
  - Because the worst case passes 30 s, `export` joins the `ADD_TIMEOUT_MS` selection with crop, frames and sheet (plan :125, :143; task :61). It gets the comment line `// EXPORT_MCP under D-616 A: a full-size WebP at Pillow's pixel refusal edge encodes in about 83 s.`
  - AC-136.17 checks the timeout as AC-135.18 does for sheet.
  - Plan :143 says 120 s is not a bound either: the server still writes the export whole or discards it whole, and no enforced deadline is added, as with crop.
- **Q11 note, fixed.**
  - Plan :90 says 24 slides of 150 s each.
  - Plan :91 says the harness enforces only the action allowlist and the root prefix. Each run is kept from the key, its siblings and the repository by its prompt's instructions, not by a sandbox.
- **Decision vocabulary.** The plan now runs from D-608 to D-620. D-619 and D-620 are autonomous, two-way and at stage planning, with `human_message_reference: null`. The ranges are updated at plan :60, :87 and :366 and task :79 and :84. D-608 is still Mat's and unruled.

### Verification

- `C:/Temp/av-kit/s64-plan-correct-r1.txt`, exit 0: `implementation-plan.md: 29 edits, 7 whole lines` and `task.md: 5 edits; not present: []`. Each edit was required to match exactly once. Both files were LF before and after (0 CR bytes, measured with Python).
- `C:/Temp/av-kit/s64-plan-task-lint-r1.txt`, exit 0: `OK: 27 row(s); 10-column table (with builder_model); 25 row(s) fully checked`.
- `C:/Temp/av-kit/s64-plan-decision-probe-r1.txt`, exit 0: the plan-and-grouping set reads `19 decisions`, with `D-619 planning implementation-plan.md` and `D-620 planning implementation-plan.md`.
- `C:/Temp/av-kit/s64-plan-eval-check-unruled-r1.txt`, exit 1, as intended: `FAIL D-608: unruled`.
- `C:/Temp/av-kit/s64-plan-eval-check-selftest-r1d.txt`, exit 0: `eval-check selftest: 0 wrong`.
- `C:/Temp/av-kit/s64-plan-census-r1-sites.txt`, exit 0 (`C:/Temp/av-kit/s64/census_r1.py`):
  - It ends `Blast-radius census: 10 values changed, 33 variants swept, 67 sites found, 29 updated, 38 confirmed consistent.`
  - Each kept site is listed with its text.
  - The sweep of stale wording after the edits is `C:/Temp/av-kit/s64-plan-census-r1.txt`. In it, `ten slides`, `stays on the 30 s`, `far under 30 s`, `not in ADD_TIMEOUT_MS`, `D-608 to D-618` and `registry.ts:392` are absent.
  - The remaining hits of `30 s default` and `.strict()` are the new D-616 reasoning and D-620's F4 precedent.
- The pre-correction copies are `C:/Temp/av-kit/s64/implementation-plan.pre-r1.md` and `C:/Temp/av-kit/s64/task.pre-r1.md`.

Verdict set to `corrections_applied` for the round 2 recheck. Only an independent recheck can set `approved`.

## Recheck (2026-11-11)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | open | partial |
| F2 | open | fixed |
| F3 | open | fixed |
| F4 | open | fixed |

### Confirmed Fixes

- **F1, ordinary grayscale path:** `implementation-plan.md:108`, `:122`, `:206`, `:555`. The depth map preserves all 65,536 values against the stated half-up reference, clamps out-of-range `I`, and gives the four opaque block centres 0, 1, 128, 255 in JPEG/WebP, before and after shrinking. Native PNG preserves the four 16-bit centres. The original direct-conversion clip is removed. The new keyed-transparency branch still needs correction below.
- **F2:** `eval-check.py:92`, `:190`, `:195`, `:302`; `implementation-plan.md:93`, `:129`. The checker now loads the actual file, requires JPEG, checks decoded dimensions against both the response and the minimum edge, and confines the resolved file's parent to the run inbox. The round 1 PNG, 16x16 JPEG and non-image counterexamples are all refused; the real JPEG positive control passes. New selftest fixtures refuse for their own named rules, including outside-inbox and exactly-500,000-byte outputs.
- **F3:** `implementation-plan.md:125`, `:216`, `:219`, `:423`. The integral-float representation difference is explicit. REST's raw `64.0`/`80.0` refusals and MCP's acceptance followed by integer JSON serialization are both specified and independently reproduced.
- **F4:** `implementation-plan.md:125`, `:128`, `:219`, `:571`; `mcp-server/src/toolsets/registry.ts:360`. The planned `z.strictObject` error callback gives exactly `EXPORT_UNKNOWN_KEY` through the real capture union and registry-style issue join. Other refusals match the bare schema's messages. The crop marker positive control still echoes the same key, making export's absence assertion meaningful.
- **Q5/Q7/Q11:** `implementation-plan.md:105`, `:122`, `:137`, `:143`, `:510`, `:90`, `:91`; `task.md:61`. The returned sRGB profile, warning/refusal thresholds, measured encode timings, 120-second client timeout and instruction-based eval isolation are now described accurately. The seed has 24 slides of 150 seconds each. Neither the timeout nor the harness is presented as an enforced server deadline or file-read sandbox.

### Remaining Findings

- **F1 — partial; High severity, High confidence, blocking; behavior; deliverable.** `EXPORT_ENCODE` still loses the stored midtone on a valid keyed 16-bit gray PNG when shrinking to JPEG, and its new PNG test cannot pass as written. **Violates AC-136**, specifically AC-136.4 and the alpha-drop/stored-colour contract at `implementation-plan.md:106`. At `implementation-plan.md:122` / D-619 `:560`, the 32768 transparency key is turned into `LA` **before** LANCZOS; JPEG drops alpha **after** LANCZOS. Pillow 13.0.0 resizes `LA` using premultiplied alpha: the centre `(128, 0)` becomes `(0, 0)`. On the exact four-block fixture of `:206`, a 256x64 source shrunk to 128x32 therefore produces a JPEG centre `(0, 0, 0)` instead of stored grey 128. The PNG remains valid and transparent, but its centre is `(0, 0)`, not the required luminance 128 within 1. Thus the proposed Green cannot satisfy the immutable AC-136.4 assertion even with an otherwise correct alpha-aware PNG resize. **Recommendation:** for JPEG, discard alpha before resampling the mapped luminance/RGB, so the stored colour survives; for PNG/WebP keep alpha-aware resampling, assert the transparent block's alpha and the opaque blocks' luminance, and do not require hidden luminance to survive a fully transparent resize. Remove any consumed `transparency` key from the resulting alpha-bearing image's save metadata. Add the keyed-and-shrunk JPEG regression beside the opaque ramp. This is the remaining branch of F1 under `EXPORT_ENCODE`, not a second finding for the same depth correction. Status: open.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### R1 — Depth and encoding

Accepted the formula, clamping, conversion order for managed colour/depth/palette/1-bit modes, native `I;16` PNG resize without a key, and mapping of `I` or keyed resized PNG to an alpha-bearing 8-bit image. Independent raw PNG fixtures confirm that 16-bit grayscale opens as `I;16`, grayscale-and-alpha as 8-bit `RGBA`, and RGB as 8-bit `RGB`; `:108` is true. The opaque four-block fixture meets the lossy tolerance of 2 and resized native PNG tolerance of 1, with exact centres in this probe, and would detect the round 1 clip. The keyed PNG's hidden-luminance requirement is unsound, and the prescribed alpha-before-JPEG-resize order visibly blackens that block. F1 therefore remains partial. This is a synthetic Pillow reproduction of the plan, not a run of unimplemented adapter code.

### R2 — Eval deliverable oracle

Accepted F2's correction. The original real-JPEG positive control passes and all three original false-pass fixtures fail for decoded format/dimensions. The new tests also distinguish an outside-inbox JPEG, an output at the byte limit, altered source bytes and a different source id. The selftest prints each refusal rule, so the new decode negatives no longer fail because of an unrelated byte-count fixture error. `:93` and `EVAL_RUN` at `:129` match the checker. A/B still require the selected runs and Mat's ruling; C bypasses run/key files and explicitly reports not-run. No live eval was performed and D-608 remains unruled.

### R3 — Transports and unknown-key text

Accepted F3 and F4. A standalone copy of the specified Pydantic input rejects the two raw integral floats and accepts ordinary integers/default omission. The planned Zod member, appended in memory to the current real capture union, accepts parsed integral floats and serializes the body as `{"format":"jpeg","max_edge":64,"quality":80}`. Its unknown-key issue joins to exactly the fixed text. Missing-format, range, fractional, enum, null and boolean refusals retain the original Zod text. Crop's same marker key remains visible in the positive control. The new export-specific `NO_RAW_OUTPUT` statement is supported; the explicitly excluded existing actions are not reopened.

### R4 — Notes

Accepted Q5: `_to_srgb` returns the replacement sRGB profile after managed conversion (`adapter.py:288-300`); the kept profile is that returned profile, with no original CMYK/LAB profile reattached. As in the current helper, an unmanaged fallback returns no profile.

Accepted Q7 against the supplied cap receipt: 89,478,485 is the warning threshold, refusal is above 178,956,970, 178,935,126 pixels opened with a warning, and 178,962,432 were refused. The quoted 82.53-second full-size WebP measurement supports joining `ADD_TIMEOUT_MS`; it is a measured case, not a universal worst-case bound. `:143` correctly disclaims a 120-second server bound and recognizes lock contention. AC-136.17 now checks the timeout like AC-135.18. Targeted inspection of current timeout tests and the plan-local scripts found no active post-baseline literal selection pin that this addition breaks. `baseline.ps1:130` checks the old selection at row 0 only; it is not rerun as a Green gate.

Accepted Q11: `eval-seed.py:36-37` establishes the slide count/duration, and `eval-harness.ts:58-64`, `:169-185` checks the lexical root prefix and action allowlist without confining a call's `path`. The corrected text describes prompt instructions, not OS enforcement.

### R5 — Correction regressions and scope

No additional blocker found beyond F1's keyed-alpha branch. The `--require` sets still cover Python AC-136.2-.16 and MCP .17-.18. The new private adapter names are Green implementation details, not row-1 imports: a Red test must import the existing module and assert availability before accessing an absent helper, rather than add a missing-symbol import. The assertion-first rule at `:319` and the checker still reject collection/missing-name failures; none is required by the revised AC. Similarly, MCP tests can compare the fixed literal without importing an absent new constant. There is no need to weaken `DECLARED_NEW` to admit setup failures.

The changed private names remain inside already enumerated source files (`:247`, `:250`; `session-gate.ps1:45`, `:49-50`), and the new tests remain in the allowed scope. Pin counts, action order, source membership and cross-family AC references remain coherent. All ten plan-folder files excluding `__pycache__` contain no CR bytes. Identity's selftest still binds executable eval scripts and rejects stale evidence when bound inputs change. Stop conditions and D-608's human gate are preserved. D-619's scaling choice is sound; its alpha/resize application needs the F1 correction. D-620 is supported by the actual union probe. The decision log has exactly D-608 through D-620; plan/task vocabulary ranges agree. The historical `D-608 to D-625 ... free` receipt describes availability at planning time, not the chosen range.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| R1 / F1 depth preservation and satisfiable pixel assertions | fail | Full-range opaque mapping passes; keyed resized PNG centre is `(0,0)` against required `(128,0)`, and JPEG centre is black instead of grey 128. |
| R2 / F2 real output and independent negative fixtures | pass | Round 1 positive passes; PNG, small JPEG and non-image fail decoded checks; selftest 0 wrong, including path/byte/source controls. |
| R3 / F3-F4 transport and refusal boundaries | pass | REST integral floats refused; MCP sends integers; fixed unknown-key message, unchanged other messages, crop marker positive control. |
| R4 profile/deadline/isolation notes | pass | Source inspection and supplied cap receipt agree with the corrected statements and timeout selection. |
| R5 Red/scope/pins/identity/stops | pass | No additional regression established; original fail-closed checker and scoped paths preserved. |
| Red-check selftest | pass | 44 fixtures, 13 positive / 31 negative, 0 wrong; exit 0. |
| Identity selftest | pass | 0 failures; exit 0; temporary fixtures only. |
| Eval-check selftest | pass | 0 wrong; exit 0; each negative's refusing rule printed. |
| Product suites, session gate, seed/harness/live eval | n/a | Not run, as required for this read-only review. |

Tested state: HEAD `2832e3d` plus the untracked Session 64 plan folder `docs/execution/plans/2026-11-11-capture-export-copy/` and `.agent/context/handoffs/2026-11-11-capture-export-copy-plan-critical-review.md`. Other sessions' dirty paths are outside this review. `.claude/settings.local.json` is ignored on the host through `<HOME>/.config/git/ignore`, which the sandbox does not read; it was not opened or counted. Repository files were only read. No network request, video read, product-suite execution or repository write was made. Every probe and new image was written under `C:/Temp/av-kit/s64/review`.

Decisive fresh evidence (all Python commands used `PYTHONDONTWRITEBYTECODE=1`; selftests also set TMP/TEMP to the review directory):

```json
{"schema_version":"evidence.v1","check_id":"r2-depth-alpha","command":"rtk proxy python C:/Temp/av-kit/s64/review/alpha_assert_r2.py","cwd":"P:/av-kit","scope":"EXPORT_ENCODE and AC-136.4 on synthetic 16-bit grayscale PNGs, Pillow 13.0.0","phase":"targeted","exit_code":0,"result":"fail","tested_state":"HEAD 2832e3d plus the two untracked Session 64 plan/review paths named above","output":"Exhaustive map mismatches 0; I clamps [0,255]. Opaque JPEG/WebP block centres [0,1,128,255], at both sizes; native PNG [0,257,32768,65535]. Keyed mapped centre (128,0); after LA LANCZOS resize (0,0), contradicting AC-136.4 L=128 +/-1. Prescribed JPEG centre (0,0,0); positive control dropping alpha before JPEG resize gives (128,128,128). Assertions proving these observations all passed.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-eval-counterexamples","command":"rtk proxy python C:/Temp/av-kit/s64/review/eval_oracle_probe.py","cwd":"P:/av-kit","scope":"Actual eval-check.py check_run(t3), round 1 counterexamples","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus the two untracked Session 64 plan/review paths named above","output":"Positive JPEG 1280x720 PASS. PNG 1280x720 FAIL only decoded JPEG format. JPEG 16x16 FAIL decoded size. Twelve-byte non-image FAIL decode format and size. Source hashes, byte counts and response dimensions otherwise match in every fixture.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-zod-union","command":"rtk proxy node C:/Temp/av-kit/s64/review/zod_r2.cjs","cwd":"P:/av-kit","scope":"Current real capture union plus exact planned export member, joined issue messages","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d, installed Zod/TypeScript, working-tree Session 64 EXPORT_MCP contract","output":"Extra key -> exactly export accepts only action, id, format, max_edge and quality. Missing format, range, fraction, enum, null and boolean messages unchanged from bare strict object. Crop positive control contains marker. Integral-float body serializes with max_edge:64 and quality:80. failures 0.","fresh":true}
```

The three actual selftest commands were `rtk proxy python docs/execution/plans/2026-11-11-capture-export-copy/red-check.py --selftest`, the same with `identity.py`, and the same with `eval-check.py`. Each preserved exit 0 and printed the results above. A separate numeric probe (`rtk proxy python C:/Temp/av-kit/s64/review/numeric_r2.py`, exit 0) reproduced `int_type` refusals for raw `64.0` and `80.0`, with integer and omission positive controls. The canonical report's original round 1 body was compared with its saved round 1 copy: unchanged apart from the allowed frontmatter verdict, with the coordinator's corrections appended.

### Verdict

`changes_required` — one High blocking finding remains: F1 is partial. F2, F3 and F4 are fixed. Correct the keyed-alpha resize order and the impossible transparent-pixel assertion, then recheck. No new independent finding is added. D-608 remains Mat's open decision; this review does not authorize execution.

## Corrections Applied (round 2, 2026-11-11)

Written by the coordinator (Claude Code), not the reviewer. Plan cites are to `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md` as it reads for the recheck. Only the plan changed in round 2; `task.md`, `eval-check.py`, product code, tests and status files did not.

- **F1, fixed, pending verification.** The resize order in `EXPORT_ENCODE` (plan :122) is corrected for every alpha source, not only the keyed 16-bit one.
  - The new step (3): JPEG runs `convert("RGB")` before any resize, so an alpha band or a `transparency` key is dropped and the stored colour shows at every size.
  - Step (2): the depth map builds an alpha band from a key only for webp and png. For jpeg the key is ignored.
  - The new step (4), for PNG and WebP before a resize: a `P`, `L` or `RGB` image with a key becomes `LA` (from `L`) or `RGBA` through Pillow's own convert, which turns the key into alpha 0. A `P` without a key becomes `RGB`, and `1` becomes `L`.
  - Step (5) says a resize keeps a fully transparent pixel's alpha 0 but not its hidden colour. That follows your recommendation not to require hidden luminance to survive a fully transparent resize.
  - Step (6): the `transparency` passed to a PNG save is read from the image being saved, never from the opened source as crop reads it (`adapter.py:458`). No key is written beside an alpha band, which removes the consumed key as you asked.
  - Step (2)'s mode list now names `I;16L`, `I;16B` and `I;16N` beside `I`, because none of them is in `_CROP_KEPT_MODES`.
  - Plan :107 and :108 say the same thing in prose.
  - D-614 (plan :473) carries the general JPEG-first order and the key rule in its chosen text, two new precedents (plan :485-486) and its reasoning (plan :490).
  - D-619 (plan :557) carries the keyed 16-bit case in its chosen text, a round 2 precedent (plan :566) and its reasoning (plan :572).
  - AC-136.4 (plan :206) replaces the keyed-PNG luminance assertion that could not pass. It now checks:
    - The fixture is built from raw little-endian bytes, and its four centres are asserted before any export. Pillow 13.0.0 writes 0 for `paste(32768)` into `I;16`; the probe hit this before its own fixture was fixed.
    - With a key on the 32768 block, at its own size and at `max_edge` 128:
      - JPEG is `RGB` with centres within 2 of 0, 1, 128 and 255. This is the keyed-and-shrunk regression you asked for.
      - WebP is `RGBA`, with that block's alpha 0 and the others' alpha 255 and centres within 2.
      - An unresized PNG keeps `I;16` with `transparency` 32768.
      - A resized PNG is `LA`, with that block's alpha 0, the others' luminance within 1 and no `transparency` in `info`.
    - A fully transparent block's colour is not asserted after a resize.
    - Stored colour: an RGBA source and a transparent-index P source, each with a transparent region stored as (200, 40, 40), export to JPEG at their own size and at `max_edge` 128 with that colour within 3, never black.
    - `L` keyed at 128 and `RGB` keyed at (200, 40, 40), shrunk to PNG, give `LA` and `RGBA` with alpha 0 on the keyed region and no `transparency`.
    - The control column names the fixture centres asserted before export and the stored colour under alpha 0.
  - Receipt `C:/Temp/av-kit/s64-plan-alpha-probe-r2.txt` (`C:/Temp/av-kit/s64/probe_alpha_r2.py`) ends `probe: 0 unexpected`, `exit=0`:
    - `old order: keyed block blackened in JPEG: [(0, 0, 0), (1, 1, 1), (0, 0, 0), (255, 255, 255)]` reproduces your finding;
    - `new JPEG keyed (128, 32): [0, 1, 128, 255]`;
    - `PNG keyed resize LA: ('LA', [(0, 255), (1, 255), (0, 0), (255, 255)])`;
    - `WebP keyed resize RGBA: ('RGBA', [(0, 0, 0, 255), (1, 1, 1, 255), (0, 0, 0, 0), (255, 255, 255, 255)])`;
    - `old order: RGBA transparent region black in shrunk JPEG: [(10, 201, 10), (0, 0, 2), (1, 0, 4), (10, 201, 10)]`;
    - `new JPEG RGBA (128, 32) shows stored colour: [(8, 202, 10), (200, 40, 40), (199, 41, 40), (10, 201, 10)]`;
    - `new JPEG P shrunk shows palette colour: [(8, 202, 10), (200, 40, 40), (199, 41, 40), (10, 201, 10)]`.
  - Receipt `C:/Temp/av-kit/s64-plan-key8-probe-r2.txt` (`C:/Temp/av-kit/s64/probe_key8_r2.py`, Pillow warnings raised as errors) ends `probe: 0 unexpected`, `exit=0`:
    - `L keyed shrink PNG has no transparency key: ('LA', {})`;
    - `RGB keyed shrink PNG has no transparency key: ('RGBA', {})`;
    - `RGB keyed JPEG shrink shows stored colour: [(8, 202, 10), (200, 40, 40), (199, 41, 40), (10, 201, 10)]`.

### Verification

- `C:/Temp/av-kit/s64-plan-correct-r2.txt`, exit 0: `implementation-plan.md: 12 edits, each matched once; LF only; 631 lines`. The pre-correction copy is `C:/Temp/av-kit/s64/implementation-plan.pre-r2.md`.
- `C:/Temp/av-kit/s64-plan-census-r2.txt`, exit 0 (`C:/Temp/av-kit/s64/census_r2.py`): `Blast-radius census: 5 values changed, 19 variants swept, 27 sites found, 16 updated, 11 confirmed consistent; 0 stale phrases left.` Each kept site is listed with its text. The stale sweep finds 0 hits in the plan and in `task.md` for `(that is, \`I\`)`, `P and 1 converted before a resize`, `(with its \`transparency\`)` and the old keyed-PNG and Limits wording.
- `C:/Temp/av-kit/s64-plan-task-lint-r2.txt`, exit 0: `OK: 27 row(s); 10-column table (with builder_model); 25 row(s) fully checked`.
- `C:/Temp/av-kit/s64-plan-decision-probe-r2.txt`, exit 0: the plan-and-grouping set reads `19 decisions`. No decision was added; D-614 and D-619 changed in place.
- The round 2 review was validated at `C:/Temp/av-kit/s64-plan-review-state-r2-temp.json` and copied byte for byte to canonical. `C:/Temp/av-kit/s64-plan-review-state-r2.json` was rebuilt there: `round 2 of 3; verdict=changes_required; open findings=1`.

Verdict set to `corrections_applied` for the round 3 recheck. Only an independent recheck can set `approved`.

## Recheck (2026-11-11, round 3)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | partial | fixed |
| F2 | fixed | fixed |
| F3 | fixed | fixed |
| F4 | fixed | fixed |

### Confirmed Fixes

Plan references below mean `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md`; script references are in that folder unless qualified.

- **F1:** `implementation-plan.md:107`, `:108`, `:122`, `:206`, `:478`, `:488`, `:562`, `:572`. The depth map now ignores a key for JPEG, and JPEG drops alpha before LANCZOS for every source mode. The keyed 16-bit JPEG centre is 128 at both sizes; RGBA and transparent-P centres retain stored (200,40,40) within 3. The old order independently reproduces black centres. Keyed PNG/WebP instead retain alpha-aware resampling. AC-136.4 no longer requires hidden colour to survive that resampling. These resolve the outstanding round 2 F1; the separate keyed-1 omission is F5 below.
- **F2:** `eval-check.py:92`, `:190`, `:195`, `:198`; plan `:129`, `:221`. Actual JPEG decoding, decoded dimensions and inbox confinement remain in force. Fresh selftest: real JPEG positive passes; PNG claiming JPEG, 16x16 JPEG claiming 1280x720, and non-image each fail the intended decode rule; byte-limit, source and outside-inbox negatives also fail. `eval-check selftest: 0 wrong`, exit 0.
- **F3:** plan `:124`, `:125`, `:216`, `:219`. The REST integral-float refusal and MCP integer serialization remain explicit. These contracts and tests are byte-identical to their accepted pre-round-2-correction text; the alpha-order edit does not affect them. No fresh Pydantic/Zod runtime result is claimed.
- **F4:** plan `:125`, `:128`, `:219`, `:579`. The export-specific fixed unknown-key error, unchanged other errors and crop marker positive control remain intact and unchanged from round 2. The fixed text is still attached to the actual proposed strict export member, rather than to unrelated actions. No fresh Zod runtime result is claimed.

### Remaining Findings

None.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F5 | High | yes | behavior | `EXPORT_ENCODE` step (4) consumes keys before resizing only for P, L and RGB; a keyed 1-bit PNG instead becomes plain L and is resized with the key still attached. A valid 256x64 mode-1 PNG of alternating opaque-black and transparent-white columns, shrunk to 128x32, exports as entirely opaque grey: PNG mode L and WebP mode RGB, centre RGBA (127,127,127,255). Converting the source key to alpha before LANCZOS yields (0,0,0,127), with transparency retained in both formats. This changes the deliverable's appearance on a dark background and loses transparency across the whole patterned image. Scan and ordinary import preserve this valid input. High confidence; subject deliverable. Violates AC-136, specifically AC-136.4's encoding/alpha contract and the source-as-shown goal. This is a different PNG/WebP output failure from F1's corrected JPEG midtone loss. | `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md:122`; `:206`; `:478` | Include keyed mode 1 in PNG/WebP key-to-alpha conversion before LANCZOS, using the source's decoded key. Add this real 1-bit tRNS fixture and assert decoded alpha/visible colour after shrinking; retain JPEG's RGB-before-resize order and native unresized PNG behavior. | open |

### R1 — Encoding and F1

Accepted the corrected JPEG order for the keyed 16-bit ramp, RGBA, transparent P, keyed L/RGB and LA, at original size and half size. All 65,536 mapped values match the specified integer formula; out-of-range I clamps to 0 and 255. JPEG/WebP opaque ramp centres are exactly 0,1,128,255 in the probe. PNG's unresized I;16 values and its 32768 key remain exact. Resized keyed PNG is LA with alpha 0 at the keyed block's centre and alpha 255 with correct luminance at opaque centres; keyed WebP is RGBA with the same alpha assertions. Converted L/RGB/P alpha images carry no stale transparency key, and no tested save has both an alpha band and a key or raises a save error.

Step (6) correctly reads transparency from the final image: the key consumed by conversion cannot be reattached from the opened source, unlike crop's no-resampling path at `packages/infrastructure/src/avkit_infra/capture/adapter.py:458`. It does not by itself repair F5's scalar resize of keyed mode 1.

AC-136.4's new keyed-JPEG assertion fails the round 2 order (centre 0) and passes the corrected order (centre 128). Raw little-endian fixture bytes plus source-centre assertions prevent a false fixture caused by paste. Tolerances of 2 for these broad grayscale block centres, 3 for the stored-red JPEG centre and 1 for native-depth PNG resizing are satisfied at the default quality 90; they are not promises for arbitrary content or every quality. Hidden colour under alpha 0 is correctly left unasserted after resizing. The specific F1 assertions are now satisfiable.

Plan `:108` and D-619 are supported by the depth probes. Plan `:107` and D-614 correctly describe the repaired JPEG path and the named P/L/RGB key paths, but their general transparency claim is not yet true for every inbox mode: F5's keyed-1 branch loses all transparency on this shrink. No additional clipping, blackening or refused-save case was established. Alpha-0/full-alpha observations above refer to interiors of broad regions; resampled boundaries may legitimately have partial alpha.

### R2 — Regressions and earlier fixes

Accepted the 16-bit map and native I;16 PNG, the replacement sRGB ICC profile after managed LAB conversion (Q5; plan `:105`, `:122`; adapter `:288-300`), and the unchanged unresized PNG mode list L, LA, RGBA, P and I;16. JPEG is RGB. The alpha-bearing WebP fixtures decode RGBA except for F5, where the plan's keyed-1 resize has already destroyed the alpha before saving. F5 is a genuine output defect, not a request to deepen an already-corrected checker or alter a label.

The Files Modified block is unchanged from the pre-round-2-correction plan (`:240-259`); the changed encoding names remain inside the listed adapter and its new test file. `session-gate.ps1:45`, `:49-50`, `:52` still permit the affected source/test paths. Row 2a (`task.md:59`) still requires exactly `test_ac_136_2` through `test_ac_136_16`; MCP .17/.18 stay in row 2b. No Red import/setup-failure relaxation is introduced by the correction. F2, F3 and F4 remain fixed as recorded above.

D-608 remains unruled (`implementation-plan.md:375-391`). A still selects six eval runs, B three, and C explicitly reports not-run without consulting run/key files (`eval-check.py:209-214`); the new encoding defect exists independently of that choice. The decision ids remain D-608 through D-620. No decision was made for Mat and no execution was authorized.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| F1 correction and updated AC-136.4 | pass | Independent Pillow 13.0.0 probe: 65,536 mappings, zero mismatches; old keyed JPEG centre 0, corrected centre 128; keyed PNG/WebP block alpha and stored-red JPEG assertions pass. |
| R1 all inbox modes preserve intended PNG/WebP transparency | fail | F5: a valid keyed mode-1 PNG shrinks to fully opaque grey in both formats; alpha-aware encoded controls retain centre alpha 127. |
| R2 depth, profile, mode-list, scope and Red requirements | pass | Native I;16 and managed sRGB checks pass; Files Modified unchanged; gate paths include affected files; row 2a requires .2 through .16. The mode-1 transparency exception is isolated in F5. |
| F2 actual eval output oracle | pass | Fresh `eval-check.py --selftest`, exit 0, 0 wrong; the three original decode counterexamples are refused. |
| F3/F4 contract regression check | pass | Exact accepted-text comparison for EXPORT_ROUTE, EXPORT_MCP, NO_RAW_OUTPUT and AC-136.14/.17/.18; no fresh transport-runtime claim. |
| D-608 and review boundary | pass | Pending human ruling preserved; A/B/C paths read; all 27 task rows remain unstarted; repository files were read only. |
| Product suites, baseline/session gate, seed/harness, live eval, videos and network | n/a | Not run or accessed, as instructed. |

Tested state: HEAD `2832e3d` plus the untracked Session 64 plan folder `docs/execution/plans/2026-11-11-capture-export-copy/` and `.agent/context/handoffs/2026-11-11-capture-export-copy-plan-critical-review.md`. Other sessions' dirty paths are outside this review. `.claude/settings.local.json` is ignored on the host through `<HOME>/.config/git/ignore`; it was neither opened nor counted. New probes and synthetic images are under `C:/Temp/av-kit/s64/review`; the rolling report and receipts are under `C:/Temp/av-kit`. All Python probes used `PYTHONDONTWRITEBYTECODE=1`; the selftest used TMP/TEMP under the review directory. No repository file was edited. This is a review of the proposed encoder, not a run of an implemented export adapter.

Decisive fresh evidence:

```json
{"schema_version":"evidence.v1","check_id":"r3-encoding","command":"rtk proxy python C:/Temp/av-kit/s64/review/encoding_r3.py","cwd":"P:/av-kit","scope":"EXPORT_ENCODE executable plan reading; synthetic depth, alpha and managed-colour fixtures","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus the two untracked Session 64 paths named above; Pillow 13.0.0","output":"195 assertions passed; all 65536 mappings match; opaque JPEG/WebP centres 0,1,128,255; native PNG 0,257,32768,65535; old keyed JPEG centre 0 versus corrected 128; stored-colour and alpha blocks pass for RGBA/P/L/RGB/LA; managed LAB outputs carry replacement sRGB profile. The separate keyed-1 counterexample is recorded below.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r3-keyed-bitonal","command":"rtk proxy python C:/Temp/av-kit/s64/review/bitonal_r3.py","cwd":"P:/av-kit","scope":"F5: valid mode-1 tRNS PNG shrunk to PNG and WebP, with independent alpha-aware controls","phase":"targeted","exit_code":0,"result":"fail","tested_state":"HEAD 2832e3d plus the two untracked Session 64 paths named above; Pillow 13.0.0","output":"Source mode 1, tRNS 255, 256x64, alternating opaque black / transparent white columns. At 128x32: planned PNG mode L and WebP mode RGB, centre (127,127,127,255), alpha range (255,255). Both alpha-aware encoded controls are RGBA, centre (0,0,0,127). Assertions confirming the defect and controls passed; source SHA-256 unchanged. Inbox reachability: scan_inbox at services/capture.py:498-525 probes .png without mode conversion; orientation-1 import at :1234-1246 copies the original bytes.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r3-eval-selftest","command":"rtk proxy python docs/execution/plans/2026-11-11-capture-export-copy/eval-check.py --selftest","cwd":"P:/av-kit","scope":"EVAL_RUN deliverable oracle and ruling fixtures, synthetic images only","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus the two untracked Session 64 paths named above","output":"eval-check selftest: 0 wrong. Positive JPEG passes. PNG claiming JPEG refuses decoded format; 16x16 JPEG claiming 1280x720 refuses decoded size; non-image refuses both. Outside-inbox, exactly-500000-byte, changed-source and wrong-source-id negatives refuse. C skips every run; unruled ruling refuses.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r3-contracts","command":"rtk proxy python C:/Temp/av-kit/s64/review/contracts_r3.py","cwd":"P:/av-kit","scope":"Correction regression comparison, gate paths, Red requirement set and target identity","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus the two untracked Session 64 paths named above","output":"EXPORT_MCP, EXPORT_ROUTE, EXPORT_AUDIT, NO_RAW_OUTPUT, EVAL_RUN, EXPORT_SOURCE and EXPORT_WRITE unchanged from accepted round 2. AC-136.14/.17/.18/.19 unchanged. Files Modified unchanged; affected paths in gate. Row 2a requires exactly test_ac_136_2 through test_ac_136_16. D-608..D-620 preserved, D-608 pending. Ten plan-folder files LF. Scope and prior fixes: PASS.","fresh":true}
```

### Verdict

`changes_required` — F1, F2, F3 and F4 are fixed. One new High, High-confidence blocking behavior finding remains, F5: keyed 1-bit PNG transparency is destroyed when shrinking to PNG/WebP. Include that source mode in alpha conversion before resampling and cover it with the demonstrated fixture. No Critical finding. Intent achieved: partial as a plan. D-608 remains Mat's open decision; this review neither chooses its option nor authorizes execution.

## Corrections Applied (round 3, 2026-11-11)

Written by the coordinator (Claude Code), not the reviewer. Plan cites are to `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md` as it reads for the recheck. In round 3 the plan and `task.md` changed. `eval-check.py`, product code, tests and status files did not.

- **F5, fixed, pending verification.** In `EXPORT_ENCODE` (plan :122), step (4) now converts a keyed `1` image like `L`, before LANCZOS. It reads "a `1`, `L`, `P` or `RGB` image with a `transparency` key becomes `LA` (from `1` or `L`) or `RGBA`". A `1` without a key still becomes `L`. This follows your recommendation.
  - Probing your fixture showed a sibling problem. Pillow 13.0.0 reports some PNG keys on a different scale from the samples it decodes, so converting first is not enough for those keys:
    - For 2-bit and 4-bit gray, it scales the samples to 0 to 255 but reports the key raw (1, 3 or 15), so the key matches no pixel. That source exports fully opaque even unresized.
    - For 16-bit RGB, it keeps each sample's high byte but reports the full 16-bit key.
    - 1-bit gray is reported scaled (key 1 → 255), so it was already correct.
  - The new step (1b) reads the PNG header itself. Export opens `source` once as a binary file, reads its first 26 bytes, seeks back to 0 and passes the same handle to `Image.open`. Any failure there is the existing fixed `InboxPathError`. `_png_key(image, header)` then works from the IHDR colour type (byte 25) and bit depth (byte 24):
    - gray at depth 2 or 4: it multiplies the key by `255 // (2 ** depth − 1)`;
    - RGB at depth 16: it removes the key, so that colour exports opaque;
    - any other image: it leaves the image unchanged.
  - I chose removal over matching on the high bytes. A high-byte match would hide opaque pixels that only share those bytes.
  - Plan :107 and :108 say the same in prose.
  - D-614 (plan :479) carries the keyed `1` and `_png_key` in its chosen text. It has two new precedents (plan :488-489) and its reasoning (plan :493).
  - Files Modified (plan :247) and `task.md` row 3 (:61) name `_png_key`.
  - AC-136.4 (plan :206) builds every fixture from hand-written PNG bytes with a `tRNS` chunk, and adds:
    - your fixture: 1-bit alternating 1-px columns, black and keyed white, shrunk to `max_edge` 128. PNG must be `LA` and WebP `RGBA`, with the centre's alpha within 10 of 127 and its colour within 10 of black, never the round 2 order's opaque grey;
    - 1-bit (keys 0 and 1), 2-bit (keys 1 and 3) and 4-bit (keys 1 and 15) stripes: alpha 0 and 255 at the interiors in PNG and WebP, unresized and shrunk, with no `transparency` in any output that has alpha. JPEG must show each keyed stripe's stored value within 3;
    - a keyed 16-bit RGB source: no `transparency` in `info` and every pixel's alpha 255.
  - The control column adds F5's 1-px columns.
  - A new §Out of Scope row (plan :283) raises the same key misreads in crop and the resized `image` view for Mat, without fixing them. `task.md` H1-6 (:75) now names three items raised for Mat.
  - Receipt `C:/Temp/av-kit/s64-plan-keynorm-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_keynorm_r3.py`, Pillow warnings raised as errors) ends `probe: 0 unexpected`, `exit=0`:
    - `F5 reproduced: round 2 order gives opaque grey: ('L', {'transparency': 255}, (127, 127, 127, 255))`;
    - the fixed PNG is `LA` and the fixed WebP is `RGBA`, both with centre `(0, 0, 0, 127)`;
    - every gray depth and key gives normalised alpha `(255, 0)` unresized, and passes shrunk in PNG and WebP;
    - the 16-bit RGB key is removed, and its PNG save holds no key.
  - Receipt `C:/Temp/av-kit/s64-plan-key16-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_key16_r3.py`) records how Pillow reports the 2-bit, 4-bit and 16-bit RGB keys.
  - Receipt `C:/Temp/av-kit/s64-plan-webp-unresized-probe-r3.txt` (`C:/Temp/av-kit/s64/probe_webp_unresized_r3.py`) ends `probe: 0 unexpected`, `exit=0`. Each keyed 1-, 2-, 4- and 8-bit gray stripe source, after `_png_key`, goes unresized through step (6) as WebP `RGBA` and PNG in its kept mode, and gives alpha `(255, 0)`.
  - `C:/Temp/av-kit/s64-plan-lowbit-probe-r3.txt` was the first low-bit probe. It exited 1 and found the unscaled 2-bit and 4-bit keys. Its 32-px stripes don't blend under a 2x shrink, so it could not reproduce F5. It is kept as a record.

### Verification

- `C:/Temp/av-kit/s64-plan-correct-r3.txt`, exit 0: `implementation-plan.md: 13 edits, each matched once; LF only; 638 lines` and `task.md: 2 edits, each matched once; LF only; 112 lines`. `C:/Temp/av-kit/s64-plan-correct-r3b.txt`, exit 0: `implementation-plan.md: 3 edits, each matched once; LF only; 639 lines`. That second pass closed step (4)'s cite bracket and recorded the unresized probe. The pre-correction copies are `C:/Temp/av-kit/s64/implementation-plan.pre-r3.md` and `C:/Temp/av-kit/s64/task.pre-r3.md`.
- `C:/Temp/av-kit/s64-plan-census-r3.txt`, exit 0 (`C:/Temp/av-kit/s64/census_r3.py`): `Blast-radius census: 5 values changed, 20 variants swept, 12 sites found, 6 updated, 6 confirmed consistent; 0 stale phrases left.`
- `C:/Temp/av-kit/s64-plan-task-lint-r3.txt`, exit 0: `OK: 27 row(s); 10-column table (with builder_model); 25 row(s) fully checked`.
- `C:/Temp/av-kit/s64-plan-decision-probe-r3.txt`, exit 0: the plan-and-grouping set reads `19 decisions`. No decision was added. D-614 changed in place.
- The round 3 review was validated at `C:/Temp/av-kit/s64-plan-review-state-r3-temp.json`. Its body begins with the canonical text byte for byte. It was then copied byte for byte to canonical, and `C:/Temp/av-kit/s64-plan-review-state-r3.json` was rebuilt there: `round 3 of 5; verdict=changes_required; open findings=1`.

Verdict set to `corrections_applied` for the round 4 recheck. Only an independent recheck can set `approved`.
## Recheck (2026-11-11, round 4)

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---------|-------------|----------------|
| F1 | fixed | fixed |
| F2 | fixed | fixed |
| F3 | fixed | fixed |
| F4 | fixed | fixed |
| F5 | open | fixed |

### Confirmed Fixes

Plan references mean `docs/execution/plans/2026-11-11-capture-export-copy/implementation-plan.md`; script references mean files in that folder unless qualified.

- **F1 remains fixed:** plan :108, :122, :206, :479 and :562-573. JPEG still converts to RGB before resizing and ignores a depth-map key. The fresh executable reading passes all 65,536 depth values, signed-I clamping, native unresized `I;16` PNG, resized depth blocks and the stored-colour JPEG cases. Keyed JPEG centres remain 128 and stored-red centres remain within 3 of (200,40,40). The Q5 managed-LAB outputs carry the replacement sRGB profile, matching the unchanged `_to_srgb` at `packages/infrastructure/src/avkit_infra/capture/adapter.py:288-300`.
- **F2 remains fixed:** `eval-check.py:92-99`, :190-199; plan :129, :221. Actual file decoding, JPEG format, decoded dimensions and direct inbox confinement remain required. The checker is byte-identical to the round 3 reviewed file, verified against the round 3 SHA-256 snapshot. Its accepted positive/negative selftest evidence remains applicable; no fresh eval or selftest run is claimed.
- **F3 remains fixed:** plan :124-125, :216, :219. REST strict-integer refusal and MCP integer serialization, including the integral-float difference, are byte-identical to round 3. AC-136.14/.17/.18 are unchanged. No fresh Pydantic/Zod runtime claim.
- **F4 remains fixed:** plan :125, :128, :219, :579-591. The export-specific fixed unknown-key refusal, other-error passthrough and crop positive control are unchanged. `EXPORT_MCP` and `NO_RAW_OUTPUT` are byte-identical to round 3. No fresh Zod runtime claim.
- **F5 fixed:** plan :107-108, :122, :206, :247, :479, :488-493; `task.md:61`. Keyed mode `1` now converts to `LA` before LANCZOS for PNG/WebP. Using the exact round 3 fixture bytes, the old encoder produces centre RGBA (127,127,127,255); the corrected encoder produces PNG `LA` and WebP `RGBA`, both centre (0,0,0,127), with no residual key. The source SHA-256 is unchanged. `_png_key` also repairs every valid 2-/4-bit gray key, and removes the unusable 16-bit RGB key without making an opaque high-byte collision transparent.

### Remaining Findings

None.

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

### R1 — F5, key normalization and assertions

Accepted `EXPORT_ENCODE` step (1b) and the corrected step (4), plan :122. For a PNG with its required first IHDR, bit depth is byte 24 and colour type byte 25. At depth 2 the exact multiplier is 85; at depth 4 it is 17. The fresh probe exhausts all 4 and all 16 gray keys, every decoded sample for each key, and both 1-bit keys. PNG/WebP saves, at original size and half size, have exactly alpha 0 at keyed stripe interiors and 255 at every other stripe interior. JPEG preserves stored luminance within 3. The old encoder's 2-/4-bit key-1 unresized PNG/WebP controls remain opaque and fail those new alpha expectations. The new assertions therefore distinguish the defect, including the unresized path through step (6).

Removing the 16-bit RGB key is appropriate for the decoded source available to this operation. Pillow has already discarded the low sample bytes; a key cannot then identify the exact original pixels. Two different 16-bit colours with the same high bytes become the same RGB tuple. Matching on those high bytes makes the opaque colour transparent, demonstrated by two separate collision fixtures. Removing the key preserves the decoded stored colour, avoids that false transparency and writes no stale key. This does not claim recovery of original 16-bit RGB transparency; the limitation is explicit at :108 and :283 and is consistent with the source-as-shown boundary accepted for the existing surface.

`_png_key` leaves the tested 8-bit gray, 16-bit gray, 8-bit RGB, palette PNG, non-PNG JPEG and PNG without a key identical in object identity, mode, pixels and metadata. In particular it leaves native `I;16` and its 32768 key alone. The helper must apply the described PNG/header/key guard; the new low-bit branch is not applied to arbitrary file headers.

The one-open contract is sound: open as binary, read 26 bytes, seek to 0, decode and load through that handle, all inside the existing fixed-error boundary (plan :122, AC-136.6 at :208). The fresh executable reading injects open, read, seek, decode, load and context-close failures; each produces exactly `InboxPathError("the image could not be opened")`, with one open attempt and no marker path in `str(error)`. This checks the proposed boundary, not an implemented adapter.

AC-136.4 at :206 supplies effective negative cases. The exact F5 fixture fails the old order and passes the new one with centre alpha 127 and black visible colour. Tolerances of 10 for this blended centre and 3 for JPEG stripe luminance are satisfied at quality 90 and leave a large margin from opaque grey. Exact alpha 0/255 is sound at the centres of 32-px stripes under a 2x shrink; it is not asserted at mixed boundaries. The 16-bit RGB PNG no-key assertion also fails the previous retained-key save. Unchanged assertions are intentionally still valid on the earlier encoder; they are regression controls.

Plan :107-108 and D-614 (:479, :488-493) agree with these observations. The new out-of-scope row :283 agrees with the current crop retaining the raw key (`adapter.py:458-463`) and the view's conversion/encoding path (`adapter.py:271-284`): these existing paths do not normalize the low-bit key, and cannot recover the RGB low bytes. Accepted as a raised existing issue, without expanding this session. Nothing in R1 remains unaccepted.

### R2 — Regressions and intent

Accepted JPEG's RGB-before-resize order and stored colour; all 65,536 depth mappings and the unresized keyed `I;16` PNG; Q5's replacement sRGB profile; and AC-136.4's unchanged initial mode list and unresized PNG L/LA/RGBA/P/I;16 requirements. The corrected executable reading passes the existing 195 regression assertions, with additional per-encode mode/key/size checks in the new cases. F1-F4 remain fixed.

`Files Modified` (:240-259) changes only the adapter description to name `_png_key` (:247). Both that adapter and its new test file remain in `session-gate.ps1:45`, :52. The gate itself and the eight other plan-folder files, including `red-check.py` and `eval-check.py`, match their round 3 reviewed hashes. `task.md:59` is byte-identical to its pre-correction row: `--require` is exactly `test_ac_136_2` through `test_ac_136_16`; MCP .17/.18 remain in row 2b. No Red setup/import-failure relaxation or product gate expansion was introduced. All ten plan-folder files remain LF.

D-608 remains unchanged and unruled (plan :375-392). The unchanged eval checker selects six runs under A and three under B (`eval-check.py:219-228`); C reports not-run before consulting answers/run files (:209-214). The encoder corrections do not affect these branches. D-608 through D-620 are retained. This approval assesses the plan under all three choices and does not choose for Mat or grant execution authorization. Nothing in R2 remains unaccepted.

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| R1 F5 negative/positive comparison | pass | Exact round 3 fixture: old PNG/WebP centre (127,127,127,255); corrected PNG LA / WebP RGBA centre (0,0,0,127); source hash unchanged. |
| R1 IHDR, every low-bit key and unaffected sources | pass | All 22 keys across depths 1/2/4, every sample, unresized/shrunk PNG/WebP; exact interior alpha; JPEG within 3; six unaffected source cases identical. |
| R1 16-bit RGB and fixed open-error boundary | pass | High-byte collision negatives demonstrate false transparency; removal keeps every output alpha 255. Open/read/seek/decode/load/close injection preserves the fixed text and one open. |
| R2 JPEG, depth, profile and mode regression | pass | Fresh 195 existing regression assertions, plus new-case encoding invariants; full depth map and native keyed I;16 pass; managed LAB gets replacement sRGB. |
| F2-F4, gate scope, Red requirements and D-608 | pass | Hash/text comparisons, unchanged transport contracts and eval checker; adapter/test allowed paths; exact .2-.16 requirement set; A/B/C branch inspection. |
| Review artifact and source preservation | pass | Complete canonical body retained; only three requested frontmatter values changed before append; reviewed repository file hashes unchanged. |
| Product suites, baseline/session gate, seed/harness, live eval, videos and network | n/a | Not run or accessed, as instructed. No implementation completion claim. |

Tested state: HEAD `2832e3d` on `main` plus the two untracked Session 64 paths: `docs/execution/plans/2026-11-11-capture-export-copy/` and `.agent/context/handoffs/2026-11-11-capture-export-copy-plan-critical-review.md`. Other sessions' paths are outside this review. `.claude/settings.local.json` is ignored on the host through `<HOME>/.config/git/ignore`; it was neither opened nor counted. Python probes used `PYTHONDONTWRITEBYTECODE=1`; synthetic images, probe scripts and snapshots were written only under `C:/Temp/av-kit/s64/review`. Report/receipts are under `C:/Temp/av-kit`. No repository file was edited.

Decisive fresh evidence:

```json
{"schema_version":"evidence.v1","check_id":"r4-encoding","command":"rtk proxy python C:/Temp/av-kit/s64/review/encoding_r4.py","cwd":"P:/av-kit","scope":"EXPORT_ENCODE executable plan reading: F5, exhaustive low-bit keys, RGB16 collision, open-error boundary, depth/JPEG/profile regressions","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus the two untracked Session 64 paths named above; Pillow 13.0.0","output":"ROUND 4 PASS: 2083 new assertions; 487 encoder/regression assertions total, including the original 195 regression assertions. F5 old centre (127,127,127,255), corrected LA/RGBA centre (0,0,0,127). All 22 valid low-bit keys preserve exact interior alpha in unresized/shrunk PNG/WebP. RGB16 high-byte matching falsely hides opaque collisions; removal keeps alpha 255. Six unaffected source cases identical. All six injected open-boundary failure types preserve fixed InboxPathError text.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"r4-contracts","command":"rtk proxy python C:/Temp/av-kit/s64/review/contracts_r4.py","cwd":"P:/av-kit","scope":"Correction regression comparison, prior reviewed hashes, gate paths, Red requirements, decisions and target identity","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 2832e3d plus the two untracked Session 64 paths named above","output":"Eleven non-encoding mechanisms byte-identical to round 3. Only AC-136.4 changed. Files Modified adds only _png_key; affected adapter/test remain in gate. Row 2a requires exactly test_ac_136_2 through test_ac_136_16. D-608 unchanged and unruled; D-608 through D-620 retained. Eight other plan-folder files unchanged since round 3; all ten LF. Canonical prior report retained. Contract regression and correction scope: PASS.","fresh":true}
```

The first contract-probe attempt used an unquoted frontmatter comparison against a quoted `verdict` value and failed that probe's preservation assertion. Its comparison was corrected in the temporary reviewer script; the rerun above passes. No plan or report source bytes changed to satisfy it.

### Verdict

`approved` — F1-F5 are fixed; zero open blocking findings and no new findings. No High or Critical defect remains established. Intent achieved: yes, as a plan for the registered Session 64 export-copy goal and conditional description eval. D-608 remains Mat's open decision. This is plan approval, not implementation verification or permission to execute.
