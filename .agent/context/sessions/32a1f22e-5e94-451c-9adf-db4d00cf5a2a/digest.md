# Session Digest — 32a1f22e-5e94-451c-9adf-db4d00cf5a2a

**Date:** 2026-11-06
**Project:** 2026-11-06-tts-build-capability (Session 51: MEU-117 build capability, MEU-118 device options), plan, implementation and closeout
**Duration:** one day, over several compactions

## Decisions Made

| # | Decision | Authority | Source |
|---|----------|-----------|--------|
| 1 | Scope: list PyTorch disabled with a reason, refuse its download with 409, no runtime download or bundled torch (D-217); never espeak (D-237) | Human-approved | Triage 2026-11-04, carried by Mat's Session 51 brief |
| 2 | Plan decisions D-309 to D-321 | Codex-verified | Plan review r1 approved; the reflection's Decisions Log carries each one |
| 3 | Run the plan with every gate default | Human-approved | USER_EXPLICIT 2026-11-06 "proceed" |
| 4 | Commit and push Session 51 | Human-approved | USER_EXPLICIT 2026-11-06 "commit and push" |
| 5 | No AI attribution trailer on the commit | Agent-decided | git-workflow SKILL §Commit Message Convention and task row H2-5 |
| 6 | Session 52's starter prompt lives at `C:/Temp/av-kit/session-52-prompt.md`, outside the repo | Agent-decided | Mat asked for the prompt on 2026-11-06 |

## Blockers & Open Questions

- `CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR` stays open; the Python suite ran with TMP and TEMP outside the home folder.
- MEU-125's rc.2 gate repeats the packaged capability smoke on the release build.
- The FP16 test set for Session 52 exists only in session `7f638658`'s scratchpad; Session 52's prompt copies it into its plan folder first.

## Test & Quality-Gate Outcomes

| Gate | Result | Notes |
|------|--------|-------|
| Codex plan review | Approved (r1) | 0 findings, 7,450,042 tokens |
| Codex execution review | Approved (r1) | 0 findings, `intent_achieved: yes`, 8,724,472 tokens; Q8 corrected one issue name in the MEU-117 handoff |
| Session gate run 1 | Failed | AC-118.2 setup race in the test's own `settled()`, fixed with one macrotask inside `act` |
| Session gate run 2 | Pass | On `71d0d3a`+`bef8c81b`: pytest 1274 (+9), Vitest UI 1163 (+19), Vitest MCP 470 (+4), Electron 45 |
| Packaged `--phase capability` | Pass on a fresh build | Failed on the 2026-11-04 onedir, as expected |
| Dev venv | Pass | `npm run dev`'s backend loads and generates with `kokoro-pt-fp32`; the real models folder kept its 159 files |
| Closeout checks | Pass | Reflection OK with 31 Decisions Log rows; `render --check` OK; canon suites 14 passed; task lint 30 rows; 59 paths, none outside scope |
| Git commit | This commit | Pushed to `main` on Mat's words |

## Files Changed

### New Files
- `.agent/context/handoffs/2026-11-06-tts-build-capability-*`: two MEU handoffs, plan and implementation reviews
- `docs/execution/plans/2026-11-06-tts-build-capability/`, `docs/execution/reflections/2026-11-06-tts-build-capability-reflection.md`
- `ui/src/renderer/src/features/tts/tts-devices.ts`; tests `tests/e2e/test_api_model_capability.py`, `mcp-server/tests/models-availability.test.ts`, `ui/tests/unit/{settings-tts-device,tts-devices,tts-model-selection}.test.ts`

### Modified Files
- Backend: `domain/tts.py`, `ports/tts.py`, `services/models.py`, `tts/adapter.py`, `routes/models.py`, `schemas/models.py`, `openapi.committed.json`
- MCP and UI: `toolsets/models.ts`, `SelectInput.tsx`, `SettingsPage.tsx`, `TTSPage.tsx`, `tts-controls.ts`, `useTtsJob.ts`
- Tests and tools: `tests/e2e/`, `tests/integration/`, `tests/unit/`, `ui/tests/`, `tools/smoke_packaged_tts.py`
- Records: `.agent/context/` status, focus, register, triage and grouping; `docs/BUILD_PLAN.md`; `docs/build-plan/03` to `06`; `docs/execution/metrics.md`

## Provenance

- Conversation ID: `32a1f22e-5e94-451c-9adf-db4d00cf5a2a`
- Transcript: `C:\Users\Mat\.claude\projects\p--av-kit\32a1f22e-5e94-451c-9adf-db4d00cf5a2a.jsonl`
- Review ledgers: `C:\Temp\av-kit\review-ledger\s51-plan-2026-11-06-tts-build-capability.json`, `C:\Temp\av-kit\review-ledger\s51-execution-2026-11-06-tts-build-capability.json`
