---
date: "2026-08-26"
project: "p9-capture-engine"
meu: "MEU-34"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md"
build_plan_section: "bp09s-domain"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-26-p8-conversion-gui-MEU-33-handoff.md"
---

# Handoff: 2026-08-26-p9-capture-engine-MEU-34-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-34 — Capture domain: `CaptureSource` / `CaptureRequestStatus` / `AnnotationType` (+ `to_wire()`), `CaptureShot`, `CaptureRequest`, annotation VOs, `BBox`, `ImageProbe`, ports, errors. `SETTING_NAMESPACES` += `capture`. `QUEUE_NAMES` still excludes `captures`. No tables, mss, or Pillow.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Domain
**Predecessor**: MEU-33 conversion GUI

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-34.1 | unit | StrEnums match named-set members; persist `.name`; `AnnotationType.to_wire()` = `ANNOTATION_WIRE`; `ENUM_MEMBERS` includes the three | Spec 202–208 | `test_domain_capture.py` AC-34.1 | ✅ |
| AC-34.2 | unit | `QUEUE_NAMES` excludes `captures`; `QueueRuntime` rejects it | Spec 200 | `test_domain_capture.py` AC-34.2 | ✅ |
| AC-34.3 | unit | `SETTING_NAMESPACES` includes `capture`; unknown ns still `ValidationError` | Spec 419 | `test_domain_capture.py` AC-34.3 | ✅ |
| AC-34.4 | unit | `CaptureShot` fields, frozen, extra `TypeError`, relative path / negative size `ValidationError` | Spec 212–226 | `test_domain_capture.py` AC-34.4 | ✅ |
| AC-34.5 | unit | `CaptureRequest` fields; `shot_id` optional until Completed; extra `TypeError` | Spec 236–246 | `test_domain_capture.py` AC-34.5 | ✅ |
| AC-34.6 | unit | `CAPTURE_REQUEST_TRANSITIONS` exhaustive; Pending → Completed/Cancelled/Expired | Spec 248–255 | `test_domain_capture.py` AC-34.6 | ✅ |
| AC-34.7 | unit | Annotation VOs reject unknown color, empty/overlong text, negative rect, extra field | Spec 259–274, 307 | `test_domain_capture.py` AC-34.7 | ✅ |
| AC-34.8 | unit | `BBox` width/height `< CAPTURE_MIN_EDGE_PX` → `ValidationError` | Spec 334, 409 | `test_domain_capture.py` AC-34.8 | ✅ |
| AC-34.9 | unit | `ImageProbe` fields; extra/missing kwargs `TypeError` | Spec 293 | `test_domain_capture.py` AC-34.9 | ✅ |
| AC-34.10 | unit | `ScreenCapturePort` / `ImageAnnotatePort` signatures; no mss in core | Spec 276–295 | `test_domain_capture.py` AC-34.10 | ✅ |
| AC-34.11 | unit | Five capture errors exist; `HotkeyConflictError` absent | Spec 299–310 | `test_domain_capture.py` AC-34.11 | ✅ |
| AC-34.12 | unit | `INFRA_NAMES` includes `PIL`/`mss`; core has zero imports of those | Local Canon AC-5.16; Spec 340 | `test_domain_capture.py` AC-34.12 | ✅ |
| AC-34.13 | unit | Highlight opacity inclusive [0,1]; `opacity=2` → `AnnotationValidationError` | Spec 269 | `test_domain_capture.py` AC-34.13 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-34.1–34.13 | `PASS: RED_ORACLE py MEU-34 AC-34 count=13` (`ModuleNotFoundError` / missing enums / missing `capture.py`) | 13 capture + domain suite green | `C:/Temp/av-kit/fail-to-pass-meu-34-py.txt`; `C:/Temp/av-kit/pytest-meu-34-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-api-tree-hash.ps1 -Mode write` | 0 | `PASS: API_BASELINE written` (`C:/Temp/av-kit/p9-engine-api-baseline-write.txt`) |
| `assert-red-oracle.ps1 -Kind py -Meu 34` | 0 | `PASS: RED_ORACLE py MEU-34 AC-34 count=13` |
| `uv run pytest tests/unit/test_domain_capture.py tests/unit/test_domain.py` | 0 | 60 passed |
| `assert-meu-scoped-gate.ps1 -Meu 34` | 0 | `PASS: MEU_SCOPED_GATE quality MEU-34` |

### Quality Gate Results

```
pytest: 60 passed (C:/Temp/av-kit/pytest-meu-34-gate.txt)
pyright: 0 errors, 0 warnings (C:/Temp/av-kit/pyright-meu-34.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-34.txt)
anti-placeholder: PASS: ANTI_PLACEHOLDER MEU-34
G36 skip/xfail: 0
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/capture.py` | new | 1– | Shot, request, annotation VOs, BBox, ImageProbe, transitions |
| `packages/core/src/avkit_core/ports/capture.py` | new | 1– | `ScreenCapturePort`, `ImageAnnotatePort` |
| `packages/core/src/avkit_core/domain/enums.py` | modified | Capture enums | `CaptureSource`, `CaptureRequestStatus`, `AnnotationType.to_wire()` |
| `packages/core/src/avkit_core/domain/errors.py` | modified | capture errors | Five types; no `HotkeyConflictError` |
| `packages/core/src/avkit_core/domain/settings.py` | modified | SETTING_NAMESPACES | `capture` |
| `tests/unit/test_domain_capture.py` | new | AC-34.1–34.13 | Red-first capture domain tests |
| `tests/unit/test_domain.py` | modified | expected sets | ENUM_MEMBERS, SETTING_NAMESPACES, INFRA_NAMES, LAYOUT, error names |

```diff
+class CaptureSource(StrEnum):
+    Hotkey = "Hotkey"
+    Gui = "Gui"
+    McpFullscreen = "McpFullscreen"
+    McpRegion = "McpRegion"
+    McpInteractive = "McpInteractive"
+    Scan = "Scan"
```

```diff
+class ScreenCapturePort(Protocol):
+    def capture_fullscreen(self, output_path: Path) -> ImageProbe: ...
+    def capture_region(self, output_path: Path, bbox: BBox) -> ImageProbe: ...
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
| SQLite tables + mss/Pillow adapter | out-of-scope this MEU | MEU-35 | Session 16 |
| `CaptureService` + `CAPTURE_KEYS` | out-of-scope this MEU | MEU-36 | Session 16 |
| REST `/captures` | out-of-scope | MEU-37 | Session 17 |
| MCP `avkit_capture` | out-of-scope | MEU-38 | Session 17 |
| GUI/tray/F2/overlay | out-of-scope | MEU-39 | Session 18 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-26 | cursor-grok | MEU-34 TDD complete |
| Submitted for review | 2026-08-26 | cursor-grok | Awaits project execution review after MEU-35–36 |
| Exec r1 F3 | 2026-08-27 | cursor-grok | Completed CaptureRequest requires shot_id |
