---
date: "2026-08-19"
project: "p3-services"
meu: "MEU-10"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-19-p3-services/implementation-plan.md"
build_plan_section: "bp03s3.1"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-19-p3-services-MEU-13-handoff.md"
---

# Handoff: 2026-08-19-p3-services-MEU-10-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-10 — `ExtractCoordinator` + `DownloadService`. Extended `DOWNLOAD_TRANSITIONS` Pending edges only. `reset_failed(job_id)` uses entity method + save (never Protocol bulk). RULE-1/2 in service progress/cookies. `DOWNLOAD_HOOK_WIRING`: fakes call `on_download_progress` / `should_stop`.
**Build Plan Section**: `docs/build-plan/03-service-layer.md` §DownloadService
**Predecessor**: MEU-13 settings/health

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-10.1 | unit | Video → 1 job; playlist → N; title fallback `video_id` | Spec add flow | `test_ac_10_1_video_and_playlist_inserts` | ✅ |
| AC-10.2 | unit | Duplicate `video_id` skipped (warn), not inserted | Spec | `test_ac_10_2_duplicate_video_id_skipped` | ✅ |
| AC-10.3 | unit | Archive + tracking → `Skipped`; tracking off → `Pending`; `clear_queue` keeps archive | Spec; Phase 1 | `test_ac_10_3_archive_skip_and_clear_keeps_archive`; `test_ac_10_3_tracking_off_inserts_pending` | ✅ |
| AC-10.4 | unit | `apply_lock`: incompatible Pending → QualityBlocked; P360/Lowest stay Pending; clear restores | Spec apply_lock | `test_ac_10_4_apply_lock_transitions`; `test_ac_10_4_p360_stays_pending` | ✅ |
| AC-10.5 | unit | SABR Active at add inserts incompatible as QualityBlocked (constructor) | Spec add flow | `test_ac_10_5_add_time_quality_blocked_insert` | ✅ |
| AC-10.6 | unit | `apply_defaults_to_pending` only Pending/QualityBlocked; returns count | Spec 178 | `test_ac_10_6_apply_defaults_skips_done` | ✅ |
| AC-10.7 | unit | Idle→Processing⇄Paused→Idle; pause finishes current; items never `DownloadStatus.Paused`; cancel → Cancelled + Idle | Spec queue runtime | `test_ac_10_7_and_10_8_worker_done_and_pause_cancel`; `test_ac_10_7_pause_after_current`; `test_ac_10_7_cancel_inflight` | ✅ |
| AC-10.8 | unit | First Pending by `queue_position`; commit before download; AgeRestricted/Cancelled/Failed mapping | Spec worker | `test_ac_10_7_and_10_8_worker_done_and_pause_cancel`; `test_ac_10_8_age_restricted` | ✅ |
| AC-10.9 | unit | Non-finite progress fields skipped (RULE-1); no `int(nan)` | Spec; RULE-1 | `test_ac_10_9_nan_progress_skipped` | ✅ |
| AC-10.10 | unit | Cookie mode/path/browser only; `CookieTestError` from `OSError` with `__cause__`; no byte persist | Spec; RULE-2 | `test_ac_10_10_cookie_error_cause`; `test_ac_10_10_unknown_cookie_mode` | ✅ |
| AC-10.11 | unit | Extract mutex+cache download side; same URL within TTL → 1 call; concurrent overlap 0 | Spec extract cache | `test_ac_10_11_extract_cache_and_mutex`; `test_ac_10_11_concurrent_extract_mutex` | ✅ |
| AC-10.12 | unit | Reorder permutation; remove keeps files/archive; missing → NotFound; illegal → Conflict | Spec | `test_ac_10_12_reorder_remove_get_job` | ✅ |
| AC-10.13 | unit | Pending→Skipped via `transition` when archive hits before start; Done→QualityBlocked still Conflict | Local Canon graph | `test_ac_10_13_pending_quality_blocked_and_skipped_edges`; `test_ac_10_13_archive_skip_before_start` | ✅ |
| AC-10.14 | integration | G29 real tmp UoW add + list_ordered | G29 | `test_ac_10_14_g29_real_tmp_uow_download` | ✅ |
| AC-10.15 | unit | `reset_failed(job_id)` entity+save; bulk repo call count 0 | Spec 113 | `test_ac_10_15_reset_failed_single_row` | ✅ |
| AC-10.16 | unit | Getters: `get_queue`=`list_ordered`; processor state; `get_sabr_status` does not probe YouTube | Spec 114–117 | `test_ac_10_16_getters_do_not_probe_sabr` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| collection AC-10 | `ModuleNotFoundError: avkit_core.services.download` | 102/171 passed | `tests/unit/test_services.py:38` |

Receipts: `C:/Temp/av-kit/fail-to-pass-meu-10-queue.txt`, `fail-to-pass-meu-10-worker.txt`. Historical isolated reds were not persisted during TDD; these are reconstructed by temporarily hiding `download.py`/`extract.py` after green. Same collection error covers queue and worker rows.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| H1-2 registered suite | 0 | 171 passed |
| pyright / ruff `packages/core/` | 0 | 0 / clean |
| import-anchored SCAN_CORE_INFRA | 0 | no hexagonal imports in core |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 171 passed
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modified | 28–35 | Pending → Downloading, QualityBlocked, Skipped |
| `packages/core/src/avkit_core/services/extract.py` | new | 1–62 | mutex held during YouTube call; 300s TTL |
| `packages/core/src/avkit_core/services/download.py` | new | 1–586 | commands + worker + RULE-1/2 |
| `tests/unit/test_services.py` | modified | AC-10.* | fakes call hooks |
| `tests/unit/test_domain.py` | modified | `test_ac_10_13_*` | graph edges |

```diff
 DOWNLOAD_TRANSITIONS[Pending] += {Downloading, QualityBlocked, Skipped}
+class ExtractCoordinator:
+    def extract_info(...):
+        with self._lock:  # held during youtube.extract_info
+class DownloadService:
+    def on_download_progress(...):  # skip non-finite before int()
+    def reset_failed(self, job_id: str) -> DownloadJob:  # entity + save
```

`apply_lock` at `download.py:344`. `should_stop` at `:144`. No `avkit_infra` import. Ports untouched.

---

## Codex Validation Report

_Left blank for reviewer agent._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | — | — | — | — |

### Verdict

`pending` — independent Codex `/execution-critical-review`

---

## Corrections Applied (2026-08-19)

**Findings resolved**: 0/0 (pre-review)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| — | — | — | — |

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Adapter ctor hook bind | API/wiring | MEU-14 | `DOWNLOAD_HOOK_WIRING` |
| Cross-service extract overlap | owned by MEU-11 | MEU-11 | AC-11.15 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | Initial MEU-10 handoff |
| Submitted for review | 2026-08-19 | cursor-grok-4.6 | Pending Codex exec review |
