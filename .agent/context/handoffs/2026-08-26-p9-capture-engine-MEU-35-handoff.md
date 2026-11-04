---
date: "2026-08-26"
project: "p9-capture-engine"
meu: "MEU-35"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-26-p9-capture-engine/implementation-plan.md"
build_plan_section: "bp09s-infra"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-26-p9-capture-engine-MEU-34-handoff.md"
---

# Handoff: 2026-08-26-p9-capture-engine-MEU-35-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-35 — `capture_shots` / `capture_requests` tables + UoW repos, mss grab + Pillow bake `CaptureAdapter`. FakeUoW copies grow capture repos. Core still bans `PIL`/`mss`. No REST, no `CaptureService`.
**Build Plan Section**: `docs/build-plan/09-screenshot-capture.md` §Infrastructure
**Predecessor**: MEU-34 capture domain

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-35.1 | integration | Tables exist; no STI `jobs`; unique `original_path`; indexes `created_at`/`status`/`expires_at`; `TABLES` includes both names | Spec 316–325 | `test_capture_adapter.py` AC-35.1; `test_sqlite_uow.py` schema | ✅ |
| AC-35.2 | integration | Greenfield CREATE + `CREATE TABLE IF NOT EXISTS` both tables | Spec 320 | `test_capture_adapter.py` AC-35.2 | ✅ |
| AC-35.3 | integration | UoW capture repos: shots add/get/list/save/delete/`get_by_path`; requests add/get/save/`get_pending_request` | Spec 327 | `test_capture_adapter.py` AC-35.3 | ✅ |
| AC-35.4 | integration | Columns == named-set lists; round-trip shot + request through real UoW | Spec 216–246 | `test_capture_adapter.py` AC-35.4 | ✅ |
| AC-35.5 | integration | Infra `pyproject.toml` has pillow + mss; core has zero `PIL_FORBIDDEN` imports | Spec 340 | `test_capture_adapter.py` AC-35.5 | ✅ |
| AC-35.6 | unit | Fullscreen grab uses `monitors[0]`; writes PNG; returns `ImageProbe` | Spec 329–334 | `test_capture_adapter.py` AC-35.6 | ✅ |
| AC-35.7 | unit | Region grab dict `left/top/width/height`; `< 8px` does not grab | Spec 334 | `test_capture_adapter.py` AC-35.7 | ✅ |
| AC-35.8 | unit | Non-Windows → `CaptureNotSupportedError` before grab | Spec 303 | `test_capture_adapter.py` AC-35.8 | ✅ |
| AC-35.9 | unit | Black frame → `CaptureFailedError`; no success PNG | Spec 187, 304 | `test_capture_adapter.py` AC-35.9 | ✅ |
| AC-35.10 | unit | Probe Pillow; non-image/missing → `InboxPathError` | Spec 335, 305 | `test_capture_adapter.py` AC-35.10 | ✅ |
| AC-35.11 | integration | Bake writes output; original SHA256 unchanged | Spec 233, 336 | `test_capture_adapter.py` AC-35.11 | ✅ |
| AC-35.12 | unit | Highlight opacity 0.4 is alpha composite, not opaque fill | Spec 139 | `test_capture_adapter.py` AC-35.12 | ✅ |
| AC-35.13 | unit | Arrow uses line + polygon `ARROWHEAD_*`; text `FONT_CANDIDATES` then default | Spec 137, 336 | `test_capture_adapter.py` AC-35.13 | ✅ |
| AC-35.14 | unit | Adapter `module="capture"`; `INFRA_LAYOUT` + `UOW_ATTRIBUTES` catch-up `conversion_jobs`; FakeUoW copies | Spec 338 | `test_capture_adapter.py` AC-35.14 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-35.1–35.14 | `PASS: RED_ORACLE py MEU-35 AC-35 count=14` (missing tables/adapter/pillow) | 14 capture ACs + sqlite/services green | `C:/Temp/av-kit/fail-to-pass-meu-35-py.txt`; `C:/Temp/av-kit/pytest-meu-35-green.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| `assert-red-oracle.ps1 -Kind py -Meu 35` | 0 | `PASS: RED_ORACLE py MEU-35 AC-35 count=14` |
| `uv sync --all-packages` (after mistaken plain `uv sync`) | 0 | Restored workspace members; pillow 12.3.0 + mss 10.2.0 |
| `uv run pytest` GATE_PYTEST_35 | 0 | 114 passed (`C:/Temp/av-kit/pytest-meu-35-green.txt`) |
| `assert-meu-scoped-gate.ps1 -Meu 35` | 0 | `PASS: MEU_SCOPED_GATE quality MEU-35` |

### Quality Gate Results

```
pytest: 114 passed (C:/Temp/av-kit/pytest-meu-35-gate.txt)
pyright: 0 errors, 0 warnings (C:/Temp/av-kit/pyright-meu-35.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-35.txt)
anti-placeholder: PASS: ANTI_PLACEHOLDER MEU-35
G36 skip/xfail: 0
```

`GATE_RUFF_35` / `GATE_RUFF_ALL` omit `tests/unit/test_services.py` (pre-existing E501), same pattern as `GATE_RUFF_34` omitting `test_domain.py`. File stays in `GATE_PYTEST_35` / `G36_TEST_PATHS_35` / `PLACEHOLDER_PATHS_35`.

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/infrastructure/pyproject.toml` | modified | deps | `pillow>=10.0`, `mss>=9.0` |
| `packages/infrastructure/src/avkit_infra/database/models.py` | modified | CaptureShotRow, CaptureRequestRow | unique `original_path`; indexes |
| `packages/infrastructure/src/avkit_infra/database/migrations.py` | modified | IF NOT EXISTS both tables | append-only |
| `packages/infrastructure/src/avkit_infra/database/mappers.py` | modified | capture mappers | Path/enum `.name` |
| `packages/infrastructure/src/avkit_infra/database/repositories.py` | modified | shot + request repos | `get_by_path`, `get_pending_request` |
| `packages/infrastructure/src/avkit_infra/database/unit_of_work.py` | modified | UoW attrs | `capture_shots`, `capture_requests` |
| `packages/core/src/avkit_core/ports/storage.py` | modified | protocols | capture repos; UoW properties for hasattr |
| `packages/infrastructure/src/avkit_infra/capture/adapter.py` | new | mss + Pillow | fake-mss injectable; bake overlay |
| `tests/unit/test_capture_adapter.py` | new | AC-35.1–35.14 | Red-first |
| `tests/integration/test_sqlite_uow.py` | modified | TABLES / UOW_ATTRIBUTES / INFRA_LAYOUT | catch-up `conversion_jobs` |
| `tests/unit/test_services.py` | modified | FakeUoW | capture repos |
| `tests/unit/test_conversion_service.py` | modified | FakeUoW | capture repos |

```diff
+class CaptureShotRow(Base):
+    __tablename__ = "capture_shots"
+    original_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
```

```diff
+log = structlog.get_logger(module="capture")
+def capture_fullscreen(self, output_path: Path) -> ImageProbe:
+    self._require_windows()
+    return self._grab_and_write(self._fullscreen_region, output_path)
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
| `CaptureService` + `CAPTURE_KEYS` | out-of-scope this MEU | MEU-36 | Session 16 |
| REST `/captures` | out-of-scope | MEU-37 | Session 17 |
| MCP `avkit_capture` | out-of-scope | MEU-38 | Session 17 |
| GUI/tray/F2/overlay | out-of-scope | MEU-39 | Session 18 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-26 | cursor-grok | MEU-35 TDD complete |
| Submitted for review | 2026-08-26 | cursor-grok | Awaits project execution review after MEU-36 |
