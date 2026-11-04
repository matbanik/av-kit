---
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p3-services/implementation-plan.md"
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
---

# Critical Review: p3-services

## Intent Anchor

Session 4 was intended to deliver MEU-13, MEU-10, MEU-11, and MEU-12 as project-integrated application services in `avkit_core/services/`, using only the frozen Phase 1 ports plus `UoWFactory`, with the approved settings, queue, transcript, TTS, and model-download state machines and one real tmp-SQLite G29 write smoke per service. The current tree contains the planned layout and passes its registered gates, but five independently reproduced behavioral/contract failures mean the delivered work does not yet achieve that intent.

## Findings

| Finding | Severity |
|---------|----------|
| **F1 — Non-finite settings values are committed and then crash reads instead of producing `ValidationError`.** Numeric encoding checks Python type and ordinary `<`/`>` comparisons but never calls `math.isfinite` (`packages/core/src/avkit_core/services/settings.py:107`); decoding later sends the stored text to `int(...)` (`packages/core/src/avkit_core/services/settings.py:127`). The real tmp-SQLite probe showed `set("tts", "speed", nan)` returning successfully and persisting `nan`, followed by raw `ValueError`; `requests_per_hour=inf` behaved the same (`C:/Temp/av-kit/p3-svc-exec-r1-settings-nonfinite-sqlite.txt`). This violates AC-13.3's `[0.5, 2.0]` speed/range and invalid-input-to-`ValidationError` contract and creates durable settings rows that can surface as downstream 500s. **Required correction:** reject every non-finite numeric value before persistence and add a defensive decode/error-mapping oracle for already-corrupt rows. | High |
| **F2 — `set_namespace` is not atomic and can partially apply a rejected mapping.** `set_namespace` validates key names, then calls `self.set(...)` once per entry (`packages/core/src/avkit_core/services/settings.py:184`); every `set` opens and commits its own UoW (`packages/core/src/avkit_core/services/settings.py:164`). The probe submitted `{quality: "720p", audio_only: "true"}`: the command raised `ValidationError` for `audio_only`, but `quality=720p` remained committed (`C:/Temp/av-kit/p3-svc-exec-r1-concurrency-atomicity-probes.txt`). This violates AC-13.2/13.3 create-update parity and the approved one-UoW-per-command/atomicity lock (`implementation-plan.md:245`, `implementation-plan.md:454`). **Required correction:** validate the complete mapping first, then persist all rows in one UoW and one commit; add a rollback/no-partial-write test. | High |
| **F3 — Stopping a fully Paused transcript processor is a no-op.** `stop_processing()` only sets `_stop` (`packages/core/src/avkit_core/services/transcript.py:238`). After pause completion, the worker has already returned (`packages/core/src/avkit_core/services/transcript.py:352`) and no thread remains to consume that flag. The production probe reached parent/runtime `Paused`, joined the worker, called stop, and still observed parent/runtime `Paused` instead of parent `Cancelled` and runtime `Idle` (`C:/Temp/av-kit/p3-svc-exec-r1-focused-probes.txt`). This violates AC-11.4 and the explicit `Processing`/**`Paused`** stop contract. **Required correction:** make stop synchronously transition a Paused parent/runtime or start an owned worker that is guaranteed to perform the transition; add the exact pause-complete-then-stop oracle. | High |
| **F4 — `ModelService.download` neither returns immediately nor atomically enforces the one-download runtime.** The method performs the catalog fetch inline (`packages/core/src/avkit_core/services/models.py:85`, `packages/core/src/avkit_core/services/models.py:114`) and its `Idle` check/runtime assignment has no lock. A blocking catalog kept the caller alive until release, contradicting the spec's “spawn one worker; return immediately” contract; a barrier forced two simultaneous callers through the pre-check and both entered the catalog (`max_in_flight=2`, two results, zero `ConflictError`) (`C:/Temp/av-kit/p3-svc-exec-r1-focused-probes.txt`, `C:/Temp/av-kit/p3-svc-exec-r1-concurrency-atomicity-probes.txt`). This violates AC-12.7 and `03-service-layer.md:343-349`. **Required correction:** reserve `Downloading` under a service-owned lock, spawn the one worker, return the current variant immediately, and keep progress/failure transitions owned by that worker. | High |
| **F5 — TTS does not enforce the MVP single-generation invariant, and invalid progress leaves a permanent `Generating` row.** `generate` overwrites `_current_id` without a conflict/lock guard (`packages/core/src/avkit_core/services/tts.py:75`, `packages/core/src/avkit_core/services/tts.py:96`); the concurrency probe entered the fake TTS port twice (`max_in_flight=2`, two successful jobs) (`C:/Temp/av-kit/p3-svc-exec-r1-concurrency-atomicity-probes.txt`). Separately, an out-of-range callback raises `ValidationError` (`packages/core/src/avkit_core/services/tts.py:155`) and the dedicated `except ValidationError: raise` bypasses `_mark(Failed)` (`packages/core/src/avkit_core/services/tts.py:187`); the probe left the persisted row `Generating` with no error (`C:/Temp/av-kit/p3-svc-exec-r1-tts-invalid-progress.txt`). This violates the spec's single-generation rule (`03-service-layer.md:311`), AC-12.5, and the `Generating → Done|Failed|Cancelled` lifecycle. **Required correction:** atomically reject a second generation and terminalize a created job before propagating callback/preparation validation failures. | High |
| **F6 — The one-second download progress throttle is a no-op.** The within-window branch executes `pass` rather than returning (`packages/core/src/avkit_core/services/download.py:117`), then always updates `_last_progress_at`, saves, and commits. Two immediate callbacks produced commit deltas `1, 1` and persisted the second value (`C:/Temp/av-kit/p3-svc-exec-r1-focused-probes.txt`). This violates the explicit approximately-one-second progress/UoW throttle (`03-service-layer.md:68`, `03-service-layer.md:162`) and can turn high-frequency yt-dlp callbacks into continuous SQLite writes. **Required correction:** return on a throttled intermediate callback while preserving the intended terminal/unknown-total exception, then add a controlled-clock commit-count test. | Medium |
| **F7 — `ModelService` performs direct filesystem mutation in core.** `dest_dir.mkdir(...)` is called directly in the service (`packages/core/src/avkit_core/services/models.py:93`), outside a port and outside the named `HealthService` append and transcript `zipfile` exceptions. This violates the plan goal and hexagonal lock that services talk only to frozen ports plus `UoWFactory` (`implementation-plan.md:21`, `implementation-plan.md:195`). The import-anchored scan is clean but cannot detect direct `Path` IO. **Required correction:** leave destination ownership to `ModelCatalogPort.download` (or a future source-backed port change, outside this correction scope); add an AST/direct-IO confinement oracle. | Medium |
| **F8 — Eight AC tests are weak under IR-5 and allow the reproduced failures or named contract branches to stay green.** `test_ac_13_2_set_round_trips_declared_types` never calls `set_namespace` (`tests/unit/test_services.py:294`); AC-13.3 omits non-finite numbers (`:311`); AC-10.6 tests only the Done negative branch (`:661`); AC-10.9 tests only NaN `downloaded` and not throttle/total/speed (`:696`); AC-10.12 does not prove file/archive preservation (`:731`); AC-11.4 covers only stop while a worker is in flight, not stop after pause completion or preservation of a pre-existing Done item (`:1071`); AC-12.5 expects invalid progress to raise but never checks the created row is terminal (`:1540`); AC-12.7 moves the synchronous call into a test-created thread and never asserts immediate return, intermediate `fraction=0.4`, or simultaneous-start exclusion (`:1608`). **Required correction:** add direct negative/positive oracles for each named branch; do not weaken existing assertions. | Medium |

## Scope

**Correlation:** The explicit plan/task slug, four same-project handoffs, and SSOT bind Session 4 to MEU-13, MEU-10, MEU-11, and MEU-12 only. The review expanded across all four handoffs and treated absent REST/MCP/GUI surfaces as required scope exclusions, not missing work. Session 2 UoW and Session 3 adapters were regression-tested but not re-reviewed or rewritten.

**Reviewed artifacts:**

- `docs/execution/plans/2026-08-19-p3-services/implementation-plan.md`
- `docs/execution/plans/2026-08-19-p3-services/task.md`
- `.agent/context/handoffs/2026-08-19-p3-services-MEU-{13,10,11,12}-handoff.md`
- `docs/build-plan/03-service-layer.md`
- `packages/core/src/avkit_core/services/`
- `packages/core/src/avkit_core/domain/{wire,health,download,transcript,tts,errors}.py`
- `packages/core/src/avkit_core/ports/` current interface surface
- `tests/unit/test_services.py` and the AC-10/11/12 domain graph tests in `tests/unit/test_domain.py`
- Session 2-3 SQLite/filesystem/YouTube/transcript/TTS regression tests
- `.agent/context/meu-status.yaml` and the Hub Next field in `docs/BUILD_PLAN.md`

The workspace is not a Git repository. Current numbered source, interface inspection, runtime probes, and exact receipts were used instead of `git diff`. No stored Phase 1 port hash baseline exists, so byte-for-byte historical identity cannot be proven; the current Protocol method set matches the frozen contract, and scoped services use only those methods.

## Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 — Live runtime evidence | Pass, contract-adjusted | The registered seven-file gate ran current domain/services plus real tmp-SQLite/filesystem and mocked external adapters: `171 passed`. The four G29 tests use real tmp-SQLite UoWs. Live YouTube/HF/Kokoro remained forbidden. Receipt: `C:/Temp/av-kit/p3-svc-exec-r1-pytest.txt`. |
| IR-2 — Stub behavioral compliance | Pass | Scoped services are concrete; no `TODO`, `FIXME`, `NotImplementedError`, skip, or xfail neutralization was found. Receipt: `C:/Temp/av-kit/p3-svc-exec-r1-placeholder-skip-scan.txt`. |
| IR-3 — Error mapping completeness | Fail for service boundary; REST N/A | REST routes are correctly absent. F1 shows invalid settings become raw `ValueError` after persistence instead of the required `ValidationError`; F5 leaves a created job nonterminal on callback validation failure. |
| IR-4 — Fix generalization | Pass for round 1 | No prior implementation-review fixes exist. Candidate classes were generalized across settings create/update, stopped/paused transcript states, model simultaneous starts, TTS simultaneous starts, and progress callback lifecycle. |
| IR-5 — Test rigor audit | Fail | Every AC test and the three domain graph tests were graded below. Eight tests are Weak and consolidated in F8; the registered suite green result false-passes F1-F6. Receipt: `C:/Temp/av-kit/p3-svc-exec-r1-ir5-assertions.txt`. |
| IR-6 — Boundary validation coverage | Fail | F1 accepts non-finite numeric settings; F2 violates update atomicity; F4/F5 lack atomic runtime admission. Unknown keys/wires, cookie-shaped values, and ordinary ranges are otherwise covered. |
| IR-7 — Deferral and AC-coverage integrity | Pass | Exact comparison found 10/10 AC-13, 16/16 AC-10, 15/15 AC-11, and 10/10 AC-12 IDs in their matching handoffs. Integration AC-13.9/10.14/11.13/12.9 map to the four G29 tests. MEU-14/15/16/21/25 are scheduled; SSOT bindings, Phase 3 plan membership, and Hub Next pass. Receipts: `C:/Temp/av-kit/p3-svc-exec-r1-ac-handoff-coverage.txt`, `C:/Temp/av-kit/p3-svc-exec-r1-ssot-clean.txt`. |

## IR-5 Test Grades

### MEU-13 — Settings and Health

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_13_1_defaults_fill_when_no_row` | Strong | Exact defaults and namespace fill. |
| `test_ac_13_2_set_round_trips_declared_types` | Weak | Strong leaf round-trips, but never exercises the named `set_namespace` path or atomicity (F2). |
| `test_ac_13_3_unknown_extra_wrong_type_and_range` | Weak | Ordinary invalid cases only; non-finite values false-pass into persistence (F1). |
| `test_ac_13_4_dotted_ui_keys_and_cookie_bytes` | Strong | Both dotted UI keys, cookie needles, length limit, and valid theme. |
| `test_ac_13_5_seq_owner_monotonic_and_restart` | Strong | Exact monotonic and restart-equivalent sequence values. |
| `test_ac_13_6_ring_and_after_seq` | Strong | Exact eviction order and exclusive cursor. |
| `test_ac_13_7_redact_before_enqueue` | Adequate | Ring redaction is exact for Bearer; stdout JSON is not directly asserted. |
| `test_ac_13_8_liveness_dependencies_and_startup_metric` | Strong | Exact dependency values and no settings-row side effect. |
| `test_ac_13_9_g29_real_tmp_uow_settings` | Strong | Real tmp-SQLite service set/get round trip. |
| `test_ac_13_10_log_file_append_exception` | Strong | Append preservation and secret exclusion over two lines. |

### MEU-10 — Download

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_10_1_video_and_playlist_inserts` | Strong | Exact single/playlist counts and titles. |
| `test_ac_10_2_duplicate_video_id_skipped` | Strong | Exact queue-count oracle. |
| `test_ac_10_3_archive_skip_and_clear_keeps_archive` | Strong | Skipped status plus archive survival and queue deletion. |
| `test_ac_10_3_tracking_off_inserts_pending` | Strong | Explicit tracking-off branch. |
| `test_ac_10_4_apply_lock_transitions` | Strong | Block, clear, and terminal-row protection. |
| `test_ac_10_4_p360_stays_pending` | Strong | Explicit compatible-quality branch. |
| `test_ac_10_5_add_time_quality_blocked_insert` | Strong | Exact add-time status. |
| `test_ac_10_6_apply_defaults_skips_done` | Weak | Only the Done negative branch; no Pending/QualityBlocked rewrite or count oracle. |
| `test_ac_10_7_and_10_8_worker_done_and_pause_cancel` | Adequate | Happy worker is specific; the final pause assertion permits either Paused or Idle, but dedicated sibling tests cover pause/cancel. |
| `test_ac_10_7_pause_after_current` | Strong | In-flight synchronization plus exact Done/Pending/runtime result. |
| `test_ac_10_7_cancel_inflight` | Strong | Exact Cancelled and Idle result. |
| `test_ac_10_8_age_restricted` | Adequate | Exact age mapping; generic DomainError/Exception and commit-before-port branches are not asserted. |
| `test_ac_10_9_nan_progress_skipped` | Weak | Only NaN `downloaded`; total/speed non-finites and the one-second throttle are absent (F6). |
| `test_ac_10_10_cookie_error_cause` | Strong | Exact cause identity. |
| `test_ac_10_10_unknown_cookie_mode` | Strong | Explicit fail-closed wire rejection. |
| `test_ac_10_11_extract_cache_and_mutex` | Adequate | Same-URL cache hit; exact 300-second expiry is not asserted. |
| `test_ac_10_11_concurrent_extract_mutex` | Strong | Deterministic overlap and `max_in_flight == 1`. |
| `test_ac_10_12_reorder_remove_get_job` | Weak | Reorder/not-found are specific; file/archive preservation and illegal-edge behavior are not exercised. |
| `test_ac_10_13_archive_skip_before_start` | Strong | Worker recheck ends in Skipped. |
| `test_ac_10_14_g29_real_tmp_uow_download` | Strong | Real tmp-SQLite service add/list round trip. |
| `test_ac_10_15_reset_failed_single_row` | Strong | Selected row, peer row, bulk-call zero, and invalid repeat. |
| `test_ac_10_16_getters_do_not_probe_sabr` | Strong | Required getter values and zero probe calls. |
| `test_ac_10_13_pending_quality_blocked_and_skipped_edges` | Strong | Both new legal edges and a terminal illegal edge. |

### MEU-11 — Transcript

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_11_1_add_channel_and_no_progress_read` | Strong | Slice/count/status/dirs/no-read/duplicate branch. |
| `test_ac_11_2_start_pending_only` | Strong | Paused row excluded, Pending selected, duplicate start rejected. |
| `test_ac_11_3_resume_only_from_paused` | Adequate | Strong rejection oracle; successful Paused resume is covered indirectly elsewhere, not here. |
| `test_ac_11_4_stop_leaves_pending_and_keeps_done` | Weak | Stops only during an in-flight fetch; no fully-Paused stop and no pre-existing Done item (F3). |
| `test_ac_11_5_requeue_and_retry` | Strong | Parent and per-item terminal/reset behavior plus illegal requeue. |
| `test_ac_11_6_skip_retry_and_write` | Adequate | Skip/retry/failure are specific; successful frontmatter/path-before-Done content is not directly asserted. |
| `test_ac_11_7_delay_and_batch_sleeps` | Adequate | Required values occur, but exact counts/order and pause-after-current are not asserted. |
| `test_ac_11_8_failed_parent_skips_zip` | Strong | Exact Failed, no zip path, and no zip artifact. |
| `test_ac_11_9_and_11_10_compile_split_and_zip` | Adequate | Split count, zip existence, raw preservation, and port reads; H1/TOC/H2 and overwrite content are not exact. |
| `test_ac_11_11_recover_stale_processing` | Strong | Processing reset and Paused preservation. |
| `test_ac_11_12_remove_keeps_files` | Adequate | Fake filesystem unchanged and row removed; illegal parent-edge branch is not exercised here. |
| `test_ac_11_13_g29_real_tmp_uow_transcript` | Strong | Real tmp-SQLite service add/list-items round trip. |
| `test_ac_11_14_required_getters_and_compile` | Adequate | Required surface is exercised; compile result is only truthy. |
| `test_ac_11_15_shared_extract_mutex` | Strong | Shared coordinator, deterministic cross-service overlap, exact max 1. |
| `test_ac_11_parent_and_item_transition_graphs` | Strong | Required recovery/retry edges plus illegal controls. |

### MEU-12 — Prepare, TTS, and Models

| Test | Grade | Basis |
|------|-------|-------|
| `test_ac_12_1_prepare_order_and_unknown` | Strong | Fixed-order equivalence, unknown rejection, and disabled-step control. |
| `test_ac_12_2_chunk_and_kokoro` | Adequate | Exact spaCy model/degrade and Kokoro transforms; chunk packing/comma minimum is weakly asserted. |
| `test_ac_12_3_and_12_4_generate_hash_and_mp3` | Adequate | No read, WAV write, exact MP3 options, and one generate; hash is only truthy rather than exact. |
| `test_ac_12_5_progress_resolution_and_cancel` | Weak | 250/1000 and cancel are specific, but invalid progress is allowed to leave a persisted Generating row (F5). |
| `test_ac_12_6_validation_and_illegal_edge` | Adequate | Core invalid arguments and graph rejection; no single-generation admission test. |
| `test_ac_12_7_model_download_runtime` | Weak | Test-created thread masks synchronous service behavior; no intermediate fraction or simultaneous-start exclusion (F4). |
| `test_ac_12_8_list_load_no_torch` | Adequate | Catalog/load delegation is specific; confinement reads only `models.py`, not the complete services surface or direct Path IO (F7). |
| `test_ac_12_9_g29_real_tmp_uow_tts` | Strong | Real tmp-SQLite TTSJob add/get and no text column, matching the approved G29 AC. |
| `test_ac_12_10_get_status` | Strong | Exact existing row and missing-row error. |
| `test_ac_12_tts_transition_graph` | Strong | Required Cancelled edge and illegal Pending-to-Done control. |

## Verified Contract Surfaces

- `DOWNLOAD_TRANSITIONS` has exactly the approved Pending edges; transcript parent/item graphs include `Processing→Pending` and `Failed→Pending`; the TTS graph is unchanged. Receipt: `C:/Temp/av-kit/p3-svc-exec-r1-transition-graphs.txt`.
- `reset_failed(job_id)` uses entity `reset_failed()` plus repository `save`; the bulk fake call remains zero.
- Non-finite download progress fields are checked before conversion; cookie `OSError` mapping and unknown cookie-mode rejection are present. The separate throttle defect is F6.
- `ExtractCoordinator` holds one lock across both YouTube calls, caches for `300.0` seconds, and is injected into download and transcript. The cross-service overlap test reaches max 1.
- Transcript slices `playlist_end` in the service, uses no direct YouTube extract call, never reads `progress.json`, uses `FilesystemPort.read_text` for compile, and avoids compile/zip for Failed parents.
- `SPACY_MODEL="en_core_web_sm"`, `TTS_PROGRESS_RESOLUTION=1000`, last-callback progress preservation, hash/preview-only generation, model runtime `fraction`, and no service `torch`/`ModelFetchJob` strings are present.
- The import-anchored core scan is clean; `SCAN_OPEN` finds only the allowed `health.py` append. Receipts: `C:/Temp/av-kit/p3-svc-exec-r1-import-scan.txt`, `C:/Temp/av-kit/p3-svc-exec-r1-open-scan.txt`, `C:/Temp/av-kit/p3-svc-exec-r1-rule3-services-only.txt`.
- Current frozen Protocols expose the expected Phase 1 method set and services do not call bulk `downloads.reset_failed()` or non-Protocol `has_video_id`. Receipt: `C:/Temp/av-kit/p3-svc-exec-r1-ports-numbered.txt`.

## Commands Executed

Every executable used `rtk proxy`, redirected all process streams to a fresh `C:/Temp/av-kit/p3-svc-exec-r1-*` receipt, and captured `$LASTEXITCODE` before receipt reads.

| Command / probe | Result | Receipt |
|-----------------|--------|---------|
| `uv run pytest tests/unit/test_domain.py tests/unit/test_services.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py` | `171 passed` | `C:/Temp/av-kit/p3-svc-exec-r1-pytest.txt` |
| `uv run pyright packages/core/` | `0 errors, 0 warnings, 0 informations` | `C:/Temp/av-kit/p3-svc-exec-r1-pyright.txt` |
| `uv run ruff check packages/core/` | `All checks passed` | `C:/Temp/av-kit/p3-svc-exec-r1-ruff.txt` |
| Import-anchored `SCAN_CORE_INFRA` supplied for Task 18 | Clean | `C:/Temp/av-kit/p3-svc-exec-r1-import-scan.txt` |
| `SCAN_OPEN` | Only `services/health.py:137` | `C:/Temp/av-kit/p3-svc-exec-r1-open-scan.txt` |
| Placeholder + G36 scan | Clean | `C:/Temp/av-kit/p3-svc-exec-r1-placeholder-skip-scan.txt` |
| Service-only `torch` / `ModelFetchJob` scan | Clean | `C:/Temp/av-kit/p3-svc-exec-r1-rule3-services-only.txt` |
| Download throttle + transcript Paused-stop + model immediate-return probes | F3/F4/F6 reproduced | `C:/Temp/av-kit/p3-svc-exec-r1-focused-probes.txt` |
| Real tmp-SQLite non-finite settings probe | F1 reproduced | `C:/Temp/av-kit/p3-svc-exec-r1-settings-nonfinite-sqlite.txt` |
| Namespace atomicity + simultaneous model/TTS admission probes | F2/F4/F5 reproduced | `C:/Temp/av-kit/p3-svc-exec-r1-concurrency-atomicity-probes.txt` |
| Invalid TTS progress lifecycle probe | ValidationError plus persisted `Generating` row | `C:/Temp/av-kit/p3-svc-exec-r1-tts-invalid-progress.txt` |
| Per-test AST assertion inventory | 55 service AC tests plus 3 domain graph tests inventoried | `C:/Temp/av-kit/p3-svc-exec-r1-ir5-assertions.txt` |
| Exact per-MEU AC/handoff and integration mapping | 10/10, 16/16, 15/15, 10/10; all G29 rows mapped | `C:/Temp/av-kit/p3-svc-exec-r1-ac-handoff-coverage.txt` |
| SSOT/phase/deferred-MEU/Hub Next check | Pass | `C:/Temp/av-kit/p3-svc-exec-r1-ssot-clean.txt` |
| Current port interface read | Expected frozen method set | `C:/Temp/av-kit/p3-svc-exec-r1-ports-numbered.txt` |

## Open Questions / Assumptions

None affect the verdict. Byte-for-byte port immutability is not independently reconstructible because the workspace is not a Git repository and no Phase 1 port hash baseline is stored; current interfaces and service usage match the frozen contract.

## Required Follow-Up

1. Use `/execution-corrections` to add failing regression tests for F1-F7 before changing production code.
2. Keep corrections inside Session 4 scope: do not edit frozen ports, Session 2 UoW, Session 3 adapters, or begin MEU-14+.
3. Strengthen the eight Weak IR-5 tests without neutralizing existing assertions.
4. Re-run the registered H1-2 gates and focused probes, then append round 2 to this same rolling review file.

## Verdict

`changes_required` — Five High behavioral/contract findings survive independent verification: settings can persist invalid or partially applied updates, stop fails from the Paused transcript state, model download blocks and admits concurrent fetches, and TTS admits concurrent generation while leaving callback-validation failures nonterminal. The green registered suite and clean static gates do not override those reproduced failures.

## Residual Risk

Live YouTube, Hugging Face, Kokoro, CUDA, and MPS execution was not run because the approved plan forbids live external access in the default suite. The findings do not depend on those surfaces: each was reproduced with current production services, real tmp-SQLite where persistence mattered, and deterministic port doubles. REST/MCP/GUI absence is required for Session 4 and was not treated as a gap.

## Corrections Applied (2026-08-20)

**Findings resolved by implementer**: 8/8 pending independent re-review. Verdict remains `corrections_applied` — not `approved`.

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| F1 | Non-finite settings persist then crash reads | `_encode` rejects non-finite numbers; `_decode` maps corrupt `nan`/`inf` to `ValidationError` | `test_ac_13_3_nonfinite_rejected_and_corrupt_decode` |
| F2 | `set_namespace` partial write | Validate/encode entire mapping, then one UoW + one commit | `test_ac_13_2_set_namespace_atomic_no_partial_write` |
| F3 | Stop after pause is a no-op | `stop_processing` calls `_apply_stop` when no worker is alive | `test_ac_11_4_stop_after_paused_keeps_done` |
| F4 | Sync download + race | Lock + spawn worker + return current variant immediately; no service `mkdir` | `test_ac_12_7_immediate_return_fraction_and_lock`; existing AC-12.7 joins worker |
| F5 | Concurrent generate + stuck Generating | Admission lock/`ConflictError`; invalid progress `_mark(Failed)` then re-raise | `test_ac_12_6_single_generation_conflict`; `test_ac_12_5_invalid_progress_marks_failed` |
| F6 | Progress throttle `pass` | `return` when inside 1s window; injectable `_clock` | `test_ac_10_9_nonfinite_total_speed_and_throttle` |
| F7 | `dest_dir.mkdir` in core | Removed; catalog owns dest | `test_ac_12_8_no_direct_mkdir_in_services` (excludes named `health.py` log dir) |
| F8 | Weak IR-5 oracles | Added the tests above without loosening existing asserts | plus apply-defaults/archive-remove oracles |

Registered gate after corrections: **181 passed**, pyright 0, ruff clean (`C:/Temp/av-kit/pytest-p3.txt`).

Cross-doc sweep: no port/UoW/adapter edits. No Session 5 files.

## Update (2026-08-20, round 2)

### Intent Anchor

This recheck determines whether the current Session 4 implementation now delivers the approved MEU-13/10/11/12 service contracts after corrections, specifically whether F1-F8 are absent in current code and fresh runtime evidence. Approval requires the registered service/regression gate to remain green and no evidence-backed High/Critical product or contract defect to survive; clerical drift does not block.

### Findings

| Finding | Severity |
|---------|----------|
| No open findings. F1-F8 were independently rechecked against current source and fresh probes; none reproduced. | — |

### F1-F8 Independent Recheck

| Prior finding | Result | Current evidence |
|---------------|--------|------------------|
| **F1 — non-finite settings persisted / corrupt reads leaked `ValueError`** | Fixed | `_encode` rejects non-finite numbers before opening a UoW and `_decode` maps corrupt numeric text to `ValidationError` (`packages/core/src/avkit_core/services/settings.py:102-147`). The fresh probe rejected `speed=nan` and `requests_per_hour=inf`, observed zero commits/rows, and mapped stored `"nan"` to `ValidationError`; the direct oracle is at `tests/unit/test_services.py:1759-1779`. Receipt: `C:/Temp/av-kit/p3-svc-exec-r2-settings-atomicity-probe.txt`. |
| **F2 — `set_namespace` partially committed invalid mappings** | Fixed | The complete mapping is encoded before persistence, then written inside one UoW with one commit (`packages/core/src/avkit_core/services/settings.py:198-221`). The fresh probe preserved prior `quality`, created no `audio_only`, opened zero UoWs for the rejected mapping, and observed exactly one UoW/commit for a valid mapping; companion oracle: `tests/unit/test_services.py:1782-1791`. Receipt: `C:/Temp/av-kit/p3-svc-exec-r2-settings-atomicity-probe.txt`. |
| **F3 — stop after pause completion was a no-op** | Fixed | `stop_processing` synchronously calls `_apply_stop` when no worker is alive (`packages/core/src/avkit_core/services/transcript.py:238-242`); `_apply_stop` transitions Processing/Paused parents to Cancelled and runtime to Idle without touching items (`:546-558`). The exact dead-worker/Paused-parent oracle preserves the pre-existing Done item (`tests/unit/test_services.py:1854-1888`) and passed in the focused run. |
| **F4 — model download blocked and admitted overlapping catalog calls** | Fixed | Admission, `Downloading` reservation, worker creation, and immediate variant return are lock-owned (`packages/core/src/avkit_core/services/models.py:86-108`); worker progress, `mark_downloaded`, and Idle completion are at `:110-159`. The oracle proves return while the catalog is held, one overlapping `ConflictError`, `max_in_flight == 1`, persisted `fraction == 0.4`, and final Idle (`tests/unit/test_services.py:1937-1990`); the existing success oracle confirms `is_downloaded` (`:1634-1652`). |
| **F5 — concurrent TTS generation and nonterminal invalid progress** | Fixed | `_current_id` admission is guarded by a lock and rejects overlap (`packages/core/src/avkit_core/services/tts.py:148-155`); callback `ValidationError` marks the created row Failed before re-raising (`:158-203`). Both the Failed-row oracle (`tests/unit/test_services.py:1891-1908`) and overlap/`max_in_flight == 1` oracle (`:1911-1934`) passed. |
| **F6 — one-second progress throttle did not throttle** | Fixed | Known-total callbacks inside the interval now return before save/commit; total and speed are rejected when non-finite (`packages/core/src/avkit_core/services/download.py:107-144`). The controlled-clock oracle observed one commit for two callbacks inside one second, then a persisted later tick, while non-finite total/speed caused no change (`tests/unit/test_services.py:1806-1832`). |
| **F7 — `ModelService.download` called `Path.mkdir`** | Fixed | `ModelService` delegates the destination to `ModelCatalogPort.download` without creating it (`packages/core/src/avkit_core/services/models.py:86-126`). The service-wide scan found only the named Health log-directory exception at `packages/core/src/avkit_core/services/health.py:135`; the AST oracle covering every other service is `tests/unit/test_services.py:1993-2007`. Receipt: `C:/Temp/av-kit/p3-svc-exec-r2-mkdir-scan.txt`. |
| **F8 — weak oracles allowed F1-F7 to remain green** | Fixed | Strong companion oracles now cover all eight previously weak surfaces (`tests/unit/test_services.py:1759-2007`). All nine focused tests collected and passed; the skip/xfail scan was empty, so no new oracle is neutralized. Receipts: `C:/Temp/av-kit/p3-svc-exec-r2-focused-pytest.txt`, `C:/Temp/av-kit/p3-svc-exec-r2-neutralization-scan.txt`. |

### Checklist Results (IR-1 through IR-7)

| Check | Result | Evidence |
|-------|--------|----------|
| **IR-1 — Live runtime evidence** | Pass, contract-adjusted | Fresh registered seven-file gate: **181 passed**. It includes current domain/services, four real tmp-SQLite G29 service write smokes, filesystem integration, and Session 2/3 adapter regressions. The approved plan forbids live YouTube/HF/Kokoro in the default suite. Receipt: `C:/Temp/av-kit/p3-svc-exec-r2-pytest.txt`. |
| **IR-2 — Stub behavioral compliance** | Pass | Scoped services are concrete and the focused runtime probes exercise save/get, state, progress, and delegation behavior. No `TODO`, `FIXME`, `NotImplementedError`, or placeholder pass remains. Receipt: `C:/Temp/av-kit/p3-svc-exec-r2-placeholder-scan.txt`. |
| **IR-3 — Error mapping completeness** | Pass for service boundary; REST N/A | Session 4 intentionally has no REST routes. Invalid/corrupt settings now surface `ValidationError` (F1), invalid TTS progress raises `ValidationError` after terminalizing the row (F5), and overlap surfaces `ConflictError` (F4/F5). |
| **IR-4 — Fix generalization** | Pass | Finite-number handling was checked across settings/download/model/TTS callbacks; atomic admission was checked for model and TTS; the mkdir scan covered the entire services directory except the named Health exception. Receipts: `C:/Temp/av-kit/p3-svc-exec-r2-f1-f2-scan.txt`, `C:/Temp/av-kit/p3-svc-exec-r2-f3-f8-scan.txt`, `C:/Temp/av-kit/p3-svc-exec-r2-mkdir-scan.txt`. |
| **IR-5 — Test rigor audit** | Pass | The round-1 per-test audit remains in this rolling file. Each formerly Weak surface now has a Strong companion oracle: settings non-finite/atomicity, defaults positive branch, throttle/non-finite progress, remove/archive, pause-complete stop, TTS terminal failure/single admission, and model immediate-return/concurrency/confinement. `test_services.py` is Strong/Adequate with no remaining Weak false-pass for F1-F8; `test_domain.py` transition-graph tests remain Strong. Focused result: **9 passed**; no skip/xfail markers. |
| **IR-6 — Boundary validation coverage** | Pass | Settings create/update paths enforce the same key/type/wire/range rules, reject non-finite values, forbid extras, and validate the full mapping before one atomic write. Runtime command boundaries atomically reject second model/TTS work and fail closed on invalid progress. Evidence: F1-F6 probes and `packages/core/src/avkit_core/services/settings.py:102-221`. |
| **IR-7 — Deferral and AC-coverage integrity** | Pass | Exact comparison found plan/handoff coverage of 10/10 AC-13, 16/16 AC-10, 15/15 AC-11, and 10/10 AC-12. MEU-13/10/11/12 remain `ready_for_review` and bound to this plan; named MEU-14/15/16/21/25 deferrals exist in SSOT. Receipt: `C:/Temp/av-kit/p3-svc-exec-r2-ac-ssot-probe.txt`. |

### Adversarial Verification

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 — Failing-then-passing proof | Pass | Round-1 receipts reproduce F1-F7; the fresh focused receipt executes their correction oracles successfully. |
| AV-2 — No bypass hacks | Pass | Assertions exercise public service behavior or deterministic state; no forced early-return or assertion monkeypatch was found. |
| AV-3 — Changed paths asserted | Pass | F1-F8 table above maps each corrected path to explicit state/value/commit/concurrency assertions. |
| AV-4 — No skip/xfail masking | Pass | Empty exact receipt: `C:/Temp/av-kit/p3-svc-exec-r2-neutralization-scan.txt`. |
| AV-5 — No unresolved placeholders | Pass | Empty exact receipt: `C:/Temp/av-kit/p3-svc-exec-r2-placeholder-scan.txt`. |
| AV-6 — Source-backed criteria | Pass | Corrections enforce existing AC-13.2/13.3, AC-10.9, AC-11.4, AC-12.5/12.7, the model immediate-return spec, and the approved hexagonal lock; no new product behavior was invented. |

### Non-Blocking Clerical Observations

- The four original MEU handoffs retain the pre-correction `171 passed` count, and the MEU-12 Changed Files prose still says model download used `dest mkdir`. Current source and round-2 receipts supersede those historical descriptions. Under the Materiality Gate and this review's strict write scope, this clerical drift is Low and does not block.
- Historical byte-for-byte immutability of frozen ports and Session 2/3 adapters remains unreconstructible because this workspace is not a Git repository and has no stored baseline hashes. Current port-facing usage, domain edges, and the full regression gate are clean; this is residual audit risk, not a reproduced defect.

### Round-2 Receipts

- `C:/Temp/av-kit/p3-svc-exec-r2-focused-pytest.txt` — 9 focused F1-F8 oracles passed.
- `C:/Temp/av-kit/p3-svc-exec-r2-settings-atomicity-probe.txt` — exact F1/F2 persistence, UoW, and commit probes passed.
- `C:/Temp/av-kit/p3-svc-exec-r2-pytest.txt` — registered seven-file gate, 181 passed.
- `C:/Temp/av-kit/p3-svc-exec-r2-pyright-core.txt` — 0 errors/warnings/information.
- `C:/Temp/av-kit/p3-svc-exec-r2-ruff-core.txt` — all checks passed.
- `C:/Temp/av-kit/p3-svc-exec-r2-ac-ssot-probe.txt` — AC coverage, ready-for-review bindings, and scheduled deferrals passed.
- `C:/Temp/av-kit/p3-svc-exec-r2-domain-port-edge-scan.txt` — current domain/port/service edge references.
- `C:/Temp/av-kit/p3-svc-exec-r2-mkdir-scan.txt` — Health log-directory exception is the only service `mkdir`.
- `C:/Temp/av-kit/p3-svc-exec-r2-neutralization-scan.txt` — empty skip/xfail scan.
- `C:/Temp/av-kit/p3-svc-exec-r2-placeholder-scan.txt` and `C:/Temp/av-kit/p3-svc-exec-r2-core-import-scan.txt` — empty placeholder and forbidden-import scans.
- `C:/Temp/av-kit/p3-svc-exec-r2-check-selftest.txt` and `C:/Temp/av-kit/p3-svc-exec-r2-check-review.txt` — deterministic review-checker receipts.

### Verdict

`approved` — F1-F8 no longer reproduce. The fresh focused probes, exact atomicity probe, 181-test registered gate, and clean pyright/ruff results show that the delivered Session 4 services now satisfy the reviewed plan contracts. No evidence-backed High or Critical finding remains.

### Residual Risk

Live YouTube, Hugging Face, Kokoro, CUDA, and MPS execution was not run because the approved plan excludes those external surfaces from the default suite. The corrections reviewed here are deterministic core-service behaviors and do not depend on live access. This approval does not authorize Session 5, port mutation, adapter mutation, commit, merge, release, or deploy.
