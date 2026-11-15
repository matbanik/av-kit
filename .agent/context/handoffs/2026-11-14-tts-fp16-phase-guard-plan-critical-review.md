---
date: "2026-11-15"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s73-plan-2026-11-14-tts-fp16-phase-guard"
round: 3
---

# Critical Review: 2026-11-14-tts-fp16-phase-guard

> **Review Mode:** `plan`
> **Verdict:** `approved`

> **Rolling report:** Rounds 1 and 2 below are historical observations, preserved except for F1's Status cell, now fixed. The current assessment, evidence and approval are in **Recheck (Round 3)**. Frontmatter and this current banner reflect round 3; historical download/read restrictions and failing checks do not describe the corrected amendment.

## Scope

**Intent anchor:** Find out whether a small change to a copy of the FP16 graph stops its non-finite audio without changing anything else, then put the measured result in front of Mat so he can decide what ships.

**Intent assessment: yes, as a plan.** Following the rows delivers the instrumented counts, unchanged-output comparisons, packaged smoke and listening material, then requires Mat's outcome ruling. Approval here authorizes no execution or shipping.

Codex independently reviewed Claude Code/Anthropic's working-tree plan, all 28 task rows and five supporting scripts. Observed HEAD: `58d028ec7f6414ed2016f34e847222540d9d1177`. Status showed the seven untracked plan files and the disclosed sandbox-only `.claude/settings.local.json` ignore discrepancy. That file was not opened. The plan remains draft with 28 unchecked rows; the measured planning spike is explicitly distinguished from execution.

Applied PR-1 through PR-9 and the Materiality Gate. Accepted the supplied source request, carried rulings, approved prior sessions, exclusions and pending human decisions as instructed. Assessed D-792/D-794/D-795/D-796 on their substance. Read the review template and Session 72 peer report for presentation only.

No repository file was edited. Only the permitted selftests and bounded local probes ran; all writes were under `C:/Temp/av-kit`. No product suite, baseline, session gate, package build, smoke or 149-job inference ran. No network, clipboard, user-data location, secret file, divergence-report content or installed avkit MCP server was accessed. `<HOME>` denotes the home folder.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal and specification coverage

**Accepted:** DENOM_COUNT measures the real denominator's exact zeros and nonzero FP16 subnormals (`0 < abs(real) < 2^-14`), per job/chunk, including the failing pairs. AC-127.3 and row 3 require the measured failing and passing totals and exact failure set. The receipts show 108 denominator zeros, 1,171,881 subnormals and 14 both-zero slots among the failing jobs. These are actual denominator counts, not a count of failed WAVs.

All five 03 rules have work and AC coverage (plan:189-206). The unchanged product scope preserves FP16 availability/preselection. Upstream posting is forbidden. Rows 8-9 supply listening and the outcome decision. SENTENCE_SMOKE reaches `_generate`'s declared-frame versus actual-payload check (`tools/smoke_packaged_tts.py:356-364`), satisfying AC-121.8 through AC-127.6. No required rule is silently deferred. D-793's explicit human interpretation remains necessary before execution.

## Q2 — PHASE_GUARD and D-793

**Accepted:** `patch_model` inserts exactly IsNaN and Where, with an FP16 scalar +0, and rewires the sole Atan consumer (phase-guard.py:130-172). The false branch is the original quotient, preserving finite values, signed zero and infinities. The independent selftest passed 24/24 under both optimization levels. The real graph inspection confirmed Div(imag, real), one Atan consumer, IR 9/opset 20, and the subsequent Greater/Less/Where quadrant path.

For both-zero inputs, `real < 0` is false even for -0, so the graph selects the guarded Atan result +0. This is a deliberate canonical zero for this exported path; it is not a general implementation of every IEEE signed-zero atan2 convention. Finite Atan output and the bounded subsequent +/-pi adjustments introduce no new NaN in this local phase path. The corpus receipts, rather than a universal claim about all future inputs, establish the measured fix.

**Verification limit:** The fixture selftest compares post-Atan outputs, not separately exposed quotient bits; exact quotient passthrough is supported by the Where wiring. I do not describe the fixture as exhaustive measurement of all FP16 bit patterns.

D-793 honestly says the division still executes and requests Mat's approval of that interpretation (plan:521-534). Patch B's effect on passing jobs is disclosed as measured; Patch C is explicitly unmeasured and requires an additional patch/compare. I accept this recommendation as a spike proposal, subject to Mat's ruling, rather than treating it as literal compliance already granted.

## Q3 — PATCH_COPY and boundary refusals

**Accepted:** The graph checks run before serialization/write: already guarded, missing/duplicate named Div, wrong operator/output shape, exposed quotient and an unexpected consumer are refused. Destination checks resolve paths and reject source equality, the checkout, Session 52's cached-model tree and `<HOME>/.avkit` (phase-guard.py:175-206). The permitted selftest exercised the declared graph and destination refusals.

Two fresh loads must serialize identically, the ONNX checker runs before the write, and source SHA-256 is measured before and after. Row 2 additionally requires the expected source hash, destination hash and byte count. Its prescribed destination and JSON receipt are under Temp. These conclusions concern the declared boundary and planned argv; they do not assert that this administrative script sandboxes arbitrary caller-supplied receipt paths or filesystem races.

## Q4 — Counts, graph comparison, WAV identity and listening

**Accepted:** Count adds graph outputs to a separate tapped copy, without rewriting nodes or their inputs. `model_unchanged` is a before/after source-file hash, correctly proving file preservation; it is not by itself a numerical-transparency test for instrumentation. The independent untapped control and comparison receipts corroborate the same 12 failing jobs. The instrumented receipt reports 14 Div/Atan/phase NaNs, all both-zero slots at bin 10, with no such NaN in passing jobs.

GRAPH_COMPARE compares every waveform chunk's shape and raw bytes (phase-guard.py:488-515). WAV_IDENTITY separately compares complete packaged WAV files byte for byte, so its 137 matches are stronger than matching lengths. Each run's database and sidecars are copied into `s73/db-copies` before SQLite opens the copy. The planned reads use the isolated run databases, not the user's database; database copies, listening output and receipts remain under Temp.

LISTEN_FOLDER pairs guarded FP16 and INT8 for each of the 12 control-failed jobs, with identifying filenames and `listen.txt`. The supplied receipt records 12 complete 24 kHz pairs and 137 identical control-passed WAVs. D-795 selects the material Mat needs to hear, without claiming that numerical finiteness proves speech quality.

## Q5 — RUN_COPIES, Red parity and backend ownership

**Accepted:** Row 1 checks all five destinations before building/copying. S17 prevents overwriting an existing row-1 run/model tree. One build with three run copies and two model copies controls the executable variable while retaining each smoke's `app-data` and `out`. This matches the smoke's destructive recreation of those sibling directories (`tools/smoke_packaged_tts.py:688-695`). D-794 is sound.

Row 5 requires exit 1, exactly 12 finite-audio failures, no unrelated errors and the same kind/index/voice keys as Session 52. Rows 6-7 then require the guarded and INT8 Greens. The supplied plan-time receipts support this parity; I did not rerun them.

The smoke stops its own Popen handle. Rows 5-7 and the gate list possible leftovers using executable name **and the relevant executable-path prefix**; they fail on a leftover and require any subsequent stop to use that listed PID. No command here stops a process by name or authorizes stopping another run's backend.

## Q6 — Records and D-792

**Accepted:** `issue-resolve.py` holds a Windows handle denying other writers, checks the expected SHA before staging, restricts semantic differences to the selected issue's four allowed keys, validates the staged serialization and re-reads all decision logs before replacement (issue-resolve.py:201-265). A scratch-only probe preserved parsed data outside the allowed fields, emitted LF and successfully read 84/84 decision logs. It never opened the real register for writing.

Row 10 requires byte insertion of 03's Delivered note after the table and before the next anchor, preserving CRLF and leaving the rule rows intact. S11 requires pre-write copies and diffs, with byte edits confined to MEU-127 when status files have concurrent changes. The existing status writer emits LF, and the render commands target the declared generated surfaces. `issue_triage.py render` does not perform triage or refresh `triage-output.yaml`.

D-792 correctly leaves the issue open: neither a successful spike nor a ship recommendation changes the FP16 file users receive. Even a ship ruling awaits a separately reviewed amendment. MEU approval records completion of this spike, not delivery of a shipped fix.

## Q7 — OUTCOME_BRIEF and shipping

**Accepted:** Row 9 explicitly requires all counts, compare/smoke/identity results and their receipts, a recommendation, alternatives including ship nothing, the listening folder and Mat's quoted ruling. It stays blocked until that ruling, with D-797 recorded in the execution decision log (task.md:74). Its command rejects a missing ruling marker or pending/null YAML decision. The brief's numeric accuracy and recommendation ordering remain substantive content-review obligations; receipt-name substring checks alone are not proof of those facts.

The do-nothing outcome retains shipped FP16 and the open issue. A ship ruling creates an amendment with its own Red and review; no current row installs, distributes or changes the product graph. Thus the spike places evidence before Mat without silently converting his outcome preference into implementation authorization.

## Q8 — Gate, identity, scope and safety

**Accepted:** Source tracing finds the declared static, full-suite/render, fresh-patch, hash-parity, package, fresh-smoke, leftover and before/after identity steps in order. Each native step's preserved failure stops later steps, and the success terminator is exactly `session-gate: all steps exit 0` (session-gate.ps1:141-206). Only the baseline's actual FAILED ids can be excused; collection errors are not excused. This is source review, not a claim that the gate has executed successfully.

The identity selftest passed. It binds HEAD, relevant tracked/untracked repository state and the declared runtime, while excluding this session's later closeout artifacts. Scope paths cover the proposed record/render and project writes; H1-4 separately rejects tracked or ignored/untracked checkout ONNX files outside `.venv/`, and product-path changes. All seven new plan files currently have LF; task.md:54 specifies LF for new files and preservation checks for existing files.

Baseline source reads the actual `meus` sequence, checks MEU-121/MEU-127 and the ancestor, records target hashes/endings, checks the two model hashes, asset presence and ONNX versions, then installs offline. It refuses today's draft Status because it lacks USER_EXPLICIT. External Temp assets are not all included in `identity.py`'s digest: the plan instead uses pinned model hashes, fixed-input checks, fresh copies and disabled intermediate reuse. This approval does not certify evidence reuse after changed external inputs, hostile CLI arguments, or failed filesystem-copy operations.

The declared operations use cached models and isolated app-data; smoke traffic is localhost with dead external proxies and private homes/caches. No row selects an upstream post, model download, clipboard spec, installed MCP operation or commit. Packaging writes its existing ignored `packaging/build` and `packaging/dist` outputs, as declared; the record/render writes are the listed repository scope. No secret or user-data read is needed for the spike. I found no demonstrated material safety violation in the prescribed execution path.

## Checklist Results

| Check | Result | Procedure / observation | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Codex traced named contracts, ACs and rows 0-10/H1/H2 | null | Same spike, decision boundary, records and review order |
| PR-2 Not-started confirmation | pass | Codex read task status and the working-tree readiness probe | null | Draft; 28/28 task rows unchecked; planning measurements disclosed |
| PR-3 Task contracts | pass | Codex inspected all 28 rows and supplied task-lint receipt | null | Owners, deliverables, validations, dependencies and statuses present |
| PR-4 Validation realism | pass | Codex traced script entrypoints, smoke payload checks and receipt predicates | null | Existing producers support each required observable; 9 referenced tool scripts exist |
| PR-5 Source-backed planning | pass | Codex mapped AC table to 03, carried rulings and local canon | null | Five binding rules covered; D-793 interpretation remains explicitly pending |
| PR-6 Review/correction readiness | pass | Codex inspected H1 handoff/review and H2 sequencing | null | Independent review before approval; caps 3/6; round-2 census not applicable |
| PR-7 Scope discipline | pass | Codex checked exclusions against the supplied scope and 03 | null | Shipping is conditional amendment; no required spike work excluded |
| PR-8 Controls and negative cases | pass | Codex traced refusals, Red parity, error exits, human gate and register handle | null | Permitted selftests and scratch register probe support the declared controls |
| PR-9 Contract consistency | pass | Codex compared named contracts and their live AC/task assertions | null | No materially conflicting behavior found |

### Independent probe evidence

Commands ran with `PYTHONDONTWRITEBYTECODE=1`; TMP/TEMP for the identity fixture were under `C:/Temp/av-kit/s73/review`. Neither full-tree identity mode nor any prohibited execution command ran.

```json
{"schema_version":"evidence.v1","check_id":"s73-review-phase-guard-selftest","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-14-tts-fp16-phase-guard/phase-guard.py selftest","cwd":"P:/av-kit","scope":"fixture guard and boundary refusals","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 58d028ec7f6414ed2016f34e847222540d9d1177; working-tree plan scripts; isolated selftest fixtures","output":"selftest: 24 checks, 0 failed; both ORT_DISABLE_ALL and ORT_ENABLE_ALL passed","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s73-review-identity-selftest","command":"rtk proxy .venv/Scripts/python.exe -B docs/execution/plans/2026-11-14-tts-fp16-phase-guard/identity.py --selftest","cwd":"P:/av-kit","scope":"scratch-repository identity binding","phase":"targeted","exit_code":0,"result":"pass","tested_state":"working-tree identity.py; scratch repository under C:/Temp/av-kit/s73/review","output":"identity selftest: 0 failure(s); bound mutations changed identity and refused historical evidence; declared artifact mutations left identity unchanged","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s73-review-source-and-receipts","procedure":"Codex read the specified plan-time JSON/text receipts, inspected the source ONNX phase nodes read-only, and exercised register parsing/serialization on a Temp-only fixture. Compared fixture differences with the selected issue and RESOLVE_KEYS; checked LF and every decision log. Inspected all task rows and referenced executable paths.","observer":"codex-independent-reviewer","cwd":"P:/av-kit","scope":"Q1-Q8 source review and bounded scratch probes","phase":"targeted","exit_code":null,"result":"pass","tested_state":"HEAD 58d028ec7f6414ed2016f34e847222540d9d1177; working-tree seven plan files; supplied planning receipts and cached source graph","output":"14 both-zero slots, bin 10; control 12 failures; guarded and INT8 149/149; 137 identical WAVs; 12 listening pairs. Scratch register: zero outside-field changes, parsed equality true, LF true, 84/84 decision logs readable. Nine referenced tool scripts present. The first scratch probe had a reviewer assertion counting changed top-level fields instead of leaf values; corrected to the allowed-path predicate and passed. No product execution result is claimed.","fresh":true}
```

## Verdict

`approved` — No evidence-backed High or Critical delivery defect found. The plan delivers the scoped measurement and outcome decision without changing shipped behavior. D-789, D-790, D-791, D-793 and explicit execute words remain Mat's plan gate; D-797 remains the execution outcome gate. This is independent plan approval, not execution approval, shipping approval or an implementation-complete claim.

## Recheck (Round 2)

**Date:** 2026-11-14. **Workflow:** `/plan-critical-review`, Amendment 1 only. **Agent:** `codex-independent-reviewer` (Codex/OpenAI; plan author Claude Code/Anthropic).

**Intent anchor:** Find out whether a small change to a copy of the FP16 graph stops its non-finite audio without changing anything else, then put the measured result in front of Mat so he can decide what ships.

**Intent assessment: partial, as a plan.** The measurement and Mat's row-9 decision remain intact. The new download step can falsely satisfy its input contract through an inherited cache. Round 1's approval of unchanged work stands.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| none | none | none |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | High | yes | control-defeat | **Inherited Hub caches bypass FRESH_INPUTS (confidence: High; violates AC-127, especially AC-127.12; mechanism: task-row-completion-predicate).** `check_env` permits `HF_HUB_CACHE` / `HUGGINGFACE_HUB_CACHE`; setting `HF_HOME` does not override them. With no explicit `cache_dir` or `force_download`, Hub 2.3.0 copies matching files from that shared cache. A no-network probe using the actual seven Session 52 inputs copied all seven bodies from an inherited fixture cache outside the private home, returned no problems, and satisfied every row 0b content/pin predicate without any body download. This defeats Mat's download ruling and permits undeclared cache reads. `HF_XET_CACHE` can also escape the private home. | `docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py:37`; `:103`; `:115`; `:218`; `docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md:66`; Hub client `file_download.py:1467` and `constants.py:173` | Refuse or confine inherited cache overrides before client import, explicitly bind its cache to the private home, and require fresh body downloads. Add an offline real-client regression for the shared-cache fallback; cover offline/staging aliases too. | fixed |

### R1 — Fidelity to Mat's ruling

**Accepted:** Status and the amended harness, S5, AC-127.11 and task header explicitly permit only row 0b's seven downloads and exact installed-file hashes. D-790/D-791/D-793 and execute words are recorded as ruled; D-798 correctly gates row 0 on this amendment review. H1-4 tests checkout/product isolation and does not reject row 0b's Temp files. No executable row introduces a database or settings read (plan:16,77–88,127–144,221; task:15,66,83).

**Not accepted:** The implementation's cache fallback can expand the authorized read boundary and omit fresh body downloads (F1). Non-blocking clerical corrections only: task:85 still asks the handoff to say no row downloaded/read user data; task:86 still uses `len(every)==11` after AC-127.12 was added. Say the row-0b exception and use 12. These are not additional findings or grounds for this verdict.

### R2 — FRESH_INPUTS

**Accepted:** `inputs()` imports the graph repository/file map, six revision pins and local ONNX folder from `voices.py`; config comes from `assets.py` with no revision, matching `vocab.py`. The four voice IDs match the spike. `token=False` reaches the actual client without an Authorization header. Metadata's first line is the commit in Hub 2.3.0, and `compare` rejects a wrong or missing pinned commit. Resolved-path equality and destination containment/existence checks implement the stated planned-path and S17 refusals (fresh-inputs.py:54–149,194–195).

**Not accepted:** `HF_HOME` alone does not isolate the client from inherited cache overrides. The real-client reproduction establishes F1; the refusal list also omits the client's `TRANSFORMERS_OFFLINE` and staging aliases. No assertion is made that the host currently has those variables set.

### R3 — INSTALLED_READ

**Accepted:** `installed()` checks exactly the seven named paths and opens present files only in binary read mode for SHA-256; it does not enumerate, copy or write installed data. Missing files become `absent`, with comparison null. `redact` replaces plain Windows, JSON-escaped and forward-slash home forms, then case-folds/slash-normalizes to refuse a remaining home form before JSON receipt write (fresh-inputs.py:46–51,152–159,201–234). Default models path agrees with settings.py:77 without opening settings.

**Not accepted:** No additional installed-read defect established. This acceptance describes the explicit hash loop and JSON receipt sanitizer; it does not certify arbitrary caller arguments or all dependency diagnostics.

### R4 — Equality, S10 and S18

**Accepted:** Download/cache inequality, pinned commit mismatch and present-installed/cache inequality each append a problem and produce exit 1; absence alone does not. The two graph cache hashes are checked against `EXPECT` for S10. This correctly preserves the approved plan-time graph values and Red parity when Session 52's other cached assets remain unchanged, as the runtime prerequisite requires (fresh-inputs.py:162–198,243–246; plan:336).

**Not accepted:** Hash equality proves byte identity, not a fresh network body transfer. F1 shows all content/commit predicates can pass after shared-cache copies. I have not recertified unmodified baseline assumptions or evidence reuse after external-input changes.

### R5 — Row 1 overlay and gate cache

**Accepted:** Row 1 checks all five destinations before building/copying, then copies the seven downloaded relative paths with `-Force` into both `models-original` and `models-guarded` before its FP16 hash assertions. Rows 2–8 retain those model roots. The gate's Session 52 cache remains a sound source for its independent patch under row 0b's equality proof and unchanged-cache prerequisite (task:67; plan:138,142,294,327).

**Not accepted:** No additional overlay defect established. Round 1's stated limits concerning failed filesystem-copy operations remain unchanged.

### R6 — AC-127.12 and selftest

**Accepted:** Independently reran the permitted selftest with bytecode disabled and Temp-local fixtures: **23 of 23**, exit 0. It exercises seven-row selection/pins, destination checks, endpoint/offline refusal, equality/absence, installed and download differences, wrong commits, wrong expected graph hash, wrong landing and home sanitization. AC-127.12's seven-file/hash/pin/installed/null/problem/redaction fields match row 0b's check (plan:222; task:66).

**Not accepted:** The passing selftest is not evidence of actual client cache isolation. It injects `fake_fetch`; it does not exercise Hub's inherited-cache fallback. F1 requires that missing negative case. The 23/23 count itself is accurate.

### R7 — Safety and limits

**Accepted:** The new prescribed receipt/destination paths are under Temp, and row 0b is the only added network/user-model read step. The amendment adds no post, clipboard write, process stop, app database/settings read, divergence-report open, installed MCP operation or model commit. Baseline and gate add only local lint/selftest execution for the new script. Unchanged operations retain round 1's approval and limitations.

**Not accepted:** The private cache boundary is not enforced against inherited cache paths (F1). Hub 2.3.0 used an external fixture cache despite private `HF_HOME`; `HF_XET_CACHE` also resolves outside it. This is a demonstrated extra read path, not a claim that I accessed the user's actual cache or observed a real Xet write.

### Round 2 evidence and scope

Observed HEAD `58d028ec7f6414ed2016f34e847222540d9d1177`, branch `main`. Read the working tree, app source constants and installed Hub client source. The first cache probe used small isolated fixture bytes; the decisive second probe used Temp copies of the actual seven Session 52 inputs and production expected graph hashes. It stubbed remote metadata and made any body-transfer/network attempt fail. No `run` subcommand, installed-user-data read, network request, product suite, baseline, session gate, build, smoke or inference ran. No repository file was written. All reviewer-created artifacts and fixture copies are under `C:/Temp/av-kit`; probe data is under `s73/review`. No secret file, installed user-model file, clipboard or forbidden report content was accessed.

| Check | Result | Exit | Decisive observation |
|---|---|---|---|
| Amendment source trace (Codex manual observation) | pass | null | Seven intended files, six pins, exact installed read loop, three S18 branches, row-1 overlay order |
| Permitted offline selftest | pass | 0 | `fresh-inputs selftest: 23 of 23` |
| Real-client inherited-cache boundary | fail | 0 | Seven files copied from external fixture cache; zero body downloads; problems empty; all row-0b content/pin checks true. Exit 0 means defect reproduced |
| Product/runtime execution | n/a | null | Prohibited by this review's scope; unchanged round-1 assessment retained |

```json
{"schema_version": "evidence.v1", "check_id": "s73-r2-fresh-selftest", "command": "rtk proxy pwsh -NoProfile -Command '$env:RECEIPTS_DIR=\"C:/Temp/av-kit\"; $env:PYTHONDONTWRITEBYTECODE=\"1\"; $env:TMP=\"C:/Temp/av-kit/s73/review\"; $env:TEMP=$env:TMP; & .venv/Scripts/python.exe docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py selftest; exit $LASTEXITCODE'", "cwd": "P:/av-kit", "scope": "fresh-inputs.py offline selftest", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md SHA256=728bea06f7ae7655714ad7ad9ab2531a429bde6f5985b8c54e5afae7c4b6b755; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md SHA256=a6f3874498f6d38fed9189eca0d344c9fb451a8043c363a172a1fd15e5b3ca16; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py SHA256=b5a2bc9826e25251fc0ca2517987c4ebad3c39237cc42e145a19425c52dc47c5; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/baseline.ps1 SHA256=28b4356829ffa79885eb24d3c28d265c24f1383988d520432d19ab1092330cc5; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/session-gate.ps1 SHA256=a19debaea74f019c6855336405da535d437cdc215f4debc2893c3cb120a5989a", "output": "fresh-inputs selftest: 23 of 23; all listed checks ok", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s73-r2-real-client-cache-boundary", "command": "rtk proxy pwsh -NoProfile -Command '$env:PYTHONDONTWRITEBYTECODE=\"1\"; $env:RECEIPTS_DIR=\"C:/Temp/av-kit\"; $env:TMP=\"C:/Temp/av-kit/s73/review\"; $env:TEMP=$env:TMP; & .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/probe_fresh_inputs.py; exit $LASTEXITCODE'", "cwd": "P:/av-kit", "scope": "offline real-client inherited-cache fallback; Temp copies of seven actual Session 52 inputs; no installed files", "phase": "targeted", "exit_code": 0, "result": "fail", "tested_state": "docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md SHA256=728bea06f7ae7655714ad7ad9ab2531a429bde6f5985b8c54e5afae7c4b6b755; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md SHA256=a6f3874498f6d38fed9189eca0d344c9fb451a8043c363a172a1fd15e5b3ca16; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py SHA256=b5a2bc9826e25251fc0ca2517987c4ebad3c39237cc42e145a19425c52dc47c5; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/baseline.ps1 SHA256=28b4356829ffa79885eb24d3c28d265c24f1383988d520432d19ab1092330cc5; docs/execution/plans/2026-11-14-tts-fp16-phase-guard/session-gate.ps1 SHA256=a19debaea74f019c6855336405da535d437cdc215f4debc2893c3cb120a5989a; installed huggingface_hub 2.3.0; source Session 52 model tree read only; isolated probe cache", "output": "Defect reproduced: check_env accepts HF_HUB_CACHE,HUGGINGFACE_HUB_CACHE,HF_XET_CACHE,TRANSFORMERS_OFFLINE,HUGGINGFACE_CO_STAGING. Private HF_HOME true; inherited Hub/Xet cache outside private home true; files_reported_download_equal=7; problems=[]; metadata stubs=7; body downloads=0; row 0b checks seven/fp16/int8/all_equal/pinned/installed/no_problems all true; actual network requests=0. Exit 0 confirms reproduction, not correctness.", "fresh": true}
```

### Round 2 verdict and follow-up

`changes_required` — one evidence-backed High finding, F1. Confine or refuse inherited cache configuration and prevent body-download substitution, then add the offline real-client regression and recheck Amendment 1 within the existing ledger. Do not start row 0 under this verdict. Mat's existing rulings remain accepted; no new human decision is requested. This is a plan review, not an execution-complete or shipping claim.

### Report validation

The repository's read-only review-state parser observed `review_mode=plan; round 2 of 3; verdict=changes_required; open findings=1`, exit 0. Command: `rtk proxy .venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s73-plan-review-round-2.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/s73/review/report-state.json`.

`rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/validate_review.py`, exit 0: verdict validates against `review-verdict.schema.v2.json`; required recheck headings and the exact prior-status table pass; the whole intent anchor is present; round 1's Scope through Verdict is preserved exactly; `## Findings` holds only its table. The first inline schema-check wrapper had a PowerShell quoting error before Python ran; the Temp script replaced it and passed. Both checks were repeated on the final report.

🕐 Completed: 2026-11-14 23:54 (EST)


## Recheck (Round 3)

**Date:** 2026-11-15. **Workflow:** `/plan-critical-review`, F1 recheck and fix-only regression scan. **Agent:** `codex-independent-reviewer` (Codex/OpenAI; plan/amendment/fix author Claude Code/Anthropic). **Ledger:** `s73-plan-2026-11-14-tts-fp16-phase-guard`, round 3 of 3. No new loop, continuation or ledger mutation was made.

**Intent anchor:** Find out whether a small change to a copy of the FP16 graph stops its non-finite audio without changing anything else, then put the measured result in front of Mat so he can decide what ships.

**Intent assessment: yes, as a plan.** The corrected amendment carries out the authorized fresh download and exact installed-file hashes while preserving the measured spike, output comparison and Mat's outcome decision. Round 1's acceptance of unchanged work and all supplied rulings remain given.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |

### New Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| none | none | no | none | none | none | none | none |

### F1 recheck

**Accepted — F1 fixed (FRESH_INPUTS, AC-127.12).** `confine_env` refuses an imported client, removes inherited `HF_*` and `HUGGINGFACE_*` names, and assigns private home/Hub/Xet/assets paths before `inputs()` and client import (`fresh-inputs.py:127-169,283-291`). `verify_client` checks the loaded constants, endpoint and offline flag. The added offline/staging refusals match Hub 2.3.0 (`fresh-inputs.py:46-52`; client `constants.py:65-74,160-194,342`). Explicit private paths override `XDG_CACHE_HOME`; scrubbed legacy assets/cache aliases fall back inside that home. `token=False` returns before token lookup, so even the differently spelled `HUGGING_FACE_HUB_TOKEN` cannot supply authorization (`fresh-inputs.py:172-189`; client `utils/_headers.py:139-149`). No token value is recorded.

**Accepted — actual download path.** Hub 2.3.0 forwards `cache_dir` and `force_download` to `_hf_hub_download_to_local_dir` (`file_download.py:1021-1045`). `force_download=True` bypasses matching local commit/metadata, matching local ETag/hash and cache-copy reuse, and raises on metadata failure instead of returning a local file (`:1342-1360,1379-1421,1429-1489`). The transfer helper also declines its existing-file early return under force (`:1991-1993`). A private, initially absent `HF_HOME` and explicit private `HF_XET_CACHE` eliminate the inherited Xet chunk-cache path; no live Xet transfer is claimed.

**Accepted — negative oracle.** The current selftest independently passed **32 of 32**, including the child that exercises real `hf_hub_download` and local-dir decisions while stubbing metadata/body transfer and forbidding `socket.connect` (`fresh-inputs.py:366-404,505-567`). The supplied mutants differ only by `force_download=False`, or an environment-activated early return in confinement. Independently rerun: exits **1**, **31/32** and **27/32**, respectively. The confinement mutant is rejected by `verify_client` before the fixture transfer, causing all five client checks to fail; its absent child result is not evidence that a token was sent or a connection attempted. A separate reviewer probe populated both inherited caches **and the private cache**, first with no destination and then with a matching stale destination. It used the real transfer helper with only metadata and `http_get` stubbed: two fresh body transfers, no authorization, zero connections, and refusal of metadata-error fallback. This directly covers the shared-cache path F1 named, beyond the selftest's stale-destination case.

**Not accepted / limit:** No residual F1 defect established. Offline stubs prove client selection and transfer invocation, not a completed upstream download or Xet body transfer. Those remain execution observations at row 0b, not prerequisites to this read-only plan approval.

### Fix regression scan

**Accepted:** Row 0b's seven-file/hash/pin/equality predicates, `force_download`, five `client_confined` constants and printed scrubbed **names only** agree with the code (task.md:66; implementation-plan.md:170,183,223,294,313,509-527). AC-127.12's 32/32 is true. D-798's app pins, unpinned config, default models folder, equality stop and row-1 overlay remain sound and within the given ruling; they were not reopened. The fixed H1-6 exception and H1-6a count of 12 are true (task.md:85-86). Baseline/gate registration adds only lint/selftest calls, as described (baseline.ps1:142-144; session-gate.ps1:145,151).

**Accepted:** S17's destination and private-home existence refusals occur before confinement/import/download (`fresh-inputs.py:113-118,283-291`; task.md:66). S18 still returns failure for different downloads, pinned commits or present installed files (`fresh-inputs.py:258-265,318-319`). INSTALLED_READ still hashes only the seven exact paths using binary reads; the fix introduces no installed-model enumeration, copy or write (`:64-69,220-227,292-294`). Receipt sanitization remains before write (`:273-279,295-307`), and scrubbed environment values never enter it. Prescribed run writes stay in the existing Temp receipt/model locations; selftest, child and reviewer fixtures stay inside the configured Temp folder and are cleaned there. The child patches network connect during the only client fetch and stubs both remote boundaries; no network request ran.

**Not accepted / limit:** No new material regression established. No `run`, baseline, session gate, product suite, smoke, build, inference, app database/settings read, installed-model read, clipboard write or forbidden file open occurred. Arbitrary caller paths, failed filesystem copies and unchanged evidence-reuse assumptions retain earlier rounds' stated limits. This approval does not claim execution completion, universal audio quality or shipping approval; D-797 still belongs to Mat.

### Round 3 checklist and evidence

All commands below ran from `P:/av-kit` with `PYTHONDONTWRITEBYTECODE=1`, `TMP=TEMP=C:/Temp/av-kit/s73/review` and `RECEIPTS_DIR=C:/Temp/av-kit`. Streams were captured under Temp and native exits preserved. Product/runtime execution is outside this review.

| Check | Result | Command / procedure | Exit | Decisive observation |
|---|---|---|---|---|
| F1 environment/client trace | pass | Codex inspected current script and installed Hub 2.3.0 constants, headers and local-dir/transfer code | null | Private caches before import, default endpoint, offline refusals, explicit no-token/force path |
| AC-127.12 selftest | pass | `rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py selftest` | 0 | `fresh-inputs selftest: 32 of 32` |
| Independent real-client cache/local fallback probe | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/r3_probe.py` | 0 | Two body calls; private and inherited cache bypass; stale destination bypass; metadata-error fallback refused; no authorization; zero connections |
| Supplied mutant sensitivity | pass | `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/r3_mutants.py` | 0 | Both selftest children exited 1: no-force 31/32; no-confinement 27/32. Driver 0 means expected failures confirmed |
| Fix-only contract/safety scan | pass | Codex compared changed plan/task text, S17/S18, installed hash loop, sanitizer and registered selftest calls with source | null | No new material defect; two prior clerical notes corrected |
| AV-1 through AV-6 (fix only) | pass | Codex inspected mutant diffs, actual client call path, result predicates and supplied ruling/source labels | null | Failing mutants and passing fix; remote I/O stubs leave client decision logic intact; no skip/placeholder or unsourced scope change |
| Product/runtime execution | n/a | User-prohibited for this review | null | Unchanged round-1 approval retained; no runtime result recertified |

```json
{"schema_version": "evidence.v1", "check_id": "s73-r3-fresh-selftest", "command": "rtk proxy .venv/Scripts/python.exe docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py selftest", "cwd": "P:/av-kit", "scope": "F1 recheck; offline fixture probes only", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 58d028ec7f6414ed2016f34e847222540d9d1177; working-tree SHA256 {\"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/baseline.ps1\": \"28b4356829ffa79885eb24d3c28d265c24f1383988d520432d19ab1092330cc5\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py\": \"0072cd61a843cac6fa57becba6028bea1a98433fa90e45ebf3d275aea55b824d\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/identity.py\": \"019a098669aacd59faa21f73879cf6c214695fbc92ae22523839d60bb71ec42f\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md\": \"391138d08e3711cd4ba44b26913b6eeb89c7e2e621c22549401b63fbdaec90c7\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/issue-resolve.py\": \"b6e4c4cbc1991112e5409f8aaae24a9ed081a0999a4578a5943c7846654875b6\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/phase-guard.py\": \"ed999c618176fc660f47b0da50bc3e6405583d1d57a622bd84157b3631a5de15\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/session-gate.ps1\": \"a19debaea74f019c6855336405da535d437cdc215f4debc2893c3cb120a5989a\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md\": \"441d92172ef895498202e2e4723ae3c3ece7d13dcc920484692586cfc1db441e\"}; installed huggingface_hub 2.3.0; PYTHONDONTWRITEBYTECODE=1; TMP=TEMP=C:/Temp/av-kit/s73/review; isolated fixture inputs", "output": "fresh-inputs selftest: 32 of 32; all five client checks and comparison/refusal/redaction cases ok", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s73-r3-real-client", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/r3_probe.py", "cwd": "P:/av-kit", "scope": "F1 recheck; offline fixture probes only", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 58d028ec7f6414ed2016f34e847222540d9d1177; working-tree SHA256 {\"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/baseline.ps1\": \"28b4356829ffa79885eb24d3c28d265c24f1383988d520432d19ab1092330cc5\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py\": \"0072cd61a843cac6fa57becba6028bea1a98433fa90e45ebf3d275aea55b824d\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/identity.py\": \"019a098669aacd59faa21f73879cf6c214695fbc92ae22523839d60bb71ec42f\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md\": \"391138d08e3711cd4ba44b26913b6eeb89c7e2e621c22549401b63fbdaec90c7\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/issue-resolve.py\": \"b6e4c4cbc1991112e5409f8aaae24a9ed081a0999a4578a5943c7846654875b6\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/phase-guard.py\": \"ed999c618176fc660f47b0da50bc3e6405583d1d57a622bd84157b3631a5de15\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/session-gate.ps1\": \"a19debaea74f019c6855336405da535d437cdc215f4debc2893c3cb120a5989a\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md\": \"441d92172ef895498202e2e4723ae3c3ece7d13dcc920484692586cfc1db441e\"}; installed huggingface_hub 2.3.0; PYTHONDONTWRITEBYTECODE=1; TMP=TEMP=C:/Temp/av-kit/s73/review; isolated fixture inputs", "output": "{\"authorization\": false, \"body\": 2, \"client_confined\": [\"HF_ASSETS_CACHE\", \"HF_HOME\", \"HF_HUB_CACHE\", \"HF_XET_CACHE\", \"HUGGINGFACE_HUB_CACHE\"], \"connects\": 0, \"hub_version\": \"2.3.0\", \"legacy_token_alias_not_sent\": true, \"metadata\": 2, \"metadata_error_refuses_local_fallback\": true, \"private_and_inherited_cache_bypass\": true, \"rows\": 7, \"scrubbed_names_only\": [\"HF_ASSETS_CACHE\", \"HF_HOME\", \"HF_HUB_CACHE\", \"HF_TOKEN\", \"HF_XET_CACHE\", \"HUGGINGFACE_ASSETS_CACHE\", \"HUGGINGFACE_HUB_CACHE\"], \"source_sha256\": \"0072cd61a843cac6fa57becba6028bea1a98433fa90e45ebf3d275aea55b824d\", \"stale_destination_bypass\": true}", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s73-r3-mutants", "command": "rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/r3_mutants.py", "cwd": "P:/av-kit", "scope": "F1 recheck; offline fixture probes only", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "HEAD 58d028ec7f6414ed2016f34e847222540d9d1177; working-tree SHA256 {\"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/baseline.ps1\": \"28b4356829ffa79885eb24d3c28d265c24f1383988d520432d19ab1092330cc5\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/fresh-inputs.py\": \"0072cd61a843cac6fa57becba6028bea1a98433fa90e45ebf3d275aea55b824d\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/identity.py\": \"019a098669aacd59faa21f73879cf6c214695fbc92ae22523839d60bb71ec42f\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md\": \"391138d08e3711cd4ba44b26913b6eeb89c7e2e621c22549401b63fbdaec90c7\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/issue-resolve.py\": \"b6e4c4cbc1991112e5409f8aaae24a9ed081a0999a4578a5943c7846654875b6\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/phase-guard.py\": \"ed999c618176fc660f47b0da50bc3e6405583d1d57a622bd84157b3631a5de15\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/session-gate.ps1\": \"a19debaea74f019c6855336405da535d437cdc215f4debc2893c3cb120a5989a\", \"docs/execution/plans/2026-11-14-tts-fp16-phase-guard/task.md\": \"441d92172ef895498202e2e4723ae3c3ece7d13dcc920484692586cfc1db441e\"}; installed huggingface_hub 2.3.0; PYTHONDONTWRITEBYTECODE=1; TMP=TEMP=C:/Temp/av-kit/s73/review; isolated fixture inputs", "output": "driver exit 0; m1_no_force.py selftest exit 1: FAIL client_fresh_body, 31 of 32; m2_no_confine.py selftest exit 1: all five client checks fail, 27 of 32; diffs confined to stated mutations", "fresh": true}
```

### Round 3 verdict

`approved` — F1 is fixed; zero open findings and no new High or Critical defect. The plan would deliver the registered objective within its stated stops and Mat's existing rulings. The amended download is review-approved; execution is for the coordinator under Mat's already supplied execute authorization. D-797 and any shipping amendment remain separate. The reviewer wrote only under `C:/Temp/av-kit`; the coordinator must save this complete report to the canonical rolling path.

**Report validation:** `rtk proxy .venv/Scripts/python.exe tools/validate_closeout_artifacts.py --review C:/Temp/av-kit/s73-plan-review-round-3.md --review-state-only --expected-review-mode plan --expected-target-plan docs/execution/plans/2026-11-14-tts-fp16-phase-guard/implementation-plan.md --max-review-rounds 3 --output C:/Temp/av-kit/s73/review/r3-report-state.json`, exit 0: `OK: review_mode=plan; round 3 of 3; verdict=approved; open findings=0`. `rtk proxy .venv/Scripts/python.exe C:/Temp/av-kit/s73/review/r3_validate.py`, exit 0: JSON verdict validates against review-verdict.schema.v2.json; round-1/2 bodies match exactly except F1 Status; exact F1/open/fixed table, none new row, table-only Findings, whole intent anchor, and unchanged hashes of all eight reviewed plan files pass. No raw home path appears in the report. No ledger or canonical report was written.

🕐 Completed: 2026-11-15 00:07 (EST)
