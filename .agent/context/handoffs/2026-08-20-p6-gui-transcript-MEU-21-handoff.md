---
date: "2026-08-20"
project: "p6-gui-transcript"
meu: "MEU-21"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-20-p6-gui-transcript/implementation-plan.md"
build_plan_section: "bp06s3"
agent: "cursor-grok-4.6"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-20-p6-gui-downloader-MEU-20-handoff.md"
---

# Handoff: 2026-08-20-p6-gui-transcript-MEU-21-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-21 — Transcript page at `/transcript` (`TRANSCRIPT_HOME`), Query poll of `{ items, processor }`, channel cards + output tree, `STOP_VERB`, G20 portaled confirm, `PALETTE_DELIVER` on AppShell, Wave 2 E2E with `E2E_SEAM_GATE`. No MEU-22–25. No FastAPI/MCP rewrites. Chrome RULE-1/2/3 consumed, not rewound.
**Build Plan Section**: `docs/build-plan/06-gui.md` §Transcript
**Predecessor**: MEU-20 downloader; MEU-26 chrome stays; MEU-27 console polish is a separate insert

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-21.1 | integration | `TRANSCRIPT_HOME` at `#/transcript` | Spec 189–192, 595 | `transcript-page.test.ts` AC-21.1; W2-1 | ✅ |
| AC-21.2 | integration | `CREATE_BODY` `{ channel_url }` only | Spec 724; Boundary | `transcript-page.test.ts` AC-21.2; W2-4 | ✅ |
| AC-21.3 | integration | `LIST_ENVELOPE` + `QUERY_KEY` | Spec 725, 737, 1147 | `transcript-page.test.ts` AC-21.3 | ✅ |
| AC-21.4 | unit | Poll 1000/5000 Query v5 | Spec 737 | `transcript-page.test.ts` AC-21.4 | ✅ |
| AC-21.5 | integration | `CARD_FIELDS` + `CARD_QUEUE` (no table) | Spec 647–659, 1149 | `transcript-page.test.ts` AC-21.5; W2-4 | ✅ |
| AC-21.6 | unit | `OUTPUT_TREE` `{output_dir}/raw\|compiled` | Spec 674–684; R3-1 | `transcript-page.test.ts` AC-21.6 | ✅ |
| AC-21.7 | integration | `ENABLED_WHEN` + `STOP_VERB` (no `cancel-btn`) | Spec 636–637, 729–732 | `transcript-page.test.ts` AC-21.7; W2-5 | ✅ |
| AC-21.8 | unit | `REORDER_BODY` `job_ids` permutation | Spec 665, 728 | `transcript-page.test.ts` AC-21.8; W2-5 | ✅ |
| AC-21.9 | unit | Requeue/Retry hide-not-disable | Spec 716–717 | `transcript-page.test.ts` AC-21.9; W2-5 | ✅ |
| AC-21.10 | integration | Compile + open compiled/zip/folder | Spec 711–715, 735 | `transcript-page.test.ts` AC-21.10; W2-5 | ✅ |
| AC-21.11 | integration | `IN_PAGE_CONFIRM` G20 portal + DELETE once | Spec 718; G20 | `transcript-page.test.ts` AC-21.11; W2-5 | ✅ |
| AC-21.12 | integration | `ERROR_SURFACE` G15 banner | G15 | `transcript-page.test.ts` AC-21.12 | ✅ |
| AC-21.13 | integration | `PALETTE_DELIVER` AppShell `av-kit:transcript:*` | index 32–36; G11 | `transcript-page.test.ts` AC-21.13; W2-6 | ✅ |
| AC-21.14 | integration | `TRANSCRIPT_LOCAL_IDS`; no settings browse | index 37–44, 62 | `transcript-page.test.ts` AC-21.14 | ✅ |
| AC-21.15 | integration | IPC open-path when path present | index 42–44; MEU-19 | `transcript-page.test.ts` AC-21.15; W2-5 | ✅ |
| AC-21.16 | integration | Wave 2 written+wired + `E2E_SEAM_PROOF` | Spec 1103; E2; RULE-2 | `transcript-queue.test.ts` W2-1…W2-6; census | ✅ |
| AC-21.17 | unit | `RATE_ETA` + `BATCH_OMIT` | Spec 655–657 | `transcript-page.test.ts` AC-21.17 | ✅ |
| AC-21.18 | unit | Tokens + `JOB_STATUSES` includes Paused | G31–G32; Spec 650 | `transcript-page.test.ts` AC-21.18 | ✅ |
| AC-21.19 | unit | G36 / anti-placeholder | G36 | `transcript-page.test.ts` AC-21.19; scans | ✅ |
| AC-21.20 | integration | Create uses `TranscriptJobOut` then invalidate | transcripts.py 58–64 | `transcript-page.test.ts` AC-21.20 | ✅ |
| AC-21.21 | integration | OpenAPI `--check`; no API/MCP/chrome rewind | G8; grouping | `transcript-page.test.ts` AC-21.21 | ✅ |
| AC-21.22 | unit | `CHANNEL_URL_HINT`; blank Add no-ops | Spec 608, 668 | `transcript-page.test.ts` AC-21.22 | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-21.1–21.22 UI | `PASS: FAIL_TO_PASS red` — 22 distinct failed JSON tests | 117 passed (24 files) | `C:/Temp/av-kit/fail-to-pass-meu-21-ui.txt`; `ui-gate-meu-21.txt` |
| Wave 2 E2E | census + Playwright not present in Red | 30 passed; `PASS: E2E_CONTROL_CENSUS` | `C:/Temp/av-kit/e2e-wave2.txt` |

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| UI Red + `assert-red-oracle.ps1 -Kind ui` | 0 | `PASS: FAIL_TO_PASS red` |
| UI Green/gate tsc/vitest/eslint/build | 0 | `Tests  117 passed`; electron-vite build |
| `assert-e2e-control-census.ps1` | 0 | `PASS: E2E_CONTROL_CENSUS` |
| Playwright wave 0/1/2/5/7 | 0 | 30 passed (`e2e-wave2.txt`) |
| Row-4 anti-placeholder / G36 | 0 | no TODO/FIXME/skip/only hits |
| H1-2 UI verify | 0 | 117 vitest (`ui-verify.txt`) |
| H1-2 Python `REGRESSION_TESTS` | 0 | 298 passed (`pytest-p6-regression.txt`) |
| H1-3 SSOT ready_for_review | 0 | `PASS: SSOT_READY`; drift check passed |
| H1-4 OpenAPI `--check` | 0 | `openapi-check.txt` |

### Quality Gate Results

```
tsc --noEmit: 0 errors
eslint src/ tests/: 0 errors
vitest: 117 passed
playwright wave0/1/2/5/7: 30 passed
pytest REGRESSION_TESTS: 298 passed
anti-placeholder / G36: clean
OpenAPI --check: pass
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/src/renderer/src/features/transcript/*` | new | — | Page, hook, commands, cards, tree, rate/eta, G20 confirm |
| `ui/src/renderer/src/router.tsx` | modified | — | `/transcript` → `TranscriptPage` |
| `ui/src/renderer/src/components/layout/AppShell.tsx` | modified | — | always-mounted `av-kit:transcript:*` |
| `ui/src/renderer/src/registry/commandRegistry.ts` | modified | — | `TRANSCRIPT_PALETTE_IDS` events only |
| `ui/src/renderer/src/lib/api.ts` | modified | — | `E2E_SEAM_GATE` (`__e2eSeamInstalled`) |
| `ui/src/main/index.ts` | modified | — | `AVKIT_E2E` no-op `openPath` |
| `ui/tests/unit/transcript-page.test.ts` | new | — | AC-21.1–21.22 |
| `ui/tests/e2e/transcript-queue.test.ts` | new | — | W2-1…W2-6 + fail-closed fetch seam |
| `ui/tests/e2e/test-ids.ts` | modified | — | transcript extras |
| `ui/tests/e2e/fixtures/transcript-job.json` | new | — | seam fixture |

```diff
-  component: LazyPlaceholder,
+  component: TranscriptPage,
```

```diff
+    // Always-mounted production owner for av-kit:transcript:* palette events.
+    window.addEventListener(TRANSCRIPT_EVENTS.add, onTranscriptAdd)
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
| 1 | — | — | — | — | — |

### Verdict

`pending` — implementer does not author `approved`

---

## Corrections Applied (2026-08-20)

**Findings resolved**: n/a (pre-review)

| # | Finding | Fix Applied | Verification |
|---|---------|-------------|--------------|
| — | MEU-27 review isolated MEU-21 sources to `.agent/context/isolated/2026-08-20-meu-21-wip/` | Restored feature/tests and re-wired router/AppShell/registry without chrome rewind | Wave 2 30 passed after restore |

---

## Deferred Items

Settings browse/write `transcript.output_dir` remains MEU-23 (`settings:browse_transcript_dir` is not on this page).

| Item | Reason | Deferred-to MEU (scheduled) | Follow-up |
|------|--------|-----------------------------|-----------|
| Browse/write transcript output dir | out-of-scope for MEU-21 | MEU-23 | grouping Session 11 |

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-20 | cursor-grok-4.6 | Initial MEU-21 handoff |
| Submitted for review | 2026-08-20 | cursor-grok-4.6 | H1-7 Codex dispatch next |
