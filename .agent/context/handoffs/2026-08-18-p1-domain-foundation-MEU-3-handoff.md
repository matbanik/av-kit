---
date: "2026-08-19"
project: "p1-domain-foundation"
meu: "MEU-3"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-18-p1-domain-foundation/implementation-plan.md"
build_plan_section: "bp01s1.3"
agent: "cursor-grok-4.6"
reviewer: "pending-codex"
predecessor: "2026-08-18-p1-domain-foundation-MEU-2-handoff.md"
---

# Handoff: 2026-08-18-p1-domain-foundation-MEU-3-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-3 — persistable entities, `DOWNLOAD_TRANSITIONS`, `reset_failed`
**Build Plan Section**: `docs/build-plan/01-domain-layer.md` persistable entities
**Predecessor**: MEU-2

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-3.1 | unit | `DownloadJob` exact persistable fields; UUID; no `parent_id` | Spec | `test_ac_3_1_download_job_persistable_fields` | ✅ |
| AC-3.2 | unit | `DownloadJob.status` cannot be `Paused` | Spec | `test_ac_3_2_download_job_status_cannot_be_paused` | ✅ |
| AC-3.3 | unit | `DOWNLOAD_TRANSITIONS` via `transition`; illegal edge `ConflictError` | Spec | `test_ac_3_3_download_transitions` | ✅ |
| AC-3.4 | unit | `reset_failed` clears error + progress | Spec | `test_ac_3_4_reset_failed_clears_error_and_progress` | ✅ |
| AC-3.5 | unit | `DownloadArchiveEntry` keys non-empty | Spec | `test_ac_3_5_download_archive_entry_keys` | ✅ |
| AC-3.6 | unit | `TranscriptJob` has no `video_ids` / `processed_ids` / progress | Spec | `test_ac_3_6_transcript_job_has_no_dropped_fields` | ✅ |
| AC-3.7 | unit | `TranscriptJob.status` may be `Paused` | Spec | `test_ac_3_7_transcript_job_may_be_paused` | ✅ |
| AC-3.8 | unit | `TranscriptItem` Done requires path | Spec | `test_ac_3_8_transcript_item_done_requires_path` | ✅ |
| AC-3.9 | unit | `TTSJob` speed/format/preview/File-path; no full-text field | Spec | `test_ac_3_9_tts_job_invariants` | ✅ |
| AC-3.10 | unit | `ModelVariant` has no `is_loaded` / `device` | Spec | `test_ac_3_10_model_variant_has_no_runtime_columns` | ✅ |
| AC-3.11 | unit | `Setting` namespace + leaf key | Spec | `test_ac_3_11_setting_namespace_and_leaf_key` | ✅ |
| AC-3.12 | unit | Forbidden persistable types absent | Spec | `test_ac_3_12_forbidden_persistable_types_absent` | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| `test_ac_3_1_download_job_persistable_fields` | `ImportError: cannot import name 'DownloadJob'` | passed | `tests/unit/test_domain.py` |

Receipt: `C:/Temp/av-kit/fail-to-pass-meu-3.txt`.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `uv run pytest tests/unit/test_domain.py -x --tb=short -v` | 0 | 42 passed |

### Quality Gate Results

```
pyright: 0 errors, 0 warnings
ruff: 0 violations
pytest: 42 passed
anti-placeholder: 0 matches
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/download.py` | modified | entities | `DownloadJob`, `DownloadArchiveEntry`, `DOWNLOAD_TRANSITIONS` |
| `packages/core/src/avkit_core/domain/transcript.py` | modified | entities | `TranscriptJob`, `TranscriptItem` |
| `packages/core/src/avkit_core/domain/tts.py` | modified | entities | `TTSJob`, `ModelVariant` |
| `packages/core/src/avkit_core/domain/settings.py` | modified | entities | `Setting`, `SETTING_NAMESPACES` |

```diff
+def reset_failed(self) -> DownloadJob:
+    if self.status is not DownloadStatus.Failed:
+        raise ConflictError("reset_failed is only valid from Failed")
```

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

`pending` — implementer does not author the verdict

---

## Deferred Items

None.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-19 | cursor-grok-4.6 | MEU-3 entity handoff |
