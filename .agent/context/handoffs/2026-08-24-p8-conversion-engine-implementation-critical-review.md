---
date: 2026-08-24
review_mode: implementation
target_plan: docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md
verdict: approved
findings_count: 0
round: 2
template_version: 2.1
requested_verbosity: standard
agent: gpt-5.6-sol
---

# Critical Review: p8-conversion-engine Implementation

> **Review Mode**: `implementation`
> **Verdict**: `approved` (latest: Round 2; Round 1 history retained below)

## Intent Anchor

Session 13 was supposed to deliver MEU-28 through MEU-30 as a usable conversion engine: isolated domain contracts, durable `conversion_jobs` persistence, correctly detected FFmpeg encoders, cancellable encode/cut/extract operations, and a sequential service whose probe failures and Extract-all fan-out remain per-job. The current state gets the schema and several frozen argv/domain contracts right, but independently reproduced failures in GPU detection, cancellation, batch probe handling, Extract-all destinations, progress, and 10-bit handling mean the delivered engine does not yet achieve that intent.

## Findings

| Finding | Severity | Confidence | File:Line | Recommendation | Status |
|---|---|---|---|---|---|
| **F1 — Real `ffmpeg -encoders` output is parsed from the wrong column, so available GPU and software encoders are reported unavailable.** `_encoder_names()` stores `parts[-1]`, but real lines contain a codec name followed by a description. The live probe found `libx264`, `libx265`, and `hevc_nvenc` in FFmpeg output while the parser returned none of them. `detect_gpu()` consequently skips the required one-frame hardware probes and reports false software capability flags, violating AC-29.5/29.6. | High | High | `packages/infrastructure/src/avkit_infra/media/adapter.py:115-121,356-405`; `tests/unit/test_ffmpeg_conversion.py:358-371,389-407`; `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md:222-223` | Parse the encoder-name column after the capability flags, add realistic description-bearing fixtures, and assert the expected names/capability booleans. Re-run against the installed FFmpeg. | open |
| **F2 — Cooperative cancellation is not polled while FFmpeg stderr is quiet.** `_run_with_progress()` checks `should_stop()` and then blocks in `stderr.readline()`. The composed service + real adapter probe cancelled while `readline()` was blocked and observed no stdin `q`, an inflight `Processing` row, remaining `Pending`, and runtime `Processing`; only releasing stderr allowed `q`, persisted `Cancelled`, and `Idle`. This violates AC-30.6's complete cancel chain. | High | High | `packages/infrastructure/src/avkit_infra/media/adapter.py:192-245`; `packages/core/src/avkit_core/services/conversion.py:204-205,440-451,488-494,549-564`; `tests/unit/test_ffmpeg_conversion.py:588-614`; `tests/unit/test_conversion_service.py:341-365`; `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md:290,314` | Use a non-blocking or timed stderr-consumption design that polls cancellation independently of line arrival. Add a composed adapter/service test that cancels after the process has entered a quiet read and asserts `q`, terminate, persisted `Cancelled`, remaining `Pending`, and `Idle`. | open |
| **F3 — Extract-all can assign the same output path to multiple jobs.** `_resolve_output()` checks only `Path.exists()`, so sibling plans created in one `add_to_queue()` call do not reserve names. Two AAC streams produced two jobs with indexes `[0, 1]` but both targeted `movie_a.m4a`, violating AC-30.13's distinct-output requirement and risking overwrite/collision at processing time. The existing test hides the defect by using AAC and AC3, which naturally yield different extensions. | High | High | `packages/core/src/avkit_core/services/conversion.py:249-250,290-306,321-340`; `tests/unit/test_conversion_service.py:499-537`; `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md:297,317` | Reserve destinations across the whole add batch (or include stream identity in Extract-all naming) and test two or more same-codec audio streams. | open |
| **F4 — A real adapter probe failure aborts the batch instead of producing one Failed job and continuing.** `FFmpegAdapter.probe()` raises `FilesystemError` for non-zero/invalid ffprobe results, while `_jobs_for_path()` catches only `MediaProbeError`, `OSError`, and `ValidationError`. The independent probe raised `FilesystemError` and stopped after storing the first good job. The AC-30.1 test uses a fake that raises `MediaProbeError`, so it false-passes the actual adapter/service composition. | High | High | `packages/infrastructure/src/avkit_infra/media/adapter.py:275-294`; `packages/core/src/avkit_core/services/conversion.py:237-247`; `packages/core/src/avkit_core/domain/errors.py:68-73,92-93`; `tests/unit/test_conversion_service.py:128-132,231-250`; `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md:285` | Make probe failures use the declared `MediaProbeError` contract and/or catch the adapter's actual probe error at the service boundary. Add a composed test with one valid and one invalid media path. | open |
| **F5 — FFmpeg `time=`/`speed=` progress and persisted speed/ETA are not implemented.** `_snapshot_from_line()` parses only `frame=`, synthesizes `frame/(frame+1)` (120 frames became `0.99` without a duration), and always returns `rate=None`, `eta_seconds=None`. The service persists only `snapshot.fraction`, leaving `speed_bps` and `eta_seconds` untouched. This contradicts the source-backed progress contract. | High | High | `packages/infrastructure/src/avkit_infra/media/adapter.py:98-112`; `packages/core/src/avkit_core/services/conversion.py:464-476`; `tests/unit/test_ffmpeg_conversion.py:193,410-440`; `docs/build-plan/08-video-conversion.md:274-275,388` | Parse frame/time/speed with duration-aware progress, populate the snapshot fields, and persist progress/speed/ETA in short UoWs. Add assertions for exact parsed/persisted values. | open |
| **F6 — The locked 10-bit `p010` path is absent.** The approved plan requires `p010` instead of `nv12` when `bit_depth >= 10`, but neither token exists in core/infrastructure, `VideoEncodeOptions` carries no bit-depth/pixel-format input, and service dispatch cannot convey the probed bit depth to `_video_args()`. A 10-bit input therefore cannot select the required format. | High | High | `packages/core/src/avkit_core/domain/conversion.py:177-194`; `packages/core/src/avkit_core/services/conversion.py:478-487`; `packages/infrastructure/src/avkit_infra/media/adapter.py:131-137,419-438`; `implementation-plan.md:127`; `docs/build-plan/08-video-conversion.md:393` | Carry the probed bit depth (or resolved pixel format) into encode options, emit the required `p010` argv for 10-bit input, and add a negative `nv12`/positive `p010` test. | open |
| **F7 — The registered Python type gate is red.** Independent `pyright packages/core packages/infrastructure` reports three `reportArgumentType` errors at `_optional_int()` and `_optional_float()` because unconstrained `object` values are passed directly to `int()`/`float()`. The plan's verification command requires this scope to pass. | Medium | High | `packages/infrastructure/src/avkit_infra/media/adapter.py:72-87`; `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md:387` | Narrow accepted runtime types before conversion (or use a typed conversion helper), then rerun the exact Pyright receipt. | open |
| **F8 — Integration-typed ACs are backed by weak fake/unit oracles that allowed F1-F5 to pass green.** The most consequential examples are description-free encoder fixtures (AC-29.5), immediate-stop fake Popen (AC-29.12), fake `MediaProbeError` (AC-30.1), a self-recording fake cancel hook (AC-30.6), and different-codec Extract-all streams (AC-30.13). Several ACs labeled `integration` are also marked and housed as unit tests without a composed adapter/service boundary. | Medium | High | `tests/unit/test_ffmpeg_conversion.py:342-371,410-453,586-614,638-663`; `tests/unit/test_conversion_service.py:231-250,341-365,397-416,444-463,499-537`; `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md:221-231,285-297` | Add contract/integration tests for the real compositions and strengthen the weak assertions listed in the IR-5 grading below. | open |

No Critical finding was identified. F1-F6 are evidence-backed behavioral or contract failures and independently satisfy the Materiality Gate for `changes_required`.

## Scope

**Target**: `docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md`

**Review Type**: multi-handoff implementation review, Round 1

**Correlation rationale**: the explicit plan slug/date, named `HANDOFFS`, current focus, and SSOT bind exactly MEU-28, MEU-29, and MEU-30 to Session 13. All three matching handoffs were reviewed. MEU-31–33, Session 14/15, and Session 8c were excluded; no REST `/conversions`, MCP `avkit_convert`, or Convert GUI behavior was required.

**Reviewed artifacts**: approved plan/task/named sets and plan-review Round 3; Phase 8 Domain/Infrastructure/Service spec; the three MEU handoffs; all named domain, port, service, persistence, adapter, and test files; MEU-28/29/30 and Phase 8 SSOT state; current files rather than Git history.

## Commands Executed

| Command / probe | Result | Receipt |
|---|---|---|
| Registered H1 `uv run pytest tests/unit tests/integration -x --tb=short -v` | PASS — 254 passed, 1 warning | `C:/Temp/av-kit/p8-engine-exec-r1-pytest-h1.txt` |
| `uv run pyright packages/core packages/infrastructure` | FAIL — 3 errors | `C:/Temp/av-kit/p8-engine-exec-r1-pyright.txt` |
| Scoped Ruff | PASS | `C:/Temp/av-kit/p8-engine-exec-r1-ruff.txt` |
| `assert-openapi-skip.ps1` | PASS — API tree unchanged, 49 entries | `C:/Temp/av-kit/p8-engine-exec-r1-openapi-skip.txt` |
| MEU-28/29/30 Red oracles | PASS — exact counts 14/14/13 | `C:/Temp/av-kit/p8-engine-exec-r1-red-oracles.txt` |
| Handoff AC-set and marker assertions | PASS — all 41 AC IDs present; three handoffs structurally valid | `C:/Temp/av-kit/p8-engine-exec-r1-handoff-acs.txt`; `p8-engine-exec-r1-handoff-markers.txt` |
| SSOT contract + render check | PASS — MEU-28/29/30 `ready_for_review`, exact no-slash MEU plan; Phase 8 contains slash path | `C:/Temp/av-kit/p8-engine-exec-r1-ssot-contract.txt`; `p8-engine-exec-r1-ssot-render-check.txt` |
| Exact persistence/domain-isolation probe | PASS — column order exact; fully populated Cut equality round-trip; no package/adapter `ConversionJob` leakage | `C:/Temp/av-kit/p8-engine-exec-r1-probe-persistence-isolation-pass.txt` |
| Live installed-FFmpeg encoder parser probe | FAIL contract — three present encoders unparsed | `C:/Temp/av-kit/p8-engine-exec-r1-probe-gpu-parser-live.txt` |
| Quiet-stderr cancellation, adapter-only and full service chain | FAIL contract until stderr released | `C:/Temp/av-kit/p8-engine-exec-r1-probe-cancel-poll.txt`; `p8-engine-exec-r1-probe-cancel-full-chain.txt` |
| Same-codec Extract-all probe | FAIL contract — 2 jobs, 1 distinct path | `C:/Temp/av-kit/p8-engine-exec-r1-probe-extract-same-codec.txt` |
| Adapter-style `FilesystemError` probe chain | FAIL contract — batch raises after first job | `C:/Temp/av-kit/p8-engine-exec-r1-probe-probe-error-chain.txt` |
| Progress parser probe | FAIL contract — `rate=None`, `eta_seconds=None`, synthetic `0.99` | `C:/Temp/av-kit/p8-engine-exec-r1-probe-progress-fields.txt` |
| 10-bit token search | FAIL contract — no `p010` or `nv12` implementation match | `C:/Temp/av-kit/p8-engine-exec-r1-probe-10bit-argv-summary.txt` |
| Even-scale and GPU-preference probes | PASS — 721 → `scale=-2:722`; Auto returns; hard Software miss raises `GpuUnavailableError` | `C:/Temp/av-kit/p8-engine-exec-r1-probe-even-scale.txt`; `p8-engine-exec-r1-probe-gpu-preference.txt` |

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | fail | SQLite round-trip and installed-FFmpeg enumeration were run, but encode/cancel/probe/extract integration ACs rely on fakes; the first realistic compositions reproduce F1-F4. |
| IR-2 Stub behavioral compliance | n/a | No implementation stub was accepted as a delivered adapter/service. |
| IR-3 Error mapping completeness | n/a | REST routes are MEU-31 and explicitly outside Session 13. |
| IR-4 Fix generalization | n/a | Round 1; no execution-review correction exists yet. |
| IR-5 Test rigor audit | fail | Multiple weak tests false-pass material runtime defects; per-AC grading follows. |
| IR-6 Boundary validation coverage | pass | Current Python constructor/dataclass boundaries reject invalid enums/ranges/extras; REST/MCP/UI schemas remain correctly deferred to MEU-31–33. |
| IR-7 Deferral and AC coverage integrity | fail | All 41 AC IDs appear in matching handoffs, Red receipts contain all titles, and later-surface deferrals are registered. Lifecycle evidence fails because multiple integration-typed ACs are backed only by fake/unit tests, including AC-30.1, AC-30.6, and AC-30.13. |

### IR-5 Per-AC Test Rigor Grades

| Test file | Grade partition (every scoped test rated) | Evidence |
|---|---|---|
| `tests/unit/test_domain_conversion.py` | 🟢 Strong: AC-28.2–28.8, 28.12. 🟡 Adequate: AC-28.1, 28.9–28.11, 28.13–28.14. 🔴 Weak: none. | Constructor failures and transitions are behaviorally asserted; some enum/catalog/existence checks sample rather than exhaust the full value contract. |
| `tests/unit/test_ffmpeg_conversion.py` | 🟢 Strong: AC-29.1, 29.2, 29.4, 29.8–29.10. 🟡 Adequate: AC-29.3, 29.6, 29.11. 🔴 Weak: AC-29.5, 29.7, 29.12–29.14. | Weak cases omit realistic encoder descriptions, time/speed fields, mid-stream cancel polling, method-specific logger behavior, and full field equality. |
| `tests/unit/test_conversion_service.py` | 🟢 Strong: AC-30.2–30.4, 30.7, 30.10, 30.12. 🟡 Adequate: AC-30.5, 30.8, 30.9. 🔴 Weak: AC-30.1, 30.6, 30.11, 30.13. | Weak cases substitute a different probe exception, self-report adapter `q`, omit the hard Software-miss branch, and use different codec extensions to conceal destination duplication. |

### Adversarial Verification (AV)

| Check | Result | Evidence |
|---|---|---|
| AV-1 Failing-then-passing proof | pass | All three Red oracles independently pass at 14/14/13; the Red task commands omit `-x`. |
| AV-2 No bypass hacks | pass | No scoped skip/xfail/only or placeholder bypass was found. |
| AV-3 Changed paths exercised by assertions | fail | F1-F5 demonstrate changed paths whose decisive runtime behavior is not asserted by the existing tests. |
| AV-4 No skipped/xfail masking | pass | No scoped masking marker was found. |
| AV-5 No unresolved placeholders | pass | No `TODO`, `FIXME`, `NotImplementedError`, or placeholder stub was found in scoped deliverables. |
| AV-6 Source-backed criteria | pass | The reviewed behavior is traceable to Spec, Local Canon, Research-backed plan locks, or the explicit user scope; no unowned deferral was found. |

### Documentation Review (DR)

| Check | Result | Evidence |
|---|---|---|
| DR-1 Claim-to-state match | fail | Handoffs mark AC-29.5/29.7 and AC-30.1/30.6/30.13 complete, but current runtime probes contradict those claims. |
| DR-2 Residual old terms | pass | No STI `jobs`, `wmic`, adapter `ConversionJob`, REST/MCP/GUI scope expansion, or invented MEU was found. |
| DR-3 Downstream references updated | pass | SSOT, Phase 8 plan list, KEEP sets, and `conversion_jobs` eighth-table expectation are consistent. |
| DR-4 Verification robustness | fail | The green suite permits all six High contract omissions. |
| DR-5 Evidence auditability | pass | All independent commands have isolated `p8-engine-exec-r1-*` receipts. |
| DR-6 Cross-reference integrity | fail | The source-backed progress and 10-bit locks are absent from the implementation despite the handoffs' completion posture. |
| DR-7 Evidence freshness | pass | H1, Ruff, Pyright, OpenAPI, Red-oracle, SSOT, schema, and focused probes were rerun against current state. |
| DR-8 Completion vs residual risk | fail | The handoffs claim all ACs complete without disclosing the reproduced runtime gaps. |

## Open Questions / Assumptions

- The workspace was reviewed from current file state because Git metadata is not assumed.
- The installed `C:/ffmpeg/bin/ffmpeg.EXE` was used only for read-only encoder enumeration; all mutation-capable probes used temporary paths under `C:/Temp/av-kit/`.
- REST `/conversions`, MCP `avkit_convert`, Convert GUI, Session 14/15, and Session 8c remain outside this verdict.

## Follow-up Actions

1. Route fixes through `/execution-corrections`; do not patch within this review workflow.
2. Correct F1-F6 and add the composed/realistic tests described in each recommendation.
3. Resolve the Pyright gate and strengthen every 🔴 test surface.
4. Re-run the registered H1 pytest, Pyright, Ruff, OpenAPI skip, Red oracles, handoff/SSOT checks, focused failure probes, and this rolling review.

## Verdict

`changes_required` — persistence, schema, domain isolation, settings, frozen audio `convert()`, argv basics, and several queue contracts pass, but six High behavioral requirements fail under independent reproduction. Green unit/integration totals do not override those runtime contract failures.

## Residual Risk

After these findings are corrected, a real FFmpeg media fixture should still verify encode/cut/extract output integrity and progress cadence. That is residual execution evidence for this engine, not authorization to start MEU-31–33, Session 14/15, or Session 8c.

---

## Corrections Applied (2026-08-24) — after Round 1 F1–F8

Implementer corrections. Verdict remains `corrections_applied` until independent Codex recheck. Not an `approved` verdict.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Encoder names parsed from description last token | `_encoder_names` takes the name column after 6-char flags; identifier-only tokens | `test_ac_29_5_encoder_names_use_name_column_not_description`; AC-29.5/29.6 description-bearing fixtures |
| F2 | Cancel blocked on quiet `stderr.readline` | Reader thread + 50ms `should_stop` poll; write `q`, terminate, close stderr | `test_ac_29_12_cancel_polls_while_stderr_is_quiet` |
| F3 | Extract-all same-codec path collision | Reserved destinations in one `add_to_queue`; Extract-all includes stream index in the stem | `test_ac_30_13_extract_all_same_codec_distinct_paths` |
| F4 | Probe `FilesystemError` aborted the batch | `probe()` raises `MediaProbeError`; service also catches `FilesystemError` | `test_ac_30_1_adapter_filesystem_probe_error_continues` |
| F5 | `time=`/`speed=` unused; synthetic `frame/(frame+1)` | Parse frame/time/speed; duration-aware fraction + ETA; persist `speed_bps`/`eta_seconds` | AC-29.7 time/speed assertions; AC-30.9 persist 1.5 / 8 |
| F6 | Missing 10-bit `p010` vs `nv12` | `VideoEncodeOptions.bit_depth`; `-pix_fmt p010` when `>= 10` else `nv12`; service passes probed depth | `test_ac_29_7_ten_bit_uses_p010_not_nv12`; `test_ac_30_9_encode_options_carry_probed_bit_depth` |
| F7 | Pyright `object` → `int()`/`float()` | Typed `_optional_int` / `_optional_float` | `pyright packages/core packages/infrastructure` 0 errors |
| F8 | Weak oracles for F1–F5 | Description fixtures, quiet-cancel, same-codec extract, adapter probe error, software-miss, progress fields | New tests listed above |

Registered H1 pytest: **261 passed** (`C:/Temp/av-kit/pytest-p8-engine-h1.txt`). Ruff clean. Pyright 0 errors (`C:/Temp/av-kit/pyright-p8-engine-r1-fix.txt`).

---

## Recheck (2026-08-24) — Round 2

### Intent Anchor

This recheck determines whether the Round 1 corrections now deliver the conversion-engine behaviors required by AC-29.5/29.7/29.12 and AC-30.1/30.6/30.9/30.13: accurate encoder detection, quiet-stderr cancellation, collision-free Extract-all fan-out, per-path probe failures, duration-aware progress persistence, and 10-bit pixel-format propagation. Current code, focused tests, independent composed probes, and every registered gate reproduce F1–F6 as fixed; no new High/Critical behavioral defect was found.

### Findings

No Critical or High findings. The approved structured finding set is empty (`findings_count: 0`).

### Prior Finding Recheck

| Finding | Recheck result | Independent evidence |
|---|---|---|
| F1 | ✅ Fixed | `_encoder_names()` selects `parts[1]`, the encoder-name column (`adapter.py:162-176`). The description-bearing AC-29.5 tests pass (`test_ffmpeg_conversion.py:797-817`), and the installed FFmpeg probe independently returned `libx264`, `libx265`, and `hevc_nvenc`. |
| F2 | ✅ Fixed behavior | `_run_with_progress()` consumes stderr on a reader thread while polling cancellation every 50 ms (`adapter.py:248-335`). The quiet-stderr regression and AC-30.6 both pass. An independent composed `ConversionService` + real `FFmpegAdapter` probe observed stdin `q`, terminate, active `Cancelled`, remaining `Pending`, and runtime `Idle`. |
| F3 | ✅ Fixed | Batch destinations are reserved and Extract-all includes stream identity (`conversion.py:169-181,258-270,345-365`). The same-codec test produces two stream indexes and two output paths (`test_conversion_service.py:560-600`). |
| F4 | ✅ Fixed | Non-zero and invalid-JSON ffprobe results raise `MediaProbeError` (`adapter.py:377-396`); the service also contains the actual `FilesystemError` compatibility catch (`conversion.py:247-255`). The direct adapter probe and the good+bad batch test both pass (`test_conversion_service.py:603-628`). |
| F5 | ✅ Fixed | Progress parsing uses `time=`/duration plus `speed=` and computes ETA (`adapter.py:122-159`); the exact 0.4/1.25/5 assertions pass (`test_ffmpeg_conversion.py:436-485`). Short UoWs persist `speed_bps` and `eta_seconds` (`conversion.py:488-503`; service assertions at `test_conversion_service.py:433-434`). |
| F6 | ✅ Fixed | Encode argv selects `p010` for bit depth >=10 and `nv12` otherwise (`adapter.py:185-189`), while service options carry probed bit depth (`conversion.py:505-519`). Both positive/negative argv and service-propagation tests pass (`test_ffmpeg_conversion.py:820-873`; `test_conversion_service.py:667-703`). |
| F7 | ✅ Fixed | Registered `uv run pyright packages/core packages/infrastructure` reports `0 errors, 0 warnings, 0 informations`. |
| F8 | ✅ Material correction tests exist and pass; non-blocking composition note remains | Description-bearing encoder, blocking-read cancellation, same-codec Extract-all, adapter-style probe failure, exact progress, and bit-depth tests all exist and pass. The repository still proves the quiet adapter loop and AC-30.6 service persistence in separate tests rather than one committed composed regression, and invalid-JSON mapping is reviewer-probed rather than directly asserted by a repository test. Independent composed/current-state probes pass, so this is residual test-rigor risk, not a reproduced product failure or a High/Critical blocker under the unchanged Materiality Gate. |

### Commands Executed

| Command / probe | Result | Receipt |
|---|---|---|
| Focused F1–F8 pytest selection (10 named tests) | PASS — 10 passed | `C:/Temp/av-kit/p8-engine-exec-r2-focused-f1-f8.txt` |
| Composed quiet-stderr cancel probe (`ConversionService` + `FFmpegAdapter`) | PASS — `q`; terminated; `Cancelled` + `Pending`; `Idle` | `C:/Temp/av-kit/p8-engine-exec-r2-probe-cancel-full-chain.txt` |
| Adapter non-zero + invalid-JSON probe | PASS — both raise `MediaProbeError` | `C:/Temp/av-kit/p8-engine-exec-r2-probe-media-errors.txt` |
| Installed-FFmpeg encoder parser probe | PASS — `libx264`, `libx265`, `hevc_nvenc` all parsed | `C:/Temp/av-kit/p8-engine-exec-r2-probe-gpu-parser-live.txt` |
| `uv run pytest tests/unit tests/integration -x --tb=short -v` | PASS — 261 passed, 1 warning | `C:/Temp/av-kit/p8-engine-exec-r2-pytest.txt` |
| `uv run pyright packages/core packages/infrastructure` | PASS — 0 errors | `C:/Temp/av-kit/p8-engine-exec-r2-pyright.txt` |
| Registered scoped Ruff command | PASS — all checks passed | `C:/Temp/av-kit/p8-engine-exec-r2-ruff.txt` |
| `pwsh -NoProfile -File .../assert-openapi-skip.ps1` | PASS — API tree unchanged, 49 entries | `C:/Temp/av-kit/p8-engine-exec-r2-openapi-skip.txt` |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live/runtime evidence | pass for recheck scope | Installed FFmpeg enumeration and independent composed cancellation/probe-error paths were executed against current implementation classes. |
| IR-2 Stub behavioral compliance | n/a | No delivered stub is used for the corrected adapter/service behavior. |
| IR-3 Error mapping completeness | n/a | REST remains MEU-31 and outside Session 13. |
| IR-4 Fix generalization | pass | Both the adapter error contract and the service compatibility catch were checked; F1/F2/F3/F5/F6 each have current-state regression coverage plus independent probes where composition mattered. |
| IR-5 Test rigor | pass with residual note | Every scoped test file was re-read. Corrected assertions are value-specific and all pass; the remaining split adapter/service composition limitation is recorded under F8 and Residual Risk. |
| IR-6 Boundary validation | pass | No new external write boundary was introduced by these corrections. |
| IR-7 Deferral / AC coverage | pass for Round 2 | No AC was deferred or dropped; the corrected AC IDs and named tests exist. Sessions 14/15 and 8c remain excluded. |
| AV-2/3/4 No bypass; assertions exercise paths; no masking | pass | No skip/xfail/early-return bypass was found on the corrected tests; exact state/argv/value assertions execute the changed paths. |
| DR-1/4/7 Claim match, verification strength, freshness | pass with residual note | Correction claims match current code and fresh receipts. The committed composed-cancellation gap is disclosed rather than treated as stronger evidence than it is. |

### Open Questions / Assumptions

- `P:/av-kit` has no available Git metadata, so this recheck used direct current-file reads, line-referenced source/test state, and fresh receipts rather than a Git diff.
- MEU-31–33, Session 14/15, Session 8c, REST, MCP, and GUI work remain outside this verdict and were not started.

### Verdict

`approved` — F1–F6 are independently reproduced as fixed, F7 is green, the material F8 regression tests exist and pass, all four registered gates pass, and no new High/Critical behavioral finding exists. Per the unchanged Materiality Gate, the remaining split-composition test-rigor note does not block approval and is not included in the structured findings count.

### Follow-up Actions

None required for this Round 2 approval. A future test-only hardening pass may commit the reviewer-probed full service+adapter quiet-cancel chain and direct invalid-JSON adapter assertion; that is not authorization to start Session 14/15 or Session 8c.

### Residual Risk

The suite still substitutes fake process/media boundaries for full output-integrity conversion. Real media encode/cut/extract output validation and a committed composed quiet-cancel regression remain useful future hardening, but current behavior for every Round 1 High finding was independently reproduced and passed.
