---
date: "2026-09-02"
project: "2026-08-28-p10-queue-card-foundations"
meu: "MEU-42"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md"
build_plan_section: "bp10s10.2"
agent: "claude-opus-5"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-28-p10-queue-card-foundations-MEU-41-handoff.md"
---

# Handoff: 2026-08-28-p10-queue-card-foundations-MEU-42-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-42 — `requeue-widening`. Widen the re-queue contract behind the card's Retry
action from "Failed only" to `REQUEUEABLE_DOWNLOAD_STATUSES` (Failed, Cancelled,
QualityBlocked, AgeRestricted) and `REQUEUEABLE_CONVERSION_STATUSES` (Failed, Cancelled),
make a blocker re-queue *revalidate* rather than launder the block, and give every
`QualityBlocked` job a real, persisted explanation that the MEU-44 card can render.

**Build Plan Section**: [10 §Re-queue contract](../../../docs/build-plan/10-queue-card-ui.md#re-queue-contract) (matrix item 10.2)

**Predecessor**: [`2026-08-28-p10-queue-card-foundations-MEU-41-handoff.md`](2026-08-28-p10-queue-card-foundations-MEU-41-handoff.md)

**Deliberately NOT in this MEU** — MEU-42 is a **backend-only** MEU. No `ui/` file, no
component, no page, no `mcp-server/` file is touched. `Skipped` is excluded from the
re-queue set per `USER_LOCKS.retry_scope`. No new route is added: the widening rides the
existing `POST /{queue}/{id}/reset`, so `ROUTE_COUNT_AFTER` is unchanged and
`ACTION_INDEX_AFTER` (the MCP action index) is unchanged. `PAGE_ISOLATION_RULE` still holds
— every `FROZEN_GLOBS` file is byte-identical to the row-1 baseline.

---

## Acceptance Criteria

> All fifteen plan ACs are present. No AC was dropped or deferred.

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-42.1 | unit | **Single-statement re-queueable sets.** `REQUEUEABLE_DOWNLOAD_STATUSES` / `REQUEUEABLE_CONVERSION_STATUSES` are module-level `frozenset`s; the re-queueable ∪ non-re-queueable partition is exhaustive and disjoint over both enums; each `reset_failed` guard names its constant and no service/route redefines it. | Human-approved (`USER_LOCKS.retry_scope`); proposal §4 | `tests/unit/test_domain.py::test_ac_42_1_requeueable_status_sets_are_single_statement` | ✅ |
| AC-42.2 | unit | **Download transitions gain exactly the re-queue edges.** `Pending ∈ DOWNLOAD_TRANSITIONS[s]` for every re-queueable `s`; `Pending ∉ …` for every non-re-queueable `s`. | Spec (canon §Re-queue contract) | `test_domain.py::test_ac_42_2_download_transitions_gain_requeue_edges` | ✅ |
| AC-42.3 | unit | **Conversion transition map stays exhaustive.** `CONVERSION_TRANSITIONS[Cancelled] == frozenset({Pending})`; `set(CONVERSION_TRANSITIONS) == set(ConversionStatus)`; `Done` / `Skipped` remain `frozenset()`. | Spec (canon §Re-queue contract) | `tests/unit/test_domain_conversion.py::test_ac_42_3_conversion_transitions_gain_requeue_edge[AC-42.3]` | ✅ |
| AC-42.4 | unit | **`DownloadJob.reset_failed` accepts the widened set.** From each re-queueable status the result matches `REQUEUE_RESET_FIELDS` (`Pending`, `error_message=None`, `progress=0.0`). | Spec; `domain/download.py:121-128` | `test_domain.py::test_ac_42_4_download_reset_failed_accepts_requeueable_set` | ✅ |
| AC-42.5 | unit | **`DownloadJob.reset_failed` still refuses the rest.** `ConflictError` from every non-re-queueable status, and the message names **every** member of the re-queueable set rather than only "Failed". | `USER_LOCKS.retry_scope` (Skipped excluded) | `test_domain.py::test_ac_42_5_download_reset_failed_refuses_non_requeueable` | ✅ |
| AC-42.6 | unit | **`ConversionJob.reset_failed` mirrors it.** Succeeds from Failed/Cancelled with `REQUEUE_RESET_FIELDS`; `ConflictError` from Pending/Processing/Done/Skipped. | proposal §4; `domain/conversion.py:310` | `test_domain_conversion.py::test_ac_42_6_conversion_reset_failed_widens_to_cancelled[AC-42.6]` | ✅ |
| AC-42.7 | integration | **Services persist the widened re-queue.** `DownloadService.reset_failed` / `ConversionService.reset_failed` on a `Cancelled` job return `Pending` **and** the repository round-trip shows `Pending` after commit; unknown id raises `NotFoundError`. | `services/download.py:303`; `services/conversion.py:230` | `tests/e2e/test_api_downloads.py::test_ac_42_7_services_persist_widened_requeue` | ✅ |
| AC-42.8 | integration | **Both reset routes honor the widened contract.** Per queue: 200 + `status="Pending"` for every re-queueable status, 409 for every non-re-queueable status, 404 for an unknown id, 422 for an extra field (`EmptyIn` `extra="forbid"` unchanged). Both docstrings read `REQUEUE_ROUTE_DOCSTRING`. | `routes/downloads.py:233`; `routes/conversions.py:255`; `ERROR_SURFACE` | `tests/e2e/test_api_conversions.py::test_ac_42_8_both_reset_routes_honor_widened_contract[AC-42.8]` | ✅ |
| AC-42.9 | integration | **Surface counts are flat and OpenAPI is regenerated.** `export_openapi.py --check` exits 0 with the new descriptions; operation count still `ROUTE_COUNT_AFTER` (71); no new `/retry` path; `mcp-server/src` byte-identical to baseline with action count still `ACTION_INDEX_AFTER` (67). | `MCP_CHANGE_BASIS`; Local Canon OpenAPI drift gate | `test_api_downloads.py::test_ac_42_9_surface_counts_are_flat_and_openapi_regenerated` | ✅ |
| AC-42.10 | integration | **Blocker re-queue revalidates instead of laundering.** (a) a `QualityBlocked` re-queue first applies the current downloader defaults, then re-evaluates `_incompatible` against the live SABR snapshot; (b) now-compatible (or SABR not Active) → persists `Pending`; (c) still incompatible under Active SABR → stays `QualityBlocked` and the route answers 409 whose message contains `BLOCKER_REMEDIATION['QualityBlocked']` verbatim; (d) `AgeRestricted` re-queues unconditionally. | Research-backed (reviewer R4-F2); `REQUEUE_BLOCKER_POLICY` | `test_api_downloads.py::test_ac_42_10_blocker_requeue_revalidates` | ✅ |
| AC-42.11 | integration | **Every `QualityBlocked` job carries a real reason.** For **both** producers (`enqueue` under an Active lock, and `apply_lock`) the job read back from the repository *and* the `GET /downloads` payload carry `error_message` == `BLOCKER_REASON_TEMPLATE['QualityBlocked']` verbatim (no interpolated job field, no "SABR"). Neither producer writes it — the repository boundary does. `AgeRestricted` is asserted to already conform and is unchanged. | Research-backed (reviewer R5-F1); `BLOCKER_REASON_RULE` | `test_api_downloads.py::test_ac_42_11_quality_blocked_jobs_carry_a_reason` | ✅ |
| AC-42.12 | integration | **A blocked job's reason survives the rest of its life.** (a) legacy reasonless row + `apply_lock` → backfilled; (b) `apply_defaults_to_pending` on a blocked row → reason preserved and still true; (c) refused Retry → 409 **and** the row is canonicalized on the way out. | Research-backed (reviewer R6-F1); `BLOCKER_REASON_INVARIANT` (1) | `test_api_downloads.py::test_ac_42_12_blocked_reason_survives_later_mutations` | ✅ |
| AC-42.13 | integration | **Un-blocking clears the reason.** After `clear_sabr()` moves a blocked job to `Pending`, both the persisted row and the `GET /downloads` payload carry `error_message is None`. | Research-backed (self-caught); `BLOCKER_REASON_INVARIANT` (2) | `test_api_downloads.py::test_ac_42_13_unblocking_clears_the_reason` | ✅ |
| AC-42.14 | integration | **The reason cannot be forgotten, because no callsite supplies it.** `normalize_blocker_reason` is a pure function in `domain/download.py`; `SqlAlchemyDownloadRepository.add`/`.save` — the only two writers — apply it. Asserted at the repository with **no service involved**, including the narrowness that makes clause (2) safe: a `Failed` job's real traceback is preserved untouched. Exactly 2 call sites in `repositories.py`, zero in the service/route/serializer. | Research-backed (reviewer R7-F1); `BLOCKER_REASON_ENFORCEMENT` | `test_api_downloads.py::test_ac_42_14_repository_boundary_owns_the_invariant` | ✅ |
| AC-42.15 | integration | **An upgraded queue explains itself before the user touches anything.** A raw-SQL `QualityBlocked` row with NULL `error_message` + a fresh engine (so `apply_migrations()` runs) + `GET /downloads` → the reason is there, with **no service call of any kind** in the test. Idempotent on a second run; an already-correct message is untouched; the literal is built from `BLOCKER_REASONS` at import. | Research-backed (reviewer R7-F1); `BLOCKER_REASON_ENFORCEMENT` | `test_api_downloads.py::test_ac_42_15_upgrade_backfills_legacy_blocked_rows` | ✅ |

### Disclosures the reviewer should check first

1. **Two Red-phase test assertions were corrected during Green.** This is a deliberate,
   flagged deviation from the test-immutability rule, disclosed here rather than buried.
   In both cases the *test* was factually wrong about the pre-existing tree and the
   *implementation was not weakened to fit it*:
   - **AC-42.9** asserted `[p for p in spec["paths"] if p.endswith("/retry")] == []`.
     `/api/v1/transcripts/{id}/retry` **pre-dates this MEU** (Phase 5), so the assertion
     could never pass. The AC's actual negative is "*a new* path appears", so it was
     corrected to assert the list equals exactly `["/api/v1/transcripts/{id}/retry"]` —
     strictly *stronger* than `== []` would have been if it were true, because it now also
     pins that no download/conversion `/retry` path was added.
   - **AC-42.15** asserted the backfill statement lived in `MIGRATIONS`. It lives in the
     sibling `DATA_MIGRATIONS` list (see disclosure 2), so the constant name was corrected.
     The assertion's substance — an append-only list applied by `apply_migrations()` at
     engine init, whose literal is built from `BLOCKER_REASONS` — is unchanged.
2. **The backfill is in `DATA_MIGRATIONS`, not `MIGRATIONS` — a deviation from the plan's
   wording, forced by two *existing* tests.** The plan says "one appended idempotent UPDATE
   statement" in `migrations.py`. Appending it to `MIGRATIONS` broke two pre-existing
   assertions that MEU-42 may not touch:
   - `test_ac_5_6_migrations_empty_apply_is_noop` asserts
     `all("IF NOT EXISTS" in statement for statement in MIGRATIONS)` — no `UPDATE` can ever
     satisfy that.
   - `test_ac_35_2_migrations_if_not_exists_both_tables` calls `apply_migrations(engine)` on
     a **bare** engine; the `UPDATE` then raised `OperationalError: no such table:
     download_jobs`.

   Resolution: a sibling append-only `DATA_MIGRATIONS` list in the same module, applied by
   the same `apply_migrations()` in the same transaction, guarded by a `sqlite_master`
   table-existence check. **Neither existing assertion was modified.** Every property
   AC-42.15 actually requires (append-only list, applied at engine init before routes can
   serve, idempotent, literal built from `BLOCKER_REASONS`) is preserved.
3. **`apply_lock` now writes for an already-blocked row.** Previously it matched a
   `QualityBlocked` row and fell through with **no write at all** — which is exactly the
   defect AC-42.12(a) names. It now saves the row (status unchanged), so the boundary
   normalizer backfills a legacy reason. This adds **no reason-writing literal** to the
   service, honouring the plan's "no reason-writing code in producers" rule (reviewer R7-F1).
4. **AC-42.10(c) "nothing is written" vs AC-42.12(c) "canonicalize on refusal."** Reconciled
   by saving the *unmodified* job through the normalizing repository before raising the 409:
   the defaults are **not** applied and the status does **not** change, so nothing the user
   asked for is written; only the blank reason is canonicalized on the way out.
5. **Out-of-plan `tests/` lint cleanup, and a plan-vs-canon scope conflict.** The row-7 gate
   command runs `ruff check packages/ tests/`, but the registered canonical receipt in
   [`.agent/docs/commands.md:20`](../../../.agent/docs/commands.md) is `ruff check packages/`
   only. `tests/` carried **29 pre-existing violations across 8 files**, 7 of which are
   outside this plan's changed-files list. Per AGENTS.md §Communication Policy the conflict
   is flagged rather than silently resolved; the debt was cleared so the gate passes **as
   written**. Every fix was formatting-only (E501 line wrapping, one dead `UP036`
   version-check block, two unused names). **No assertion, expected value, or test semantic
   was changed** — full pytest count is identical before and after (`507 passed`).

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

All fifteen tests were written across `tests/unit/test_domain.py`,
`tests/unit/test_domain_conversion.py`, `tests/e2e/test_api_downloads.py` and
`tests/e2e/test_api_conversions.py` **before** any `packages/` edit, and observed failing.
Red receipt: `C:/Temp/av-kit/fail-to-pass-meu-42-py.txt` → `15 failed, 267 passed`.
Oracle receipt: `C:/Temp/av-kit/red-oracle-meu-42.txt` →
`PASS: RED_ORACLE py MEU-42 AC-42 count=15` (15 distinct mapped ids == `RED_COUNT_42`).

| Test | Red Output (snippet) | Green Output | File:Line |
|------|---------------------|--------------|-----------|
| `test_ac_42_1_requeueable_status_sets_are_single_statement` | `ImportError: cannot import name 'REQUEUEABLE_DOWNLOAD_STATUSES' from 'avkit_core.domain.download'` | passes — both frozensets exhaustive + disjoint; each guard names its constant | `domain/download.py:107`, `domain/conversion.py:298` |
| `test_ac_42_2_download_transitions_gain_requeue_edges` | `KeyError: <DownloadStatus.Cancelled: 'Cancelled'>` | passes — 4 re-queue edges present, 4 absent | `domain/download.py:96-104` |
| `test_ac_42_3_conversion_transitions_gain_requeue_edge[AC-42.3]` | `AssertionError: assert <ConversionStatus.Pending: 'Pending'> in frozenset()` | passes — `Cancelled → {Pending}`; map still exhaustive | `domain/conversion.py:289` |
| `test_ac_42_4_download_reset_failed_accepts_requeueable_set` | `ConflictError: reset_failed is only valid from Failed` | passes — all 4 statuses reset to `Pending`/`None`/`0.0` | `domain/download.py:130-137` |
| `test_ac_42_5_download_reset_failed_refuses_non_requeueable` | `ImportError: cannot import name 'REQUEUEABLE_DOWNLOAD_STATUSES'` | passes — 409 message names all 4 members | `domain/download.py:132-134` |
| `test_ac_42_6_conversion_reset_failed_widens_to_cancelled[AC-42.6]` | `ConflictError: reset_failed is only valid from Failed` | passes | `domain/conversion.py:315-320` |
| `test_ac_42_7_services_persist_widened_requeue` | `assert 409 == 200` | passes — both services round-trip `Pending`; `NotFoundError` on unknown id | `services/download.py:303`, `services/conversion.py:230` |
| `test_ac_42_8_both_reset_routes_honor_widened_contract[AC-42.8]` | `assert 409 == 200` | passes — 200/409/404/422 matrix green on both queues; both docstrings updated | `routes/downloads.py:233`, `routes/conversions.py:255` |
| `test_ac_42_9_surface_counts_are_flat_and_openapi_regenerated` | `AssertionError: assert ['/api/v1/tra...s/{id}/retry'] == []` *(defective Red assertion — see disclosure 1)* | passes — 71 operations, 2 reset ops with the new description, MCP action count 67 | `openapi.committed.json` |
| `test_ac_42_10_blocker_requeue_revalidates` | `ImportError: cannot import name 'BLOCKER_REASONS' from 'avkit_core.domain.download'` | passes — (a)–(d) all green; 409 body carries the remediation string verbatim | `services/download.py` `reset_failed` |
| `test_ac_42_11_quality_blocked_jobs_carry_a_reason` | `AssertionError: assert None == 'YouTube is limiting which formats this video will serve right now, …'` | passes — both producers, repo read + `GET /downloads` | `domain/download.py` `BLOCKER_REASONS` |
| `test_ac_42_12_blocked_reason_survives_later_mutations` | `AssertionError: assert None == 'YouTube is limiting …'` | passes — (a) legacy backfill, (b) Apply Defaults, (c) refused-Retry canonicalization | `services/download.py` `apply_lock` |
| `test_ac_42_13_unblocking_clears_the_reason` | `AssertionError: assert 'YouTube is limiting …' is None` | passes — normalizer clause (2) clears on the `Pending` save | `domain/download.py` `normalize_blocker_reason` |
| `test_ac_42_14_repository_boundary_owns_the_invariant` | `ImportError: cannot import name 'normalize_blocker_reason'` | passes — 2 call sites in `repositories.py`, 0 elsewhere; `Failed` traceback preserved | `repositories.py` `add`/`save` |
| `test_ac_42_15_upgrade_backfills_legacy_blocked_rows` | `assert False` (no data-migration statement existed) | passes — fresh engine backfills; idempotent; no service call in the test | `migrations.py` `DATA_MIGRATIONS` |

Red totals: `15 failed, 267 passed, 1 warning in 7.26s`.
Two Red assertions were corrected in Green — both disclosed above with rationale. No other
test assertion or expected value was modified.

### Commands Executed

Every command ran under the P0 redirect-to-file pattern with receipts under `C:/Temp/av-kit/`.

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `uv run pytest tests/unit tests/e2e/test_api_downloads.py tests/e2e/test_api_conversions.py --tb=short -q` (row 5, Red) | 1 by design | `15 failed, 267 passed` — receipt `C:/Temp/av-kit/fail-to-pass-meu-42-py.txt` |
| `assert-red-oracle.ps1 -Kind py -Meu 42` (row 5) | 0 | `PASS: RED_ORACLE py MEU-42 AC-42 count=15` |
| `uv run pytest tests/unit tests/integration tests/e2e -q` (row 6, Green) | 0 | `507 passed, 1 warning in 26.87s` |
| `uv run pyright packages/` (row 6) | 0 | `0 errors, 0 warnings, 0 informations` |
| `uv run python tools/export_openapi.py -o openapi.committed.json` then `--check` (row 6) | 0 | regenerated with the new reset descriptions; drift check clean |
| `assert-page-isolation.ps1` (row 6) | 0 | `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42` |
| `uv run ruff check packages/ tests/ --fix` then `--output-format concise` (row 7) | 0 | 29 pre-existing `tests/` violations cleared (7 auto-fixed, 22 by hand) → `All checks passed!` — see disclosure 5 |
| `uv run pytest tests/unit tests/integration tests/e2e -q` (row 7, post-lint re-verify) | 0 | `507 passed, 1 warning in 26.87s` — identical to the pre-lint count |
| Row 7 `MEU_SCOPED_GATE_PY` (pytest + pyright + ruff + OpenAPI `--check` + anti-placeholder on `PLACEHOLDER_PATHS_42` + G36 on `G36_TEST_PATHS_PY` + `HANDOFF_SOURCE_READ_42`/handoff existence, ordering and AC-coverage checks) | 0 | `PASS: MEU-42 MEU_SCOPED_GATE_PY` — receipt `C:/Temp/av-kit/handoff-meu-42.txt` |

### Quality Gate Results

```
pytest (unit+integration+e2e):  507 passed, 0 failed
pyright packages/:                0 errors, 0 warnings, 0 informations
ruff check packages/ tests/:      All checks passed
export_openapi.py --check:        exit 0 (no drift)
anti-placeholder:                 0 matches (PLACEHOLDER_PATHS_42, 7 files)
G36 skip/only/xfail scan:         0 matches (tests/unit, tests/integration, tests/e2e)
PAGE_ISOLATION_CHECK:             PASS — frozen=28 carveout=2 scanned=73 e2e=59 preserved=42
```

**Final session-close verification (task.md H1-2, 2026-09-02).** Re-run over the whole tree after all four MEUs landed: pytest 507 passed - pyright 0 errors - ruff clean - tsc 0 errors - vitest 366 passed (43 files) - eslint clean - electron-vite build ok - `export_openapi.py --check` clean - `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42`. Receipt `C:/Temp/av-kit/full-verify.txt`.

**Playwright E2E passes: 59 passed / 0 failed, EXIT=0** (task.md H1-2a), on a bundle rebuilt after the last source change (P9 RULE-1). Receipt `C:/Temp/av-kit/e2e-regression-rerun.txt`. This **retracts** the earlier `[B]` and its "external electron 42.9.3 / playwright-core 1.62.1 incompatibility" claim: the real cause of `electron.exe: bad option: --remote-debugging-port=0` was `ELECTRON_RUN_AS_NODE=1` set in the agent's own shell (inherited from the Cursor extension host) and spread into the launched app by `...process.env` at all 14 `_electron.launch()` sites. Proof: `electron --version` prints `v24.18.1` with the variable set and `v42.9.3` without. Known-issue `E2E-ELECTRON-LAUNCH-FLAG` has been re-filed against that real cause (env leakage through `...process.env`, severity lowered to low). The specs stay written and wired; no wave was added or removed (`E2E_NEW_WAVES_THIS_SESSION` = 0).

### Blocker copy (AC-42.11 / AC-42.10c — verbatim, quality-independent, acronym-free)

| Key | Value |
|-----|-------|
| `BLOCKER_REASONS[QualityBlocked]` | `YouTube is limiting which formats this video will serve right now, so the requested quality or audio format is not available.` |
| `BLOCKER_REASONS[AgeRestricted]` | `video is age-restricted` |
| `BLOCKER_REMEDIATION[QualityBlocked]` | `Settings > Downloader > Quality (choose a lower quality, or a supported audio format for audio-only jobs)` |
| `BLOCKER_REMEDIATION[AgeRestricted]` | `Settings > Cookies & Authentication (sign-in required for this video)` |

Neither template interpolates a job field, so `apply_defaults_to_pending` rewriting a blocked
row's `quality` cannot make the stored sentence go stale (AC-42.12b).

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modified | transitions, `REQUEUEABLE_DOWNLOAD_STATUSES`, `BLOCKER_REASONS`, `BLOCKER_REMEDIATION`, `normalize_blocker_reason`, `reset_failed` | 3 re-queue edges added; the single-statement frozenset; the blocker copy tables; the pure boundary normalizer; widened guard |
| `packages/core/src/avkit_core/domain/conversion.py` | modified | `CONVERSION_TRANSITIONS`, `REQUEUEABLE_CONVERSION_STATUSES`, `reset_failed` | `Cancelled → {Pending}` edge; the frozenset; the same widened guard shape |
| `packages/core/src/avkit_core/services/download.py` | modified | `_with_current_defaults`, `reset_failed`, `apply_lock` | `REQUEUE_BLOCKER_POLICY` branch (AC-42.10); 409-path canonicalization (AC-42.12c); `apply_lock` now writes for an already-blocked row (AC-42.12a). **No reason-writing literal** |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modified | `add`, `save` | the two — and only — write paths apply `normalize_blocker_reason` (AC-42.14) |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | modified | `DATA_MIGRATIONS`, `_data_migration_table`, `apply_migrations` | append-only data-migration list + table-existence guard (AC-42.15) — see disclosure 2 |
| `packages/api/src/avkit_api/routes/downloads.py` | modified | reset docstring | `Reset a Failed job.` → `Re-queue a job from a re-queueable state.` |
| `packages/api/src/avkit_api/routes/conversions.py` | modified | reset docstring | same |
| `openapi.committed.json` | regenerated | 2 operation descriptions | `export_openapi.py -o`; `--check` clean. Operation count unchanged at 71 |
| `tests/unit/test_domain.py` | modified | AC-42.1, 42.2, 42.4, 42.5 appended | plus the `UP036`/`F401` lint fixes of disclosure 5 |
| `tests/unit/test_domain_conversion.py` | modified | AC-42.3, 42.6 appended | — |
| `tests/e2e/test_api_downloads.py` | modified | AC-42.7, 42.9–42.15 appended | — |
| `tests/e2e/test_api_conversions.py` | modified | AC-42.8 appended | — |
| `tests/e2e/real_stack.py` | new | 261 | production `DownloadService`/`ConversionService` over a real temp SQLite file; only `YouTubePort`/`ExtractCoordinator`/`MediaPort` stubbed. `insert_legacy_row` uses SQLAlchemy Core to produce the pre-release on-disk shape the repository would otherwise normalize away |
| `tests/integration/test_youtube_adapter.py`, `tests/unit/test_backend_cli.py`, `tests/unit/test_console_level.py`, `tests/unit/test_services.py` | modified | line wrapping only | disclosure 5 — formatting, no assertion touched |
| `docs/execution/plans/2026-08-28-p10-queue-card-foundations/task.md` | modified | rows 5–7 | closed with evidence |

**The single-statement re-queueable sets (AC-42.1):**

```diff
+REQUEUEABLE_DOWNLOAD_STATUSES: frozenset[DownloadStatus] = frozenset(
+    {
+        DownloadStatus.Failed,
+        DownloadStatus.Cancelled,
+        DownloadStatus.QualityBlocked,
+        DownloadStatus.AgeRestricted,
+    }
+)
```

**The widened guard, in both domains (AC-42.5 / AC-42.6):**

```diff
-        if self.status is not DownloadStatus.Failed:
-            raise ConflictError("reset_failed is only valid from Failed")
+        if self.status not in REQUEUEABLE_DOWNLOAD_STATUSES:
+            allowed = ", ".join(sorted(status.value for status in REQUEUEABLE_DOWNLOAD_STATUSES))
+            raise ConflictError(f"reset_failed is only valid from {allowed}")
```

**The boundary normalizer — the single enforcement point (AC-42.14):**

```diff
+def normalize_blocker_reason(job: DownloadJob) -> DownloadJob:
+    reason = BLOCKER_REASONS.get(job.status)
+    if reason is not None:
+        current = job.error_message
+        if current is None or not current.strip():
+            return replace(job, error_message=reason)
+        return job
+    if job.error_message in _BLOCKER_REASON_VALUES:
+        return replace(job, error_message=None)
+    return job
```

```diff
-        self.session.add(download_job_to_row(job))
+        self.session.add(download_job_to_row(normalize_blocker_reason(job)))
```

```diff
-        apply_download_job(row, job)
+        apply_download_job(row, normalize_blocker_reason(job))
```

**The blocker revalidation branch (AC-42.10):**

```diff
+            if job.status is DownloadStatus.QualityBlocked:
+                candidate = self._with_current_defaults(job)
+                if self._sabr.mode is SABRMode.Active and _incompatible(candidate):
+                    uow.downloads.save(job)   # canonicalize the reason only
+                    uow.commit()
+                    raise ConflictError(
+                        "download is still blocked; change "
+                        + BLOCKER_REMEDIATION[DownloadStatus.QualityBlocked]
+                    )
+                updated = candidate.reset_failed()
+            else:
+                updated = job.reset_failed()
```

**`apply_lock` — the previously write-less fall-through (AC-42.12a):**

```diff
-                if job.status is not DownloadStatus.QualityBlocked:
-                    uow.downloads.save(job.transition(DownloadStatus.QualityBlocked))
+                blocked = (
+                    job
+                    if job.status is DownloadStatus.QualityBlocked
+                    else job.transition(DownloadStatus.QualityBlocked)
+                )
+                uow.downloads.save(DownloadJob(**{**blocked.__dict__, "updated_at": _now()}))
```

**The upgrade backfill (AC-42.15) — append-only, idempotent, literal built at import:**

```diff
+_QUALITY_BLOCKED_REASON_SQL = BLOCKER_REASONS[DownloadStatus.QualityBlocked].replace("'", "''")
+
+DATA_MIGRATIONS: list[str] = [
+    "UPDATE download_jobs SET error_message = '"
+    + _QUALITY_BLOCKED_REASON_SQL
+    + "' WHERE status = 'QualityBlocked'"
+    + " AND (error_message IS NULL OR TRIM(error_message) = '')",
+]
```

```diff
+        rows = connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type = 'table'")
+        tables = {str(row[0]) for row in rows}
+        applied_data = 0
+        for statement in DATA_MIGRATIONS:
+            if _data_migration_table(statement) not in tables:
+                continue
+            connection.exec_driver_sql(statement)
+            applied_data += 1
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/execution-critical-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | _pending review_ | — | — | — |

### Verdict

_pending_

---

## Corrections Applied

| # | Correction | Trigger | Resolution |
|---|-----------|---------|------------|
| 1 | AC-42.9 Red assertion `endswith("/retry") == []` | `/api/v1/transcripts/{id}/retry` pre-dates MEU-42 | Corrected to pin the exact pre-existing list — strictly stronger than the original intent. Disclosure 1 |
| 2 | AC-42.15 Red assertion referenced `MIGRATIONS` | Backfill moved to `DATA_MIGRATIONS` | Constant name corrected; assertion substance unchanged. Disclosure 1 |
| 3 | Backfill relocated `MIGRATIONS` → `DATA_MIGRATIONS` | `test_ac_5_6_migrations_empty_apply_is_noop` (all statements must contain `IF NOT EXISTS`) and `test_ac_35_2_migrations_if_not_exists_both_tables` (bare engine → `no such table`) both broke | Sibling append-only list applied by the same `apply_migrations()`, guarded by a `sqlite_master` check. **Neither existing assertion modified.** Disclosure 2 |
| 4 | 29 pre-existing `tests/` ruff violations | Row-7 gate lints `tests/`; canonical receipt does not | Cleared (formatting-only). Plan-vs-canon scope conflict flagged. Disclosure 5 |

---

## Deferred Items

_No AC was deferred._

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| The card's Retry button, kebab, and blocker meta zone | out-of-scope (backend MEU) | MEU-44 (`AC-44.15` renders `BLOCKER_REASONS` + `BLOCKER_REMEDIATION`) | canon §Primary action map |
| Wiring Retry into the three queue pages | out-of-scope | MEU-45, MEU-46, MEU-48 | `.agent/context/meu-status.yaml` phase `'10'` |
| Bulk re-queue over a selection | `BULK_ENDPOINT_POLICY` — no new bulk endpoint this phase | MEU-47 | canon §Selection and bulk model |
| `ruff check tests/` in the registered canonical receipt | scope conflict flagged, not silently resolved | — | `.agent/docs/commands.md:20` — reviewer to rule on whether the canonical receipt should widen to `packages/ tests/` |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-02 | claude-opus-5 | Initial handoff — MEU-42 re-queue widening + blocker-reason invariant, 15 ACs, gate green |

---

## Round 2 — correction of execution-review Finding 1 (2026-09-02)

**Finding (High, reviewer round 1).** `normalize_blocker_reason` only filled a *blank* blocker
reason. A blocked row whose `error_message` was nonblank but **not** the canonical text kept that
stale text forever, on every path: repository `add`/`save`, `apply_defaults_to_pending()` (which
rewrites the row's quality), the refused-Retry save, and the upgrade backfill. Reproduced against
real SQLite (`C:/Temp/av-kit/review-stale-blocker-repro.txt`):

```text
status=QualityBlocked
quality=P360
error_message=The requested 1080p quality is unavailable
```

— a 360p job telling the user 1080p is unavailable, which is exactly the failure mode
`BLOCKER_REASON_INVARIANT` was written to prevent.

### Red first

Two new tests in `tests/e2e/test_api_downloads.py`, run before any production edit — both failed
on the stale text (receipt `C:/Temp/av-kit/r1f1-red.txt`, `2 failed`):

| Test | Surface covered |
|------|-----------------|
| `test_r1f1_stale_blocker_reason_is_canonicalized_at_the_boundary` | repository `add()`, repository `save()`, the refused Retry (409), `apply_defaults_to_pending()` over a legacy stale row (the reviewer's exact repro, asserting `quality is P360` **and** the canonical reason), narrowness (a `Failed` row's `"Traceback: boom"` untouched), and domain purity (the input job is not mutated) |
| `test_r1f1_upgrade_backfills_noncanonical_legacy_blocked_rows` | fresh-engine upgrade over a stale `QualityBlocked` row, a whitespace-only one, and a `Failed` row carrying the *same* stale string (which must survive), plus a second `apply_migrations()` pass for idempotence |

No existing assertion was weakened. One setup-order change inside the new test (the refused-Retry
block runs before the block that lowers the settings default to 360p, because `reset_failed`
revalidates against the *current* default and would otherwise legitimately return 200) — assertions,
expected values and titles are unchanged.

### Green

```diff
--- packages/core/src/avkit_core/domain/download.py
     reason = BLOCKER_REASONS.get(job.status)
     if reason is not None:
-        current = job.error_message
-        if current is None or not current.strip():
-            return replace(job, error_message=reason)
-        return job
+        if job.error_message == reason:
+            return job
+        return replace(job, error_message=reason)
```

```diff
--- packages/infrastructure/src/avkit_infra/database/migrations.py
     + "' WHERE status = 'QualityBlocked'"
-    + " AND (error_message IS NULL OR TRIM(error_message) = '')",
+    + " AND (error_message IS NULL OR error_message <> '"
+    + _QUALITY_BLOCKED_REASON_SQL
+    + "')",
```

The `status = 'QualityBlocked'` clause is unchanged, so a `Failed` row's real error text is still
never rewritten — proved by the third row of the new migration test. The statement stays idempotent:
once the canonical reason is in place the predicate stops matching. `AgeRestricted` needs no
migration statement because the domain boundary canonicalizes it on every add/save (AC-42.14).

### Disclosure — one Green-phase test constant changed

`BLOCKER_REASON_MIGRATION_PREDICATE` (`tests/e2e/test_api_downloads.py`) is asserted by AC-42.15 to
appear verbatim inside a `DATA_MIGRATIONS` statement, so widening the SQL forced it to change with
it:

```diff
-    "status = 'QualityBlocked' AND (error_message IS NULL OR TRIM(error_message) = '')"
+    "status = 'QualityBlocked' AND (error_message IS NULL OR error_message <> '"
+    + QUALITY_BLOCKED_REASON
+    + "')"
```

This is inside the reviewer's accepted correction scope (item 2: *"backfill noncanonical legacy
`QualityBlocked` messages, not only blank ones"*) — the constant mirrors the SQL by design and
carries no independent expectation. AC-42.15's assertions are otherwise untouched.

### Correction to the round-1 dispatch prompt

The round-1 prompt said exactly one Green-phase test edit was disclosed project-wide (the AC-44.4
fixture type annotation). That phrasing was wrong: the two Green-phase assertion corrections in this
handoff's *Corrections Applied* table (AC-42.9 and AC-42.15) were already disclosed here and predate
it. The reviewer flagged this as a non-blocking evidence caveat and it is accepted.

### Gates after the fix

| Gate | Result | Receipt |
|------|--------|---------|
| Targeted (`-k "r1f1 or 42_"`) | 10 passed | `C:/Temp/av-kit/r1f1-green.txt` |
| pytest (full) | **509 passed** (507 + 2 new) | `C:/Temp/av-kit/py-full.txt` |
| pyright | 0 errors, 0 warnings | `C:/Temp/av-kit/pyright.txt` |
| `ruff check packages/ tests/` | All checks passed | `C:/Temp/av-kit/ruff.txt` |
| vitest | 366 passed (43 files) — unchanged | `C:/Temp/av-kit/vitest.txt` |
| Page isolation | `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42` | `C:/Temp/av-kit/page-isolation.txt` |

No UI file was touched by this correction; `PAGE_ISOLATION` counts are byte-identical to round 1.
