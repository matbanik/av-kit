---
date: "2026-09-02"
review_mode: "implementation"
target_plan: "docs/execution/plans/2026-08-28-p10-queue-card-foundations/implementation-plan.md"
verdict: "approved"
findings_count: 0
round: 2
template_version: "2.1"
requested_verbosity: "standard"
agent: "gpt-5.6-sol"
dispatch_id: "exec-review-p10-queue-card-foundations"
---

# Critical Review: p10-queue-card-foundations

> **Review Mode**: `implementation`
> **Verdict**: `changes_required`

---

## Scope

**Target**: MEU-41 through MEU-44, correlated by the four named handoffs and the execution plan at `docs/execution/plans/2026-08-28-p10-queue-card-foundations/`.

**Review Type**: Multi-handoff implementation review of the Phase 10 queue-card foundations. No page migration was expected or reviewed as missing work.

**Intent anchor**: This execution was supposed to establish the queue-card canon, safely widen re-queue, and deliver accessible prop-driven queue primitives/cards without mounting them. The card and isolation foundations achieve that intent, but the backend's promised persisted blocker-reason invariant does not hold for a nonblank legacy or stale explanation.

---

## Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | High | A nonblank stale blocker explanation is preserved instead of canonicalized. A persisted `QualityBlocked` row whose message names 1080p, followed by Apply Defaults changing the row to 360p, remains `QualityBlocked` at 360p while still displaying the 1080p explanation. This violates AC-42.12/AC-42.14 and the blocker-reason invariant; the same stale value also survives the refused-Retry save and the upgrade backfill because both only repair blank values. | `packages/core/src/avkit_core/domain/download.py:86-91`; `packages/core/src/avkit_core/services/download.py:398-419`; `packages/infrastructure/src/avkit_infra/database/migrations.py:84-92` | For a blocker status, replace any value unequal to that status's canonical `BLOCKER_REASONS` value, not only `None`/blank. Extend the upgrade migration to canonicalize noncanonical `QualityBlocked` messages while continuing to preserve non-blocker failures. Add integration coverage for a nonblank quality-specific legacy reason through repository add/save, Apply Defaults, refused Retry, and fresh-engine upgrade. | open |

### Finding 1 reproduction

The independent real-stack reproduction persisted a `QualityBlocked` 1080p row with `error_message="The requested 1080p quality is unavailable"`, changed downloader defaults to 360p, then called `apply_defaults_to_pending()`. The committed readback was:

```text
status=QualityBlocked
quality=P360
error_message=The requested 1080p quality is unavailable
```

Receipt: `C:/Temp/av-kit/review-stale-blocker-repro.txt`.

The cause is the early `return job` for every nonblank blocker message at `download.py:91`. Existing tests cover `None`, blank, canonical, and non-blocker traceback values, but not a nonblank noncanonical blocker reason.

---

## Checklist Results

### Information Retrieval (IR)

| Check | Result | Evidence |
|-------|--------|----------|
| Runtime / persistence contract | fail | The blocker revalidation branch itself does not launder an incompatible job, but the real SQLite reproduction above disproves the broader persisted-reason invariant. `Skipped` remains excluded in the domain sets, transition guards, service path, repository bulk reset, and card default retry set. |
| Boundary validation | pass | Both reset routes retain strict `EmptyIn` (`extra="forbid"`), return 422 for extra keys, 404 for unknown ids, and 409 for non-re-queueable states. The plan deliberately defines `id` as an opaque string and has no create/update pair for these routes. |
| Card keyboard and screen-reader model | pass | Checkbox, primary action, and kebab are DOM siblings of the `role="button"` region. Enter/Space activation suppresses Space scrolling. The menu implements Enter/Space/ArrowDown open, roving arrows, Escape refocus, Tab close, and outside-click close. Browse is a native button. |
| One-primary-action and destructive semantics | pass | `resolvePrimaryAction` returns one value at most; queue Cancel requires `isInFlight`, calls a zero-argument queue callback, is named `Cancel queue`, has the scope-bearing title, and opens no dialog. No page currently wires Remove directly to deletion; the verb-labelled confirm remains a migration-host responsibility. |
| Drag/drop state machine | pass | Nested enter/leave uses a depth counter; drop resets depth before callback; unmount leaves no global listener or asynchronous work. Rejected payloads show a reason during hover, and QueueList overlays without removing or sorting cards. The jsdom `dataTransfer` seam drives the same React handler fields used in Electron. |
| Page/dependency isolation | pass | Live gate: `PASS: PAGE_ISOLATION frozen=28 carveout=2 scanned=73 e2e=59 preserved=42`. Its 19-case self-test rejected frozen edits/adds/deletes, illegal carve-outs, direct/barrel/alias reachability, E2E identity drift, testid loss, and missing baseline. |
| Token port and contrast | pass | All four dark/light token values are byte-identical to `P:/zorivest/ui/src/renderer/src/globals.css`. The suite recomputes 80 label pairings from `styles.css`, enforces >= 4.5, and pins the full matrix. |

### Test rigor audit (IR-5)

| Test surface | Grade | Evidence |
|--------------|-------|----------|
| `ui/tests/unit/queue-canon.test.ts` | Strong | Direct source/token parity, supersession preservation, status mapping, and SSOT/matrix assertions. |
| `ui/tests/unit/queue-primitives.test.ts` | Strong | Runtime DOM/ARIA/focus assertions plus independently recomputed contrast and strict-envelope negatives. |
| `ui/tests/unit/queue-card.test.ts` | Strong | Rendered ancestry, callback isolation, action ordering, focus movement, server-order preservation, drag states, and page-isolation assertions. |
| MEU-42 domain/API suites | Adequate with material gap | The status/route matrices and real-stack round trips are meaningful, but AC-42.12/14/15 omit the nonblank noncanonical blocker case reproduced above. |

No `.skip`, `.only`, `.todo`, pytest skip/xfail, conditional test escape, or tautological pass was found in the reviewed suites. The fabricated `dataTransfer` does not mock the hook or state transitions; it only supplies the browser object jsdom lacks.

### Evidence caveat (non-blocking, not counted as a finding)

The dispatch prompt says the only Green-phase test edit was the AC-44.4 fixture type annotation. That is not accurate across the project: the MEU-42 handoff discloses, and `C:/Temp/av-kit/fail-to-pass-meu-42-py.txt:55-60,114-118` proves, two Green-phase assertion changes. AC-42.9 changed `no /retry paths` to the exact pre-existing transcript retry path, and AC-42.15 changed `MIGRATIONS` to `DATA_MIGRATIONS`. The current assertions are meaningful, so this is not a second product finding, but `assert-red-oracle.ps1` checks failed AC titles rather than hashing test source and therefore cannot prove assertion immutability. The AC-44.4 current edit is type-only in the reviewed file; no Red source snapshot exists to independently prove it was the sole MEU-44 edit.

---

## Commands Executed

| Verification | Result | Receipt |
|--------------|--------|---------|
| Full Python suite | 507 passed, 1 warning | `C:/Temp/av-kit/review-pytest-full.txt` |
| Full UI unit suite | 366 passed in 43 files | `C:/Temp/av-kit/review-vitest-full.txt` |
| Pyright + Ruff | 0 errors; clean | `C:/Temp/av-kit/review-python-static.txt` |
| TypeScript + ESLint + Electron build | clean; build completed | `C:/Temp/av-kit/review-ui-static-build.txt` |
| OpenAPI drift | exit 0, empty canonical output | `C:/Temp/av-kit/review-openapi-check.txt` |
| Page isolation self-test + live gate | 19 cases; live 28/2/73/59/42 | `C:/Temp/av-kit/review-page-isolation-selftest.txt`; `C:/Temp/av-kit/review-page-isolation-live.txt` |
| Red-oracle self-test | 11 cases | `C:/Temp/av-kit/review-red-oracle-selftest.txt` |
| Handoff AC/marker gates | pass | `C:/Temp/av-kit/review-handoff-acs-live.txt`; `C:/Temp/av-kit/review-handoff-markers-live.txt` |
| Stale blocker real-stack reproduction | reproduced | `C:/Temp/av-kit/review-stale-blocker-repro.txt` |

---

## Verdict

`changes_required` - The foundations are largely sound, including safe Retry revalidation, accessibility structure, drag behavior, isolation, and token contrast. Approval is blocked by one reproduced High persistence defect: a nonblank stale blocker explanation survives a quality-changing partial update and contradicts the row shown to the user.

### Accepted correction scope

1. Canonicalize nonblank noncanonical blocker messages at the persistence boundary.
2. Backfill noncanonical legacy `QualityBlocked` messages, not only blank ones.
3. Add the missing real-stack regression cases without weakening existing assertions.
4. Re-run the targeted MEU-42 suite, full Python gate, and the unchanged UI/isolation gates, then append round 2 to this file.

### Residual risk

Playwright remains the acknowledged external Electron/Playwright launch blocker and is not a finding in this round. Remove confirmation is not yet page-wired because page migration is expressly MEU-45-47 scope; review that host wiring when it lands.

---

## Round 2 Recheck (2026-09-02)

**Intent anchor**: This recheck determines whether the sole round-1 persistence defect is closed
across every named write/upgrade path without erasing legitimate non-blocker failures. The already
accepted queue-card, accessibility, drag/drop, token, and isolation work was not reopened.

### Findings

None.

### Round-1 Finding Disposition

| Round-1 finding | Status | Recheck evidence |
|-----------------|--------|------------------|
| 1. Nonblank noncanonical blocker reasons survived persistence and upgrade | **resolved** | `normalize_blocker_reason` now replaces every differing blocker message with the status's canonical reason (`packages/core/src/avkit_core/domain/download.py:78-93`), and both repository writers still apply it (`packages/infrastructure/src/avkit_infra/database/repositories.py:74-93`). The real-stack test proves `add`, `save`, refused Retry, Apply Defaults after 1080p→360p, API readback, non-blocker narrowness, and domain purity (`tests/e2e/test_api_downloads.py:666-749`). The upgrade test proves stale and whitespace `QualityBlocked` rows are repaired while an identically worded `Failed` row survives two migration passes (`tests/e2e/test_api_downloads.py:752-790`). |

### Substantive Recheck

- **All named paths are closed.** Apply Defaults and the refused-Retry branch both save through the
  normalizing repository (`packages/core/src/avkit_core/services/download.py:317-341`, `:398-420`),
  so they cannot bypass the corrected pure function. The migration uses the same canonical literal
  and is applied through the existing engine-initialization migration path
  (`packages/infrastructure/src/avkit_infra/database/migrations.py:84-123`).
- **The overwrite is the intended invariant, not over-reach.** Generic yt-dlp/domain failures are
  stored as `Failed`; the production age-gate adapter raises the canonical
  `"video is age-restricted"` string. `QualityBlocked` is the SABR policy state, not a container for
  arbitrary yt-dlp diagnostics. Therefore a differing message on either blocker status is
  inconsistent state under `BLOCKER_REASON_INVARIANT`. If future blocker-specific diagnostics must
  be retained, they need a separate diagnostic field or an explicit contract change rather than an
  exception to this invariant.
- **The migration is narrow, indexed, and idempotent.** Its `status = 'QualityBlocked'` predicate
  leaves every `Failed` row alone, even one carrying the same stale string. A synthetic 120,000-row
  SQLite verification used `ix_download_jobs_status`, changed exactly 60,000 noncanonical blocker
  rows on the first pass, changed zero on the second, left zero noncanonical `QualityBlocked` rows,
  and preserved all 20,000 `Failed` and 20,000 `AgeRestricted` controls. The single set-based UPDATE
  remains transactional; the synthetic timing is evidence of query shape, not a production latency
  guarantee.
- **The new tests are non-vacuous.** `C:/Temp/av-kit/r1f1-red.txt` reports both new tests failing on
  the exact stale-string assertions before the production corrections: repository `add` and fresh
  engine upgrade. Current assertions then force the remaining `save`, Retry, Apply Defaults,
  narrowness, purity, and second-pass cases. Reverting either production correction makes its
  corresponding new test fail.
- **The Green-phase constant edit is honest.** `BLOCKER_REASON_MIGRATION_PREDICATE` is a structural
  mirror of the SQL and does not independently prove behavior, but it is not carrying that burden:
  the two real-database upgrade tests independently assert stale/blank repair, canonical stability,
  non-blocker preservation, and repeat execution (`tests/e2e/test_api_downloads.py:625-659`,
  `:752-790`). Changing the mirror to match the accepted widened predicate did not weaken those
  assertions.
- **The new test's setup order is valid.** The refused Retry executes under the original incompatible
  default before the test lowers the default to 360p for Apply Defaults (`tests/e2e/test_api_downloads.py:698-719`);
  otherwise a 200 response would be the correct product behavior.
- **The Playwright blocker retraction is supported.** The preserved rerun receipt records a rebuilt
  bundle and `59 passed / 0 failed`; `task.md` H1-2a is `[x]`. This correction did not touch UI code,
  so the round-1 UI conclusions remain unaffected.

### Test Rigor (IR-5 / AV)

| Surface | Grade | Evidence |
|---------|-------|----------|
| `test_r1f1_stale_blocker_reason_is_canonicalized_at_the_boundary` | Strong | Real SQLite repository/service/API chain; exact status, quality, message, narrowness, and purity assertions; failed before the code change. |
| `test_r1f1_upgrade_backfills_noncanonical_legacy_blocked_rows` | Strong | Fresh-engine migration plus repeat pass; exact blocker repair and same-string `Failed` preservation; failed before the SQL change. |
| Existing AC-42.14/42.15 coverage affected by the correction | Strong | Direct repository ownership and real upgrade behavior remain asserted; no skip/xfail or exception safety net. |

### Verification Evidence

| Check | Result | Receipt |
|-------|--------|---------|
| Red receipt inspection | Both new tests failed on the stale text before production edits | `C:/Temp/av-kit/r1f1-red.txt` |
| Independent affected-suite rerun | `10 passed`, `10 deselected` | `C:/Temp/av-kit/review-r2-targeted-venv2.txt` |
| Independent full Python suite | `509 passed`, 1 warning | `C:/Temp/av-kit/review-r2-pytest-full.txt` |
| Independent Pyright | `0 errors, 0 warnings` | `C:/Temp/av-kit/review-r2-pyright.txt` |
| Independent Ruff | `All checks passed` for `packages/ tests/` | `C:/Temp/av-kit/review-r2-ruff.txt` |
| Synthetic migration scale/idempotence check | 120,000 rows; indexed search; 60,000 then 0 changes; non-blockers preserved | `C:/Temp/av-kit/review-r2-migration-scale.txt` |
| Recorded rebuilt Electron regression rerun | `59 passed` | `C:/Temp/av-kit/e2e-regression-rerun.txt` |

The canonical `uv` command could not initialize its user cache inside this reviewer sandbox, and
pytest's default user-temp root was likewise inaccessible. The independent runs therefore used the
repository's existing `.venv` executables, an explicit fresh `C:/Temp/av-kit/` basetemp, and the
cache provider disabled. Those environment-only failures are preserved at
`C:/Temp/av-kit/review-r2-targeted.txt` and `C:/Temp/av-kit/review-r2-targeted-venv.txt`; neither
reached a product assertion.

### Open Questions / Assumptions

None.

### Verdict

`approved` — Round-1 Finding 1 is resolved on every accepted correction path. The implementation
now enforces one canonical explanation for blocker states, preserves real non-blocker failures, and
upgrades legacy rows with a narrow idempotent statement. No blocking finding remains.

**Residual risk**: Canonical blocker copy intentionally cannot retain a second, status-specific
diagnostic in `error_message`. That is the declared data contract, not a regression; a future need
for both user-facing reason and low-level diagnostic would require separate storage.
