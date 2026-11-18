---
date: "2026-11-18"
review_mode: "plan"
target_plan: "docs/execution/plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ff-plan-2026-11-17-tts-fp16-guard-ship"
round: 1
---

# Critical Review: tts-fp16-guard-ship

> **Review Mode:** plan
> **Verdict:** approved

## Scope

**Intent anchor:** when a user loads ONNX FP16 Kokoro, the app builds its ONNX Runtime session from Session 73's guarded graph, made in memory from the user's own downloaded file and checked against Session 73's source hash (`ba4527a8…`) and result hash (`9037c82b…`), so the packaged `--phase sentences` smoke passes 149 of 149 jobs where today it fails 12; a file with any other size or hash loads exactly as shipped; a splice that refuses or gives another hash loads the file as shipped and logs one warning with no path; no file in the models folder is written, renamed or added; INT8 and FP32 load exactly as before; FP16 stays never preselected (D-330, D-331); nothing is posted to Hugging Face and no new package is added. Scripts and tests prove each part, with no manual check.

Reviewed the complete working-tree plan and task, grouping Session 74 and its rulings, the issue and resolution path, HDP, expert-pass receipt, referenced adapter/model-manager/build and smoke code, test pins, registration precedent, and scratch splice/synthetic/WAV probes. Applied PR-1 to PR-9 and the Materiality Gate. Claude Code/Anthropic authored the plan; Codex/OpenAI is the independent reviewer.

The tree is `main` at `174bafa8a9ff327d38e54bd36f3edcb0e0b62085`. The target folder contains only the two plan documents, with 17 ACs and 27 unstarted task rows. Future product/test/handoff paths are absent. Plan-local checkers are explicitly scheduled for creation; this review validates their specified predicates and existing reference implementations, not future code that is not yet written.

Only `C:/Temp/av-kit` was written. No product suite, package install/sync/lock, build, application process, or network request ran. SQLite read only private copies of Session 73's databases. Forbidden files and the real models/settings/database were not opened. The coordinator owns canonical publication and ledger recording.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal and complete proof

Accepted: AC-144.1–.3 and .12 bind the splice to the intended graph and bytes; .4–.7 cover the gate, pass-through and refusals; .8, .12, .14 and .15 cover model-folder preservation; .9–.11 cover the actual adapter and unchanged variants. AC-144.13–.15 and rows 3/7/8 require the current packaged Red, Green and INT8 proofs with WAV identity by job. AC-144.16 preserves preselection, and .17/rows 1 and 9 register and close the work. Scope and source hashes guard the package, catalog and unrelated surfaces. No manual behavior-check row is substituted.

Executing these contracts successfully would deliver the goal. No missing goal clause or concealed required deliverable was demonstrated. This is plan approval, not an execution-pass claim.

## Q2 — Splice correctness, memory and hashes

Accepted: `GUARD_IN_MEMORY` identifies the single named Div and its sole Atan consumer, refuses already guarded/unknown shapes, rewrites that input, inserts IsNaN/Where and the FP16 positive-zero initializer, and preserves other serialized fields. `ONE_JOIN` constructs the graph/file with source memoryviews and one final join. The exact source and result hashes contain parser mistakes: unrecognized input is not spliced, and a different output cannot reach ORT.

The independent scratch probe reproduced **163,235,204 bytes**, byte-equal to Session 73's guarded file, with result SHA-256 `9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33`. Peak allocation including the read was **329,180,563 bytes**, below S10's limit. Real ORT 1.31.1 loaded those bytes. The synthetic graph matched both pins, changed 0/0 from NaN to +0, preserved finite output bytes, and refused already guarded/truncated/overlong-varint/unsupported-wire inputs. No blocking objection remains; production `guarded_model` is still an execution deliverable.

## Q3 — Gate, pass-through, refusals and Red

Accepted: `GUARD_GATE` bypasses every non-FP16 id before stat, then rejects missing/wrong-size or unknown-hash files without patching. `GUARD_REFUSE` returns the path on a splice exception or wrong result hash and logs only the event, variant, outcome and class-name/result-hash reason; `GUARD_APPLIED` emits one info event. Source bytes are hashed and spliced as the same in-memory object, avoiding a second path read between those operations.

AC-144.3–.7 have concrete refusal/pass-through/logging oracles. Row 4's first `find_spec` assertion and lazy helper import make today's missing guard an assertion failure rather than collection/setup failure; the Red checker requires the named AC prefixes with digit boundaries. Existing pin tests must pass before Green and remain unchanged. No guard-path failure or vacuous required Red was demonstrated.

## Q4 — Adapter integration and scope guards

Accepted: `BOTH_SESSIONS` inserts one call before the CUDA branch and supplies its result to both constructors, preserving CUDA-to-CPU fallback on the same bytes object. The module-level import exposes the new module to PyInstaller analysis. A real serialized session built from the guarded model without external-data files in the independent probe. Synthetic adapter integration, the recording CUDA fake, real CPU integration, and the four unchanged pin files cover the relevant paths. S14, catalog/voices/preselection pins and source hashes keep INT8/FP32 and other surfaces unchanged.

One nonblocking wording correction: task.md:55 says the fake replaces `onnxruntime.InferenceSession`, but its cited precedent actually patches `avkit_infra.tts.adapter.InferenceSession` (`test_tts_device_resolution.py:126`), the alias the adapter calls. Use that cited target. The intended fake and assertions are clear; a wrong patch would fail the required integration test rather than silently approve missing behavior.

## Q5 — Packaged proof, WAV mapping and process safety

Accepted: `BUILD_SAME` checks today's pre-change build against both earlier failure sets and all 137 control WAVs. Green and INT8 each require 149 successful jobs and equality against their corresponding Session 73 WAVs. `WAV_BY_JOB` uses unique `(text_hash, voice)` keys from copied DB/WAL files, avoiding collision-suffixed filenames. The snapshot compares relative names, sizes, hashes and mtimes. S7–S13 and S15 stop on build/input/copy/hash/WAV/process/load failures; exclusive new run folders preserve prior evidence, and S13 performs no additional cleanup.

Independent rechecking confirmed equal 149-key sets, one row per key, Done counts 137/149/149, all 137 control WAVs equal to guarded, and Session 52/73's same 12 finite-audio failures. The three new smokes remain execution obligations.

The literal “backend is never killed” wording at implementation-plan.md:65/task.md:38 is inaccurate: the unchanged smoke calls `Backend.stop()` in `finally` (`tools/smoke_packaged_tts.py:730`), which terminates its retained child and has a kill fallback (`:162–169`). An AST-only fake-process probe confirmed both branches; no real process was launched or stopped. The source handover expressly permits ending the smoke by its recorded process id (`session-74-prompt.md:149–150`), and the stored Popen object targets its own child, not another session or an image name. Clarify the plan to distinguish this existing owned-child teardown from S13's detect-only leftover handling. This wording mismatch does not defeat the packaged proof or authorize broad cleanup, so it is nonblocking. The smoke's initial app-data/out deletion encounters absent paths on the prescribed first invocation in each new S9-checked run folder; no rerun over retained evidence is approved here.

## Q6 — Registration and records

Accepted: D-1135 A and D-1136 A are carried out as Mat's rulings. Row 1 uses the established registration adapter through `tools.meu_status.model` (the CLI has no add command), with expected content hashes, `band: P2`, dependency MEU-127, the new 03 section and matrix row 3.21. Rendering and later status changes go through `tools/meu_status.py`; generated files are not hand-edited. Row 9 adds MEU-144 to the issue's existing links, sets verification/resolution status, compares the unchanged resolution-path value, and checks the grouping's single changed row.

D-1137–D-1139 describe reversible internal design, tests and record mechanics under the two rulings. No additional M hit outside the handed allowance was demonstrated. No registration or issue-closure blocker remains.

## Checklist Results

Manual source observations below were performed by `codex-independent-reviewer`; null exits are not product-test passes.

| Check | Result | Command / procedure | Exit | Evidence |
|---|---|---|---|---|
| PR-1 Plan/task alignment | pass | Read both complete documents; map all ACs to rows 0–9/H1/H2 | null | Same guard, packaged proof, scope and record sequence. |
| PR-2 Not started | pass | Run scratch inventory and inspect target folder/future paths | 0 | Two plan files; 17 ACs; 27 unchecked rows; future product/test/handoff absent. |
| PR-3 Task contracts | pass | Inspect each row's owner, deliverable, command and status | null | Creation rows precede calls to future checkers; inherited sources exist. |
| PR-4 Validation realism | pass | Trace specified checkers against real smoke fields, source code and probes | null | Required Red/Green/hash/WAV/snapshot predicates observe actual outputs. Two wording notes above cannot false-pass required behavior. |
| PR-5 Source-backed planning | pass | Compare grouping, issue, HDP, rulings and expert-pass adoption | null | Human route/registration preserved; internal design and proof have cited precedents. |
| PR-6 Corrections readiness | pass | Inspect single target, handoff path and round | null | Round 1; correction census not applicable. |
| PR-7 Scope discipline | pass | Compare exclusions with D-1136, preselection ruling and source handover | null | No required product behavior deferred; CUDA hardware claim honestly limited to fake coverage. |
| PR-8 Observable/control chain | pass | Trace load_model → _load_onnx → guarded_model → both ORT constructors and automated oracles | null | Exact hashes, negative fixtures, real ORT and packaged proof cover the named contracts. |
| PR-9 Named contracts | pass | Compare contract definitions, ACs and row references | null | No materially conflicting live behavior found; repeated counts/pins do not alter the governing contracts. |
| Independent splice/ORT/refusal probe | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/tts-fp16-guard-ship/review/reviewer_probe.py` | 0 | Exact guarded bytes; peak 329,180,563; real ORT bytes load; synthetic positive/negative checks pass. |
| Independent Session 73 WAV/reference probe | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/tts-fp16-guard-ship/review/reference_wavs.py` | 0 | 149 unique keys/run; 137/149/149 Done; 137 equal control/guarded WAVs; control failures match Session 52. |
| Inventory and source presence | pass | `rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/tts-fp16-guard-ship/review/inventory.py` | 0 | 16 inherited executable sources and four pin files present; MEU-144 unregistered; preselection pin matches. |
| New product suites, builds and packaged smokes | n/a | Excluded by this read-only plan review | null | Required execution work remains; no fresh packaged-pass claim. |

### Durable evidence

All Python probes used `PYTHONDONTWRITEBYTECODE=1` and `-B`; stdout/stderr were redirected under `C:/Temp/av-kit`, with child exits preserved before receipt reads.

```json
{"schema_version":"evidence.v1","check_id":"ff-plan-r1-splice","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/tts-fp16-guard-ship/review/reviewer_probe.py","cwd":"P:/av-kit","scope":"Scratch reference splice and synthetic model; real ORT CPU bytes load on Session 73 copies; fake-process AST teardown only","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"plan sha256 f7cca9f396c1cf5e1e7386a596fccf4b4e39f64223a29025a94cb23f600dc9ec; task sha256 ae954894bb0401693db3dc7e0c8e6a44584827c3261eaa7f7848391d1c0aa831; source ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a; ORT 1.31.1","output":"Synthetic 375 -> 839 bytes with exact hashes; NaN -> positive zero and finite bytes identical; already guarded, truncated field/varint, long varint and wire 3 refused. Real result 163235204 bytes, SHA256 9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33, byte-equal to Session 73. Peak 329180563 bytes including read. Real ORT bytes load succeeds. Source size/mtime unchanged. Fake stop traces: terminate,wait; terminate,wait,kill,wait. No real process launched or stopped.","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"ff-plan-r1-reference-wavs","command":"rtk proxy P:/av-kit/.venv/Scripts/python.exe -B C:/Temp/av-kit/tts-fp16-guard-ship/review/reference_wavs.py","cwd":"P:/av-kit","scope":"Session 73 scratch runs; SQLite opened only after DB/WAL copies into a new private review directory","phase":"plan-review","exit_code":0,"result":"pass","tested_state":"Saved Session 52/73 smoke JSONs and Session 73 run-control/run-guarded/run-int8 DB and WAV copies; review of reference evidence, not a new packaged smoke","output":"149 keys per run; equal keysets; one row per key; Done control 137, guarded 149, int8 149. All 137 control WAVs byte-identical to guarded. The 12 control failures equal Session 52 by kind/index/voice, all generated audio must be finite. Saved guarded and INT8 smokes both pass.","fresh":true}
```

## Verdict

**approved** — no evidence-backed High or Critical delivery defect was found. The plan would deliver the registered intent. Clarify the adapter fake's patch target and the existing smoke's owned-child teardown wording; neither is a missing deliverable or false-passing gate. Implement the scheduled scripts/tests and obtain their prescribed Red, Green and packaged evidence before execution approval. The coordinator may publish this complete report byte for byte to the canonical review path; this reviewer has made no repository changes.
