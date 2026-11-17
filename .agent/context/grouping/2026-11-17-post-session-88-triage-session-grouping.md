# 2026-11-17 Post-Session 88 triage · Session grouping

> **Source:** the 2026-11-17 issue triage of `.agent/context/known-issues.yaml` (24 issues open or mitigated; all in the §1 traceability table) and Mat's request "run @.agent/skills/issue-triage/ create session grouping and continue planning and executing as orchestrator".
> **Generated:** 2026-11-17
> **Method:**
> - Triage (`.agent/workflows/issue-triage.md`): `discover` found 0 candidates and `verify --deep` no findings (`C:/Temp/av-kit/triage-1117/discover-scan.txt`, `verify-deep.txt`). The five issues filed since the last triage were classified; no other category changed. D-1100 (Mat's ruling) and D-1101 are stage `triage` entries in their issues' `decision_log`. `bucket` proposed one P3 batch of the two MEU-NEW issues, which §3 keeps. `triage --output` rewrote `triage-output.yaml`, and `render --check` is OK (`C:/Temp/av-kit/triage-1117/render-check2.txt`).
> - Stage A: two MEUs, MEU-156 and MEU-157, registered in `meu-status.yaml`, band P2 and `pending`, with homes in 10 and 06 and matrix rows 10.11 and 6.21. `meu_status render --check` is green with 156 MEUs (`C:/Temp/av-kit/triage-1117/meu-check.txt`).
> - Stage B: the two MEUs and the three test and dev debt issues with no MEU are grouped into Sessions 89 and 90.
> - Mat's rulings on the Session 76 follow-ups, 2026-11-17: D-913 B ("I authourize this session to edit that repo, commit and push on it as well"), so the dispatch fixture fix went upstream as agentic-framework `1aabe2d` after a Codex review approved it with no findings; D-914 B, so the leftover `%TEMP%/av-kit/receipts` folder is gone (Mat ran the removal). `CLI-DISPATCH-PLACEHOLDER-FIXTURE` records both.
> **Origin:** Session 88 closed MEU-155 (`ae1a33c`) and filed `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT`; Sessions 78 and 81 filed the three flakes and the dev-run gap. Nothing here is a new capability.
> **Status:** Active. This is a reversible draft, not a gate. Mat's message asks for planning and execution to continue, so each session's plan goes to execution once its Codex plan review approves (D-1104).
> **Parallel work:** none seen. Only the `main` worktree exists, and HEAD is `ae1a33c`. The highest decision ID in use before this triage was D-1098 (D-1099 was reserved by Session 88 and left unused). No Session 89 or later, MEU-156 or later, or D-1100 or later was claimed anywhere.

---

## 1. MEU / scope summary

| MEU | Slug | Covers (issue) | Layer | Depends on |
|-----|------|----------------|-------|------------|
| MEU-156 | `gui-queue-cancel-paused` | `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT` | renderer (`convert-controls.ts`, `download-controls.ts`, the two command modules) | MEU-45, MEU-46, MEU-155 |
| MEU-157 | `gui-convert-browse-after-mount` | `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE` | renderer (`convert-commands.ts`, `ConvertPage.tsx`), E2E (`convert-queue.test.ts`) | MEU-97 |

Build-plan homes, each an anchored section with source-labelled rows:
- [10 §Cancel while paused (residual)](../../../docs/build-plan/10-queue-card-ui.md#queue-cancel-paused-residual)
- [06 §Convert browse waits for the page (residual)](../../../docs/build-plan/06-gui.md#convert-browse-after-mount-residual)

Issue → disposition traceability (every issue open or mitigated, 24 in all):

| Issue | Status · category | Disposition |
|-------|-------------------|-------------|
| `QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT` | open · MEU-NEW P4 | MEU-156, Session 89 (D-1100, Mat's ruling) |
| `CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE` | open · MEU-NEW P3 | MEU-157, Session 89 (D-1101) |
| `PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD` | open · TECH-DEBT P3 | Session 90, no MEU (D-1103) |
| `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED` | open · TECH-DEBT P4 | Session 90, no MEU (D-1103) |
| `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT` | open · TECH-DEBT P4 | Session 90, no MEU (D-1103) |
| `TTS-ONNX-FP16-NONFINITE-AUDIO` | open · MEU-NEW P2 | Session 74 (D-797 ship amendment), outside this grouping; MEU-144 held for it (D-801). Not run yet |
| `TOOLING-SHARED-REGISTRY-COUPLING` | mitigated · TECH-DEBT P2 | Not grouped: one test (`test_hdp_expert_pass.py` `test_ac_10_…`) still reads the machine registry (D-912); it rides the next change to that file |
| `MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT` | open · TECH-DEBT P3 | Not grouped: rides the next change under the MCP audit's gated paths |
| `MCP-AUDIT-BASELINE-PENDING-CROP` | open · TECH-DEBT P3 | Not grouped: closes at the next release's MCP audit baseline |
| `DOWNLOADER-ADVANCED-PANEL-GAP` | open · TECH-DEBT P4 | Not grouped: standing debt, no current consumer |
| `DOWNLOAD-QUEUE-DRAG-OVER-MISS` | open · MONITORING | Not grouped: watch for a repeat |
| `CAPTURE-ZOOM-PAN-ORIGIN-FLAKE` | open · MONITORING | Not grouped: watch for a repeat |
| `CAPTURE-E2E-LAUNCH-TEARDOWN-HANG` | open · MONITORING | Not grouped: watch for a repeat |
| `TRANSCRIPT-ADD-CHANNEL-422` | open · MONITORING | Not grouped: watch for a repeat |
| `E2E-CLIPBOARD-PRIMER-EMPTY` | open · MONITORING | Not grouped: watch for a repeat |
| `E2E-TRANSCRIPT-SEAM-RELOAD-FLAKE` | open · MONITORING | Not grouped: watch for a repeat |
| `VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE` | open · MONITORING | Not grouped: watch for a repeat |
| `MCP-ELICITATION-VSCODE-AUTO-DECLINE` | mitigated · UPSTREAM | Not grouped: waits on the IDE client |
| `YOUTUBE-CAPTIONS-IP-BLOCK` | open · UPSTREAM | Not grouped: YouTube-side block, mitigated by MEU-115 and MEU-116 |
| `MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL` | open · UPSTREAM | Not grouped: waits on the MCP clients |
| `CAPTURE-JOURNAL-VOLATILE` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-JA-ZH-G2P-EXTRAS` | open · DEFER | Not grouped: deferred by its own ruling |
| `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` | open · BLOCKED | Not grouped: waits for eSpeak NG on a test machine |
| `FFMPEG-LIBDVDCSS-BUNDLED` | open · CLOSE | Not grouped: accepted risk (D-266); stays open as the record |

---

## 2. Dependency graph + critical path

```
MEU-45, MEU-46, MEU-155 ──► MEU-156 ─┐
MEU-97 ───────────────────► MEU-157 ─┴── Session 89 (156, 157)
(test and dev tooling, no MEU) ───────── Session 90
```

Every prerequisite is approved, and neither MEU depends on the other.

**Critical path:** none. The order in §5 is a priority order, not a dependency chain.

**Soft order (shared files, not dependencies):**
- `features/converter/convert-commands.ts`: MEU-156 (the palette's cancel) and MEU-157 (browse delivery), which is one reason they share Session 89.
- `ui/tests/e2e/`: Session 89 adds or edits Convert and queue specs; Session 90 changes `main-error-watch.cjs`, which every launch preloads. Session 90 runs after Session 89's commit, not beside it.
- `tests/integration/`: Session 90 only.

---

## 3. Recommended grouping — 2 sessions (89, 90)

### Session 89 — `queue-convert-fixes` (MEU-156, MEU-157) · P3

- **Layer / files:** `features/converter/convert-controls.ts` and `features/downloader/download-controls.ts` (the cancel rule), the two command modules (the palette's cancel, and `navigateAndDeliver` for browse), `ConvertPage.tsx` (the browse listener), `ui/tests/e2e/convert-queue.test.ts` (AC-97.7) and an Electron E2E spec for Cancel while Paused.
- **Why grouped:** both are small renderer fixes on the Convert queue page that Electron E2E must prove, and both touch `convert-commands.ts`. The bucket tool proposed the same pair.
- **Order:** MEU-156 → MEU-157. MEU-156 is Mat's ruling; MEU-157 then edits AC-97.7's spec, which the session gate runs.
- **Gate:** MEU-156 follows Mat's ruling (D-1100): disabled while Paused, no service or API change. MEU-157's holding mechanism, and whether other chords that navigate to a lazy page share the gap, are decided at plan time.
- **Cloud/local:** local (Electron E2E).
- **Token estimate:** calibrate against Session 88 `queue-pause-feedback` (the same toolbar, command modules and Electron proof; execution review 10,324,038 tokens).
- **Split flag:** no.

### Session 90 — `test-run-reliability` (no MEU) · P3

- **Layer / files:** the two integration tests with fixed 5-second waits (`tests/integration/test_youtube_adapter.py`, `tests/integration/test_tts_assets.py`) and any shared wait helper; `ui/tests/e2e/main-error-watch.cjs` and `electron-app.ts` (unhandled rejections); the `ui/package.json` dev script (`ELECTRON_RUN_AS_NODE`).
- **Covers:** `PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD` (P3), `E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED`, `UI-DEV-ELECTRON-RUN-AS-NODE-SILENT`.
- **Why grouped:** each makes a test or dev run report what really happened: a loaded host no longer fails a test on a short wait, a main-process promise rejection fails the E2E test, and `npm run dev` from an IDE terminal opens the app or says why it can't. Two of them finish Session 78's launch work. One theme, test and dev tooling only, no product change.
- **Order:** the Python waits (the P3, and it costs every session's gate a rerun) → the rejection watch → the dev script.
- **Gate:** a test whose wait changes keeps its assertions; any assertion change is named in the plan.
- **Cloud/local:** local (Electron E2E, the full Python suite).
- **Token estimate:** calibrate against Session 78 `e2e-harness-hardening` and Session 79 `triage-tool-fixes`.
- **Split flag:** no.

---

## 4. Plan-creation pathway

Mat asked for planning and execution to continue, so `/create-plan` runs once per session, in the §5 order, each followed by its Codex plan review and, once approved, execution. Each plan re-reads its MEU's build-plan home and the issues it closes. The no-MEU session plans as Session 78 did: the plan names the issues it closes, and no MEU status changes.

1. `/create-plan queue-convert-fixes` → MEU-156, MEU-157
2. `/create-plan test-run-reliability` → no MEU

---

## 5. Prerequisite gate

- **Queue (D-1104):** Session 89, then Session 90. Session 74 (`tts-fp16-guard-ship`) stays outside this grouping and waits on Mat.
- **Session 89:** MEU-156's contract is Mat's ruling (D-1100); nothing else is open.
- **Session 90:** none.
- No branch or worktree; main only. The coordinator commits each session after its execution review and does not push.

---

## 6. Session summary

| Session | Slug | MEUs | Band | Status | Plan folder |
|---------|------|------|------|--------|-------------|
| 89 | `queue-convert-fixes` | MEU-156, MEU-157 | P3 | proposed | — |
| 90 | `test-run-reliability` | — | P3 | proposed | — |

The Band column is the session's queue priority. Both MEUs are registered in band P2, as the earlier triage residuals were; a session band below P2 orders the queue and changes no register field.

---

## 7. Token calibration sources

`metrics.md` has no token column, so these are named sessions, not numbers.

- **Session 89:** Session 88 `queue-pause-feedback` (execution review 10,324,038 tokens) and Session 81 `convert-settings-drafts`.
- **Session 90:** Session 78 `e2e-harness-hardening` and Session 79 `triage-tool-fixes`.

---

## 8. Open Decisions

| ID | Question | Resolution | Chosen | Source tag | Reasoning (why this; why the alternatives lost) | Human ref |
|----|----------|------------|--------|------------|--------------------------------------------------|-----------|
| D-1102 | Triage the register, group what it leaves, and keep planning and executing? | human | Yes. D-1100 and D-1101 written; MEU-156 and MEU-157 registered and grouped with the three debt issues into Sessions 89 and 90, which are planned and executed in order. | Human-approved | Mat asked for exactly this. | USER_EXPLICIT 2026-11-17 "run @.agent/skills/issue-triage/ create session grouping and continue planning and executing as orchestrator" |
| D-1103 | Which work shares a session, and does the debt with no MEU get one? | autonomous | Session 89: MEU-156 and MEU-157, the Convert queue renderer pair the bucket tool also proposed. Session 90: the three test and dev debt issues, no MEU. The TTS FP16 issue stays with Session 74. | Local Canon | Sessions 78 and 79 ran test-harness and tooling debt with no MEU (D-815), and the closeout validator accepts it. Riding the debt on Session 89 lost: it widens that review for no shared file. One session per MEU lost: each is a few lines with its own E2E proof, and they share `convert-commands.ts`. Session 74 is Mat's ship gate (D-797). Two-way. | — |
| D-1104 | Queue order, and when does a plan go to execution? | autonomous | Session 89, then Session 90. Each plan goes to execution once its Codex plan review approves, unless the plan raises a decision that is Mat's. | Local Canon | User-facing fixes go ahead of test debt of the same band (D-816, D-538), and Session 89 holds Mat's ruling. Mat's message asks for execution to continue, which is the word `plan_to_exec_gate: human` waits for; a brief with an M hit outside M-3, M-5, M-6 or M-8 still goes to Mat. Two-way: one message from Mat moves it. | — |

Carry-forward: the closeout validator reads every §8 row of the declared grouping through `--decision-source` on this file, so a session's reflection does not restate them; its `### Decisions Log` lists only that session's own reversible autonomous choices (HDP §6), as Session 88's did.

- Session 89 carries D-1102, D-1103 and D-1104.
- Session 90 carries D-1102, D-1103 and D-1104.
