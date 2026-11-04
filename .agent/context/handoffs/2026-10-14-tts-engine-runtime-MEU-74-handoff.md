---
date: "2026-10-15"
project: "tts-engine-runtime"
meu: "MEU-74"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md"
build_plan_section: "bp03"
agent: "claude-code (Claude Opus 5.5)"
reviewer: "Codex gpt-6.1-sol via local dispatch (tools/Invoke-CodexDispatch.ps1)"
predecessor: "2026-10-14-tts-engine-runtime-MEU-73-handoff.md"
---

# Handoff: 2026-10-14-tts-engine-runtime-MEU-74-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-74. Voices are honestly available: each one is listed with a reason when it cannot generate, and eSpeak NG is detected and called as a user-installed CLI.

- **Availability (`VOICE_REASON`, D-70):**
  - `voice_availability(lang_code, espeak_available)` returns a frozen `VoiceAvailability`:
    - a/b are always available;
    - e/f/h/i/p need eSpeak NG, otherwise `espeak_missing`;
    - j/z are never available (`language_unsupported`);
    - an unknown lang code raises `ValidationError`.
  - `VoiceConfig` keeps its five fields (D-89). `TTSService.list_voices` returns `(VoiceConfig, VoiceAvailability)` pairs and reads the eSpeak status once per call.
- **`VOICE_AVAILABLE_409`:**
  - `generate` raises `ConflictError("voice unavailable: <id> (<reason>)")`. The order is: model loaded → voice known → this 409 → the `required_tts_assets` 409 → the job row (`ASSET_409_ORDER`).
  - No job row is written after the 409, and the asset port is never called.
- **`EspeakCliAdapter` (`avkit_infra/tts/espeak.py`, new):**
  - **`ESPEAK_DETECT`:** looks on `PATH`, then under `%ProgramFiles%` and `%ProgramFiles(x86)%`, and probes `--version`. The version is cached per `(path, mtime_ns)`, and only successful probes are stored, so a fresh install or a fixed failure is seen on the next call.
  - **`ESPEAK_G2P`:** the argv is `[exe,"-q","--ipa","--tie=^","-v",<voice>,"--stdin"]`, and the text goes on stdin only. Punctuation is kept in order, `(en)` flags are stripped, and `«` `»` become `“` `”`. A nonzero exit, a timeout or a missing CLI raises `TtsRuntimeError` (a `DomainError`, D-97).
  - **`ESPEAK_MAP`:** `MULTI_E2M` (e/f/h/i/p), `EN_E2M` and the `ESPEAK_EN_FALLBACK` post-steps. They are pinned to the installed misaki tables by `ESPEAK_MAP_PARITY`.
  - **Licensing (D-71):** no GPL code is imported. An AST scan proves that `espeak.py` imports none of `misaki`, `phonemizer` or `espeakng_loader` (D-98).
- **Wire:**
  - API:
    - `VoiceOut` gains `available: bool` and `reason: "espeak_missing" | "language_unsupported" | null` on every row.
    - `DependenciesOut` gains `tts_espeak: EspeakOut {available, version, path}`.
    - `wiring.py` injects the real adapter into both services, and `openapi.committed.json` is regenerated.
  - MCP passes both routes through unchanged, because its strict schemas cover inputs only.
- **GUI:**
  - **`VoiceCombobox`:**
    - An unavailable voice stays listed and keyboard-reachable as an `aria-disabled` option. It shows its `voice-unavailable-reason` text, and click, Enter and Space do not select it.
    - An unavailable current selection shows its reason on a warning chip.
    - A row without the fields counts as available.
  - **Settings:**
    - `tts-espeak-row` reads "Detected" plus the version, or "Not installed".
    - When eSpeak NG is not installed, `tts-espeak-guidance` names the five languages and shows the releases URL as text, with a "Copy link" button (D-96).
    - An older backend without `tts_espeak` renders no row.
- **What MEU-74 does not do:** it makes Spanish, French, Hindi, Italian and Portuguese voices honestly *available*, but it does not make them *speak*. A Spanish WAV needs the MEU-72 G2P router (row 10), which calls `ESPEAK_G2P`.
- **Test amendments applied:**
  - the MEU-74 halves of TA-4 (`tts_espeak` in the three dependency fakes) and TA-5 (the `settings-page.test.ts` deps fixture);
  - TA-7 (fixture rows gain `available`/`reason`);
  - TA-9 (`ef_dora` replaces `jf_alpha`, with eSpeak NG reported present);
  - TA-14 (the AC-16.7 dict gains `available`/`reason`, D-95).
  - `ta-check` enforces all of them.

**Build Plan Section**: `docs/build-plan/03-*` §TTS language runtime ("Voice availability", "Detect"). Row 13 reconciles the hub.
**Predecessor**: MEU-73, which supplies `ASSET_409_ORDER`, `/health/dependencies` and the settle-refresh hook. MEU-72 builds on `ESPEAK_G2P` and on `ESPEAK_EN_FALLBACK`.

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-74.1 | unit | `voice_availability` follows `VOICE_REASON` over all 9 lang codes × 2 eSpeak states; a closed string enum; frozen; an unknown lang code raises `ValidationError` | Spec 03 "Voice availability"; D-70 | `tests/unit/test_tts_voice_availability.py:32`, `:40`, `:49`, `:59`, `:70` | ✅ |
| AC-74.2 | unit | `ESPEAK_DETECT`: on PATH; only under `%ProgramFiles%` / `(x86)`; nowhere → nulls; a failing `--version` → unavailable; cached per `(path, mtime_ns)`; a fresh install is seen; a failed probe is not latched | Spec 03 "Detect"; D-77 | `tests/unit/test_espeak_adapter.py:94`, `:107`, `:118`, `:133`, `:147`, `:161`, `:174`, `:185` | ✅ |
| AC-74.3 | integration | `GET /tts/voices` has `available`/`reason` on every row; espeak absent: `ef_dora` false/`espeak_missing`, `jf_alpha` false/`language_unsupported`, `af_heart` true/null; present: `ef_dora` true, `jf_alpha` still unavailable | Spec 03; Boundary Input Contract | `tests/e2e/test_api_tts_runtime.py:221`, `:237` | ✅ |
| AC-74.4 | integration | `generate ef_dora` with espeak absent → 409 `voice unavailable: ef_dora (espeak_missing)`; no job row; the fake asset port records no call; j/z → `language_unsupported` | Spec 03; `ASSET_409_ORDER` | `test_api_tts_runtime.py:256`, `:267` | ✅ |
| AC-74.5 | integration | `/health/dependencies` `tts_espeak` mirrors `ESPEAK_DETECT` (present → version and path; absent → nulls) | Spec 03 "Detect" | `test_api_tts_runtime.py:301`, `:310` | ✅ |
| AC-74.6 | unit | `ESPEAK_G2P` exact argv and stdin; punctuation; `(en)` stripped; curly quotes; nonzero exit or timeout → `TtsRuntimeError`; one sample per `MULTI_E2M` / `EN_E2M` rule; Spanish `e` stays; French keeps U+0303; `ESPEAK_EN_FALLBACK`; `ESPEAK_MAP_PARITY` with the installed misaki (D-98) | Spec 03; D-71 | `test_espeak_adapter.py:198`–`:414`, parity `:464` | ✅ |
| AC-74.7 | integration | Settings `tts-espeak-row`: "Detected" + version; "Not installed" + `tts-espeak-guidance` (five languages, the URL as text, "Copy link" → `writeClipboardText`, D-96); no row from an older backend | Spec 03; D-96 | `ui/tests/unit/settings-tts-runtime.test.ts:269`, `:280`, `:296` | ✅ |
| AC-74.8 | integration | `VoiceCombobox`: unavailable options are `aria-disabled="true"`; click and Enter select nothing; reason text; available voices unchanged; an unavailable selection's chip shows the reason | Spec 03 "Voice availability" | `ui/tests/unit/voice-combobox.test.tsx:216`, `:232`, `:241`, `:253`, `:263`, `:270` | ✅ |
| AC-74.9 | integration | Electron: the seam serves `jf_alpha` unavailable; its option is `aria-disabled="true"` with the reason visible | Spec 03; 06-gui | `ui/tests/e2e/tts-generate.test.ts:667` (plus `--repeat-each=20` in `gate74`) | ✅ |
| AC-74.10 | integration | `openapi.committed.json` regenerated; `export_openapi.py --check` passes | G8 | gate stage `openapi` in `gate74` | ✅ |
| AC-74.11 | integration | LOCAL-ESPEAK (optional, manual, after row 10): a real espeak-ng 1.52 install generates Spanish and French WAVs | D-71 | `walkthrough.md` §LOCAL-ESPEAK (row 12) | ⏭ deferred to row 12: the step needs row 10, and eSpeak NG is not installed on this machine |

### Other plan AC references (not owned by MEU-74)

| AC | Owner | Status in MEU-74 |
|----|-------|------------------|
| AC-73.x | MEU-73 handoff | pass. `PY73` is inside `gate74`. AC-73.16's fixture teardown now waits for the background spaCy download (walkthrough §Execution amendments, Row 8). |
| AC-72.x | MEU-72 handoff | pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`); AC-72.8 by `PACKAGE_SMOKE` |
| AC-9.x | existing `test_tts_models.py` (MEU-9) | untouched by MEU-74 (TA-1, TA-2 are MEU-73/72); pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`) |
| AC-23.20 | existing `gui-actions-audit.test.ts` (MEU-23) | pass in the H1-2 `WINDOWS_GATE` (attempt 2, identity `cd879e6e…`). D-100 (row 13) adds no gui-actions-index row, because this audit cannot resolve a `writeClipboardText` settings cell. |
| AC-16.7 | existing `test_api_tts_models.py` (MEU-16) | pass with TA-14 (D-95). The facade call count, the `lang_code` ban and the route source scans are unchanged. |
| AC-62.9 | existing `test_tts_assets.py` (MEU-62) | pass with TA-9. The 409 and 201 expectations are unchanged. |
| AC-2.x | existing `test_domain.py` (MEU-2) | untouched. `VoiceConfig` keeps five fields (D-89). |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| pytest AC-74.x (`PY74`, 109) | each one an import error on a declared symbol: `voice_availability`, `VoiceUnavailableReason`, `EspeakStatus`, `EspeakCliAdapter`, `avkit_infra.tts.espeak`, `MULTI_E2M`, `EN_E2M`, `ESPEAK_VOICE` | pass | see AC table |
| ui Vitest AC-74.7/74.8 (6 decisive) | `expect()` failures, for example a missing `tts-espeak-row` and a missing `aria-disabled` on options; 41 passing, including 3 regression guards that pass by design | pass, 47/47 | `voice-combobox.test.tsx`, `settings-tts-runtime.test.ts` |
| Electron AC-74.9 | `expect(option).toHaveAttribute('aria-disabled', 'true')`, received `null` | pass, 15/15 | `tts-generate.test.ts:667` |
| TA-14 `test_ac_16_7` | the route still built rows from bare `VoiceConfig`s (fails until row 6) | pass | `test_api_tts_models.py:156` |

Red, the TA dispositions and the Green design notes are in [walkthrough.md](../../../docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md) §MEU-74 Red, §MEU-74 Green and §MEU-74 GUI.

### Live probes (real adapter, no fakes; this machine has no eSpeak NG)

- **The adapter** (`scratchpad/probe74.py`):
  - `status()` returns unavailable.
  - `phonemize("este","e")` raises `TtsRuntimeError: espeak-ng failed: espeak-ng is not installed`.
  - Lang `a` raises `ValidationError`.
  - The real catalog has 54 voices: 28 available, 13 `language_unsupported` and 13 `espeak_missing`.
- **The API** (`build_services` and the real wiring, temp app data; receipt `C:/Temp/av-kit/s32-probe74-api.txt`):
  - `tts_espeak` is `{available: false, version: null, path: null}`.
  - `/tts/voices` returns the same 28/13/13 split. Every row carries `available` and `reason`. `af_heart` is true/null, `ef_dora` is false/`espeak_missing`, and `jf_alpha` and `zf_xiaobei` are false/`language_unsupported`.
  - With no model loaded, `generate ef_dora` returns the earlier "a TTS model must be loaded" 409, per `ASSET_409_ORDER`, and `tts_jobs` has 0 rows.
  - The voice 409 itself needs a loaded model, so AC-74.4 covers it with fakes.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s32-74-red","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check red-74 > C:/Temp/av-kit/s32-red-74-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PY74 pytest, ui Vitest UI74, Electron -g AC-74.9","phase":"red","exit_code":0,"result":"pass","tested_state":"MEU-73 tree + MEU-74 tests and TA edits only; no MEU-74 production edit","output":"PASS red-74 pytest: 109 failed (declared-symbol import errors only), 6 passed; no TEST_AMENDMENTS-file failure | PASS red-74 ui Vitest: 6 decisive, 41 passing | PASS red-74 Electron: 1 failing spec (AC-74.9) | PASS red-74","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-74-green","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check green-74 > C:/Temp/av-kit/s32-green-74-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PY74 + PY73 + REG73 pytest","phase":"green","exit_code":0,"result":"pass","tested_state":"MEU-74 Python implementation on base c72fc44 + MEU-73","output":"PASS pytest s32-green-74-pytest: 259 passed; baseline failures tolerated: [] | PASS green-74","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-74-green-ui","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check green-74-ui > C:/Temp/av-kit/s32-green-74-ui-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"ui Vitest UI74, UI builds, Electron tts-generate.test.ts","phase":"green","exit_code":0,"result":"pass","tested_state":"MEU-74 GUI implementation","output":"PASS s32-green-74-ui: 47 passed of 47 | PASS Electron tts-generate: 15 passed of 15 | PASS green-74-ui","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s32-74-gate","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check gate74 > C:/Temp/av-kit/s32-gate74-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"pyright, ruff, ui/mcp typecheck and lint, PY74+PY73+REG73 pytest, full ui Vitest and full mcp-server Vitest against the baseline, mcp build, UI builds, Electron tts-generate + AC-74.9 --repeat-each=20, OpenAPI two-step, ta-check","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-74 final working tree (base c72fc44 + MEU-73 + MEU-74 diff, incl. the Row 8 fixture repair)","output":"PASS pytest s32-gate74-pytest: 259 passed; baseline failures tolerated: [] | PASS s32-gate74-ui: 816 passed of 816 | PASS s32-gate74-mcp: 414 passed of 414 | PASS s32-gate74-e2e: 15 passed | PASS s32-gate74-e2e-repeat: 20 passed | openapi --check rc 0 | PASS ta-check: 15 TEST_AMENDMENTS rows (TA-1..TA-14), base c72fc44 | PASS gate74","fresh":true}
```

The first `gate74` run failed 12 `test_tts_assets.py` tests because of a test-order `sys.path` leak from the AC-73.16 fixture (walkthrough §Execution amendments, Row 8). The run above is the rerun after the setup repair.

```json
{"schema_version":"evidence.v1","check_id":"s32-74-api-scope","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check api-scope > C:/Temp/av-kit/s32-api-scope-74-run.txt 2>&1","cwd":"P:/av-kit-wt/tts-engine-runtime","scope":"PRODUCT_SCOPE against baseline.sha (tracked + untracked), OpenAPI check, ta-check","phase":"static","exit_code":0,"result":"pass","tested_state":"MEU-74 final working tree","output":"PASS PRODUCT_SCOPE: 45 changed product files since c72fc44, all listed | PASS ta-check (base c72fc44) | PASS api-scope","fresh":true}
```

The full Python suite was run outside the gate: 786 passed and 2 failed. The two failures are `test_pack_dist_onedir_layout[AC-24.10]` and `test_nsis_pack_check_script[AC-25.10]`. Both need a built onedir and installer, and both already fail in the row-0 baseline. The authoritative full gate is `WINDOWS_GATE` (H1-2).

**Authoritative gate (H1-2, attempt 2).** `windows-gate-result.json` and `package-smoke-result.json` are bound to one `WORKTREE_IDENTITY` (`cd879e6e…`). Attempt 1 missed `AC-63.5` and `AC-49.28` under host load; both passed 10/10 alone, with no file changed between attempts (walkthrough §Windows gate).

```json
{"schema_version": "evidence.v1", "check_id": "s32-h1-windows-gate", "command": "rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check windows-gate, then -Check package-smoke, then -Check windows-gate-check (H1-2; log C:/Temp/av-kit/s32-h1-gate-run.txt)", "cwd": "P:/av-kit-wt/tts-engine-runtime", "scope": "17 PROFILE D6 stages (full pytest, full Vitest, full Electron E2E, types, lint, builds, OpenAPI, SSOT render), PACKAGE_SMOKE, and the binding check", "phase": "full", "exit_code": 0, "result": "pass", "tested_state": "Session 32 final working tree on HEAD c72fc44, WORKTREE_IDENTITY cd879e6ef3f5f16a7266c0a66afbf19f284baa6863bc2fa17c1bc599f2611e18 at start and end of the gate and the smoke", "output": "PASS WINDOWS_GATE (17/17; pytest 803/0, Vitest 816/816, Electron 138/0/0/0 flaky 0) | PASS PACKAGE_SMOKE (offline 41,400 samples, negative probe Failed, MCP probe unreachable) | PASS windows gate + package smoke @ cd879e6ef3f5", "fresh": true}
```

### Quality Gate Results

```
pyright packages/: 0 errors
ruff check packages/ tests/: clean (ruff format drift is pre-existing at c72fc44, not gated)
ui + mcp-server typecheck, ui lint: clean
pytest PY74 + PY73 + REG73: 259 passed
ui Vitest full: 816/816 (COUNT_FLOORS 800)
mcp-server Vitest full: 414/414
Electron tts-generate: 15/15; AC-74.9 --repeat-each=20: 20/20
OpenAPI: --check passes; diff adds EspeakOut, DependenciesOut.tts_espeak, VoiceOut.available/reason
ta-check: 15 TA rows (TA-1..TA-14), base c72fc44
PRODUCT_SCOPE: 45 files, all listed
```

---

## Changed Files

Line counts are cumulative since `c72fc44`. Where MEU-73 and MEU-74 touch the same file, the counts include both.

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/tts.py` | modified | +72/−1 | `ESPEAK_LANG_CODES`, `UNSUPPORTED_LANG_CODES`, `VoiceUnavailableReason`, `VoiceAvailability`, `EspeakStatus`, `voice_availability` (plus the MEU-73 constants) |
| `packages/core/src/avkit_core/ports/tts.py` | modified | +20/−1 | `EspeakPort` (`status`, `phonemize`) |
| `packages/core/src/avkit_core/services/tts.py` | modified | +20/−4 | `list_voices` pairs; `VOICE_AVAILABLE_409`; `espeak=` injection |
| `packages/core/src/avkit_core/{domain,services}/health.py` | modified | +14/−3 | `tts_espeak` (plus MEU-73's `tts_voice_packs`) |
| `packages/infrastructure/src/avkit_infra/tts/espeak.py` | new | 1–258 | `EspeakCliAdapter`, `TtsRuntimeError`, `ESPEAK_VOICE`, `MULTI_E2M`, `EN_E2M`, `ESPEAK_EN_FALLBACK` |
| `packages/api/src/avkit_api/schemas/tts.py`, `routes/tts.py` | modified | +16/−4 | `VoiceOut.available/reason`; `_REASON_WIRES` maps the enum to the wire literal |
| `packages/api/src/avkit_api/schemas/health.py`, `routes/health.py` | modified | +22 | `EspeakOut`; the `tts_espeak` row |
| `packages/api/src/avkit_api/wiring.py` | modified | +7/−1 | one `EspeakCliAdapter` injected into `TTSService` and `HealthService` |
| `openapi.committed.json` | modified | +78/−7 | `EspeakOut`, `DependenciesOut.tts_espeak`, `VoiceOut.available/reason` (plus MEU-73's `tts_voice_packs`) |
| `ui/src/renderer/src/features/tts/tts-voices.ts` | modified | +20 | `VoiceUnavailableReason`, the optional fields, `VOICE_REASON_TEXT`, `voiceUnavailableText` |
| `ui/src/renderer/src/features/tts/VoiceCombobox.tsx` | modified | +56/−18 | disabled options, reason spans, the warning chip, guarded selection |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | +58 | `EspeakRow` and guidance (plus MEU-73's hook call) |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modified | +1 type import, 1 line (D-99) | `useVoices` typed `VoiceOut[]` (the rest is MEU-73) |
| `ui/tests/e2e/test-ids.ts`, `ui/tests/e2e/fixtures/tts-voices.json` | modified | +5; TA-7 | `NEW_TESTIDS`; the fixture rows gain `available`/`reason` |
| tests | new / modified | see `git diff --stat` | `test_tts_voice_availability.py`, `test_espeak_adapter.py` (new); AC-74 tests appended to `test_api_tts_runtime.py`, `settings-tts-runtime.test.ts`, `voice-combobox.test.tsx` and `tts-generate.test.ts`; TA-4, TA-5, TA-7, TA-9 and TA-14 edits; the `test_tts_voice_packs.py` `stack` fixture teardown (setup repair, Row 8 amendment) |

```diff
+        # `VOICE_AVAILABLE_409`, ahead of the asset check and the job row (`ASSET_409_ORDER`).
+        availability = voice_availability(config.lang_code, self._espeak_available())
+        if availability.reason is not None:
+            raise ConflictError(f"voice unavailable: {voice} ({availability.reason.value})")
         variant_id = status.variant_id
         self._require_assets(variant_id, voice, enabled_steps)
```

```diff
+def voice_availability(lang_code: str, espeak_available: bool) -> VoiceAvailability:
+    """`VOICE_REASON`: j/z never; e/f/h/i/p only with eSpeak NG; a/b always."""
+    if lang_code not in KOKORO_LANG_CODES:
+        raise ValidationError(f"unknown lang_code: {lang_code!r}")
+    if lang_code in UNSUPPORTED_LANG_CODES:
+        return VoiceAvailability(False, VoiceUnavailableReason.LANGUAGE_UNSUPPORTED)
+    if lang_code in ESPEAK_LANG_CODES and not espeak_available:
+        return VoiceAvailability(False, VoiceUnavailableReason.ESPEAK_MISSING)
+    return VoiceAvailability(True, None)
```

---

## Codex Validation Report

_Left blank for the reviewer agent, which fills this section during `/validation-review`._

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

- **AC-74.11 LOCAL-ESPEAK:** optional and manual. It needs eSpeak NG 1.52 installed and the MEU-72 router (row 10). Row 12 writes the walkthrough §LOCAL-ESPEAK. eSpeak NG is not installed on this machine, so unless Mat installs it, that section records the check as unverified (plan `LOCAL-ESPEAK`, S5).
- **ja/zh voices** stay `language_unsupported`. The follow-up issue is recorded in D-70.

---

## Decision Log

```yaml
decision_log:
  - id: D-95
    stage: execution
    question: "Row 5 census S2 (missed at row 1): tests/e2e/test_api_tts_models.py:156-161 (AC-16.7) asserts the exact /tts/voices row as four keys, but AC-74.3 and spec 03 add available/reason to every row, and the file is not in TEST_AMENDMENTS. How does MEU-74 handle it?"
    resolution: human
    class: two-way
    chosen: "Add TA-14: the AC-16.7 expected dict gains \"available\": True, \"reason\": None. Additive only; the VOICES_FACADE call count, the lang_code ban and the route source scans are unchanged. The file joins the MEU-74 Files Modified table."
    source_tag: Human-approved
    precedents: ["tests/e2e/test_api_tts_models.py:150-167 — AC-16.7 VOICES_FACADE", "docs/build-plan/03-service-layer.md:451 — every /tts/voices row carries available/reason", "D-89"]
    research: { engine: none, sources: [] }
    reasoning: "AC-16.7's control is the facade (public list_voices called, no lang_code); the exact-dict equality is incidental. Omitting the fields on available rows would contradict AC-74.3 'both fields on every row'."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'Add TA-14 (Recommended)' (AskUserQuestion, census S2b)"
  - id: D-96
    stage: execution
    question: "Row 5: AC-74.7 says the eSpeak NG releases link 'opens through the existing external-link path', but the app has none (main denies window.open and navigation; the preload exposes openPath, showItemInFolder and clipboard IPC only). How does the guidance link work?"
    resolution: human
    class: two-way
    chosen: "Show the releases URL as selectable text plus a 'Copy link' button that calls the existing window.api.writeClipboardText. Renderer-only (SettingsPage.tsx); no new IPC channel or main-process surface. AC-74.7 is reworded from 'opens' to 'copies'."
    source_tag: Human-approved
    precedents: ["ui/src/main/index.ts:484-489 — setWindowOpenHandler deny and will-navigate block", "ui/src/main/preload.ts:51-53 — openPath, showItemInFolder, writeClipboardText", "ui/src/renderer/src/features/settings/SettingsPage.tsx:948 — 'Copy log path' uses writeClipboardText"]
    research: { engine: none, sources: [] }
    reasoning: "An openExternal channel would add three files outside the MEU-74 Files Modified table and a new main-process surface for one link. Copying uses a control Settings already has."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'URL + Copy link (Recommended)' (AskUserQuestion, eSpeak link)"
  - id: D-97
    stage: execution
    question: "Row 6: ESPEAK_G2P raises TtsRuntimeError, and the red-74 tests import it with the adapter, but no TtsRuntimeError exists and packages/core/src/avkit_core/domain/errors.py is not in the MEU-74 Files Modified table. Where is it defined?"
    resolution: autonomous
    class: two-way
    chosen: "avkit_infra/tts/espeak.py defines class TtsRuntimeError(DomainError). It is a DomainError subclass, so the API's existing DomainError handling covers it, and errors.py is not touched."
    source_tag: Local Canon
    precedents: ["implementation-plan.md ESPEAK_G2P and AC-74.6 — 'raises TtsRuntimeError(\"espeak-ng failed: …\")'", "packages/core/src/avkit_core/domain/errors.py — DomainError base"]
    research: { engine: none, sources: [] }
    reasoning: "The contract names the error but not its module. Defining it beside its only raiser stays inside the Files Modified fence. MEU-72 may move it to domain/errors.py if the ONNX path raises it too, which its own Files Modified table governs."
  - id: D-98
    stage: execution
    question: "Row 6: the ESPEAK_MAP_PARITY test ends with assert 'misaki.espeak' not in sys.modules. Importing avkit_infra.tts.espeak runs the avkit_infra.tts package init, which imports KokoroAdapter, then kokoro, whose pipeline.py does 'from misaki import en, espeak'. The assertion can never pass in this process. How is it corrected?"
    resolution: human
    class: two-way
    chosen: "Replace the sys.modules line with an AST scan of avkit_infra/tts/espeak.py: no Import or ImportFrom of misaki, phonemizer or espeakng_loader. The two table-parity assertions are unchanged. The runtime sys.modules check stays with MEU-72 IMPORT_HYGIENE, which runs in a fresh interpreter after the adapter stops importing kokoro."
    source_tag: Human-approved
    precedents: [".venv/Lib/site-packages/kokoro/pipeline.py:5 — 'from misaki import en, espeak'", "packages/infrastructure/src/avkit_infra/tts/__init__.py:3 — imports KokoroAdapter", "AGENTS.md:57 — a proven wrong expectation needs human authorization", "implementation-plan.md IMPORT_HYGIENE"]
    research: { engine: none, sources: [] }
    reasoning: "D-71's control is that av-kit's adapter never imports misaki.espeak. A process-wide sys.modules check measures whatever else the pytest process imported, so it fails for reasons outside espeak.py. The import scan tests the adapter's own source directly."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'AST import scan (Recommended)' (AskUserQuestion, parity fix)"
  - id: D-99
    stage: execution
    question: "Row 7: VoiceOut gains the optional boolean available, and ui typecheck then fails at TTSPage.tsx:126. That line casts useVoices() rows, typed Array<Record<string, string>> in useTtsJob.ts, to VoiceOut[], and a string record no longer overlaps a type with a boolean field. TTSPage.tsx and useTtsJob.ts are not in the MEU-74 Files Modified table. How is it fixed?"
    resolution: autonomous
    class: two-way
    chosen: "useTtsJob.ts useVoices types the /tts/voices rows as VoiceOut[] (type-only import from tts-voices.ts). TTSPage.tsx is unchanged; its cast becomes a no-op. useTtsJob.ts is already a plan file (MEU-73) and joins the MEU-74 Files Modified table."
    source_tag: Local Canon
    precedents: ["implementation-plan.md MEU-74 Files Modified — tts-voices.ts 'available?: boolean / reason?: … types'", "ui/src/renderer/src/features/tts/TTSPage.tsx:126 — the VoiceOut[] cast", "D-95 — a file added to the MEU-74 Files Modified table"]
    research: { engine: none, sources: [] }
    reasoning: "The plan fixes the VoiceOut field types, so the compile break is a direct consequence of the plan, not a design choice. Typing the query at its source is a one-line, type-only change with no runtime effect. The alternative, editing TTSPage.tsx, touches a file no plan table lists."
  - id: D-100
    stage: execution
    question: "Row 13: the eSpeak NG guidance 'Copy link' button (D-96) has no data-testid, and the plan's NEW_TESTIDS lists only tts-espeak-row, tts-espeak-guidance and voice-unavailable-reason. The GUI canon requires a test id on every interactive element and an index row for every user-visible action. Is it added?"
    resolution: autonomous
    class: two-way
    chosen: "Add data-testid=\"tts-espeak-copy-link-btn\" to the button in SettingsPage.tsx, and register TTS_ESPEAK_COPY_LINK_BTN in ui/tests/e2e/test-ids.ts after the MEU-74 block. No behaviour or assertion changes; both files are already in the MEU-74 Files Modified table. No gui-actions-index row is added: the AC-23.20 audit resolves every settings row's IPC cell through gui-actions-audit.test.ts:66-77, which maps no writeClipboardText cell, so a settings:copy_espeak_link row fails it. Extending that resolver is a test edit outside TEST_AMENDMENTS. The existing Settings 'Copy log path' button has no index row either, for the same reason. Both go to closeout as one follow-up."
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1259 and :1275 — every interactive element uses a test-ids.ts constant", "docs/build-plan/gui-actions-index.md:111 — a page is incomplete if a button has no testid", "ui/tests/unit/gui-actions-audit.test.ts:66-77 — resolveIpcChannel has no writeClipboardText mapping", "D-96"]
    research: { engine: none, sources: [] }
    reasoning: "D-96 added the button after NEW_TESTIDS was fixed, so the list missed it. The canon rule is explicit, the change is one attribute plus one registry line, and the AC-74.7 test still finds the button by role and name. Leaving it would ship a control the GUI audit rules call incomplete. The index row is the one part that needs a test change, so it is deferred rather than forced."
```

The row 8 setup repair (the `test_tts_voice_packs.py` `stack` fixture waits for the background spaCy download before teardown) is not a decision. It changes no assertion, expected value or product line, and it is recorded as a walkthrough amendment.

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-15 | claude-code | Initial handoff after gate74 and api-scope |
| Amended | 2026-10-15 | claude-code | Row 13 (D-100): `data-testid="tts-espeak-copy-link-btn"` on the eSpeak NG Copy link button and `TTS_ESPEAK_COPY_LINK_BTN` in `test-ids.ts`; no gui-actions-index row (AC-23.20 resolver). `settings-tts-runtime` + `capture-flatten` Vitest 18/18 after the change. |
| Reconciled | 2026-10-15 | claude-code | H1-5: added the authoritative H1-2 gate record (`WINDOWS_GATE` 17/17 + `PACKAGE_SMOKE` @ `cd879e6e`) |
