---
date: "2026-08-26"
project: "p9-capture-engine"
meu: "MEU-36"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md"
build_plan_section: "bp09s-service"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-26-p9-capture-engine-MEU-35-handoff.md"
---

# Handoff: 2026-08-26-p9-capture-engine-MEU-36-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-36 — `CaptureService` (scan, register, grab, interactive request, annotate/bake, remove-deletes-files) + `CAPTURE_KEYS`. Coordinate clamp before bake. G29 tmp-SQLite. No REST/MCP/GUI. Service does not `mkdir`.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Service layer
**Predecessor**: MEU-35 tables + adapter

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-36.1 | integration | Scan only `SCAN_EXTENSIONS`, non-recursive; upsert `Scan` | Spec 350 | `test_capture_service.py` AC-36.1 | ✅ |
| AC-36.2 | integration | Scan deletes rows whose original vanished | Spec 232, 350 | `test_capture_service.py` AC-36.2 | ✅ |
| AC-36.3 | unit | `list_shots` scan first; newest `created_at` then filename | Spec 127, 351 | `test_capture_service.py` AC-36.3 | ✅ |
| AC-36.4 | unit | Register: relative/`..` → `InboxPathError`; same path+size idempotent | Spec 231, 353 | `test_capture_service.py` AC-36.4 | ✅ |
| AC-36.5 | unit | Timestamp local `TIMESTAMP_FORMAT`; collision `_2`/`_3`; MCP sources | Spec 354, 362 | `test_capture_service.py` AC-36.5 | ✅ |
| AC-36.6 | unit | Pending ttl `REQUEST_TTL_S`; second Pending → `CaptureRequestConflictError` | Spec 257, 355 | `test_capture_service.py` AC-36.6 | ✅ |
| AC-36.7 | unit | `expire_stale_requests` from list/get | Spec 254, 357 | `test_capture_service.py` AC-36.7 | ✅ |
| AC-36.8 | integration | complete registers path + Completed; cancel no shot | Spec 356 | `test_capture_service.py` AC-36.8 | ✅ |
| AC-36.9 | integration | Sidecar `SIDECAR_VERSION` + wire list; empty list clears files | Spec 261–274, 358 | `test_capture_service.py` AC-36.9 | ✅ |
| AC-36.10 | unit | `read_image` original/annotated; missing annotated/id → `NotFoundError` | Spec 359, 310 | `test_capture_service.py` AC-36.10 | ✅ |
| AC-36.11 | integration | `remove` deletes files then row | Spec 150, 360 | `test_capture_service.py` AC-36.11 | ✅ |
| AC-36.12 | unit | `SETTINGS_KEY_TABLE` `CAPTURE_KEYS`/`CAPTURE_DEFAULTS`; unknown leaf 422-class | Spec 421–426 | `test_capture_service.py` AC-36.12 | ✅ |
| AC-36.13 | integration | G29 tmp-SQLite register+list; download/tts/conversion sources isolated | Spec 234; G29 | `test_capture_service.py` AC-36.13 | ✅ |
| AC-36.14 | unit | Clamp integer coords to `[0, width]`/`[0, height]` before bake | Spec 274 | `test_capture_service.py` AC-36.14 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-36.1–36.14 | `PASS: RED_ORACLE py MEU-36 AC-36 count=14` (missing `CaptureService`) | 14 capture service ACs green | `C:/Temp/av-kit/fail-to-pass-meu-36-py.txt`; `C:/Temp/av-kit/pytest-meu-36-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind py -Meu 36` | 0 | `PASS: RED_ORACLE py MEU-36 AC-36 count=14` |
| Green pytest `GATE_PYTEST_36` | 0 | 96 passed (`C:/Temp/av-kit/pytest-meu-36-green.txt`) |
| `assert-meu-scoped-gate.ps1 -Meu 36` | 0 | `PASS: MEU_SCOPED_GATE quality MEU-36` |

### Quality Gate Results

```
pytest: 96 passed (C:/Temp/av-kit/pytest-meu-36-gate.txt)
pyright: 0 errors, 0 warnings (C:/Temp/av-kit/pyright-meu-36.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-36.txt)
anti-placeholder: PASS: ANTI_PLACEHOLDER MEU-36
G36 skip/xfail: 0
```

Existing `test_ac_12_8_no_direct_mkdir_in_services` forbids `Path.mkdir` in services (except `health.py`). Inbox creation stays with the caller / adapter.

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/services/capture.py` | new | CaptureService | scan/register/grab/request/annotate/remove |
| `packages/core/src/avkit_core/services/settings.py` | modified | SETTINGS_KEY_TABLE | `capture.*` keys |
| `tests/unit/test_capture_service.py` | new | AC-36.1–36.14 | Red-first |

```diff
+("capture", "inbox_dir"): SettingSpec("string", "~/Pictures/av-kit"),
+("capture", "hotkey"): SettingSpec("string", "F2"),
+("capture", "copy_to_clipboard"): SettingSpec("boolean", False),
+("capture", "close_to_tray"): SettingSpec("boolean", True),
```

```diff
+def annotate_and_save(self, shot_id: str, annotations: Sequence[Annotation]) -> CaptureShot:
+    clamped = [self._clamp_annotation(item, shot.width, shot.height) for item in annotations]
+    self._annotate.bake(shot.original_path, clamped, annotated_path)
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| 1 | | | | | |

### Verdict

`{approved | changes_required}` — pending independent execution review

---

## Deferred Items

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| REST `/captures` + OpenAPI + 15 MiB | out-of-scope | MEU-37 | Session 17 |
| MCP `avkit_capture` | out-of-scope | MEU-38 | Session 17 |
| GUI/tray/F2/overlay | out-of-scope | MEU-39 | Session 18 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-26 | cursor-grok | MEU-36 TDD complete |
| Submitted for review | 2026-08-26 | cursor-grok | Awaits project execution review |
| Exec r1 F1/F2/F4 | 2026-08-27 | cursor-grok | Skip `.annotated.png` on scan; atomic complete_request; real-SQLite bake→scan |
