---
date: "2026-08-24"
project: "p8-conversion-engine"
meu: "MEU-28"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-24-p8-conversion-engine/implementation-plan.md"
build_plan_section: "bp08s1"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-24-p7-distribution-MEU-25-handoff.md"
---

# Handoff: 2026-08-24-p8-conversion-engine-MEU-28-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-28 — Conversion domain: enums, `ConversionJob`, built-in presets, `GPUCapabilities` session VO, additive `MediaPort` (`detect_gpu`/`encode`/`cut`/`extract_stream` with `on_progress` + `should_stop`), `MediaInfo` optional fields, `QUEUE_NAMES` += `conversions`, `SETTING_NAMESPACES` += `converter`, `UNIT_LABELS` += `frames`, new domain errors. No FFmpeg encode. No REST/MCP/GUI. `ConversionJob` is not a `avkit_core.domain` package attribute (AC-3.12).
**Build Plan Section**: `docs/build-plan/08-video-conversion.md` §Domain
**Predecessor**: MEU-25 NSIS installer (Phase 7)

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-28.1 | unit | StrEnums `ConversionKind`, `ConversionStatus`, `ConversionPresetId`, `CutCopyMode`, `AudioEncodeMode`, `GpuPreference` persist `.name` | Spec 224–233 | `test_domain_conversion.py` AC-28.1 | ✅ |
| AC-28.2 | unit | `ConversionStatus` has no `Paused`; job status `"Paused"` raises | Spec 285–286 | `test_domain_conversion.py` AC-28.2 | ✅ |
| AC-28.3 | unit | Compress job with `in_ms` or `out_ms` raises `ValidationError` | Spec 290 | `test_domain_conversion.py` AC-28.3 | ✅ |
| AC-28.4 | unit | Cut `out_ms <= in_ms` or negative raises `InvalidTimeRangeError` | Spec 359 | `test_domain_conversion.py` AC-28.4 | ✅ |
| AC-28.5 | unit | `reset_failed` only from `Failed`; clears error and progress | Spec 286, 294–301 | `test_domain_conversion.py` AC-28.5 | ✅ |
| AC-28.6 | unit | `CONVERSION_TRANSITIONS` keys exhaustive over `ConversionStatus` | Spec state machine; Local Canon | `test_domain_conversion.py` AC-28.6 | ✅ |
| AC-28.7 | unit | `MediaPort` KEEP+ADDITIVE; encode/cut/extract require `on_progress` and `should_stop` | Spec 316–348; Local Canon | `test_domain_conversion.py` AC-28.7 | ✅ |
| AC-28.8 | unit | `MediaInfo` additive fields default `None`; extra `codec=` is `TypeError` | Spec 308–309 | `test_domain_conversion.py` AC-28.8 | ✅ |
| AC-28.9 | unit | `QUEUE_NAMES` includes `conversions`; `UNIT_LABELS` includes `frames` | Spec 366, 388 | `test_domain_conversion.py` AC-28.9 | ✅ |
| AC-28.10 | unit | `SETTING_NAMESPACES` includes `converter` | Spec 479–487 | `test_domain_conversion.py` AC-28.10 | ✅ |
| AC-28.11 | unit | Five frozen builtin presets; default id Balanced | Spec 134–144, 314 | `test_domain_conversion.py` AC-28.11 | ✅ |
| AC-28.12 | unit | `CONVERT_OPTIONS_FIELDS` re-exported unchanged | Spec 312, 291 | `test_domain_conversion.py` AC-28.12 | ✅ |
| AC-28.13 | unit | New errors exist; reuse `FFmpegNotFoundError` | Spec 352–360 | `test_domain_conversion.py` AC-28.13 | ✅ |
| AC-28.14 | unit | `GPUCapabilities` session VO; no `__tablename__` | Spec 235–250 | `test_domain_conversion.py` AC-28.14 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-28.1–28.14 | `PASS: RED_ORACLE py MEU-28 AC-28 count=14` | 14 conversion + domain suite green | `C:/Temp/av-kit/fail-to-pass-meu-28-py.txt`; `pytest-meu-28-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind py -Meu 28` | 0 | `PASS: RED_ORACLE py MEU-28 AC-28 count=14` |
| `uv run pytest tests/unit/test_domain_conversion.py tests/unit/test_domain.py -x --tb=short -v` | 0 | 61 passed |
| `uv run ruff check` (domain + media.py + conversion tests) | 0 | All checks passed |
| `uv run pyright packages/core` | 0 | 0 errors, 0 warnings |

### Quality Gate Results

```
pytest: 61 passed (C:/Temp/av-kit/pytest-meu-28-green.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-28.txt)
pyright: 0 errors, 0 warnings (C:/Temp/av-kit/pyright-meu-28.txt)
anti-placeholder: 0 matches in conversion.py / media.py
G36 skip/only: 0 matches
RED_ORACLE py MEU-28: PASS (count=14)
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/conversion.py` | new | 1–310 | Job, presets, GPU VO, encode DTOs, `CONVERT_OPTIONS_FIELDS` re-export |
| `packages/core/src/avkit_core/domain/enums.py` | modified | 154–206 | Conversion/cut/audio/GPU enums |
| `packages/core/src/avkit_core/domain/errors.py` | modified | 68–80, 218–222 | Four new `DomainError` types in `DOMAIN_ERROR_TYPES` |
| `packages/core/src/avkit_core/domain/progress.py` | modified | UNIT_LABELS + MediaInfo | `frames`; optional probe fields default `None` |
| `packages/core/src/avkit_core/domain/queue.py` | modified | QUEUE_NAMES | `conversions` |
| `packages/core/src/avkit_core/domain/settings.py` | modified | SETTING_NAMESPACES | `converter` |
| `packages/core/src/avkit_core/ports/media.py` | modified | 1–55 | Additive Protocol methods + `should_stop` |
| `tests/unit/test_domain_conversion.py` | new | 1–348 | AC-28.1–28.14 |
| `tests/unit/test_domain.py` | modified | expected sets | MEDIA_PORT_METHODS, QUEUE_NAMES, SETTING_NAMESPACES, MediaInfo fields, errors |

```diff
+class ConversionKind(StrEnum):
+    Compress = "Compress"
+    Cut = "Cut"
+    Extract = "Extract"
```

```diff
+    def encode(
+        self,
+        input_path: Path,
+        output_path: Path,
+        options: VideoEncodeOptions,
+        on_progress: Callable[[ProgressSnapshot], None],
+        should_stop: Callable[[], bool],
+    ) -> None: ...
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
| — | — | pending independent review | — | — | open |

### Verdict

`pending` — implementer does not author the verdict

---

## Deferred Items

_Skipped. FFmpeg table/adapter encode is MEU-29. ConversionService is MEU-30._

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-24 | cursor-grok | MEU-28 Red→Green + handoff |
