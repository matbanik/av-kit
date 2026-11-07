---
date: "2026-11-07"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-06-tts-load-fp16/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "s52-execution-2026-11-06-tts-load-fp16"
round: 2
---

# Critical Review: 2026-11-06-tts-load-fp16

> **Review Mode:** execution
> **Verdict:** approved — two non-blocking Medium findings; no High or Critical finding.

## Scope

Session 52's three MEU-119/120/121 handoffs, canonical implementation-plan/task, working-tree changes against HEAD `b6c38952d1a96e3bbdc9c11c94bcdb60330152b3`, relevant callers/regressions, plan-local tooling, decisions and saved execution evidence. Author: Claude Code/Anthropic; independent reviewer: Codex/OpenAI, class `avkit_independent_reviewer`. Applied IR-1–IR-7, AV-1–AV-6 and relevant claim/freshness checks.

**Intent anchor:** Session 52 makes a load that fails one of its checks leave the model that was loaded in place. It makes the first-run readiness check probe the models folder the backend actually uses, without creating it. It makes a fresh install preselect ONNX INT8 instead of FP16, and proves on a fresh packaged build that INT8 generates the fixed test set with no failure. A time-boxed spike looks for the FP16 cause, and its findings, or Mat's ruling on FP16, are recorded.

**Intent achieved: yes.** All writes in this review are under `C:/Temp/av-kit`. No repository edit, product-suite execution, app/package/spike execution, real model/session construction, network request or download occurred. Probes used offline, bytecode-disabled Python and in-memory TypeScript transpilation with scratch fixtures. The isolated smoke helper probe used a synthetic completed-job response; it did not start a backend or run a smoke phase.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | Medium | no | behavior | A probe write that creates its file and then throws, or an `accessSync` failure after a successful write, returns `false` without attempting deletion. On a fresh install this can leave `.write-probe-*` in the user's home/nearest existing ancestor. The scratch fault probes reproduced both cases. This is a bounded cleanup gap in `DIR_PROBE` (AC-120.4/AC-120.6), inherited from the existing-folder probe and newly relevant to the ancestor path; the readiness answer remains conservative and no directory is created. | `ui/src/main/setup-readiness.ts:108` | Keep the probe path outside the try and attempt best-effort unlink in a finally block, including after a partial write; add fault cases alongside the existing empty-directory assertions. | open |
| F2 | Medium | no | control-defeat | `SENTENCE_SMOKE` trusts the WAV header's frame count. A 44-byte WAV declaring 100 frames but containing **zero PCM bytes**, returned by a synthetic `Done` job inside the output folder, produced `wav_samples=100` and passed the phase's rejection predicate. A truncated-output/writer regression could therefore satisfy the task's audio check (AC-121.8). **mechanism: task-row-completion-predicate**. This does not invalidate these runs: independently reading every retained WAV from both INT8 runs found 149 + 149 complete, nonempty payloads. | `tools/smoke_packaged_tts.py:357`; acceptance at `:710` | Read the declared frames and require a nonempty payload of the expected byte length; add a header-only/truncated WAV negative fixture. | open |

Both findings are non-blocking under the Verdict Rule: F1 leaves a small scratch-file artifact on an I/O error, while F2's evidentiary gap was independently closed for the actual outputs under review. Neither demonstrates a material failure of the delivered goal. No formatting/process-paperwork findings were sought or raised.

## Checklist Results

### Q1 — Delivered behavior and routes

**Accepted.** The four adapter checks precede unload (`tts/adapter.py:302`, `:307`, `:313`, `:317`, `:332`). The production service delegates at `services/models.py:171`; REST `/models/load` and MCP converge there. Generate requires an already loaded model (`services/tts.py:226`); it has no separate loader. Settings stores preferences, and the renderer passes its resolved device through `postLoad` (`tts-commands.ts:205`). There is no alternate unload-before-check route introduced here.

`MODELS_DEFAULT` equals `settings.py:67`; the readiness probe creates no directory. A fresh catalog selects INT8. The two recorded offline packaged INT8 runs each completed 149/149 jobs, with actual retained audio independently checked. The spike's results are in the MEU-121 handoff and the issue's verification; FP16 remains open/offered and D-336 awaits Mat. F1/F2 qualify cleanup and future smoke detection, not those observed outcomes.

### Q2 — Load order, failures and concurrency

**Accepted.** `LOAD_CHECKS` order is weight → device → format → runtime → unload. No loaded-model/session/device field changes on a refused check; the runtime capability memo is the intended `RUNTIME_PRESENT` state. Independent probes retained the same sentinel model/session/device on missing weight, device exception, unsupported format, absent runtime and raising runtime. Each emitted exactly one `tts.load_failed`; raising runtime logged its class without its text/detail. Existing cause/device logging, `DEVICE_RESOLVE`/`LOAD_FALLBACK`, and `LOAD_ERROR_HTTP` remain intact; `ModelLoadError` and `ValidationError` still map to 422 (`avkit_api/errors.py:28`). The service's earlier AC-117.8 refusal is unchanged.

Construction still occurs after unload and commits local results at the end; AC-119.7/.8 preserve the accepted unloaded-on-construction-failure behavior. A′ makes the two old import tests reach precisely that later branch without weakening their assertions. Amended AC-75.9 changes only the intended kept-A assertion; its cause, engine-call, logging, path and unloaded-vocab checks remain (`test_tts_device_resolution.py:639`, `:649`). The shared adapter and existing unsynchronized successful-load/generate windows predate this delta; moving read-only checks ahead of unload introduces no new mixed committed state or model swap during a failed check. This is not a new concurrency guarantee.

### Q3 — Home-folder scrub and sinks

**Accepted within the specified path boundary.** `console_field` runs single-line conversion, `scrub_home`, link replacement, redaction and the limit in that order (`health.py:125`). Independent probes covered Windows case folding, slash forms, the bare home, OSError quoting, JSON-escaped backslashes, sibling/nested-path exclusion and the cut boundary. Every member of `CONSOLE_FIELDS` was scrubbed through the actual `_process` method into stdout, ring and file payloads (`health.py:207`, `:229`, `:234`). The raising-runtime path emits no raw cause text. No further in-contract app-surface leak was found; D-337 explicitly raises the 8.3 exception with Mat.

The AC-119.10 surface test is honest: exact ring message, raw-stdout username absence, decoded JSON message path assertions, and file assertions test distinct surfaces (`test_services.py:3379`). The temporary setup amendment precedes Red; it asserts the new names exist instead of turning absence into an import/setup failure. Existing Console assertions are unchanged, and the saved TEMP-under-home run passed 230 tests. Raw home paths in copied review/runner diagnostics were not treated as app leaks.

### Q4 — Models directory and probe

**Accepted for the requested default/no-directory-creation behavior; F1 records the error cleanup limit.** Both fallbacks use the backend's expanded `~/.avkit/models`, while a stored setting still wins. The stat/dirname walk finds the nearest existing folder, stops on a file or unreadable entry, and terminates at a missing root (`setup-readiness.ts:85`). Scratch probes returned true with no new entries for a missing nested directory and false beneath a regular file. Success deletes the probe; partial-write/access failures can leave it behind, as demonstrated in F1.

The amended AC-120.2 changes the source-backed default, and AC-120.1 ties it to the backend. The unchanged AC-58.12 tests still test Settings layout/readiness-count/dirty-dot behavior; their count assertion does not independently certify filesystem correctness. That producer behavior is covered by the readiness tests and the recorded real probe, whose model snapshots show zero lasting changes.

### Q5 — Preselection

**Accepted.** The chosen runnable row wins, then the catalog's loaded row as previously agreed, then downloaded rows ranked INT8 → FP32 → stable catalog order, then the first runnable ranked row (`tts-controls.ts:118`). Scratch execution confirmed fresh → INT8, FP16+FP32 downloaded → FP32, all ONNX downloaded → INT8, and only FP16 downloaded → FP16. Unavailable rows are filtered; the loaded-row exception and missing-availability compatibility remain unchanged.

AC-117.13/.14 and AC-63 retain their assertions. The new unit fixture reads the real seed; AC-121.6 uses the compiled Electron app with a fresh-state catalog seam and asserts both enabled FP16 and selected INT8. This is an honest built-renderer selection test, complemented by the seed contract and the separate real packaged backend smoke.

### Q6 — Smoke, spike and decisions

**Accepted execution evidence.** FP16 Red exited 1: 149 jobs, exactly 12 failures, all `Failed` with `generated audio must be finite` and zero samples, no other error. INT8 Green and final gate Green each report 149 `Done` rows with positive frames and no failures/errors. Each onedir is outside the checkout, fresh app-data/home/cache folders are used, dead proxies are set, and registration takes the existing-file fast path. The baseline checked 122 installed packages without installing any, verified cached assets, and the model snapshots remain unchanged. F2 shows why future WAV payload validation should be stronger; all 298 retained Green outputs were read and were complete/nonempty.

The spike ran about 15 minutes within its two-hour box: E0 11 failing pairs, E1 15/16/16, E2 honestly `not_run` with offline-resolution errors, E3 70/77 non-base nudges finite, E4 16/11. E5's two exact hashed pins installed with `--no-deps --require-hashes` into the Temp target; its before/after venv distribution list, pyproject and lock match. Cache additions are only onnx/ml-dtypes, S5 is empty, and the analysis child is offline. Other experiments inherit dead proxies; only E5's install receives the saved fetch environment.

E5 measures first non-finite node outputs at `/decoder/decoder/generator/Div` with finite inputs across the 11 inspected pairs. The `atan2`/STFT interpretation comes from the separately identified outside reports; local E5 did not measure zero counts or distinguish NaN from Inf. D-336 keeps 0/0 a hypothesis and distinguishes the DirectML-tone report from this FP16 failure. D-336 and D-337 both preserve an explicit do-nothing state and authorize no work. D-336's “keep as shipped” is read with the explicit D-330 only-FP16-downloaded exception. D-338 truthfully records `done`, not S13, as the reason to send the outcome brief. No ruling on those choices is made here.

### Q7 — Tests and Red rigor

**Accepted required Red evidence.** Replayed `red-check.run` against all four original receipts and their `.txt.exit` sidecars: every child exit is 1, required title counts are 8/1/4/4, and there are zero attribution problems. A synthetic setup-error receipt was rejected, and AC-100.7 did not match AC-100.70. No suite was rerun. The fail-to-pass receipts agree with the actual asserted paths and baseline behavior; guards that intentionally pass Red are identified as such.

| Tests audited | Grade | Decisive assertions / limit |
|---|---|---|
| AC-119.1, .2, .3, .4, .5 | Strong each | Exact failure/cause/log, A's id/device, zero unload and engine calls; .4 forbids detail/text. |
| AC-119.6, .7, .8 | Strong each | Memo calls/counts; exact constructor failure and unloaded state. |
| AC-119.9 | Strong contract | Real service/adapter behind HTTP; fake session disclosed; 200 → 422 envelope → retained status. |
| AC-119.10, amended AC-75.9, A′ and AC-115.9 guards | Strong | Exact strings/sinks and retained error contracts; no existing Console expectation weakened. |
| AC-120.1–.6 | Strong for declared cases | Backend-default equality, real SQLite fallbacks, directory/file state; exceptional cleanup gap F1. |
| AC-121.1–.5 / unchanged AC-117.13 | Strong | Seed-derived selection and exact preference/availability cases. |
| AC-121.6 / unchanged AC-117.14, AC-58.12 and AC-63 | Adequate integration / Strong component checks | Built Electron with explicit seams, exact selected values and UI behavior; no claim that mocked catalog equals a full backend install. |
| AC-121.7/.8 smoke | Adequate | Real packaged jobs and failing-output detection; WAV-payload subcheck is weak against truncation (F2), independently repaired for these saved results. |
| AC-121.9 | Adequate record check | Experiment JSONs, issue verification and decision briefs agree; no causal fix falsely claimed. |

`test-ids.ts` has no session diff; HEAD/working content agrees after Git's LF/CRLF conversion. Independently hashing the actual raw working prefix reproduced AC-51.6's `6E569F820459EA2BE3264324635C0A9D22FC4AACFA2DAD6A6B54F840870FF454`; AC-81.13's registry test remains unchanged and passed in the saved full UI run. F1/F2 are the demonstrated gaps, not hidden passes represented as fresh product testing.

### Q8 — Freshness, evidence and write scope

**Accepted.** Recomputed state with `ELECTRON_RUN_AS_NODE` unset:

`b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055`

The initial sandbox uv-cache access failed; using a Temp cache with offline/no-sync preserved the project interpreter. A process-local Git configuration then preserved repository ownership access and excluded only `.claude/settings.local.json`, which was never opened. The resulting identity exactly matches both gate endpoints and all full evidence records. All 8/7/10 handoff evidence records validate against that state. Saved gate: pytest 1293, UI 1172, MCP 470, Electron 46; all registered steps exit 0, no baseline failure excused. No prohibited full gate or suite was rerun.

Parsed register comparison against HEAD reproduces exactly 13 changed fields, limited to the two issues' status/resolution/verification and the FP16 issue's three verification fields. Comparing row 12's saved pre-write register confirms exactly those three issue ids changed. FP16 stays open. An independent listing/stat comparison against `models-before.json` found 159 files and zero changes, agreeing with all row/gate snapshots. The specified package/voice/runtime/model/spaCy download restrictions were respected, with only the approved E5 pair fetched; the transient Settings probe is the accepted exception to a completely write-free model folder.

### IR / AV disposition

| Check | Result | Observation |
|---|---|---|
| IR-1 live runtime evidence | pass | Real packaged generation and Electron evidence exists and matches the tested state. |
| IR-2 fake behavior | pass | AC-119.9 routes through real service/adapter; fake assets/session prevent downloads and do not manufacture retention. |
| IR-3 error mapping | pass | Preserved 422 mapping/envelope, accepted later-load failures, unchanged 404/409 boundaries. |
| IR-4 generalization | pass | Shared loader and all Console allowlisted fields inspected/probed. |
| IR-5 required AC test audit | pass | Grades and required Reds above; F2 explicitly limits the smoke's corruption detection. |
| IR-6 external boundaries | pass | No new product input surface; existing strict load/generate/settings schemas and no-payload IPC retained. |
| IR-7 scope/coverage | pass | All three MEUs and declared ACs represented; FP16 outcome and MEU-125 boundaries remain explicit. |
| AV-1–AV-6 | pass | Source-backed cases, genuine Red assertions, no changed skip/xfail/expectation bypass or implementation placeholder. |
| H2 reflection/metrics/commit | n/a | Follow this review by design; not execution-review deficiencies. |

### Commands executed and durable reviewer evidence

All commands ran from `P:/av-kit` through `rtk proxy`, with streams redirected under `C:/Temp/av-kit`, child status captured before reading. Python probes used `-B`, `HF_HUB_OFFLINE=1`, `PYTHONDONTWRITEBYTECODE=1`; temporary-file probes also set TMP/TEMP to `C:/Temp/av-kit/s52/tmp`. Commands below are the substantive invocations; the `s52-review-*` receipts retain the wrappers/output. Source/diff/receipt reads used `git diff HEAD`, scoped `rg`, and `s52_review_read.py`.

```json
{"schema_version":"evidence.v1","check_id":"review-current-state","command":"rtk proxy uv run python -B docs/execution/plans/2026-11-06-tts-load-fp16/identity.py --state-only","cwd":"P:/av-kit","scope":"current D6 state; ELECTRON_RUN_AS_NODE unset; offline/no-sync, Temp uv cache; process-local safe.directory and sole ignored settings path","phase":"identity","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055","output":"Exact match to both original full-gate endpoints and the three handoffs."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-python-probes","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52_review_python.py","cwd":"P:/av-kit","scope":"actual adapter and Console methods; isolated WAV helper; saved PCM; parsed issue diff","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055","output":"Five refusal probes kept A/session/device. Five path forms and every allowlisted field scrubbed at stdout/ring/file payload. Header-only negative: 44 file bytes, zero PCM bytes, wav_samples 100, phase_rejects false (F2). Both retained Green folders: 149 WAVs each, zero empty/truncated. Register diff: 13 fields, exactly the stated scope."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-ts-probes","command":"rtk proxy node C:/Temp/av-kit/s52_review_ts.cjs","cwd":"P:/av-kit","scope":"in-memory actual readiness/preselection source, scratch filesystem/fault collaborators","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055","output":"Missing folder true/entries []; file ancestor false. Both create-then-write-error and post-write-access-error returned false with a .write-probe-* entry (F1). Four selection cases returned INT8, FP32, INT8, FP16 as contracted."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-evidence-controls","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52_review_contract_checks.py","cwd":"P:/av-kit","scope":"original Red attribution, negative controls, current-state evidence validation, real models stat-only comparison","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055","output":"All four Red receipts child exit 1; 8/1/4/4 required titles, zero problems. Setup error rejected and AC-100.7/AC-100.70 boundary preserved. MEU-119/120/121: 8/7/10 valid evidence records, one matching full record each. Models: 159 files, zero changes. Test set: 40 sentences, 8 paragraphs."}
```

```json
{"schema_version":"evidence.v1","check_id":"review-saved-execution-audit","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52_review_evidence.py","cwd":"P:/av-kit","scope":"specified baseline/Red/Green/runtime/gate receipts and smoke/spike JSONs","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+906c583e2bb62512fd468de2a8375a351f1c6ce5051a369d4cd0f88bc7f97055","output":"Saved full gate: Python 1293, UI 1172, MCP 470, Electron 46; all registered steps exit 0. FP16 12/149 finite-audio failures only; both INT8 runs 149/149 Done, zero failures. Spike stop done, no candidate, E2 offline not_run, E5 exactly two hashed installs and unchanged venv/locks."}
```

## Verdict

**approved**, `intent_achieved: yes`. No evidence-backed High/Critical defect remains. F1 and F2 are concrete non-blocking follow-ups; they do not require another review round for this delivered state. D-336/D-337 remain Mat's open decisions, without authorizing an FP16 change or a short-path fix. H2 and any commit remain with the coordinator and Mat under their existing gates. Report delivered only to `C:/Temp/av-kit/s52-exec-review-round-1.md`; the coordinator owns canonical publication.

Final verification: the independent identity recheck after all review probes reproduced the same tested state. `validate_closeout_artifacts.py --review-state-only` accepted this report as execution round 1/6, approved, with zero open blocking findings. The JSON verdict passed the repository's v2 schema and agrees with the report's two non-blocking findings.

🕐 Completed: 2026-11-07 10:39 (EST)


## Recheck (Round 2)

Date: 2026-11-07. Reviewer: Codex/OpenAI, class `avkit_independent_reviewer`; author: Claude Code/Anthropic. Scope is F1, F2 and task rows C1–C7 only. The round 1 judgments on all other work stand. The unrelated instruction change and the coordinator's C8–C10 publication/closeout steps are outside this review. The initial report above is preserved, except its frontmatter round, verdict and open-findings count.

### Prior Pass Summary

| Finding | Prior Status | Recheck Result |
|---|---|---|
| F1 | open | fixed |
| F2 | open | fixed |

### Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|
| F1 | Medium | no | behavior | `DIR_PROBE` cleanup is fixed (AC-120.4/.6, D-342). Independent execution of the actual function source against scratch folders returned false and left no entry after a create-then-write exception, post-write access exception, and unlink exception. Removing the new cleanup in memory left one file in each original negative case. Saved C1 Red: two assertion failures, ten passes, child exit 1; C2 Green: thirteen passes across two files, clean types/lint. | `ui/src/main/setup-readiness.ts:109`; cleanup `:115`; tests `ui/tests/unit/setup-readiness.test.ts:186` and `:201` | Retain the cleanup and the two regression cases; no further correction required for F1. | fixed |
| F2 | Medium | no | control-defeat | `SENTENCE_SMOKE` / `PACKAGE_SMOKE` header trust is fixed (AC-121.8, D-343; mechanism: task-row-completion-predicate). The actual `_generate` counts header-only and truncated payloads as zero. Removing the completeness check in memory makes both new negative assertions fail. C3 Red: two assertion failures, one positive guard pass, child exit 1; C4 Green: three passes, clean Ruff. All 149 retained run-2 WAV payloads independently read complete/nonempty, with frame counts matching the saved result rows. | `tools/smoke_packaged_tts.py:357`; acceptances `:434` and `:716`; tests `tests/tooling/test_smoke_packaged_tts.py:52`, `:59`, `:66` | Retain the payload check and all three regression cases; no further correction required for F2. | fixed |

No new finding. No evidence-backed High or Critical defect was found within this recheck.

### RF1 — Probe cleanup and regression coverage

**Accepted.** The path is named before the try, and every failure of write/access/unlink enters the same best-effort `rmSync(probe, { force: true })` cleanup. The isolated Node probe transpiled the actual `nearestExistingEntry` and `probeModelsDirWritable` source in memory; only the injected failing collaborator was replaced. Write-after-create, access-after-write, and unlink failures each returned false with an empty folder and no intermediate directory. Existing-directory success returned true with no entry, missing nested-directory success returned true without making it, and a regular-file ancestor returned false without modification. The success sequence remains write → access → unlink → true. The C2 delta does not alter defaults, stored-setting resolution, the Settings UI, or AC-58.12; AC-120.1–.6's round 1 acceptance stands.

The two added unit cases are **Strong**: real create/read/remove behavior, a single replaced call, exact false/empty-directory assertions, and restoration in `finally`. The module mock forwards all other calls to the real filesystem and the replaced implementations are restored; it does not turn the other cases into filesystem stubs (`setup-readiness.test.ts:26-37`, `:189-197`, `:204-211`). Both real saved Reds reproduce their exact assertions; independently replaying `red-check.run` found zero problems. The unchanged shared/full checks also passed in the saved fresh gate.

**Limit, not a reopened finding:** “no file on any conceivable path” is not guaranteed. If the cleanup operation itself is also denied or fails, the inner catch returns false and a file can remain (`setup-readiness.ts:119-122`). The isolated double-fault probe confirmed that boundary. D-342 expressly specifies best-effort removal, including retry after unlink failure; the reported omissions are fixed. A further filesystem failure is the same mutation class, not a newly demonstrated material defect.

### RF2 — WAV payload, consumers and packaged evidence

**Accepted.** `wave.readframes(declared)` must return exactly `declared * sample_width * channels` bytes before the declared frame count becomes `wav_samples` (`smoke_packaged_tts.py:360-364`). Header-only 100-frame and truncated 50-of-100-frame files returned `(wav_samples, wav_declared) == (0, 100)`. An additional 9,999-of-10,000-frame case also returned zero, so even a header above the offline threshold cannot pass. Complete 100-frame mono and 10,000-frame, 24-bit stereo files retained exactly their former frame counts; a zero-frame complete header still returns zero and fails acceptance. Malformed WAV reads raise and the existing phase exception handlers fail the phase/job.

The only consumers of `_generate`/`wav_samples` are the offline and sentences phases (`:428-435`, `:710-724`). The sentences phase refuses zero; offline refuses 8,000 or fewer. Online generates nothing. `wav_declared` adds diagnostic data without changing the meaning of complete-file counts. The three tooling cases are **Strong** for this defect: exact count/declared assertions for two corrupt files and exact Done/count/output-directory assertions for the complete guard. Breaking the payload check makes both negative assertions fail, while the positive guard preserves compatible counting.

The recorded run-2 sentence smoke passed on `kokoro-onnx-int8`: 149 jobs, all Done, no failures/errors, minimum 55,200 frames. The stdout receipt's results, phase, variant, times and verdict equal the JSON; stdout intentionally omits `backend_tail` (`:767`). Independently reading every retained WAV found 149 complete/nonempty payloads and exactly the same frame-count multiset as the JSON. Thus the original complete-output evidence and this new check mean the same thing. The gate rebuilds the onedir, copies the backend outside the checkout, and invokes the current **repository smoke runner** against that copy (`session-gate.ps1:118-126`, `:149-150`); no embedded copy of the smoke runner inside the executable is claimed. No backend/model execution was repeated by this reviewer.

### RC — Registers, freshness, evidence and output exposure

**Accepted register scope.** A recursive parsed comparison with `C:/Temp/av-kit/s52/register-before-resolve.yaml` found exactly 11 changed paths: eight scalar resolve fields on issues 112/113, one `meu_links[3]` append on issue 110, and appended issues 114/115. No other existing field changed. The resolve set-file matches the current resolve fields except the single disclosed `SMOKE-TTS-WAV-HEADER-TRUSTED.resolution_path` correction; the current text correctly names sentences and offline, never online. The corrected register's SHA-256 is `0bcd5af73a865097f2353d1f9ad9bb51c503c6924f94629c6f6f8e0ed34285fa`, LF 4176, CRLF 0, exactly matching `s52-c5-register-fix`. Both resolved issues are resolved; the two new issues and FP16 issue stay open.

MEU-127 consistently names `svc-tts-fp16-phase-guard`, phase 3 / P2, matrix item 3.18, dependency MEU-121, and the `tts-fp16-phase-guard-residual` anchor (`meu-status.yaml:3320`, matrix `:47`, `03-service-layer.md:677`). It is pending, spike first, with the shipping outcome returned to Mat and no upstream post. Both saved render checks pass and the current input identity binds their source and rendered files. **Clerical qualification:** `docs/BUILD_PLAN.md:47` still enumerates the older November 4 phase-3 residuals; it does not explicitly name MEU-127 there. Its generated summary does include the new total/P2 range (`:67-68`), and the authoritative scheduled MEU/matrix/03 entries agree. This does not hide or unschedule the follow-up and is not a new finding.

**Accepted freshness.** With `ELECTRON_RUN_AS_NODE` unset, offline/no-sync uv and a Temp uv cache, the requested identity command reproduced:

`b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e`

Only process-local Git ownership configuration and the authorized exclusion of `.claude/settings.local.json` were applied; that file was never opened. This exactly matches gate run 2's before/after endpoints and the three new full-gate records. The gate has 23 registered steps, all exit 0; pytest 1296, UI 1174/112 files, MCP 470/35 files, Electron 46, no excused baseline failures, model snapshot 159 files/zero changes. The first attempt's identity is not accepted as current evidence after the scalar correction; the rerun is the matching full gate.

Each new C1–C7 record's decisive results agree with the saved receipt/current state. The historical Red/Green/register records describe their row states; they do not all carry the final hash. The three `s52-gate-c6` full records carry the exact final hash, and `durable_evidence.evidence_problems(..., require_full=True, expected_state=current)` accepted all three handoffs. The C1/C3 child exits are 1, while the Red-validator rows exit 0 for proving those failures; those are not product-pass exits. The disclosed set-file text remains historical, and is not mistaken for the corrected register.

**Accepted output boundary.** C2 adds no error-text/path logging: faults return false after cleanup. C4 adds an integer `wav_declared` and validates payload length; it adds no raw path/cause interpolation to an application log, stdout or Console. The new fault strings contain no user path. Existing short-home-form and tracked-home-path limits were explicitly raised with and ruled on by Mat (D-337/D-344), and filed; they are not silently accepted residuals. No new C1–C7 runtime exposure was demonstrated. All paths in this recheck use `<HOME>` if a home folder would otherwise appear.

### Independent commands and decisive evidence

All reviewer writes are under `C:/Temp/av-kit`. Source/diff/receipt reads used `rtk proxy`, preserved exits and Temp receipts. Python ran with bytecode disabled and `HF_HUB_OFFLINE=1`; TMP/TEMP were set to `C:/Temp/av-kit/s52/tmp` for probes. No repository write, suite/app/gate/package/spike execution, model construction, network request or download occurred.

```json
{"schema_version":"evidence.v1","check_id":"r2-dir-probe","command":"rtk proxy node C:/Temp/av-kit/s52_r2_probe.cjs","cwd":"P:/av-kit","scope":"actual readiness function source transpiled in memory; scratch filesystem with one injected operation failure","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e","output":"write, access and unlink faults: false, entries [], no nested directory. Existing and missing writable-folder success clean; file ancestor false. Removing cleanup leaves one file in both original negative cases. Denying cleanup as well confirms best-effort limit."}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-wav-probe","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52_r2_wav.py","cwd":"P:/av-kit","scope":"actual _generate with fake Done backend and scratch WAVs; retained gate WAV reads","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e","output":"Header-only, truncated and zero-frame WAVs count 0; complete mono 100 and stereo 10000 retain exact counts. Removing check breaks both negative assertions. Retained 149 gate WAVs complete/nonempty; exact frame-count multiset matches JSON; minimum 55200."}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-register-gate-audit","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52_r2_audit.py","cwd":"P:/av-kit","scope":"parsed pre-C5/current register diff, three handoffs, MEU-127 scheduling, saved D6 receipts and smoke JSON","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e","output":"11 changed register paths: eight resolve scalars, one MEU link append, two appended issues. Three handoffs accept current full evidence. Gate: 23 steps all exit 0, identical endpoints. INT8 149/149 Done, min 55200. Original round-1 report hash matches supplied SHA-256."}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-red-controls","command":"rtk proxy .venv/Scripts/python.exe -B C:/Temp/av-kit/s52_r2_controls.py","cwd":"P:/av-kit","scope":"replay original C1/C3 Red attribution; register correction hash; smoke stdout versus saved JSON","phase":"targeted","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e","output":"C1 and C3 each have child exit 1, two required assertion failures, zero red-check problems. Corrected register hash matches the handoff. Smoke stdout/saved decisive fields match; backend_tail omitted from stdout by design; PASS footer present."}
```

```json
{"schema_version":"evidence.v1","check_id":"r2-current-identity","command":"rtk proxy uv run python -B docs/execution/plans/2026-11-06-tts-load-fp16/identity.py --state-only","cwd":"P:/av-kit","scope":"full current input identity, ELECTRON_RUN_AS_NODE unset; UV_OFFLINE=true, UV_NO_SYNC=true, Temp uv cache; authorized sole settings-file exclusion","phase":"identity","exit_code":0,"result":"pass","tested_state":"b6c38952d1a96e3bbdc9c11c94bcdb60330152b3+dc766c783a9331271420a972423ec661ede36dc84e213d7e6e333adcbd70758e","output":"Exact match to both gate-run-2 endpoints and all three new full-gate records."}
```

### Verdict

**approved**, `intent_achieved: yes`. F1 and F2 are fixed; zero new/open findings. The round 1 intent judgment stands with these corrections verified. The remaining report publication, ledger acceptance and C10 closeout belong to the coordinator; this review does not claim those actions have occurred. Report destination: `C:/Temp/av-kit/s52-exec-review-round-2.md`; canonical publication remains with the coordinator.


🕐 Completed: 2026-11-07 12:20 (EST)
