---
review_mode: implementation
target_plan: docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md
agent: gpt-5.6-sol
verdict: approved
findings_count: 0
round: 2
date: 2026-08-27
template_version: 2.1
dispatch_id: p9-capture-engine-exec-r2
---

# Critical Review: p9-capture-engine

> **Review Mode**: `implementation`
> **Verdict**: `changes_required`

## Intent Anchor

Session 16 was intended to deliver the capture engine only—MEU-34 domain contracts, MEU-35 SQLite/mss/Pillow infrastructure, and MEU-36 capture service behavior—without starting REST, MCP, Capture GUI, MEU-37–39, or Session 8c. The implementation covers most of that engine and its registered gates are green, but three independently reproduced state/identity defects mean the delivered work does not yet achieve the approved contract.

## Findings

| Finding | Severity |
|---|---|
| **F1 — Scanning after annotation registers the annotated derivative as a second original shot.** `scan_inbox()` accepts every top-level path whose suffix is `.png` and adds an unseen path as `CaptureSource.Scan` (`packages/core/src/avkit_core/services/capture.py:131-160`), while `annotate_and_save()` writes `{stem}.annotated.png` into that same inbox (`packages/core/src/avkit_core/services/capture.py:293-340`). The canonical model defines one row per original and uses `annotated_path` as the annotation flag (`docs/build-plan/09-screenshot-capture.md:210-221`), and AC-36.1/AC-36.9 combine scan with annotated-output behavior (`implementation-plan.md:305`, `implementation-plan.md:313`). A real Pillow + temporary-SQLite probe produced `['original.annotated.png', 'original.png']` after bake then scan (`C:/Temp/av-kit/p9-engine-exec-r1-real-sqlite-repros.txt`). The existing scan test only seeds an original PNG, GIF, and nested PNG (`tests/unit/test_capture_service.py:111-130`), so all 302 tests stay green. Exclude deterministic annotated derivatives from inbox discovery and add a bake→scan/list regression proving exactly one original row remains. | High |
| **F2 — A failed `complete_request` commits an orphan `CaptureShot` before request validation.** `complete_request()` calls `register_shot()` first, then performs the request transition (`packages/core/src/avkit_core/services/capture.py:262-270`). Registration commits through its own UoW (`packages/core/src/avkit_core/services/capture.py:196-231`); only afterward can `_transition_request()` raise for an unknown or non-Pending request (`packages/core/src/avkit_core/services/capture.py:403-421`). This violates AC-36.8 and the explicit one-UoW-per-mutating-method/transition lock (`implementation-plan.md:142`, `implementation-plan.md:312`, `implementation-plan.md:342`). A real temporary-SQLite probe completed an unknown UUID, raised `NotFoundError`, and still left `['orphan.png']` in `capture_shots` (`C:/Temp/av-kit/p9-engine-exec-r1-real-sqlite-repros.txt`). Validate the request and perform registration + transition atomically, with negative tests proving unknown, cancelled, and expired requests leave `capture_shots` unchanged. | High |
| **F3 — The domain permits `CaptureRequest(status=Completed, shot_id=None)`.** AC-34.5 says `shot_id` is optional **until** Completed (`implementation-plan.md:170`), matching the canonical `shot_id` “yes when Completed” contract (`docs/build-plan/09-screenshot-capture.md:236-246`). `CaptureRequest.__post_init__()` only validates `shot_id` when it is already non-null and never couples it to status (`packages/core/src/avkit_core/domain/capture.py:258-275`). The current test constructs only the valid Completed form and does not assert rejection of the invalid form (`tests/unit/test_domain_capture.py:198-209`). The independent constructor probe successfully created `Completed` with `None` (`C:/Temp/av-kit/p9-engine-exec-r1-repro-completed-null-shot.txt`). Enforce the status/shot invariant in the domain and add the missing negative test. | High |
| **F4 — Several plan ACs labeled `integration` have only unit-marked lifecycle evidence.** AC-35.1–35.3 require live table/migration/repository behavior (`implementation-plan.md:234-236`), but their matching tests inspect SQLAlchemy metadata, migration strings, and `hasattr` under `@pytest.mark.unit` (`tests/unit/test_capture_adapter.py:86-147`). AC-36.1, AC-36.2, AC-36.8, AC-36.9, and AC-36.11 are also declared integration ACs (`implementation-plan.md:305-315`) but use the fake `_stack` and are unit-marked (`tests/unit/test_capture_service.py:111-144`, `tests/unit/test_capture_service.py:269-370`). AC-35.4 and AC-36.13 do provide real temporary-SQLite coverage, and the product code currently passes the independent runtime probes, so this is an IR-7 lifecycle-evidence gap rather than an additional blocking product defect. Add real-SQLite/real-adapter contract coverage, including applying migrations twice and exercising repository save/delete paths. | Medium |

## Scope

**Correlated plan:** `docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md` (user-identified plan review Round 5 `approved`)

**Expanded handoff set:**

- `.agent/context/handoffs/2026-08-26-p9-capture-engine-MEU-34-handoff.md`
- `.agent/context/handoffs/2026-08-26-p9-capture-engine-MEU-35-handoff.md`
- `.agent/context/handoffs/2026-08-26-p9-capture-engine-MEU-36-handoff.md`

**Correlation rationale:** the named set declares exactly these three handoffs and the plan/task bind Session 16 to MEU-34 + MEU-35 + MEU-36. REST `/captures`, MCP `avkit_capture`, tray/F2/overlay, Capture GUI, MEU-37–39 packing, invented MEU IDs, and Session 8c were treated as explicit exclusions—not missing implementation.

**Implementation reviewed:** the user-named domain, port, settings, queue, persistence, migration, mapper, repository, UoW, adapter, service, test, SSOT, task, named-set, spec, and handoff surfaces. Current file state was used because Git history was not assumed available.

## Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| `uv run pytest tests/unit tests/integration -x --tb=short -v` | 302 passed, 1 warning | `C:/Temp/av-kit/p9-engine-exec-r1-pytest.txt` |
| `uv run pyright packages/core packages/infrastructure` | 0 errors, 0 warnings | `C:/Temp/av-kit/p9-engine-exec-r1-pyright.txt` |
| Scoped Ruff command from the named set | all checks passed | `C:/Temp/av-kit/p9-engine-exec-r1-ruff.txt` |
| `assert-openapi-skip.ps1` | API tree unchanged, count 27 | `C:/Temp/av-kit/p9-engine-exec-r1-openapi-skip.txt` |
| `assert-handoff-acs.ps1` | exact per-MEU AC sets pass | `C:/Temp/av-kit/p9-engine-exec-r1-handoff-acs.txt` |
| Red-oracle validation for MEU-34/35/36 | counts 13 / 14 / 14 pass; non-fail-fast receipts accepted | `C:/Temp/av-kit/p9-engine-exec-r1-red34.txt`; `...-red35.txt`; `...-red36.txt` |
| SSOT exact probe | MEU-34/35/36 `ready_for_review`, no-slash MEU binding, slash phase-9 entry | `C:/Temp/av-kit/p9-engine-exec-r1-ssot.txt` |
| Core/queue/error/dependency/G29 source-isolation probe | all seven contract checks pass | `C:/Temp/av-kit/p9-engine-exec-r1-contract-absence.txt` |
| Placeholder + capture-test skip/xfail scan | no hits | `C:/Temp/av-kit/p9-engine-exec-r1-placeholder-skip-scan.txt` |
| AST assertion-strength audit across all seven scoped test files | no assertion-free collected capture tests; counts recorded below | `C:/Temp/av-kit/p9-engine-exec-r1-test-rigor-ast.txt` |
| Real Pillow + temporary-SQLite adversarial probe | F1 and F2 independently reproduced | `C:/Temp/av-kit/p9-engine-exec-r1-real-sqlite-repros.txt` |
| Direct domain constructor probe | F3 independently reproduced | `C:/Temp/av-kit/p9-engine-exec-r1-repro-completed-null-shot.txt` |

## Checklist Results

### Implementation Review (IR)

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | AC-36.13 uses real temporary SQLite + real `CaptureAdapter.probe` (`tests/unit/test_capture_service.py:394-440`); the independent real-stack probes and 302-test run completed. |
| IR-2 Stub behavioral compliance | pass | No completed-deliverable stubs were found; real repository add/get/list/path round trips pass. |
| IR-3 Error mapping completeness | n/a | No REST route is in Session 16 scope; REST `/captures` remains MEU-37. |
| IR-4 Fix generalization | n/a | Round 1; no prior implementation-review finding exists. |
| IR-5 Test rigor audit | fail (F1–F3) | Assertions are generally specific, but the missing cross-operation and negative invariants allow three live defects through a 302-pass suite. Per-file grades follow. |
| IR-6 Boundary validation coverage | fail (F3) | Python domain construction accepts a Completed request without its required shot ID. External REST/MCP schemas are explicitly deferred. |
| IR-7 Deferral and AC-coverage integrity | fail (F4) | Every AC ID appears in the matching handoff and all declared deferrals are scheduled or source-backed; lifecycle evidence fails for the unit-only integration AC subset. |

### IR-5 Test Rigor Audit

| Test file | Grade | Rationale |
|---|---|---|
| `tests/unit/test_domain_capture.py` | 🟡 Adequate | 13 tests, 57 assertions, 20 `pytest.raises`, no skips; exact enum/VO/port checks, but no Completed-with-null-shot rejection. |
| `tests/unit/test_capture_adapter.py` | 🟡 Adequate | 14 tests, 75 assertions, six negative raises, fake mss and real Pillow checks; AC-35.1–35.3 do not exercise their declared integration lifecycle. |
| `tests/unit/test_capture_service.py` | 🟡 Adequate | 14 tests, 80 assertions, eight negative raises, no skips; strong single-method checks, but no bake→scan identity test or failed-completion side-effect assertion, and several integration ACs use fake repositories. |
| `tests/unit/test_domain.py` | 🟢 Strong for scoped KEEP updates | Exact capture enum, namespace, forbidden-import, and runtime Protocol membership assertions. |
| `tests/unit/test_services.py` | 🟢 Strong for scoped KEEP updates | Fake UoW exposes both capture repositories and the AST guard proves service source has no direct `mkdir` (`tests/unit/test_services.py:2113-2127`). |
| `tests/unit/test_conversion_service.py` | 🟢 Strong for scoped KEEP updates | Fake UoW capture repositories preserve the shared storage contract without weakening conversion assertions. |
| `tests/integration/test_sqlite_uow.py` | 🟢 Strong | 18 tests and 155 assertions over real SQLite schema/UoW behavior; capture table and runtime UoW names are included. |

### Adversarial Verification (AV)

| Check | Result | Evidence |
|---|---|---|
| AV-1 Failing-then-passing proof | pass | Red-oracle scripts independently accept the 13/14/14 receipts; the Red pytest commands were non-fail-fast. |
| AV-2 No bypass hacks | pass | AST audit found no private patch calls or try/except safety nets in the three capture test files. |
| AV-3 Changed paths exercised by assertions | fail | The primary paths are asserted, but F1–F3 identify unasserted state transitions/interactions that fail live. |
| AV-4 No skipped/xfail masking | pass | No skip/xfail marker exists in the three capture test files; the scoped placeholder/G36 scan is clean. |
| AV-5 No unresolved placeholders | pass | No `TODO`, `FIXME`, `NotImplementedError`, or placeholder stub hit in the scoped capture deliverables. |
| AV-6 Source-backed criteria | pass | Plan ACs use Spec/Local Canon/Research-backed sources; no unsourced product behavior was used as a finding. |

### Contract and Evidence Checks

| Check | Result | Evidence |
|---|---|---|
| Queue/error/port locks | pass | `captures` absent from `QUEUE_NAMES`; no Python `HotkeyConflictError`; capture port has no future-annotations import. |
| mss grab and black-frame behavior | pass | Non-Windows guard precedes grab; fullscreen uses monitors[0]; mean luminance `<= 2.0` raises before PNG write; fake-mss tests pass. |
| Pillow bake behavior | pass | RGBA highlight + `Image.alpha_composite`, arrow line + polygon constants, and font-candidate/default fallback are present; original-hash test passes. |
| Tables/UoW | pass subject to F4 evidence depth | Unique/index declarations, `CREATE TABLE IF NOT EXISTS`, repositories, and runtime Protocol properties are present; real UoW round trip passes. |
| Register/naming/request/settings/remove | pass except F2/F3 | Containment, idempotent same-size registration, size refresh, local timestamp collisions, TTL/conflict/expiry, sidecar/empty clear, removal, and capture settings pass their targeted checks. |
| Scan/annotation interaction | fail (F1) | Real-stack bake→scan duplicates the derivative as an original row. |
| G29 isolation and dependencies | pass | Real temporary-SQLite probe, download/TTS/conversion source isolation, `pillow>=10.0`, `mss>=9.0`, and core import ban all pass. |
| Handoff/SSOT/OpenAPI-skip integrity | pass | AC set, red counts, exact status/path binding, and source-only API hash checks pass. |

## Open Questions / Assumptions

None. F1 is anchored to the canonical one-row-per-original/annotated-path model, and F2 is anchored to the plan's explicit one-UoW atomicity lock; neither depends on an unstated product choice.

## Required Follow-up

Use `/execution-corrections` for F1–F4. Add Red→Green regression tests before production changes, preserve the existing tests, then rerun the registered Python/type/lint/red-evidence/handoff/SSOT/OpenAPI-skip checks and dispatch an independent Round 2 recheck. Do not start `p6-gui-console-polish` / MEU-27, MEU-37–39, REST `/captures`, MCP `avkit_capture`, tray/F2/overlay, or Capture GUI as part of these corrections.

## Verdict

`changes_required` — F1–F3 are independently reproduced High behavioral/contract defects. The green 302-test suite, type/lint gates, red-oracle receipts, handoff AC coverage, SSOT binding, and OpenAPI skip do not override duplicate capture identity, non-atomic failed completion, or an invalid Completed request domain state.

## Residual Risk

The review exercised current domain, SQLite, real Pillow probe/bake, service state transitions, and registered regression gates. Live unattended desktop capture was not run because the approved contract uses fake mss for this session; REST, MCP, and GUI surfaces were explicitly excluded and were not treated as missing work.

---

## Corrections Applied — 2026-08-27 after Round 1

Implementer (not the reviewer). Red receipt: `C:/Temp/av-kit/fail-to-pass-p9-exec-r1-corrections.txt` (3 failed). Green: `C:/Temp/av-kit/pytest-p9-exec-r1-corrections-green.txt`. Full gate: `C:/Temp/av-kit/meu-all-gate-r2.txt` (**305 passed**).

| Finding | Fix | Tests |
|---------|-----|-------|
| F1 | `scan_inbox` skips names ending with `ANNOTATED_SUFFIX` | `test_ac_36_1_scan_skips_annotated_derivative`; real SQLite bake→scan in `test_ac_36_9_real_sqlite_bake_scan_one_original` |
| F2 | `complete_request` validates the request and upserts the shot in **one** UoW | `test_ac_36_8_failed_complete_does_not_orphan_shot` (unknown / cancelled / expired) |
| F3 | `CaptureRequest` requires `shot_id` when `Completed` | `test_ac_34_5_capture_request_fields_optional_shot` negative |
| F4 | Live `apply_migrations` twice; UoW save/delete; real bake→scan | `test_ac_35_2_*` engine apply; `test_ac_35_4_*` save/delete; `test_ac_36_9_real_sqlite_*` |

---

## Round 2 Recheck — 2026-08-27

**Workflow:** `/execution-critical-review`  
**Dispatch ID:** `p9-capture-engine-exec-r2`  
**Agent:** `gpt-5.6-sol`

### Intent Anchor

This recheck determines whether the Round 1 corrections now deliver the Session 16 capture engine contract for MEU-34–36: one row per original after annotation, atomic failed-completion behavior, a valid Completed-request domain state, and real persistence/lifecycle evidence. REST `/captures`, MCP `avkit_capture`, tray/F2/overlay, Capture GUI, MEU-37–39, and Session 8c remain explicit exclusions.

### Findings

| Finding | Severity | Status | Evidence |
|---|---|---|---|
| No Round 2 findings. No evidence-backed High or Critical behavioral or contract defect remained after generate→verify review and the Materiality Gate. | — | closed | 44 scoped capture tests and the 305-test full suite pass independently; source and regression checks below. |

### Prior Pass Summary

| Finding | Prior Severity | Recheck Result | Evidence |
|---|---|---|---|
| F1 — annotated derivative registered as a second original | High | ✅ Fixed | `scan_inbox` skips `ANNOTATED_SUFFIX` before probing/upsert (`packages/core/src/avkit_core/services/capture.py:132-177`). The fake-stack regression asserts exactly `['original.png']` and one repository row (`tests/unit/test_capture_service.py:470-488`); the real SQLite bake→list path asserts the same invariant (`tests/unit/test_capture_service.py:529-578`). |
| F2 — failed complete orphaned a shot | High | ✅ Fixed | `complete_request` validates request existence and transition eligibility before `_upsert_shot`, then saves the Completed transition in the same UoW (`packages/core/src/avkit_core/services/capture.py:237-260`). Unknown, Cancelled, and Expired cases assert an unchanged shot repository (`tests/unit/test_capture_service.py:491-526`), and the real SQLite unknown-ID path preserves only the original row (`tests/unit/test_capture_service.py:572-578`). |
| F3 — Completed allowed `shot_id=None` | High | ✅ Fixed | `CaptureRequest.__post_init__` rejects Completed without a shot ID (`packages/core/src/avkit_core/domain/capture.py:259-277`). The test retains a valid Pending/no-shot case and adds the Completed/no-shot negative assertion (`tests/unit/test_domain_capture.py:193-213`). |
| F4 — integration lifecycle evidence gap | Medium | ✅ Fixed | `apply_migrations` runs twice against a real engine (`tests/unit/test_capture_adapter.py:115-130`); a real `SqlAlchemyUnitOfWork` round-trip now covers repository save and delete (`tests/unit/test_capture_adapter.py:149-232`); real Pillow + SQLite bake→scan/list is exercised (`tests/unit/test_capture_service.py:529-578`). Existing unit markers do not negate these live runtime paths. |

### Commands Executed

| Verification | Result | Receipt |
|---|---|---|
| `uv run pytest tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py -v --tb=short` | 44 passed | `C:/Temp/av-kit/p9-engine-exec-r2-pytest-targeted.txt` |
| `uv run pytest tests/unit tests/integration -x --tb=short -v` | 305 passed, 1 warning | `C:/Temp/av-kit/p9-engine-exec-r2-pytest-full.txt` |
| `uv run pyright packages/core packages/infrastructure` | 0 errors, 0 warnings | `C:/Temp/av-kit/p9-engine-exec-r2-pyright.txt` |
| `uv run ruff check packages/core packages/infrastructure tests/unit/test_domain_capture.py tests/unit/test_capture_adapter.py tests/unit/test_capture_service.py` | All checks passed | `C:/Temp/av-kit/p9-engine-exec-r2-ruff.txt` |
| `assert-openapi-skip.ps1` (source-only; no `-o`) | API tree unchanged, count 27 | `C:/Temp/av-kit/p9-engine-exec-r2-openapi-skip.txt` |
| Queue/error/port/service static-lock probe | pass | `C:/Temp/av-kit/p9-engine-exec-r2-static-locks.txt` |
| Implementer Red correction receipt | 3 intended failures reproduced in receipt | `C:/Temp/av-kit/fail-to-pass-p9-exec-r1-corrections.txt` |
| Implementer correction Green receipt | 7 passed | `C:/Temp/av-kit/pytest-p9-exec-r1-corrections-green.txt` |

### Checklist Results

| Check | Result | Evidence |
|---|---|---|
| IR-1 Live runtime evidence | pass | Real SQLite migration/UoW and real Pillow bake→scan paths execute in the scoped suite. |
| IR-2 Stub behavioral compliance | pass | No stub is involved in the corrected persistence or bake→scan paths. |
| IR-3 Error mapping completeness | n/a | REST is MEU-37 and outside Session 16. |
| IR-4 Fix generalization | pass | F1–F4 are each verified by current file state and executable regressions; unknown, Cancelled, and Expired completion paths are covered. |
| IR-5 Test rigor audit | pass | No scoped test file is 🔴 Weak; per-file grades follow. |
| IR-6 Boundary validation coverage | pass for Session 16 | Completed/no-shot construction is rejected; REST/MCP schemas remain scheduled MEU-37/38. |
| IR-7 Deferral and AC-coverage integrity | pass | Real lifecycle evidence closes F4; all Session 16 ACs remain represented, and excluded surfaces are scheduled rather than silently dropped. |

### IR-5 Test Rigor Audit

| Test file | Grade | Rationale |
|---|---|---|
| `tests/unit/test_domain_capture.py` | 🟢 Strong | Specific domain values and negative constructors are asserted, including Pending/no-shot validity and Completed/no-shot rejection. |
| `tests/unit/test_capture_adapter.py` | 🟢 Strong | Specific adapter outputs and negative paths are asserted; migrations, real UoW round-trip, save, and delete run against SQLite. |
| `tests/unit/test_capture_service.py` | 🟢 Strong | Specific state, row-count, file, and error invariants cover fake and real SQLite paths, including all three failed-completion states and bake→scan identity. |

### Regression Spot-Checks

| Surface | Result | Evidence |
|---|---|---|
| No `captures` queue, no Python `HotkeyConflictError`, no future-annotations import in `ports/capture.py`, no service `mkdir` | pass | `C:/Temp/av-kit/p9-engine-exec-r2-static-locks.txt`; source lines `packages/core/src/avkit_core/ports/capture.py:1-28` |
| Black-frame rejection and mss virtual monitor 0 | pass | `test_ac_35_9_black_frame_fails_and_leaves_no_png` and `test_ac_35_6_fullscreen_grabs_monitor_zero` passed in the 44-test receipt; implementation at `packages/infrastructure/src/avkit_infra/capture/adapter.py:82-85`, `142-146`, `193-207`. |
| G29 isolation | pass | `test_ac_36_13_g29_tmp_sqlite_and_isolation` passed and continues to assert download/TTS/conversion source isolation (`tests/unit/test_capture_service.py:394-440`). |
| Session 16 scope lock / OpenAPI skip | pass | Plan remains MEU-34–36 only; source-only API hash is unchanged. No REST, MCP, tray/F2, or Capture GUI requirement was imposed. |

### Open Questions / Assumptions

None. Current file state was reviewed directly because Git history was not assumed available.

### Verdict

`approved` — Round 1 F1–F4 are fixed. The corrected runtime behavior satisfies the Session 16 MEU-34–36 contract, all independently executed targeted and full checks pass, and no blocking behavioral or contract finding remains.

### Follow-up

No execution correction is required. This review does not authorize or begin Session 8c / MEU-27, MEU-37–39 packing, REST `/captures`, MCP `avkit_capture`, tray/F2/overlay, or Capture GUI work.

### Residual Risk

Live unattended desktop capture was not exercised; the approved Session 16 contract uses fake mss for deterministic display-independent verification. REST, MCP, and GUI surfaces remain outside this review scope.
