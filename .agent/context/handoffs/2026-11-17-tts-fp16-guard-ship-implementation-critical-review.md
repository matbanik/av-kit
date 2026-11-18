---
date: "2026-11-18"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-11-17-tts-fp16-guard-ship/implementation-plan.md"
verdict: "approved"
findings_count: 0
template_version: "2.2"
requested_verbosity: "standard"
agent: "codex-independent-reviewer"
loop_id: "ff-execution-2026-11-17-tts-fp16-guard-ship"
round: 1
tested_state: "174bafa8a9ff327d38e54bd36f3edcb0e0b62085+8afc8a7a04434687c654454239b91bef722d1ce387854ee7b8fa52ef27bfce73"
---

# Critical Review: 2026-11-17-tts-fp16-guard-ship

> **Review Mode:** execution
> **Verdict:** approved

## Scope

Independent Codex review of the Anthropic-authored Session 74 implementation, MEU-144, against AC-144.1–AC-144.17. Scope is the delta from `baseline.sha` in the plan's Files Modified paths, plus its supporting scripts, baseline data, handoff and receipts. Sessions 91–94 are excluded under D-1140. No repository file was edited; reviewer scripts, fixtures, receipts and this report are under `C:/Temp/av-kit`. The coordinator publishes the report and performs the remaining review-state and H2 steps.

**Intent anchor:** when a user loads ONNX FP16 Kokoro, the app builds its ONNX Runtime session from Session 73's guarded graph, made in memory from the user's own downloaded file and checked against Session 73's source hash (`ba4527a8…`) and result hash (`9037c82b…`), so the packaged `--phase sentences` smoke passes 149 of 149 jobs where today it fails 12; a file with any other size or hash loads exactly as shipped; a splice that refuses or gives another hash loads the file as shipped and logs one warning with no path; no file in the models folder is written, renamed or added; INT8 and FP32 load exactly as before; FP16 stays never preselected (D-330, D-331); nothing is posted to Hugging Face and no new package is added. Scripts and tests prove each part, with no manual check.

**Intent achieved:** yes. No evidence-backed behavioral defect, regression or false implementation claim was established. My `identity.py --state-only` result exactly equals the gate's value above. There is no sandbox-ignore or sibling-plan discrepancy to reconcile.

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|---|---|---|---|---|---|---|

## Q1 — Goal

Accepted every goal clause within the approved scope. All seventeen ACs have substantive tests or scripted proofs and handoff coverage.

| Goal clause | ACs and decisive evidence |
|---|---|
| Build in memory from the pinned download; return Session 73's bytes | AC-144.1–3/7/12: `phase_guard.py:55`, `:150`, `:209`; `ff-guard-check.json` records source `ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a`, result `9037c82b84dca069464f707f31a4fcb6e5d57107b0534fd4a7ae0c044396fd33`, 163235204 result bytes and successful real ORT CPU construction. |
| Packaged FP16 changes from twelve failures to 149/149 | AC-144.13/14: actual smoke JSON and check receipts; control 12 failures, guarded zero; by-job equality 137 control and 149 guarded WAVs. |
| Unknown files load as shipped; refused/wrong result falls back with one path-free warning | AC-144.4–6: unit assertions; independent read/splice error and hash-mismatch probes. |
| No models-folder write | AC-144.8/12/14/15: no writer in product module; synthetic bytes/mtime/name assertions; snapshot equality after rows 3, 6, 7 and 8. |
| INT8 and FP32 unchanged; FP16 never preselected | AC-144.9–11/15/16: identical-path fallback, unchanged FP32 pins, INT8 149/149 and 149 equal WAVs, unchanged catalog and `PRESELECT_ORDER`. |
| No Hugging Face post, download or new package; automated proof | Product delta uses stdlib and existing structlog only; manifests/lockfile are unchanged; smoke uses copies and dead proxies; tests/scripts carry the proofs without a human-check row. |

Not claimed: new guarantees for a different upstream model, CUDA hardware validation, or a fresh reviewer packaged run. The plan expressly uses source/result hashes, a CUDA recording fake and the saved packaged proofs.

## Q2 — Splice

Accepted GUARD_IN_MEMORY, ONE_JOIN and GUARD_BYTES_EQUAL. The reader advances on every field, bounds varints, checks message ends and refuses unsupported wire types. It parses the single graph, identifies the named Div, checks its output and sole Atan consumer, rewrites that input, inserts IsNaN/Where and the FP16 positive-zero initializer, and adjusts the graph length. Unchanged graph/file spans are memoryviews in the final join (`phase_guard.py:184–206`); it does not materialize another whole graph first.

Real-file evidence is exact: `ff-guard-check.json` and `ff-D6-guard-check.json` both record the required result hash and peak **329181494 bytes**, below **400000000**, with the file unchanged. The packaged Green independently supports use of those bytes in the shipped load path.

My small synthetic probe exercised 5378 inputs: all 375 source prefixes, 5000 deterministic random byte strings and three hostile length/varint cases. There were 5377 SpliceError refusals and no hang or other uncaught error. The one accepted prefix ends exactly after a complete graph at byte 369, omitting the later opset field; it remains a complete protobuf shape and is excluded by GUARD_GATE's size/hash. The probe's initial overly broad expectation that every prefix must refuse was corrected in the reviewer-only script after inspecting that field boundary. This is not a product exception or an amended product expectation.

The parser is not a general ONNX validator. Its safety boundary is the approved exact source hash, checked before parsing; attacker-controlled length fields cannot request a length-sized allocation on the application path. No requirement to generalize the splice to arbitrary models was inferred.

## Q3 — Gate and refusals

Accepted GUARD_GATE, GUARD_REFUSE and GUARD_APPLIED (`phase_guard.py:217–246`). With the production call signature, every non-FP16 id returns the original path before stat; stat failure or size mismatch returns before reading; read OSError/MemoryError returns the path; source-hash mismatch never splices or logs. The stable eligible source read is limited by the preceding 163234740-byte size gate, and hashing adds no second source-sized copy. An exception from splice or wrong result hash returns the path with exactly the specified warning. Exceptions contribute only their class name, never their message, filename or path. Applied bytes produce exactly one info event.

Independent probes also verified FP32/INT8/unknown-id no-stat behavior, read OSError/MemoryError, splice RuntimeError/MemoryError and unknown-hash no-splice. Unit tests verify wrong-result refusal and exact event dictionaries.

Red is genuine: `ff-red.txt.exit` is 1, `ff-red.txt` has 25 assertion failures for the missing guard, and `ff-red-check.txt` reports ten required test families and zero problems. This is not an import/setup Red. `ff-red-pins.txt` has 62 passes; all three new test-side hashes still equal their Red pins. Green has 171 passes. No expectation weakening was found.

## Q4 — Adapter

Accepted BOTH_SESSIONS, NO_FILE_WRITE and PRESELECT_KEPT. The whole adapter delta is the import at `adapter.py:38`, one `guarded_model` call at `:401`, and replacements of the two session inputs at `:404` and `:416`. The guard is before the branch; CUDA failure and the CPU retry reuse one bytes object. The three recording-fake tests check call count, object identity, provider routing and reported device. The real synthetic ORT integration test distinguishes guarded positive zero from unguarded NaN through `load_model`; actual real-file and packaged receipts show the pinned graph works in ORT bytes form without external data.

`voices.py`, `tts/__init__.py`, preselection, catalog, packaging specification and existing pin tests have no session delta. Twelve read-never-changed hashes match row 0. Four snapshot compares cover all **153 files / 299058987 bytes**, including names, sizes, hashes and nanosecond mtimes; every equality predicate is true.

No CUDA device run was performed or represented as real hardware evidence. That is the approved test boundary.

## Q5 — Packaged proof

Accepted BUILD_SAME and WAV_BY_JOB. `smoke-check.py:151` copies each `avkit.db*` before opening SQLite, keys rows by `(text_hash, voice)`, requires one row per key and equal key/Done sets, and checks each WAV remains inside its own run. Comparisons hash complete WAV files. I independently checked every hash pair in the three saved by-key JSON objects, without rerunning smokes or reading real user data.

| Proof | Jobs | Done in both runs | Equal WAVs | Result |
|---|---|---|---|---|
| Control versus Session 73 control | 149 | 137 | 137 | pass; same twelve `(kind, index, voice)` failures as Sessions 52 and 73, all non-finite audio |
| Guarded FP16 versus Session 73 guarded | 149 | 149 | 149 | pass; zero failures |
| INT8 versus Session 73 INT8 | 149 | 149 | 149 | pass; zero failures |

The smoke JSONs name the expected variants, empty errors/forbidden directories and the dead HTTPS proxy. Both build receipts end in Build complete; copy checks pass. The S9 receipts show no existing target folders before creation; all three run folders and models-copy remain present now. Product/model files were not rewritten. Rebuilding the shared ignored packaging output is disclosed and authorized by the plan.

S13 is supported by the row commands' run-specific post-smoke process checks, successful row evidence and `Backend.stop()` at `tools/smoke_packaged_tts.py:162–169`, called in `finally` at `:730`. It terminates only the Popen child it owns, with a kill fallback after its bounded wait. No name-wide stop appears in these rows. I started/stopped no app or backend. The corrected wording in the handoff is accepted.

## Q6 — Gate, registers and records

Accepted the passing gate and record changes. `ff-gate-h1.txt` has all **22** required run steps at exit 0, and matching before/after identity. The individual receipts contain actual results: 13 Python files formatted; lint passes; pyright zero errors/warnings; 21 unit passes; 66 integration/pin passes; successful real guard check; **3112 Python passes**, versus row 0's **3087**, matching **25 new tests**; two canon Vitest files / fourteen tests pass. No baseline test failure was excused. All 594 skip hashes still match, supporting the scoped UI/MCP/OpenAPI skips.

D-1140 is sound: only foreign untracked planning artifacts are excluded; delivered code, tests, registers and relevant tool inputs remain bound. D-1141 records pre-existing pin-file format drift while keeping edited files' formatting and all five files' lint fatal; the original failure is retained. The read-only pin remains byte-identical and no product check was weakened. The clean baseline rerun and final suite are accepted.

The registration script uses `tools.meu_status.model` load/save validation and `band: P2`; its receipt shows pending, phase 3, matrix 3.21, dependency MEU-127. The status-tool receipt shows ready_for_review. The actual diffs contain the 03 section/Delivered note, matrix row 3.21, register entry and generated outputs. The issue is resolved with all five MEU links; I compared the actual parsed resolution_path against HEAD and found it identical. Only grouping line **162**, row 74, differs. Both render checks pass independently now.

H2, canonical publication and the coordinator's authorized commit follow review; their pending state is not a delivered-product finding.

## Q7 — Safety and fidelity

Accepted the scoped delta and evidence fidelity. Independent eol-check reports **18 scope paths, zero problems**, including current-focus and the handoff. CRLF is preserved for all named product/test/03/matrix/focus paths; registers, grouping and handoff remain LF. HEAD still equals baseline and the index is empty. Scope receipts show no outside-scope delta, and the current matching tested state corroborates them. There is no evidence of a session commit, stash or revert; historical absence of a transient action cannot be proved solely by the present tree.

The independent scan of 35 own changed/new paths found no introduced home prefix or personal email; inherited out-of-scope legacy occurrences were not represented as new defects. Secret paths and sibling plans were excluded before reads. No reviewer network request, install, sync, build, heavy suite, backend, Electron process or real-user-model/app-data read occurred. The initial uv invocation was refused access to its default cache before checks ran; I relocated UV_CACHE_DIR into the permitted review temp folder, set UV_OFFLINE=1 and reran successfully. All reviewer Python commands use PYTHONDONTWRITEBYTECODE=1 and temp directories under the assigned review folder.

Handoff counts, hashes and claimed outcomes agree with the actual receipts and current input identity. Disclosed status-line/decision-log edits, no-sync runs, extracted row scripts, guard-check selftest, grouping byte edit, repeated post-focus render, handoff rebuild and optional peer omission do not undermine the delivered proof. No paperwork findings were raised.

## Checklist Results

### Independent commands

Commands below run from `P:/av-kit` with the safe environment described above. Receipts remain in `C:/Temp/av-kit/tts-fp16-guard-ship/exec-review/`.

| Check | Result | Command | Exit | Decisive output |
|---|---|---|---|---|
| Current input identity | pass | `uv run --no-sync python -B docs/execution/plans/2026-11-17-tts-fp16-guard-ship/identity.py --state-only` | 0 | exact equality with gate state |
| Synthetic unit behavior | pass | `uv run --no-sync python -B -m pytest -p no:cacheprovider tests/unit/test_tts_phase_guard.py -q` | 0 | 21 passed in 1.07s |
| Guard checker negative cases | pass | `uv run --no-sync python -B docs/execution/plans/2026-11-17-tts-fp16-guard-ship/guard-check.py --selftest` | 0 | 4 cases, 0 wrong |
| Packaged checker fixtures | pass | `uv run --no-sync python -B docs/execution/plans/2026-11-17-tts-fp16-guard-ship/smoke-check.py --selftest` | 0 | 33 cases, 0 wrong |
| Red parser fixtures | pass | `uv run --no-sync python -B docs/execution/plans/2026-11-17-tts-fp16-guard-ship/red-check.py --selftest` | 0 | 86 fixtures, 0 wrong |
| Line endings | pass | `uv run --no-sync python -B docs/execution/plans/2026-11-17-tts-fp16-guard-ship/eol-check.py` | 0 | 18 scope paths, 0 problems |
| Issue render | pass | `uv run --no-sync python -B tools/issue_triage.py render --check` | 0 | known-issues.md is up-to-date |
| MEU render | pass | `uv run --no-sync python -B tools/meu_status.py render --check` | 0 | 159 MEUs, 12 phases, no drift |
| Adversarial parser/fallback | pass | `uv run --no-sync python -B C:/Temp/av-kit/tts-fp16-guard-ship/exec-review/probe.py` | 0 | 5378 inputs; refusals/gates pass; 0.011s |
| Pin, proof and record audit | pass | `uv run --no-sync python -B C:/Temp/av-kit/tts-fp16-guard-ship/exec-review/audit.py` | 0 | all saved by-job hash pairs equal; skip/pin/Red/build hashes unchanged; records/safety pass |

```json
{"schema_version":"evidence.v1","check_id":"ff-review-independent-checks","command":"rtk proxy pwsh -NoProfile -File C:/Temp/av-kit/ff-review-safe-checks.ps1","cwd":"P:/av-kit","scope":"identity, synthetic unit behavior, plan checker selftests, line endings and read-only renders","phase":"targeted","exit_code":0,"result":"pass","tested_state":"174bafa8a9ff327d38e54bd36f3edcb0e0b62085+8afc8a7a04434687c654454239b91bef722d1ce387854ee7b8fa52ef27bfce73","output":"All eight child commands exited 0. Identity exactly matches gate; 21 unit tests passed; guard checker 4 cases, smoke checker 33 cases, Red checker 86 fixtures all correct; 18 line-ending paths have no problems; issue and MEU renders have no drift."}
```

### Review observations

| Check | Result | Observation |
|---|---|---|
| IR-1 runtime evidence | pass | Real ORT synthetic integration plus real-file ORT construction and packaged proofs; saved matching-state receipts inspected, heavy processes not rerun. |
| IR-2/3/6 unrelated write boundaries | n/a | No new API/MCP/persistence write boundary or behavioral stub is delivered. |
| IR-4/5 rigor and negative paths | pass | Every test in both new files audited: Strong. Exact bytes/hashes, float16 signs/bits, refusal messages, event dictionaries, no writes, same-object fallback and real ORT outputs are asserted; the synthetic helper pins its graph independently. |
| IR-7 AC completeness | pass | AC-144.1–17 all implemented and covered; integration ACs have integration tests; no disguised deferral. |
| DR-1/4/5/7/8 substantive claims/evidence | pass | Actual file delta, individual receipts, full-gate counts, identity, immutable test hashes and saved by-job pairs agree. |
| AV-1–6 | pass | Intended Red then Green; no bypass/skip masking/placeholders; changed paths have behavioral assertions; criteria trace to approved plan/canon/rulings. |

These are manual reviewer observations by codex-independent-reviewer of the files, diffs and receipts cited above; they are not additional product-suite executions.

## Verdict

**approved** — intent achieved, zero findings. The work implements the pinned, in-memory guard and the packaged proofs establish the specified user outcome. Residual limits remain the approved pinned-file boundary, CPU-only real runtime proof and saved packaged evidence; CUDA branching is verified by the recording fake. No correction is required before the coordinator proceeds with publication, ledger validation and H2. This report does not authorize a push.
