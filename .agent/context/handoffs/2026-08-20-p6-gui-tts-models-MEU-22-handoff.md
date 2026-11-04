---
date: "2026-08-20"
project: "p6-gui-tts-models"
meu: "MEU-22"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-20-p6-gui-tts-models/implementation-plan.md"
build_plan_section: "bp06s4"
agent: "cursor-composer"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-20-p6-gui-transcript-MEU-21-handoff.md"
---

# Handoff: 2026-08-20-p6-gui-tts-models-MEU-22-handoff

> **Status**: `draft`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-22 — TTS page at `/tts` (`TTS_HOME`), prepare/generate/cancel (no queue), Model Manager (`CATALOG_ITEMS` as-is), voices + language filter, `FILE_LOAD_OUT` `{ text, basename }`, clipboard paste via IPC, `PALETTE_DELIVER` for `tts:prepare`/`tts:generate`, Wave 2 E2E with `installTtsSeam`. No MEU-23–25. No FastAPI/MCP rewrites. Chrome not rewound.
**Build Plan Section**: `docs/build-plan/06-gui.md` §TTS
**Predecessor**: MEU-21 transcript; Settings models Browse deferred to MEU-23

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-22.1 | integration | `TTS_HOME` at `#/tts` | Spec 194–197, 741 | `tts-page.test.ts` AC-22.1; W2-1 | ✅ |
| AC-22.2 | unit | `WORD_COUNT` / `SENTENCE_COUNT` / `DURATION_WPM` | Spec 832–834 | `tts-page.test.ts` AC-22.2 | ✅ |
| AC-22.3 | integration | `FILE_LOAD` + `FILE_LOAD_OUT` `{ text, basename }` | Spec 106–107, 830, 894 | `tts-page.test.ts` AC-22.3; W2-5 | ✅ |
| AC-22.4 | integration | `PASTE` + `CLIPBOARD_READ` via `deps.readClipboard` | Spec 831 | `tts-page.test.ts` AC-22.4; W2-5 | ✅ |
| AC-22.5 | unit | `PREPARE_STEPS` + `PREPARE_DEFAULT_ON` | Spec 809–821 | `tts-page.test.ts` AC-22.5 | ✅ |
| AC-22.6 | integration | `PREPARE_BODY` + `PREVIEW_SPLIT` | Spec 823 | `tts-page.test.ts` AC-22.6; W2-4 | ✅ |
| AC-22.7 | integration | `GENERATE_BODY` + `JOB_OUT` (no `output_path`) | Spec 894 | `tts-page.test.ts` AC-22.7; W2-4 | ✅ |
| AC-22.8 | unit | `JOB_POLL` Query v5 1000/5000 | Spec 846 | `tts-page.test.ts` AC-22.8 | ✅ |
| AC-22.9 | integration | `ENABLED_WHEN` + Cancel DELETE (no stop) | Spec 875; lock 4 | `tts-page.test.ts` AC-22.9; W2-5 | ✅ |
| AC-22.10 | integration | `SEGMENT` from `segments_done`/`total` | Spec 882 | `tts-page.test.ts` AC-22.10 | ✅ |
| AC-22.11 | integration | `VOICES_ENVELOPE` + `LANG_FILTER` | Spec 851–866 | `tts-page.test.ts` AC-22.11 | ✅ |
| AC-22.12 | unit | `SPEED_RANGE` + `FORMAT_VALUES` G30 | Spec 872–873; G30 | `tts-page.test.ts` AC-22.12 | ✅ |
| AC-22.13 | integration | `OUTPUT_DEFAULT` + browse `output_path` only | Spec 874, 1003 | `tts-page.test.ts` AC-22.13; W2-5 | ✅ |
| AC-22.14 | integration | `RESUME_TEXT` SETTINGS_LEAVES | Spec 894, 1006 | `tts-page.test.ts` AC-22.14 | ✅ |
| AC-22.15 | integration | Model status + unload VOID_204 | Spec 842–848 | `tts-page.test.ts` AC-22.15; W2-5 | ✅ |
| AC-22.16 | integration | `CATALOG_ITEMS` + `RUNTIME_BIND` | Spec 845–846 | `tts-page.test.ts` AC-22.16 | ✅ |
| AC-22.17 | integration | `LOAD_BODY` + `DEVICE_VALUES` | Spec 847–849 | `tts-page.test.ts` AC-22.17; W2-5 | ✅ |
| AC-22.18 | integration | `ERROR_SURFACE` G15 | G15 | `tts-page.test.ts` AC-22.18 | ✅ |
| AC-22.19 | integration | `PALETTE_DELIVER` AppShell `av-kit:tts:*` | index 48–49; G11 | `tts-page.test.ts` AC-22.19; W2-6 | ✅ |
| AC-22.20 | integration | `TTS_LOCAL_IDS`; no settings models browse | index 45–55 | `tts-page.test.ts` AC-22.20 | ✅ |
| AC-22.21 | integration | Open file/folder IPC | index 51–52 | `tts-page.test.ts` AC-22.21; W2-5 | ✅ |
| AC-22.22 | integration | Wave 2 written+wired + census | Spec 1104; E2 | `tts-generate.test.ts` W2-1…W2-6; census | ✅ |
| AC-22.23 | unit | G36 / anti-placeholder; no API/MCP edit | G36; G8 | `tts-page.test.ts` AC-22.23; scans | ✅ |
| AC-22.24 | unit | `STATUS_COLORS` / `SPEED_PRESETS` / SelectInput | G30–G32 | `tts-page.test.ts` AC-22.24 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-22.1–22.24 UI | `PASS: RED_ORACLE ui` — 24 distinct failed JSON tests | 24 passed (`tts-page.test.ts`); full suite 141 passed | `C:/Temp/av-kit/fail-to-pass-meu-22-ui.txt`; `ui-green-meu-22.txt` |
| Wave 2 E2E | census required before Playwright | 6 passed; `PASS: E2E_CONTROL_CENSUS` | `C:/Temp/av-kit/e2e-wave2.txt`; `e2e-control-census.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| UI Red + `assert-red-oracle.ps1 -Kind ui` | 0 | `PASS: RED_ORACLE ui` / `RED_ORACLE_OK` |
| UI Green tsc/vitest/eslint/build | 0 | `Tests  141 passed`; electron-vite build |
| `assert-e2e-control-census.ps1` | 0 | `PASS: E2E_CONTROL_CENSUS` |
| Playwright `tts-generate.test.ts` | 0 | 6 passed (`e2e-wave2.txt`) |

### Quality Gate Results

```
tsc: 0 errors
eslint: 0 warnings (max-warnings 0)
vitest: 141 passed
anti-placeholder: 0 matches (tts + ipc)
G36 skip/only: 0 matches
npm run build: ok
E2E_CONTROL_CENSUS: PASS
Playwright TTS wave: 6 passed
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/tts/*` | new | — | TTS page, hooks, commands, controls, prepare, stats, voices |
| `ui/src/renderer/src/router.tsx` | modified | — | `/tts` → `TTSPage` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | — | `av-kit:tts:*` palette listeners |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | — | `tts:prepare` / `tts:generate` |
| `ui/src/main/ipc.ts` | modified | — | `FILE_LOAD_OUT` + `readClipboard` |
| `ui/src/main/index.ts` | modified | — | `clipboard.readText` deps |
| `ui/src/renderer/src/env.d.ts` | modified | — | `readTextFile` return type |
| `ui/tests/unit/tts-page.test.ts` | new | — | AC-22.1–22.24 |
| `ui/tests/e2e/tts-generate.test.ts` | new | — | W2-1…W2-6 + `installTtsSeam` |
| `ui/tests/e2e/test-ids.ts` | modified | — | WAVE2 + EXTRA ids |
| `ui/tests/unit/secret-paths.test.ts` | modified | — | assert `{ text, basename }` |

```diff
 case 'read-text-file': {
-  return { ok: true, value: sliced }
+  return { ok: true, value: { text: sliced, basename: basename(chosen) } }
 }
 case 'read-clipboard-text': {
-  return { ok: true, value: '' }
+  const text = (await deps.readClipboard?.()) ?? ''
+  return { ok: true, value: text }
 }
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

`pending` — awaiting Codex `/execution-critical-review`

---

## Corrections Applied (2026-08-20)

**Findings resolved**: 6/6 (exec Round 2 `approved`)

| Finding | Fix |
|--------|-----|
| F1 | Catalog uses `ModelVariantOut` (`id`, `name`, `is_downloaded`); load/get enablement; `memory_bytes`; download Zod |
| F2 | Paste inserts at caret; empty clipboard no-op |
| F3 | `Pending` in statuses; Generate/Cancel enablement |
| F4 | `chunk_max_chars` hydrated and passed to prepare |
| F5 | Debounced `input_text` PUT (300ms) |
| F6 | E2E `new Response(null, { status: 204 })`; main E2E IPC stubs |

---

## Deferred Items

| Item | Target MEU | Basis |
|------|------------|-------|
| Settings models Browse / HelpCards | MEU-23 | grouping Session 11 |
| PyInstaller / NSIS | MEU-24/25 | grouping Session 12 |

---

## Residual Risk

- First-row-only `model-get-btn` / `model-load-btn` testids (strict Playwright + census); other rows remain clickable without those testids.
- Live HF/Kokoro never exercised in Wave 2 (by design; seam fail-closed).
