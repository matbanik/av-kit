---
date: "2026-10-15"
project: "2026-10-14-backend-robustness"
meu: "MEU-78"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-backend-robustness/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch"
predecessor: "2026-10-14-backend-robustness-MEU-76-handoff"
---

# Handoff: 2026-10-14-backend-robustness-MEU-78-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-78 — `svc-ffmpeg-resolver`.
- `RESOLVER_ORDER`: `FFmpegAdapter` has no latch. `_probed`, `_ffmpeg` and `_gpu` are gone. Every call to `_resolve_ffmpeg()` takes the configured file, then the bundled file, then `shutil.which("ffmpeg")`. The configured path is either fixed (`configured_path`) or comes from the new `configured_source` callable. Passing both raises `ValueError`. `ffmpeg_binaries()` returns `FFmpegBinaries(ffmpeg, ffprobe)` (new frozen dataclass, `domain/conversion.py`), or `None`. It is on `MediaPort`. `detect_gpu()` keeps no cache, so every call probes the ffmpeg it resolves (A-8).
- `FFPROBE_RULE`: the ffprobe is the sibling `ffprobe(.exe)` of the resolved ffmpeg, else `shutil.which("ffprobe")`. When neither exists, `probe()` raises `FFmpegNotFoundError("ffprobe binary was not found")` before any subprocess runs.
- `LIVE_SOURCE`: `build_services` builds `media` before `youtube`. `configured_source` reads `downloader.ffmpeg_path` from the settings service on every call, so a PUT applies without a restart.
- `FFMPEG_LOCATION`: `YouTubeAdapter(ffmpeg_location=...)` receives a callable over `media.ffmpeg_binaries()`. Each `_base_opts` call re-reads it and sets `ffmpeg_location` to the resolved binary's directory. When the callable returns `None` the key is absent.
- `DEPS_FFMPEG`: `DependencyHealth` gains `ffmpeg_path` and `ffprobe_available`, which `HealthService` fills from `ffmpeg_binaries()`. The route drops `_ffmpeg_path`, so it no longer echoes the raw setting. `FfmpegDependencyOut` gains `ffprobe_available`, and `openapi.committed.json` was regenerated.
- `DEPS_CARD` / `DEPS_REFRESH`: Settings gains a `deps-ffprobe-row` FFprobe chip. `useSettingsPage` invalidates `QUERY_HEALTH_DEPENDENCIES` after a successful `downloader` PUT whose body carries `ffmpeg_path`.
- `TEST_AMENDMENTS`:
  - **TA-2:** `test_ac_8_6` expects two `which` lookups for two `is_available()` calls.
  - **TA-3 and TA-4:** `ffmpeg_binaries` is added to both `MEDIA_PORT_METHODS` lists.
  - **TA-11 (A-10):** `ffmpeg_binaries` is added to the `test_ac_28_7` `keep` tuple. Mat approved it under S2 at the gate, because the row-1 census missed the site.
  - Each edit carries `TA-n (Session 33, MEU-78)`.
- `FIXTURE_REPAIRS`:
  - **(c):** `FakeMedia.ffmpeg_binaries`.
  - **(d):** the `SimpleNamespace` dependency fakes gain `ffmpeg_path`/`ffprobe_available` (A-6).
  - **(g):** a sibling `ffprobe.exe` in `test_ac_8_10` and `test_ac_29_4` (A-5).
  - No assertion changed.

**Build Plan Section**: `docs/build-plan/03-service-layer.md` §FFmpeg resolution (residual) (03:485-496, registry 3.10)
**Predecessor**: MEU-76. Both MEUs edit `youtube/adapter.py`, `services/health.py` and `tests/integration/test_youtube_adapter.py`, in separate hunks: MEU-76 owns `_run_extract` and `CONSOLE_FIELDS`, and MEU-78 owns `_base_opts` and `dependencies()`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-78.1 | unit | `RESOLVER_ORDER`: a configured file beats the bundle and PATH. A missing configured path falls to the bundle, and with both missing it falls to PATH. With nothing found, `ffmpeg_binaries()` is `None` and `convert` raises `FFmpegNotFoundError` without running a subprocess. | Spec 03:491; 02:428 | `tests/unit/test_ffmpeg_resolver.py:59` `test_ac_78_1_configured_beats_bundle_then_path`, `:84` `…_nothing_found_neg` | ✅ |
| AC-78.2 | unit | No latch: a `configured_source` path is picked up once its file exists and dropped once it is removed, and the source is read on each call. A fixed `configured_path` never consults a source, and passing both arguments raises `ValueError`. | Spec 03:492 | `test_ffmpeg_resolver.py:101` `test_ac_78_2_configured_source_has_no_latch`, `:131` `…_fixed_path_and_both_arguments_neg` | ✅ |
| AC-78.3 | unit | `FFPROBE_RULE`: the sibling is preferred, then PATH. POSIX `ffmpeg`/`ffprobe` names also work. With no ffprobe, `ffprobe is None` and `probe()` raises `FFmpegNotFoundError` naming ffprobe, without running a subprocess. | Spec 03:493 | `test_ffmpeg_resolver.py:152` `test_ac_78_3_ffprobe_sibling_then_path`, `:177` `…_no_ffprobe_anywhere_neg` | ✅ |
| AC-78.4 | unit | `detect_gpu()` runs the binary resolved at each call. With an unchanged path, it probes `-encoders` on every call (A-8). | `RESOLVER_ORDER` | `test_ffmpeg_resolver.py:192` `test_ac_78_4_detect_gpu_runs_the_binary_resolved_at_each_call`, `:214` `…_unchanged_path_probes_every_call_neg` | ✅ |
| AC-78.5 | integration | `FFMPEG_LOCATION`: `_base_opts` sets `ffmpeg_location` to the callable path's directory and re-reads it on every call. A `None` result, or no callable, leaves the key absent. | Spec 03:491 | `tests/integration/test_youtube_adapter.py:740` `test_ac_78_5_base_opts_ffmpeg_location_rereads_the_callable`, `:766` `…_no_location_leaves_the_key_absent_neg` | ✅ |
| AC-78.6 | integration | After `settings.set("downloader", "ffmpeg_path", …)`, `dependencies().ffmpeg_path` and the wired `ffmpeg_location()` both name the new file, with no rebuild. Clearing the setting falls back to PATH. | Spec 03:491-492 | `tests/integration/test_api_wiring.py:91` `test_ac_78_6_ffmpeg_setting_applies_without_rebuild`, `:110` `…_cleared_setting_falls_back_neg` | ✅ |
| AC-78.7 | contract | `GET /api/v1/health/dependencies` reports the resolved `ffmpeg.path` and `ffprobe_available` (True with a sibling, False without). When the setting points at a missing file, it reports the PATH binary, not the raw setting. | Spec 03:493 | `tests/e2e/test_api_ffmpeg_resolution.py:65` `test_ac_78_7_dependencies_report_resolved_ffmpeg_and_ffprobe`, `:85` `…_missing_setting_reports_the_path_binary_neg` | ✅ |
| AC-78.8 | unit | An `ffmpeg_path` PUT invalidates the dependencies query once, after the PUT. A quality PUT, a `ui` PUT and a failed PUT do not invalidate it. | Spec 03:492 | `ui/tests/unit/settings-deps-refresh.test.ts:59`, `:72` `AC-78.8 [neg] …` | ✅ |
| AC-78.9 | e2e | `deps-ffprobe-row` shows `available`. A Browse-driven `ffmpeg_path` PUT (A-9) adds exactly one dependencies GET, and a theme PUT adds none. | Spec 03:492-493 | `ui/tests/e2e/settings.test.ts:605` `AC-78.9 FFprobe row, …` | ✅ |

### Other plan AC references (not owned by MEU-78)

| AC | Owner | Status in MEU-78 |
|----|-------|------------------|
| AC-76.x | MEU-76 handoff | ✅ gate76; still green in gate78 |
| AC-77.x | MEU-77 handoff | ⏳ rows 8–11 |
| AC-8.6, AC-28.7, AC-4.x port lists | existing suites | pass with TA-2, TA-3, TA-4 and TA-11 applied, and no other assertion changed |
| AC-8.10, AC-29.4 | existing suites | pass with repair (g) (sibling fake `ffprobe.exe`) |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (snippet) | Green Output | File:Line |
|------|----------------------|--------------|-----------|
| pytest AC-78.1 to AC-78.4 (all 8) | `AssertionError: avkit_core.domain.conversion.FFmpegBinaries is missing` (`_require_resolver` presence assertion) | pass | `test_ffmpeg_resolver.py:59,84,101,131,152,177,192,214` |
| pytest AC-78.5, AC-78.6 (all 4) | `AssertionError: YouTubeAdapter(ffmpeg_location=...) is missing` | pass | `test_youtube_adapter.py:740,766`; `test_api_wiring.py:91,110` |
| pytest AC-78.7 (both) | `AssertionError: ffmpeg.ffprobe_available is missing assert 'ffprobe_available' in {'version': …, 'available': …, 'path': …}` | pass | `test_api_ffmpeg_resolution.py:65,85` |
| Vitest AC-78.8 | `AssertionError: expected [] to have a length of 1 but got +0` | pass | `settings-deps-refresh.test.ts:59` |
| Electron AC-78.9 | `expect(locator).toBeVisible() failed  Locator: getByTestId('deps-ffprobe-row') … element(s) not found` | pass (5 of 5 under `--repeat-each=5`) | `settings.test.ts:605` |

The Vitest `[neg]` passed at Red, since it needs no new symbol. Before any test ran, red-guard confirmed the 11 MEU-78 product files were unchanged against the `gate76` snapshot.

### Commands Executed

```json
{"schema_version": "evidence.v1", "check_id": "s33-row5-red78", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check red78", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 5: MEU-78 Red over AC-78.1-78.9 (pytest, ui Vitest, Electron); red-guard first", "phase": "red", "exit_code": 0, "result": "pass", "tested_state": "MEU-76 tree plus MEU-78 test edits only; red-guard: 11 MEU-78 product files unchanged vs the gate76 snapshot", "output": "pytest failed 14, passed 21 | vitest failed 1, passed 1 | electron failed 1 | PASS red78 (RED_RULE)", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row6-green78", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check green78", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 6: MEU-78 Green over AC-78.1-78.9 plus TA-2/3/4 and fixture repairs (c), (d), (g) (pytest MEU-78 files with test_domain.py and test_filesystem_media.py, ui Vitest, Electron E2E AC-78.9, openapi --check)", "phase": "green", "exit_code": 0, "result": "pass", "tested_state": "HEAD ddd11171ceb3ce307a6a735a5b77094b7d456d39 plus MEU-76 diff plus MEU-78 test and product edits, TA-2/3/4 and repairs (c), (d), (g)", "output": "PASS green pytest MEU-78: passed 98 | PASS green vitest MEU-78: passed 2 | PASS green electron MEU-78: passed 1 | green78-openapi exit 0 | PASS green78", "fresh": true}
```

```json
{"schema_version": "evidence.v1", "check_id": "s33-row7-gate78", "command": "pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check gate78", "cwd": "P:/av-kit-wt/backend-robustness", "scope": "row 7: MEU-78 targeted gate (pyright, ruff, ui typecheck and lint, mcp typecheck, openapi --check, pytest tests/, ui Vitest, MCP Vitest, source audit, Electron settings.test.ts --repeat-each=5, product snapshot)", "phase": "targeted", "exit_code": 0, "result": "pass", "tested_state": "MEU-78 final working tree (baseline ddd1117 + MEU-76 diff + MEU-78 diff + TA-1 to TA-4 and TA-11 + repairs (c), (d), (g))", "output": "py-types, py-lint, ui-types, ui-lint, mcp-types, openapi exit 0 | PASS suite pytest: passed 682 | PASS suite vitest: passed 804 | PASS suite mcp: passed 413 | source-audit rg exit 1 (no hits) | PASS suite electron: passed 65 | PASS snapshot of 25 product files | PASS gate78", "fresh": true}
```

The first `gate78` run failed one step: pytest `test_ac_28_7_mediaport_additive_requires_cancel_hook`, whose ordered `MediaPort` method tuple lacked `ffmpeg_binaries`. This was S2. No test was edited until Mat chose TA-11 (walkthrough A-10). The rerun above is the gate of record. The authoritative full gate is `WINDOWS_GATE` (H1-3).

Final evidence on the whole Session 33 tree (walkthrough §Audit, §Windows gate), rerun after the R1 F1 correction and the A-14 plan rewording: the H1-2 MCP audit of record (`s33-h1-2-audit-r3`) passed 99/99 with `tts.cancel` FIXED and every other action unchanged, `AUDIT_FINGERPRINT` 49d577f4bc8c5ea65e22676d96e83050ef41bd5e37f1c7d28efec93f59a56ce7. H1-3 `WINDOWS_GATE` (`s33-h1-3-windows-gate-r2`) passed 17/17 stages: pytest 724/0, Vitest 804/804, Electron 139/0/0/0, MCP 423/423, source audit 0 hits, `GATE_FINGERPRINT` 300cc234644b17997d1e6e7f2c3a7e6ffc3d0a41bb37b9e6252db41799b26f80 before and after. H1-4 `gate-check` (`s33-h1-4-gate-check-r2`) passed. The earlier `s33-h1-2-audit-final` and `s33-h1-3-windows-gate` runs are superseded.

### Quality Gate Results

```
pyright packages/: 0 errors
ruff check packages/ tests/: All checks passed!
ui typecheck / lint, mcp typecheck: exit 0
openapi --check: exit 0 (FfmpegDependencyOut.ffprobe_available only; OPENAPI_DIFF)
pytest tests/: 682 passed
ui Vitest: 804 passed
MCP Vitest: 413 passed
Electron settings.test.ts --repeat-each=5: 65 passed (13 tests x 5)
source audit over the MEU-78 files: 0 hits
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/conversion.py` | modified | +8 | `FFmpegBinaries` |
| `packages/core/src/avkit_core/ports/media.py` | modified | +3 | `ffmpeg_binaries()` |
| `packages/infrastructure/src/avkit_infra/media/adapter.py` | modified | +40/−16 | `configured_source`; latch-free `_resolve_ffmpeg`; `_resolve_ffprobe`; `ffmpeg_binaries`; `probe` ffprobe rule; no GPU cache |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | modified | +6 (MEU-78 hunks) | `ffmpeg_location` parameter; `_base_opts` sets `ffmpeg_location` |
| `packages/api/src/avkit_api/wiring.py` | modified | +6/−2 | media before youtube; `LIVE_SOURCE`; `ffmpeg_location` callable |
| `packages/core/src/avkit_core/domain/health.py` | modified | +2 | `ffmpeg_path`, `ffprobe_available` |
| `packages/core/src/avkit_core/services/health.py` | modified | +3 (MEU-78 hunk) | fill from `ffmpeg_binaries()` |
| `packages/api/src/avkit_api/routes/health.py` | modified | +4/−16 | drop `_ffmpeg_path` and the settings dependency |
| `packages/api/src/avkit_api/schemas/health.py` | modified | +2/−1 | `ffprobe_available` |
| `openapi.committed.json` | modified | +7/−2 | regenerated (`tools/export_openapi.py -o`) |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | +10/−1 | `deps-ffprobe-row` FFprobe chip |
| `ui/src/renderer/src/features/settings/useSettingsPage.ts` | modified | +5 | `DEPS_REFRESH` |
| `ui/tests/e2e/test-ids.ts` | modified (append only) | +3 | `DEPS_FFPROBE_ROW` |
| `tests/unit/test_ffmpeg_resolver.py` | new | 1–225 | AC-78.1–78.4 |
| `tests/integration/test_youtube_adapter.py` | modified (append only) | +48 | AC-78.5 |
| `tests/integration/test_api_wiring.py` | modified (imports + append) | +87 | AC-78.6 |
| `tests/e2e/test_api_ffmpeg_resolution.py` | new | 1–95 | AC-78.7 |
| `ui/tests/unit/settings-deps-refresh.test.ts` | new | 1–89 | AC-78.8 |
| `ui/tests/e2e/settings.test.ts` | modified (seam field + import + append) | +56/−1 | AC-78.9 |
| `tests/integration/test_filesystem_media.py` | modified | +4/−1 | TA-2, TA-4; repair (g) |
| `tests/unit/test_domain.py` | modified | +1 (MEU-78) | TA-3 |
| `tests/unit/test_domain_conversion.py` | modified | +7/−1 | TA-11 (A-10) |
| `tests/unit/test_ffmpeg_conversion.py` | modified | +2 | repair (g) |
| `tests/unit/test_services.py` | modified | +4 | repair (c) |
| `tests/e2e/test_api_health_settings.py`, `tests/e2e/test_api_auth.py` | modified | +3 each | repair (d) |

```diff
     def _resolve_ffmpeg(self) -> Path | None:
-        if self._probed:
-            return self._ffmpeg
-        self._probed = True
-        if self._configured_path is not None and self._configured_path.is_file():
-            self._ffmpeg = self._configured_path
-            return self._ffmpeg
+        """RESOLVER_ORDER, per call: the configured file, the bundled file, then PATH."""
+        configured = self._configured()
+        if configured is not None and configured.is_file():
+            return configured
```

```diff
+    # LIVE_SOURCE: the ffmpeg setting is read at each resolution, so a PUT needs no restart.
+    media = FFmpegAdapter(
+        configured_source=lambda: _ffmpeg_configured(settings.get("downloader", "ffmpeg_path")),
+        bundle_path=bundled_ffmpeg(),
+    )
     youtube = YouTubeAdapter(
 ...
+        ffmpeg_location=lambda: b.ffmpeg if (b := media.ffmpeg_binaries()) else None,
     )
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Deferred Items

None. The Spec 02:428 edit ("probe once; cache" → per-call resolution, D-16) is row 12, the hub.

---

## Decision Log

```yaml
decision_log:
  - id: A-8
    stage: execution
    question: "AC-78.4 names a gpu_capabilities() cache keyed by the ffmpeg path, which does not exist; what does it test?"
    resolution: human
    class: two-way
    chosen: "Retarget AC-78.4 to detect_gpu(); remove the dead self._gpu field; drop the cache clause from RESOLVER_ORDER"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-10-14-backend-robustness/walkthrough.md §Gate decisions A-8"]
    research: { engine: none, sources: [] }
    reasoning: "detect_gpu() already probes on every call and self._gpu was written but never read; the only GPU cache is ConversionService._gpu, outside PRODUCT_SCOPE. Inventing a cache would add behavior the plan did not scope."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'Retarget to detect_gpu (Recommended)'"
  - id: A-9
    stage: execution
    question: "The FFmpeg path input is readOnly; how does AC-78.9 write ffmpeg_path?"
    resolution: human
    class: two-way
    chosen: "Click browse-ffmpeg-btn, which flushes PUT /settings/downloader with ffmpeg_path"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-10-14-backend-robustness/walkthrough.md §Gate decisions A-9"]
    research: { engine: none, sources: [] }
    reasoning: "Browse is the only control that writes ffmpeg_path; making the input editable would change product UX outside scope. The DEPS_REFRESH proof is unchanged."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'Use Browse (Recommended)'"
  - id: A-10
    stage: execution
    question: "test_ac_28_7 pins MediaPort's public methods exactly; how is the new ffmpeg_binaries admitted?"
    resolution: human
    class: governance-value
    chosen: "TA-11: the keep tuple gains ffmpeg_binaries after ffmpeg_version; nothing else in the test changes"
    source_tag: Human-approved
    precedents: ["docs/execution/plans/2026-10-14-backend-robustness/walkthrough.md §Gate decisions A-10"]
    research: { engine: none, sources: [] }
    reasoning: "The census missed this third closed list; a sweep for ffmpeg_version, MediaPort.__dict__ and MEDIA_PORT_METHODS found no other site. An explicit TA keeps the test change visible to review instead of loosening the assertion."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'Add TA-11 (Recommended)'"
  - id: D-34
    stage: execution
    question: "Does configured_source read settings on every resolution, including download worker threads?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: SettingsService.get per call, one short unit of work, no state held across threads"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/wiring.py:151 — configured_source reads settings.get", "packages/infrastructure/src/avkit_infra/media/adapter.py:201 — nothing cached between calls"]
    research: { engine: none, sources: [] }
    reasoning: "RESOLVER_ORDER requires the live value; each call is a single-row read, so caching would only reintroduce the stale-path divergence this MEU removes."
  - id: D-35
    stage: execution
    question: "Is yt-dlp's ffmpeg_location set when ffmpeg was found on PATH?"
    resolution: autonomous
    class: two-way
    chosen: "Yes: always set it to the resolved directory"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/youtube/adapter.py:338 — _base_opts"]
    research: { engine: none, sources: [] }
    reasoning: "yt-dlp then gets the same directory it would have searched, the ffprobe sibling rule matches, and one code path serves both sources."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate78 |
| Corrected | 2026-10-16 | claude-code | Decision Log rewritten as the canonical `decision_log` YAML, one entry per former bullet (D-43); final evidence points at the A-14 reruns (`s33-h1-2-audit-r3`, `s33-h1-3-windows-gate-r2`) |
