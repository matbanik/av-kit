---
date: "2026-08-19"
review_mode: implementation
target_plan: "docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md"
verdict: approved
findings_count: 0
template_version: "2.1"
requested_verbosity: "standard"
agent: gpt-5.6-sol
round: 2
---

# Critical Review: p2-persistence-io

## Intent Anchor

Session 2 was intended to deliver only MEU-5 and MEU-8: a file-backed SQLite WAL persistence layer implementing the frozen Phase 1 storage ports, plus bounded filesystem and subprocess FFmpeg adapters. The delivery is substantially present and its registered gate is green, but two independently reproduced contract failures mean it does not yet achieve the full approved intent.

## Findings

| # | Finding | Severity | File:Line | Recommendation | Status |
|---|---------|----------|-----------|----------------|--------|
| 1 | **AC-8.4 accepts non-finite float PCM and writes corrupted audio.** The contract admits only float samples in `[-1, 1]`. The implementation checks only `< -1` / `> 1`; `NaN` makes both comparisons false, is cast to int16 with a runtime warning, and a WAV is written. Independent probe `C:/Temp/av-kit/p2-exec-r1-probe-wav-nan.txt` failed with `FAIL: NaN accepted; wav_exists=True size=46`. The existing AC-8.4 test covers shape and finite endpoints but lets this defect pass. | High | `docs/execution/plans/2026-08-19-p2-persistence-io/implementation-plan.md:252`; `packages/infrastructure/src/avkit_infra/filesystem/writer.py:73`; `tests/integration/test_filesystem_media.py:93` | Reject non-finite floating samples before scaling and add an immutable regression assertion for `NaN` (and the same non-finite class) raising `ValidationError`. | open |
| 2 | **The normal missing-binary path does not wrap `FileNotFoundError`.** Round-1 Focus 7 requires missing FFmpeg to raise `FFmpegNotFoundError` with a `FileNotFoundError` cause. `_require_ffmpeg()` raises the domain error directly when probe resolution returns `None`; only `_run()` chains a caught `FileNotFoundError`. Independent probe `C:/Temp/av-kit/p2-exec-r1-probe-ffmpeg-cause.txt` observed `exception=FFmpegNotFoundError` and `cause=None`. The AC-8.7 test asserts only the outer type and therefore false-passes this contract. | High | `packages/infrastructure/src/avkit_infra/media/adapter.py:46`; `packages/infrastructure/src/avkit_infra/media/adapter.py:64`; `tests/integration/test_filesystem_media.py:239` | Preserve the domain error surface while chaining a `FileNotFoundError` on the resolution-miss path; assert `isinstance(exc.value.__cause__, FileNotFoundError)` for both `convert` and `probe`. | open |
| 3 | **IR-5 found two additional false-passable predicates.** AC-5.2's version check accepts any spec containing character `2` after `>=` rather than proving a SQLAlchemy minimum major of 2; AC-8.6 never exercises bundle fallback or bundle-over-PATH priority despite claiming the full three-step order. Current product code is correct on both inspected surfaces, so this is test rigor rather than a reproduced product defect. | Medium | `tests/integration/test_sqlite_uow.py:83`; `tests/integration/test_filesystem_media.py:200` | Parse the dependency requirement semantically and add bundle-present/PATH-present probe-order cases. | open |

## Scope

**Review Type**: project-integrated implementation review, round 1  
**Correlation**: both handoffs use the `2026-08-19-p2-persistence-io` plan source and the plan declares the two-file handoff set.  
**Checklist Applied**: IR-1 through IR-7, reviewer AV-1 through AV-6, and the round-specific adversarial focus.

Reviewed:

- `docs/execution/plans/2026-08-19-p2-persistence-io/{implementation-plan.md,task.md}`
- `.agent/context/handoffs/2026-08-19-p2-persistence-io-MEU-{5,8}-handoff.md`
- `docs/build-plan/02-infrastructure.md` Database, ORM/UoW, Media, and Filesystem sections only
- `packages/core/src/avkit_core/ports/{storage,filesystem,media}.py`
- all current source under `packages/infrastructure/src/avkit_infra/`
- `tests/integration/test_sqlite_uow.py` and `tests/integration/test_filesystem_media.py`
- `.agent/context/meu-status.yaml` entries MEU-5 and MEU-8

The workspace is not a git repository, so verification used current file state, executable behavior, exact source reads, and literal frozen-signature comparison rather than `git diff`. The required absence of `youtube/`, `transcript/`, `tts/`, and `model_manager/` was confirmed; Session 3 was not treated as missing Session 2 work.

## Commands Executed

| Command / probe | Result | Round-1 receipt |
|-----------------|--------|-----------------|
| `uv run pytest tests/unit/test_domain.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py` | 74 passed | `C:/Temp/av-kit/p2-exec-r1-pytest-gate.txt` |
| `uv run pyright packages/infrastructure/ packages/core/` | 0 errors, 0 warnings | `C:/Temp/av-kit/p2-exec-r1-pyright-gate.txt` |
| `uv run ruff check packages/infrastructure/ packages/core/` | All checks passed | `C:/Temp/av-kit/p2-exec-r1-ruff-gate.txt` |
| AC/handoff/integration coverage parser | 30 plan ACs; 16 integration ACs; no missing handoff rows or integration tests | `C:/Temp/av-kit/p2-exec-r1-ac-coverage.txt` |
| MEU SSOT parser | MEU-5 and MEU-8 both `ready_for_review`, both bound to the target plan | `C:/Temp/av-kit/p2-exec-r1-ssot-probe.txt` |
| Missing-FFmpeg cause probe | Failed: `cause=None` | `C:/Temp/av-kit/p2-exec-r1-probe-ffmpeg-cause.txt` |
| Non-finite WAV probe | Failed: `NaN` accepted and WAV written | `C:/Temp/av-kit/p2-exec-r1-probe-wav-nan.txt` |
| Deferred-directory check | Pass: all four deferred adapter directories absent | `C:/Temp/av-kit/p2-exec-r1-deferred-dirs.txt` |
| Media forbidden-symbol scan | Pass: no UoW, `ConversionJob`, or `get_version` in product adapter | `C:/Temp/av-kit/p2-exec-r1-media-forbidden-code-scan.txt` |
| Filesystem forbidden-symbol scan | Pass: no `soundfile` or progress reader | `C:/Temp/av-kit/p2-exec-r1-filesystem-forbidden-scan.txt` |
| UoW stale-oracle scan | Pass: no `Session.is_active is False` assertion | `C:/Temp/av-kit/p2-exec-r1-uow-stale-oracle-scan.txt` |
| Skip/xfail and placeholder scans | Pass | `C:/Temp/av-kit/p2-exec-r1-skip-scan.txt`; `C:/Temp/av-kit/p2-exec-r1-placeholder-scan.txt` |

No `census-*`, p1, or other leftover receipt was used as global proof.

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | pass | Real file-backed SQLite and filesystem integration tests ran; FFmpeg subprocess is mocked as required by the spec. |
| IR-2 Stub behavioral compliance | pass | Repositories perform real save/get/filter/cascade behavior; no placeholder implementation was found. |
| IR-3 Error mapping completeness | not applicable | Session 2 has no REST/API write routes. |
| IR-4 Fix generalization | not applicable | First review round; no prior correction surface. |
| IR-5 Test rigor audit | fail | Every test is graded below. Weak tests are tied to Findings 1-3. |
| IR-6 Boundary validation coverage | fail | AC-8.4's numeric boundary admits `NaN` and writes output. |
| IR-7 Deferral and AC integrity | pass | All 30 AC IDs appear in the two handoff AC tables; every one of the 16 integration-typed ACs is backed by a test in an integration file. Deferred adapters are scheduled Session 3 work and correctly absent here. |

### IR-5 Test Grades — `test_sqlite_uow.py`

| Test | Grade | Rationale |
|------|-------|-----------|
| `test_ac_5_1_workspace_layout_and_no_deferred_adapters` | Strong | Exact workspace list, import, required files, and forbidden directories. |
| `test_ac_5_2_infra_dependencies_and_tool_paths` | Weak | Meaningful path/dependency checks, but the SQLAlchemy minimum-version predicate can false-pass an invalid requirement. |
| `test_ac_5_3_file_engine_applies_pragma_locks` | Strong | Real file DB; exact WAL, timeout, FK, and thread argument assertions. |
| `test_ac_5_4_init_schema_creates_exactly_seven_tables` | Strong | Exact table-set and forbidden-column assertions against live metadata. |
| `test_ac_5_5_catalog_seed_is_idempotent` | Strong | Second initialization plus exact IDs, metadata, sizes, paths, and flags. |
| `test_ac_5_6_migrations_empty_apply_is_noop` | Strong | Exact empty list, repeated apply, and no-Alembic assertion. |
| `test_ac_5_15_resolve_app_data_env_and_defaults` | Strong | Override, Windows default, POSIX default, and filename are specific. |
| `test_ac_5_7_mapper_enums_paths_and_preview_truncation` | Strong | Real round trip, non-ORM return, enum/path values, and over-limit map-in truncation. |
| `test_ac_5_8_download_repo_order_delete_all_and_reset_failed` | Strong | Exercises ordering, reorder, reset semantics, Done negative path, archive survival, delete, and duplicate lookup. |
| `test_ac_5_9_archive_unique_is_idempotent` | Adequate | Proves one-row idempotency and missing lookup; does not assert first-write preservation. |
| `test_ac_5_10_transcript_aggregate_cascade_and_counts` | Adequate | Strong cascade/count/order/save coverage, but no second `replace_items` call or duplicate-key negative case. |
| `test_ac_5_11_tts_repo_has_no_full_text_column` | Strong | Live schema census plus add/save/get/delete round trip. |
| `test_ac_5_12_settings_missing_none_and_namespace_replace` | Strong | Missing, replacement isolation, value, and namespace ordering are asserted. |
| `test_ac_5_13_model_mark_downloaded_and_list_downloaded` | Strong | Exact catalog, existing/missing path behavior, size update, filtering, and forbidden columns. |
| `test_ac_5_14_uow_commits_on_clean_exit_rolls_back_on_error` | Strong | No in-block commit, fresh-UoW persistence/rollback, shared session, and `in_transaction() is False`; no stale `is_active` oracle. |
| `test_ac_5_16_core_has_no_infra_imports` | Strong | AST scan across every core Python file. |
| `test_ac_5_17_finite_progress_round_trips_nan_rejected` | Strong | Finite DB round trip plus constructor and mapper rejection of NaN. |
| `test_ac_5_18_storage_protocol_signatures_and_concrete_extras` | Strong | Exact parameter/annotation/return snapshots for all frozen storage methods and concrete-only extras. |

### IR-5 Test Grades — `test_filesystem_media.py`

| Test | Grade | Rationale |
|------|-------|-----------|
| `test_ac_8_1_write_text_atomic_uses_replace` | Strong | Same-directory temp, real replace, final content, failure mapping, and old-content preservation. |
| `test_ac_8_2_progress_export_has_no_reader` | Strong | Exact JSON body and explicit absence of progress-load APIs. |
| `test_ac_8_3_ensure_channel_dirs_creates_raw_and_compiled` | Strong | Both required directories are asserted. |
| `test_ac_8_4_write_audio_wav_stdlib_wave` | Weak | Exact finite int16/float output and shape rejection, but it lets non-finite float PCM through (Finding 1). |
| `test_ac_8_5_read_text_compile_only_and_bounded` | Strong | Resolve/traversal, parents, suffix, size, TTS-like path, values, and keyword-only signature. |
| `test_ac_8_6_is_available_probe_order_and_cache` | Weak | Configured-first and negative caching are covered; bundle fallback and bundle-over-PATH are not exercised. |
| `test_ac_8_7_missing_binary_raises_ffmpeg_not_found` | Weak | Outer type is asserted, but required `FileNotFoundError` chaining is not; the final try/except also has no `else` failure. |
| `test_ac_8_8_ffmpeg_version_parses_first_line` | Strong | Exact first line, argv method, missing result, and no parallel helper. |
| `test_ac_8_9_convert_argv_maps_convert_options` | Strong | Exact binary, overwrite flag, codec, bitrate, rate, channels, input, and output. |
| `test_ac_8_10_probe_maps_ffprobe_json` | Strong | Exact command shape and all `MediaInfo` fields, including nullable video codec. |
| `test_ac_8_11_no_conversion_job_and_mocked_subprocess` | Adequate | Static absence is exact; mocked-subprocess behavior is demonstrated more strongly by AC-8.8 through AC-8.10. |
| `test_ac_8_12_port_signatures_match_frozen_protocols` | Strong | Exact frozen parameter kinds, annotations, defaults, returns, and method names. |

### Adversarial Verification (AV)

| Check | Result | Evidence |
|-------|--------|----------|
| AV-1 Failing-then-passing proof | pass | Both MEU handoffs contain FAIL_TO_PASS tables; this round independently reproduced the current 74-test green state. Prior receipts were not used as current global proof. |
| AV-2 No bypass hacks | pass | No assertion monkeypatching or forced early return found; adapter dependencies are patched at their real boundary. |
| AV-3 Changed paths exercised by assertions | fail | Findings 1-3 identify contract branches that the green suite does not assert. |
| AV-4 No skipped/xfail masking | pass | Round-specific scan is clean. |
| AV-5 No unresolved placeholders | pass | Round-specific infrastructure scan is clean. |
| AV-6 Source-backed criteria | pass | Plan ACs are labeled; the two blocking expectations are AC-8.4 and the human-supplied round-1 Focus 7 expansion of AC-8.7. |

### Post-Implementation Review (PR)

| Check | Result | Evidence |
|-------|--------|----------|
| Evidence bundle complete | pass | Both target handoffs include AC, FAIL_TO_PASS, commands, quality, and changed-file sections. |
| FAIL_TO_PASS table present | pass | Present in both handoffs; historical receipts were not reused as this round's proof. |
| Commands independently runnable | pass | Registered gate and targeted probes ran from `P:/av-kit`. |
| Anti-placeholder scan clean | pass | `p2-exec-r1-placeholder-scan.txt`. |

## Open Questions / Assumptions

- None requiring a product decision. The missing-error-cause requirement is explicit in the human's round-1 review scope.
- Because no git metadata exists, “frozen ports unmutated” was verified semantically against the literal required method names/signatures and concrete-only extras, not by historical blob comparison.

## Follow-Up Actions

1. Route Findings 1-3 through `/execution-corrections`; do not patch them in this review workflow.
2. Re-run the registered gate and both failing probes with new round-specific receipts.
3. Recheck this same rolling review file. Do not start `p2-external-adapters` while the Session 2 verdict remains blocking.

## Verdict

`changes_required` — Findings 1 and 2 are independently reproduced High contract failures in filesystem/media behavior. The green 74-test gate, correct SQLite/UoW behavior, complete AC mapping, and correct scope lock do not override those failures.

## Residual Risk

SQLite/UoW, schema/seed, repository signatures, filesystem path restrictions, and FFmpeg argv/probe mapping have good current evidence. The residual risk is concentrated in numeric audio validation and missing-binary error provenance, plus the two non-blocking false-passable test predicates in Finding 3.

---

## Corrections Applied (2026-08-19)

**Findings resolved**: 3/3 claimed (independent recheck required)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| 1 | AC-8.4 accepted non-finite float PCM | `write_audio_wav` rejects non-finite floats with `ValidationError` before scaling | `test_ac_8_4_write_audio_wav_stdlib_wave`; red `C:/Temp/av-kit/fail-to-pass-p2-exec-r1-corrections.txt`; green 74 passed |
| 2 | Missing-binary path had `FFmpegNotFoundError.__cause__ is None` | `_require_ffmpeg` now raises `from FileNotFoundError(...)` | `test_ac_8_7_missing_binary_raises_ffmpeg_not_found`; red `C:/Temp/av-kit/fail-to-pass-p2-exec-r1-ffmpeg-cause.txt` |
| 3 | Weak SQLAlchemy version predicate; AC-8.6 skipped bundle-over-PATH | `_sqlalchemy_floor_major` requires `>=` major ≥ 2; AC-8.6 now asserts bundle fallback and PATH last | `test_ac_5_2_infra_dependencies_and_tool_paths`; `test_ac_8_6_is_available_probe_order_and_cache` |

Registered gate after corrections: 74 passed; pyright 0 errors; ruff clean (`C:/Temp/av-kit/pytest-infra.txt`, `pyright-infra.txt`, `ruff-infra.txt`).

### Ready for

Round-2 `/execution-critical-review` on the same rolling file. Implementer did not author `approved`.

---

## Recheck (2026-08-19) — Round 2

**Workflow**: `/execution-critical-review` recheck round 2  
**Agent**: `gpt-5.6-sol`

### Intent Anchor

This recheck determines whether the Session 2 MEU-5/MEU-8 delivery now satisfies the approved SQLite persistence, bounded filesystem, and FFmpeg adapter contracts while preserving the frozen Phase 1 ports. It independently re-verifies Round 1 Findings F1–F3 against current file state and fresh `p2-exec-r2-*` receipts; Session 3 is outside this review.

### Prior Pass Summary

| Finding | Prior Severity | Recheck Result | Fresh Evidence |
|---------|----------------|----------------|----------------|
| F1 / AC-8.4 — non-finite float PCM was accepted and a WAV was written | High | ✅ Fixed | `writer.py:74-75` rejects non-finite values before opening the destination; the regression test covers both `NaN` and `inf` at `test_filesystem_media.py:123-134`; independent probe observed `ValidationError`, `exists=False`, and `size=0` for each value. Receipt: `C:/Temp/av-kit/p2-exec-r2-probe-wav-nonfinite.txt`. |
| F2 / AC-8.7 — missing-binary errors lacked `FileNotFoundError` provenance | High | ✅ Fixed | `_require_ffmpeg` chains the domain error from `FileNotFoundError` at `adapter.py:46-51`; the regression test asserts the cause for both `convert` and `probe` at `test_filesystem_media.py:281-297`; independent PATH-isolated probe observed the required outer error and cause for both operations. Receipt: `C:/Temp/av-kit/p2-exec-r2-probe-ffmpeg-cause.txt`. |
| F3 — SQLAlchemy floor and FFmpeg probe-order tests could false-pass | Medium | ✅ Fixed | `_sqlalchemy_floor_major` parses the `>=` major at `test_sqlite_uow.py:47-51`, and AC-5.2 requires a parsed major `>= 2` at lines 91-95; the independent probe proves `>=1.2` parses as major 1. AC-8.6 exercises bundle-over-PATH and PATH fallback at `test_filesystem_media.py:251-277`. Receipts: `C:/Temp/av-kit/p2-exec-r2-probe-sqlalchemy-floor.txt`, `C:/Temp/av-kit/p2-exec-r2-f3-media-test-lines.txt`. |

### Commands Executed

| Command / probe | Result | Round-2 Receipt |
|-----------------|--------|-----------------|
| Independent non-finite WAV probe (`NaN`, `inf`) | pass — both raised `ValidationError`; no destination existed and size was 0 bytes | `C:/Temp/av-kit/p2-exec-r2-probe-wav-nonfinite.txt` |
| Independent missing-FFmpeg probe with configured, bundle, and PATH candidates absent | pass — `convert` and `probe` raised `FFmpegNotFoundError` with `FileNotFoundError` causes | `C:/Temp/av-kit/p2-exec-r2-probe-ffmpeg-cause.txt` |
| Independent SQLAlchemy floor parser probe | pass — `>=2` parsed as 2 and the old false-pass input `>=1.2` parsed as 1 | `C:/Temp/av-kit/p2-exec-r2-probe-sqlalchemy-floor.txt` |
| `uv run pytest tests/unit/test_domain.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py -x --tb=short -v` | pass — 74 passed | `C:/Temp/av-kit/p2-exec-r2-pytest-gate.txt` |
| `uv run pyright packages/infrastructure/ packages/core/` | pass — 0 errors, 0 warnings | `C:/Temp/av-kit/p2-exec-r2-pyright-gate.txt` |
| `uv run ruff check packages/infrastructure/ packages/core/` | pass — all checks passed | `C:/Temp/av-kit/p2-exec-r2-ruff-gate.txt` |
| Scoped skip/xfail scan | pass — no masking markers | `C:/Temp/av-kit/p2-exec-r2-skip-scan.txt` |
| Scoped placeholder scan | pass — no unresolved placeholders | `C:/Temp/av-kit/p2-exec-r2-placeholder-scan.txt` |
| Frozen-port SHA-256 before/after comparison | pass — `storage.py`, `filesystem.py`, and `media.py` hashes matched exactly; signature contract tests also passed in the gate | `C:/Temp/av-kit/p2-exec-r2-frozen-ports-before-exact.txt`; `C:/Temp/av-kit/p2-exec-r2-frozen-ports-after.txt` |

All runtime and gate commands used `rtk proxy` with all streams redirected to isolated `C:/Temp/av-kit/p2-exec-r2-*` receipts. No Round 1 probe receipt is used as current proof.

### Findings

| # | Finding | Severity | File:Line | Status |
|---|---------|----------|-----------|--------|
| — | No new material finding. F1, F2, and F3 are independently verified fixed, and the fresh registered gate is green. | — | — | closed |

### Checklist Results

| Check | Result | Evidence |
|-------|--------|----------|
| IR-1 Live runtime evidence | pass | Fresh file-backed SQLite/filesystem integration gate passed; the approved FFmpeg boundary remains subprocess-mocked in tests, with an additional independent real resolution-path probe. |
| IR-4 Fix generalization | pass | F1 covers both required non-finite classes; F2 covers both `convert` and `probe`; F3 covers semantic major parsing plus configured, bundle, and PATH resolution branches. |
| IR-5 Test rigor | pass | The three Round 1 weak/false-passable predicates now assert specific failure provenance, zero output, semantic version meaning, and probe order. No new weak predicate was found in the corrected surfaces. |
| IR-6 Boundary validation | pass | Non-finite PCM is rejected before any WAV output is created. |
| IR-7 Deferral and AC integrity | pass | Review remains limited to scheduled MEU-5 and MEU-8; no Session 3 work was introduced or treated as required. |
| AV-2 / AV-4 / AV-5 | pass | No bypass assertions, skip/xfail masking, or unresolved placeholders were found in the scoped files. |
| Frozen ports | pass | The registered signature tests passed, and pre/post review SHA-256 receipts match for `storage.py`, `filesystem.py`, and `media.py`. |

### Findings Disposition

- F1: closed.
- F2: closed.
- F3: closed.
- New High/Critical failure classes: none.

### Verdict

`approved` — The two prior High contract failures and the Medium test-rigor finding are fixed in current file state and independently verified by fresh Round 2 probes. The registered pytest, Pyright, and Ruff gate is green, frozen ports remain unchanged during this review, and no new material failure class was found.

### Residual Risk and Follow-up

Residual risk is limited to the plan-approved mocked-subprocess boundary for FFmpeg; the independent missing-resolution probe exercised the required failure provenance without requiring a live binary. No correction workflow is required. This review authorizes Session 2 H2 closeout only; it does not start or review Session 3.
